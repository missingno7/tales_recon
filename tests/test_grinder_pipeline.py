import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError
from function_census import Census
from compiler_oracle import identity,validate_source,harness,cached
from function_compare import target_identity,unique_word_site,decode_all
from function_compare import compare_function
from recovery_state import evidence,ROOT
from compiler_oracle import CACHE
from unittest.mock import patch
from common import write_json,sha256
from recovery_evidence import load_promotions
from overlay_experiment import relocation_profile

class FunctionCensusTests(unittest.TestCase):
    def census(self,raw,ranges=None):
        b=bytes.fromhex(raw)
        model={'hunks':[{'number':0,'node':'resident','type':'CODE','content_offset':0,'initialized_size':len(b)}], 'relocations':[],'overlay':None}
        return Census(b,model,ranges or [])

    def test_calls_create_entries_without_swallowing_callee(self):
        c=self.census('4e550000610000064e5d4e754e5500004e5d4e75')
        r=c.run();fs={f['start']:f for f in r['functions']}
        self.assertEqual(set(fs),{0,12});self.assertEqual(fs[0]['size'],12)
        self.assertEqual(fs[12]['size'],8);self.assertEqual(fs[0]['extent_status'],'CLOSED_CFG')
        self.assertEqual(fs[0]['direct_callees'][0]['offset'],12)
        self.assertEqual(fs[12]['callers'][0]['site'],4)

    def test_return_does_not_linear_sweep_adjacent_code(self):
        c=self.census('4e5500004e5d4e754e5500004e5d4e75');r=c.run()
        self.assertEqual(r['summary']['decoded_bytes'],8);self.assertEqual(len(r['functions']),1)

    def test_data_barrier_blocks_promotion(self):
        c=self.census('4e5500004e5d4e75',[{'hunk':0,'start':4,'end':8,'classification':'STRING'}])
        f=c.run()['functions'][0];self.assertEqual(f['extent_status'],'UNCERTAIN')

    def test_indirect_jump_stops_without_inventing_switch_targets(self):
        c=self.census('4e5500004ed04e5d4e75');f=c.run()['functions'][0]
        self.assertEqual(f['extent_status'],'UNCERTAIN');self.assertEqual(f['size'],6)

    def test_seed_in_instruction_cannot_make_closed_extent(self):
        c=self.census('4e5500004e5d4e75');c.seed(0,2,{'kind':'RELOCATION_POINTER'})
        self.assertEqual(c.run()['functions'][0]['extent_status'],'UNCERTAIN')

    def test_a4_clobber_prevents_abi_identity_promotion(self):
        c=self.census('4e55000028404e5d4e75')
        self.assertEqual(c.run()['functions'][0]['extent_status'],'UNCERTAIN')

class VerifierContractTests(unittest.TestCase):
    def test_source_escape_hatches_rejected(self):
        for src in ('int recovered(){asm("rts");}','#include "x.h"\nint recovered(){return 0;}'):
            with self.assertRaises(FormatError):validate_source(src)

    def test_plain_harness_contains_no_fixed_placement(self):
        h=harness('extern char G_h01_1424; int recovered(){G_h01_1424=1;}')
        self.assertIn('char G_h01_1424;',h);self.assertNotIn('0x1424',h)

    def test_target_identity_requires_bounded_data_addend(self):
        symbols=[{'hunk':1,'offset':8,'name':'_G_h01_1424'}]
        self.assertIsNone(target_identity(1,10,symbols))
        self.assertEqual(target_identity(1,9,symbols,{'_G_h01_1424':12})['offset'],0x1425)
        self.assertIsNone(target_identity(1,20,symbols,{'_G_h01_1424':12}))

    def test_call_target_may_not_absorb_addend(self):
        self.assertIsNone(target_identity(0,2,[{'hunk':0,'offset':0,'name':'_F_h00_1234'}]))

    def test_non_unique_displacement_is_not_masked(self):
        instructions,_=decode_all(bytes.fromhex('196d00090009'))
        self.assertIsNone(unique_word_site(instructions[0],9))

    def test_cache_key_changes_with_source_flags_or_harness(self):
        a=identity('int recovered(a) int a; { return a; }','aztec36')[0]
        b=identity('int recovered(a) int a; { return a+1; }','aztec36')[0]
        c=identity('int recovered(a) int a; { return a; }','aztec36-long')[0]
        self.assertEqual(len({a,b,c}),3)


class CachedVerifierRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=ROOT/'experiments/grinder-bootstrap/ov14_F_03AE.c'
        if not source.exists():raise unittest.SkipTest('local historical bootstrap cache absent')
        key=identity(source.read_text(),'aztec36')[0]
        cls.compiled=cached(key)
        if cls.compiled is None:raise unittest.SkipTest('local historical bootstrap cache absent')
        l=evidence();cls.bias=l['a4']['bias'];cls.f=next(f for f in l['functions'] if f['id']=='ov14_F_03AE')

    def check(self,compiled=None,f=None):
        return compare_function(f or self.f,compiled or self.compiled,self.bias)

    def test_complete_contribution_matches(self):
        r=self.check();self.assertEqual(r['verdict'],'EQUAL')
        self.assertEqual(len(r['relocation_proof']),2)

    def test_trailing_instruction_cannot_be_ignored(self):
        c=copy.deepcopy(self.compiled);c['contribution']['code_hex']+='4e71'
        self.assertNotEqual(self.check(c)['verdict'],'EQUAL')

    def test_changed_opcode_cannot_be_masked(self):
        c=copy.deepcopy(self.compiled);s=c['contribution']['code_hex'];c['contribution']['code_hex']='4e71'+s[4:]
        self.assertNotEqual(self.check(c)['verdict'],'EQUAL')

    def test_same_displacement_wrong_global_identity_rejected(self):
        c=copy.deepcopy(self.compiled)
        for s in c['contribution']['symbols']:
            if s['name']=='_G_h01_1424':s['name']='_G_h01_1425'
        self.assertNotEqual(self.check(c)['verdict'],'EQUAL')

    def test_candidate_owned_data_is_not_silently_omitted(self):
        c=copy.deepcopy(self.compiled);c['contribution']['data_size']=2
        self.assertEqual(self.check(c)['verdict'],'BLOCKED')

    def test_missing_expected_relocation_rejected(self):
        f=copy.deepcopy(self.f);f['relocations']=[dict(relative_offset=4,type='RELOC32',width=4,target_hunk=1,addend_raw=0)]
        self.assertNotEqual(self.check(f=f)['verdict'],'EQUAL')

    def test_uncertain_extent_cannot_promote(self):
        f=copy.deepcopy(self.f);f['extent_status']='UNCERTAIN'
        self.assertEqual(self.check(f=f)['verdict'],'BLOCKED')

    def test_cache_metadata_corruption_rejected(self):
        with patch('compiler_oracle.extract',return_value={}):
            with self.assertRaises(FormatError):cached(self.compiled['cache_key'])

    def test_failed_candidate_preserves_canonical_ownership(self):
        import check_function
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);src=root/'candidate.c';src.write_text('recovered() { return 0; }')
            ledger=root/'recovery/ledger.json'
            initial={'schema_version':1,'functions':{'other':{'state':'FUNCTION_CODE_MATCH'}},'attempts':{},'blockers':{}}
            write_json(ledger,initial)
            c=copy.deepcopy(self.compiled);c['contribution']['code_hex']='4e5500004e5d4e75'
            with patch.object(check_function,'ROOT',root),patch.object(check_function,'LEDGER',ledger),patch.object(check_function,'recovery',lambda:json.loads(ledger.read_text())),patch.object(check_function,'validated_function',return_value=(self.f,{'a4':{'bias':self.bias}})),patch.object(check_function,'compile_many',return_value=[c]),patch.object(check_function,'save_rank'):
                r=check_function.check_many([dict(id=self.f['id'],source=str(src),profiles=['aztec36'])])
            self.assertEqual(r[0]['verdict'],'DIFFER')
            self.assertEqual(json.loads(ledger.read_text())['functions'],initial['functions'])
            self.assertFalse((root/'src').exists())

    def test_generated_coverage_rejects_source_or_proof_changes(self):
        from analysis_support import game
        b,m,_=game();l=evidence()
        original=json.loads((ROOT/'recovery/ledger.json').read_text())
        if self.f['id'] not in original['functions']:self.skipTest('bootstrap not promoted yet')
        item=original['functions'][self.f['id']]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);write_json(root/'recovery/ledger.json',dict(functions={self.f['id']:item}))
            for name in (item['source'],item['proof']):
                dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/name).read_bytes())
            self.assertEqual(len(load_promotions(root,b,m,l)),1)
            src=root/item['source'];before=src.read_bytes();src.write_bytes(before+b'\n')
            with self.assertRaises(FormatError):load_promotions(root,b,m,l)
            src.write_bytes(before);proof=root/item['proof'];proof.write_bytes(proof.read_bytes()+b'\n')
            with self.assertRaises(FormatError):load_promotions(root,b,m,l)
