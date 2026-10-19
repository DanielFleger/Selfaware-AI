# -*- coding: utf-8 -*-
"""Lord-Ring messen, bevor er gebaut wird (Daniel 19.10. 17:51 "deinen Lord einmauern UND eingraben, um doppelt sicher zu sein";
18:58 "die Macht liegt darin zu wissen, wann der Lord Sicherheit braucht"; 19:18 "ja mach den Lord-Ring").

Bekannt: eine Mauerstrecke scheitert ganz, wenn ein Feind naeher als 15 Felder steht (validateWallBuildPath, kornring.py);
Assassinen klettern ueber Mauern; hohe Steinmauer (Mapper 25) kostet 2 Viertel Stein je Kachel (mauer_pruefen.py).
Offen und hier gemessen: halten Nahkaempfer eine Mauer auf - und wie lange?

VORHER FESTGELEGT (Totschlagtest):
  R1  Ring: hohe Steinmauer als Kasten im Abstand 2 um den Lord (16 Kacheln) -> alle 16 tragen das Mauerbit, Stein sinkt.
  R2  4 feindliche arab. Schwertkaempfer (75) 20 Felder weg, Befehl Angriff auf den Lord, 3.000 Takte: gemessen Leben des
      Lords, Mauerbit je Kachel, kleinster Abstand eines Angreifers zum Lord. RING HAELT = keine Kachel verliert ihr Bit UND
      der Lord verliert unter 5 %; RING BRICHT = eine Kachel verliert ihr Bit -> Takte bis dahin.
  R2g Gegenprobe ohne Ring (Spielstand neu, Lord am selben Platz): dieselben 4 -> der Lord verliert binnen 1.500 Takten Leben.
      Sonst wirkt der Angriffsbefehl nicht, und R2 misst nichts.
Aufruf (Spiel steht, Lenker aus): SHC_INSTANZ=4 python werkzeug/lordring_messen.py [stand="Walltest 4"] [nur=r1,r2,r2g]
Ergebnis: daten/lordring_messung_<stempel>.json"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from editor_messen import lage, setze as setze_einheit
from laden import peek, befehl, lade_stand
from steuerkarte import tick
import mauer_pruefen as MP

D = os.path.join(HIER, "..", "daten")
LORD, SCHWERT = 55, 75
RING_R = 2
FREI_R = 3                  # um den Platz muss ein 7x7-Feld frei sein (Ring + 1 Feld Rand)
STEIN = 4                   # Warenart Stein (ware(4)); Spielbefehl 38 [0, 4] kauft ein 5er-Los


def warte_ticks(n, sekunden=90):
    t0 = tick() or 0
    ende = time.time() + sekunden
    while time.time() < ende and (tick() or 0) < t0 + n:
        time.sleep(0.3)


_zeile = {}


def logik(x, y):
    if y not in _zeile:
        _zeile[y] = peek(0x023372F8 + y * 12 + 8)[0]
    return peek(MP.LOGIK + 4 * (_zeile[y] + x))[0]


def ring_kacheln(x, y, r=RING_R):
    return [(i, j) for i in range(x - r, x + r + 1) for j in range(y - r, y + r + 1) if max(abs(i - x), abs(j - y)) == r]


def platz_frei(x, y):
    return all(logik(i, j) & MP.FREI_NICHT == 0 for i in range(x - FREI_R, x + FREI_R + 1) for j in range(y - FREI_R, y + FREI_R + 1)
               if (i, j) != (x, y))


def lord_von(L, sp=1):
    return next(((n, e) for n, e in L.items() if e["besitzer"] == sp and e["typ"] == LORD and e["leben"] > 0), (None, None))


def freier_platz(lx, ly, bis=14):
    for r in range(2, bis + 1, 2):
        for dx in range(-r, r + 1, 2):
            for dy in (-r, r):
                for p in ((lx + dx, ly + dy), (lx + dy, ly + dx)):
                    if platz_frei(*p):
                        return p
    return None


def lord_hin(ln, p, sekunden=90):
    befehl({"halten": {"nr": [ln], "x": p[0], "y": p[1]}}, 1.0, bis="HALTEN")
    ende = time.time() + sekunden
    while time.time() < ende:
        _, L = lage()
        e = L.get(ln)
        if e and (e["x"], e["y"]) == p:
            return True
        time.sleep(0.5)
    return False


def mauern(p):
    x, y = p
    r = RING_R
    for (x1, y1, x2, y2, n) in ((x - r, y - r, x + r, y - r, 2 * r + 1), (x - r, y + r, x + r, y + r, 2 * r + 1),
                                (x - r, y - r + 1, x - r, y + r - 1, 2 * r - 1), (x + r, y - r + 1, x + r, y + r - 1, 2 * r - 1)):
        MP.setze(x1, y1, x2, y2, 25, n)


def mauerbits(p):
    return {k: bool(logik(*k) & 0x100) for k in ring_kacheln(*p)}


def angriff(ln, p, ticks, mit_ring):
    nrs = []
    for i in range(4):
        n = setze_einheit(2, SCHWERT, p[0] + 20, p[1] - 2 + i)
        if n:
            nrs.append(n)
    time.sleep(0.5)
    befehl({"player": 2, "angriff": {"einheiten": nrs, "ziel": ln}}, 1.0, bis="ANGRIFF")
    t0 = tick() or 0
    reihe, bruch = [], None
    i = 0
    ende = time.time() + 240
    while time.time() < ende and (tick() or 0) < t0 + ticks:
        t = (tick() or 0) - t0
        _, L = lage()
        lord = L.get(ln)
        an = [L[n] for n in nrs if n in L and L[n]["besitzer"] == 2 and L[n]["leben"] > 0]
        z = {"t": t, "lord": lord["leben"] if lord and lord["besitzer"] == 1 else 0, "angreifer": len(an),
             "naechster": min((max(abs(e["x"] - p[0]), abs(e["y"] - p[1])) for e in an), default=None),
             "ziele": sorted({(e.get("zieleinheit"), e.get("nahziel")) for e in an})[:4]}
        if mit_ring and i % 4 == 0:
            mb = mauerbits(p)
            z["mauer"] = sum(mb.values())
            if bruch is None and not all(mb.values()):
                bruch = t
        reihe.append(z)
        if z["lord"] <= 0:
            break
        i += 1
        time.sleep(0.4)
    return {"angreifer": nrs, "bruch_takt": bruch, "reihe": reihe}


def laden(stand):
    from serie import zuruecksetzen
    print("Zuruecksetzen:", zuruecksetzen(), flush=True)
    print("geladen bei Tick", lade_stand(stand, mit_bild=False), flush=True)
    _zeile.clear()
    befehl({"eigenerPlatz": 1}, 0.8)
    befehl({"pause": False}, 0.5)
    warte_ticks(50)


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    stand = arg.get("stand", "Walltest 4")
    nur = set(arg.get("nur", "r1,r2,r2g").split(","))
    erg = {"stand": stand}
    laden(stand)
    _, L = lage()
    ln, le = lord_von(L)
    if ln is None:
        raise SystemExit("kein Lord von Spieler 1")
    p = freier_platz(le["x"], le["y"])
    print("Lord %d bei (%d,%d), freier Platz %s" % (ln, le["x"], le["y"], p), flush=True)
    if p is None:
        raise SystemExit("kein freier 7x7-Platz bis 14 Felder")
    erg["platz"] = p
    erg["lord_angekommen"] = lord_hin(ln, p)
    if "r1" in nur or "r2" in nur:
        for _ in range(2):
            if MP.ware(STEIN) < 8:
                befehl({"player": 1, "spielbefehl": {"nr": 38, "werte": [0, STEIN]}}, 1.0, bis="SPIELBEFEHL")
                warte_ticks(20)
        s0 = MP.ware(STEIN)
        mauern(p)
        warte_ticks(10)
        mb = mauerbits(p)
        erg["r1"] = {"stein": [s0, MP.ware(STEIN)], "mauer": sum(mb.values()), "kacheln": len(mb),
                     "fehlend": [k for k, v in mb.items() if not v]}
        print("R1 Ring: %d von %d Kacheln mit Mauerbit, Stein %d -> %d, fehlend %s" % (
            erg["r1"]["mauer"], len(mb), s0, erg["r1"]["stein"][1], erg["r1"]["fehlend"]), flush=True)
    if "r2" in nur:
        r2 = angriff(ln, p, 3000, True)
        erg["r2"] = r2
        rh = r2["reihe"]
        print("R2 mit Ring: Lord %s -> %s, Mauer zuletzt %s, Bruch bei %s, naechster Angreifer zuletzt %s, Ziele %s" % (
            rh[0]["lord"] if rh else None, rh[-1]["lord"] if rh else None, next((z["mauer"] for z in reversed(rh) if "mauer" in z), None),
            r2["bruch_takt"], rh[-1]["naechster"] if rh else None, rh[-1]["ziele"] if rh else None), flush=True)
    if "r2g" in nur:
        laden(stand)
        _, L = lage()
        ln, le = lord_von(L)
        erg["r2g_lord_angekommen"] = lord_hin(ln, p)
        r2g = angriff(ln, p, 1500, False)
        erg["r2g"] = r2g
        rh = r2g["reihe"]
        print("R2g ohne Ring (Gegenprobe): Lord %s -> %s, naechster Angreifer zuletzt %s" % (
            rh[0]["lord"] if rh else None, rh[-1]["lord"] if rh else None, rh[-1]["naechster"] if rh else None), flush=True)
    befehl({"pause": True}, 0.5)
    pfad = os.path.join(D, "lordring_messung_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
    json.dump(erg, open(pfad, "w", encoding="utf-8"), ensure_ascii=False)
    print("gesichert:", pfad)


if __name__ == "__main__":
    main()
