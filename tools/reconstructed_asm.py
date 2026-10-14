"""Strict reconstructed ASM contributions, separate from C and SDK ASM.

V1 admits the independently bounded RNG CCR-X and saved-A4 record consumers.
Other driver spans require separately measured predicates/object grammars.
"""
import argparse
import json
import sys
from pathlib import Path

COMMANDS=['Old1:bin/as -o rng.o rng.asm >rng-as.log', 'Old1:bin/as -o note.o note.asm >note-as.log', 'Old1:bin/as -o bind.o bind.asm >bind-as.log', 'Old1:bin/ln -m -t -o rng.exe rng.o bind.o >rng-ln.log', 'Old1:bin/ln -m -t -o note.exe note.o bind.o >note-ln.log']
def expected_source(data_declaration=False):
    lines=['\tfar data','\tpublic _resident_asm_559E,_resident_asm_55D6']
    if not data_declaration:lines+=['\tpublic _G_h01_2B89,_G_h01_2B8A']
    lines+=['_resident_asm_559E','\tmovem.l d7/a0-a1,-(sp)','\tmove.w #7,d7',
      '\tlea _G_h01_2B89,a0','\tlea _G_h01_2B8A,a1','_rng_bit',
      '\tmove.b 1(a1),d0','\troxl.b #4,d0','\teor.b d0,1(a1)',
      '\tmove.b 1(a1),d0','\troxl.b #1,d0','\tmove.b (a0),d0',
      '\troxr.b #1,d0','\tmove.b d0,(a0)','\troxr.w (a1)',
      '\tdbra d7,_rng_bit','\tmove.b (a0),d0','\tmovem.l (sp)+,d7/a0-a1',
      '\trts','_resident_asm_55D6']
    if data_declaration:lines+=['\tdseg','\tpublic _G_h01_2B89,_G_h01_2B8A','\tend']
    return ('\n'.join(lines)+'\n').encode('ascii')

BIND=b'\tpublic _G_h01_2B89,_G_h01_2B8A,_G_h01_2B4E,_G_h01_29DE,_G_h01_2A0A\n\tdseg\n_G_h01_2B89\n\tds.b 1\n\tds 0\n_G_h01_2B8A\n\tds.w 1\n_G_h01_2B4E\n\tds.w 1\n_G_h01_29DE\n\tds.w 1\n_G_h01_2A0A\n\tds.b 1\n\tend\n'
NOTE_SOURCE=b'\tfar data\n\tpublic _resident_asm_59A4,_resident_asm_5A50\n_G_h01_27E4_A4 equ -22554\n_resident_asm_59A4\n\tmovem.l a2-a4,-(sp)\n\tand.w #$ff,d0\n\tclr.l d1\n\tmove.b d0,d1\n\tand.b #$f,d1\n\tadd.b $12(a0),d1\n\tcmp.b #$b,d1\n\tble _L59C6\n\tadd.b #$10,d0\n\tsub.b #$c,d1\n_L59C6\n\tadd.b $23(a0),d0\n\tbpl _L59CE\n\tclr.w d0\n_L59CE\n\tlsr.b #4,d0\n\tmove.w d7,d3\n\tlsl.w #3,d3\n\tlea _G_h01_2B4E,a2\n\tadda.w d3,a2\n\tmove.w d7,d3\n\tlsl.w #4,d3\n\tmovea.l #$dff0a0,a3\n\tadda.w d3,a3\n\tcmp.b #1,d0\n\tbhi _L59F6\n\tmoveq #2,d3\n\tsub.b d0,d3\n\tclr.l d0\n\tbra _L59FA\n_L59F6\n\tsubq.b #2,d0\n\tmoveq #0,d3\n_L59FA\n\tadd.b $3a(a0),d0\n\tlsl.w #2,d0\n\tlea _G_h01_27E4_A4(a4),a4\n\tmovea.l 0(a4,d0.w),a4\n\tmove.w (a4)+,(a2)\n\tmove.w (a4)+,4(a3)\n\tmove.l (a4)+,(a3)\n\tmove.l a4,4(a2)\n\tmove.b #1,$39(a0)\n\tlsl.w #1,d1\n\tlea _G_h01_29DE,a2\n\tmove.w 0(a2,d1.w),d1\n\tadd.w $c(a0),d1\n\tlsl.l d3,d1\n\tmove.w d1,6(a3)\n\tbtst d7,_G_h01_2A0A\n\tbeq _L5A46\n\tmove.l d1,d2\n\tclr.l d3\n\tmove.b $25(a0),d3\n\tlsl.l d3,d2\n\tmove.l d2,$14(a0)\n_L5A46\n\tswap d1\n\tmove.l d1,(a0)\n\tmovem.l (sp)+,a2-a4\n\trts\n_resident_asm_5A50\n\tdseg\n\tpublic _G_h01_2B4E,_G_h01_29DE,_G_h01_2A0A\n\tend\n'


def audit_producer(root,job,source_bytes):
    from common import require,sha256
    from repo_paths import canonical_path,candidate_path,active_files
    import check_data_contribution as score
    job=candidate_path(root,root/job);work=job/'sys/work'
    for p in active_files(job):
        require(candidate_path(root,p).is_relative_to(job),'producer input escapes selected job')
    request=json.loads((job/'request.json').read_bytes());receipt=json.loads((job/'result.json').read_bytes())
    require(receipt['request']==request and receipt['all_steps_succeeded'] is True,'request/receipt')
    require(request['steps']==[dict(index=i,command=c,returncode_file='step-%02d.rc'%i) for i,c in enumerate(COMMANDS)],'command recipe')
    require(receipt['steps']==[dict(s,returncode=0) for s in request['steps']],'guest statuses')
    expected={'bind.asm':BIND,'rng.asm':expected_source(True),'note.asm':NOTE_SOURCE}
    require(source_bytes in [expected_source(True),NOTE_SOURCE],'unknown batch source')
    require(request['source_files']==[dict(path=n,sha256=sha256(expected[n])) for n in sorted(expected)],'source inventory')
    for name,value in expected.items():require((work/name).read_bytes()==value,'source differs from mnemonic recipe')
    pins=[]
    for version in ('5.0a','3.6a'):
        inv=json.loads(canonical_path(root,'evidence/toolchain/aztec-'+version+'.json').read_bytes())
        for disk in inv['disks']:
            if disk['status']!='VALIDATED':continue
            manifest=disk['filesystem_manifest'] if version=='5.0a' else disk['manifest']
            volume=disk['volume'] if version=='5.0a' else manifest['volume']
            pins += [dict(path='toolchain/installed/aztec-'+version+'/'+volume+'/'+e['path'],sha256=e['sha256']) for e in manifest['entries'] if e['kind']=='file']
    require(request['pinned_inputs']==pins,'full pinned inventory')
    for pin in pins:require(sha256(canonical_path(root,pin['path']).read_bytes())==pin['sha256'],'pinned input differs')
    lock=json.loads(canonical_path(root,'toolchain/candidate-lock.json').read_bytes())
    require(request['archive_sha256']==lock['sha256']==sha256(canonical_path(root,lock['archive']).read_bytes()),'archive')
    require(request['rom_sha256']==next(x['sha256'] for x in lock['members'] if x['path']=='Kick30.rom'),'ROM pin')
    require(sha256(Path(request['emulator']).read_bytes())==request['emulator_sha256'],'emulator')
    for name,key in [('kick.rom','rom_sha256'),('worker.uae','config_sha256'),('sys/s/startup-sequence','guest_script_sha256')]:
        require(sha256((job/name).read_bytes())==request[key],'environment hash')
    previous=score.COMMANDS
    try:
        score.COMMANDS=COMMANDS
        score.environment(root,job) # Full exact settings/mounts/script and guest OS copies.
    finally:score.COMMANDS=previous
    artifacts=receipt['artifacts'];names=[a['path'] for a in artifacts]
    require(len(names)==len(set(names)) and set(names)=={p.relative_to(work).as_posix() for p in active_files(work)},'complete artifact inventory')
    for a in artifacts:
        require(Path(a['path']).name==a['path'],'artifact path')
        raw=(work/a['path']).read_bytes();require(len(raw)==a['size'] and sha256(raw)==a['sha256'],'artifact hash')
    require((work/'done.txt').read_bytes().strip()==b'done' and all((work/('step-%02d.rc'%i)).read_bytes().strip()==b'0' for i in range(len(COMMANDS))),'completion')
    return dict(job=job.relative_to(root).as_posix(),request_sha256=sha256((job/'request.json').read_bytes()),receipt_sha256=sha256((job/'result.json').read_bytes()),audit='FULL_PINNED_GRAPH_CHECKED',artifact_sha256={a['path']:a['sha256'] for a in artifacts})


def object_rng(raw):
    """Whole AJ grammar for this measured external-long DATA-reference control.

    No unparsed token, symbol, section, COMMON, trailer or addend is accepted.
    Admission additionally requires the independently rederived non-C predicate,
    exact mnemonic recipe and complete pinned producer graph.
    """
    from common import require,sha256
    require(len(raw)>=36 and raw[:10]==b'AJ'+bytes(8),'AJ header')
    u16=lambda p:int.from_bytes(raw[p:p+2],'big')
    u32=lambda p:int.from_bytes(raw[p:p+4],'big')
    require((u32(10),u32(14),u32(18))==(56,0,0),'whole object sections')
    start=u32(24)*4;syms=u16(28)*4;end=u16(30)*4
    require(start==36 and syms<=end==u16(32)*4==len(raw) and u16(22)==4 and raw[34:36]==b'\x80\0','AJ bounds/model')
    definitions=[];p=syms
    for index in range(4):
        require(p+4<=end,'truncated symbol')
        kind,attr=raw[p:p+2];value=u16(p+2);p+=4
        segment=None
        if kind==7:
            require(attr==14 and value==0 and p+2<=end,'external DATA attributes');segment=u16(p);p+=2
        else:require(kind==2 and attr==8,'CODE symbol attributes')
        stop=raw.find(b'\0',p,end);require(stop>=p,'symbol terminator')
        name=raw[p:stop].decode('ascii');p=stop+1
        definitions.append(dict(kind=kind,attribute=attr,offset=value,segment=segment,name=name))
    require(end-p<=3 and raw[p:]==bytes(end-p),'symbol trailer')
    require(definitions==[dict(kind=2,attribute=8,offset=0,segment=None,name='_resident_asm_559E'),dict(kind=2,attribute=8,offset=56,segment=None,name='_resident_asm_55D6'),dict(kind=7,attribute=14,offset=0,segment=1,name='_G_h01_2B89'),dict(kind=7,attribute=14,offset=0,segment=1,name='_G_h01_2B8A')],'complete symbol inventory')
    code=bytearray();fixups=[];p=start
    while len(code)<56:
        require(p<syms,'truncated CODE');token=raw[p];p+=1
        if 0x10<=token<=0x1f:
            n=token-15;require(p+n<=syms and len(code)+n<=56,'literal extent');code+=raw[p:p+n];p+=n
        elif token==0xfd:
            require(p+2<=syms and raw[p] in (0x72,0x73) and raw[p+1]==0,'named zero-addend long fixup')
            index=raw[p]-0x70;p+=2
            fixups.append(dict(offset=len(code),width=4,type='HUNK_RELOC32',symbol=definitions[index]['name'],addend=0));code+=bytes(4)
        else:require(False,'unknown AJ CODE token')
    require(raw[p:syms]==b'\xf5'+bytes(syms-p-1),'empty DATA transition/alignment')
    require(fixups==[dict(offset=10,width=4,type='HUNK_RELOC32',symbol='_G_h01_2B89',addend=0),dict(offset=16,width=4,type='HUNK_RELOC32',symbol='_G_h01_2B8A',addend=0)],'exhaustive fixups')
    return bytes(code),fixups,dict(CODE=56,DATA=0,BSS=0,COMMON=0,symbols=definitions,object_sha256=sha256(raw))


def compare(root,job,source_bytes,original=None):
    from census import verify_lock,_derive_uncached
    from common import require,sha256
    from audio_sequence_data import payload,field
    from analysis_support import decoder
    from hunk import parse
    from overlay_experiment import symbols
    if original is None:
        verify_lock(root);_,files,om=_derive_uncached(root,False);ob=files['DT1:DuckTales']
    else:ob,om=original
    oracle=payload(ob,om,0)[0x559e:0x55d6];w=root/job/'sys/work';obj=(w/'rng.o').read_bytes()
    object_code,refs,structure=object_rng(obj)
    linked=(w/'rng.exe').read_bytes();lm=parse(linked);code=payload(linked,lm,0);sm=symbols((w/'rng.sym').read_text())
    require([(h['number'],h['type'],h['allocated_size'],h['initialized_size']) for h in lm['hunks']]==[(0,'CODE',56,56),(1,'DATA',12,12),(2,'BSS',4,0)],'whole linked topology')
    require(payload(linked,lm,1)==bytes(12),'diagnostic harness DATA')
    require(sm=={(0,'__H0_org'):0,(0,'_resident_asm_559E'):0,(0,'_resident_asm_55D6'):56,(0,'__H0_end'):56,(1,'__H1_org'):0,(1,'_G_h01_2B89'):0,(1,'_G_h01_2B8A'):2,(1,'_G_h01_2B4E'):4,(1,'_G_h01_29DE'):6,(1,'_G_h01_2A0A'):8,(1,'__H1_end'):12,(2,'__H2_org'):12,(2,'__H2_end'):12},'complete symbol map')
    original_rels=[field(r) for r in om['relocations'] if r['source_hunk']==0 and 0x559e<=r['source_offset']<0x55d6]
    require(original_rels==[dict(source_hunk=0,source_offset=0x55a8,target_hunk=1,addend_raw=0x2b89,type='HUNK_RELOC32',width=4),dict(source_hunk=0,source_offset=0x55ae,target_hunk=1,addend_raw=0x2b8a,type='HUNK_RELOC32',width=4)],'original named LEA targets')
    require([field(r) for r in lm['relocations']]==[dict(source_hunk=0,source_offset=10,target_hunk=1,addend_raw=0,type='HUNK_RELOC32',width=4),dict(source_hunk=0,source_offset=16,target_hunk=1,addend_raw=2,type='HUNK_RELOC32',width=4)],'candidate named relocations')
    bindings=[];cursor=0
    for ref,original in zip(refs,original_rels):
        p=ref['offset'];require(object_code[cursor:p]==code[cursor:p]==oracle[cursor:p],'ordinary bytes')
        require(code[p:p+4]==sm[(1,ref['symbol'])].to_bytes(4,'big'),'linked named target payload')
        require(oracle[p:p+4]==original['addend_raw'].to_bytes(4,'big'),'oracle target payload')
        require(object_code[p:p+4]==bytes(4),'object external addend')
        bindings.append(dict(ref,original_hunk=1,original_target=original['addend_raw'],candidate_hunk=1,candidate_target=sm[(1,ref['symbol'])],basis='DECODED_ORIGINAL_LEA_PLUS_AJ_EXTERNAL_DATA_SYMBOL_AND_LINK_MAP'))
        cursor=p+4
    require(object_code[cursor:]==code[cursor:]==oracle[cursor:],'terminal ordinary bytes')
    decoded=list(decoder().disasm(oracle,0x559e));require(sum(i.size for i in decoded)==56,'whole original decode')
    rotations=[dict(offset=i.address,mnemonic=i.mnemonic,operands=i.op_str) for i in decoded if i.mnemonic.startswith(('roxl','roxr'))]
    require([(r['offset'],r['mnemonic'],r['operands']) for r in rotations]==[(0x55b6,'roxl.b','#$4, d0'),(0x55c0,'roxl.b','#$1, d0'),(0x55c4,'roxr.b','#$1, d0'),(0x55c8,'roxr.w','(a1)')],'CCR-X observations')
    return dict(verdict='EQUAL_CANDIDATE',span=dict(hunk=0,start=0x559e,end=0x55d6,size=56,sha256=sha256(oracle)),oracle_sha256=sha256(ob),object_structure=structure,named_relocation_bindings=bindings,ordinary_bytes_compared=48,relocated_bytes_compared_by_named_identity=8,ccr_x_observations=rotations,linked_sha256=sha256(linked),source_sha256=sha256(source_bytes),source_acceptance=False,accounting_acceptance=False,proof_level=None,historical_owner='UNKNOWN',historical_object_membership='UNKNOWN',natural_root_layout_proof=False)



MAP='reconstructed_asm'
MANIFEST='evidence/reconstructed-asm/batch.json'
FACT='evidence/reconstructed-asm/resident_asm_559E.json'
SOURCE='src/recovered/asm-reconstructed/resident_asm_559E.asm'
CANDIDATE='evidence/rules/asm-reconstructed/resident_asm_559E.asm'


def document(root,name):
    from repo_paths import canonical_path
    return json.loads(canonical_path(root,name).read_bytes())


def non_c_predicate(blob,model,start,end):
    """Require the complete X-carry register/memory loop, decoded on every read.

    68000 MOVE/EOR leave X intact. The two ROXL.B operations, intervening MOVE,
    ROXR.B and ROXR.W memory form a cross-instruction extend-state chain whose
    X input/output cannot be named by ordinary pinned Aztec C expressions.
    A normal rotate or ADD/Bcc idiom is insufficient. No absence-of-frame test.
    """
    from common import require
    from audio_sequence_data import payload
    from analysis_support import decoder
    raw=payload(blob,model,0)
    require(0<=start<end<=len(raw),'predicate bounds')
    items=list(decoder().disasm(raw[start:end],start))
    require(items and sum(i.size for i in items)==end-start and all(not i.mnemonic.startswith('dc.') for i in items),'whole instruction decode')
    pattern=[('move.b','$1(a1), d0'),('roxl.b','#$4, d0'),('eor.b','d0, $1(a1)'),
      ('move.b','$1(a1), d0'),('roxl.b','#$1, d0'),('move.b','(a0), d0'),
      ('roxr.b','#$1, d0'),('move.b','d0, (a0)'),('roxr.w','(a1)')]
    hits=[]
    for n in range(len(items)-len(pattern)):
        seq=items[n:n+len(pattern)];tail=items[n+len(pattern)]
        if [(i.mnemonic,i.op_str) for i in seq]!=pattern:continue
        # Decode DBRA's actual target rather than trusting a curated offset.
        if tail.mnemonic=='dbra' and tail.op_str=='d7, $%x'%seq[0].address:
            hits.append(dict(start=seq[0].address,end=tail.address+tail.size,
                instructions=[dict(offset=i.address,mnemonic=i.mnemonic,operands=i.op_str) for i in seq+[tail]]))
    require(len(hits)==1,'non-C CCR-X chain not independently present')
    return dict(kind='CCR_X_REGISTER_MEMORY_ROTATION_LOOP',chain=hits[0],c_compatible=False,
                basis='Cross-instruction 68000 X state and memory ROXR; no C flag primitive.')


def validate_fact(root,blob,model,analysis,fact):
    from common import require,sha256
    from audio_sequence_data import payload,field
    require(set(fact)=={'schema_version','id','oracle_sha256','original','predicate','source','candidate','source_sha256','relocations','historical_owner','historical_tu','original_filename'},'ASM fact fields (masks/opaque bindings reject)')
    require(type(fact['schema_version']) is int and fact['schema_version']==1 and fact['id']=='resident_asm_559E','supported ASM fact')
    require(fact['source']==SOURCE and fact['candidate']==CANDIDATE,'ASM source paths')
    require(fact['historical_owner']==fact['historical_tu']=='UNKNOWN' and fact['original_filename'] is None,'unsupported historical provenance')
    require(fact['oracle_sha256']==sha256(blob),'stale ASM oracle fact')
    o=fact['original'];require(set(o)=={'hunk','start','end','size','sha256'},'complete span fields')
    require(all(type(o[k]) is int for k in ['hunk','start','end','size']),'integer span')
    require(o['hunk']==0 and o['start']==0x559e and o['end']==0x55d6 and o['size']==o['end']-o['start'],'whole supported contiguous span')
    raw=payload(blob,model,0)[o['start']:o['end']]
    require(sha256(raw)==o['sha256'],'stale ASM span fact')
    f=next((f for f in analysis['functions'] if f['id']=='resident_F_559E'),None)
    require(f is not None and (f['hunk'],f['start'],f['end'],f['size'])==(0,o['start'],o['end'],o['size']) and not f['boundary_stops'] and not f['undecoded_gaps'] and any(e['kind']=='DIRECT_CALL' for e in f['entry_evidence']),'independent complete function boundary')
    from analysis_support import decoder
    instructions=list(decoder().disasm(raw,o['start']))
    require([(i.mnemonic,i.op_str) for i in instructions[:2]]==[('movem.l','d7/a0-a1, -(a7)'),('move.w','#$7, d7')] and [(i.mnemonic,i.op_str) for i in instructions[-2:]]==[('movem.l','(a7)+, d7/a0-a1'),('rts','')], 'complete register-save/restore boundary')
    neighbour=next(decoder().disasm(payload(blob,model,0)[o['end']:o['end']+8],o['end']),None)
    require(neighbour is not None and (neighbour.mnemonic,neighbour.op_str)==('move.w','$dff002.l, d0'),'independent next IRQ boundary')
    predicate=non_c_predicate(blob,model,o['start'],o['end'])
    require(fact['predicate']==predicate,'stale ASM non-C predicate fact')
    expected=[]
    for r in model['relocations']:
        if r['source_hunk']==0 and r['source_offset']<o['end'] and o['start']<r['source_offset']+r['width']:
            require(r['source_offset']>=o['start'] and r['source_offset']+r['width']<=o['end'],'straddling ASM relocation')
            expected.append(dict(field(r),symbol='_G_h01_%04X'%r['addend_raw']))
    require(fact['relocations']==expected and len(expected)==2 and [r['symbol'] for r in expected]==['_G_h01_2B89','_G_h01_2B8A'],'unnamed/masked/wrong relocation')
    require(fact['source_sha256']==sha256(expected_source(True)),'source recipe fact changed')
    return predicate


def verify(root,blob,model,analysis,fact,batch=None):
    from common import require,sha256,json_bytes
    from repo_paths import canonical_path
    require([(h['number'],h['type'],h['node']) for h in model['hunks'][:2]]==[(0,'CODE','resident'),(1,'DATA','resident')],'original ASM containers')
    (validate_fact if fact['id']=='resident_asm_559E' else validate_note_fact)(root,blob,model,analysis,fact)
    direct_entry(blob,model,fact['original']['start'],0x4ca2 if fact['id']=='resident_asm_559E' else 0x5aac)
    # A narrow independent mnemonic recipe prevents consistently rehashed
    # opaque carriers, directives and stale output from replacing this source.
    src=canonical_path(root,fact['candidate']).read_bytes()
    require(src==source_for(fact['id']),'ASM source differs from independent mnemonic recipe; dc/opaque carriers reject')
    batch=document(root,MANIFEST) if batch is None else batch
    require(set(batch)=={'schema_version','profile','facts','fact_sha256','job','request_sha256','receipt_sha256','artifacts'},'batch fields')
    require(batch['schema_version']==1 and batch['profile']=='aztec36' and batch['facts']==FACTS and batch['fact_sha256']=={n:sha256(json_bytes(document(root,n))) for n in FACTS},'complete ASM batch/fact pins')
    require(__import__('re').fullmatch(r'build/worker-jobs/sol-audio-asm-[A-Za-z0-9_-]+',batch['job']),'ASM producer job path')
    producer=audit_producer(root,Path(batch['job']),src)
    require(producer['request_sha256']==batch['request_sha256'] and producer['receipt_sha256']==batch['receipt_sha256'] and producer['artifact_sha256']==batch['artifacts'],'ASM producer SHA pins')
    report=(compare if fact['id']=='resident_asm_559E' else compare_note)(root,Path(batch['job']),src,original=(blob,model))
    require(report['span']==fact['original'],'exact whole span comparison changed')
    report.update(id=fact['id'],category='RECONSTRUCTED_ASM',state='FUNCTION_CODE_MATCH',
        non_c_predicate=fact['predicate'],fact_sha256=sha256(json_bytes(fact)),producer=producer,
        object_membership='UNKNOWN',data_credit=0,verifier_identity={
            n:sha256(canonical_path(root,'tools/'+n).read_bytes()) for n in ['reconstructed_asm.py','check_data_contribution.py','hunk.py','audio_sequence_data.py','analysis_support.py','repo_paths.py','common.py']})
    return report


def rows(root,blob,model,analysis,ledger,*,staged=False):
    from common import require,sha256
    from repo_paths import canonical_path
    entries=ledger.get(MAP,{})
    require(set(entries)<=set(SPECS),'unknown canonical reconstructed ASM entry')
    if not entries and not staged:return []
    batch=document(root,MANIFEST);results=[]
    for name in FACTS:
        fact=document(root,name);ident=fact['id']
        if not staged and ident not in entries:continue
        report=verify(root,blob,model,analysis,fact,batch)
        if ident not in entries:results.append(report);continue
        item=entries[ident];proof_path='recovery/proofs/asm-reconstructed/'+ident+'.json'
        require(set(item)=={'state','fact','source','source_sha256','proof','proof_sha256'} and item['state']=='FUNCTION_CODE_MATCH' and item['fact']==name and item['source']==fact['source'] and item['proof']==proof_path,'ASM ownership identity')
        src=canonical_path(root,item['source']).read_bytes();proofraw=canonical_path(root,item['proof']).read_bytes();proof=json.loads(proofraw)
        require(src==source_for(ident) and sha256(src)==item['source_sha256']==fact['source_sha256'],'canonical ASM source')
        require(sha256(proofraw)==item['proof_sha256'] and set(proof)=={'fact','comparison','regression'} and proof['regression'].get('passed') is True,'ASM proof/gate')
        comparable=lambda r:{k:v for k,v in r.items() if k!='verifier_identity'}
        require(proof['fact']==fact and comparable(proof['comparison'])==comparable(report) and proof['comparison'].get('verifier_identity'),'canonical ASM proof no longer rederives')
        for other,rec in ledger.get('functions',{}).items():
            o=rec['evidence_extent'];require(o['hunk']!=0 or o['end']<=fact['original']['start'] or o['start']>=fact['original']['end'],'ASM overlaps canonical C')
        for other in ['mixed_source_objects','dead_code_functions']:
            for rec in ledger.get(other,{}).values():
                p=document(root,rec['proof']);e=p.get('complete_extent') or p.get('evidence_extent') or p.get('original')
                if e:require(e['hunk']!=0 or e['end']<=fact['original']['start'] or e['start']>=fact['original']['end'],'ASM overlaps another source route')
        results.append(dict(report,acceptance=True,source_acceptance=True,proof_level='FUNCTION_CODE_MATCH',source=fact['source'],proof=proof_path))
    return results


def contributions(root,records):
    """Only AJ-produced bytes and independently bound named fixups reach output."""
    from common import require
    result=[]
    for r in records:
        if not r.get('acceptance'):continue
        obj=root/r['producer']['job']/('sys/work/'+SPECS[r['id']]['prefix']+'.o');code,fixups,_=(object_rng if r['id']=='resident_asm_559E' else object_note)(obj.read_bytes());out=bytearray(code);rels=[]
        for f,b in zip(fixups,r['named_relocation_bindings']):
            require(f['symbol']==b['symbol'] and f['offset']==b['offset'],'ASM fixup identity')
            p=f['offset'];out[p:p+4]=b['original_target'].to_bytes(4,'big')
            rels.append(dict(source_offset=r['span']['start']+p,target_hunk=b['original_hunk'],type=f['type'],width=f['width'],addend_raw=b['original_target']))
        result.append(dict(id=r['id'],hunk=0,start=r['span']['start'],end=r['span']['end'],category='RECONSTRUCTED_ASM',bytes=bytes(out),relocations=rels))
    return result


def input_identity(root):
    from common import sha256
    from repo_paths import canonical_path,candidate_path
    root=Path(root);names={MANIFEST,*FACTS,*[candidate_for(i) for i in SPECS]};external={}
    p=canonical_path(root,MANIFEST)
    if p.exists():
        batch=document(root,MANIFEST);job=batch['job']
        names.update(job+'/'+n for n in ['request.json','result.json','worker.uae','sys/s/startup-sequence','kick.rom'])
        names.update(job+'/sys/work/'+n for n in batch['artifacts'])
        request=json.loads(candidate_path(root,root/job/'request.json').read_bytes())
        names.update(p['path'] for p in request['pinned_inputs']);lock=document(root,'toolchain/candidate-lock.json');names.add(lock['archive'])
        for folder in ['c','l','libs','devs']:
            from repo_paths import active_files
            names.update(p.relative_to(root).as_posix() for p in active_files(root/job/'sys'/folder))
        for n in ['evidence/toolchain/aztec-3.6a.json','evidence/toolchain/aztec-5.0a.json','toolchain/candidate-lock.json']:names.add(n)
        external[request['emulator']]=sha256(Path(request['emulator']).read_bytes())
    ledger_path=canonical_path(root,'recovery/ledger.json')
    state=document(root,'recovery/ledger.json') if ledger_path.exists() else {}
    for item in state.get(MAP,{}).values():names.update([item['source'],item['proof'],item['fact']])
    def path(n):return candidate_path(root,root/n) if n.startswith('build/worker-jobs/') else canonical_path(root,n)
    return {**{str(path(n)):sha256(path(n).read_bytes()) if path(n).exists() else None for n in sorted(names)},**external}

SPECS={'resident_asm_559E':dict(start=0x559e,end=0x55d6,prefix='rng'),
       'resident_asm_59A4':dict(start=0x59a4,end=0x5a50,prefix='note')}
FACTS=['evidence/reconstructed-asm/'+i+'.json' for i in SPECS]
def candidate_for(ident):return 'evidence/rules/asm-reconstructed/'+ident+'.asm'
def source_for(ident):return expected_source(True) if ident=='resident_asm_559E' else NOTE_SOURCE


def a4_predicate(blob,model,start,end):
    """Reserved small-data A4 is saved, replaced and consumed as a record cursor.

    This is not merely a write to A4: require an original A4-world displacement,
    self-indexed pointer load, typed postincrement word/word/long accesses and
    a restore of the caller's A4 world before return, in one complete routine.
    """
    from common import require
    from audio_sequence_data import payload
    from analysis_support import decoder
    ins=list(decoder().disasm(payload(blob,model,0)[start:end],start))
    require(ins and sum(i.size for i in ins)==end-start,'A4 complete decode')
    require([(i.mnemonic,i.op_str) for i in ins[:1]]==[('movem.l','a2-a4, -(a7)')] and [(i.mnemonic,i.op_str) for i in ins[-2:]]==[('movem.l','(a7)+, a2-a4'),('rts','')],'A4 save/restore contract')
    pattern=[('lea.l','-$581a(a4), a4'),('movea.l','(a4, d0.w), a4'),
             ('move.w','(a4)+, (a2)'),('move.w','(a4)+, $4(a3)'),('move.l','(a4)+, (a3)'),('move.l','a4, $4(a2)')]
    hits=[n for n in range(len(ins)-len(pattern)+1) if [(i.mnemonic,i.op_str) for i in ins[n:n+len(pattern)]]==pattern]
    require(len(hits)==1,'non-C saved-world A4 record cursor absent')
    seq=ins[hits[0]:hits[0]+len(pattern)]
    require(seq[0].address==0x5a00 and start==0x59a4 and end==0x5a50,'A4 bounded consumer')
    return dict(kind='SAVED_A4_WORLD_REPLACED_BY_TYPED_RECORD_CURSOR',site=seq[0].address,
        world_symbol='_G_h01_27E4',world_hunk=1,world_offset=32766-22554,a4_bias=32766,
        displacement=-22554,access_widths=[2,2,4],restores_a4=True,c_compatible=False,
        instructions=[dict(offset=i.address,mnemonic=i.mnemonic,operands=i.op_str) for i in seq])


def validate_note_fact(root,blob,model,analysis,fact):
    from common import require,sha256
    from audio_sequence_data import payload,field
    require(set(fact)=={'schema_version','id','oracle_sha256','original','predicate','source','candidate','source_sha256','relocations','historical_owner','historical_tu','original_filename'},'ASM fact fields')
    require(type(fact['schema_version']) is int and fact['schema_version']==1 and fact['id']=='resident_asm_59A4' and fact['source']=='src/recovered/asm-reconstructed/'+fact['id']+'.asm' and fact['candidate']==candidate_for(fact['id']),'A4 source identity')
    require(fact['historical_owner']==fact['historical_tu']=='UNKNOWN' and fact['original_filename'] is None,'A4 historical ownership')
    require(fact['oracle_sha256']==sha256(blob),'stale A4 oracle')
    o=fact['original'];require(set(o)=={'hunk','start','end','size','sha256'} and all(type(o[k]) is int for k in ['hunk','start','end','size']),'A4 integer complete extent')
    raw=payload(blob,model,0)[0x59a4:0x5a50]
    require(o==dict(hunk=0,start=0x59a4,end=0x5a50,size=172,sha256=sha256(raw)),'partial/stale A4 span')
    f=next((f for f in analysis['functions'] if f['id']=='resident_F_59A4'),None)
    require(f is not None and (f['hunk'],f['start'],f['end'],f['size'])==(0,0x59a4,0x5a50,172) and f['boundary_stops']==[dict(offset=p,reason='A4_BASE_DATAFLOW_UNPROVEN') for p in [0x5a00,0x5a04,0x5a4a]] and not f['undecoded_gaps'] and any(e['kind']=='DIRECT_CALL' for e in f['entry_evidence']),'independent A4 complete boundary')
    require(analysis['a4']['bias']==32766,'independent A4 world bias')
    require(fact['predicate']==a4_predicate(blob,model,o['start'],o['end']),'stale A4 predicate')
    touched=[r for r in model['relocations'] if r['source_hunk']==0 and r['source_offset']<o['end'] and o['start']<r['source_offset']+r['width']]
    require(all(o['start']<=r['source_offset'] and r['source_offset']+r['width']<=o['end'] for r in touched),'straddling A4 relocation')
    wanted=[dict(field(r),symbol='_G_h01_%04X'%r['addend_raw']) for r in touched]
    require(len(wanted)==3 and fact['relocations']==wanted,'A4 unnamed/masked relocation')
    require(fact['source_sha256']==sha256(NOTE_SOURCE),'A4 independent mnemonic source recipe')


def object_note(raw):
    """Complete bounded AJ CODE + three named external-long DATA references."""
    from common import require,sha256
    require(len(raw)>=36 and raw[:10]==b'AJ'+bytes(8),'A4 AJ header')
    u16=lambda p:int.from_bytes(raw[p:p+2],'big');u32=lambda p:int.from_bytes(raw[p:p+4],'big')
    require((u32(10),u32(14),u32(18))==(172,0,0),'A4 complete sections')
    begin=u32(24)*4;symbols=u16(28)*4;end=u16(30)*4
    require(begin==36 and symbols<=end==u16(32)*4==len(raw) and u16(22)==5 and raw[34:36]==b'\x80\0','A4 object structure')
    names=[];p=symbols
    for kind,value,name in [(2,0,'_resident_asm_59A4'),(2,172,'_resident_asm_5A50'),(7,0,'_G_h01_2B4E'),(7,0,'_G_h01_29DE'),(7,0,'_G_h01_2A0A')]:
        require(p+4<=end and raw[p]==kind and raw[p+1]==(8 if kind==2 else 14) and u16(p+2)==value,'A4 symbol type/value');p+=4
        if kind==7:require(u16(p)==1,'A4 external DATA section');p+=2
        stop=raw.find(b'\0',p,end);require(stop>=p and raw[p:stop].decode('ascii')==name,'A4 named symbol');p=stop+1;names.append(name)
    require(end-p<=3 and raw[p:]==bytes(end-p),'A4 symbol trailer')
    code=bytearray();fixups=[];p=begin
    while len(code)<172:
        require(p<symbols,'truncated A4 CODE');token=raw[p];p+=1
        if 0x10<=token<=0x1f:
            n=token-15;require(p+n<=symbols and len(code)+n<=172,'A4 literal extent');code+=raw[p:p+n];p+=n
        elif token==0xfd:
            require(p+2<=symbols and raw[p] in (0x72,0x73,0x74) and raw[p+1]==0,'A4 named fixup')
            fixups.append(dict(offset=len(code),width=4,type='HUNK_RELOC32',symbol=names[raw[p]-0x70],addend=0));p+=2;code+=bytes(4)
        else:require(False,'A4 unsupported object token')
    require(raw[p:symbols]==b'\xf5'+bytes(symbols-p-1),'A4 empty DATA/trailer')
    require(fixups==[dict(offset=p,width=4,type='HUNK_RELOC32',symbol=n,addend=0) for p,n in [(50,'_G_h01_2B4E'),(122,'_G_h01_29DE'),(142,'_G_h01_2A0A')]],'A4 exhaustive fixups')
    return bytes(code),fixups,dict(CODE=172,DATA=0,BSS=0,COMMON=0,symbols=names,object_sha256=sha256(raw))


def compare_note(root,job,source_bytes,original):
    from common import require,sha256
    from audio_sequence_data import payload,field
    from hunk import parse
    from overlay_experiment import symbols
    ob,om=original;oracle=payload(ob,om,0)[0x59a4:0x5a50];work=root/job/'sys/work'
    object_code,fixups,structure=object_note((work/'note.o').read_bytes())
    linked=(work/'note.exe').read_bytes();lm=parse(linked);code=payload(linked,lm,0);sm=symbols((work/'note.sym').read_text())
    require([(h['number'],h['type'],h['allocated_size'],h['initialized_size']) for h in lm['hunks']]==[(0,'CODE',172,172),(1,'DATA',12,12),(2,'BSS',4,0)],'A4 complete link topology')
    require(payload(linked,lm,1)==bytes(12),'A4 harness DATA')
    require(sm=={(0,'__H0_org'):0,(0,'_resident_asm_59A4'):0,(0,'_resident_asm_5A50'):172,(0,'__H0_end'):172,(1,'__H1_org'):0,(1,'_G_h01_2B89'):0,(1,'_G_h01_2B8A'):2,(1,'_G_h01_2B4E'):4,(1,'_G_h01_29DE'):6,(1,'_G_h01_2A0A'):8,(1,'__H1_end'):12,(2,'__H2_org'):12,(2,'__H2_end'):12},'A4 complete symbol map')
    originals=[field(r) for r in om['relocations'] if r['source_hunk']==0 and 0x59a4<=r['source_offset']<0x5a50]
    expected=[dict(source_hunk=0,source_offset=0x59a4+p,target_hunk=1,addend_raw=o,type='HUNK_RELOC32',width=4) for p,o in [(50,0x2b4e),(122,0x29de),(142,0x2a0a)]]
    require(originals==expected,'A4 original exhaustive fields')
    require([field(r) for r in lm['relocations']]==[dict(source_hunk=0,source_offset=f['offset'],target_hunk=1,addend_raw=sm[(1,f['symbol'])],type='HUNK_RELOC32',width=4) for f in fixups],'A4 linked exhaustive fields')
    cursor=0;bindings=[]
    for f,o in zip(fixups,originals):
        p=f['offset'];require(oracle[cursor:p]==code[cursor:p]==object_code[cursor:p],'A4 ordinary bytes')
        require(object_code[p:p+4]==bytes(4) and code[p:p+4]==sm[(1,f['symbol'])].to_bytes(4,'big') and oracle[p:p+4]==o['addend_raw'].to_bytes(4,'big'),'A4 named payload')
        bindings.append(dict(f,original_hunk=1,original_target=o['addend_raw'],candidate_hunk=1,candidate_target=sm[(1,f['symbol'])],basis='ORIGINAL_RELOCATION_AJ_DATA_EXTERNAL_AND_LINK_MAP'));cursor=p+4
    require(oracle[cursor:]==code[cursor:]==object_code[cursor:],'A4 terminal ordinary bytes')
    return dict(verdict='EQUAL_CANDIDATE',span=dict(hunk=0,start=0x59a4,end=0x5a50,size=172,sha256=sha256(oracle)),oracle_sha256=sha256(ob),object_structure=structure,named_relocation_bindings=bindings,ordinary_bytes_compared=160,relocated_bytes_compared_by_named_identity=12,a4_observations=a4_predicate(ob,om,0x59a4,0x5a50),linked_sha256=sha256(linked),source_sha256=sha256(source_bytes),source_acceptance=False,accounting_acceptance=False,proof_level=None,historical_owner='UNKNOWN',historical_object_membership='UNKNOWN',natural_root_layout_proof=False)


def direct_entry(blob,model,target,site):
    from common import require
    from analysis_support import decoder
    from audio_sequence_data import payload
    i=next(decoder().disasm(payload(blob,model,0)[site:site+8],site,count=1),None)
    require(i is not None and i.mnemonic.split('.')[0] in ['jsr','bsr'] and i.op_str in ['$%x'%target,'$%x(pc)'%target],'independent decoded inbound call anchor')
