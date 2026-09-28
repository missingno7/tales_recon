import json
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import diag
from compiler_oracle import cached


class DiagnosticComparisonTests(unittest.TestCase):
    def test_identical_and_shifted_streams_remain_diagnostic_only(self):
        code = bytes.fromhex('70004e75')  # moveq #0,d0; rts
        exact = diag.compare_code(code, code)
        self.assertEqual(exact['status'], 'DIAGNOSTIC_ONLY')
        self.assertIn('NO_EQUALITY', exact['claim'])
        self.assertEqual(exact['alignment']['expected_only'], [])
        shifted = diag.compare_code(bytes.fromhex('4e75'), bytes.fromhex('70004e75'))
        self.assertEqual(shifted['status'], 'DIAGNOSTIC_ONLY')
        self.assertEqual(len(shifted['alignment']['actual_only']), 1)

    def test_pc_relative_call_is_not_a_cfg_edge(self):
        # BSR to just beyond the payload is a call/reference, followed by RTS.
        report = diag.compare_code(bytes.fromhex('61024e75'), bytes.fromhex('61024e75'))
        self.assertEqual(report['status'], 'DIAGNOSTIC_ONLY')
        self.assertEqual(report['blocks']['unresolved_edges']['expected'], None)
        self.assertEqual(len(report['blocks']['paired']), 1)
        self.assertEqual(report['blocks']['paired'][0]['terminators'], ['return', 'return'])

    def test_dbcc_branch_and_conditional_polarity_are_kept_in_cfg(self):
        loop = diag.compare_code(bytes.fromhex('700051c8fffc4e75'), bytes.fromhex('700051c8fffc4e75'))
        self.assertEqual(loop['status'], 'DIAGNOSTIC_ONLY')
        self.assertGreaterEqual(len(loop['blocks']['paired']), 2)
        polarity = diag.compare_code(bytes.fromhex('66024e714e75'), bytes.fromhex('67024e714e75'))
        self.assertTrue(any(h['category'] == 'branch_condition_or_kind' for h in polarity['hypotheses']))
        self.assertIn('different_or_unresolved', [b['target_check'] for b in polarity['blocks']['paired']])

    def test_unmapped_data_span_fails_closed(self):
        result = diag.compare_code(bytes.fromhex('4e75'), bytes.fromhex('4e75'), data_spans=((0, 2),))
        self.assertEqual(result['status'], 'UNSUPPORTED')
        self.assertEqual(result['reason'], 'DATA_SPAN_MAPPING_REQUIRED_FOR_BOTH_STREAMS')

    def test_cached_ov09_near_match_reports_full_shifted_extents(self):
        key = '5d74128b28b30c647f3528921a6bca6ac9f28bab31c5128da77f1c4cb132c580'
        if cached(key) is None:
            self.skipTest('cached ov09 compiler artifact unavailable')
        report = diag.diagnose('ov09_F_298E', key)
        self.assertEqual(report['status'], 'DIAGNOSTIC_ONLY', report.get('reason'))
        self.assertEqual(report['original_extent']['bytes'], 660)
        self.assertEqual(report['candidate_extent']['bytes'], 672)
        self.assertTrue(report['alignment']['pairs'])
        self.assertTrue(report['alignment']['expected_only'] or report['alignment']['actual_only'])
        self.assertLess(report['alignment']['instruction_similarity'], 1.0)
        self.assertIn('register_assignment', {h['category'] for h in report['hypotheses']})
        self.assertLessEqual(len(str(diag.compact_summary(report)).encode()), 6000)

    def test_cached_exact_control_has_no_unpaired_code(self):
        key = 'f25f68d19e2811fa7533a18a206ec128d932d9de16c8f6cf7e6c96009b0e9456'
        if cached(key) is None:
            self.skipTest('cached exact compiler artifact unavailable')
        report = diag.diagnose('ov14_F_03AE', key)
        self.assertEqual(report['status'], 'DIAGNOSTIC_ONLY')
        self.assertEqual(report['alignment']['expected_only'], [])
        self.assertEqual(report['alignment']['actual_only'], [])
        summary = diag.compact_summary(report)
        self.assertIn('NO_EQUALITY', summary['claim'])


class RegisterTraceTests(unittest.TestCase):
    def test_first_divergence_mapping_and_conflict_are_located(self):
        # expected: move.l d0,d1; move.l d1,d2; rts
        # candidate: move.l d0,d2; move.l d1,d2; rts
        report = diag.compare_code(bytes.fromhex('220024014e75'), bytes.fromhex('240024014e75'))
        trace = report['register_trace']
        self.assertIn('NO_ALLOCATION_OR_LIVENESS_CLAIM', trace['claim'])
        self.assertEqual(trace['first_divergence']['expected']['offset'], 0)
        self.assertEqual(trace['first_divergence']['actual']['operands'], 'd0, d2')
        conflict = trace['first_conflict']
        self.assertEqual((conflict['kind'], conflict['original'], conflict['candidate'], conflict['previous']),
                         ('original_maps_to_multiple_candidates', 'd1', 'd1', ['d2']))
        self.assertEqual(conflict['expected']['offset'], 2)
        mapping = {(m['original'], m['candidate']): m['consistent'] for m in trace['mapping']}
        self.assertTrue(mapping[('d0', 'd0')])
        self.assertFalse(mapping[('d1', 'd2')])
        self.assertEqual(trace['def_use']['expected']['d1'], dict(writes=1, reads=1, first_offset=0))
        self.assertEqual(trace['def_use']['actual']['d2']['writes'], 2)
        compact = diag.compact_summary(report)['register_trace']
        self.assertEqual(compact['remapped'], ['d1->d2'])
        self.assertEqual(compact['first_conflict']['original'], 'd1')

    def test_identical_streams_have_no_register_divergence(self):
        report = diag.compare_code(bytes.fromhex('220024014e75'), bytes.fromhex('220024014e75'))
        trace = report['register_trace']
        self.assertIsNone(trace['first_divergence'])
        self.assertIsNone(trace['first_conflict'])
        self.assertTrue(all(m['consistent'] for m in trace['mapping']))

    def test_structurally_different_pairs_do_not_contribute_mappings(self):
        # tst.l d0 vs moveq #0,d1 are paired only as a substitution.
        report = diag.compare_code(bytes.fromhex('4a804e75'), bytes.fromhex('72004e75'))
        trace = report['register_trace']
        self.assertEqual(trace['structurally_incomparable_pairs'], 1)
        self.assertEqual(trace['mapping'], [])


class ReferenceIdentityTests(unittest.TestCase):
    """Synthetic fixtures: no repository proofs, cache entries or compiler jobs."""

    START = 0x100

    def fixture(self, symbols, *, referenced=True, callees=(), stub_relocs=(), proofs=None,
                source='extern char G_h01_1424;\n'):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        # Linked startup fragment: LEA DATA+32766,A4; RTS (the pinned A4 ABI).
        (root / 't000.exe').write_bytes(bytes.fromhex('49f9000000004e75'))
        (root / 't000.c').write_text(source)
        if proofs is not None:
            (root / 'recovery' / 'proofs').mkdir(parents=True)
            (root / 'recovery' / 'proofs' / 'x.json').write_text(json.dumps(dict(relocation_proof=proofs)))
        f = dict(id='ovXX_F_0100', start=self.START, direct_callees=list(callees), relocations=[],
                 referenced_data=[dict(hunk=1, offset=5156, instruction_offset=self.START, kind='A4_RELATIVE')]
                 if referenced else [])
        ledger = dict(a4=dict(bias=32766, evidence=dict(relocation=dict(target_hunk=1, addend_raw=32766))))
        relocs = [dict(source_hunk=0, source_offset=2, target_hunk=1, addend_raw=32766)] + list(stub_relocs)
        compiled = dict(directory=str(root), prefix='t000', identity=dict(profile='aztec36'),
                        contribution=dict(hunk=3, symbols=symbols, relocations=[], all_relocations=relocs,
                                          hunks=[dict(number=0, content_offset=0, type='CODE'),
                                                 dict(number=1, type='DATA', initialized_size=40, allocated_size=120)]))
        return diag.ReferenceResolver(f, ledger, compiled, root=root)

    def compare(self, expected, actual, resolver):
        result = diag.compare_code(bytes.fromhex(expected), bytes.fromhex(actual), resolver=resolver)
        self.assertEqual(result['status'], 'DIAGNOSTIC_ONLY')
        return result, {h['category']: h for h in result['hypotheses']}

    # move.b d0,-$6bda(a4) (original DATA 5156) versus -$7fd6(a4) (candidate DATA 40).
    ORIGINAL = '194094264e75'
    CANDIDATE = '1940802a4e75'

    def test_same_symbol_different_displacement_is_layout_only_not_a_hypothesis(self):
        result, cats = self.compare(self.ORIGINAL, self.CANDIDATE,
                                    self.fixture([dict(hunk=1, name='_G_h01_1424', offset=40)]))
        ref = result['reference_identity']
        self.assertEqual(ref['counts'], dict(same_identity=0, layout_only=1, different_identity=0, unresolved=0))
        self.assertEqual(cats, {})
        self.assertEqual(result['hypothesis_groups']['binding_or_layout']['total'], 0)
        self.assertIn('NO_EQUALITY', ref['claim'])

    def test_identical_encoding_with_same_identity_is_same_identity(self):
        # Candidate symbol placed so the displacement is identical.
        result, cats = self.compare(self.ORIGINAL, self.ORIGINAL,
                                    self.fixture([dict(hunk=1, name='_G_h01_1424', offset=5156)]))
        self.assertEqual(result['reference_identity']['counts']['same_identity'], 1)
        self.assertEqual(cats, {})

    def test_different_bound_symbol_is_a_binding_hypothesis(self):
        result, cats = self.compare(self.ORIGINAL, self.CANDIDATE,
                                    self.fixture([dict(hunk=1, name='_G_h01_1425', offset=40)],
                                                 source='extern char G_h01_1425;\n'))
        self.assertEqual(result['reference_identity']['counts']['different_identity'], 1)
        h = cats['a4_global_layout']
        self.assertEqual((h['group'], h['identity_states']), ('binding_or_layout', {'different_identity': 1}))
        self.assertEqual(result['hypothesis_groups']['source_shape']['total'], 0)

    def test_unbound_names_and_unledgered_originals_stay_unresolved(self):
        result, cats = self.compare(self.ORIGINAL, self.CANDIDATE,
                                    self.fixture([dict(hunk=1, name='_score', offset=40)], referenced=False,
                                                 source='extern char score;\n'))
        ref = result['reference_identity']
        self.assertEqual(ref['counts']['unresolved'], 1)
        self.assertEqual(set(ref['unresolved_reasons']),
                         {'expected:ORIGINAL_A4_REFERENCE_NOT_IN_LEDGER',
                          'actual:CANDIDATE_SYMBOL_HAS_NO_ESTABLISHED_ORIGINAL_BINDING'})
        self.assertEqual(cats['a4_global_layout']['identity_states'], {'unresolved': 1})

    def test_bytes_only_comparison_keeps_references_unresolved(self):
        result, cats = self.compare(self.ORIGINAL, self.CANDIDATE, None)
        self.assertEqual(result['reference_identity']['context'], 'NONE_BYTES_ONLY')
        self.assertEqual(result['reference_identity']['counts']['unresolved'], 1)
        self.assertEqual(cats['a4_global_layout']['count'], 1)

    def test_register_change_survives_resolved_reference(self):
        # Candidate stores d1 instead of d0 into the same established global.
        result, cats = self.compare(self.ORIGINAL, '1941802a4e75',
                                    self.fixture([dict(hunk=1, name='_G_h01_1424', offset=40)]))
        self.assertIn('register_assignment', cats)
        self.assertNotIn('a4_global_layout', cats)
        self.assertEqual(cats['register_assignment']['group'], 'source_shape')
        self.assertEqual(result['reference_identity']['counts']['layout_only'], 1)

    def test_a4_call_stub_resolves_through_candidate_relocation(self):
        # jsr -$7f56(a4) original (ledger callee 0:$463E) vs jsr -$7ffe(a4) candidate stub at DATA 0.
        callee = dict(site=self.START, hunk=0, offset=0x463E, id='resident_F_463E', basis='A4_RELOCATED_JMP_STUB')
        resolver = self.fixture([dict(hunk=0, name='_F_h00_463E', offset=34)], referenced=False, callees=[callee],
                                stub_relocs=[dict(source_hunk=1, source_offset=2, target_hunk=0, addend_raw=34)],
                                proofs=[dict(identity=dict(symbol='_F_h00_463E', hunk=0, offset=0x463E, addend=0))])
        result, cats = self.compare('4eac80aa4e75', '4eac80024e75', resolver)
        self.assertEqual(cats, {})
        self.assertEqual(result['reference_identity']['counts']['layout_only'], 1)
        wrong = self.fixture([dict(hunk=0, name='_F_h00_4640', offset=34)], referenced=False, callees=[callee],
                             stub_relocs=[dict(source_hunk=1, source_offset=2, target_hunk=0, addend_raw=34)])
        _, cats = self.compare('4eac80aa4e75', '4eac80024e75', wrong)
        self.assertEqual(cats['call_target_or_encoding']['identity_states'], {'different_identity': 1})

    def test_absolute_short_address_is_not_a_link_reference(self):
        # pea $ff.w cannot carry a HUNK_RELOC32, so it has no identity to resolve.
        result, cats = self.compare('487800ff4e75', '487800ff4e75', None)
        self.assertEqual(sum(result['reference_identity']['counts'].values()), 0)
        self.assertEqual(cats, {})

    def test_frame_displacement_is_source_shape_only(self):
        # MOVE.W 8(A5),D0 versus MOVE.W 10(A5),D0.
        result, cats = self.compare('302d00084e75', '302d000a4e75', None)
        self.assertIn('frame_or_stack_reference', cats)
        self.assertNotIn('memory_reference_or_layout', cats)
        self.assertEqual(result['hypothesis_groups']['source_shape']['categories'], {'frame_or_stack_reference': 1})

    def test_cached_exact_control_references_resolve(self):
        key = 'f25f68d19e2811fa7533a18a206ec128d932d9de16c8f6cf7e6c96009b0e9456'
        if cached(key) is None:
            self.skipTest('cached exact compiler artifact unavailable')
        report = diag.diagnose('ov14_F_03AE', key)
        self.assertEqual(report['reference_identity']['counts'],
                         dict(same_identity=0, layout_only=2, different_identity=0, unresolved=0))
        self.assertEqual(report['hypotheses'], [])
        summary = diag.compact_summary(report)
        self.assertEqual(summary['reference_identity']['counts']['unresolved'], 0)


class UnitMemberBoundTests(unittest.TestCase):
    """Synthetic prepared units: the target is ``_recovered`` beside bundled callees."""

    HELPER_A = '70004e75'        # moveq #0,d0; rts
    MEMBER = '72014e714e75'      # moveq #1,d1; nop; rts
    HELPER_B = '74024e75'        # moveq #2,d2; rts

    def unit(self, *, objects=True, member_labels=('_recovered',), extra_symbols=(), entry_offset=4):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        parts = [('candidate', self.HELPER_A, '_F_h11_0010'), ('part001', self.MEMBER, '_recovered'),
                 ('part002', self.HELPER_B, '_F_h11_0200')]
        for label, code, name in parts:
            stem = 't000' if label == 'candidate' else 't000_' + label
            if objects:
                (root / (stem + '.o')).write_bytes(b'AJ' + bytes(8) + (len(code) // 2).to_bytes(4, 'big') + bytes(8))
            labels = member_labels if name == '_recovered' else (name,)
            (root / (stem + '.asm')).write_text(''.join('\tpublic\t%s\n%s:\n' % (n, n) for n in labels) + '\trts\n')
        code = ''.join(p[1] for p in parts)
        symbols = [dict(hunk=3, name='__H3_org', offset=0), dict(hunk=3, name='_F_h11_0010', offset=0),
                   dict(hunk=3, name='_recovered', offset=4), dict(hunk=3, name='_F_h11_0200', offset=10),
                   dict(hunk=3, name='__H3_end', offset=14)] + list(extra_symbols)
        contribution = dict(hunk=3, code_hex=code, code_size=len(code) // 2, symbols=symbols, relocations=[],
                            all_relocations=[], hunks=[], data_size=0, bss_size=0)
        if entry_offset is not None:
            contribution['entry_offset'] = entry_offset
        return dict(status='COMPILED', directory=str(root), prefix='t000', cache_key='k' * 64,
                    identity=dict(profile='aztec36', object_labels=[p[0] for p in parts]), contribution=contribution)

    def test_entry_member_is_bounded_by_its_own_symbols_and_objects(self):
        bound, why = diag.unit_member_extent(self.unit())
        self.assertIsNone(why)
        self.assertEqual((bound['start'], bound['end'], bound['bytes'], bound['object']), (4, 10, 6, 'part001'))
        self.assertEqual(bound['end_basis'], 'object_end_and_next_linked_symbol')
        self.assertEqual(bound['piece']['contribution']['code_hex'], self.MEMBER)
        self.assertEqual(bound['piece']['contribution']['code_offset'], 4)

    def test_member_that_cannot_be_bounded_independently_is_refused(self):
        self.assertEqual(diag.unit_member_extent(self.unit(objects=False))[1], 'UNIT_OBJECT_SIZES_UNAVAILABLE')
        # A static helper label with no linked symbol could sit inside the segment.
        _, why = diag.unit_member_extent(self.unit(member_labels=('_recovered', '_helper')))
        self.assertEqual(why, 'UNIT_MEMBER_OBJECT_HAS_UNSYMBOLED_LABELS:_helper')
        _, why = diag.unit_member_extent(self.unit(entry_offset=0))
        self.assertEqual(why, 'UNIT_ENTRY_OFFSET_DISAGREES_WITH_ENTRY_SYMBOL')
        unit = self.unit()
        unit['contribution']['symbols'] = [s for s in unit['contribution']['symbols'] if s['name'] != '_recovered']
        self.assertEqual(diag.unit_member_extent(unit)[1], 'UNIT_ENTRY_SYMBOL_ABSENT_OR_AMBIGUOUS')
        _, why = diag.unit_member_extent(self.unit(extra_symbols=[dict(hunk=3, name='_F_h11_0104', offset=4)]))
        self.assertEqual(why, 'UNIT_ENTRY_SHARES_OFFSET_WITH_OTHER_SYMBOL')

    def diagnose(self, unit):
        f = dict(id='ov11_F_0100', hunk=13, start=0x100, end=0x106, size=6, extent_status='CLOSED_CFG',
                 raw_bytes=self.MEMBER, referenced_data=[], direct_callees=[], relocations=[])
        ledger = dict(game_sha256='0' * 64, a4=dict(bias=32766, evidence=dict(relocation=dict(target_hunk=1, addend_raw=32766))))
        with mock.patch.object(diag, 'validated_function', return_value=(f, ledger)), \
                mock.patch.object(diag, 'cached', return_value=unit):
            return diag.diagnose(f['id'], unit['cache_key'])

    def test_prepared_unit_member_is_diagnosed_not_the_whole_unit(self):
        report = self.diagnose(self.unit())
        self.assertEqual(report['status'], 'DIAGNOSTIC_ONLY', report.get('unit_member_reason'))
        self.assertEqual(report['bounded_by'], 'unit_member_symbol')
        self.assertEqual(report['unit_standalone_reason'], 'CANDIDATE_ENTRY_NOT_AT_OBJECT_START')
        ext = report['candidate_extent']
        self.assertEqual((ext['bytes'], ext['unit_offset'], ext['unit_code_bytes']), (6, 4, 14))
        self.assertEqual((report['alignment']['expected_only'], report['alignment']['actual_only']), ([], []))
        self.assertEqual(report['hypotheses'], [])
        summary = diag.compact_summary(report)
        self.assertEqual(summary['bounded_by'], 'unit_member_symbol')
        self.assertEqual(summary['extents'], dict(expected=6, candidate=6))

    def test_unbounded_member_keeps_the_standalone_refusal(self):
        report = self.diagnose(self.unit(member_labels=('_recovered', '_helper')))
        self.assertEqual((report['status'], report['reason']), ('UNSUPPORTED', 'CANDIDATE_ENTRY_NOT_AT_OBJECT_START'))
        self.assertTrue(report['unit_member_reason'].startswith('UNIT_MEMBER_OBJECT_HAS_UNSYMBOLED_LABELS'))
        self.assertIsNone(report['candidate_extent'])
        self.assertNotIn('bounded_by', report)

    def test_cached_prepared_unit_equal_keys_align_fully(self):
        for fid, key, size in (('ov11_F_415A', '652f00b4c6a427f60aea26a5177817679599139e4c154c0831edbd28e39b1e6d', 156),
                               ('ov11_F_6486', 'cc5bc703820070aa3a6bf394a025b98c7cfb1a7b476d904c864eba7969acb75b', 252)):
            if cached(key) is None:
                self.skipTest('cached prepared-unit compiler artifact unavailable')
            report = diag.diagnose(fid, key)
            self.assertEqual(report['status'], 'DIAGNOSTIC_ONLY', report.get('unit_member_reason'))
            self.assertEqual(report['bounded_by'], 'unit_member_symbol')
            self.assertEqual(report['candidate_extent']['bytes'], size)
            self.assertEqual((report['alignment']['expected_only'], report['alignment']['actual_only']), ([], []))
            self.assertEqual(report['hypotheses'], [])
            self.assertEqual(report['reference_identity']['counts']['unresolved'], 0)
            self.assertEqual(report['reference_identity']['counts']['different_identity'], 0)


class CodeDataBoundaryTests(unittest.TestCase):
    """Synthetic original/candidate pairs whose extents carry CODE data."""

    # cmp.l #2,d0; bcc.s default; asl.l #1,d0; move.w table(pc,d0.w),d0;
    # jmp (pc,d0.w); default: rts; table: 8,12; case0: moveq #1,d0; rts;
    # case1: moveq #2,d0; rts.
    SWITCH = 'b0bc00000002' '640a' 'e380' '303b0008' '4efb0000' '4e75' '0008000c' '70014e75' '70024e75'
    LISTING_TABLE = ('\tpublic\t_recovered\n_recovered:\n\tcmp.l\t#2,d0\n\tbcc\t.8\n\tasl.l\t#1,d0\n'
                     '\tmove.w\t.19(pc,d0.w),d0\n.20\n\tjmp\t(pc,d0.w)\n.8\n\trts\n.19\n'
                     '\tdc.w\t.9-.20-2\n\tdc.w\t.10-.20-2\n.9\n\tmoveq\t#1,d0\n\trts\n.10\n\tmoveq\t#2,d0\n\trts\n'
                     '.2\tequ\t0\n.3\treg\t\n\tend\n')
    # pea .1(pc); rts; .1: "abc\0"
    POOL_CODE = '487a0004' '4e75'
    LISTING_POOL = ('\tpublic\t_recovered\n_recovered:\n\tpea\t.1+0\n\trts\n.2\tequ\t0\n.3\treg\t\n.1\n'
                    '\tdc.b\t97,98,99,0\n\tds\t0\n\tpublic\t_F_h00_1234\n\tdseg\n\tpublic\t_G_h01_0010\n\tend\n')

    def table(self, raw):
        tables, why = diag._reachable_jump_tables(bytes.fromhex(raw))
        self.assertIsNone(why)
        return tables

    def test_listing_declares_pool_tables_and_refuses_unclassified_code_data(self):
        stmts, nxt, why = diag._listing_section(self.LISTING_POOL, '_recovered')
        self.assertIsNone(why)
        self.assertIsNone(nxt)
        declared, why = diag.listing_code_data(stmts)
        self.assertEqual((declared['pool']['bytes'], declared['pool']['references'], declared['tables']),
                         (b'abc\0', [0], []))
        stmts, _, _ = diag._listing_section(self.LISTING_TABLE, '_recovered')
        declared, _ = diag.listing_code_data(stmts)
        self.assertEqual([len(t['entries']) for t in declared['tables']], [2])
        self.assertTrue(declared['tables'][0]['referenced'])
        for text, reason in (
                ('_recovered:\n\trts\n\tdc.w\t1\n', 'LISTING_UNLABELLED_CODE_DATA'),
                ('_recovered:\n\trts\n.1\n\tdc.w\t3\n', 'LISTING_UNCLASSIFIED_CODE_WORDS'),
                ('_recovered:\n\trts\n.1\n\tdc.l\t3\n', 'LISTING_UNCLASSIFIED_CODE_DATA'),
                ('_recovered:\n.1\n\tdc.b\t1,0\n\trts\n', 'LISTING_LITERAL_POOL_NOT_AT_SECTION_END'),
                ('_recovered:\n\trts\n.1\n\tdc.b\t1,0\n.4\n\tdc.b\t2,0\n', 'LISTING_HAS_MULTIPLE_LITERAL_POOLS')):
            stmts, _, _ = diag._listing_section(text, '_recovered')
            declared, why = diag.listing_code_data(stmts)
            self.assertIsNone(declared)
            self.assertTrue(why.startswith(reason), why)
        self.assertTrue(diag._listing_section('_other:\n\trts\n', '_recovered')[2].startswith('LISTING_ENTRY_LABEL_ABSENT'))

    def test_jump_table_entries_are_targets_that_must_map_to_paired_blocks(self):
        tables = self.table(self.SWITCH)
        self.assertEqual([(t['dispatch_offset'], t['table_start'], [e['target'] for e in t['entries']]) for t in tables],
                         [(14, 20, [24, 28])])
        same = diag.compare_code(bytes.fromhex(self.SWITCH), bytes.fromhex(self.SWITCH),
                                 expected_tables=tables, actual_tables=tables)
        self.assertEqual(same['status'], 'DIAGNOSTIC_ONLY')
        self.assertEqual([t['state'] for t in same['blocks']['jump_tables']], ['consistent'])
        self.assertEqual(same['hypotheses'], [])
        self.assertEqual(same['blocks']['indirect_transfers'], [])
        # Swapped entries: the table decodes, but entry targets no longer map.
        swapped = self.SWITCH.replace('0008000c', '000c0008')
        report = diag.compare_code(bytes.fromhex(self.SWITCH), bytes.fromhex(swapped),
                                   expected_tables=tables, actual_tables=self.table(swapped))
        row = report['blocks']['jump_tables'][0]
        self.assertEqual((row['state'], [m['index'] for m in row['mismatched_entries']]),
                         ('different_or_unresolved', [0, 1]))
        self.assertIn('control_flow_target_or_edge', {h['category'] for h in report['hypotheses']})
        # Without table evidence the table bytes are never accepted as a data span.
        self.assertEqual(diag.compare_code(bytes.fromhex(self.SWITCH), bytes.fromhex(self.SWITCH),
                                           data_spans=((20, 24),))['status'], 'UNSUPPORTED')

    def candidate(self, code_hex, listing, *, write_listing=True):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        if write_listing:
            (Path(tmp.name) / 't000.asm').write_text(listing)
        symbols = [dict(hunk=3, name='__H3_org', offset=0), dict(hunk=3, name='_recovered', offset=0),
                   dict(hunk=3, name='__H3_end', offset=len(code_hex) // 2)]
        contribution = dict(hunk=3, code_hex=code_hex, code_size=len(code_hex) // 2, symbols=symbols, relocations=[],
                            all_relocations=[], hunks=[], data_size=0, bss_size=0, entry_offset=0)
        return dict(status='COMPILED', directory=tmp.name, prefix='t000', cache_key='d' * 64,
                    identity=dict(profile='aztec36', object_labels=['candidate']), contribution=contribution)

    def original(self, raw, *, pool_text=None, tables=()):
        start = 0x100
        f = dict(id='ov04_F_0100', hunk=9, start=start, end=start + len(raw) // 2, size=len(raw) // 2,
                 extent_status='CLOSED_CFG', raw_bytes=raw, referenced_data=[], referenced_strings=[],
                 direct_callees=[], relocations=[], jump_tables=list(tables))
        if pool_text is not None:
            f['referenced_data'] = [dict(kind='PC_RELATIVE_DATA', hunk=9, offset=f['end'], instruction_offset=start)]
            f['referenced_strings'] = [dict(hunk=9, offset=f['end'], text=pool_text)]
        return f

    def diagnose(self, f, unit):
        ledger = dict(game_sha256='0' * 64, a4=dict(bias=32766, evidence=dict(relocation=dict(target_hunk=1, addend_raw=32766))))
        with mock.patch.object(diag, 'validated_function', return_value=(f, ledger)), \
                mock.patch.object(diag, 'cached', return_value=unit):
            return diag.diagnose(f['id'], unit['cache_key'])

    def test_literal_pool_boundaries_come_from_each_side_independently(self):
        f = self.original(self.POOL_CODE, pool_text='abc')
        report = self.diagnose(f, self.candidate(self.POOL_CODE + '61626300', self.LISTING_POOL))
        self.assertEqual(report['status'], 'DIAGNOSTIC_ONLY', report.get('data_boundary_reason'))
        bound = report['data_boundary']
        self.assertEqual(bound['original_basis'], ['owned_code_data.expected_string_tail'])
        self.assertIn('candidate_listing_dc_b_literal_pool', bound['candidate_basis'])
        self.assertEqual(bound['code'], dict(original_bytes=6, candidate_bytes=6))
        self.assertTrue(bound['literal']['bytes_equal'] and bound['literal']['pc_targets_equal'])
        self.assertEqual((report['candidate_extent']['bytes'], report['candidate_extent']['code_bytes']), (10, 6))
        self.assertEqual(report['hypotheses'], [])
        self.assertEqual(report['reference_identity']['counts']['same_identity'], 1)
        summary = diag.compact_summary(report)
        self.assertTrue(summary['data_boundary']['literal']['bytes_equal'])
        # Different literal bytes: the boundary still stands; the data part differs.
        other = self.diagnose(f, self.candidate(self.POOL_CODE + '61626400',
                                                self.LISTING_POOL.replace('97,98,99', '97,98,100')))
        self.assertEqual(other['status'], 'DIAGNOSTIC_ONLY')
        self.assertEqual(other['data_boundary']['literal']['first_difference'], 2)
        self.assertEqual({h['category'] for h in other['hypotheses']}, {'data_ownership_review'})

    def test_candidate_boundary_that_is_not_independently_established_stays_unsupported(self):
        f = self.original(self.POOL_CODE, pool_text='abc')
        for unit, why in (
                (self.candidate(self.POOL_CODE + '61626300', self.LISTING_POOL, write_listing=False),
                 'CANDIDATE_LISTING_UNAVAILABLE'),
                (self.candidate(self.POOL_CODE + '61626400', self.LISTING_POOL),
                 'CANDIDATE_LISTING_POOL_BYTES_DISAGREE_WITH_PAYLOAD'),
                (self.candidate(self.POOL_CODE + '61626300', self.LISTING_POOL.replace('.1+0', '.1+1')),
                 'CANDIDATE_POOL_TARGETS_DISAGREE_WITH_LISTING_REFERENCES')):
            report = self.diagnose(f, unit)
            self.assertEqual((report['status'], report['reason']),
                             ('UNSUPPORTED', 'ORIGINAL_DATA_BOUNDARY_HAS_NO_MAPPED_CANDIDATE_BOUNDARY'))
            self.assertEqual(report['data_boundary_reason'], why)
            self.assertEqual(diag.compact_summary(report)['data_boundary_reason'], why)
        # The original side needs the strict owned-string proof as well.
        report = self.diagnose(self.original(self.POOL_CODE, pool_text='abcd'),
                               self.candidate(self.POOL_CODE + '61626300', self.LISTING_POOL))
        self.assertTrue(report['data_boundary_reason'].startswith('ORIGINAL_CODE_DATA_NOT_STRICTLY_PROVEN'))

    def test_original_and_candidate_jump_tables_are_paired_end_to_end(self):
        start = 0x100
        tables = [dict(t, dispatch_offset=t['dispatch_offset'] + start, table_start=t['table_start'] + start,
                       table_end=t['table_end'] + start,
                       entries=[dict(e, offset=e['offset'] + start, target=e['target'] + start) for e in t['entries']])
                  for t in self.table(self.SWITCH)]
        report = self.diagnose(self.original(self.SWITCH, tables=tables), self.candidate(self.SWITCH, self.LISTING_TABLE))
        self.assertEqual(report['status'], 'DIAGNOSTIC_ONLY', report.get('data_boundary_reason'))
        self.assertEqual(report['data_boundary']['original_basis'], ['census_pc_relative_word_jump_table'])
        self.assertIsNone(report['data_boundary']['literal'])
        self.assertEqual([t['state'] for t in report['blocks']['jump_tables']], ['consistent'])
        self.assertEqual(report['hypotheses'], [])
        # A listing that declares a different table shape is not a boundary.
        bad = self.LISTING_TABLE.replace('\tdc.w\t.10-.20-2\n', '')
        report = self.diagnose(self.original(self.SWITCH, tables=tables), self.candidate(self.SWITCH, bad))
        self.assertEqual(report['data_boundary_reason'], 'CANDIDATE_SWITCH_TABLES_DISAGREE_WITH_LISTING')

    def test_cached_code_data_controls_have_zero_differences(self):
        for fid, key in (('ov04_F_18A6', '55be4b1eedcb2030015091a69451d955253bc849b2188ea83da221400c2d538a'),
                         ('ov07_F_03CC', '616b5b9bfbedc1dd58aa3f760dc99e86429d878f17e42139e485c5389870b403'),
                         ('ov08_F_3DF4', '4d019117a0643cde05fa42afd6d381323c5a41f3135f52e6dcac30726ac5df76')):
            if cached(key) is None:
                self.skipTest('cached exact-verified compiler artifact unavailable')
            report = diag.diagnose(fid, key)
            self.assertEqual(report['status'], 'DIAGNOSTIC_ONLY', report.get('data_boundary_reason'))
            self.assertEqual((report['alignment']['expected_only'], report['alignment']['actual_only']), ([], []))
            self.assertEqual(report['hypotheses'], [])
            self.assertEqual(report['reference_identity']['counts']['unresolved'], 0)
            bound = report['data_boundary']
            self.assertEqual(bound['code']['original_bytes'], bound['code']['candidate_bytes'])
            if bound['literal']:
                self.assertTrue(bound['literal']['bytes_equal'] and bound['literal']['pc_targets_equal'])
            for row in report['blocks'].get('jump_tables', []):
                self.assertEqual(row['state'], 'consistent')

    def test_cached_ov04_0536_candidate_is_measurable(self):
        key = '8c7d483d046e0d37e94c64e73f60751d537551a569a39dcbe2f8a6b412c605ac'
        if cached(key) is None:
            self.skipTest('cached ov04_F_0536 compiler artifact unavailable')
        report = diag.diagnose('ov04_F_0536', key)
        self.assertEqual(report['status'], 'DIAGNOSTIC_ONLY', report.get('data_boundary_reason'))
        self.assertEqual(report['data_boundary']['code'], dict(original_bytes=622, candidate_bytes=682))
        self.assertEqual((report['data_boundary']['literal']['original_bytes'],
                          report['data_boundary']['literal']['candidate_bytes']), (38, 38))
        self.assertEqual(report['candidate_extent']['bytes'], 720)


if __name__ == '__main__':
    unittest.main()
