import json,pathlib,sys
root=pathlib.Path.cwd();sys.path.insert(0,str(root/'tools'))
from check_unit import prepare_unit
from compiler_oracle import compile_many
fid='ov11_F_3B92';p=next(p for p in (root/'recovery/units'/fid).rglob('receipt.json') if json.loads(p.read_text()).get('actual_length')==1052);src=(p.parent/'candidate.c').read_text();members,names,parts,combined,ledger=prepare_unit(fid,src,True,True,remove_stale_externs=False)
trial=dict(source=combined,profile='aztec36',target_node=9,objects=[dict(source=parts[m['id']]) for m in members],local_functions=[names[m['id']] for m in members if m['id']!=fid]);c=compile_many([trial])[0]
for m in members:
 name='_'+names[m['id']]; sym=next((s for s in c['contribution']['symbols'] if s['name']==name),None);print(m['id'],'expected',m['size'],'actual_start',sym and sym['offset'])
print('code size',c['contribution']['code_size'])
