"""Independently bounded graphics register bridge, never library provenance."""
import json
from pathlib import Path
from common import require,sha256,json_bytes
from repo_paths import canonical_path,candidate_path,active_files
from audio_sequence_data import payload,field
from audio_driver_objects import parse as aj_parse
from hunk import parse as hunk_parse
from overlay_experiment import symbols as symbol_map
ID='resident_glue_4692'
MAP='reconstructed_asm'
FACT='evidence/reconstructed-asm/'+ID+'.json'
FACTS=[FACT]
MANIFEST='evidence/reconstructed-asm/batch-glue-4692.json'
RULES='evidence/rules/asm-reconstructed/glue-4692/'
SOURCE='src/recovered/asm-reconstructed/'+ID+'.asm'
SPECS={ID:dict(start=0x4692,end=0x46ce,prefix='glue')}
REGISTERS=['a0','d0','d1','a1','d2','d3','d4','d5','d6','a2']
COMMANDS=['Old1:bin/as -o glue.o glue.asm >glue-as.log','Old1:bin/as -o bind.o bind.asm >bind-as.log','Old1:bin/ln -m -t -o glue.exe glue.o bind.o >glue-ln.log']
ASM=b'''\tfar data
\tdseg
\tpublic _G_h01_5374
\tcseg
\tpublic _F_h00_4692
_F_h00_4692
\tmovem.l d4-d6/a2-a6,-(sp)
\tmovea.l 36(sp),a0
\tmove.l 40(sp),d0
\tmove.l 44(sp),d1
\tmovea.l 48(sp),a1
\tmove.l 52(sp),d2
\tmove.l 56(sp),d3
\tmove.l 60(sp),d4
\tmove.l 64(sp),d5
\tmove.l 68(sp),d6
\tmovea.l 72(sp),a2
\tmovea.l _G_h01_5374,a6
\tjsr -636(a6)
\tmovem.l (sp)+,d4-d6/a2-a6
\trts
\tdseg
\tend
'''
BINDER=b'''\tpublic .begin
.begin
\trts
\tdseg
\tpublic _G_h01_5374
_G_h01_5374
\tds.l 1
\tend
'''
SDK={
 'toolchain/installed/aztec-3.6a/Library Source/graphics.arc':'707a6b294bcdf29eaf0a17e4fbf30b9533c06e97487f933e2a65d81164272c34',
 'toolchain/installed/aztec-5.0a/Aztec1/include/pragmas.h':'f8cfe465c59e842e48f5b2ba65fbf3eebaed77fc90530c34e109c4addcb45c32',
 'toolchain/installed/aztec-5.0a/Aztec1/include/functions.h':'07c0cc55c0ef3633d3eb651f9e212e924d029b15f0c37c0a5fa53789bb040d4d'}
def document(root,name):return json.loads(canonical_path(root,name).read_bytes())
def sdk(root):
 texts=[]
 for name,digest in SDK.items():
  raw=canonical_path(root,name).read_bytes();require(sha256(raw)==digest,'graphics SDK pin changed');texts.append(raw.decode('latin1'))
 vector=next(l for l in texts[0].splitlines() if '_LVOBltMaskBitMapRastPort' in l and 'equ' in l)
 pragma='#pragma amicall(GfxBase, 0x27c, BltMaskBitMapRastPort('+','.join(REGISTERS)+'))'
 prototype='void BltMaskBitMapRastPort(struct BitMap *srcbm,long srcx,long srcy,struct RastPort *destrp,long destX,long destY,long sizeX,long sizeY,long minterm,void *bltmask);'
 require(vector.split()==['_LVOBltMaskBitMapRastPort','equ','-636'] and pragma in texts[1].splitlines() and prototype in texts[2].splitlines(),'pinned vector/register/prototype contract')
 return dict(pins=SDK,vector=-636,registers=REGISTERS,pragma=pragma,prototype=prototype)
def base(root):
 item=document(root,'recovery/ledger.json')['functions']['ov04_F_1E36'];raw=canonical_path(root,item['proof']).read_bytes();source=canonical_path(root,item['source']).read_bytes();p=json.loads(raw)
 require(sha256(raw)==item['proof_sha256'] and sha256(source)==item['source_sha256'],'graphics base canonical source/proof pins')
 require(p['id']=='ov04_F_1E36' and p['source_sha256']==item['source_sha256'],'graphics base proof/source identity')
 cmp=p['comparison'];cmp=cmp.get('code_comparison',cmp)
 require(cmp['verdict']=='EQUAL' and cmp['relocation_equal'] and cmp['normalized_sha256']==item['evidence_extent']['sha256'],'graphics base exact C proof')
 require(b'G_h01_5374 = F_h00_89D0("graphics.library", 0L);' in source,'graphics base independently named producer')
 refs=[x for x in p['comparison'].get('relocation_proof',[]) if x.get('identity',{}).get('symbol')=='_G_h01_5374']
 require(refs and all(x['identity']==dict(addend=0,hunk=1,offset=0x5374,symbol='_G_h01_5374') for x in refs),'graphics base named relocation identities')
 return dict(id='ov04_F_1E36',source=item['source'],source_sha256=item['source_sha256'],proof=item['proof'],proof_sha256=item['proof_sha256'],symbol='_G_h01_5374',hunk=1,target=0x5374,storage_ownership='UNKNOWN')
def control(root,blob,model):
 import audio_frameless_asm as batch
 import audio_frame_calibration as frame
 b=document(root,batch.MANIFEST);audit=batch.producer(root,b)
 return dict(frame_calibration=frame.derive(root,blob,model,b),frame_producer=audit)
def witness(items,entry,measured,abi):
 """The complete independently entered bridge, not adjacency or ABI guesses.

 The existing calibration measures all pinned C entries/options anew. This
 predicate additionally requires the SDK's ten register inputs and A6 vector.
 A C-compatible framed call never earns assembly eligibility.
 """
 import audio_frame_calibration as frame
 require(measured.get('all_required_entries_link_a5') is True,'graphics glue lacks current frame calibration')
 require(abi['vector']==-636 and abi['registers']==REGISTERS,'SDK ABI changed')
 require(entry==dict(kind='DIRECT_CALL',caller='resident_F_34E0',site=0x35a4,target=0x4692),'graphics glue lacks independent entry')
 expected=[('movem.l','d4-d6/a2-a6, -(a7)')]
 expected += [('movea.l' if reg.startswith('a') else 'move.l','$%x(a7), %s'%(36+4*n,reg)) for n,reg in enumerate(REGISTERS)]
 expected += [('movea.l','$5374.l, a6'),('jsr','-$27c(a6)'),('movem.l','(a7)+, d4-d6/a2-a6'),('rts','')]
 require([(i['mnemonic'],i['operands']) for i in items]==expected,'complete register ABI save/load/call/restore changed')
 require([i['offset'] for i in items]==list(range(0x4692,0x46c2,4))+[0x46c4,0x46c8,0x46cc] and items[-1]['offset']+items[-1]['size']==0x46ce,'glue complete instruction boundaries')
 require(all(a['offset']+a['size']==b['offset'] for a,b in zip(items,items[1:])),'glue instruction gap')
 # The sole computed call is independently the bound SDK A6 vector. Its
 # return edge reaches the restore and RTS; no other transfer is permitted.
 pred=dict(kind='CALIBRATED_FRAMELESS_LINEAR_SDK_CALL',entry=0x4692,return_sites=[0x46cc],reachable_instructions=[i['offset'] for i in items],sdk_call=dict(site=0x46c4,base='a6',vector=-636,return_to=0x46c8),stack_frame=False,calibration='PINNED_36A_ALL_ACCEPTED_OPTIONS_AND_CANONICAL_C',c_compatible=False)
 return dict(kind='FRAMELESS_REGISTER_ABI_LIBRARY_BRIDGE',frame=pred,entry_evidence=entry,saved_registers='d4-d6/a2-a6',saved_stack_bytes=32,arguments=[dict(stack_offset=36+4*n,width=4,register=reg) for n,reg in enumerate(REGISTERS)],vector=-636,base_symbol='_G_h01_5374',c_compatible=False,basis='Measured pinned C entries use LINK; complete bridge transfers ten stack arguments into the pinned SDK register ABI and calls the A6 library vector.')
def derive(blob,model,measured,root):
 import audio_driver_contracts as contracts
 c=payload(blob,model,0);call=contracts.decode(c[0x35a4:0x35a8],0x35a4)
 require(len(call)==1 and (call[0]['mnemonic'],call[0]['operands'])==('jsr','$4692(pc)'),'independent sprite caller entry')
 items=contracts.decode(c[0x4692:0x46ce],0x4692);neighbor=contracts.decode(c[0x46ce:0x46d2],0x46ce)
 require(len(neighbor)==1 and neighbor[0]['mnemonic']=='link.w' and neighbor[0]['operands'].startswith('a5, '),'independent next C entry boundary')
 pred=witness(items,dict(kind='DIRECT_CALL',caller='resident_F_34E0',site=0x35a4,target=0x4692),measured,sdk(root))
 rels=[field(r) for r in model['relocations'] if r['source_hunk']==0 and r['source_offset']<0x46ce and 0x4692<r['source_offset']+r['width']]
 require(rels==[dict(source_hunk=0,source_offset=0x46c0,target_hunk=1,addend_raw=0x5374,type='HUNK_RELOC32',width=4)],'complete graphics base relocation')
 return dict(predicate=pred,sdk=sdk(root),base_binding=base(root),relocations=rels)
def make_fact(root,blob,model,contract):
 return dict(schema_version=1,id=ID,oracle_sha256=sha256(blob),original=dict(hunk=0,start=0x4692,end=0x46ce,size=60,sha256=sha256(payload(blob,model,0)[0x4692:0x46ce])),predicate=contract['predicate'],sdk=contract['sdk'],base_binding=contract['base_binding'],relocations=[dict(r,symbol='_G_h01_5374') for r in contract['relocations']],prefix='glue',exports=[dict(name='_F_h00_4692',offset=0,original=0x4692)],external_data=[dict(name='_G_h01_5374',hunk=1,target=0x5374)],source=SOURCE,candidate=RULES+'glue.asm',source_sha256=sha256(ASM),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None)
def source_for(ident):
 require(ident==ID,'unknown library glue source');return ASM

def producer(root,batch):
 import audio_score_measured as score
 require(set(batch)=={'schema_version','profile','facts','fact_sha256','job','request_sha256','receipt_sha256','artifacts','source_files'} and batch['schema_version']==1 and batch['profile']=='aztec36' and batch['facts']==FACTS,'glue batch schema')
 expected={'glue.asm':ASM,'bind.asm':BINDER}
 require(batch['source_files']=={n:sha256(b) for n,b in expected.items()},'closed mnemonic/binder source pins')
 require(all(canonical_path(root,RULES+n).read_bytes()==b for n,b in expected.items()),'independent mnemonic recipe; opaque carriers reject')
 require(batch['fact_sha256']=={FACT:sha256(json_bytes(document(root,FACT)))},'glue fact pins')
 return score.audit_producer(root,batch,expected,COMMANDS)
def object_code(raw):
 code,refs,structure=aj_parse(raw)
 require((structure['CODE'],structure['DATA'],structure['BSS'],structure['COMMON'])==(60,0,0,0),'complete glue object sections')
 require(structure['symbols']==[dict(name='_G_h01_5374',kind=7,attribute=14,offset=0,reference_count=1),dict(name='_F_h00_4692',kind=2,attribute=8,offset=0,reference_count=None)],'complete glue AJ symbol inventory')
 require(refs==[dict(offset=46,width=4,type='HUNK_RELOC32',symbol='_G_h01_5374',symbol_index=0,addend=0)],'complete glue AJ named fixups')
 return code,refs,structure
def verify(root,blob,model,analysis,fact,batch=None,contract=None,audit=None,cctrl=None):
 cctrl=control(root,blob,model) if cctrl is None else cctrl;contract=derive(blob,model,cctrl['frame_calibration'],root) if contract is None else contract
 require(fact==make_fact(root,blob,model,contract),'glue fact does not rederive in full')
 batch=document(root,MANIFEST) if batch is None else batch;audit=producer(root,batch) if audit is None else audit
 work=candidate_path(root,root/batch['job']/'sys/work');code,refs,structure=object_code((work/'glue.o').read_bytes())
 linked=(work/'glue.exe').read_bytes();lm=hunk_parse(linked);actual=payload(linked,lm,0);sm=symbol_map((work/'glue.sym').read_text())
 require([(h['type'],h['allocated_size'],h['initialized_size']) for h in lm['hunks']]==[('CODE',64,64),('DATA',4,4),('BSS',4,0)],'complete glue linked topology')
 require(sm=={(0,'__H0_org'):0,(0,'_F_h00_4692'):0,(0,'.begin'):60,(0,'__H0_end'):64,(1,'__H1_org'):0,(1,'_G_h01_5374'):0,(1,'__H1_end'):4,(2,'__H2_org'):4,(2,'__H2_end'):4},'complete glue link symbols')
 require(actual[:60]==code and actual[60:]==b'\x4e\x75\0\0' and payload(linked,lm,1)==bytes(4),'complete glue object/link/binder comparison')
 require([field(r) for r in lm['relocations']]==[dict(source_hunk=0,source_offset=46,target_hunk=1,addend_raw=0,type='HUNK_RELOC32',width=4)],'complete linked glue relocation')
 original=payload(blob,model,0)[0x4692:0x46ce]
 require(code[:46]==original[:46] and code[46:50]==bytes(4) and original[46:50]==(0x5374).to_bytes(4,'big') and code[50:]==original[50:],'whole glue CODE/named relocation differs')
 bindings=[dict(refs[0],original_hunk=1,original_target=0x5374,candidate_hunk=1,candidate_target=0)]
 return dict(id=ID,verdict='EQUAL_CANDIDATE',category='RECONSTRUCTED_ASM',span=fact['original'],manifest=MANIFEST,source_sha256=sha256(ASM),fact_sha256=sha256(json_bytes(fact)),non_c_predicate=contract['predicate'],object_structure=structure,named_relocation_bindings=bindings,ordinary_bytes_compared=56,named_field_bytes=4,producer=audit,linked_sha256=sha256(linked),frame_calibration=cctrl['frame_calibration'],frame_producer=cctrl['frame_producer'],data_credit=0,source_acceptance=False,proof_level=None,historical_owner='UNKNOWN',historical_object_membership='UNKNOWN',natural_root_layout_proof=False,verifier_identity={n:sha256(canonical_path(root,'tools/'+n).read_bytes()) for n in ['glue_library_asm.py','audio_driver_objects.py','audio_frame_calibration.py']})
def rows(root,blob,model,analysis,ledger):
 item=ledger.get(MAP,{}).get(ID)
 if item is None:return []
 fact=document(root,FACT);report=verify(root,blob,model,analysis,fact);dest='recovery/proofs/asm-reconstructed/'+ID+'.json'
 require(set(item)=={'state','fact','source','source_sha256','proof','proof_sha256'} and item['state']=='FUNCTION_CODE_MATCH' and item['fact']==FACT and item['source']==SOURCE and item['proof']==dest,'glue ownership identity')
 src=canonical_path(root,SOURCE).read_bytes();raw=canonical_path(root,dest).read_bytes();p=json.loads(raw)
 require(src==ASM and sha256(src)==item['source_sha256'] and sha256(raw)==item['proof_sha256'],'canonical glue source/proof pins')
 require(set(p)=={'fact','comparison','regression'} and p['fact']==fact and p['regression'].get('passed') is True,'canonical glue fact/gate')
 comparable=lambda r:{k:v for k,v in r.items() if k not in ['verifier_identity','frame_calibration']}
 require(p['comparison'].get('verifier_identity') and comparable(p['comparison'])==comparable(report),'canonical glue replay differs')
 for rec in ledger.get('functions',{}).values():
  o=rec['evidence_extent'];require(o['hunk']!=0 or o['end']<=0x4692 or o['start']>=0x46ce,'glue overlaps canonical C')
 return [dict(report,acceptance=True,source_acceptance=True,proof_level='FUNCTION_CODE_MATCH',source=SOURCE,proof=dest)]
def contributions(root,records):
 result=[]
 for r in records:
  if r['id']!=ID or not r.get('acceptance'):continue
  code,refs,_=object_code((root/r['producer']['job']/'sys/work/glue.o').read_bytes());out=bytearray(code)
  require(r['named_relocation_bindings']==[dict(refs[0],original_hunk=1,original_target=0x5374,candidate_hunk=1,candidate_target=0)],'glue contribution named identity')
  out[46:50]=(0x5374).to_bytes(4,'big')
  result.append(dict(id=ID,hunk=0,start=0x4692,end=0x46ce,category='RECONSTRUCTED_ASM',bytes=bytes(out),relocations=[dict(source_offset=0x46c0,target_hunk=1,type='HUNK_RELOC32',width=4,addend_raw=0x5374)]))
 return result
def input_identity(root):
 import audio_frameless_asm as frames
 p=canonical_path(root,MANIFEST)
 if not p.exists():return {str(p):None}
 out=frames.input_identity(root);names={MANIFEST,FACT,RULES+'glue.asm',RULES+'bind.asm',*SDK}
 if p.exists():
  b=document(root,MANIFEST);j=b['job'];names.update(j+'/'+n for n in ['request.json','result.json','worker.uae','kick.rom','sys/s/startup-sequence']);names.update(j+'/sys/work/'+n for n in b['artifacts'])
  req=json.loads((root/j/'request.json').read_bytes());names.update(x['path'] for x in req['pinned_inputs']);out[req['emulator']]=sha256(Path(req['emulator']).read_bytes())
  for folder in ['c','l','libs','devs']:names.update(p.relative_to(root).as_posix() for p in active_files(root/j/'sys'/folder))
 ledger=document(root,'recovery/ledger.json');item=ledger['functions']['ov04_F_1E36'];names.update([item['source'],item['proof']])
 for item in [ledger.get(MAP,{}).get(ID)]:
  if item:names.update([item['source'],item['proof'],item['fact']])
 for n in names:
  p=candidate_path(root,root/n) if n.startswith('build/') else canonical_path(root,n);out[str(p)]=sha256(p.read_bytes()) if p.exists() else None
 return out
