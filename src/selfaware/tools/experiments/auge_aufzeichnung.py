# -*- coding: utf-8 -*-
"""B-142 Aufzeichnung fuer die Pruefung des Auges: schreibt Stand und Aenderungen des Spielspeichers mit, nur lesend.

Datei: Kennung, Kopf als JSON, dann Rahmen je Bereich und Takt. Der erste Rahmen eines Bereichs ist voll, danach nur
Aenderungen; springt der Takt zurueck (Spielstand geladen), wieder voll. Jeder Rahmen traegt eine Pruefsumme.
Aufruf (nur nach Daniels Ja, nur in einer freien Instanz):
  python -m selfaware.tools.experiments.auge_aufzeichnung --pid 1234 --ausgabe lauf_f.auge --takte 5000 --lauf F
"""
import argparse
import ctypes
import json
import os
import queue
import struct
import threading
import time
import zlib
from ctypes import wintypes
from dataclasses import dataclass

KENNUNG = b"AUGE1\n"
RAHMEN = struct.Struct("<BBHIIddII")  # Art, Bereich, Merker, Takt vorher, Takt nachher, Zeit, Dauer, Rohlaenge, Laenge
VOLL, AENDERUNG = 0, 1
REIN = 1
TAKT_ADRESSE = 0x0117CADC  # mapAndTime.totalGameTicksUnk
LUECKE_ZUSAMMEN = 16  # naeher liegende Aenderungen werden ein Abschnitt


@dataclass(frozen=True)
class Bereich:
    name: str
    adresse: int
    laenge: int
    alle: int = 1  # alle wieviel Takte gelesen wird


class ProzessQuelle:
    """Liest fremden Prozessspeicher, ohne Schreibrechte anzufordern. Instanz 5 ist Daniels Spiel und wird abgelehnt."""

    GESPERRT = ("instanz5", "instanz 5")

    def __init__(self, pid, erlaube_pfad=None):
        self._k = ctypes.WinDLL("kernel32", use_last_error=True)
        self._k.OpenProcess.restype = wintypes.HANDLE
        self._k.ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
        self._griff = self._k.OpenProcess(0x0010 | 0x1000, False, pid)  # VM_READ | QUERY_LIMITED_INFORMATION
        if not self._griff:
            raise OSError(f"Prozess {pid} nicht lesbar: {ctypes.get_last_error()}")
        self.pfad = self._bild()
        pruefe_instanz(self.pfad)

    def _bild(self):
        puffer = ctypes.create_unicode_buffer(1024)
        n = wintypes.DWORD(1024)
        self._k.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
        if not self._k.QueryFullProcessImageNameW(self._griff, 0, puffer, ctypes.byref(n)):
            raise OSError(f"Programmpfad nicht lesbar: {ctypes.get_last_error()}")
        return puffer.value

    def lies(self, adresse, laenge):
        puffer = ctypes.create_string_buffer(laenge)
        gelesen = ctypes.c_size_t(0)
        if not self._k.ReadProcessMemory(self._griff, ctypes.c_void_p(adresse), puffer, laenge, ctypes.byref(gelesen)) or gelesen.value != laenge:
            raise OSError(f"Lesen {adresse:#x}+{laenge} fehlgeschlagen: {ctypes.get_last_error()}")
        return puffer.raw


def prozesspfade():
    """Programmpfade aller lesbaren Prozesse."""
    return [p for _, p in _prozesse()]


def _prozesse():
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    k.OpenProcess.restype = wintypes.HANDLE
    ids = (wintypes.DWORD * 8192)()
    n = wintypes.DWORD(0)
    if not psapi.EnumProcesses(ids, ctypes.sizeof(ids), ctypes.byref(n)):
        raise OSError("EnumProcesses fehlgeschlagen")
    aus = []
    k.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    for pid in ids[:n.value // 4]:
        h = k.OpenProcess(0x1000, False, pid)
        if not h:
            continue
        puffer = ctypes.create_unicode_buffer(1024)
        m = wintypes.DWORD(1024)
        if k.QueryFullProcessImageNameW(h, 0, puffer, ctypes.byref(m)):
            aus.append((pid, puffer.value))
        k.CloseHandle(h)
    return aus


def pid_der_instanz(n, stamm=r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme"):
    """Prozess der Spielinstanz n, erkannt am Programmordner; None, wenn sie nicht laeuft."""
    ziel = (stamm if n == 1 else f"{stamm} Instanz{n}").lower()
    for pid, pfad in _prozesse():
        if pfad.lower().rsplit("\\", 1)[0] == ziel and pfad.lower().endswith(".exe"):
            return pid
    return None


def pruefe_instanz(pfad):
    if any(s in pfad.replace("\\", "/").lower() for s in ProzessQuelle.GESPERRT):
        raise PermissionError(f"Instanz 5 ist Daniels Spiel und bleibt unberuehrt: {pfad}")


def aenderungen(alt, neu):
    """Packt die Unterschiede zweier gleich langer Puffer: (Versatz, Laenge, Bytes)..."""
    import numpy as np

    a, b = np.frombuffer(alt, dtype=np.uint8), np.frombuffer(neu, dtype=np.uint8)
    stellen = np.flatnonzero(a != b)
    if not stellen.size:
        return b""
    schnitt = np.flatnonzero(np.diff(stellen) > LUECKE_ZUSAMMEN)
    anfang = np.concatenate(([stellen[0]], stellen[schnitt + 1]))
    ende = np.concatenate((stellen[schnitt], [stellen[-1]])) + 1
    teile = []
    for x, y in zip(anfang.tolist(), ende.tolist()):
        teile.append(struct.pack("<II", x, y - x))
        teile.append(bytes(neu[x:y]))
    return b"".join(teile)


class Aufzeichner:
    def __init__(self, quelle, bereiche, datei, kopf=None, takt_adresse=TAKT_ADRESSE, uhr=time.perf_counter, voll_bei=()):
        """voll_bei: Takte, in denen alle Bereiche gelesen werden, z. B. der Takt des Speicherns fuer Probe A5."""
        self.quelle, self.bereiche, self.takt_adresse, self.uhr = quelle, list(bereiche), takt_adresse, uhr
        self.voll_bei = set(voll_bei)
        self.letzter = None
        self._stand = {}
        self._zuletzt = {}
        self._fehler = None
        self._f = open(datei, "wb")
        k = dict(kopf or {})
        k["bereiche"] = [[b.name, b.adresse, b.laenge, b.alle] for b in self.bereiche]
        k["takt_adresse"] = self.takt_adresse
        roh = json.dumps(k, ensure_ascii=False).encode("utf-8")
        self._f.write(KENNUNG + struct.pack("<I", len(roh)) + roh)
        # Lesen und Packen getrennt: Vergleichen, Packen und Schreiben kosten mehr Zeit als ein Takt auf Tempo 40 hat (Lauf F
        # 02.11.2026: 7 Takte fehlten). Ist die Schlange voll, wartet nur das Lesen, nie das Spiel; dann fehlen Takte.
        self._schlange = queue.Queue(maxsize=128)
        self._packer = threading.Thread(target=self._packen, daemon=True)
        self._packer.start()

    def takt(self):
        return struct.unpack("<I", self.quelle.lies(self.takt_adresse, 4))[0]

    def schritt(self):
        """Schreibt die faelligen Bereiche, falls ein neuer Takt da ist. Rueckgabe: neuer Takt ja/nein."""
        t = self.takt()
        if t == self.letzter:
            return False
        zurueck = self.letzter is not None and t < self.letzter
        if zurueck:
            self._zuletzt.clear()
        self.letzter = t
        for i, b in enumerate(self.bereiche):
            if i in self._zuletzt and t - self._zuletzt[i] < b.alle and t not in self.voll_bei:
                continue
            start = self.uhr()
            vor = self.takt()
            roh = self.quelle.lies(b.adresse, b.laenge)
            nach = self.takt()
            dauer = self.uhr() - start
            self._zuletzt[i] = t
            self._schlange.put((i, zurueck, vor, nach, start, dauer, roh))
        if self._fehler:
            raise self._fehler
        return True

    def _packen(self):
        n = 0
        while True:
            auftrag = self._schlange.get()
            if auftrag is None:
                return
            try:
                i, voll, vor, nach, start, dauer, roh = auftrag
                alt = None if voll else self._stand.get(i)
                art, nutz = (VOLL, roh) if alt is None else (AENDERUNG, aenderungen(alt, roh))
                self._stand[i] = roh
                z = zlib.compress(nutz, 1)
                self._f.write(RAHMEN.pack(art, i, REIN if vor == nach else 0, vor, nach, start, dauer, len(nutz), len(z)))
                self._f.write(z)
                self._f.write(struct.pack("<I", zlib.crc32(z)))
                n += 1
                if n % 50 == 0:
                    self._f.flush()  # damit die Wache des Laufs mitlesen kann
            except Exception as e:  # noqa: BLE001  der Lesefaden meldet den Fehler weiter
                self._fehler = e
                return

    def lauf(self, takte=None, sekunden=None, pause=0.001, stop=None):
        """Bis die Takte voll sind, die Zeit um ist oder stop() wahr wird."""
        anfang, n = self.uhr(), 0
        while (takte is None or n < takte) and (sekunden is None or self.uhr() - anfang < sekunden) and not (stop and stop()):
            if self.schritt():
                n += 1
            else:
                time.sleep(pause)
        return n

    def schliessen(self):
        if self._packer.is_alive():
            self._schlange.put(None)
            self._packer.join()
        self._f.close()
        if self._fehler:
            raise self._fehler


def tempo_ohne_lesen(quelle, sekunden=10.0, takt_adresse=TAKT_ADRESSE):
    """Takte je Sekunde, wenn nur die Taktnummer gelesen wird (Vergleichswert fuer Probe A4)."""
    lies = lambda: struct.unpack("<I", quelle.lies(takt_adresse, 4))[0]
    a, t0 = lies(), time.perf_counter()
    while time.perf_counter() - t0 < sekunden:
        time.sleep(0.01)
    return (lies() - a) / (time.perf_counter() - t0)


def standard_bereiche(karte, datenblock_alle=250, karte_alle=25):
    """Hauptstrukturen jeden Takt, Kartenebenen seltener, der ganze Datenblock fuer den Aenderungsmelder noch seltener."""
    from selfaware.tools.analysis.auge_feldkarte import DATEN_ANFANG, DATEN_ENDE

    aus = []
    for name, alle in (("DAT_UnitsState", 1), ("DAT_EntityState", 1), ("DAT_BuildingsState", 1), ("DAT_TribesState", 1), ("DAT_GameState", 1),
                       ("SEC_RNG", 1), ("DAT_GameCore", 1), ("DAT_LandscapeState", 1), ("DAT_WildlifeState", 1), ("DAT_TroopValueState", 1),
                       ("DAT_AIVState", 25), ("DAT_MapPropertiesState", 25), ("DAT_PathFindingState", 25), ("DAT_TileMapState", karte_alle)):
        g = karte.struktur(name)
        aus.append(Bereich(name, g[0], g[1] - g[0], alle))
    adr, gr, schritt, anzahl = karte.adresse("DAT_GameSynchronyState", "DAT_GameCommandArray")
    aus.append(Bereich("befehle", adr, schritt * anzahl, 1))
    aus.append(Bereich("datenblock", DATEN_ANFANG, DATEN_ENDE + 1 - DATEN_ANFANG, datenblock_alle))
    return aus


def spielart_lesen(quelle, karte):
    aus = {}
    for name, g, p in (("currentGameMode", "DAT_GameSynchronyState", "currentGameMode"), ("gameMode_2", "DAT_GameCore", "gameMode_2")):
        adr, gr, _, _ = karte.adresse(g, p)
        aus[name] = struct.unpack("<i", quelle.lies(adr, 4))[0]
    return aus


def main(argv=None):
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pid", type=int)
    p.add_argument("--instanz", type=int, help="statt --pid: Nummer der Spielinstanz")
    p.add_argument("--stop-datei", help="die Aufzeichnung endet, sobald diese Datei da ist")
    p.add_argument("--ausgabe", required=True)
    p.add_argument("--lauf", default="-", help="F, K oder S")
    p.add_argument("--takte", type=int)
    p.add_argument("--sekunden", type=float)
    p.add_argument("--datenblock-alle", type=int, default=250)
    p.add_argument("--karte-alle", type=int, default=25)
    p.add_argument("--tempo-sekunden", type=float, default=10.0)
    p.add_argument("--voll-bei", type=int, nargs="*", default=[], help="Takte, in denen alle Bereiche gelesen werden (Takt des Speicherns)")
    a = p.parse_args(argv)
    pid = a.pid if a.pid else pid_der_instanz(a.instanz) if a.instanz else None
    if not pid:
        p.error("Prozess nicht gefunden (--pid oder --instanz)")
    quelle = ProzessQuelle(pid)
    karte = Feldkarte.laden(feldliste=FELDLISTE)
    kopf = {"lauf": a.lauf, "programm": quelle.pfad, "spielart": spielart_lesen(quelle, karte), "tempo_ohne_lesen": tempo_ohne_lesen(quelle, a.tempo_sekunden)}
    auf = Aufzeichner(quelle, standard_bereiche(karte, a.datenblock_alle, a.karte_alle), a.ausgabe, kopf, voll_bei=a.voll_bei)
    try:
        n = auf.lauf(takte=a.takte, sekunden=a.sekunden, stop=(lambda: os.path.exists(a.stop_datei)) if a.stop_datei else None)
    finally:
        auf.schliessen()
    print(f"{n} Takte aufgezeichnet: {a.ausgabe}")


if __name__ == "__main__":
    main()
