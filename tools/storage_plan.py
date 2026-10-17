"""Resident storage interpretation. No initializers, allocation emission or proof credit."""
from collections import defaultdict
import ast
import hashlib
import json
from pathlib import Path
import re

from common import require, FormatError
import declaration_views as dv
import data_model as dm
from repo_paths import active_files, is_active_repo_path

NAME = re.compile(r'(?<!\w)_?(G_h(01|02)_([0-9A-F]{4}))(?!\w)')
DEFINITION = re.compile(
    r'(?:^|[;\n])\s*((?:(?:unsigned|signed)\s+)?(?:char|short|int|long|float)'
    r'|struct\s+\w+)\s+(\**\s*)(G_h(?:01|02)_[0-9A-F]{4})'
    r'\s*((?:\[\s*\d*\s*\]\s*)*)\s*(?=[=;])', re.M)
POLICY = ('Storage interpretation only; no proof, ownership or initializer credit. '
          'BOUNDED means independently supported access-domain extent, not historical '
          'TU/allocation provenance. UNBOUNDED ranges are measured link gaps, never '
          'permission to emit opaque arrays or padding. Private array extents are views.')


def coordinate(name):
    m = NAME.fullmatch(name) if isinstance(name,str) else None
    require(m is not None, 'invalid resident storage name: ' + str(name))
    return int(m[2]), int(m[3], 16)


def clean(text, assembly=False):
    if assembly:
        text=re.sub(r'(?m)^\s*\*[^\n]*','',text)
        return re.sub(r';[^\n]*', '', text)
    token = re.compile(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27', re.S)
    return token.sub(lambda m: ''.join('\n' if c=='\n' else ' ' for c in m[0]),text)


def view_extent(view, structs):
    return dv.view_extent('long' + view[5:] if view.startswith('float') else view, structs)


def source_views(text):
    """Keep all alternatives; float support is local, with no parser monkeypatch."""
    declarations, structs, bad = dv.parse_source(clean(text))
    for statement in bad:
        match = re.fullmatch(r'float\s+(.+)', statement)
        parts = [dv.DECLARATOR_RE.fullmatch(p.strip()) for p in match[1].split(',')] if match else []
        if parts and all(parts):
            declarations.extend(dict(name=p['name'], kind='data',
                view=dv._view('float', p['ptr'], p['dims'])) for p in parts)
        else:
            declarations.extend(dict(name=m[1], kind='data', view='UNPARSED: ' + statement)
                                for m in NAME.finditer(statement))
    for m in DEFINITION.finditer(clean(text)):
        declarations.append(dict(name=m[3], kind='data', view=dv._view(m[1], m[2], m[4])))
    # Resolve a local function-pointer typedef without assuming its spelling.
    for t in re.finditer(r'\btypedef\s+([^;()]+?)\s*\(\s*\*\s*(\w+)\s*\)\s*\(\s*\)\s*;',clean(text)):
        pattern=r'\b'+re.escape(t[2])+r'\s+(G_h(?:01|02)_[0-9A-F]{4})\s*((?:\[\d+\]\s*)*)\s*(?=[=;])'
        for m in re.finditer(pattern,clean(text)):
            declarations.append(dict(name=m[1],kind='data',
                view=' '.join(t[1].split())+' (*)()'+(' '+m[2].strip() if m[2].strip() else '')))
    return declarations, structs


def private_layout(view, structs):
    result, todo = {}, re.findall(r'\bstruct\s+(\w+)', view)
    while todo:
        tag = todo.pop()
        if tag not in result and tag in structs:
            result[tag] = structs[tag]
            todo.extend(re.findall(r'\bstruct\s+(\w+)', structs[tag]))
    return result


def collect(root, curation=None):
    """Read active sources and existing evidence. Never read oracle payload files."""
    root = Path(root)
    files = {p.relative_to(root).as_posix(): p.read_text(encoding='ascii')
             for p in active_files(root / 'src') if p.suffix.lower() in ('.c','.s','.asm','.a68')}
    hunks = json.loads((root / 'evidence/executable/hunks.json').read_text())['hunks']
    regions = []
    for h in hunks:
        if h['number'] not in (1,2):
            continue
        if h['initialized_size']:
            regions.append(dict(hunk=h['number'],start=0,end=h['initialized_size'],
                                kind='DATA',memory_flags=h['memory_flags_raw']))
        if h['zero_fill_size']:
            regions.append(dict(hunk=h['number'],start=h['initialized_size'],end=h['allocated_size'],
                                kind='BSS',memory_flags=h['memory_flags_raw']))
    document = json.loads((root / 'evidence/types.json').read_text())
    from type_evidence import evidence_staleness
    stale = evidence_staleness(document,root)
    require(not stale, '; '.join(stale))
    # Do not retain the instruction encodings present in the evidence document.
    widths = {g['data_hunk_offset']:dict(
        widths=sorted({a['width_bytes'] for a in g['accesses'] if a['width_bytes']}),
        sites=[dict(function=a['function'],hunk=a['hunk'],offset=a['offset'],
                    width=a['width_bytes'],direction=a['direction'])
               for a in g['accesses'] if a['width_bytes']],
        address_taken=len(g['address_taken'])) for g in document['globals']}
    model = json.loads((root / dm.MODEL).read_text())
    source_by_id = {}
    def walk(row,key=None):
        if isinstance(row,dict):
            if isinstance(row.get('source'),str) and row['source'].startswith('src/'):
                source_by_id[key] = row['source']
            for k,value in row.items():
                walk(value,k)
        elif isinstance(row,list):
            for value in row:
                walk(value)
    walk(json.loads((root / 'recovery/ledger.json').read_text()))
    providers = []
    for p in json.loads((root / 'evidence/data-providers/accepted.json').read_text())['objects']:
        original = p['original']
        if original['hunk'] not in (1,2):
            continue
        candidates = [s for s in files if Path(s).stem == p['id']]
        if p['id'] in source_by_id:
            candidates.append(source_by_id[p['id']])
        candidates = [s for s in sorted(set(candidates)) if is_active_repo_path(root/s,root)
                      and hashlib.sha256((root/s).read_bytes()).hexdigest() == p['source_sha256']]
        require(len(candidates)==1,p['id']+': unique hash-bound source required')
        require(p['state']=='DATA_LAYOUT_MATCH' and p['typed_evidence'],p['id']+': typed provider required')
        providers.append(dict(id=p['id'],source=candidates[0],hunk=original['hunk'],
            start=original['start'],size=original['size'],
            symbols=[dict(name=s['name'].lstrip('_'),offset=s['offset']) for s in p['symbols']],
            evidence_kinds=sorted({str(e.get('kind',e.get('type','TYPED_PROVIDER'))) for e in p['typed_evidence']})))
    external_evidence={}
    for rule in (curation or {}).get('external_bindings',[]):
        relative=rule['artifact']
        path=Path(relative)
        require(not path.is_absolute() and '..' not in path.parts and
                path.parts[0] in ('src','recovery','evidence','docs') and
                is_active_repo_path(root/path,root),'inactive/external binding evidence path')
        external_evidence[relative]=(root/path).read_text(encoding='utf-8')
    return dict(external_evidence=external_evidence,a4_bias=document['inputs']['a4_bias_evidence']['relocation']['addend_raw'],
                regions=regions,sources=files,widths=widths,providers=providers,model=model,names=json.loads((root / 'recovery/names.json').read_text()).get('globals',{}))


def declarations(facts):
    grouped,identities,layouts,definitions = defaultdict(dict),defaultdict(set),{},{}
    for source,text in sorted(facts['sources'].items()):
        assembly = Path(source).suffix.lower() != '.c'
        used = {m[1] for m in NAME.finditer(clean(text,assembly))}
        for name in used:
            identities[name].add(source)
        if assembly:
            continue
        decls,structs = source_views(text)
        definitions[source] = structs
        for d in decls:
            name,view = d['name'],d['view']
            if name not in used or not NAME.fullmatch(name) or d['kind']!='data':
                continue
            ids = []
            for tag,body in sorted(private_layout(view,structs).items()):
                token = tag+':'+hashlib.sha256(body.encode()).hexdigest()[:16]
                layouts.setdefault(token,dict(tag=tag,body=body,sources=[]))['sources'].append(source)
                ids.append(token)
            if view.startswith(('UNPARSED:','UNKNOWN')):
                size = None
            elif ' (*)()' in view:
                size=4
                for n in re.findall(r'\[(\d+)\]',view):
                    size*=int(n)
            else:
                size = view_extent(view,structs)
            row = grouped[name].setdefault((view,tuple(ids)),dict(type=view,private_layouts=ids,
                declared_extent=size,sources=[]))
            row['sources'].append(source)
    for name,sources in identities.items():
        supplied = {s for v in grouped[name].values() for s in v['sources']}
        if sources-supplied:
            grouped[name][('UNKNOWN',())] = dict(type='UNKNOWN',private_layouts=[],
                declared_extent=None,sources=sorted(sources-supplied))
    for row in layouts.values():
        row['sources'] = sorted(set(row['sources']))
    return ({n:[dict(v,sources=sorted(set(v['sources']))) for _,v in sorted(rows.items())]
             for n,rows in sorted(grouped.items())},dict(sorted(layouts.items())),definitions)


def capture(extractor,facts,allow_zero=False):
    require({'source','pattern'} <= set(extractor) <= {'source','pattern','radix','offset'},'numeric extractor keys')
    radix=extractor.get('radix',10)
    # offset: e.g. +1 for a DBRA loop counter, whose loop runs counter+1 times.
    offset=extractor.get('offset',0)
    require(type(offset) is int,'extractor offset must be an integer')
    require(type(radix) is int and radix in (10,16),'extractor radix must be 10 or 16')
    source = extractor['source']
    require(source in facts['sources'],'missing storage bound source: '+source)
    found = re.findall(extractor['pattern'],clean(facts['sources'][source]),re.S)
    require(found and all(isinstance(v,str) and re.fullmatch(r'[0-9]+' if radix==10 else r'[0-9A-Fa-f]+',v) for v in found),
            source+': numeric storage evidence missing/ambiguous')
    values = {int(v,radix) for v in found}
    require(len(values)==1 and min(values)+offset>=(0 if allow_zero else 1),source+': conflicting numeric storage evidence')
    return values.pop()+offset


def check_dependencies(curation,facts):
    for note in curation['dependencies']:
        require(set(note)=={'symbols','constraint','evidence','coallocate'},'storage dependency keys')
        require(note['symbols'] and note['constraint'].strip() and note['evidence'],'empty dependency')
        require(type(note['coallocate']) is bool,'coallocate must be boolean')
        for name in note['symbols']:
            coordinate(name)
        for e in note['evidence']:
            require(set(e)=={'source','text'},'source evidence keys')
            require(e['source'] in facts['sources'] and e['text'].strip()
                    and e['text'] in facts['sources'][e['source']],'stale storage dependency: '+e['source'])


def supported_bounds(curation,facts,views,definitions):
    bounds = []
    for rule in curation['bounds']:
        require(set(rule)=={'symbol','element_type','count','stride','name','evidence'},'storage domain bound keys')
        hunk,start = coordinate(rule['symbol'])
        count = capture(rule['count'],facts)
        stride = rule['stride']
        if set(stride)=={'source','struct'}:
            require(stride['source'] in definitions,'missing stride source')
            size = dv.struct_size(stride['struct'],definitions[stride['source']])
            require(size is not None and size>0,'unknown record stride')
        elif set(stride)=={'source','element_of'}:
            require(stride['source'] in facts['sources'],'missing element-stride source')
            ds,ss=source_views(facts['sources'][stride['source']])
            sizes=set()
            for d in ds:
                if d['name']==stride['element_of'] and '[' in d['view']:
                    element=re.sub(r'\[\d+\]','',d['view'],count=1)
                    value=view_extent(element,ss)
                    if value is not None:
                        sizes.add(value)
            require(len(sizes)==1,'ambiguous array element stride')
            size=sizes.pop()
        elif set(stride)=={'source','access'}:
            # Element size from the accessing instruction's size suffix.
            require(stride['source'] in facts['sources'],'missing access-stride source')
            sizes={dict(b=1,w=2,l=4)[m.lower()] for m in re.findall(stride['access'],clean(facts['sources'][stride['source']]),re.S)}
            require(len(sizes)==1,'ambiguous or missing access size')
            size=sizes.pop()
        else:
            size = capture(stride,facts)
        width,_ = dm.type_layout(rule['element_type'],dict(facts['model']['structs'],**curation['structs']))
        require(width==size,rule['symbol']+': type disagrees with independent stride')
        require(rule['name'].strip() and rule['evidence'].strip(),'bound needs evidence/name')
        bounds.append(dict(hunk=hunk,start=start,end=start+count*size,
            type=rule['element_type']+' [%d]' % count,name=rule['name'],basis='SOURCE_DOMAIN',
            evidence=rule['evidence'],source=rule['count']['source']))
    for p in facts['providers']:
        require(all(type(p[k]) is int for k in ('hunk','start','size')) and p['size']>0 and p['start']>=0,'invalid provider extent')
        require(all(type(s['offset']) is int and 0<=s['offset']<p['size'] for s in p['symbols']),p['id']+': symbol outside provider')
        bounds.append(dict(hunk=p['hunk'],start=p['start'],end=p['start']+p['size'],
            type='ACCEPTED_PROVIDER_LAYOUT',name=p['id'],basis='ACCEPTED_TYPED_PROVIDER',
            evidence='evidence/data-providers/accepted.json/'+p['id'],source=p['source'],
            members=[dict(symbol=s['name'],offset=s['offset'],
                provider_views=[v['type'] for v in views.get(s['name'],[]) if p['source'] in v['sources']])
                for s in p['symbols']],
            evidence_kinds=p['evidence_kinds']))
    for rule in curation['receiver_calls']:
        require(set(rule)=={'callee','element_type','allocation','consumer','evidence'},'receiver rule keys')
        require(dm.identifier(rule['callee']),'invalid receiver callee')
        size=capture(rule['allocation'],facts)
        consumer=rule['consumer']
        require(set(consumer)=={'source','struct'},'consumer layout keys')
        require(consumer['source'] in definitions,'missing receiver consumer source')
        require(dv.struct_size(consumer['struct'],definitions[consumer['source']])==size,
                'receiver consumer layout disagrees with allocation size')
        require(dm.type_layout(rule['element_type'],dict(facts['model']['structs'],**curation['structs']))[0]==size,
                'receiver type disagrees with allocation size')
        require(rule['evidence'].strip(),'receiver evidence required')
        pattern=r'\b'+re.escape(rule['callee'])+r'\(\s*(?:\([^()]+\)\s*)?&\s*(G_h(?:01|02)_[0-9A-F]{4})\s*\)'
        targets=defaultdict(list)
        for source,text in sorted(facts['sources'].items()):
            if Path(source).suffix.lower()=='.c':
                for m in re.finditer(pattern,clean(text)):
                    targets[m[1]].append(source)
        for symbol,sources in sorted(targets.items()):
            hunk,start=coordinate(symbol)
            bounds.append(dict(hunk=hunk,start=start,end=start+size,type=rule['element_type'],
                name='graphic descriptor '+symbol,basis='BOUNDED_RECEIVER_SUBOBJECT',
                evidence=rule['evidence'],sources=sorted(set(sources))))
    aggregates = list(bounds)
    for name,alternatives in views.items():
        hunk,start = coordinate(name)
        observed = facts['widths'].get(start,{}) if hunk==1 else {}
        if not observed.get('widths'):
            continue
        width,scalar = max(observed['widths']),[]
        for view in alternatives:
            try:
                parsed = dm.parse_type(view['type'])
                if parsed and not parsed[2] and (parsed[1] or not dm.struct_tag(view['type'])):
                    if dm.type_layout(view['type'],{})[0]==width:
                        scalar.append(view['type'])
            except FormatError:
                pass
        if not scalar or any(b['hunk']==hunk and b['start']<=start<b['end'] for b in aggregates):
            continue
        selected=sorted(scalar)[0]
        type_basis='CANONICAL_SCALAR_VIEW'
        interpreted=facts['model'].get('globals',{}).get(name,{})
        if interpreted.get('basis')=='CURATED':
            try:
                parsed=dm.parse_type(interpreted['type'])
                if parsed and not parsed[2] and (parsed[1] or not dm.struct_tag(interpreted['type'])):
                    if dm.type_layout(interpreted['type'],facts['model']['structs'])[0]==width:
                        selected=interpreted['type']
                        type_basis='CURATED_DATA_MODEL'
            except FormatError:
                pass
        bounds.append(dict(hunk=hunk,start=start,end=start+width,type=selected,type_basis=type_basis,
            name=name,basis='DIRECT_SCALAR_CELL',evidence='evidence/types.json and scalar source view',
            access_evidence=dict(path='evidence/types.json',offset=start,widths=observed['widths'],
                count=len(observed['sites']),functions=sorted({a['function'] for a in observed['sites']}),
                address_taken=observed.get('address_taken',0))))
    return sorted(bounds,key=lambda b:(b['hunk'],b['start'],b['end'],b['basis'],b['name']))


def union_size(intervals):
    end,total = -1,0
    for lo,hi in sorted(intervals):
        if hi>end:
            total += hi-max(lo,end)
            end = hi
    return total


def external_bindings(curation,facts):
    """Re-derive ABI slot identities; this never determines their provider."""
    rows=[]
    for rule in curation['external_bindings']:
        require(set(rule)=={'native','mechanical','artifact','kind'},'external binding keys')
        require(dm.identifier(rule['native']),'invalid native data name')
        require(rule['artifact'] in facts.get('external_evidence',{}),'missing external binding evidence')
        text=facts['external_evidence'][rule['artifact']]
        coordinates,view=set(),None
        if rule['kind']=='RUNTIME_OPERAND_IDENTITY':
            def walk(value):
                if isinstance(value,dict):
                    if value.get('symbol')==rule['native'] and value.get('kind')=='A4':
                        original=value.get('original')
                        require(isinstance(original,list) and len(original)==2 and
                                all(type(x) is int for x in original),'invalid runtime operand coordinate')
                        require(type(value.get('addend')) is int,'runtime binding addend must be an integer')
                        require(original[1]-value['addend']>=0,'runtime slot base precedes hunk')
                        coordinates.add((original[0],original[1]-value['addend']))
                    for v in value.values():
                        walk(v)
                elif isinstance(value,list):
                    for v in value:
                        walk(v)
            walk(json.loads(text))
        else:
            require(rule['kind']=='STARTUP_RECIPE_SLOT','unknown external binding kind')
            choices=[]
            for node in ast.walk(ast.parse(text)):
                if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='global_views' for t in node.targets):
                    choices.extend(ast.literal_eval(node.value))
            for typ,name,suffix in choices:
                if '_'+name==rule['native']:
                    coordinates.add((1,int(suffix,16)))
                    view=typ
        require(len(coordinates)==1,'absent/conflicting runtime slot: '+rule['native'])
        hunk,offset=coordinates.pop()
        mechanical='G_h%02d_%04X' % (hunk,offset)
        require(mechanical==rule['mechanical'],'runtime name/coordinate evidence disagrees')
        rows.append(dict(native=rule['native'],mechanical=mechanical,view_type=view,
            evidence=rule['artifact'],kind=rule['kind'],
            ownership='BINDING_ONLY; runtime ABI identity is not storage-provider/library provenance'))
    require(len({r['native'] for r in rows})==len(rows),'duplicate native binding')
    return sorted(rows,key=lambda r:r['native'])


def use_sites(facts):
    result=defaultdict(list)
    for source,text in sorted(facts['sources'].items()):
        assembly=Path(source).suffix.lower()!='.c'
        text=clean(text,assembly)
        if assembly:
            text=re.sub(r'(?im)^\s*(?:public|extern|xref)\b[^\n]*','',text)
            text=re.sub(r'(?im)^\s*[_A-Za-z]\w*\s+equ\b[^\n]*','',text)
        else:
            text=dv.EXTERN_RE.sub('',text)
        for name in sorted({m[1] for m in NAME.finditer(text)}):
            result[name].append(source)
    return dict(result)


def address_equates(facts):
    result=[]
    for source,text in sorted(facts['sources'].items()):
        if Path(source).suffix.lower()=='.c':
            continue
        for m in re.finditer(r'(?im)^\s*(_?G_h(01|02)_([0-9A-F]{4})_A4)\s+equ\s+(-?\d+)\s*$',clean(text,True)):
            require(m[2]=='01','A4 equate needs independently established DATA-hunk base')
            target='G_h%s_%s' % (m[2],m[3])
            offset=int(m[3],16)
            require(type(facts.get('a4_bias')) is int and int(m[4])+facts['a4_bias']==offset,
                    'A4 source equate disagrees with independently evidenced bias')
            result.append(dict(source=source,symbol=m[1],target=target,offset=offset,
                               displacement=int(m[4]),role='ADDRESS_EXPRESSION_ONLY; no separate allocation'))
    return result


def derive(curation,facts):
    require(isinstance(curation,dict) and set(curation)=={'bounds','dependencies','structs','receiver_calls','external_bindings','indexed_aliases'},'storage curation keys')
    require(isinstance(curation['bounds'],list) and isinstance(curation['dependencies'],list),'storage curation lists')
    require(isinstance(curation['structs'],dict),'curated structs must be a map')
    for tag in curation['structs']:
        require(tag not in facts['model']['structs'],'curated struct shadows data model')
        dm.struct_layout(tag,dict(facts['model']['structs'],**curation['structs']))
    check_dependencies(curation,facts)
    views,layouts,definitions = declarations(facts)
    uses=use_sites(facts)
    source_identities=set(views)
    bindings=external_bindings(curation,facts)
    equates=address_equates(facts)
    for e in equates:
        if e['target'] not in views:
            views[e['target']]=[dict(type='UNKNOWN',private_layouts=[],declared_extent=None,sources=[e['source']])]
    for b in bindings:
        if b['mechanical'] not in views:
            typ=b['view_type'] or 'UNKNOWN'
            views[b['mechanical']]=[dict(type=typ,private_layouts=[],
                declared_extent=view_extent(typ,{}) if typ!='UNKNOWN' else None,sources=[b['evidence']])]
    bounds = supported_bounds(curation,facts,views,definitions)
    regions = facts['regions']
    for i,r in enumerate(regions):
        require(all(type(r[k]) is int for k in ('hunk','start','end')) and 0<=r['start']<r['end'],'storage region bounds')
        require(not any(r['hunk']==o['hunk'] and r['start']<o['end'] and o['start']<r['end']
                        for o in regions[:i]),'overlapping storage regions')
    for b in bounds:
        require(any(r['hunk']==b['hunk'] and r['start']<=b['start']<b['end']<=r['end'] for r in regions),
                b['name']+': bound crosses resident region')
    indexed=[]
    for rule in curation['indexed_aliases']:
        require(set(rule)=={'base','target','index','element_type','evidence'},'indexed alias keys')
        hunk,start=coordinate(rule['base'])
        th,target=coordinate(rule['target'])
        index=capture(rule['index'],facts,allow_zero=True)
        width,_=dm.type_layout(rule['element_type'],dict(facts['model']['structs'],**curation['structs']))
        require(width is not None and hunk==th and start+index*width==target,
                'indexed alias address disagrees with named target')
        require(rule['evidence'].strip(),'indexed alias needs evidence')
        indexed.append(dict(base=rule['base'],target=rule['target'],index=index,width=width,
            byte_offset=index*width,view_type=rule['element_type'],hunk=hunk,start=start,end=target+width,evidence=rule['evidence']))
    windows,overruns = {},[]
    for name,alternatives in views.items():
        hunk,start = coordinate(name)
        region = next((r for r in regions if r['hunk']==hunk and r['start']<=start<r['end']),None)
        require(region is not None,name+': outside resident storage')
        extent = max([v['declared_extent'] or 0 for v in alternatives]+
                     (facts['widths'].get(start,{}).get('widths',[]) if hunk==1 else [])+[1])
        authoritative = [b['end'] for b in bounds if b['basis']!='DIRECT_SCALAR_CELL'
                         and b['hunk']==hunk and b['start']<=start<b['end']]
        end = min(start+extent,min(authoritative) if authoritative else region['end'])
        if start+extent>end:
            overruns.append(dict(symbol=name,declared_end=start+extent,window_end=end,
                disposition='PRIVATE_VIEW_TAIL_NOT_ALLOCATION; review consumer domain'))
        windows[name] = (hunk,start,end)
    # Candidate declaration overlap is a coallocation obligation, not an
    # extent claim. Keep its anchors in the same aggregate, even where the
    # declaration's padded tail is not a valid capacity.
    dependency_spans=[]
    declared=sorted((coordinate(n)[0],coordinate(n)[1],coordinate(n)[1]+
                     max(v['declared_extent'] or 0 for v in vs),n) for n,vs in views.items())
    for i,(h,start,end,name) in enumerate(declared):
        for oh,os,oe,other in declared[i+1:]:
            if oh!=h or os>=end:
                break
            if start<oe:
                dependency_spans.append((h,start,max(windows[name][2],windows[other][2])))
    objects,aliases = [],{}
    for r in regions:
        hunk,lo,hi = r['hunk'],r['start'],r['end']
        seeds = [(b['start'],b['end']) for b in bounds if b['hunk']==hunk and lo<=b['start']<hi]
        seeds += [(s,e) for h,s,e in windows.values() if h==hunk and lo<=s<hi]
        for note in curation['dependencies']:
            if note['coallocate']:
                require(all(n in windows for n in note['symbols']),'missing coallocation anchor')
                points = [windows[n] for n in note['symbols']]
                require(len({p[0] for p in points})==1,'coallocation crosses hunks')
                if points[0][0]==hunk and lo<=min(p[1] for p in points)<hi:
                    require(max(p[2] for p in points)<=hi,'coallocation crosses region')
                    seeds.append((min(p[1] for p in points),max(p[2] for p in points)))
        for edge in indexed:
            if edge['hunk']==hunk and lo<=edge['start']<hi:
                require(edge['end']<=hi,'indexed access crosses storage region')
                seeds.append((edge['start'],edge['end']))
        for h,start,end in dependency_spans:
            if h==hunk and lo<=start<hi:
                require(end<=hi,'declaration overlap crosses DATA/BSS boundary')
                seeds.append((start,end))
        components = []
        for start,end in sorted(seeds):
            if components and start<components[-1][1]:
                components[-1][1] = max(end,components[-1][1])
            else:
                components.append([start,end])
        segments,cursor = [],lo
        for start,end in components:
            if start>cursor:
                segments.append([cursor,start,False])
            known = [(max(start,b['start']),min(end,b['end'])) for b in bounds
                     if b['hunk']==hunk and start<b['end'] and b['start']<end]
            segments.append([start,end,union_size(known)==end-start])
            cursor = end
        if cursor<hi:
            segments.append([cursor,hi,False])
        merged = []
        for start,end,bounded in segments:
            if merged and not bounded and not merged[-1][2]:
                merged[-1][1] = end
            else:
                merged.append([start,end,bounded])
        for start,end,bounded in merged:
            key = 'storage_h%02d_%04X' % (hunk,start)
            members = [dict(b,offset=b['start']-start) for b in bounds
                       if b['hunk']==hunk and start<=b['start'] and b['end']<=end]
            names = sorted(n for n,(h,s,e) in windows.items() if h==hunk and start<=s<end)
            unresolved = [n for n in names if not any(b['start']<=windows[n][1]<b['end'] for b in members)]
            shape = 'aggregate' if not bounded or len(members)!=1 or members[0]['type']=='ACCEPTED_PROVIDER_LAYOUT' else (
                    'array' if '[' in members[0]['type'] else 'struct' if members[0]['type'].startswith('struct ') else 'scalar')
            row = dict(id=key,hunk=hunk,kind=r['kind'],start=start,end=end,
                status='BOUNDED' if bounded else 'UNBOUNDED',extent=end-start if bounded else None,
                shape=shape,name=members[0]['name'] if len(members)==1 else key,
                members=members,symbols=names,unresolved_anchors=unresolved)
            gaps=[]
            cursor=start
            for member in sorted(members,key=lambda b:(b['start'],b['end'])):
                if cursor<member['start']:
                    gaps.append(dict(start=cursor,end=member['start'],bytes=member['start']-cursor,
                        status='UNBOUNDED',extent=None,limit='NEXT_BOUNDED_MEMBER',
                        next_member=member['name'],reason='No independently bounded typed member covers this span.'))
                cursor=max(cursor,member['end'])
            if cursor<end:
                gaps.append(dict(start=cursor,end=end,bytes=end-cursor,status='UNBOUNDED',extent=None,
                    limit='NEXT_BOUNDED_OBJECT_OR_MEASURED_REGION_END',
                    reason='No independent extent; end is only the next bounded object or measured region boundary.'))
            row.update(unbounded_gaps=gaps,known_member_bytes=union_size([(b['start'],b['end']) for b in members]),
                       unbounded_gap_bytes=sum(g['bytes'] for g in gaps))
            require(row['known_member_bytes']+row['unbounded_gap_bytes']==end-start,'member/gap partition error')
            require(not bounded or not gaps,'bounded object contains an unevidenced gap')
            if not bounded:
                row.update(link_gap_bytes=end-start,gap_limit='NEXT_BOUNDED_OBJECT_OR_MEASURED_REGION_END',
                    reason='No independent full extent for '+(', '.join(unresolved) if unresolved else 'unclassified bytes')+
                           '; view sizes and neighboring addresses are not capacities. Nested bounded members are retained; unbounded_gaps lists the actual uncovered spans.')
            objects.append(row)
            for name in names:
                h,address,_ = windows[name]
                alternatives = views[name]
                variants,unknown = set(),False
                for v in alternatives:
                    try:
                        normalized = dm.type_key(v['type'])
                    except FormatError:
                        normalized = v['type'] if not v['type'].startswith('UNPARSED:') else None
                    unknown |= normalized is None
                    if normalized is not None:
                        variants.add((str(normalized),tuple(v['private_layouts'])))
                aliases[name] = dict(object=key,offset=address-start,address=address,hunk=h,views=alternatives,
                    alias_kind='INTERIOR' if address!=start else 'BASE',
                    reinterpretation=True if len(variants)>1 else None if unknown else False,
                    interpretation_status='VIEW_ONLY' if name in unresolved else 'BOUNDED_MEMBER_OR_INTERIOR_ALIAS',
                    active_sources=uses.get(name,[]),
                    observed_access_widths=facts['widths'].get(address,{}).get('widths',[]) if h==1 else [],
                    origin='SOURCE' if name in source_identities else 'IMPORTED_BINDING_ANCHOR',
                    modeled_type=facts['model'].get('globals',{}).get(name,{}).get('type','UNKNOWN'),
                    semantic_name=facts.get('names',{}).get(name,{}).get('name'),
                    semantic_evidence=facts.get('names',{}).get(name,{}).get('evidence'))
    overlaps = []
    declared = sorted((coordinate(n)[0],coordinate(n)[1],coordinate(n)[1]+
                       max(v['declared_extent'] or 0 for v in vs),n) for n,vs in views.items())
    for i,(h,lo,hi,name) in enumerate(declared):
        for oh,olo,ohi,other in declared[i+1:]:
            if oh!=h or olo>=hi:
                break
            if lo<ohi:
                same = aliases[name]['object']==aliases[other]['object']
                overlaps.append(dict(left=name,right=other,bytes=min(hi,ohi)-olo,
                    disposition='SHARED_STORAGE' if same else 'DECLARED_TAIL_ONLY_DEPENDENCY',same_object=same))
    totals = {}
    for r in regions:
        selected = [o for o in objects if o['hunk']==r['hunk'] and o['kind']==r['kind']]
        totals['h%d_%s' % (r['hunk'],r['kind'])] = dict(total=r['end']-r['start'],
            bounded=sum(o['end']-o['start'] for o in selected if o['status']=='BOUNDED'),
            UNBOUNDED=sum(o['end']-o['start'] for o in selected if o['status']=='UNBOUNDED'),
            bounded_member_union=union_size([(b['start'],b['end']) for b in bounds
                if b['hunk']==r['hunk'] and r['start']<=b['start']<r['end']]),
            UNBOUNDED_gaps=sum(o['unbounded_gap_bytes'] for o in selected))
    for edge in indexed:
        require(edge['base'] in aliases and edge['target'] in aliases,'indexed alias needs both named source targets')
        a,b=aliases[edge['base']],aliases[edge['target']]
        require(a['object']==b['object'] and b['offset']-a['offset']==edge['byte_offset'],
                'indexed alias allocations were disconnected')
        edge.update(object=a['object'],target_offset=b['offset'])
    for b in bindings:
        a=aliases[b['mechanical']]
        b.update(object=a['object'],offset=a['offset'])
    for e in equates:
        a=aliases[e['target']]
        e.update(object=a['object'],object_offset=a['offset'])
    return dict(indexed_aliases=indexed,external_bindings=bindings,address_equates=equates,
        regions=regions,objects=objects,aliases=dict(sorted(aliases.items())),private_structs=layouts,
        declared_overlap_candidates=overlaps,private_view_overruns=overruns,
        summary=dict(bytes=totals,symbols=len(aliases),source_identifiers=len(source_identities),
            source_referenced_or_defined=sum(bool(uses.get(n)) for n in source_identities),
            declaration_only=sum(not uses.get(n) for n in source_identities),
            external_bindings=len(bindings),address_equates=len(equates),indexed_aliases=len(indexed),objects=len(objects),
            interior_aliases=sum(a['offset']!=0 for a in aliases.values()),
            alternate_views=sum(len(a['views'])>1 for a in aliases.values()),
            overlap_pairs_shared=sum(o['same_object'] for o in overlaps),
            overlap_pairs_disconnected=sum(not o['same_object'] for o in overlaps),
            private_view_overruns_requiring_domain_review=len(overruns)))


def validate(document,facts):
    require(isinstance(document,dict) and set(document)=={'schema_version','policy','curation','derived'},'storage plan keys')
    require(type(document['schema_version']) is int and document['schema_version']==1,'storage plan schema_version')
    require(document['policy']==POLICY,'storage policy changed')
    expected = derive(document['curation'],facts)
    require(json.dumps(document['derived'],sort_keys=True,allow_nan=False)==json.dumps(expected,sort_keys=True,allow_nan=False),'stale/modified storage partition, alias, view, bound or coverage; re-derive')
    return document


CURATION = 'recovery/storage_curation.json'
OUTPUT = 'build/storage-plan.json'


def load(root,path=CURATION):
    """Curated rules are canonical; the plan is re-derived from them and the
    current sources on every load (about 1.5 s), never stored in git."""
    root = Path(root)
    require(is_active_repo_path(root/path,root),'inactive storage curation path')
    curation = json.loads((root/path).read_text(),object_pairs_hook=dm._unique_object)
    return dict(schema_version=1,policy=POLICY,curation=curation,
                derived=derive(curation,collect(root,curation)))


def write(root,out=OUTPUT):
    """Write the derived plan for readers (link staging, trace decoding)."""
    document = load(root)
    target = Path(root)/out
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes((json.dumps(document,indent=1,sort_keys=True,allow_nan=False)+'\n').encode())
    return document
