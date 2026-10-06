"""Replay complete mixed-source evidence without granting promotion."""
import sys,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from common import require,sha256
from analysis_support import game,signed16
from hunk import parse
from overlay_experiment import symbols,contribution
from resident_object import code_size
from recovery_state import evidence
from recovery_evidence import load_promotions
from library_a4 import load_library_a4
r=json.loads((ROOT/'evidence/experiments/resident-exit-mechanical.json').read_text())
l=json.loads((ROOT/'evidence/experiments/resident-exit-message-leaves.json').read_text())
for doc in (r,l):
 for item in doc['retained_inputs']:
  require(sha256((ROOT/item['path']).read_bytes())==item['sha256'],'retained artifact changed')
blob,model,_=game();a=evidence();ledger=json.loads((ROOT/'recovery/ledger.json').read_text())
prom=load_promotions(ROOT,blob,model,a)
rows=load_library_a4(ROOT,blob,model,a,prom,ledger)
require(any(x['id']=='runtime_closelib_unit' for x in rows),'known base unit not accepted')
require(sha256(blob)==l['game_sha256'],'oracle identity changed')
require(sha256((ROOT/l['known_base_basis']['document']).read_bytes())==l['known_base_basis']['document_sha256'],'base evidence stale')
lib=(ROOT/l['library']['path']).read_bytes()
require(sha256(lib)==l['library']['sha256'],'library changed')
for item in l['objects']:
 p=ROOT/'evidence/rules/resident-exit-message-leaves';name=item['member'];n=item['code_bytes'];field=item['base_field'];variants=[]
 obj=(p/(name+'.o')).read_bytes();assembled=(p/(name+'-source.o')).read_bytes()
 require(lib.count(obj)==1 and code_size(p/(name+'.o'))==code_size(p/(name+'-source.o'))==n,'whole leaf object differs')
 require(obj[14:22]==assembled[14:22]==bytes(8),'leaf owns storage')
 for ctrl in item['controls']:
  b=(ROOT/ctrl['executable']).read_bytes();m=parse(b);s=symbols((ROOT/ctrl['symbols']).read_text());h=next(h for h in m['hunks'] if h['number']==0)
  require(h['initialized_size']==h['allocated_size']==n and not m['relocations'],'leaf clipped or relocations added')
  c=contribution(b,m,0,s[(0,item['symbol'])],n)
  require(c[field-2:field]==bytes.fromhex('2c6c'),'base opcode changed')
  require(signed16(int.from_bytes(c[field:field+2],'big'))+a['a4']['bias']==s[(1,'_SysBase')]==ctrl['base_offset'],'leaf base binding differs')
  variants.append(c[:field]+bytes(2)+c[field+2:])
 require(len(set(variants))==1,'source/library controls differ')
 offset=item['original_base']['offset'];needle=variants[0][:field]+(offset-a['a4']['bias']).to_bytes(2,'big',signed=True)+variants[0][field+2:];matches=[]
 for h in model['hunks']:
  if h['type']!='CODE':continue
  raw=blob[h['content_offset']:h['content_offset']+h['initialized_size']];pos=0
  while True:
   off=raw.find(needle,pos)
   if off<0:break
   pos=off+1
   if not off%2 and not any(x['source_hunk']==h['number'] and x['source_offset']<off+n and x['source_offset']+x['width']>off for x in model['relocations']):matches.append(dict(hunk=h['number'],offset=off))
 require(matches==item['unique_original_matches'] and len(matches)==1,'original callee match not unique')
p=Path(__file__).parent
for key in ('accepted_inbound_basis','positive_access_view_basis'):
 basis=r[key];require(sha256((ROOT/basis['proof']).read_bytes())==basis['proof_sha256'],'canonical basis stale')
 require(any(x['id']==basis['id'] for x in prom),'basis not canonical')
require(sha256((ROOT/r['sdk_variant']['path']).read_bytes())==r['sdk_variant']['sha256'],'SDK variant stale')
blocks=lambda t:re.findall(r'^#asm\n(.*?)^#endasm',t,re.M|re.S)
old=blocks((ROOT/r['sdk_variant']['path']).read_text());new=blocks((p/'candidate.c').read_text())
require(len(old)==len(new)==2 and new==[x.replace('__savsp#','_G_h01_B39E#') for x in old],'SDK assembly changed')
b=(p/'candidate.exe').read_bytes();m=parse(b);s=symbols((p/'candidate.sym').read_text());start=s[(0,'_recovered')];n=code_size(p/'candidate.o');require(n==238,'source object extent changed')
c=contribution(b,m,0,start,n);o=contribution(blob,model,0,34130,238);mask=set()
for f in r['mechanical_field_bindings']:
 pos=f['field'];site=f['site'];require(pos==site+2 and c[site:pos]==o[site:pos],'field opcode differs')
 if f['original_hunk']==1:
  actual=signed16(int.from_bytes(c[pos:pos+2],'big'))+a['a4']['bias'];original=signed16(int.from_bytes(o[pos:pos+2],'big'))+a['a4']['bias']
  require(f['symbol']=='_G_h01_%04X'%original and any(k[1]==f['symbol'] and k[0] in (1,2) and v==actual for k,v in s.items()),'mechanical global identity changed')
 else:
  require(c[site:pos]==bytes.fromhex('4eba'),'callee opcode differs')
  actual=start+pos+signed16(int.from_bytes(c[pos:pos+2],'big'));original=34130+pos+signed16(int.from_bytes(o[pos:pos+2],'big'))
  require(f['symbol']=='_F_h00_%04X'%original and s[(0,f['symbol'])]==actual,'mechanical callee identity changed')
 require(actual==f['actual_offset'] and original==f['original_offset'] and not mask.intersection(range(pos,pos+2)),'field correspondence changed')
 mask.update(range(pos,pos+2))
require(len(mask)==58 and len(r['mechanical_field_bindings'])==29 and all(x==y for i,(x,y) in enumerate(zip(o,c)) if i not in mask),'complete object bytes differ')
part=json.loads((ROOT/'evidence/experiments/resident-exit-partition.json').read_text())
for item in part['retained_inputs']:
 require(sha256((ROOT/item['path']).read_bytes())==item['sha256'],'partition artifact changed')
mp=ROOT/'evidence/rules/resident-exit-partition';mb=(mp/'candidate.exe').read_bytes();mm=parse(mb);ms=symbols((mp/'candidate.sym').read_text());mstart=ms[(0,'_recovered')]
require(code_size(mp/'candidate.o')==238 and contribution(mb,mm,0,mstart,238)==c,'marker control changes CODE')
for key,value in s.items():
 if key[1].startswith(('_F_h00_','_G_h01_')):require(ms[key]==value,'marker control changes binding')
spans=[]
for index in range(2):
 lo=ms[(0,'_runtime_asm_begin%d'%index)]-mstart;hi=ms[(0,'_runtime_asm_end%d'%index)]-mstart
 spans.append((lo,hi))
require(spans==[(x['start'],x['end']) for x in part['partitions'] if x['language']=='ASM'],'source marker partition differs')
require(sum(hi-lo for lo,hi in spans)==42 and part['c_compiler_bytes']==196,'language byte totals differ')
require(sum(x['size'] for x in part['partitions'])==238,'partition is not complete')
print('PASS: independent message leaves; complete mixed source238;29 identities;196 C+42 ASM. EXPERIMENT ONLY.')
