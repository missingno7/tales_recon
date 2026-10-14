"""Exact provider controls. Fixtures are independently compiled, never oracle CODE."""
import copy
import shutil
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'tools'))
import data_providers as dp
from common import FormatError
from hunk import parse
from analysis_support import ROOT,game
from recovery_state import canonical_state


class DataProviderControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=ROOT/'build/worker-jobs/tu-layout-d-001'
        cls.recipe=json.loads((HERE/'evidence/data-providers/producer.json').read_bytes())
        cls.files={n:(cls.retained/'sys/work'/n).read_bytes() for n in cls.recipe['artifacts']}
        cls.batch=[json.loads((HERE/n).read_bytes()) for n in json.loads((HERE/'evidence/data-providers/batch.json').read_bytes())['facts']]
        cls.facts=[f for f in cls.batch if f['id'] in ['resident_data_1608','resident_data_1708']]
        cls.blob,cls.model,_=game()
        cls.analysis=dp.document(ROOT,'evidence/functions/ledger.json');cls.ledger=dp.document(ROOT,'recovery/ledger.json')
        # typed_evidence receives verified caller IDs from the normal loader.
        # The complete scratch verification separately invokes load_promotions.
        cls.promotions=[dict(id=k) for k in cls.ledger['functions']]

    def compare(self,fact=None,obj=None,linked=None,map_text=None,model=None):
        f=fact or self.facts[0];p=f['producer']['prefix']
        return dp.compare_data(self.blob,model or self.model,f,obj or self.files[p+'.o'],linked or self.files[p+'.exe'],map_text or self.files[p+'.sym'].decode())

    def proposed_document(self,root,path):
        p=HERE/path
        return json.loads(p.read_bytes()) if str(path).startswith('evidence/data-providers/') and p.is_file() else self.original_document(root,path)

    def producer_check(self,fact=None,temporary=None,recipe=None):
        self.original_document=dp.document
        def doc(root,path):
            return recipe if recipe is not None and path=='evidence/data-providers/producer.json' else self.proposed_document(root,path)
        original_candidate=dp.candidate_path
        def candidate(root,path):
            path=original_candidate(root,path)
            # Keep the original absolute job coordinate for environment validation;
            # only explicitly requested files redirect into a task-local copy.
            if temporary and path!=self.retained and path.is_relative_to(self.retained):return temporary/path.relative_to(self.retained)
            return path
        with patch.object(dp,'document',doc),patch.object(dp,'candidate_path',candidate):
            return dp.producer(ROOT,fact or self.facts[0],None)

    def retained_copy(self):
        directory=HERE/'build/workers/sol-tu-layout/test-scratch';directory.mkdir(parents=True,exist_ok=True)
        temporary=tempfile.TemporaryDirectory(dir=directory);root=Path(temporary.name)
        for name in ['request.json','result.json','worker.uae','kick.rom','sys/s/startup-sequence']:
            target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((self.retained/name).read_bytes())
        for name in self.recipe['artifacts']:
            target=root/'sys/work'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(self.files[name])
        return temporary,root

    def repin_receipts(self,root):
        recipe=copy.deepcopy(self.recipe)
        recipe['request_sha256']=dp.sha256((root/'request.json').read_bytes());recipe['result_sha256']=dp.sha256((root/'result.json').read_bytes());recipe['cache_key']=dp.batch_key(recipe)
        return recipe

    def test_full_current_producer_inventory(self):
        files,proof=self.producer_check()
        self.assertEqual(files['p1608.c'],dp.source(self.facts[0]));self.assertEqual(proof['cache_key'],self.recipe['cache_key'])
        self.assertEqual(proof['job'],'build/worker-jobs/tu-layout-d-001')

    def test_missing_job_requires_explicit_regeneration(self):
        self.original_document=dp.document
        with patch.object(dp,'document',self.proposed_document),patch.object(dp,'candidate_path',lambda r,p:HERE/'absent-data-producer'):
            with self.assertRaisesRegex(FormatError,'Missing DATA producer artifact.*Regenerate.*data_provider_job.py'):dp.producer(ROOT,self.facts[0])

    def test_no_embedded_request_result_or_artifact_bytes(self):
        text=(HERE/'evidence/data-providers/producer.json').read_text()
        self.assertNotIn('base64',text);self.assertNotIn('pinned_inputs',text);self.assertNotIn('all_steps_succeeded',text)
        self.assertEqual({f['producer']['batch'] for f in self.batch},{'evidence/data-providers/producer.json'})
        self.assertEqual(len(self.recipe['members']),5)

    def test_consistently_rehashed_missing_tool_inventory_rejected(self):
        temporary,root=self.retained_copy()
        try:
            request=json.loads((root/'request.json').read_bytes());request['pinned_inputs'].pop()
            receipt=json.loads((root/'result.json').read_bytes());receipt['request']=request
            (root/'request.json').write_text(json.dumps(request));(root/'result.json').write_text(json.dumps(receipt))
            with self.assertRaisesRegex(FormatError,'pinned compiler/header inventory'):self.producer_check(temporary=root,recipe=self.repin_receipts(root))
        finally:temporary.cleanup()

    def test_consistently_rehashed_oracle_mount_rejected(self):
        temporary,root=self.retained_copy()
        try:
            config=(root/'worker.uae').read_bytes()+b'filesystem2=ro,DH8:Game:assets,-128\n';(root/'worker.uae').write_bytes(config)
            request=json.loads((root/'request.json').read_bytes());request['config_sha256']=dp.sha256(config)
            receipt=json.loads((root/'result.json').read_bytes());receipt['request']=request
            (root/'request.json').write_text(json.dumps(request));(root/'result.json').write_text(json.dumps(receipt))
            with self.assertRaisesRegex(FormatError,'oracle or changed producer mount'):self.producer_check(temporary=root,recipe=self.repin_receipts(root))
        finally:temporary.cleanup()

    def test_deleted_producer_artifact_rejected(self):
        temporary,root=self.retained_copy()
        try:
            (root/'sys/work/p1608.asm').unlink()
            with self.assertRaisesRegex(FormatError,'Missing DATA producer artifact'):self.producer_check(temporary=root)
        finally:temporary.cleanup()

    def test_changed_artifact_hash_rejected(self):
        temporary,root=self.retained_copy()
        try:
            (root/'sys/work/p1322.o').write_bytes(self.files['p1322.o']+b'x')
            with self.assertRaisesRegex(FormatError,'producer artifact changed'):self.producer_check(temporary=root)
        finally:temporary.cleanup()

    def test_two_complete_typed_objects(self):
        for fact in self.facts:
            result=self.compare(fact)
            self.assertEqual(result['verdict'],'EQUAL_CANDIDATE')
            self.assertEqual(result['sections'],dict(CODE=0,DATA=8,BSS=0,COMMON=0))
            self.assertEqual(result['original_relocations'],[])

    def test_current_canonical_typed_accesses_and_bounds(self):
        for fact in self.facts:
            rows=dp.typed_evidence(ROOT,fact,self.analysis,self.ledger,self.promotions)
            self.assertEqual([r['bytes'] for r in rows],[2,2,2,2])
            self.assertTrue(all(r['bounds']=='SCALAR_ABI' for r in rows))

    def test_rehashed_byte_array_source_rejected(self):
        fact=self.facts[0]
        with self.assertRaises(FormatError):
            dp.verify(ROOT,self.blob,self.model,self.analysis,self.ledger,self.promotions,fact,b'unsigned char blob[8] = {0,98,0,130,0,179,4,216};\n',self.retained)

    def test_byte_array_type_rejected(self):
        fact=copy.deepcopy(self.facts[0]);fact['definitions'][0]['type']='unsigned char[8]'
        with self.assertRaises(FormatError):dp.shape(fact)

    def test_guessed_array_extent_rejected(self):
        fact=copy.deepcopy(self.facts[0]);fact['definitions'][0]['bounds']=dict(kind='GUESSED_ARRAY',bytes=8)
        with self.assertRaises(FormatError):dp.shape(fact)

    def test_guessed_extra_scalar_extent_rejected(self):
        fact=copy.deepcopy(self.facts[0]);fact['original']['size']=10
        with self.assertRaises(FormatError):dp.shape(fact)

    def test_padding_filler_rejected(self):
        fact=copy.deepcopy(self.facts[0]);fact['definitions'][1]['offset']=4
        with self.assertRaises(FormatError):dp.shape(fact)

    def test_only_typed_value_not_arbitrary_byte_payload(self):
        fact=copy.deepcopy(self.facts[0]);fact['definitions'][0]['initializer']=99
        with self.assertRaises(FormatError):self.compare(fact)

    def test_value_range_and_bool_rejected(self):
        for value in [65536,True]:
            fact=copy.deepcopy(self.facts[0]);fact['definitions'][0]['initializer']=value
            with self.assertRaises(FormatError):dp.shape(fact)

    def test_original_historical_owner_must_stay_unknown(self):
        fact=copy.deepcopy(self.facts[0]);fact['historical_tu']='original_globals.c'
        with self.assertRaises(FormatError):dp.shape(fact)

    def test_original_CODE_cannot_be_provider(self):
        fact=copy.deepcopy(self.facts[0]);fact['original']['hunk']=0
        with self.assertRaises(FormatError):dp.shape(fact)

    def test_object_CODE_and_BSS_rejected(self):
        for off in [10,18]:
            raw=bytearray(self.files['p1608.o']);raw[off:off+4]=(2).to_bytes(4,'big')
            with self.assertRaises(FormatError):self.compare(obj=bytes(raw))

    def test_hidden_COMMON_symbol_rejected(self):
        raw=bytearray(self.files['p1608.o']);start=int.from_bytes(raw[28:30],'big')*4;raw[start]=5
        with self.assertRaises(FormatError):dp.data_object(bytes(raw))

    def test_unknown_AJ_token_rejected(self):
        raw=bytearray(self.files['p1608.o']);raw[36]=0xf6
        with self.assertRaises(FormatError):dp.data_object(bytes(raw))

    def test_partial_object_and_extra_DATA_rejected(self):
        raw=bytearray(self.files['p1608.o']);raw[14:18]=(10).to_bytes(4,'big')
        with self.assertRaises(FormatError):self.compare(obj=bytes(raw))
        with self.assertRaises(FormatError):dp.data_object(self.files['p1608.o'][:-2])

    def test_symbol_order_and_position_rejected(self):
        text=self.files['p1608.sym'].decode().replace('00000002 _G_h01_160A','00000004 _G_h01_160A')
        with self.assertRaises(FormatError):self.compare(map_text=text)

    def test_changed_initialized_scalar_rejected(self):
        raw=bytearray(self.files['p1608.exe']);m=parse(raw);h=m['hunks'][1];raw[h['content_offset']+1]^=1
        with self.assertRaises(FormatError):self.compare(linked=bytes(raw))

    def test_extra_original_relocation_rejected(self):
        m=copy.deepcopy(self.model);m['relocations'].append(dict(source_hunk=1,source_offset=0x1608,width=4,type='HUNK_RELOC32',target_hunk=1,addend_raw=0x1608))
        with self.assertRaises(FormatError):self.compare(model=m)

    def test_stale_consumer_and_missing_binding_rejected(self):
        fact=copy.deepcopy(self.facts[0]);fact['definitions'][0]['evidence']['proof_sha256']='0'*64
        with self.assertRaises(FormatError):dp.typed_evidence(ROOT,fact,self.analysis,self.ledger,self.promotions)
        fact=copy.deepcopy(self.facts[0]);fact['definitions'][0]['evidence']['access_site']+=2
        with self.assertRaises(FormatError):dp.typed_evidence(ROOT,fact,self.analysis,self.ledger,self.promotions)

    def test_A4_only_miner_cannot_hide_absolute_alias(self):
        analysis=copy.deepcopy(self.analysis)
        f=next(f for f in analysis['functions'] if f['id']==self.facts[0]['definitions'][0]['evidence']['function'])
        f['relocations'].append(dict(target_hunk=1,addend_raw=0x1608))
        with self.assertRaises(FormatError):dp.typed_evidence(ROOT,self.facts[0],analysis,self.ledger,self.promotions)

    def test_unaccepted_consumer_rejected(self):
        with self.assertRaises(FormatError):dp.typed_evidence(ROOT,self.facts[0],self.analysis,self.ledger,[])

    def test_wrong_width_and_scalar_declaration_rejected(self):
        fact=copy.deepcopy(self.facts[0]);fact['definitions'][0]['type']='long';fact['definitions'][0]['bounds']['bytes']=4
        with self.assertRaises(FormatError):dp.typed_evidence(ROOT,fact,self.analysis,self.ledger,self.promotions)

    def test_preserve_separate_sections_on_legacy_writes(self):
        ledger=dict(schema_version=1,functions={},attempts={'scratch':1},blockers={},mixed_source_objects={'m':{}},data_providers={'d':{}})
        saved=canonical_state(ledger)
        self.assertEqual(saved['data_providers'],ledger['data_providers']);self.assertEqual(saved['mixed_source_objects'],ledger['mixed_source_objects'])
        self.assertEqual(saved['attempts'],{})

    def test_absent_section_is_backward_compatible(self):
        self.assertEqual(dp.load_data_providers(ROOT,self.blob,self.model,self.analysis,dict(functions={}),[]),[])

    def pointer_fixture(self):
        fact=copy.deepcopy(self.facts[0]);fact.update(id='resident_data_0000',source='src/recovered/data/resident_data_0000.c',original=dict(hunk=1,start=0,size=6),object_sections=dict(CODE=0,DATA=6,BSS=0,COMMON=0))
        fact['definitions']=[dict(symbol='DP_test_target',type='int',offset=0,initializer=7,bounds=dict(kind='SCALAR_ABI',bytes=2)),
                             dict(symbol='DP_test_pointer',type='int *',offset=2,target='DP_test_target',bounds=dict(kind='SCALAR_ABI',bytes=4))]
        b=self.files['relprobe.exe'];return fact,b,parse(b)

    def test_positive_named_internal_RELOC32_control(self):
        fact,b,m=self.pointer_fixture()
        result=dp.compare_data(b,m,fact,self.files['relprobe.o'],b,self.files['relprobe.sym'].decode())
        self.assertEqual(result['verdict'],'EQUAL_CANDIDATE');self.assertEqual(result['relocation_bindings'][0]['symbol'],'_DP_test_target')
        self.assertEqual(result['sections']['DATA'],6)

    def test_quarantine_canonical_input_rejected(self):
        with self.assertRaises(FormatError):dp.document(ROOT,'to_delete/provider.json')

    def test_wrong_or_unnamed_pointer_target_rejected(self):
        fact,b,m=self.pointer_fixture();fact['definitions'][1]['target']='wrong_target'
        with self.assertRaises(FormatError):dp.shape(fact)
        fact,b,m=self.pointer_fixture();m['relocations'][0]['addend_raw']=2
        with self.assertRaises(FormatError):dp.compare_data(b,m,fact,self.files['relprobe.o'],b,self.files['relprobe.sym'].decode())

    def test_missing_pointer_relocation_rejected(self):
        fact,b,m=self.pointer_fixture();m['relocations']=[]
        with self.assertRaises(FormatError):dp.compare_data(b,m,fact,self.files['relprobe.o'],b,self.files['relprobe.sym'].decode())

    def test_unsupported_nonzero_AJ_pointer_addend_rejected(self):
        raw=bytearray(self.files['relprobe.o']);p=raw.index(b'\xfd\x70\0');raw[p+2]=1
        with self.assertRaises(FormatError):dp.data_object(bytes(raw))

    def test_zero_fill_credit_never_granted(self):
        self.assertEqual(self.compare()['zero_fill_credit'],0)

    def test_accounting_credit_and_overlap_rejection(self):
        from hybrid_image import account
        rows=[self.compare(f) for f in self.facts];contributions=dp.contributions(rows)
        _,result=account(self.blob,self.model,contributions)
        self.assertEqual(result['totals']['RECOVERED_DATA'],16)
        with self.assertRaises(FormatError):account(self.blob,self.model,contributions+[dict(contributions[0],id='overlap')])

    def test_all_bounded_arrays_complete_objects(self):
        for fact in self.batch:
            result=self.compare(fact)
            self.assertEqual(result['verdict'],'EQUAL_CANDIDATE')
            dp.typed_evidence(ROOT,fact,self.analysis,self.ledger,self.promotions)
        from hybrid_image import account
        _,report=account(self.blob,self.model,dp.contributions([self.compare(f) for f in self.batch]))
        self.assertEqual(report['totals']['RECOVERED_DATA'],320)

    def test_meaningful_byte_lookup_requires_its_exact_bit_domain(self):
        fact=copy.deepcopy(next(f for f in self.batch if f['id']=='resident_data_1F14'))
        rows=dp.typed_evidence(ROOT,fact,self.analysis,self.ledger,self.promotions)
        self.assertEqual(rows[0]['index_domain'],list(range(32)))
        fact['definitions'][0]['bounds']['kind']='MASKED_INDEX'
        with self.assertRaises(FormatError):dp.typed_evidence(ROOT,fact,self.analysis,self.ledger,self.promotions)

    def test_guessed_array_count_rejected_even_with_complete_values(self):
        fact=copy.deepcopy(next(f for f in self.batch if f['id']=='resident_data_1322'))
        d=fact['definitions'][0];d['count']=63;d['initializer']=d['initializer'][:-1];d['bounds']['bytes']=126
        d['evidence']['declaration']='extern int G_h01_1322[63];'
        fact['definitions'][1]['offset']=126;fact['original']['size']=254;fact['object_sections']['DATA']=254
        with self.assertRaises(FormatError):dp.typed_evidence(ROOT,fact,self.analysis,self.ledger,self.promotions)

    def test_changed_decoded_index_scale_rejected(self):
        fact=next(f for f in self.batch if f['id']=='resident_data_1322');analysis=copy.deepcopy(self.analysis)
        f=next(f for f in analysis['functions'] if f['id']=='ov11_F_727A')
        next(i for i in f['instructions'] if i['offset']==29324)['operands']='#$2, d1'
        with self.assertRaises(FormatError):dp.typed_evidence(ROOT,fact,analysis,self.ledger,self.promotions)

    def test_missing_second_loop_read_rejected(self):
        fact=copy.deepcopy(next(f for f in self.batch if f['id']=='resident_data_0A92'))
        fact['definitions'][0]['evidence']['additional_sites']=[]
        with self.assertRaises(FormatError):dp.typed_evidence(ROOT,fact,self.analysis,self.ledger,self.promotions)

    def test_arbitrary_pointer_table_and_struct_rejected(self):
        for ty in ['int *[44]','struct ByteCarrier']:
            f=copy.deepcopy(self.facts[0]);f['definitions'][0]['type']=ty
            with self.assertRaises(FormatError):dp.shape(f)

    def test_curated_batch_cache_key_binds_members(self):
        recipe=copy.deepcopy(self.recipe);recipe['members'].pop()
        self.assertNotEqual(dp.batch_key(recipe),self.recipe['cache_key'])
        with self.assertRaisesRegex(FormatError,'cache key changed'):self.producer_check(recipe=recipe)

    def test_job_path_quarantine_escape_and_prefix_rejected(self):
        for job in ['build/worker-jobs/tu-layout-good/../bad','to_delete/tu-layout-old','build/worker-jobs/other']:
            r=copy.deepcopy(self.recipe);r['job']=job
            with self.assertRaises(FormatError):dp.producer_paths(ROOT,r)


    def test_new_absolute_interior_consumer_requires_evidence(self):
        fact=next(f for f in self.batch if f['id']=='resident_data_1322');analysis=copy.deepcopy(self.analysis)
        f=next(f for f in analysis['functions'] if f['id']=='ov11_F_727A');f['relocations'].append(dict(target_hunk=1,addend_raw=0x1324,source_offset=29328,width=4))
        with self.assertRaisesRegex(FormatError,'additional absolute aggregate consumer'):dp.typed_evidence(ROOT,fact,analysis,self.ledger,self.promotions)

    def test_snapshot_identity_includes_ignored_job_artifacts(self):
        temporary,root=self.retained_copy()
        try:
            fixture=root/'identity-root';fixture.mkdir()
            target=fixture/'recovery/ledger.json';target.parent.mkdir(parents=True);target.write_text(json.dumps(dict(functions={})))
            for name in ['evidence/data-providers/batch.json','evidence/data-providers/producer.json']+[m['fact'] for m in self.recipe['members']]:
                target=fixture/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((HERE/name).read_bytes())
            job=fixture/self.recipe['job'];job.mkdir(parents=True)
            for name in ['request.json','result.json','worker.uae','kick.rom','sys/s/startup-sequence']+['sys/work/'+n for n in self.recipe['artifacts']]:
                target=job/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((root/name).read_bytes())
            target=fixture/'toolchain/candidate-lock.json';target.parent.mkdir(parents=True);target.write_bytes((ROOT/'toolchain/candidate-lock.json').read_bytes())
            before=dp.input_identity(fixture)
            target=job/'sys/work/p1322.o';target.write_bytes(target.read_bytes()+b'change')
            after=dp.input_identity(fixture)
            self.assertNotEqual(before,after)
            self.assertNotEqual(before[str(target.resolve())],after[str(target.resolve())])
        finally:temporary.cleanup()



if __name__=='__main__':unittest.main()
