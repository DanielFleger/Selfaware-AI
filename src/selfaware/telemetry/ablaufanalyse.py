# -*- coding: utf-8 -*-
"""Ablaufanalyse (Daniel 06.10. 22:44: "wie lange jede Produktion braucht, nach welcher Menge an Arbeitern ... du sollst
wirklich ALLES festhalten, damit du wirklich alles weisst, was passiert, passierte und passieren wird, und Wissen im Vor-
und Nachfeld, warum etwas so und nicht anders passiert ist").

Liest ein Lageprotokoll (lageprotokoll.py: jede Runde der komplette Abzug) und vermisst daraus OHNE Annahmen:
  1. Zustaende je Einheitenart: wie lange dauert jeder Zustand (nur Abschnitte, deren Anfang UND Ende im Protokoll
     liegen), wie viel Zeit verbringt die Art darin, bewegt sie sich darin (Felder je Tick).
  2. Gehen: Felder je Tick mit und ohne Ladung (Schachbrett-Abstand zwischen zwei Runden, nur wenn sie sich bewegt).
  3. Ablieferungen: Ladung faellt auf 0 -> wie viel, wo, Abstand zwischen zwei Ablieferungen derselben Einheit.
  4. Gebaeude-Vorrat: jeder Zugang/Abgang je Gebaeude (Lagerteile, Steinhaufen, Kornspeicher ...), Zugang je 1.000 Ticks.
  5. Waren des Spielers je 1.000 Ticks (Statuszeile).
  6. Arbeitsvergabe: wann bekommt eine Einheit einen Arbeitsplatz, welche Gebaeudeart (Reihenfolge der Vergabe).
  7. Besetzung: Arbeiter je Gebaeudeart im Mittel - damit Ertrag je Arbeiter.
Aufloesung = mittlerer Abstand zwischen zwei Runden; kuerzere Zustaende koennen fehlen - steht bei jedem Ergebnis dabei.

Ausgabe: data/research/ablauf_<name>.json (alles) + Text; mit wissen=ja wird jede Messung als Zeile an data/research/wissen_ablauf.jsonl
angehaengt (Quelle, Groesse, Wert, Anzahl, Aufloesung) - das Wissen waechst mit jedem Lauf.
Aufruf: uv run python -m selfaware.telemetry.ablaufanalyse <lage...jsonl.gz> [besitzer=1] [wissen=ja]
"""

from selfaware import workspace as _workspace
import json
import os
import statistics
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

from selfaware.telemetry.lageprotokoll import runden

EINHEIT = {1: "Bauer", 3: "Holzfaeller", 6: "Jaeger", 7: "Steinmetz", 8: "Steinbrucharbeiter", 9: "Steinochse",
           10: "Pechmann", 11: "Hofbauer 11", 12: "Hofbauer 12", 13: "Apfelbauer", 14: "Milchbauer", 19: "Schmied",
           21: "Gerber", 26: "Streitkolbenkaempfer", 31: "Bergmann", 51: "Kuh", 55: "Lord"}


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def mittel(xs):
    return round(statistics.mean(xs), 2) if xs else None


def median(xs):
    return round(statistics.median(xs), 1) if xs else None


def analyse(pfad, sp=1):
    R = list(runden(pfad))
    ticks = [r[0] for r in R]
    abst = [b - a for a, b in zip(ticks, ticks[1:]) if b > a]
    aufl = round(statistics.mean(abst), 1) if abst else None
    gname = {}
    try:
        from selfaware.game.ucp.bauen import NACH_TYP
        gname = {t: g["name"] for t, g in NACH_TYP.items()}
    except Exception:
        pass
    # ---- je Einheit eine Zeitreihe -------------------------------------------------------------------------------
    reihe = {}                       # nr -> [(t, d)]
    for t, st, E, G in R:
        for d in E:
            if d["besitzer"] == sp:
                reihe.setdefault(d["nr"], []).append((t, d))
    gtyp = {}                        # Gebaeudenummer -> typ (letzter Stand)
    for t, st, E, G in R:
        for g in G:
            gtyp[g["nr"]] = g["typ"]
    zust, gehen, abliefern, vergabe = {}, {}, [], []
    for nr, s in reihe.items():
        typ = s[-1][1]["typ"]
        # 1. Zustandsabschnitte
        abschn = []
        for i, (t, d) in enumerate(s):
            k = (d["zustand"], d.get("ladung", 0) > 0)
            if abschn and abschn[-1]["k"] == k and t - abschn[-1]["bis"] <= 3 * (aufl or 50):
                abschn[-1]["bis"] = t
                abschn[-1]["weg"] += schach((d["x"], d["y"]), abschn[-1]["pos"])
                abschn[-1]["pos"] = (d["x"], d["y"])
            else:
                abschn.append({"k": k, "von": t, "bis": t, "pos": (d["x"], d["y"]), "weg": 0, "erster": i == 0})
        for j, a in enumerate(abschn):
            voll = not a["erster"] and j < len(abschn) - 1         # Anfang und Ende beobachtet
            z = zust.setdefault(typ, {}).setdefault("z%d%s" % (a["k"][0], "+Last" if a["k"][1] else ""),
                                                   {"dauer": [], "zeit": 0, "weg": 0})
            z["zeit"] += a["bis"] - a["von"]
            z["weg"] += a["weg"]
            if voll:
                # Ende = Beginn des naechsten Abschnitts (die Einheit war bis dahin in diesem Zustand)
                z["dauer"].append(abschn[j + 1]["von"] - a["von"])
        # 2. Gehen, 3. Ablieferungen, 6. Vergabe
        # Gehen ueber GANZE Abschnitte eines Zustands, in dem sich die Einheit bewegt (>= 3 Felder): Weg / Dauer.
        # 22:52 korrigiert: vorher nur Runden mit Bewegung gezaehlt - eine Einheit kommt je Runde (14,5 Ticks) hoechstens
        # 1 Feld weiter, gemessen wurde damit der Rundenabstand (14,5) statt der Geschwindigkeit (~25, Arbeitsgaenge G).
        for j, a in enumerate(abschn):
            if a["weg"] >= 3 and not a["erster"] and j < len(abschn) - 1:
                g = gehen.setdefault(typ, {"mit": [0, 0], "ohne": [0, 0]})
                g["mit" if a["k"][1] else "ohne"][0] += a["weg"]
                g["mit" if a["k"][1] else "ohne"][1] += abschn[j + 1]["von"] - a["von"]
        for (t0, d0), (t1, d1) in zip(s, s[1:]):
            dt = t1 - t0
            if dt <= 0:
                continue
            if d0.get("ladung", 0) > 0 and d1.get("ladung", 0) < d0.get("ladung", 0):
                abliefern.append({"nr": nr, "typ": typ, "t": t1, "menge": d0["ladung"] - d1.get("ladung", 0),
                                  "ort": (d1["x"], d1["y"]), "arbeitsplatz": d0.get("arbeitsplatz")})
            a0, a1 = d0.get("arbeitsplatz"), d1.get("arbeitsplatz")
            if a1 and a1 != a0 and gtyp.get(a1) not in (55, None):
                vergabe.append({"t": t1, "nr": nr, "einheit": typ, "gebaeude": a1, "gebaeudeart": gtyp.get(a1)})
    # 4. Gebaeude-Vorrat
    vorrat = {}
    letzt = {}
    for t, st, E, G in R:
        for g in G:
            if g["besitzer"] != sp or g.get("vorrat") is None:
                continue
            v0 = letzt.get(g["nr"])
            if v0 is not None and g["vorrat"] != v0:
                vorrat.setdefault(g["nr"], {"typ": g["typ"], "ort": (g["x"], g["y"]), "ware": g.get("ware"), "zu": [], "ab": []})
                (vorrat[g["nr"]]["zu"] if g["vorrat"] > v0 else vorrat[g["nr"]]["ab"]).append((t, g["vorrat"] - v0))
            letzt[g["nr"]] = g["vorrat"]
    # 5. Waren
    t0, t1 = ticks[0], ticks[-1]
    st0, st1 = R[0][1], R[-1][1]
    waren = {k: round(1000.0 * (st1.get(k, 0) - st0.get(k, 0)) / max(1, t1 - t0), 2)
             for k in ("holz", "stein", "eisen", "gold", "apfel", "brot", "kaese", "fleisch") if k in st1}
    # 7. Besetzung: Arbeiter je Gebaeudeart im Mittel
    besetzt = {}
    for t, st, E, G in R:
        je = {}
        for d in E:
            if d["besitzer"] == sp and d.get("arbeitsplatz") and gtyp.get(d["arbeitsplatz"]) not in (55, None):
                je[gtyp[d["arbeitsplatz"]]] = je.get(gtyp[d["arbeitsplatz"]], 0) + 1
        for gt, n in je.items():
            besetzt.setdefault(gt, []).append(n)
    # ---- zusammenfassen ------------------------------------------------------------------------------------------
    erg = {"quelle": os.path.basename(pfad), "von": t0, "bis": t1, "runden": len(R), "aufloesung_ticks": aufl,
           "zustaende": {}, "gehen": {}, "ablieferungen": {}, "vorrat": {}, "waren_je_1000": waren,
           "vergabe": vergabe, "besetzung_mittel": {gname.get(gt, gt): round(statistics.mean(n), 1) for gt, n in besetzt.items()}}
    for typ, zs in zust.items():
        name = EINHEIT.get(typ, "Einheit %d" % typ)
        ges = sum(z["zeit"] for z in zs.values()) or 1
        erg["zustaende"][name] = {k: {"anteil_zeit": round(z["zeit"] / ges, 3), "dauer_median": median(z["dauer"]),
                                      "dauer_mittel": mittel(z["dauer"]), "n": len(z["dauer"]),
                                      "felder_je_tick": round(z["weg"] / max(1, z["zeit"]), 3)}
                                  for k, z in sorted(zs.items())}
    for typ, g in gehen.items():
        erg["gehen"][EINHEIT.get(typ, "Einheit %d" % typ)] = {
            k: {"ticks_je_feld": round(v[1] / v[0], 1) if v[0] else None, "felder": v[0], "ticks": v[1]} for k, v in g.items()}
    for a in abliefern:
        e = erg["ablieferungen"].setdefault(EINHEIT.get(a["typ"], "Einheit %d" % a["typ"]), {"anzahl": 0, "menge": 0, "abstand": []})
        e["anzahl"] += 1
        e["menge"] += a["menge"]
    for typ_name, e in erg["ablieferungen"].items():
        je = {}
        for a in abliefern:
            if EINHEIT.get(a["typ"], "Einheit %d" % a["typ"]) == typ_name:
                je.setdefault(a["nr"], []).append(a["t"])
        e["abstand"] = [b - a for ts in je.values() for a, b in zip(ts, ts[1:])]
        e["abstand_median"] = median(e["abstand"])
        e["menge_je_gang"] = round(e["menge"] / e["anzahl"], 1) if e["anzahl"] else None
    for nr, v in vorrat.items():
        zu = sum(m for _, m in v["zu"])
        erg["vorrat"]["%s %d %s ware %s" % (gname.get(v["typ"], v["typ"]), nr, v["ort"], v["ware"])] = {
            "zugang": zu, "abgang": -sum(m for _, m in v["ab"]), "zugang_je_1000": round(1000.0 * zu / max(1, t1 - t0), 1),
            "zugaenge": len(v["zu"]), "groesse_je_zugang": median([m for _, m in v["zu"]])}
    return erg, abliefern


def text(erg):
    z = ["ABLAUF %s: Tick %d-%d, %d Runden, Aufloesung %s Ticks" % (erg["quelle"], erg["von"], erg["bis"], erg["runden"], erg["aufloesung_ticks"])]
    z.append("Waren je 1.000 Ticks (netto): %s" % erg["waren_je_1000"])
    z.append("Besetzung im Mittel (Arbeiter je Gebaeudeart): %s" % erg["besetzung_mittel"])
    for name, zs in erg["zustaende"].items():
        z.append("%s: %s" % (name, "; ".join("%s %.0f%% Zeit, Dauer Median %s (n=%d), %.2f Felder/Tick" % (
            k, 100 * v["anteil_zeit"], v["dauer_median"], v["n"], v["felder_je_tick"]) for k, v in zs.items())))
    for name, g in erg["gehen"].items():
        z.append("Gehen %s: %s" % (name, ", ".join("%s Last %s Ticks/Feld (%d Felder)" % (k, v["ticks_je_feld"], v["felder"]) for k, v in g.items())))
    for name, e in erg["ablieferungen"].items():
        z.append("Ablieferungen %s: %d Gaenge, %d Stueck, %s je Gang, Abstand Median %s Ticks" % (
            name, e["anzahl"], e["menge"], e["menge_je_gang"], e["abstand_median"]))
    for k, v in erg["vorrat"].items():
        z.append("Vorrat %s: +%d / -%d, %d Zugaenge (Median %s), %s je 1.000 Ticks" % (
            k, v["zugang"], v["abgang"], v["zugaenge"], v["groesse_je_zugang"], v["zugang_je_1000"]))
    if erg["vergabe"]:
        z.append("Arbeitsvergabe (Tick: Einheit -> Gebaeudeart): %s" % ", ".join(
            "%d:%s->%s" % (v["t"], EINHEIT.get(v["einheit"], v["einheit"]), v["gebaeudeart"]) for v in erg["vergabe"][:40]))
    return "\n".join(z)


def wissen_anhaengen(erg):
    pfad = os.path.join(_workspace.DATA, 'wissen_ablauf.jsonl')
    with open(pfad, "a", encoding="utf-8") as f:
        def zeile(groesse, wert, n=None, einheit=""):
            f.write(json.dumps({"quelle": erg["quelle"], "ticks": [erg["von"], erg["bis"]], "aufloesung": erg["aufloesung_ticks"],
                                "groesse": groesse, "wert": wert, "n": n, "einheit": einheit, "stufe": "gemessen"},
                               ensure_ascii=False) + "\n")
        for name, zs in erg["zustaende"].items():
            for k, v in zs.items():
                if v["n"]:
                    zeile("%s Zustand %s Dauer" % (name, k), v["dauer_median"], v["n"], "Ticks (Median)")
        for name, g in erg["gehen"].items():
            for k, v in g.items():
                if v["felder"] >= 10:
                    zeile("%s gehen %s Last" % (name, k), v["ticks_je_feld"], v["felder"], "Ticks je Feld")
        for name, e in erg["ablieferungen"].items():
            zeile("%s Menge je Gang" % name, e["menge_je_gang"], e["anzahl"], "Stueck")
            if e["abstand"]:
                zeile("%s Abstand zwischen Ablieferungen" % name, e["abstand_median"], len(e["abstand"]), "Ticks (Median)")
        for k, v in erg["vorrat"].items():
            zeile("Zugang %s" % k, v["zugang_je_1000"], v["zugaenge"], "Stueck je 1.000 Ticks")
        for k, v in erg["waren_je_1000"].items():
            zeile("Ware %s netto" % k, v, None, "je 1.000 Ticks")
        for k, v in erg["besetzung_mittel"].items():
            zeile("Besetzung %s" % k, v, None, "Arbeiter im Mittel (alle Gebaeude dieser Art)")
    return pfad


def main():
    pfad = sys.argv[1]
    arg = dict(a.split("=", 1) for a in sys.argv[2:])
    erg, abl = analyse(pfad, int(arg.get("besitzer", 1)))
    ziel = os.path.join(_workspace.DATA, 'ablauf_%s.json' % os.path.basename(pfad).split('.')[0])
    json.dump({"ergebnis": erg, "ablieferungen": abl}, open(ziel, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
    print(text(erg))
    print("Daten:", os.path.abspath(ziel))
    if arg.get("wissen") == "ja":
        print("Wissen angehaengt:", os.path.abspath(wissen_anhaengen(erg)))


if __name__ == "__main__":
    main()
