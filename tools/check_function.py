"""One-command exact candidate check. Compiler and emulator details stay behind this API."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from common import require,sha256,write_json,FormatError
from analysis_support import ROOT,game
from recovery_state import evidence,recovery,LEDGER,save_rank
from compiler_oracle import compile_many,PROFILES,identity
from function_compare import compare_function


def validated_function(fid):
    ledger=evidence();blob,model,_=game()
    require(sha256(blob)==ledger['game_sha256'],'stale function ledger: game changed')
    require(all(sha256((ROOT/'tools'/p).read_bytes())==digest for p,digest in ledger['analysis_identity'].items()),
            'stale analysis implementation: run tools/function_census.py')
    f=next((f for f in ledger['functions'] if f['id']==fid),None)
    require(f is not None,'unknown function '+fid)
    h=next(h for h in model['hunks'] if h['number']==f['hunk'])
    raw=blob[h['content_offset']+f['start']:h['content_offset']+f['end']]
    require(raw.hex()==f['raw_bytes'] and sha256(raw)==f['sha256'],'function evidence bytes changed')
    require(f['size']==len(raw),'function extent inconsistent')
    if f['extent_status']=='CLOSED_CFG':
        # A closed CFG normally consists entirely of decoded instructions.
        # The census may also prove a bounded PC-relative switch table inside
        # the extent; that table is executable-control evidence but DATA, so
        # it must cover its exact bytes without pretending to be code.
        covered=[]
        for item in f['instructions']:
            covered.append((item['offset']-f['start'],item['offset']-f['start']+item['size'],'instruction'))
        for table in f.get('jump_tables',[]):
            covered.append((table['table_start']-f['start'],table['table_end']-f['start'],'proven jump table'))
        covered.sort()
        cursor=0
        for lo,hi,kind in covered:
            require(lo==cursor and hi>lo,'closed function has unaccounted or overlapping '+kind+' bytes')
            cursor=hi
        require(cursor==f['size'],'closed function has unaccounted bytes')
        require(not f['boundary_stops'] and not f['undecoded_gaps'] and f['return_sites'],'closed function evidence not complete')
    return f,ledger


def promote(fid,source,report,compiled,f,state='FUNCTION_CODE_MATCH',replace_canonical=False):
    for other,item in recovery()['functions'].items():
        e=item['evidence_extent']
        require(other==fid or e['hunk']!=f['hunk'] or e['end']<=f['start'] or e['start']>=f['end'],
                'promotion would overlap canonical source ownership: '+other)
    # Regression suite is host-only; no nested compilation or emulator launch.
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests'],cwd=ROOT,capture_output=True,text=True)
    require(tests.returncode==0,'promotion regression tests failed: '+tests.stdout+tests.stderr)
    r=recovery();prior=r['functions'].get(fid)
    source_hash=sha256(source.encode('ascii'))
    require(not prior or prior['source_sha256']==source_hash or replace_canonical,
            'already promoted with another source; preserve canonical source')
    require(not prior or prior['state']!='FUNCTION_WITH_DATA_MATCH' or state=='FUNCTION_WITH_DATA_MATCH',
            'replacement may not discard an existing owned CODE-data proof')
    path=ROOT/'src/recovered'/f['node']/(fid+'.c');path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(source,encoding='ascii',newline='\n')
    receipt_path=ROOT/'recovery/proofs'/(fid+'.json')
    proof=dict(schema_version=1,id=fid,state=state,source=str(path.relative_to(ROOT)).replace('\\','/'),source_sha256=source_hash,
        evidence_extent={k:f[k] for k in ('hunk','start','end','size','sha256','extent_status')},
        compiler=compiled['identity'],object_hash=compiled['contribution']['object_sha256'],
        artifacts=compiled['artifacts'],cache_key=compiled['cache_key'],
        verifier_identity={p:sha256((ROOT/'tools'/p).read_bytes()) for p in ('check_function.py','function_compare.py','compiler_oracle.py','runtime_arithmetic.py')},
        comparison=report,relocation_proof=report['relocation_proof'],dependencies=f['direct_callees'],
        data_ownership=(report['owned_code_data'] if state=='FUNCTION_WITH_DATA_MATCH'
                        else 'External references only; no candidate-owned data or padding omitted'),
        compiler_selection='Matching candidate; historical release remains ambiguous',
        regression=dict(command='python -m unittest discover -s tests',passed=True,output_sha256=sha256((tests.stdout+tests.stderr).encode())))
    write_json(receipt_path,proof)
    r['functions'][fid]={k:proof[k] for k in ('state','source','source_sha256','evidence_extent','compiler_selection')}
    r['functions'][fid]['proof']=receipt_path.relative_to(ROOT).as_posix()
    r['functions'][fid]['proof_sha256']=sha256(receipt_path.read_bytes())
    # The immutable blocker package remains historical evidence; it must no
    # longer appear as an active queue blocker once a verified source owns it.
    r['blockers'].pop(fid,None)
    write_json(LEDGER,r)
    return r['functions'][fid]


def owned_code_data_boundary(f,ledger,report):
    """Require a proven CODE-data tail to stop exactly at the next entry.

    An intermediate data match becomes canonical source ownership only when its
    separately claimed literal/padding extent ends where the next discovered
    candidate begins.  This prevents a source literal from silently claiming
    unrelated bytes between functions.
    """
    owned=report['owned_code_data'];end=owned['end']
    starts=sorted(other['start'] for other in ledger['functions']
                  if other['hunk']==f['hunk'] and other['start']>=f['end'] and other['id']!=f['id'])
    if starts:
        require(starts[0]==end,
                'owned CODE-data extent is not bounded by the next discovered function entry')
        return
    # A final function may own a literal tail at the physical end of a CODE
    # hunk. HUNK CODE payloads are longword-aligned, so permit only the
    # immutable zero bytes needed to serialize that final tail; never use this
    # exception to absorb arbitrary undiscovered bytes.
    blob,model,_=game()
    hunk=next((h for h in model['hunks'] if h['number']==f['hunk']),None)
    require(hunk is not None,'owned CODE-data hunk is absent from immutable game model')
    physical_end=hunk['initialized_size']
    padding=physical_end-end
    require(0<=padding<=3 and (end+padding)%4==0,
            'owned CODE-data extent is not bounded by a next entry or terminal HUNK alignment')
    actual=blob[hunk['content_offset']+end:hunk['content_offset']+physical_end]
    require(actual==b'\0'*padding,
            'terminal HUNK padding after owned CODE-data extent is not immutable zero fill')


def check_many(requests,promote_equal=True):
    prepared=[];trials=[]
    for req in requests:
        f,l=validated_function(req['id']);source=Path(req['source']).read_text()
        target_node=f['hunk']-2 if f.get('node')!='resident' and f.get('hunk',0)>=3 else 1
        source_hash=sha256(source.encode())
        retained=ROOT/'recovery/candidates'/f['id']/(source_hash+'.c')
        retained.parent.mkdir(parents=True,exist_ok=True);retained.write_text(source,encoding='utf-8',newline='\n')
        unit=None;unit_blocker=None;compile_source=source;objects=None;local_functions=()
        if any(c['basis']=='PC_RELATIVE' and c['hunk']==f['hunk'] and c['id']!=f['id']
               for c in f.get('direct_callees',[])):
            from check_unit import prepare_unit
            try:
                members,names,compile_source,_=prepare_unit(f['id'],source);unit=(members,names,compile_source)
            except FormatError as exc:unit_blocker=str(exc)
            # A recovered dependency can sit across a real but still
            # unclaimed original gap.  Prove the compact source contribution
            # through normal separate objects, preserving only adjacent local
            # call pairs in one object for Manx BSR shortening.
            if unit is None:
                try:
                    from check_unit import partitioned_objects
                    members,names,parts,compile_source,_=prepare_unit(
                        f['id'],source,True,allow_gaps=True,remove_stale_externs=False)
                    objects=partitioned_objects(members,names,parts,True)
                    local_functions=tuple(names[m['id']] for m in members if m['id']!=f['id'])
                    unit=(members,names,compile_source,True)
                    unit_blocker=None
                except FormatError as gap_exc:unit_blocker=str(gap_exc)
        profiles=req.get('profiles',['aztec36','aztec50-short'])
        for profile in profiles:
            require(profile in PROFILES,'unsupported compiler profile')
            try:
                # Validate the candidate source before batching.  The oracle
                # assigns stable object labels to the optional partition.
                identity(compile_source,profile,target_node)
                slot=len(trials);trials.append(dict(source=compile_source,profile=profile,target_node=target_node,
                                                    objects=objects,local_functions=local_functions))
            except FormatError as exc:
                slot=dict(status='SOURCE_REJECTED',identity=dict(profile=profile,flags=PROFILES[profile]['flags']),
                          cache_key=sha256((source_hash+profile+str(exc)).encode()),cache_hit=False,
                          guest_returncodes=[],directory=str(ROOT/'build/source-rejections'),error=str(exc))
            prepared.append((req,f,l,source,profile,slot,unit,unit_blocker))
    results=compile_many(trials);reports=[]
    for req,f,l,source,profile,slot,unit,unit_blocker in prepared:
        compiled=results[slot] if isinstance(slot,int) else slot
        if req.get('owned_code_data'):
            from owned_code_data import compare_owned_code_data
            report=compare_owned_code_data(f,compiled,l['a4']['bias'])
        elif req.get('owned_static_data'):
            from owned_static_data import compare_owned_static_data
            report=compare_owned_static_data(f,compiled,l['a4']['bias'])
        elif unit and compiled['status']=='COMPILED':
            from check_unit import retain_unit
            members,names,combined,*unit_options=unit
            _,report=retain_unit(f['id'],source,members,names,combined,compiled,l['a4']['bias'],
                                 allow_gaps=bool(unit_options and unit_options[0]))
        else:report=compare_function(f,compiled,l['a4']['bias'])
        report['id']=f['id'];report['source_sha256']=sha256(source.encode())
        if unit_blocker:report['unit_blocker']=unit_blocker
        verification_files=('check_function.py','function_compare.py','check_unit.py','runtime_arithmetic.py','owned_code_data.py','owned_static_data.py')
        report['comparison_identity']=sha256(b''.join(Path(__file__).with_name(p).read_bytes() for p in verification_files))
        if req.get('proposer_receipt'):
            proposal_path=(ROOT/req['proposer_receipt']).resolve()
            require(proposal_path.is_relative_to(ROOT/'recovery/proposals'),'proposer receipt escapes ledger')
            proposal=json.loads(proposal_path.read_text())
            require(proposal['id']==f['id'] and proposal['source_sha256']==report['source_sha256'],'proposer source identity differs')
            report['proposer']=dict(receipt=req['proposer_receipt'],receipt_sha256=sha256(proposal_path.read_bytes()),model=proposal['identity']['model'])
        if report['verdict']=='BLOCKED' and compiled['status']!='COMPILED':
            logs=[dict(file='harness-validation',text=compiled['error'])] if compiled.get('error') else []
            for p in sorted(Path(compiled['directory']).glob('*.log')):
                text=p.read_text(errors='replace')
                if text:logs.append(dict(file=p.name,text=text[:1800]))
            report['compiler_feedback']=logs
        path=ROOT/'recovery/attempts'/f['id']/(report['source_sha256']+'-'+profile+'-'+report['cache_key'][:12]+'-'+report['comparison_identity'][:12]+'.json')
        write_json(path,report)
        r=recovery();attempts=r['attempts'].setdefault(f['id'],[])
        short=dict(source_sha256=report['source_sha256'],profile=profile,verdict=report['verdict'],receipt=path.relative_to(ROOT).as_posix(),
                   expected_length=report['expected_length'],actual_length=report['actual_length'],first_difference=report.get('normalized_first_difference'),mnemonic_similarity=report.get('mnemonic_similarity'))
        if report['verdict']=='EQUAL':
            short['state']=report.get('proof_level','CODEGEN_SIMILAR')
        else:
            short['state']='CODEGEN_SIMILAR' if (report.get('mnemonic_similarity') or 0)>=0.75 else 'CANDIDATE_C'
        short.update(cache_key=report['cache_key'],comparison_identity=report['comparison_identity'])
        if not any(a.get('cache_key')==short['cache_key'] and a.get('comparison_identity')==short['comparison_identity'] for a in attempts):attempts.append(short)
        write_json(LEDGER,r)
        # Compiler-owned CODE data is promoted only when its independently
        # proved tail ends at the next discovered entry, so no unowned bytes
        # can be absorbed between the function and its natural literal bundle.
        proof_level=report.get('proof_level')
        if report['verdict']=='EQUAL' and proof_level in ('FUNCTION_CODE_MATCH','FUNCTION_WITH_DATA_MATCH') and promote_equal:
            if proof_level=='FUNCTION_WITH_DATA_MATCH':
                owned_code_data_boundary(f,l,report)
            canonical=recovery()['functions'].get(f['id'])
            if not canonical or canonical['source_sha256']==report['source_sha256'] or req.get('replace_canonical'):
                report['promotion']=promote(f['id'],source,report,compiled,f,proof_level,req.get('replace_canonical',False))
        reports.append(report)
    save_rank()
    return reports


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('id',nargs='?');ap.add_argument('source',type=Path,nargs='?')
    ap.add_argument('--profile',action='append',choices=sorted(PROFILES))
    ap.add_argument('--batch',type=Path,help='JSON array of {id,source,profiles}; one boot for all cache misses')
    ap.add_argument('--owned-code-data',action='store_true',help='strictly verify an adjacent compiler-owned PC-relative string tail; promotes only at a proved next-entry boundary')
    ap.add_argument('--owned-static-data',action='store_true',help='strictly verify a manifest-declared initialized static DATA contribution; never promotes alone')
    ap.add_argument('--no-promote',action='store_true');ap.add_argument('--replace-canonical',action='store_true',
        help='replace an already promoted source only after this exact proof succeeds')
    ap.add_argument('--json',action='store_true');args=ap.parse_args()
    req=json.loads(args.batch.read_text()) if args.batch else [dict(id=args.id,source=str(args.source),profiles=args.profile or ['aztec36','aztec50-short'],owned_code_data=args.owned_code_data,owned_static_data=args.owned_static_data,replace_canonical=args.replace_canonical)]
    reports=check_many(req,not args.no_promote)
    for r in reports:
        if args.json:print(json.dumps(r))
        else:
            diff=r.get('normalized_first_difference');where='none' if not diff else hex(diff['offset'])
            relocations=r.get('relocation_equal')
            print(f"{r['id']} {r['compiler']}: {r['verdict']} expected={r['expected_length']} actual={r['actual_length']} first_diff={where} relocations={relocations} cache_hit={r['cache_hit']}")
    return 0 if any(r['verdict']=='EQUAL' for r in reports) else 1

if __name__=='__main__':
    try:sys.exit(main())
    except (FormatError,OSError,ValueError) as e:print(json.dumps(dict(verdict='BLOCKED',reason=str(e))));sys.exit(2)
