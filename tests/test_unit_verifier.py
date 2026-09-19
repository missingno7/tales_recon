import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError
from compiler_oracle import identity,cached
from check_unit import prepare_unit,compare_unit
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

    def test_recovered_bridge_joins_a_contiguous_local_unit(self):
        source=ROOT/'experiments/direct-recovery/ov13_F_0190-v1.c'
        if not source.exists():self.skipTest('ov13 bridge candidate absent')
        members,names,combined,_=prepare_unit('ov13_F_0190',source.read_text())
        self.assertEqual([m['id'] for m in members],['ov13_F_0000','ov13_F_012E','ov13_F_0190'])
        self.assertIn('F_h13_012E()',combined)
        self.assertEqual(names['ov13_F_0000'],'F_h13_0000')
