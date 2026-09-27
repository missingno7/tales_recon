import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import diag
from compiler_oracle import cached


class DiagnosticComparisonTests(unittest.TestCase):
    def test_identical_and_shifted_streams_remain_diagnostic_only(self):
        code = bytes.fromhex('70004e75')  # moveq #0,d0; rts
        exact = diag.compare_code(code, code)
        self.assertEqual(exact['status'], 'DIAGNOSTIC_ONLY')
        self.assertIn('NO_EQUALITY', exact['claim'])
        self.assertEqual(exact['alignment']['expected_only'], [])
        shifted = diag.compare_code(bytes.fromhex('4e75'), bytes.fromhex('70004e75'))
        self.assertEqual(shifted['status'], 'DIAGNOSTIC_ONLY')
        self.assertEqual(len(shifted['alignment']['actual_only']), 1)

    def test_pc_relative_call_is_not_a_cfg_edge(self):
        # BSR to just beyond the payload is a call/reference, followed by RTS.
        report = diag.compare_code(bytes.fromhex('61024e75'), bytes.fromhex('61024e75'))
        self.assertEqual(report['status'], 'DIAGNOSTIC_ONLY')
        self.assertEqual(report['blocks']['unresolved_edges']['expected'], None)
        self.assertEqual(len(report['blocks']['paired']), 1)
        self.assertEqual(report['blocks']['paired'][0]['terminators'], ['return', 'return'])

    def test_dbcc_branch_and_conditional_polarity_are_kept_in_cfg(self):
        loop = diag.compare_code(bytes.fromhex('700051c8fffc4e75'), bytes.fromhex('700051c8fffc4e75'))
        self.assertEqual(loop['status'], 'DIAGNOSTIC_ONLY')
        self.assertGreaterEqual(len(loop['blocks']['paired']), 2)
        polarity = diag.compare_code(bytes.fromhex('66024e714e75'), bytes.fromhex('67024e714e75'))
        self.assertTrue(any(h['category'] == 'branch_condition_or_kind' for h in polarity['hypotheses']))
        self.assertIn('different_or_unresolved', [b['target_check'] for b in polarity['blocks']['paired']])

    def test_unmapped_data_span_fails_closed(self):
        result = diag.compare_code(bytes.fromhex('4e75'), bytes.fromhex('4e75'), data_spans=((0, 2),))
        self.assertEqual(result['status'], 'UNSUPPORTED')
        self.assertEqual(result['reason'], 'DATA_SPAN_MAPPING_REQUIRED_FOR_BOTH_STREAMS')

    def test_cached_ov09_near_match_reports_full_shifted_extents(self):
        key = '5d74128b28b30c647f3528921a6bca6ac9f28bab31c5128da77f1c4cb132c580'
        if cached(key) is None:
            self.skipTest('cached ov09 compiler artifact unavailable')
        report = diag.diagnose('ov09_F_298E', key)
        self.assertEqual(report['status'], 'DIAGNOSTIC_ONLY', report.get('reason'))
        self.assertEqual(report['original_extent']['bytes'], 660)
        self.assertEqual(report['candidate_extent']['bytes'], 672)
        self.assertTrue(report['alignment']['pairs'])
        self.assertTrue(report['alignment']['expected_only'] or report['alignment']['actual_only'])
        self.assertLess(report['alignment']['instruction_similarity'], 1.0)
        self.assertIn('register_assignment', {h['category'] for h in report['hypotheses']})
        self.assertLessEqual(len(str(diag.compact_summary(report)).encode()), 6000)

    def test_cached_exact_control_has_no_unpaired_code(self):
        key = 'f25f68d19e2811fa7533a18a206ec128d932d9de16c8f6cf7e6c96009b0e9456'
        if cached(key) is None:
            self.skipTest('cached exact compiler artifact unavailable')
        report = diag.diagnose('ov14_F_03AE', key)
        self.assertEqual(report['status'], 'DIAGNOSTIC_ONLY')
        self.assertEqual(report['alignment']['expected_only'], [])
        self.assertEqual(report['alignment']['actual_only'], [])
        summary = diag.compact_summary(report)
        self.assertIn('NO_EQUALITY', summary['claim'])


if __name__ == '__main__':
    unittest.main()
