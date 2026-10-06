"""Replay a diagnostic complete runtime variant; never grants acceptance."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from common import require,sha256
from analysis_support import game,signed16
from overlay_experiment import symbols,contribution
from resident_object import code_size
from hunk import parse
from recovery_state import facts
r=json.loads((ROOT/'evidence/experiments/resident-exit-variant.json').read_text())
receipts=json.loads((Path(__file__).parent/'receipts.json').read_text())
for kind in ('compile','link'):
 for item in receipts[kind]['pinned_inputs']:
  require(sha256((ROOT/item['path']).read_bytes())==item['sha256'],'pinned compiler input changed')
for item in receipts['compile']['source_files']:
 if item['path'] in ('exit.c','root.c'):
  require(sha256((Path(__file__).parent/item['path']).read_bytes())==item['sha256'],'compiled source changed')
for item in receipts['link']['source_files']:
 if item['path'] in ('exit.o','root.o'):
  require(sha256((Path(__file__).parent/item['path']).read_bytes())==item['sha256'],'relinked object changed')
for a in r['artifacts']:
 require(sha256((ROOT/a['path']).read_bytes())==a['sha256'],'retained artifact changed')
p=Path(__file__).parent
b=(p/'exit-control.exe').read_bytes(); m=parse(b)
s=symbols((p/'exit-control.sym').read_text()); start=s[(0,'__exit')]
size=code_size(p/'exit.o'); require(size==238,'whole object extent changed')
c=contribution(b,m,0,start,size); original,om,_=game()
require(sha256(original)==r['game_sha256'],'oracle identity changed')
o=contribution(original,om,0,34130,238)
mask=set(); ins={i['offset']-34130:i for i in facts('resident_F_8552')['instructions']}
for f in r['field_correspondences']:
 site=f['site']; pos=f['field']; require(pos==site+2,'unexpected field coordinate')
 i=ins[site]
 if f['kind']=='A4_GLOBAL_CORRESPONDENCE':
  require('(a4)' in i['operands'] and o[site:site+2]==c[site:site+2],'A4 opcode mismatch')
  av=signed16(int.from_bytes(c[pos:pos+2],'big'))+32766
  ov=signed16(int.from_bytes(o[pos:pos+2],'big'))+32766
  names=[k[1] for k,v in s.items() if k[0] in (1,2) and v==av]
  require(names==f['names'] and av==f['candidate_offset'] and ov==f['original_offset'],'A4 correspondence changed')
 else:
  require(f['kind']=='PC_CALLEE_CORRESPONDENCE' and i['mnemonic']=='jsr' and '(pc)' in i['operands'],'unexpected projected field')
  require(o[site:site+2]==c[site:site+2]==bytes.fromhex('4eba'),'PC opcode mismatch')
  av=start+pos+signed16(int.from_bytes(c[pos:pos+2],'big'))
  ov=34130+pos+signed16(int.from_bytes(o[pos:pos+2],'big'))
  require(s[(0,f['name'])]==av==f['candidate_offset'] and ov==f['original_offset'],'PC correspondence changed')
 require(not mask.intersection(range(pos,pos+2)),'field overlap')
 mask.update(range(pos,pos+2))
require(len(mask)==58 and all(a==b for i,(a,b) in enumerate(zip(o,c)) if i not in mask),'ordinary bytes mismatch')
require(o[148:154]==c[148:154] and o[232:238]==c[232:238],'thunk or epilogue mismatch')
print('PASS: whole238-byte diagnostic variant;180 ordinary bytes equal;58 address bytes remain unaccepted')
