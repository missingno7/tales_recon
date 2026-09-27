import json
from pathlib import Path
p=Path('evidence/experiments/runtime-arithmetic.json')
print('runtime evidence exists',p.exists())
if p.exists():
 d=json.loads(p.read_text());print(json.dumps(d,indent=2)[:6000])
