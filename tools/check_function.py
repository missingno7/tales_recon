"""One-command exact candidate check. Compiler and emulator details stay behind this API."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from common import require,sha256,write_json,FormatError,json_bytes
from analysis_support import ROOT,game
from recovery_state import evidence,recovery,LEDGER,save_rank,write_recovery
from compiler_oracle import compile_many,PROFILES,identity
from recovery_transaction import ledger_lock
from function_compare import compare_function
from evidence_snapshot import scoped
from repo_paths import candidate_path,active_files


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


def regression_receipt():
    """Run the host-only regression suite once; no nested compilation or emulator launch."""
    def inputs():
        paths=sorted(list(active_files(ROOT/'tools','.py'))+list(active_files(ROOT/'tests','.py')))
        return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()) for p in paths}
    before=inputs()
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests'],cwd=ROOT,capture_output=True,text=True)
    require(tests.returncode==0,'promotion regression tests failed: '+tests.stdout+tests.stderr)
    require(inputs()==before,'regression suite inputs changed during execution; rerun verification')
    return dict(command='python -m unittest discover -s tests',passed=True,
                output_sha256=sha256((tests.stdout+tests.stderr).encode()),input_sha256=sha256(json_bytes(before)))


def promotion_proof(fid,source,report,compiled,f,state,regression):
    """Construct the existing individual proof without canonical writes."""
    source_hash=sha256(source.encode('ascii'))
    path=ROOT/'src/recovered'/f['node']/(fid+'.c')
    proof=dict(schema_version=1,id=fid,state=state,source=str(path.relative_to(ROOT)).replace('\\','/'),source_sha256=source_hash,
        evidence_extent={k:f[k] for k in ('hunk','start','end','size','sha256','extent_status')},
        compiler=compiled['identity'],object_hash=compiled['contribution']['object_sha256'],
        artifacts=compiled['artifacts'],cache_key=compiled['cache_key'],
        verifier_identity={p:sha256((ROOT/'tools'/p).read_bytes()) for p in ('check_function.py','function_compare.py','compiler_oracle.py','runtime_arithmetic.py')},
        comparison=report,relocation_proof=report['relocation_proof'],dependencies=f['direct_callees'],
        data_ownership=(report['owned_code_data'] if state=='FUNCTION_WITH_DATA_MATCH'
                        else 'External references only; no candidate-owned data or padding omitted'),
        compiler_selection='Matching candidate; historical release remains ambiguous',
        regression=regression)
    return proof


def durable_unit(report):
    """Promote only the re-derivable inputs of an accepted unit from scratch."""
    import shutil
    report=dict(report)
    if report.get('proposer'):
        proposal=dict(report['proposer'])
        source=(ROOT/proposal['receipt']).resolve()
        if source.is_relative_to(ROOT/'build/recovery/proposals'):
            require(sha256(source.read_bytes())==proposal['receipt_sha256'],'proposal receipt changed before retention')
            dest=ROOT/'recovery/proposals'/source.relative_to(ROOT/'build/recovery/proposals')
            dest.parent.mkdir(parents=True,exist_ok=True)
            require(not dest.exists() or dest.read_bytes()==source.read_bytes(),'durable proposal identity collision')
            if not dest.exists():shutil.copyfile(source,dest)
            proposal['receipt']=dest.relative_to(ROOT).as_posix();report['proposer']=proposal
    name=report.get('complete_unit_receipt')
    if not name:return report
    path=(ROOT/name).resolve()
    if not path.is_relative_to(ROOT/'build/recovery/units'):return report
    require(sha256(path.read_bytes())==report['complete_unit_receipt_sha256'],'unit receipt changed before retention')
    unit=json.loads(path.read_text());require(unit['verdict']=='EQUAL','only exact units can become durable')
    destination=ROOT/'recovery/units'/path.parent.relative_to(ROOT/'build/recovery/units')
    destination.mkdir(parents=True,exist_ok=True)
    inputs=[path,path.parent/'unit.c']
    if unit.get('object_groups'):
        inputs+=list((path.parent/'parts').glob('*.c'))
    for source in inputs:
        dest=destination/source.relative_to(path.parent);dest.parent.mkdir(parents=True,exist_ok=True)
        require(not dest.exists() or dest.read_bytes()==source.read_bytes(),'durable unit identity collision')
        if not dest.exists():shutil.copyfile(source,dest)
    return dict(report,complete_unit_receipt=(destination/'receipt.json').relative_to(ROOT).as_posix())


def promote(fid,source,report,compiled,f,state='FUNCTION_CODE_MATCH',replace_canonical=False,regression=None):
    """Write canonical source and proof.  ``regression`` lets a complete
    multi-member unit share one suite run taken before its first write."""
    for other,item in recovery()['functions'].items():
        e=item['evidence_extent']
        require(other==fid or e['hunk']!=f['hunk'] or e['end']<=f['start'] or e['start']>=f['end'],
                'promotion would overlap canonical source ownership: '+other)
    if regression is None:regression=regression_receipt()
    require(regression.get('passed') is True,'promotion requires a passing regression receipt')
    r=recovery();prior=r['functions'].get(fid)
    source_hash=sha256(source.encode('ascii'))
    require(not prior or prior['source_sha256']==source_hash or replace_canonical,
            'already promoted with another source; preserve canonical source')
    require(not prior or prior['state']!='FUNCTION_WITH_DATA_MATCH' or state=='FUNCTION_WITH_DATA_MATCH',
            'replacement may not discard an existing owned CODE-data proof')
    report=durable_unit(report)
    proof=promotion_proof(fid,source,report,compiled,f,state,regression)
    path=ROOT/proof['source']
    receipt_path=ROOT/'recovery/proofs'/(fid+'.json')
    with ledger_lock(LEDGER):
        r=recovery()
        prior=r['functions'].get(fid)
        require(not prior or prior['source_sha256']==source_hash or replace_canonical,
                'already promoted with another source; preserve canonical source')
        require(not prior or prior['state']!='FUNCTION_WITH_DATA_MATCH' or state=='FUNCTION_WITH_DATA_MATCH',
                'replacement may not discard an existing owned CODE-data proof')
        for other,item in r['functions'].items():
            e=item['evidence_extent']
            require(other==fid or e['hunk']!=f['hunk'] or e['end']<=f['start'] or e['start']>=f['end'],
                    'promotion would overlap canonical source ownership: '+other)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(source,encoding='ascii',newline='\n')
        write_json(receipt_path,proof)
        r['functions'][fid]={k:proof[k] for k in ('state','source','source_sha256','evidence_extent','compiler_selection')}
        r['functions'][fid]['proof']=receipt_path.relative_to(ROOT).as_posix()
        r['functions'][fid]['proof_sha256']=sha256(receipt_path.read_bytes())
        # The immutable blocker package remains historical evidence; it must no
        # longer appear as an active queue blocker once a verified source owns it.
        r['blockers'].pop(fid,None)
        write_recovery(r,LEDGER)
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


def isolated_output_root(output_dir):
    if output_dir is None:return None
    path=Path(output_dir).resolve();experiments=(ROOT/'experiments').resolve();build=(ROOT/'build').resolve()
    require(path.is_relative_to(experiments) or path.is_relative_to(build),
            'isolated output must be under experiments/ or build/')
    path.mkdir(parents=True,exist_ok=True)
    return path


@scoped
def check_many(requests,promote_equal=True,isolated=False,output_dir=None):
    if isolated:promote_equal=False
    output_root=isolated_output_root(output_dir) if isolated else None
    prepared=[];trials=[]
    for req in requests:
        f,l=validated_function(req['id']);source=candidate_path(ROOT,req['source']).read_text()
        # Opt-in: canonical unit members compile with their own proof's
        # profile (separate objects only; see check_unit.member_profile_plan).
        per_member=bool(req.get('per_member_profiles'))
        target_node=f['hunk']-2 if f.get('node')!='resident' and f.get('hunk',0)>=3 else 1
        source_hash=sha256(source.encode())
        if not isolated:
            retained=ROOT/'build/recovery/candidates'/f['id']/(source_hash+'.c')
            retained.parent.mkdir(parents=True,exist_ok=True);retained.write_text(source,encoding='utf-8',newline='\n')
        unit=None;unit_blocker=None;compile_source=source;objects=None;local_functions=()
        if any(c['basis']=='PC_RELATIVE' and c['hunk']==f['hunk'] and c['id']!=f['id']
               for c in f.get('direct_callees',[])):
            from check_unit import prepare_unit
            try:
                from check_unit import partitioned_objects,proven_unit_groups,grouped_objects,external_stand_in_source
                members,names,parts,combined,_=prepare_unit(
                    f['id'],source,True,allow_gaps=True,remove_stale_externs=False)
                groups,_=proven_unit_groups(members,{f['id']})
                objects=grouped_objects(members,names,parts,False,groups,with_members=per_member)
                local_functions=tuple(names[m['id']] for m in members if m['id']!=f['id'])
                compile_source,merged=external_stand_in_source(combined,local_functions,target_node)
                # Retain every original per-object declaration in unit.c;
                # only the shared harness input removes conflicting views.
                # The strict proof consumer re-derives that removal itself.
                unit=(members,names,combined,True,merged)
            except FormatError as exc:unit_blocker=str(exc)
            # A recovered dependency can sit across a real but still
            # unclaimed original gap.  Prove the compact source contribution
            # through normal separate objects, preserving only adjacent local
            # call pairs in one object for Manx BSR shortening.
            if unit is None and req.get('join_direct_callees',False):
                try:
                    from check_unit import gap_partitioned_objects
                    members,names,parts,compile_source,_=prepare_unit(
                        f['id'],source,True,allow_gaps=True,remove_stale_externs=False)
                    objects=gap_partitioned_objects(members,names,parts,with_members=per_member)
                    local_functions=tuple(names[m['id']] for m in members if m['id']!=f['id'])
                    unit=(members,names,compile_source,True)
                    unit_blocker=None
                except FormatError as gap_exc:unit_blocker=str(gap_exc)
        profiles=req.get('profiles',['aztec36'] if 'm.lib' in req.get('extra_libraries',()) else ['aztec36','aztec50-short'])
        for profile in profiles:
            require(profile in PROFILES,'unsupported compiler profile')
            try:
                # Validate the candidate source before batching.  The oracle
                # assigns stable object labels to the optional partition.
                extra_libraries=req.get('extra_libraries',())
                identity(compile_source,profile,target_node,extra_libraries=extra_libraries)
                trial=dict(source=compile_source,profile=profile,target_node=target_node,
                           objects=objects,local_functions=local_functions,extra_libraries=extra_libraries)
                if unit is not None:
                    from check_unit import unit_export_roots
                    roots=unit_export_roots(unit[0],unit[1],f['id'])
                    if roots is not None:trial['same_overlay_exports']=roots
                if per_member and unit is not None:
                    from check_unit import member_profile_plan,apply_member_profiles
                    plan,klass=member_profile_plan(unit[0],profile,{f['id']})
                    trial['profile_record']=apply_member_profiles(trial,plan,klass,
                                                                  single_object=[m['id'] for m in unit[0]])
                    if trial.get('object_profiles'):
                        from mixed_profile_oracle import mixed_identity
                        mixed_identity(trial)
                slot=len(trials);trials.append(trial)
            except FormatError as exc:
                slot=dict(status='SOURCE_REJECTED',identity=dict(profile=profile,flags=PROFILES[profile]['flags'],
                                                                  extra_libraries=list(req.get('extra_libraries',()))),
                          cache_key=sha256((source_hash+profile+str(exc)+repr(req.get('extra_libraries',()))).encode()),cache_hit=False,
                          guest_returncodes=[],directory=str(ROOT/'build/source-rejections'),error=str(exc))
            prepared.append((req,f,l,source,profile,slot,unit,unit_blocker))
    if any(t.get('object_profiles') for t in trials) and getattr(compile_many,'supports_object_profiles',False) is not True:
        import mixed_profile_oracle
        results=mixed_profile_oracle.compile_many(trials,base=compile_many)
    else:results=compile_many(trials)
    reports=[]
    for req,f,l,source,profile,slot,unit,unit_blocker in prepared:
        compiled=results[slot] if isinstance(slot,int) else slot
        if unit and compiled['status']=='COMPILED' and not req.get('owned_static_data'):
            from check_unit import retain_unit
            members,names,combined,*unit_options=unit
            _,report=retain_unit(f['id'],source,members,names,combined,compiled,l['a4']['bias'],
                                 owned_code_data=bool(req.get('owned_code_data')),
                                 allow_gaps=bool(unit_options and unit_options[0]),isolated=isolated,
                                 merged_externals=unit_options[1] if len(unit_options)>1 else None,
                                 profile_record=trials[slot].get('profile_record') if isinstance(slot,int) else None)
        elif req.get('owned_code_data'):
            from owned_code_data import compare_owned_code_data
            report=compare_owned_code_data(f,compiled,l['a4']['bias'])
        elif req.get('owned_static_data'):
            from owned_static_data import compare_owned_static_data
            report=compare_owned_static_data(f,compiled,l['a4']['bias'])
        else:report=compare_function(f,compiled,l['a4']['bias'])
        report['id']=f['id'];report['source_sha256']=sha256(source.encode())
        if unit_blocker:report['unit_blocker']=unit_blocker
        verification_files=('check_function.py','function_compare.py','check_unit.py','runtime_arithmetic.py','owned_code_data.py','owned_static_data.py')
        report['comparison_identity']=sha256(b''.join(Path(__file__).with_name(p).read_bytes() for p in verification_files))
        if req.get('proposer_receipt'):
            proposal_path=(ROOT/req['proposer_receipt']).resolve()
            require(proposal_path.is_relative_to(ROOT/'build/recovery/proposals'),'proposer receipt escapes ledger')
            proposal=json.loads(proposal_path.read_text())
            require(proposal['id']==f['id'] and proposal['source_sha256']==report['source_sha256'],'proposer source identity differs')
            report['proposer']=dict(receipt=req['proposer_receipt'],receipt_sha256=sha256(proposal_path.read_bytes()),model=proposal['identity']['model'])
        if report['verdict']=='BLOCKED' and compiled['status']!='COMPILED':
            logs=[dict(file='harness-validation',text=compiled['error'])] if compiled.get('error') else []
            for p in sorted(Path(compiled['directory']).glob('*.log')):
                text=p.read_text(errors='replace')
                if text:logs.append(dict(file=p.name,text=text[:1800]))
            report['compiler_feedback']=logs
        if isolated:
            if output_root is not None:
                base=output_root/f['id'];base.mkdir(parents=True,exist_ok=True)
                stem=report['source_sha256']+'-'+profile+'-'+report['cache_key'][:12]
                (base/(stem+'.c')).write_text(source,encoding='utf-8',newline='\n')
                write_json(base/(stem+'.json'),report)
        else:
            path=ROOT/'build/recovery/attempts'/f['id']/(report['source_sha256']+'-'+profile+'-'+report['cache_key'][:12]+'-'+report['comparison_identity'][:12]+'.json')
            write_json(path,report)
            with ledger_lock(LEDGER):
                r=recovery();attempts=r['attempts'].setdefault(f['id'],[])
                short=dict(source_sha256=report['source_sha256'],profile=profile,verdict=report['verdict'],receipt=path.relative_to(ROOT).as_posix(),
                           expected_length=report['expected_length'],actual_length=report['actual_length'],first_difference=report.get('normalized_first_difference'),mnemonic_similarity=report.get('mnemonic_similarity'))
                if report['verdict']=='EQUAL':
                    short['state']=report.get('proof_level','CODEGEN_SIMILAR')
                else:
                    short['state']='CODEGEN_SIMILAR' if (report.get('mnemonic_similarity') or 0)>=0.75 else 'CANDIDATE_C'
                short.update(cache_key=report['cache_key'],comparison_identity=report['comparison_identity'])
                if not any(a.get('cache_key')==short['cache_key'] and a.get('comparison_identity')==short['comparison_identity'] for a in attempts):attempts.append(short)
                write_recovery(r,LEDGER)
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
    if not isolated:save_rank()
    return reports


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('id',nargs='?');ap.add_argument('source',type=Path,nargs='?')
    ap.add_argument('--profile',action='append',choices=sorted(PROFILES))
    ap.add_argument('--batch',type=Path,help='JSON array of {id,source,profiles}; one boot for all cache misses')
    ap.add_argument('--owned-code-data',action='store_true',help='strictly verify an adjacent compiler-owned PC-relative string tail; promotes only at a proved next-entry boundary')
    ap.add_argument('--owned-static-data',action='store_true',help='strictly verify a manifest-declared initialized static DATA contribution; never promotes alone')
    ap.add_argument('--with-m-lib',action='store_true',help='link pinned Aztec 3.6a m.lib after c.lib (3.6a profiles only)')
    ap.add_argument('--isolated',action='store_true',help='run exact comparison without writing recovery candidates, receipts, proofs, ledger, or ranking')
    ap.add_argument('--output-dir',type=Path,help='with --isolated, save source and JSON reports under experiments/ or build/')
    ap.add_argument('--no-promote',action='store_true');ap.add_argument('--replace-canonical',action='store_true',
        help='replace an already promoted source only after this exact proof succeeds')
    ap.add_argument('--per-member-profiles',action='store_true',
        help='in a separate-object dependency unit, compile each canonical member with the profile of its own proof '
             '(only link-compatible profiles mix)')
    ap.add_argument('--json',action='store_true');args=ap.parse_args()
    require(args.output_dir is None or args.isolated,'--output-dir requires --isolated')
    req=json.loads(args.batch.read_text()) if args.batch else [dict(id=args.id,source=str(args.source),profiles=args.profile or (['aztec36'] if args.with_m_lib else ['aztec36','aztec50-short']),owned_code_data=args.owned_code_data,owned_static_data=args.owned_static_data,replace_canonical=args.replace_canonical,**({'per_member_profiles':True} if args.per_member_profiles else {}))]
    if args.with_m_lib:
        for item in req:
            profiles=item.setdefault('profiles',['aztec36'])
            require(all(p=='aztec36' for p in profiles),'--with-m-lib is pinned to the standard aztec36 profile; other variants are unverified')
            extras=list(item.get('extra_libraries',()))
            if 'm.lib' not in extras:extras.append('m.lib')
            item['extra_libraries']=extras
    reports=check_many(req,not args.no_promote,args.isolated,args.output_dir)
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
