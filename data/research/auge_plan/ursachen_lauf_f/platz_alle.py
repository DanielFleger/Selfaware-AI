# -*- coding: utf-8 -*-
"""Lauf F, angehaltenes Spiel Instanz 2: je Gebaeudeart die Spielpruefung ueber die ganze Karte. Baut nichts."""
import collections, json, os, sys
sys.path.insert(0, "src")
from selfaware.game.ucp import bauen

AUS, TMP = sys.argv[1], sys.argv[2]
STELLEN = [(205, 181), (205, 195), (212, 181), (212, 195), (219, 181), (219, 195), (205, 188), (219, 188), (198, 174), (198, 202), (205, 174), (205, 202)]
erg = {}
for typ in sorted(bauen.NACH_TYP):
    g = bauen.NACH_TYP[typ]
    gut, alle, _ = bauen.platzkarte(typ, 0, 0, 399, 399, TMP)
    z = open(TMP, encoding="utf-8").read().splitlines()
    karte = z[1:]
    gruende = collections.Counter(c for zeile in karte for c in zeile if c != "+")
    an_stellen = "".join(karte[y][x] for x, y in STELLEN)
    # naechste erlaubte Stelle zur Burg
    best = None
    for y, zeile in enumerate(karte):
        for x, c in enumerate(zeile):
            if c == "+":
                d = max(abs(x - 212), abs(y - 188))
                if best is None or d < best[0]:
                    best = (d, x, y)
    erg[typ] = {"name": g.get("name"), "mapper": g["mapper"], "b": g["b"], "gut": gut, "an_stellen": an_stellen, "naechste": best, "gruende": gruende.most_common(5)}
    print(typ, g.get("name"), "erlaubt", gut, "| an meinen 12 Stellen:", an_stellen, "| naechste", best, flush=True)
json.dump(erg, open(AUS, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
