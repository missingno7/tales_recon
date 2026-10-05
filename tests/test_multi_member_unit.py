"""Complete units whose members are all new (for example a same-node call cycle)."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

import check_unit
from common import FormatError
from compiler_oracle import cached,identity,object_specs

# Cycle A <-> B in original hunk 9: A (0x64) BSR.B B; RTS, B (0x68) BSR.B A; RTS.
A=dict(id='ov09_F_0064',hunk=9,start=0x64,end=0x68,size=4,raw_bytes='61024e75',extent_status='CLOSED_CFG',
       referenced_data=[],relocations=[],direct_callees=[dict(id='ov09_F_0068',hunk=9,offset=0x68,site=0x64,basis='PC_RELATIVE')])
B=dict(id='ov09_F_0068',hunk=9,start=0x68,end=0x6C,size=4,raw_bytes='61fa4e75',extent_status='CLOSED_CFG',
       referenced_data=[],relocations=[],direct_callees=[dict(id='ov09_F_0064',hunk=9,offset=0x64,site=0x68,basis='PC_RELATIVE')])
NAMES={A['id']:'recovered',B['id']:'F_h09_0068'}


def linked(root,code,symbols):
    (root/'candidate.c').write_text('recovered() {}\n');(root/'candidate.exe').write_bytes(b'\0'*64)
    return dict(status='COMPILED',identity=dict(profile='aztec36',flags=[]),cache_key='cycle',cache_hit=True,
                directory=str(root),prefix='candidate',contribution=dict(
                    entry_offset=0,code_hex=code,code_size=len(code)//2,code_offset=0,hunk=3,data_size=0,bss_size=0,
                    relocations=[],all_relocations=[],object_sha256='test',
                    symbols=[dict(hunk=3,name=n,offset=o) for n,o in symbols],
                    hunks=[dict(number=0,content_offset=0),dict(number=1,initialized_size=0,allocated_size=0),
                           dict(number=2,allocated_size=0)]))


class CyclicUnitComparisonTests(unittest.TestCase):
    def compare(self,code,symbols=(('_recovered',0),('_F_h09_0068',4)),names=NAMES,allow_gaps=False):
        with tempfile.TemporaryDirectory() as temp:
            return check_unit.compare_unit([A,B],names,linked(Path(temp),code,symbols),32766,allow_gaps=allow_gaps)

    def test_mutual_calls_between_new_members_prove_as_one_unit(self):
        for gaps in (False,True):
            report=self.compare('61024e75'+'61fa4e75',allow_gaps=gaps)
            self.assertEqual(report['verdict'],'EQUAL')
            self.assertEqual([m['verdict'] for m in report['members']],['EQUAL','EQUAL'])
            back=[p for p in report['members'][1]['relocation_proof'] if p['kind']=='PC_RELATIVE_CALL_SYMBOL']
            # The call back to the entry binds through its linked _recovered symbol.
            self.assertEqual([(p['identity']['hunk'],p['identity']['offset']) for p in back],[(9,0x64)])

    def test_one_wrong_member_fails_the_whole_unit(self):
        report=self.compare('61024e75'+'61fa4e71')
        self.assertEqual(report['verdict'],'DIFFER')
        self.assertEqual(report['reason'],'MEMBER_DIFFERS')
        self.assertEqual([m['verdict'] for m in report['members']],['EQUAL','DIFFER'])

    def test_intra_unit_call_bound_to_the_wrong_member_fails(self):
        # B calls itself instead of A: same length, wrong local identity.
        report=self.compare('61024e75'+'61fe4e75')
        self.assertEqual(report['verdict'],'DIFFER')
        self.assertIn('DIRECT_CALL_BINDING_UNPROVEN',[i['kind'] for i in report['members'][1]['relocation_issues']])
        # Swapped member symbols cannot satisfy the ordered linked partition.
        with self.assertRaises(FormatError):
            self.compare('61024e75'+'61fa4e75',symbols=(('_F_h09_0068',0),('_recovered',4)))

    def test_candidate_bytes_beyond_the_members_are_not_claimed(self):
        # An extra function standing in for an original gap is never absorbed.
        report=self.compare('61024e75'+'61fa4e75'+'4e75',
                            symbols=(('_recovered',0),('_F_h09_0068',4),('_F_h09_006C',8)),allow_gaps=True)
        self.assertEqual((report['verdict'],report['reason']),('DIFFER','COMPLETE_UNIT_SIZE_DIFFERS'))


class MultiMemberPreparationTests(unittest.TestCase):
    def prepare(self,functions,member_sources,source,allow_gaps=False,remove=True,canonical=None):
        def validated(fid):
            if fid not in functions:raise FormatError('unknown function '+fid)
            return functions[fid],dict(functions=list(functions.values()),a4=dict(bias=32766))
        with patch.object(check_unit,'validated_function',side_effect=validated), \
             patch.object(check_unit,'recovery',return_value=dict(functions=canonical or {})):
            return check_unit.prepare_unit(A['id'],source,True,allow_gaps,remove,member_sources=member_sources)

    def test_cycle_sources_bind_the_entry_and_member_names(self):
        functions={A['id']:A,B['id']:B}
        entry='extern int F_h09_0068();\nrecovered() { F_h09_0068(); }\n'
        other='extern int F_h09_0064();\nrecovered() { F_h09_0064(); }\n'
        members,names,parts,combined,_=self.prepare(functions,{B['id']:other},entry,remove=False)
        self.assertEqual([m['id'] for m in members],[A['id'],B['id']])
        self.assertEqual(parts[B['id']],'extern int recovered();\nF_h09_0068() { recovered(); }\n')
        _,_,parts,combined,_=self.prepare(functions,{B['id']:other},entry)
        self.assertNotIn('extern',combined)
        self.assertIn('F_h09_0068() { recovered(); }',combined)

    def test_without_members_a_cycle_still_needs_a_canonical_dependency(self):
        with self.assertRaisesRegex(FormatError,'unrecovered same-node dependency: ov09_F_0068'):
            self.prepare({A['id']:A,B['id']:B},{},'recovered() {}')

    def test_gaps_and_unknown_members_are_refused(self):
        far=dict(B,id='ov09_F_0070',start=0x70,end=0x74,direct_callees=[])
        a=dict(A,direct_callees=[])
        with self.assertRaisesRegex(FormatError,'unowned gaps'):
            self.prepare({A['id']:a,far['id']:far},{far['id']:'recovered() {}'},'recovered() {}')
        with self.assertRaisesRegex(FormatError,'unknown function ov09_F_006C'):
            self.prepare({A['id']:a},{'ov09_F_006C':'recovered() {}'},'recovered() {}',allow_gaps=True)
        other=dict(far,id='ov10_F_0070',hunk=10)
        with self.assertRaisesRegex(FormatError,'outside the entry CODE hunk'):
            self.prepare({A['id']:a,other['id']:other},{other['id']:'recovered() {}'},'recovered() {}',allow_gaps=True)


class MultiMemberPromotionTests(unittest.TestCase):
    def setUp(self):
        self.report=dict(verdict='EQUAL',reason='ENTIRE_OBJECT_AND_ALL_MEMBER_CONTRIBUTIONS',expected_length=8,actual_length=8,
                         members=[dict(id=A['id'],verdict='EQUAL'),dict(id=B['id'],verdict='EQUAL')],
                         member_sources={A['id']:check_unit.sha256(b'a'),B['id']:check_unit.sha256(b'b')})
        self.comparison=dict(id=A['id'],verdict='EQUAL',complete_unit_receipt='recovery/units/x/receipt.json',
                             complete_unit_receipt_sha256='0'*64)

    def run_promotion(self,canonical):
        import check_function
        with patch.object(check_unit,'recovery',return_value=dict(functions=canonical)), \
             patch.object(check_function,'regression_receipt',return_value=dict(passed=True)) as regression, \
             patch.object(check_unit,'promote',return_value='promoted') as promote:
            try:
                check_unit.promote_unit_members(A['id'],'a',{B['id']:'b'},[A,B],self.report,self.comparison,{},'FUNCTION_CODE_MATCH')
            finally:
                self.calls=(regression.call_count,promote.call_args_list)

    def test_every_new_member_is_promoted_with_the_shared_receipt(self):
        self.run_promotion({})
        runs,calls=self.calls
        self.assertEqual(runs,1)
        self.assertEqual([c.args[0] for c in calls],[A['id'],B['id']])
        for c in calls:
            self.assertEqual(c.args[2]['complete_unit_receipt'],'recovery/units/x/receipt.json')
            self.assertEqual(c.kwargs['regression'],dict(passed=True))
        self.assertEqual(calls[1].args[2]['source_sha256'],check_unit.sha256(b'b'))

    def test_a_conflicting_member_blocks_every_write(self):
        extent=dict(hunk=9,start=0x68,end=0x6C)
        with self.assertRaises(FormatError):
            self.run_promotion({B['id']:dict(source_sha256='f'*64,evidence_extent=extent)})
        self.assertEqual(self.calls,(0,[]))
        self.report['members'][1]['verdict']='DIFFER'
        with self.assertRaises(FormatError):
            self.run_promotion({})
        self.assertEqual(self.calls,(0,[]))


def cache_only(trials):
    out=[]
    for t in trials:
        objects=object_specs(t) if t.get('objects') is not None else None
        compiled=cached(identity(t['source'],t['profile'],t.get('target_node',1),objects,t.get('local_functions',()))[0])
        if compiled is None:raise unittest.SkipTest('positive-control compile cache absent')
        out.append(compiled)
    return out


class PositiveControlTests(unittest.TestCase):
    """Re-prove exact-verified units with every member supplied as new source."""

    def control(self,entry,cache_key,others,**options):
        from recovery_state import recovery
        receipts=sorted((ROOT/'recovery/units'/entry/cache_key).glob('*/receipt.json'))
        if not receipts:self.skipTest('control receipt absent')
        functions=recovery()['functions']
        if not all(o in functions for o in others):self.skipTest('control members not canonical')
        members={o:ROOT/functions[o]['source'] for o in others}
        with patch.object(check_unit,'compile_many',side_effect=cache_only), \
             patch.object(check_unit,'promote') as promote,patch.object(check_unit,'save_rank') as save_rank:
            reports=check_unit.check(entry,ROOT/functions[entry]['source'],['aztec36'],isolated=True,
                                     member_sources=members,**options)
        promote.assert_not_called();save_rank.assert_not_called()
        report=reports[0]
        self.assertEqual(report['cache_key'],cache_key)
        self.assertEqual(report['verdict'],'EQUAL')
        self.assertEqual(set(report['member_sources']),{entry,*others})
        self.assertEqual(report['dependency_sources'],{})
        self.assertEqual(report['acceptance'],'ALL_NEW_MEMBERS_EQUAL_IN_ONE_COMPLETE_UNIT')

    def test_two_member_single_object_unit(self):
        self.control('ov10_F_2160','af14c54801ae01b91b77bdd8a571641445390950e915f1febc540d5e712ab7d5',['ov10_F_1FDE'],separate_objects=False)

    def test_six_member_compact_unit(self):
        self.control('ov11_F_3B92','71af3f34444521e9f48df3ce43d629067859ec436d2e989ee6ba7e87a4870ea1',
                     ['ov11_F_25D6','ov11_F_25F8','ov11_F_37A0','ov11_F_40E0','ov11_F_4696'],
                     separate_objects=True,allow_gaps=True,join_direct_callees=True)


if __name__=='__main__':
    unittest.main()
