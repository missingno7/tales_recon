import json,pathlib,re,sys,hashlib
root=pathlib.Path.cwd();sys.path.insert(0,str(root/'tools'))
from compiler_oracle import compile_many
from function_compare import decode_all,basic
out=root/'experiments/worker-ov11-zero'
ids=['ov11_F_25D6','ov11_F_25F8','ov11_F_37A0','ov11_F_3B92','ov11_F_40E0','ov11_F_4696']
sources={fid:re.sub(r'\brecovered\b','F_h11_'+fid[-4:],(root/'src/recovered/ov11'/(fid+'.c')).read_text()) for fid in ids if fid!='ov11_F_3B92'}
sources['ov11_F_3B92']=re.sub(r'\brecovered\b','recovered',(next((root/'recovery/units'/'ov11_F_3B92').rglob('candidate.c'))).read_text())
objects_sep=[dict(source=sources[f]) for f in ids]
joined=sources['ov11_F_25D6']+'\n'+sources['ov11_F_25F8']
joined=re.sub(r'\bextern\s+(?:int|long|short|char|void)\s+F_h11_25D6\s*\(\s*\)\s*;','',joined)
objects_join=[dict(source=joined)]+[dict(source=sources[f]) for f in ids[2:]]
allsource='\n'.join(sources[f] for f in ids)
local=['F_h11_'+fid[-4:] for fid in ids if fid!='ov11_F_3B92']
records=[]
for mode,objects in [('separate',objects_sep),('joined',objects_join)]:
 c=compile_many([dict(source=allsource,profile='aztec36',target_node=9,objects=objects,local_functions=local)])[0]
 syms=c['contribution']['symbols']; fn='_F_h11_25F8'; st=next(s['offset'] for s in syms if s['name']==fn);en=next(s['offset'] for s in syms if s['name']=='_F_h11_37A0');raw=bytes.fromhex(c['contribution']['code_hex'])[st:en];ins,bad=decode_all(raw);records.append(dict(mode=mode,code_bytes=c['contribution']['code_size'],f25f8_start=st,f25f8_end=en,size=len(raw),hex=raw.hex(),instructions=[basic(x) for x in ins],decode_error=bad,cache_key=c.get('cache_key')))
ev=json.loads((root/'evidence/functions/ledger.json').read_text());f=next(x for x in ev['functions'] if x['id']=='ov11_F_25F8');expected=bytes.fromhex(f['raw_bytes']);ei,_=decode_all(expected)
results=dict(expected=dict(size=len(expected),hex=expected.hex(),instructions=[basic(x) for x in ei]),actual=records)
(out/'f25f8-span.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'expected':results['expected'],'separate':records[0],'joined':records[1]}))
