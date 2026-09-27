import json,pathlib,sys
root=pathlib.Path.cwd(); out=root/'experiments/worker-ov11-zero'; sys.path.insert(0,str(root/'tools'))
from check_unit import prepare_unit, compare_unit
from compiler_oracle import compile_many
fid='ov11_F_3B92'
receipt=next(p for p in (root/'recovery/units'/fid).rglob('receipt.json') if json.loads(p.read_text()).get('actual_length')==1052)
base=(receipt.parent/'candidate.c').read_text()
needle='((unsigned char *)&event->value12)[1] + 0'
variants={'plus_zero':base,'int_cast':base.replace(needle,'(int)((unsigned char *)&event->value12)[1]'),'unsigned_int_cast':base.replace(needle,'(unsigned int)((unsigned char *)&event->value12)[1]')}
results=[]
for name,source in variants.items():
    (out/(name+'_unit_target.c')).write_text(source,encoding='ascii')
    members,names,parts,combined,ledger=prepare_unit(fid,source,True,True,remove_stale_externs=False)
    trial=dict(source=combined,profile='aztec36',target_node=9,objects=[dict(source=parts[m['id']]) for m in members],local_functions=[names[m['id']] for m in members if m['id']!=fid])
    compiled=compile_many([trial])[0]
    report=compare_unit(members,names,compiled,ledger['a4']['bias'],allow_gaps=True,source_text=combined)
    target=next((m for m in report.get('members',[]) if m['id']==fid),{})
    result=dict(hypothesis=name,combined_source_sha256=__import__('hashlib').sha256(combined.encode()).hexdigest(),compiler_status=compiled['status'],cache_key=compiled.get('cache_key'),code_bytes=compiled.get('contribution',{}).get('code_size'),unit_verdict=report.get('verdict'),reason=report.get('reason'),expected_length=report.get('expected_length'),actual_length=report.get('actual_length'),target_verdict=target.get('verdict'),target_reason=target.get('reason'),target_first=target.get('normalized_first_difference') or target.get('raw_first_difference'),members=[dict(id=m['id'],verdict=m['verdict'],reason=m.get('reason'),actual_length=m.get('actual_length')) for m in report.get('members',[])])
    results.append(result)
(out/'compact-unit-results.json').write_text(json.dumps(results,indent=2)+'\n')
for r in results: print(json.dumps(r))
