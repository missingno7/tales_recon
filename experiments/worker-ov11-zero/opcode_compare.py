import json,pathlib,sys
root=pathlib.Path.cwd();sys.path.insert(0,str(root/'tools'))
from check_unit import prepare_unit
from compiler_oracle import compile_many
fid='ov11_F_3B92'; p=next(p for p in (root/'recovery/units'/fid).rglob('receipt.json') if json.loads(p.read_text()).get('actual_length')==1052); base=(p.parent/'candidate.c').read_text()
needle='((unsigned char *)&event->value12)[1] + 0'
forms={'plus0':base,'intcast':base.replace(needle,'(int)((unsigned char *)&event->value12)[1]'),'uintcast':base.replace(needle,'(unsigned int)((unsigned char *)&event->value12)[1]'),'directv4':(root/'experiments/direct-recovery/ov11_F_3B92-v4.c').read_text()}
for name,src in forms.items():
 members,names,parts,combined,ledger=prepare_unit(fid,src,True,True,remove_stale_externs=False)
 trial=dict(source=combined,profile='aztec36',target_node=9,objects=[dict(source=parts[m['id']]) for m in members],local_functions=[names[m['id']] for m in members if m['id']!=fid])
 c=compile_many([trial])[0]; code=bytes.fromhex(c['contribution']['code_hex']); pos=next(sum(m['size'] for m in members[:i]) for i,m in enumerate(members) if m['id']==fid)
 target=code[pos:]
 print(name,'unit',len(code),'target_start',pos,'target_size',len(target)-sum(m['size'] for m in members[members.index(next(m for m in members if m['id']==fid))+1:]),'moveq',[i for i in range(len(target)-1) if target[i:i+2]==b'\x70\0'],'move.l.zero',[i for i in range(len(target)-5) if target[i:i+6]==bytes.fromhex('203c00000000')],'windows',target[282:300].hex(),target[346:364].hex())
