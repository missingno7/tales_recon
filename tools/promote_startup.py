"""Canonical startup admission after unchanged full regression and fresh controls."""
from names import to_mechanical
import argparse
import json
import re

from analysis_support import ROOT, game
from common import require, sha256, write_json
from recovery_state import evidence, canonical_state
from recovery_evidence import load_promotions
from repo_paths import canonical_path
from startup_recovery import ID, SOURCE, PROOF, inputs, load, proof
from startup_producer import source_views
from pathlib import Path


def validation_inputs(root):
    paths = set(inputs(root)) | {'recovery/ledger.json', 'evidence/fixture-lock.json', 'evidence/functions/ledger.json'}
    ledger = json.loads(canonical_path(root, 'recovery/ledger.json').read_bytes())
    for item in list(ledger['functions'].values()) + list(ledger.get('mixed_source_objects', {}).values()):
        paths.update(item[k] for k in ('source', 'proof'))
    paths.update(p.relative_to(root).as_posix() for p in (root / 'tools').glob('*.py'))
    paths.update(p.relative_to(root).as_posix() for p in (root / 'tests').glob('*.py'))
    return [dict(path=p, sha256=sha256((to_mechanical(canonical_path(root, p).read_bytes()) if p.startswith('src/') else canonical_path(root, p).read_bytes()))) for p in sorted(paths)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--record-inputs', type=Path)
    parser.add_argument('--validation-inputs', type=Path)
    parser.add_argument('--regression-log', type=Path)
    args = parser.parse_args()
    if args.record_inputs:
        write_json(args.record_inputs, validation_inputs(ROOT))
        return
    blob, model, _ = game(); analysis = evidence()
    ledger = json.loads((ROOT / 'recovery/ledger.json').read_bytes())
    promotions = load_promotions(ROOT, blob, model, analysis)
    from resident_mixed import load_exit_source_objects
    others = load_exit_source_objects(ROOT, blob, model, analysis, promotions, ledger)
    row, = load(ROOT, blob, model, analysis, promotions, ledger, others)
    result = proof(ROOT, blob, model, ledger, row)
    if args.verify_only or row['acceptance']:
        print('EQUAL complete startup:304 C/6 ASM/2 literal bytes; acceptance=' + str(row['acceptance']))
        return
    require(args.validation_inputs and args.regression_log, 'startup promotion requires unchanged inputs and full regression')
    require(json.loads(args.validation_inputs.read_bytes()) == validation_inputs(ROOT), 'startup validation inputs changed')
    log = args.regression_log.read_bytes().decode('utf-8', errors='replace')
    require(re.search(r'Ran \d+ tests in [\d.]+s', log) and
            re.search(r'^OK(?: \(skipped=\d+\))?\s*$', log, re.M), 'startup regression incomplete or failed')
    source = source_views(ROOT)['candidate'].encode('ascii')
    path = canonical_path(ROOT, SOURCE)
    require(not path.exists() or to_mechanical(path.read_bytes()) == source, 'startup existing canonical source differs')
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(source)
    write_json(ROOT / PROOF, result)
    ledger.setdefault('mixed_source_objects', {})[ID] = dict(state='FUNCTION_WITH_DATA_MATCH',
        source=SOURCE, source_sha256=sha256(source), proof=PROOF, proof_sha256=sha256((ROOT / PROOF).read_bytes()))
    write_json(ROOT / 'recovery/ledger.json', canonical_state(ledger))
    accepted, = load(ROOT, blob, model, analysis, promotions, ledger, others)
    require(accepted['acceptance'], 'startup admission did not reload')
    print('Promoted complete startup:304 C/6 ASM/2 literal bytes at FUNCTION_WITH_DATA_MATCH.')


if __name__ == '__main__':
    main()
