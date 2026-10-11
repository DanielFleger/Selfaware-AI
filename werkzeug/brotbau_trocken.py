# -*- coding: utf-8 -*-
"""Trockenprobe brotbau.py (SAI 11.10.): gestellte Runden, kein Spiel. Rueckgabe 0 = alles wie erwartet.
Gegenprobe: 'sabotage' setzt SPERRE auf 0 - dann MUSS Fall C (keine Doppelbestellung) rot werden."""
import sys
import brotbau as B

if "sabotage" in sys.argv:
    B.SPERRE = 0

PREIS = {30: {"holz": 18}, 34: {"holz": 18}, 17: {"holz": 12}}


def welt(gebaeude):
    return {i: {"besitzer": 1, "typ": t} for i, t in enumerate(gebaeude)}


fehler = 0
def pruefe(name, ok):
    global fehler
    fehler += not ok
    print("%s  %s" % ("OK  " if ok else "ROT ", name))


bestellt = []
bb = B.BrotBau({"getreide": [(177, 260)], "baeckereien": 2, "ab_tick": 1000}, 1, (186, 280), (200, 242),
               lambda typ, x, y, r: bestellt.append(typ) or (x, y), lambda typ: PREIS[typ])
pruefe("A vor ab_tick nichts", bb.schritt(500, {"holz": 100}, welt([])) == [] and bestellt == [])
pruefe("B ab_tick: zuerst Getreidefarm", bool(bb.schritt(1000, {"holz": 100}, welt([]))) and bestellt == [30])
pruefe("C gleiche Runde danach: keine Doppelbestellung", bb.schritt(1100, {"holz": 100}, welt([])) == [] and bestellt == [30])
pruefe("D Farm steht: Muehle", bool(bb.schritt(1200, {"holz": 100}, welt([30]))) and bestellt == [30, 34])
pruefe("E zu wenig Holz: keine Baeckerei", not [x for x in bb.schritt(1600, {"holz": 5}, welt([30, 34]))
                                               if "bestellt" in x] and bestellt == [30, 34])
pruefe("F genug Holz: Baeckerei", bool(bb.schritt(1700, {"holz": 50}, welt([30, 34]))) and bestellt == [30, 34, 17])
pruefe("G alles steht: fertig, nichts mehr", "steht" in " ".join(bb.schritt(3000, {"holz": 50}, welt([30, 34, 17, 17])))
       and bb.schritt(3100, {"holz": 50}, welt([30, 34, 17, 17])) == [] and bestellt == [30, 34, 17])
bb2 = B.BrotBau({"getreide": [(177, 260)], "baeckereien": 2, "ab_tick": 1000}, 1, (186, 280), (200, 242), None, lambda typ: PREIS[typ])
pruefe("I Ruecklage vor ab_tick leer", bb2.bedarf(500, welt([])) == {})
pruefe("J Ruecklage = Muehle, wenn die Farm steht", bb2.bedarf(1500, welt([30])) == {"holz": 18, "gold": 0})
pruefe("K Ruecklage leer, wenn alles steht", bb2.bedarf(1500, welt([30, 34, 17, 17])) == {})
pruefe("H ohne Brotplan nichts", B.BrotBau(None, 1, (0, 0), (0, 0), None, None).schritt(5000, {}, {}) == [])
print("ERGEBNIS: %d Fehler" % fehler)
raise SystemExit(1 if fehler else 0)
