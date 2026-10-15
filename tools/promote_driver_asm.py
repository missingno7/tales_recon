"""Promote the separate audio driver batch through the shared regression gate."""
import argparse,json,sys
from common import require,sha256,json_bytes
from repo_paths import canonical_path
from recovery_state import canonical_state
from recovery_transaction import ledger_lock,publish
import audio_driver_asm as asm


def stage(root,blob,model,analysis,ledger):
 batch=asm.document(root,asm.MANIFEST);audit=asm.producer(root,batch);control=asm.control(root,batch,blob,model);contract=asm.contracts.derive(blob,model,control['register_calibration']);rows=[]
 require({'resident_asm_559E','resident_asm_59A4'}<=set(ledger.get(asm.MAP,{})),'first batch must be canonically admitted before batch0002')
 for name in asm.FACTS:
  fact=asm.document(root,name);require(fact['id'] not in ledger.get(asm.MAP,{}),'driver already admitted; use canonical census replay')
  report=asm.verify(root,blob,model,fact,batch,contract,audit,control);rows.append((name,fact,report))
 from hybrid_image import build
 _,accounting=build(root)
 for name,fact,report in rows:
  o=fact['original'];covered=[r for r in accounting['ranges'] if r['hunk']==0 and r['start']<o['end'] and o['start']<r['end']]
  require(covered and all(r['category']=='RAW_ORACLE_DEBT' for r in covered),'driver span overlaps an already credited category')
 return rows


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',default=asm.MANIFEST);mode=ap.add_mutually_exclusive_group(required=True);mode.add_argument('--verify-only',action='store_true');mode.add_argument('--promote',action='store_true');args=ap.parse_args()
 require(args.manifest==asm.MANIFEST,'unsupported driver manifest')
 from analysis_support import ROOT,game
 from evidence_snapshot import snapshot,Snapshot
 from check_function import regression_receipt
 root=ROOT;ledger_path=root/'recovery/ledger.json'
 with snapshot(),ledger_lock(ledger_path):
  ledger=asm.document(root,'recovery/ledger.json');before=sha256(ledger_path.read_bytes());print('Verifying batch0002 and current source accounting...',file=sys.stderr,flush=True)
  blob,model,_=game();analysis=asm.document(root,'evidence/functions/ledger.json');rows=stage(root,blob,model,analysis,ledger)
  if args.verify_only:print(json.dumps(dict(verdict='EQUAL_CANDIDATE',manifest=asm.MANIFEST,members=[f['id'] for n,f,r in rows],size=sum(f['original']['size'] for n,f,r in rows),data_credit=0,source_acceptance=False)));return
  inputs=Snapshot().inputs(root,True);print('Running unchanged shared regression gate for batch0002...',file=sys.stderr,flush=True);regression=regression_receipt()
  require(regression.get('passed') is True,'driver promotion requires passing shared regression');require(Snapshot().inputs(root,True)==inputs,'driver inputs changed during regression')
  print('Gate passed; rechecking exact unchanged driver batch...',file=sys.stderr,flush=True);fresh=stage(root,blob,model,analysis,ledger);require(fresh==rows,'driver replay changed after gate')
  artifacts={};updated=canonical_state(ledger)
  for name,fact,report in rows:
   source=canonical_path(root,fact['candidate']).read_bytes();proof=json_bytes(dict(fact=fact,comparison=report,regression=regression));dest='recovery/proofs/asm-reconstructed/'+fact['id']+'.json'
   for n,raw in [(fact['source'],source),(dest,proof)]:
    p=canonical_path(root,n);require(not p.exists() or p.read_bytes()==raw,'driver destination differs');artifacts[p]=raw
   updated.setdefault(asm.MAP,{})[fact['id']]=dict(state='FUNCTION_CODE_MATCH',fact=name,source=fact['source'],source_sha256=sha256(source),proof=dest,proof_sha256=sha256(proof))
  publish(root,ledger_path,artifacts,updated,before);asm.rows(root,blob,model,analysis,updated)
  print(json.dumps(dict(verdict='PROMOTED',manifest=asm.MANIFEST,members=[f['id'] for n,f,r in rows],category='RECONSTRUCTED_ASM',bytes=sum(f['original']['size'] for n,f,r in rows),data_credit=0)))


if __name__=='__main__':main()
