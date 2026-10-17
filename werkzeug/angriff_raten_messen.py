# -*- coding: utf-8 -*-
"""Drei Raten fuer die Assassinen-Entscheidung aus Lageprotokollen (SAI 17.10., Daniel 10:05 "ja": Gefahrenkarte und
Zielwahl neu nach L75-L80 - dafuer muessen die bisher geschaetzten Zahlen gemessen sein).

1. SCHUSS: Schaden je Schuetze und Takt an einer SICHTBAREN Assassine (naechster waehlbarer Feind <= 160 Feinmass in
   beiden Runden, L75), ohne Nahkampf (kein Feind im Umkreis 2, kein Nahangreifer). Schuetzen in Reichweite (Kreis,
   live-Reichweiten L78) getrennt nach FREIER und VERSPERRTER Schusslinie: versperrt, wenn ein Gebaeudefeld (nicht flach,
   nicht das Gebaeude, auf dem der Schuetze steht) auf der Linie liegt; Schuetzen auf Turm/Torhaus/Bergfried nie versperrt.
   VORHER FESTGELEGT: haelt das Sperr-Modell, ist die Rate bei nur versperrten Schuetzen unter 30 % der Rate bei nur
   freien. Sonst sperren Gebaeude anders (Hoehe, L79) - dann zaehlt jeder Schuetze in Reichweite.
2. GEBAEUDE: Lebensverlust eines feindlichen Gebaeudes je angreifender Assassine (Zustand 107, hoechstens 1 Feld neben
   seiner Grundflaeche) und Takt, je Gebaeudeart -> Zeit bis zur Zerstoerung = Leben / (Rate x Zahl).
3. ARBEITER: Lebensverlust eines feindlichen Nicht-Soldaten je zuschlagender Assassine (Zustand 106, Nahziel = er) und
   Takt, je Art -> Zeit bis zum Tod.
Grundflaechen: VillageStudio/lib/gebaeude.json (Spalte laufzeit -> b). Gebaeude-x/y = linke obere Ecke (acquireShootTarget
rechnet die Mitte als x + Breite/2, abgelesen 17.10.; im Protokoll stand die Assassine 1 Feld unter der Grundflaeche).
Aufruf: python werkzeug/angriff_raten_messen.py daten/lage_....jsonl.gz [...]   Ergebnis auch nach daten/angriff_raten.json"""
import json
import os
import sys
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from lageprotokoll import runden
import entdeckung_pruefen as P

GJ = os.path.join(HIER, "..", "..", "VillageStudio", "lib", "gebaeude.json")
GROESSE = {int(v["laufzeit"]): int(v["b"]) for v in json.load(open(GJ, encoding="utf-8"))["gebaeude"].values()
           if isinstance(v, dict) and v.get("laufzeit")}
FLACH = {10, 30, 31, 32, 33}                     # Lagerplatz, Getreide-, Hopfen-, Apfelplantage, Milchviehhof (vermutet flach)
ERHOEHT = {41, 45, 46, 74, 75, 76, 77, 78}       # wie assassinen.Einzeln.ERHOEHT


def linie(a, b):
    """Felder zwischen a und b (ohne Endpunkte), Bresenham."""
    x0, y0 = a
    x1, y1 = b
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err, aus = dx + dy, []
    while (x0, y0) != (x1, y1):
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy
        if (x0, y0) != (x1, y1):
            aus.append((x0, y0))
    return aus


def felder_von(G):
    """Feld -> (Gebaeude-Nr, Typ) fuer alle Gebaeude (jeder Besitzer) mit bekannter Groesse."""
    f = {}
    for g in G:
        b = GROESSE.get(g["typ"])
        if not b:
            continue
        for x in range(g["x"], g["x"] + b):
            for y in range(g["y"], g["y"] + b):
                f[(x, y)] = (g["nr"], g["typ"])
    return f


def main():
    pfade = [a for a in sys.argv[1:] if "=" not in a]
    sp = 1
    schuss = defaultdict(lambda: [0.0, 0.0, 0])          # (frei, versperrt) -> [Verlust, Takte, Runden]
    geb = defaultdict(lambda: [0.0, 0.0, 0])             # Typ -> [Verlust, Assassinen-Takte, Paare]
    arb = defaultdict(lambda: [0.0, 0.0, 0])
    geb_leben = defaultdict(list)
    for pfad in pfade:
        vorher = None
        for t, st, E, G in runden(pfad):
            jetzt = {"t": t, "E": {e["nr"]: e for e in E}, "G": {g["nr"]: g for g in G}}
            if vorher and t > vorher["t"]:
                dt = t - vorher["t"]
                E0, G0 = vorher["E"], vorher["G"]
                feinde = [e for e in E if e["besitzer"] not in (0, sp) and e["typ"] not in P.TIERE]
                waehl = [(e["x"], e["y"]) for e in feinde if e["typ"] in P.WAEHLBAR]
                alle = [(e["x"], e["y"]) for e in feinde]
                fe = None
                # 1. Schuss
                for e in E:
                    if e["typ"] != 73 or e["besitzer"] != sp or e["nr"] not in E0:
                        continue
                    a = E0[e["nr"]]
                    ort, ort0 = (e["x"], e["y"]), (a["x"], a["y"])
                    if e.get("nahangreifer") or a.get("nahangreifer") or any(P.schach(ort, p) <= 2 or P.schach(ort0, p) <= 2 for p in alle):
                        continue
                    if min((P.abstand_fein(ort, w) for w in waehl), default=99999) > P.SICHT or \
                            min((P.abstand_fein(ort0, w) for w in waehl), default=99999) > P.SICHT:
                        continue
                    if fe is None:
                        fe = felder_von(G)
                    frei = zu = 0
                    for s in feinde:
                        r = P.FERN.get(s["typ"])
                        sp_ = (s["x"], s["y"])
                        if not r or (sp_[0] - ort[0]) ** 2 + (sp_[1] - ort[1]) ** 2 > r * r:
                            continue
                        steht = fe.get(sp_)
                        if steht and steht[1] in ERHOEHT:
                            frei += 1
                            continue
                        block = any(q in fe and fe[q][1] not in FLACH and (not steht or fe[q][0] != steht[0])
                                    for q in linie(sp_, ort))
                        zu += block
                        frei += not block
                    if frei or zu:
                        z = schuss[(min(frei, 9), min(zu, 9))]
                        z[0] += max(0, a["leben"] - e["leben"]); z[1] += dt; z[2] += 1
                # 2. Gebaeude
                for gn, g in jetzt["G"].items():
                    if g["besitzer"] in (0, sp) or gn not in G0 or g["typ"] not in GROESSE:
                        continue
                    b = GROESSE[g["typ"]]
                    def dran(einh):
                        return sum(1 for x in einh.values() if x["typ"] == 73 and x["besitzer"] == sp and x["zustand"] == 107
                                   and g["x"] - 1 <= x["x"] <= g["x"] + b and g["y"] - 1 <= x["y"] <= g["y"] + b)
                    n0, n1 = dran(E0), dran(jetzt["E"])
                    if n0 and n1:
                        z = geb[g["typ"]]
                        z[0] += max(0, G0[gn]["leben"] - g["leben"]); z[1] += dt * (n0 + n1) / 2.0; z[2] += 1
                        geb_leben[g["typ"]].append(G0[gn]["leben"])
                # 3. Arbeiter
                ziele = defaultdict(int)
                ziele0 = defaultdict(int)
                for x in E:
                    if x["typ"] == 73 and x["besitzer"] == sp and x["zustand"] == 106 and x.get("nahziel"):
                        ziele[x["nahziel"]] += 1
                for x in E0.values():
                    if x["typ"] == 73 and x["besitzer"] == sp and x["zustand"] == 106 and x.get("nahziel"):
                        ziele0[x["nahziel"]] += 1
                for w, n1 in ziele.items():
                    if w in E0 and w in jetzt["E"] and ziele0.get(w) and E0[w]["besitzer"] not in (0, sp) \
                            and E0[w]["typ"] not in P.WAEHLBAR:
                        z = arb[E0[w]["typ"]]
                        z[0] += max(0, E0[w]["leben"] - jetzt["E"][w]["leben"]); z[1] += dt * (n1 + ziele0[w]) / 2.0; z[2] += 1
            vorher = jetzt
    erg = {"schuss": {}, "gebaeude": {}, "arbeiter": {}}
    nur_frei = [0.0, 0.0]
    nur_zu = [0.0, 0.0]
    for (f, z), (d, tt, n) in schuss.items():
        if z == 0 and f:
            nur_frei[0] += d; nur_frei[1] += tt * f
        if f == 0 and z:
            nur_zu[0] += d; nur_zu[1] += tt * z
    r_frei = nur_frei[0] / nur_frei[1] if nur_frei[1] else float("nan")
    r_zu = nur_zu[0] / nur_zu[1] if nur_zu[1] else float("nan")
    erg["schuss"] = {"rate_frei_je_schuetze_takt": round(r_frei, 3), "rate_versperrt_je_schuetze_takt": round(r_zu, 3),
                     "schuetzen_takte_frei": round(nur_frei[1]), "schuetzen_takte_versperrt": round(nur_zu[1]),
                     "sperrmodell": "haelt" if r_zu < 0.3 * r_frei else "WIDERLEGT"}
    print("SCHUSS an sichtbarer Assassine: nur freie Linien %.3f je Schuetze und Takt (%d Schuetzen-Takte), nur versperrte %.3f (%d) -> Sperrmodell %s"
          % (r_frei, nur_frei[1], r_zu, nur_zu[1], erg["schuss"]["sperrmodell"]))
    for k in sorted(schuss, key=lambda k: (k[1], k[0]))[:12]:
        d, tt, n = schuss[k]
        print("   frei %d / versperrt %d: %d Runden, Verlust je Takt %.2f" % (k[0], k[1], n, d / tt if tt else 0))
    print("GEBAEUDE: Lebensverlust je angreifender Assassine und Takt")
    for typ, (d, tt, n) in sorted(geb.items(), key=lambda x: -x[1][2]):
        if n >= 5:
            lmax = max(geb_leben[typ])
            erg["gebaeude"][typ] = {"rate": round(d / tt, 3), "paare": n, "leben_max": lmax}
            print("   Typ %3d: %.2f je Takt (%d Rundenpaare), hoechstes Leben %d -> allein %.0f Takte" % (
                typ, d / tt, n, lmax, lmax / (d / tt) if d else float("inf")))
    print("ARBEITER: Lebensverlust je zuschlagender Assassine und Takt")
    for typ, (d, tt, n) in sorted(arb.items(), key=lambda x: -x[1][2]):
        if n >= 3:
            erg["arbeiter"][typ] = {"rate": round(d / tt, 2), "paare": n}
            print("   Typ %3d: %.1f je Takt (%d Rundenpaare)" % (typ, d / tt, n))
    json.dump(erg, open(os.path.join(HIER, "..", "daten", "angriff_raten.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
