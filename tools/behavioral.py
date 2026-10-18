"""Behaviorally reconstructed C: exact apart from byte-return widening.

Four game routines return a byte in D0 with a bare ``move.b ..,d0``. Every
pinned Aztec release widens a C ``char`` return with ``ext.w d0``, so their
source cannot match exactly (docs/blockers.json, TOOLCHAIN). This tool proves
the strongest claim available short of a match:

1. Candidate == original after deleting only ``ext.w d0`` instructions that
   directly follow a ``move.b <ea>,d0`` on a return path. The deletion
   re-encodes PC-relative displacements that cross it and shifts relocations;
   the unchanged ``function_compare.compare_function`` must then report EQUAL,
   so every remaining byte, A4 identity, call binding and relocation is proved
   exactly as for an ordinary FUNCTION_CODE_MATCH.
2. Every original caller reads only D0.b before redefining D0, so the widened
   upper byte is unobservable.

The result is BEHAVIORAL_CHAR_RETURN, never a match. It is reported and
accounted separately, and is upgradeable to exact if a compiler without the
widening is ever pinned.
"""
from names import to_mechanical
import argparse
import json
import sys
from unittest.mock import patch

from common import FormatError, require, sha256

STATE = 'BEHAVIORAL_CHAR_RETURN'
WIDEN_RAW = bytes.fromhex('4880')  # ext.w d0


def _is_byte_load_d0(ins):
    return ins.mnemonic == 'move.b' and ins.op_str.replace(' ', '').endswith(',d0')


def _is_return_path(ins, by_address):
    m = ins.mnemonic.split('.')[0]
    if m in ('unlk', 'rts'):
        return True
    if m in ('bra', 'jmp') and ins.operands and hasattr(ins.operands[-1], 'br_disp'):
        target = ins.address + 2 + ins.operands[-1].br_disp.disp
        nxt = by_address.get(target)
        return nxt is not None and nxt.mnemonic.split('.')[0] in ('unlk', 'rts', 'movem')
    return False


def align(expected, actual, spans=()):
    """Return the widening instructions the candidate inserts, or raise."""
    from function_compare import decode_all
    ei, ebad = decode_all(expected, spans)
    ai, abad = decode_all(actual, spans)
    require(ebad is None and abad is None, 'behavioral comparison needs completely decoded code')
    by_address = {i.address: i for i in ei}
    i = j = 0
    deletions = []
    while i < len(ei) or j < len(ai):
        if (j < len(ai) and bytes(ai[j].bytes) == WIDEN_RAW and j > 0 and i > 0 and i < len(ei)
                and _is_byte_load_d0(ai[j - 1]) and _is_byte_load_d0(ei[i - 1])
                and bytes(ei[i].bytes) != WIDEN_RAW and _is_return_path(ei[i], by_address)):
            deletions.append(ai[j])
            j += 1
            continue
        require(i < len(ei) and j < len(ai), 'instruction streams differ beyond byte-return widening')
        e, a = ei[i], ai[j]
        require(e.mnemonic == a.mnemonic and e.size == a.size,
                'instruction differs beyond byte-return widening at original +0x%X' % e.address)
        i += 1
        j += 1
    require(deletions, 'no byte-return widening: verify with check_function instead')
    return ai, deletions


def reduced_contribution(expected, contribution, spans=()):
    """Candidate contribution with the proven widenings removed."""
    from analysis_support import K
    actual = bytes.fromhex(contribution['code_hex'])
    ai, deletions = align(expected, actual, spans)
    removed = sorted(d.address for d in deletions)

    def before(address):
        return sum(1 for r in removed if r < address) * 2

    out = bytearray()
    for ins in ai:
        if ins.address in removed:
            continue
        raw = bytearray(ins.bytes)
        shift = before(ins.address)
        for op in ins.operands:
            if op.type == K.M68K_OP_BR_DISP:
                width = {2: 1, 4: 2}.get(ins.size)
                require(width is not None and not (ins.size == 2 and op.br_disp.disp == 0),
                        'unsupported branch encoding across a widening')
                target = ins.address + 2 + op.br_disp.disp
                inside = 0 <= target < len(actual)
                new_disp = (target - before(target) if inside else target) - (ins.address - shift) - 2
                lo, hi = (-128, 127) if width == 1 else (-32768, 32767)
                require(lo <= new_disp <= hi and (width == 2 or new_disp not in (0, -1)),
                        'branch no longer encodes in its original width')
                field = 1 if width == 1 else 2
                raw[field:field + width] = (new_disp & (0xFF if width == 1 else 0xFFFF)).to_bytes(width, 'big')
            elif op.type == K.M68K_OP_MEM and op.address_mode == K.M68K_AM_PCI_DISP:
                require(ins.size == 4, 'unsupported PC-relative operand across a widening')
                target = ins.address + 2 + op.mem.disp
                inside = 0 <= target < len(actual)
                new_disp = (target - before(target) if inside else target) - (ins.address - shift) - 2
                require(-32768 <= new_disp <= 32767, 'PC-relative operand out of range')
                raw[2:4] = (new_disp & 0xFFFF).to_bytes(2, 'big')
        out += raw
    relocs = []
    for r in contribution['relocations']:
        require(r['relative_offset'] not in removed, 'relocation inside a widening')
        relocs.append(dict(r, relative_offset=r['relative_offset'] - before(r['relative_offset'])))
    result = dict(contribution, code_hex=bytes(out).hex(), relocations=relocs)
    return result, [dict(offset=d.address, raw=bytes(d.bytes).hex(), mnemonic=d.mnemonic, operands=d.op_str)
                    for d in deletions]


def _reads_writes(ins):
    """(size read from d0, defines d0 fully?, defines low word?) for one instruction."""
    m = ins.mnemonic
    base, _, suffix = m.partition('.')
    ops = [o.strip() for o in ins.op_str.split(',')] if ins.op_str else []
    size = {'b': 1, 'w': 2, 'l': 4}.get(suffix, 4)
    if 'd0' not in ops:
        return 0, False, False
    dest = ops[-1] == 'd0'
    src = 'd0' in ops[:-1]
    if base == 'ext':
        return (1 if suffix == 'w' else 2), suffix == 'l', suffix == 'w'
    if base in ('moveq',):
        return 0, True, True
    if base in ('move', 'movea', 'lea') and dest and not src:
        return 0, size == 4, size == 2
    if base == 'clr' and dest:
        return 0, size == 4, size == 2
    if base in ('tst', 'cmp', 'cmpi', 'btst') or src:
        return size, False, False
    # Read-modify-write on d0 (add, sub, and, or, eor, lsl, swap, ...).
    return (4 if base == 'swap' else size), False, False


def byte_only_callers(f, functions):
    """Prove every original caller reads only D0.b before redefining D0."""
    from analysis_support import decoder
    by_id = {x['id']: x for x in functions}
    md = decoder()
    sites = []
    require(f.get('callers'), 'behavioral claim needs measured callers')
    for c in f['callers']:
        caller = by_id[c['id']]
        code = bytes.fromhex(caller['raw_bytes'])
        start = caller['start']
        insns = {i.address: i for i in md.disasm(code, start)}
        call = insns.get(c['site'])
        require(call is not None and call.mnemonic.split('.')[0] in ('jsr', 'bsr'), 'caller site is not a call')
        # Worklist over straight-line paths; trusted = defined D0 bits (0, 8, 16, 32).
        todo = [(call.address + call.size, 8)]
        seen = set()
        steps = 0
        while todo:
            pc, trusted = todo.pop()
            while True:
                steps += 1
                require(steps < 400, 'caller D0 analysis did not converge: ' + c['id'])
                if (pc, trusted) in seen:
                    break
                seen.add((pc, trusted))
                ins = insns.get(pc)
                require(ins is not None, 'caller path leaves its decoded extent: ' + c['id'])
                base = ins.mnemonic.split('.')[0]
                read, full, word = _reads_writes(ins)
                require(read * 8 <= trusted, 'caller %s reads widened D0 bits at 0x%X' % (c['id'], ins.address))
                if full:
                    break
                if word:
                    trusted = max(trusted, 16)
                if base in ('jsr', 'bsr'):
                    break  # C calls redefine the scratch return register.
                if base in ('rts', 'rte'):
                    require(trusted >= 32, 'caller %s returns D0 with widened bits' % c['id'])
                    break
                if base in ('bra', 'jmp') or base.startswith('b') and base not in ('btst', 'bset', 'bclr', 'bchg'):
                    op = ins.operands[-1] if ins.operands else None
                    require(op is not None and hasattr(op, 'br_disp') and op.type != 0,
                            'caller %s has an unresolved transfer at 0x%X' % (c['id'], ins.address))
                    target = ins.address + 2 + op.br_disp.disp
                    if base == 'bra':
                        pc = target
                        continue
                    todo.append((target, trusted))
                pc = ins.address + ins.size
        sites.append(dict(caller=c['id'], site=c['site']))
    return sites


def check(fid, source, profile):
    """Isolated verification; never writes canonical state."""
    import check_function
    import function_compare
    from recovery_state import evidence
    real = function_compare.compare_function
    analysis = evidence()
    f0 = next(x for x in analysis['functions'] if x['id'] == fid)
    callers = byte_only_callers(f0, analysis['functions'])
    captured = {}

    def compare(f, compiled, a4_bias, *args, **kwargs):
        if f['id'] != fid or compiled.get('status') != 'COMPILED':
            return real(f, compiled, a4_bias, *args, **kwargs)
        spans = [(t['table_start'] - f['start'], t['table_end'] - f['start']) for t in f.get('jump_tables', [])]
        contribution, deletions = reduced_contribution(bytes.fromhex(f['raw_bytes']), compiled['contribution'], spans)
        report = real(f, dict(compiled, contribution=contribution), a4_bias, *args, **kwargs)
        captured.update(deletions=deletions, candidate_length=len(compiled['contribution']['code_hex']) // 2)
        return report

    with patch.object(check_function, 'compare_function', compare):
        reports = check_function.check_many([dict(id=fid, source=source, profiles=[profile])], isolated=True)
    report = reports[0]
    equal = report.get('verdict') == 'EQUAL' and bool(captured.get('deletions'))
    return dict(id=fid, profile=profile, state=STATE if equal else None,
                verdict='BEHAVIORAL_EQUAL' if equal else report.get('verdict'),
                reason=None if equal else report.get('reason'),
                deletions=captured.get('deletions'), candidate_length=captured.get('candidate_length'),
                original_length=f0['size'], byte_only_callers=callers,
                exact_report=report)


MAP = 'behavioral_functions'
PROOFS = 'recovery/proofs/behavioral/'
CATEGORY = 'BEHAVIORAL_C'


def _extent(f):
    return {k: f[k] for k in ('hunk', 'start', 'end', 'size', 'sha256')}


def proof_for(result, f, source, regression):
    report = result['exact_report']
    return dict(id=f['id'], state=STATE, profile=result['profile'], source_sha256=sha256(source),
                original=_extent(f), deletions=result['deletions'],
                candidate_length=result['candidate_length'], byte_only_callers=result['byte_only_callers'],
                reduced_comparison={k: report.get(k) for k in (
                    'verdict', 'reason', 'cache_key', 'expected_sha256', 'normalized_sha256',
                    'relocation_equal', 'relocation_proof', 'relocation_issues', 'compiler', 'flags')},
                claim='Exact after deleting the listed byte-return widenings; every caller reads only D0.b. '
                      'Not a match: the pinned compilers cannot emit the bare byte return.',
                regression=regression)


def validate(root, f, item, analysis):
    """Canonical read: hash bindings, oracle extent, recorded claim and caller reads."""
    from repo_paths import canonical_path
    require(set(item) == {'state', 'source', 'source_sha256', 'proof', 'proof_sha256', 'evidence_extent'} and
            item['state'] == STATE and item['proof'] == PROOFS + f['id'] + '.json', 'behavioral ledger entry')
    source = to_mechanical(canonical_path(root, item['source']).read_bytes())
    raw = canonical_path(root, item['proof']).read_bytes()
    require(sha256(source) == item['source_sha256'] and sha256(raw) == item['proof_sha256'],
            'behavioral source/proof binding')
    proof = json.loads(raw)
    require(proof['id'] == f['id'] and proof['state'] == STATE and proof['source_sha256'] == item['source_sha256'],
            'behavioral proof identity')
    require(proof['original'] == _extent(f) == item['evidence_extent'] and f['extent_status'] == 'CLOSED_CFG',
            'behavioral oracle extent changed')
    comparison = proof['reduced_comparison']
    require(comparison['verdict'] == 'EQUAL' and comparison['relocation_equal'] and not comparison['relocation_issues']
            and comparison['normalized_sha256'] == comparison['expected_sha256'] == f['sha256'],
            'behavioral reduced comparison is not exact')
    require(proof['deletions'] and all(d['raw'] == WIDEN_RAW.hex() for d in proof['deletions']) and
            proof['candidate_length'] == f['size'] + 2 * len(proof['deletions']),
            'behavioral deletions are not widenings only')
    require(proof['regression'].get('passed') is True, 'behavioral admission lacks a passed regression gate')
    require(byte_only_callers(f, analysis['functions']) == proof['byte_only_callers'], 'behavioral caller reads changed')
    return proof


def contributions(root, blob, model, analysis, ledger):
    """Accounting rows: the oracle extent, credited only as BEHAVIORAL_C."""
    from audio_sequence_data import payload
    by = {f['id']: f for f in analysis['functions']}
    rows = []
    for fid, item in sorted(ledger.get(MAP, {}).items()):
        f = by[fid]
        validate(root, f, item, analysis)
        require(fid not in ledger.get('functions', {}), 'behavioral entry is also exact C')
        raw = payload(blob, model, f['hunk'])[f['start']:f['end']]
        require(sha256(raw) == f['sha256'], 'behavioral oracle bytes changed')
        rels = [{k: r[k] for k in ('source_offset', 'target_hunk', 'type', 'width', 'addend_raw')}
                for r in model['relocations']
                if r['source_hunk'] == f['hunk'] and f['start'] <= r['source_offset'] < f['end']]
        rows.append(dict(id=fid, hunk=f['hunk'], start=f['start'], end=f['end'], category=CATEGORY,
                         bytes=raw, relocations=rels))
    return rows


def promote(requests):
    """Admit several candidates under one regression gate and one ledger commit."""
    from analysis_support import ROOT
    from common import write_json, json_bytes
    from evidence_snapshot import Snapshot
    from recovery_state import evidence, canonical_state
    from recovery_transaction import ledger_lock
    from repo_paths import candidate_path
    from check_function import regression_receipt
    root = ROOT
    require(requests and len({r['id'] for r in requests}) == len(requests), 'behavioral batch needs distinct ids')
    fingerprint = Snapshot().inputs(root, True)
    analysis = evidence()
    by = {f['id']: f for f in analysis['functions']}
    staged = []
    for r in requests:
        source = to_mechanical(candidate_path(root, root / r['source']).read_bytes())
        result = check(r['id'], r['source'], r.get('profile', 'aztec36'))
        require(result.get('state') == STATE, r['id'] + ' is not behaviorally equal: ' + str(result.get('reason')))
        staged.append((r['id'], source, result))
    regression = regression_receipt()
    require(regression.get('passed') is True, 'regression gate failed')
    ledger_path = root / 'recovery/ledger.json'
    with ledger_lock(ledger_path):
        require(Snapshot().inputs(root, True) == fingerprint, 'canonical inputs changed during behavioral verification')
        state = json.loads(ledger_path.read_bytes())
        writes, items = {}, {}
        for fid, source, result in staged:
            f = by[fid]
            require(fid not in state.get('functions', {}) and fid not in state.get(MAP, {}), fid + ' already accepted')
            node = 'resident' if f['hunk'] == 0 else 'ov%02d' % f['hunk']
            dest = 'src/recovered/%s/%s.c' % (node, fid)
            proof = proof_for(result, f, source, regression)
            items[fid] = dict(state=STATE, source=dest, source_sha256=sha256(source), proof=PROOFS + fid + '.json',
                              proof_sha256=sha256(json_bytes(proof)), evidence_extent=_extent(f))
            writes[root / dest] = source
            writes[root / items[fid]['proof']] = json_bytes(proof)
        require(not any(q.exists() for q in writes), 'behavioral destination exists')
        saved = ledger_path.read_bytes()
        try:
            for path, raw in writes.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            state.setdefault(MAP, {}).update(items)
            write_json(ledger_path, canonical_state(state))
        except BaseException:
            for path in writes:
                path.unlink(missing_ok=True)
            ledger_path.write_bytes(saved)
            raise
    return items


def replay_all():
    """Recompile every accepted behavioral source and require the recorded claim."""
    from analysis_support import ROOT
    from recovery_state import recovery
    out = []
    for fid, item in sorted(recovery().get(MAP, {}).items()):
        proof = json.loads((ROOT / item['proof']).read_text())
        result = check(fid, item['source'], proof['profile'])
        require(result.get('state') == STATE and result['deletions'] == proof['deletions'] and
                result['exact_report'].get('normalized_sha256') == proof['reduced_comparison']['normalized_sha256'],
                'behavioral replay differs: ' + fid)
        out.append(fid)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('id', nargs='?')
    ap.add_argument('source', nargs='?')
    ap.add_argument('--profile', default='aztec36')
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--promote', metavar='MANIFEST',
                      help='JSON list of {id, source, profile}: one regression gate, then admit the unchanged sources')
    mode.add_argument('--replay', action='store_true', help='recompile and recheck every accepted entry')
    args = ap.parse_args(argv)
    try:
        if args.replay:
            result = dict(verdict='REPLAYED', ids=replay_all())
        elif args.promote:
            result = dict(verdict='PROMOTED', items=promote(json.loads(open(args.promote).read())))
        else:
            require(args.id and args.source, 'id and source are required')
            result = check(args.id, args.source, args.profile)
    except FormatError as exc:
        result = dict(id=args.id, verdict='REJECTED', reason=str(exc))
    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get('verdict') in ('BEHAVIORAL_EQUAL', 'PROMOTED', 'REPLAYED') else 1


if __name__ == '__main__':
    sys.exit(main())
