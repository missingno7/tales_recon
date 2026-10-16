"""Win32 structures for the private WinUAE debugger console transport."""
import ctypes as C
from ctypes import wintypes as W
import trace_probe_ipc as I
k=I.k
class COORD(C.Structure): _fields_=[("X",C.c_short),("Y",C.c_short)]
class RECT(C.Structure): _fields_=[("Left",C.c_short),("Top",C.c_short),("Right",C.c_short),("Bottom",C.c_short)]
class INFO(C.Structure): _fields_=[("size",COORD),("cursor",COORD),("attr",W.WORD),("rect",RECT),("maxsize",COORD)]
class KEY(C.Structure): _fields_=[("down",W.BOOL),("repeat",W.WORD),("vk",W.WORD),("scan",W.WORD),("char",W.WCHAR),("ctrl",W.DWORD)]
class UNION(C.Union): _fields_=[("key",KEY),("pad",C.c_byte*16)]
class RECORD(C.Structure): _fields_=[("type",W.WORD),("event",UNION)]
