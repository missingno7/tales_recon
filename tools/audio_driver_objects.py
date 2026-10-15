"""Complete AJ CODE grammar measured by the audio SYS1 as/ln controls.

Only zero-addend named external long DATA and external PC16 CODE fields are
supported. Empty segment transitions are checked explicitly; hidden DATA/BSS,
unknown records, masked references and trailers reject.
"""
from common import require,sha256

def parse(raw,initial_transition=True):
 require(len(raw)>=36 and raw[:10]==b'AJ'+bytes(8),'driver AJ header')
 u16=lambda p:int.from_bytes(raw[p:p+2],'big');u32=lambda p:int.from_bytes(raw[p:p+4],'big')
 size=u32(10);require(size>0 and u32(14)==u32(18)==0,'complete CODE-only AJ sections')
 start=u32(24)*4;syms=u16(28)*4;end=u16(30)*4
 require(start==36 and start<=syms<=end==u16(32)*4==len(raw) and raw[34:36]==b'\x80\0','driver AJ object bounds/model')
 count=u16(22);symbols=[];p=syms
 for n in range(count):
  require(p+4<=end,'truncated driver symbol');kind,attr=raw[p:p+2];value=u16(p+2);p+=4;reference_count=None
  require(kind in [2,7] and attr in [8,14] and (kind!=2 or attr==8),'driver symbol kind/attribute')
  if kind==7:
   require(value==0,'nonzero external offset')
   if attr==14:require(u16(p)>0,'external long-reference count');reference_count=u16(p);p+=2
  stop=raw.find(b'\0',p,end);require(stop>p,'driver symbol terminator');name=raw[p:stop].decode('ascii');p=stop+1
  require(all(32<=ord(c)<127 for c in name),'symbol encoding');symbols.append(dict(name=name,kind=kind,attribute=attr,offset=value,reference_count=reference_count))
 require(len({s['name'] for s in symbols})==count and end-p<=3 and raw[p:]==bytes(end-p),'complete unique symbol inventory/trailer')
 p=start
 if initial_transition:
  require(raw[p:p+2]==b'\xf5\xf4','measured initial empty DATA/CODE transition');p+=2
 code=bytearray();refs=[]
 while len(code)<size:
  require(p<syms,'truncated driver CODE');token=raw[p];p+=1
  if 0x10<=token<=0x1f:
   n=token-15;require(p+n<=syms and len(code)+n<=size,'driver literal extent');code+=raw[p:p+n];p+=n
  elif token in [0xfa,0xfd]:
   require(p+2<=syms and 0x70<=raw[p]<=0x7f and raw[p+1]==0,'named zero-addend driver reference')
   n=raw[p]-0x70;p+=2;require(n<count and symbols[n]['kind']==7,'reference must name an external')
   width=2 if token==0xfa else 4;kind='PC_RELATIVE_CODE16' if width==2 else 'HUNK_RELOC32'
   require(symbols[n]['attribute']==(8 if width==2 else 14),'reference section/type differs')
   refs.append(dict(offset=len(code),width=width,type=kind,symbol=symbols[n]['name'],symbol_index=n,addend=0));code+=bytes(width)
  else:require(False,'unknown driver AJ CODE token %02X'%token)
 require(p<syms and raw[p]==0xf5,'measured final empty DATA transition');p+=1
 require(1<=syms-p<=4 and raw[p:syms]==bytes(syms-p),'driver CODE trailer')
 require(all(s['reference_count']==sum(r['symbol']==s['name'] for r in refs) for s in symbols if s['kind']==7 and s['attribute']==14),'long reference inventory count')
 require(all(s['offset']<=size for s in symbols if s['kind']==2),'definition outside complete CODE')
 return bytes(code),refs,dict(CODE=size,DATA=0,BSS=0,COMMON=0,symbols=symbols,object_sha256=sha256(raw))
