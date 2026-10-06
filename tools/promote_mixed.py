"""Bounded canonical admission for the independently verified SDK mixed object."""
import argparse
import json
from pathlib import Path
import re

from analysis_support import ROOT, game
from common import require, sha256, write_json
from recovery_state import evidence, canonical_state
from recovery_evidence import load_promotions
from resident_mixed import FACT, SOURCE, PROOF, expected_source, load_source_objects, source_object_proof, source_object_inputs
from repo_paths import canonical_path


def validation_inputs(root):
    paths = set(source_object_inputs(root)) | {'recovery/ledger.json'}
    ledger = json.loads(canonical_path(root, 'recovery/ledger.json').read_bytes())
    for item in ledger['functions'].values():
        paths.update([item['source'], item['proof']])
    paths.update(p.relative_to(root).as_posix() for p in (root / 'tools').glob('*.py'))
    return [dict(path=p, sha256=sha256(canonical_path(root, p).read_bytes())) for p in sorted(paths)]


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
    row, = load_source_objects(ROOT, blob, model, analysis, promotions, ledger)
    proof = source_object_proof(ROOT, blob, model, analysis, ledger, row)
    if args.verify_only or row['acceptance']:
        print('EQUAL complete mixed object:196 C/42 ASM bytes; acceptance=' + str(row['acceptance']))
        return
    require(args.validation_inputs and args.regression_log, 'promotion requires unchanged validation inputs and complete regression log')
    require(json.loads(args.validation_inputs.read_bytes()) == validation_inputs(ROOT),
            'promotion validation inputs changed; revalidate unchanged source against current dependencies')
    log = args.regression_log.read_bytes().decode('utf-8', errors='replace')
    require(re.search(r'Ran \d+ tests in [\d.]+s', log) and
            re.search(r'^OK(?: \(skipped=\d+\))?\s*$', log, re.M), 'promotion regression incomplete or failed')
    source = expected_source(ROOT).encode('ascii')
    path = canonical_path(ROOT, SOURCE)
    require(not path.exists() or path.read_bytes() == source, 'canonical mixed source already differs')
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(source)
    write_json(ROOT / PROOF, proof)
    ledger.setdefault('mixed_source_objects', {})[row['id']] = dict(state='FUNCTION_CODE_MATCH',
        source=SOURCE, source_sha256=sha256(source), proof=PROOF, proof_sha256=sha256((ROOT / PROOF).read_bytes()))
    write_json(ROOT / 'recovery/ledger.json', canonical_state(ledger))
    # Re-read through the canonical consumer, preserving normal C admission.
    accepted, = load_source_objects(ROOT, blob, model, analysis, promotions, ledger)
    require(accepted['acceptance'], 'mixed admission did not reload')
    print('Promoted complete mixed source object:196 C/42 ASM bytes at FUNCTION_CODE_MATCH.')


if __name__ == '__main__':
    main()
