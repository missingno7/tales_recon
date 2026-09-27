import json
from pathlib import Path
D=json.loads(Path('evidence/functions/ledger.json').read_text())['functions']
for f in D:
 if any(x.get('offset') in (9514,9562) for x in f.get('referenced_strings',[])):
  print('\nSTRING FUNCTION',f['id'],f['hunk'],f['start'],f['size'],f.get('referenced_strings'))
  for i in f['instructions']:
   if i['offset'] in (f['start'],) or i['mnemonic'].startswith(('jsr','bsr')) or '5374' in i['operands'] or '5378' in i['operands']:
    print(i['offset'],i['mnemonic'],i['operands'])
for f in D:
 refs=[r for r in f.get('referenced_data',[]) if r.get('hunk')==1 and r.get('offset') in (21364,21368)]
 if refs:
  print('\nGLOBALS',f['id'],f['hunk'],f['start'],f['size'],refs)
  for r in refs:
   ix=next((j for j,i in enumerate(f['instructions']) if i['offset']==r['instruction_offset']),None)
   if ix is not None:
    for i in f['instructions'][max(0,ix-2):ix+3]: print(i['offset'],i['mnemonic'],i['operands'])
