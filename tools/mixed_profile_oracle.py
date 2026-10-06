"""Separate-object compiles whose objects use different link-compatible profiles.

``compiler_oracle`` compiles every object of a trial with one profile and is
deliberately not edited (its file hash is part of some cache identities).  A
trial with ``object_profiles`` (one profile per source object, see
``check_unit.apply_member_profiles``) is compiled here instead, with the same
worker, harness, link recipe, extraction and receipt format:

* The trial ``profile`` links the unit: its tools, ``c.lib`` and flags compile
  the harness and overlay proxies, exactly as in an ordinary trial.
* Object N is compiled with ``cc <flags of object_profiles[N]>``.  All profiles
  must share one ``profile_compat`` link class, and their oracle identities
  must name the same tools, compiler version and library (checked here).
* The cache identity is the ordinary oracle identity plus ``object_profiles``,
  ``member_profiles``, ``link_compatibility`` and this runner's hash, so it
  can never collide with, or change, an ordinary cache key.
  ``compiler_oracle.cached`` validates these receipts unchanged.

Trials without ``object_profiles`` are passed to ``base`` untouched (the
oracle, or the compile queue when installed), keeping their exact keys.
"""
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid
import compiler_oracle
from compiler_oracle import PROFILES,identity,object_specs,overlay_proxies,cached,extract
from common import require,sha256,write_json,FormatError,json_bytes
from aztec_worker import prepare,collect,ROOT
import link_line
import profile_compat

LOCK=ROOT/'build/compiler-oracle.lock'
LINK_FIELDS=('compiler_version','tools','library','library_guest','library_sha256','headers_sha256','worker_sha256')


def is_mixed(trial):
    return bool(trial.get('object_profiles'))


def mixed_identity(trial):
    """``(key, keydata, harness, objects)`` of one per-object profile trial."""
    require(trial.get('objects') is not None,'per-object profiles need separate source objects')
    objects=object_specs(trial);profiles=list(trial['object_profiles']);link=trial['profile']
    require(len(profiles)==len(objects),'one compiler profile per source object is required')
    require(all(p in PROFILES for p in profiles),'unsupported per-object compiler profile')
    klass=profile_compat.link_class([link,*profiles])
    for p in {link,*profiles}:
        require(PROFILES[p]['flags']==profile_compat.PROFILE_FLAGS.get(p),'profile flags differ from the link-compatibility policy: '+p)
        require(PROFILES[p]['base']==PROFILES[link]['base'] and PROFILES[p]['guest']==PROFILES[link]['guest'],
                'profile %s does not use the %s tool installation'%(p,link))
    require(not trial.get('extra_libraries'),'additional link libraries are not supported with per-object profiles')
    node=trial.get('target_node',1);local=trial.get('local_functions',());entry=trial.get('entry_function','recovered')
    _,keydata,h=identity(trial['source'],link,node,objects,local,entry,same_overlay_exports=trial.get('same_overlay_exports'))
    for p in sorted(set(profiles)-{link}):
        _,other,_=identity(trial['source'],p,node,objects,local,entry,same_overlay_exports=trial.get('same_overlay_exports'))
        require(all(other.get(k)==keydata.get(k) for k in LINK_FIELDS),
                'PROFILES_NOT_LINK_COMPATIBLE: %s and %s name different tools or runtime library'%(p,link))
    keydata=dict(keydata,object_profiles=[dict(label=o['label'],profile=p,flags=list(PROFILES[p]['flags']))
                                          for o,p in zip(objects,profiles)],
                 link_compatibility=klass,mixed_profile_runner_sha256=sha256(Path(__file__).read_bytes()))
    if trial.get('member_profiles'):keydata['member_profiles']=dict(sorted(trial['member_profiles'].items()))
    return sha256(json_bytes(keydata)),keydata,h,objects


def trial_key(trial):
    return mixed_identity(trial)[0]


def compile_many(trials,base=None):
    """Ordinary trials go to ``base`` unchanged; per-object profile trials are compiled here."""
    base=base or compiler_oracle.compile_many
    trials=list(trials);results=[None]*len(trials)
    plain=[i for i,t in enumerate(trials) if not is_mixed(t)]
    mixed=[i for i,t in enumerate(trials) if is_mixed(t)]
    if plain:
        for i,r in zip(plain,base([trials[i] for i in plain])):results[i]=r
    if mixed:
        for i,r in zip(mixed,_compile_mixed([trials[i] for i in mixed])):results[i]=r
    return results


def _wait_timeout():
    try:return float(os.environ.get('TALES_COMPILE_WAIT_SECONDS','1800'))
    except ValueError:return 1800.0


def _acquire():
    """Take the oracle's own exclusive lock, waiting (never removing a lock)."""
    deadline=time.monotonic()+_wait_timeout()
    while True:
        try:
            fd=os.open(LOCK,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd);return
        except FileExistsError:
            if time.monotonic()>=deadline:
                raise FormatError('compiler worker still active; per-object profile compile not started '
                                  '(stale lock requires inspection)')
            time.sleep(1.0)


def _compile_mixed(trials):
    started=time.perf_counter();requests=[];missing={}
    for trial in trials:
        key,meta,h,objects=mixed_identity(trial);requests.append(key)
        if cached(key) is None:
            missing.setdefault(key,dict(trial=trial,meta=meta,harness=h,objects=objects,
                                        proxies=overlay_proxies(trial['source'],trial.get('target_node',1))))
    if not missing:return [cached(k) for k in requests]
    compiler_oracle.CACHE.mkdir(parents=True,exist_ok=True)
    _acquire()
    try:
        missing={k:v for k,v in missing.items() if cached(k) is None}
        if not missing:return [cached(k) for k in requests]
        batch='compile-'+uuid.uuid4().hex[:12];source_dir=ROOT/'build/compiler-inputs'/batch;source_dir.mkdir(parents=True)
        compiler_input='n\n'*20
        (source_dir/'compiler-input.txt').write_text(compiler_input,encoding='ascii',newline='\n')
        commands=['C:FailAt 1000000'];mapping=[]
        for idx,(key,item) in enumerate(missing.items()):
            prefix='t%03d'%idx;hp='h%03d'%idx;link=PROFILES[item['trial']['profile']];guest=link['guest']
            link_flags=' '.join(link['flags']);object_names=[];object_flags=[]
            for obj,profile in zip(item['objects'],item['trial']['object_profiles']):
                name=prefix if obj['label']=='candidate' else prefix+'_'+obj['label']
                object_names.append(name);object_flags.append(' '.join(PROFILES[profile]['flags']))
                (source_dir/(name+'.c')).write_text(obj['source'],encoding='ascii',newline='\n')
            (source_dir/(hp+'.c')).write_text(item['harness'],encoding='ascii',newline='\n')
            first=len(commands)
            for name,flags in list(zip(object_names,object_flags))+[(hp,link_flags)]:
                commands += [f'{guest}bin/cc <compiler-input.txt >{name}-cc.log -a {flags} {name}.c',
                             f'{guest}bin/as <compiler-input.txt >{name}-as.log -o {name}.o {name}.asm']
            proxy_args=[]
            for proxy_index,proxy in enumerate(item['proxies']):
                name='p%03d_%02d'%(idx,proxy_index)
                (source_dir/(name+'.c')).write_text(proxy['source'],encoding='ascii',newline='\n')
                commands += [f'{guest}bin/cc <compiler-input.txt >{name}-cc.log -a {link_flags} {name}.c',
                             f'{guest}bin/as <compiler-input.txt >{name}-as.log -o {name}.o {name}.asm']
                proxy_args += [f'+o{proxy["node"]}',name+'.o']
            node=item['trial'].get('target_node',1)
            command,argument_file=link_line.plan(guest,prefix,hp,node,object_names,proxy_args,item['meta'])
            require((argument_file is not None)==('link_argument_file' in item['meta']),'link argument-file decision differs from cache identity')
            if argument_file is not None:
                (source_dir/argument_file[0]).write_text(argument_file[1],encoding='ascii',newline='\n')
            commands += [command]
            mapping.append((key,item,prefix,hp,first,2*(len(object_names)+1+len(item['proxies']))+1,idx))
        job=prepare(batch,source_dir,commands,Path('C:/Program Files/WinUAE/winuae64.exe'),
                    aztec36=any(v['trial']['profile'].startswith('aztec36') for v in missing.values()))
        shell=shutil.which('pwsh') or shutil.which('powershell')
        require(shell,'PowerShell not found')
        done=subprocess.run([shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'tools/run_worker.ps1'),'-Job',str(job),
                             '-TimeoutSeconds',str(max(120,len(commands)*2))],capture_output=True,text=True)
        require(done.returncode==0,'worker failed: '+done.stdout+done.stderr)
        result=collect(job);work=job/'sys/work'
        for key,item,prefix,hp,first,steps,idx in mapping:
            dest=compiler_oracle.CACHE/key;dest.mkdir()
            statuses=[s['returncode'] for s in result['steps'][first:first+steps]]
            for f in work.iterdir():
                if f.is_file() and (f.name=='compiler-input.txt' or f.name.startswith(prefix+'.') or f.name.startswith(prefix+'_') or
                                    f.name.startswith(prefix+'-') or f.name.startswith(hp+'.') or f.name.startswith(hp+'-') or
                                    f.name.startswith('p%03d_'%idx)):
                    shutil.copyfile(f,dest/f.name)
            receipt=dict(cache_key=key,identity=item['meta'],status='COMPILED' if statuses==[0]*steps else 'COMPILE_ERROR',
                         guest_returncodes=statuses,worker_job=batch,worker_receipt_sha256=sha256((job/'result.json').read_bytes()),
                         prefix=prefix,noninteractive_input_sha256=sha256(compiler_input.encode('ascii')))
            if receipt['status']=='COMPILED':
                try:
                    receipt['contribution']=extract(dest,prefix,item['meta'].get('object_labels'),
                                                    item['trial'].get('entry_function','recovered'),item['meta'].get('same_overlay_exports'),
                                                    **({'resident':True} if 'resident_object_extractor_sha256' in item['meta'] else {}))
                except (FormatError,KeyError,ValueError) as exc:receipt.update(status='EXTRACTION_BLOCKED',error=str(exc))
            receipt['artifacts']=[dict(path=f.name,size=f.stat().st_size,sha256=sha256(f.read_bytes())) for f in sorted(dest.iterdir()) if f.is_file()]
            write_json(dest/'receipt.json',receipt)
        write_json(ROOT/'build/compiler-last-run-mixed.json',dict(requests=len(requests),unique=len(set(requests)),worker_invocations=1,
                                                                 cache_misses=len(missing),elapsed_seconds=time.perf_counter()-started))
        return [dict(cached(k),cache_hit=k not in missing) for k in requests]
    finally:
        LOCK.unlink()
