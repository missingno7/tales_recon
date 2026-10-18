import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from names import to_mechanical
from common import FormatError,sha256,json_bytes
import dead_code_promotion as promote
from recovery_state import canonical_state

class CompleteCPromotionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.ledger=self.root/'recovery/ledger.json';self.ledger.parent.mkdir()
  self.original=dict(schema_version=1,functions={'ordinary':dict(source='src/old.c',source_sha256='old')},mixed_source_objects={'mixed':dict(source='src/mixed.c')},data_providers={'provider':dict(source='src/data.c')},attempts={},blockers={})
  self.ledger.write_bytes(json_bytes(self.original));self.source=b'void recovered(){}\n'
  self.proof=dict(id='ov03_F_0000',kind='EXACT_C_OBJECT_WITH_DEAD_CODE',state='FUNCTION_CODE_MATCH',source='src/recovered/complete-c/ov03_F_0000.c',source_sha256=sha256(self.source),source_acceptance=True,extent_basis=promote.BASIS,regression_provenance=dict(passed=True))
 def tearDown(self):self.tmp.cleanup()
 def test_atomic_map_preserves_ordinary_sources_and_mixed_proofs(self):
  item=promote.commit(self.root,self.proof['id'],self.source,self.proof,canonical_state(self.original))
  current=json.loads(self.ledger.read_bytes());self.assertEqual(current['functions'],self.original['functions']);self.assertEqual(current['mixed_source_objects'],self.original['mixed_source_objects'])
  self.assertEqual(current['data_providers'],self.original['data_providers'])
  self.assertEqual(current[promote.MAP][self.proof['id']],item)
  self.assertEqual(to_mechanical((self.root/item['source']).read_bytes()),self.source);self.assertEqual(sha256((self.root/item['proof']).read_bytes()),item['proof_sha256'])
  self.assertIn(promote.MAP,canonical_state(current))
 def test_raced_canonical_state_rejected_before_source_write(self):
  state=copy.deepcopy(self.original);state['functions']['ordinary']['source_sha256']='changed';self.ledger.write_bytes(json_bytes(state))
  with self.assertRaisesRegex(FormatError,'inputs changed'):promote.commit(self.root,self.proof['id'],self.source,self.proof,canonical_state(self.original))
  self.assertFalse((self.root/self.proof['source']).exists());self.assertEqual(json.loads(self.ledger.read_bytes()),state)
 def test_input_guard_failure_leaves_state_intact(self):
  def reject():raise FormatError('changed input')
  with self.assertRaisesRegex(FormatError,'changed input'):promote.commit(self.root,self.proof['id'],self.source,self.proof,canonical_state(self.original),reject)
  self.assertEqual(self.ledger.read_bytes(),json_bytes(self.original));self.assertFalse((self.root/self.proof['source']).exists())
 def test_failed_publish_rolls_back_all_three_files(self):
  real=promote.write_json
  def failing(path,doc):
   if path==self.ledger:raise OSError('synthetic ledger failure')
   return real(path,doc)
  with patch.object(promote,'write_json',side_effect=failing):
   with self.assertRaisesRegex(OSError,'ledger failure'):promote.commit(self.root,self.proof['id'],self.source,self.proof,canonical_state(self.original))
  self.assertEqual(self.ledger.read_bytes(),json_bytes(self.original));self.assertFalse((self.root/self.proof['source']).exists());self.assertFalse((self.root/'recovery/proofs/complete-c/ov03_F_0000.json').exists())
 def test_existing_unregistered_source_is_preserved(self):
  source=self.root/self.proof['source'];source.parent.mkdir(parents=True);source.write_bytes(b'other C source')
  with self.assertRaisesRegex(FormatError,'another source'):promote.commit(self.root,self.proof['id'],self.source,self.proof,canonical_state(self.original))
  self.assertEqual(source.read_bytes(),b'other C source')
 def test_deduplicates_only_same_owner_prefix(self):
  row=dict(id='ov11_F_66FE',complete_extent=dict(hunk=11,start=0x66FE,end=0x67B0,size=178),owned_literal_end=0x67B0)
  ordinary=[dict(id=row['id'],hunk=11,start=0x66FE,end=0x673E)]
  self.assertEqual(promote.coverage(row,ordinary),[(0x673E,0x67B0)])
  ordinary[0]['id']='other'
  with self.assertRaisesRegex(FormatError,'foreign canonical'):promote.coverage(row,ordinary)
 def test_cli_requires_explicit_mode_and_isolated_preview_cannot_promote(self):
  with patch.object(sys,'argv',['dead_code_promotion.py','ov03_F_0000']),patch.object(promote,'run') as call:
   with self.assertRaises(SystemExit):promote.main()
   call.assert_not_called()
  with patch.object(sys,'argv',['dead_code_promotion.py','ov03_F_0000','--isolated']),patch.object(promote,'run',return_value={'verdict':'EQUAL'}) as call:
   promote.main();self.assertFalse(call.call_args.kwargs['promote'])
 def test_pending_fact_and_cached_false_pass_are_not_canonical_acceptance(self):
  with patch.object(promote.dead,'verified_admissions',return_value=[]),patch.object(promote,'records',return_value={}):
   self.assertEqual(promote.canonical_rows(self.root,b'',{},dict(functions=[]),dict(functions={})),[])
   with self.assertRaisesRegex(FormatError,'admission missing'):promote.canonical_rows(self.root,b'',{},dict(functions=[]),dict(functions={},dead_code_functions={'ov03_F_0000':dict(state='FUNCTION_CODE_MATCH')}))

 def test_real_canonical_proof_and_compiler_projection(self):
  from analysis_support import ROOT,game
  from recovery_state import evidence,recovery
  from recovery_evidence import load_promotions
  blob,model,_=game();analysis=evidence();state=recovery()
  verified=promote.dead.verified_admissions(ROOT,blob,model,analysis)
  row=next(r for r in verified if r['id']=='ov13_F_0942');record=promote.records(ROOT)[row['id']]
  proof=promote.proof_for(ROOT,blob,model,analysis,row,record);proof['regression_provenance']=dict(passed=True)
  source=self.root/'candidate.c';source.write_bytes((ROOT/record['source']['path']).read_bytes())
  receipt=self.root/'proof.json';receipt.write_bytes(json_bytes(proof))
  item=dict(state=proof['state'],source=proof['source'],source_sha256=sha256(source.read_bytes()),proof='recovery/proofs/complete-c/'+row['id']+'.json',proof_sha256=sha256(receipt.read_bytes()))
  hypothetical=copy.deepcopy(state);hypothetical[promote.MAP]={row['id']:item}
  real_path=promote.canonical_path
  def resolve(root,name):
   if name==item['source']:return source
   if name==item['proof']:return receipt
   return real_path(root,name)
  # Exact replay above uses the real unchanged producing inputs; these local
  # files model only the future destination, without promoting this repository.
  with patch.object(promote.dead,'verified_admissions',return_value=verified),patch.object(promote,'canonical_path',side_effect=resolve), \
       patch.object(promote,'read_source',side_effect=lambda root,ref,**kwargs: to_mechanical(source.read_bytes())):
   accepted=promote.canonical_rows(ROOT,blob,model,analysis,hypothetical)
   self.assertTrue(next(r for r in accepted if r['id']==row['id'])['source_acceptance'])
   source.write_bytes(source.read_bytes()+b' ')
   with self.assertRaisesRegex(FormatError,'source changed'):promote.canonical_rows(ROOT,blob,model,analysis,hypothetical)
  # Normalize only actual compiler output. The ordinary 64-byte prefix is
  # independently accepted and must never be credited a second time.
  accepted=[dict(r,acceptance=True) for r in verified]
  ordinary=load_promotions(ROOT,blob,model,analysis)
  projected=dict(state,**{promote.MAP:{r['id']:{} for r in accepted}})
  with patch.object(promote,'canonical_rows',return_value=accepted):parts=promote.accepted_contributions(ROOT,blob,model,analysis,ordinary,projected)
  self.assertEqual(sum(len(p['bytes']) for p in parts if p['category']=='RECOVERED_C'),1490)
  self.assertEqual(sum(len(p['bytes']) for p in parts if p['category']=='COMPILER_OWNED_DATA'),220)
  for part in parts:
   h=next(h for h in model['hunks'] if h['number']==part['hunk']);expected=blob[h['content_offset']+part['start']:h['content_offset']+part['end']]
   self.assertEqual(part['bytes'],expected)
  self.assertEqual(state['functions'],recovery()['functions'])

if __name__=='__main__':unittest.main()
