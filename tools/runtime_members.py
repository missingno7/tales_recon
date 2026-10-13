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
    argparse.ArgumentParser(description=__doc__).parse_args()
    result = analyze()
    write_json(ROOT / OUTPUT, result)
    print(json.dumps(dict(status=result['status'], contributions=[(c['member'], c['original'], c['size']) for c in result['contributions']])))
