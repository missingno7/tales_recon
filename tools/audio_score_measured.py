"""Whole measured typed score provider, including complete AJ objects and debt partitions."""
from names import read_source, source_path as source_file
from validation_memo import shared
import json,re
from pathlib import Path
from collections import Counter
from common import require,sha256,json_bytes
from repo_paths import canonical_path,candidate_path,active_files
from audio_sequence_data import payload,field
from audio_score_catalogue import rederive,INTERVAL,ZERO_DEBT
from audio_score_commands import source,encode,check

IDENT='resident_audio_score'
FACT='evidence/code-data-providers/score.json'
MANIFEST='evidence/code-data-providers/score-batch.json'
CATEGORY='TYPED_CODE_DATA'
MAP='code_data_providers'
ODD_SOURCE=b'HEADER macro\n\tdc.b \\1,\\2\n\tendm\nSC_STOP macro\n\tdc.b $88\n\tendm\n\tcseg\n\tpublic _odd_begin,_odd_end\n_odd_begin:\n\tHEADER 0,1\n\tSC_STOP\n_odd_end:\n\tend\n'


def document(root,name):return json.loads(canonical_path(root,name).read_bytes())


def members(fact,layout):
    labels=set(layout['proven_labels']);result={}
    for member in fact['objects']:
        rows=[c for c in fact['commands'] if member['start']<=c['offset']<member['end']-1]
        raw=source(member,rows,labels);sem=encode(rows,labels)
        result[member['prefix']]=dict(member=member,source=raw,semantic=sem)
    return result


def validate(root,blob,model,fact):
    require(set(fact)=={'schema_version','id','oracle_sha256','grammar_sha256','commands','objects','historical_owner','historical_tu','original_filename'},'measured score fact fields; raw carriers/masks reject')
    require(fact['schema_version']==2 and type(fact['schema_version']) is int and fact['id']==IDENT,'measured score identity')
    require(fact['historical_owner']==fact['historical_tu']=='UNKNOWN' and fact['original_filename'] is None,'measured score historical provenance')
    for c in fact['commands']:check(c)
    from audio_score_grammar import derive
    grammar=derive(blob,model)
    # This single grammar identity includes every bound handler, including
    # rejected unused handlers; a change stales every object in this batch.
    require(fact['grammar_sha256']==sha256(json_bytes(grammar)),'stale grammar or handler binding for every stream')
    require(fact['oracle_sha256']==sha256(blob),'stale measured score oracle')
    grammar,layout,objects=rederive(root,blob,model,grammar=grammar)
    labels=set(layout['proven_labels'])
    for c in fact['commands']:
        if 'target' in c['operands']:require(c['operands']['target'] in labels,'pointer to an unproved stream')
    require(fact['commands']==layout['commands'],'partial stream, measured operand mismatch or uncovered-zero crossing')
    expected=[]
    for obj in objects:
        rows=[c for c in fact['commands'] if obj['start']<=c['offset']<obj['end']-1]
        expected.append(dict(obj,source_sha256=sha256(source(obj,rows,labels))))
    require(fact['objects']==expected,'partial object, guessed gap or clipped provider')
    for item in members(fact,layout).values():
        require(canonical_path(root,item['member']['candidate']).read_bytes()==item['source'],'raw byte carrier or changed grammar macro source')
    return grammar,layout,members(fact,layout)


def commands_for(fact):
    commands=['Old1:bin/as -o '+o['prefix']+'.o '+o['prefix']+'.asm >'+o['prefix']+'-as.log' for o in fact['objects']]
    return commands+['Old1:bin/ln -m -t -o scoreall.exe '+' '.join(o['prefix']+'.o' for o in fact['objects'])+' >scoreall-ln.log',
                     'Old1:bin/as -o odd.o odd.asm >odd-as.log','Old1:bin/ln -m -t -o odd.exe odd.o >odd-ln.log']


def audit_producer(root,batch,expected,commands):
    import check_data_contribution as bounded
    from aztec_worker import ROOT as actual_root
    require(Path(root).resolve()==actual_root.resolve(),'producer toolchain root differs')
    require(re.fullmatch(r'build/(?:worker-jobs|workers/[A-Za-z0-9_-]+)/sol-audio-score-[A-Za-z0-9_-]+',batch['job']),'measured score job path')
    job=candidate_path(root,Path(root)/batch['job']);work=job/'sys/work'
    request=json.loads((job/'request.json').read_bytes());receipt=json.loads((job/'result.json').read_bytes())
    require(sha256((job/'request.json').read_bytes())==batch['request_sha256'] and sha256((job/'result.json').read_bytes())==batch['receipt_sha256'],'score batch SHA pins')
    require(receipt['request']==request and receipt['all_steps_succeeded'] is True,'score request/receipt')
    steps=[dict(index=i,command=c,returncode_file='step-%02d.rc'%i) for i,c in enumerate(commands)]
    require(request['steps']==steps and receipt['steps']==[dict(s,returncode=0) for s in steps],'score producing commands/status')
    require(request['source_files']==[dict(path=n,sha256=sha256(expected[n])) for n in sorted(expected)],'score complete typed source inventory')
    for n,b in expected.items():require((work/n).read_bytes()==b,'score producer source differs from grammar macros')
    pins=[]
    for version in ('5.0a','3.6a'):
        report=document(root,'evidence/toolchain/aztec-'+version+'.json')
        for disk in report['disks']:
            if disk['status']!='VALIDATED':continue
            manifest=disk['filesystem_manifest'] if version=='5.0a' else disk['manifest']
            volume=disk['volume'] if version=='5.0a' else manifest['volume']
            pins += [dict(path='toolchain/installed/aztec-'+version+'/'+volume+'/'+e['path'],sha256=e['sha256']) for e in manifest['entries'] if e['kind']=='file']
    require(request['pinned_inputs']==pins,'score full pinned producer inventory')
    for p in pins:require(sha256(canonical_path(root,p['path']).read_bytes())==p['sha256'],'score pinned producer changed')
    lock=document(root,'toolchain/candidate-lock.json')
    require(request['archive_sha256']==lock['sha256']==sha256(canonical_path(root,lock['archive']).read_bytes()),'score archive pin')
    require(request['rom_sha256']==next(x['sha256'] for x in lock['members'] if x['path']=='Kick30.rom'),'score ROM pin')
    require(sha256(Path(request['emulator']).read_bytes())==request['emulator_sha256'],'score emulator changed')
    for n,k in [('kick.rom','rom_sha256'),('worker.uae','config_sha256'),('sys/s/startup-sequence','guest_script_sha256')]:
        require(sha256((job/n).read_bytes())==request[k],'score environment hash')
    previous=bounded.COMMANDS
    try:bounded.COMMANDS=commands;bounded.environment(root,job,headless=request.get('backend')=='vamos')
    finally:bounded.COMMANDS=previous
    artifacts=receipt['artifacts'];names=[a['path'] for a in artifacts]
    require(len(set(names))==len(names) and set(names)=={p.relative_to(work).as_posix() for p in active_files(work)},'score complete artifact inventory')
    require(batch['artifacts']=={a['path']:a['sha256'] for a in artifacts},'score artifact SHA pins')
    for a in artifacts:
        require(Path(a['path']).name==a['path'],'score artifact path')
        raw=(work/a['path']).read_bytes();require(len(raw)==a['size'] and sha256(raw)==a['sha256'],'score artifact changed')
    require((work/'done.txt').read_bytes().strip()==b'done' and all((work/('step-%02d.rc'%i)).read_bytes().strip()==b'0' for i in range(len(commands))),'score guest completion')
    if request.get('backend') is not None:
        from data_provider_vamos import input_paths,validate
        require(request['backend']==batch.get('backend')=='vamos' and batch['backend_inputs']==input_paths(root,request),'complete pinned score backend inputs')
        validate(root,job,request,receipt,commands)
    else:require(batch.get('backend') is None,'score producer backend differs')
    return dict(job=batch['job'],request_sha256=batch['request_sha256'],receipt_sha256=batch['receipt_sha256'],artifacts=batch['artifacts'],audit='FULL_PINNED_GRAPH_CHECKED')


def object_code(raw,size,definitions,expected_fixups):
    """Complete measured AJ grammar: local CODE definitions and named long fixups.

    FD followed by 70..7F and a high-index byte is the measured packed symbol
    index (low nibble plus high*16), NOT an addend. This batch uses indices <=25.
    Attribute 0C's extra word is the exact reference count, not a symbol index.
    No unknown token/attribute, section, COMMON, addend or trailer is accepted.
    """
    require(len(raw)>=36 and raw[:10]==b'AJ'+bytes(8),'score AJ header')
    u16=lambda p:int.from_bytes(raw[p:p+2],'big');u32=lambda p:int.from_bytes(raw[p:p+4],'big')
    require((u32(10),u32(14),u32(18))==(size,0,0),'score complete AJ sections')
    begin=u32(24)*4;syms=u16(28)*4;end=u16(30)*4
    require(begin==36 and syms<=end==u16(32)*4==len(raw) and raw[34:36]==b'\xc0\0' and u16(22)==len(definitions),'score complete AJ object structure')
    counts=Counter(f['symbol'] for f in expected_fixups);symbols=[];p=syms
    for d in definitions:
        require(p+4<=end,'score truncated AJ symbol')
        attr=12 if counts[d['name']] else 8
        require(raw[p]==2 and raw[p+1]==attr and u16(p+2)==d['offset'],'score AJ definition type/value');p+=4
        if attr==12:require(p+2<=end and u16(p)==counts[d['name']],'score AJ reference count');p+=2
        z=raw.find(b'\0',p,end);require(z>=p,'score AJ symbol terminator')
        name=raw[p:z].decode('ascii');require(name==d['name'],'score complete AJ named definitions');p=z+1
        symbols.append(dict(d,attribute=attr,references=counts[d['name']]))
    require(end-p<=3 and raw[p:]==bytes(end-p),'score AJ symbol trailer')
    logical_end=definitions[1]['offset']
    require(logical_end%2==1 and size==logical_end+1,'measured AJ implicit alignment contract')
    code=bytearray();fixups=[];p=begin
    while len(code)<logical_end:
        require(p<syms,'score truncated AJ CODE');token=raw[p];p+=1
        if 0x10<=token<=0x1f:
            n=token-15;require(p+n<=syms and len(code)+n<=logical_end,'score AJ literal extent');code+=raw[p:p+n];p+=n
        else:
            require(token==0xfd and p+2<=syms,'score unsupported AJ token')
            low,high=raw[p:p+2];p+=2
            require(0x70<=low<=0x7f and high<=1,'score unmeasured AJ symbol index')
            index=low-0x70+16*high;require(index<len(symbols) and index<=25,'score AJ symbol index outside measured bounds')
            d=symbols[index]
            fixups.append(dict(offset=len(code),symbol=d['name'],type='HUNK_RELOC32',width=4,addend=0))
            require(len(code)+4<=logical_end,'score AJ relocation straddles CODE');code+=d['offset'].to_bytes(4,'big')
    require(syms==((p+4)//4)*4 and raw[p:syms]==bytes(syms-p),'score AJ CODE terminator/alignment trailer')
    code.append(0) # independently measured implicit assembler alignment; no DATA credit
    require(fixups==expected_fixups,'score exhaustive named AJ fixups')
    require(Counter(f['symbol'] for f in fixups)==counts,'score AJ fixup/reference count')
    return dict(code=bytes(code),definitions=symbols,fixups=fixups,object_sha256=sha256(raw))


def expected_definitions(member,sem):
    return [dict(name='_audio_'+member['prefix']+'_begin',offset=0),dict(name='_audio_'+member['prefix']+'_end',offset=member['typed_bytes'])]+sem['definitions']


def padding_control(work):
    from hunk import parse
    from overlay_experiment import symbols
    raw=(work/'odd.o').read_bytes();obj=object_code(raw,4,[dict(name='_odd_begin',offset=0),dict(name='_odd_end',offset=3)],[])
    require(obj['code']==b'\0\1\x88\0','independent typed odd-size control CODE')
    linked=(work/'odd.exe').read_bytes();lm=parse(linked);sm=symbols((work/'odd.sym').read_text())
    require([(h['type'],h['allocated_size'],h['initialized_size']) for h in lm['hunks']]==[('CODE',4,4),('DATA',0,0),('BSS',4,0)] and not lm['relocations'],'odd control complete topology')
    require(payload(linked,lm,0)==obj['code'] and sm=={(0,'__H0_org'):0,(0,'_odd_begin'):0,(0,'_odd_end'):3,(0,'__H0_end'):4,(1,'__H1_org'):0,(1,'__H1_end'):0,(2,'__H2_org'):0,(2,'__H2_end'):0},'odd control complete symbols/CODE')
    return dict(CODE=4,typed_command_end=3,implicit_assembler_padding=1,object_sha256=sha256(raw),game_credit=0)


def verify(root,blob,model,fact,batch=None):
    grammar,layout,items=validate(root,blob,model,fact)
    batch=document(root,MANIFEST) if batch is None else batch
    require(set(batch)=={'schema_version','profile','facts','fact_sha256','job','request_sha256','receipt_sha256','artifacts'},'measured batch fields')
    require(batch['schema_version']==2 and batch['profile']=='aztec36' and batch['facts']==[FACT] and batch['fact_sha256']=={FACT:sha256(json_bytes(fact))},'complete measured batch/fact pins')
    expected={prefix+'.asm':item['source'] for prefix,item in items.items()};expected['odd.asm']=ODD_SOURCE
    producer=audit_producer(root,batch,expected,commands_for(fact));work=candidate_path(root,Path(root)/producer['job']/'sys/work')
    control=padding_control(work)
    from hunk import parse
    from overlay_experiment import symbols
    linked=(work/'scoreall.exe').read_bytes();lm=parse(linked);code=payload(linked,lm,0);sm=symbols((work/'scoreall.sym').read_text())
    total=sum(m['CODE'] for m in fact['objects'])
    require(total%4==0 and [(h['type'],h['allocated_size'],h['initialized_size']) for h in lm['hunks']]==[('CODE',total,total),('DATA',0,0),('BSS',4,0)],'score whole linked topology')
    expected_symbols={(0,'__H0_org'):0,(0,'__H0_end'):total,(1,'__H1_org'):0,(1,'__H1_end'):0,(2,'__H2_org'):0,(2,'__H2_end'):0}
    original=payload(blob,model,0);reports=[];rels=[];base=0
    binding_index={b['source_offset']:b for b in layout['bindings']}
    for prefix,item in items.items():
        member=item['member'];sem=item['semantic'];defs=expected_definitions(member,sem)
        # This measured batch has no cross-object or unproved target stand-ins.
        require(all(f['symbol'] in sem['coordinates'] for f in sem['fixups']),'pointer to unproved/external stream object')
        aj=object_code((work/(prefix+'.o')).read_bytes(),member['CODE'],defs,sem['fixups'])
        expected_code=bytearray(sem['code']+b'\0')
        for f in sem['fixups']:expected_code[f['offset']:f['offset']+4]=sem['coordinates'][f['symbol']].to_bytes(4,'big')
        require(aj['code']==expected_code,'score complete AJ CODE differs from typed commands/padding')
        expected_linked=bytearray(expected_code)
        for d in defs:expected_symbols[(0,d['name'])]=base+d['offset']
        for f in sem['fixups']:
            value=base+sem['coordinates'][f['symbol']];expected_linked[f['offset']:f['offset']+4]=value.to_bytes(4,'big')
            rels.append(dict(source_hunk=0,source_offset=base+f['offset'],target_hunk=0,addend_raw=value,type='HUNK_RELOC32',width=4))
        require(code[base:base+member['CODE']]==expected_linked,'score complete linked object CODE/bindings differ')
        mapped=bytearray(expected_code);bindings=[]
        for part in member['parts']:
            a,z=part['original_start'],part['original_end'];ca,cz=part['candidate_start'],part['candidate_end']
            for f in sem['fixups']:
                if ca<=f['offset']<cz:
                    require(f['offset']+4<=cz,'score pointer crosses typed partition')
                    site=a+f['offset']-ca;b=binding_index.get(site)
                    require(b is not None and b['symbol']==f['symbol'],'score named original command target differs')
                    target=int(f['symbol'].rsplit('_',1)[-1],16)
                    require(b==dict(source_hunk=0,source_offset=site,target_hunk=0,addend_raw=target,type='HUNK_RELOC32',width=4,symbol=f['symbol']),'score exhaustive original named relocation')
                    mapped[f['offset']:f['offset']+4]=target.to_bytes(4,'big')
                    bindings.append(dict(b,object_offset=f['offset'],linked_offset=base+f['offset'],linked_target=base+sem['coordinates'][f['symbol']]))
            require(mapped[ca:cz]==original[a:z],'score exact typed CODE-resident DATA differs')
        pad=member['implicit_assembler_padding']
        require(mapped[pad['candidate_offset']]==original[pad['original_offset']]==0 and pad['original_offset'] in ZERO_DEBT,'score uncredited natural padding differs')
        require(sum(p['candidate_end']-p['candidate_start'] for p in member['parts'])+pad['size']==len(mapped),'score clipped or unaccounted object byte')
        reports.append(dict(member,kind='MEASURED_TYPED_AUDIO_SCORE',original=dict(hunk=0,start=member['start'],end=member['end'],size=member['end']-member['start']),
                            bindings=bindings,object_sha256=aj['object_sha256'],object_definitions=aj['definitions'],object_code_sha256=sha256(aj['code']),
                            linked_start=base,linked_CODE_sha256=sha256(bytes(expected_linked)),padding_credit=0))
        base+=member['CODE']
    require(sm==expected_symbols,'score complete linked symbol inventory/coordinates')
    require(sorted(map(field,lm['relocations']),key=lambda r:r['source_offset'])==sorted(rels,key=lambda r:r['source_offset']),'score exhaustive linked RELOC32 sites/types/widths/targets')
    return dict(id=IDENT,kind='MEASURED_TYPED_AUDIO_SCORE',category=CATEGORY,typed_bytes=layout['typed_bytes'],command_count=len(layout['commands'])-len(layout['roots']),
                root_count=len(layout['roots']),streams=layout['streams'],unproved_intervals=layout['unproved_intervals'],named_relocations=len(layout['bindings']),
                grammar_sha256=fact['grammar_sha256'],layout_sha256=sha256(json_bytes(layout)),fact_sha256=sha256(json_bytes(fact)),objects=reports,producer=producer,padding_control=control,
                linked_sha256=sha256(linked),whole_CODE_bytes=total,c_bytes=0,asm_instruction_bytes=0,padding_credit=0,source_acceptance=False,proof_level=None,
                historical_owner='UNKNOWN',historical_tu='UNKNOWN',natural_root_layout_proof=False,
                verifier_identity={n:sha256(canonical_path(root,'tools/'+n).read_bytes()) for n in ['audio_score_measured.py','audio_score_catalogue.py','audio_score_commands.py','audio_score_grammar.py','check_data_contribution.py','hunk.py','repo_paths.py']})


@shared
def rows(root,blob,model,analysis,ledger):
    item=ledger.get(MAP,{}).get(IDENT)
    if item is None:return []
    require(set(item)=={'state','fact','sources','proof','proof_sha256'} and item['state']=='DATA_LAYOUT_MATCH' and item['fact']==FACT and item['proof']=='recovery/proofs/code-data/'+IDENT+'.json','measured score ownership identity')
    fact=document(root,FACT);report=verify(root,blob,model,fact)
    expected={o['source']:o['source_sha256'] for o in fact['objects']}
    require(item['sources']==expected,'measured complete source inventory')
    for o in fact['objects']:
        raw=read_source(root, o['source'])
        require(raw==canonical_path(root,o['candidate']).read_bytes() and sha256(raw)==o['source_sha256'],'canonical measured source changed')
    proofraw=canonical_path(root,item['proof']).read_bytes();proof=json.loads(proofraw)
    require(sha256(proofraw)==item['proof_sha256'] and set(proof)=={'fact','comparison','regression'} and proof['fact']==fact and proof['regression'].get('passed') is True,'measured score proof/gate')
    comparable=lambda r:{k:v for k,v in r.items() if k!='verifier_identity'}
    require(proof['comparison'].get('verifier_identity') and comparable(proof['comparison'])==comparable(report),'measured score canonical proof no longer rederives')
    return [dict(o,acceptance=True,source_acceptance=True,proof_level='DATA_LAYOUT_MATCH',proof=item['proof'],producer=report['producer'],category=CATEGORY,provider=IDENT) for o in report['objects']]


def contributions(root,records):
    out=[]
    for r in records:
        require(r.get('acceptance') is True,'measured contribution requires canonical replay')
        # The full object was verified, including its uncredited automatic pad.
        # Only its separately typed partitions receive DATA credit.
        objraw=candidate_path(root,Path(root)/r['producer']['job']/('sys/work/'+r['prefix']+'.o')).read_bytes()
        defs=[{k:d[k] for k in ('name','offset')} for d in r['object_definitions']]
        fixups=[dict(offset=b['object_offset'],symbol=b['symbol'],type=b['type'],width=b['width'],addend=0) for b in r['bindings']]
        aj=object_code(objraw,r['CODE'],defs,fixups);mapped=bytearray(aj['code'])
        for b in r['bindings']:mapped[b['object_offset']:b['object_offset']+4]=b['addend_raw'].to_bytes(4,'big')
        for i,p in enumerate(r['parts']):
            a,z=p['original_start'],p['original_end'];rels=[{k:b[k] for k in ('source_offset','target_hunk','type','width','addend_raw')} for b in r['bindings'] if a<=b['source_offset']<z]
            out.append(dict(id=r['id']+'_part%d'%i,hunk=0,start=a,end=z,category=CATEGORY,
                            bytes=bytes(mapped[p['candidate_start']:p['candidate_end']]),relocations=rels))
    return out


def input_identity(root):
    root=Path(root);names={FACT,MANIFEST};external={}
    fact=document(root,FACT) if canonical_path(root,FACT).exists() else {}
    for obj in fact.get('objects',[]):names.add(obj['candidate'])
    if canonical_path(root,MANIFEST).exists():
        batch=document(root,MANIFEST);job=batch['job']
        names.update(job+'/'+n for n in ['request.json','result.json','worker.uae','kick.rom','sys/s/startup-sequence'])
        names.update(job+'/sys/work/'+n for n in batch['artifacts'])
        request=json.loads(candidate_path(root,root/job/'request.json').read_bytes());names.update(p['path'] for p in request['pinned_inputs'])
        names.update(['toolchain/candidate-lock.json','evidence/toolchain/aztec-3.6a.json','evidence/toolchain/aztec-5.0a.json'])
        names.add(document(root,'toolchain/candidate-lock.json')['archive'])
        for folder in ('c','l','libs','devs'):names.update(p.relative_to(root).as_posix() for p in active_files(root/job/'sys'/folder))
        external[request['emulator']]=sha256(Path(request['emulator']).read_bytes())
    ledger=document(root,'recovery/ledger.json') if canonical_path(root,'recovery/ledger.json').exists() else {}
    item=ledger.get(MAP,{}).get(IDENT)
    if item:names.update([item['fact'],item['proof'],*item['sources']])
    def path(n):return candidate_path(root,root/n) if n.startswith('build/worker-jobs/') else canonical_path(root,n)
    return {**{str(path(n)):sha256((read_source(root, path(n)) if n.startswith('src/') else path(n).read_bytes())) if (source_file(root, path(n)) if n.startswith('src/') else path(n)).exists() else None for n in sorted(names)},**external}
