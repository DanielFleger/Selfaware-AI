# -*- coding: utf-8 -*-
"""Der Zielpunkt jedes aufgezeichneten Schusses gegen streuung_modell.py.

Je Schuss: Der Punkt, den das Geschoss traegt (targetX, targetY, targetZ), muss aus dem Zustand von Schuetze und Ziel folgen, mit einer Zufallszahl, die in genau diesem Takt verbraucht wurde (Tabelle plus Zufallszeiger aus der Aufzeichnung).
Widerlegt das Modell: ein Schuss, zu dem keine Zufallszahl des Takts passt.
Dazu: Wandert der Zielpunkt beim Schuss auf den Boden von Schuss zu Schuss (Die Funktion ueberschreibt ihren eigenen Ausgangspunkt)?
Aufruf: ziel_pruefen.py [Muster ...]. Ausgabe: ziel_pruefung.txt
"""
import collections
import glob
import os
import struct
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import flug_pruefen as fp  # noqa: E402
import streuung_modell as sm  # noqa: E402
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

fp.U_F.update({"blick": "facingDirection", "lauf": "tunnelerFinishedDigging", "ts": "stateBasedSpeed", "tl": "calculatedMovementSpeed", "rng": "fixedRng", "mxx": "microXPosition", "myy": "microYPosition", "sx": "shootTargetMicroX", "sy": "shootTargetMicroY", "sz": "shootTargetZ", "tgt": "targetingType", "schiesst": "shootTargetedUnit"})
BODEN = 5


def zufall_lesen(pfad, k):
    auf = Aufzeichnung(pfad)
    ir = auf.namen.index("SEC_RNG")
    br = auf.bereiche[ir][1]
    a_i = k.adresse("SEC_RNG", "index2")
    a_t = k.adresse("SEC_RNG", "randomNumbers[]")
    a_c = k.adresse("SEC_RNG", "currentNumber2")
    zeiger, tab, jetzt = {}, None, {}
    for r, p, _ in auf.staende():
        if r.bereich == ir and r.rein:
            b = bytes(p)
            zeiger[r.takt] = struct.unpack_from("<i", b, a_i[0] - br)[0]
            jetzt[r.takt] = struct.unpack_from("<h", b, a_c[0] - br)[0]
            if tab is None:
                tab = struct.unpack_from("<%dh" % a_t[3], b, a_t[0] - br)
    return zeiger, tab, jetzt


def kandidaten(t, zeiger, tab):
    """Alle Zufallszahlen, die im Takt t als aktuelle Zahl galten. Die aktuelle Zahl ist immer die zuletzt gezogene."""
    if t - 1 not in zeiger or t not in zeiger:
        return None
    a, b = zeiger[t - 1], zeiger[t]
    if b < a:
        b += 20000
    return [tab[(i - 1) % 20000] for i in range(a, b + 1)]


def plaetze(t, zeiger):
    """Die Plaetze der Tabelle, deren Zahl im Takt t als aktuelle Zahl galt."""
    a, b = zeiger[t - 1], zeiger[t]
    if b < a:
        b += 20000
    return [(i - 1) % 20000 for i in range(a, b + 1)]


def pruefe(pfad, k):
    lauf = fp.Lauf(pfad, k)
    zeiger, tab, _ = zufall_lesen(pfad, k)
    u = lauf.u
    erg = collections.Counter()
    fehl = []
    abstand_z = collections.Counter()
    wandern = collections.defaultdict(list)
    vorig = {}  # (Schuetze, Takt): Punkt des vorigen Steins derselben Salve
    for s, f in sorted(lauf.fluege.items(), key=lambda x: (x[1][0][0], x[0][0])):
        z = f[0][1]
        t = f[0][0]
        if z["wg"] != 0 or t not in u or t - 1 not in u:
            erg[(z["art"], "nicht geprueft: Takt fehlt")] += 1
            continue
        kand = kandidaten(t, zeiger, tab)
        if kand is None:
            erg[(z["art"], "nicht geprueft: Zufall fehlt")] += 1
            continue
        sch = z["sch"]
        q0, q1 = u[t - 1], u[t]
        typ = int(q0["typ"][sch])
        ziel = int(q1["schiesst"][sch])
        if typ in (39, 40, 41, 61):
            auf_einheit = False  # Geraete rufen immer den Bodenweg (UpdateCatapult, UpdateTrebuchet, UpdateMangonel, UpdateBallista)
        elif typ == 77:
            auf_einheit = ziel >= 1
        else:
            auf_einheit = ziel >= 0
        treffer = False
        zusatz = None
        if auf_einheit:
            for q in (q0, q1):
                ez = int(q["hb"][ziel]) + int(q["ht"][ziel])
                ab = max(abs(int(q["mxx"][sch]) - int(q["mxx"][ziel])), abs(int(q["myy"][sch]) - int(q["myy"][ziel]))) - 1
                for ab_ in ((ab, ab + 1, ab - 1) if typ != 77 else (200,)):
                    x, y, zz = sm.zielpunkt_einheit(int(q["x"][ziel]), int(q["y"][ziel]), ez, int(q["lauf"][ziel]) == 2, int(q["blick"][ziel]), ab_, int(q["ts"][ziel]), int(q["tl"][ziel]))
                    for r in kand:
                        sx, sy, sz, _ = sm.streuung_einheit(x, y, zz, typ, int(q0["ht"][sch]), r, int(q0["rng"][sch]), int(q["rng"][ziel]))
                        if (sx, sy) == (z["zx"], z["zy"]) and z["zz"] - sz in (0, 26, 30, 45):
                            treffer = True
                            zusatz = z["zz"] - sz
                            break
                    if treffer:
                        break
                if treffer:
                    break
        else:
            bx, by, bz = vorig.get((sch, t), (int(q0["sx"][sch]), int(q0["sy"][sch]), int(q0["sz"][sch])))
            auf_boden = int(q0["tgt"][sch]) == BODEN
            zusaetze = (0,) if typ in (39, 40, 41) else (0, 26, 30)
            for bl in (int(q1["blick"][sch]), int(q0["blick"][sch])):
                for i in plaetze(t, zeiger):
                    sx, sy, sz, _ = sm.ziel_vorbereiten_boden(typ, auf_boden, int(q0["mxx"][sch]), int(q0["myy"][sch]), bl, bx, by, bz, int(q0["ht"][sch]), int(q0["rng"][sch]), tab, i)
                    if (sx, sy) == (z["zx"], z["zy"]) and z["zz"] - sz in zusaetze:
                        treffer = True
                        zusatz = z["zz"] - sz
                        vorig[(sch, t)] = (sx, sy, sz)
                        break
                if treffer:
                    break
            wandern[(sch, typ)].append((t, z["zx"], z["zy"], z["zz"], bx, by, bz))
        erg[(z["art"], typ, "auf Einheit" if auf_einheit else "Bodenweg", "passt" if treffer else "PASST NICHT")] += 1
        if treffer:
            abstand_z[(z["art"], typ, zusatz)] += 1
        elif len(fehl) < 15:
            gefunden = []
            fehl.append((os.path.basename(pfad), s, "Art", z["art"], "Typ", typ, "Takt", t, "schiesst", ziel, "Punkt", z["zx"], z["zy"], z["zz"], "Zahlen", len(kand), "Schuetze", int(q0["mxx"][sch]), int(q0["myy"][sch]), "Blick", int(q0["blick"][sch]), int(q1["blick"][sch]), "Ziel-Art", int(q0["tgt"][sch]), "Basis", bx, by, bz, "Fundstellen relativ", gefunden[:4]))
    return erg, fehl, abstand_z, wandern


def main():
    k = Feldkarte.laden(feldliste=FELDLISTE)
    muster = sys.argv[1:] or ["lauf_s_*_beschuss.auge"]
    dateien = []
    for m in muster:
        dateien += sorted(glob.glob(os.path.join(HIER, "..", "laeufe", m)))
    summe, zs = collections.Counter(), collections.Counter()
    alle_fehl = []
    aus = []
    for d in dateien:
        try:
            e, fe, a, w = pruefe(d, k)
        except Exception as x:
            aus.append("%s: nicht lesbar %r" % (os.path.basename(d), x))
            continue
        summe.update(e)
        zs.update(a)
        alle_fehl += fe
        if w:
            aus.append(os.path.basename(d) + ": Schuss auf den Boden, Zielpunkt je Schuss (Schuetze, Typ: Takt, Punkt):")
            for (sch, typ), l in sorted(w.items()):
                aus.append("   %d Typ %d: %s" % (sch, typ, [(x[1], x[2], x[3]) for x in l[:10]]))
    aus.append("SUMME: " + str(sorted(summe.items(), key=str)))
    aus.append("Hoehen-Zusatz (Art, Zusatz): " + str(sorted(zs.items(), key=str)))
    aus.append("Passt nicht, Beispiele:")
    aus += ["  " + str(x) for x in alle_fehl[:15]]
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "ziel_pruefung.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
