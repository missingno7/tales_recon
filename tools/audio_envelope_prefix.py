"""Complete typed envelope-pointer access prefix, with legacy support retained.

A rooted ENVELOPE operand bounds the paired attack/release pointer prefix.
Every newly reached envelope byte gets its role from the decoded driver grammar.
Only new fields earn TYPED_CODE_DATA; prior source stays accepted and unchanged.
"""
from names import read_source, source_path as source_file
from collections import defaultdict
from pathlib import Path
from common import require,sha256,json_bytes
from repo_paths import canonical_path,candidate_path,active_files
from validation_memo import shared
from audio_sequence_data import payload,field
from hunk import parse
from overlay_experiment import symbols
import audio_stateful_catalogue as types
import audio_stateful_provider as previous
import audio_h1_provider as h1
import audio_score_measured as score

IDENT='resident_audio_envelope_prefix_0006'
FACT='evidence/code-data-providers/envelope-prefix-0006.json'
MANIFEST='evidence/code-data-providers/batch-0006.json'
KIND='MEASURED_TYPED_ENVELOPE_PREFIX'
CATEGORY='TYPED_CODE_DATA'
MAP='code_data_providers'
RULES='evidence/rules/audio-envelope-prefix-0006/'


def doc(root,name):return __import__('json').loads(canonical_path(root,name).read_bytes())

def renamed(name):return name.replace('_audio4_','_audio6_')


def partition(objects,occupied):
 for o in objects:
  o['credit_parts']=[];o['support_parts']=[]
  for p in o['parts']:
   a,z,ca=p['original_start'],p['original_end'],p['candidate_start'];q=a
   while q<z:
    support=q in occupied;end=q+1
    while end<z and (end in occupied)==support:end+=1
    o['support_parts' if support else 'credit_parts'].append(dict(original_start=q,original_end=end,candidate_start=ca+q-a,candidate_end=ca+end-a));q=end
  o['credit_bytes']=sum(p['original_end']-p['original_start'] for p in o['credit_parts'])


def derive(root,blob,model):
 g=types.contract(blob,model);code=payload(blob,model,0);rel={r['source_offset']:r for r in model['relocations'] if r['source_hunk']==0}
 supports=[doc(root,previous.FACT),doc(root,h1.FACT)]
 operand_rows=[c for f in supports for o in f['objects'] for c in o['rows'] if c['type']=='ENVELOPE']
 require(operand_rows,'no rooted typed envelope operand')
 highest=max(c['values'][0] for c in operand_rows)
 require(highest%2==0,'paired prefix needs an even rooted selector operand')
 # The driver consumes the selected pointer and its adjacent release pointer.
 # Highest+2 bounds a reconstructed prefix, never a historical capacity.
 count=highest+2;require(0x5e6c+4*count<=0x5fac,'pointer prefix crosses independently decoded envelope fields')
 roles=defaultdict(set);bindings=[];views=[]
 for index in range(0,count,2):
  v,rs,bs=types.envelopes(code,rel,index);views.extend(v);bindings.extend(bs)
  for p,kinds in rs.items():roles[p].update(kinds)
 rows=[dict(offset=b['source_offset'],type='ENVELOPE_PTR',values=[b['symbol']]) for b in bindings]
 rows += [dict(offset=p,type='ENVELOPE_FIELD',roles=sorted(kinds),values=[code[p]]) for p,kinds in roles.items()]
 rows.sort(key=lambda c:c['offset'])
 for c in rows:types.check(c)
 layout=dict(rows=rows,bindings=sorted(bindings,key=lambda b:b['source_offset']),views=views,highest_rooted_operand=highest,pointer_prefix_count=count,bounds='ROOTED_PAIRED_POINTER_ACCESS_PREFIX; CAPACITY_UNKNOWN')
 objects=types.plan(layout,g)
 occupied={q for f in supports for o in f['objects'] if o.get('hunk',0)==0 for p in o['parts'] for q in range(p['original_start'],p['original_end'])}
 for j,o in enumerate(objects):
  prefix='r6%02d'%j;o.update(id=IDENT+'_'+prefix,prefix=prefix,source='src/recovered/code-data/'+prefix+'.asm',candidate=RULES+prefix+'.asm')
 partition(objects,occupied)
 return g,layout,objects


def encode(o,g):
 s=types.encode(o,g)
 return dict(code=s['code'],definitions=[dict(d,name=renamed(d['name'])) for d in s['definitions']],fixups=[dict(f,symbol=renamed(f['symbol'])) for f in s['fixups']])


def definitions(o,sem,targets):
 local={d['name']:d['offset'] for d in sem['definitions']};used={f['symbol'] for f in sem['fixups']}
 global_base=[dict(name='_G_h00_5E6C',offset=next(p['candidate_start'] for p in o['parts'] if p['original_start']==0x5e6c),external=False)] if any(p['original_start']==0x5e6c for p in o['parts']) else []
 return [dict(name='_'+o['prefix']+'_begin',offset=0,external=False),dict(name='_'+o['prefix']+'_end',offset=o['typed_bytes'],external=False)]+global_base+[dict(name=n,offset=local[n],external=False) for n in sorted(local.keys()&targets)]+[dict(name=n,offset=0,external=True) for n in sorted(used-local.keys())]


def source(o,g,targets):
 sem=encode(o,g);defs=definitions(o,sem,targets);names={d['name'] for d in defs if not d['external']};lines=['; Typed envelope DATA only. Historical source/TU/owner UNKNOWN.']
 for name,body in [('PTR','dc.l \\1'),('INITIAL','dc.b \\1'),('DELTA','dc.b \\1'),('TARGET','dc.b \\1'),('DELAY','dc.b \\1'),('ZERO','dc.b 0')]:lines+=['E6_'+name+' macro','\t'+body,'\tendm']
 lines+=['\tcseg']+['\tpublic '+d['name'] for d in defs]+[defs[0]['name']+':']
 for c in o['rows']:
  if c['offset']==0x5e6c:lines.append('_G_h00_5E6C:')
  sym=renamed(types.row_symbol(c))
  if sym in names:lines.append(sym+':')
  if c['type']=='ENVELOPE_PTR':lines.append('\tE6_PTR '+renamed(c['values'][0]))
  else:
   role=next(k for k in ('ZERO','DELTA','DELAY','INITIAL','TARGET') if k in c['roles']);v=c['values'][0]
   lines.append('\tE6_'+role+(' '+str(v-256 if role=='DELTA' and v>=128 else v) if role!='ZERO' else ''))
 return ('\n'.join(lines+[defs[1]['name']+':','\tend',''])).encode('ascii')


def exclude_code_candidates(analysis,ledger,points,typed_refs):
 # Relocation-only CFG candidates are not independent executable entries.
 # Every incoming pointer must instead bind to this decoded DATA reader or
 # to a typed pointer in this provider; a real caller/entry still rejects.
 for f in analysis['functions']:
  if f['hunk']!=0 or not any(f['start']<=p<f['end'] for p in points):continue
  require(not f.get('callers') and f.get('entry_evidence'),'envelope DATA has an executable caller or unknown entry')
  require(not any(f['id'] in ledger.get(k,{}) for k in ('functions','behavioral_functions','dead_code_functions','mixed_source_objects','reconstructed_asm')),'envelope DATA overlaps accepted executable source')
  require(all(e['kind']=='RELOCATION_POINTER' and (e['source_hunk'],e['source_offset']) in typed_refs for e in f['entry_evidence']),'envelope candidate has an independent code entry or untyped incoming pointer')


def validate(root,blob,model,fact):
 require(set(fact)=={'schema_version','id','oracle_sha256','contract_sha256','layout_sha256','support_facts','objects','historical_owner','historical_tu','original_filename'},'closed envelope-prefix fact')
 require(fact['schema_version']==6 and fact['id']==IDENT and fact['historical_owner']==fact['historical_tu']=='UNKNOWN' and fact['original_filename'] is None,'envelope prefix identity/provenance')
 ledger=doc(root,'recovery/ledger.json');analysis=doc(root,'evidence/functions/ledger.json')
 require(previous.IDENT in ledger.get(MAP,{}) and h1.IDENT in ledger[MAP],'rooted canonical support must precede envelope prefix')
 previous.rows(root,blob,model,analysis,ledger);h1.rows(root,blob,model,analysis,ledger)
 support={n:sha256(json_bytes(doc(root,n))) for n in (previous.FACT,h1.FACT)}
 require(fact['support_facts']==support and fact['oracle_sha256']==sha256(blob),'changed source support or oracle')
 g,layout,objects=derive(root,blob,model);targets={renamed(b['symbol']) for b in layout['bindings']}
 for o in objects:o['source_sha256']=sha256(source(o,g,targets))
 require(fact['contract_sha256']==sha256(json_bytes(g)) and fact['layout_sha256']==sha256(json_bytes(layout)) and fact['objects']==objects,'changed typed prefix bounds/fields/targets/credit')
 points={p for o in objects for part in o['parts'] for p in range(part['original_start'],part['original_end'])}
 typed_refs={(b['source_hunk'],b['source_offset']) for b in layout['bindings']+g['consumer_relocations']}
 exclude_code_candidates(analysis,ledger,points,typed_refs)
 for o in objects:require(canonical_path(root,o['candidate']).read_bytes()==source(o,g,targets),'source is not strict typed envelope macros')
 return g,layout,targets


def commands_for(fact):
 ps=[o['prefix'] for o in fact['objects']]
 return ['Old1:bin/as -o '+p+'.o '+p+'.asm >'+p+'-as.log' for p in ps]+['Old1:bin/ln -m -t -o envelopes.exe '+' '.join(p+'.o' for p in ps)+' >envelopes-ln.log','Old1:bin/as -o packed.o packed.asm >packed-as.log','Old1:bin/ln -m -t -o packed.exe packed.o >packed-ln.log','Old1:bin/as -o odd.o odd.asm >odd-as.log','Old1:bin/ln -m -t -o odd.exe odd.o >odd-ln.log']


def verify(root,blob,model,fact,batch=None):
 g,layout,targets=validate(root,blob,model,fact);batch=doc(root,MANIFEST) if batch is None else batch
 require(set(batch)=={'schema_version','profile','facts','fact_sha256','job','request_sha256','receipt_sha256','artifacts','backend','backend_inputs'} and batch['schema_version']==6 and batch['profile']=='aztec36' and batch['facts']==[FACT] and batch['fact_sha256']=={FACT:sha256(json_bytes(fact))},'one complete pinned envelope producer batch')
 expected={o['prefix']+'.asm':source(o,g,targets) for o in fact['objects']};expected.update({'packed.asm':previous.packed_control(),'odd.asm':score.ODD_SOURCE})
 producer=score.audit_producer(root,batch,expected,commands_for(fact));work=candidate_path(root,Path(root)/producer['job']/'sys/work');odd=score.padding_control(work)
 cd=[dict(name='_packed_begin',offset=0,external=False),dict(name='_packed_end',offset=1000,external=False)]+[dict(name='_packed_%03d'%i,offset=800+i,external=False) for i in range(200)]
 cf=[dict(offset=4*i,symbol='_packed_%03d'%i,type='HUNK_RELOC32',width=4,addend=0) for i in range(200)]
 packed=previous.object_code((work/'packed.o').read_bytes(),1000,1000,cd,cf);cc=b''.join((800+i).to_bytes(4,'big') for i in range(200))+bytes(range(200))
 linked=(work/'packed.exe').read_bytes();lm=parse(linked)
 require(packed['code']==cc and payload(linked,lm,0)==cc and [(h['type'],h['allocated_size'],h['initialized_size']) for h in lm['hunks']]==[('CODE',1000,1000),('DATA',0,0),('BSS',4,0)],'independent complete packed-index control')
 require(symbols((work/'packed.sym').read_text())=={**{(0,d['name']):d['offset'] for d in cd},(0,'__H0_org'):0,(0,'__H0_end'):1000,(1,'__H1_org'):0,(1,'__H1_end'):0,(2,'__H2_org'):0,(2,'__H2_end'):0},'packed control whole symbols')
 require(sorted(map(field,lm['relocations']),key=lambda b:b['source_offset'])==[dict(source_hunk=0,source_offset=4*i,target_hunk=0,addend_raw=800+i,type='HUNK_RELOC32',width=4) for i in range(200)],'packed control all relocations')
 units=[];all_defs={};base=0
 for o in fact['objects']:
  sem=encode(o,g);defs=definitions(o,sem,targets);aj=previous.object_code((work/(o['prefix']+'.o')).read_bytes(),o['CODE'],o['typed_bytes'],defs,sem['fixups']);local={d['name']:d['offset'] for d in defs if not d['external']};want=bytearray(sem['code']+bytes(o['typed_bytes']%2))
  for f in sem['fixups']:want[f['offset']:f['offset']+4]=local.get(f['symbol'],0).to_bytes(4,'big')
  require(aj['code']==want,'whole AJ object differs from typed fields')
  for d in defs:
   if not d['external']:require(d['name'] not in all_defs,'duplicate envelope definition');all_defs[d['name']]=base+d['offset']
  units.append((o,sem,defs,aj,base));base+=o['CODE']
 linked=(work/'envelopes.exe').read_bytes();lm=parse(linked);lc=payload(linked,lm,0);total=(base+3)&~3
 require([(h['type'],h['allocated_size'],h['initialized_size']) for h in lm['hunks']]==[('CODE',total,total),('DATA',0,0),('BSS',4,0)],'complete envelope link topology')
 require(symbols((work/'envelopes.sym').read_text())=={**{(0,n):v for n,v in all_defs.items()},(0,'__H0_org'):0,(0,'__H0_end'):total,(1,'__H1_org'):0,(1,'__H1_end'):0,(2,'__H2_org'):0,(2,'__H2_end'):0},'complete envelope link symbol inventory')
 rels=[];reports=[];original=payload(blob,model,0);bi={b['source_offset']:b for b in layout['bindings']}
 for o,sem,defs,aj,at in units:
  want=bytearray(aj['code']);mapped=bytearray(aj['code']);bindings=[]
  for f in sem['fixups']:
   require(f['symbol'] in all_defs,'unbound envelope target');v=all_defs[f['symbol']];want[f['offset']:f['offset']+4]=v.to_bytes(4,'big');rels.append(dict(source_hunk=0,source_offset=at+f['offset'],target_hunk=0,addend_raw=v,type='HUNK_RELOC32',width=4))
  require(lc[at:at+o['CODE']]==want,'entire linked envelope object differs')
  for part in o['parts']:
   a,z,ca,cz=[part[k] for k in ('original_start','original_end','candidate_start','candidate_end')]
   for f in sem['fixups']:
    if ca<=f['offset']<cz:
     require(f['offset']+4<=cz,'straddling pointer field');b=bi[a+f['offset']-ca];require(renamed(b['symbol'])==f['symbol'],'independent named envelope target differs');mapped[f['offset']:f['offset']+4]=b['addend_raw'].to_bytes(4,'big');bindings.append(dict(b,symbol=f['symbol'],object_offset=f['offset']))
   require(mapped[ca:cz]==original[a:z],'every typed field and symbolic pointer must equal original DATA')
  require(mapped[o['typed_bytes']:]==bytes(o['CODE']-o['typed_bytes']),'implicit alignment differs')
  ps=o['credit_parts'];bounds=ps or o['parts'];reports.append(dict(id=o['id'],prefix=o['prefix'],kind=KIND,category=CATEGORY,original=dict(hunk=0,start=min(p['original_start'] for p in bounds),end=max(p['original_end'] for p in bounds),size=o['credit_bytes']),parts=ps,all_parts=o['parts'],typed_bytes=o['credit_bytes'],logical_size=o['typed_bytes'],CODE=o['CODE'],object_definitions=defs,bindings=bindings,object_sha256=aj['object_sha256'],padding_credit=0))
 require(lc[base:]==bytes(total-base) and sorted(map(field,lm['relocations']),key=lambda b:b['source_offset'])==sorted(rels,key=lambda b:b['source_offset']),'entire link tail/relocation inventory')
 return dict(id=IDENT,kind=KIND,category=CATEGORY,objects=reports,typed_bytes=sum(o['credit_bytes'] for o in fact['objects']),producer=producer,contract_sha256=fact['contract_sha256'],layout_sha256=fact['layout_sha256'],fact_sha256=sha256(json_bytes(fact)),prefix_count=layout['pointer_prefix_count'],highest_rooted_operand=layout['highest_rooted_operand'],padding_control=odd,packed_index_control=dict(max_index=201,object_sha256=packed['object_sha256'],game_credit=0),exports=[dict(symbol='_G_h00_5E6C',hunk=0,offset=0x5e6c,object=o['prefix'],object_offset=d['offset']) for o,sem,defs,aj,at in units for d in defs if d['name']=='_G_h00_5E6C'],c_bytes=0,asm_instruction_bytes=0,padding_credit=0,historical_owner='UNKNOWN',historical_tu='UNKNOWN',natural_root_layout_proof=False,verifier_identity={n:sha256(canonical_path(root,'tools/'+n).read_bytes()) for n in ['audio_envelope_prefix.py','audio_stateful_catalogue.py','audio_stateful_provider.py','audio_h1_provider.py','audio_score_measured.py']})


@shared
def rows(root,blob,model,analysis,ledger):
 item=ledger.get(MAP,{}).get(IDENT)
 if item is None:return []
 require(set(item)=={'state','fact','sources','proof','proof_sha256'} and item['state']=='DATA_LAYOUT_MATCH' and item['fact']==FACT and item['proof']=='recovery/proofs/code-data/'+IDENT+'.json','canonical envelope identity')
 fact=doc(root,FACT);report=verify(root,blob,model,fact)
 require(item['sources']=={o['source']:o['source_sha256'] for o in fact['objects']},'canonical envelope source inventory')
 for o in fact['objects']:require(read_source(root, o['source'], names_root=None)==canonical_path(root,o['candidate']).read_bytes(),'canonical envelope source differs')
 raw=canonical_path(root,item['proof']).read_bytes();proof=__import__('json').loads(raw)
 require(sha256(raw)==item['proof_sha256'] and set(proof)=={'fact','comparison','regression'} and proof['fact']==fact and proof['regression'].get('passed') is True,'canonical envelope proof/gate')
 comparable=lambda r:{k:v for k,v in r.items() if k!='verifier_identity'}
 require(comparable(proof['comparison'])==comparable(report),'envelope proof no longer rederives')
 return [dict(o,producer=report['producer'],acceptance=True,source_acceptance=True,proof_level='DATA_LAYOUT_MATCH',proof=item['proof'],provider=IDENT) for o in report['objects']]


def contributions(root,records):
 out=[]
 for r in records:
  require(r.get('acceptance') is True,'canonical envelope replay required');fix=[dict(offset=b['object_offset'],symbol=b['symbol'],type=b['type'],width=b['width'],addend=0) for b in r['bindings']];fix.sort(key=lambda f:f['offset'])
  raw=candidate_path(root,Path(root)/r['producer']['job']/('sys/work/'+r['prefix']+'.o')).read_bytes();aj=previous.object_code(raw,r['CODE'],r['logical_size'],r['object_definitions'],fix);data=bytearray(aj['code'])
  for b in r['bindings']:data[b['object_offset']:b['object_offset']+4]=b['addend_raw'].to_bytes(4,'big')
  for j,p in enumerate(r['parts']):
   a,z=p['original_start'],p['original_end'];rels=[{k:b[k] for k in ('source_offset','target_hunk','type','width','addend_raw')} for b in r['bindings'] if a<=b['source_offset']<z]
   out.append(dict(id=r['id']+'_part%d'%j,hunk=0,start=a,end=z,category=CATEGORY,bytes=bytes(data[p['candidate_start']:p['candidate_end']]),relocations=rels))
 return out


def input_identity(root):
 root=Path(root);names={FACT,MANIFEST};external={};fact=doc(root,FACT) if canonical_path(root,FACT).exists() else {}
 names.update(o['candidate'] for o in fact.get('objects',[]))
 if canonical_path(root,MANIFEST).exists():
  batch=doc(root,MANIFEST);job=batch['job'];names.update(job+'/'+n for n in ['request.json','result.json','worker.uae','kick.rom','sys/s/startup-sequence']);names.update(job+'/sys/work/'+n for n in batch['artifacts']);request=__import__('json').loads(candidate_path(root,root/job/'request.json').read_bytes());names.update(p['path'] for p in request['pinned_inputs']);names.update(['toolchain/candidate-lock.json','evidence/toolchain/aztec-3.6a.json','evidence/toolchain/aztec-5.0a.json']);names.add(doc(root,'toolchain/candidate-lock.json')['archive']);names.update(batch['backend_inputs'])
  for folder in ('c','l','libs','devs'):names.update(p.relative_to(root).as_posix() for p in active_files(root/job/'sys'/folder))
  external[request['emulator']]=sha256(Path(request['emulator']).read_bytes())
 item=(doc(root,'recovery/ledger.json') if canonical_path(root,'recovery/ledger.json').exists() else {}).get(MAP,{}).get(IDENT)
 if item:names.update([item['fact'],item['proof'],*item['sources']])
 def path(n):return candidate_path(root,root/n) if n.startswith('build/') else canonical_path(root,n)
 return {**{str(path(n)):sha256((read_source(root, path(n), names_root=None) if n.startswith('src/') else path(n).read_bytes())) if (source_file(root, path(n)) if n.startswith('src/') else path(n)).exists() else None for n in sorted(names)},**external}
