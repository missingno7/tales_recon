"""Complete pinned freeseg and CRT0; structural references and seven exact fields.

Resolved bytes exist only in validation comparisons. No storage ownership,
original object order, source language for freeseg, or root layout is inferred.
"""
from names import to_mechanical
import json
from pathlib import Path
from common import require, sha256, json_bytes
from repo_paths import canonical_path, candidate_path
from hunk import parse
from overlay_experiment import symbols
from resident_mixed import pinned
import runtime_natural_members as n
import runtime_members as r
import crt0_controls as c

RECIPE='evidence/contributions/runtime-root-members.json'
OUTPUT='evidence/experiments/runtime-members-root.json'
RECIPE_DIGEST='e345445cc302834a8555407a1fe2f7442f3627f636fc74f9096c1c5c1561dc4b'
FREERELOCS=[dict(offset=o,type='HUNK_RELOC32',width=4,target=dict(kind='ROOT_HUNK_ORIGIN',hunk=h,type='CODE' if h==0 else 'DATA',addend=a)) for o,h,a in [(18,0,12),(24,1,0),(66,1,0),(84,0,16)]]
CRTREL=[dict(offset=116,type='HUNK_RELOC32',width=4,target=dict(kind='ROOT_HUNK_ORIGIN',hunk=1,type='DATA',addend=32766))]
COMMANDS=['Old2:bin/lb >extract.log Old1:lib/c.lib -x freeseg','Old1:bin/ln -m -t -o freeseg.exe freeseg.o >freeseg-ln.log']

def read(root,path):return (to_mechanical(candidate_path(root,Path(root)/path).read_bytes()) if str(path).startswith('src/') else candidate_path(root,Path(root)/path).read_bytes())

def checked(root,row):
    raw=read(root,row['path']);require(sha256(raw)==row['sha256'],'root runtime retained input changed: '+row['path']);return raw

def producer(root,doc):
    job=doc['job'];require(job=='build/worker-jobs/sol-glue-tail-root-14','root runtime producer path differs')
    request=json.loads(checked(root,doc['request']));receipt=json.loads(checked(root,doc['receipt']))
    require(receipt['request']==request and [s['command'] for s in request['steps']]==[s['command'] for s in receipt['steps']]==COMMANDS and receipt['all_steps_succeeded'] and all(s['returncode']==0 for s in receipt['steps']),'root runtime producer recipe failed/differs')
    for path,key in [('sys/s/startup-sequence','guest_script_sha256'),('worker.uae','config_sha256'),('kick.rom','rom_sha256')]:require(sha256(read(root,job+'/'+path))==request[key],'root runtime environment changed')
    require(sha256(Path(request['emulator']).read_bytes())==request['emulator_sha256'],'root runtime emulator changed')
    for path in ('SYS2/bin/lb','SYS1/bin/ln','SYS1/lib/c.lib'):
        path='toolchain/installed/aztec-3.6a/'+path
        require(dict(path=path,sha256=sha256(pinned(root,path))) in request['pinned_inputs'],'root runtime producer pin differs')
    inventory={a['path']:a for a in receipt['artifacts']}
    require(len(inventory)==len(receipt['artifacts']),'root runtime duplicate artifact')
    for name in ('freeseg.o','freeseg.exe','freeseg.sym','extract.log','freeseg-ln.log','scope.txt'):
        raw=read(root,job+'/sys/work/'+name);require(name in inventory and inventory[name]['sha256']==sha256(raw) and inventory[name]['size']==len(raw),'root runtime artifact changed')
    obj=read(root,job+'/sys/work/freeseg.o');require(n.object_sizes(obj)==(182,0,0),'freeseg partial/storage object')
    require(pinned(root,'toolchain/installed/aztec-3.6a/SYS1/lib/c.lib').count(obj)==1,'freeseg pinned complete membership differs')
    b=read(root,job+'/sys/work/freeseg.exe');return (b,parse(b),symbols(read(root,job+'/sys/work/freeseg.sym').decode('ascii'))),obj

def compare_freeseg(candidate,original,*,size=182):
    b,m,sm=candidate;require(size==182,'freeseg partial object')
    require([(h['number'],h['type'],h['initialized_size'],h['allocated_size']) for h in m['hunks']]==[(0,'CODE',184,184),(1,'DATA',0,0),(2,'BSS',0,0)],'freeseg whole standalone sections differ')
    require(n.extent(b,m,0,size,2)==bytes(2),'freeseg standalone alignment differs')
    entries=sorted((name,off) for (hn,name),off in sm.items() if hn==0 and not name.startswith('__H'))
    require(entries==[('_freeseg',0)],'freeseg exports differ')
    for model,off in ((m,0),(original[1],0x7522)):
        require(r.relocation_identity(model,dict(hunk=0,offset=off,size=size))==FREERELOCS,'freeseg complete structural relocations differ')
    require(len(m['relocations'])==4,'freeseg extra standalone relocation')
    raw=n.extent(b,m,0,0,size);require(raw==n.extent(*original,0,0x7522,size),'freeseg complete CODE differs')
    return raw

def anchors(root,doc,original):
    ledger=json.loads(canonical_path(root,'recovery/ledger.json').read_text());proofs={}
    for fid,record in doc['anchors'].items():
        row=ledger['mixed_source_objects'].get(fid)
        require(row and all(row[k]==v for k,v in record.items()),'CRT0 independent canonical anchor differs')
        for key in ('source','proof'):require(sha256(read(root,record[key]))==record[key+'_sha256'],'CRT0 anchor bytes changed')
        proof=json.loads(read(root,record['proof']));require(proof['kind']=='SDK_DERIVED_MIXED_OBJECT' and proof['comparison']['verdict']=='EQUAL' and proof['comparison']['complete_object'],'CRT0 incomplete anchor')
        for item in proof['input_graph']:checked(root,item)
        proofs[fid]=proof
    require(set(proofs)=={'resident_F_8552','resident_F_766C'},'CRT0 anchor inventory differs')
    import resident_mixed
    require(read(root,doc['anchors']['resident_F_8552']['source']).decode('ascii')==resident_mixed.expected_source(root),'CRT0 saved stack SDK role differs')
    saved=[f for f in proofs['resident_F_8552']['field_identities'] if f['site']==226]
    require(saved==[dict(original_offset=0xb39e,site=226,symbol='_G_h01_B39E')],'CRT0 saved stack independent identity differs')
    savedoff=saved[0]['original_offset'];p=proofs['resident_F_8552']
    require(32766+int.from_bytes(n.extent(*original,0,p['original']['start']+228,2),'big',signed=True)==savedoff,'CRT0 original saved-stack anchor changed')
    startup=proofs['resident_F_766C']['original'];require(startup==dict(hunk=0,start=0x766c,end=0x77a4),'CRT0 complete startup entry differs')
    # Independent existing bootstrap and DOS initializer, already consumed by glue.
    nr=json.loads(canonical_path(root,n.RECIPE).read_text());crt=n.producer(root,nr)['crt'];bases=n.bootstrap(crt,original)
    from startup_callees import dosbase
    sysbase=bases['_SysBase']['original'][1];dos=dosbase(root,*original,sysbase,32766)
    return dict(saved_stack=savedoff,sysbase=sysbase,dosbase=dos,startup=startup['start'])

def field_values(model,sm,start,identities=None):
    h=next(h for h in model['hunks'] if h['number']==1);end=h['initialized_size'];allocation=h['allocated_size']
    require(allocation>=end and (allocation-end)%4==0,'CRT0 BSS allocation bound differs')
    if identities is None:
        require(sm[(1,'__H1_end')]==sm[(2,'__H2_org')]==end and sm[(2,'__H2_end')]==allocation,'CRT0 candidate structural symbols differ')
        identities=dict(saved_stack=n.symbol(sm,'__savsp')[1],sysbase=n.symbol(sm,'_SysBase')[1],dosbase=n.symbol(sm,'_DOSBase')[1],startup=n.symbol(sm,'__main')[1])
    return [end-32766,end-32766,(allocation-end)//4-1,identities['saved_stack']-32766,identities['sysbase']-32766,identities['dosbase']-32766,identities['startup']-start-96]

def resolve_crt(raw,values,*,fields=c.FIELDS):
    require(fields==(4,8,16,30,38,78,96) and len(raw)==122 and len(values)==7,'CRT0 masked/partial field contract')
    out=bytearray(raw)
    for off,value in zip(fields,values):
        require(-32768<=value<=32767,'CRT0 field width differs');out[off:off+2]=value.to_bytes(2,'big',signed=True)
    return bytes(out)

def compare_crt(candidate,original,identities,*,fields=c.FIELDS,size=122):
    b,m,sm=candidate;require(size==122 and fields==c.FIELDS,'CRT0 partial/masked contract')
    start=n.symbol(sm,'.begin')[1];raw=n.extent(b,m,0,start,size)
    require(n.symbol(sm,'_geta4')==(0,start+114) and n.symbol(sm,'_segload')==(0,start+122),'CRT0 complete boundary differs')
    cv=field_values(m,sm,start);require([int.from_bytes(raw[f:f+2],'big',signed=True) for f in fields]==cv,'CRT0 candidate field binding differs')
    entry=n.extent(*original,0,0,4);require(entry[:2]==bytes.fromhex('6000') and 2+int.from_bytes(entry[2:],'big',signed=True)==0x75f2,'CRT0 independent root entry differs')
    ov=field_values(original[1],None,0x75f2,identities)
    for model,at in ((m,start),(original[1],0x75f2)):
        require(r.relocation_identity(model,dict(hunk=0,offset=at,size=size))==CRTREL,'CRT0 complete structural relocation differs')
    resolved=resolve_crt(raw,ov,fields=fields)
    require(resolved==n.extent(*original,0,0x75f2,size),'CRT0 complete bytes/independent fields differ')
    return resolved,dict(zip(map(str,fields),ov))

def contexts(root):
    # This replays unmodified complete library and SDK assembly in three contexts.
    c.verify(root);result=[]
    for scope,prefix in [('allocation','base'),('allocation','shifted'),('order','dos-first')]:
        path=c.BASE+'/'+scope+'/'+prefix+'-lib';b=read(root,path+'.exe');result.append((b,parse(b),symbols(read(root,path+'.sym').decode('ascii'))))
    return result

def verify(root,*,document=None,original=None):
    if document is None:document=json.loads(canonical_path(root,RECIPE).read_text())
    require(sha256(json_bytes(document))==RECIPE_DIGEST,'root runtime curated recipe changed')
    if original is None:
        from analysis_support import game
        from census import advisory_image
        with advisory_image():original=game()[:2]
    require(sha256(original[0])==document['game_sha256'],'root runtime oracle differs')
    candidate,obj=producer(root,document);free=compare_freeseg(candidate,original)
    ids=anchors(root,document,original);variants=[compare_crt(x,original,ids) for x in contexts(root)]
    require(all(v==variants[0] for v in variants),'CRT0 contexts differ after independent binding')
    raw,values=variants[0];rows=[]
    for member,start,size,payload,entries,rels,objecthash in [
        ('freeseg',0x7522,182,free,[dict(name='_freeseg',offset=0)],FREERELOCS,sha256(obj)),
        ('crt0',0x75f2,122,raw,[dict(name='.begin',offset=0,abi='CRT_ENTRY'),dict(name='_geta4',offset=114,abi='REGISTER_A4')],CRTREL,sha256(read(root,c.BASE+'/order/crt0.o')))]:
        rows.append(dict(member=member,members=[member],profile='aztec36',provider='PINNED_LIBRARY_OBJECT',original=dict(hunk=0,offset=start,size=size),size=size,entries=entries,code_sha256=sha256(payload),object_sha256s={member:objecthash},owned_data_size=0,owned_bss_size=0,relocation_identity=rels,**(dict(field_values=values) if member=='crt0' else {})))
    return dict(schema_version=1,status='COMPLETE_RUNTIME_CODE_MATCH',game_sha256=document['game_sha256'],recipe=RECIPE,recipe_sha256=RECIPE_DIGEST,contributions=rows,reconstructed_game_functions=0,exact_compiler_release_selected=False,limitations=['No DATA/BSS credit, historical TU, release or natural root layout.','CRT0 entry and register-A4 helper have no ordinary C call route.','Standalone freeseg two-byte alignment is excluded.'])

def specimens(root,report,*,original=None):
    if original is None:
        from analysis_support import game
        from census import advisory_image
        with advisory_image():original=game()[:2]
    doc=json.loads(canonical_path(root,RECIPE).read_text());candidate,_=producer(root,doc);crt=contexts(root)[0];result=[]
    for row in report['contributions']:
        if row['member']=='freeseg':raw=n.extent(candidate[0],candidate[1],0,0,182)
        else:raw=resolve_crt(n.extent(crt[0],crt[1],0,n.symbol(crt[2],'.begin')[1],122),[row['field_values'][str(f)] for f in c.FIELDS])
        require(sha256(raw)==row['code_sha256'],'root runtime resolved specimen differs');o=row['original']
        rels=[dict(source_offset=o['offset']+r['offset'],target_hunk=r['target']['hunk'],type=r['type'],width=r['width'],addend_raw=r['target']['addend']) for r in row['relocation_identity']]
        rels.sort(key=lambda row:next(i for i,actual in enumerate(original[1]['relocations']) if actual['source_hunk']==0 and all(actual[k]==v for k,v in row.items())))
        result.append(dict(id='runtime_root_'+row['member'],hunk=0,start=o['offset'],end=o['offset']+o['size'],actual_hex=raw.hex(),actual_sha256=sha256(raw),representation='RESOLVED_VALIDATION_COMPARISON',relocations=rels,proof=dict(receipt=OUTPUT,member=row['member'],object_sha256s=row['object_sha256s'],relocation_identity=row['relocation_identity'],field_values=row.get('field_values',{}))))
    return result

def input_identity(root):
    path=canonical_path(root,RECIPE)
    if not path.exists():return {str(path):None}
    doc=json.loads(path.read_text());paths={RECIPE,OUTPUT,'tools/runtime_root_members.py','tools/crt0_controls.py',c.SDK,'toolchain/installed/aztec-3.6a/SYS1/lib/c.lib',doc['request']['path'],doc['receipt']['path']}
    receipt=json.loads(read(root,doc['receipt']['path']));paths.update(doc['job']+'/sys/work/'+r['path'] for r in receipt['artifacts']);paths.update(r['path'] for r in receipt['request']['pinned_inputs'])
    paths.update(doc['job']+'/'+p for p in ('sys/s/startup-sequence','worker.uae','kick.rom'))
    for scope in ('allocation','order'):
        directory=c.BASE+'/'+scope;paths.add(directory+'/receipt.json');rec=json.loads(read(root,directory+'/receipt.json'));paths.update(directory+'/'+r['path'] for r in rec['artifacts']);paths.update(r['path'] for r in rec['tool_inputs'])
    for row in doc['anchors'].values():
        paths.update(row[k] for k in ('source','proof'));proof=json.loads(read(root,row['proof']));paths.update(r['path'] for r in proof['input_graph'])
    result={str(Path(root)/p):sha256(read(root,p)) if Path(root,p).exists() else None for p in paths}
    emulator=Path(receipt['request']['emulator']);result[str(emulator)]=sha256(emulator.read_bytes());return result
