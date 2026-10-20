# -*- coding: utf-8 -*-
"""Den Aufbau eines Gefechts aus dem Speicher lesen - Plaetze, KIs, Karte, Lords.

Wozu: vergleichen, wie das Spiel selbst (Lobby) ein Gefecht aufsetzt und wie
unser Startbefehl es tut. Laeuft im Menue, in der Lobby und im Gefecht.

Aufruf:  uv run python -m selfaware.game.ucp.aufbau
"""
import re, sys, os

from selfaware.game.ucp.befehl import sende

def peek(adr, n):
    for z in sende({"player": 1, "peek": adr, "worte": n}, 1.2):
        m = re.search(r"PEEK 0x%08X: (.*)" % adr, z)
        if m:
            return [int(w, 16) & 0xFFFFFFFF for w in m.group(1).split()]
    return None

def s32(v): return v - 0x100000000 if v > 0x7FFFFFFF else v
def byts(ws, n): return list(b"".join(w.to_bytes(4, "little") for w in ws)[:n]) if ws else None

def main():
    print("Uhr:          ", sende({"player": 1, "zeit": True}, 1.2))
    print("Ansicht:      ", peek(0x01FE7D10 + 0x0C, 1), "| Spielmodus:", peek(0x0191DD80, 1),
          "| Kampagne (isSkirmishTrail):", peek(0x01FE7D10 + 0x1F94, 1))
    kb = peek(0x01A22F9C, 10)
    print("Karte:        ", b"".join(w.to_bytes(4, "little") for w in kb).split(b"\0")[0].decode("latin-1") if kb else None)
    print("Spieler-IDs [0..8] (fullID, -1 = leer):", [s32(x) for x in (peek(0x0191DE10, 9) or [])])
    print("KI-Art      [0..8] (0 = keine KI):     ", [s32(x) for x in (peek(0x0191DE7C, 9) or [])])
    print("KI-Variante [0..8]:                    ", [s32(x) for x in (peek(0x0191DEA0, 9) or [])])
    print("Mannschaft  [0..8] (255 = nicht dabei):", byts(peek(0x01A275B4, 3), 10)[1:10])
    print("Startplatz-Liste [0..7] (246 = frei):  ", byts(peek(0x01A275D0, 2), 8))
    print("Slot des Menschen (currentPlayerSlotID):", peek(0x01A275DC, 1))
    for p in range(1, 5):
        r = peek(0x0115BDF8 + p * 0x39F4 + 0x4D0, 16)
        if r:
            print("Spieler %d Waren: Holz %d  Stein %d  Brot %d  Gold %d" % (p, s32(r[2]), s32(r[4]), s32(r[10]), s32(r[15])))
    for z in sende({"player": 1, "einheiten": True}, 2.5):
        if "Besitzer" in z or "Lords" in z:
            print("   ", z.split("]: ", 1)[-1])

if __name__ == "__main__":
    main()
