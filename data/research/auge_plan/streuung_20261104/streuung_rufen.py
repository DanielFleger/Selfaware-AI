# -*- coding: utf-8 -*-
"""Ruft die Zielfunktionen des Spiels direkt (Instanz 2, angehalten) und vergleicht jeden Wert mit streuung_modell.py.

Widerlegt das Modell: eine einzige Abweichung bei bekannter Zufallszahl. Schreibt nur in zwei Probe-Einheiten und den Zufallszeiger, stellt alles danach wieder her. Nichts davon geht in SamurAI.
Aufruf: streuung_rufen.py PROBE (Aufrufe je Fall). Ergebnis: streuung_rufen.txt.
"""
import json
import os
import random
import struct
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import streuung_modell as sm  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402
from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz  # noqa: E402
from selfaware.tools.experiments.spielcode_rufen import Rufer  # noqa: E402

K = Feldkarte.laden(feldliste=FELDLISTE)
UNITS = 0x1387F38
SET_RANDOM = 0x5330A0
PREPARE = 0x53CBD0
FELDER = ["unitType", "facingDirection", "microXPosition", "microYPosition", "targetingType", "shootTargetMicroX", "shootTargetMicroY", "shootTargetZ", "x", "y", "buildingHeight", "terrainOrClimbHeight", "tunnelerFinishedDigging", "stateBasedSpeed", "calculatedMovementSpeed", "fixedRng"]
ARTEN = [22, 23, 70, 72, 74, 76, 39, 40, 41, 61, 77]


def feld(n, i):
    a = K.adresse("DAT_UnitsState", "units[]." + n)
    return a[0] + i * a[2], a[1]


def main():
    probe = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    gegen = "gegen" in sys.argv  # Gegenprobe: das Modell bekommt die naechste Zufallszahl, muss also fast ueberall abweichen
    aus = []
    rnd = random.Random(20261104)
    with Rufer(pid_der_instanz(2)) as r:
        ra = K.adresse("SEC_RNG", "currentNumber2")
        ri = K.adresse("SEC_RNG", "index2")
        tab = K.adresse("SEC_RNG", "randomNumbers[]")
        print("Zufall: Feld", ra, "Zeiger", ri, "Tabelle", tab, flush=True)
        tabelle = struct.unpack("<%dh" % tab[3], r.lies(tab[0], tab[3] * tab[1])) if tab[1] == 2 else struct.unpack("<%di" % tab[3], r.lies(tab[0], tab[3] * tab[1]))
        print("Tabelle: Zahl", len(tabelle), "kleinste", min(tabelle), "groesste", max(tabelle), flush=True)
        # zwei lebende Einheiten suchen
        da = K.adresse("DAT_UnitsState", "units[].logicalState")
        lebend = [i for i in range(1, 2400) if r.lies_i(da[0] + i * da[2], da[1]) != 0]
        print("lebende Einheiten", len(lebend), lebend[:5], flush=True)
        if len(lebend) < 2:
            print("zu wenig Einheiten, Abbruch")
            return
        s, t = lebend[0], lebend[1]
        alt = {(n, i): r.lies(feld(n, i)[0], feld(n, i)[1]) for n in FELDER for i in (s, t)}
        alt_r = r.lies(ra[0], ra[1]), r.lies(ri[0], ri[1])
        # UIT_ATTACK_LAND aus dem Export
        ty = json.load(open(r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\types.json", encoding="utf-8"))
        import re
        boden = next(int(re.search(r"UIT_ATTACK_LAND: (\d+)", str(x["definition"])).group(1)) for x in ty if "UIT_ATTACK_LAND" in str(x["definition"]))
        print("UIT_ATTACK_LAND", boden, flush=True)

        def setze(n, i, w):
            a, g = feld(n, i)
            r.setze_i(a, w, g)

        def lies(n, i):
            a, g = feld(n, i)
            v = r.lies_i(a, g)
            if g == 2 and v >= 0x8000:
                v -= 0x10000
            return v

        try:
            import collections
            verbrauch = collections.Counter()
            gesichert = {"boden": [], "einheit": [], "bodenweg": []}
            t0 = time.time()
            ok = fehl = 0
            beispiele = []
            # Teil 1: Schuss auf den Boden
            for typ in ARTEN:
                setze("unitType", s, typ)
                for auf_boden in ((0, 1) if typ in (61, 77) else (0,)):
                    setze("targetingType", s, boden if auf_boden else 0)
                    for blick in range(8):
                        setze("facingDirection", s, blick)
                        for d in (6, 20, 60, 130, 500):
                            for _ in range(probe):
                                sx, sy = 1600, 1600
                                setze("microXPosition", s, sx)
                                setze("microYPosition", s, sy)
                                tx, ty_, tz = sx + d, sy - rnd.randint(0, d), rnd.randint(0, 200)
                                z = rnd.choice(tabelle)
                                r.setze_i(ra[0], z, ra[1])
                                i0 = r.lies_i(ri[0], ri[1])
                                r.rufe(SET_RANDOM, s, tx, ty_, tz, this=UNITS)
                                verbrauch[r.lies_i(ri[0], ri[1]) - i0] += 1
                                ist = (lies("shootTargetMicroX", s), lies("shootTargetMicroY", s), lies("shootTargetZ", s))
                                soll = sm.ziel_boden(typ, bool(auf_boden), sx, sy, blick, tx, ty_, tz, z + 1 if gegen else z)
                                if rnd.random() < 0.05 and sum(1 for g_ in gesichert["boden"] if g_["typ"] == typ) < 40:
                                    gesichert["boden"].append({"typ": typ, "auf_boden": auf_boden, "blick": blick, "sx": sx, "sy": sy, "tx": tx, "ty": ty_, "tz": tz, "r": z, "ist": ist})
                                if ist == soll:
                                    ok += 1
                                else:
                                    fehl += 1
                                    if len(beispiele) < 12:
                                        beispiele.append(("Boden", typ, auf_boden, blick, d, "r", z, "Spiel", ist, "Modell", soll))
            aus.append("Teil 1 Boden: gleich %d, abweichend %d, Dauer %.1f s, Zufallszahlen je Aufruf %s" % (ok, fehl, time.time() - t0, sorted(verbrauch.items())))
            aus += ["   " + str(x) for x in beispiele]
            print(aus[-1 - len(beispiele)], flush=True)
            # Teil 2: Schuss auf eine Einheit
            verbrauch2 = collections.Counter()
            t0 = time.time()
            ok = fehl = 0
            beispiele = []
            for typ in ARTEN:
                setze("unitType", s, typ)
                setze("targetingType", s, 0)
                for lauf in (0, 2):
                    setze("tunnelerFinishedDigging", t, lauf)
                    for blick in range(8):
                        setze("facingDirection", t, blick)
                        for _ in range(probe * 6):
                            ex, ey = rnd.randint(100, 300), rnd.randint(100, 300)
                            setze("x", t, ex)
                            setze("y", t, ey)
                            zb, zt = rnd.choice((0, 0, 40, 100)), rnd.randint(0, 60)
                            setze("buildingHeight", t, zb)
                            setze("terrainOrClimbHeight", t, zt)
                            eb, et = rnd.choice((0, 0, 40, 100)), rnd.randint(0, 60)
                            setze("buildingHeight", s, eb)
                            setze("terrainOrClimbHeight", s, et)
                            ts, tl = rnd.choice((0, 0, 1)), rnd.choice((0, 1, 2, 3, 4, 6))
                            setze("stateBasedSpeed", t, ts)
                            setze("calculatedMovementSpeed", t, tl)
                            re_, rz = rnd.randint(0, 32000), rnd.randint(0, 32000)
                            setze("fixedRng", s, re_)
                            setze("fixedRng", t, rz)
                            abst = rnd.randint(0, 400)
                            z = rnd.choice(tabelle)
                            r.setze_i(ra[0], z, ra[1])
                            i0 = r.lies_i(ri[0], ri[1])
                            r.rufe(PREPARE, s, t, abst, this=UNITS)
                            i1 = r.lies_i(ri[0], ri[1]) - i0
                            ist = (lies("shootTargetMicroX", s), lies("shootTargetMicroY", s), lies("shootTargetZ", s))
                            x, y, zz = sm.zielpunkt_einheit(ex, ey, zb + zt, lauf == 2, blick, abst, ts, tl)
                            sx_, sy_, sz_, zieht = sm.streuung_einheit(x, y, zz, typ, EIGEN(lies, s), z + 1 if gegen else z, re_, rz)
                            i1 = i1 % 20000  # der Zeiger springt nach 20.000 auf 0
                            verbrauch2[(typ, int(zieht), i1)] += 1
                            if rnd.random() < 0.02 and sum(1 for g_ in gesichert["einheit"] if g_["typ"] == typ) < 40:
                                gesichert["einheit"].append({"typ": typ, "lauf": lauf, "blick": blick, "ex": ex, "ey": ey, "ez": zb + zt, "abst": abst, "ts": ts, "tl": tl, "eigen": EIGEN(lies, s), "r": z, "rng_e": re_, "rng_z": rz, "ist": ist, "zog": i1})
                            if ist == (sx_, sy_, sz_) and i1 == int(zieht):
                                ok += 1
                            else:
                                fehl += 1
                                if len(beispiele) < 12:
                                    beispiele.append(("Einheit", typ, "lauf", lauf, "blick", blick, "r", z, "abst", abst, "tempo", ts, tl, "z", zz, "eigen", EIGEN(lies, s), "Spiel", ist, "Modell", (sx_, sy_, sz_)))
            aus.append("Teil 2 Einheit: gleich %d, abweichend %d, Dauer %.1f s" % (ok, fehl, time.time() - t0))
            aus.append("   Zufallszahlen (Art, Modell zieht, Spiel zog, Anzahl): " + str(sorted(verbrauch2.items())))
            aus += ["   " + str(x) for x in beispiele]
            # Teil 3: prepareProjectileTarget mit Ziel -1 (so schiesst jeder auf den Boden und jedes Geraet auf alles): beide Stufen, die zweite Zahl ist die naechste der Tabelle
            t0 = time.time()
            ok = fehl = 0
            beispiele = []
            verbrauch3 = collections.Counter()
            for typ in ARTEN:
                setze("unitType", s, typ)
                for auf_boden in ((0, 1) if typ in (61, 77) else (0,)):
                    setze("targetingType", s, boden if auf_boden else 0)
                    for blick in range(8):
                        setze("facingDirection", s, blick)
                        for d in (6, 20, 60, 130, 500):
                            for _ in range(probe):
                                sx, sy = 1600, 1600
                                setze("microXPosition", s, sx)
                                setze("microYPosition", s, sy)
                                tx, ty_, tz = sx + d, sy - rnd.randint(0, d), rnd.randint(0, 200)
                                setze("shootTargetMicroX", s, tx)
                                setze("shootTargetMicroY", s, ty_)
                                setze("shootTargetZ", s, tz)
                                eb, et = rnd.choice((0, 0, 40, 100)), rnd.randint(0, 60)
                                setze("buildingHeight", s, eb)
                                setze("terrainOrClimbHeight", s, et)
                                re_ = rnd.randint(0, 32000)
                                setze("fixedRng", s, re_)
                                i = rnd.randint(0, 19990)
                                r.setze_i(ra[0], tabelle[i], ra[1])
                                r.setze_i(ri[0], i + 1, ri[1])
                                r.rufe(PREPARE, s, 0xFFFFFFFF, 200, this=UNITS)
                                ist = (lies("shootTargetMicroX", s), lies("shootTargetMicroY", s), lies("shootTargetZ", s))
                                zog_ist = r.lies_i(ri[0], ri[1]) - (i + 1)
                                x, y, zz, zog = sm.ziel_vorbereiten_boden(typ, bool(auf_boden), sx, sy, blick, tx, ty_, tz, et, re_, tabelle, i + 1 if gegen else i)
                                verbrauch3[(typ, zog, zog_ist)] += 1
                                if rnd.random() < 0.05 and sum(1 for g_ in gesichert["bodenweg"] if g_["typ"] == typ) < 40:
                                    gesichert["bodenweg"].append({"typ": typ, "auf_boden": auf_boden, "blick": blick, "sx": sx, "sy": sy, "tx": tx, "ty": ty_, "tz": tz, "eigen": et, "rng_e": re_, "r1": tabelle[i], "r2": tabelle[i + 1], "ist": ist, "zog": zog_ist})
                                if ist == (x, y, zz) and zog == zog_ist:
                                    ok += 1
                                else:
                                    fehl += 1
                                    if len(beispiele) < 12:
                                        beispiele.append(("Boden2", typ, auf_boden, blick, d, "i", i, "eigen", et, "Spiel", ist, zog_ist, "Modell", (x, y, zz), zog))
            aus.append("Teil 3 Bodenweg mit beiden Stufen: gleich %d, abweichend %d, Dauer %.1f s" % (ok, fehl, time.time() - t0))
            aus.append("   Zufallszahlen (Art, Modell zieht, Spiel zog, Anzahl): " + str(sorted(verbrauch3.items())))
            aus += ["   " + str(x) for x in beispiele]
            print(chr(10).join(aus[-(len(beispiele) + 2):]), flush=True)
        finally:
            for (n, i), b in alt.items():
                r.schreibe(feld(n, i)[0], b) if hasattr(r, "schreibe") else r.setze_i(feld(n, i)[0], int.from_bytes(b, "little"), len(b))
            r.setze_i(ra[0], int.from_bytes(alt_r[0], "little"), ra[1])
            r.setze_i(ri[0], int.from_bytes(alt_r[1], "little"), ri[1])
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "streuung_gegenprobe.txt" if gegen else "streuung_rufen.txt"), "w", encoding="utf-8").write(text)
    if not gegen:
        with open(os.path.join(HIER, "streuung_beispiele.json"), "w", encoding="utf-8") as f:
            json.dump(gesichert, f)
    print(text)


def EIGEN(lies, s):
    """Vergleichswert des Schuetzen: nur terrainOrClimbHeight (Versatz 0x6ce), nicht die Gebaeudehoehe."""
    return lies("terrainOrClimbHeight", s)


if __name__ == "__main__":
    main()
