import json
from pathlib import Path
D=json.loads(Path('evidence/functions/ledger.json').read_text())['functions']
for fid in ['resident_F_8B88','resident_F_8B76','resident_F_8B4C','resident_F_8AA8','resident_F_8C10']:
 f=next(x for x in D if x['id']==fid)
 ins=f['instructions']
 print(fid,'start',hex(f['start']),'bytes',f['size'])
 for x in ins: print(' ',hex(x['offset']),x['mnemonic'],x['operands'])
