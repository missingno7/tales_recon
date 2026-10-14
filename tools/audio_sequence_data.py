"""Replayed DATA-in-CODE classification facts; never reconstructed-source credit."""
import json
from collections import Counter
from pathlib import Path
from common import require, sha256
from repo_paths import active_files, canonical_path


def inputs(root):
    folder=Path(root)/'evidence/data-facts'
    return [p.relative_to(root).as_posix() for p in active_files(folder,'.json')] if folder.exists() else []


def identity(root):
    return {name:sha256(canonical_path(root,name).read_bytes()) for name in inputs(root)}


def payload(blob,model,hunk):
    h=next((h for h in model['hunks'] if h['number']==hunk),None)
    require(h is not None and h['content_offset'] is not None,'data fact needs initialized hunk')
    return blob[h['content_offset']:h['content_offset']+h['initialized_size']]


def field(r):
    return {k:r[k] for k in ('source_hunk','source_offset','target_hunk','addend_raw','type','width')}


def decode(code,start,end,roots,continuations,relocations):
    """Static score grammar from the curated, pinned audio interpreter review.

    Roots are two-byte channel/priority headers. Continuations have no header
    and retain their unreferenced status. CPU execution is never inferred from
    a byte that happens to disassemble as an instruction.
    """
    rows={};todo=[p+2 for p in roots]+list(continuations)
    rel={r['source_offset']:r for r in relocations if r['source_hunk']==0}
    for p in roots:
        require(start<=p and p+2<=end and code[p]<4,'invalid audio header')
    while todo:
        p=todo.pop()
        if p in rows:continue
        require(start<=p<end,'audio edge outside classified interval')
        op=code[p];q=p+1;targets=[];pointer=None
        if op<0x80:q=p+2;kind='NOTE_DURATION'
        elif op in (0x81,0x84,0x85):
            pointer=(p+2)&~1;q=pointer+4
            require(q<=end,'truncated audio pointer')
            require(pointer==p+1 or code[p+1]==0,'nonzero pointer alignment filler')
            rr=rel.get(pointer);target=int.from_bytes(code[pointer:q],'big')
            require(rr is not None and rr['type']=='HUNK_RELOC32' and rr['width']==4 and rr['target_hunk']==0 and rr['addend_raw']==target,'unproved audio pointer')
            targets=[target];kind={0x81:'COUNTED_LOOP',0x84:'JUMP',0x85:'PATTERN_CALL'}[op]
        elif op in (0x86,0x88):kind='PATTERN_RETURN' if op==0x86 else 'STOP'
        elif op==0x8a:q=((p+2)&~1)+2;kind='WORD_PARAMETER'
        elif op in (0x92,0x96,0x9c,0xaa,0xa7):kind='NO_PARAMETER'
        elif op in (0x91,0x95):q=p+3;kind='TWO_PARAMETERS'
        elif op==0x98:q=((p+2)&~1)+3;kind='PERIOD_DURATION'
        elif op==0x8b:q=p+3;kind='NOTE_DURATION_COMMAND'
        else:
            require(0x80<=op<=0xab,'unsupported audio opcode')
            q=p+2;kind='BYTE_PARAMETER'
        require(q<=end,'truncated audio command')
        if op not in (0x84,0x86,0x88):targets.append(q)
        rows[p]=dict(offset=p,end=q,opcode=op,kind=kind,successors=targets)
        if pointer is not None:rows[p]['pointer_field']=pointer
        todo.extend(targets)
    coverage=Counter(q for row in rows.values() for q in range(row['offset'],row['end']))
    for p in roots:coverage.update((p,p+1))
    require(coverage and max(coverage.values())==1,'overlapping audio commands/headers')
    residual=[q for q in range(start,end) if q not in coverage]
    pointers=[r for r in relocations if r['source_hunk']==0 and start<=r['source_offset']<end]
    require({r['source_offset'] for r in pointers}=={r['pointer_field'] for r in rows.values() if 'pointer_field' in r},'unclassified relocation in score')
    require(all(r['addend_raw'] in rows for r in pointers),'audio pointer target is not command start')
    return dict(commands=[rows[p] for p in sorted(rows)],residual=residual,
                headers=[dict(offset=p,channel=code[p],priority=code[p+1]) for p in roots],
                pointers=[field(r) for r in pointers])


def validate(fact,blob,model,analysis=None,claimed=()):
    require(fact.get('schema_version')==1 and fact.get('kind')=='AUDIO_SEQUENCE_BYTECODE','unsupported CODE-data fact')
    require(fact.get('classification')=='DATA' and fact.get('ownership')=='UNKNOWN','classification/ownership policy differs')
    require(fact.get('source_acceptance') is False and fact.get('proof_level') is None,'classification grants no acceptance')
    require(all(fact.get(k)=='UNKNOWN' for k in ('source_language','source_filename','object_membership')),'unsupported provenance claim')
    require(fact.get('oracle_sha256')==sha256(blob),'data fact fixture differs')
    interval=fact['interval'];h=interval['hunk'];a=interval['start'];z=interval['end']
    require(type(h) is int and h==0 and type(a) is int and type(z) is int and 0<=a<z,'invalid CODE-data interval')
    require(next(x for x in model['hunks'] if x['number']==h)['type']=='CODE','historical container is not CODE')
    code=payload(blob,model,h)
    require(z<=len(code) and sha256(code[a:z])==interval['sha256'],'CODE-data extent/hash differs')
    require(not any(x['hunk']==h and x['start']<z and a<x['end'] for x in claimed),'data fact overlaps accepted source')
    # A classifier must not erase independently established executable evidence.
    for f in (analysis or {}).get('functions',[]):
        strong=any(e['kind']!='RELOCATION_POINTER' for e in f.get('entry_evidence',[]))
        require(not(f['hunk']==h and a<=f['start']<z and strong),'data fact contradicts executable entry')
        if f['hunk']==h and not a<=f['start']<z:
            edges=[(h,x['target']) for x in f.get('cfg',[])]
            edges += [(x['hunk'],x['offset']) for x in f.get('direct_callees',[])]
            require(not any(th==h and a<=to<z for th,to in edges),'data fact contradicts direct control-flow edge')
    # Positive consumer evidence includes the complete reviewed interpreter,
    # selector initialization, dispatch table, and immediately adjoining code.
    require(fact['consumer_anchors'],'consumer evidence missing')
    for anchor in fact['consumer_anchors']:
        data=payload(blob,model,anchor['hunk']);p=anchor['start'];n=anchor['size']
        require(type(p) is int and type(n) is int and 0<=p<p+n<=len(data) and sha256(data[p:p+n])==anchor['sha256'],'audio consumer anchor differs')
    require({x['role'] for x in fact['consumer_anchors']}=={'INTERPRETER','SELECTOR_INIT','DISPATCH_TABLE','LEFT_CODE_NEIGHBOUR','RIGHT_CODE_NEIGHBOUR'},'incomplete audio consumer roles')
    left=next(x for x in fact['consumer_anchors'] if x['role']=='LEFT_CODE_NEIGHBOUR')
    right=next(x for x in fact['consumer_anchors'] if x['role']=='RIGHT_CODE_NEIGHBOUR')
    require(left['hunk']==right['hunk']==h and left['start']+left['size']==a and right['start']==z,
            'classified data no longer abuts the reviewed code neighbours')
    rels=model['relocations']
    for want in fact['consumer_relocations']:
        require(sum(field(r)==want for r in rels)==1,'audio consumer relocation differs')
    dispatch=fact['dispatch']
    require(len(dispatch)==44 and [x['opcode'] for x in dispatch]==list(range(0x80,0xac)),'incomplete audio dispatch')
    for entry in dispatch:
        want=dict(source_hunk=1,source_offset=fact['dispatch_offset']+4*(entry['opcode']-0x80),target_hunk=0,addend_raw=entry['handler'],type='HUNK_RELOC32',width=4)
        require(sum(field(r)==want for r in rels)==1,'audio dispatch binding differs')
    incoming=[field(r) for r in rels if r['target_hunk']==h and a<=r['addend_raw']<z and not(r['source_hunk']==h and a<=r['source_offset']<z)]
    require(sorted(incoming,key=lambda r:(r['source_hunk'],r['source_offset']))==fact['incoming_relocations'],'audio incoming references differ')
    table=fact['selector_table'];root_refs=[r for r in incoming if r['source_hunk']==0 and table['start']<=r['source_offset']<table['end']]
    require(len(root_refs)==len(incoming) and (table['end']-table['start'])%4==0,'unexplained audio inbound reference')
    require(all(r['source_offset']%4==0 and r['type']=='HUNK_RELOC32' and r['width']==4 for r in root_refs),'invalid selector field')
    table_fields=[field(r) for r in rels if r['source_hunk']==0 and table['start']<=r['source_offset']<table['end']]
    require(sorted(table_fields,key=lambda r:r['source_offset'])==fact['selector_relocations'],'selector table differs')
    roots=sorted({r['addend_raw'] for r in incoming});require(roots==fact['roots'],'audio stream roots differ')
    layout=decode(code,a,z,roots,fact['unreferenced_continuations'],rels)
    require(layout['residual']==fact['unclassified_zero_offsets'] and all(p%2 and code[p]==0 for p in layout['residual']),'unclassified score bytes differ')
    require(layout['pointers']==fact['pointer_fields'],'audio pointer fields differ')
    return dict(fact,layout=layout)


def load(root,blob,model,analysis=None,claimed=()):
    rows=[]
    for name in inputs(root):
        path=canonical_path(root,name);raw=path.read_bytes()
        row=validate(json.loads(raw),blob,model,analysis,claimed)
        row.update(evidence_path=name,evidence_sha256=sha256(raw))
        i=row['interval']
        require(not any(x['interval']['hunk']==i['hunk'] and x['interval']['start']<i['end'] and i['start']<x['interval']['end'] for x in rows),'overlapping CODE-data facts')
        rows.append(row)
    return rows


def ranges(facts):
    return [dict(hunk=f['interval']['hunk'],start=f['interval']['start'],end=f['interval']['end'],classification='DATA',ownership='UNKNOWN',evidence=f['evidence_path']) for f in facts]
