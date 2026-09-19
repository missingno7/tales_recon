"""Bounded fact-package / proposer / batched-verifier grinder contract.

A proposer executable reads one JSON fact package on stdin and returns JSON
{"source": "...C..."} on stdout. It receives no project-control responsibilities.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import uuid
import os
import time
from common import require,write_json,sha256,FormatError
from recovery_state import ROOT,LEDGER,recovery,ranked,facts,save_rank
from check_function import check_many
from compiler_oracle import PROFILES


def block(fid,reason):
    r=recovery();r['blockers'][fid]=dict(state='BLOCKED',reason=reason,attempts=r['attempts'].get(fid,[])[-5:],
                                       ownership_unchanged=True,next_action='Revise ABI/data hypothesis or use a stronger model; retry explicitly')
    write_json(LEDGER,r)
    try:package=facts(fid)
    except FormatError:package=dict(id=fid)
    write_json(ROOT/'recovery/blockers'/(fid+'.json'),dict(blocker=r['blockers'][fid],facts=package))


def exhausted(reports,before,after,max_attempts):
    count=len({a['source_sha256'] for a in after})
    already_seen=any(a['source_sha256']==reports[0]['source_sha256'] for a in before)
    return count>=max_attempts or (already_seen and all(x['cache_hit'] or x.get('reason')=='SOURCE_REJECTED' for x in reports))


def canonical_promotion(reports):
    """True only when the verifier emitted a canonical promotion receipt."""
    return any(report.get('promotion') for report in reports)


def checkpoint(totals):
    totals['elapsed_seconds']=time.time()-totals['started_unix']
    write_json(ROOT/'recovery/runs'/(totals['run_id']+'.json'),totals)
    write_json(ROOT/'recovery/grinder-last-run.json',totals)
    from grinder_report import summarize
    write_json(ROOT/'recovery/reports'/(totals['run_id']+'.json'),summarize(totals,ROOT))


def eligible(item,args,limit):
    return (item['extent']=='CLOSED_CFG' and item['size']<=limit and item.get('node')!='resident'
            and item.get('confidence','HIGH')=='HIGH' and item.get('indirect',0)==0
            and item.get('unknown_calls',0)<=getattr(args,'max_unknown_calls',1)
            and item.get('data_references',0)<=getattr(args,'max_data_references',8)
            and not item.get('pending_local_dependencies') and item.get('same_node_unit_ready',True))


def deferral_reason(item,args,limit):
    """Return the first explicit reason a discovered item is not grinder-safe."""
    if item['extent']!='CLOSED_CFG':return 'UNCERTAIN_EXTENT'
    if item.get('node')=='resident':return 'RESIDENT_DEFERRED'
    if item['size']>limit:return 'SIZE_LIMIT'
    if item.get('confidence','HIGH')!='HIGH':return 'LOW_CONFIDENCE'
    if item.get('indirect',0):return 'INDIRECT_CONTROL_FLOW'
    if item.get('unknown_calls',0)>getattr(args,'max_unknown_calls',1):return 'UNKNOWN_CALL_LIMIT'
    if item.get('data_references',0)>getattr(args,'max_data_references',8):return 'DATA_REFERENCE_LIMIT'
    if item.get('pending_local_dependencies'):return 'UNRECOVERED_LOCAL_DEPENDENCY'
    if not item.get('same_node_unit_ready',True):return 'NONCONTIGUOUS_LOCAL_UNIT'
    return None


def frontier(node=None,limit=512,max_unknown_calls=1,max_data_references=8):
    args=type('Frontier',(),dict(max_unknown_calls=max_unknown_calls,max_data_references=max_data_references))()
    r=recovery();eligible_ids=[];deferred={}
    for item in ranked(node):
        if item['id'] in r['blockers']:continue
        reason=deferral_reason(item,args,limit)
        if reason is None:eligible_ids.append(item['id'])
        else:deferred.setdefault(reason,[]).append(item['id'])
    return dict(schema_version=1,node=node,max_bytes=limit,eligible=eligible_ids,deferred_by_mechanism=deferred,
                blocked_by_mechanism=__import__('grinder_report').summarize(dict(run_id='frontier',status='DIAGNOSED',elapsed_seconds=0),ROOT)['supervisor_blocker_groups'])


def run(args):
    require(args.proposer,'--proposer executable [arguments...] is required')
    totals=dict(run_id=uuid.uuid4().hex,rounds=0,promoted=[],blocked=[],proposer_errors=[],oracle_runs=[],status='RUNNING',
                proposer_command=args.proposer,requested_ids=args.ids,started_unix=time.time(),proposals=[],trials=[],
                verification_seconds=0,profile=getattr(args,'profile',None) or ['aztec36'],max_bytes=args.max_bytes)
    limit=min(args.max_bytes,64) if getattr(args,'adaptive',False) else args.max_bytes
    totals['eligibility_limit']=limit
    for _ in range(args.max_rounds):
        r=recovery();queue=[x for x in ranked(args.node) if x['id'] not in r['blockers']]
        previous_attempts=r['attempts']
        if args.ids:queue=[x for x in queue if x['id'] in args.ids]
        selected=[]
        for item in queue:
            if not eligible(item,args,limit):continue
            if len(selected)>=args.batch_size:break
            selected.append(item)
        if not selected:
            totals['status']='NO_ELIGIBLE_WORK';break
        requests=[];service_error=None
        for item in selected:
            fid=item['id']
            try:
                package=facts(fid)
                sidecar=ROOT/'build/proposer-calls'/(uuid.uuid4().hex+'.json')
                env=dict(os.environ,TALES_PROPOSER_RECEIPT_PATH=str(sidecar.resolve()))
                proposal_start=time.perf_counter()
                response=subprocess.run(args.proposer,input=json.dumps(package),capture_output=True,text=True,timeout=args.proposer_timeout,env=env)
                extra=json.loads(sidecar.read_text()) if sidecar.exists() else {}
                totals['proposals'].append(dict(id=fid,elapsed_seconds=time.perf_counter()-proposal_start,returncode=response.returncode,**extra))
                if response.returncode==3:
                    rejection=json.loads(response.stderr)
                    require(rejection.get('status')=='BLOCKED','invalid bounded proposer rejection')
                    block(fid,rejection.get('blocker_class','PROPOSER_FAILURE')+': '+rejection.get('reason',''))
                    totals['blocked'].append(fid);continue
                if response.returncode!=0:
                    service_error='PROPOSER_SERVICE_FAILURE: '+response.stderr[:500];break
                result=json.loads(response.stdout);source=result['source'];require(isinstance(source,str),'proposer source must be text')
                for key in ('proposer_receipt','proposer_cache_hit'):
                    if key in extra:result[key]=extra[key]
                require(source.isascii() and len(source)<=16384,'proposer source must be bounded ASCII C')
                p=ROOT/'recovery/candidates'/fid/(sha256(source.encode())+'.c');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source,newline='\n')
                requests.append(dict(id=fid,source=str(p),profiles=getattr(args,'profile',None) or ['aztec36'],proposer_receipt=result.get('proposer_receipt')))
            except (OSError,subprocess.TimeoutExpired) as exc:
                service_error='PROPOSER_SERVICE_FAILURE: '+str(exc);break
            except (FormatError,ValueError,KeyError) as exc:
                block(fid,'PROPOSER_FAILURE: '+str(exc));totals['proposer_errors'].append(dict(id=fid,reason=str(exc)));totals['blocked'].append(fid)
        if requests:
            verification_start=time.perf_counter()
            try:reports=check_many(requests,True)
            except (FormatError,OSError) as exc:
                totals.update(status='SERVICE_BLOCKED',service_error='COMPILER_SERVICE_FAILURE: '+str(exc),
                              pending_candidates=[dict(id=r['id'],source=r['source']) for r in requests])
                checkpoint(totals)
                break
            oracle_run=json.loads((ROOT/'build/compiler-last-run.json').read_text())
            totals['oracle_runs'].append(oracle_run)
            totals['verification_seconds']+=max(0,time.perf_counter()-verification_start-oracle_run['elapsed_seconds'])
            for report in reports:
                totals['trials'].append({k:report[k] for k in ('id','verdict','proof_level','reason','compiler','expected_length','actual_length','cache_hit','source_sha256','unit_blocker','relocation_issues','data_contributions','promotion','proposer','compiler_feedback') if k in report})
            for req in requests:
                fid=req['id'];matching=[x for x in reports if x['id']==fid]
                # Some exact checks are intentionally intermediate proofs
                # (for example FUNCTION_WITH_DATA_MATCH).  Only the checker
                # can attach a canonical promotion receipt after its
                # regression gate, so the run report must follow that receipt
                # rather than equating every EQUAL verdict with promotion.
                if canonical_promotion(matching):totals['promoted'].append(fid)
                else:
                    r=recovery();attempts=r['attempts'].get(fid,[])
                    # A cache hit from a different function is still fresh feedback
                    # for this proposer. Only an already-seen failure ends the item.
                    if exhausted(matching,previous_attempts.get(fid,[]),attempts,args.max_attempts):
                        block(fid,'NON_CONVERGENCE: bounded attempts exhausted or cached failure repeated');totals['blocked'].append(fid)
            print(json.dumps(dict(round=totals['rounds']+1,results=[{k:r[k] for k in ('id','compiler','verdict','expected_length','actual_length','cache_hit')} for r in reports])),flush=True)
        totals['rounds']+=1
        if getattr(args,'adaptive',False):
            attempted={t['id'] for t in totals['trials']}
            if len(attempted)>=10 and len(set(totals['promoted']))/len(attempted)>=0.3:
                limit=min(args.max_bytes,max(limit,128 if limit<=64 else 256))
                totals['eligibility_limit']=limit
        if service_error:
            totals.update(status='SERVICE_BLOCKED',service_error=service_error)
        checkpoint(totals)
        if service_error:break
    if totals['status']=='RUNNING':totals['status']='ROUND_LIMIT'
    save_rank();checkpoint(totals);return totals


def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='action',required=True)
    rank=sub.add_parser('rank');rank.add_argument('--node');rank.add_argument('--limit',type=int,default=20)
    package=sub.add_parser('facts');package.add_argument('id')
    nxt=sub.add_parser('next');nxt.add_argument('--node')
    front=sub.add_parser('frontier');front.add_argument('--node');front.add_argument('--max-bytes',type=int,default=512)
    runner=sub.add_parser('run');runner.add_argument('--node');runner.add_argument('--ids',nargs='+');runner.add_argument('--profile',action='append')
    runner.add_argument('--batch-size',type=int,default=8);runner.add_argument('--max-rounds',type=int,default=20)
    runner.add_argument('--max-attempts',type=int,default=5);runner.add_argument('--max-bytes',type=int,default=256)
    runner.add_argument('--max-unknown-calls',type=int,default=1);runner.add_argument('--max-data-references',type=int,default=8)
    runner.add_argument('--adaptive',action='store_true',help='start at 64 bytes and expand only after measured successes')
    runner.add_argument('--proposer-timeout',type=int,default=360);runner.add_argument('--proposer',nargs=argparse.REMAINDER)
    retry=sub.add_parser('retry');retry.add_argument('id')
    args=ap.parse_args()
    if args.action=='rank':print(json.dumps(ranked(args.node)[:args.limit],indent=2))
    elif args.action=='facts':print(json.dumps(facts(args.id),indent=2))
    elif args.action=='next':
        # Keep the interactive selector under the same mechanical contract as
        # unattended runs.  In particular, never hand a proposer a caller
        # whose exact PC-relative binding would require an unowned code gap.
        selector=type('Selector',(),dict(max_unknown_calls=1,max_data_references=8))()
        q=[x for x in ranked(args.node) if x['id'] not in recovery()['blockers'] and eligible(x,selector,512)]
        print(json.dumps(facts(q[0]['id']) if q else {'status':'NO_BOUNDED_WORK'},indent=2))
    elif args.action=='frontier':print(json.dumps(frontier(args.node,args.max_bytes),indent=2))
    elif args.action=='retry':
        r=recovery();r['blockers'].pop(args.id,None);write_json(LEDGER,r)
    else:
        result=run(args)
        print(json.dumps({k:result[k] for k in ('run_id','status','rounds','promoted','blocked','elapsed_seconds')},indent=2))
        print('Report: recovery/reports/'+result['run_id']+'.json')

if __name__=='__main__':main()
