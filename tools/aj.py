"""Strict bounded AJ external-word reference decoder.

Only the grammar established by evidence/rules/aj-external-fixups/controls is
supported. Reject other records, symbol attributes, addends and widths. Never
scan for a symbol name or infer references from the assembler text.
"""
from common import require,sha256,FormatError


def parse_external_words(blob):
    require(len(blob)>=36 and blob[:2]==b'AJ' and blob[2:10]==bytes(8),'unsupported AJ header')
    u16=lambda n:int.from_bytes(blob[n:n+2],'big')
    u32=lambda n:int.from_bytes(blob[n:n+4],'big')
    size=u32(10);require(u32(14)==u32(18)==0,'AJ DATA/BSS needs a separate proved grammar')
    count=u16(22);start=u32(24)*4;symbols_start=u16(28)*4;end=u16(30)*4
    require(start==36 and symbols_start<=end==u16(32)*4==len(blob),'unsupported AJ section layout')
    require(blob[34:36]==b'\xc0\0','unsupported AJ CODE origin')
    symbols=[];cursor=symbols_start
    for _ in range(count):
        require(cursor+4<=end,'truncated AJ symbol')
        kind,attribute=blob[cursor:cursor+2];value=u16(cursor+2);cursor+=4
        require(kind in (2,7) and attribute==8,'unsupported AJ symbol record')
        require(kind!=7 or value==0,'unsupported AJ external attributes')
        stop=blob.find(b'\0',cursor,end);require(stop>=cursor,'unterminated AJ symbol name')
        name=blob[cursor:stop]
        require(name and all(32<=b<127 for b in name),'unsupported AJ symbol name')
        symbols.append(dict(name=name.decode('ascii'),kind='CODE_DEFINITION' if kind==2 else 'EXTERNAL',offset=value))
        cursor=stop+1
    require(end-cursor<=3 and blob[cursor:]==bytes(end-cursor),'unexpected AJ symbol trailer')
    code=bytearray();refs=[];cursor=start
    while len(code)<size:
        require(cursor<symbols_start,'truncated AJ CODE stream')
        token=blob[cursor];cursor+=1
        if 0x10<=token<=0x1f:
            n=token-0x10+1
            require(cursor+n<=symbols_start and len(code)+n<=size,'AJ literal exceeds CODE extent')
            code+=blob[cursor:cursor+n];cursor+=n
        elif token==0xfa:
            require(cursor+2<=symbols_start,'truncated AJ external word')
            index_token,addend=blob[cursor:cursor+2];cursor+=2
            require(0x70<=index_token<=0x7f and addend==0,'unsupported AJ symbol index/addend')
            index=index_token-0x70;require(index<len(symbols) and symbols[index]['kind']=='EXTERNAL','AJ reference names no external')
            require(len(code)+2<=size,'AJ fixup exceeds CODE extent')
            refs.append(dict(offset=len(code),width=2,symbol=symbols[index]['name'],symbol_index=index,addend=0))
            code+=b'\0\0'
        else:raise FormatError('unsupported AJ CODE token 0x%02x at 0x%x'%(token,cursor-1))
    require(symbols_start-cursor<=3 and blob[cursor:symbols_start]==bytes(symbols_start-cursor),'unexpected AJ CODE trailer')
    require(all(s['offset']<size for s in symbols if s['kind']=='CODE_DEFINITION'),'AJ definition outside CODE')
    return dict(object_sha256=sha256(blob),code_size=size,code_hex=code.hex(),symbols=symbols,external_references=refs)


def linked_pc_bindings(parsed, linked_code, definitions):
    """Validate a normal linked PC call against separate object definitions.

    This bounded consumer handles JSR d16(PC) only. Register-relative gateways
    and public stack-call wrappers must not be confused with these bindings.
    """
    require(len(linked_code)==parsed['code_size'],'linked AJ contribution extent differs')
    result=[]
    for ref in parsed['external_references']:
        site=ref['offset'];require(site>=2 and linked_code[site-2:site]==b'\x4e\xba','unsupported AJ linked reference instruction')
        require(ref['symbol'] in definitions,'external definition is not independently bounded')
        target=site+int.from_bytes(linked_code[site:site+2],'big',signed=True)
        require(target==definitions[ref['symbol']],'natural AJ external binding differs')
        result.append(dict(ref,target=target))
    return result
