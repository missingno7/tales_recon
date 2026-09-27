import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from recovery_plan import build_plan, plan


class RecoveryPlanTests(unittest.TestCase):
    def setUp(self):
        self.functions = [
            {'id': 'ov07_F_0100', 'node': 'ov07', 'hunk': 7, 'start': 0x100, 'end': 0x120,
             'direct_callees': [{'id': 'ov07_F_0120', 'basis': 'PC_RELATIVE'}]},
            {'id': 'ov07_F_0120', 'node': 'ov07', 'hunk': 7, 'start': 0x120, 'end': 0x140,
             'direct_callees': [{'id': 'ov07_F_0100', 'basis': 'PC_RELATIVE'}]},
            {'id': 'ov07_F_0140', 'node': 'ov07', 'hunk': 7, 'start': 0x140, 'end': 0x160,
             'direct_callees': []},
        ]
        self.ranked = [
            {'id': 'ov07_F_0100', 'node': 'ov07', 'size': 32, 'extent': 'CLOSED_CFG',
             'confidence': 'HIGH', 'indirect': 0, 'unknown_calls': 0, 'data_references': 0,
             'pc_relative_data': 0, 'pending_local_dependencies': ['ov07_F_0120'],
             'same_node_unit_ready': True, 'state': 'DISCOVERED'},
            {'id': 'ov07_F_0120', 'node': 'ov07', 'size': 32, 'extent': 'UNCERTAIN',
             'confidence': 'HIGH', 'indirect': 0, 'unknown_calls': 0, 'data_references': 2,
             'pc_relative_data': 1, 'pending_local_dependencies': ['ov07_F_0100'],
             'same_node_unit_ready': False, 'state': 'CODEGEN_SIMILAR'},
            {'id': 'ov07_F_0140', 'node': 'ov07', 'size': 40, 'extent': 'CLOSED_CFG',
             'confidence': 'HIGH', 'indirect': 0, 'unknown_calls': 0, 'data_references': 0,
             'pc_relative_data': 0, 'pending_local_dependencies': [],
             'same_node_unit_ready': True, 'state': 'DISCOVERED'},
        ]

    def test_plan_counts_overlapping_mechanisms_and_groups_cycle(self):
        state = {'attempts': {'ov07_F_0120': [{'profile': 'aztec36', 'verdict': 'DIFFER'}]},
                 'blockers': {}}
        ranked = [dict(x) for x in self.ranked]
        ranked[1]['extent'] = 'CLOSED_CFG'
        ranked[2]['extent'] = 'UNCERTAIN'
        result = build_plan(self.functions, ranked, state, node='ov07', limit=64)
        self.assertEqual(result['mode'], 'RECOVERY_REVIEW_REQUIRED')
        self.assertEqual(result['measurement']['eligible_count'], 0)
        self.assertEqual(result['measurement']['all_constraint_counts']['UNCERTAIN_EXTENT'], 1)
        self.assertEqual(result['measurement']['all_constraint_counts']['UNRECOVERED_LOCAL_DEPENDENCY'], 2)
        cycle = next(p for p in result['packages'] if p['kind'] == 'DEPENDENCY_SCC_HYPOTHESIS')
        self.assertEqual(cycle['members'], ['ov07_F_0100', 'ov07_F_0120'])
        self.assertTrue(cycle['dispatch']['read_only'])
        self.assertFalse(cycle['metadata']['source_unit_compile_ready'])
        self.assertEqual(cycle['diagnostics'][1]['source']['state'], 'ATTEMPT_RECEIPTS_AVAILABLE')

    def test_proof_blocker_is_mechanism_specific_and_retry_is_not_suggested(self):
        state = {'attempts': {}, 'blockers': {
            'ov07_F_0140': {'reason': 'BYTE_RETURN_ABI_MISMATCH: compiler extension differs', 'attempts': []}}}
        result = build_plan(self.functions, self.ranked, state, limit=64)
        package = next(p for p in result['packages'] if p['kind'] == 'PROOF_BLOCKER_REVIEW')
        self.assertEqual(package['dispatch']['action'], 'audit_profile_or_codegen')
        self.assertIn('change the hypothesis', package['rationale'])

    def test_limits_are_bounded(self):
        state = {'attempts': {}, 'blockers': {}}
        result = build_plan(self.functions, self.ranked, state, limit=64, max_packages=1)
        self.assertLessEqual(len(result['packages']), 1)
        with self.assertRaises(ValueError):
            build_plan(self.functions, self.ranked, state, limit=0)

    def test_large_scc_is_review_not_a_truncated_unit(self):
        count = 9
        functions, ranked = [], []
        for i in range(count):
            fid = f'ov07_F_{0x200 + i * 0x20:04X}'
            nxt = f'ov07_F_{0x200 + ((i + 1) % count) * 0x20:04X}'
            functions.append({'id': fid, 'node': 'ov07', 'hunk': 7, 'start': 0x200 + i * 0x20,
                              'end': 0x220 + i * 0x20,
                              'direct_callees': [{'id': nxt, 'basis': 'PC_RELATIVE'}]})
            ranked.append({'id': fid, 'node': 'ov07', 'size': 32, 'extent': 'CLOSED_CFG',
                           'confidence': 'HIGH', 'indirect': 0, 'unknown_calls': 0,
                           'data_references': 0, 'pc_relative_data': 0,
                           'pending_local_dependencies': [nxt], 'same_node_unit_ready': True,
                           'state': 'DISCOVERED'})
        result = build_plan(functions, ranked, {'attempts': {}, 'blockers': {}}, limit=64)
        package = next(p for p in result['packages'] if p['kind'] == 'DEPENDENCY_SCC_REVIEW')
        self.assertEqual(package['member_count'], 9)
        self.assertFalse(package['members_complete'])
        self.assertNotEqual(package['dispatch']['action'], 'inspect_compact_unit')

    def test_self_recursion_does_not_create_a_multi_function_unit(self):
        recursive = [dict(self.functions[0], direct_callees=[{'id': 'ov07_F_0100', 'basis': 'PC_RELATIVE'}])]
        result = build_plan(recursive, [self.ranked[0]], {'attempts': {}, 'blockers': {}}, limit=64)
        self.assertFalse(any(p['kind'].startswith('DEPENDENCY_SCC') for p in result['packages']))

    def test_blocked_candidate_is_never_counted_as_eligible(self):
        state = {'attempts': {}, 'blockers': {'ov07_F_0140': {'reason': 'SOURCE_HYPOTHESIS'}}}
        result = build_plan(self.functions, [self.ranked[2]], state, limit=64)
        self.assertEqual(result['measurement']['eligible_count'], 0)
        self.assertEqual(result['measurement']['all_constraint_counts']['RECOVERY_BLOCKER'], 1)

    def test_eligible_candidate_remains_actionable(self):
        result = build_plan(self.functions, [self.ranked[2]], {'attempts': {}, 'blockers': {}}, limit=64)
        self.assertEqual(result['mode'], 'ACTIONABLE')
        self.assertEqual(result['measurement']['eligible_ids'], ['ov07_F_0140'])

    def test_live_frontier_report_is_read_only_and_capped(self):
        result = plan(limit=512, max_packages=3)
        self.assertTrue(result['read_only'])
        self.assertLessEqual(len(result['packages']), 3)
        self.assertIn(result['mode'], ('RECOVERY_REVIEW_REQUIRED', 'ACTIONABLE', 'NO_CANDIDATES'))


if __name__ == '__main__':
    unittest.main()
