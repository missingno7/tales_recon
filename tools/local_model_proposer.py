"""Production local proposer: bounded facts in, JSON source only out."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import time
from common import require,sha256,json_bytes,write_json,FormatError
from model_proposer import ROOT,SCHEMA
from local_proposer import parse_response
from local_model_server import running
from local_http import LocalHTTP
from local_fact_pack import fit,BudgetError,SYSTEM
from gpu_telemetry import Sampler


class ProposalRejected(FormatError):
    def __init__(self,message,metadata):super().__init__(message);self.metadata=metadata


def service(endpoint=None,model=None,identity_file=None):
    if identity_file:
        state=json.loads(Path(identity_file).read_text())
        for k in ('model_sha256','runner_sha256'):
            require(re.fullmatch('[0-9a-f]{64}',state.get(k,'')) is not None,'custom local service needs pinned '+k)
        require(endpoint,'custom service identity requires --endpoint')
        key=Path(state['key_file']).read_text().strip() if state.get('key_file') else ''
    else:
        state=running();key=state['key']
        if endpoint:
            probe=LocalHTTP(endpoint)
            require(probe.host=='127.0.0.1' and probe.port==state['port'],'custom server requires --identity-file')
    client=LocalHTTP(endpoint or 'http://127.0.0.1:%d'%state['port'],key)
    alias=model or state['alias']
    require(any(x['id']==alias for x in client.call('/v1/models')['data']),'requested model name is not served by the local endpoint')
    return client,state,alias


def propose(package,endpoint=None,model=None,temperature=0.3,max_tokens=1024,seed=1,timeout=180,identity_file=None):
    require(isinstance(package,dict) and re.fullmatch(r'(?:ov\d+|resident)_F_[0-9A-F]+',package.get('id','')),'invalid function fact identity')
    require(0<=temperature<=2 and 1<=max_tokens<=8192,'invalid generation parameters')
    raw=json_bytes(package);require(len(raw)<=100000,'generic facts exceed input bound')
    client,state,alias=service(endpoint,model,identity_file)
    generation=dict(temperature=temperature,max_tokens=max_tokens,seed=seed,top_p=0.95,top_k=40,repeat_penalty=1.05)
    identity=dict(model=state['model'],model_alias=alias,quantization=state.get('quantization'),
                  model_sha256=state['model_sha256'],runner_sha256=state['runner_sha256'],
                  context_size=state['context_size'],kv_cpu=state.get('kv_cpu',False),generation=generation,
                  facts_sha256=sha256(raw),system_sha256=sha256(SYSTEM.encode()),transport='LOCAL_LOOPBACK_ONLY',
                  implementation={n:sha256((ROOT/'tools'/n).read_bytes()) for n in ('local_model_proposer.py','local_fact_pack.py','local_http.py')})
    key=sha256(json_bytes(identity));base=ROOT/'build/local-model-proposals'/key;base.mkdir(parents=True,exist_ok=True)
    public=ROOT/'recovery/proposals'/package['id']/(key+'.json');receipt=base/'receipt.json'
    def metadata(r,hit):
        return dict(proposer_receipt=public.relative_to(ROOT).as_posix(),proposer_cache_hit=hit,
                    local_model_metrics=dict(cache_hit=hit,model_call=not hit and r.get('response_sha256') is not None,
                        model_identity=identity,budget=r.get('budget'),usage=r.get('usage',{}),timings=r.get('timings',{}),
                        inference_seconds=0 if hit else r.get('inference_seconds',0),gpu=r.get('gpu'),
                        status=r['status'],blocker_class=r.get('blocker_class'),server_pid=state.get('pid'),
                        service_gpu_at_start=state.get('gpu_at_start')))
    if receipt.exists():
        r=json.loads(receipt.read_text());require(r['identity']==identity,'local proposal cache identity changed')
        if r.get('response_sha256'):require(sha256((base/'response.json').read_bytes())==r['response_sha256'],'cached raw response changed')
        meta=metadata(r,True)
        if r['status']!='PROPOSED':raise ProposalRejected(r['error'],meta)
        source=(base/'candidate.c').read_text()
        require(sha256(source.encode('ascii'))==r['source_sha256'],'cached source changed')
        require(public.exists() and json.loads(public.read_text())==r,'public proposal receipt changed')
        return dict(source=source,**meta)
    write_json(base/'facts.json',package)
    r=dict(schema_version=1,id=package['id'],identity=identity,tool_operations=0,
           public_receipt=public.relative_to(ROOT).as_posix(),retained_directory=base.relative_to(ROOT).as_posix())
    try:
        started=time.perf_counter()
        messages,budget=fit(package,client.count,state['context_size'],max_tokens)
        r.update(budget=budget,packing_seconds=time.perf_counter()-started)
        write_json(base/'messages.json',messages)
        payload=dict(model=alias,messages=messages,**generation,stream=False,cache_prompt=True,
                     response_format=dict(type='json_schema',json_schema=dict(name='candidate',strict=True,schema=SCHEMA)))
        with Sampler() as gpu:
            started=time.perf_counter();response=client.call('/v1/chat/completions',payload,timeout)
            r['inference_seconds']=time.perf_counter()-started
        write_json(base/'response.json',response)
        r.update(response_sha256=sha256((base/'response.json').read_bytes()),usage=response.get('usage',{}),
                 timings=response.get('timings',{}),gpu=gpu.summary())
        try:
            source=parse_response(response);require(bool(source.strip()),'empty local source')
            require(not response.get('truncated',False),'server truncated the context')
        except (FormatError,KeyError,ValueError) as exc:
            r.update(status='REJECTED_RESPONSE',error=str(exc),blocker_class='MODEL_RESPONSE')
            write_json(receipt,r);write_json(public,r);raise ProposalRejected(str(exc),metadata(r,False))
        (base/'candidate.c').write_text(source,encoding='ascii',newline='\n')
        r.update(status='PROPOSED',source_sha256=sha256(source.encode('ascii')))
    except BudgetError as exc:
        r.update(status='CONTEXT_BLOCKED',error=str(exc),blocker_class='CONTEXT_BUDGET')
        write_json(receipt,r);write_json(public,r);raise ProposalRejected(str(exc),metadata(r,False))
    write_json(receipt,r);write_json(public,r)
    return dict(source=source,**metadata(r,False))


def sidecar(metadata):
    path=os.environ.get('TALES_PROPOSER_RECEIPT_PATH')
    if path:
        target=Path(path).resolve()
        require(target.is_relative_to((ROOT/'build/proposer-calls').resolve()),'proposer sidecar escapes designated directory')
        write_json(target,metadata)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--endpoint',default=os.environ.get('TALES_LOCAL_ENDPOINT'))
    ap.add_argument('--model');ap.add_argument('--temperature',type=float,default=0.3)
    ap.add_argument('--max-output-tokens',type=int,default=1024);ap.add_argument('--seed',type=int,default=1)
    ap.add_argument('--timeout',type=int,default=180);ap.add_argument('--identity-file',type=Path)
    a=ap.parse_args()
    try:
        result=propose(json.load(sys.stdin),a.endpoint,a.model,a.temperature,a.max_output_tokens,a.seed,a.timeout,a.identity_file)
        sidecar({k:v for k,v in result.items() if k!='source'})
        print(json.dumps(dict(source=result['source'])))
    except ProposalRejected as exc:
        sidecar(exc.metadata)
        print(json.dumps(dict(status='BLOCKED',blocker_class=exc.metadata['local_model_metrics']['blocker_class'],reason=str(exc))),file=sys.stderr)
        return 3
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (FormatError,OSError,ValueError,KeyError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
