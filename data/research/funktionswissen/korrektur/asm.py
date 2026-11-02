# -*- coding: utf-8 -*-
"""python korrektur/asm.py <adr> <regex>: Assembly-Zeilen des Exports, die passen, mit je 2 Nachbarn."""
import json, re, sys
d = json.load(open(r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions\%s.json" % sys.argv[1].lower().replace("0x", "").rjust(8, "0"), encoding="utf-8"))
a = d["assembly"]; r = re.compile(sys.argv[2], re.I); zeig = set()
for i, x in enumerate(a):
    if r.search(x["text"]):
        zeig.update(range(max(0, i - 2), min(len(a), i + 3)))
for i in sorted(zeig)[:80]:
    print(a[i]["address"], a[i]["text"])
