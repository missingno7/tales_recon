import json
from pathlib import Path
f=json.loads(Path('recovery/blockers/ov11_F_5FB2.json').read_text())['facts']
for i in f['instructions']: print(f"{i['offset']:05x} {i['mnemonic']:<12} {i['operands']:<34} {i['raw']}")
print('\nDATA')
for k in ('data','argument_accesses','calls','entry_evidence','cfg','stack_frames','relocations'):
 print(k,json.dumps(f.get(k),indent=2))
