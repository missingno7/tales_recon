"""Complete staged startup source/binding verification; no canonical acceptance."""
from names import read_source
import json
from pathlib import Path
from analysis_support import K
import capstone
from common import require, sha256
from function_compare import unique_word_site
from overlay_experiment import symbols, contribution
from hunk import parse, manx_overlay
from startup_producer import verify as producer_verify
from startup_callees import verify as callee_verify
from repo_paths import canonical_path


def verify(root, blob, model_original, analysis, promotions, ledger):
    root = Path(root).resolve()
    producer = producer_verify(root)
    bindings = callee_verify(root, blob, model_original, analysis, promotions, ledger)
    for fid, target in [('resident_F_77A4', 30628), ('resident_F_7B24', 31524), ('resident_F_8534', 34100)]:
        item = ledger['functions'].get(fid)
        require(item and any(p['id'] == fid and p['hunk'] == 0 and p['start'] == target for p in promotions),
                'startup canonical callee missing')
        for key in ('source', 'proof'):
            require(sha256((read_source(root, item[key]) if str(item[key]).startswith('src/') else canonical_path(root, item[key]).read_bytes())) == item[key + '_sha256'],
                    'startup canonical callee stale')
    require(not any(r['source_hunk'] == 0 and r['source_offset'] < 30628 and
                    r['source_offset'] + r['width'] > 30316 for r in model_original['relocations']),
            'startup original CODE relocation differs')
    directory=root/'evidence/rules/startup-mechanical/abi'
    b=(directory/'x3.exe').read_bytes();model=parse(b);sm=symbols((directory/'x3.sym').read_text());start=sm[(0,'_recovered')]
    raw=contribution(b,model,0,start,312)
    obj=(directory/'x3.o').read_bytes()
    require(obj[:2]==b'AJ' and [int.from_bytes(obj[n:n+4],'big') for n in (10,14,18)]==[312,0,0],
        'complete startup object bounds/storage differ')
    require(sm[(0,'_segload')]==start+312 and not any(r['source_hunk']==0 and r['source_offset']<start+312 and
        r['source_offset']+r['width']>start for r in model['relocations']), 'startup boundary or relocation differs')
    om=model_original;original=contribution(blob,om,0,30316,312)
    md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000);md.detail=True
    ei=list(md.disasm(original[:310],0));ai=list(md.disasm(raw[:310],0))
    require(sum(i.size for i in ei)==sum(i.size for i in ai)==310 and not any(i.mnemonic.startswith('dc.') for i in ei+ai),'startup incomplete decode')
    require([(i.address,i.size,i.mnemonic) for i in ei]==[(i.address,i.size,i.mnemonic) for i in ai],'shape differs')
    fields=[];mask=set()
    for e,a in zip(ei,ai):
        require(len(e.operands)==len(a.operands),'startup operand count differs')
        for eo,ao in zip(e.operands,a.operands):
            require(eo.type==ao.type and eo.address_mode==ao.address_mode,'startup operand form differs')
            if eo.type!=K.M68K_OP_MEM:continue
            kind=None
            if eo.mem.base_reg==K.M68K_REG_A4 and eo.address_mode==K.M68K_AM_REGI_ADDR_DISP:
                kind='A4';old=32766+eo.mem.disp;actual=32766+ao.mem.disp
                if e.mnemonic=='jsr' and old==270:
                    name='_F_h00_8534';require(sm.get((1,name))==actual,'exit DATA name differs')
                    odh=next(h for h in om['hunks'] if h['number']==1)
                    original_entry=blob[odh['content_offset']+old:odh['content_offset']+old+6]
                    original_refs=[r for r in om['relocations'] if r['source_hunk']==1 and r['source_offset']<old+6 and r['source_offset']+r['width']>old]
                    require(original_entry==bytes.fromhex('4ef9')+(34100).to_bytes(4,'big') and len(original_refs)==1 and
                        original_refs[0]['source_offset']==old+2 and original_refs[0]['target_hunk']==0 and original_refs[0]['addend_raw']==34100,
                        'original exit route differs')
                    dh=next(h for h in model['hunks'] if h['number']==1)
                    require(0<=actual and actual+6<=dh['initialized_size'],'exit DATA bounds differ')
                    data=b[dh['content_offset']+actual:dh['content_offset']+actual+6]
                    require(data[:2]==bytes.fromhex('4ef9'),'exit DATA record differs')
                    rr=[r for r in model['relocations'] if r['source_hunk']==1 and r['source_offset']==actual+2]
                    require(len(rr)==1 and rr[0]['target_hunk']==0 and rr[0]['addend_raw']==sm[(0,'_exit_body')],'exit relocation differs')
                elif e.mnemonic=='jsr' and old==584:
                    name='_F_h03_0000'
                    otree=manx_overlay(om,blob)
                    original_routes=[s for slot in otree['slots'] for s in slot['symbols'] if s['trampoline_offset']==old]
                    require(len(original_routes)==1 and original_routes[0]['target_hunk']==3 and original_routes[0]['target_offset']==0 and original_routes[0]['encoded_node_id']==1,
                        'original main route differs')
                    tree=manx_overlay(model,b)
                    matches=[s for slot in tree['slots'] for s in slot['symbols'] if s['trampoline_offset']==actual]
                    require(len(matches)==1 and matches[0]['target_hunk']==3 and matches[0]['target_offset']==sm[(3,name)]==0 and matches[0]['encoded_node_id']==1,'main overlay route differs')
                else:
                    name='_G_h01_%04X'%old
                    require(any(n==name and h in (1,2) and off==actual for (h,n),off in sm.items()),'global identity differs')
            elif eo.address_mode==K.M68K_AM_PCI_DISP:
                old=e.address+2+eo.mem.disp;actual=a.address+2+ao.mem.disp
                if e.mnemonic=='jsr':
                    old+=30316;actual+=start;kind='CALL';name='_F_h00_%04X'%old
                    require(sm.get((0,name))==actual,'callee identity differs')
                else:
                    require(old==actual==310 and raw[310:]==original[310:]==b'*\0','literal identity differs')
                    name='COMPILER_LITERAL_STAR';kind='LITERAL'
            if kind:
                es=unique_word_site(e,eo.mem.disp);as_=unique_word_site(a,ao.mem.disp)
                require(es==as_ and es is not None,'field encoding ambiguous')
                pos=e.address+es;mask.update([pos,pos+1]);fields.append(dict(site=e.address,field=pos,kind=kind,symbol=name,original_offset=old,actual_offset=actual))
    require(len(fields)==38 and len(mask)==76,'startup field set differs')
    require(all(x==y for i,(x,y) in enumerate(zip(original,raw)) if i not in mask),'ordinary byte differs')
    marked_dir=root/'evidence/rules/startup-mechanical/partition'
    require([int.from_bytes((marked_dir/'marked.o').read_bytes()[n:n+4],'big') for n in (10,14,18)]==[312,0,0],
        'complete marked object bounds/storage differ')
    mb=(marked_dir/'marked.exe').read_bytes();mm=parse(mb);ms=symbols((marked_dir/'marked.sym').read_text());mst=ms[(0,'_recovered')]
    require(contribution(mb,mm,0,mst,312)==raw,'marker changes whole CODE')
    require([ms[(0,n)]-mst for n in ('_startup_asm_begin','_startup_asm_end')]==[48,54],'marker span differs')
    for key,off in sm.items():
        if key[1].startswith(('_G_h01_','_F_h00_','_F_h03_')):require(ms.get(key)==off,'marker changes bindings')
    report=dict(status='VERIFIED_STAGED_STARTUP_OBJECT',acceptance=False,
        code_bytes=312,c_compiler_bytes=304,sdk_asm_bytes=6,compiler_literal_bytes=2,
        field_identities=fields,masked_bytes=len(mask),ordinary_bytes=312-len(mask),
        partitions=[['C_COMPILER',0,48],['ASM',48,54],['C_COMPILER',54,310],['COMPILER_OWNED_DATA',310,312]])

    expected = {r['start'] for r in bindings['leaves']} | set(bindings['accepted_private_helpers']) | {30628, 31524}
    require({f['original_offset'] for f in fields if f['kind'] == 'CALL'} == expected,
            'startup complete callee set differs')
    report['source_sha256'] = producer['source_sha256']
    report['storage_ownership'] = 'UNKNOWN'
    report['callees_independently_bound'] = True
    return report


if __name__ == '__main__':
    from analysis_support import ROOT, game
    from recovery_state import evidence
    from recovery_evidence import load_promotions
    blob, model, _ = game(); analysis = evidence()
    ledger = json.loads((ROOT / 'recovery/ledger.json').read_bytes())
    report = verify(ROOT, blob, model, analysis, load_promotions(ROOT, blob, model, analysis), ledger)
    print(json.dumps(report, indent=2))
