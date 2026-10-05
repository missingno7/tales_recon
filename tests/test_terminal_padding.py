"""Strict serialization-only padding from real source-produced full-node input."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import ExitStack
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from analysis_support import game,ROOT
from common import FormatError,sha256,write_json
from recovery_state import evidence
from recovery_evidence import load_promotions,terminal_padding_recipe,load_terminal_padding,PADDING_INPUT
from compiler_oracle import cached
from hunk import parse
from hybrid_image import account
from evidence_snapshot import snapshot


class TerminalPaddingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob,cls.model,_=game();cls.analysis=evidence()
        cls.ledger=json.loads((ROOT/'recovery/ledger.json').read_text())
        cls.promotions=load_promotions(ROOT,cls.blob,cls.model,cls.analysis)
        cls.temp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temp.cleanup)
        cls.base=Path(cls.temp.name)/'base';cls.base.mkdir()
        for fid,item in cls.ledger['functions'].items():
            if not fid.startswith('ov04_'):continue
            for rel in (item['source'],item['proof']):
                target=cls.base/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,target)
            proof=json.loads((ROOT/item['proof']).read_text());unit=proof['comparison'].get('complete_unit_receipt')
            if unit:
                for source in ((ROOT/unit),(ROOT/unit).with_name('unit.c')):
                    target=cls.base/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        runtime='evidence/experiments/runtime-arithmetic.json'
        p=cls.base/runtime;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/runtime,p)
        recipe,_,_,combined,_=terminal_padding_recipe(cls.base,cls.blob,cls.model,cls.analysis,cls.promotions,cls.ledger,'ov04_F_1E36')
        cls.compiled=cached(recipe['cache_key'])
        if cls.compiled is None:raise unittest.SkipTest('current canonical full ov04 cache absent')
        c=cls.compiled;cache=Path(c['directory']);prefix=c['prefix']
        exe=(cache/(prefix+'.exe')).read_bytes();model=parse(exe)
        h=next(h for h in model['hunks'] if h['number']==c['contribution']['hunk'])
        pad=exe[h['content_offset']+recipe['start']:h['content_offset']+recipe['end']]
        path='evidence/rules/ov04-terminal-padding/unit.c';p=cls.base/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(combined,encoding='ascii',newline='\n')
        hashes=[sha256((cache/((prefix if label=='candidate' else prefix+'_'+label)+'.o')).read_bytes())
                for label in recipe['compiler']['object_labels']]
        claim=dict(entry='ov04_F_1E36',recipe=recipe,unit_source=dict(path=path,sha256=sha256(combined.encode('ascii'))),
                   object_sha256s=hashes,executable_sha256=sha256(exe),padding_sha256=sha256(pad))
        cls.document=dict(schema_version=1,game_sha256=sha256(cls.blob),claims=[claim])
        cls.exe=exe;cls.h=h

    def setUp(self):
        self.temp_case=tempfile.TemporaryDirectory();self.addCleanup(self.temp_case.cleanup)
        self.root=Path(self.temp_case.name)/'repo';shutil.copytree(self.base,self.root)
        self.doc=copy.deepcopy(self.document)

    def validate(self,doc=None,**kwargs):
        # Any branch requiring a new game/census read is a test failure.
        with patch('analysis_support.game',side_effect=AssertionError('recursive game read')), \
             patch('owned_code_data.game',side_effect=AssertionError('recursive word-tail game read')), \
             patch('check_unit.recovery',side_effect=AssertionError('unsupplied ledger')):
            return load_terminal_padding(self.root,self.blob,self.model,kwargs.get('analysis',self.analysis),
                self.promotions,kwargs.get('ledger',self.ledger),document=self.doc if doc is None else doc)

    def test_live_supplied_context_produces_only_two_padding_bytes(self):
        contributions=self.validate()
        self.assertEqual(contributions,[dict(id='ov04_terminal_hunk_padding',hunk=4,start=10766,end=10768,
            category='CLASSIFIED_PADDING',bytes=b'\0\0',relocations=[])])
        _,report=account(self.blob,self.model,contributions)
        self.assertEqual(report['totals']['CLASSIFIED_PADDING'],2)
        self.assertIsNone(report['reconstruction_proof_level'])
        self.assertEqual(report['by_overlay']['ov04']['RAW_ORACLE_DEBT'],10766)

    def test_legacy_absence_has_no_contributions(self):
        with patch('analysis_support.game',side_effect=AssertionError('legacy game read')):
            self.assertEqual(load_terminal_padding(self.root,self.blob,self.model,self.analysis,self.promotions,self.ledger),[])

    def test_supplied_context_reaches_natural_owned_literal_replay(self):
        from check_unit import compare_unit
        recipe,members,names,source,context=terminal_padding_recipe(self.root,self.blob,self.model,self.analysis,self.promotions,self.ledger,'ov04_F_1E36')
        natural=dict(members=[dict(id=m['id'],role='canonical') for m in members],blocked_reason=None)
        with patch('analysis_support.game',side_effect=AssertionError('natural game read')), \
             patch('owned_code_data.game',side_effect=AssertionError('natural word-tail read')), \
             patch('check_unit.recovery',side_effect=AssertionError('natural ledger read')):
            report=compare_unit(members,names,self.compiled,self.analysis['a4']['bias'],owned_code_data=True,
                                source_text=source,natural=natural,context=context)
        self.assertEqual(report['verdict'],'EQUAL')

    def test_runtime_alias_branch_uses_supplied_original_context(self):
        from function_compare import compare_function,runtime_symbol_names
        runtime=json.loads((self.root/'evidence/experiments/runtime-arithmetic.json').read_text())
        name=next(iter(runtime_symbol_names(runtime)));(self.root/'candidate.exe').write_bytes(b'\0'*64)
        f=dict(id='ov04_F_0000',hunk=4,start=0,end=2,size=2,raw_bytes='4e75',extent_status='CLOSED_CFG',
               referenced_data=[],direct_callees=[],relocations=[])
        c=dict(status='COMPILED',identity=dict(profile='aztec36',flags=[]),cache_key='context',cache_hit=True,
            directory=str(self.root),prefix='candidate',contribution=dict(code_hex='4e75',hunk=3,data_size=0,bss_size=0,
            symbols=[dict(hunk=0,offset=0,name=name)],relocations=[],all_relocations=[],
            hunks=[dict(number=0,content_offset=0),dict(number=1,initialized_size=0,allocated_size=0),dict(number=2,allocated_size=4)]))
        context=dict(root=self.root,blob=self.blob,model=self.model)
        with patch('analysis_support.game',side_effect=AssertionError('runtime game read')), \
             patch('runtime_arithmetic.aliases',return_value=([],[])) as aliases:
            result=compare_function(f,c,self.analysis['a4']['bias'],source_text='recovered(){}',context=context)
        self.assertEqual(result['verdict'],'EQUAL')
        self.assertIs(aliases.call_args.args[2],self.blob);self.assertIs(aliases.call_args.args[3],self.model)

    def test_missing_wrong_reordered_members_objects_bounds_and_profiles_reject(self):
        changes=[lambda r:r.update(hunk=3),lambda r:r.update(node='ov03'),lambda r:r.update(start=10765),
            lambda r:r.update(end=10769),lambda r:r.update(interval=[2,10768]),
            lambda r:r['member_dependencies'].pop(),lambda r:r['member_dependencies'].reverse(),
            lambda r:r['object_partition'].pop(),lambda r:r['object_partition'].reverse(),
            lambda r:r['object_partition'][1].reverse(),lambda r:r['proven_groups'].clear(),
            lambda r:r['compiler'].update(profile='aztec36'),lambda r:r['compiler']['same_overlay_exports']['members'].clear(),
            lambda r:r.update(cache_key='0'*64)]
        for change in changes:
            with self.subTest(change=change):
                bad=copy.deepcopy(self.doc);change(bad['claims'][0]['recipe'])
                with self.assertRaisesRegex(FormatError,'recipe does not re-derive'):self.validate(bad)
        bad=copy.deepcopy(self.doc);bad['claims'][0]['entry']='ov04_F_UNKNOWN'
        with self.assertRaises(FormatError):self.validate(bad)

    def test_source_proof_group_and_retained_raw_source_edits_reject(self):
        recipe=self.doc['claims'][0]['recipe']
        paths=[recipe['member_dependencies'][0]['source'],recipe['member_dependencies'][0]['proof'],
               recipe['unit_dependencies'][0]['path'],self.doc['claims'][0]['unit_source']['path']]
        for path in paths:
            with self.subTest(path=path):
                p=self.root/path;original=p.read_bytes();p.write_bytes(original+b' ')
                try:
                    with self.assertRaises(FormatError):self.validate()
                finally:p.write_bytes(original)

    def test_consistently_rehashed_canonical_change_invalidates_old_recipe(self):
        ledger=copy.deepcopy(self.ledger);fid='ov04_F_1E36';item=ledger['functions'][fid]
        p=self.root/item['source'];raw=p.read_bytes()+b'\n';p.write_bytes(raw);item['source_sha256']=sha256(raw)
        proof_path=self.root/item['proof'];proof=json.loads(proof_path.read_bytes());proof['source_sha256']=item['source_sha256']
        write_json(proof_path,proof);item['proof_sha256']=sha256(proof_path.read_bytes())
        with self.assertRaisesRegex(FormatError,'recipe does not re-derive'):self.validate(ledger=ledger)

    def test_literal_and_artifact_changes_reject_even_at_same_size(self):
        modified=copy.deepcopy(self.compiled);raw=bytearray.fromhex(modified['contribution']['code_hex']);raw[9518]^=1
        modified['contribution']['code_hex']=raw.hex()
        import compiler_oracle
        original_cached=compiler_oracle.cached
        def altered(key):return modified if key==self.doc['claims'][0]['recipe']['cache_key'] else original_cached(key)
        with patch('compiler_oracle.cached',side_effect=altered):
            with self.assertRaisesRegex(FormatError,'complete member verification failed'):self.validate()
        for field in ('executable_sha256','padding_sha256'):
            bad=copy.deepcopy(self.doc);bad['claims'][0][field]='0'*64
            with self.subTest(field=field),self.assertRaises(FormatError):self.validate(bad)
        bad=copy.deepcopy(self.doc);bad['claims'][0]['object_sha256s'].reverse()
        with self.assertRaisesRegex(FormatError,'object hashes'):self.validate(bad)

    def test_real_cached_reextraction_rejects_same_size_nonzero_pad(self):
        # Work on an isolated cache copy. No original or real cache artifact
        # is patched; this negative specimen cannot become an accepted output.
        cache=self.root/'negative-cache';dest=cache/self.compiled['cache_key'];shutil.copytree(self.compiled['directory'],dest)
        prefix=self.compiled['prefix'];p=dest/(prefix+'.exe');raw=bytearray(p.read_bytes())
        raw[self.h['content_offset']+10766]=1;p.write_bytes(raw)
        receipt=json.loads((dest/'receipt.json').read_bytes())
        for artifact in receipt['artifacts']:
            if artifact['path']==p.name:artifact['sha256']=sha256(raw)
        write_json(dest/'receipt.json',receipt)
        import compiler_oracle
        original_cached=compiler_oracle.cached
        def changed_cache(key):
            if key==self.compiled['cache_key']:
                with patch('compiler_oracle.CACHE',cache):return original_cached(key)
            return original_cached(key)
        with patch('compiler_oracle.cached',side_effect=changed_cache),self.assertRaisesRegex(FormatError,'nonzero HUNK padding'):self.validate()

    def test_relocation_or_analyzed_reference_into_pad_rejects(self):
        for kind in ('referenced_data','direct_callees'):
            analysis=copy.deepcopy(self.analysis)
            f=next(f for f in analysis['functions'] if f['id']=='ov04_F_0000')
            ref=dict(hunk=4,offset=10766)
            if kind=='referenced_data':ref.update(kind='A4_RELATIVE',instruction_offset=f['start'])
            else:ref.update(id='padding_nonentry',site=f['start'],basis='PC_RELATIVE')
            f[kind].append(ref)
            with self.subTest(kind=kind),self.assertRaisesRegex(FormatError,'incoming analyzed reference'):self.validate(analysis=analysis)

    def test_extra_code_allocation_rejects_even_with_consistently_rehashed_artifact(self):
        import compiler_oracle
        cache=self.root/'allocation-cache';dest=cache/self.compiled['cache_key'];shutil.copytree(self.compiled['directory'],dest)
        prefix=self.compiled['prefix'];p=dest/(prefix+'.exe');raw=bytearray(p.read_bytes());model=parse(raw)
        node=next(n for n in model['nodes'] if self.h['number'] in n['hunks'])
        at=node['header_offset']+20
        raw[at:at+4]=(int.from_bytes(raw[at:at+4],'big')+1).to_bytes(4,'big');p.write_bytes(raw)
        receipt=json.loads((dest/'receipt.json').read_bytes())
        for artifact in receipt['artifacts']:
            if artifact['path']==p.name:artifact['sha256']=sha256(raw)
        receipt['contribution']=compiler_oracle.extract(dest,prefix,self.compiled['identity']['object_labels'],
            self.compiled['identity'].get('entry_function','recovered'),self.compiled['identity'].get('same_overlay_exports'))
        write_json(dest/'receipt.json',receipt)
        doc=copy.deepcopy(self.doc);doc['claims'][0]['executable_sha256']=sha256(raw)
        original_cached=compiler_oracle.cached
        def changed_cache(key):
            if key==self.compiled['cache_key']:
                with patch('compiler_oracle.CACHE',cache):return original_cached(key)
            return original_cached(key)
        with patch('compiler_oracle.cached',side_effect=changed_cache),self.assertRaisesRegex(FormatError,'produced hunk/bounds'):self.validate(doc)

    def test_default_input_is_reread_inside_an_existing_snapshot_scope(self):
        path=self.root/PADDING_INPUT;write_json(path,self.doc)
        with snapshot():
            self.assertEqual(len(load_terminal_padding(self.root,self.blob,self.model,self.analysis,self.promotions,self.ledger)),1)
            bad=copy.deepcopy(self.doc);bad['claims'][0]['padding_sha256']='0'*64;write_json(path,bad)
            with self.assertRaises(FormatError):load_terminal_padding(self.root,self.blob,self.model,self.analysis,self.promotions,self.ledger)


if __name__=='__main__':unittest.main()
