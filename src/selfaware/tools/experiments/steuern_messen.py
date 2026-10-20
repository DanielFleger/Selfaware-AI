# -*- coding: utf-8 -*-
"""Steuern messen (Daniel 05.10.: "es fehlt noch Steuern"; Liga-Start mit 0 Gold): je Steuerstufe Gold und Beliebtheit.

Je Stufe: Liga-Startstand laden, Steuerstufe setzen (Spielbefehl 34, ein Wert = Stufe; abgelesen ClickChangeTaxes),
<ticks> Ticks laufen lassen, dann Gold, Beliebtheit, Steuer-Anteil der Beliebtheit und Leute ablesen.
PlayerData (Spieler 1): Gold +0x50C, Beliebtheit +0x60 (Hundertstel), Steuer-Teilwert +0x215C, Steuerstufe +0x2188,
Leute +8576 (alles abgelesen/gemessen, Wissensstand 13k).

Aufruf:  uv run python -m selfaware.tools.experiments.steuern_messen [stufen=0-11] [ticks=600] [start=M19 Liga Start Grumpy T600]
Ergebnis: data/research/steuern_messung.txt
"""

from selfaware import workspace as _workspace
import os, sys, time

from selfaware.game.ucp.laden import befehl, peek, lade_stand
from selfaware.game.ucp.steuerkarte import laufe, tick

PD = 0x0115BDF8 + 1 * 0x39F4

def s32(v):
    return v - 0x100000000 if v > 0x7FFFFFFF else v

def lies():
    return {"gold": s32(peek(PD + 0x50C)[0]), "beliebt": s32(peek(PD + 0x60)[0]) / 100.0,
            "steuerteil": s32(peek(PD + 0x215C)[0]), "stufe": s32(peek(PD + 0x2188)[0]), "leute": s32(peek(PD + 8576)[0])}

def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    von, bis = (int(x) for x in arg.get("stufen", "0-11").split("-"))
    ticks = int(arg.get("ticks", 600))
    start = arg.get("start", "M19 Liga Start Grumpy T600")
    aus = os.path.join(_workspace.DATA, 'steuern_messung.txt')
    zeilen = ["# %s, %d Ticks je Stufe, Start '%s'" % (time.strftime("%d.%m.%Y %H:%M"), ticks, start),
              "stufe | gold vorher -> nachher (je 100 Ticks) | beliebt vorher -> nachher | steuerteil | leute"]
    print(zeilen[1])
    for stufe in range(von, bis + 1):
        lade_stand(start, mit_bild=False)
        befehl({"eigenerPlatz": 1}, 0.8)
        befehl({"tempo": 1000}, 0.5)
        a = lies()
        befehl({"spielbefehl": {"nr": 34, "werte": [stufe]}}, 1.0, bis="SPIELBEFEHL")
        laufe(ticks)
        b = lies()
        z = "%5d | %4d -> %4d (%+.1f) | %6.2f -> %6.2f | %5d | %d (Stufe im Spiel %d)" % (
            stufe, a["gold"], b["gold"], 100.0 * (b["gold"] - a["gold"]) / ticks, a["beliebt"], b["beliebt"],
            b["steuerteil"], b["leute"], b["stufe"])
        print(z, flush=True)
        zeilen.append(z)
        open(aus, "w", encoding="utf-8").write("\n".join(zeilen) + "\n")

if __name__ == "__main__":
    main()
