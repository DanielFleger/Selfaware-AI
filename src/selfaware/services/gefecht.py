# -*- coding: utf-8 -*-
"""Gefechtsbewertung: lohnt sich ein Gegenangriff? (Daniel 19.10.2026, Partie 1019b: "die lassen sich einfach angreifen ohne
Grund und koennen noch nicht evaluieren, wann ein Counter sich lohnt - jede Sekunde Zoegerung bei so einer Entscheidung
kostet wertvolle Leben"; "die Staerkewerte je Einheit vorher im Editor messen").

Grundlage: Duelle im Karteneditor (editor_messen.py duell, data/research/editor_duell_*.jsonl) - je Paar Einheitenart X gegen Y:
Schaden je Takt, den X an Y macht, solange beide kaempfen (Nahkampf auf Beruehrung, Schuetzen schiessen aus Reichweite),
volles Leben je Art. Daraus SCHADEN[x][y] (beide Richtungen jedes Duells, Mittel ueber Wiederholungen).

simuliere(): Gefecht in Schritten von SCHRITT Takten - jede Einheit nimmt das naechste lebende Ziel der Gegenseite,
Nahkaempfer laufen hin (TEMPO Takte je Feld) und schlagen auf Beruehrung (<= 1 Feld), Schuetzen schiessen bis zu ihrer
Reichweite (sicht.REICHWEITE) und laufen sonst naeher; der Schaden einer Einheit geht ganz an ihr Ziel. Feindliche
Schuetzen, die nicht zur angreifenden Gruppe gehoeren, aber in Reichweite des Kampfplatzes stehen, schiessen mit (sie
laufen nicht). Ende: eine Seite tot oder BIS Takte.

bewerte(): Angriff lohnt, wenn die feindliche Gruppe faellt und von unserem eingesetzten Leben mindestens BEHALTEN bleibt.
Alles Weitere entscheidet der Waechter (waechter.py).
"""

from selfaware import workspace as _workspace
import glob
import io
import json
import math
import os

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(_workspace.DATA)
FERN_REICH = {22: 44, 23: 44, 70: 44, 74: 44, 72: 17, 76: 11}
SCHRITT = 10              # Takte je Simulationsschritt
TEMPO = 15.0              # Takte je Feld (L68: 16 fuer die meisten, Assassine 14,6 - L80)
BIS = 1500                # laengstens so viele Takte rechnen
BEHALTEN = 0.4            # Anteil unseres eingesetzten Lebens, der nach dem Sieg mindestens bleiben muss (Stellgroesse)
LORD = 55
LORD_LEBEN = 150000       # 1018o: "Lord 26 mit 149750 Leben" (voll; Mitschrift LORD EINDEUTIG)
LORD_PROBEN = 5           # Lord-Werte aus Partien erst ab so vielen Proben (lord_messen.py)
# Lauftempo, Takte je Feld (L80, Median aus 11 Mitschriften, 17.10.); fehlt eine Art, ist ihr Tempo unbekannt (None)
TEMPO_ART = {22: 11.5, 71: 12.0, 70: 12.2, 24: 13.5, 73: 14.6, 72: 15.0, 55: 19.0, 75: 19.5, 23: 21.0, 76: 21.5,
             25: 24.0}

_TABELLE = None


def raten(r):
    """19.10. (Auswertung der ersten Duell-Reihe): Schaden je Takt beider Richtungen aus der Zeitreihe eines Duells.
    - Wer nie getroffen hat, liefert KEINEN Wert (None): der Gegenbefehl an Spieler 2 wird quittiert, wirkt aber nicht - ein
      feindlicher Nahkaempfer, den unser Schuetze aus 3 Feldern beschiesst, bleibt stehen (sonst 0 statt seines Schadens).
    - Endet der Schaden binnen 30 Takten nach dem ersten Treffer (ein Pfeil toetet den Sklaven), zaehlt die Zeit ab
      Kampfbeginn (Zielen gehoert dazu) - sonst Teilen durch ~0 Takte (6.000 je Takt)."""
    reihe = r["reihe"]
    ende = reihe[-1][0]
    abst = [z[3] for z in reihe if z[3] is not None]
    # aus der Ferne = die beiden kamen sich nie naeher als beim Setzen (3 Felder); sonst Nahkampf
    aus = {"fern": bool(abst) and min(abst) >= 3}
    for name, i, voll in (("a_an_d", 2, r.get("leben_d")), ("d_an_a", 1, r.get("leben_a"))):
        erst = next((z[0] for z in reihe if voll and z[i] < voll), None)
        if erst is None:
            aus[name] = None
            continue
        verlust = voll - reihe[-1][i]
        dauer = ende - erst if ende - erst >= 30 else ende
        aus[name] = verlust / float(max(1, dauer))
    return aus


def tabelle(dateien=None):
    """(SCHADEN {x: {y: je Takt}}, LEBEN {x: voll}, FERN {x: {y: je Takt}}) aus allen Duell-Messungen. 19.10.: Schuetzen
    machen aus der Ferne mehr Schaden als im Nahkampf (Bogen gegen Speer ~24 statt ~10) - FERN haelt die Werte der
    Duelle, in denen sie aus 3 Feldern schossen, SCHADEN die aus dem Nahkampf (fuer Nahkaempfer nur SCHADEN)."""
    global _TABELLE
    if _TABELLE is not None and dateien is None:
        return _TABELLE
    dateien = dateien or sorted(glob.glob(os.path.join(D, "editor_duell_*.jsonl")))
    summen, leben, fsum = {}, {}, {}
    for f in dateien:
        for z in io.open(f, encoding="utf-8"):
            r = json.loads(z)
            a, d = r["a_typ"], r["d_typ"]
            if r.get("leben_a"):
                leben[a] = max(leben.get(a, 0), r["leben_a"])
            if r.get("leben_d"):
                leben[d] = max(leben.get(d, 0), r["leben_d"])
            rt = raten(r) if r.get("reihe") else {"a_an_d": r["schaden_a_an_d_je_takt"], "d_an_a": r["schaden_d_an_a_je_takt"]}
            for x, y, w in ((a, d, rt["a_an_d"]), (d, a, rt["d_an_a"])):
                if w is None:
                    continue
                ziel = fsum if (rt.get("fern") and x in FERN_REICH) else summen
                s = ziel.setdefault(x, {}).setdefault(y, [0.0, 0])
                s[0] += w
                s[1] += 1
    schaden = {x: {y: s / n for y, (s, n) in ys.items()} for x, ys in summen.items()}
    fern = {x: {y: s / n for y, (s, n) in ys.items()} for x, ys in fsum.items()}
    # 19.10. 18:15: der Lord fehlt in den Editor-Duellen - seine Werte kommen aus echten Partien (lord_messen.py,
    # data/research/lord_kampfwerte.json); vorher Ersatzwert 20 je Takt -> die Lordwache hielt 2 Assassinen fuer toedlich (1018o)
    lw = os.path.join(D, "lord_kampfwerte.json")
    if os.path.exists(lw):
        k = json.load(io.open(lw, encoding="utf-8"))
        for y, v in k.get("lord_an", {}).items():
            if v["proben"] >= LORD_PROBEN:
                schaden.setdefault(LORD, {})[int(y)] = v["je_takt"]
        for x, v in k.get("an_lord", {}).items():
            if v["proben"] >= LORD_PROBEN:
                schaden.setdefault(int(x), {})[LORD] = v["je_takt"]
        # 18:45: Arten ohne reine Probe aus gemischten Gruppen (kleinste Quadrate, lord_messen.gemischt)
        for x, v in k.get("an_lord_gemischt", {}).items():
            if LORD not in schaden.get(int(x), {}) and v["proben"] >= LORD_PROBEN and v["je_takt"] > 0:
                schaden.setdefault(int(x), {})[LORD] = v["je_takt"]
        leben.setdefault(LORD, LORD_LEBEN)
    _TABELLE = (schaden, leben, fern)
    return _TABELLE


def gemessen(x, y, d=1):
    """19.10.: ist der Schaden von Art x an Art y gemessen (Duell oder Partie) - oder nur Ersatz (Mittel/20)?"""
    tb = tabelle()
    if d > 1 and len(tb) > 2 and y in tb[2].get(x, {}):
        return True
    return y in tb[0].get(x, {})


def dps(x, y, schaden, fern=None, d=1):
    """Schaden je Takt von Art x an Art y; Schuetzen ueber 1 Feld aus der Fern-Tabelle (wenn gemessen); fehlt das Paar,
    Mittel von x ueber alle gemessenen Ziele, sonst 20."""
    if fern and d > 1 and fern.get(x):
        zeile = fern[x]
        return zeile[y] if y in zeile else sum(zeile.values()) / len(zeile)
    zeile = schaden.get(x)
    if not zeile:
        return 20.0
    if y in zeile:
        return zeile[y]
    return sum(zeile.values()) / len(zeile)


def simuliere(wir, sie, schaden=None, bis=BIS, rest_aus=None):
    """wir/sie: Listen von dict(typ, leben, x, y, steht=False). Gibt (wir_leben_rest, sie_leben_rest, takte, sieg) -
    sieg = True, wenn alle von "sie" tot sind und von "wir" noch jemand lebt."""
    fern = None
    if schaden is None:
        tb = tabelle()
        schaden, fern = tb[0], (tb[2] if len(tb) > 2 else None)
    seiten = [[dict(e) for e in wir], [dict(e) for e in sie]]
    for s in seiten:
        for e in s:
            e["x"], e["y"] = float(e["x"]), float(e["y"])
    t = 0
    while t < bis:
        lebend = [[e for e in s if e["leben"] > 0] for s in seiten]
        if not lebend[0] or not lebend[1]:
            break
        treffer = [{}, {}]
        for i in (0, 1):
            gegner = lebend[1 - i]
            for e in lebend[i]:
                z = min(gegner, key=lambda g: max(abs(g["x"] - e["x"]), abs(g["y"] - e["y"])))
                d = max(abs(z["x"] - e["x"]), abs(z["y"] - e["y"]))
                reich = FERN_REICH.get(e["typ"], 1)
                if d <= reich:
                    treffer[1 - i][id(z)] = treffer[1 - i].get(id(z), 0.0) + dps(e["typ"], z["typ"], schaden, fern, d) * SCHRITT
                elif not e.get("steht"):
                    schritt = min(d - reich, SCHRITT / TEMPO)
                    e["x"] += (z["x"] - e["x"]) / d * schritt
                    e["y"] += (z["y"] - e["y"]) / d * schritt
        for i in (0, 1):
            for e in lebend[i]:
                e["leben"] -= treffer[i].get(id(e), 0.0)
        t += SCHRITT
    rest = [sum(max(0.0, e["leben"]) for e in s) for s in seiten]
    if rest_aus is not None:                 # 19.10.: Rest je Einheit von "wir" (lebt der Lord?) - zuweisung.py
        rest_aus.extend(max(0.0, e["leben"]) for e in seiten[0])
    return rest[0], rest[1], t, rest[1] <= 0 and rest[0] > 0


def bewerte(wir, sie, schaden=None):
    """(lohnt, Text): Gegenangriff lohnt, wenn die Gruppe faellt und mindestens BEHALTEN unseres Lebens bleibt."""
    if not wir or not sie:
        return False, "keine Gegner" if wir else "keine Verteidiger"
    voll = sum(e["leben"] for e in wir)
    r_wir, r_sie, t, sieg = simuliere(wir, sie, schaden)
    anteil = r_wir / float(max(1, voll))
    lohnt = sieg and anteil >= BEHALTEN
    return lohnt, "%d eigene (%d Leben) gegen %d (%d Leben): %s nach %d Takten, uns bleiben %.0f %%" % (
        len(wir), voll, len(sie), sum(e["leben"] for e in sie), "Sieg" if sieg else "Niederlage" if r_wir <= 0 else "offen",
        t, 100 * anteil)
