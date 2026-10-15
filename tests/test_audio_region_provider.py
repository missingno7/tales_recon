"""Typed region controls; no writes to canonical source or producer jobs."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE/'tools'))
from analysis_support import ROOT
from census import _derive_uncached
from common import FormatError,sha256,json_bytes
from audio_sequence_data import payload
import audio_region_catalogue as t
import audio_region_provider as p
import promote_code_data as promote

class AudioRegionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  _,files,cls.model=_derive_uncached(ROOT,False);cls.blob=files['DT1:DuckTales'];cls.code=payload(cls.blob,cls.model,0);cls.fact=p.doc(ROOT,p.FACT);cls.batch=p.doc(ROOT,p.MANIFEST);cls.g=t.contract(cls.blob,cls.model);cls.layout=t.discover(ROOT,cls.blob,cls.model,cls.g)
 def test_exact_complete_typed_region(self):
  r=p.verify(ROOT,self.blob,self.model,self.fact,self.batch)
  self.assertEqual((r['typed_bytes'],len(r['objects']),r['named_relocations']),(2638,10,200));self.assertEqual((r['c_bytes'],r['asm_instruction_bytes'],r['padding_credit']),(0,0,0));self.assertEqual(r['packed_index_control']['max_index'],201)
 def test_types_do_not_read_any_region_bytes(self):
  b=bytearray(self.blob);o=self.model['hunks'][0]['content_offset'];b[o+0x5e6c:o+0x704e]=bytes(4578)
  self.assertEqual(t.contract(bytes(b),self.model),self.g)
 def test_four_state_dependent_opcodes_reject(self):
  for op in (0x93,0x9a,0x9b,0xa7):
   with self.subTest(op=op),self.assertRaises(FormatError):t.form(self.g,op,0)
 def test_unreviewed_and_unknown_opcodes_reject(self):
  for op in (0x8a,0xa1,0xac,0xff):
   with self.subTest(op=op),self.assertRaises(FormatError):t.form(self.g,op,1)
 def test_new_fixed_handlers_have_independent_consumption(self):
  for op in t.NEW:
   for parity in (0,1):self.assertEqual(t.form(self.g,op,parity)['length'],1 if op==0x92 else 2)
 def test_selector_extent_is_accepted_trigger_access(self):
  self.assertEqual(self.layout['selector_extent_basis'],[dict(offset=0x19c1,command='TRIGGER',operands=dict(identifier=175))]);self.assertEqual(len(self.layout['roots'])+len(self.layout['blocked_selectors']),176)
 def test_h1_targets_and_state_dependent_streams_stay_unproved(self):
  blocked=self.layout['blocked_selectors'];self.assertEqual(sum(x['target_hunk']==1 for x in blocked),4);self.assertEqual(sum('0x9A' in x['reason'] for x in blocked),53)
 def test_negative_ramp_zero_is_terminal(self):
  views=[v for v in self.layout['envelope_views'] if v['steps'][-1]['command']=='RAMP_DOWN_END'];self.assertTrue(views)
  for v in views:
   last=v['steps'][-1]['offset'];self.assertEqual(v['end'],last+2);self.assertGreaterEqual(self.code[last],128);self.assertEqual(self.code[last+1],0)
 def test_shared_envelope_fields_count_once(self):
  rows=[c for c in self.layout['rows'] if c['type']=='ENVELOPE_FIELD'];self.assertEqual(len(rows),len({c['offset'] for c in rows}));self.assertTrue(any(len(c['roles'])>1 for c in rows))
 def test_real_code_is_not_typed_data(self):
  points={q for c in self.layout['rows'] for q in range(c['offset'],c['offset']+t.length(c,self.g))};self.assertFalse(points.intersection(range(0x615e,0x6200)));self.assertIn(dict(start=0x615e,end=0x6200,reason='EXECUTABLE_CODE_SEPARATE_INSTRUCTION_ROUTE'),self.layout['unproved_intervals'])
 def test_measured_operand_ranges(self):
  for row in [dict(offset=0,type='NOTE',values=[128,0]),dict(offset=0,type='HEADER',values=[4,0]),dict(offset=0,type='ENV_INITIAL',values=[0]),dict(offset=0,type='ENVELOPE_FIELD',roles=['DELAY'],values=[0]),dict(offset=0,type='ENVELOPE_FIELD',roles=['ZERO'],values=[1])]:
   with self.subTest(row=row),self.assertRaises(FormatError):t.check(row)
  for value in (-1,256,True):
   with self.subTest(value=value),self.assertRaises(FormatError):t.check(dict(offset=0,type='FLAGS',values=[value]))
 def test_raw_carrier_and_masked_fields(self):
  for row in [dict(offset=0,type='RAW',values=[0]),dict(offset=0,type='ENVELOPE_FIELD',roles=[],values=[0]),dict(offset=0,type='NOTE',values=[1,2],mask=255)]:
   with self.subTest(row=row),self.assertRaises(FormatError):t.check(row)
 def test_unnamed_pointer_rejects(self):
  for value in ('1234','_unproved','_audio3_c_704e',0):
   with self.subTest(value=value),self.assertRaises(FormatError):t.check(dict(offset=0,type='CALL',values=[value]))
 def test_wrong_grammar_length_rejects_encoding(self):
  g=copy.deepcopy(self.g);op=next(x for x in g['score']['opcodes'] if x['opcode']==0x81)
  for f in op['forms']:f['length']+=1
  member=next(o for o in self.fact['objects'] if any(c['type']=='LOOP' for c in o['rows']))
  with self.assertRaisesRegex(FormatError,'parity/length'):t.encode(member,g)
 def test_pointer_to_unproved_stream_blocks_entire_root(self):
  model=copy.deepcopy(self.model);binding=next(b for b in self.layout['bindings'] if b['source_offset']>=0x64c0);rr=next(r for r in model['relocations'] if r['source_hunk']==0 and r['source_offset']==binding['source_offset']);rr['addend_raw']=0x615e
  layout=t.discover(ROOT,self.blob,model,self.g);self.assertLess(layout['typed_bytes'],self.layout['typed_bytes']);self.assertNotIn(binding['source_offset'],[b['source_offset'] for b in layout['bindings']])
 def test_unknown_stream_opcode_does_not_retain_prefix(self):
  root=next(r for r in self.layout['roots'] if not r['canonical']);blob=bytearray(self.blob);base=self.model['hunks'][0]['content_offset'];blob[base+root['entry']+2]=255
  layout=t.discover(ROOT,bytes(blob),self.model,self.g);self.assertNotIn(root['index'],[r['index'] for r in layout['roots']]);self.assertLess(layout['typed_bytes'],self.layout['typed_bytes'])
 def test_handler_binding_stales_every_object(self):
  model=copy.deepcopy(self.model);rr=next(r for r in model['relocations'] if r['source_hunk']==1 and r['source_offset']==0x292e+4*(0x9a-0x80));rr['addend_raw']=0x5dac
  for o in self.fact['objects']:
   with self.subTest(member=o['prefix']),self.assertRaisesRegex(FormatError,'every region stream'):p.validate(ROOT,self.blob,model,self.fact)
 def test_envelope_dispatch_binding_changes_contract(self):
  model=copy.deepcopy(self.model);rr=next(r for r in model['relocations'] if r['source_hunk']==1 and r['source_offset']==0x2b82);rr['addend_raw']=0x5514
  with self.assertRaisesRegex(FormatError,'state handler binding'):t.contract(self.blob,model)
 def test_stale_grammar_and_extra_fact_mask_reject(self):
  for mutate in ('contract_sha256','mask'):
   fact=copy.deepcopy(self.fact);fact[mutate]='0'*64
   with self.subTest(mutate=mutate),self.assertRaises(FormatError):p.validate(ROOT,self.blob,self.model,fact)
 def test_partial_stream_or_guessed_gap_reject(self):
  for mutate in ('partial','gap'):
   fact=copy.deepcopy(self.fact)
   if mutate=='partial':fact['objects'][0]['rows'].pop()
   else:fact['objects'][0]['rows'].append(dict(offset=0x615e,type='NOTE',values=[1,2]))
   with self.subTest(mutate=mutate),self.assertRaisesRegex(FormatError,'partial stream'):p.validate(ROOT,self.blob,self.model,fact)
 def test_raw_source_carrier_rejects(self):
  original=p.canonical_path;name=self.fact['objects'][0]['candidate'];raw=original(ROOT,name).read_bytes()+b'\tdc.b 0\n'
  class Carrier:
   def read_bytes(self):return raw
  with patch.object(p,'canonical_path',side_effect=lambda root,n:Carrier() if n==name else original(root,n)),self.assertRaisesRegex(FormatError,'raw carrier'):p.validate(ROOT,self.blob,self.model,self.fact)
 def test_object_complete_structure_negative_controls(self):
  o=self.fact['objects'][0];sem=t.encode(o,self.g);targets={b['symbol'] for b in self.layout['bindings']};defs=p.definition_plan(o,sem,targets);raw=(ROOT/self.batch['job']/('sys/work/'+o['prefix']+'.o')).read_bytes();syms=int.from_bytes(raw[28:30],'big')*4
  for label,pos,val in [('section',14,1),('symbolkind',syms,7),('token',36,0xfe),('trailer',syms-1,1)]:
   altered=bytearray(raw);altered[pos]=val
   with self.subTest(control=label),self.assertRaises(FormatError):p.object_code(bytes(altered),o['CODE'],o['typed_bytes'],defs,sem['fixups'])
 def test_canonical_replay_requires_shared_gate(self):
  with patch.object(promote,'stage',return_value=({},{})),self.assertRaisesRegex(FormatError,'shared regression'):promote.gated(ROOT,b'',{}, {},lambda:dict(passed=False),lambda:{},p.MANIFEST)
 def test_regression_drift_blocks_region_promotion(self):
  values=iter([{'x':1},{'x':2}])
  with patch.object(promote,'stage',return_value=({},{})),self.assertRaisesRegex(FormatError,'inputs changed'):promote.gated(ROOT,b'',{}, {},lambda:dict(passed=True),lambda:next(values),p.MANIFEST)
 def test_fresh_replay_is_mandatory_for_new_manifest(self):
  with patch.object(promote,'stage',side_effect=[({},{}),({},{'changed':1})]),self.assertRaisesRegex(FormatError,'exact replay changed'):promote.gated(ROOT,b'',{}, {},lambda:dict(passed=True),lambda:{},p.MANIFEST)
 def test_successful_gate_preserves_manifest(self):
  with patch.object(promote,'stage',return_value=({},{})) as stage:self.assertEqual(promote.gated(ROOT,b'',{}, {},lambda:dict(passed=True),lambda:{},p.MANIFEST),({},{},dict(passed=True)))
  self.assertEqual(stage.call_count,2);self.assertEqual(stage.call_args.args[-1],p.MANIFEST)

if __name__=='__main__':unittest.main()
