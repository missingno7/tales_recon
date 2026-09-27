import json
from pathlib import Path
p=Path('evidence/functions/ledger.json')
d=json.loads(p.read_text())
for fid in ['resident_F_8B76','ov08_F_1D42']:
 f=next(x for x in d['functions'] if x['id']==fid)
 print('\n###',fid, 'node',f['node'],'hunk',f['hunk'],'start',f['start'],'size',f['size'],'state',f['extent_status'])
 print('calls',json.dumps(f['direct_callees'],indent=2))
 print('data',json.dumps(f['referenced_data'],indent=2))
 for i in f['instructions']:
  print(i['offset'],i['mnemonic'],i['operands'])
