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

class Unsupported(Exception): pass
class ExecutionFailure(Exception): pass

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
        if ty["kind"]=="struct" or (ty["kind"]=="pointer" and (ty["stars"]!=1 or ty["base"]=="void" or ty["base"].startswith("struct "))):
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

def globals_in(source,body):
    allg={}
    for m in re.finditer(r"\bextern\s+([^;]+);",strip_comments(source)):
        decl=m[1].strip()
        nm=re.search(r"\b(G_h(?P<h>\d{2})_(?P<o>[0-9A-Fa-f]{4}))\b\s*(?P<a>\[\s*(?P<n>\d+)\s*\])?\s*$",decl)
        if not nm: continue
        name=nm[1]; ty=ctype(decl[:nm.start()])
        count=int(nm["n"]) if nm["n"] else 1
        width={"char":1,"int":2,"long":4,"pointer":4}.get(ty["kind"],0)
        allg[name]=dict(name=name,hunk=int(nm["h"]),offset=int(nm["o"],16),type=ty,count=count,
                        array=bool(nm["a"]),width=width,size=width*count)
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
    for ins in ev.get("instructions",[]):
        op=ins.get("mnemonic","").lower()
        if op.startswith(("bsr","jsr")): calls.append(ins)
        elif op.startswith("jmp"): raise Unsupported("tail/indirect JMP is unsupported")
    callees=ev.get("direct_callees",[])
    sites={x.get("site") for x in callees if x.get("site") is not None}
    offsets={x.get("offset") for x in calls}
    if offsets!=sites:
        missing=sorted(offsets-sites)
        if missing: raise Unsupported("unresolved/indirect call at "+hex(missing[0]))
        raise Unsupported("callee ledger has unmatched call site")
    stubs=[]
    for x in callees:
        if any(x.get(k) is None for k in ("site","hunk","offset")): raise Unsupported("callee lacks measured target")
        stubs.append(dict(site=int(x["site"]),id=x.get("id"),name=f"F_h{int(x['hunk']):02d}_{int(x['offset']):04X}",
                          policy="returns zero; no side effects"))
    return calls,stubs

def prepare(fid):
    entries,evs=catalog()
    if fid not in entries: raise Unsupported("not in canonical functions/behavioral_functions ledger")
    if fid not in evs: raise Unsupported("no original execution fixture")
    entry,ev=entries[fid],evs[fid]
    if ev.get("extent_status")!="CLOSED_CFG" or ev.get("confidence")!="HIGH": raise Unsupported("extent is not a high-confidence closed CFG")
    if ev.get("jump_tables"): raise Unsupported("jump-table control flow is unsupported")
    if ev.get("undecoded_gaps"): raise Unsupported("function contains undecoded gaps")
    ex=entry.get("evidence_extent")
    if ex and (ex.get("hunk"),ex.get("start"),ex.get("end"))!=(ev.get("hunk"),ev.get("start"),ev.get("end")):
        raise Unsupported("canonical extent differs from execution fixture")
    path,src=canonical_source(entry); sig=signature(src); calls,stubs=calls_of(ev)
    allg,used=globals_in(src,sig["body"])
    for n in used:
        g=allg[n]
        if g["type"]["kind"]=="struct": raise Unsupported("global "+n+" has an unmodeled struct layout")
        if g["hunk"]!=1: raise Unsupported("global "+n+" is not in resident DATA hunk 1")
    call_offsets={item["offset"] for item in calls}
    for ref in ev.get("referenced_data",[]):
        if int(ref.get("instruction_offset",-1)) in call_offsets: continue
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
    data=bytearray(h1["allocated_size"]); p=h1["content_offset"]
    data[:h1["initialized_size"]]=exe[p:p+h1["initialized_size"]]; bss=bytearray(h2["allocated_size"])
    bases={0:CODE,1:DATA,2:BSS}
    for h in model["hunks"]: bases.setdefault(h["number"],0xA00000+h["number"]*0x10000)
    for r in model["relocations"]:
        if r["source_hunk"]!=1: continue
        if r["type"]!="HUNK_RELOC32" or r["width"]!=4: raise Unsupported("unmodeled DATA relocation "+r["type"])
        data[r["source_offset"]:r["source_offset"]+4]=((bases[r["target_hunk"]]+r["addend_raw"])&0xffffffff).to_bytes(4,"big")
    evidence=json_read(ROOT/"evidence"/"functions"/"ledger.json")
    return dict(data=bytes(data),bss=bytes(bss),data_size=len(data),bss_size=len(bss),
                bias=int(evidence["a4"]["bias"]),model=model)

_IMAGE=None
def image():
    global _IMAGE
    if _IMAGE is None: _IMAGE=game_image()
    return _IMAGE

def c_spelling(t):
    base="int" if t["kind"]=="int" else t["base"]
    if t["unsigned"]: base="unsigned "+base
    return base+" *" if t["kind"]=="pointer" else base

def g_decl(g):
    return f"{c_spelling(g['type'])} {g['name']}"+(f"[{g['count']}]" if g["array"] else "")

def be_expr(off,width):
    return " | ".join(f"((uint32_t)data[{off+i}] << {8*(width-1-i)})" for i in range(width))

def reloc_by_off(im):
    return {r["source_offset"]:r for r in im["model"]["relocations"] if r["source_hunk"]==1}

def pointer_expr(g,i,im,globals_used):
    off=g["offset"]+4*i; rel=reloc_by_off(im).get(off)
    raw=int.from_bytes(im["data"][off:off+4],"big")
    if rel is None:
        if raw==0: return "(void *)0"
        raise Unsupported("nonzero pointer global lacks relocation evidence: "+g["name"])
    if rel["target_hunk"]==2: return f"(void *)(difftest_bss+{rel['addend_raw']})"
    if rel["target_hunk"]!=1: raise Unsupported("pointer global targets unmodeled hunk")
    target=int(rel["addend_raw"])
    obj=next((x for x in globals_used.values() if x["offset"]<=target<x["offset"]+x["size"] and x["type"]["kind"]!="pointer"),None)
    if obj: return f"(void *)((unsigned char *)&{obj['name']}+{target-obj['offset']})"
    if target<im["data_size"]: return f"(void *)(difftest_data+{target})"
    raise Unsupported("pointer target outside resident DATA")

def make_host_source(plan,im,override=None):
    src=plan["source"] if override is None else override
    globs=plan["globals"]; ds,bs=im["data_size"],im["bss_size"]
    np=sum(p["kind"]=="pointer" for p in plan["signature"]["params"])
    lines=["#include <stdint.h>","#include <stddef.h>","#include <string.h>","#define int short",
           "typedef char check_32bit_long[(sizeof(long)==4)?1:-1];",
           f"static unsigned char difftest_data[{ds}];",f"static unsigned char difftest_bss[{max(1,bs)}];",
           f"static void *difftest_buffers[{max(1,np)}];"]
    for g in globs.values(): lines.append("extern "+g_decl(g)+";")
    lines += ["static uint32_t normptr(uintptr_t p) {","if(!p)return 0;",
           f"if(p>=(uintptr_t)difftest_data&&p<(uintptr_t)difftest_data+{ds}u)return 0x10000000u+(uint32_t)(p-(uintptr_t)difftest_data);",
           f"if(p>=(uintptr_t)difftest_bss&&p<(uintptr_t)difftest_bss+{bs}u)return 0x40000000u+(uint32_t)(p-(uintptr_t)difftest_bss);"]
    for g in globs.values():
        lines.append(f"if(p>=(uintptr_t)&{g['name']}&&p<(uintptr_t)&{g['name']}+sizeof({g['name']}))return 0x10000000u+{g['offset']}u+(uint32_t)(p-(uintptr_t)&{g['name']});")
    for i in range(max(1,np)):
        lines.append(f"if(difftest_buffers[{i}]&&p>=(uintptr_t)difftest_buffers[{i}]&&p<(uintptr_t)difftest_buffers[{i}]+{SCRATCH_SIZE}u)return 0x20000000u+{i*SCRATCH_SIZE}u+(uint32_t)(p-(uintptr_t)difftest_buffers[{i}]);")
    lines+=["return 0xffffffffu;}","uint32_t difftest_norm_result(void*p){return normptr((uintptr_t)p);}"]
    for g in globs.values(): lines.append(g_decl(g)+";")
    st=callee_types(plan["source"],plan["stubs"]); emitted=set()
    for x in plan["stubs"]:
        if x["name"] in emitted: continue
        emitted.add(x["name"]); t=st[x["name"]]; r=c_spelling(t)
        body="return;" if t["kind"]=="void" else (f"return ({r})0;" if t["kind"]=="pointer" else ("return 0L;" if t["kind"]=="long" else "return 0;"))
        lines.append(f"{r} {x['name']}(){{{body}}}")
    reset=["void difftest_reset(const unsigned char*data,const unsigned char*bss){",f"memcpy(difftest_data,data,{ds}u);"]
    if bs: reset.append(f"memcpy(difftest_bss,bss,{bs}u);")
    for g in globs.values():
        kind,w=g["type"]["kind"],g["width"]
        for i in range(g["count"]):
            off=g["offset"]+i*w; var=f"{g['name']}[{i}]" if g["array"] else g["name"]
            if kind=="pointer": reset.append(f"{var}=({c_spelling(g['type'])})({pointer_expr(g,i,im,globs)});")
            elif kind=="char": reset.append(f"{var}=({c_spelling(g['type'])})data[{off}];")
            elif kind in ("int","long"): reset.append(f"{var}=({c_spelling(g['type'])})({be_expr(off,w)});")
    reset+=["}",f"void difftest_set_buffer(short i,void*p){{if((unsigned short)i<{max(1,np)}u)difftest_buffers[(unsigned short)i]=p;}}"]
    snap=["void difftest_snapshot(unsigned char*out){",f"memcpy(out,difftest_data,{ds}u);"]
    if bs: snap.append(f"memcpy(out+{ds}u,difftest_bss,{bs}u);")
    for g in globs.values():
        kind,w=g["type"]["kind"],g["width"]
        for i in range(g["count"]):
            off=g["offset"]+i*w; var=f"{g['name']}[{i}]" if g["array"] else g["name"]
            if kind=="char": snap.append(f"out[{off}]=(unsigned char){var};")
            elif kind=="int": snap.append(f"{{uint16_t v=(uint16_t){var};out[{off}]=(unsigned char)(v>>8);out[{off+1}]=(unsigned char)v;}}")
            elif kind=="long": snap.append(f"{{uint32_t v=(uint32_t){var};out[{off}]=(unsigned char)(v>>24);out[{off+1}]=(unsigned char)(v>>16);out[{off+2}]=(unsigned char)(v>>8);out[{off+3}]=(unsigned char)v;}}")
            elif kind=="pointer": snap.append(f"{{uint32_t v=normptr((uintptr_t){var});out[{off}]=(unsigned char)(v>>24);out[{off+1}]=(unsigned char)(v>>16);out[{off+2}]=(unsigned char)(v>>8);out[{off+3}]=(unsigned char)v;}}")
    snap.append("}")
    return "\n".join(lines+[src]+reset+snap)+"\n"

def unicorn_api():
    try:
        from unicorn import Uc,UC_ARCH_M68K,UC_HOOK_CODE,UC_MODE_BIG_ENDIAN
        from unicorn.m68k_const import UC_CPU_M68K_M68000,UC_M68K_REG_A4,UC_M68K_REG_A7,UC_M68K_REG_D0,UC_M68K_REG_PC
        return locals()
    except Exception as exc: raise Unsupported("unicorn unavailable: "+str(exc))

def patch_code(plan,im):
    raw=bytearray.fromhex(plan["evidence"]["raw_bytes"]); start=plan["evidence"]["start"]; h=plan["evidence"]["hunk"]

    for r in plan["evidence"].get("relocations",[]):
        off=r.get("relative_offset",int(r["source_offset"])-start); w=int(r.get("width",0))
        if off<0 or off+w>len(raw): continue
        if w!=4 or r.get("type")!="HUNK_RELOC32": raise Unsupported("function uses unmodeled relocation")
        target=int(r["target_hunk"]); addend=int(r["addend_raw"])
        if target==h:
            if not start<=addend<start+len(raw): raise Unsupported("relocation targets CODE outside the function fixture")
            value=CODE+addend-start
        elif target==1: value=DATA+addend
        elif target==2: value=BSS+addend
        else: raise Unsupported("relocation targets CODE or overlay data outside the function fixture")
        raw[off:off+4]=(value&0xffffffff).to_bytes(4,"big")
    return bytes(raw)

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
    if CODE<=value<CODE+0x10000 or RESIDENT_CODE<=value<RESIDENT_CODE+0x10000:return 0x30000000+value%0x10000
    return 0xffffffff

def emu_memory(uc,plan,im,ptrs):
    data=bytearray(uc.mem_read(DATA,im["data_size"])); bss=bytearray(uc.mem_read(BSS,im["bss_size"]))
    for g in plan["globals"].values():
        if g["type"]["kind"]=="pointer":
            for i in range(g["count"]):
                off=g["offset"]+i*4; data[off:off+4]=normptr(int.from_bytes(data[off:off+4],"big"),im,ptrs).to_bytes(4,"big")
    return bytes(data+bss)

def run_original(plan,code,im,args,pointer_data,stub_sites):
    api=unicorn_api(); uc=api["Uc"](api["UC_ARCH_M68K"],api["UC_MODE_BIG_ENDIAN"]); uc.ctl_set_cpu_model(api["UC_CPU_M68K_M68000"])
    uc.mem_map(CODE,0x10000); uc.mem_map(DATA,0x10000)
    if im["bss_size"]: uc.mem_map(BSS,max(0x1000,(im["bss_size"]+0xfff)//0x1000*0x1000))
    uc.mem_map(SCRATCH,max(0x1000,(len(pointer_data)*SCRATCH_SIZE+0xfff)//0x1000*0x1000))
    uc.mem_map(STACK-0x10000,0x10000); uc.mem_map(SENTINEL&~0xfff,0x1000)
    uc.mem_write(CODE,code); uc.mem_write(DATA,im["data"])
    if im["bss_size"]: uc.mem_write(BSS,im["bss"])
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
    uc.reg_write(api["UC_M68K_REG_A7"],sp); uc.reg_write(api["UC_M68K_REG_A4"],DATA+im["bias"]); uc.reg_write(api["UC_M68K_REG_PC"],CODE)
    hooks={CODE+site-plan["evidence"]["start"]:size for site,size in stub_sites}
    def on_code(machine,address,size,_):
        if address in hooks:
            machine.reg_write(api["UC_M68K_REG_D0"],0); machine.reg_write(api["UC_M68K_REG_PC"],address+hooks[address])
    if hooks:uc.hook_add(api["UC_HOOK_CODE"],on_code)
    try:uc.emu_start(CODE,SENTINEL,count=100000)
    except Exception as exc:raise ExecutionFailure("Unicorn stopped: "+str(exc))
    if uc.reg_read(api["UC_M68K_REG_PC"])!=SENTINEL:raise ExecutionFailure("instruction budget exhausted before RTS")
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

def compare_function(fid,trials=DEFAULT_TRIALS,*,source_override=None,seed=1,im=None):
    try:plan=prepare(fid)
    except Unsupported as exc:return dict(id=fid,status="unsupported",eligible=False,phase="classification",reason=str(exc))
    deps=dependencies()
    if not deps["ok"]:return dict(id=fid,status="unsupported",eligible=True,phase="dependencies",reason="; ".join(deps["reasons"]))
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
            mismatches=[]; attempted=0
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
                    for i,(a,b) in enumerate(zip(ob,hb)):
                        if a!=b:
                            at=next((j for j,(x,y) in enumerate(zip(a,b)) if x!=y),None)
                            mismatches.append(dict(trial=trial,args=args,area="pointer_buffer",buffer=i,first_difference=at,
                                original=a[at:at+8].hex() if at is not None else None,host=b[at:at+8].hex() if at is not None else None))
                    if len(mismatches)>=5:break
                except ExecutionFailure as exc:
                    mismatches.append(dict(trial=trial,args=args,area="execution",reason=str(exc)));break
                except OSError as exc:
                    # A host-side fault (e.g. an unrelocated pointer) is a harness or
                    # source-view finding for this function, never a crash of the run.
                    mismatches.append(dict(trial=trial,args=args,area="host_fault",reason=str(exc)));break
            rt=plan["signature"]["return_type"]["kind"]
            result=dict(id=fid,status="mismatch" if mismatches else "agree",eligible=True,trials=attempted,
                proof_category=plan["proof_category"],return_comparison="D0.b" if plan["behavioral"] else ("omitted for void" if rt=="void" else "declared result width"),
                memory_bytes_compared=im["data_size"]+im["bss_size"],pointer_buffers=np,stubs=plan["stubs"],mismatches=mismatches)
            import _ctypes
            _ctypes.FreeLibrary(host["lib"]._handle)
            host["lib"]._handle=0
            host.clear()
            return result
    except Unsupported as exc:return dict(id=fid,status="unsupported",eligible=True,phase="setup",reason=str(exc))

def summarize(results,n):
    vals=list(results.values())
    return dict(canonical_functions=n,processed=len(vals),eligible=sum(bool(v.get("eligible")) for v in vals),
        drivable=sum(v.get("status") in ("agree","mismatch") for v in vals),
        agree=sum(v.get("status")=="agree" for v in vals),mismatch=sum(v.get("status")=="mismatch" for v in vals),
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
    args=parser.parse_args(argv)
    if args.trials<1:parser.error("--trials must be positive")
    if bool(args.id)==bool(args.all):parser.error("provide one ID or --all")
    entries,_=catalog(); selected=sorted(entries) if args.all else [args.id]; results={}
    for fid in selected:
        results[fid]=compare_function(fid,args.trials)
        print(json.dumps(results[fid],sort_keys=True))
    path,counts=write_results(results)
    print(json.dumps(dict(results=path.relative_to(ROOT).as_posix(),summary=counts),sort_keys=True))
    return 0

if __name__=="__main__":raise SystemExit(main())
