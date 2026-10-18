"""Second reconstructed-ASM batch: independently checked audio register ABI spans."""
from names import read_source, source_path as source_file
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

MANIFEST='evidence/reconstructed-asm/batch-0002.json'
RULES='evidence/rules/asm-reconstructed/batch-0002/'
SPECS={'resident_driver_%04X'%a:dict(start=a,end=z,prefix=p) for a,z,p in contracts.SPANS}
FACTS=['evidence/reconstructed-asm/'+i+'.json' for i in SPECS]
MAP='reconstructed_asm'
BATCH2_SPECS=dict(SPECS)
CONTROL=b'''extern int (*C_handlers[44])();
int C_dispatch(p, i)
char *p;
unsigned i;
{
    if (i <= 43) return (*C_handlers[i])(*p++);
    return 0;
}
'''


def document(root,name):return json.loads(canonical_path(root,name).read_bytes())
def code_symbol(t):return '_resident_asm_%04X'%t if t in [0x559e,0x59a4] else '_recon_h00_%04X'%t

def measured_bindings(blob,model,contract,spec):
 lo,hi=spec['start'],spec['end'];items=contracts.decode(payload(blob,model,0)[lo:hi],lo)
 targets={contracts.target(i) for i in items if i['mnemonic'].split('.')[0] in ['bra','bsr','jsr','dbra'] or i['mnemonic'].startswith(('beq','bne','bpl','bmi','bcc','bcs','ble','bhi'))};targets.discard(None)
 span=next(s for s in contract['spans'] if s['start']==lo)
 entries=set(span['predicate'].get('entries',[]))|{e['target'] for e in contract['complete_edges'] if e['target'] is not None and lo<=e['target']<hi and not lo<=e['site']<hi}|{lo}|{t for t in targets if lo<=t<hi}|{r['addend_raw'] for r in contract['handler_table'] if lo<=r['addend_raw']<hi}
 exports=[dict(name=code_symbol(t),offset=t-lo,original=t) for t in sorted(entries)]+[dict(name='_end_'+spec['prefix'],offset=hi-lo,original=None)]
 external_code=[dict(name=code_symbol(t),hunk=0,target=t) for t in sorted(targets) if not lo<=t<hi]
 rels=[r for r in model['relocations'] if r['source_hunk']==0 and r['source_offset']<hi and lo<r['source_offset']+r['width']]
 require(all(lo<=r['source_offset'] and r['source_offset']+r['width']<=hi for r in rels),'straddling driver relocation')
 require(all(r['width']==4 and r['type']=='HUNK_RELOC32' for r in rels),'driver relocation type/width')
 external_data=[dict(name='_G_h%02d_%04X'%(h,t),hunk=h,target=t) for h,t in sorted(set((r['target_hunk'],r['addend_raw']) for r in rels))]
 long_refs=[dict(field(r),symbol='_G_h%02d_%04X'%(r['target_hunk'],r['addend_raw'])) for r in rels]
 pc=[]
 for i in items:
  t=contracts.target(i)
  if t is not None and not lo<=t<hi:
   require(i['size']==4 and i['mnemonic'].split('.')[0] in ['bra','bsr','jsr'],'unproved external displacement encoding')
   pc.append(dict(offset=i['offset']+2-lo,width=2,type='PC_RELATIVE_CODE16',symbol=code_symbol(t),hunk=0,target=t,site=i['offset']))
 return exports,external_code,external_data,long_refs,pc


def source_policy(raw,fact):
 require(raw and b'\0' not in raw and b'\r' not in raw and raw.endswith(b'\n'),'ASCII LF mnemonic source only')
 text=raw.decode('ascii');segment='CODE';public=[];labels=[];mnemonics=0;equ=[]
 allowed={'tst','move','movea','moveq','movem','clr','lea','lsl','lsr','asl','add','adda','addq','sub','subq','cmp','and','andi','or','ori','eor','eori','btst','bset','bclr','bra','bsr','beq','bne','bpl','bmi','bcc','bcs','ble','bhi','dbra','rts','jsr','jmp','swap','ext'}
 for line in text.splitlines():
  require(line and ';' not in line and '"' not in line and "'" not in line,'opaque/comment/macro carrier rejects')
  words=line.strip().split(None,1);op=words[0];arg=words[1] if len(words)>1 else ''
  if not line[0].isspace():
   if len(words)==2:
    require(op=='_G_h01_27E4_A4' and arg=='equ -22554','unproved EQU carrier');equ.append(op)
   else:require(re.fullmatch(r'_[A-Za-z0-9_]+',op),'symbolic labels only');labels.append(op)
   continue
  if op=='far':require(arg=='data','only measured far data');continue
  if op in ['dseg','cseg']:require(not arg,'segment directive operands');segment='DATA' if op=='dseg' else 'CODE';continue
  if op=='public':
   require(re.fullmatch(r'_[A-Za-z0-9_]+',arg),'one independently named public per line');public.append((arg,segment));continue
  if op=='end':require(not arg,'end directive');continue
  require(segment=='CODE' and op.split('.')[0] in allowed,'dc/ds/incbin/opaque CODE carrier rejects')
  require(not re.search(r'\b(?:include|incbin|macro|dc|ds|org)\b',arg,re.I),'opaque source operand');mnemonics+=1
 expected=[(e['name'],'DATA') for e in fact['external_data']]+[(e['name'],'CODE') for e in fact['external_code']]+[(e['name'],'CODE') for e in fact['exports']]
 require(public==expected and len(labels)==len(set(labels)) and set(labels)=={e['name'] for e in fact['exports']},'complete named source/label inventory')
 require(mnemonics>0 and len(equ)==(1 if fact['prefix']=='dispatch' else 0),'independent A4 EQU/source extent')
 return dict(policy='MNEMONICS_NAMED_LABELS_AND_TARGETS_ONLY',mnemonics=mnemonics,source_sha256=sha256(raw))


def commands():
 result=[]
 for s in BATCH2_SPECS.values():
  p=s['prefix'];result+=['Old1:bin/as -o '+p+'.o '+p+'.asm >'+p+'-as.log','Old1:bin/as -o bind_'+p+'.o bind_'+p+'.asm >bind_'+p+'-as.log','Old1:bin/ln -m -t -o '+p+'.exe '+p+'.o bind_'+p+'.o >'+p+'-ln.log']
 result+=['Old1:bin/as -o bind_control.o bind_control.asm >bind_control-as.log','Old1:bin/cc -a +D cctrl.c >cctrl-cc.log','Old1:bin/as -o cctrl.o cctrl.asm >cctrl-as.log','Old1:bin/ln -m -t -o cctrl.exe cctrl.o bind_control.o >cctrl-ln.log']
 result+=['Old1:bin/as -o bind_regs.o bind_regs.asm >bind_regs-as.log']
 for n in [4,6]:result+=['Old1:bin/cc -a +D reg%d.c >reg%d-cc.log'%(n,n),'Old1:bin/as -o reg%d.o reg%d.asm >reg%d-as.log'%(n,n,n),'Old1:bin/ln -m -t -o reg%d.exe reg%d.o bind_regs.o >reg%d-ln.log'%(n,n,n)]
 return result


def binder_source(code,data):
 lines=['\tpublic .begin','.begin','\trts'];exports=[]
 for n in sorted(code):lines+=['\tpublic '+n,n,'\trts'];exports.append(dict(name=n,offset=2+2*len(exports),hunk=0))
 lines+=['\tdseg'];d=0
 for n in data:lines+=['\tpublic '+n,n,'\tds.l 1'];exports.append(dict(name=n,offset=d,hunk=1));d+=4
 lines+=['\tpublic _C_handlers','_C_handlers','\tds.l 44','\tend']
 return ('\n'.join(lines)+'\n').encode('ascii'),exports,2+2*len(code),d+176


@shared
def producer(root,batch):
 """Full retained producer graph; no embedded job receipts in curated evidence."""
 import check_data_contribution as score
 job=candidate_path(root,root/batch['job']);work=job/'sys/work'
 require(re.fullmatch(r'build/worker-jobs/sol-audio-asm-[A-Za-z0-9_-]+',batch['job']),'producer job path')
 request=document_job(job/'request.json');receipt=document_job(job/'result.json')
 require(sha256((job/'request.json').read_bytes())==batch['request_sha256'] and sha256((job/'result.json').read_bytes())==batch['receipt_sha256'],'producer SHA pins')
 require(receipt['request']==request and receipt['all_steps_succeeded'] is True,'complete successful producer')
 expected=[dict(index=i,command=c,returncode_file='step-%02d.rc'%i) for i,c in enumerate(commands())]
 require(request['steps']==expected and receipt['steps']==[dict(s,returncode=0) for s in expected],'exact command recipe/statuses')
 require(request['source_files']==[dict(path=n,sha256=e['sha256']) for n,e in sorted(batch['source_files'].items())],'source inventory')
 for n,e in batch['source_files'].items():
  require(set(e)=={'path','sha256'} and Path(n).name==n and e['path']==RULES+n,'source recipe path');raw=canonical_path(root,e['path']).read_bytes()
  require(sha256(raw)==e['sha256'] and (work/n).read_bytes()==raw,'unchanged producer source')
 require((work/'cctrl.c').read_bytes()==CONTROL,'independent C-compatible dispatcher recipe')
 pins=[]
 for version in ['5.0a','3.6a']:
  inv=document(root,'evidence/toolchain/aztec-'+version+'.json')
  for disk in inv['disks']:
   if disk['status']!='VALIDATED':continue
   manifest=disk['filesystem_manifest'] if version=='5.0a' else disk['manifest'];volume=disk['volume'] if version=='5.0a' else manifest['volume']
   pins += [dict(path='toolchain/installed/aztec-'+version+'/'+volume+'/'+e['path'],sha256=e['sha256']) for e in manifest['entries'] if e['kind']=='file']
 require(request['pinned_inputs']==pins,'full tool/header/library inventory')
 for p in pins:require(sha256(canonical_path(root,p['path']).read_bytes())==p['sha256'],'pinned tool input')
 lock=document(root,'toolchain/candidate-lock.json')
 require(request['archive_sha256']==lock['sha256']==sha256(canonical_path(root,lock['archive']).read_bytes()),'archive')
 require(request['rom_sha256']==next(m['sha256'] for m in lock['members'] if m['path']=='Kick30.rom'),'ROM')
 require(sha256(Path(request['emulator']).read_bytes())==request['emulator_sha256'],'emulator')
 for n,k in [('kick.rom','rom_sha256'),('worker.uae','config_sha256'),('sys/s/startup-sequence','guest_script_sha256')]:require(sha256((job/n).read_bytes())==request[k],'environment pin')
 old=score.COMMANDS
 try:score.COMMANDS=commands();score.environment(root,job)
 finally:score.COMMANDS=old
 artifact={a['path']:a['sha256'] for a in receipt['artifacts']}
 require(len(artifact)==len(receipt['artifacts']) and artifact==batch['artifacts'] and set(artifact)=={p.relative_to(work).as_posix() for p in active_files(work)},'complete artifact inventory')
 for a in receipt['artifacts']:
  require(Path(a['path']).name==a['path'],'artifact path');raw=(work/a['path']).read_bytes();require(len(raw)==a['size'] and sha256(raw)==a['sha256'],'artifact hash')
 require((work/'done.txt').read_bytes().strip()==b'done' and all((work/s['returncode_file']).read_bytes().strip()==b'0' for s in expected),'completion markers')
 return dict(job=batch['job'],request_sha256=batch['request_sha256'],receipt_sha256=batch['receipt_sha256'],artifact_sha256=artifact,audit='FULL_PINNED_PRODUCER_GRAPH_CHECKED')


def document_job(p):return json.loads(p.read_bytes())

@shared
def control(root,batch,blob,model):
 measured=calibration.derive(root,blob,model,batch)
 work=root/batch['job']/'sys/work';raw=(work/'cctrl.o').read_bytes();code,refs,structure=aj_parse(raw,False)
 image=(work/'cctrl.exe').read_bytes();model=hunk_parse(image);linked=payload(image,model,0);sm=symbol_map((work/'cctrl.sym').read_text())
 require(sm[(0,'_C_dispatch')]==0 and len(code)>0,'pinned C control entry')
 require([s['name'] for s in structure['symbols']]==['_C_dispatch','_C_handlers','.begin'],'complete C control symbols')
 require(len(refs)==1 and refs[0]['type']=='HUNK_RELOC32' and refs[0]['symbol']=='_C_handlers','C control external pointer array')
 bind,be,bc,bd=binder_source([],batch['all_data']);require((work/'bind_control.asm').read_bytes()==bind,'C control binder recipe')
 require([(h['type'],h['initialized_size']) for h in model['hunks']]==[('CODE',(len(code)+bc+3)//4*4),('DATA',(bd+3)//4*4),('BSS',0)],'complete control link structure')
 require(payload(image,model,1)==bytes((bd+3)//4*4),'control harness DATA')
 p=refs[0]['offset'];require([field(r) for r in model['relocations']]==[dict(source_hunk=0,source_offset=p,target_hunk=1,addend_raw=sm[(1,'_C_handlers')],type='HUNK_RELOC32',width=4)],'control relocation inventory');copy=bytearray(linked[:len(code)]);require(int.from_bytes(copy[p:p+4],'big')==sm[(1,'_C_handlers')],'C control named binding');copy[p:p+4]=bytes(4);require(bytes(copy)==code,'whole C control object/link')
 ins=contracts.decode(linked[:len(code)],0)
 require(ins[0]['mnemonic']=='link.w' and any(i['mnemonic']=='jsr' and i['operands']=='(a1)' for i in ins),'ordinary compiled C frame/indirect-call control')
 try:contracts.signature(ins)
 except Exception as e:
  from common import FormatError
  require(isinstance(e,FormatError),'unexpected control failure');reason=str(e)
 else:require(False,'C-compatible dispatcher incorrectly accepted')
 checks=contracts.control_rejections(ins,measured);require(not any(checks[k] for k in checks if k!='bank_writes'),'compiled C dispatcher satisfies a forbidden non-C predicate')
 return dict(register_calibration=measured,rejected_predicates=checks,verdict='C_COMPATIBLE_DISPATCHER_REJECTED',source_sha256=sha256(CONTROL),object_sha256=sha256(raw),linked_sha256=sha256(image),code_size=len(code),reason=reason,has_stack_frame=True,indirect_call=True,data_credit=0)


def validate_fact(root,blob,model,contract,fact):
 require(fact['id'] in SPECS,'unsupported driver span');spec=SPECS[fact['id']];lo,hi=spec['start'],spec['end'];span=next(s for s in contract['spans'] if s['start']==lo)
 require(set(fact)=={'schema_version','id','oracle_sha256','original','predicate','boundary_edges','prefix','candidate','source','source_sha256','exports','external_code','external_data','relocations','historical_owner','historical_tu','original_filename','binder'},'driver fact schema; masks/opaque fields reject')
 require(type(fact['schema_version']) is int and fact['schema_version']==2 and fact['prefix']==spec['prefix'] and fact['oracle_sha256']==sha256(blob),'stale driver oracle/fact')
 require(fact['original']==dict(hunk=0,start=lo,end=hi,size=hi-lo,sha256=sha256(payload(blob,model,0)[lo:hi])) and all(type(fact['original'][k]) is int for k in ['hunk','start','end','size']),'complete whole contiguous driver span')
 require(json_bytes(fact['predicate'])==json_bytes(span['predicate']) and json_bytes(fact['boundary_edges'])==json_bytes(span['boundary_edges']),'stale per-span predicate/boundary fact')
 require(fact['historical_owner']==fact['historical_tu']=='UNKNOWN' and fact['original_filename'] is None,'historical provenance unsupported')
 require(fact['candidate']==RULES+spec['prefix']+'.asm' and fact['source']=='src/recovered/asm-reconstructed/'+fact['id']+'.asm','driver source paths')
 ex,ec,ed,rels,pc=measured_bindings(blob,model,contract,spec)
 require(json_bytes((fact['exports'],fact['external_code'],fact['external_data'],fact['relocations']))==json_bytes((ex,ec,ed,rels)),'unnamed/masked/partial target bindings')
 source=canonical_path(root,fact['candidate']).read_bytes();require(sha256(source)==fact['source_sha256'],'source hash');policy=source_policy(source,fact)
 return source,pc,policy


def verify(root,blob,model,fact,batch=None,contract=None,audit=None,cctrl=None):
 require([(h['number'],h['type'],h['node']) for h in model['hunks'][:2]]==[(0,'CODE','resident'),(1,'DATA','resident')],'driver containers')
 batch=document(root,MANIFEST) if batch is None else batch
 audit=producer(root,batch) if audit is None else audit;cctrl=control(root,batch,blob,model) if cctrl is None else cctrl
 contract=contracts.derive(blob,model,cctrl['register_calibration']) if contract is None else contract
 require(set(batch)=={'schema_version','profile','facts','fact_sha256','job','request_sha256','receipt_sha256','artifacts','source_files','all_data'},'batch0002 schema')
 require(batch['schema_version']==2 and batch['profile']=='aztec36' and batch['facts']==FACTS and batch['fact_sha256']=={n:sha256(json_bytes(document(root,n))) for n in FACTS},'batch0002 complete fact pins')
 src,pc,policy=validate_fact(root,blob,model,contract,fact);audit=producer(root,batch) if audit is None else audit;cctrl=control(root,batch,blob,model) if cctrl is None else cctrl
 # Diagnostic bindings never own bytes in the accounting image.
 bind,exports,bc,bd=binder_source([e['name'] for e in fact['external_code']],batch['all_data'])
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
 return dict(id=fact['id'],verdict='EQUAL_CANDIDATE',category='RECONSTRUCTED_ASM',state='FUNCTION_CODE_MATCH',span=fact['original'],non_c_predicate=fact['predicate'],boundary_edges=fact['boundary_edges'],fact_sha256=sha256(json_bytes(fact)),manifest=MANIFEST,source_sha256=sha256(src),source_policy=policy,object_structure=structure,named_relocation_bindings=bindings,ordinary_bytes_compared=size-sum(r['width'] for r in refs),named_field_bytes=sum(r['width'] for r in refs),linked_sha256=sha256(linked),producer=audit,c_compatible_control={k:v for k,v in cctrl.items() if k!='register_calibration'},data_credit=0,historical_owner='UNKNOWN',historical_object_membership='UNKNOWN',natural_root_layout_proof=False,source_acceptance=False,proof_level=None,verifier_identity={n:sha256(canonical_path(root,'tools/'+n).read_bytes()) for n in ['audio_driver_asm.py','audio_driver_contracts.py','audio_driver_objects.py','check_data_contribution.py','hunk.py','repo_paths.py','audio_register_calibration.py']},register_calibration=cctrl['register_calibration'])


def rows(root,blob,model,analysis,ledger):
 import audio_callback_asm as callback
 extra=callback.rows(root,blob,model,analysis,ledger)
 import audio_frameless_asm as frameless
 extra+=frameless.rows(root,blob,model,analysis,ledger)
 entries={k:v for k,v in ledger.get(MAP,{}).items() if k in BATCH2_SPECS}
 if not entries:return extra
 batch=document(root,MANIFEST);audit=producer(root,batch);cctrl=control(root,batch,blob,model);contract=contracts.derive(blob,model,cctrl['register_calibration']);result=[]
 for name in FACTS:
  fact=document(root,name);ident=fact['id']
  if ident not in entries:continue
  report=verify(root,blob,model,fact,batch,contract,audit,cctrl);item=entries[ident];dest='recovery/proofs/asm-reconstructed/'+ident+'.json'
  require(set(item)=={'state','fact','source','source_sha256','proof','proof_sha256'} and item['state']=='FUNCTION_CODE_MATCH' and item['fact']==name and item['source']==fact['source'] and item['proof']==dest,'driver ownership identity')
  src=read_source(root, item['source'], names_root=None);raw=canonical_path(root,item['proof']).read_bytes();proof=json.loads(raw)
  require(src==canonical_path(root,fact['candidate']).read_bytes() and sha256(src)==item['source_sha256']==fact['source_sha256'] and sha256(raw)==item['proof_sha256'],'canonical driver source/proof')
  require(set(proof)=={'fact','comparison','regression'} and proof['regression'].get('passed') is True,'driver shared regression receipt')
  comparable=lambda r:{k:v for k,v in r.items() if k not in ['verifier_identity','register_calibration']}
  require(proof['fact']==fact and isinstance(proof['comparison'].get('verifier_identity'),dict) and proof['comparison']['verifier_identity'] and comparable(proof['comparison'])==comparable(report),'canonical driver proof no longer rederives')
  for rec in ledger.get('functions',{}).values():
   o=rec['evidence_extent'];require(o['hunk']!=0 or o['end']<=fact['original']['start'] or o['start']>=fact['original']['end'],'driver overlaps canonical C')
  for other in ['mixed_source_objects','dead_code_functions']:
   for rec in ledger.get(other,{}).values():
    p=document(root,rec['proof']);o=p.get('complete_extent') or p.get('evidence_extent') or p.get('original')
    if o:require(o['hunk']!=0 or o['end']<=fact['original']['start'] or o['start']>=fact['original']['end'],'driver overlaps another source route')
  result.append(dict(report,acceptance=True,source_acceptance=True,proof_level='FUNCTION_CODE_MATCH',source=fact['source'],proof=dest))
 # All source categories are checked globally again by hybrid overlap accounting.
 return result+extra


def contributions(root,records):
 result=[]
 for r in records:
  if not r.get('acceptance'):continue
  if r['id'].startswith('resident_frameless_'):
   import audio_frameless_asm as frameless
   result.extend(frameless.contributions(root,[r]));continue
  if r['id'] not in BATCH2_SPECS:
   import audio_callback_asm as callback
   result.extend(callback.contributions(root,[r]));continue
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
 batch=document(root,MANIFEST);names={MANIFEST,*FACTS};names.update(e['path'] for e in batch['source_files'].values());job=batch['job']
 names.update(job+'/'+n for n in ['request.json','result.json','worker.uae','sys/s/startup-sequence','kick.rom']);names.update(job+'/sys/work/'+n for n in batch['artifacts'])
 request=document_job(candidate_path(root,root/job/'request.json'));names.update(p['path'] for p in request['pinned_inputs']);lock=document(root,'toolchain/candidate-lock.json');names.add(lock['archive'])
 for folder in ['c','l','libs','devs']:names.update(p.relative_to(root).as_posix() for p in active_files(root/job/'sys'/folder))
 names.update(['evidence/toolchain/aztec-3.6a.json','evidence/toolchain/aztec-5.0a.json','toolchain/candidate-lock.json'])
 lp=canonical_path(root,'recovery/ledger.json');ledger=document(root,'recovery/ledger.json') if lp.exists() else {}
 names.update(['evidence/functions/ledger.json','recovery/ledger.json'])
 for section in ['functions','dead_code_functions']:
  for item in ledger.get(section,{}).values():names.update([item['source'],item['proof']])
 for k,item in ledger.get(MAP,{}).items():
  if k in SPECS:names.update([item['source'],item['proof'],item['fact']])
 def path(n):return candidate_path(root,root/n) if n.startswith('build/worker-jobs/') else canonical_path(root,n)
 return {**{str(path(n)):sha256((read_source(root, path(n), names_root=None) if n.startswith('src/') else path(n).read_bytes())) if (source_file(root, path(n)) if n.startswith('src/') else path(n)).exists() else None for n in sorted(names)},request['emulator']:sha256(Path(request['emulator']).read_bytes()),**(__import__('audio_frameless_asm').input_identity(root) if canonical_path(root,__import__('audio_frameless_asm').MANIFEST).exists() else {}),**(__import__('audio_callback_asm').input_identity(root) if canonical_path(root,__import__('audio_callback_asm').MANIFEST).exists() else {})}

# Extend ownership recognition without changing batch0002 producer recipes.
from audio_frameless_asm import SPECS as FRAMELESS_SPECS
SPECS.update(FRAMELESS_SPECS)
from audio_callback_asm import SPECS as CALLBACK_SPECS
SPECS.update(CALLBACK_SPECS)
