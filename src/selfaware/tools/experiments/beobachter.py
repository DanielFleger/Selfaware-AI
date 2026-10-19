# -*- coding: utf-8 -*-
"""Ein laufendes Gefecht mitschreiben, bis es endet.

Schreibt alle paar Sekunden eine Zeile JSON: Zeit, Tick, Einheiten und Lords
je Spieler, Gold/Holz/Brot je Spieler. Endet, wenn die Uhr dreimal
hintereinander steht, auf 0 springt oder nach der Hoechstdauer.

Aufruf:  uv run python -m selfaware.tools.experiments.beobachter <ausgabe.jsonl> [abstand_s] [hoechstdauer_min]
"""
import io, json, os, re, sys, time

from selfaware.game.ucp.befehl import sende

def s32(v): return v - 0x100000000 if v > 0x7FFFFFFF else v

def probe():
    z = " ".join(sende({"player": 1, "zeit": True}, 1.0))
    m = re.search(r"Tick (\d+)", z)
    tick = int(m.group(1)) if m else None
    einheiten, lords = {}, {}
    for zeile in sende({"player": 1, "einheiten": True}, 1.8):
        m = re.search(r"Besitzer (\d+) :\s+(\d+) Einheiten, Lords: (\d+)", zeile)
        if m:
            einheiten[m.group(1)] = int(m.group(2)); lords[m.group(1)] = int(m.group(3))
    waren = {}
    for p in (1, 2, 3, 4):
        adr = 0x0115BDF8 + p * 0x39F4 + 0x4D0
        for zeile in sende({"player": 1, "peek": adr, "worte": 16}, 1.0):
            m = re.search(r"PEEK 0x%08X: (.*)" % adr, zeile)
            if m:
                w = [s32(int(x, 16) & 0xFFFFFFFF) for x in m.group(1).split()]
                waren[str(p)] = {"holz": w[2], "stein": w[4], "brot": w[10], "gold": w[15]}
    return {"zeit": time.strftime("%H:%M:%S"), "tick": tick, "einheiten": einheiten, "lords": lords, "waren": waren}

def main():
    ziel = sys.argv[1]
    abstand = float(sys.argv[2]) if len(sys.argv) > 2 else 5
    ende = time.time() + 60 * (float(sys.argv[3]) if len(sys.argv) > 3 else 40)
    vorher, gleich = None, 0
    while time.time() < ende:
        p = probe()
        io.open(ziel, "a", encoding="utf-8").write(json.dumps(p, ensure_ascii=False) + "\n")
        print(p["zeit"], "Tick", p["tick"], "Lords", p["lords"], "Einheiten", p["einheiten"], flush=True)
        if p["tick"] is not None and vorher is not None:
            if p["tick"] == 0 and vorher > 0:
                print("ENDE: Uhr auf 0 - Gefecht verlassen"); break
            gleich = gleich + 1 if p["tick"] == vorher else 0
            if gleich >= 3:
                print("ENDE: Uhr steht seit drei Proben"); break
        vorher = p["tick"]
        time.sleep(abstand)

if __name__ == "__main__":
    main()
