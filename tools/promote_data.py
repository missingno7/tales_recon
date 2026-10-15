"""Separate, serialized DATA-provider promotion; no function-state substitution."""
import argparse
from contextlib import nullcontext
from evidence_snapshot import snapshot,isolated_verification,Snapshot
from pathlib import Path
from analysis_support import ROOT,game
from common import require,sha256,json_bytes
from repo_paths import canonical_path,candidate_path,active_files
from recovery_evidence import load_promotions
from recovery_state import canonical_state
from recovery_transaction import ledger_lock,publish
from data_providers import document,source,verify,load_data_providers,producer_paths
from check_function import regression_receipt


def manifest_facts(root,path):
    manifest=document(root,path);require(manifest.get('schema_version')==1,'DATA batch schema')
    names=manifest['facts'];require(names and len(names)==len(set(names)),'empty/duplicate DATA facts')
    facts=[document(root,n) for n in names];require(len({f['producer']['batch'] for f in facts})==1,'one producer job per complete batch required');require(len({f['id'] for f in facts})==len(facts),'duplicate provider IDs')
    return list(zip(names,facts))


def validation_inputs(root,path):
    names={'recovery/ledger.json','evidence/functions/ledger.json','evidence/types.json',path}
    for name,fact in manifest_facts(root,path):
        names.add(name)
        batch=fact['producer']['batch'];names.add(batch)
        names.update(producer_paths(root,document(root,batch)))
        if fact.get('kind')=='EXTERNAL_CODE_POINTER_TABLE':
            from data_provider_pointers import evidence_paths
            names.update(evidence_paths(root,fact))
        else:
            for d in fact['definitions']:
                item=document(root,'recovery/ledger.json')['functions'][d['evidence']['function']]
                names.update([item['source'],item['proof']])
    names.update(p.relative_to(root).as_posix() for p in active_files(root/'tools','.py'))
    return dict(explicit=[dict(path=n,sha256=sha256((candidate_path(root,Path(root)/n) if n.startswith('build/worker-jobs/') else canonical_path(root,n)).read_bytes())) for n in sorted(names)],closure=Snapshot().inputs(root,True))


def stage_entries(root,blob,model,analysis,ledger,promotions,path):
    rows=[];seen=set();facts=manifest_facts(root,path)
    recipe=document(root,facts[0][1]['producer']['batch'])
    require([n for n,f in facts]==[m['fact'] for m in recipe['members']],'manifest must select the complete producer batch')
    existing=load_data_providers(root,blob,model,analysis,ledger,promotions)
    occupied={(r['original']['hunk'],p) for r in existing for p in range(r['original']['start'],r['original']['start']+r['original']['size'])}
    for name,fact in facts:
        src=source(fact);original=canonical_path(root,fact['source'])
        require(not original.exists() or original.read_bytes()==src,'existing provider source differs')
        report=verify(root,blob,model,analysis,ledger,promotions,fact,src,None)
        o=report['original'];points={(o['hunk'],p) for p in range(o['start'],o['start']+o['size'])}
        require(not(points&seen),'overlapping batch providers');seen|=points
        require(fact['id'] not in ledger.get('data_providers',{}),'provider already admitted; replay it through census/accounting')
        require(not(points&occupied),'provider overlaps accepted DATA')
        rows.append(dict(fact_path=name,fact=fact,source_bytes=src,proof=dict(fact=fact,comparison=report)))
    # Existing accounting, including runtime and compiler-owned DATA, is another
    # overlap boundary. Replaying it is deliberate at this promotion boundary.
    from hybrid_image import build
    _,accounting=build(root)
    for row in rows:
        o=row['proof']['comparison']['original'];start=o['start'];end=start+o['size']
        covered=[r for r in accounting['ranges'] if r['hunk']==o['hunk'] and r['start']<end and start<r['end']]
        require(covered and all(r['category']=='RAW_ORACLE_DEBT' for r in covered),'DATA provider overlaps already credited bytes')
    return rows


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',default='evidence/data-providers/batch.json')
    ap.add_argument('--verify-only',action='store_true')
    args=ap.parse_args();canonical_path(ROOT,args.manifest)
    ledger_path=ROOT/'recovery/ledger.json'
    with (isolated_verification(ROOT) if args.verify_only else snapshot()), (nullcontext() if args.verify_only else ledger_lock(ledger_path)):
        before=sha256(ledger_path.read_bytes());ledger=document(ROOT,'recovery/ledger.json')
        blob,model,_=game();analysis=document(ROOT,'evidence/functions/ledger.json')
        promotions=load_promotions(ROOT,blob,model,analysis)
        rows=stage_entries(ROOT,blob,model,analysis,ledger,promotions,args.manifest)
        if args.verify_only:
            print('EQUAL_CANDIDATE DATA providers='+str(len(rows))+' initialized_bytes='+str(sum(r['fact']['original']['size'] for r in rows)));return
        # The same host regression gate as every other promotion route, run here
        # under the ledger lock; never an operator-supplied log.
        inputs=validation_inputs(ROOT,args.manifest)
        regression=regression_receipt()
        require(regression.get('passed') is True,'promotion requires a passing regression receipt')
        require(validation_inputs(ROOT,args.manifest)==inputs,'validation inputs changed during regression; reverify the batch')
        regression=dict(regression,batch_members=[r['fact']['id'] for r in rows],batch_inputs_sha256=sha256(json_bytes(inputs)))
        artifacts={};updated=canonical_state(ledger)
        for row in rows:
            fact=row['fact'];proof_path='recovery/proofs/data/'+fact['id']+'.json';proof=json_bytes(dict(row['proof'],regression=regression))
            artifacts[ROOT/fact['source']]=row['source_bytes'];artifacts[ROOT/proof_path]=proof
            updated.setdefault('data_providers',{})[fact['id']]=dict(state='DATA_LAYOUT_MATCH',fact=row['fact_path'],source=fact['source'],
                source_sha256=sha256(row['source_bytes']),proof=proof_path,proof_sha256=sha256(proof))
        # Sources/proofs publish first; the ledger is the atomic final commit.
        publish(ROOT,ledger_path,artifacts,updated,before)
        load_data_providers(ROOT,blob,model,analysis,updated,promotions)
        print('Promoted '+str(len(rows))+' strict DATA providers; historical ownership/TU remain UNKNOWN.')


if __name__=='__main__':main()
