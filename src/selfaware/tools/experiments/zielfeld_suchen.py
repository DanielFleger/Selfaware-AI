# -*- coding: utf-8 -*-
"""Wo steht im Spielspeicher, auf wen eine KI-Einheit zielt? (Daniel 06.10.: nichts vorher aussortieren; erst der
gemessene Schaden zeigt, wer wirklich stoert.)

Anlass: In den Lord-Minimum-Messungen (Codex 06.10.) zeigte keine feindliche Einheit sichtbar auf einen Assassinen,
obwohl die Angreifer ~120.000 Leben verloren. Die KI-Einheiten stehen auf Zielart 3 (+924); ihr Ziel steht nicht im
gelesenen Feld +926. Gesucht ist das Feld, in dem es steht.

Ablauf: Trainingsstand laden, eine Gruppe angreifen lassen (wie lordminimum_messen), Tempo niedrig. Sobald ein
Assassine Leben verliert: Spiel anhalten, die ganze Einheiten-Struktur (1168 Byte) aller Feinde im Umkreis 45 und der
getroffenen Assassinen lesen und jedes Feld (16 und 32 Bit) mit Nummer und UID der Assassinen vergleichen.

Vorher festgelegt, was als Treffer zaehlt und was widerlegt:
  Ein Feld F ist das Zielfeld, wenn es bei Feinden in mindestens der Haelfte der Schadens-Momente auf einen GETROFFENEN
  Assassinen zeigt und auf einen nicht getroffenen hoechstens halb so oft. Zeigt es gleich oft auf unbeteiligte, ist
  es ein Zufallstreffer (z. B. eine kleine Zahl, die zufaellig einer Nummer gleicht) - widerlegt.
  Gegenrichtung genauso: Feld der getroffenen Assassinen, das auf einen Feind im Umkreis zeigt ("wer hat mich
  getroffen").

Aufruf: uv run python -m selfaware.tools.experiments.zielfeld_suchen [stand=...] [groesse=20] [momente=12] [tempo=100] [ticks=2500]
"""

from selfaware import workspace as _workspace
import json
import os
import sys
import time
from collections import Counter

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.game.ucp.befehl as kanal
from selfaware.game.ucp.befehl import INSTANZ
from selfaware.runtime.live.erstes_spiel import runde_lesen
from selfaware.game.ucp.laden import befehl, peek
from selfaware.tools.experiments.lordminimum_messen import vorbereiten

D = os.path.join(_workspace.DATA)
SP = 1
EINHEITEN, GROESSE = 0x0138854C, 1168
WORTE = GROESSE // 4
UMKREIS = 45


def struktur(nr):
    """Die ganze Einheit als Bytes (292 Worte ueber den Modulbefehl peek)."""
    return b"".join(w.to_bytes(4, "little") for w in peek(EINHEITEN + nr * GROESSE, WORTE))


def felder(roh):
    """Alle 16- und 32-Bit-Felder: (breite, versatz) -> Wert (vorzeichenbehaftet)."""
    f = {}
    for o in range(0, len(roh) - 1, 2):
        f[(16, o)] = int.from_bytes(roh[o:o + 2], "little", signed=True)
    for o in range(0, len(roh) - 3, 4):
        f[(32, o)] = int.from_bytes(roh[o:o + 4], "little", signed=True)
    return f


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    stand = arg.get("stand", "SAI Lordminimum Basis 2026-10-06")
    groesse, momente = int(arg.get("groesse", 20)), int(arg.get("momente", 12))
    tempo, dauer = int(arg.get("tempo", 100)), int(arg.get("ticks", 2500))
    st, L, G, truppe, ln, le = vorbereiten(stand, groesse)
    uid = {n: int.from_bytes(struktur(n)[0x98:0x9C], "little", signed=True) for n in truppe}
    leben = {n: L[n]["leben"] for n in truppe}
    auf_getroffen, auf_andere, zurueck, gesehen = Counter(), Counter(), Counter(), []
    start = st["t"]
    befehl({"tempo": tempo}, 0.5)
    befehl({"pause": False}, 0.5)
    befehl({"angriff": {"einheiten": truppe, "ziel": ln}}, 0.8, bis="ANGRIFF")
    while len(gesehen) < momente:
        st, L, G = runde_lesen()
        lebend = [n for n in truppe if n in L and L[n]["besitzer"] == SP]
        if not lebend or st["t"] - start >= dauer or not any(e["typ"] == 55 and e["besitzer"] not in (0, SP) for e in L.values()):
            break
        getroffen = [n for n in lebend if L[n]["leben"] < leben[n]]
        leben.update({n: L[n]["leben"] for n in lebend})
        if not getroffen:
            befehl({"angriff": {"einheiten": lebend, "ziel": ln}}, 0.8, bis="ANGRIFF")
            continue
        befehl({"pause": True}, 0.5)
        orte = {n: (L[n]["x"], L[n]["y"]) for n in lebend}
        feinde = [n for n, e in L.items() if e["besitzer"] not in (0, SP)
                  and min(schach((e["x"], e["y"]), orte[g]) for g in getroffen) <= UMKREIS]
        werte_g = {v for g in getroffen for v in (g, uid[g])}
        werte_a = {v for a in lebend if a not in getroffen for v in (a, uid[a])}
        feind_werte = set()
        moment = {"tick": st["t"], "getroffen": getroffen, "feinde": {}, "angreifer": {}}
        for n in feinde:
            roh = struktur(n)
            fe = felder(roh)
            feind_werte |= {n, fe[(32, 0x98)]}
            moment["feinde"][n] = {"typ": L[n]["typ"], "ort": (L[n]["x"], L[n]["y"]), "roh": roh.hex()}
            for k, v in fe.items():
                if v in werte_g:
                    auf_getroffen[k] += 1
                elif v in werte_a:
                    auf_andere[k] += 1
        for g in getroffen:
            roh = struktur(g)
            moment["angreifer"][g] = roh.hex()
            for k, v in felder(roh).items():
                if v in feind_werte and v not in (0, -1):
                    zurueck[k] += 1
        gesehen.append(moment)
        print("Moment %d bei Tick %d: %d getroffen, %d Feinde im Umkreis %d" % (
            len(gesehen), st["t"], len(getroffen), len(feinde), UMKREIS), flush=True)
        befehl({"pause": False}, 0.5)
        befehl({"angriff": {"einheiten": lebend, "ziel": ln}}, 0.8, bis="ANGRIFF")
    befehl({"pause": True}, 0.5)
    m = len(gesehen)
    kandidaten = sorted(((k, auf_getroffen[k], auf_andere[k]) for k in auf_getroffen
                         if auf_getroffen[k] >= max(1, m // 2) and auf_andere[k] * 2 <= auf_getroffen[k]),
                        key=lambda x: (-x[1], x[2]))
    rueck = [(k, v) for k, v in zurueck.most_common(20) if v >= max(1, m // 2)]
    pfad = os.path.join(D, "zielfeld_%s_i%d.json" % (time.strftime("%Y%m%d_%H%M%S"), INSTANZ))
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump({"stand": stand, "groesse": groesse, "momente": gesehen,
                   "kandidaten_feind": [("%d@0x%03X" % k, a, b) for k, a, b in kandidaten],
                   "kandidaten_zurueck": [("%d@0x%03X" % k, v) for k, v in rueck]}, f)
    print("Momente mit Schaden: %d" % m)
    print("Feind-Feld zeigt auf getroffenen / auf unbeteiligten Assassinen (Treffer-Regel erfuellt):")
    for k, a, b in kandidaten[:15]:
        print("   %2d Bit @0x%03X (%4d): %d / %d" % (k[0], k[1], k[1], a, b))
    print("Feld des getroffenen Assassinen zeigt auf einen Feind im Umkreis:")
    for k, v in rueck:
        print("   %2d Bit @0x%03X (%4d): %d" % (k[0], k[1], k[1], v))
    print("Rohdaten:", pfad)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
