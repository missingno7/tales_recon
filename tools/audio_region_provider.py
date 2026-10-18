"""Exact rooted envelope/selector/score DATA provider for H0 5E6C..704E."""
from names import read_source, source_path as source_file
from validation_memo import shared
import json
from pathlib import Path
from collections import Counter
from common import require,sha256,json_bytes
from repo_paths import canonical_path,candidate_path,active_files
from audio_sequence_data import payload,field
import audio_region_catalogue as types
import audio_score_measured as score
IDENT='resident_audio_region_0003'
FACT='evidence/code-data-providers/region-0003.json'
MANIFEST='evidence/code-data-providers/batch-0003.json'
CATEGORY='TYPED_CODE_DATA'
MAP='code_data_providers'
KIND='MEASURED_TYPED_AUDIO_REGION'
def doc(root,name):return json.loads(canonical_path(root,name).read_bytes())
def packed_control():
 lines=['CV macro','\tdc.b \\1','\tendm','CP macro','\tdc.l \\1','\tendm','\tcseg','\tpublic _packed_begin','\tpublic _packed_end']+['\tpublic _packed_%03d'%i for i in range(200)]+['_packed_begin:']+['\tCP _packed_%03d'%i for i in range(200)]
 for i in range(200):lines+=['_packed_%03d:'%i,'\tCV %d'%i]
 return ('\n'.join(lines+['_packed_end:','\tend',''])).encode('ascii')
def validate(root,blob,model,fact):
 require(set(fact)=={'schema_version','id','oracle_sha256','contract_sha256','layout_sha256','objects','historical_owner','historical_tu','original_filename'},'region fact fields; raw carriers/masks reject')
 require(type(fact['schema_version']) is int and fact['schema_version']==3 and fact['id']==IDENT,'region identity')
 require(fact['historical_owner']==fact['historical_tu']=='UNKNOWN' and fact['original_filename'] is None,'region historical provenance')
 for o in fact['objects']:
  for c in o['rows']:types.check(c)
 g=types.contract(blob,model);require(fact['contract_sha256']==sha256(json_bytes(g)),'stale grammar/handler binding for every region stream')
 require(fact['oracle_sha256']==sha256(blob),'stale region oracle')
 ledger=doc(root,'recovery/ledger.json')
 require(score.IDENT in ledger.get(MAP,{}),'selector extent/old target source is not canonical')
 # Recheck the accepted source, not just a cached proof or an address range.
 score.rows(root,blob,model,{},ledger)
 import reconstructed_asm
 asm=reconstructed_asm.rows(root,blob,model,doc(root,'evidence/functions/ledger.json'),ledger)
 spans=[(r['span']['start'],r['span']['end']) for r in asm]
 require(all(any(a<=p and z<=b for a,b in spans) for p,z in ((0x544c,0x558a),(0x57e4,0x5868),(0x58bc,0x59a4),(0x5a50,0x5cc2),(0x5cc6,0x5d74),(0x5d78,0x5d80),(0x5d92,0x5e6c))),'driver consumer is not canonically proved')
 layout=types.discover(root,blob,model,g);require(fact['layout_sha256']==sha256(json_bytes(layout)),'root closure/terminal/relocation layout changed')
 objects=types.plan(layout,g);targets={b['symbol'] for b in layout['bindings']};expected=[]
 for o in objects:expected.append(dict(o,source_sha256=sha256(types.source(o,g,targets))))
 require(fact['objects']==expected,'partial stream, guessed gap, changed typed value or clipped object')
 for o in expected:require(canonical_path(root,o['candidate']).read_bytes()==types.source(o,g,targets),'raw carrier or changed typed macro source')
 return g,layout,targets

def definition_plan(o,sem,targets):
 local={d['name']:d['offset'] for d in sem['definitions']};used={f['symbol'] for f in sem['fixups']}
 return [dict(name='_'+o['prefix']+'_begin',offset=0,external=False),dict(name='_'+o['prefix']+'_end',offset=o['typed_bytes'],external=False)]+[dict(name=n,offset=local[n],external=False) for n in sorted(local.keys()&targets)]+[dict(name=n,offset=0,external=True) for n in sorted(used-local.keys())]

def object_code(raw,size,logical,defs,fixups):
 """Whole CSEG AJ grammar, calibrated at packed symbol indices 2..201.

 FD carries a low-nibble 70..7F and a high byte. Attribute 0C carries the
 actual reference count for local definitions and named external CODE refs.
 No addend, other section, unparsed byte or unnamed symbol is admitted.
 """
 require(raw[:10]==b'AJ'+bytes(8) and len(raw)>=36,'region AJ header')
 u16=lambda p:int.from_bytes(raw[p:p+2],'big');u32=lambda p:int.from_bytes(raw[p:p+4],'big')
 begin=u32(24)*4;syms=u16(28)*4;end=u16(30)*4
 require((u32(10),u32(14),u32(18))==(size,0,0) and begin==36 and syms<=end==u16(32)*4==len(raw) and raw[34:36]==b'\xc0\0' and u16(22)==len(defs),'whole region AJ structure')
 require(size==logical+logical%2 and len(defs)<=202,'unmeasured AJ extent/index domain')
 counts=Counter(f['symbol'] for f in fixups);p=syms
 for d in defs:
  attr=12 if counts[d['name']] else 8
  require(p+4<=end and raw[p:p+2]==bytes((7 if d['external'] else 2,attr)) and u16(p+2)==d['offset'],'AJ named definition/external kind/value');p+=4
  if attr==12:require(u16(p)==counts[d['name']],'AJ reference count');p+=2
  z=raw.find(b'\0',p,end);require(z>=p and raw[p:z].decode('ascii')==d['name'],'AJ complete symbol name/order');p=z+1
 require(end-p<=3 and raw[p:]==bytes(end-p),'AJ symbol trailer')
 code=bytearray();got=[];p=begin
 while len(code)<logical:
  require(p<syms,'AJ truncated CODE');t=raw[p];p+=1
  if 0x10<=t<=0x1f:
   n=t-15;require(p+n<=syms and len(code)+n<=logical,'AJ literal extent');code+=raw[p:p+n];p+=n
  else:
   require(t==0xfd and p+2<=syms,'AJ unmeasured token');low,high=raw[p:p+2];p+=2
   require(0x70<=low<=0x7f,'AJ packed symbol token');index=low-0x70+16*high;require(index<len(defs) and index<=201,'AJ packed index outside control')
   d=defs[index];got.append(dict(offset=len(code),symbol=d['name'],type='HUNK_RELOC32',width=4,addend=0));require(len(code)+4<=logical,'AJ straddling fixup');code+=d['offset'].to_bytes(4,'big')
 require(syms==((p+4)//4)*4 and raw[p:syms]==bytes(syms-p),'AJ CODE terminator/alignment')
 code+=bytes(logical%2);require(got==fixups,'AJ exhaustive named RELOC32')
 return dict(code=bytes(code),definitions=defs,fixups=got,object_sha256=sha256(raw))

def commands_for(fact,old):
 prefixes=[o['prefix'] for o in fact['objects']]+[o['prefix'] for o in old['objects']]
 return ['Old1:bin/as -o '+p+'.o '+p+'.asm >'+p+'-as.log' for p in prefixes]+['Old1:bin/ln -m -t -o regionall.exe '+' '.join(p+'.o' for p in prefixes)+' >regionall-ln.log','Old1:bin/as -o packed.o packed.asm >packed-as.log','Old1:bin/ln -m -t -o packed.exe packed.o >packed-ln.log','Old1:bin/as -o odd.o odd.asm >odd-as.log','Old1:bin/ln -m -t -o odd.exe odd.o >odd-ln.log']

def verify(root,blob,model,fact,batch=None):
 g,layout,targets=validate(root,blob,model,fact);batch=doc(root,MANIFEST) if batch is None else batch
 require(set(batch)=={'schema_version','profile','facts','fact_sha256','job','request_sha256','receipt_sha256','artifacts'} and batch['schema_version']==3 and batch['profile']=='aztec36' and batch['facts']==[FACT] and batch['fact_sha256']=={FACT:sha256(json_bytes(fact))},'complete region producer manifest')
 old=doc(root,score.FACT);_,oldlayout,_=__import__('audio_score_catalogue').rederive(root,blob,model);olditems=score.members(old,oldlayout)
 expected={o['prefix']+'.asm':types.source(o,g,targets) for o in fact['objects']};expected.update({p+'.asm':x['source'] for p,x in olditems.items()});expected.update({'packed.asm':packed_control(),'odd.asm':score.ODD_SOURCE})
 producer=score.audit_producer(root,batch,expected,commands_for(fact,old));work=candidate_path(root,Path(root)/producer['job']/'sys/work');padding=score.padding_control(work)
 # The independent packed-index control exercises beyond every batch index.
 cd=[dict(name='_packed_begin',offset=0,external=False),dict(name='_packed_end',offset=1000,external=False)]+[dict(name='_packed_%03d'%i,offset=800+i,external=False) for i in range(200)]
 cf=[dict(offset=4*i,symbol='_packed_%03d'%i,type='HUNK_RELOC32',width=4,addend=0) for i in range(200)]
 control=object_code((work/'packed.o').read_bytes(),1000,1000,cd,cf);cc=b''.join((800+i).to_bytes(4,'big') for i in range(200))+bytes(range(200));require(control['code']==cc,'independent packed index control CODE')
 from hunk import parse
 from overlay_experiment import symbols
 cb=(work/'packed.exe').read_bytes();cm=parse(cb);cs=symbols((work/'packed.sym').read_text())
 require([(h['type'],h['allocated_size'],h['initialized_size']) for h in cm['hunks']]==[('CODE',1000,1000),('DATA',0,0),('BSS',4,0)] and payload(cb,cm,0)==cc,'whole packed control link')
 require(cs=={**{(0,d['name']):d['offset'] for d in cd},(0,'__H0_org'):0,(0,'__H0_end'):1000,(1,'__H1_org'):0,(1,'__H1_end'):0,(2,'__H2_org'):0,(2,'__H2_end'):0},'packed control symbols')
 require(sorted(map(field,cm['relocations']),key=lambda x:x['source_offset'])==[dict(source_hunk=0,source_offset=4*i,target_hunk=0,addend_raw=800+i,type='HUNK_RELOC32',width=4) for i in range(200)],'packed control relocations')
 units=[];base=0;globaldefs={};newitems=[]
 for o in fact['objects']:
  sem=types.encode(o,g);defs=definition_plan(o,sem,targets);aj=object_code((work/(o['prefix']+'.o')).read_bytes(),o['CODE'],o['typed_bytes'],defs,sem['fixups'])
  want=bytearray(sem['code']+bytes(o['typed_bytes']%2));local={d['name']:d['offset'] for d in defs if not d['external']}
  for f in sem['fixups']:want[f['offset']:f['offset']+4]=local.get(f['symbol'],0).to_bytes(4,'big')
  require(aj['code']==want,'complete new AJ CODE differs from typed macros')
  units.append(dict(base=base,code=aj['code'],defs=defs,fixups=sem['fixups']));newitems.append((o,aj,base))
  for d in defs:
   if not d['external']:require(d['name'] not in globaldefs,'duplicate definition');globaldefs[d['name']]=base+d['offset']
  base+=o['CODE']
 oldbatch=doc(root,score.MANIFEST)
 for prefix,item in olditems.items():
  o=item['member'];sem=item['semantic'];defs=score.expected_definitions(o,sem);raw=(work/(prefix+'.o')).read_bytes()
  require(sha256(raw)==oldbatch['artifacts'][prefix+'.o'],'unchanged canonical score supporting object differs')
  aj=score.object_code(raw,o['CODE'],defs,sem['fixups']);defs=[dict(d,external=False) for d in defs];units.append(dict(base=base,code=aj['code'],defs=defs,fixups=sem['fixups']))
  for d in defs:require(d['name'] not in globaldefs,'duplicate supporting definition');globaldefs[d['name']]=base+d['offset']
  base+=o['CODE']
 linked=(work/'regionall.exe').read_bytes();lm=parse(linked);lc=payload(linked,lm,0);sm=symbols((work/'regionall.sym').read_text());total=(base+3)//4*4
 require([(h['type'],h['allocated_size'],h['initialized_size']) for h in lm['hunks']]==[('CODE',total,total),('DATA',0,0),('BSS',4,0)],'whole region link topology')
 require(sm=={**{(0,n):v for n,v in globaldefs.items()},(0,'__H0_org'):0,(0,'__H0_end'):total,(1,'__H1_org'):0,(1,'__H1_end'):0,(2,'__H2_org'):0,(2,'__H2_end'):0},'complete region link symbols')
 rels=[]
 for u in units:
  expected_code=bytearray(u['code'])
  for f in u['fixups']:
   require(f['symbol'] in globaldefs,'pointer to unproved external symbol');value=globaldefs[f['symbol']];expected_code[f['offset']:f['offset']+4]=value.to_bytes(4,'big');rels.append(dict(source_hunk=0,source_offset=u['base']+f['offset'],target_hunk=0,addend_raw=value,type='HUNK_RELOC32',width=4))
  require(lc[u['base']:u['base']+len(expected_code)]==expected_code,'whole linked CODE/target binding differs')
 require(lc[base:]==bytes(total-base),'link tail alignment differs')
 require(sorted(map(field,lm['relocations']),key=lambda x:x['source_offset'])==sorted(rels,key=lambda x:x['source_offset']),'exhaustive linked RELOC32')
 original=payload(blob,model,0);bi={b['source_offset']:b for b in layout['bindings']};reports=[]
 for o,aj,offset in newitems:
  mapped=bytearray(aj['code']);bindings=[]
  for part in o['parts']:
   a,z,ca,cz=[part[k] for k in ('original_start','original_end','candidate_start','candidate_end')]
   for f in aj['fixups']:
    if ca<=f['offset']<cz:
     require(f['offset']+4<=cz,'straddling typed partition');site=a+f['offset']-ca;b=bi[site];require(b['symbol']==f['symbol'],'original named pointer differs')
     mapped[f['offset']:f['offset']+4]=b['addend_raw'].to_bytes(4,'big');bindings.append(dict(b,object_offset=f['offset']))
   require(mapped[ca:cz]==original[a:z],'exact original CODE data/typed value differs')
  require(len(mapped)==o['typed_bytes']+o['typed_bytes']%2,'clipped object');require(mapped[o['typed_bytes']:]==bytes(o['typed_bytes']%2),'natural padding')
  reports.append(dict(o,kind=KIND,original=dict(hunk=0,start=min(p['original_start'] for p in o['parts']),end=max(p['original_end'] for p in o['parts']),size=max(p['original_end'] for p in o['parts'])-min(p['original_start'] for p in o['parts'])),bindings=bindings,object_definitions=aj['definitions'],object_sha256=aj['object_sha256'],linked_start=offset,padding_credit=0))
 return dict(id=IDENT,kind=KIND,category=CATEGORY,typed_bytes=layout['typed_bytes'],objects=reports,producer=producer,roots=layout['roots'],envelope_views=layout['envelope_views'],blocked_selectors=layout['blocked_selectors'],unproved_intervals=layout['unproved_intervals'],named_relocations=len(layout['bindings']),contract_sha256=fact['contract_sha256'],layout_sha256=fact['layout_sha256'],fact_sha256=sha256(json_bytes(fact)),linked_sha256=sha256(linked),whole_CODE_bytes=total,padding_control=padding,packed_index_control=dict(max_index=201,object_sha256=control['object_sha256'],game_credit=0),c_bytes=0,asm_instruction_bytes=0,padding_credit=0,source_acceptance=False,proof_level=None,historical_owner='UNKNOWN',historical_tu='UNKNOWN',natural_root_layout_proof=False,verifier_identity={n:sha256(canonical_path(root,'tools/'+n).read_bytes()) for n in ('audio_region_catalogue.py','audio_region_provider.py','audio_score_grammar.py','audio_score_commands.py','audio_score_measured.py','reconstructed_asm.py','hunk.py','repo_paths.py')})

@shared
def rows(root,blob,model,analysis,ledger):
 item=ledger.get(MAP,{}).get(IDENT)
 if item is None:return []
 require(set(item)=={'state','fact','sources','proof','proof_sha256'} and item['state']=='DATA_LAYOUT_MATCH' and item['fact']==FACT and item['proof']=='recovery/proofs/code-data/'+IDENT+'.json','region ownership identity')
 fact=doc(root,FACT);report=verify(root,blob,model,fact);require(item['sources']=={o['source']:o['source_sha256'] for o in fact['objects']},'region source inventory')
 for o in fact['objects']:require(read_source(root, o['source'])==canonical_path(root,o['candidate']).read_bytes(),'canonical region source differs')
 raw=canonical_path(root,item['proof']).read_bytes();proof=json.loads(raw);require(sha256(raw)==item['proof_sha256'] and set(proof)=={'fact','comparison','regression'} and proof['fact']==fact and proof['regression'].get('passed') is True,'region proof/gate')
 comparable=lambda x:{k:v for k,v in x.items() if k!='verifier_identity'}
 require(proof['comparison'].get('verifier_identity') and comparable(proof['comparison'])==comparable(report),'region canonical proof no longer rederives')
 return [dict(o,acceptance=True,source_acceptance=True,proof_level='DATA_LAYOUT_MATCH',proof=item['proof'],producer=report['producer'],category=CATEGORY,provider=IDENT) for o in report['objects']]
def contributions(root,records):
 result=[]
 for r in records:
  require(r.get('acceptance') is True,'region requires canonical replay');raw=candidate_path(root,Path(root)/r['producer']['job']/('sys/work/'+r['prefix']+'.o')).read_bytes();fix=[dict(offset=b['object_offset'],symbol=b['symbol'],type=b['type'],width=b['width'],addend=0) for b in r['bindings']];fix.sort(key=lambda x:x['offset'])
  aj=object_code(raw,r['CODE'],r['typed_bytes'],r['object_definitions'],fix);code=bytearray(aj['code'])
  for b in r['bindings']:code[b['object_offset']:b['object_offset']+4]=b['addend_raw'].to_bytes(4,'big')
  for i,p in enumerate(r['parts']):
   a,z=p['original_start'],p['original_end'];rels=[{k:b[k] for k in ('source_offset','target_hunk','type','width','addend_raw')} for b in r['bindings'] if a<=b['source_offset']<z]
   result.append(dict(id=r['id']+'_part%d'%i,hunk=0,start=a,end=z,category=CATEGORY,bytes=bytes(code[p['candidate_start']:p['candidate_end']]),relocations=rels))
 return result
def input_identity(root):
 root=Path(root);names={FACT,MANIFEST};external={};fact=doc(root,FACT) if canonical_path(root,FACT).exists() else {}
 names.update(o['candidate'] for o in fact.get('objects',[]))
 if canonical_path(root,MANIFEST).exists():
  batch=doc(root,MANIFEST);job=batch['job'];names.update(job+'/'+n for n in ['request.json','result.json','worker.uae','kick.rom','sys/s/startup-sequence']);names.update(job+'/sys/work/'+n for n in batch['artifacts']);request=json.loads(candidate_path(root,root/job/'request.json').read_bytes());names.update(p['path'] for p in request['pinned_inputs']);names.update(['toolchain/candidate-lock.json','evidence/toolchain/aztec-3.6a.json','evidence/toolchain/aztec-5.0a.json']);names.add(doc(root,'toolchain/candidate-lock.json')['archive'])
  for folder in ('c','l','libs','devs'):names.update(p.relative_to(root).as_posix() for p in active_files(root/job/'sys'/folder))
  external[request['emulator']]=sha256(Path(request['emulator']).read_bytes())
 item=(doc(root,'recovery/ledger.json') if canonical_path(root,'recovery/ledger.json').exists() else {}).get(MAP,{}).get(IDENT)
 if item:names.update([item['fact'],item['proof'],*item['sources']])
 def path(n):return candidate_path(root,root/n) if n.startswith('build/worker-jobs/') else canonical_path(root,n)
 return {**{str(path(n)):sha256((read_source(root, path(n)) if n.startswith('src/') else path(n).read_bytes())) if (source_file(root, path(n)) if n.startswith('src/') else path(n)).exists() else None for n in sorted(names)},**external}
