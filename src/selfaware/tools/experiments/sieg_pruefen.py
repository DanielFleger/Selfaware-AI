# -*- coding: utf-8 -*-
"""Pruefung nach einem Sturm (SAI 11.10.): ist der Sieg gueltig nach Daniels Regeln? Zwei unabhaengige Quellen:
  1. Protokoll (neuestes data/research/lage_*_sturm.jsonl.gz oder protokoll=<datei>): in wie vielen Runden schlug unser Lord den
     gegnerischen Lord (nahziel), wer schlug ihn ab <ab> Ticks vor seinem Tod, kleinste Beliebtheit, ist er im Protokoll tot.
  2. Spiel: Pause aufheben, bis zum Endbildschirm laufen lassen (hoechstens 30 s), dann gameOver, Ansicht, Lords,
     Gebaeude des Gegners lesen und wieder pausieren.
Gueltig = Gegner-Lord tot, 0 Runden unser Lord am gegnerischen Lord, Beliebtheit nie unter 50, Spiel gameOver 1 mit
unserem Lord am Leben. Rueckgabe 0 = gueltig, 1 = nicht.
Aufruf: SHC_INSTANZ=4 uv run python -m selfaware.tools.experiments.sieg_pruefen [protokoll=<datei>] [ab=300]"""

from selfaware import workspace as _workspace
import glob
import os
import sys
import time
from collections import Counter

import selfaware.game.ucp.befehl as kanal
from selfaware.telemetry.lageprotokoll import runden

DATEN = os.path.join(_workspace.DATA)
ART = {22: "Bogen", 23: "Armbrust", 24: "Speer", 26: "Streitkolben", 73: "Assassine", 55: "LORD"}


def protokoll_pruefen(pfad, ab=300):
    lordschlag, verlauf, tod, min_beliebt, letzte = 0, [], None, None, None
    for t, st, E, G in runden(pfad):
        g = next((e for e in E if e["typ"] == 55 and e["besitzer"] == 2), None)
        w = next((e for e in E if e["typ"] == 55 and e["besitzer"] == 1), None)
        b = st.get("beliebt")
        if b is not None:
            min_beliebt = b if min_beliebt is None else min(min_beliebt, b)
        if g is None or g["leben"] <= 0:
            tod = t
            break
        if w and w.get("nahziel") == g["nr"]:
            lordschlag += 1
        verlauf.append((t, [e["typ"] for e in E if e["besitzer"] == 1 and e.get("nahziel") == g["nr"]]))
        letzte = (t, g["leben"], max(abs(w["x"] - g["x"]), abs(w["y"] - g["y"])) if w else None)
    wer = Counter()
    if tod is not None:
        for t, typen in verlauf:
            if t >= tod - ab:
                wer.update(ART.get(x, x) for x in typen)
    return {"tod": tod, "lordschlag": lordschlag, "wer": dict(wer), "min_beliebt": min_beliebt, "letzte": letzte}


def spiel_pruefen():
    import selfaware.runtime.live.erstes_spiel as E
    from selfaware.game.ucp.laden import peek, ANSICHT
    E.befehl({"pause": False}, 0.5)
    a = g = None
    for _ in range(15):
        time.sleep(2)
        kanal.belege()
        a, g = peek(ANSICHT)[0], peek(0x0117D500)[0]
        if a != 14:
            break
    st, L, G = E.runde_lesen()
    E.befehl({"pause": True}, 0.5)
    return {"tick": st.get("t"), "ansicht": a, "gameOver": g,
            "lords": [(e["besitzer"], e["leben"]) for e in L.values() if e["typ"] == 55],
            "gegner_gebaeude": sum(1 for x in G.values() if x["besitzer"] == 2)}


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    pfad = arg.get("protokoll") or sorted(glob.glob(os.path.join(DATEN, "lage_*_sturm.jsonl.gz")))[-1]
    p = protokoll_pruefen(pfad, int(arg.get("ab", 300)))
    s = spiel_pruefen()
    gueltig = (p["tod"] is not None and p["lordschlag"] == 0 and (p["min_beliebt"] is None or p["min_beliebt"] >= 5000)
               and s["gameOver"] == 1 and any(b == 1 and l > 0 for b, l in s["lords"]))
    print("PRUEFUNG %s | %s | Protokoll: Gegner-Lord tot bei %s, unser Lord am Gegner-Lord %d Runden, Schlaege auf ihn in den "
          "letzten %s Ticks %s, Beliebtheit min %s | Spiel: Tick %s, Ansicht %s, gameOver %s, Lords %s, Gegner-Gebaeude %s" % (
              "GUELTIGER SIEG" if gueltig else "NICHT GUELTIG", os.path.basename(pfad), p["tod"], p["lordschlag"],
              arg.get("ab", 300), p["wer"], "%.1f" % (p["min_beliebt"] / 100.0) if p["min_beliebt"] is not None else "?",
              s["tick"], s["ansicht"], s["gameOver"], s["lords"], s["gegner_gebaeude"]), flush=True)
    return 0 if gueltig else 1


if __name__ == "__main__":
    kanal.belege()
    try:
        rc = main()
    finally:
        kanal.freigeben()
    raise SystemExit(rc)
