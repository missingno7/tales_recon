"""Regenerate a whole typed-provider batch through aztec_worker, never import receipts.

Prepare once, run the emitted worker.uae in WinUAE, collect with aztec_worker,
then --pins emits compact replacement pins for supervisor review/reverification.
"""
import argparse,json
from pathlib import Path
from analysis_support import ROOT
from common import require,sha256,json_bytes
from repo_paths import candidate_path
from aztec_worker import prepare
from data_providers import source,document,HARNESSSOURCE,batch_key,STRUCT_CONTROL_SOURCE
from promote_data import manifest_facts

CONTROL=b'int DP_test_target = 7;\nint *DP_test_pointer = &DP_test_target;\n'


def commands(prefixes,controls=()):
    if list(controls)==['extprobe']:
        from data_provider_pointers import commands as external_commands
        return external_commands(prefixes)
    if list(controls)==['dataprobe']:
        from data_provider_cells import commands as cell_commands
        return cell_commands(prefixes)
    out=[]
    for p in prefixes:out += [f'Old1:bin/cc >{p}-cc.log -a +b {p}.c',f'Old1:bin/as >{p}-as.log -o {p}.o {p}.asm']
    out+=['Old1:bin/as >h000-as.log -o h000.o h000.asm']
    for p in prefixes:out += [f'Old1:bin/ln >{p}-ln.log -m -t -o {p}.exe h000.o {p}.o']
    return out


def pins(root,rows,job,controls=(),manifest=None):
    job=candidate_path(root,Path(root)/'build/worker-jobs'/job)
    request_raw=(job/'request.json').read_bytes();result_raw=(job/'result.json').read_bytes()
    request=json.loads(request_raw);receipt=json.loads(result_raw)
    members=[dict(fact=n,fact_sha256=sha256(json_bytes(f)),prefix=f['producer']['prefix']) for n,f in rows]
    require(list(controls) in ([],['structprobe'],['extprobe'],['litprobe'],['tableprobe'],['dataprobe']),'unsupported ABI control')
    prefixes=[m['prefix'] for m in members]+['relprobe']+list(controls)
    require(receipt['all_steps_succeeded'] and receipt['request']==request,'collect a successful batch job before pinning')
    require([s['command'] for s in request['steps']]==commands(prefixes,controls),'job does not produce complete batch')
    for n,f in rows:require((job/'sys/work'/(f['producer']['prefix']+'.c')).read_bytes()==source(f),'producer source differs')
    require((job/'sys/work/relprobe.c').read_bytes()==CONTROL and (job/'sys/work/h000.asm').read_bytes()==HARNESSSOURCE,'controls differ')
    recipe=dict(schema_version=1,job=job.relative_to(Path(root)).as_posix(),profile='aztec36',members=members,prefixes=prefixes,commands=commands(prefixes,controls),sources={s['path']:s['sha256'] for s in request['source_files']},toolchain_inventory_sha256={n:sha256((Path(root)/n).read_bytes()) for n in ['evidence/toolchain/aztec-5.0a.json','evidence/toolchain/aztec-3.6a.json','toolchain/candidate-lock.json']},request_sha256=sha256(request_raw),result_sha256=sha256(result_raw),artifacts={a['path']:a['sha256'] for a in receipt['artifacts']})
    if list(controls)==['structprobe']:
        require((job/'sys/work/structprobe.c').read_bytes()==STRUCT_CONTROL_SOURCE,'struct control differs');recipe['controls']=list(controls)
    if list(controls)==['extprobe']:
        from data_provider_pointers import binder_names,binder_source,CONTROL_SOURCE
        require((job/'sys/work/extprobe.c').read_bytes()==CONTROL_SOURCE and (job/'sys/work/bindptr.asm').read_bytes()==binder_source(binder_names([f for n,f in rows])),'external control/binder differs')
        recipe['controls']=list(controls)
    if list(controls)==['litprobe']:
        from data_provider_literals import CONTROL_SOURCE
        require((job/'sys/work/litprobe.c').read_bytes()==CONTROL_SOURCE,'literal control differs');recipe['controls']=list(controls)
    if list(controls)==['tableprobe']:
        from data_provider_tables import CONTROL_SOURCE
        require((job/'sys/work/tableprobe.c').read_bytes()==CONTROL_SOURCE,'table control differs');recipe['controls']=list(controls)
    if list(controls)==['dataprobe']:
        from data_provider_cells import binder_names,binder_source,CONTROL_SOURCE
        require((job/'sys/work/dataprobe.c').read_bytes()==CONTROL_SOURCE and (job/'sys/work/binddata.c').read_bytes()==binder_source(binder_names([f for n,f in rows])),'DATA cell control/binder differs')
        recipe['controls']=list(controls)
    if manifest:recipe['manifest']=manifest
    recipe['cache_key']=batch_key(recipe);return recipe


def normalize_config(job):
    # Producer validation compares one exact portable mount recipe on Windows.
    config=job/'worker.uae';raw=config.read_bytes().replace(b'\\',b'/').replace(b'\r\n',b'\n')
    config.write_bytes(raw)
    path=job/'request.json';request=json.loads(path.read_bytes());request['config_sha256']=sha256(raw)
    path.write_bytes(json_bytes(request))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',default='evidence/data-providers/batch.json');ap.add_argument('--job',required=True)
    ap.add_argument('--prepare',action='store_true');ap.add_argument('--pins',action='store_true');ap.add_argument('--source-dir',default='build/workers/data-provider-regeneration');ap.add_argument('--emulator',default='C:/Program Files/WinUAE/winuae64.exe');a=ap.parse_args()
    require(a.job.startswith('tu-layout-') and a.prepare!=a.pins,'choose --prepare or --pins for a tu-layout-* job')
    rows=manifest_facts(ROOT,a.manifest);controls=document(ROOT,a.manifest).get('controls',[]);require(controls in ([],['structprobe'],['extprobe'],['litprobe'],['tableprobe'],['dataprobe']),'unsupported control');prefixes=[f['producer']['prefix'] for n,f in rows]+['relprobe']+controls
    if a.prepare:
        directory=candidate_path(ROOT,ROOT/a.source_dir)
        require(directory.is_relative_to(ROOT/'build/workers') and not directory.exists(),'fresh worker source directory required')
        directory.mkdir(parents=True)
        for n,f in rows:(directory/(f['producer']['prefix']+'.c')).write_bytes(source(f))
        if controls==['structprobe']:(directory/'structprobe.c').write_bytes(STRUCT_CONTROL_SOURCE)
        if controls==['extprobe']:
            from data_provider_pointers import binder_names,binder_source,CONTROL_SOURCE
            (directory/'extprobe.c').write_bytes(CONTROL_SOURCE);(directory/'bindptr.asm').write_bytes(binder_source(binder_names([f for n,f in rows])))
        if controls==['litprobe']:
            from data_provider_literals import CONTROL_SOURCE
            (directory/'litprobe.c').write_bytes(CONTROL_SOURCE)
        if controls==['tableprobe']:
            from data_provider_tables import CONTROL_SOURCE
            (directory/'tableprobe.c').write_bytes(CONTROL_SOURCE)
        if controls==['dataprobe']:
            from data_provider_cells import binder_names,binder_source,CONTROL_SOURCE
            (directory/'dataprobe.c').write_bytes(CONTROL_SOURCE);(directory/'binddata.c').write_bytes(binder_source(binder_names([f for n,f in rows])))
        (directory/'relprobe.c').write_bytes(CONTROL);(directory/'h000.asm').write_bytes(HARNESSSOURCE)
        job=prepare(a.job,directory,commands(prefixes,controls),Path(a.emulator),aztec36=True)
        normalize_config(job);print(job)
    else:print(json_bytes(pins(ROOT,rows,a.job,controls,a.manifest if controls else None)).decode('utf-8'),end='')


if __name__=='__main__':main()
