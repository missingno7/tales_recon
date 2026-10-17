"""Synthetic symbolic CODE-entry offsets and bounded startup provider invariants."""
import copy,json,sys,unittest,struct,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError
import data_provider_selector as selectors
import data_provider_startup as st
import data_provider_pointers as ptr
import data_provider_vamos as backend
import data_provider_job as gen


def aj(targets=('_A','_B','_A'),addends=(2,4,2)):
 names=list(dict.fromkeys(targets));stream=bytearray(b'\xf5')
 for name,a in zip(targets,addends):
  stream+=b'\xfd'+(b'\x21' if a else b'')+bytes([0x71+names.index(name),0])+(st.ADDEND_BYTES[a] if a else b'')
 stream+=b'\xf4\xf5';stream+=bytes((-(36+len(stream))-1)%4+1)
 sym=b'\x03\x0a\0\0_P\0'
 for n in names:sym+=b'\x07\x28\0\0'+targets.count(n).to_bytes(2,'big')+n.encode()+b'\0'
 sym+=bytes((-len(sym))%4);h=bytearray(36);h[:2]=b'AJ';h[34:36]=b'\xc0\0'
 for off,value in [(14,4*len(targets)),(24,9)]:h[off:off+4]=value.to_bytes(4,'big')
 for off,value in [(22,1+len(names)),(28,(36+len(stream))//4),(30,(36+len(stream)+len(sym))//4),(32,(36+len(stream)+len(sym))//4)]:h[off:off+2]=value.to_bytes(2,'big')
 return bytes(h)+stream+sym


def linked(targets=('_A','_B','_A'),addends=(2,4,2),names=('_A','_B')):
 size=4*len(targets);round4=lambda n:(n+3)&~3;code=b'\x4e\x75'*(1+len(names));code+=bytes((-len(code))%4);data=b''.join((2+2*names.index(n)+a).to_bytes(4,'big') for n,a in zip(targets,addends));data+=bytes((-len(data))%4)
 words=lambda *a:struct.pack('>'+str(len(a))+'I',*a)
 blob=words(1011,0,3,0,2,len(code)//4,len(data)//4,1,1001,len(code)//4)+code+words(1010,1002,len(data)//4)+data+words(1004,len(targets),0,*range(0,size,4),0,1010,1003,1,1010)
 groups=[{'.begin':0,'__H0_org':0,'__H0_end':len(code),**{n:2+2*i for i,n in enumerate(names)}},{'__H1_org':0,'_P':0,'__H1_end':len(data)},{'__H2_org':len(data),'__H2_end':len(data)}]
 text=''.join('Segment 00:  Hunk %03d\n'%i+''.join('\t%08x %s\n'%(off,n) for n,off in g.items()) for i,g in enumerate(groups))
 return blob,text


def prefix():
 bs={'_recon_h00_619E':dict(hunk=0,offset=0x619e,provider='bridge',entry='_recon_h00_619E',addend=0),'_recon_h00_61A0':dict(hunk=0,offset=0x61a0,provider='copy',entry='_recon_h00_61A0',addend=0)}
 return dict(selector_writers=dict(fact=selectors.FACT,sha256='a'*64),schema_version=1,kind='EXTERNAL_CODE_POINTER_TABLE',id='resident_data_2BC2',source='src/recovered/data/resident_data_2BC2.c',original=dict(hunk=1,start=0x2bc2,size=20),definitions=[dict(symbol='G_h01_2BC2',type='CODE_ENTRY_POINTER',offset=0,count=5,targets=[list(bs)[0]]+[list(bs)[1]]*4,bounds=dict(kind='CALLBACK_INDEX_DOMAIN_PREFIX',bytes=20),evidence={})],bindings=bs,object_sections=dict(CODE=0,DATA=20,BSS=0,COMMON=0),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,producer={})


class SymbolicCodeEntryControls(unittest.TestCase):
 def test_complete_addend_object_and_repeated_external(self):
  r=ptr.object_data(aj(),'_P',['_A','_B','_A'],[2,4,2]);self.assertEqual(r['bytes'],bytes.fromhex('000000020000000400000002'));self.assertEqual([x['addend'] for x in r['fixups']],[2,4,2]);self.assertEqual(r['sections'],dict(CODE=0,DATA=12,BSS=0,COMMON=0))
 def test_zero_addend_old_grammar_is_preserved(self):
  r=ptr.object_data(aj(addends=(0,0,0)),'_P',['_A','_B','_A']);self.assertEqual(r['bytes'],bytes(12));self.assertTrue(all(x['addend']==0 for x in r['fixups']))
 def test_every_measured_addend_constant_is_checked(self):
  for a in st.ADDEND_BYTES:
   r=ptr.object_data(aj(('_A',),(a,)),'_P',['_A'],[a]);self.assertEqual(r['fixups'][0]['addend'],a)
 def test_wrong_addend_and_unknown_expression_reject(self):
  for mode in ('value','operator','symbol','hidden_CODE','COMMON','trailer','reference_count'):
   raw=bytearray(aj())
   if mode=='value':raw[41]^=1
   elif mode=='operator':raw[38]=0x22
   elif mode=='symbol':raw[39]=0x72
   elif mode=='hidden_CODE':raw[10:14]=(2).to_bytes(4,'big')
   elif mode=='COMMON':raw[18:22]=(4).to_bytes(4,'big')
   elif mode=='trailer':raw[-1]=1
   else:raw[raw.index(b'\x07\x28')+5]^=1
   with self.subTest(mode=mode),self.assertRaises(FormatError):ptr.object_data(bytes(raw),'_P',['_A','_B','_A'],[2,4,2])
 def test_unmeasured_or_partial_addend_request_rejects(self):
  for addends in ([2,4],[3,4,2],[-2,4,2],[True,4,2]):
   with self.subTest(addends=addends),self.assertRaises(FormatError):ptr.object_data(aj(),'_P',['_A','_B','_A'],addends)
 def test_complete_named_link_sums_relocations_and_topology(self):
  blob,text=linked();r=ptr.linked_view(aj(),blob,text,'_P',['_A','_B','_A'],['_A','_B'],[2,4,2]);self.assertEqual(r[2],bytes.fromhex('000000040000000800000004'))
 def test_changed_link_payload_or_named_offset_rejects(self):
  blob,text=linked();b=bytearray(blob);from hunk import parse
  h=parse(blob)['hunks'][1];b[h['content_offset']+3]^=2
  for image,mapping in ((bytes(b),text),(blob,text.replace('00000002 _A','00000004 _A'))):
   with self.assertRaises(FormatError):ptr.linked_view(aj(),image,mapping,'_P',['_A','_B','_A'],['_A','_B'],[2,4,2])
 def test_prefix_does_not_admit_metadata_or_global_capacity(self):
  f=prefix();self.assertEqual(st.shape(f),20);self.assertIn(b'G_h01_2BC2[5]',st.source(f))
  for count in (2,4,6,15,25):
   g=copy.deepcopy(f);g['definitions'][0]['count']=count;g['original']['size']=4*count;g['object_sections']['DATA']=4*count;g['definitions'][0]['bounds']['bytes']=4*count
   with self.assertRaises(FormatError):st.shape(g)
 def test_selector_census_keeps_unrestricted_argument_and_all_literal_stores(self):
  rows=selectors.assignments('/* G_h01_2C26=99; */\nG_h01_2C26=0L; G_h01_2C26 = 1; G_h01_2C26=0x4; G_h01_2C26=p;')
  self.assertEqual([r['value'] for r in rows],[0,1,4,None]);self.assertEqual(rows[-1]['expression'],'p')
 def test_selector_census_does_not_confuse_reads_comments_or_comparisons(self):
  self.assertEqual(selectors.assignments('extern long G_h01_2C26; x=G_h01_2C26; if (G_h01_2C26==4) x=0; // G_h01_2C26=9;\n'),[])
  self.assertIsNone(selectors.assignments('G_h01_2C26 += 1;')[0]['value'])
 def test_reachable_domain_retains_unknown_writer_unless_explicitly_excluded(self):
  writers=[dict(function='live',value=0),dict(function='live',value=1),dict(function='live',value=4),dict(function='dead',value=None)]
  with self.assertRaises(FormatError):selectors.reachable_domain(0,writers,set())
  self.assertEqual(selectors.reachable_domain(0,writers,{'dead'}),([0,1,4],5))
  writers.append(dict(function='other',value=None))
  with self.assertRaises(FormatError):selectors.reachable_domain(0,writers,{'dead'})
 def test_reachable_domain_rejects_negative_and_noninteger_indices(self):
  for value in (-1,None,True):
   with self.assertRaises(FormatError):selectors.reachable_domain(0,[dict(function='live',value=value)],set())
  self.assertEqual(selectors.reachable_domain(2,[dict(function='live',value=6)],set()),([2,6],7))
 def test_selector_census_requires_its_pinned_fact(self):
  f=prefix();del f['selector_writers']['sha256']
  with self.assertRaises(FormatError):st.shape(f)
 def test_target_is_named_provider_not_integer_pointer(self):
  f=prefix();f['definitions'][0]['targets'][0]=0x619e
  with self.assertRaises(FormatError):st.source(f)
  f=prefix();next(iter(f['bindings'].values()))['addend']=2
  with self.assertRaises(FormatError):st.source(f)
 def test_backend_unknown_or_unpinned_rejects_without_execution(self):
  with patch.object(backend,'runtime_pin',return_value={'pin':'valid'}):
   for request in ({'backend':'winuae','backend_pin':{'pin':'valid'}},{'backend':'vamos','backend_pin':{'pin':'changed'}}):
    with self.assertRaises(FormatError):backend.validate(Path('.'),Path('.'),request,{},[])
 def test_backend_cannot_discover_arbitrary_scratch_copy(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);request={'backend':'vamos','backend_pin':dict(toolchain_copy='other',vamos_executable='a',vamos_python='b',compatibility_shim='c')}
   with self.assertRaises(FormatError):backend.input_paths(root,request)
 def test_legacy_dependency_paths_do_not_read_a_job_per_provider(self):
  import data_providers as dp
  recipe=dict(job='build/worker-jobs/tu-layout-synthetic',artifacts={})
  with patch.object(dp,'candidate_path',side_effect=AssertionError('per-provider job I/O')):
   paths=dp.producer_paths(Path('.'),recipe)
  self.assertIn(recipe['job']+'/request.json',paths)

 def test_backend_dependency_paths_are_explicit_and_complete(self):
  import data_providers as dp
  recipe=dict(job='build/worker-jobs/tu-layout-synthetic',artifacts={},backend='vamos',backend_inputs=['docs/toolchain.json'])
  with patch.object(dp,'candidate_path',side_effect=AssertionError('per-provider job I/O')):
   self.assertIn('docs/toolchain.json',dp.producer_paths(Path('.'),recipe))
  del recipe['backend_inputs']
  with self.assertRaises(FormatError):dp.producer_paths(Path('.'),recipe)

 def test_batch_generates_one_controlled_command_graph(self):
  commands=gen.commands(['a','b','relprobe','extprobe','entryprobe'],['extprobe','entryprobe']);self.assertEqual(commands,ptr.commands(['a','b','relprobe','extprobe','entryprobe']));self.assertEqual(sum('bindptr.o bindptr.asm' in c for c in commands),1)

if __name__=='__main__':unittest.main()
