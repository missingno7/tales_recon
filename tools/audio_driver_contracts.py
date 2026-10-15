"""Oracle-derived audio register-stream contracts; no source or CODE generation."""
import re
from common import require,sha256
from audio_sequence_data import payload,field
from analysis_support import decoder

COMMAND_TABLE=(0x292e,0x29de)
SPANS=[(0x544c,0x558a,'envelope'),(0x5796,0x57c0,'world'),(0x57e4,0x5868,'start'),(0x58bc,0x59a4,'update'),(0x5a50,0x5cc2,'dispatch'),(0x5cc6,0x5d74,'handlers_b'),(0x5d78,0x5d80,'handlers_c'),(0x5d92,0x5e6c,'handlers_d')]

def decode(raw,start=0):
 ins=list(decoder().disasm(raw,start));require(ins and sum(i.size for i in ins)==len(raw),'complete instruction boundaries')
 require(all(not i.mnemonic.startswith('dc.') for i in ins),'undecoded CODE')
 return [dict(offset=i.address,size=i.size,mnemonic=i.mnemonic,operands=i.op_str) for i in ins]

def at(by,address,mnemonic,operands):
 i=by.get(address);require(i and (i['mnemonic'],i['operands'])==(mnemonic,operands),'instruction contract at %04X'%address);return i

def table(blob,model,ins):
 lo,hi=COMMAND_TABLE;rs=[r for r in model['relocations'] if r['source_hunk']==1 and lo<=r['source_offset']<hi]
 require(len(rs)==44 and [r['source_offset'] for r in rs]==list(range(lo,hi,4)),'exact44 handler slots; no45th')
 data=payload(blob,model,1);result=[]
 for n,r in enumerate(rs):
  require(r['type']=='HUNK_RELOC32' and r['width']==4 and r['target_hunk']==0 and r['addend_raw'] in ins,'named CODE handler boundary')
  require(int.from_bytes(data[r['source_offset']:r['source_offset']+4],'big')==r['addend_raw'],'handler pointer payload')
  result.append(dict(slot=n,opcode=0x80+n,**field(r),symbol='_resident_asm_%04X'%r['addend_raw']))
 require(not any(r['source_hunk']==1 and r['source_offset']==hi for r in model['relocations']),'slot44 is not a CODE relocation')
 return result

def signature(items):
 """The entry explicitly receives A0/D7 and loads the persistent A1 cursor.

 A normal C function-pointer dispatcher can contain indirect jumps; that alone
 is never eligible. Require this ordered unstacked byte-stream dispatch chain.
 """
 require(items and (items[0]['mnemonic'],items[0]['operands'])==('movea.l','$4(a0), a1'),'unstacked stream entry absent (C-compatible control)')
 require(not any(i['mnemonic'].split('.')[0] in ['link','unlk'] for i in items),'C frame is not an ASM predicate')
 pattern=[('tst.b','(a1)'),('bpl.b',None),('move.b','(a1)+, d0'),('and.w','#$7f, d0'),('cmp.b','#$2c, d0'),('ble.b',None),('bra.w',None),('lsl.w','#$2, d0'),('lea.l','$292e.l, a2'),('movea.l','(a2, d0.w), a2'),('clr.w','d0'),('move.b','(a1)+, d0'),('jmp','(a2)')]
 require(len(items)>=14,'short stream dispatch')
 for i,(m,o) in zip(items[1:14],pattern):require(i['mnemonic']==m and (o is None or i['operands']==o),'byte prefetch/register dispatch differs')
 return dict(entry=items[0]['offset'],jump=items[13]['offset'],parameter_prefetch=items[12]['offset'],stream='A1 postincrement',parameter='D0 low byte, zero word',channel='A0/D7',new_return_address_on_dispatch=False)

def target(i):
 if i['mnemonic'].startswith('dbra'):m=re.search(r', \$([0-9a-f]+)$',i['operands'])
 else:m=re.fullmatch(r'\$([0-9a-f]+)(?:\(pc\))?',i['operands'])
 return int(m.group(1),16) if m else None

def edges(items,commands):
 result=[]
 for i in items:
  m=i['mnemonic'].split('.')[0];p=i['offset'];q=p+i['size'];t=target(i)
  if m=='rts':result.append(dict(site=p,kind='RETURN_TO_EXISTING_CALLER',target=None));continue
  if m in ['bsr','jsr']:
   result.append(dict(site=p,kind='CALL' if t is not None else 'INDIRECT_CALLBACK',target=t,operands=i['operands']));result.append(dict(site=p,kind='CALL_RETURN',target=q));continue
  if m=='jmp':
   require(p==0x5a9a and i['operands']=='(a2)','unproved computed transfer')
   result.extend(dict(site=p,kind='HANDLER_JUMP_NO_NEW_FRAME',target=c['addend_raw'],slot=c['slot'],opcode=c['opcode']) for c in commands)
   result.append(dict(site=p,kind='INDEX44_ADJACENT_PERIOD_DATA_UNPROVED',target=None,table_field=0x29de));continue
  if m=='bra':result.append(dict(site=p,kind='TAIL',target=t));continue
  if m.startswith('b') and m not in ['bset','bclr','btst'] or m=='dbra':
   require(t is not None,'unknown conditional edge');result.append(dict(site=p,kind='BRANCH',target=t));result.append(dict(site=p,kind='FALLTHROUGH',target=q));continue
  result.append(dict(site=p,kind='FALLTHROUGH',target=q))
 return result

def bank_save(items,register):
 for i in items:
  if i['mnemonic']=='movem.l' and i['operands'].endswith(', -(a7)'):
   regs=i['operands'].split(',')[0]
   for part in regs.split('/'):
    if '-' in part:
     a,z=part.split('-')
     if register[0]==a[0]==z[0] and int(a[1:])<=int(register[1:])<=int(z[1:]):return True
    elif part==register:return True
 return False

def derive(blob,model,calibration):
 from audio_register_calibration import require_preserved
 require_preserved(calibration,"d7")
 require("d2" in calibration["scratch"] and "d2" not in calibration["callee_saved"],"D2 scratch calibration required")
 raw=payload(blob,model,0);items=decode(raw[0x544c:0x5e6c],0x544c);by={i['offset']:i for i in items};commands=table(blob,model,by);es=edges(items,commands)
 sig=signature([i for i in items if 0x5a72<=i['offset']<0x5aca])
 for p,m,o in [(0x5912,'move.b','$49(a0), d0'),(0x591c,'subq.b','#$1, $8(a0)')]:at(by,p,m,o)
 require(not any('(a5)' in i['operands'] or '(a7)' in i['operands'] for i in items if 0x5912<=i['offset']<0x5922),'dispatcher call acquired stack arguments')

 for p,m,o in [(0x5922,'bsr.w','$5a72'),(0x5a9c,'move.w','#$1, d2'),(0x5ac8,'bra.b','$5a50'),(0x5a70,'rts',''),(0x5aac,'bsr.w','$59a4'),(0x5a4a,'movem.l','(a7)+, a2-a4'),(0x5a4e,'rts','')]:at(by,p,m,o)
 # D2 is measured scratch in the canonical pinned-C corpus. Its writes
 # below are ordinary instructions and never provide non-C eligibility.
 require(not any(i['mnemonic'].split('.')[0] in ['link','unlk'] for i in items if 0x5a72<=i['offset']<0x5a9c),'register-entry frame changed')
 at(by,0x5a36,'beq.b','$5a46');at(by,0x5a46,'swap','d1')
 result=dict(schema_version=1,oracle_sha256=sha256(blob),dispatch=sig,handler_table=commands,
  dispatch_non_c=dict(kind='UNSTACKED_A0_CHANNEL_A1_STREAM_REGISTER_ARGUMENT_ENTRY_AND_JMP_ABI',entry=0x5a72,caller=0x5922,caller_channel_read=0x5912,caller_channel_timer_write=0x591c,stack_argument_push=False,channel_argument='A0',first_channel_read=0x5a72,parameter_prefetch=0x5a98,dispatch=0x5a9a,return_tail=0x5a50,return_site=0x5a70,stack_argument_fetch=False,c_compatible=False),
  index_bound=dict(compare=0x5a80,branch=0x5a84,inclusive_limit=44,proved_slots=44,first_opcode=0x80,last_opcode=0xab,index44_field=0x29de,index44_target='UNKNOWN_PERIOD_DATA_ALIAS',invented_slot=False),
  complete_edges=es,boundary_edges=[e for e in es if 0x5a72<=e['site']<0x5aca and (e['target'] is None or not 0x5a72<=e['target']<0x5aca)],data_credit=0)
 # Every pointer, direct transfer and shared entry is an instruction boundary.
 known_external={0x5064}
 require(all(e['target'] is None or e['target'] in by or e['target'] in known_external for e in es),'boundary edge lacks independent instruction entry')
 result['spans']=[]
 for lo,hi,name in SPANS:
  block=[i for i in items if lo<=i['offset']<hi];require(sum(i['size'] for i in block)==hi-lo,'partial proposed span')
  if name=='envelope':
   for p,m,o in [(0x544c,'tst.b','$1e(a0)'),(0x54ae,'rts',''),(0x54b4,'rts',''),(0x5926,'move.b','$44(a0), d0'),(0x5930,'move.b','#$5, $1e(a0)'),(0x5936,'bsr.w','$544c')]:at(by,p,m,o)
   call_setup=[i for i in items if 0x5926<=i['offset']<0x5936]
   require(not any('(a5)' in i['operands'] or '(a7)' in i['operands'] for i in call_setup),'envelope call acquired stack arguments')
   require(not any(i['mnemonic'].split('.')[0] in ['link','unlk'] for i in block),'envelope register-entry frame changed')
   predicate=dict(kind='CALLER_SUPPLIED_A0_CHANNEL_REGISTER_ARGUMENT_ENTRY',entry=lo,caller=0x5936,caller_channel_read=0x5926,caller_channel_write=0x5930,first_parameter_read=0x544c,parameter='A0 channel',stack_argument_fetch=False,stack_argument_push=False,return_sites=[0x54ae,0x54b4],d2_preservation_is_not_a_witness=True)
  elif name=='world':
   for p,m,o in [(0x5796,'movea.l','$2b4a.l, a4'),(0x579c,'rts',''),(0x57a2,'movem.l','a0-a1, -(a7)'),(0x57a6,'bsr.b','$5796'),(0x57a8,'jsr','$5064(pc)'),(0x57ae,'movem.l','(a7)+, d1-d7/a0-a6'),(0x57bc,'move.l','a4, (a0)')]:at(by,p,m,o)
   predicate=dict(kind='A4_WORLD_LOAD_REGISTER_ARGUMENT_BRIDGE_AND_WORLD_CAPTURE',entries=[0x5796,0x579e,0x57b6],bank='A4',temporary_world_call=0x57a6,register_arguments=['A0','A1'],world_global=[1,0x2b4a],caller_world_restored=0x57ae)
  elif name=='start':
   require({'d0','d1','d2','a0','a1'}<=set(calibration['scratch']),'explicit scratch-bank premise changed')
   at(by,0x5d0c,'and.l','#$ff, d0');at(by,0x5d12,'jsr','$57e4(pc)');at(by,0x57e4,'movem.l','d0-d2/a0-a1, -(a7)');at(by,0x57e8,'and.l','#$ff, d0');at(by,0x5862,'movem.l','(a7)+, d0-d2/a0-a1');at(by,0x5866,'rts','')
   predicate=dict(kind='D0_REGISTER_ARGUMENT_AND_EXPLICIT_CALLER_SCRATCH_BANK_PRESERVATION',entry=lo,caller=0x5d12,parameter='D0',first_use=0x57e8,stack_argument_fetch=False,preserves_parameter=True,preserved_caller_scratch=['D0','D1','D2','A0','A1'])
  elif name=='update':
   for p,m,o in [(0x58bc,'movem.l','a2-a6, -(a7)'),(0x58c0,'bsr.b','$58c8'),(0x58c8,'moveq','#$3, d7'),(0x58d8,'tst.l','$4(a0)'),(0x58dc,'beq.b','$58e0'),(0x58e0,'dbra','d7, $58ca'),(0x58e4,'rts','')]:at(by,p,m,o)
   require_preserved(calibration,'d7')
   require(not bank_save(block,'d7'),'channel loop preserves the calibrated D7 bank')
   predicate=dict(kind='CALIBRATED_UNPRESERVED_D7_CHANNEL_LOOP',preservation_premise=dict(register='d7',compiler='3.6a',controls=['reg4','reg6'],measured=True),entry=lo,inner_entry=0x58c8,overwrite=0x58c8,return_site=0x58e4,empty_channels_witness=True,final_d7_long=0x0000ffff,final_d7_word=-1,saved=False)
  else:
   roots=[c for c in commands if lo<=c['addend_raw']<hi]
   require(roots or lo==0x5a50,'handler span has no independently relocated entry')
   predicate=dict(kind='DISPATCH_PROVED_A0_D7_A1_D0_REGISTER_ABI_COMPONENT',entries=sorted(set(c['addend_raw'] for c in roots)),opcodes=[c['opcode'] for c in roots],dispatch=0x5a9a,prefetch=0x5a98,no_new_call_frame=True,ordinary_c_stack_argument_entry=False,root_non_c_witness=result['dispatch_non_c'])
  if name in ['dispatch','handlers_b','handlers_c','handlers_d']:
   predicate['shared_tail_edges']=[dict(site=e['site'],target=e['target']) for e in es if lo<=e['site']<hi and e['kind']=='TAIL' and e['target'] in [0x5a50,0x5a76]]
   predicate['rewind_sites']=[i['offset'] for i in block if (i['mnemonic'],i['operands'])==('subq.l','#$1, a1')]
   predicate['register_inputs']=['A0 channel','D7 channel index','A1 stream','D0 prefetched byte']
  if name=='dispatch':
   for p,m,o in [(0x5bf0,'movem.l','a3-a4, -(a7)'),(0x5c12,'lea.l','-$581a(a4), a4'),(0x5c16,'movea.l','(a4, d0.w), a4'),(0x5c1a,'move.w','(a4)+, (a2, d1.w)'),(0x5c1e,'move.w','(a4)+, $4(a3)'),(0x5c22,'move.l','(a4)+, (a3)'),(0x5c54,'movem.l','(a7)+, a3-a4')]:at(by,p,m,o)
   predicate['saved_a4_record_consumer']=dict(save=0x5bf0,world_base=0x5c12,indexed_replacement=0x5c16,reads=[2,2,4],restore=0x5c54)
  predicate['c_compatible']=False
  result['spans'].append(dict(start=lo,end=hi,size=hi-lo,name=name,sha256=sha256(raw[lo:hi]),predicate=predicate,boundary_edges=[e for e in es if lo<=e['site']<hi and (e['target'] is None or not lo<=e['target']<hi)]))
 result['unclaimed']=[dict(start=a,end=z,reason=why) for a,z,why in [(0x55d6,0x5796,'IRQ routines use only ordinary C scratch D0/A0; no non-C predicate established'),(0x57c0,0x57d2,'save-bank/timer wrapper lacks sufficient non-C evidence'),(0x57d2,0x57e4,'C-compatible stack-argument prefix'),(0x5868,0x58bc,'initializer routine lacks sufficient non-C evidence'),(0x5cc2,0x5cc6,'unreferenced tail fragment; no entry proof'),(0x5d74,0x5d78,'unreferenced tail fragment; no entry proof'),(0x5d80,0x5d92,'unreferenced A4 callback fragment; no entry proof')]]
 return result


def control_rejections(items,calibration=None):
 """Instruction-level negative controls, independent of curated span IDs.

 A frame, ordinary indirect C call, hardware store or a frameless return never
 establishes any register-stream, saved-world or unpreserved-bank predicate.
 """
 frame=any(i['mnemonic'].split('.')[0] in ['link','unlk'] for i in items)
 try:signature(items);stream=True
 except Exception as e:
  from common import FormatError
  require(isinstance(e,FormatError),'unexpected signature control failure');stream=False
 banks=[]
 for i in items:
  m=i['mnemonic'].split('.')[0];dst=i['operands'].rsplit(', ',1)[-1]
  if m in ['move','movea','moveq','lea','clr','add','adda','addq','sub','subq','and','or','eor','lsl','lsr','asl','swap'] and re.fullmatch(r'(?:d[2-7]|a[2-6])',dst) and calibration is not None and dst in calibration['callee_saved'] and not frame and not bank_save(items,dst):banks.append(dict(site=i['offset'],register=dst))
 saved_a4=not frame and any(i['mnemonic']=='lea.l' and i['operands']=='-$581a(a4), a4' for i in items) and any(i['mnemonic']=='movea.l' and i['operands']=='(a4, d0.w), a4' for i in items)
 bridge=not frame and len(items)>1 and (items[0]['mnemonic'],items[0]['operands'])==('movem.l','d0-d2/a0-a1, -(a7)') and (items[1]['mnemonic'],items[1]['operands'])==('and.l','#$ff, d0')
 frame_free_jump=not frame and any(i['mnemonic']=='jmp' and i['operands']=='(a2)' for i in items) and stream
 capture=not frame and any(i['mnemonic']=='move.l' and i['operands']=='a4, (a0)' for i in items)
 world_bridge=not frame and any(i['mnemonic']=='movem.l' and i['operands']=='a0-a1, -(a7)' for i in items) and any(i['mnemonic'].startswith('bsr') and i['operands']=='$5796' for i in items)
 a0_entry=not frame and bool(items) and (items[0]['mnemonic'],items[0]['operands'])==('tst.b','$1e(a0)')
 return dict(a0_register_argument_entry=a0_entry,a4_world_capture=capture,a4_world_argument_bridge=world_bridge,unstacked_stream_dispatch=stream,unpreserved_nonvolatile_bank=bool(banks),saved_a4_record_world_reuse=saved_a4,d0_register_argument_entry=bridge,shared_tail_register_dispatch=frame_free_jump,bank_writes=banks)
