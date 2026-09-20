import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from cycle_cluster_extended_experiment import build


class CycleClusterExtendedExperimentTests(unittest.TestCase):
    def test_extended_cluster_keeps_layout_evidence_non_promoting(self):
        report = build()
        self.assertEqual(report['status'], 'CODEGEN_SIMILAR_LAYOUT_ONLY')
        self.assertFalse(report['promotion_eligible'])
        self.assertEqual((report['comparison']['expected_length'], report['comparison']['actual_length']),
                         (1394, 1392))
        compact = next(x for x in report['members'] if x['id'] == 'ov11_F_5C42')
        self.assertEqual((compact['expected_size'], compact['actual_size'], compact['size_delta']),
                         (168, 166, -2))
        kinds = {d['kind'] for member in report['members'] for d in member['instruction_differences']}
        self.assertIn('COMPACT_FORWARD_CALL_ENCODING', kinds)
        self.assertIn('PC_RELATIVE_LAYOUT_DISPLACEMENT', kinds)
        self.assertNotIn('FORWARD_EXTERNAL_CALL_BINDING', kinds)
        self.assertTrue(all(not x['promotion_eligible'] for x in report['members']))


if __name__ == '__main__':
    unittest.main()
