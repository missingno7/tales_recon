import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from cycle_layout_gap_audit import build


class CycleLayoutGapAuditTests(unittest.TestCase):
    def test_frontier_retains_only_existing_candidates_and_unclaimed_gap(self):
        report = build()
        self.assertEqual(report['status'], 'LAYOUT_FRONTIER_ONLY')
        self.assertFalse(report['promotion_eligible'])
        self.assertEqual(report['interval']['size'], 4562)
        self.assertEqual(report['summary'], dict(candidate_count=15, canonical_candidate_count=8,
                         canonical_candidate_bytes=858, unrecovered_candidate_count=7,
                         unrecovered_candidate_bytes=3664, unclaimed_bytes=40))
        self.assertEqual(report['unclaimed_spans'], [dict(start=0x5174, end=0x519c, size=40,
                                                          state='UNCLAIMED', promotion_eligible=False)])
        self.assertEqual([x['id'] for x in report['candidate_spans'] if x['recovery_state']=='DISCOVERED'],
                         ['ov11_F_487E','ov11_F_4B0C','ov11_F_4EC6','ov11_F_51C0',
                          'ov11_F_54F8','ov11_F_55B8','ov11_F_583A'])


if __name__ == '__main__':
    unittest.main()
