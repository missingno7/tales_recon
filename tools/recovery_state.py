"""Rank and package bounded work; no reconstructed-source claims from discovery."""
import json
from difflib import SequenceMatcher
from pathlib import Path
from common import require,write_json,sha256
from analysis_support import ROOT

LEDGER=ROOT/'recovery/ledger.json'


def recovery():
    return json.loads(LEDGER.read_text()) if LEDGER.exists() else dict(schema_version=1,functions={},attempts={},blockers={})


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
    known_runtime={x['id'] for x in l['functions'] if x['ownership']=='RUNTIME_CANDIDATE'}
    for f in l['functions']:
        if node and f['node']!=node:continue
        state=r['functions'].get(f['id'],{}).get('state','DISCOVERED')
        if state in ('FUNCTION_CODE_MATCH','FUNCTION_WITH_DATA_MATCH','MODULE_MATCH','OVERLAY_NODE_MATCH','BLOCKED'):continue
        if f['id'] in r['blockers']:state='BLOCKED'
        elif f['id'] in r['attempts']:
            state='CODEGEN_SIMILAR' if any((a.get('mnemonic_similarity') or 0)>=0.75 for a in r['attempts'][f['id']]) else 'CANDIDATE_C'
        known=sum(c['id'] in r['functions'] or c['id'] in known_runtime or (c['hunk'],c['offset']) in runtime for c in f['direct_callees'])
        score=f['size']+80*len(f['direct_callees'])-30*known+30*len(f['referenced_data'])+100*len(f['relocations'])+500*len(f['indirect_control_flow'])
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
        result.append(dict(id=f['id'],node=f['node'],size=f['size'],score=score,extent=f['extent_status'],calls=len(f['direct_callees']),indirect=len(f['indirect_control_flow']),state=state,
                           confidence=f['confidence'],unknown_calls=len(unknown),data_references=len(f['referenced_data']),pending_local_dependencies=local_dependencies,
                           pc_relative_data=sum(x['kind']=='PC_RELATIVE_DATA' for x in f['referenced_data']),same_node_unit_ready=unit_ready))
    return sorted(result,key=lambda x:(x['score'],x['id']))


def facts(fid,max_instructions=160):
    ledger=evidence();r=recovery();f=next((f for f in ledger['functions'] if f['id']==fid),None)
    runtime=runtime_dependencies(ledger)
    require(f is not None,'unknown function id')
    require(len(f['instructions'])<=max_instructions,'function exceeds bounded grinder budget; choose a smaller ranked candidate')
    refs=sorted({(x['hunk'],x['offset']) for x in f['referenced_data']} |
                {(x['target_hunk'],x['addend_raw']) for x in f['relocations'] if x['target_hunk'] in (1,2)})
    previous=[];previous_sources={}
    for attempt in r['attempts'].get(fid,[])[-5:]:
        receipt=json.loads((ROOT/attempt['receipt']).read_text())
        previous.append({k:receipt[k] for k in ('source_sha256','compiler','flags','verdict','reason','expected_length','actual_length','first_differing_instruction','relocation_issues','mnemonic_similarity','compiler_feedback','unit_feedback','unit_blocker') if k in receipt})
        cache=ROOT/'build/compile-cache'/receipt['cache_key'];manifest=cache/'receipt.json'
        candidate=ROOT/'recovery/candidates'/fid/(receipt['source_sha256']+'.c')
        source=None
        if candidate.exists():source=candidate.read_text()
        elif manifest.exists():
            retained=json.loads(manifest.read_text());source=(cache/(retained['prefix']+'.c')).read_text()
        if source is not None:
            require(sha256(source.encode())==receipt['source_sha256'],'previous candidate source hash changed')
            previous_sources[receipt['source_sha256']]=dict(source=source[:4096],truncated=len(source)>4096)
    fingerprints=[];index=ROOT/'evidence/fingerprints/index.json'
    if index.exists():
        m=[i['mnemonic'] for i in f['instructions']]
        entries=json.loads(index.read_text())['entries']
        for profile in ('aztec36','aztec50-short'):
            closest=sorted((e for e in entries if e['profile']==profile and e['status']=='COMPILED'),key=lambda e:SequenceMatcher(None,m,e['mnemonics']).ratio(),reverse=True)[:2]
            fingerprints.extend(dict(name=e['name'],profile=profile,source=(ROOT/e['source']).read_text(),assembly=e['assembly'][:2400],flags=e['compiler']['flags']) for e in closest)
    dependencies=[]
    for call in f['direct_callees'][:12]:
        dep=r['functions'].get(call['id'])
        if dep:dependencies.append(dict(id=call['id'],name='F_h%02d_%04X'%(call['hunk'],call['offset']),state=dep['state'],source=(ROOT/dep['source']).read_text()[:3000]))
    packages=dict(schema_version=1,id=fid,extent={k:f[k] for k in ('node','hunk','start','end','size','sha256','extent_status','confidence')},
        entry_evidence=f['entry_evidence'],instructions=f['instructions'],cfg=f['cfg'],
        calls=[dict(c,name='F_h%02d_%04X'%(c['hunk'],c['offset']),current_state=r['functions'].get(c['id'],runtime.get((c['hunk'],c['offset']),{})).get('state','DISCOVERED'),
                    **({'runtime':runtime[(c['hunk'],c['offset'])]} if (c['hunk'],c['offset']) in runtime else {})) for c in f['direct_callees']],
        indirect=f['indirect_control_flow'],data=[dict(hunk=h,offset=o,name='G_h%02d_%04X'%(h,o),type_status='INFER_FROM_ACCESSES') for h,o in refs],
        strings=f['referenced_strings'],relocations=[dict(x,target_name=('G_h%02d_%04X'%(x['target_hunk'],x['addend_raw'])) if x['target_hunk'] in (1,2) else None) for x in f['relocations']],stack_frames=f['stack_frames'],argument_accesses=f['likely_argument_accesses'],
        abi=dict(a4_bias=ledger['a4']['bias'],profiles=['aztec36','aztec36-x3','aztec36-large-data','aztec36-long','aztec50','aztec50-short'],historical_selection='AMBIGUOUS',fingerprints='evidence/fingerprints/index.json'),
        previous_attempts=previous,previous_sources=previous_sources,compiler_examples=fingerprints,recovered_dependencies=dependencies,
        contract='Return self-contained historical-style C defining recovered(...). Use extern declarations and mechanical G_hNN_OFFSET / F_hNN_OFFSET names for evidence-backed dependencies. No asm, placement directives, binary literal code, or emulator operations. The verifier decides equality.')
    require(len(json.dumps(packages).encode())<=65536,'fact package exceeds 64 KiB budget; choose a smaller candidate')
    return packages


def save_rank():
    write_json(ROOT/'evidence/functions/ranking.json',dict(schema_version=1,bootstrap='ov14',semantic_pilot='ov07',
        bootstrap_reason='ov12 has a single 2998-byte closed CFG with 132 calls; ov14 contains 20-byte and 80-byte no-call leaves.',candidates=ranked()))
