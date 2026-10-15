"""Manage one pinned, offline, loopback-only llama.cpp inference worker."""
import argparse
import ctypes
import http.client
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
from common import require,sha256,write_json,FormatError
from setup_local_model import file_hash,ROOT
from gpu_telemetry import snapshot

BASE=ROOT/'build/local-model-server'
STATE=BASE/'service.json'
PORT=18087


def request(state,path,payload=None,timeout=10):
    # No proxy handling, DNS, redirects, user-selected host, or remote fallback.
    require(state['port']==PORT,'unexpected local inference port')
    conn=http.client.HTTPConnection('127.0.0.1',PORT,timeout=timeout)
    try:
        conn.request('POST' if payload is not None else 'GET',path,
                     body=None if payload is None else json.dumps(payload).encode('utf-8'),
                     headers={'Authorization':'Bearer '+state['key'],'Content-Type':'application/json'})
        response=conn.getresponse();raw=response.read(2*1024*1024+1)
        require(len(raw)<=2*1024*1024,'local model response exceeds bound')
        require(response.status==200,'local inference HTTP '+str(response.status)+': '+raw[:300].decode(errors='replace'))
        return json.loads(raw)
    finally:conn.close()


def process_matches(state):
    if os.name!='nt':return False
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
    kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.QueryFullProcessImageNameW.argtypes=[ctypes.c_void_p,ctypes.c_ulong,ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_ulong)]
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    handle=kernel.OpenProcess(0x1000,False,state['pid'])
    if not handle:return False
    try:
        buf=ctypes.create_unicode_buffer(32768);size=ctypes.c_ulong(len(buf))
        return bool(kernel.QueryFullProcessImageNameW(handle,0,buf,ctypes.byref(size))) and Path(buf.value).resolve()==Path(state['executable']).resolve()
    finally:kernel.CloseHandle(handle)


def running():
    require(STATE.exists(),'local model not started: python tools/local_model_server.py start')
    state=json.loads(STATE.read_text())
    require(process_matches(state),'local inference process is not live')
    require(state['lock_sha256']==sha256(Path(state.get('lock_path',ROOT/'toolchain/local-model.lock.json')).read_bytes()),'local model lock changed; restart server')
    require(request(state,'/health').get('status')=='ok','local inference is not ready')
    models=request(state,'/v1/models')
    require(any(m['id']==state['alias'] for m in models['data']),'local inference model identity differs')
    return state


def start(context=8192,kv_cpu=False,lock_path=None,quantization=None):
    lock_path=lock_path or ROOT/'toolchain/qwen3-coder.lock.json'
    if STATE.exists():
        state=json.loads(STATE.read_text())
        if process_matches(state):
            require(state['context_size']==context and state.get('kv_cpu',False)==kv_cpu
                    and Path(state.get('lock_path','')).resolve()==lock_path.resolve()
                    and (not quantization or quantization==state.get('quantization')),
                    'server already resident with different settings; stop it before changing configuration')
            return running()
    lock=json.loads(lock_path.read_text())
    require(2048<=context<=32768,'explicit local context must be 2048..32768 tokens')
    dest=ROOT/'toolchain/installed/local-model';installed=json.loads((dest/'installed.json').read_text())
    for item in installed['inputs']+installed['files']:
        require(file_hash(ROOT/item['path'])==item['sha256'],'local inference artifact changed: '+item['path'])
    model=next(i for i in lock['files'] if i['kind']=='model')
    quantization=quantization or lock.get('quantization','Q4_K_M')
    if quantization!=lock.get('quantization','Q4_K_M'):
        require(quantization==lock.get('fallback',{}).get('quantization'),'unavailable quantization')
        model=lock['fallback']
    model_path=dest/model['name'];require(file_hash(model_path)==model['sha256'],'model weights differ from upstream pin')
    exe=dest/'llama-server.exe';BASE.mkdir(parents=True,exist_ok=True)
    key=secrets.token_hex(32);key_file=BASE/'api-key.txt';key_file.write_text(key+'\n')
    alias='tales-local-coder'
    cmd=[str(exe),'--model',str(model_path),'--offline','--host','127.0.0.1','--port',str(PORT),
         '--ctx-size',str(context),'--parallel','1','--n-gpu-layers','99','--alias',alias,
         '--batch-size','512','--ubatch-size','128','--flash-attn','on','--cache-prompt',
         '--api-key-file',str(key_file),'--no-agent','--no-webui','--no-ui-mcp-proxy']
    if kv_cpu:cmd+=['--no-kv-offload']
    env={k:v for k,v in os.environ.items() if not k.startswith('LLAMA_')}
    vram_start=snapshot()
    with (BASE/'stdout.log').open('wb') as out,(BASE/'stderr.log').open('wb') as err:
        proc=subprocess.Popen(cmd,cwd=BASE,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,
                              creationflags=subprocess.CREATE_NO_WINDOW)
    state=dict(pid=proc.pid,executable=str(exe),port=PORT,key=key,alias=alias,model=lock['model'],
               model_sha256=model['sha256'],runner_sha256=file_hash(exe),lock_sha256=sha256(lock_path.read_bytes()),
               installed_manifest_sha256=sha256((dest/'installed.json').read_bytes()),
               context_size=context,kv_cpu=kv_cpu,quantization=quantization,lock_path=str(lock_path.resolve()),
               gpu_at_start=vram_start,started_unix=time.time(),tools_enabled=False,offline=True)
    write_json(STATE,state)
    deadline=time.monotonic()+120
    while time.monotonic()<deadline:
        require(proc.poll() is None,'local model exited; inspect build/local-model-server/stderr.log')
        try:
            ready=running();ready['gpu_after_load']=snapshot();write_json(STATE,ready);return ready
        except (OSError,FormatError):time.sleep(0.5)
    raise FormatError('local model startup still pending; inspect the existing process before retrying')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['start','status','stop'])
    ap.add_argument('--context',type=int,default=8192);ap.add_argument('--kv-cpu',action='store_true')
    ap.add_argument('--lock',type=Path);ap.add_argument('--quantization',choices=['Q4_K_M','Q4_K_S']);a=ap.parse_args()
    if a.action=='stop':
        require(STATE.exists(),'no managed local server state')
        state=json.loads(STATE.read_text())
        require(process_matches(state),'managed server process is not live')
        subprocess.run(['taskkill','/PID',str(state['pid']),'/F'],check=True,capture_output=True)
        print('Stopped the verified local inference process');return
    state=start(a.context,a.kv_cpu,a.lock,a.quantization) if a.action=='start' else running()
    print(json.dumps({k:v for k,v in state.items() if k!='key'}))


if __name__=='__main__':main()
