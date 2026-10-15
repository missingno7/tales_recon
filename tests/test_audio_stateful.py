"""Stateful bytecode forms, independently decoded cursor/state cases."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE/'tools'))
from analysis_support import ROOT
from census import _derive_uncached
from common import FormatError,json_bytes,sha256
import audio_stateful_catalogue as t
import audio_stateful_provider as p
import audio_region_catalogue as old
class StatefulTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  _,files,cls.model=_derive_uncached(ROOT,False);cls.blob=files['DT1:DuckTales'];cls.g=t.contract(cls.blob,cls.model);cls.fact=p.doc(ROOT,p.FACT);cls.batch=p.doc(ROOT,p.MANIFEST);cls.layout=t.discover(ROOT,cls.blob,cls.model,cls.g)
 def test_exact_stateful_provider_and_named_selector_export(self):
  if p.previous.IDENT not in p.doc(ROOT,'recovery/ledger.json').get('code_data_providers',{}):
   with self.assertRaisesRegex(FormatError,'batch0003 must be canonical'):p.verify(ROOT,self.blob,self.model,self.fact,self.batch)
   return
  r=p.verify(ROOT,self.blob,self.model,self.fact,self.batch)
  self.assertEqual((r['typed_bytes'],r['total_proved_bytes'],r['support_bytes']),(1379,4017,2638));self.assertEqual(len(r['roots']),172);self.assertEqual(len(r['blocked_selectors']),4)
  self.assertEqual([(e['symbol'],e['hunk'],e['offset']) for e in r['exports']],[('_G_h00_6200',0,0x6200)])
  self.assertEqual((r['c_bytes'],r['asm_instruction_bytes'],r['padding_credit']),(0,0,0))
 def test_grammar_never_reads_region_bytes(self):
  b=bytearray(self.blob);base=self.model['hunks'][0]['content_offset'];b[base+0x5e6c:base+0x704e]=bytes(4578)
  self.assertEqual(t.contract(bytes(b),self.model),self.g)
 def test_lookahead_forms_derived_for_both_parities_and_alias_93(self):
  for p0 in (4,5):
   for op in (0x93,0x9a):
    for look in (7,0xa7):
     code=bytearray(32);code[p0]=op;code[p0+1]=3;word=(p0+3)&~1;code[word:word+2]=b'\x12\x34';code[word+2]=look;sh=t.stream_form(self.g,code,p0);name=sh['command']
     self.assertEqual(sh['length'],word+2-p0+(look!=0xa7));self.assertEqual(t.read_values(code,p0,name,sh),[3,0x1234]+([] if look==0xa7 else [look]));self.assertEqual(name.endswith('WAIT'),look==0xa7)
 def test_a7_has_one_byte_lexical_extent_for_every_state(self):
  cases=[c for c in self.g['stateful']['cases'] if c['opcode']==0xa7];self.assertEqual(len(cases),4);self.assertEqual({c['length'] for c in cases},{1})
  self.assertEqual({c['saved_cursor'] for c in cases if c['sample_state']=='NONZERO'},{0});self.assertEqual({c['next'] for c in cases if c['sample_state']=='ZERO'},{1})
 def test_9b_is_modelled_but_unproved_state_rejects(self):
  self.assertEqual(self.g['stateful']['conditional_9b']['active'],'STOP_WITHOUT_OPERANDS')
  with self.assertRaisesRegex(FormatError,'independently proved zero'):t.stream_form(self.g,bytes([0x9b,1,2,3,4,5]),0)
 def test_accepted_batch3_grammar_stays_rejected(self):
  for op in (0x93,0x9a,0x9b,0xa7):
   with self.subTest(op=op),self.assertRaises(FormatError):old.form(self.g,op,0)
 def test_unknown_opcodes_still_reject(self):
  for op in (0xac,0xff,0xa1):
   with self.subTest(op=op),self.assertRaises(FormatError):t.stream_form(self.g,bytes([op,0,0,0]),0)
 def test_period_and_duration_ranges_are_typed(self):
  for row in [dict(offset=0,type='SAMPLE_TIMED',values=[1,65536,1]),dict(offset=0,type='SAMPLE_TIMED',values=[1,12,0xa7]),dict(offset=0,type='SAMPLE_WAIT',values=[256,12]),dict(offset=0,type='SAMPLE_WAIT',values=[1,-1]),dict(offset=0,type='SAMPLE_WAIT',values=[True,12])]:
   with self.subTest(row=row),self.assertRaises(FormatError):t.check(row)
 def test_period_is_not_raw_word_carrier(self):
  for name in ('dc.w','WORDS','RAW_SAMPLE'):
   with self.subTest(name=name),self.assertRaises(FormatError):t.check(dict(offset=0,type=name,values=[0x1234]))
 def test_nonzero_alignment_byte_rejects(self):
  code=bytearray([0]*16);code[5:11]=bytes([0x9a,3,1,0x12,0x34,7]);sh=t.stream_form(self.g,code,5)
  with self.assertRaisesRegex(FormatError,'alignment'):t.read_values(code,5,sh['command'],sh)
 def test_partial_sample_lookahead_rejects(self):
  for raw in (b'\x9a',b'\x9a\x01\0\1'):
   with self.subTest(raw=raw),self.assertRaisesRegex(FormatError,'partial'):t.stream_form(self.g,raw,0)
 def test_wait_lookahead_is_followed_as_command(self):
  rows={c['offset']:c for c in self.layout['rows']}
  waits=[c for c in rows.values() if c['type']=='SAMPLE_WAIT'];self.assertEqual(len(waits),50)
  for c in waits:self.assertEqual(rows[c['offset']+t.length(c,self.g)]['type'],'WAIT_SAMPLE')
 def test_rederived_lookahead_predicate_change_fails(self):
  b=bytearray(self.blob);base=self.model['hunks'][0]['content_offset'];b[base+0x5c5d]^=1
  with self.assertRaises(FormatError):t.contract(bytes(b),self.model)
 def test_rederived_rewind_change_fails(self):
  b=bytearray(self.blob);base=self.model['hunks'][0]['content_offset'];b[base+0x5c7c:base+0x5c7e]=b'\x4e\x71'
  with self.assertRaises(FormatError):t.contract(bytes(b),self.model)
 def test_handler_binding_change_stales_every_new_stream(self):
  model=copy.deepcopy(self.model);r=next(r for r in model['relocations'] if r['source_hunk']==1 and r['source_offset']==0x292e+4*(0xa7-0x80));r['addend_raw']=0x5d92
  with self.assertRaises(FormatError):t.contract(self.blob,model)
 def test_support_subtraction_has_zero_overlap(self):
  full={q for o in self.fact['objects'] for p0 in o['parts'] for q in range(p0['original_start'],p0['original_end'])};new={q for o in self.fact['objects'] for p0 in o['credit_parts'] for q in range(p0['original_start'],p0['original_end'])};support={q for o in self.fact['objects'] for p0 in o['support_parts'] for q in range(p0['original_start'],p0['original_end'])}
  self.assertFalse(new&support);self.assertEqual(full,new|support);self.assertEqual((len(new),len(support)),(1379,2638))
 def test_fabricated_support_credit_is_recomputed(self):
  objects=t.plan(self.layout,self.g);prior=p.doc(ROOT,p.previous.FACT);p.partition(objects,prior)
  self.assertEqual([o['credit_parts'] for o in objects],[o['credit_parts'] for o in self.fact['objects']])
 def test_h1_pointers_still_have_no_admission(self):
  self.assertEqual({x['entry'] for x in self.layout['blocked_selectors']},{0x19e8,0x1b41,0x1bcd,0x1cf1});self.assertTrue(all(x['target_hunk']==1 for x in self.layout['blocked_selectors']))
 def test_zero_credit_support_object_is_fully_retained(self):
  o=next(o for o in self.fact['objects'] if o['credit_bytes']==0);self.assertGreater(o['typed_bytes'],0);self.assertTrue(o['support_parts'])
 def test_public_symbol_is_assembled_not_an_equ(self):
  source=b'\n'.join(p.canonical_path(ROOT,o['candidate']).read_bytes() for o in self.fact['objects']);self.assertIn(b'\tpublic _G_h00_6200\n',source);self.assertIn(b'\n_G_h00_6200:\n',source);self.assertNotIn(b' equ ',source)
 def test_packed_control_bounds_cover_every_object(self):
  for o in self.fact['objects']:
   raw=(ROOT/self.batch['job']/('sys/work/'+o['prefix']+'.o')).read_bytes();self.assertLessEqual(int.from_bytes(raw[22:24],'big'),202)
 def test_no_raw_asm_instruction_credit(self):
  source=b'\n'.join(p.canonical_path(ROOT,o['candidate']).read_bytes() for o in self.fact['objects']);self.assertNotIn(b'\tmove.',source);self.assertIn(b'dc.w \\2',source)

class IdentityFixtureTests(unittest.TestCase):
 def test_missing_fixture_ledger_is_an_unadmitted_provider(self):
  import tempfile,os
  with tempfile.TemporaryDirectory(dir=os.environ.get('AUDIO_TEST_TMP')) as folder:
   root=Path(folder);identity=p.input_identity(root)
   self.assertEqual(identity,{str(root/p.FACT):None,str(root/p.MANIFEST):None})

if __name__=='__main__':unittest.main()
