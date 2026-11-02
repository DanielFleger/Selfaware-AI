# -*- coding: utf-8 -*-
"""B-142 Aufzeichnung fuer die Pruefung des Auges: schreibt Stand und Aenderungen des Spielspeichers mit, nur lesend.

Datei: Kennung, Kopf als JSON, dann Rahmen je Bereich und Takt. Der erste Rahmen eines Bereichs ist voll, danach nur
Aenderungen; springt der Takt zurueck (Spielstand geladen), wieder voll. Jeder Rahmen traegt eine Pruefsumme.
Gezaehlt wird in Takten (Daniel 02.11.2026). Echte Zeit nur dort, wo sie die Messgroesse ist: Lesedauer und Takte je Sekunde.
Aufruf (nur nach Daniels Ja, nur in einer freien Instanz):
  python -m selfaware.tools.experiments.auge_aufzeichnung --pid 1234 --ausgabe lauf_f.auge --takte 5000 --lauf F
"""
import argparse
import ctypes
import json
import os
import queue
import struct
import sys
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


def aenderungen(alt, neu, merke=None):
    """Packt die Unterschiede zweier gleich langer Puffer: (Versatz, Laenge, Bytes)... merke bekommt die geaenderten Stellen."""
    import numpy as np

    a, b = np.frombuffer(alt, dtype=np.uint8), np.frombuffer(neu, dtype=np.uint8)
    stellen = np.flatnonzero(a != b)
    if not stellen.size:
        return b""
    if merke is not None:
        merke(stellen)
    schnitt = np.flatnonzero(np.diff(stellen) > LUECKE_ZUSAMMEN)
    anfang = np.concatenate(([stellen[0]], stellen[schnitt + 1]))
    ende = np.concatenate((stellen[schnitt], [stellen[-1]])) + 1
    teile = []
    for x, y in zip(anfang.tolist(), ende.tolist()):
        teile.append(struct.pack("<II", x, y - x))
        teile.append(bytes(neu[x:y]))
    return b"".join(teile)


class Streng(RuntimeError):
    """Im strengen Modus (Tempo 40, jeder Takt) beendet ein fehlender Takt oder ein gemischter Schnappschuss die Aufzeichnung."""


class FeldWache:
    """Merkt sich, welche Felder der Feldliste sich schon geaendert haben, und schreibt alle n Takte den Stand in eine Datei.
    Daran erkennt der Lauf sein gemessenes Ende: ein Jahr lang kein neues Feld."""

    def __init__(self, karte, bereiche, datei, alle=800):
        self.karte, self.datei, self.alle = karte, datei, alle
        self.basis = [b.adresse for b in bereiche]
        self.masken, self.gesehen, self.schon = {}, set(), set()
        self.letzter_neuer = self.naechster = None

    def merke(self, i, stellen, laenge):
        import numpy as np

        m = self.masken.get(i)
        if m is None:
            m = self.masken[i] = np.zeros(laenge, dtype=bool)
        m[stellen] = True

    def pruefe(self, takt):
        import numpy as np

        if self.naechster is None:
            self.naechster = takt + self.alle
        if takt < self.naechster:
            return
        self.naechster = takt + self.alle
        neu = 0
        for i, m in self.masken.items():
            stellen = np.flatnonzero(m)
            if not stellen.size:
                continue
            m.fill(False)
            schnitt = np.flatnonzero(np.diff(stellen) > 1)
            anfang = np.concatenate(([stellen[0]], stellen[schnitt + 1])).tolist()
            ende = (np.concatenate((stellen[schnitt], [stellen[-1]])) + 1).tolist()
            for x, y in zip(anfang, ende):
                k = (i, x, y)
                if k in self.schon:
                    continue
                self.schon.add(k)
                for f in self.karte.felder_einer_aenderung(self.basis[i] + x, y - x):
                    if f not in self.gesehen and self.karte.bekannt(*f):
                        self.gesehen.add(f)
                        neu += 1
        if neu or self.letzter_neuer is None:
            self.letzter_neuer = takt
        self.schreibe(takt, neu)

    def schreibe(self, takt, neu=0):
        roh = json.dumps({"takt": takt, "felder": len(self.gesehen), "neu": neu, "letzter_neuer_takt": self.letzter_neuer})
        try:
            with open(self.datei + ".neu", "w", encoding="utf-8") as f:
                f.write(roh)
            os.replace(self.datei + ".neu", self.datei)
        except OSError:
            pass  # der Lauf liest gerade mit; der naechste Stand kommt in n Takten


class Aufzeichner:
    def __init__(self, quelle, bereiche, datei, kopf=None, takt_adresse=TAKT_ADRESSE, uhr=time.perf_counter, voll_bei=(), streng=False, felder=None):
        """voll_bei: Takte, in denen alle Bereiche gelesen werden, z. B. der Takt des Speicherns fuer Probe A5.
        streng: jeder Takt muss ankommen, sonst Streng. felder: FeldWache, sie laeuft im Packfaden."""
        self.quelle, self.bereiche, self.takt_adresse, self.uhr = quelle, list(bereiche), takt_adresse, uhr
        self.voll_bei = set(voll_bei)
        self.streng, self.felder = streng, felder
        self.fehlend = self.gemischt = self.gemischt_selten = self.schlange_voll = 0
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
        elif self.letzter is not None and t > self.letzter + 1:
            self.fehlend += t - self.letzter - 1
            if self.streng:
                raise Streng(f"Takt {self.letzter + 1} bis {t - 1} fehlt")
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
            if vor != nach:
                # nur Bereiche, die jeden Takt gelesen werden, muessen rein sein: Selten gelesene dienen dem Aenderungsmelder
                # (Lauf F 02.11.2026: der einzige gemischte Rahmen auf Tempo 40 war der Datenblock, 8,2 ms Lesezeit)
                if b.alle == 1:
                    self.gemischt += 1
                    if self.streng:
                        raise Streng(f"Bereich {b.name} ist gemischt: Takt {vor} bis {nach}")
                else:
                    self.gemischt_selten += 1
            self._einreihen((i, zurueck, vor, nach, start, dauer, roh))
        if self._fehler:
            raise self._fehler
        return True

    def _einreihen(self, auftrag):
        if self._schlange.full():
            self.schlange_voll += 1
            if self.streng:
                raise Streng("Die Warteschlange zum Schreiben ist voll")
        self._schlange.put(auftrag)

    def _packen(self):
        n = 0
        while True:
            auftrag = self._schlange.get()
            if auftrag is None:
                return
            try:
                i, voll, vor, nach, start, dauer, roh = auftrag
                alt = None if voll else self._stand.get(i)
                merke = None
                if self.felder is not None:
                    merke = lambda stellen, i=i, l=len(roh): self.felder.merke(i, stellen, l)  # noqa: E731
                art, nutz = (VOLL, roh) if alt is None else (AENDERUNG, aenderungen(alt, roh, merke))
                self._stand[i] = roh
                z = zlib.compress(nutz, 1)
                self._f.write(RAHMEN.pack(art, i, REIN if vor == nach else 0, vor, nach, start, dauer, len(nutz), len(z)))
                self._f.write(z)
                self._f.write(struct.pack("<I", zlib.crc32(z)))
                n += 1
                if n % 50 == 0:
                    self._f.flush()  # damit die Wache des Laufs mitlesen kann
                if self.felder is not None:
                    self.felder.pruefe(vor)
            except Exception as e:  # noqa: BLE001  der Lesefaden meldet den Fehler weiter
                self._fehler = e
                return

    def lauf(self, takte=None, bis_takt=None, pause=0.001, stop=None, aussetzen=None):
        """Bis so viele Takte gelesen sind, der Spieltakt bis_takt erreicht ist oder stop() wahr wird.
        Solange aussetzen() wahr ist, wird nichts gelesen (Bremsprobe: Takte je Sekunde ohne Lesen)."""
        n = 0
        while (takte is None or n < takte) and not (stop and stop()):
            if aussetzen and aussetzen():
                self.letzter = None  # die ausgesetzten Takte fehlen nicht, sie wurden bewusst nicht gelesen
                time.sleep(pause)
                continue
            if self.schritt():
                n += 1
                if bis_takt is not None and self.letzter >= bis_takt:
                    break
            else:
                if bis_takt is not None and self.takt() >= bis_takt:
                    break
                time.sleep(pause)
        return n

    def schliessen(self):
        if self._packer.is_alive():
            self._schlange.put(None)
            self._packer.join()
        self._f.close()
        if self._fehler:
            raise self._fehler


def tempo_ohne_lesen(quelle, takte=1000, takt_adresse=TAKT_ADRESSE, frist=30.0):
    """Takte je Sekunde, wenn nur die Taktnummer gelesen wird (Vergleichswert fuer Probe A4). frist nur gegen ein stehendes Spiel."""
    lies = lambda: struct.unpack("<I", quelle.lies(takt_adresse, 4))[0]
    a, t0 = lies(), time.perf_counter()
    while lies() - a < takte and time.perf_counter() - t0 < frist:
        time.sleep(0.002)
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
    p.add_argument("--tempo-wert", type=int, help="eingestelltes Spieltempo, fuer die Auswertung")
    p.add_argument("--ausgabe", required=True)
    p.add_argument("--lauf", default="-", help="F, K oder S")
    p.add_argument("--takte", type=int)
    p.add_argument("--datenblock-alle", type=int, default=250)
    p.add_argument("--karte-alle", type=int, default=25)
    p.add_argument("--tempo-takte", type=int, default=1000, help="Vergleichswert: so viele Takte ohne Lesen messen, 0 = nicht messen")
    p.add_argument("--voll-bei", type=int, nargs="*", default=[], help="Takte, in denen alle Bereiche gelesen werden (Takt des Speicherns)")
    p.add_argument("--streng", action="store_true", help="jeder Takt muss ankommen, sonst Ende mit Rueckgabe 3")
    p.add_argument("--aussetzen-datei", help="solange diese Datei da ist, wird nichts gelesen")
    p.add_argument("--felder-datei", help="hierhin schreibt die Feld-Wache ihren Stand")
    p.add_argument("--felder-alle", type=int, default=800, help="Abstand der Feld-Wache in Takten")
    a = p.parse_args(argv)
    pid = a.pid if a.pid else pid_der_instanz(a.instanz) if a.instanz else None
    if not pid:
        p.error("Prozess nicht gefunden (--pid oder --instanz)")
    sys.setswitchinterval(0.0005)  # der Packfaden darf das Lesen nicht aufhalten
    quelle = ProzessQuelle(pid)
    karte = Feldkarte.laden(feldliste=FELDLISTE)
    kopf = {"tempo": a.tempo_wert, "lauf": a.lauf, "programm": quelle.pfad, "spielart": spielart_lesen(quelle, karte), "tempo_ohne_lesen": tempo_ohne_lesen(quelle, a.tempo_takte) if a.tempo_takte else None}
    bereiche = standard_bereiche(karte, a.datenblock_alle, a.karte_alle)
    felder = FeldWache(karte, bereiche, a.felder_datei, a.felder_alle) if a.felder_datei else None
    auf = Aufzeichner(quelle, bereiche, a.ausgabe, kopf, voll_bei=a.voll_bei, streng=a.streng, felder=felder)
    stand = {"gelesen": 0, "grund": None}
    code = 0
    try:
        stand["gelesen"] = auf.lauf(takte=a.takte, pause=0.0 if a.streng else 0.0002, stop=(lambda: os.path.exists(a.stop_datei)) if a.stop_datei else None,
                                    aussetzen=(lambda: os.path.exists(a.aussetzen_datei)) if a.aussetzen_datei else None)
    except Streng as e:
        stand["grund"], code = str(e), 3
    finally:
        try:
            auf.schliessen()
        except Streng as e:
            stand["grund"], code = str(e), 3
        stand.update(fehlend=auf.fehlend, gemischt=auf.gemischt, gemischt_selten=auf.gemischt_selten, schlange_voll=auf.schlange_voll, letzter_takt=auf.letzter)
        if felder is not None:
            stand["felder"] = len(felder.gesehen)
        with open(a.ausgabe + ".stand", "w", encoding="utf-8") as f:
            json.dump(stand, f, ensure_ascii=False)
    print(f"Aufzeichnung {a.ausgabe}: {stand}")
    sys.exit(code)


if __name__ == "__main__":
    main()
