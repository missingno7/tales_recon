import json
from pathlib import Path
D=json.loads(Path('evidence/functions/ledger.json').read_text())['functions']
f=next(x for x in D if x['id']=='ov04_F_1E36')
print('function metadata',json.dumps({k:f[k] for k in ('id','hunk','start','end','size','extent_status','referenced_strings','direct_callees','referenced_data')},indent=2))
for x in f['instructions']:
 if 7720 <= x['offset'] <= 7790: print(x['offset'],x['mnemonic'],x['operands'])
