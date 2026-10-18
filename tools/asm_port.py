"""Translate the reconstructed 68000 assembly of the Amiga build to C for the SDL3 port.

Input: the assembly units of `tools/game_build.py`'s compile plan that carry game code or
data - RECONSTRUCTED_ASM modules (the audio driver, the Paula interrupt handlers, the
VBlank server and its colour callbacks) and TYPED_CODE_DATA tables (scores, envelopes,
selectors). Output (build/port-gen/, never committed):

  asm_code.c     one C function per module; every instruction is a labelled C statement
                 on the emulated register file (port/m68k.h) and a dispatcher maps an
                 original CODE address to it
  asm_tables.c   the tables as their big-endian bytes, 32-bit references patched in at start
  asm_symbols.s  the public names: code labels are keys M68K_CODE_BASE + original address
                 (the DATA hunk's code pointers `recon_h00_544C + 200` stay decodable),
                 table labels alias into the tables

The original addresses come from instruction sizes and the span-dependent branch sizes the
pinned assembler picks; every address-named label (`_recon_h00_5480`, `_L59C6`) is checked
against them. Units that have a hand-written port version are skipped (PORT_C_VERSIONS).

Usage: python tools/asm_port.py [--source DIR] [--output DIR]
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE_BASE = 0x70000000                     # m68k.h M68K_CODE_BASE

# Assembly with a port version in port/ (os_graphics.c: BltMaskBitMapRastPort glue;
# asm_ports.c: kprintf through RawDoFmt).
PORT_C_VERSIONS = {'resident_glue_4692', 'resident_frameless_701A'}

# Entries the game's C code calls directly: the argument widths the assembly reads from
# the stack ('w' 16-bit, 'l' 32-bit), pushed as Aztec C pushes them.
C_ENTRIES = {
    'recon_h00_57D2': 'w',               # sound command
    'recon_h00_5868': '',                # driver init
    'recon_h00_5594': '',                # audio interrupts off
    'recon_h00_57B6': '',                # remember A4
    'resident_asm_559E': '',             # random byte
}
# C functions the assembly calls: (result width, argument widths on the stack).
C_CALLEES = {
    'recon_h00_5064': ('w', 'll'),       # the input handler body (event list, data)
}

SIZE = {'b': 1, 'w': 2, 'l': 4, 's': 1}


class AsmError(Exception):
    pass


def strip_comment(line):
    quote = None
    for i, c in enumerate(line):
        if quote:
            quote = None if c == quote else quote
        elif c in '\'"':
            quote = c
        elif c == ';' or (c == '*' and not line[:i].strip()):
            return line[:i]
    return line


def split_operands(text):
    out, depth, cur = [], 0, ''
    for c in text:
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        if c == ',' and depth == 0:
            out.append(cur.strip()); cur = ''
        else:
            cur += c
    if cur.strip():
        out.append(cur.strip())
    return out


class Statement:
    def __init__(self, op, args, line, section):
        self.op, self.args, self.line, self.section = op, args, line, section
        self.labels, self.address, self.size = [], None, 0


def parse(text, name):
    """Statements with macros expanded. Returns (statements, equates, publics, end labels)."""
    macros, equates, publics, statements = {}, {}, {}, []
    pending, section, lines, i = [], None, text.splitlines(), 0

    def emit(op, args, raw):
        st = Statement(op, args, raw, section or 'cseg')
        st.labels, pending[:] = list(pending), []
        statements.append(st)

    def body_lines(lines_iter):
        for raw in lines_iter:
            yield raw

    queue = [(raw, None) for raw in lines]
    while queue:
        raw, args = queue.pop(0)
        if args is not None:
            raw = re.sub(r'\\(\d)', lambda m: args[int(m.group(1)) - 1] if int(m.group(1)) <= len(args) else '', raw)
        line = strip_comment(raw).rstrip()
        if not line.strip():
            continue
        m = re.match(r'^([A-Za-z_.]\w*)\s+macro\b', line)
        if m:
            body = []
            while True:
                if not queue:
                    raise AsmError('%s: unterminated macro %s' % (name, m.group(1)))
                nxt = queue.pop(0)[0]
                if re.match(r'^\s+endm\b', strip_comment(nxt)):
                    break
                body.append(nxt)
            macros[m.group(1)] = body
            continue
        m = re.match(r'^([A-Za-z_.]\w*)\s+equ\s+(.+)$', line)
        if m:
            equates[m.group(1)] = m.group(2).strip()
            continue
        m = re.match(r'^([A-Za-z_.]\w*):?(\s+.*)?$', line)
        if m and not line[0].isspace():
            pending.append(m.group(1))
            line = m.group(2) or ''
            if not line.strip():
                continue
        parts = line.strip().split(None, 1)
        op = parts[0].lower() if parts[0] not in macros else parts[0]
        operands = split_operands(parts[1]) if len(parts) > 1 else []
        if op in macros:
            queue[0:0] = [(b, operands) for b in macros[op]]
            continue
        if op in ('cseg', 'dseg'):
            if pending:                          # labels that end the section before
                emit('.mark', [], '')
            section = op; continue
        if op == 'public':
            publics.update((a.strip(), section) for a in operands); continue
        if op in ('far', 'near', 'end', 'endm', 'global'):
            continue
        emit(op, operands, raw.strip())
    ends = list(pending)                     # labels after the last statement
    return statements, equates, publics, ends


NUMBER = re.compile(r'^-?(\$[0-9A-Fa-f]+|\d+)$')


def number(text):
    text = text.strip()
    neg = text.startswith('-')
    body = text[1:] if neg else text
    value = int(body[1:], 16) if body.startswith('$') else int(body)
    return -value if neg else value


def expression(text, equates):
    """A number, an equate, or a symbol with an optional +/- constant. Returns (symbol, offset)."""
    text = text.strip()
    if NUMBER.match(text):
        return None, number(text)
    if text in equates:
        return expression(equates[text], equates)
    m = re.match(r'^([A-Za-z_.]\w*)\s*(?:([-+])\s*(\$?[0-9A-Fa-f]+))?$', text)
    if not m:
        raise AsmError('expression: ' + text)
    offset = number(m.group(3)) * (1 if m.group(2) == '+' else -1) if m.group(2) else 0
    return m.group(1), offset


# ---------------------------------------------------------------- operands
REG = re.compile(r'^(d[0-7]|a[0-7]|sp)$', re.I)


class Operand:
    """mode: dreg areg ind postinc predec disp index abs imm pcdisp reglist"""
    def __init__(self, text, equates):
        self.text = t = text.strip()
        low = t.lower()
        self.symbol, self.value, self.reg, self.index = None, 0, None, None
        if low.startswith('#'):
            self.mode = 'imm'; self.symbol, self.value = expression(t[1:], equates)
        elif REG.match(low):
            r = 'a7' if low == 'sp' else low
            self.mode, self.reg = ('dreg' if r[0] == 'd' else 'areg'), int(r[1])
        elif re.match(r'^(d[0-7]|a[0-7])(-(d[0-7]|a[0-7]))?(/(d[0-7]|a[0-7])(-(d[0-7]|a[0-7]))?)*$', low):
            self.mode, self.regs = 'reglist', reglist(low)
        elif re.match(r'^\((a[0-7]|sp)\)$', low):
            self.mode, self.reg = 'ind', areg(low[1:-1])
        elif re.match(r'^\((a[0-7]|sp)\)\+$', low):
            self.mode, self.reg = 'postinc', areg(low[1:-2])
        elif re.match(r'^-\((a[0-7]|sp)\)$', low):
            self.mode, self.reg = 'predec', areg(low[2:-1])
        else:
            m = re.match(r'^(.*)\(\s*(pc|a[0-7]|sp)\s*(?:,\s*([da][0-7])(?:\.([wl]))?)?\s*\)$', t, re.I)
            if m:
                disp = m.group(1).strip() or '0'
                self.symbol, self.value = expression(disp, equates)
                base = m.group(2).lower()
                if base == 'pc':
                    self.mode = 'pcdisp'
                elif m.group(3):
                    self.mode, self.reg = 'index', areg(base)
                    x = m.group(3).lower()
                    self.index = (x[0], int(x[1]), (m.group(4) or 'w').lower())
                else:
                    self.mode, self.reg = 'disp', areg(base)
            else:
                self.mode = 'abs'; self.symbol, self.value = expression(t, equates)

    def extension(self, size):
        if self.mode in ('dreg', 'areg', 'ind', 'postinc', 'predec', 'reglist'):
            return 0
        if self.mode in ('disp', 'index', 'pcdisp'):
            return 2
        if self.mode == 'abs':
            if getattr(self, 'near', False):
                return 2                          # d16(a4): a public declared outside dseg
            return 2 if self.symbol is None and -0x8000 <= self.value <= 0x7FFF else 4
        if self.mode == 'imm':
            return 4 if size == 4 else 2
        raise AsmError(self.text)


def areg(text):
    return 7 if text in ('sp', 'a7') else int(text[1])


def reglist(text):
    regs = []
    for part in text.split('/'):
        lo, _, hi = part.partition('-')
        a, b = (lo[0], int(lo[1])), (hi[0], int(hi[1])) if hi else (lo[0], int(lo[1]))
        idx = lambda r: (0 if r[0] == 'd' else 8) + r[1]
        regs += list(range(idx(a), idx(b) + 1))
    return sorted(set(regs))


# ---------------------------------------------------------------- sizes
BRANCHES = {'bra', 'bsr', 'beq', 'bne', 'bcc', 'bcs', 'bmi', 'bpl', 'ble', 'bhi', 'bge', 'blt', 'bgt', 'bls',
            'bvc', 'bvs', 'bhs', 'blo'}
QUICK = {'addq', 'subq'}
SHIFTS = {'lsl', 'lsr', 'asl', 'asr', 'roxl', 'roxr', 'rol', 'ror'}
BITS = {'btst', 'bclr', 'bset', 'bchg'}


def mnemonic(op):
    base, _, suffix = op.partition('.')
    return base, SIZE.get(suffix, 2 if base not in ('moveq',) else 4) if suffix else None


def instruction_size(st, ops, internal):
    """Bytes of one instruction; branches get their size from layout()."""
    base, size = mnemonic(st.op)
    size = size or (4 if base in ('lea', 'movea', 'moveq', 'swap', 'ext') else 2)
    if base in BRANCHES:
        return None
    if base == 'dbra' or base == 'dbf':
        return 4
    if base in ('rts', 'nop', 'rte'):
        return 2
    if base in ('moveq',):
        return 2
    if base in QUICK:
        return 2 + ops[1].extension(size)
    if base in SHIFTS:
        return 2 + (ops[0].extension(2) if len(ops) == 1 else 0)
    if base in BITS:
        return 2 + (2 if ops[0].mode == 'imm' else 0) + ops[1].extension(1)
    if base == 'movem':
        return 4 + sum(o.extension(4) for o in ops)
    return 2 + sum(o.extension(size) for o in ops)


def layout(statements, base_address, equates, name, near=(), ends=()):
    """Assign original addresses: instructions in cseg from base_address; branch sizes
    by the span-dependent rule (short when the displacement fits and is not zero)."""
    code = [s for s in statements if s.section == 'cseg']
    labels = {l for s in code for l in s.labels} | set(ends)
    for st in code:
        st.ops = [Operand(a, equates) for a in st.args] if not st.op.startswith('dc') and st.op != 'ds' else []
        st.base = mnemonic(st.op)[0]
        for o in st.ops:
            if o.mode == 'abs' and o.symbol in near and o.symbol not in labels:
                o.near = True
            if o.mode == 'abs' and st.base in ('jsr', 'jmp') and o.symbol:
                o.mode = 'pcdisp'                 # the assembler makes a code reference PC-relative
        st.fixed = 0 if st.op == '.mark' else instruction_size(st, st.ops, labels) if st.base not in BRANCHES else None
        if st.base in BRANCHES:
            target = st.ops[0].symbol
            st.size = 2 if target in labels else 4
    while True:
        address, where = base_address, {}
        for st in code:
            st.address = address
            for l in st.labels:
                where[l] = address
            address += st.fixed if st.fixed is not None else st.size
        for l in ends:
            where[l] = address
        changed = False
        for st in code:
            if st.base in BRANCHES and st.size == 2:
                disp = where[st.ops[0].symbol] - (st.address + 2)
                if disp == 0 or not -128 <= disp <= 127:
                    st.size, changed = 4, True
        if not changed:
            for st in code:
                st.size = st.fixed if st.fixed is not None else st.size
            return where, address


def check_named_labels(where, name):
    for label, address in where.items():
        m = re.match(r'^_(?:recon_h00|resident_asm|L)_?([0-9A-F]{4})$', label)
        if m and int(m.group(1), 16) != address:
            raise AsmError('%s: %s laid out at %04X' % (name, label, address))


# ---------------------------------------------------------------- C generation
def c_name(symbol):
    return symbol[1:] if symbol.startswith('_') else symbol


MASK = {1: '0xFFu', 2: '0xFFFFu', 4: '0xFFFFFFFFu'}


class Module:
    def __init__(self, source, text, unit):
        self.source, self.unit = source, unit
        self.statements, self.equates, self.publics, self.ends = parse(text, unit)
        first = next(l for s in self.statements for l in s.labels)
        m = re.match(r'^_(?:recon_h00|resident_asm)_([0-9A-F]{4})$', first)
        if not m:
            raise AsmError('%s: first label %s names no address' % (unit, first))
        near = {n for n, section in self.publics.items() if section != 'dseg'}
        self.where, self.end = layout(self.statements, int(m.group(1), 16), self.equates, unit, near, self.ends)
        for l in self.ends:
            self.where[l] = self.end
        check_named_labels(self.where, unit)
        self.start = int(m.group(1), 16)


class Generator:
    def __init__(self, modules, data_symbols):
        self.modules, self.data_symbols = modules, data_symbols
        self.code = {}
        for mod in modules:
            for label, address in mod.where.items():
                self.code[label] = address
        self.externs, self.ccalls = set(), set()

    def value_of(self, symbol, offset=0):
        """C expression for a symbol's value as the 68000 sees it."""
        if symbol in self.code:
            return '0x%08Xu' % (CODE_BASE + self.code[symbol] + offset)
        self.externs.add(c_name(symbol))
        return '((uint32_t)(uintptr_t)%s + %du)' % (c_name(symbol), offset) if offset else '(uint32_t)(uintptr_t)%s' % c_name(symbol)

    # -- effective addresses
    def address(self, op, size, tmp, pre):
        """Statements into `pre` computing the address into `tmp`; returns tmp."""
        if op.mode == 'ind':
            pre.append('%s = A(%d);' % (tmp, op.reg))
        elif op.mode == 'postinc':
            step = 2 if size == 1 and op.reg == 7 else size
            pre.append('%s = A(%d); A(%d) += %d;' % (tmp, op.reg, op.reg, step))
        elif op.mode == 'predec':
            step = 2 if size == 1 and op.reg == 7 else size
            pre.append('A(%d) -= %d; %s = A(%d);' % (op.reg, step, tmp, op.reg))
        elif op.mode == 'disp':
            disp = op.value if op.symbol is None else None
            if disp is None:
                raise AsmError('symbolic displacement ' + op.text)
            pre.append('%s = A(%d) + (uint32_t)(int32_t)%d;' % (tmp, op.reg, disp))
        elif op.mode == 'index':
            kind, n, width = op.index
            reg = '%s(%d)' % (kind.upper(), n)
            x = '(uint32_t)(int32_t)(int16_t)%s' % reg if width == 'w' else reg
            pre.append('%s = A(%d) + (uint32_t)(int32_t)%d + %s;' % (tmp, op.reg, op.value, x))
        elif op.mode == 'abs':
            pre.append('%s = %s;' % (tmp, self.value_of(op.symbol, op.value) if op.symbol else '0x%Xu' % (op.value & 0xFFFFFFFF)))
        elif op.mode == 'pcdisp':
            pre.append('%s = %s;' % (tmp, self.value_of(op.symbol, op.value)))
        else:
            raise AsmError('no address: ' + op.text)
        return tmp

    def read(self, op, size, tmp, pre, signed_word=False):
        if op.mode == 'dreg':
            return '(D(%d) & %s)' % (op.reg, MASK[size])
        if op.mode == 'areg':
            return '(A(%d) & %s)' % (op.reg, MASK[size])
        if op.mode == 'imm':
            if op.symbol:
                return self.value_of(op.symbol, op.value)
            return '0x%Xu' % (op.value & int(MASK[size][:-1], 16))
        return 'm68k_rd%d(%s)' % (size * 8, self.address(op, size, tmp, pre))

    def write(self, op, size, value, addr=None):
        if op.mode == 'dreg':
            if size == 4:
                return 'D(%d) = %s;' % (op.reg, value)
            return 'D(%d) = (D(%d) & ~%s) | ((%s) & %s);' % (op.reg, op.reg, MASK[size], value, MASK[size])
        if op.mode == 'areg':
            return 'A(%d) = %s;' % (op.reg, value)
        return 'm68k_wr%d(%s, %s);' % (size * 8, addr, value)

    def target(self, symbol):
        if symbol not in self.code:
            return None
        return self.code[symbol]

    def call(self, symbol, next_address):
        if symbol in self.code:
            return 'm68k_push32(0x%08Xu); m68k_run(0x%04X);' % (CODE_BASE + next_address, self.code[symbol])
        name = c_name(symbol)
        if name not in C_CALLEES:
            raise AsmError('call to %s: not translated and no C signature (C_CALLEES)' % name)
        self.ccalls.add(name)
        return 'm68k_push32(0x%08Xu); ccall_%s(); A(7) += 4;' % (CODE_BASE + next_address, name)

    def jump(self, symbol, mod):
        address = self.code.get(symbol)
        if address is None:
            raise AsmError('jump to unknown %s' % symbol)
        if mod.start <= address < mod.end:
            return 'goto L_%04X;' % address
        return 'm68k_run(0x%04X); return;' % address

    def instruction(self, st, mod, nxt):
        b, size = mnemonic(st.op)
        ops = st.ops
        pre, body = [], []
        cond = {'beq': 'm68k.z', 'bne': '!m68k.z', 'bcc': '!m68k.c', 'bhs': '!m68k.c', 'bcs': 'm68k.c', 'blo': 'm68k.c',
                'bmi': 'm68k.n', 'bpl': '!m68k.n', 'ble': '(m68k.z || m68k.n != m68k.v)', 'bgt': '(!m68k.z && m68k.n == m68k.v)',
                'blt': '(m68k.n != m68k.v)', 'bge': '(m68k.n == m68k.v)', 'bhi': '(!m68k.c && !m68k.z)', 'bls': '(m68k.c || m68k.z)',
                'bvc': '!m68k.v', 'bvs': 'm68k.v'}
        if b in cond:
            return 'if (%s) { %s }' % (cond[b], self.jump(ops[0].symbol, mod))
        if b == 'bra':
            return self.jump(ops[0].symbol, mod)
        if b in ('bsr', 'jsr') and ops[0].mode in ('abs', 'pcdisp'):
            return self.call(ops[0].symbol, nxt)
        if b == 'jsr':
            a = self.address(ops[0], 4, 'ea', pre)
            return ' '.join(pre) + ' m68k_push32(0x%08Xu); m68k_run(ea);' % (CODE_BASE + nxt)
        if b == 'jmp':
            if ops[0].mode in ('abs', 'pcdisp'):
                return self.jump(ops[0].symbol, mod)
            a = self.address(ops[0], 4, 'ea', pre)
            return ' '.join(pre) + ' m68k_run(ea); return;'
        if b == 'rts':
            return 'A(7) += 4; return;'
        if b in ('dbra', 'dbf'):
            n = ops[0].reg
            return '{ uint16_t w = (uint16_t)(D(%d) - 1); D(%d) = (D(%d) & 0xFFFF0000u) | w; if (w != 0xFFFFu) { %s } }' % (
                n, n, n, self.jump(ops[1].symbol, mod))
        size = size or {'moveq': 4, 'lea': 4, 'swap': 4}.get(b, 2)
        if b == 'move' or b == 'movea':
            v = self.read(ops[0], size, 'ea', pre)
            if ops[1].mode == 'areg':
                v = '(uint32_t)(int32_t)(int16_t)%s' % v if size == 2 else v
                return ' '.join(pre + ['A(%d) = %s;' % (ops[1].reg, v)])
            pre.append('v = %s;' % v)
            dst = self.address(ops[1], size, 'eb', pre) if ops[1].mode not in ('dreg',) else None
            return ' '.join(pre + ['m68k_logic(v, %d);' % size, self.write(ops[1], size, 'v', dst)])
        if b == 'moveq':
            return 'D(%d) = (uint32_t)(int32_t)(int8_t)%d; m68k_logic(D(%d), 4);' % (ops[1].reg, ops[0].value, ops[1].reg)
        if b == 'lea':
            return ' '.join(pre + ['A(%d) = %s;' % (ops[1].reg, self.address(ops[0], 4, 'ea', pre))]) if False else \
                self.lea(ops)
        if b == 'clr':
            dst = self.address(ops[0], size, 'eb', pre) if ops[0].mode != 'dreg' else None
            return ' '.join(pre + [self.write(ops[0], size, '0', dst), 'm68k_logic(0, %d);' % size])
        if b == 'tst':
            return ' '.join(pre + ['m68k_logic(%s, %d);' % (self.read(ops[0], size, 'ea', pre), size)])
        if b in ('add', 'sub', 'addq', 'subq', 'addi', 'subi', 'adda', 'suba'):
            kind = 'add' if b.startswith('add') else 'sub'
            src = '0x%Xu' % ops[0].value if b in ('addq', 'subq') else self.read(ops[0], size, 'ea', pre)
            if ops[1].mode == 'areg':
                if size == 2 and b in ('adda', 'suba', 'add', 'sub'):
                    src = '(uint32_t)(int32_t)(int16_t)%s' % src
                return ' '.join(pre + ['A(%d) %s= %s;' % (ops[1].reg, '+' if kind == 'add' else '-', src)])
            pre.append('v = %s;' % src)
            if ops[1].mode == 'dreg':
                return ' '.join(pre + [self.write(ops[1], size, 'm68k_%s(D(%d), v, %d)' % (kind, ops[1].reg, size))])
            a = self.address(ops[1], size, 'eb', pre)
            return ' '.join(pre + ['m68k_wr%d(eb, m68k_%s(m68k_rd%d(eb), v, %d));' % (size * 8, kind, size * 8, size)])
        if b in ('cmp', 'cmpi', 'cmpa'):
            src = self.read(ops[0], size, 'ea', pre)
            pre.append('v = %s;' % src)
            dst = self.read(ops[1], size, 'eb', pre)
            return ' '.join(pre + ['m68k_cmp(%s, v, %d);' % (dst, size)])
        if b in ('and', 'or', 'eor', 'andi', 'ori', 'eori'):
            op = {'a': '&', 'o': '|', 'e': '^'}[b[0]]
            pre.append('v = %s;' % self.read(ops[0], size, 'ea', pre))
            if ops[1].mode == 'dreg':
                return ' '.join(pre + [self.write(ops[1], size, 'm68k_logic(D(%d) %s v, %d)' % (ops[1].reg, op, size))])
            a = self.address(ops[1], size, 'eb', pre)
            return ' '.join(pre + ['m68k_wr%d(eb, m68k_logic(m68k_rd%d(eb) %s v, %d));' % (size * 8, size * 8, op, size)])
        if b in SHIFTS:
            if len(ops) == 1:                      # memory, by one
                a = self.address(ops[0], 2, 'eb', pre)
                return ' '.join(pre + ['m68k_wr16(eb, m68k_%s(m68k_rd16(eb), 1, 2));' % b])
            count = '%du' % ops[0].value if ops[0].mode == 'imm' else '(D(%d) & 63u)' % ops[0].reg
            return self.write(ops[1], size, 'm68k_%s(D(%d), %s, %d)' % (b, ops[1].reg, count, size))
        if b in BITS:
            bit = '%du' % ops[0].value if ops[0].mode == 'imm' else 'D(%d)' % ops[0].reg
            if ops[1].mode == 'dreg':
                n = ops[1].reg
                pre.append('v = 1u << (%s & 31u); m68k.z = (D(%d) & v) == 0;' % (bit, n))
                if b == 'bclr': pre.append('D(%d) &= ~v;' % n)
                if b == 'bset': pre.append('D(%d) |= v;' % n)
                if b == 'bchg': pre.append('D(%d) ^= v;' % n)
                return ' '.join(pre)
            a = self.address(ops[1], 1, 'eb', pre)
            pre.append('v = 1u << (%s & 7u); r = m68k_rd8(eb); m68k.z = (r & v) == 0;' % bit)
            if b == 'bclr': pre.append('m68k_wr8(eb, r & ~v);')
            if b == 'bset': pre.append('m68k_wr8(eb, r | v);')
            if b == 'bchg': pre.append('m68k_wr8(eb, r ^ v);')
            return ' '.join(pre)
        if b == 'swap':
            n = ops[0].reg
            return 'D(%d) = (D(%d) >> 16) | (D(%d) << 16); m68k_logic(D(%d), 4);' % (n, n, n, n)
        if b == 'ext':
            n = ops[0].reg
            if size == 4:
                return 'D(%d) = (uint32_t)(int32_t)(int16_t)D(%d); m68k_logic(D(%d), 4);' % (n, n, n)
            return 'D(%d) = (D(%d) & 0xFFFF0000u) | (uint16_t)(int16_t)(int8_t)D(%d); m68k_logic(D(%d), 2);' % (n, n, n, n)
        if b == 'movem':
            if ops[0].mode == 'reglist':
                regs, dst = ops[0].regs, ops[1]
                if dst.mode != 'predec':
                    raise AsmError('movem to ' + dst.text)
                return ' '.join('A(%d) -= 4; m68k_wr32(A(%d), %s);' % (dst.reg, dst.reg, reg_c(r)) for r in reversed(regs))
            src, regs = ops[0], ops[1].regs
            if src.mode != 'postinc':
                raise AsmError('movem from ' + src.text)
            return ' '.join('%s = m68k_rd32(A(%d)); A(%d) += 4;' % (reg_c(r), src.reg, src.reg) for r in regs)
        raise AsmError('%s: no translation for %s' % (mod.unit, st.line))

    def lea(self, ops):
        pre = []
        a = self.address(ops[0], 4, 'ea', pre)
        return ' '.join(pre + ['A(%d) = ea;' % ops[1].reg])

    def module(self, mod):
        out = ['/* %s (%s) */' % (mod.source, mod.unit),
               'static void mod_%04X(uint32_t pc)' % mod.start, '{',
               '    uint32_t ea = 0, eb = 0, v = 0, r = 0;', '    (void)ea; (void)eb; (void)v; (void)r;',
               '    switch (pc) {']
        code = [s for s in mod.statements if s.section == 'cseg']
        for st in code:
            out.append('    case 0x%04X: goto L_%04X;' % (st.address, st.address))
        out += ['    default: m68k_bad_entry(pc); return;', '    }']
        for i, st in enumerate(code):
            nxt = st.address + st.size
            out.append('L_%04X: /* %s */' % (st.address, st.line.replace('*/', '* /')))
            if st.op != '.mark':
                out.append('    ' + self.instruction(st, mod, nxt))
        out.append('    m68k_run(0x%04X);       /* falls through into the next module */' % mod.end)
        out.append('}')
        return '\n'.join(out)


def reg_c(r):
    return 'D(%d)' % r if r < 8 else 'A(%d)' % (r - 8)


# ---------------------------------------------------------------- tables
class Table:
    """The bytes of one section of a TYPED_CODE_DATA unit, big-endian, and its references."""
    def __init__(self, unit, source, section, statements, equates):
        self.unit, self.source, self.section = unit, source, section
        self.bytes, self.labels, self.refs = bytearray(), {}, []
        for st in statements:
            for l in st.labels:
                self.labels[l] = len(self.bytes)
            if st.op in ('dc.b', 'dc.w', 'dc.l', 'dc'):
                width = SIZE.get(st.op.partition('.')[2] or 'w')
                if width > 1 and len(self.bytes) % 2:
                    raise AsmError('%s: odd %s at +%d' % (unit, st.op, len(self.bytes)))
                for arg in st.args:
                    if arg.startswith(("'", '"')):
                        self.bytes += arg[1:-1].encode('latin-1'); continue
                    symbol, value = expression(arg, equates)
                    if symbol:
                        if width != 4:
                            raise AsmError('%s: %d-byte reference %s' % (unit, width, arg))
                        self.refs.append((len(self.bytes), symbol, value))
                        value = 0
                    self.bytes += (value & ((1 << (8 * width)) - 1)).to_bytes(width, 'big')
            elif st.op == 'ds':
                count = number(st.args[0]) if st.args else 0
                if count == 0:
                    if len(self.bytes) % 2:
                        self.bytes.append(0)
                else:
                    self.bytes += bytes(2 * count)
            elif st.op == '.mark':
                pass
            elif st.op in ('even', 'cnop'):
                if len(self.bytes) % 2:
                    self.bytes.append(0)
            else:
                raise AsmError('%s: not table data: %s' % (unit, st.line))


def read_symbols(path):
    """{(hunk, name): address} from the Amiga build's linker symbol file (DuckTales.sym)."""
    table, hunk = {}, None
    for line in path.read_text(encoding='latin-1').splitlines():
        m = re.match(r'Segment \d+:\s+Hunk (\d+)', line)
        if m:
            hunk = int(m.group(1)); continue
        m = re.match(r'\s+([0-9a-f]{8}) (\S+)$', line)
        if m:
            table.setdefault(m.group(2), (hunk, int(m.group(1), 16)))
    return table


def check_against_build(unit, offsets, built):
    """The offsets this tool computed between labels equal the assembled Amiga build's."""
    known = [(label, at) for label, at in offsets.items() if label in built]
    if not known:
        return 0
    first, first_at = known[0]
    for label, at in known:
        if built[label][0] != built[first][0] or built[label][1] - built[first][1] != at - first_at:
            raise AsmError('%s: %s at +%d from %s; the Amiga build has +%d'
                           % (unit, label, at - first_at, first, built[label][1] - built[first][1]))
    return len(known)


STAGED = re.compile(r'staged from accepted source: (\S+?); proof class: (\w+)')


def units(plan, guest):
    """(source, proof class, unit, text) of every game assembly unit in plan order."""
    for entry in plan:
        if entry['kind'] == 'c':
            continue
        text = (guest / entry['source']).read_text(encoding='latin-1')
        m = STAGED.search(text.splitlines()[0]) if text else None
        if not m or m.group(2) not in ('RECONSTRUCTED_ASM', 'TYPED_CODE_DATA'):
            continue
        if Path(m.group(1)).stem in PORT_C_VERSIONS:
            continue
        yield m.group(1), m.group(2), Path(entry['source']).stem, text


def data_gaps(data_hunk_c):
    """(start, size) of the zero-filled gaps of the generated DATA hunk structure."""
    return [(int(o, 16), int(n)) for o, n in re.findall(r'uint8_t gap_([0-9A-F]{4})\[(\d+)\];', data_hunk_c)]


def generate(source, output, data_hunk_c=None):
    plan = json.loads((source / 'compile-plan.json').read_text())
    guest = source / 'guest_source'
    modules, tables, defined, report = [], [], {}, dict(modules=[], tables=[], duplicates=[], data_parts=[])
    for src, proof, unit, text in units(plan, guest):
        if proof == 'RECONSTRUCTED_ASM':
            mod = Module(src, text, unit)
            modules.append(mod)
            report['modules'].append(dict(unit=unit, source=src, start='%04X' % mod.start, end='%04X' % mod.end))
            continue
        statements, equates, publics, ends = parse(text, unit)
        for section in ('cseg', 'dseg'):
            part = [s for s in statements if s.section == section]
            if part:
                table = Table(unit, src, section, part, equates)
                if section == statements[-1].section:
                    for l in ends:                  # labels after the last statement: the end
                        table.labels.setdefault(l, len(table.bytes))
                table.publics = publics
                tables.append(table)
    built = read_symbols(source / 'DuckTales.sym') if (source / 'DuckTales.sym').exists() else {}
    counts = {}
    for item in modules + tables:
        for label in (item.where if hasattr(item, 'where') else item.labels):
            counts[label] = counts.get(label, 0) + 1
    checked = 0
    for item in modules + tables:
        offsets = item.where if hasattr(item, 'where') else item.labels
        checked += check_against_build(item.unit, {l: at for l, at in offsets.items() if counts[l] == 1}, built)
    report['labels_checked_against_build'] = checked
    gen = Generator(modules, set())
    # Table symbols: the first definition wins, as with the Amiga linker.
    code_tables = [t for t in tables if t.section == 'cseg']
    data_tables = [t for t in tables if t.section == 'dseg']
    symbols, offset = {}, 0
    for t in code_tables:
        offset += offset % 2
        t.offset = offset
        for label, at in t.labels.items():
            if label in symbols or label in gen.code:
                report['duplicates'].append(dict(unit=t.unit, label=label)); continue
            symbols[label] = ('asm_code_data', offset + at)
        offset += len(t.bytes)
    code_data = bytearray()
    for t in code_tables:
        code_data += bytes(t.offset - len(code_data)) + t.bytes
    gaps = data_gaps(data_hunk_c) if data_hunk_c else []
    for t in data_tables:
        anchor = min(int(m.group(1), 16) - at for l, at in t.labels.items()
                     for m in [re.search(r'_h01_([0-9A-F]{4})$', l)] if m)
        if gaps and not any(g <= anchor and anchor + len(t.bytes) <= g + n for g, n in gaps):
            raise AsmError('%s: DATA part %04X+%d is not inside a gap of the DATA hunk' % (t.unit, anchor, len(t.bytes)))
        t.anchor = anchor
        report['data_parts'].append(dict(unit=t.unit, at='%04X' % anchor, size=len(t.bytes)))
        for label, at in t.labels.items():
            if label in symbols:
                report['duplicates'].append(dict(unit=t.unit, label=label)); continue
            symbols[label] = ('data', anchor + at)
    gen.data_symbols = symbols

    # asm_code.c
    body = [gen.module(m) for m in modules]
    lines = ['/* generated by tools/asm_port.py: the reconstructed 68000 assembly as C (port/m68k.h). */',
             '#include "m68k.h"']
    lines += ['extern char %s[];' % e for e in sorted(gen.externs)]
    for name in sorted(gen.ccalls):
        result, args = C_CALLEES[name]
        params = ', '.join('m68k_rd%d(A(7) + %d)' % ((32 if w == 'l' else 16), 4 + sum(4 if x == 'l' else 2 for x in args[:i]))
                           for i, w in enumerate(args))
        lines.append('extern %s %s(%s);' % ('int16_t' if result == 'w' else 'int32_t', name,
                                             ', '.join('uint32_t' if w == 'l' else 'int32_t' for w in args) or 'void'))
        lines.append('static void ccall_%s(void) { D(0) = (uint32_t)(int32_t)%s(%s); }' % (name, name, params))
    lines += body
    lines.append('void m68k_run(uint32_t pc)\n{\n    if (pc >= M68K_CODE_BASE) pc -= M68K_CODE_BASE;')
    for m in modules:
        lines.append('    if (pc >= 0x%04X && pc < 0x%04X) { mod_%04X(pc); return; }' % (m.start, m.end, m.start))
    lines.append('    m68k_bad_entry(pc);\n}')
    for name, args in C_ENTRIES.items():
        address = gen.code.get('_' + name)
        if address is None:
            raise AsmError('C entry %s is not in the translated assembly' % name)
        params = ', '.join('int32_t a%d' % i for i in range(len(args))) or 'void'
        values = ', '.join('(uint32_t)a%d' % i for i in range(len(args)))
        lines.append('int32_t %s(%s) { uint32_t args[%d] = {%s}; return (int32_t)m68k_entry(0x%04X, "%s", args); }'
                     % (name, params, max(1, len(args)), values or '0', address, args))
    (output / 'asm_code.c').write_text('\n'.join(lines) + '\n', encoding='latin-1', newline='\n')

    # asm_tables.c
    t_lines = ['/* generated by tools/asm_port.py: the TYPED_CODE_DATA tables, big-endian. */',
               '#include "m68k.h"', '#include <string.h>',
               'extern char amiga_data_hunk[];']
    refs = []
    for t in tables:
        for at, symbol, value in t.refs:
            refs.append((t, at, symbol, value))
    names = sorted({c_name(s) for _, _, s, _ in refs if s not in symbols and s not in gen.code})
    t_lines += ['extern char %s[];' % n for n in names]
    t_lines.append('uint8_t asm_code_data[%d] __attribute__((aligned(4))) = {' % max(1, len(code_data)))
    for i in range(0, len(code_data), 16):
        t_lines.append('    ' + ', '.join('0x%02X' % b for b in code_data[i:i + 16]) + ',')
    t_lines.append('};')
    for t in data_tables:
        t_lines.append('static const uint8_t data_part_%04X[%d] = {' % (t.anchor, len(t.bytes)))
        for i in range(0, len(t.bytes), 16):
            t_lines.append('    ' + ', '.join('0x%02X' % b for b in t.bytes[i:i + 16]) + ',')
        t_lines.append('};')

    def where_c(t, at):
        return ('asm_code_data + %d' % (t.offset + at)) if t.section == 'cseg' else \
            '(uint8_t *)amiga_data_hunk + 0x%X' % (t.anchor + at)

    def symbol_c(symbol, value):
        if symbol in gen.code:
            return '0x%08Xu' % (CODE_BASE + gen.code[symbol] + value)
        if symbol in symbols:
            kind, at = symbols[symbol]
            base = '(uintptr_t)asm_code_data' if kind == 'asm_code_data' else '(uintptr_t)amiga_data_hunk'
            return '(uint32_t)(%s + %d)' % (base, at + value)
        return '(uint32_t)((uintptr_t)%s + %d)' % (c_name(symbol), value)
    t_lines.append('void asm_tables_init(void)\n{')
    for t in data_tables:
        t_lines.append('    memcpy((uint8_t *)amiga_data_hunk + 0x%X, data_part_%04X, %d);' % (t.anchor, t.anchor, len(t.bytes)))
        t_lines.append('    m68k_big_endian((uint8_t *)amiga_data_hunk + 0x%X, %d);' % (t.anchor, len(t.bytes)))
    t_lines.append('    m68k_big_endian(asm_code_data, sizeof asm_code_data);')
    for t, at, symbol, value in refs:
        t_lines.append('    m68k_put_be32(%s, %s);' % (where_c(t, at), symbol_c(symbol, value)))
    t_lines.append('}')
    (output / 'asm_tables.c').write_text('\n'.join(t_lines) + '\n', encoding='latin-1', newline='\n')

    # asm_symbols.s: code keys and table labels
    s_lines = ['# generated by tools/asm_port.py']
    for label, address in sorted(gen.code.items(), key=lambda x: x[1]):
        if c_name(label) in C_ENTRIES or not any(label in m.publics for m in modules):
            continue
        s_lines += ['\t.globl %s' % label, '\t.set %s, 0x%08X' % (label, CODE_BASE + address)]
    (output / 'asm_symbols.s').write_text('\n'.join(s_lines) + '\n', encoding='latin-1', newline='\n')
    # Table labels alias into the object that defines their base (a COFF assembler exports
    # an alias only to a symbol of the same object): asm_tables.c for the code-data array,
    # the DATA hunk (port_gen.py appends report['data_aliases'] to data_hunk.c) for DATA parts.
    public = [(label, kind, at) for label, (kind, at) in symbols.items() if any(label in t.publics for t in tables)]
    code_aliases = ''.join('    ".globl %s\\n.set %s, _asm_code_data+%d\\n"\n' % (l, l, at)
                           for l, kind, at in public if kind == 'asm_code_data')
    with (output / 'asm_tables.c').open('a', encoding='latin-1', newline='\n') as f:
        f.write('__asm__(\n%s);\n' % code_aliases)
    report['data_aliases'] = [(l, at) for l, kind, at in public if kind == 'data']
    report['code_data_bytes'] = len(code_data)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--source', type=Path, default=ROOT / 'build/game')
    ap.add_argument('--output', type=Path, default=ROOT / 'build/port-gen')
    args = ap.parse_args(argv)
    args.output.mkdir(parents=True, exist_ok=True)
    hunk = args.output / 'data_hunk.c'
    report = generate(args.source, args.output, hunk.read_text(encoding='latin-1') if hunk.exists() else None)
    print('modules:', len(report['modules']), 'code-data bytes:', report['code_data_bytes'],
          'DATA parts:', len(report['data_parts']), 'duplicate labels:', len(report['duplicates']))


if __name__ == '__main__':
    main()
