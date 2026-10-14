"""Reconstructed ASM acceptance controls, using the retained pinned RNG producer."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import reconstructed_asm as asm
from common import FormatError,sha256,json_bytes
from census import verify_lock,_derive_uncached
from recovery_state import canonical_state

class ReconstructedASMTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  verify_lock(ROOT);_,files,cls.model=_derive_uncached(ROOT,False);cls.blob=files['DT1:DuckTales']
  cls.analysis=asm.document(ROOT,'evidence/functions/ledger.json');cls.fact=asm.document(ROOT,asm.FACT)
  cls.job=asm.document(ROOT,asm.MANIFEST)['job'];cls.object=(ROOT/cls.job/'sys/work/rng.o').read_bytes()
 def test_exact_whole_rng_and_named_bindings(self):
  r=asm.verify(ROOT,self.blob,self.model,self.analysis,self.fact)
  self.assertEqual((r['category'],r['span']['size'],r['ordinary_bytes_compared']),('RECONSTRUCTED_ASM',56,48))
  self.assertEqual([(x['offset'],x['symbol']) for x in r['named_relocation_bindings']],[(10,'_G_h01_2B89'),(16,'_G_h01_2B8A')])
  self.assertEqual(r['data_credit'],0)
 def test_c_compatible_enable_disable_reject(self):
  for a,z in [(0x558a,0x5594),(0x5594,0x559e)]:
   with self.subTest(start=a),self.assertRaisesRegex(FormatError,'non-C CCR-X'):
    asm.non_c_predicate(self.blob,self.model,a,z)
 def test_stale_oracle_and_predicate_facts_reject(self):
  for key in ['oracle_sha256','predicate']:
   f=copy.deepcopy(self.fact);f[key]='stale'
   with self.subTest(key=key),self.assertRaises(FormatError):asm.validate_fact(ROOT,self.blob,self.model,self.analysis,f)
 def test_partial_span_reject(self):
  f=copy.deepcopy(self.fact);f['original']['end']-=2;f['original']['size']-=2
  with self.assertRaises(FormatError):asm.validate_fact(ROOT,self.blob,self.model,self.analysis,f)
 def test_masked_and_unnamed_relocation_reject(self):
  for change in ['mask','symbol','width','target_hunk']:
   f=copy.deepcopy(self.fact)
   if change=='mask':f['relocations'][0]['mask']='ffffffff'
   elif change=='symbol':f['relocations'][0]['symbol']=''
   elif change=='width':f['relocations'][0]['width']=2
   else:f['relocations'][0]['target_hunk']=0
   with self.subTest(change=change),self.assertRaises(FormatError):asm.validate_fact(ROOT,self.blob,self.model,self.analysis,f)
 def test_dc_words_and_opaque_carriers_reject_even_rehashed(self):
  original=Path.read_bytes
  for raw in [b'\tdc.w $4e75\n',b'\tdc.l $48e701c0\n',b'\tincbin "oracle.bin"\n',b'unsigned char carrier[56] = {0};\n']:
   f=copy.deepcopy(self.fact);f['source_sha256']=sha256(raw)
   with self.subTest(raw=raw),self.assertRaises(FormatError):asm.validate_fact(ROOT,self.blob,self.model,self.analysis,f)
   def read(p,raw=raw):return raw if str(p).replace('\\','/').endswith(asm.CANDIDATE) else original(p)
   with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(FormatError,'mnemonic recipe'):
    asm.verify(ROOT,self.blob,self.model,self.analysis,self.fact)
 def test_aj_hidden_section_partial_unknown_fixup_and_trailer(self):
  for pos,value in [(13,54),(21,2),(self.object.index(b'\xfd'),0xfa),(self.object.index(b'\xfd')+1,0x74),(self.object.index(b'\xfd')+2,1)]:
   b=bytearray(self.object);b[pos]=value
   with self.subTest(pos=pos,value=value),self.assertRaises(FormatError):asm.object_rng(bytes(b))
  with self.assertRaises(FormatError):asm.object_rng(self.object+b'\0')
 def test_every_original_relocation_checked(self):
  m=copy.deepcopy(self.model);r=next(r for r in m['relocations'] if r['source_hunk']==0 and r['source_offset']==0x55a8);r['addend_raw']+=1
  with self.assertRaises(FormatError):asm.validate_fact(ROOT,self.blob,m,self.analysis,self.fact)
 def test_compiler_producer_pin_mismatch_reject(self):
  b=asm.document(ROOT,asm.MANIFEST);b['receipt_sha256']='0'*64
  with self.assertRaisesRegex(FormatError,'SHA pins'):asm.verify(ROOT,self.blob,self.model,self.analysis,self.fact,b)
 def test_canonical_map_preserved(self):
  state=dict(schema_version=1,functions={},reconstructed_asm={'x':{'state':'test'}})
  self.assertEqual(canonical_state(state)['reconstructed_asm'],state['reconstructed_asm'])
 def test_category_separate_and_contribution_source_is_object(self):
  from hybrid_image import CATEGORIES
  self.assertIn('RECONSTRUCTED_ASM',CATEGORIES);self.assertIn('RECOVERED_ASM',CATEGORIES)
  r=asm.verify(ROOT,self.blob,self.model,self.analysis,self.fact);r['acceptance']=True
  c=asm.contributions(ROOT,[r])[0];self.assertEqual(c['category'],'RECONSTRUCTED_ASM');self.assertEqual(len(c['bytes']),56)
 def test_canonical_proof_rederived_and_provenance_only(self):
  from contextlib import ExitStack
  batch=asm.document(ROOT,asm.MANIFEST);ledger={'functions':{},asm.MAP:{}};virtual={}
  for name in asm.FACTS:
   fact=asm.document(ROOT,name);report=asm.verify(ROOT,self.blob,self.model,self.analysis,fact,batch)
   report['verifier_identity']={'old-verifier':'historical-provenance'}
   proof=json_bytes(dict(fact=fact,comparison=report,regression={'passed':True}))
   dest='recovery/proofs/asm-reconstructed/'+fact['id']+'.json'
   virtual[dest]=proof;virtual[fact['source']]=asm.source_for(fact['id'])
   ledger[asm.MAP][fact['id']]=dict(state='FUNCTION_CODE_MATCH',fact=name,source=fact['source'],source_sha256=fact['source_sha256'],proof=dest,proof_sha256=sha256(proof))
  original=Path.read_bytes
  def read(p):
   try:n=p.relative_to(ROOT).as_posix()
   except ValueError:return original(p)
   return virtual[n] if n in virtual else original(p)
  with patch.object(Path,'read_bytes',read):
   rows=asm.rows(ROOT,self.blob,self.model,self.analysis,ledger)
   self.assertEqual(sum(r['span']['size'] for r in rows),228)
   self.assertTrue(all(r['acceptance'] for r in rows))
   key=next(k for k in virtual if k.endswith('.json'));virtual[key]=virtual[key]+b' '
   with self.assertRaises(FormatError):asm.rows(ROOT,self.blob,self.model,self.analysis,ledger)
 def test_promotion_shared_gate_failure_prevents_publish(self):
  from contextlib import nullcontext
  import promote_asm,check_function,evidence_snapshot,analysis_support
  with patch.object(sys,'argv',['promote_asm','--promote']),patch.object(promote_asm,'ledger_lock',lambda p:nullcontext()),patch.object(promote_asm,'stage',return_value=[]),patch.object(check_function,'regression_receipt',return_value={'passed':False}),patch.object(evidence_snapshot.Snapshot,'inputs',return_value={}),patch.object(analysis_support,'game',return_value=(self.blob,self.model,None)),patch.object(promote_asm,'publish') as publish:
   with self.assertRaisesRegex(FormatError,'passing shared regression'):promote_asm.main()
   publish.assert_not_called()
 def test_a4_span_exact_independent_predicate(self):
  fact=asm.document(ROOT,asm.FACTS[1]);r=asm.verify(ROOT,self.blob,self.model,self.analysis,fact)
  self.assertEqual((r['span']['size'],r['ordinary_bytes_compared']),(172,160))
  self.assertEqual(r['non_c_predicate']['world_offset'],0x27e4)
  for a,z in [(0x558a,0x5594),(0x5594,0x559e)]:
   with self.assertRaises(FormatError):asm.a4_predicate(self.blob,self.model,a,z)
 def test_transaction_restricts_asm_to_separate_source_dir(self):
  from recovery_transaction import target
  ledger=ROOT/'recovery/ledger.json'
  self.assertEqual(target(ROOT,'src/recovered/asm-reconstructed/x.asm',ledger),ROOT/'src/recovered/asm-reconstructed/x.asm')
  with self.assertRaises(FormatError):target(ROOT,'src/recovered/resident/x.asm',ledger)
 def test_optional_snapshot_inputs_allow_an_empty_repository(self):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   values=asm.input_identity(Path(tmp))
   self.assertTrue(values)
   self.assertTrue(all(v is None for v in values.values()))
 def test_straddling_relocations_reject_for_both_spans(self):
  for name in asm.FACTS:
   f=asm.document(ROOT,name);m=copy.deepcopy(self.model)
   m['relocations'].append(dict(source_hunk=0,source_offset=f['original']['start']-2,target_hunk=1,addend_raw=0,type='HUNK_RELOC32',width=4))
   validator=asm.validate_fact if f['id']=='resident_asm_559E' else asm.validate_note_fact
   with self.subTest(id=f['id']),self.assertRaisesRegex(FormatError,'straddling'):validator(ROOT,self.blob,m,self.analysis,f)
 def test_inbound_anchor_and_container_must_rederive(self):
  with self.assertRaises(FormatError):asm.direct_entry(self.blob,self.model,0x559e,0x5594)
  m=copy.deepcopy(self.model);m['hunks'][0]['type']='DATA'
  with self.assertRaisesRegex(FormatError,'containers'):asm.verify(ROOT,self.blob,m,self.analysis,self.fact)
 def test_accounting_skips_only_unowned_staged_complete_c(self):
  import dead_code_promotion as dead
  with patch.object(dead,'canonical_rows',side_effect=FormatError('canonical replay required')) as replay:
   self.assertEqual(dead.accepted_contributions(ROOT,b'',{}, {},[],{}),[])
   replay.assert_not_called()
   with self.assertRaisesRegex(FormatError,'canonical replay required'):
    dead.accepted_contributions(ROOT,b'',{}, {},[],{dead.MAP:{'owned':{}}})

if __name__=='__main__':unittest.main()
