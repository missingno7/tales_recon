"""Validate curated source-proof inputs independently of generated topology metrics."""
import json
from common import require,sha256


def owned_tail_boundary(h,fid,end,owned_end,analysis,blob):
    """Prove a literal tail ends at the next entry or final HUNK alignment."""
    starts=sorted(x['start'] for x in analysis['functions']
                  if x['hunk']==h['number'] and x['start']>=end and x['id']!=fid)
    if starts:
        return owned_end==starts[0]
    padding=h['initialized_size']-owned_end
    if not (0<=padding<=3 and (owned_end+padding)%4==0):
        return False
    return blob[h['content_offset']+owned_end:h['content_offset']+h['initialized_size']]==b'\0'*padding


def load_promotions(root,blob,model,analysis):
    path=root/'recovery/ledger.json'
    if not path.exists():return []
    ledger=json.loads(path.read_text());out=[];occupied=set()
    for fid,item in sorted(ledger['functions'].items()):
        require(item['state'] in ('FUNCTION_CODE_MATCH','FUNCTION_WITH_DATA_MATCH'),'unsupported promotion level: '+fid)
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
        require(comparison['verdict']=='EQUAL' and comparison['relocation_equal'] and not comparison['relocation_issues'],'promotion comparison failed')
        f=next((f for f in analysis.get('functions',[]) if f['id']==fid),None)
        require(f and all(f[k]==extent[k] for k in ('hunk','start','end','size','sha256','extent_status')) and f['extent_status']=='CLOSED_CFG','promotion extent no longer supported')
        if item['state']=='FUNCTION_CODE_MATCH':
            require(sha256(raw)==extent['sha256']==comparison['expected_sha256']==comparison['normalized_sha256'],'promotion bytes disagree')
            require(comparison['expected_length']==comparison['actual_length']==size and proof['regression']['passed'],'incomplete promotion')
            require(comparison['data_contributions']['candidate_data']==comparison['data_contributions']['candidate_bss']==0,'unproven owned data')
            owned_end=end
        else:
            owned=proof['data_ownership'];code=comparison.get('code_comparison',{})
            require(isinstance(owned,dict) and owned==comparison.get('owned_code_data'),'owned CODE-data receipt differs')
            require(comparison.get('proof_level')=='FUNCTION_WITH_DATA_MATCH','wrong data promotion proof level')
            require(code.get('verdict')=='EQUAL' and code.get('expected_length')==code.get('actual_length')==size,
                    'function portion of CODE-data promotion is incomplete')
            require(sha256(raw)==extent['sha256']==code.get('expected_sha256')==code.get('normalized_sha256'),
                    'CODE-data function bytes disagree')
            owned_end=owned.get('end');strings=owned.get('strings');padding=owned.get('alignment_padding')
            require(isinstance(owned_end,int) and owned.get('start')==end and isinstance(strings,list) and padding in (0,1),
                    'invalid owned CODE-data bounds')
            literals=b''.join(s['text'].encode('ascii')+b'\0' for s in strings)
            tail=literals+(b'\0' if padding else b'')
            require(owned_end==end+len(tail) and sha256(tail)==owned.get('expected_tail_sha256')==owned.get('actual_tail_sha256'),
                    'owned CODE-data payload disagrees')
            actual_tail=blob[h['content_offset']+end:h['content_offset']+owned_end]
            require(actual_tail==tail and comparison['actual_length']==size+len(tail) and proof['regression']['passed'],
                    'owned CODE-data contribution is incomplete')
            refs=sorted(r['offset'] for r in f['referenced_data'] if r['kind']=='PC_RELATIVE_DATA' and r['hunk']==f['hunk'])
            require(refs==[s['offset'] for s in strings] and owned_tail_boundary(h,fid,end,owned['end'],analysis,blob),
                    'owned CODE-data lacks contiguous reference or next-entry proof')
        if proof['compiler']['source_sha256']!=proof['source_sha256']:
            unit_path=(root/comparison.get('complete_unit_receipt','')).resolve()
            require(unit_path.is_relative_to(root.resolve()) and unit_path.is_file(),'combined source requires complete unit receipt')
            require(sha256(unit_path.read_bytes())==comparison['complete_unit_receipt_sha256'],'complete unit receipt changed')
            unit=json.loads(unit_path.read_text());unit_source=unit_path.parent/'unit.c'
            require(sha256(unit_source.read_bytes())==unit['combined_source_sha256']==proof['compiler']['source_sha256'],'combined source hash differs')
            require(unit['object_sha256']==proof['object_hash'] and unit['source_sha256']==proof['source_sha256'],'unit object/source identity differs')
            require(unit['verdict']=='EQUAL' and unit['unclaimed_bytes']==0,'unit is not completely proven')
            # A complete unit normally contains only closed function CODE.
            # It can also carry literal tails already proved for internal
            # canonical members.  Every such byte is revalidated below; no
            # other excess byte is permitted in the natural object.
            tails=unit.get('owned_code_tails')
            if tails is None:
                # Receipts predating internal-tail support could only own the
                # target's final tail.
                tail_size=owned_end-end if item['state']=='FUNCTION_WITH_DATA_MATCH' else 0
                tail_payloads={fid:tail} if tail_size else {}
            else:
                require(isinstance(tails,list),'unit owned CODE tails are malformed')
                tail_size=0;seen_tail_ids=set();tail_payloads={}
                for owned_tail in tails:
                    tail_id=owned_tail.get('id')
                    require(isinstance(tail_id,str) and tail_id not in seen_tail_ids,'duplicate unit owned CODE tail')
                    seen_tail_ids.add(tail_id)
                    tf=next((v for v in analysis.get('functions',[]) if v['id']==tail_id),None)
                    require(tf is not None and tf['hunk']==extent['hunk'],'unit owned CODE tail has unknown function')
                    tail_start,tail_end=owned_tail.get('start'),owned_tail.get('end')
                    strings=owned_tail.get('strings');padding=owned_tail.get('alignment_padding')
                    require(tail_start==tf['end'] and isinstance(tail_end,int) and isinstance(strings,list) and padding in (0,1),
                            'invalid unit owned CODE-data bounds')
                    literal=b''.join(s['text'].encode('ascii')+b'\0' for s in strings)
                    payload=literal+(b'\0' if padding else b'')
                    require(tail_end==tail_start+len(payload) and sha256(payload)==owned_tail.get('expected_tail_sha256'),
                            'unit owned CODE-data payload disagrees')
                    require(blob[h['content_offset']+tail_start:h['content_offset']+tail_end]==payload,
                            'unit owned CODE-data is not immutable game bytes')
                    mr=next((v for v in unit['members'] if v['id']==tail_id),None)
                    require(mr and all(mr.get('owned_code_data',{}).get(k)==v for k,v in owned_tail.items() if k!='id'),
                            'unit member tail proof differs')
                    tail_payloads[tail_id]=payload
                    tail_size+=len(payload)
                if item['state']=='FUNCTION_WITH_DATA_MATCH':
                    require(fid in seen_tail_ids,'unit omitted promoted target CODE-data tail')
            require(unit['actual_length']==unit['expected_length']+tail_size,
                    'unit has unproven bytes beyond its complete contribution')
            if item['state']=='FUNCTION_WITH_DATA_MATCH' and tails is None and tail_size:
                require(unit['ordered_members'][-1]['id']==fid,
                        'owned CODE-data target is not the final unit member')
            require(unit['expected_sha256']==unit['normalized_sha256'],'unit normalized bytes differ')
            require(any(m['id']==fid for m in unit['ordered_members']),'promoted function missing from unit')
            unit_raw=[];unit_compiled_raw=[]
            for m in unit['ordered_members']:
                mf=next((v for v in analysis.get('functions',[]) if v['id']==m['id']),None)
                require(mf and all(mf[k]==m[k] for k in ('hunk','start','end','size','sha256')),'unit member evidence changed')
                mr=next((v for v in unit['members'] if v['id']==m['id']),None)
                # The final owned-literal member carries its code comparison
                # beneath the distinct tail proof; ordinary members expose it
                # directly.  In either case only the closed function bytes
                # may equal the immutable function extent hash.
                normalized=mr.get('normalized_sha256') if mr else None
                if normalized is None and mr:
                    normalized=mr.get('code_comparison',{}).get('normalized_sha256')
                require(mr and mr['verdict']=='EQUAL' and normalized==m['sha256'],'unmatched member in unit')
                # The linker's CODE contribution places a member's compiler-
                # owned literal bundle immediately after that member, before
                # the following separately linked source object.  It is
                # immutable and already checked above, but must participate in
                # the complete-object hash in that physical order.
                member_raw=bytes.fromhex(mf['raw_bytes'])
                unit_raw.append(member_raw)
                unit_compiled_raw.append(member_raw+tail_payloads.get(m['id'],b''))
            body_hash=sha256(b''.join(unit_raw));compiled_hash=sha256(b''.join(unit_compiled_raw))
            # Older receipts name the closed function extents as their expected
            # bytes.  New receipts retain that stable coverage hash and add an
            # explicit complete-contribution hash for literal bundles.  Accept
            # the brief transitional format created before the latter field
            # existed, but still require it to be one of the two immutable
            # constructions rather than an arbitrary digest.
            require(unit['expected_sha256'] in (body_hash,compiled_hash),'complete unit original bytes disagree')
            if 'expected_compiled_sha256' in unit:
                # Address fields in the actual linked object are normalized
                # only by the member comparisons above.  The immutable
                # complete-contribution digest therefore proves the expected
                # code-plus-tail sequence, not raw link-time displacements.
                require(unit['expected_sha256']==body_hash and unit['expected_compiled_sha256']==compiled_hash,
                        'complete unit compiled bytes disagree')
            for dep,digest in unit['dependency_sources'].items():
                require(ledger['functions'].get(dep,{}).get('source_sha256')==digest,'unit dependency source changed')
        locations={(extent['hunk'],offset) for offset in range(start,owned_end)}
        require(not locations & occupied,'overlapping promoted source contributions');occupied.update(locations)
        out.append(dict(id=fid,node=h['node'],**extent,source=item['source'],proof=item['proof'],state=item['state']))
    return out
