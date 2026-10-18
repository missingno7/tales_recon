"""Strict staged complete-C views, preserving the original reachable CFG.

Pending intervals are not census extents or source acceptance. Only an explicit
isolated unit check may use a pending view; a verified admission must replay
that entire exact natural unit with unchanged source and producing inputs.
"""
from names import to_mechanical
from contextlib import contextmanager,nullcontext
from contextvars import ContextVar
import copy,json
from common import require,sha256,json_bytes,FormatError
from repo_paths import canonical_path
from analysis_support import K,decoder,instruction,basic
INPUT='evidence/rules/dead-code-extents/entries.json'
STATUS='COMPLETE_C_SOURCE_OBJECT_WITH_DEAD_CODE'
_ACTIVE=ContextVar('staged_dead_code_entry',default=None)
_ANALYSIS=ContextVar('fresh_dead_code_analysis',default=None)
_IMAGE=ContextVar('exact_dead_code_image',default=None)
_REFRESH=ContextVar('refresh_dead_code_analysis',default=False)
_REPLAY=ContextVar('dead_code_replay_context',default=None)
def replay_context():return _REPLAY.get()
def replay_root(default):return (_REPLAY.get() or {}).get('root',default)
def refreshing_analysis():return _REFRESH.get()
@contextmanager
def analysis_refresh():
 token=_REFRESH.set(True)
 try:yield
 finally:_REFRESH.reset(token)
def current_image():return _IMAGE.get()
def current_analysis():return _ANALYSIS.get()
def mode_active():return _ACTIVE.get() is not None

@contextmanager
def isolated_view(fid,analysis=None,image=None,context=None):
 token=_ACTIVE.set(fid);other=_ANALYSIS.set(analysis);picture=_IMAGE.set(image);scope=_REPLAY.set(context)
 try:yield
 finally:_ACTIVE.reset(token);_ANALYSIS.reset(other);_IMAGE.reset(picture);_REPLAY.reset(scope)

def active_entry(fid):return _ACTIVE.get()==fid

def inputs(root,*,resolve=None):
 """Enumerate readable dependencies, also for a stale noncanonical record.
 Schema/ownership decisions belong to verified_admissions. A malformed or
 missing retained file still changes the registry/compiler hash and cannot
 reuse a successful replay; it must not break unrelated snapshot creation.
 """
 resolve=resolve or (lambda name:canonical_path(root,name))
 names=[INPUT,'evidence/rules/dead-code-extents/admissions.json']
 def document(path):
  try:return json.loads(path.read_bytes())
  except (OSError,ValueError):return {}
 def add(name):
  try:path=resolve(name)
  except (FormatError,TypeError):return None
  names.append(path.relative_to(root).as_posix());return path
 p=resolve(names[1]);doc=document(p)
 rows=doc.get('admissions',[]) if isinstance(doc,dict) else []
 for row in rows if isinstance(rows,list) else []:
  if not isinstance(row,dict):continue
  specs=[row.get(k) for k in ['source','entry_source','receipt','compiler']]
  if isinstance(row.get('member_sources'),dict):specs+=list(row['member_sources'].values())
  for spec in specs:
   if isinstance(spec,dict) and isinstance(spec.get('path'),str):add(spec['path'])
  compiler=row.get('compiler',{})
  if not isinstance(compiler,dict) or not isinstance(compiler.get('path'),str):continue
  compiled=add(compiler['path'])
  producer=document(compiled) if compiled is not None else {}
  artifacts=producer.get('artifacts',[]) if isinstance(producer,dict) else []
  for artifact in artifacts if isinstance(artifacts,list) else []:
   if isinstance(artifact,dict) and isinstance(artifact.get('path'),str):add(compiled.parent/artifact['path'])
 return sorted(set(names))

def identity(root):
 # CFG identity tracks curated decisions. Producing artifacts are checked by
 # replay_identity and exact admission, not once for each decoded member.
 return {name:sha256(canonical_path(root,name).read_bytes()) for name in [INPUT,ADMISSIONS] if canonical_path(root,name).exists()}

def row_for(root,blob,fid):
 p=canonical_path(root,INPUT);require(p.exists(),'dead-code input missing')
 doc=json.loads(p.read_bytes())
 require(set(doc)=={'schema_version','game_sha256','source_acceptance','entries'},'dead-code input schema differs')
 require(type(doc['schema_version']) is int and doc['schema_version']==1 and doc['source_acceptance'] is False and doc['game_sha256']==sha256(blob),'dead-code input identity differs')
 fields={'id','hunk','start','code_end','contribution_end','dead_spans','next_entry','justification','admission'}
 require(isinstance(doc['entries'],list),'dead-code entries must be a list')
 seen=set();found=None
 for row in doc['entries']:
  require(isinstance(row,dict) and set(row)==fields,'dead-code entry schema differs')
  require(row['id'] not in seen,'duplicate dead-code entry');seen.add(row['id'])
  require(all(type(row[k]) is int for k in ['hunk','start','code_end','contribution_end']),'dead-code coordinates must be integers')
  require(row['hunk']>=3 and row['id']=='ov%02d_F_%04X'%(row['hunk'],row['start']),'dead-code overlay identity differs')
  require(0<=row['start']<row['code_end']<=row['contribution_end'] and all(row[k]%2==0 for k in ['start','code_end','contribution_end']),'dead-code bounds differ')
  require(isinstance(row['justification'],str) and row['justification'].strip(),'dead-code justification missing')
  require(isinstance(row['dead_spans'],list) and row['dead_spans'],'dead-code spans missing')
  require(isinstance(row['next_entry'],str),'dead-code next entry missing')
  require(row['admission'] is None,'pending entry cannot assert admission')
  if row['id']==fid:found=row
 require(found is not None,'dead-code entry not listed: '+fid)
 return found

def make_view(base,ledger,blob,model,root):
 row=row_for(root,blob,base['id']);h=base['hunk'];start=base['start'];end=row['code_end']
 require((row['hunk'],row['start'])==(h,start),'dead-code measured entry changed')
 require(end>=base['end'],'dead-code view truncates reachable body')
 hu=next(x for x in model['hunks'] if x['number']==h);data=blob[hu['content_offset']:hu['content_offset']+hu['initialized_size']]
 require(end<=len(data),'dead-code object outside hunk')
 spans=[];cursor=start
 for span in row['dead_spans']:
  require(isinstance(span,list) and len(span)==2 and all(type(v) is int for v in span),'dead-code span schema differs')
  a,b=span;require(start<a<b<=end and a%2==b%2==0 and a>=cursor,'dead-code span bounds/ordering differ');cursor=b;spans.append((a,b))
 reachable=[(i['offset'],i['offset']+i['size']) for i in base['instructions']]
 require(not base['boundary_stops'],'dead-code base has unresolved stops')
 require(not any(a<d and c<b for a,b in spans for c,d in reachable),'dead-code overlaps reachable instructions')
 require(sorted(spans)==sorted([tuple(x) for x in base['undecoded_gaps']]+([(base['end'],end)] if end>base['end'] else [])),'dead-code spans are not exactly the reachable CFG holes/tail')
 require(not base['jump_tables'] and not base['indirect_control_flow'],'dead-code view requires direct decoded control flow')
 from function_census import Census,function_id
 c=Census(blob,model,[]);md=decoder();items=[];calls=[];refs=[];edges=[];returns=[];pc=start
 while pc<end:
  ins=instruction(md,data,pc);require(ins is not None and pc+ins.size<=end,'dead-code bytes do not decode completely')
  items.append(basic(ins));mn=ins.mnemonic.split('.')[0];nxt=pc+ins.size
  require(pc!=start or (mn=='link' and data[pc:pc+2]==b'\x4e\x55'),'dead-code owner does not start with LINK A5')
  require(pc==start or mn!='link','dead-code hides another LINK entry')
  if mn in ['rts','rte','rtr','rtd']:
   require(mn=='rts' and len(items)>1 and items[-2]['offset']==pc-2 and items[-2]['mnemonic']=='unlk' and data[pc-2:pc]==b'\x4e\x5d','dead-code return is not terminal decoded UNLK/RTS');returns.append(pc)
  require(mn not in ['stop','illegal','trap','trapv'],'dead-code contains terminal trap')
  is_call=mn in ['jsr','bsr'];branch=mn in ['bra','jmp'] or (ins.operands and ins.operands[-1].type==K.M68K_OP_BR_DISP and not is_call)
  if is_call or branch:
   target=c.target(h,ins);require(target is not None,'dead-code has unresolved control flow')
   th,to,basis=target
   if is_call:calls.append(dict(site=pc,hunk=th,offset=to,id=function_id(th,to),basis=basis))
   else:
    require(th==h and start<=to<end,'dead-code branch escapes complete object');edges.append(dict(source=pc,target=to,kind='UNCONDITIONAL' if mn in ['bra','jmp'] else 'CONDITIONAL'))
    if mn not in ['bra','jmp']:edges.append(dict(source=pc,target=nxt,kind='FALLTHROUGH'))
  for o in ins.operands:
   if o.type!=K.M68K_OP_MEM:continue
   ref=None
   if o.address_mode==K.M68K_AM_PCI_DISP and mn not in ['jsr','jmp']:ref=dict(hunk=h,offset=pc+2+o.mem.disp,kind='PC_RELATIVE_DATA')
   elif o.mem.base_reg==K.M68K_REG_A4 and o.address_mode==K.M68K_AM_REGI_ADDR_DISP and c.a4_bias is not None:ref=dict(hunk=1,offset=c.a4_bias+o.mem.disp,kind='A4_RELATIVE')
   if ref:ref['instruction_offset']=pc;refs.append(ref)
  pc=nxt
 terminal=items[-1];terminal_targets=[e['target'] for e in edges if e['source']==terminal['offset']]
 require(returns and (terminal['mnemonic']=='rts' or (terminal['mnemonic'].split('.')[0] in ['bra','jmp'] and len(terminal_targets)==1 and terminal_targets[0]+2 in returns)), 'dead-code terminal instruction does not close at its UNLK/RTS epilogue')
 boundaries={i['offset'] for i in items}
 require(all(e['target'] in boundaries for e in edges),'dead-code branch target splits an instruction')
 # Every byte not reachable from the original entry is exactly a listed span.
 by={i['offset']:i for i in items};edgeby={}
 for e in edges:edgeby.setdefault(e['source'],[]).append(e['target'])
 seen=set();todo=[start]
 while todo:
  at=todo.pop()
  if at in seen:continue
  require(at in by,'complete object falls into non-instruction bytes');seen.add(at);i=by[at];mn=i['mnemonic'].split('.')[0]
  if mn=='rts':continue
  if at in edgeby:todo+=edgeby[at]
  elif at+i['size']<end:todo.append(at+i['size'])
  else:require(False,'complete object falls through its end')
 deadbytes={v for a,b in spans for v in range(a,b)}
 measured={v for i in items if i['offset'] not in seen for v in range(i['offset'],i['offset']+i['size'])}
 require(measured==deadbytes,'listed dead bytes are not exactly unreachable from entry')
 # No other function may own, call, branch or take data addresses into dead bytes or own literals.
 foreign_intervals=spans+([(end,row['contribution_end'])] if end<row['contribution_end'] else [])
 from curated_unreferenced_entries import claimed_ranges
 for owner,hh,a,b in claimed_ranges(root):
  require(owner==base['id'] or hh!=h or not any(a<d and c0<b for c0,d in foreign_intervals),'dead-code overlaps foreign owned contribution')
 for fact in ledger.get('classified_code_data',[]):
  iv=fact['interval'];require(iv['hunk']!=h or not any(iv['start']<b and a<iv['end'] for a,b in foreign_intervals),'dead-code overlaps classified data')
 def inside(hh,off):return hh==h and any(a<=off<b for a,b in foreign_intervals)
 for other in ledger['functions']:
  if other['id']==base['id']:continue
  require(other['hunk']!=h or not any(other['start']<b and a<other['end'] for a,b in foreign_intervals),'dead-code overlaps foreign function')
  targets=[(r['hunk'],r['offset']) for r in other['direct_callees']+other['referenced_data']]
  if other['hunk']==h:targets += [(h,e['target']) for e in other['cfg']]
  require(not any(inside(hh,off) for hh,off in targets),'dead-code has foreign reference')
 for r in model['relocations']:
  require(not inside(r['target_hunk'],r['addend_raw']) or (r['source_hunk']==h and start<=r['source_offset']<end),'dead-code has foreign relocation')
 nxt=next((f for f in ledger['functions'] if f['id']==row['next_entry']),None)
 if row['next_entry']=='TERMINAL_LITERAL_BOUNDARY':
  require(row['contribution_end']>end and 0<=len(data)-row['contribution_end']<=2 and all(v==0 for v in data[row['contribution_end']:]),'dead-code terminal literal boundary differs')
  require(not any(o['hunk']==h and o['start']>=end for o in ledger['functions']),'dead-code terminal tail precedes another function')
 else:require(nxt is not None and nxt['hunk']==h and nxt['start']==row['contribution_end'] and nxt['extent_status']=='CLOSED_CFG','dead-code next closed boundary differs')
 f=copy.deepcopy(base);f.update(end=end,size=end-start,raw_bytes=data[start:end].hex(),sha256=sha256(data[start:end]),instructions=items,direct_callees=calls,referenced_data=refs,referenced_strings=[],return_sites=returns,relocations=[dict(r,relative_offset=r['source_offset']-start) for r in model['relocations'] if r['source_hunk']==h and start<=r['source_offset']<end],extent_status=STATUS,source_object_cfg=edges)
 for r in refs:
  if r['kind']!='PC_RELATIVE_DATA' or r['hunk']!=h:continue
  off=r['offset'];nul=data.find(b'\0',off,min(len(data),off+160));raw=data[off:nul] if nul>=off else b''
  if nul>=off and all(32<=v<127 or v in (9,10,13) for v in raw):f['referenced_strings'].append(dict(hunk=h,offset=off,text=raw.decode('ascii')))
 if row['contribution_end']>end:
  from owned_code_data import expected_string_tail
  tail,own=expected_string_tail(f,context=dict(blob=blob,model=model));require(own['end']==row['contribution_end'] and tail==data[end:own['end']],'dead-code literal tail is not complete')
 else:require(not any(r['kind']=='PC_RELATIVE_DATA' and r['hunk']==h for r in refs),'dead-code literal references lack owned tail')
 f['dead_code_extent']=dict(input=INPUT,input_sha256=sha256(canonical_path(root,INPUT).read_bytes()),validator_sha256=sha256(__import__('pathlib').Path(__file__).read_bytes()),reachable_extent={k:base[k] for k in ['start','end','size','sha256','extent_status']},dead_spans=row['dead_spans'],contribution_end=row['contribution_end'],source_acceptance=False)
 return f

def selected_view(f,ledger,blob,model,root):
 return make_view(f,ledger,blob,model,root) if _ACTIVE.get()==f['id'] else f

def comparison_allowed(f,context=None):
 if f.get('extent_status')!=STATUS or _ACTIVE.get()!=f['id']:return False
 from analysis_support import game,ROOT
 from recovery_state import evidence
 blob,model,_=game() if context is None else (context['blob'],context['model'],None)
 root=ROOT if context is None else context['root'];ledger=(current_analysis() or evidence()) if context is None else context['analysis']
 base=next(x for x in ledger['functions'] if x['id']==f['id']);view=make_view(base,ledger,blob,model,root)
 require(f==view,'dead-code comparison view does not re-derive')
 return True

ADMISSIONS='evidence/rules/dead-code-extents/admissions.json'

def admission_boundary(view):
 """Re-derive internal holes or a bounded owner-epilogue back-transfer tail."""
 spans=view['dead_code_extent']['dead_spans'];dead=lambda off:any(a<=off<b for a,b in spans)
 reachable_returns=[r for r in view['return_sites'] if not dead(r) and not dead(r-2)]
 require(reachable_returns,'dead-code object lacks a reachable owner epilogue')
 last=max(reachable_returns)
 post=[(a,b) for a,b in spans if b>last+2]
 if not post:return dict(kind='INTERNAL_UNREACHABLE_C',last_reachable_epilogue=last-2)
 require(post==[(last+2,view['end'])], 'post-epilogue tail must start immediately after the last reachable RTS and end at its closed boundary')
 terminal=view['instructions'][-1]
 edges=[e for e in view['source_object_cfg'] if e['source']==terminal['offset']]
 require(terminal['mnemonic'].split('.')[0] in ['bra','jmp'] and len(edges)==1 and edges[0]['kind']=='UNCONDITIONAL' and edges[0]['target']==last-2,
         'post-epilogue tail must transfer unconditionally to the same last reachable owner UNLK/RTS')
 return dict(kind='POST_EPILOGUE_OWNER_BACK_TRANSFER',last_reachable_epilogue=last-2,tail=[last+2,view['end']],terminal_transfer=dict(site=terminal['offset'],target=last-2))


def verified_admissions(root,blob,model,analysis,ledger=None,*,report_stale=False):
 """Re-derive exact complete source objects; never rewrite CLOSED_CFG evidence.

 Admissions are active, reviewed producing inputs, not a cached PASS. Both the
 current natural-unit recipe and every retained producing artifact must match,
 followed by an all-member exact comparison. Identical replay is memoized
 only by its complete current content identity; changed inputs always miss.
 """
 p=canonical_path(root,ADMISSIONS)
 if not p.exists():return []
 doc=json.loads(p.read_bytes())
 require(set(doc)=={'schema_version','admissions'} and doc['schema_version']==1 and isinstance(doc['admissions'],list),'dead-code admission schema differs')
 if ledger is None:
  state_path=canonical_path(root,'recovery/ledger.json')
  ledger=json.loads(state_path.read_bytes()) if state_path.exists() else dict(functions={})
 results=[];seen=set();common_key=None
 for row in doc['admissions']:
  require(set(row)=={'id','unit_entry','source','entry_source','receipt','compiler','member_sources'},'dead-code admission entry schema differs')
  fid=row['id'];entry=row['unit_entry'];require(fid not in seen,'duplicate dead-code admission');seen.add(fid)
  try:
   if common_key is None:common_key=replay_identity(root,blob,model,analysis,ledger,None)
   key=_row_identity(common_key,row)
   from evidence_snapshot import memoized
   results.append(memoized(root,'exact-dead-code:'+fid,key,lambda:_stable_replay(root,blob,model,analysis,ledger,row,key),process_cache=True))
  except (FormatError,OSError,ValueError,KeyError,TypeError) as error:
   if not report_stale or fid in ledger.get('dead_code_functions',{}):raise
   results.append(dict(id=fid,status='STALE_ADMISSION',reason=str(error),source_acceptance=False,proof_level=None))
 return results


def _verify_admission(root,blob,model,analysis,ledger,row):
 fid=row['id'];entry=row['unit_entry']
 base=next((f for f in analysis['functions'] if f['id']==fid),None);require(base is not None,'dead-code admission entry missing')
 admission_boundary(make_view(base,analysis,blob,model,root))
 def pinned(spec):
  require(isinstance(spec,dict) and set(spec)=={'path','sha256'},'dead-code retained input schema differs')
  path=canonical_path(root,spec['path']);require(sha256((to_mechanical(path.read_bytes()) if spec['path'].startswith('src/') else path.read_bytes()))==spec['sha256'],'dead-code retained input changed: '+spec['path']);return path
 source_path=pinned(row['source']);entry_path=pinned(row['entry_source']);receipt_path=pinned(row['receipt']);compiler_path=pinned(row['compiler'])
 receipt=json.loads(receipt_path.read_bytes());producer=json.loads(compiler_path.read_bytes())
 source=(to_mechanical(source_path.read_text(encoding='ascii')) if row['source']['path'].startswith('src/') else source_path.read_text(encoding='ascii'));entry_source=(to_mechanical(entry_path.read_text(encoding='ascii')) if row['entry_source']['path'].startswith('src/') else entry_path.read_text(encoding='ascii'));member_paths={k:pinned(v) for k,v in row['member_sources'].items()}
 require(receipt.get('verdict')=='EQUAL' and receipt.get('id')==entry and receipt.get('unclaimed_bytes')==0,'dead-code admission lacks exact whole-unit verdict')
 require(receipt.get('source_sha256')==sha256(entry_source.encode('ascii')),'dead-code admission candidate source changed')
 require((fid==entry and source_path==entry_path) or (fid in member_paths and source_path==member_paths[fid]),'dead-code source is not a producing unit member')
 require(all(receipt.get('member_sources',{}).get(k)==sha256((to_mechanical(v.read_text(encoding='ascii')) if row['member_sources'][k]['path'].startswith('src/') else v.read_text(encoding='ascii')).encode('ascii')) for k,v in member_paths.items()),'dead-code member source changed')
 state=ledger
 require(all(state['functions'].get(k,{}).get('source_sha256')==v for k,v in receipt['dependency_sources'].items()),'dead-code canonical dependencies changed')
 # The receipt's verifier identity is retained provenance. Acceptance comes
 # from the complete exact replay below with today's comparator (as for every
 # other proof class), so later tooling changes do not stale the admission.
 require(isinstance(receipt.get('verifier_identity'),dict) and receipt['verifier_identity'],'dead-code receipt lacks verifier provenance')
 require(producer['status']=='COMPILED' and producer['cache_key']==receipt['cache_key'] and sha256(json_bytes(producer['identity']))==producer['cache_key'],'dead-code producer identity differs')
 directory=compiler_path.parent
 for a in producer['artifacts']:
  path=canonical_path(root,directory/a['path']);require(sha256(path.read_bytes())==a['sha256'],'dead-code producing artifact changed: '+a['path'])
 from compiler_oracle import extract
 meta=producer['identity'];prefix=producer['prefix']
 contribution=extract(directory,prefix,meta.get('object_labels'),meta.get('entry_function','recovered'),meta.get('same_overlay_exports'))
 require(contribution==producer['contribution'],'dead-code compiler object/executable extraction differs')
 compiled=dict(producer,directory=str(directory),cache_hit=True)
 import check_unit
 context=dict(root=root,ledger=ledger)
 with isolated_view(fid,analysis,(blob,model,{}),context):
  plans=check_unit.check(entry,entry_path,[receipt['profile']],promote_equal=False,owned_code_data=bool(receipt.get('owned_code_tails')),isolated=True,member_sources=member_paths,natural_interval=receipt['natural_interval']['interval'],prepare_only=True,object_groups=receipt.get('object_groups'),per_member_profiles=receipt.get('per_member_profiles',False),with_m_lib=bool(meta.get('additional_libraries')))
  require(len(plans)==1 and plans[0]['trials'][0]['cache_key']==producer['cache_key'],'dead-code current natural-unit producer recipe changed')
  require(plans[0]['natural_interval']==receipt['natural_interval'],'dead-code natural interval or gap encoding changed')
  members,names,parts,combined,prepared_ledger=context['prepared_unit']
  expected_dependencies={m['id']:ledger['functions'][m['id']]['source_sha256'] for m in members if m['id']!=entry and m['id'] not in member_paths}
  require(receipt['dependency_sources']==expected_dependencies,'dead-code retained dependencies are not the complete planned set')
  # The normal exact comparator re-derives every CODE byte, literal and field.
  compared=check_unit.compare_unit(members,names,compiled,prepared_ledger['a4']['bias'],bool(receipt.get('owned_code_tails')),source_text=combined,natural=receipt['natural_interval'])
  require(compared['verdict']=='EQUAL' and compared['unclaimed_bytes']==0,'dead-code exact full-unit replay differs')
  target=next(m for m in members if m['id']==fid)
  # Compare the extent facts; the validator's own file hash is provenance.
  facts=lambda w:{k:v for k,v in (w or {}).items() if k!='validator_sha256'}
  require(facts(next(m for m in receipt['members'] if m['id']==fid).get('dead_code_extent'))==facts(target['dead_code_extent']),'dead-code extent witness changed')
 return dict(id=fid,status='VERIFIED_COMPLETE_C_SOURCE_OBJECT',original_cfg=target['dead_code_extent']['reachable_extent'],complete_extent={k:target[k] for k in ['hunk','start','end','size','sha256']},dead_spans=target['dead_code_extent']['dead_spans'],owned_literal_end=target['dead_code_extent']['contribution_end'],source=row['source'],receipt=row['receipt'],source_acceptance=False,proof_level=None)


def replay_identity(root,blob,model,analysis,ledger,row,*,input_files=None):
 """Complete exact-replay closure; every content hash is current.
 DATA provider jobs are not read by the supplied-image unit comparator.
 """
 from pathlib import Path
 from replay_inputs import ContentScan
 scan=ContentScan(root)
 read=scan.read
 documents={}
 def document(path):
  target=scan.canonical(path);name=str(target)
  if name not in documents:
   raw=read(target);documents[name]=json.loads(raw) if raw is not None else {}
  return documents[name]
 for path in sorted((root/'tools').glob('*.py')):read(path)
 for name in inputs(root,resolve=scan.canonical):read(name)
 for name in ['recovery/ledger.json','evidence/fixture-lock.json','evidence/functions/ledger.json','evidence/executable/overlay-tree.json','evidence/types.json','toolchain/candidate-lock.json','evidence/rules/unreferenced-entries/entries.json']:
  read(name)
 for directory in [root/'evidence/experiments',root/'evidence/contributions']:
  for path in sorted(directory.glob('*.json')):read(path)
 registry=document(ADMISSIONS);required=set()
 for admission in registry.get('admissions',[]):
  # A stale noncanonical receipt cannot block another admission's inventory.
  # Its raw contents are hashed above; the strict per-row pin check rejects it.
  spec=admission.get('receipt') if isinstance(admission,dict) else None
  if not isinstance(spec,dict) or not isinstance(spec.get('path'),str):continue
  try:retained=document(spec['path'])
  except (FormatError,OSError,ValueError):continue
  if isinstance(retained,dict) and isinstance(retained.get('dependency_sources'),dict):required.update(retained['dependency_sources'])
 cache_keys=set()
 # Both supplied ownership and the on-disk ownership consulted by make_view.
 actual=document('recovery/ledger.json')
 for state in [ledger,actual]:
  for map_name in ['functions','mixed_source_objects','dead_code_functions']:
   for fid,item in state.get(map_name,{}).items():
    planned=map_name=='functions' and fid in required
    ownership=map_name=='mixed_source_objects' or item.get('state')=='FUNCTION_WITH_DATA_MATCH'
    if not planned and not ownership:continue
    if planned and item.get('source'):read(item['source'])
    if not item.get('proof'):continue
    proof=document(item['proof']);unit_name=proof.get('comparison',{}).get('complete_unit_receipt')
    if planned and unit_name:
     unit_path=scan.canonical(unit_name);unit=document(unit_path);read(unit_path.parent/'unit.c')
     if unit.get('cache_key'):cache_keys.add(unit['cache_key'])
     if unit.get('object_groups') is not None:
      for member in unit.get('ordered_members',[]):read(unit_path.parent/'parts'/(member['id']+'.c'))
 # Object-group planning reads these canonical units' hash-checked compile
 # receipts and assembler/object artifacts, including absence of a cache entry.
 from compiler_oracle import CACHE,ROOT as compiler_root
 cache_scan=scan if compiler_root.resolve()==root.resolve() else ContentScan(compiler_root)
 for cache_key in sorted(cache_keys):
  require(isinstance(cache_key,str) and len(cache_key)==64 and all(c in '0123456789abcdef' for c in cache_key),'canonical unit cache identity differs')
  directory=CACHE/cache_key;raw=cache_scan.read(directory/'receipt.json',scratch=True)
  if raw is None:continue
  producer=json.loads(raw)
  for artifact in producer.get('artifacts',[]):cache_scan.read(directory/artifact['path'],scratch=True)
 values=dict(scan.values);values.update(cache_scan.values)
 # Minimal explicit-context fixtures may lack tools/toolchain. Hash the actual
 # comparator implementations and compiler binaries used by this interpreter.
 from compiler_oracle import PROFILES,ROOT as compiler_root
 actual_scan=scan if compiler_root.resolve()==root.resolve() else ContentScan(compiler_root)
 for path in sorted(Path(__file__).parent.glob('*.py')):actual_scan.read(path)
 # Callback ABI validation reads these SDK headers even during an ordinary
 # complete-C replay. Include every header, including its absence, in the
 # actual interpreter/toolchain closure (minimal fixture roots may lack it).
 from function_pointer_evidence import HEADERS,PREFIX
 actual_scan.read(compiler_root/'evidence/toolchain/aztec-3.6a.json')
 for header in HEADERS:actual_scan.read(compiler_root/(PREFIX+header))
 for profile in PROFILES.values():
  for name in ['bin/cc','bin/as','bin/ln','lib/c.lib','lib/c16.lib','lib/c32.lib','lib/m.lib']:
   actual_scan.read(compiler_root/profile['base']/name)
 values.update(actual_scan.values)
 if input_files is not None:input_files.update(values)
 return sha256(json.dumps(dict(row=row,oracle=sha256(blob),model=model,analysis=analysis,ledger=ledger,contents=values),sort_keys=True,separators=(',',':')).encode('utf-8'))


def _row_identity(common_key,row):return sha256(json_bytes([common_key,row]))


def _stable_replay(root,blob,model,analysis,ledger,row,key):
 from evidence_snapshot import snapshot,content_stage
 # The exact replay closure supplies the nested memoization stage identity.
 # The fresh full content check below is its mandatory exit check.
 with snapshot(),content_stage(root,key):
  result=_verify_admission(root,blob,model,analysis,ledger,row)
  require(_row_identity(replay_identity(root,blob,model,analysis,ledger,None),row)==key,'dead-code replay inputs changed during verification')
  return result
