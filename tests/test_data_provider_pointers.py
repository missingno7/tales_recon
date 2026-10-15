import copy,json,pathlib,unittest
from unittest.mock import patch
from common import FormatError
from analysis_support import ROOT,game
from evidence_snapshot import isolated_verification
from recovery_evidence import load_promotions
from hunk import parse
import data_providers as dp
import data_provider_pointers as ptr
import data_provider_job as gen
HERE=pathlib.Path(__file__).resolve().parents[1]

class ExternalPointerControls(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.context=isolated_verification(ROOT);cls.context.__enter__()
  cls.fact=json.loads((HERE/'evidence/data-providers/resident_data_292E.json').read_bytes());cls.recipe=json.loads((HERE/'evidence/data-providers/producer-0003.json').read_bytes());w=ROOT/cls.recipe['job']/'sys/work';cls.files={n:(w/n).read_bytes() for n in cls.recipe['artifacts']};cls.blob,cls.model,_=game();cls.analysis=dp.document(ROOT,'evidence/functions/ledger.json');cls.ledger=dp.document(ROOT,'recovery/ledger.json');cls.promotions=load_promotions(ROOT,cls.blob,cls.model,cls.analysis)
 @classmethod
 def tearDownClass(cls):cls.context.__exit__(None,None,None)
 def f(self):return copy.deepcopy(self.fact)
 def compare(self,f=None,obj=None,linked=None,model=None):return dp.compare_data(self.blob,model or self.model,f or self.fact,obj or self.files['p292e.o'],linked or self.files['p292e.exe'],self.files['p292e.sym'].decode())
 def typed(self,f=None,ledger=None):return ptr.typed_evidence(ROOT,f or self.fact,self.blob,self.model,self.analysis,ledger or self.ledger)
 def test_complete44_named_pointer_object_and_relocations(self):
  r=self.compare();self.assertEqual(r['sections'],dict(CODE=0,DATA=176,BSS=0,COMMON=0));self.assertEqual(len(r['original_relocations']),44);self.assertEqual(len(set(x['symbol'] for x in r['relocation_bindings'])),36);self.assertEqual(self.typed()[0]['count'],44)
 def test_off_by_one_is_period_data_not45th_pointer(self):
  r=self.typed()[0];self.assertEqual(r['index_limit_inclusive'],44);self.assertFalse(r['index44']['pointer']);self.assertTrue(r['index44']['unproved_execution'])
  f=self.f();f['original']['size']=180;f['object_sections']['DATA']=180;d=f['definitions'][0];d['count']=45;d['targets'].append(d['targets'][-1]);d['bounds']['bytes']=180
  with self.assertRaises(FormatError):dp.source(f)
 def test_control_has_repeated_named_external_targets(self):
  r=ptr.control_report(self.files,ptr.binder_names([self.fact]));self.assertEqual((r['DATA'],r['relocations'],r['unique_named_targets'],r['game_credit']),(12,3,2,0))
 def test_external_symbol_indices_cross16_and32(self):
  p=ptr.object_data(self.files['p292e.o'],'_G_h01_292E',self.fact['definitions'][0]['targets']);self.assertEqual(len(p['symbols']),37);self.assertIn(b'\xfd\x74\x02',self.files['p292e.o']);self.assertEqual(len(p['fixups']),44)
 def test_source_is_named_function_designators_only(self):
  src=dp.source(self.fact);self.assertIn(b'typedef void (*DP_CodeEntry)();',src);self.assertNotIn(b'0x',src);self.assertNotIn(b'char ',src);self.assertNotIn(b'long ',src);self.assertIn(b'G_h01_292E[44]',src)
 def test_integer_target_and_opaque_carriers_reject(self):
  for mode in ['integer','char','long','initializer']:
   f=self.f();d=f['definitions'][0]
   if mode=='integer':d['targets'][0]=0x5cd6
   elif mode=='initializer':d['initializer']=[0]*44
   else:d['type']=mode
   with self.assertRaises(FormatError):dp.source(f)
 def test_wrong_named_target_and_unproved_symbol_reject(self):
  for n,b in [('_recon_h00_5A50',dict(hunk=0,offset=0x5a50,provider='resident_driver_5A50')),('_recon_h00_5CC2',dict(hunk=0,offset=0x5cc2,provider='resident_driver_5A50'))]:
   f=self.f();old=f['definitions'][0]['targets'][0];f['definitions'][0]['targets'][0]=n;del f['bindings'][old];f['bindings'][n]=b
   with self.assertRaises(FormatError):self.typed(f)
 def test_canonical_target_provider_must_be_accepted(self):
  l=copy.deepcopy(self.ledger);del l['reconstructed_asm']['resident_driver_5CC6']
  with self.assertRaises(FormatError):self.typed(ledger=l)
 def test_stale_consumer_and_address_addend_reject(self):
  for mode in ['pin','addend']:
   f=self.f()
   if mode=='pin':f['definitions'][0]['evidence']['proof_sha256']='0'*64
   else:next(iter(f['bindings'].values()))['addend']=2
   with self.assertRaises(FormatError):self.typed(f)
 def test_original_missing_or_extra_relocation_rejects(self):
  for extra in [False,True]:
   m=copy.deepcopy(self.model);rs=m['relocations'];r=next(x for x in rs if x['source_hunk']==1 and x['source_offset']==0x292e)
   if extra:rs.append(dict(r,source_offset=0x2930))
   else:rs.remove(r)
   with self.assertRaises(FormatError):self.compare(model=m)
 def test_wrong_linked_pointer_payload_rejects(self):
  b=bytearray(self.files['p292e.exe']);h=next(h for h in parse(b)['hunks'] if h['number']==1);b[h['content_offset']+3]^=2
  with self.assertRaises(FormatError):self.compare(linked=bytes(b))
 def test_unknown_packed_index_literal_carrier_and_common_reject(self):
  for mode in ['index','literal','COMMON']:
   b=bytearray(self.files['p292e.o'])
   if mode=='index':b[39]=3
   elif mode=='literal':b[37]=0x13
   else:b[18:22]=(4).to_bytes(4,'big')
   with self.assertRaises(FormatError):self.compare(obj=bytes(b))
 def test_external_reference_count_and_symbol_order_reject(self):
  for mode in ['count','name']:
   b=bytearray(self.files['p292e.o']);p=b.index(b'\x07\x28')
   if mode=='count':b[p+5]+=1
   else:
    z=b.index(b'_recon_h00_5CD6',p);b[z:z+15]=b'_recon_h00_5CDE'
   with self.assertRaises(FormatError):self.compare(obj=bytes(b))
 def test_binder_extra_code_or_changed_symbol_reject(self):
  names=ptr.binder_names([self.fact]);b=bytearray(self.files['bindptr.o']);b[38]^=4
  with self.assertRaises(FormatError):ptr.binder_object(bytes(b),names)
  with self.assertRaises(FormatError):ptr.binder_object(self.files['bindptr.o'],names[:-1])
 def test_wrong_hunk_and_hidden_section_reject(self):
  for mode in ['hunk','section']:
   f=self.f()
   if mode=='hunk':next(iter(f['bindings'].values()))['hunk']=1
   else:f['object_sections']['BSS']=2
   with self.assertRaises(FormatError):dp.source(f)
 def test_new_pins_roundtrip_and_old_batch_unchanged(self):
  rows=[('evidence/data-providers/resident_data_292E.json',self.fact)];self.assertEqual(gen.pins(ROOT,rows,'tu-layout-g-001',['extprobe'],'evidence/data-providers/batch-0003.json'),self.recipe)
  manifest=dp.document(ROOT,'evidence/data-providers/batch-0002.json');rows=[(n,dp.document(ROOT,n)) for n in manifest['facts']];old=dp.document(ROOT,'evidence/data-providers/producer-0002.json');self.assertEqual(gen.pins(ROOT,rows,pathlib.Path(old['job']).name,['structprobe'],'evidence/data-providers/batch-0002.json'),old)
 def test_passing_regression_is_not_fabricated_by_compare(self):
  self.assertNotIn('regression',self.compare());self.assertEqual(self.compare()['zero_fill_credit'],0);self.assertFalse(self.compare()['root_layout_proof'])
 def test_all_existing_providers_still_rederive(self):
  rows=dp.load_data_providers(ROOT,self.blob,self.model,self.analysis,self.ledger,self.promotions);self.assertEqual({r['id'] for r in rows},set(self.ledger['data_providers']));self.assertGreaterEqual(sum(r['sections']['DATA'] for r in rows),540)

if __name__=='__main__':unittest.main()
