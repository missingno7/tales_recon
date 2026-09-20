import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from cycle_cluster_experiment import build


class CycleClusterExperimentTests(unittest.TestCase):
    def test_cluster_retains_non_promoting_mechanism_map(self):
        report=build()
        self.assertEqual(report['status'],'CODEGEN_SIMILAR_LAYOUT_ONLY')
        self.assertFalse(report['promotion_eligible'])
        self.assertEqual((report['comparison']['expected_length'],report['comparison']['actual_length']),(1080,1080))
        self.assertTrue(all(x['mnemonic_similarity']==1.0 and not x['promotion_eligible'] for x in report['members']))
        kinds={d['kind'] for member in report['members'] for d in member['instruction_differences']}
        self.assertTrue({'A4_GLOBAL_LAYOUT','FORWARD_EXTERNAL_CALL_BINDING','PC_RELATIVE_LAYOUT_DISPLACEMENT'} <= kinds)


if __name__=='__main__':unittest.main()
