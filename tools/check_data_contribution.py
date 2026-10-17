"""Bounded isolated score-DATA verifier. No promotion or accounting writes.

Only the independent semantic score recipe and complete AJ object supported
here are admitted. Original address fields are compared by proved local symbol
identity; arbitrary relocation normalization and clipped object matches reject.
"""
import argparse
import json
from pathlib import Path
from common import require,sha256,FormatError
from repo_paths import canonical_path,candidate_path
from hunk import parse
from overlay_experiment import symbols
from audio_score_recipe import source,encoding
from audio_sequence_data import payload,load

FACT='evidence/data-facts/resident-audio-sequences.json'
RECIPE='evidence/rules/audio-score-16e4/recipe.json'
SOURCE='evidence/rules/audio-score-16e4/score.asm'
COMMANDS=['Old1:bin/as -o score.o score.asm >score-as.log',
          'Old1:bin/ln -m -t -o score.exe score.o >score-ln.log']


def object_code(blob):
    """Exact AJ grammar measured by this isolated local-label control only."""
    require(len(blob)>=36 and blob[:2]==b'AJ' and blob[2:10]==bytes(8),'unsupported score object header')
    u16=lambda p:int.from_bytes(blob[p:p+2],'big')
    u32=lambda p:int.from_bytes(blob[p:p+4],'big')
    size=u32(10);require(size==72 and u32(14)==u32(18)==0,'score must own complete72 CODE/zero DATA/BSS')
    start=u32(24)*4;symstart=u16(28)*4;end=u16(30)*4
    require(start==36 and end==u16(32)*4==len(blob) and blob[34:36]==b'\xc0\0','unsupported score object layout')
    require(u16(22)==3,'score object must have exactly three labels')
    definitions=[];p=symstart
    for _ in range(3):
        require(p+4<=end and blob[p]==2 and blob[p+1] in (8,12),'unsupported score symbol')
        attr=blob[p+1];value=u16(p+2);p+=4
        if attr==12:
            require(p+2<=end and u16(p)==len(definitions),'score relocation symbol index differs');p+=2
        stop=blob.find(b'\0',p,end);require(stop>=p,'unterminated score symbol')
        definitions.append(dict(name=blob[p:stop].decode('ascii'),offset=value));p=stop+1
    require(end-p<=3 and blob[p:]==bytes(end-p),'score symbol trailer differs')
    require(definitions==[dict(name='_score_begin',offset=0),dict(name='_score_pattern',offset=18),dict(name='_score_end',offset=72)],'score object symbol boundaries differ')
    code=bytearray();fixups=[];p=start
    while len(code)<size:
        require(p<symstart,'truncated score object stream');token=blob[p];p+=1
        if 0x10<=token<=0x1f:
            n=token-0x10+1
            require(p+n<=symstart and len(code)+n<=size,'score literal overruns object')
            code+=blob[p:p+n];p+=n
        else:
            require(token==0xfd and p+5<=symstart,'unsupported score object token')
            index=blob[p]-0x70;addend=u32(p+1);p+=5
            require(index==1 and addend==0 and len(code)==68,'unsupported score fixup')
            fixups.append(dict(offset=68,width=4,symbol='_score_pattern',addend=0))
            code+=definitions[index]['offset'].to_bytes(4,'big')
    require(symstart-p<=3 and blob[p:symstart]==bytes(symstart-p),'score CODE trailer differs')
    require(len(fixups)==1,'missing/extra score object relocation')
    return dict(code=bytes(code),definitions=definitions,fixups=fixups)


def compare(original,original_model,fact,object_blob,linked_blob,symbol_text):
    interval=fact['interval'];start=0x16e4;end=0x172c
    require(interval['hunk']==0 and interval['start']<=start<end<=interval['end'],'score experiment outside classified data')
    require(start in fact['roots'],'score experiment lacks original stream-header identity')
    command={x['offset']:x for x in fact['layout']['commands']}
    require(start+18 in command and command[start+66]['kind']=='JUMP' and command[start+66]['pointer_field']==start+68,'original local pattern binding differs')
    expected=payload(original,original_model,0)[start:end]
    require(fact['oracle_sha256']==sha256(original),'original data fixture differs')
    obj=object_code(object_blob);linked=parse(linked_blob)
    require(len(linked['hunks'])==3 and [(h['number'],h['type']) for h in linked['hunks']]==[(0,'CODE'),(1,'DATA'),(2,'BSS')],'score link topology differs')
    h=linked['hunks'][0]
    require(h['initialized_size']==h['allocated_size']==72 and h['zero_fill_size']==0,'score CODE is clipped or contains extra bytes')
    require(linked['hunks'][1]['allocated_size']==0 and linked['hunks'][2]['allocated_size']==4,'unexpected link allocation (pinned linker has minimum4-byte BSS)')
    sm=symbols(symbol_text)
    require(all(sm.get((0,x['name']))==x['offset'] for x in obj['definitions']),'score linked symbol coordinates differ')
    expected_symbols={'__H0_org','_score_begin','_score_pattern','_score_end','__H0_end'}
    require({n for (hn,n) in sm if hn==0}==expected_symbols,'unexpected score CODE symbols')
    actual=payload(linked_blob,linked,0)
    require(actual==obj['code'],'complete AJ object does not reproduce linked CODE')
    original_rels=[r for r in original_model['relocations'] if r['source_hunk']==0 and r['source_offset']<end and start<r['source_offset']+r['width']]
    require(len(original_rels)==1,'original score relocation count differs')
    r=original_rels[0]
    require((r['source_offset']-start,r['width'],r['type'],r['target_hunk'],r['addend_raw']-start)==(68,4,'HUNK_RELOC32',0,18),'original score pointer is not the local pattern label')
    require(int.from_bytes(expected[68:72],'big')==r['addend_raw'],'original pointer payload/metadata differ')
    require(len(linked['relocations'])==1,'score candidate has extra/missing relocations')
    r=linked['relocations'][0]
    require((r['source_hunk'],r['source_offset'],r['width'],r['type'],r['target_hunk'],r['addend_raw'])==(0,68,4,'HUNK_RELOC32',0,18),'candidate score pointer binding differs')
    # Prove both address fields by local symbol identity first, then compare
    # all ordinary bytes. No unrelated field can be ignored or normalized.
    differences=[dict(offset=p,expected=expected[p],actual=actual[p]) for p in range(68) if expected[p]!=actual[p]]
    return dict(verdict='DIFFER' if differences else 'EQUAL_CANDIDATE',kind='BOUNDED_INITIALIZED_CODE_DATA',
                complete_logical_stream=True,original=dict(hunk=0,start=start,end=end,size=72,sha256=sha256(expected)),
                candidate=dict(hunk=0,start=0,end=72,size=72,sha256=sha256(actual)),ordinary_bytes_compared=68,
                fields=[dict(offset=68,width=4,type='HUNK_RELOC32',target_hunk=0,target_symbol='_score_pattern',target_relative_offset=18,original_target=start+18)],
                differences=differences,source_acceptance=False,accounting_acceptance=False,proof_level=None,
                ownership='UNKNOWN',historical_object_membership='UNKNOWN',root_layout_proof=False,
                link_only_bss_allocation=4)



def environment(root,job,headless=False):
    installed=Path(root)/'toolchain/installed/aztec-5.0a'
    older=Path(root)/'toolchain/installed/aztec-3.6a'
    expected_config=f'''config_description=DuckTales isolated historical build worker
use_gui=no
kickstart_rom_file={job/'kick.rom'}
cpu_model=68020
cpu_speed=max
cpu_compatible=false
cpu_24bit_addressing=true
chipset=aga
chipmem_size=4
fastmem_size=8
bogomem_size=0
sound_output=none
gfx_fullscreen_amiga=false
gfx_width_windowed=640
gfx_height_windowed=256
gfx_framerate=10
win32.start_minimized=yes
win32.inactive_pause=false
win32.minimized_pause=false
filesystem2=rw,DH0:Worker:{job/'sys'},0
filesystem2=ro,DH1:Tools1:{installed/'Aztec1'},-128
filesystem2=ro,DH2:Tools2:{installed/'Aztec2'},-128
filesystem2=ro,DH3:Tools4:{installed/'Aztec4'},-128
filesystem2=ro,DH4:Old1:{older/'SYS1'},-128
filesystem2=ro,DH5:Old2:{older/'SYS2'},-128
'''
    if headless:expected_config+='headless=true\ngfx_api=directdraw\n'
    startup=['C:FailAt 100','C:Assign Aztec1: Tools1:','C:Assign Aztec2: Tools2:',
             'C:Assign INCLUDE: Tools1:include','C:Assign LIB: Tools2:lib',
             'C:Path Tools2:bin ADD','C:Stack 65536','C:CD SYS:work','C:Echo booted >booted.txt']
    for n,command in enumerate(COMMANDS):startup += [command,'C:Echo $RC >step-%02d.rc'%n]
    startup.append('C:Echo done >done.txt')
    # Host path spelling (D:/ versus D:\) depends on the shell that prepared
    # the job; every mount, ROM and option must still match exactly.
    spelling=lambda text:text.replace('\\','/')
    require(spelling((job/'worker.uae').read_text())==spelling(expected_config),'producer mounts/configuration recipe differs')
    require((job/'sys/s/startup-sequence').read_text()=='\n'.join(startup)+'\n','producer startup recipe differs')
    for folder in ('c','l','libs','devs'):
        original=installed/'Aztec1'/folder
        expected={p.relative_to(original).as_posix():sha256(p.read_bytes()) for p in original.rglob('*') if p.is_file()}
        copies=job/'sys'/folder
        actual={p.relative_to(copies).as_posix():sha256(p.read_bytes()) for p in copies.rglob('*') if p.is_file()}
        require(expected==actual,'producer guest OS/command copy differs: '+folder)


def producer(root,job,recipe,expected_source):
    job=candidate_path(root,job);request=json.loads((job/'request.json').read_text());receipt=json.loads((job/'result.json').read_text())
    require(receipt.get('request')==request and receipt.get('all_steps_succeeded') is True,'producer receipt/request differs')
    require([s['command'] for s in request['steps']]==COMMANDS and len(receipt['steps'])==2 and all(s['returncode']==0 for s in receipt['steps']),'score producing commands/status differ')
    require(receipt['steps']==[dict(s,returncode=0) for s in request['steps']],'producer step graph differs')
    require(request['source_files']==[dict(path='score.asm',sha256=sha256(expected_source))],'producer source inventory differs')
    require((job/'sys/work/score.asm').read_bytes()==expected_source==source(recipe).encode('ascii'),'score source differs from independent semantic recipe')
    # Full pinned inventory, not a worker-selected subset of tools.
    from aztec_worker import ROOT as actual_root
    require(Path(root).resolve()==actual_root.resolve(),'producer toolchain root differs')
    lock=json.loads(canonical_path(root,'toolchain/candidate-lock.json').read_text())
    require(request['archive_sha256']==lock['sha256'] and sha256(canonical_path(root,lock['archive']).read_bytes())==lock['sha256'],'pinned toolchain archive differs')
    pins=[]
    report=json.loads(canonical_path(root,'evidence/toolchain/aztec-5.0a.json').read_text())
    for disk in report['disks']:
        if disk['status']=='VALIDATED':
            pins += [dict(path='toolchain/installed/aztec-5.0a/'+disk['volume']+'/'+e['path'],sha256=e['sha256']) for e in disk['filesystem_manifest']['entries'] if e['kind']=='file']
    report=json.loads(canonical_path(root,'evidence/toolchain/aztec-3.6a.json').read_text())
    for disk in report['disks']:
        if disk['status']=='VALIDATED':
            pins += [dict(path='toolchain/installed/aztec-3.6a/'+disk['manifest']['volume']+'/'+e['path'],sha256=e['sha256']) for e in disk['manifest']['entries'] if e['kind']=='file']
    require(request['pinned_inputs']==pins,'omitted/changed pinned producer inventory')
    for pin in pins:require(sha256(canonical_path(root,pin['path']).read_bytes())==pin['sha256'],'pinned producer file differs')
    require(sha256(Path(request['emulator']).read_bytes())==request['emulator_sha256'],'emulator changed')
    environment(root,job)
    for name,key in (('kick.rom','rom_sha256'),('worker.uae','config_sha256'),('sys/s/startup-sequence','guest_script_sha256')):
        require(sha256((job/name).read_bytes())==request[key],'producer configuration differs: '+name)
    rom=next(x for x in lock['members'] if x['path']=='Kick30.rom')
    require(request['rom_sha256']==rom['sha256'],'producer ROM pin differs')
    artifacts=receipt['artifacts'];names=[p['path'] for p in artifacts]
    require(len(names)==len(set(names)),'duplicate artifact inventory')
    actual_names=sorted(p.relative_to(job/'sys/work').as_posix() for p in (job/'sys/work').rglob('*') if p.is_file())
    require(sorted(names)==actual_names and {'score.asm','score.o','score.exe','score.sym','done.txt','step-00.rc','step-01.rc'}<=set(names),'producer artifact inventory incomplete')
    for item in artifacts:
        p=(job/'sys/work'/item['path']).resolve();require(p.is_relative_to((job/'sys/work').resolve()),'artifact path escapes job')
        require(p.stat().st_size==item['size'] and sha256(p.read_bytes())==item['sha256'],'producer artifact changed')
    require((job/'sys/work/done.txt').read_text().strip()=='done' and all((job/('sys/work/step-%02d.rc'%n)).read_text().strip()=='0' for n in range(2)),'guest completion/status differs')
    return dict(job=str(job),request_sha256=sha256((job/'request.json').read_bytes()),receipt_sha256=sha256((job/'result.json').read_bytes()),source_sha256=sha256(expected_source),object_sha256=sha256((job/'sys/work/score.o').read_bytes()),linked_sha256=sha256((job/'sys/work/score.exe').read_bytes()))


def verify(root,job,blob,model,fact,recipe,source_bytes):
    evidence=producer(root,job,recipe,source_bytes);w=Path(job)/'sys/work'
    semantic=encoding(recipe)
    require(semantic['pattern_offset']==18 and semantic['pointer_field']==68 and
            object_code((w/'score.o').read_bytes())['code']==semantic['code'],
            'complete producer object differs from independent semantic recipe')
    report=compare(blob,model,fact,(w/'score.o').read_bytes(),(w/'score.exe').read_bytes(),(w/'score.sym').read_text())
    report['producer']=evidence;return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--isolated',action='store_true',required=True)
    ap.add_argument('--job',type=Path,required=True)
    args=ap.parse_args()
    from analysis_support import ROOT
    from census import derive,verify_lock
    verify_lock(ROOT);_,files,model=derive(ROOT,promotion_evidence=False);blob=files['DT1:DuckTales']
    fact=next(f for f in load(ROOT,blob,model) if f['evidence_path']==FACT)
    recipe=json.loads(canonical_path(ROOT,RECIPE).read_text());asm=canonical_path(ROOT,SOURCE).read_bytes()
    report=verify(ROOT,args.job,blob,model,fact,recipe,asm)
    print(json.dumps(report,indent=2));return 0 if report['verdict']=='EQUAL_CANDIDATE' else 1


if __name__=='__main__':
    try:raise SystemExit(main())
    except (FormatError,OSError,ValueError,StopIteration,KeyError) as exc:
        print(json.dumps(dict(verdict='BLOCKED',reason=str(exc),source_acceptance=False,proof_level=None)));raise SystemExit(1)
