"""Prove complete library members linked alone against the immutable game.

Each member is extracted from a pinned library with ``lb -x``, linked alone,
and must own CODE only, be relocation-free and match the original exactly
once.  Entries come from the member's own linked symbol map.  This identifies
runtime contributions inside the resident image (for example c.lib's
``kputchar`` debug-output member below the runtime tail); it adds no game
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
# (job prefix, profile, pinned library, library member)
MEMBERS = (('kputchar36', 'aztec36', 'aztec-3.6a/SYS1/lib/c.lib', 'kputchar'),)


def analyze(job):
    receipt = json.loads((job/'result.json').read_text())
    work = job/'sys/work'
    for item in receipt['artifacts']:
        require(sha256((work/item['path']).read_bytes()) == item['sha256'], 'runtime member artifact changed')
    original, model, _ = game()
    contributions = []
    for prefix, profile, library, member in MEMBERS:
        steps = [s for s in receipt['steps'] if prefix in s['command'] or (' -x '+member) in s['command']]
        require(steps and all(s['returncode'] == 0 for s in steps), 'runtime member extraction or link failed: '+member)
        obj = (work/(prefix+'.o')).read_bytes()
        require(obj[:2] in (b'AJ', b'CJ'), 'unsupported object')
        size = int.from_bytes(obj[10:14], 'big')
        require(obj[14:22] == bytes(8), 'runtime member owns data/BSS: '+member)
        linked = code((work/prefix).read_bytes())
        require(size > 0 and len(linked) == (size+3)//4*4 and linked[size:] == bytes((-size) % 4), 'runtime member extent mismatch')
        raw = linked[:size]
        matches = find_matches(original, model, raw)
        require(len(matches) == 1, 'runtime member does not match uniquely: '+member)
        entries = sorted((dict(name=n, offset=o) for (h, n), o in symbols((work/(prefix+'.sym')).read_text()).items()
                          if h == 0 and not n.startswith('__H')), key=lambda e: (e['offset'], e['name']))
        require(entries and all(0 <= e['offset'] < size for e in entries), 'invalid runtime member entries')
        contributions.append(dict(member=member, profile=profile,
                                  library_sha256=sha256((ROOT/'toolchain/installed'/library).read_bytes()),
                                  object_sha256=sha256(obj), code_sha256=sha256(raw), size=size,
                                  original=matches[0], entries=entries))
    return dict(schema_version=1, game_sha256=sha256(original), status='COMPLETE_RUNTIME_CODE_MATCH',
                job_receipt_sha256=sha256((job/'result.json').read_bytes()), contributions=contributions,
                reconstructed_game_functions=0, exact_compiler_release_selected=False,
                limitations=['Library members linked alone; only relocation-free complete contributions are accepted.',
                             'Identifies runtime ownership of these bytes; no game source and no release selection.'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('job', type=Path)
    result = analyze(ap.parse_args().job)
    write_json(ROOT/OUTPUT, result)
    print(json.dumps(dict(status=result['status'], contributions=[(c['member'], c['original'], c['size']) for c in result['contributions']])))
