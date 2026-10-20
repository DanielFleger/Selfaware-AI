# -*- coding: utf-8 -*-
"""Wie schnell folgt eine Einheit einem neuen Befehl - bis hin zu jedem Tick? (04.10.2026)

Daniel: "wie schnell kannst du sie befehlen, koenntest du sie jeden Tick live die Richtung
aendern lassen? Damit waere es moeglich, Steinen oder Geschossen auszuweichen."
Modulbefehl "zickzack": die Einheit bekommt alle K Ticks abwechselnd Ziel B (rechts) und A
(links); jeden Tick wird ihre Feinposition (8 je Feld) mitgeschrieben.
Vorher festgelegt, je K (aus demselben Spielstand, Laden ist wiederholbar):
  REAKTION   Ticks vom Befehl bis die Feinposition sich erstmals in die NEUE Richtung bewegt
             (Median und Hoechstwert ueber alle Wechsel)
  FOLGT      die Einheit bewegt sich in den K Ticks nach einem Befehl ueberhaupt in dessen Richtung
  BEWEGUNG   Anteil der Ticks mit veraenderter Feinposition
Aufruf:  uv run python -m selfaware.tools.experiments.zickzack "<Spielstand>" <einheit> [K ...]     z. B. "M7-04 Mensch Grumpy T600" 147 50 10 5 2 1
"""

from selfaware import workspace as _workspace
import io, json, os, re, sys, time

from selfaware.game.ucp.befehl import LOG
from selfaware.game.ucp.laden import lade_stand, befehl
from selfaware.game.ucp.steuerkarte import laufe
from selfaware.tools.experiments.einheiten_steuern import liste

ZZ = re.compile(r"ZZ (\d+) (-?\d+) (-?\d+) (-?\d+) (-?\d+)( BEFEHL->\((\d+),(\d+)\))?")

def lauf(stand, nr, k, ticks=200):
    lade_stand(stand, mit_bild=False)
    _, _, x, y = liste(nr=[nr])[0]
    a, b = [x - 6, y], [x + 6, y]
    pos = os.path.getsize(LOG)
    befehl({"zickzack": {"nr": nr, "a": a, "b": b, "alle": k, "ticks": ticks}}, 0.8)
    befehl({"tempo": 300}, 0.5)
    laufe(ticks + 5)
    with io.open(LOG, encoding="utf-8", errors="replace") as f:
        f.seek(pos); text = f.read()
    zeilen = [m for m in (ZZ.search(z) for z in text.splitlines()) if m]
    reihe = [(int(m.group(1)), int(m.group(2)), int(m.group(5)) if False else int(m.group(4)),
              (int(m.group(7)), int(m.group(8))) if m.group(6) else None) for m in zeilen]
    # reihe: (tick, feinX, zielX, befehl)
    reaktionen, folgt, bewegt = [], 0, 0
    for i, (t, fx, zx, bef) in enumerate(reihe):
        if i > 0 and fx != reihe[i - 1][1]:
            bewegt += 1
        if bef is None:
            continue
        richtung = 1 if bef[0] > x else -1
        for j in range(i + 1, min(i + 1 + max(k, 1) + 60, len(reihe))):
            d = reihe[j][1] - reihe[j - 1][1]
            if d * richtung > 0:
                reaktionen.append(reihe[j][0] - t)
                if reihe[j][0] - t <= k:
                    folgt += 1
                break
    befehle = sum(1 for r in reihe if r[3])
    reaktionen.sort()
    erg = {"K": k, "befehle": befehle, "reaktion_median": reaktionen[len(reaktionen) // 2] if reaktionen else None,
           "reaktion_max": max(reaktionen) if reaktionen else None, "reaktion_min": min(reaktionen) if reaktionen else None,
           "folgt_binnen_K": folgt, "ticks": len(reihe), "ticks_mit_bewegung": bewegt,
           "reihe": reihe}
    print("K=%-3d Befehle %3d | Reaktion min/median/max %s/%s/%s Ticks | folgt binnen K: %d von %d | bewegt in %d von %d Ticks" % (
        k, befehle, erg["reaktion_min"], erg["reaktion_median"], erg["reaktion_max"], folgt, befehle, bewegt, len(reihe)), flush=True)
    return erg

def main():
    stand, nr = sys.argv[1], int(sys.argv[2])
    ks = [int(v) for v in sys.argv[3:]] or [50, 10, 5, 2, 1]
    ergebnisse = [lauf(stand, nr, k) for k in ks]
    io.open(os.path.join(_workspace.DATA, 'zickzack_%s.json' % time.strftime('%H%M%S')), "w", encoding="utf-8").write(
        json.dumps({"stand": stand, "einheit": nr, "laeufe": ergebnisse}, indent=1, default=list))

if __name__ == "__main__":
    main()
