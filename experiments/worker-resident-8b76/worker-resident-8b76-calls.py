import json
from pathlib import Path
D=json.loads(Path('evidence/functions/ledger.json').read_text())['functions']
for f in D:
 calls=[c for c in f.get('direct_callees',[]) if c['id']=='resident_F_8B76']
 if calls:
  print('\nCALLER',f['id'],'node',f['node'],'n',len(calls))
  for c in calls:
   site=c['site']
   ix=next(i for i,x in enumerate(f['instructions']) if x['offset']==site)
   print('callsite',site)
   for x in f['instructions'][max(0,ix-7):ix+3]: print(' ',x['offset'],x['mnemonic'],x['operands'])
