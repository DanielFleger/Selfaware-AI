# -*- coding: utf-8 -*-
"""Selbstspiel starten und pruefen: zwei Rotkaeppchen oben/unten, kein Mensch.

Widerlegungssatz (vorher festgelegt, 30.09.2026): In N Starts hintereinander
stimmt die Startplatz-Liste, Spieler 2 und 3 haben je genau einen Lord,
Spieler 1 hat keine einzige Einheit, und die Burgen (keepX/keepY je KI-Slot)
stehen jedes Mal an derselben Stelle. Weicht ein Start ab: nicht geschafft.

Aufruf:  uv run python -m selfaware.tools.experiments.selbstspiel [anzahl_starts=3]
Nach dem letzten Start bleibt das Spiel pausiert stehen (zum Ansehen).
"""
import os, re, sys, time

from selfaware.game.ucp.befehl import sende

def peek(adr, n):
    for z in sende({"player": 1, "peek": adr, "worte": n}, 1.0):
        m = re.search(r"PEEK 0x%08X: (.*)" % adr, z)
        if m:
            return [int(w, 16) & 0xFFFFFFFF for w in m.group(1).split()]
    return None

def s32(v): return v - 0x100000000 if v > 0x7FFFFFFF else v

def ein_start(nr):
    sende({"player": 1, "menue": 41}, 3)
    sende({"player": 1, "pause": False}, 1.0)   # sonst startet das neue Gefecht eingefroren
    antwort = sende({"eigenesGefecht": True, "selbstspiel": True, "karte": "Liga_Grumpy Neighbors",
                     "ki": 1, "gegner": 2, "trotzdem": True}, 5)
    sende({"player": 1, "pause": True}, 1.0)
    tick = re.search(r"Tick (\d+)", " ".join(sende({"player": 1, "zeit": True}, 1.0)))
    liste = list(b"".join(w.to_bytes(4, "little") for w in (peek(0x01A275D0, 2) or []))[:8])
    burgen = []
    for k in (1, 2):   # aivs[] ist nach aktiver Reihenfolge gepackt
        w = peek(0x01866AB0 + 4 + k * 0x6D98, 13) or []
        if len(w) >= 13:
            burgen.append((s32(w[0]), s32(w[11]), s32(w[12])))   # playerID, keepX, keepY
    lords, einheiten = {}, {}
    for z in sende({"player": 1, "einheiten": True}, 2.0):
        m = re.search(r"Besitzer (\d+) :\s+(\d+) Einheiten, Lords: (\d+)", z)
        if m:
            einheiten[int(m.group(1))] = int(m.group(2)); lords[int(m.group(1))] = int(m.group(3))
    ergebnis = {"tick": int(tick.group(1)) if tick else None, "startliste": liste, "burgen": burgen,
                "lords": lords, "einheiten": einheiten,
                "selbstspiel_bestaetigt": any("Selbstspiel-Aufbau" in z for z in antwort)}
    print("Start %d: %s" % (nr, ergebnis))
    return ergebnis

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    laeufe = [ein_start(i + 1) for i in range(n)]
    fehler = []
    for i, r in enumerate(laeufe, 1):
        if not r["selbstspiel_bestaetigt"]:
            fehler.append("Start %d: Modul hat den Selbstspiel-Aufbau nicht gemeldet" % i)
        if r["lords"].get(2) != 1 or r["lords"].get(3) != 1:
            fehler.append("Start %d: Lords %s statt je einer bei Spieler 2 und 3" % (i, r["lords"]))
        if r["einheiten"].get(1, 0) != 0:
            fehler.append("Start %d: Spieler 1 hat %d Einheiten" % (i, r["einheiten"][1]))
        if r["startliste"] != laeufe[0]["startliste"] or r["burgen"] != laeufe[0]["burgen"]:
            fehler.append("Start %d: Startliste/Burgen anders als bei Start 1" % i)
    if fehler:
        print("NICHT GESCHAFFT:"); [print("  - " + f) for f in fehler]
        sys.exit(1)
    print("GESCHAFFT: %d Starts, jedes Mal zwei Lords (Spieler 2 und 3), kein Mensch, Burgen gleich %s"
          % (n, laeufe[0]["burgen"]))

if __name__ == "__main__":
    main()
