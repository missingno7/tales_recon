"""Rederived root closure and measured typed definitions for the complete score."""
import json
from common import require,sha256,json_bytes
from audio_sequence_data import payload,field,load as classified_facts
from audio_score_grammar import derive,form
from audio_score_commands import SPECS,BY_OPCODE,label,header_label,encode,check

INTERVAL=(0x13b8,0x2816)
ZERO_DEBT=(0x16e3,0x1835,0x1cc5,0x21dd,0x257b,0x2815)


def discover(blob,model,classification,grammar):
    code=payload(blob,model,0);start,end=INTERVAL
    require(classification['interval']['hunk']==0 and (classification['interval']['start'],classification['interval']['end'])==INTERVAL,'score interval changed')
    require(classification['unclassified_zero_offsets']==list(ZERO_DEBT),'uncovered zero evidence changed')
    roots=classification['roots'];commands={};todo=[p+2 for p in roots]
    header_points={p+i for p in roots for i in (0,1)};covered=set(header_points)
    rel={r['source_offset']:r for r in model['relocations'] if r['source_hunk']==0}
    headers=[dict(offset=p,command='HEADER',operands=dict(channel=code[p],priority=code[p+1])) for p in roots]
    bindings=[];entries={p+2:[dict(kind='SELECTOR_HEADER',offset=p)] for p in roots}
    for h in headers:check(h)
    while todo:
        p=todo.pop()
        if p in commands:continue
        require(start<=p<end and p not in ZERO_DEBT,'stream crosses uncovered zero or classified boundary')
        op=code[p];shape=form(grammar,op,p);z=p+shape['length']
        require(z<=end and not set(range(p,z)).intersection(ZERO_DEBT),'stream crosses uncovered zero')
        require(not covered.intersection(range(p,z)),'overlapping stream/header command boundary')
        require(op<0x80 or op in BY_OPCODE,'unknown or unused opcode command')
        name='NOTE' if op<0x80 else BY_OPCODE[op]
        fields=('pitch','ticks') if name=='NOTE' else SPECS[name][1]
        targets=[];pointer=shape['pointer_field']
        if pointer is not None:
            site=p+pointer;rr=rel.get(site)
            require(rr is not None and rr['type']=='HUNK_RELOC32' and rr['width']==4 and rr['target_hunk']==0,'unproved score pointer field')
            target=int.from_bytes(code[site:site+4],'big')
            require(target==rr['addend_raw'] and start<=target<end and target not in ZERO_DEBT and target not in header_points,'pointer to an unproved stream')
            require(site==(p+2)&~1 and (site==p+1 or code[p+1]==0),'untyped pointer alignment byte')
            args=dict(target=label(target));targets.append(target)
            bindings.append(dict(field(rr),symbol=label(target)))
            entries.setdefault(target,[]).append(dict(kind='TYPED_POINTER_OPERAND',site=site,command=p))
        elif name=='NOTE':args=dict(pitch=op,ticks=code[p+1])
        else:
            require(shape['length']==1+len(fields),'grammar length differs from typed operand fields')
            args={k:code[p+1+i] for i,k in enumerate(fields)}
        c=dict(offset=p,command=name,operands=args);check(c)
        commands[p]=c;covered.update(range(p,z))
        if 'NEXT' in shape['flows'] or 'CALL' in shape['flows']:targets.append(z)
        todo.extend(targets)
    require(all(int(b['symbol'].rsplit('_',1)[-1],16) in commands for b in bindings),'pointer to an unproved stream')
    # Every relocation at a proved source site is exhaustively bound; straddles
    # and fields in a scalar/header cannot hide behind comparison masks.
    touched=[r for r in model['relocations'] if r['source_hunk']==0 and any(q in covered for q in range(r['source_offset'],r['source_offset']+r['width']))]
    require(sorted(map(field,touched),key=lambda r:r['source_offset'])==sorted([{k:v for k,v in b.items() if k!='symbol'} for b in bindings],key=lambda r:r['source_offset']),'unnamed/masked/straddling relocation in proved data')
    # Follow each proved entry linearly to a grammar terminal. Pointer targets
    # acquire provenance only from commands reached from an already proved root.
    streams=[]
    for p,evidence in sorted(entries.items()):
        path=[];q=p
        while True:
            require(q in commands and q not in path,'stream lacks a grammar-terminal boundary')
            path.append(q);c=commands[q];op=c['operands']['pitch'] if c['command']=='NOTE' else SPECS[c['command']][0]
            sh=form(grammar,op,q)
            if c['command'] in ('RETURN','END','JUMP'):break
            q+=sh['length']
        streams.append(dict(entry=p,evidence=evidence,terminal=path[-1],end=path[-1]+form(grammar,op,path[-1])['length'],commands=len(path)))
    rows=sorted(headers+list(commands.values()),key=lambda c:c['offset'])
    gaps=[]
    for p in range(start,end):
        if p not in covered:
            if gaps and gaps[-1]['end']==p:gaps[-1]['end']=p+1
            else:gaps.append(dict(start=p,end=p+1))
    return dict(roots=roots,commands=rows,streams=streams,bindings=sorted(bindings,key=lambda r:r['source_offset']),
                typed_bytes=len(covered),unproved_intervals=gaps,
                proven_labels=sorted({header_label(p) for p in roots}|{b['symbol'] for b in bindings}))


def plan(layout,grammar):
    """Six natural even-start groups, ending at the six uncredited zeros.

    Unreached interior islands are omitted only between independently terminal
    and independently rooted commands. Object coordinates arise from commands.
    """
    objects=[];start=INTERVAL[0];alllabels=set(layout['proven_labels'])
    for zero in ZERO_DEBT:
        rows=[c for c in layout['commands'] if start<=c['offset']<zero]
        require(rows and rows[0]['offset']==start,'object lacks independent first root')
        ident='score_%04X'%start;sem=encode(rows,alllabels);parts=[];cursor=0
        for c in rows:
            name=c['command'];op=c['operands']['pitch'] if name=='NOTE' else SPECS[name][0] if name!='HEADER' else None
            n=2 if name=='HEADER' else form(grammar,op,c['offset'])['length']
            symbol=header_label(c['offset']) if name=='HEADER' else label(c['offset'])
            require(sem['coordinates'][symbol]==cursor and cursor%2==c['offset']%2,'compaction changes grammar pointer parity')
            if parts and parts[-1]['original_end']==c['offset']:parts[-1]['original_end']+=n;parts[-1]['candidate_end']+=n
            else:parts.append(dict(original_start=c['offset'],original_end=c['offset']+n,candidate_start=cursor,candidate_end=cursor+n))
            cursor+=n
        require(parts[-1]['original_end']==zero and cursor%2==1,'object terminal/implicit padding bound differs')
        objects.append(dict(id='resident_audio_'+ident,prefix=ident,start=start,end=zero+1,typed_bytes=cursor,
                            CODE=cursor+1,implicit_assembler_padding=dict(original_offset=zero,candidate_offset=cursor,size=1),parts=parts,
                            source='src/recovered/code-data/'+ident+'.asm',candidate='evidence/rules/audio-score-measured/'+ident+'.asm'))
        start=zero+1
    require(sum(x['typed_bytes'] for x in objects)==layout['typed_bytes'],'partial score provider plan')
    return objects


def rederive(root,blob,model,grammar=None):
    grammar=derive(blob,model) if grammar is None else grammar
    classification=next(f for f in classified_facts(root,blob,model) if f['evidence_path']=='evidence/data-facts/resident-audio-sequences.json')
    layout=discover(blob,model,classification,grammar)
    return grammar,layout,plan(layout,grammar)
