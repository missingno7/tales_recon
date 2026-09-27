import json
from pathlib import Path
rank=json.loads(Path('evidence/functions/ranking.json').read_text())['candidates']
tried=set()
for p in Path('recovery/attempts').glob('*/*.json'):
 try: tried.add(json.loads(p.read_text()).get('id') or p.parent.name)
 except: tried.add(p.parent.name)
tried.update({'ov08_F_1AB8','ov08_F_1D42'})
rows=[]
for r in rank:
 if not r['node'].startswith('ov') or r['id'] in tried: continue
 if r.get('extent')!='CLOSED_CFG' or r.get('size',9999)>256: continue
 if (Path('src/recovered')/r['node']/(r['id']+'.c')).exists(): continue
 rows.append(r)
print('all untried closed<=256',len(rows))
for s in sorted({r.get('state') for r in rows}):
 z=[r for r in rows if r.get('state')==s]
 print('state',s,'count',len(z),'zero unknown',sum(r.get('unknown_calls')==0 for r in z),'empty local',sum(not r.get('pending_local_dependencies') for r in z))
for r in rows:
 if not r.get('unknown_calls') and not r.get('pending_local_dependencies'):
  print('GATE-CLEAR',r['id'],r['size'],r['state'],r['calls'],r['data_references'],r['pc_relative_data'],r['score'])
print('\nCandidate rows with 1 pending local target and <=1 unknown:')
for r in sorted([r for r in rows if len(r.get('pending_local_dependencies',[]))==1 and r.get('unknown_calls',99)<=1],key=lambda x:(x['size'],x['score'])):
 print(r['id'],r['size'],r['state'],'unknown',r['unknown_calls'],'calls',r['calls'],'data',r['data_references'],'pending',r['pending_local_dependencies'],'score',r['score'])
