import json
from pathlib import Path
D=json.loads(Path('evidence/fingerprints/index.json').read_text())
for e in D.get('entries',[]):
 s=e.get('source','')
 if 'float' in s.lower() or 'double' in s.lower():
  print('\nsource:',s.strip()[:300]);print('profile:',e.get('compiler',{}).get('profile'));print(e.get('assembly','')[:1800])
