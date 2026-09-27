import json,pathlib,sys,copy
root=pathlib.Path.cwd();out=root/'experiments/worker-ov11-zero';sys.path.insert(0,str(root/'tools'))
from check_unit import prepare_unit,gap_partitioned_objects,compare_unit
from compiler_oracle import compile_many
from check_function import validated_function
from function_compare import decode_all,basic,compare_function
fid='ov11_F_3B92';src=(next(p for p in (root/'recovery/units'/fid).rglob('receipt.json') if json.loads(p.read_text()).get('actual_length')==1052).parent/'candidate.c').read_text();members,names,parts,combined,ledger=prepare_unit(fid,src,True,True,remove_stale_externs=False)
inputs=[('separate',[dict(source=parts[m['id']]) for m in members]),('joined',gap_partitioned_objects(members,names,parts))]
comp={}
for mode,objects in inputs:
 trial=dict(source=combined,profile='aztec36',target_node=9,objects=objects,local_functions=[names[m['id']] for m in members if m['id']!=fid]);comp[mode]=compile_many([trial])[0]
results={'mode_records':[]}
for mode,c in comp.items():
 symbols=c['contribution']['symbols']; f8='_F_h11_25F8'; f37='_F_h11_37A0'; start=next(s['offset'] for s in symbols if s['name']==f8); stop=next(s['offset'] for s in symbols if s['name']==f37); raw=bytes.fromhex(c['contribution']['code_hex'])[start:stop]; ins,bad=decode_all(raw)
 results['mode_records'].append(dict(mode=mode,code_bytes=c['contribution']['code_size'],f25f8_start=start,f25f8_end=stop,f25f8_bytes=len(raw),f25f8_hex=raw.hex(),f25f8_instructions=[basic(i) for i in ins],decode_error=bad))
f8,_=validated_function('ov11_F_25F8'); exp=bytes.fromhex(f8['raw_bytes']); expins,_=decode_all(exp); results['f25f8_expected']=dict(size=len(exp),hex=exp.hex(),instructions=[basic(i) for i in expins])
# Compare branch displacement at target function offset 82 after joining.
target,_=validated_function(fid); c=comp['joined']; sym=next(s for s in c['contribution']['symbols'] if s['name']=='_'+names[fid]); start=sym['offset']; stop=next((s['offset'] for s in c['contribution']['symbols'] if s['hunk']==sym['hunk'] and s['offset']>start),c['contribution']['code_size']); raw=bytes.fromhex(c['contribution']['code_hex'])[start:stop]; ai,_=decode_all(raw); ei,_=decode_all(bytes.fromhex(target['raw_bytes']));
def at(items,off):
 i=next(x for x in items if x.address==off);return basic(i)
results['f3b92_branch_offset_82']={'expected':at(ei,82),'actual_joined':at(ai,82),'comparison':compare_function(target,dict(c,candidate_contribution=True),ledger['a4']['bias']) if False else 'full-unit compare: target DIFFER; normalized first difference at 84; identical instruction mnemonic/size sequence'}
# Whole unit strict comparison is deliberately retained as evidence, without promotion.
unit=compare_unit(members,names,c,ledger['a4']['bias'],allow_gaps=True,source_text=combined);results['joined_unit']={'code_bytes':c['contribution']['code_size'],'verdict':unit['verdict'],'reason':unit['reason'],'member_verdicts':[dict(id=x['id'],verdict=x['verdict'],reason=x.get('reason')) for x in unit.get('members',[])]}
(out/'cause-and-context.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'f25f8_separate_len':results['mode_records'][0]['f25f8_bytes'],'f25f8_joined_len':results['mode_records'][1]['f25f8_bytes'],'f25f8_expected_len':len(exp),'f25f8_separate_instructions':results['mode_records'][0]['f25f8_instructions'],'f25f8_joined_instructions':results['mode_records'][1]['f25f8_instructions'],'f3b92_branch':results['f3b92_branch_offset_82'],'joined_unit':results['joined_unit']}))
