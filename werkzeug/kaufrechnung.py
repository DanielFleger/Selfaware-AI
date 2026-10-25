# -*- coding: utf-8 -*-
"""B-241 Kaufrechnung aus den Spielwerten (Daniel 25.10.2026 08:27 "die Liste von Preisen und die Rechnung steht im Spielcode -
egal welche Modifikation, Balance, Namen oder Anzahl"; 09:37 "ja bau die Kaufrechnung aus den Spielwerten").

Nichts hier ist eine Liste von uns: Preise, Leben, Schaden, Schlag- und Schusstakt und Namen kommen aus daten/spielwerte_<stempel>.json
(SRE, B-242, spielwerte.py liest sie einmal je Partie aus dem laufenden Spiel):
  - Nahkampf: melee_damage[Angreifer][Ziel] ist Schaden je TAKT (processMeleeInitiation schlaegt bei anliegendem Gegner jeden Takt,
    SRE 25.10. 09:53; takt.nahkampf_je_treffer = 1) - Daniels 70/Takt Streitkolben am Lord = Tabelle 70
  - Fernkampf: arrow_damage[Ziel] je Geschoss / takt.schuss_zyklus[Schuetze] (Animationstabellen: Bogen 129, Armbrust 228,
    arab. Bogen 90, Schleuderer 57, Feuerwerfer 143; Katapult 84, Tribok 183, Mangonel 90, Balliste 78, Feuerballiste 66)
Die Duell-Messungen (gefecht.tabelle) dienen nur noch der Gegenprobe (kalibrierung: gemessen / Spielwert je Art; Nahkampf 0,8-1,5
= Pausen und Gedraenge, Bogen 0,009 gegen 0,0078 passt, Armbrust gemessen 0,02 gegen 0,0044 passt NICHT - offen, nachmessen).
So liefert gefecht.simuliere fuer JEDE Art der Tabelle (auch unbekannte eines Mods) einen Wert aus dem Spiel selbst.

Preis einer Einheit = Gold (truppe.kaserne_gold / truppe.soeldner_gold) + Marktpreis je Stueck der Waffe/Ruestung
(einheit.euro_resource_costs, markt.kaufpreis_je5 / 5); Ritter brauchen zusaetzlich ein Pferd aus dem Stall (-1 in der Tabelle).

bewerte(gold, feinde): je kaufbarer Art so viele, wie Gold (und Bauern am Feuer) hergeben, gegen die Feindaufstellung gerechnet;
Wert = zugefuegter Feindverlust je Gold, Sieg zaehlt den eigenen Rest dazu. Rang: Sieg zuerst, dann Wert je Gold.
Aufruf: python werkzeug/kaufrechnung.py <gold> [feinde wie 22x10,26x5] [feuer]"""
import glob
import json
import os
import statistics
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
D = os.path.join(HIER, "..", "daten")

KASERNE, SOELDNER, STALL = 9, 8, 35                 # BT: BARRACKS, MERCENARYPOST, STABLES (aufzaehlungen.BT der Spielwerte)
KASERNE_ARTEN = (22, 23, 24, 25, 26, 27, 28)        # Reihenfolge truppe.kaserne_gold / einheit.euro_resource_costs (UT)
SOELDNER_ARTEN = (70, 71, 72, 73, 74, 75, 76)       # Reihenfolge truppe.soeldner_gold (nonEuroRecruit)
ABSTAND = 12                                        # Felder zwischen beiden Seiten in der Rechnung (Schuetzen schiessen erst)
# SRE 25.10. 09:59 (processEntityDamageToUnit 0x00531920): Geschossschaden je Schuetzenart aus verschiedenen Tabellen -
# Bogen/arab. Bogen/Pferdebogen arrow_damage, Armbrust bolt_damage, Schleuderer stone_damage; der Feuerwerfer wirkt ueber
# Feuer-Entities (Tabelle gibt 0) - fuer ihn bleibt die Duellmessung (gefecht.tabelle, FERN)
GESCHOSS_TABELLE = {22: "einheit.arrow_damage", 70: "einheit.arrow_damage", 74: "einheit.arrow_damage",
                    23: "einheit.bolt_damage", 72: "einheit.stone_damage"}
MIN_PAARE = 3                                       # so viele gemessene Paare braucht ein Faktor je Art


def spielwerte_laden(pfad=None):
    """Juengste daten/spielwerte_*.json mit quelle live (oder pfad). None, wenn keine da ist."""
    if pfad is None:
        for p in sorted(glob.glob(os.path.join(D, "spielwerte_*.json")), key=os.path.getmtime, reverse=True):
            try:
                d = json.load(open(p, encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if d.get("quelle") == "live":
                d["_pfad"] = p
                return d
        return None
    d = json.load(open(pfad, encoding="utf-8"))
    d["_pfad"] = pfad
    return d


def _w(sw, name):
    return sw["tabellen"][name]["werte"]


def name(sw, typ):
    n = (sw.get("namen") or {}).get("einheit") or {}
    return n.get(str(typ)) or (sw.get("aufzaehlungen") or {}).get("UT", {}).get(str(typ)) or str(typ)


def preise(sw):
    """{typ: {"gold": Gesamtpreis je Einheit, "basis": Gold beim Anwerben, "waren": [(RT, Preis je Stueck)], "gebaeude": BT,
    "stall": bool}} - nur Arten mit Preis > 0."""
    kauf5 = _w(sw, "markt.kaufpreis_je5")
    aus = {}
    for i, typ in enumerate(KASERNE_ARTEN):
        gold = _w(sw, "truppe.kaserne_gold")[i]
        waren, stall = [], False
        for rt in _w(sw, "einheit.euro_resource_costs")[i]:
            if rt == -1:
                stall = True
            elif rt > 0:
                waren.append((rt, kauf5[rt] / 5.0))
        aus[typ] = {"gold": gold + sum(p for _, p in waren), "basis": gold, "waren": waren, "gebaeude": KASERNE, "stall": stall}
    for i, typ in enumerate(SOELDNER_ARTEN):
        gold = _w(sw, "truppe.soeldner_gold")[i]
        if gold > 0:
            aus[typ] = {"gold": gold, "basis": gold, "waren": [], "gebaeude": SOELDNER, "stall": False}
    return aus


def schuss_zyklus(sw, typ):
    """Takte zwischen zwei Geschossen aus takt.schuss_zyklus (0 = kein Schuetze / nicht gelesen); None ohne Tabelle."""
    t = sw["tabellen"].get("takt.schuss_zyklus")
    if t is None or typ >= len(t["werte"]):
        return None
    return t["werte"][typ] or None


def kalibrierung(sw, duelle=None):
    """Gegenprobe Duell-Messung gegen Spielwert: (nah {Angreifer: gemessen je Takt / melee_damage}, fern {Schuetze: gemessene
    Rate / Spielrate}, gemessen {Art}). Geht NICHT in die Rechnung ein - sie zeigt, wo Messung und Spiel auseinanderliegen."""
    import gefecht
    S, _, F = duelle if duelle is not None else gefecht.tabelle()
    md, ad = _w(sw, "einheit.melee_damage"), _w(sw, "einheit.arrow_damage")
    n = len(md)
    nah, fern, gemessen = {}, {}, set()
    for a, zeile in S.items():
        if a >= n:
            continue
        q = [v / md[a][z] for z, v in zeile.items() if z < n and md[a][z] > 0]
        if len(q) >= MIN_PAARE:
            nah[a] = statistics.median(q)
            gemessen.add(a)
    for a, zeile in (F or {}).items():
        zyk = schuss_zyklus(sw, a)
        gd = _w(sw, GESCHOSS_TABELLE[a]) if a in GESCHOSS_TABELLE else ad
        q = [v / gd[z] for z, v in zeile.items() if z < n and gd[z] > 0]
        if len(q) >= MIN_PAARE:
            fern[a] = statistics.median(q) * zyk if zyk else statistics.median(q)
            gemessen.add(a)
    return nah, fern, gemessen


def schadenstabelle(sw, duelle=None):
    """(SCHADEN {x: {y: je Takt}}, FERN {x: {y: je Takt}}, LEBEN {x}, kalib) fuer gefecht.simuliere - alles aus den Spielwerten:
    Nahkampf = melee_damage / takt.nahkampf_je_treffer (1), Fernkampf = arrow_damage[Ziel] / takt.schuss_zyklus[Schuetze].
    Schuetzen ohne gelesenen Zyklus bekommen den Median der gelesenen (kalib["ungelesen"])."""
    import gefecht
    S, LEB, F = duelle if duelle is not None else gefecht.tabelle()
    nah, fern, gemessen = kalibrierung(sw, (S, LEB, F))
    md, ad, hp = _w(sw, "einheit.melee_damage"), _w(sw, "einheit.arrow_damage"), _w(sw, "einheit.base_hp")
    n = len(md)
    treffer = (sw["tabellen"].get("takt.nahkampf_je_treffer") or {}).get("werte") or [1] * n
    zyklen = {a: schuss_zyklus(sw, a) for a in range(n)}
    gelesen = [z for z in zyklen.values() if z]
    zyk_std = statistics.median(gelesen) if gelesen else None
    schaden, fernt, leben, ungelesen = {}, {}, {}, []
    for a in range(n):
        if hp[a] <= 0:
            continue
        leben[a] = hp[a]
        je = max(1, treffer[a] if a < len(treffer) and treffer[a] else 1)
        schaden[a] = {z: md[a][z] / float(je) for z in range(n) if hp[z] > 0 and md[a][z] > 0}
        if a in gefecht.FERN_REICH:
            if a not in GESCHOSS_TABELLE:
                if a in (F or {}):
                    fernt[a] = dict(F[a])                    # Feuerwerfer: Feuer-Entities, nur die Duellmessung kennt den Wert
                continue
            gd = _w(sw, GESCHOSS_TABELLE[a])
            zyk = zyklen.get(a)
            if not zyk:
                ungelesen.append(a)
                zyk = zyk_std
            if zyk:
                fernt[a] = {z: gd[z] / float(zyk) for z in range(n) if hp[z] > 0 and gd[z] > 0}
    kalib = {"nah": nah, "fern": fern, "gemessen": sorted(gemessen), "zyklus_standard": zyk_std, "ungelesen": ungelesen}
    return schaden, fernt, leben, kalib


def feinde_aus(text):
    """'22x10,26x5' -> [dict(typ, n)]"""
    aus = []
    for teil in text.split(","):
        if "x" in teil:
            t, k = teil.split("x")
            aus.append({"typ": int(t), "n": int(k)})
    return aus


def bewerte(sw, gold, feinde, feuer=None, duelle=None, arten=None, bis=None):
    """feinde: [dict(typ, n[, leben])]. Gibt [dict(typ, name, n, gold, preis, sieg, rest, feind_rest, takte, wert, ungemessen)],
    bester zuerst (Sieg vor Wert je Gold). Kauft je Art so viele, wie gold // Preis und feuer (Bauern am Feuer) hergeben."""
    import gefecht
    schaden, fernt, leben, kalib = schadenstabelle(sw, duelle)
    pr = preise(sw)
    sie = []
    for f in feinde:
        for i in range(f["n"]):
            sie.append(dict(typ=f["typ"], leben=f.get("leben", leben.get(f["typ"], 1)), x=ABSTAND + (i % 5), y=i // 5, steht=False))
    sie_voll = sum(e["leben"] for e in sie)
    aus = []
    for typ, p in pr.items():
        if arten is not None and typ not in arten:
            continue
        if p["gold"] <= 0 or typ not in leben:
            continue
        n = int(gold // p["gold"])
        if feuer is not None:
            n = min(n, int(feuer))
        if n <= 0:
            continue
        wir = [dict(typ=typ, leben=leben[typ], x=(i % 5), y=i // 5) for i in range(n)]
        voll = sum(e["leben"] for e in wir)
        rest_w, rest_s, takte, sieg = gefecht.simuliere(wir, sie, schaden, bis=bis or gefecht.BIS, fern=fernt) if sie else (voll, 0.0, 0, True)
        ausgegeben = n * p["gold"]
        wert = ((sie_voll - rest_s) + (rest_w if sieg else 0.0)) / float(max(1, ausgegeben))
        aus.append({"typ": typ, "name": name(sw, typ), "n": n, "gold": ausgegeben, "preis": p["gold"], "gebaeude": p["gebaeude"],
                    "stall": p["stall"], "waren": p["waren"], "sieg": bool(sieg), "rest": rest_w / float(max(1, voll)),
                    "feind_rest": rest_s / float(max(1, sie_voll)) if sie_voll else 0.0, "takte": takte, "wert": wert,
                    "ungelesen": typ in kalib["ungelesen"]})
    aus.sort(key=lambda r: (not r["sieg"], -r["wert"]))
    return aus


def main(argv):
    sw = spielwerte_laden()
    if sw is None:
        print("keine daten/spielwerte_*.json mit quelle live - erst spielwerte.py im laufenden Spiel ausfuehren")
        return 1
    gold = int(argv[0]) if argv else 1000
    feinde = feinde_aus(argv[1]) if len(argv) > 1 else [{"typ": 22, "n": 10}, {"typ": 24, "n": 10}]
    feuer = int(argv[2]) if len(argv) > 2 else None
    _, _, _, kalib = schadenstabelle(sw)
    print("Spielwerte:", os.path.basename(sw["_pfad"]), "| Gegenprobe Duell/Spiel Nahkampf:", {k: round(v, 2) for k, v in kalib["nah"].items()},
          "| Fernkampf:", {k: round(v, 2) for k, v in kalib["fern"].items()}, "| Zyklus ungelesen:", kalib["ungelesen"])
    print("Preise:", {t: round(p["gold"], 1) for t, p in sorted(preise(sw).items())})
    print("Gold %d gegen %s%s:" % (gold, ",".join("%dx%d" % (f["typ"], f["n"]) for f in feinde), " (Feuer %d)" % feuer if feuer else ""))
    for r in bewerte(sw, gold, feinde, feuer):
        print("  %-22s x%3d fuer %5d (je %5.1f%s) | %s nach %4d Takten, Rest %3.0f %%, Feind-Rest %3.0f %% | Wert je Gold %6.1f%s" % (
            r["name"], r["n"], r["gold"], r["preis"], ", Stall" if r["stall"] else "", "SIEG     " if r["sieg"] else "Niederlage",
            r["takte"], 100 * r["rest"], 100 * r["feind_rest"], r["wert"], " ZYKLUS UNGELESEN" if r["ungelesen"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
