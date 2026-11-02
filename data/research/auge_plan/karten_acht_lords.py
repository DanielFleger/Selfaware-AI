# -*- coding: utf-8 -*-
"""B-142: Welche Karten stellen 8 KI-Lords auf? Startet sie auf der Laufinstanz nacheinander kurz und zaehlt. Baut nichts, schreibt nur die Liste.

Aufruf: PYTHONPATH=src python data/research/auge_plan/karten_acht_lords.py 2 [Treffer=3]
Grenze: 12 Minuten, danach Schluss. Am Ende steht das Spiel angehalten, die Sperre ist frei.
"""
import glob
import json
import os
import sys
import time

from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments import auge_lauf_k as lk
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

n = int(sys.argv[1])
ziel = int(sys.argv[2]) if len(sys.argv) > 2 else 3
lf.pruefe_laufinstanz(n)
os.environ["SHC_INSTANZ"] = str(n)
AUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "karten_acht_lords.json")
# Der Ordner maps enthaelt keine Gefechtskarten (gemessen: 113 von 113 ohne Lord); Liga_Grumpy Neighbors liegt im Plugin und stellt 4 Lords
ordner = [os.path.join(os.path.expandvars("%USERPROFILE%"), "Documents", "Stronghold Crusader", x) for x in ("MapsExtreme", "Maps")] + [os.path.join(lf.ordner(n), "mapsExtreme")]
ordner += glob.glob(os.path.join(lf.ordner(n), "ucp", "plugins", "Mod-KI-Team-Liga-*", "resources", "maps"))
karten = sorted({f[:-4] for o in ordner if os.path.isdir(o) for f in os.listdir(o) if f.endswith(".map")})
lf.sperre_holen("Karten mit 8 Lords (B-142)")
lf.logik_einspielen(os.path.join(lf.ordner(n), "ucp", "villagestudio", "logik.lua"), os.path.join(lf.ordner(lf.QUELL_INSTANZ), "ucp", "villagestudio", "logik.lua"))
time.sleep(3)  # das Modul laedt die Datei von selbst nach
k = lf.EchterKanal()
s = lk.SpeicherK(ProzessQuelle(pid_der_instanz(n)))
ende = time.time() + 720
alt = json.load(open(AUS, encoding="utf-8")) if os.path.exists(AUS) else {}
ergebnis = {k_: v for k_, v in alt.get("lords", {}).items() if k_ in karten}
treffer = [k_ for k_ in alt.get("treffer", []) if k_ in karten]
steht = False
try:
    for name in [k_ for k_ in karten if k_ not in ergebnis]:
        if time.time() > ende or len(treffer) >= ziel:
            break
        try:
            ergebnis[name] = "Absturz"  # bleibt stehen, wenn das Spiel dabei stirbt
            with open(AUS, "w", encoding="utf-8") as f:
                json.dump({"treffer": treffer, "lords": ergebnis}, f, ensure_ascii=False, indent=0)
            lk.gefecht_starten(k, name, 0, warte=15)
            k.befehl({"tempo": 200}, 0.3)
            a = s.takt()
            t0 = time.time()
            while s.takt() < a + 60 and time.time() < t0 + 3:
                time.sleep(0.02)
            ergebnis[name] = s.lords()
        except (lf.Fehler, OSError, RuntimeError) as e:
            ergebnis[name] = f"Fehler: {str(e)[:60]}"
        if ergebnis[name] == 8:
            treffer.append(name)
        print(name, ergebnis[name], flush=True)
        with open(AUS, "w", encoding="utf-8") as f:
            json.dump({"treffer": treffer, "lords": ergebnis}, f, ensure_ascii=False, indent=0)
finally:
    try:
        steht, t = lf.anhalten_und_pruefen(k, s)
    except OSError:
        steht, t = True, None  # das Spiel ist weg, nichts mehr anzuhalten
    print("angehalten", steht, t, flush=True)
    if steht:
        lf.sperre_freigeben()
print("TREFFER:", treffer)
