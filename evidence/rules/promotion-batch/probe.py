"""Run the supervisor path with a real shared suite in a retained scratch workspace."""
import json
from pathlib import Path
import shutil
import sys
import time
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import check_function
import promote_batch
from common import require, sha256, write_json
from recovery_evidence import load_promotions
from analysis_support import game
from recovery_state import evidence


def canonical_hashes():
    paths = [ROOT / 'recovery/ledger.json']
    paths += list((ROOT / 'src/recovered').rglob('*.c')) + list((ROOT / 'recovery/proofs').glob('*.json'))
    return {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()) for p in paths}


def main():
    before = canonical_hashes()
    scratch = ROOT / 'build/promotion-control' / uuid.uuid4().hex
    require(scratch.resolve().is_relative_to((ROOT / 'build/promotion-control').resolve()), 'scratch path escapes control directory')
    (scratch / 'tools').mkdir(parents=True)
    for path in (ROOT / 'tools').glob('*.py'):
        shutil.copyfile(path, scratch / 'tools' / path.name)
    requests = []
    for fid in ('ov14_F_03AE', 'ov03_F_154E'):
        path = scratch / 'inputs' / (fid + '.c')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / 'src/recovered' / fid.split('_F_')[0] / path.name).read_bytes())
        requests.append(dict(id=fid, source=str(path), profiles=['aztec36']))
    ledger = scratch / 'recovery/ledger.json'
    write_json(ledger, dict(schema_version=1, functions={}, attempts={}, blockers={}))
    gate, calls = check_function.regression_receipt, []
    def real_gate():
        started = time.perf_counter()
        with patch.object(check_function, 'ROOT', ROOT):
            value = gate()
        calls.append(dict(elapsed_seconds=time.perf_counter() - started, receipt=value))
        return value
    with patch.object(check_function, 'ROOT', scratch), patch.object(check_function, 'LEDGER', ledger), \
         patch.object(check_function, 'recovery', lambda: json.loads(ledger.read_text())), \
         patch.object(check_function, 'regression_receipt', side_effect=real_gate), \
         patch.object(check_function, 'save_rank'):
        result = promote_batch.run(requests)
    require(len(calls) == 1, 'batch did not use exactly one real regression gate')
    blob, model, _ = game()
    require(len(load_promotions(scratch, blob, model, evidence())) == 2, 'proof loader rejected control batch')
    require(canonical_hashes() == before, 'control changed canonical repository state')
    report = dict(schema_version=1, status='PASSED', functions=result['functions'],
                  policy='Already-owned source controls in a scratch workspace; zero new canonical coverage.',
                  scratch=scratch.relative_to(ROOT).as_posix(), transaction=result['transaction'],
                  regression_calls=calls, independent_proof_loader_count=2, canonical_repository_unchanged=True,
                  implementation={p: sha256((ROOT / 'tools' / p).read_bytes()) for p in
                                  ('promote_batch.py', 'recovery_transaction.py', 'check_function.py')})
    write_json(Path(__file__).with_name('report.json'), report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
