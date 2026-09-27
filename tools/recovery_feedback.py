"""Bounded advisory feedback; never part of the exact acceptance gate."""
import json
from pathlib import Path

from analysis_support import ROOT


def advisory_feedback(fid, attempt=None, root=ROOT):
    """Read cached diagnostics and shared evidence without starting a compiler."""
    root = Path(root)
    result = dict(status='DIAGNOSTIC_ONLY', promotion_eligible=False)
    if attempt:
        result['based_on'] = {k: attempt[k] for k in ('source_sha256', 'profile', 'cache_key') if k in attempt}
    if (root / 'evidence/types.json').is_file():
        try:
            from type_evidence import function_evidence
            result['type_evidence'] = function_evidence(fid, root=root)
        except Exception as exc:
            result['type_evidence'] = dict(status='UNAVAILABLE', reason=type(exc).__name__+': '+str(exc)[:300])
    if attempt and attempt.get('cache_key'):
        try:
            from diag import diagnose, compact_summary
            result['compiler_diagnostic'] = compact_summary(diagnose(fid, attempt['cache_key']))
        except Exception as exc:
            # An advisory parser error must not disable the existing proposer
            # or exact verifier. Direct diagnostic tests still expose bugs.
            result['compiler_diagnostic'] = dict(status='UNAVAILABLE', reason=type(exc).__name__+': '+str(exc)[:300])
    # Optional guidance must not crowd complete instructions/identity evidence
    # out of the proposer's hard input budget. Keep omission explicit.
    for key in ('type_evidence', 'compiler_diagnostic'):
        if key in result and len(json.dumps(result[key]).encode()) > 6000:
            result[key] = dict(status='OMITTED_FOR_BUDGET',
                               command=('python tools/type_evidence.py --function ' + fid
                                        if key == 'type_evidence' else
                                        'python tools/diag.py ' + fid + ' --cache-key ' + attempt['cache_key']))
    return result


def review_frontier(node=None, ids=None, limit=256, max_packages=8,
                    max_unknown_calls=1, max_data_references=40):
    """Execute bounded read-only analysis when the ordinary proposal queue ends."""
    from recovery_plan import plan
    from recovery_state import recovery
    result = plan(node=node, ids=ids, limit=limit, max_packages=max_packages,
                  max_unknown_calls=max_unknown_calls, max_data_references=max_data_references)
    state = recovery()
    candidates = []
    for package in result['packages']:
        for fid in package['dispatch']['ids']:
            if fid not in candidates and state.get('attempts', {}).get(fid):
                candidates.append(fid)
    result['executed_diagnostics'] = [
        dict(id=fid, feedback=advisory_feedback(fid, state['attempts'][fid][-1]))
        for fid in candidates[:4]
    ]
    result['execution'] = dict(mode='CACHED_DIAGNOSTIC_REVIEW', max_functions=4,
                               compiler_trials=0, model_proposals=0, promotions=0,
                               note='Remaining package actions require a new evidence or source hypothesis; none was silently retried.')
    return result
