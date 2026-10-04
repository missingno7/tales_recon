"""Measure real isolated cached checks with and without bounded game reuse."""
import json
from pathlib import Path
import statistics
import sys
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import check_function
import compiler_oracle
import compile_queue
from common import require, sha256, json_bytes, write_json
from evidence_snapshot import snapshot


def canonical_identity():
    ledger_path = ROOT / 'recovery/ledger.json'
    ledger = json.loads(ledger_path.read_text())
    paths = {ledger_path}
    for item in ledger['functions'].values():
        paths.update((ROOT / item[name]) for name in ('source', 'proof'))
    return {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()) for p in sorted(paths)}


def requests():
    analysis = {f['id']: f for f in check_function.evidence()['functions']}
    ledger = check_function.recovery()
    result = []
    excluded = []
    for fid, item in sorted(ledger['functions'].items()):
        f = analysis[fid]
        if item['state'] != 'FUNCTION_CODE_MATCH' or any(
                c['basis'] == 'PC_RELATIVE' and c['hunk'] == f['hunk'] and c['id'] != fid
                for c in f['direct_callees']):continue
        proof = json.loads((ROOT / item['proof']).read_text())
        profile = proof['compiler']['profile']
        if proof['compiler']['source_sha256'] != item['source_sha256']:continue
        request = dict(id=fid, source=str(ROOT / item['source']), profiles=[profile],
                       extra_libraries=[x['library'] for x in proof['compiler'].get('additional_libraries', [])])
        trial = dict(source=(ROOT / item['source']).read_text(), profile=profile,
                     target_node=f['hunk'] - 2 if f['node'] != 'resident' and f['hunk'] >= 3 else 1,
                     extra_libraries=request['extra_libraries'])
        key = compile_queue.trial_key(trial)
        if not compile_queue.is_cached(key):
            excluded.append(dict(id=fid, reason='CURRENT_RECIPE_NOT_CACHED', cache_key=key))
            continue
        result.append(request)
        if len(result) == 12:break
    require(len(result) == 12, 'need twelve canonical standalone controls')
    return result, excluded


def cached_only(trials):
    result = [compiler_oracle.cached(compile_queue.trial_key(trial)) for trial in trials]
    require(all(result), 'control requires existing cache artifacts; no compiler launch allowed')
    return result


def main():
    before = canonical_identity()
    work, excluded = requests()
    measured = {False: [], True: []}
    expected = None
    stats = []
    # Alternate order to reduce filesystem-warming bias. All exact comparison
    # and cache artifact checks remain real, and no promotion or emulator runs.
    for enabled in (False, True, True, False, False, True):
        started = time.perf_counter()
        with snapshot(enabled) as state, patch.object(check_function, 'compile_many', cached_only):
            reports = check_function.check_many(work, promote_equal=False, isolated=True)
        elapsed = time.perf_counter() - started
        require(all(r['verdict'] == 'EQUAL' and r['cache_hit'] for r in reports),
                'control lost an exact cached match')
        signature = sha256(json_bytes(reports))
        if expected is None:expected = signature
        require(signature == expected, 'snapshot changed exact reports')
        measured[enabled].append(elapsed)
        stats.append(dict(enabled=enabled, seconds=elapsed, hits=state.hits, misses=state.misses,
                          invalidations=state.invalidations, hash_seconds=state.hash_seconds,
                          derive_seconds=state.derive_seconds))
    require(canonical_identity() == before, 'isolated control changed canonical recovery')
    baseline, reused = (statistics.median(measured[enabled]) for enabled in (False, True))
    report = dict(schema_version=1, status='PASSED',
                  policy='Performance control only; no new reconstruction proof or canonical writes.',
                  functions=[r['id'] for r in work], requests=len(work), repetitions=3,
                  baseline_median_seconds=baseline, snapshot_median_seconds=reused,
                  speedup=baseline / reused, exact_reports_sha256=expected,
                  all_reports_identical=True, all_verdicts='EQUAL', worker_invocations=0,
                  canonical_state_unchanged=True, measurements=stats,
                  preflight_exclusions=excluded,
                  implementation_sha256={name: sha256((ROOT / 'tools' / name).read_bytes()) for name in
                                         ('evidence_snapshot.py', 'analysis_support.py', 'check_function.py', 'check_unit.py')})
    write_json(Path(__file__).with_name('report.json'), report)
    print(json.dumps(report))


if __name__ == '__main__':main()
