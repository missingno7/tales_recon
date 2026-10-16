"""WinUAE ORIGINAL-game observer. Private files and owned processes only.

Native debugger console supplies paused commands (IPC is starved while paused).
All guest writes below are emulator control/input events, never memory patches.
"""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
_HERE=Path(__file__).resolve();ROOT=next((p for p in _HERE.parents if (p/'docs'/'toolchain.json').is_file() and (p/'recovery'/'data_model.json').is_file()),_HERE.parents[1])
B=ROOT/'build'/'trace';sys.path.insert(0,str(ROOT/'tools'))
import ctypes as C
from ctypes import wintypes as W
import json,os,re,time,subprocess,hashlib,argparse,shutil
import trace_probe_console as con
import trace_probe_ipc as ipc
from ofs import OFSDisk
import hunk
k=ipc.k
u=C.WinDLL('user32',use_last_error=True)
u.VkKeyScanW.argtypes=[W.WCHAR];u.VkKeyScanW.restype=C.c_short


def digest(data):return hashlib.sha256(data).hexdigest()
def write_json(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')

def original():
 disk=OFSDisk((B/'disk1.adf').read_bytes());manifest=disk.parse()
 blob=disk.files['DuckTales'];model=hunk.parse(blob)
 write_json(B/'disk-observation.json',dict(volume=manifest['volume'],startup_sequences=manifest['startup_sequences'],files=list(disk.files),executable_sha256=digest(blob)))
 return blob,model

def signatures(blob,model):
 result={}
 for h in model['hunks']:
  if h['type']!='CODE':continue
  relocs=[(r['source_offset'],r['source_offset']+r['width']) for r in model['relocations'] if r['source_hunk']==h['number']]
  data=blob[h['content_offset']:h['content_offset']+h['initialized_size']]
  for off in range(0x100 if h['number']==0 else 0,len(data)-64,2):
   if not any(a<off+64 and b>off for a,b in relocs) and len(set(data[off:off+64]))>16:
    result[h['number']]=(off,data[off:off+64]);break
 return result

class Emulator:
 def __init__(self,name,state=None):
  assert re.fullmatch(r'[A-Za-z0-9_-]+',name),'invalid private run name'
  self.dir=B;assert self.dir.name==name,'run directory/name mismatch';self.p=None;self.hin=None;self.hout=None;self.log=[]
  self.state=state
 def start(self):
  pins=json.loads((self.dir/'inputs.json').read_text())
  assert digest(Path(pins['emulator']).read_bytes())==pins['emulator_sha256']
  assert digest((self.dir/'kick13.rom').read_bytes())==pins['rom_sha256']
  for disk in pins['disks']:
   assert digest(Path(disk['copy']).read_bytes())==disk['sha256']
  write_json(self.dir/'input-pins.json',pins)
  existing_pipes=set(os.listdir('\\\\.\\pipe\\'))
  cfg=(self.dir/'console.uae').read_text()+'\njoyport1=kbd1\n'
  if self.state:
   shutil.copyfile(self.state,self.dir/'replay.uss');cfg+='statefile_name=replay.uss\n'
  (self.dir/'session.uae').write_text(cfg)
  args=[str(Path(pins['emulator'])),'-portable','-datapath',str(self.dir),'-f',str(self.dir/'session.uae'),'-console','-log','-ini',str(self.dir/'winuae.ini')]
  si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
  env=os.environ.copy();env['TMP']=str(self.dir);env['TEMP']=str(self.dir)
  self.p=subprocess.Popen(args,cwd=self.dir,startupinfo=si,creationflags=subprocess.CREATE_NEW_CONSOLE,env=env)
  write_json(self.dir/'process.json',dict(pid=self.p.pid,args=args,config_sha256=digest(cfg.encode())))
  print('START',self.dir.name,self.p.pid,flush=True)
  end=time.monotonic()+15
  while time.monotonic()<end:
   if self.p.poll() is not None:raise RuntimeError('WinUAE exited '+str(self.p.returncode))
   k.FreeConsole()
   if k.AttachConsole(self.p.pid):
    self.hin=k.CreateFileW('CONIN$',0xc0000000,3,None,3,0,None)
    self.hout=k.CreateFileW('CONOUT$',0xc0000000,3,None,3,0,None)
    break
   time.sleep(.1)
  assert self.hout is not None,'console not allocated'
  self.pipe=None
  deadline=time.monotonic()+15
  while self.pipe is None and time.monotonic()<deadline:
   for n in os.listdir('\\\\.\\pipe\\'):
    if 'winuae' not in n.lower() or n in existing_pipes:continue
    try:
     h=ipc.open_pipe(n,self.p.pid);probe_reply=ipc.send(h,'CFG cpu_model');k.CloseHandle(h);self.pipe=n;self.log.append(dict(initial_query=probe_reply));break
    except Exception:pass
   if self.pipe is None:time.sleep(.1)
  assert self.pipe,'no owned IPC pipe'
  k.GetConsoleWindow.restype=W.HWND
  u.ShowWindow(k.GetConsoleWindow(),0)
  return self
 def reconnect_console(self):
  for h in [self.hin,self.hout]:
   if h is not None:k.CloseHandle(h)
  self.hin=self.hout=None;k.FreeConsole();end=time.monotonic()+15
  while time.monotonic()<end:
   if k.AttachConsole(self.p.pid):
    self.hin=k.CreateFileW('CONIN$',0xc0000000,3,None,3,0,None)
    self.hout=k.CreateFileW('CONOUT$',0xc0000000,3,None,3,0,None)
    u.ShowWindow(k.GetConsoleWindow(),0);return
   time.sleep(.05)
  raise RuntimeError('No replacement console')
 def remote(self,text):
  h=ipc.open_pipe(self.pipe,self.p.pid)
  try:result=ipc.send(h,text)
  finally:k.CloseHandle(h)
  self.log.append(dict(remote=text,result=result))
  return result
 def snap(self,rows=55):
  inf=con.INFO();assert k.GetConsoleScreenBufferInfo(self.hout,C.byref(inf)),C.get_last_error()
  y=max(0,inf.cursor.Y-rows);length=inf.size.X*(inf.cursor.Y-y)+inf.cursor.X
  buf=C.create_unicode_buffer(length+1);n=W.DWORD()
  assert k.ReadConsoleOutputCharacterW(self.hout,buf,length,con.COORD(0,y),C.byref(n)),C.get_last_error()
  text='\n'.join(buf.value[i:i+inf.size.X].rstrip() for i in range(0,len(buf.value),inf.size.X))
  return (inf.cursor.X,inf.cursor.Y),text
 def wait_prompt(self,before=None,timeout=10):
  end=time.monotonic()+timeout
  while time.monotonic()<end:
   pos,text=self.snap()
   if text.rstrip().endswith('>') and (before is None or (pos,text)!=before):return text
   if self.p.poll() is not None:raise RuntimeError('Emulator exited')
   time.sleep(.002)
  raise TimeoutError('No debugger prompt: '+text[-1600:])
 def enter(self):
  pos,_=self.snap();self.remote('EVT SPC_ENTERDEBUGGER 0');result=self.remote('EVT SPC_ENTERDEBUGGER 1')
  time.sleep(.1);self.reconnect_console();text=self.wait_prompt();self.log.append(dict(enter=result,console=text));return text
 def send_keys(self,text):
  records=[]
  for char in text+'\r':
   scan=u.VkKeyScanW(char)
   vk=13 if char=='\r' else scan&255
   ctrl=0x10 if scan&0x100 else 0
   for down in [True,False]:
    r=con.RECORD();r.type=1;r.event.key.down=down;r.event.key.repeat=1;r.event.key.vk=vk;r.event.key.char=char;r.event.key.ctrl=ctrl
    records.append(r)
  a=(con.RECORD*len(records))(*records);n=W.DWORD()
  assert k.WriteConsoleInputW(self.hin,a,len(a),C.byref(n)),C.get_last_error()
 def cmd(self,text,wait=True,timeout=10):
  pos,old_text=self.snap();start=time.perf_counter();self.send_keys(text)
  result=self.wait_prompt((pos,old_text),timeout) if wait else ''
  marker=result.rfind('>'+text)
  if marker>=0:result=result[marker:]
  self.log.append(dict(command=text,wall_seconds=time.perf_counter()-start,console=result[-6500:]))
  return result
 def dump(self,filename,address,size):
  path=self.dir/filename
  if path.exists():path.unlink()
  result=self.cmd('S '+filename+' '+format(address,'x')+' '+format(size,'x'))
  if not path.exists():raise RuntimeError('Dump failed: '+result[-1200:])
  data=path.read_bytes();assert len(data)==size,(path,len(data),size)
  return data
 def memory(self):return [(0,self.dump('chip.bin',0,0x80000)),(0xc00000,self.dump('slow.bin',0xc00000,0x80000))]
 def close(self):
  try:
   if self.hout is not None:(self.dir/'console-final.txt').write_text(self.snap(2000)[1],encoding='utf-8')
  finally:
   for h in [self.hin,self.hout]:
    if h is not None:k.CloseHandle(h)
   k.FreeConsole()
   if self.p is not None:
    actual=ipc.k.GetProcessId(self.p._handle)
    image=C.create_unicode_buffer(32768);length=W.DWORD(len(image))
    if not ipc.k.QueryFullProcessImageNameW(self.p._handle,0,image,C.byref(length)) or actual!=self.p.pid or Path(image.value).resolve()!=Path(self.p.args[0]).resolve():
     raise RuntimeError('refusing cleanup: WinUAE PID/image identity changed')
    if self.p.poll() is None:self.p.terminate()
    try:self.p.wait(timeout=5)
    except subprocess.TimeoutExpired:self.p.kill();self.p.wait()
    write_json(self.dir/'cleanup.json',dict(pid=self.p.pid,checked_pid=actual,exit=self.p.returncode,terminated=True))
   write_json(self.dir/'commands.json',self.log)

def read(mem,addr,n):
 for base,data in mem:
  if base<=addr and addr+n<=base+len(data):return data[addr-base:addr-base+n]
 raise ValueError(('unmapped',addr,n))
def u32(mem,addr):return int.from_bytes(read(mem,addr,4),'big')
def locate(mem,blob,model,sigs):
 found={}
 for num,(off,sig) in sigs.items():
  matches=[]
  for base,data in mem:
   pos=data.find(sig)
   while pos>=0:matches.append(base+pos-off);pos=data.find(sig,pos+1)
  if matches:found[num]=matches
 if 0 not in found:return dict(signatures=found,resident=None)
 assert len(found[0])==1,found
 code=found[0][0];bases={0:code};derivations=[]
 for target in [1,2]:
  rows=[r for r in model['relocations'] if r['source_hunk']==0 and r['target_hunk']==target]
  values={u32(mem,code+r['source_offset'])-r['addend_raw'] for r in rows}
  if len(values)==1:bases[target]=values.pop()
  derivations.append(dict(target=target,fields=len(rows),candidate_bases=sorted(values) if target not in bases else [bases[target]]))
 if 1 not in bases:return dict(signatures=found,resident=None,pending_relocations=derivations)
 next_bptr=u32(mem,bases[1]-4)
 if 2 not in bases:bases[2]=(next_bptr<<2)+4
 chain=[dict(hunk=i,base=b,allocation_header=u32(mem,b-8),next_bptr=u32(mem,b-4)) for i,b in bases.items()]
 assert ((u32(mem,code-4)<<2)+4)==bases[1],chain
 assert ((u32(mem,bases[1]-4)<<2)+4)==bases[2],chain
 return dict(signatures=found,resident=bases,relocation_derivations=derivations,segment_chain=chain)

