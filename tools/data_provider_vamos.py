"""Pinned, serial vamos execution of a complete DATA producer command graph."""
import json,re,time
from pathlib import Path
from common import require,sha256,json_bytes
import vamos_backend as vb


def runtime_pin():
    vamos,spec=vb._runtime();toolchain=vb.toolchain_root()
    require(toolchain.resolve()==(vb.ROOT/spec['toolchain_copy']).resolve(),'DATA producer requires the pinned shared vamos toolchain location')
    return {k:spec[k] for k in ('vamos_executable','vamos_executable_sha256','vamos_python','vamos_python_sha256','amitools_version','machine68k_version','toolchain_copy','tree_inventory','compatibility_shim','compatibility_shim_sha256')}


def execute(job):
    request=json.loads((job/'request.json').read_bytes());work=job/'sys/work';sysroot=job/'vamos-root';sysroot.mkdir()
    pin=runtime_pin();request['backend']='vamos';request['backend_pin']=pin
    (job/'request.json').write_bytes(json_bytes(request))
    vamos,_=vb._runtime();toolchain=vb.toolchain_root();execution=[]
    for step in request['steps']:
        c=step['command'];guest,args=vb.link_guest_command(c)
        require(guest in ('Old1:bin/cc','Old1:bin/as','Old1:bin/ln'),'closed historical compile commands only')
        log=next(t[1:] for t in c.split() if t.startswith('>'));trace=work/(log+'.trace') if guest.endswith('/cc') else None
        if trace is not None:require(not vb.has_float_type((work/args[-1]).read_text(encoding='ascii')),'math/float source requires WinUAE')
        record=vb._run_guest(vamos,sysroot,toolchain,work,guest,args,work/log,trace=trace,timeout=90)
        if trace is not None:require(not vb.trace_math_libraries(trace.read_bytes()),'math library use is not supported by this producer')
        execution.append(record);(work/step['returncode_file']).write_bytes(b'0\n')
    (work/'booted.txt').write_bytes(b'vamos-hosted historical tools\n');(work/'done.txt').write_bytes(b'done\n')
    from aztec_worker import collect
    result=collect(job);result['backend_execution']=execution;(job/'result.json').write_bytes(json_bytes(result))
    return result


def validate(root,job,request,receipt,commands):
    require(request.get('backend')=='vamos' and request.get('backend_pin')==runtime_pin(),'pinned vamos backend/version/inventory changed')
    work=job/'sys/work';sysroot=job/'vamos-root';vamos,_=vb._runtime();toolchain=vb.toolchain_root()
    runs=receipt.get('backend_execution');require(isinstance(runs,list) and len(runs)==len(commands),'complete serial vamos execution graph')
    for c,record in zip(commands,runs):
        guest,args=vb.link_guest_command(c);log=next(t[1:] for t in c.split() if t.startswith('>'));trace=work/(log+'.trace') if guest.endswith('/cc') else None
        require(guest in ('Old1:bin/cc','Old1:bin/as','Old1:bin/ln') and set(record)=={'guest','argv','returncode','wall_seconds','log'},'closed vamos step record')
        require(record['guest']==guest and record['argv']==vb.build_vamos_args(vamos,sysroot,toolchain,work,guest,args,trace) and record['returncode']==0 and record['log']==log and isinstance(record['wall_seconds'],(float,int)) and record['wall_seconds']>=0,'vamos command/argv/status/log differs')
        if trace is not None:
            require(not vb.has_float_type((work/args[-1]).read_text(encoding='ascii')) and not vb.trace_math_libraries(trace.read_bytes()),'float/math source cannot use the vamos DATA producer')
    return dict(backend='vamos',steps=len(runs),runtime_pin=pin_summary(request['backend_pin']))


def pin_summary(pin):
    return {k:pin[k] for k in ('vamos_executable_sha256','vamos_python_sha256','amitools_version','machine68k_version')}


def input_paths(root,request):
    """Explicit backend inputs, once per job; never scratch discovery."""
    from repo_paths import candidate_path,active_files
    require(request.get('backend')=='vamos' and isinstance(request.get('backend_pin'),dict),'unknown DATA backend')
    pin=request['backend_pin'];names={'docs/toolchain.json',pin['vamos_executable'],pin['vamos_python'],pin['compatibility_shim']}
    directory=candidate_path(root,Path(root)/pin['toolchain_copy'])
    require(directory==Path(root)/'build/vamos-toolchain','only the independently pinned shared compiler copy is allowed')
    for relative in vb.TREE_DIRECTORIES:
        for p in active_files(directory/relative):names.add(p.relative_to(root).as_posix())
    return sorted(names)
