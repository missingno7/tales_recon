"""Calibrated callback predicates and exact reconstructed ASM producer controls."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE/'tools'))
from analysis_support import ROOT
from census import _derive_uncached
from common import FormatError,json_bytes,sha256
import audio_callback_asm as p
import audio_driver_asm as old
from audio_driver_objects import parse
class CallbackTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  _,fs,cls.model=_derive_uncached(ROOT,False);cls.blob=fs['DT1:DuckTales'];cls.batch=p.document(ROOT,p.MANIFEST);cls.audit=p.producer(ROOT,cls.batch);cls.control=p.control(ROOT,cls.batch,cls.blob,cls.model);cls.contract=p.derive(cls.blob,cls.model,cls.control['register_calibration']);cls.facts=[p.document(ROOT,n) for n in p.FACTS];cls.reports=[p.verify(ROOT,cls.blob,cls.model,f,cls.batch,cls.contract,cls.audit,cls.control) for f in cls.facts]
 def test_both_members_complete_exact_code_only(self):
  self.assertEqual([r['span']['size'] for r in self.reports],[36,96]);self.assertEqual(sum(len(r['named_relocation_bindings']) for r in self.reports),9);self.assertTrue(all(r['data_credit']==0 for r in self.reports))
 def test_wrapper_30_bytes_has_no_inherited_eligibility(self):
  self.assertEqual(self.contract['unclaimed'][0]['start'],0x615e);self.assertEqual(self.contract['unclaimed'][0]['end'],0x617c);self.assertNotIn(0x615e,{v['start'] for v in p.SPECS.values()})
 def test_real_pc_lea_callback_anchor(self):
  self.assertEqual(self.contract['caller_callback'],dict(site=0x52d0,target=0x615e,store=0x52d4))
 def test_shared_return_and_copy_entries_are_named(self):
  exports={e['original']:e['name'] for f in self.facts for e in f['exports'] if e['original'] is not None};self.assertIn(0x619e,exports);self.assertIn(0x61a0,exports)
 def test_unstacked_a1_call_argument_is_rederived(self):
  predicate=self.facts[0]['predicate'];self.assertEqual((predicate['call'],predicate['callee_use']),(0x619c,0x61f0));self.assertTrue(predicate['no_stack_arguments'])
 def test_d7_and_a2_are_measured_preserved_d2_is_scratch(self):
  c=self.control['register_calibration'];self.assertIn('d7',c['callee_saved']);self.assertIn('a2',c['callee_saved']);self.assertIn('d2',c['scratch']);self.assertNotIn('d2',c['callee_saved'])
 def test_stale_or_counterexample_calibration_rejects(self):
  c=copy.deepcopy(self.control['register_calibration']);c['observations']['d7']['unsaved']+=1
  with self.assertRaises(FormatError):p.derive(self.blob,self.model,c)
 def test_callback_root_change_fails(self):
  model=copy.deepcopy(self.model);r=next(r for r in model['relocations'] if r['source_hunk']==1 and r['source_offset']==0x2bc2);r['addend_raw']=0x61a0
  with self.assertRaisesRegex(FormatError,'shared return'):p.derive(self.blob,model,self.control['register_calibration'])
 def test_a1_argument_consumer_change_fails(self):
  b=bytearray(self.blob);base=self.model['hunks'][0]['content_offset'];b[base+0x61f0:base+0x61f2]=b'\x4e\x71'
  with self.assertRaises(FormatError):p.derive(bytes(b),self.model,self.control['register_calibration'])
 def test_partial_masked_or_stale_fact_rejects(self):
  for kind in ('extent','predicate','relocation','mask','oracle'):
   f=copy.deepcopy(self.facts[1])
   if kind=='extent':f['original']['end']-=2
   elif kind=='predicate':f['predicate']['c_compatible']=True
   elif kind=='relocation':f['relocations'][0]['width']=2
   elif kind=='mask':f['mask']='ffffffff'
   else:f['oracle_sha256']='0'*64
   with self.subTest(kind=kind),self.assertRaises(FormatError):p.validate_fact(ROOT,self.blob,self.model,self.contract,f)
 def test_raw_word_long_and_filler_carriers_reject(self):
  for raw in (b'\tdc.w $4e75\n',b'\tdc.l 0\n',b'\tds.b 96\n',b'\tincbin "x"\n'):
   with self.subTest(raw=raw),self.assertRaises(FormatError):old.source_policy(raw,self.facts[1])
 def test_complete_aj_hidden_section_or_trailer_reject(self):
  raw=(ROOT/self.batch['job']/'sys/work/cbcopy.o').read_bytes();altered=bytearray(raw);altered[14]=1
  with self.assertRaises(FormatError):parse(bytes(altered))
  with self.assertRaises(FormatError):parse(raw+bytes(4))
 def test_new_contributions_are_source_derived(self):
  parts=p.contributions(ROOT,[dict(r,acceptance=True) for r in self.reports]);self.assertEqual(sum(len(x['bytes']) for x in parts),132)
  for part,report in zip(parts,self.reports):self.assertEqual(sha256(part['bytes']),report['span']['sha256'])
 def test_whole_hybrid_overlap_free_for_both_members(self):
  from hybrid_image import account
  parts=p.contributions(ROOT,[dict(r,acceptance=True) for r in self.reports]);image,report=account(self.blob,self.model,parts);self.assertEqual(image,self.blob);self.assertEqual(report['totals']['RECONSTRUCTED_ASM'],132);self.assertEqual(report['totals']['overlap'],0)
 def test_batch2_command_graph_remains_unchanged(self):
  batch=old.document(ROOT,old.MANIFEST);request=json.loads((ROOT/batch['job']/'request.json').read_bytes());self.assertEqual(old.commands(),[x['command'] for x in request['steps']]);self.assertEqual(len(old.FACTS),8)
 def test_batch3_and_batch2_facts_are_distinct(self):
  self.assertFalse(set(old.FACTS)&set(p.FACTS));self.assertNotEqual(old.MANIFEST,p.MANIFEST)
 def test_producer_pin_drift_fails(self):
  b=copy.deepcopy(self.batch);b['receipt_sha256']='0'*64
  with self.assertRaisesRegex(FormatError,'SHA pins'):p.producer(ROOT,b)
 def test_absent_optional_inputs(self):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:self.assertEqual(list(p.input_identity(Path(tmp)).values()),[None])
 def test_failed_shared_gate_never_publishes(self):
  import promote_callback_asm as promote,check_function,evidence_snapshot,analysis_support
  from contextlib import nullcontext
  with patch.object(sys,'argv',['promote_callback_asm','--promote']),patch.object(promote,'ledger_lock',lambda p:nullcontext()),patch.object(promote,'stage',return_value=[]),patch.object(check_function,'regression_receipt',return_value={'passed':False}),patch.object(evidence_snapshot.Snapshot,'inputs',return_value={}),patch.object(analysis_support,'game',return_value=(self.blob,self.model,None)),patch.object(promote,'publish') as publish:
   with self.assertRaisesRegex(FormatError,'passing shared regression'):promote.main()
   publish.assert_not_called()

if __name__=='__main__':unittest.main()
