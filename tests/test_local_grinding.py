import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch,MagicMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError,write_json,sha256
from local_fact_pack import fit,messages_for,BudgetError
from local_http import LocalHTTP
import local_model_proposer as proposer
from grinder import eligible,canonical_promotion,blocker_next_action,compact_blocker_facts
from grinder_report import summarize,blocker_class,blocker_impact
from fingerprint import CORPUS
import recovery_state
from recovery_state import call_excerpt,canonical_call_examples


def facts():
    return dict(id='ov14_F_0000',extent=dict(start=0,end=2,size=2),
        instructions=[dict(offset=0,raw='4e75',mnemonic='rts',operands='')],cfg=[],
        abi=dict(a4_bias=32766),relocations=[dict(target_hunk=1,addend_raw=20,target_name='G_h01_0014')],
        data=[dict(hunk=1,offset=20,name='G_h01_0014')])


class FactBudgetTests(unittest.TestCase):
    def count(self,messages):return len(json.dumps(messages))
    def test_drops_examples_before_required_facts(self):
        f=facts();f['compiler_examples']=[dict(profile='aztec36',name='unrelated',source='x'*10000,assembly='x'*10000)]
        size=self.count(messages_for(f,1));messages,budget=fit(f,self.count,size+512,max_output_tokens=256,reserve=256)
        self.assertEqual(budget['reduction_stage'],1)
        base=json.loads(messages[1]['content'].split('\n',1)[1].split('\n\nTARGET',1)[0])
        self.assertEqual(base['references'],f['relocations']);self.assertEqual(base['cfg'],f['cfg'])
        self.assertIn('0000: 4e75 rts',messages[1]['content'])
    def test_oversize_required_facts_block_without_truncation(self):
        f=facts();f['instructions']*=2000
        with self.assertRaises(BudgetError):fit(f,self.count,4096,1024)
        self.assertEqual(len(f['instructions']),2000)
    def test_latest_candidate_and_mismatch_survive_reduction(self):
        f=facts();latest=dict(compiler='aztec36',source_sha256='hash',verdict='DIFFER',actual_length=4,expected_length=2)
        f['previous_attempts']=[latest];f['previous_sources']={'hash':dict(source='recovered() {return 0;}',truncated=False)}
        messages=messages_for(f,4)
        self.assertIn('recovered()',messages[-2]['content']);self.assertIn('DIFFER',messages[-1]['content'])
        self.assertIn('G_h01_0014',messages[1]['content'])
    def test_truncated_previous_c_is_not_silently_sent(self):
        f=facts();f['previous_attempts']=[dict(compiler='aztec36',source_sha256='x')]
        f['previous_sources']={'x':dict(source='incomplete',truncated=True)}
        with self.assertRaises(BudgetError):messages_for(f)

    def test_blocker_package_keeps_current_evidence_without_source_duplication(self):
        f=facts();f.update(previous_attempts=[dict(source_sha256='x')],previous_sources={'x':dict(source='old',truncated=False)},
                   compiler_examples=[dict(source='example')],recovered_dependencies=[dict(source='dependency')])
        compact=compact_blocker_facts(f)
        self.assertEqual(compact['instructions'],f['instructions'])
        self.assertEqual(compact['previous_attempts'],f['previous_attempts'])
        self.assertNotIn('previous_sources',compact)
        self.assertNotIn('compiler_examples',compact)
        self.assertNotIn('recovered_dependencies',compact)

    def test_canonical_call_excerpt_is_complete_and_bounded(self):
        source='extern int F_h00_8A46();\nvoid x() { F_h00_8A46(a, nested(b,c), d); }'
        self.assertEqual(call_excerpt(source,'F_h00_8A46'),'F_h00_8A46(a, nested(b,c), d);')
        self.assertIsNone(call_excerpt(source,'F_h00_9999'))

    def test_canonical_examples_cover_each_external_callee_before_duplicates(self):
        source='extern int F_h00_8A46(); extern int F_h00_8A47();\nvoid x() { F_h00_8A46(a); F_h00_8A47(b); }'
        package={'functions':{'caller':{'source':'tests/fixture-call-examples.c'}}}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'tests').mkdir()
            (root/'tests/fixture-call-examples.c').write_text(source)
            with patch.object(recovery_state,'ROOT',root):
                examples=canonical_call_examples([
                    {'basis':'A4_RELOCATED_JMP_STUB','hunk':0,'offset':0x8a46},
                    {'basis':'A4_RELOCATED_JMP_STUB','hunk':0,'offset':0x8a47}],package)
        self.assertEqual([example['callee'] for example in examples],['F_h00_8A46','F_h00_8A47'])


class TransportAndQueueTests(unittest.TestCase):
    def test_intermediate_exact_proof_is_not_a_promotion(self):
        self.assertFalse(canonical_promotion([dict(verdict='EQUAL',proof_level='FUNCTION_WITH_DATA_MATCH')]))
        self.assertTrue(canonical_promotion([dict(verdict='EQUAL',proof_level='FUNCTION_CODE_MATCH',promotion=dict(proof='recovery/proofs/x.json'))]))

    def test_only_loopback_endpoints(self):
        for endpoint in ('http://example.com','http://127.0.0.1.evil','http://127.0.0.1@evil','http://0.0.0.0','http://192.168.1.2','https://localhost'):
            with self.assertRaises(FormatError):LocalHTTP(endpoint)
        self.assertEqual(LocalHTTP('http://localhost:9999/v1').host,'127.0.0.1')
        self.assertEqual(LocalHTTP('http://[::1]:9999').port,9999)
    def test_redirect_not_followed(self):
        response=MagicMock(status=302);response.read.return_value=b'redirect'
        with patch('local_http.http.client.HTTPConnection') as cls:
            cls.return_value.getresponse.return_value=response
            with self.assertRaises(FormatError):LocalHTTP().call('/health')
            self.assertEqual(cls.call_count,1)
    def test_frontier_requires_safe_overlay_evidence(self):
        f=dict(extent='CLOSED_CFG',size=64,node='ov14',confidence='HIGH',indirect=0,unknown_calls=0,data_references=1,pending_local_dependencies=[])
        args=SimpleNamespace(max_unknown_calls=1,max_data_references=8)
        self.assertTrue(eligible(f,args,256))
        for change in (dict(node='resident'),dict(indirect=1),dict(size=258),dict(extent='UNCERTAIN'),dict(pending_local_dependencies=['callee']),dict(unknown_calls=2),dict(pc_relative_data=1),dict(same_node_unit_ready=False)):
            self.assertFalse(eligible(dict(f,**change),args,256))
        self.assertFalse(eligible(dict(f,data_references=9),args,256))


class LocalCacheTests(unittest.TestCase):
    def test_completed_response_reused_and_raw_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'tools').mkdir()
            for name in ('local_model_proposer.py','local_fact_pack.py','local_http.py'):(root/'tools'/name).write_text('test implementation')
            client=MagicMock();client.count.return_value=100
            client.call.return_value=dict(choices=[dict(finish_reason='stop',message=dict(content=json.dumps(dict(source='recovered() { return 0; }'))))],usage=dict(prompt_tokens=100,completion_tokens=20))
            state=dict(model='test',model_sha256='a'*64,runner_sha256='b'*64,context_size=4096,quantization='Q4_K_M',pid=1)
            with patch.object(proposer,'ROOT',root),patch.object(proposer,'service',return_value=(client,state,'test')),patch.object(proposer,'Sampler') as sample:
                sample.return_value.__enter__.return_value.summary.return_value={}
                first=proposer.propose(facts());second=proposer.propose(facts())
                self.assertEqual(first['source'],second['source']);self.assertTrue(second['proposer_cache_hit'])
                self.assertEqual(client.call.call_count,1)
                next((root/'build/local-model-proposals').glob('*/response.json')).write_text('{}')
                with self.assertRaises(FormatError):proposer.propose(facts())
                self.assertEqual(client.call.call_count,1)
    def test_empty_completed_response_is_cached_as_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'tools').mkdir()
            for name in ('local_model_proposer.py','local_fact_pack.py','local_http.py'):(root/'tools'/name).write_text('test')
            client=MagicMock();client.count.return_value=100
            client.call.return_value=dict(choices=[dict(finish_reason='stop',message=dict(content='{"source":""}'))])
            state=dict(model='test',model_sha256='a'*64,runner_sha256='b'*64,context_size=4096)
            with patch.object(proposer,'ROOT',root),patch.object(proposer,'service',return_value=(client,state,'test')),patch.object(proposer,'Sampler') as sample:
                sample.return_value.__enter__.return_value.summary.return_value={}
                for _ in range(2):
                    with self.assertRaises(proposer.ProposalRejected):proposer.propose(facts())
                self.assertEqual(client.call.call_count,1)


class ReportTests(unittest.TestCase):
    def test_fingerprint_retains_the_byte_return_abi_matrix(self):
        self.assertTrue({'char_return','unsigned_char_return','int_from_char_return',
                         'unsigned_int_from_char_return','long_from_char_return'} <= set(CORPUS))

    def test_fingerprint_retains_the_byte_zero_extension_probe(self):
        self.assertIn('unsigned_char_assignment',CORPUS)

    def test_byte_return_blocker_does_not_recommend_more_candidate_retries(self):
        self.assertIn('do not retry ordinary candidate C',
                      blocker_next_action('BYTE_RETURN_ABI_MISMATCH: return convention differs'))
        self.assertIn('do not retry ordinary candidate C',
                      blocker_next_action('CHAR_RETURN_EXTENSION: return convention differs'))

    def test_byte_zero_extension_blocker_does_not_recommend_more_candidate_retries(self):
        self.assertIn('Do not retry ordinary candidate C',
                      blocker_next_action('BYTE_ZERO_EXTENSION_CODEGEN_MISMATCH: measured compiler form differs'))

    def test_cyclic_call_blocker_uses_layout_proof_not_isolated_retries(self):
        self.assertIn('normal source-layout proof',
                      blocker_next_action('CYCLIC_INTER_OBJECT_PC_CALL: reciprocal PC-relative calls'))

    def test_local_match_requires_both_pinned_canonical_and_proposer_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            proposal=root/'recovery/proposals/local.json'
            write_json(proposal,dict(identity=dict(transport='LOCAL_LOOPBACK_ONLY')))
            provenance=dict(receipt='recovery/proposals/local.json',receipt_sha256=sha256(proposal.read_bytes()))
            proof=root/'recovery/proofs/local.json'
            write_json(proof,dict(state='FUNCTION_CODE_MATCH',comparison=dict(proposer=provenance),evidence_extent=dict(size=20)))
            run=dict(run_id='test',status='DONE',elapsed_seconds=10,
                proposals=[dict(id='ov14_F_0000',local_model_metrics=dict(model_identity={},model_call=True))],
                trials=[dict(id='ov14_F_0000',verdict='EQUAL',proposer=provenance,
                    promotion=dict(proof='recovery/proofs/local.json',proof_sha256=sha256(proof.read_bytes())))])
            self.assertEqual(summarize(run,root)['verified_game_bytes'],20)
            proposal.write_text('{}')
            self.assertEqual(summarize(run,root)['verified_game_bytes'],0)
    def test_fixture_and_hosted_promotions_are_not_local_successes(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=summarize(dict(run_id='test',status='DONE',promoted=['fixture'],elapsed_seconds=10,proposals=[],trials=[]),Path(tmp))
            self.assertEqual(r['functions_promoted'],0);self.assertEqual(r['verified_game_bytes'],0)
            self.assertIsNone(r['verified_bytes_per_gpu_hour'])
    def test_blockers_group_by_mechanism(self):
        self.assertEqual(blocker_class(dict(data_contributions=dict(candidate_bss=4))),'CANDIDATE_OWNED_BSS')
        self.assertEqual(blocker_class(dict(unit_blocker='unrecovered callee')),'UNRESOLVED_INTER_OBJECT_CALL')
        self.assertEqual(blocker_class(dict(relocation_issues=[dict(kind='PC_RELATIVE_DATA_OWNERSHIP_UNPROVEN')])),'PC_RELATIVE_OWNED_DATA')
        self.assertEqual(blocker_class(dict(relocation_issues=[dict(kind='HUNK_RELOCATION')]),
                                       'PERSISTENT_CODEGEN_MISMATCH: established profile mismatch'),
                         'PERSISTENT_CODEGEN_MISMATCH')
        self.assertEqual(blocker_class({},'CYCLIC_INTER_OBJECT_PC_CALL: reciprocal PC-relative calls'),
                         'CYCLIC_INTER_OBJECT_PC_CALL')
        self.assertEqual(blocker_class({},'UNSUPPORTED_REGISTER_CALL_ABI: D0/D1 library wrapper'),
                         'UNSUPPORTED_REGISTER_CALL_ABI')
        self.assertEqual(blocker_class({},'BYTE_RETURN_ABI_MISMATCH: signed and unsigned byte returns differ'),
                         'BYTE_RETURN_ABI_MISMATCH')
        self.assertEqual(blocker_class({},'BYTE_ZERO_EXTENSION_CODEGEN_MISMATCH: measured compiler form differs'),
                         'BYTE_ZERO_EXTENSION_CODEGEN_MISMATCH')

    def test_blocker_impact_follows_callers_without_claiming_recovery(self):
        functions=[dict(id='leaf',direct_callees=[]),dict(id='middle',direct_callees=[dict(id='leaf')]),
                   dict(id='caller',direct_callees=[dict(id='middle')]),dict(id='done',direct_callees=[dict(id='leaf')])]
        impact=blocker_impact(functions,{'leaf':{}},{'done':dict(state='FUNCTION_CODE_MATCH')})
        self.assertEqual(impact['leaf']['immediate_callers'],['done','middle'])
        self.assertEqual(impact['leaf']['affected_functions'],['caller','middle'])


if __name__=='__main__':unittest.main()
