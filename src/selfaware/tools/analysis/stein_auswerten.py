# -*- coding: utf-8 -*-
"""Steinkette aus einem vollstaendigen Lageprotokoll auswerten.

Regel vor dem Einzelfall:
  Steinbruch -> Steinhaufen -> Ochse -> Vorratslager wird als eine Kette gemessen.
  Mehr Ochsen helfen nur, wenn fertiger Stein am Haufen auf Abholung wartet. Ein
  zusaetzlicher Ochse, der keine Ladung abholt, erhoeht die Kettenleistung nicht.

Aufruf:
  uv run python -m selfaware.tools.analysis.stein_auswerten data/research/lage_....jsonl.gz [...]
"""
import gzip
import json
import os
import statistics
import sys


STEINMETZ, TREIBER, OCHSE = 7, 8, 9
JOCH, LAGER, STEINBRUCH, HAUFEN = 4, 10, 20, 21


def tabelle(roh, kopfzeile):
    zeilen = roh.splitlines()
    if len(zeilen) <= kopfzeile:
        return []
    kopf = zeilen[kopfzeile].split()
    aus = []
    for zeile in zeilen[kopfzeile + 1:]:
        werte = zeile.split()
        if len(werte) >= len(kopf):
            aus.append({k: int(v) for k, v in zip(kopf, werte)})
    return aus


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def auswerten(pfad):
    runden = []
    with gzip.open(pfad, "rt", encoding="utf-8") as f:
        for zeile in f:
            roh = json.loads(zeile)
            runden.append((roh["t"], tabelle(roh["einheiten"], 1), tabelle(roh["gebaeude"], 0)))
    if len(runden) < 2:
        return {"datei": pfad, "gueltig": False, "grund": "zu wenige Runden"}

    alle_g = {}
    erste_vorraete = {}
    letzte_vorraete = {}
    besetzt_ab = {}
    ox_vor = {}
    ox_daten = {}
    abholung_je_haufen = {}

    for tick, einheiten, gebaeude in runden:
        eigene_g = {g["nr"]: g for g in gebaeude if g.get("besitzer") == 1}
        alle_g.update(eigene_g)
        for nr, g in eigene_g.items():
            if g["typ"] == HAUFEN:
                erste_vorraete.setdefault(nr, g.get("vorrat", 0))
                letzte_vorraete[nr] = g.get("vorrat", 0)

        steinmetze = {}
        for e in einheiten:
            if e.get("besitzer") == 1 and e["typ"] == STEINMETZ:
                steinmetze[e.get("arbeitsplatz", 0)] = steinmetze.get(e.get("arbeitsplatz", 0), 0) + 1
        for nr, anzahl in steinmetze.items():
            if anzahl >= 3:
                besetzt_ab.setdefault(nr, tick)

        haufen = [g for g in eigene_g.values() if g["typ"] == HAUFEN]
        for e in einheiten:
            if e.get("besitzer") != 1 or e["typ"] != OCHSE:
                continue
            nr, ladung = e["nr"], e.get("ladung", 0)
            d = ox_daten.setdefault(nr, {"arbeitsplatz": e.get("arbeitsplatz"), "erste_runde": tick,
                                         "letzte_runde": tick, "abgeholt": 0, "geliefert": 0,
                                         "fahrten": 0, "abhol_ticks": [], "beladene_wege": [],
                                         "transportzyklen": [], "fahrt": None})
            d["letzte_runde"] = tick
            d["arbeitsplatz"] = e.get("arbeitsplatz") or d["arbeitsplatz"]
            vor = ox_vor.get(nr)
            # Zustand 4 ist das Joch/der Abholpunkt. Damit endet die LEERE Rueckfahrt. Die Wartezeit bis genug Stein
            # liegt wird bewusst nicht der Transportkapazitaet zugerechnet.
            if d["fahrt"] is not None and d["fahrt"].get("abgeladen") is not None and e.get("zustand") == 4:
                fahrt = d["fahrt"]
                fahrt["rueckkehr"] = tick
                fahrt["leer_ticks"] = tick - fahrt["abgeladen"]
                fahrt["transport_ticks"] = fahrt["beladen_ticks"] + fahrt["leer_ticks"]
                d["transportzyklen"].append(fahrt)
                d["fahrt"] = None
            if vor is not None:
                alt, altort, alttick = vor
                if ladung > alt:
                    menge = ladung - alt
                    d["abgeholt"] += menge
                    d["fahrten"] += 1
                    d["abhol_ticks"].append(tick)
                    d["fahrt"] = {"start": tick, "menge": menge, "ort": (e["x"], e["y"]), "weg": 0}
                    if haufen:
                        nah = min(haufen, key=lambda g: schach((e["x"], e["y"]), (g["x"], g["y"])))
                        abholung_je_haufen[nah["nr"]] = abholung_je_haufen.get(nah["nr"], 0) + menge
                if d["fahrt"] is not None and ladung > 0:
                    d["fahrt"]["weg"] += schach(altort, (e["x"], e["y"]))
                if ladung < alt:
                    d["geliefert"] += alt - ladung
                if alt > 0 and ladung == 0 and d["fahrt"] is not None:
                    d["fahrt"]["weg"] += schach(altort, (e["x"], e["y"]))
                    d["beladene_wege"].append(d["fahrt"]["weg"])
                    d["fahrt"]["abgeladen"] = tick
                    d["fahrt"]["beladen_ticks"] = tick - d["fahrt"]["start"]
            ox_vor[nr] = (ladung, (e["x"], e["y"]), tick)

    t_ende = runden[-1][0]
    brueche = []
    for nr, g in sorted(alle_g.items()):
        if g["typ"] != STEINBRUCH:
            continue
        passende = [h for h in alle_g.values() if h["typ"] == HAUFEN and h["nr"] == g.get("verbund")]
        # Der Steinbruch verweist normalerweise auf seinen Haufen. Falls dieser Verweis fehlt, ist der naechste
        # Haufen nur eine gekennzeichnete Not-Gegenprobe, keine stillschweigende Zuordnung nach Luftlinie.
        if not passende:
            passende = sorted((h for h in alle_g.values() if h["typ"] == HAUFEN),
                               key=lambda h: schach((g["x"], g["y"]), (h["x"], h["y"])))[:1]
        h = passende[0] if passende else None
        ab = besetzt_ab.get(nr)
        erzeugt = None
        rate = None
        if h:
            erzeugt = (letzte_vorraete.get(h["nr"], 0) - erste_vorraete.get(h["nr"], 0)
                        + abholung_je_haufen.get(h["nr"], 0))
            if ab is not None and t_ende > ab:
                rate = 1000.0 * erzeugt / (t_ende - ab)
        brueche.append({"nr": nr, "ort": [g["x"], g["y"]], "voll_besetzt_ab": ab,
                        "haufen": h["nr"] if h else None, "erzeugt": erzeugt,
                        "je_1000_ticks": None if rate is None else round(rate, 3)})

    ochsen = []
    for nr, d in sorted(ox_daten.items()):
        dauer = d["letzte_runde"] - d["erste_runde"]
        zyklen = d["transportzyklen"]
        transport = [z["transport_ticks"] for z in zyklen if z["transport_ticks"] > 0]
        kapazitaet = [1000.0 * z["menge"] / z["transport_ticks"] for z in zyklen if z["transport_ticks"] > 0]
        abhol_intervalle = [b - a for a, b in zip(d["abhol_ticks"], d["abhol_ticks"][1:])]
        ochsen.append({"nr": nr, "joch": d["arbeitsplatz"], "fahrten": d["fahrten"],
                       "abgeholt": d["abgeholt"], "geliefert": d["geliefert"],
                       "geliefert_je_1000_ticks": round(1000.0 * d["geliefert"] / dauer, 3) if dauer else None,
                       "beladener_weg_median": (round(statistics.median(d["beladene_wege"]), 1)
                                                if d["beladene_wege"] else None),
                       "beladen_ticks_median": (round(statistics.median(z["beladen_ticks"] for z in zyklen), 1)
                                                if zyklen else None),
                       "leer_zurueck_ticks_median": (round(statistics.median(z["leer_ticks"] for z in zyklen), 1)
                                                     if zyklen else None),
                       "transportzyklus_ticks_median": (round(statistics.median(transport), 1) if transport else None),
                       "transportkapazitaet_je_1000": (round(statistics.median(kapazitaet), 3) if kapazitaet else None),
                       "abholintervall_ticks_median": (round(statistics.median(abhol_intervalle), 1)
                                                        if abhol_intervalle else None),
                       "praktische_abholung_je_1000": (round(12000.0 / statistics.median(abhol_intervalle), 3)
                                                       if abhol_intervalle else None)})

    raten = [b["je_1000_ticks"] for b in brueche if b["je_1000_ticks"] is not None]
    aktive_ochsen = [o for o in ochsen if o["fahrten"]]
    return {"datei": os.path.normpath(pfad), "gueltig": bool(raten), "tick_von": runden[0][0], "tick_bis": t_ende,
            "steinbrueche": brueche, "joche": sum(1 for g in alle_g.values() if g["typ"] == JOCH), "ochsen": ochsen,
            "steinbruch_mittel_je_1000": round(statistics.mean(raten), 3) if raten else None,
            "aktive_ochsen": len(aktive_ochsen), "geliefert_gesamt": sum(o["geliefert"] for o in ochsen)}


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Lageprotokoll fehlt")
    ergebnisse = [auswerten(p) for p in sys.argv[1:]]
    for e in ergebnisse:
        print(json.dumps(e, ensure_ascii=False, indent=1))
    ziel = os.path.join(os.path.dirname(sys.argv[1]), "stein_auswertung.json")
    with open(ziel, "w", encoding="utf-8") as f:
        json.dump(ergebnisse, f, ensure_ascii=False, indent=1)
    print("Daten:", ziel)


if __name__ == "__main__":
    main()
