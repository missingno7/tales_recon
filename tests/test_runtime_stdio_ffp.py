"""Whole SDK stdio/FFP and untouched mixed-object dependency acceptance."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from names import to_mechanical
from analysis_support import ROOT,game
from census import advisory_image
from common import FormatError,sha256
from repo_paths import canonical_path
import runtime_stdio_ffp_members as e
import mixed_object_dependencies as d

class StdioFfpTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with advisory_image():cls.original=game()[:2]
  cls.doc=json.loads(canonical_path(ROOT,e.RECIPE).read_text());cls.ids=e.identities(ROOT,cls.doc,cls.original)
  cls.contexts={k:e.producer(ROOT,cls.doc,k) for k in ('stdio','ffp')}
  cls.report=e.verify(ROOT,document=cls.doc,original=cls.original)
 def test_six_complete_objects_and_zero_storage_credit(self):
  self.assertEqual(sum(r['size'] for r in self.report['contributions']),432)
  self.assertEqual([(r['member'],r['size']) for r in self.report['contributions']],[('putchar',22),('isatty',88),('unlink',36),('chkabort',48),('write',126),('ffp',112)])
  self.assertTrue(all(r['owned_data_size']==r['owned_bss_size']==0 for r in self.report['contributions']))
  self.assertEqual(self.contexts['ffp']['one-lib'],self.contexts['ffp']['one-source'])
  self.assertEqual(self.contexts['ffp']['two-lib'],self.contexts['ffp']['two-source'])
 def test_each_complete_member_in_two_data_orders(self):
  for spec in e.SPECS:
   key='ffp' if spec[0]=='ffp' else 'stdio';ids=copy.deepcopy(self.ids)
   ids['_Chk_Abort']=dict(original=(0,0x84da),basis='COMPLETE_CHKABORT')
   for prefix in (['one-lib','two-lib'] if key=='ffp' else ['stdio-one','stdio-two']):
    with self.subTest(member=spec[0],context=prefix):self.assertEqual(e.compare(self.contexts[key][prefix],self.original,spec,ids,object_size=spec[3])['size'],spec[3])
 def test_wrong_mathbase_and_each_stdio_global_reject(self):
  for spec,symbol in [(e.SPECS[-1],'_MathBase'),(e.SPECS[0],'_Cbuffs'),(e.SPECS[1],'__devtab'),(e.SPECS[1],'__numdev'),(e.SPECS[2],'_errno'),(e.SPECS[3],'_Enable_Abort')]:
   ids=copy.deepcopy(self.ids);ids[symbol]['original']=(1,ids[symbol]['original'][1]+2)
   c=self.contexts['ffp']['one-lib'] if spec[0]=='ffp' else self.contexts['stdio']['stdio-one']
   with self.subTest(symbol=symbol),self.assertRaises(FormatError):e.compare(c,self.original,spec,ids,object_size=spec[3])
 def test_masked_and_partial_members_reject(self):
  for spec in e.SPECS:
   c=self.contexts['ffp']['one-lib'] if spec[0]=='ffp' else self.contexts['stdio']['stdio-one']
   with self.subTest(member=spec[0]):
    with self.assertRaises(FormatError):e.compare(c,self.original,spec,self.ids,object_size=spec[3]-2)
    with self.assertRaises(FormatError):e.compare(c,self.original,spec,self.ids,object_size=spec[3],contract={})
 def test_unknown_private_binding_is_not_inferred(self):
  self.assertTrue(all(name not in self.ids for name in ('_cls_','__cln','Free')))
  self.assertTrue(all(r['member'] not in ('putc','malloc','getbuff','aputc') for r in self.report['contributions']))
 def test_ffp_following_zero_bytes_remain_unowned(self):
  spec=e.SPECS[-1];self.assertEqual(spec[2]+spec[3],0x8da2)
  self.assertEqual(e.n.extent(*self.original,0,0x8da2,2),b'\0\0')
 def test_missing_abort_target_rejects(self):
  ids=copy.deepcopy(self.ids);ids.pop('__abort')
  with self.assertRaises(FormatError):e.compare(self.contexts['ffp']['one-lib'],self.original,e.SPECS[-1],ids,object_size=112)
 def test_ordinary_literal_byte_change_rejects(self):
  b,m,sm=self.contexts['ffp']['one-lib'];out=bytearray(b);out[m['hunks'][0]['content_offset']+100]^=1
  with self.assertRaises(FormatError):e.compare((bytes(out),m,sm),self.original,e.SPECS[-1],self.ids,object_size=112)
 def test_wrong_callee_coordinate_rejects(self):
  ids=copy.deepcopy(self.ids);ids['__OpenLibrary']['original']=(0,0x89d0)
  with self.assertRaises(FormatError):e.compare(self.contexts['ffp']['one-lib'],self.original,e.SPECS[-1],ids,object_size=112)

class MixedDependencyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with advisory_image():cls.original=game()[:2]
  cls.recipe=d.recipe(ROOT)
  cls.work=ROOT/'build/worker-jobs/sol-glue-tail-mixed-11/sys/work'
  from compiler_oracle import extract
  cls.compiled=dict(identity=dict(mixed_object_dependencies=[cls.recipe],entry_function=d.ENTRY),directory=str(cls.work),prefix='t000',contribution=extract(cls.work,'t000',['candidate'],d.ENTRY,resident=True))
 def test_real_producer_links_unchanged_complete_mixed_object(self):
  job=json.loads((self.work.parent.parent/'result.json').read_text())
  self.assertTrue(job['all_steps_succeeded'])
  self.assertEqual(sha256((self.work/'t000_mixed8552.o').read_bytes()),self.recipe['object']['sha256'])
  result=d.validate_linked(self.compiled,original=self.original)
  self.assertTrue(any(s['name']=='_F_h00_8552' for s in result['contribution']['symbols']))
  self.assertTrue(any(s['name']=='_recovered' and s['offset']!=next(s['offset'] for s in result['contribution']['symbols'] if s['name']=='_F_h00_8552') for s in result['contribution']['symbols']))
  self.assertEqual(result['contribution']['code_hex'],self.compiled['contribution']['code_hex'])
 def test_staging_retains_object_bytes_exactly(self):
  with tempfile.TemporaryDirectory() as td:
   self.assertEqual(d.stage(dict(mixed_object_dependencies=[self.recipe]),Path(td),'t000'),['t000_mixed8552'])
   self.assertEqual((Path(td)/'t000_mixed8552.o').read_bytes(),canonical_path(ROOT,self.recipe['object']['path']).read_bytes())
 def test_recipe_rejects_uncanonical_or_changed_state(self):
  ledger=json.loads(canonical_path(ROOT,'recovery/ledger.json').read_text())
  ledger['mixed_source_objects'].pop(d.ID)
  with self.assertRaises(FormatError):d.recipe(ROOT,ledger)
  ledger=json.loads(canonical_path(ROOT,'recovery/ledger.json').read_text());ledger['mixed_source_objects'][d.ID]['state']='IDENTIFIED'
  with self.assertRaises(FormatError):d.recipe(ROOT,ledger)
 def test_interior_and_wrong_abi_calls_reject(self):
  for call in [dict(id=d.ID,hunk=0,offset=0x8554,basis='PC_RELATIVE'),dict(id=d.ID,hunk=0,offset=0x8552,basis='REGISTER_ABI')]:
   with self.assertRaises(FormatError):d.derive([dict(direct_callees=[call])])
 def test_inline_asm_stays_outside_ordinary_source_contract(self):
  from compiler_oracle import validate_source
  with self.assertRaises(FormatError):validate_source(to_mechanical(canonical_path(ROOT,self.recipe['source']['path']).read_text()))
 def test_trial_uses_header_and_ordinary_entry_rename(self):
  trial=dict(source='extern int F_h00_8552();\nrecovered(){return F_h00_8552();}\n',objects=[dict(source='extern int F_h00_8552();\nrecovered(){return F_h00_8552();}\n')],profile='aztec36',target_node=0)
  d.configure(trial,[self.recipe]);self.assertEqual(trial['entry_function'],'unit_entry');self.assertNotIn('#asm',trial['source']);self.assertIn('#define F_h00_8552 recovered',trial['objects'][0]['source'])
  self.assertEqual(trial['mixed_object_dependencies'][0]['storage_credit'],0)
 def test_retained_harness_source_replays_mechanical_entry_and_header(self):
  import recovery_evidence as r
  from compiler_oracle import harness
  source='extern int F_h00_8552();\nrecovered(code)\nint code;\n{return F_h00_8552(code);}\n'
  changed=source.replace('recovered','unit_entry')+'\n'+d.header()
  unit=dict(id='caller',ordered_members=[dict(id='caller',hunk=0,start=0x1,size=2)],mixed_object_dependencies=[self.recipe])
  compiler=dict(source_sha256=sha256(changed.encode('ascii')),harness_sha256=sha256(harness(changed,0,[d.NAME,'recovered'],entry_function=d.ENTRY).encode('ascii')),candidate_overlay_node=0,entry_function=d.ENTRY,local_functions=[d.NAME,'recovered'],mixed_object_dependencies=[self.recipe])
  self.assertEqual(r.compiled_unit_source_sha256(unit,source,compiler),compiler['source_sha256'])
  r.unit_export_evidence(unit,source,compiler,*self.original,functions=[dict(id='caller',direct_callees=[dict(id=d.ID,hunk=0,offset=0x8552,basis='PC_RELATIVE')])])
 def test_partial_or_changed_dependency_recipe_rejects(self):
  trial=dict(source='recovered(){return 0;}',objects=[dict(source='recovered(){return 0;}')],profile='aztec36',target_node=0)
  for key,value in [('size',236),('symbol','_F_h00_8552'),('storage_credit',4)]:
   bad=copy.deepcopy(self.recipe);bad[key]=value
   with self.subTest(key=key),self.assertRaises(FormatError):d.configure(copy.deepcopy(trial),[bad])
 def test_linked_ordinary_and_address_corruption_reject(self):
  for offset in (0,92):
   b,m=self.original;out=bytearray(b);out[m['hunks'][0]['content_offset']+0x8552+offset]^=1
   with self.subTest(offset=offset),self.assertRaises(FormatError):d.validate_linked(self.compiled,original=(bytes(out),m))
 def test_dependency_boundary_cannot_absorb_or_clip_objects(self):
  bad=copy.deepcopy(self.compiled);bad['contribution']['resident_bounds']['end']+=2
  with self.assertRaises(FormatError):d.validate_linked(bad,original=self.original)

if __name__=='__main__':unittest.main()
