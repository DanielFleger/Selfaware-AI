# -*- coding: utf-8 -*-
"""B-142 Lauf K: Die allerletzten Rechnungen: P295, P289, P258, P268, P246, P257, P259, P272, P278, P242, P250.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_rechnen8.py > data/research/auge_plan/lauf_k_20261102/punkte_rechnung8.txt
"""
import collections
import os
import pickle

HIER = os.path.dirname(os.path.abspath(__file__))
d8 = pickle.load(open(os.path.join(HIER, "reihen8.pkl"), "rb"))
d7 = pickle.load(open(os.path.join(HIER, "reihen7.pkl"), "rb"))
d6 = pickle.load(open(os.path.join(HIER, "reihen6.pkl"), "rb"))
d1 = pickle.load(open(os.path.join(HIER, "reihen.pkl"), "rb"))
KI = {1: 14, 2: 15, 3: 1, 4: 9, 5: 2, 6: 5, 7: 7, 8: 4}


def reihe(sp, f):
    return d1["t1"]["spieler"].get((sp, f), []) + d1["danach"]["spieler"].get((sp, f), [])


def stand(r, t):
    w = None
    for a, b in r:
        if a > t:
            break
        w = b
    return w


print("=== P295 Ziele der Einheiten: (Flagge, Art des Ziels)")


def art(x):
    t, i, ty, o, fl, ti, lg, geb, gty, gow, wo, ls, alter = x
    if geb:
        return f"Gebaeude {gty}"
    if lg & 0x300:
        return "Mauer"
    if lg & 0x40000000:
        return "Graben"
    return "Feld"


alle = collections.Counter()
liste = collections.Counter()
typen = collections.Counter()
for x in d8["ziel"]:
    alle[(x[4], art(x))] += 1
    liste[(x[4], x[11])] += 1
    typen[(x[4], x[2])] += 1
print("Ereignisse", len(d8["ziel"]), "Alter der Karte hoechstens", max(x[12] for x in d8["ziel"]))
print("Flagge, Zielart", sorted(alle.items()))
print("Flagge, Liste", sorted(liste.items(), key=lambda a: (a[0][0], -a[1]))[:30])
print("Flagge, Einheitentyp", sorted(typen.items()))
wand = [x for x in d8["ziel"] if x[4] == 1010]
print("Flagge 1010: Anteile Mauer und Gebaeude", collections.Counter("Mauer" if art(x) == "Mauer" else ("Tor/Turm" if x[8] in (45, 46, 47, 48, 60, 61, 74, 75, 76, 77, 78) else ("Gebaeude" if x[7] else "Feld")) for x in wand))
print("Flagge 1010: Zielart gegen Liste", collections.Counter((art(x), x[11][:1] if x[11] else ()) for x in wand).most_common(24))
print("Flagge 1010: nach Liste, wie im UCP-Stueck 4 Mauer, 2 Tor oder Turm, 1 Gebaeude?", collections.Counter((x[11][0].rstrip("2") if x[11] else "keine") for x in wand).most_common())
print("Flagge 1014: Listen", collections.Counter(x[11] for x in d8["ziel"] if x[4] == 1014).most_common(), "1019", collections.Counter(x[11] for x in d8["ziel"] if x[4] == 1019).most_common(4))

print("\n=== P289 Zaehler gegen die eigene Zaehlung der Mauerfelder im ganzen Kampf")
sum_v = collections.Counter()
bsp = []
for sp, r in d8["zaehler"].items():
    for t, ziel, z, mauer, alter in r[1:]:
        if z["wide_c"] + z["hack_c"] == 0:
            continue
        sum_v["Berechnungen"] += 1
        sum_v["scale_10 == hack_c"] += z["scale_10"] == z["hack_c"]
        sum_v["wide_c == wide_8"] += z["wide_c"] == z["wide_8"]
        if mauer is not None:
            sum_v["mit Zaehlung"] += 1
            sum_v["wide+hack == Mauer"] += z["wide_c"] + z["hack_c"] == mauer
            d = abs(z["wide_c"] + z["hack_c"] - mauer)
            sum_v["Unterschied bis 3"] += d <= 3
            if d > 3 and len(bsp) < 8:
                bsp.append((t, sp, ziel, z["wide_c"], z["hack_c"], mauer, alter))
print(dict(sum_v), "groessere Unterschiede", bsp)

print("\n=== P258 Gold beim Ende von isEngineerRequired: Aenderung in dieser Runde")
h = collections.Counter()
for t, sp, vor, nach, tag in d8["ing"]:
    h[(nach - vor) if vor is not None else None] += 1
print("Ereignisse", len(d8["ing"]), "Aenderungen", h.most_common(12), "Beispiele", d8["ing"][:6])

print("\n=== P268 Feuer im ganzen Kampf")
print("Runden mit brennendem Gebaeude", d8["feuer_runden"], "je Art hoechstens gleichzeitig", sorted(d8["feuer"].items()))

print("\n=== P246 Tabelle ShowRubble je Art gegen noRubble")
tab = d8["rubble"]
ty_ = {}
for a in (d1["t1"], d1["danach"]):
    for (i, f), r in a["geb"].items():
        if f == "buildingType":
            ty_.setdefault(i, []).extend(r)
gesetzt = collections.Counter()
weg = collections.Counter()
for (i, f), r in d1["danach"]["geb"].items():
    if f == "noRubble":
        for t, w in r:
            if w == 1:
                gesetzt[stand(ty_.get(i, []), t) or 0] += 1
    if f == "logicalState":
        for t, w in r:
            if w == 3:
                weg[stand(ty_.get(i, []), t) or 0] += 1
print("Tabelle", {i: v for i, v in enumerate(tab) if v == 0})
print("noRubble 1 je Art, Tabelle", sorted((a, c, tab[a]) for a, c in gesetzt.items()))
print("noRubble 1 bei Tabelle 0", [(a, c) for a, c in gesetzt.items() if tab[a] == 0])
print("zerstoert gesehen und Tabelle 0, noRubble nie 1", sorted((a, c) for a, c in weg.items() if tab[a] == 0 and not gesetzt[a]))

print("\n=== P257 Bedarf: Flaggen gegen die Rechnung irgendeines Spielers mit Wahl Angriff, im letzten Tagesumlauf")
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


for fn in ("t1", "t6", "t8"):
    R = d6[fn]["R"]
    aic = d6[fn]["aic"]
    gut = schlecht = 0
    wer = collections.Counter()
    falsch = []
    for t in sorted(R):
        if not R[t]["req_frisch"]:
            continue
        treffer = set()
        for x in range(t - 250, t + 1):
            if x not in R:
                continue
            d = R[x]["dayTicks"]
            if 1 <= d <= 8 and R[x][d]["aiRecruitUnitChoiceState"] == 2 and bedarf(R, x, d, aic) == R[t]["req"]:
                treffer.add(d)
        if treffer or x - 250 < min(R):
            gut += bool(treffer)
            schlecht += not treffer
            wer[tuple(sorted(treffer))] += 1
            if not treffer:
                falsch.append((t, R[t]["req"]))
    print(fn, "passt", gut, "nicht", schlecht, wer.most_common(5), falsch[:3])

print("\n=== P259 Ziel der Belaestigungs-Geraete gegen attackedPlayerID")
h = collections.Counter()
for a in (d1["t1"], d1["danach"]):
    for t, i, ty, o, v in a["einh_feld"].get("siegeTargetPlayerID", []):
        if ty in (39, 40, 41, 61, 77) and 1 <= o <= 8 and v:
            h[(ty, o, v == stand(reihe(o, "attackedPlayerID"), t))] += 1
print("(Typ, Besitzer, Ziel == attackedPlayerID)", sorted(h.items()))

print("\n=== P272 Spieler 3 ueber der Wunschzahl")
print([x for x in d7["raub"][3] if x[1] > x[2] + d6["t1"]["aic"]["RaidUnitsBase"][KI[3]]])

print("\n=== P278 Tod des Lords gegen die Zielwechsel")
for sp in (2, 4, 7, 8):
    print("Spieler", sp, "lordKilledByPlayerID", reihe(sp, "lordKilledByPlayerID")[:4], "lordID", reihe(sp, "lordID")[:4])
for sp, t in ((1, 132003), (2, 88004), (3, 43221), (3, 76004), (4, 24004)):
    print("Spieler", sp, "Takt", t, "Zustaende davor", [x for x in reihe(sp, "aiPlayerState") if t - 900 < x[0] <= t + 10])

print("\n=== P242 Flaggenwerte, die vorkamen")
print("strenge Fenster", collections.Counter(x[5] for fn in ("t1", "t6", "t8") for x in d6[fn]["flagge"]))
print("ganzer Kampf", collections.Counter(x[5] for x in d8["flagge"]))
h = collections.Counter()
bsp = []
for t, i, ty, o, alt, neu in d8["flagge"]:
    if not 1 <= o <= 8:
        continue
    n = stand(d8["nerv"].get(o, []) and [(a, (b, c)) for a, b, c in d8["nerv"][o]], t) or (0, 0)
    nervoes = n[0] != 0 or n[1] != 0
    h[(neu == 3, nervoes)] += 1
    if neu == 3 and not nervoes and len(bsp) < 6:
        bsp.append((t, i, ty, o, alt, neu, n))
print("(neuer Wert 3, Merker gesetzt)", sorted(h.items()), bsp)

print("\n=== P258 Gold beim neuen Ingenieur im ganzen Kampf: Aenderung im Fenster um den Takt, nur am Zug des Besitzers (Tagestakt == Spieler)")
GOLD = {sp: d1["t1"]["gold"].get(sp, []) + d1["danach"]["gold"].get(sp, []) for sp in range(1, 9)}
d2 = pickle.load(open(os.path.join(HIER, "reihen2.pkl"), "rb"))
am_zug = collections.Counter()
sonst = collections.Counter()
for t, i, ty, o in d2["danach"]["neu"]:
    if ty == 30 and 1 <= o <= 8:
        v, n = stand(GOLD[o], t - 8), stand(GOLD[o], t + 1)
        (am_zug if (t % 50 - o) % 50 <= 8 else sonst)[(n - v) if v is not None and n is not None else None] += 1
print("am Zug", sum(am_zug.values()), am_zug.most_common(14))
print("sonst", sum(sonst.values()), sonst.most_common(6))

print("\n=== P259 Ziel der Geraete: Faelle mit anderem Ziel gegen das Ziel kurz davor und danach")
for a in (d1["t1"], d1["danach"]):
    for t, i, ty, o, v in a["einh_feld"].get("siegeTargetPlayerID", []):
        if ty in (39, 77) and 1 <= o <= 8 and v and v != stand(reihe(o, "attackedPlayerID"), t):
            print(" ", t, "Platz", i, "Typ", ty, "Besitzer", o, "Ziel", v, "Angriff auf", stand(reihe(o, "attackedPlayerID"), t), "davor", stand(reihe(o, "attackedPlayerID"), t - 800), "danach", stand(reihe(o, "attackedPlayerID"), t + 800))

print("\n=== P250 Abstand zur Auswahl-Einheit und freie Nachbarn")
ab = []
fr = collections.Counter()
for t, i, art_, o, bx, by, welle, sel, orte, nah, frei in d7["siege"]:
    fr[frei[:1] if frei else None] += 1
    for q in orte:
        if q:
            ab.append((max(abs(q[0] - bx - 1), abs(q[1] - by - 1)), art_, welle))
print("Abstaende (Luftlinie ist die untere Grenze der Wegschritte)", sorted(ab)[:12], "hoechster", max(ab), "Anzahl", len(ab), "freie Nachbarn", fr)
print("Hoehenunterschied", collections.Counter(x[10][1] for x in d7["siege"] if x[10]))
