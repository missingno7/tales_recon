"""Bounded fact-package / proposer / batched-verifier grinder contract.

A proposer executable reads one JSON fact package on stdin and returns JSON
{"source": "...C..."} on stdout. It receives no project-control responsibilities.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from common import require,write_json,sha256,FormatError
from recovery_state import ROOT,LEDGER,recovery,ranked,facts,save_rank
from check_function import check_many
from compiler_oracle import validate_source,PROFILES


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
    return count>=max_attempts or (already_seen and all(x['cache_hit'] for x in reports))


def run(args):
    require(args.proposer,'--proposer executable [arguments...] is required')
    totals=dict(rounds=0,promoted=[],blocked=[],proposer_errors=[],oracle_runs=[],status='RUNNING')
    for _ in range(args.max_rounds):
        r=recovery();queue=[x for x in ranked(args.node) if x['id'] not in r['blockers']]
        previous_attempts=r['attempts']
        if args.ids:queue=[x for x in queue if x['id'] in args.ids]
        selected=[]
        for item in queue:
            if item['extent']!='CLOSED_CFG' or item['size']>args.max_bytes:continue
            if len(selected)>=args.batch_size:break
            selected.append(item)
        if not selected:
            totals['status']='NO_ELIGIBLE_WORK';break
        requests=[];service_error=None
        for item in selected:
            fid=item['id']
            try:
                package=facts(fid);response=subprocess.run(args.proposer,input=json.dumps(package),capture_output=True,text=True,timeout=args.proposer_timeout)
                if response.returncode!=0:
                    service_error='PROPOSER_SERVICE_FAILURE: '+response.stderr[:500];break
                result=json.loads(response.stdout);source=result['source'];require(isinstance(source,str),'proposer source must be text')
                validate_source(source)
                p=ROOT/'recovery/candidates'/fid/(sha256(source.encode())+'.c');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source,newline='\n')
                requests.append(dict(id=fid,source=str(p),profiles=args.profile or ['aztec36','aztec50-short'],proposer_receipt=result.get('proposer_receipt')))
            except (OSError,subprocess.TimeoutExpired) as exc:
                service_error='PROPOSER_SERVICE_FAILURE: '+str(exc);break
            except (FormatError,ValueError,KeyError) as exc:
                block(fid,'PROPOSER_FAILURE: '+str(exc));totals['proposer_errors'].append(dict(id=fid,reason=str(exc)));totals['blocked'].append(fid)
        if requests:
            reports=check_many(requests,True)
            totals['oracle_runs'].append(json.loads((ROOT/'build/compiler-last-run.json').read_text()))
            for req in requests:
                fid=req['id'];matching=[x for x in reports if x['id']==fid]
                if any(x['verdict']=='EQUAL' for x in matching):totals['promoted'].append(fid)
                else:
                    r=recovery();attempts=r['attempts'].get(fid,[])
                    # A cache hit from a different function is still fresh feedback
                    # for this proposer. Only an already-seen failure ends the item.
                    if exhausted(matching,previous_attempts.get(fid,[]),attempts,args.max_attempts):
                        block(fid,'NON_CONVERGENCE: bounded attempts exhausted or cached failure repeated');totals['blocked'].append(fid)
            print(json.dumps(dict(round=totals['rounds']+1,results=[{k:r[k] for k in ('id','compiler','verdict','expected_length','actual_length','cache_hit')} for r in reports])),flush=True)
        totals['rounds']+=1
        if service_error:
            totals.update(status='SERVICE_BLOCKED',service_error=service_error)
        write_json(ROOT/'recovery/grinder-last-run.json',totals)
        if service_error:break
    if totals['status']=='RUNNING':totals['status']='ROUND_LIMIT'
    save_rank();write_json(ROOT/'recovery/grinder-last-run.json',totals);return totals


def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='action',required=True)
    rank=sub.add_parser('rank');rank.add_argument('--node');rank.add_argument('--limit',type=int,default=20)
    package=sub.add_parser('facts');package.add_argument('id')
    nxt=sub.add_parser('next');nxt.add_argument('--node')
    runner=sub.add_parser('run');runner.add_argument('--node');runner.add_argument('--ids',nargs='+');runner.add_argument('--profile',action='append')
    runner.add_argument('--batch-size',type=int,default=8);runner.add_argument('--max-rounds',type=int,default=20)
    runner.add_argument('--max-attempts',type=int,default=5);runner.add_argument('--max-bytes',type=int,default=512)
    runner.add_argument('--proposer-timeout',type=int,default=360);runner.add_argument('--proposer',nargs=argparse.REMAINDER)
    retry=sub.add_parser('retry');retry.add_argument('id')
    args=ap.parse_args()
    if args.action=='rank':print(json.dumps(ranked(args.node)[:args.limit],indent=2))
    elif args.action=='facts':print(json.dumps(facts(args.id),indent=2))
    elif args.action=='next':
        q=[x for x in ranked(args.node) if x['id'] not in recovery()['blockers'] and x['extent']=='CLOSED_CFG' and x['size']<=512]
        print(json.dumps(facts(q[0]['id']) if q else {'status':'NO_BOUNDED_WORK'},indent=2))
    elif args.action=='retry':
        r=recovery();r['blockers'].pop(args.id,None);write_json(LEDGER,r)
    else:print(json.dumps(run(args),indent=2))

if __name__=='__main__':main()
