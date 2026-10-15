"""Measured score controls; all source inputs remain typed command definitions."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE/'tools'))
from analysis_support import ROOT
from census import _derive_uncached,verify_lock
from common import FormatError,sha256,json_bytes
from audio_sequence_data import load,payload
from audio_score_grammar import derive
from audio_score_catalogue import discover,rederive,ZERO_DEBT
from audio_score_commands import source,check,encode
import audio_score_measured as m
import code_data_providers as p


class MeasuredAudioScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify_lock(ROOT);_,files,cls.model=_derive_uncached(ROOT,False);cls.blob=files['DT1:DuckTales']
        cls.fact=m.document(ROOT,m.FACT);cls.batch=m.document(ROOT,m.MANIFEST)
        cls.grammar,cls.layout,cls.objects=rederive(ROOT,cls.blob,cls.model)
        cls.classification=next(f for f in load(ROOT,cls.blob,cls.model) if f['evidence_path']=='evidence/data-facts/resident-audio-sequences.json')
        cls.analysis=m.document(ROOT,'evidence/functions/ledger.json')

    def test_all_root_reached_bytes_exact_in_six_complete_objects(self):
        r=m.verify(ROOT,self.blob,self.model,self.fact,self.batch)
        self.assertEqual((r['typed_bytes'],r['whole_CODE_bytes'],r['named_relocations'],r['command_count'],r['root_count']),(5182,5188,90,2400,35))
        self.assertEqual(len(r['objects']),6);self.assertEqual((r['c_bytes'],r['asm_instruction_bytes'],r['padding_credit']),(0,0,0))
        self.assertTrue(all(o['CODE']==o['typed_bytes']+1 for o in r['objects']))
        self.assertEqual(sum(len(o['parts']) for o in r['objects']),7)

    def test_value_outside_typed_operand_range_reject(self):
        for value in (-1,256,True):
            fact=copy.deepcopy(self.fact);command=next(c for c in fact['commands'] if c['command']=='NOTE');command['operands']['ticks']=value
            with self.subTest(value=value),self.assertRaisesRegex(FormatError,'outside typed operand range'):m.validate(ROOT,self.blob,self.model,fact)

    def test_positive_note_sign_boundary_and_channel_range_reject(self):
        for command in [dict(offset=0,command='NOTE',operands=dict(pitch=128,ticks=1)),dict(offset=0,command='HEADER',operands=dict(channel=4,priority=0))]:
            with self.subTest(command=command),self.assertRaises(FormatError):check(command)

    def test_pointer_to_unproved_stream_reject(self):
        for target in ('_audio_c_19F7','_audio_c_13BB','_audio_c_2815'):
            fact=copy.deepcopy(self.fact);command=next(c for c in fact['commands'] if 'target' in c['operands']);command['operands']['target']=target
            with self.subTest(target=target),self.assertRaisesRegex(FormatError,'unproved stream'):m.validate(ROOT,self.blob,self.model,fact)

    def test_stream_crossing_uncovered_zero_reject(self):
        raw=bytearray(self.blob);start=self.model['hunks'][0]['content_offset'];raw[start+0x16e2]=0x89
        with self.assertRaisesRegex(FormatError,'crosses uncovered zero'):discover(bytes(raw),self.model,self.classification,self.grammar)

    def test_handler_binding_change_stales_every_object(self):
        model=copy.deepcopy(self.model);raw=bytearray(self.blob);slot=0x292e+4*(0x83-0x80)
        rel=next(r for r in model['relocations'] if r['source_hunk']==1 and r['source_offset']==slot)
        rel['addend_raw']=0x5d08
        data=next(h for h in model['hunks'] if h['number']==1);raw[data['content_offset']+slot:data['content_offset']+slot+4]=(0x5d08).to_bytes(4,'big')
        self.assertNotEqual(sha256(json_bytes(derive(bytes(raw),model))),self.fact['grammar_sha256'])
        for obj in self.fact['objects']:
            with self.subTest(object=obj['prefix']),self.assertRaisesRegex(FormatError,'stale grammar or handler binding for every stream'):
                m.validate(ROOT,bytes(raw),model,self.fact)

    def test_stale_grammar_rejects_whole_batch(self):
        fact=copy.deepcopy(self.fact);fact['grammar_sha256']='0'*64
        with self.assertRaisesRegex(FormatError,'every stream'):m.verify(ROOT,self.blob,self.model,fact,self.batch)

    def test_raw_carrier_and_unknown_command_reject(self):
        for name in ('RAW','BYTES','dc.b','UNUSED_93'):
            fact=copy.deepcopy(self.fact);fact['commands'][1]['command']=name
            with self.subTest(name=name),self.assertRaises(FormatError):m.validate(ROOT,self.blob,self.model,fact)

    def test_partial_stream_and_object_reject(self):
        for key in ('commands','objects'):
            fact=copy.deepcopy(self.fact);fact[key].pop()
            with self.subTest(key=key),self.assertRaises(FormatError):m.validate(ROOT,self.blob,self.model,fact)

    def test_guessed_gap_command_reject(self):
        fact=copy.deepcopy(self.fact);fact['commands'].append(dict(offset=0x16e3,command='NOTE',operands=dict(pitch=0,ticks=0)))
        with self.assertRaisesRegex(FormatError,'uncovered-zero crossing'):m.validate(ROOT,self.blob,self.model,fact)

    def test_unreached_island_has_no_manufactured_root(self):
        self.assertIn(dict(start=0x19f7,end=0x1a11),self.layout['unproved_intervals'])
        self.assertFalse(any(0x19f7<=c['offset']<0x1a11 for c in self.fact['commands']))
        self.assertEqual(len(self.layout['bindings']),90)
        self.assertEqual(sum(i['end']-i['start'] for i in self.layout['unproved_intervals']),32)

    def test_padding_control_and_all_padding_are_uncredited(self):
        work=ROOT/self.batch['job']/'sys/work';r=m.padding_control(work)
        self.assertEqual((r['CODE'],r['typed_command_end'],r['implicit_assembler_padding'],r['game_credit']),(4,3,1,0))
        self.assertEqual({o['implicit_assembler_padding']['original_offset'] for o in self.fact['objects']},set(ZERO_DEBT))

    def test_code_relocation_and_symbol_inventory_are_exhaustive(self):
        obj=self.fact['objects'][2];rows=[c for c in self.fact['commands'] if obj['start']<=c['offset']<obj['end']-1]
        sem=encode(rows,set(self.layout['proven_labels']));defs=m.expected_definitions(obj,sem);raw=(ROOT/self.batch['job']/('sys/work/'+obj['prefix']+'.o')).read_bytes()
        parsed=m.object_code(raw,obj['CODE'],defs,sem['fixups'])
        self.assertTrue(any(d['references']==7 for d in parsed['definitions']))
        self.assertTrue(any(f['symbol']=='_audio_c_1BA4' for f in parsed['fixups']))
        for key in ('symbol','width','type','addend'):
            fixes=copy.deepcopy(sem['fixups']);fixes[0][key]={'symbol':'','width':2,'type':'MASK','addend':1}[key]
            with self.subTest(key=key),self.assertRaises(FormatError):m.object_code(raw,obj['CODE'],defs,fixes)
        with self.assertRaises(FormatError):m.object_code(raw[:-4],obj['CODE'],defs,sem['fixups'])

    def test_batch_pins_and_omitted_artifacts_reject(self):
        for key in ('receipt_sha256','fact_sha256','artifacts'):
            b=copy.deepcopy(self.batch);b[key]={} if key!='receipt_sha256' else '0'*64
            with self.subTest(key=key),self.assertRaises(FormatError):m.verify(ROOT,self.blob,self.model,self.fact,b)

    def test_measured_canonical_replay_keeps_verifier_provenance_only(self):
        report=m.verify(ROOT,self.blob,self.model,self.fact,self.batch);report['verifier_identity']={'old.py':'provenance'}
        proof=json_bytes(dict(fact=self.fact,comparison=report,regression={'passed':True,'TEST_ONLY':True}))
        dest='recovery/proofs/code-data/'+m.IDENT+'.json';virtual={str(ROOT/dest):proof}
        for o in self.fact['objects']:virtual[str(ROOT/o['source'])]=m.canonical_path(ROOT,o['candidate']).read_bytes()
        ledger={'functions':{},p.MAP:{m.IDENT:dict(state='DATA_LAYOUT_MATCH',fact=m.FACT,sources={o['source']:o['source_sha256'] for o in self.fact['objects']},proof=dest,proof_sha256=sha256(proof))}}
        original=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda path:virtual[str(path)] if str(path) in virtual else original(path)):
            rows=p.rows(ROOT,self.blob,self.model,self.analysis,ledger)
            self.assertEqual(len(rows),6);self.assertTrue(all(o['acceptance'] for o in rows))
        report['typed_bytes']-=1;changed=json_bytes(dict(fact=self.fact,comparison=report,regression={'passed':True}));virtual[str(ROOT/dest)]=changed
        ledger[p.MAP][m.IDENT]['proof_sha256']=sha256(changed)
        with patch.object(Path,'read_bytes',lambda path:virtual[str(path)] if str(path) in virtual else original(path)):
            with self.assertRaisesRegex(FormatError,'no longer rederives'):p.rows(ROOT,self.blob,self.model,self.analysis,ledger)

    def test_accounting_delta_exactly_once_and_unproved_bytes_remain_debt(self):
        from hybrid_image import account
        r=m.verify(ROOT,self.blob,self.model,self.fact,self.batch)
        records=[dict(o,acceptance=True,producer=r['producer']) for o in r['objects']]
        contributions=m.contributions(ROOT,records);self.assertEqual(len(contributions),7)
        _,before=account(self.blob,self.model,[]);_,after=account(self.blob,self.model,contributions)
        self.assertEqual(after['totals'][p.CATEGORY],5182)
        self.assertEqual(after['totals']['file_RAW_ORACLE_DEBT'],before['totals']['file_RAW_ORACLE_DEBT']-5182)
        for gap in self.layout['unproved_intervals']:
            for q in range(gap['start'],gap['end']):self.assertTrue(any(x['hunk']==0 and x['start']<=q<x['end'] and x['category']=='RAW_ORACLE_DEBT' for x in after['ranges']))
        with self.assertRaises(FormatError):account(self.blob,self.model,contributions+contributions)


if __name__=='__main__':unittest.main()
