"""Bounded local-model JSON-to-C adapter; all inference stays on loopback."""
import argparse
import json
from pathlib import Path
import sys
import time
from common import require,sha256,json_bytes,write_json,FormatError
from model_proposer import SCHEMA,ROOT
from local_model_server import running,request

LOCAL_PROMPT='''Translate the target Motorola 68000 function to plausible historical C.
Return JSON with one field, source. Define recovered with K&R argument declarations
after the parameter names, before the opening brace. Aztec 3.6a has 16-bit int and
short, 32-bit long and pointers, big endian. A5 is the stack frame, parameters
start at 8(A5); a char parameter occupies a word with the byte at its odd address.
A4-relative symbols are globals. Use exactly the supplied mechanical global and
callee names, never placeholders. Declare each external separately. Functions
must use an empty old-style parameter list in extern declarations. No includes,
assembler, fixed addresses, byte arrays containing code, tools or file access.
Reproduce local variable order, type widths, comparison order and control flow.
The final target disassembly is authoritative. Prior failed source is only a
starting point; correct it using the mismatch. Never replace the target with an
unrelated example. Compiler helpers must arise naturally from C operations.
'''


def model_input(package):
    context={k:package[k] for k in ('abi','cfg','calls','indirect','data','strings','relocations','stack_frames','argument_accesses','recovered_dependencies','previous_attempts','previous_sources') if k in package}
    instructions='\n'.join('0x%04X: %s %s'%(i['offset'],i['mnemonic'],i['operands']) for i in package['instructions'])
    return ('Context and previous feedback:\n'+json.dumps(context,separators=(',',':'))+
            '\nTARGET '+package['id']+' '+json.dumps(package['extent'])+'\n'+instructions+
            '\nProduce source for this TARGET only.')


def parse_response(response):
    choices=response.get('choices',[])
    require(len(choices)==1 and choices[0].get('finish_reason')=='stop','local proposal incomplete')
    message=choices[0]['message']
    require(not message.get('tool_calls') and not message.get('function_call'),'local proposer attempted tools')
    result=json.loads(message['content'])
    require(set(result)=={'source'} and isinstance(result['source'],str),'invalid local proposal schema')
    source=result['source']
    require(source.isascii() and len(source)<=16384,'local source exceeds ASCII/size bound')
    return source


def propose(package,timeout=180):
    require(isinstance(package,dict) and 'id' in package,'function facts required')
    raw=json_bytes(package);require(len(raw)<=100000,'fact package too large')
    state=running()
    prompt=model_input(package)
    identity=dict(model=state['model'],model_sha256=state['model_sha256'],runner_sha256=state['runner_sha256'],
                  installed_manifest_sha256=state['installed_manifest_sha256'],lock_sha256=state['lock_sha256'],
                  facts_sha256=sha256(raw),model_input_sha256=sha256(prompt.encode()),prompt_sha256=sha256(LOCAL_PROMPT.encode()),adapter_sha256=sha256(Path(__file__).read_bytes()),
                  context_size=state['context_size'],temperature=0,seed=1,max_tokens=4096,transport='LOCAL_LOOPBACK_ONLY')
    key=sha256(json_bytes(identity));base=ROOT/'build/local-proposals'/key;base.mkdir(parents=True,exist_ok=True)
    receipt=base/'receipt.json'
    if receipt.exists():
        r=json.loads(receipt.read_text());source=(base/'candidate.c').read_text()
        require(r['identity']==identity and sha256(source.encode('ascii'))==r['source_sha256'],'local proposal cache changed')
        return dict(source=source,proposer_receipt=r['public_receipt'],proposer_cache_hit=True)
    write_json(base/'facts.json',package)
    (base/'input.txt').write_text(prompt,encoding='utf-8',newline='\n')
    payload=dict(model=state['alias'],messages=[dict(role='system',content=LOCAL_PROMPT),dict(role='user',content=prompt)],
                 temperature=0,seed=1,max_tokens=4096,stream=False,
                 response_format=dict(type='json_schema',json_schema=dict(name='candidate',strict=True,schema=SCHEMA)))
    started=time.perf_counter();response=request(state,'/v1/chat/completions',payload,timeout)
    write_json(base/'response.json',response);source=parse_response(response)
    (base/'candidate.c').write_text(source,encoding='ascii',newline='\n')
    public=ROOT/'recovery/proposals'/package['id']/(key+'.json')
    r=dict(schema_version=1,id=package['id'],identity=identity,source_sha256=sha256(source.encode('ascii')),
           usage=response.get('usage',{}),tool_operations=0,elapsed_seconds=time.perf_counter()-started,
           response_sha256=sha256(json_bytes(response)),public_receipt=public.relative_to(ROOT).as_posix(),
           retained_directory=base.relative_to(ROOT).as_posix())
    write_json(receipt,r);write_json(public,r)
    return dict(source=source,proposer_receipt=r['public_receipt'],proposer_cache_hit=False)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--timeout',type=int,default=180);args=ap.parse_args()
    try:print(json.dumps(propose(json.load(sys.stdin),args.timeout)))
    except (FormatError,OSError,ValueError,KeyError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
