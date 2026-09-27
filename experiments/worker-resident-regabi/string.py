import json
from pathlib import Path
D=json.loads(Path('evidence/executable/strings.json').read_text())
for x in D['candidates']:
 if 'mathffp' in x.get('text','').lower() or 'no math library' in x.get('text','').lower(): print(x)
