"""Read only startup postconditions from a specified Crusader process."""
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import struct
import sys


def probe(pid):
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.restype=wintypes.HANDLE
    k.ReadProcessMemory.argtypes=[wintypes.HANDLE,wintypes.LPCVOID,wintypes.LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
    k.QueryFullProcessImageNameW.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)]
    k.CloseHandle.argtypes=[wintypes.HANDLE]
    h=k.OpenProcess(0x1010,False,pid)
    if not h:raise ctypes.WinError(ctypes.get_last_error())
    try:
        buf=ctypes.create_unicode_buffer(32768);n=wintypes.DWORD(len(buf))
        if not k.QueryFullProcessImageNameW(h,0,buf,ctypes.byref(n)):raise ctypes.WinError(ctypes.get_last_error())
        if Path(buf.value).name.lower()!='stronghold crusader.exe':raise ValueError('Unexpected program')
        result={'pid':pid,'program':buf.value}
        for key,addr in [('ansicht',0x01FE7D1C),('tick',0x0117CADC),('gameover',0x0117D500)]:
            data=ctypes.create_string_buffer(4);read=ctypes.c_size_t()
            if not k.ReadProcessMemory(h,addr,data,4,ctypes.byref(read)) or read.value!=4:raise ctypes.WinError(ctypes.get_last_error())
            result[key]=struct.unpack('<i',data.raw)[0]
        return result
    finally:k.CloseHandle(h)


if __name__=='__main__':
    try:result=probe(int(sys.argv[1]))
    except Exception as ex:result={'error':str(ex)}
    Path(sys.argv[2]).write_text(json.dumps(result,indent=2),encoding='utf-8')
