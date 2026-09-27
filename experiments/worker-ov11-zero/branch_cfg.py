import json,pathlib,sys
root=pathlib.Path.cwd();sys.path.insert(0,str(root/'tools'))
from check_unit import prepare_unit,gap_partitioned_objects,compare_unit
from compiler_oracle import compile_many
from function_compare import decode_all,basic
fid='ov11_F_3B92'; receipt=next(p for p in (root/'recovery/units'/fid).rglob('receipt.json') if json.loads(p.read_text()).get('actual_length')==1052); source=(receipt.parent/'candidate.c').read_text(); members,names,parts,combined,ledger=prepare_unit(fid,source,True,True,remove_stale_externs=False)
objects=gap_partitioned_objects(members,names,parts); trial=dict(source=combined,profile='aztec36',target_node=9,objects=objects,local_functions=[names[m['id']] for m in members if m['id']!=fid]); c=compile_many([trial])[0]; report=compare_unit(members,names,c,ledger['a4']['bias'],allow_gaps=True,source_text=combined)
syms=c['contribution']['symbols']; st=next(s['offset'] for s in syms if s['name']=='_recovered'); stop=next(s['offset'] for s in syms if s['name']=='_F_h11_40E0'); actual=bytes.fromhex(c['contribution']['code_hex'])[st:stop]
ev=json.loads((root/'evidence/functions/ledger.json').read_text()); f=next(x for x in ev['functions'] if x['id']==fid); expected=bytes.fromhex(f['raw_bytes']); ei,_=decode_all(expected); ai,_=decode_all(actual)
for label,items in [('oracle',ei),('candidate',ai)]:
 print(label)
 for i in items:
  if 66<=i.address<=112 or 224<=i.address<=264 or 488<=i.address<=514:
   print(basic(i))
print('unit',report['verdict'],report['reason'],'target',next(m for m in report['members'] if m['id']==fid)['normalized_first_difference'])
