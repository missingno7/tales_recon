import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError,sha256
from function_census import Census
import dead_code_extents as dead
R=bytes.fromhex('4e5500004e5d4e75')
class DeadCodeTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'tools').mkdir();(self.root/'tools/dead_code_extents.py').write_bytes(b'synthetic-validator')
 def tearDown(self):self.tmp.cleanup()
 def fixture(self,after_return=False):
  data=(R+bytes.fromhex('303c000760f6') if after_return else bytes.fromhex('4e55000060044e714e714e5d4e75'))+R
  model=dict(hunks=[dict(number=3,node='ov03',type='CODE',content_offset=0,initialized_size=len(data))],relocations=[],overlay=None)
  c=Census(data,model,[]);c.seed(3,0,dict(kind='OVERLAY_EXPORT',slot=1));c.seed(3,14,dict(kind='OVERLAY_EXPORT',slot=1));ledger=c.run();base=next(f for f in ledger['functions'] if f['start']==0)
  row=dict(id=base['id'],hunk=3,start=0,code_end=14,contribution_end=14,dead_spans=[[8,14] if after_return else [6,10]],next_entry='ov03_F_000E',justification='Synthetic bounded unreachable instructions.',admission=None)
  self.write(data,row);return base,ledger,data,model,row
 def write(self,blob,row):
  p=self.root/dead.INPUT;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(dict(schema_version=1,game_sha256=sha256(blob),source_acceptance=False,entries=[row])))
 def view(self,x):return dead.make_view(*x[:4],self.root)
 def test_internal_hole_and_after_return_tail(self):
  for tail in [False,True]:
   x=self.fixture(tail);f=self.view(x);self.assertEqual(f['extent_status'],dead.STATUS);self.assertEqual(f['size'],14);self.assertFalse(f['dead_code_extent']['source_acceptance']);self.assertEqual(f['dead_code_extent']['reachable_extent']['size'],x[0]['size'])
 def test_pending_is_not_normal_view_or_admission(self):
  x=self.fixture();self.assertIs(dead.selected_view(*x[:4],self.root),x[0]);self.assertFalse(dead.comparison_allowed(self.view(x)));self.assertEqual(dead.verified_admissions(self.root,x[2],x[3],x[1]),[])
 def test_scope_is_explicit_and_restored(self):
  x=self.fixture()
  with dead.isolated_view(x[0]['id']):self.assertEqual(dead.selected_view(*x[:4],self.root)['extent_status'],dead.STATUS)
  self.assertIs(dead.selected_view(*x[:4],self.root),x[0])
 def test_invalid_bounds_and_unreachable_partition(self):
  for key,value in [('start',True),('code_end',13),('code_end',16),('dead_spans',[[4,10]]),('dead_spans',[[6,8]]),('dead_spans',[[6,10],[8,10]]),('justification',' '),('next_entry','ov03_F_9999')]:
   with self.subTest(key=key,value=value):
    x=self.fixture();x[4][key]=value;self.write(x[2],x[4])
    with self.assertRaises((FormatError,KeyError)):self.view(x)
 def test_foreign_reference_and_relocation(self):
  x=self.fixture();x[1]['functions'][1]['referenced_data'].append(dict(hunk=3,offset=6,kind='PC_RELATIVE_DATA'))
  with self.assertRaises(FormatError):self.view(x)
  x=self.fixture();x[3]['relocations'].append(dict(source_hunk=1,source_offset=0,target_hunk=3,addend_raw=6))
  with self.assertRaises(FormatError):self.view(x)
 def test_classified_or_owned_bytes_rejected(self):
  x=self.fixture();x[1]['classified_code_data']=[dict(interval=dict(hunk=3,start=6,end=10))]
  with self.assertRaises(FormatError):self.view(x)
  x=self.fixture();p=self.root/'recovery/ledger.json';p.parent.mkdir();p.write_text(json.dumps(dict(functions={'other':dict(state='FUNCTION_CODE_MATCH',evidence_extent=dict(hunk=3,start=6,end=10))})))
  with self.assertRaises(FormatError):self.view(x)
 def test_reachable_or_unresolved_dead_bytes_rejected(self):
  x=self.fixture();x[0]['boundary_stops']=[dict(reason='UNRESOLVED_JUMP')]
  with self.assertRaises(FormatError):self.view(x)
  x=self.fixture();x[0]['undecoded_gaps']=[]
  with self.assertRaises(FormatError):self.view(x)
 def test_foreign_next_entry_cannot_hide_in_body(self):
  x=self.fixture();x[1]['functions'][1]['start']=8
  with self.assertRaises(FormatError):self.view(x)
 def test_source_object_keeps_original_cfg(self):
  x=self.fixture();original=copy.deepcopy(x[0]);f=self.view(x);self.assertEqual(x[0],original);self.assertEqual(f['cfg'],original['cfg']);self.assertEqual(f['undecoded_gaps'],original['undecoded_gaps'])
 def test_changed_game_and_missing_justification(self):
  x=self.fixture();x=list(x);x[2]+=b'x'
  with self.assertRaises(FormatError):self.view(x)
 def test_cached_pass_without_pinned_inputs_rejected(self):
  x=self.fixture();p=self.root/dead.ADMISSIONS;p.write_text(json.dumps(dict(schema_version=1,admissions=[dict(id='ov03_F_0000',unit_entry='ov03_F_0000',entry_source=dict(path='to_delete/foo.c',sha256='0'*64),source=dict(path='to_delete/foo.c',sha256='0'*64),receipt={},compiler={},member_sources={})])))
  with self.assertRaises(FormatError):dead.verified_admissions(self.root,x[2],x[3],x[1])
 def test_dead_mode_cannot_promote(self):
  from unittest.mock import patch
  import check_unit
  with patch.object(sys,'argv',['check_unit.py','ov03_F_0000','dummy.c','--dead-code-extent']),patch.object(check_unit,'check') as check:
   with self.assertRaises(FormatError):check_unit.main()
   check.assert_not_called()
 def test_consistently_pinned_false_pass_source_rejected(self):
  x=self.fixture();source=self.root/'wrong.c';source.write_bytes(b'recovered(){return 7;}\n')
  receipt=self.root/'receipt.json';receipt.write_text(json.dumps(dict(verdict='EQUAL',id=x[0]['id'],unclaimed_bytes=0,source_sha256='0'*64)))
  compiler=self.root/'compiler.json';compiler.write_text(json.dumps(dict(artifacts=[])))
  def spec(path):return dict(path=path.relative_to(self.root).as_posix(),sha256=sha256(path.read_bytes()))
  p=self.root/dead.ADMISSIONS;p.write_text(json.dumps(dict(schema_version=1,admissions=[dict(id=x[0]['id'],unit_entry=x[0]['id'],entry_source=spec(source),source=spec(source),receipt=spec(receipt),compiler=spec(compiler),member_sources={})])))
  with self.assertRaisesRegex(FormatError,'candidate source changed'):dead.verified_admissions(self.root,x[2],x[3],x[1])
 def test_post_epilogue_tail_only_has_experimental_view(self):
  dead.admission_boundary(self.view(self.fixture(False)))
  with self.assertRaisesRegex(FormatError,'keep pending'):dead.admission_boundary(self.view(self.fixture(True)))
 def test_api_nonisolated_guards(self):
  import check_unit,check_function
  with dead.isolated_view('ov03_F_0000'):
   with self.assertRaisesRegex(FormatError,'requires isolated'):check_unit.check('ov03_F_0000',Path('missing.c'),['aztec36'])
   with self.assertRaisesRegex(FormatError,'requires isolated'):check_function.check_many([])
 def test_terminal_fallthrough_rejected(self):
  x=list(self.fixture(True));x[2]=x[2][:12]+bytes.fromhex('4e71')+x[2][14:];self.write(x[2],x[4])
  with self.assertRaisesRegex(FormatError,'terminal instruction'):self.view(x)
 def test_retained_exact_natural_unit_admitted_separately(self):
  from analysis_support import ROOT,game
  from recovery_state import evidence
  blob,model,_=game();analysis=evidence();rows=dead.verified_admissions(ROOT,blob,model,analysis)
  self.assertEqual([r['id'] for r in rows],['ov13_F_0942']);row=rows[0]
  self.assertEqual(row['dead_spans'],[[0xD80,0xE62]]);self.assertEqual(row['owned_literal_end'],0xF7E)
  self.assertFalse(row['source_acceptance']);self.assertEqual(row['complete_extent']['size'],1376)
  base=next(f for f in analysis['functions'] if f['id']==row['id']);self.assertTrue(base['undecoded_gaps'])
 def test_rehashed_cached_pass_contribution_cannot_replace_extraction(self):
  import shutil
  from analysis_support import ROOT,game
  from recovery_state import evidence
  blob,model,_=game();analysis=evidence()
  shutil.copytree(ROOT/'evidence/rules/dead-code-extents',self.root/'evidence/rules/dead-code-extents')
  registry=json.loads((self.root/dead.ADMISSIONS).read_bytes());row=registry['admissions'][0]
  receipt=json.loads((self.root/row['receipt']['path']).read_bytes())
  for name in receipt['verifier_identity']:shutil.copyfile(ROOT/'tools'/name,self.root/'tools'/name)
  compiler=self.root/row['compiler']['path'];producer=json.loads(compiler.read_bytes())
  raw=producer['contribution']['code_hex'];producer['contribution']['code_hex']=('00' if raw[:2]!='00' else '01')+raw[2:]
  compiler.write_bytes(json.dumps(producer).encode());row['compiler']['sha256']=sha256(compiler.read_bytes())
  (self.root/dead.ADMISSIONS).write_bytes(json.dumps(registry).encode())
  with self.assertRaisesRegex(FormatError,'extraction differs'):dead.verified_admissions(self.root,blob,model,analysis)
if __name__=='__main__':unittest.main()
