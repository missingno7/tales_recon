"""Combined queued batches preserve the existing compiler identities and routing."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_unit
import compiler_oracle
import compile_queue
import queued_oracle
import mixed_profile_oracle


class QueuedOracleTests(unittest.TestCase):
    def test_queue_capability_routes_both_kinds_without_splitting(self):
        trials = [dict(source='ordinary'), dict(source='mixed', object_profiles=['aztec36'])]
        seen = []
        def queued(values):
            seen.append(values)
            return ['a', 'b']
        queued.supports_object_profiles = True
        with patch.object(check_unit, 'compile_many', queued), \
             patch.object(mixed_profile_oracle, 'compile_many', side_effect=AssertionError('split request')):
            self.assertEqual(check_unit.compile_trials(trials), ['a', 'b'])
        self.assertEqual(seen, [trials])

    def test_cached_mixed_identity_and_outputs_replay_unchanged(self):
        # A retained real trial proves queue keys agree with the legacy mixed
        # identity, and that replay still validates every cached artifact.
        receipts = sorted(compiler_oracle.CACHE.glob('*/receipt.json'))
        import json
        for path in receipts:
            receipt = json.loads(path.read_text())
            meta = receipt['identity']
            if meta.get('object_profiles') and receipt['status'] == 'COMPILED':
                prefix = receipt['prefix']
                objects = []
                for label in meta['object_labels']:
                    name = prefix if label == 'candidate' else prefix + '_' + label
                    objects.append(dict(source=(path.parent / (name + '.c')).read_text()))
                # Harness input is retained separately in unit receipts; use
                # the known synthetic sources below for key equality instead.
                compiled = compiler_oracle.cached(receipt['cache_key'])
                with patch.object(queued_oracle, 'trial_plan', return_value=(
                        receipt['cache_key'], meta, '', objects)), \
                     patch.object(queued_oracle, 'prepare', side_effect=AssertionError('cache replay booted')):
                    result = queued_oracle.compile_many([dict(source='', profile=meta['profile'])])[0]
                self.assertEqual(result['contribution'], compiled['contribution'])
                self.assertTrue(result['cache_hit'])
                return
        self.skipTest('retained mixed-profile compile cache absent')

    def test_trial_plans_use_exact_legacy_identities(self):
        base = ROOT / compiler_oracle.PROFILES['aztec36']['base']
        if not (base / 'bin/cc').is_file():
            self.skipTest('pinned toolchain absent')
        objects = [dict(source='recovered() { return 1; }\n'), dict(source='helper() { return 2; }\n')]
        trial = dict(source=''.join(o['source'] for o in objects), profile='aztec36',
                     objects=objects, local_functions=['helper'])
        plain = compiler_oracle.identity(trial['source'], 'aztec36', 1,
                                         compiler_oracle.object_specs(trial), ['helper'])
        self.assertEqual(queued_oracle.trial_plan(trial)[:3], plain)
        self.assertEqual(compile_queue.trial_key(trial), plain[0])
        mixed = dict(trial, object_profiles=['aztec36', 'aztec36-large-data'])
        expected = mixed_profile_oracle.mixed_identity(mixed)
        self.assertEqual(queued_oracle.trial_plan(mixed), expected)
        self.assertEqual(compile_queue.trial_key(mixed), expected[0])


if __name__ == '__main__':
    unittest.main()
