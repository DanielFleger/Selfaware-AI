# -*- coding: utf-8 -*-
"""Was passiert IM Betrieb? (SAI 12.10., Daniel 01:26: "warum liest du die Ressourcen im Lager - das sind vielleicht 10 %
der Infos; in der Mine selbst sind die ganzen Infos, lieber dort messen und daraus eine kohaerente Idee entwickeln").

Liest aus einem Lauf von arbeitsgang_rohstoff.py die mitgeschriebenen GANZEN Gebaeude-Datensaetze (je Betrieb alle 50 Ticks,
203 Worte ab Gebaeude+0x14 = Ghidra-Offsets) und benennt jedes Wort, das sich im Lauf aendert, mit dem Feldnamen aus
data/research/struktur_Building.txt (== Building, 812 Byte). Je Feld: Zahl der Aenderungen, Wertebereich, und
  - Zaehler (steigt in Schritten): Zuwachs je 1.000 Ticks (z.B. resourceIron = Erz im Betrieb),
  - Zeitgeber (zaehlt herunter und springt zurueck): mittlere Periode in Ticks.
Kurze Worte (short) werden einzeln ausgewertet (unteres/oberes Halbwort).
Aufruf: uv run python -m selfaware.tools.analysis.gebaeude_auswerten [data/research/arbeitsgang_rohstoff_....json] [nur=5,20,21]"""

from selfaware import workspace as _workspace
import glob
import json
import os
import re
import statistics as S
import sys
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(_workspace.DATA)
TYPNAME = {3: "Holzfaeller", 4: "Ochsenkarren", 5: "Eisenmine", 6: "Pechgraeber", 20: "Steinbruch", 21: "Steinhaufen",
           31: "Hopfenfarm"}


def felder():
    """[(Offset, Name, Typ)] des Building-Datensatzes."""
    aus, drin = [], False
    for z in open(os.path.join(D, "struktur_Building.txt"), encoding="utf-8"):
        if z.startswith("== "):
            drin = z.startswith("== Building ")
            continue
        m = re.match(r"\s+\+(\d+)\s+(\S+)\s+(.*)", z)
        if drin and m:
            aus.append((int(m.group(1)), m.group(2), m.group(3).strip()))
    return aus


def name_an(feld_liste, byte):
    kand = [f for f in feld_liste if f[0] <= byte]
    return kand[-1] if kand else (byte, "?", "?")


def s16(v):
    return v - 0x10000 if v & 0x8000 else v


def s32(v):
    return v - 0x100000000 if v & 0x80000000 else v


def art_der_reihe(reihe):
    """Zaehler / Zeitgeber / Wechsel - und die Kennzahl dazu."""
    werte = [w for _, w in reihe]
    auf = sum(1 for a, b in zip(werte, werte[1:]) if b > a)
    ab = sum(1 for a, b in zip(werte, werte[1:]) if b < a)
    if auf and not ab:
        d = reihe[-1][0] - reihe[0][0]
        return "Zaehler", round(1000.0 * (werte[-1] - werte[0]) / d, 2) if d else None
    if ab > auf * 2 and auf:
        spruenge = [t for (t, a), (_, b) in zip(reihe, reihe[1:]) if b > a]
        per = [b - a for a, b in zip(spruenge, spruenge[1:])]
        return "Zeitgeber", round(S.median(per)) if per else None
    return "Wechsel", None


def main():
    args = [a for a in sys.argv[1:] if "=" not in a]
    opt = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    pfad = args[0] if args else sorted(glob.glob(os.path.join(D, "arbeitsgang_rohstoff_2*[0-9].json")))[-1]
    nur = {int(x) for x in opt["nur"].split(",")} if "nur" in opt else None
    d = json.load(open(pfad, encoding="utf-8"))
    fl = felder()
    gd = d.get("gebaeude_daten", {})
    print("Datei:", os.path.basename(pfad), "| Betriebe mit Datensatz:", len(gd))
    erg = {}
    for nr, e in sorted(gd.items(), key=lambda x: (x[1]["typ"], int(x[0]))):
        if nur and e["typ"] not in nur:
            continue
        reihe = e["reihe"]
        if len(reihe) < 3:
            continue
        aend = []
        for k in range(len(reihe[0][1])):
            ws = [(t, w[k]) for t, w in reihe if k < len(w)]
            if len({w for _, w in ws}) <= 1:
                continue
            byte = 4 * k
            f0, f2 = name_an(fl, byte), name_an(fl, byte + 2)
            if f0[0] != f2[0] and f0[0] == byte and f2[0] == byte + 2:     # zwei Halbworte = zwei Felder
                for teil, f, schieb in (("lo", f0, 0), ("hi", f2, 16)):
                    r = [(t, s16((w >> schieb) & 0xFFFF)) for t, w in ws]
                    if len({w for _, w in r}) > 1:
                        a, kz = art_der_reihe(r)
                        aend.append(dict(off=f[0], name=f[1], typ=f[2], art=a, kennzahl=kz, aenderungen=sum(
                            1 for x, y in zip(r, r[1:]) if x[1] != y[1]), min=min(w for _, w in r), max=max(w for _, w in r)))
            else:
                r = [(t, s32(w)) for t, w in ws]
                a, kz = art_der_reihe(r)
                aend.append(dict(off=byte, name=f0[1] if f0[0] == byte else "%s+%d" % (f0[1], byte - f0[0]), typ=f0[2], art=a,
                                 kennzahl=kz, aenderungen=sum(1 for x, y in zip(r, r[1:]) if x[1] != y[1]),
                                 min=min(w for _, w in r), max=max(w for _, w in r)))
        erg[nr] = dict(typ=e["typ"], ort=e["ort"], felder=aend)
        print("\n%s Nr %s bei %s (%d Stiche, Tick %d-%d):" % (TYPNAME.get(e["typ"], e["typ"]), nr, tuple(e["ort"]), len(reihe),
                                                             reihe[0][0], reihe[-1][0]))
        for f in aend:
            print("   +%-4d %-34s %-9s %-10s Aenderungen %4d  Bereich %s..%s" % (
                f["off"], f["name"][:34], f["art"], f["kennzahl"] if f["kennzahl"] is not None else "", f["aenderungen"],
                f["min"], f["max"]))
    json.dump(erg, open(pfad.replace(".json", "_gebaeude.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
