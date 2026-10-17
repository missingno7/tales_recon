"""Serialized typed CODE-data promotion, behind the shared regression gate."""
import argparse,json
from contextlib import nullcontext
from common import require,sha256,json_bytes
from repo_paths import canonical_path
from recovery_transaction import ledger_lock,publish
from recovery_state import canonical_state
import code_data_providers as provider
import audio_score_measured as measured
import audio_region_provider as region
import audio_stateful_provider as stateful
import audio_h1_provider as h1
import audio_envelope_prefix as envelopes
from validation_memo import scoped


@scoped
def stage(root,blob,model,ledger,manifest=None):
    from evidence_snapshot import validated_stage
    # Hash the complete current input closure before AND after this read-only
    # stage. Nested canonical replays must not rehash the corpus per provider.
    with validated_stage(root,True),validated_stage(root,False):
        return _stage(root,blob,model,ledger,manifest)


def _stage(root,blob,model,ledger,manifest=None):
    backend=envelopes if manifest==envelopes.MANIFEST else h1 if manifest==h1.MANIFEST else stateful if manifest==stateful.MANIFEST else region if manifest==region.MANIFEST else measured
    require(manifest in (None,measured.MANIFEST,region.MANIFEST,stateful.MANIFEST,h1.MANIFEST,envelopes.MANIFEST),'unsupported CODE-data manifest')
    require(backend.IDENT not in ledger.get(provider.MAP,{}),'CODE-data already admitted; replay through census')
    fact=provider.document(root,backend.FACT);report=backend.verify(root,blob,model,fact)
    if backend in (h1,envelopes):
        # Same overlap boundary as promote_data: the shared publication gate
        # re-proves this committed accounting before any canonical write.
        accounting=provider.document(root,'evidence/hybrid/accounting.json')
    else:
        from hybrid_image import build
        _,accounting=build(root)
    for obj in report['objects']:
        for part in obj['parts']:
            a,z=part['original_start'],part['original_end']
            covered=[r for r in accounting['ranges'] if r['hunk']==obj['original']['hunk'] and r['start']<z and a<r['end']]
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
    args=ap.parse_args();require(args.manifest in (measured.MANIFEST,region.MANIFEST,stateful.MANIFEST,h1.MANIFEST,envelopes.MANIFEST),'unsupported CODE-data batch')
    backend=envelopes if args.manifest==envelopes.MANIFEST else h1 if args.manifest==h1.MANIFEST else stateful if args.manifest==stateful.MANIFEST else region if args.manifest==region.MANIFEST else measured
    from analysis_support import ROOT
    from game_image import game
    from evidence_snapshot import snapshot,Snapshot,isolated_verification
    from check_function import regression_receipt
    root=ROOT;path=root/'recovery/ledger.json'
    with (isolated_verification(root) if args.verify_only else snapshot()), (nullcontext() if args.verify_only else ledger_lock(path)):
        ledger=provider.document(root,'recovery/ledger.json');before=sha256(path.read_bytes());blob,model,_=game()
        if args.verify_only:
            fact,report=stage(root,blob,model,ledger,args.manifest)
            categories=dict(categories=report['credit_by_category']) if backend is h1 else dict(category=provider.CATEGORY)
            print(json.dumps(dict(verdict='EQUAL_CANDIDATE',**categories,bytes=report['typed_bytes'],objects=len(report['objects']),source_acceptance=False)))
            return
        fact,report,regression=gated(root,blob,model,ledger,regression_receipt,lambda:Snapshot().inputs(root,True),args.manifest)
        proof=json_bytes(dict(fact=fact,comparison=report,regression=regression))
        proof_path='recovery/proofs/code-data/'+backend.IDENT+'.json';updated=canonical_state(ledger);artifacts={};sources={}
        publish_objects=[dict(candidate=fact['candidate'],source=fact['source'],source_sha256=fact['source_sha256'])] if backend is h1 else fact['objects']
        for obj in publish_objects:
            raw=canonical_path(root,obj['candidate']).read_bytes();dest=canonical_path(root,obj['source'])
            require(sha256(raw)==obj['source_sha256'] and (not dest.exists() or dest.read_bytes()==raw),'CODE-data source destination differs')
            artifacts[dest]=raw;sources[obj['source']]=sha256(raw)
        dest=canonical_path(root,proof_path);require(not dest.exists() or dest.read_bytes()==proof,'CODE-data proof destination differs');artifacts[dest]=proof
        updated.setdefault(provider.MAP,{})[backend.IDENT]=dict(state=provider.STATE,fact=backend.FACT,sources=sources,proof=proof_path,proof_sha256=sha256(proof))
        publish(root,path,artifacts,updated,before)
        provider.rows(root,blob,model,provider.document(root,'evidence/functions/ledger.json'),updated)
        categories=dict(categories=report['credit_by_category']) if backend is h1 else dict(category=provider.CATEGORY)
        print(json.dumps(dict(verdict='PROMOTED',**categories,bytes=report['typed_bytes'],objects=len(report['objects']))))


if __name__=='__main__':main()
