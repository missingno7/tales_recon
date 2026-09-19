"""Shared read-only host analysis support; no emulator is needed."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HOST_SITE=ROOT/'toolchain/installed/host-python/Lib/site-packages'
if str(HOST_SITE) not in sys.path:
    sys.path.insert(0,str(HOST_SITE))
import capstone
from capstone import m68k_const as K
from common import require,sha256
from census import verify_lock,derive

def decoder():
    md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
    md.detail=True
    return md

def game():
    verify_lock(ROOT)
    outputs,files,model=derive(ROOT)
    return files['DT1:DuckTales'],model,outputs

def instruction(md,data,offset):
    ins=next(md.disasm(data[offset:offset+24],offset,count=1),None)
    if ins is None or ins.mnemonic.startswith('dc.') or not ins.size or offset+ins.size>len(data):
        return None
    return ins

def signed16(n):
    return n-65536 if n&32768 else n

def basic(ins):
    return dict(offset=ins.address,size=ins.size,raw=bytes(ins.bytes).hex(),mnemonic=ins.mnemonic,operands=ins.op_str)
