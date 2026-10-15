"""Rederive typed score operand widths from driver instructions, never score bytes."""
from common import require, sha256, json_bytes, FormatError
from audio_sequence_data import payload, field
from analysis_support import decoder

# Only explicitly reviewed opcodes can enter a provider. Others are inventoried,
# including their measured consumption where derivable, but reject on use.
REVIEWED=frozenset((0x80,0x81,0x82,0x84,0x85,0x86,0x87,0x88,0x89,
                   0x8b,0x8c,0x8f,0x90,0x91,0x95,0x97,0xa0,0xab))


def instructions(code,start,end):
    rows=list(decoder().disasm(code[start:end],start))
    require(rows and sum(i.size for i in rows)==end-start and
            all(not i.mnemonic.startswith('dc.') for i in rows),'grammar incomplete driver decode')
    return {i.address:(i.mnemonic,i.op_str,i.address+i.size) for i in rows}


def consumption(ins,entry,parity):
    """Enumerate handler CFG with symbolic A1, alignment and stream-PC stores.

    A1 begins at P+2 after command dispatch prefetch, or P on the
    separately decoded positive-note branch. Calls have separately checked
    cursor contracts. Unmodelled A1 uses and variable consumption reject.
    """
    todo=[(entry,parity if entry==0x5a9c else parity+2,None,None,None,(),None,None,())];out=[]
    while todo:
        pc,a1,d0,z,saved,reads,transfer,lexical,visited=todo.pop()
        require(pc not in visited and len(visited)<160,'grammar cyclic/unsupported handler')
        visited=visited+(pc,)
        require(pc in ins,'grammar edge outside decoded driver')
        m,o,nxt=ins[pc]
        if pc==0x5a76:
            out.append(dict(length=(lexical if transfer else a1)-parity,
                            reads=list(reads),flow=transfer or 'NEXT',trace=list(visited)))
            continue
        if m=='rts':
            require(saved is not None,'grammar RTS without saved stream PC')
            out.append(dict(length=1 if saved=='STOP' else a1-parity,reads=list(reads),
                            flow='STOP' if saved=='STOP' else 'NEXT',trace=list(visited)))
            continue
        if m.startswith(('bra.','beq.','bne.','bpl.','bhi.','ble.')):
            target=int(o.replace('$',''),16)
            if m.startswith('bra.'):choices=[target]
            elif m.startswith('beq.') and z is not None:choices=[target if z else nxt]
            elif m.startswith('bne.') and z is not None:choices=[nxt if z else target]
            else:choices=[target,nxt]
            for dest in choices:todo.append((dest,a1,d0,None,saved,reads,transfer,lexical,visited))
            continue
        if m=='move.l' and o=='a1, d0':d0=a1
        elif m=='btst.b' and o=='#$0, d0':
            require(type(d0) is int,'grammar alignment without cursor');z=d0%2==0
        elif m in ('addq.l','subq.l') and o.endswith(', a1'):
            require(type(a1) is int,'grammar arithmetic on unknown cursor')
            a1+=int(o.split(',')[0].replace('#$',''),16)*(1 if m=='addq.l' else -1)
        elif '(a1)+' in o or (m=='movea.l' and o=='(a1), a1'):
            require(type(a1) is int,'grammar read at unknown cursor')
            width={'b':1,'w':2,'l':4}.get(m.split('.')[-1]);require(width is not None,'grammar stream width')
            require(o.startswith('(a1)'),'grammar unsupported stream use')
            reads=reads+((a1-parity,width),)
            if m=='movea.l' and o=='(a1), a1':lexical=a1+4;transfer='POINTER';a1=None
            else:
                a1+=width
                if m=='movea.l' and o.endswith(', a3'):lexical=a1
        elif m=='movea.l' and o=='a3, a1':
            require(lexical is not None,'grammar call pointer missing');transfer='CALL';a1=None
        elif m=='movea.l' and o=='(a1, d0.w), a1':
            require(any(ins[p][:2]==('subq.b','#$1, $24(a0)') for p in visited),'grammar return decrement')
            transfer='RETURN';lexical=parity+1;a1=None
        elif m=='lea.l' and o=='$2a(a0), a1':a1=None
        elif m=='move.l' and o=='a1, $4(a0)':saved=a1
        elif m=='clr.l' and o=='$4(a0)':saved='STOP'
        elif m.startswith(('jsr','bsr')):
            target=int(o.split('(')[0].replace('$',''),16)
            require(target in (0x559e,0x57e4,0x59a4),'grammar unknown callee cursor contract')
        elif 'a1' in o:
            require((m=='movem.l' and o in ('a0-a1, -(a7)','(a7)+, a0-a1')) or
                    (m=='move.l' and o=='a1, (a2, d0.w)'),'grammar unmodelled A1 effect: '+m+' '+o)
        elif o.endswith(', d0') or m in ('swap','clr.w') and o=='d0':d0=None;z=None
        elif not m.startswith(('move','lea','movem','bra')):z=None
        todo.append((nxt,a1,d0,z,saved,reads,transfer,lexical,visited))
    require(out,'grammar no terminal outcome')
    lengths={r['length'] for r in out}
    pointers={x for r in out for x in r['reads'] if x[1]==4}
    require(len(pointers)<=1,'grammar multiple pointer operands')
    return dict(length=next(iter(lengths)) if len(lengths)==1 else None,
                possible_lengths=sorted(lengths),pointer_field=next(iter(pointers))[0] if pointers else None,
                flows=sorted({r['flow'] for r in out}),reads=sorted({tuple(x) for r in out for x in r['reads']}),
                instruction_offsets=sorted({p for r in out for p in r['trace']}))


def derive(blob,model):
    code=payload(blob,model,0);ins=instructions(code,0x5a50,0x5e6c)
    selector=instructions(code,0x57e4,0x5868)
    require([selector[p][:2] for p in (0x57fa,0x57fc,0x57fe,0x5800,0x5804,0x5806,0x580c,0x5818,0x581c,0x5828)]==
            [('clr.w','d0'),('move.b','(a0)+, d0'),('move.b','(a0)+, d1'),('and.w','#$ff, d1'),
             ('lsl.l','#$2, d0'),('lea.l','$29fa.l, a1'),('movea.l','(a1, d0.w), a1'),
             ('cmp.w','d2, d1'),('move.b','d1, $3b(a1)'),('move.l','a0, $4(a1)')],
            'grammar two-byte channel/priority header consumption changed')
    prelude=[('tst.b','(a1)'),('bpl.b','$5a9c'),('move.b','(a1)+, d0'),
             ('and.w','#$7f, d0'),('cmp.b','#$2c, d0'),('ble.b','$5a8a'),
             ('bra.w','$5b62'),('lsl.w','#$2, d0'),('lea.l','$292e.l, a2'),
             ('movea.l','(a2, d0.w), a2'),('clr.w','d0'),('move.b','(a1)+, d0'),('jmp','(a2)')]
    require([ins[p][:2] for p in sorted(ins) if 0x5a76<=p<0x5a9c]==prelude,'grammar dispatch/prefetch changed')
    rels=model['relocations']
    require(any(field(r)==dict(source_hunk=0,source_offset=0x5a8e,target_hunk=1,addend_raw=0x292e,
                              type='HUNK_RELOC32',width=4) for r in rels),'grammar dispatch relocation')
    note=instructions(code,0x59a4,0x5a50)
    require(all('a1' not in o for m,o,n in note.values()),'grammar note callee modifies cursor')
    rng=instructions(code,0x559e,0x55d6)
    require(list(rng.values())[0][:2]==('movem.l','d7/a0-a1, -(a7)') and
            list(rng.values())[-2][:2]==('movem.l','(a7)+, d7/a0-a1'),'grammar RNG cursor contract')
    require(ins[0x5d08][:2]==('movem.l','a0-a1, -(a7)') and
            ins[0x5d16][:2]==('movem.l','(a7)+, a0-a1'),'grammar trigger cursor contract')
    rows=[];noteforms=[consumption(ins,0x5a9c,p) for p in (0,1)]
    for op in range(0x80,0xac):
        slot=0x292e+4*(op-0x80)
        rr=[r for r in rels if r['source_hunk']==1 and r['source_offset']==slot]
        require(len(rr)==1 and rr[0]['target_hunk']==0 and rr[0]['type']=='HUNK_RELOC32' and rr[0]['width']==4,
                'grammar missing handler dispatch')
        handler=rr[0]['addend_raw'];require(handler in ins,'grammar handler not decoded')
        try:forms=[consumption(ins,handler,p) for p in (0,1)];error=None
        except (FormatError,TypeError,ValueError) as exc:forms=None;error=str(exc)
        require(op not in REVIEWED or forms is not None and all(f['length'] is not None for f in forms),'reviewed grammar no longer derivable: '+str(error))
        rows.append(dict(opcode=op,handler=handler,forms=forms,accepted=op in REVIEWED,
                         rejection=None if op in REVIEWED else 'UNUSED_OR_UNREVIEWED_OPCODE',diagnostic=error))
    result=dict(schema_version=1,kind='DECODED_AUDIO_OPERAND_GRAMMAR',dispatch_prefetch=2,
                pointer_alignment='(P+2)&~1',header_width=2,selector_sha256=sha256(code[0x57e4:0x5868]),driver_sha256=sha256(code[0x5a50:0x5e6c]),note_forms=noteforms,opcodes=rows)
    import json
    return json.loads(json_bytes(result))


def form(grammar,opcode,position):
    require(type(opcode) is int and 0<=opcode<256,'grammar opcode domain')
    if opcode<0x80:return grammar['note_forms'][position%2]
    row=next((r for r in grammar['opcodes'] if r['opcode']==opcode),None)
    require(row is not None and row['accepted'] and row['forms'] is not None,'unknown or unused audio opcode')
    return row['forms'][position%2]
