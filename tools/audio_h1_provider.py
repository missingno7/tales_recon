"""Exact mixed-hunk audio DATA provider, with one pinned vamos producer.

H1 records earn RECOVERED_DATA; only newly proved H0 fields earn TYPED_CODE_DATA.
Complete original support and producer objects are checked but never credited twice.
"""
from names import read_source, source_path as source_file
from collections import Counter
from pathlib import Path
import json,re
from common import require,sha256,json_bytes
from repo_paths import canonical_path,candidate_path,active_files
from validation_memo import shared
from audio_sequence_data import payload,field
import audio_h1_catalogue as types
import audio_score_measured as score
import audio_stateful_provider as previous

IDENT='resident_audio_h1_0005'
FACT='evidence/code-data-providers/h1-0005.json'
MANIFEST='evidence/code-data-providers/batch-0005.json'
KIND='MEASURED_TYPED_AUDIO_H1'
SOURCE='src/recovered/code-data/audio5.asm'
CANDIDATE='evidence/rules/audio-h1-0005/audio5.asm'
MAP='code_data_providers'
MIXED_SOURCE=b'\tcseg\n\tpublic _mx_c_begin\n\tpublic _mx_c_end\n\tpublic _mx_a\n\tpublic _mx_b\n_mx_c_begin:\n\tdc.l _mx_a\n\tdc.l _mx_b\n\tdc.l _mx_c_begin\n_mx_c_end:\n\tdseg\n\tpublic _mx_d_begin\n\tpublic _mx_d_end\n\tpublic _mx_pattern\n_mx_d_begin:\n_mx_a:\n\tdc.b 0,1\n\tdc.b $85\n\tds 0\n\tdc.l _mx_pattern\n\tdc.b $88\n_mx_b:\n\tdc.b 1,2\n\tdc.b $88\n_mx_pattern:\n\tdc.b $86\n_mx_d_end:\n\tend\n'

def doc(root,name):
 from code_data_providers import document
 return document(root,name)

def partition(objects,layout,prior,base):
 support={(0,p) for f in (prior,base) for o in f['objects'] for part in o['parts'] for p in range(part['original_start'],part['original_end'])}
 new={(0,r['selector']['source_offset']+i) for r in layout['roots'] for i in range(4)}
 new|={(0,b['source_offset']+i) for b in layout['bindings'] if b['source_hunk']==0 and b['source_offset']<0x6200 for i in range(4)}
 # Every DATA byte is grammar-rooted. H0 envelope byte roles are independent
 # cursor reads, not a guessed physical envelope allocation.
 for o in objects:
  o['credit_parts']=[];o['support_parts']=[]
  for part in o['parts']:
   a,z,ca=part['original_start'],part['original_end'],part['candidate_start'];p=a
   while p<z:
    isnew=o['hunk']==1 or (o['hunk'],p) in new or any(c['type']=='ENVELOPE_FIELD' and c['offset']==p for c in o['rows'])
    require(isnew or (o['hunk'],p) in support,'support lacks an independently accepted field')
    require(not isnew or (o['hunk'],p) not in support,'new credit overlaps accepted support')
    end=p+1
    while end<z:
     nxt=o['hunk']==1 or (o['hunk'],end) in new or any(c['type']=='ENVELOPE_FIELD' and c['offset']==end for c in o['rows'])
     if nxt!=isnew:break
     require(nxt or (o['hunk'],end) in support,'support lacks an independently accepted field');require(not nxt or (o['hunk'],end) not in support,'new credit overlaps support');end+=1
    o['credit_parts' if isnew else 'support_parts'].append(dict(original_start=p,original_end=end,candidate_start=ca+p-a,candidate_end=ca+end-a));p=end
  o['credit_bytes']=sum(p['original_end']-p['original_start'] for p in o['credit_parts'])

def make_objects(root,layout,g):
 objects=types.plan(layout,g);partition(objects,layout,doc(root,previous.FACT),doc(root,score.FACT));return objects

def validate(root,blob,model,fact):
 require(set(fact)=={'schema_version','id','oracle_sha256','contract_sha256','layout_sha256','source','candidate','source_sha256','objects','support_facts','historical_owner','historical_tu','original_filename'},'closed H1 audio fact; carriers/masks reject')
 require(fact['schema_version']==5 and fact['id']==IDENT and fact['source']==SOURCE and fact['candidate']==CANDIDATE,'H1 audio identity/source')
 require(fact['historical_owner']==fact['historical_tu']=='UNKNOWN' and fact['original_filename'] is None,'unknown historical source/TU')
 require(fact['oracle_sha256']==sha256(blob),'H1 audio oracle changed');g=types.old.contract(blob,model);require(fact['contract_sha256']==sha256(json_bytes(g)),'every handler/grammar binding must rederive')
 ledger=doc(root,'recovery/ledger.json');require(previous.IDENT in ledger.get(MAP,{}) and score.IDENT in ledger[MAP],'H0 canonical support missing')
 # Fresh canonical source/object proofs; no cached PASS is accepted here.
 previous.rows(root,blob,model,doc(root,'evidence/functions/ledger.json'),ledger)
 support={name:sha256(json_bytes(doc(root,name))) for name in (previous.FACT,score.FACT)};require(fact['support_facts']==support,'changed supporting facts')
 layout=types.discover(root,blob,model,g);objects=make_objects(root,layout,g)
 require(fact['layout_sha256']==sha256(json_bytes(layout)) and fact['objects']==objects,'changed root/terminal/typed operand/credit extent')
 raw=types.source(objects,g);require(fact['source_sha256']==sha256(raw) and canonical_path(root,CANDIDATE).read_bytes()==raw,'source differs from typed grammar macros')
 return g,layout,objects,types.encode(objects,g)

def definition_plan(objects,sem):
 used={b['symbol'] for b in sem['fixups']};local={d['name']:d for d in sem['definitions']};exports=used&local.keys()|{'_G_h00_6200_complete'}
 headers=[types.row_symbol(c) for o in objects for c in o['rows'] if c['hunk']==1 and c['type']=='HEADER'];exports.update(headers)
 def item(n,h=None,offset=0,external=False,context=None):
  d=local.get(n);return dict(name=n,hunk=(d['hunk'] if d else h),offset=(d['offset'] if d else offset),external=external,context=context)
 defs=[item(n,context='CSEG') for n in headers]
 for h in (0,1):
  o=next(o for o in objects if o['hunk']==h);context='CSEG' if h==0 else 'DSEG';defs += [item('_audio5_%s_begin'%h,h,0,context=context),item('_audio5_%s_end'%h,h,o['typed_bytes'],context=context)]
  defs += [item(d['name'],context=context) for d in sem['definitions'] if d['hunk']==h and d['name'] in exports and d['name'] not in headers]
  if h==0:defs += [item(n,0,external=True,context='CSEG') for n in sorted(used-local.keys())]
 return defs

def object_mixed(raw,logical,defs,fixups):
 """Measured complete CSEG/DSEG AJ grammar, including section identities.

 CSEG 0208/020C, external 0708/070C, DSEG 030A/032A and cross-section
 predeclared DATA 030C are independently controlled. Other attributes reject.
 Packed index 0..201 is bounded by the retained 202-symbol control.
 """
 require(len(raw)>=36 and raw[:10]==b'AJ'+bytes(8),'mixed AJ header')
 u16=lambda p:int.from_bytes(raw[p:p+2],'big');u32=lambda p:int.from_bytes(raw[p:p+4],'big');sizes={h:logical[h]+logical[h]%2 for h in (0,1)}
 syms=u16(28)*4;end=u16(30)*4
 require((u32(10),u32(14),u32(18))==(sizes[0],sizes[1],0) and u32(24)*4==36 and syms<=end==u16(32)*4==len(raw) and raw[34:36]==b'\xc0\0' and u16(22)==len(defs)<=202,'whole mixed AJ sections/structure')
 counts=Counter(f['symbol'] for f in fixups);p=syms
 for d in defs:
  refs=counts[d['name']];kind=7 if d['external'] else 2 if d['hunk']==0 else 3
  attr=(12 if refs else 8) if kind in (2,7) or d['context']=='CSEG' else (42 if refs else 10)
  require(p+4<=end and raw[p:p+2]==bytes((kind,attr)) and u16(p+2)==d['offset'],'mixed named definition section/attribute/value');p+=4
  if refs:require(p+2<=end and u16(p)==refs,'mixed reference count');p+=2
  z=raw.find(b'\0',p,end);require(z>=p and raw[p:z].decode('ascii')==d['name'],'whole mixed named symbol order');p=z+1
 require(end-p<=3 and raw[p:]==bytes(end-p),'mixed symbol trailer')
 contents={0:bytearray(),1:bytearray()};actual=[];h=0;p=36;switched=False
 while p<syms:
  token=raw[p];p+=1
  if token==0xf5:
   require(not switched and h==0 and len(contents[0])==logical[0],'single complete CODE-to-DATA transition');h=1;switched=True;continue
  if token==0 and syms-p+1<=4 and raw[p-1:syms]==bytes(syms-p+1):p=syms;break
  out=contents[h]
  if 0x10<=token<=0x1f:
   n=token-15;require(p+n<=syms and len(out)+n<=logical[h],'mixed literal outside complete logical section');out+=raw[p:p+n];p+=n
  else:
   require(token==0xfd and p+2<=syms,'unmeasured mixed AJ record');low,high=raw[p:p+2];p+=2;index=low-0x70+16*high
   require(0x70<=low<=0x7f and 0<=index<len(defs) and index<=201,'mixed packed symbol outside control');d=defs[index]
   actual.append(dict(hunk=h,offset=len(out),symbol=d['name'],type='HUNK_RELOC32',width=4,addend=0));require(len(out)+4<=logical[h],'straddling mixed fixup');out+=d['offset'].to_bytes(4,'big')
 require(switched and all(len(contents[h])==logical[h] for h in (0,1)) and actual==fixups,'partial section or incomplete named fixup inventory')
 for h in (0,1):contents[h]+=bytes(logical[h]%2)
 return dict(sections={h:bytes(b) for h,b in contents.items()},definitions=defs,fixups=actual,object_sha256=sha256(raw))

def support(root):
 result=[]
 for module in (score,previous):
  fact=doc(root,module.FACT);batch=doc(root,module.MANIFEST)
  for o in fact['objects']:
   require(sha256(read_source(root, o['source']))==o['source_sha256'],'support source changed')
   result.append(dict(prefix=o['prefix'],source=o['source'],source_sha256=o['source_sha256'],object_sha256=batch['artifacts'][o['prefix']+'.o'],provider=module.IDENT,object=o))
 return result

def commands_for(supports):
 prefixes=['audio5']+[s['prefix'] for s in supports]
 commands=['Old1:bin/as -o '+p+'.o '+p+'.asm >'+p+'-as.log' for p in prefixes]+['Old1:bin/ln -m -t -o audio5all.exe '+' '.join(p+'.o' for p in prefixes)+' >audio5all-ln.log']
 for p in ('mixed','packed','odd'):commands += ['Old1:bin/as -o '+p+'.o '+p+'.asm >'+p+'-as.log','Old1:bin/ln -m -t -o '+p+'.exe '+p+'.o >'+p+'-ln.log']
 return commands

def link_view(blob,map_text,units):
 from hunk import parse
 from overlay_experiment import symbols
 m=parse(blob);sm=symbols(map_text);bases={0:0,1:0};globaldefs={}
 for u in units:
  u['base']=dict(bases)
  for d in u['definitions']:
   if not d['external']:
    require(d['name'] not in globaldefs,'duplicate complete linked definition');globaldefs[d['name']]=(d['hunk'],bases[d['hunk']]+d['offset'])
  for h in (0,1):bases[h]+=len(u['sections'][h])
 rounded={h:(n+3)&~3 for h,n in bases.items()}
 require([(h['type'],h['allocated_size'],h['initialized_size']) for h in m['hunks']]==[('CODE',rounded[0],rounded[0]),('DATA',rounded[1],rounded[1]),('BSS',4,0)],'complete mixed link allocation/topology')
 require(sm=={**{(h,n):p for n,(h,p) in globaldefs.items()},(0,'__H0_org'):0,(0,'__H0_end'):rounded[0],(1,'__H1_org'):0,(1,'__H1_end'):rounded[1],(2,'__H2_org'):rounded[1],(2,'__H2_end'):rounded[1]},'complete mixed linked symbols')
 wanted=[]
 for u in units:
  expected={h:bytearray(u['sections'][h]) for h in (0,1)}
  for f in u['fixups']:
   require(f['symbol'] in globaldefs,'unproved linked external');th,tp=globaldefs[f['symbol']];h,p=f['hunk'],f['offset'];expected[h][p:p+4]=tp.to_bytes(4,'big');wanted.append(dict(source_hunk=h,source_offset=u['base'][h]+p,target_hunk=th,addend_raw=tp,type='HUNK_RELOC32',width=4))
  for h in (0,1):require(payload(blob,m,h)[u['base'][h]:u['base'][h]+len(expected[h])]==expected[h],'complete linked bytes/target identity')
 for h in (0,1):require(payload(blob,m,h)[bases[h]:]==bytes(rounded[h]-bases[h]),'whole link tail alignment')
 require(sorted(map(field,m['relocations']),key=lambda r:(r['source_hunk'],r['source_offset']))==sorted(wanted,key=lambda r:(r['source_hunk'],r['source_offset'])),'exhaustive mixed linked relocations')
 return m,globaldefs

def mixed_control(work):
 defs=[dict(name=n,hunk=h,offset=p,external=False,context=c) for n,h,p,c in [('_mx_c_begin',0,0,'CSEG'),('_mx_c_end',0,12,'CSEG'),('_mx_a',1,0,'CSEG'),('_mx_b',1,9,'CSEG'),('_mx_d_begin',1,0,'DSEG'),('_mx_d_end',1,13,'DSEG'),('_mx_pattern',1,12,'DSEG')]]
 fix=[dict(hunk=h,offset=p,symbol=n,type='HUNK_RELOC32',width=4,addend=0) for h,p,n in [(0,0,'_mx_a'),(0,4,'_mx_b'),(0,8,'_mx_c_begin'),(1,4,'_mx_pattern')]]
 aj=object_mixed((work/'mixed.o').read_bytes(),{0:12,1:13},defs,fix)
 require(aj['sections']=={0:bytes.fromhex('000000000000000900000000'),1:bytes.fromhex('000185000000000c880102888600')},'independent cross-hunk pointer/typed header and terminal control')
 link_view((work/'mixed.exe').read_bytes(),(work/'mixed.sym').read_text(),[aj]);return dict(object_sha256=aj['object_sha256'],CODE=12,DATA=14,DATA_padding=1,named_relocations=4,game_credit=0)

def verify(root,blob,model,fact,batch=None):
 g,layout,objects,sem=validate(root,blob,model,fact);batch=doc(root,MANIFEST) if batch is None else batch;supports=support(root)
 require(set(batch)=={'schema_version','profile','facts','fact_sha256','job','request_sha256','receipt_sha256','artifacts','backend','backend_inputs'} and batch['schema_version']==5 and batch['profile']=='aztec36' and batch['facts']==[FACT] and batch['fact_sha256']=={FACT:sha256(json_bytes(fact))} and batch['backend']=='vamos','complete H1 batch pins')
 expected={'audio5.asm':types.source(objects,g),'mixed.asm':MIXED_SOURCE,'packed.asm':previous.packed_control(),'odd.asm':score.ODD_SOURCE};expected.update({s['prefix']+'.asm':read_source(root, s['source']) for s in supports})
 producer=score.audit_producer(root,batch,expected,commands_for(supports));work=candidate_path(root,Path(root)/batch['job']/'sys/work');mixed=mixed_control(work);odd=score.padding_control(work)
 cd=[dict(name='_packed_begin',offset=0,external=False),dict(name='_packed_end',offset=1000,external=False)]+[dict(name='_packed_%03d'%i,offset=800+i,external=False) for i in range(200)]
 cf=[dict(offset=4*i,symbol='_packed_%03d'%i,type='HUNK_RELOC32',width=4,addend=0) for i in range(200)]
 packed=previous.object_code((work/'packed.o').read_bytes(),1000,1000,cd,cf);require(packed['code']==b''.join((800+i).to_bytes(4,'big') for i in range(200))+bytes(range(200)),'whole packed-index control')
 pu=dict(sections={0:packed['code'],1:b''},definitions=[dict(d,hunk=0) for d in cd],fixups=[dict(f,hunk=0) for f in cf]);link_view((work/'packed.exe').read_bytes(),(work/'packed.sym').read_text(),[pu])
 defs=definition_plan(objects,sem);aj=object_mixed((work/'audio5.o').read_bytes(),{o['hunk']:o['typed_bytes'] for o in objects},defs,sem['fixups']);local={d['name']:d for d in defs};want={h:bytearray(b) for h,b in sem['sections'].items()}
 for f in sem['fixups']:want[f['hunk']][f['offset']:f['offset']+4]=local[f['symbol']]['offset'].to_bytes(4,'big')
 require(aj['sections']=={h:bytes(b) for h,b in want.items()},'whole mixed AJ differs from typed fields')
 from audio_score_catalogue import rederive
 _,oldlayout,_=rederive(root,blob,model,g['score']);olditems=score.members(doc(root,score.FACT),oldlayout)
 prior_objects=doc(root,previous.FACT)['objects'];prior_targets={c['values'][0] for ob in prior_objects for c in ob['rows'] if c['type'] in ('SELECTOR','ENVELOPE_PTR') or c['type'] in types.SPECS and types.SPECS[c['type']][1]==('target',)}|{'_G_h00_6200'}
 units=[aj]
 for s in supports:
  raw=(work/(s['prefix']+'.o')).read_bytes();require(sha256(raw)==s['object_sha256'],'unchanged canonical supporting AJ object differs')
  o=s['object']
  if s['provider']==score.IDENT:
   encoded=olditems[s['prefix']]['semantic'];sdefs=score.expected_definitions(o,encoded);a=score.object_code(raw,o['CODE'],sdefs,encoded['fixups']);sdefs=[dict(d,external=False) for d in sdefs];fix=encoded['fixups']
  else:
   encoded=types.old.encode(o,g);targets=prior_targets;sdefs=previous.definition_plan(o,encoded,targets);a=previous.object_code(raw,o['CODE'],o['typed_bytes'],sdefs,encoded['fixups']);fix=encoded['fixups']
  units.append(dict(sections={0:a['code'],1:b''},definitions=[dict(d,hunk=0) for d in sdefs],fixups=[dict(f,hunk=0) for f in fix]))
 link_view((work/'audio5all.exe').read_bytes(),(work/'audio5all.sym').read_text(),units)
 bi={(b['source_hunk'],b['source_offset']):b for b in layout['bindings']};reports=[]
 for o in objects:
  h=o['hunk'];mapped=bytearray(aj['sections'][h]);bindings=[]
  for part in o['parts']:
   a,z,ca,cz=[part[k] for k in ('original_start','original_end','candidate_start','candidate_end')]
   for f in sem['fixups']:
    if f['hunk']==h and ca<=f['offset']<cz:
     require(f['offset']+4<=cz,'straddling typed part');b=bi[h,a+f['offset']-ca];require(b['symbol']==f['symbol'],'independent original named target differs');mapped[f['offset']:f['offset']+4]=b['addend_raw'].to_bytes(4,'big');bindings.append(dict(b,object_offset=f['offset']))
   require(mapped[ca:cz]==payload(blob,model,h)[a:z],'complete original typed fields differ')
  require(mapped[o['typed_bytes']:]==bytes(o['allocated_bytes']-o['typed_bytes']),'implicit assembler alignment differs')
  parts=o['credit_parts'];reports.append(dict(id=IDENT+'_h%d'%h,kind=KIND,original=dict(hunk=h,start=min(p['original_start'] for p in parts),end=max(p['original_end'] for p in parts),size=sum(p['original_end']-p['original_start'] for p in parts)),parts=parts,typed_bytes=o['credit_bytes'],category='TYPED_CODE_DATA' if h==0 else 'RECOVERED_DATA',bindings=bindings,padding_credit=0))
 return dict(id=IDENT,kind=KIND,objects=reports,typed_bytes=sum(o['credit_bytes'] for o in objects),credit_by_hunk={str(o['hunk']):o['credit_bytes'] for o in objects},credit_by_category={('TYPED_CODE_DATA' if o['hunk']==0 else 'RECOVERED_DATA'):o['credit_bytes'] for o in objects},source_sha256=fact['source_sha256'],fact_sha256=sha256(json_bytes(fact)),object_sha256=aj['object_sha256'],producer=producer,mixed_control=mixed,padding_control=odd,packed_index_control=dict(max_index=201,object_sha256=packed['object_sha256'],game_credit=0),roots=layout['roots'],streams=layout['streams'],stop_roots=layout['stop_roots'],envelope_views=layout['envelope_views'],selector_prefix_count=len(layout['selector_prefix']),new_named_relocations=sum(1 for b in layout['bindings'] if any(o['hunk']==b['source_hunk'] and p['original_start']<=b['source_offset']<p['original_end'] for o in objects for p in o['credit_parts'])),exports=[dict(symbol='_G_h00_6200_complete',hunk=0,offset=0x6200,object='audio5',object_offset=0)]+[dict(symbol=types.symbol(1,'h',r['entry']),hunk=1,offset=r['entry'],object='audio5',object_offset=next(d['offset'] for d in defs if d['name']==types.symbol(1,'h',r['entry']))) for r in layout['roots']],c_bytes=0,asm_instruction_bytes=0,padding_credit=0,historical_owner='UNKNOWN',historical_tu='UNKNOWN',natural_root_layout_proof=False,verifier_identity={n:sha256(Path(__import__(n).__file__).read_bytes()) for n in ('audio_h1_catalogue','audio_h1_provider','audio_score_measured','audio_score_grammar','audio_stateful_catalogue','data_provider_vamos')})

@shared
def rows(root,blob,model,analysis,ledger):
 item=ledger.get(MAP,{}).get(IDENT)
 if item is None:return []
 require(set(item)=={'state','fact','sources','proof','proof_sha256'} and item['state']=='DATA_LAYOUT_MATCH' and item['fact']==FACT and item['proof']=='recovery/proofs/code-data/'+IDENT+'.json','H1 provider canonical identity')
 fact=doc(root,FACT);report=verify(root,blob,model,fact);require(item['sources']=={SOURCE:fact['source_sha256']} and read_source(root, SOURCE)==canonical_path(root,CANDIDATE).read_bytes(),'H1 canonical source differs')
 raw=canonical_path(root,item['proof']).read_bytes();proof=json.loads(raw);require(sha256(raw)==item['proof_sha256'] and set(proof)=={'fact','comparison','regression'} and proof['fact']==fact and proof['regression'].get('passed') is True,'H1 canonical proof/gate')
 comparable=lambda r:{k:v for k,v in r.items() if k!='verifier_identity'};require(comparable(proof['comparison'])==comparable(report),'H1 canonical receipt no longer rederives')
 return [dict(o,acceptance=True,source_acceptance=True,proof_level='DATA_LAYOUT_MATCH',proof=item['proof'],producer=report['producer'],provider=IDENT) for o in report['objects']]

def contributions(root,records):
 if not records:return []
 fact=doc(root,FACT);objects=fact['objects'];from game_image import game
 blob,model,_=game();g=types.old.contract(blob,model);sem=types.encode(objects,g);defs=definition_plan(objects,sem);job=records[0]['producer']['job']
 require(all(r['producer']['job']==job and r.get('acceptance') is True for r in records),'one exact canonical H1 provider')
 work=candidate_path(root,Path(root)/job/'sys/work');aj=object_mixed((work/'audio5.o').read_bytes(),{o['hunk']:o['typed_bytes'] for o in objects},defs,sem['fixups']);result=[]
 for r in records:
  h=r['original']['hunk'];out=bytearray(aj['sections'][h])
  for b in r['bindings']:out[b['object_offset']:b['object_offset']+4]=b['addend_raw'].to_bytes(4,'big')
  for i,p in enumerate(r['parts']):
   a,z=p['original_start'],p['original_end'];rels=[{k:b[k] for k in ('source_offset','target_hunk','type','width','addend_raw')} for b in r['bindings'] if a<=b['source_offset']<z]
   result.append(dict(id=r['id']+'_part%d'%i,hunk=h,start=a,end=z,category=r['category'],bytes=bytes(out[p['candidate_start']:p['candidate_end']]),relocations=rels))
 return result


def input_identity(root):
 names={FACT,MANIFEST,CANDIDATE};path=canonical_path(root,MANIFEST)
 if path.exists():
  batch=doc(root,MANIFEST);job=batch['job'];names.update(job+'/'+n for n in ('request.json','result.json','worker.uae','kick.rom','sys/s/startup-sequence'));names.update(job+'/sys/work/'+n for n in batch['artifacts']);names.update(batch['backend_inputs'])
  request=json.loads(candidate_path(root,Path(root)/job/'request.json').read_bytes());names.update(p['path'] for p in request['pinned_inputs'])
  for folder in ('c','l','libs','devs'):names.update(p.relative_to(root).as_posix() for p in active_files(Path(root)/job/'sys'/folder))
 item=(doc(root,'recovery/ledger.json') if canonical_path(root,'recovery/ledger.json').exists() else {}).get(MAP,{}).get(IDENT)
 if item:names.update([SOURCE,item['proof']])
 def resolve(n):return candidate_path(root,Path(root)/n) if n.startswith('build/') else canonical_path(root,n)
 return {str(resolve(n)):sha256((read_source(root, resolve(n)) if n.startswith('src/') else resolve(n).read_bytes())) if (source_file(root, resolve(n)) if n.startswith('src/') else resolve(n)).exists() else None for n in sorted(names)}
