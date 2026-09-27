import json, pathlib, sys
root=pathlib.Path.cwd(); out=root/'experiments/worker-ov11-zero'
ledger=json.loads((root/'evidence/functions/ledger.json').read_text())
f=next(x for x in ledger['functions'] if x['id']=='ov11_F_3B92')
b=bytes.fromhex(f['raw_bytes'])
for p in (282,346): print('oracle-window',p,b[p:p+20].hex())
sys.path.insert(0,str(root/'tools'))
from compiler_oracle import compile_many
base=(root/'experiments/direct-recovery/ov11_F_3B92-v4.c').read_text()
variants={'baseline':base,
'cast_uint':base.replace('= event->valueD;', '= (unsigned int)event->valueD;'),
'cast_ushort':base.replace('= event->valueD;', '= (unsigned short)event->valueD;'),
'cast_signedchar':base.replace('= event->valueD;', '= (signed char)event->valueD;')}
for name,source in variants.items():
    (out/(name+'.c')).write_text(source,encoding='ascii')
trials=[]
for name,source in variants.items():
    for profile in ('aztec36','aztec36-x3','aztec50','aztec50-short'):
        trials.append(dict(source=source,profile=profile,target_node=9))
for name,compiled in zip([(n,p) for n in variants for p in ('aztec36','aztec36-x3','aztec50','aztec50-short')],compile_many(trials)):
    n,p=name
    if compiled['status']!='COMPILED': print(n,p,compiled['status']); continue
    code=bytes.fromhex(compiled['contribution']['code_hex'])
    print(n,p,'len',len(code),'moveq0',[i for i in range(len(code)-1) if code[i:i+2]==b'\x70\x00'],'move.l0',[i for i in range(len(code)-5) if code[i:i+6]==bytes.fromhex('203c00000000') or code[i:i+6]==bytes.fromhex('203c00000000')])
