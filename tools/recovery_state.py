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


def ranked(node=None):
    l=evidence();r=recovery();result=[]
    for f in l['functions']:
        if node and f['node']!=node:continue
        state=r['functions'].get(f['id'],{}).get('state','DISCOVERED')
        if state in ('FUNCTION_CODE_MATCH','FUNCTION_WITH_DATA_MATCH','MODULE_MATCH','OVERLAY_NODE_MATCH','BLOCKED'):continue
        if f['id'] in r['blockers']:state='BLOCKED'
        elif f['id'] in r['attempts']:
            state='CODEGEN_SIMILAR' if any((a.get('mnemonic_similarity') or 0)>=0.75 for a in r['attempts'][f['id']]) else 'CANDIDATE_C'
        known=sum(c['id'] in r['functions'] or any(x['id']==c['id'] and x['ownership']=='RUNTIME_CANDIDATE' for x in l['functions']) for c in f['direct_callees'])
        score=f['size']+80*len(f['direct_callees'])-30*known+30*len(f['referenced_data'])+100*len(f['relocations'])+500*len(f['indirect_control_flow'])
        if f['extent_status']!='CLOSED_CFG':score+=10000
        if f['hunk']==0:score+=20000
        if f['ownership']!='UNKNOWN':continue
        if f['hunk']==14:score-=100
        result.append(dict(id=f['id'],node=f['node'],size=f['size'],score=score,extent=f['extent_status'],calls=len(f['direct_callees']),indirect=len(f['indirect_control_flow']),state=state))
    return sorted(result,key=lambda x:(x['score'],x['id']))


def facts(fid,max_instructions=160):
    ledger=evidence();r=recovery();f=next((f for f in ledger['functions'] if f['id']==fid),None)
    require(f is not None,'unknown function id')
    require(len(f['instructions'])<=max_instructions,'function exceeds bounded grinder budget; choose a smaller ranked candidate')
    refs=sorted({(x['hunk'],x['offset']) for x in f['referenced_data']})
    previous=[];previous_sources={}
    for attempt in r['attempts'].get(fid,[])[-5:]:
        receipt=json.loads((ROOT/attempt['receipt']).read_text())
        previous.append({k:receipt[k] for k in ('source_sha256','compiler','flags','verdict','reason','expected_length','actual_length','first_differing_instruction','relocation_issues','mnemonic_similarity','compiler_feedback') if k in receipt})
        cache=ROOT/'build/compile-cache'/receipt['cache_key'];manifest=cache/'receipt.json'
        if manifest.exists():
            retained=json.loads(manifest.read_text());source=(cache/(retained['prefix']+'.c')).read_text()
            require(sha256(source.encode('ascii'))==receipt['source_sha256'],'previous candidate source hash changed')
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
        if dep:dependencies.append(dict(id=call['id'],state=dep['state'],source=(ROOT/dep['source']).read_text()[:3000]))
    packages=dict(schema_version=1,id=fid,extent={k:f[k] for k in ('node','hunk','start','end','size','sha256','extent_status','confidence')},
        entry_evidence=f['entry_evidence'],instructions=f['instructions'],cfg=f['cfg'],
        calls=[dict(c,current_state=r['functions'].get(c['id'],{}).get('state','DISCOVERED')) for c in f['direct_callees']],
        indirect=f['indirect_control_flow'],data=[dict(hunk=h,offset=o,name='G_h%02d_%04X'%(h,o),type_status='INFER_FROM_ACCESSES') for h,o in refs],
        strings=f['referenced_strings'],relocations=f['relocations'],stack_frames=f['stack_frames'],argument_accesses=f['likely_argument_accesses'],
        abi=dict(a4_bias=ledger['a4']['bias'],profiles=['aztec36','aztec36-long','aztec50','aztec50-short'],historical_selection='AMBIGUOUS',fingerprints='evidence/fingerprints/index.json'),
        previous_attempts=previous,previous_sources=previous_sources,compiler_examples=fingerprints,recovered_dependencies=dependencies,
        contract='Return self-contained historical-style C defining recovered(...). Use extern declarations and mechanical G_hNN_OFFSET / F_hNN_OFFSET names for evidence-backed dependencies. No asm, placement directives, binary literal code, or emulator operations. The verifier decides equality.')
    require(len(json.dumps(packages).encode())<=65536,'fact package exceeds 64 KiB budget; choose a smaller candidate')
    return packages


def save_rank():
    write_json(ROOT/'evidence/functions/ranking.json',dict(schema_version=1,bootstrap='ov14',semantic_pilot='ov07',
        bootstrap_reason='ov12 has a single 2998-byte closed CFG with 132 calls; ov14 contains 20-byte and 80-byte no-call leaves.',candidates=ranked()))
