import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from cycle_gap_codegen_experiment import build


class CycleGapCodegenExperimentTests(unittest.TestCase):
    def test_latent_candidates_are_exact_length_but_never_promoted(self):
        report=build()
        self.assertEqual(report['status'],'CODEGEN_SIMILAR_LAYOUT_ONLY')
        self.assertEqual([x['actual_length'] for x in report['cases']],[44,42])
        self.assertTrue(all(x['mnemonic_similarity']==1.0 and not x['promotion_eligible'] for x in report['cases']))


if __name__=='__main__':unittest.main()
