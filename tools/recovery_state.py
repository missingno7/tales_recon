"""Rank and package bounded work; no reconstructed-source claims from discovery."""
import json
from difflib import SequenceMatcher
from pathlib import Path
import re
from common import require,write_json,sha256
from analysis_support import ROOT
from repo_paths import canonical_path,is_active_repo_path

LEDGER=ROOT/'recovery/ledger.json'


def recovery():
    result=json.loads(LEDGER.read_text()) if LEDGER.exists() else dict(schema_version=1,functions={},attempts={},blockers={})
    root=LEDGER.parent.parent
    scratch=root/'build/recovery/state.json'
    if scratch.exists():result['attempts']=json.loads(scratch.read_text()).get('attempts',{})
    blockers=root/'docs/blockers.json'
    if blockers.exists():result['blockers']=json.loads(blockers.read_text()).get('function_blockers',result.get('blockers',{}))
    return result


def canonical_state(value):
    return dict(schema_version=value.get('schema_version',1),functions=value['functions'],attempts={},blockers={})


def write_recovery(value, ledger=None):
    """Ownership, current blockers, and scratch history have separate homes."""
    ledger=ledger or LEDGER
    root=ledger.parent.parent
    write_json(root/'build/recovery/state.json',dict(attempts=value.get('attempts',{})))
    path=root/'docs/blockers.json'
    doc=json.loads(path.read_text()) if path.exists() else dict(schema_version=1,blockers=[])
    doc['function_blockers']=value.get('blockers',{})
    write_json(path,doc)
    write_json(ledger,canonical_state(value))


def evidence():
    path=ROOT/'evidence/functions/ledger.json'
    require(path.exists(),'run tools/function_census.py first')
    return json.loads(path.read_text())


def runtime_dependencies(ledger):
    """Read measured entry identities for guidance, never source ownership."""
    path=ROOT/'evidence/experiments/runtime-arithmetic.json'
    if not path.exists():return {}
    proof=json.loads(path.read_text())
    require(proof['game_sha256']==ledger['game_sha256'],'runtime guidance belongs to another executable')
    require(proof['status']=='COMPLETE_RUNTIME_CODE_MATCH','runtime guidance lacks a complete match')
    result={}
    for contribution in proof['contributions']:
        extent=contribution['original']
        for entry in contribution['entries']:
            require(0<=entry['offset']<contribution['size'],'runtime guidance entry outside extent')
            key=(extent['hunk'],extent['offset']+entry['offset'])
            item=result.setdefault(key,dict(state='MATCHED_RUNTIME_CONTRIBUTION',
                kind='COMPILER_GENERATED_HELPER',symbol=entry['name'],profiles=[],
                evidence=path.relative_to(ROOT).as_posix(),evidence_sha256=sha256(path.read_bytes()),
                source_contract='Express the C operation; let the compiler emit this helper. Do not declare a C function for its register ABI.'))
            require(item['symbol']==entry['name'],'conflicting runtime entry names')
            item['profiles'].append(contribution['profile'])
    return result


def ranked(node=None):
    l=evidence();r=recovery();result=[];runtime=runtime_dependencies(l)
    r['functions']={fid:item for fid,item in r['functions'].items() if
                    not item.get('source') or is_active_repo_path(ROOT/item['source'],ROOT)}
    incoming={f['id']:sum(any(c['id']==f['id'] for c in caller['direct_callees'])
                         for caller in l['functions'] if caller['id'] not in r['functions']) for f in l['functions']}
    known_runtime={x['id'] for x in l['functions'] if x['ownership']=='RUNTIME_CANDIDATE'}
    for f in l['functions']:
        if node and f['node']!=node:continue
        state=r['functions'].get(f['id'],{}).get('state','DISCOVERED')
        if state in ('FUNCTION_CODE_MATCH','FUNCTION_WITH_DATA_MATCH','MODULE_MATCH','OVERLAY_NODE_MATCH','BLOCKED'):continue
        if f['id'] in r['blockers']:state='BLOCKED'
        elif f['id'] in r['attempts']:
            state='CODEGEN_SIMILAR' if any((a.get('mnemonic_similarity') or 0)>=0.75 for a in r['attempts'][f['id']]) else 'CANDIDATE_C'
        known=sum(c['id'] in r['functions'] or c['id'] in known_runtime or (c['hunk'],c['offset']) in runtime for c in f['direct_callees'])
        unresolved_indirect=[x for x in f['indirect_control_flow'] if x.get('kind')!='PC_RELATIVE_WORD_JUMP_TABLE']
        # Lower cost wins. Closure and dependency unlocks dominate byte size.
        unlock=10000*(f['node']=='ov04')+400*incoming[f['id']]+200*len(unresolved_indirect)
        attempts=r['attempts'].get(f['id'],[])
        unchanged=max(0,len(attempts)-len({(a.get('source_sha256'),a.get('comparison_identity')) for a in attempts}))
        score=f['size']//8+80*len(f['direct_callees'])-30*known+30*len(f['referenced_data'])+100*len(f['relocations'])+500*len(unresolved_indirect)-unlock+1000*unchanged
        if f['id'] in r['blockers'] and not r['blockers'][f['id']].get('next_action'):score+=5000
        if f['extent_status']!='CLOSED_CFG':score+=10000
        if f['hunk']==0:score+=20000
        if f['ownership']!='UNKNOWN':continue
        if f['hunk']==14:score-=100
        # Resident A4 jump stubs are naturally linkable extern calls.  Their
        # exact identity is independently checked by function_compare, so an
        # unrecovered resident implementation is not an unknown dependency for
        # an overlay candidate.
        unknown={c['id'] for c in f['direct_callees'] if c['basis']!='A4_RELOCATED_JMP_STUB'
                 and c['id'] not in r['functions'] and c['id'] not in known_runtime and (c['hunk'],c['offset']) not in runtime}
        local_dependencies=sorted({c['id'] for c in f['direct_callees'] if c['basis']=='PC_RELATIVE' and c['hunk']==f['hunk'] and c['id'] not in r['functions']})
        same_node_calls=[c for c in f['direct_callees'] if c['basis']=='PC_RELATIVE' and c['hunk']==f['hunk']]
        # A local unit may include recovered bridge functions between its caller
        # and callee.  It is usable only when the full interval is contiguous
        # canonical ownership; otherwise no source unit may span the gap.
        unit_ready=True
        if same_node_calls:
            lo=min([f['start']]+[c['offset'] for c in same_node_calls])
            hi=max([f['end']]+[c['offset'] for c in same_node_calls])
            cursor=lo
            for item in sorted((x for x in l['functions'] if x['hunk']==f['hunk'] and lo<=x['start'] and x['end']<=hi),key=lambda x:x['start']):
                if item['start']!=cursor or item['id']!=f['id'] and item['id'] not in r['functions']:
                    unit_ready=False;break
                cursor=item['end']
            unit_ready=unit_ready and cursor==hi
        result.append(dict(id=f['id'],node=f['node'],size=f['size'],score=score,extent=f['extent_status'],calls=len(f['direct_callees']),indirect=len(unresolved_indirect),state=state,
                           confidence=f['confidence'],unknown_calls=len(unknown),data_references=len(f['referenced_data']),pending_local_dependencies=local_dependencies,
                           pc_relative_data=sum(x['kind']=='PC_RELATIVE_DATA' for x in f['referenced_data']),same_node_unit_ready=unit_ready,
                           unlock_value=unlock,unlocks_callers=incoming[f['id']],unchanged_hypotheses=unchanged,
                           campaign='ov04' if f['node']=='ov04' else None,
                           blocker_category=blocker_category(r['blockers'].get(f['id'],{}).get('reason',''))))
    return sorted(result,key=lambda x:(x['score'],x['id']))


BLOCKER_CATEGORIES=('SOURCE_SHAPE','DECLARATION_VIEW','OBJECT/TU_LAYOUT','DATA_OWNERSHIP',
                    'CALL_BINDING','CFG/BOUNDARY','RUNTIME/LIBRARY','TOOLCHAIN')


def blocker_category(reason):
    text=reason.upper()
    for words,category in [(('DECLARATION','STRUCT_VIEW'),'DECLARATION_VIEW'),
                           (('FFP','FIXUP','CALL_BINDING','REGISTER_CALL'),'CALL_BINDING'),
                           (('CFG','BOUNDARY','INDIRECT','EXTENT'),'CFG/BOUNDARY'),
                           (('LAYOUT','OBJECT','CYCLIC','GAP'),'OBJECT/TU_LAYOUT'),
                           (('DATA','LITERAL','TABLE'),'DATA_OWNERSHIP'),
                           (('RUNTIME','LIBRARY'),'RUNTIME/LIBRARY'),
                           (('TOOLCHAIN','BYTE_RETURN_ABI','CHAR_RETURN_EXTENSION'),'TOOLCHAIN')]:
        if any(w in text for w in words):return category
    return 'SOURCE_SHAPE'


def call_excerpt(source,name,limit=900):
    """Return one complete bounded C call expression for an evidence-backed name."""
    for match in re.finditer(r'\b'+re.escape(name)+r'\s*\(',source):
        line_start=source.rfind('\n',0,match.start())+1
        if re.search(r'\bextern\b',source[line_start:match.start()]):continue
        depth=0
        for index in range(match.start(),len(source)):
            char=source[index]
            if char=='(':depth+=1
            elif char==')':
                depth-=1
                if depth==0:
                    end=index+1
                    while end<len(source) and source[end].isspace():end+=1
                    if end<len(source) and source[end]==';':end+=1
                    excerpt=source[match.start():end]
                    return excerpt if len(excerpt)<=limit else None
    return None


def canonical_call_examples(calls,ledger,limit=4):
    """Expose proven caller expressions for external ABI guidance only."""
    wanted=[]
    for call in calls:
        if call['basis']=='A4_RELOCATED_JMP_STUB':
            name='F_h%02d_%04X'%(call['hunk'],call['offset'])
            if name not in wanted:wanted.append(name)
    examples=[]
    for name in wanted:
        for caller_id,item in sorted(ledger.get('functions',{}).items()):
            path=item.get('source')
            if not path:continue
            if not is_active_repo_path(ROOT/path,ROOT):continue
            source_path=canonical_path(ROOT,path)
            if not source_path.is_file():continue
            excerpt=call_excerpt(source_path.read_text(),name)
            if excerpt:
                examples.append(dict(callee=name,caller=caller_id,call=excerpt))
                break
        if len(examples)>=limit:return examples
    return examples


def facts(fid,max_instructions=160,max_bytes=65536):
    ledger=evidence();r=recovery();f=next((f for f in ledger['functions'] if f['id']==fid),None)
    runtime=runtime_dependencies(ledger)
    require(f is not None,'unknown function id')
    require(len(f['instructions'])<=max_instructions,'function exceeds bounded grinder budget; choose a smaller ranked candidate')
    refs=sorted({(x['hunk'],x['offset']) for x in f['referenced_data']} |
                {(x['target_hunk'],x['addend_raw']) for x in f['relocations'] if x['target_hunk'] in (1,2)})
    previous=[];previous_sources={}
    # Fresh packets never import attempt history. Workers use an explicit
    # current diagnostic/cache key when testing a changed hypothesis.
    fingerprints=[];index=ROOT/'evidence/fingerprints/index.json'
    if index.exists():
        m=[i['mnemonic'] for i in f['instructions']]
        entries=json.loads(index.read_text())['entries']
        for profile in ('aztec36','aztec50-short'):
            closest=sorted((e for e in entries if e['profile']==profile and e['status']=='COMPILED'),key=lambda e:SequenceMatcher(None,m,e['mnemonics']).ratio(),reverse=True)[:2]
            fingerprints.extend(dict(name=e['name'],profile=profile,source=canonical_path(ROOT,e['source']).read_text(),assembly=e['assembly'][:2400],flags=e['compiler']['flags']) for e in closest if is_active_repo_path(ROOT/e['source'],ROOT))
    dependencies=[]
    for call in f['direct_callees'][:12]:
        dep=r['functions'].get(call['id'])
        if dep and is_active_repo_path(ROOT/dep['source'],ROOT):dependencies.append(dict(id=call['id'],name='F_h%02d_%04X'%(call['hunk'],call['offset']),state=dep['state'],source=canonical_path(ROOT,dep['source']).read_text()[:3000]))
    call_examples=canonical_call_examples(f['direct_callees'],r)
    packages=dict(schema_version=1,id=fid,extent={k:f[k] for k in ('node','hunk','start','end','size','sha256','extent_status','confidence')},
        entry_evidence=f['entry_evidence'],instructions=f['instructions'],cfg=f['cfg'],
        calls=[dict(c,name='F_h%02d_%04X'%(c['hunk'],c['offset']),current_state=r['functions'].get(c['id'],runtime.get((c['hunk'],c['offset']),{})).get('state','DISCOVERED'),
                    **({'runtime':runtime[(c['hunk'],c['offset'])]} if (c['hunk'],c['offset']) in runtime else {})) for c in f['direct_callees']],
        indirect=f['indirect_control_flow'],data=[dict(hunk=h,offset=o,name='G_h%02d_%04X'%(h,o),type_status='INFER_FROM_ACCESSES') for h,o in refs],
        strings=f['referenced_strings'],relocations=[dict(x,target_name=('G_h%02d_%04X'%(x['target_hunk'],x['addend_raw'])) if x['target_hunk'] in (1,2) else None) for x in f['relocations']],stack_frames=f['stack_frames'],argument_accesses=f['likely_argument_accesses'],
        abi=dict(a4_bias=ledger['a4']['bias'],profiles=['aztec36','aztec36-x3','aztec36-large-data','aztec36-long','aztec50','aztec50-short'],historical_selection='AMBIGUOUS',fingerprints='evidence/fingerprints/index.json'),
        previous_attempts=previous,previous_sources=previous_sources,compiler_examples=fingerprints,recovered_dependencies=dependencies,
        canonical_call_examples=call_examples,
        contract='Return self-contained historical-style C defining recovered(...). Use extern declarations and mechanical G_hNN_OFFSET / F_hNN_OFFSET names for evidence-backed dependencies. No asm, placement directives, binary literal code, or emulator operations. The verifier decides equality.')
    from recovery_feedback import advisory_feedback
    guidance=advisory_feedback(fid,None,root=ROOT)
    if len(json.dumps(packages).encode())+len(json.dumps(guidance).encode())<max_bytes-536:
        packages['advisory_feedback']=guidance
    else:
        packages['advisory_feedback']=dict(status='OMITTED_FOR_BUDGET',promotion_eligible=False)
    require(len(json.dumps(packages).encode())<=max_bytes,'fact package exceeds %d-byte budget; choose a smaller candidate'%max_bytes)
    return packages


def save_rank():
    write_json(ROOT/'evidence/functions/ranking.json',dict(schema_version=2,closure_campaign='ov04',
        policy='Expected closure/dependency/CFG unlock dominates size. Requeue only with a changed hypothesis and a bounded next experiment.',candidates=ranked()))
