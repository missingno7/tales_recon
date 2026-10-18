"""Opt-in complete natural runtime objects with independently checked operands.

Only the curated 3.6a recipe is supported. No masks, opcode conversions,
linked-output edits, guessed slot votes, or historical release selection.
"""
from names import read_source
import json
from pathlib import Path
from common import require, sha256, json_bytes
from repo_paths import canonical_path, candidate_path
from hunk import parse
from overlay_experiment import symbols
from resident_mixed import pinned
import function_compare as fc
from capstone import m68k as K

RECIPE = 'evidence/contributions/runtime-natural-members.json'
RECIPE_DIGEST = 'b3d7302e992a139b289356aca128ccdab8d3e6a4bd8f3e25cf2a9b9256d8fb8b'
OUTPUT = 'evidence/experiments/runtime-members-natural.json'
SPECS = {
 'wbparse': dict(object='wbparse.o', export='__wb_parse', delta=0, size=180, code_size=158, original=0x7B24, entries=[('__wb_parse',0)]),
 'format': dict(object='format.o', export='_format', delta=-142, size=936, code_size=936, original=0x7BF4, entries=[('_format',142)]),
 'printf': dict(object='printf.o', export='_printf', delta=0, size=28, code_size=28, original=0x7BD8, entries=[('_printf',0)]),
}


LEGACY_MEMBERS = ('wbparse','format','printf')
SPECS.update({
 'sscanf': dict(object='sscanf.o',export='_sscanf',delta=0,size=112,code_size=112,original=0x704e,entries=[('_sscanf',0)]),
 'scan': dict(object='scan.o',export='_scanfmt',delta=0,size=1124,code_size=1124,original=0x70be,entries=[('_scanfmt',0),('_skipblank',824),('_getnum',882)]),
 'abort': dict(object='abort.o',export='__abort',delta=0,size=42,code_size=38,original=0x850a,entries=[('__abort',0)]),
 'createpo': dict(object='createpo.o',export='_CreatePort',delta=0,size=210,code_size=210,original=0x8794,entries=[('_CreatePort',0),('_DeletePort',140)]),
 'createst': dict(object='createst.o',export='_CreateStdIO',delta=0,size=40,code_size=40,original=0x887e,entries=[('_CreateStdIO',0),('_DeleteStdIO',22)]),
 'createex': dict(object='createex.o',export='_CreateExtIO',delta=0,size=128,code_size=128,original=0x88a6,entries=[('_CreateExtIO',0),('_DeleteExtIO',68)]),
})
TAIL_MEMBERS=('sscanf','scan','abort','createpo','createst','createex')


def read(root, path):
    return (read_source(root, Path(root) / path, scratch=True, names_root=None) if str(path).startswith('src/') else candidate_path(root, Path(root)/path).read_bytes())


def extent(blob, model, hn, start, size):
    h = next((h for h in model['hunks'] if h['number']==hn), None)
    require(h and 0 <= start <= h['initialized_size']-size, 'natural runtime extent outside initialized hunk')
    return blob[h['content_offset']+start:h['content_offset']+start+size]


def relocations(model, hn, start, size):
    return [r for r in model['relocations'] if r['source_hunk']==hn and
            r['source_offset'] < start+size and r['source_offset']+r['width'] > start]


def object_sizes(raw):
    require(raw[:2] in (b'AJ',b'CJ') and len(raw)>=22, 'natural runtime object format')
    return tuple(int.from_bytes(raw[i:i+4],'big') for i in (10,14,18))


def symbol(sm, name):
    found=[(h,o) for (h,n),o in sm.items() if n==name]
    require(len(found)==1, 'missing/duplicate natural runtime symbol: '+name)
    return found[0]


def unique(payload, raw):
    hits=[i for i in range(0,len(payload)-len(raw)+1,2) if payload[i:i+len(raw)]==raw]
    require(len(hits)==1, 'natural runtime complete payload is not unique')
    return hits[0]


def slot_target(blob, model, displacement):
    offset=32766+displacement
    require(any(h['number']==1 and h['type']=='DATA' for h in model['hunks']) and
            any(h['number']==0 and h['type']=='CODE' for h in model['hunks']), 'natural runtime slot hunk type differs')
    raw=extent(blob,model,1,offset,6)
    require(raw[:2]==bytes.fromhex('4ef9'), 'natural runtime slot is not JMP absolute')
    rs=relocations(model,1,offset,6)
    require(len(rs)==1 and (rs[0]['source_offset'],rs[0]['type'],rs[0]['width'],rs[0]['target_hunk'])==
            (offset+2,'HUNK_RELOC32',4,0), 'natural runtime slot relocation differs')
    target=int.from_bytes(raw[2:],'big')
    require(rs[0]['addend_raw']==target, 'natural runtime slot addend differs')
    extent(blob,model,0,target,2)
    return (0,target), dict(slot_hunk=1,slot_offset=offset,relocation=dict(rs[0]))


def compare_member(candidate, original, original_start, candidate_start, size, code_size, fields, identities):
    """Check all operands, then compare every byte after resolving proven fields.

    identities maps a symbol to independently proved original/candidate
    coordinates. fields is the exhaustive external-operand contract. Internal
    PC references must preserve their exact relative target. Literal tails
    remain in the full comparison, without decoding them as instructions.
    """
    cb,cm,cs=candidate;ob,om=original
    raw=extent(cb,cm,0,candidate_start,size);expected=extent(ob,om,0,original_start,size)
    require(not relocations(cm,0,candidate_start,size) and not relocations(om,0,original_start,size),
            'natural runtime contribution has unchecked relocation')
    ci,err=fc.decode_all(raw[:code_size],[]);oi,oerr=fc.decode_all(expected[:code_size],[])
    require(err is None and oerr is None and sum(i.size for i in ci)==code_size and sum(i.size for i in oi)==code_size,
            'natural runtime incomplete instruction decode')
    require([(i.address,i.size,i.mnemonic) for i in ci]==[(i.address,i.size,i.mnemonic) for i in oi],
            'natural runtime instruction layout differs')
    seen=set();proof=[]
    for c,o in zip(ci,oi):
        require(len(c.operands)==len(o.operands), 'natural runtime operand count differs')
        for cp,op in zip(c.operands,o.operands):
            def kind(p):
                if p.type==K.M68K_OP_BR_DISP:return 'PC'
                if p.type==K.M68K_OP_MEM:
                    if p.address_mode==K.M68K_AM_PCI_DISP:return 'PC'
                    require(p.mem.base_reg!=K.M68K_REG_PC and p.address_mode not in
                            {v for n,v in vars(K).items() if n.startswith('M68K_AM_PCI')}, 'unsupported natural runtime PC mode')
                    if p.mem.base_reg==K.M68K_REG_A4:
                        require(p.address_mode==K.M68K_AM_REGI_ADDR_DISP, 'unsupported natural runtime A4 mode')
                        return 'A4'
                return None
            ck,ok=kind(cp),kind(op)
            require(ck==ok, 'natural runtime addressing mode changed')
            if ck is None:continue
            cd=cp.br_disp.disp if cp.type==K.M68K_OP_BR_DISP else cp.mem.disp
            od=op.br_disp.disp if op.type==K.M68K_OP_BR_DISP else op.mem.disp
            if ck=='PC' and c.address+2+cd>=0 and c.address+2+cd<size and o.address+2+od>=0 and o.address+2+od<size:
                require(cd==od, 'natural runtime internal PC target changed')
                proof.append(dict(site=c.address,kind='INTERNAL_PC',target=c.address+2+cd))
                continue
            require(c.size>=4, 'unsupported external short natural runtime branch')
            local=fc.unique_word_site(c,cd) if ck=='A4' else 2
            olocal=fc.unique_word_site(o,od) if ok=='A4' else 2
            require(local is not None and local==olocal, 'natural runtime field site differs')
            field=c.address+local
            require(field in fields and field not in seen, 'unbound/duplicate natural runtime operand')
            spec=fields[field];seen.add(field)
            require(spec['kind']==ck, 'natural runtime operand contract differs')
            name=spec['symbol'];addend=spec.get('addend',0)
            require(name in identities, 'natural runtime operand lacks independent identity: '+name)
            ct,ot=identities[name]['candidate'],identities[name]['original']
            cpcoord=(ct[0],ct[1]+addend);opcoord=(ot[0],ot[1]+addend)
            slot_proof={}
            if ck=='PC':
                actual=(0,candidate_start+c.address+2+cd);want=(0,original_start+o.address+2+od)
            elif spec.get('route'):
                require(c.bytes[:2]==o.bytes[:2]==bytes.fromhex('4eac'), 'natural runtime routed opcode differs')
                actual,cslot=slot_target(cb,cm,cd);want,oslot=slot_target(ob,om,od)
                slot_proof=dict(candidate_slot=cslot,original_slot=oslot)
            else:actual=(1,32766+cd);want=(1,32766+od)
            require(actual==cpcoord and want==opcoord, 'natural runtime operand target identity differs: '+name)
            proof.append(dict(site=c.address,field=field,width=2,kind=ck,symbol=name,addend=addend,
                              candidate=list(actual),original=list(want),**slot_proof))
    require(seen==set(fields), 'natural runtime operand contract not exhausted')
    cursor=0
    for field in sorted(seen):
        require(field>=cursor and raw[cursor:field]==expected[cursor:field], 'natural runtime whole member bytes differ')
        cursor=field+2
    require(raw[cursor:]==expected[cursor:], 'natural runtime whole member bytes differ')
    return dict(size=size,raw_equal=raw==expected,code_sha256=sha256(expected),candidate_code_sha256=sha256(raw),
                operand_identity=proof)


def producer(root, recipe):
    require(sha256(json_bytes(recipe))==RECIPE_DIGEST, 'natural runtime curated recipe changed')
    directory=recipe['work'];request=json.loads(read(root,recipe['request']['path']))
    receipt=json.loads(read(root,recipe['receipt']['path']))
    for record in (recipe['request'],recipe['receipt']):
        require(sha256(read(root,record['path']))==record['sha256'], 'natural runtime producer receipt changed')
    require(receipt['request']==request and receipt['all_steps_succeeded'] and
            [s['command'] for s in receipt['steps']]==recipe['commands'] and
            all(s['returncode']==0 for s in receipt['steps']), 'natural runtime producing recipe differs')
    require([s['command'] for s in request['steps']]==recipe['commands'], 'natural runtime request commands differ')
    job=Path(recipe['request']['path']).parent.as_posix()
    for path,key in [(job+'/sys/s/startup-sequence','guest_script_sha256'),(job+'/worker.uae','config_sha256'),(job+'/kick.rom','rom_sha256')]:
        require(sha256(read(root,path))==request[key], 'natural runtime producer environment changed')
    require(sha256(Path(request['emulator']).read_bytes())==request['emulator_sha256'], 'natural runtime emulator changed')
    sources={s['path']:s for s in request['source_files']}
    require(set(sources)==set(recipe['sources'])|{'format.c'}, 'natural runtime source inventory differs')
    archive=read(root,recipe['sdk']['path'])
    require(sha256(archive)==recipe['sdk']['sha256'], 'natural runtime SDK archive changed')
    lines=archive.splitlines(keepends=True)
    a=next(i for i,l in enumerate(lines) if l.strip()==b'format.c')+1
    z=next(i for i in range(a,len(lines)) if lines[i].strip()==b'makefile')
    expected={n:t.encode('ascii') for n,t in recipe['sources'].items()};expected['format.c']=b''.join(lines[a:z])
    for n,raw in expected.items():
        require(read(root,directory+'/'+n)==raw and sources[n]['sha256']==sha256(raw), 'natural runtime source does not rederive')
    pins={p['path']:p for p in request['pinned_inputs']}
    for path,digest in recipe['tools'].items():
        require(path in pins and pins[path]['sha256']==digest and sha256(pinned(root,path))==digest,
                'natural runtime tool pin differs')
    artifacts={a['path']:a for a in receipt['artifacts']}
    require(len(artifacts)==len(receipt['artifacts']) and set(recipe['artifacts'])<=set(artifacts), 'natural runtime artifact inventory differs')
    for name,digest in recipe['artifacts'].items():
        require(Path(name).name==name and '/' not in name and '\\' not in name, 'natural runtime artifact path differs')
        raw=read(root,directory+'/'+name)
        require(artifacts[name]['sha256']==digest==sha256(raw) and artifacts[name]['size']==len(raw), 'natural runtime artifact changed')
    library=pinned(root,'toolchain/installed/aztec-3.6a/SYS1/lib/c.lib')
    for name in recipe['library_objects']:
        raw=read(root,directory+'/'+name)
        require(library.count(raw)==1, 'natural runtime object not unique in pinned library: '+name)
    for name in LEGACY_MEMBERS:
        spec=SPECS[name]
        require(object_sizes(read(root,directory+'/'+spec['object']))==(spec['size'],18 if name=='format' else 0,0), 'natural runtime whole object size differs')
    result={}
    for prefix in ('natural','reverse','crt'):
        b=read(root,directory+'/'+prefix);m=parse(b);sm=symbols(read(root,directory+'/'+prefix+'.sym').decode('ascii'))
        result[prefix]=(b,m,sm)
    result.update(producer_tail(root,recipe['tail']))
    return result


def anchor(root, recipe, fid, original, field):
    record=recipe['anchors'][fid]
    proof=json.loads(read(root,record['proof']));ledger=json.loads(canonical_path(root,'recovery/ledger.json').read_text())
    item=ledger['functions'][fid]
    require(item['state']=='FUNCTION_WITH_DATA_MATCH' and item['proof']==record['proof'] and
            item['proof_sha256']==record['proof_sha256']==sha256(read(root,item['proof'])) and
            item['source']==record['source'] and item['source_sha256']==record['source_sha256']==sha256(read(root,item['source'])),
            'natural runtime canonical anchor changed')
    ex=item['evidence_extent'];ob,om=original
    require(sha256(extent(ob,om,ex['hunk'],ex['start'],ex['size']))==ex['sha256'], 'natural runtime canonical original anchor changed')
    rows=[r for r in proof['relocation_proof'] if r['offset']==field]
    require(len(rows)==1 and rows[0]['identity']['addend']==0, 'natural runtime canonical field anchor missing')
    return rows[0]['identity']['hunk'],rows[0]['identity']['offset']


def bootstrap(candidate, original):
    cb,cm,cs=candidate;ob,om=original
    cstart=symbol(cs,'.begin')[1]
    entry=extent(ob,om,0,0,4)
    require(entry[:2]==bytes.fromhex('6000'), 'natural runtime original root entry differs')
    ostart=2+int.from_bytes(entry[2:],'big',signed=True)
    c=extent(cb,cm,0,cstart,122);o=extent(ob,om,0,ostart,122)
    require(c[32:38]==o[32:38]==bytes.fromhex('2c780004294e') and
            c[68:78]==o[68:78]==bytes.fromhex('43fa00204eaefe682940') and
            c[102:114]==o[102:114]==b'dos.library\0', 'natural runtime independent bootstrap base initializer differs')
    result={}
    for n,field in [('_SysBase',38),('_DOSBase',78)]:
        ct=symbol(cs,n)[1];ot=32766+int.from_bytes(o[field:field+2],'big',signed=True)
        require(32766+int.from_bytes(c[field:field+2],'big',signed=True)==ct, 'natural runtime bootstrap symbol binding differs')
        result[n]=dict(candidate=(1,ct),original=(1,ot),basis='PINNED_CRT0_INITIALIZER')
    return result


def bind_data(candidate, original, name, size, obj, root, recipe):
    cb,cm,cs=candidate;ob,om=original
    require(object_sizes(read(root,recipe['work']+'/'+obj))[1:]==(size,0), 'natural runtime DATA provider extent differs')
    hn,off=symbol(cs,name);require(hn==1, 'natural runtime DATA provider symbol hunk differs')
    raw=extent(cb,cm,1,off,size)
    require(not relocations(cm,1,off,size), 'natural runtime DATA provider has unchecked relocations')
    h=next(h for h in om['hunks'] if h['number']==1);payload=extent(ob,om,1,0,h['initialized_size'])
    where=unique(payload,raw)
    require(not relocations(om,1,where,size), 'natural runtime original DATA provider relocation differs')
    return dict(candidate=(1,off),original=(1,where),basis='UNIQUE_COMPLETE_PINNED_DATA_PAYLOAD',size=size,sha256=sha256(raw))


def raw_leaf(candidate, original, name, size, obj, root, recipe):
    cb,cm,cs=candidate;ob,om=original
    require(object_sizes(read(root,recipe['work']+'/'+obj))==(size,0,0), 'natural runtime leaf extent differs')
    hn,start=symbol(cs,name);require(hn==0, 'natural runtime leaf symbol hunk differs')
    raw=extent(cb,cm,0,start,size)
    require(not relocations(cm,0,start,size), 'natural runtime leaf relocation unsupported')
    h=next(h for h in om['hunks'] if h['number']==0);where=unique(extent(ob,om,0,0,h['initialized_size']),raw)
    require(not relocations(om,0,where,size), 'natural runtime original leaf relocation differs')
    return dict(candidate=(0,start),original=(0,where),basis='UNIQUE_COMPLETE_PINNED_CODE',size=size,sha256=sha256(raw))


def environment(root, recipe, candidate, original, crt):
    cb,cm,cs=candidate;ob,om=original
    bases=bootstrap(crt,original)
    # COMMON positions come from each natural link's own map, not CRT context.
    for name,item in bases.items():item['candidate']=(1,symbol(cs,name)[1])
    icon=anchor(root,recipe,'resident_F_7B24',original,24)
    bases['_IconBase']=dict(candidate=(1,symbol(cs,'_IconBase')[1]),original=icon,basis='CANONICAL_WORKBENCH_ACCESS')
    for name,size,obj in [('_ctp_',130,'ctype.o'),('_Cbuffs',440,'getbuff.o')]:
        bases[name]=bind_data(candidate,original,name,size,obj,root,recipe)
    # Anonymous compiler-owned DATA from the unchanged SDK initializer.
    digits=b'0123456789abcdef\0\0'
    dstart=symbol(cs,'_ctp_')[1]-18
    require(extent(cb,cm,1,dstart,18)==digits and not relocations(cm,1,dstart,18), 'natural runtime format complete DATA differs')
    h=next(h for h in om['hunks'] if h['number']==1)
    ostart=unique(extent(ob,om,1,0,h['initialized_size']),digits)
    require(not relocations(om,1,ostart,18), 'natural runtime original format DATA relocation differs')
    bases['FORMAT_LOCAL_DIGITS']=dict(candidate=(1,dstart),original=(1,ostart),basis='COMPLETE_COMPILER_LOCAL_DATA',size=18,sha256=sha256(digits))
    ids=dict(bases)
    for name,size,obj in [('_strlen',18,'strlen.o'),('.divs',168,'ldiv.o'),('_aputc',66,'aputc.o')]:
        ids[name]=raw_leaf(candidate,original,name,size,obj,root,recipe)
    for name,delta in [('.mods',40),('.modu',66),('.divu',78)]:
        ids[name]=dict(candidate=(0,ids['.divs']['candidate'][1]+delta),original=(0,ids['.divs']['original'][1]+delta),basis='COMPLETE_LDIV_EXPORT')
        require(symbol(cs,name)==ids[name]['candidate'], 'natural runtime ldiv export differs')
    leaves=[
      ('__OpenLibrary',16,'_openlib.o',20, {2:dict(kind='A4',symbol='_SysBase')}),
      ('_GetDiskObject',12,'getdisko.o',52, {6:dict(kind='A4',symbol='_IconBase')}),
      ('_FindToolType',14,'findtool.o',72, {8:dict(kind='A4',symbol='_IconBase')}),
      ('__Open',14,'_open.o',90, {8:dict(kind='A4',symbol='_DOSBase')}),
      ('_FreeDiskObject',12,'freedisk.o',138, {6:dict(kind='A4',symbol='_IconBase')}),
    ]
    dependencies=[]
    for name,size,obj,field,fields in leaves:
        require(object_sizes(read(root,recipe['work']+'/'+obj))==(size,0,0), 'natural runtime wrapper object extent differs')
        ct=symbol(cs,name);ot=anchor(root,recipe,'resident_F_7B24',original,field)
        proof=compare_member(candidate,original,ot[1],ct[1],size,size,fields,ids)
        ids[name]=dict(candidate=ct,original=ot,basis='CANONICAL_ENTRY_AND_COMPLETE_PINNED_WRAPPER')
        dependencies.append(dict(member=name,**proof))
    public=anchor(root,recipe,'resident_F_7B24',original,148)
    ids['__CloseLibrary']=dict(candidate=symbol(cs,'__CloseLibrary'),original=(0,public[1]+4),basis='COMPLETE_PUBLIC_PRIVATE_PAIR')
    private=compare_member(candidate,original,public[1]+4,ids['__CloseLibrary']['candidate'][1],12,12,{6:dict(kind='A4',symbol='_SysBase')},ids)
    require(object_sizes(read(root,recipe['work']+'/_closeli.o'))==(12,0,0) and
            object_sizes(read(root,recipe['work']+'/closelib.o'))==(4,0,0), 'natural runtime CloseLibrary whole pair extent differs')
    close=symbol(cs,'_CloseLibrary');require(close==(0,ids['__CloseLibrary']['candidate'][1]-4), 'natural runtime public CloseLibrary entry differs')
    front=compare_member(candidate,original,public[1],close[1],4,4,{2:dict(kind='PC',symbol='__CloseLibrary')},ids)
    ids['_CloseLibrary']=dict(candidate=close,original=public,basis='CANONICAL_PUBLIC_ENTRY_AND_COMPLETE_PAIR')
    put=symbol(cs,'_putchar')
    require(object_sizes(read(root,recipe['work']+'/putchar.o'))==(22,0,0), 'natural runtime putchar whole extent differs')
    put_original=ids['_aputc']['original'][1]-22
    pp=compare_member(candidate,original,put_original,put[1],22,22,{6:dict(kind='A4',symbol='_Cbuffs',addend=22),14:dict(kind='PC',symbol='_aputc')},ids)
    ids['_putchar']=dict(candidate=put,original=(0,put_original),basis='COMPLETE_PINNED_PUTCHAR_WITH_CBUFFS22_AND_APUTC')
    dependencies += [dict(member='_CloseLibrary',**front),dict(member='__CloseLibrary',**private),dict(member='_putchar',**pp)]
    return ids,dependencies


def prove_context(root, recipe, candidate, original, crt):
    cb,cm,cs=candidate
    ids,deps=environment(root,recipe,candidate,original,crt)
    ids['_format']=dict(candidate=symbol(cs,'_format'),original=(0,0x7BF4+142),basis='COMPLETE_SOURCE_OBJECT_BELOW')
    contracts={
      'wbparse': {20:dict(kind='PC',symbol='__OpenLibrary'),24:dict(kind='A4',symbol='_IconBase'),52:dict(kind='PC',symbol='_GetDiskObject'),72:dict(kind='PC',symbol='_FindToolType'),90:dict(kind='PC',symbol='__Open'),126:dict(kind='PC',symbol='__Open'),138:dict(kind='PC',symbol='_FreeDiskObject'),144:dict(kind='A4',symbol='_IconBase'),148:dict(kind='A4',symbol='_CloseLibrary',route=True),152:dict(kind='A4',symbol='_IconBase')},
      'format': {92:dict(kind='PC',symbol='.modu'),96:dict(kind='A4',symbol='FORMAT_LOCAL_DIGITS'),114:dict(kind='PC',symbol='.divu'),334:dict(kind='A4',symbol='_ctp_'),430:dict(kind='A4',symbol='_ctp_'),580:dict(kind='A4',symbol='_strlen',route=True)},
      'printf': {14:dict(kind='PC',symbol='_putchar'),18:dict(kind='PC',symbol='_format')},
    }
    contributions=[]
    for name in ('wbparse','format','printf'):
        spec=SPECS[name];start=symbol(cs,spec['export'])[1]+spec['delta']
        proof=compare_member(candidate,original,spec['original'],start,spec['size'],spec['code_size'],contracts[name],ids)
        entries=sorted((n,o-start) for (h,n),o in cs.items() if h==0 and start<=o<start+spec['size'] and not n.startswith('__H'))
        require(entries==spec['entries'], 'natural runtime complete member exports differ')
        require(start+spec['size']==({'wbparse':symbol(cs,'_printf')[1],'format':symbol(cs,'_strlen')[1],'printf':symbol(cs,'_format')[1]-142}[name]), 'natural runtime next object boundary differs')
        contributions.append(dict(member=name,members=[name],profile='aztec36-x3' if name=='format' else 'aztec36',
           provider='PINNED_SDK_SOURCE' if name=='format' else 'PINNED_LIBRARY_OBJECT',
           original=dict(hunk=0,offset=spec['original'],size=spec['size']),entries=[dict(name=n,offset=o) for n,o in entries],
           owned_data_size=18 if name=='format' else 0,owned_bss_size=0,
           owned_data=ids['FORMAT_LOCAL_DIGITS'] if name=='format' else None,**proof))
    # Prove the allocating consumer rather than inferring that a slot exists.
    hn,start=symbol(cs,'_routing_consumer');require(hn==3, 'natural runtime consumer overlay membership differs')
    consumer=extent(cb,cm,3,start,28)
    ci,err=fc.decode_all(consumer,[]);require(err is None and sum(i.size for i in ci)==28, 'natural runtime complete consumer differs')
    calls=[i for i in ci if i.mnemonic=='jsr']
    require(len(calls)==2 and all(i.bytes[:2]==bytes.fromhex('4eac') for i in calls), 'natural runtime consumer calls are not A4 routes')
    for i,name in zip(calls,('_CloseLibrary','_strlen')):
        target,_=slot_target(cb,cm,int.from_bytes(i.bytes[2:4],'big',signed=True))
        require(target==ids[name]['candidate'], 'natural runtime consumer slot target differs')
    require(object_sizes(read(root,recipe['work']+'/consumer.o'))==(28,0,0), 'natural runtime consumer whole object differs')
    return contributions,dict(identities=ids,dependencies=deps,consumer=dict(hunk=3,offset=start,size=28))


def verify(root, *, recipe=None, original=None):
    root=Path(root).resolve()
    if recipe is None:recipe=json.loads(canonical_path(root,RECIPE).read_text())
    if original is None:
        from analysis_support import game
        b,m,_=game();original=(b,m)
    require(sha256(original[0])==recipe['game_sha256'], 'natural runtime oracle identity differs')
    contexts=producer(root,recipe)
    first,proof=prove_context(root,recipe,contexts['natural'],original,contexts['crt'])
    second,other=prove_context(root,recipe,contexts['reverse'],original,contexts['crt'])
    require(first==second, 'natural runtime independent contexts differ')
    for item in first:
        item['library_sha256']=recipe['tools']['toolchain/installed/aztec-3.6a/SYS1/lib/c.lib']
        item['object_sha256s']={item['member']:recipe['artifacts'][SPECS[item['member']]['object']]}
        item['job_receipt_sha256']=recipe['receipt']['sha256']
        item['natural_recipe_sha256']=RECIPE_DIGEST
    extra,tail_proof=prove_tail_context(root,recipe,contexts['tail_natural'],original,contexts['crt'])
    other_extra,other_tail=prove_tail_context(root,recipe,contexts['tail_reverse'],original,contexts['crt'])
    require([(r['member'],r['original'],r['code_sha256'],r['entries']) for r in extra]==
            [(r['member'],r['original'],r['code_sha256'],r['entries']) for r in other_extra],
            'natural tail independent contexts differ')
    for item in extra:
        item['library_sha256']=recipe['tail']['tools']['toolchain/installed/aztec-3.6a/SYS1/lib/c.lib']
        item['object_sha256s']={item['member']:recipe['tail']['artifacts'][SPECS[item['member']]['object']]}
        item['job_receipt_sha256']=recipe['tail']['receipt']['sha256']
        item['natural_recipe_sha256']=RECIPE_DIGEST
    first.extend(extra)
    return dict(schema_version=1,status='COMPLETE_RUNTIME_CODE_MATCH',game_sha256=recipe['game_sha256'],
                recipe=RECIPE,recipe_sha256=RECIPE_DIGEST,contributions=first,contexts=[proof,other],tail_contexts=[tail_proof,other_tail],
                exact_compiler_release_selected=False,reconstructed_game_functions=0,
                limitations=['No original TU/source filename, DATA/COMMON ownership or complete root layout claimed.',
                             'SDK format source output is not identified as an unchanged archive member.'])


def producer_tail(root, tail):
    """Second producer, within the same curated recipe and natural ledger."""
    request=json.loads(read(root,tail['request']['path']));receipt=json.loads(read(root,tail['receipt']['path']))
    for record in (tail['request'],tail['receipt']):
        require(sha256(read(root,record['path']))==record['sha256'],'natural tail producing receipt changed')
    require(receipt['request']==request and receipt['all_steps_succeeded'] and
            [s['command'] for s in receipt['steps']]==tail['commands']==[s['command'] for s in request['steps']] and
            all(s['returncode']==0 for s in receipt['steps']), 'natural tail producing commands differ')
    job=Path(tail['request']['path']).parent.as_posix()
    require(job.startswith('build/worker-jobs/') and tail['work']==job+'/sys/work','natural tail producer job path differs')
    for path,key in [(job+'/sys/s/startup-sequence','guest_script_sha256'),(job+'/worker.uae','config_sha256'),(job+'/kick.rom','rom_sha256')]:
        require(sha256(read(root,path))==request[key],'natural tail producing environment changed')
    require(sha256(Path(request['emulator']).read_bytes())==request['emulator_sha256'],'natural tail emulator changed')
    sources={s['path']:s for s in request['source_files']}
    require(set(sources)==set(tail['sources'])|{'scan.c','sscanf.c'},'natural tail source inventory differs')
    archive=read(root,tail['sdk']['path']);require(sha256(archive)==tail['sdk']['sha256'],'natural tail SDK changed')
    expected={name:source.encode('ascii') for name,source in tail['sources'].items()}
    for member in ('sscanf','scan'):
        name=member+'.c'
        chunks=[c for c in archive.split(b'\x0c') if c.strip() and c.strip().splitlines()[0].strip()==name.encode()]
        require(len(chunks)==1,'natural tail SDK member differs')
        lines=chunks[0].splitlines(keepends=True);at=next(i for i,line in enumerate(lines) if line.strip()==name.encode())
        expected[name]=b''.join(lines[at+1:]).rstrip(b'\x1a')
    for name,raw in expected.items():
        require(read(root,tail['work']+'/'+name)==raw and sources[name]['sha256']==sha256(raw),'natural tail source does not rederive')
    pins={p['path']:p for p in request['pinned_inputs']}
    for path,digest in tail['tools'].items():
        require(path in pins and pins[path]['sha256']==digest==sha256(pinned(root,path)),'natural tail tool pin differs')
    artifacts={a['path']:a for a in receipt['artifacts']}
    require(len(artifacts)==len(receipt['artifacts']) and set(tail['artifacts'])<=set(artifacts),'natural tail artifact inventory differs')
    for name,digest in tail['artifacts'].items():
        require(Path(name).name==name,'natural tail artifact path differs')
        raw=read(root,tail['work']+'/'+name)
        require(artifacts[name]['sha256']==digest==sha256(raw) and artifacts[name]['size']==len(raw),'natural tail producing artifact changed')
    library=pinned(root,'toolchain/installed/aztec-3.6a/SYS1/lib/c.lib')
    for name in tail['library_objects']:
        require(library.count(read(root,tail['work']+'/'+name))==1,'natural tail complete object not unique in pinned archive')
    for member in TAIL_MEMBERS:
        require(object_sizes(read(root,tail['work']+'/'+SPECS[member]['object']))==
                (SPECS[member]['size'],46 if member=='scan' else 0,6 if member in ('sscanf','scan') else 0),
                'natural tail complete object extent differs')
    for member in ('sscanf','scan'):
        require(object_sizes(read(root,tail['work']+'/'+member+'-source.o'))==object_sizes(read(root,tail['work']+'/'+member+'.o')),
                'natural tail SDK complete object extent differs')
    require(tail['original_bss_claim'] is None and tail['claimed_data_size']==0 and
            all(a['ownership']=='UNKNOWN' and a['allocation_identity'] is None for a in tail['private_accesses'].values()),
            'natural tail cannot claim original storage allocation/ownership')
    result={}
    for prefix in ('natural','reverse','source'):
        b=read(root,tail['work']+'/'+prefix);m=parse(b);sm=symbols(read(root,tail['work']+'/'+prefix+'.sym').decode('ascii'))
        result['tail_'+prefix]=(b,m,sm)
    require(result['tail_natural'][0]==result['tail_source'][0] and result['tail_natural'][2]==result['tail_source'][2],
            'natural tail unchanged SDK source/library whole links differ')
    return result


def private_accesses(root, tail, candidate, original):
    """Bind typed accesses by independent SDK initializers, never BSS ownership.

    Original padding/allocation origin is absent. Whole SDK/library controls
    corroborate candidate private roles; canonical inbound entry and invariant
    parameter/constant stores corroborate original access coordinates. No
    inference from repeated references, adjacent private variables or spacing.
    """
    cb,cm,cs=candidate;ob,om=original;ids={}
    require(anchor(root,tail,'ov04_F_037E',original,356)==(0,SPECS['sscanf']['original']),
            'natural tail sscanf canonical inbound entry changed')
    # The original complete wrapper's transfer independently locates scanfmt.
    s=SPECS['sscanf'];start=symbol(cs,s['export'])[1]
    c=extent(cb,cm,0,start+26,4);o=extent(ob,om,0,s['original']+26,4)
    require(c[:2]==o[:2]==bytes.fromhex('4eba') and
            start+28+int.from_bytes(c[2:],'big',signed=True)==symbol(cs,'_scanfmt')[1] and
            s['original']+28+int.from_bytes(o[2:],'big',signed=True)==SPECS['scan']['original'],
            'natural tail scanfmt entry transfer differs')
    templates={'SSCANF_SCNSTR':(4,'296d0008','\tmove.l\t8(a5),_scnstr'),
               'SSCANF_QUIT':(2,'422c','\tclr.b\t_quit'),
               'SCAN_GSUB':(4,'296d0008','\tmove.l\t8(a5),_gsub'),
               'SCAN_MAXWIDTH':(4,'397c007f','\tmove.w\t#127,_maxwidth')}
    for name,access in tail['private_accesses'].items():
        member=access['member'];spec=SPECS[member];field=access['field'];width,opcode,line=templates[name]
        asm=read(root,tail['work']+'/'+member+'.asm').decode('ascii')
        require(('\tbss\t'+access['sdk_symbol']+','+str(access['size'])) in asm and line in asm,
                'natural tail SDK initializer role differs')
        ct=symbol(cs,spec['export'])[1];ot=spec['original']
        c=extent(cb,cm,0,ct+field-width,width+2);o=extent(ob,om,0,ot+field-width,width+2)
        require(c[:width]==o[:width]==bytes.fromhex(opcode),'natural tail private initializer template differs')
        cp=32766+int.from_bytes(c[width:],'big',signed=True);op=32766+int.from_bytes(o[width:],'big',signed=True)
        require(access['original']==[1,op],'natural tail private original access identity differs')
        cd=next(h for h in cm['hunks'] if h['number']==1);od=next(h for h in om['hunks'] if h['number']==1)
        require(cd['type']==od['type']=='DATA' and cd['initialized_size']<=cp<=cd['allocated_size']-access['size'] and
                od['initialized_size']<=op<=od['allocated_size']-access['size'],'natural tail private access outside zero-fill allocation')
        ids[name]=dict(candidate=(1,cp),original=(1,op),basis='CANONICAL_ENTRY_AND_PINNED_SDK_INITIALIZER_ACCESS',
                       access_size=access['size'],ownership='UNKNOWN',allocation_identity=None)
    return ids


def prove_tail_context(root, recipe, candidate, original, crt):
    tail=recipe['tail'];cb,cm,cs=candidate
    bases=bootstrap(crt,original)
    for name,item in bases.items():item['candidate']=(1,symbol(cs,name)[1])
    ids=dict(bases);dependencies=[]
    # Replay the accepted tail leaf ledger, not majority symbol votes.
    from runtime_tail_members import verify as tail_leaves
    leaf=tail_leaves(root,original=original)
    for row in leaf['contributions']:
        name=row['entries'][0]['name'];spec=row['original'];ct=symbol(cs,name);fields={}
        for field in row['operand_identity']:fields[field['field']]=dict(kind='A4',symbol=field['symbol'])
        proof=compare_member(candidate,original,spec['offset'],ct[1],row['size'],row['size'],fields,ids)
        ids[name]=dict(candidate=ct,original=(0,spec['offset']),basis='REPLAYED_COMPLETE_TAIL_LEAF')
        dependencies.append(dict(member=name,**proof))
    for public,private,size,obj,field,anchor_field in [
        ('_AllocMem','__AllocMem',18,'_allocme.o',12,206),
        ('_FindTask','__FindTask',16,'_findtas.o',10,540),
        ('_FreeMem','__FreeMem',20,'_freemem.o',14,406)]:
        ot=anchor(root,tail,'ov04_F_1E36',original,anchor_field);ct=symbol(cs,public)
        require(symbol(cs,private)==(0,ct[1]+4),'natural tail public/private wrapper pair differs')
        require(object_sizes(read(root,tail['work']+'/'+obj))==(size-4,0,0),'natural tail private wrapper extent differs')
        public_obj={'_AllocMem':'allocmem.o','_FindTask':'findtask.o','_FreeMem':'freemem.o'}[public]
        require(object_sizes(read(root,tail['work']+'/'+public_obj))==(4,0,0),'natural tail public wrapper extent differs')
        ids[private]=dict(candidate=(0,ct[1]+4),original=(0,ot[1]+4),basis='CANONICAL_PUBLIC_ENTRY_AND_COMPLETE_PAIR')
        back=compare_member(candidate,original,ot[1]+4,ct[1]+4,size-4,size-4,{field-4:dict(kind='A4',symbol='_SysBase')},ids)
        front=compare_member(candidate,original,ot[1],ct[1],4,4,{2:dict(kind='PC',symbol=private)},ids)
        ids[public]=dict(candidate=ct,original=ot,basis='CANONICAL_PUBLIC_ENTRY_AND_COMPLETE_PAIR')
        dependencies.extend([dict(member=public,**front),dict(member=private,**back)])
    ids['_exit']=dict(candidate=symbol(cs,'_exit'),original=anchor(root,tail,'ov04_F_1E36',original,754),basis='CANONICAL_EXIT_ENTRY')
    for name,size,obj in [('_index',26,'index.o'),('.mulu',36,'lmul.o')]:
        ids[name]=raw_leaf(candidate,original,name,size,obj,root,tail)
    ids['_ctp_']=bind_data(candidate,original,'_ctp_',130,'ctype.o',root,tail)
    # Anonymous scan initializer is checked complete, without accepting DATA.
    cp=symbol(cs,'_ctp_')[1]-46;raw=extent(cb,cm,1,cp,46)
    want=b'ABCDEFabcdef9876543210\0'+bytes([10,11,12,13,14,15]*2+list(range(9,-1,-1)))+b'\0'
    require(raw==want and not relocations(cm,1,cp,46),'natural tail complete scan initializer differs')
    ob,om=original;h=next(h for h in om['hunks'] if h['number']==1)
    op=unique(extent(ob,om,1,0,h['initialized_size']),raw)
    require(not relocations(om,1,op,46),'natural tail original scan initializer relocation differs')
    ids['SCAN_LOCAL_DATA']=dict(candidate=(1,cp),original=(1,op),basis='UNIQUE_COMPLETE_PINNED_DATA_PAYLOAD',size=46,sha256=sha256(raw),claimed_size=0)
    ids.update(private_accesses(root,tail,candidate,original))
    for member in TAIL_MEMBERS:
        spec=SPECS[member];start=symbol(cs,spec['export'])[1]
        for name,off in spec['entries']:
            require(symbol(cs,name)==(0,start+off),'natural tail complete object export differs')
            ids[name]=dict(candidate=(0,start+off),original=(0,spec['original']+off),basis='COMPLETE_PINNED_MEMBER_GRAPH')
    members=[]
    for member in TAIL_MEMBERS:
        spec=SPECS[member];start=symbol(cs,spec['export'])[1]
        fields={int(k):v for k,v in tail['contracts'][member].items()}
        proof=compare_member(candidate,original,spec['original'],start,spec['size'],spec['code_size'],fields,ids)
        entries=sorted(((n,off-start) for (h,n),off in cs.items() if h==0 and start<=off<start+spec['size'] and not n.startswith('__H')),key=lambda row:(row[1],row[0]))
        require(entries==spec['entries'],'natural tail complete member entries differ')
        # Every complete member ends at the next object, with no clipping.
        following={'sscanf':'_scanfmt','scan':'__abort','abort':'_CreatePort','createpo':'_CreateStdIO','createst':'_CreateExtIO'}
        boundary=symbol(cs,following[member])[1] if member in following else min(off for (h,n),off in cs.items() if h==0 and off>=start+spec['size'])
        require(start+spec['size']==boundary,'natural tail natural complete object boundary differs')
        members.append(dict(member=member,members=[member],profile='aztec36',provider='PINNED_LIBRARY_OBJECT',
            original=dict(hunk=0,offset=spec['original'],size=spec['size']),entries=[dict(name=n,offset=o) for n,o in entries],
            candidate_owned_data_size=46 if member=='scan' else 0,candidate_owned_bss_size=6 if member in ('sscanf','scan') else 0,
            owned_data_size=None if member=='scan' else 0,owned_bss_size=None if member in ('sscanf','scan') else 0,
            accepted_storage_size=0,storage_ownership='UNKNOWN' if member in ('sscanf','scan') else 'NO_OWNED_STORAGE',**proof))
    # Actual compiled overlay consumer allocates all six shared routes.
    hn,start=symbol(cs,'_tail_consumer');size=object_sizes(read(root,tail['work']+'/consumer.o'))[0]
    require(hn==3 and size==86,'natural tail allocating consumer complete extent differs')
    consumer=extent(cb,cm,hn,start,size);ins,err=fc.decode_all(consumer,[])
    require(err is None and sum(i.size for i in ins)==size,'natural tail consumer incomplete decode')
    calls=[i for i in ins if i.mnemonic=='jsr']
    require(len(calls)==6 and all(i.bytes[:2]==bytes.fromhex('4eac') for i in calls),'natural tail consumer routes differ')
    for i,name in zip(calls,('_AllocMem','_FindTask','_FreeMem','_index','_exit','.mulu')):
        actual,_=slot_target(cb,cm,int.from_bytes(i.bytes[2:4],'big',signed=True))
        require(actual==ids[name]['candidate'],'natural tail allocating consumer target identity differs')
    return members,dict(identities=ids,dependencies=dependencies,consumer=dict(hunk=hn,offset=start,size=size))
