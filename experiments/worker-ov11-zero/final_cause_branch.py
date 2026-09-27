import json,pathlib,re,sys
root=pathlib.Path.cwd();out=root/'experiments/worker-ov11-zero';sys.path.insert(0,str(root/'tools'))
from compiler_oracle import compile_many
from function_compare import decode_all,basic
ids=['ov11_F_25D6','ov11_F_25F8','ov11_F_37A0','ov11_F_3B92','ov11_F_40E0','ov11_F_4696']
closest=next(p for p in (root/'recovery/units'/'ov11_F_3B92').rglob('receipt.json') if json.loads(p.read_text()).get('actual_length')==1052)
sources={fid:re.sub(r'\brecovered\b','F_h11_'+fid[-4:],(root/'src/recovered/ov11'/(fid+'.c')).read_text()) for fid in ids if fid!='ov11_F_3B92'}
sources['ov11_F_3B92']=(closest.parent/'candidate.c').read_text()
separate=[dict(source=sources[f]) for f in ids]
joined=sources['ov11_F_25D6']+'\n'+sources['ov11_F_25F8'];joined=re.sub(r'\bextern\s+(?:int|long|short|char|void)\s+F_h11_25D6\s*\(\s*\)\s*;','',joined)
joined_objects=[dict(source=joined)]+[dict(source=sources[f]) for f in ids[2:]]
all_source='\n'.join(sources[f] for f in ids);local=['F_h11_'+f[-4:] for f in ids if f!='ov11_F_3B92']
ledger=json.loads((root/'evidence/functions/ledger.json').read_text());f8=next(x for x in ledger['functions'] if x['id']=='ov11_F_25F8');target=next(x for x in ledger['functions'] if x['id']=='ov11_F_3B92')
expected_f8=bytes.fromhex(f8['raw_bytes']);expected_target=bytes.fromhex(target['raw_bytes']);ei,_=decode_all(expected_f8);eti,_=decode_all(expected_target)
records=[]
for mode,objects in [('separate',separate),('joined',joined_objects)]:
 c=compile_many([dict(source=all_source,profile='aztec36',target_node=9,objects=objects,local_functions=local)])[0];syms=c['contribution']['symbols'];start=next(s['offset'] for s in syms if s['name']=='_F_h11_25F8');stop=next(s['offset'] for s in syms if s['name']=='_F_h11_37A0');f8raw=bytes.fromhex(c['contribution']['code_hex'])[start:stop];fi,_=decode_all(f8raw)
 tstart=next(s['offset'] for s in syms if s['name']=='_recovered');tstop=next((s['offset'] for s in syms if s['hunk']==1 and s['offset']>tstart),c['contribution']['code_size']);traw=bytes.fromhex(c['contribution']['code_hex'])[tstart:tstop];ti,_=decode_all(traw)
 branch_expected=next(basic(i) for i in eti if i.address==82);branch_actual=next(basic(i) for i in ti if i.address==82)
 records.append(dict(mode=mode,code_bytes=c['contribution']['code_size'],f25f8_span=dict(start=start,end=stop,size=len(f8raw),hex=f8raw.hex(),instructions=[basic(i) for i in fi]),f3b92=dict(start=tstart,size=len(traw),branch_at_82=branch_actual,moveq_zero=[i.address for i in ti if i.mnemonic=='moveq' and i.op_str.strip()=='#$0, d0'])))
results={'f25f8_expected':dict(size=len(expected_f8),hex=expected_f8.hex(),instructions=[basic(i) for i in ei]),'f3b92_expected_branch_at_82':branch_expected,'records':records}
(out/'final-cause-and-branch.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
