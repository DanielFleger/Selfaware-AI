# -*- coding: utf-8 -*-
"""B-161 Augen ohne Umweg: den Spielspeicher direkt lesen - NUR lesen (PROCESS_VM_READ), nie schreiben.
21.10.2026 gemessen an Instanz 5 (Takt 74.036, vor Franz' Burg): OpenProcess + ReadProcessMemory gehen ohne erhoehte Rechte;
Ansicht 0x01FE7D1C las 14 wie shc.zustand(); die ganze Wegkarte (3 Ebenen, 80.400 Felder) in 0,004 s - ueber den Befehlskanal
(logik.lua "wegkarte") waeren es 160.000 Lesebefehle im Spieltakt.
Welche Instanz: die aus befehl.SPIEL (SHC_INSTANZ). Die Prozessnummer kommt aus ucp-pid-<nr> im Spielordner und wird gegen
den Programmpfad des Prozesses geprueft - eine neu vergebene Nummer (anderer Prozess) wird nicht gelesen (Wissensstand 13q).
Kartenfelder (abgelesen 21.10.): translationMatrix 0x023372F8, je Zeile y 12 Byte (x_min, erstes Feld, addXgetTile); Zeile y
hat die Felder x = x_min .. 399 - x_min, Feldnummer = addXgetTile + x (wie logik.lua feld()); 80.400 Felder (Raute).
"""
import ctypes
import glob
import os
from ctypes import wintypes

import numpy as np

from befehl import SPIEL

ZEILEN = 0x023372F8         # translationMatrix
WEGLINKS = 0x01E1E4F8       # PathLinkageLayer, 1 Byte je Feld: erlaubte Schritte zum Nachbarn (Bits im Uhrzeigersinn ab N)
GEBIETE = 0x01DF70D8        # PathConnectionLayer, ushort je Feld: Gebiet (zusammenhaengend begehbar), 0 = keins
GEBAEUDE_EBENE = 0x01C95BB8  # BuildingLayer, ushort je Feld: Gebaeudenummer
HOEHE = 0x01D32C38          # HeightLayer, 1 Byte je Feld (logik.lua mauer: Mauerkachel = hoeher als der Boden)
BODEN = 0x01D46648          # Bodenhoehe, 1 Byte je Feld
LOGIK = 0x01BF8368          # LogicLayer, 4 Byte je Feld
BESITZ = 0x01D5A058         # Besitzer-Ebene, 1 Byte je Feld (Spieler - 1)
MAUERBITS = 0x100 | 0x200 | 0x800 | 0x10000 | 0x400000      # wie logik.lua (B-147, VillageStudio Wissensstand 5d)
GROESSE = 400

_k = ctypes.WinDLL("kernel32", use_last_error=True)
_k.OpenProcess.restype = wintypes.HANDLE
_k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
_k.ReadProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPCVOID, wintypes.LPVOID, ctypes.c_size_t,
                                 ctypes.POINTER(ctypes.c_size_t)]
_k.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
_k.CloseHandle.argtypes = [wintypes.HANDLE]
_griff = {"pid": None, "h": None}
_felder = {}


def _programm(pid):
    h = _k.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return None
    try:
        puf, n = ctypes.create_unicode_buffer(1024), wintypes.DWORD(1024)
        return puf.value if _k.QueryFullProcessImageNameW(h, 0, puf, ctypes.byref(n)) else None
    finally:
        _k.CloseHandle(h)


def griff():
    """Lesegriff auf den Spielprozess dieser Instanz; RuntimeError, wenn keiner laeuft oder die Nummer nicht passt."""
    explicit=os.environ.get('SHC_GAME_PID')
    pids = [int(explicit)] if explicit else sorted(int(os.path.basename(p).rsplit("-", 1)[-1]) for p in glob.glob(os.path.join(SPIEL, "ucp-pid-*")))
    if _griff["pid"] in pids and _griff["h"]:
        return _griff["h"]
    for pid in pids:
        pfad = _programm(pid)
        if pfad and os.path.normcase(os.path.dirname(pfad)) == os.path.normcase(SPIEL):
            h = _k.OpenProcess(0x0010, False, pid)  # PROCESS_VM_READ
            if h:
                if _griff["h"]:
                    _k.CloseHandle(_griff["h"])
                _griff.update(pid=pid, h=h)
                _felder.clear()
                return h
    raise RuntimeError("kein laufendes Spiel in %s (ucp-pid: %s)" % (SPIEL, pids or "keine"))


def lies(adr, n):
    puf, m = ctypes.create_string_buffer(n), ctypes.c_size_t()
    if not _k.ReadProcessMemory(griff(), adr, puf, n, ctypes.byref(m)) or m.value != n:
        _griff.update(pid=None, h=None)
        raise RuntimeError("Lesen 0x%08X (%d Byte) fehlgeschlagen, Fehler %d" % (adr, n, ctypes.get_last_error()))
    return puf.raw


def felder():
    """(xs, ys, ks): fuer jedes Kartenfeld x, y und Feldnummer - einmal je Prozess."""
    if not _felder:
        z = np.frombuffer(lies(ZEILEN, GROESSE * 12), dtype="<i4").reshape(GROESSE, 3)
        xs, ys, ks = [], [], []
        for y in range(GROESSE):
            x = np.arange(int(z[y, 0]), GROESSE - int(z[y, 0]))
            xs.append(x)
            ys.append(np.full(len(x), y))
            ks.append(z[y, 2] + x)
        _felder.update(xs=np.concatenate(xs), ys=np.concatenate(ys), ks=np.concatenate(ks))
    return _felder["xs"], _felder["ys"], _felder["ks"]


def ebene(adr, groesse=1, dtype=None):
    """Eine Kartenebene als Feld [x, y] (400 x 400, ausserhalb der Raute 0); groesse = Byte je Feld."""
    xs, ys, ks = felder()
    n = int(ks.max()) + 1
    roh = np.frombuffer(lies(adr, groesse * n), dtype=dtype or {1: np.uint8, 2: "<u2", 4: "<u4"}[groesse])
    aus = np.zeros((GROESSE, GROESSE), roh.dtype)
    aus[xs, ys] = roh[ks]
    return aus


def mauern(spieler):
    """bool [x, y]: Mauerkacheln von spieler (Mauerbit, Besitzer, hoeher als der Boden - wie logik.lua mauer) und die
    Hoehe ueber dem Boden je Feld (int [x, y])."""
    hoch = ebene(HOEHE).astype(np.int32) - ebene(BODEN).astype(np.int32)
    m = ((ebene(LOGIK, 4) & MAUERBITS) != 0) & (ebene(BESITZ) == spieler - 1) & (hoch > 0)
    return m, hoch


def wegkarte():
    """{"link", "gebiet", "gebaeude"} als Felder [x, y] (400 x 400, ausserhalb der Raute 0). gebiet ist 0, wo kein Schritt
    erlaubt ist (link 0) - so ist gebiet > 0 genau "begehbar, und zwar in diesem zusammenhaengenden Stueck"."""
    xs, ys, ks = felder()
    n = int(ks.max()) + 1
    link1 = np.frombuffer(lies(WEGLINKS, n), dtype=np.uint8)
    geb1 = np.frombuffer(lies(GEBIETE, 2 * n), dtype="<u2")
    bau1 = np.frombuffer(lies(GEBAEUDE_EBENE, 2 * n), dtype="<u2")
    aus = {"link": np.zeros((GROESSE, GROESSE), np.uint8), "gebiet": np.zeros((GROESSE, GROESSE), np.int32),
           "gebaeude": np.zeros((GROESSE, GROESSE), np.int32)}
    aus["link"][xs, ys] = link1[ks]
    aus["gebiet"][xs, ys] = np.where(link1[ks] > 0, geb1[ks], 0)
    aus["gebaeude"][xs, ys] = bau1[ks]
    aus["hoehe"] = ebene(HOEHE)
    aus["boden"] = ebene(BODEN)
    return aus
