# -*- coding: utf-8 -*-
"""Lernkreis fuer die 1v1-SamurAI (Daniel 19.10.2026 23:43: "mache das Lernen selbststaendig, bis ich sage stopp").
lernen.py lernt die Solo-Aufgabe (10/25 Streitkolbenkaempfer, leere KI); hier lernt die SamurAI so, wie sie gegen
Daniel spielt: Einstellungen der SamurAI-Wache (samurai_wache.LENKER_ARGS), echte Gegner-KI, eigenes Gefecht.

Ablauf je Schritt (gepaarter Vergleich - eine Startposition je Schritt, Daniel 19.10.: "bei jedem Test eine andere
Position, bis alle durch sind, dann andere Map"):
  1. Position = naechste aus POSITIONEN (reihum).
  2. Ein Knopf anders als in der besten Strategie (der Knopfwert mit den wenigsten Vergleichen zuerst).
  3. Zwei Laeufe auf DERSELBEN Position bis BIS_TICK: A = beste Strategie, B = mit dem geaenderten Knopf.
  4. Wert je Lauf (GEMESSEN aus dem Lageprotokoll): Gold-Einnahmen der ganzen Partie (Summe aller Gold-Zuwaechse
     zwischen zwei Lagezeilen) + Verkaufswert des Lagers am Ende (Preise aus der Balance-Datei der Instanz, je Stueck =
     Los-Preis / 5; Holz 0,25 je Stueck - gemessen 19.10., 400 Holz brachten ~80-100 Gold). Das ist das Gold, das fuer
     Truppen da war oder da waere (B-120).
  5. Unterschied B gegen A in Prozent je Knopfwert sammeln. Uebernommen wird ein Knopfwert, sobald er in mindestens
     UEBERNAHME_N Vergleichen IMMER besser war (keine Niederlage) - dann ist er Teil der besten Strategie.
Alles nach daten/lernen_1v1.jsonl (je Lauf) und daten/lernen_1v1_wissen.json (beste Strategie, Wirkung je Knopfwert).
Jede Partie geht ausserdem durch partie_lernen.py (Trainingsdaten, Gold-Bilanz).
Anhalten: Datei daten/STOP_LERNEN anlegen (der laufende Schritt wird zu Ende gespielt) oder den Prozess beenden.
Pause fuer Code-Aenderungen: daten/PAUSE_LERNEN anlegen - der Kreis wartet vor dem naechsten Schritt, bis sie weg ist
(sonst laufen A und B mit verschiedenem Code; das erkennt der Kreis an der CODE-KENNUNG und verwirft das Paar).
Aufruf: SHC_INSTANZ=5 python werkzeug/lernen_1v1.py [schritte=1000] [bis_tick=15000]"""
import glob
import gzip
import json
import os
import re
import subprocess
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HIER, "..", "daten")
AUS = os.path.join(D, "lernen_1v1")
STOP = os.path.join(D, "STOP_LERNEN")
PAUSE = os.path.join(D, "PAUSE_LERNEN")      # liegt sie da, wartet der Kreis vor dem naechsten Schritt (Code-Aenderungen)
PROTOKOLL = os.path.join(D, "lernen_1v1.jsonl")
WISSEN = os.path.join(D, "lernen_1v1_wissen.json")
sys.path.insert(0, HIER)

POSITIONEN = [("Green Haven", "4,3"), ("Close Encounters", "2,3"), ("Green Haven", "3,4"), ("Close Encounters", "3,2"),
              ("The Killing Plains", "0,1"), ("The Killing Plains", "1,0")]
KNOEPFE = {
    "lager_max": [45, 60, 75],                 # B-124
    "steinbrueche_frueh": [2, 0, 3],           # B-125
    "kausal_sparen": ["ja", "nein"],           # B-122
    "kausal_horizont": [16000, 10000, 24000],  # B-123
    "holzfaeller_je_baum": [4, 2, 1],
    "holz_spam": [20, 10, 0],
}
UEBERNAHME_N = 2
BIS_TICK = 15000
TEMPO = 100
HOLZ_JE_STUECK = 0.25


def wache_args():
    """Die Einstellungen, mit denen die SamurAI gegen Daniel spielt - ohne Uebernahme, Laufzeit und Tempo."""
    t = open(os.path.join(HIER, "samurai_wache.py"), encoding="utf-8").read()
    m = re.search(r"LENKER_ARGS = \((.*?)\)\.split\(\)", t, re.S)
    a = "".join(re.findall(r'"([^"]*)"', m.group(1))).split()
    weg = ("uebernehmen=", "bis_tick=", "minuten=", "tempo=") + tuple(k + "=" for k in KNOEPFE)
    return [x for x in a if not x.startswith(weg)]


def preise():
    import gold_bilanz
    B = json.load(open(gold_bilanz.balance_datei(int(os.environ.get("SHC_INSTANZ", "1"))), encoding="utf-8"))
    p = {}
    for name, ware in (("Stone", "stein"), ("Iron", "eisen"), ("Hop", "hopfen"), ("Pitch", "pech"), ("Wheat", "weizen"),
                       ("Flour", "mehl")):
        sell = (B["resources"].get(name) or {}).get("sell")
        if sell:
            p[ware] = float(sell) / 5.0
    p["holz"] = HOLZ_JE_STUECK
    return p


def wert(lage, P):
    einnahmen, letzte, vor = 0, None, None
    for z in gzip.open(lage, "rt", encoding="utf-8"):
        st = json.loads(z)["st"]
        if vor is not None and st.get("gold", 0) > vor:
            einnahmen += st["gold"] - vor
        vor, letzte = st.get("gold", 0), st
    lager = sum(letzte.get(w, 0) * p for w, p in P.items())
    return {"einnahmen": einnahmen, "lager_wert": round(lager, 1), "wert": round(einnahmen + lager, 1), "tick": letzte.get("t"),
            "leute": letzte.get("leute"), "lager": {w: letzte.get(w, 0) for w in P if letzte.get(w, 0)}}


def lauf(strategie, pos, nr, rolle, P):
    stempel = time.strftime("%Y%m%d_%H%M%S")
    os.makedirs(AUS, exist_ok=True)
    konsole = os.path.join(AUS, "lauf_%s_%d%s_konsole.txt" % (stempel, nr, rolle))
    args = [sys.executable, "-u", os.path.join(HIER, "erstes_spiel.py")] + wache_args() + \
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
         "dauer_s": round(time.time() - t0), "konsole": os.path.relpath(konsole, os.path.join(HIER, ".."))}
    fehler = re.search(r"Traceback|EROEFFNUNGSPLAN .*|ABBRUCH[^\n]*", text)
    if not lp or not os.path.exists(lp.group(1)):
        r["ungueltig"] = "kein Lageprotokoll" + (" (%s)" % fehler.group(0)[:120] if fehler else "")
        return r
    r["lage"] = os.path.relpath(lp.group(1), os.path.join(HIER, ".."))
    r.update(wert(lp.group(1), P))
    if fehler and "Traceback" in fehler.group(0):
        r["fehler"] = "Traceback im Lenker"
    if (r.get("tick") or 0) < 0.8 * BIS_TICK:
        r["ungueltig"] = "nur bis Tick %s" % r.get("tick")
    # Trainingsdaten wie bei jeder Partie
    subprocess.run([sys.executable, "-P", os.path.join(HIER, "partie_lernen.py"), konsole, lp.group(1), "gegner=KI 7",
                    "anmerkung=lernen_1v1 Lauf %d%s %s %s" % (nr, rolle, pos[0], pos[1])],
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
                kand.append((len(vergleiche.get("%s=%s" % (k, v), [])), list(KNOEPFE).index(k), k, v))
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
        vergleiche.setdefault(schl, []).append({"nr": nr, "position": "%s %s" % pos, "a": a["wert"], "b": b["wert"],
                                                "diff_prozent": round(diff, 1)})
        print("  A %.0f (Einnahmen %d, Lager %s) | B %.0f (Einnahmen %d, Lager %s) -> %+.1f %%" % (
            a["wert"], a["einnahmen"], a["lager"], b["wert"], b["einnahmen"], b["lager"], diff), flush=True)
        vg = vergleiche[schl]
        if len(vg) >= UEBERNAHME_N and all(x["diff_prozent"] > 0 for x in vg):
            beste = variante
            print("  UEBERNOMMEN: %s - in %d Vergleichen immer besser (%s)" % (schl, len(vg), [x["diff_prozent"] for x in vg]), flush=True)
        json.dump({"stand": time.strftime("%Y-%m-%d %H:%M"), "beste": beste, "vergleiche": vergleiche,
                   "bis_tick": BIS_TICK, "preise_je_stueck": P}, open(WISSEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        nr += 1
    print("LERNEN 1v1 Ende: beste Strategie %s" % beste, flush=True)


if __name__ == "__main__":
    main()
