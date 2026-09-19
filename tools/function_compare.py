"""Exact complete-function comparison with explicit relocation/address identity proofs."""
from difflib import SequenceMatcher
import re
from analysis_support import decoder,instruction,K,basic,ROOT
from common import require,sha256,FormatError
from compare import first_bytes


def decode_all(raw):
    md=decoder();out=[];pc=0
    while pc<len(raw):
        ins=instruction(md,raw,pc)
        if ins is None:return out,pc
        out.append(ins);pc+=ins.size
    return out,None


def first_structural_instruction_difference(expected,actual):
    """Return the first mnemonic/width divergence without masking references.

    Exact comparison still owns the verdict.  This auxiliary receipt avoids
    letting the first naturally different A4 displacement hide the code-shape
    mismatch that a candidate author can actually revise.
    """
    ei,ebad=decode_all(expected);ai,abad=decode_all(actual)
    if ebad is not None or abad is not None:return None
    expected_shape=[(i.mnemonic,i.size) for i in ei]
    actual_shape=[(i.mnemonic,i.size) for i in ai]
    for tag,i1,i2,j1,j2 in SequenceMatcher(None,expected_shape,actual_shape).get_opcodes():
        if tag=='equal':continue
        return dict(kind=tag,
                    expected=[basic(i) for i in ei[i1:min(i2,i1+3)]],
                    actual=[basic(i) for i in ai[j1:min(j2,j1+3)]])
    return None


def mechanical(name):
    m=re.fullmatch(r'_?([GF])_h(\d+)_(?:0x)?([0-9A-Fa-f]+)',name)
    return None if m is None else (int(m[2]),int(m[3],16),m[1])


def target_identity(hunk,offset,symbols,bounds=None):
    entries=[]
    for s in symbols:
        identity=mechanical(s['name'])
        if identity and s['hunk']==hunk and s['offset']<=offset:
            entries.append((s['offset'],identity,s['name']))
    if not entries:return None
    location,identity,name=max(entries)
    # Data addends are constrained further by evidence identities and instruction
    # correspondence. Function symbols may not absorb unrelated code offsets.
    delta=offset-location
    if identity[2]=='F' and delta:return None
    if identity[2]=='G' and delta and (bounds is None or delta>=bounds.get(name,0)):return None
    return dict(hunk=identity[0],offset=identity[1]+delta,symbol=name,addend=delta)


def overlay_trampoline_identity(contribution,stub,symbols,bounds=None):
    """Resolve one parsed Manx trampoline without treating its bytes as data.

    The overlay table is separately validated by ``manx_overlay`` when the
    compiler artifact is extracted.  A candidate still passes only if the
    table's physical target has a mechanical proxy symbol whose hunk/offset
    identity equals the original call evidence.
    """
    entry=next((x for x in contribution.get('overlay_trampolines',[])
                if x['trampoline_hunk']==1 and x['trampoline_offset']==stub),None)
    if entry is None:return None
    return target_identity(entry['target_hunk'],entry['target_offset'],symbols,bounds)


def unique_word_site(ins,value):
    word=(value & 65535).to_bytes(2,'big');raw=bytes(ins.bytes)
    sites=[i for i in range(2,len(raw)-1,2) if raw[i:i+2]==word]
    return sites[0] if len(sites)==1 else None


def runtime_symbol_names(evidence):
    """Names eligible for a separately proven runtime contribution alias."""
    return {entry['name'] for contribution in evidence['contributions']
            for entry in contribution['entries']}


def compare_function(f,compiled,a4_bias,allow_pc_relative_data=False):
    report=dict(expected_length=f['size'],actual_length=None,compiler=compiled['identity']['profile'],flags=compiled['identity']['flags'],
                cache_key=compiled['cache_key'],cache_hit=compiled['cache_hit'],verdict='BLOCKED',relocation_equal=False,proof_level=None)
    if compiled['status']!='COMPILED':
        report.update(reason=compiled['status'],compile_returncodes=compiled['guest_returncodes']);return report
    c=compiled['contribution'];expected=bytes.fromhex(f['raw_bytes']);actual=bytes.fromhex(c['code_hex'])
    if c.get('entry_offset',0):
        report.update(actual_length=len(actual),reason='MULTI_FUNCTION_OBJECT_REQUIRES_COMPLETE_UNIT_PROOF');return report
    # Manx symbol maps label folded COMMON as logical H2, while storage is in
    # the tail of root H1. Verify that convention from this linked artifact.
    symbol_map=[dict(s) for s in c['symbols']]
    data_hunk=next(h for h in c['hunks'] if h['number']==1)
    bss_hunk=next(h for h in c['hunks'] if h['number']==2)
    org=next((s['offset'] for s in symbol_map if s['name']=='__H2_org'),None)
    if org==data_hunk['initialized_size'] and bss_hunk['allocated_size']==4:
        for s in symbol_map:
            if s['hunk']==2 and org<=s['offset']<data_hunk['allocated_size']:
                s['hunk']=1
    from pathlib import Path
    source=(Path(compiled['directory'])/(compiled['prefix']+'.c')).read_text()
    int_size=2 if compiled['identity']['profile'] in ('aztec36','aztec50-short') else 4
    bounds={}
    for m in re.finditer(r'extern\s+(?:(?:signed|unsigned)\s+)?(char|short|int|long|float|double)\s+(\**)(\w+)(?:\[(\d+)\])?\s*;',source):
        width=4 if m[2] else dict(char=1,short=2,int=int_size,long=4,float=4,double=8)[m[1]]
        bounds['_'+m[3]]=width*int(m[4] or 1)
    for m in re.finditer(r'extern\s+struct\s+\w+\s+(\w+)(?:\[\d+\])?\s*;',source):
        s=next((s for s in symbol_map if s['name']=='_'+m[1] and s['hunk']==1),None)
        if s:
            end=min((t['offset'] for t in symbol_map if t['hunk']==1 and t['offset']>s['offset']),default=data_hunk['allocated_size'])
            bounds[s['name']]=end-s['offset']
    report['actual_length']=len(actual)
    report['expected_sha256']=sha256(expected);report['actual_sha256']=sha256(actual)
    ei,ebad=decode_all(expected);ai,abad=decode_all(actual)
    report['mnemonic_similarity']=round(SequenceMatcher(None,[i.mnemonic for i in ei],[i.mnemonic for i in ai]).ratio(),4)
    report['prologue']={'expected':[basic(i) for i in ei[:3]],'actual':[basic(i) for i in ai[:3]]}
    report['epilogue']={'expected':[basic(i) for i in ei[-3:]],'actual':[basic(i) for i in ai[-3:]]}
    report['data_contributions']=dict(candidate_data=c['data_size'],candidate_bss=c['bss_size'],expected_owned_data='NOT_CLAIMED')
    report['raw_first_difference']=first_bytes(expected,actual)
    report['first_structural_instruction_difference']=first_structural_instruction_difference(expected,actual)
    if f['extent_status']!='CLOSED_CFG':report['reason']='UNCERTAIN_EVIDENCE_EXTENT';return report
    if c['data_size'] or c['bss_size'] or ebad is not None or abad is not None:
        report['reason']='DATA_OR_UNDECODED_CONTRIBUTION_REQUIRES_OWNERSHIP_PROOF';return report
    norm=bytearray(actual);proof=[];issues=[]
    original_refs={(r['hunk'],r['offset']) for r in f['referenced_data']}
    original_calls={(r['hunk'],r['offset']) for r in f['direct_callees']}
    # HUNK relocation fields are never simply zeroed. Each target is resolved by
    # the natural linker symbol map to an explicit original evidence identity.
    expected_relocs={r['relative_offset']:r for r in f['relocations']}
    actual_relocs={r['relative_offset']:r for r in c['relocations']}
    report['relocation_profiles']=dict(expected=list(expected_relocs.values()),actual=list(actual_relocs.values()))
    for off,r in actual_relocs.items():
        er=expected_relocs.get(off);identity=target_identity(r['target_hunk'],r['addend_raw'],symbol_map,bounds)
        if not er or r['type']!=er['type'] or r['width']!=er['width'] or not identity or (identity['hunk'],identity['offset'])!=(er['target_hunk'],er['addend_raw']):
            issues.append(dict(kind='HUNK_RELOCATION',offset=off,expected=er,actual=r,resolved=identity));continue
        norm[off:off+r['width']]=er['addend_raw'].to_bytes(r['width'],'big');proof.append(dict(kind='HUNK_RELOCATION',offset=off,identity=identity))
    for off in expected_relocs.keys()-actual_relocs.keys():issues.append(dict(kind='MISSING_HUNK_RELOCATION',offset=off))
    candidate_a4=None
    # The compiler's pinned small-data ABI sets A4 to root DATA+32766. Prove it
    # from the naturally linked startup's LEA relocation in the actual binary.
    from pathlib import Path
    blob=(Path(compiled['directory'])/(compiled['prefix']+'.exe')).read_bytes()
    runtime_evidence_path=ROOT/'evidence/experiments/runtime-arithmetic.json'
    runtime_evidence=None
    if runtime_evidence_path.exists():
        import json
        from analysis_support import game
        from runtime_arithmetic import aliases
        runtime_evidence=json.loads(runtime_evidence_path.read_text())
    if runtime_evidence and any(s['name'] in runtime_symbol_names(runtime_evidence) for s in c['symbols']):
        original,original_model,_=game()
        runtime_symbols,runtime_proof=aliases(compiled,blob,original,original_model,runtime_evidence)
        symbol_map.extend(runtime_symbols)
        report['runtime_contributions']=runtime_proof
        report['runtime_evidence_sha256']=sha256(runtime_evidence_path.read_bytes())
    root=next(h for h in c['hunks'] if h['number']==0)
    for r in c['all_relocations']:
        p=root['content_offset']+r['source_offset']
        if r['source_hunk']==0 and r['target_hunk']==1 and blob[p-2:p]==bytes.fromhex('49f9') and blob[p+4:p+6]==bytes.fromhex('4e75'):
            candidate_a4=r['addend_raw']
    same_layout=len(ei)==len(ai) and all(x.address==y.address and x.size==y.size and x.mnemonic==y.mnemonic for x,y in zip(ei,ai))
    # PC-relative data requires a separately owned data extent; code equality
    # alone cannot establish the target object's identity or bounds.
    if not allow_pc_relative_data and any(r['kind']=='PC_RELATIVE_DATA' for r in f['referenced_data']):
        issues.append(dict(kind='PC_RELATIVE_DATA_OWNERSHIP_UNPROVEN'))
    if same_layout:
        for e,a in zip(ei,ai):
            if len(e.operands)!=len(a.operands):continue
            for eo,ao in zip(e.operands,a.operands):
                if eo.type==ao.type==K.M68K_OP_MEM and eo.mem.base_reg==ao.mem.base_reg==K.M68K_REG_A4 and eo.address_mode==ao.address_mode==K.M68K_AM_REGI_ADDR_DISP:
                    eo_target=(1,a4_bias+eo.mem.disp)
                    identity=target_identity(1,(candidate_a4 or 0)+ao.mem.disp,symbol_map,bounds)
                    # A4 call stubs may name symbols in DATA at the stub itself.
                    if identity is None:
                        stub=(candidate_a4 or 0)+ao.mem.disp
                        rr=next((r for r in c['all_relocations'] if r['source_hunk']==1 and r['source_offset']==stub+2),None)
                        if rr:identity=target_identity(rr['target_hunk'],rr['addend_raw'],symbol_map,bounds)
                        if identity is None:identity=overlay_trampoline_identity(c,stub,symbol_map,bounds)
                    expected_identity=eo_target
                    if e.mnemonic.startswith(('jsr','jmp','pea')):
                        call=next((x for x in f['direct_callees'] if x['site']-f['start']==e.address),None)
                        if call:expected_identity=(call['hunk'],call['offset'])
                    site=unique_word_site(a,ao.mem.disp);es=unique_word_site(e,eo.mem.disp)
                    if candidate_a4 is None or identity is None or (identity['hunk'],identity['offset'])!=expected_identity or site is None or site!=es:
                        issues.append(dict(kind='A4_IDENTITY',offset=a.address,expected=expected_identity,actual=identity));continue
                    at=a.address+site;norm[at:at+2]=(eo.mem.disp&65535).to_bytes(2,'big')
                    proof.append(dict(kind='A4_D16_SYMBOL',offset=at,identity=identity,expected=expected_identity))
            if e.mnemonic.split('.')[0] in ('bsr','jsr') and e.operands[-1].address_mode != K.M68K_AM_REGI_ADDR_DISP:
                call=next((x for x in f['direct_callees'] if x['site']-f['start']==e.address),None)
                if call:
                    ao=a.operands[-1];disp=None;field=None;width=None
                    if ao.type==K.M68K_OP_BR_DISP:
                        disp=ao.br_disp.disp;width=1 if a.size==2 else 2 if a.size==4 else None
                        field=1 if width==1 else 2
                    elif ao.type==K.M68K_OP_MEM and ao.address_mode==K.M68K_AM_PCI_DISP and a.size==4:
                        disp=ao.mem.disp;field=2;width=2
                    identity=None
                    if disp is not None and width:
                        target=c.get('code_offset',0)+a.address+2+disp
                        identity=target_identity(c['hunk'],target,symbol_map)
                    if identity and (identity['hunk'],identity['offset'])==(call['hunk'],call['offset']):
                        at=a.address+field
                        norm[at:at+width]=bytes(e.bytes)[field:field+width]
                        proof.append(dict(kind='PC_RELATIVE_CALL_SYMBOL',offset=at,width=width,identity=identity))
                    else:
                        issues.append(dict(kind='DIRECT_CALL_BINDING_UNPROVEN',offset=e.address,target=call['id']))
    else:
        if any(r for r in f['referenced_data'] if r['kind']=='A4_RELATIVE'):issues.append(dict(kind='INSTRUCTION_LAYOUT_DIFFERS_FOR_SYMBOL_PROOF'))
    report.update(relocation_equal=not issues,relocation_proof=proof,relocation_issues=issues,
                  normalized_sha256=sha256(bytes(norm)),
                  normalized_first_difference=first_bytes(expected,bytes(norm)))
    equal=expected==bytes(norm) and not issues and len(expected)==len(actual)
    report.update(verdict='EQUAL' if equal else 'DIFFER',reason='COMPLETE_CONTRIBUTION' if equal else 'CODE_OR_REFERENCE_DIFFERS',
                  proof_level='FUNCTION_CODE_MATCH' if equal else None)
    mismatch=report['normalized_first_difference']
    if mismatch:
        off=mismatch['offset'];report['first_differing_instruction']={
            'expected':next((basic(i) for i in ei if i.address<=off<i.address+i.size),None),
            'actual':next((basic(i) for i in ai if i.address<=off<i.address+i.size),None)}
    return report
