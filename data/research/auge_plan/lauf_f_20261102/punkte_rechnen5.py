# -*- coding: utf-8 -*-
"""B-142 Lauf F: die offenen und die nicht nachgerechneten Punkte in einem Durchgang. Tabellen aus dem Speicher von Instanz 2 (nur lesend), der Rest aus der Aufzeichnung von Lauf F und Lauf K.

  PYTHONPATH="src;data/research/auge_plan/lauf_s_20261103" python data/research/auge_plan/lauf_f_20261102/punkte_rechnen5.py <prozessnummer> > data/research/auge_plan/lauf_f_20261102/punkte_rechnung5.txt
"""
import collections
import glob
import json
import os
import re
import struct
import sys

import numpy as np

import punkte_lesen as pl
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle

E = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions\%s.json"
L = pl.L
K = pl.karte
T = open(r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\types.json", encoding="utf-8").read().replace("\\n", " ")
UT = {int(v): n for n, v in re.findall(r"(UT_[A-Z0-9_]+): (\d+)", T)}
RT = {int(v): n for n, v in re.findall(r"(RT_[A-Z0-9_]+): (\d+)", T)}


def tabellen(pid):
    q = ProzessQuelle(pid)
    roh = open(q.pfad, "rb").read()

    def datei(adr, n):
        # .data beginnt bei 0x5b6000, Dateiversatz aus dem Kopf
        pe = struct.unpack_from("<I", roh, 0x3c)[0]
        for i in range(struct.unpack_from("<H", roh, pe + 6)[0]):
            s = pe + 24 + struct.unpack_from("<H", roh, pe + 20)[0] + 40 * i
            v, a, r, ra = struct.unpack_from("<IIII", roh, s + 8)
            if 0x400000 + a <= adr < 0x400000 + a + r:
                return roh[adr - 0x400000 - a + ra:adr - 0x400000 - a + ra + n]
        return None

    for name, adr, n, fmt in (("P065 Tueren", 0xb491b8, 96, "<24i"), ("P065 Lagerstelle", 0xb492d8, 48, "<12i"), ("P065 Lagerplatz", 0xb49338, 48, "<12i"), ("P070 Rang erste Zeile", 0xb4c830, 80, "<20i"), ("P070 Rang 0xb4c880", 0xb4c880, 16, "<4i"), ("P071 Zeltart", 0xb4c7cc, 36, "<9i"), ("P071 Ingenieure", 0xb4d0f0, 36, "<9i")):
        s = struct.unpack(fmt, q.lies(adr, n))
        d = datei(adr, n)
        print(name, hex(adr), "Speicher", s, "gleich wie Datei" if d is not None and bytes(q.lies(adr, n)) == d else "ANDERS als Datei: %s" % (struct.unpack(fmt, d),) if d else "keine Datei")
    for adr_f, was in (("0049f2f0", "P041"),):
        pass
    for n, a in (("P041", None),):
        for f in glob.glob(os.path.dirname(E) + r"\*.json"):
            d = json.load(open(f, encoding="utf-8"))
            if d["name"].endswith("unitIDIsRangedOrArmored"):
                z = [x["text"] for x in d["assembly"]]
                ad = [int(m, 16) for t_ in z for m in re.findall(r"0x00([0-9a-f]{6})\b", t_) if int(m, 16) > 0x5b0000]
                print("P041 Befehle mit Tabelle:", [t_ for t_ in z if re.search(r"0x00[0-9a-f]{6}", t_)][:3])
                if ad:
                    print("   Tabelle", hex(ad[0]), "Speicher", struct.unpack("<7i", q.lies(ad[0], 28)), [UT.get(x) for x in struct.unpack("<7i", q.lies(ad[0], 28))])
                break
    b = q.lies(0x4fa5e8, 0x20)
    print("P058 Sprungtabelle 0x4fa5e8, Bytes:", b.hex(), "gleich wie Datei" if datei(0x4fa5e8, 0x20) == b else "ANDERS")


def auge_datei(muster):
    f = sorted(glob.glob(os.path.join(L, muster)), key=os.path.getsize)
    return f[-1] if f else None


def waren(p):
    print("Datei", os.path.basename(p))
    auf = Aufzeichnung(p)
    basis = {b[0]: b[1] for b in auf.bereiche}
    st = K.adresse("DAT_GameState", "playerDataArray[].currentResources[]")
    u = {n: K.adresse("DAT_UnitsState", "units[]." + n) for n in ("logicalState", "unitType", "owner", "resourceToDeposit")}
    stufen = {i: collections.Counter() for i in RT if 0 <= i < 30}
    alt = None
    ladung = collections.defaultdict(collections.Counter)
    zahl = collections.Counter()
    for r, roh, _ in auf.staende():
        if not r.rein:
            continue
        n = auf.namen[r.bereich]
        if n == "DAT_GameState":
            w = struct.unpack_from("<30i", roh, st[0] + st[2] - basis[n])
            if alt is not None:
                for i, (a, b) in enumerate(zip(alt, w)):
                    if a != b and i in stufen:
                        stufen[i][b - a] += 1
            alt = w
        elif n == "DAT_UnitsState":
            a = bytes(roh)
            f = lambda x: np.ndarray(shape=(u[x][3],), dtype=pl.TYP[u[x][1]], buffer=a, offset=u[x][0] - basis[n], strides=(u[x][2],))  # noqa: E731
            d, t, l = f("logicalState"), f("unitType"), f("resourceToDeposit")
            m = (d != 0) & (l != 0)
            m[0] = False
            for ty, v in zip(t[m], l[m]):
                ladung[int(ty)][int(v)] += 1
            ki = (d != 0) & np.isin(t, [k for k, v in UT.items() if "CHILD" in v or "MOTHER" in v])
            ki[0] = False
            zahl["hoechst"] = max(zahl["hoechst"], int(ki.sum()))
    print("Waren: Stufen des Bestands von Spieler 1 (Stufe: Anzahl):")
    for i, c in sorted(stufen.items()):
        if c:
            print("  ", RT.get(i), dict(sorted(c.items(), key=lambda z: -z[1])[:6]))
    print("Ladung je Art, Wert von resourceToDeposit (Wert: Rahmen):")
    for ty, c in sorted(ladung.items()):
        print("  ", UT.get(ty, ty), "hoechstens", max(c), dict(sorted(c.items(), key=lambda z: -z[1])[:5]))
    print("Muetter und Kinder, alle Spieler, hoechstens:", zahl["hoechst"])


def sumpf():
    p = auge_datei("lauf_k_*_t1.auge")
    for t, m in pl.stand(p, "DAT_TileMapState", {"l": "LogicLayer[]", "ma": "MacroLayer[]"}, rein=False):
        lg, ma = np.array(m["l"]), np.array(m["ma"])
        break
    s = (lg & 0x20000000) != 0
    print("P059 Sumpffelder", int(s.sum()), "MacroLayer & 0x3f (Wert: Felder):", collections.Counter((ma[s] & 0x3f).tolist()).most_common(8))


def tor_bits():
    p = pl.neueste("sonder10")
    plan = pl.plan_von(p)
    g = next(x for x in plan["gebaeude"] if x.get("posten") == "tor_weg")
    fn = json.load(open(os.path.join(os.path.dirname(pl.__file__), "feldnummern.json"), encoding="utf-8"))
    S = plan["von"]
    aus = []
    for t, m in pl.stand(p, "DAT_TileMapState", {"pl": "PathLinkageLayer[]"}, rein=False):
        w = tuple(int(m["pl"][fn[g["y"] + j] + g["x"] + i]) for j in (-1, 2, 5) for i in (2,))
        if not aus or aus[-1][1] != w:
            aus.append((t - S, w))
    print("P176 Tor bei", (g["x"], g["y"]), "PathLinkageLayer (Takt, oben, Mitte, unten):", aus[:8], "pathLinkageRelated2 laut P304: 1 bei Takt 35, 2 bei 82, 3 bei 1.185, 0 bei 1.233")


if __name__ == "__main__":
    for f, a in ((tabellen, (int(sys.argv[1]),)), (waren, (auge_datei("lauf_f_20261102_214240.auge") or auge_datei("lauf_f_20261102_2142*.auge"),)), (sumpf, ()), (tor_bits, ())):
        try:
            f(*a)
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=2)
