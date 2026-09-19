"""One-command exact candidate check. Compiler and emulator details stay behind this API."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from common import require,sha256,write_json,FormatError
from analysis_support import ROOT,game
from recovery_state import evidence,recovery,LEDGER,save_rank
from compiler_oracle import compile_many,PROFILES
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
        require(''.join(i['raw'] for i in f['instructions'])==f['raw_bytes'],'closed function has unaccounted bytes')
        require(not f['boundary_stops'] and not f['undecoded_gaps'] and f['return_sites'],'closed function evidence not complete')
    return f,ledger


def promote(fid,source,report,compiled,f):
    for other,item in recovery()['functions'].items():
        e=item['evidence_extent']
        require(other==fid or e['hunk']!=f['hunk'] or e['end']<=f['start'] or e['start']>=f['end'],
                'promotion would overlap canonical source ownership: '+other)
    # Regression suite is host-only; no nested compilation or emulator launch.
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests'],cwd=ROOT,capture_output=True,text=True)
    require(tests.returncode==0,'promotion regression tests failed: '+tests.stdout+tests.stderr)
    r=recovery();prior=r['functions'].get(fid)
    source_hash=sha256(source.encode('ascii'))
    require(not prior or prior['source_sha256']==source_hash,'already promoted with another source; preserve canonical source')
    path=ROOT/'src/recovered'/f['node']/(fid+'.c');path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(source,encoding='ascii',newline='\n')
    receipt_path=ROOT/'recovery/proofs'/(fid+'.json')
    proof=dict(schema_version=1,id=fid,state='FUNCTION_CODE_MATCH',source=str(path.relative_to(ROOT)).replace('\\','/'),source_sha256=source_hash,
        evidence_extent={k:f[k] for k in ('hunk','start','end','size','sha256','extent_status')},
        compiler=compiled['identity'],object_hash=compiled['contribution']['object_sha256'],
        artifacts=compiled['artifacts'],cache_key=compiled['cache_key'],
        verifier_identity={p:sha256((ROOT/'tools'/p).read_bytes()) for p in ('check_function.py','function_compare.py','compiler_oracle.py')},
        comparison=report,relocation_proof=report['relocation_proof'],dependencies=f['direct_callees'],
        data_ownership='External references only; no candidate-owned data or padding omitted',
        compiler_selection='Matching candidate; historical release remains ambiguous',
        regression=dict(command='python -m unittest discover -s tests',passed=True,output_sha256=sha256((tests.stdout+tests.stderr).encode())))
    write_json(receipt_path,proof)
    r['functions'][fid]={k:proof[k] for k in ('state','source','source_sha256','evidence_extent','compiler_selection')}
    r['functions'][fid]['proof']=receipt_path.relative_to(ROOT).as_posix()
    r['functions'][fid]['proof_sha256']=sha256(receipt_path.read_bytes());write_json(LEDGER,r)
    return r['functions'][fid]


def check_many(requests,promote_equal=True):
    prepared=[];trials=[]
    for req in requests:
        f,l=validated_function(req['id']);source=Path(req['source']).read_text()
        profiles=req.get('profiles',['aztec36','aztec50-short'])
        for profile in profiles:
            require(profile in PROFILES,'unsupported compiler profile')
            prepared.append((req,f,l,source,profile));trials.append(dict(source=source,profile=profile))
    results=compile_many(trials);reports=[]
    for (req,f,l,source,profile),compiled in zip(prepared,results):
        report=compare_function(f,compiled,l['a4']['bias']);report['id']=f['id'];report['source_sha256']=sha256(source.encode('ascii'))
        report['comparison_identity']=sha256(Path(__file__).with_name('function_compare.py').read_bytes())
        if report['verdict']=='BLOCKED' and compiled['status']!='COMPILED':
            logs=[]
            for p in sorted(Path(compiled['directory']).glob('*.log')):
                text=p.read_text(errors='replace')
                if text:logs.append(dict(file=p.name,text=text[:1800]))
            report['compiler_feedback']=logs
        path=ROOT/'recovery/attempts'/f['id']/(report['source_sha256']+'-'+profile+'-'+report['cache_key'][:12]+'-'+report['comparison_identity'][:12]+'.json')
        write_json(path,report)
        r=recovery();attempts=r['attempts'].setdefault(f['id'],[])
        short=dict(source_sha256=report['source_sha256'],profile=profile,verdict=report['verdict'],receipt=path.relative_to(ROOT).as_posix(),
                   expected_length=report['expected_length'],actual_length=report['actual_length'],first_difference=report.get('normalized_first_difference'),mnemonic_similarity=report.get('mnemonic_similarity'))
        short['state']='FUNCTION_CODE_MATCH' if report['verdict']=='EQUAL' else 'CODEGEN_SIMILAR' if (report.get('mnemonic_similarity') or 0)>=0.75 else 'CANDIDATE_C'
        short.update(cache_key=report['cache_key'],comparison_identity=report['comparison_identity'])
        if not any(a.get('cache_key')==short['cache_key'] and a.get('comparison_identity')==short['comparison_identity'] for a in attempts):attempts.append(short)
        write_json(LEDGER,r)
        if report['verdict']=='EQUAL' and promote_equal:
            canonical=recovery()['functions'].get(f['id'])
            if not canonical or canonical['source_sha256']==report['source_sha256']:
                report['promotion']=promote(f['id'],source,report,compiled,f)
        reports.append(report)
    save_rank()
    return reports


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('id',nargs='?');ap.add_argument('source',type=Path,nargs='?')
    ap.add_argument('--profile',action='append',choices=sorted(PROFILES))
    ap.add_argument('--batch',type=Path,help='JSON array of {id,source,profiles}; one boot for all cache misses')
    ap.add_argument('--no-promote',action='store_true');ap.add_argument('--json',action='store_true');args=ap.parse_args()
    req=json.loads(args.batch.read_text()) if args.batch else [dict(id=args.id,source=str(args.source),profiles=args.profile or ['aztec36','aztec50-short'])]
    reports=check_many(req,not args.no_promote)
    for r in reports:
        if args.json:print(json.dumps(r))
        else:
            diff=r.get('normalized_first_difference');where='none' if not diff else hex(diff['offset'])
            print(f"{r['id']} {r['compiler']}: {r['verdict']} expected={r['expected_length']} actual={r['actual_length']} first_diff={where} relocations={r['relocation_equal']} cache_hit={r['cache_hit']}")
    return 0 if any(r['verdict']=='EQUAL' for r in reports) else 1

if __name__=='__main__':
    try:sys.exit(main())
    except (FormatError,OSError,ValueError) as e:print(json.dumps(dict(verdict='BLOCKED',reason=str(e))));sys.exit(2)
