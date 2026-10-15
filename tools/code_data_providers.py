"""Exact typed CODE-resident audio DATA provider; no instruction/C credit.

The retained pilot controls cover 16E4; measured source covers every proved root.
No clipped objects, raw directives, guessed gaps or unnamed fixups are accepted.
"""
import json,re
from pathlib import Path
from common import require,sha256,json_bytes
from repo_paths import canonical_path,candidate_path,active_files
from audio_sequence_data import payload,field,load as classified_facts
from audio_score_recipe import source,encoding
import check_data_contribution as bounded
from audio_score_grammar import derive,form

MAP='code_data_providers'
CATEGORY='TYPED_CODE_DATA'
STATE='DATA_LAYOUT_MATCH'
IDENT='resident_audio_score_16E4'
FACT='evidence/code-data-providers/'+IDENT+'.json'
MANIFEST='evidence/code-data-providers/batch.json'
SOURCE='src/recovered/code-data/'+IDENT+'.asm'
RECIPE=bounded.RECIPE
CANDIDATE=bounded.SOURCE


def document(root,name):return json.loads(canonical_path(root,name).read_bytes())


def typed_stream(code,relocations,start,end,grammar):
    require(type(start) is int and type(end) is int and start+2<end<=len(code),'partial score interval')
    require(code[start]<4,'score channel header')
    rels={r['source_offset']:r for r in relocations if r['source_hunk']==0 and start<=r['source_offset']<end}
    todo=[start+2];rows={};covered={start,start+1};bindings=[]
    while todo:
        p=todo.pop()
        if p in rows:continue
        require(start+2<=p<end,'partial stream or external pattern dependency')
        op=code[p];f=form(grammar,op,p);q=p+f['length']
        require(q<=end,'partial score command')
        require(not covered.intersection(range(p,q)),'overlapping typed commands')
        covered.update(range(p,q));targets=[]
        pf=f['pointer_field']
        if pf is not None:
            site=p+pf;require(site==(p+2)&~1,'grammar pointer alignment')
            rr=rels.get(site)
            require(rr is not None and rr['type']=='HUNK_RELOC32' and rr['width']==4 and rr['target_hunk']==0,
                    'missing/unnamed score pointer relocation')
            target=int.from_bytes(code[site:site+4],'big')
            require(target==rr['addend_raw'] and start+2<=target<end,'partial/external pattern binding')
            require(site==p+1 or code[p+1]==0,'untyped pointer alignment value')
            targets.append(target)
            bindings.append(dict(field(rr),symbol='_score_pattern'))
        if 'NEXT' in f['flows'] or 'CALL' in f['flows']:targets.append(q)
        rows[p]=dict(offset=p,end=q,opcode=op,pointer_field=None if pf is None else p+pf,successors=targets)
        todo.extend(targets)
    require(covered==set(range(start,end)),'guessed gap or partial/unreachable stream')
    require({r['source_offset'] for r in bindings}==set(rels),'unnamed or masked relocation')
    require(all(r['addend_raw'] in rows for r in bindings),'pointer target is not a named command')
    return dict(header=dict(offset=start,channel=code[start],priority=code[start+1]),
                commands=[rows[p] for p in sorted(rows)],relocations=sorted(bindings,key=lambda r:r['source_offset']))


def validate_fact(root,blob,model,fact):
    require(set(fact)=={'schema_version','id','original','oracle_sha256','source','candidate','recipe',
                       'source_sha256','recipe_sha256','grammar','relocations','historical_owner','historical_tu','original_filename'},
            'CODE-data fact fields (raw carriers/masks reject)')
    require(type(fact['schema_version']) is int and fact['schema_version']==1 and fact['id']==IDENT,'CODE-data identity')
    require(fact['source']==SOURCE and fact['candidate']==CANDIDATE and fact['recipe']==RECIPE,'CODE-data source paths')
    require(fact['historical_owner']==fact['historical_tu']=='UNKNOWN' and fact['original_filename'] is None,'historical provenance unknown')
    require(fact['oracle_sha256']==sha256(blob),'stale score oracle')
    code=payload(blob,model,0);expected=dict(hunk=0,start=0x16e4,end=0x172c,size=72,sha256=sha256(code[0x16e4:0x172c]))
    require(fact['original']==expected,'partial stream or guessed gap')
    grammar=derive(blob,model);require(fact['grammar']==grammar,'stale/wrong-length grammar')
    classified=next(f for f in classified_facts(root,blob,model) if f['evidence_path']==bounded.FACT)
    require(0x16e4 in classified['roots'] and 0x172c in classified['roots'],'independent adjacent selector-root bounds')
    layout=typed_stream(code,model['relocations'],0x16e4,0x172c,grammar)
    require(layout['relocations']==fact['relocations']==[dict(source_hunk=0,source_offset=0x1728,target_hunk=0,
            addend_raw=0x16f6,type='HUNK_RELOC32',width=4,symbol='_score_pattern')],'unnamed/masked score relocation')
    recipe=document(root,RECIPE);src=source(recipe).encode('ascii');sem=encoding(recipe)
    require(fact['source_sha256']==sha256(src) and fact['recipe_sha256']==sha256(json_bytes(recipe)),'score semantic recipe changed')
    # Regenerated source is constrained by semantic fields, not arbitrary dc.b.
    require(canonical_path(root,CANDIDATE).read_bytes()==src,'raw byte carrier or changed macro source')
    local=[dict(source_hunk=0,source_offset=sem['pointer_field'],target_hunk=0,addend_raw=sem['pattern_offset'],type='HUNK_RELOC32',width=4)]
    candidate=typed_stream(sem['code'],local,0,len(sem['code']),grammar)
    require(len(candidate['commands'])==len(layout['commands']) and
            [(x['offset']-0x16e4,x['end']-0x16e4,x['opcode']) for x in layout['commands']]==
            [(x['offset'],x['end'],x['opcode']) for x in candidate['commands']],'semantic command boundaries differ')
    return grammar,layout,recipe,src


def verify(root,blob,model,fact,batch=None):
    grammar,layout,recipe,src=validate_fact(root,blob,model,fact)
    batch=document(root,MANIFEST) if batch is None else batch
    require(set(batch)=={'schema_version','profile','facts','fact_sha256','job','request_sha256','receipt_sha256','artifacts'},'CODE-data batch fields')
    require(batch['schema_version']==1 and batch['profile']=='aztec36' and batch['facts']==[FACT] and
            batch['fact_sha256']=={FACT:sha256(json_bytes(fact))},'complete one-job CODE-data batch')
    require(re.fullmatch(r'build/worker-jobs/sol-audio-score-[A-Za-z0-9_-]+',batch['job']),'CODE-data producer job path')
    job=candidate_path(root,Path(root)/batch['job'])
    require(sha256((job/'request.json').read_bytes())==batch['request_sha256'] and
            sha256((job/'result.json').read_bytes())==batch['receipt_sha256'],'stale CODE-data producer SHA pins')
    receipt=json.loads((job/'result.json').read_bytes())
    require(batch['artifacts']=={a['path']:a['sha256'] for a in receipt['artifacts']},'CODE-data complete artifact pins')
    producer=bounded.producer(root,job,recipe,src)
    w=job/'sys/work';obj=bounded.object_code((w/'score.o').read_bytes())
    require(obj['code']==encoding(recipe)['code'],'AJ object differs from semantic commands')
    classified=next(f for f in classified_facts(root,blob,model) if f['evidence_path']==bounded.FACT)
    report=bounded.compare(blob,model,classified,(w/'score.o').read_bytes(),(w/'score.exe').read_bytes(),(w/'score.sym').read_text())
    require(report['verdict']=='EQUAL_CANDIDATE','exact whole score mismatch')
    return dict(id=IDENT,category=CATEGORY,state=STATE,original=fact['original'],grammar=grammar,
                layout=layout,producer=producer,comparison=report,source_sha256=sha256(src),
                fact_sha256=sha256(json_bytes(fact)),object_sha256=sha256((w/'score.o').read_bytes()),
                source_acceptance=False,proof_level=None,historical_owner='UNKNOWN',historical_tu='UNKNOWN',
                natural_root_layout_proof=False,c_bytes=0,asm_instruction_bytes=0,
                verifier_identity={n:sha256(canonical_path(root,'tools/'+n).read_bytes()) for n in
                    ['code_data_providers.py','audio_score_grammar.py','audio_score_recipe.py','audio_sequence_data.py','check_data_contribution.py','hunk.py','repo_paths.py']})


def rows(root,blob,model,analysis,ledger):
    entries=ledger.get(MAP,{})
    import audio_score_measured as measured
    require(set(entries)<={IDENT,measured.IDENT},'unknown CODE-data provider')
    out=[]
    for ident,item in entries.items():
        if ident==measured.IDENT:continue
        require(set(item)=={'state','fact','source','source_sha256','proof','proof_sha256'} and
                item['state']==STATE and item['fact']==FACT and item['source']==SOURCE and
                item['proof']=='recovery/proofs/code-data/'+IDENT+'.json','CODE-data ownership identity')
        fact=document(root,FACT);replay=verify(root,blob,model,fact)
        raw=canonical_path(root,item['proof']).read_bytes();proof=json.loads(raw)
        require(sha256(raw)==item['proof_sha256'],'CODE-data proof hash')
        src=canonical_path(root,SOURCE).read_bytes()
        require(src==source(document(root,RECIPE)).encode('ascii') and sha256(src)==item['source_sha256'],'CODE-data canonical source')
        require(set(proof)=={'fact','comparison','regression'} and proof['fact']==fact and
                proof['regression'].get('passed') is True,'CODE-data shared regression proof')
        comparable=lambda r:{k:v for k,v in r.items() if k!='verifier_identity'}
        require(proof['comparison'].get('verifier_identity') and comparable(proof['comparison'])==comparable(replay),
                'CODE-data proof no longer rederives')
        # Classification validation independently excludes executable entries and
        # C/ASM claims. Hybrid's common overlap gate covers every other class.
        claimed=[]
        for rec in ledger.get('functions',{}).values():
            e=rec['evidence_extent'];claimed.append(dict(hunk=e['hunk'],start=e['start'],end=e['end']))
        classified_facts(root,blob,model,analysis,claimed)
        out.append(dict(replay,acceptance=True,source_acceptance=True,proof_level=STATE,source=SOURCE,proof=item['proof']))
    out.extend(measured.rows(root,blob,model,analysis,ledger))
    occupied=set()
    for row in out:
        intervals=row.get('parts',[dict(original_start=row['original']['start'],original_end=row['original']['end'])])
        points={(row['original']['hunk'],q) for part in intervals for q in range(part['original_start'],part['original_end'])}
        require(not points.intersection(occupied),'overlapping canonical CODE-data providers');occupied.update(points)
    return out


def contributions(root,records):
    import audio_score_measured as measured
    out=measured.contributions(root,[r for r in records if r.get('kind')=='MEASURED_TYPED_AUDIO_SCORE'])
    for r in records:
        if r.get('kind')=='MEASURED_TYPED_AUDIO_SCORE':continue
        require(r.get('acceptance') is True,'CODE-data contributions require canonical replay')
        obj=bounded.object_code((Path(r['producer']['job'])/'sys/work/score.o').read_bytes())
        code=bytearray(obj['code']);rel=[];o=r['original']
        for f,b in zip(obj['fixups'],r['layout']['relocations']):
            require(f['symbol']==b['symbol'] and f['offset']==b['source_offset']-o['start'] and f['width']==b['width'],
                    'CODE-data named AJ/RELOC32 binding')
            code[f['offset']:f['offset']+4]=b['addend_raw'].to_bytes(4,'big')
            rel.append({k:b[k] for k in ('source_offset','target_hunk','type','width','addend_raw')})
        out.append(dict(id=r['id'],hunk=0,start=o['start'],end=o['end'],category=CATEGORY,bytes=bytes(code),relocations=rel))
    return out


def input_identity(root):
    root=Path(root);names={FACT,MANIFEST,RECIPE,CANDIDATE,bounded.FACT};external={}
    p=canonical_path(root,MANIFEST)
    if p.exists():
        batch=document(root,MANIFEST);job=batch['job']
        names.update(job+'/'+n for n in ['request.json','result.json','worker.uae','sys/s/startup-sequence','kick.rom'])
        names.update(job+'/sys/work/'+n for n in batch['artifacts'])
        request=json.loads(candidate_path(root,root/job/'request.json').read_bytes())
        names.update(p['path'] for p in request['pinned_inputs'])
        lock=document(root,'toolchain/candidate-lock.json');names.add(lock['archive'])
        names.update(['toolchain/candidate-lock.json','evidence/toolchain/aztec-3.6a.json','evidence/toolchain/aztec-5.0a.json'])
        for folder in ['c','l','libs','devs']:
            names.update(p.relative_to(root).as_posix() for p in active_files(root/job/'sys'/folder))
        external[request['emulator']]=sha256(Path(request['emulator']).read_bytes())
    ledger=document(root,'recovery/ledger.json') if canonical_path(root,'recovery/ledger.json').exists() else {}
    for item in ledger.get(MAP,{}).values():
        if 'source' in item:names.update([item['source'],item['proof'],item['fact']])
    def path(n):return candidate_path(root,root/n) if n.startswith('build/worker-jobs/') else canonical_path(root,n)
    import audio_score_measured as measured
    return {**{str(path(n)):sha256(path(n).read_bytes()) if path(n).exists() else None for n in sorted(names)},**external,**measured.input_identity(root)}
