"""Synthetic mixed-hunk score/data invariants; no real corpus counts or emulators."""
import copy,struct,unittest,tempfile
from unittest.mock import patch
from contextlib import contextmanager
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError
import audio_h1_catalogue as t
import audio_h1_provider as p


def control():
 defs=[dict(name=n,hunk=h,offset=o,external=False,context=c) for n,h,o,c in [('_mx_c_begin',0,0,'CSEG'),('_mx_c_end',0,12,'CSEG'),('_mx_a',1,0,'CSEG'),('_mx_b',1,9,'CSEG'),('_mx_d_begin',1,0,'DSEG'),('_mx_d_end',1,13,'DSEG'),('_mx_pattern',1,12,'DSEG')]]
 fix=[dict(hunk=h,offset=o,symbol=n,type='HUNK_RELOC32',width=4,addend=0) for h,o,n in [(0,0,'_mx_a'),(0,4,'_mx_b'),(0,8,'_mx_c_begin'),(1,4,'_mx_pattern')]]
 sections={0:bytes(12),1:bytes.fromhex('00018500000000008801028886')}
 return defs,fix,sections


def aj(defs,fix,sections):
 stream=bytearray();symbol_ids={d['name']:i for i,d in enumerate(defs)}
 for h in (0,1):
  if h:stream.append(0xf5)
  raw=sections[h];by={f['offset']:f for f in fix if f['hunk']==h};offset=0
  while offset<len(raw):
   if offset in by:
    index=symbol_ids[by[offset]['symbol']];stream+=bytes((0xfd,0x70+index%16,index//16));offset+=4
   else:
    end=offset+1
    while end<len(raw) and end not in by and end-offset<16:end+=1
    stream+=bytes((0x0f+end-offset,))+raw[offset:end];offset=end
 stream+=bytes((-(36+len(stream))-1)%4+1);symbols=bytearray()
 for d in defs:
  count=sum(f['symbol']==d['name'] for f in fix);kind=7 if d['external'] else 2 if d['hunk']==0 else 3
  attr=(12 if count else 8) if kind in (2,7) or d['context']=='CSEG' else (42 if count else 10)
  symbols+=bytes((kind,attr))+d['offset'].to_bytes(2,'big')
  if count:symbols+=count.to_bytes(2,'big')
  symbols+=d['name'].encode()+b'\0'
 symbols+=bytes((-len(symbols))%4);header=bytearray(36);header[:2]=b'AJ';header[34:36]=b'\xc0\0'
 for at,n in [(10,len(sections[0])+(len(sections[0])%2)),(14,len(sections[1])+(len(sections[1])%2)),(24,9)]:header[at:at+4]=n.to_bytes(4,'big')
 for at,n in [(22,len(defs)),(28,(36+len(stream))//4),(30,(36+len(stream)+len(symbols))//4),(32,(36+len(stream)+len(symbols))//4)]:header[at:at+2]=n.to_bytes(2,'big')
 return bytes(header+stream+symbols)


def grammar():
 forms=lambda length,flow,pointer=None:[dict(length=length,pointer_field=pointer,flows=flow),dict(length=length,pointer_field=pointer,flows=flow)]
 return dict(score=dict(note_forms=forms(2,['NEXT']),opcodes=[dict(opcode=0x88,forms=forms(1,['STOP'])),dict(opcode=0x85,forms=forms(6,['CALL'],2)),dict(opcode=0x86,forms=forms(1,['RETURN']))]))


def image(score=b'\0\1\x3c\2\x88',target_hunk=1):
 h0=bytearray(0x6240);h1=bytes(score);h0[0x6218:0x621c]=bytes(4)
 model=dict(hunks=[dict(number=0,content_offset=0,initialized_size=len(h0)),dict(number=1,content_offset=len(h0),initialized_size=len(h1))],relocations=[dict(source_hunk=0,source_offset=0x6218,target_hunk=target_hunk,addend_raw=0,type='HUNK_RELOC32',width=4)])
 return bytes(h0)+h1,model


class AudioH1(unittest.TestCase):
 def test_whole_mixed_object_and_section_aware_fixups(self):
  ds,fs,ss=control();out=p.object_mixed(aj(ds,fs,ss),{0:12,1:13},ds,fs)
  self.assertEqual(out['sections'][0],bytes.fromhex('000000000000000900000000'))
  self.assertEqual(out['sections'][1],bytes.fromhex('000185000000000c880102888600'))
  self.assertEqual(out['fixups'],fs)
 def test_changed_target_section_or_symbol_rejects(self):
  ds,fs,ss=control();raw=aj(ds,fs,ss)
  for key,value in [('hunk',0),('name','_wrong'),('offset',2)]:
   bad=copy.deepcopy(ds);bad[2][key]=value
   with self.subTest(key=key),self.assertRaises(FormatError):p.object_mixed(raw,{0:12,1:13},bad,fs)
 def test_extra_sections_common_trailer_or_partial_objects_reject(self):
  ds,fs,ss=control();raw=aj(ds,fs,ss)
  for kind in ('CODE','DATA','BSS','symbol','trailer'):
   bad=bytearray(raw)
   if kind in ('CODE','DATA','BSS'):
    at={'CODE':10,'DATA':14,'BSS':18}[kind];bad[at+3]^=2
   elif kind=='symbol':bad[int.from_bytes(raw[28:30],'big')*4+1]^=2
   else:bad[-1]=1
   with self.subTest(kind=kind),self.assertRaises(FormatError):p.object_mixed(bytes(bad),{0:12,1:13},ds,fs)
  with self.assertRaises(FormatError):p.object_mixed(raw,{0:12,1:12},ds,fs)
 def test_wrong_fixup_reference_count_or_packed_index_rejects(self):
  ds,fs,ss=control();raw=aj(ds,fs,ss)
  bad=bytearray(raw);bad[37]=0x7f;bad[38]=0xff
  with self.assertRaises(FormatError):p.object_mixed(bytes(bad),{0:12,1:13},ds,fs)
  with self.assertRaises(FormatError):p.object_mixed(raw,{0:12,1:13},ds,fs[:-1])
 def test_hidden_section_switch_or_addend_rejects(self):
  ds,fs,ss=control();raw=bytearray(aj(ds,fs,ss));raw[36]=0xf4
  with self.assertRaises(FormatError):p.object_mixed(bytes(raw),{0:12,1:13},ds,fs)
 def test_typed_commands_reject_opaque_bytes_integer_pointers_and_extra_fields(self):
  for c in [dict(hunk=1,offset=0,type='BYTES',values=[1,2]),dict(hunk=1,offset=0,type='CALL',values=[123]),dict(hunk=1,offset=0,type='NOTE',values=[128,1]),dict(hunk=1,offset=0,type='HEADER',values=[4,0]),dict(hunk=1,offset=0,type='END',values=[],padding=[0])]:
   with self.subTest(c=c),self.assertRaises((FormatError,KeyError)):t.check(c)
 def test_h1_record_ends_at_decoded_terminal_not_hunk_limit(self):
  b,m=image(b'\0\1\x3c\2\x88\0\0\0');out=t.score_closure(b,m,grammar(),6)
  self.assertEqual([(c['hunk'],c['offset'],c['type']) for c in out['rows']],[(1,0,'HEADER'),(1,2,'NOTE'),(1,4,'END')]);self.assertEqual(out['streams'][0]['end'],5)
 def test_unterminated_or_unknown_scores_reject(self):
  for score in (b'\0\1\x3c\2',b'\0\1\xff'):
   b,m=image(score)
   with self.assertRaises((FormatError,KeyError)):t.score_closure(b,m,grammar(),6)
 def test_wrong_selector_hunk_or_relocation_rejects(self):
  b,m=image(target_hunk=2)
  with self.assertRaises(FormatError):t.score_closure(b,m,grammar(),6)
  b,m=image();m['relocations']=[]
  with self.assertRaises(FormatError):t.score_closure(b,m,grammar(),6)
 def test_cross_hunk_pattern_is_not_silently_treated_as_local(self):
  b,m=image(b'\0\1\x85\0'+bytes(4)+b'\x88');m['relocations'].append(dict(source_hunk=1,source_offset=4,target_hunk=0,addend_raw=0,type='HUNK_RELOC32',width=4))
  with self.assertRaises(FormatError):t.score_closure(b,m,grammar(),6)
 def test_publication_overlap_checks_the_original_hunk_and_avoids_corpus_replay(self):
  import promote_code_data as publish
  import hybrid_image
  report=dict(objects=[dict(original=dict(hunk=0),parts=[dict(original_start=10,original_end=12)]),dict(original=dict(hunk=1),parts=[dict(original_start=10,original_end=13)])])
  accounting=dict(ranges=[dict(hunk=0,start=10,end=13,category='RAW_ORACLE_DEBT'),dict(hunk=1,start=10,end=13,category='RAW_ORACLE_DEBT')])
  def document(root,name):return accounting if name=='evidence/hybrid/accounting.json' else {'id':'synthetic'}
  with patch.object(publish.provider,'document',side_effect=document),patch.object(publish.h1,'verify',return_value=report),patch.object(hybrid_image,'build',side_effect=AssertionError('whole-corpus replay')):
   self.assertEqual(publish._stage(Path('.'),b'',{}, {},p.MANIFEST)[1],report)
   accounting['ranges'][1]['category']='RECOVERED_DATA'
   with self.assertRaises(FormatError):publish._stage(Path('.'),b'',{}, {},p.MANIFEST)
   accounting['ranges'].pop()
   with self.assertRaises(FormatError):publish._stage(Path('.'),b'',{}, {},p.MANIFEST)
 def test_publisher_batches_strict_and_advisory_input_validation_once_per_stage(self):
  import promote_code_data as publish
  events=[]
  @contextmanager
  def boundary(root,strict):
   events.append(('before',strict));yield;events.append(('after',strict))
  with tempfile.TemporaryDirectory() as temp,patch('evidence_snapshot.validated_stage',side_effect=boundary),patch.object(publish,'_stage',return_value=('fact','report')) as stage:
   self.assertEqual(publish.stage(Path(temp),b'',{}, {},p.MANIFEST),('fact','report'));self.assertEqual(stage.call_count,1)
  self.assertEqual(events,[('before',True),('before',False),('after',False),('after',True)])
 def test_source_uses_semantic_fields_and_named_targets(self):
  rows=[dict(hunk=0,offset=0,type='SELECTOR',values=[t.symbol(1,'h',0)]),dict(hunk=1,offset=0,type='HEADER',values=[0,1]),dict(hunk=1,offset=2,type='NOTE',values=[60,2]),dict(hunk=1,offset=4,type='END',values=[])]
  objects=[dict(hunk=0,rows=rows[:1],typed_bytes=4),dict(hunk=1,rows=rows[1:],typed_bytes=5)]
  src=t.source(objects,grammar());self.assertIn(b'T5_HEADER 0,1',src);self.assertIn(b'T5_NOTE 60,2',src);self.assertIn(b'T5_END',src);self.assertIn(b'\tdseg',src)
  self.assertNotIn(b'\tds.b',src)

if __name__=='__main__':unittest.main()
