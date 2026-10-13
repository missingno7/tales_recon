"""Re-derive the curated ov04 terminal-padding claim after a canonical ov04 change.

The claim (evidence/contributions/padding.json) binds every canonical ov04
member source, the proven object partition, the compiler recipe, the produced
executable and the retained raw unit source.  A canonical replacement inside
ov04 therefore invalidates it by design.  This tool derives the recipe from
the current canonical state, compiles that exact trial, records the produced
object/executable/padding hashes and the retained unit source, and then
requires the unchanged strict loader (load_terminal_padding) to accept the
new claim.  Nothing is copied from the original bytes; the loader still
checks that the two emitted bytes are zero and equal to the original.
"""
import argparse
import json
from pathlib import Path

from analysis_support import game, ROOT
from common import require, sha256, write_json
from recovery_evidence import PADDING_INPUT, load_promotions, load_terminal_padding, terminal_padding_recipe

UNIT = 'evidence/rules/ov04-terminal-padding/unit.c'


def refresh(root=ROOT):
    blob, model, _ = game()
    analysis = json.loads((root / 'evidence/functions/ledger.json').read_text())
    promoted = load_promotions(root, blob, model, analysis)
    ledger = json.loads((root / 'recovery/ledger.json').read_text())
    previous = json.loads((root / PADDING_INPUT).read_text())
    require(len(previous['claims']) == 1, 'padding refresh expects one ov04 claim')
    entry = previous['claims'][0]['entry']
    recipe, members, names, combined, context = terminal_padding_recipe(root, blob, model, analysis, promoted, ledger, entry)
    trial = context['trial']
    if trial.get('object_profiles'):
        import mixed_profile_oracle, compiler_oracle
        compiled = mixed_profile_oracle.compile_many([trial], base=compiler_oracle.compile_many)[0]
    else:
        from compiler_oracle import compile_many
        compiled = compile_many([trial])[0]
    require(compiled['status'] == 'COMPILED' and compiled['cache_key'] == recipe['cache_key'], 'padding trial did not compile to its recipe')
    c = compiled['contribution']; directory = Path(compiled['directory']); prefix = compiled['prefix']
    hashes = [sha256((directory / ((prefix if label == 'candidate' else prefix + '_' + label) + '.o')).read_bytes())
              for label in c.get('object_labels', recipe['compiler']['object_labels'])]
    executable = (directory / (prefix + '.exe')).read_bytes()
    from hunk import parse
    produced = parse(executable); h = next(x for x in produced['hunks'] if x['number'] == c['hunk'])
    payload = executable[h['content_offset'] + recipe['start']:h['content_offset'] + recipe['end']]
    (root / UNIT).write_bytes(combined.encode('ascii'))
    claim = dict(entry=entry, executable_sha256=sha256(executable), object_sha256s=hashes,
                 padding_sha256=sha256(payload), recipe=recipe,
                 unit_source=dict(path=UNIT, sha256=sha256(combined.encode('ascii'))))
    document = dict(previous, claims=[claim])
    out = load_terminal_padding(root, blob, model, analysis, promoted, ledger, document=document)
    require(len(out) == 1 and out[0]['category'] == 'CLASSIFIED_PADDING', 'strict padding loader rejected the refreshed claim')
    write_json(root / PADDING_INPUT, document)
    return out[0]


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    row = refresh()
    print(json.dumps(dict(id=row['id'], start=row['start'], end=row['end'])))
