"""Content-addressed replay, explicit ledger scoping and fail-closed ownership."""
import copy,json,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from unittest.mock import patch
import dead_code_extents as dead
from common import FormatError,sha256
from evidence_snapshot import memoized,_PROCESS

class ReplayMemoTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);_PROCESS.clear()
 def tearDown(self):self.tmp.cleanup();_PROCESS.clear()
 def test_process_memo_is_detached_bounded_and_never_caches_failures(self):
  calls=[]
  def load():calls.append(1);return dict(items=[])
  first=memoized(self.root,'test','a',load,process_cache=True);first['items'].append(7)
  self.assertEqual(memoized(self.root,'test','a',load,process_cache=True),dict(items=[]));self.assertEqual(len(calls),1)
  memoized(self.root,'test','b',load,process_cache=True);self.assertEqual(len(calls),2)
  def reject():raise FormatError('comparison failed')
  for _ in range(2):
   with self.assertRaises(FormatError):memoized(self.root,'bad','x',reject,process_cache=True)
  self.assertFalse(any(k[2]=='bad' for k in _PROCESS))
  for n in range(30):memoized(self.root,'test',str(n),load,process_cache=True)
  self.assertLessEqual(len(_PROCESS),16)
 def fixture(self):
  directory=self.root/'evidence/rules/dead-code-extents';directory.mkdir(parents=True)
  files={n:directory/n for n in ['source.c','receipt.json','compiler.json','part.o','entries.json']}
  for n,p in files.items():p.write_bytes(b'{}' if n.endswith('.json') else b'independent test input')
  files['compiler.json'].write_text(json.dumps(dict(artifacts=[dict(path='part.o',sha256=sha256(files['part.o'].read_bytes()))])))
  def spec(n):return dict(path=files[n].relative_to(self.root).as_posix(),sha256=sha256(files[n].read_bytes()))
  row=dict(id='ov03_F_0000',unit_entry='ov03_F_0000',source=spec('source.c'),entry_source=spec('source.c'),receipt=spec('receipt.json'),compiler=spec('compiler.json'),member_sources={})
  (self.root/dead.ADMISSIONS).write_text(json.dumps(dict(schema_version=1,admissions=[row])))
  return row,files
 def test_complete_identity_changes_for_every_kind_of_input(self):
  row,files=self.fixture();analysis=dict(functions=[]);ledger=dict(functions={});blob=b'oracle';model={}
  key=lambda:dead.replay_identity(self.root,blob,model,analysis,ledger,row)
  before=key()
  for name,path in files.items():
   old=path.read_bytes();path.write_bytes(old+b' ')
   self.assertNotEqual(key(),before,name);path.write_bytes(old)
  tools=self.root/'tools';tools.mkdir();helper=tools/'function_compare.py';helper.write_bytes(b'helper')
  a=key();helper.write_bytes(b'change');self.assertNotEqual(key(),a)
  old=key();blob+=b'changed';self.assertNotEqual(key(),old)
  old=key();ledger['functions']['new']=dict(source_sha256='changed');self.assertNotEqual(key(),old)
  old=key();analysis['foreign_reference']=7;self.assertNotEqual(key(),old)
  old=key();row['unit_entry']='changed';self.assertNotEqual(key(),old)
 def test_stale_noncanonical_is_reported_but_canonical_raises(self):
  row,_=self.fixture()
  with patch.object(dead,'_verify_admission',side_effect=FormatError('dead-code canonical dependencies changed')):
   state=dict(functions={})
   got=dead.verified_admissions(self.root,b'oracle',{},dict(functions=[]),state,report_stale=True)
   self.assertEqual(got[0]['status'],'STALE_ADMISSION');self.assertFalse(got[0]['source_acceptance'])
   state['dead_code_functions']={row['id']:dict()}
   with self.assertRaisesRegex(FormatError,'dependencies changed'):dead.verified_admissions(self.root,b'oracle',{},dict(functions=[]),state,report_stale=True)
 def test_dependency_check_uses_supplied_ledger_before_exact_comparison(self):
  row,files=self.fixture();raw=files['source.c'].read_bytes()
  receipt=dict(verdict='EQUAL',id=row['id'],unclaimed_bytes=0,source_sha256=sha256(raw),dependency_sources={'dependency':'current'})
  files['receipt.json'].write_text(json.dumps(receipt));row['receipt']['sha256']=sha256(files['receipt.json'].read_bytes())
  analysis=dict(functions=[dict(id=row['id'])]);state=dict(functions={'dependency':dict(source_sha256='other')})
  with patch.object(dead,'make_view',return_value={}),patch.object(dead,'admission_boundary'),patch('recovery_state.recovery',side_effect=AssertionError('global ledger read')):
   with self.assertRaisesRegex(FormatError,'canonical dependencies changed'):dead._verify_admission(self.root,b'oracle',{},analysis,state,row)
   state['functions']['dependency']['source_sha256']='current'
   with self.assertRaisesRegex(FormatError,'verifier provenance'):dead._verify_admission(self.root,b'oracle',{},analysis,state,row)
 def test_stale_malformed_producer_remains_visible_to_snapshot(self):
  row,files=self.fixture();files['compiler.json'].write_bytes(b'not-json')
  names=dead.inputs(self.root)
  self.assertIn(row['compiler']['path'],names)
  rows=dead.verified_admissions(self.root,b'oracle',{},dict(functions=[]),dict(functions={}),report_stale=True)
  self.assertEqual(rows[0]['status'],'STALE_ADMISSION');self.assertFalse(rows[0]['source_acceptance'])
 def test_image_only_harness_controls_do_not_load_canonical_proofs(self):
  import check_unit,census
  from analysis_support import game
  from evidence_snapshot import snapshot
  from unittest.mock import patch
  with snapshot(),patch.object(census,'load_promotions',side_effect=AssertionError('strict canonical read')):
   # A synthetic unit has no exports in the real immutable image.
   self.assertIsNone(check_unit.unit_export_roots([dict(id='ov09_F_0100',hunk=9,start=256)],{'ov09_F_0100':'recovered'},'ov09_F_0100'))
   # That advisory read must never satisfy an actual strict image request.
   with self.assertRaisesRegex(AssertionError,'strict canonical read'):game()
 def test_mutation_during_replay_never_publishes_a_memo(self):
  row,files=self.fixture()
  def changed(*args):
   files['part.o'].write_bytes(b'changed while comparing');return dict(id=row['id'])
  with patch.object(dead,'_verify_admission',side_effect=changed):
   with self.assertRaisesRegex(FormatError,'inputs changed during verification'):
    dead.verified_admissions(self.root,b'oracle',{},dict(functions=[]),dict(functions={}))
  self.assertFalse(any(k[2]=='exact-dead-code:'+row['id'] for k in _PROCESS))
 def test_cfg_refresh_cannot_supply_a_strict_data_proof_view(self):
  import census
  from analysis_support import game
  from evidence_snapshot import snapshot
  with snapshot(),patch('data_providers.load_data_providers',side_effect=FormatError('strict DATA replay')):
   with dead.analysis_refresh():game()
   with self.assertRaisesRegex(FormatError,'strict DATA replay'):game()
 def test_real_complete_replay_reads_only_fingerprinted_inputs(self):
  from analysis_support import ROOT,game
  from census import advisory_image
  from recovery_state import evidence
  with advisory_image():blob,model,_=game()
  analysis=evidence();analysis['replay_io_audit']=True
  state=json.loads((ROOT/'recovery/ledger.json').read_bytes());expected={}
  dead.replay_identity(ROOT,blob,model,analysis,state,None,input_files=expected)
  observed=set();original_open=Path.open;verify=dead._verify_admission
  def audited(*args):
   def opened(path,*a,**kw):
    mode=a[0] if a else kw.get('mode','r')
    if 'r' in mode:observed.add(str(path.resolve()))
    return original_open(path,*a,**kw)
   with patch.object(Path,'open',opened):return verify(*args)
  with patch.object(dead,'_verify_admission',side_effect=audited):rows=dead.verified_admissions(ROOT,blob,model,analysis,state)
  self.assertEqual({r['status'] for r in rows},{'VERIFIED_COMPLETE_C_SOURCE_OBJECT'})
  self.assertTrue(observed);self.assertEqual(observed-set(expected),set())
 def test_canonical_dependency_and_partition_cache_changes_miss(self):
  import compiler_oracle
  from analysis_support import ROOT
  row,files=self.fixture()
  receipt=json.loads(files['receipt.json'].read_bytes());receipt['dependency_sources']={'dep':'metadata'};files['receipt.json'].write_text(json.dumps(receipt))
  source=self.root/'dep.c';source.write_bytes(b'canonical source')
  proof=self.root/'proof.json';proof.write_text(json.dumps(dict(comparison=dict(complete_unit_receipt='unit/receipt.json'))))
  unit=self.root/'unit';unit.mkdir();(unit/'unit.c').write_bytes(b'unit source')
  key='a'*64;(unit/'receipt.json').write_text(json.dumps(dict(cache_key=key,ordered_members=[])))
  state=dict(functions={'dep':dict(source='dep.c',proof='proof.json',source_sha256='metadata')})
  with tempfile.TemporaryDirectory(dir=ROOT/'build') as cache_dir,patch.object(compiler_oracle,'CACHE',Path(cache_dir)):
   cache=Path(cache_dir)/key;cache.mkdir();artifact=cache/'part.o';artifact.write_bytes(b'object')
   (cache/'receipt.json').write_text(json.dumps(dict(artifacts=[dict(path='part.o')])) )
   identity=lambda:dead.replay_identity(self.root,b'oracle',{},dict(functions=[]),state,row)
   before=identity()
   for path in [source,proof,unit/'unit.c',artifact,cache/'receipt.json']:
    old=path.read_bytes();path.write_bytes(old+b' ')
    self.assertNotEqual(identity(),before,str(path));path.write_bytes(old)
 def test_nested_derivations_share_hashes_but_outer_exit_checks_mutation(self):
  from evidence_snapshot import snapshot
  version=[0]
  for mutate in [False,True]:
   version[0]=0
   with snapshot() as active,patch.object(active,'inputs',side_effect=lambda *a:{'input':version[0]}) as scans:
    def child():
     if mutate:version[0]=1
     return dict(value=7)
    def outer():return memoized(self.root,'child','inner',child)
    if mutate:
     with self.assertRaisesRegex(FormatError,'inputs changed during snapshot'):memoized(self.root,'parent','outer',outer)
     self.assertFalse(active.entries)
    else:self.assertEqual(memoized(self.root,'parent','outer',outer),dict(value=7))
    self.assertEqual(scans.call_count,2)
 def test_replay_scope_restores_root_ledger_analysis_and_image(self):
  from recovery_state import recovery
  state=dict(functions={});analysis=dict(functions=[])
  with dead.isolated_view('entry',analysis,(b'oracle',{},None),dict(root=self.root,ledger=state)):
   self.assertEqual(dead.replay_root(None),self.root);self.assertIs(recovery(),state)
  self.assertIsNone(dead.replay_root(None));self.assertIsNone(dead.current_analysis());self.assertIsNone(dead.current_image())



class ContentScanTests(unittest.TestCase):
 def test_every_scan_rehashes_files_and_keeps_scratch_explicit(self):
  from replay_inputs import ContentScan
  with tempfile.TemporaryDirectory() as name:
   root=Path(name);file=root/'source.c';file.write_bytes(b'first')
   a=ContentScan(root);a.read(file);file.write_bytes(b'other')
   b=ContentScan(root);b.read(file);self.assertNotEqual(a.values,b.values)
   build=root/'build';build.mkdir();output=build/'part.o';output.write_bytes(b'artifact')
   with self.assertRaises(FormatError):ContentScan(root).read(output)
   self.assertEqual(ContentScan(root).read(output,scratch=True),b'artifact')
   quarantine=root/'to_delete';quarantine.mkdir();bad=quarantine/'source.c';bad.write_bytes(b'rejected')
   with self.assertRaises(FormatError):ContentScan(root).read(bad,scratch=True)
 def test_directory_junction_retarget_cannot_reuse_a_content_identity(self):
  import os,subprocess
  from replay_inputs import ContentScan
  with tempfile.TemporaryDirectory() as name:
   outer=Path(name);root=outer/'repo';root.mkdir();inside=root/'inside';inside.mkdir();outside=outer/'foreign';outside.mkdir()
   (inside/'source.c').write_bytes(b'input');(outside/'source.c').write_bytes(b'input')
   link=root/'entry'
   def connect(target):
    result=subprocess.run(['cmd','/c','mklink','/J',str(link).replace('/','\\'),str(target).replace('/','\\')],capture_output=True)
    if result.returncode:self.skipTest('directory junction creation unavailable')
   connect(inside);ContentScan(root).read(link/'source.c');os.rmdir(link)
   connect(outside)
   try:
    with self.assertRaises(FormatError):ContentScan(root).read(link/'source.c')
   finally:os.rmdir(link)

class RebasedRoutesTests(unittest.TestCase):
 def test_staged_admissions_never_enter_empty_canonical_accounting(self):
  import dead_code_promotion as promotion
  with patch.object(promotion,'canonical_rows',side_effect=AssertionError('staged replay has no accounting authority')):
   self.assertEqual(promotion.accepted_contributions(Path('.'),b'',{}, {},[],dict(functions={})),[])
 def test_glue_entry_guidance_uses_the_ledger_validation_root(self):
  from recovery_state import runtime_dependencies
  with tempfile.TemporaryDirectory() as name:
   root=Path(name);p=root/'evidence/experiments/runtime-arithmetic.json';p.parent.mkdir(parents=True)
   p.write_text(json.dumps(dict(game_sha256='fixture',status='COMPLETE_RUNTIME_CODE_MATCH',contributions=[])))
   route={(0,123):dict(kind='LIBRARY_MEMBER',symbol='__fixture')}
   with dead.isolated_view('entry',context=dict(root=root,ledger=dict(functions={}))):
    with patch('runtime_entry_routes.load',return_value=route) as load:
     self.assertEqual(runtime_dependencies(dict(game_sha256='fixture')),route)
     load.assert_called_once_with(root,'fixture')
 def test_canonical_transaction_retains_both_source_ownership_routes(self):
  from recovery_state import canonical_state
  value=dict(functions={},dead_code_functions={'dead':dict(source='complete.c')},reconstructed_asm={'asm':dict(source='nonc.s')})
  result=canonical_state(value)
  self.assertEqual(result['dead_code_functions'],value['dead_code_functions'])
  self.assertEqual(result['reconstructed_asm'],value['reconstructed_asm'])

if __name__=='__main__':unittest.main()
