"""Recursive-descent M68K evidence census. Uncertain extents never become source proof."""
import argparse
from collections import defaultdict,deque
import json
from pathlib import Path
from analysis_support import ROOT,K,decoder,game,instruction,basic,signed16,capstone
from common import require,sha256,write_json
from hunk import manx_overlay


def function_id(hunk,start):
    return ('resident' if hunk==0 else 'ov%02d'%hunk)+'_F_%04X'%start


class Census:
    def __init__(self,blob,model,ranges):
        self.blob=blob;self.model=model;self.md=decoder()
        self.hunks={h['number']:h for h in model['hunks']}
        self.data={h['number']:blob[h['content_offset']:h['content_offset']+h['initialized_size']]
                   for h in model['hunks'] if h['content_offset'] is not None}
        self.blocked=defaultdict(list)
        for r in ranges:
            if r['classification'] in ('DATA','STRING','BSS'):
                self.blocked[r['hunk']].append((r['start'],r['end'],r['classification']))
        self.entries=defaultdict(list);self.runtime=[]
        self.relocs={(r['source_hunk'],r['source_offset']):r for r in model['relocations']}
        self.a4_bias=None
        # Establish A4 solely from LEA abs.l,A4 plus its independent relocation.
        for r in model['relocations']:
            h,off=r['source_hunk'],r['source_offset']
            if h==0 and r['target_hunk']==1 and self.data[0][off-2:off]==bytes.fromhex('49f9') and self.data[0][off+4:off+6]==bytes.fromhex('4e75'):
                self.a4_bias=r['addend_raw'];self.a4_evidence=dict(hunk=0,offset=off-2,relocation=r)
        self.trampolines={}
        if model['overlay']:
            self.tree=manx_overlay(model,blob)
            for slot in self.tree['slots']:
                for s in slot['symbols']:
                    self.seed(s['target_hunk'],s['target_offset'],{'kind':'OVERLAY_EXPORT','slot':slot['slot']+1})
                    self.trampolines[s['trampoline_offset']]=(s['target_hunk'],s['target_offset'])
        self.seed(0,0,{'kind':'EXECUTABLE_ENTRY'})
        for r in model['relocations']:
            self.seed(r['target_hunk'],r['addend_raw'],{'kind':'RELOCATION_POINTER','source_hunk':r['source_hunk'],'source_offset':r['source_offset']})

    def valid(self,h,off):
        return h in self.hunks and self.hunks[h]['type']=='CODE' and 0<=off<len(self.data.get(h,b'')) and off%2==0 and not any(a<=off<b for a,b,_ in self.blocked[h])

    def seed(self,h,off,evidence):
        if self.valid(h,off) and evidence not in self.entries[(h,off)]:
            self.entries[(h,off)].append(evidence)

    def target(self,h,ins):
        if not ins.operands:return None
        o=ins.operands[-1]
        if o.type==K.M68K_OP_BR_DISP:
            return h,ins.address+2+o.br_disp.disp,'PC_RELATIVE'
        if o.type==K.M68K_OP_MEM and o.address_mode==K.M68K_AM_PCI_DISP:
            return h,ins.address+2+o.mem.disp,'PC_RELATIVE'
        rr=[r for (rh,ro),r in self.relocs.items() if rh==h and ins.address<=ro<ins.address+ins.size]
        if o.type==K.M68K_OP_MEM and o.address_mode in (K.M68K_AM_ABSOLUTE_DATA_LONG,K.M68K_AM_ABSOLUTE_DATA_SHORT) and len(rr)==1:
            r=rr[0];return r['target_hunk'],r['addend_raw'],'HUNK_RELOCATION'
        if o.type==K.M68K_OP_MEM and o.mem.base_reg==K.M68K_REG_A4 and o.address_mode==K.M68K_AM_REGI_ADDR_DISP and self.a4_bias is not None:
            off=self.a4_bias+o.mem.disp
            if off in self.trampolines:return (*self.trampolines[off],'A4_OVERLAY_TRAMPOLINE')
            r=self.relocs.get((1,off+2))
            if self.data.get(1,b'')[off:off+2]==bytes.fromhex('4ef9') and r:
                return r['target_hunk'],r['addend_raw'],'A4_RELOCATED_JMP_STUB'
        return None

    def walk(self,h,start):
        todo=[start];seen={};edges=[];calls=[];indirect=[];stops=[];refs=[];frames=[];args=[];saves=[];returns=[]
        while todo:
            pc=todo.pop()
            while pc not in seen:
                if pc!=start and (h,pc) in self.entries:
                    stops.append(dict(offset=pc,reason='OTHER_ENTRY'));break
                if not self.valid(h,pc):
                    stops.append(dict(offset=pc,reason='DATA_OR_OUTSIDE_CODE'));break
                ins=instruction(self.md,self.data[h],pc)
                if ins is None:
                    stops.append(dict(offset=pc,reason='UNDECODABLE'));break
                if any(eh==h and pc<ep<pc+ins.size for eh,ep in self.entries):
                    stops.append(dict(offset=pc,reason='ENTRY_INSIDE_INSTRUCTION'));break
                if any(pc<a<pc+ins.size or pc<b<pc+ins.size for a,b,_ in self.blocked[h]):
                    stops.append(dict(offset=pc,reason='INSTRUCTION_OVERLAPS_DATA'));break
                if any(p<pc<p+x['size'] or pc<p<pc+ins.size for p,x in seen.items()):
                    stops.append(dict(offset=pc,reason='OVERLAPPING_DECODE'));break
                row=basic(ins);seen[pc]=row;mn=ins.mnemonic.split('.')[0];nxt=pc+ins.size
                # A4 identities assume the established process small-data base.
                # Any explicit write/restore invalidates that assumption for this
                # function until register dataflow proves otherwise.
                dest=ins.operands[-1] if ins.operands else None
                if dest and ((dest.type==K.M68K_OP_REG and dest.reg==K.M68K_REG_A4)
                             or (dest.type==K.M68K_OP_REG_BITS and dest.register_bits & (1<<12))
                             or (mn=='exg' and any(o.type==K.M68K_OP_REG and o.reg==K.M68K_REG_A4 for o in ins.operands))):
                    stops.append(dict(offset=pc,reason='A4_BASE_DATAFLOW_UNPROVEN'))
                if mn=='link':frames.append(dict(offset=pc,register=ins.reg_name(ins.operands[0].reg),local_bytes=-signed16(ins.operands[1].imm & 65535)))
                if mn in ('movem','unlk'):saves.append(row)
                # A verified Manx trampoline is executable linkage even when
                # its address is passed as a callback rather than invoked at
                # this site.  Keep it out of generic DATA references so later
                # proof can require its code identity.
                pointer_target=self.target(h,ins) if mn=='pea' else None
                if pointer_target and pointer_target[2]=='A4_OVERLAY_TRAMPOLINE' and self.valid(pointer_target[0],pointer_target[1]):
                    th,to,basis=pointer_target
                    calls.append(dict(site=pc,hunk=th,offset=to,id=function_id(th,to),basis=basis,reference_kind='FUNCTION_POINTER'))
                    self.seed(th,to,dict(kind='FUNCTION_REFERENCE',caller=function_id(h,start),site=pc,basis=basis))
                for oi,o in enumerate(ins.operands):
                    if o.type==K.M68K_OP_MEM:
                        ref=None
                        if o.address_mode==K.M68K_AM_PCI_DISP and mn not in ('jsr','jmp'):
                            ref=dict(hunk=h,offset=pc+2+o.mem.disp,kind='PC_RELATIVE_DATA')
                        elif o.mem.base_reg==K.M68K_REG_A4 and o.address_mode==K.M68K_AM_REGI_ADDR_DISP and self.a4_bias is not None and pointer_target is None:
                            ref=dict(hunk=1,offset=self.a4_bias+o.mem.disp,kind='A4_RELATIVE')
                        if ref:
                            ref['instruction_offset']=pc;refs.append(ref)
                        if o.mem.base_reg==K.M68K_REG_A5 and o.mem.disp>=8:
                            args.append(dict(instruction_offset=pc,frame_offset=o.mem.disp,width=ins.mnemonic.split('.')[-1]))
                if mn in ('rts','rte','rtr','rtd'):
                    returns.append(pc);break
                if mn in ('stop','illegal','trap','trapv'):
                    stops.append(dict(offset=pc,reason='TERMINAL_OR_TRAP'));break
                is_call=mn in ('jsr','bsr')
                is_branch=mn in ('jmp','bra') or (ins.operands and ins.operands[-1].type==K.M68K_OP_BR_DISP and not is_call)
                if is_call or is_branch:
                    target=self.target(h,ins)
                    if is_call:
                        if target and self.valid(target[0],target[1]):
                            th,to,basis=target;calls.append(dict(site=pc,hunk=th,offset=to,id=function_id(th,to),basis=basis))
                            self.seed(th,to,dict(kind='DIRECT_CALL',caller=function_id(h,start),site=pc,basis=basis))
                        else:indirect.append(dict(offset=pc,kind='CALL',operands=ins.op_str))
                    else:
                        if target and target[0]==h and self.valid(h,target[1]):
                            to=target[1];edges.append(dict(source=pc,target=to,kind='UNCONDITIONAL' if mn in ('jmp','bra') else 'CONDITIONAL'))
                            if mn in ('jmp','bra') and pc==start and to!=start:
                                self.seed(h,to,dict(kind='TAIL_TARGET',caller=function_id(h,start),site=pc))
                            if (h,to) in self.entries and to!=start:
                                stops.append(dict(offset=pc,reason='TAIL_TO_ENTRY',target=to))
                            else:todo.append(to)
                        else:
                            indirect.append(dict(offset=pc,kind='JUMP',operands=ins.op_str));stops.append(dict(offset=pc,reason='UNRESOLVED_JUMP'))
                        if mn in ('jmp','bra'):break
                    if not is_call and mn not in ('jmp','bra'):
                        edges.append(dict(source=pc,target=nxt,kind='FALLTHROUGH'))
                pc=nxt
        ordered=[seen[p] for p in sorted(seen)];end=max((i['offset']+i['size'] for i in ordered),default=start)
        gaps=[];cursor=start
        for i in ordered:
            if i['offset']!=cursor:gaps.append([cursor,i['offset']])
            cursor=i['offset']+i['size']
        evidence=self.entries[(h,start)]
        strong=any(e['kind'] in ('OVERLAY_EXPORT','DIRECT_CALL','PROVEN_RUNTIME','EXECUTABLE_ENTRY') for e in evidence)
        complete=bool(ordered and returns and not stops and not gaps and strong and ordered[0]['mnemonic'].startswith('link') and all(p>=start for p in seen))
        return dict(id=function_id(h,start),hunk=h,node=self.hunks[h]['node'],start=start,end=end,size=end-start,
            raw_bytes=self.data[h][start:end].hex(),sha256=sha256(self.data[h][start:end]),entry_evidence=evidence,
            instructions=ordered,cfg=edges,direct_callees=calls,callers=[],indirect_control_flow=indirect,
            branch_targets=sorted({e['target'] for e in edges}),boundary_stops=stops,undecoded_gaps=gaps,
            relocations=[dict(r,relative_offset=r['source_offset']-start) for r in self.model['relocations'] if r['source_hunk']==h and start<=r['source_offset']<end],
            referenced_data=refs,referenced_strings=[],register_save_restore=saves,stack_frames=frames,
            likely_argument_accesses=args,return_sites=returns,extent_status='CLOSED_CFG' if complete else 'UNCERTAIN',
            confidence='HIGH' if complete else 'LOW',ownership='RUNTIME_CANDIDATE' if any(rh==h and a<=start<b for rh,a,b in self.runtime) else 'UNKNOWN',
            reconstruction_state='DISCOVERED',tail_bytes_included=False)

    def run(self):
        # Discovery fixpoint, followed by a stable pass with all entry barriers.
        previous=-1
        while previous!=len(self.entries):
            previous=len(self.entries)
            for h,start in sorted(list(self.entries),key=lambda x:({14:0,12:1,13:2,7:3}.get(x[0],4),x)):
                self.walk(h,start)
        functions=[self.walk(h,s) for h,s in sorted(self.entries)]
        by_id={f['id']:f for f in functions};coverage=defaultdict(set)
        for f in functions:
            for c in f['direct_callees']:
                if c['id'] in by_id:by_id[c['id']]['callers'].append(dict(id=f['id'],site=c['site'],basis=c['basis'],reference_kind=c.get('reference_kind','CALL')))
            for i in f['instructions']:coverage[f['hunk']].update(range(i['offset'],i['offset']+i['size']))
            for r in f['referenced_data']:
                data=self.data.get(r['hunk'],b'');off=r['offset']
                if 0<=off<len(data):
                    end=data.find(b'\0',off,min(len(data),off+160));raw=data[off:end] if end>=0 else b''
                    # A PC-relative reference is the evidence that this is a
                    # literal candidate.  Do not impose the generic four-byte
                    # string-search threshold here: short format fragments such
                    # as "%d " are compiler-owned CODE data too.  They still
                    # need a NUL terminator, printable payload, contiguous-tail
                    # proof, and an exact candidate contribution before any
                    # source promotion can use them.
                    if raw and all(32<=v<127 or v in (9,10,13) for v in raw):
                        f['referenced_strings'].append(dict(hunk=r['hunk'],offset=off,text=raw.decode('ascii'),confidence='REFERENCED_PRINTABLE_CANDIDATE'))
        unreached=[]
        for h in self.hunks.values():
            if h['type']!='CODE':continue
            start=None
            for off in range(h['initialized_size']+1):
                unknown=off<h['initialized_size'] and off not in coverage[h['number']]
                if unknown and start is None:start=off
                if not unknown and start is not None:
                    unreached.append(dict(hunk=h['number'],start=start,end=off,classification='NOT_REACHED_BY_DESCENT'));start=None
        return dict(schema_version=1,game_sha256=sha256(self.blob),decoder='Capstone '+capstone.__version__,
            analysis_identity={p:sha256((ROOT/'tools'/p).read_bytes()) for p in ('function_census.py','analysis_support.py')},
            method='RECURSIVE_DESCENT_FROM_EVIDENCE_ONLY',a4=dict(bias=self.a4_bias,evidence=getattr(self,'a4_evidence',None)),
            unreached_ranges=unreached,functions=functions,summary=dict(candidates=len(functions),closed_cfg=sum(f['extent_status']=='CLOSED_CFG' for f in functions),
                decoded_bytes=sum(len(v) for v in coverage.values()),by_hunk={str(k):len(v) for k,v in coverage.items()},reconstruction_claimed_by_census=False))


def build():
    blob,model,outputs=game();c=Census(blob,model,outputs['evidence/executable/byte-map.json']['ranges'])
    for file in ('runtime-matches.json','overlay-topology.json'):
        p=ROOT/'evidence/experiments'/file
        if not p.exists():continue
        report=json.loads(p.read_text())
        objects=report.get('objects',[])
        if 'runtime' in report:
            r=report['runtime'];objects=[dict(name='segload',matches=[dict(hunk=r['game_hunk'],offset=r['game_offset'],size=r['size'])])]
        for obj in objects:
            for m in obj['matches']:
                c.seed(m['hunk'],m['offset'],dict(kind='PROVEN_RUNTIME',candidate=obj['name']))
                c.runtime.append((m['hunk'],m['offset'],m['offset']+m['size']))
    return c.run()

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.parse_args()
    report=build();write_json(ROOT/'evidence/functions/ledger.json',report)
    print(json.dumps(report['summary']))
