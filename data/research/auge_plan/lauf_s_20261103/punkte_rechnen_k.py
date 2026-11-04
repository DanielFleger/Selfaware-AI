# -*- coding: utf-8 -*-
"""B-142 Lauf S: Die Punkte, die eine KI brauchen, aus der Aufzeichnung von Lauf K (8 KI-Lords): P319, P320, P370, P308. Ein Durchgang ueber die Datei, kein Zwischenspeicher, Teilergebnis wird laufend geschrieben (Lauf K: 38 GB).

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/punkte_rechnen_k.py [datei] > data/research/auge_plan/lauf_s_20261103/punkte_rechnung_k.txt
"""
import collections
import os
import struct
import sys

import numpy as np

import punkte_lesen as pl
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung

DATEI = sys.argv[1] if len(sys.argv) > 1 else os.path.join(pl.L, "lauf_k_20261102_234952_danach.auge")
K = pl.karte
ASSASSINE, KATAPULT, TREBUCHET = 73, 39, 40
A = {n: K.adresse("DAT_GameState", "playerDataArray[]." + n) for n in ("totalAssassinTroops", "totalAttackTroops", "closestEnemyDistanceToTheLord", "aivID")}
STEIN = K.adresse("DAT_GameState", "playerDataArray[].currentResources[]")
U = {n: K.adresse("DAT_UnitsState", "units[]." + n) for n in ("logicalState", "unitType", "owner", "stoneAmmunition", "health", "aiUnitBehaviourType", "workplaceBuildingID_1", "targetX_2", "targetY_2")}
B = {n: K.adresse("DAT_BuildingsState", "buildings[]." + n) for n in ("logicalState", "buildingType", "idleTimerUnk", "owner", "x", "y", "uid")}
ZUSTAND = U["logicalState"][0] + 564
STEINMETZ, MOENCH, STEINBRUCH, KATHEDRALE = 7, 37, 20, 38
H = K.adresse("DAT_AIVState", "heatMaps[][].destructionBasedPlacementCooldown")
S_ST = K.adresse("DAT_AIVState", "aivs[].aivBuildingSteps[].buildStatus")
S_W = K.adresse("DAT_AIVState", "aivs[].aivBuildingSteps[].wait")
SCHRITT = K.adresse("DAT_AIVState", "aivs[].aivBuildingSteps[]")
AIV_N = K.adresse("DAT_AIVState", "aivs[].totalSteps")


def feld(a, roh, basis, i):
    adr, g, schritt, _ = a
    return struct.unpack_from({1: "<b", 2: "<h", 4: "<i"}[g], roh, adr + i * schritt - basis)[0]


def main():
    auf = Aufzeichnung(DATEI)
    basis = {b[0]: b[1] for b in auf.bereiche}
    print("Datei", os.path.basename(DATEI), "Bereiche", auf.namen, flush=True)
    t0 = None
    # P370
    assassinen = {sp: [] for sp in range(1, 9)}
    angriff = {sp: [] for sp in range(1, 9)}
    zahl = {sp: [] for sp in range(1, 9)}
    # P308
    mun = {}
    stein = {sp: 0 for sp in range(1, 9)}
    stein_vor = {sp: 0 for sp in range(1, 9)}
    auf_mun = []
    # P319
    naehe = {sp: [] for sp in range(1, 9)}
    wait_alt = {}
    aiv_von = {}
    wechsel = collections.Counter()
    wechsel_beispiele = []
    # P320
    kuehl_alt = None
    kuehl = collections.Counter()
    kuehl_beispiele = {}
    rahmen = collections.Counter()
    # P350, P358, P370: Steinbruch, Moench, Assassinen-Auftrag
    bruch = {}
    bruch_sprung = []
    arten = None
    mason = set()
    mason_tod = []
    moench_zustand = collections.Counter()
    moench_ziel = {}
    moench_folge = []
    auftrag = collections.Counter()
    # P319: Bau an einer Stelle, an der schon einmal dasselbe stand
    uid_alt = None
    gesehen = set()
    wiederaufbau = collections.Counter()
    wiederaufbau_nah = []
    for r, roh, _ in auf.staende():
        name = auf.namen[r.bereich]
        if not r.rein:
            continue
        rahmen[name] += 1
        t0 = t0 if t0 is not None else r.takt
        t = r.takt - t0
        if name == "DAT_GameState":
            b = basis[name]
            for sp in range(1, 9):
                for reihe, a in ((assassinen, A["totalAssassinTroops"]), (angriff, A["totalAttackTroops"]), (naehe, A["closestEnemyDistanceToTheLord"])):
                    w = feld(a, roh, b, sp)
                    if not reihe[sp] or reihe[sp][-1][1] != w:
                        reihe[sp].append((t, w))
                aiv_von[sp] = feld(A["aivID"], roh, b, sp)
                stein_vor[sp] = stein[sp]
                stein[sp] = struct.unpack_from("<i", roh, STEIN[0] + sp * STEIN[2] + 4 * 4 - b)[0]
        elif name == "DAT_BuildingsState":
            b = basis[name]
            a = bytes(roh)
            art = np.ndarray(shape=(B["buildingType"][3],), dtype="<i2", buffer=a, offset=B["buildingType"][0] - b, strides=(B["buildingType"][2],))
            da = np.ndarray(shape=(B["logicalState"][3],), dtype="<i2", buffer=a, offset=B["logicalState"][0] - b, strides=(B["logicalState"][2],))
            uhr = np.ndarray(shape=(B["idleTimerUnk"][3],), dtype=pl.TYP[B["idleTimerUnk"][1]], buffer=a, offset=B["idleTimerUnk"][0] - b, strides=(B["idleTimerUnk"][2],))
            arten = art.copy()
            f_ = lambda n: np.ndarray(shape=(B[n][3],), dtype=pl.TYP[B[n][1]], buffer=a, offset=B[n][0] - b, strides=(B[n][2],))  # noqa: E731
            uid = f_("uid")
            wem_b, x_b, y_b = f_("owner"), f_("x"), f_("y")
            neu = np.nonzero((uid != uid_alt) & (da != 0))[0] if uid_alt is not None else np.nonzero(da != 0)[0]
            for i in neu:
                i = int(i)
                sp, ort = int(wem_b[i]), (int(art[i]), int(x_b[i]), int(y_b[i]))
                if 1 <= sp <= 8:
                    if (sp, ort) in gesehen and uid_alt is not None:
                        nah = naehe[sp][-1][1] < 120 if naehe[sp] else False
                        wiederaufbau[(nah, ort[0])] += 1
                        if nah and len(wiederaufbau_nah) < 12:
                            wiederaufbau_nah.append((t, sp, ort, naehe[sp][-1]))
                    gesehen.add((sp, ort))
            uid_alt = uid.copy()
            for i in np.nonzero((da != 0) & (art == STEINBRUCH))[0]:
                i = int(i)
                w = int(uhr[i])
                alt = bruch.get(i)
                if alt is not None and w > alt + 100:
                    bruch_sprung.append((t, i, alt, w))
                bruch[i] = w
        elif name == "DAT_UnitsState":
            b = basis[name]
            a = bytes(roh)
            feld_ = lambda n: np.ndarray(shape=(U[n][3],), dtype=pl.TYP[U[n][1]], buffer=a, offset=U[n][0] - b, strides=(U[n][2],))  # noqa: E731
            d_ = feld_("logicalState")
            ty_ = feld_("unitType")
            zu_ = np.ndarray(shape=(U["logicalState"][3],), dtype="<i2", buffer=a, offset=ZUSTAND - b, strides=(U["logicalState"][2],))
            jetzt_m = {int(i) for i in np.nonzero((d_ != 0) & (ty_ == STEINMETZ))[0] if i}
            for i in mason - jetzt_m:
                mason_tod.append((t, i))
            mason = jetzt_m
            for i in np.nonzero((d_ != 0) & (ty_ == MOENCH))[0]:
                i = int(i)
                if not i:
                    continue
                z = int(zu_[i])
                wo = int(feld_("workplaceBuildingID_1")[i])
                moench_zustand[(z, int(arten[wo]) if arten is not None and 0 <= wo < len(arten) else None)] += 1
                if z == 0x69:
                    ziel = (int(feld_("targetX_2")[i]), int(feld_("targetY_2")[i]))
                    if moench_ziel.get(i) != ziel and len(moench_folge) < 30:
                        moench_folge.append((t, i, ziel))
                    moench_ziel[i] = ziel
            for i in np.nonzero((d_ != 0) & (ty_ == ASSASSINE))[0]:
                if i:
                    auftrag[int(feld_("aiUnitBehaviourType")[i])] += 1
            da = np.ndarray(shape=(U["logicalState"][3],), dtype="<i2", buffer=a, offset=U["logicalState"][0] - b, strides=(U["logicalState"][2],))
            typ = np.ndarray(shape=(U["unitType"][3],), dtype="<i2", buffer=a, offset=U["unitType"][0] - b, strides=(U["unitType"][2],))
            wem = np.ndarray(shape=(U["owner"][3],), dtype="<i2", buffer=a, offset=U["owner"][0] - b, strides=(U["owner"][2],))
            am = np.ndarray(shape=(U["stoneAmmunition"][3],), dtype="<i2", buffer=a, offset=U["stoneAmmunition"][0] - b, strides=(U["stoneAmmunition"][2],))
            m = (da != 0) & (typ == ASSASSINE)
            m[0] = False
            for sp in range(1, 9):
                w = int((m & (wem == sp)).sum())
                if not zahl[sp] or zahl[sp][-1][1] != w:
                    zahl[sp].append((t, w))
            g = (da != 0) & ((typ == KATAPULT) | (typ == TREBUCHET))
            g[0] = False
            jetzt = set()
            for i in np.nonzero(g)[0]:
                i = int(i)
                jetzt.add(i)
                w = int(am[i])
                alt = mun.get(i)
                if alt is not None and w > alt:
                    sp = int(wem[i])
                    auf_mun.append((t, i, int(typ[i]), sp, alt, w, stein_vor.get(sp), stein.get(sp)))
                mun[i] = w
            for i in list(mun):
                if i not in jetzt:
                    del mun[i]
        elif name == "DAT_AIVState":
            b = basis[name]
            a = bytes(roh)
            werte = np.ndarray(shape=(H[3] * H[3],), dtype="u1", buffer=a, offset=H[0] - b, strides=(H[2],))
            if kuehl_alt is not None:
                d = np.nonzero(werte != kuehl_alt)[0]
                for i in d:
                    i = int(i)
                    vor, nach = int(kuehl_alt[i]), int(werte[i])
                    kuehl[(vor, nach)] += 1
                    if len(kuehl_beispiele) < 40 or i in kuehl_beispiele:
                        kuehl_beispiele.setdefault(i, []).append((t, nach))
            kuehl_alt = werte.copy()
            # P319: Warte-Wert und Stand je Schritt, getrennt nach Lord in Gefahr oder nicht
            for sp in range(1, 9):
                aiv = aiv_von.get(sp)
                if aiv is None or aiv <= 0:
                    continue
                n = struct.unpack_from("<i", a, AIV_N[0] + aiv * AIV_N[2] - b)[0]
                nah = naehe[sp][-1][1] < 120 if naehe[sp] else False
                n = min(n, 2300)
                stand = np.frombuffer(a, dtype="u1", count=n * SCHRITT[1], offset=S_ST[0] + aiv * S_ST[2] + SCHRITT[1] - b)[::SCHRITT[1]]
                warte = np.frombuffer(a, dtype="u1", count=n * SCHRITT[1], offset=S_W[0] + aiv * S_W[2] + SCHRITT[1] - b)[::SCHRITT[1]]
                alt = wait_alt.get(sp)
                if alt is not None and len(alt[0]) == n:
                    for st in np.nonzero((alt[0] != stand) | (alt[1] != warte))[0]:
                        st = int(st)
                        vor, nach = (int(alt[0][st]), int(alt[1][st])), (int(stand[st]), int(warte[st]))
                        wechsel[(nah, vor[0], nach[0], "runter" if nach[1] < vor[1] else "hoch" if nach[1] > vor[1] else "")] += 1
                        if nah and vor[0] == 3 and len(wechsel_beispiele) < 12:
                            wechsel_beispiele.append((t, sp, st + 1, vor, nach, naehe[sp][-1][1]))
                wait_alt[sp] = (stand.copy(), warte.copy())
    print("Rahmen", dict(rahmen), flush=True)
    print("P370 je Spieler (Takt, Wert):")
    for sp in range(1, 9):
        if any(w for _, w in zahl[sp]) or any(w for _, w in assassinen[sp]):
            print("  Spieler", sp, "Assassinen gezaehlt", zahl[sp][:8], "...", zahl[sp][-3:], "totalAssassinTroops", assassinen[sp][:8], "...", assassinen[sp][-3:], "totalAttackTroops Wechsel", len(angriff[sp]), angriff[sp][:6], "...", angriff[sp][-3:])
    print("   Spieler ohne Assassinen:", [sp for sp in range(1, 9) if not any(w for _, w in zahl[sp])])
    print("P308 Nachladen (Takt, Platz, Art, Spieler, Munition vorher, nachher, Stein vorher, nachher):", len(auf_mun))
    for z in auf_mun[:20]:
        print("   ", z)
    print("    Spruenge:", collections.Counter(z[5] - z[4] for z in auf_mun).most_common(6), "Stein-Abzug:", collections.Counter((z[6] - z[7]) if z[6] is not None else None for z in auf_mun).most_common(6))
    print("P320 Wechsel (vorher, nachher): haeufigste", kuehl.most_common(14))
    print("   Beispiele (Feld, Folge Takt und Wert):", list(kuehl_beispiele.items())[:6])
    print("P350 Steinbruch: Spruenge von idleTimerUnk (Takt, Platz, vorher, nachher):", bruch_sprung[:20], "Anzahl", len(bruch_sprung), "Steinmetz weg (Takt, Platz):", mason_tod[:20], "Anzahl", len(mason_tod))
    print("P358 Moench je (Zustand, Art des Arbeitsplatzes), Rahmen:", moench_zustand.most_common(10), "Folge bei 0x69 (Takt, Platz, Ziel):", moench_folge[:20])
    print("P370 Assassinen je aiUnitBehaviourType, Rahmen:", auftrag.most_common(6))
    print("P319 Wiederaufbau an alter Stelle (Lord in Gefahr, Art): Anzahl", sorted(wiederaufbau.items(), key=lambda z: -z[1])[:24], "Beispiele in Gefahr (Takt, Spieler, (Art, x, y), (Takt der Naehe, Naehe)):", wiederaufbau_nah)
    print("P319 Naehe je Spieler, Rahmen unter 120 nur als Wechsel:")
    for sp in range(1, 9):
        unter = [z for z in naehe[sp] if z[1] < 120]
        print("   Spieler", sp, "Wechsel", len(naehe[sp]), "davon unter 120:", len(unter), unter[:3])
    print("   Stand-Wechsel (Lord in Gefahr, Stand vorher, Stand nachher, wait geaendert):", sorted(wechsel.items(), key=lambda z: -z[1])[:24])
    print("   Beispiele in Gefahr (Takt, Spieler, Schritt, (Stand, wait) vorher, nachher, Naehe):", wechsel_beispiele)


if __name__ == "__main__":
    main()
