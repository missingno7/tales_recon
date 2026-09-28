"""Prove a caller plus adjacent recovered callees as one complete natural object.

No code fragment is accepted alone: every byte in the full compiled unit must
belong to a closed function extent and every member must pass exact comparison.
"""
import argparse
import copy
import json
from pathlib import Path
import re
import sys
from common import require,sha256,write_json,FormatError,json_bytes
from analysis_support import ROOT
from recovery_state import recovery,evidence,save_rank
from check_function import validated_function,promote
from compiler_oracle import compile_many,PROFILES
from function_compare import compare_function
from recovery_evidence import stand_in_source,EXTERN_FUNCTION


def stable_receipt(value):
    """Remove cache observations from a persisted proof, at every depth."""
    if isinstance(value,dict):
        return {k:stable_receipt(v) for k,v in value.items() if k!='cache_hit'}
    if isinstance(value,list):return [stable_receipt(v) for v in value]
    return value


def proven_tail(f,ledger):
    """Return a canonical member's separately proven adjacent CODE tail."""
    item=ledger['functions'].get(f['id'])
    if not item or item['state']!='FUNCTION_WITH_DATA_MATCH':return b'',None
    from owned_code_data import expected_string_tail
    tail,ownership=expected_string_tail(f)
    proof=json.loads((ROOT/item['proof']).read_text())
    claimed=proof.get('data_ownership',{})
    require(claimed.get('start')==ownership['start'] and claimed.get('end')==ownership['end'] and
            claimed.get('expected_tail_sha256')==sha256(tail),'canonical owned CODE-data proof changed')
    return tail,ownership


def mechanical_name(f):
    return 'F_h%02d_%04X'%(f['hunk'],f['start'])


def parse_interval(text):
    """``0xSTART..0xEND`` (hex, or decimal without ``0x``) -> (start, end)."""
    if isinstance(text,(tuple,list)):start,end=text
    else:
        lo,sep,hi=str(text).partition('..')
        require(sep=='..','natural interval must be START..END')
        try:start,end=int(lo.strip(),0),int(hi.strip(),0)
        except ValueError as exc:raise FormatError('natural interval bounds must be integers') from exc
    require(0<=start<end,'natural interval must satisfy 0 <= START < END')
    return start,end


# Displacement classes for the gap-dependence rule (68000 short BSR/Bcc.B
# carry a nonzero 8-bit displacement; d16(PC) and BSR/Bcc.W a 16-bit one).
BYTE_MIN,BYTE_MAX=-128,127
WORD_MIN,WORD_MAX=-32768,32767


def displacement_class(d):
    if BYTE_MIN<=d<=BYTE_MAX and d!=0:return 'BYTE'
    if WORD_MIN<=d<=WORD_MAX:return 'WORD'
    return 'OUT_OF_RANGE'


def natural_layout(members,interval,tails,new_ids,all_functions=()):
    """Pure description of a natural-interval link (no compilation).

    ``members`` are the linked functions in original address order and
    ``tails`` maps an id to the byte length of its proven literal tail.  The
    compact linked object places every member (plus that tail) back to back,
    so each run of original bytes absent between two consecutive members is a
    *compaction span*: an ``UNKNOWN_GAP`` when both neighbours lie inside the
    interval, else ``UNLINKED_OUTSIDE_INTERVAL`` (bytes of functions outside
    the claimed interval that are not needed by any member).  Nothing inside
    a span is claimed, filled or copied.
    """
    lo,hi=interval
    rows=[];spans=[];removed=0;previous=None;base=members[0]['start'] if members else lo
    for f in members:
        end=f['end']+tails.get(f['id'],0)
        if previous is not None:
            require(f['start']>=previous['contribution_end'],'natural layout members overlap: '+previous['id']+'/'+f['id'])
            if f['start']>previous['contribution_end']:
                a,b=previous['contribution_end'],f['start']
                inside=lo<=a and b<=hi
                spans.append(dict(start=a,end=b,size=b-a,after=previous['id'],before=f['id'],
                                  kind='UNKNOWN_GAP' if inside else 'UNLINKED_OUTSIDE_INTERVAL',
                                  ownership='UNKNOWN_NOT_ASSIGNED' if inside else 'NOT_LINKED_NOT_CLAIMED',
                                  object_offset=a-removed-base,
                                  discovered_functions_inside=[x['id'] for x in all_functions
                                                               if x.get('hunk')==f['hunk'] and a<=x['start']<b]))
                removed+=b-a
        role=('new' if f['id'] in new_ids else 'canonical')+('' if lo<=f['start'] and end<=hi else '_outside_interval')
        row=dict(id=f['id'],role=role,start=f['start'],end=f['end'],contribution_end=end,
                 tail_bytes=tails.get(f['id'],0),object_offset=f['start']-removed-base,shift=-removed)
        rows.append(row);previous=row
    # Interval bytes covered by no linked contribution, including its edges.
    unknown=[];cursor=lo
    for row in rows:
        if row['contribution_end']<=lo or row['start']>=hi:continue
        if row['start']>cursor:unknown.append(dict(start=cursor,end=row['start'],size=row['start']-cursor,ownership='UNKNOWN_NOT_ASSIGNED'))
        cursor=max(cursor,row['contribution_end'])
    if cursor<hi:unknown.append(dict(start=cursor,end=hi,size=hi-cursor,ownership='UNKNOWN_NOT_ASSIGNED'))
    return dict(interval=[lo,hi],interval_hex='0x%04X..0x%04X'%(lo,hi),members=rows,compaction_spans=spans,
                unknown_gaps=unknown,unknown_gap_bytes=sum(g['size'] for g in unknown),
                interval_members=[r['id'] for r in rows if not r['role'].endswith('_outside_interval')],
                outside_interval_members=[r['id'] for r in rows if r['role'].endswith('_outside_interval')])


def _pc_references(f):
    """Original PC-relative calls and data references of ``f`` (absolute hunk offsets)."""
    instructions={i.get('offset'):i for i in f.get('instructions') or []}
    for call in f.get('direct_callees') or []:
        if call.get('basis')!='PC_RELATIVE' or call.get('hunk')!=f['hunk']:continue
        ins=instructions.get(call['site'],{})
        yield dict(kind='CALL',site=call['site'],target=call['offset'],target_id=call.get('id'),
                   size=ins.get('size'),raw=str(ins.get('raw',''))[:4].lower() or None)
    for ref in f.get('referenced_data') or []:
        if ref.get('kind')!='PC_RELATIVE_DATA' or ref.get('hunk')!=f['hunk']:continue
        ins=instructions.get(ref['instruction_offset'],{})
        yield dict(kind='DATA',site=ref['instruction_offset'],target=ref['offset'],target_id=None,
                   size=ins.get('size'),raw=str(ins.get('raw',''))[:4].lower() or None)


def gap_crossings(members,layout):
    """Classify every original PC-relative reference that crosses a compaction span.

    Conservative rule: the natural link differs from the compact link only by
    the absent span bytes, so a reference is ``GAP_INDEPENDENT_ENCODING`` only
    when its original and compact displacements fall in the same displacement
    class (nonzero 8-bit, 16-bit).  Whatever rule (compiler, assembler or
    linker) selected the original form then sees the same class in both
    links, and the member comparison proves the reference by target identity.
    A crossing whose class changes (for example a 4-byte ``JSR d16(PC)`` whose
    compact distance would fit ``BSR.B``) is ``GAP_DEPENDENT_ENCODING``; a
    reference whose target lies inside an unlinked span is
    ``TARGET_IN_UNLINKED_SPAN``.  Both block the unit.
    """
    spans=layout['compaction_spans'];rows=[]
    shift={r['id']:r['shift'] for r in layout['members']}
    def removed_before(addr):
        return sum(s['size'] for s in spans if s['end']<=addr)
    for f in members:
        for ref in _pc_references(f):
            site,target=ref['site'],ref['target']
            lo,hi=sorted((site,target))
            crossed=[s for s in spans if lo<s['end'] and s['start']<hi]
            if not crossed:continue
            origin=site+2
            original=target-origin
            inside=next((s for s in crossed if s['start']<=target<s['end']),None)
            compact=(target-removed_before(target))-(origin+shift[f['id']])
            row=dict(member=f['id'],kind=ref['kind'],site=site,target=target,target_id=ref['target_id'],
                     instruction_size=ref['size'],opcode=ref['raw'],original_displacement=original,
                     compact_displacement=compact if inside is None else None,
                     distance_delta=(compact-original) if inside is None else None,
                     spans=[[s['start'],s['end'],s['kind']] for s in crossed])
            if inside is not None:
                row['classification']='TARGET_IN_UNLINKED_SPAN'
            else:
                row.update(original_class=displacement_class(original),compact_class=displacement_class(compact))
                same=row['original_class']==row['compact_class']!='OUT_OF_RANGE'
                row['classification']='GAP_INDEPENDENT_ENCODING' if same else 'GAP_DEPENDENT_ENCODING'
            rows.append(row)
    counts={}
    for r in rows:counts[r['classification']]=counts.get(r['classification'],0)+1
    return rows,counts


def natural_interval_plan(members,interval,new_ids,owned_code_data=False,target_id=None,all_functions=()):
    """Layout plus gap-crossing classification for a natural-interval unit."""
    ledger=recovery();tails={}
    for f in members:
        tail,_=proven_tail(f,ledger)
        if owned_code_data and f['id']==target_id and not tail:
            from owned_code_data import expected_string_tail
            tail,_=expected_string_tail(f)
        if tail:tails[f['id']]=len(tail)
    layout=natural_layout(members,interval,tails,new_ids,all_functions)
    crossings,counts=gap_crossings(members,layout)
    blocking=[c for c in crossings if c['classification']!='GAP_INDEPENDENT_ENCODING']
    layout.update(gap_crossings=crossings,gap_crossing_counts=counts,
                  gap_policy=('A PC-relative reference crossing a compaction span is compared by target identity only when '
                              'its original and compact displacement classes agree; otherwise the unit is BLOCKED '
                              '(GAP_DEPENDENT_ENCODING). No span byte is claimed.'),
                  blocked_reason=None if not blocking else
                  ('GAP_DEPENDENT_ENCODING' if any(c['classification']=='GAP_DEPENDENT_ENCODING' for c in blocking)
                   else 'TARGET_IN_UNLINKED_SPAN'))
    return layout


def prepare_unit(fid,source,with_parts=False,allow_gaps=False,remove_stale_externs=True,member_sources=None,natural_interval=None):
    """Build one complete unit around ``fid`` (compiled as ``recovered``).

    ``member_sources`` maps further *new* member ids to candidate source text.
    They join the unit exactly like canonical dependencies (renamed from
    ``recovered`` to their mechanical name), but need no prior proof: the unit
    is then accepted only as a whole, so a same-node call cycle whose members
    are all unproven can be verified in one normal compilation.  A reference
    to the entry's mechanical name inside a new member is bound to the entry's
    ``recovered`` definition, the only name it has in the compiled unit.
    """
    f,l=validated_function(fid);r=recovery();members={fid:f};parts={fid:source};names={fid:'recovered'}
    member_sources=dict(member_sources or {})
    require(fid not in member_sources,'the entry member source is the positional candidate, not a --member')
    entry_name=mechanical_name(f)
    def new_part(text):
        return re.sub(r'\b'+re.escape(entry_name)+r'\b','recovered',text)
    if member_sources:
        parts[fid]=new_part(source)
    def add_recovered(dep_id):
        if dep_id in members:return
        if dep_id in member_sources:
            df,_=validated_function(dep_id)
            require(df['hunk']==f['hunk'],'new unit member is outside the entry CODE hunk: '+dep_id)
            name=mechanical_name(df);names[dep_id]=name;members[dep_id]=df
            # A missing definition is rejected by the linked-symbol partition
            # check in compare_unit, never guessed from source text.
            parts[dep_id]=new_part(re.sub(r'\brecovered\b',name,member_sources[dep_id]))
            for call in df['direct_callees']:
                if call['hunk']==df['hunk'] and call['id']!=dep_id:
                    add_recovered(call['id'])
            return
        dep=r['functions'].get(dep_id)
        require(dep is not None,'unrecovered same-node dependency: '+dep_id)
        df,_=validated_function(dep_id);text=(ROOT/dep['source']).read_text()
        require(sha256(text.encode())==dep['source_sha256'],'recovered dependency source changed')
        name=mechanical_name(df);names[dep_id]=name;members[dep_id]=df
        parts[dep_id]=re.sub(r'\brecovered\b',name,text)
        # The routine's own local calls must stay in this translation unit as
        # well.  Leaving them as externs can preserve a plausible instruction
        # shape while changing the original PC-relative call identity.
        for call in df['direct_callees']:
            if call['hunk']==df['hunk'] and call['id']!=dep_id:
                add_recovered(call['id'])
    for call in f['direct_callees']:
        if call['hunk']!=f['hunk'] or call['id']==fid:continue
        add_recovered(call['id'])
    # Every named new member is part of the claimed unit, even one reached
    # only through a canonical bridge or by physical adjacency.
    for dep_id in member_sources:add_recovered(dep_id)
    if natural_interval is not None:
        # Natural interval: every discovered function of the claimed interval
        # is linked in original order, canonical ones from their exact
        # canonical sources and new ones from their candidate sources.  An
        # unrecovered function without a candidate source cannot be skipped.
        lo,hi=parse_interval(natural_interval)
        for m in members.values():
            if m['id']==fid or m['id'] in member_sources:
                require(lo<=m['start'] and m['end']<=hi,'new unit member is outside the natural interval: '+m['id'])
        for candidate in sorted(l['functions'],key=lambda x:x['start']):
            if candidate['hunk']!=f['hunk'] or candidate['end']<=lo or candidate['start']>=hi:continue
            require(lo<=candidate['start'] and candidate['end']<=hi,'natural interval splits function '+candidate['id'])
            if candidate['id'] in members:continue
            require(candidate['id'] in r['functions'],
                    'natural interval contains an unrecovered function without a member source: '+candidate['id'])
            add_recovered(candidate['id'])
    elif not allow_gaps:
        # A natural source unit can contain recovered routines that sit between
        # a caller and its local dependency without being directly called by
        # either. Include them only when every intervening extent is canonical.
        lo=min(x['start'] for x in members.values());hi=max(x['end'] for x in members.values())
        for candidate in l['functions']:
            if candidate['hunk']==f['hunk'] and lo<=candidate['start'] and candidate['end']<=hi:
                if candidate['id'] not in members: add_recovered(candidate['id'])
    ordered=sorted(members.values(),key=lambda x:x['start'])
    require(len(ordered)>1,'unit requires a recovered same-node dependency')
    # A canonical predecessor can own only its separately proved literal tail.
    # This permits source units to span that real compiler output, without
    # treating arbitrary bytes between recovered functions as source-owned.
    def contribution_end(member):
        tail,_=proven_tail(member,r);return member['end']+len(tail)
    if not allow_gaps and natural_interval is None:
        require(all(contribution_end(a)==b['start'] for a,b in zip(ordered,ordered[1:])),
                'unit has unowned gaps; do not fill or copy original bytes')
    # A bridge source may retain an old ``extern`` declaration for another
    # recovered member that now precedes it in this same translation unit.
    # Manx treats that later declaration as external linkage and can omit the
    # earlier definition from the linked symbol map.  Remove these stale
    # declarations from every unit member, not only the target candidate.
    if remove_stale_externs:
        for dep_id,name in names.items():
            # A new member's declaration of the entry now names ``recovered``;
            # it is the same stale external declaration in one object.
            if dep_id==fid and not member_sources:continue
            pattern=r'\bextern\s+(?:int|long|short|char|void)\s+'+re.escape(name)+r'\s*\(\s*\)\s*;'
            for part_id in parts:
                parts[part_id]=re.sub(pattern,'',parts[part_id])
    combined='\n'.join(parts[m['id']] for m in ordered)+'\n'
    return (ordered,names,parts,combined,l) if with_parts else (ordered,names,combined,l)


def compare_unit(members,names,compiled,a4_bias,owned_code_data=False,allow_gaps=False,source_text=None,natural=None):
    """Exact comparison of a complete linked unit.

    ``natural`` is a ``natural_interval_plan`` layout.  Members are then
    compared in compact linked coordinates (like ``allow_gaps``), and the unit
    verdict additionally requires every gap-crossing reference to be
    gap-independent; otherwise it is BLOCKED with the layout's reason.
    """
    if natural is None:
        return _compare_unit(members,names,compiled,a4_bias,owned_code_data,allow_gaps,source_text)
    result=_compare_unit(members,names,compiled,a4_bias,owned_code_data,True,source_text)
    new_ids={r['id'] for r in natural['members'] if r['role'].startswith('new')}
    result['canonical_regressions']=[dict(id=m['id'],verdict=m.get('verdict'),reason=m.get('reason'))
                                     for m in result.get('members',[]) if m['id'] not in new_ids]
    if natural.get('blocked_reason'):
        result['member_verdict']=result['verdict']
        result.update(verdict='BLOCKED',reason=natural['blocked_reason'],normalized_sha256=None)
    return result


def _compare_unit(members,names,compiled,a4_bias,owned_code_data=False,allow_gaps=False,source_text=None):
    if compiled['status']!='COMPILED':return dict(verdict='BLOCKED',reason=compiled['status'],members=[])
    c=compiled['contribution'];raw=bytes.fromhex(c['code_hex']);expected=b''.join(bytes.fromhex(f['raw_bytes']) for f in members)
    result=dict(verdict='BLOCKED',expected_length=len(expected),actual_length=len(raw),members=[],object_sha256=c['object_sha256'])
    if c['data_size'] or c['bss_size']:
        result['reason']='UNIT_DATA_OWNERSHIP_UNPROVEN';return result
    ledger=recovery();tails={};tail_receipts=[]
    try:
        target_id=next(fid for fid,name in names.items() if name=='recovered')
        for f in members:
            tail,ownership=proven_tail(f,ledger)
            # A source object's literal bundle is emitted directly after its
            # own function, even when a separately linked local callee follows
            # it in this compact proof.  The requested tail always belongs to
            # the target, not to whichever member happens to be last by
            # original address.
            if owned_code_data and f['id']==target_id and not tail:
                from owned_code_data import expected_string_tail
                tail,ownership=expected_string_tail(f)
            tails[f['id']]=tail
            if tail:tail_receipts.append(dict(id=f['id'],**ownership,expected_tail_sha256=sha256(tail)))
    except FormatError as exc:
        return dict(verdict='BLOCKED',reason='UNIT_OWNED_CODE_DATA_UNPROVEN: '+str(exc),members=[])
    expected_compiled=b''.join(bytes.fromhex(f['raw_bytes'])+tails[f['id']] for f in members)
    expected_compiled_length=len(expected_compiled)
    result['expected_compiled_length']=expected_compiled_length
    if tail_receipts:result['owned_code_tails']=tail_receipts
    if len(raw)!=expected_compiled_length:
        result.update(verdict='DIFFER',reason='COMPLETE_UNIT_SIZE_DIFFERS');return result
    cursor=0
    # The standalone oracle has only one emitted overlay CODE hunk.  Its
    # physical number is determined by the temporary link topology, while
    # every member in this closed, contiguous source unit belongs to one
    # original overlay hunk.  Map that one proven contribution hunk to the
    # original identity before proving PC-relative calls.  No other hunk or
    # symbol is remapped, and the symbol/partition checks below still require
    # exact ordered extents for the complete object.
    require(len({f['hunk'] for f in members})==1,'unit members cross original CODE hunks')
    source_hunk=c['hunk'];original_hunk=members[0]['hunk'];original_base=members[0]['start']
    # The entry member is linked as ``_recovered``.  Its identity is fixed by
    # the verifier's own naming (names[target_id]=='recovered') and its extent
    # by the ordered symbol partition below, so give that linked symbol its
    # mechanical identity too.  A call from another member back to the entry
    # (a same-node cycle) can then be proved like any other local call; a
    # call to any other offset still fails target_identity's exact-entry rule.
    target=next(f for f in members if f['id']==target_id)
    entry_alias='_'+mechanical_name(target)
    linked_entry=[s for s in c['symbols'] if s['hunk']==source_hunk and s['name']=='_recovered']
    symbols=list(c['symbols'])
    if len(linked_entry)==1 and not any(s['name']==entry_alias for s in symbols):
        symbols.append(dict(linked_entry[0],name=entry_alias))
    for f in members:
        symbol=next((s for s in c['symbols'] if s['hunk']==c['hunk'] and s['name']=='_'+names[f['id']]),None)
        require(symbol is not None and symbol['offset']==cursor,'natural function ordering/extent differs; no slice accepted')
        stop=cursor+f['size'];piece=copy.deepcopy(compiled);pc=piece['contribution']
        owned_tail=tails[f['id']]
        code_offset=cursor if allow_gaps else original_base+cursor
        pc.update(code_hex=raw[cursor:stop].hex()+owned_tail.hex(),code_size=f['size']+len(owned_tail),code_offset=code_offset,entry_offset=0)
        pc['hunk']=original_hunk
        pc['symbols']=[dict(s,hunk=original_hunk,offset=s['offset'] if allow_gaps else s['offset']+original_base) if s['hunk']==source_hunk else dict(s)
                       for s in symbols]
        pc['relocations']=[]
        for relocation in c['relocations']:
            at=relocation['relative_offset'];end=at+relocation['width']
            if end<=cursor or at>=stop:continue
            require(cursor<=at<end<=stop,'unit boundary splits a relocation')
            pc['relocations'].append(dict(relocation,relative_offset=at-cursor))
        if owned_tail:
            from owned_code_data import compare_owned_code_data
            report=compare_owned_code_data(f,piece,a4_bias,source_text)
        else:
            report=compare_function(f,piece,a4_bias,source_text=source_text)
        report['id']=f['id'];result['members'].append(report)
        cursor=stop+len(owned_tail)
    require(cursor==len(raw),'unclaimed code bytes in unit')
    equal=all(m['verdict']=='EQUAL' for m in result['members'])
    result.update(verdict='EQUAL' if equal else 'DIFFER',reason='ENTIRE_OBJECT_AND_ALL_MEMBER_CONTRIBUTIONS' if equal else 'MEMBER_DIFFERS',
                  # Keep the historical function-extent hash stable for
                  # generated coverage.  The explicit compiled hash includes
                  # any independently proved literal bundles in physical
                  # source-object order.
                  expected_sha256=sha256(expected),expected_compiled_sha256=sha256(expected_compiled),actual_sha256=sha256(raw),
                  normalized_sha256=sha256(expected) if equal else None,unclaimed_bytes=0)
    return result


def member_comparison(report,fid,source_sha256,base=None):
    """One member's promotion comparison, bound to the whole unit verdict."""
    comparison=next((m for m in report['members'] if m['id']==fid),None)
    require(comparison is not None,'unit member has no comparison: '+fid)
    comparison=dict(comparison,id=fid,verdict=report['verdict'],reason=report['reason'],
                    source_sha256=source_sha256,
                    unit_feedback={k:report[k] for k in ('expected_length','actual_length','reason') if k in report})
    if base is not None:
        comparison['complete_unit_receipt']=(base/'receipt.json').relative_to(ROOT).as_posix()
        comparison['complete_unit_receipt_sha256']=sha256((base/'receipt.json').read_bytes())
    return comparison


NATURAL_POLICY=('Every linked byte comes from a recovered or candidate source object; every function of the natural '
                'interval is linked in original address order (canonical members are regression checks); unknown gaps '
                'and unlinked outside spans remain unclaimed; gap-crossing PC-relative references are accepted only '
                'when their displacement class is gap-independent')


def retain_unit(fid,source,members,names,combined,compiled,a4_bias,owned_code_data=False,allow_gaps=False,isolated=False,member_sources=None,natural=None,merged_externals=None):
    report=compare_unit(members,names,compiled,a4_bias,owned_code_data,allow_gaps,combined,natural=natural)
    # Differing per-object views of one external share one harness stand-in.
    if merged_externals:report['merged_external_declarations']=merged_externals
    member_sources=dict(member_sources or {})
    new_ids={fid,*member_sources}
    report.update(id=fid,profile=compiled['identity']['profile'],cache_key=compiled['cache_key'],cache_hit=compiled['cache_hit'],
                      compiler=compiled['identity'],
                      combined_source_sha256=sha256(combined.encode()),source_sha256=sha256(source.encode()),
                      dependency_sources={f['id']:recovery()['functions'][f['id']]['source_sha256'] for f in members if f['id'] not in new_ids},
                      ordered_members=[{k:f[k] for k in ('id','hunk','start','end','size','sha256')} for f in members],
                      verification_policy=(NATURAL_POLICY if natural is not None else
                                           'Every byte and member of the complete naturally compiled object; no omitted padding or data'
                                           if not allow_gaps else
                                           'Every compact linked byte belongs to a recovered source object; original gaps remain unclaimed'))
    if natural is not None:report['natural_interval']=natural
    if member_sources:
        # Several members are proved together: all of them, or none, may
        # acquire canonical source from this receipt.
        report['member_sources']={f['id']:sha256((source if f['id']==fid else member_sources[f['id']]).encode())
                                  for f in members if f['id'] in new_ids}
        report['acceptance']='ALL_NEW_MEMBERS_EQUAL_IN_ONE_COMPLETE_UNIT'
    verifier_identity={p:sha256((ROOT/'tools'/p).read_bytes()) for p in ('check_unit.py','function_compare.py','compiler_oracle.py','runtime_arithmetic.py')}
    report['verifier_identity']=verifier_identity
    version=sha256(json_bytes(verifier_identity))[:16]
    base=None
    if not isolated:
        base=ROOT/'recovery/units'/fid/compiled['cache_key']/version;base.mkdir(parents=True,exist_ok=True)
        (base/'unit.c').write_text(combined,encoding='ascii',newline='\n')
        (base/'candidate.c').write_text(source,encoding='ascii',newline='\n')
        for member_id,text in member_sources.items():
            (base/'members').mkdir(exist_ok=True)
            (base/'members'/(member_id+'.c')).write_text(text,encoding='ascii',newline='\n')
        persisted=stable_receipt(report)
        write_json(base/'receipt.json',persisted)
    target=next(f for f in members if f['id']==fid)
    comparison=next((m for m in report['members'] if m['id']==fid),None)
    if comparison is None:
        comparison=compare_function(target,compiled,a4_bias);comparison['actual_length']=None
    comparison=dict(comparison,id=fid,verdict=report['verdict'],reason=report['reason'],
                    source_sha256=report['source_sha256'],
                    unit_feedback={k:report[k] for k in ('expected_length','actual_length','reason') if k in report})
    if base is not None:
        comparison['complete_unit_receipt']=(base/'receipt.json').relative_to(ROOT).as_posix()
        comparison['complete_unit_receipt_sha256']=sha256((base/'receipt.json').read_bytes())
    return report,comparison


def joined_source(parts,members):
    """Join source fragments while retaining one coherent record declaration.

    A historical C source unit may use one complete record declaration while
    separately recovered routines currently retain narrower views of it.  The
    first fragment supplies the declaration; later duplicate tags and extern
    globals are removed before Manx sees the one physical source object.
    """
    tags=set();globals=set();result=[]
    for member in members:
        text=parts[member['id']]
        for tag in list(tags):
            text=re.sub(r'\bstruct\s+'+re.escape(tag)+r'\s*\{[^{}]*\}\s*;\s*','',text)
        for name in list(globals):
            text=re.sub(r'\bextern\s+struct\s+\w+\s+'+re.escape(name)+r'\s*\[\s*[1-9]\d*\s*\]\s*;\s*','',text)
        tags.update(re.findall(r'\bstruct\s+(\w+)\s*\{[^{}]*\}\s*;',text))
        globals.update(re.findall(r'\bextern\s+struct\s+\w+\s+(\w+)\s*\[\s*[1-9]\d*\s*\]\s*;',text))
        result.append(text)
    return '\n'.join(result)


def partitioned_objects(members,names,parts,join_direct_callees=False):
    """Return ordinary source objects in original CODE order.

    With ``join_direct_callees``, only adjacent functions with a proven
    same-node direct edge share an object.  This is enough for Manx to retain
    its normal short local branches without claiming bytes across a gap.
    """
    if not join_direct_callees:return [dict(source=parts[m['id']]) for m in members]
    callees={m['id']:{c['id'] for c in m['direct_callees'] if c['hunk']==m['hunk']}
              for m in members}
    groups=[];current=[]
    for member in members:
        if current:
            previous=current[-1]
            contiguous=previous['end']==member['start']
            linked=(member['id'] in callees[previous['id']] or
                    previous['id'] in callees[member['id']])
            if not (contiguous and linked):groups.append(current);current=[]
        current.append(member)
    if current:groups.append(current)
    require(any(len(group)>1 for group in groups),
            'joined local source proof requires an adjacent direct-call pair')
    result=[]
    for group in groups:
        if len(group)==1:
            result.append(dict(source=parts[group[0]['id']]))
            continue
        text=joined_source(parts,group)
        # Declarations for definitions in this source object force external
        # linkage in Manx.  Calls to functions in other groups remain externs.
        for member in group:
            name=names[member['id']]
            pattern=r'\bextern\s+(?:int|long|short|char|void)\s+'+re.escape(name)+r'\s*\(\s*\)\s*;'
            text=re.sub(pattern,'',text)
        result.append(dict(source=text))
    return result


def proven_object_partition(receipt):
    """Ordinary source objects of an EQUAL unit receipt, as ordered member-id lists.

    A receipt compiled without an object partition was one object.  A
    partitioned receipt is read from its own hash-checked compile-cache
    artifacts: each object's assembler output names the functions it defines.
    Returns ``None`` when that evidence is unavailable.
    """
    ids=[x['id'] for x in receipt.get('ordered_members') or []]
    labels=(receipt.get('compiler') or {}).get('object_labels')
    if labels is None:return [ids]
    from compiler_oracle import cached
    compiled=cached(receipt.get('cache_key',''))
    if compiled is None or compiled.get('status')!='COMPILED' or compiled['identity'].get('object_labels')!=labels:return None
    by_symbol={'_'+('recovered' if x['id']==receipt['id'] else 'F_h%02d_%04X'%(x['hunk'],x['start'])):x['id']
               for x in receipt['ordered_members']}
    directory=Path(compiled['directory']);objects=[];placed=[]
    for label in labels:
        name=compiled['prefix'] if label=='candidate' else compiled['prefix']+'_'+label
        path=directory/(name+'.asm')
        if not path.is_file():return None
        defined=[by_symbol[n] for n in re.findall(r'^(_\w+):',path.read_text(errors='replace'),re.M) if n in by_symbol]
        objects.append(sorted(defined,key=ids.index));placed+=defined
    if sorted(placed)!=sorted(ids):return None
    return objects


def proven_unit_groups(members,new_ids,ledger=None):
    """Canonical member runs that were proved together in one natural object.

    Evidence comes only from a canonical member's own proof: its
    ``complete_unit_receipt`` (hash-checked, verdict EQUAL) and that receipt's
    ordinary object partition (``proven_object_partition``).  Every object of
    two or more members becomes a group here when all of its members are
    canonical in this unit, still have the proved source hashes, and are
    consecutive in this unit's address order (so no other linked function
    would have to enter that object).  Returns ``(groups, skipped)``;
    ``skipped`` lists receipts or objects not applied and why.
    """
    ledger=ledger or recovery();functions=ledger['functions']
    order=[m['id'] for m in members]
    groups=[];skipped=[];seen=set()
    for m in members:
        item=functions.get(m['id'])
        if m['id'] in new_ids or not item or not item.get('proof'):continue
        proof_path=ROOT/item['proof']
        if not proof_path.is_file():continue
        comparison=json.loads(proof_path.read_text()).get('comparison') or {}
        receipt_path=comparison.get('complete_unit_receipt')
        if not receipt_path or receipt_path in seen:continue
        seen.add(receipt_path)
        def skip(reason,ids=None):
            skipped.append(dict(receipt=receipt_path,reason=reason,**({'object':ids} if ids else {})))
        path=ROOT/receipt_path
        if not path.is_file() or sha256(path.read_bytes())!=comparison.get('complete_unit_receipt_sha256'):
            skip('RECEIPT_MISSING_OR_CHANGED');continue
        receipt=json.loads(path.read_text())
        if receipt.get('verdict')!='EQUAL' or len(receipt.get('ordered_members') or [])<2:continue
        partition=proven_object_partition(receipt)
        if partition is None:
            skip('PROVEN_OBJECT_PARTITION_UNAVAILABLE');continue
        proved={**receipt.get('dependency_sources',{}),receipt['id']:receipt.get('source_sha256')}
        for ids in partition:
            if len(ids)<2:continue
            if any(x not in order or x in new_ids for x in ids):
                skip('PROVEN_MEMBERS_NOT_ALL_CANONICAL_IN_UNIT',ids);continue
            if any((functions.get(x) or {}).get('source_sha256')!=proved.get(x) for x in ids):
                skip('PROVEN_SOURCE_CHANGED',ids);continue
            at=order.index(ids[0])
            if order[at:at+len(ids)]!=ids:
                skip('PROVEN_MEMBERS_NOT_CONSECUTIVE_HERE',ids);continue
            if ids not in groups:groups.append(ids)
    # Overlapping proven objects describe one source object here.
    merged=[]
    for ids in sorted(groups,key=lambda g:order.index(g[0])):
        if merged and order.index(ids[0])<=order.index(merged[-1][-1]):
            merged[-1]=merged[-1]+[x for x in ids if x not in merged[-1]]
        else:merged.append(list(ids))
    return merged,skipped


def grouped_objects(members,names,parts,join_direct_callees,proven_groups):
    """Ordinary objects in original order, keeping proven natural units together.

    Without ``proven_groups`` this is exactly the historical partition (one
    object per member, or ``partitioned_objects`` with joined callees).
    """
    if not proven_groups:
        return partitioned_objects(members,names,parts,True) if join_direct_callees else [dict(source=parts[m['id']]) for m in members]
    owner={}
    for index,ids in enumerate(proven_groups):
        for x in ids:owner[x]=('proven',index)
    callees={m['id']:{c['id'] for c in m['direct_callees'] if c['hunk']==m['hunk']} for m in members}
    groups=[];current=[]
    for member in members:
        if current:
            previous=current[-1]
            same=owner.get(member['id']) is not None and owner.get(member['id'])==owner.get(previous['id'])
            joined=(join_direct_callees and previous['end']==member['start'] and
                    (member['id'] in callees[previous['id']] or previous['id'] in callees[member['id']]))
            if not (same or joined):groups.append(current);current=[]
        current.append(member)
    if current:groups.append(current)
    result=[]
    for group in groups:
        if len(group)==1:
            result.append(dict(source=parts[group[0]['id']]));continue
        text=joined_source(parts,group)
        for member in group:
            pattern=r'\bextern\s+(?:int|long|short|char|void)\s+'+re.escape(names[member['id']])+r'\s*\(\s*\)\s*;'
            text=re.sub(pattern,'',text)
        result.append(dict(source=text))
    return result


def gap_partitioned_objects(members,names,parts):
    """Keep a gap proof in ordinary objects when no adjacent pair can join.

    Joining an adjacent direct caller and callee preserves Manx's short local
    call form where the original source object proves it.  A real source gap
    can instead leave every recovered member in its own ordinary object; that
    remains a complete linked proof and must not be rejected merely because
    there is no eligible pair to join.
    """
    try:
        return partitioned_objects(members,names,parts,True)
    except FormatError as exc:
        if str(exc)!='joined local source proof requires an adjacent direct-call pair':
            raise
        return partitioned_objects(members,names,parts,False)


def promote_unit_members(fid,source,member_sources,members,report,comparison,compiled,state):
    """Promote every new member of one EQUAL unit, or none of them.

    All preconditions are checked before the first canonical write, and the
    host regression suite runs once for the whole unit, so a failure cannot
    leave a cycle half-promoted.  Each member keeps its own authored source;
    all proofs name the same complete-unit receipt.
    """
    import check_function
    require(report['verdict']=='EQUAL' and all(m['verdict']=='EQUAL' for m in report['members']),
            'multi-member promotion requires every unit member EQUAL')
    require(comparison.get('complete_unit_receipt'),'multi-member promotion requires a retained unit receipt')
    sources={fid:source,**member_sources};by_id={f['id']:f for f in members}
    ledger=recovery()['functions'];plan=[]
    for member_id,text in sources.items():
        digest=sha256(text.encode('ascii'))
        require(report['member_sources'].get(member_id)==digest,'unit receipt does not name member source: '+member_id)
        canonical=ledger.get(member_id)
        require(not canonical or canonical['source_sha256']==digest,
                'already promoted with another source; preserve canonical source: '+member_id)
        f=by_id[member_id]
        for other,item in ledger.items():
            e=item['evidence_extent']
            require(other==member_id or e['hunk']!=f['hunk'] or e['end']<=f['start'] or e['start']>=f['end'],
                    'promotion would overlap canonical source ownership: '+other)
        member_report=comparison if member_id==fid else member_comparison(report,member_id,digest)
        member_report=dict(member_report,complete_unit_receipt=comparison['complete_unit_receipt'],
                           complete_unit_receipt_sha256=comparison['complete_unit_receipt_sha256'])
        plan.append((member_id,text,member_report,state if member_id==fid else 'FUNCTION_CODE_MATCH'))
    regression=check_function.regression_receipt()
    return [promote(member_id,text,member_report,compiled,by_id[member_id],state=member_state,regression=regression)
            for member_id,text,member_report,member_state in plan]


def external_stand_in_source(combined,local_functions,target_node):
    """Harness input defining each external stand-in exactly once.

    With separate objects, every member object keeps its own ``extern``
    declarations (``void F_h00_3674()`` in one, ``int F_h00_3674()`` in
    another).  The oracle harness defines one naturally allocated stand-in per
    distinct declaration, so differing views of one external identity would
    become duplicate definitions.  Keep only the first declaration of each such
    name for the harness input (``recovery_evidence.stand_in_source``, which
    also re-derives it from a retained ``unit.c``); member objects still
    compile their own declarations and the linker binds them to the one
    stand-in symbol.  Stand-ins are harness code and never claimed bytes.
    Without a conflicting declaration the combined source is returned
    unchanged, so every previously compiling unit keeps its cache identity.
    """
    from compiler_oracle import overlay_proxies
    skip=set(local_functions)|{p['name'] for p in overlay_proxies(combined,target_node)}
    return stand_in_source(combined,skip)


def unit_trials(fid,members,names,parts,combined,profiles,separate_objects,join_direct_callees,member_sources,proven_groups=()):
    """``proven_groups`` (natural-interval only) keeps canonical runs that
    were proved as one natural object in that one object."""
    target,_=validated_function(fid)
    node=target['hunk']-2 if target['node']!='resident' else 1
    trials=[]
    for p in profiles:
        trial=dict(source=combined,profile=p,target_node=node)
        if separate_objects:
            # Preserve historical module boundaries when their ordinary link
            # codegen matters (for example JSR instead of an intra-object BSR).
            trial['objects']=grouped_objects(members,names,parts,join_direct_callees,proven_groups)
            if proven_groups:trial['proven_object_groups']=[list(g) for g in proven_groups]
            trial['local_functions']=[names[m['id']] for m in members if m['id']!=fid]
            # A new member's extern for the entry is a real cross-object call
            # into this unit; the harness must not define a stand-in for it.
            # Added only when present, so ordinary unit cache keys are stable.
            if member_sources and re.search(r'\bextern\s+(?:int|long|short|char|void)\s+recovered\s*\(\s*\)\s*;',combined):
                trial['local_functions'].append('recovered')
            # Each object keeps its own declarations; the shared harness
            # defines every external stand-in once.
            trial['source'],merged=external_stand_in_source(combined,trial['local_functions'],node)
            if merged:trial['merged_external_declarations']=merged
        trials.append(trial)
    return trials


def stand_in_summary(trial):
    """Harness stand-in definitions of one trial: merged views and any duplicate name."""
    from compiler_oracle import harness
    text=harness(trial['source'],trial.get('target_node',1),trial.get('local_functions',()))
    defined=re.findall(r'^'+EXTERN_FUNCTION+r'\s*\{',text,re.M)
    counts={}
    for name in defined:counts[name]=counts.get(name,0)+1
    return dict(harness_function_stand_ins=len(defined),
                duplicate_stand_in_definitions=sorted(n for n,c in counts.items() if c>1),
                merged_external_declarations=trial.get('merged_external_declarations',{}))


def trial_cache_key(trial):
    """The compile-cache identity of one trial, computed without compiling."""
    from compiler_oracle import identity,object_specs,cached
    objects=object_specs(trial) if trial.get('objects') is not None else None
    key=identity(trial['source'],trial['profile'],trial.get('target_node',1),objects,trial.get('local_functions',()))[0]
    return key,cached(key) is not None


def check(fid,path,profiles,promote_equal=True,owned_code_data=False,separate_objects=False,allow_gaps=False,join_direct_callees=False,isolated=False,output_dir=None,member_sources=None,natural_interval=None,prepare_only=False):
    """Exact complete-unit check.  ``member_sources`` ({id: path}) adds new
    members authored with the entry; acceptance is then the complete unit.

    ``natural_interval`` (``START..END``) links every function of that
    interval in original order; ``prepare_only`` returns the planned unit
    (members, spacing, gap crossings, trial cache keys) without compiling."""
    if isolated or prepare_only:promote_equal=False
    require(not allow_gaps or separate_objects,'original-gap proof requires separate ordinary source objects')
    require(not join_direct_callees or separate_objects,'joined local source proof requires separate ordinary source objects')
    if natural_interval is not None:
        natural_interval=parse_interval(natural_interval)
        require(not allow_gaps,'--natural-interval replaces --allow-original-gaps; its gaps are listed and classified')
    output_root=None
    if isolated and output_dir is not None:
        from check_function import isolated_output_root
        output_root=isolated_output_root(output_dir)
    member_sources={k:Path(v).read_text() for k,v in (member_sources or {}).items()}
    source=Path(path).read_text();members,names,parts,combined,ledger=prepare_unit(
        fid,source,True,allow_gaps,remove_stale_externs=not separate_objects,member_sources=member_sources,
        natural_interval=natural_interval)
    natural=None
    if natural_interval is not None:
        natural=natural_interval_plan(members,natural_interval,{fid,*member_sources},owned_code_data,fid,ledger['functions'])
        # Like --allow-original-gaps, a compacted link keeps ordinary object
        # boundaries; one combined object is accepted only without spans,
        # where the natural interval is the ordinary contiguous unit.
        require(separate_objects or not natural['compaction_spans'],
                'natural-interval proof across compaction spans requires separate ordinary source objects')
    reports=[];proven_groups=[]
    if natural is not None and separate_objects:
        # Canonical members proved together as one natural object stay one
        # object; splitting them would change their proved local call forms.
        proven_groups,skipped=proven_unit_groups(members,{fid,*member_sources},ledger=recovery())
        natural['proven_object_groups']=proven_groups
        if skipped:natural['proven_object_groups_not_applied']=skipped
    trials=unit_trials(fid,members,names,parts,combined,profiles,separate_objects,join_direct_callees,member_sources,proven_groups)
    if prepare_only:
        keys=[trial_cache_key(t) for t in trials]
        plan=dict(verdict='PREPARED_NOT_COMPILED',id=fid,
                  ordered_members=[dict(id=m['id'],start=m['start'],end=m['end'],size=m['size'],
                                        role='new' if m['id']==fid or m['id'] in member_sources else 'canonical',
                                        linked_name=names[m['id']]) for m in members],
                  objects=len(trials[0].get('objects') or [None]) if trials else 0,
                  trials=[dict(profile=t['profile'],cache_key=k,cached=c,**stand_in_summary(t)) for t,(k,c) in zip(trials,keys)],
                  combined_source_sha256=sha256(combined.encode()))
        if natural is not None:plan['natural_interval']=natural
        return [plan]
    for trial,compiled in zip(trials,compile_many(trials)):
        report,comparison=retain_unit(fid,source,members,names,combined,compiled,ledger['a4']['bias'],owned_code_data,allow_gaps,isolated,
                                      member_sources=member_sources,natural=natural,
                                      merged_externals=trial.get('merged_external_declarations'))
        if report['verdict']=='EQUAL' and promote_equal:
            target=next(f for f in members if f['id']==fid);canonical=recovery()['functions'].get(fid)
            if owned_code_data:
                from check_function import owned_code_data_boundary
                owned_code_data_boundary(target,ledger,comparison)
                state='FUNCTION_WITH_DATA_MATCH'
            else:
                state='FUNCTION_CODE_MATCH'
            if member_sources:
                report['promotions']=promote_unit_members(fid,source,member_sources,members,report,comparison,compiled,state)
            elif not canonical or canonical['source_sha256']==report['source_sha256']:
                promote(fid,source,comparison,compiled,target,state=state)
        if isolated and output_root is not None:
            base=output_root/fid/(compiled['identity']['profile']+'-'+compiled['cache_key'][:12]);base.mkdir(parents=True,exist_ok=True)
            (base/'unit.c').write_text(combined,encoding='ascii',newline='\n')
            (base/'candidate.c').write_text(source,encoding='ascii',newline='\n')
            for member_id,text in member_sources.items():
                (base/'members').mkdir(exist_ok=True)
                (base/'members'/(member_id+'.c')).write_text(text,encoding='ascii',newline='\n')
            write_json(base/'receipt.json',stable_receipt(report))
        reports.append(report)
    if not isolated:save_rank()
    return reports


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('id');ap.add_argument('source',type=Path)
    ap.add_argument('--profile',action='append',choices=sorted(PROFILES));ap.add_argument('--no-promote',action='store_true')
    ap.add_argument('--owned-code-data',action='store_true',help='prove only the target function\'s adjacent PC-relative CODE string tail')
    ap.add_argument('--separate-objects',action='store_true',help='compile each proven unit member as an ordinary object before the normal overlay link')
    ap.add_argument('--allow-original-gaps',action='store_true',help='with separate objects, prove compact linked source ownership across known but unreconstructed original gaps')
    ap.add_argument('--join-direct-callees',action='store_true',help='compile the target and its following direct same-node callees as one ordinary source object')
    ap.add_argument('--isolated',action='store_true',help='run exact unit comparison without writing recovery units, proofs, ledger, or ranking')
    ap.add_argument('--output-dir',type=Path,help='with --isolated, save source and JSON reports under experiments/ or build/')
    ap.add_argument('--member',action='append',default=[],metavar='ID=SOURCE',
                    help='another new (not yet canonical) unit member and its source; repeat. The unit is accepted only if every member is EQUAL')
    ap.add_argument('--natural-interval',metavar='START..END',
                    help='link every function of this original interval in address order '
                         '(canonical sources are regression checks); unknown gaps stay unclaimed and gap-crossing '
                         'references are classified (GAP_DEPENDENT_ENCODING blocks the unit)')
    ap.add_argument('--prepare-only',action='store_true',help='print the planned unit, spacing, gap crossings and trial cache keys; never compile')
    a=ap.parse_args()
    require(a.output_dir is None or a.isolated,'--output-dir requires --isolated')
    member_sources={}
    for item in a.member:
        member_id,sep,member_path=item.partition('=')
        require(sep and member_id and member_path and member_id not in member_sources,'--member expects a unique ID=SOURCE')
        member_sources[member_id]=Path(member_path)
    reports=check(a.id,a.source,a.profile or ['aztec36','aztec50-short'],not a.no_promote,a.owned_code_data,a.separate_objects,a.allow_original_gaps,a.join_direct_callees,a.isolated,a.output_dir,member_sources,
                  a.natural_interval,a.prepare_only)
    for r in reports:print(json.dumps(r))
    if a.prepare_only:return 0
    return 0 if any(r['verdict']=='EQUAL' for r in reports) else 1

if __name__=='__main__':
    try:sys.exit(main())
    except (FormatError,OSError,ValueError) as e:print(json.dumps(dict(verdict='BLOCKED',reason=str(e))));sys.exit(2)
