# -*- coding: utf-8 -*-
"""B-142: Wie lange rechnet das Spiel, nachdem der Takt hochgezaehlt wurde? Der Zaehler steigt am Anfang des Takts, Einheiten und Gebaeude rechnen danach.

Aufruf: PYTHONPATH=src python data/research/auge_plan/takt_dauer_messen.py 2 [Takte=40] [Tempo=40]
Das Spiel muss stehen, in einer Partie. Liest nur und gibt nur Tempo und Pause. Am Ende steht es wieder.
Waehrend des Laufs wird nur gelesen und gemerkt, verglichen wird danach: Der Vergleich dauert laenger als ein Takt.
Ergebnis: je Feld die spaeteste Aenderung nach dem Hochzaehlen. Wer ueber den ganzen Takt schreibt, ist nicht die Spielrechnung, sondern das Zeichnen.
"""
import collections
import os
import struct
import sys
import time

import numpy as np

from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments import auge_lauf_k as lk
from selfaware.tools.experiments.auge_aufzeichnung import TAKT_ADRESSE, ProzessQuelle, pid_der_instanz

n = int(sys.argv[1])
takte = int(sys.argv[2]) if len(sys.argv) > 2 else 40
tempo = int(sys.argv[3]) if len(sys.argv) > 3 else 40
lf.pruefe_laufinstanz(n)
os.environ["SHC_INSTANZ"] = str(n)
karte = Feldkarte.laden(feldliste=FELDLISTE)
q = ProzessQuelle(pid_der_instanz(n))
BEREICHE = [karte.struktur(x)[:2] for x in ("DAT_UnitsState", "DAT_BuildingsState", "DAT_EntityState", "DAT_TribesState")]


def takt():
    return struct.unpack("<I", q.lies(TAKT_ADRESSE, 4))[0]


def stand():
    return [q.lies(a, b - a) for a, b in BEREICHE]


def luecken(x, y):
    """(Versatz, Laenge) der abweichenden Stellen, schnell ueber numpy."""
    d = np.flatnonzero(np.frombuffer(x, dtype=np.uint8) != np.frombuffer(y, dtype=np.uint8))
    if not len(d):
        return []
    grenzen = np.flatnonzero(np.diff(d) > 1)
    anfang = np.concatenate(([d[0]], d[grenzen + 1]))
    ende = np.concatenate((d[grenzen], [d[-1]]))
    return list(zip(anfang.tolist(), (ende - anfang + 1).tolist()))


lf.sperre_holen("Takt-Dauer messen (B-142)")
k = lf.EchterKanal()
s = lk.SpeicherK(q)
ende_uhr = time.time() + takte / tempo * 4 + 20
abstaende, sprung = [], 0
merker = []  # (Takt-Nummer in der Reihe, Zeit nach dem Hochzaehlen, Bereich, alt, neu)
try:
    k.befehl({"tempo": tempo}, lf.KANAL)
    k.befehl({"pause": False}, lf.KANAL)
    alt = takt()
    while takt() == alt and time.time() < ende_uhr:
        pass
    alt = takt()
    t0 = time.perf_counter()
    vorher = stand()
    lesungen = []
    nr = 0
    while nr < takte and time.time() < ende_uhr:
        t = takt()
        if t != alt:
            jetzt = time.perf_counter()
            abstaende.append(jetzt - t0)
            sprung += t - alt > 1
            lesungen.append(0)
            alt, t0 = t, jetzt
            nr += 1
            continue
        neu = stand()
        zeit = time.perf_counter() - t0
        for b, (x, y) in enumerate(zip(vorher, neu)):
            if x is not y and x != y:
                merker.append((nr, zeit, b, x, y))
        vorher = neu
        if lesungen:
            lesungen[-1] += 1
finally:
    steht, tt = lf.anhalten_und_pruefen(k, s)
    print("angehalten", steht, tt, flush=True)
    if steht:
        lf.sperre_freigeben()
print(f"Takte {len(abstaende)}, mehr als ein Takt weiter {sprung}; Abstand der Takte in ms: Mitte {sorted(1000 * x for x in abstaende)[len(abstaende) // 2]:.1f}; Lesungen je Takt: Mitte {sorted(lesungen)[len(lesungen) // 2]}, Aenderungs-Merker {len(merker)}")
spaeteste = collections.defaultdict(float)
stufe = collections.defaultdict(collections.Counter)
for nr, zeit, b, x, y in merker:
    for o, l in luecken(x, y):
        for g, f in karte.felder_einer_aenderung(BEREICHE[b][0] + o, l):
            spaeteste[(g, f)] = max(spaeteste[(g, f)], zeit)
            stufe[(g, f)][int(zeit * 1000) // 5 * 5] += 1
reihe = sorted(spaeteste.items(), key=lambda x: -x[1])
ZEICHNEN = {"units[].drawX", "units[].drawY", "units[].drawWidth", "units[].drawHeight1", "buildings[].surfaceAreaUnk"}
print("Felder gesamt", len(reihe))
gesamt = collections.Counter()
for (g, f), c in stufe.items():
    if f not in ZEICHNEN:
        for a, m in c.items():
            gesamt[a] += m
print("Fundstellen ohne Zeichenfelder, je 5-ms-Stufe:", sorted(gesamt.items()))
print("Felder mit Aenderung zwischen 5 und 20 ms, ohne Zeichenfelder:")
for (g, f), c in sorted(stufe.items()):
    if f not in ZEICHNEN and any(5 <= a < 20 for a in c):
        print(f"  {g} {f}  " + " ".join(f"{a}:{m}" for a, m in sorted(c.items())))
