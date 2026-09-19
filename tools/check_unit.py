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


def prepare_unit(fid,source,with_parts=False):
    f,l=validated_function(fid);r=recovery();members={fid:f};parts={fid:source};names={fid:'recovered'}
    def add_recovered(dep_id):
        if dep_id in members:return
        dep=r['functions'].get(dep_id)
        require(dep is not None,'unrecovered same-node dependency: '+dep_id)
        df,_=validated_function(dep_id);text=(ROOT/dep['source']).read_text()
        require(sha256(text.encode())==dep['source_sha256'],'recovered dependency source changed')
        name='F_h%02d_%04X'%(df['hunk'],df['start']);names[dep_id]=name;members[dep_id]=df
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
    # A natural source unit can contain recovered routines that sit between a
    # caller and its local dependency without being directly called by either.
    # Include those bridges only when every intervening extent is already
    # canonical; the contiguity gate below still rejects any unowned byte.
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
    require(all(contribution_end(a)==b['start'] for a,b in zip(ordered,ordered[1:])),
            'unit has unowned gaps; do not fill or copy original bytes')
    # A bridge source may retain an old ``extern`` declaration for another
    # recovered member that now precedes it in this same translation unit.
    # Manx treats that later declaration as external linkage and can omit the
    # earlier definition from the linked symbol map.  Remove these stale
    # declarations from every unit member, not only the target candidate.
    for dep_id,name in names.items():
        if dep_id==fid:continue
        pattern=r'\bextern\s+(?:int|long|short|char|void)\s+'+re.escape(name)+r'\s*\(\s*\)\s*;'
        for part_id in parts:
            parts[part_id]=re.sub(pattern,'',parts[part_id])
    combined='\n'.join(parts[m['id']] for m in ordered)+'\n'
    return (ordered,names,parts,combined,l) if with_parts else (ordered,names,combined,l)


def compare_unit(members,names,compiled,a4_bias,owned_code_data=False):
    if compiled['status']!='COMPILED':return dict(verdict='BLOCKED',reason=compiled['status'],members=[])
    c=compiled['contribution'];raw=bytes.fromhex(c['code_hex']);expected=b''.join(bytes.fromhex(f['raw_bytes']) for f in members)
    result=dict(verdict='BLOCKED',expected_length=len(expected),actual_length=len(raw),members=[],object_sha256=c['object_sha256'])
    if c['data_size'] or c['bss_size']:
        result['reason']='UNIT_DATA_OWNERSHIP_UNPROVEN';return result
    ledger=recovery();tails={};tail_receipts=[]
    try:
        for f in members:
            tail,ownership=proven_tail(f,ledger)
            if owned_code_data and f is members[-1] and not tail:
                from owned_code_data import expected_string_tail
                tail,ownership=expected_string_tail(f)
            tails[f['id']]=tail
            if tail:tail_receipts.append(dict(id=f['id'],**ownership,expected_tail_sha256=sha256(tail)))
    except FormatError as exc:
        return dict(verdict='BLOCKED',reason='UNIT_OWNED_CODE_DATA_UNPROVEN: '+str(exc),members=[])
    expected_compiled_length=len(expected)+sum(len(t) for t in tails.values())
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
    for f in members:
        symbol=next((s for s in c['symbols'] if s['hunk']==c['hunk'] and s['name']=='_'+names[f['id']]),None)
        require(symbol is not None and symbol['offset']==cursor,'natural function ordering/extent differs; no slice accepted')
        stop=cursor+f['size'];piece=copy.deepcopy(compiled);pc=piece['contribution']
        owned_tail=tails[f['id']]
        pc.update(code_hex=raw[cursor:stop].hex()+owned_tail.hex(),code_size=f['size']+len(owned_tail),code_offset=original_base+cursor,entry_offset=0)
        pc['hunk']=original_hunk
        pc['symbols']=[dict(s,hunk=original_hunk,offset=s['offset']+original_base) if s['hunk']==source_hunk else dict(s)
                       for s in c['symbols']]
        pc['relocations']=[]
        for relocation in c['relocations']:
            at=relocation['relative_offset'];end=at+relocation['width']
            if end<=cursor or at>=stop:continue
            require(cursor<=at<end<=stop,'unit boundary splits a relocation')
            pc['relocations'].append(dict(relocation,relative_offset=at-cursor))
        if owned_tail:
            from owned_code_data import compare_owned_code_data
            report=compare_owned_code_data(f,piece,a4_bias)
        else:
            report=compare_function(f,piece,a4_bias)
        report['id']=f['id'];result['members'].append(report)
        cursor=stop+len(owned_tail)
    require(cursor==len(raw),'unclaimed code bytes in unit')
    equal=all(m['verdict']=='EQUAL' for m in result['members'])
    result.update(verdict='EQUAL' if equal else 'DIFFER',reason='ENTIRE_OBJECT_AND_ALL_MEMBER_CONTRIBUTIONS' if equal else 'MEMBER_DIFFERS',
                  expected_sha256=sha256(expected),actual_sha256=sha256(raw),
                  normalized_sha256=sha256(expected) if equal else None,unclaimed_bytes=0)
    return result


def retain_unit(fid,source,members,names,combined,compiled,a4_bias,owned_code_data=False):
    report=compare_unit(members,names,compiled,a4_bias,owned_code_data)
    report.update(id=fid,profile=compiled['identity']['profile'],cache_key=compiled['cache_key'],cache_hit=compiled['cache_hit'],
                      compiler=compiled['identity'],
                      combined_source_sha256=sha256(combined.encode()),source_sha256=sha256(source.encode()),
                      dependency_sources={f['id']:recovery()['functions'][f['id']]['source_sha256'] for f in members if f['id']!=fid},
                      ordered_members=[{k:f[k] for k in ('id','hunk','start','end','size','sha256')} for f in members],
                      verification_policy='Every byte and member of the complete naturally compiled object; no omitted padding or data')
    verifier_identity={p:sha256((ROOT/'tools'/p).read_bytes()) for p in ('check_unit.py','function_compare.py','compiler_oracle.py','runtime_arithmetic.py')}
    report['verifier_identity']=verifier_identity
    version=sha256(json_bytes(verifier_identity))[:16]
    base=ROOT/'recovery/units'/fid/compiled['cache_key']/version;base.mkdir(parents=True,exist_ok=True)
    (base/'unit.c').write_text(combined,encoding='ascii',newline='\n')
    (base/'candidate.c').write_text(source,encoding='ascii',newline='\n')
    persisted=copy.deepcopy(report);persisted.pop('cache_hit',None)
    for m in persisted['members']:m.pop('cache_hit',None)
    write_json(base/'receipt.json',persisted)
    target=next(f for f in members if f['id']==fid)
    comparison=next((m for m in report['members'] if m['id']==fid),None)
    if comparison is None:
        comparison=compare_function(target,compiled,a4_bias);comparison['actual_length']=None
    comparison=dict(comparison,id=fid,verdict=report['verdict'],reason=report['reason'],
                    source_sha256=report['source_sha256'],complete_unit_receipt=(base/'receipt.json').relative_to(ROOT).as_posix(),
                    complete_unit_receipt_sha256=sha256((base/'receipt.json').read_bytes()),
                    unit_feedback={k:report[k] for k in ('expected_length','actual_length','reason') if k in report})
    return report,comparison


def check(fid,path,profiles,promote_equal=True,owned_code_data=False,separate_objects=False):
    source=Path(path).read_text();members,names,parts,combined,ledger=prepare_unit(fid,source,True)
    reports=[]
    target,_=validated_function(fid)
    node=target['hunk']-2 if target['node']!='resident' else 1
    trials=[]
    for p in profiles:
        trial=dict(source=combined,profile=p,target_node=node)
        if separate_objects:
            # Preserve historical module boundaries when their ordinary link
            # codegen matters (for example JSR instead of an intra-object BSR).
            trial['objects']=[dict(source=parts[m['id']]) for m in members]
            trial['local_functions']=[names[m['id']] for m in members if m['id']!=fid]
        trials.append(trial)
    for compiled in compile_many(trials):
        report,comparison=retain_unit(fid,source,members,names,combined,compiled,ledger['a4']['bias'],owned_code_data)
        if report['verdict']=='EQUAL' and promote_equal:
            target=next(f for f in members if f['id']==fid);canonical=recovery()['functions'].get(fid)
            if owned_code_data:
                from check_function import owned_code_data_boundary
                owned_code_data_boundary(target,ledger,comparison)
                state='FUNCTION_WITH_DATA_MATCH'
            else:
                state='FUNCTION_CODE_MATCH'
            if not canonical or canonical['source_sha256']==report['source_sha256']:
                promote(fid,source,comparison,compiled,target,state=state)
        reports.append(report)
    save_rank();return reports


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('id');ap.add_argument('source',type=Path)
    ap.add_argument('--profile',action='append',choices=sorted(PROFILES));ap.add_argument('--no-promote',action='store_true')
    ap.add_argument('--owned-code-data',action='store_true',help='prove only the target function\'s adjacent PC-relative CODE string tail')
    ap.add_argument('--separate-objects',action='store_true',help='compile each proven unit member as an ordinary object before the normal overlay link')
    a=ap.parse_args()
    reports=check(a.id,a.source,a.profile or ['aztec36','aztec50-short'],not a.no_promote,a.owned_code_data,a.separate_objects)
    for r in reports:print(json.dumps(r))
    return 0 if any(r['verdict']=='EQUAL' for r in reports) else 1

if __name__=='__main__':
    try:sys.exit(main())
    except (FormatError,OSError,ValueError) as e:print(json.dumps(dict(verdict='BLOCKED',reason=str(e))));sys.exit(2)
