"""Closed-prefix bounds and complete external DATA-object rejection controls."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from analysis_support import ROOT
from common import FormatError
import data_providers as dp
import data_provider_sample_tables as tables
import data_provider_callback_tables as cycles
import data_provider_cells as cells


def sample_fact(first=1,count=2):
 start=0x27e4+4*first;names=['G_h01_%04X'%(0x3400+0x20*i) for i in range(count)]
 return dict(schema_version=1,kind=tables.KIND,id='resident_data_%04X'%start,source='src/recovered/data/resident_data_%04X.c'%start,original=dict(hunk=1,start=start,size=4*count),definitions=[dict(symbol='G_h01_%04X'%start,type='struct DP_Sample *',offset=0,count=count,first_index=first,target_record_count=1,targets=names,bounds=dict(kind='SAMPLE_ACCESS_PREFIX_SLICE',bytes=4*count))],bindings={n:dict(fact='evidence/data-providers/resident_data_'+n[-4:]+'.json',sha256='0'*64) for n in names},anchors={'consumer':{}},object_sections=dict(CODE=0,DATA=4*count,BSS=0,COMMON=0),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,producer={})


class PrefixBounds(unittest.TestCase):
 def test_source_uses_consumed_first_record_view(self):
  f=sample_fact();src=tables.source(f).decode('ascii')
  self.assertIn('struct DP_Sample { int duration; unsigned int length_words; char *sample_data; };',src)
  self.assertIn('struct DP_Sample *'+f['definitions'][0]['symbol']+'[2]',src)
  self.assertNotIn('char reserved',src)
  self.assertIn('struct DP_Sequence { struct DP_Sample records[1]; int terminal_duration; };',src)
  self.assertIn('extern struct DP_Sequence ',src)
  self.assertIn('(struct DP_Sample *)&',src)

 def test_target_extern_count_requires_independent_target_shape(self):
  from common import sha256,json_bytes
  f=sample_fact(first=1,count=1);name=f['definitions'][0]['targets'][0]
  target=dict(kind='BOUNDED_DATA_TABLE',route='SAMPLE_RECORD_PREFIX_MEMBER',selector_index=1,definitions=[dict(symbol=name,initializer=dict(records=[{},{}]))])
  f['bindings'][name]['sha256']=sha256(json_bytes(target))
  with patch('data_provider_sequences.anchors',return_value={}),patch('data_provider_sequences.sample_domain',return_value=({0,1},{})),patch('game_image.game',return_value=(b'',{},{})),patch('data_providers.document',return_value=target):
   with self.assertRaisesRegex(FormatError,'complete separately proved record shape'):
    tables.typed_evidence(ROOT,f,{}, {},[])

 def test_asset_source_declares_typed_programs(self):
  f=sample_fact();d=f['definitions'][0];d['type']='unsigned char *';d.pop('target_record_count');d['bounds']['kind']='ASSET_ACCESS_PREFIX_SLICE'
  off=0x1f9e+4*d['first_index'];f['id']='resident_data_%04X'%off;f['source']='src/recovered/data/'+f['id']+'.c';f['original']['start']=off;d['symbol']='G_h01_%04X'%off
  src=tables.source(f).decode('ascii')
  self.assertIn('extern unsigned char ',src);self.assertNotIn('struct DP_Sample',src)
  self.assertIn('unsigned char *'+d['symbol'],src)

 def test_asset_extent_needs_a_literal_canonical_witness(self):
  from data_provider_sequences import asset_prefix
  with self.assertRaises(FormatError):asset_prefix({'consumer':('F_h00_4D04(n);',{},None)})

 def test_guessed_slice_extent_rejects(self):
  f=sample_fact();f['original']['size']+=4
  with self.assertRaises(FormatError):tables.shape(f)

 def test_pointer_must_name_independent_fact(self):
  f=sample_fact();name=next(iter(f['bindings']));f['bindings'][name]['fact']='evidence/data-providers/unnamed.json'
  with self.assertRaises(FormatError):tables.shape(f)

 def test_slice_after_highest_access_rejects(self):
  f=sample_fact(first=3,count=1)
  with patch('data_provider_sequences.anchors',return_value={}),patch('data_provider_sequences.sample_domain',return_value=({0,1,2},{})),patch('game_image.game',return_value=(b'',{},{})):
   with self.assertRaisesRegex(FormatError,'exceeds independently accessed prefix'):
    tables.typed_evidence(ROOT,f,{}, {},[])

 def test_cursor_transition_includes_previous_record(self):
  self.assertEqual(cycles.consumed_words(1,3),4)
  self.assertGreater(cycles.consumed_words(1,3),2*1+1)

 def test_machine_width_cursor_transitions_fit_the_source_bound(self):
  # Independent execution model of the decoded CLR.L/MOVE.B/SUBQ.L/BPL,
  # MOVE.W/LSL.W/AND.L, then MOVE.W postincrement plus DBRA sequence.
  for maximum in range(12):
   for last in range(maximum+1):
    touched=set()
    for previous in range(maximum+1):
     d0=(previous-1)&0xffffffff
     if d0&0x80000000:d0=(d0&0xffff0000)|last
     d0=(d0&0xffff0000)|((d0<<1)&0xffff)
     a0=d0&0xff;d7=last
     while True:
      touched.add(a0//2);a0+=2;d7=(d7-1)&0xffff
      if d7==0xffff:break
    self.assertEqual(touched,set(range(cycles.consumed_words(last,maximum))))

 def test_wrapping_cursor_requires_another_proof(self):
  for args in [(-1,1),(2,1),(128,128),(True,1)]:
   with self.assertRaises(FormatError):cycles.consumed_words(*args)


class ExternalDataObjects(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  recipe=dp.document(ROOT,'evidence/data-providers/producer-raw-sample-pointers.json');work=ROOT/recipe['job']/'sys/work'
  cls.table_files={n:(work/n).read_bytes() for n in recipe['artifacts']}
  cls.table_facts=[dp.document(ROOT,m['fact']) for m in recipe['members']]
  recipe=dp.document(ROOT,'evidence/data-providers/producer-raw-cycle-records.json');work=ROOT/recipe['job']/'sys/work'
  cls.cycle_files={n:(work/n).read_bytes() for n in recipe['artifacts']}
  cls.cycle_facts=[dp.document(ROOT,m['fact']) for m in recipe['members']]
  cls.control_rows=[dict(words='DP_a',last=1,destination=2),dict(words=None,last=0,destination=0),dict(words='DP_b',last=3,destination=4)]

 def test_independently_compiled_many_target_control(self):
  r=tables.control_report(self.table_files,tables.binder_names(self.table_facts))
  self.assertEqual(r['game_credit'],0)
  self.assertGreater(r['unique_test_targets'],r['cell_control']['unique_test_targets'])
  self.assertGreater(r['relocations'],r['unique_test_targets'])

 def test_scalar_route_does_not_inherit_wider_index_support(self):
  raw=self.table_files['datatablesprobe.o']
  with self.assertRaises(FormatError):cells.object_data(raw,'_DP_table_probe',tables.CONTROL_TARGETS)

 def test_many_target_control_cannot_be_omitted(self):
  f=self.table_facts[0]
  with patch.object(dp,'typed_evidence',return_value=[]),patch.object(dp,'producer',return_value=({},{})):
   with self.assertRaisesRegex(FormatError,'independent many-target control'):
    dp.verify(ROOT,b'',{}, {},{},[],f,dp.source(f),None)

 def test_mixed_record_control_cannot_be_omitted(self):
  f=self.cycle_facts[0]
  with patch.object(dp,'typed_evidence',return_value=[]),patch.object(dp,'producer',return_value=({},{})):
   with self.assertRaisesRegex(FormatError,'independent record control'):
    dp.verify(ROOT,b'',{}, {},{},[],f,dp.source(f),None)

 def test_wrong_named_external_index_rejects(self):
  raw=bytearray(self.table_files['datatablesprobe.o']);self.assertEqual(raw[36:40],bytes.fromhex('f5fd7100'));raw[38]=0x7f
  with self.assertRaises(FormatError):cells.object_data(bytes(raw),'_DP_table_probe',tables.CONTROL_TARGETS,max_externals=14)

 def test_hidden_bss_rejects(self):
  raw=bytearray(self.table_files['datatablesprobe.o']);raw[18:22]=(2).to_bytes(4,'big')
  with self.assertRaises(FormatError):cells.object_data(bytes(raw),'_DP_table_probe',tables.CONTROL_TARGETS,max_externals=14)

 def test_truncated_object_rejects(self):
  with self.assertRaises(FormatError):cells.object_data(self.table_files['datatablesprobe.o'][:-1],'_DP_table_probe',tables.CONTROL_TARGETS,max_externals=14)

 def test_independently_compiled_record_control(self):
  r=cycles.control_report(self.cycle_files,cycles.binder_names(self.cycle_facts))
  self.assertEqual(r['game_credit'],0);self.assertGreater(r['null_pointers'],0)
  self.assertEqual(r['field_widths'],[4,2,2])

 def test_record_word_cannot_be_masked(self):
  rows=copy.deepcopy(self.control_rows);rows[0]['destination']+=1
  with self.assertRaises(FormatError):cycles.object_records(self.cycle_files['cycleprobe.o'],'_DP_cycles',rows)

 def test_record_pointer_cannot_be_replaced_with_integer(self):
  rows=copy.deepcopy(self.control_rows);rows[0]['words']=None
  with self.assertRaises(FormatError):cycles.object_records(self.cycle_files['cycleprobe.o'],'_DP_cycles',rows)

 def test_record_hidden_code_rejects(self):
  raw=bytearray(self.cycle_files['cycleprobe.o']);raw[10:14]=(2).to_bytes(4,'big')
  with self.assertRaises(FormatError):cycles.object_records(bytes(raw),'_DP_cycles',self.control_rows)

 def test_null_record_is_not_padding(self):
  rows=copy.deepcopy(self.control_rows);rows.pop(1)
  with self.assertRaises(FormatError):cycles.object_records(self.cycle_files['cycleprobe.o'],'_DP_cycles',rows)


class EnvelopePrefixControls(unittest.TestCase):
 def candidate(self):
  return dict(id='relocated_candidate',hunk=0,start=10,end=14,callers=[],entry_evidence=[dict(kind='RELOCATION_POINTER',source_hunk=0,source_offset=4)])

 def check_candidate(self,f,ledger=None,refs=None):
  import audio_envelope_prefix as env
  return env.exclude_code_candidates(dict(functions=[f]),ledger or {},set(range(10,14)),{(0,4)} if refs is None else refs)

 def test_pointer_only_candidate_requires_typed_incoming_reference(self):
  self.check_candidate(self.candidate())
  with self.assertRaises(FormatError):self.check_candidate(self.candidate(),refs=set())

 def test_direct_caller_prevents_data_admission(self):
  f=self.candidate();f['callers']=['actual_caller']
  with self.assertRaises(FormatError):self.check_candidate(f)

 def test_independent_executable_entry_prevents_data_admission(self):
  f=self.candidate();f['entry_evidence'].append(dict(kind='DIRECT_CALL',source_hunk=0,source_offset=4))
  with self.assertRaises(FormatError):self.check_candidate(f)

 def test_accepted_source_cannot_be_reclassified_as_data(self):
  f=self.candidate()
  with self.assertRaises(FormatError):self.check_candidate(f,dict(functions={f['id']:{}}))

 def test_support_partition_has_no_double_credit_or_holes(self):
  import audio_envelope_prefix as env
  o=dict(parts=[dict(original_start=10,original_end=20,candidate_start=0,candidate_end=10)])
  occupied={11,12,15};env.partition([o],occupied)
  covered=lambda parts:{p for x in parts for p in range(x['original_start'],x['original_end'])}
  credit=covered(o['credit_parts']);support=covered(o['support_parts'])
  self.assertEqual(support,occupied);self.assertFalse(credit&support)
  self.assertEqual(credit|support,set(range(10,20)));self.assertEqual(o['credit_bytes'],len(credit))

 def test_regeneration_preserves_new_control_command_graphs(self):
  import data_provider_job as jobs
  for controls in (['dataprobe','datatablesprobe'],['cycleprobe']):
   prefixes=['provider','relprobe']+controls
   self.assertEqual(jobs.commands(prefixes,controls),cells.commands(prefixes))

 def test_code_data_verify_only_never_takes_publication_lock(self):
  import contextlib,io,sys
  import audio_envelope_prefix as env
  import promote_code_data as publisher
  report=dict(typed_bytes=0,objects=[])
  with patch.object(sys,'argv',['promote_code_data.py','--manifest',env.MANIFEST,'--verify-only']),patch('game_image.game',return_value=(b'',{},{})),patch('evidence_snapshot.isolated_verification',return_value=contextlib.nullcontext()),patch.object(publisher,'stage',return_value=({},report)),patch.object(publisher,'ledger_lock',side_effect=AssertionError('verification must not lock/write canonical state')),patch.object(publisher,'publish',side_effect=AssertionError('verification must not publish')):
   with contextlib.redirect_stdout(io.StringIO()) as out:publisher.main()
  self.assertIn('EQUAL_CANDIDATE',out.getvalue())
