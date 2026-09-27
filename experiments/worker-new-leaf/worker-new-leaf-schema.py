import json
from pathlib import Path
for p in ['evidence/functions/ranking.json','evidence/functions/ledger.json','recovery/ledger.json']:
 d=json.loads(Path(p).read_text())
 print('\nFILE',p,'keys',list(d)[:20])
 if p.endswith('ranking.json'):
  print('counts',len(d.get('ranked',[])),len(d.get('candidates',[])))
  rows=d.get('ranked',d.get('candidates',[]))
  for x in rows[:2]: print(json.dumps(x,indent=2)[:3000])
