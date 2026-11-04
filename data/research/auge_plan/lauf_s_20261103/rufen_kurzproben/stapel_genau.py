# -*- coding: utf-8 -*-
"""Daniels Frage: Entwirren sie sich nach rund 1.000 Takten? Vom letzten Befehl aus gerechnet: erster Takt mit weniger als 8, erster Takt mit jedem einzeln."""
import collections
import punkte_lesen as pl

for szene, posten, letzter in (("sonder23", "punkt_einzeln", 0), ("sonder24_g", "punkt_halten", 1000)):
    p = pl.neueste(szene)
    plan = pl.plan_von(p)
    S = plan["von"]
    wer = [e for e in plan["einheiten"] if e.get("posten") == posten]
    reihe = []
    for t, u in pl.stand(p, "DAT_UnitsState", {"mx": "units[].microXPosition", "my": "units[].microYPosition"}):
        c = collections.Counter((int(u["mx"][e["nr"]]) // 8, int(u["my"][e["nr"]]) // 8) for e in wer)
        reihe.append((t - S, c.most_common(1)[0][1], len(c)))
    voll = [t for t, m, _ in reihe if m == 8]
    erst8, letzt8 = (voll[0], voll[-1]) if voll else (None, None)
    allein = next((t for t, m, _ in reihe if m == 1 and t > (letzt8 or 0)), None)
    print(szene, posten, "Zahl", len(wer), "8 auf einem Feld von", erst8, "bis", letzt8, "jeder einzeln ab", allein, "letzter Befehl", letzter,
          "| nach letztem Befehl: Stapel haelt", (letzt8 - letzter) if letzt8 else None, "ganz auseinander", (allein - letzter) if allein else None)
    print("   Verlauf (Takt, meiste auf einem Feld) ab da:", [(t, m) for t, m, _ in reihe if t >= (letzt8 or 0)][:1], [q for q in pl.wechsel([(t, m) for t, m, _ in reihe if t >= (letzt8 or 0)])][:14])
