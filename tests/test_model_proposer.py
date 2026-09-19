import json
from pathlib import Path
import sys
import unittest
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError
from model_proposer import parse_events
import grinder
import check_function


class ModelProposerTests(unittest.TestCase):
    def events(self,extra=None,source='recovered() { return 1; }'):
        rows=[{'type':'thread.started','thread_id':'synthetic'},
              {'type':'item.completed','item':{'type':'agent_message','text':json.dumps({'source':source})}},
              {'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':5}}]
        if extra:rows.insert(1,extra)
        return '\n'.join(json.dumps(r) for r in rows)

    def test_structured_source_and_usage(self):
        source,usage=parse_events(self.events())
        self.assertIn('return 1',source);self.assertEqual(usage['input_tokens'],10)

    def test_tool_attempt_rejects_otherwise_valid_source(self):
        extra={'type':'item.started','item':{'type':'command_execution','command':'echo forbidden'}}
        with self.assertRaises(FormatError):parse_events(self.events(extra))

    def test_failed_turn_never_returns_candidate(self):
        with self.assertRaises(FormatError):parse_events(self.events({'type':'turn.failed'}))

    def test_truncated_stream_never_returns_candidate(self):
        with self.assertRaises(FormatError):parse_events('\n'.join(self.events().splitlines()[:-1]))

    def test_bounded_ascii_source_required(self):
        for source in ('x'*16385,'/* \u2603 */ recovered(){}'):
            with self.assertRaises(FormatError):parse_events(self.events(source=source))


class GrinderContinuationTests(unittest.TestCase):
    def test_eligibility_excludes_unowned_same_node_dependencies(self):
        args=SimpleNamespace(max_unknown_calls=1,max_data_references=8)
        candidate=dict(extent='CLOSED_CFG',size=36,node='ov11',confidence='HIGH',indirect=0,
                       unknown_calls=0,data_references=1,pending_local_dependencies=[],same_node_unit_ready=True)
        self.assertTrue(grinder.eligible(candidate,args,256))
        candidate['same_node_unit_ready']=False
        self.assertFalse(grinder.eligible(candidate,args,256))

    def test_eligibility_excludes_pc_relative_data_without_owned_data_proof(self):
        args=SimpleNamespace(max_unknown_calls=1,max_data_references=8)
        candidate=dict(extent='CLOSED_CFG',size=36,node='ov11',confidence='HIGH',indirect=0,
                       unknown_calls=0,data_references=1,pc_relative_data=1,pending_local_dependencies=[],same_node_unit_ready=True)
        self.assertFalse(grinder.eligible(candidate,args,256))
        self.assertEqual(grinder.deferral_reason(candidate,args,256),'PC_RELATIVE_DATA_OWNERSHIP')

    def test_deferral_reports_the_dependency_gap(self):
        args=SimpleNamespace(max_unknown_calls=1,max_data_references=8)
        candidate=dict(extent='CLOSED_CFG',size=36,node='ov11',confidence='HIGH',indirect=0,
                       unknown_calls=0,data_references=1,pending_local_dependencies=[],same_node_unit_ready=False)
        self.assertEqual(grinder.deferral_reason(candidate,args,256),'NONCONTIGUOUS_LOCAL_UNIT')
        candidate['same_node_unit_ready']=True;candidate['pending_local_dependencies']=['ov11_F_4610']
        self.assertFalse(grinder.eligible(candidate,args,256))

    def test_first_cached_mismatch_gets_revision_opportunity(self):
        reports=[dict(source_sha256='candidate',cache_hit=True)]
        after=[dict(source_sha256='candidate')]
        self.assertFalse(grinder.exhausted(reports,[],after,5))
        self.assertTrue(grinder.exhausted(reports,after,after,5))

    def test_service_failure_does_not_poison_function_queue(self):
        args=SimpleNamespace(proposer=['synthetic'],max_rounds=2,node=None,ids=None,max_bytes=512,batch_size=2,proposer_timeout=1)
        r=dict(functions={},attempts={},blockers={})
        queue=[dict(id='ov14_F_TEST',extent='CLOSED_CFG',size=10)]
        response=SimpleNamespace(returncode=2,stderr='Service unavailable',stdout='')
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(grinder,'ROOT',Path(tmp)),patch.object(grinder,'recovery',return_value=r),patch.object(grinder,'ranked',return_value=queue),patch.object(grinder,'facts',return_value={}),patch.object(grinder.subprocess,'run',return_value=response),patch.object(grinder,'block') as blocked,patch.object(grinder,'check_many') as checked,patch.object(grinder,'save_rank'):
                result=grinder.run(args)
            self.assertEqual(result['status'],'SERVICE_BLOCKED');blocked.assert_not_called();checked.assert_not_called()
            self.assertFalse(result['blocked'])

    def test_compiler_service_failure_checkpoints_without_poisoning_queue(self):
        args=SimpleNamespace(proposer=['synthetic'],max_rounds=2,node=None,ids=None,max_bytes=512,batch_size=1,proposer_timeout=1,profile=['aztec36'])
        state=dict(functions={},attempts={},blockers={})
        queue=[dict(id='ov14_F_TEST',extent='CLOSED_CFG',size=10)]
        response=SimpleNamespace(returncode=0,stderr='',stdout=json.dumps(dict(source='recovered() { return 1; }')))
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(grinder,'ROOT',Path(tmp)),patch.object(grinder,'recovery',return_value=state),patch.object(grinder,'ranked',return_value=queue),patch.object(grinder,'facts',return_value={}),patch.object(grinder.subprocess,'run',return_value=response),patch.object(grinder,'block') as blocked,patch.object(grinder,'check_many',side_effect=FormatError('worker timeout')),patch.object(grinder,'save_rank'):
                result=grinder.run(args)
            self.assertEqual(result['status'],'SERVICE_BLOCKED')
            self.assertEqual(result['pending_candidates'][0]['id'],'ov14_F_TEST')
            self.assertTrue(Path(result['pending_candidates'][0]['source']).is_file())
            blocked.assert_not_called()

    def test_bad_harness_trial_does_not_cancel_valid_trial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);bad=root/'bad.c';good=root/'good.c';ledger=root/'ledger.json'
            bad.write_text('extern unsigned G_h01_1234; recovered() {return G_h01_1234;}')
            good.write_text('recovered() {return 0;}')
            initial=dict(functions={},attempts={},blockers={})
            def state():return json.loads(ledger.read_text()) if ledger.exists() else initial
            fs=[({'id':'bad','size':8,'direct_callees':[]},{'a4':{'bias':0}}),({'id':'good','size':8,'direct_callees':[]},{'a4':{'bias':0}})]
            compiled=dict(status='COMPILE_ERROR',identity=dict(profile='aztec36',flags=[]),cache_key='synthetic',cache_hit=False,guest_returncodes=[1],directory=str(root/'logs'))
            with patch.object(check_function,'ROOT',root),patch.object(check_function,'LEDGER',ledger),patch.object(check_function,'recovery',state),patch.object(check_function,'validated_function',side_effect=fs),patch.object(check_function,'compile_many',return_value=[compiled]) as compile_batch,patch.object(check_function,'save_rank'):
                reports=check_function.check_many([dict(id='bad',source=str(bad),profiles=['aztec36']),dict(id='good',source=str(good),profiles=['aztec36'])])
            self.assertEqual(len(compile_batch.call_args.args[0]),1)
            self.assertEqual([r['reason'] for r in reports],['SOURCE_REJECTED','COMPILE_ERROR'])
            self.assertEqual(len(state()['attempts']),2);self.assertFalse(state()['functions'])
