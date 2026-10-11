# -*- coding: utf-8 -*-
"""Beste Mischung aus Weizen-, Hopfen-, Apfel- und Kuhfarmen fuer jede Karte (M13c, 04.10.2026).

Daniels Auftrag (20:51): "so leicht ... so schnell wie moeglich, auch fuer andere Plantagenarten
und Mixturen ... egal welche Karte man hat, damit das optimalst ist".

Eingabe: je Farmart die Platzkarte des Spiels (Modulbefehl "platzkarte", ganze Karte < 1 s).
Regeln (gemessen 04.10.):
  - Bau-Stelle = obere linke Ecke; Weizen/Hopfen 9x9, Apfel/Kuehe 10x10.
  - Zwei Farmen duerfen sich nicht ueberschneiden, aber lueckenlos beruehren.
Rechnung mit OR-Tools CP-SAT (Google), zwei Stufen:
  1. hoechster Gesamtwert  sum(wert[Sorte] * Anzahl[Sorte])  - mit Mindest-/Hoechstmengen je Sorte
  2. bei diesem Wert: kuerzester Gesamtweg  sum(Abstand Farm-Mitte -> Abgabeort der Sorte)
     (Aepfel und Kaese gehen in den Kornspeicher, Weizen und Hopfen ins Vorratslager)
"OPTIMAL" heisst: fuer DIESE Platzkarten und Regeln gibt es nachweislich nichts Besseres.
Grenzen: Platzkarte eines Zeitpunkts (stehende Einheiten sperren, Baeume koennen verschwinden).

Aufruf:  python farmen_mischen.py <auftrag.json>
Auftrag (Beispiel):
  {"karten": {"apfel": "../daten/platzkarte_apfel_Basis_ganz.txt", ...},
   "mitte": [170.5, 117.5], "umkreis": 50,
   "sorten": {"apfel": {"wert": 1, "min": 0, "max": 99, "ziel": [170.5, 117.5]},
              "hopfen": {"wert": 1, "ziel": [165, 120]}},
   "sekunden": 30, "ausgabe": "../daten/mischung_beispiel.json"}
Als Baustein:  from farmen_mischen import mische
"""
import json, math, os, sys, time

GROESSE = {"weizen": 9, "hopfen": 9, "apfel": 10, "kuehe": 10}
TYP = {"weizen": 30, "hopfen": 31, "apfel": 32, "kuehe": 33}          # Gebaeudetyp im Spiel
ZEICHEN = {"weizen": "W", "hopfen": "H", "apfel": "A", "kuehe": "K"}

def lies_karte(pfad):
    z = open(pfad, encoding="utf-8").read().split("\n")
    kopf = dict(t.split("=") for t in z[0].split())
    x0, y0 = int(kopf["x0"]), int(kopf["y0"])
    return {(x0 + i, y0 + j) for j, r in enumerate(z[1:]) for i, c in enumerate(r) if c == "+"}

def mische(karten, mitte, umkreis, sorten, sekunden=30.0, kerne=8):
    """karten: {sorte: set((x,y))}; sorten: {sorte: {wert, min, max, ziel}}. Gibt ein Ergebnis-dict."""
    # Karten lesen wird auch vom Echtzeit-Planer gebraucht und benoetigt keinen Optimierer. OR-Tools deshalb erst
    # laden, wenn wirklich eine Farmmischung gerechnet wird; sonst duerfte ein unabhaengiger Spielpfad nicht starten.
    from ortools.sat.python import cp_model
    t0 = time.time()
    m = cp_model.CpModel()
    var, abst, feld = {}, {}, {}
    for s, opt in sorten.items():
        g = GROESSE[s]; h = (g - 1) / 2.0
        zx, zy = opt.get("ziel", mitte)
        for (x, y) in karten[s]:
            if max(abs(x + h - mitte[0]), abs(y + h - mitte[1])) > umkreis:
                continue
            v = m.NewBoolVar("%s_%d_%d" % (s, x, y))
            var[(s, x, y)] = v
            abst[(s, x, y)] = math.hypot(x + h - zx, y + h - zy)
            for a in range(g):
                for b in range(g):
                    feld.setdefault((x + a, y + b), []).append(v)
    for liste in feld.values():                       # je Feld hoechstens eine Farm
        if len(liste) > 1:
            m.AddAtMostOne(liste)
    anzahl = {}
    for s, opt in sorten.items():
        vs = [v for k, v in var.items() if k[0] == s]
        anzahl[s] = sum(vs) if vs else 0
        if vs and opt.get("min") is not None:
            m.Add(anzahl[s] >= int(opt["min"]))
        if vs and opt.get("max") is not None:
            m.Add(anzahl[s] <= int(opt["max"]))
        if not vs and int(opt.get("min") or 0) > 0:
            return {"status": "UNMOEGLICH", "grund": "keine einzige Stelle fuer %s im Umkreis" % s}
    wert = {s: int(round(100 * float(opt.get("wert", 1)))) for s, opt in sorten.items()}
    ziel1 = sum(wert[k[0]] * v for k, v in var.items())
    m.Maximize(ziel1)
    loeser = cp_model.CpSolver()
    loeser.parameters.max_time_in_seconds = float(sekunden)
    loeser.parameters.num_workers = kerne
    st1 = loeser.Solve(m)
    if st1 not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": loeser.StatusName(st1), "kandidaten": len(var)}
    best1 = int(round(loeser.ObjectiveValue()))
    grenze1 = int(round(loeser.BestObjectiveBound()))
    s1_status, t1 = loeser.StatusName(st1), round(loeser.WallTime(), 2)
    # Stufe 2: Wert festhalten, Weg minimieren (Startloesung aus Stufe 1)
    for k, v in var.items():
        m.AddHint(v, loeser.Value(v))
    m.Add(ziel1 >= best1)
    m.Minimize(sum(int(round(10 * abst[k])) * v for k, v in var.items()))
    st2 = loeser.Solve(m)
    wahl = sorted(((k[0], k[1], k[2]) for k, v in var.items() if loeser.Value(v)), key=lambda k: abst[k])
    return {"status": "%s / %s" % (s1_status, loeser.StatusName(st2)), "kandidaten": len(var),
            "felder_mit_konflikt": sum(1 for l in feld.values() if len(l) > 1),
            "wert": best1 / 100.0, "wert_grenze": grenze1 / 100.0,
            "anzahl": {s: sum(1 for k in wahl if k[0] == s) for s in sorten},
            "weg_summe": round(sum(abst[k] for k in wahl), 1),
            "weg_grenze": round(loeser.BestObjectiveBound() / 10.0, 1),
            "sekunden": {"stufe1": t1, "stufe2": round(loeser.WallTime(), 2), "gesamt": round(time.time() - t0, 2)},
            "farmen": [{"sorte": k[0], "typ": TYP[k[0]], "x": k[1], "y": k[2], "abstand": round(abst[k], 1)} for k in wahl]}

def bild(e, rand=2):
    farmen = e["farmen"]
    if not farmen:
        return "(keine Farm)"
    feld = {}
    for i, f in enumerate(farmen):
        g = GROESSE[f["sorte"]]
        for a in range(g):
            for b in range(g):
                feld[(f["x"] + a, f["y"] + b)] = ZEICHEN[f["sorte"]] if (a in (0, g - 1) or b in (0, g - 1)) \
                    else ZEICHEN[f["sorte"]].lower()
    xs = [p[0] for p in feld]; ys = [p[1] for p in feld]
    return "\n".join("%3d " % y + "".join(feld.get((x, y), ".") for x in range(min(xs) - rand, max(xs) + rand + 1))
                     for y in range(min(ys) - rand, max(ys) + rand + 1)) + "\n    x ab %d" % (min(xs) - rand)

def main():
    auftrag = json.load(open(sys.argv[1], encoding="utf-8"))
    basis = os.path.dirname(os.path.abspath(sys.argv[1]))
    karten = {s: lies_karte(os.path.join(basis, p)) for s, p in auftrag["karten"].items() if s in auftrag["sorten"]}
    e = mische(karten, auftrag["mitte"], auftrag["umkreis"], auftrag["sorten"], auftrag.get("sekunden", 30))
    print("Status:", e["status"], "| Stellen:", e.get("kandidaten"), "| Felder mit Konflikt:", e.get("felder_mit_konflikt"))
    if "farmen" in e:
        print("Anzahl:", e["anzahl"], "| Wert %.2f (Grenze %.2f) | Weg-Summe %.1f (Grenze %.1f) | Zeit %s s" % (
            e["wert"], e["wert_grenze"], e["weg_summe"], e["weg_grenze"], e["sekunden"]))
        print("Stellen:", " ".join("%s(%d,%d)" % (ZEICHEN[f["sorte"]], f["x"], f["y"]) for f in e["farmen"]))
        if auftrag.get("bild"):
            print(bild(e))
    if auftrag.get("ausgabe"):
        json.dump(e, open(os.path.join(basis, auftrag["ausgabe"]), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
