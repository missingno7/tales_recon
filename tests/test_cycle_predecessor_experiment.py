import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from cycle_predecessor_experiment import build


class CyclePredecessorExperimentTests(unittest.TestCase):
    def test_predecessor_and_local_callee_are_layout_evidence_only(self):
        report = build()
        self.assertEqual(report['status'], 'CODEGEN_SIMILAR_LAYOUT_ONLY')
        self.assertFalse(report['promotion_eligible'])
        self.assertEqual((report['comparison']['expected_length'], report['comparison']['actual_length']), (428, 428))
        predecessor = report['members'][0]
        self.assertEqual(predecessor['id'], 'ov11_F_583A')
        self.assertEqual(predecessor['mnemonic_similarity'], 1.0)
        self.assertEqual({d['kind'] for d in predecessor['instruction_differences']}, {'A4_GLOBAL_LAYOUT'})
        self.assertTrue(all(not x['promotion_eligible'] for x in report['members']))


if __name__ == '__main__':
    unittest.main()
