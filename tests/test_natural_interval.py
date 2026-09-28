"""Natural-interval units: order, compaction spans and gap-dependent encodings."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tests'))

import check_unit
import unit_diag
from common import FormatError


def fn(start,raw,calls=(),node='ov09',hunk=9):
    """A closed synthetic function; ``calls`` are (target, site) PC-relative calls."""
    size=len(raw)//2
    instructions=[]
    for target,site in calls:
        at=(site-start)*2
        instructions.append(dict(offset=site,raw=raw[at:at+8],size=2 if raw[at:at+2]=='61' and raw[at+2:at+4]!='00' else 4,
                                 mnemonic='jsr',operands=''))
    return dict(id='%s_F_%04X'%(node,start),hunk=hunk,node=node,start=start,end=start+size,size=size,raw_bytes=raw,
                extent_status='CLOSED_CFG',referenced_data=[],referenced_strings=[],relocations=[],
                instructions=instructions,
                direct_callees=[dict(id='%s_F_%04X'%(node,t),hunk=hunk,offset=t,site=s,basis='PC_RELATIVE') for t,s in calls])


NOPS='4e71'*99+'4e75'  # 200 bytes


def plan(members,interval,new_ids):
    with patch.object(check_unit,'recovery',return_value=dict(functions={})):
        return check_unit.natural_interval_plan(members,interval,set(new_ids))


def linked(root,code,symbols):
    (root/'candidate.c').write_text('recovered() {}\n');(root/'candidate.exe').write_bytes(b'\0'*64)
    return dict(status='COMPILED',identity=dict(profile='aztec36',flags=[]),cache_key='natural',cache_hit=True,
                directory=str(root),prefix='candidate',contribution=dict(
                    entry_offset=0,code_hex=code,code_size=len(code)//2,code_offset=0,hunk=3,data_size=0,bss_size=0,
                    relocations=[],all_relocations=[],object_sha256='test',
                    symbols=[dict(hunk=3,name=n,offset=o) for n,o in symbols],
                    hunks=[dict(number=0,content_offset=0),dict(number=1,initialized_size=0,allocated_size=0),
                           dict(number=2,allocated_size=0)]))


class DisplacementClassTests(unittest.TestCase):
    def test_classes(self):
        c=check_unit.displacement_class
        self.assertEqual([c(-128),c(127),c(0),c(128),c(-129),c(32767),c(-32769)],
                         ['BYTE','BYTE','WORD','WORD','WORD','WORD','OUT_OF_RANGE'])

    def test_interval_text(self):
        self.assertEqual(check_unit.parse_interval('0x4790..0x5CEA'),(0x4790,0x5CEA))
        for bad in ('0x10..0x10','0x10-0x20','x..y'):
            with self.subTest(bad=bad),self.assertRaises(FormatError):
                check_unit.parse_interval(bad)


class GapCrossingTests(unittest.TestCase):
    """Layout 0x64 A | 0x6A B (200 bytes) | gap | C, all in one interval."""

    def layout(self,gap,call_raw='4eba'):
        c_start=0x132+gap
        disp=c_start-0x66
        a=fn(0x64,call_raw+'%04x'%disp+'4e75',[(c_start,0x64)])
        b=fn(0x6A,NOPS)
        c=fn(c_start,'4e75')
        return [a,b,c],plan([a,b,c],(0x64,c_start+2),{a['id']})

    def test_long_call_whose_compact_distance_stays_long_is_gap_independent(self):
        members,layout=self.layout(14)
        self.assertEqual([r['id'] for r in layout['members']],[m['id'] for m in members])
        self.assertEqual([r['object_offset'] for r in layout['members']],[0,6,206])
        self.assertEqual([(s['start'],s['end'],s['kind']) for s in layout['compaction_spans']],[(0x132,0x140,'UNKNOWN_GAP')])
        self.assertEqual(layout['unknown_gaps'],[dict(start=0x132,end=0x140,size=14,ownership='UNKNOWN_NOT_ASSIGNED')])
        (row,)=layout['gap_crossings']
        self.assertEqual((row['original_displacement'],row['compact_displacement'],row['distance_delta']),(218,204,-14))
        self.assertEqual((row['original_class'],row['compact_class']),('WORD','WORD'))
        self.assertEqual(row['classification'],'GAP_INDEPENDENT_ENCODING')
        self.assertIsNone(layout['blocked_reason'])

    def test_canonical_members_are_regression_checks(self):
        members,layout=self.layout(14)
        a,b,c=members
        names={a['id']:'recovered',b['id']:'F_h09_006A',c['id']:'F_h09_0140'}
        symbols=(('_recovered',0),('_F_h09_006A',6),('_F_h09_0140',206))
        for tail,verdict in (('4e75','EQUAL'),('4e71','DIFFER')):
            with self.subTest(tail=tail),tempfile.TemporaryDirectory() as temp:
                report=check_unit.compare_unit(members,names,linked(Path(temp),'4eba00cc4e75'+NOPS+tail,symbols),
                                               32766,natural=layout)
                self.assertEqual(report['verdict'],verdict)
                self.assertEqual([r['id'] for r in report['canonical_regressions']],[b['id'],c['id']])
                self.assertEqual(report['canonical_regressions'][1]['verdict'],verdict)

    def test_long_call_that_would_fit_bsr_b_when_compacted_is_gap_dependent(self):
        # 0x66 + 0x9A: original WORD; compact without 0xAC gap bytes: BYTE.
        a=fn(0x64,'4eba009a4e75',[(0x100,0x64)])
        c=fn(0x100,'4e75')
        layout=plan([a,c],(0x64,0x102),{a['id']})
        (row,)=layout['gap_crossings']
        self.assertEqual((row['original_class'],row['compact_class'],row['compact_displacement']),('WORD','BYTE',4))
        self.assertEqual(row['classification'],'GAP_DEPENDENT_ENCODING')
        self.assertEqual(layout['blocked_reason'],'GAP_DEPENDENT_ENCODING')
        # Every member compares EQUAL by call identity, yet the unit is BLOCKED.
        with tempfile.TemporaryDirectory() as temp:
            report=check_unit.compare_unit([a,c],{a['id']:'recovered',c['id']:'F_h09_0100'},
                                           linked(Path(temp),'4eba00044e75'+'4e75',(('_recovered',0),('_F_h09_0100',6))),
                                           32766,natural=layout)
        self.assertEqual([m['verdict'] for m in report['members']],['EQUAL','EQUAL'])
        self.assertEqual((report['verdict'],report['reason'],report['member_verdict']),
                         ('BLOCKED','GAP_DEPENDENT_ENCODING','EQUAL'))
        self.assertEqual(report['canonical_regressions'],[dict(id=c['id'],verdict='EQUAL',reason=report['members'][1].get('reason'))])

    def test_short_call_across_a_gap_stays_short(self):
        a=fn(0x64,'61204e75',[(0x86,0x64)])
        c=fn(0x86,'4e75')
        layout=plan([a,c],(0x64,0x88),{a['id']})
        (row,)=layout['gap_crossings']
        self.assertEqual((row['original_class'],row['compact_class'],row['classification']),
                         ('BYTE','BYTE','GAP_INDEPENDENT_ENCODING'))

    def test_backward_call_and_non_crossing_calls(self):
        a=fn(0x64,'4e75')
        b=fn(0x66,'4ebaFFFC4e75'.lower(),[(0x64,0x66)])  # adjacent: no span crossed
        c=fn(0x140,'4eba%04x4e75'%((0x64-0x142)&0xFFFF),[(0x64,0x140)])
        layout=plan([a,b,c],(0x64,0x146),{c['id']})
        (row,)=layout['gap_crossings']
        self.assertEqual(row['member'],c['id'])
        # The backward distance shrinks by the 0x6C..0x140 gap: -222 becomes -10, a BYTE displacement.
        self.assertEqual((row['original_displacement'],row['compact_displacement'],row['distance_delta']),(-222,-10,212))
        self.assertEqual(row['classification'],'GAP_DEPENDENT_ENCODING')

    def test_target_inside_an_unlinked_span_blocks(self):
        a=fn(0x64,'4eba00304e75',[(0x96,0x64)])
        c=fn(0x100,'4e75')
        layout=plan([a,c],(0x64,0x102),{a['id']})
        self.assertEqual(layout['gap_crossings'][0]['classification'],'TARGET_IN_UNLINKED_SPAN')
        self.assertEqual(layout['blocked_reason'],'TARGET_IN_UNLINKED_SPAN')

    def test_outside_interval_callee_span_is_reported_separately(self):
        a=fn(0x64,'4e75')
        b=fn(0x200,'4eba%04x4e75'%((0x64-0x202)&0xFFFF),[(0x64,0x200)])
        layout=plan([a,b],(0x200,0x206),{b['id']})
        self.assertEqual([r['role'] for r in layout['members']],['canonical_outside_interval','new'])
        self.assertEqual(layout['compaction_spans'][0]['kind'],'UNLINKED_OUTSIDE_INTERVAL')
        self.assertEqual(layout['unknown_gaps'],[])
        self.assertEqual(layout['gap_crossings'][0]['classification'],'GAP_DEPENDENT_ENCODING')


class NaturalPreparationTests(unittest.TestCase):
    """Canonical A, new B, canonical C, gap, new D inside 0x100..0x140."""

    def setUp(self):
        self.a=fn(0x100,'4e75'*8);self.b=fn(0x110,'4e75'*8);self.c=fn(0x120,'4e75'*4)
        self.d=fn(0x130,'4e75'*8);self.far=fn(0x200,'4e75')
        self.b['direct_callees']=[dict(id=self.far['id'],hunk=9,offset=0x200,site=0x110,basis='PC_RELATIVE')]
        self.functions={f['id']:f for f in (self.a,self.b,self.c,self.d,self.far)}
        self.canonical={f['id']:dict(state='FUNCTION_CODE_MATCH',source='x.c',source_sha256=check_unit.sha256(b'recovered() {}\n'))
                        for f in (self.a,self.c,self.far)}

    def prepare(self,interval,member_sources,entry=None,canonical=None):
        functions=self.functions
        def validated(fid):
            if fid not in functions:raise FormatError('unknown function '+fid)
            return functions[fid],dict(functions=list(functions.values()),a4=dict(bias=32766))
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp)/'x.c').write_text('recovered() {}\n')
            with patch.object(check_unit,'validated_function',side_effect=validated), \
                 patch.object(check_unit,'recovery',return_value=dict(functions=self.canonical if canonical is None else canonical)), \
                 patch.object(check_unit,'ROOT',Path(temp)):
                return check_unit.prepare_unit((entry or self.b)['id'],'recovered() {}',True,False,False,
                                               member_sources=member_sources,natural_interval=interval)

    def test_every_interval_function_is_linked_in_address_order(self):
        members,names,parts,_,_=self.prepare('0x100..0x140',{self.d['id']:'recovered() {}'})
        self.assertEqual([m['start'] for m in members],[0x100,0x110,0x120,0x130,0x200])
        self.assertEqual(names[self.b['id']],'recovered')
        self.assertEqual(names[self.a['id']],'F_h09_0100')
        self.assertEqual(parts[self.c['id']],'F_h09_0120() {}\n')

    def test_unrecovered_interval_function_needs_a_source(self):
        with self.assertRaisesRegex(FormatError,'without a member source: ov09_F_0130'):
            self.prepare('0x100..0x140',{})

    def test_members_and_bounds_must_respect_the_interval(self):
        with self.assertRaisesRegex(FormatError,'outside the natural interval'):
            self.prepare('0x100..0x130',{self.d['id']:'recovered() {}'})
        with self.assertRaisesRegex(FormatError,'splits function ov09_F_0100'):
            self.prepare('0x104..0x140',{self.d['id']:'recovered() {}'})

    def test_legacy_modes_ignore_the_interval_machinery(self):
        # Without --natural-interval a gap is still refused as before.
        with self.assertRaisesRegex(FormatError,'unowned gaps'):
            self.prepare(None,{self.d['id']:'recovered() {}'})


class ReceiptSummaryTests(unittest.TestCase):
    def test_natural_receipt_summary_flags_dependent_crossings(self):
        receipt=dict(verdict='BLOCKED',reason='GAP_DEPENDENT_ENCODING',member_verdict='EQUAL',
                     canonical_regressions=[dict(id='x',verdict='EQUAL'),dict(id='y',verdict='DIFFER')],
                     natural_interval=dict(interval=[1,9],blocked_reason='GAP_DEPENDENT_ENCODING',
                                           compaction_spans=[dict(start=3,end=5,size=2,kind='UNKNOWN_GAP',after='a')],
                                           unknown_gaps=[dict(start=3,end=5,size=2)],gap_crossing_counts={'GAP_DEPENDENT_ENCODING':1},
                                           gap_crossings=[dict(member='a',classification='GAP_DEPENDENT_ENCODING',site=2),
                                                          dict(member='b',classification='GAP_INDEPENDENT_ENCODING')]))
        s=unit_diag.natural_receipt_summary(receipt)
        self.assertEqual([c['member'] for c in s['flagged_crossings']],['a'])
        self.assertEqual(s['canonical_not_equal'],['y'])
        self.assertEqual(s['unknown_gaps'],[[3,5]])
        self.assertEqual(s['compaction_spans'],[dict(start=3,end=5,size=2,kind='UNKNOWN_GAP')])


class NaturalPositiveControlTests(unittest.TestCase):
    """Re-prove an exact-verified contiguous unit in natural-interval mode from the cache only."""

    def test_three_member_unit_with_canonical_regressions(self):
        from test_multi_member_unit import cache_only
        key='f1abc6d578b8c6992aa0c0061c9c88ef9dc0562f2463f09f174e20951b74fc14'
        receipts=sorted((ROOT/'recovery/units/ov10_F_22E6'/key).glob('*/receipt.json'))
        if not receipts:self.skipTest('control receipt absent')
        with patch.object(check_unit,'compile_many',side_effect=cache_only), \
             patch.object(check_unit,'promote') as promote,patch.object(check_unit,'save_rank') as save_rank:
            dry=check_unit.check('ov10_F_22E6',receipts[0].parent/'candidate.c',['aztec36'],isolated=True,
                                 natural_interval='0x1FDE..0x25A2',prepare_only=True)[0]
            report=check_unit.check('ov10_F_22E6',receipts[0].parent/'candidate.c',['aztec36'],isolated=True,
                                    natural_interval='0x1FDE..0x25A2')[0]
        promote.assert_not_called();save_rank.assert_not_called()
        self.assertEqual(dry['verdict'],'PREPARED_NOT_COMPILED')
        self.assertEqual(dry['trials'][0]['cache_key'],key)
        self.assertEqual([m['id'] for m in dry['ordered_members']],['ov10_F_1FDE','ov10_F_2160','ov10_F_22E6'])
        self.assertEqual((report['cache_key'],report['verdict']),(key,'EQUAL'))
        self.assertEqual([c['verdict'] for c in report['canonical_regressions']],['EQUAL','EQUAL'])
        self.assertEqual(report['natural_interval']['compaction_spans'],[])
        self.assertEqual(report['verification_policy'],check_unit.NATURAL_POLICY)


if __name__=='__main__':
    unittest.main()
