"""Validate curated source-proof inputs independently of generated topology metrics."""
import json
from common import require,sha256
from repo_paths import canonical_path


EXTERN_FUNCTION=r'(?:(?:unsigned|signed)\s+)?(?:int|long|short|char|void)\s+(\w+)\s*\(\s*\)'


def stand_in_source(combined,skip=()):
    """Harness input that declares every external stand-in once.

    Separate objects may declare one external differently (``void`` in one,
    ``int`` in another).  Later differing ``extern`` function declarations of
    a name are removed (names in ``skip``, i.e. unit members and overlay
    proxies, are never touched); identical repeats stay.  Returns the text
    and ``{name: {defined, merged}}``; without a conflict the text is
    ``combined`` itself.  Shared by the verifier and this evidence check, so
    a retained ``unit.c`` re-derives exactly what was compiled.
    """
    import re
    skip=set(skip);first={};drop=[];merged={}
    for m in re.finditer(r'\bextern\s+([^;{}]+);',combined):
        decl=m[1].strip();match=re.fullmatch(EXTERN_FUNCTION,decl)
        if match is None or match[1] in skip:continue
        name=match[1]
        if name not in first:first[name]=decl
        elif decl!=first[name]:
            drop.append(m.span());merged.setdefault(name,[first[name]]).append(decl)
    if not drop:return combined,{}
    pieces=[];cursor=0
    for a,b in drop:pieces.append(combined[cursor:a]);cursor=b
    pieces.append(combined[cursor:])
    return ''.join(pieces),{name:dict(defined=decls[0],merged=decls[1:]) for name,decls in sorted(merged.items())}


def joined_source(texts):
    """Join address-ordered source fragments into one physical source object.

    A historical C source unit may use one complete record declaration while
    separately recovered routines currently retain narrower views of it.  The
    first fragment supplies the declaration; later duplicate tags and extern
    globals are removed before Manx sees the one physical source object.
    """
    import re
    tags=set();globals=set();result=[]
    for text in texts:
        for tag in list(tags):
            text=re.sub(r'\bstruct\s+'+re.escape(tag)+r'\s*\{[^{}]*\}\s*;\s*','',text)
        for name in list(globals):
            text=re.sub(r'\bextern\s+struct\s+\w+\s+'+re.escape(name)+r'\s*\[\s*[1-9]\d*\s*\]\s*;\s*','',text)
        tags.update(re.findall(r'\bstruct\s+(\w+)\s*\{[^{}]*\}\s*;',text))
        globals.update(re.findall(r'\bextern\s+struct\s+\w+\s+(\w+)\s*\[\s*[1-9]\d*\s*\]\s*;',text))
        result.append(text)
    return '\n'.join(result)


def proven_object_source(texts,own_names):
    """One object of joined canonical members (``--join-direct-callees`` and
    proven natural groups): declarations of its own definitions are removed,
    since they would force external linkage in Manx."""
    import re
    text=joined_source(texts)
    for name in own_names:
        text=re.sub(r'\bextern\s+(?:int|long|short|char|void)\s+'+re.escape(name)+r'\s*\(\s*\)\s*;','',text)
    return text


def group_object_source(texts,own_names):
    """One ``--object-group`` translation-unit hypothesis.

    The address-ordered member sources are concatenated (``joined_source``);
    every ``extern`` function declaration of a member defined in this object
    is removed, and differing views of one external are kept once, as for the
    harness stand-ins (``stand_in_source``).  Returns ``(text, merged)``.
    """
    import re
    text=joined_source(texts)
    for name in own_names:
        text=re.sub(r'\bextern\s+'+EXTERN_FUNCTION.replace(r'(\w+)',re.escape(name))+r'\s*;','',text)
    return stand_in_source(text,own_names)


def object_partition_sources(unit,unit_text,parts_dir):
    """Re-derive every object source hash of an ``object_groups`` unit receipt.

    ``parts_dir`` holds each member's part as linked in that unit; together
    they must re-derive ``unit.c`` exactly, so every object source below is
    bound to the retained, hash-checked unit source.  Object groups must be
    whole partition objects of address-consecutive members with no original
    byte between them; a canonical member may join only a group that contains
    its whole proven object group.
    """
    ordered=unit['ordered_members'];ids=[m['id'] for m in ordered];by={m['id']:m for m in ordered}
    partition=unit.get('object_partition');groups=unit.get('object_groups')
    require(isinstance(partition,list) and all(isinstance(o,list) and o for o in partition) and
            [x for o in partition for x in o]==ids,'object partition is not the ordered unit')
    require(isinstance(groups,list) and groups and all(len(g)>1 and g in partition for g in groups),
            'object groups are not objects of the partition')
    parts={x:(parts_dir/(x+'.c')).read_bytes().decode('ascii') for x in ids}
    require('\n'.join(parts[x] for x in ids)+'\n'==unit_text,'unit member parts do not re-derive unit.c')
    tails={t['id']:t['end']-t['start'] for t in unit.get('owned_code_tails') or []}
    new=set(unit.get('member_sources') or ())|{unit['id']}
    proven=[list(g) for g in unit.get('proven_object_groups') or []]
    for g in groups:
        for a,b in zip(g,g[1:]):
            require(by[a]['end']+tails.get(a,0)==by[b]['start'],'object group spans original bytes it does not own: '+a+'/'+b)
        for x in g:
            require(x in new or any(x in p and set(p)<=set(g) for p in proven),
                    'canonical member joins an object group without agreeing proven grouping: '+x)
    names={m['id']:'recovered' if m['id']==unit['id'] else 'F_h%02d_%04X'%(m['hunk'],m['start']) for m in ordered}
    hashes=[]
    for o in partition:
        texts=[parts[x] for x in o];own=[names[x] for x in o]
        text=texts[0] if len(o)==1 else group_object_source(texts,own)[0] if o in groups else proven_object_source(texts,own)
        hashes.append(sha256(text.encode('ascii')))
    return hashes


def compiled_unit_source_sha256(unit,unit_text,compiler):
    """Hash of the source the oracle compiled for a retained complete unit.

    Ordinarily that is ``unit.c`` itself.  A separate-object unit whose
    receipt lists ``merged_external_declarations`` compiled the stand-in
    harness input re-derived here from ``unit.c``, the identity's local
    functions and overlay proxies; the receipt's merge list must match.
    """
    merged=unit.get('merged_external_declarations')
    if merged is None:return sha256(unit_text.encode('ascii'))
    skip=set(compiler.get('local_functions') or ())|{p['name'] for p in compiler.get('overlay_proxies') or ()}
    derived,actual=stand_in_source(unit_text,skip)
    require(merged and actual==merged,'merged external declarations do not re-derive from unit.c')
    return sha256(derived.encode('ascii'))


def member_profile_evidence(root,ledger,unit,compiler):
    """Re-derive and validate the per-member profiles of a complete unit receipt.

    Every unit member has one recorded profile.  A canonical dependency's
    profile must re-derive from its own hash-checked proof; a new member's is
    the link (requested) profile or a recorded ``member_profile_hypotheses``
    entry.  All profiles share one established ``profile_compat`` link class,
    every source object has one profile, and a per-object compile identity
    (``mixed_profile_oracle``) names exactly these object profiles and flags.
    Returns ``{member id: profile}``.
    """
    from profile_compat import link_class,proof_profile,PROFILE_FLAGS
    ids=[m['id'] for m in unit['ordered_members']];recorded=unit.get('member_profiles')
    require(unit.get('per_member_profiles') is True and isinstance(recorded,dict) and sorted(recorded)==sorted(ids),
            'per-member profiles do not name every unit member')
    link=compiler.get('profile')
    require(unit.get('link_profile')==link==unit.get('profile'),'per-member link profile differs from the compile identity')
    klass=link_class([link,*recorded.values()])
    require(unit.get('link_compatibility')==klass,'per-member link-compatibility class does not re-derive')
    partition=unit.get('object_profile_partition');object_profiles=unit.get('object_profiles')
    require(isinstance(partition,list) and all(isinstance(o,list) and o for o in partition) and
            [x for o in partition for x in o]==ids and isinstance(object_profiles,list) and len(object_profiles)==len(partition),
            'per-member object partition is not the ordered unit')
    for ids_in_object,profile in zip(partition,object_profiles):
        require(all(recorded[x]==profile for x in ids_in_object),'a source object mixes member profiles: '+','.join(ids_in_object))
    compiled=compiler.get('object_profiles')
    if compiled is None:
        require(unit.get('mixed_object_profiles') is False and all(p==link for p in object_profiles) and
                'member_profiles' not in compiler,'per-member profiles differ from a single-profile compile identity')
    else:
        labels=compiler.get('object_labels') or []
        require(unit.get('mixed_object_profiles') is True and compiler.get('member_profiles')==recorded and
                compiler.get('link_compatibility')==klass,'compiled member profiles differ from the unit receipt')
        require(isinstance(compiled,list) and [c.get('label') for c in compiled]==labels and
                [c.get('profile') for c in compiled]==object_profiles,'compiled object profiles do not re-derive from the partition')
        require(all(c.get('flags')==PROFILE_FLAGS.get(c.get('profile')) for c in compiled),
                'compiled object flags disagree with their profiles')
    new=set(unit.get('member_sources') or ())|{unit['id']}
    hypotheses=unit.get('member_profile_hypotheses') or {}
    require(isinstance(hypotheses,dict) and set(hypotheses)<=new-{unit['id']},'member profile hypotheses name no new member')
    for x in ids:
        if x in new:
            require(recorded[x]==hypotheses.get(x,link),'new member profile is neither requested nor a recorded hypothesis: '+x)
            continue
        item=ledger['functions'].get(x) or {}
        path=canonical_path(root,item['proof']) if item.get('proof') else None
        require(path is not None and path.is_relative_to(root.resolve()) and path.is_file() and
                sha256(path.read_bytes())==item.get('proof_sha256'),'canonical member proof missing or changed: '+x)
        require(proof_profile(json.loads(path.read_text()),x)==recorded[x],'canonical member profile differs from its own proof: '+x)
    return dict(recorded)


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
        source=canonical_path(root,item['source']);proof_path=canonical_path(root,item['proof'])
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
            unit_path=canonical_path(root,comparison.get('complete_unit_receipt',''))
            require(unit_path.is_relative_to(root.resolve()) and unit_path.is_file(),'combined source requires complete unit receipt')
            require(sha256(unit_path.read_bytes())==comparison['complete_unit_receipt_sha256'],'complete unit receipt changed')
            unit=json.loads(unit_path.read_text());unit_source=unit_path.parent/'unit.c'
            require(sha256(unit_source.read_bytes())==unit['combined_source_sha256'] and
                    compiled_unit_source_sha256(unit,unit_source.read_bytes().decode('ascii'),proof['compiler'])==proof['compiler']['source_sha256'],
                    'combined source hash differs')
            if unit.get('object_groups') is not None:
                # An --object-group unit compiled re-derivable object sources.
                derived=object_partition_sources(unit,unit_source.read_bytes().decode('ascii'),unit_path.parent/'parts')
                compiled_objects=proof['compiler'].get('partitioned_object_sources') or []
                require(derived==[o.get('source_sha256') for o in compiled_objects],
                        'object group sources do not re-derive from unit.c')
            if (unit.get('per_member_profiles') or proof['compiler'].get('object_profiles') is not None or
                    proof['compiler'].get('member_profiles') is not None):
                # Separately compiled objects with per-member profiles.
                member_profile_evidence(root,ledger,unit,proof['compiler'])
            # A multi-member unit names every new member's authored source.
            # Its receipt proves them together, so each must be canonical
            # with exactly that source (all members or none).
            member_sources=unit.get('member_sources')
            if member_sources is None:
                source_ok=unit['source_sha256']==proof['source_sha256']
            else:
                require(isinstance(member_sources,dict) and member_sources.get(unit['id'])==unit['source_sha256'],
                        'unit member sources are malformed')
                require(all(ledger['functions'].get(mid,{}).get('source_sha256')==digest for mid,digest in member_sources.items()),
                        'multi-member unit is not canonical for every new member')
                require(not set(member_sources)&set(unit['dependency_sources']) and
                        {m['id'] for m in unit['ordered_members']}==set(member_sources)|set(unit['dependency_sources']),
                        'unit members are not partitioned into new sources and canonical dependencies')
                source_ok=member_sources.get(fid)==proof['source_sha256']
            require(unit['object_sha256']==proof['object_hash'] and source_ok,'unit object/source identity differs')
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
