import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from cycle_gap_audit import build


class CycleGapAuditTests(unittest.TestCase):
    def test_cycle_gaps_remain_latent_and_exactly_decoded(self):
        report=build()
        self.assertEqual([x['id'] for x in report['windows']],['ov11_LATENT_59E6','ov11_LATENT_5CEA'])
        for window in report['windows']:
            self.assertFalse(window['promotion_eligible'])
            self.assertEqual(window['instructions'][0]['mnemonic'],'link.w')
            self.assertEqual(window['instructions'][-1]['mnemonic'],'rts')
            self.assertEqual(sum(x['size'] for x in window['instructions']),window['end']-window['start'])


if __name__=='__main__':unittest.main()
