"""Checkpoint and per-frame original-game trace, with explicit binary schema."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
_HERE=Path(__file__).resolve()
ROOT=next((p for p in _HERE.parents if (p/'docs'/'toolchain.json').is_file() and (p/'recovery'/'data_model.json').is_file()),_HERE.parents[1])
sys.path.insert(0,str(ROOT/'tools'))
import trace_harness as H
import trace_decoder as D
import json,re,time,argparse,statistics,collections,hashlib,shutil,os
B=ROOT/'build'/'trace'
FRAME_BYTES=46048
TraceError=RuntimeError
def decode_value(raw,typ,structs):return D.value(raw,typ,structs)
def select_root(path):
 global B
 B=Path(path).resolve();B.mkdir(parents=True,exist_ok=True);H.B=B;D.B=B
def runtime_config(path=None):
 p=Path(path) if path else ROOT/'docs'/'toolchain.json'
 if not p.is_absolute():p=ROOT/p
 cfg=json.loads(p.read_text(encoding='utf-8')).get('game_trace')
 if not isinstance(cfg,dict):raise RuntimeError('toolchain.json has no game_trace entry')
 return cfg
def resolve_path(value):
 p=Path(value);return p if p.is_absolute() else ROOT/p
def build_path(value):
 p=Path(value);p=p if p.is_absolute() else ROOT/p;p=p.resolve()
 if not p.is_relative_to((ROOT/'build').resolve()):raise ValueError('checkpoint paths must stay under build/')
 return p
def output_root(path=None):
 root=Path(path).resolve() if path else (ROOT/'build'/'trace').resolve()
 if not root.is_relative_to((ROOT/'build').resolve()):raise ValueError('output root must stay under build/')
 return root
def run_path(root,name):
 if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9_-]+',name):raise ValueError('run name must contain only letters, digits, _ or -')
 root=Path(root).resolve();candidate=root/name
 if candidate.is_symlink():raise ValueError('run directory must not be a symlink')
 resolved=candidate.resolve()
 if resolved.parent!=root:raise ValueError('run directory must be a direct child of its output root')
 return resolved
def stage_run(run,cfg,floppy_speed=100):
 if run.exists():
  if any(run.iterdir()):raise FileExistsError('run directory already contains files')
 else:run.mkdir(parents=True,exist_ok=False)
 emulator=resolve_path(cfg['emulator']['path']);rom_source=resolve_path(cfg['rom']['path'])
 pins={'emulator':str(emulator),'emulator_sha256':cfg['emulator']['sha256'],'rom_sha256':cfg['rom']['sha256'],'disks':[]}
 if floppy_speed!=100:pins['floppy_speed']=floppy_speed
 for i,disc in enumerate(cfg['disks'],1):
  source=resolve_path(disc['source']);target=run/f'disk{i}.adf';shutil.copyfile(source,target)
  if hashlib.sha256(target.read_bytes()).hexdigest()!=disc['sha256']:raise RuntimeError(f'disk {i} checksum mismatch')
  os.chmod(target,0o444);pins['disks'].append({'copy':str(target.resolve()),'sha256':disc['sha256']})
 rom=run/'kick13.rom';shutil.copyfile(rom_source,rom)
 if hashlib.sha256(rom.read_bytes()).hexdigest()!=cfg['rom']['sha256']:raise RuntimeError('ROM checksum mismatch')
 profile=f'''config_description=private trace A500 PAL\nuse_gui=no\nkickstart_rom_file={rom}\ncpu_model=68000\ncpu_speed=real\ncpu_compatible=true\ncpu_24bit_addressing=true\ncpu_cycle_exact=true\ncpu_memory_cycle_exact=true\nblitter_cycle_exact=true\nchipset=ocs\nchipmem_size=1\nbogomem_size=2\nfastmem_size=0\nntsc=false\ncachesize=0\nsound_output=interrupts\nfloppy0={run/'disk1.adf'}\nfloppy1={run/'disk2.adf'}\nfloppy0wp=true\nfloppy1wp=true\nfloppy0type=0\nfloppy1type=0\nnr_floppies=2\nfloppy_speed={floppy_speed}\nfloppy_write_protect=true\nheadless=true\ngfx_api=directdraw\ngfx_fullscreen_amiga=false\ngfx_width_windowed=640\ngfx_height_windowed=512\ngfx_framerate=1\nwin32.start_minimized=yes\nwin32.inactive_pause=false\nwin32.minimized_pause=false\nwin32.inactive_input=0\nwin32.minimized_input=0\nwin32.rom_path={run}\nwin32.floppy_path={run}\nwin32.savestate_path={run}\nwin32.screenshot_path={run}\nrtc=none\n'''
 # Screenshots need rendering: TALES_TRACE_RENDER=1 drops headless; gfx_api
 # stays directdraw (GDI, CPU only), so the GPU is still not used.
 if os.environ.get('TALES_TRACE_RENDER')=='1':profile=profile.replace('headless=true\n','')
 (run/'console.uae').write_text(profile,encoding='utf-8',newline='\n');(run/'inputs.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8');(run/'winuae.ini').write_text('',encoding='utf-8')


def cpu(text):
 text=text[text.rfind('VPOS:'):]
 regs={k:int(v,16) for k,v in re.findall(r'\b([AD][0-7]|USP|ISP)\s+([0-9a-fA-F]{8})',text)}
 pcs=re.findall(r'(?m)^([0-9a-fA-F]{8})\s+[0-9a-fA-F]{4}\s',text)
 if not pcs:raise RuntimeError('No CPU state: '+text[-1000:])
 beam=re.search(r'VPOS:\s*(\d+).*HPOS:\s*(\d+)',text)
 return dict(pc=int(pcs[-1],16),regs=regs,vpos=int(beam[1]),hpos=int(beam[2]))

def frame(e):
 if getattr(e,'vblank_hook',None) is not None:
  # Break at the game-installed IT V Blank server, before its first instruction.
  if getattr(e,'at_vblank',False):e.cmd('t')
  before=e.snap();e.cmd('g',wait=False);e.reconnect_console()
  result=e.wait_prompt(before=before,timeout=5);state=cpu(result)
  assert state['pc']==e.vblank_hook,('wrong VBlank PC',state,e.vblank_hook)
  cia=e.cmd('c');tod=re.search(r'TOD ([0-9A-Fa-f]{6})',cia);cycles=re.search(r'CYC=([0-9A-Fa-f]+)',cia)
  assert tod and cycles,cia
  state['cia_a_tod']=int(tod[1],16);state['cycle_clock']=int(cycles[1],16)
  if getattr(e,'last_tod',None) is not None:
   delta=(state['cia_a_tod']-e.last_tod)&0xffffff
   assert delta==1,('not one VBlank per sample',delta,state,e.last_tod)
   state['chip_cycles']=(state['cycle_clock']-e.last_cycle_clock)//512
  else:state['chip_cycles']=None
  e.last_tod=state['cia_a_tod'];e.last_cycle_clock=state['cycle_clock'];e.at_vblank=True
  return state
 a=e.cmd('fs 1');b=e.cmd('fs 0 0')
 state=cpu(b)
 cycles=[]
 for text in [a,b]:
  found=re.findall(r'Cycles:\s*(\d+) Chip',text)
  cycles.append(int(found[-1]) if found else None)
 state['chip_cycles']=sum(cycles) if None not in cycles else None
 assert state['vpos']==0,state
 return state

def prepare(name):
 blob,model=H.original();e=H.Emulator(name)
 try:
  e.start();time.sleep(45);e.enter();mem=e.memory();mapping=H.locate(mem,blob,model,H.signatures(blob,model))
  assert mapping['resident'],mapping
  H.write_json(e.dir/'mapping.json',mapping)
  state=frame(e);sync_state=state
  e.cmd('I evt SPC_SCREENSHOT 1');e.cmd('I evt SPC_SCREENSHOT 0')
  e.cmd('I evt SPC_STATESAVE 1');state=frame(e);e.cmd('I evt SPC_STATESAVE 0')
  candidates=list(e.dir.rglob('*.uss'));print('QUICKSAVES',candidates,flush=True)
  assert len(candidates)==1,candidates
  path=candidates[0]
  info=dict(checkpoint=str(path),checkpoint_sha256=H.digest(path.read_bytes()),sync_pc=sync_state['pc'],mapping=mapping,cpu=state,sync_selection_cpu=sync_state)
  H.write_json(e.dir/'prepared.json',info);H.write_json(B/'checkpoint.json',info)
  print('PREPARED',info,flush=True)
  # Verify a held fire event reaches a game poll; checkpoint predates this test.
  e.cmd('I evt JOY2_FIRE_BUTTON 1')
  for _ in range(12):frame(e)
  e.cmd('I evt JOY2_FIRE_BUTTON 0');e.cmd('I evt SPC_SCREENSHOT 1');frame(e)
 finally:e.close()


def make_schema(data_path=None,names_path=None):
 # Always rederive from current data-model and semantic-name evidence.
 fixture_mode=data_path is not None or names_path is not None
 data_path=Path(data_path) if data_path else H.ROOT/'recovery'/'data_model.json'
 names_path=Path(names_path) if names_path else H.ROOT/'recovery'/'names.json'
 data=json.loads(data_path.read_text());names=json.loads(names_path.read_text())
 rows=[]
 for name,entry in data['globals'].items():
  m=re.fullmatch(r'G_h(\d+)_([0-9a-fA-F]+)',name)
  if not m or int(m[1]) not in [1,2]:continue
  hunk=int(m[1]);offset=int(m[2],16);extent=entry.get('extent')
  if not isinstance(extent,int):continue
  limit=46044 if hunk==1 else 4
  assert 0<=offset and offset+extent<=limit,(name,entry)
  semantic=names.get('globals',{}).get(name,{})
  rows.append(dict(id=name,name=semantic.get('name'),hunk=hunk,offset=offset,frame_offset=offset+(46044 if hunk==2 else 0),extent=extent,type=entry['type'],basis=entry.get('basis')))
 schema=dict(version=1,endianness='big',int_bits=16,long_bits=32,pointer_bits=32,float='Amiga FFP; kept raw',frame_bytes=46048,regions=[dict(hunk=1,frame_offset=0,extent=46044,initialized=11956,zero_fill=34088),dict(hunk=2,frame_offset=46044,extent=4,initialized=0,zero_fill=4)],globals=rows,structs=data.get('structs',{}),raw_policy='All region bytes retained, including typed overlaps and untyped spans. No inferred raw object bounds.')
 if not fixture_mode:H.write_json(B/'trace-schema.json',schema)
 return schema

def decode(raw,row):
 t=' '.join(row['type'].split());n=row['extent'];b=raw[row['frame_offset']:row['frame_offset']+n]
 if '*' in t:return dict(raw=b.hex(),address=int.from_bytes(b,'big')) if n==4 else dict(raw=b.hex())
 signed='unsigned' not in t
 if t in ['char','signed char','unsigned char','int','short','short int','unsigned int','unsigned short','long','long int','unsigned long','unsigned long int'] and n in [1,2,4]:return int.from_bytes(b,'big',signed=signed)
 arr=re.fullmatch(r'(unsigned )?(char|short|int|long)\s*\[(\d+)\]',t)
 if arr:
  size={'char':1,'short':2,'int':2,'long':4}[arr[2]];count=int(arr[3])
  if size*count==n:return [int.from_bytes(b[i:i+size],'big',signed=not bool(arr[1])) for i in range(0,n,size)]
 return dict(raw=b.hex())

def overlays(data,tree):
 found={}
 for slot in tree['slots']:
  bases=[]
  for sym in slot['symbols']:
   off=sym['trampoline_offset'];entry=data[off:off+8]
   if entry[:2]==bytes.fromhex('4ef9'):bases.append(int.from_bytes(entry[2:6],'big')-sym['target_offset'])
  if bases:
   assert len(set(bases))==1,(slot,bases)
   number=slot['symbols'][0]['target_hunk'];found[number]=bases[0]
 return found

def classify(pc,bases,model):
 for h in model['hunks']:
  n=h['number']
  if n in bases and bases[n]<=pc<bases[n]+h['allocated_size']:return n
 return None

def irq_abi():
 # Re-derive this pinned ROM's stack layout from decoded instructions.
 sys.path.insert(0,str(H.ROOT/'toolchain/installed/host-python/Lib/site-packages'))
 import capstone
 rom=(B/'kick13.rom').read_bytes();pins=json.loads((B/'inputs.json').read_text())
 assert H.digest(rom)==pins['rom_sha256']
 md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
 required={0xfc0d14:('movem.l','d0-d1/a0-a1/a5-a6, -(a7)'),0xfc0d50:('pea.l','-$24(a6)'),0xfc1338:('move.w','$12(a1), -(a7)'),0xfc133c:('move.l','a2, -(a7)'),0xfc134a:('jsr','(a5)')}
 instructions=[]
 for address,wanted in required.items():
  ins=next(md.disasm(rom[address-0xfc0000:address-0xfc0000+12],address,count=1))
  assert (ins.mnemonic,ins.op_str)==wanted,(address,ins.mnemonic,ins.op_str)
  instructions.append(dict(address=address,mnemonic=ins.mnemonic,operands=ins.op_str,size=ins.size))
 # MOVEM saves six long registers. PEA, server-mask word, A2 and JSR add 14 bytes.
 extra=4+2+4+4;saved=6*4
 result=dict(rom_sha256=H.digest(rom),instructions=instructions,return_pc=0xfc134c,saved_a5_offset=extra+4*4,saved_sr_offset=extra+saved,saved_pc_offset=extra+saved+2,extent=extra+saved+6)
 H.write_json(B/'irq-abi.json',result);return result

def caller_context(e,pc,a5,bases,model):
 direct=classify(pc,bases,model)
 if direct is not None and direct>=3:return dict(overlay=direct,basis='PC',pc_hunk=direct,frames=[])
 chain=[]
 if not 0xc00000<=a5<0xc7fff8:return dict(overlay=None,basis='UNRESOLVED_A5',pc_hunk=direct,frames=[])
 start=a5&~0xfff;size=min(0x6000,0xc80000-start)
 stack=e.dump('stack.bin',start,size);seen=set()
 for _ in range(40):
  if a5 in seen or not start<=a5<=start+len(stack)-8 or a5&1:break
  seen.add(a5);off=a5-start;previous=int.from_bytes(stack[off:off+4],'big');ret=int.from_bytes(stack[off+4:off+8],'big')
  n=classify(ret-2,bases,model);chain.append(dict(a5=a5,return_pc=ret,hunk=n))
  if n is not None and n>=3:return dict(overlay=n,basis='A5_RETURN',pc_hunk=direct,frames=chain)
  if previous<=a5:break
  a5=previous
 return dict(overlay=None,basis='UNRESOLVED_CALLER',pc_hunk=direct,frames=chain)

def context(e,state,bases,model):
 if getattr(e,'vblank_hook',None)==state['pc']:
  abi=e.irq_abi;sp=state['regs']['A7'];assert 0xc00000<=sp and sp+abi['extent']<=0xc80000
  raw=e.dump('irq-stack.bin',sp,abi['extent'])
  def get(offset,n):return int.from_bytes(raw[offset:offset+n],'big')
  assert get(0,4)==abi['return_pc'],('ROM dispatcher return mismatch',raw.hex())
  sr=get(abi['saved_sr_offset'],2);assert sr&~0xa71f==0,sr
  pc=get(abi['saved_pc_offset'],4);a5=get(abi['saved_a5_offset'],4)
  assert pc&1==0 and pc<0x1000000,pc
  result=caller_context(e,pc,a5,bases,model)
  result['basis']='IRQ_'+result['basis']
  result['interrupted']=dict(pc=pc,a5=a5,sr=sr,irq_sp=sp,raw_stack=raw.hex())
  return result
 return caller_context(e,state['pc'],state['regs'].get('A5',0),bases,model)

def default_input():
 events=[]
 for f in [30,200,350,500,700,900]:events.extend([dict(frame=f,event='JOY2_FIRE_BUTTON',value=1),dict(frame=f+5,event='JOY2_FIRE_BUTTON',value=0)])
 events += [dict(frame=550,event='JOY2_RIGHT',value=1),dict(frame=590,event='JOY2_RIGHT',value=0),dict(frame=750,event='JOY2_DOWN',value=1),dict(frame=780,event='JOY2_DOWN',value=0)]
 return sorted(events,key=lambda r:r['frame'])

def trace(name,count=1000,input_path=None):
 info=json.loads((B/'checkpoint.json').read_text());checkpoint=build_path(info['checkpoint']);info['checkpoint']=str(checkpoint);assert H.digest(checkpoint.read_bytes())==info['checkpoint_sha256']
 blob,model=H.original();tree=H.hunk.manx_overlay(model,blob);schema=make_schema()
 events=json.loads(Path(input_path).read_text()) if input_path else default_input()
 e=H.Emulator(name,state=checkpoint)
 try:
  e.start();time.sleep(2);e.enter()
  # The breakpoint aligns fresh restores; it does not patch guest memory.
  sync=info['sync_pc'];e.cmd('f '+format(sync,'x'))
  reply=e.cmd('I evt SPC_STATERESTORE 1');print('RESTORE REQUEST',reply[-700:],flush=True)
  e.cmd('g',wait=False);time.sleep(.3);e.reconnect_console();restored=e.wait_prompt(timeout=5)
  restore_log=e.snap(2000)[1];(e.dir/'restore-console.txt').write_text(restore_log,encoding='utf-8')
  if 'State restored' not in restore_log: raise RuntimeError('restore failed')
  assert H.digest((e.dir/'replay.uss').read_bytes())==info['checkpoint_sha256']
  print('RESTORE STOP',restored[-1700:],flush=True)
  assert cpu(restored)['pc']==sync,('not synchronized',cpu(restored),sync)
  e.cmd('f '+format(sync,'x'))
  state=frame(e)
  mem=e.memory();mapping=H.locate(mem,blob,model,H.signatures(blob,model));assert mapping['resident']
  bases={int(k):v for k,v in mapping['resident'].items()}
  ti=e.cmd('Ti');(e.dir/'interrupt-servers.txt').write_text(ti)
  hook=re.search(r'\(C=([0-9a-fA-F]+) D=[0-9a-fA-F]+\) \'IT V Blank\'',ti)
  assert hook,'game VBlank server absent'
  e.irq_abi=irq_abi();e.vblank_hook=int(hook[1],16)
  assert bases[0]<=e.vblank_hook<bases[0]+model['hunks'][0]['allocated_size']
  e.cmd('f '+format(e.vblank_hook,'x'))
  print('VBLANK HOOK',hex(e.vblank_hook),'resident offset',hex(e.vblank_hook-bases[0]),flush=True)
  state=frame(e)
  H.write_json(e.dir/'sampling.json',dict(kind='GAME_VBLANK_SERVER_ENTRY',server_name='IT V Blank',pc=e.vblank_hook,resident_offset=e.vblank_hook-bases[0],basis='Live Exec interrupt-server list; breakpoint before first instruction; CIA-A TOD advances exactly one per sample',initial_cpu=state))
  H.write_json(e.dir/'mapping.json',mapping);H.write_json(e.dir/'input.json',events)
  H.write_json(e.dir/'trace-meta.json',dict(frame_bytes=46048,count=count,checkpoint_sha256=info['checkpoint_sha256'],input_sha256=H.digest(json.dumps(events,sort_keys=True).encode()),schema_sha256=H.digest((B/'trace-schema.json').read_bytes()),comparison='All resident bytes, exact; overlay context separately; timing costs excluded'))
  by_frame=collections.defaultdict(list)
  for event in events:by_frame[event['frame']].append(event)
  costs=[];began=time.perf_counter()
  with open(e.dir/'trace.bin','wb') as binary,open(e.dir/'index.jsonl','w') as index,open(e.dir/'named.jsonl','w') as named:
   for f in range(count):
    begin=time.perf_counter()
    for event in by_frame[f]:e.cmd('I evt '+event['event']+' '+str(event['value']))
    if f%200==0 or f==count-1:
     e.cmd('I evt SPC_SCREENSHOT 1');e.cmd('I evt SPC_SCREENSHOT 0')
    state=frame(e)
    raw=e.dump('data.bin',bases[1],46044)+e.dump('bss.bin',bases[2],4)
    loaded=overlays(raw,tree);all_bases=dict(bases,**{})
    all_bases.update(loaded);ctx=context(e,state,all_bases,model)
    binary.write(raw)
    values={r.get('name') or r['id']:decode(raw,r) for r in schema['globals'] if r.get('name')}
    named.write(json.dumps(dict(frame=f,values=values),separators=(',',':'))+'\n')
    row=dict(frame=f,offset=f*46048,sha256=H.digest(raw),overlay=ctx['overlay'],overlay_basis=ctx['basis'],loaded=loaded,pc=state['pc'],beam=[state['vpos'],state['hpos']],chip_cycles=state['chip_cycles'],cia_a_tod=state['cia_a_tod'],cycle_clock=state['cycle_clock'],callers=ctx.get('frames',[]),interrupted=ctx.get('interrupted'))
    cost=time.perf_counter()-begin;costs.append(cost)
    index.write(json.dumps(row,separators=(',',':'))+'\n')
    if f%100==0:print('FRAME',f,'overlay',ctx['overlay'],'PC',hex(state['pc']),'wall',round(cost,4),flush=True)
  elapsed=time.perf_counter()-began
  H.write_json(e.dir/'cost.json',dict(frames=count,total_seconds=elapsed,mean_seconds=statistics.mean(costs),median_seconds=statistics.median(costs),max_seconds=max(costs),bytes_per_frame=46048,trace_sha256=H.digest((e.dir/'trace.bin').read_bytes())))
  print('TRACE COMPLETE',name,count,elapsed,flush=True)
 finally:e.close()


def compare(left,right):
 a=run_path(B,left);b=run_path(B,right);schema=json.loads((a/'trace-schema.json').read_text());meta_a=json.loads((a/'trace-meta.json').read_text());meta_b=json.loads((b/'trace-meta.json').read_text())
 assert meta_a==meta_b,('trace metadata differs',meta_a,meta_b)
 ia=[json.loads(l) for l in (a/'index.jsonl').read_text().splitlines()];ib=[json.loads(l) for l in (b/'index.jsonl').read_text().splitlines()]
 result=dict(left=left,right=right,frames_a=len(ia),frames_b=len(ib),bytes_per_frame=46048,identical=False,first_divergence=None)
 with open(a/'trace.bin','rb') as fa,open(b/'trace.bin','rb') as fb:
  for f,(ra,rb) in enumerate(zip(ia,ib)):
   va=fa.read(46048);vb=fb.read(46048)
   if va!=vb:
    off=next(i for i,(x,y) in enumerate(zip(va,vb)) if x!=y)
    covering=[r for r in schema['globals'] if r['frame_offset']<=off<r['frame_offset']+r['extent']]
    result['first_divergence']=dict(frame=f,frame_offset=off,hunk=1 if off<46044 else 2,hunk_offset=off if off<46044 else off-46044,a=va[off],b=vb[off],globals=covering);break
   # Execution/boundary checks are distinct from resident-byte identity.
   fields=['overlay','overlay_basis','loaded','pc','beam','chip_cycles','cia_a_tod','cycle_clock','callers','interrupted']
   if any(ra[k]!=rb[k] for k in fields):
    result['first_divergence']=dict(frame=f,kind='context',a={k:ra[k] for k in fields},b={k:rb[k] for k in fields});break
  else:result['identical']=len(ia)==len(ib)==meta_a['count'] and (a/'trace.bin').stat().st_size==(b/'trace.bin').stat().st_size==meta_a['count']*46048
 result['files']={name:dict(a_sha256=H.digest((a/name).read_bytes()),b_sha256=H.digest((b/name).read_bytes()),identical=(a/name).read_bytes()==(b/name).read_bytes()) for name in ['trace.bin','index.jsonl','named.jsonl']}
 result['identical']=result['identical'] and all(row['identical'] for row in result['files'].values())
 H.write_json(a/('comparison-'+right+'.json'),result)
 return result

def validate_input(events,frames):
 if not isinstance(events,list):raise ValueError('input must be a JSON event array')
 allowed={'JOY2_FIRE_BUTTON','JOY2_RIGHT','JOY2_LEFT','JOY2_UP','JOY2_DOWN'};out=[];previous=-1
 for i,row in enumerate(events):
  if not isinstance(row,dict) or set(row)!={'frame','event','value'}:raise ValueError(f'event {i} must have frame,event,value')
  f,event,value=row['frame'],row['event'],row['value']
  if not isinstance(f,int) or isinstance(f,bool) or not 0<=f<frames:raise ValueError(f'event {i} frame outside [0,{frames})')
  if f<previous:raise ValueError('events must be sorted by frame')
  if event not in allowed:raise ValueError(f'unsupported joystick event {event!r}')
  if value not in (0,1) or isinstance(value,bool):raise ValueError('event value must be integer 0 or 1')
  out.append({'frame':f,'event':event,'value':value});previous=f
 return out

def cli():
 ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='action',required=True)
 q=sub.add_parser('prepare');q.add_argument('run');q.add_argument('--output-root',type=Path);q.add_argument('--toolchain',type=Path)
 q=sub.add_parser('trace');q.add_argument('run');q.add_argument('--frames',type=int,required=True);q.add_argument('--input',type=Path,required=True);q.add_argument('--checkpoint',type=Path,required=True);q.add_argument('--output-root',type=Path);q.add_argument('--toolchain',type=Path)
 q=sub.add_parser('compare');q.add_argument('left');q.add_argument('right');q.add_argument('--output-root',type=Path)
 q=sub.add_parser('decode');q.add_argument('run');q.add_argument('frame',type=int);q.add_argument('--all',action='store_true');q.add_argument('--output-root',type=Path)
 a=ap.parse_args()
 try:
  if a.action in ('prepare','trace'):
   root=output_root(a.output_root);select_root(run_path(root,a.run));cfg=runtime_config(a.toolchain);stage_run(B,cfg)
   if a.action=='prepare':prepare(a.run)
   else:
    if a.frames<=0:raise ValueError('frames must be positive')
    events=validate_input(json.loads(a.input.read_text(encoding='utf-8')),a.frames);input_copy=B/'input.json';input_copy.write_text(json.dumps(events,indent=2)+'\n',encoding='utf-8')
    info=json.loads(build_path(a.checkpoint).read_text(encoding='utf-8'));info['checkpoint']=str(build_path(info['checkpoint']));H.write_json(B/'checkpoint.json',info);trace(a.run,a.frames,input_copy)
  elif a.action=='compare':
   select_root(output_root(a.output_root));result=compare(a.left,a.right);print(json.dumps(result,indent=2));return 0 if result['identical'] else 1
  else:
   run=run_path(output_root(a.output_root),a.run);select_root(run);old=json.loads((run/'trace-schema.json').read_text());fresh=make_schema()
   if old!=fresh:raise ValueError('current data model differs from captured schema')
   print(json.dumps(D.decode('.',a.frame,a.all),indent=2))
  return 0
 except Exception as exc:
  print('game_trace:',exc,file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(cli())
