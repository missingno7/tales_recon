"""The typed 6200 selector's complete canonical provider objects for a C link.

This bounded dependency retains the accepted stateful recipe and its measured
score support objects. It supplies no new ownership, C or assembly credit.
"""
from names import read_source
import json,re
from pathlib import Path
from common import require,sha256
from repo_paths import canonical_path,candidate_path


def derive(members,root,ledger):
    if not any(r.get('target_hunk')==0 and r.get('addend_raw')==0x6200 for m in members for r in m.get('relocations',())):return None
    import audio_stateful_provider as stateful
    import audio_score_measured as score
    inputs={};objects=[];job=None
    for module in [stateful,score]:
        item=ledger.get('code_data_providers',{}).get(module.IDENT)
        require(item is not None,'selector needs canonical complete typed provider: '+module.IDENT)
        raw=canonical_path(root,item['proof']).read_bytes();proof=json.loads(raw)
        require(sha256(raw)==item['proof_sha256'] and proof['regression'].get('passed') is True,'selector provider canonical proof changed')
        fact=json.loads(canonical_path(root,item['fact']).read_bytes())
        require(proof['fact']==fact,'selector provider fact changed')
        inputs[module.IDENT]=item
        if module is stateful:job=proof['comparison']['producer']['job']
        by={o['prefix']:o for o in proof['comparison']['objects']}
        for obj in fact['objects']:
            src=read_source(root, obj['source'])
            require(sha256(src)==obj['source_sha256']==item['sources'][obj['source']],'selector provider source changed')
            path=job+'/sys/work/'+obj['prefix']+'.o';assembled=candidate_path(root,Path(root)/path).read_bytes()
            require(sha256(assembled)==by[obj['prefix']]['object_sha256'],'selector provider supporting object changed')
            objects.append(dict(prefix=obj['prefix'],source=obj['source'],source_sha256=sha256(src),object=path,
                                object_sha256=sha256(assembled),label='typed%03d'%len(objects),category='TYPED_CODE_DATA'))
    return dict(inputs=inputs,objects=objects,omit_harness_objects=['G_h00_6200'],c_bytes=0,asm_instruction_bytes=0,data_credit=0)


def harness_source(text,recipe):
    for name in recipe['omit_harness_objects']:
        text,n=re.subn(r'\bextern\s+long\s+'+re.escape(name)+r'\s*;', '',text)
        require(n>=1,'selected CODE provider lacks its exact declaration')
    return text


def object_code(raw,row):
    import audio_stateful_provider as stateful
    import audio_score_measured as score
    refs=[dict(offset=b['object_offset'],symbol=b['symbol'],type=b['type'],width=b['width'],addend=0) for b in row['bindings']]
    refs.sort(key=lambda r:r['offset'])
    definitions=[{k:d[k] for k in ['name','offset','external']} for d in row['object_definitions']] if 'logical_size' in row else [{k:d[k] for k in ['name','offset']} for d in row['object_definitions']]
    if 'logical_size' in row:return stateful.object_code(raw,row['CODE'],row['logical_size'],definitions,refs)
    return score.object_code(raw,row['CODE'],definitions,refs)


def validate_linked(compiled,recipe,start,root,context):
    import audio_stateful_provider as stateful
    import audio_score_measured as score
    from hunk import parse
    from overlay_experiment import symbols
    from audio_sequence_data import payload,field
    ledger=context['ledger'];blob,model,analysis=(context[k] for k in ['blob','model','analysis'])
    require({k:ledger.get('code_data_providers',{}).get(k) for k in recipe['inputs']}==recipe['inputs'],'typed dependency canonical ownership changed')
    rows={}
    for module in [stateful,score]:
        module.rows(root,blob,model,analysis,ledger)  # Re-proves the complete canonical report.
        # Some complete objects are support only and own zero new typed bytes.
        # They remain required inputs even though accounting omits their rows.
        proof=json.loads(canonical_path(root,recipe['inputs'][module.IDENT]['proof']).read_bytes())
        rows.update({o['prefix']:o for o in proof['comparison']['objects']})
    directory,prefix=Path(compiled['directory']),compiled['prefix'];linked=(directory/(prefix+'.exe')).read_bytes()
    lm=parse(linked);sm=symbols((directory/(prefix+'.sym')).read_text());cursor=start;reports=[]
    for obj in recipe['objects']:
        row=rows[obj['prefix']];raw=(directory/(prefix+'_'+obj['label']+'.o')).read_bytes()
        require(sha256(raw)==obj['object_sha256']==row['object_sha256'],'linked typed dependency object changed')
        aj=object_code(raw,row);code=bytearray(aj['code'])
        for d in aj['definitions']:
            if not d.get('external',False):require(sm.get((0,d['name']))==cursor+d['offset'],'typed dependency complete object order/definition differs')
        expected_rels=[]
        for ref in aj['fixups']:
            matches=[(h,v) for (h,n),v in sm.items() if n==ref['symbol']]
            require(len(matches)==1 and matches[0][0]==0,'typed pointer target lacks unique CODE definition')
            target=matches[0][1];at=ref['offset'];require(ref['type']=='HUNK_RELOC32' and ref['width']==4,'typed dependency fixup class differs')
            code[at:at+4]=target.to_bytes(4,'big');expected_rels.append(dict(source_hunk=0,source_offset=cursor+at,target_hunk=0,addend_raw=target,type='HUNK_RELOC32',width=4))
        require(payload(linked,lm,0)[cursor:cursor+len(code)]==code,'typed complete linked CODE/named pointers differ')
        actual=[field(r) for r in lm['relocations'] if r['source_hunk']==0 and r['source_offset']<cursor+len(code) and cursor<r['source_offset']+r['width']]
        require(sorted(actual,key=lambda r:r['source_offset'])==expected_rels,'typed dependency relocation inventory differs')
        reports.append(dict(prefix=obj['prefix'],category='TYPED_CODE_DATA',verdict='EQUAL',size=len(code),linked_start=cursor,c_bytes=0,asm_instruction_bytes=0,data_credit=0))
        cursor+=len(code)
    require((0,'_G_h00_6200') in sm and not any(h!=0 and n=='_G_h00_6200' for h,n in sm),'selector was allocated outside CODE')
    return reports
