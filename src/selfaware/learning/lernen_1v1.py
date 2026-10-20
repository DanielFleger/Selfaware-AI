# -*- coding: utf-8 -*-
"""Lernkreis fuer die 1v1-SamurAI (Daniel 19.10.2026 23:43: "mache das Lernen selbststaendig, bis ich sage stopp").
lernen.py lernt die Solo-Aufgabe (10/25 Streitkolbenkaempfer, leere KI); hier lernt die SamurAI so, wie sie gegen
Daniel spielt: Einstellungen der SamurAI-Wache (samurai_wache.LENKER_ARGS), echte Gegner-KI, eigenes Gefecht.

Ablauf je Schritt (gepaarter Vergleich - eine Startposition je Schritt, Daniel 19.10.: "bei jedem Test eine andere
Position, bis alle durch sind, dann andere Map"):
  1. Position = naechste aus POSITIONEN (reihum).
  2. Ein Knopf anders als in der besten Strategie (der Knopfwert mit den wenigsten Vergleichen zuerst).
  3. Zwei Laeufe auf DERSELBEN Position bis BIS_TICK: A = beste Strategie, B = mit dem geaenderten Knopf.
  4. Wert je Lauf (GEMESSEN aus dem Lageprotokoll; Metrik 2 ab 20.10. 00:05 mit Truppenwert): Gold-Einnahmen der ganzen
     Partie (Summe aller Gold-Zuwaechse
     zwischen zwei Lagezeilen) + Verkaufswert des Lagers am Ende (Preise aus der Balance-Datei der Instanz, je Stueck =
     Los-Preis / 5; Holz 0,25 je Stueck - gemessen 19.10., 400 Holz brachten ~80-100 Gold). Das ist das Gold, das fuer
     Truppen da war oder da waere (B-120) + Truppenwert der lebenden eigenen Kampfeinheiten am Ende (Anwerbegold + Waffen
     zum Verkaufspreis) - sonst waere eigene Waffenproduktion gegen Verkauf + Soeldner (B-128) nicht vergleichbar.
  5. Unterschied B gegen A in Prozent je Knopfwert sammeln. Uebernommen wird ein Knopfwert, sobald er in mindestens
     UEBERNAHME_N Vergleichen IMMER besser war (keine Niederlage) - dann ist er Teil der besten Strategie.
Alles nach data/research/lernen_1v1.jsonl (je Lauf) und data/research/lernen_1v1_wissen.json (beste Strategie, Wirkung je Knopfwert).
Jede Partie geht ausserdem durch partie_lernen.py (Trainingsdaten, Gold-Bilanz).
Anhalten: Datei var/legacy/STOP_LERNEN anlegen (der laufende Schritt wird zu Ende gespielt) oder den Prozess beenden.
Pause fuer Code-Aenderungen: var/legacy/PAUSE_LERNEN anlegen - der Kreis wartet vor dem naechsten Schritt, bis sie weg ist
(sonst laufen A und B mit verschiedenem Code; das erkennt der Kreis an der CODE-KENNUNG und verwirft das Paar).
Aufruf: SHC_INSTANZ=5 uv run python -m selfaware.learning.lernen_1v1 [schritte=1000] [bis_tick=15000]"""

from selfaware import workspace as _workspace
import glob
import gzip
import json
import os
import re
import subprocess
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(_workspace.DATA)
AUS = os.path.join(D, "lernen_1v1")
STOP = os.path.join(_workspace.STATE, "STOP_LERNEN")
PAUSE = os.path.join(_workspace.STATE, "PAUSE_LERNEN")  # wartet vor dem naechsten Schritt (Code-Aenderungen)
PROTOKOLL = os.path.join(D, "lernen_1v1.jsonl")
WISSEN = os.path.join(D, "lernen_1v1_wissen.json")


POSITIONEN = [("Green Haven", "4,3"), ("Close Encounters", "2,3"), ("Green Haven", "3,4"), ("Close Encounters", "3,2"),
              ("The Killing Plains", "0,1"), ("The Killing Plains", "1,0")]
KNOEPFE = {
    # 20.10. 00:13: Daniels Siegerweg zuerst pruefen (B-128 Verkauf + Soeldner, B-129 Deckung) - Reihenfolge = Testfolge
    "heer_anteil": [0.0, 0.3, 0.6],            # B-132: Anteil jedes Gold-Zuwachses fuer die Heereskasse
    "produktion": ["ja", "nein"],              # B-128: eigene Waffenkette ODER (Daniels Weg) Stein/Eisen verkaufen + Soeldner
    "deckung_soll": [0, 4, 8],                 # B-129: Schleuderer decken die Brand-Sklaven
    "lager_max": [45, 60, 75],                 # B-124
    "steinbrueche_frueh": [2, 0, 3],           # B-125
    "kausal_sparen": ["ja", "nein"],           # B-122
    "kausal_horizont": [16000, 10000, 24000],  # B-123
    "holzfaeller_je_baum": [4, 2, 1],
    "holz_spam": [20, 10, 0],
}
METRIK = 3     # 3 = Einnahmen + Lagerwert + Truppenwert + Feindschaden (ab 20.10. 00:15); andere Metriken zaehlen nicht
# Feindschaden: feindliche Gebaeude, die im Lauf verschwunden sind (uid gesehen, am Ende weg; Lagerplatz/Steinhaufen nicht),
# bewertet mit den Baukosten der Balance-Datei in Gold (Holz und Stein zum Kaufpreis je Stueck)
GEB_NAME = {1: "Hovel", 3: "Woodcutter hut", 4: "Ox tether", 5: "Iron mine", 6: "Pitch rig", 7: "Hunters hut",
            8: "Mercenary post", 9: "Barracks", 11: "Armory", 12: "Fletcher", 13: "Blacksmith", 14: "Poleturner",
            15: "Armourer", 16: "Tanner", 17: "Bakery", 18: "Brewery", 20: "Quarry", 22: "Inn", 23: "Apothecary",
            26: "Marketplace", 27: "Well", 28: "Oil smelter", 30: "Wheat farm", 31: "Hop farm", 32: "Apple farm",
            33: "Dairy farm", 34: "Mill", 35: "Stables"}
NICHT_SCHADEN = {10, 21}
# Truppenwert je lebender eigener Kampfeinheit am Ende: Anwerbegold (Balance units.goldCost) + Waffen zum Verkaufspreis
# (Balance resources sell / 5 je Stueck); fuer Einheiten ohne goldCost der Spielwert (Sklave 5 gemessen, Schleuder 12 Vanilla)
EINHEIT = {22: ("European archer", ["Bow"]), 23: ("European crossbowman", ["Xbow", "Leather"]),
           24: ("European spearman", ["Spear"]), 25: ("European pikeman", ["Armor"]),
           26: ("European maceman", ["Mace", "Leather"]), 27: ("European swordsman", ["Sword", "Armor"]),
           28: ("European knight", ["Sword", "Armor"]), 70: ("Arabian archer", []), 71: ("Arabian slave", []),
           72: ("Arabian slinger", []), 73: ("Arabian assassin", []), 74: ("Arabian horse archer", []),
           75: ("Arabian swordsman", []), 76: ("Arabian firethrower", [])}
OHNE_GOLDCOST = {71: 5, 72: 12}
UEBERNAHME_N = 2
BIS_TICK = 24000        # 20.10. 00:30: Daniels Partie entschied sich zwischen Tick 19.000 und 24.000
TEMPO = 100
HOLZ_JE_STUECK = 0.25


def wache_args():
    """Die Einstellungen, mit denen die SamurAI gegen Daniel spielt - ohne Uebernahme, Laufzeit und Tempo."""
    t = open(_workspace.module_file('samurai_wache'), encoding="utf-8").read()
    m = re.search(r"LENKER_ARGS = \((.*?)\)\.split\(\)", t, re.S)
    a = "".join(re.findall(r'"([^"]*)"', m.group(1))).split()
    weg = ("uebernehmen=", "bis_tick=", "minuten=", "tempo=") + tuple(k + "=" for k in KNOEPFE)
    return [x for x in a if not x.startswith(weg)]


def preise():
    import selfaware.telemetry.gold_bilanz as gold_bilanz
    B = json.load(open(gold_bilanz.balance_datei(int(os.environ.get("SHC_INSTANZ", "1"))), encoding="utf-8"))
    p = {}
    for name, ware in (("Stone", "stein"), ("Iron", "eisen"), ("Hop", "hopfen"), ("Pitch", "pech"), ("Wheat", "weizen"),
                       ("Flour", "mehl")):
        sell = (B["resources"].get(name) or {}).get("sell")
        if sell:
            p[ware] = float(sell) / 5.0
    p["holz"] = HOLZ_JE_STUECK
    tw = {}
    for typ, (name, waffen) in EINHEIT.items():
        g = (B["units"].get(name) or {}).get("goldCost", OHNE_GOLDCOST.get(typ, 0))
        for w in waffen:
            r = B["resources"].get(w) or {}
            g += float(r.get("sell", r.get("buy", 0) / 2.0)) / 5.0
        tw[typ] = round(g, 1)
    p["_truppen"] = tw
    holz_k = float((B["resources"].get("Wood") or {}).get("buy", 15)) / 5.0
    stein_k = float((B["resources"].get("Stone") or {}).get("buy", 50)) / 5.0
    gw = {}
    for typ, name in GEB_NAME.items():
        c = (B["buildings"].get(name) or {}).get("cost")
        if c:
            gw[typ] = round(c[0] * holz_k + c[1] * stein_k + c[4], 1)
    p["_gebaeude"] = gw
    return p


def wert(lage, P, sp=1):
    einnahmen, letzte, vor, zeile = 0, None, None, None
    feind = {}          # uid -> Typ, alle je gesehenen feindlichen Gebaeude
    for z in gzip.open(lage, "rt", encoding="utf-8"):
        zeile = json.loads(z)
        st = zeile["st"]
        if vor is not None and st.get("gold", 0) > vor:
            einnahmen += st["gold"] - vor
        vor, letzte = st.get("gold", 0), st
        for e in zeile["gebaeude"].split("\n")[1:]:
            w = e.split()
            if len(w) >= 7 and int(w[1]) not in (0, sp) and int(w[2]) not in NICHT_SCHADEN:
                feind[w[6]] = int(w[2])
    waren = {w: p for w, p in P.items() if not w.startswith("_")}
    lager = sum(letzte.get(w, 0) * p for w, p in waren.items())
    truppen = {}
    for e in zeile["einheiten"].split("\n")[2:]:
        w = e.split()
        if len(w) >= 6 and int(w[1]) == sp and int(w[2]) in P["_truppen"] and int(w[5]) > 0:
            truppen[int(w[2])] = truppen.get(int(w[2]), 0) + 1
    tw = sum(P["_truppen"][k] * n for k, n in truppen.items())
    am_ende = {e.split()[6] for e in zeile["gebaeude"].split("\n")[1:] if len(e.split()) >= 7}
    weg = [typ for u, typ in feind.items() if u not in am_ende]
    schaden = sum(P["_gebaeude"].get(typ, 0) for typ in weg)
    return {"metrik": METRIK, "einnahmen": einnahmen, "lager_wert": round(lager, 1), "truppen_wert": round(tw, 1),
            "feindschaden": round(schaden, 1), "feind_verloren": len(weg),
            "wert": round(einnahmen + lager + tw + schaden, 1), "tick": letzte.get("t"), "leute": letzte.get("leute"),
            "lager": {w: letzte.get(w, 0) for w in waren if letzte.get(w, 0)}, "truppen": truppen}


def lauf(strategie, pos, nr, rolle, P):
    stempel = time.strftime("%Y%m%d_%H%M%S")
    os.makedirs(AUS, exist_ok=True)
    konsole = os.path.join(AUS, "lauf_%s_%d%s_konsole.txt" % (stempel, nr, rolle))
    args = [sys.executable, '-u', '-m', 'selfaware.runtime.live.erstes_spiel'] + wache_args() + \
        ["tempo=%d" % TEMPO, "bis_tick=%d" % BIS_TICK, "minuten=40", "karte=%s" % pos[0], "plaetze=%s" % pos[1], "gegner_ki=7"] + \
        ["%s=%s" % kv for kv in sorted(strategie.items())]
    t0 = time.time()
    with open(konsole, "w", encoding="utf-8") as f:
        try:
            rc = subprocess.run(args, stdout=f, stderr=subprocess.STDOUT, cwd=HIER, timeout=3600).returncode
        except subprocess.TimeoutExpired:
            rc = "Zeit"
    text = open(konsole, encoding="utf-8", errors="replace").read()
    lp = re.search(r"Lageprotokoll \(jede Runde komplett\): (.+?\.jsonl\.gz)", text)
    kennung = re.search(r"CODE-KENNUNG (\w+)", text)
    r = {"nr": nr, "rolle": rolle, "zeit": stempel, "position": list(pos), "strategie": strategie, "rc": rc, "code": kennung.group(1) if kennung else None,
         "dauer_s": round(time.time() - t0), "konsole": os.path.relpath(konsole, os.path.join(_workspace.ROOT))}
    fehler = re.search(r"Traceback|EROEFFNUNGSPLAN .*|ABBRUCH[^\n]*", text)
    if not lp or not os.path.exists(lp.group(1)):
        r["ungueltig"] = "kein Lageprotokoll" + (" (%s)" % fehler.group(0)[:120] if fehler else "")
        return r
    r["lage"] = os.path.relpath(lp.group(1), os.path.join(_workspace.ROOT))
    r.update(wert(lp.group(1), P))
    if fehler and "Traceback" in fehler.group(0):
        r["fehler"] = "Traceback im Lenker"
    if (r.get("tick") or 0) < 0.8 * BIS_TICK:
        r["ungueltig"] = "nur bis Tick %s" % r.get("tick")
    # Trainingsdaten wie bei jeder Partie
    subprocess.run([sys.executable, '-P', '-m', 'selfaware.learning.partie_lernen', konsole, lp.group(1), 'gegner=KI 7', 'anmerkung=lernen_1v1 Lauf %d%s %s %s' % (nr, rolle, pos[0], pos[1])],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=HIER, timeout=900)
    return r


def laden():
    alle = [json.loads(z) for z in open(PROTOKOLL, encoding="utf-8")] if os.path.exists(PROTOKOLL) else []
    w = json.load(open(WISSEN, encoding="utf-8")) if os.path.exists(WISSEN) else {}
    return alle, w.get("beste") or {}, w.get("vergleiche") or {}


def naechster_knopf(beste, vergleiche):
    kand = []
    for k, werte in KNOEPFE.items():
        jetzt = beste.get(k, werte[0])
        for v in werte:
            if v != jetzt:
                n = sum(1 for x in vergleiche.get("%s=%s" % (k, v), []) if x.get("metrik") == METRIK)
                kand.append((n, list(KNOEPFE).index(k), k, v))
    kand.sort()
    return (kand[0][2], kand[0][3]) if kand else (None, None)


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    global BIS_TICK
    BIS_TICK = int(arg.get("bis_tick", BIS_TICK))
    schritte = int(arg.get("schritte", 1000))
    P = preise()
    alle, beste, vergleiche = laden()
    beste = dict({k: v[0] for k, v in KNOEPFE.items()}, **beste)
    nr = max([r.get("nr", 0) for r in alle] + [0]) + 1
    pos_i = len({r["nr"] for r in alle}) % len(POSITIONEN)
    print("LERNEN 1v1: Instanz %s, bis Tick %d, Preise je Stueck %s, beste Strategie %s" % (
        os.environ.get("SHC_INSTANZ"), BIS_TICK, P, beste), flush=True)
    for _ in range(schritte):
        if os.path.exists(STOP):
            print("LERNEN 1v1: STOP_LERNEN gefunden - Ende", flush=True)
            break
        if os.path.exists(PAUSE):
            print("LERNEN 1v1: PAUSE_LERNEN - warte", flush=True)
            while os.path.exists(PAUSE) and not os.path.exists(STOP):
                time.sleep(5)
            if os.path.exists(STOP):
                continue
            print("LERNEN 1v1: weiter", flush=True)
        pos = POSITIONEN[pos_i % len(POSITIONEN)]
        pos_i += 1
        k, v = naechster_knopf(beste, vergleiche)
        variante = dict(beste, **{k: v})
        print("SCHRITT %d: %s Platz %s - %s = %s (statt %s)" % (nr, pos[0], pos[1], k, v, beste[k]), flush=True)
        a = lauf(dict(beste), pos, nr, "A", P)
        b = lauf(variante, pos, nr, "B", P)
        for r in (a, b):
            r["knopf"] = "%s=%s" % (k, v)
            with open(PROTOKOLL, "a", encoding="utf-8") as f:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        if a.get("code") != b.get("code"):
            # zwischen A und B wurde am Lenker gebaut - der Vergleich misst dann den Code, nicht den Knopf
            b["ungueltig"] = "Code zwischen A und B geaendert (%s -> %s)" % (a.get("code"), b.get("code"))
        if a.get("ungueltig") or b.get("ungueltig"):
            print("  UNGUELTIG: A %s | B %s" % (a.get("ungueltig", "ok"), b.get("ungueltig", "ok")), flush=True)
            nr += 1
            continue
        diff = 100.0 * (b["wert"] - a["wert"]) / max(1.0, a["wert"])
        schl = "%s=%s" % (k, v)
        vergleiche.setdefault(schl, []).append({"nr": nr, "metrik": METRIK, "position": "%s %s" % pos, "a": a["wert"], "b": b["wert"],
                                                "diff_prozent": round(diff, 1)})
        print("  A %.0f (Einnahmen %d, Lager %s, Truppen %s, Feindschaden %.0f) | B %.0f (Einnahmen %d, Lager %s, Truppen %s, "
              "Feindschaden %.0f) -> %+.1f %%" % (a["wert"], a["einnahmen"], a["lager"], a["truppen"], a["feindschaden"], b["wert"],
                                                b["einnahmen"], b["lager"], b["truppen"], b["feindschaden"], diff), flush=True)
        vg = [x for x in vergleiche[schl] if x.get("metrik") == METRIK]
        if len(vg) >= UEBERNAHME_N and all(x["diff_prozent"] > 0 for x in vg):
            beste = variante
            print("  UEBERNOMMEN: %s - in %d Vergleichen immer besser (%s)" % (schl, len(vg), [x["diff_prozent"] for x in vg]), flush=True)
        json.dump({"stand": time.strftime("%Y-%m-%d %H:%M"), "beste": beste, "vergleiche": vergleiche,
                   "bis_tick": BIS_TICK, "preise_je_stueck": P}, open(WISSEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        nr += 1
    print("LERNEN 1v1 Ende: beste Strategie %s" % beste, flush=True)


if __name__ == "__main__":
    main()
