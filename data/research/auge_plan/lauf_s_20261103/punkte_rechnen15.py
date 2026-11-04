# -*- coding: utf-8 -*-
"""B-142: Greifen die Kaefighunde an? Je Posten die Opfer: erster Verlust und Tote. Die Hunde gehoeren laut Aufzeichnung Besitzer 0.

  PYTHONPATH="src;data/research/auge_plan/lauf_s_20261103" python data/research/auge_plan/lauf_s_20261103/punkte_rechnen15.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung15.txt
"""
import punkte_lesen as pl
from selfaware.tools.analysis import auge_regeln as ar

U = {"da": "units[].logicalState", "typ": "units[].unitType", "l": "units[].health", "z": ("units[].logicalState", ar.ZUSTAND_ABSTAND)}
for szene, posten, zahl in (("sonder3_g", "hunde", 3), ("sonder19_g", "hunde4", 4), ("sonder20_g", "hunde_5", 5), ("sonder20_g", "hunde_6", 6)):
    p = pl.neueste(szene)
    plan = pl.plan_von(p)
    S = plan["von"]
    op = [e for e in plan["einheiten"] if e.get("posten") == posten and e["rolle"] == "opfer" and "nr" in e]
    erst, tot = {}, set()
    for t, u in pl.stand(p, "DAT_UnitsState", U):
        for e in op:
            n = e["nr"]
            if u["typ"][n] != 24 or not u["da"][n] or u["l"][n] <= 0:
                tot.add(n)
            elif int(u["l"][n]) < 12500 and n not in erst:
                erst[n] = t - S
    print(szene, posten, "Opfer", len(op), "gesetzt", zahl, "erster Verlust", sorted(erst.values())[:3], "Tote", len(tot), "Takte", plan["bis"] - S)
