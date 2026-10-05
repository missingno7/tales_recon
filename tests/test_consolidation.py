import copy
import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from common import FormatError,sha256,write_json
from repo_paths import active_files,is_active_repo_path,canonical_path,candidate_path
import declaration_views as dv
import type_evidence as te
import recovery_state as rs
from evidence_snapshot import Snapshot
from hybrid_image import account,build
from aj import parse_external_words,linked_pc_bindings
from runtime_cfg import analyze


class QuarantineTests(unittest.TestCase):
    def test_conflicting_quarantine_cannot_enter_source_type_or_declaration_views(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for folder in ['src','recovery','to_delete/src','src/to_delete','build','src/__pycache__']:(root/folder).mkdir(parents=True,exist_ok=True)
            (root/'src/good.c').write_text('extern int G_h01_1234;\n')
            for relative in ['to_delete/src/bad.c','src/to_delete/bad.c','build/bad.c','src/__pycache__/bad.c']:
                (root/relative).write_text('struct Flags { long contamination; };\nextern long G_h01_1234;\n')
            write_json(root/'recovery/ledger.json',dict(functions={'good':dict(source='src/good.c'),'bad':dict(source='to_delete/src/bad.c')}))
            self.assertEqual(dv.canonical_sources(root),['src/good.c'])
            self.assertEqual(list(te._declarations(root)),['G_h01_1234'])
            self.assertEqual(len(te._declarations(root)['G_h01_1234']),1)
            self.assertEqual([p.relative_to(root).as_posix() for p in active_files(root,'.c')],['src/good.c'])
            for relative in ['to_delete/src/bad.c','src/to_delete/bad.c','build/bad.c']:
                with self.assertRaises(FormatError):canonical_path(root,relative)
            with self.assertRaises(FormatError):candidate_path(root,root/'to_delete/src/bad.c')
            self.assertEqual(candidate_path(root,root/'build/bad.c'),root/'build/bad.c')

    def test_snapshot_and_canonical_validation_reject_quarantined_proof_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'recovery').mkdir();(root/'to_delete').mkdir()
            write_json(root/'recovery/ledger.json',dict(functions={'bad':dict(source='to_delete/bad.c',proof='to_delete/bad.json')}))
            with patch('census.inputs',return_value=[]):
                with self.assertRaisesRegex(FormatError,'outside active'):Snapshot().inputs(root,True)
            from recovery_evidence import load_promotions
            item=dict(state='FUNCTION_CODE_MATCH',source='to_delete/bad.c',proof='to_delete/bad.json')
            write_json(root/'recovery/ledger.json',dict(functions={'bad':item}))
            with self.assertRaisesRegex(FormatError,'outside active'):load_promotions(root,b'',{}, {})

    def test_fresh_context_and_ranking_ignore_quarantine(self):
        # Add deliberately conflicting source to the actual quarantine. It must
        # have no effect on an active worker packet, ranking, or hybrid output.
        target=ROOT/'to_delete/isolation-control.c'
        before=(rs.facts('ov04_F_0536',max_instructions=1000,max_bytes=150000),rs.ranked('ov04'),build()[1])
        if target.exists():self.fail('isolation fixture already exists')
        target.write_text('struct Flags { long corrupt; }; recovered(){return 666;}\n')
        try:
            after=(rs.facts('ov04_F_0536',max_instructions=1000,max_bytes=150000),rs.ranked('ov04'),build()[1])
            self.assertEqual(before,after)
            self.assertEqual(after[0]['previous_attempts'],[])
            self.assertEqual(after[0]['previous_sources'],{})
        finally:
            # Preserve even this newly created control under quarantine.
            target.rename(ROOT/('to_delete/isolation-control-'+uuid.uuid4().hex+'.c'))


class AccountingTests(unittest.TestCase):
    def test_complete_real_file_is_accounted_without_source_increase(self):
        output,report=build();t=report['totals']
        self.assertEqual((len(output),t['RECOVERED_C'],t['file_RAW_ORACLE_DEBT']),(193004,38604,152988))
        self.assertEqual((t['overlap'],t['unaccounted']),(0,0))
        self.assertIsNone(report['reconstruction_proof_level'])

    def test_negative_overlap_extent_bytes_and_relocations(self):
        from analysis_support import game
        blob,model,_=game();h=model['hunks'][4];raw=blob[h['content_offset']:h['content_offset']+12]
        c=dict(id='test',hunk=4,start=0,end=12,bytes=raw,category='RECOVERED_C')
        account(blob,model,[c])
        for contributions in [[c,dict(c,id='overlap')],[dict(c,end=13)],[dict(c,start=-1,end=11)],
                              [dict(c,bytes=b'\0'*12)],[dict(c,relocations=[dict(source_offset=0)])]]:
            with self.assertRaises(FormatError):account(blob,model,contributions)


class AJControls(unittest.TestCase):
    def test_repeated_names_swapped_names_and_shifted_sites(self):
        root=ROOT/'evidence/rules/aj-external-fixups/controls'
        refs=lambda name:parse_external_words((root/(name+'.o')).read_bytes())['external_references']
        self.assertEqual([(r['offset'],r['symbol']) for r in refs('two')],[(2,'_alpha'),(6,'_alpha')])
        self.assertEqual([r['symbol'] for r in refs('names')],['_alpha','_beta'])
        self.assertEqual([r['symbol'] for r in refs('swap')],['_beta','_alpha'])
        self.assertEqual(refs('shift')[0]['offset']-refs('one')[0]['offset'],2)
        self.assertEqual(refs('far')[0]['offset'],302)
        self.assertEqual(refs('ffp')[0]['symbol'],'.Fflt')
        self.assertEqual(refs('plain'),[])
        with self.assertRaises(FormatError):refs('long')

    def test_unsupported_truncated_corrupt_and_wrong_natural_binding(self):
        root=ROOT/'evidence/rules/aj-external-fixups/controls';b=(root/'one.o').read_bytes()
        for mutant in [b[:-1],b[:36]+b'\xff'+b[37:],b[:40]+b'\x7f'+b[41:]]:
            with self.assertRaises(FormatError):parse_external_words(mutant)
        p=parse_external_words(b)
        self.assertEqual(linked_pc_bindings(p,bytes.fromhex('4eba00044e75'),{'_alpha':6})[0]['target'],6)
        with self.assertRaises(FormatError):linked_pc_bindings(p,bytes.fromhex('4eba00044e75'),{'_alpha':8})


class RuntimeObservationTests(unittest.TestCase):
    def test_single_step_observation_never_closes_target_set(self):
        blob=bytes.fromhex('4ed04e75');h=dict(number=4,node='ov04',type='CODE',initialized_size=4,content_offset=0,sha256=sha256(blob))
        doc=dict(game_sha256=sha256(blob),events=[dict(kind='LOAD',epoch='one',hunk=4,node='ov04',base=4096,content_sha256=sha256(blob)),
             dict(kind='PC',epoch='one',pc=4096,opcode_hex='4ed0',next_pc=4098,acquisition='SINGLE_STEP',exception=False)])
        result=analyze(doc,blob,dict(hunks=[h]));self.assertEqual(result['indirect_edges'][0]['confidence'],'OBSERVED_EDGE')
        self.assertFalse(result['indirect_edges'][0]['all_targets_proved']);self.assertIsNone(result['proof_level'])
        doc['events'][-1]['acquisition']='HISTORY'
        self.assertEqual(analyze(doc,blob,dict(hunks=[h]))['indirect_edges'][0]['confidence'],'CANDIDATE_HISTORY_EDGE')
        doc['events'].insert(1,dict(kind='UNLOAD',epoch='one'))
        with self.assertRaises(FormatError):analyze(doc,blob,dict(hunks=[h]))
