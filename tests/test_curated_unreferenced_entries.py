import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError,sha256
from function_census import Census
import curated_unreferenced_entries as entries
R=bytes.fromhex('4e5500004e5d4e75')
class CuratedEntryTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def fixture(self,data=None,anchors=(0,16)):
  data=data or R*3;c=Census(data,dict(hunks=[dict(number=3,node='ov03',type='CODE',content_offset=0,initialized_size=len(data))],relocations=[],overlay=None),[])
  for a in anchors:c.seed(3,a,dict(kind='OVERLAY_EXPORT',slot=1))
  c.run();return c
 def rows(self):return [dict(id='ov03_F_0008',hunk=3,start=8,end=16,contribution_end=16,predecessor='ov03_F_0000',next_entry='ov03_F_0010',justification='Adjacent complete uncalled LINK routine.')]
 def write(self,c,rows):
  p=self.root/entries.INPUT;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(dict(schema_version=1,game_sha256=sha256(c.blob),source_acceptance=False,entries=rows)),encoding='utf-8')
 def test_weak_stays_uncertain(self):
  c=self.fixture();f=next(x for x in c.run()['functions'] if x['start']==8)
  self.assertEqual(f['extent_status'],'UNCERTAIN');self.assertEqual(f['entry_evidence'][0]['kind'],'POST_FUNCTION_PROLOGUE')
 def test_positive_no_source_credit(self):
  c=self.fixture();self.write(c,self.rows());facts=entries.validate(c,self.root)
  for r in facts:c.seed(r['hunk'],r['start'],r)
  f=next(x for x in c.run()['functions'] if x['start']==8)
  self.assertEqual(f['extent_status'],'CLOSED_CFG');self.assertEqual(f['ownership'],'UNKNOWN');self.assertEqual(f['reconstruction_state'],'DISCOVERED')
 def test_chain(self):
  c=self.fixture(R*4,(0,24));rows=self.rows();rows.append(dict(id='ov03_F_0010',hunk=3,start=16,end=24,contribution_end=24,predecessor='ov03_F_0008',next_entry='ov03_F_0018',justification='Second anchored complete routine.'))
  self.write(c,rows);self.assertEqual(len(entries.validate(c,self.root)),2)
 def test_bad_schema_and_coordinates(self):
  c=self.fixture()
  for k,v in [('justification',' '),('hunk',0),('start',9),('end',18),('contribution_end',18),('predecessor','ov03_F_0010'),('next_entry','ov03_F_0000'),('start',True)]:
   with self.subTest(k=k,v=v):
    rows=self.rows();rows[0][k]=v;self.write(c,rows)
    with self.assertRaises(FormatError):entries.validate(c,self.root)
  rows=self.rows()*2;self.write(c,rows)
  with self.assertRaises(FormatError):entries.validate(c,self.root)
 def test_foreign_reference(self):
  c=self.fixture();self.write(c,self.rows());c.model['relocations'].append(dict(target_hunk=3,addend_raw=10,source_hunk=1,source_offset=0))
  with self.assertRaises(FormatError):entries.validate(c,self.root)
 def test_classified_data(self):
  c=self.fixture();self.write(c,self.rows());c.blocked[3].append((8,16,'DATA'))
  with self.assertRaises(FormatError):entries.validate(c,self.root)
 def test_overlap_and_future_self_ownership(self):
  c=self.fixture();self.write(c,self.rows());p=self.root/'recovery/ledger.json';p.parent.mkdir()
  for fid,accept in [('other',False),('ov03_F_0008',True)]:
   p.write_text(json.dumps(dict(functions={fid:dict(state='FUNCTION_CODE_MATCH',evidence_extent=dict(hunk=3,start=8,end=16))})))
   if accept:self.assertEqual(len(entries.validate(c,self.root)),1)
   else:
    with self.assertRaises(FormatError):entries.validate(c,self.root)
 def test_unreachable_bytes_rejected(self):
  c=self.fixture(R+bytes.fromhex('4e55000060024e714e5d4e75')+R,(0,20));rows=self.rows();rows[0].update(end=20,contribution_end=20,next_entry='ov03_F_0014');self.write(c,rows)
  with self.assertRaises(FormatError):entries.validate(c,self.root)
 def test_literal_boundaries(self):
  lit=bytes.fromhex('4e550000487a0008588f4e5d4e75')+b'x\0'
  for predecessor in [True,False]:
   if predecessor:
    c=self.fixture(lit+R*2,(0,24));row=dict(id='ov03_F_0010',hunk=3,start=16,end=24,contribution_end=24,predecessor='ov03_F_0000',next_entry='ov03_F_0018',justification='Following a contiguous referenced literal tail.')
   else:
    c=self.fixture(R+lit,(0,));row=dict(id='ov03_F_0008',hunk=3,start=8,end=22,contribution_end=24,predecessor='ov03_F_0000',next_entry=None,justification='Own contiguous referenced terminal literal tail.')
   self.write(c,[row]);self.assertEqual(len(entries.validate(c,self.root)),1)
 def test_identity_and_changed_game(self):
  c=self.fixture();rows=self.rows();self.write(c,rows);a=entries.identity(self.root);rows[0]['justification']+=' Review.';self.write(c,rows);self.assertNotEqual(a,entries.identity(self.root));c.blob+=b'x'
  with self.assertRaises(FormatError):entries.validate(c,self.root)
 def test_floating_chain(self):
  c=self.fixture(R*3,(16,));self.write(c,self.rows())
  with self.assertRaises(FormatError):entries.validate(c,self.root)
if __name__=='__main__':unittest.main()
