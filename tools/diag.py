"""Shift-tolerant M68K comparison diagnostics.

This module is advisory evidence only. Its output never establishes semantic,
source, or machine-code equality and is not read by the exact verifier.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

from analysis_support import K, ROOT, decoder, instruction, basic
from common import FormatError, sha256
from compiler_oracle import cached
from check_function import validated_function

SCHEMA_VERSION = 1


def _decode(raw: bytes, data_spans=()):
    """Decode a complete byte extent, refusing partial/invalid instruction streams."""
    md = decoder()
    spans = sorted((int(a), int(b)) for a, b in data_spans)
    out, pc, si = [], 0, 0
    while pc < len(raw):
        while si < len(spans) and pc == spans[si][0]:
            if spans[si][1] <= pc or spans[si][1] > len(raw):
                return None, dict(offset=pc, reason='INVALID_DATA_SPAN')
            pc = spans[si][1]
            si += 1
        if si < len(spans) and spans[si][0] < pc < spans[si][1]:
            return None, dict(offset=pc, reason='OVERLAPPING_DATA_SPAN')
        ins = instruction(md, raw, pc)
        if ins is None:
            return None, dict(offset=pc, reason='UNDECODABLE_OR_TRUNCATED')
        out.append(ins)
        pc += ins.size
    if si < len(spans):
        return None, dict(offset=spans[si][0], reason='UNCONSUMED_DATA_SPAN')
    return out, None


def _mnemonic(ins):
    return ins.mnemonic.lower()


def _stem(ins):
    # Keep operation families alignable when the width suffix is itself the
    # hypothesis under review (move.w vs move.l, etc.).
    return _mnemonic(ins).split('.', 1)[0]


def _operand_shape(ins):
    shapes = []
    for op in ins.operands:
        if op.type == K.M68K_OP_REG:
            shapes.append(('reg',))
        elif op.type == K.M68K_OP_IMM:
            shapes.append(('imm',))
        elif op.type == K.M68K_OP_MEM:
            shapes.append(('mem', int(op.address_mode)))
        elif op.type == K.M68K_OP_BR_DISP:
            shapes.append(('branch',))
        else:
            shapes.append(('other', int(op.type)))
    return tuple(shapes)


def _token(ins):
    return (_stem(ins), _operand_shape(ins))


def _branch_target(ins):
    if not _is_branch(ins):
        return None
    if not ins.operands:
        return None
    op = ins.operands[-1]
    if op.type == K.M68K_OP_BR_DISP:
        return int(ins.address) + 2 + int(op.br_disp.disp)
    if op.type == K.M68K_OP_MEM and op.address_mode == K.M68K_AM_PCI_DISP:
        return int(ins.address) + 2 + int(op.mem.disp)
    return None


def _is_branch(ins):
    mn = _stem(ins)
    if mn in ('bra', 'jmp') or _is_conditional(mn):
        return True
    return mn in ('dbra', 'dbf') or bool(re.fullmatch(r'db(?:cc|cs|eq|ge|gt|hi|le|ls|lt|mi|ne|pl|t|vc|vs)', mn))


def _is_conditional(mn):
    return bool(re.fullmatch(r'b(?:cc|cs|eq|f|ge|gt|hi|le|ls|lt|mi|ne|pl|t|vc|vs)', mn.split('.', 1)[0]))


def _is_unconditional(ins):
    return _stem(ins) in ('bra', 'jmp')


def _is_return(ins):
    return _stem(ins) in ('rts', 'rte', 'rtr', 'rtm')


def _insn_record(ins):
    return basic(ins)


def _alignment(expected, actual):
    """Coarse instruction alignment which tolerates inserted code and shifts."""
    akeys = [_token(x) for x in expected]
    bkeys = [_token(x) for x in actual]
    matcher = difflib.SequenceMatcher(None, akeys, bkeys, autojunk=False)
    pairs, expected_only, actual_only = [], [], []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for i, j in zip(range(i1, i2), range(j1, j2)):
                pairs.append(dict(expected_index=i, actual_index=j, kind='shape', confidence='coarse'))
        elif tag == 'replace':
            n = min(i2 - i1, j2 - j1)
            for k in range(n):
                pairs.append(dict(expected_index=i1+k, actual_index=j1+k, kind='substitution', confidence='low'))
            expected_only.extend(range(i1+n, i2))
            actual_only.extend(range(j1+n, j2))
        elif tag == 'delete':
            expected_only.extend(range(i1, i2))
        else:
            actual_only.extend(range(j1, j2))
    pairs.sort(key=lambda p: (p['expected_index'], p['actual_index']))
    return pairs, expected_only, actual_only, matcher.ratio()


def _blocks(insns):
    if not insns:
        return [], dict(reason='EMPTY_CODE')
    by_off = {int(i.address): i for i in insns}
    leaders = {int(insns[0].address)}
    for idx, ins in enumerate(insns):
        mn = _mnemonic(ins)
        target = _branch_target(ins)
        if target is not None:
            if target not in by_off:
                return None, dict(offset=int(ins.address), target=target, reason='CONTROL_TARGET_OUTSIDE_DECODED_EXTENT')
            leaders.add(target)
        if (_is_branch(ins) or _is_return(ins)) and idx + 1 < len(insns):
            leaders.add(int(insns[idx+1].address))
    sorted_leaders = sorted(leaders)
    result = []
    for i, start in enumerate(sorted_leaders):
        end = sorted_leaders[i+1] if i+1 < len(sorted_leaders) else int(insns[-1].address)+int(insns[-1].size)
        members = [x for x in insns if start <= int(x.address) < end]
        if not members:
            return None, dict(offset=start, reason='EMPTY_BLOCK')
        last = members[-1]
        target = _branch_target(last)
        mn = _mnemonic(last)
        term = ('return' if _is_return(last) else 'jump' if _is_unconditional(last) else
                'branch' if _is_branch(last) else None)
        result.append(dict(start=start, end=end, instructions=members, terminator=term, condition=mn.split('.', 1)[0] if term == 'branch' else None,
                           target=target, fallthrough=(not _is_unconditional(last) and not _is_return(last))))
    return result, None


def _registers(ins):
    regs = set()
    for op in ins.operands:
        if op.type == K.M68K_OP_REG:
            regs.add(ins.reg_name(op.reg))
        elif op.type == K.M68K_OP_MEM:
            for r in (op.mem.base_reg, op.mem.index_reg):
                if r:
                    regs.add(ins.reg_name(r))
    return regs


def _register_roles(ins):
    """Ordered register use, retaining operand position and addressing role."""
    out = []
    for i, op in enumerate(ins.operands):
        if op.type == K.M68K_OP_REG:
            out.append((i, 'operand', ins.reg_name(op.reg)))
        elif op.type == K.M68K_OP_MEM:
            if op.mem.base_reg:
                out.append((i, 'base', ins.reg_name(op.mem.base_reg)))
            if op.mem.index_reg:
                out.append((i, 'index', ins.reg_name(op.mem.index_reg)))
    return out


_READ_ONLY_STEMS = {'cmp', 'cmpa', 'cmpi', 'cmpm', 'tst', 'btst', 'pea', 'jsr', 'jmp', 'bsr', 'chk'}
_SINGLE_OPERAND_WRITERS = {'clr', 'ext', 'extb', 'swap', 'neg', 'negx', 'not', 'st', 'sf', 'seq', 'sne',
                           'scc', 'scs', 'sge', 'sgt', 'shi', 'sle', 'sls', 'slt', 'smi', 'spl', 'svc', 'svs'}


def _register_def_use(ins):
    """Approximate syntactic register writes/reads for one instruction.

    The last register operand of a multi-operand instruction and the register
    operand of a known single-operand writer count as a write. Everything else,
    including address base/index registers, counts as a read. Read-modify-write,
    implicit, predecrement/postincrement and MOVEM effects are ignored. This is
    a coarse count, never a liveness or dataflow proof.
    """
    stem = _stem(ins)
    defs, uses = [], []
    ops = list(ins.operands)
    for i, op in enumerate(ops):
        if op.type == K.M68K_OP_REG:
            name = ins.reg_name(op.reg)
            write = stem not in _READ_ONLY_STEMS and (
                (len(ops) > 1 and i == len(ops) - 1) or (len(ops) == 1 and stem in _SINGLE_OPERAND_WRITERS))
            (defs if write else uses).append(name)
        elif op.type == K.M68K_OP_MEM:
            for r in (op.mem.base_reg, op.mem.index_reg):
                if r:
                    uses.append(ins.reg_name(r))
    return defs, uses


def _def_use_summary(stream):
    out = {}
    for ins in stream:
        defs, uses = _register_def_use(ins)
        for kind, names in (('writes', defs), ('reads', uses)):
            for name in names:
                cur = out.setdefault(name, dict(writes=0, reads=0, first_offset=int(ins.address)))
                cur[kind] += 1
    return {k: out[k] for k in sorted(out)}


def register_trace(expected, actual, pairs):
    """Advisory first register divergence and original->candidate mapping.

    Walks aligned pairs in expected order. Only pairs with the same operation
    stem and identical (operand position, role) structure contribute register
    correspondences; other pairs are counted as structurally incomparable.
    A mapping conflict is recorded when one original register corresponds to
    more than one candidate register, or one candidate register to more than
    one original register. None of this proves allocation, liveness or intent.
    """
    mapping, reverse, first_div, first_conflict = {}, {}, None, None
    comparable = incomparable = 0
    for n, p in enumerate(pairs):
        e, a = expected[p['expected_index']], actual[p['actual_index']]
        eroles, aroles = _register_roles(e), _register_roles(a)
        if not eroles and not aroles:
            continue
        if _stem(e) != _stem(a) or [r[:2] for r in eroles] != [r[:2] for r in aroles]:
            incomparable += 1
            continue
        comparable += 1
        if first_div is None and eroles != aroles:
            first_div = dict(pair_index=n, expected=_insn_record(e), actual=_insn_record(a),
                             expected_roles=[list(r) for r in eroles], actual_roles=[list(r) for r in aroles])
        for (pos, role, ereg), (_, _, areg) in zip(eroles, aroles):
            entry = mapping.setdefault(ereg, {})
            if areg not in entry:
                entry[areg] = dict(count=0, first_expected_offset=int(e.address), first_actual_offset=int(a.address))
            entry[areg]['count'] += 1
            sources = reverse.setdefault(areg, [])
            if ereg not in sources:
                sources.append(ereg)
            if first_conflict is None and (len(entry) > 1 or len(sources) > 1):
                kind = 'original_maps_to_multiple_candidates' if len(entry) > 1 else 'candidate_maps_from_multiple_originals'
                first_conflict = dict(kind=kind, pair_index=n, original=ereg, candidate=areg, operand=pos, role=role,
                                      previous=(sorted(x for x in entry if x != areg) if len(entry) > 1
                                                else [x for x in sources if x != ereg]),
                                      expected=_insn_record(e), actual=_insn_record(a))
    table = []
    for ereg in sorted(mapping):
        for areg in sorted(mapping[ereg]):
            table.append(dict(original=ereg, candidate=areg, consistent=len(mapping[ereg]) == 1 and len(reverse[areg]) == 1,
                              **mapping[ereg][areg]))
    return dict(claim='ADVISORY_REGISTER_CORRESPONDENCE_NO_ALLOCATION_OR_LIVENESS_CLAIM',
                comparable_pairs=comparable, structurally_incomparable_pairs=incomparable,
                first_divergence=first_div, mapping=table, first_conflict=first_conflict,
                def_use=dict(method='APPROXIMATE_SYNTACTIC_COUNTS', expected=_def_use_summary(expected),
                             actual=_def_use_summary(actual)))


def _mem_layout(op):
    return (int(op.address_mode), int(op.mem.base_reg), int(op.mem.index_reg),
            int(op.mem.scale), int(op.mem.disp))


# ---------------------------------------------------------------------------
# Reference identity.
#
# Diagnostics only consume identities that an existing proof path already
# accepts. Nothing here guesses a binding from a displacement, a printable run
# or a numeric container name that the exact verifier would not accept.
# ---------------------------------------------------------------------------

IDENTITY_STATES = ('same_identity', 'layout_only', 'different_identity', 'unresolved')
SOURCE_SHAPE_CATEGORIES = frozenset({
    'operand_width', 'register_assignment', 'frame_or_stack_reference', 'immediate_constant',
    'instruction_layout', 'branch_condition_or_kind', 'control_flow_target_or_edge',
    'control_flow_unresolved', 'control_flow_shape', 'unknown_codegen'})
BINDING_CATEGORIES = frozenset({
    'a4_global_layout', 'pc_relative_layout', 'memory_reference_or_layout',
    'call_target_or_encoding', 'data_ownership_review'})
IDENTITY_SOURCES = (
    dict(id='ledger_a4_bias', side='original', proof_level='OBSERVED_RELOCATION',
         where='evidence/functions/ledger.json a4 (startup LEA HUNK_RELOC32 to DATA+bias)'),
    dict(id='ledger_referenced_data', side='original', proof_level='OBSERVED_FUNCTION_EVIDENCE',
         where='ledger function referenced_data (A4_RELATIVE hunk/offset per instruction)'),
    dict(id='ledger_direct_callees', side='original', proof_level='OBSERVED_FUNCTION_EVIDENCE',
         where='ledger function direct_callees (site -> callee hunk/offset, recorded basis)'),
    dict(id='ledger_relocations', side='original', proof_level='OBSERVED_RELOCATION',
         where='ledger function relocations (HUNK_RELOC32 target hunk/addend)'),
    dict(id='candidate_link_map', side='candidate', proof_level='COMPILER_OUTPUT',
         where='cached compile contribution symbols/relocations/all_relocations and linked .exe startup A4 LEA'),
    dict(id='mechanical_proxy_name', side='binding', proof_level='FUNCTION_CODE_MATCH_RULE',
         where='function_compare.mechanical/target_identity: [GF]_hNN_HEX names the original hunk/offset'),
    dict(id='runtime_aliases', side='binding', proof_level='RUNTIME_CONTRIBUTION_BYTE_PROOF',
         where='evidence/experiments/runtime-arithmetic.json via runtime_arithmetic.aliases'),
    dict(id='recovered_function_ids', side='binding', proof_level='FUNCTION_CODE_MATCH',
         where='docs/symbols.json recovered_functions: exact-verified id -> hunk/start'),
    dict(id='exact_proof_bindings', side='corroboration', proof_level='FUNCTION_CODE_MATCH',
         where='recovery/proofs/*.json relocation_proof symbol -> identity'),
)


def _a4_reg():
    return getattr(K, 'M68K_REG_A4', 0)


def _reference_operands(ins):
    """Reference-bearing operand indices and kinds for one instruction."""
    out = {}
    stem = _stem(ins)
    for i, op in enumerate(ins.operands):
        if op.type == K.M68K_OP_MEM:
            if op.address_mode == K.M68K_AM_REGI_ADDR_DISP and op.mem.base_reg == _a4_reg() and _a4_reg():
                out[i] = 'a4'
            elif op.address_mode == K.M68K_AM_PCI_DISP:
                out[i] = 'call_pc' if stem in ('bsr', 'jsr') else 'pc'
            elif op.address_mode == K.M68K_AM_ABSOLUTE_DATA_LONG:
                # Absolute short addresses cannot carry a HUNK_RELOC32 and so
                # have no link identity; they stay ordinary operand bytes.
                out[i] = 'absolute'
        elif op.type == K.M68K_OP_BR_DISP and stem == 'bsr':
            out[i] = 'call_pc'
    return out


def _field(ins, op, kind):
    """(start, width) of the operand's displacement field inside the instruction."""
    from function_compare import unique_word_site
    if op.type == K.M68K_OP_BR_DISP:
        if ins.size == 2:
            return 1, 1
        if ins.size == 4:
            return 2, 2
        return None
    if kind in ('a4', 'pc', 'call_pc'):
        site = unique_word_site(ins, op.mem.disp)
        return (site, 2) if site is not None else None
    return None


class ReferenceResolver:
    """Resolve A4, PC-relative and call references through established bindings.

    Original side: ledger evidence only (A4 bias, referenced_data,
    direct_callees, relocations). Candidate side: the cached compile's own
    linked symbol map and relocations, bound to an original identity only by
    rules the exact verifier already accepts. Unresolved stays unresolved.
    """

    def __init__(self, f, ledger, compiled, source_text=None, root=ROOT):
        from function_compare import target_identity, overlay_trampoline_identity
        self._target_identity = target_identity
        self._trampoline = overlay_trampoline_identity
        self.f = f
        self.start = int(f['start'])
        self.notes = []
        a4 = (ledger or {}).get('a4') or {}
        rel = (a4.get('evidence') or {}).get('relocation') or {}
        self.a4_bias = a4.get('bias') if rel.get('target_hunk') == 1 and rel.get('addend_raw') == a4.get('bias') else None
        if self.a4_bias is None:
            self.notes.append('ORIGINAL_A4_BIAS_NOT_BACKED_BY_LEDGER_RELOCATION')
        self.refdata = {}
        for r in f.get('referenced_data', []):
            self.refdata.setdefault(int(r['instruction_offset']), []).append(r)
        self.callees = {int(c['site']): c for c in f.get('direct_callees', []) if 'site' in c}
        self.orig_relocs = {int(r['relative_offset']): r for r in f.get('relocations', []) if 'relative_offset' in r}
        c = compiled['contribution']
        self.c = c
        symbol_map = [dict(s) for s in c.get('symbols', [])]
        hunks = {h['number']: h for h in c.get('hunks', [])}
        data_hunk, bss_hunk = hunks.get(1), hunks.get(2)
        org = next((s['offset'] for s in symbol_map if s['name'] == '__H2_org'), None)
        # Same folded-COMMON convention the exact verifier checks.
        if data_hunk and bss_hunk and org == data_hunk['initialized_size'] and bss_hunk['allocated_size'] == 4:
            for s in symbol_map:
                if s['hunk'] == 2 and org <= s['offset'] < data_hunk['allocated_size']:
                    s['hunk'] = 1
        if source_text is None and compiled.get('directory') and compiled.get('prefix'):
            p = Path(compiled['directory']) / (compiled['prefix'] + '.c')
            source_text = p.read_text() if p.exists() else ''
        source_text = source_text or ''
        profile = (compiled.get('identity') or {}).get('profile')
        int_size = 2 if profile in ('aztec36', 'aztec36-x3', 'aztec36-large-data', 'aztec50-short') else 4
        self.bounds = {}
        for m in re.finditer(r'extern\s+(?:(?:signed|unsigned)\s+)?(char|short|int|long|float|double)\s+(\**)(\w+)(?:\[(\d+)\])?\s*;', source_text):
            width = 4 if m[2] else dict(char=1, short=2, int=int_size, long=4, float=4, double=8)[m[1]]
            self.bounds['_' + m[3]] = width * int(m[4] or 1)
        for m in re.finditer(r'extern\s+struct\s+\w+\s+(\w+)(?:\[\d+\])?\s*;', source_text):
            s = next((s for s in symbol_map if s['name'] == '_' + m[1] and s['hunk'] == 1), None)
            if s and data_hunk:
                end = min((t['offset'] for t in symbol_map if t['hunk'] == 1 and t['offset'] > s['offset']),
                          default=data_hunk['allocated_size'])
                self.bounds[s['name']] = end - s['offset']
        # Recovered function ids are exact-verified hunk/start identities.
        self.recovered = {}
        try:
            for r in json.loads((root / 'docs' / 'symbols.json').read_text()).get('recovered_functions', []):
                if r.get('state') == 'FUNCTION_CODE_MATCH':
                    self.recovered['_' + r['id']] = (int(r['hunk']), int(r['start']))
        except (OSError, ValueError, KeyError, TypeError):
            self.notes.append('RECOVERED_FUNCTION_IDS_UNAVAILABLE')
        # Runtime aliases need the same byte proofs the exact verifier uses.
        self.runtime = []
        blob = None
        if compiled.get('directory') and compiled.get('prefix'):
            exe = Path(compiled['directory']) / (compiled['prefix'] + '.exe')
            blob = exe.read_bytes() if exe.exists() else None
        rpath = root / 'evidence' / 'experiments' / 'runtime-arithmetic.json'
        if blob is not None and rpath.exists():
            try:
                from function_compare import runtime_symbol_names
                revidence = json.loads(rpath.read_text())
                if any(s['name'] in runtime_symbol_names(revidence) for s in c.get('symbols', [])):
                    from analysis_support import game
                    from runtime_arithmetic import aliases
                    original, model, _ = game()
                    self.runtime, _ = aliases(compiled, blob, original, model, revidence)
                    symbol_map.extend(self.runtime)
            except Exception as exc:  # advisory: never let alias failure invent identities
                self.notes.append('RUNTIME_ALIAS_UNAVAILABLE: ' + type(exc).__name__)
        self.symbol_map = symbol_map
        self.candidate_a4 = None
        root_hunk = hunks.get(0)
        if blob is not None and root_hunk is not None:
            for r in c.get('all_relocations', []):
                p = root_hunk['content_offset'] + r['source_offset']
                if (r['source_hunk'] == 0 and r['target_hunk'] == 1 and blob[p-2:p] == bytes.fromhex('49f9')
                        and blob[p+4:p+6] == bytes.fromhex('4e75')):
                    self.candidate_a4 = r['addend_raw']
        if self.candidate_a4 is None:
            self.notes.append('CANDIDATE_A4_BASE_UNPROVEN')
        self.cand_relocs = {int(r['relative_offset']): r for r in c.get('relocations', []) if 'relative_offset' in r}
        self.proof_bindings = set()
        pdir = root / 'recovery' / 'proofs'
        if pdir.is_dir():
            for p in sorted(pdir.glob('*.json')):
                try:
                    for pr in json.loads(p.read_text()).get('relocation_proof', []):
                        ident = pr.get('identity') or {}
                        if ident.get('symbol') is not None:
                            self.proof_bindings.add((ident['symbol'], int(ident['hunk']), int(ident['offset'])))
                except (OSError, ValueError, TypeError, KeyError, AttributeError):
                    continue

    # -- binding -----------------------------------------------------------
    def _bind(self, hunk, offset, function=False):
        """Candidate linked location -> original identity, or (None, reason)."""
        ident = self._target_identity(hunk, offset, self.symbol_map, None if function else self.bounds)
        if ident is not None:
            key = (ident['hunk'], ident['offset'])
            basis = ('exact_proof_bindings' if (ident['symbol'], key[0], key[1]) in self.proof_bindings
                     else 'runtime_aliases' if any(s['name'] == ident['symbol'] for s in self.runtime)
                     else 'mechanical_proxy_name')
            return dict(key=key, symbol=ident['symbol'], addend=ident['addend'], basis=basis), None
        exact = [s for s in self.symbol_map if s['hunk'] == hunk and s['offset'] == offset]
        for s in exact:
            if s['name'] in self.recovered:
                return dict(key=self.recovered[s['name']], symbol=s['name'], addend=0,
                            basis='recovered_function_ids'), None
        if exact:
            return None, 'CANDIDATE_SYMBOL_HAS_NO_ESTABLISHED_ORIGINAL_BINDING:' + exact[0]['name']
        return None, 'CANDIDATE_LOCATION_HAS_NO_BINDABLE_SYMBOL'

    def expected(self, ins, i, kind):
        op = ins.operands[i]
        site = self.start + int(ins.address)
        stem = _stem(ins)
        if stem in ('jsr', 'jmp', 'pea', 'bsr') and site in self.callees:
            call = self.callees[site]
            return dict(key=(int(call['hunk']), int(call['offset'])), symbol=call.get('id'),
                        basis='ledger_direct_callees:' + str(call.get('basis'))), None
        if kind == 'a4':
            if self.a4_bias is None:
                return None, 'ORIGINAL_A4_BIAS_UNPROVEN'
            key = (1, self.a4_bias + int(op.mem.disp))
            if any((int(r['hunk']), int(r['offset'])) == key for r in self.refdata.get(site, [])):
                return dict(key=key, symbol=None, basis='ledger_referenced_data'), None
            return None, 'ORIGINAL_A4_REFERENCE_NOT_IN_LEDGER'
        if kind == 'absolute':
            hits = [r for off, r in self.orig_relocs.items() if int(ins.address) <= off < int(ins.address) + int(ins.size)]
            if len(hits) == 1:
                return dict(key=(int(hits[0]['target_hunk']), int(hits[0]['addend_raw'])), symbol=None,
                            basis='ledger_relocations'), None
            return None, 'ORIGINAL_ABSOLUTE_RELOCATION_NOT_UNIQUE'
        if kind == 'call_pc':
            return None, 'ORIGINAL_CALL_SITE_NOT_IN_LEDGER'
        return None, 'PC_RELATIVE_DATA_IDENTITY_NOT_ESTABLISHED'

    def actual(self, ins, i, kind):
        op = ins.operands[i]
        stem = _stem(ins)
        if kind == 'a4':
            if self.candidate_a4 is None:
                return None, 'CANDIDATE_A4_BASE_UNPROVEN'
            loc = self.candidate_a4 + int(op.mem.disp)
            ident, why = self._bind(1, loc)
            if ident is None and stem in ('jsr', 'jmp', 'pea'):
                rr = next((r for r in self.c.get('all_relocations', [])
                           if r['source_hunk'] == 1 and r['source_offset'] == loc + 2), None)
                if rr:
                    ident, why = self._bind(rr['target_hunk'], rr['addend_raw'], function=True)
                    if ident: ident['basis'] += '+candidate_a4_stub_relocation'
                if ident is None:
                    t = self._trampoline(self.c, loc, self.symbol_map, self.bounds)
                    if t:
                        ident = dict(key=(t['hunk'], t['offset']), symbol=t['symbol'], addend=t['addend'],
                                     basis='mechanical_proxy_name+overlay_trampoline')
            return ident, why
        if kind == 'absolute':
            hits = [r for off, r in self.cand_relocs.items() if int(ins.address) <= off < int(ins.address) + int(ins.size)]
            if len(hits) != 1:
                return None, 'CANDIDATE_ABSOLUTE_RELOCATION_NOT_UNIQUE'
            return self._bind(hits[0]['target_hunk'], hits[0]['addend_raw'])
        if kind == 'call_pc':
            disp = int(op.br_disp.disp) if op.type == K.M68K_OP_BR_DISP else int(op.mem.disp)
            target = int(self.c.get('code_offset', 0)) + int(ins.address) + 2 + disp
            if target == int(self.c.get('code_offset', 0)):
                # Recursive call to the one-function object's own entry.
                call = next((c for c in self.f.get('direct_callees', []) if c.get('id') == self.f.get('id')), None)
                if call:
                    return dict(key=(int(call['hunk']), int(call['offset'])), symbol='SELF_ENTRY',
                                basis='candidate_link_map:self_entry'), None
            return self._bind(self.c['hunk'], target, function=True)
        return None, 'PC_RELATIVE_DATA_IDENTITY_NOT_ESTABLISHED'


def _classify_references(e, a, resolver):
    """Classify every paired reference operand; see IDENTITY_STATES."""
    eref, aref = _reference_operands(e), _reference_operands(a)
    out = []
    for i in sorted(set(eref) & set(aref)):
        if eref[i] != aref[i]:
            continue
        kind = eref[i]
        eo, ao = e.operands[i], a.operands[i]
        same_encoding = _operand_encoding(eo) == _operand_encoding(ao)
        if resolver is None:
            ei, ew, ai, aw = None, 'NO_IDENTITY_CONTEXT', None, 'NO_IDENTITY_CONTEXT'
        else:
            ei, ew = resolver.expected(e, i, kind)
            ai, aw = resolver.actual(a, i, kind)
        if ei and ai:
            state = ('different_identity' if ei['key'] != ai['key'] else
                     'same_identity' if same_encoding else 'layout_only')
        else:
            state = 'unresolved'
        obs = dict(operand=i, kind=kind, state=state, expected_offset=int(e.address), actual_offset=int(a.address))
        if ei: obs['expected_identity'] = dict(hunk=ei['key'][0], offset=ei['key'][1], basis=ei['basis'])
        if ai: obs['actual_identity'] = dict(hunk=ai['key'][0], offset=ai['key'][1], symbol=ai.get('symbol'), basis=ai['basis'])
        reasons = [w for w in (None if ei else 'expected:' + ew, None if ai else 'actual:' + aw) if w]
        if reasons: obs['unresolved_reasons'] = reasons
        if state in ('same_identity', 'layout_only'):
            ef, af = _field(e, eo, kind), _field(a, ao, kind)
            obs['_patch'] = (ef, af) if ef and af and ef == af else None
        out.append(obs)
    return out


def _operand_encoding(op):
    if op.type == K.M68K_OP_MEM:
        return _mem_layout(op)
    if op.type == K.M68K_OP_BR_DISP:
        return ('br', int(op.br_disp.disp))
    return (int(op.type),)


def _reference_normalized(e, a, refs):
    """True when patching resolved same-identity fields makes the bytes equal."""
    raw = bytearray(bytes(a.bytes))
    exp = bytes(e.bytes)
    if len(raw) != len(exp):
        return False
    for obs in refs:
        if obs['state'] not in ('same_identity', 'layout_only'):
            continue
        patch = obs.get('_patch')
        if not patch:
            return False
        (start, width), _ = patch
        raw[start:start+width] = exp[start:start+width]
    return bytes(raw) == exp


def _hypotheses(expected, actual, pairs, expected_only, actual_only, exp_blocks, act_blocks, resolver=None,
                reference_log=None):
    counts = {}
    examples = {}
    def add(kind, confidence, exp=None, act=None, note=None, identity_state=None):
        cur = counts.setdefault(kind, dict(category=kind, count=0, confidence=confidence, evidence=[]))
        cur['count'] += 1
        if identity_state:
            states = cur.setdefault('identity_states', {})
            states[identity_state] = states.get(identity_state, 0) + 1
        if len(cur['evidence']) < 4:
            item = {}
            if exp is not None: item['expected'] = _insn_record(exp)
            if act is not None: item['actual'] = _insn_record(act)
            if note: item['note'] = note
            cur['evidence'].append(item)
    def worst(refs):
        states = {r['state'] for r in refs}
        return 'different_identity' if 'different_identity' in states else 'unresolved' if 'unresolved' in states else None
    for p in pairs:
        e, a = expected[p['expected_index']], actual[p['actual_index']]
        refs = _classify_references(e, a, resolver)
        if reference_log is not None:
            reference_log.extend(refs)
        resolved_ops = {r['operand'] for r in refs if r['state'] in ('same_identity', 'layout_only')}
        conflicting = [r for r in refs if r['state'] == 'different_identity']
        if bytes(e.bytes) == bytes(a.bytes):
            for r in conflicting:
                cat = ('call_target_or_encoding' if _stem(e) in ('bsr', 'jsr') else
                       'a4_global_layout' if r['kind'] == 'a4' else
                       'pc_relative_layout' if r['kind'] == 'pc' else 'memory_reference_or_layout')
                add(cat, 'medium', e, a, 'Identical encoding binds to a different established identity.',
                    identity_state='different_identity')
            continue
        if refs and all(r['state'] in ('same_identity', 'layout_only') for r in refs) and _reference_normalized(e, a, refs):
            # Only resolved same-identity displacement fields differ.
            continue
        before_count = sum(x['count'] for x in counts.values())
        if _is_branch(e) and _is_branch(a) and _mnemonic(e).split('.', 1)[0] != _mnemonic(a).split('.', 1)[0]:
            add('branch_condition_or_kind', 'medium', e, a,
                'Branch opcode/condition differs; matching target addresses would not prove matching edges.')
        if _mnemonic(e) != _mnemonic(a) and _stem(e) == _stem(a):
            add('operand_width', 'low', e, a, 'Mnemonic width suffix differs; this is a code-shape observation.')
        er, ar = _registers(e), _registers(a)
        eroles, aroles = _register_roles(e), _register_roles(a)
        if (er != ar or eroles != aroles) and _stem(e) == _stem(a):
            add('register_assignment', 'low', e, a,
                'Ordered register roles differ; register allocation or operand lifetime is a hypothesis, not a source claim.')
        frame_regs = tuple(r for r in (getattr(K, 'M68K_REG_A5', 0), getattr(K, 'M68K_REG_A6', 0), K.M68K_REG_A7) if r)
        frame_e = [o for o in e.operands if o.type == K.M68K_OP_MEM and o.mem.base_reg in frame_regs]
        frame_a = [o for o in a.operands if o.type == K.M68K_OP_MEM and o.mem.base_reg in frame_regs]
        if frame_e or frame_a:
            if [(o.mem.base_reg, o.mem.disp, o.address_mode) for o in frame_e] != [(o.mem.base_reg, o.mem.disp, o.address_mode) for o in frame_a]:
                add('frame_or_stack_reference', 'low', e, a, 'Frame-relative operand differs; slot ownership is unproved.')
        if bytes(e.bytes) != bytes(a.bytes):
            if _stem(e) in ('bsr', 'jsr') or _stem(a) in ('bsr', 'jsr'):
                call_refs = [r for r in refs if r['kind'] in ('a4', 'call_pc', 'absolute')]
                state = worst(call_refs) or ('unresolved' if not call_refs else None)
                if state is None and _mnemonic(e) == _mnemonic(a) and _reference_normalized(e, a, call_refs):
                    pass
                else:
                    add('call_target_or_encoding', 'low', e, a,
                        'Call binds to a different established callee identity.' if state == 'different_identity' else
                        'Call encoding/target differs; callee identity is unresolved.' if state == 'unresolved' else
                        'Call encoding differs although the callee identity resolves identically.',
                        identity_state=state or 'encoding_only')
            else:
                em = [(i, o) for i, o in enumerate(e.operands) if o.type == K.M68K_OP_MEM]
                am = [(i, o) for i, o in enumerate(a.operands) if o.type == K.M68K_OP_MEM]
                mem_diffs = []
                for (ei_, eo), (ai_, ao) in zip(em, am):
                    if ei_ == ai_ and ei_ in resolved_ops:
                        continue  # established same identity; only link layout differs
                    if _mem_layout(eo) != _mem_layout(ao):
                        # Base/index register changes are handled as register
                        # assignment hypotheses. A layout hypothesis needs a
                        # changed displacement or addressing mode.
                        if eo.address_mode != ao.address_mode or eo.mem.disp != ao.mem.disp:
                            mem_diffs.append((ei_, eo, ao))
                by_op = {r['operand']: r['state'] for r in refs}
                a4 = _a4_reg()
                a4_diffs = [i for i, eo, ao in mem_diffs if eo.mem.base_reg == ao.mem.base_reg == a4]
                pc_diffs = [i for i, eo, ao in mem_diffs if eo.address_mode == K.M68K_AM_PCI_DISP
                            and ao.address_mode == K.M68K_AM_PCI_DISP and eo.mem.disp != ao.mem.disp]
                if a4_diffs:
                    state = 'different_identity' if any(by_op.get(i) == 'different_identity' for i in a4_diffs) else 'unresolved'
                    add('a4_global_layout', 'low', e, a,
                        'A4 reference binds to a different established identity.' if state == 'different_identity' else
                        'A4-relative displacement/addressing mode differs; symbol identity is unresolved.',
                        identity_state=state)
                elif pc_diffs:
                    state = 'different_identity' if any(by_op.get(i) == 'different_identity' for i in pc_diffs) else 'unresolved'
                    add('pc_relative_layout', 'low', e, a, 'PC-relative displacement differs; data-vs-control target is not inferred.',
                        identity_state=state)
                elif [x for x in mem_diffs if x[1].mem.base_reg not in frame_regs or x[2].mem.base_reg not in frame_regs]:
                    # Frame-slot displacements are already source-shape
                    # observations (frame_or_stack_reference), not bindings.
                    state = 'different_identity' if any(by_op.get(i) == 'different_identity' for i, _, _ in mem_diffs) else 'unresolved'
                    add('memory_reference_or_layout', 'low', e, a, 'Memory displacement/addressing mode differs; ownership is unresolved.',
                        identity_state=state)
                if any(eo.imm != ao.imm for eo, ao in zip(
                        [o for o in e.operands if o.type == K.M68K_OP_IMM],
                        [o for o in a.operands if o.type == K.M68K_OP_IMM])):
                    add('immediate_constant', 'low', e, a, 'Immediate value differs; semantic role is unknown.')
        after_count = sum(x['count'] for x in counts.values())
        if bytes(e.bytes) != bytes(a.bytes) and before_count == after_count and not (_is_branch(e) and _is_branch(a)):
            add('unknown_codegen', 'low', e, a,
                'Bytes differ without a classified operand change; retain this as unexplained code generation evidence.')
    if expected_only or actual_only:
        add('instruction_layout', 'medium', note='Unpaired instructions remain after shift-tolerant alignment.')
    if exp_blocks is None or act_blocks is None:
        add('control_flow_unresolved', 'low', note='At least one stream did not yield a fully bounded direct-target CFG.')
    else:
        if len(exp_blocks) != len(act_blocks):
            add('control_flow_shape', 'medium', note='Basic-block counts differ; block correspondence is incomplete.')
    return [counts[k] for k in sorted(counts)]


def _group(category):
    if category in BINDING_CATEGORIES:
        return 'binding_or_layout'
    if category in SOURCE_SHAPE_CATEGORIES:
        return 'source_shape'
    return 'unclassified'


def _group_hypotheses(hypotheses):
    groups = dict(source_shape={}, binding_or_layout={}, unclassified={})
    for h in hypotheses:
        h['group'] = _group(h['category'])
        groups[h['group']][h['category']] = h['count']
    return {k: dict(categories=v, total=sum(v.values())) for k, v in groups.items()}


def _reference_summary(log, resolver, max_examples=12):
    counts = {s: 0 for s in IDENTITY_STATES}
    by_kind, reasons, examples = {}, {}, []
    for obs in log:
        counts[obs['state']] += 1
        k = by_kind.setdefault(obs['kind'], {s: 0 for s in IDENTITY_STATES})
        k[obs['state']] += 1
        for r in obs.get('unresolved_reasons', []):
            key = r.split(':', 2)[0] + ':' + r.split(':', 2)[1] if ':' in r else r
            reasons[key] = reasons.get(key, 0) + 1
        if obs['state'] in ('different_identity', 'unresolved') and len(examples) < max_examples:
            examples.append({k: v for k, v in obs.items() if not k.startswith('_')})
    out = dict(claim='ADVISORY_IDENTITY_FROM_ESTABLISHED_BINDINGS_ONLY_NO_EQUALITY_CLAIM',
               context='ESTABLISHED_BINDINGS' if resolver is not None else 'NONE_BYTES_ONLY',
               counts=counts, by_kind={k: by_kind[k] for k in sorted(by_kind)},
               unresolved_reasons={k: reasons[k] for k in sorted(reasons)},
               nonmatching_examples=examples,
               hypothesis_exclusion='same_identity and layout_only observations are not counted as hypotheses')
    if resolver is not None:
        out['sources'] = [dict(s) for s in IDENTITY_SOURCES]
        out['candidate_a4_base'] = resolver.candidate_a4
        out['original_a4_bias'] = resolver.a4_bias
        out['resolver_notes'] = list(resolver.notes)
    return out


def compare_code(expected_bytes: bytes, actual_bytes: bytes, *, data_spans=(), resolver=None):
    """Compare two explicit extents for diagnostic guidance only.

    ``data_spans`` applies only to the expected stream. Candidate literal/data
    boundaries are not inferred. If expected evidence contains data, callers
    must independently supply a corresponding mapped candidate span or retain
    the unsupported result. ``resolver`` optionally supplies established
    reference identities (see ``ReferenceResolver``); without it every
    reference remains ``unresolved``.
    """
    if data_spans:
        return dict(schema_version=SCHEMA_VERSION, status='UNSUPPORTED',
                    claim='DIAGNOSTIC_ONLY_NO_EQUALITY_OR_SEMANTIC_CLAIM',
                    reason='DATA_SPAN_MAPPING_REQUIRED_FOR_BOTH_STREAMS',
                    expected_extent=dict(bytes=len(expected_bytes)), actual_extent=dict(bytes=len(actual_bytes)),
                    alignment=None, blocks=None, hypotheses=[])
    exp, exp_bad = _decode(expected_bytes)
    act, act_bad = _decode(actual_bytes)
    base = dict(schema_version=SCHEMA_VERSION, claim='DIAGNOSTIC_ONLY_NO_EQUALITY_OR_SEMANTIC_CLAIM',
                expected_extent=dict(bytes=len(expected_bytes)), actual_extent=dict(bytes=len(actual_bytes)))
    if exp_bad or act_bad:
        base.update(status='UNSUPPORTED', reason='UNDECODABLE_OR_UNMAPPED_DATA_EXTENT',
                    decode=dict(expected=exp_bad, actual=act_bad), alignment=None, blocks=None, hypotheses=[])
        return base
    pairs, eo, ao, ratio = _alignment(exp, act)
    exp_blocks, ebad = _blocks(exp)
    act_blocks, abad = _blocks(act)
    idx_map = {p['expected_index']: p['actual_index'] for p in pairs}
    bpair, bunpaired = [], {'expected': [], 'actual': []}
    if exp_blocks is None or act_blocks is None:
        bunpaired['expected'] = [b['start'] for b in exp_blocks or []]
        bunpaired['actual'] = [b['start'] for b in act_blocks or []]
    else:
        actual_by_start = {b['start']: b for b in act_blocks}
        actual_starts = set(actual_by_start)
        by_exp_start = {b['start']: b for b in exp_blocks}
        by_act_start = {b['start']: b for b in act_blocks}
        paired_starts = {}
        for bi, eb in enumerate(exp_blocks):
            ei = next((i for i, x in enumerate(exp) if int(x.address) == eb['start']), None)
            mapped = idx_map.get(ei) if ei is not None else None
            candidate_start = int(act[mapped].address) if mapped is not None else None
            ab = actual_by_start.get(candidate_start)
            if ab is None:
                bunpaired['expected'].append(eb['start'])
                continue
            paired_starts[eb['start']] = ab['start']
            actual_starts.discard(candidate_start)
            target_state = 'not_applicable'
            if eb['terminator'] != ab['terminator'] or eb['condition'] != ab['condition']:
                target_state = 'different_or_unresolved'
            if eb['target'] is not None or ab['target'] is not None:
                mapped_target = None
                if eb['target'] is not None:
                    target_i = next((i for i, x in enumerate(exp) if int(x.address) == eb['target']), None)
                    ti = idx_map.get(target_i) if target_i is not None else None
                    mapped_target = int(act[ti].address) if ti is not None else None
                target_state = ('consistent' if target_state == 'not_applicable' and mapped_target is not None and mapped_target == ab['target']
                                else 'different_or_unresolved')
            if eb['fallthrough']:
                enext = exp_blocks[bi+1]['start'] if bi+1 < len(exp_blocks) else None
                if enext is not None:
                    ni = next((i for i, x in enumerate(exp) if int(x.address) == enext), None)
                    na = idx_map.get(ni) if ni is not None else None
                    mapped_next = int(act[na].address) if na is not None else None
                    abi = next((i for i, b in enumerate(act_blocks) if b['start'] == ab['start']), None)
                    actual_next = act_blocks[abi+1]['start'] if abi is not None and abi+1 < len(act_blocks) else None
                    if mapped_next is None or actual_next != mapped_next or not ab['fallthrough']:
                        target_state = 'different_or_unresolved'
            bpair.append(dict(expected_start=eb['start'], actual_start=ab['start'],
                              terminators=[eb['terminator'], ab['terminator']], conditions=[eb['condition'], ab['condition']], target_check=target_state,
                              confidence='coarse'))
        bunpaired['actual'] = sorted(actual_starts)
    reference_log = []
    hypotheses = _hypotheses(exp, act, pairs, eo, ao, exp_blocks, act_blocks, resolver, reference_log)
    if any(b.get('target_check') == 'different_or_unresolved' for b in bpair):
        hypotheses.append(dict(category='control_flow_target_or_edge', count=sum(
            b.get('target_check') == 'different_or_unresolved' for b in bpair), confidence='low',
            evidence=[dict(note='Paired block targets, branch conditions, or fallthrough edges do not map cleanly.')]))
        hypotheses.sort(key=lambda h: h['category'])
    hypothesis_groups = _group_hypotheses(hypotheses)
    # Unresolved indirect transfers are surfaced instead of counted as CFG proof.
    indirect = []
    for side, stream in (('expected', exp), ('actual', act)):
        for ins in stream:
            if _stem(ins) in ('jmp', 'jsr') and _branch_target(ins) is None:
                indirect.append(dict(side=side, offset=int(ins.address), instruction=_insn_record(ins)))
    base.update(status='DIAGNOSTIC_ONLY', alignment=dict(instruction_similarity=round(ratio, 4),
        pairs=[dict(expected_offset=int(exp[p['expected_index']].address), actual_offset=int(act[p['actual_index']].address),
                    kind=p['kind'], confidence=p['confidence']) for p in pairs],
        expected_only=[_insn_record(exp[i]) for i in eo], actual_only=[_insn_record(act[i]) for i in ao]),
        blocks=dict(paired=bpair, unpaired=bunpaired, conservative=True,
                    unresolved_edges=dict(expected=ebad, actual=abad), indirect_transfers=indirect),
        hypotheses=hypotheses, hypothesis_groups=hypothesis_groups,
        reference_identity=_reference_summary(reference_log, resolver),
        register_trace=register_trace(exp, act, pairs))
    first_shape = next((p for p in pairs if p['kind'] == 'substitution' or
                        _mnemonic(exp[p['expected_index']]) != _mnemonic(act[p['actual_index']])), None)
    first_unpaired = min([int(exp[i].address) for i in eo] + [int(act[i].address) for i in ao], default=None)
    if first_shape:
        p = first_shape
        base['first_nonreference_divergence'] = dict(expected=_insn_record(exp[p['expected_index']]),
            actual=_insn_record(act[p['actual_index']]), confidence='low',
            note='First coarse-aligned instruction-shape difference; operand reference identity is not evaluated.')
    elif first_unpaired is not None:
        if eo and (not ao or int(exp[eo[0]].address) <= int(act[ao[0]].address)):
            idx = eo[0]
            base['first_nonreference_divergence'] = dict(side='expected', instruction=_insn_record(exp[idx]), confidence='medium',
                note='First unpaired expected instruction after shift-tolerant alignment.')
        else:
            idx = ao[0]
            base['first_nonreference_divergence'] = dict(side='candidate', instruction=_insn_record(act[idx]), confidence='medium',
                note='First unpaired candidate instruction after shift-tolerant alignment.')
    else:
        base['first_nonreference_divergence'] = None
    return base


def diagnose(function_id: str, cache_key: str):
    """Load a closed original function and a validated cached standalone compile."""
    f, ledger = validated_function(function_id)
    compiled = cached(cache_key)
    if compiled is None:
        raise FormatError('compiler cache entry not found: '+cache_key)
    report = dict(schema_version=SCHEMA_VERSION, function=function_id,
                  original_extent=dict(hunk=f['hunk'], start=f['start'], end=f['end'], bytes=f['size'],
                                       extent_status=f['extent_status']),
                  cache_key=cache_key, compiler=compiled.get('identity', {}).get('profile'),
                  diagnostic_sha256=sha256((ROOT/'tools'/'diag.py').read_bytes()),
                  claim='DIAGNOSTIC_ONLY_NO_EQUALITY_OR_SEMANTIC_CLAIM')
    reason = None
    if f.get('extent_status') != 'CLOSED_CFG': reason = 'ORIGINAL_EXTENT_NOT_CLOSED_CFG'
    elif compiled.get('status') != 'COMPILED': reason = 'CACHED_COMPILER_OUTPUT_NOT_COMPILED'
    else:
        c = compiled.get('contribution') or {}
        ident = compiled.get('identity') or {}
        if int(c.get('entry_offset', 0)) != 0: reason = 'CANDIDATE_ENTRY_NOT_AT_OBJECT_START'
        elif len(ident.get('object_labels', ['candidate'])) != 1: reason = 'MULTI_OBJECT_UNIT_UNBOUNDED'
        elif c.get('data_size', 0) or c.get('bss_size', 0): reason = 'CANDIDATE_HAS_UNMAPPED_DATA_OR_BSS'
        elif any(s.get('hunk') == c.get('hunk') and s.get('name') not in ('_recovered', 'recovered')
                 and not re.fullmatch(r'__H\d+_(?:org|end)', s.get('name', ''))
                 and 0 <= s.get('offset', -1) < c.get('code_size', 0) for s in c.get('symbols', [])):
            reason = 'MULTIPLE_OR_UNIDENTIFIED_CODE_SYMBOLS'
    if reason:
        report.update(status='UNSUPPORTED', reason=reason, candidate_extent=None)
        return report
    raw = bytes.fromhex(compiled['contribution']['code_hex'])
    report['candidate_extent'] = dict(bytes=len(raw), hunk=compiled['contribution'].get('hunk'),
                                      entry_offset=compiled['contribution'].get('entry_offset', 0),
                                      boundary='ENTIRE_SINGLE_OBJECT_CODE_PAYLOAD; may include compiler-owned code data')
    if f.get('jump_tables') or any(r.get('kind') == 'PC_RELATIVE_DATA' for r in f.get('referenced_data', [])):
        report.update(status='UNSUPPORTED', reason='ORIGINAL_DATA_BOUNDARY_HAS_NO_MAPPED_CANDIDATE_BOUNDARY',
                      alignment=None, blocks=None, hypotheses=[dict(category='data_ownership_review', count=1,
                      confidence='high', evidence=[dict(note='Original contains separately evidenced data; candidate boundary is not independently mapped.')])])
        return report
    resolver_error = None
    try:
        resolver = ReferenceResolver(f, ledger, compiled)
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        resolver, resolver_error = None, type(exc).__name__ + ': ' + str(exc)
    core = compare_code(bytes.fromhex(f['raw_bytes']), raw, resolver=resolver)
    if resolver_error:
        core['reference_identity']['resolver_error'] = resolver_error
    report.update(core)
    report['provenance'] = dict(original_game_sha256=ledger['game_sha256'], cache_key=cache_key,
                                compiler_cache_hit=bool(compiled.get('cache_hit')),
                                diagnostic_sha256=report['diagnostic_sha256'])
    return report


def compact_summary(result, max_bytes=6000):
    """Return bounded, non-authoritative feedback suitable for attempt facts."""
    summary = dict(schema_version=SCHEMA_VERSION, status=result.get('status'),
                   claim='DIAGNOSTIC_ONLY_NO_EQUALITY_OR_SEMANTIC_CLAIM',
                   function=result.get('function'), cache_key=result.get('cache_key'))
    if result.get('status') != 'DIAGNOSTIC_ONLY':
        summary['reason'] = result.get('reason', 'UNSUPPORTED')
        return summary
    align = result.get('alignment') or {}
    blocks = result.get('blocks') or {}
    summary['extents'] = dict(expected=(result.get('original_extent') or {}).get('bytes',
                                        (result.get('expected_extent') or {}).get('bytes')),
                              candidate=(result.get('candidate_extent') or {}).get('bytes',
                                        (result.get('actual_extent') or {}).get('bytes')))
    summary['instruction_similarity'] = align.get('instruction_similarity')
    summary['alignment_counts'] = dict(paired=len(align.get('pairs', [])),
                                       expected_only=len(align.get('expected_only', [])),
                                       actual_only=len(align.get('actual_only', [])))
    summary['hypotheses'] = []
    for h in result.get('hypotheses', []):
        examples = []
        for ex in h.get('evidence', [])[:4]:
            item = {k: ex[k] for k in ('note',) if k in ex}
            for side in ('expected', 'actual'):
                ins = ex.get(side)
                if ins:
                    item[side] = {k: ins[k] for k in ('offset', 'mnemonic', 'operands') if k in ins}
            examples.append(item)
        item = dict(category=h.get('category'), count=h.get('count'), group=h.get('group', _group(h.get('category'))),
                    confidence=h.get('confidence'), evidence=examples)
        if h.get('identity_states'):
            item['identity_states'] = dict(h['identity_states'])
        summary['hypotheses'].append(item)
    groups = result.get('hypothesis_groups')
    if isinstance(groups, dict):
        summary['hypothesis_groups'] = {g: dict(v) for g, v in groups.items() if isinstance(v, dict) and v.get('total')}
    ref = result.get('reference_identity')
    if isinstance(ref, dict):
        summary['reference_identity'] = dict(context=ref.get('context'), counts=ref.get('counts'),
                                             unresolved_reasons=ref.get('unresolved_reasons'))
    first = result.get('first_nonreference_divergence')
    if first:
        summary['first_nonreference_divergence'] = {k: first[k] for k in ('side', 'confidence', 'note') if k in first}
        for side in ('expected', 'actual', 'instruction'):
            ins = first.get(side)
            if ins:
                summary['first_nonreference_divergence'][side] = {k: ins[k] for k in ('offset', 'mnemonic', 'operands') if k in ins}
    else:
        summary['first_nonreference_divergence'] = None
    summary['cfg'] = dict(paired_blocks=len(blocks.get('paired', [])),
                          expected_unpaired=len((blocks.get('unpaired') or {}).get('expected', [])),
                          actual_unpaired=len((blocks.get('unpaired') or {}).get('actual', [])),
                          target_checks={state: sum(b.get('target_check') == state for b in blocks.get('paired', []))
                                         for state in ('consistent', 'different_or_unresolved', 'not_applicable')},
                          condition_or_terminator_changes=sum(b.get('terminators', [None, None])[0] != b.get('terminators', [None, None])[1]
                              or b.get('conditions', [None, None])[0] != b.get('conditions', [None, None])[1]
                              for b in blocks.get('paired', [])),
                          unresolved_indirect=len(blocks.get('indirect_transfers', [])))
    trace = result.get('register_trace')
    if isinstance(trace, dict):
        def _brief(ins):
            return {k: ins[k] for k in ('offset', 'mnemonic', 'operands') if k in ins} if ins else None
        fd, fc = trace.get('first_divergence'), trace.get('first_conflict')
        summary['register_trace'] = dict(
            comparable_pairs=trace.get('comparable_pairs'),
            first_divergence=(dict(expected=_brief(fd.get('expected')), actual=_brief(fd.get('actual'))) if fd else None),
            first_conflict=(dict(kind=fc.get('kind'), original=fc.get('original'), candidate=fc.get('candidate'),
                                 previous=fc.get('previous'), expected=_brief(fc.get('expected')),
                                 actual=_brief(fc.get('actual'))) if fc else None),
            remapped=sorted(m['original'] + '->' + m['candidate'] for m in trace.get('mapping', [])
                            if m.get('original') != m.get('candidate'))[:16])
    unresolved_edges = blocks.get('unresolved_edges') or {}
    summary['cfg']['unresolved_edges'] = dict(expected=unresolved_edges.get('expected'),
                                               actual=unresolved_edges.get('actual'))
    summary['uncertainty'] = [
        'Coarse instruction alignment is heuristic and does not establish semantic correspondence.',
        'Reference identities are only reused from established bindings; unresolved references stay unresolved. '
        'Data ownership and source intent are not proved by this report.'
    ]
    cats = {h.get('category') for h in result.get('hypotheses', [])}
    suggestions = []
    if 'register_assignment' in cats: suggestions.append('register roles or temporary lifetime')
    if 'operand_width' in cats: suggestions.append('expression or declaration width')
    if 'instruction_layout' in cats: suggestions.append('local statement structure around the inserted or missing instructions')
    if 'control_flow_shape' in cats or 'branch_condition_or_kind' in cats: suggestions.append('branch condition and block structure')
    if suggestions:
        summary['recommended_search_scope'] = suggestions
    elif cats.intersection({'a4_global_layout', 'pc_relative_layout', 'memory_reference_or_layout', 'call_target_or_encoding'}):
        summary['recommended_search_scope'] = ['reference identity and data-boundary evidence']
    else:
        summary['recommended_search_scope'] = ['inspect paired instruction evidence']
    encoded = json.dumps(summary, separators=(',', ':'), sort_keys=True).encode()
    if len(encoded) > max_bytes:
        for h in summary.get('hypotheses', []):
            h['evidence'] = h['evidence'][:1]
        summary['truncated'] = True
        if len(json.dumps(summary, separators=(',', ':'), sort_keys=True).encode()) > max_bytes:
            for h in summary.get('hypotheses', []): h['evidence'] = []
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('function', help='evidence function id, such as ov09_F_298E')
    ap.add_argument('--cache-key', required=True, help='validated key in build/compile-cache')
    ap.add_argument('--json', action='store_true', help='print the complete JSON diagnostic')
    args = ap.parse_args(argv)
    result = diagnose(args.function, args.cache_key)
    print(json.dumps(result, indent=2 if args.json else None, sort_keys=True))
    return 0 if result.get('status') == 'DIAGNOSTIC_ONLY' else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (FormatError, OSError, KeyError, ValueError) as exc:
        print('ERROR: '+str(exc), file=sys.stderr)
        sys.exit(2)
