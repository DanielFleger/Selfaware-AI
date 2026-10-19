# -*- coding: utf-8 -*-
"""M7.03 eingrenzen: Ist der geladene Stand B "A plus ein Tick"?

Anlass: verlusttest.py (30.09., 23:28) fand 1.655 abweichende Woerter zwischen
A (Tick 1200, vor dem Speichern) und B (nach dem Wiederladen, Tick 1200) - viele
davon genau um eins weiter (Zeitstempel 1200 -> 1201).

Vorher festgelegt:
  B  gegen B2 : zweimal dieselbe Datei laden muss gleich sein (sonst ist Laden unzuverlaessig).
  A  gegen A' : zweimal "M7-01 laden + 100 Ticks" muss gleich sein (sonst ist der Lauf nicht wiederholbar
                und A taugt nicht als Massstab).
  B  gegen A'1: ist B = A plus ein Tick? Deutlich weniger Abweichungen als B gegen A stuetzt das;
                gleich viele oder mehr widerlegen es.
  B1 gegen A'2: dasselbe einen Tick spaeter (bleibt der Versatz bei genau einem Tick?).

Aufruf:  uv run python -m selfaware.tools.analysis.verlust_eingrenzen <stempel des verlusttests, z. B. 232853>
"""
import io, json, os, sys, time

from selfaware.game.ucp.laden import lade_stand, peek, TICK
from selfaware.game.ucp.steuerkarte import laufe
from selfaware.tools.experiments.wirkung import lade
from selfaware.tools.experiments.verlusttest import schnappschuss, vergleiche, summe, zeige, M701, M703, DATEN

def lauf_zu(ziel):
    t = laufe(ziel - peek(TICK)[0])
    if t != ziel or peek(TICK)[0] != ziel:
        raise RuntimeError("Tick %d nicht erreicht (%s)" % (ziel, t))

def main():
    alt = sys.argv[1]
    s = time.strftime("%H%M%S")
    A, B = lade("m703_%s_A" % alt), lade("m703_%s_B" % alt)
    if len(A) != 11 or len(B) != 11:
        raise RuntimeError("Schnappschuesse A/B von %s fehlen" % alt)

    print("== M7-03 noch einmal laden -> B2, dann 1 Tick -> B1", flush=True)
    lade_stand(M703, mit_bild=False)
    B2 = schnappschuss("m703e_%s_B2" % s)
    lauf_zu(1201)
    B1 = schnappschuss("m703e_%s_B1" % s)
    print("== M7-01 laden, 100 Ticks -> A', dann 1 Tick -> A'1, dann 1 Tick -> A'2", flush=True)
    lade_stand(M701, mit_bild=False)
    lauf_zu(1200)
    A_ = schnappschuss("m703e_%s_Astrich" % s)
    lauf_zu(1201)
    A1 = schnappschuss("m703e_%s_Astrich1" % s)
    lauf_zu(1202)
    A2 = schnappschuss("m703e_%s_Astrich2" % s)

    paare = [("B gegen B2 (zweimal laden)", B, B2), ("A gegen A' (zweimal laufen)", A, A_),
             ("B gegen A (Verlusttest)", B, A), ("B gegen A'1 (A plus ein Tick?)", B, A1),
             ("B1 gegen A'2 (einen Tick spaeter)", B1, A2), ("B1 gegen A'1 (gleicher Tickzaehler)", B1, A1)]
    bericht = {"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "aus_verlusttest": alt}
    for titel, x, y in paare:
        v = vergleiche(x, y)
        bericht[titel] = v
        zeige(titel, v)
    io.open(os.path.join(DATEN, "verlust_eingrenzen_%s.json" % s), "w", encoding="utf-8").write(
        json.dumps(bericht, ensure_ascii=False, indent=1))
    print("Bericht: data/research/verlust_eingrenzen_%s.json" % s)

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print("ABBRUCH:", e); sys.exit(1)
