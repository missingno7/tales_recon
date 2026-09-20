import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from cycle_prefix_experiment import build


class CyclePrefixExperimentTests(unittest.TestCase):
    def test_prefix_is_layout_evidence_only(self):
        report=build()
        self.assertEqual(report['status'],'CODEGEN_SIMILAR_LAYOUT_ONLY')
        self.assertFalse(report['promotion_eligible'])
        self.assertEqual(report['comparison']['expected_length'],176)
        self.assertEqual(report['comparison']['actual_length'],176)
        self.assertEqual(report['comparison']['mnemonic_similarity'],1.0)


if __name__=='__main__':unittest.main()
