"""Canonical complete C objects, separate from reachable-function proofs.
Every canonical read replays the registered natural unit. Existing reachable
prefix proofs stay valid; accounting counts their remainder only once.
"""
from names import read_source
import argparse,copy,json,sys
from pathlib import Path
from common import require,sha256,json_bytes,write_json,FormatError
from repo_paths import canonical_path
import dead_code_extents as dead
BASIS='CURATED_UNREACHABLE_C_OBJECT_AND_EXACT_NATURAL_UNIT'
MAP='dead_code_functions'

def records(root):
 return {r['id']:r for r in json.loads(canonical_path(root,dead.ADMISSIONS).read_bytes())['admissions']}

def proof_for(root,blob,model,analysis,row,record):
 fid=row['id'];base=next(f for f in analysis['functions'] if f['id']==fid)
 view=dead.make_view(base,analysis,blob,model,root);boundary=dead.admission_boundary(view)
 receipt=json.loads(canonical_path(root,record['receipt']['path']).read_bytes())
 return dict(schema_version=1,id=fid,kind='EXACT_C_OBJECT_WITH_DEAD_CODE',
  state='FUNCTION_WITH_DATA_MATCH' if row['owned_literal_end']>view['end'] else 'FUNCTION_CODE_MATCH',
  source='src/recovered/complete-c/'+fid+'.c',source_sha256=record['source']['sha256'],source_acceptance=True,
  game_sha256=sha256(blob),extent_basis=BASIS,complete_extent=copy.deepcopy(row['complete_extent']),
  reachable_cfg={k:copy.deepcopy(base[k]) for k in ['start','end','size','sha256','extent_status','confidence','return_sites','cfg','boundary_stops','undecoded_gaps']},
  dead_spans=copy.deepcopy(row['dead_spans']),boundary=boundary,owned_literal_end=row['owned_literal_end'],
  unit_entry=record['unit_entry'],exact_receipt=record['receipt'],compiler=record['compiler'],
  candidate=record['source'],entry_source=record['entry_source'],member_sources=record['member_sources'],
  verifier_provenance=receipt['verifier_identity'],original_filename='UNKNOWN',
  original_translation_unit='UNKNOWN',natural_overlay_layout_proved=False)

def canonical_rows(root,blob,model,analysis,ledger):
 rows=dead.verified_admissions(root,blob,model,analysis,ledger,report_stale=True)
 registry=records(root);entries=ledger.get(MAP,{})
 require(set(entries)<=set(r['id'] for r in rows if r['status']=='VERIFIED_COMPLETE_C_SOURCE_OBJECT'),'canonical dead-code admission missing')
 result=[]
 for row in rows:
  if row['status']=='STALE_ADMISSION':
   result.append(dict(row,acceptance=False,extent_basis=BASIS));continue
  expected=proof_for(root,blob,model,analysis,row,registry[row['id']]);fid=row['id']
  fact=dict(row,acceptance=False,extent_basis=BASIS,boundary=expected['boundary'],reachable_cfg=expected['reachable_cfg'])
  if fid in entries:
   item=entries[fid];source=canonical_path(root,item['source']);proof=canonical_path(root,item['proof'])
   require(item['source']==expected['source'] and item['proof']=='recovery/proofs/complete-c/'+fid+'.json' and item['state']==expected['state'],'canonical complete-C identity differs')
   require(read_source(root, source, names_root=None)==canonical_path(root,registry[fid]['source']['path']).read_bytes() and sha256(read_source(root, source, names_root=None))==item['source_sha256']==expected['source_sha256'],'canonical complete-C source changed')
   observed=json.loads(proof.read_bytes());gate=observed.pop('regression_provenance',None)
   require(isinstance(gate,dict) and gate.get('passed') is True,'canonical complete-C regression provenance missing')
   require(sha256(proof.read_bytes())==item['proof_sha256'] and observed==expected,'canonical complete-C proof does not rederive')
   fact.update(acceptance=True,source_acceptance=True,status=expected['state'],source=item['source'],proof=item['proof'])
  result.append(fact)
 return result

def subtract(start,end,covered):
 spans=[(start,end)]
 for a,b in covered:
  out=[]
  for x,y in spans:
   if b<=x or y<=a:out.append((x,y));continue
   if x<a:out.append((x,a))
   if b<y:out.append((b,y))
  spans=out
 return spans

def coverage(row,promotions):
 e=row['complete_extent'];covered=[]
 for p in promotions:
  if p['hunk']!=e['hunk'] or p['end']<=e['start'] or p['start']>=row['owned_literal_end']:continue
  require(p['id']==row['id'] and p['start']==e['start'] and p['end']<=e['end'],'complete-C object overlaps foreign canonical source')
  covered.append((p['start'],p['end']))
 return subtract(e['start'],e['end'],covered)

def accepted_contributions(root,blob,model,analysis,promotions,ledger,*,rows=None):
 # Staged experiments have no accounting authority. Canonical entries still replay.
 if not ledger.get(MAP):return []
 if rows is None:rows=canonical_rows(root,blob,model,analysis,ledger)
 registry=records(root);out=[]
 from hybrid_image import normalize
 for row in rows:
  if not row['acceptance']:continue
  rec=registry[row['id']];producer=json.loads(canonical_path(root,rec['compiler']['path']).read_bytes())
  receipt=json.loads(canonical_path(root,rec['receipt']['path']).read_bytes())
  raw=bytes.fromhex(producer['contribution']['code_hex']);cursor=0
  for m in receipt['ordered_members']:
   comparison=next(r for r in receipt['members'] if r['id']==m['id']);length=comparison['actual_length']
   if m['id']==row['id']:actual=raw[cursor:cursor+length];break
   cursor+=length
  else:raise FormatError('complete-C member absent from producer')
  base=next(f for f in analysis['functions'] if f['id']==row['id']);view=dead.make_view(base,analysis,blob,model,root)
  normalized=normalize(view,actual,comparison,analysis['a4']['bias']);e=row['complete_extent']
  for i,(a,b) in enumerate(coverage(row,promotions)):
   rels=[{k:r[k] for k in ['source_offset','target_hunk','type','width','addend_raw']} for r in model['relocations'] if r['source_hunk']==e['hunk'] and a<=r['source_offset']<b]
   out.append(dict(id=row['id']+'_complete_%d'%i,hunk=e['hunk'],start=a,end=b,bytes=normalized[a-e['start']:b-e['start']],category='RECOVERED_C',relocations=rels))
  if row['owned_literal_end']>e['end']:
   out.append(dict(id=row['id']+'_complete_literal',hunk=e['hunk'],start=e['end'],end=row['owned_literal_end'],bytes=normalized[e['size']:],category='COMPILER_OWNED_DATA'))
 return out

def commit(root,fid,source,proof,expected_state,input_guard=None):
 """Atomic source/proof/map transaction, retaining ordinary function proofs."""
 from recovery_transaction import ledger_lock
 from recovery_state import canonical_state
 ledger_path=root/'recovery/ledger.json';source_path=root/proof['source'];proof_path=root/('recovery/proofs/complete-c/'+fid+'.json')
 require(proof.get('id')==fid and proof.get('source_sha256')==sha256(source) and proof.get('source_acceptance') is True and proof.get('extent_basis')==BASIS,'complete-C source/proof binding differs')
 require(proof.get('regression_provenance',{}).get('passed') is True,'complete-C promotion requires regression provenance')
 with ledger_lock(ledger_path):
  state=json.loads(ledger_path.read_bytes());require(canonical_state(state)==expected_state,'canonical inputs changed before complete-C commit')
  if input_guard is not None:input_guard()
  current=state.get(MAP,{}).get(fid)
  item=dict(state=proof['state'],source=proof['source'],source_sha256=sha256(source),proof=proof_path.relative_to(root).as_posix(),proof_sha256=sha256(json_bytes(proof)))
  require(not current or current==item,'already accepted complete-C object differs')
  require(not source_path.exists() or read_source(root, source_path, names_root=None)==source,'complete-C source path contains another source')
  require(not proof_path.exists() or proof_path.read_bytes()==json_bytes(proof),'complete-C proof path contains another proof')
  paths=[source_path,proof_path,ledger_path];saved={p:p.read_bytes() if p.exists() else None for p in paths}
  try:
   source_path.parent.mkdir(parents=True,exist_ok=True);proof_path.parent.mkdir(parents=True,exist_ok=True)
   source_path.write_bytes(source);write_json(proof_path,proof);require(sha256(proof_path.read_bytes())==item['proof_sha256'],'canonical complete-C proof serialization differs')
   state.setdefault(MAP,{})[fid]=item;write_json(ledger_path,canonical_state(state))
  except BaseException:
   for path,raw in saved.items():
    if raw is None:path.unlink(missing_ok=True)
    else:path.write_bytes(raw)
   raise
 return item

def run(fid,*,promote=False,output_dir=None):
 from analysis_support import ROOT
 from game_image import game
 from recovery_state import recovery,evidence,canonical_state
 from recovery_evidence import load_promotions
 from evidence_snapshot import snapshot,Snapshot
 fingerprint=Snapshot().inputs(ROOT,True)
 def unchanged():require(Snapshot().inputs(ROOT,True)==fingerprint,'complete-C verification inputs changed before promotion')
 with snapshot():
  blob,model,_=game();analysis=evidence();state=recovery();before=canonical_state(state)
  rows=canonical_rows(ROOT,blob,model,analysis,state);row=next((r for r in rows if r['id']==fid),None)
  require(row is not None,'complete-C entry is not exactly admitted')
  coverage(row,load_promotions(ROOT,blob,model,analysis))
  rec=records(ROOT)[fid];proof=proof_for(ROOT,blob,model,analysis,row,rec);source=canonical_path(ROOT,rec['source']['path']).read_bytes()
  result=dict(id=fid,verdict='EQUAL',source_acceptance=False,extent_basis=BASIS,complete_extent=row['complete_extent'],dead_spans=row['dead_spans'],boundary=proof['boundary'],exact_receipt=rec['receipt'])
  if output_dir is not None:
   from check_function import isolated_output_root
   out=isolated_output_root(output_dir);(out/(fid+'.c')).write_bytes(source);write_json(out/(fid+'.proof.json'),proof);write_json(out/(fid+'.json'),result)
  if promote and row['acceptance']:
   result.update(promotion=state[MAP][fid],source_acceptance=True);return result
  if promote:
   from check_function import regression_receipt
   gate=regression_receipt()
   fresh=canonical_rows(ROOT,blob,model,analysis,recovery());require(next(r for r in fresh if r['id']==fid)['complete_extent']==row['complete_extent'],'complete-C extent changed during regression')
   proof['regression_provenance']=gate
   result['promotion']=commit(ROOT,fid,source,proof,before,unchanged);result['source_acceptance']=True
  return result

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('id');mode=ap.add_mutually_exclusive_group(required=True);mode.add_argument('--isolated',action='store_true');mode.add_argument('--promote',action='store_true');ap.add_argument('--output-dir',type=Path);a=ap.parse_args()
 require(a.output_dir is None or a.isolated,'--output-dir requires --isolated')
 print(json.dumps(run(a.id,promote=a.promote,output_dir=a.output_dir)));return 0
if __name__=='__main__':
 try:sys.exit(main())
 except (FormatError,OSError,ValueError) as e:print(json.dumps(dict(verdict='BLOCKED',reason=str(e))));sys.exit(2)
