# -*- coding: utf-8 -*-
"""Kampfwerte des Lords aus echten Partien messen (19.10. 18:15). Anlass: der Lord (Typ 55) fehlt in den Editor-Duellen
(daten/editor_duell_*.jsonl: 22-28, 70-76) - gefecht.dps nahm fuer ihn den Ersatzwert 20 je Takt und fuer seine Gegner
deren Mittel. Folge in 1018o: die Lordwache hielt 2 Assassinen (20.695 Leben) fuer toedlich gegen den vollen Lord und
schickte 195-mal das ganze Heer los.

Quelle: Lageprotokolle (daten/lage_*.jsonl.gz), je Runde jede Einheit mit leben, nahziel (wen sie schlaegt) und
nahangreifer (wie viele sie schlagen). Gezaehlt wird nur, was eindeutig ist:
  LORD SCHLAEGT X: in zwei aufeinanderfolgenden Runden (hoechstens MAX_DT Takte) schlaegt der Lord dieselbe Einheit X,
    X wird in beiden Runden von genau einem geschlagen und keine andere Einheit zielt auf X (zieleinheit/nahziel).
    Schaden je Takt = Lebensverlust von X / Takte.
  X SCHLAEGT LORD: in beiden Runden schlagen den Lord dieselben k Einheiten, alle vom selben Typ, und sonst zielt keine
    Einheit auf ihn. Schaden je Takt und Einheit = Lebensverlust des Lords / Takte / k.
Ergebnis: Median je Typ, Anzahl Proben, nach daten/lord_kampfwerte.json (liest gefecht.py).
Aufruf: python werkzeug/lord_messen.py [datei ...]   (ohne Angabe: alle Lageprotokolle)"""
import glob
import gzip
import json
import os
import statistics
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HIER, "..", "daten")
LORD = 55
MAX_DT = 400
ZIEL = os.path.join(D, "lord_kampfwerte.json")


def runden(pfad):
    try:
        for z in gzip.open(pfad, "rt", encoding="utf-8"):
            try:
                r = json.loads(z)
            except ValueError:
                continue
            zs = r.get("einheiten", "").split("\n")
            if len(zs) < 3:
                continue
            kopf = zs[1].split()
            try:
                i = {k: kopf.index(k) for k in ("nr", "besitzer", "typ", "leben", "zieleinheit", "nahziel", "nahangreifer")}
            except ValueError:
                continue
            E = {}
            for s in zs[2:]:
                w = s.split()
                if len(w) < len(kopf):
                    continue
                E[int(w[i["nr"]])] = {k: int(w[v]) for k, v in i.items()}
            yield r.get("t") or 0, E
    except (OSError, EOFError):
        return


def zielen_auf(E, n):
    """Wer zielt auf Einheit n (Schuss oder Schlag)?"""
    return {k for k, e in E.items() if e["zieleinheit"] == n or e["nahziel"] == n}


def messen(dateien):
    aus = {}       # Lord -> Typ
    ein = {}       # Typ -> Lord
    for f in dateien:
        alt_t, alt = None, None
        for t, E in runden(f):
            if alt is not None and 0 < t - alt_t <= MAX_DT:
                dt = t - alt_t
                for ln, l1 in alt.items():
                    if l1["typ"] != LORD or ln not in E or E[ln]["typ"] != LORD:
                        continue
                    l2 = E[ln]
                    x = l1["nahziel"]
                    if x > 0 and l2["nahziel"] == x and x in alt and x in E and alt[x]["besitzer"] != l1["besitzer"]:
                        if alt[x]["nahangreifer"] == 1 and E[x]["nahangreifer"] == 1 and zielen_auf(alt, x) <= {ln} \
                                and zielen_auf(E, x) <= {ln}:
                            v = alt[x]["leben"] - E[x]["leben"]
                            if v > 0:
                                aus.setdefault(alt[x]["typ"], []).append(v / float(dt))
                    a1 = {k for k, e in alt.items() if e["nahziel"] == ln}
                    a2 = {k for k, e in E.items() if e["nahziel"] == ln}
                    if a1 and a1 == a2 and zielen_auf(alt, ln) == a1 and zielen_auf(E, ln) == a2:
                        typen = {alt[k]["typ"] for k in a1}
                        v = l1["leben"] - l2["leben"]
                        if len(typen) == 1 and v > 0:
                            ein.setdefault(typen.pop(), []).append(v / float(dt) / len(a1))
            alt_t, alt = t, E
    zus = lambda d: {str(k): {"je_takt": round(statistics.median(v), 1), "proben": len(v)} for k, v in sorted(d.items())}
    return {"lord_an": zus(aus), "an_lord": zus(ein), "dateien": len(dateien)}


def main():
    dateien = sys.argv[1:] or sorted(glob.glob(os.path.join(D, "lage_*.jsonl.gz")))
    erg = messen(dateien)
    with open(ZIEL, "w", encoding="utf-8") as f:
        json.dump(erg, f, ensure_ascii=False, indent=1)
    print(json.dumps(erg, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
