"""Separate mixed startup extent, canonical proof and language-aware accounting."""
from names import to_mechanical
import json
from pathlib import Path

from common import require, sha256
from repo_paths import canonical_path, active_files
from startup_producer import FACT, BASE, PARTS, source_views, verify as producer_verify
from startup_mixed import verify
from overlay_experiment import contribution, symbols
from hunk import parse

ID = 'resident_F_766C'
SOURCE = 'src/recovered/resident/resident_F_766C.c'
PROOF = 'recovery/proofs/resident_F_766C.mixed.json'
REFRESH = 'evidence/rules/startup-refresh'
ANCHORS = ('resident_F_77A4', 'resident_F_7B24', 'resident_F_8534', 'ov04_F_1E36')


def read(root, path):
    return (to_mechanical(canonical_path(root, path).read_bytes()) if str(path).startswith('src/') else canonical_path(root, path).read_bytes())


def inputs(root):
    paths = {FACT}
    if not canonical_path(root, FACT).exists():
        return sorted(paths)
    from resident_mixed import source_object_inputs
    paths.update(source_object_inputs(root))
    paths.update(['toolchain/installed/aztec-3.6a/SYS2/crt_src/_main.c',
                  'toolchain/installed/aztec-3.6a/SYS2/crt_src/crt0.a68',
                  'toolchain/installed/aztec-3.6a/Library Source/dos.arc',
                  BASE + '/source_recipe.py', BASE + '/abi_recipe.py'])
    for base in (BASE, REFRESH, 'evidence/rules/startup-callees'):
        for scope in (('exec', 'dos') if base.endswith('callees') else ('abi', 'partition')):
            directory = base + '/' + scope
            paths.update(p.relative_to(root).as_posix() for p in active_files(canonical_path(root, directory)))
            paths.add(directory + '/receipt.json')
            if canonical_path(root, directory + '/receipt.json').exists():
                receipt = json.loads(read(root, directory + '/receipt.json'))
                paths.update(t['path'] for t in receipt['tool_inputs'])
    return sorted(paths)


def comparison_bytes(root, blob, model, row):
    prefix = BASE + '/abi/x3'
    linked = read(root, prefix + '.exe'); linked_model = parse(linked)
    sm = symbols(read(root, prefix + '.sym').decode('ascii'))
    raw = contribution(linked, linked_model, 0, sm[(0, '_recovered')], 312)
    normalized = bytearray(raw)
    for f in row['field_identities']:
        base = 32766 if f['kind'] == 'A4' else f['site'] + 2 + (30316 if f['kind'] == 'CALL' else 0)
        normalized[f['field']:f['field'] + 2] = (f['original_offset'] - base).to_bytes(2, 'big', signed=True)
    require(bytes(normalized) == contribution(blob, model, 0, 30316, 312), 'startup exact comparison differs')
    return raw, bytes(normalized)


def proof(root, blob, model, ledger, row):
    raw, normalized = comparison_bytes(root, blob, model, row)
    paths = set(inputs(root))
    for fid in ANCHORS:
        paths.update(ledger['functions'][fid][k] for k in ('source', 'proof'))
    return dict(schema_version=1, id=ID, state='FUNCTION_WITH_DATA_MATCH', kind='SDK_DERIVED_MIXED_OBJECT',
                source=SOURCE, source_sha256=row['source_sha256'], game_sha256=sha256(blob),
                original=row['original'], size=312, extent_basis=row['extent_basis'],
                partitions=row['partitions'], c_compiler_bytes=304, sdk_asm_bytes=6, compiler_literal_bytes=2,
                field_identities=row['field_identities'],
                comparison=dict(verdict='EQUAL', complete_object=True, actual_sha256=sha256(raw),
                                normalized_sha256=sha256(normalized), length=312, owned_data=0, owned_bss=0),
                input_graph=[dict(path=p, sha256=sha256(read(root, p))) for p in sorted(paths)],
                original_storage_ownership='UNKNOWN', original_filename='UNKNOWN', original_tu='UNKNOWN',
                exact_historical_library_release='UNKNOWN', natural_root_layout_proved=False)


def load(root, blob, model, analysis, promotions, ledger, other_rows=()):
    root = Path(root).resolve()
    item = ledger.get('mixed_source_objects', {}).get(ID)
    if not canonical_path(root, FACT).exists():
        require(item is None, 'canonical startup fact missing')
        return []
    report = verify(root, blob, model, analysis, promotions, ledger)
    fresh = producer_verify(root, control_base=REFRESH)
    require(fresh['source_sha256'] == report['source_sha256'], 'fresh startup source differs')
    for scope, prefix in [('abi', 'x3'), ('partition', 'marked')]:
        for name in (prefix, 'root', 'overlay'):
            for suffix in ('.asm', '.o') + (('.exe', '.sym') if name == prefix else ()):
                require(read(root, REFRESH + '/' + scope + '/' + name + suffix) ==
                        read(root, BASE + '/' + scope + '/' + name + suffix), 'fresh startup artifact differs')
    matches = [f for f in analysis['functions'] if f['id'] == ID]
    require(len(matches) == 1, 'startup descent entry missing or duplicated')
    cfg = matches[0]
    require(cfg['hunk'] == 0 and cfg['start'] == 30316 and cfg['end'] == 30626 and cfg['size'] == 310 and
            cfg['extent_status'] == 'CLOSED_CFG' and
            cfg['sha256'] == sha256(contribution(blob, model, 0, 30316, 310)), 'startup descent extent conflicts')
    require(ID not in ledger['functions'], 'startup cannot replace ordinary C proof')
    require(not any(f['id'] != ID and f['hunk'] == 0 and 30316 < f['start'] < 30628 for f in analysis['functions']),
            'startup complete object contains another entry')
    require(any(f['hunk'] == 0 and f['start'] == 30628 for f in analysis['functions']), 'startup literal lacks next entry')
    require(not any(p['hunk'] == 0 and p['start'] < 30628 and p['end'] > 30316 for p in promotions),
            'startup overlaps accepted source')
    require(not any(r['original']['hunk'] == 0 and r['original']['start'] < 30628 and
                    r['original']['end'] > 30316 for r in other_rows), 'startup overlaps mixed source')
    row = dict(id=ID, status=report['status'], acceptance=False,
               fact=dict(path=FACT, sha256=sha256(read(root, FACT))), original=dict(hunk=0, start=30316, end=30628),
               size=312, source_sha256=report['source_sha256'],
               cfg_extent={k: cfg[k] for k in ('start', 'end', 'size', 'extent_status', 'confidence')},
               extent_basis='PINNED_SDK_DERIVATION_AND_COMPLETE_LINKED_OBJECT',
               partitions=[dict(language=k, start=30316 + a, end=30316 + b) for k, a, b in PARTS],
               c_compiler_bytes=304, sdk_asm_bytes=6, compiler_literal_bytes=2,
               field_identities=report['field_identities'], original_storage_ownership='UNKNOWN',
               original_filename='UNKNOWN', original_tu='UNKNOWN')
    comparison_bytes(root, blob, model, row)
    if item:
        require(item.get('source') == SOURCE and item.get('proof') == PROOF and
                item.get('state') == 'FUNCTION_WITH_DATA_MATCH', 'startup canonical identity differs')
        source, raw = read(root, SOURCE), read(root, PROOF)
        require(source == source_views(root)['candidate'].encode('ascii') and sha256(source) == item['source_sha256'],
                'startup canonical source differs')
        require(sha256(raw) == item['proof_sha256'] and json.loads(raw) == proof(root, blob, model, ledger, row),
                'startup canonical proof does not rederive')
        row.update(status='FUNCTION_WITH_DATA_MATCH', acceptance=True, source=SOURCE, proof=PROOF)
    return [row]


def contributions(root, blob, model, row):
    _, normalized = comparison_bytes(root, blob, model, row)
    categories = {'C_COMPILER': 'RECOVERED_C', 'ASM': 'RECOVERED_ASM', 'COMPILER_OWNED_DATA': 'COMPILER_OWNED_DATA'}
    return [dict(id=ID + '_part%d' % i, hunk=0, start=p['start'], end=p['end'],
                 bytes=normalized[p['start'] - 30316:p['end'] - 30316], relocations=[], category=categories[p['language']])
            for i, p in enumerate(row['partitions'])]
