# -*- coding: utf-8 -*-
"""1v1-Vorstufe (Daniel 19.10.2026: "1v1 Selfaware gegen sich selbst", "moeglichst nachhaltig"): wirken Befehle mit
"player": 2 fuer Spieler 2? Braucht logik.lua ab 19.10. (alsSpieler: Platz je Befehl, bis zum naechsten Takt gehalten;
Laufbefehle anderer Spieler direkt je Einheit).

Ablauf: frisches Gefecht Green Haven, wir Platz 4, ein Nomade Platz 3 (Spieler 2); sobald beide Lords stehen, die KI von
Spieler 2 aus (currentAIArray[2] = 0, PlayerData[2].aiType = 0, Mensch-Eintrag 1). Dann ALS SPIELER 2 und gemischt mit
Spieler 1 im selben Paket:
  1. Holzfaeller bauen (Spieler 2) und Holzfaeller bauen (Spieler 1) in EINEM Paket -> je der richtige Besitzer
  2. Soeldnerposten + Markt (Spieler 2), Sklave anwerben, Holz verkaufen -> Bestand von Spieler 2 aendert sich
  3. Abreissen des Holzfaellers von Spieler 2
  4. Laufbefehl fuer eine Einheit von Spieler 2 und eine von Spieler 1 im selben Paket -> beide am Ziel
  5. Angriffsbefehl fuer eine Einheit von Spieler 2 -> sie hat das Ziel
Am Ende muss der Platz (0x01A275DC) wieder 1 sein.
Aufruf (Spiel laeuft, Lenker aus): uv run python -m selfaware.tools.experiments.spieler2_pruefen"""
import re
import sys
import time
import os


import selfaware.game.ucp.befehl as kanal
from selfaware.tools.experiments.serie import zuruecksetzen
from selfaware.micro.tasks.waechter import LAGEBILD, GEBAEUDEDATEI

SLOT, AI, FULL = 0x01A275DC, 0x0191DE7C, 0x0191DE10
AITYP2 = 0x0115BDF8 + 2 * 0x39F4 + 0x2300
ok = []


def s(c, w=1.0, bis=None):
    return kanal.sende(c, w, bis=bis)


def pruefe(nr, text, bed):
    ok.append(bool(bed))
    print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)


def peek(adr):
    for z in s({"player": 1, "peek": adr, "worte": 1}):
        m = re.search(r"PEEK 0x%08X: (\w+)" % adr, z)
        if m:
            return int(m.group(1), 16)


def lauf(t=1.5):
    s({"player": 1, "pause": False}, 0.5); time.sleep(t); s({"player": 1, "pause": True}, 0.5)


def lage():
    s({"player": 1, "lagebild": True}, 1.0)
    E = {r.split()[0]: r.split() for r in open(LAGEBILD).read().split("\n")[2:] if len(r.split()) >= 16}
    G = [r.split() for r in open(GEBAEUDEDATEI).read().splitlines()[1:] if len(r.split()) > 4]
    return E, G


def vorrat(sp):
    z = " ".join(s({"player": 1, "status": sp}, 1.0, "STATUS"))
    m = re.findall(r"STATUS t=[^\[]*", z)
    st = m[-1] if m else ""
    return {k: int(v) for k, v in re.findall(r" (gold|holz|feuer)=(-?\d+)", st)}


def frei(sp, mapper, groesse, x, y, schon=()):
    z = " ".join(s({"player": sp, "platzsuche": {"spieler": sp, "mapper": mapper, "groesse": groesse, "x": x, "y": y, "r": 25, "max": 12}},
                   2.0, "PLATZSUCHE"))
    for p in re.findall(r"\((\d+),(\d+)\)", z.split("geprueft:")[-1]):
        p = tuple(map(int, p))
        if all(max(abs(p[0] - q[0]), abs(p[1] - q[1])) > 5 for q in schon):
            return p


def an(G, p):
    return [int(g[1]) for g in G if (int(g[3]), int(g[4])) == p]


def lords():
    return re.findall(r"LORD \d+: Spieler (\d+) bei \((\d+),(\d+)\)", " ".join(s({"player": 1, "lords": True}, 1.0, "LORDS")))


def main():
    print("Zuruecksetzen:", zuruecksetzen(), flush=True)
    start = [246] * 8
    start[4], start[3] = 0, 1
    s({"eigenesGefecht": True, "karte": "Green Haven", "ki": 7, "gegner": 1, "ausgleich": 3, "startliste": start}, 4,
      bis="LaunchSkirmishGame zurueck")
    s({"player": 1, "tempo": 300}, 1.0, "TEMPO")
    s({"player": 1, "pause": False}, 0.5)
    t0 = time.time()
    while time.time() - t0 < 60 and len(lords()) < 2:
        time.sleep(0.5)
    s({"player": 1, "pause": True}, 0.5)
    s({"player": 1, "eigenerPlatz": 1}, 0.8)
    for adr, wert in ((AI + 8, 0), (AITYP2, 0), (FULL + 8, 1)):
        s({"player": 1, "poke": adr, "wert": wert}, 1.0, "POKE")
    E, G = lage()
    lord2 = [(int(x), int(y)) for sp, x, y in lords() if sp == "2"][0]
    lord1 = [(int(x), int(y)) for sp, x, y in lords() if sp == "1"][0]
    belegt = [(int(g[3]), int(g[4])) for g in G]
    # 1
    a2 = frei(2, 51, 3, lord2[0] - 20, lord2[1] + 25, belegt)
    b1 = frei(1, 51, 3, lord1[0] + 10, lord1[1] + 20, belegt)
    s({"befehle": [{"player": 2, "id": kanal.neue_id(), "baue": {"mapper": 51, "x": a2[0], "y": a2[1], "groesse": 3}},
                   {"player": 1, "id": kanal.neue_id(), "baue": {"mapper": 51, "x": b1[0], "y": b1[1], "groesse": 3}}]}, 1.5)
    lauf()
    E, G = lage()
    pruefe(1, "ein Paket: Holzfaeller fuer Spieler 2 an %s -> Besitzer %s, fuer Spieler 1 an %s -> Besitzer %s" % (
        a2, an(G, a2), b1, an(G, b1)), an(G, a2) == [2] and an(G, b1) == [1])
    # 2
    pp = frei(2, 86, 5, lord2[0] - 10, lord2[1] - 12, belegt + [a2])
    pm = frei(2, 77, 5, lord2[0] + 14, lord2[1] - 12, belegt + [a2, pp])
    s({"befehle": [{"player": 2, "id": kanal.neue_id(), "baue": {"mapper": 86, "x": pp[0], "y": pp[1], "groesse": 5}},
                   {"player": 2, "id": kanal.neue_id(), "baue": {"mapper": 77, "x": pm[0], "y": pm[1], "groesse": 5}}]}, 1.5)
    lauf()
    E, G = lage()
    posten = [int(g[0]) for g in G if g[1] == "2" and g[2] == "8"]
    markt = [int(g[0]) for g in G if g[1] == "2" and g[2] == "26"]
    v0 = vorrat(2)
    sklaven0 = sum(1 for e in E.values() if e[1] == "2" and e[2] == "71")
    if posten:
        s({"player": 2, "werbe": {"typ": 71, "gebaeude": posten[0]}}, 1.0, "WERBE")
    if markt:
        s({"player": 2, "spielbefehl": {"nr": 38, "werte": [1, 2]}}, 1.0, "SPIELBEFEHL")       # 1 = verkaufen, 2 = Holz
    lauf()
    E, G = lage()
    v1 = vorrat(2)
    sklaven1 = sum(1 for e in E.values() if e[1] == "2" and e[2] == "71")
    pruefe(2, "Spieler 2: Soeldnerposten %s, Markt %s; Sklaven %d -> %d; Holz %s -> %s, Gold %s -> %s" % (
        posten, markt, sklaven0, sklaven1, v0.get("holz"), v1.get("holz"), v0.get("gold"), v1.get("gold")),
        posten and markt and sklaven1 > sklaven0 and v1.get("holz", 0) < v0.get("holz", 0))
    # 3
    hf = [int(g[0]) for g in G if g[1] == "2" and g[2] == "3"]
    if hf:
        s({"player": 2, "abreissen": {"nr": hf[0]}}, 1.0, "ABREISSEN")
        lauf()
        E, G = lage()
    pruefe(3, "Abriss des Holzfaellers %s von Spieler 2: steht noch %s" % (hf[:1], [g[0] for g in G if hf and g[0] == str(hf[0])]),
           hf and not [g for g in G if g[0] == str(hf[0]) and g[1] == "2"])
    # 4
    # Kampfeinheit, kein Sklave: ein Sklave des Nomaden kehrt nach einem einmaligen Laufziel von selbst um (gemessen 19.10.;
    # nur der Haltebefehl - jeden Takt neu gesetzt - brachte ihn ans Ziel)
    e2 = [k for k, e in E.items() if e[1] == "2" and e[2] in ("70", "72", "76", "73", "75")]
    e1 = [k for k, e in E.items() if e[1] == "1" and e[2] in ("22", "24", "71", "26")]
    if e2 and e1:
        n2, n1 = e2[0], e1[0]
        # Ziele auf freiem Boden (Bauplatz frei laut Spiel), ~12 Felder weit - nicht in die Burg
        z2 = list(frei(2, 51, 3, int(E[n2][3]) - 12, int(E[n2][4]) + 12) or (int(E[n2][3]), int(E[n2][4])))
        z1 = list(frei(1, 51, 3, int(E[n1][3]) + 12, int(E[n1][4]) + 12) or (int(E[n1][3]), int(E[n1][4])))
        s({"befehle": [{"player": 2, "id": kanal.neue_id(), "angriff": {"einheiten": [int(n2)], "lauf": z2}},
                       {"player": 1, "id": kanal.neue_id(), "angriff": {"einheiten": [int(n1)], "lauf": z1}}]}, 1.5)
        lauf(4.0)
        E, G = lage()
        pruefe(4, "Laufbefehle im selben Paket: Spieler 2 Einheit %s jetzt %s (Ziel %s), Spieler 1 Einheit %s jetzt %s (Ziel %s)" % (
            n2, E[n2][3:5], z2, n1, E[n1][3:5], z1),
            max(abs(int(E[n2][3]) - z2[0]), abs(int(E[n2][4]) - z2[1])) <= 2 and max(abs(int(E[n1][3]) - z1[0]), abs(int(E[n1][4]) - z1[1])) <= 2)
        # 5
        ziel = e1[0]
        s({"player": 2, "angriff": {"einheiten": [int(n2)], "ziel": int(ziel)}}, 1.0, "ANGRIFF")
        lauf(2.0)
        E, G = lage()
        pruefe(5, "Angriff: Einheit %s von Spieler 2 hat Zieleinheit %s (soll %s)" % (n2, E[n2][8], ziel), E[n2][8] == ziel)
    else:
        pruefe(4, "keine Einheiten zum Pruefen (Spieler 2: %d, Spieler 1: %d)" % (len(e2), len(e1)), False)
    pruefe(6, "Platz am Ende %s" % peek(SLOT), peek(SLOT) == 1)
    print("%d von %d gruen" % (sum(ok), len(ok)), flush=True)
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
