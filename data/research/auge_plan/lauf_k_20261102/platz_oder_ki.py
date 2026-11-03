# -*- coding: utf-8 -*-
"""B-142 Lauf K: Im Lauf griffen nur die Spieler 1 bis 4 an. Liegt das an der KI oder am Platz? Dieselben 8 KI in umgekehrter Reihenfolge, bis Takt 60.000 mitlesen.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/platz_oder_ki.py 2
Grenze: 3 Minuten. Am Ende steht das Spiel, die Sperre ist frei.
"""
import os
import struct
import sys
import time

from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments import auge_lauf_k as lk
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

n = int(sys.argv[1])
lf.pruefe_laufinstanz(n)
os.environ["SHC_INSTANZ"] = str(n)
karte = Feldkarte.laden(feldliste=FELDLISTE)
q = ProzessQuelle(pid_der_instanz(n))
s = lk.SpeicherK(q)
k = lf.EchterKanal()
KIS = tuple(reversed(lk.KIS))
ST = karte.adresse("DAT_GameState", "playerDataArray[].aiPlayerState")
TR = karte.adresse("DAT_GameState", "playerDataArray[].totalAttackTroops")
WE = karte.adresse("DAT_GameState", "playerDataArray[].currentAttackWave")
lf.sperre_holen("Platz oder KI (B-142)")
ende = time.time() + 180
try:
    if k.peek(lf.ANSICHT)[0] != lf.HAUPTMENUE:
        k.befehl({"menue": lf.HAUPTMENUE}, 1.5)
        lf.warte_auf(lambda: k.peek(lf.ANSICHT)[0] == lf.HAUPTMENUE, 10, "Hauptmenue")
    k.befehl({"pause": False}, lf.KANAL)
    k.befehl({"eigenesGefecht": True, "karte": "Green Haven", "kis": list(KIS), "friedenszeit": 1, "gegner": 0, "trotzdem": True}, 5.0)
    lf.warte_auf(lambda: k.peek(lf.ANSICHT)[0] == lf.IN_PARTIE, 15, "Partie laeuft")
    k.befehl({"tempo": lf.TEMPO_LAUF}, lf.KANAL)
    print("KI je Platz", KIS, flush=True)
    angriff, truppen, welle = {}, {}, {}
    while s.takt() < 60000 and time.time() < ende:
        t = s.takt()
        for sp in range(1, 9):
            z = struct.unpack("<i", q.lies(ST[0] + sp * ST[2], 4))[0]
            if z != 0 and sp not in angriff:
                angriff[sp] = t
            truppen[sp] = max(truppen.get(sp, 0), struct.unpack("<i", q.lies(TR[0] + sp * TR[2], 4))[0])
            welle[sp] = struct.unpack("<i", q.lies(WE[0] + sp * WE[2], 4))[0]
        time.sleep(0.05)
    print("bis Takt", s.takt(), "erster Angriff je Platz", dict(sorted(angriff.items())), flush=True)
    print("hoechste Angriffstruppen je Platz", truppen, "Welle", welle, "Lords", s.lord_besitzer(), flush=True)
finally:
    steht, tt = lf.anhalten_und_pruefen(k, s)
    print("angehalten", steht, tt, flush=True)
    if steht:
        lf.sperre_freigeben()
