# -*- coding: utf-8 -*-
"""B-142: Eine Funktion des laufenden Spiels direkt aufrufen und den Rueckgabewert lesen. Nur fuer Messlaeufe auf Instanz 2.

Warum: Viele Pruefungen des Spiels gehoeren zur Oberflaeche (Bauplatz, Reparaturkosten, Punkte, Mauerzahl). Sie laufen nur, wenn ein
Mensch klickt, und ihr Ergebnis steht in keinem Feld. Statt Klicks nachzustellen, ruft ein eigener kurzer Ablauf im Spiel die Funktion
mit festen Eingaben auf, im angehaltenen Spiel. Das geht in Bruchteilen einer Sekunde und zeigt genau diese eine Regel.

Grenze: SamurAI darf das nie benutzen (Fairness). Es verlaesst den Messlauf nicht, und Instanz 5 lehnt das Werkzeug ab.
"""

import ctypes
import ctypes.wintypes as w
import struct

ERLAUBT = "Instanz2"
RECHTE = (
    0x0002 | 0x0008 | 0x0010 | 0x0020 | 0x0400
)  # CREATE_THREAD, VM_OPERATION, VM_READ, VM_WRITE, QUERY_INFORMATION
MEM_NEU, MEM_WEG, AUSFUEHRBAR = 0x3000, 0x8000, 0x40
GRENZE_MS = 5000

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = w.HANDLE
k32.OpenProcess.argtypes = (w.DWORD, w.BOOL, w.DWORD)
k32.VirtualAllocEx.restype = ctypes.c_void_p
k32.VirtualAllocEx.argtypes = (w.HANDLE, ctypes.c_void_p, ctypes.c_size_t, w.DWORD, w.DWORD)
k32.VirtualFreeEx.argtypes = (w.HANDLE, ctypes.c_void_p, ctypes.c_size_t, w.DWORD)
k32.WriteProcessMemory.argtypes = (
    w.HANDLE,
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
)
k32.ReadProcessMemory.argtypes = (
    w.HANDLE,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
)
k32.CreateRemoteThread.restype = w.HANDLE
k32.CreateRemoteThread.argtypes = (
    w.HANDLE,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_void_p,
    ctypes.c_void_p,
    w.DWORD,
    ctypes.c_void_p,
)
k32.WaitForSingleObject.argtypes = (w.HANDLE, w.DWORD)
k32.GetExitCodeThread.argtypes = (w.HANDLE, ctypes.POINTER(w.DWORD))
k32.CloseHandle.argtypes = (w.HANDLE,)
k32.QueryFullProcessImageNameW.argtypes = (w.HANDLE, w.DWORD, w.LPWSTR, ctypes.POINTER(w.DWORD))


def ablauf(ziel, werte, this, ergebnis):
    """Maschinencode (32 Bit): Stapel merken, Werte schieben, this nach ECX, aufrufen, EAX ablegen, Stapel zurueck. So ist egal, wer die Werte vom Stapel raeumt."""
    b = bytearray(b"\x55\x89\xe5")  # push ebp; mov ebp, esp
    for v in reversed(werte):
        b += b"\x68" + struct.pack("<I", v & 0xFFFFFFFF)  # push wert
    if this is not None:
        b += b"\xb9" + struct.pack("<I", this)  # mov ecx, this
    b += b"\xb8" + struct.pack("<I", ziel)  # mov eax, ziel
    b += b"\xff\xd0"  # call eax
    b += b"\xa3" + struct.pack("<I", ergebnis)  # mov [ergebnis], eax
    b += b"\x89\xec\x5d\x31\xc0\xc2\x04\x00"  # mov esp, ebp; pop ebp; xor eax, eax; ret 4
    return bytes(b)


class Rufer:
    def __init__(self, pid):
        self.h = k32.OpenProcess(RECHTE, False, pid)
        if not self.h:
            raise OSError(f"Prozess {pid} nicht zu oeffnen: {ctypes.get_last_error()}")
        puffer, n = ctypes.create_unicode_buffer(600), w.DWORD(600)
        if not k32.QueryFullProcessImageNameW(self.h, 0, puffer, ctypes.byref(n)):
            raise OSError("Pfad des Prozesses nicht lesbar")
        if ERLAUBT not in puffer.value:
            k32.CloseHandle(self.h)
            raise PermissionError(f"Nur {ERLAUBT}, nicht {puffer.value}")
        self.speicher = k32.VirtualAllocEx(self.h, None, 0x1000, MEM_NEU, AUSFUEHRBAR)
        if not self.speicher:
            raise OSError(f"Kein Speicher im Spiel: {ctypes.get_last_error()}")

    def schreibe(self, adr, daten):
        if not k32.WriteProcessMemory(self.h, adr, daten, len(daten), None):
            raise OSError(f"Schreiben {adr:#x}: {ctypes.get_last_error()}")

    def lies(self, adr, n=4):
        p = ctypes.create_string_buffer(n)
        if not k32.ReadProcessMemory(self.h, adr, p, n, None):
            raise OSError(f"Lesen {adr:#x}: {ctypes.get_last_error()}")
        return p.raw

    def lies_i(self, adr, n=4):
        return int.from_bytes(self.lies(adr, n), "little", signed=True)

    def setze_i(self, adr, wert, n=4):
        self.schreibe(adr, int(wert).to_bytes(n, "little", signed=True))

    def rufe(self, ziel, *werte, this=None):
        erg = self.speicher + 0x800
        self.schreibe(erg, b"\xef\xbe\xad\xde")
        self.schreibe(self.speicher, ablauf(ziel, werte, this, erg))
        t = k32.CreateRemoteThread(self.h, None, 0, self.speicher, None, 0, None)
        if not t:
            raise OSError(f"Aufruf nicht moeglich: {ctypes.get_last_error()}")
        try:
            if k32.WaitForSingleObject(t, GRENZE_MS) != 0:
                raise TimeoutError(f"Funktion {ziel:#x} kam nicht zurueck")
        finally:
            k32.CloseHandle(t)
        return self.lies_i(erg)

    def schliessen(self):
        if self.h:
            k32.VirtualFreeEx(self.h, self.speicher, 0, MEM_WEG)
            k32.CloseHandle(self.h)
            self.h = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.schliessen()
