# -*- coding: utf-8 -*-
"""Alles, was der Eroeffnungsplaner braucht, fuer EINEN Startstand frisch aus dem Spiel holen (Daniel 05.10. 18:55:
"du darfst nicht einfach blind starten, weil du auch schauen musst wo dein Keep steht").

1. Startstand laden, eigener Platz.
2. Bergfried = eigenes Gebaeude Typ 41; Eingang aus dem Gebaeude-Datensatz +0x112/+0x114
   (Gegenprobe 05.10.: im alten Start M7-04 kam genau (165,111) heraus, der bis dahin feste Wert).
3. Rohstoffkarte und Baumliste (Modulbefehl rohstoffkarte) -> daten/rohstoffe_<kurz>.txt, baeume_<kurz>.txt.
4. Platzkarten (Spielpruefung je Feld) fuer Holzfaeller, Huette, Apfelplantage, Kornspeicher, Steinbruch,
   Ochsenjoch, Eisenmine ueber die GANZE Karte -> daten/start_<kurz>_platz_<name>.txt. (Bis 05.10. 19:58 nur
   Bergfried +- 80: die meisten Baeume unserer Seite lagen ausserhalb - 9t baute Holzfaeller bei x=26..37 ohne Karte.
   Eine Karte dauert 0-1 s, die ganze Karte kostet nichts.)
5. Lagerkarte OHNE Lager: Startlager kurz abreissen, Karte nehmen, Startstand neu laden (nichts bleibt veraendert).
6. daten/start_<kurz>.json mit Spielstand, Bergfried-Anker und -Eingang, feindlichem Bergfried.

Aufruf:  python karten_holen.py "M19 Liga Start Grumpy T600" M19
         python karten_holen.py "gefecht:Two Montains" TM      (frisches Gefecht statt Spielstand, SAI 11.10.)
"""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laden import befehl, lade_stand, peek
from steuerkarte import laufe
from bauen import platzkarte
from waechter import lies_gebaeude, lies_lagebild
from befehl import ABZUG

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
KARTEN = {"holzfaeller": 3, "huette": 1, "apfel": 32, "speicher": 19, "steinbruch": 20, "ochsen": 4, "eisenmine": 5}

def bergfriede():
    befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
    G = lies_gebaeude()
    aus = {}
    for n, g in G.items():
        if g["typ"] == 41 and g["besitzer"] > 0:
            w = peek(0xF98520 + n * 0x32C + 0x110, 2)
            aus[g["besitzer"]] = {"anker": (g["x"], g["y"]), "eingang": (w[0] >> 16 & 0xFFFF, w[1] & 0xFFFF)}
    return aus

def gefecht_frisch(karte, ki=7):
    """SAI 11.10. (Daniel 16:46 "teste eine andere Map, diagonale bzw. opposite Aufstellung"): statt eines gespeicherten
    Startstands ein frisches Gefecht auf <karte> - wir Platz 0, Gegner (ki, 7 = Sultan-Platz = Nomade) Platz 1 - und
    anhalten, sobald beide Lords stehen. Platz 2-5 gaben auf allen gemessenen Karten keinen Gegner-Lord."""
    import time
    import befehl as kanal
    from serie import zuruecksetzen
    from laden import TICK
    print("Zuruecksetzen:", zuruecksetzen(), flush=True)
    gefecht = {"eigenesGefecht": True, "karte": karte, "ki": ki, "gegner": 1, "ausgleich": 3,
               "startliste": [0, 1] + [246] * 6}
    z = kanal.sende(gefecht, 4, bis="LaunchSkirmishGame zurueck")
    print("Start:", [x for x in z if "GEFECHT" in x][-2:], flush=True)
    befehl({"pause": False}, 0.5)
    t0 = time.time()
    while time.time() - t0 < 60:
        if len(bergfriede()) >= 2 and peek(TICK)[0] >= 150:
            break
        time.sleep(0.5)
    befehl({"pause": True}, 0.5)
    befehl({"eigenerPlatz": 1}, 0.8)
    print("Gefecht steht bei Tick %d" % peek(TICK)[0], flush=True)

def laden(spielstand):
    if spielstand.startswith("gefecht:"):
        return gefecht_frisch(spielstand.split(":", 1)[1])
    lade_stand(spielstand, mit_bild=False)
    befehl({"eigenerPlatz": 1}, 0.8)

def main():
    spielstand, kurz = sys.argv[1], sys.argv[2]
    laden(spielstand)
    bf = bergfriede()
    eigen = bf[1]
    befehl({"rohstoffkarte": {}}, 8.0, bis="ROHSTOFF")
    shutil.copy(os.path.join(ABZUG, "rohstoffe.txt"), os.path.join(D, "rohstoffe_%s.txt" % kurz))
    shutil.copy(os.path.join(ABZUG, "baeume.txt"), os.path.join(D, "baeume_%s.txt" % kurz))
    zeilen = open(os.path.join(D, "rohstoffe_%s.txt" % kurz)).read().splitlines()[1:]
    x0, y0, x1, y1 = 0, 0, max(len(r) for r in zeilen) - 1, len(zeilen) - 1      # ganze Karte
    print("Bergfried Spieler 1: Anker %s, Eingang %s; Karte (%d,%d)-(%d,%d)" % (eigen["anker"], eigen["eingang"], x0, y0, x1, y1), flush=True)
    for name, typ in KARTEN.items():
        gut, alle, sek = platzkarte(typ, x0, y0, x1, y1, os.path.join(D, "start_%s_platz_%s.txt" % (kurz, name)))
        print("Platzkarte %-11s: %6d von %6d Feldern gehen (%.0f s)" % (name, gut, alle, sek), flush=True)
    # Lager ohne Lager: Startlager abreissen, Karte nehmen, Stand neu laden
    lager = [n for n, g in lies_gebaeude().items() if g["besitzer"] == 1 and g["typ"] == 10]
    for n in lager:
        befehl({"abreissen": {"nr": n}}, 0.8, bis="ABREISSEN")
    laufe(2)
    gut, alle, sek = platzkarte(10, x0, y0, x1, y1, os.path.join(D, "start_%s_platz_lager_keins.txt" % kurz))
    print("Platzkarte lager_keins: %6d von %6d (Startlager %s abgerissen, %.0f s)" % (gut, alle, lager, sek), flush=True)
    laden(spielstand)
    L = lies_lagebild(neu_holen=True)
    info = {"spielstand": spielstand, "kurz": kurz, "bergfried_anker": eigen["anker"], "bergfried_eingang": eigen["eingang"],
            "feind_bergfried": {str(sp): v for sp, v in bf.items() if sp != 1},
            "lord": [(e["x"], e["y"]) for e in L.values() if e["besitzer"] == 1 and e["typ"] == 55],
            "fenster": (x0, y0, x1, y1)}
    json.dump(info, open(os.path.join(D, "start_%s.json" % kurz), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(info, ensure_ascii=False))

if __name__ == "__main__":
    main()
