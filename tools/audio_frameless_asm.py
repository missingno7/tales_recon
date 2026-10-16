"""Batch 0004: independent audio entries under calibrated FRAMELESS_ENTRY."""
from validation_memo import shared
import json,re
from pathlib import Path
from common import require,sha256,json_bytes
from repo_paths import canonical_path,candidate_path,active_files
from audio_sequence_data import payload,field
from hunk import parse as hunk_parse
from overlay_experiment import symbols as symbol_map
import audio_driver_contracts as contracts
import audio_register_calibration as calibration
from audio_driver_objects import parse as aj_parse
import audio_score_measured as score
MANIFEST='evidence/reconstructed-asm/batch-0004.json'
RULES='evidence/rules/asm-reconstructed/batch-0004/'
SPECS={'resident_frameless_%04X'%a:dict(start=a,end=z,prefix=p) for a,z,p in [(0x5594,0x559e,'disable'),(0x55d6,0x5646,'irq0'),(0x5646,0x56b6,'irq1'),(0x56b6,0x5726,'irq2'),(0x5726,0x5796,'irq3'),(0x5868,0x58bc,'clear'),(0x615e,0x617c,'cbwrap')]}
FACTS=['evidence/reconstructed-asm/'+i+'.json' for i in SPECS]
MAP='reconstructed_asm'
def document(root,name):return json.loads(canonical_path(root,name).read_bytes())

def derive(blob,model,measured,root=None):
 from analysis_support import ROOT
 import audio_frame_calibration as frame
 import function_pointer_evidence as pointer
 root=ROOT if root is None else root
 require(measured['all_required_entries_link_a5'] is True,'frame calibration not established')
 c=payload(blob,model,0);outer=contracts.decode(c[0x50e8:0x534e],0x50e8);ob={i['offset']:i for i in outer}
 roots=pointer.callback_apis(root,blob,model)
 rels={(r['source_hunk'],r['source_offset']):field(r) for r in model['relocations']}
 def data(site,target):
  require(rels.get((0,site))==dict(source_hunk=0,source_offset=site,target_hunk=1,addend_raw=target,type='HUNK_RELOC32',width=4),'SDK registration DATA binding')
 entries={}
 for target,site,record,number in [(0x55d6,0x51d4,0xb33e,7),(0x5646,0x5212,0xb354,8),(0x56b6,0x5250,0xb36a,9),(0x5726,0x528e,0xb380,10),(0x615e,0x52d0,0xb312,5)]:
  api='_AddIntServer' if target==0x615e else '_SetIntVector'
  contracts.at(ob,site,'lea.l','$%x(pc), a0'%target)
  contracts.at(ob,site+4,'move.l','a0, $%x.l'%(record+18));data(site+6,record+18)
  contracts.at(ob,site+10,'pea.l','$%x.l'%record);data(site+12,record)
  contracts.at(ob,site+16,'pea.l','$%x.w'%number)
  call=ob[site+20];require(call['mnemonic']=='jsr' and roots.get((0,contracts.target(call)))==api,'independent pinned SDK API binding')
  entries[target]=dict(kind='SDK_INTERRUPT_IS_CODE',caller=0x50e8,site=site,store_site=site+4,record_hunk=1,record_offset=record,code_field_offset=18,registration_site=site+20,api=api,header_identity=pointer.identity(root))
 caller=contracts.decode(c[0x53e6:0x5428],0x53e6);by={i['offset']:i for i in caller}
 contracts.at(by,0x53ea,'jsr','$5594(pc)');contracts.at(by,0x53ee,'jsr','$5868(pc)');contracts.at(ob,0x52a8,'jsr','$5868(pc)')
 entries[0x5594]=dict(kind='DIRECT_CALL',caller=0x53e6,site=0x53ea,target=0x5594)
 entries[0x5868]=dict(kind='DIRECT_CALL',caller=0x53e6,site=0x53ee,target=0x5868,other_caller=0x50e8,other_site=0x52a8)
 # A named one-past boundary is independently the accepted callback entry.
 # Its zero-size export is a symbolic branch destination, never CODE credit.
 import audio_callback_asm as callbacks
 neighbor=callbacks.document(root,'evidence/reconstructed-asm/resident_callback_617C.json')
 verified=callbacks.verify(root,blob,model,neighbor)
 require(verified['verdict']=='EQUAL_CANDIDATE' and neighbor['original']['start']==0x617c,'independently proved named next callback boundary')
 spans=[];allitems=[]
 for spec in SPECS.values():
  lo,hi=spec['start'],spec['end'];items=contracts.decode(c[lo:hi],lo);es=frame.cfg(items)
  pred=frame.witness(items,lo,es);pred['entry_evidence']=entries[lo]
  allitems+=items;spans.append(dict(start=lo,end=hi,size=hi-lo,sha256=sha256(c[lo:hi]),predicate=pred,boundary_edges=[e for e in es if lo<=e['site']<hi and (e['target'] is None or not lo<=e['target']<hi)]))
 return dict(spans=spans,complete_edges=frame.cfg(allitems),handler_table=[],data_credit=0,unclaimed=[dict(start=a,end=z,reason=why) for a,z,why in [(0x558a,0x5594,'NO_INDEPENDENT_CODE_ENTRY'),(0x57c0,0x57d2,'NO_INDEPENDENT_CODE_ENTRY'),(0x57d2,0x57e4,'RELOCATED_POINTER_WITHOUT_INDEPENDENT_FUNCTION_CONSUMER'),(0x5cc2,0x5cc6,'NO_PROVED_ENTRY_OR_INCOMING_EDGE'),(0x5d74,0x5d78,'NO_PROVED_ENTRY_OR_INCOMING_EDGE'),(0x5d80,0x5d92,'NO_PROVED_ENTRY_OR_INCOMING_EDGE')]])

from audio_driver_asm import code_symbol

def measured_bindings(blob,model,contract,spec):
 lo,hi=spec['start'],spec['end'];items=contracts.decode(payload(blob,model,0)[lo:hi],lo)
 targets={contracts.target(i) for i in items if i['mnemonic'].split('.')[0] in ['bra','bsr','jsr','dbra'] or i['mnemonic'].startswith(('beq','bne','bpl','bmi','bcc','bcs','ble','bhi'))};targets.discard(None)
 span=next(s for s in contract['spans'] if s['start']==lo)
 entries=set(span['predicate'].get('entries',[]))|{e['target'] for e in contract['complete_edges'] if e['target'] is not None and lo<=e['target']<hi and not lo<=e['site']<hi}|{lo}|{t for t in targets if lo<=t<hi}|{r['addend_raw'] for r in contract['handler_table'] if lo<=r['addend_raw']<hi}
 exports=[dict(name=code_symbol(t),offset=t-lo,original=t) for t in sorted(entries)]+[dict(name='_end_'+spec['prefix'],offset=hi-lo,original=None)]
 external_code=[dict(name=code_symbol(t),hunk=0,target=t) for t in sorted(targets) if not lo<=t<=hi]
 rels=[r for r in model['relocations'] if r['source_hunk']==0 and r['source_offset']<hi and lo<r['source_offset']+r['width']]
 require(all(lo<=r['source_offset'] and r['source_offset']+r['width']<=hi for r in rels),'straddling driver relocation')
 require(all(r['width']==4 and r['type']=='HUNK_RELOC32' for r in rels),'driver relocation type/width')
 external_data=[dict(name='_G_h%02d_%04X'%(h,t),hunk=h,target=t) for h,t in sorted(set((r['target_hunk'],r['addend_raw']) for r in rels))]
 long_refs=[dict(field(r),symbol='_G_h%02d_%04X'%(r['target_hunk'],r['addend_raw'])) for r in rels]
 pc=[]
 for i in items:
  t=contracts.target(i)
  if t is not None and not lo<=t<=hi:
   require(i['size']==4 and i['mnemonic'].split('.')[0] in ['bra','bsr','jsr'],'unproved external displacement encoding')
   pc.append(dict(offset=i['offset']+2-lo,width=2,type='PC_RELATIVE_CODE16',symbol=code_symbol(t),hunk=0,target=t,site=i['offset']))
 return exports,external_code,external_data,long_refs,pc


def source_for(blob,model,contract,ident):
 import audio_driver_asm as driver
 spec=SPECS[ident];ex,ec,ed,rels,pc=measured_bindings(blob,model,contract,spec);lo,hi=spec['start'],spec['end'];items=contracts.decode(payload(blob,model,0)[lo:hi],lo)
 lines=['\tfar data','\tdseg']+['\tpublic '+d['name'] for d in ed]+['\tcseg']+['\tpublic '+d['name'] for d in ec+ex]
 labels={}
 for d in ex:labels.setdefault(lo+d['offset'],[]).append(d['name'])
 rs={r['source_offset']:r for r in rels}
 for i in items:
  if i['offset'] in labels:lines.extend(labels[i['offset']])
  m=i['mnemonic'];o=i['operands'];target=contracts.target(i)
  if target is not None and (m.split('.')[0] in ['bra','bsr','jsr','dbra'] or m.startswith(('beq','bne','bpl','bmi','bcc','bcs'))):
   n='_end_'+spec['prefix'] if target==hi else driver.code_symbol(target);o=re.sub(r'\$[0-9a-f]+(?:\(pc\))?$',n,o)
  for site,r in rs.items():
   if i['offset']<=site<i['offset']+i['size']:o=o.replace('$%x.l'%r['addend_raw'],r['symbol']).replace('$%x'%r['addend_raw'],r['symbol'])
  # Manx chooses the measured short local branch from symbolic destinations.
  if m.startswith(('bmi.','bpl.','bcc.','bne.','beq.','bra.','bsr.')):m=m.split('.')[0]
  o=re.sub(r'(\$[0-9a-f]+)\.l',r'\1',o)
  if m=='btst.b' and re.search(r', d[0-7]$',o):m='btst'
  o=o.replace(', ', ',');o=re.sub(r'\((a[0-7]),([ad][0-7]\.w)\)',r'0(\1,\2)',o)
  lines.append('\t'+m+(' '+o if o else ''))
 if hi in labels:lines.extend(labels[hi])
 return ('\n'.join(lines+['\tdseg','\tend',''])).encode('ascii'),(ex,ec,ed,rels,pc)
def commands(batch):
 import audio_frame_calibration as frame
 result=[]
 for spec in SPECS.values():
  p=spec['prefix'];result+=['Old1:bin/as -o '+p+'.o '+p+'.asm >'+p+'-as.log','Old1:bin/as -o bind_'+p+'.o bind_'+p+'.asm >bind_'+p+'-as.log','Old1:bin/ln -m -t -o '+p+'.exe '+p+'.o bind_'+p+'.o >'+p+'-ln.log']
 result+=['Old1:bin/as -o bind_regs.o bind_regs.asm >bind_regs-as.log']
 for n in (4,6):result+=['Old1:bin/cc -a +D reg%d.c >reg%d-cc.log'%(n,n),'Old1:bin/as -o reg%d.o reg%d.asm >reg%d-as.log'%(n,n,n),'Old1:bin/ln -m -t -o reg%d.exe reg%d.o bind_regs.o >reg%d-ln.log'%(n,n,n)]
 for k,opts in enumerate(frame.FLAGS):
  p='frame%d'%k;result+=['Old1:bin/cc -a '+' '.join(opts)+' '+p+'.c >'+p+'-cc.log','Old1:bin/as -o '+p+'.o '+p+'.asm >'+p+'-as.log','Old1:bin/ln -m -t -o '+p+'.exe '+p+'.o bind_regs.o >'+p+'-ln.log']
 for p,opts in [('frame50',''),('frame50s','-ps')]:result+=['Tools2:bin/cc -a '+opts+' '+p+'.c >'+p+'-cc.log','Tools2:bin/as -o '+p+'.o '+p+'.asm >'+p+'-as.log']
 return result

@shared
def producer(root,batch):
 import audio_frame_calibration as frame
 names={x['prefix']+suffix for x in SPECS.values() for suffix in ['.asm']}|{'bind_'+x['prefix']+'.asm' for x in SPECS.values()}|{'reg4.c','reg6.c','bind_regs.asm'}|{'frame%d.c'%k for k in range(len(frame.FLAGS))}|{'frame50.c','frame50s.c'}
 require(set(batch['source_files'])==names,'closed frame batch source inventory')
 expected={n:canonical_path(root,RULES+n).read_bytes() for n in batch['source_files']}
 require(batch['source_files']=={n:sha256(raw) for n,raw in expected.items()},'callback source pins')
 for n in (4,6):require(expected['reg%d.c'%n]==calibration.source(n),'callback C control recipe')
 require(expected['bind_regs.asm']==calibration.BINDER,'callback register binder')
 import audio_frame_calibration as frame
 for n in ['frame%d'%k for k in range(len(frame.FLAGS))]+['frame50','frame50s']:require(expected[n+'.c']==frame.SOURCE,'frame matrix source pins')
 return score.audit_producer(root,batch,expected,commands(batch))
@shared
def control(root,batch,blob,model):
 import audio_frame_calibration as frame
 return dict(register_calibration=calibration.derive(root,blob,model,batch),frame_calibration=frame.derive(root,blob,model,batch),ordinary_c_controls='LINK_FRAMED_VOID_LEAF_NO_LOCALS_REGISTER_VARIABLE_OPTION_MATRIX')

def validate_fact(root,blob,model,contract,fact):
 import audio_driver_asm as driver
 require(fact['id'] in SPECS,'callback identity');spec=SPECS[fact['id']];lo,hi=spec['start'],spec['end'];span=next(s for s in contract['spans'] if s['start']==lo)
 require(set(fact)=={'schema_version','id','oracle_sha256','original','predicate','boundary_edges','prefix','candidate','source','source_sha256','exports','external_code','external_data','relocations','historical_owner','historical_tu','original_filename','binder'},'callback fields; masks/raw carriers reject')
 require(all(type(fact['original'][k]) is int for k in ['hunk','start','end','size']),'frame extent integer types')
 require(fact['schema_version']==4 and type(fact['schema_version']) is int and fact['oracle_sha256']==sha256(blob) and fact['original']==dict(hunk=0,start=lo,end=hi,size=hi-lo,sha256=sha256(payload(blob,model,0)[lo:hi])),'callback whole extent/oracle')
 require(fact['predicate']==span['predicate'] and fact['boundary_edges']==span['boundary_edges'],'callback non-C predicate changed')
 src,(ex,ec,ed,rels,pc)=source_for(blob,model,contract,fact['id'])
 require((fact['exports'],fact['external_code'],fact['external_data'],fact['relocations'])==(ex,ec,ed,rels),'callback named bindings')
 require(fact['prefix']==spec['prefix'] and fact['candidate']==RULES+spec['prefix']+'.asm' and fact['source']=='src/recovered/asm-reconstructed/'+fact['id']+'.asm','callback paths')
 require(fact['historical_owner']==fact['historical_tu']=='UNKNOWN' and fact['original_filename'] is None,'callback provenance')
 require(canonical_path(root,fact['candidate']).read_bytes()==src and fact['source_sha256']==sha256(src),'callback source recipe')
 return src,pc,driver.source_policy(src,fact)

def verify(root,blob,model,fact,batch=None,contract=None,audit=None,cctrl=None):
 require([(h['number'],h['type'],h['node']) for h in model['hunks'][:2]]==[(0,'CODE','resident'),(1,'DATA','resident')],'driver containers')
 batch=document(root,MANIFEST) if batch is None else batch
 audit=producer(root,batch) if audit is None else audit;cctrl=control(root,batch,blob,model) if cctrl is None else cctrl
 contract=derive(blob,model,cctrl['frame_calibration'],root) if contract is None else contract
 require(set(batch)=={'schema_version','profile','facts','fact_sha256','job','request_sha256','receipt_sha256','artifacts','source_files','all_data'} and batch['schema_version']==4 and batch['profile']=='aztec36' and batch['facts']==FACTS and batch['fact_sha256']=={n:sha256(json_bytes(document(root,n))) for n in FACTS},'callback batch schema/pins')
 src,pc,policy=validate_fact(root,blob,model,contract,fact);audit=producer(root,batch) if audit is None else audit;cctrl=control(root,batch,blob,model) if cctrl is None else cctrl
 # Diagnostic bindings never own bytes in the accounting image.
 import audio_driver_asm as driver
 bind,exports,bc,bd=driver.binder_source([e['name'] for e in fact['external_code']],batch['all_data'])
 require(fact['binder']==dict(source='bind_'+fact['prefix']+'.asm',sha256=sha256(bind),exports=exports,CODE=bc,DATA=bd),'diagnostic binder bounds/names')
 require(canonical_path(root,RULES+fact['binder']['source']).read_bytes()==bind,'binder recipe')
 work=root/batch['job']/'sys/work';obj=(work/(fact['prefix']+'.o')).read_bytes();code,refs,structure=aj_parse(obj)
 require(len(code)==fact['original']['size'],'complete CODE size; unsupported encoding is TOOLCHAIN')
 expected_symbols=[dict(name=e['name'],kind=7,attribute=14,offset=0,reference_count=sum(r['symbol']==e['name'] for r in fact['relocations'])) for e in fact['external_data']]+[dict(name=e['name'],kind=7,attribute=8,offset=0,reference_count=None) for e in fact['external_code']]+[dict(name=e['name'],kind=2,attribute=8,offset=e['offset'],reference_count=None) for e in fact['exports']]
 require(structure['symbols']==expected_symbols,'complete AJ symbol/object structure')
 names=[s['name'] for s in expected_symbols];wanted=[]
 for r in fact['relocations']:wanted.append(dict(offset=r['source_offset']-fact['original']['start'],width=4,type='HUNK_RELOC32',symbol=r['symbol'],symbol_index=names.index(r['symbol']),addend=0))
 for r in pc:wanted.append(dict(offset=r['offset'],width=2,type=r['type'],symbol=r['symbol'],symbol_index=names.index(r['symbol']),addend=0))
 wanted.sort(key=lambda r:r['offset']);require(refs==wanted,'exhaustive named AJ references')
 linked=(work/(fact['prefix']+'.exe')).read_bytes();lm=hunk_parse(linked);actual=payload(linked,lm,0);sm=symbol_map((work/(fact['prefix']+'.sym')).read_text());size=len(code);rounded=lambda n:(n+3)//4*4
 require([(h['number'],h['type'],h['allocated_size'],h['initialized_size']) for h in lm['hunks']]==[(0,'CODE',rounded(size+bc),rounded(size+bc)),(1,'DATA',rounded(bd),rounded(bd)),(2,'BSS',4,0)],'complete linked hunk structure')
 expected={(0,'__H0_org'):0,(0,'__H0_end'):rounded(size+bc),(0,'.begin'):size,(1,'__H1_org'):0,(1,'__H1_end'):rounded(bd),(1,'_C_handlers'):len(batch['all_data'])*4,(2,'__H2_org'):rounded(bd),(2,'__H2_end'):rounded(bd)}
 expected.update({(0,e['name']):e['offset'] for e in fact['exports']});expected.update({(e['hunk'],e['name']):e['offset']+(size if e['hunk']==0 else 0) for e in exports})
 require(sm==expected,'complete linked named map')
 require(actual[size:size+bc]==b'\x4e\x75'*(bc//2) and actual[size+bc:]==bytes(rounded(size+bc)-size-bc) and payload(linked,lm,1)==bytes(rounded(bd)),'diagnostic stub/data/alignment structure')
 candidate_relocs=[dict(source_hunk=0,source_offset=r['offset'],target_hunk=1,addend_raw=sm[(1,r['symbol'])],type='HUNK_RELOC32',width=4) for r in refs if r['width']==4]
 require([field(r) for r in lm['relocations']]==candidate_relocs,'complete linked relocation sites/types/widths')
 original=payload(blob,model,0)[fact['original']['start']:fact['original']['end']];normalized=bytearray(actual[:size]);bindings=[];cursor=0
 for r in refs:
  p=r['offset'];n=r['width'];require(code[cursor:p]==actual[cursor:p]==original[cursor:p] and code[p:p+n]==bytes(n),'ordinary CODE / zero external addend')
  t=next(e for e in fact['external_code']+fact['external_data'] if e['name']==r['symbol'])
  if n==2:
   require(p+int.from_bytes(actual[p:p+2],'big',signed=True)==sm[(0,r['symbol'])],'PC16 named candidate target');value=t['target']-(fact['original']['start']+p);require(-(1<<15)<=value<(1<<15),'original PC16 range');raw=value.to_bytes(2,'big',signed=True)
  else:
   require(int.from_bytes(actual[p:p+4],'big')==sm[(1,r['symbol'])],'long named candidate target');raw=t['target'].to_bytes(4,'big')
  require(original[p:p+n]==raw,'original named payload');normalized[p:p+n]=raw;bindings.append(dict(r,original_hunk=t['hunk'],original_target=t['target'],candidate_hunk=0 if n==2 else 1,candidate_target=sm[(0 if n==2 else 1,r['symbol'])]));cursor=p+n
 require(code[cursor:]==actual[cursor:size]==original[cursor:] and bytes(normalized)==original,'terminal/whole CODE comparison')
 return dict(id=fact['id'],verdict='EQUAL_CANDIDATE',category='RECONSTRUCTED_ASM',state='FUNCTION_CODE_MATCH',span=fact['original'],non_c_predicate=fact['predicate'],boundary_edges=fact['boundary_edges'],fact_sha256=sha256(json_bytes(fact)),manifest=MANIFEST,source_sha256=sha256(src),source_policy=policy,object_structure=structure,named_relocation_bindings=bindings,ordinary_bytes_compared=size-sum(r['width'] for r in refs),named_field_bytes=sum(r['width'] for r in refs),linked_sha256=sha256(linked),producer=audit,c_compatible_control={k:v for k,v in cctrl.items() if k not in ['register_calibration','frame_calibration']},data_credit=0,historical_owner='UNKNOWN',historical_object_membership='UNKNOWN',natural_root_layout_proof=False,source_acceptance=False,proof_level=None,verifier_identity={n:sha256(canonical_path(root,'tools/'+n).read_bytes()) for n in ['audio_frameless_asm.py','audio_frame_calibration.py','audio_driver_asm.py','audio_driver_contracts.py','audio_driver_objects.py','check_data_contribution.py','hunk.py','repo_paths.py','audio_register_calibration.py']},register_calibration=cctrl['register_calibration'],frame_calibration=cctrl['frame_calibration'])



def rows(root,blob,model,analysis,ledger):
 entries={k:v for k,v in ledger.get(MAP,{}).items() if k in SPECS}
 if not entries:return []
 batch=document(root,MANIFEST);audit=producer(root,batch);cctrl=control(root,batch,blob,model);contract=derive(blob,model,cctrl['frame_calibration'],root);result=[]
 for name in FACTS:
  fact=document(root,name);ident=fact['id']
  if ident not in entries:continue
  report=verify(root,blob,model,fact,batch,contract,audit,cctrl);item=entries[ident];dest='recovery/proofs/asm-reconstructed/'+ident+'.json'
  require(set(item)=={'state','fact','source','source_sha256','proof','proof_sha256'} and item['state']=='FUNCTION_CODE_MATCH' and item['fact']==name and item['source']==fact['source'] and item['proof']==dest,'driver ownership identity')
  src=canonical_path(root,item['source']).read_bytes();raw=canonical_path(root,item['proof']).read_bytes();proof=json.loads(raw)
  require(src==canonical_path(root,fact['candidate']).read_bytes() and sha256(src)==item['source_sha256']==fact['source_sha256'] and sha256(raw)==item['proof_sha256'],'canonical driver source/proof')
  require(set(proof)=={'fact','comparison','regression'} and proof['regression'].get('passed') is True,'driver shared regression receipt')
  comparable=lambda r:{k:v for k,v in r.items() if k not in ['verifier_identity','register_calibration','frame_calibration']}
  require(proof['fact']==fact and isinstance(proof['comparison'].get('verifier_identity'),dict) and proof['comparison']['verifier_identity'] and comparable(proof['comparison'])==comparable(report),'canonical driver proof no longer rederives')
  for rec in ledger.get('functions',{}).values():
   o=rec['evidence_extent'];require(o['hunk']!=0 or o['end']<=fact['original']['start'] or o['start']>=fact['original']['end'],'driver overlaps canonical C')
  for other in ['mixed_source_objects','dead_code_functions','behavioral_functions']:
   for rec in ledger.get(other,{}).values():
    p=document(root,rec['proof']);o=p.get('complete_extent') or p.get('evidence_extent') or p.get('original')
    if o:require(o['hunk']!=0 or o['end']<=fact['original']['start'] or o['start']>=fact['original']['end'],'driver overlaps another source route')
  result.append(dict(report,acceptance=True,source_acceptance=True,proof_level='FUNCTION_CODE_MATCH',source=fact['source'],proof=dest))
 # All source categories are checked globally again by hybrid overlap accounting.
 return result


def contributions(root,records):
 result=[]
 for r in records:
  if not r.get('acceptance'):continue
  spec=SPECS[r['id']];raw=(root/r['producer']['job']/('sys/work/'+spec['prefix']+'.o')).read_bytes();code,refs,_=aj_parse(raw);out=bytearray(code);relocations=[]
  require(len(refs)==len(r['named_relocation_bindings']),'complete contribution references')
  for x,b in zip(refs,r['named_relocation_bindings']):
   require(all(x[k]==b[k] for k in x),'contribution named identity');p=x['offset'];n=x['width']
   if n==2:out[p:p+2]=(b['original_target']-(r['span']['start']+p)).to_bytes(2,'big',signed=True)
   else:out[p:p+4]=b['original_target'].to_bytes(4,'big');relocations.append(dict(source_offset=r['span']['start']+p,target_hunk=b['original_hunk'],type='HUNK_RELOC32',width=4,addend_raw=b['original_target']))
  # AJ references occur in instruction order. Original HUNK relocation
  # groups occur in target-hunk order, which differs for the CODE-data base.
  # Reorder the source-derived identities by the freshly validated fact; never
  # drop a field or replace its site/type/width/target to satisfy accounting.
  original=document(root,'evidence/reconstructed-asm/'+r['id']+'.json')['relocations']
  fields=('source_offset','target_hunk','type','width','addend_raw')
  expected=[{k:x[k] for k in fields} for x in original]
  by_site={x['source_offset']:x for x in relocations}
  require(len(by_site)==len(relocations)==len(expected) and all(by_site.get(x['source_offset'])==x for x in expected),'complete contribution relocation identities')
  relocations=[by_site[x['source_offset']] for x in expected]
  result.append(dict(id=r['id'],hunk=0,start=r['span']['start'],end=r['span']['end'],category='RECONSTRUCTED_ASM',bytes=bytes(out),relocations=relocations))
 return result



def input_identity(root):
 root=Path(root);p=canonical_path(root,MANIFEST)
 if not p.exists():return {str(p):None}
 batch=document(root,MANIFEST);names={MANIFEST,*FACTS};
 from audio_frame_calibration import SUPPLEMENTAL
 extra=document(root,SUPPLEMENTAL);names.add(SUPPLEMENTAL);names.update(extra['pins'])
 rom_path=root/extra['rom36b_job']/'dosbox-request.json'
 rom_request=json.loads(rom_path.read_bytes()) if rom_path.is_file() else {}
 if rom_request:names.add(rom_request['compiler'])
 names.add('evidence/toolchain/aztec-3.20a.json')
 for q in ['amiga320_job','rom36b_job']:
  request_path=root/extra[q]/'request.json'
  if request_path.is_file():
   supplemental_request=json.loads(request_path.read_bytes());names.update(p['path'] for p in supplemental_request['pinned_inputs'])
 names.update(RULES+n for n in batch['source_files']);job=batch['job']
 names.update(job+'/'+n for n in ['request.json','result.json','worker.uae','sys/s/startup-sequence','kick.rom']);names.update(job+'/sys/work/'+n for n in batch['artifacts'])
 request=json.loads(candidate_path(root,root/job/'request.json').read_bytes());names.update(p['path'] for p in request['pinned_inputs']);lock=document(root,'toolchain/candidate-lock.json');names.add(lock['archive'])
 for folder in ['c','l','libs','devs']:names.update(p.relative_to(root).as_posix() for p in active_files(root/job/'sys'/folder))
 names.update(['evidence/toolchain/aztec-3.6a.json','evidence/toolchain/aztec-5.0a.json','toolchain/candidate-lock.json'])
 lp=canonical_path(root,'recovery/ledger.json');ledger=document(root,'recovery/ledger.json') if lp.exists() else {}
 names.update(['evidence/functions/ledger.json','recovery/ledger.json'])
 for section in ['functions','dead_code_functions','behavioral_functions']:
  for item in ledger.get(section,{}).values():names.update([item['source'],item['proof']])
 for k,item in ledger.get(MAP,{}).items():
  if k in SPECS:names.update([item['source'],item['proof'],item['fact']])
 def path(n):return candidate_path(root,root/n) if n.startswith('build/worker-jobs/') else canonical_path(root,n)
 return {**{str(path(n)):sha256(path(n).read_bytes()) if path(n).exists() else None for n in sorted(names)},request['emulator']:sha256(Path(request['emulator']).read_bytes()),**({rom_request['runner']:sha256(Path(rom_request['runner']).read_bytes()) if Path(rom_request['runner']).is_file() else None} if rom_request else {})}
