"""Rooted measured audio fields; types rederived from decoded driver instructions."""
import json
from collections import defaultdict
from common import require,sha256,json_bytes,FormatError
from audio_sequence_data import payload,field
from audio_score_grammar import derive,instructions
from audio_score_commands import SPECS as OLD,integer
INTERVAL=(0x5e6c,0x704e)
SPECS=dict(OLD,FLAGS=(0x83,('value',)),RAMP_OFF=(0x92,()),RANDOM_NOTE=(0x99,('mask',)),CHANNEL_ATTENUATION=(0x9e,('value',)),SOUND_ENABLE=(0x9f,('value',)),MASTER_ATTENUATION=(0xa3,('value',)),ADD_MASTER_ATTENUATION=(0xa4,('delta',)))
BY_OPCODE={op:name for name,(op,_) in SPECS.items()}
NEW={0x83:('move.b','d0, $44(a0)'),0x92:('clr.l','$e(a0)'),0x99:('move.b','d0, d1'),0x9e:('move.b','d0, $46(a0)'),0x9f:('move.b','d0, $2b8d.l'),0xa3:('move.b','d0, $2b8c.l'),0xa4:('add.b','d0, $2b8c.l')}
def doc(root,name):return json.loads((root/name).read_bytes())
def symbol(k,p):return '_audio3_%s_%04X'%(k,p)
def contract(blob,model):
 g=derive(blob,model);code=payload(blob,model,0);ins=instructions(code,0x5a50,0x5e6c)
 for row in g['opcodes']:
  if row['opcode'] in NEW:
   require(ins[row['handler']][:2]==NEW[row['opcode']],'new handler meaning changed')
   require(row['forms'] is not None and all(f['length']==(1 if row['opcode']==0x92 else 2) and f['flows']==['NEXT'] for f in row['forms']),'new consumption changed')
 e=instructions(code,0x544c,0x558a)
 checks={0x5454:('move.b','$1f(a0), d3'),0x5458:('movea.l','$1a(a0), a3'),0x545e:('move.b','$1e(a0), d0'),0x5462:('lsl.l','#$2, d0'),0x5464:('lea.l','$2b6e.l, a2'),0x546a:('movea.l','(a2, d0.w), a2'),0x546e:('jsr','(a2)'),0x54b6:('tst.b','(a3, d3.w)'),0x54ba:('bne.b','$54de'),0x54bc:('addq.w','#$1, d3'),0x54be:('tst.b','(a3, d3.w)'),0x54c2:('bne.b','$54ca'),0x54c4:('clr.b','$1e(a0)'),0x54ca:('move.b','#$4, $1e(a0)'),0x54d0:('move.b','(a3, d3.w), $21(a0)'),0x54d6:('addq.b','#$1, d3'),0x54d8:('move.b','d3, $1f(a0)'),0x54de:('bmi.b','$54e8'),0x54e0:('move.b','#$2, $1e(a0)'),0x54e8:('move.b','#$3, $1e(a0)'),0x54ee:('move.b','(a3, d3.w), $20(a0)'),0x54f4:('addq.b','#$1, d3'),0x54f6:('move.b','(a3, d3.w), $21(a0)'),0x54fc:('addq.b','#$1, d3'),0x5504:('move.l','$40(a0), d0'),0x5508:('move.l','d0, $1a(a0)'),0x550c:('movea.l','d0, a3'),0x550e:('clr.l','d3'),0x5510:('bsr.b','$54b6'),0x5514:('move.b','(a3, d3.w), $22(a0)'),0x551a:('addq.w','#$1, d3'),0x551c:('bsr.b','$54b6'),0x554c:('beq.b','$5558'),0x5558:('tst.b','$21(a0)'),0x555c:('bne.b','$5568'),0x5562:('clr.b','$1e(a0)'),0x5570:('jsr','$54b6(pc)'),0x557a:('subq.b','#$1, $21(a0)'),0x5586:('bra.w','$54b6')}
 require(all(e[p][:2]==v for p,v in checks.items()),'envelope field/cursor contract changed')
 rel={(r['source_hunk'],r['source_offset']):field(r) for r in model['relocations']};states=[]
 for i,t in enumerate((0x5514,0x5514,0x5520,0x5542,0x557a,0x5504)):
  want=dict(source_hunk=1,source_offset=0x2b6e+4*i,target_hunk=0,addend_raw=t,type='HUNK_RELOC32',width=4)
  require(rel.get((1,want['source_offset']))==want,'envelope state handler binding changed');states.append(want)
 init=instructions(code,0x533e,0x534a)
 require([x[:2] for x in init.values()]==[('lea.l','$6200.l, a0'),('move.l','a0, $b39a.l')],'selector initialization changed')
 start=instructions(code,0x57e4,0x5800)
 require(start[0x57e8][:2]==('and.l','#$ff, d0') and start[0x57ee][:2]==('lsl.l','#$2, d0') and start[0x57f0][:2]==('movea.l','$b39a.l, a0') and start[0x57f6][:2]==('movea.l','(a0, d0.l), a0'),'selector index/width changed')
 envsel=instructions(code,0x5b8c,0x5baa)
 require([x[:2] for x in envsel.values()]==[('and.w','#$ff, d0'),('lsl.w','#$2, d0'),('lea.l','$5e6c.l, a2'),('move.l','(a2, d0.w), $3c(a0)'),('addq.w','#$4, d0'),('move.l','(a2, d0.w), $40(a0)'),('bra.w','$5a76')],'envelope pair selection changed')
 require(all(ins[p][:2]==v for p,v in {0x5ab0:('move.b','#$1, $1e(a0)'),0x5ab6:('clr.b','$1f(a0)'),0x5aba:('move.l','$3c(a0), d0'),0x5abe:('move.l','d0, $1a(a0)')}.items()),'attack initial-state contract changed')
 update=instructions(code,0x58bc,0x59a4)
 require(update[0x5930][:2]==('move.b','#$5, $1e(a0)') and update[0x5936][:2]==('bsr.w','$544c'),'release-state transition changed')
 anchors=[dict(start=a,end=z,sha256=sha256(code[a:z])) for a,z in ((0x533e,0x534a),(0x544c,0x558a),(0x57e4,0x5868),(0x58bc,0x59a4),(0x5a50,0x5e6c))]
 return dict(score=g,envelope_states=states,anchors=anchors,consumer_relocations=[rel[0,p] for p in (0x5340,0x5346,0x5466,0x57f2,0x5b94)],envelope_fields=dict(initial='U8',delta='I8_NONZERO',target='U8',delay='U8_NONZERO',terminal=[0,0],negative_zero_target_terminal=True,cursor_bits=8))
def form(g,op,p):
 if op<128:return g['score']['note_forms'][p%2]
 require(op in BY_OPCODE,'unknown, unused or state-dependent audio opcode 0x%02X'%op)
 row=next(x for x in g['score']['opcodes'] if x['opcode']==op)
 require(row['forms'] is not None and row['forms'][p%2]['length'] is not None,'variable grammar length')
 return row['forms'][p%2]
def envelopes(code,rel,index):
 views=[];roles=defaultdict(set);bindings=[]
 for release in (False,True):
  site=0x5e6c+4*(index+release);r=rel.get(site)
  require(r is not None and r['type']=='HUNK_RELOC32' and r['width']==4 and r['target_hunk']==0,'unproved envelope pointer pair')
  p=r['addend_raw'];entry=p;require(0x5fac<=p<0x615e,'envelope pointer to unproved record')
  bindings.append(dict(field(r),symbol=symbol('e',p)))
  if not release:roles[p].add('INITIAL');p+=1
  steps=[]
  while True:
   require(p+2<=0x615e and p+2-entry<=256,'envelope lacks terminal before cursor/boundary')
   a,b=code[p:p+2]
   if a==0:
    roles[p].add('ZERO');roles[p+1].add('ZERO' if b==0 else 'DELAY');steps.append(dict(offset=p,command='END' if b==0 else 'WAIT'))
   else:roles[p].add('DELTA');roles[p+1].add('TARGET');steps.append(dict(offset=p,command='RAMP_DOWN_END' if a>=128 and b==0 else 'RAMP'))
   p+=2
   if a==b==0 or a>=128 and b==0:break
  views.append(dict(index=index,release=release,entry=entry,end=p,steps=steps))
 return views,roles,bindings
def length(c,g):
 if c['type'] in ('SELECTOR','ENVELOPE_PTR'):return 4
 if c['type']=='ENVELOPE_FIELD':return 1
 if c['type']=='HEADER':return 2
 return form(g,c['values'][0] if c['type']=='NOTE' else SPECS[c['type']][0],c['offset'])['length']
def discover(root,blob,model,g):
 code=payload(blob,model,0);rel={r['source_offset']:r for r in model['relocations'] if r['source_hunk']==0};old=doc(root,'evidence/code-data-providers/score.json')
 oldheaders={c['offset'] for c in old['commands'] if c['command']=='HEADER'};triggers=[c for c in old['commands'] if c['command']=='TRIGGER'];highest=max(c['operands']['identifier'] for c in triggers)
 # The accepted root-reached command TRIGGER 175 supplies independent positive
 # indexed-access extent evidence. Each prefix slot additionally needs RELOC32.
 require(highest==175,'independently accessed selector prefix changed')
 rows={};bindings={};roots=[];blocked=[];env_indexes={c['operands']['identifier'] for c in old['commands'] if c['command']=='ENVELOPE'}
 for index in range(highest+1):
  site=0x6200+4*index;r=rel.get(site);local={};lb={};ei=set();entry=None
  try:
   require(r is not None and r['type']=='HUNK_RELOC32' and r['width']==4,'selector field missing relocation')
   entry=r['addend_raw'];require(r['target_hunk']==0,'selector target is unproved H1 data')
   if entry in oldheaders:target='_audio_h_%04X'%entry
   else:
    require(0x64c0<=entry<INTERVAL[1] and code[entry]<4,'unproved selector header')
    local[entry]=dict(offset=entry,type='HEADER',values=[code[entry],code[entry+1]]);todo=[entry+2];seen=set()
    while todo:
     p=todo.pop()
     if p in seen:continue
     seen.add(p);require(0x64c0<=p<INTERVAL[1],'pointer to unproved stream')
     op=code[p];sh=form(g,op,p);z=p+sh['length'];require(z<=INTERVAL[1],'partial stream');name='NOTE' if op<128 else BY_OPCODE[op];targets=[]
     if sh['pointer_field'] is not None:
      q=p+sh['pointer_field'];rr=rel.get(q);require(rr is not None and rr['type']=='HUNK_RELOC32' and rr['width']==4 and rr['target_hunk']==0,'unnamed/masked command relocation')
      require(q==p+1 or code[p+1]==0,'untyped command alignment field');t=rr['addend_raw'];values=[symbol('c',t)];targets.append(t);lb[q]=dict(field(rr),symbol=values[0])
     else:
      require((2 if name=='NOTE' else 1+len(SPECS[name][1]))==sh['length'],'wrong grammar length');values=list(code[p:z]) if name=='NOTE' else list(code[p+1:z])
     local[p]=dict(offset=p,type=name,values=values)
     if name=='ENVELOPE':envelopes(code,rel,values[0]);ei.add(values[0])
     if 'NEXT' in sh['flows'] or 'CALL' in sh['flows']:targets.append(z)
     todo.extend(targets)
    for p in seen:
     path=set();q=p
     while True:
      require(q in seen and q not in path,'stream has no grammar terminal');path.add(q);sh=form(g,code[q],q)
      if set(sh['flows']).intersection(('STOP','RETURN','POINTER')):break
      q+=sh['length']
    target=symbol('h',entry)
   for p,c in local.items():require(p not in rows or rows[p]==c,'inconsistent command overlap')
   rows.update(local);bindings.update(lb);env_indexes.update(ei);bindings[site]=dict(field(r),symbol=target);rows[site]=dict(offset=site,type='SELECTOR',values=[target]);roots.append(dict(index=index,site=site,entry=entry,canonical=entry in oldheaders))
  except (FormatError,KeyError) as exc:blocked.append(dict(index=index,site=site,target_hunk=None if r is None else r['target_hunk'],entry=entry,reason=str(exc)))
 envroles=defaultdict(set);views=[]
 for i in sorted(env_indexes):
  v,roles,bs=envelopes(code,rel,i);views.extend(v)
  for p,rs in roles.items():envroles[p].update(rs)
  for b in bs:bindings[b['source_offset']]=b;rows[b['source_offset']]=dict(offset=b['source_offset'],type='ENVELOPE_PTR',values=[b['symbol']])
 for p,rs in envroles.items():rows[p]=dict(offset=p,type='ENVELOPE_FIELD',roles=sorted(rs),values=[code[p]])
 rows=sorted(rows.values(),key=lambda c:c['offset']);covered=set()
 for c in rows:
  points=set(range(c['offset'],c['offset']+length(c,g)));require(not points.intersection(covered),'overlapping typed field/command');covered.update(points)
 touched=[field(r) for r in model['relocations'] if r['source_hunk']==0 and any(p in covered for p in range(r['source_offset'],r['source_offset']+r['width']))]
 require(sorted(touched,key=lambda x:x['source_offset'])==[{k:v for k,v in b.items() if k!='symbol'} for _,b in sorted(bindings.items())],'unnamed/straddling relocation')
 gaps=[]
 for p in range(*INTERVAL):
  if p in covered:continue
  reason=('ENVELOPE_SLOT_NOT_REACHED_BY_PROVED_OPERAND' if p<0x5fac else 'ENVELOPE_BYTE_NOT_REACHED_BY_PROVED_PAIR' if p<0x615e else 'EXECUTABLE_CODE_SEPARATE_INSTRUCTION_ROUTE' if p<0x6200 else next(x['reason'] for x in blocked if x['index']==(p-0x6200)//4) if p<0x64c0 else 'NO_COMPLETE_SUPPORTED_ROOT_CLOSURE')
  if gaps and gaps[-1]['end']==p and gaps[-1]['reason']==reason:gaps[-1]['end']+=1
  else:gaps.append(dict(start=p,end=p+1,reason=reason))
 return dict(rows=rows,bindings=[v for _,v in sorted(bindings.items())],roots=roots,blocked_selectors=blocked,envelope_views=views,selector_extent_basis=[c for c in triggers if c['operands']['identifier']==highest],typed_bytes=len(covered),unproved_intervals=gaps)
def check(c):
 import re
 require(type(c['offset']) is int and isinstance(c['values'],list),'typed field shape');name=c['type'];v=c['values']
 if name in ('SELECTOR','ENVELOPE_PTR') or name in SPECS and SPECS[name][1]==('target',):require(len(v)==1 and type(v[0]) is str and re.fullmatch(r'_(audio3_[ceh]_[0-9A-F]{4}|audio_h_[0-9A-F]{4})',v[0]),'unnamed pointer operand')
 else:
  n=1 if name=='ENVELOPE_FIELD' else 2 if name in ('HEADER','NOTE') else len(SPECS[name][1]) if name in SPECS else -1
  require(len(v)==n,'unknown command or wrong typed field count')
  for x in v:integer(x)
  if name=='HEADER':integer(v[0],3)
  if name=='NOTE':integer(v[0],127)
  if name=='ENVELOPE_FIELD':
   require(set(c)=={'offset','type','values','roles'} and c['roles'] and set(c['roles'])<={'INITIAL','DELTA','TARGET','DELAY','ZERO'},'untyped envelope carrier')
   if 'ZERO' in c['roles']:require(v==[0],'envelope sentinel range')
   if set(c['roles']).intersection(('DELTA','DELAY')):require(v[0]!=0,'envelope nonzero typed range')
 if name!='ENVELOPE_FIELD':require(set(c)=={'offset','type','values'},'raw carrier/extra field')
def row_symbol(c):return symbol('h' if c['type']=='HEADER' else 'e' if c['type']=='ENVELOPE_FIELD' else 'c',c['offset'])
def plan(layout,g):
 fragments=[]
 for c in layout['rows']:
  if fragments and fragments[-1][-1]['offset']+length(fragments[-1][-1],g)==c['offset']:fragments[-1].append(c)
  else:fragments.append([c])
 # Fragment scheduling changes no field or command; parity is checked for each
 # command. No fillers bridge omitted or blocked fields.
 objects=[];remaining=fragments[:]
 while remaining:
  rows=[];cursor=0
  while True:
   found=next((i for i,fs in enumerate(remaining) if fs[0]['offset']%2==cursor%2),None)
   if found is None:break
   fs=remaining.pop(found);rows+=fs;cursor+=sum(length(c,g) for c in fs)
  require(rows,'odd-root fragment needs typed parity prefix; fillers forbidden')
  prefix='audio3_%02d'%len(objects);parts=[];q=0
  for c in rows:
   n=length(c,g)
   if parts and parts[-1]['original_end']==c['offset']:parts[-1]['original_end']+=n;parts[-1]['candidate_end']+=n
   else:parts.append(dict(original_start=c['offset'],original_end=c['offset']+n,candidate_start=q,candidate_end=q+n))
   q+=n
  objects.append(dict(id='resident_'+prefix,prefix=prefix,typed_bytes=cursor,CODE=cursor+cursor%2,parts=parts,rows=rows,source='src/recovered/code-data/'+prefix+'.asm',candidate='evidence/rules/audio-region-0003/'+prefix+'.asm'))
 return objects
def encode(member,g):
 out=bytearray();definitions=[];fixups=[]
 for c in member['rows']:
  check(c);p=len(out);name=c['type'];v=c['values'];definitions.append(dict(name=row_symbol(c),offset=p))
  if name in ('SELECTOR','ENVELOPE_PTR'):fixups.append(dict(offset=p,symbol=v[0],type='HUNK_RELOC32',width=4,addend=0));out+=bytes(4)
  elif name in ('HEADER','NOTE','ENVELOPE_FIELD'):out+=bytes(v)
  else:
   op,fields=SPECS[name];out.append(op)
   if fields==('target',):
    if len(out)%2:out.append(0)
    fixups.append(dict(offset=len(out),symbol=v[0],type='HUNK_RELOC32',width=4,addend=0));out+=bytes(4)
   else:out+=bytes(v)
  require(len(out)-p==length(c,g) and p%2==c['offset']%2,'changed pointer grammar parity/length')
 return dict(code=bytes(out),definitions=definitions,fixups=fixups)
def source(member,g,targets):
 sem=encode(member,g);used={f['symbol'] for f in sem['fixups']};local={d['name'] for d in sem['definitions']};names=['_'+member['prefix']+'_begin','_'+member['prefix']+'_end']+sorted(local&targets)+sorted(used-local)
 lines=['; Typed CODE-resident audio data; historical ownership/TU UNKNOWN.']
 macros={'HEADER':['dc.b \\1,\\2'],'NOTE':['dc.b \\1,\\2'],'SELECTOR':['dc.l \\1'],'ENVELOPE_PTR':['dc.l \\1'],'ENV_INITIAL':['dc.b \\1'],'ENV_DELTA':['dc.b \\1'],'ENV_TARGET':['dc.b \\1'],'ENV_DELAY':['dc.b \\1'],'ENV_ZERO':['dc.b 0']}
 for name,(op,fields) in SPECS.items():macros[name]=['dc.b $%02x'%op,'ds 0','dc.l \\1'] if fields==('target',) else ['dc.b '+','.join(['$%02x'%op]+['\\%d'%(i+1) for i in range(len(fields))])]
 for name,body in macros.items():lines+=['T3_'+name+' macro']+['\t'+s for s in body]+['\tendm']
 lines+=['\tcseg']+['\tpublic '+n for n in names]+[names[0]+':']
 for c in member['rows']:
  sym=row_symbol(c)
  if sym in targets:lines.append(sym+':')
  name=c['type'];args=c['values']
  if name=='ENVELOPE_FIELD':
   role=next(x for x in ('ZERO','DELTA','DELAY','INITIAL','TARGET') if x in c['roles']);name='ENV_'+role;args=[] if role=='ZERO' else [args[0]-256 if role=='DELTA' and args[0]>=128 else args[0]]
  lines.append('\tT3_'+name+(' '+','.join(map(str,args)) if args else ''))
 return ('\n'.join(lines+[names[1]+':','\tend',''])).encode('ascii')
