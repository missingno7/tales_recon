import sys,pathlib,json,unittest,copy
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
# Normal canonical tests import tools through their existing bootstrap.
if str(ROOT/'tools') not in sys.path:sys.path.insert(0,str(ROOT/'tools'))
import data_provider_literals as lit
import data_providers as dp
from common import FormatError
class LiteralProviderControls(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  root=pathlib.Path(dp.__file__).resolve().parents[1]
  # Scratch imports materialize changed files only; the test runner supplies the
  # real dependency root, never a copied build/assets/toolchain tree.
  import os
  cls.root=pathlib.Path(os.environ.get('TALES_TEST_REAL_ROOT',str(root)))
  cls.fact=json.loads((root/'evidence/data-providers/resident_data_0320.json').read_bytes())
  recipe=json.loads((root/'evidence/data-providers/producer-0004.json').read_bytes());w=cls.root/recipe['job']/'sys/work'
  cls.files={p.name:p.read_bytes() for p in w.iterdir() if p.is_file()};cls.obj=cls.files['p0320.o'];cls.exe=cls.files['p0320.exe'];cls.map=cls.files['p0320.sym'].decode('ascii')
  from analysis_support import game
  from census import advisory_image
  from evidence_snapshot import isolated_verification
  from recovery_evidence import load_promotions
  with isolated_verification(cls.root),advisory_image():
   cls.blob,cls.model,_=game();cls.analysis=json.loads((cls.root/'evidence/functions/ledger.json').read_bytes());cls.ledger=json.loads((cls.root/'recovery/ledger.json').read_bytes());cls.promotions=load_promotions(cls.root,cls.blob,cls.model,cls.analysis)
 def evidence(self,fact=None,analysis=None,ledger=None,promotions=None):
  return lit.typed_evidence(self.root,self.fact if fact is None else fact,self.blob,self.model,self.analysis if analysis is None else analysis,self.ledger if ledger is None else ledger,self.promotions if promotions is None else promotions)
 def test_current_typed_consumer_domains(self):
  ev=self.evidence();self.assertEqual(len(ev[0]['domains']['G_h01_0320']['indices']),15);self.assertEqual(len(ev[0]['domains']['G_h01_0398']['indices']),26)
 def test_unaccepted_consumer_rejected(self):
  with self.assertRaises(FormatError):self.evidence(promotions=[])
 def test_stale_type_source_pin_rejected(self):
  f=copy.deepcopy(self.fact);f['evidence']['ov04_F_0926']['source_sha256']='0'*64
  with self.assertRaises(FormatError):self.evidence(fact=f)
 def test_decoded_stride_rejected(self):
  a=copy.deepcopy(self.analysis);f=next(f for f in a['functions'] if f['id']=='ov04_F_0926');next(i for i in f['instructions'] if i['mnemonic']=='asl.l')['operands']='#$2, d0'
  with self.assertRaises(FormatError):self.evidence(analysis=a)
 def test_decoded_pointer_width_rejected(self):
  a=copy.deepcopy(self.analysis);f=next(f for f in a['functions'] if f['id']=='ov04_F_0926');next(i for i in f['instructions'] if i['offset']==0x9bc)['mnemonic']='move.w'
  with self.assertRaises(FormatError):self.evidence(analysis=a)
 def test_neighbour_code_boundary_rejected(self):
  l=copy.deepcopy(self.ledger);l['functions']['resident_F_01BA']['evidence_extent']['start']=0x1bc
  with self.assertRaises(FormatError):self.evidence(ledger=l)
 def test_unbounded_printable_extension_rejected(self):
  f=copy.deepcopy(self.fact);f['definitions'][1]['initializer'][-1]['text']+=' '
  with self.assertRaises(FormatError):self.evidence(fact=f)
 def reject_fact(self,mut):
  f=copy.deepcopy(self.fact);mut(f)
  with self.assertRaises(FormatError):lit.shape(f)
 def test_complete_object_and_link(self):
  p,m,s,a=lit.linked_view(self.obj,self.exe,self.map,self.fact['definitions']);self.assertEqual(p['sections'],dict(CODE=418,DATA=328,BSS=0,COMMON=0));self.assertEqual(len(p['fixups']),41);self.assertEqual([p['size'] for p in p['pools']],[130,288])
 def test_independent_odd_duplicate_control(self):
  report=lit.control_report(self.files);self.assertEqual(report['pools'][0]['padding'],1);self.assertEqual(report['game_credit'],0)
 def test_generated_source_has_literals_and_no_carriers(self):
  src=lit.source(self.fact);self.assertIn(b'char *text;',src);self.assertIn(b'G_h01_0320[15]',src);self.assertNotIn(b'unsigned char',src);self.assertNotIn(b'padding',src);self.assertNotIn(b'0x',src)
 def test_opaque_byte_array_rejected(self):self.reject_fact(lambda f:f['definitions'][0].update(type='unsigned char',count=120))
 def test_guessed_extent_rejected(self):self.reject_fact(lambda f:f['definitions'][1].update(count=27))
 def test_merged_array_without_independent_extent_rejected(self):self.reject_fact(lambda f:f.update(definitions=[dict(f['definitions'][0],count=41,initializer=f['definitions'][0]['initializer']+f['definitions'][1]['initializer'])]))
 def test_rotated_record_boundary_rejected(self):self.reject_fact(lambda f:f.update(original=dict(hunk=1,start=0x324,size=328)))
 def test_root_header_credit_rejected(self):self.reject_fact(lambda f:f.update(literal_original=dict(hunk=0,start=0,size=442)))
 def test_padding_filler_rejected(self):self.reject_fact(lambda f:f['definitions'][0]['fields'].append(dict(name='padding',type='char',offset=8)))
 def test_pointer_integer_rejected(self):self.reject_fact(lambda f:f['definitions'][0]['initializer'][0].update(text=24))
 def test_embedded_nul_rejected(self):self.reject_fact(lambda f:f['definitions'][0]['initializer'][0].update(text='HA!\0I'))
 def test_sized_string_extent_rejected(self):self.reject_fact(lambda f:f['definitions'][0]['initializer'][0].update(extent=9))
 def test_incomplete_record_rejected(self):self.reject_fact(lambda f:f['definitions'][0]['initializer'][0].pop('y'))
 def test_untyped_field_rejected(self):self.reject_fact(lambda f:f['definitions'][0]['fields'][0].update(type='char'))
 def test_hidden_bss_rejected(self):self.reject_fact(lambda f:f['object_sections'].update(BSS=2))
 def test_hidden_common_rejected(self):self.reject_fact(lambda f:f['object_sections'].update(COMMON=4))
 def test_extra_function_section_rejected(self):self.reject_fact(lambda f:f['object_sections'].update(CODE=420))
 def test_object_byte_mutation_rejected(self):
  a=bytearray(self.obj);a[39]^=1
  with self.assertRaises(FormatError):lit.object_data(bytes(a),self.fact['definitions'])
 def test_object_literal_mutation_rejected(self):
  a=self.obj.replace(b'HA! I',b'HA? I',1)
  with self.assertRaises(FormatError):lit.object_data(a,self.fact['definitions'])
 def test_object_fixup_mutation_rejected(self):
  a=self.obj.replace(b'\xfd\x21\x60\0\x30',b'\xfd\x21\x61\0\x30',1)
  with self.assertRaises(FormatError):lit.object_data(a,self.fact['definitions'])
 def test_object_refcount_mutation_rejected(self):
  a=bytearray(self.obj);a[-1]^=1
  with self.assertRaises(FormatError):lit.object_data(bytes(a),self.fact['definitions'])
 def test_object_hidden_section_rejected(self):
  a=bytearray(self.obj);a[21]=2
  with self.assertRaises(FormatError):lit.object_data(bytes(a),self.fact['definitions'])
 def test_object_extra_tail_rejected(self):
  with self.assertRaises(FormatError):lit.object_data(self.obj+b'\0\0',self.fact['definitions'])
 def test_linked_harness_mutation_rejected(self):
  a=self.exe.replace(b'\x4e\x75',b'\x4e\x71',1)
  with self.assertRaises(FormatError):lit.linked_view(self.obj,a,self.map,self.fact['definitions'])
 def test_linked_literal_mutation_rejected(self):
  a=self.exe.replace(b'HA! I',b'HA? I',1)
  with self.assertRaises(FormatError):lit.linked_view(self.obj,a,self.map,self.fact['definitions'])
 def test_missing_symbol_rejected(self):
  with self.assertRaises(FormatError):lit.linked_view(self.obj,self.exe,self.map.replace('_G_h01_0398','_G_h01_0399'),self.fact['definitions'])
 def test_complete_contributions_include_literal_ownership(self):
  sem=lit.semantic(self.fact['definitions']);r=dict(id='test',original=self.fact['original'],data_hex=sem['data'].hex(),original_relocations=[],owned_literals=[dict(self.fact['literal_original'],bytes_hex=sem['code'].hex(),relocations=[])])
  cs=dp.contributions([r]);self.assertEqual([(c['hunk'],c['category'],len(c['bytes'])) for c in cs],[(1,'RECOVERED_DATA',328),(0,'COMPILER_OWNED_DATA',418)]);self.assertEqual(min(c['start'] for c in cs if c['hunk']==0),24)
if __name__=='__main__':unittest.main()
