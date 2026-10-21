# -*- coding: utf-8 -*-
"""B-150 Augen-Test FEUER (Daniel 21.10.2026 18:29, Bild: eigene Sklaven zuendeten eine Mine an und das Heer lief durch das
Feuer; 18:56 "ja mach Feuer-Test"). Erst messen, was Feuer im Spiel tut, dann bekommt der Kern ein Auge dafuer.

Aufbau: shc.sandkasten (Franz' Burg aus dem Pruefstand, beide Heere ohne Lord abgeraeumt, Franz ohne Waren - es gibt keine
Schuetzen und keinen Nachbau, Schaden an unseren Einheiten kann nur vom Feuer kommen). Ziel: ein Holzgebaeude von Spieler 2
mit freiem Feld drumherum. Zwei eigene Sklaven zuenden es an (angriff "gebaeude", Art 9 - der echte Weg). Eigene
Streitkolben stehen still in 1, 2, 3, 5 Feldern Abstand, einer 10 Felder weg (Gegenprobe).

VORHER FESTGELEGT:
  BRAND erkannt, wenn fireDuration (Gebaeude +0x14+702, raid_messen.py) am Ziel binnen 600 Takten nach dem Befehl > 0 wird.
  FEUERSCHADEN im Abstand d belegt, wenn der Streitkolben in d Feldern Leben verliert; die Gegenprobe (10 Felder) darf nichts
  verlieren - sonst schiesst noch jemand und der Versuch misst nicht das Feuer.
  UEBERGREIFEN belegt, wenn ein anderes Gebaeude bis 4 Felder danach fireDuration > 0 hat.
Ergebnis: eine Zeile in daten/augen_feuer.jsonl, Verlauf alle 100 Takte.

Aufruf:  SHC_INSTANZ=5 python werkzeug/augen_feuer.py [takte=2000] [stand="B140 Burg Franz T40126"]
"""
import json
import os
import sys
import time

os.environ.setdefault("SHC_INSTANZ", "5")
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
sys.path.insert(0, os.path.join(HIER, "..", "..", "Selfaware-AI-kern", "src"))
import shc  # noqa: E402
from laden import befehl, peek  # noqa: E402
from befehl import SPIEL  # noqa: E402
from selfaware.game.kern_leitung import Leitung  # noqa: E402

GEBAEUDE, G_SCHRITT, FEUER = 0xF98520, 0x32C, 0x14 + 702
HOLZ = (3, 30, 31, 32, 1)          # Holzfaeller, Getreide, Hopfen, Apfel, Huette (raid_messen.ZIELARTEN)
ABSTAENDE = (1, 2, 3, 5, 10)
AUS = os.path.join(HIER, "..", "daten", "augen_feuer.jsonl")
le = Leitung(SPIEL)


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def feuer(nr):
    return peek(GEBAEUDE + nr * G_SCHRITT + FEUER)[0] & 0xFFFF


def gebiet(x, y):
    """Wegnetz-Gebiet des Feldes (PathConnectionLayer 0x01DF70D8, L174)."""
    z = peek(0x023372F8 + y * 12, 3)
    k = z[1] + x - z[0]
    a = 0x01DF70D8 + 2 * k
    w = peek(a & ~3)[0]
    return (w >> 16) & 0xFFFF if a % 4 else w & 0xFFFF


def laufen(takte, tempo=100):
    """takte Spieltakte laufen lassen. B-154 (Daniel 20:40): endet die Partie dabei (Endbildschirm, Menue, gameOver) oder
    steht die Uhr 30 s still, sofort abbrechen - mit dem Grund des Spielende-Melders (vorher wartete das hier ewig)."""
    t0 = shc.zustand()["tick"]
    befehl({"pause": False, "tempo": tempo}, 0.2)
    letzt, seit = t0, time.time()
    while True:
        z = shc.zustand()
        if z.get("ansicht") not in (shc.IN_PARTIE, 16) or z.get("gameover") != 0:
            raise shc.Fehler("SPIELENDE waehrend des Versuchs: %s | Melder: %s" % (z, shc.letztes_spielende()))
        if z["tick"] >= t0 + takte:
            break
        if z["tick"] != letzt:
            letzt, seit = z["tick"], time.time()
        elif time.time() - seit > 30:
            raise shc.Fehler("Spieluhr steht seit 30 s bei Takt %d: %s | Melder: %s" % (letzt, z, shc.letztes_spielende()))
        time.sleep(0.2)
    befehl({"pause": True}, 0.3)
    return shc.zustand()["tick"]


def main(takte=2000, stand=shc.STANDARD_STAND, ziel="frei", schritt=100, nur_soldaten="nein"):
    print("OK:", shc.sandkasten(stand, nur_soldaten=nur_soldaten), flush=True)
    w = le.lesen()
    G2 = {n: g for n, g in w.gebaeude.items() if g["besitzer"] == 2 and g["typ"] in HOLZ and g["leben"] > 0}
    # Ziel: das Holzgebaeude mit den wenigsten anderen Gebaeuden bis 3 Felder (Platz fuer die Streitkolben), Nachbarn bis 4
    # Felder werden fuer das Uebergreifen mitgemessen
    def dicht(g):
        return sum(1 for h in w.gebaeude.values() if h is not g and schach((g["x"], g["y"]), (h["x"], h["y"])) <= 3)
    # ziel=frei: Platz fuer die Streitkolben (Test 1); ziel=siedlung: mitten in Franz' Siedlung, wo Brunnen und Loescher
    # sind (Test 2, Daniel 19:00 "hast du gesehen und berechnet, wie viel die Feuerloescher geloescht haben?")
    nr = (max if ziel == "siedlung" else min)(G2, key=lambda n: (dicht(G2[n]), -n if ziel == "siedlung" else n))
    if ziel == "brunnen":     # (19:07: das Holzgebaeude am naechsten an einem Brunnen (27) - dort koennen Loescher (53) helfen)
        brunnen = [(g["x"], g["y"]) for g in w.gebaeude.values() if g["besitzer"] == 2 and g["typ"] == 27]
        # (Test 3, 19:11: Huette 71 lag hinter Franz' Mauer, die Sklaven standen 500 Takte davor - darum nur Ziele, die von
        # draussen erreichbar sind: ein Feld bis 2 neben dem Gebaeude im selben Wegnetz-Gebiet wie unser Startpunkt (L174))
        draussen = gebiet(160, 186)
        G2 = {n: g for n, g in G2.items()
              if any(gebiet(g["x"] + dx, g["y"] + dy) == draussen for dx in (-2, 0, 2) for dy in (-2, 0, 2) if dx or dy)}
        print("von draussen erreichbare Holzgebaeude von Spieler 2:", sorted(G2), "(Gebiet draussen %d)" % draussen, flush=True)
        nr = min(G2, key=lambda n: (min((schach((G2[n]["x"], G2[n]["y"]), b) for b in brunnen), default=999), n))
        print("Brunnen von Spieler 2:", brunnen, flush=True)
    if ziel.isdigit():        # (19:16: Ziel fest vorgeben - Apfelplantage 19 brannte in Test 1/2 sicher, Huetten 71/172 nicht)
        nr = int(ziel)
    z = G2[nr]
    ort = (z["x"], z["y"])
    nachbarn = [n for n, h in w.gebaeude.items() if n != nr and schach(ort, (h["x"], h["y"])) <= 4]
    print("Ziel: Gebaeude %d (Typ %d) bei %s, Leben %d, Feuer %d, Nachbarn bis 4 Felder %s" % (
        nr, z["typ"], ort, z["leben"], feuer(nr), nachbarn), flush=True)
    sklaven = shc.setze(spieler=1, typ=71, x=ort[0] - 4, y=ort[1], anzahl=2)
    stk = {}
    for d in ABSTAENDE:
        r = shc.setze(spieler=1, typ=26, x=ort[0], y=ort[1] + d - 1, anzahl=1)     # (setze stellt 1 Feld weiter, gemessen 17.10.)
        stk[d] = int(r.split("Nummern [")[1].split("]")[0])
    s_nrs = [int(x) for x in sklaven.split("Nummern [")[1].split("]")[0].split(",")]
    laufen(3, 40)
    w = le.lesen()
    leben0 = {d: w.einheiten[n]["leben"] for d, n in stk.items() if n in w.einheiten}
    orte0 = {d: (w.einheiten[n]["x"], w.einheiten[n]["y"]) for d, n in stk.items() if n in w.einheiten}
    print("Streitkolben (Abstand -> Ort, Leben):", {d: (orte0.get(d), leben0.get(d)) for d in stk}, flush=True)
    befehl({"angriff": {"einheiten": s_nrs, "gebaeude": nr}}, 1.0)
    t_befehl = shc.zustand()["tick"]
    verlauf, brand_ab, ueber, geloescht = [], None, {}, None
    for k in range(takte // schritt):
        t = laufen(schritt)
        w = le.lesen()
        f = feuer(nr)
        if f > 0 and brand_ab is None:
            brand_ab = t
        for n in nachbarn:
            if n not in ueber and feuer(n) > 0:
                ueber[n] = t
        zl = w.gebaeude.get(nr)
        stand_k = {d: (w.einheiten[n]["leben"], (w.einheiten[n]["x"], w.einheiten[n]["y"]))
                   for d, n in stk.items() if n in w.einheiten}
        sk = {n: (w.einheiten[n]["x"], w.einheiten[n]["y"], w.einheiten[n]["leben"]) for n in s_nrs if n in w.einheiten}
        # Franz' Leute bis 10 Felder ums Feuer: wer kommt hin (Loescher)?
        franz = sorted((n, e["typ"], e["x"], e["y"], e["zustand"]) for n, e in w.einheiten.items()
                       if e["besitzer"] == 2 and e["leben"] > 0 and e["typ"] != 55 and schach(ort, (e["x"], e["y"])) <= 10)
        if brand_ab and f == 0 and zl and zl["leben"] > 0 and geloescht is None:
            geloescht = t
        verlauf.append({"tick": t, "feuer": f, "leben_ziel": zl["leben"] if zl else 0, "kolben": stand_k, "sklaven": sk,
                        "franz_bis_10": franz})
        print(verlauf[-1], flush=True)
    schaden = {d: leben0[d] - (verlauf[-1]["kolben"].get(d, (0,))[0]) for d in leben0}
    ergebnis = {
        "brand": ("erkannt nach %d Takten" % (brand_ab - t_befehl)) if brand_ab and brand_ab - t_befehl <= 600
                 else "WIDERLEGT (kein Feuer binnen 600 Takten)" if not brand_ab else "spaet (%d Takte)" % (brand_ab - t_befehl),
        "schaden_je_abstand": schaden,
        "gegenprobe_10": "sauber" if schaden.get(10, 0) == 0 else "UNGUELTIG (10 Felder verlor %d)" % schaden.get(10),
        "uebergreifen": ueber or "nein",
        "geloescht": ("JA bei Tick %d (Gebaeude stand noch)" % geloescht) if geloescht else "nein (abgebrannt oder brennt noch)",
    }
    zeile = {"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "ziel": nr, "typ": z["typ"], "ort": ort, "orte_kolben": orte0,
             "t_befehl": t_befehl, "verlauf": verlauf, "ergebnis": ergebnis}
    with open(AUS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(zeile, ensure_ascii=False) + "\n")
    print("ERGEBNIS:", json.dumps(ergebnis, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    a = dict(x.split("=", 1) for x in sys.argv[1:])
    main(int(a.get("takte", 2000)), a.get("stand", shc.STANDARD_STAND), a.get("ziel", "frei"), int(a.get("schritt", 100)),
         a.get("nur_soldaten", "nein"))
