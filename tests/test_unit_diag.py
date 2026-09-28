import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import unit_diag
from compiler_oracle import cached


def member(fid, start, code, tail=''):
    code = bytes.fromhex(code)
    return dict(id=fid, hunk=5, start=start, end=start + len(code), bytes=code, tail=bytes.fromhex(tail))


def candidate(code, symbols, relocations=()):
    return dict(status='COMPILED', identity=dict(profile='aztec36'),
                contribution=dict(hunk=3, code_hex=code, code_size=len(code) // 2, symbols=[
                    dict(hunk=3, name=n, offset=o) for n, o in symbols] + [dict(hunk=3, name='__H3_org', offset=0)],
                    relocations=list(relocations), all_relocations=[], hunks=[]))


A = member('ovXX_F_0100', 0x100, '70004e75')   # moveq #0,d0; rts
B = member('ovXX_F_0108', 0x108, '4e75')       # rts; [0x104,0x108) is unclaimed
DISCOVERED = [('ovXX_F_0100', 5, 0x100, 0x104), ('ovXX_F_0108', 5, 0x108, 0x10A)]


class UnitShapeTests(unittest.TestCase):
    """Synthetic fixtures: no repository proofs, cache entries or compiler jobs."""

    def test_gap_stays_unknown_and_candidate_only_bytes_are_not_assigned(self):
        # Candidate order B, A(moveq #1), a proxy inside the original gap, an unbound helper.
        c = candidate('4e75' + '70014e75' + '4e75' + '4e714e75',
                      [('_F_h05_0108', 0), ('_F_h05_0100', 2), ('_F_h05_0106', 6), ('_helper', 8)])
        r = unit_diag.analyze_unit([A, B], c, discovered=DISCOVERED)
        self.assertIn('NO_EQUALITY', r['claim'])
        self.assertNotIn('verdict', r)
        self.assertEqual(r['original']['unknown_gaps'], [dict(
            state='unknown', ownership='UNKNOWN_NOT_ASSIGNED', hunk=5, start=0x104, end=0x108, offset=4, length=4,
            discovered_function_starts_inside=[])])
        self.assertEqual(r['original']['claimed_bytes'], 6)
        self.assertFalse(r['order']['matches'])
        self.assertEqual(r['order']['inversions'], [['ovXX_F_0100', 'ovXX_F_0108']])
        states = {m['id']: m for m in r['members']}
        self.assertEqual(states['ovXX_F_0108']['state'], 'same_bytes')
        self.assertEqual(states['ovXX_F_0100']['state'], 'differs')
        self.assertIn('immediate_constant', states['ovXX_F_0100']['comparison']['categories'])
        only = {tuple(x['names']): x for x in r['candidate']['candidate_only']}
        self.assertEqual(only[('_F_h05_0106',)]['proxy_location_in_unknown_gap'], [0x104, 0x108])
        self.assertEqual(only[('_F_h05_0106',)]['ownership'], 'CANDIDATE_ONLY_NOT_ASSIGNED')
        self.assertEqual(only[('_helper',)]['note'], 'NO_ESTABLISHED_BINDING')
        self.assertEqual(only[('_helper',)]['bytes'], 4)
        # The gap is still unknown even though a candidate proxy name points into it.
        self.assertEqual(r['unit_shape']['unknown_gap_count'], 1)
        self.assertEqual(r['unit_shape']['total_length_delta'], 12 - 6)

    def test_candidate_is_bounded_by_its_own_symbols_not_original_lengths(self):
        # A gains a nop; the B symbol still bounds A's contribution at 6 bytes.
        c = candidate('4e7170004e75' + '4e75', [('_F_h05_0100', 0), ('_F_h05_0108', 6)])
        r = unit_diag.analyze_unit([A, B], c, discovered=DISCOVERED, interval=(0x100, 0x10A))
        a = next(m for m in r['members'] if m['id'] == 'ovXX_F_0100')
        self.assertEqual((a['candidate']['bytes'], a['length_delta']), (6, 2))
        self.assertEqual(a['comparison']['actual_only'], 1)
        self.assertIn('instruction_layout', a['comparison']['categories'])
        self.assertTrue(r['order']['matches'])

    def test_missing_member_and_entry_convention(self):
        c = candidate('70004e75', [('_recovered', 0)])
        r = unit_diag.analyze_unit([A, B], c, discovered=DISCOVERED)
        self.assertEqual({m['id']: m['state'] for m in r['members']},
                         {'ovXX_F_0100': 'missing_in_candidate', 'ovXX_F_0108': 'missing_in_candidate'})
        self.assertEqual(r['candidate']['candidate_only'][0]['note'], 'NO_ESTABLISHED_BINDING')
        r = unit_diag.analyze_unit([A, B], c, discovered=DISCOVERED, entry_member='ovXX_F_0100')
        a = next(m for m in r['members'] if m['id'] == 'ovXX_F_0100')
        self.assertEqual((a['state'], a['pairing']['basis']), ('same_bytes', 'unit_entry_convention'))
        self.assertEqual(r['member_states'], {'same_bytes': 1, 'missing_in_candidate': 1})

    def test_overlapping_claims_are_reported(self):
        overlap = member('ovXX_F_0102', 0x102, '4e75')
        r = unit_diag.analyze_unit([A, overlap], candidate('4e75', []), discovered=DISCOVERED)
        self.assertEqual(r['original']['claim_conflicts'][0]['id'], 'ovXX_F_0102')
        self.assertEqual(r['candidate']['candidate_only'][0]['note'], 'UNSYMBOLED_CANDIDATE_BYTES')

    def literal_fixture(self, candidate_hex, tail_hex='68690000'):
        # lea 4(pc),a0 targets the proven literal tail directly after rts.
        m = member('ovXX_F_0200', 0x200, '41fa00044e75', tail_hex)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / 't000.exe').write_bytes(b'')
        (root / 't000.c').write_text('')
        ledger = dict(a4=dict(bias=32766, evidence=dict(relocation=dict(target_hunk=1, addend_raw=32766))))

        def factory(mm, piece):
            f = dict(id=mm['id'], start=mm['start'], end=mm['end'], direct_callees=[], relocations=[], referenced_data=[])
            return unit_diag.UnitReferenceResolver(f, ledger, dict(piece, directory=str(root), prefix='t000'),
                                                   tail_bytes=len(mm['tail']), root=root)
        c = candidate(candidate_hex, [('_F_h05_0200', 0)])
        return unit_diag.analyze_unit([m], c, resolver_factory=factory)

    def test_pc_relative_literal_binds_through_proven_tail_and_candidate_bundle(self):
        # Candidate inserts a nop; its own lea target bounds its literal bundle.
        r = self.literal_fixture('4e7141fa00044e75' + '68690000')
        m = r['members'][0]
        self.assertEqual(m['candidate_literal_boundary'], 'CANDIDATE_PC_RELATIVE_LITERAL_TARGET')
        self.assertEqual(m['literal'], dict(original_bytes=4, candidate_bytes=4, bytes_equal=True))
        self.assertEqual(m['comparison']['reference_identity']['unresolved'], 0)
        self.assertEqual(m['comparison']['reference_identity']['same_identity'], 1)
        self.assertEqual(r['original']['unknown_gaps'], [])
        # A different string is a literal difference, not a code hypothesis.
        r = self.literal_fixture('41fa00044e75' + '6f6b0000')
        self.assertEqual(r['members'][0]['literal']['bytes_equal'], False)
        self.assertEqual(r['members'][0]['state'], 'differs')

    def test_compact_summary_is_bounded(self):
        many = [member('ovXX_F_%04X' % (0x100 + 4 * i), 0x100 + 4 * i, '70004e75') for i in range(60)]
        c = candidate('70014e75' * 60, [('_F_h05_%04X' % (0x100 + 4 * i), 4 * i) for i in range(60)])
        s = unit_diag.compact_summary(dict(unit_diag.analyze_unit(many, c), status='DIAGNOSTIC_ONLY'))
        self.assertLessEqual(len(json.dumps(s, separators=(',', ':'), sort_keys=True).encode()), 5000)
        self.assertTrue(s.get('truncated'))


class CachedUnitTests(unittest.TestCase):
    CONTROL = 'af14c54801ae01b91b77bdd8a571641445390950e915f1febc540d5e712ab7d5'
    CYCLE = '0b66dd65e9063d0c60d599e670250cee907ac9134fdd7e157359d4e7206fcaeb'

    def test_exact_verified_two_member_unit_is_all_same_with_no_gaps(self):
        if cached(self.CONTROL) is None:
            self.skipTest('cached ov10 unit artifact unavailable')
        r = unit_diag.diagnose_unit(['ov10_F_1FDE', 'ov10_F_2160'], self.CONTROL, entry_member='ov10_F_2160')
        self.assertEqual(r['status'], 'DIAGNOSTIC_ONLY')
        self.assertTrue(r['unit_shape']['all_members_same'], r['member_states'])
        self.assertEqual(r['original']['unknown_gaps'], [])
        self.assertEqual(r['candidate']['candidate_only'], [])
        self.assertIn('EQUAL', r['exact_verdict'])
        for m in r['members']:
            self.assertEqual(m['comparison']['reference_identity']['unresolved'], 0)

    def test_ov11_cycle_package_gap_remains_unknown(self):
        if cached(self.CYCLE) is None:
            self.skipTest('cached ov11 cycle experiment artifact unavailable')
        h = unit_diag.package_hypothesis('RP01')
        r = unit_diag.diagnose_unit(h['members'], self.CYCLE, interval=h['interval'])
        gaps = r['original']['unknown_gaps']
        self.assertEqual([(g['start'], g['end'], g['length'], g['state']) for g in gaps], [(23014, 23058, 44, 'unknown')])
        self.assertEqual([[g['start'], g['end']] for g in gaps], h['package_unclassified_gaps'])
        proxy = next(c for c in r['candidate']['candidate_only'] if c['names'] == ['_F_h11_59E6'])
        self.assertEqual(proxy['ownership'], 'CANDIDATE_ONLY_NOT_ASSIGNED')
        self.assertEqual(r['exact_verdict'], 'NOT_RUN_FOR_THIS_CACHE_KEY')
        self.assertTrue(r['unit_shape']['all_members_paired'])
        self.assertLessEqual(len(json.dumps(unit_diag.compact_summary(r)).encode()), 5000)


if __name__ == '__main__':
    unittest.main()
