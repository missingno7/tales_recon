import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError
from compiler_oracle import identity,cached
from check_unit import prepare_unit,compare_unit,partitioned_objects,stable_receipt
from function_compare import compare_function
from recovery_state import ROOT


class CompleteUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=ROOT/'experiments/grinder-leaves/ov11_F_25F8-01.c'
        if not source.exists():raise unittest.SkipTest('local unit bootstrap absent')
        cls.members,cls.names,combined,ledger=prepare_unit('ov11_F_25F8',source.read_text())
        cls.compiled=cached(identity(combined,'aztec36')[0]);cls.bias=ledger['a4']['bias']
        if cls.compiled is None:raise unittest.SkipTest('local unit compilation cache absent')

    def compare(self,c=None):return compare_unit(self.members,self.names,c or self.compiled,self.bias)

    def test_entire_unit_and_call_targets_match(self):
        r=self.compare();self.assertEqual(r['verdict'],'EQUAL');self.assertEqual(r['unclaimed_bytes'],0)
        self.assertEqual(r['actual_length'],88)
        self.assertEqual(len(r['members'][1]['relocation_proof']),2)

    def test_no_standalone_slice_promotion(self):
        self.assertEqual(compare_function(self.members[1],self.compiled,self.bias)['verdict'],'BLOCKED')

    def test_extra_trailing_instruction_rejects_unit(self):
        c=copy.deepcopy(self.compiled);c['contribution']['code_hex']+='4e71'
        self.assertNotEqual(self.compare(c)['verdict'],'EQUAL')

    def test_changed_dependency_cannot_be_omitted(self):
        c=copy.deepcopy(self.compiled);raw=c['contribution']['code_hex'];c['contribution']['code_hex']='4e71'+raw[4:]
        self.assertNotEqual(self.compare(c)['verdict'],'EQUAL')

    def test_wrong_call_identity_rejected_even_with_same_bytes(self):
        c=copy.deepcopy(self.compiled)
        for s in c['contribution']['symbols']:
            if s['name']=='_F_h11_25D6':s['name']='_F_h11_25D8'
        names=dict(self.names);names['ov11_F_25D6']='F_h11_25D8'
        self.assertEqual(compare_unit(self.members,names,c,self.bias)['verdict'],'DIFFER')

    def test_call_into_middle_of_dependency_is_not_normalized(self):
        c=copy.deepcopy(self.compiled);raw=bytearray.fromhex(c['contribution']['code_hex'])
        raw[34+17]+=2;c['contribution']['code_hex']=raw.hex()
        self.assertEqual(self.compare(c)['verdict'],'DIFFER')

    def test_shifted_function_symbol_rejects_natural_partition(self):
        c=copy.deepcopy(self.compiled)
        for s in c['contribution']['symbols']:
            if s['name']=='_recovered':s['offset']+=2
        with self.assertRaises(FormatError):self.compare(c)

    def test_owned_data_requires_stronger_proof(self):
        c=copy.deepcopy(self.compiled);c['contribution']['data_size']=2
        self.assertEqual(self.compare(c)['verdict'],'BLOCKED')

    def test_same_overlay_pc_call_uses_proven_original_unit_coordinates(self):
        """Temporary link hunk numbers cannot hide a verified local call."""
        first=dict(id='ov09_F_0064',hunk=9,start=100,end=102,size=2,raw_bytes='4e75',
                   extent_status='CLOSED_CFG',referenced_data=[],relocations=[],direct_callees=[])
        caller=dict(id='ov09_F_0066',hunk=9,start=102,end=108,size=6,raw_bytes='4ebafffc4e75',
                    extent_status='CLOSED_CFG',referenced_data=[],relocations=[],
                    direct_callees=[dict(id='ov09_F_0064',hunk=9,offset=100,site=102)])
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'candidate.c').write_text('recovered() {}\n')
            (root/'candidate.exe').write_bytes(b'\0'*64)
            compiled=dict(status='COMPILED',identity=dict(profile='aztec36',flags=[]),cache_key='unit-map',cache_hit=True,
                directory=str(root),prefix='candidate',contribution=dict(entry_offset=0,code_hex='4e754ebafffc4e75',
                code_size=8,code_offset=0,hunk=3,data_size=0,bss_size=0,relocations=[],all_relocations=[],object_sha256='test',
                symbols=[dict(hunk=3,name='_F_h09_0064',offset=0),dict(hunk=3,name='_recovered',offset=2)],
                hunks=[dict(number=0,content_offset=0),dict(number=1,initialized_size=0,allocated_size=0),dict(number=2,allocated_size=0)]))
            report=compare_unit([first,caller],{first['id']:'F_h09_0064',caller['id']:'recovered'},compiled,32766)
        self.assertEqual(report['verdict'],'EQUAL')
        self.assertIn('PC_RELATIVE_CALL_SYMBOL',[p['kind'] for p in report['members'][1]['relocation_proof']])

    def test_target_owned_tail_precedes_a_separately_linked_callee(self):
        """A compact gap proof keeps a target's literal bundle in its object."""
        target=dict(id='ov09_F_0064',hunk=9,start=100,end=102,size=2,raw_bytes='4e75',
                    extent_status='CLOSED_CFG',referenced_data=[],referenced_strings=[],relocations=[],direct_callees=[])
        callee=dict(id='ov09_F_00C8',hunk=9,start=200,end=202,size=2,raw_bytes='4e75',
                    extent_status='CLOSED_CFG',referenced_data=[],referenced_strings=[],relocations=[],direct_callees=[])
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'candidate.c').write_text('recovered() {}\n')
            (root/'candidate.exe').write_bytes(b'\0'*64)
            compiled=dict(status='COMPILED',identity=dict(profile='aztec36',flags=[]),cache_key='unit-tail',cache_hit=True,
                directory=str(root),prefix='candidate',contribution=dict(entry_offset=0,code_hex='4e7558004e75',
                code_size=6,code_offset=0,hunk=3,data_size=0,bss_size=0,relocations=[],all_relocations=[],object_sha256='test',
                symbols=[dict(hunk=3,name='_recovered',offset=0),dict(hunk=3,name='_F_h09_00C8',offset=4)],
                hunks=[dict(number=0,content_offset=0),dict(number=1,initialized_size=0,allocated_size=0),dict(number=2,allocated_size=0)]))
            ownership=dict(start=102,end=104,strings=[dict(offset=102,text='X')],alignment_padding=0)
            with patch('owned_code_data.expected_string_tail',return_value=(b'X\0',ownership)):
                report=compare_unit([target,callee],{target['id']:'recovered',callee['id']:'F_h09_00C8'},
                                    compiled,32766,owned_code_data=True,allow_gaps=True)
        self.assertEqual(report['verdict'],'EQUAL')
        self.assertEqual(report['expected_compiled_length'],6)
        self.assertEqual(report['members'][0]['proof_level'],'FUNCTION_WITH_DATA_MATCH')

    def test_recovered_bridge_joins_a_contiguous_local_unit(self):
        source=ROOT/'experiments/direct-recovery/ov13_F_0190-v1.c'
        if not source.exists():self.skipTest('ov13 bridge candidate absent')
        members,names,combined,_=prepare_unit('ov13_F_0190',source.read_text())
        self.assertEqual([m['id'] for m in members],['ov13_F_0000','ov13_F_012E','ov13_F_0190'])
        self.assertIn('F_h13_012E()',combined)
        self.assertEqual(names['ov13_F_0000'],'F_h13_0000')

    def test_transitive_local_calls_close_the_whole_source_unit(self):
        source=ROOT/'experiments/direct-recovery/ov04_F_0000-v1.c'
        if not source.exists():self.skipTest('ov04 wrapper candidate absent')
        members,_,_,_=prepare_unit('ov04_F_0000',source.read_text())
        self.assertEqual([m['id'] for m in members],[
            'ov04_F_0000','ov04_F_000C','ov04_F_0088','ov04_F_00C4',
            'ov04_F_00E6','ov04_F_0104','ov04_F_037E'])

    def test_bridge_extern_for_an_earlier_member_is_removed(self):
        # ov10_F_2160 calls the earlier ov10_F_1FDE and its canonical source
        # still carries the old external declaration.  It must not survive in
        # a larger natural unit, where it would hide the first definition from
        # Manx's linked symbol map.
        _,_,combined,_=prepare_unit('ov10_F_22E6','recovered() {}')
        self.assertNotIn('extern int F_h10_1FDE();',combined)

    def test_separate_source_parts_retain_direct_callee_return_declarations(self):
        source='extern long F_h11_4610(); recovered() { return F_h11_4610(); }'
        _,_,parts,_,_=prepare_unit('ov11_F_23F4',source,True,True,False)
        self.assertIn('extern long F_h11_4610();',parts['ov11_F_23F4'])

    def test_gap_partition_joins_only_adjacent_direct_calls(self):
        first=dict(id='ov09_F_0000',hunk=9,start=0,end=2,direct_callees=[dict(id='ov09_F_0002',hunk=9)])
        second=dict(id='ov09_F_0002',hunk=9,start=2,end=4,direct_callees=[])
        distant=dict(id='ov09_F_0010',hunk=9,start=16,end=18,direct_callees=[])
        names={first['id']:'recovered',second['id']:'F_h09_0002',distant['id']:'F_h09_0010'}
        parts={first['id']:'extern int F_h09_0002(); recovered() { F_h09_0002(); }',
               second['id']:'F_h09_0002() {}',distant['id']:'F_h09_0010() {}'}
        objects=partitioned_objects([first,second,distant],names,parts,True)
        self.assertEqual(len(objects),2)
        self.assertIn('F_h09_0002() {}',objects[0]['source'])
        self.assertNotIn('extern int F_h09_0002();',objects[0]['source'])
        self.assertEqual(objects[1]['source'],parts[distant['id']])

    def test_persisted_receipt_has_no_nested_cache_observations(self):
        receipt=stable_receipt(dict(cache_hit=True,members=[dict(cache_hit=False,
            owned_code_data=dict(code_comparison=dict(cache_hit=True,verdict='EQUAL')))]))
        self.assertNotIn('cache_hit',str(receipt))
