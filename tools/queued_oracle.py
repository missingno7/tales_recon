"""One guest batch for ordinary and mixed-profile queued trials.

The two legacy oracle modules remain unchanged because their file hashes are
part of existing cache identities. This runner uses their identity functions,
unchanged guest recipes, extraction and receipt validation. Scheduling does not
change compiler inputs or evidence acceptance. No original game is read here.
"""
import shutil
import subprocess
import time
import uuid
from pathlib import Path

import compiler_oracle
from compiler_oracle import PROFILES, CACHE, identity, object_specs, overlay_proxies, cached, extract
from aztec_worker import ROOT, prepare, collect
from common import require, sha256, write_json, FormatError
import file_lock
import link_line


def trial_plan(trial):
    if trial.get('object_profiles'):
        from mixed_profile_oracle import mixed_identity
        return mixed_identity(trial)
    objects=object_specs(trial)
    key,meta,h=identity(trial['source'],trial['profile'],trial.get('target_node',1),
                        objects if trial.get('objects') is not None else None,
                        trial.get('local_functions',()),trial.get('entry_function','recovered'),
                        trial.get('extra_libraries',()),trial.get('same_overlay_exports'))
    return key,meta,h,objects


def compile_many(trials):
    """Compile ordinary and per-object profile trials together with unchanged identities."""
    started=time.perf_counter()
    requests=[];missing={}
    for trial in trials:
        target_node=trial.get('target_node',1)
        key,meta,h,objects=trial_plan(trial)
        requests.append(key)
        if cached(key) is None:
            missing.setdefault(key,dict(trial=trial,meta=meta,harness=h,
                                        proxies=overlay_proxies(trial['source'],target_node),objects=objects))
    if not missing:
        result=[cached(k) for k in requests]
        write_json(ROOT/'build/compiler-last-run.json',dict(requests=len(requests),unique=len(set(requests)),worker_invocations=0,cache_misses=0,elapsed_seconds=time.perf_counter()-started))
        return result
    CACHE.mkdir(parents=True,exist_ok=True)
    lock=ROOT/'build/compiler-oracle.lock'
    owner=file_lock.try_acquire(lock,'combined compiler batch')
    if owner is None:raise FormatError('compiler worker already active; retry after it completes (stale lock requires inspection)')
    try:
        # Serialize writers and recheck after acquiring the lock.
        missing={k:v for k,v in missing.items() if cached(k) is None}
        if not missing:return [cached(k) for k in requests]
        batch='compile-'+uuid.uuid4().hex[:12];source_dir=ROOT/'build/compiler-inputs'/batch;source_dir.mkdir(parents=True)
        # Aztec 3.6 asks an interactive question after several syntax errors.
        # Decline it explicitly so malformed candidates cannot stall the batch.
        # This changes process I/O, not code-generation identity: prior immutable
        # successful/error cache artifacts remain valid and are never recompiled.
        compiler_input='n\n'*20
        (source_dir/'compiler-input.txt').write_text(compiler_input,encoding='ascii',newline='\n')
        # 5.0a returns 254 on ordinary compilation errors, above the worker's
        # conservative general-purpose default of 100. Continue to record every
        # trial's actual status, including valid trials following a bad one.
        commands=['C:FailAt 1000000'];mapping=[]
        for idx,(key,item) in enumerate(missing.items()):
            prefix='t%03d'%idx;hp='h%03d'%idx;p=PROFILES[item['trial']['profile']];guest=p['guest'];flags=' '.join(p['flags'])
            object_names=[]
            for obj in item['objects']:
                name=prefix if obj['label']=='candidate' else prefix+'_'+obj['label']
                object_names.append(name)
                (source_dir/(name+'.c')).write_text(obj['source'],encoding='ascii',newline='\n')
            (source_dir/(hp+'.c')).write_text(item['harness'],encoding='ascii',newline='\n')
            first=len(commands)
            object_profiles=item['trial'].get('object_profiles') or [item['trial']['profile']]*len(object_names)
            for name,profile in list(zip(object_names,object_profiles))+[(hp,item['trial']['profile'])]:
                object_flags=' '.join(PROFILES[profile]['flags'])
                commands += [f'{guest}bin/cc <compiler-input.txt >{name}-cc.log -a {object_flags} {name}.c',
                             f'{guest}bin/as <compiler-input.txt >{name}-as.log -o {name}.o {name}.asm']
            proxy_args=[]
            for proxy_index,proxy in enumerate(item['proxies']):
                name='p%03d_%02d'%(idx,proxy_index)
                (source_dir/(name+'.c')).write_text(proxy['source'],encoding='ascii',newline='\n')
                commands += [f'{guest}bin/cc <compiler-input.txt >{name}-cc.log -a {flags} {name}.c',
                             f'{guest}bin/as <compiler-input.txt >{name}-as.log -o {name}.o {name}.asm']
                proxy_args += [f'+o{proxy["node"]}',name+'.o']
            node=item['trial'].get('target_node',1)
            command,argument_file=link_line.plan(guest,prefix,hp,node,object_names,proxy_args,item['meta'])
            require((argument_file is not None)==('link_argument_file' in item['meta']),'link argument-file decision differs from cache identity')
            if argument_file is not None:
                (source_dir/argument_file[0]).write_text(argument_file[1],encoding='ascii',newline='\n')
            commands += [command]
            mapping.append((key,item,prefix,hp,first,2*(len(object_names)+1+len(item['proxies']))+1,idx))
        job=prepare(batch,source_dir,commands,Path('C:/Program Files/WinUAE/winuae64.exe'),aztec36=any(v['trial']['profile'].startswith('aztec36') for v in missing.values()))
        shell=shutil.which('pwsh') or shutil.which('powershell')
        require(shell,'PowerShell not found')
        done=subprocess.run([shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'tools/run_worker.ps1'),'-Job',str(job),'-TimeoutSeconds',str(max(120,len(commands)*2))],capture_output=True,text=True)
        require(done.returncode==0,'worker failed: '+done.stdout+done.stderr)
        result=collect(job);work=job/'sys/work'
        for key,item,prefix,hp,first,steps,idx in mapping:
            dest=CACHE/key;dest.mkdir()
            statuses=[s['returncode'] for s in result['steps'][first:first+steps]]
            for f in work.iterdir():
                if f.is_file() and (f.name=='compiler-input.txt' or f.name.startswith(prefix+'.') or f.name.startswith(prefix+'_') or f.name.startswith(prefix+'-') or f.name.startswith(hp+'.') or f.name.startswith(hp+'-') or f.name.startswith('p%03d_'%idx)):
                    shutil.copyfile(f,dest/f.name)
            receipt=dict(cache_key=key,identity=item['meta'],status='COMPILED' if statuses==[0]*steps else 'COMPILE_ERROR',
                guest_returncodes=statuses,worker_job=batch,worker_receipt_sha256=sha256((job/'result.json').read_bytes()),prefix=prefix,
                noninteractive_input_sha256=sha256(compiler_input.encode('ascii')))
            if receipt['status']=='COMPILED':
                try:
                    receipt['contribution']=extract(dest,prefix,item['meta'].get('object_labels'),
                                                    item['trial'].get('entry_function','recovered'),item['meta'].get('same_overlay_exports'))
                except (FormatError,KeyError,ValueError) as exc:receipt.update(status='EXTRACTION_BLOCKED',error=str(exc))
            receipt['artifacts']=[dict(path=f.name,size=f.stat().st_size,sha256=sha256(f.read_bytes())) for f in sorted(dest.iterdir()) if f.is_file()]
            write_json(dest/'receipt.json',receipt)
        result=[dict(cached(k),cache_hit=k not in missing) for k in requests]
        write_json(ROOT/'build/compiler-last-run.json',dict(requests=len(requests),unique=len(set(requests)),worker_invocations=1,cache_misses=len(missing),elapsed_seconds=time.perf_counter()-started))
        return result
    finally:
        file_lock.release(lock,owner)
