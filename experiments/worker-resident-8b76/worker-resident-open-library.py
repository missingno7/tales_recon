import json
from pathlib import Path
D=json.loads(Path('evidence/functions/ledger.json').read_text())['functions']
for f in D:
 for c in f.get('direct_callees',[]):
  if c['id']=='resident_F_89D0':
   ix=next((i for i,x in enumerate(f['instructions']) if x['offset']==c['site']),None)
   print('\n',f['id'],'site',c['site'])
   if ix is not None:
    for x in f['instructions'][max(0,ix-10):ix+3]:print(x['offset'],x['mnemonic'],x['operands'])
