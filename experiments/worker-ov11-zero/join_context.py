import copy,json,pathlib,sys
root=pathlib.Path.cwd();out=root/'experiments/worker-ov11-zero';sys.path.insert(0,str(root/'tools'))
from check_unit import prepare_unit,compare_unit,gap_partitioned_objects
from compiler_oracle import compile_many
from check_function import validated_function
from function_compare import compare_function
fid='ov11_F_3B92'; target,_=validated_function(fid);rpath=next(p for p in (root/'recovery/units'/fid).rglob('receipt.json') if json.loads(p.read_text()).get('actual_length')==1052);src=(rpath.parent/'candidate.c').read_text();members,names,parts,combined,ledger=prepare_unit(fid,src,True,True,remove_stale_externs=False)
for mode,objects in [('separate',[dict(source=parts[m['id']]) for m in members]),('joined_adjacent',gap_partitioned_objects(members,names,parts))]:
 trial=dict(source=combined,profile='aztec36',target_node=9,objects=objects,local_functions=[names[m['id']] for m in members if m['id']!=fid]);c=compile_many([trial])[0];unit=compare_unit(members,names,c,ledger['a4']['bias'],allow_gaps=True,source_text=combined)
 sym=next(s for s in c['contribution']['symbols'] if s['name']=='_'+names[fid]);start=sym['offset'];stop=next((s['offset'] for s in c['contribution']['symbols'] if s['hunk']==sym['hunk'] and s['offset']>start),c['contribution']['code_size']);piece=copy.deepcopy(c);co=piece['contribution'];raw=bytes.fromhex(co['code_hex']);co['code_hex']=raw[start:stop].hex();co['code_size']=stop-start;co['code_offset']=start;co['entry_offset']=0;co['relocations']=[dict(x,relative_offset=x['relative_offset']-start) for x in co['relocations'] if start<=x['relative_offset']<stop]
 cr=compare_function(target,piece,ledger['a4']['bias'],source_text=combined)
 result=dict(mode=mode,code_bytes=c['contribution']['code_size'],members=[(m['name'],m['offset']) for m in c['contribution']['symbols'] if m['name'] in ['_F_h11_25D6','_F_h11_25F8','_F_h11_37A0','_F_h11_3B92']],unit_verdict=unit['verdict'],unit_reason=unit['reason'],member_verdicts=[(m['id'],m['verdict'],m.get('reason')) for m in unit.get('members',[])],target_len=cr.get('actual_length'),target_norm_first=cr.get('normalized_first_difference'),target_shape_diff=cr.get('first_structural_instruction_difference'))
 print(json.dumps(result))
(out/'join_context.json').write_text(json.dumps(result,indent=2)+'\n')
