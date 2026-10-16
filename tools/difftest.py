"""Differentially compare canonical C with its original 68000 function fixture.

Original CODE bytes are copied only from evidence/functions/ledger.json into
Unicorn memory. They are never emitted as reconstructed source. Direct callees
are stubbed on both sides as zero-return, no-side-effect functions; the result
records that modeling limit.
"""
from __future__ import annotations
import argparse, ctypes, hashlib, json, os, random, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/"build"/"difftest"
TOOLS=ROOT/"tools"
if str(TOOLS) not in sys.path: sys.path.insert(0,str(TOOLS))
for candidate in (os.environ.get("DIFFTEST_UNICORN_SITE"),r"C:\tools\gp-recon-python"):
    if candidate and candidate not in sys.path: sys.path.append(candidate)
CODE, RESIDENT_CODE, DATA, BSS, SCRATCH = 0x10000,0x200000,0x300000,0x400000,0x500000
SCRATCH_SIZE, STACK, SENTINEL, DEFAULT_TRIALS = 8192,0x800000,0xFFFF0,512
INSTRUCTION_BUDGET=500000

class Unsupported(Exception): pass
class ExecutionFailure(Exception):
    def __init__(self,message,details=None):
        super().__init__(message); self.details=details or {}

def digest(data): return hashlib.sha256(data).hexdigest()
def json_read(path): return json.loads(path.read_text(encoding="utf-8"))

def catalog():
    ledger=json_read(ROOT/"recovery"/"ledger.json")
    evidence=json_read(ROOT/"evidence"/"functions"/"ledger.json")
    entries={}
    for state,group in (("FUNCTION_CODE_MATCH",ledger.get("functions",{})),
                        ("BEHAVIORAL_CHAR_RETURN",ledger.get("behavioral_functions",{}))):
        for fid,item in group.items():
            if fid in entries: raise Unsupported("duplicate canonical ledger entry: "+fid)
            entries[fid]=dict(item,proof_category=state)
    return entries,{f["id"]:f for f in evidence.get("functions",[])}

def canonical_source(entry):
    path=(ROOT/entry.get("source","")).resolve()
    if not path.is_relative_to((ROOT/"src"/"recovered").resolve()): raise Unsupported("source is outside src/recovered")
    if not path.is_file(): raise Unsupported("canonical source is missing")
    raw=path.read_bytes()
    if entry.get("source_sha256") and digest(raw)!=entry["source_sha256"]: raise Unsupported("canonical source hash is stale")
    return path,raw.decode("latin-1")

def strip_comments(s):
    return re.sub(r"//[^\r\n]*"," ",re.sub(r"/\*.*?\*/"," ",s,flags=re.S))

def ctype(text,allow_void=False):
    s=re.sub(r"\b(const|volatile|register|auto|extern|static)\b"," ",text)
    stars=s.count("*"); base=" ".join(s.replace("*"," ").split())
    unsigned=base.startswith("unsigned "); signed=base.startswith("signed ")
    if unsigned or signed: base=base.split(None,1)[1]
    if base in ("int","short","short int"): kind,base="int","int"
    elif base in ("long","long int"): kind,base="long","long"
    elif base=="char": kind="char"
    elif base=="void" and allow_void: kind="pointer" if stars else "void"
    elif re.fullmatch(r"struct\s+[A-Za-z_]\w*",base): kind="pointer" if stars else "struct"
    else: raise Unsupported("untyped or unsupported C type: "+text.strip())
    if stars: kind="pointer"
    return dict(kind=kind,base=base,unsigned=unsigned,stars=stars,spelling=text.strip())

def declarator(text):
    m=re.match(r"(?P<stars>\**\s*)(?P<name>[A-Za-z_]\w*)(?P<array>\s*\[[^]]*\])?\s*$",text.strip())
    if not m: raise Unsupported("unsupported K&R declarator: "+text.strip())
    return m["name"],bool(m["stars"].count("*") or m["array"])

def signature(source):
    clean=strip_comments(source)
    matches=list(re.finditer(r"\brecovered\s*\(([^()]*)\)([^{}]*)\{",clean,re.S))
    if not matches: raise Unsupported("no K&R recovered() definition")
    m=matches[-1]; names_text=m[1].strip()
    names=[] if not names_text or names_text=="void" else [x.strip() for x in names_text.split(",")]
    if any(not re.fullmatch(r"[A-Za-z_]\w*",x) for x in names): raise Unsupported("non-identifier K&R parameter list")
    declared={}
    for stmt in m[2].split(";"):
        stmt=stmt.strip()
        if not stmt: continue
        t=re.match(r"(?:register\s+)*(?P<type>(?:(?:unsigned|signed)\s+)?(?:char|short(?:\s+int)?|int|long(?:\s+int)?|struct\s+\w+|void))\b(?P<decls>.*)",stmt)
        if not t: raise Unsupported("unsupported K&R parameter declaration: "+stmt)
        for part in t["decls"].split(","):
            name,ptr=declarator(part)
            if name not in names: raise Unsupported("non-parameter declaration before body: "+name)
            declared[name]=ctype(t["type"]+(" *" if ptr else ""),True)
    params=[]
    for name in names:
        ty=declared.get(name,dict(kind="int",base="int",unsigned=False,stars=0,spelling="implicit int"))
        if ty["kind"]=="struct" or (ty["kind"]=="pointer" and (ty["stars"]!=1 or ty["base"]=="void")):
            raise Unsupported("parameter layout is not modeled: "+name)
        params.append(dict(name=name,**ty))
    before=clean[:m.start()]; bound=max(before.rfind(";"),before.rfind("}"))
    ret=ctype(before[bound+1:].strip() or "int",True)
    if ret["kind"]=="struct" or (ret["kind"]=="pointer" and (ret["stars"]!=1 or ret["base"].startswith("struct "))):
        raise Unsupported("return type layout is not modeled")
    op=m.end()-1; depth=0; quote=None; escape=False; end=None
    for i in range(op,len(clean)):
        ch=clean[i]
        if quote:
            if escape: escape=False
            elif ch=="\\": escape=True
            elif ch==quote: quote=None
        elif ch in ("'","\""): quote=ch
        elif ch=="{": depth+=1
        elif ch=="}":
            depth-=1
            if depth==0: end=i; break
    if end is None: raise Unsupported("unbalanced source function body")
    return dict(params=params,return_type=ret,body=clean[op:end+1])

def model_type_layout(text,structs=None):
    structs=structs or data_model().get("structs",{})
    value=" ".join(text.replace("*"," * ").split())
    if value=="UNKNOWN": return None
    stars=value.count("*"); base=" ".join(value.replace("*","").split())
    dims=[int(x,16) if x.lower().startswith("0x") else int(x) for x in re.findall(r"\[\s*(0[xX][0-9A-Fa-f]+|\d+)\s*\]",base)]
    base=re.sub(r"\s*\[\s*\d+\s*\]", "",base).strip()
    count=1
    for n in dims: count*=n
    if stars: width=4; kind="pointer"
    elif base in ("char","unsigned char","signed char"): width=1; kind="char"
    elif base in ("int","unsigned int","signed int","short","unsigned short","short int","unsigned short int"): width=2; kind="int"
    elif base in ("long","unsigned long","signed long","long int","unsigned long int"): width=4; kind="long"
    elif base.startswith("struct "):
        spec=structs.get(base.split()[-1],{}); width=int(spec.get("size") or 0); kind="struct"
        if width<=0:return None
    else:return None
    return dict(kind=kind,base=base,width=width,count=count,size=width*count,stars=stars,unsigned=base.startswith("unsigned"))

def source_struct_layout(source,tag):
    clean=strip_comments(source)
    m=re.search(r"\bstruct\s+"+re.escape(tag)+r"\s*\{([^{}]*)\}",clean,re.S)
    if not m:return None
    fields=[]; offset=0
    for statement in m[1].split(";"):
        statement=statement.strip()
        if not statement:continue
        tm=re.match(r"(?P<base>(?:(?:unsigned|signed)\s+)?(?:char|short(?:\s+int)?|int|long(?:\s+int)?|struct\s+[A-Za-z_]\w*))\s+(?P<decls>.+)$",statement)
        if not tm:return None
        base=tm["base"].strip()
        for decl in tm["decls"].split(","):
            dm=re.fullmatch(r"\s*(?P<stars>\**)?\s*(?P<name>[A-Za-z_]\w*)(?P<dims>(?:\s*\[\s*(?:0[xX][0-9A-Fa-f]+|\d+)\s*\])*)\s*",decl)
            if not dm:return None
            stars=len(dm["stars"] or ""); dims=[int(x,16) if x.lower().startswith("0x") else int(x) for x in re.findall(r"\[\s*(0[xX][0-9A-Fa-f]+|\d+)\s*\]",dm["dims"])]
            count=1
            for n in dims:count*=n
            if stars:width=8; kind="pointer"; align=2
            elif base in ("char","unsigned char","signed char"):width=1;kind="char";align=1
            elif base in ("int","unsigned int","signed int","short","unsigned short","short int","unsigned short int"):width=2;kind="int";align=2
            elif base in ("long","unsigned long","signed long","long int","unsigned long int"):width=4;kind="long";align=2
            else:return None
            offset=(offset+align-1)//align*align
            fields.append(dict(name=dm["name"],offset=offset,width=width*count,element_width=width,count=count,kind=kind,base=base))
            offset+=width*count
    size=(offset+1)//2*2
    return dict(tag=tag,size=size,fields=fields)

def data_model_struct_entry(name,source_type,source):
    globals_model=data_model().get("globals",{}); structs=data_model().get("structs",{})
    item=globals_model.get(name,{})
    tag=item.get("struct")
    extent=item.get("extent")
    if not tag or not isinstance(extent,int) or tag not in structs:return None
    size=structs[tag].get("size")
    if not isinstance(size,int) or size<=0 or extent%size:return None
    source_tag=source_type["base"].split()[-1]
    view=source_struct_layout(source,source_tag)
    if not view or view["size"]!=size or any(f["kind"]=="pointer" for f in view["fields"]):return None
    model_count=extent//size
    if model_count>1 and not source_type.get("array",False):return None
    known=[]; unknown=[]; model_fields=structs[tag].get("fields",[])
    for field in model_fields:
        layout=model_type_layout(field.get("type","UNKNOWN"),structs)
        if layout is None:
            off=int(field["offset"]); next_off=min([int(x["offset"]) for x in model_fields if int(x["offset"])>off]+[size])
            unknown.append((off,next_off)); continue
        known.append((int(field["offset"]),layout["size"],layout["kind"],field))
    for member in view["fields"]:
        if member["kind"]=="char":continue
        match=next((x for x in known if x[0]==member["offset"] and x[1]==member["width"]),None)
        if not match and not any(a<=member["offset"] and member["offset"]+member["width"]<=b for a,b in unknown):return None
        member["pointer_value"]=bool(match and match[2]=="pointer" and member["width"]==4)
    return dict(tag=tag,size=size,extent=extent,model_count=model_count,view=view,
                pointer_offsets=[f["offset"] for f in view["fields"] if f.get("pointer_value")])

def globals_in(source,body):
    allg={}
    for m in re.finditer(r"\bextern\s+([^;]+);",strip_comments(source)):
        decl=m[1].strip()
        nm=re.search(r"\b(G_h(?P<h>\d{2})_(?P<o>[0-9A-Fa-f]{4}))\b\s*(?P<a>\[\s*(?P<n>\d+)\s*\])?\s*$",decl)
        if not nm: continue
        name=nm[1]; ty=ctype(decl[:nm.start()])
        count=int(nm["n"]) if nm["n"] else 1
        width={"char":1,"int":2,"long":4,"pointer":4}.get(ty["kind"],0)
        allg[name]=dict(name=name,hunk=int(nm["h"]),offset=int(nm["o"],16),type=ty,count=count,decl_count=count,
                        array=bool(nm["a"]),width=width,size=width*count)
    model_globals=data_model().get("globals",{})
    for name,g in allg.items():
        model_entry=model_globals.get(name,{})
        model_type=model_entry.get("type","")
        g["pointer_valued"]=bool(model_type!="UNKNOWN" and "*" in model_type)
        model_layout=model_type_layout(model_type) if model_type and model_type!="UNKNOWN" else None
        if model_layout and model_layout["kind"] in ("char","int","long") and model_entry.get("extent")==g["size"] and model_layout["size"]==g["size"] and model_layout["count"]==g["count"] and model_layout["width"]==g["width"]:
            g["model_scalar_type"]=model_layout
        if g["type"]["kind"]=="struct":
            layout=data_model_struct_entry(name,dict(g["type"],array=g["array"]),source)
            if layout:
                g["struct_model"]=layout["tag"];g["struct_size"]=layout["size"];g["model_count"]=layout["model_count"]
                g["host_count"]=max(g["decl_count"],layout["model_count"]);g["width"]=layout["size"];g["size"]=layout["extent"]
                g["struct_fields"]=layout["view"]["fields"];g["pointer_fields"]=layout["pointer_offsets"]
    for target,source_name in re.findall(r"\b(G_h\d{2}_[0-9A-Fa-f]{4})\s*=\s*\(\s*(?:unsigned\s+)?(?:long|int)\s*\)\s*&\s*(G_h\d{2}_[0-9A-Fa-f]{4})",body):
        if target in allg: allg[target]["pointer_valued"]=True; allg[target]["pointer_store_target"]=source_name
    used={n for n in allg if re.search(r"\b"+re.escape(n)+r"\b",body)}
    return allg,used

def callee_types(source,stubs):
    result={}; clean=strip_comments(source)
    for stub in stubs:
        m=re.search(r"\bextern\s+([^;]*?)\b"+re.escape(stub["name"])+r"\s*\([^;]*\)\s*;",clean,re.S)
        if m: result[stub["name"]]=ctype(m[1],True)
    return result

def calls_of(ev):
    calls=[]
    table_dispatches={int(x.get("dispatch_offset",-1)) for x in ev.get("jump_tables",[])}
    for ins in ev.get("instructions",[]):
        op=ins.get("mnemonic","").lower()
        if op.startswith(("bsr","jsr")): calls.append(ins)
        elif op.startswith("jmp") and int(ins.get("offset",-1)) not in table_dispatches:
            raise Unsupported("tail/indirect JMP without a measured jump table is unsupported")
    callees=ev.get("direct_callees",[])
    sites={x.get("site") for x in callees if x.get("site") is not None}
    offsets={x.get("offset") for x in calls}
    missing=sorted(offsets-sites)
    if missing: raise Unsupported("unresolved/indirect call at "+hex(missing[0]))
    # Some measured callee references identify a PEA/relocation supplying a
    # function pointer to an immediately following stubbed dispatcher. They
    # are not calls themselves and must not become emulator hooks.
    callees=[x for x in callees if x.get("site") in offsets]
    stubs=[]
    for x in callees:
        if any(x.get(k) is None for k in ("site","hunk","offset")): raise Unsupported("callee lacks measured target")
        stubs.append(dict(site=int(x["site"]),id=x.get("id"),name=f"F_h{int(x['hunk']):02d}_{int(x['offset']):04X}",
                          policy="returns zero; no side effects"))
    return calls,stubs

def prepare(fid,candidate=None):
    """Plan one comparison. ``candidate`` (a source path) checks an unresolved
    function's best candidate: execution evidence only, never a proof class."""
    entries,evs=catalog()
    if candidate is not None:
        if fid in entries: raise Unsupported("canonical functions use their accepted source")
        entries={fid:dict(source=str(candidate),proof_category="UNRESOLVED_CANDIDATE")}
    if fid not in entries: raise Unsupported("not in canonical functions/behavioral_functions ledger")
    if fid not in evs: raise Unsupported("no original execution fixture")
    entry,ev=entries[fid],evs[fid]
    if ev.get("extent_status")!="CLOSED_CFG" or ev.get("confidence")!="HIGH": raise Unsupported("extent is not a high-confidence closed CFG")
    if ev.get("undecoded_gaps"): raise Unsupported("function contains undecoded gaps")
    ex=entry.get("evidence_extent")
    if ex and (ex.get("hunk"),ex.get("start"),ex.get("end"))!=(ev.get("hunk"),ev.get("start"),ev.get("end")):
        raise Unsupported("canonical extent differs from execution fixture")
    if candidate is not None:
        path=Path(candidate).resolve();src=path.read_bytes().decode("latin-1")
    else:path,src=canonical_source(entry)
    sig=signature(src); calls,stubs=calls_of(ev)
    struct_layouts=data_model().get("structs",{})
    for param in sig["params"]:
        if param["kind"]=="pointer" and param["base"].startswith("struct "):
            tag=param["base"].split()[-1];spec=struct_layouts.get(tag,{})
            view=source_struct_layout(src,tag)
            if not isinstance(spec.get("size"),int) or not view or view["size"]!=spec["size"] or any(f["kind"]=="pointer" for f in view["fields"]):
                raise Unsupported("pointer parameter struct layout is not compatible with data_model: "+param["name"])
            param["struct_layout"]=view
    allg,used=globals_in(src,sig["body"])
    for n in used:
        g=allg[n]
        if g["type"]["kind"]=="struct" and not g.get("struct_model"):
            raise Unsupported("global "+n+" has no compatible typed data_model layout")
        if g["hunk"]!=1: raise Unsupported("global "+n+" is not in resident DATA hunk 1")
    call_offsets={item["offset"] for item in calls}
    for ref in ev.get("referenced_data",[]):
        if int(ref.get("instruction_offset",-1)) in call_offsets: continue
        if int(ref.get("hunk",-1))==int(ev.get("hunk",-2)) and ref.get("kind")=="PC_RELATIVE_DATA": continue
        if int(ref.get("hunk",-1))!=1: raise Unsupported("reference to non-resident DATA hunk")
        off=int(ref.get("offset",-1))
        if not any(g["offset"]<=off<g["offset"]+g["size"] for n,g in allg.items() if n in used):
            raise Unsupported(f"DATA reference at hunk1+{off:#x} has no typed extern view")
    usedg={n:allg[n] for n in used}
    ranges=sorted((g["offset"],g["offset"]+g["size"],n) for n,g in usedg.items())
    for left,right in zip(ranges,ranges[1:]):
        if left[1]>right[0]: raise Unsupported("overlapping global views are not modeled: "+left[2]+" / "+right[2])
    for n,g in usedg.items():
        if g["type"]["kind"]=="pointer" and g["count"]!=1: raise Unsupported("pointer-array host width differs: "+n)
    ct=callee_types(src,stubs)
    for x in stubs:
        if x["name"] not in ct: raise Unsupported("stubbed callee lacks return declaration: "+x["name"])
    return dict(id=fid,entry=entry,evidence=ev,source_path=path,source=src,signature=sig,
                globals=usedg,all_globals=allg,calls=calls,stubs=stubs,
                proof_category=entry["proof_category"],behavioral=entry["proof_category"]=="BEHAVIORAL_CHAR_RETURN")

def classify_function(fid):
    try: return dict(id=fid,eligible=True,plan=prepare(fid))
    except Unsupported as exc: return dict(id=fid,eligible=False,reason=str(exc))

def gcc_path():
    p=os.environ.get("DIFFTEST_GCC")
    if p and Path(p).is_file(): return str(Path(p))
    p=shutil.which("gcc")
    if p: return p
    p=Path(r"C:\msys64\mingw64\bin\gcc.exe")
    return str(p) if p.is_file() else None

def dependencies():
    missing=[]
    try:
        import unicorn  # noqa
        import unicorn.m68k_const  # noqa
    except Exception as exc: missing.append("unicorn unavailable: "+str(exc))
    gcc=gcc_path()
    if not gcc: missing.append("MSYS2 gcc not found")
    return dict(ok=not missing,reasons=missing,gcc=gcc)

def game_image():
    from hunk import parse as parse_hunks
    from ofs import OFSDisk
    found=[]
    for path in sorted((ROOT/"assets").glob("*.adf")):
        disk=OFSDisk(path.read_bytes()); disk.parse()
        found += [(path,n,b) for n,b in disk.files.items() if n.rsplit("/",1)[-1].lower()=="ducktales"]
    if len(found)!=1: raise Unsupported(f"expected one immutable DuckTales load file, found {len(found)}")
    path,name,exe=found[0]; model=parse_hunks(exe)
    h1=next((h for h in model["hunks"] if h["number"]==1 and h["type"]=="DATA"),None)
    h2=next((h for h in model["hunks"] if h["number"]==2 and h["type"]=="BSS"),None)
    if not h1 or not h2: raise Unsupported("missing resident DATA/BSS hunks")
    raw_segments={}
    for h in model["hunks"]:
        raw=bytearray(h["allocated_size"])
        if h["type"]!="BSS":
            pos=h["content_offset"]; raw[:h["initialized_size"]]=exe[pos:pos+h["initialized_size"]]
        raw_segments[h["number"]]=raw
    original_segments={n:bytes(raw) for n,raw in raw_segments.items()}
    bases={h["number"]:hunk_base(h["number"]) for h in model["hunks"]}
    for rel in model["relocations"]:
        if rel["type"]!="HUNK_RELOC32" or rel["width"]!=4:
            continue
        source=raw_segments[rel["source_hunk"]]
        value=(bases[rel["target_hunk"]]+rel["addend_raw"])&0xffffffff
        source[rel["source_offset"]:rel["source_offset"]+4]=value.to_bytes(4,"big")
    segments={}
    by_number={h["number"]:h for h in model["hunks"]}
    for number,raw in raw_segments.items():
        h=by_number[number]
        segments[number]=dict(number=number,node=h["node"],type=h["type"],base=bases[number],
                              allocated_size=h["allocated_size"],bytes=bytes(raw))
    data=segments[1]["bytes"]; bss=segments[2]["bytes"]
    evidence=json_read(ROOT/"evidence"/"functions"/"ledger.json")
    return dict(data=data,bss=bss,data_size=len(data),bss_size=len(bss),bias=int(evidence["a4"]["bias"]),
                model=model,segments=segments,raw_segments=original_segments)

_IMAGE=None
def image():
    global _IMAGE
    if _IMAGE is None: _IMAGE=game_image()
    return _IMAGE

_DATA_MODEL=None
def data_model():
    global _DATA_MODEL
    if _DATA_MODEL is None:
        path=ROOT/"recovery"/"data_model.json"
        _DATA_MODEL=json_read(path) if path.is_file() else {"globals":{},"structs":{}}
    return _DATA_MODEL

def page_size(n): return max(0x1000,(int(n)+0xfff)//0x1000*0x1000)

def hunk_base(number):
    number=int(number)
    if number==0:return CODE
    if number==1:return DATA
    if number==2:return BSS
    return 0xA00000+number*0x10000

def segment_for_address(im,address):
    for number,seg in im.get("segments",{}).items():
        if seg["base"]<=address<seg["base"]+seg["allocated_size"]:return int(number),address-seg["base"]
    return None

def c_spelling(t):
    base="int" if t["kind"]=="int" else t["base"]
    if t["unsigned"]: base="unsigned "+base
    return base+" *" if t["kind"]=="pointer" else base

def g_decl(g):
    return f"{c_spelling(g['type'])} {g['name']}"+(f"[{g['count']}]" if g["array"] else "")

def host_g_decl(g):
    if g.get("struct_model"):
        suffix=f"[{g['host_count']}]" if g["array"] or g["host_count"]>1 else ""
        return f"{c_spelling(g['type'])} {g['name']}{suffix}"
    return g_decl(g)

def be_expr(off,width):
    return " | ".join(f"((uint32_t)data[{off+i}] << {8*(width-1-i)})" for i in range(width))

def reloc_by_off(im):
    return {r["source_offset"]:r for r in im["model"]["relocations"] if r["source_hunk"]==1}

def pointer_expr_at(off,im,globals_used):
    rel=reloc_by_off(im).get(off)
    raw=int.from_bytes(im["data"][off:off+4],"big")
    if rel is None:
        if raw==0:return "(void *)0"
        raise Unsupported(f"nonzero pointer at DATA+{off:#x} lacks relocation evidence")
    if rel["target_hunk"]==2:return f"(void *)(difftest_bss+{rel['addend_raw']})"
    if rel["target_hunk"]!=1:raise Unsupported("pointer target is not resident DATA or BSS")
    target=int(rel["addend_raw"])
    obj=next((x for x in globals_used.values() if x["offset"]<=target<x["offset"]+x["size"]),None)
    if obj:return f"(void *)((unsigned char *)&{obj['name']}+{target-obj['offset']})"
    if target<im["data_size"]:return f"(void *)(difftest_data+{target})"
    raise Unsupported("pointer target outside resident DATA")

def pointer_expr(g,i,im,globals_used):
    return pointer_expr_at(g["offset"]+4*i,im,globals_used)

def make_host_source(plan,im,override=None):
    src=plan["source"] if override is None else override
    globs=plan["globals"]; ds,bs=im["data_size"],im["bss_size"]
    np=sum(p["kind"]=="pointer" for p in plan["signature"]["params"])
    # Address-anchor declarations in canonical C may say [1]; the measured
    # model extent supplies the allocation while preserving the source tag.
    for g in globs.values():
        if not g.get("struct_model") or g["host_count"]==g["decl_count"]:continue
        name=re.escape(g["name"])
        pat=re.compile(r"(\bextern\s+[^;]*?\b"+name+r"\s*\[)\s*\d+\s*(\])",re.S)
        src=pat.sub(lambda m:m.group(1)+str(g["host_count"])+m.group(2),src,count=1)
    lines=["#include <stdint.h>","#include <stddef.h>","#include <string.h>","#define int short",
           "typedef char check_32bit_long[(sizeof(long)==4)?1:-1];",
           f"static unsigned char difftest_data[{ds}];",f"static unsigned char difftest_bss[{max(1,bs)}];",
           f"static void *difftest_buffers[{max(1,np)}];","#pragma pack(push,2)",src,"#pragma pack(pop)"]
    for g in globs.values():lines.append(host_g_decl(g)+";")
    # Catch source aliases whose compiled layout differs from the independent
    # measured model before any trial can be called.
    for g in globs.values():
        if g.get("struct_model"):
            tag=g["type"]["base"].split()[-1]
            lines.append(f"typedef char difftest_check_{g['name']}[(sizeof(struct {tag})=={g['struct_size']}u)?1:-1];")
    lines += ["static uint32_t normptr(uintptr_t p) {","if(!p)return 0;",
           f"if(p>=(uintptr_t)difftest_data&&p<(uintptr_t)difftest_data+{ds}u)return 0x10000000u+(uint32_t)(p-(uintptr_t)difftest_data);",
           f"if(p>=(uintptr_t)difftest_bss&&p<(uintptr_t)difftest_bss+{bs}u)return 0x40000000u+(uint32_t)(p-(uintptr_t)difftest_bss);"]
    for g in globs.values():
        lines.append(f"if(p>=(uintptr_t)&{g['name']}&&p<(uintptr_t)&{g['name']}+{g['size']}u)return 0x10000000u+{g['offset']}u+(uint32_t)(p-(uintptr_t)&{g['name']});")
    for i in range(max(1,np)):
        lines.append(f"if(difftest_buffers[{i}]&&p>=(uintptr_t)difftest_buffers[{i}]&&p<(uintptr_t)difftest_buffers[{i}]+{SCRATCH_SIZE}u)return 0x20000000u+{i*SCRATCH_SIZE}u+(uint32_t)(p-(uintptr_t)difftest_buffers[{i}]);")
    lines += ["return 0xffffffffu;}","static uint32_t normptr32(uint32_t p){if(!p)return 0;",
           f"if(p>=(uint32_t)(uintptr_t)difftest_data&&p<(uint32_t)(uintptr_t)difftest_data+{ds}u)return 0x10000000u+(uint32_t)(p-(uint32_t)(uintptr_t)difftest_data);",
           f"if(p>=(uint32_t)(uintptr_t)difftest_bss&&p<(uint32_t)(uintptr_t)difftest_bss+{bs}u)return 0x40000000u+(uint32_t)(p-(uint32_t)(uintptr_t)difftest_bss);"]
    for g in globs.values():
        lines.append(f"if(p>=(uint32_t)(uintptr_t)&{g['name']}&&p<(uint32_t)(uintptr_t)&{g['name']}+{g['size']}u)return 0x10000000u+{g['offset']}u+(uint32_t)(p-(uint32_t)(uintptr_t)&{g['name']});")
    for i in range(max(1,np)):
        lines.append(f"if(difftest_buffers[{i}]&&p>=(uint32_t)(uintptr_t)difftest_buffers[{i}]&&p<(uint32_t)(uintptr_t)difftest_buffers[{i}]+{SCRATCH_SIZE}u)return 0x20000000u+{i*SCRATCH_SIZE}u+(uint32_t)(p-(uint32_t)(uintptr_t)difftest_buffers[{i}]);")
    lines += ["return 0xffffffffu;}","uint32_t difftest_norm_result(void*p){return normptr((uintptr_t)p);}"]
    st=callee_types(src,plan["stubs"]); emitted=set()
    for x in plan["stubs"]:
        if x["name"] in emitted:continue
        emitted.add(x["name"]); t=st[x["name"]]; r=c_spelling(t)
        body="return;" if t["kind"]=="void" else (f"return ({r})0;" if t["kind"]=="pointer" else ("return 0L;" if t["kind"]=="long" else "return 0;"))
        lines.append(f"{r} {x['name']}(){{{body}}}")
    reset=["void difftest_reset(const unsigned char*data,const unsigned char*bss){",f"memcpy(difftest_data,data,{ds}u);"]
    if bs:reset.append(f"memcpy(difftest_bss,bss,{bs}u);")
    for g in globs.values():
        if g.get("struct_model"):
            size=g["struct_size"]
            for i in range(g["model_count"]):
                off=g["offset"]+i*size; var=f"{g['name']}[{i}]" if g["array"] or g["host_count"]>1 else g["name"]
                reset.append(f"memcpy(&{var},data+{off},{size}u);")
                for field in g["struct_fields"]:
                    foff=off+field["offset"]
                    if field.get("pointer_value"):
                        expr=pointer_expr_at(foff,im,globs)
                        reset.append(f"{{uint32_t v=(uint32_t)(uintptr_t)({expr});memcpy((unsigned char*)&{var}+{field['offset']},&v,4u);}}")
                    elif field["kind"] in ("int","long"):
                        w=field["width"]; ctype_name="uint16_t" if w==2 else "uint32_t"
                        reset.append(f"{{{ctype_name} v=({ctype_name})({be_expr(foff,w)});memcpy((unsigned char*)&{var}+{field['offset']},&v,{w}u);}}")
            continue
        kind,w=g["type"]["kind"],g["width"]
        for i in range(g["count"]):
            off=g["offset"]+i*w; var=f"{g['name']}[{i}]" if g["array"] else g["name"]
            if g["pointer_valued"]:
                target=g.get("pointer_store_target")
                expr=f"(void *)&{target}" if target and target in globs else pointer_expr(g,i,im,globs)
                reset.append(f"{var}=({c_spelling(g['type'])})({expr});")
            elif kind=="char":reset.append(f"{var}=({c_spelling(g['type'])})data[{off}];")
            elif kind in ("int","long"):reset.append(f"{var}=({c_spelling(g['type'])})({be_expr(off,w)});")
    reset += ["}",f"void difftest_set_buffer(short i,void*p){{if((unsigned short)i<{max(1,np)}u)difftest_buffers[(unsigned short)i]=p;}}"]
    snap=["void difftest_snapshot(unsigned char*out){",f"memcpy(out,difftest_data,{ds}u);"]
    if bs:snap.append(f"memcpy(out+{ds}u,difftest_bss,{bs}u);")
    for g in globs.values():
        if g.get("struct_model"):
            size=g["struct_size"]
            snap.append(f"memcpy(out+{g['offset']},&{g['name']},{g['size']}u);")
            for i in range(g["model_count"]):
                off=g["offset"]+i*size; var=f"{g['name']}[{i}]" if g["array"] or g["host_count"]>1 else g["name"]
                for field in g["struct_fields"]:
                    if field["kind"] not in ("int","long") and not field.get("pointer_value"):continue
                    foff=off+field["offset"];w=field["width"]
                    ctype_name="uint16_t" if w==2 else "uint32_t"
                    norm="normptr32(v);" if field.get("pointer_value") else ""
                    shifts=range(w-1,-1,-1)
                    writes="".join(f"out[{foff+j}]=(unsigned char)(v>>{8*shift});" for j,shift in enumerate(shifts))
                    snap.append(f"{{{ctype_name} v;memcpy(&v,(unsigned char*)&{var}+{field['offset']},{w}u);{norm}{writes}}}")
            continue
        kind,w=g["type"]["kind"],g["width"]
        for i in range(g["count"]):
            off=g["offset"]+i*w;var=f"{g['name']}[{i}]" if g["array"] else g["name"]
            if g["pointer_valued"]:
                snap.append(f"{{uint32_t v=normptr32((uint32_t){var});out[{off}]=(unsigned char)(v>>24);out[{off+1}]=(unsigned char)(v>>16);out[{off+2}]=(unsigned char)(v>>8);out[{off+3}]=(unsigned char)v;}}")
            elif kind=="char":snap.append(f"out[{off}]=(unsigned char){var};")
            elif kind=="int":snap.append(f"{{uint16_t v=(uint16_t){var};out[{off}]=(unsigned char)(v>>8);out[{off+1}]=(unsigned char)v;}}")
            elif kind=="long":snap.append(f"{{uint32_t v=(uint32_t){var};out[{off}]=(unsigned char)(v>>24);out[{off+1}]=(unsigned char)(v>>16);out[{off+2}]=(unsigned char)(v>>8);out[{off+3}]=(unsigned char)v;}}")
            elif kind=="pointer":snap.append(f"{{uint32_t v=normptr((uintptr_t){var});out[{off}]=(unsigned char)(v>>24);out[{off+1}]=(unsigned char)(v>>16);out[{off+2}]=(unsigned char)(v>>8);out[{off+3}]=(unsigned char)v;}}")
    snap.append("}")
    return "\n".join(lines+reset+snap)+"\n"

def unicorn_api():
    try:
        from unicorn import (Uc,UC_ARCH_M68K,UC_HOOK_CODE,UC_HOOK_MEM_INVALID,UC_MODE_BIG_ENDIAN,
                             UC_MEM_READ_UNMAPPED,UC_MEM_WRITE_UNMAPPED,UC_MEM_FETCH_UNMAPPED)
        from unicorn.m68k_const import UC_CPU_M68K_M68000,UC_M68K_REG_A4,UC_M68K_REG_A7,UC_M68K_REG_D0,UC_M68K_REG_PC
        return locals()
    except Exception as exc: raise Unsupported("unicorn unavailable: "+str(exc))

def patch_code(plan,im):
    ev=plan["evidence"]; h=int(ev["hunk"]); start=int(ev["start"]); end=int(ev["end"])
    seg=im.get("segments",{}).get(h)
    if not seg: raise Unsupported("original CODE hunk is absent from executable")
    raw=im.get("raw_segments",{}).get(h,b"")[start:end]
    fixture=bytes.fromhex(ev["raw_bytes"])
    if raw!=fixture: raise Unsupported("raw execution fixture does not match immutable executable hunk bytes")
    if end>seg["allocated_size"]: raise Unsupported("function extent exceeds CODE hunk allocation")
    return dict(hunk=h,base=seg["base"],entry=seg["base"]+start,bytes=seg["bytes"],start=start,end=end)

def arg_ctype(p):
    if p["kind"]=="pointer": return ctypes.c_void_p
    if p["kind"]=="long": return ctypes.c_uint32 if p["unsigned"] else ctypes.c_int32
    if p["kind"]=="int": return ctypes.c_uint16 if p["unsigned"] else ctypes.c_int16
    if p["kind"]=="char": return ctypes.c_uint8 if p["unsigned"] else ctypes.c_int8
    raise Unsupported("unsupported argument type")
def ret_ctype(t):
    if t["kind"]=="void": return None
    if t["kind"]=="pointer": return ctypes.c_void_p
    if t["kind"]=="long": return ctypes.c_uint32 if t["unsigned"] else ctypes.c_int32
    if t["kind"]=="int": return ctypes.c_uint16 if t["unsigned"] else ctypes.c_int16
    if t["kind"]=="char": return ctypes.c_uint8 if t["unsigned"] else ctypes.c_int8
    raise Unsupported("unsupported return type")

def compile_host(plan,im,directory,override=None,gcc=None):
    gcc=gcc or gcc_path()
    if not gcc: raise Unsupported("MSYS2 gcc not found")
    cfile=directory/(plan["id"]+"_host.c"); dll=directory/(plan["id"]+"_host.dll")
    cfile.write_text(make_host_source(plan,im,override),encoding="latin-1")
    env=os.environ.copy(); env["PATH"]=env.get("PATH","")+os.pathsep+str(Path(gcc).resolve().parent)
    cmd=[gcc,"-std=gnu89","-O0","-fsigned-char","-shared","-Wl,--export-all-symbols","-o",str(dll),str(cfile)]
    proc=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True)
    if proc.returncode: raise Unsupported("host C compile failed: "+(proc.stderr or proc.stdout).strip()[-1800:])
    try:
        dll_dir=os.add_dll_directory(str(Path(gcc).resolve().parent)) if hasattr(os,"add_dll_directory") else None
        lib=ctypes.CDLL(str(dll)); fn=lib.recovered
        fn.argtypes=[arg_ctype(p) for p in plan["signature"]["params"]]; fn.restype=ret_ctype(plan["signature"]["return_type"])
        reset=lib.difftest_reset; reset.argtypes=[ctypes.POINTER(ctypes.c_ubyte),ctypes.POINTER(ctypes.c_ubyte)]
        setbuf=lib.difftest_set_buffer; setbuf.argtypes=[ctypes.c_int16,ctypes.c_void_p]
        snap=lib.difftest_snapshot; snap.argtypes=[ctypes.POINTER(ctypes.c_ubyte)]
        norm=lib.difftest_norm_result; norm.argtypes=[ctypes.c_void_p]; norm.restype=ctypes.c_uint32
    except Exception as exc: raise Unsupported("compiled DLL lacks harness ABI: "+str(exc))
    return dict(lib=lib,fn=fn,reset=reset,setbuf=setbuf,snap=snap,norm=norm,dll_dir=dll_dir)

def vectors(plan,count,seed):
    ps=plan["signature"]["params"]; out=[]; edges=[0,1,-1,2,-2,32767,-32768,0x7fffffff,-0x80000000]
    for v in (0,1,-1,2,-2,32767,-32768): out.append([v if p["kind"]!="pointer" else None for p in ps])
    for i,p in enumerate(ps):
        if p["kind"]=="pointer": continue
        for v in edges:
            row=[0 if q["kind"]!="pointer" else None for q in ps]; row[i]=v; out.append(row)
    rng=random.Random(seed)
    while len(out)<count:
        row=[]
        for p in ps:
            if p["kind"]=="pointer": row.append(None)
            elif p["kind"]=="long": row.append(rng.choice(edges) if rng.random()<.3 else rng.randint(-100000,100000))
            elif p["kind"]=="char": row.append(rng.choice([-128,-1,0,1,127]) if rng.random()<.5 else rng.randint(-128,127))
            elif p["unsigned"]: row.append(rng.choice([0,1,32767,32768,65535]) if rng.random()<.5 else rng.randint(0,65535))
            else: row.append(rng.choice([-32768,-1,0,1,32767]) if rng.random()<.5 else rng.randint(-32768,32767))
        out.append(row)
    return out[:count]

def normptr(value,im,ptrs):
    value &= 0xffffffff
    if not value:return 0
    if DATA<=value<DATA+im["data_size"]:return 0x10000000+value-DATA
    if BSS<=value<BSS+im["bss_size"]:return 0x40000000+value-BSS
    for i,p in enumerate(ptrs):
        if p<=value<p+SCRATCH_SIZE:return 0x20000000+i*SCRATCH_SIZE+value-p
    target=segment_for_address(im,value)
    if target:
        hunk,offset=target
        return (0x30000000+offset) if hunk==0 else (0x31000000+(hunk<<16)+offset)
    return 0xffffffff

def emu_memory(uc,plan,im,ptrs):
    data=bytearray(uc.mem_read(DATA,im["data_size"])); bss=bytearray(uc.mem_read(BSS,im["bss_size"]))
    for g in plan["globals"].values():
        fields=[]
        if g["pointer_valued"]:fields.extend(g["offset"]+i*4 for i in range(g["count"]))
        if g.get("struct_model"):
            fields.extend(g["offset"]+i*g["struct_size"]+off for i in range(g["model_count"]) for off in g.get("pointer_fields",[]))
        for off in fields:
            data[off:off+4]=normptr(int.from_bytes(data[off:off+4],"big"),im,ptrs).to_bytes(4,"big")
    return bytes(data+bss)

def run_original(plan,code,im,args,pointer_data,stub_sites):
    api=unicorn_api(); uc=api["Uc"](api["UC_ARCH_M68K"],api["UC_MODE_BIG_ENDIAN"]); uc.ctl_set_cpu_model(api["UC_CPU_M68K_M68000"])
    for seg in im["segments"].values(): uc.mem_map(seg["base"],page_size(seg["allocated_size"]))
    uc.mem_map(SCRATCH,page_size(max(1,len(pointer_data))*SCRATCH_SIZE))
    uc.mem_map(STACK-0x10000,0x10000); uc.mem_map(SENTINEL&~0xfff,0x1000)
    for seg in im["segments"].values():
        if seg["bytes"]: uc.mem_write(seg["base"],seg["bytes"])
    uc.mem_write(SENTINEL,b"\x4e\x71")
    ptrs=[]
    for i,b in enumerate(pointer_data):
        addr=SCRATCH+i*SCRATCH_SIZE; ptrs.append(addr); uc.mem_write(addr,b)
    frame=bytearray(); pi=0
    for p,v in zip(plan["signature"]["params"],args):
        if p["kind"]=="pointer":frame.extend(ptrs[pi].to_bytes(4,"big"));pi+=1
        elif p["kind"]=="long":frame.extend((int(v)&0xffffffff).to_bytes(4,"big"))
        else:frame.extend((int(v)&0xffff).to_bytes(2,"big"))
    sp=STACK-0x100; uc.mem_write(sp,SENTINEL.to_bytes(4,"big")+frame)
    uc.reg_write(api["UC_M68K_REG_A7"],sp); uc.reg_write(api["UC_M68K_REG_A4"],DATA+im["bias"]); uc.reg_write(api["UC_M68K_REG_PC"],code["entry"])
    hooks={code["base"]+site:size for site,size in stub_sites}
    instructions={code["base"]+int(item["offset"]):item for item in plan["evidence"].get("instructions",[])}
    state={"last_pc":None,"last_size":0,"fault":None}
    def on_code(machine,address,size,_):
        state["last_pc"]=int(address); state["last_size"]=int(size)
        if address in hooks:
            machine.reg_write(api["UC_M68K_REG_D0"],0); machine.reg_write(api["UC_M68K_REG_PC"],address+hooks[address])
    def on_invalid(machine,access,address,size,value,_):
        names={api["UC_MEM_READ_UNMAPPED"]:"READ_UNMAPPED",api["UC_MEM_WRITE_UNMAPPED"]:"WRITE_UNMAPPED",api["UC_MEM_FETCH_UNMAPPED"]:"FETCH_UNMAPPED"}
        pc=state["last_pc"]
        ins=instructions.get(pc,{}) if pc is not None else {}
        raw=""
        if pc is not None and state["last_size"]:
            try: raw=bytes(machine.mem_read(pc,state["last_size"])).hex()
            except Exception: pass
        state["fault"]={"cause":names.get(access,f"MEMORY_ACCESS_{access}"),"address":f"0x{int(address):08x}","size":int(size),
                         "instruction_pc":None if pc is None else f"0x{pc:08x}",
                         "instruction":(ins.get("mnemonic","")+((" "+ins.get("operands","")) if ins.get("operands") else "")) or None,
                         "instruction_bytes":raw or ins.get("raw")}
        return False
    uc.hook_add(api["UC_HOOK_CODE"],on_code)
    uc.hook_add(api["UC_HOOK_MEM_INVALID"],on_invalid)
    try:uc.emu_start(code["entry"],SENTINEL,count=INSTRUCTION_BUDGET)
    except Exception as exc:
        if state["fault"]:
            raise ExecutionFailure(state["fault"]["cause"],state["fault"])
        raise ExecutionFailure("Unicorn stopped: "+str(exc),{"cause":"UNICORN_ERROR","detail":str(exc)})
    if state["fault"]:raise ExecutionFailure(state["fault"]["cause"],state["fault"])
    pc=int(uc.reg_read(api["UC_M68K_REG_PC"]))
    if pc!=SENTINEL:
        last=state["last_pc"]; ins=instructions.get(last,{}) if last is not None else {}
        details={"cause":"INSTRUCTION_BUDGET","instruction_pc":None if last is None else f"0x{last:08x}",
                 "instruction":(ins.get("mnemonic","")+((" "+ins.get("operands","")) if ins.get("operands") else "")) or None,
                 "instruction_bytes":ins.get("raw")}
        raise ExecutionFailure("instruction budget exhausted before RTS",details)
    d0=int(uc.reg_read(api["UC_M68K_REG_D0"]))&0xffffffff
    return d0,emu_memory(uc,plan,im,ptrs),[bytes(uc.mem_read(p,SCRATCH_SIZE)) for p in ptrs],ptrs

def run_host(host,plan,im,args,pointer_data):
    db=(ctypes.c_ubyte*im["data_size"]).from_buffer_copy(im["data"]); br=im["bss"] or b"\0"
    bb=(ctypes.c_ubyte*max(1,im["bss_size"])).from_buffer_copy(br); host["reset"](db,bb)
    bufs=[]; cargs=[]; pi=0
    for p,v in zip(plan["signature"]["params"],args):
        if p["kind"]=="pointer":
            b=ctypes.create_string_buffer(pointer_data[pi],SCRATCH_SIZE); host["setbuf"](pi,ctypes.cast(b,ctypes.c_void_p))
            bufs.append(b); cargs.append(ctypes.cast(b,ctypes.c_void_p)); pi+=1
        else:cargs.append(int(v))
    result=host["fn"](*cargs)
    if plan["signature"]["return_type"]["kind"]=="pointer": result=("ptr",int(host["norm"](ctypes.c_void_p(result))))
    size=im["data_size"]+im["bss_size"]; out=(ctypes.c_ubyte*size)(); host["snap"](out)
    return result,bytes(out),[ctypes.string_at(ctypes.addressof(b),SCRATCH_SIZE) for b in bufs]

def results_for(d0,host_result,plan,im,ptrs):
    ret=plan["signature"]["return_type"]
    if plan["behavioral"]:return d0&255,int(host_result)&255
    if ret["kind"]=="void":return None,None
    # An implicit-int function with no valued return leaves D0 undefined; callers
    # cannot rely on it, so only memory and pointer effects are compared.
    if not re.search(r"(?<![A-Za-z0-9_])return\s*[^;\s]",strip_comments(plan["source"])):return None,None
    if ret["kind"]=="pointer":return normptr(d0,im,ptrs),host_result[1]
    mask=0xffffffff if ret["kind"]=="long" else 0xffff
    return d0&mask,int(host_result)&mask

def compare_pointer_buffer(param,original,host,buffer_index):
    base=param.get("base",""); width={"char":1,"int":2,"long":4}.get(base)
    spans=[]
    if param.get("struct_layout"):
        for field in param["struct_layout"]["fields"]:
            if field["kind"] in ("int","long"):spans.append((field["offset"],field["width"],field["kind"],field["name"]))
    elif param.get("kind")=="pointer" and width is not None:
        spans=[(off,width,base,"") for off in range(0,min(len(original),len(host)),width)]
    else:
        return ([dict(area="pointer_buffer",buffer=buffer_index,first_difference=next((i for i,(a,b) in enumerate(zip(original,host)) if a!=b),None),
                      original=original[:8].hex(),host=host[:8].hex())] if original!=host else []),[]
    mismatches=[];portability=[]
    if param.get("struct_layout"):
        element=param["struct_layout"]["size"]
        spans=[(baseoff+off,w,k,n) for baseoff in range(0,min(len(original),len(host)),element) for off,w,k,n in spans]
    for off,w,kind,name in spans:
        if off+w>min(len(original),len(host)):continue
        left=original[off:off+w];right=host[off:off+w]
        if left==right:continue
        ov=int.from_bytes(left,"big",signed=not param.get("unsigned",False))
        hv=int.from_bytes(right,"little",signed=not param.get("unsigned",False))
        if ov==hv:
            if not portability:
                portability.append(dict(area="pointer_buffer",buffer=buffer_index,type=kind,cause="host_endianness",
                    first_difference=off,field=name or None,original_bytes=left.hex(),host_bytes=right.hex(),logical_value=ov))
        else:
            mismatches.append(dict(area="pointer_buffer",buffer=buffer_index,first_difference=off,
                                   field=name or None,original_value=ov,host_value=hv,original=left.hex(),host=right.hex()))
            break
    return mismatches,portability

def compare_function(fid,trials=DEFAULT_TRIALS,*,source_override=None,seed=1,im=None,candidate=None):
    try:plan=prepare(fid,candidate)
    except Unsupported as exc:return dict(id=fid,status="unsupported",eligible=False,phase="classification",reason=str(exc),portability_findings=[])
    deps=dependencies()
    if not deps["ok"]:return dict(id=fid,status="unsupported",eligible=True,phase="dependencies",reason="; ".join(deps["reasons"]),portability_findings=[])
    try:
        im=im if im is not None else image()
        if ctypes.sizeof(ctypes.c_long)!=4:raise Unsupported("host C long is not 32 bits")
        for g in plan["globals"].values():
            if g["offset"]+g["size"]>im["data_size"]:raise Unsupported("global extends beyond resident DATA: "+g["name"])
        code=patch_code(plan,im); BUILD.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="difftest_",dir=str(BUILD.resolve()),ignore_cleanup_errors=True) as td:
            sizes={x["offset"]:x["size"] for x in plan["calls"]}
            stub_sites=[(x["site"],sizes.get(x["site"],0)) for x in plan["stubs"]]
            if any(not size for _,size in stub_sites):raise Unsupported("stubbed call has no decoded instruction size")
            host=compile_host(plan,im,Path(td),source_override,deps["gcc"])
            np=sum(p["kind"]=="pointer" for p in plan["signature"]["params"])
            pointer_data=[bytes(SCRATCH_SIZE) for _ in range(np)]
            mismatches=[]; portability=[]; attempted=0
            for trial,args in enumerate(vectors(plan,max(1,int(trials)),seed)):
                attempted+=1
                try:
                    od0,om,ob,ptrs=run_original(plan,code,im,args,pointer_data,stub_sites)
                    hr,hm,hb=run_host(host,plan,im,args,pointer_data)
                    ov,hv=results_for(od0,hr,plan,im,ptrs)
                    if ov!=hv:mismatches.append(dict(trial=trial,args=args,area="D0",original=ov,host=hv))
                    if om!=hm:
                        at=next((i for i,(a,b) in enumerate(zip(om,hm)) if a!=b),None)
                        mismatches.append(dict(trial=trial,args=args,area="resident_memory",first_difference=at,
                            original=om[at:at+8].hex() if at is not None else None,host=hm[at:at+8].hex() if at is not None else None))
                    param_index=0
                    for param in plan["signature"]["params"]:
                        if param["kind"]!="pointer": continue
                        a,b=ob[param_index],hb[param_index]
                        mm,pf=compare_pointer_buffer(param,a,b,param_index)
                        for item in mm:
                            item.update(trial=trial,args=args); mismatches.append(item)
                        for item in pf:
                            item.update(trial=trial,args=args)
                            if not any(x.get("area")==item.get("area") and x.get("buffer")==item.get("buffer") and x.get("cause")==item.get("cause") for x in portability):
                                portability.append(item)
                        param_index+=1
                    for g in plan["globals"].values():
                        if not g.get("pointer_valued"): continue
                        off=g["offset"]
                        value=int.from_bytes(om[off:off+4],"big")
                        if value and not any(x.get("global_name")==g["name"] for x in portability):
                            portability.append(dict(area="resident_memory",global_name=g["name"],cause="pointer_width_or_address_space",
                                target_identity=f"0x{value:08x}",detail="host and 68000 pointer representations are compared by target identity"))
                    for g in plan["globals"].values():
                        if not g.get("struct_model"):continue
                        for i in range(g["model_count"]):
                            for field_offset in g.get("pointer_fields",[]):
                                off=g["offset"]+i*g["struct_size"]+field_offset
                                value=int.from_bytes(om[off:off+4],"big")
                                if value and not any(x.get("global_name")==g["name"] and x.get("offset")==off for x in portability):
                                    portability.append(dict(area="resident_memory",global_name=g["name"],offset=off,
                                        cause="pointer_width_or_address_space",target_identity=f"0x{value:08x}",
                                        detail="host and 68000 pointer representations are compared by target identity"))
                    def note_endian(name,off,width,unsigned):
                        if width<=1 or om[off:off+width]!=hm[off:off+width]:return
                        initial=im["data"][off:off+width] if off+width<=im["data_size"] else b""
                        value_bytes=om[off:off+width]
                        if initial==value_bytes or value_bytes==value_bytes[::-1]:return
                        if not any(x.get("global_name")==name and x.get("cause")=="host_endianness" for x in portability):
                            portability.append(dict(area="resident_memory",global_name=name,offset=off,type=f"{width*8}-bit",
                                cause="host_endianness",original_bytes=value_bytes.hex(),host_native_bytes=value_bytes[::-1].hex(),
                                logical_value=int.from_bytes(value_bytes,"big",signed=not unsigned)))
                    for g in plan["globals"].values():
                        if g.get("pointer_valued"):continue
                        if g.get("struct_model"):
                            for i in range(g["model_count"]):
                                baseoff=g["offset"]+i*g["struct_size"]
                                for field in g["struct_fields"]:
                                    if field["kind"] in ("int","long") and not field.get("pointer_value"):
                                        note_endian(g["name"],baseoff+field["offset"],field["width"],field["base"].startswith("unsigned"))
                        elif g["type"]["kind"] in ("int","long"):
                            width=g.get("model_scalar_type",{}).get("width",g["width"])
                            for i in range(g["count"]):note_endian(g["name"],g["offset"]+i*g["width"],width,g["type"]["unsigned"])
                    if len(mismatches)>=5:break
                except ExecutionFailure as exc:
                    item=dict(trial=trial,args=args,area="execution",cause=exc.details.get("cause","EXECUTION_FAILURE"),reason=str(exc))
                    if exc.details.get("cause") in ("READ_UNMAPPED","WRITE_UNMAPPED","FETCH_UNMAPPED"):
                        item["first_unmapped"]=exc.details
                    else:item["instruction"]=exc.details
                    mismatches.append(item);break
                except OSError as exc:
                    mismatches.append(dict(trial=trial,args=args,area="host_fault",cause="HOST_FAULT",reason=str(exc)));break
            rt=plan["signature"]["return_type"]["kind"]
            result=dict(id=fid,status="mismatch" if mismatches else "agree",eligible=True,trials=attempted,
                proof_category=plan["proof_category"],return_comparison="D0.b" if plan["behavioral"] else ("omitted for void" if rt=="void" else "declared result width"),
                memory_bytes_compared=im["data_size"]+im["bss_size"],pointer_buffers=np,stubs=plan["stubs"],mismatches=mismatches,
                portability_findings=portability)
            import _ctypes
            _ctypes.FreeLibrary(host["lib"]._handle)
            host["lib"]._handle=0
            host.clear()
            return result
    except Unsupported as exc:return dict(id=fid,status="unsupported",eligible=True,phase="setup",reason=str(exc),portability_findings=[])

def summarize(results,n):
    vals=list(results.values()); causes={};
    for value in vals:
        if value.get("status")!="mismatch": continue
        function_causes=set()
        for item in value.get("mismatches",[]):
            cause=item.get("cause") or {"D0":"D0","resident_memory":"RESIDENT_MEMORY","pointer_buffer":"POINTER_BUFFER","host_fault":"HOST_FAULT"}.get(item.get("area"),"OTHER")
            function_causes.add(cause)
        for cause in function_causes: causes[cause]=causes.get(cause,0)+1
    return dict(canonical_functions=n,processed=len(vals),eligible=sum(bool(v.get("eligible")) for v in vals),
        drivable=sum(v.get("status") in ("agree","mismatch") for v in vals),
        agree=sum(v.get("status")=="agree" for v in vals),mismatch=sum(v.get("status")=="mismatch" for v in vals),
        mismatch_causes=dict(sorted(causes.items())),
        portability_findings=sum(len(v.get("portability_findings",[])) for v in vals),
        unsupported=sum(v.get("status")=="unsupported" for v in vals))

def write_results(new):
    BUILD.mkdir(parents=True,exist_ok=True); path=BUILD/"results.json"
    doc=json_read(path) if path.exists() else {"schema_version":1,"results":{}}
    results=doc.setdefault("results",{}); results.update(new); entries,_=catalog()
    out=dict(schema_version=1,results=dict(sorted(results.items())),summary=summarize(results,len(entries)))
    temp=path.with_suffix(".json.tmp"); temp.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"); temp.replace(path)
    return path,out["summary"]

def main(argv=None):
    parser=argparse.ArgumentParser(description="Compare original 68000 behavior with host-compiled canonical C")
    parser.add_argument("id",nargs="?"); parser.add_argument("--all",action="store_true"); parser.add_argument("--trials",type=int,default=DEFAULT_TRIALS)
    parser.add_argument("--timeout",type=int,default=120); parser.add_argument("--no-write",action="store_true")
    parser.add_argument("--candidate",help="check an unresolved function against this candidate source (evidence only)")
    args=parser.parse_args(argv)
    if args.trials<1:parser.error("--trials must be positive")
    if bool(args.id)==bool(args.all):parser.error("provide one ID or --all")
    entries,_=catalog(); selected=sorted(entries) if args.all else [args.id]; results={}
    for fid in selected:
        if args.all:
            # Native host code has no instruction budget: a loop that waits on
            # hardware state never ends on a PC. Isolate each function in a child
            # process with a wall-clock limit so one hang cannot stall the sweep.
            try:
                proc=subprocess.run([sys.executable,__file__,fid,"--trials",str(args.trials),"--no-write"],
                                    capture_output=True,text=True,timeout=args.timeout)
                line=next((l for l in reversed(proc.stdout.splitlines()) if l.startswith("{")),None)
                results[fid]=json.loads(line) if line else dict(id=fid,status="unsupported",eligible=True,
                    phase="child",reason=(proc.stderr or "no result")[-400:])
            except subprocess.TimeoutExpired:
                results[fid]=dict(id=fid,status="timeout",eligible=True,phase="execution",
                    reason="host or emulated run exceeded %ds (likely a loop waiting on hardware or I/O state)"%args.timeout)
        else:
            results[fid]=compare_function(fid,args.trials,candidate=args.candidate)
        print(json.dumps(results[fid],sort_keys=True),flush=True)
    if args.no_write:return 0
    path,counts=write_results(results)
    print(json.dumps(dict(results=path.relative_to(ROOT).as_posix(),summary=counts),sort_keys=True))
    return 0

if __name__=="__main__":raise SystemExit(main())
