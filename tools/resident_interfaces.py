"""Evidence-derived named resident DATA call interfaces; no CODE bytes supplied.

External harness bodies remain ordinary function-level stand-ins. Linked unit
members keep their real CODE symbol; an overlay control makes Manx emit their
root DATA JMP slot. Both routes prove the complete slot and its CODE relocation.
"""
import re
from pathlib import Path
from common import require, sha256

FIELD='resident_data_interfaces'
FUNCTION=r'(?:(?:unsigned|signed)\s+)?(?:int|long|short|char|void)\s+(F_h00_[0-9A-Fa-f]+)\s*\(\s*\)'

CONTROL='resident_slot_export_control'
_routes={}
_installed=False


def original_a4_bias(blob,model):
    root=next(h for h in model['hunks'] if h['number']==0)
    values=[]
    for r in model['relocations']:
        p=root['content_offset']+r['source_offset']
        if r['source_hunk']==0 and r['target_hunk']==1 and r['type']=='HUNK_RELOC32' and r['width']==4 and \
                blob[p-2:p]==b'\x49\xf9' and blob[p+4:p+6]==b'\x4e\x75':
            values.append(r['addend_raw'])
    require(len(set(values))==1,'original resident A4 bias is not independently established')
    return values[0]


def declarations(source):
    clean=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"', '', source, flags=re.S)
    result={}
    for m in re.finditer(r'\bextern\s+([^;{}]+);',clean):
        match=re.fullmatch(FUNCTION,m[1].strip())
        if match:
            name=match[1]
            require(name not in result or result[name]==m[1].strip(), 'conflicting resident interface declarations')
            result[name]=m[1].strip()
    return result


def defines(source,name):
    """Recognize the unit member's ordinary old-style C definition, not an extern."""
    clean=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"', '', source, flags=re.S)
    parameters=r'(?:(?:(?:unsigned|signed|register)\s+)*(?:int|long|short|char|void|struct\s+\w+)\s+[^;{}]+;\s*)*'
    return re.search(r'\b'+re.escape(name)+r'\s*\([^;{}]*\)\s*'+parameters+r'\{',clean) is not None


def derive(functions,source,blob,model,a4_bias):
    """Select declared functions whose decoded calls use a real DATA jump entry."""
    from analysis_support import K
    from function_compare import decode_all
    declared=declarations(source);members={}
    if not declared:return None
    data=next(h for h in model['hunks'] if h['number']==1)
    code=next(h for h in model['hunks'] if h['number']==0)
    for f in functions:
        if f['hunk']!=0:continue
        raw_function=blob[code['content_offset']+f['start']:code['content_offset']+f['end']]
        require(sha256(raw_function)==f['sha256'],'resident DATA interface function evidence changed')
        spans=[(t['table_start']-f['start'],t['table_end']-f['start']) for t in f.get('jump_tables',[])]
        decoded,bad=decode_all(raw_function,spans)
        require(bad is None,'resident interface source function is not completely decoded')
        for ins in decoded:
            if ins.mnemonic.split('.')[0] not in ('jsr','jmp'):continue
            operands=[o for o in ins.operands if o.type==K.M68K_OP_MEM and
                      o.mem.base_reg==K.M68K_REG_A4 and o.address_mode==K.M68K_AM_REGI_ADDR_DISP]
            if not operands:continue
            require(len(operands)==1,'resident DATA call is ambiguous')
            site=f['start']+ins.address;stub=a4_bias+operands[0].mem.disp
            require(0<=stub and stub+6<=data['initialized_size'],'resident DATA interface is not initialized')
            raw=blob[data['content_offset']+stub:data['content_offset']+stub+6]
            rr=[r for r in model['relocations'] if r['source_hunk']==1 and
                r['source_offset']<stub+6 and r['source_offset']+r['width']>stub]
            # Only an explicit CODE mechanical extern can select this route.
            target=int.from_bytes(raw[2:],'big');name='F_h00_%04X'%target
            if name not in declared:continue
            call=next((c for c in f.get('direct_callees',[]) if c['site']==site),None)
            if 'direct_callees' in f:
                require(call is not None and call['hunk']==0 and call['offset']==target,
                        'resident DATA interface disagrees with decoded call evidence')
            require(raw[:2]==b'\x4e\xf9' and len(rr)==1 and rr[0]['source_offset']==stub+2 and
                    rr[0]['type']=='HUNK_RELOC32' and rr[0]['width']==4 and rr[0]['target_hunk']==0 and
                    rr[0]['addend_raw']==target,
                    'original resident DATA call lacks a unique complete JMP/CODE relocation')
            member=dict(name=name,body='resident_body_'+name,hunk=0,start=target,
                        data_hunk=1,data_offset=stub,payload_sha256=sha256(raw),sites=[])
            prior=members.setdefault(name,member)
            require(all(prior[k]==member[k] for k in member if k!='sites'),'resident DATA call has conflicting interfaces')
            prior['sites'].append(dict(id=f['id'],start=f['start'],sha256=f['sha256'],offset=site))
    if not members:return None
    for member in members.values():
        name=member['name']
        # A real definition, independently present in the unit's member list.
        # The entry is named recovered and cannot accidentally select this route.
        if any(f['hunk']==0 and f['start']==member['start'] for f in functions) and \
                defines(source,name):
            member.update(binding='LINKED_MEMBER',body=name)
    recipe=dict(executable_sha256=sha256(blob),source_sha256=sha256(source.encode('ascii')),
                members=[dict(m,sites=sorted(m['sites'],key=lambda s:(s['id'],s['offset'])))
                         for _,m in sorted(members.items())])
    register(source,recipe)
    return recipe


def validate(recipe,source=None,target_node=0,local_functions=None):
    if recipe is None:return
    require(target_node==0,'resident DATA interfaces require the root node')
    require(isinstance(recipe,dict) and set(recipe)=={'executable_sha256','source_sha256','members'},'invalid resident DATA interface recipe')
    require(all(isinstance(recipe[k],str) and re.fullmatch('[0-9a-f]{64}',recipe[k])
                for k in ('executable_sha256','source_sha256')),'invalid resident DATA interface hashes')
    require(isinstance(recipe['members'],list) and recipe['members'],'empty resident DATA interface recipe')
    declared=declarations(source) if source is not None else None
    if source is not None:require(sha256(source.encode('ascii'))==recipe['source_sha256'],'resident DATA interface source identity differs')
    seen=set();locations=set()
    for m in recipe['members']:
        linked=isinstance(m,dict) and m.get('binding')=='LINKED_MEMBER'
        require(isinstance(m,dict) and set(m)=={'name','body','hunk','start','data_hunk','data_offset','payload_sha256','sites'}|({'binding'} if linked else set()),
                'invalid resident DATA interface member')
        require(type(m['start']) is int and m['start']>=0 and m['hunk']==0 and m['data_hunk']==1 and
                type(m['data_offset']) is int and m['data_offset']>=0 and
                m['name']=='F_h00_%04X'%m['start'] and m['body']==(m['name'] if linked else 'resident_body_'+m['name']) and
                m['name'] not in seen and m['data_offset'] not in locations,
                'resident DATA interface is not a unique root member')
        if local_functions is not None:
            require((m['name'] in local_functions)==linked,
                    'resident DATA interface linked-member binding disagrees with local functions')
        require(isinstance(m['payload_sha256'],str) and re.fullmatch('[0-9a-f]{64}',m['payload_sha256']),
                'invalid resident DATA interface payload identity')
        if declared is not None:
            require(m['name'] in declared and ((linked and defines(source,m['name'])) or (not linked and not re.search(r'\b'+re.escape(m['body'])+r'\b',source))),
                    'resident DATA interface needs an explicit external function and distinct body')
        require(isinstance(m['sites'],list) and m['sites'],'resident DATA interface needs decoded call sites')
        sites=set()
        for s in m['sites']:
            require(isinstance(s,dict) and set(s)=={'id','start','sha256','offset'} and
                    type(s['start']) is int and s['start']>=0 and type(s['offset']) is int and s['offset']>=s['start'] and
                    s['id']=='resident_F_%04X'%s['start'] and isinstance(s['sha256'],str) and
                    re.fullmatch('[0-9a-f]{64}',s['sha256']) and (s['id'],s['offset']) not in sites,
                    'invalid resident DATA interface call site')
            sites.add((s['id'],s['offset']))
        seen.add(m['name']);locations.add(m['data_offset'])


def definition(decl,member):
    """Ordinary C fields encode a real six-byte absolute JMP in small-int ABI."""
    name=member['name'];body=member['body']
    renamed=decl.replace(name,body)
    return (renamed+(' { }' if decl.startswith('void ') else ' { return 0; }')+'\n'+
            'struct resident_jump_'+name+' { unsigned short opcode; int (*body)(); };\n'+
            'struct resident_jump_'+name+' '+name+' = { 0x4ef9, '+body+' };')


def register(source,recipe):
    """Opt-in linker control, like helper_exports; candidate objects are untouched."""
    names=tuple(m['name'] for m in recipe['members'] if m.get('binding')=='LINKED_MEMBER')
    if not names:return
    require(_routes.get(source,names)==names,'one source has conflicting resident slot exports')
    _routes[source]=names
    install()


def install():
    global _installed
    if _installed:return
    import sys
    import compiler_oracle
    base_harness,base_proxies=compiler_oracle.harness,compiler_oracle.overlay_proxies
    def harness(source,target_node=1,local_functions=(),entry_function='recovered',same_overlay_exports=None,resident_data_interfaces=None):
        text=base_harness(source,target_node,local_functions,entry_function,same_overlay_exports,resident_data_interfaces)
        if target_node==0 and any(m.get('binding')=='LINKED_MEMBER' for m in (resident_data_interfaces or {}).get('members',[])):
            text+=('/* Linked resident member slot export control. */\nextern int '+CONTROL+'();\n'
                   'int (*resident_slot_export_reference)() = '+CONTROL+';\n')
        return text
    def overlay_proxies(source,target_node):
        proxies=base_proxies(source,target_node)
        names=_routes.get(source,()) if target_node==0 else ()
        if names:
            require(all(p['name']!=CONTROL for p in proxies),'resident slot export control name collides')
            text=''.join('extern int '+name+'();\n' for name in names)
            text+=CONTROL+'() {\n'+''.join('    '+name+'();\n' for name in names)+'    return 0;\n}\n'
            proxies=proxies+[dict(name=CONTROL,hunk=3,node=1,source=text)]
        return proxies
    compiler_oracle.harness,compiler_oracle.overlay_proxies=harness,overlay_proxies
    for name in ('queued_oracle','mixed_profile_oracle','resident_mixed'):
        module=sys.modules.get(name)
        if module is not None:
            if getattr(module,'harness',None) is base_harness:module.harness=harness
            if getattr(module,'overlay_proxies',None) is base_proxies:module.overlay_proxies=overlay_proxies
    _installed=True


def extract(recipe,blob,model,symbols):
    """Validate emitted payload, callable symbol, and unique distinct CODE body."""
    validate(recipe)
    data=next(h for h in model['hunks'] if h['number']==1);code=next(h for h in model['hunks'] if h['number']==0)
    result=[]
    for member in recipe['members']:
        bodies=[(h,v) for (h,n),v in symbols.items() if n=='_'+member['body']]
        if member.get('binding')=='LINKED_MEMBER':
            require(len(bodies)==1 and bodies[0][0]==0,'resident DATA interface linked CODE member symbol differs')
            # Manx's root slots have no DATA symbol. Select the unique JMP
            # relocation to the actual member, never a substitute CODE body.
            entries=[(1,r['source_offset']-2) for r in model['relocations']
                     if r['source_hunk']==1 and r['target_hunk']==0 and r['type']=='HUNK_RELOC32' and
                     r['width']==4 and r['addend_raw']==bodies[0][1] and r['source_offset']>=2 and
                     blob[data['content_offset']+r['source_offset']-2:data['content_offset']+r['source_offset']]==b'\x4e\xf9']
        else:
            entries=[(h,v) for (h,n),v in symbols.items() if n=='_'+member['name']]
        require(len(entries)==len(bodies)==1 and entries[0][0]==1 and bodies[0][0]==0,
                'resident DATA interface callable/body symbols differ')
        stub=entries[0][1];body=bodies[0][1]
        require(0<=stub and stub+6<=data['initialized_size'] and 0<=body<code['initialized_size'],
                'resident DATA interface payload/body outside initialized hunks')
        raw=blob[data['content_offset']+stub:data['content_offset']+stub+6]
        rr=[r for r in model['relocations'] if r['source_hunk']==1 and
            r['source_offset']<stub+6 and r['source_offset']+r['width']>stub]
        require(raw[:2]==b'\x4e\xf9' and int.from_bytes(raw[2:],'big')==body and len(rr)==1 and
                rr[0]['source_offset']==stub+2 and rr[0]['type']=='HUNK_RELOC32' and rr[0]['width']==4 and
                rr[0]['target_hunk']==0 and rr[0]['addend_raw']==body,
                'resident DATA interface is not a complete JMP with a unique mapped CODE relocation')
        result.append(dict(name=member['name'],body=member['body'],hunk=1,offset=stub,
                           target_hunk=0,target_offset=body,payload_sha256=sha256(raw),
                           original_hunk=0,original_offset=member['start']))
    return result


def local_call_issues(function,contribution,recipe,blob):
    """Bind each original slot site to the validated emitted slot, not any pointer.

    Called on a complete member (or the independently reduced behavioral member).
    The ordinary comparator still proves instruction shape and CODE target identity.
    """
    members=[m for m in (recipe or {}).get('members',[]) if m.get('binding')=='LINKED_MEMBER']
    sites=[(m,s) for m in members for s in m['sites'] if s['id']==function['id']]
    if not sites:return []
    model=dict(hunks=contribution['hunks'],relocations=contribution['all_relocations'])
    symbols={(s['hunk'],s['name']):s['offset'] for s in contribution['symbols']}
    emitted=extract(recipe,blob,model,symbols)
    bias=original_a4_bias(blob,model)
    raw=bytes.fromhex(contribution['code_hex']);issues=[]
    for member,site in sites:
        at=site['offset']-function['start']
        slot=next(e for e in emitted if e['name']==member['name'])
        stub=bias+int.from_bytes(raw[at+2:at+4],'big',signed=True)
        if raw[at:at+2] not in (b'\x4e\xac',b'\x4e\xec') or stub!=slot['offset']:
            issues.append(dict(kind='LINKED_MEMBER_SLOT',offset=at,name=member['name'],
                               expected_slot=slot['offset'],actual_slot=stub))
    return issues


def provenance():
    return sha256(Path(__file__).read_bytes())


def validate_provenance(compiler):
    # These hashes identify the historical producer, not acceptance. Current
    # recipe/harness re-derivation and cached artifact extraction remain strict.
    require(all(isinstance(compiler.get(k),str) and re.fullmatch('[0-9a-f]{64}',compiler[k])
                for k in ('resident_interface_producer_sha256','resident_interface_extractor_sha256')),
            'invalid resident DATA interface producer provenance')


def evidence(functions,source,compiler,blob,model,a4_bias,unit=None):
    """Strict proof boundary: independently re-derive every optional recipe."""
    if FIELD not in compiler and (unit is None or FIELD not in unit):
        require('resident_interface_producer_sha256' not in compiler and
                'resident_interface_extractor_sha256' not in compiler,
                'resident DATA interface producer lacks its recipe')
        if compiler.get('candidate_overlay_node')==0:
            from compiler_oracle import harness
            text=harness(source,0,compiler.get('local_functions',()),compiler.get('entry_function','recovered'))
            require(sha256(text.encode('ascii'))==compiler.get('harness_sha256'),
                    'resident DATA interface harness hash does not re-derive')
        return None
    expected=derive(functions,source,blob,model,a4_bias)
    require(expected is not None and compiler.get(FIELD)==expected and
            (unit is None or unit.get(FIELD)==expected),
            'resident DATA interfaces do not re-derive from original calls and source')
    validate_provenance(compiler)
    from compiler_oracle import harness
    text=harness(source,compiler.get('candidate_overlay_node',1),compiler.get('local_functions',()),
                 compiler.get('entry_function','recovered'),compiler.get('same_overlay_exports'),expected)
    require(sha256(text.encode('ascii'))==compiler.get('harness_sha256'),
            'resident DATA interface harness hash does not re-derive')
    return expected
