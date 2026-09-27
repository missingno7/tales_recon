import json,pathlib,sys
root=pathlib.Path.cwd();out=root/'experiments/worker-ov11-zero';sys.path.insert(0,str(root/'tools'))
from check_unit import prepare_unit,gap_partitioned_objects,compare_unit
from compiler_oracle import compile_many
from function_compare import decode_all,basic
fid='ov11_F_3B92';rp=next(p for p in (root/'recovery/units'/fid).rglob('receipt.json') if json.loads(p.read_text()).get('actual_length')==1052);base=(rp.parent/'candidate.c').read_text()
# Nest both the count/switch block and the work-field updates in the value4==1 block.
source=base.replace('\n        }\n        if (event->count1c > 0','\n        if (event->count1c > 0',1)
source=source.replace('\n        event->work18 = screen_y;\n    }\n}','\n        event->work18 = screen_y;\n        }\n    }\n}',1)
if source==base: raise SystemExit('nested guard transformation did not apply')
(out/'nested_outer_guard_and_updates.c').write_text(source,encoding='ascii')
members,names,parts,combined,ledger=prepare_unit(fid,source,True,True,remove_stale_externs=False);objects=gap_partitioned_objects(members,names,parts)
trial=dict(source=combined,profile='aztec36',target_node=9,objects=objects,local_functions=[names[m['id']] for m in members if m['id']!=fid]);c=compile_many([trial])[0];report=compare_unit(members,names,c,ledger['a4']['bias'],allow_gaps=True,source_text=combined)
target=next((m for m in report.get('members',[]) if m['id']==fid),{});syms=c.get('contribution',{}).get('symbols',[])
result=dict(compiler_status=c.get('status'),unit_code_bytes=c.get('contribution',{}).get('code_size'),unit_verdict=report.get('verdict'),unit_reason=report.get('reason'),target_verdict=target.get('verdict'),target_reason=target.get('reason'),target_normalized_first=target.get('normalized_first_difference'),target_raw_first=target.get('raw_first_difference'),target_shape_diff=target.get('first_structural_instruction_difference'),member_verdicts=[dict(id=m['id'],verdict=m['verdict'],reason=m.get('reason')) for m in report.get('members',[])],cache_key=c.get('cache_key'))
if c.get('status')=='COMPILED':
 start=next(s['offset'] for s in syms if s['name']=='_recovered');stop=next(s['offset'] for s in syms if s['name']=='_F_h11_40E0');raw=bytes.fromhex(c['contribution']['code_hex'])[start:stop];ins,_=decode_all(raw);result['branch_at_82']=next(basic(i) for i in ins if i.address==82)
(out/'nested-guard-and-updates-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
