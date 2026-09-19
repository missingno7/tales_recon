"""Content-addressed, batched historical compiler oracle. Original game is never read here."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid
import time
from common import require,sha256,write_json,FormatError,json_bytes
from aztec_worker import prepare,collect,ROOT
from hunk import parse,manx_overlay
from overlay_experiment import symbols

PROFILES={
 'aztec36':dict(version='3.6a',base='toolchain/installed/aztec-3.6a/SYS1',guest='Old1:',flags=[]),
 'aztec36-x3':dict(version='3.6a',base='toolchain/installed/aztec-3.6a/SYS1',guest='Old1:',flags=['+X3']),
 'aztec36-long':dict(version='3.6a',base='toolchain/installed/aztec-3.6a/SYS1',guest='Old1:',flags=['+L']),
 'aztec50':dict(version='5.0a',base='toolchain/installed/aztec-5.0a/Aztec2',guest='Tools2:',flags=[]),
 'aztec50-short':dict(version='5.0a',base='toolchain/installed/aztec-5.0a/Aztec2',guest='Tools2:',flags=['-ps'])}
CACHE=ROOT/'build/compile-cache'
SERVICE_VERSION=1


def validate_source(source):
    require(not re.search(r'\b(?:asm|__asm|__asm__)\b',source),'inline assembly is outside candidate-C contract')
    require(not re.search(r'^\s*#\s*(?:include|pragma|line)',source,re.M),'candidate must be self-contained C; includes/pragmas need a pinned harness extension')
    require(bool(re.search(r'\brecovered\s*\(',source)),'candidate must define recovered(...)')
    require(not re.search(r'\brecovered\s*\(\s*(?:signed|unsigned|short|long|char|int|void|float|double|struct)\b',source),
            'use K&R parameter names, then type declarations before the function body; typed ANSI parameters are unsupported')
    require(not re.search(r'\b[GF]_hNN_OFFSET\b',source),'replace placeholder symbols with exact mechanical names from function evidence')
    outside_strings=re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*.*?\*/|//[^\n]*','',source,flags=re.S)
    require(not re.search(r'\\[nrt]',outside_strings),'source has literal backslash escapes outside C strings; JSON source must decode to actual line breaks')
    require(source.isascii(),'historical source must be ASCII')


def overlay_proxies(source,target_node=1):
    """Return ordinary C definitions needed to make a cross-overlay call real.

    A mechanical external such as F_h03_154E denotes original CODE hunk 3.
    The proxy is deliberately empty: it exists only so the historical linker
    emits its normal overlay trampoline.  It is linked in its own node and is
    never part of the extracted candidate contribution.
    """
    proxies=[]
    for m in re.finditer(r'\bextern\s+([^;{}]+);',source):
        decl=m[1].strip()
        if '(' not in decl:continue
        match=re.fullmatch(r'(?:int|long|short|char|void)\s+(F_h(\d+)_[0-9A-Fa-f]+)\s*\(\s*\)',decl)
        if not match:continue
        hunk=int(match[2])
        if hunk < 3:continue
        # HUNKS 0..2 are the resident CODE/DATA/BSS triplet.  The remaining
        # physical code hunks map one-for-one to Manx's one-based overlay node.
        node=hunk-2
        # Same-overlay calls are required to go through check_unit's complete
        # source-unit proof.  A proxy there would create a synthetic local
        # definition and could mask an unrecovered gap.
        if node==target_node:continue
        proxies.append(dict(name=match[1],hunk=hunk,node=node,
                            source='int '+match[1]+'() { return 0; }\n'))
    unique={p['name']:p for p in proxies}
    return [unique[name] for name in sorted(unique)]


def harness(source,target_node=1):
    # Explicit extern declarations become ordinary naturally allocated harness
    # definitions. Mechanical names carry identities for comparison, never layout.
    declarations=re.findall(r'\bstruct\s+\w+\s*\{[^{}]*\}\s*;',source)
    emitted=set(declarations)
    def emit(declaration):
        """Keep repeated compatible externs from becoming duplicate harness definitions."""
        if declaration not in emitted:
            declarations.append(declaration);emitted.add(declaration)
    proxy_names={p['name'] for p in overlay_proxies(source,target_node)}
    for m in re.finditer(r'\bextern\s+([^;{}]+);',source):
        decl=m[1].strip()
        require('\n#' not in decl,'bad extern declaration')
        if '(' in decl:
            match=re.fullmatch(r'(?:(?:unsigned|signed)\s+)?(?:int|long|short|char|void)\s+(\w+)\s*\(\s*\)',decl)
            require(match is not None,'extern function must use old-style empty parameter list')
            # Cross-overlay mechanical functions are supplied by a separate
            # proxy object in their own Manx node.  Keeping them out of the
            # resident harness is what makes the linker produce a trampoline.
            if match[1] not in proxy_names:
                emit(decl+' { return 0; }')
        else:
            require(re.fullmatch(r'(?:(?:unsigned|signed)\s+)?(?:char|short|int|long|float|double|struct\s+\w+)\s+\**\s*\w+(?:\s*\[\s*[1-9]\d*\s*\])*',decl) is not None,'unsupported extern declaration; use scalar/pointer/positive-bound array facts')
            emit(decl+';')
    return '/* Independent naturally allocated link harness. */\nextern int recovered();\nint (*candidate_reference)() = recovered;\nmain() { return 0; }\n'+'\n'.join(declarations)+'\n'


def identity(source,profile,target_node=1):
    validate_source(source);p=PROFILES[profile];h=harness(source,target_node);proxies=overlay_proxies(source,target_node)
    require(target_node>=1,'candidate overlay node must be positive')
    versions={n:sha256((ROOT/p['base']/'bin'/n).read_bytes()) for n in ('cc','as','ln')}
    library='c32.lib' if profile=='aztec36-long' else 'c16.lib' if profile=='aztec50-short' else 'c.lib'
    libbase='toolchain/installed/aztec-3.6a/SYS2' if profile=='aztec36-long' else p['base']
    lib=ROOT/libbase/'lib'/library
    require(lib.is_file(),'missing profile library '+str(lib))
    recipe='harness.o +o%d candidate.o'%target_node
    if proxies:recipe+=' '+' '.join('+o%d %s.o'%(x['node'],x['name']) for x in proxies)
    recipe+=' +o0 c.lib; -m -t'
    keydata=dict(service_version=SERVICE_VERSION,source_sha256=sha256(source.encode('ascii')),
        profile=profile,compiler_version=p['version'],tools=versions,flags=p['flags'],harness_sha256=sha256(h.encode('ascii')),
        headers_sha256=sha256(b''),library=library,library_guest=('Old2:' if profile=='aztec36-long' else p['guest']),library_sha256=sha256(lib.read_bytes()),
        link_recipe=recipe,worker_sha256=sha256((ROOT/'tools/aztec_worker.py').read_bytes()))
    # Preserve all previous default-node cache identities.  A non-default
    # candidate node is material only when a link must model overlay calls.
    if target_node!=1:keydata['candidate_overlay_node']=target_node
    if proxies:
        # Proxy extraction reads semantic HUNK_OVERLAY data, so an old cache
        # entry without that parsed table is never reused after this machinery
        # changes.  Ordinary no-proxy cache identities remain stable.
        keydata['overlay_proxy_extractor_sha256']=sha256((ROOT/'tools/compiler_oracle.py').read_bytes())
        keydata['overlay_proxies']=[dict(name=x['name'],hunk=x['hunk'],node=x['node'],source_sha256=sha256(x['source'].encode('ascii'))) for x in proxies]
    return sha256(json_bytes(keydata)),keydata,h


def cached(key):
    dest=CACHE/key;receipt=dest/'receipt.json'
    if not receipt.exists():return None
    r=json.loads(receipt.read_text());require(r['cache_key']==key,'cache key mismatch')
    require(sha256(json_bytes(r['identity']))==key,'cache identity changed')
    for a in r['artifacts']:
        require((dest/a['path']).is_file() and sha256((dest/a['path']).read_bytes())==a['sha256'],'cached artifact changed: '+a['path'])
    if r['status']=='COMPILED':
        require(extract(dest,r['prefix'])==r['contribution'],'cached contribution metadata changed')
    return dict(r,cache_hit=True,directory=str(dest))


def extract(directory,prefix):
    blob=(directory/(prefix+'.exe')).read_bytes();model=parse(blob)
    overlay=manx_overlay(model,blob) if model['overlay'] is not None else None
    obj=(directory/(prefix+'.o')).read_bytes();require(obj[:2] in (b'AJ',b'CJ'),'unsupported object dialect')
    code_size=int.from_bytes(obj[10:14],'big');data_size=int.from_bytes(obj[14:18],'big');bss_size=int.from_bytes(obj[18:22],'big')
    sym=symbols((directory/(prefix+'.sym')).read_text())
    entries=[(h,v) for (h,n),v in sym.items() if n=='_recovered']
    require(len(entries)==1,'expected one recovered symbol')
    hnum,start=entries[0];h=next(h for h in model['hunks'] if h['number']==hnum)
    require(h['node']!='resident' and 0<=start<code_size,'candidate symbol must lie inside its natural overlay contribution')
    require(h['initialized_size']==(code_size+3)//4*4,'object/HUNK size mismatch')
    raw=blob[h['content_offset']:h['content_offset']+code_size]
    require(blob[h['content_offset']+code_size:h['content_offset']+h['initialized_size']]==bytes((-code_size)%4),'nonzero HUNK padding')
    result=dict(code_hex=raw.hex(),code_size=code_size,data_size=data_size,bss_size=bss_size,hunk=hnum,
        object_sha256=sha256(obj),executable_sha256=sha256(blob),hunks=model['hunks'],
        relocations=[dict(r,relative_offset=r['source_offset']) for r in model['relocations'] if r['source_hunk']==hnum],
        all_relocations=model['relocations'],symbols=[dict(hunk=h,name=n,offset=v) for (h,n),v in sym.items()])
    # Old ordinary cache entries intentionally have no overlay-table payload.
    # Only proxy builds need this extra semantic evidence for call resolution.
    if overlay and any(directory.glob('p*.o')):
        result['overlay_trampolines']=[s for slot in overlay['slots'] for s in slot['symbols']]
    if start:result['entry_offset']=start
    return result


def compile_many(trials):
    """Trials are {source: text, profile: PROFILES key}; one boot for all cache misses."""
    started=time.perf_counter()
    requests=[];missing={}
    for trial in trials:
        target_node=trial.get('target_node',1)
        key,meta,h=identity(trial['source'],trial['profile'],target_node);requests.append(key)
        if cached(key) is None:missing.setdefault(key,dict(trial=trial,meta=meta,harness=h,proxies=overlay_proxies(trial['source'],target_node)))
    if not missing:
        result=[cached(k) for k in requests]
        write_json(ROOT/'build/compiler-last-run.json',dict(requests=len(requests),unique=len(set(requests)),worker_invocations=0,cache_misses=0,elapsed_seconds=time.perf_counter()-started))
        return result
    CACHE.mkdir(parents=True,exist_ok=True)
    lock=ROOT/'build/compiler-oracle.lock'
    try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:raise FormatError('compiler worker already active; retry after it completes (stale lock requires inspection)')
    os.close(fd)
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
            (source_dir/(prefix+'.c')).write_text(item['trial']['source'],encoding='ascii',newline='\n')
            (source_dir/(hp+'.c')).write_text(item['harness'],encoding='ascii',newline='\n')
            first=len(commands)
            for name in (prefix,hp):
                commands += [f'{guest}bin/cc <compiler-input.txt >{name}-cc.log -a {flags} {name}.c',
                             f'{guest}bin/as <compiler-input.txt >{name}-as.log -o {name}.o {name}.asm']
            proxy_args=[]
            for proxy_index,proxy in enumerate(item['proxies']):
                name='p%03d_%02d'%(idx,proxy_index)
                (source_dir/(name+'.c')).write_text(proxy['source'],encoding='ascii',newline='\n')
                commands += [f'{guest}bin/cc <compiler-input.txt >{name}-cc.log -a {flags} {name}.c',
                             f'{guest}bin/as <compiler-input.txt >{name}-as.log -o {name}.o {name}.asm']
                proxy_args += [f'+o{proxy["node"]}',name+'.o']
            node=item['trial'].get('target_node',1)
            commands += [f'{guest}bin/ln <compiler-input.txt >{prefix}-ln.log -m -t -o {prefix}.exe {hp}.o +o{node} {prefix}.o '+ ' '.join(proxy_args) +f' +o0 {item["meta"]["library_guest"]}lib/{item["meta"]["library"]}']
            mapping.append((key,item,prefix,hp,first,2*(2+len(item['proxies']))+1,idx))
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
                if f.is_file() and (f.name=='compiler-input.txt' or f.name.startswith(prefix+'.') or f.name.startswith(prefix+'-') or f.name.startswith(hp+'.') or f.name.startswith(hp+'-') or f.name.startswith('p%03d_'%idx)):
                    shutil.copyfile(f,dest/f.name)
            receipt=dict(cache_key=key,identity=item['meta'],status='COMPILED' if statuses==[0]*steps else 'COMPILE_ERROR',
                guest_returncodes=statuses,worker_job=batch,worker_receipt_sha256=sha256((job/'result.json').read_bytes()),prefix=prefix,
                noninteractive_input_sha256=sha256(compiler_input.encode('ascii')))
            if receipt['status']=='COMPILED':
                try:
                    receipt['contribution']=extract(dest,prefix)
                except (FormatError,KeyError,ValueError) as exc:receipt.update(status='EXTRACTION_BLOCKED',error=str(exc))
            receipt['artifacts']=[dict(path=f.name,size=f.stat().st_size,sha256=sha256(f.read_bytes())) for f in sorted(dest.iterdir()) if f.is_file()]
            write_json(dest/'receipt.json',receipt)
        result=[dict(cached(k),cache_hit=k not in missing) for k in requests]
        write_json(ROOT/'build/compiler-last-run.json',dict(requests=len(requests),unique=len(set(requests)),worker_invocations=1,cache_misses=len(missing),elapsed_seconds=time.perf_counter()-started))
        return result
    finally:
        lock.unlink()
