"""Evidence-derived named resident DATA call interfaces; no CODE bytes supplied.

The harness bodies remain ordinary function-level stand-ins.  This recipe proves
only the call route: an authored JMP record in DATA points to a distinct CODE
body, and the callable mechanical symbol names that record itself.
"""
import re
from pathlib import Path
from common import require, sha256

FIELD='resident_data_interfaces'
FUNCTION=r'(?:(?:unsigned|signed)\s+)?(?:int|long|short|char|void)\s+(F_h00_[0-9A-Fa-f]+)\s*\(\s*\)'


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
    return dict(executable_sha256=sha256(blob),source_sha256=sha256(source.encode('ascii')),
                members=[dict(m,sites=sorted(m['sites'],key=lambda s:(s['id'],s['offset'])))
                         for _,m in sorted(members.items())])


def validate(recipe,source=None,target_node=0,local_functions=()):
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
        require(isinstance(m,dict) and set(m)=={'name','body','hunk','start','data_hunk','data_offset','payload_sha256','sites'},
                'invalid resident DATA interface member')
        require(type(m['start']) is int and m['start']>=0 and m['hunk']==0 and m['data_hunk']==1 and
                type(m['data_offset']) is int and m['data_offset']>=0 and
                m['name']=='F_h00_%04X'%m['start'] and m['body']=='resident_body_'+m['name'] and
                m['name'] not in seen and m['data_offset'] not in locations and m['name'] not in local_functions,
                'resident DATA interface is not a unique external root member')
        require(isinstance(m['payload_sha256'],str) and re.fullmatch('[0-9a-f]{64}',m['payload_sha256']),
                'invalid resident DATA interface payload identity')
        if declared is not None:
            require(m['name'] in declared and not re.search(r'\b'+re.escape(m['body'])+r'\b',source),
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


def extract(recipe,blob,model,symbols):
    """Validate emitted payload, callable symbol, and unique distinct CODE body."""
    validate(recipe)
    data=next(h for h in model['hunks'] if h['number']==1);code=next(h for h in model['hunks'] if h['number']==0)
    result=[]
    for member in recipe['members']:
        entries=[(h,v) for (h,n),v in symbols.items() if n=='_'+member['name']]
        bodies=[(h,v) for (h,n),v in symbols.items() if n=='_'+member['body']]
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


def provenance():
    return sha256(Path(__file__).read_bytes())


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
    require(compiler.get('resident_interface_producer_sha256')==provenance(),
            'stale resident DATA interface producer identity')
    from compiler_oracle import harness
    require(compiler.get('resident_interface_extractor_sha256')==sha256(Path(__file__).with_name('compiler_oracle.py').read_bytes()),
            'stale resident DATA interface extractor identity')
    text=harness(source,compiler.get('candidate_overlay_node',1),compiler.get('local_functions',()),
                 compiler.get('entry_function','recovered'),compiler.get('same_overlay_exports'),expected)
    require(sha256(text.encode('ascii'))==compiler.get('harness_sha256'),
            'resident DATA interface harness hash does not re-derive')
    return expected
