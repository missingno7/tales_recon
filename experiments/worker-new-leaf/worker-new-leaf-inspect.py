import json
from pathlib import Path
R=json.loads(Path('evidence/functions/ranking.json').read_text())['candidates']
by={x['id']:x for x in R}
D=json.loads(Path('evidence/functions/ledger.json').read_text())['functions']; fs={x['id']:x for x in D}
for fid in ['ov11_F_13DC','ov11_F_583A','ov11_F_4696','ov11_F_2430','ov11_F_247C','ov11_F_5EC0','ov11_F_5C42']:
 r=by.get(fid,{})
 print('\n###',fid,'rank',json.dumps(r))
 f=fs.get(fid)
 if not f:continue
 print('instruction list')
 for i in f['instructions']:print(i['offset'],i['mnemonic'],i['operands'])
