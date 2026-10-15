"""Address-taken CODE entries from independent decoded API use, not prologues.

The Amiga small-int ABI is pinned: pointer/long4, short2, byte1. SDK Node14,
Message20, Interrupt.is_Code18, IORequest.io_Command28, IOStdReq.io_Data40.
A PC-relative address alone is NOT a CODE classification; literal references
and arbitrary pointer stores remain DATA candidates. No source acceptance.
"""
from common import require,sha256
from analysis_support import instruction,K
HEADERS=('exec/nodes.h','exec/interrupts.h','exec/io.h','devices/input.h')
PREFIX='toolchain/installed/aztec-3.6a/SYS1/include/'

def identity(root):
    from resident_mixed import pinned
    out={PREFIX+p:sha256(pinned(root,PREFIX+p)) for p in HEADERS}
    text=pinned(root,PREFIX+'exec/interrupts.h').decode('ascii')
    require('struct Node is_Node;' in text and 'APTR is_Data;' in text and 'VOID (*is_Code)();' in text,'pinned Interrupt ABI changed')
    return out

def callback_apis(root,blob,model):
    identity(root)
    from runtime_entry_routes import load
    routes=load(root,sha256(blob),original=(blob,model),audit=True)
    names={'_SetIntVector','_AddIntServer','_DoIO','_OpenDevice'}
    return {key:row['symbol'] for key,row in routes.items() if row['symbol'] in names}

def absolute_data(c,h,ins):
    rels=[r for (rh,off),r in c.relocs.items() if rh==h and ins.address<=off and off+4<=ins.address+ins.size]
    if len(rels)!=1:return None
    r=rels[0]
    return r['addend_raw'] if r['target_hunk']==1 and r['width']==4 and r['type']=='HUNK_RELOC32' else None

def name(c,h,ins):
    t=c.target(h,ins)
    return c.callback_apis.get(t[:2]) if t else None

def discover(c,functions):
    added=0
    for f in functions:
        # Only independently closed source callers drive this rule. A weak
        # adjacent LINK cannot manufacture strong references for itself.
        if f['extent_status']!='CLOSED_CFG':continue
        h=f['hunk'];ins=[instruction(c.md,c.data[h],r['offset']) for r in f['instructions']]
        records={}
        input_requests=set()
        for j,i in enumerate(ins):
            if i.mnemonic=='jsr' and name(c,h,i)=='_OpenDevice' and j>=4:
                flags,request,unit,p=ins[j-4:j];t=c.target(h,p)
                slot=absolute_data(c,h,request)
                if (p.mnemonic=='pea.l' and t and t[0]==h and slot is not None and
                    (flags.mnemonic,flags.op_str)==('clr.l','-(a7)') and
                    (unit.mnemonic,unit.op_str)==('clr.l','-(a7)') and
                    (request.mnemonic,request.op_str)==('move.l','$%x.l, -(a7)'%slot) and
                    c.data[h][t[1]:t[1]+13]==b'input.device\0'):
                    input_requests.add(slot)
            if i.mnemonic!='jsr':continue
            api=name(c,h,i)
            if api in ('_SetIntVector','_AddIntServer') and j>=2:
                p,n=ins[j-2:j]
                record=absolute_data(c,h,p)
                # A real long stack argument followed by a long interrupt
                # number and exact pinned public API entry, never an interior.
                if (p.mnemonic=='pea.l' and record is not None and n.mnemonic=='pea.l'
                    and n.size==4 and n.operands[0].address_mode==K.M68K_AM_ABSOLUTE_DATA_SHORT):
                    records[record]=dict(contract='SDK_INTERRUPT_IS_CODE',registration_site=i.address,api=api)
            elif api=='_DoIO' and input_requests and j>=6:
                a,b,d,e,g,p=ins[j-6:j]
                request=absolute_data(c,h,a);record=absolute_data(c,h,d)
                if (request in input_requests and record is not None and
                    (a.mnemonic,a.op_str)==('movea.l','$%x.l, a0'%request) and
                    (b.mnemonic,b.op_str)==('move.w','#$9, $1c(a0)') and
                    d.mnemonic=='lea.l' and d.op_str.endswith(', a0') and
                    (e.mnemonic,e.op_str)==('movea.l','$%x.l, a1'%request) and absolute_data(c,h,e)==request and
                    (g.mnemonic,g.op_str)==('move.l','a0, $28(a1)') and
                    (p.mnemonic,p.op_str)==('move.l','$%x.l, -(a7)'%request) and absolute_data(c,h,p)==request):
                    records[record]=dict(contract='SDK_INPUT_DEVICE_ADDHANDLER_IS_CODE',registration_site=i.address,api=api,request_hunk=1,request_slot=request)
        for j,i in enumerate(ins):
            if i.mnemonic not in ('lea.l','pea.l'):continue
            target=c.target(h,i)
            if not target or target[2]!='PC_RELATIVE' or not c.valid(target[0],target[1]):continue
            evidence=None
            independent=c.entries.get(target[:2],[])
            if any(e['kind'] in ('DIRECT_CALL','OVERLAY_EXPORT','PROVEN_RUNTIME','EXECUTABLE_ENTRY','CURATED_UNREFERENCED_ENTRY') for e in independent):
                evidence=dict(contract='ALREADY_INDEPENDENT_CODE_ENTRY')
            if i.mnemonic=='lea.l' and j+1<len(ins):
                store=ins[j+1];slot=absolute_data(c,h,store)
                reg=i.operands[-1]
                if reg.type==K.M68K_OP_REG and slot is not None and store.mnemonic=='move.l' and store.operands[0].type==K.M68K_OP_REG and store.operands[0].reg==reg.reg:
                    record=slot-18
                    if record in records:evidence=dict(records[record],record_hunk=1,record_offset=record,code_field_offset=18,store_site=store.address)
            if evidence is None:continue
            key=(h,i.address);fact=dict(hunk=target[0],offset=target[1],basis='PC_RELATIVE',evidence=evidence)
            if key in c.function_references:
                require(c.function_references[key]==fact,'conflicting decoded function reference')
                continue
            c.function_references[key]=fact
            c.seed(target[0],target[1],dict(kind='FUNCTION_REFERENCE',caller=f['id'],site=i.address,basis='PC_RELATIVE',reference_evidence=evidence))
            added+=1
    return added
