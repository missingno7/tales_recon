"""Serialized reconstructed-ASM batch promotion behind the shared regression gate."""
from names import read_source
import argparse,json,sys
from pathlib import Path
from common import require,sha256,json_bytes
from repo_paths import canonical_path
from recovery_transaction import ledger_lock,publish
from recovery_state import canonical_state
import reconstructed_asm as asm


def stage(root,blob,model,analysis,ledger,*,predicate=asm,manifest=None):
    asm=predicate
    batch=asm.document(root,asm.MANIFEST if manifest is None else manifest);rows=[]
    import audio_driver_asm as driver
    import audio_callback_asm as callback
    import audio_frameless_asm as frameless
    driver_style=predicate in (driver,callback,frameless)
    if driver_style:
        audit=asm.producer(root,batch);control=asm.control(root,batch,blob,model)
        if predicate is driver:
            required={'resident_asm_559E','resident_asm_59A4'}
            contract=asm.contracts.derive(blob,model,control['register_calibration'])
        elif predicate is callback:
            required={'resident_driver_58BC','resident_driver_5A50'}
            contract=asm.derive(blob,model,control['register_calibration'])
        else:
            required={'resident_driver_58BC','resident_driver_5A50','resident_callback_617C','resident_callback_61A0'}
            contract=asm.derive_batch(blob,model,control['frame_calibration'],root,batch)
        require(required<=set(ledger.get(asm.MAP,{})),'canonical prerequisites must precede ASM batch')
    for name in (batch['facts'] if predicate is frameless else asm.FACTS):
        fact=asm.document(root,name)
        report=(asm.verify(root,blob,model,fact,batch,contract,audit,control) if driver_style else
                asm.verify(root,blob,model,analysis,fact,batch))
        require(fact['id'] not in ledger.get(asm.MAP,{}),'ASM already admitted; replay through census')
        rows.append((name,fact,report))
    # All accepted classes, including runtime/DATA, must be RAW debt here.
    from hybrid_image import build
    _,accounting=build(root)
    for name,fact,report in rows:
        o=fact['original'];covered=[r for r in accounting['ranges'] if r['hunk']==o['hunk'] and r['start']<o['end'] and o['start']<r['end']]
        require(covered and all(r['category']=='RAW_ORACLE_DEBT' for r in covered),'ASM overlaps already credited bytes')
    return rows


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',default=asm.MANIFEST)
    mode=ap.add_mutually_exclusive_group(required=True);mode.add_argument('--verify-only',action='store_true');mode.add_argument('--promote',action='store_true');a=ap.parse_args()
    from analysis_support import ROOT
    from game_image import game
    from evidence_snapshot import snapshot,validated_stage,Snapshot
    from check_function import regression_receipt
    import audio_driver_asm as driver
    import audio_callback_asm as callback
    import audio_frameless_asm as frameless
    import glue_library_asm as glue
    predicates={p.MANIFEST:p for p in (asm,driver,callback,frameless,glue)}
    predicates[frameless.TAIL_MANIFEST]=frameless
    require(a.manifest in predicates,'unsupported batch manifest')
    predicate=predicates[a.manifest]
    root=ROOT;ledger_path=root/'recovery/ledger.json'
    with snapshot(),ledger_lock(ledger_path):
        ledger=predicate.document(root,'recovery/ledger.json');before=sha256(ledger_path.read_bytes())
        print('Replaying current canonical inputs...',file=sys.stderr,flush=True)
        # Validated stages hash the input closure on entry and exit instead of
        # around every nested read.
        with validated_stage(root,True),validated_stage(root,False):
            blob,model,_=game();analysis=predicate.document(root,'evidence/functions/ledger.json')
            print('Verifying complete ASM batch and existing accounting...',file=sys.stderr,flush=True)
            rows=stage(root,blob,model,analysis,ledger,predicate=predicate,manifest=a.manifest)
        if a.verify_only:
            print(json.dumps(dict(verdict='EQUAL_CANDIDATE',members=[f['id'] for n,f,r in rows],size=sum(f['original']['size'] for n,f,r in rows),source_acceptance=False)));return
        inputs=Snapshot().inputs(root,True)
        print('Running shared regression gate...',file=sys.stderr,flush=True)
        regression=regression_receipt()
        require(regression.get('passed') is True,'ASM promotion requires passing shared regression')
        require(Snapshot().inputs(root,True)==inputs,'ASM validation inputs changed during regression')
        print('Gate passed; rechecking unchanged inputs and exact batch...',file=sys.stderr,flush=True)
        with validated_stage(root,True),validated_stage(root,False):
            fresh=stage(root,blob,model,analysis,ledger,predicate=predicate,manifest=a.manifest)
        require(fresh==rows,'ASM replay changed after gate')
        artifacts={};updated=canonical_state(ledger)
        for name,fact,report in rows:
            proof=json_bytes(dict(fact=fact,comparison=report,regression=regression));source=canonical_path(root,fact['candidate']).read_bytes()
            proof_path='recovery/proofs/asm-reconstructed/'+fact['id']+'.json'
            for dest,raw in [(fact['source'],source),(proof_path,proof)]:
                p=canonical_path(root,dest);require(not p.exists() or (read_source(root, p) if dest.startswith('src/') else p.read_bytes())==raw,'ASM destination differs')
            updated.setdefault(predicate.MAP,{})[fact['id']]=dict(state='FUNCTION_CODE_MATCH',fact=name,source=fact['source'],source_sha256=sha256(source),proof=proof_path,proof_sha256=sha256(proof))
            artifacts[root/fact['source']]=source;artifacts[root/proof_path]=proof
        publish(root,ledger_path,artifacts,updated,before)
        with validated_stage(root,True),validated_stage(root,False):
            asm.rows(root,blob,model,analysis,updated)
        print(json.dumps(dict(verdict='PROMOTED',members=[f['id'] for n,f,r in rows],category='RECONSTRUCTED_ASM',bytes=sum(f['original']['size'] for n,f,r in rows))))


if __name__=='__main__':main()
