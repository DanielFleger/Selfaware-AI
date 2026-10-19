# -*- coding: utf-8 -*-
"""Nachschau fuer schon gespielte Lernlaeufe nachtragen (Lauf 1/2 liefen mit dem Pfadfehler: Nachschau leer)."""
import json, os, re, sys
HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.learning.lernen as LN
pfad = os.path.join(LN.D, "lernen.jsonl")
alle = [json.loads(z) for z in open(pfad, encoding="utf-8")]
for r in alle:
    if not r.get("nachschau"):
        t = open(os.path.join(LN.D, r["datei"]), encoding="utf-8", errors="replace").read()
        lp = re.search(r"Lageprotokoll \(jede Runde komplett\): (.+?\.jsonl\.gz)", t)
        if lp and os.path.exists(lp.group(1)):
            r["nachschau"] = LN.nachschau(lp.group(1))
            print("Lauf %d nachgetragen: %s" % (r["nr"], r["nachschau"]))
with open(pfad, "w", encoding="utf-8") as f:
    for r in alle:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
