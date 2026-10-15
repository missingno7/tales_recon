"""Serialized typed CODE-data promotion, behind the shared regression gate."""
import argparse,json
from common import require,sha256,json_bytes
from repo_paths import canonical_path
from recovery_transaction import ledger_lock,publish
from recovery_state import canonical_state
import code_data_providers as provider
import audio_score_measured as measured
import audio_region_provider as region
import audio_stateful_provider as stateful


def stage(root,blob,model,ledger,manifest=None):
    backend=stateful if manifest==stateful.MANIFEST else region if manifest==region.MANIFEST else measured
    require(manifest in (None,measured.MANIFEST,region.MANIFEST,stateful.MANIFEST),'unsupported CODE-data manifest')
    require(backend.IDENT not in ledger.get(provider.MAP,{}),'CODE-data already admitted; replay through census')
    fact=provider.document(root,backend.FACT);report=backend.verify(root,blob,model,fact)
    from hybrid_image import build
    _,accounting=build(root)
    for obj in report['objects']:
        for part in obj['parts']:
            a,z=part['original_start'],part['original_end']
            covered=[r for r in accounting['ranges'] if r['hunk']==0 and r['start']<z and a<r['end']]
            require(covered and all(r['category']=='RAW_ORACLE_DEBT' for r in covered),'CODE-data overlaps already credited bytes')
    return fact,report


def gated(root,blob,model,ledger,regression_receipt,inputs,manifest=None):
    """No publication until the shared gate AND unchanged exact replay pass."""
    stager=(lambda:stage(root,blob,model,ledger)) if manifest is None else (lambda:stage(root,blob,model,ledger,manifest))
    fact,report=stager();before=inputs()
    regression=regression_receipt()
    require(regression.get('passed') is True,'CODE-data promotion requires shared regression')
    require(inputs()==before,'CODE-data validation inputs changed during regression')
    require(stager()==(fact,report),'CODE-data exact replay changed after regression')
    return fact,report,regression


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',default=measured.MANIFEST)
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--verify-only',action='store_true');mode.add_argument('--promote',action='store_true')
    args=ap.parse_args();require(args.manifest in (measured.MANIFEST,region.MANIFEST,stateful.MANIFEST),'unsupported CODE-data batch')
    backend=stateful if args.manifest==stateful.MANIFEST else region if args.manifest==region.MANIFEST else measured
    from analysis_support import ROOT,game
    from evidence_snapshot import snapshot,Snapshot
    from check_function import regression_receipt
    root=ROOT;path=root/'recovery/ledger.json'
    with snapshot(),ledger_lock(path):
        ledger=provider.document(root,'recovery/ledger.json');before=sha256(path.read_bytes());blob,model,_=game()
        if args.verify_only:
            fact,report=stage(root,blob,model,ledger,args.manifest)
            print(json.dumps(dict(verdict='EQUAL_CANDIDATE',category=provider.CATEGORY,bytes=report['typed_bytes'],objects=len(report['objects']),source_acceptance=False)))
            return
        fact,report,regression=gated(root,blob,model,ledger,regression_receipt,lambda:Snapshot().inputs(root,True),args.manifest)
        proof=json_bytes(dict(fact=fact,comparison=report,regression=regression))
        proof_path='recovery/proofs/code-data/'+backend.IDENT+'.json';updated=canonical_state(ledger);artifacts={};sources={}
        for obj in fact['objects']:
            raw=canonical_path(root,obj['candidate']).read_bytes();dest=canonical_path(root,obj['source'])
            require(sha256(raw)==obj['source_sha256'] and (not dest.exists() or dest.read_bytes()==raw),'CODE-data source destination differs')
            artifacts[dest]=raw;sources[obj['source']]=sha256(raw)
        dest=canonical_path(root,proof_path);require(not dest.exists() or dest.read_bytes()==proof,'CODE-data proof destination differs');artifacts[dest]=proof
        updated.setdefault(provider.MAP,{})[backend.IDENT]=dict(state=provider.STATE,fact=backend.FACT,sources=sources,proof=proof_path,proof_sha256=sha256(proof))
        publish(root,path,artifacts,updated,before)
        provider.rows(root,blob,model,provider.document(root,'evidence/functions/ledger.json'),updated)
        print(json.dumps(dict(verdict='PROMOTED',category=provider.CATEGORY,bytes=report['typed_bytes'],objects=len(report['objects']))))


if __name__=='__main__':main()
