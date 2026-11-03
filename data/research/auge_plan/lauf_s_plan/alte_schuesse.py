# -*- coding: utf-8 -*-
"""B-142 Plan Lauf S: Trefferquote auf ein stehendes Ziel aus den Messungen vom 17.10.: Gibt es Luecken in der Trefferreihe, also verfehlte Schuesse? Nur lesen.
Grenze der Aussage: nur stehendes Ziel, nur diese fuenf Schuetzen, gelesen alle rund 7 Takte. Darum 3 Treffer je Paar in V3, und das laufende Ziel wird eigens gemessen.

Aufruf: python data/research/auge_plan/lauf_s_plan/alte_schuesse.py > data/research/auge_plan/lauf_s_plan/alte_schuesse.txt
"""
import collections
import json
import os
import statistics as S

HIER = os.path.dirname(os.path.abspath(__file__))
z = [json.loads(x) for x in open(os.path.join(HIER, "..", "..", "editor_messung_20261017_233353.jsonl"), encoding="utf-8")]
g = collections.defaultdict(list)
for r in z:
    if r["treffer"] and len(r["treffer"]) > 2:
        t = [a[0] for a in r["treffer"]]
        ab = [b - a for a, b in zip(t, t[1:])]
        m = S.median(ab)
        g[r["art"]].append((S.median(ab), sum(1 for x in ab if x > 1.5 * m), len(ab)))
print("Versuche", len(z))
for k, v in g.items():
    print("%-12s Schussabstand Median %5.1f, Luecken ueber dem 1,5-Fachen: %d von %d" % (k, S.median(x[0] for x in v), sum(x[1] for x in v), sum(x[2] for x in v)))
print("Zusammen: %d Luecken in %d Abstaenden" % (sum(x[1] for v in g.values() for x in v), sum(x[2] for v in g.values() for x in v)))

d = [json.loads(x) for x in open(os.path.join(HIER, "..", "..", "editor_duell_20261018_124723.jsonl"), encoding="utf-8")]
a = [r["a_trifft_ab"] for r in d if r["a_trifft_ab"] is not None]
print("Duelle 18.10.: %d, erster Treffer in Takten: kleinster %d, Median %.1f, groesster %d (Abstand 3 Felder, gelesen alle rund 7 Takte)" % (len(d), min(a), S.median(a), max(a)))
