"""Compare the unified queue with unchanged legacy oracle paths; never promotes."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import compiler_oracle
import mixed_profile_oracle
import compile_queue
from common import require, sha256, write_json


def trials(label):
    ordinary = dict(source='/* queue probe %s */\nrecovered(x) int x; { return x + 73; }\n' % label,
                    profile='aztec36')
    objects = [dict(source='/* queue probe %s */\nextern int helper();\nrecovered() { return helper() + 7; }\n' % label),
               dict(source='extern int value;\nhelper() { return value; }\n')]
    mixed = dict(source=''.join(o['source'] for o in objects), profile='aztec36', objects=objects,
                 local_functions=['helper'], object_profiles=['aztec36', 'aztec36-large-data'])
    return [ordinary, mixed]


def main():
    baseline = trials('legacy')
    expected = [compiler_oracle.compile_many([baseline[0]])[0],
                mixed_profile_oracle.compile_many([baseline[1]])[0]]
    candidates = trials('combined')
    actual = compile_queue.compile_many(candidates)
    jobs = {r['worker_job'] for r in actual}
    require(len(jobs) == 1, 'combined trials did not share one guest job')
    comparisons = []
    for old, new in zip(expected, actual):
        require(old['status'] == new['status'] == 'COMPILED', 'probe failed to compile')
        checks = {}
        for suffix in ('.o', '.exe'):
            first = Path(old['directory']) / (old['prefix'] + suffix)
            second = Path(new['directory']) / (new['prefix'] + suffix)
            checks[suffix] = sha256(first.read_bytes()) == sha256(second.read_bytes())
        checks['code'] = old['contribution']['code_hex'] == new['contribution']['code_hex']
        checks['relocations'] = old['contribution']['all_relocations'] == new['contribution']['all_relocations']
        require(all(checks.values()), 'combined output differs from legacy output')
        comparisons.append(dict(legacy_key=old['cache_key'], combined_key=new['cache_key'], checks=checks,
                                legacy_job=old['worker_job'], combined_job=new['worker_job']))
    stats = json.loads((ROOT / 'build/compiler-last-run.json').read_text())
    replay = compile_queue.compile_many(candidates)
    require(all(r['cache_hit'] for r in replay), 'combined replay was not cached')
    report = dict(schema_version=1, policy='Infrastructure probe only; no game reconstruction proof or promotion.',
                  runner_sha256=sha256((ROOT / 'tools/queued_oracle.py').read_bytes()),
                  legacy_oracle_sha256=sha256((ROOT / 'tools/compiler_oracle.py').read_bytes()),
                  legacy_mixed_sha256=sha256((ROOT / 'tools/mixed_profile_oracle.py').read_bytes()),
                  combined_stats=stats, comparisons=comparisons, replay_cached=True)
    write_json(Path(__file__).with_name('report.json'), report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
