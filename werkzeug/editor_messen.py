# -*- coding: utf-8 -*-
"""Kontrollierte Messungen im Karteneditor (Daniel 17.10.2026: "im Kreativmodus checken - jeden Abstand selbst und live
nachmessen, beliebig viele Gebaeude dazwischen"). Voraussetzung: Editor offen (Handbuch, Abschnitt Testing:
editor_test.py oeffnen), Modulbefehle setzeEinheit / setzeGebaeude / toeteAlle (logik.lua, 17.10.).

Reihe "abstand" (Entdeckung + Schaden in einem): ein feindlicher Schuetze (Spieler 2) bei (240,200), eine eigene Assassine
(Spieler 1) steht STILL im Abstand D links davon. Gemessen ueber BEOBACHTEN Ticks (mehr als 3 Pruefrunden der Assassine,
L75: alle 128 Takte): erster Lebensverlust (Tick und Abstand), Verlust je Takt danach, ob sie stirbt. Warum stillstehen statt
anlaufen: beim Gehen legt sie zwischen zwei Pruefrunden ~8 Felder zurueck - die Grenze waere nur auf 8 Felder genau.
Jede Zeile kommt nach daten/editor_messung_<stempel>.jsonl (eine Zeile je Versuch, mit Zeitreihe).

Aufruf:
  python editor_messen.py abstand [typen=22,23,70,72,74,76] [abstaende=30,25,22,20,18,15,12,10,8,6,4] [ticks=500] [wdh=1]
  python editor_messen.py auswerten <datei.jsonl>
"""
import io
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import befehl as K

D = os.path.join(HIER, "..", "daten")
SCHUETZE = (240, 200)
NAMEN = {22: "Bogen", 23: "Armbrust", 70: "arab. Bogen", 72: "Schleuder", 74: "Pferdebogen", 76: "Feuerwerfer"}


def sende(liste, bis=None, warte=4.0):
    return K.sende({"befehle": liste}, warte, bis=bis)


def lage():
    """(Tick, {nr: Einheit}) - ein Lagebild direkt aus dem Spiel."""
    sende([{"lagebild": True}], bis="LAGEBILD", warte=3.0)
    z = io.open(os.path.join(K.ABZUG, "lagebild.txt"), encoding="utf-8").read().splitlines()
    kopf = z[1].split()
    return int(z[0].split()[1]), {int(r.split()[0]): dict(zip(kopf, map(int, r.split()))) for r in z[2:] if r.strip()}


def leeren():
    sende([{"toeteAlle": 1}, {"toeteAlle": 2}], bis="TOETE ALLE: Spieler 2")
    for _ in range(40):                       # bis die Toten weg sind (Sterbeanimation)
        t, L = lage()
        if not [e for e in L.values() if e["besitzer"] in (1, 2)]:
            return True
        time.sleep(0.25)
    return False


def setze(sp, typ, x, y):
    z = sende([{"setzeEinheit": {"spieler": sp, "typ": typ, "x": x, "y": y}}], bis="SETZE EINHEIT")
    for s in z:
        if "SETZE EINHEIT" in s and "Nummern" in s:
            try:
                return int(s.rsplit("Nummern", 1)[1].strip().split(",")[0])
            except ValueError:
                return None
    return None


def versuch(typ, abstand, ticks):
    leeren()
    s = setze(2, typ, SCHUETZE[0] - 1, SCHUETZE[1] - 1)     # +4 Mikro -> landet 1 Feld weiter (gemessen 17.10.)
    a = setze(1, 73, SCHUETZE[0] - 1 - abstand, SCHUETZE[1] - 1)
    t0, L = lage()
    reihe, erster = [], None
    while True:
        t, L = lage()
        ea, es = L.get(a), L.get(s)
        if ea is None or ea["besitzer"] != 1:
            reihe.append((t, None, None, es and es["zustand"]))
            break
        d = max(abs(ea["x"] - es["x"]), abs(ea["y"] - es["y"])) if es else None
        reihe.append((t, ea["leben"], d, es and es["zustand"], ea["zustand"], (ea["x"], ea["y"])))
        if erster is None and ea["leben"] < 12500:
            erster = (t - t0, d)
        if t - t0 >= ticks:
            break
        time.sleep(0.05)
    leben_ende = reihe[-1][1] if reihe[-1][1] is not None else 0
    tot = reihe[-1][1] is None
    rate = None
    if erster:
        dauer = (reihe[-1][0] - t0) - erster[0]
        rate = (12500 - leben_ende) / max(1, dauer)
    # jeder einzelne Treffer: (Tick seit Start, Schaden) - daraus Schaden je Treffer und Abstand der Treffer
    treffer, vor = [], 12500
    for z in reihe:
        if z[1] is not None and z[1] < vor:
            treffer.append((z[0] - t0, vor - z[1]))
            vor = z[1]
    takte = [b[0] - a_[0] for a_, b in zip(treffer, treffer[1:])]
    return {"typ": typ, "art": NAMEN.get(typ, typ), "abstand": abstand, "ticks": reihe[-1][0] - t0, "erster_treffer": erster,
            "leben_ende": leben_ende, "tot": tot, "rate_je_tick": rate, "treffer": treffer,
            "schaden_je_treffer": (sum(s for _, s in treffer) / len(treffer)) if treffer else None,
            "takt_median": sorted(takte)[len(takte) // 2] if takte else None, "reihe": reihe}


def reihe_abstand(arg):
    typen = [int(x) for x in arg.get("typen", "22,23,70,72,74,76").split(",")]
    abst = [int(x) for x in arg.get("abstaende", "30,25,22,20,18,15,12,10,8,6,4").split(",")]
    ticks, wdh = int(arg.get("ticks", 900)), int(arg.get("wdh", 1))
    datei = os.path.join(D, "editor_messung_%s.jsonl" % time.strftime("%Y%m%d_%H%M%S"))
    print("Ergebnis ->", os.path.abspath(datei), flush=True)
    for typ in typen:
        for d in abst:
            for w in range(wdh):
                r = versuch(typ, d, ticks)
                r["wdh"] = w + 1
                io.open(datei, "a", encoding="utf-8").write(json.dumps(r) + "\n")
                print("%-12s D=%2d: erster Treffer %s, %d Treffer je %s Schaden, Takt %s, Rate %s je Tick, Leben Ende %s%s" % (
                    r["art"], d, r["erster_treffer"], len(r["treffer"]), "%.0f" % r["schaden_je_treffer"] if r["schaden_je_treffer"] else "-",
                    r["takt_median"], "%.1f" % r["rate_je_tick"] if r["rate_je_tick"] is not None else "-",
                    r["leben_ende"], " TOT" if r["tot"] else ""), flush=True)
    leeren()
    return datei


def kette(typ, abstand, ticks=900):
    """Tick-genau (Modulbefehl tickProtokoll): wann traegt der Schuetze die Assassine als Ziel ein (Erkennen), wann wechselt
    sein Zustand / laeuft seine Animation (Angriffsanimation), wann verliert sie Leben (Treffer)."""
    leeren()
    s = setze(2, typ, SCHUETZE[0] - 1, SCHUETZE[1] - 1)
    a = setze(1, 73, SCHUETZE[0] - 1 - abstand, SCHUETZE[1] - 1)
    rel = "ucp/villagestudio/tick_kette.txt"
    quelle = os.path.join(K.SPIEL, rel.replace("/", os.sep))
    if os.path.exists(quelle):
        os.remove(quelle)
    sende([{"tickProtokoll": {"nr": [s, a], "ticks": ticks, "datei": rel}}], bis="TICKPROTOKOLL")
    ende = time.time() + ticks / 20.0 + 30
    while time.time() < ende and not os.path.exists(quelle):
        time.sleep(0.5)
    time.sleep(0.5)
    z = io.open(quelle, encoding="utf-8").read().splitlines()
    kopf = z[0].split()
    zeilen = [dict(zip(kopf, map(int, r.split()))) for r in z[1:] if r.strip()]
    S = [r for r in zeilen if r["nr"] == s]
    A = [r for r in zeilen if r["nr"] == a]
    t0 = zeilen[0]["tick"]
    ereig = []
    for vor, nach in zip(S, S[1:]):
        for f in ("state", "angegriffen", "ziel", "zielart", "suche"):
            if vor[f] != nach[f]:
                ereig.append((nach["tick"] - t0, "Schuetze %s %d->%d" % (f, vor[f], nach[f])))
        if nach["animzyklus"] != vor["animzyklus"] and nach["state"] != 0:
            pass
    for vor, nach in zip(A, A[1:]):
        if nach["leben"] < vor["leben"]:
            ereig.append((nach["tick"] - t0, "TREFFER -%d (Leben %d)" % (vor["leben"] - nach["leben"], nach["leben"])))
        if nach["logisch"] != vor["logisch"]:
            ereig.append((nach["tick"] - t0, "Assassine logisch %d->%d" % (vor["logisch"], nach["logisch"])))
    ereig.sort()
    erkannt = next((r["tick"] - t0 for r in S if a in (r["angegriffen"], r["ziel"])), None)
    treffer = [e[0] for e in ereig if e[1].startswith("TREFFER")]
    return {"typ": typ, "art": NAMEN.get(typ, typ), "abstand": abstand, "erkannt": erkannt, "erster_treffer": treffer[0] if treffer else None,
            "treffer": treffer, "ereignisse": ereig, "schuetze_nr": s, "assassine_nr": a}


def reihe_kette(arg):
    typen = [int(x) for x in arg.get("typen", "22,23,70,72,74,76").split(",")]
    abst = [int(x) for x in arg.get("abstaende", "10,5").split(",")]
    datei = os.path.join(D, "editor_kette_%s.jsonl" % time.strftime("%Y%m%d_%H%M%S"))
    print("Ergebnis ->", os.path.abspath(datei), flush=True)
    for typ in typen:
        for d in abst:
            r = kette(typ, d, int(arg.get("ticks", 900)))
            io.open(datei, "a", encoding="utf-8").write(json.dumps(r) + chr(10))
            tr = r["treffer"]
            print("%-12s D=%2d: erkannt %s, erster Treffer %s, Treffer-Takte %s" % (
                r["art"], d, r["erkannt"], r["erster_treffer"], [b - a_ for a_, b in zip(tr, tr[1:])][:6]), flush=True)
            for e in r["ereignisse"][:14]:
                print("     %5d  %s" % e, flush=True)
    leeren()
    return datei


def spaeher(abstand, mit_spaeher, typ=22, ticks=900):
    """Reihe E: macht ein anderer waehlbarer Feind nahe der Assassine sie fuer einen weit entfernten Schuetzen sichtbar (L75)?
    Schuetze bei SCHUETZE, Assassine im Abstand D links, Speertraeger (24) 8 Felder WEITER links (nicht auf der Linie zum
    Schuetzen, ausserhalb seiner Verfolgung 5 Felder, innerhalb 20 Felder Sicht)."""
    leeren()
    s = setze(2, typ, SCHUETZE[0] - 1, SCHUETZE[1] - 1)
    ax = SCHUETZE[0] - 1 - abstand
    a = setze(1, 73, ax, SCHUETZE[1] - 1)
    sp = setze(2, 24, ax - 8, SCHUETZE[1] - 1) if mit_spaeher else None
    t0, L = lage()
    treffer, vor, t = [], 12500, t0
    while t - t0 < ticks:
        time.sleep(0.05)
        t, L = lage()
        e = L.get(a)
        if e is None or e["besitzer"] != 1:
            treffer.append((t - t0, "tot"))
            break
        if e["leben"] < vor:
            treffer.append((t - t0, vor - e["leben"]))
            vor = e["leben"]
    sp_ort = (L[sp]["x"], L[sp]["y"]) if sp and sp in L else None
    return {"typ": typ, "abstand": abstand, "spaeher": bool(mit_spaeher), "treffer": treffer, "leben_ende": vor,
            "spaeher_ort_ende": sp_ort, "assassine_ort_ende": (L[a]["x"], L[a]["y"]) if a in L else None}


def reihe_spaeher(arg):
    abst = [int(x) for x in arg.get("abstaende", "25,30,35,40,45,50").split(",")]
    typ = int(arg.get("typ", 22))
    datei = os.path.join(D, "editor_spaeher_%s.jsonl" % time.strftime("%Y%m%d_%H%M%S"))
    print("Ergebnis ->", os.path.abspath(datei), flush=True)
    for d in abst:
        for mit in (True, False):
            r = spaeher(d, mit, typ, int(arg.get("ticks", 900)))
            io.open(datei, "a", encoding="utf-8").write(json.dumps(r) + chr(10))
            print("%s D=%2d %s Spaeher: Treffer %s, Leben Ende %d, Spaeher Ende %s" % (
                NAMEN.get(typ, typ), d, "mit " if mit else "ohne", r["treffer"][:8], r["leben_ende"], r["spaeher_ort_ende"]), flush=True)
    leeren()
    return datei


def gebaeude_angriff(abstand, zeile, typ=22, ticks=1200):
    """Reihe D: wird eine Assassine beim Zerstoeren eines Gebaeudes beschossen? Schuetze bei (240, y), Holzfaellerhuette
    (Mapper 51, 3x3) so, dass ihr naechstes Feld `abstand` Felder vom Schuetzen liegt; Assassine kommt von links."""
    y = 60 + 14 * zeile
    leeren()
    s = setze(2, typ, 239, y - 1)
    gx = 240 - abstand - 2
    z = sende([{"setzeGebaeude": {"spieler": 2, "x": gx, "y": y - 1, "mapper": 51, "groesse": 3}}], bis="SETZE GEBAEUDE")
    sende([{"lagebild": True}], bis="LAGEBILD", warte=3.0)
    G = [r.split() for r in io.open(os.path.join(K.ABZUG, "gebaeude.txt"), encoding="utf-8").read().splitlines()[1:] if r.strip()]
    gn = next((int(r[0]) for r in G if int(r[1]) == 2 and int(r[3]) == gx and int(r[4]) == y - 1), None)
    a = setze(1, 73, gx - 10, y - 1)
    sende([{"player": 1, "angriff": {"einheiten": [a], "gebaeude": gn}}], bis="ANGRIFF")
    t0, L = lage()
    treffer, vor, t, nah = [], 12500, t0, []
    while t - t0 < ticks:
        time.sleep(0.05)
        t, L = lage()
        e = L.get(a)
        if e is None or e["besitzer"] != 1:
            treffer.append((t - t0, "tot"))
            break
        es = L.get(s)
        if es and e["zustand"] in (106, 107):
            nah.append(max(abs(e["x"] - es["x"]), abs(e["y"] - es["y"])))
        if e["leben"] < vor:
            treffer.append((t - t0, vor - e["leben"], e["zustand"], (e["x"], e["y"])))
            vor = e["leben"]
    Gn = [r.split() for r in io.open(os.path.join(K.ABZUG, "gebaeude.txt"), encoding="utf-8").read().splitlines()[1:] if r.strip()]
    steht = any(int(r[0]) == gn for r in Gn)
    return {"typ": typ, "abstand_gebaeude": abstand, "gebaeude": gn, "zerstoert": not steht, "treffer": treffer,
            "angriffsabstand_min": min(nah) if nah else None, "angriffsabstand_max": max(nah) if nah else None, "leben_ende": vor}


def reihe_gebaeude(arg):
    abst = [int(x) for x in arg.get("abstaende", "10,14,17,19,21,23,26").split(",")]
    typ = int(arg.get("typ", 22))
    datei = os.path.join(D, "editor_gebaeude_%s.jsonl" % time.strftime("%Y%m%d_%H%M%S"))
    print("Ergebnis ->", os.path.abspath(datei), flush=True)
    for i, d in enumerate(abst):
        r = gebaeude_angriff(d, i, typ, int(arg.get("ticks", 1200)))
        io.open(datei, "a", encoding="utf-8").write(json.dumps(r) + chr(10))
        print("%s Gebaeude %2d Felder vom Schuetzen: Angriff aus %s-%s Feldern, zerstoert %s, Treffer %s, Leben Ende %d" % (
            NAMEN.get(typ, typ), d, r["angriffsabstand_min"], r["angriffsabstand_max"], r["zerstoert"], r["treffer"][:6], r["leben_ende"]), flush=True)
    leeren()
    return datei


DECKUNG = {"keins": None, "Holzfaellerhuette": (51, 3), "Kornspeicher": (80, 4), "Lagerplatz": (52, 5), "Apfelplantage": (72, 10),
           "Kaserne": (87, 5), "Wachturm": (110, 3), "Bergfried": (61, 7)}


def deckung(name, zeile, typ=22, abstand=14, ticks=900):
    """Reihe C: sperrt ein Gebaeude auf der Linie Schuetze -> Assassine den Beschuss? Beide sichtbar nah (abstand <= 20)."""
    y = 60 + 16 * zeile
    leeren()
    s = setze(2, typ, 239, y - 1)
    ax = 240 - abstand
    g = DECKUNG[name]
    if g:
        mapper, b = g
        gx = (240 + ax) // 2 - b // 2           # Gebaeude mittig auf der Linie
        sende([{"setzeGebaeude": {"spieler": 2, "x": gx, "y": y - b // 2, "mapper": mapper, "groesse": b}}], bis="SETZE GEBAEUDE")
    a = setze(1, 73, ax - 1, y - 1)
    t0, L = lage()
    treffer, vor, t = [], 12500, t0
    while t - t0 < ticks:
        time.sleep(0.05)
        t, L = lage()
        e = L.get(a)
        if e is None or e["besitzer"] != 1:
            treffer.append((t - t0, "tot"))
            break
        if e["leben"] < vor:
            treffer.append((t - t0, vor - e["leben"]))
            vor = e["leben"]
    sende([{"lagebild": True}], bis="LAGEBILD", warte=3.0)
    G = [r.split() for r in io.open(os.path.join(K.ABZUG, "gebaeude.txt"), encoding="utf-8").read().splitlines()[1:] if r.strip()]
    steht = [r for r in G if int(r[1]) == 2 and abs(int(r[4]) - (y - 1)) <= 6]
    return {"typ": typ, "deckung": name, "abstand": abstand, "gebaeude_steht": [r[2:5] for r in steht], "treffer": treffer, "leben_ende": vor}


def reihe_deckung(arg):
    namen = arg.get("gebaeude", ",".join(DECKUNG)).split(",")
    typ = int(arg.get("typ", 22))
    datei = os.path.join(D, "editor_deckung_%s.jsonl" % time.strftime("%Y%m%d_%H%M%S"))
    print("Ergebnis ->", os.path.abspath(datei), flush=True)
    for i, name in enumerate(namen):
        r = deckung(name, i, typ, int(arg.get("abstand", 14)), int(arg.get("ticks", 900)))
        io.open(datei, "a", encoding="utf-8").write(json.dumps(r) + chr(10))
        print("%s %-18s: Gebaeude %s, Treffer %d %s, Leben Ende %d" % (NAMEN.get(typ, typ), name, r["gebaeude_steht"],
              len([x for x in r["treffer"] if x[1] != "tot"]), r["treffer"][:3], r["leben_ende"]), flush=True)
    leeren()
    return datei


def auswerten(datei):
    zeilen = [json.loads(z) for z in io.open(datei, encoding="utf-8")]
    for typ in sorted({z["typ"] for z in zeilen}):
        rz = sorted((z for z in zeilen if z["typ"] == typ), key=lambda z: -z["abstand"])
        grenze = max((z["abstand"] for z in rz if z["erster_treffer"]), default=None)
        print("%s: groesster Abstand mit Schaden %s | %s" % (NAMEN.get(typ, typ), grenze, ", ".join(
            "D%d:%s" % (z["abstand"], "%.1f" % z["rate_je_tick"] if z["rate_je_tick"] is not None else "0") for z in rz)))


def main():
    was = sys.argv[1] if len(sys.argv) > 1 else "abstand"
    if was == "auswerten":
        auswerten(sys.argv[2])
        return
    arg = dict(a.split("=", 1) for a in sys.argv[2:] if "=" in a)
    if was == "abstand":
        auswerten(reihe_abstand(arg))
    elif was == "kette":
        reihe_kette(arg)
    elif was == "spaeher":
        reihe_spaeher(arg)
    elif was == "gebaeude":
        reihe_gebaeude(arg)
    elif was == "deckung":
        reihe_deckung(arg)


if __name__ == "__main__":
    main()
