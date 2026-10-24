# -*- coding: utf-8 -*-
"""Gebiets-Ebene und Gebietswechsel gegen echte Laufwege (B-211, SRE 24.10.2026) - zweiter Teil des Laufwegbeweises.

Quelle: daten/torhaus_aufnahme_<zeit>.json (SAI-Sitzung, werkzeug/torhaus_aufnahme.py): 8 Einheiten als Spieler 2 in
Franz' Burg, 4 Speertraeger durchs Torhaus nach draussen, 4 Bogenschuetzen auf den Turm, Orte alle 2 Takte; dazu drei
Wegkarten der GANZEN Karte (speicher.wegkarte(): link, gebiet, gebaeude, hoehe, boden) zu drei Takten. Die Gebiets-Spalte
ist hier von der richtigen Adresse 0x01DF70D8 (anders als in den Wegkarten vom 06.-12.10., W33); speicher.wegkarte()
setzt gebiet auf 0, wo link 0 ist.

Totschlagtests (vorher festgelegt):
  P1 (W35) Die Gebietsnummern des Spiels sind genau die Zusammenhangsstuecke ueber die Weg-Bits: eigene Flutfuellung in
     der Reihenfolge des Spiels (Zeile fuer Zeile, Feld fuer Feld, Fluten entlang der gesetzten Bits) muss dieselbe
     Einteilung ergeben - jedes Spiel-Gebiet entspricht genau einem eigenen Stueck und umgekehrt. Widerlegt, wenn
     Felder mit link != 0 in verschiedene Spiel-Gebiete fallen, die bei mir zusammenhaengen, oder umgekehrt.
     ERGEBNIS 24.10. 22:20: in der rohen Form WIDERLEGT (Variante A: 64.454 Felder in Stuecken, die das Spiel trennt) -
     das Spiel schliesst vor dem Fluten alle Torhaeuser (updatePathLinkageTileMap(1), 0x00419960); mit der Naeherung
     "Bits ueber Hoehensprung > 16 nicht folgen" (B) 0 abweichende Felder, nur noch zu fein zerteilt (Saat-Maske fehlt).
  P2 Jeder Ein-Feld-Schritt der 8 Einheiten hat das Bit im Startfeld (wie W29) - ausser an Gebietswechseln.
  P3 Gebietswechsel (Start- und Zielfeld mit verschiedener Gebietsnummer != 0) passieren NUR an Treppen/Torhaus/Turm,
     also auf oder neben einem Gebaeudefeld; dort ist das Weg-Bit nicht gesetzt (die Weg-Ebene kennt keinen Schritt
     zwischen Gebieten - den kennen nur die Kletterdaten).
  P4 (offen, braucht PathFindingState roh, 0x012BB8C8): fuer jeden Gebietswechsel (a -> b) muss ein Kletter-Eintrag
     existieren, der a und b verbindet, und die Wegabfrage query(a, b) != 0 liefern. Ohne die Rohdaten wird P4 nur als
     Luecke gemeldet, nie als bestanden.

Aufruf: python werkzeug/engine_knowledge/torhaus_pruefen.py [daten/torhaus_aufnahme_<zeit>.json]
Schreibt daten/torhaus_pruefung_<zeit>.json und druckt die Tafel.
"""
import glob
import json
import os
import re
import sys
import time
from collections import Counter, deque

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
WERKZEUG = os.path.dirname(HIER)
sys.path.insert(0, WERKZEUG)
sys.path.insert(0, HIER)
import wegkarte as W  # noqa: E402
from laufweg_beweis import orte, schritte, BIT  # noqa: E402

D = os.path.join(WERKZEUG, "..", "daten")
G = 400


def flutfuellung(link, folgen=lambda px, py, nx, ny: True, saat=lambda x, y: True):
    """Eigene Gebietsnummern wie updateSeparateAreaTileMap (0x004995E0): Felder in Spielreihenfolge (y, dann x) durchgehen,
    jedes noch nummernlose Feld mit link != 0 (und saat(x, y)) bekommt die naechste Nummer und flutet entlang seiner
    gesetzten Bits weiter (gerichtet: nur wohin ein Bit zeigt; nur wenn folgen(...)). Gibt int32 [x, y].
    Das Spiel saet nur Felder ohne Sperrbits (LogicLayer & 0x4A5014B1 == 0) - die Logik-Ebene ist in der Aufnahme nicht
    dabei, darum Varianten (siehe p1)."""
    mein = np.zeros((G, G), np.int32)
    n = 0
    for y in range(G):
        for x in range(G):
            if link[x, y] == 0 or mein[x, y] or not saat(x, y):
                continue
            n += 1
            mein[x, y] = n
            q = deque([(x, y)])
            while q:
                px, py = q.popleft()
                b = int(link[px, py])
                for bit, (dx, dy) in W.RICHTUNG.items():
                    if b & bit:
                        nx, ny = px + dx, py + dy
                        if 0 <= nx < G and 0 <= ny < G and mein[nx, ny] == 0 and link[nx, ny] != 0 and folgen(px, py, nx, ny):
                            mein[nx, ny] = n
                            q.append((nx, ny))
    return mein


def vergleich(mein, link, geb):
    """Eigene Einteilung gegen die Spiel-Gebiete (nur Felder mit link != 0 und Spiel-Gebiet != 0).
    getrennt   = Felder in eigenen Stuecken, die das Spiel in mehrere Gebiete trennt (mein Stueck zu grob)
    zerteilt   = Felder in Spiel-Gebieten, die ich in mehrere Stuecke zerlege (mein Stueck zu fein)
    abweichend = Felder, deren Spiel-Gebiet nicht das Mehrheits-Gebiet ihres eigenen Stuecks ist (echter Widerspruch)."""
    m = (link != 0) & (geb != 0)
    paare = Counter(zip(mein[m].tolist(), geb[m].tolist()))
    m2s, s2m = {}, {}
    for (a, b), k in paare.items():
        m2s.setdefault(a, set()).add(b)
        s2m.setdefault(b, set()).add(a)
    best = {a: max(s, key=lambda b: paare[(a, b)]) for a, s in m2s.items()}
    return {"eigene_stuecke": int(mein.max()), "spiel_gebiete": len(s2m), "felder": int(m.sum()),
            "getrennt": int(sum(k for (a, b), k in paare.items() if len(m2s[a]) > 1)),
            "zerteilt": int(sum(k for (a, b), k in paare.items() if len(s2m[b]) > 1)),
            "abweichend": int(sum(k for (a, b), k in paare.items() if best[a] != b))}


def p1(z):
    """Vier Varianten der Flutfuellung gegen die Spiel-Gebiete. Erwartung nach dem Code: updateSeparateAreaTileMap ruft vor
    dem Fluten updatePathLinkageTileMap(1) (0x00419960: alle Torhaeuser 'zu', Kletter-Eintrag nicht erkannt) und danach
    (0) wieder auf - Torhaus-Durchgaenge verbinden also KEINE Gebiete. Da die Durchgangs-Bits in der danach gelesenen
    Weg-Ebene wieder drin sind, naehert Variante B sie ueber den Hoehensprung an (Boden 8 <-> Torhaus/Mauer 68-98)."""
    link, geb, bau, hoe = z["link"], z["gebiet"], z["gebaeude"], z["hoehe"].astype(int)
    immer = lambda *a: True
    kein_sprung = lambda px, py, nx, ny: abs(hoe[px, py] - hoe[nx, ny]) <= 16
    ohne_bau = lambda x, y: bau[x, y] == 0
    aus = {"spiel_gebiet_0_bei_weg": int(((link != 0) & (geb == 0)).sum())}
    for name, fo, sa in (("A roh (jede Saat, jedem Bit folgen)", immer, immer),
                         ("B Bits ueber Hoehensprung > 16 nicht folgen", kein_sprung, immer),
                         ("C wie B, Saat nur ohne Gebaeude", kein_sprung, ohne_bau),
                         ("D Saat nur ohne Gebaeude", immer, ohne_bau)):
        aus[name] = vergleich(flutfuellung(link, fo, sa), link, geb)
    return aus


# ---------------------------------------------------------------------------------------------------------------
# P4: Wegabfrage 0x004A5320 gegen die Gebietswechsel. Kletterdaten aus PathFindingState roh (speicher.lies(0x012BB8C8,
# 107428)): Anzahl bei +0, Eintrag i ab 4228 + i*516 (Felder wie navigation_capture.py / Ghidra ClimbData):
# +0 canBeUsed, +4 type (1 = Leiter), +12 buildingID, +24 isRecognizedByPathfinding, +52 area, +56 wallGroupAreaID,
# +484 ownerPlayerIndex, +488 buildingArea. Die Abfrage ist ein Nachbau von scripts/navigation_rule.rs (Codex, 20.000
# isolierte Vergleiche gegen den Originalcode ohne Abweichung) - hier in Python, nur Rueckgabewert, kein Hilfsfeld.
# Mannschaften (playerTeams) und "Gebaeude offen" (+0x2c6) sind nicht im Abzug: fuer Eintraege mit anderem Besitzer als
# dem Spieler wird "gleiche Mannschaft" als unbekannt gemeldet, nicht angenommen.
import struct


def kletterdaten(pfs):
    n = struct.unpack_from("<i", pfs, 0)[0]
    if not 0 <= n <= 200:
        raise ValueError("unerwartete Anzahl Kletter-Eintraege %d" % n)
    aus = []
    for i in range(1, n):
        o = 4228 + i * 516
        g = lambda j: struct.unpack_from("<i", pfs, o + j)[0]
        aus.append({"i": i, "canBeUsed": g(0), "type": g(4), "building": g(12), "recognized": g(24), "area": g(52),
                    "wall": g(56), "owner": g(484), "building_area": g(488)})
    return aus


def wegabfrage(eintraege, player, von, nach, climb=0, fremde_gelten=False):
    """Rueckgabe wie das Original: von, wenn gleich; 0, wenn eines 0; sonst das Gebiet, ueber das man 'nach' von 'von'
    aus erreicht (nach selbst oder ein Zwischengebiet), oder 0. fremde_gelten: Eintraege anderer Besitzer mitzaehlen
    (Mannschaftstabelle fehlt im Abzug)."""
    if von == nach:
        return von
    if von == 0 or nach == 0:
        return 0
    ok = []
    for r in eintraege:
        if r["canBeUsed"] != 1 or r["recognized"] == 0:
            continue
        if (r["type"] == 1 and climb == 0) or (r["type"] != 1 and climb == 2):
            continue
        if player == 0 or r["owner"] == player or fremde_gelten:
            ok.append(r)

    def nachbarn(r, bei):
        if r["area"] == bei:
            return r["wall"], r["building_area"], r["building_area"] > 0
        if r["wall"] == bei:
            return r["area"], r["building_area"], r["building_area"] > 0
        if r["building_area"] == bei:
            return r["area"], r["wall"], True
        return None

    queue, used, naechst = [], [False] * len(ok), 0
    for phase in (0, 1):
        for i, r in enumerate(ok):
            if phase == 0 and r["type"] == 1:
                continue
            t = nachbarn(r, nach)
            if t:
                a, b, mit_b = t
                if a == von or b == von:
                    return nach
                queue.append(a)
                if mit_b:
                    queue.append(b)
                used[i] = True
        while naechst < len(queue):
            bei = queue[naechst]
            naechst += 1
            for i, r in enumerate(ok):
                if used[i] or (phase == 0 and r["type"] == 1):
                    continue
                t = nachbarn(r, bei)
                if t:
                    a, b, mit_b = t
                    if a == von or b == von:
                        return bei
                    queue.append(a)
                    if mit_b:
                        queue.append(b)
                    used[i] = True
    return 0


def p4(pfad_pfs, wechsel, karte_pfs, player):
    pfs = open(pfad_pfs, "rb").read()
    if len(pfs) != 107428:
        raise ValueError("PathFindingState-Abzug hat %d Byte, erwartet 107428" % len(pfs))
    E = kletterdaten(pfs)
    aktiv = [r for r in E if r["canBeUsed"] == 1 and r["recognized"] != 0]
    aus = {"datei": os.path.basename(pfad_pfs), "eintraege": len(E), "aktiv": len(aktiv),
           "aktive_eintraege": aktiv, "wechsel": [], "negativ": {}}
    print("P4 - Kletter-Eintraege: %d, davon nutzbar und vom Wegfinder erkannt: %d" % (len(E), len(aktiv)))
    for r in aktiv:
        print("   Eintrag %3d Typ %d Gebaeude %4d Besitzer %d: Boden-Gebiet %3d  Mauer-Gebiet %3d  Gebaeude-Gebiet %3d" % (
            r["i"], r["type"], r["building"], r["owner"], r["area"], r["wall"], r["building_area"]))
    # Gebietsnummern des Wechsels auf die Wegkarte des Abzug-Takts umrechnen (W38: Nummern wechseln je Neuberechnung)
    geb = karte_pfs["gebiet"]
    gut = 0
    for w in wechsel:
        gv, gn = int(geb[tuple(w["von"])]), int(geb[tuple(w["nach"])])
        direkt = [r["i"] for r in aktiv if {gv, gn} <= {r["area"], r["wall"], r["building_area"]}]
        q = wegabfrage(aktiv, player, gv, gn)
        q_rueck = wegabfrage(aktiv, player, gn, gv)
        e = {"t": w["t"], "nr": w["nr"], "art": w["art"], "von": w["von"], "nach": w["nach"], "gebiet_zum_abzugstakt": [gv, gn],
             "gebiet_zur_laufzeit": w["gebiet"], "eintrag_direkt": direkt, "abfrage_hin": q, "abfrage_rueck": q_rueck}
        aus["wechsel"].append(e)
        if q:
            gut += 1
        print("   t %d %3d %-13s %s -> %s Gebiet %s (Lauf %s) Eintrag %s Abfrage hin %s rueck %s" % (
            w["t"], w["nr"], w["art"], tuple(w["von"]), tuple(w["nach"]), [gv, gn], w["gebiet"], direkt or "-", q, q_rueck))
    print("   Abfrage != 0 bei %d von %d Gebietswechseln" % (gut, len(wechsel)))
    echt = [e for e, w in zip(aus["wechsel"], wechsel) if w.get("aufenthalt_takte", 99) >= 10]
    kurz = [e for e, w in zip(aus["wechsel"], wechsel) if w.get("aufenthalt_takte", 99) < 10]
    aus["echte_uebergaenge"] = {"anzahl": len(echt), "mit_eintrag": sum(1 for e in echt if e["eintrag_direkt"]),
                                "abfrage_hin_und_rueck": sum(1 for e in echt if e["abfrage_hin"] and e["abfrage_rueck"])}
    aus["kurzkontakte"] = {"anzahl": len(kurz), "mit_eintrag": sum(1 for e in kurz if e["eintrag_direkt"]),
                           "abfrage_hin": sum(1 for e in kurz if e["abfrage_hin"])}
    print("   Echte Uebergaenge (>= 10 Takte): %s" % aus["echte_uebergaenge"])
    print("   Kurzkontakte (< 10 Takte):       %s" % aus["kurzkontakte"])
    # Negativlauf: Gebiete, zwischen denen keine Einheit wechselte und die kein Eintrag verbindet, muessen 0 liefern;
    # und ein ausgedachtes Gebiet (9999) ebenso.
    gebiete = sorted({int(g) for g in set(geb[geb != 0].tolist())})
    verbunden = set()
    for r in aktiv:
        trio = [g for g in (r["area"], r["wall"], r["building_area"]) if g > 0]
        for a in trio:
            for b in trio:
                verbunden.add((a, b))
    import random
    random.seed(24102026)
    paare = [(a, b) for a in gebiete for b in gebiete if a != b and (a, b) not in verbunden]
    probe = random.sample(paare, min(300, len(paare)))
    falsch_positiv = [(a, b, wegabfrage(aktiv, player, a, b)) for a, b in probe]
    falsch_positiv = [x for x in falsch_positiv if x[2]]
    aus["negativ"] = {"geprueft_paare": len(probe), "abfrage_trotzdem_nicht_0": falsch_positiv[:20], "anzahl": len(falsch_positiv),
                      "erfunden_9999": wegabfrage(aktiv, player, 9999, gebiete[0]) if gebiete else None,
                      "hinweis": "nicht 0 ist hier kein Fehler, wenn ein Zwischengebiet verbindet - die Liste zeigt, welche"}
    print("   Negativlauf: %d zufaellige Gebietspaare ohne direkten Eintrag, Abfrage != 0 bei %d (Mehrschritt-Wege moeglich): %s; erfundenes Gebiet 9999 -> %s" % (
        len(probe), len(falsch_positiv), falsch_positiv[:8], aus["negativ"]["erfunden_9999"]))
    return aus


def main():
    pfad = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(D, "torhaus_aufnahme_*.json")))[-1]
    d = json.load(open(pfad, encoding="utf-8"))
    zeit = d["zeit"]
    karten = {}
    for p in sorted(glob.glob(os.path.join(D, "torhaus_wegkarte_%s_*.npz" % zeit))):
        t = int(re.search(r"_(\d+)\.npz$", p).group(1))
        karten[t] = dict(np.load(p))
    takte = sorted(karten)
    aus = {"datei": os.path.basename(pfad), "wegkarten": takte, "p1": {}, "p2": {}, "p3": [], "p4": "offen - PathFindingState roh (0x012BB8C8) nicht in der Aufnahme"}
    print("P1 - Gebiets-Ebene gegen eigene Flutfuellung ueber die Weg-Bits:")
    for t in takte:
        aus["p1"][t] = p1(karten[t])
        print("  Takt %d: Felder mit Weg, aber Spiel-Gebiet 0: %d" % (t, aus["p1"][t]["spiel_gebiet_0_bei_weg"]))
        for name, v in aus["p1"][t].items():
            if isinstance(v, dict):
                print("     %-46s Stuecke %4d / Spiel %3d | getrennt %6d | zerteilt %5d | abweichend %5d" % (
                    name, v["eigene_stuecke"], v["spiel_gebiete"], v["getrennt"], v["zerteilt"], v["abweichend"]))
    # Aenderung der Ebenen zwischen den Takten
    for a, b in zip(takte, takte[1:]):
        print("  Felder mit geaendertem link %d -> %d: %d; gebiet: %d; gebaeude: %d" % (
            a, b, int((karten[a]["link"] != karten[b]["link"]).sum()), int((karten[a]["gebiet"] != karten[b]["gebiet"]).sum()),
            int((karten[a]["gebaeude"] != karten[b]["gebaeude"]).sum())))

    def karte_zu(t):
        passend = [k for k in takte if k <= t]
        return karten[passend[-1] if passend else takte[0]], (passend[-1] if passend else takte[0])

    namen = {int(k): v for k, v in d["arbeiter"].items()}
    typen = W.gebaeude_typen() if hasattr(W, "gebaeude_typen") else {}
    alle, wechsel, verst = 0, [], []
    je_einheit = {}
    for nr, reihe in orte(d["ew"]).items():
        n_schritt, n_verst, n_wechsel, spruenge = 0, 0, 0, 0
        S = schritte(reihe)
        for i, (t, von, nach) in enumerate(S):
            # Aufenthalt auf dem HOEHEREN der beiden Felder (Mauer/Torhaus/Turm): beim Hinauf die Zeit auf dem Zielfeld bis
            # zum naechsten Ortswechsel, beim Herunter die Zeit, die die Einheit vorher auf dem Startfeld stand.
            dauer_nach = (S[i + 1][0] if i + 1 < len(S) else reihe[-1][0]) - t
            dauer_von = t - (S[i - 1][0] if i else reihe[0][0])
            aufenthalt = (dauer_nach, dauer_von)
            dx, dy = nach[0] - von[0], nach[1] - von[1]
            if max(abs(dx), abs(dy)) != 1:
                spruenge += 1
                continue
            z, zt = karte_zu(t)
            lv, ln = int(z["link"][von]), int(z["link"][nach])
            gv, gn = int(z["gebiet"][von]), int(z["gebiet"][nach])
            bv, bn = int(z["gebaeude"][von]), int(z["gebaeude"][nach])
            hv, hn = int(z["hoehe"][von]), int(z["hoehe"][nach])
            alle += 1
            n_schritt += 1
            erlaubt = bool(lv & BIT[(dx, dy)])
            if gv and gn and gv != gn:
                n_wechsel += 1
                nachbar_geb = sorted({int(z["gebaeude"][von[0] + i, von[1] + j]) for i in (-1, 0, 1) for j in (-1, 0, 1)} |
                                     {int(z["gebaeude"][nach[0] + i, nach[1] + j]) for i in (-1, 0, 1) for j in (-1, 0, 1)})
                wechsel.append({"t": t, "nr": nr, "art": namen.get(nr, "?"), "von": list(von), "nach": list(nach), "gebiet": [gv, gn],
                                "hoehe": [hv, hn], "gebaeude": [bv, bn], "gebaeude_umkreis1": [g for g in nachbar_geb if g],
                                "bit_gesetzt": erlaubt, "wegkarte_takt": zt,
                                "aufenthalt_takte": aufenthalt[0] if hn >= hv else aufenthalt[1]})
            elif not erlaubt:
                n_verst += 1
                verst.append({"t": t, "nr": nr, "art": namen.get(nr, "?"), "von": list(von), "nach": list(nach), "link_von": "%02x" % lv,
                              "gebiet": [gv, gn], "hoehe": [hv, hn], "gebaeude": [bv, bn], "wegkarte_takt": zt})
        je_einheit[nr] = {"art": namen.get(nr, "?"), "schritte": n_schritt, "spruenge": spruenge, "verstoesse": n_verst, "gebietswechsel": n_wechsel}
    aus["p2"] = {"schritte": alle, "verstoesse_ohne_gebietswechsel": len(verst), "je_einheit": je_einheit, "verstoesse": verst}
    aus["p3"] = wechsel
    print("P2 - Schritte der 8 Einheiten: %d, Verstoesse gegen das Weg-Bit ausserhalb von Gebietswechseln: %d" % (alle, len(verst)))
    for nr, e in sorted(je_einheit.items()):
        print("   %3d %-14s Schritte %3d  Spruenge %d  Verstoesse %d  Gebietswechsel %d" % (nr, e["art"], e["schritte"], e["spruenge"], e["verstoesse"], e["gebietswechsel"]))
    for v in verst[:20]:
        print("   Verstoss", v)
    print("P3 - Gebietswechsel: %d" % len(wechsel))
    for w in wechsel:
        print("   t %d %3d %-14s %s -> %s Gebiet %s Hoehe %s Gebaeude %s Umkreis %s Bit %s Aufenthalt %d Takte" % (
            w["t"], w["nr"], w["art"], tuple(w["von"]), tuple(w["nach"]), w["gebiet"], w["hoehe"], w["gebaeude"], w["gebaeude_umkreis1"], w["bit_gesetzt"], w["aufenthalt_takte"]))
    print("   Gebietspaare:", Counter(tuple(w["gebiet"]) for w in wechsel).most_common())
    print("   Bit gesetzt bei Gebietswechsel:", Counter(w["bit_gesetzt"] for w in wechsel))
    print("   Wechsel ohne Gebaeude im Umkreis 1:", sum(1 for w in wechsel if not w["gebaeude_umkreis1"]))
    # Echter Uebergang oder Kurzkontakt? Ein Schritt dauert >= 10 Takte (L1, hier gemessen 8-18); wer das hoehere Feld
    # (Mauer/Torhaus/Turm) nach < 10 Takten wieder verlaesst, hat es nur gestreift (Feinposition am Mauereck - vermutet).
    echt = [w for w in wechsel if w["aufenthalt_takte"] >= 10]
    kurz = [w for w in wechsel if w["aufenthalt_takte"] < 10]
    print("   Echte Uebergaenge (Aufenthalt >= 10 Takte): %d  %s" % (len(echt), Counter(tuple(w["gebiet"]) for w in echt).most_common()))
    print("   Kurzkontakte (< 10 Takte): %d  %s  Aufenthalte %s" % (len(kurz), Counter(tuple(w["gebiet"]) for w in kurz).most_common(),
                                                                     sorted(Counter(w["aufenthalt_takte"] for w in kurz).items())))
    aus["p3_echt"] = len(echt)
    aus["p3_kurz"] = len(kurz)
    pfs_dateien = sorted(glob.glob(os.path.join(D, "torhaus_pfs_%s_*.npz" % zeit)) + glob.glob(os.path.join(D, "torhaus_pfs_%s_*.bin" % zeit)))
    if pfs_dateien:
        tp = int(re.search(r"_(\d+)\.bin$", pfs_dateien[-1]).group(1))
        if tp in karten:
            aus["p4"] = p4(pfs_dateien[-1], wechsel, karten[tp], d.get("spieler", 0))
            aus["p4"]["abzug_takt"] = tp
        else:
            print("P4 - Abzug-Takt %d hat keine Wegkarte, nicht geprueft" % tp)
    else:
        print("P4 -", aus["p4"])
    ziel = os.path.join(D, "torhaus_pruefung_%s.json" % zeit)
    json.dump(aus, open(ziel, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
    print("Beleg:", ziel)


if __name__ == "__main__":
    main()
