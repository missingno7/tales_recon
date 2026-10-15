"""Typed CODE-data admission and rejection controls; no canonical writes."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE/'tools'))
from analysis_support import ROOT
from census import _derive_uncached,verify_lock
from common import FormatError,sha256,json_bytes
from audio_sequence_data import payload
from audio_score_grammar import derive,form
import code_data_providers as p
import promote_code_data as promote


class TypedCodeDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify_lock(ROOT);_,files,cls.model=_derive_uncached(ROOT,False);cls.blob=files['DT1:DuckTales']
        cls.fact=p.document(ROOT,p.FACT);cls.batch=p.document(ROOT,p.MANIFEST)
        cls.grammar=derive(cls.blob,cls.model);cls.code=payload(cls.blob,cls.model,0)
        cls.analysis=p.document(ROOT,'evidence/functions/ledger.json')

    def test_exact_complete_object_and_named_relocation(self):
        r=p.verify(ROOT,self.blob,self.model,self.fact,self.batch)
        self.assertEqual((r['category'],r['original']['size'],r['c_bytes'],r['asm_instruction_bytes']),('TYPED_CODE_DATA',72,0,0))
        self.assertEqual(r['comparison']['verdict'],'EQUAL_CANDIDATE')
        self.assertEqual(r['layout']['relocations'],self.fact['relocations'])

    def test_grammar_rederived_without_score_bytes(self):
        raw=bytearray(self.blob);h=self.model['hunks'][0];raw[h['content_offset']+0x16e6]^=0xff
        self.assertEqual(derive(bytes(raw),self.model),self.grammar)

    def test_pointer_alignment_prefetch_and_rewind(self):
        for op in (0,0x33,0x7f):self.assertEqual([form(self.grammar,op,q)['length'] for q in (0,1)],[2,2])
        for op in (0x81,0x84,0x85):
            self.assertEqual([(form(self.grammar,op,p)['length'],form(self.grammar,op,p)['pointer_field']) for p in (0,1)],[(6,2),(5,1)])
        for op in (0x86,0x88):self.assertEqual([form(self.grammar,op,q)['length'] for q in (0,1)],[1,1])
        self.assertEqual(form(self.grammar,0xa0,0)['length'],2)
        self.assertEqual(form(self.grammar,0x8b,0)['length'],3)

    def test_all_44_slots_inventoried_and_unused_reject(self):
        self.assertEqual([x['opcode'] for x in self.grammar['opcodes']],list(range(0x80,0xac)))
        for x in self.grammar['opcodes']:
            if not x['accepted']:
                with self.subTest(opcode=x['opcode']),self.assertRaises(FormatError):form(self.grammar,x['opcode'],0)

    def test_unknown_opcode_reject(self):
        for op in (0xac,0xff):
            code=bytearray(self.code);code[0x16e6]=op
            with self.subTest(opcode=op),self.assertRaisesRegex(FormatError,'unknown or unused'):
                p.typed_stream(code,self.model['relocations'],0x16e4,0x172c,self.grammar)

    def test_unused_opcode_reject(self):
        code=bytearray(self.code);code[0x16e6]=0x83
        with self.assertRaisesRegex(FormatError,'unknown or unused'):p.typed_stream(code,self.model['relocations'],0x16e4,0x172c,self.grammar)

    def test_wrong_grammar_length_reject(self):
        f=copy.deepcopy(self.fact);f['grammar']['opcodes'][-1]['forms'][0]['length']=1
        with self.assertRaisesRegex(FormatError,'grammar'):p.validate_fact(ROOT,self.blob,self.model,f)

    def test_stale_grammar_reject(self):
        f=copy.deepcopy(self.fact);f['grammar']['driver_sha256']='0'*64
        with self.assertRaisesRegex(FormatError,'grammar'):p.validate_fact(ROOT,self.blob,self.model,f)

    def test_driver_dispatch_change_reject(self):
        raw=bytearray(self.blob);raw[self.model['hunks'][0]['content_offset']+0x5a81]^=1
        with self.assertRaises(FormatError):derive(bytes(raw),self.model)

    def test_missing_handler_binding_reject(self):
        m=copy.deepcopy(self.model);m['relocations']=[r for r in m['relocations'] if not(r['source_hunk']==1 and r['source_offset']==0x292e)]
        with self.assertRaises(FormatError):derive(self.blob,m)

    def test_raw_carrier_reject_even_with_rehashed_source_fact(self):
        for raw in (b'\tdc.b 3,0,171,192\n',b'\tincbin "oracle.bin"\n',b'char raw[72];\n'):
            f=copy.deepcopy(self.fact);f['source_sha256']=sha256(raw)
            with self.subTest(raw=raw),self.assertRaises(FormatError):p.validate_fact(ROOT,self.blob,self.model,f)

    def test_unnamed_and_masked_relocations_reject(self):
        for key,value in [('symbol',''),('mask','ffffffff'),('width',2),('type','HUNK_RELOC16'),('addend_raw',0x16f8)]:
            f=copy.deepcopy(self.fact);f['relocations'][0][key]=value
            with self.subTest(key=key),self.assertRaises(FormatError):p.validate_fact(ROOT,self.blob,self.model,f)

    def test_missing_stream_relocation_reject(self):
        rel=[r for r in self.model['relocations'] if r['source_offset']!=0x1728 or r['source_hunk']!=0]
        with self.assertRaises(FormatError):p.typed_stream(self.code,rel,0x16e4,0x172c,self.grammar)

    def test_partial_stream_reject(self):
        f=copy.deepcopy(self.fact);f['original']['end']-=2;f['original']['size']-=2
        with self.assertRaisesRegex(FormatError,'partial'):p.validate_fact(ROOT,self.blob,self.model,f)

    def test_guessed_zero_gap_reject(self):
        f=copy.deepcopy(self.fact);f['original']['start']=0x16e3;f['original']['size']+=1
        with self.assertRaisesRegex(FormatError,'gap'):p.validate_fact(ROOT,self.blob,self.model,f)

    def test_partial_or_unreachable_command_coverage_reject(self):
        with self.assertRaises(FormatError):p.typed_stream(self.code,self.model['relocations'],0x16e4,0x172d,self.grammar)

    def test_producer_pin_reject(self):
        b=copy.deepcopy(self.batch);b['receipt_sha256']='0'*64
        with self.assertRaisesRegex(FormatError,'SHA pins'):p.verify(ROOT,self.blob,self.model,self.fact,b)

    def test_incomplete_or_multiple_job_batch_reject(self):
        b=copy.deepcopy(self.batch);b['facts'].append(p.FACT)
        with self.assertRaises(FormatError):p.verify(ROOT,self.blob,self.model,self.fact,b)

    def test_canonical_map_preserved(self):
        from recovery_state import canonical_state
        state={'schema_version':1,'functions':{},p.MAP:{'retained':{'state':'test'}}}
        self.assertEqual(canonical_state(state)[p.MAP],state[p.MAP])

    def test_source_transaction_boundary(self):
        from recovery_transaction import target
        self.assertEqual(target(ROOT,p.SOURCE,ROOT/'recovery/ledger.json'),ROOT/p.SOURCE)
        with self.assertRaises(FormatError):target(ROOT,'src/recovered/resident/raw.asm',ROOT/'recovery/ledger.json')

    def test_provenance_hashes_do_not_replace_replay(self):
        report=p.verify(ROOT,self.blob,self.model,self.fact,self.batch)
        report['verifier_identity']={'historical.py':'provenance-only'}
        proof=json_bytes(dict(fact=self.fact,comparison=report,regression={'passed':True}))
        dest='recovery/proofs/code-data/'+p.IDENT+'.json';src=p.source(p.document(ROOT,p.RECIPE)).encode('ascii')
        ledger={'functions':{},p.MAP:{p.IDENT:dict(state=p.STATE,fact=p.FACT,source=p.SOURCE,source_sha256=sha256(src),proof=dest,proof_sha256=sha256(proof))}}
        original=Path.read_bytes
        virtual={str(ROOT/dest):proof,str(ROOT/p.SOURCE):src}
        with patch.object(Path,'read_bytes',lambda path:virtual.get(str(path),b'') if str(path) in virtual else original(path)):
            rows=p.rows(ROOT,self.blob,self.model,self.analysis,ledger)
        self.assertEqual(rows[0]['proof_level'],'DATA_LAYOUT_MATCH')

    def test_accounting_delta_once_and_six_gaps_remain_debt(self):
        from hybrid_image import account,CATEGORIES
        r=p.verify(ROOT,self.blob,self.model,self.fact,self.batch);r['acceptance']=True
        c=p.contributions(ROOT,[r]);self.assertIn(p.CATEGORY,CATEGORIES)
        _,base=account(self.blob,self.model,[]);_,after=account(self.blob,self.model,c)
        self.assertEqual(after['totals'][p.CATEGORY],72)
        self.assertEqual(after['totals']['RAW_ORACLE_DEBT'],base['totals']['RAW_ORACLE_DEBT']-72)
        for q in (0x16e3,0x1835,0x1cc5,0x21dd,0x257b,0x2815):
            self.assertTrue(any(x['hunk']==0 and x['start']<=q<x['end'] and x['category']=='RAW_ORACLE_DEBT' for x in after['ranges']))
        with self.assertRaisesRegex(FormatError,'duplicate'):account(self.blob,self.model,c+c)

    def test_failed_regression_gate_reject(self):
        with patch.object(promote,'stage',return_value=(self.fact,{})) as stage:
            with self.assertRaisesRegex(FormatError,'shared regression'):promote.gated(ROOT,b'',{}, {},lambda:{'passed':False},lambda:{'pins':'unchanged'})
            self.assertEqual(stage.call_count,1)

    def test_changed_inputs_during_regression_reject(self):
        with patch.object(promote,'stage',return_value=(self.fact,{})) as stage:
            pins=iter([{'pin':1},{'pin':2}])
            with self.assertRaisesRegex(FormatError,'changed during'):promote.gated(ROOT,b'',{}, {},lambda:{'passed':True},lambda:next(pins))
            self.assertEqual(stage.call_count,1)

    def test_changed_replay_after_regression_reject(self):
        with patch.object(promote,'stage',side_effect=[(self.fact,{}),(self.fact,{'changed':True})]):
            with self.assertRaisesRegex(FormatError,'replay changed'):promote.gated(ROOT,b'',{}, {},lambda:{'passed':True},lambda:{'pin':1})

    def test_unchanged_replay_gate_passes(self):
        with patch.object(promote,'stage',return_value=(self.fact,{})) as stage:
            self.assertEqual(promote.gated(ROOT,b'',{}, {},lambda:{'passed':True},lambda:{'pin':1})[2],{'passed':True})
            self.assertEqual(stage.call_count,2)


if __name__=='__main__':unittest.main()
