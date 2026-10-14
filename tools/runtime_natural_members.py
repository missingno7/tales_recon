"""Opt-in complete natural runtime objects with independently checked operands.

Only the curated 3.6a recipe is supported. No masks, opcode conversions,
linked-output edits, guessed slot votes, or historical release selection.
"""
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
RECIPE_DIGEST = 'a617b42cbfe2f265f12aea439f4af58ffc00d69e352f59d8e36bb8488840e8f5'
OUTPUT = 'evidence/experiments/runtime-members-natural.json'
SPECS = {
 'wbparse': dict(object='wbparse.o', export='__wb_parse', delta=0, size=180, code_size=158, original=0x7B24, entries=[('__wb_parse',0)]),
 'format': dict(object='format.o', export='_format', delta=-142, size=936, code_size=936, original=0x7BF4, entries=[('_format',142)]),
 'printf': dict(object='printf.o', export='_printf', delta=0, size=28, code_size=28, original=0x7BD8, entries=[('_printf',0)]),
}


def read(root, path):
    return candidate_path(root, Path(root)/path).read_bytes()


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
    resolved=bytearray(raw);seen=set();proof=[]
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
            # Comparison buffer only; emitted artifacts are never rewritten.
            resolved[field:field+2]=expected[field:field+2]
            proof.append(dict(site=c.address,field=field,width=2,kind=ck,symbol=name,addend=addend,
                              candidate=list(actual),original=list(want),**slot_proof))
    require(seen==set(fields), 'natural runtime operand contract not exhausted')
    require(bytes(resolved)==expected, 'natural runtime whole member bytes differ')
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
    for name,spec in SPECS.items():
        require(object_sizes(read(root,directory+'/'+spec['object']))==(spec['size'],18 if name=='format' else 0,0), 'natural runtime whole object size differs')
    result={}
    for prefix in ('natural','reverse','crt'):
        b=read(root,directory+'/'+prefix);m=parse(b);sm=symbols(read(root,directory+'/'+prefix+'.sym').decode('ascii'))
        result[prefix]=(b,m,sm)
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
    return dict(schema_version=1,status='COMPLETE_RUNTIME_CODE_MATCH',game_sha256=recipe['game_sha256'],
                recipe=RECIPE,recipe_sha256=RECIPE_DIGEST,contributions=first,contexts=[proof,other],
                exact_compiler_release_selected=False,reconstructed_game_functions=0,
                limitations=['No original TU/source filename, DATA/COMMON ownership or complete root layout claimed.',
                             'SDK format source output is not identified as an unchanged archive member.'])
