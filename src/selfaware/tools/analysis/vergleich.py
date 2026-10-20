# -*- coding: utf-8 -*-
"""Zwei Schnappschuesse vergleichen: was hat sich bewegt?

Erst sammeln, dann das Klare herausfischen (Daniel, 30.09.2026). Das Werkzeug
deutet nichts - es sagt nur, WO sich WIE VIEL bewegt hat. Bei Tabellen
(Spieler, Einheiten, Gebaeude, Bauplaene) wird nach Feld zusammengefasst:
"an Stelle +X aenderte sich bei N Eintraegen etwas". Felder, die genau um die
Tickdifferenz wachsen, sind als Uhr markiert.

Aufruf:  uv run python -m selfaware.tools.analysis.vergleich <nameA> <nameB> [ausgabe.json]
Liest:   ucp/villagestudio/abzug/<name>_t<tick>_<bereich>.bin
"""
import glob, json, os, re, struct, sys
from collections import defaultdict


from selfaware.game.ucp.befehl import ABZUG as ORDNER   # Ordner der gewaehlten Instanz (SHC_INSTANZ)
# Bereich -> (Kopf in Byte, Satzgroesse in Byte, Name des Satzes); None = flach
TABELLEN = {"spieler": (0, 0x39F4, "Spieler"), "einheiten": (0, 1168, "Einheit"),
            "gebaeude": (0x14, 812, "Gebaeude"), "aiv": (4, 0x6D98, "KI-Slot")}


def lade(name):
    daten, tick = {}, None
    for pfad in glob.glob(os.path.join(ORDNER, name + "_t*_*.bin")):
        m = re.match(re.escape(name) + r"_t(\d+)_(.+)\.bin$", os.path.basename(pfad))
        if m:
            tick = int(m.group(1))
            daten[m.group(2)] = open(pfad, "rb").read()
    return tick, daten


def woerter(b):
    return struct.unpack("<%di" % (len(b) // 4), b[: len(b) // 4 * 4])


def main():
    a, b = sys.argv[1], sys.argv[2]
    ta, da = lade(a)
    tb, db = lade(b)
    dt = tb - ta
    print("Vergleich %s (Tick %d) -> %s (Tick %d), Tickdifferenz %d\n" % (a, ta, b, tb, dt))
    bericht = {"a": a, "b": b, "tick_a": ta, "tick_b": tb, "bereiche": {}}
    for bereich in sorted(da):
        if bereich not in db:
            continue
        wa, wb = woerter(da[bereich]), woerter(db[bereich])
        n = min(len(wa), len(wb))
        geaendert = [i for i in range(n) if wa[i] != wb[i]]
        eintrag = {"worte": n, "geaendert": len(geaendert)}
        print("== %-11s %7d Woerter, %6d geaendert" % (bereich, n, len(geaendert)))
        if bereich in TABELLEN and geaendert:
            kopf, satz, wort = TABELLEN[bereich]
            felder = defaultdict(list)
            for i in geaendert:
                off = i * 4 - kopf
                if off < 0:
                    felder[("Kopf", i * 4)].append((None, wa[i], wb[i]))
                else:
                    felder[("Feld", off % satz)].append((off // satz, wa[i], wb[i]))
            zeilen = []
            for (art, off), liste in sorted(felder.items(), key=lambda kv: -len(kv[1])):
                deltas = [nb - na for _, na, nb in liste]
                uhr = sum(1 for d in deltas if d == dt) >= max(1, len(deltas) // 2)
                bsp = ", ".join("%s%s:%d->%d" % (wort, "" if nr is None else nr, na, nb) for nr, na, nb in liste[:3])
                zeilen.append({"art": art, "stelle": "+0x%X" % off, "saetze": len(liste), "uhr": uhr, "beispiele": bsp})
            for z in zeilen[:25]:
                print("   %-4s %-8s in %4d %s%s  z.B. %s" % (z["art"], z["stelle"], z["saetze"], TABELLEN[bereich][2],
                      "  [TICKT MIT DER UHR]" if z["uhr"] else "", z["beispiele"]))
            if len(zeilen) > 25:
                print("   ... und %d weitere Stellen" % (len(zeilen) - 25))
            eintrag["felder"] = zeilen
        elif geaendert:
            bsp = [{"stelle": "+0x%X" % (i * 4), "a": wa[i], "b": wb[i],
                    "uhr": wb[i] - wa[i] == dt} for i in geaendert[:40]]
            for z in bsp[:12]:
                print("   %-9s %d -> %d%s" % (z["stelle"], z["a"], z["b"], "  [TICKT MIT DER UHR]" if z["uhr"] else ""))
            if len(geaendert) > 12:
                print("   ... und %d weitere" % (len(geaendert) - 12))
            eintrag["beispiele"] = bsp
        bericht["bereiche"][bereich] = eintrag
    if len(sys.argv) > 3:
        json.dump(bericht, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("\nBericht gespeichert:", sys.argv[3])


if __name__ == "__main__":
    main()
