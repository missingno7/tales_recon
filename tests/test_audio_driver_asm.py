"""Audio batch0002: source/ABI, full AJ, binding and publication controls."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from common import FormatError,sha256,json_bytes
from census import verify_lock,_derive_uncached
from audio_sequence_data import payload
import audio_driver_asm as a
import audio_driver_contracts as c
from audio_driver_objects import parse

class DriverASMTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  verify_lock(ROOT);_,fs,cls.model=_derive_uncached(ROOT,False);cls.blob=fs['DT1:DuckTales'];cls.batch=a.document(ROOT,a.MANIFEST);cls.audit=a.producer(ROOT,cls.batch);cls.control=a.control(ROOT,cls.batch,cls.blob,cls.model);cls.calibration=cls.control['register_calibration'];cls.contract=c.derive(cls.blob,cls.model,cls.calibration)
  cls.facts=[a.document(ROOT,n) for n in a.FACTS];cls.rows=[a.verify(ROOT,cls.blob,cls.model,f,cls.batch,cls.contract,cls.audit,cls.control) for f in cls.facts]
 def test_complete_eight_object_batch_exact(self):
  self.assertEqual([r['span']['size'] for r in self.rows],[318,42,132,232,626,174,8,218]);self.assertEqual(sum(r['span']['size'] for r in self.rows),1750)
  self.assertTrue(all(r['data_credit']==0 and r['object_structure']['DATA']==r['object_structure']['BSS']==r['object_structure']['COMMON']==0 for r in self.rows))
 def test_all44_handlers_have_named_exported_exact_targets(self):
  exports={e['original']:e['name'] for f in self.facts for e in f['exports'] if e['original'] is not None}
  for e in self.contract['handler_table']:self.assertEqual(exports[e['addend_raw']],a.code_symbol(e['addend_raw']))
  self.assertEqual(len(self.contract['handler_table']),44)
 def test_dispatch_every_boundary_edge_and_off_by_one(self):
  es=self.contract['boundary_edges'];self.assertEqual(len(es),48);self.assertEqual(sum(e['kind']=='HANDLER_JUMP_NO_NEW_FRAME' for e in es),44)
  self.assertEqual(sum(e['kind']=='INDEX44_ADJACENT_PERIOD_DATA_UNPROVED' for e in es),1)
  b=self.contract['index_bound'];self.assertEqual((b['inclusive_limit'],b['proved_slots'],b['index44_field']),(44,44,0x29de));self.assertFalse(b['invented_slot'])
 def test_compiled_c_dispatcher_rejected_by_every_predicate(self):
  self.assertEqual(self.control['verdict'],'C_COMPATIBLE_DISPATCHER_REJECTED');self.assertTrue(self.control['has_stack_frame'] and self.control['indirect_call'])
  self.assertFalse(any(self.control['rejected_predicates'].values()))
 def test_c_compatible_store_wrappers_and_stack_entry_reject(self):
  raw=payload(self.blob,self.model,0)
  for lo,hi in [(0x558a,0x5594),(0x5594,0x559e),(0x5428,0x544c)]:
   with self.subTest(start=lo):self.assertFalse(any(c.control_rejections(c.decode(raw[lo:hi],lo),self.calibration).values()))
 def test_irq_routines_have_no_inherited_non_c_eligibility(self):
  raw=payload(self.blob,self.model,0)
  for lo,hi in [(0x55d6,0x5646),(0x5646,0x56b6),(0x56b6,0x5726),(0x5726,0x5796)]:
   self.assertFalse(any(c.control_rejections(c.decode(raw[lo:hi],lo),self.calibration).values()));self.assertNotIn(lo,{s['start'] for s in self.contract['spans']})
 def test_saved_a4_and_stream_rewind_are_rederived(self):
  p=next(f for f in self.facts if f['prefix']=='dispatch')['predicate'];self.assertEqual(p['saved_a4_record_consumer']['reads'],[2,2,4]);self.assertIn(0x5b20,p['rewind_sites']);self.assertTrue(p['shared_tail_edges'])
  witness=self.contract['dispatch_non_c'];self.assertEqual((witness['channel_argument'],witness['first_channel_read'],witness['return_site']),('A0',0x5a72,0x5a70));self.assertNotIn('bank',witness)
 def test_register_preservation_is_measured_from_corpus_and_controls(self):
  cal=self.calibration
  self.assertEqual(cal['callee_saved'],['a2','a3','d4','d5','d6','d7'])
  self.assertEqual(cal['scratch'],['a0','a1','d0','d1','d2'])
  self.assertEqual(cal['unmeasured'],['a4','d3'])
  # Counts grow with the canonical corpus; the classification may not change.
  self.assertEqual(cal['observations']['d2']['preserved'],0);self.assertGreaterEqual(cal['observations']['d2']['unsaved'],11)
  self.assertEqual(cal['observations']['d7']['unsaved'],0);self.assertGreaterEqual(cal['observations']['d7']['preserved'],2)
  self.assertEqual(set(cal['d2_counterexamples']),{'resident_F_31AA','ov08_F_1F4C'})
 def test_d2_canonical_counterexamples_never_establish_non_c_bank(self):
  import audio_register_calibration as cal
  for record in self.calibration['d2_counterexamples'].values():
   instruction=record['instruction']
   self.assertFalse(c.control_rejections([instruction],self.calibration)['unpreserved_nonvolatile_bank'])
  with self.assertRaisesRegex(FormatError,'not measured'):cal.require_preserved(self.calibration,'d2')
  # Aztec uses a pop to discard an argument into D2, without an entry save.
  pop=[dict(offset=0,size=2,mnemonic='move.l',operands='(a7)+, d2'),dict(offset=2,size=2,mnemonic='rts',operands='')]
  self.assertEqual(cal.observation(pop)['unsaved'],['d2'])
 def test_missing_stale_or_counterexample_calibration_fails_closed(self):
  import audio_register_calibration as cal
  with self.assertRaisesRegex(FormatError,'rederived calibration'):c.derive(self.blob,self.model,None)
  broken=copy.deepcopy(self.calibration);broken['observations']['d7']['unsaved']=1
  with self.assertRaisesRegex(FormatError,'stale register'):c.derive(self.blob,self.model,broken)
  broken['callee_saved'],broken['scratch'],broken['unmeasured']=cal.classification(broken['observations'])
  with self.assertRaisesRegex(FormatError,'not measured'):c.derive(self.blob,self.model,broken)
 def test_four_and_six_register_controls_rederive_d7_save_restore(self):
  for control in self.calibration['controls']:
   self.assertIn('d7',control['saved']);self.assertIn('d7',control['paired']);self.assertIn('d7',control['preserved']);self.assertNotIn('d7',control['unsaved'])
   self.assertEqual(control['DATA'],0);self.assertTrue(control['d7_live_across_named_c_call']['definition']<control['d7_live_across_named_c_call']['call']<control['d7_live_across_named_c_call']['use']);self.assertFalse(any(control['predicate_rejections'].values()))
  # Both independent compiled shapes supply D7 on top of any canonical C witnesses.
  self.assertEqual(sum('d7' in x['preserved'] for x in self.calibration['controls']),
                   self.calibration['observations']['d7']['preserved']-self.calibration['canonical_observations']['d7']['preserved'])
 def test_envelope_and_dispatch_have_no_d2_preservation_premise(self):
  env=self.facts[0]['predicate'];self.assertEqual(env['kind'],'CALLER_SUPPLIED_A0_CHANNEL_REGISTER_ARGUMENT_ENTRY')
  self.assertEqual((env['first_parameter_read'],env['caller']),(0x544c,0x5936));self.assertFalse(env['stack_argument_fetch'] or env['stack_argument_push'])
  self.assertTrue(env['d2_preservation_is_not_a_witness'])
  self.assertNotIn('D2',self.contract['dispatch_non_c']['kind'])
  update=self.facts[3]['predicate'];self.assertTrue(update['preservation_premise']['measured']);self.assertEqual(update['preservation_premise']['register'],'d7');self.assertEqual((update['final_d7_long'],update['final_d7_word']),(0xffff,-1))
 def test_calibration_rejects_changed_canonical_c_proof(self):
  import audio_register_calibration as cal
  owner=a.document(ROOT,'recovery/ledger.json')['functions']['resident_F_31AA']
  path=ROOT/owner['proof'];original=Path.read_bytes
  def read(p):return original(p)+b' ' if p==path else original(p)
  with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(FormatError,'canonical C source/proof binding'):
   cal.derive(ROOT,self.blob,self.model,self.batch)
 def test_partial_stale_and_masked_facts_reject(self):
  original=self.facts[4]
  for kind in ['partial','oracle','predicate','edge','mask','unnamed','width','type','target']:
   f=copy.deepcopy(original)
   if kind=='partial':f['original']['end']-=2;f['original']['size']-=2
   elif kind=='oracle':f['oracle_sha256']='0'*64
   elif kind=='predicate':f['predicate']['c_compatible']=True
   elif kind=='edge':f['boundary_edges'].pop()
   elif kind=='mask':f['relocations'][0]['mask']='ffffffff'
   elif kind=='unnamed':f['relocations'][0]['symbol']=''
   elif kind=='width':f['relocations'][0]['width']=2
   elif kind=='type':f['relocations'][0]['type']='HUNK_RELOC16'
   else:f['relocations'][0]['addend_raw']+=4
   with self.subTest(kind=kind),self.assertRaises(FormatError):a.validate_fact(ROOT,self.blob,self.model,self.contract,f)
 def test_dc_ds_incbin_and_opaque_carriers_reject_even_rehashed(self):
  for raw in [b'\tdc.w $4e75\n',b'\tdc.l $48e701c0\n',b'\tdseg\n\tdc.l $4e754e75\n',b'\tds.b 626\n',b'\tincbin "object.bin"\n',b'unsigned char code[626] = {0};\n',b'_opcode equ 20085\n']:
   f=copy.deepcopy(self.facts[4]);f['source_sha256']=sha256(raw)
   with self.subTest(source=raw),self.assertRaises((FormatError,UnicodeError)):a.source_policy(raw,f)
 def test_aj_repeated_long_reference_count_is_exhaustive(self):
  f=self.facts[1];raw=(ROOT/self.batch['job']/'sys/work/world.o').read_bytes();_,refs,s=parse(raw)
  self.assertEqual(s['symbols'][0]['reference_count'],2);self.assertEqual(sum(r['symbol']=='_G_h01_2B4A' for r in refs),2)
  p=raw.index(b'\x07\x0e\0\0\0\x02');bad=bytearray(raw);bad[p+5]=3
  with self.assertRaisesRegex(FormatError,'reference inventory'):parse(bytes(bad))
 def test_aj_hidden_sections_unknown_records_addends_and_trailers_reject(self):
  raw=(ROOT/self.batch['job']/'sys/work/world.o').read_bytes();p=raw.index(b'\xfa\x71\0',36)
  for pos,v in [(17,1),(21,1),(p,0xfb),(p+1,0x7f),(p+2,1)]:
   bad=bytearray(raw);bad[pos]=v
   with self.subTest(offset=pos),self.assertRaises(FormatError):parse(bytes(bad))
  with self.assertRaises(FormatError):parse(raw+bytes(4))
 def test_exact_contribution_from_aj_only_and_both_reference_classes(self):
  rows=[dict(r,acceptance=True) for r in self.rows];parts=a.contributions(ROOT,rows)
  self.assertEqual(sum(len(p['bytes']) for p in parts),1750);self.assertEqual({p['category'] for p in parts},{'RECONSTRUCTED_ASM'})
  for p,r in zip(parts,rows):
   self.assertEqual(sha256(p['bytes']),r['span']['sha256'])
   expected=[{k:x[k] for k in ['source_offset','target_hunk','type','width','addend_raw']} for x in self.model['relocations'] if x['source_hunk']==0 and p['start']<=x['source_offset']<p['end']]
   self.assertEqual(p['relocations'],expected)
  self.assertTrue(any(b['width']==2 for r in rows for b in r['named_relocation_bindings']));self.assertTrue(any(b['original_hunk']==0 and b['width']==4 for r in rows for b in r['named_relocation_bindings']))
 def test_full_hybrid_account_accepts_all_eight_real_contributions(self):
  from hybrid_image import account
  parts=a.contributions(ROOT,[dict(r,acceptance=True) for r in self.rows])
  image,report=account(self.blob,self.model,parts)
  self.assertEqual(image,self.blob);self.assertEqual(report['totals']['RECONSTRUCTED_ASM'],1750)
  self.assertEqual((report['totals']['overlap'],report['totals']['unaccounted']),(0,0))
 def test_straddling_relocation_rejects(self):
  f=self.facts[0];model=copy.deepcopy(self.model);model['relocations'].append(dict(source_hunk=0,source_offset=f['original']['end']-2,target_hunk=1,addend_raw=0,type='HUNK_RELOC32',width=4))
  with self.assertRaisesRegex(FormatError,'straddling'):a.validate_fact(ROOT,self.blob,model,self.contract,f)
 def test_swapped_handler_wrong_width_and_slot45_reject(self):
  for kind in ['swap','width','extra']:
   model=copy.deepcopy(self.model);refs=[r for r in model['relocations'] if r['source_hunk']==1 and 0x292e<=r['source_offset']<0x29de]
   if kind=='swap':refs[0]['addend_raw'],refs[1]['addend_raw']=refs[1]['addend_raw'],refs[0]['addend_raw']
   elif kind=='width':refs[0]['width']=2
   else:model['relocations'].append(dict(refs[-1],source_offset=0x29de))
   with self.subTest(kind=kind),self.assertRaises(FormatError):c.derive(self.blob,model,self.calibration)
 def test_named_target_and_pc_site_proof_cannot_be_masked(self):
  f=copy.deepcopy(self.facts[7]);f['external_code'][0]['target']+=2
  with self.assertRaisesRegex(FormatError,'target bindings'):a.validate_fact(ROOT,self.blob,self.model,self.contract,f)
 def test_producer_pin_mismatch_rejects(self):
  batch=copy.deepcopy(self.batch);batch['receipt_sha256']='0'*64
  with self.assertRaisesRegex(FormatError,'SHA pins'):a.producer(ROOT,batch)
 def test_canonical_proofs_rederive_verifier_identity_is_provenance_only(self):
  virtual={};ledger={'functions':{},a.MAP:{}}
  for name,f,r in zip(a.FACTS,self.facts,self.rows):
   report=dict(r,verifier_identity={'previous-verifier':'historical provenance'},register_calibration={'historical_corpus':'provenance only'});proof=json_bytes(dict(fact=f,comparison=report,regression={'passed':True}));dest='recovery/proofs/asm-reconstructed/'+f['id']+'.json';virtual[dest]=proof;virtual[f['source']]=(ROOT/f['candidate']).read_bytes();ledger[a.MAP][f['id']]=dict(state='FUNCTION_CODE_MATCH',fact=name,source=f['source'],source_sha256=f['source_sha256'],proof=dest,proof_sha256=sha256(proof))
  original=Path.read_bytes
  def read(p):
   try:n=p.relative_to(ROOT).as_posix()
   except ValueError:return original(p)
   return virtual[n] if n in virtual else original(p)
  with patch.object(Path,'read_bytes',read):
   self.assertEqual(sum(r['span']['size'] for r in a.rows(ROOT,self.blob,self.model,{},ledger)),1750)
   ledger['functions']['conflict']={'evidence_extent':dict(hunk=0,start=0x544c,end=0x544e)}
   with self.assertRaisesRegex(FormatError,'overlaps canonical C'):a.rows(ROOT,self.blob,self.model,{},ledger)
 def test_failed_shared_gate_prevents_publication(self):
  import promote_asm as promote,check_function,evidence_snapshot,analysis_support
  from contextlib import nullcontext
  with patch.object(sys,'argv',['promote_asm','--manifest',a.MANIFEST,'--promote']),patch.object(promote,'ledger_lock',lambda p:nullcontext()),patch.object(promote,'stage',return_value=[]),patch.object(check_function,'regression_receipt',return_value={'passed':False}),patch.object(evidence_snapshot.Snapshot,'inputs',return_value={}),patch.object(analysis_support,'game',return_value=(self.blob,self.model,None)),patch.object(promote,'publish') as publish:
   with self.assertRaisesRegex(FormatError,'passing shared regression'):promote.main()
   publish.assert_not_called()
 def test_optional_empty_repository_inputs(self):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:self.assertEqual(list(a.input_identity(Path(tmp)).values()),[None])
 def test_old_and_new_manifests_remain_distinct(self):
  import reconstructed_asm as old
  self.assertNotEqual(old.MANIFEST,a.MANIFEST);self.assertFalse(set(old.SPECS)&set(a.SPECS));self.assertEqual(len(old.FACTS),2)

if __name__=='__main__':unittest.main()
