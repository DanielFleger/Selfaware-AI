# -*- coding: utf-8 -*-
"""B-143: Listet jede Stelle in src/, die in echter Zeit rechnet oder wartet (Daniel 02.11.2026: alles in Takten).
Die Klasse ist ein Vorschlag aus dem Code um die Stelle und ersetzt nicht das Lesen:
  warten_spiel    feste Wartezeit ueber 1 s: laesst das Spiel eine Zeit laufen, gehoert in Takte
  abfragetakt     kurze Pause in einer Schleife: wie oft nachgesehen wird, keine Spielregel
  frist           Uhr als Schutz gegen Haengen, bleibt (kommen keine Takte, kann man sie nicht zaehlen)
  messung         Uhr als Messwert oder fuer Tempo, bleibt nur dort, wo echte Zeit die Messgroesse ist
  unklar          muss gelesen werden
Lauf aus dem Repo-Stamm: python data/research/auge_plan/zeit_stellen.py
"""
import ast
import collections
import csv
import os
import re

UHR = {"time", "perf_counter", "monotonic", "clock"}
AUS = os.path.join("data", "research", "auge_plan", "zeit_stellen.csv")


def zahl(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
        return float(n.value)
    return None


def klasse_uhr(zeile):
    z = zeile.lower()
    if re.search(r"ende|frist|timeout|deadline|grenze|hoechstens|limit", z):
        return "frist"
    if re.search(r"dauer|takte_je|tempo|/ *\(|- *t0|- *start|- *beginn|- *anfang|messe|mess", z):
        return "messung"
    return "unklar"


zeilen = []
for wurzel, _, dateien in os.walk(os.path.join("src", "selfaware")):
    for d in dateien:
        if not d.endswith(".py"):
            continue
        pfad = os.path.join(wurzel, d)
        text = open(pfad, encoding="utf-8", errors="replace").read()
        try:
            baum = ast.parse(text)
        except SyntaxError:
            zeilen.append({"datei": pfad, "zeile": 0, "art": "syntaxfehler", "klasse": "unklar", "wert": "", "text": ""})
            continue
        quelle = text.splitlines()
        for f in ast.walk(baum):
            if not isinstance(f, ast.Call) or not isinstance(f.func, ast.Attribute):
                continue
            basis = f.func.value
            if not (isinstance(basis, ast.Name) and basis.id == "time"):
                continue
            z = quelle[f.lineno - 1].strip()
            if f.func.attr == "sleep":
                w = zahl(f.args[0]) if f.args else None
                k = "unklar" if w is None else ("warten_spiel" if w > 1.0 else "abfragetakt")
                zeilen.append({"datei": pfad, "zeile": f.lineno, "art": "sleep", "klasse": k, "wert": "" if w is None else w, "text": z[:150]})
            elif f.func.attr in UHR:
                zeilen.append({"datei": pfad, "zeile": f.lineno, "art": "uhr", "klasse": klasse_uhr(z), "wert": "", "text": z[:150]})
with open(AUS, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["datei", "zeile", "art", "klasse", "wert", "text"], delimiter=";")
    w.writeheader()
    w.writerows(sorted(zeilen, key=lambda z: (z["datei"], z["zeile"])))
print(len(zeilen), "Stellen in", len({z["datei"] for z in zeilen}), "Dateien")
print(collections.Counter((z["art"], z["klasse"]) for z in zeilen).most_common())
je = collections.Counter(z["datei"] for z in zeilen if z["klasse"] in ("warten_spiel", "unklar"))
print("zu lesen je Datei:", [(k.split(os.sep)[-1], v) for k, v in je.most_common(12)])
g = collections.Counter(z["datei"].split(os.sep)[2] for z in zeilen)
print(g.most_common())
