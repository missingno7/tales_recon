"""Strict re-derived anchored entry boundaries; no source acceptance."""
import json
from common import require, sha256
from repo_paths import canonical_path
INPUT = 'evidence/rules/unreferenced-entries/entries.json'
KIND = 'CURATED_UNREFERENCED_ENTRY'

def identity(root):
    p=canonical_path(root,INPUT)
    return {INPUT:sha256(p.read_bytes())} if p.exists() else {}

def load(root,blob):
    p=canonical_path(root,INPUT)
    if not p.exists():return []
    doc=json.loads(p.read_bytes())
    require(set(doc)=={'schema_version','game_sha256','source_acceptance','entries'},'uncalled input schema differs')
    require(type(doc['schema_version']) is int and doc['schema_version']==1 and doc['source_acceptance'] is False,'uncalled input grants no source acceptance')
    require(doc['game_sha256']==sha256(blob),'uncalled game hash changed')
    require(isinstance(doc['entries'],list),'uncalled entries must be a list')
    fields={'id','hunk','start','end','contribution_end','predecessor','next_entry','justification'};ids=set();coords=set()
    for r in doc['entries']:
        require(isinstance(r,dict) and set(r)==fields,'uncalled entry schema differs')
        require(all(type(r[k]) is int for k in ('hunk','start','end','contribution_end')),'uncalled coordinates must be integers')
        h,a,b=r['hunk'],r['start'],r['end']
        require((h==0 or h>=3) and 0<=a<b<=r['contribution_end'] and a%2==0,'uncalled entry is not an aligned CODE interval')
        require(r['id']==(('resident' if h==0 else 'ov%02d'%h)+'_F_%04X'%a),'uncalled identity differs')
        require(isinstance(r['predecessor'],str) and (r['next_entry'] is None or isinstance(r['next_entry'],str)),'uncalled neighbor identity differs')
        require(isinstance(r['justification'],str) and r['justification'].strip(),'uncalled justification missing')
        require(r['id'] not in ids and (h,a) not in coords,'duplicate uncalled entry')
        ids.add(r['id']);coords.add((h,a))
    return doc['entries']

def fresh_functions(c):
    """Walk actual decoder inputs instead of trusting serialized extents."""
    out=[]
    for h,a in sorted(c.entries):
        f=c.walk(h,a)
        for r in f['referenced_data']:
            data=c.data.get(r['hunk'],b'');off=r['offset']
            if not 0<=off<len(data):continue
            end=data.find(b'\0',off,min(len(data),off+160));raw=data[off:end] if end>=0 else b''
            empty=end==off and r['kind']=='PC_RELATIVE_DATA' and r['hunk']==h
            if (raw or empty) and all(32<=v<127 or v in (9,10,13) for v in raw):
                f['referenced_strings'].append(dict(hunk=r['hunk'],offset=off,text=raw.decode('ascii')))
        out.append(f)
    return out

def closed_shape(c,f):
    data=c.data[f['hunk']]
    require(f['instructions'] and f['instructions'][0]['offset']==f['start'] and data[f['start']:f['start']+2]==b'\x4e\x55','uncalled entry lacks LINK')
    require(not f['boundary_stops'] and not f['undecoded_gaps'] and f['return_sites'],'uncalled CFG does not close')
    require(not f['indirect_control_flow'],'uncalled entry has unresolved control flow')
    from function_census import ends_in_epilogue
    require(ends_in_epilogue(c,f),'uncalled entry lacks a closed local epilogue')
    require(all(data[a:a+2]==b'\x4e\x75' for a in f['return_sites']),'uncalled CFG has a non-RTS return')
    spans=[(i['offset'],i['offset']+i['size']) for i in f['instructions']]
    spans += [(t['table_start'],t['table_end']) for t in f.get('jump_tables',[])]
    cursor=f['start']
    for lo,hi in sorted(spans):
        require(lo==cursor and hi>lo,'uncalled entry has overlapping or undecoded bytes');cursor=hi
    require(cursor==f['end'] and all(f['start']<=e['target']<f['end'] for e in f['cfg']),'uncalled CFG escapes extent')

def tail_end(c,f):
    refs=[r for r in f['referenced_data'] if r['kind']=='PC_RELATIVE_DATA' and r['hunk']==f['hunk']]
    if not refs:return f['end']
    from owned_code_data import expected_string_tail
    tail,own=expected_string_tail(f,context=dict(blob=c.blob,model=c.model))
    require(c.data[f['hunk']][f['end']:own['end']]==tail,'uncalled literal bytes differ')
    return own['end']

def claimed_ranges(root):
    p=canonical_path(root,'recovery/ledger.json')
    if not p.exists():return []
    ledger=json.loads(p.read_bytes());out=[]
    for fid,item in ledger.get('functions',{}).items():
        e=item['evidence_extent'];end=e['end']
        if item['state']=='FUNCTION_WITH_DATA_MATCH':
            proof=canonical_path(root,item['proof']);require(sha256(proof.read_bytes())==item['proof_sha256'],'uncalled ownership proof changed')
            end=json.loads(proof.read_bytes())['data_ownership']['end']
        out.append((fid,e['hunk'],e['start'],end))
    for fid,item in ledger.get('mixed_source_objects',{}).items():
        proof=canonical_path(root,item['proof']);require(sha256(proof.read_bytes())==item['proof_sha256'],'uncalled mixed ownership proof changed')
        e=json.loads(proof.read_bytes())['original'];out.append((fid,e['hunk'],e['start'],e['end']))
    return out

def independently_referenced_entry(c, target, functions):
    """A next boundary may be a non-C entry; rederive an actual incoming edge.

    This does not close that neighbor's CFG, change its language, or grant any
    entry strength to an adjacent LINK. No curated text/source-match shortcut.
    """
    from analysis_support import instruction
    for caller in functions:
        for call in caller['direct_callees']:
            if (call['hunk'],call['offset']) != (target['hunk'],target['start']):continue
            ins=instruction(c.md,c.data[caller['hunk']],call['site'])
            if ins is None:continue
            derived=c.target(caller['hunk'],ins)
            if derived and derived[:2]==(target['hunk'],target['start']):return True
    return False


def validate(c,root):
    """Validate all listed CFGs before admitting any coordinate-ordered chain.

    Listed neighbors must independently close; a chain must have pre-existing
    closed anchors, or end in its own fully bounded contiguous literal tail.
    All ownership and incoming references are checked afresh, including tails.
    """
    rows=load(root,c.blob)
    if not rows:return []
    fs=fresh_functions(c);by={f['id']:f for f in fs};listed={r['id']:r for r in rows};claims=claimed_ranges(root)
    ordered=sorted(rows,key=lambda r:(r['hunk'],r['start']))
    for r in ordered:
        fid=r['id'];f=by.get(fid)
        require(f is not None,'uncalled entry not independently discovered: '+fid)
        require((f['hunk'],f['start'],f['end'])==(r['hunk'],r['start'],r['end']),'uncalled measured extent changed: '+fid)
        closed_shape(c,f);require(tail_end(c,f)==r['contribution_end'],'uncalled contribution boundary changed')
        for owner,h,a,b in claims:
            if h==f['hunk'] and a<r['contribution_end'] and f['start']<b:
                # After exact promotion, only this identical own span is allowed.
                require(owner==fid and (a,b)==(f['start'],r['contribution_end']),'uncalled entry owned by another contribution')
        require(not any(a<r['contribution_end'] and f['start']<b for a,b,_ in c.blocked[f['hunk']]),'uncalled entry overlaps classified data')
        for other in fs:
            if other['id']==fid:continue
            require(other['hunk']!=f['hunk'] or not (other['start']<r['contribution_end'] and f['start']<other['end']),'uncalled entry overlaps decoded function')
            targets=[(q['hunk'],q['offset']) for q in other['referenced_data']+other['direct_callees']]
            if other['hunk']==f['hunk']:targets += [(f['hunk'],e['target']) for e in other['cfg']]
            require(not any(h==f['hunk'] and f['start']<=a<r['contribution_end'] for h,a in targets),'uncalled entry has foreign reference')
        for q in c.model['relocations']:
            if q['target_hunk']==f['hunk'] and f['start']<=q['addend_raw']<r['contribution_end']:
                require(q['source_hunk']==f['hunk'] and f['start']<=q['source_offset']<f['end'],'uncalled entry has foreign relocation')
        pred=by.get(r['predecessor'])
        require(pred is not None and pred['hunk']==f['hunk'] and pred['start']<f['start'],'uncalled predecessor differs')
        if pred['id'] in listed:closed_shape(c,pred)
        else:require(pred['extent_status']=='CLOSED_CFG','uncalled predecessor is not closed')
        from function_census import ends_in_epilogue
        require(ends_in_epilogue(c,pred),'uncalled predecessor lacks a closed local epilogue')
        require(tail_end(c,pred)==f['start'],'uncalled entry does not follow complete predecessor')
        if r['next_entry'] is None:
            require(r['contribution_end']>f['end'] and r['contribution_end']==len(c.data[f['hunk']]),'uncalled terminal entry lacks bounded literal tail')
        else:
            nxt=by.get(r['next_entry'])
            require(nxt is not None and nxt['hunk']==f['hunk'] and nxt['start']==r['contribution_end'],'uncalled next boundary differs')
            if nxt['id'] in listed:closed_shape(c,nxt)
            else:require(nxt['extent_status']=='CLOSED_CFG' or independently_referenced_entry(c,nxt,fs),'uncalled next anchor is not independently bounded')
    for r in ordered:
        pred=r['predecessor'];seen=set()
        while pred in listed:
            require(pred not in seen,'uncalled predecessor cycle');seen.add(pred);pred=listed[pred]['predecessor']
        require(by[pred]['extent_status']=='CLOSED_CFG','uncalled chain lacks closed predecessor anchor')
    return [dict(kind=KIND,id=r['id'],hunk=r['hunk'],start=r['start'],justification=r['justification'],input=INPUT,input_sha256=identity(root)[INPUT]) for r in ordered]
