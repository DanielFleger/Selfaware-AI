# -*- coding: utf-8 -*-
"""B-120: Woher kam das Gold, wohin ging es - fuer den Lenker UND seinen Gegner. Liest das Lageprotokoll einer Partie
(lage_*_iN_spM.jsonl.gz), die Mitschrift des Lenkers (samurai_*_spM_konsole.txt) und sein Ertragsprotokoll
(ertrag_live_*), schreibt data/research/lernen/gold_<stamp>.txt.

Alles hier ist GEMESSEN (Protokollzeilen gezaehlt), ausser wo GERECHNET davorsteht. Preise, Steuersaetze und Anwerbegold
kommen aus der Balance-Datei, die die Instanz laut ucp-config.yml laedt (rebalancer: balance_config_file_selector) - und
werden gegen die Baukosten geprueft, die der Lenker zu Partiebeginn aus dem Spiel gelesen hat ("Baukosten aus dem Spiel").
Instanz 4 spielt Ascension, nicht Liga (Wissensregister L54).
Aufruf: uv run python -m selfaware.telemetry.gold_bilanz <konsole.txt> <lage.jsonl.gz>"""

from selfaware import workspace as _workspace
import ast
import glob
import gzip
import json
import os
import re
import sys
from collections import Counter

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(_workspace.DATA)
AUS = os.path.join(D, "lernen")
STAMM = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme"
MONAT = 800                                   # Wissensregister B27
WAREN = {2: "holz", 4: "stein", 6: "eisen", 13: "apfel", 10: "brot", 11: "kaese", 12: "fleisch", 9: "weizen", 3: "hopfen"}
LIGA_NAME = {22: "European archer", 23: "European crossbowman", 24: "European spearman", 25: "European pikeman",
             26: "European maceman", 27: "European swordsman", 28: "European knight", 70: "Arabian archer", 71: "Arabian slave",
             72: "Arabian slinger", 73: "Arabian assassin", 74: "Arabian horse archer", 75: "Arabian swordsman",
             76: "Arabian firethrower"}
KURZ = {22: "Bogen", 23: "Armbrust", 24: "Speer", 25: "Pike", 26: "Keule", 27: "Schwert", 28: "Ritter", 70: "arab.Bogen",
        71: "Sklave", 72: "Schleuder", 73: "Assassine", 74: "Pferdebogen", 75: "arab.Schwert", 76: "Feuerwerfer"}
# Einheiten, fuer die die Balance-Datei kein goldCost setzt: Spielwert. Sklave 5 gemessen (30 Abbuchungen zu -5 in Partie
# 20261019_2240 bei 42 RAID-WERBUNG Sklaven), Schleuder 12 = Vanilla-Tabelle, UNGEPRUEFT
OHNE_BALANCE = {71: (5, "gemessen"), 72: (12, "Vanilla, ungeprueft")}
GEB_BALANCE = {32: "Apple farm", 5: "Iron mine", 31: "Hop farm", 20: "Quarry", 33: "Dairy farm", 7: "Hunters hut", 22: "Inn",
               17: "Bakery", 34: "Mill", 30: "Wheat farm", 18: "Brewery", 8: "Mercenary post", 9: "Barracks", 26: "Marketplace"}


def balance_datei(instanz):
    spiel = STAMM if instanz == 1 else "%s Instanz%d" % (STAMM, instanz)
    cfg = open(os.path.join(spiel, "ucp-config.yml"), encoding="utf-8", errors="replace").read()
    m = re.search(r"balance_config_file_selector:\s*\n\s*contents:\s*\n\s*value:\s*(\S+)", cfg)
    if not m:
        return None
    treffer = sorted(glob.glob(os.path.join(spiel, m.group(1).replace("/", os.sep))))
    return treffer[-1] if treffer else None


def main():
    pos = [a for a in sys.argv[1:] if "=" not in a]
    if len(pos) < 2:
        raise SystemExit(__doc__)
    konsole, lage = pos
    stamp = (re.search(r"(\d{8}_\d{6})", os.path.basename(lage)) or re.search(r"(\d{8}_\d{6})", os.path.basename(konsole))).group(1)
    m_sp = re.search(r"_sp(\d)", os.path.basename(lage))
    sp = int(m_sp.group(1)) if m_sp else 1          # eigene Partien ohne _spN: der Lenker ist Spieler 1
    instanz = int(re.search(r"_i(\d+)", os.path.basename(lage)).group(1))
    text = open(konsole, encoding="utf-8", errors="replace").read()
    Z = [json.loads(z) for z in gzip.open(lage, "rt", encoding="utf-8")]
    aus = []

    def p(s=""):
        aus.append(s)
        print(s, flush=True)

    bd = balance_datei(instanz)
    B = json.load(open(bd, encoding="utf-8"))
    p("GOLD-BILANZ Partie %s, Lenker Spieler %d, Instanz %d, %d Lagezeilen bis Tick %d" % (stamp, sp, instanz, len(Z), Z[-1]["t"]))
    m = re.search(r"Baukosten aus dem Spiel (\{.*?\}\})", text)
    if m:
        spiel_k = ast.literal_eval(m.group(1))
        ab = []
        for typ, name in GEB_BALANCE.items():
            if typ in spiel_k and name in B["buildings"] and "cost" in B["buildings"][name]:
                c = dict(zip(("holz", "stein", "eisen", "pech", "gold"), B["buildings"][name]["cost"]))
                c = {k: v for k, v in c.items() if v}
                if c != spiel_k[typ]:
                    ab.append("%s Spiel %s / Datei %s" % (name, spiel_k[typ], c))
        p("Balance %s - %s" % (os.path.basename(bd), "passt zu den Baukosten aus dem Spiel" if not ab else "WEICHT AB: " + "; ".join(ab)))
    steuer_gold = [float(x) for x in B["taxation"]["gold"]]

    # 1. Gold des Lenkers: jede Aenderung zwischen zwei Lagezeilen
    rein, raus = [], []
    for a, b in zip(Z, Z[1:]):
        d = b["st"]["gold"] - a["st"]["gold"]
        if d:
            (rein if d > 0 else raus).append((a["t"], b["t"], d))
    monatlich = [x for x in rein if any(x[0] < k * MONAT + 10 <= x[1] for k in range(x[0] // MONAT, x[1] // MONAT + 2))]
    p()
    p("1. GOLD DES LENKERS (Start %d)" % Z[0]["st"]["gold"])
    p("   Einnahmen %d in %d Schritten, Groessen %s" % (sum(x[2] for x in rein), len(rein), Counter(x[2] for x in rein).most_common(6)))
    p("   davon ueber einen Monatswechsel (Steuer): %d Schritte, %d Gold" % (len(monatlich), sum(x[2] for x in monatlich)))
    p("   Ausgaben %d in %d Schritten, Groessen %s" % (sum(x[2] for x in raus), len(raus), Counter(x[2] for x in raus).most_common(8)))
    wechsel = re.findall(r"STEUER (\d+) -> (\d+)", text)
    p("   Steuer-Aenderungen in der Mitschrift: %d %s; Stufe 0-2 bringen laut Balance %s Gold je Kopf" % (
        len(wechsel), wechsel[:8] if wechsel else "(Stufe blieb beim Startwert)", B["taxation"]["gold"][:3]))
    gold_sp = [r["st"]["gold"] for r in Z]
    p("   Gold-Stand: Anteil der Zeilen mit 0 Gold %.0f %%, hoechstens %d" % (100.0 * gold_sp.count(0) / len(gold_sp), max(gold_sp)))

    # 2. Beliebtheit: Wochenspruenge (Steuer + Rationen + Vielfalt, L34)
    spr = Counter(b["st"]["beliebt"] - a["st"]["beliebt"] for a, b in zip(Z, Z[1:]) if b["st"]["beliebt"] != a["st"]["beliebt"])
    p()
    p("2. BELIEBTHEIT DES LENKERS - Wochenspruenge in Hundertsteln (L34: Steuer + Rationen + Vielfalt): %s" % spr.most_common(8))
    p("   Steuer-Beliebtheit laut Balance je Stufe 0-11: %s; Gold je Kopf und Monat: %s" % (
        B["taxation"]["popularity"], B["taxation"]["gold"]))
    leute = [r["st"]["leute"] for r in Z]
    p("   GERECHNET brutto (dieselben Leute, ohne Beliebtheitsfolgen): Stufe 4 %d, Stufe 6 %d Gold ueber die Partie" % (
        sum(l * steuer_gold[4] for l in leute[::1]) * (Z[-1]["t"] / float(len(Z))) / MONAT,
        sum(l * steuer_gold[6] for l in leute) * (Z[-1]["t"] / float(len(Z))) / MONAT))

    # 3. Erzeugung des Lenkers (ertrag_live) und Lager beider Spieler (Gebaeudevorrat)
    ertrag = os.path.join(os.path.dirname(lage), os.path.basename(lage).replace("lage_", "ertrag_live_").replace(".jsonl.gz", ".jsonl"))
    p()
    if os.path.exists(ertrag):
        zug, verk = Counter(), Counter()
        for z in open(ertrag, encoding="utf-8"):
            r = json.loads(z)
            zug.update(r.get("zug", {}))
            verk.update(r.get("verk", {}))
        p("3. ERZEUGUNG DES LENKERS (ertrag_live zug, ganze Partie): %s; verkauft: %s" % (dict(zug), dict(verk)))
    hf = [(int(m.group(1)), int(m.group(2))) for m in re.finditer(
        r"^STAND Tick (\d+) .*?Holzfaellerhuette \d+ \(Arbeiter (\d+)/", text, re.M)]
    if hf and os.path.exists(ertrag):
        besetzt_ticks = sum((b[0] - a[0]) * a[1] for a, b in zip(hf, hf[1:]))
        p("   Holz je besetzter Holzfaellerhuette und 1.000 Ticks: %.1f (Wissensregister L3: 5,3 bei 55-75 Feldern Weg)" % (
            1000.0 * zug.get("holz", 0) / max(1, besetzt_ticks)))
    p("   LAGER beider Spieler (Lagerplatz + Kornspeicher, Summe Vorrat je Ware):")
    for t in range(4000, Z[-1]["t"], 4000):
        r = min(Z, key=lambda r: abs(r["t"] - t))
        s = Counter()
        for e in r["gebaeude"].split("\n")[1:]:
            w = e.split()
            if len(w) >= 12 and w[2] in ("10", "19") and int(w[8]):
                s[(int(w[1]), WAREN.get(int(w[11]), w[11]))] += int(w[8])
        p("     Tick %5d | %s" % (r["t"], " | ".join("Sp%d: %s" % (q, ", ".join("%s %d" % (wa, n) for (sq, wa), n in sorted(s.items()) if sq == q))
                                                    for q in sorted({k[0] for k in s}))))

    # 4. Neue Kampfeinheiten und neue Gebaeude je Spieler (erste Lagezeile = Startbestand, zaehlt nicht)
    def kosten_einheit(typ):
        u = B["units"].get(LIGA_NAME[typ], {})
        if "goldCost" in u:
            return u["goldCost"], "Balance"
        return OHNE_BALANCE.get(typ, (0, "unbekannt"))

    vorher, neu_e = None, {}
    for r in Z:
        jetzt = {}
        for e in r["einheiten"].split("\n")[2:]:
            w = e.split()
            if len(w) >= 6 and int(w[2]) in LIGA_NAME and int(w[1]) > 0 and int(w[5]) > 0:
                jetzt[int(w[0])] = (int(w[1]), int(w[2]))
        if vorher is not None:
            for nr, (q, typ) in jetzt.items():
                if vorher.get(nr) != (q, typ):
                    neu_e.setdefault(q, []).append((r["t"], typ))
        vorher = jetzt
    p()
    p("4. NEU ANGEWORBENE KAMPFEINHEITEN (Slot + Typ neu, Startbestand nicht gezaehlt) x Anwerbegold:")
    for q in sorted(neu_e):
        n = Counter(typ for _, typ in neu_e[q])
        g = sum(kosten_einheit(typ)[0] * k for typ, k in n.items())
        je = Counter()
        for t, typ in neu_e[q]:
            je[t // 4000] += kosten_einheit(typ)[0]
        p("   Spieler %d: %d Einheiten, %d Gold: %s" % (q, sum(n.values()), g, ", ".join(
            "%d %s (%d %s)" % (k, KURZ[typ], kosten_einheit(typ)[0], kosten_einheit(typ)[1]) for typ, k in n.most_common())))
        p("      Gold je 4.000 Ticks: %s" % ", ".join("%d-%d: %d" % (k * 4000, (k + 1) * 4000, v) for k, v in sorted(je.items())))
    gesehen, neu_g = None, {}
    for r in Z:
        uids = {}
        for e in r["gebaeude"].split("\n")[1:]:
            w = e.split()
            if len(w) >= 7 and int(w[1]) > 0:
                uids[int(w[6])] = (int(w[1]), int(w[2]))
        if gesehen is not None:
            for u, (q, typ) in uids.items():
                if u not in gesehen:
                    neu_g.setdefault(q, Counter())[typ] += 1
            gesehen.update(uids)
        else:
            gesehen = dict(uids)

    from selfaware.game.ucp.bauen import NACH_TYP
    p("5. NEUE GEBAEUDE je Spieler (nach der ersten Lagezeile):")
    for q in sorted(neu_g):
        p("   Spieler %d: %s" % (q, ", ".join("%d %s" % (k, NACH_TYP.get(t, {}).get("name", t)) for t, k in neu_g[q].most_common())))
    os.makedirs(AUS, exist_ok=True)
    open(os.path.join(AUS, "gold_%s.txt" % stamp), "w", encoding="utf-8").write("\n".join(aus) + "\n")
    print("gesichert: data/research/lernen/gold_%s.txt" % stamp)


if __name__ == "__main__":
    main()
