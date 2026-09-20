import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from cycle_object_order_experiment import build


class CycleObjectOrderExperimentTests(unittest.TestCase):
    def test_earlier_callee_retains_non_promoting_layout_receipt(self):
        report = build()
        self.assertEqual(report['status'], 'CODEGEN_SIMILAR_LAYOUT_ONLY')
        self.assertFalse(report['promotion_eligible'])
        target = report['target']
        self.assertEqual((target['expected_length'], target['actual_length']), (168, 168))
        self.assertNotIn('FORWARD_CALL_RELAXATION',
                         {x['kind'] for x in target['instruction_differences']})


if __name__ == '__main__':
    unittest.main()
