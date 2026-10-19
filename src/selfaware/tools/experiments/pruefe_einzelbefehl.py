# -*- coding: utf-8 -*-
"""Totschlagtest: bekommt jeder Angriffsbefehl genau seine Einheiten - und keine sonst? (04.10.2026, 23:58)

Anlass: In Partie 9c steckten am Ende 78 Assassinen, alle Bogenschuetzen, Speertraeger und der Lord in Gruppe 1249
und folgten einem Befehl, der nur EINEM Assassinen galt (Auswahlmarken +178/+180 blieben stehen).

Ablauf am laufenden Spiel (Spieler 1, Assassinen vorhanden):
  1. Lagebild vorher: Gruppe und Laufziel jeder eigenen Einheit.
  2. <n> Assassinen, je EINER, in EINEM Befehlspaket auf <n> verschiedene erreichbare Feindgebaeude.
  3. <ticks> Ticks laufen lassen, Lagebild nachher.
Widerlegt (ROT), wenn
  - eine der uebrigen Einheiten ihre Gruppe wechselt oder ein neues Laufziel bei einem der Testziele bekommt, oder
  - zwei Testeinheiten in derselben Gruppe landen, oder
  - eine Testeinheit nicht bei ihrem eigenen Gebaeude ankommt bzw. dorthin laeuft.

Aufruf:  uv run python -m selfaware.tools.experiments.pruefe_einzelbefehl [n=3] [ticks=100]
"""
import os, sys

from selfaware.game.ucp.laden import befehl
from selfaware.game.ucp.befehl import sende, neue_id, ABZUG
from selfaware.micro.tasks.assassinen import WERT
from selfaware.micro.tasks.waechter import lies_lagebild, lies_gebaeude, schach
from selfaware.game.ucp.steuerkarte import laufe

LAGEBILD = os.path.join(ABZUG, "lagebild.txt")
WIRTSCHAFT = set(WERT)   # dieselben Wirtschaftsgebaeude wie der Assassinen-Lenker


def gruppen():
    """nr -> (gruppe, laufx, laufy, zielart) aus den neuen Lagebild-Spalten."""
    G = {}
    for z in open(LAGEBILD).read().split("\n")[2:]:
        w = z.split()
        if len(w) >= 20 and int(w[1]) == 1:
            G[int(w[0])] = (int(w[18]), int(w[14]), int(w[15]), int(w[7]), int(w[2]))
    return G


def main():
    arg = dict(a.split("=") for a in sys.argv[1:])
    n, ticks = int(arg.get("n", 3)), int(arg.get("ticks", 100))
    befehl({"lagebild": True}, 1.5, bis="LAGEBILD")
    vorher = gruppen()
    L = lies_lagebild(neu_holen=False)
    geb = lies_gebaeude()
    assa = sorted(nr for nr, e in L.items() if e["besitzer"] == 1 and e["typ"] == 73)
    ziele = sorted((g for g, b in geb.items() if b["besitzer"] == 2 and b["erreichbar"] and b["typ"] in WIRTSCHAFT),
                   key=lambda g: (geb[g]["x"], geb[g]["y"]))
    if len(assa) < n or len(ziele) < n:
        print("TEST NICHT MOEGLICH: %d Assassinen, %d Ziele" % (len(assa), len(ziele))); sys.exit(2)
    # Ziele moeglichst weit auseinander: gleichmaessig aus der Liste
    wahl_ziele = [ziele[i * (len(ziele) - 1) // max(1, n - 1)] for i in range(n)]
    wahl = list(zip(assa[:n], wahl_ziele))
    print("Test:", ", ".join("Assassine %d -> Gebaeude %d Typ %d bei (%d,%d)" % (a, g, geb[g]["typ"], geb[g]["x"], geb[g]["y"])
                              for a, g in wahl))
    # ein Paket wie im Lenker (erstes_spiel.py): alle Befehle im selben Takt
    antwort = sende({"befehle": [{"angriff": {"einheiten": [a], "gebaeude": g}, "player": 1, "id": neue_id()}
                                 for a, g in wahl]}, 2.0, bis="Befehlen ausgefuehrt")
    print("\n".join(z for z in antwort if "ANGRIFF" in z or "Befehlen" in z))
    laufe(ticks)
    befehl({"lagebild": True}, 1.5, bis="LAGEBILD")
    nachher = gruppen()
    rot = []
    test = {a for a, _ in wahl}
    testgruppen = {}
    for a, g in wahl:
        if a not in nachher:
            rot.append("Testeinheit %d ist weg" % a); continue
        gr, lx, ly, za, _ = nachher[a]
        testgruppen.setdefault(gr, []).append(a)
        d = schach((lx, ly), (geb[g]["x"], geb[g]["y"]))
        print("  Testeinheit %d: Gruppe %d (vorher %d), Laufziel (%d,%d) = %d Felder von Gebaeude %d, Zielart %d" % (
            a, gr, vorher.get(a, (-1,))[0], lx, ly, d, g, za))
        if d > 6:
            rot.append("Testeinheit %d laeuft nicht zu ihrem Gebaeude %d (%d Felder daneben)" % (a, g, d))
    for gr, ns in testgruppen.items():
        if len(ns) > 1:
            rot.append("Testeinheiten %s teilen sich Gruppe %d" % (ns, gr))
    mitgerissen = []
    for nr, (gr, lx, ly, za, typ) in nachher.items():
        if nr in test or nr not in vorher:
            continue
        if gr != vorher[nr][0] or any(schach((lx, ly), (geb[g]["x"], geb[g]["y"])) <= 6 and
                                      schach((vorher[nr][1], vorher[nr][2]), (geb[g]["x"], geb[g]["y"])) > 6 for _, g in wahl):
            mitgerissen.append((nr, typ, vorher[nr][0], gr))
    if mitgerissen:
        rot.append("%d uebrige Einheiten mitgerissen, z. B. %s" % (len(mitgerissen), mitgerissen[:5]))
    print("Uebrige eigene Einheiten geprueft: %d" % sum(1 for nr in nachher if nr not in test and nr in vorher))
    if rot:
        print("ROT:\n  " + "\n  ".join(rot)); sys.exit(1)
    print("GRUEN: jede Testeinheit in eigener Gruppe auf eigenem Ziel, keine andere Einheit mitgerissen")


if __name__ == "__main__":
    main()
