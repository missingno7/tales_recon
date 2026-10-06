import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from analysis_support import game,K
from function_compare import unique_word_site
from overlay_experiment import symbols,contribution
from hunk import parse,manx_overlay
from common import require
import capstone

from source_recipe import source_views
from abi_recipe import abi_views
from common import sha256
expected=abi_views(source_views(ROOT))
for scope, views in [('pointer',source_views(ROOT)),('abi',expected),('partition',expected)]:
    retained=ROOT/'evidence/rules/startup-mechanical'/scope
    for name,source in views.items():
        require((retained/(name+'.c')).read_bytes()==source.encode('ascii'),'retained source does not rederive')
    receipt=json.loads((retained/'receipt.json').read_bytes())
    require(all(s['returncode']==0 for s in receipt['steps']),'producing step failed')
    for item in receipt['artifacts']:
        require(sha256((retained/item['path']).read_bytes())==item['sha256'],'retained artifact hash differs')
    for item in receipt['tool_inputs']:
        require(sha256((ROOT/item['path']).read_bytes())==item['sha256'],'producing tool/header differs')
inventory=json.loads((ROOT/'evidence/toolchain/aztec-3.6a.json').read_bytes())
sdk='toolchain/installed/aztec-3.6a/SYS2/crt_src/_main.c'
pins={'toolchain/installed/aztec-3.6a/'+d['manifest']['volume']+'/'+e['path']:e['sha256']
      for d in inventory['disks'] if d['status']=='VALIDATED' for e in d['manifest']['entries'] if e['kind']=='file'}
require(sha256((ROOT/sdk).read_bytes())==pins[sdk],'SDK source identity differs')
for scope in ('pointer','abi','partition'):
    receipt=json.loads((ROOT/'evidence/rules/startup-mechanical'/scope/'receipt.json').read_bytes())
    for tool in receipt['tool_inputs']:
        require(pins.get(tool['path'])==tool['sha256'],'tool/header receipt not pinned to inventory')
    producing=[]
    profiles=([('candidate','candidate',''),('marked','marked',''),('root','root',''),('overlay','overlay','')]
        if scope=='pointer' else [('candidate','candidate',''),('x3','candidate','+X3 '),('marked','marked',''),('root','root',''),('overlay','overlay','')]
        if scope=='abi' else [('marked','marked','+X3 '),('root','root',''),('overlay','overlay','')])
    for name,src,flags in profiles:
        producing.extend([f'Old1:bin/cc -a {flags}-I Old1:include -o {name}.asm {src}.c <compiler-input.txt >{name}-cc.log',
            f'Old1:bin/as -o {name}.o {name}.asm <compiler-input.txt >{name}-as.log'])
    for name in (('candidate','marked') if scope=='pointer' else ('candidate','x3','marked') if scope=='abi' else ('marked',)):
        producing.append(f'Old1:bin/ln -m -t -o {name}.exe root.o {name}.o +o1 overlay.o +o0 Old1:lib/c.lib >{name}-ln.log')
    require([step['command'] for step in receipt['steps']]==producing,'source producing recipe differs')

directory=ROOT/'evidence/rules/startup-mechanical/abi'
b=(directory/'x3.exe').read_bytes();model=parse(b);sm=symbols((directory/'x3.sym').read_text());start=sm[(0,'_recovered')]
raw=contribution(b,model,0,start,312)
obj=(directory/'x3.o').read_bytes()
require(obj[:2]==b'AJ' and [int.from_bytes(obj[n:n+4],'big') for n in (10,14,18)]==[312,0,0],
    'complete startup object bounds/storage differ')
require(sm[(0,'_segload')]==start+312 and not any(r['source_hunk']==0 and r['source_offset']<start+312 and
    r['source_offset']+r['width']>start for r in model['relocations']), 'startup boundary or relocation differs')
blob,om,_=game();original=contribution(blob,om,0,30316,312)
md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000);md.detail=True
ei=list(md.disasm(original[:310],0));ai=list(md.disasm(raw[:310],0))
require([(i.address,i.size,i.mnemonic) for i in ei]==[(i.address,i.size,i.mnemonic) for i in ai],'shape differs')
fields=[];mask=set()
for e,a in zip(ei,ai):
    for eo,ao in zip(e.operands,a.operands):
        if eo.type!=K.M68K_OP_MEM:continue
        kind=None
        if eo.mem.base_reg==K.M68K_REG_A4 and eo.address_mode==K.M68K_AM_REGI_ADDR_DISP:
            kind='A4';old=32766+eo.mem.disp;actual=32766+ao.mem.disp
            if e.mnemonic=='jsr' and old==270:
                name='_F_h00_8534';require(sm.get((1,name))==actual,'exit DATA name differs')
                odh=next(h for h in om['hunks'] if h['number']==1)
                original_entry=blob[odh['content_offset']+old:odh['content_offset']+old+6]
                original_refs=[r for r in om['relocations'] if r['source_hunk']==1 and r['source_offset']<old+6 and r['source_offset']+r['width']>old]
                require(original_entry==bytes.fromhex('4ef9')+(34100).to_bytes(4,'big') and len(original_refs)==1 and
                    original_refs[0]['source_offset']==old+2 and original_refs[0]['target_hunk']==0 and original_refs[0]['addend_raw']==34100,
                    'original exit route differs')
                dh=next(h for h in model['hunks'] if h['number']==1)
                require(0<=actual and actual+6<=dh['initialized_size'],'exit DATA bounds differ')
                data=b[dh['content_offset']+actual:dh['content_offset']+actual+6]
                require(data[:2]==bytes.fromhex('4ef9'),'exit DATA record differs')
                rr=[r for r in model['relocations'] if r['source_hunk']==1 and r['source_offset']==actual+2]
                require(len(rr)==1 and rr[0]['target_hunk']==0 and rr[0]['addend_raw']==sm[(0,'_exit_body')],'exit relocation differs')
            elif e.mnemonic=='jsr' and old==584:
                name='_F_h03_0000'
                otree=manx_overlay(om,blob)
                original_routes=[s for slot in otree['slots'] for s in slot['symbols'] if s['trampoline_offset']==old]
                require(len(original_routes)==1 and original_routes[0]['target_hunk']==3 and original_routes[0]['target_offset']==0 and original_routes[0]['encoded_node_id']==1,
                    'original main route differs')
                tree=manx_overlay(model,b)
                matches=[s for slot in tree['slots'] for s in slot['symbols'] if s['trampoline_offset']==actual]
                require(len(matches)==1 and matches[0]['target_hunk']==3 and matches[0]['target_offset']==sm[(3,name)]==0 and matches[0]['encoded_node_id']==1,'main overlay route differs')
            else:
                name='_G_h01_%04X'%old
                require(any(n==name and h in (1,2) and off==actual for (h,n),off in sm.items()),'global identity differs')
        elif eo.address_mode==K.M68K_AM_PCI_DISP:
            old=e.address+2+eo.mem.disp;actual=a.address+2+ao.mem.disp
            if e.mnemonic=='jsr':
                old+=30316;actual+=start;kind='CALL';name='_F_h00_%04X'%old
                require(sm.get((0,name))==actual,'callee identity differs')
            else:
                require(old==actual==310 and raw[310:]==original[310:]==b'*\0','literal identity differs')
                name='COMPILER_LITERAL_STAR';kind='LITERAL'
        if kind:
            es=unique_word_site(e,eo.mem.disp);as_=unique_word_site(a,ao.mem.disp)
            require(es==as_ and es is not None,'field encoding ambiguous')
            pos=e.address+es;mask.update([pos,pos+1]);fields.append(dict(site=e.address,field=pos,kind=kind,symbol=name,original_offset=old,actual_offset=actual))
require(all(x==y for i,(x,y) in enumerate(zip(original,raw)) if i not in mask),'ordinary byte differs')
marked_dir=ROOT/'evidence/rules/startup-mechanical/partition'
require([int.from_bytes((marked_dir/'marked.o').read_bytes()[n:n+4],'big') for n in (10,14,18)]==[312,0,0],
    'complete marked object bounds/storage differ')
mb=(marked_dir/'marked.exe').read_bytes();mm=parse(mb);ms=symbols((marked_dir/'marked.sym').read_text());mst=ms[(0,'_recovered')]
require(contribution(mb,mm,0,mst,312)==raw,'marker changes whole CODE')
require([ms[(0,n)]-mst for n in ('_startup_asm_begin','_startup_asm_end')]==[48,54],'marker span differs')
for key,off in sm.items():
    if key[1].startswith(('_G_h01_','_F_h00_','_F_h03_')):require(ms.get(key)==off,'marker changes bindings')
report=dict(status='COMPLETE_MECHANICAL_STARTUP_MATCH_EXPERIMENT_ONLY',acceptance=False,
    code_bytes=312,c_compiler_bytes=304,sdk_asm_bytes=6,compiler_literal_bytes=2,
    field_identities=fields,masked_bytes=len(mask),ordinary_bytes=312-len(mask),
    partitions=[['C_COMPILER',0,48],['ASM',48,54],['C_COMPILER',54,310],['COMPILER_OWNED_DATA',310,312]])

print(json.dumps({k:v for k,v in report.items() if k!='field_identities'},indent=2))
