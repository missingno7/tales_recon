"""Canonical complete mnemonic objects linked outside ordinary C contributions.

Accepted source and assembler objects stay intact. Every acceptance replays the
existing reconstructed-ASM comparison and proves the new physical link. Neither
the objects nor diagnostic storage receive C or DATA credit.
"""
from names import read_source
import copy,json,re
from pathlib import Path
from common import require,sha256,json_bytes
from repo_paths import canonical_path,candidate_path
from analysis_support import ROOT
FIELD='reconstructed_asm_dependencies'


def specifications():
    # Source-controlled measured spans are a negative lookup filter only.
    # A positive lookup still requires canonical facts, exports and replay.
    from reconstructed_asm import SPECS as first
    from audio_driver_asm import SPECS as driver
    from glue_library_asm import SPECS as glue
    return dict(first,**driver,**glue)


def possible_target(target,ledger):
    specs=specifications()
    return any(ident in specs and specs[ident]['start']<=target<specs[ident]['end']
               for ident in ledger.get('reconstructed_asm',{}))


def has_dependencies(members,ledger=None):
    if ledger is None:
        from recovery_state import recovery
        ledger=recovery()
    if not ledger.get('reconstructed_asm'):return False
    return any(c.get('basis')=='PC_RELATIVE' and c.get('hunk')==0 and
               isinstance(c.get('offset'),int) and possible_target(c['offset'],ledger)
               for m in members for c in m.get('direct_callees',()))


def inventory(root=ROOT,ledger=None):
    if ledger is None:
        from recovery_state import recovery
        ledger=recovery()
    result={}
    for ident,item in ledger.get('reconstructed_asm',{}).items():
        fact=json.loads(canonical_path(root,item['fact']).read_bytes())
        exports=fact.get('exports')
        if exports is None:
            start=fact['original']['start']
            exports=[dict(name='_resident_asm_%04X'%start,offset=0,original=start)]
        for export in exports:
            target=export.get('original')
            if target is None:continue  # One-past is not an instruction entry.
            require(fact['original']['start']<=target<fact['original']['end'],'ASM export outside complete object')
            key=(fact['original']['hunk'],target)
            require(key not in result,'duplicate canonical ASM entry')
            result[key]=dict(id=ident,item=item,fact=fact,symbol=export['name'])
    return result


def closure(members,root=ROOT,ledger=None):
    by=inventory(root,ledger);selected={};c_targets=set()
    pending=[(c['hunk'],c['offset']) for m in members for c in m.get('direct_callees',()) if c.get('basis')=='PC_RELATIVE']
    while pending:
        record=by.get(pending.pop())
        if record is None or record['id'] in selected:continue
        selected[record['id']]=record;fact=record['fact']
        for call in fact.get('external_code',()):
            target=(call['hunk'],call['target'])
            if target in by:pending.append(target)
            else:c_targets.add(target)
        for edge in fact.get('boundary_edges',()):
            if edge.get('target')==fact['original']['end']:
                target=(fact['original']['hunk'],edge['target'])
                require(target in by,'ASM one-past transfer has no canonical next object')
                pending.append(target)
    return sorted(selected.values(),key=lambda x:x['fact']['original']['start']),sorted(c_targets)


def owns(fid,root=ROOT,ledger=None,entries=None):
    match=re.fullmatch(r'resident_F_([0-9A-F]+)',fid)
    if match is None:return False
    target=int(match[1],16)
    if entries is not None:return (0,target) in entries
    if ledger is None:
        from recovery_state import recovery
        ledger=recovery()
    if not possible_target(target,ledger):return False
    return (0,target) in inventory(root,ledger)


def c_dependencies(fid,root=ROOT,ledger=None):
    match=re.fullmatch(r'resident_F_([0-9A-F]+)',fid)
    require(match is not None,'ASM dependency must be a resident instruction entry')
    member=dict(direct_callees=[dict(hunk=0,offset=int(match[1],16),basis='PC_RELATIVE')])
    targets=closure([member],root,ledger)[1]
    require(all(h==0 for h,t in targets),'ASM/C dependency left resident CODE')
    return ['resident_F_%04X'%target for hunk,target in targets]


def derive(members,root=ROOT,ledger=None):
    if not has_dependencies(members,ledger):return None
    records,c_targets=closure(members,root,ledger)
    if not records:return None
    by=inventory(root,ledger);objects=[];aliases={}
    for record in records:
        ident,item,fact=record['id'],record['item'],record['fact']
        src=read_source(root, item['source'], names_root=None);proof_raw=canonical_path(root,item['proof']).read_bytes()
        require(sha256(src)==item['source_sha256'] and sha256(proof_raw)==item['proof_sha256'],'canonical ASM source/proof changed')
        proof=json.loads(proof_raw)
        require(proof['fact']==fact and proof['regression'].get('passed') is True,'ASM dependency is not canonical')
        comparison=proof['comparison'];prefix=fact.get('prefix','rng' if ident=='resident_asm_559E' else 'note')
        path=comparison['producer']['job']+'/sys/work/'+prefix+'.o'
        raw=candidate_path(root,Path(root)/path).read_bytes()
        require(sha256(raw)==comparison['object_structure']['object_sha256'],'canonical assembled object changed')
        objects.append(dict(id=ident,category='RECONSTRUCTED_ASM',source=item['source'],source_sha256=item['source_sha256'],
                            proof=item['proof'],proof_sha256=item['proof_sha256'],fact=item['fact'],fact_sha256=sha256(json_bytes(fact)),
                            object=path,object_sha256=sha256(raw),producer=comparison['producer'],original=fact['original'],label='asm%03d'%len(objects)))
    selected={o['id'] for o in objects}
    for (hunk,target),record in by.items():
        if record['id'] in selected:aliases['F_h%02d_%04X'%(hunk,target)]=record['symbol'][1:]
    for hunk,target in c_targets:
        require(any(m['hunk']==hunk and m['start']==target for m in members),'ASM dependency has no complete C member: %04X'%target)
        names={c['name'] for r in records for c in r['fact'].get('external_code',()) if (c['hunk'],c['target'])==(hunk,target)}
        require(len(names)==1,'ASM/C binding has conflicting names')
        aliases['F_h%02d_%04X'%(hunk,target)]=names.pop()[1:]
    data={d['name'][1:] for r in records for d in r['fact'].get('external_data',())}
    data.update(r['symbol'][1:] for x in records for r in x['fact'].get('relocations',()))
    from canonical_code_data_dependencies import derive as typed_derive
    if ledger is None:
        from recovery_state import recovery
        ledger=recovery()
    recipe=dict(objects=objects,aliases=dict(sorted(aliases.items())),external_data=sorted(data),c_bytes=0,data_credit=0,historical_object_membership='UNKNOWN')
    typed=typed_derive(members,root,ledger)
    if typed is not None:recipe['typed_provider']=typed
    return recipe


def source(text,recipe):
    def spelling(match):
        name='F_h%02d_%04X'%(int(match[1]),int(match[2],16))
        return recipe['aliases'].get(name,match[0])
    return re.sub(r'\bF_h(\d+)_([0-9A-Fa-f]+)\b',spelling,text)


def harness_source(text,recipe):
    text=source(text,recipe);present=set(re.findall(r'\bG_h\d+_[0-9A-F]+\b',text))
    text=text+''.join('\nextern long '+n+';' for n in recipe['external_data'] if n not in present)+'\n'
    if recipe.get('typed_provider'):
        from canonical_code_data_dependencies import harness_source as typed_source
        text=typed_source(text,recipe['typed_provider'])
    return text


def configure(trial,recipe):
    if recipe is None:return
    require(trial.get('target_node')==0 and trial['profile'].startswith('aztec36') and trial.get('objects'),'ASM dependencies require separate compatible resident C objects')
    require(not trial.get('mixed_object_dependencies'),'combined mixed/ASM recipes are unmeasured')
    trial['source']=harness_source(trial['source'],recipe)
    for obj in trial['objects']:obj['source']=source(obj['source'],recipe)
    trial['local_functions']=sorted(set(source(n,recipe) for n in trial.get('local_functions',()))|set(recipe['aliases'].values()))
    trial[FIELD]=recipe


def plan(trial,base_plan):
    key,meta,harness,objects=base_plan(trial);recipe=trial[FIELD];meta=dict(meta,**{FIELD:recipe})
    meta['assembled_dependency_base_key']=key
    from link_line import identity_field
    from compiler_oracle import overlay_proxies
    dependencies=recipe['objects']+recipe.get('typed_provider',{}).get('objects',[])
    labels=[o['label'] for o in objects]+[o['label'] for o in dependencies]
    meta['linked_dependency_objects']=[o['label'] for o in dependencies]
    field=identity_field(labels,overlay_proxies(trial['source'],0),0,meta)
    if field is not None:meta['link_argument_file']=field
    else:meta.pop('link_argument_file',None)
    return sha256(json_bytes(meta)),meta,harness,objects


def stage(trial,source_dir,prefix,root=ROOT):
    recipe=trial.get(FIELD)
    if recipe is None:return []
    names=[]
    for obj in recipe['objects']+recipe.get('typed_provider',{}).get('objects',[]):
        raw=candidate_path(root,Path(root)/obj['object']).read_bytes()
        require(sha256(raw)==obj['object_sha256'],'ASM object changed before staging')
        name=prefix+'_'+obj['label'];(source_dir/(name+'.o')).write_bytes(raw);names.append(name)
    return names


def object_code(ident,raw):
    from reconstructed_asm import object_rng,object_note
    from audio_driver_objects import parse
    from glue_library_asm import ID as glue_id,object_code as glue_code
    if ident==glue_id:return glue_code(raw)
    return object_rng(raw) if ident=='resident_asm_559E' else object_note(raw) if ident=='resident_asm_59A4' else parse(raw)


def validate_linked(compiled,root=ROOT,context=None):
    recipe=compiled['identity'].get(FIELD)
    if recipe is None:return compiled
    if context is None:
        from analysis_support import game
        from recovery_state import recovery,evidence
        blob,model,_=game();ledger,analysis=recovery(),evidence()
    else:blob,model,ledger,analysis=(context[k] for k in ('blob','model','ledger','analysis'))
    from reconstructed_asm import rows
    accepted={r['id']:r for r in rows(root,blob,model,analysis,ledger)}
    require(all(o['id'] in accepted for o in recipe['objects']),'ASM dependency lost canonical ownership')
    from hunk import parse
    from overlay_experiment import symbols
    from audio_sequence_data import payload,field
    directory,prefix=Path(compiled['directory']),compiled['prefix']
    linked=(directory/(prefix+'.exe')).read_bytes();lm=parse(linked);sm=symbols((directory/(prefix+'.sym')).read_text())
    # The ordinary comparator proves this same Manx COMMON folding convention.
    data=next(h for h in lm['hunks'] if h['number']==1);bss=next(h for h in lm['hunks'] if h['number']==2)
    origin=sm.get((2,'__H2_org'))
    if origin==data['initialized_size'] and bss['allocated_size']==4:
        sm={(1 if h==2 and origin<=v<data['allocated_size'] else h,n):v for (h,n),v in sm.items()}
    cursor=compiled['contribution']['resident_bounds']['end'];reports=[]
    for obj in recipe['objects']:
        item=ledger['reconstructed_asm'][obj['id']]
        require(all(item[k]==obj[k] for k in ('source','source_sha256','proof','proof_sha256','fact')),'ASM dependency canonical identity changed')
        fact=json.loads(canonical_path(root,item['fact']).read_bytes())
        require(sha256(json_bytes(fact))==obj['fact_sha256'],'ASM dependency fact changed')
        raw=(directory/(prefix+'_'+obj['label']+'.o')).read_bytes()
        require(sha256(raw)==obj['object_sha256']==accepted[obj['id']]['object_structure']['object_sha256'],'linked ASM is not complete canonical object')
        code,refs,structure=object_code(obj['id'],raw)
        exports=fact.get('exports',[dict(name='_resident_asm_%04X'%fact['original']['start'],offset=0)])
        for export in exports:require(sm.get((0,export['name']))==cursor+export['offset'],'ASM object order/export differs')
        expected=bytearray(code);rels=[]
        for ref in refs:
            matches=[(h,v) for (h,n),v in sm.items() if n==ref['symbol']]
            require(len(matches)==1,'ASM dependency has no unique named linked target')
            hunk,target=matches[0];at,width=ref['offset'],ref['width']
            if width==2:
                require(hunk==0,'ASM PC reference left root CODE')
                expected[at:at+2]=(target-cursor-at).to_bytes(2,'big',signed=True)
            else:
                expected[at:at+4]=target.to_bytes(4,'big')
                rels.append(dict(source_hunk=0,source_offset=cursor+at,target_hunk=hunk,addend_raw=target,type='HUNK_RELOC32',width=4))
        require(payload(linked,lm,0)[cursor:cursor+len(code)]==expected,'ASM complete linked CODE/named fields differ')
        actual=[field(r) for r in lm['relocations'] if r['source_hunk']==0 and r['source_offset']<cursor+len(code) and cursor<r['source_offset']+r['width']]
        require(sorted(actual,key=lambda r:r['source_offset'])==sorted(rels,key=lambda r:r['source_offset']),'ASM linked relocation inventory differs: '+str(dict(actual=actual,expected=rels)))
        for edge in fact.get('boundary_edges',()):
            if edge.get('target')==fact['original']['end']:
                neighbor=next((r for r in recipe['objects'] if r['original']['start']==edge['target']),None)
                require(neighbor is not None,'ASM one-past dependency missing')
                nf=json.loads(canonical_path(root,neighbor['fact']).read_bytes())
                entry=next(e['name'] for e in nf['exports'] if e.get('original')==edge['target'])
                require(sm.get((0,entry))==cursor+len(code),'ASM one-past transfer bound to another object')
        reports.append(dict(id=obj['id'],category='RECONSTRUCTED_ASM',verdict='EQUAL',linked_start=cursor,size=len(code),object_sha256=sha256(raw),c_bytes=0,data_credit=0))
        cursor+=len(code)
    typed_reports=[]
    if recipe.get('typed_provider'):
        from canonical_code_data_dependencies import validate_linked as typed_validate
        typed_reports=typed_validate(compiled,recipe['typed_provider'],cursor,root,dict(blob=blob,model=model,ledger=ledger,analysis=analysis))
    from function_compare import mechanical
    locations={}
    for name,actual in recipe['aliases'].items():
        coord=mechanical('_'+name)
        matches=[(h,v) for (h,n),v in sm.items() if n=='_'+actual]
        require(len(matches)==1 and matches[0][0]==0,'ASM/C alias has no unique CODE target')
        locations[coord[:2]]=matches[0]
    for (h,name),offset in sm.items():
        coord=mechanical(name)
        if coord is not None and coord[:2] in locations:
            require((h,offset)==locations[coord[:2]],'synthetic stand-in shadows a canonical ASM/C entry')
    out=copy.deepcopy(compiled)
    if typed_reports:out['typed_dependency_comparisons']=typed_reports
    # Aliases are checked analysis metadata. No producing bytes are modified.
    for name,actual in recipe['aliases'].items():
        matches=[(h,v) for (h,n),v in sm.items() if n=='_'+actual]
        require(len(matches)==1 and matches[0][0]==0,'ASM/C alias has no unique CODE target')
        hunk,target=matches[0];alias=dict(name='_'+name,hunk=hunk,offset=target)
        existing=[s for s in out['contribution']['symbols'] if s['name']==alias['name']]
        require(not existing or existing==[alias],'ASM/C alias conflicts with contribution symbols')
        if not existing:out['contribution']['symbols'].append(alias)
    out[FIELD]=reports
    return out
