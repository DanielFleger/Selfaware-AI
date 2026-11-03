# -*- coding: utf-8 -*-
"""B-142 Lauf K: Die letzten Einzelpunkte, gerechnet aus den Takt-fuer-Takt-Fenstern (reihen6.pkl) und den Zeitreihen (reihen.pkl, reihen2.pkl).

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_rechnen6.py > data/research/auge_plan/lauf_k_20261102/punkte_rechnung6.txt
"""
import collections
import os
import pickle

HIER = os.path.dirname(os.path.abspath(__file__))
d6 = pickle.load(open(os.path.join(HIER, "reihen6.pkl"), "rb"))
d1 = pickle.load(open(os.path.join(HIER, "reihen.pkl"), "rb"))
d2 = pickle.load(open(os.path.join(HIER, "reihen2.pkl"), "rb"))
FENSTER = ("t1", "t6", "t8")
GESAMT = ("Friede t1", "Kampf t6", "Kampf t8")


def reihe(sp, f):
    return d1["t1"]["spieler"].get((sp, f), []) + d1["danach"]["spieler"].get((sp, f), [])


def stand(r, t):
    w = None
    for a, b in r:
        if a > t:
            break
        w = b
    return w


GOLD = {sp: d1["t1"]["gold"].get(sp, []) + d1["danach"]["gold"].get(sp, []) for sp in range(1, 9)}

print("=== Versatz: Bei welchem gelesenen monthTicks wechselt attackedPlayerID oder aiStrengthState?")
for fn in FENSTER:
    R = d6[fn]["R"]
    h = collections.Counter()
    for t in sorted(R):
        if t - 1 in R:
            for sp in range(1, 9):
                if R[t][sp]["aiStrengthState"] != R[t - 1][sp]["aiStrengthState"]:
                    h[("Staerke", R[t]["monthTicks"] - sp)] += 1
                if R[t][sp]["attackedPlayerID"] != R[t - 1][sp]["attackedPlayerID"]:
                    h[("Ziel", R[t]["monthTicks"] - sp)] += 1
    print(fn, h.most_common(6))

print("\n=== P258 Gold im Takt des neuen Soldaten: (Typ, Aenderung) und Ingenieure einzeln")
hist = collections.Counter()
ing = []
for fn in FENSTER:
    R = d6[fn]["R"]
    for t, i, ty, o in d6[fn]["neu"]:
        if t - 1 in R and 1 <= o <= 8:
            dg = R[t][o]["gold"] - R[t - 1][o]["gold"]
            hist[(ty, dg)] += 1
            if ty == 30:
                ing.append((fn, t, o, dg, R[t - 1][o]["gold"], R[t]["dayTicks"]))
print("Ingenieure", len(ing), ing[:30])
je = collections.defaultdict(collections.Counter)
for (ty, dg), c in hist.items():
    je[ty][dg] += c
for ty in sorted(je):
    print(" Typ", ty, je[ty].most_common(6))

print("\n=== P242 Flaggen: Besitzer und Art im ersten Takt, Wechsel gegen die Regel")
for fn in FENSTER:
    print(fn, "Start", d6[fn]["flaggen_start"], "Wechsel", len(d6[fn]["flagge"]))
    R = d6[fn]["R"]

    def soll(t, o):
        z = R[t][o]
        if z["aiBuildingDestroyChoiceTracker"] != 0 or z["aiNervousActionsTracker"] != 0:
            return 3
        return {0: 0, 1: 1}.get(z["aiRecruitUnitChoiceState"], 2)

    treffer = collections.Counter()
    verz = []
    wechsel_soll = {}
    for t in sorted(R):
        if t - 1 in R:
            for o in range(1, 9):
                if soll(t, o) != soll(t - 1, o):
                    wechsel_soll[o] = t
    for t, i, ty, o, alt, neu in d6[fn]["flagge"]:
        if not 1 <= o <= 8:
            treffer["Besitzer 0"] += 1
            continue
        ok = neu == soll(t, o) or (t - 1 in R and neu == soll(t - 1, o))
        treffer[ok] += 1
        if not ok and treffer[False] <= 5:
            print("   weicht ab", t, i, ty, o, alt, neu, "soll", soll(t, o))
    print("   Wechsel passt zur Regel", dict(treffer))
    # Verzoegerung: je Soll-Wechsel bis zum ersten passenden Flaggenwechsel dieses Besitzers
    for o in range(1, 9):
        seq = [(t, soll(t, o)) for t in sorted(R) if t - 1 in R and soll(t, o) != soll(t - 1, o)]
        for t, s in seq[:6]:
            spaeter = [(x[0] - t) for x in d6[fn]["flagge"] if x[3] == o and x[5] == s and x[0] >= t]
            verz.append((o, t, s, min(spaeter) if spaeter else None))
    print("   Soll-Wechsel und Takte bis zur Flagge", verz[:24])

print("\n=== P245 Feindliste beim Neuaufbau: Unterschied Soll minus Index")
for fn in FENSTER:
    h = collections.Counter()
    falsch_typ = falsch_team = 0
    ohne_filter = collections.Counter()
    for t, sp, n, soll, alle, ft, ftm in d6[fn]["feind"]:
        h[soll - n] += 1
        ohne_filter[alle - soll] += 1
        falsch_typ += ft
        falsch_team += ftm
    print(fn, "Aufbauten", len(d6[fn]["feind"]), "Soll-Index", h.most_common(5), "Eintraege mit ausgeschlossener Art", falsch_typ, "eigenes Team", falsch_team, "ausgeschlossen je Aufbau", ohne_filter.most_common(3))

print("\n=== P257 Bedarf: Die Flaggen sind nur alle 250 Takte gelesen. Passen sie zur Rechnung fuer den letzten Spieler, der sie gesetzt haben kann (Wahl Angriff, zuletzt am Zug)?")
FELD = ["AttMaxEngineers", "AttDiggingUnitMax", "AttMaxAssassins", "AttUnit2Max", "AttMaxLaddermen", "AttMaxTunnelers", "AttUnitPatrolMax", "AttUnitBackupMax", "AttUnitEngageMax", "AttUnitSiegeDefMax", "AttMaxDefault"]
IST = ["totalAttackingEngineerTroops", "totalDiggingUnitTroops", "totalAssassinTroops", "totalUnit2Troops", "totalLaddermenTroops", "totalTunnelerTroops", "totalUnitPatrolTroops", "totalUnitBackupTroops", "totalUnitEngageTroops", "totalUnitSiegeDefTroops", "totalMaxDefaultTroops"]


def bedarf(R, t, sp, aic):
    z = R[t][sp]
    ki = z["aiType"] - 1
    aus = []
    for i, (f, g) in enumerate(zip(FELD, IST)):
        m = aic[f][ki]
        w = z[g]
        if i == 0:
            aus.append(int(m != 0 and w < min(m, z["currentAttackWave"] * 4)))
        elif i == 1:
            ziel = z["attackedPlayerID"]
            aus.append(int(m != 0 and w < m and 1 <= ziel <= 8 and R[t][ziel]["moatsOwned"] > 5))
        else:
            aus.append(int(m != 0 and w < m))
    return tuple(aus)


for fn in FENSTER:
    R = d6[fn]["R"]
    aic = d6[fn]["aic"]
    ja = nein = 0
    bsp = []
    ts = sorted(R)
    for t in ts:
        if R[t]["req_frisch"] and t - 60 in R:
            # Zuletzt am Zug: der Spieler mit Wahl Angriff, dessen dayTicks == Spieler zuletzt erreicht wurde; gerechnet wird mit dem Stand kurz davor
            zug = {}
            for x in range(t - 60, t + 1):
                d = R[x]["dayTicks"]
                if 1 <= d <= 8 and R[x][d]["aiRecruitUnitChoiceState"] == 2 and d in R[x]["lords"]:
                    zug[d] = x
            if not zug:
                continue
            letzter = max(zug, key=lambda s: zug[s])
            werte = {bedarf(R, y, letzter, aic) for y in (zug[letzter] - 1, zug[letzter]) if y in R}
            if R[t]["req"] in werte:
                ja += 1
            else:
                nein += 1
            bsp.append((t, "Spieler", letzter, "Takt", zug[letzter], R[t]["req"] in werte, R[t]["req"], sorted(werte)[:2]))
    print(fn, "passt", ja, "passt nicht", nein, bsp[:9])

print("\n=== P276 Staerke: Formel gegen Wert im Monatstakt")


def staerke(z):
    g, v, n = z["gold"], z["currentPopulation"], z["totalFood"]
    tr = z["totalAttackTroops"] + z["totalRaidingTroopsUnk"] + z["totalDefensiveTroopsUnk"]
    w = 0 if g < 200 else (1 if g < 2000 else 2)
    w += 0 if v <= 14 else (1 if v < 40 else 2)
    w += 0 if n <= 19 else (1 if n < 200 else 2)
    w += 0 if tr <= 7 else (2 if tr < 40 else 4)
    return w


for fn in FENSTER:
    R = d6[fn]["R"]
    ok = schlecht = fok = fsch = 0
    bsp = []
    for t in sorted(R):
        for sp in range(1, 9):
            if R[t]["monthTicks"] == sp and t + 1 in R and sp in R[t]["lords"] and t - 1 in R:
                z = R[t][sp]
                w = (staerke(z), staerke(R[t - 1][sp]))
                ist = z["aiStrengthState"]
                if ist in w:
                    ok += 1
                else:
                    schlecht += 1
                    bsp.append((t, sp, ist, w, z["gold"], z["currentPopulation"], z["totalFood"], z["totalAttackTroops"], z["totalRaidingTroopsUnk"], z["totalDefensiveTroopsUnk"]))
                soll = 1 if ist < 3 else (0 if ist < 8 else 2)
                if z["aiNervousActionsTracker"] > 0 or z["aiBuildingDestroyChoiceTracker"] > 0 or (z["aivCurrentPauseIndex"] == 1 and z["pause1"] > 0):
                    soll = 1
                if z["aiStrengthFeeling"] == soll:
                    fok += 1
                else:
                    fsch += 1
                    bsp.append(("Gefuehl", t, sp, ist, z["aiStrengthFeeling"], z["aiNervousActionsTracker"], z["aiBuildingDestroyChoiceTracker"], z["aivCurrentPauseIndex"], z["pause1"]))
    print(fn, "Staerke passt", ok, "nicht", schlecht, "Gefuehl passt", fok, "nicht", fsch, bsp[:6])

print("\n=== P277 Nervositaet: Formel gegen isNotNervousByEnemyTroopValue im Monatstakt")


def rand(e):
    if e < 50:
        return -20
    if e < 100:
        return 0
    if e < 200:
        return 20
    if e < 400:
        return 100
    if e < 600:
        return 200
    return 500 if e >= 800 else 300


for fn in FENSTER:
    R = d6[fn]["R"]
    ok = schlecht = 0
    bsp = []
    for t in sorted(R):
        for sp in range(1, 9):
            if R[t]["monthTicks"] == sp and t - 1 in R and sp in R[t]["lords"]:
                z = R[t][sp]
                soll = 0 if rand(z["totalEnemyTroopValue"]) + z["totalEnemyTroopValue"] < z["nah"] else 1
                if soll == z["isNotNervousByEnemyTroopValue"]:
                    ok += 1
                else:
                    schlecht += 1
                    bsp.append((t, sp, z["totalEnemyTroopValue"], z["nah"], z["isNotNervousByEnemyTroopValue"]))
    print(fn, "passt", ok, "nicht", schlecht, bsp[:5], "Beispiele", [(sp, R[max(R)][sp]["totalEnemyTroopValue"], R[max(R)][sp]["nah"], R[max(R)][sp]["isNotNervousByEnemyTroopValue"]) for sp in range(1, 9)])

print("\n=== P278 Ziel: Rechnung mit dem UCP-Stueck gegen attackedPlayerID im Monatstakt, je TargetChoice")


def ziel_rechnen(R, t, sp, tc, ucp=True):
    z = R[t][sp]
    x0, y0 = z["campground.xEntry"], z["campground.yEntry"]
    bester = 0
    punkte = 10**6
    gold = 0
    nah = 10000
    for i in range(1, 9):
        if i == sp or i not in R[t]["lords"]:
            continue
        if ucp and z["aiPlayerState"] >= 3 and z["attackedPlayerID"] == i:
            return i
        y = R[t][i]
        d = max(abs(y["campground.xEntry"] - x0), abs(y["campground.yEntry"] - y0))
        if tc == 2 and d <= nah:
            nah, bester = d, i
        elif tc == 0 and gold <= y["gold"]:
            gold, bester = y["gold"], i
        elif tc == 1:
            w = y["roh71d"] * 5 + y["rohcf7"] + int(y["gold"] / 100) + d * 2
            if w <= punkte:
                punkte, bester = w, i
    return bester


for fn in FENSTER:
    R = d6[fn]["R"]
    aic = d6[fn]["aic"]
    h = collections.Counter()
    bsp = []
    for t in sorted(R):
        for sp in range(1, 9):
            if R[t]["monthTicks"] == sp and t - 1 in R and sp in R[t]["lords"]:
                z = R[t][sp]
                tc = aic["TargetChoice"][z["aiType"] - 1]
                ist = z["attackedPlayerID"]
                # gerechnet wird mit dem Stand vor dem Aufruf
                alt = R[t - 1][sp]["attackedPlayerID"]
                za = dict(R[t - 1])
                za["lords"] = R[t]["lords"]
                soll = ziel_rechnen({t: za}, t, sp, tc)
                soll_ohne = ziel_rechnen({t: za}, t, sp, tc, ucp=False)
                h[(tc, soll == ist, soll_ohne == ist)] += 1
                if soll != ist:
                    bsp.append((t, sp, "tc", tc, "ist", ist, "soll", soll, "vorher", alt))
    print(fn, "(TargetChoice, mit UCP passt, ohne UCP passt)", sorted(h.items()), bsp[:6])

print("\n=== P289 Zaehler je Angreifer gegen eigene Zaehlung der Mauerfelder")
for fn in FENSTER:
    for sp, r in d6[fn]["zaehler"].items():
        fehler = collections.Counter()
        for t, ziel, z, mauer in r[1:]:
            fehler["scale_10==hack_c"] += z["scale_10"] == z["hack_c"]
            fehler["wide_c==wide_8"] += z["wide_c"] == z["wide_8"]
            if mauer is not None and z["wide_c"] + z["hack_c"] > 0:
                fehler["wide+hack==Mauer"] += z["wide_c"] + z["hack_c"] == mauer
                fehler["verglichen"] += 1
            fehler["Wechsel"] += 1
        print(fn, "Spieler", sp, dict(fehler), "letzte", [(t, zz, x["wide_c"], x["hack_c"], x["scale_10"], x["wide_8"], m) for t, zz, x, m in r[-3:]])

print("\n=== P295, P294 Ziele der Einheiten: (Flagge, Art des Ziels), Listen")


def art(x):
    t, i, ty, o, fl, ti, lg, geb, gty, gow, wo, ls = x
    if geb:
        return f"Gebaeude {gty}" + ("" if gow else " herrenlos")
    if lg & 0x300:
        return "Mauer"
    if lg & 0x40000000:
        return "Graben"
    return "Feld"


alle = collections.Counter()
liste = collections.Counter()
typen = collections.Counter()
for fn in FENSTER:
    for x in d6[fn]["ziel"]:
        alle[(x[4], art(x))] += 1
        liste[(x[4], x[11])] += 1
        typen[(x[4], x[2])] += 1
print("Flagge, Zielart", sorted(alle.items()))
print("Flagge, Liste", sorted(liste.items(), key=lambda a: (a[0][0], -a[1]))[:40])
print("Flagge, Einheitentyp", sorted(typen.items()))

print("\n=== P258 Nachtrag, P260, P261 Ausfall: Typen mit Verhalten 6 und 7 je Spieler, Grenzen, Kaserne")
for w in (6, 7):
    c = collections.Counter()
    for a in (d1["t1"], d1["danach"]):
        for t, i, ty, o, v in a["einh_feld"].get("aiUnitBehaviourType", []):
            if v == w:
                c[(o, ty)] += 1
    print("Verhalten", w, sorted(c.items()))
aic_roh = d2["danach"].get("aic_roh") or d2["t1"].get("aic_roh")
KI = {1: 14, 2: 15, 3: 1, 4: 9, 5: 2, 6: 5, 7: 7, 8: 4}
for sp in range(1, 9):
    ro = aic_roh[KI[sp]]
    t6, u1, t7 = reihe(sp, "totalTroopsType6"), reihe(sp, "unknownCounter_01"), reihe(sp, "totalTroopsType7")
    verletzt6 = verletzt7 = stiege6 = stiege7 = 0
    for (a, va), (b, vb) in zip(t6, t6[1:]):
        if vb > va:
            stiege6 += 1
            if va >= (stand(u1, b) or 0) / 2 + ro["+14c"]:
                verletzt6 += 1
    for (a, va), (b, vb) in zip(t7, t7[1:]):
        if vb > va:
            stiege7 += 1
            if va >= ro["+154"]:
                verletzt7 += 1
    z = d6["t6"]["R"][min(d6["t6"]["R"])].get(sp) or {}
    z1 = d6["t1"]["R"][min(d6["t1"]["R"])][sp]
    print(f"Spieler {sp} KI {KI[sp]} +14c {ro['+14c']} +150 {ro['+150']} +154 {ro['+154']} +158 {ro['+158']} T6 hoechst {max(v for _, v in t6)} Anstiege {stiege6} ueber Grenze {verletzt6} T7 hoechst {max(v for _, v in t7)} Anstiege {stiege7} ueber Grenze {verletzt7} Kaserne {z1['barracks.id']} Soeldner {z1['mercenaryPost.id']} Gilde {z1['engineersGuild.id']} Kathedrale {sum(1 for (i, f), r in d1['danach']['geb'].items() if f == 'buildingType' and r and r[-1][1] == 38)}")

print("\n=== P265 Raubzug-Parameter bei jedem Wellenstart gegen Gold")
for sp in range(1, 9):
    w = reihe(sp, "currentAttackWave")
    par = reihe(sp, "currentAttackRaidParameter")
    ziel = reihe(sp, "attackedPlayerID")
    zeile = []
    for t, v in w[1:]:
        if v > 1 and t > 17040:
            zi = stand(ziel, t)
            zeile.append((t, "Wert", stand(par, t), "Gold", stand(GOLD[sp], t), "Ziel", zi, "Zielgold", stand(GOLD[zi], t) if zi else None))
    print(sp, zeile[:9])
print("Grundwerte RaidUnitsBase, RaidUnitsRandom je Spieler", {sp: (d6["t1"]["aic"]["RaidUnitsBase"][KI[sp]], d6["t1"]["aic"]["RaidUnitsRandom"][KI[sp]]) for sp in KI})

print("\n=== P269 Rammen und P267 Graben: Flagge gegen gate2, moat2 im selben Rahmen")
pi = {}
for a in (d2["t1"], d2["danach"]):
    for kk, r in a["pi"].items():
        pi.setdefault(kk, []).extend(r)
h = collections.Counter()
for a in (d1["t1"], d1["danach"]):
    for t, i, ty, o, v in a["einh_feld"].get("unknownDigMoatOrWallAttackFlag1015", []):
        if v in (1014, 1043, 1044, 1015) and 1 <= o <= 8:
            g = stand(pi[(o - 1, "gate2")], t) or 0
            wi = stand(pi[(o - 1, "wide3")], t) or 0
            m = stand(pi[(o - 1, "moat2")], t) or 0
            h[(v, ty, g != 0, wi != 0, m != 0)] += 1
print("(Flagge, Typ, gate2, wide3, moat2)", sorted(h.items()))

print("\n=== P243 Belagerungsbauten: Bau, Besitzer, Wellen und Folge logicalState gegen den Zustand des Besitzers")
SIEGE = {29: "Zelt", 50: "Tunnel", 54: "Feuerballiste", 69: "Turm gesetzt", 80: "Katapult", 81: "Trebuchet", 82: "Ramme", 83: "Belagerungsturm", 84: "Schild", 86: "Mangonel", 87: "Ballista"}
ty_, ow_, ls_ = {}, {}, collections.defaultdict(list)
for a in (d1["t1"], d1["danach"]):
    for (i, f), r in a["geb"].items():
        if f == "buildingType":
            ty_.setdefault(i, []).extend(r)
        elif f == "owner":
            ow_.setdefault(i, []).extend(r)
        elif f == "logicalState":
            ls_[i].extend(r)
zaehl = collections.Counter()
drei = []
for i, r in ls_.items():
    for (t, w) in r:
        ty = stand(ty_.get(i, []), t) or 0
        if ty in SIEGE:
            zaehl[(ty, w)] += 1
            if w == 3:
                o = stand(ow_.get(i, []), t)
                drei.append((t, i, SIEGE[ty], o, stand(reihe(o, "aiPlayerState"), t) if o and 1 <= o <= 8 else None))
print("(Art, logicalState)", sorted(zaehl.items()))
print("Beobachtet auf BLS_REMOVE:", len(drei), sorted(drei)[:30])
print("Wellenenden (Zustand 9) je Spieler", {sp: [t for t, v in reihe(sp, "aiPlayerState") if v == 9][:10] for sp in range(1, 5)})

print("\n=== P246 noRubble")
tab = None
for (i, f), r in d1["danach"]["geb"].items():
    pass
nr = collections.Counter()
for (i, f), r in d1["danach"]["geb"].items():
    if f == "noRubble":
        for t, w in r:
            nr[(stand(ty_.get(i, []), t) or 0, w)] += 1
print("(Art, noRubble) Wechsel", sorted(nr.items())[:80])
print("Art ohne je gesetzt", sorted({stand(r, 10**9) for (i, f), r in ((k, v) for k, v in d1['danach']['geb'].items() if k[1] == 'buildingType')} - {a for (a, w) in nr if w == 1})[:80])
