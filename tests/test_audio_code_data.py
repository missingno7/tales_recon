"""Positive replay and rejection controls for classified CODE data/score proof."""
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'tools'))
from analysis_support import ROOT
from census import derive,verify_lock
from common import FormatError,sha256
import audio_sequence_data as data
import audio_score_recipe as recipe_tool
import check_data_contribution as checker
import function_census


class Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify_lock(ROOT);_,files,cls.model=derive(ROOT,promotion_evidence=False)
        cls.blob=files['DT1:DuckTales']
        cls.analysis=json.loads((ROOT/'evidence/functions/ledger.json').read_text())
        cls.raw=json.loads((HERE/checker.FACT).read_text())
        cls.fact=data.load(HERE,cls.blob,cls.model,analysis=cls.analysis)[0]
        cls.recipe=json.loads((HERE/checker.RECIPE).read_text())
        cls.asm=(HERE/checker.SOURCE).read_bytes()
        cls.fixtures=HERE/'tests/fixtures/audio-score-16e4'
        cls.obj=bytes.fromhex((cls.fixtures/'score.o.hex').read_text())
        cls.exe=bytes.fromhex((cls.fixtures/'score.exe.hex').read_text())
        cls.sym=(cls.fixtures/'score.sym').read_text()

    def reject_fact(self,fact=None,blob=None,model=None,analysis=None,claimed=()):
        with self.assertRaises(FormatError):
            data.validate(self.raw if fact is None else fact,self.blob if blob is None else blob,
                          self.model if model is None else model,analysis,claimed)


class Classification(Fixture):
    def test_positive_complete_replay_without_acceptance(self):
        self.assertEqual(len(self.fact['layout']['commands']),2406)
        self.assertEqual(len(self.fact['layout']['headers']),35)
        self.assertEqual(len(self.fact['layout']['pointers']),94)
        self.assertEqual(len(self.fact['layout']['residual']),6)
        self.assertFalse(self.fact['source_acceptance']);self.assertIsNone(self.fact['proof_level'])
        self.assertEqual(self.fact['ownership'],'UNKNOWN')

    def test_fixture_hash_rejects(self):
        f=copy.deepcopy(self.raw);f['oracle_sha256']='0'*64;self.reject_fact(f)

    def test_clipped_extent_rejects(self):
        f=copy.deepcopy(self.raw);f['interval']['end']-=1;self.reject_fact(f)

    def test_consumer_hash_rejects(self):
        f=copy.deepcopy(self.raw);f['consumer_anchors'][0]['sha256']='0'*64;self.reject_fact(f)

    def test_missing_consumer_role_rejects(self):
        f=copy.deepcopy(self.raw);f['consumer_anchors'].pop();self.reject_fact(f)

    def test_wrong_dispatch_binding_rejects(self):
        f=copy.deepcopy(self.raw);f['dispatch'][4]['handler']+=2;self.reject_fact(f)

    def test_missing_pointer_relocation_rejects(self):
        m=copy.deepcopy(self.model);m['relocations']=[r for r in m['relocations'] if not(r['source_hunk']==0 and r['source_offset']==0x1728)];self.reject_fact(model=m)

    def test_wrong_pointer_target_hunk_rejects(self):
        m=copy.deepcopy(self.model)
        next(r for r in m['relocations'] if r['source_hunk']==0 and r['source_offset']==0x1728)['target_hunk']=1
        self.reject_fact(model=m)

    def test_extra_relocation_in_data_rejects(self):
        m=copy.deepcopy(self.model);r=copy.deepcopy(next(r for r in m['relocations'] if r['source_hunk']==0 and r['source_offset']==0x1728));r['source_offset']=0x16e6;m['relocations'].append(r);self.reject_fact(model=m)

    def test_unsupported_opcode_even_with_rehashed_interval_rejects(self):
        b=bytearray(self.blob);h=next(h for h in self.model['hunks'] if h['number']==0);b[h['content_offset']+0x13ba]=0xff
        f=copy.deepcopy(self.raw);f['oracle_sha256']=sha256(b);f['interval']['sha256']=sha256(data.payload(b,self.model,0)[0x13b8:0x2816])
        self.reject_fact(f,blob=bytes(b))

    def test_claimed_source_overlap_rejects(self):
        self.reject_fact(claimed=[dict(hunk=0,start=0x13b8,end=0x13c0)])

    def test_strong_entry_rejects(self):
        self.reject_fact(analysis=dict(functions=[dict(hunk=0,start=0x13b8,entry_evidence=[dict(kind='DIRECT_CALL')])]))

    def test_direct_call_into_data_rejects(self):
        self.reject_fact(analysis=dict(functions=[dict(hunk=0,start=0x3000,entry_evidence=[],cfg=[],direct_callees=[dict(hunk=0,offset=0x13b8)])]))

    def test_credit_or_provenance_claim_rejects(self):
        for key,value in (('source_acceptance',True),('proof_level','DATA_LAYOUT_MATCH'),('ownership','GAME_C'),('source_language','ASM')):
            f=copy.deepcopy(self.raw);f[key]=value
            with self.subTest(key=key):self.reject_fact(f)

    def test_zero_filler_cannot_be_erased(self):
        f=copy.deepcopy(self.raw);f['unclassified_zero_offsets'].pop();self.reject_fact(f)

    def test_incoming_relocation_target_not_hunkless(self):
        f=copy.deepcopy(self.raw);f['incoming_relocations'][0]['target_hunk']=1;self.reject_fact(f)

    def test_fact_discovery_ignores_quarantine_and_tracks_removal(self):
        folder=os.environ.get('AUDIO_TEST_TMP')
        with tempfile.TemporaryDirectory(dir=folder) as temp:
            root=Path(temp);p=root/checker.FACT;p.parent.mkdir(parents=True);p.write_text(json.dumps(self.raw))
            q=p.parent/'to_delete/bad.json';q.parent.mkdir();q.write_text('{}')
            before=data.identity(root);self.assertEqual(len(before),1)
            p.write_text(json.dumps(dict(self.raw,comment='classification notes')))
            self.assertNotEqual(before,data.identity(root));p.unlink();self.assertEqual(data.identity(root),{})

    def test_constructor_excludes_all52_phantoms_retains131_references(self):
        census=function_census.Census(self.blob,self.model,[],classified_data=[self.fact])
        self.assertFalse(any(h==0 and 0x13b8<=p<0x2816 for h,p in census.entries))
        self.assertEqual(len(census.non_executable_references),131)
        self.assertIn((0,0x2816),census.entries)
        self.assertTrue(census.valid(0,0x139a));self.assertFalse(census.valid(0,0x13b8))
        with self.assertRaises(FormatError):census.seed(0,0x13b8,dict(kind='DIRECT_CALL'))

    def test_constructor_rejects_known_code_overlap(self):
        with self.assertRaises(FormatError):function_census.Census(self.blob,self.model,[dict(hunk=0,start=0x13b8,end=0x13c0,classification='CODE')],classified_data=[self.fact])

    def test_snapshot_tracks_fact_content_and_removal(self):
        import evidence_snapshot
        with tempfile.TemporaryDirectory(dir=os.environ.get('AUDIO_TEST_TMP')) as temp:
            root=Path(temp);(root/'assets').mkdir();(root/'assets/a').write_bytes(b'independent test asset');(root/'tools').mkdir()
            p=root/checker.FACT;p.parent.mkdir(parents=True);p.write_text(json.dumps(self.raw))
            snap=evidence_snapshot.Snapshot();before=snap.inputs(root,False)
            self.assertIn(str(p.resolve()),before)
            p.write_text(json.dumps(dict(self.raw,comment='notes')));self.assertNotEqual(before,snap.inputs(root,False))
            p.unlink();self.assertNotEqual(before,snap.inputs(root,False))


class CensusIntegration(Fixture):
    def test_full_generated_census_and_review_ranking_have_no_phantoms(self):
        census=function_census.Census(self.blob,self.model,[],classified_data=[self.fact])
        with patch.object(function_census,'ROOT',HERE):generated=census.run()
        self.assertFalse(any(f['hunk']==0 and 0x13b8<=f['start']<0x2816 for f in generated['functions']))
        self.assertFalse(generated['summary']['reconstruction_claimed_by_census'])
        self.assertEqual(generated['data_fact_identity'],data.identity(HERE))
        self.assertEqual(len(generated['non_executable_references']),131)
        import recovery_state
        with patch.object(recovery_state,'evidence',return_value=generated),patch.object(recovery_state,'runtime_dependencies',return_value={}):
            ranking=recovery_state.ranked()
        # The phantom baseline comes from the same census without the fact,
        # so the check holds before and after the generated ledger refresh.
        with patch.object(function_census,'ROOT',HERE):
            baseline=function_census.Census(self.blob,self.model,[],classified_data=[]).run()
        ghosts={f['id'] for f in baseline['functions'] if f['hunk']==0 and 0x13b8<=f['start']<0x2816}
        self.assertEqual(len(ghosts),52)
        self.assertFalse(ghosts & {f['id'] for f in self.analysis['functions']})
        self.assertFalse(ghosts & {r['id'] for r in ranking})



class ExactScore(Fixture):
    def check(self,obj=None,exe=None,sym=None,model=None):
        return checker.compare(self.blob,self.model if model is None else model,self.fact,
                               self.obj if obj is None else obj,self.exe if exe is None else exe,self.sym if sym is None else sym)

    def test_complete_source_output_and_one_internal_binding_are_equal(self):
        self.assertEqual(self.asm,recipe_tool.source(self.recipe).encode('ascii'))
        r=self.check();self.assertEqual(r['verdict'],'EQUAL_CANDIDATE');self.assertEqual(r['ordinary_bytes_compared'],68)
        self.assertEqual(r['fields'][0]['offset'],68);self.assertEqual(r['fields'][0]['target_relative_offset'],18)
        self.assertFalse(r['source_acceptance']);self.assertFalse(r['accounting_acceptance']);self.assertIsNone(r['proof_level'])

    def test_wrong_ordinary_byte_is_differ_even_with_consistent_object_link(self):
        obj=bytearray(self.obj);obj[38]^=1
        exe=bytearray(self.exe);h=checker.parse(exe)['hunks'][0];exe[h['content_offset']+1]^=1
        r=self.check(obj=bytes(obj),exe=bytes(exe));self.assertEqual(r['verdict'],'DIFFER');self.assertEqual(r['differences'][0]['offset'],1)

    def test_wrong_candidate_pointer_cannot_be_normalized(self):
        exe=bytearray(self.exe);h=checker.parse(exe)['hunks'][0];exe[h['content_offset']+71]+=2
        with self.assertRaises(FormatError):self.check(exe=bytes(exe))

    def test_wrong_original_target_is_blocked_not_equal(self):
        model=copy.deepcopy(self.model)
        next(r for r in model['relocations'] if r['source_hunk']==0 and r['source_offset']==0x1728)['addend_raw']+=2
        with self.assertRaises(FormatError):self.check(model=model)

    def test_missing_original_relocation_rejects(self):
        model=copy.deepcopy(self.model);model['relocations']=[r for r in model['relocations'] if not(r['source_hunk']==0 and r['source_offset']==0x1728)]
        with self.assertRaises(FormatError):self.check(model=model)

    def test_extra_original_relocation_rejects(self):
        model=copy.deepcopy(self.model);r=copy.deepcopy(next(r for r in model['relocations'] if r['source_hunk']==0 and r['source_offset']==0x1728));r['source_offset']=0x16e6;model['relocations'].append(r)
        with self.assertRaises(FormatError):self.check(model=model)

    def test_clipped_object_rejects(self):
        obj=bytearray(self.obj);obj[13]=70
        with self.assertRaises(FormatError):self.check(obj=bytes(obj))

    def test_nonlocal_object_fixup_rejects(self):
        obj=bytearray(self.obj);p=obj.index(b'\xfd\x71');obj[p+1]=0x70
        with self.assertRaises(FormatError):self.check(obj=bytes(obj))

    def test_nonzero_object_fixup_addend_rejects(self):
        obj=bytearray(self.obj);p=obj.index(b'\xfd\x71');obj[p+5]=1
        with self.assertRaises(FormatError):self.check(obj=bytes(obj))

    def test_symbol_map_pointer_alias_rejects(self):
        with self.assertRaises(FormatError):self.check(sym=self.sym.replace('00000012 _score_pattern','00000014 _score_pattern'))

    def test_recipe_forbids_raw_or_fixed_pointer_inputs(self):
        for key,value in (('raw_bytes','0000'),('org',0x16e4),('target_address',0x16f6)):
            recipe=copy.deepcopy(self.recipe);recipe[key]=value
            with self.subTest(key=key),self.assertRaises(FormatError):recipe_tool.source(recipe)

    def test_retained_candidate_fixtures_are_pinned_independent_outputs(self):
        provenance=json.loads((self.fixtures/'producer.json').read_text())
        self.assertEqual(sha256(self.obj),provenance['object_sha256']);self.assertEqual(sha256(self.exe),provenance['linked_sha256'])


class FreshProducer(Fixture):
    def setUp(self):
        name=os.environ.get('AUDIO_DATA_JOB')
        if not name:self.skipTest('set AUDIO_DATA_JOB to a fresh pinned score job to audit complete producer')
        self.job=Path(name).resolve()

    def test_complete_fresh_producer_passes(self):
        r=checker.verify(ROOT,self.job,self.blob,self.model,self.fact,self.recipe,self.asm)
        self.assertEqual(r['verdict'],'EQUAL_CANDIDATE')

    def changed_job(self,mutate,recipe=None,asm=None):
        with tempfile.TemporaryDirectory(dir=os.environ.get('AUDIO_TEST_TMP')) as temp:
            job=Path(temp)/'job';shutil.copytree(self.job,job)
            # Move the same isolated producer layout naturally to the test job.
            config=(job/'worker.uae').read_text().replace(str(self.job),str(job));(job/'worker.uae').write_text(config)
            request=json.loads((job/'request.json').read_text());request['config_sha256']=sha256((job/'worker.uae').read_bytes())
            receipt=json.loads((job/'result.json').read_text());mutate(job,request,receipt)
            receipt['request']=request;(job/'request.json').write_text(json.dumps(request));(job/'result.json').write_text(json.dumps(receipt))
            with self.assertRaises(FormatError):checker.verify(ROOT,job,self.blob,self.model,self.fact,self.recipe if recipe is None else recipe,self.asm if asm is None else asm)

    def test_omitted_pinned_tool_inventory_rejects(self):
        self.changed_job(lambda job,r,v:r['pinned_inputs'].pop())

    def test_rehashed_source_edit_still_rejects(self):
        def mutate(job,r,v):
            p=job/'sys/work/score.asm';p.write_bytes(p.read_bytes().replace(b'NOTE\t51,4',b'NOTE\t52,4'))
            digest=sha256(p.read_bytes());r['source_files'][0]['sha256']=digest
            artifact=next(x for x in v['artifacts'] if x['path']=='score.asm');artifact['sha256']=digest;artifact['size']=p.stat().st_size
        self.changed_job(mutate)

    def test_consistently_rehashed_source_recipe_cannot_reuse_stale_object(self):
        recipe=copy.deepcopy(self.recipe);recipe['events'][0]['pitch']='E'
        asm=recipe_tool.source(recipe).encode('ascii')
        def mutate(job,r,v):
            p=job/'sys/work/score.asm';p.write_bytes(asm);digest=sha256(asm)
            r['source_files'][0]['sha256']=digest
            item=next(x for x in v['artifacts'] if x['path']=='score.asm');item.update(sha256=digest,size=len(asm))
        self.changed_job(mutate,recipe=recipe,asm=asm)

    def test_omitted_artifact_inventory_rejects(self):
        self.changed_job(lambda job,r,v:v['artifacts'].pop())

    def test_rehashed_extra_oracle_mount_rejects(self):
        def mutate(job,r,v):
            p=job/'worker.uae';p.write_text(p.read_text()+'filesystem2=ro,DH9:Oracle:assets,-128\n');r['config_sha256']=sha256(p.read_bytes())
        self.changed_job(mutate)

    def test_rehashed_guest_command_change_rejects(self):
        def mutate(job,r,v):
            p=job/'sys/s/startup-sequence';p.write_text(p.read_text().replace('as -o score.o','as -o fake.o'));r['guest_script_sha256']=sha256(p.read_bytes())
        self.changed_job(mutate)

    def test_guest_os_copy_edit_rejects(self):
        def mutate(job,r,v):
            p=next(p for p in (job/'sys/c').rglob('*') if p.is_file());p.write_bytes(p.read_bytes()+b'changed')
        self.changed_job(mutate)

    def test_source_inventory_empty_rejects(self):
        self.changed_job(lambda job,r,v:r['source_files'].clear())


if __name__=='__main__':unittest.main()
