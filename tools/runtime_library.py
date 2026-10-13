"""Identify c.lib members in the resident image with relocated fields masked.

Every c.lib member is extracted (``lb -x``) and linked alone with c.lib (and a
link-only object defining the library-base globals the game defines itself).
A member matches the original when every byte outside its masked fields is
equal.  The masked fields are A4 d16 displacements, absolute relocations and
PC-relative transfers that leave the member.  Each A4 field names the data
symbol it reaches in the member's own link, so library-base slots
(``_GfxBase`` and the like) are identified by a vote over addresses matched
by exactly one member.  A member is kept only when every A4 field agrees with
the voted slot of its symbol, and an address is kept only when exactly one
member survives.  The result identifies runtime code; it adds no game source,
claims no DATA ownership and selects no compiler release.
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

from analysis_support import game, ROOT
from common import require, sha256, write_json
from hunk import parse

OUTPUT = 'evidence/experiments/runtime-library.json'
LIBRARY = 'aztec-3.6a/SYS1/lib/c.lib'
JOBS = ('runtime-sweep-c36-20261013', 'runtime-sweep2-c36-20261013')
A4_BIAS = 0x7FFE


def members(work):
    """Member names linked in a job (``m_NAME`` executables with symbol maps)."""
    return sorted(p.name[2:] for p in work.glob('m_*') if p.suffix == '' and (work / (p.name + '.sym')).exists())


def symbol_map(path):
    """{hunk: {offset: [names]}} from an Aztec ``ln -t`` map."""
    out = {}; hunk = None
    for line in Path(path).read_text(errors='replace').splitlines():
        m = re.match(r'Segment \d+:\s+Hunk (\d+)', line.strip())
        if m:
            hunk = int(m.group(1)); continue
        m = re.match(r'\s*([0-9a-fA-F]{8})\s+(\S+)', line)
        if m and hunk is not None:
            out.setdefault(hunk, {}).setdefault(int(m.group(1), 16), []).append(m.group(2))
    return out


def linked_member(work, name, lead_allowed):
    import function_compare as fc
    from capstone import m68k as K
    obj = (work / (name + '.o')).read_bytes()
    if obj[:2] not in (b'AJ', b'CJ'):
        return None
    size = int.from_bytes(obj[10:14], 'big')
    data = (work / ('m_' + name)).read_bytes(); model = parse(data)
    code_h = next((h for h in model['hunks'] if h['type'] == 'CODE'), None)
    if code_h is None or size < 6:
        return None
    code = data[code_h['content_offset']:code_h['content_offset'] + code_h['initialized_size']]
    lead = (4 if code[1] == 0 else 2) if lead_allowed and code[:1] == b'\x60' else 0
    raw = code[lead:lead + size]
    if len(raw) != size:
        return None
    syms = symbol_map(work / ('m_' + name + '.sym'))
    mask = bytearray(b'\xff' * size); a4 = []
    for r in model['relocations']:
        so = r['source_offset'] - lead
        if r['source_hunk'] == code_h['number'] and 0 <= so < size:
            for k in range(r['width']):
                mask[so + k] = 0
    instructions, _ = fc.decode_all(raw, [])
    for i in instructions:
        for op in i.operands:
            if op.type == K.M68K_OP_MEM and op.mem.base_reg == K.M68K_REG_A4 and op.address_mode == K.M68K_AM_REGI_ADDR_DISP:
                site = fc.unique_word_site(i, op.mem.disp)
                if site is None:
                    return None
                mask[i.address + site] = mask[i.address + site + 1] = 0
                names = [n for h in (1, 2) for n in syms.get(h, {}).get(A4_BIAS + op.mem.disp, []) if not n.startswith('__H')]
                a4.append(dict(offset=i.address + site, symbols=sorted(names)))
            branch = op.type == K.M68K_OP_BR_DISP or (op.type == K.M68K_OP_MEM and op.address_mode == K.M68K_AM_PCI_DISP
                                                       and i.mnemonic.startswith(('jsr', 'jmp', 'bsr')))
            if branch:
                disp = op.br_disp.disp if op.type == K.M68K_OP_BR_DISP else op.mem.disp
                if not 0 <= i.address + 2 + disp < size:
                    if i.size == 2:
                        mask[i.address + 1] = 0
                    elif i.address + 3 < size:
                        mask[i.address + 2] = mask[i.address + 3] = 0
                    else:
                        return None
    entries = sorted((dict(name=n, offset=o - lead) for o, ns in syms.get(0, {}).items() for n in ns
                      if not n.startswith('__H') and 0 <= o - lead < size), key=lambda e: (e['offset'], e['name']))
    return dict(name=name, size=size, raw=raw, mask=bytes(mask), a4=a4, entries=entries,
                object_sha256=sha256(obj))


def matches(original, mem):
    raw, mask, n = mem['raw'], mem['mask'], mem['size']
    keep = [k for k in range(n) if mask[k]]
    hits = []
    for off in range(0, len(original) - n + 1, 2):
        if all(original[off + k] == raw[k] for k in keep):
            hits.append(off)
            if len(hits) > 3:
                break
    return hits


def analyze():
    blob, model, _ = game()
    h0 = model['hunks'][0]
    original = blob[h0['content_offset']:h0['content_offset'] + h0['initialized_size']]
    receipts = {}; found = []
    for index, job in enumerate(JOBS):
        work = ROOT / 'build/worker-jobs' / job / 'sys/work'
        receipt = ROOT / 'build/worker-jobs' / job / 'result.json'
        require(receipt.is_file(), 'missing runtime library job receipt: ' + job)
        receipts[job] = sha256(receipt.read_bytes())
        done = {m['name'] for m in found}
        for name in members(work):
            if name in done:
                continue
            mem = linked_member(work, name, lead_allowed=index > 0)
            if mem is None:
                continue
            hits = matches(original, mem)
            if hits:
                mem['hits'] = hits; mem['job'] = job; found.append(mem)
    # Library-base slots from addresses that exactly one member matches.
    by_address = {}
    for mem in found:
        if len(mem['hits']) == 1:
            by_address.setdefault(mem['hits'][0], []).append(mem)
    votes = {}
    for address, mems in by_address.items():
        if len(mems) != 1:
            continue
        for field in mems[0]['a4']:
            disp = int.from_bytes(original[address + field['offset']:address + field['offset'] + 2], 'big', signed=True)
            for symbol in field['symbols']:
                votes.setdefault(symbol, Counter())[disp] += 1
    slots = {s: c.most_common(1)[0][0] for s, c in votes.items()}
    # A slot holds one symbol: the symbol with the most votes keeps it.
    owner = {}
    for s in sorted(slots, key=lambda s: (-votes[s][slots[s]], s)):
        owner.setdefault(slots[s], s)
    slots = {s: d for s, d in slots.items() if owner[d] == s}
    contributions = []; unresolved = []
    for address, mems in sorted(by_address.items()):
        ok = []
        for mem in mems:
            fields = []
            for field in mem['a4']:
                disp = int.from_bytes(original[address + field['offset']:address + field['offset'] + 2], 'big', signed=True)
                fields.append((field, disp))
            if all(slots.get(s) == d for f, d in fields for s in f['symbols']) and all(f['symbols'] for f, _ in fields):
                ok.append((mem, fields))
        if len(ok) != 1:
            unresolved.append(dict(offset=address, members=sorted(m['name'] for m in mems)))
            continue
        mem, fields = ok[0]
        masked = bytes(b if m else 0 for b, m in zip(original[address:address + mem['size']], mem['mask']))
        contributions.append(dict(member=mem['name'], original=dict(hunk=0, offset=address, size=mem['size']),
                                  size=mem['size'], masked_bytes=sum(1 for m in mem['mask'] if not m),
                                  masked_code_sha256=sha256(masked), object_sha256=mem['object_sha256'], job=mem['job'],
                                  a4_fields=[dict(offset=f['offset'], symbols=f['symbols'], a4_displacement=d) for f, d in fields],
                                  entries=mem['entries']))
    return dict(schema_version=1, game_sha256=sha256(blob), status='MASKED_RUNTIME_CODE_MATCH',
                library=LIBRARY, library_sha256=sha256((ROOT / 'toolchain/installed' / LIBRARY).read_bytes()),
                job_receipt_sha256s=receipts,
                base_slots={s: dict(a4_displacement=d, votes=votes[s][d], dissent=sum(votes[s].values()) - votes[s][d])
                            for s, d in sorted(slots.items())},
                contributions=contributions, unresolved=unresolved,
                identified_bytes=sum(c['size'] for c in contributions),
                limitations=['Masked fields are A4 displacements, absolute relocations and external PC-relative transfers.',
                             'Library-base slot names come from the member links and a majority vote; they claim no DATA ownership.',
                             'Identifies runtime code only; no game source and no compiler release selection.'])


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    result = analyze()
    write_json(ROOT / OUTPUT, result)
    print(json.dumps(dict(status=result['status'], contributions=len(result['contributions']),
                          identified_bytes=result['identified_bytes'], unresolved=len(result['unresolved']),
                          base_slots={k: hex(v['a4_displacement'] & 0xffff) for k, v in result['base_slots'].items()})))
