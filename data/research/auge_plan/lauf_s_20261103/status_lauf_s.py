# -*- coding: utf-8 -*-
"""Schreibt den Status je Zeile in versuche_szenario.csv aus den Belegen von Lauf S. Nur Status: gemessen, gerechnet aus Regel, offen, mit kurzem Grund. Gezaehlt wird am Ende.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/status_lauf_s.py > data/research/auge_plan/lauf_s_20261103/status_lauf_s.txt
"""
import collections
import csv
import json
import os

HIER = os.path.dirname(os.path.abspath(__file__))
LISTE = os.path.join(HIER, "..", "versuche_szenario.csv")
TYP = {"UT_E_ARCHER": 22, "UT_E_XBOW": 23, "UT_E_SPEAR": 24, "UT_E_PIKE": 25, "UT_E_MACE": 26, "UT_E_SWORD": 27, "UT_E_KNIGHT": 28, "UT_E_LADDER": 29, "UT_E_ENGINEER": 30, "UT_TUNNELER": 5, "UT_E_MONK": 37, "UT_A_ARCHER": 70, "UT_A_SLAVE": 71, "UT_A_SLINGER": 72, "UT_A_ASSASSIN": 73, "UT_A_HARCHER": 74, "UT_A_SWORDSMAN": 75, "UT_A_FIRETHROWER": 76, "UT_LORD": 55,
       "UT_S_CATAPULT": 39, "UT_S_TREBUCHET": 40, "UT_S_MANGONEL": 41, "UT_S_BALLISTA": 61, "UT_S_FBALLISTA": 77, "UT_S_BATTERINGRAM": 59, "UT_S_TOWER": 58, "UT_S_SHIELD": 60}
GESCHOSS = {22: "pfeil", 70: "pfeil", 74: "pfeil", 23: "bolzen", 72: "stein", 76: "feuer"}


def zeilen(n):
    return json.load(open(os.path.join(HIER, n + ".regeln.json"), encoding="utf-8"))["zeilen"]


nah = {(z["schlaeger"], z["opfer"]): z["urteil"] for z in zeilen("nahkampf")}
ziel_beschuss = {z["ziel"]: z for z in zeilen("beschuss")}
belagerung = {(z["geraet"], z["ziel"]): z for z in zeilen("belagerung") if z["urteil"] != "falsches Gebaeude"}
nahbau = {(z["wer"], z["ziel"]): z for n in ("gebaeude_nah_erster", "gebaeude_nah") for z in zeilen(n) if z["urteil"] != "falsches Gebaeude"}
STEIN_REGEL = {39, 40, 41}
V5 = {"V5.001": "gemessen", "V5.002": "gerechnet aus Regel: laeuft in 1.000 gegen 1.000 durch diese Groesse", "V5.003": "gerechnet aus Regel: wie V5.002", "V5.004": "gemessen", "V5.005": "gerechnet aus Regel: wie V5.002", "V5.006": "gemessen", "V5.007": "gemessen", "V5.008": "gemessen mit 1.150 gegen 1.150: 132 Plaetze belegen Tiere"}
V7 = {"V7.001": "gemessen, Loeschen offen", "V7.002": "gemessen: Feuerwerfer zuendet, rund 230 Takte, Schaden nicht getrennt", "V7.003": "gemessen", "V7.004": "gemessen: Mordgrube 18.000 je Grube; Hunde kommen bei 8 Feinden, bei 3 nicht", "V7.005": "gesehen: eine Kuh, wenige Faelle", "V7.006": "gemessen: 275 Takte je Feld, Zuschuetten nur beim fremden Graben, rund 220 Takte", "V7.007": "Leiter gemessen, Turm gesehen", "V7.008": "gemessen: Eingang 66, 48 Takte je Feld, Ziel faellt, Gang wird Grube", "V7.009": "gemessen", "V7.010": "gemessen auf der Mauer", "V7.011": "gesehen: Zustand wechselt, Durchgang offen"}


def status(r):
    g, nr, wer, ziel = r["gruppe"], r["nr"], TYP.get(r["wer"]), r["ziel"]
    if g == "V1":
        return "teils gemessen: Leben, Tempo, bei Schuetzen Reichweite und Schusstakt, Steigen offen, Reaktion nur an 3 Arten"
    if g == "V2":
        u = nah.get((wer, TYP.get(ziel))) or nah.get((TYP.get(ziel), wer))
        return f"gemessen: {u}" if u else "offen"
    if g == "V3":
        if wer in (41, 61, 77):
            return "offen: Schaden der Geraete an Einheiten nicht einzeln gewertet"
        z = ziel_beschuss.get(TYP.get(ziel))
        if z is None:
            return "offen"
        art = GESCHOSS[wer]
        if art == "feuer":
            return "gemessen: Feuer"
        return "gemessen" if z["gesehen"].get(art) else "gerechnet aus Regel: dieses Geschoss gegen dieses Ziel nicht gesehen, Tabelle hielt sonst ueberall"
    if g == "V4":
        z = belagerung.get((wer, ziel))
        if z is not None and z["verluste"]:
            return f"gemessen: {z['urteil']}"
        if z is not None:
            return "gesetzt, kein Treffer in 3 Steinen" if z["steine"] else "gesetzt, kein Stein"
        return "gerechnet aus Regel: Wert je Stein, Leben aus der Tabelle" if wer in STEIN_REGEL else "offen"
    if g == "V4b":
        z = nahbau.get((wer, ziel))
        return f"gemessen: {z['urteil']}" if z is not None else "offen: Gebaeude nicht gesetzt oder nicht gefahren"
    if g == "V5":
        return V5[nr]
    if g == "V6":
        return "gemessen"
    if g == "V7":
        return V7[nr]
    return r["status"]


text = open(LISTE, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in text else "\n"
rd = list(csv.DictReader(text.splitlines(), delimiter=";"))
felder = [f for f in rd[0] if f is not None]  # ein Strichpunkt im Status haette eine Spalte zu viel gemacht (03.11.), der Status wird hier neu gerechnet
zahl = collections.defaultdict(collections.Counter)
aus = [";".join(felder)]
for r in rd:
    r["status"] = status(r)
    zahl[r["gruppe"]][r["status"].split(":")[0].split(",")[0]] += 1
    aus.append(";".join(r[f] for f in felder))
open(LISTE, "w", encoding="utf-8", newline="").write(nl.join(aus) + nl)
for g, c in zahl.items():
    print(g, sum(c.values()), dict(c))
