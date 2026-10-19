# -*- coding: utf-8 -*-
"""M7.03 Verlusttest: verliert Speichern und Wiederladen etwas?

Ablauf (alles im Hintergrund, ohne Klick):
 1. M7-01 laden (Tick 1100), genau 100 Ticks laufen lassen -> Tick 1200, Pause.
 2. Schnappschuss A  (11 Speicherbereiche, wie {"abzug"}).
 3. Speichern als "M7-03 Verlusttest Grumpy T1200".
 4. Schnappschuss A2 - veraendert das Speichern selbst etwas?
 5. M7-01 laden (anderer Stand) - der Speicher wird ueberschrieben. Schnappschuss Z.
 6. M7-03 laden -> muss Tick 1200 sein. Schnappschuss B.

Vorher festgelegt, was gilt:
  A gegen A2: Speichern darf nichts veraendern.
  A gegen B : "verlustfrei in diesen 11 Bereichen" nur, wenn ausser dem bekannten
              Rauschen (Uhr-Felder aus der Kontrolle vom 30.09.) nichts abweicht.
              Jede andere Abweichung widerlegt es und wird aufgelistet.
  A gegen Z : Gegenprobe - muss sich stark unterscheiden, sonst misst der Vergleich nichts.

Aufruf:  uv run python -m selfaware.tools.experiments.verlusttest
"""

from selfaware import workspace as _workspace
import io, json, os, sys, time

from selfaware.game.ucp.laden import lade_stand, befehl, peek, TICK
from selfaware.game.ucp.speichern import speichere
from selfaware.game.ucp.steuerkarte import laufe, SATZ
from selfaware.tools.experiments.wirkung import lade, SAETZE

M701 = "M7-01 Speichertest Grumpy T1100"
M703 = "M7-03 Verlusttest Grumpy T1200"
# Bekanntes Rauschen (wirkung.py, 30.09.): +0x8, +0x8C, +0xBC und Spieler 1 +0x34 wichen zwischen zwei
# gleichen Kontroll-Laeufen ab; +0xAC nur in den Feld-Laeufen - vorsichtshalber mitgezaehlt.
RAUSCHEN = {("kern", 0x8), ("kern", 0x8C), ("kern", 0xAC), ("kern", 0xBC), ("spieler", 1 * SATZ + 0x34)}
DATEN = os.path.join(_workspace.DATA)

def schnappschuss(name):
    befehl({"abzug": name}, 1.5)
    d = lade(name)
    if len(d) != 11:
        raise RuntimeError("Schnappschuss %s unvollstaendig: %d Bereiche" % (name, len(d)))
    return d

def stelle(ber, off):
    if ber in SAETZE:
        kopf, satz = SAETZE[ber]
        o = off - kopf
        if o >= 0:
            return "%s%d+0x%X" % (ber[:3], o // satz, o % satz)
    return "%s+0x%X" % (ber, off)

def vergleiche(a, b):
    erg = {}
    for ber in sorted(a):
        x, y = a[ber], b.get(ber, ())
        n = min(len(x), len(y))
        diffs = [(i * 4, x[i], y[i]) for i in range(n) if x[i] != y[i]]
        echt = [d for d in diffs if (ber, d[0]) not in RAUSCHEN]
        erg[ber] = {"abweichend": len(echt), "rauschen": len(diffs) - len(echt),
                    "woerter": [len(x), len(y)],
                    "stellen": [[stelle(ber, o), p, q] for o, p, q in echt[:500]]}
    return erg

def summe(v):
    return sum(r["abweichend"] for r in v.values())

def zeige(titel, v):
    print("%s: %d abweichende Woerter ausser Rauschen" % (titel, summe(v)), flush=True)
    for ber, r in v.items():
        if r["abweichend"] or r["rauschen"] or r["woerter"][0] != r["woerter"][1]:
            print("   %-10s %6d abweichend, %d Rauschen, Laenge %s  %s" % (
                ber, r["abweichend"], r["rauschen"], r["woerter"],
                "; ".join("%s: %d->%d" % tuple(s) for s in r["stellen"][:4])), flush=True)

def main():
    s = time.strftime("%H%M%S")
    bericht = {"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "stempel": s}

    print("== 1. M7-01 laden und 100 Ticks laufen", flush=True)
    lade_stand(M701, mit_bild=False)
    t = laufe(100)
    if t != 1200 or peek(TICK)[0] != 1200:
        raise RuntimeError("Tick 1200 nicht erreicht (%s)" % t)
    print("== 2. Schnappschuss A bei Tick 1200", flush=True)
    A = schnappschuss("m703_%s_A" % s)
    print("== 3. Speichern", flush=True)
    bericht["kopie"] = speichere(M703)
    print("== 4. Schnappschuss A2 nach dem Speichern", flush=True)
    A2 = schnappschuss("m703_%s_A2" % s)
    print("== 5. anderer Stand dazwischen (M7-01)", flush=True)
    lade_stand(M701, mit_bild=False)
    Z = schnappschuss("m703_%s_Z" % s)
    print("== 6. M7-03 wieder laden", flush=True)
    tb = lade_stand(M703)
    bericht["tick_nach_laden"] = tb
    B = schnappschuss("m703_%s_B" % s)

    bericht["A_gegen_A2"] = vergleiche(A, A2)
    bericht["A_gegen_B"] = vergleiche(A, B)
    bericht["A_gegen_Z"] = vergleiche(A, Z)
    io.open(os.path.join(DATEN, "verlusttest_%s.json" % s), "w", encoding="utf-8").write(
        json.dumps(bericht, ensure_ascii=False, indent=1))

    print("\nTick nach dem Laden: %d (gespeichert bei 1200)" % tb)
    zeige("A gegen A2 (veraendert Speichern etwas?)", bericht["A_gegen_A2"])
    zeige("A gegen Z  (Gegenprobe, muss stark abweichen)", bericht["A_gegen_Z"])
    zeige("A gegen B  (verlustfrei?)", bericht["A_gegen_B"])
    gegen = summe(bericht["A_gegen_Z"])
    verlust = summe(bericht["A_gegen_B"])
    if gegen < 100:
        print("URTEIL: KEINE AUSSAGE - die Gegenprobe weicht kaum ab (%d), der Vergleich misst nichts" % gegen)
    elif verlust == 0 and tb == 1200:
        print("URTEIL: verlustfrei in diesen 11 Bereichen (3,6 MB) - ausser dem bekannten Rauschen gleich")
    else:
        print("URTEIL: NICHT verlustfrei - %d abweichende Woerter (Liste oben und in verlusttest_%s.json)" % (verlust, s))

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print("ABBRUCH:", e); sys.exit(1)
