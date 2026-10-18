"""Separate, serialized DATA-provider promotion; no function-state substitution."""
from names import read_source
import argparse
from contextlib import nullcontext
from evidence_snapshot import snapshot,isolated_verification,validated_stage,Snapshot
from pathlib import Path
from analysis_support import ROOT
from game_image import game
from common import require,sha256,json_bytes
from repo_paths import canonical_path,candidate_path,active_files
from recovery_evidence import load_promotions
from recovery_state import canonical_state
from recovery_transaction import ledger_lock,publish
from data_providers import document,source,verify,load_data_providers,producer_paths,contributions
from check_function import regression_receipt
from validation_memo import scoped, scope as memo_scope


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
        if fact.get('kind')=='EXTERNAL_DATA_POINTER_TABLE':
            from data_provider_sample_tables import evidence_paths
            names.update(evidence_paths(root,fact))
        elif fact.get('kind')=='EXTERNAL_DATA_POINTER_CELL':
            from data_provider_cells import evidence_paths
            names.update(evidence_paths(root,fact))
        elif fact.get('kind')=='EXTERNAL_CODE_POINTER_TABLE':
            from data_provider_pointers import evidence_paths
            names.update(evidence_paths(root,fact))
        elif fact.get('kind')=='BOUNDED_DATA_TABLE':
            from data_provider_tables import evidence_paths
            names.update(evidence_paths(root,fact))
        elif fact.get('kind')=='LITERAL_LINE_RECORDS':
            from data_provider_literals import evidence_paths
            names.update(evidence_paths(root,fact))
        else:
            for d in fact['definitions']:
                item=document(root,'recovery/ledger.json')['functions'][d['evidence']['function']]
                names.update([item['source'],item['proof']])
    names.update(p.relative_to(root).as_posix() for p in active_files(root/'tools','.py'))
    return dict(explicit=[dict(path=n,sha256=sha256((read_source(root, candidate_path(root, Path(root) / n) if n.startswith('build/') else canonical_path(root, n), scratch=True, names_root=None) if n.startswith('src/') else (candidate_path(root,Path(root)/n) if n.startswith('build/') else canonical_path(root,n)).read_bytes()))) for n in sorted(names)],closure=Snapshot().inputs(root,True))


# One validation scope: each producer job is audited once, not once per provider.
@scoped
def stage_entries(root,blob,model,analysis,ledger,promotions,path):
    rows=[];seen=set();facts=manifest_facts(root,path)
    recipe=document(root,facts[0][1]['producer']['batch'])
    require([n for n,f in facts]==[m['fact'] for m in recipe['members']],'manifest must select the complete producer batch')
    existing=load_data_providers(root,blob,model,analysis,ledger,promotions)
    occupied={(c['hunk'],p) for c in contributions(existing) for p in range(c['start'],c['end'])}
    for name,fact in facts:
        src=source(fact);original=canonical_path(root,fact['source'])
        require(not original.exists() or read_source(root, original, scratch=True, names_root=None)==src,'existing provider source differs')
        report=verify(root,blob,model,analysis,ledger,promotions,fact,src,None)
        points={(c['hunk'],p) for c in contributions([report]) for p in range(c['start'],c['end'])}
        require(not(points&seen),'overlapping batch providers');seen|=points
        require(fact['id'] not in ledger.get('data_providers',{}),'provider already admitted; replay it through census/accounting')
        require(not(points&occupied),'provider overlaps accepted DATA')
        rows.append(dict(fact_path=name,fact=fact,source_bytes=src,proof=dict(fact=fact,comparison=report)))
    # Existing accounting, including runtime and compiler-owned DATA, is another
    # overlap boundary. The committed accounting is used here; the promotion
    # gate's `hybrid_image.py --check` proves it current before anything is
    # published, so rebuilding it in-process would only repeat that check.
    accounting=document(root,'evidence/hybrid/accounting.json')
    for row in rows:
        for c in contributions([row['proof']['comparison']]):
            start,end=c['start'],c['end']
            covered=[r for r in accounting['ranges'] if r['hunk']==c['hunk'] and r['start']<end and start<r['end']]
            require(covered and all(r['category']=='RAW_ORACLE_DEBT' for r in covered),'DATA/literal provider overlaps already credited bytes')
    return rows


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',action='append',help='batch manifest; repeat to publish several under one gate')
    ap.add_argument('--verify-only',action='store_true')
    args=ap.parse_args();manifests=args.manifest or ['evidence/data-providers/batch.json']
    for path in manifests:canonical_path(ROOT,path)
    ledger_path=ROOT/'recovery/ledger.json'
    with (isolated_verification(ROOT) if args.verify_only else snapshot()), (nullcontext() if args.verify_only else ledger_lock(ledger_path)):
        before=sha256(ledger_path.read_bytes());ledger=document(ROOT,'recovery/ledger.json')
        # One validated stage: the input closure is hashed on entry and exit
        # instead of around every nested read (that cost hours per batch).
        with validated_stage(ROOT,True),validated_stage(ROOT,False):
            blob,model,_=game();analysis=document(ROOT,'evidence/functions/ledger.json')
            promotions=load_promotions(ROOT,blob,model,analysis)
            rows=[row for path in manifests for row in stage_entries(ROOT,blob,model,analysis,ledger,promotions,path)]
            # Each manifest is checked against the ledger; across manifests the new rows
            # must not overlap each other either.
            seen=set()
            for row in rows:
                points={(c['hunk'],p) for c in contributions([row['proof']['comparison']]) for p in range(c['start'],c['end'])}
                require(not(points&seen),'overlapping providers across manifests: '+row['fact']['id']);seen|=points
        if args.verify_only:
            print('EQUAL_CANDIDATE DATA providers='+str(len(rows))+' initialized_bytes='+str(sum(r['fact']['original']['size'] for r in rows)));return
        # The same host regression gate as every other promotion route, run here
        # under the ledger lock; never an operator-supplied log.
        def all_inputs():
            each=[validation_inputs(ROOT,path) for path in manifests]
            return each[0] if len(each)==1 else each
        inputs=all_inputs()
        regression=regression_receipt()
        require(regression.get('passed') is True,'promotion requires a passing regression receipt')
        require(all_inputs()==inputs,'validation inputs changed during regression; reverify the batch')
        regression=dict(regression,batch_members=[r['fact']['id'] for r in rows],batch_inputs_sha256=sha256(json_bytes(inputs)))
        artifacts={};updated=canonical_state(ledger)
        for row in rows:
            fact=row['fact'];proof_path='recovery/proofs/data/'+fact['id']+'.json';proof=json_bytes(dict(row['proof'],regression=regression))
            artifacts[ROOT/fact['source']]=row['source_bytes'];artifacts[ROOT/proof_path]=proof
            updated.setdefault('data_providers',{})[fact['id']]=dict(state='DATA_LAYOUT_MATCH',fact=row['fact_path'],source=fact['source'],
                source_sha256=sha256(row['source_bytes']),proof=proof_path,proof_sha256=sha256(proof))
        # Sources/proofs publish first; the ledger is the atomic final commit.
        publish(ROOT,ledger_path,artifacts,updated,before)
        # Re-prove the newly published entries from the canonical files; the
        # census refresh that follows re-validates the complete ledger.
        with validated_stage(ROOT,True),validated_stage(ROOT,False),memo_scope(ROOT):
            for row in rows:load_data_providers(ROOT,blob,model,analysis,updated,promotions,only=row['fact']['id'])
        print('Promoted '+str(len(rows))+' strict DATA providers; historical ownership/TU remain UNKNOWN.')


if __name__=='__main__':main()
