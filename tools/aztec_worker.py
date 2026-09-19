"""Prepare isolated WinUAE jobs from pinned candidate tools. No game oracle reads.

Each preparation requires a fresh name and retains its source, guest script,
configuration, tool identities, assembly, objects, link output and logs.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile

from common import FormatError, require, sha256, write_json

ROOT = Path(__file__).resolve().parents[1]


def prepare(name, source_dir, commands, emulator):
    require(re.fullmatch(r'[a-zA-Z0-9_-]+', name) is not None, 'invalid experiment name')
    base = ROOT/'build/worker-jobs'/name
    require(not base.exists(), 'job exists; use a new name to preserve prior experiments')
    lock = json.loads((ROOT/'toolchain/candidate-lock.json').read_text())
    archive = ROOT/lock['archive']
    require(sha256(archive.read_bytes())==lock['sha256'], 'Aztec archive changed')
    inventory = json.loads((ROOT/'evidence/toolchain/aztec-5.0a.json').read_text())
    require(inventory['archive_sha256']==lock['sha256'], 'candidate inventory belongs to another archive')
    installed = ROOT/'toolchain/installed/aztec-5.0a'
    # Validate every candidate file, including OS dependencies mounted read-only.
    pinned = []
    for disk in inventory['disks']:
        if disk['status']!='VALIDATED':
            continue
        for entry in disk['filesystem_manifest']['entries']:
            if entry['kind']!='file':
                continue
            p=installed/disk['volume']/entry['path']
            require(p.is_file() and sha256(p.read_bytes())==entry['sha256'], f'candidate file changed: {p}')
            pinned.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=entry['sha256']))
    require(emulator.is_file(), 'WinUAE executable not found')
    source_files = sorted(p for p in source_dir.rglob('*') if p.is_file())
    require(source_files, 'experiment source directory is empty')
    guest=base/'sys';work=guest/'work';work.mkdir(parents=True)
    (guest/'s').mkdir()
    for folder in ('c','l','libs','devs'):
        shutil.copytree(installed/'Aztec1'/folder,guest/folder)
    for p in source_files:
        target=work/p.relative_to(source_dir)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,target)
    with zipfile.ZipFile(archive) as z:
        rom=z.read('Kick30.rom')
    rom_entry=next(m for m in lock['members'] if m['path']=='Kick30.rom')
    require(sha256(rom)==rom_entry['sha256'],'ROM member mismatch')
    (base/'kick.rom').write_bytes(rom)
    startup=['C:FailAt 100','C:Assign Aztec1: Tools1:','C:Assign Aztec2: Tools2:',
             'C:Assign INCLUDE: Tools1:include','C:Assign LIB: Tools2:lib',
             'C:Path Tools2:bin ADD','C:Stack 65536','C:CD SYS:work','C:Echo booted >booted.txt']
    steps=[]
    for i,command in enumerate(commands):
        require('\n' not in command and '\r' not in command, 'commands must be single guest shell lines')
        startup += [command, f'C:Echo $RC >step-{i:02d}.rc']
        steps.append(dict(index=i, command=command, returncode_file=f'step-{i:02d}.rc'))
    startup.append('C:Echo done >done.txt')
    (guest/'s/startup-sequence').write_text('\n'.join(startup)+'\n',encoding='ascii',newline='\n')
    config=f'''config_description=DuckTales isolated historical build worker
use_gui=no
kickstart_rom_file={base/'kick.rom'}
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
filesystem2=rw,DH0:Worker:{guest},0
filesystem2=ro,DH1:Tools1:{installed/'Aztec1'},-128
filesystem2=ro,DH2:Tools2:{installed/'Aztec2'},-128
filesystem2=ro,DH3:Tools4:{installed/'Aztec4'},-128
'''
    (base/'worker.uae').write_text(config,encoding='utf-8')
    write_json(base/'request.json',dict(schema_version=1,name=name,archive_sha256=lock['sha256'],
        emulator=str(emulator),emulator_sha256=sha256(emulator.read_bytes()),rom_sha256=sha256(rom),
        pinned_inputs=pinned,steps=steps,source_files=[dict(path=p.relative_to(source_dir).as_posix(),sha256=sha256(p.read_bytes())) for p in source_files],
        guest_script_sha256=sha256((guest/'s/startup-sequence').read_bytes()),
        config_sha256=sha256((base/'worker.uae').read_bytes()),
        source_policy='Experiment source supplied independently; original game not mounted or read.'))
    return base


def collect(base):
    request=json.loads((base/'request.json').read_text())
    work=base/'sys/work'
    require((work/'done.txt').is_file(), 'guest did not reach completion marker')
    steps=[]
    for step in request['steps']:
        raw=(work/step['returncode_file']).read_text().strip()
        require(raw.isdigit(), f'unparseable guest status {raw!r}')
        steps.append(dict(step,returncode=int(raw)))
    artifacts=[dict(path=p.relative_to(work).as_posix(),size=p.stat().st_size,sha256=sha256(p.read_bytes()))
               for p in sorted(work.rglob('*')) if p.is_file()]
    result=dict(schema_version=1,request=request,steps=steps,all_steps_succeeded=all(s['returncode']==0 for s in steps),
                artifacts=artifacts,reconstruction_proof_level=None)
    write_json(base/'result.json',result)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest='action',required=True)
    prep=sub.add_parser('prepare');prep.add_argument('name');prep.add_argument('source',type=Path)
    prep.add_argument('--commands',type=Path,required=True,help='JSON array of explicit guest command lines')
    prep.add_argument('--emulator',type=Path,default=Path('C:/Program Files/WinUAE/winuae64.exe'))
    coll=sub.add_parser('collect');coll.add_argument('job',type=Path)
    args=ap.parse_args()
    if args.action=='prepare':
        print(prepare(args.name,args.source,json.loads(args.commands.read_text()),args.emulator))
        return 0
    result=collect(args.job)
    print('Guest return codes:',[s['returncode'] for s in result['steps']])
    return 0 if result['all_steps_succeeded'] else 1


if __name__=='__main__':
    try:
        sys.exit(main())
    except (FormatError,OSError,ValueError) as e:
        print(f'ERROR: {e}',file=sys.stderr);sys.exit(1)
