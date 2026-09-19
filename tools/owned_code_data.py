"""Strict proof for compiler-owned PC-relative string tails in CODE.

Aztec may emit a function's string literals immediately after its final RTS in
the same CODE contribution.  This module never treats that as ordinary
function code.  It verifies the separately evidenced tail, its exact bounds,
and every PC-relative instruction that addresses it before asking the normal
function comparator to normalize relocations and A4 references.
"""
import copy

from analysis_support import K,decoder,instruction,game
from common import FormatError,sha256
from function_compare import compare_function,decode_all


def alignment_padding(tail):
    """Return the zero bytes Aztec adds to word-align a CODE literal bundle."""
    return b'\0' if len(tail)&1 else b''


def expected_string_tail(f):
    """Return the contiguous printable-string tail independently evidenced for f.

    The ledger records printable strings from executable data references.  A
    candidate may own a tail only when every same-hunk PC-relative reference
    points at one of those strings and the NUL-terminated strings occupy every
    byte immediately after the closed function extent.  A single zero byte is
    accepted only when it is the word-alignment padding required by an
    odd-length literal bundle and the immutable hunk contains that exact byte.
    This deliberately rejects interleaved bytes, inferred literals, and distant
    data.
    """
    refs=sorted(r['offset'] for r in f['referenced_data']
                if r['kind']=='PC_RELATIVE_DATA' and r['hunk']==f['hunk'])
    strings=sorted((s['offset'],s['text']) for s in f['referenced_strings']
                   if s['hunk']==f['hunk'])
    if not refs:
        raise FormatError('function has no same-hunk PC-relative data references')
    if len(refs)!=len(set(refs)):
        raise FormatError('duplicate PC-relative data reference requires stronger ownership proof')
    if [offset for offset,_ in strings]!=refs:
        raise FormatError('PC-relative data references are not exactly the printable string evidence')
    cursor=f['end'];tail=[]
    for offset,text in strings:
        try:raw=text.encode('ascii')+b'\0'
        except UnicodeEncodeError as exc:raise FormatError('non-ASCII owned string evidence') from exc
        if offset!=cursor:
            raise FormatError('owned string tail is not contiguous immediately after function extent')
        tail.append(raw);cursor+=len(raw)
    literals=b''.join(tail);padding=alignment_padding(literals)
    if padding:
        blob,model,_=game()
        hunk=next((h for h in model['hunks'] if h['number']==f['hunk']),None)
        if hunk is None:
            raise FormatError('owned string tail hunk is absent from immutable game model')
        pad=blob[hunk['content_offset']+cursor:hunk['content_offset']+cursor+len(padding)]
        if pad!=padding:
            raise FormatError('owned string tail alignment padding is not the immutable zero byte')
    return literals+padding,dict(start=f['end'],end=cursor+len(padding),
        strings=[dict(offset=o,text=t) for o,t in strings],alignment_padding=len(padding))


def pc_relative_tail_proof(f,prefix,tail_start):
    """Prove candidate PC-relative operands address the declared tail offsets."""
    expected=bytes.fromhex(f['raw_bytes']);ei,ebad=decode_all(expected);ai,abad=decode_all(prefix)
    if ebad is not None or abad is not None or len(ei)!=len(ai):
        raise FormatError('cannot decode complete code prefix for PC-relative tail proof')
    refs={r['instruction_offset']:r['offset'] for r in f['referenced_data']
          if r['kind']=='PC_RELATIVE_DATA' and r['hunk']==f['hunk']}
    proof=[]
    for e,a in zip(ei,ai):
        if e.address+f['start'] not in refs:continue
        if e.mnemonic!=a.mnemonic or len(e.operands)!=len(a.operands):
            raise FormatError('PC-relative data instruction layout differs at +0x%X'%e.address)
        # Capstone represents the base register for this 68000 addressing mode
        # as zero on some releases; the addressing-mode tag is the stable fact.
        operands=[(eo,ao) for eo,ao in zip(e.operands,a.operands)
                  if eo.type==ao.type==K.M68K_OP_MEM and
                  eo.address_mode==ao.address_mode==K.M68K_AM_PCI_DISP]
        if len(operands)!=1:
            raise FormatError('PC-relative data instruction is not uniquely comparable at +0x%X'%e.address)
        eo,ao=operands[0];expected_target=refs[e.address+f['start']]
        original_target=f['start']+e.address+2+eo.mem.disp
        candidate_target=a.address+2+ao.mem.disp
        if original_target!=expected_target:
            raise FormatError('ledger PC-relative target disagrees with instruction at +0x%X'%e.address)
        if candidate_target!=tail_start+(expected_target-f['end']):
            raise FormatError('candidate PC-relative target does not address owned tail at +0x%X'%e.address)
        proof.append(dict(kind='PC_RELATIVE_OWNED_STRING',offset=e.address,
                          original_offset=expected_target,candidate_offset=candidate_target,
                          tail_offset=expected_target-f['end']))
    if len(proof)!=len(refs):
        raise FormatError('not every PC-relative string reference has a candidate proof')
    return proof


def compare_owned_code_data(f,compiled,a4_bias,source_text=None):
    """Compare a closed function plus a separately proven compiler CODE tail.

    The returned verdict is intentionally an intermediate proof level.  It is
    unsuitable for ordinary promotion until a complete natural source unit
    owns both the function and this tail without gaps.
    """
    report=dict(verdict='BLOCKED',proof_level=None,expected_length=f['size'],actual_length=None,
                compiler=compiled['identity']['profile'],flags=compiled['identity']['flags'],
                cache_key=compiled['cache_key'],cache_hit=compiled['cache_hit'],owned_code_data=None)
    if compiled['status']!='COMPILED':
        report.update(reason=compiled['status']);return report
    c=compiled['contribution'];actual=bytes.fromhex(c['code_hex']);report['actual_length']=len(actual)
    tail=None
    try:
        tail,ownership=expected_string_tail(f)
        if c.get('entry_offset',0):raise FormatError('multi-function object requires complete unit proof')
        if c['data_size'] or c['bss_size']:raise FormatError('candidate has separate DATA/BSS contribution')
        if len(actual)!=f['size']+len(tail):raise FormatError('candidate CODE contribution has unclaimed bytes')
        if actual[f['size']:]!=tail:raise FormatError('candidate CODE tail differs from independently evidenced strings')
        pc_proof=pc_relative_tail_proof(f,actual[:f['size']],f['size'])
    except FormatError as exc:
        report.update(reason=str(exc),owned_code_data=dict(expected_tail_sha256=sha256(tail) if tail is not None else None,
                                                            actual_tail_sha256=sha256(actual[f['size']:]),
                                                            actual_tail_length=max(0,len(actual)-f['size'])))
        return report
    piece=copy.deepcopy(compiled);pc=piece['contribution']
    # A complete-unit verifier supplies the member's original hunk-relative
    # base so same-overlay PC calls can be proved against the full natural
    # unit.  A standalone candidate still has the ordinary zero default.
    pc.update(code_hex=actual[:f['size']].hex(),code_size=f['size'],code_offset=pc.get('code_offset',0))
    code_report=compare_function(f,piece,a4_bias,allow_pc_relative_data=True,source_text=source_text)
    report.update(code_comparison=code_report,owned_code_data=dict(**ownership,expected_tail_sha256=sha256(tail),
        actual_tail_sha256=sha256(actual[f['size']:]),actual_tail_length=len(tail),pc_relative_proof=pc_proof))
    for key in ('mnemonic_similarity','prologue','epilogue','relocation_equal','relocation_proof',
                'relocation_issues','normalized_first_difference','first_differing_instruction'):
        if key in code_report:report[key]=code_report[key]
    if code_report['verdict']=='EQUAL':
        report.update(verdict='EQUAL',reason='FUNCTION_AND_COMPILER_OWNED_CODE_DATA_MATCH',
                      proof_level='FUNCTION_WITH_DATA_MATCH')
    else:
        report.update(verdict='DIFFER',reason='FUNCTION_CODE_OR_REFERENCE_DIFFERS')
    return report
