"""Measured pinned-C register preservation, rederived from proofs and controls."""
from names import read_source
import re
from common import require,sha256,json_bytes
from repo_paths import canonical_path
from audio_sequence_data import payload
from functools import lru_cache
from analysis_support import decoder
from audio_driver_objects import parse
from hunk import parse as hunk_parse
from overlay_experiment import symbols as symbol_map
import json

REGISTERS=['d%d'%n for n in range(8)]+['a%d'%n for n in range(5)]
BINDER=b'\tpublic .begin\n.begin\n\trts\n\tpublic _C_sink\n_C_sink\n\trts\n\tend\n'

def source(n):
 return ('extern long C_sink();\nlong C_reg%d(p)\nlong *p;\n{\n    register long '%n+
  ', '.join('r'+str(i) for i in range(n))+';\n'+
  ''.join('    r%d = p[%d] + %d;\n'%(i,i,i+1) for i in range(n))+
  '    C_sink();\n    return '+' + '.join('r'+str(i) for i in range(n))+';\n}\n').encode('ascii')

def registers(text):
 if not re.fullmatch(r'[ad][0-7](?:-[ad][0-7])?(?:/[ad][0-7](?:-[ad][0-7])?)*',text):return set()
 result=set()
 for piece in text.split('/'):
  if '-' in piece:
   a,z=piece.split('-');require(a[0]==z[0] and a[1:].isdigit() and z[1:].isdigit(),'register range')
   result.update(a[0]+str(n) for n in range(int(a[1:]),int(z[1:])+1))
  elif re.fullmatch('[ad][0-7]',piece):result.add(piece)
 return result

# One decoder per process: Capstone construction costs an import lookup,
# and this is called for every instruction window during canonical replay.
_decoder=lru_cache(maxsize=None)(decoder)

@lru_cache(maxsize=None)
def _decoded(raw,start):
 return tuple((i.address,i.size,i.mnemonic,i.op_str) for i in _decoder().disasm(raw,start))

def instructions(raw,start=0):
 items=_decoded(bytes(raw),start)
 require(sum(i[1] for i in items)==len(raw) and not any(i[2].startswith('dc.') for i in items),'calibration instruction boundaries')
 return [dict(offset=a,size=n,mnemonic=m,operands=o) for a,n,m,o in items]

def save(i):
 m=i['mnemonic'];o=i['operands']
 if o.endswith(', -(a7)') and (m=='movem.l' or m=='move.l'):
  return registers(o.split(',')[0])
 return set()

def restore(i):
 m=i['mnemonic'];o=i['operands']
 if o.startswith('(a7)+, ') and m in ['movem.l','move.l','movea.l']:return registers(o.split(', ')[1])
 return set()

def written(i):
 m=i['mnemonic'].split('.')[0];o=i['operands']
 # A pop is a write. It restores an entry value only when paired with an
 # actual prologue save; Aztec also pops discarded arguments into scratch D2.
 if restore(i):return restore(i)
 if m=='movem':return registers(o.split(', ')[-1])
 if m=='dbra':return registers(o.split(', ')[0])
 if m=='exg':return set(re.findall(r'\b[ad][0-7]\b',o))
 if m in ['move','movea','moveq','lea','clr','add','adda','addq','sub','suba','subq','and','andi','or','ori','eor','eori','lsl','lsr','asl','asr','rol','ror','ext','swap','neg','not','mulu','muls','divu','divs','scc','seq','sne','slt','sgt']:
  dest=o.split(', ')[-1]
  return {dest} if dest in REGISTERS else set()
 return set()

def observation(items):
 saved=set()
 for i in items:
  if i['mnemonic'].split('.')[0]=='link':continue
  bank=save(i)
  if bank:saved|=bank;continue
  break
 returns=[n for n,i in enumerate(items) if i['mnemonic']=='rts']
 paired=set(saved)
 for n in returns:
  restored=set().union(*(restore(i) for i in items[max(0,n-3):n]))
  paired &= restored
 if not returns:paired=set()
 writes=set().union(*(written(i) for i in items))
 return dict(writes=sorted(writes),saved=sorted(saved),paired=sorted(paired),
  unsaved=sorted(writes-paired),preserved=sorted(writes&paired))

def classification(observations):
 saved=sorted(r for r,v in observations.items() if v['preserved'] and not v['unsaved'])
 scratch=sorted(r for r,v in observations.items() if v['unsaved'])
 unknown=sorted(set(REGISTERS)-set(saved)-set(scratch))
 return saved,scratch,unknown

def require_preserved(calibration,register):
 require(calibration is not None,'register preservation requires a rederived calibration')
 classified=classification(calibration['observations'])
 require(classified==(calibration['callee_saved'],calibration['scratch'],calibration['unmeasured']),'stale register-preservation calibration')
 require(register in classified[0],'register preservation premise is not measured: '+register)
 return True

def compiled_control(root,job,n):
 work=root/job/'sys/work';name='reg%d'%n
 require((work/(name+'.c')).read_bytes()==source(n),'register control source')
 require((work/'bind_regs.asm').read_bytes()==BINDER,'register control binder')
 # The diagnostic-only default-model binder has the separate C000 AJ form:
 # one four-byte literal record, zero terminator/alignment, two CODE definitions.
 # It supplies no accepted source bytes and cannot relax the driver AJ grammar.
 binder=(work/'bind_regs.o').read_bytes()
 header=(b'AJ'+bytes(8)+(4).to_bytes(4,'big')+bytes(8)+(2).to_bytes(2,'big')+
  (9).to_bytes(4,'big')+(11).to_bytes(2,'big')+(17).to_bytes(2,'big')*2+b'\xc0\0')
 names=b'\x02\x08\0\0.begin\0'+b'\x02\x08\0\x02_C_sink\0'+bytes(1)
 require(binder==header+b'\x13'+b'\x4e\x75'*2+bytes(3)+names,'complete diagnostic register binder AJ')
 obj=(work/(name+'.o')).read_bytes();code,refs,structure=parse(obj,False)
 require([s['name'] for s in structure['symbols']]==['_C_reg%d'%n,'_C_sink','.begin'],'complete register control symbols')
 require(len(refs)==1 and refs[0]['type']=='PC_RELATIVE_CODE16' and refs[0]['symbol']=='_C_sink','named register control call')
 image=(work/(name+'.exe')).read_bytes();model=hunk_parse(image);sm=symbol_map((work/(name+'.sym')).read_text())
 rounded=(len(code)+7)//4*4
 require([(h['type'],h['initialized_size'],h['allocated_size']) for h in model['hunks']]==[('CODE',rounded,rounded),('DATA',0,0),('BSS',0,4)],'complete register control link topology')
 require(sm=={(0,'__H0_org'):0,(0,'_C_reg%d'%n):0,(0,'.begin'):len(code),(0,'_C_sink'):len(code)+2,(0,'__H0_end'):rounded,(1,'__H1_org'):0,(1,'__H1_end'):0,(2,'__H2_org'):0,(2,'__H2_end'):0},'complete register control named map')
 linked=payload(image,model,0);p=refs[0]['offset'];copy=bytearray(linked[:len(code)])
 require(p+int.from_bytes(copy[p:p+2],'big',signed=True)==len(code)+2 and not model['relocations'],'named PC16 control binding')
 copy[p:p+2]=bytes(2)
 require(bytes(copy)==code and linked[len(code):len(code)+4]==b'\x4e\x75'*2 and linked[len(code)+4:]==bytes(rounded-len(code)-4),'whole register control object/link')
 items=instructions(code);record=observation(items)
 expected=['d4','d5','d6','d7']+(['a2','a3'] if n==6 else [])
 require(set(record['preserved'])==set(expected),'pinned register control preservation changed')
 require(items[0]['mnemonic']=='link.w' and any(i['operands']=='$8(a5), a0' for i in items),'ordinary C stack argument control')
 call=p-2;require(any(i['offset']==call and i['mnemonic']=='jsr' for i in items),'ordinary external C call instruction')
 definitions=[i['offset'] for i in items if i['offset']<call and 'd7' in written(i) and not restore(i)]
 uses=[i['offset'] for i in items if i['offset']>call and i['mnemonic']=='add.l' and i['operands']=='d7, d0']
 require(definitions and uses,'control does not keep a D7 local live across its C call')
 first_use=min(uses);last_definition=max(definitions)
 require(not any(last_definition<i['offset']<call and 'd7' in save(i) for i in items),'D7 local saved around C call')
 require(not any(call<i['offset']<first_use and 'd7' in written(i) for i in items),'D7 local reloaded after C call')
 return dict(id=name,**record,d7_live_across_named_c_call=dict(definition=last_definition,call=call,use=first_use,symbol='_C_sink',save_around_call=False,reload_after_call=False),object_sha256=sha256(obj),linked_sha256=sha256(image),source_sha256=sha256(source(n)),CODE=len(code),DATA=0)

def derive(root,blob,model,batch):
 ledger=json.loads(canonical_path(root,'recovery/ledger.json').read_bytes())
 analysis=json.loads(canonical_path(root,'evidence/functions/ledger.json').read_bytes());by={f['id']:f for f in analysis['functions']}
 records=[];anchors={}
 for ident,item in sorted(ledger['functions'].items()):
  raw=canonical_path(root,item['proof']).read_bytes();proof=json.loads(raw)
  require(sha256(raw)==item['proof_sha256'] and sha256(read_source(root, item['source']))==item['source_sha256'],'calibration canonical C source/proof binding')
  if proof['compiler'].get('compiler_version')!='3.6a':continue
  f=by[ident];extent=item['evidence_extent'];body=payload(blob,model,f['hunk'])[f['start']:f['end']]
  comparison=proof['comparison'].get('code_comparison',proof['comparison'])
  require(proof['id']==ident and comparison['verdict']=='EQUAL' and comparison['relocation_equal'] and comparison['normalized_sha256']==f['sha256']==sha256(body),'calibration exact C body proof')
  # The canonical CFG separates inline jump-table DATA from instructions.
  # Rederive each instruction from the hash-bound oracle, never decode table
  # entries as instructions or count their apparent register operands.
  items=[];covered=set()
  for expected in f['instructions']:
   off=expected['offset']-f['start'];size=expected['size']
   require(0<=off and off+size<=len(body),'canonical instruction outside exact body')
   decoded=instructions(body[off:off+size],expected['offset'])
   require(len(decoded)==1 and all(decoded[0][k]==expected[k] for k in ['offset','size','mnemonic','operands']),'canonical calibration instruction changed')
   items+=decoded;covered.update(range(off,off+size))
  data=set()
  for table in f['jump_tables']:
   data.update(range(table['table_start']-f['start'],table['table_end']-f['start']))
  require(set(range(len(body)))<=covered|data,'untyped canonical calibration gap: '+ident)
  record=observation(items)
  records.append(dict(id=ident,proof_sha256=item['proof_sha256'],body_sha256=sha256(body),**record))
  for target,site,mnemonic,operands in [('resident_F_31AA',0x32d0,'move.w','-$4(a5), d2'),('ov08_F_1F4C',0x2c60,'moveq','#$14, d2')]:
   if ident==target:
    instruction=next((i for i in items if i['offset']==site),None)
    require(instruction and (instruction['mnemonic'],instruction['operands'])==(mnemonic,operands) and 'd2' in record['unsaved'],'D2 scratch counterexample changed')
    anchors[ident]=dict(site=site,instruction=instruction,proof_sha256=item['proof_sha256'],unsaved_d2=True)
 require(len(anchors)==2,'both canonical D2 counterexamples required')
 # Complete C objects have a separate ownership map. Include their proved
 # unreachable instruction regions too; exclude mixed C/ASM modules from this
 # ordinary-C ABI calibration rather than letting inline ASM define the ABI.
 import dead_code_extents as dead
 for ident,item in sorted(ledger.get('dead_code_functions',{}).items()):
  raw=canonical_path(root,item['proof']).read_bytes();proof=json.loads(raw)
  require(sha256(raw)==item['proof_sha256'] and sha256(read_source(root, item['source']))==item['source_sha256'],'complete C calibration source/proof')
  producer_raw=canonical_path(root,proof['compiler']['path']).read_bytes();receipt_raw=canonical_path(root,proof['exact_receipt']['path']).read_bytes()
  require(sha256(producer_raw)==proof['compiler']['sha256'] and sha256(receipt_raw)==proof['exact_receipt']['sha256'],'complete C calibration retained pins')
  producer=json.loads(producer_raw);receipt=json.loads(receipt_raw)
  require(producer['status']=='COMPILED' and receipt['verdict']=='EQUAL' and receipt['unclaimed_bytes']==0,'complete C exact calibration proof')
  if producer['identity'].get('compiler_version')!='3.6a':continue
  f=dead.make_view(by[ident],analysis,blob,model,root);body=payload(blob,model,f['hunk'])[f['start']:f['end']]
  require(proof['complete_extent']=={k:f[k] for k in ['hunk','start','end','size','sha256']} and sha256(body)==f['sha256'],'complete C oracle extent changed')
  items=[]
  for expected in f['instructions']:
   off=expected['offset']-f['start'];decoded=instructions(body[off:off+expected['size']],expected['offset'])
   require(len(decoded)==1 and all(decoded[0][k]==expected[k] for k in ['offset','size','mnemonic','operands']),'complete C instruction changed')
   items+=decoded
  records.append(dict(id=ident,proof_sha256=item['proof_sha256'],body_sha256=sha256(body),**observation(items)))
 controls=[compiled_control(root,batch['job'],n) for n in [4,6]]
 counts={r:dict(preserved=0,unsaved=0) for r in REGISTERS}
 for record in records:
  for field in ['preserved','unsaved']:
   for r in record[field]:
    if r in counts:counts[r][field]+=1
 canonical_counts={r:dict(v) for r,v in counts.items()}
 for record in controls:
  for field in ['preserved','unsaved']:
   for r in record[field]:
    if r in counts:counts[r][field]+=1
 saved,scratch,unmeasured=classification(counts)
 result=dict(canonical_observations=canonical_counts,observations=counts,callee_saved=saved,scratch=scratch,unmeasured=unmeasured,
  canonical_functions=len(records),corpus_digest=sha256(json_bytes(records)),
  d2_counterexamples=anchors,controls=controls,
  method='HASH_BOUND_CANONICAL_36A_C_INSTRUCTIONS_AND_PINNED_4_6_REGISTER_CONTROLS')
 require('d2' in scratch and 'd2' not in saved,'D2 is measured scratch, never a nonvolatile witness')
 require_preserved(result,'d7')
 from audio_driver_contracts import control_rejections
 for n,record in zip([4,6],controls):
  raw=(root/batch['job']/('sys/work/reg%d.o'%n)).read_bytes();code,_,_=parse(raw,False)
  checks=control_rejections(instructions(code),result)
  require(not any(checks.values()),'ordinary register-variable C control satisfies a non-C predicate')
  record['predicate_rejections']=checks
 return result
