"""Invariant and rejection coverage for the calibrated graphics glue route."""
import copy,json,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import glue_library_asm as glue
from common import FormatError,sha256,json_bytes

def instructions():
 pairs=[('movem.l','d4-d6/a2-a6, -(a7)')]
 pairs += [('movea.l' if r.startswith('a') else 'move.l','$%x(a7), %s'%(36+4*n,r)) for n,r in enumerate(glue.REGISTERS)]
 pairs += [('movea.l','$5374.l, a6'),('jsr','-$27c(a6)'),('movem.l','(a7)+, d4-d6/a2-a6'),('rts','')]
 result=[];p=0x4692
 for m,o in pairs:
  size=6 if o=='$5374.l, a6' else 2 if m=='rts' else 4
  result.append(dict(offset=p,size=size,mnemonic=m,operands=o));p+=size
 return result
ENTRY=dict(kind='DIRECT_CALL',caller='resident_F_34E0',site=0x35a4,target=0x4692)
ABI=dict(vector=-636,registers=glue.REGISTERS)
MEASURED=dict(all_required_entries_link_a5=True)

class PredicateTests(unittest.TestCase):
 def witness(self,items=None,entry=None,measured=None,abi=None):return glue.witness(instructions() if items is None else items,ENTRY if entry is None else entry,MEASURED if measured is None else measured,ABI if abi is None else abi)
 def test_absent_manifest_has_no_graphics_prerequisites(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.assertEqual(glue.input_identity(root),{str(root/glue.MANIFEST):None})
 def test_complete_independently_entered_bridge(self):
  r=self.witness();self.assertFalse(r['c_compatible']);self.assertEqual([x['register'] for x in r['arguments']],glue.REGISTERS)
  self.assertEqual(r['frame']['sdk_call']['return_to'],r['frame']['reachable_instructions'][-2])
 def test_each_argument_register_and_stack_offset_is_required(self):
  for n in range(1,len(glue.REGISTERS)+1):
   for change in ['register','offset']:
    with self.subTest(n=n,change=change):
     items=instructions();items[n]['operands']='$24(a7), a3' if change=='register' else '$7c(a7), '+glue.REGISTERS[n-1]
     with self.assertRaises(FormatError):self.witness(items)
 def test_saves_base_vector_restore_and_return_are_required(self):
  for n in [0,11,12,13,14]:
   with self.subTest(n=n):
    items=instructions();items[n]['operands']='d0'
    with self.assertRaises(FormatError):self.witness(items)
 def test_no_inherited_entry(self):
  for entry in [{},dict(ENTRY,site=ENTRY['site']+2),dict(ENTRY,kind='ADJACENT')]:
   with self.subTest(entry=entry),self.assertRaises(FormatError):self.witness(entry=entry)
 def test_framed_c_rejects(self):
  items=instructions();items[0].update(mnemonic='link.w',operands='a5, #$0')
  with self.assertRaises(FormatError):self.witness(items)
 def test_missing_or_refuted_calibration_rejects(self):
  for measured in [{},dict(all_required_entries_link_a5=False)]:
   with self.subTest(measured=measured),self.assertRaises(FormatError):self.witness(measured=measured)
 def test_sdk_argument_contract_is_independent(self):
  for abi in [dict(ABI,vector=-30),dict(ABI,registers=list(reversed(glue.REGISTERS)))]:
   with self.subTest(abi=abi),self.assertRaises(FormatError):self.witness(abi=abi)
 def test_clipped_extra_or_gapped_instruction_rejects(self):
  for items in [instructions()[:-1],instructions()+[dict(offset=0x46ce,size=2,mnemonic='rts',operands='')]]:
   with self.assertRaises(FormatError):self.witness(items)
  items=instructions();items[4]['offset']+=2
  with self.assertRaises(FormatError):self.witness(items)
  items=instructions();items[4]['size']+=2
  with self.assertRaises(FormatError):self.witness(items)

class ExactProducerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from analysis_support import ROOT,game
  from census import advisory_image
  cls.root=ROOT
  with advisory_image():cls.blob,cls.model,_=game()
  cls.controls=glue.control(ROOT,cls.blob,cls.model);cls.contract=glue.derive(cls.blob,cls.model,cls.controls['frame_calibration'],ROOT)
  cls.fact=glue.document(ROOT,glue.FACT);cls.batch=glue.document(ROOT,glue.MANIFEST);cls.audit=glue.producer(ROOT,cls.batch)
 def verify(self,fact=None):return glue.verify(self.root,self.blob,self.model,{},self.fact if fact is None else fact,self.batch,self.contract,self.audit,self.controls)
 def test_complete_object_code_relocations_and_link(self):
  r=self.verify();self.assertEqual(r['verdict'],'EQUAL_CANDIDATE');self.assertEqual(r['category'],'RECONSTRUCTED_ASM');self.assertEqual(r['data_credit'],0)
  self.assertEqual(r['ordinary_bytes_compared']+r['named_field_bytes'],r['span']['size'])
 def test_changed_fact_source_extent_or_target_rejects(self):
  for key,value in [('source_sha256','0'*64),('historical_owner','Manx'),('original',dict(self.fact['original'],end=self.fact['original']['end']-2)),('relocations',[])]:
   with self.subTest(key=key):
    f=copy.deepcopy(self.fact);f[key]=value
    with self.assertRaises(FormatError):self.verify(f)
 def test_whole_object_mutations_reject(self):
  raw=(self.root/self.batch['job']/'sys/work/glue.o').read_bytes()
  for pos in [14,18,22,34,len(raw)-1]:
   with self.subTest(pos=pos):
    changed=bytearray(raw);changed[pos]^=1
    with self.assertRaises((FormatError,UnicodeDecodeError)):glue.object_code(bytes(changed))
 def test_ordinary_byte_mutation_fails_exact_comparison(self):
  from audio_sequence_data import payload
  changed=bytearray(self.blob);h=next(x for x in self.model['hunks'] if x['number']==0);changed[h['content_offset']+0x4696]^=1
  with self.assertRaises(FormatError):glue.derive(bytes(changed),self.model,self.controls['frame_calibration'],self.root)
class PromotionStageTests(unittest.TestCase):
 def test_predicate_uses_existing_stage_and_raw_overlap_check(self):
  from types import SimpleNamespace
  import promote_asm
  fact=dict(id='synthetic',original=dict(hunk=0,start=16,end=24))
  predicate=SimpleNamespace(MANIFEST='batch',FACTS=['fact'],MAP='reconstructed_asm',
   document=lambda root,name:fact if name=='fact' else {},
   verify=lambda root,blob,model,analysis,fact,batch:dict(verdict='EQUAL_CANDIDATE'))
  for category in ['RAW_ORACLE_DEBT','RECOVERED_C','RECONSTRUCTED_ASM']:
   accounting=dict(ranges=[dict(hunk=0,start=16,end=24,category=category)])
   with patch('hybrid_image.build',return_value=(b'',accounting)):
    if category=='RAW_ORACLE_DEBT':
     rows=promote_asm.stage(Path('.'),b'',{}, {},{},predicate=predicate)
     self.assertEqual(rows,[('fact',fact,dict(verdict='EQUAL_CANDIDATE'))])
    else:
     with self.assertRaisesRegex(FormatError,'overlaps already credited'):
      promote_asm.stage(Path('.'),b'',{}, {},{},predicate=predicate)
 def test_glue_metadata_binds_complete_object_for_the_general_recipe(self):
  from analysis_support import ROOT
  import reconstructed_asm_dependencies as deps
  fact=glue.document(ROOT,glue.FACT)
  self.assertEqual(fact['prefix'],glue.SPECS[glue.ID]['prefix'])
  self.assertEqual(fact['exports'],[dict(name='_F_h00_4692',offset=0,original=fact['original']['start'])])
  self.assertEqual(fact['external_data'],[dict(name=fact['base_binding']['symbol'],hunk=fact['base_binding']['hunk'],target=fact['base_binding']['target'])])
  self.assertEqual([r['symbol'] for r in fact['relocations']],[fact['base_binding']['symbol']])
  self.assertIn(glue.ID,deps.specifications())
if __name__=='__main__':unittest.main()
