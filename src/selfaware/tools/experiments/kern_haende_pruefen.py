"""B-145 S2: die Haende des Kerns im Spiel pruefen (Instanz/Spieler ueber SHC_INSTANZ / SHC_SPIELER).

  python -m selfaware.tools.experiments.kern_haende_pruefen [Spielstand]

1. Spielstand laden (Standard: Pruefstand "B140 Burg Franz T40126"), eigenen Platz setzen, neueste Kern-Fassung laden.
2. Drei Kaempfer des Spielers dem Kern uebergeben, Laufauftrag 6 Felder nach Osten.
3. Gegenprobe A: Auftrag fuer eine NICHT uebergebene Einheit -> -4.
4. Spiel laeuft kurz: im Weltbild muessen die drei in einer neuen Gruppe stehen und ihr Laufziel = Auftrag sein;
   die nicht uebergebene Einheit hat kein solches Laufziel.
5. Gegenprobe B: derselbe Auftrag noch einmal, waehrend sie laufen -> 0 (kein Dauer-Neubefehl).
"""

import os
import sys
import time

from selfaware.tools.experiments.kern_vergleich import lesen

KAEMPFER = {22, 23, 24, 26, 70, 72, 75}
KERN = os.environ.get("SHC_KERN", "samurai_kern_6.dll")


def welt(befehl, vs):
    befehl({"kern": {"welt": True}}, 1.5, bis="KERN welt")
    _, _, e = lesen(os.path.join(vs, "kern_lagebild.txt"), True)
    return e


def main(argv=None):
    from selfaware.game.ucp.laden import PAUSE, SPIEL, TICK, befehl, lade_stand, peek

    argv = sys.argv[1:] if argv is None else argv
    stand = argv[0] if argv else "B140 Burg Franz T40126"
    sp = int(os.environ.get("SHC_SPIELER", "1"))
    vs = os.path.join(SPIEL, "ucp", "villagestudio")
    try:
        lade_stand(stand, mit_bild=False)
    except RuntimeError as e:
        print("lade_stand:", str(e)[:90])
    befehl({"eigenerPlatz": sp}, 1.0)
    print(befehl({"kern": {"laden": KERN}}, 1.5)[0])
    e = welt(befehl, vs)
    eigene = [
        nr
        for nr, z in e.items()
        if int(z["besitzer"]) == sp and int(z["typ"]) in KAEMPFER
    ]
    if len(eigene) < 4:
        print("zu wenige Kaempfer:", len(eigene))
        return 1
    drei, fremd = eigene[:3], eigene[3]
    x = int(e[drei[0]]["x"]) + 6
    y = int(e[drei[0]]["y"])
    print("drei:", drei, "Ziel", (x, y), "| nicht uebergeben:", fremd)
    print(befehl({"kern": {"uebernehmen": drei}}, 1.0)[0])
    print(befehl({"kern": {"lauf": {"einheiten": drei, "x": x, "y": y}}}, 1.0)[0])
    print("Gegenprobe A:", befehl({"kern": {"lauf": {"einheiten": [fremd], "x": x, "y": y}}}, 1.0)[0])
    t0 = peek(TICK)[0]
    befehl({"pause": False}, 1.0)
    time.sleep(1.0)
    print("Gegenprobe B:", befehl({"kern": {"lauf": {"einheiten": drei, "x": x, "y": y}}}, 1.0)[0])
    befehl({"pause": True}, 1.0)
    t1 = peek(TICK)[0]
    e2 = welt(befehl, vs)
    gut = 0
    for nr in drei:
        z = e2.get(nr)
        if z is None:
            print(nr, "lebt nicht mehr")
            continue
        ok = (int(z["laufx"]), int(z["laufy"])) == (x, y)
        gut += ok
        print(nr, "Gruppe", z["gruppe"], "Laufziel", (z["laufx"], z["laufy"]), "Zustand", z["zustand"], "OK" if ok else "")
        print("   vorher Gruppe", e[nr]["gruppe"], "Laufziel", (e[nr]["laufx"], e[nr]["laufy"]))
    zf = e2.get(fremd, {})
    print("nicht uebergeben", fremd, "Laufziel", (zf.get("laufx"), zf.get("laufy")))
    print(f"Takte {t0} -> {t1}, Pause {peek(PAUSE)[0]}: {gut} von 3 mit Laufziel des Kerns")
    return 0 if gut == 3 else 1


if __name__ == "__main__":
    sys.exit(main())
