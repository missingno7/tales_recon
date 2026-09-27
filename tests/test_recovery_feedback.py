"""The next proposal must receive retained source, not a second receipt list."""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import recovery_state
from common import sha256
from local_fact_pack import representation
import recovery_feedback
import grinder


class RecoveryFeedbackTests(unittest.TestCase):
    def test_advisory_failure_does_not_disable_existing_recovery(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch('diag.diagnose', side_effect=RuntimeError('diagnostic fixture failure')):
            result = recovery_feedback.advisory_feedback('fixture', dict(cache_key='fixture'), root=Path(directory))
        self.assertEqual(result['compiler_diagnostic']['status'], 'UNAVAILABLE')
        self.assertIn('RuntimeError', result['compiler_diagnostic']['reason'])
        self.assertFalse(result['promotion_eligible'])

    def test_frontier_analysis_is_bounded_and_deduplicated(self):
        ids = ['f%d' % i for i in range(7)]
        planned = dict(packages=[dict(dispatch=dict(ids=ids)), dict(dispatch=dict(ids=ids))])
        state = dict(attempts={fid: [dict(cache_key=fid)] for fid in ids})
        with patch('recovery_plan.plan', return_value=planned) as planner, \
                patch.object(recovery_state, 'recovery', return_value=state), \
                patch.object(recovery_feedback, 'advisory_feedback', return_value={}) as feedback:
            result = recovery_feedback.review_frontier(node='ov09', ids=ids, limit=300)
        self.assertEqual([x['id'] for x in result['executed_diagnostics']], ids[:4])
        self.assertEqual(feedback.call_count, 4)
        self.assertEqual(planner.call_args.kwargs['ids'], ids)
        self.assertEqual(result['execution']['compiler_trials'], 0)
        self.assertEqual(result['execution']['promotions'], 0)

    def test_exhaustion_runs_review_with_original_scope_without_proposals(self):
        args = SimpleNamespace(proposer=['must-not-run'], ids=['ov14_F_0412'],
                               node='ov14', max_rounds=1, max_bytes=256, batch_size=8,
                               max_unknown_calls=2, max_data_references=30)
        review = dict(packages=[dict(kind='PROOF_BLOCKER_REVIEW')], executed_diagnostics=[])
        with patch.object(grinder, 'recovery', return_value=dict(blockers={}, attempts={})), \
                patch.object(grinder, 'ranked', return_value=[]), \
                patch.object(grinder, 'checkpoint'), patch.object(grinder, 'save_rank'), \
                patch.object(grinder, 'check_many') as compile_call, \
                patch.object(recovery_feedback, 'review_frontier', return_value=review) as reviewed:
            result = grinder.run(args)
        reviewed.assert_called_once_with(node='ov14', ids=['ov14_F_0412'], limit=256,
                                         max_unknown_calls=2, max_data_references=30)
        compile_call.assert_not_called()
        self.assertEqual(result['status'], 'RECOVERY_REVIEW_REQUIRED')
        self.assertEqual(result['recovery_review'], review)
        self.assertEqual(result['proposals'], [])
        self.assertEqual(result['promoted'], [])

    def test_advice_is_optional_during_local_context_reduction(self):
        package = dict(id='test', extent={}, instructions=[], cfg=[],
                       advisory_feedback=dict(status='DIAGNOSTIC_ONLY'))
        self.assertIn('advisory_feedback', representation(package, stage=0)[0])
        self.assertNotIn('advisory_feedback', representation(package, stage=4)[0])

    def test_local_prompt_does_not_mix_another_candidates_diagnostic(self):
        package = dict(id='test', extent={}, instructions=[], cfg=[],
                       previous_attempts=[dict(compiler='aztec36', source_sha256='current')],
                       advisory_feedback=dict(based_on=dict(profile='aztec50', source_sha256='other'),
                                              compiler_diagnostic=dict(status='DIAGNOSTIC_ONLY'),
                                              type_evidence=dict(policy='ACCESS_FACT_ONLY')))
        base, _, _ = representation(package)
        self.assertNotIn('compiler_diagnostic', base['advisory_feedback'])
        self.assertIn('type_evidence', base['advisory_feedback'])
        self.assertIn('compiler_diagnostic', package['advisory_feedback'])

    def test_prior_candidate_text_is_available_by_hash(self):
        source = 'int recovered() { return 3; }\n'
        digest = sha256(source.encode())
        fid = 'ov14_F_0000'
        function = dict(id=fid, node='ov14', hunk=14, start=0, end=4,
                        size=4, sha256='fixture', extent_status='CLOSED_CFG',
                        confidence='HIGH', instructions=[], referenced_data=[],
                        relocations=[], direct_callees=[], entry_evidence=[], cfg=[],
                        indirect_control_flow=[], referenced_strings=[], stack_frames=[],
                        likely_argument_accesses=[])
        receipt = dict(source_sha256=digest, cache_key='fixture', verdict='DIFFER',
                       compiler='aztec36', reason='CODE_OR_REFERENCE_DIFFERS')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / 'recovery/candidates' / fid / (digest + '.c')
            candidate.parent.mkdir(parents=True)
            candidate.write_text(source)
            attempt = root / 'attempt.json'
            attempt.write_text(json.dumps(receipt))
            ledger = dict(functions=[function], a4=dict(bias=32766))
            recovery = dict(functions={}, blockers={}, attempts={fid: [dict(receipt='attempt.json')]})
            with patch.object(recovery_state, 'ROOT', root), \
                    patch.object(recovery_state, 'evidence', return_value=ledger), \
                    patch.object(recovery_state, 'recovery', return_value=recovery), \
                    patch.object(recovery_state, 'runtime_dependencies', return_value={}):
                result = recovery_state.facts(fid)
        self.assertEqual(result['previous_sources'], {digest: dict(source=source, truncated=False)})
        self.assertEqual(result['previous_attempts'][0]['verdict'], 'DIFFER')
        self.assertNotIn('source', result['previous_attempts'][0])
        _, current, latest = representation(result)
        self.assertEqual(current, source)
        self.assertEqual(latest['source_sha256'], digest)


if __name__ == '__main__':
    unittest.main()
