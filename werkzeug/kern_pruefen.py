# -*- coding: utf-8 -*-
"""B-115 im Spiel pruefen: liest der Rust-Kern (samurai_kern.dll) dasselbe wie das Lagebild?
Braucht logik.lua mit Kern-Lader (logik_stand_20261019.lua ab 23:05) und samurai_kern.dll in <Instanz>/ucp/villagestudio/.
  A. Kern geladen (Version gemeldet)
  B. Einheiten je Spieler 1-8 aus der DLL = Zaehlung im Lagebild (gleicher Filter: Typ > 0, nicht sterbend)
  C. GEGENPROBE: eine Einheit fuer Spieler 2 setzen -> DLL Spieler 2 genau +1, Spieler 1 unveraendert
  D. Protokoll ucp/villagestudio/samurai_kern.log bekommt Zeilen (der Kern laeuft je Takt)
Aufruf: SHC_INSTANZ=5 python werkzeug/kern_pruefen.py"""
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import befehl as kanal
import spieler2_pruefen as S2
from serie import zuruecksetzen

ok = []


def pruefe(nr, text, bed):
    ok.append(bool(bed))
    print("%-4s %s %s" % ("OK" if bed else "ROT", nr, text), flush=True)


def kern_status():
    z = " ".join(kanal.sende({"befehle": [{"id": kanal.neue_id(), "kern": "status"}]}, 1.5, bis="KERN status"))
    m = re.search(r"KERN status: (\S+) - ([^;]*); Einheiten je Spieler 0-8 aus der DLL: ([\d\- ]+)", z)
    if not m:
        return None, z[-200:], []
    return m.group(1) == "ok", m.group(2), [int(x) for x in m.group(3).split()]


def lagebild_je_spieler():
    E, G = S2.lage()
    je = [0] * 9
    for e in E.values():
        b = int(e[1])
        if 0 <= b <= 8:
            je[b] += 1
    return je


def main():
    print("Zuruecksetzen:", zuruecksetzen(), flush=True)
    start = [246] * 8
    start[4], start[3] = 0, 1
    kanal.sende({"eigenesGefecht": True, "karte": "Green Haven", "ki": 7, "gegner": 1, "ausgleich": 3, "startliste": start}, 4,
                bis="LaunchSkirmishGame zurueck")
    S2.s({"player": 1, "tempo": 300}, 1.0, "TEMPO")
    S2.s({"player": 1, "pause": False}, 0.5)
    t0 = time.time()
    while time.time() - t0 < 60 and len(S2.lords()) < 2:
        time.sleep(0.5)
    S2.s({"player": 1, "pause": True}, 0.5)
    gut, text, dll = kern_status()
    pruefe("A", "Kern: %s" % text, gut and "Version" in text)
    lb = lagebild_je_spieler()
    gut, text, dll = kern_status()
    pruefe("B", "Einheiten je Spieler 1-8: DLL %s, Lagebild %s" % (dll[1:], lb[1:]), dll[1:] == lb[1:] and sum(lb[1:]) > 0)
    lord2 = [(int(x), int(y)) for sp, x, y in S2.lords() if sp == "2"][0]
    kanal.sende({"setzeEinheit": {"spieler": 2, "typ": 70, "x": lord2[0] + 4, "y": lord2[1] + 4, "anzahl": 1}}, 1.0, "SETZE")
    gut, text, dll2 = kern_status()
    pruefe("C", "GEGENPROBE eine Einheit fuer Spieler 2: Spieler 2 %d -> %d, Spieler 1 %d -> %d" % (dll[2], dll2[2], dll[1], dll2[1]),
           dll2[2] == dll[2] + 1 and dll2[1] == dll[1])
    S2.lauf(2.0)
    pfad = os.path.join(os.path.dirname(kanal.BEFEHL), "..", "..", "ucp", "villagestudio", "samurai_kern.log")
    zeilen = open(pfad, encoding="utf-8").read().splitlines() if os.path.exists(pfad) else []
    pruefe("D", "Kern-Protokoll: %d Zeilen, letzte: %s" % (len(zeilen), zeilen[-1] if zeilen else "-"), len(zeilen) > 0)
    print("%d von %d gruen" % (sum(ok), len(ok)), flush=True)
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
