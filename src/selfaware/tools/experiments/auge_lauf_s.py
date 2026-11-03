# -*- coding: utf-8 -*-
"""B-142 Lauf S: wenige Szenen im Karteneditor, das Auge zeichnet auf, der Regel-Pruefer wertet aus. Plan: docs/plans/Plan_Lauf_S.md.

  python -m selfaware.tools.experiments.auge_lauf_s los --instanz 2 --szenen nahkampf --daniel-ja
  python -m selfaware.tools.experiments.auge_lauf_s los --instanz 2 --szenen laufen_g nahkampf_g beschuss_g lord_g --daniel-ja

Szenen mit _g laufen im Gefecht statt im Karteneditor: zwei Mensch-Plaetze ohne KI, die Lords bleiben stehen. Beides zugleich geht nicht.

Jede Szene: anhalten, setzen, weiter, bis fertig oder Grenze, anhalten, abraeumen. Grenzen in Takten, die Uhr nur gegen Haengen.
Scheitert eine Szene, wird erklaert und nur sie neu gefahren. Setzen und Abraeumen gibt es nur in diesem Messlauf, nichts davon geht in SamurAI.
Bausteine aus Lauf F und K: Kanal, Speicher, Rekorder, Anhalten, Sperre.
"""
import argparse
import itertools
import json
import os
import shutil
import struct
import sys
import time
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments import auge_lauf_k as lk
from selfaware.tools.experiments.auge_lauf_f import Abbruch, Fehler

KARTE = "Liga_Grumpy Neighbors"
SOLDATEN = (22, 23, 24, 25, 26, 27, 28, 29, 30, 5, 37, 70, 71, 72, 73, 74, 75, 76, 55)  # die 19 Arten aus versuche_szenario.csv, V2
LAUFENDE_GERAETE = (39, 77, 60, 59, 58)  # Katapult, Feuerballiste, Schild, Ramme, Turm; Trebuchet, Mangonel, Ballista: DAT_UNIT_MOVABLE 0
FUSS_SCHUETZEN = (22, 23, 70, 72, 74, 76)
HAUPTMENUE, SZENARIEN, EIGENSCHAFTEN, LANDSCHAFT = 41, 44, 17, 12  # Ansichten laut Handbuch, Testen im Karteneditor
START_HAUFEN = ((165, 107), (251, 127), (141, 265), (227, 285))  # Mitten der 4 Gebaeudehaufen der Karte (zellen_je_art.txt); daran erkennt das Programm die richtige Karte
ANZAHL, MARKIERT, SCROLL = 0x0112661C, 0x01126624, 0x01126628  # Ladedialog, wie selfaware.game.ucp.laden
SPIELER_S = (1, 2)
E_UID, E_MX, E_MY, E_LEBEN = 0x98, 0xB6, 0xB8, 0x3C8  # gegen die Feldkarte geprueft 03.11.
ABRAEUMEN_GRENZE = 1000  # Takte; das alte Werkzeug wartete 400 (Steintod), gemessen wird das in der ersten Szene
SETZEN_FRIST = 20.0  # s, Kanal; das Spiel steht dabei
MASSE_FRIST = 60.0  # s, Kanal; 381 Einheiten brauchten 1,33 s
PLATZ_FUER_MASSE = 1150  # je Seite: 2.498 Plaetze (spawnUnit) minus 132 Tiere der Karte, die toeteAlle nicht nimmt, also keine 1.200 je Seite wie in der Liste
GRENZE_SCHLACHT = 10000  # Takte; laengste Toetung laut Tabelle 8.000 (Sklave gegen Pikenier). Kein Ende ist ein Ergebnis
RUHE_SCHLACHT = 2000  # Takte ohne einen Toten: Die Reste stehen zu weit auseinander, sie suchen sich ohne Befehl keinen Gegner
NAHKAEMPFER = (24, 25, 26, 27, 28, 71, 73, 75)
EUROPAEER, ARABER = (22, 23, 24, 25, 26, 27, 28), (70, 71, 72, 73, 74, 75, 76)
LAST_STUFEN = ((1000, 1000, 11), (500, 1000, 3), (200, 400, 3), (100, 200, 3), (40, 80, 3))  # Plan: Stufe 1 und 10 und die leere Karte sind leichter, Begruendung dort
MELEE = 0x00B4EE60  # DAT_MELEE_DAMAGE, 80 x 80 Ints, Tabellen.txt
OHNE_LORD = tuple(t for t in SOLDATEN if t != 55)  # im Gefecht: Faellt ein gesetzter Lord, entscheidet vielleicht die Niederlage-Pruefung (P313), das klaert die Szene lord_g
GESETZT = OHNE_LORD + LAUFENDE_GERAETE + (40, 41, 61)  # Trebuchet, Mangonel, Ballista; das raeumt das Abraeumen im Gefecht weg, Bauern und Lords nicht
GEFECHT_ABSTAND = 60  # Felder zu allem, was schon steht: Lords stoeren nicht, ihr Radius ist 25 (aggressiv), Bauern laufen nicht weit
GRENZE_NAH_G = 120  # Takte: Im Editor kam jeder erste Treffer nach 1 oder 2 Takten, und jeder Takt traf
LORD_GRENZE = 2000  # Takte; 150.000 Leben, 8 Ritter schlagen zusammen rund 800 je Takt, dazu der Laufweg
STARTPLAETZE = (0, 1, 246, 246, 246, 246, 246, 246)  # playerPositionsArray: Platz je Spieler, 246 = keiner
NACH_LORD = 300  # Takte: Wann das Spiel das Ende merkt, ist hier die Frage, die Pruefrunde des Lords liegt bei 64 Takten
STUECK = 100  # Befehle je Sendung
GRENZE_NAH = 251 + 256  # groesster erster Treffer vom 18.10. plus groesste Pruefrunde (Maske 255), alte_schuesse.txt
GRENZE_SCHUSS = 411 + 2 * 228  # groesster erster Treffer plus 2 Schuesse Armbrust, Handbuch 17.10.
FELDER_LAUF = 20  # 20 Felder: Anlauf hoechstens 12 Takte (calculateUnitMovementSpeed), Ablesefehler rund 2 Takte auf mindestens 230
GRENZE_LAUF = FELDER_LAUF * 36 * 2  # Tempo-Wert 3 (Schwertkaempfer), rund 12 Takte je Feld je Stufe (L80), Annahme; mal 2. Geraete fahren erst bemannt, das braucht eine eigene Szene


class SpeicherS(lk.SpeicherK):
    def __init__(self, quelle, karte):
        super().__init__(quelle)
        self.karte = karte
        self.fern = 0

    def einheiten_alle(self):
        """Alle belegten Plaetze ab Platz 1: Platz 0 ist ein Merkplatz (Lauf K)."""
        roh = self.q.lies(lf.EINHEITEN, lk.ALLE_PLAETZE * lf.E_SCHRITT)
        aus = []
        for i in range(1, lk.ALLE_PLAETZE):
            b = i * lf.E_SCHRITT
            if struct.unpack_from("<h", roh, b + lf.E_DA)[0]:
                h = lambda o: struct.unpack_from("<h", roh, b + o)[0]  # noqa: E731
                aus.append({"nr": i, "typ": h(lf.E_TYP), "besitzer": h(lf.E_BESITZER), "x": h(E_MX) // 8, "y": h(E_MY) // 8,
                            "leben": struct.unpack_from("<i", roh, b + E_LEBEN)[0], "uid": struct.unpack_from("<i", roh, b + E_UID)[0]})
        return aus

    def raster(self):
        """Die Karte, wie sie gerade ist: frei und Hoehe je Feld (y, x). Frei heisst: Logik wie die grosse Flaeche, nichts darauf. Was die Logik-Bits sonst heissen, ist hier nicht entschieden."""
        schicht = lambda n, t: np.frombuffer(self.q.lies(self.karte.adresse("DAT_TileMapState", n)[0], lf.KACHELN * np.dtype(t).itemsize), dtype=t)  # noqa: E731
        lo, ho, og, ge, ei = schicht("LogicLayer", "<u4"), schicht("HeightLayer", "u1"), schicht("OrganismLayer", "<u2"), schicht("BuildingLayer", "<u2"), schicht("UnitLayer", "<u2")
        zeilen = np.frombuffer(self.q.lies(lf.ZEILEN, 400 * 12), dtype="<i4").reshape(400, 3)[:, 2]
        maske = np.frombuffer(self.q.lies(lf.KARTENMASKE, 400 * 400), dtype="u1").reshape(400, 400) != 0
        kachel = zeilen[:, None] + np.arange(400)
        gueltig = maske & (kachel >= 0) & (kachel < lf.KACHELN)
        kachel = np.where(gueltig, kachel, 0)
        werte, zahl = np.unique(lo[kachel[gueltig]], return_counts=True)
        haeufig = werte[zahl.argmax()]
        frei = gueltig & (lo[kachel] == haeufig) & (og[kachel] == 0) & (ge[kachel] == 0) & (ei[kachel] == 0)
        if self.fern:
            frei = fern_maske(frei, self.einheiten_alle(), self.fern)
        return frei, ho[kachel].astype(np.int32), ge[kachel]


def fern_maske(frei, einheiten, abstand):
    """Nur Felder mit Abstand zu allem, was einem Spieler gehoert. Tiere gehoeren keinem (besitzer 0), sie liessen die Szenen im Editor unberuehrt."""
    aus = frei.copy()
    for e in einheiten:
        if 1 <= e["besitzer"] <= 8:
            aus[max(0, e["y"] - abstand):e["y"] + abstand + 1, max(0, e["x"] - abstand):e["x"] + abstand + 1] = False
    return aus


def gitter(frei, hoehe, breite, hoch, dx, dy, n, flach=False):
    """Bis zu n Ecken (x, y) im Raster dx, dy, an denen das Rechteck breite x hoch ganz frei ist. flach: Hoehenspanne hoechstens 4, sonst misst das Tempo den Hang mit."""
    summe = np.zeros((frei.shape[0] + 1, frei.shape[1] + 1), dtype=np.int64)
    summe[1:, 1:] = frei.cumsum(0).cumsum(1)
    aus = []
    for y in range(0, frei.shape[0] - hoch, dy):
        for x in range(0, frei.shape[1] - breite, dx):
            if summe[y + hoch, x + breite] - summe[y, x + breite] - summe[y + hoch, x] + summe[y, x] < breite * hoch:
                continue
            if flach:
                t = hoehe[y:y + hoch, x:x + breite]
                if t.max() - t.min() > 4:
                    continue
            aus.append((x, y))
            if len(aus) == n:
                return aus
    return aus


def kontrollort(frei, belegt, abstand=60):
    """Ein freies Feld mit Abstand zu allem in dieser Szene. None, wenn keins da ist."""
    ys, xs = np.nonzero(frei)
    pos = np.array(belegt)
    for x, y in zip(xs[::7], ys[::7]):
        if (np.maximum(np.abs(pos[:, 0] - x), np.abs(pos[:, 1] - y)) >= abstand).all():
            return int(x), int(y)
    return None


def setzen_masse(l, einheiten):
    """Mehrere Einheiten je Feld, darum ohne Zuordnung je Einheit: Hier zaehlt nur die Zahl. Das Spiel steht."""
    vorher = {(e["nr"], e["uid"]) for e in l.s.einheiten_alle()}
    bef = [{"setzeEinheit": {"spieler": e["spieler"], "typ": e["typ"], "x": e["x"] - 1, "y": e["y"] - 1, "anzahl": e["anzahl"]}} for e in einheiten]
    for i in range(0, len(bef), STUECK):
        l.k.liste(bef[i:i + STUECK], lf.KANAL)
    soll, neu = sum(e["anzahl"] for e in einheiten), 0
    ende = l.uhr() + MASSE_FRIST
    while l.uhr() < ende and neu < soll:
        neu = sum(1 for e in l.s.einheiten_alle() if (e["nr"], e["uid"]) not in vorher)
        l.ruhe(0.5)
    if neu < soll:
        raise Abbruch(f"Nur {neu} von {soll} Einheiten stehen")


def setzen(l, einheiten):
    """Setzt und liest zurueck. Das Spiel steht. Eine Einheit steht 1 Feld weiter als angegeben (gemessen 17.10.). Fehlt am Ende eine, stimmt die Szene nicht."""
    vorher = {(e["nr"], e["uid"]) for e in l.s.einheiten_alle()}
    bef = [{"setzeEinheit": {"spieler": e["spieler"], "typ": e["typ"], "x": e["x"] - 1, "y": e["y"] - 1, "anzahl": 1}} for e in einheiten]
    for i in range(0, len(bef), STUECK):
        l.k.liste(bef[i:i + STUECK], lf.KANAL)
    neu = []
    ende = l.uhr() + SETZEN_FRIST
    while l.uhr() < ende:
        neu = [e for e in l.s.einheiten_alle() if (e["nr"], e["uid"]) not in vorher]
        if len(neu) >= len(einheiten):
            break
        l.ruhe(0.2)
    frei = {(e["besitzer"], e["typ"], e["x"], e["y"]): e for e in neu}
    fehlt = 0
    for e in einheiten:
        g = frei.pop((e["spieler"], e["typ"], e["x"], e["y"]), None)
        if g is None:
            fehlt += 1
        else:
            e.update(nr=g["nr"], uid=g["uid"], voll=g["leben"])
    if fehlt:
        raise Abbruch(f"{fehlt} von {len(einheiten)} Einheiten stehen nicht, wo sie sollen, neu sind {len(neu)}")


# --- Die Szenen. Beziehung: Jede Einheit gehoert ueber Nummer und uid zu genau einem Paar, jedes Paar nennt seine Einheiten. ---
def mit_kontrolle(einheiten, frei, typ=24):
    o = kontrollort(frei, [(e["x"], e["y"]) for e in einheiten])
    if o is None:
        raise Abbruch("Kein Platz fuer die Kontrolle")
    einheiten.append({"rolle": "kontrolle", "spieler": 1, "typ": typ, "x": o[0], "y": o[1]})
    return einheiten


def aufbau_nahkampf(l, arten=SOLDATEN):
    """Alle 190 ungeordneten Paare der 19 Arten, je Paar Abstand 1: Der naechste Feind ist der Partner, weil die Paare 6 Felder auseinander stehen. Kein Befehl: Nahkampf beginnt im Umkreis von 2 Feldern von selbst (P346)."""
    frei, hoehe, _ = l.s.raster()
    paare = list(itertools.combinations_with_replacement(arten, 2))
    orte = gitter(frei, hoehe, 2, 1, 6, 6, len(paare))
    if len(orte) < len(paare):
        raise Abbruch(f"Nur {len(orte)} Plaetze fuer {len(paare)} Paare")
    aus = []
    for i, ((a, b), (x, y)) in enumerate(zip(paare, orte)):
        aus += [{"rolle": "a", "paar": i, "spieler": 1, "typ": a, "x": x, "y": y}, {"rolle": "b", "paar": i, "spieler": 2, "typ": b, "x": x + 1, "y": y}]
    return {"einheiten": mit_kontrolle(aus, frei)}


def aufbau_beschuss(l, arten=SOLDATEN):
    """Jeder Fussschuetze gegen jede der 19 Arten, Abstand 8: Der Schaden ist von 4 bis 20 Feldern gleich (Handbuch 17.10.), der Feuerwerfer reicht bis 10. Raster 20 x 12: Der naechste Feind ist das eigene Ziel. Kein Befehl: Schuetzen waehlen ihr Ziel selbst."""
    frei, hoehe, _ = l.s.raster()
    paare = list(itertools.product(FUSS_SCHUETZEN, arten))
    orte = gitter(frei, hoehe, 9, 1, 20, 12, len(paare))
    if len(orte) < len(paare):
        raise Abbruch(f"Nur {len(orte)} Plaetze fuer {len(paare)} Paare")
    aus = []
    for i, ((a, b), (x, y)) in enumerate(zip(paare, orte)):
        aus += [{"rolle": "a", "paar": i, "spieler": 1, "typ": a, "x": x, "y": y}, {"rolle": "b", "paar": i, "spieler": 2, "typ": b, "x": x + 8, "y": y}]
    return {"einheiten": mit_kontrolle(aus, frei)}


def aufbau_laufen(l, arten=SOLDATEN):
    """Alle Soldaten nebeneinander, ein Besitzer: Es gibt keinen Feind, also stoert nichts. Einmal gerade, einmal schraeg. Eben, sonst misst das Tempo den Hang mit."""
    frei, hoehe, _ = l.s.raster()
    n = len(arten)
    g = gitter(frei, hoehe, FELDER_LAUF + 3, n + 2, 4, 4, 1, flach=True)
    s = gitter(frei, hoehe, FELDER_LAUF + n + 2, FELDER_LAUF + n + 2, 4, 4, 1, flach=True)
    if not g or not s:
        raise Abbruch("Keine ebene Flaeche fuer die Laufbahnen")
    aus = []
    for i, t in enumerate(arten):
        aus.append({"rolle": "gerade", "spieler": 1, "typ": t, "x": g[0][0], "y": g[0][1] + i, "ziel": (g[0][0] + FELDER_LAUF, g[0][1] + i)})
        aus.append({"rolle": "schraeg", "spieler": 1, "typ": t, "x": s[0][0] + i, "y": s[0][1] + n - i, "ziel": (s[0][0] + i + FELDER_LAUF, s[0][1] + n - i + FELDER_LAUF)})
    return {"einheiten": aus}


def befehle_laufen(plan):
    return [{"einheit_ziel": {"nr": e["nr"], "x": e["ziel"][0], "y": e["ziel"][1]}} for e in plan["einheiten"]]


def alle_am_ziel(l, plan):
    orte = {e["nr"]: (e["x"], e["y"]) for e in l.s.einheiten_alle()}
    return all(orte.get(e["nr"]) == tuple(e["ziel"]) for e in plan["einheiten"])


@dataclass
class Szene:
    name: str
    tempo: int
    streng: bool
    grenze: int
    aufbau: Callable
    befehle: Optional[Callable] = None
    fertig: Optional[Callable] = None
    treffer_noetig: bool = True
    masse: bool = False


def aufbau_schlacht(a, b, n, je_feld=4):
    """Beide Seiten im Schachbrett: Jeder hat von Anfang an einen Feind neben sich, Nahkampf beginnt dort in 1 oder 2 Takten ohne Befehl (Szene Nahkampf). So aendern sich alle Einheiten in jedem Takt, das ist die schwerste Lage fuers Lesen."""
    def aufbau(l):
        frei, hoehe, _ = l.s.raster()
        seite = int(np.ceil(np.sqrt(2 * n / je_feld)))
        ecke = gitter(frei, hoehe, seite + 1, seite + 1, 4, 4, 1)
        if not ecke:
            raise Abbruch(f"Keine freie Flaeche {seite} x {seite}")
        aus, zahl = [], {1: 0, 2: 0}
        for j in range(seite):
            for i in range(seite):
                sp = 1 if (i + j) % 2 == 0 else 2
                arten = a if sp == 1 else b
                rest = n - zahl[sp]
                if rest <= 0:
                    continue
                k = min(je_feld, rest)
                aus.append({"rolle": "masse", "spieler": sp, "typ": arten[(i + j // 2) % len(arten)], "x": ecke[0][0] + i, "y": ecke[0][1] + j, "anzahl": k})
                zahl[sp] += k
        return {"einheiten": aus}
    return aufbau


def schlacht_zu_ende():
    """Eine Seite ist weg, oder RUHE_SCHLACHT Takte lang ist niemand gefallen. Nachgesehen wird alle 200 Takte: Jedes Nachsehen liest alle Plaetze."""
    z = {"takt": None, "zahl": None, "ruhe_ab": None}

    def fertig(l, plan):
        t = l.s.takt()
        if z["takt"] is not None and t - z["takt"] < 200:
            return False
        z["takt"] = t
        e = l.s.einheiten_alle()
        je = {p: sum(1 for x in e if x["besitzer"] == p) for p in SPIELER_S}
        if min(je.values()) == 0:
            return True
        n = sum(je.values())
        if n != z["zahl"]:
            z["zahl"], z["ruhe_ab"] = n, t
        return t - z["ruhe_ab"] >= RUHE_SCHLACHT
    return fertig


def szene_last(l):
    """Daniels Vorgabe unter Last: 2.300 Einheiten im Nahkampf, im Wechsel ohne und mit Lesen. Der Schaden Pikenier gegen Pikenier steht fuer diese Szene auf 1, so bleibt die Last fast gleich: Gemessen fielen 42 von 2.300 in 16.328 Takten (80.000 Leben, bis zu 12 Angreifer). Es verliert nur rund jeder Vierte je Takt Leben, weil alle auf einem Feld dasselbe Ziel nehmen. Danach kommt der alte Wert zurueck."""
    from selfaware.tools.analysis.auge_auswertung import a4_wechselprobe

    k, s = l.k, l.s
    lk.anhalten(l)
    plan = aufbau_schlacht((25,), (25,), PLATZ_FUER_MASSE)(l)
    setzen_masse(l, plan["einheiten"])
    adr = MELEE + (25 * 80 + 25) * 4
    alt = k.peek(adr)[0]
    k.liste([{"poke": adr, "wert": 1}], lf.KANAL)
    a = lk.aufnahme_im_stand(l, "last", 1000, False)
    l.warte_takte(100)  # bis alle kaempfen
    wechsel, zahlen = {}, {}
    try:
        for stufe, takte, phasen in LAST_STUFEN:
            k.befehl({"tempo": stufe}, lf.KANAL)
            l.tempo = stufe
            l.puls_neu()
            ohne, mit, sek = [], [], 0.0
            for i in range(phasen):
                l.rek.aussetzen(i % 2 == 0)
                m = l.messe(takte)
                (mit if i % 2 else ohne).append(m["rate"])
                sek = m["sekunden"]
            l.rek.aussetzen(False)
            zahlen[stufe] = len(s.einheiten_alle())
            wechsel[stufe] = {"ohne": ohne, "mit": mit, "sekunden": sek}
            l.schreib({"stufe": stufe, "ohne": [round(x, 1) for x in ohne], "mit": [round(x, 1) for x in mit], "einheiten": zahlen[stufe]})
    finally:
        k.liste([{"poke": adr, "wert": alt}], lf.KANAL)
    if k.peek(adr)[0] != alt:
        raise Abbruch("Der Tabellenwert ist nicht zurueck")
    b = lk.anhalten(l)
    pfad = l.rek.pfad
    stand = l.rek.beenden()
    e = a4_wechselprobe(wechsel)
    with open(pfad + ".plan.json", "w", encoding="utf-8") as f:
        json.dump({"szene": "last", "von": a, "bis": b, "tempo": 1000, "einheiten": plan["einheiten"], "wechsel": {str(t): v for t, v in wechsel.items()}, "zahlen": {str(t): v for t, v in zahlen.items()}, "ergebnis": e.status, "text": e.text}, f, ensure_ascii=False)
    abr = abraeumen(l)
    return {"szene": "last", "von": a, "bis": b, "ergebnis": e.status, "text": e.text, "einheiten": zahlen, "abraeumen_takte": abr, "stand": stand, "pfad": pfad}


def naechste_felder(frei, x, y, n):
    ys, xs = np.nonzero(frei)
    o = np.argsort(np.maximum(np.abs(xs - x), np.abs(ys - y)), kind="stable")[:n]
    return [(int(xs[i]), int(ys[i])) for i in o]


def szene_lord(l):
    """P313, P362, P306: 8 Ritter von Spieler 1 greifen den Lord von Spieler 2 an. Danach ist das Gefecht vorbei, darum kommt diese Szene zuletzt. Fertig ist sie, wenn das Spiel das Ende gemerkt hat oder NACH_LORD Takte um sind."""
    k, s = l.k, l.s
    lk.anhalten(l)
    lord = next((e for e in s.einheiten_alle() if e["typ"] == 55 and e["besitzer"] == 2), None)
    if lord is None:
        raise Abbruch("Kein Lord von Spieler 2")
    fern, s.fern = s.fern, 0
    frei = s.raster()[0]
    s.fern = fern
    plan = {"einheiten": [{"rolle": "ritter", "spieler": 1, "typ": 28, "x": x, "y": y} for x, y in naechste_felder(frei, lord["x"], lord["y"], 8)]}
    setzen(l, plan["einheiten"])
    k.liste([{"player": 1, "angriff": {"einheiten": [e["nr"] for e in plan["einheiten"]], "ziel": lord["nr"]}}], lf.KANAL)
    a = lk.aufnahme_im_stand(l, "lord_g", lf.TEMPO_JEDER_TAKT, False)

    def lebt():
        return any(e["nr"] == lord["nr"] and e["uid"] == lord["uid"] and e["leben"] > 0 for e in s.einheiten_alle())
    gefallen = l.warte_takte(LORD_GRENZE, lambda: not lebt())
    tod = s.takt()
    ende = gefallen and l.warte_takte(NACH_LORD, lambda: k.peek(lf.GAMEOVER)[0] != 0)
    lage = {"gefallen": gefallen, "tod": tod, "ende_gemerkt": ende, "gameover": k.peek(lf.GAMEOVER)[0], "ansicht": k.peek(lf.ANSICHT)[0]}
    b = lk.anhalten(l)
    pfad = l.rek.pfad
    stand = l.rek.beenden()
    with open(pfad + ".plan.json", "w", encoding="utf-8") as f:
        json.dump({"szene": "lord_g", "von": a, "bis": b, "tempo": lf.TEMPO_JEDER_TAKT, "lord": lord, "einheiten": plan["einheiten"], **lage}, f, ensure_ascii=False)
    k.befehl({"menue": HAUPTMENUE}, 1.5)  # eine haengende Partie wird ueber den Kanal zurueckgesetzt, nicht beendet
    return {"szene": "lord_g", "von": a, "bis": b, **lage, "stand": stand, "pfad": pfad}


SZENEN = {
    "laufen": Szene("laufen", 200, False, GRENZE_LAUF, aufbau_laufen, befehle_laufen, alle_am_ziel, treffer_noetig=False),
    "nahkampf": Szene("nahkampf", lf.TEMPO_JEDER_TAKT, True, GRENZE_NAH, aufbau_nahkampf),
    "beschuss": Szene("beschuss", lf.TEMPO_JEDER_TAKT, True, GRENZE_SCHUSS, aufbau_beschuss),
    "schlacht_20": Szene("schlacht_20", lf.TEMPO_LAUF, False, GRENZE_SCHLACHT, aufbau_schlacht(NAHKAEMPFER, NAHKAEMPFER, 20), None, schlacht_zu_ende(), masse=True),
    "schlacht_1000": Szene("schlacht_1000", lf.TEMPO_LAUF, False, GRENZE_SCHLACHT, aufbau_schlacht(NAHKAEMPFER, NAHKAEMPFER, 1000), None, schlacht_zu_ende(), masse=True),
    "schlacht_schuetzen": Szene("schlacht_schuetzen", lf.TEMPO_LAUF, False, GRENZE_SCHLACHT, aufbau_schlacht(FUSS_SCHUETZEN, NAHKAEMPFER, 500), None, schlacht_zu_ende(), masse=True),
    "schlacht_araber": Szene("schlacht_araber", lf.TEMPO_LAUF, False, GRENZE_SCHLACHT, aufbau_schlacht(EUROPAEER, ARABER, 500), None, schlacht_zu_ende(), masse=True),
    "schlacht_streng": Szene("schlacht_streng", lf.TEMPO_JEDER_TAKT, True, 500, aufbau_schlacht(NAHKAEMPFER, NAHKAEMPFER, 20), masse=True),  # jeder Takt: Die Summe der Angreifer ohne Luecken
    "last": szene_last,
    "laufen_g": Szene("laufen_g", 200, False, GRENZE_LAUF, lambda l: aufbau_laufen(l, OHNE_LORD), befehle_laufen, alle_am_ziel, treffer_noetig=False),
    "nahkampf_g": Szene("nahkampf_g", lf.TEMPO_JEDER_TAKT, True, GRENZE_NAH_G, lambda l: aufbau_nahkampf(l, OHNE_LORD)),
    "beschuss_g": Szene("beschuss_g", lf.TEMPO_JEDER_TAKT, True, GRENZE_SCHUSS, lambda l: aufbau_beschuss(l, OHNE_LORD)),
    "lord_g": szene_lord,
}


def hat_treffer(s, plan):
    jetzt = {e["nr"]: e for e in s.einheiten_alle()}
    return any((e["nr"] not in jetzt or jetzt[e["nr"]]["uid"] != e["uid"] or jetzt[e["nr"]]["leben"] < e["voll"]) for e in plan["einheiten"] if e["rolle"] != "kontrolle")


def abraeumen(l, spieler=SPIELER_S):
    """toeteAlle ist der Steintod: Die Einheiten brauchen ein paar Takte, bis ihr Platz frei ist. Gemessen, weil das bisher nur eine Wartezeit war. Im Gefecht bleiben Lord und Bauern: Ohne Lord ist die Partie vorbei (B-149)."""
    def steht_noch(e):
        return e["besitzer"] in spieler and (not l.gefecht or e["typ"] in GESETZT)
    l.k.liste([{"toeteAlle": {"spieler": p, "ohneLord": True, "typen": list(GESETZT)} if l.gefecht else p} for p in spieler], lf.KANAL)
    a = lk.aufnahme_im_stand_ohne(l, lf.TEMPO_LAUF)
    weg = l.warte_takte(ABRAEUMEN_GRENZE, lambda: not any(steht_noch(e) for e in l.s.einheiten_alle()))
    b = lk.anhalten(l)
    if not weg:
        rest = sum(1 for e in l.s.einheiten_alle() if steht_noch(e))
        raise Abbruch(f"Abraeumen: Nach {ABRAEUMEN_GRENZE} Takten stehen noch {rest} Einheiten")
    return b - a


def szene_fahren(l, sz):
    k, s = l.k, l.s
    lk.anhalten(l)
    plan = sz.aufbau(l)
    u0 = l.uhr()
    (setzen_masse if sz.masse else setzen)(l, plan["einheiten"])
    setzen_s = round(l.uhr() - u0, 2)
    if sz.befehle:
        k.liste(sz.befehle(plan), lf.KANAL)
    a = lk.aufnahme_im_stand(l, sz.name, sz.tempo, sz.streng, warte_ms=lk.WARTE_MS if sz.streng else 0)
    fertig = sz.fertig
    u1 = l.uhr()
    am_ziel = l.warte_takte(sz.grenze, (lambda: fertig(l, plan)) if fertig else None)
    d = l.uhr() - u1
    b = lk.anhalten(l)
    pfad = l.rek.pfad
    stand = l.rek.beenden()
    if sz.streng and (stand.get("fehlend") or stand.get("gemischt")):
        raise Abbruch(f"Szene {sz.name}: Takt fehlt oder ist gemischt: {stand}")
    if sz.treffer_noetig and not sz.masse and not hat_treffer(s, plan):
        raise Abbruch(f"Szene {sz.name}: Kein einziger Treffer in {b - a} Takten, der Aufbau stimmt nicht")
    if not sz.treffer_noetig and fertig and not am_ziel and not sz.masse:
        l.wirkung(f"Szene {sz.name}: nicht alle am Ziel", False, takte=b - a)
    with open(pfad + ".plan.json", "w", encoding="utf-8") as f:
        json.dump({"szene": sz.name, "von": a, "bis": b, "tempo": sz.tempo, "einheiten": plan["einheiten"]}, f, ensure_ascii=False)
    abr = abraeumen(l)
    return {"szene": sz.name, "von": a, "bis": b, "einheiten": len(plan["einheiten"]), "setzen_s": setzen_s, "takte_je_s": round((b - a) / d, 1) if d > 0 else None, "abraeumen_takte": abr, "stand": stand, "pfad": pfad}


# --- Karte im Editor ---
def namen_lesen(k):
    anzahl = k.peek(ANZAHL)[0]
    if not 0 < anzahl <= 500:
        raise Abbruch(f"Kartenliste unplausibel: {anzahl} Eintraege")
    return [lf.name_von(k, nr) for nr in k.peek(lf.LISTE, anzahl)]


def editor_oeffnen(k, s, n, ruhe=time.sleep):
    """Eigene Szenarien, Knopf 1: Liste (CustomScenarios_Main 0x00440770). Laden setzt gameMode_2 = GM_EDITOR (0x004950B0). Fehlt die Karte, kommt eine Kopie nach maps; Rueckweg: wieder herausnehmen."""
    if k.peek(lf.ANSICHT)[0] != HAUPTMENUE:
        k.befehl({"menue": HAUPTMENUE}, 1.5)
        lf.warte_auf(lambda: k.peek(lf.ANSICHT)[0] == HAUPTMENUE, 10, "Hauptmenue", ruhe=ruhe)
    k.befehl({"pause": False}, lf.KANAL)
    k.befehl({"hauptmenue": 9}, 1.5)
    lf.warte_auf(lambda: k.peek(lf.ANSICHT)[0] == SZENARIEN, 10, "Eigene Szenarien (Ansicht 44)", ruhe=ruhe)
    k.befehl({"knopf": "CustomScenarios_Main", "nr": 1}, 1.5)
    namen = namen_lesen(k)
    kopie = None
    if KARTE not in namen:
        kopie = karte_kopieren(n)
        k.befehl({"laden": 17}, 1.0)  # schliesst den Dialog (Handbuch)
        k.befehl({"knopf": "CustomScenarios_Main", "nr": 1}, 1.5)
        namen = namen_lesen(k)
        if KARTE not in namen:
            raise Abbruch(f"{KARTE} steht auch nach dem Kopieren nicht in der Liste ({len(namen)} Eintraege)")
    i = namen.index(KARTE)
    scroll = max(0, i - 12)
    k.liste([{"poke": SCROLL, "wert": scroll}, {"poke": MARKIERT, "wert": i - scroll}, {"laden": 2}], 4.0)
    lf.warte_auf(lambda: k.peek(lf.ANSICHT)[0] == EIGENSCHAFTEN, 60, "Karteneigenschaften (Ansicht 17)", ruhe=ruhe)
    k.befehl({"menue": LANDSCHAFT}, 1.5)
    k.befehl({"pause": False}, lf.KANAL)
    return {"eintrag": i, "von": len(namen), "kopie": kopie, "ansicht": k.peek(lf.ANSICHT)[0]}


def gefecht_oeffnen(k, ruhe=time.sleep):
    """Zwei Mensch-Plaetze, keine KI (L119): Spieler 2 tut nur, was befohlen wird. Feste Startplaetze: Ohne sie bekommt Spieler 2 Platz 246, also 6 Bogenschuetzen, aber weder Burg noch Lord (gemessen 03.11. 20:04)."""
    if k.peek(lf.ANSICHT)[0] != HAUPTMENUE:
        k.befehl({"menue": HAUPTMENUE}, 1.5)
        lf.warte_auf(lambda: k.peek(lf.ANSICHT)[0] == HAUPTMENUE, 10, "Hauptmenue", ruhe=ruhe)
    k.befehl({"pause": False}, lf.KANAL)  # sonst startet das neue Gefecht eingefroren (selbstspiel.py)
    k.befehl({"eigenesGefecht": True, "karte": KARTE, "menschen": 2, "gegner": 0, "trotzdem": True, "startpause": 1, "startliste": list(STARTPLAETZE)}, 5.0)
    lf.warte_auf(lambda: k.peek(lf.ANSICHT)[0] == lf.IN_PARTIE, 60, "Partie laeuft (Ansicht 14)", ruhe=ruhe)
    return {"ansicht": k.peek(lf.ANSICHT)[0]}


def richtige_lords(s):
    """Genau die Lords der zwei Menschen, jeder bei einem Haufen der Karte: Das ist die Karte, und niemand sonst spielt mit."""
    lords = [e for e in s.einheiten_alle() if e["typ"] == 55]
    return sorted(e["besitzer"] for e in lords) == [1, 2] and all(min(max(abs(e["x"] - x), abs(e["y"] - y)) for x, y in START_HAUFEN) <= 40 for e in lords)


def karte_kopieren(n):
    ziel = os.path.join(lf.ordner(n), "maps", KARTE + ".map")
    for o in lk.karten_ordner(n):
        p = os.path.join(o, KARTE + ".map")
        if os.path.exists(p) and p != ziel:
            shutil.copy2(p, ziel)
            return ziel
    raise Abbruch(f"{KARTE} liegt in keinem Kartenordner")


def richtige_karte(s):
    _, _, ge = s.raster()
    return all(ge[y, x] for x, y in START_HAUFEN)


class LaufS(lk.LaufK):
    def __init__(self, k, s, rek, schreib, uhr=time.perf_counter, ruhe=time.sleep, stop=lambda: False):
        super().__init__(k, s, {}, rek, schreib, frist=10 ** 9, uhr=uhr, ruhe=ruhe, stop=stop)  # keine Frist: Die Grenzen sind Takte, gegen Haengen wacht die Stillstandsgrenze
        self.gefecht = False


def bank_von(szenen):
    """Gefecht ja oder nein. Beides in einem Lauf geht nicht."""
    gefecht = all(z.endswith("_g") for z in szenen)
    if not gefecht and any(z.endswith("_g") for z in szenen):
        raise Fehler("Szenen mit _g laufen im Gefecht, die anderen im Editor: nicht im selben Lauf")
    return gefecht


def los(n, szenen, ziel=None):
    if os.environ.get("PYTEST_CURRENT_TEST"):
        raise Fehler("Aus einem Test startet kein echter Lauf")  # 03.11.: ein Prueffall kam bis hierher und fuhr zweimal echte Szenen auf Instanz 2
    lf.pruefe_laufinstanz(n)
    gefecht = bank_von(szenen)
    os.environ["SHC_INSTANZ"] = str(n)
    from selfaware import workspace
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
    from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz, spielart_lesen, standard_bereiche

    ziel = ziel or os.path.join(workspace.DATA, "auge_plan", "laeufe")
    os.makedirs(ziel, exist_ok=True)
    stempel = time.strftime("%Y%m%d_%H%M%S")
    basis = os.path.join(ziel, f"lauf_s_{stempel}")
    laeuft_schon = pid_der_instanz(n) is not None
    fehlt = [z for z in lf.pruefen(n, laeuft_schon=laeuft_schon) if not z[1]]
    if fehlt:
        raise Fehler(f"Trockenprobe rot: {fehlt}")
    stop = lf.stop_datei(ziel)
    if os.path.exists(stop):
        os.remove(stop)
    lf.sperre_holen(f"Lauf S Auge (B-142) {','.join(szenen)}")

    def schreib(e):
        with open(basis + ".protokoll.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(e, ensure_ascii=False, default=str) + "\n")
        print(json.dumps(e, ensure_ascii=False, default=str)[:500], flush=True)

    rek = k = s = None
    ergebnis = {"szenen": []}
    try:
        q = os.path.join(lf.ordner(lf.QUELL_INSTANZ), "ucp", "villagestudio", "logik.lua")
        log = os.path.join(lf.ordner(n), "ucp3.log")
        log_vorher = os.path.getsize(log) if os.path.exists(log) else 0
        sicherung = lf.logik_einspielen(os.path.join(lf.ordner(n), "ucp", "villagestudio", "logik.lua"), q, stempel)
        schreib({"schritt": "logik", "sicherung": sicherung})
        schreib({"schritt": "ladeliste", "sicherung": lf.modul_eintragen(os.path.join(lf.ordner(n), "ucp-config.yml"), stempel)})
        if not laeuft_schon:
            ps = os.path.join(workspace.ROOT, "tools", "windows", "spiel_starten.ps1")
            import subprocess
            a = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps, "-Instanz", str(n)], capture_output=True, text=True, timeout=120)
            schreib({"schritt": "start", "ausgabe": a.stdout.strip()[-200:]})
            if a.returncode != 0:
                raise Fehler(f"Spielstart: {a.stdout} {a.stderr}")
        k = lf.EchterKanal()
        lf.warte_auf_modul(k)
        if laeuft_schon and sicherung:
            def nachgeladen():
                with open(log, encoding="utf-8", errors="replace") as f:
                    f.seek(log_vorher)
                    return "logik.lua neu geladen" in f.read()
            lf.warte_auf(nachgeladen, 20, "Modul hat die logik.lua nachgeladen")
        for rest in lf.ALTE_SCHALTER:
            k.befehl(rest, lf.KANAL)
        karte = Feldkarte.laden(feldliste=FELDLISTE)
        quelle = ProzessQuelle(pid_der_instanz(n))
        s = SpeicherS(quelle, karte)
        schreib({"schritt": "spielart_vorher", **spielart_lesen(quelle, karte)})
        if gefecht:
            schreib({"schritt": "gefecht", **gefecht_oeffnen(k)})
        else:
            schreib({"schritt": "editor", **editor_oeffnen(k, s, n)})
            if not richtige_karte(s):
                raise Abbruch(f"Nicht die Karte {KARTE}: An den Startplaetzen steht kein Gebaeude")
        art = spielart_lesen(quelle, karte)
        schreib({"schritt": "spielart", **art})
        if gefecht and (art["currentGameMode"], art["gameMode_2"]) != (99, 3):
            raise Abbruch(f"Nicht im Gefecht: {art}")
        if not gefecht and art["gameMode_2"] != 1:
            raise Abbruch(f"Nicht im Editor: gameMode_2 {art['gameMode_2']}")
        rek = lf.Rekorder(n, ziel, stempel, quelle, standard_bereiche(karte))
        rek.lauf = "S"
        rek.basis = basis
        rek.stop_datei, rek.aus_datei, rek.felder_datei = basis + ".stop", basis + ".aussetzen", basis + ".felder.json"
        l = LaufS(k, s, rek, schreib, stop=lambda: os.path.exists(stop))
        if gefecht:
            l.gefecht, s.fern = True, GEFECHT_ABSTAND
            lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
            if not l.warte_takte(lk.LORDS_STEHEN, lambda: richtige_lords(s)):
                raise Abbruch(f"Nicht die erwarteten Lords: {[(e['besitzer'], e['x'], e['y']) for e in s.einheiten_alle() if e['typ'] == 55]}")
            lk.anhalten(l)
            schreib({"schritt": "lords", "lords": [e for e in s.einheiten_alle() if e["typ"] == 55], "bleiben": len(s.einheiten_alle()), "freie_felder": int(s.raster()[0].sum())})
        else:
            schreib({"schritt": "start_raeumen", "takte": abraeumen(l, spieler=tuple(range(1, 9))), "bleiben": len(s.einheiten_alle()), "freie_felder": int(s.raster()[0].sum())})
        for name in szenen:
            e = SZENEN[name](l) if callable(SZENEN[name]) else szene_fahren(l, SZENEN[name])
            schreib(e)
            ergebnis["szenen"].append(e)
    except Abbruch as e:
        schreib({"schritt": "abbruch", "grund": str(e)})
        ergebnis["abbruch"] = str(e)
    finally:
        steht = False
        if k is not None and s is not None:
            try:
                steht, t = lf.anhalten_und_pruefen(k, s)
                schreib({"schritt": "angehalten", "steht": steht, "takt": t})
            except (OSError, RuntimeError) as e:
                schreib({"schritt": "anhalten_fehlgeschlagen", "grund": str(e)})
        else:
            steht = True
        if rek is not None:
            schreib({"schritt": "aufzeichnung_beendet", "stand": rek.beenden()})
        if steht:
            lf.sperre_freigeben()
        else:
            schreib({"schritt": "sperre_bleibt", "grund": "Der Takt steht nicht, die Sperre bleibt, bis das geklaert ist"})
    print("SZENEN ZU ENDE:", json.dumps({k_: v for k_, v in ergebnis.items() if k_ != "szenen"}, ensure_ascii=False), [e["szene"] for e in ergebnis["szenen"]], flush=True)
    return ergebnis, basis


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("was", choices=["los"])
    p.add_argument("--instanz", type=int, required=True)
    p.add_argument("--szenen", nargs="+", choices=sorted(SZENEN), required=True)
    p.add_argument("--daniel-ja", action="store_true", help="Lauf nur nach Daniels Ja")
    a = p.parse_args(argv)
    lf.pruefe_laufinstanz(a.instanz)
    if not a.daniel_ja:
        raise Fehler("Szenen starten nur mit --daniel-ja")
    e, _ = los(a.instanz, a.szenen)
    return 1 if e.get("abbruch") else 0


if __name__ == "__main__":
    sys.exit(main())
