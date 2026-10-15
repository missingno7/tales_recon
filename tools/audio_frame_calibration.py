"""Fail-closed frame calibration from hash-bound C proofs and fresh pinned controls.

This is a measured compiler property, not a general statement about C or 68000.
New accepted 3.6a options require a new compiled control before admission.
"""
import json,re
from common import require,sha256,json_bytes
from repo_paths import canonical_path
from audio_sequence_data import payload
import audio_register_calibration as registers
from audio_driver_objects import parse
from hunk import parse as hunk_parse
from overlay_experiment import symbols as symbol_map

FLAGS=[[],['+D'],['+X3'],['+x3'],['+x3,5'],['+L']]
SOURCE=b"""extern long C_sink();
void C_empty() {}
int C_leaf() { return 7; }
void C_void(p)
int *p;
{ *p = 1; }
long C_regs(p)
long *p;
{
 register long r0,r1,r2,r3,r4,r5;
 r0=p[0]+1; r1=p[1]+2; r2=p[2]+3;
 r3=p[3]+4; r4=p[4]+5; r5=p[5]+6;
 C_sink();
 return r0+r1+r2+r3+r4+r5;
}
"""
FUNCTIONS=['_C_empty','_C_leaf','_C_void','_C_regs']

def framed(items):
 return bool(items and items[0]['mnemonic']=='link.w' and items[0]['operands'].startswith('a5, '))

def require_framed(records):
 require(records and all(r['link_a5'] is True for r in records),'FRAMELESS_ENTRY calibration refuted by canonical C or compiled control')

def corpus(root,blob,model):
 ledger=json.loads(canonical_path(root,'recovery/ledger.json').read_bytes())
 analysis=json.loads(canonical_path(root,'evidence/functions/ledger.json').read_bytes())
 by={f['id']:f for f in analysis['functions']};out=[]
 for section in ['functions','dead_code_functions','behavioral_functions']:
  for ident,item in sorted(ledger.get(section,{}).items()):
   raw=canonical_path(root,item['proof']).read_bytes();proof=json.loads(raw)
   require(sha256(raw)==item['proof_sha256'] and sha256(canonical_path(root,item['source']).read_bytes())==item['source_sha256'],'frame corpus source/proof pins')
   if section=='functions':
    o=item['evidence_extent'];cmp=proof['comparison'].get('code_comparison',proof['comparison'])
    require(proof['id']==ident and cmp['verdict']=='EQUAL' and cmp['relocation_equal'] and cmp['normalized_sha256']==o['sha256'],'frame corpus exact C proof')
   elif section=='dead_code_functions':
    o=proof['complete_extent'];rec=proof['exact_receipt'];rr=canonical_path(root,rec['path']).read_bytes()
    require(sha256(rr)==rec['sha256'] and json.loads(rr)['verdict']=='EQUAL','frame complete C receipt')
    producer=proof['compiler'];pr=canonical_path(root,producer['path']).read_bytes()
    require(sha256(pr)==producer['sha256'] and json.loads(pr)['status']=='COMPILED','frame complete C producer')
   else:
    # Behavioral C remains a separate category. Only its independently
    # bound entry instruction contributes to this compiler-frame measurement.
    import behavioral
    behavioral.validate(root,by[ident],item,analysis)
    o=item['evidence_extent']
   body=payload(blob,model,o['hunk'])[o['start']:o['end']]
   require(len(body)==o['size'] and sha256(body)==o['sha256'] and len(body)>=4,'frame corpus oracle body')
   first=registers.instructions(body[:4],o['start'])
   require(len(first)==1,'frame corpus first instruction must be LINK a5')
   out.append(dict(id=ident,section=section,proof_sha256=item['proof_sha256'],body_sha256=sha256(body),entry=o['start'],hunk=o['hunk'],first=first[0],link_a5=framed(first)))
 require_framed(out)
 return out

def compiled(root,job,k):
 name='frame%d'%k;work=root/job/'sys/work';raw=(work/(name+'.o')).read_bytes()
 require((work/(name+'.c')).read_bytes()==SOURCE,'frame control source recipe')
 require((work/'bind_regs.asm').read_bytes()==registers.BINDER,'frame control binder source')
 code,refs,structure=parse(raw,False,0x80 if FLAGS[k]==['+D'] else 0xc0)
 syms=structure['symbols']
 require([x['name'] for x in syms]==FUNCTIONS+['_C_sink','.begin'],'complete frame control symbols')
 require(all(x['kind']==2 and x['attribute']==8 for x in syms[:4]) and all(x['kind']==7 and x['attribute']==8 for x in syms[4:]),'frame control symbol attributes')
 require(len(refs)==1 and refs[0]['width']==2 and refs[0]['type']=='PC_RELATIVE_CODE16' and refs[0]['symbol']=='_C_sink' and refs[0]['addend']==0,'frame control named call')
 image=(work/(name+'.exe')).read_bytes();model=hunk_parse(image);sm=symbol_map((work/(name+'.sym')).read_text());rounded=(len(code)+7)//4*4
 require([(h['type'],h['initialized_size'],h['allocated_size']) for h in model['hunks']]==[('CODE',rounded,rounded),('DATA',0,0),('BSS',0,4)],'frame control full link topology')
 expected={(0,'__H0_org'):0,(0,'__H0_end'):rounded,(0,'.begin'):len(code),(0,'_C_sink'):len(code)+2,(1,'__H1_org'):0,(1,'__H1_end'):0,(2,'__H2_org'):0,(2,'__H2_end'):0}
 expected.update({(0,x['name']):x['offset'] for x in syms[:4]})
 require(sm==expected and not model['relocations'],'frame control complete map/relocations')
 actual=payload(image,model,0);p=refs[0]['offset'];copy=bytearray(actual[:len(code)])
 require(p+int.from_bytes(copy[p:p+2],'big',signed=True)==sm[(0,'_C_sink')],'frame control named PC16 binding');copy[p:p+2]=bytes(2)
 require(bytes(copy)==code and actual[len(code):len(code)+4]==b'\x4e\x75'*2 and actual[len(code)+4:]==bytes(rounded-len(code)-4),'frame control whole CODE and alignment')
 rows=[]
 for n,s in enumerate(syms[:4]):
  lo=s['offset'];hi=syms[n+1]['offset'] if n<3 else len(code);ins=registers.instructions(code[lo:hi],lo)
  returns=[j for j,i in enumerate(ins) if i['mnemonic']=='rts']
  rows.append(dict(id=name+':'+s['name'],entry=lo,end=hi,link_a5=framed(ins),return_sites=[ins[j]['offset'] for j in returns]))
  require(returns and all(j and ins[j-1]['mnemonic']=='unlk' and ins[j-1]['operands']=='a5' for j in returns),'frame control LINK/UNLK/RTS pair')
 require_framed(rows)
 return dict(id=name,flags=FLAGS[k],source_sha256=sha256(SOURCE),object_sha256=sha256(raw),linked_sha256=sha256(image),structure=structure,functions=rows)

def derive(root,blob,model,batch):
 from compiler_oracle import PROFILES
 accepted={tuple(p['flags']) for p in PROFILES.values() if p['version']=='3.6a'}
 require(accepted<=set(map(tuple,FLAGS)),'new accepted compiler options lack frame controls')
 records=corpus(root,blob,model);controls=[compiled(root,batch['job'],k) for k in range(len(FLAGS))]
 # Supplemental pinned 5.0a controls are observations, not premises.
 optional=[]
 work=root/batch['job']/'sys/work'
 for name,flags in [('frame50',[]),('frame50s',['-ps'])]:
  asm=(work/(name+'.asm')).read_bytes();obj=(work/(name+'.o')).read_bytes()
  require((work/(name+'.c')).read_bytes()==SOURCE,'supplemental C control source')
  text=asm.decode('ascii');entry=[]
  for f in FUNCTIONS:
   tail=text.split(f+':',1)[1];line=next(x.strip() for x in tail.splitlines() if x.strip() and not x.lstrip().startswith(';'))
   entry.append(dict(name=f,first=line,link=bool(re.match(r'^link(?:\.w)?\s+a[56],',line))))
  optional.append(dict(compiler='5.0a',flags=flags,source_sha256=sha256(SOURCE),assembly_sha256=sha256(asm),object_sha256=sha256(obj),entries=entry,required=False))
 require(all(e['link'] for row in optional for e in row['entries']),'supplemental compiler produced a frameless C entry')
 extras=supplemental(root)
 require(all(e['link'] for row in extras for e in row.get('entries',[])),'supplemental compiler produced a frameless C entry')
 return dict(method='HASH_BOUND_CANONICAL_C_ENTRY_AND_PINNED_OPTION_MATRIX',canonical_functions=len(records),canonical_categories={s:sum(r['section']==s for r in records) for s in ['functions','dead_code_functions','behavioral_functions']},corpus_sha256=sha256(json_bytes(records)),accepted_36a_flags=sorted(map(list,accepted)),controls=controls,supplemental=optional+extras,all_required_entries_link_a5=True)

def cfg(items):
 """Own-function flow: calls may return; no opaque computed transfer."""
 from audio_driver_contracts import target
 edges=[]
 for i in items:
  p=i['offset'];q=p+i['size'];m=i['mnemonic'].split('.')[0];t=target(i)
  if m in ['rts','rte']:
   edges.append(dict(site=p,kind='RETURN_TO_EXISTING_CALLER',target=None));continue
  if m in ['jsr','bsr']:
   require(t is not None,'frameless computed call lacks a named contract')
   edges.extend([dict(site=p,kind='CALL',target=t,operands=i['operands']),dict(site=p,kind='CALL_RETURN',target=q)]);continue
  if m=='bra':edges.append(dict(site=p,kind='TAIL',target=t));continue
  if m.startswith('b') and m not in ['btst','bset','bclr'] or m.startswith('db'):
   require(t is not None,'unproved frameless conditional edge')
   edges.extend([dict(site=p,kind='BRANCH',target=t),dict(site=p,kind='FALLTHROUGH',target=q)]);continue
  require(m not in ['jmp','rtr','stop','reset','trap','trapv','illegal'],'unproved frameless terminal transfer')
  edges.append(dict(site=p,kind='FALLTHROUGH',target=q))
 return edges

def witness(items,entry,edges=None):
 by={i['offset']:i for i in items}
 require(len(by)==len(items) and entry in by,'independently proved entry outside instruction graph')
 require(by[entry]['mnemonic'].split('.')[0]!='link','LINK-framed C rejection control')
 derived=cfg(items)
 if edges is not None:require(edges==derived,'frameless CFG edges do not rederive')
 seen=set();pending=[entry];returns=[]
 while pending:
  p=pending.pop()
  if p in seen:continue
  require(p in by,'frameless path crosses an unproved CFG boundary');seen.add(p);i=by[p]
  require(i['mnemonic'].split('.')[0] not in ['link','unlk'],'frameless CFG gained frame')
  if i['mnemonic'] in ['rts','rte']:returns.append(p);continue
  successors=[e['target'] for e in derived if e['site']==p and e['kind']!='CALL']
  require(successors and all(q is not None for q in successors),'unproved frameless CFG edge')
  pending.extend(successors)
 require(returns,'frameless CFG has no RTS/RTE')
 require(seen==set(by),'frameless extent includes instructions without entry reachability')
 return dict(kind='FRAMELESS_ENTRY',entry=entry,return_sites=sorted(returns),reachable_instructions=sorted(seen),stack_frame=False,calibration='PINNED_36A_ALL_ACCEPTED_OPTIONS_AND_CANONICAL_C',c_compatible=False)

SUPPLEMENTAL='evidence/reconstructed-asm/frame-supplemental-0004.json'
def supplemental(root):
 from repo_paths import candidate_path
 fact=json.loads(canonical_path(root,SUPPLEMENTAL).read_bytes())
 require(set(fact)=={'schema_version','amiga320_job','rom36b_job','pins','rom_status','required'} and fact['schema_version']==1 and fact['required'] is False,'supplemental frame observations schema')
 missing=[]
 for n,digest in fact['pins'].items():
  p=candidate_path(root,root/n)
  require(n.startswith('build/worker-jobs/'),'supplemental frame producer path')
  if not p.is_file():missing.append(n)
  else:require(sha256(p.read_bytes())==digest,'supplemental frame producer pin')
 if missing:return [dict(compiler='3.20a / 3.6b ROM',status='UNAVAILABLE_RETAINED_ARTIFACTS',missing=missing,required=False)]
 job=root/fact['amiga320_job'];req=json.loads((job/'request.json').read_bytes());rec=json.loads((job/'result.json').read_bytes())
 require(rec['request']==req and rec['all_steps_succeeded'] is True and all(s['returncode']==0 for s in rec['steps']),'supplemental 3.20a successful producer')
 require(req['experimental_toolchain']['inventory_sha256']==sha256(canonical_path(root,'evidence/toolchain/aztec-3.20a.json').read_bytes()),'supplemental 3.20a inventory pin')
 for pin in req['pinned_inputs']:
  require(sha256(canonical_path(root,pin['path']).read_bytes())==pin['sha256'],'supplemental 3.20a pinned compiler inputs')
 require((job/'sys/work/frame.c').read_bytes()==SOURCE,'supplemental 3.20a source')
 asm=(job/'sys/work/frame.asm').read_bytes();entries=[]
 for f in FUNCTIONS:
  tail=asm.decode('ascii').split(f+':',1)[1]
  first=next(x.strip() for x in tail.splitlines() if x.strip() and not x.lstrip().startswith(';'))
  entries.append(dict(name=f,first=first,link=bool(re.match(r'^link(?:\.w)?\s+a[56],',first))))
 rom=root/fact['rom36b_job'];rr=json.loads((rom/'dosbox-request.json').read_bytes())
 require(sha256(canonical_path(root,rr['compiler']).read_bytes())==rr['compiler_sha256'] and sha256(__import__('pathlib').Path(rr['runner']).read_bytes())==rr['runner_sha256'],'supplemental ROM compiler/runner pins')
 require((rom/'sys/work/frame.c').read_bytes()==SOURCE and sha256((rom/'dosbox.conf').read_bytes())==rr['config_sha256'],'supplemental ROM source/config')
 require(fact['rom_status']=='COMPILED_FRAMED_LINK_A6' and (rom/'sys/work/ROMDONE.TXT').read_bytes().strip()==b'done','supplemental ROM completed compilation')
 rom_asm=(rom/'sys/work/FRAME.A').read_bytes();rom_entries=[]
 for f in FUNCTIONS:
  tail=rom_asm.decode('ascii').split(f+':',1)[1]
  first=next(x.strip() for x in tail.splitlines() if x.strip() and not x.lstrip().startswith(';'))
  rom_entries.append(dict(name=f,first=first,link=bool(re.match(r'^link(?:\.w)?\s+a[56],',first))))
 return [dict(compiler='3.20a',flags=[],entries=entries,assembly_sha256=sha256(asm),producer=fact['amiga320_job'],required=False),dict(compiler='3.6b ROM',status=fact['rom_status'],producer=fact['rom36b_job'],entries=rom_entries,assembly_sha256=sha256(rom_asm),required=False)]
