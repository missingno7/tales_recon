"""Frameless admission controls. No fixture relocking or compiler output fabrication."""
import copy,json,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from analysis_support import ROOT,game
from common import FormatError
from evidence_snapshot import snapshot
import audio_frameless_asm as asm
import audio_frame_calibration as frame
import audio_driver_asm as driver
from audio_driver_objects import parse

class FramelessTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with snapshot():
   from census import verify_lock,_derive_uncached
   verify_lock(ROOT);_,files,cls.model=_derive_uncached(ROOT,False);cls.blob=files['DT1:DuckTales']
   cls.batch=asm.document(ROOT,asm.MANIFEST);cls.audit=asm.producer(ROOT,cls.batch)
   cls.control=asm.control(ROOT,cls.batch,cls.blob,cls.model)
   cls.contract=asm.derive(cls.blob,cls.model,cls.control['frame_calibration'],ROOT)
   cls.facts=[asm.document(ROOT,n) for n in asm.FACTS]
 def validate(self,f):
  return asm.validate_fact(ROOT,self.blob,self.model,self.contract,f)
 def test_exact_complete_batch_and_accounting(self):
  records=[asm.verify(ROOT,self.blob,self.model,f,self.batch,self.contract,self.audit,self.control) for f in self.facts]
  self.assertEqual(sum(r['span']['size'] for r in records),572)
  self.assertTrue(all(r['data_credit']==0 and r['category']=='RECONSTRUCTED_ASM' for r in records))
  from hybrid_image import account
  image,report=account(self.blob,self.model,asm.contributions(ROOT,[dict(r,acceptance=True) for r in records]))
  self.assertEqual(image,self.blob)
  self.assertEqual(report['totals']['RECONSTRUCTED_ASM'],572)
  self.assertEqual(report['totals']['overlap'],0)
  self.assertEqual(report['totals']['unaccounted'],0)
 def test_calibration_matrix_and_corpus(self):
  m=self.control['frame_calibration']
  self.assertGreaterEqual(m['canonical_functions'],278)
  self.assertGreaterEqual(m['canonical_categories']['behavioral_functions'],4)
  self.assertGreaterEqual(m['canonical_categories']['dead_code_functions'],2)
  self.assertEqual([x['flags'] for x in m['controls']],frame.FLAGS)
  self.assertEqual(sum(len(x['functions']) for x in m['controls']),24)
  self.assertTrue(all(r['link_a5'] for x in m['controls'] for r in x['functions']))
 def test_every_compiled_C_entry_rejected(self):
  work=ROOT/self.batch['job']/'sys/work'
  for k,opts in enumerate(frame.FLAGS):
   code,_,s=parse((work/('frame%d.o'%k)).read_bytes(),False,0x80 if opts==['+D'] else 0xc0)
   for symbol in s['symbols'][:4]:
    with self.subTest(k=k,name=symbol['name']),self.assertRaises(FormatError):
     frame.witness(frame.registers.instructions(code),symbol['offset'],[])
 def test_canonical_link_C_rejected(self):
  rows=frame.corpus(ROOT,self.blob,self.model)
  self.assertTrue(all(x['link_a5'] for x in rows))
  with self.assertRaises(FormatError):frame.witness([rows[0]['first']],rows[0]['entry'],[])
 def test_any_frameless_control_refutes_calibration(self):
  with self.assertRaises(FormatError):frame.require_framed([dict(link_a5=True),dict(link_a5=False)])
 def test_new_accepted_option_fails_closed(self):
  import compiler_oracle
  with patch.dict(compiler_oracle.PROFILES,{'future':dict(version='3.6a',flags=['+NEW'])}):
   with self.assertRaisesRegex(FormatError,'new accepted'):frame.derive(ROOT,self.blob,self.model,self.batch)
 def test_frame_on_reachable_path_rejects(self):
  items=[dict(offset=0,size=2,mnemonic='nop',operands=''),dict(offset=2,size=4,mnemonic='link.w',operands='a5, #$0'),dict(offset=6,size=2,mnemonic='rts',operands='')]
  with self.assertRaises(FormatError):frame.witness(items,0,[dict(site=0,kind='FALLTHROUGH',target=2),dict(site=2,kind='FALLTHROUGH',target=6)])
 def test_missing_rts_or_boundary_rejected(self):
  ins=[dict(offset=0,size=2,mnemonic='nop',operands='')]
  for edges in [[],[dict(site=0,kind='TAIL',target=8)],[dict(site=0,kind='TAIL',target=0)]]:
   with self.assertRaises(FormatError):frame.witness(ins,0,edges)
 def test_word_and_long_code_carriers_rejected(self):
  f=self.facts[0];src=asm.source_for(self.blob,self.model,self.contract,f['id'])[0]
  for directive in [b'dc.w $4e75',b'dc.l $4e754e75',b'incbin "carrier"',b'ds.b 10']:
   with self.assertRaises(FormatError):driver.source_policy(src.replace(b'\trts',b'\t'+directive),f)
 def test_opaque_fact_rejected(self):
  f=copy.deepcopy(self.facts[0]);f['carrier']='bytes'
  with self.assertRaises(FormatError):self.validate(f)
 def test_partial_span_rejected(self):
  f=copy.deepcopy(self.facts[0]);f['original']['end']-=2;f['original']['size']-=2
  with self.assertRaises(FormatError):self.validate(f)
 def test_stale_oracle_and_predicate_rejected(self):
  for field in ['oracle','predicate']:
   f=copy.deepcopy(self.facts[0])
   if field=='oracle':f['oracle_sha256']='0'*64
   else:f['predicate']['return_sites']=[]
   with self.assertRaises(FormatError):self.validate(f)
 def test_unnamed_or_masked_relocation_rejected(self):
  for mode in ['unnamed','masked','width','target']:
   f=copy.deepcopy(self.facts[1]);r=f['relocations'][0]
   if mode=='unnamed':r['symbol']=''
   elif mode=='masked':r['mask']=0
   elif mode=='width':r['width']=2
   else:r['addend_raw']+=2
   with self.assertRaises(FormatError):self.validate(f)
 def test_no_entry_is_not_invented(self):
  self.assertNotIn('resident_frameless_558A',asm.SPECS)
  self.assertTrue(any(x['start']==0x558a and 'NO_INDEPENDENT' in x['reason'] for x in self.contract['unclaimed']))
 def test_one_past_named_callback_has_zero_credit(self):
  f=self.facts[-1]
  self.assertEqual(f['original']['end'],0x617c)
  self.assertIn(dict(name='_end_cbwrap',offset=30,original=None),f['exports'])
  self.assertNotIn('_recon_h00_617C',[x['name'] for x in f['external_code']+f['exports']])
  self.assertEqual(f['original']['size'],30)
 def test_unavailable_supplemental_compilers_are_not_required(self):
  with tempfile.TemporaryDirectory() as d:
   with patch('repo_paths.candidate_path',return_value=Path(d)/'missing'):
    rows=frame.supplemental(ROOT)
   self.assertEqual(rows[0]['status'],'UNAVAILABLE_RETAINED_ARTIFACTS')
   self.assertFalse(rows[0]['required'])
 def test_wrong_manifest_profile_rejected(self):
  bad=copy.deepcopy(self.batch);bad['profile']='aztec50'
  with self.assertRaisesRegex(FormatError,'schema/pins'):
   asm.verify(ROOT,self.blob,self.model,self.facts[0],bad,self.contract,self.audit,self.control)
 def test_D2_stays_scratch(self):
  m=self.control['register_calibration']
  self.assertIn('d2',m['scratch']);self.assertNotIn('d2',m['callee_saved'])
  self.assertEqual(len(m['d2_counterexamples']),2)

class FrameMechanismTests(unittest.TestCase):
 def ins(self,raw):return frame.registers.instructions(bytes.fromhex(raw))
 def test_rts_and_rte_reachable_without_link(self):
  for raw in ['4e71 4e75','4e71 4e73']:
   ins=self.ins(raw);w=frame.witness(ins,0)
   self.assertEqual(w['return_sites'],[2]);self.assertFalse(w['stack_frame'])
 def test_cfg_cannot_hide_link_edge_or_invent_return(self):
  ins=self.ins('4e71 4e55 0000 4e75')
  with self.assertRaisesRegex(FormatError,'edges do not rederive'):
   frame.witness(ins,0,[dict(site=0,kind='TAIL',target=6)])
  with self.assertRaisesRegex(FormatError,'gained frame'):frame.witness(ins,0)
 def test_unknown_computed_transfer_and_unreachable_tail_reject(self):
  for raw in ['4ed0','4e90 4e75','4e75 4e71','6002 4e71 4e75']:
   with self.subTest(raw=raw),self.assertRaises(FormatError):frame.witness(self.ins(raw),0)
 def test_closed_loop_without_return_rejects(self):
  with self.assertRaisesRegex(FormatError,'no RTS/RTE'):frame.witness(self.ins('60fe'),0)
 def test_frameless_bound_canonical_body_refutes_corpus(self):
  from common import sha256,json_bytes
  from audio_sequence_data import payload
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for folder in ['recovery','src','evidence/functions']:(root/folder).mkdir(parents=True,exist_ok=True)
   for raw,accepted in [('4e55 0000 4e5d 4e75',True),('4e71 4e71 4e75',False)]:
    body=bytes.fromhex(raw);source=b'int recovered() { return 0; }\n'
    extent=dict(hunk=0,start=0,end=len(body),size=len(body),sha256=sha256(body))
    proof=json_bytes(dict(id='synthetic',comparison=dict(verdict='EQUAL',relocation_equal=True,normalized_sha256=sha256(body))))
    item=dict(evidence_extent=extent,source='src/control.c',source_sha256=sha256(source),proof='recovery/control.json',proof_sha256=sha256(proof))
    (root/'src/control.c').write_bytes(source);(root/'recovery/control.json').write_bytes(proof)
    (root/'recovery/ledger.json').write_bytes(json_bytes(dict(functions=dict(synthetic=item))))
    (root/'evidence/functions/ledger.json').write_bytes(json_bytes(dict(functions=[])))
    model=dict(hunks=[dict(number=0,content_offset=0,initialized_size=len(body))])
    if accepted:self.assertTrue(frame.corpus(root,body,model)[0]['link_a5'])
    else:
     with self.assertRaises(FormatError):frame.corpus(root,body,model)
 def test_supported_aj_models_are_explicit(self):
  with self.assertRaisesRegex(FormatError,'unmeasured AJ'):parse(b'',False,0)

if __name__=='__main__':unittest.main()
