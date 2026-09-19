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


def prepare_unit(fid,source):
    f,l=validated_function(fid);r=recovery();members={fid:f};parts={fid:source};names={fid:'recovered'}
    for call in f['direct_callees']:
        if call['hunk']!=f['hunk'] or call['id']==fid:continue
        dep=r['functions'].get(call['id'])
        require(dep is not None,'unrecovered same-node dependency: '+call['id'])
        df,_=validated_function(call['id']);text=(ROOT/dep['source']).read_text()
        require(sha256(text.encode())==dep['source_sha256'],'recovered dependency source changed')
        name='F_h%02d_%04X'%(df['hunk'],df['start']);names[df['id']]=name;members[df['id']]=df
        parts[df['id']]=re.sub(r'\brecovered\b',name,text)
    ordered=sorted(members.values(),key=lambda x:x['start'])
    require(len(ordered)>1,'unit requires a recovered same-node dependency')
    require(all(a['end']==b['start'] for a,b in zip(ordered,ordered[1:])),'unit has unowned gaps; do not fill or copy original bytes')
    for dep_id,name in names.items():
        if dep_id!=fid:parts[fid]=re.sub(r'\bextern\s+(?:int|long|short|char|void)\s+'+re.escape(name)+r'\s*\(\s*\)\s*;','',parts[fid])
    combined='\n'.join(parts[m['id']] for m in ordered)+'\n'
    return ordered,names,combined,l


def compare_unit(members,names,compiled,a4_bias):
    if compiled['status']!='COMPILED':return dict(verdict='BLOCKED',reason=compiled['status'],members=[])
    c=compiled['contribution'];raw=bytes.fromhex(c['code_hex']);expected=b''.join(bytes.fromhex(f['raw_bytes']) for f in members)
    result=dict(verdict='BLOCKED',expected_length=len(expected),actual_length=len(raw),members=[],object_sha256=c['object_sha256'])
    if c['data_size'] or c['bss_size']:
        result['reason']='UNIT_DATA_OWNERSHIP_UNPROVEN';return result
    if len(raw)!=len(expected):
        result.update(verdict='DIFFER',reason='COMPLETE_UNIT_SIZE_DIFFERS');return result
    cursor=0
    for f in members:
        symbol=next((s for s in c['symbols'] if s['hunk']==c['hunk'] and s['name']=='_'+names[f['id']]),None)
        require(symbol is not None and symbol['offset']==cursor,'natural function ordering/extent differs; no slice accepted')
        stop=cursor+f['size'];piece=copy.deepcopy(compiled);pc=piece['contribution']
        pc.update(code_hex=raw[cursor:stop].hex(),code_size=f['size'],code_offset=cursor,entry_offset=0)
        pc['relocations']=[]
        for relocation in c['relocations']:
            at=relocation['relative_offset'];end=at+relocation['width']
            if end<=cursor or at>=stop:continue
            require(cursor<=at<end<=stop,'unit boundary splits a relocation')
            pc['relocations'].append(dict(relocation,relative_offset=at-cursor))
        report=compare_function(f,piece,a4_bias);report['id']=f['id'];result['members'].append(report)
        cursor=stop
    require(cursor==len(raw),'unclaimed code bytes in unit')
    equal=all(m['verdict']=='EQUAL' for m in result['members'])
    result.update(verdict='EQUAL' if equal else 'DIFFER',reason='ENTIRE_OBJECT_AND_ALL_MEMBER_CONTRIBUTIONS' if equal else 'MEMBER_DIFFERS',
                  expected_sha256=sha256(expected),actual_sha256=sha256(raw),
                  normalized_sha256=sha256(expected) if equal else None,unclaimed_bytes=0)
    return result


def retain_unit(fid,source,members,names,combined,compiled,a4_bias):
    report=compare_unit(members,names,compiled,a4_bias)
    report.update(id=fid,profile=compiled['identity']['profile'],cache_key=compiled['cache_key'],cache_hit=compiled['cache_hit'],
                      compiler=compiled['identity'],
                      combined_source_sha256=sha256(combined.encode()),source_sha256=sha256(source.encode()),
                      dependency_sources={f['id']:recovery()['functions'][f['id']]['source_sha256'] for f in members if f['id']!=fid},
                      ordered_members=[{k:f[k] for k in ('id','hunk','start','end','size','sha256')} for f in members],
                      verification_policy='Every byte and member of the complete naturally compiled object; no omitted padding or data')
    verifier_identity={p:sha256((ROOT/'tools'/p).read_bytes()) for p in ('check_unit.py','function_compare.py','compiler_oracle.py')}
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


def check(fid,path,profiles,promote_equal=True):
    source=Path(path).read_text();members,names,combined,ledger=prepare_unit(fid,source)
    reports=[]
    for compiled in compile_many([dict(source=combined,profile=p) for p in profiles]):
        report,comparison=retain_unit(fid,source,members,names,combined,compiled,ledger['a4']['bias'])
        if report['verdict']=='EQUAL' and promote_equal:
            target=next(f for f in members if f['id']==fid);canonical=recovery()['functions'].get(fid)
            if not canonical or canonical['source_sha256']==report['source_sha256']:promote(fid,source,comparison,compiled,target)
        reports.append(report)
    save_rank();return reports


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('id');ap.add_argument('source',type=Path)
    ap.add_argument('--profile',action='append',choices=sorted(PROFILES));ap.add_argument('--no-promote',action='store_true');a=ap.parse_args()
    reports=check(a.id,a.source,a.profile or ['aztec36','aztec50-short'],not a.no_promote)
    for r in reports:print(json.dumps(r))
    return 0 if any(r['verdict']=='EQUAL' for r in reports) else 1

if __name__=='__main__':
    try:sys.exit(main())
    except (FormatError,OSError,ValueError) as e:print(json.dumps(dict(verdict='BLOCKED',reason=str(e))));sys.exit(2)
