# -*- coding: utf-8 -*-
"""Lageprotokoll (Daniel 06.10. 22:39: "warum pruefst du das nicht einfach jede Runde? ... eigentlich sollte ich dich
fragen koennen, wo genau jede Einheit, jedes Gebaeude und jede Person steht, auf dem ganzen Feld").

Jede Runde wird der KOMPLETTE Abzug des Spiels gespeichert - abzug/lagebild.txt (jede Einheit der Karte, alle Spalten,
alle Besitzer, auch Tiere) und abzug/gebaeude.txt (jedes Gebaeude) - unveraendert, mit Spaltenkopf, dazu die Statuszeile.
Eine Zeile je Runde, gzip (mehrere Glieder, jede Runde angehaengt): data/research/lage_<stempel>_i<instanz>.jsonl.gz.
Nichts wird beim Schreiben gefiltert oder umgerechnet - was das Spiel abgab, liegt so in der Datei.

Abfragen (Antwort auf "wo stand X bei Tick T"):
  uv run python -m selfaware.telemetry.lageprotokoll <datei> stand  tick=T [typ=3] [besitzer=1] [nr=5] [bereich=x0,y0,x1,y1] [gebaeude=ja]
  uv run python -m selfaware.telemetry.lageprotokoll <datei> spur   nr=N [gebaeude=ja]       Weg und Zustand einer Einheit (eines Gebaeudes) je Runde
  uv run python -m selfaware.telemetry.lageprotokoll <datei> waren                          Bestand je Runde (nur Aenderungen)
  uv run python -m selfaware.telemetry.lageprotokoll <datei> art    typ=3 [besitzer=1]       Zustaende/Ladung aller Einheiten einer Art je Runde
"""
import gzip
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))



class Lageprotokoll:
    def __init__(self, pfad):
        self.pfad = pfad
        self.runden = 0

    def schreibe(self, st):
        """Nach runde_lesen() aufrufen: die Abzugsdateien sind dann die dieser Runde."""
        from selfaware.micro.tasks.waechter import LAGEBILD, GEBAEUDEDATEI
        zeile = {"t": st.get("t"), "st": st, "einheiten": open(LAGEBILD).read(), "gebaeude": open(GEBAEUDEDATEI).read()}
        with gzip.open(self.pfad, "at", encoding="utf-8") as f:
            f.write(json.dumps(zeile, ensure_ascii=False) + "\n")
        self.runden += 1
        return zeile["einheiten"], zeile["gebaeude"]      # 19.10.: fuer den Endspurt (endspurt.py), ohne zweites Lesen


# ---- lesen --------------------------------------------------------------------------------------------------------
def _tabelle(roh, kopfzeile):
    z = roh.splitlines()
    kopf = z[kopfzeile].split()
    aus = []
    for r in z[kopfzeile + 1:]:
        w = r.split()
        if len(w) >= len(kopf):
            aus.append({k: int(v) for k, v in zip(kopf, w)})
    return aus


def runden(pfad):
    with gzip.open(pfad, "rt", encoding="utf-8") as f:
        for z in f:
            r = json.loads(z)
            yield r["t"], r["st"], _tabelle(r["einheiten"], 1), _tabelle(r["gebaeude"], 0)


def _passt(d, arg):
    for k in ("typ", "besitzer", "nr"):
        if k in arg and d.get(k) != int(arg[k]):
            return False
    if "bereich" in arg:
        x0, y0, x1, y1 = map(int, arg["bereich"].split(","))
        if not (x0 <= d["x"] <= x1 and y0 <= d["y"] <= y1):
            return False
    return True


def main():
    pfad, was = sys.argv[1], sys.argv[2]
    arg = dict(a.split("=", 1) for a in sys.argv[3:])
    geb = arg.get("gebaeude") == "ja"
    if was == "stand":
        ziel = int(arg["tick"])
        best = min(runden(pfad), key=lambda r: abs(r[0] - ziel))
        t, st, E, G = best
        print("Runde bei Tick %d (gefragt %d) | %s" % (t, ziel, {k: st.get(k) for k in ("holz", "stein", "eisen", "gold", "leute", "platz", "feuer")}))
        for d in (G if geb else E):
            if _passt(d, arg):
                print(" ".join("%s=%s" % kv for kv in d.items()))
    elif was == "spur":
        n, letzte = int(arg["nr"]), None
        for t, st, E, G in runden(pfad):
            d = next((x for x in (G if geb else E) if x["nr"] == n), None)
            kurz = None if d is None else {k: d[k] for k in d if k not in ("nr",)}
            if kurz != letzte:
                print("Tick %5d: %s" % (t, kurz if kurz else "nicht da"))
                letzte = kurz
    elif was == "waren":
        letzte = None
        for t, st, E, G in runden(pfad):
            w = {k: st.get(k) for k in ("holz", "stein", "eisen", "gold", "apfel", "leute", "platz", "feuer")}
            if w != letzte:
                print("Tick %5d: %s" % (t, w))
                letzte = w
    elif was == "art":
        for t, st, E, G in runden(pfad):
            es = [d for d in E if _passt(d, arg)]
            zust = {}
            for d in es:
                k = "z%d%s" % (d["zustand"], "+%d" % d["ladung"] if d.get("ladung") else "")
                zust[k] = zust.get(k, 0) + 1
            print("Tick %5d: %d Stueck %s" % (t, len(es), dict(sorted(zust.items()))))


if __name__ == "__main__":
    main()
