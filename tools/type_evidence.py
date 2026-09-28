"""Bounded diagnostic type evidence from original 68k instructions.

This miner reports observed access widths, A4 data identities, address-taking,
and conservative A5 frame access clues. It never emits reconstructed hard
types, prototypes, ownership, or source names.
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from analysis_support import ROOT, K, decoder, game
from common import FormatError, require, sha256

OUT = ROOT / 'evidence/types.json'
LEDGER = ROOT / 'evidence/functions/ledger.json'
INSTRUCTIONS = ROOT / 'evidence/executable/instructions.json'
DECL_RE = re.compile(
    r'^\s*extern\s+(?P<type>(?:(?:unsigned|signed)\s+)?(?:char|short|int|long|struct\s+\w+))'
    r'\s*(?P<ptr>\*\s*)?(?P<name>[A-Za-z_]\w*)\s*(?P<array>\[\s*(\d*)\s*\])?\s*;\s*$')


def access_direction(mnemonic, operand_index, operand_count):
    """Return only instruction-local operand direction, never C constness."""
    base = mnemonic.lower().split('.')[0]
    if base in ('add', 'addq', 'sub', 'subq', 'and', 'or', 'eor', 'neg', 'not') and operand_index == operand_count - 1:
        return 'READ_WRITE'
    if base == 'clr' or (base == 'move' and operand_index == operand_count - 1):
        return 'WRITE'
    if base == 'move' or base in ('add', 'addq', 'sub', 'subq', 'and', 'or', 'eor'):
        return 'READ'
    return 'UNKNOWN'


def address_taking_kind(mnemonic):
    base = mnemonic.lower().split('.')[0]
    return base.upper() if base in ('lea', 'pea') else None


def extension_matches_load(load, extension, base_reg=K.M68K_REG_A4):
    """Only associate EXT with an immediately preceding A4/A5-to-register MOVE."""
    if (load.mnemonic.lower().split('.')[0] != 'move' or not load.operands or not extension.operands or
            extension.mnemonic.lower().split('.')[0] != 'ext'):
        return False
    src, dst = load.operands[0], load.operands[-1]
    return (src.type == K.M68K_OP_MEM and src.mem.base_reg == base_reg and
            dst.type == K.M68K_OP_REG and extension.operands[0].type == K.M68K_OP_REG and
            dst.reg == extension.operands[0].reg)


def identity(path):
    return sha256(path.read_bytes()) if path.is_file() else None


def mine(root=ROOT):
    """Return JSON-safe evidence derived from the immutable executable ledger."""
    root = Path(root)
    ledger_path = root / 'evidence/functions/ledger.json'
    ins_path = root / 'evidence/executable/instructions.json'
    ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
    instruction_index = json.loads(ins_path.read_text(encoding='utf-8'))
    require(instruction_index.get('analysis_current'), 'instruction analysis is stale')
    for relative, digest in ledger.get('analysis_identity', {}).items():
        require(sha256((root / 'tools' / relative).read_bytes()) == digest,
                'function census is stale: ' + relative)
    require(ledger.get('game_sha256'), 'function ledger has no oracle identity')
    # game() verifies fixture-lock identity and returns the executable from disks.
    blob, model, _ = game()
    require(sha256(blob) == ledger['game_sha256'], 'function ledger belongs to another executable')
    hunks = {h['number']: h for h in model['hunks']}
    data = {n: blob[h['content_offset']:h['content_offset'] + h['initialized_size']]
            for n, h in hunks.items() if h['content_offset'] is not None}
    bias_record = ledger.get('a4') or {}
    bias = bias_record.get('bias')
    require(isinstance(bias, int), 'ledger has no independently established A4 bias')
    md = decoder()
    globals_ = defaultdict(lambda: dict(accesses=[], address_taken=[], extension_context=[]))
    params = defaultdict(lambda: dict(accesses=[], extension_context=[], address_taken=[]))
    functions = {}
    for f in ledger.get('functions', []):
        fid, hunk = f['id'], f['hunk']
        if hunk not in data:
            continue
        functions[fid] = f
        by_off = {}
        for row in f.get('instructions', []):
            off = row['offset']
            ins = next(md.disasm(data[hunk][off:off + 24], off, count=1), None)
            if ins is not None and ins.size == row['size']:
                by_off[off] = ins
        refs_by_ins = defaultdict(list)
        for ref in f.get('referenced_data', []):
            if ref.get('kind') == 'A4_RELATIVE' and ref.get('hunk') == 1:
                refs_by_ins[ref['instruction_offset']].append(ref)
        ordered = sorted(by_off)
        for ix, off in enumerate(ordered):
            ins = by_off[off]
            mnemonic = ins.mnemonic.lower()
            size = {'b': 1, 'w': 2, 'l': 4}.get(mnemonic.rsplit('.', 1)[-1])
            for ref in refs_by_ins.get(off, []):
                target = ref['offset']
                dest_operand = ins.operands[-1] if ins.operands else None
                # LEA computes an address; all other forms are only recorded as
                # reads/writes, without guessing a C scalar or pointer type.
                address_kind = address_taking_kind(mnemonic)
                is_lea = address_kind is not None
                if is_lea:
                    direction = 'ADDRESS_TAKEN_CANDIDATE'
                    globals_[str(target)]['address_taken'].append(dict(
                        function=fid, hunk=1, offset=off, raw=bytes(ins.bytes).hex(),
                        mnemonic=ins.mnemonic, operands=ins.op_str,
                        basis='A4 identity + ' + address_kind))
                else:
                    direction = 'UNKNOWN'
                    # Destination is the last operand in Capstone's 68k detail.
                    for oi, operand in enumerate(ins.operands):
                        if operand.type == K.M68K_OP_MEM and operand.address_mode == K.M68K_AM_REGI_ADDR_DISP and operand.mem.base_reg == K.M68K_REG_A4 and target == bias + operand.mem.disp:
                            direction = access_direction(mnemonic, oi, len(ins.operands))
                    globals_[str(target)]['accesses'].append(dict(
                        function=fid, hunk=1, offset=off, raw=bytes(ins.bytes).hex(),
                        mnemonic=ins.mnemonic, operands=ins.op_str, width_bytes=size,
                        direction=direction, basis='A4 bias + decoded displacement'))
                # A nearby EXT operation only contextualizes the exact source
                # register load; it does not establish signed C semantics.
                if not is_lea and ix + 1 < len(ordered):
                    nxt = by_off[ordered[ix + 1]]
                    if nxt.address == ins.address + ins.size and extension_matches_load(ins, nxt):
                        globals_[str(target)]['extension_context'].append(dict(
                            function=fid, hunk=hunk, load_offset=off,
                            extension_offset=nxt.address, extension=nxt.mnemonic,
                            confidence='LOCAL_ADJACENCY_ONLY'))
            # A5 displacement accesses are frame-relative observations. The
            # first argument offset is deliberately not assigned: compiler,
            # return-address and caller conventions remain to be proved.
            for operand in ins.operands:
                if (operand.type == K.M68K_OP_MEM and operand.mem.base_reg == K.M68K_REG_A5
                        and operand.mem.disp >= 8):
                    key = str(operand.mem.disp)
                    frame_row = dict(
                        function=fid, hunk=hunk, offset=off, raw=bytes(ins.bytes).hex(),
                        mnemonic=ins.mnemonic, operands=ins.op_str,
                        frame_offset=operand.mem.disp, width_bytes=size,
                        basis='decoded A5 displacement; argument boundary unproved')
                    params[(fid, key)]['accesses'].append(frame_row)
                    if address_taking_kind(mnemonic):
                        params[(fid, key)]['address_taken'].append(dict(
                            function=fid, hunk=hunk, offset=off, mnemonic=ins.mnemonic,
                            kind=address_taking_kind(mnemonic), basis='A5 frame identity + address instruction'))
                    if ix + 1 < len(ordered):
                        nxt = by_off[ordered[ix + 1]]
                        if nxt.address == ins.address + ins.size and extension_matches_load(ins, nxt, K.M68K_REG_A5):
                            params[(fid, key)]['extension_context'].append(dict(
                                function=fid, hunk=hunk, load_offset=off,
                                extension_offset=nxt.address, extension=nxt.mnemonic,
                                confidence='LOCAL_ADJACENCY_ONLY; FRAME_SLOT_CANDIDATE'))
    global_rows = []
    for off, ev in sorted(globals_.items(), key=lambda x: int(x[0])):
        widths = sorted({x['width_bytes'] for x in ev['accesses'] if x['width_bytes']})
        global_rows.append(dict(data_hunk_offset=int(off), accesses=ev['accesses'],
                                observed_widths_bytes=widths,
                                width_interpretation='ACCESS_FACT_ONLY',
                                address_taken=ev['address_taken'],
                                extension_context=ev['extension_context']))
    param_rows = [dict(function=f, frame_offset=int(o), accesses=v['accesses'],
                       address_taken=v['address_taken'], extension_context=v['extension_context'],
                       interpretation='FRAME_ACCESS_CANDIDATE; not a parameter declaration')
                  for (f, o), v in sorted(params.items(), key=lambda x: (x[0][0], int(x[0][1])))]
    declarations = declaration_conflicts(root)
    return dict(schema_version=1, scope='bounded original-instruction observations',
                oracle_sha256=ledger['game_sha256'],
                inputs={'function_ledger_sha256': identity(ledger_path),
                        'instruction_index_sha256': identity(ins_path),
                        'miner_sha256': identity(root / 'tools/type_evidence.py'),
                        'declaration_source_hashes': declarations['source_hashes'],
                        'analysis_identity': ledger.get('analysis_identity', {}),
                        'a4_bias_evidence': bias_record.get('evidence')},
                counts={'functions_scanned': len(functions), 'global_identities': len(global_rows),
                        'global_accesses': sum(len(g['accesses']) for g in global_rows),
                        'address_taken_sites': sum(len(g['address_taken']) for g in global_rows),
                        'extension_context_sites': sum(len(g['extension_context']) for g in global_rows),
                        'frame_access_sites': sum(len(p['accesses']) for p in param_rows),
                        'frame_address_taken_sites': sum(len(p['address_taken']) for p in param_rows),
                        'frame_extension_context_sites': sum(len(p['extension_context']) for p in param_rows),
                        'frame_slots': len(param_rows)},
                policy='No inferred hard C types, prototypes, ownership, semantic global names, or exact string boundaries.',
                globals=global_rows, frame_access_candidates=param_rows,
                declaration_conflicts=declarations)


def _type_shape(decl):
    m = DECL_RE.fullmatch(decl)
    if not m:
        return None
    base = ' '.join(m['type'].split())
    pointer = bool(m['ptr'])
    array = m['array']
    extent = int(m[5]) if array and m[5] else None
    if pointer:
        category = 'pointer'
    elif base.startswith('struct '):
        category = 'struct'
    elif base.endswith('char'):
        category = 'char'
    elif base.endswith('long'):
        category = 'long'
    elif base.endswith(('short', 'int')):
        category = 'word'
    else:
        category = 'unknown'
    return dict(base=base, category=category, pointer=pointer, array=bool(array), extent=extent)


def _declarations(root):
    found = defaultdict(list)
    for path in sorted((Path(root) / 'src').rglob('*.c')):
        try:
            text = path.read_text(encoding='ascii')
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(text.splitlines(), 1):
            m = DECL_RE.fullmatch(line)
            if not m:
                continue
            found[m['name']].append(dict(path=path.relative_to(root).as_posix(), line=number,
                declaration=' '.join(line.strip().split()), shape=_type_shape(line)))
    return found


def declaration_source_hashes(root, declarations=None):
    declarations = _declarations(root) if declarations is None else declarations
    source_paths = sorted({item['path'] for rows in declarations.values() for item in rows})
    return {path: identity(Path(root) / path) for path in source_paths}


def _relation(a, b):
    x, y = a['shape'], b['shape']
    if x == y:
        return 'SAME_DECLARATION_SHAPE'
    if (x['category'] == y['category'] == 'word' and x['array'] == y['array'] and
            x['extent'] == y['extent'] and x['base'].startswith('unsigned') == y['base'].startswith('unsigned')):
        return 'ABI_COMPATIBLE_INT_SHORT_VIEW'
    if x['category'] == y['category'] == 'word' and x['base'].startswith('unsigned') != y['base'].startswith('unsigned'):
        return 'SIGNEDNESS_VIEW_CONFLICT'
    if x['category'] == y['category'] == 'struct':
        return 'STRUCT_VIEW_DIFFERENCE_REVIEW'
    if x['pointer'] != y['pointer']:
        return 'POINTER_SCALAR_VIEW_CONFLICT'
    if x['array'] != y['array']:
        return 'ARRAY_SCALAR_VIEW_CONFLICT'
    if x['array'] and y['array'] and x['extent'] != y['extent']:
        return 'ARRAY_EXTENT_CONFLICT'
    if {x['category'], y['category']} & {'char', 'long'}:
        return 'STORAGE_WIDTH_CONFLICT'
    return 'DECLARATION_VIEW_REVIEW'


def declaration_conflicts(root=ROOT):
    """Compare repeated simple extern declarations without resolving structs."""
    declarations = _declarations(root)
    conflicts = []
    counts = Counter()
    for name, rows in sorted(declarations.items()):
        for i, left in enumerate(rows):
            for right in rows[i + 1:]:
                relation = _relation(left, right)
                if relation == 'SAME_DECLARATION_SHAPE':
                    continue
                counts[relation] += 1
                conflicts.append(dict(symbol=name, relation=relation, left=left, right=right,
                    order_sensitive_harness=relation not in ('ABI_COMPATIBLE_INT_SHORT_VIEW',),
                    disposition='DIAGNOSTIC; no declaration was changed'))
    source_hashes = declaration_source_hashes(root, declarations)
    return dict(schema_version=1, declarations_scanned=sum(map(len, declarations.values())),
                symbols_with_multiple_views=sum(len(v) > 1 for v in declarations.values()),
                source_hashes=source_hashes,
                relation_counts=dict(sorted(counts.items())), conflicts=conflicts,
                parser='single-line extern scalar/pointer/array declarations only',
                policy='int/short are ABI-compatible 16-bit views in observed Manx target use; struct views are review items because partial tags may be intentional. Harness declaration deduplication is first-declaration-wins.')


def outputs(root=ROOT):
    evidence = mine(root)
    evidence['declaration_conflicts'] = declaration_conflicts(root)
    return evidence


def evidence_staleness(document, root=ROOT):
    """Reasons the generated report no longer matches its inputs (empty when fresh)."""
    root = Path(root)
    inputs = document.get('inputs', {})
    reasons = []
    if not (isinstance(inputs.get('miner_sha256'), str) and inputs['miner_sha256'] == identity(root / 'tools/type_evidence.py')):
        reasons.append('stale type evidence: miner changed; run tools/type_evidence.py --write')
    if not (isinstance(inputs.get('function_ledger_sha256'), str) and inputs['function_ledger_sha256'] == identity(root / 'evidence/functions/ledger.json')):
        reasons.append('type evidence is stale; run tools/type_evidence.py --write')
    if not (isinstance(inputs.get('instruction_index_sha256'), str) and inputs['instruction_index_sha256'] == identity(root / 'evidence/executable/instructions.json')):
        reasons.append('type evidence instruction index is stale; run tools/type_evidence.py --write')
    current_source_hashes = declaration_source_hashes(root)
    if current_source_hashes != inputs.get('declaration_source_hashes'):
        reasons.append('stale type evidence: declaration source inventory changed; run tools/type_evidence.py --write')
    else:
        for relative, digest in current_source_hashes.items():
            if digest != identity(root / relative):
                reasons.append('type evidence declaration source is stale; run tools/type_evidence.py --write')
                break
    return reasons


def function_evidence(fid, root=ROOT, allow_stale=False):
    """Compact per-function slice for recovery feedback; validates data freshness.

    Strict by default. ``allow_stale`` (worker-facing reads) serves the last
    generated report with an explicit ``stale: true`` flag and the reasons
    instead of refusing; it never hides staleness and never rewrites the file.
    """
    root = Path(root)
    document = json.loads((root / 'evidence/types.json').read_text(encoding='utf-8'))
    stale = evidence_staleness(document, root)
    if stale and not allow_stale:
        raise FormatError(stale[0])
    touched = []
    for g in document['globals']:
        current = [a for a in g['accesses'] if a['function'] == fid]
        addr = [a for a in g['address_taken'] if a['function'] == fid]
        ext = [a for a in g['extension_context'] if a['function'] == fid]
        if not (current or addr or ext):
            continue
        prog = g['accesses']
        directions = Counter(a['direction'] for a in prog)
        touched.append(dict(data_hunk_offset=g['data_hunk_offset'],
            observed_widths_bytes=g['observed_widths_bytes'], program_access_count=len(prog),
            program_read_write_counts=dict(sorted(directions.items())),
            function_access_count=len(current), function_address_taken_count=len(addr),
            function_extension_context_count=len(ext),
            sites=[dict(offset=a['offset'], mnemonic=a['mnemonic'], width_bytes=a['width_bytes'],
                        direction=a['direction']) for a in current[:2]],
            address_sites=[a['offset'] for a in addr[:2]], extension_sites=[a['load_offset'] for a in ext[:2]]))
    frame_rows = []
    for p in document['frame_access_candidates']:
        if p['function'] != fid:
            continue
        frame_rows.append(dict(frame_offset=p['frame_offset'], access_count=len(p['accesses']),
            address_taken_count=len(p['address_taken']), extension_context_count=len(p['extension_context']),
            observed_widths_bytes=sorted({a['width_bytes'] for a in p['accesses'] if a['width_bytes']}),
            sites=[dict(offset=a['offset'], mnemonic=a['mnemonic'], width_bytes=a['width_bytes'])
                   for a in p['accesses'][:2]],
            address_sites=[a['offset'] for a in p['address_taken'][:2]],
            extension_sites=[a['load_offset'] for a in p['extension_context'][:2]]))
    touched_names = {'G_h01_%04X' % row['data_hunk_offset'] for row in touched}
    conflicts = [c for c in document['declaration_conflicts']['conflicts'] if c['symbol'] in touched_names]
    return dict(function=fid, stale=bool(stale), stale_reasons=stale,
        stale_note=('served from the last generated evidence/types.json; inputs changed since (e.g. a promotion); '
                    'advisory only' if stale else None),
        global_identity_count=len(touched), omitted_global_identities=max(0, len(touched)-12),
        globals=touched[:12], frame_slot_count=len(frame_rows), omitted_frame_slots=max(0, len(frame_rows)-8),
        frame_accesses=frame_rows[:8],
        declaration_conflict_summary=dict(
            relevant_total=len(conflicts), relation_counts=dict(sorted(Counter(c['relation'] for c in conflicts).items())),
            corpus_total=len(document['declaration_conflicts']['conflicts']),
            examples=[dict(symbol=c['symbol'], relation=c['relation'],
                           declarations=[c['left']['declaration'], c['right']['declaration']])
                      for c in conflicts[:8]], omitted=max(0, len(conflicts)-8),
            identity_basis='mechanical G_h01_HEX symbol maps its suffix to the exact DATA HUNK offset',
            scope='candidate source declarations at touched mechanically named global offsets; see evidence/types.json'))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--function')
    ap.add_argument('--strict', action='store_true',
                    help='with --function: refuse stale evidence instead of serving it flagged stale')
    args = ap.parse_args(argv)
    if args.function:
        print(json.dumps(function_evidence(args.function, allow_stale=not args.strict), indent=2))
        return
    result = outputs()
    raw = (json.dumps(result, indent=2, sort_keys=True) + '\n').encode('utf-8')
    if args.check:
        require(OUT.exists() and OUT.read_bytes() == raw, 'stale type evidence: run tools/type_evidence.py --write')
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(raw)
    print('PASS: %s (%d global identities, %d declaration conflicts)' %
          ('checked' if args.check else 'wrote', result['counts']['global_identities'],
           len(result['declaration_conflicts']['conflicts'])))


if __name__ == '__main__':
    main()
