import json
from pathlib import Path
p=Path('evidence/functions/ledger.json')
d=json.loads(p.read_text())
f=next(x for x in d['functions'] if x['id']=='ov08_F_1D42')
print('keys',sorted(f))
for k in ['id','node','hunk','start','end','size','extent_status','direct_callees','referenced_data','relocations','return_sites','branch_targets','stack_frames']:
 print('\n###',k)
 print(json.dumps(f.get(k),indent=2)[:12000])
print('\n### instructions')
for x in f['instructions']:
 print(json.dumps({k:x.get(k) for k in ('offset','size','mnemonic','operands','text','flow','target')}, separators=(',',':')))
