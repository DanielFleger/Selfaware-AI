"""Create a literal Windows Shell link with known-folder aliasing disabled.

Uses Windows IShellLinkW/IShellLinkDataList/IPersistFile instead of WScript's
implicit package-relative AppData conversion. No console or UI interaction.
https://learn.microsoft.com/windows/win32/api/shlobj_core/nf-shlobj_core-ishelllinkdatalist-setflags
"""
import ctypes
from pathlib import Path, PureWindowsPath
import tempfile
import uuid

NO_TRACKING = 0x00040000 | 0x00200000 | 0x00400000 | 0x01000000


class GUID(ctypes.Structure):
    _fields_=[('bytes',ctypes.c_ubyte*16)]
    def __init__(self,value):super().__init__((ctypes.c_ubyte*16).from_buffer_copy(uuid.UUID(value).bytes_le))


def _method(pointer,index,*arguments):
    table=ctypes.cast(pointer,ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    return ctypes.WINFUNCTYPE(ctypes.c_long,ctypes.c_void_p,*arguments)(table[index])


def _check(result):
    if result<0:raise OSError('Windows shortcut failed: 0x%08X'%(result & 0xffffffff))


def absolute_link(target,arguments,working_directory,icon,description):
    target,working_directory,icon=map(str,(target,working_directory,icon))
    for value in (target,working_directory,icon):
        if not PureWindowsPath(value).is_absolute() or '\x00' in value:
            raise ValueError('Shortcut paths must be absolute Windows paths')
        if 'appdata\\local\\packages\\openai.codex_' in value.replace('/','\\').lower():
            raise ValueError('Refusing a Codex package-cache shortcut target')
    ole=ctypes.OleDLL('ole32')
    initialized=ole.CoInitializeEx(None,2)
    shell=ctypes.c_void_p();data=ctypes.c_void_p();persist=ctypes.c_void_p()
    try:
        cls=GUID('00021401-0000-0000-c000-000000000046')
        iid=GUID('000214f9-0000-0000-c000-000000000046')
        _check(ole.CoCreateInstance(ctypes.byref(cls),None,1,ctypes.byref(iid),ctypes.byref(shell)))
        data=ctypes.c_void_p();iid_data=GUID('45e2b4ae-b1c3-11d0-b92f-00a0c90312e1')
        _check(_method(shell,0,ctypes.POINTER(GUID),ctypes.POINTER(ctypes.c_void_p))(shell,ctypes.byref(iid_data),ctypes.byref(data)))
        _check(_method(data,7,ctypes.c_uint32)(data,NO_TRACKING))
        for index,value in ((20,target),(9,working_directory),(11,arguments),(7,description)):
            _check(_method(shell,index,ctypes.c_wchar_p)(shell,value))
        _check(_method(shell,17,ctypes.c_wchar_p,ctypes.c_int)(shell,icon,0))
        _check(_method(shell,15,ctypes.c_int)(shell,1))
        flags=ctypes.c_uint32()
        _check(_method(data,6,ctypes.POINTER(ctypes.c_uint32))(data,ctypes.byref(flags)))
        _check(_method(data,7,ctypes.c_uint32)(data,flags.value|NO_TRACKING))
        persist=ctypes.c_void_p();iid_file=GUID('0000010b-0000-0000-c000-000000000046')
        _check(_method(shell,0,ctypes.POINTER(GUID),ctypes.POINTER(ctypes.c_void_p))(shell,ctypes.byref(iid_file),ctypes.byref(persist)))
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'literal.lnk'
            _check(_method(persist,6,ctypes.c_wchar_p,ctypes.c_int)(persist,str(path),1))
            return path.read_bytes()
    finally:
        for pointer in (persist,data,shell):
            if pointer:_method(pointer,2)(pointer)
        if initialized in (0,1):ole.CoUninitialize()


def desktop_directory():
    buffer=ctypes.create_unicode_buffer(32768)
    result=ctypes.windll.shell32.SHGetFolderPathW(None,0x10,None,0,buffer)
    if result != 0:raise OSError('Windows desktop lookup failed: '+hex(result & 0xffffffff))
    return Path(buffer.value)
