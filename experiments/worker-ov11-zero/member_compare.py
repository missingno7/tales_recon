import copy,json,pathlib,sys
root=pathlib.Path.cwd();sys.path.insert(0,str(root/'tools'))
from check_unit import prepare_unit
from compiler_oracle import compile_many
from check_function import validated_function
from function_compare import compare_function
fid='ov11_F_3B92'; expected,_=validated_function(fid); receipt=next(p for p in (root/'recovery/units'/fid).rglob('receipt.json') if json.loads(p.read_text()).get('actual_length')==1052); base=(receipt.parent/'candidate.c').read_text(); needle='((unsigned char *)&event->value12)[1] + 0'
forms={'plus0':base,'intcast':base.replace(needle,'(int)((unsigned char *)&event->value12)[1]'),'uintcast':base.replace(needle,'(unsigned int)((unsigned char *)&event->value12)[1]'),'direct_v4':(root/'experiments/direct-recovery/ov11_F_3B92-v4.c').read_text()}
for name,source in forms.items():
 members,names,parts,combined,ledger=prepare_unit(fid,source,True,True,remove_stale_externs=False); trial=dict(source=combined,profile='aztec36',target_node=9,objects=[dict(source=parts[m['id']]) for m in members],local_functions=[names[m['id']] for m in members if m['id']!=fid]);compiled=compile_many([trial])[0]
 sym=next(s for s in compiled['contribution']['symbols'] if s['name']=='_'+names[fid]); start=sym['offset']; stop=next((s['offset'] for s in compiled['contribution']['symbols'] if s['hunk']==sym['hunk'] and s['offset']>start),compiled['contribution']['code_size']); piece=copy.deepcopy(compiled); c=piece['contribution']; raw=bytes.fromhex(c['code_hex']);c['code_hex']=raw[start:stop].hex();c['code_size']=stop-start;c['code_offset']=start;c['entry_offset']=0;c['relocations']=[dict(r,relative_offset=r['relative_offset']-start) for r in c['relocations'] if start<=r['relative_offset']<stop]
 report=compare_function(expected,piece,ledger['a4']['bias'],source_text=combined);print(name,json.dumps({k:report.get(k) for k in ('actual_length','verdict','reason','raw_first_difference','normalized_first_difference','first_structural_instruction_difference','relocation_issues','mnemonic_similarity')}))
