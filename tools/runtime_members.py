"""Prove complete library members against the immutable game.

Each spec extracts members from a pinned library with ``lb -x`` and links
them.  A single member is linked alone; an ordered group (for example
m.lib's ten-byte FFP operator stubs, which each ``jmp`` to the following
``amiga_ffp`` member) is linked in library order, and only its leading stub
members form the contribution, because the common member that follows calls
other library code.  A contribution must own CODE only, be relocation-free,
match the original exactly once and carry its entries from the linked symbol
map.  This identifies runtime code inside the resident image; it adds no game
source, selects no compiler release and does not move the runtime floor.
"""
import argparse
import json
from pathlib import Path

from analysis_support import game, ROOT
from common import require, sha256, write_json
from overlay_experiment import symbols
from runtime_match import code, find_matches

OUTPUT = 'evidence/experiments/runtime-members.json'
# Separate opt-in ledger preserves legacy runtime-members.json receipts.
RELOCATED_OUTPUT = 'evidence/experiments/runtime-members-relocated.json'
NATURAL_OUTPUT = 'evidence/experiments/runtime-members-natural.json'
TAIL_OUTPUT = 'evidence/experiments/runtime-members-tail.json'
SEGLOAD_RELOCATIONS = [
    dict(offset=0x28, type='HUNK_RELOC32', width=4,
         target=dict(kind='ROOT_HUNK_ORIGIN', hunk=0, type='CODE', addend=8)),
    dict(offset=0x3e, type='HUNK_RELOC32', width=4,
         target=dict(kind='ROOT_HUNK_ORIGIN', hunk=1, type='DATA', addend=0)),
]
RELOCATED_SPECS = (
    dict(job='runtime-segload-c36', prefix='segload36', profile='aztec36',
         library='aztec-3.6a/SYS1/lib/c.lib', members=['segload'], contribution=['segload'],
         relocation_identity=SEGLOAD_RELOCATIONS),
)


def relocation_identity(model, extent):
    """Complete site/type/width/root-origin target identities; no masking.

    Deliberately bounded to structural root hunk references. Equal addends
    do not identify arbitrary objects or prove the referenced data contents.
    """
    hunk, base, size = extent['hunk'], extent['offset'], extent['size']
    result = []
    for r in model['relocations']:
        if r['source_hunk'] != hunk or r['source_offset'] >= base+size or r['source_offset']+r['width'] <= base:
            continue
        require(base <= r['source_offset'] and r['source_offset']+r['width'] <= base+size,
                'runtime relocation straddles contribution')
        target = next((h for h in model['hunks'] if h['number'] == r['target_hunk']), None)
        require(target and target.get('node') == 'resident' and target['number'] in (0, 1),
                'runtime relocation target is not a root origin')
        require(target['type'] == ('CODE' if target['number'] == 0 else 'DATA'),
                'runtime root hunk target type differs')
        result.append(dict(offset=r['source_offset']-base, type=r['type'], width=r['width'],
                           target=dict(kind='ROOT_HUNK_ORIGIN', hunk=target['number'],
                                       type=target['type'], addend=r['addend_raw'])))
    result.sort(key=lambda r: (r['offset'], r['type'], r['width']))
    require(len({r['offset'] for r in result}) == len(result), 'duplicate runtime relocation')
    return result


def relocated_contribution(spec, original, model, *, root=ROOT):
    """Prove the complete segload object, exports and structural references.

    Its object owns zero DATA/BSS; the DATA-origin relocation is an external
    reference. Nonzero ownership fails rather than being clipped or ignored.
    """
    from hunk import parse
    require(spec['members'] == spec['contribution'] == ['segload'] and
            spec['relocation_identity'] == SEGLOAD_RELOCATIONS, 'unsupported relocated runtime recipe')
    job = Path(root) / 'build/worker-jobs' / spec['job']
    work = job / 'sys/work'
    receipt = json.loads((job / 'result.json').read_text())
    require(receipt['all_steps_succeeded'], 'relocated runtime link failed')
    artifacts = {a['path']: a['sha256'] for a in receipt['artifacts']}
    for name in (spec['prefix']+'.o', spec['prefix'], spec['prefix']+'.sym'):
        require(name in artifacts and sha256((work/name).read_bytes()) == artifacts[name],
                'missing/changed relocated runtime artifact')
    library = 'toolchain/installed/' + spec['library']
    digest = sha256((Path(root)/library).read_bytes())
    require(any(p['path'] == library and p['sha256'] == digest
                for p in receipt['request']['pinned_inputs']), 'relocated runtime library is not pinned')
    steps = [s['command'] for s in receipt['steps']]
    prefix = spec['prefix']
    require('Old2:bin/lb Old1:lib/c.lib -x segload' in steps and
            'copy segload.o '+prefix+'.o' in steps and
            'Old1:bin/ln -m -t -o '+prefix+' '+prefix+'.o' in steps,
            'relocated runtime standalone producer recipe differs')
    obj = (work/(prefix+'.o')).read_bytes()
    size = object_code_size(obj)
    require(size == 244, 'segload complete object extent differs')
    data = (work/prefix).read_bytes(); linked_model = parse(data)
    require([(h['number'], h['type']) for h in linked_model['hunks']] ==
            [(0, 'CODE'), (1, 'DATA'), (2, 'BSS')], 'segload standalone hunk layout differs')
    h = linked_model['hunks'][0]
    require(h['initialized_size'] == size and h['allocated_size'] == size and
            all(x['initialized_size'] == x['allocated_size'] == 0 for x in linked_model['hunks'][1:]),
            'segload link owns extra content/storage')
    expected = spec['relocation_identity']
    require(relocation_identity(linked_model, dict(hunk=0, offset=0, size=size)) == expected and
            len(linked_model['relocations']) == len(expected), 'segload linked relocation identities differ')
    raw = data[h['content_offset']:h['content_offset']+size]
    matches = []
    for oh in model['hunks']:
        if oh['number'] != 0 or oh['type'] != 'CODE' or oh['node'] != 'resident': continue
        payload = original[oh['content_offset']:oh['content_offset']+oh['initialized_size']]
        at = 0
        while (at := payload.find(raw, at)) >= 0:
            extent = dict(hunk=0, offset=at, size=size)
            if at % 2 == 0 and relocation_identity(model, extent) == expected: matches.append(extent)
            at += 1
    require(len(matches) == 1, 'segload bytes/relocations do not match uniquely')
    sm = symbols((work/(prefix+'.sym')).read_text())
    require(sm.get((0, '__H0_org')) == sm.get((1, '__H1_org')) == 0,
            'segload origin symbols differ')
    entries = sorted((dict(name=n, offset=o) for (hn,n),o in sm.items()
                      if hn == 0 and not n.startswith('__H') and 0 <= o < size),
                     key=lambda e: (e['offset'], e['name']))
    require(entries == [dict(name='_segload', offset=0), dict(name='.segload', offset=18)],
            'segload exports differ')
    return dict(member='segload', members=['segload'], profile=spec['profile'], library_sha256=digest,
                object_sha256s={'segload':sha256(obj)}, code_sha256=sha256(raw), size=size,
                original=matches[0], entries=entries, relocation_identity=expected,
                owned_data_size=0, owned_bss_size=0,
                job_receipt_sha256=sha256((job/'result.json').read_bytes()))


def analyze_natural():
    from runtime_natural_members import verify
    return verify(ROOT)


def analyze_tail():
    from runtime_tail_members import verify
    return verify(ROOT)


def analyze_relocated():
    original, model, _ = game()
    return dict(schema_version=1, game_sha256=sha256(original), status='COMPLETE_RUNTIME_CODE_MATCH',
                contributions=[relocated_contribution(s, original, model) for s in RELOCATED_SPECS],
                limitations=['Root hunk-origin RELOC32 identities only; no normalization.',
                             'Nonzero owned DATA/BSS requires a separate complete ownership proof.'],
                reconstructed_game_functions=0, exact_compiler_release_selected=False)


# prefix: linked output name in the job; members: lb -x names, in link order;
# contribution: leading members whose code forms the proven contribution.
SPECS = (
    dict(job='runtime-debug-c36-20261013', prefix='kputchar36', profile='aztec36',
         library='aztec-3.6a/SYS1/lib/c.lib', members=['kputchar'], contribution=['kputchar']),
    dict(job='runtime-ffp-m36-20261013', prefix='ffp36', profile='aztec36',
         library='aztec-3.6a/SYS1/lib/m.lib',
         members=['fadd', 'fcmp', 'fneg', 'ftst', 'ffix', 'fsub', 'fdiv', 'fflt', 'fmul', 'ffp'],
         contribution=['fadd', 'fcmp', 'fneg', 'ftst', 'ffix', 'fsub', 'fdiv', 'fflt', 'fmul']),
)


def object_code_size(obj):
    require(obj[:2] in (b'AJ', b'CJ'), 'unsupported object')
    require(obj[14:22] == bytes(8), 'runtime member owns data/BSS')
    return int.from_bytes(obj[10:14], 'big')


def contribution(spec, original, model):
    job = ROOT / 'build/worker-jobs' / spec['job']
    receipt = json.loads((job / 'result.json').read_text())
    work = job / 'sys/work'
    for item in receipt['artifacts']:
        require(sha256((work / item['path']).read_bytes()) == item['sha256'], 'runtime member artifact changed')
    require(receipt['all_steps_succeeded'] or spec['members'] == spec['contribution'],
            'runtime member group link failed: ' + spec['prefix'])
    if spec['members'] == spec['contribution'] and len(spec['members']) == 1:
        obj = (work / (spec['prefix'] + '.o')).read_bytes()
        size = object_code_size(obj)
        linked = code((work / spec['prefix']).read_bytes())
        require(len(linked) == (size + 3) // 4 * 4 and linked[size:] == bytes((-size) % 4), 'runtime member extent mismatch')
        objects = {spec['members'][0]: sha256(obj)}
    else:
        # The group links in the given order: the contribution is the exact
        # concatenation of its members' own CODE at the start of the link.
        sizes = [object_code_size((work / (m + '.o')).read_bytes()) for m in spec['contribution']]
        size = sum(sizes)
        from hunk import parse
        data = (work / spec['prefix']).read_bytes(); model_linked = parse(data)
        h = next(x for x in model_linked['hunks'] if x['type'] == 'CODE')
        linked = data[h['content_offset']:h['content_offset'] + h['initialized_size']]
        require(not any(r['source_hunk'] == h['number'] and r['source_offset'] < size for r in model_linked['relocations']),
                'runtime member group contribution has relocations')
        objects = {m: sha256((work / (m + '.o')).read_bytes()) for m in spec['contribution']}
    raw = linked[:size]
    matches = find_matches(original, model, raw)
    require(len(matches) == 1, 'runtime member does not match uniquely: ' + spec['prefix'])
    entries = sorted((dict(name=n, offset=o) for (h, n), o in symbols((work / (spec['prefix'] + '.sym')).read_text()).items()
                      if h == 0 and not n.startswith('__H') and 0 <= o < size), key=lambda e: (e['offset'], e['name']))
    require(entries, 'runtime member has no entries')
    return dict(member=spec['members'][0] if len(spec['contribution']) == 1 else '+'.join(spec['contribution']),
                members=spec['contribution'], profile=spec['profile'],
                library_sha256=sha256((ROOT / 'toolchain/installed' / spec['library']).read_bytes()),
                object_sha256s=objects, code_sha256=sha256(raw), size=size, original=matches[0], entries=entries,
                job_receipt_sha256=sha256((job / 'result.json').read_bytes()))


def analyze():
    original, model, _ = game()
    return dict(schema_version=2, game_sha256=sha256(original), status='COMPLETE_RUNTIME_CODE_MATCH',
                contributions=[contribution(spec, original, model) for spec in SPECS],
                reconstructed_game_functions=0, exact_compiler_release_selected=False,
                limitations=['Only relocation-free complete member contributions are accepted.',
                             'Identifies runtime ownership of these bytes; no game source and no release selection.'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--relocated', action='store_true')
    mode.add_argument('--natural-routes', action='store_true')
    mode.add_argument('--tail-leaves', action='store_true')
    args = ap.parse_args()
    result = analyze_tail() if args.tail_leaves else analyze_natural() if args.natural_routes else analyze_relocated() if args.relocated else analyze()
    output = TAIL_OUTPUT if args.tail_leaves else NATURAL_OUTPUT if args.natural_routes else RELOCATED_OUTPUT if args.relocated else OUTPUT
    write_json(ROOT / output, result)
    print(json.dumps(dict(status=result['status'], contributions=[(c['member'], c['original'], c['size']) for c in result['contributions']])))
