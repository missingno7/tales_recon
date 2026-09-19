"""Measured local grinding outcomes; only canonical promotions count as recovery."""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
from common import sha256,write_json

ROOT=Path(__file__).resolve().parents[1]


def blocker_class(report,reason=''):
    text=reason+' '+json.dumps(report)
    data=report.get('data_contributions',{})
    if 'CONTEXT_BUDGET' in text:return 'CONTEXT_BUDGET'
    if 'MODEL_RESPONSE' in text:return 'MODEL_RESPONSE'
    # A supervisor's explicit confirmed mechanism takes precedence over raw
    # byte-level symptoms retained in the final comparison receipt.
    if 'UNSUPPORTED_REGISTER_CALL_ABI' in reason:return 'UNSUPPORTED_REGISTER_CALL_ABI'
    if 'CYCLIC_INTER_OBJECT_PC_CALL' in reason:return 'CYCLIC_INTER_OBJECT_PC_CALL'
    if 'PERSISTENT_CODEGEN_MISMATCH' in reason:return 'PERSISTENT_CODEGEN_MISMATCH'
    if data.get('candidate_bss',0):return 'CANDIDATE_OWNED_BSS'
    if data.get('candidate_data',0):return 'CANDIDATE_OWNED_DATA'
    if 'PC_RELATIVE_DATA' in text:return 'PC_RELATIVE_OWNED_DATA'
    if report.get('unit_blocker') or 'DIRECT_CALL_BINDING_UNPROVEN' in text:return 'UNRESOLVED_INTER_OBJECT_CALL'
    if 'A4_REGISTER' in text or 'A4_CLOBBER' in text:return 'A4_MANIPULATION'
    if 'JUMP_TABLE' in text or 'INDEXED_JUMP' in text:return 'JUMP_TABLE'
    if 'undefined symbol' in text or 'extern' in text or 'declaration' in text:return 'UNSUPPORTED_DECLARATION'
    if report.get('reason')=='SOURCE_REJECTED':return 'CANDIDATE_SOURCE_CONTRACT'
    if 'A4_IDENTITY' in text or 'HUNK_RELOCATION' in text:return 'REFERENCE_IDENTITY'
    if 'DATA_OR_UNDECODED_CONTRIBUTION' in text:return 'UNACCOUNTED_CONTRIBUTION'
    return 'PERSISTENT_CODEGEN_MISMATCH'


def summarize(run,root=ROOT):
    proposals=[p for p in run.get('proposals',[]) if 'local_model_metrics' in p]
    local={p['id'] for p in proposals};fresh=[p['local_model_metrics'] for p in proposals if p['local_model_metrics'].get('model_call')]
    trials=run.get('trials',[]);matches={}
    for trial in trials:
        promotion=trial.get('promotion');proposer=trial.get('proposer')
        if trial['id'] not in local or not promotion or not proposer or trial.get('verdict')!='EQUAL':continue
        path=root/promotion['proof']
        if not path.is_file() or sha256(path.read_bytes())!=promotion['proof_sha256']:continue
        proof=json.loads(path.read_text())
        if proof['comparison'].get('proposer')!=proposer or proof['state']!='FUNCTION_CODE_MATCH':continue
        proposal_path=root/proposer['receipt']
        if not proposal_path.is_file() or sha256(proposal_path.read_bytes())!=proposer['receipt_sha256']:continue
        identity=json.loads(proposal_path.read_text())['identity']
        if identity.get('transport')!='LOCAL_LOOPBACK_ONLY':continue
        matches[trial['id']]=proof['evidence_extent']['size']
    attempts=Counter(t['id'] for t in trials if t['id'] in local)
    compiler_runs=run.get('oracle_runs',[]);jobs=sum(r['worker_invocations'] for r in compiler_runs)
    compiler_seconds=sum(r['elapsed_seconds'] for r in compiler_runs)
    model_seconds=sum(p.get('inference_seconds',0) for p in fresh)
    usage=dict(prompt_tokens=sum(p.get('usage',{}).get('prompt_tokens',0) for p in fresh),
               generated_tokens=sum(p.get('usage',{}).get('completion_tokens',0) for p in fresh),
               cached_prompt_tokens=sum(p.get('usage',{}).get('prompt_tokens_details',{}).get('cached_tokens',0) for p in fresh))
    prediction_seconds=sum(p.get('timings',{}).get('predicted_ms',0)/1000 for p in fresh)
    observations=[p['gpu'] for p in fresh if p.get('gpu')]
    identities={}
    for p in proposals:
        i=p['local_model_metrics']['model_identity']
        entry={k:i.get(k) for k in ('model','quantization','model_sha256','runner_sha256','context_size','kv_cpu','generation')}
        identities[json.dumps(entry,sort_keys=True)]=entry
    blocked=defaultdict(list)
    ledger_path=root/'recovery/ledger.json'
    ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {'blockers':{}}
    for fid,item in ledger['blockers'].items():
        last={}
        if item.get('attempts'):
            p=root/item['attempts'][-1]['receipt']
            if p.exists():last=json.loads(p.read_text())
        blocked[blocker_class(last,item['reason'])].append(fid)
    wall=run.get('elapsed_seconds',0);gpu_hours=wall/3600 if proposals else None
    n=len(matches);calls=len(fresh);compiled_trials=[t for t in trials if t.get('reason')!='SOURCE_REJECTED']
    guidance=['Keep one GPU generation at a time; no concurrency increase is automatic.']
    if len(local)>=10 and n/len(local)>=0.3:guidance.append('Measured match rate supports trying the next extent tier, within the configured ceiling.')
    if compiler_seconds>model_seconds*2 and jobs:guidance.append('Historical compilation dominates: increase proposal batch size before adding GPU concurrency.')
    elif model_seconds>compiler_seconds*2 and calls:guidance.append('Model inference dominates; retain single-request stability and prompt-prefix caching before testing parallelism.')
    shared=[k for k,v in blocked.items() if len(v)>=3]
    if shared:guidance.append('Supervisor should address shared mechanisms once: '+', '.join(sorted(shared)))
    return dict(schema_version=1,run_id=run['run_id'],status=run['status'],model_identities=list(identities.values()),
        functions_attempted=len(local),functions_promoted=n,promoted_functions=matches,verified_game_bytes=sum(matches.values()),
        function_code_match_rate=n/len(local) if local else None,attempts_per_promoted_function={fid:attempts[fid] for fid in matches},
        model_calls=calls,model_calls_per_match=calls/n if n else None,matches_per_100_model_calls=100*n/calls if calls else None,
        historical_compiler_jobs=jobs,historical_compiler_jobs_per_match=jobs/n if n else None,
        model_cache_hit_rate=sum(bool(p['local_model_metrics'].get('cache_hit')) for p in proposals)/len(proposals) if proposals else None,
        compiler_cache_hit_rate=sum(bool(t.get('cache_hit')) for t in compiled_trials)/len(compiled_trials) if compiled_trials else None,
        token_usage=usage,generation_tokens_per_second=usage['generated_tokens']/prediction_seconds if prediction_seconds else None,
        per_call_tokens_per_second=[p.get('timings',{}).get('predicted_per_second') for p in fresh],
        prompt_budget_measurements=[p['local_model_metrics'].get('budget') for p in proposals],
        gpu=dict(before_server_load=next((p['local_model_metrics'].get('service_gpu_at_start') for p in proposals),None),
                 start=observations[0].get('start') if observations else None,
                 peak_observed_used_mib=max((g['peak_observed_used_mib'] for g in observations if g.get('peak_observed_used_mib') is not None),default=None),
                 minimum_observed_free_mib=min((g['minimum_observed_free_mib'] for g in observations if g.get('minimum_observed_free_mib') is not None),default=None),
                 server_pids=sorted({p['local_model_metrics']['server_pid'] for p in proposals if p['local_model_metrics'].get('server_pid')})),
        wall_clock_seconds=dict(total=wall,model_inference=model_seconds,historical_compilation=compiler_seconds,
                                verification_including_regressions=run.get('verification_seconds',0),
                                orchestration_and_prompt_packing=max(0,wall-model_seconds-compiler_seconds-run.get('verification_seconds',0))),
        gpu_hours=gpu_hours,gpu_hour_definition='Single resident GPU reserved during measured run wall time; includes desktop use and compiler waits; excludes initial model loading.',
        verified_functions_per_gpu_hour=n/gpu_hours if gpu_hours else None,verified_bytes_per_gpu_hour=sum(matches.values())/gpu_hours if gpu_hours else None,
        blocked_this_run_by_class={k:[f for f in v if f in run.get('blocked',[])] for k,v in sorted(blocked.items()) if any(f in run.get('blocked',[]) for f in v)},
        supervisor_blocker_groups=dict(sorted(blocked.items())),recommendations=guidance,
        limitations=['Only new canonical promotions with local-model provenance count; no fixture or hosted-model matches are included.',
                     'VRAM peak is sampled across the whole GPU, including Windows/desktop allocations.',
                     'A small bounded run measures this candidate set; it does not prove whole-overlay convergence.'])


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',type=Path,default=ROOT/'recovery/grinder-last-run.json');a=ap.parse_args()
    report=summarize(json.loads(a.run.read_text()));write_json(ROOT/'recovery/reports'/(report['run_id']+'.json'),report)
    print(json.dumps(report,indent=2))
