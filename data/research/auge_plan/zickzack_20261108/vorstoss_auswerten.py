# -*- coding: utf-8 -*-
"""Szene vorstoss_g (B-174): Klappt das Zusammenspiel von Vorstoss, Kern und Spiel?

Vor dem Lauf festgelegt (die Grenzen sind meine, ohne Vorgabe dahinter): widerlegt, wenn beim Vorruecken weniger als die Haelfte der
Schritte die Richtung wechselt, wenn nach dem Befehl zum Schiessen kein Pfeil der Gruppe fliegt, wenn die Gruppe beim Abziehen nicht
weiter vom Feind wegkommt oder wenn der Kern einen Fehler meldet. Treffer werden hier nicht gemessen: Die Lage ist gestellt.
Eingabe: neueste lauf_s_*_vorstoss_g.auge unter laeufe/, Protokoll lauf_vorstoss_g.log. Ausgabe: vorstoss_g_ergebnis.txt.
"""
import collections
import glob
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "streuung_20261104"))
import flug_pruefen as fp  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

ART = 1
KENN = (("rueckt vor", "vor"), ("schiessen auf", "schuss"), ("Schussfeld", "abziehen"), ("weicht", "weichen"))
TEIL = 12  # Takte Abstand der Blicke auf die Aufstellung: ein Feld


def art_von(z):
    return next((n for k, n in KENN if k in z), None)


def main():
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_vorstoss_g.auge")), key=os.path.getmtime)[-1]
    k = Feldkarte.laden(feldliste=FELDLISTE)
    lauf = fp.Lauf(pfad, k)
    b = [json.loads(z) for z in open(os.path.join(HIER, "lauf_vorstoss_g.log"), encoding="utf-8", errors="replace") if z.startswith('{"schritt": "vorstoss_probe"')][-1]
    eigene = b["eigene"]
    plan = sorted((v["takt"], art_von(v["ereignis"])) for v in b["verlauf"] if "ereignis" in v and art_von(v["ereignis"]))
    aus = ["Datei %s, Takte %d bis %d" % (os.path.basename(pfad), b["von"], b["bis"]), "Bericht: %s" % b["bericht"], ""]
    aus.append("Verlauf:")
    for v in b["verlauf"]:
        aus.append("  %s" % json.dumps(v, ensure_ascii=False)[:150])
    aus.append("")
    takte = [t for t in sorted(lauf.u) if b["von"] <= t <= b["bis"]]

    def phase(t):
        p = None
        for a, n in plan:
            if a <= t:
                p = n
        return p

    schritte = collections.defaultdict(collections.Counter)
    for i in eigene:
        vor = richt = None
        for t in takte:
            q = lauf.u[t]
            if int(q["leben"][i]) <= 0:
                continue
            p = (int(q["x"][i]), int(q["y"][i]))
            if vor is not None and p != vor:
                r = (p[0] - vor[0], p[1] - vor[1])
                n = phase(t)
                schritte[n]["felder"] += 1
                schritte[n]["schraeg"] += bool(r[0] and r[1])
                if richt is not None:
                    schritte[n]["paare"] += 1
                    schritte[n]["wechsel"] += r != richt
                richt = r
            vor = p
    zeit = collections.Counter(phase(t) for t in takte)
    abstaende = collections.defaultdict(list)
    for t in takte[::TEIL]:
        q = lauf.u[t]
        o = [(int(q["x"][i]), int(q["y"][i])) for i in eigene]
        abstaende[phase(t)].append(min(max(abs(a[0] - c[0]), abs(a[1] - c[1])) for n, a in enumerate(o) for c in o[n + 1:]))
    for n in sorted(schritte, key=str):
        c = schritte[n]
        w = sorted(abstaende[n])
        aus.append("Phase %-9s %5d Takte: je Einheit %.1f Felder je 1000 Takte, Schritte mit neuer Richtung %s, schraeg %s, kleinster Abstand in der Gruppe (Median) %s" % (
            n, zeit[n], 1000 * c["felder"] / len(eigene) / max(zeit[n], 1), "%.0f %%" % (100 * c["wechsel"] / c["paare"]) if c["paare"] else "-", "%.0f %%" % (100 * c["schraeg"] / c["felder"]) if c["felder"] else "-", w[len(w) // 2] if w else "-"))
    pfeile = collections.Counter()
    for _s, f in lauf.fluege.items():
        z = f[0][1]
        if z["art"] == ART and z["sch"] in eigene and b["von"] <= f[0][0] <= b["bis"]:
            pfeile[phase(f[0][0])] += 1
    aus += ["", "Pfeile der Gruppe je Phase: %s" % sorted(pfeile.items(), key=str)]
    # Abziehen: Wird der Abstand zur Ueberzahl groesser?
    ab = next((t for t, n in plan if n == "abziehen"), None)
    aus.append("Erstes Abziehen bei Takt %s" % ab)
    if ab is not None:
        def abstand(t):
            q = lauf.u[t]
            leben = [i for i in eigene if int(q["leben"][i]) > 0]
            mx = sorted(int(q["x"][i]) for i in leben)[len(leben) // 2]
            my = sorted(int(q["y"][i]) for i in leben)[len(leben) // 2]
            feinde = [j for j in range(1, 2400) if int(q["bes"][j]) == 2 and int(q["typ"][j]) == 22 and int(q["leben"][j]) > 0 and int(q["stirbt"][j]) == 0]
            return min(max(abs(int(q["x"][j]) - mx), abs(int(q["y"][j]) - my)) for j in feinde) if feinde else None

        for t in (ab, ab + 100, ab + 200, ab + 300):
            if t in lauf.u:
                aus.append("  Takt %d: Abstand der Gruppenmitte zum naechsten feindlichen Bogenschuetzen %s, lebende Einheiten der Gruppe %d" % (t, abstand(t), sum(int(lauf.u[t]["leben"][i]) > 0 for i in eigene)))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "vorstoss_g_ergebnis.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
