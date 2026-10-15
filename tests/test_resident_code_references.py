import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError,sha256
from function_census import Census
from function_compare import compare_function
import curated_unreferenced_entries as entries
R=bytes.fromhex('4e5500004e5d4e75')

class CallbackEntryTests(unittest.TestCase):
 def fixture(self,slot=0x100,record=0xee,api='_SetIntVector',classified=False,weak=False):
  start=0x10 if weak else 0;data=bytearray(0x82);data[:2]=bytes.fromhex('4e75')
  code=bytearray(R[:4]);lea=start+len(code);code+=bytes.fromhex('41fa')+(0x40-lea-2).to_bytes(2,'big',signed=True)
  store=start+len(code);code+=bytes.fromhex('23c8')+slot.to_bytes(4,'big')
  pea=start+len(code);code+=bytes.fromhex('4879')+record.to_bytes(4,'big')+bytes.fromhex('48780007')
  call=start+len(code);code+=bytes.fromhex('4eba')+(0x80-call-2).to_bytes(2,'big',signed=True)+bytes.fromhex('504f4e5d4e75')
  data[start:start+len(code)]=code;data[0x40:0x48]=R;data[0x80:]=bytes.fromhex('4e75')
  rels=[dict(source_hunk=0,source_offset=x+2,target_hunk=1,type='HUNK_RELOC32',width=4,addend_raw=v) for x,v in [(store,slot),(pea,record)]]
  model=dict(hunks=[dict(number=0,node='resident',type='CODE',content_offset=0,initialized_size=len(data)),dict(number=1,node='resident',type='DATA',content_offset=len(data),initialized_size=0x120)],relocations=rels,overlay=None)
  ranges=[dict(hunk=0,start=0x40,end=0x48,classification='DATA')] if classified else []
  c=Census(bytes(data)+bytes(0x120),model,ranges);c.callback_apis={(0,0x80):api}
  if weak:c.seed(0,start,dict(kind='POST_FUNCTION_PROLOGUE',code_predecessor='resident_F_0000'))
  return c,lea
 def test_registered_callback_is_independent_entry(self):
  c,lea=self.fixture();report=c.run();f=next(f for f in report['functions'] if f['start']==0x40)
  self.assertEqual(f['extent_status'],'CLOSED_CFG');self.assertEqual(f['reconstruction_state'],'DISCOVERED');self.assertEqual(f['ownership'],'UNKNOWN')
  caller=next(f for f in report['functions'] if f['start']==0)
  self.assertTrue(any(q.get('reference_kind')=='FUNCTION_POINTER' and q['site']==lea for q in caller['direct_callees']))
  self.assertFalse(any(q['instruction_offset']==lea for q in caller['referenced_data']))
 def test_wrong_field_or_unproved_api_rejects(self):
  for options in [dict(slot=0x104),dict(api='_Unknown'),dict(api='_DoIO'),dict(record=0xec)]:
   with self.subTest(options=options):
    c,_=self.fixture(**options);c.run();self.assertNotIn((0,0x40),c.function_references)
    self.assertFalse(any(f['start']==0x40 for f in c.run()['functions']))
 def test_code_shaped_data_is_not_an_entry_without_callback_use(self):
  c,_=self.fixture(api='_Unknown');c.run();self.assertFalse(c.function_references)
  self.assertNotIn((0,0x40),c.entries)
 def test_classified_data_cannot_be_callback_code(self):
  c,_=self.fixture(classified=True);c.run();self.assertNotIn((0,0x40),c.entries)
 def test_weak_caller_cannot_bootstrap_callback_strength(self):
  c,_=self.fixture(weak=True);c.run();self.assertFalse(c.function_references)
 def test_rts_does_not_discover_adjacent_resident_frame(self):
  c=Census(R*2,dict(hunks=[dict(number=0,node='resident',type='CODE',content_offset=0,initialized_size=16)],relocations=[],overlay=None),[])
  report=c.run();self.assertEqual(report['summary']['decoded_bytes'],8);self.assertEqual(len(report['functions']),1)
 def test_reference_uses_source_operand_of_lea(self):
  c,lea=self.fixture();from analysis_support import instruction
  self.assertEqual(c.target(0,instruction(c.md,c.data[0],lea)),(0,0x40,'PC_RELATIVE'))

class CallbackFingerprintTests(unittest.TestCase):
 def test_each_sdk_header_edit_and_removal_changes_complete_replay_identity(self):
  import dead_code_extents as dead,compiler_oracle
  from unittest.mock import patch
  from function_pointer_evidence import HEADERS,PREFIX
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   with patch.object(compiler_oracle,'ROOT',root),patch.object(dead,'__file__',str(root/'tools/dead_code_extents.py')):
    identity=lambda:dead.replay_identity(root,b'oracle',{},dict(functions=[]),dict(functions={}),None)
    for header in [PREFIX+h for h in HEADERS]+['evidence/toolchain/aztec-3.6a.json']:
     p=root/header;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'ABI')
     before=identity();p.write_bytes(b'ABI changed');self.assertNotEqual(identity(),before,header)
     p.write_bytes(b'ABI');self.assertEqual(identity(),before)
     p.unlink();self.assertNotEqual(identity(),before,header)

class InputDeviceEntryTests(unittest.TestCase):
 def fixture(self,opened=0x300,issued=0x300,device=b'input.device\0',command=9,api='_OpenDevice'):
  code=bytearray(R[:4]);rels=[]
  def absolute(op,value):
   site=len(code);code.extend(bytes.fromhex(op)+value.to_bytes(4,'big'))
   rels.append(dict(source_hunk=0,source_offset=site+2,target_hunk=1,type='HUNK_RELOC32',width=4,addend_raw=value))
  def pc(op,target):
   site=len(code);code.extend(bytes.fromhex(op)+(target-site-2).to_bytes(2,'big',signed=True))
  pc('41fa',0x100);absolute('23c8',0x212)
  code.extend(bytes.fromhex('42a7'));absolute('2f39',opened);code.extend(bytes.fromhex('42a7'));pc('487a',0x120);pc('4eba',0x180)
  code.extend(bytes.fromhex('4fef0010'));absolute('2079',issued);code.extend(bytes.fromhex('317c')+command.to_bytes(2,'big')+bytes.fromhex('001c'))
  absolute('41f9',0x200);absolute('2279',issued);code.extend(bytes.fromhex('23480028'));absolute('2f39',issued);pc('4eba',0x182)
  code.extend(bytes.fromhex('584f4e5d4e75'));data=bytearray(0x184);data[:len(code)]=code;data[0x100:0x108]=R;data[0x120:0x120+len(device)]=device;data[0x180:]=bytes.fromhex('4e754e75')
  model=dict(hunks=[dict(number=0,node='resident',type='CODE',content_offset=0,initialized_size=len(data)),dict(number=1,node='resident',type='DATA',content_offset=len(data),initialized_size=0x400)],relocations=rels,overlay=None)
  c=Census(bytes(data)+bytes(0x400),model,[]);c.callback_apis={(0,0x180):api,(0,0x182):'_DoIO'};return c
 def test_same_input_request_and_addhandler_prove_callback(self):
  c=self.fixture();c.run();fact=c.function_references[(0,4)]
  self.assertEqual(fact['evidence']['request_slot'],0x300);self.assertEqual(fact['offset'],0x100)
 def test_other_request_is_not_input_device_evidence(self):
  c=self.fixture(issued=0x304);c.run();self.assertFalse(c.function_references)
 def test_wrong_device_command_and_api_reject(self):
  for options in [dict(device=b'audio.device\0'),dict(command=10),dict(api='_Unknown')]:
   with self.subTest(options=options):
    c=self.fixture(**options);c.run();self.assertFalse(c.function_references)

class A4AddressEntryTests(unittest.TestCase):
 def fixture(self,kind='HUNK_RELOC32',width=4,opcode='4ef9'):
  code=bytearray(0x48);code[:12]=R[:4]+bytes.fromhex('41ec8002')+R[4:];code[0x40:]=R
  stub=bytes.fromhex(opcode)+(0x40).to_bytes(4,'big')
  rel=dict(source_hunk=1,source_offset=2,target_hunk=0,addend_raw=0x40,type=kind,width=width)
  c=Census(bytes(code)+stub,dict(hunks=[dict(number=0,node='resident',type='CODE',content_offset=0,initialized_size=len(code)),dict(number=1,node='resident',type='DATA',content_offset=len(code),initialized_size=6)],relocations=[rel],overlay=None),[])
  c.a4_bias=32766;return c
 def test_a4_slot_address_has_independent_code_pointer(self):
  f=next(f for f in self.fixture().run()['functions'] if f['start']==0x40)
  self.assertEqual(f['extent_status'],'CLOSED_CFG');self.assertTrue(any(e['kind']=='FUNCTION_REFERENCE' for e in f['entry_evidence']))
 def test_wrong_slot_opcode_width_type_never_strengthens_entry(self):
  for kwargs in [dict(opcode='4e75'),dict(width=2),dict(kind='HUNK_RELOC16')]:
   with self.subTest(kwargs=kwargs):
    f=next(f for f in self.fixture(**kwargs).run()['functions'] if f['start']==0x40)
    self.assertEqual(f['extent_status'],'UNCERTAIN')

class ResidentCurationTests(unittest.TestCase):
 def fixture(self,non_c_next=False,with_edge=False):
  data=R*3
  if non_c_next:data=R*2+bytes.fromhex('4e75')+bytes(6)+R[:4]+bytes.fromhex('4ebafff2')+R[4:]
  c=Census(data,dict(hunks=[dict(number=0,node='resident',type='CODE',content_offset=0,initialized_size=len(data))],relocations=[],overlay=None),[])
  if not non_c_next:c.seed(0,16,dict(kind='DIRECT_CALL',caller='fixture',site=0))
  if with_edge:c.seed(0,24,dict(kind='DIRECT_CALL',caller='fixture',site=0))
  c.run();return c
 def row(self):return dict(id='resident_F_0008',hunk=0,start=8,end=16,contribution_end=16,predecessor='resident_F_0000',next_entry='resident_F_0010',justification='Reviewed independently bounded complete chain; no source acceptance.')
 def validate(self,c,row=None):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);p=root/entries.INPUT;p.parent.mkdir(parents=True);p.write_text(json.dumps(dict(schema_version=1,game_sha256=sha256(c.blob),source_acceptance=False,entries=[row or self.row()])))
   entries.discover_reviewed_candidates(c,root);c.run()
   return entries.validate(c,root)
 def test_reviewed_resident_curation(self):
  c=self.fixture();self.assertNotIn((0,8),c.entries)
  facts=self.validate(c);self.assertEqual(len(facts),1)
  weak=next(f for f in c.run()['functions'] if f['start']==8)
  self.assertEqual(weak['extent_status'],'UNCERTAIN')
  self.assertTrue(any(e['kind']=='CURATED_UNREFERENCED_CANDIDATE' for e in weak['entry_evidence']))
  for fact in facts:c.seed(fact['hunk'],fact['start'],fact)
  self.assertEqual(next(f for f in c.run()['functions'] if f['start']==8)['extent_status'],'CLOSED_CFG')
 def test_data_hunks_and_wrong_names_reject(self):
  for key,value in [('hunk',1),('hunk',2),('id','ov00_F_0008')]:
   row=self.row();row[key]=value
   with self.subTest(key=key,value=value),self.assertRaises(FormatError):self.validate(self.fixture(),row)
 def test_next_non_c_boundary_requires_actual_incoming_edge(self):
  self.assertEqual(len(self.validate(self.fixture(True,True))),1)
  with self.assertRaises(FormatError):self.validate(self.fixture(True,False))
 def test_foreign_relocation_rejects_curation(self):
  c=self.fixture();c.model['relocations'].append(dict(source_hunk=1,source_offset=0,target_hunk=0,addend_raw=10))
  with self.assertRaises(FormatError):self.validate(c)
 def test_changed_bounds_and_missing_anchor_reject(self):
  for key,value in [('end',18),('predecessor','resident_F_0010'),('next_entry','resident_F_0000')]:
   row=self.row();row[key]=value
   with self.subTest(key=key),self.assertRaises(FormatError):self.validate(self.fixture(),row)

class EarlyEpilogueBoundsTests(unittest.TestCase):
 def fixture(self,tail='60f8'):
  # Both branches are reachable; the final block returns through an earlier
  # local UNLK/RTS. These are synthetic instructions, not oracle source.
  first=bytes.fromhex('4e5500004a4066044e5d4e757001'+tail)
  data=first+R*2;c=Census(data,dict(hunks=[dict(number=0,node='resident',type='CODE',content_offset=0,initialized_size=len(data))],relocations=[],overlay=None),[])
  c.seed(0,24,dict(kind='DIRECT_CALL',caller='fixture',site=0));return c
 def test_early_epilogue_predecessor_discovers_weak_entry(self):
  c=self.fixture();r=c.run();f=next(f for f in r['functions'] if f['start']==16)
  self.assertEqual(f['extent_status'],'UNCERTAIN')
  self.assertEqual(f['entry_evidence'][0]['kind'],'POST_FUNCTION_PROLOGUE')
 def test_loop_tail_is_not_an_epilogue(self):
  c=self.fixture('60f4');r=c.run();self.assertFalse(any(f['start']==16 for f in r['functions']))
 def test_rts_without_unlk_is_not_an_epilogue(self):
  c=self.fixture('60fa');r=c.run();self.assertFalse(any(f['start']==16 for f in r['functions']))
 def test_curated_chain_after_early_epilogue(self):
  c=self.fixture();c.run()
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);p=root/entries.INPUT;p.parent.mkdir(parents=True)
   p.write_text(json.dumps(dict(schema_version=1,game_sha256=sha256(c.blob),source_acceptance=False,entries=[dict(id='resident_F_0010',hunk=0,start=16,end=24,contribution_end=24,predecessor='resident_F_0000',next_entry='resident_F_0018',justification='Reviewed gap-free complete body after separately closed predecessor.')])) )
   self.assertEqual(len(entries.validate(c,root)),1)

class PointerComparisonTests(unittest.TestCase):
 def compare(self,symbol='_F_h00_0040',inside=0,has_reference=True):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);root.joinpath('t.c').write_text('extern int F_h00_0040(); recovered() { }\n');root.joinpath('t.exe').write_bytes(bytes(128))
   original=R[:4]+bytes.fromhex('41fa003a')+R[4:];actual=R[:4]+bytes.fromhex('41fa')+(0x30+inside-6).to_bytes(2,'big')+R[4:]
   f=dict(id='resident_F_0000',hunk=0,start=0,end=12,size=12,raw_bytes=original.hex(),extent_status='CLOSED_CFG',relocations=[],referenced_data=[],direct_callees=[dict(site=4,hunk=0,offset=0x40,id='resident_F_0040',basis='PC_RELATIVE',reference_kind='FUNCTION_POINTER')] if has_reference else [])
   c=dict(code_hex=actual.hex(),code_offset=0,code_size=12,data_size=0,bss_size=0,hunk=0,all_relocations=[],relocations=[],symbols=[dict(name=symbol,hunk=0,offset=0x30)],hunks=[dict(number=0,content_offset=0),dict(number=1,initialized_size=0,allocated_size=0),dict(number=2,allocated_size=4)])
   compiled=dict(status='COMPILED',identity=dict(profile='aztec36',flags=[]),cache_key='x'*64,cache_hit=False,contribution=c,directory=str(root),prefix='t')
   return compare_function(f,compiled,32766,context=dict(root=root,blob=b'',model={}))
 def test_named_callback_field_matches(self):self.assertEqual(self.compare()['verdict'],'EQUAL')
 def test_wrong_callback_identity_rejects(self):self.assertNotEqual(self.compare('_F_h00_0042')['verdict'],'EQUAL')
 def test_interior_callback_does_not_bind(self):self.assertNotEqual(self.compare(inside=2)['verdict'],'EQUAL')
 def test_no_reference_never_normalizes_pointer(self):self.assertNotEqual(self.compare(has_reference=False)['verdict'],'EQUAL')
class LaterObjectEntryTests(unittest.TestCase):
 def fixture(self):
  from resident_object import bounds
  tmp=tempfile.TemporaryDirectory();root=Path(tmp.name)
  for name,label in [('h000','_main'),('t000','_F_h00_0000'),('t000_part001','_recovered')]:
   root.joinpath(name+'.asm').write_text('\tpublic '+label+'\n'+label+':\n\trts\n')
   root.joinpath(name+'.o').write_bytes(b'AJ'+bytes(8)+(2).to_bytes(4,'big')+bytes(8))
  model=dict(hunks=[dict(number=0,type='CODE',node='resident',initialized_size=6)],relocations=[])
  symbols={(0,'_main'):0,(0,'_F_h00_0000'):2,(0,'_recovered'):4}
  return tmp,root,model,symbols,bounds
 def test_named_entry_in_later_ordered_object(self):
  tmp,root,model,symbols,bounds=self.fixture()
  with tmp:
   base,entry,meta=bounds(root,'t000',['candidate','part001'],model,symbols,'recovered')
   self.assertEqual((base,entry,meta['end']),(2,2,6));self.assertEqual(len(meta['objects']),2)
 def test_missing_outside_or_unauthored_entry_rejects(self):
  for edit in ('outside','missing','unauthored','order','foreign'):
   tmp,root,model,symbols,bounds=self.fixture()
   with tmp,self.subTest(edit=edit):
    if edit=='outside':symbols[(0,'_recovered')]=6
    elif edit=='missing':del symbols[(0,'_recovered')]
    elif edit=='unauthored':root.joinpath('t000_part001.asm').write_text('_other:\n\trts\n');symbols[(0,'_other')]=4
    elif edit=='order':symbols[(0,'_recovered')]=5
    else:symbols[(0,'_foreign')]=3
    with self.assertRaises(FormatError):bounds(root,'t000',['candidate','part001'],model,symbols,'recovered')

class CallbackSnapshotInputTests(unittest.TestCase):
 def test_callback_abi_header_edit_and_removal_invalidate_snapshot(self):
  import evidence_snapshot as snapshots
  from common import write_json
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   for name in ('assets','tools','evidence/functions','recovery','custom'):(root/name).mkdir(parents=True,exist_ok=True)
   (root/'assets/disk.adf').write_bytes(b'fixture')
   header=root/'custom/abi.h';header.write_bytes(b'ABI1')
   write_json(root/'evidence/fixture-lock.json',{})
   write_json(root/'evidence/functions/ledger.json',dict(analysis_identity={},callback_reference_identity={'custom/abi.h':sha256(b'ABI1')}))
   write_json(root/'recovery/ledger.json',dict(functions={},attempts={},blockers={}))
   with snapshots.snapshot() as state:
    load=lambda:(b'game',{}, {})
    snapshots.game_read(root,load)
    header.write_bytes(b'ABI2');snapshots.game_read(root,load)
    header.unlink();snapshots.game_read(root,load)
    self.assertEqual(state.invalidations,2)

if __name__=='__main__':unittest.main(verbosity=2)
