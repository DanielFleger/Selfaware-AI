# -*- coding: utf-8 -*-
"""B-142: Stellen die Karten mit 8 Spielern wirklich je Spieler einen Lord auf? Die Spielerzahl steht im Kartenkopf, gestartet werden nur diese Karten. Baut nichts, schreibt nur die Liste.

Aufruf: PYTHONPATH=src python data/research/auge_plan/karten_acht_lords.py 2
Grenze: 6 Minuten, danach Schluss. Am Ende steht das Spiel angehalten, die Sperre ist frei. Rueckgabe 3: Das Spiel ist abgestuerzt, nach dem Neustart setzt derselbe Aufruf fort.
"""
import json
import os
import sys
import time

from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments import auge_lauf_k as lk
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

n = int(sys.argv[1])
lf.pruefe_laufinstanz(n)
os.environ["SHC_INSTANZ"] = str(n)
AUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "karten_acht_lords.json")
GRENZE_TAKTE = 1000  # die Lords standen in der ersten Suche nach 300 Takten, hier soll das nicht die Messung begrenzen


def sichern(ergebnis):
    with open(AUS, "w", encoding="utf-8") as f:
        json.dump(ergebnis, f, ensure_ascii=False, indent=0)


karten = sorted(lk.karten_fuer_acht(n))
print("Karten mit 8 Spielern:", len(karten), flush=True)
lf.sperre_holen("Karten mit 8 Lords (B-142)")
lf.logik_einspielen(os.path.join(lf.ordner(n), "ucp", "villagestudio", "logik.lua"), os.path.join(lf.ordner(lf.QUELL_INSTANZ), "ucp", "villagestudio", "logik.lua"))
time.sleep(3)  # das Modul laedt die Datei von selbst nach
k = lf.EchterKanal()
lf.warte_auf_modul(k)
lf.warte_auf(lambda: k.peek(lf.ANSICHT)[0] in (lf.HAUPTMENUE, lf.IN_PARTIE), 90, "Spiel ist im Menue")  # gemessen: rund 26 s Vorspann
s = lk.SpeicherK(ProzessQuelle(pid_der_instanz(n)))
ergebnis = {x: v for x, v in (json.load(open(AUS, encoding="utf-8")) if os.path.exists(AUS) else {}).items() if x in karten}
abgestuerzt = False
ende = time.time() + 360
steht = False
try:
    for name in [x for x in karten if x not in ergebnis]:
        if time.time() > ende:
            break
        try:
            ergebnis[name] = {"ende": "Absturz"}  # bleibt stehen, wenn das Spiel dabei stirbt
            sichern(ergebnis)
            lk.gefecht_starten(k, name, 0, warte=15)
            k.befehl({"tempo": 200}, 0.3)
            t0 = time.time()
            while s.lord_besitzer() != lk.SOLL_LORDS and s.takt() < GRENZE_TAKTE and time.time() < t0 + 10:
                time.sleep(0.02)
            ergebnis[name] = {"ende": "gemessen", "lords_bei": s.lord_besitzer(), "takt": s.takt()}
        except (lf.Fehler, OSError, RuntimeError) as e:
            if pid_der_instanz(n) is None:
                abgestuerzt = True
                print(name, "Absturz", flush=True)
                break
            ergebnis[name] = {"ende": f"Fehler: {str(e)[:60]}"}
        print(name, ergebnis[name], flush=True)
        sichern(ergebnis)
finally:
    try:
        steht, t = lf.anhalten_und_pruefen(k, s)
    except OSError:
        steht, t = True, None  # das Spiel ist weg, nichts mehr anzuhalten
    print("angehalten", steht, t, flush=True)
    if steht:
        lf.sperre_freigeben()
acht = [x for x, v in ergebnis.items() if v.get("lords_bei") == lk.SOLL_LORDS]
print("ACHT LORDS:", len(acht), "von", len(ergebnis), "geprueft, Karten mit 8 Spielern", len(karten), "| spaetester Takt", max((ergebnis[x]["takt"] for x in acht), default=None), "| andere", [x for x in ergebnis if x not in acht])
sys.exit(3 if abgestuerzt else 0)
