# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer schussfeld.py (Daniel 12.10. 01:03/01:08: sicherster Weg, der trotzdem der kuerzeste ist; toter
Winkel). Vorher festgelegt, was gelten muss:
  1. Freies Gelaende, 3 Bogenschuetzen (Reichweite 40) mitten auf der Geraden Start -> Ziel: der Weg hat Belastung 0, die
     Gerade Belastung > 0, es gibt Wegpunkte, kein Wegpunkt liegt in Reichweite eines Schuetzen.
  2. Derselbe Fall: der Umweg ist hoechstens so lang wie noetig - kein Wegpunkt weiter als 60 Felder von der Geraden weg.
  3. Keine Schuetzen: keine Wegpunkte (die Gerade ist schon sicher).
  4. Mauer aus Wasser (nicht begehbar) mit einer Luecke: der Weg geht durch die Luecke.
  5. Schuetzen-Ring ohne Luecke um das Ziel: Weg wird trotzdem gefunden (Ziel bleibt erreichbar), Belastung > 0, aber
     nicht groesser als die Gerade.
Gegenprobe: mit GEWICHT 0 muss Fall 1 rot werden (der Weg geht dann gerade durch die Schuetzen).
Aufruf: uv run python -m selfaware.tools.checks.schussfeld_pruefen [gewicht]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.services.schussfeld as S


def leer():
    return ["G" * 400 for _ in range(400)]


def main():
    gew = float(sys.argv[1]) if len(sys.argv) > 1 else S.GEWICHT
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    start, ziel = (60, 200), (300, 200)
    sch = [((180, 200), 40), ((180, 190), 40), ((180, 210), 40)]
    g = S.Gitter(leer(), sch)
    zellen = g.weg(start, ziel, gewicht=gew)
    wp = S.wegpunkte(g, zellen, ziel)
    bw, bg = g.belastung(zellen), g.belastung(g.gerade(start, ziel))
    in_reichweite = [p for p in wp[:-1] if S.gefahr_am(p, sch)]
    pruefe(1, "Schuetzen auf der Geraden: Belastung Weg %d, Gerade %d, %d Wegpunkte, in Reichweite %s" % (bw, bg, len(wp), in_reichweite),
           bw == 0 and bg > 0 and len(wp) > 1 and not in_reichweite)
    weit = max((abs(p[1] - 200) for p in wp), default=0)
    pruefe(2, "Umweg nicht weiter als noetig: groesste Abweichung von der Geraden %d Felder" % weit, weit <= 60)
    g0 = S.Gitter(leer(), [])
    wp0, b0w, b0g, _ = S.sicherer_weg(leer(), {}, 1, start, ziel, gitter=g0)
    pruefe(3, "keine Schuetzen: Wegpunkte %s" % wp0, wp0 == [])
    gel = leer()
    for y in range(400):
        if not 190 <= y <= 200:
            gel[y] = gel[y][:150] + "W" * 8 + gel[y][158:]
    gw = S.Gitter(gel, [])
    zw = gw.weg(start, ziel, gewicht=gew)
    durch = [gw.mitte(c) for c in zw if 150 <= gw.mitte(c)[0] < 158]
    pruefe(4, "Wassermauer mit Luecke y 190-200: Weg quert bei %s" % durch[:3],
           zw is not None and durch and all(186 <= p[1] <= 204 for p in durch))
    ring = [((ziel[0] + dx, ziel[1] + dy), 40) for dx, dy in ((-30, 0), (30, 0), (0, -30), (0, 30))]
    gr = S.Gitter(leer(), ring)
    zr = gr.weg(start, ziel, gewicht=gew)
    pruefe(5, "Ring um das Ziel: Weg %s, Belastung %s (Gerade %d)" % ("gefunden" if zr else "keiner",
                                                                   gr.belastung(zr) if zr else None, gr.belastung(gr.gerade(start, ziel))),
           zr is not None and 0 < gr.belastung(zr) <= gr.belastung(gr.gerade(start, ziel)))
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
