import copy,json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
from common import FormatError,json_bytes
from analysis_support import ROOT,game
from evidence_snapshot import isolated_verification
from recovery_evidence import load_promotions
import data_providers as dp
import data_provider_job as gen

HERE=pathlib.Path(__file__).resolve().parents[1]

class ProviderExtensions(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.manifest=json.loads((HERE/'evidence/data-providers/batch-0002.json').read_bytes());cls.facts=[json.loads((HERE/n).read_bytes()) for n in cls.manifest['facts']]
  cls.recipe=json.loads((HERE/'evidence/data-providers/producer-0002.json').read_bytes());job=ROOT/cls.recipe['job']/'sys/work';cls.files={n:(job/n).read_bytes() for n in cls.recipe['artifacts']}
  with isolated_verification(ROOT):
   cls.blob,cls.model,_=game();cls.analysis=dp.document(ROOT,'evidence/functions/ledger.json');cls.ledger=dp.document(ROOT,'recovery/ledger.json');cls.promotions=load_promotions(ROOT,cls.blob,cls.model,cls.analysis)
 def fact(self,ident):return copy.deepcopy(next(f for f in self.facts if f['id'].endswith(ident)))
 def typed(self,f,analysis=None,types=None):
  if types is None:return dp.typed_evidence(ROOT,f,analysis or self.analysis,self.ledger,self.promotions)
  real=dp.document
  with patch.object(dp,'document',lambda r,p:types if p=='evidence/types.json' else real(r,p)):return dp.typed_evidence(ROOT,f,analysis or self.analysis,self.ledger,self.promotions)
 def compare(self,f=None,linked=None):
  f=f or self.fact('12B4');p=f['producer']['prefix'];return dp.compare_data(self.blob,self.model,f,self.files[p+'.o'],linked or self.files[p+'.exe'],self.files[p+'.sym'].decode())
 def test_complete_new_batch_exact(self):
  self.assertEqual(sum(f['original']['size'] for f in self.facts),220)
  for f in self.facts:
   r=self.compare(f);self.assertEqual(r['verdict'],'EQUAL_CANDIDATE');self.assertEqual(r['original_relocations'],[]);self.assertTrue(self.typed(f))
 def test_struct_fields_source_and_ABI(self):
  f=self.fact('12B4');text=dp.source(f).decode();self.assertIn('unsigned char kind; unsigned char active; int pos; int t;',text)
  self.assertEqual([d['offset'] for d in f['definitions']],[0,6]);self.assertEqual(self.compare(f)['sections'],dict(CODE=0,DATA=12,BSS=0,COMMON=0))
 def test_struct_wrong_offset_order_width_rejected(self):
  for change in ['offset','order','width']:
   f=self.fact('12B4');fs=f['definitions'][0]['fields']
   if change=='offset':fs[2]['offset']=4
   elif change=='order':fs[0],fs[1]=fs[1],fs[0]
   else:fs[2]['type']='long'
   with self.assertRaises(FormatError):self.typed(f)
 def test_opaque_struct_array_filler_rejected(self):
  for ty,name in [('char[4]','rest'),('int','padding'),('unsigned char','unused')]:
   f=self.fact('12B4');f['definitions'][0]['fields'][2].update(type=ty,name=name)
   with self.assertRaises(FormatError):dp.source(f)
 def test_guessed_extra_struct_extent_rejected(self):
  f=self.fact('12B4');f['original']['size']+=2;f['object_sections']['DATA']+=2
  with self.assertRaises(FormatError):dp.shape(f)
 def test_changed_typed_struct_constant_rejected(self):
  f=self.fact('12B4');f['definitions'][0]['initializer'][0]=8
  with self.assertRaises(FormatError):self.compare(f)
 def test_field_from_other_Entry_rejected(self):
  f=self.fact('12B4');e=f['definitions'][0]['evidence'];e['block_end']=20000;e['field_accesses'][0]=f['definitions'][1]['evidence']['field_accesses'][0]
  with self.assertRaisesRegex(FormatError,'Entry pointer changed'):self.typed(f)
 def test_padded_struct_positive_control(self):
  f=dp.struct_control_fact();b=self.files['structprobe.exe'];m=dp.parse(b)
  r=dp.compare_data(b,m,f,self.files['structprobe.o'],b,self.files['structprobe.sym'].decode());self.assertEqual(r['sections']['DATA'],10)
  self.assertEqual(dp.data_object(self.files['structprobe.o'])['bytes'],bytes.fromhex('070012345678ff000017'))
 def test_changed_natural_padding_rejected(self):
  f=dp.struct_control_fact();b=bytearray(self.files['structprobe.exe']);m=dp.parse(b);h=m['hunks'][1];b[h['content_offset']+1]=9
  with self.assertRaises(FormatError):dp.compare_data(bytes(b),m,f,self.files['structprobe.o'],bytes(b),self.files['structprobe.sym'].decode())
 def test_keyboard_guard_count_and_signed_type(self):
  f=self.fact('1EA4');r=self.typed(f)[0];self.assertEqual(r['details']['index_domain'],[1,111]);self.assertEqual(f['definitions'][0]['count'],112)
  for count in [110,114,128]:
   g=copy.deepcopy(f);d=g['definitions'][0];d['count']=count;d['initializer']=[0]*count;d['bounds']['bytes']=count;g['original']['size']=count;g['object_sections']['DATA']=count
   with self.assertRaises(FormatError):self.typed(g)
 def test_guard_branch_changed_rejected(self):
  f=self.fact('1EA4');a=copy.deepcopy(self.analysis);fn=next(x for x in a['functions'] if x['id']=='resident_F_4F62');next(i for i in fn['instructions'] if i['offset']==20484)['mnemonic']='blt.b'
  with self.assertRaises(FormatError):self.typed(f,a)
 def test_coordinate_mask_changed_rejected(self):
  f=self.fact('0AA2');a=copy.deepcopy(self.analysis);fn=next(x for x in a['functions'] if x['id']=='ov08_F_0000');next(i for i in fn['instructions'] if i['offset']==2322)['operands']='#$1f, -$64(a5)'
  with self.assertRaises(FormatError):self.typed(f,a)
 def test_state_helper_anchor_required(self):
  f=self.fact('0A3A');f['definitions'][0]['evidence']['anchors'].pop()
  with self.assertRaises(FormatError):self.typed(f)
 def test_state_byte_alias_write_rejected(self):
  f=self.fact('0A3A');t=copy.deepcopy(dp.document(ROOT,'evidence/types.json'));g=next(g for g in t['globals'] if g['data_hunk_offset']==0x5E41);g['accesses'][0]['direction']='WRITE'
  with self.assertRaisesRegex(FormatError,'overlapping state write'):self.typed(f,types=t)
 def test_new_unowned_state_writer_rejected(self):
  f=self.fact('0A3A');t=copy.deepcopy(dp.document(ROOT,'evidence/types.json'));g=next(g for g in t['globals'] if g['data_hunk_offset']==0x5E40);g['accesses'].append(dict(g['accesses'][0],function='resident_F_UNKNOWN'))
  with self.assertRaises(FormatError):self.typed(f,types=t)
 def test_new_absolute_alias_rejected(self):
  f=self.fact('0A3A');a=copy.deepcopy(self.analysis);next(x for x in a['functions'] if x['id']=='ov05_F_0000')['relocations'].append(dict(target_hunk=1,addend_raw=0xA3B,source_offset=0))
  with self.assertRaises(FormatError):self.typed(f,a)
 def test_new_batch_pins_regenerate_without_old_recipe_rewrite(self):
  rows=list(zip(self.manifest['facts'],self.facts));self.assertEqual(gen.pins(ROOT,rows,'tu-layout-e-001',['structprobe'],'evidence/data-providers/batch-0002.json'),self.recipe)
  self.assertNotEqual(self.recipe['job'],dp.document(ROOT,'evidence/data-providers/producer.json')['job'])
 def test_new_manifest_snapshot_without_ledger(self):
  base=HERE/'build/workers/sol-tu-layout/extensions-tests';base.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=base) as temporary:
   root=pathlib.Path(temporary);folder=root/'evidence/data-providers';folder.mkdir(parents=True)
   (folder/'batch-0002.json').write_bytes(json_bytes(dict(facts=['evidence/data-providers/f.json'])))
   (folder/'f.json').write_bytes(json_bytes(dict(producer=dict(batch='evidence/data-providers/p.json'))))
   recipe=dict(job='build/worker-jobs/tu-layout-fixture',artifacts={'x.o':'0'*64},toolchain_inventory_sha256={});(folder/'p.json').write_bytes(json_bytes(recipe))
   before=dp.input_identity(root);target=root/recipe['job']/'sys/work/x.o';target.parent.mkdir(parents=True);target.write_bytes(b'changed')
   after=dp.input_identity(root);self.assertNotEqual(before,after);self.assertIn(str(target.resolve()),after)
 def test_accepted_five_providers_still_rederive(self):
  with isolated_verification(ROOT):rows=dp.load_data_providers(ROOT,self.blob,self.model,self.analysis,self.ledger,self.promotions)
  required={dp.document(ROOT,n)['id'] for n in dp.document(ROOT,'evidence/data-providers/batch.json')['facts']}
  self.assertEqual({r['id'] for r in rows},set(self.ledger.get('data_providers',{})))
  retained=[r for r in rows if r['id'] in required]
  self.assertEqual({r['id'] for r in retained},required);self.assertEqual(sum(r['original']['size'] for r in retained),320)

if __name__=='__main__':unittest.main()
