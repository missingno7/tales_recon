import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from analysis_support import ROOT
from common import sha256
from cycle_layout_gap_audit import build


class CycleLayoutGapAuditTests(unittest.TestCase):
    def test_frontier_counts_proven_literal_tail_without_promoting_coverage(self):
        report = build()
        self.assertEqual(report['status'], 'LAYOUT_FRONTIER_ONLY')
        self.assertFalse(report['promotion_eligible'])
        self.assertEqual(report['schema_version'], 2)
        self.assertEqual(report['interval']['size'], 4562)
        self.assertEqual(report['summary'], dict(candidate_count=15, canonical_candidate_count=9,
                         canonical_candidate_bytes=1812, unrecovered_candidate_count=6,
                         unrecovered_candidate_bytes=2710, unclaimed_bytes=0))
        self.assertEqual(report['unclaimed_spans'], [])
        self.assertEqual([x['id'] for x in report['candidate_spans'] if x['recovery_state']=='DISCOVERED'],
                         ['ov11_F_487E','ov11_F_4EC6','ov11_F_51C0',
                          'ov11_F_54F8','ov11_F_55B8','ov11_F_583A'])
        capsule=report['source_layout_capsule']
        self.assertEqual(capsule['canonical_runs'][0]['members'],['ov11_F_4790','ov11_F_4848'])
        self.assertEqual(capsule['canonical_runs'][0]['size'],238)
        data_tail=next(x for x in report['candidate_spans'] if x['id']=='ov11_F_506A')
        self.assertEqual(data_tail['contribution_end'],0x519c)
        owned_code_data=data_tail['owned_code_data']
        self.assertEqual({k:owned_code_data[k] for k in ('start','end','size','sha256',
                         'alignment_padding','strings','proof')},dict(
            start=0x5174, end=0x519c, size=40,
            sha256='b412d75b98c6aba75a06599ce39999541b5b1a2ae7884b03ecc8069207706538',
            alignment_padding=1,
            strings=[dict(offset=0x5174,text='P %d'), dict(offset=0x5179,text=' %d '),
                     dict(offset=0x517e,text='%*d %d %d %d %d %d %d %d %d\n')],
            proof='recovery/proofs/ov11_F_506A.json'))
        self.assertEqual(owned_code_data['proof_sha256'],
                         sha256((ROOT/owned_code_data['proof']).read_bytes()))
        joined=next(x for x in capsule['canonical_runs'] if 'ov11_F_506A' in x['members'])
        self.assertEqual(joined['members'],['ov11_F_506A','ov11_F_519C'])
        self.assertEqual((joined['start'],joined['end'],joined['size']),
                         (0x506a,0x51c0,0x156))
        first_pending=next(x for x in report['candidate_spans'] if x['id']=='ov11_F_487E')
        self.assertEqual(first_pending['layout_dependencies']['internal'],['ov11_F_55B8'])
        self.assertEqual(first_pending['layout_dependencies']['pending'],['ov11_F_55B8'])


if __name__ == '__main__':
    unittest.main()
