"""Validate curated source-proof inputs independently of generated topology metrics."""
import json
from common import require,sha256


def load_promotions(root,blob,model,analysis):
    path=root/'recovery/ledger.json'
    if not path.exists():return []
    ledger=json.loads(path.read_text());out=[];occupied=set()
    for fid,item in sorted(ledger['functions'].items()):
        require(item['state']=='FUNCTION_CODE_MATCH','unsupported promotion level: '+fid)
        source=(root/item['source']).resolve();proof_path=(root/item['proof']).resolve()
        require(source.is_relative_to(root.resolve()) and proof_path.is_relative_to(root.resolve()),'proof paths escape workspace')
        proof=json.loads(proof_path.read_text());extent=proof['evidence_extent'];comparison=proof['comparison']
        require(sha256(proof_path.read_bytes())==item['proof_sha256'],'promotion receipt changed: '+fid)
        require(proof['id']==fid and proof['state']==item['state'] and extent==item['evidence_extent'],'promotion identity differs')
        require(sha256(source.read_bytes())==item['source_sha256']==proof['source_sha256'],'promoted source changed: '+fid)
        h=next(h for h in model['hunks'] if h['number']==extent['hunk'])
        start,end=extent['start'],extent['end'];size=end-start
        require(h['type']=='CODE' and 0<=start<end<=h['initialized_size'] and size==extent['size'],'invalid promotion extent')
        raw=blob[h['content_offset']+start:h['content_offset']+end]
        require(sha256(raw)==extent['sha256']==comparison['expected_sha256']==comparison['normalized_sha256'],'promotion bytes disagree')
        require(comparison['verdict']=='EQUAL' and comparison['relocation_equal'] and not comparison['relocation_issues'],'promotion comparison failed')
        require(comparison['expected_length']==comparison['actual_length']==size and proof['regression']['passed'],'incomplete promotion')
        require(comparison['data_contributions']['candidate_data']==comparison['data_contributions']['candidate_bss']==0,'unproven owned data')
        f=next((f for f in analysis.get('functions',[]) if f['id']==fid),None)
        require(f and all(f[k]==extent[k] for k in ('hunk','start','end','size','sha256','extent_status')) and f['extent_status']=='CLOSED_CFG','promotion extent no longer supported')
        if proof['compiler']['source_sha256']!=proof['source_sha256']:
            unit_path=(root/comparison.get('complete_unit_receipt','')).resolve()
            require(unit_path.is_relative_to(root.resolve()) and unit_path.is_file(),'combined source requires complete unit receipt')
            require(sha256(unit_path.read_bytes())==comparison['complete_unit_receipt_sha256'],'complete unit receipt changed')
            unit=json.loads(unit_path.read_text());unit_source=unit_path.parent/'unit.c'
            require(sha256(unit_source.read_bytes())==unit['combined_source_sha256']==proof['compiler']['source_sha256'],'combined source hash differs')
            require(unit['object_sha256']==proof['object_hash'] and unit['source_sha256']==proof['source_sha256'],'unit object/source identity differs')
            require(unit['verdict']=='EQUAL' and unit['unclaimed_bytes']==0 and unit['expected_length']==unit['actual_length'],'unit is not completely proven')
            require(unit['expected_sha256']==unit['normalized_sha256'],'unit normalized bytes differ')
            require(any(m['id']==fid for m in unit['ordered_members']),'promoted function missing from unit')
            unit_raw=[]
            for m in unit['ordered_members']:
                mf=next((v for v in analysis.get('functions',[]) if v['id']==m['id']),None)
                require(mf and all(mf[k]==m[k] for k in ('hunk','start','end','size','sha256')),'unit member evidence changed')
                mr=next((v for v in unit['members'] if v['id']==m['id']),None)
                require(mr and mr['verdict']=='EQUAL' and mr['normalized_sha256']==m['sha256'],'unmatched member in unit')
                unit_raw.append(bytes.fromhex(mf['raw_bytes']))
            require(sha256(b''.join(unit_raw))==unit['expected_sha256'],'complete unit original bytes disagree')
            for dep,digest in unit['dependency_sources'].items():
                require(ledger['functions'].get(dep,{}).get('source_sha256')==digest,'unit dependency source changed')
        locations={(extent['hunk'],offset) for offset in range(start,end)}
        require(not locations & occupied,'overlapping promoted source contributions');occupied.update(locations)
        out.append(dict(id=fid,node=h['node'],**extent,source=item['source'],proof=item['proof'],state=item['state']))
    return out
