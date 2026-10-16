from pathlib import Path
import ctypes as C, os, time
from ctypes import wintypes as W
k=C.WinDLL('kernel32',use_last_error=True)
k.CreateFileW.argtypes=[W.LPCWSTR,W.DWORD,W.DWORD,C.c_void_p,W.DWORD,W.DWORD,W.HANDLE];k.CreateFileW.restype=W.HANDLE
k.WriteFile.argtypes=[W.HANDLE,C.c_void_p,W.DWORD,C.POINTER(W.DWORD),C.c_void_p]
k.ReadFile.argtypes=[W.HANDLE,C.c_void_p,W.DWORD,C.POINTER(W.DWORD),C.c_void_p]
k.PeekNamedPipe.argtypes=[W.HANDLE,C.c_void_p,W.DWORD,C.POINTER(W.DWORD),C.POINTER(W.DWORD),C.POINTER(W.DWORD)]
k.CloseHandle.argtypes=[W.HANDLE]
k.GetNamedPipeServerProcessId.argtypes=[W.HANDLE,C.POINTER(W.ULONG)];k.GetNamedPipeServerProcessId.restype=W.BOOL
k.GetProcessId.argtypes=[W.HANDLE];k.GetProcessId.restype=W.DWORD
k.QueryFullProcessImageNameW.argtypes=[W.HANDLE,W.DWORD,W.LPWSTR,C.POINTER(W.DWORD)]
def open_pipe(name,pid):
    deadline=time.monotonic()+3
    while True:
        handle=k.CreateFileW('\\\\.\\pipe\\'+name,0xC0000000,0,None,3,0,None)
        if handle!=C.c_void_p(-1).value:break
        error=C.get_last_error()
        if error!=231 or time.monotonic()>deadline:raise OSError(error,'opening pipe')
        time.sleep(.03)
    server=W.ULONG()
    if not k.GetNamedPipeServerProcessId(handle,C.byref(server)) or server.value!=pid:
        k.CloseHandle(handle);raise RuntimeError(('pipe server PID mismatch',server.value,pid))
    return handle
def send(handle,command):
    raw=command.encode('ascii')+b'\0';written=W.DWORD()
    if not k.WriteFile(handle,raw,len(raw),C.byref(written),None):raise OSError(C.get_last_error(),'pipe write')
    available=W.DWORD();deadline=time.monotonic()+3
    while time.monotonic()<deadline:
        if not k.PeekNamedPipe(handle,None,0,None,C.byref(available),None):raise OSError(C.get_last_error(),'pipe poll')
        if available.value:break
        time.sleep(.01)
    if not available.value:return 'NO_RESPONSE'
    buf=C.create_string_buffer(max(available.value,65536));read=W.DWORD()
    if not k.ReadFile(handle,buf,len(buf),C.byref(read),None):raise OSError(C.get_last_error(),'pipe read')
    return buf.raw[:read.value].decode('utf-8',errors='replace').rstrip('\0')
