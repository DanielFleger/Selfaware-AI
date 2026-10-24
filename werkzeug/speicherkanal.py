"""Volatile UCP bridge client. Opens existing mappings; never creates a peer.

The external application may persist results in Documents. The game module uses
only this pagefile-backed allocation and its own read-only UCP resources.
Callers serialize whole transactions and consume replies after materialization.
"""
import ctypes
from ctypes import wintypes
import struct
import time

MAGIC=0x53414942
VERSION=1
HEADER=4096
REQUEST_CAP=1024*1024
RESPONSE_CAP=32*1024*1024
RESPONSE=HEADER+REQUEST_CAP
SIZE=RESPONSE+RESPONSE_CAP
STATUS=64
STATUS_CAP=HEADER-STATUS


class Channel:
    def __init__(self,pid):
        self.pid=int(pid);self.handle=self.base=self.process=None
        self.k=ctypes.WinDLL('kernel32',use_last_error=True)
        self.k.OpenFileMappingW.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.LPCWSTR]
        self.k.OpenFileMappingW.restype=wintypes.HANDLE
        self.k.MapViewOfFile.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.DWORD,wintypes.DWORD,ctypes.c_size_t]
        self.k.MapViewOfFile.restype=ctypes.c_void_p
        self.k.UnmapViewOfFile.argtypes=[ctypes.c_void_p]
        self.k.CloseHandle.argtypes=[wintypes.HANDLE]
        self.k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        self.k.OpenProcess.restype=wintypes.HANDLE
        self.k.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
        try:
            self.process=self.k.OpenProcess(0x100000,False,self.pid)
            if not self.process:raise ctypes.WinError(ctypes.get_last_error())
            name='Local\\SelfawareBridge_%d_V%d'%(self.pid,VERSION)
            self.handle=self.k.OpenFileMappingW(0xF001F,False,name)
            if not self.handle:raise RuntimeError('Selfaware memory bridge not ready for process %d'%self.pid)
            self.base=self.k.MapViewOfFile(self.handle,0xF001F,0,0,SIZE)
            if not self.base:raise ctypes.WinError(ctypes.get_last_error())
            if self.read(0,16)!=struct.pack('<4I',MAGIC,VERSION,SIZE,self.pid):raise RuntimeError('Bridge identity/version/size mismatch')
            if not self.u32(40):raise RuntimeError('Memory bridge has not finished enabling')
        except BaseException:self.close();raise

    def read(self,offset,length):
        if offset<0 or length<0 or offset+length>SIZE:raise ValueError('Read outside shared allocation')
        return ctypes.string_at(self.base+offset,length)

    def write(self,offset,data):
        if offset<0 or offset+len(data)>SIZE:raise ValueError('Write outside shared allocation')
        ctypes.memmove(self.base+offset,data,len(data))

    def u32(self,offset):return struct.unpack('<I',self.read(offset,4))[0]
    def put(self,offset,value):self.write(offset,struct.pack('<I',value))
    def alive(self):return bool(self.process) and self.k.WaitForSingleObject(self.process,0)==0x102

    def status(self):
        for _ in range(10):
            sequence=self.u32(32)
            if sequence & 1:continue
            length=self.u32(36)
            if length>=STATUS_CAP:raise RuntimeError('Invalid bridge status length')
            data=self.read(STATUS,length)
            if self.u32(32)==sequence:return data
        raise RuntimeError('Bridge status is being updated')

    def transact(self,payload,timeout=3):
        if not isinstance(payload,bytes) or not 0<len(payload)<REQUEST_CAP:raise ValueError('Invalid request size')
        request,reply,consumed=self.u32(16),self.u32(20),self.u32(48)
        if request!=reply or reply!=consumed:
            raise RuntimeError('Previous bridge transaction is unresolved; do not overwrite or blindly retry')
        if not self.alive() or not self.u32(40):raise RuntimeError('Game process/bridge is no longer available')
        sequence=(request+1)&0xffffffff or 1
        self.write(HEADER,payload);self.put(24,len(payload))
        # Windows x86/x64 target: aligned store published last (TSO).
        self.put(16,sequence)
        deadline=time.monotonic()+timeout
        while self.u32(20)!=sequence:
            if not self.alive():raise RuntimeError('Game closed; pending command outcome unknown; do not retry')
            if not self.u32(40):raise RuntimeError('Bridge stopped; pending command outcome unknown; do not retry')
            if time.monotonic()>=deadline:raise TimeoutError('Memory command outcome unknown; do not retry')
            time.sleep(.001)
        length=self.u32(28)
        if length>=RESPONSE_CAP:raise RuntimeError('Invalid bridge reply length')
        return sequence,self.read(RESPONSE,length),self.u32(44)

    def consume(self,sequence):
        if self.u32(20)!=sequence:raise RuntimeError('Reply sequence changed before consumption')
        self.put(48,sequence)

    def close(self):
        if self.base:self.k.UnmapViewOfFile(self.base);self.base=None
        for attr in ('handle','process'):
            value=getattr(self,attr,None)
            if value:self.k.CloseHandle(value);setattr(self,attr,None)

    def __enter__(self):return self
    def __exit__(self,*args):self.close()


def records(payload):
    """Decode the complete reply before allowing any external filesystem writes."""
    result=[];offset=0
    while offset<len(payload):
        if len(payload)-offset<9:raise ValueError('Truncated bridge record')
        kind,key_length,data_length=struct.unpack_from('<BII',payload,offset);offset+=9
        if kind not in (1,2,3) or key_length>1024 or key_length+data_length>len(payload)-offset:
            raise ValueError('Invalid bridge record framing')
        key=payload[offset:offset+key_length].decode('utf-8');offset+=key_length
        data=payload[offset:offset+data_length];offset+=data_length
        if kind in (2,3):
            normalized=key.replace('\\','/')
            prefix='ucp/villagestudio/'
            if not normalized.startswith(prefix):raise ValueError('Unknown snapshot resource namespace')
            relative=normalized[len(prefix):]
            if not relative or '\0' in relative or any(p in ('','..','.') for p in relative.split('/')) or ':' in relative:
                raise ValueError('Invalid snapshot resource key')
            key=relative
        result.append((kind,key,data))
    return result
