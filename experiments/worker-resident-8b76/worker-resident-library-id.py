import json
from pathlib import Path
D=json.loads(Path('evidence/executable/strings.json').read_text())
for x in D.get('candidates',[]):
 if 'graphics.library' in x.get('text',''):
  print(json.dumps(x,indent=2))
for p in ['evidence/executable/hunks.json','docs/symbols.json']:
 d=json.loads(Path(p).read_text());print('\n',p)
 if 'symbols' in d:
  for x in d['symbols']:
   if x.get('hunk')==1 and x.get('offset') in [21360,21364,21368,21372]:print(json.dumps(x))
