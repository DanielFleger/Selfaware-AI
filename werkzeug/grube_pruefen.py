# -*- coding: utf-8 -*-
"""Moerderloch (Fallgrube, Typ 67, Mapper 98) gegen Assassinen - im Spiel messen (18.10., Daniel 23:05: "vllt muss es ja doch
irgendwas wie Burggraben mit eins Abstand sein mit Moerderloechern? weil Stein kommt viel zu spaet rein"; 23:07: "4 Holz ist
ja wohl sehr wenig, wenn es einem Assassinen das Leben nimmt").

Vorher festgelegt (Totschlagtest):
  1. Der Besitzer baut eine Fallgrube ueber den NORMALEN Baubefehl (ClickPlaceBuilding, kostet wie beim Menschen) auf einem
     freien Feld P -> Gebaeude Typ 67 des Besitzers bei P, Holz sinkt um den Spielpreis (kosten(67), Ascension: 4)
  2. Gegenprobe ohne Grube: eine feindliche Assassine (Typ 73) laeuft 12 Felder ueber eine freie Reihe -> kommt mit vollem
     Leben an (sonst misst 3 etwas anderes als die Grube)
  3. Mit Grube: dieselbe Strecke in der Reihe von P -> gemessen: Leben vorher/nachher, tot ja/nein, steht die Grube danach noch
  4. Eine eigene Assassine des Besitzers laeuft ueber dieselbe Grube (falls sie noch steht, sonst eine zweite) -> Leben gleich
Widerlegt ist "Grube toetet Assassinen", wenn in 3 das Leben nicht sinkt oder sie mit mehr als der Haelfte durchkommt.
Aufruf (Spiel laeuft, Lenker aus): SHC_INSTANZ=4 python werkzeug/grube_pruefen.py [besitzer=2] [grube=x,y]"""
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import befehl as K
from editor_messen import lage, setze
from mauer_pruefen import feld
from laden import peek

ASSASSINE, GRUBE_TYP, GRUBE_MAPPER = 73, 67, 98
PD = 0x0115BDF8
FREI_NICHT = 0x01 | 0x02 | 0x04 | 0x08 | 0x30 | 0x100 | 0x200 | 0x400 | 0x800 | 0x1000 | 0x20000 | 0x4000 | 0x40000000


def holz(sp):
    return peek(PD + sp * 0x39F4 + 0x4D0 + 2 * 4)[0]


def gebaeude():
    from waechter import lies_gebaeude
    K.sende({"befehle": [{"player": 1, "id": K.neue_id(), "lagebild": True}]}, 3.0, bis="LAGEBILD")
    return lies_gebaeude()


def reihe_frei(x0, y, n):
    return all(feld(x, yy)["logik"] & FREI_NICHT == 0 for x in range(x0, x0 + n) for yy in (y - 1, y, y + 1))


def suche_reihe(mitte, n=14):
    for r in range(0, 40, 2):
        for dy in range(-r, r + 1, 2):
            for dx in (-r, r) if abs(dy) != r else range(-r, r + 1, 2):
                x0, y = mitte[0] + dx, mitte[1] + dy
                if reihe_frei(x0, y, n):
                    return x0, y
    return None


def laufe(sp, nr, ziel):
    K.sende({"befehle": [{"player": sp, "id": K.neue_id(), "angriff": {"einheiten": [nr], "lauf": list(ziel)}}]}, 2.0,
            bis="ANGRIFF")


def verfolge(nr, ziel, sekunden=25):
    """Zeitreihe (Tick, x, y, Leben) bis Ziel erreicht, tot oder Zeit um."""
    reihe, t_ende = [], time.time() + sekunden
    while time.time() < t_ende:
        t, L = lage()
        e = L.get(nr)
        if e is None:
            reihe.append((t, None, None, 0))
            break
        reihe.append((t, e["x"], e["y"], e["leben"]))
        if e["leben"] <= 0 or (abs(e["x"] - ziel[0]) <= 1 and abs(e["y"] - ziel[1]) <= 1):
            break
        time.sleep(0.15)
    return reihe


def main():
    arg = dict(a.split("=") for a in sys.argv[1:])
    besitzer = int(arg.get("besitzer", 2))
    feind = 3 - besitzer
    K.sende({"befehle": [{"player": 1, "id": K.neue_id(), "pause": False}]}, 1.0)
    lords = {e["besitzer"]: (e["x"], e["y"]) for e in lage()[1].values() if e["typ"] == 55}
    mitte = ((lords[1][0] + lords[2][0]) // 2, (lords[1][1] + lords[2][1]) // 2) if len(lords) >= 2 else (200, 200)
    if arg.get("grube"):
        # 18.10.: Gruben gehen nur nahe der eigenen Burg (Platzsuche: Spieler 2 bei (208,75)/(190,110) ja, (211,150) nein)
        p = tuple(int(v) for v in arg["grube"].split(","))
        x0, y = p[0] - 6, p[1]
        if not reihe_frei(x0, y, 14):
            print("WARNUNG: Reihe um die Grube nicht ganz frei", flush=True)
    else:
        platz = suche_reihe(mitte)
        if platz is None:
            raise SystemExit("keine freie Reihe um %s" % (mitte,))
        x0, y = platz
        p = (x0 + 6, y)                   # Grube in der Mitte der 14er-Reihe
    print("Reihe frei ab (%d,%d), Grube bei %s, Besitzer Spieler %d (Holz %d)" % (x0, y, p, besitzer, holz(besitzer)), flush=True)
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)

    # 1 Grube bauen wie ein Mensch - ZUERST, solange kein Feind in der Naehe steht (18.10. erster Versuch: die Assassine der
    # Gegenprobe stand 2 Felder daneben, das Spiel lehnt Bauen mit Feind in der Naehe ab)
    def baue_grube(q):
        z = K.sende({"befehle": [{"player": besitzer, "id": K.neue_id(),
                                  "baue": {"mapper": GRUBE_MAPPER, "x": q[0], "y": q[1], "groesse": 1, "richtung": 0}}]}, 2.0,
                    bis="BAUE")
        time.sleep(1.5)
        G = gebaeude()
        return [n for n, g in G.items() if g["typ"] == GRUBE_TYP and g["besitzer"] == besitzer and (g["x"], g["y"]) == q],             [l for l in z if "BAUE" in l or "logik" in l][-2:]
    h0 = holz(besitzer)
    gr, antwort = baue_grube(p)
    pruefe(1, "Grube bei %s: %s, Holz %d -> %d, Modul: %s" % (p, gr, h0, holz(besitzer), antwort), bool(gr))
    if not gr:
        K.sende({"befehle": [{"player": 1, "id": K.neue_id(), "pause": True}]}, 1.0)
        return 1
    # 3 feindliche Assassine ueber die Grube
    a1 = setze(feind, ASSASSINE, x0, y)
    time.sleep(0.5)
    laufe(feind, a1, (x0 + 12, y))
    r1 = verfolge(a1, (x0 + 12, y))
    G = gebaeude()
    noch = [n for n, g in G.items() if g["typ"] == GRUBE_TYP and (g["x"], g["y"]) == p]
    tot = bool(r1) and r1[-1][3] <= 0
    pruefe(3, "mit Grube: Leben %s -> %s, tot %s, Grube danach %s, Verlauf %s" % (
        r1[0][3] if r1 else None, r1[-1][3] if r1 else None, tot, "steht" if noch else "weg",
        [(s_[0], s_[1], s_[3]) for s_ in r1][::max(1, len(r1) // 12)]),
           bool(r1) and (tot or r1[-1][3] < r1[0][3] / 2.0))
    weg = (x0 + 12, y + 30)
    if r1 and r1[-1][3] > 0:
        laufe(feind, a1, weg)                 # ueberlebt: weit weg, damit sie die naechsten Faelle nicht stoert
    # 2 Gegenprobe ohne Grube: 8 Reihen tiefer, gleiche Strecke
    yg = next((yy for yy in (y + 8, y - 8, y + 12, y - 12) if reihe_frei(x0, yy, 14)), None)
    if yg is None:
        pruefe(2, "keine freie Reihe fuer die Gegenprobe", False)
    else:
        a0 = setze(feind, ASSASSINE, x0, yg)
        time.sleep(0.5)
        laufe(feind, a0, (x0 + 12, yg))
        r0 = verfolge(a0, (x0 + 12, yg))
        voll = r0[0][3] if r0 else None
        pruefe(2, "ohne Grube (y=%d): Leben %s -> %s, Ende bei %s" % (yg, voll, r0[-1][3] if r0 else None,
                                                                   r0[-1][1:3] if r0 else None),
               bool(r0) and r0[-1][3] == voll and r0[-1][1] is not None and abs(r0[-1][1] - (x0 + 12)) <= 1)
        laufe(feind, a0, weg)
    time.sleep(2.0)
    # 4 eigene Assassine ueber die (noch stehende oder eine neue) Grube
    if not noch:
        noch, _ = baue_grube(p)
    a2 = setze(besitzer, ASSASSINE, x0, y)
    time.sleep(0.5)
    laufe(besitzer, a2, (x0 + 12, y))
    r2 = verfolge(a2, (x0 + 12, y))
    G = gebaeude()
    noch2 = [n for n, g in G.items() if g["typ"] == GRUBE_TYP and (g["x"], g["y"]) == p]
    pruefe(4, "eigene Assassine ueber die eigene Grube (Grube vorher %s): Leben %s -> %s, Grube danach %s" % (
        "steht" if noch else "fehlt", r2[0][3] if r2 else None, r2[-1][3] if r2 else None, "steht" if noch2 else "weg"),
           bool(noch) and bool(r2) and r2[-1][3] == r2[0][3] and r2[-1][1] is not None)
    K.sende({"befehle": [{"player": 1, "id": K.neue_id(), "pause": True}]}, 1.0)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
