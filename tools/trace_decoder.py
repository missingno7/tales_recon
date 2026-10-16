"""Decode a frame using the pinned schema; raw bytes always remain available."""
from pathlib import Path
import argparse,hashlib,json,math,re,sys
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent

def clean(t):return ' '.join(t.replace('const ','').replace('volatile ','').split())
def array(t):
 m=re.fullmatch(r'(.+?)\s*((?:\[\d+\]\s*)+)',t)
 return (m[1].strip(),[int(n) for n in re.findall(r'\[(\d+)\]',m[2])]) if m else None

def size(t,records):
 t=clean(t);a=array(t)
 if a:
  n=size(a[0],records);return None if n is None else n*math.prod(a[1])
 if '*' in t:return 4
 if t in ['char','signed char','unsigned char']:return 1
 if t in ['int','signed int','unsigned int','short','short int','signed short','unsigned short','unsigned short int']:return 2
 if t in ['long','long int','signed long','unsigned long','unsigned long int','float']:return 4
 return records.get(t.removeprefix('struct '),{}).get('size')

def value(raw,t,records,depth=0):
 t=clean(t);out=dict(raw=raw.hex());width=size(t,records)
 if width is None or width!=len(raw) or depth>12:return dict(out,decode='RAW_UNSUPPORTED_OR_UNBOUNDED')
 a=array(t)
 if a:
  base,dims=a;elem=base+''.join('[%d]'%n for n in dims[1:]);stride=size(elem,records)
  out['value']=[value(raw[i*stride:(i+1)*stride],elem,records,depth+1) for i in range(dims[0])]
 elif '*' in t:out.update(address=int.from_bytes(raw,'big'),decode='RAW_AMIGA_ADDRESS_NOT_DEREFERENCED')
 elif t=='float':
  bits=int.from_bytes(raw,'big');mant=bits>>8;exp=bits&127;out['format']='AMIGA_FFP'
  if not bits:out['value']=0.0
  elif mant>=0x800000 and exp:out['value']=math.ldexp(mant/2**24,exp-64)*(-1 if bits&128 else 1)
  else:out['decode']='RAW_NONCANONICAL_FFP'
 elif t.removeprefix('struct ') in records:
  fields={}
  for f in records[t.removeprefix('struct ')].get('fields',[]):
   off=f['offset'];n=size(f['type'],records)
   fields[f['name']]=value(raw[off:off+n],f['type'],records,depth+1) if n is not None and off>=0 and off+n<=len(raw) else dict(decode='UNRESOLVED',type=f['type'],offset=off)
  out['fields']=fields
 else:out['value']=int.from_bytes(raw,'big',signed='unsigned' not in t)
 return out

def decode(run,frame,all_globals=False):
 run=(B/run).resolve();assert run.is_relative_to(B) and frame>=0
 schema=json.loads((B/'trace-schema.json').read_text());extent=schema['frame_bytes'];length=(run/'trace.bin').stat().st_size
 assert length%extent==0 and (frame+1)*extent<=length
 with (run/'trace.bin').open('rb') as stream:stream.seek(frame*extent);raw=stream.read(extent)
 with (run/'index.jsonl').open() as stream:row=next(json.loads(line) for n,line in enumerate(stream) if n==frame)
 assert hashlib.sha256(raw).hexdigest()==row['sha256']
 fields={};covered=bytearray(extent)
 for f in schema['globals']:
  off=f['frame_offset'];n=f['extent'];assert 0<=off and off+n<=extent
  covered[off:off+n]=b'\1'*n
  if all_globals or f.get('name'):fields[f['id']]=dict(name=f.get('name'),type=f['type'],basis=f.get('basis'),hunk=f['hunk'],offset=f['offset'],**value(raw[off:off+n],f['type'],schema['structs']))
 out=dict(frame=frame,overlay=row['overlay'],overlay_basis=row['overlay_basis'],globals=fields)
 if all_globals:
  spans=[]
  for region in schema['regions']:
   begin=region['frame_offset'];end=begin+region['extent'];pos=begin
   while pos<end:
    if covered[pos]:pos+=1;continue
    stop=pos+1
    while stop<end and not covered[stop]:stop+=1
    spans.append(dict(hunk=region['hunk'],offset=pos-begin,raw=raw[pos:stop].hex()));pos=stop
  out.update(untyped_spans=spans,untyped_policy='Coverage complement only; not object boundaries')
 return out

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('run');ap.add_argument('frame',type=int);ap.add_argument('--all',action='store_true');a=ap.parse_args();print(json.dumps(decode(a.run,a.frame,a.all),indent=2))
