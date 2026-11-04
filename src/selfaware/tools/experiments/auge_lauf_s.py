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
E_TRUPP = 728  # tribeID, wie im Modul
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
WARTESCHLANGE = 20  # Takte je Angriffsbefehl hoechstens: So lange wartet das Modul, bis die Gruppe steht
FELDER_BAHN = 60  # groesste Reichweite laut Tabelle 0x5B6358: Pfeil 54 Felder; geflogen sind schon 40
GRENZE_BAHN = FELDER_BAHN * 32 + 2 * 228 + 19 * WARTESCHLANGE  # langsamste Art 32 Takte je Feld, dazu 2 Schuss Armbrust und die Warteschlange
SCHUSS_WEITE = {22: 54, 23: 40, 70: 54, 72: 18, 74: 54, 76: 11}  # Felder, Tabelle 0x5B6358 je Geschossart: Pfeil 54, Bolzen 40, Schleuder 18, Feuer 11
GRENZE_SCHUSSWEITE = 36 * WARTESCHLANGE + 2 * 228  # alle Befehle, dann 2 Schuss Armbrust
FAELLE_SCHUSSWEITE = [(t, d) for t, r in SCHUSS_WEITE.items() for d in (r // 2, r - 2, r - 1, r, r + 1, r + 2)]
FAELLE_PFEIL = [(t, d) for t in (22, 70, 74) for d in range(28, 52, 2)]  # Pfeil schoss auf 27 Felder, auf 52 nicht mehr (Lauf 20:30): dazwischen liegt die Grenze, die Tabelle sagt 54
ABSTAND_PENDEL, FELDER_PENDEL, GRENZE_PENDEL = 8, 20, 1323  # 5 Schuss Armbrust (228) und die Warteschlange. Abstand 8: Das reicht auch dem Feuerwerfer (flog bis 8,5 Felder)
PENDLER = 26  # Streitkolbenkaempfer: 25.000 Leben, schnell, schlaegt auf Abstand 8 nicht zu
HALTUNGEN = (("aggressiv", 2, 24), ("aggressiv", 2, 26), ("defensiv", 1, 4), ("defensiv", 1, 6), ("stehen", 0, 4))  # Code: aggressiv 200 Mikro, defensiv 40 Mikro, 8 je Feld
HALTUNG_ARTEN = (28, 24, 30)  # Ritter, Speertraeger, Ingenieur: je eine Pruefrunde 63, 127, 255. Keine Schuetzen: Sie schiessen ueber 40 Felder, das stoert die Nachbarn
HALTUNG_RASTER_X, HALTUNG_RASTER_Y = 60, 40  # Abstand der Faelle: Der naechste fremde Feind steht mindestens 34 Felder weg, groesster Radius 25. Es passen 11 Faelle, darum zwei Szenen
FAELLE_HALTUNG = list(itertools.product(HALTUNG_ARTEN, HALTUNGEN))
GRENZE_HALTUNG, HALTUNG_TRUPP, HALTUNG_BEFEHL = 1024, 15 * WARTESCHLANGE, 100  # 2 volle Pruefrunden der langsamsten Art; alle Gruppen; Befehl im naechsten Takt, gemessen wird es hier
BESATZUNG = {39: 2, 40: 3, 41: 2, 61: 2, 77: 2, 59: 4, 58: 4, 60: 1}  # getRemainingRequiredEngineers 0x5334A0
SCHIESSEN, FAHREN = (39, 40, 41, 61, 77), (39, 77, 60, 59, 58)  # Trebuchet, Mangonel, Ballista fahren nicht (DAT_UNIT_MOVABLE 0)
ABSTAND_GERAET, GRENZE_GERAET = 20, 1600  # innerhalb jeder Reichweite der Tabelle (kleinste 39); Grenze: 8 Steine Katapult (123) oder 20 Felder bei 64 Takten je Feld, der langsamste Wert ist noch nicht gemessen
GRENZE_BEMANNEN = 40 * WARTESCHLANGE
KLASSEN = (1, 41, 46, 74)  # Huette, Burg (kein Leben), kleines Tor, Turm. Mauern haben kein Gebaeude, sie kommen mit den Sonderfaellen
ANDERE_GERAETE = (40, 41, 61, 77, 59)
ABSTAND_BELAGERUNG, GRENZE_BELAGERUNG = 16, 1000  # 8 Steine Katapult
NAH_GEGEN_GEBAEUDE = (24, 25, 26, 27, 28, 37, 55, 71, 73, 75)  # die 10 der Liste V4b
NAH_ZIELE = (1, 41, 45, 46, 74)  # Huette, Burg (kein Leben), grosses und kleines Tor, Turm. Das Lager liess sich nicht setzen (Lauf 20:41), Holztor und Mauern fehlen hier
GERAETE_WEITE = {39: 57, 40: 68, 41: 54, 61: 68, 77: 39}  # Felder, Tabelle 0x5B6358 je Geschossart. Beim Pfeil stimmte sie nicht
GRENZE_GERAETE_WEITE = 1000  # 3 Schuss Trebuchet (296 Takte)
PUNKT_FAELLE = (("feld", 10), ("feld", 100), ("feld", 500), ("tor", 100), ("tor", 500), ("turm", 100), ("luecke", 100), ("luecke", 500))  # Liste V6
PUNKT_WEG, GRENZE_PUNKT = 30, 3000  # Felder bis zum Ziel; 30 Felder zu 12 Takten, mal 8 fuer den Stau bei 500
GRENZE_SONDER, SONDER_ABSTAND = 3000, 30  # Takte; Abstand der Posten, Feuerwerfer reicht 11, Schuetzen haben ihr Ziel per Befehl
STARTTRUPPEN_TAKT = 410  # Gefecht: 6 Bogenschuetzen kamen bei Takt 202, 8 Speertraeger bei 403, je Spieler an der Burg (Lauf 22:41). Wer vorher raeumt, hat sie danach im Feld
SONDER_SPIELER_TAKTE = 40  # Takte je Spieler fuer die Spielbefehle davor: Im selben Takt laufen alle als der zuletzt gesetzte Spieler (Modul: PLATZ_TAKTE 1), Graben, Mauern und Pech kamen so nie an (Lauf 21:30)
SONDER_BEMANNEN = 400  # Takte: Geraete waren nach 356 Takten bemannt (Szene besatzung)
GRENZE_NAH_GEBAEUDE = 300  # Takte auf Tempo 40: Schaden je Schlag, Weg hoechstens 2 Felder
STARTPLAETZE = (0, 1, 246, 246, 246, 246, 246, 246)  # playerPositionsArray: Platz je Spieler, 246 = keiner
LORD_RUHE, LORD_WEG = 300, 600  # Takte: Am Anfang geht der Lord von selbst auf die Burg (gemessen 97 bis 197). Weg zum Ring: 10 Felder, 24 Takte je Feld, mal 2
NACH_LORD = 300  # Takte: Wann das Spiel das Ende merkt, ist hier die Frage, die Pruefrunde des Lords liegt bei 64 Takten
STUECK = 100  # Befehle je Sendung
GRENZE_NAH = 251 + 256  # groesster erster Treffer vom 18.10. plus groesste Pruefrunde (Maske 255), alte_schuesse.txt
GRENZE_SCHUSS = 411 + 2 * 228  # groesster erster Treffer plus 2 Schuesse Armbrust, Handbuch 17.10.
FELDER_LAUF = 20  # 20 Felder: Anlauf hoechstens 12 Takte (calculateUnitMovementSpeed), Ablesefehler rund 2 Takte auf mindestens 230
GRENZE_LAUF = FELDER_LAUF * 36 * 2  # Tempo-Wert 3 (Schwertkaempfer), rund 12 Takte je Feld je Stufe (L80), Annahme; mal 2. Geraete fahren erst bemannt, das braucht eine eigene Szene
GRENZE_TRUPP = GRENZE_LAUF + 38 * WARTESCHLANGE


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
                aus.append({"nr": i, "typ": h(lf.E_TYP), "besitzer": h(lf.E_BESITZER), "x": h(E_MX) // 8, "y": h(E_MY) // 8, "trupp": h(E_TRUPP),
                            "leben": struct.unpack_from("<i", roh, b + E_LEBEN)[0], "uid": struct.unpack_from("<i", roh, b + E_UID)[0]})
        return aus

    def kachel(self, x, y):
        """Feldnummer: Mauerangriff und Leiter nehmen sie statt x und y (giveTribeAnInstruction, tileTranslationMatrix)."""
        return struct.unpack("<i", self.q.lies(lf.ZEILEN + y * 12 + 8, 4))[0] + x

    def feld(self, gruppe, name):
        adr, _, schritt, _ = self.karte.adresse(gruppe, name)
        return adr, schritt

    def pech_liste(self, sp):
        """Die Pechgraeben eines Spielers: Nummer und uid fuer Anweisung 34."""
        a = self.karte.adresse("DAT_TileMapState", "pitchDitches[].uid")
        roh = self.q.lies(a[0], a[2] * a[3])
        aus = []
        o = {n: self.karte.adresse("DAT_TileMapState", "pitchDitches[]." + n)[0] - a[0] for n in ("x", "y", "owner")}
        for i in range(1, a[3]):
            b = i * a[2]
            u = struct.unpack_from("<i", roh, b)[0]
            if u and struct.unpack_from("<h", roh, b + o["owner"])[0] == sp:
                aus.append({"nr": i, "uid": u, "x": struct.unpack_from("<h", roh, b + o["x"])[0], "y": struct.unpack_from("<h", roh, b + o["y"])[0]})
        return aus

    def besatzung(self, nr):
        adr, _, schritt, _ = self.karte.adresse("DAT_UnitsState", "units[].digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300")
        return struct.unpack("<h", self.q.lies(adr + nr * schritt, 2))[0]

    def haltung(self, trupp):
        adr, _, schritt, _ = self.karte.adresse("DAT_TribesState", "tribes[].unitStance")
        return struct.unpack("<h", self.q.lies(adr + trupp * schritt, 2))[0]

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


def packen(frei, masse, rand=2):
    """Legt Rechtecke (Breite, Hoehe) der Reihe nach an die erste freie Stelle und sperrt sie samt Rand. Die Karte ist zerklueftet, im festen Raster gab es nur 15 Plaetze 40 x 15. Rueckgabe je Eintrag (x, y), None, wenn nichts mehr passt."""
    belegt = ~frei
    aus = []
    for b, h in masse:
        s = np.zeros((frei.shape[0] + 1, frei.shape[1] + 1), dtype=np.int64)
        s[1:, 1:] = (~belegt).cumsum(0).cumsum(1)
        f = s[h:, b:] - s[:-h, b:] - s[h:, :-b] + s[:-h, :-b]
        ys, xs = np.nonzero(f == b * h)
        if not len(ys):
            aus.append(None)
            continue
        x, y = int(xs[0]), int(ys[0])
        belegt[max(0, y - rand):y + h + rand, max(0, x - rand):x + b + rand] = True
        aus.append((x, y))
    return aus


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


def aufbau_beschuss(l, arten=SOLDATEN, dy=12):
    """Jeder Fussschuetze gegen jede der 19 Arten, Abstand 8: Der Schaden ist von 4 bis 20 Feldern gleich (Handbuch 17.10.), der Feuerwerfer reicht bis 10. Raster 20 x 12: Der naechste Feind ist das eigene Ziel. Kein Befehl: Schuetzen waehlen ihr Ziel selbst."""
    frei, hoehe, _ = l.s.raster()
    paare = list(itertools.product(FUSS_SCHUETZEN, arten))
    orte = gitter(frei, hoehe, 9, 1, 20, dy, len(paare))
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


def befehle_laufen_trupp(plan):
    """Der echte Weg im Spiel: Auswahl, Gruppe, Laufbefehl (Spielbefehle 16 und 17), je Einheit eine Gruppe."""
    return [{"player": 1, "angriff": {"einheiten": [e["nr"]], "lauf": list(e["ziel"])}} for e in plan["einheiten"]]


def aufbau_reichweite(l, arten=SOLDATEN):
    """Jede Art auf eigener Bahn gegen eine unbemannte Ramme von Spieler 2: 400.000 Leben, sie wehrt sich nicht. Mit Angriffsbefehl laufen Schuetzen, bis sie schiessen, Nahkaempfer, bis sie schlagen. Das misst Reichweite, Schusstakt und das Tempo im Angriff in einer Szene."""
    frei, hoehe, _ = l.s.raster()
    orte = gitter(frei, hoehe, FELDER_BAHN + 2, 1, FELDER_BAHN + 6, 6, len(arten), flach=True)
    eben = len(orte) >= len(arten)
    if not eben:
        orte = gitter(frei, hoehe, FELDER_BAHN + 2, 1, FELDER_BAHN + 6, 6, len(arten))
    if len(orte) < len(arten):
        raise Abbruch(f"Nur {len(orte)} Bahnen fuer {len(arten)} Arten")
    aus = []
    for i, (t, (x, y)) in enumerate(zip(arten, orte)):
        aus += [{"rolle": "laeufer", "paar": i, "spieler": 1, "typ": t, "x": x, "y": y}, {"rolle": "ziel", "paar": i, "spieler": 2, "typ": 59, "x": x + FELDER_BAHN, "y": y}]
    return {"einheiten": mit_kontrolle(aus, frei), "eben": eben}


def aufbau_schussweite(l, faelle=FAELLE_SCHUSSWEITE):
    """Schuetzen laufen auf einen Angriffsbefehl nicht los (giveTribeAnInstruction, UIT_UNIT_ATTACK_UNIT: makeUnitStopWalking), Szene reichweite_g hat es gezeigt. Darum eine Leiter: jede Art mit Befehl auf eine Ramme in Abstaenden rund um den Tabellenwert. Gezaehlt werden nur Geschosse auf das befohlene Ziel."""
    frei, hoehe, _ = l.s.raster()
    breite = max(d for _, d in faelle) + 2
    orte = gitter(frei, hoehe, breite, 1, breite + 4, 6, len(faelle), flach=True)
    eben = len(orte) >= len(faelle)
    if not eben:
        orte = gitter(frei, hoehe, breite, 1, breite + 4, 6, len(faelle))
    if len(orte) < len(faelle):
        raise Abbruch(f"Nur {len(orte)} Bahnen fuer {len(faelle)} Faelle")
    aus = []
    for i, ((t, d), (x, y)) in enumerate(zip(faelle, orte)):
        aus += [{"rolle": "laeufer", "paar": i, "spieler": 1, "typ": t, "x": x, "y": y, "abstand": d}, {"rolle": "ziel", "paar": i, "spieler": 2, "typ": 59, "x": x + d, "y": y}]
    return {"einheiten": mit_kontrolle(aus, frei), "eben": eben}


def befehle_auf_partner(plan, rolle_a="laeufer", rolle_b="ziel"):
    ziele = {e["paar"]: e["nr"] for e in plan["einheiten"] if e["rolle"] == rolle_b}
    return [{"player": 1, "angriff": {"einheiten": [e["nr"]], "ziel": ziele[e["paar"]]}} for e in plan["einheiten"] if e["rolle"] == rolle_a]


def befehle_auf_geraet(plan):
    return befehle_auf_partner(plan, "geraet", "ziel")


def aufbau_laufziel(l):
    """Jeder Fussschuetze mit Befehl auf einen Streitkolbenkaempfer, der quer zur Schussrichtung hin und her laeuft. Der Zielpunkt eines Geschosses steht beim Abschuss fest: Trifft es den Laeufer?"""
    frei, hoehe, _ = l.s.raster()
    orte = gitter(frei, hoehe, ABSTAND_PENDEL + 2, FELDER_PENDEL + 2, 60, 60, len(FUSS_SCHUETZEN))
    if len(orte) < len(FUSS_SCHUETZEN):
        raise Abbruch(f"Nur {len(orte)} Plaetze fuer {len(FUSS_SCHUETZEN)} Schuetzen")
    aus = []
    for i, (t, (x, y)) in enumerate(zip(FUSS_SCHUETZEN, orte)):
        ax = x + ABSTAND_PENDEL
        aus += [{"rolle": "schuetze", "paar": i, "spieler": 1, "typ": t, "x": x, "y": y + FELDER_PENDEL // 2},
                {"rolle": "pendel", "paar": i, "spieler": 2, "typ": PENDLER, "x": ax, "y": y, "wende": [[ax, y + FELDER_PENDEL], [ax, y]], "weiter": 0}]
    return {"einheiten": mit_kontrolle(aus, frei)}


def befehle_laufziel(plan):
    return [{"einheit_ziel": {"nr": e["nr"], "x": e["wende"][0][0], "y": e["wende"][0][1]}} for e in plan["einheiten"] if e["rolle"] == "pendel"] + befehle_auf_partner(plan, "schuetze", "pendel")


def pendeln(l, plan):
    """Wer am Wendepunkt ist, bekommt den anderen. Immer False: Die Szene endet an der Grenze. Nachgesehen wird alle 8 Takte, das ist ein halbes Feld: Jedes Nachsehen liest alle Plaetze."""
    t = l.s.takt()
    if t < plan.get("naechstes_wenden", 0):
        return False
    plan["naechstes_wenden"] = t + 8
    orte = {e["nr"]: (e["x"], e["y"]) for e in l.s.einheiten_alle()}
    bef = []
    for e in plan["einheiten"]:
        if e["rolle"] == "pendel" and orte.get(e["nr"]) == tuple(e["wende"][e["weiter"]]):
            e["weiter"] ^= 1
            x, y = e["wende"][e["weiter"]]
            bef.append({"einheit_ziel": {"nr": e["nr"], "x": x, "y": y}})
    if bef:
        l.k.liste(bef, lf.KANAL)
    return False


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
    am_ende_am_ziel: bool = True


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


def gebaeude_setzen(l, ziele):
    """Das Spiel steht. setzeGebaeude meldet immer ok, also wird nachgelesen, was wirklich steht: Jedes Ziel bekommt nr und uid des neuen Gebaeudes an seinem Ort. Rueckgabe: was nicht steht, das ist ein Fund."""
    vorher = {g["nr"] for g in l.s.gebaeude(None)}
    bef = [{"setzeGebaeude": {"spieler": z["spieler"], "x": z["x"], "y": z["y"], "mapper": z["mapper"], "groesse": z["groesse"]}} for z in ziele]
    for i in range(0, len(bef), STUECK):
        l.k.liste(bef[i:i + STUECK], lf.KANAL)
    neu = []
    ende = l.uhr() + SETZEN_FRIST
    while l.uhr() < ende:
        neu = [g for g in l.s.gebaeude(None) if g["nr"] not in vorher]
        if len(neu) >= len(ziele):
            break
        l.ruhe(0.2)
    for z in ziele:
        g = next((g for g in neu if g["typ"] == z["typ"] and max(abs(g["x"] - z["x"]), abs(g["y"] - z["y"])) <= z["groesse"]), None)  # Art und Ort: Sonst nimmt ein nicht gesetztes Ziel das Gebaeude des Nachbarn
        if g is not None:
            neu.remove(g)
            z.update(nr=g["nr"], uid=g["uid"], laufzeit=g["typ"])
    return [z for z in ziele if "nr" not in z]


def erlaubte_stelle(l, z, rand=6):
    """Das Spiel selbst fragen: Frei und eben reichte nicht, checkBuildingCanBePlacedHere lehnte Kaefig und Wachturm trotzdem ab (Lauf 21:30). Rueckgabe: die naechste erlaubte Stelle (x, y) oder None."""
    zeilen = l.k.platzkarte(z["mapper"], z["groesse"], z["x"] - rand, z["y"] - rand, z["x"] + rand, z["y"] + rand, z["spieler"])
    beste = None
    for j, reihe in enumerate(zeilen):
        for i, c in enumerate(reihe):
            d = max(abs(i - rand), abs(j - rand))
            if c == "+" and (beste is None or d < beste[0]):
                beste = (d, z["x"] - rand + i, z["y"] - rand + j)
    return beste[1:] if beste else None


def aufbau_besatzung(l):
    """Je Geraet eine Zeile mit voller Besatzung und eine mit einem Mann zu wenig, einmal schiessen, einmal fahren. Das Ziel beim Schiessen ist ein Pikenier von Spieler 2: 80.000 Leben, er laeuft ohne Gruppe nicht los."""
    frei, hoehe, _ = l.s.raster()
    faelle = [("schiessen", t, n) for t in SCHIESSEN for n in (BESATZUNG[t], BESATZUNG[t] - 1)] + [("fahren", t, n) for t in FAHREN for n in (BESATZUNG[t], BESATZUNG[t] - 1)]
    b, h = ABSTAND_GERAET + 8, 9
    orte = gitter(frei, hoehe, b, h, b + 6, h + 6, len(faelle), flach=True)
    if len(orte) < len(faelle):
        orte = gitter(frei, hoehe, b, h, b + 6, h + 6, len(faelle))
    if len(orte) < len(faelle):
        raise Abbruch(f"Nur {len(orte)} Plaetze fuer {len(faelle)} Geraete-Faelle")
    aus = []
    for i, ((art, t, n), (x, y)) in enumerate(zip(faelle, orte)):
        gx, gy = x + 4, y + 4
        aus.append({"rolle": "geraet", "fall": i, "art": art, "soll": BESATZUNG[t], "mann": n, "spieler": 1, "typ": t, "x": gx, "y": gy, "dorthin": [gx + ABSTAND_GERAET, gy]})
        aus += [{"rolle": "ingenieur", "fall": i, "spieler": 1, "typ": 30, "x": x + j % 2, "y": y + 2 + j // 2 * 2} for j in range(n)]
        if art == "schiessen":
            aus.append({"rolle": "ziel", "fall": i, "spieler": 2, "typ": 25, "x": gx + ABSTAND_GERAET, "y": gy})
    return {"einheiten": mit_kontrolle(aus, frei)}


def befehle_einsteigen(plan):
    """Anweisung 16 (UIT_MAN_SIEGE_EQUIPMENT): Die Ingenieure eines Geraets werden eine Gruppe und steigen ein."""
    aus = []
    for g in plan["einheiten"]:
        if g["rolle"] == "geraet":
            leute = [e["nr"] for e in plan["einheiten"] if e["rolle"] == "ingenieur" and e["fall"] == g["fall"]]
            if leute:
                aus.append({"player": 1, "angriff": {"einheiten": leute, "art": 16, "a": g["nr"], "b": g["uid"]}})
    return aus


def befehle_besatzung(plan):
    ziele = {e["fall"]: e["nr"] for e in plan["einheiten"] if e["rolle"] == "ziel"}
    return [{"player": 1, "angriff": {"einheiten": [g["nr"]], **({"ziel": ziele[g["fall"]]} if g["art"] == "schiessen" else {"lauf": list(g["dorthin"])})}} for g in plan["einheiten"] if g["rolle"] == "geraet"]


def aufbau_belagerung(l):
    """Der Schaden je Stein steht fest (processEntityHitBuildingOrUnit), das Leben steht in der Tabelle: Darum alle Gebaeude mit Bauzeile gegen ein Katapult und die anderen Geraete gegen 4 Klassen. Es zaehlt, was auf die Karte passt, zuerst die Klassen; der Rest ist gerechnet und so gekennzeichnet."""
    from selfaware.game.ucp.bauen import NACH_TYP

    frei, hoehe, _ = l.s.raster()
    rest = sorted((z for z in NACH_TYP if z not in KLASSEN), key=lambda z: -NACH_TYP[z]["b"])  # die grossen zuerst, sonst passen sie nicht mehr
    faelle = [(t, z) for t in ANDERE_GERAETE for z in KLASSEN] + [(39, z) for z in KLASSEN] + [(39, z) for z in rest]
    orte = packen(frei, [(3 + ABSTAND_BELAGERUNG + NACH_TYP[z]["b"] + 2, max(NACH_TYP[z]["b"] + 2, 9)) for _, z in faelle], rand=3)
    if any(o is None for o in orte[:len(KLASSEN) * (len(ANDERE_GERAETE) + 1)]):
        raise Abbruch(f"Nur {sum(o is not None for o in orte)} Plaetze fuer die Belagerung")
    einheiten, ziele = [], []
    for i, ((t, z), o) in enumerate(zip(faelle, orte)):
        if o is None:
            continue
        x, y = o
        gx, gy = x + 3, y + 4
        einheiten.append({"rolle": "geraet", "fall": i, "art": "belagern", "soll": BESATZUNG[t], "mann": BESATZUNG[t], "spieler": 1, "typ": t, "x": gx, "y": gy})
        einheiten += [{"rolle": "ingenieur", "fall": i, "spieler": 1, "typ": 30, "x": x + j % 2, "y": y + 2 + j // 2 * 2} for j in range(BESATZUNG[t])]
        ziele.append({"fall": i, "spieler": 2, "typ": z, "mapper": NACH_TYP[z]["mapper"], "groesse": NACH_TYP[z]["b"], "name": NACH_TYP[z]["laufzeitName"], "x": gx + ABSTAND_BELAGERUNG, "y": y + 1})
    fehlt = gebaeude_setzen(l, ziele)
    faelle_da = {z["fall"] for z in ziele if "nr" in z}
    return {"einheiten": mit_kontrolle([e for e in einheiten if e["fall"] in faelle_da], frei), "gebaeude": ziele, "nicht_gesetzt": [z["name"] for z in fehlt], "nicht_gefahren": [NACH_TYP[z]["laufzeitName"] for (_, z), o in zip(faelle, orte) if o is None]}


def befehle_belagerung(plan):
    ziele = {z["fall"]: z["nr"] for z in plan["gebaeude"] if "nr" in z}
    return [{"player": 1, "angriff": {"einheiten": [g["nr"]], "gebaeude": ziele[g["fall"]]}} for g in plan["einheiten"] if g["rolle"] == "geraet"]


def aufbau_gebaeude_nah(l):
    """Die 10 Nahkaempfer der Liste gegen 5 Gebaeude, jeder direkt daneben, mit Angriffsbefehl: Schlaegt er, und was kostet ein Schlag?"""
    from selfaware.game.ucp.bauen import NACH_TYP

    frei, hoehe, _ = l.s.raster()
    faelle = list(itertools.product(NAH_GEGEN_GEBAEUDE, NAH_ZIELE))
    orte = packen(frei, [(12, 10)] * len(faelle), rand=3)
    if any(o is None for o in orte):
        raise Abbruch(f"Nur {sum(o is not None for o in orte)} Plaetze fuer {len(faelle)} Paare")
    einheiten, ziele = [], []
    for i, ((t, z), (x, y)) in enumerate(zip(faelle, orte)):
        einheiten.append({"rolle": "angreifer", "fall": i, "spieler": 1, "typ": t, "x": x, "y": y + 4})
        ziele.append({"fall": i, "spieler": 2, "typ": z, "mapper": NACH_TYP[z]["mapper"], "groesse": NACH_TYP[z]["b"], "name": NACH_TYP[z]["laufzeitName"], "x": x + 2, "y": y + 1})
    fehlt = gebaeude_setzen(l, ziele)
    da = {z["fall"] for z in ziele if "nr" in z}
    return {"einheiten": mit_kontrolle([e for e in einheiten if e["fall"] in da], frei), "gebaeude": ziele, "nicht_gesetzt": [z["name"] for z in fehlt]}


def aufbau_geraete_weite(l):
    """Die Leiter fuer die schiessenden Geraete, je Geraet 5 Abstaende bis etwas ueber den Tabellenwert. Das Ziel ist eine unbemannte Ramme von Spieler 2."""
    frei, hoehe, _ = l.s.raster()
    faelle = [(t, d) for t, r in GERAETE_WEITE.items() for d in (r // 2, r * 7 // 10, r * 85 // 100, r, r + 2)]
    orte = packen(frei, [(d + 8, 9) for _, d in faelle], rand=3)
    einheiten = []
    fehlt = []
    for i, ((t, d), o) in enumerate(zip(faelle, orte)):
        if o is None:
            fehlt.append((t, d))
            continue
        x, y = o
        gx, gy = x + 4, y + 4
        einheiten.append({"rolle": "geraet", "fall": i, "paar": i, "art": "schiessen", "soll": BESATZUNG[t], "mann": BESATZUNG[t], "abstand": d, "spieler": 1, "typ": t, "x": gx, "y": gy})
        einheiten += [{"rolle": "ingenieur", "fall": i, "spieler": 1, "typ": 30, "x": x + j % 2, "y": y + 2 + j // 2 * 2} for j in range(BESATZUNG[t])]
        einheiten.append({"rolle": "ziel", "fall": i, "paar": i, "spieler": 2, "typ": 59, "x": gx + d, "y": gy})
    return {"einheiten": mit_kontrolle(einheiten, frei), "nicht_gefahren": fehlt}


def aufbau_punkt(l):
    """Liste V6, alle 8 zugleich: Bloecke von Speertraegern laufen auf ein freies Feld, greifen ein leeres Tor oder einen Turm an oder muessen durch eine Luecke in der Mauer. Ein Besitzer je Block, die Ziele gehoeren Spieler 2: Kein Beschuss, denn dort steht niemand."""
    from selfaware.game.ucp.bauen import NACH_TYP

    frei, hoehe, _ = l.s.raster()
    faelle = []
    for art, n in PUNKT_FAELLE:
        s = int(np.ceil(np.sqrt(n / 4))) + 1
        faelle.append((art, n, s, s + PUNKT_WEG + 8, max(s + 4, 26)))
    orte = packen(frei, [(b, h) for *_, b, h in faelle], rand=6)
    if any(o is None for o in orte):
        raise Abbruch(f"Nur {sum(o is not None for o in orte)} Plaetze fuer {len(faelle)} Punkte")
    posten, masse, ziele, mauern = [], [], [], []
    for i, ((art, n, s, b, h), (x, y)) in enumerate(zip(faelle, orte)):
        mitte = y + h // 2
        tx, ty = x + s + PUNKT_WEG, mitte
        rest = n
        for j in range(s):
            for m in range(s):
                k = min(4, rest)
                if k:
                    masse.append({"rolle": "masse", "fall": i, "spieler": 1, "typ": 24, "x": x + m, "y": y + (h - s) // 2 + j, "anzahl": k})
                rest -= k
        p = {"fall": i, "art": art, "anzahl": n, "x": x, "y": y, "breite": s + 2, "hoehe": h, "ziel": [tx, ty]}
        if art in ("tor", "turm"):
            typ = 46 if art == "tor" else 74
            z = {"fall": i, "spieler": 2, "typ": typ, "mapper": NACH_TYP[typ]["mapper"], "groesse": NACH_TYP[typ]["b"], "name": NACH_TYP[typ]["laufzeitName"], "x": tx, "y": ty - 2}
            ziele.append(z)
        if art == "luecke":
            wx = x + s + PUNKT_WEG // 2
            p["mauer"] = [wx, y, y + h - 1, mitte]
            mauern += [{"player": 2, "spielbefehl": {"nr": 25, "werte": [wx, y, wx, mitte - 2, 25, 13]}}, {"player": 2, "spielbefehl": {"nr": 25, "werte": [wx, mitte + 2, wx, y + h - 1, 25, 13]}}]
        posten.append(p)
    fehlt = gebaeude_setzen(l, ziele)
    return {"einheiten": masse, "posten": posten, "gebaeude": ziele, "mauern": mauern, "nicht_gesetzt": [z["name"] for z in fehlt]}


def szene_punkt(l):
    """Die Mauern kommen ueber Spielbefehl 25, der nur im laufenden Spiel wirkt, darum zuerst. Dann erst die Einheiten: Wer zu welchem Block gehoert, sagt der Ort."""
    k, s = l.k, l.s
    lk.anhalten(l)
    plan = aufbau_punkt(l)
    if plan["mauern"]:
        k.liste(plan["mauern"], lf.KANAL)
        lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
        l.warte_takte(40)
        lk.anhalten(l)
    plan["mauer_felder"] = len(s.felder_mit_bit(lf.BIT_MAUER)) if hasattr(s, "felder_mit_bit") else None
    setzen_masse(l, plan["einheiten"])
    alle = [e for e in s.einheiten_alle() if e["besitzer"] == 1 and e["typ"] == 24]
    bef = []
    ziele = {z["fall"]: z for z in plan["gebaeude"] if "nr" in z}
    for p in plan["posten"]:
        p["nummern"] = [e["nr"] for e in alle if p["x"] <= e["x"] < p["x"] + p["breite"] and p["y"] <= e["y"] < p["y"] + p["hoehe"]]
        if p["art"] in ("tor", "turm") and p["fall"] in ziele:
            bef.append({"player": 1, "angriff": {"einheiten": p["nummern"], "gebaeude": ziele[p["fall"]]["nr"]}})
        else:
            bef.append({"player": 1, "angriff": {"einheiten": p["nummern"], "lauf": list(p["ziel"])}})
    k.liste(bef, lf.KANAL)
    a = lk.aufnahme_im_stand(l, "punkt", 200, False)
    l.warte_takte(GRENZE_PUNKT)
    b = lk.anhalten(l)
    pfad = l.rek.pfad
    stand = l.rek.beenden()
    with open(pfad + ".plan.json", "w", encoding="utf-8") as f:
        json.dump({"szene": "punkt", "von": a, "bis": b, "tempo": 200, **plan}, f, ensure_ascii=False)
    abr = abraeumen(l)
    return {"szene": "punkt", "von": a, "bis": b, "bloecke": [len(p["nummern"]) for p in plan["posten"]], "mauer_felder": plan["mauer_felder"], "nicht_gesetzt": plan["nicht_gesetzt"], "abraeumen_takte": abr, "stand": stand, "pfad": pfad}


def _g(typ, x, y, spieler=2, **f):
    from selfaware.game.ucp.bauen import NACH_TYP
    return {"spieler": spieler, "typ": typ, "mapper": NACH_TYP[typ]["mapper"], "groesse": NACH_TYP[typ]["b"], "name": NACH_TYP[typ]["laufzeitName"], "x": x, "y": y, **f}


def _e(rolle, typ, x, y, spieler=1):
    return {"rolle": rolle, "typ": typ, "x": x, "y": y, "spieler": spieler}


def _ing(x, y, n):
    return [_e("ingenieur", 30, x + j % 2, y + j // 2) for j in range(n)]


def _angriff(wer, spieler=1, **f):
    return {"player": spieler, "angriff": {"einheiten": [e["nr"] for e in wer], **f}}


def _grabenplan(x, y):
    return [{"player": 1, "spielbefehl": {"nr": 21, "werte": [x, y, 0, 0x40000000, 0]}}]  # L126: Flag 2 = 0 plant, 2 wuerde sofort ausheben


def _leiter_an(s, trag, x, y):
    return _angriff(trag, art=24, a=s.kachel(x, y), b=0)  # die Feldnummer der Mauer, nicht x und y


# Die Posten der Liste V7. Jeder: Breite, Hoehe, und eine Funktion (x, y) -> Gebaeude, Einheiten, Befehle davor (Spielbefehle), Befehle(nachher), Befehle nach dem Einsteigen
def p_feuer(x, y):
    g = [_g(1, x + 10, y + 2), _g(1, x + 15, y + 2)]
    ft, opfer = _e("taeter", 76, x + 1, y + 4), _e("opfer", 25, x + 12, y + 8, 2)
    return g, [ft, opfer], [], lambda: [_angriff([ft], gebaeude=g[0]["nr"])] if "nr" in g[0] else [], None


def p_pech(x, y):
    g = [_g(68, x + 10 + i, y + 4) for i in range(5)]
    ft, opfer = _e("taeter", 76, x + 4, y + 4), _e("opfer", 25, x + 12, y + 4, 2)
    return g, [ft, opfer], [], lambda: [_angriff([ft], ziel=opfer["nr"])], None


def p_mordloch(x, y):
    g = [_g(67, x + 10 + i, y + 3) for i in range(3)]
    wer = _e("opfer", 25, x + 2, y + 3)
    return g, [wer], [], lambda: [_angriff([wer], lauf=[x + 20, y + 3])], None


def p_hunde(x, y):
    g = [_g(99, x + 2, y + 2, spieler=1)]
    opfer = [_e("opfer", 24, x + 12, y + 3 + i, 2) for i in range(3)]
    return g, opfer, [], lambda: [{"player": 1, "spielbefehl": {"nr": 74, "werte": [g[0]["nr"], g[0]["uid"]]}}] if "nr" in g[0] else [], None


def p_kuh(x, y):
    t = dict(_e("geraet", 40, x + 4, y + 4), mann=3, soll=3)
    leute = _ing(x, y + 2, 3)
    opfer = [_e("opfer", 25, x + 28, y + 3, 2), _e("opfer", 25, x + 28, y + 5, 2)]
    return [], [t] + leute + opfer, [], lambda: [_angriff(leute, art=16, a=t["nr"], b=t["uid"])], lambda: [_angriff([t], art=22, a=x + 28, b=y + 4)]


def p_graben(x, y):
    sklaven = [_e("graeber", 71, x + 2 + i, y + 4) for i in range(3)]
    plan = [{"player": 1, "spielbefehl": {"nr": 21, "werte": [x + 10 + i, y + 4, 0, 0x40000000, 2]}} for i in range(3)]
    return [], sklaven, plan, lambda: [_angriff(sklaven, art=6, a=x + 10, b=y + 4)], None


def p_leiter(x, y):
    mauer = [{"player": 2, "spielbefehl": {"nr": 25, "werte": [x + 20, y, x + 20, y + 15, 25, 13]}}]
    leiter = [_e("leiter", 29, x + 8, y + 6), _e("leiter", 29, x + 8, y + 8)]
    speer = [_e("steiger", 24, x + 4, y + 6 + i) for i in range(3)]
    return [], leiter + speer, mauer, lambda: [_angriff(leiter, art=24, a=x + 20, b=y + 7), _angriff(speer, lauf=[x + 20, y + 7])], None


def p_turmgeraet(x, y):
    mauer = [{"player": 2, "spielbefehl": {"nr": 25, "werte": [x + 20, y, x + 20, y + 11, 25, 13]}}]
    t = dict(_e("geraet", 58, x + 4, y + 6), mann=4, soll=4)
    leute = _ing(x, y + 4, 4)
    return [], [t] + leute, mauer, lambda: [_angriff(leute, art=16, a=t["nr"], b=t["uid"])], lambda: [_angriff([t], lauf=[x + 19, y + 6])]


def p_tunnel(x, y):
    g = [_g(1, x + 22, y + 3)]
    wer = [_e("taeter", 5, x + 2, y + 3 + i) for i in range(3)]
    return g, wer, [], lambda: [_angriff(wer, gebaeude=g[0]["nr"])] if "nr" in g[0] else [], None


def p_schild(x, y):
    s_ = dict(_e("geraet", 60, x + 8, y + 3), mann=1, soll=1)
    leute = _ing(x + 6, y, 1)
    hinten, offen = _e("hinter_schild", 25, x + 4, y + 3), _e("ohne_schild", 25, x + 4, y + 7)
    a = [_e("schuetze", 22, x + 28, y + 2 + i, 2) for i in range(2)]
    b = [_e("schuetze", 22, x + 28, y + 6 + i, 2) for i in range(2)]
    return [], [s_] + leute + [hinten, offen] + a + b, [], lambda: [_angriff(leute, art=16, a=s_["nr"], b=s_["uid"])], lambda: [_angriff(a, 2, ziel=hinten["nr"]), _angriff(b, 2, ziel=offen["nr"])]


def p_hoehe(x, y):
    """Schuetzen auf der Mauer: Auf einen einzelnen Turm fanden sie im Editor keinen Weg (Lauf 20:50), darum Treppe und Mauer. Am Boden reicht der Pfeil bis 40 Felder."""
    mauer = [{"player": 1, "spielbefehl": {"nr": 25, "werte": [x + 3, y + 3, x + 9, y + 3, 25, 13]}}, {"player": 1, "spielbefehl": {"nr": 25, "werte": [x + 2, y + 3, x + 2, y + 3, 27, 13]}}]
    wer = [_e("schuetze", 22, x, y + 2 + i) for i in range(3)]
    ziele = [_e("ziel", 59, x + 6 + d, y + 3, 2) for d in (38, 42, 46)]
    return [], wer + ziele, mauer, lambda: [_angriff(wer, lauf=[x + 6, y + 3])], lambda: [_angriff([w], ziel=z["nr"]) for w, z in zip(wer, ziele)]


def p_tor(x, y):
    g = [_g(46, x + 10, y + 2, spieler=1)]
    feind = [_e("feind", 24, x + 24, y + 4 + i, 2) for i in range(2)]
    return g, feind, [], lambda: ([{"player": 1, "spielbefehl": {"nr": 45, "werte": [g[0]["nr"], 1, g[0]["uid"]]}}] if "nr" in g[0] else []) + [_angriff(feind, 2, lauf=[x + 4, y + 4])], None


def p_oel(x, y):
    """Ein Ingenieur holt Oel erst in der Oelschmelze (Anweisung 15, Code giveTribeAnInstruction), ohne sie blieb er stehen (Lauf 20:50)."""
    g = [_g(28, x + 6, y + 1, spieler=1)]
    leute = [_e("oel", 30, x + 2, y + 3 + i) for i in range(2)]
    opfer = _e("opfer", 24, x + 18, y + 3, 2)
    return g, leute + [opfer], [], lambda: [_angriff(leute, art=15, a=g[0]["nr"], b=g[0]["uid"])] if "nr" in g[0] else [], lambda: [_angriff(leute, art=20, a=x + 18, b=y + 3)]


SONDER1 = (("feuer", p_feuer, 24, 12), ("pech", p_pech, 24, 8), ("mordloch", p_mordloch, 24, 6), ("hunde", p_hunde, 20, 8), ("kuh", p_kuh, 36, 8), ("graben", p_graben, 24, 8))
def sonder_g2(l):
    """Die Sonderfaelle, die im ersten Durchgang nicht erreicht wurden, jeder mit dem, was der Code verlangt (Ergebnis_Lauf_S.md). Kuh-Zaehler und Pech in der Schmelze werden gesetzt: Das ist ein Messlauf, nichts davon geht in SamurAI."""
    s = l.s

    def graben(x, y):
        wer = [_e("graeber", 71, x + 2 + i, y + 4) for i in range(3)]
        fueller = [_e("fueller", 71, x + 34, y + 3 + i, 2) for i in range(2)]  # so weit weg, dass sie nicht schon beim Graben kaempfen (Lauf 21:30)
        plan = _grabenplan(x + 11, y + 4)
        return [], wer + fueller, plan, lambda: [_angriff(wer, art=6, a=x + 11, b=y + 4)], [(1000, lambda: [_angriff(wer, lauf=[x + 1, y + 1])]), (1500, lambda: [_angriff(fueller, 2, art=7, a=x + 11, b=y + 4)])], [(x + 10 + i, y + 3 + j) for i in range(3) for j in range(3)]  # bei 1000 gehen die Graeber weg: Sonst erschlagen sie die Zuschuetter (Lauf 23:06, 9 Felder fertig bei 901)

    def leiter(x, y):
        mauer = [{"player": 2, "spielbefehl": {"nr": 25, "werte": [x + 20, y, x + 20, y + 15, 25, 13]}}]
        trag = [_e("leiter", 29, x + 8, y + 6), _e("leiter", 29, x + 8, y + 8)]
        speer = [_e("steiger", 24, x + 4, y + 6 + i) for i in range(3)]
        return [], trag + speer, mauer, lambda: [_leiter_an(s, trag, x + 20, y + 7)], [(500, lambda: [_angriff(speer, lauf=[x + 20, y + 7])])]

    def kuh(x, y):
        adr, schritt = s.feld("DAT_GameState", "playerDataArray[].counter")
        t = dict(_e("geraet", 40, x + 4, y + 4), mann=3, soll=3)
        leute = _ing(x, y + 2, 3)
        opfer = [_e("opfer", 25, x + 28, y + 3, 2), _e("opfer", 25, x + 28, y + 5, 2)]
        return [], [t] + leute + opfer, [], lambda: [_angriff(leute, art=16, a=t["nr"], b=t["uid"])], lambda: [{"poke": adr + schritt, "wert": 5}, _angriff([t], art=22, a=x + 28, b=y + 4)]

    def hunde(x, y):
        g = [_g(99, x + 2, y + 2, spieler=1)]
        opfer = [_e("opfer", 24, x + 8, y + 2 + i, 2) for i in range(3)]
        return g, opfer, [], lambda: [{"player": 1, "spielbefehl": {"nr": 74, "werte": [g[0]["nr"], g[0]["uid"]]}}] if "nr" in g[0] else [], None

    def pech(x, y):
        baue = [{"player": 2, "baue": {"mapper": 99, "x": x + 10 + i, "y": y + 4, "groesse": 1, "richtung": 15}} for i in range(5)]
        schuetze = _e("schuetze", 22, x + 30, y + 2, 2)
        opfer = _e("opfer", 25, x + 2, y + 4)

        def anzuenden():
            nah = [d for d in s.pech_liste(2) if abs(d["y"] - (y + 4)) <= 1 and x + 8 <= d["x"] <= x + 16]
            return [_angriff([schuetze], 2, art=34, a=nah[len(nah) // 2]["nr"], b=nah[len(nah) // 2]["uid"])] if nah else []
        return [], [schuetze, opfer], baue, lambda: [_angriff([opfer], lauf=[x + 13, y + 4])], [(200, anzuenden)]

    def oel(x, y):
        g = [_g(28, x + 6, y + 1, spieler=1)]
        adr, schritt = s.feld("DAT_BuildingsState", "buildings[].resourcePitch")
        leute = [_e("oel", 30, x + 2, y + 3 + i) for i in range(2)]
        opfer = _e("opfer", 24, x + 18, y + 3, 2)

        def holen():
            return [{"poke": adr + schritt * g[0]["nr"], "wert": 20}, _angriff(leute, art=15, a=g[0]["nr"], b=g[0]["uid"])] if "nr" in g[0] else []
        def werfen():
            return [_angriff([w], art=20, a=x + 18, b=y + 3) for w in leute]  # einzeln: Als Gruppe traf der Befehl nur den, der noch kein Oel hatte (Lauf 21:30)

        def hingehen():
            return [_angriff([w], lauf=[x + 14, y + 3 + i]) for i, w in enumerate(leute)]
        return g, leute + [opfer], [], holen, [(800, werfen), (1800, hingehen), (2400, werfen)]

    def tunnel(x, y):
        g = [_g(74, x + 22, y + 2)]
        mauer = [{"player": 2, "spielbefehl": {"nr": 25, "werte": [x + 24, y + 9, x + 24, y + 14, 25, 13]}}]
        wer = [_e("taeter", 5, x + 2, y + 2 + i) for i in range(3)]
        wand = [_e("taeter_mauer", 5, x + 2, y + 10 + i) for i in range(3)]
        return g, wer + wand, mauer, lambda: ([_angriff(wer, gebaeude=g[0]["nr"])] if "nr" in g[0] else []) + [_angriff(wand, art=23, a=s.kachel(x + 24, y + 11), b=0)], None

    return (("graben", graben, 40, 8), ("leiter", leiter, 30, 16), ("kuh", kuh, 36, 8), ("hunde", hunde, 20, 8), ("pech", pech, 34, 8), ("oel", oel, 24, 8), ("tunnel", tunnel, 30, 16))


def burgbereich(l, sp=1, innen=14, aussen=40):
    """Burgbauten (Mauer, Graben, Pechgraben, Kaefig, Turm) gehen im Gefecht nur nahe der eigenen Burg (checkBuildingCanBePlacedHere: getCastleBuildRangeForMapSize, probe_burgbereich.txt). Innen 14 Felder Abstand zum Lord, damit er nicht eingreift."""
    lord = next(e for e in l.s.einheiten_alle() if e["typ"] == 55 and e["besitzer"] == sp)

    def maske(frei):
        ys, xs = np.indices(frei.shape)
        d = np.maximum(np.abs(xs - lord["x"]), np.abs(ys - lord["y"]))
        return frei & (d >= innen) & (d <= aussen)
    return maske


def sonder3(l):
    """Im Editor gilt der Burgbereich nicht: Leiter, Belagerungsturm, Tunnel, Tor und Schuetzen auf der Mauer."""
    d = {z[0]: z for z in sonder_g2(l)}

    def hoehe(x, y):
        """Im ersten Durchgang stand die Mauer nicht (Burgbereich), die Treffer auf 42 und 46 Felder sagten also nichts."""
        mauer = [{"player": 1, "spielbefehl": {"nr": 25, "werte": [x + 3, y + 3, x + 9, y + 3, 25, 13]}}, {"player": 1, "spielbefehl": {"nr": 25, "werte": [x + 2, y + 3, x + 2, y + 3, 27, 13]}}]
        wer = [dict(_e("laeufer", 22, x, y + i), paar=i, abstand=a) for i, a in enumerate((38, 42, 46, 50))]
        ziele = [dict(_e("ziel", 59, x + 6 + a, y + 1 + 2 * i, 2), paar=i) for i, a in enumerate((38, 42, 46, 50))]
        return [], wer + ziele, mauer, lambda: [_angriff(wer, lauf=[x + 6, y + 3])], [(400, lambda: [_angriff([w], ziel=z["nr"]) for w, z in zip(wer, ziele)])], [(x + 6, y + 3), (x + 2, y + 3)]
    return (d["leiter"], ("turmgeraet", p_turmgeraet, 30, 12), d["tunnel"], ("hoehe", hoehe, 64, 10), ("tor", p_tor, 30, 10))


def sonder3_g(l):
    """Im Gefecht und im Burgbereich von Spieler 1: Graben und Hunde. Zuschuetten geht nur beim Graben eines anderen Teams (findNearestFriendlyMoatTileForDigging, Stufe 2): Eigene Sklaven taten nichts (Lauf 21:41), darum schuettet Spieler 2 zu."""
    d = {z[0]: z for z in sonder_g2(l)}

    def hunde(x, y):
        """Die Hunde kommen von selbst, wenn mehr als 5 Feinde oder Truppenwert ueber 24 binnen 16 Schritten stehen (UpdateCageDog). 3 Speertraeger reichten nicht (Lauf 23:06). Ohne Befehl 74: Der setzt 4 weitere Hunde in den Kaefig, die dort feststecken."""
        g = [_g(99, x + 2, y + 2, spieler=1)]
        opfer = [_e("opfer", 24, x + 8 + i % 2, y + 1 + i // 2, 2) for i in range(8)]
        return g, opfer, [], lambda: [], None
    return (d["graben"], ("hunde", hunde, 20, 8))


def sonder4_g(l):
    """Pechgraben von Spieler 1 im Burgbereich, sein Bogenschuetze zuendet ihn an, ein Pikenier von Spieler 2 steht darauf. Allein, weil der Schuetze sonst auf alles schiesst."""
    s = l.s

    def pech(x, y):
        baue = [{"player": 1, "baue": {"mapper": 99, "x": x + 10 + i, "y": y + 4, "groesse": 1, "richtung": 15}} for i in range(5)]
        schuetze = _e("schuetze", 22, x + 12, y + 1)
        opfer = _e("opfer", 25, x + 2, y + 4, 2)

        def anzuenden():
            nah = [g for g in s.pech_liste(1) if abs(g["y"] - (y + 4)) <= 1 and x + 8 <= g["x"] <= x + 16]
            return [_angriff([schuetze], art=34, a=nah[len(nah) // 2]["nr"], b=nah[len(nah) // 2]["uid"])] if nah else []
        return [], [schuetze, opfer], baue, lambda: [_angriff([opfer], 2, lauf=[x + 12, y + 4])], [(250, anzuenden)]
    return (("pech", pech, 24, 8),)


def sonder5(l):
    """Hoehe: Bogenschuetzen steigen ueber eine Leiter wirklich auf die Mauer (Speertraeger kamen so auf Hoehe 98, Lauf 21:50), dann Befehl auf Rammen jenseits der 40 Felder, die am Boden gelten."""
    s = l.s

    def hoehe(x, y):
        mauer = [{"player": 2, "spielbefehl": {"nr": 25, "werte": [x + 20, y, x + 20, y + 15, 25, 13]}}]
        trag = [_e("leiter", 29, x + 8, y + 6), _e("leiter", 29, x + 8, y + 8)]
        wer = [dict(_e("laeufer", 22, x + 4, y + 5 + i), paar=i, abstand=a) for i, a in enumerate((38, 42, 46, 50))]
        ziele = [dict(_e("ziel", 59, x + 20 + a, y + 1 + 4 * i, 2), paar=i) for i, a in enumerate((38, 42, 46, 50))]
        return [], trag + wer + ziele, mauer, lambda: [_leiter_an(s, trag, x + 20, y + 7)], [(500, lambda: [_angriff(wer, lauf=[x + 20, y + 7])]), (1500, lambda: [_angriff([w], ziel=z["nr"]) for w, z in zip(wer, ziele)])]
    return (("hoehe", hoehe, 74, 16),)


def sonder5_g(l):
    """Pechgraben, Versuch 2: Der Bogenschuetze zuendete ihn nicht an (Lauf 21:50, Anweisung 34 angenommen, nur normale Pfeile). Jetzt ein Feuerwerfer auf den Gegner, der auf dem Graben steht."""
    def pech(x, y):
        baue = [{"player": 1, "baue": {"mapper": 99, "x": x + 10 + i, "y": y + 4, "groesse": 1, "richtung": 15}} for i in range(5)]
        ft = _e("taeter", 76, x + 12, y + 1)
        opfer = _e("opfer", 25, x + 2, y + 4, 2)
        return [], [ft, opfer], baue, lambda: [_angriff([opfer], 2, lauf=[x + 12, y + 4])], [(300, lambda: [_angriff([ft], ziel=opfer["nr"])])]
    return (("pech", pech, 24, 8),)


MAPPER_TUNNEL, EINGANG = 66, (85, 50)  # M_MAPPER_TUNNEL_CONSTRUCTION, Groesse 3; BT_UNKNOWN4 bis der Graeber da ist, dann BT_TUNNEL
TUNNEL_TRUPP, TUNNEL_PRUEFEN, TUNNEL_STOEREN = 60, 120, 1100  # Takte: Der Trupp entsteht erst mit dem ersten Befehl; der Eingang steht spaetestens im naechsten Takt, 60 sind reichlich; der Graeber grub ab Takt 1001 und 1012 (Lauf 22:41)


def sonder6_g(l):
    """Tunnel wie beim Menschen: Bauen mit Mapper 66, Groesse 3 und dem Trupp des Graebers (ClickPlaceBuilding), setupBuildingData gibt dem Trupp Anweisung 21. Das Spiel erlaubt den Eingang nur mit feindlicher Mauer oder kleinem Turm (Art 74 bis 76) binnen 76 Schritten (algTunnelerFindTarget, probe_tunnel.txt: ohne beides nirgends). Im Burgbereich von Spieler 2, weil nur dort seine Mauer und sein Turm stehen."""
    s = l.s

    def eingang_bauen(wer, x, y):
        def f():
            ort = erlaubte_stelle(l, {"mapper": MAPPER_TUNNEL, "groesse": 3, "x": x, "y": y, "spieler": 1})
            trupp = {e["nr"]: e["trupp"] for e in s.einheiten_alle()}.get(wer[0]["nr"], 0)
            return [{"player": 1, "baue": {"mapper": MAPPER_TUNNEL, "x": ort[0], "y": ort[1], "groesse": 3, "richtung": 15, "trupp": trupp}}] if ort and trupp else []
        return f

    def eingang_da():
        if not any(g["typ"] in EINGANG for g in s.gebaeude(None)):
            raise Abbruch("Tunnel: Kein Eingang steht, der Lauf beweist nichts")
        return []

    def mauer(x, y):
        wer = [_e("taeter", 5, x + 2, y + 5), _e("reserve", 5, x + 2, y + 8)]  # je Eingang geht einer (giveTribeAnInstruction), der zweite bleibt
        wand = [{"player": 2, "spielbefehl": {"nr": 25, "werte": [x + 20, y, x + 20, y + 13, 25, 13]}}]
        return [], wer, wand, lambda: [_angriff(wer, lauf=[x + 2, y + 6])], [(TUNNEL_TRUPP, eingang_bauen(wer, x + 8, y + 5)), (TUNNEL_PRUEFEN, eingang_da)], [(x + 20, y + i) for i in range(14)]

    def turm(x, y):
        wer = [_e("taeter", 5, x + 2, y + 4)]
        return [_g(74, x + 20, y + 3)], wer, [], lambda: [_angriff(wer, lauf=[x + 2, y + 4])], [(TUNNEL_TRUPP, eingang_bauen(wer, x + 8, y + 4))]

    def weit(x, y):
        """Weiter als die ersten 20 Felder der Zielsuche (findTunnelTarget: 20, 40, 80)."""
        wer = [_e("taeter", 5, x + 2, y + 4)]
        return [_g(74, x + 38, y + 3)], wer, [], lambda: [_angriff(wer, lauf=[x + 2, y + 4])], [(TUNNEL_TRUPP, eingang_bauen(wer, x + 8, y + 4))]

    def abbruch(x, y):
        """Der Gegner schlaegt den Eingang, waehrend gegraben wird (processDamageToBuilding, BT_TUNNEL)."""
        wer = [_e("taeter", 5, x + 2, y + 4)]
        st = _e("stoerer", 24, x + 20, y + 10, 2)  # 9 Felder vom Graeber: Auf 5 griff er ihn von selbst an (Lauf 22:41)

        def stoeren():
            g = next((g for g in s.gebaeude(None) if g["typ"] in EINGANG and abs(g["x"] - (x + 8)) <= 8 and abs(g["y"] - (y + 4)) <= 8), None)
            return [_angriff([st], 2, gebaeude=g["nr"])] if g else []
        return [_g(74, x + 22, y + 3)], wer + [st], [], lambda: [_angriff(wer, lauf=[x + 2, y + 4])], [(TUNNEL_TRUPP, eingang_bauen(wer, x + 8, y + 4)), (TUNNEL_STOEREN, stoeren)]
    return (("weit", weit, 44, 10), ("mauer", mauer, 26, 14), ("turm", turm, 26, 10), ("abbruch", abbruch, 28, 12))  # der breiteste zuerst, sonst passt der Ring um die Burg nicht


MAUER_ARTEN = (24, 25, 26, 27, 28, 71, 73, 75)  # Speer, Pike, Keule, Schwert, Ritter, Sklave, Assassine, arabisches Schwert: P353 bis P357, P366 bis P368
STEIN_MENGE, STEIN_TAKTE = 200, (1700, 1760, 1820)  # ware haelt nicht lange (2000 auf 0 bei Takt 100), startResources wurde nicht abgeholt (punkte_rechnung7.txt). Darum kurz vor dem Bedarf: Der 10. Schuss fiel bei Takt 1709
NACH_FUELLEN, OEL_HALTUNG, OEL_FEIND = 800, 500, 600  # Takte: Das Oel war bei 350 da (Lauf 21:35)
LORD_SELBST = 6000  # Takte: Niemand hilft nach, 8 Ritter schlagen, bis der Lord faellt


def steigung(frei, hoehe, laenge=14, mindestens=8):
    """Die erste Zeile, die ueber laenge Felder frei ist und nur ansteigt, um mindestens so viel. P330 braucht bergauf. Rueckgabe (x, y) des unteren Endes oder None."""
    w = np.lib.stride_tricks.sliding_window_view
    fr = w(frei, laenge, axis=1).all(axis=-1)
    st = w(np.diff(hoehe, axis=1) >= 0, laenge - 1, axis=1).all(axis=-1)
    m = fr & st & (hoehe[:, laenge - 1:] - hoehe[:, :-(laenge - 1)] >= mindestens)
    ys, xs = np.nonzero(m)
    return (int(xs[0]), int(ys[0])) if len(ys) else None


def sonder8(l):
    """Die Lagen, die in Lauf S fehlten (Punkte_Lauf_S.md), im Editor: Dort gilt der Burgbereich nicht, und Spieler 2 tut nichts von selbst."""
    s = l.s
    frei, hoehe, _ = s.raster()
    hang = steigung(frei, hoehe)

    def vorbei(x, y):
        """P352, P371: Armbrust mit und ohne Haltung stehen, berittener Bogenschuetze laufen an einem Feind vorbei."""
        wer = [_e("laeufer", 23, x + 1, y + 1), _e("steher", 23, x + 1, y + 3), _e("reiter", 74, x + 1, y + 5)]
        feind = _e("feind", 25, x + 18, y + 11, 2)

        def stehen():
            trupp = {e["nr"]: e["trupp"] for e in s.einheiten_alle()}.get(wer[1]["nr"], 0)
            return [{"player": 1, "spielbefehl": {"nr": 70, "werte": [trupp, 0]}}] if trupp else []
        return [], wer + [feind], [], lambda: [_angriff([w], lauf=[x + 34, y + 1 + 2 * i]) for i, w in enumerate(wer)], [(20, stehen)]

    def mauer_art(x, y):
        """Je Art 5 Mauerstuecke, Ziel das mittlere (2 Nachbarn). Dazu ein Kreuz: Das Feld dort hat 3 Nachbarn (P322)."""
        wer, wand, ziele = [], [], []
        for i, typ in enumerate(MAUER_ARTEN):
            cx, cy = x + 10 * (i % 4), y + 8 * (i // 4)
            wand.append({"player": 2, "spielbefehl": {"nr": 25, "werte": [cx + 6, cy, cx + 6, cy + 5, 25, 13]}})
            wer.append(_e("taeter", typ, cx + 1, cy + 2))
            ziele.append((cx + 6, cy + 2))
        cx, cy = x, y + 16
        wand.append({"player": 2, "spielbefehl": {"nr": 25, "werte": [cx + 6, cy, cx + 6, cy + 7, 25, 13]}})
        wand.append({"player": 2, "spielbefehl": {"nr": 25, "werte": [cx + 7, cy + 3, cx + 12, cy + 3, 25, 13]}})
        wer.append(_e("kreuz", 25, cx + 1, cy + 3))
        ziele.append((cx + 6, cy + 3))
        return [], wer, wand, lambda: [_angriff([w], art=23, a=s.kachel(fx, fy), b=0) for w, (fx, fy) in zip(wer, ziele)], None, ziele

    def turm_oben(x, y):
        """P338: 8 Leute auf einen Wachturm, die Obergrenze soll 5 sein."""
        wer = [_e("steiger", 24, x + 1, y + i) for i in range(8)]
        return [_g(74, x + 12, y + 2, spieler=1)], wer, [], lambda: [_angriff([w], lauf=[x + 13, y + 3]) for w in wer], None

    def turm4(x, y):
        """P302: Einer auf die Grundflaeche des grossen Turms, spaeter wieder herunter."""
        wer = [_e("steiger", 24, x + 1, y + 3)]
        return [_g(77, x + 12, y + 1, spieler=1)], wer, [], lambda: [_angriff(wer, lauf=[x + 14, y + 3])], [(1500, lambda: [_angriff(wer, lauf=[x + 1, y + 3])])]

    def tor_vor(abstand):
        """P303, P304: Der Feind steht 24 oder 26 Felder vor dem Tor (Code: unter 200 Mikro) und geht spaeter weg."""
        def f(x, y):
            feind = [_e("feind", 24, x + 30 - abstand, y + 4)]
            return [_g(46, x + 30, y + 2)], feind, [], lambda: [], [(1500, lambda: [_angriff(feind, lauf=[x, y + 4])])]
        return f

    def tor_feld(x, y):
        """P303: Der Feind geht auf die Torfelder."""
        feind = [_e("feind", 24, x + 3, y + 4)]
        return [_g(46, x + 6, y + 2)], feind, [], lambda: [_angriff(feind, lauf=[x + 8, y + 4])], None

    def trupp_frei(x, y):
        """P326: 6 Schwertkaempfer auf ein freies Feld. Die Zielfelder gleich nach dem Befehl."""
        wer = [_e("trupp", 27, x + 1 + 2 * (i % 3), y + 1 + 2 * (i // 3)) for i in range(6)]
        return [], wer, [], lambda: [_angriff(wer, lauf=[x + 24, y + 3])], None

    def trupp_kampf(x, y):
        """P325: Einer steht in Reichweite eines Feindes (2 Felder), die anderen nicht. Der Marschbefehl kommt, wenn er kaempft."""
        wer = [_e("trupp", 27, x + 1 + 3 * i, y + 2) for i in range(6)]
        feind = _e("feind", 25, x + 1, y + 4, 2)
        return [], wer + [feind], [], lambda: [], [(150, lambda: [_angriff(wer, lauf=[x + 30, y + 2])])]

    def unerreichbar(x, y):
        """P343: Das Ziel liegt in einem geschlossenen Mauerring."""
        ring = [[x + 10, y, x + 19, y], [x + 10, y + 8, x + 19, y + 8], [x + 10, y + 1, x + 10, y + 8], [x + 18, y + 1, x + 18, y + 8]]
        wer = [_e("laeufer", 24, x + 2, y + 4)]
        return [], wer, [{"player": 2, "spielbefehl": {"nr": 25, "werte": r + [25, 13]}} for r in ring], lambda: [_angriff(wer, lauf=[x + 14, y + 4])], None

    def bergauf(x, y):
        """P330: bergauf. Der Ort kommt von der Karte, nicht vom Packen."""
        if hang is None:
            return [], [], [], lambda: [], None
        wer = [_e("laeufer", 24, hang[0], hang[1])]
        return [], wer, [], lambda: [_angriff(wer, lauf=[hang[0] + 13, hang[1]])], None

    def ramme(x, y):
        """P328, P345: 4 Rammen mit 1, 2, 3 und 4 Mann, Gebaeudeangriff auf ein Tor, das viele Treffer aushaelt."""
        tor = [_g(46, x + 30, y + 8)]
        paare = []
        for i, n in enumerate((1, 2, 3, 4)):
            paare.append((dict(_e("geraet", 59, x + 6, y + 1 + 5 * i), mann=n, soll=4), _ing(x, y + 5 * i, n)))
        return tor, [e for r, m in paare for e in [r] + m], [], lambda: [_angriff(m, art=16, a=r["nr"], b=r["uid"]) for r, m in paare], [(SONDER_BEMANNEN, lambda: [_angriff([r], gebaeude=tor[0]["nr"]) for r, _ in paare] if "nr" in tor[0] else [])]

    def turmgeraet(x, y):
        """P344: Belagerungsturm mit Anweisung 23 an die Mauer. Ein Laufbefehl haelt nur davor (Lauf 21:42, UpdateSiegeTower)."""
        mauer = [{"player": 2, "spielbefehl": {"nr": 25, "werte": [x + 20, y, x + 20, y + 11, 25, 13]}}]
        t = dict(_e("geraet", 58, x + 4, y + 6), mann=4, soll=4)
        leute = _ing(x, y + 4, 4)
        return [], [t] + leute, mauer, lambda: [_angriff(leute, art=16, a=t["nr"], b=t["uid"])], [(SONDER_BEMANNEN, lambda: [_angriff([t], art=23, a=s.kachel(x + 20, y + 6), b=0)])]

    return (("vorbei", vorbei, 36, 13), ("mauer_art", mauer_art, 40, 24), ("ramme", ramme, 38, 22), ("turmgeraet", turmgeraet, 30, 12), ("tor_24", tor_vor(24), 36, 8), ("tor_26", tor_vor(26), 36, 8), ("tor_feld", tor_feld, 14, 8), ("turm_oben", turm_oben, 18, 8), ("turm4", turm4, 20, 8), ("trupp_frei", trupp_frei, 28, 6), ("unerreichbar", unerreichbar, 20, 9), ("bergauf", bergauf, 2, 2), ("trupp_kampf", trupp_kampf, 32, 6))


def sonder8_g(l):
    """Lagen, die Waren brauchen oder die echten Regeln des Gefechts: Nachladen mit Stein, Oel und Haltung, die Grenze um das Lager."""
    s = l.s

    def nachladen(x, y):
        """P308: Ein Katapult schiesst seine 10 Steine, dann soll es selbst nachladen. P309: Ein zweites bekommt den Befehl zum Auffuellen (Spielbefehl 86)."""
        def stein():
            return [{"player": 1, "ware": {"typ": 4, "menge": STEIN_MENGE}}]
        a, b = dict(_e("geraet", 39, x + 4, y + 2), mann=2, soll=2), dict(_e("geraet", 39, x + 4, y + 10), mann=2, soll=2)
        la, lb = _ing(x, y + 1, 2), _ing(x, y + 9, 2)
        ziel = _e("ziel", 25, x + 28, y + 2, 2)

        def schiessen():
            return [_angriff([a], ziel=ziel["nr"]), _angriff([b], lauf=[x + 4, y + 10])]  # der Laufbefehl macht den Trupp fuer Spielbefehl 86

        def auffuellen():
            trupp = {e["nr"]: e["trupp"] for e in s.einheiten_alle()}.get(b["nr"], 0)
            return [{"player": 1, "spielbefehl": {"nr": 86, "werte": [trupp, 0]}}] if trupp else []
        return [], [a, b] + la + lb + [ziel], [], lambda: [_angriff(la, art=16, a=a["nr"], b=a["uid"]), _angriff(lb, art=16, a=b["nr"], b=b["uid"])], [(SONDER_BEMANNEN, schiessen), (NACH_FUELLEN, lambda: stein() + auffuellen())] + [(t, stein) for t in STEIN_TAKTE]

    def oel(wert):
        """P323: Ingenieur mit Oel, ein Feind kommt nahe. Code: Nur die Haltung stehen wirft nicht (ifNecessaryThrowOilAutomatically)."""
        def f(x, y):
            g = [_g(28, x + 6, y + 1, spieler=1)]
            adr, schritt = s.feld("DAT_BuildingsState", "buildings[].resourcePitch")
            leute = [_e("oel", 30, x + 2, y + 3 + i) for i in range(2)]  # einer bedient die Schmelze, einer traegt: Allein hatte keiner Oel (Lauf 00:40)
            feind = _e("feind", 24, x + 22, y + 3, 2)

            def jetzt():
                return {e["nr"]: e for e in s.einheiten_alle()}.get(leute[1]["nr"], {})  # das Oel hat immer der zweite (Lauf 01:02), ohne Trupp bricht der Code ab (Lauf 01:05)

            def trupp_machen():
                e = jetzt()
                return [_angriff([leute[1]], lauf=[e["x"], e["y"]])] if e else []

            def holen():
                return [{"poke": adr + schritt * g[0]["nr"], "wert": 20}, _angriff(leute, art=15, a=g[0]["nr"], b=g[0]["uid"])] if "nr" in g[0] else []

            def haltung():
                return [{"player": 1, "spielbefehl": {"nr": 70, "werte": [jetzt().get("trupp", 0), wert]}}] if jetzt().get("trupp") else []

            def kommen():
                traeger = {e["nr"]: e for e in s.einheiten_alle()}.get(leute[1]["nr"], {})  # das Oel hatte immer der zweite (Lauf 01:02)
                return [_angriff([feind], 2, lauf=[traeger["x"] + 2, traeger["y"]])] if traeger else []  # Code: Umkreis 4 Schritte
            return g, leute + [feind], [], holen, [(OEL_HALTUNG - 60, trupp_machen), (OEL_HALTUNG, haltung), (OEL_FEIND, kommen)]
        return f

    def grenze(x, y):
        """P324: Ein Speertraeger 39 Felder vom Lager, ein Bogenschuetze 41. Code: unter 41 zaehlt. Der Ort kommt vom Lager, nicht vom Packen."""
        ax, sch = s.feld("DAT_GameState", "playerDataArray[].campground.xEntry")
        ay, _ = s.feld("DAT_GameState", "playerDataArray[].campground.yEntry")
        cx, cy = l.k.peek(ax + sch)[0], l.k.peek(ay + sch)[0]
        fern, s.fern = s.fern, 0
        frei = s.raster()[0]
        s.fern = fern
        ys, xs = np.indices(frei.shape)
        d = np.maximum(np.abs(xs - cx), np.abs(ys - cy))
        wer = []
        for abstand, rolle, typ in ((39, "nah", 24), (41, "weit", 22)):
            f = np.argwhere(frei & (d == abstand))
            if len(f):
                wer.append(dict(_e(rolle, typ, int(f[0][1]), int(f[0][0])), abstand=abstand))
        return [], wer, [], lambda: [], None

    return (("nachladen", nachladen, 34, 14), ("oel_aggressiv", oel(2), 28, 7), ("oel_defensiv", oel(1), 28, 7), ("oel_stehen", oel(0), 28, 7), ("grenze", grenze, 2, 2))


def sonder9_g(l):
    """P314: 5 Gegner laufen quer durch den brennenden Pechgraben. Aufbau wie sonder5_g, dort brannte er von Takt 501 bis 729."""
    def pech(x, y):
        baue = [{"player": 1, "baue": {"mapper": 99, "x": x + 10 + i, "y": y + 4, "groesse": 1, "richtung": 15}} for i in range(5)]
        ft = _e("taeter", 76, x + 12, y + 1)
        opfer = _e("opfer", 25, x + 2, y + 4, 2)
        geher = [_e("geher", 24, x + 10 + i, y + 9, 2) for i in range(5)]
        return [], [ft, opfer] + geher, baue, lambda: [_angriff([opfer], 2, lauf=[x + 12, y + 4])], [(300, lambda: [_angriff([ft], ziel=opfer["nr"])]), (510, lambda: [_angriff([g], 2, lauf=[g["x"], y + 2]) for g in geher])]
    return (("pech", pech, 24, 11),)


TREPPE, TOR_ZU_TAKT = 27, 300  # Mapper der Treppe (sonder3); Takte: Das Tor ist nach 3 bis 50 Takten zu (Lauf 00:30)
ANGST_BAUTEN = 5  # Die Stufe ist gut minus schlecht, bei kleiner Bevoelkerung geteilt durch 1, begrenzt auf 5 (recomputeAllFearFactors)
MUNITION_TRUPP, MUNITION_EINHEIT = 1000, 1100  # Takte: Das Katapult schiesst ab Takt 400 alle rund 130 Takte (sonder8_g), bei 1000 ist also noch Munition da, aber nicht mehr voll
VERLUSTE = 0xb98460  # DAT_UnitValueLossesPerEnemyPlayer (UpdateUnitLossData, Maschinencode)
AUFTRAG_ASSASSINE, AUFTRAG_TAKT, AUFTRAG_TOD = 12, 200, 1200  # updateUnits: case 0xc zaehlt totalAssassinTroops
KORB_GOLD, KORB_TAKT, ET_BRAZIER, GM_SIEGE_THAT, GM_GEFECHT_2 = 2000, 300, 14, 6, 3  # Typen: EntityType, GameMode2. Gefecht misst 3 (Protokoll spielart)
RUSH_LAUF, RUSH_SETZEN, RUSH_TAKTE, RUSH_NACH, GM_MEHRSPIELER, GM_EINZEL = 50, 100, 1000, 800, 1, 99  # Takte: Der Weg dauert rund 12 Takte je Feld, 12 Felder also rund 150: Die Einheit kommt an, wenn der Schutz schon gilt
LAUF_NACH_BAU = 300  # Takte: Die Flaechenkarte rechnet das Spiel alle 50 Takte neu (updateSeparateAreaTileMap), ein Vielfaches davon ist sicher
MAUER_VERSUCHE, GEBAEUDE_VERSUCHE = 5, 2  # Wie oft ein abgelehnter Bau neu geschickt wird. Ein Tier geht in 40 Takten weiter, ein Felsen nie


def linie_felder(w):
    """Die Felder einer Linie aus Spielbefehl 25, hoechstens so viele, wie der letzte Wert erlaubt (placeWalls: tileCountUnk)."""
    x0, y0, x1, y1 = w[:4]
    n = max(abs(x1 - x0), abs(y1 - y0))
    return [(x0 + (x1 - x0) * i // max(n, 1), y0 + (y1 - y0) * i // max(n, 1)) for i in range(n + 1)][:w[5]]


def linien_fehlen(s, befehle, boden):
    """Eine Linie baut das Spiel ganz oder gar nicht: Ein belegtes Feld oder eine Einheit darauf genuegt (validateWallBuildPath; sonder12: 2 von 4 Seiten des Rings fehlten und niemand merkte es). Darum nachlesen."""
    _, hoehe, _ = s.raster()
    return [c for c in befehle if c.get("spielbefehl", {}).get("nr") == 25 and any(hoehe[y, x] <= boden[y, x] for x, y in linie_felder(c["spielbefehl"]["werte"]))]


def verluste_lesen(l):
    """P305, P306: Beide Zaehler stehen nicht in der Aufzeichnung (DAT_GameSynchronyState fehlt dort), also direkt aus dem Speicher."""
    adr, _ = l.s.feld("DAT_GameSynchronyState", "finalResults.finalKillMatrix[]")
    return {"kills": l.k.peek(adr, 81), "verlust": l.k.peek(VERLUSTE, 9)}


def sonder10(l):
    """Der zweite Nachlauf im Editor: was im ersten nicht zustande kam (Punkte_Lauf_S.md)."""
    s = l.s
    frei, hoehe, _ = s.raster()
    hang = steigung(frei, hoehe, 8, 3)

    def treppe(x, y, spieler=1):
        return [{"player": spieler, "spielbefehl": {"nr": 25, "werte": [x + 3, y + 3, x + 10, y + 3, 25, 13]}}, {"player": spieler, "spielbefehl": {"nr": 25, "werte": [x + 2, y + 3, x + 2, y + 3, TREPPE, 13]}}]

    def turm_oben(x, y):
        """P338: Ein Laufbefehl vom Boden wirkte nicht (Lauf 00:30). Jetzt mit Treppe und Mauer bis an den Wachturm."""
        wer = [_e("steiger", 24, x, y + i) for i in range(8)]
        return [_g(74, x + 10, y + 2, spieler=1)], wer, treppe(x, y), lambda: [_angriff([w], lauf=[x + 11, y + 3]) for w in wer], None

    def turm4(x, y):
        """P302: Mit Treppe und Mauer auf den grossen Turm, spaeter wieder herunter."""
        wer = [_e("steiger", 24, x, y + 3)]
        return [_g(77, x + 10, y + 1, spieler=1)], wer, treppe(x, y), lambda: [_angriff(wer, lauf=[x + 12, y + 3])], [(1500, lambda: [_angriff(wer, lauf=[x, y + 3])])]

    def tor_weg(x, y):
        """P304: Feind auf 10 Feldern, das Tor schliesst. Er geht weg: Entwarnung."""
        feind = [_e("feind", 24, x + 20, y + 4)]
        return [_g(46, x + 30, y + 2)], feind, [], lambda: [], [(1000, lambda: [_angriff(feind, lauf=[x, y + 4])])]

    def tor_gang(mit_feind):
        """P304: Die eigene Einheit geht durchs Tor, einmal offen, einmal zu. Rechts und links Mauer, sonst geht sie aussen herum."""
        def f(x, y):
            wand = [{"player": 2, "spielbefehl": {"nr": 25, "werte": w + [25, 13]}} for w in ([x, y + 5, x + 10, y + 5], [x + 15, y + 5, x + 26, y + 5])]
            geher = [_e("geher", 24, x + 12, y, 2)]
            feind = [_e("feind", 24, x + 3, y + 10)] if mit_feind else []
            return [_g(46, x + 10, y + 3)], geher + feind, wand, lambda: [], [(TOR_ZU_TAKT, lambda: [_angriff(geher, 2, lauf=[x + 12, y + 11])])]
        return f

    def trupp_nah(x, y):
        """P325: Der erste steht direkt am Feind, der Abstand 2 reichte nicht (Lauf 00:30)."""
        wer = [_e("trupp", 27, x + 1 + 3 * i, y + 2) for i in range(6)]
        feind = _e("feind", 25, x + 1, y + 3, 2)
        return [], wer + [feind], [], lambda: [], [(150, lambda: [_angriff(wer, lauf=[x + 30, y + 2])])]

    def bergauf(x, y):
        """P330: Der erste Lauf fand mit 8 Hoehe auf 14 Felder keinen Hang."""
        if hang is None:
            return [], [], [], lambda: [], None
        wer = [_e("laeufer", 24, hang[0], hang[1])]
        return [], wer, [], lambda: [_angriff(wer, lauf=[hang[0] + 7, hang[1]])], None

    return (("turm_oben", turm_oben, 18, 9), ("turm4", turm4, 22, 9), ("tor_weg", tor_weg, 36, 8), ("tor_offen", tor_gang(False), 28, 12), ("tor_zu", tor_gang(True), 28, 12), ("trupp_nah", trupp_nah, 32, 6), ("bergauf", bergauf, 2, 2))


def sonder10_g(l):
    """Der zweite Nachlauf im Gefecht: Loeschen, Angst, Munition und die Verlustzaehler."""
    s = l.s
    lords = {e["besitzer"]: e for e in s.einheiten_alle() if e["typ"] == 55}

    def loeschen(x, y):
        """V7.001: Eine Huette von Spieler 1 brennt, ein Brunnen steht daneben (UpdateFireWatch, Art 53). Ohne Brunnen brannte sie rund 960 bis 980 Takte (sonder1)."""
        h = _g(1, x + 10, y + 2, spieler=1)
        ft = _e("taeter", 76, x + 1, y + 4, 2)
        return [h, _g(27, x + 16, y + 2, spieler=1)], [ft], [], lambda: [], [(SONDER_BEMANNEN, lambda: [_angriff([ft], 2, gebaeude=h["nr"])] if "nr" in h else [])]

    def angst(x, y):
        """P332: Schwert gegen Schwert. Spieler 1 hat Gaerten, Spieler 2 Galgen: Die Stufe rechnet das Spiel aus gut minus schlecht (recomputeAllFearFactors), ein gesetzter Wert hielte nicht. Der Schaden folgt laut Speicher einer Tabelle von UCP3, nicht 5 Prozent je Stufe."""
        g1 = [_g(66, x + 8 + 4 * i, y, spieler=1) for i in range(ANGST_BAUTEN)]
        lp = lords.get(2)
        g2 = []
        if lp:
            dx, dy = (16 if lp["x"] < 200 else -16), (16 if lp["y"] < 200 else -16)  # zur Kartenmitte
            g2 = [_g(93, lp["x"] + dx + (3 * i if dx > 0 else -3 * i), lp["y"] + dy, spieler=2) for i in range(ANGST_BAUTEN)]
        return g1 + g2, [_e("taeter", 27, x + 2, y + 2), _e("opfer", 27, x + 3, y + 2, 2)], [], lambda: [], None

    def munition(x, y):
        """P308, P309: Spielbefehl 86 hat zwei Werte (CommandSelectionReplenishAmmo): 0 laedt die Einheit mit der Nummer im ersten Wert (TryAcquireAmmunitionOrPlanToBuyStone), sonst fuellt er den Trupp auf (SelectionReplenishAmmo). Lauf 01:08 schickte den Trupp mit 0, also den falschen Zweig."""
        a, b = dict(_e("geraet", 39, x + 4, y + 2), mann=2, soll=2), dict(_e("geraet", 39, x + 4, y + 10), mann=2, soll=2)
        la, lb = _ing(x, y + 1, 2), _ing(x, y + 9, 2)
        za, zb = _e("ziel", 25, x + 28, y + 2, 2), _e("ziel", 25, x + 28, y + 10, 2)

        def stein():
            return [{"player": 1, "ware": {"typ": 4, "menge": STEIN_MENGE}}]

        def schiessen():
            return [_angriff([a], ziel=za["nr"]), _angriff([b], ziel=zb["nr"])]

        def trupp_auffuellen():
            trupp = {e["nr"]: e["trupp"] for e in s.einheiten_alle()}.get(b["nr"], 0)
            return stein() + ([{"player": 1, "spielbefehl": {"nr": 86, "werte": [trupp, 1]}}] if trupp else [])

        def einheit_laden():
            return stein() + [{"player": 1, "spielbefehl": {"nr": 86, "werte": [a["nr"], 0]}}]
        return [], [a, b] + la + lb + [za, zb], [], lambda: [_angriff(la, art=16, a=a["nr"], b=a["uid"]), _angriff(lb, art=16, a=b["nr"], b=b["uid"])], [(SONDER_BEMANNEN, schiessen), (MUNITION_TRUPP, trupp_auffuellen), (MUNITION_EINHEIT, einheit_laden)]

    def verlust(x, y):
        """P305, P306: Ein Speertraeger von Spieler 1 faellt durch einen Ritter von Spieler 2. Beide Zaehler stehen nicht in der Aufzeichnung, szene_sonder liest sie vorher und nachher."""
        return [], [_e("opfer", 24, x + 1, y + 1), _e("taeter", 28, x + 2, y + 1, 2)], [], lambda: [], None
    return (("munition", munition, 36, 14), ("angst", angst, 30, 5), ("loeschen", loeschen, 22, 8), ("verlust", verlust, 6, 4))


def sonder12(l):
    """Dritter Nachlauf im Editor. Turm: Nur die vier Eckfelder tragen Bit 0x400, der Rest 0x10000000 (placeTower, gelesen in sonder10), und eine Mauerlinie, die auf ein belegtes Feld reicht, baut das Spiel gar nicht. Darum Mauer bis vor den Turm, Ziel ist das Eckfeld."""
    s = l.s
    frei, hoehe, _ = s.raster()
    hang = steigung(frei, hoehe, 8, 3)

    def weg(x, zeile, nur_treppe=False):
        if nur_treppe:
            return [{"player": 1, "spielbefehl": {"nr": 25, "werte": [x + 9, zeile, x + 9, zeile, TREPPE, 13]}}]
        return [{"player": 1, "spielbefehl": {"nr": 25, "werte": [x + 3, zeile, x + 9, zeile, 25, 13]}}, {"player": 1, "spielbefehl": {"nr": 25, "werte": [x + 2, zeile, x + 2, zeile, TREPPE, 13]}}]

    def turm_eck(x, y):
        """P338: 8 Mann ueber Treppe und Mauer auf den Wachturm. Die Obergrenze 5 prueft laut Code nur der Mausklick (MenuItemActionHandler), der Befehl selbst nicht."""
        wer = [_e("steiger", 24, x, y + i) for i in range(8)]
        return [_g(74, x + 10, y + 2, spieler=1)], wer, weg(x, y + 2), lambda: [_angriff([w], lauf=[x + 10, y + 2]) for w in wer], None

    def turm_mitte(x, y):
        """Wie turm_eck, aber die Mauer trifft den Turm in der Mitte seiner Seite."""
        wer = [_e("steiger", 24, x, y + 3)]
        return [_g(74, x + 10, y + 2, spieler=1)], wer, weg(x, y + 3), lambda: [_angriff(wer, lauf=[x + 10, y + 2])], None

    def turm_treppe(x, y):
        """Nur eine Treppe direkt am Eckfeld, keine Mauer."""
        wer = [_e("steiger", 24, x, y + 2)]
        return [_g(74, x + 10, y + 2, spieler=1)], wer, weg(x, y + 2, True), lambda: [_angriff(wer, lauf=[x + 10, y + 2])], None

    def turm_direkt(x, y):
        """P302 woertlich: Die Einheit steht von Anfang an auf dem Eckfeld des grossen Turms, spaeter geht sie herunter."""
        wer = [_e("steiger", 24, x + 10, y + 1)]
        return [_g(77, x + 10, y + 1, spieler=1)], wer, [], lambda: [], [(1500, lambda: [_angriff(wer, lauf=[x, y + 1])])]

    def turm4_weg(x, y):
        """P302: Der Weg auf den grossen Turm, spaeter zurueck."""
        wer = [_e("steiger", 24, x, y + 1)]
        return [_g(77, x + 10, y + 1, spieler=1)], wer, weg(x, y + 1), lambda: [_angriff(wer, lauf=[x + 10, y + 1])], [(1500, lambda: [_angriff(wer, lauf=[x, y + 1])])]

    def tor_abstand(abstand):
        """P303: Im Speicher steht 140 Mikro statt der 200 aus dem Export (code_abgleich.txt), also 17,5 Felder."""
        def f(x, y):
            return [_g(46, x + 30, y + 2)], [_e("feind", 24, x + 30 - abstand, y + 4)], [], lambda: [], None
        return f

    def tor_wand(mit_feind):
        """P304: Mauer links und rechts bis vor das Tor. In sonder10 reichte die linke Linie auf das Torfeld und fehlte darum ganz."""
        def f(x, y):
            wand = [{"player": 2, "spielbefehl": {"nr": 25, "werte": w + [25, 13]}} for w in ([x, y + 5, x + 9, y + 5], [x + 15, y + 5, x + 26, y + 5])]
            geher = [_e("geher", 24, x + 12, y, 2)]
            feind = [_e("feind", 24, x + 3, y + 10)] if mit_feind else []
            return [_g(46, x + 10, y + 3)], geher + feind, wand, lambda: [], [(TOR_ZU_TAKT, lambda: [_angriff(geher, 2, lauf=[x + 12, y + 11])])]
        return f

    def trupp_ring(x, y):
        """P325: applyMoveCommandOrRallyCommandToTribe laeuft nur, wenn das Ziel nicht erreichbar ist, sonst rechnet giveTribeMoveInstruction die Zielfelder selbst (sonder10: Der Kaempfer lief mit). Darum liegt das Ziel im Mauerring. Der erste steht neben dem Feind und kaempft (Zustand 106)."""
        ring = [[x + 30, y, x + 39, y], [x + 30, y + 8, x + 39, y + 8], [x + 30, y + 1, x + 30, y + 8], [x + 38, y + 1, x + 38, y + 8]]
        wer = [_e("trupp", 27, x + 1 + 3 * i, y + 2) for i in range(6)]
        gegner = _e("feind", 25, x + 1, y + 3, 2)
        return [], wer + [gegner], [{"player": 2, "spielbefehl": {"nr": 25, "werte": r + [25, 13]}} for r in ring], lambda: [], [(150, lambda: [_angriff(wer, lauf=[x + 34, y + 4])])]

    def bergab_auf(x, y):
        """P330: Die gesetzte Einheit hat Hoehe 8, auch auf einem Feld mit 4 (sonder10). Also erst hinunter, dann hinauf: Der Code erhoeht das Tempo nur, wenn das Feld hoeher liegt als die Einheit."""
        if hang is None:
            return [], [], [], lambda: [], None
        wer = [_e("laeufer", 24, hang[0] + 7, hang[1])]
        return [], wer, [], lambda: [_angriff(wer, lauf=[hang[0], hang[1]])], [(400, lambda: [_angriff(wer, lauf=[hang[0] + 7, hang[1]])])]
    return (("turm_eck", turm_eck, 14, 9), ("turm_mitte", turm_mitte, 14, 6), ("turm_treppe", turm_treppe, 14, 6), ("turm_direkt", turm_direkt, 18, 9), ("turm4_weg", turm4_weg, 18, 9), ("tor_17", tor_abstand(17), 36, 8), ("tor_18", tor_abstand(18), 36, 8), ("tor_offen_w", tor_wand(False), 28, 12), ("tor_zu_w", tor_wand(True), 28, 12), ("trupp_ring", trupp_ring, 40, 10), ("bergab_auf", bergab_auf, 2, 2))


def acht_steiger(x, y):
    """8 Mann unter der Linie: Wer auf einem Feld der Linie steht, verhindert den Bau (validateWallBuildPath)."""
    return [_e("steiger", 24, x + i, y + 6) for i in range(8)]


def treppe_und_mauer(x, zeile):
    """M_MAPPER_STAIR beginnt neben dem Mauerende und faellt je Feld um 16 (placeWalls): 82, 66, 50, 34, 18. Die Mauer endet vor dem Turm, eine Linie auf ein belegtes Feld baut das Spiel gar nicht."""
    return [{"player": 1, "spielbefehl": {"nr": 25, "werte": [x + 6, zeile, x + 12, zeile, 25, 13]}}, {"player": 1, "spielbefehl": {"nr": 25, "werte": [x + 5, zeile, x + 1, zeile, TREPPE, 13]}}]


def sonder13(l):

    """Vierter Nachlauf im Editor: der Weg auf den Turm mit echter Treppe. M_MAPPER_STAIR beginnt neben dem Mauerende und faellt je Feld um 16 (placeWalls): 82, 66, 50, 34, 18. Mit einem einzigen Feld sprang sie in sonder12 von 8 auf 82, darum blieb jeder unten."""
    def turm_eck(x, y):
        """P338: 8 Mann ueber Treppe und Mauer auf den Wachturm. Die Obergrenze 5 prueft laut Code nur der Mausklick (MenuItemActionHandler), der Befehl selbst nicht."""
        wer = acht_steiger(x, y)
        return [_g(74, x + 13, y + 2, spieler=1)], wer, treppe_und_mauer(x, y + 2), lambda: [_angriff([w], lauf=[x + 13, y + 2]) for w in wer], None

    def turm_mitte(x, y):
        """Wie turm_eck, aber die Mauer trifft den Turm in der Mitte seiner Seite."""
        wer = [_e("steiger", 24, x, y + 6)]
        return [_g(74, x + 13, y + 2, spieler=1)], wer, treppe_und_mauer(x, y + 3), lambda: [_angriff(wer, lauf=[x + 13, y + 2])], None

    def turm4_weg(x, y):
        """P302: Der Weg auf den grossen Turm, spaeter zurueck. Den Zaehler setzt erst processUnitMove, wer gesetzt wird, startet ihn nicht (sonder12)."""
        wer = [_e("steiger", 24, x, y + 8)]
        return [_g(77, x + 13, y + 1, spieler=1)], wer, treppe_und_mauer(x, y + 1), lambda: [_angriff(wer, lauf=[x + 13, y + 1])], [(1500, lambda: [_angriff(wer, lauf=[x, y + 8])])]

    def tor_17(x, y):
        """P303: Im Speicher steht 140 Mikro (code_abgleich.txt). In sonder12 stand das Tor bei 17 nicht, das Tor bei 18 reagierte nicht."""
        return [_g(46, x + 30, y + 2)], [_e("feind", 24, x + 13, y + 4)], [], lambda: [], None

    def trupp_ring(x, y):
        """P325: Das Ziel liegt im Ring, wie in sonder12, dort war der Ring aber offen. szene_sonder wiederholt jetzt fehlende Linien."""
        ring = [[x + 30, y, x + 39, y], [x + 30, y + 8, x + 39, y + 8], [x + 30, y + 1, x + 30, y + 8], [x + 38, y + 1, x + 38, y + 8]]
        wer = [_e("trupp", 27, x + 1 + 3 * i, y + 2) for i in range(6)]
        zweikampf = _e("feind", 25, x + 1, y + 3, 2)
        return [], wer + [zweikampf], [{"player": 2, "spielbefehl": {"nr": 25, "werte": r + [25, 13]}} for r in ring], lambda: [], [(150, lambda: [_angriff(wer, lauf=(x + 34, y + 4))])]
    return (("turm_eck", turm_eck, 17, 8), ("turm_mitte", turm_mitte, 17, 8), ("turm4_weg", turm4_weg, 20, 10), ("tor_17", tor_17, 36, 8), ("trupp_ring", trupp_ring, 40, 10))


def sonder14(l):
    """Fuenfter Nachlauf im Editor. giveTribeMoveInstruction gibt auf, wenn die Flaechen nicht verbunden sind (return 0), und die Flaechenkarte wird nur alle 50 Takte neu gerechnet (updateSeparateAreaTileMap, im Speicher 50 statt 200). In sonder13 kam der Laufbefehl im selben Augenblick wie die Mauer: Niemand ging los. Darum Befehl erst nach LAUF_NACH_BAU, und zum Vergleich ein Ziel auf der Mauer selbst und eines in der Turmmitte."""
    def nur_mauer(x, y):
        """Der einfachste Fall: Treppe und Mauer, das Ziel liegt auf der Mauer. Geht das nicht, ist die Frage nach dem Turm verfrueht."""
        wer = [_e("steiger", 24, x, y + 4)]
        return [], wer, treppe_und_mauer(x, y + 2), lambda: [], [(LAUF_NACH_BAU, lambda: [_angriff(wer, lauf=[x + 9, y + 2])])]

    def turm_eck(x, y):
        """P338: 8 Mann auf das Eckfeld des Wachturms."""
        wer = acht_steiger(x, y)
        return [_g(74, x + 13, y + 2, spieler=1)], wer, treppe_und_mauer(x, y + 2), lambda: [], [(LAUF_NACH_BAU, lambda: [_angriff([w], lauf=[x + 13, y + 2]) for w in wer])]

    def turm_mitte(x, y):
        """Das Ziel ist die Mitte des Wachturms, so wie ein Klick auf den Turm."""
        wer = [_e("steiger", 24, x, y + 6)]
        return [_g(74, x + 13, y + 2, spieler=1)], wer, treppe_und_mauer(x, y + 3), lambda: [], [(LAUF_NACH_BAU, lambda: [_angriff(wer, lauf=[x + 14, y + 3])])]

    def turm4_weg(x, y):
        """P302: Der Weg auf den grossen Turm, spaeter zurueck. Den Zaehler setzt erst processUnitMove."""
        wer = [_e("steiger", 24, x, y + 8)]
        return [_g(77, x + 13, y + 1, spieler=1)], wer, treppe_und_mauer(x, y + 1), lambda: [], [(LAUF_NACH_BAU, lambda: [_angriff(wer, lauf=[x + 13, y + 1])]), (LAUF_NACH_BAU + 1500, lambda: [_angriff(wer, lauf=[x, y + 8])])]

    def trupp_ohne_flaeche(x, y):
        """P325: applyMoveCommandOrRallyCommandToTribe laeuft nur, wenn die erste Einheit des Trupps auf keiner Flaeche steht (giveTribeMoveInstruction, sonst rechnet der Befehl selbst oder gibt auf). Darum steht sie in der Mitte eines Wachturms. Ein anderer kaempft neben dem Feind (Zustand 106)."""
        erster = _e("trupp", 27, x + 21, y + 3)
        kaempfer = _e("trupp", 27, x + 1, y + 2)
        rest = [_e("trupp", 27, x + 4 + 3 * i, y + 2) for i in range(4)]
        gegner_ohne = _e("feind", 25, x + 1, y + 3, 2)
        return [_g(74, x + 20, y + 2, spieler=1)], [erster, kaempfer] + rest + [gegner_ohne], [], lambda: [], [(150, lambda: [_angriff([erster, kaempfer] + rest, lauf=[x + 30, y + 3])])]
    return (("nur_mauer", nur_mauer, 17, 6), ("turm_eck", turm_eck, 17, 8), ("turm_mitte", turm_mitte, 17, 8), ("turm4_weg", turm4_weg, 20, 10), ("trupp_ohne_flaeche", trupp_ohne_flaeche, 34, 6))


def sonder17(l):
    """Sechster Nachlauf im Editor. sonder14 hat gezeigt: Die Mitte des Turms ist begehbar und mit der Treppe verbunden, die vier Ecken haben Flaeche 0 und sind gesperrt (Bit 0x400). Mein Eckfeld war also falsch herum gelesen."""
    def turm_voll(x, y):
        """P338: 8 Mann auf den Wachturm. Die Obergrenze 5 prueft laut Code nur der Mausklick (MenuItemActionHandler), der Befehl selbst nicht."""
        wer = acht_steiger(x, y)
        return [_g(74, x + 13, y + 2, spieler=1)], wer, treppe_und_mauer(x, y + 3), lambda: [], [(LAUF_NACH_BAU, lambda: [_angriff([w], lauf=[x + 14, y + 3]) for w in wer])]

    def turm4_gang(x, y):
        """P302: Der grosse Turm, Mauer in einer Zeile ohne Ecke. Hin und spaeter zurueck: hasUnitsOntop wechselt, wenn der Zaehler 0 erreicht."""
        wer = [_e("steiger", 24, x, y + 8)]
        return [_g(77, x + 13, y + 1, spieler=1)], wer, treppe_und_mauer(x, y + 3), lambda: [], [(LAUF_NACH_BAU, lambda: [_angriff(wer, lauf=[x + 15, y + 3])]), (LAUF_NACH_BAU + 1500, lambda: [_angriff(wer, lauf=[x, y + 8])])]

    def trupp_eck(x, y):
        """P325: applyMoveCommandOrRallyCommandToTribe laeuft nur, wenn die erste Einheit auf Flaeche 0 steht. Die Turmecke hat Flaeche 0 (sonder14). Ein anderer kaempft neben dem Feind (Zustand 106)."""
        erster = _e("trupp", 27, x + 20, y + 2)
        am_feind = _e("trupp", 27, x + 1, y + 2)
        rest = [_e("trupp", 27, x + 4 + 3 * i, y + 2) for i in range(4)]
        feind_nah = _e("feind", 25, x + 1, y + 3, 2)
        return [_g(74, x + 20, y + 2, spieler=1)], [erster, am_feind] + rest + [feind_nah], [], lambda: [], [(150, lambda: [_angriff([erster, am_feind] + rest, lauf=[x + 30, y + 3])])]
    return (("turm_voll", turm_voll, 17, 8), ("turm4_gang", turm4_gang, 20, 10), ("trupp_eck", trupp_eck, 34, 6))


def poke2(l, adr, wert):
    """Ein Befehl fuer ein Feld von 2 Byte. Der poke-Befehl schreibt immer 4 Byte (Modul), das Nachbarfeld bleibt so erhalten."""
    alt = l.k.peek(adr)[0]
    return {"poke": adr, "wert": (alt & 0xFFFF0000) | (wert & 0xFFFF)}


def sonder15_g(l):
    """Lagen mit gesetzten Schaltern. Fairness: Nur in diesem Messlauf, nichts davon geht in SamurAI."""
    s = l.s

    def assassinen(x, y):
        """P370: totalAssassinTroops zaehlt nur Einheiten mit aiUnitBehaviourType 12 (updateUnits), in Lauf K hatten alle Assassinen 1. Den Wert vergibt die KI, Spieler 1 hat keine, also setzen. Spaeter sterben sie."""
        wer = [_e("assassine", 73, x + 1 + 2 * i, y + 1) for i in range(2)]
        adr, schritt = s.feld("DAT_UnitsState", "units[].aiUnitBehaviourType")
        return [], wer, [], lambda: [], [(AUFTRAG_TAKT, lambda: [poke2(l, adr + schritt * w["nr"], AUFTRAG_ASSASSINE) for w in wer]), (AUFTRAG_TOD, lambda: [{"player": 1, "toeteAlle": {"spieler": 1, "ohneLord": True, "typen": [73]}}])]

    def korb(x, y):
        """P312: CommandSpawnEntity (Spielbefehl 69) kostet nur in GM_SIEGE_THAT Gold: gameMode_2 == 6 und Art ET_BRAZIER. Einmal in der Spielart des Gefechts, einmal gesetzt. Zurueck auf den alten Wert, damit der Rest des Laufs unberuehrt bleibt."""
        adr, _ = s.feld("DAT_GameCore", "gameMode_2")

        def stein_gold():
            return [{"player": 1, "ware": {"typ": 15, "menge": KORB_GOLD}}]

        def korb_setzen(dx):
            return stein_gold() + [{"player": 1, "spielbefehl": {"nr": 69, "werte": [1, (x + dx) * 8, y * 8, 8, ET_BRAZIER, 1]}}]
        return [], [], [], lambda: [], [(KORB_TAKT, lambda: korb_setzen(1)), (KORB_TAKT + 60, lambda: [{"poke": adr, "wert": GM_SIEGE_THAT}]), (KORB_TAKT + 120, lambda: korb_setzen(4)), (KORB_TAKT + 180, lambda: [{"poke": adr, "wert": GM_GEFECHT_2}])]
    return (("assassinen", assassinen, 8, 4), ("korb", korb, 8, 3))


def sonder16_g(l):
    """P331, zuletzt und allein, weil currentGameMode den ganzen Lauf betrifft: Der Rush-Schutz gilt laut Code nicht im Einzelspieler-Gefecht (shouldUnitsEngageInMelee). Also Spielart Mehrspieler setzen. Bleibt das Spiel stehen, ist auch das eine Messung."""
    s = l.s

    def rush(x, y):
        a, b = _e("taeter", 27, x + 1, y + 1), _e("opfer", 27, x + 14, y + 1, 2)
        modus, _ = s.feld("DAT_GameSynchronyState", "currentGameMode")
        rest, _ = s.feld("DAT_GameState", "mapAndTime.totalNoRushTicks")
        return [], [a, b], [], lambda: [], [(RUSH_LAUF, lambda: [_angriff([a], lauf=[x + 13, y + 1])]), (RUSH_SETZEN, lambda: [{"poke": rest, "wert": RUSH_TAKTE}, {"poke": modus, "wert": GM_MEHRSPIELER}]), (RUSH_SETZEN + RUSH_TAKTE + RUSH_NACH, lambda: [{"poke": modus, "wert": GM_EINZEL}])]
    return (("rush", rush, 18, 3),)


def sonder11_g(l):
    """P314: Wie sonder9_g, aber die Gegner gehen genau auf ein Feld des brennenden Pechs (Lauf 00:40: bis 1 Feld daneben, counter blieb 0)."""
    s = l.s

    def pech(x, y):
        baue = [{"player": 1, "baue": {"mapper": 99, "x": x + 10 + i, "y": y + 4, "groesse": 1, "richtung": 15}} for i in range(5)]
        ft = _e("taeter", 76, x + 12, y + 1)
        opfer = _e("opfer", 25, x + 2, y + 4, 2)
        geher = [_e("geher", 24, x + 10 + i, y + 9, 2) for i in range(5)]

        def hin():
            nah = [g for g in s.pech_liste(1) if abs(g["y"] - (y + 4)) <= 1 and x + 8 <= g["x"] <= x + 16]
            return [_angriff([g], 2, lauf=[nah[i % len(nah)]["x"], nah[i % len(nah)]["y"]]) for i, g in enumerate(geher)] if nah else []
        return [], [ft, opfer] + geher, baue, lambda: [_angriff([opfer], 2, lauf=[x + 12, y + 4])], [(300, lambda: [_angriff([ft], ziel=opfer["nr"])]), (510, hin)]
    return (("pech", pech, 24, 11),)


SONDER_G = (("graben", p_graben, 24, 8), ("leiter", p_leiter, 30, 16), ("turmgeraet", p_turmgeraet, 30, 12), ("schild", p_schild, 34, 10), ("hoehe", p_hoehe, 60, 6), ("tor", p_tor, 30, 10), ("oel", p_oel, 24, 8))
SONDER_WAREN = ((4, 2000), (7, 500))  # Stein fuer Mauern, Pech fuer das Oel: Im Gefecht kosten Spielbefehle Waren, der Start reicht nicht
SONDER2 = (("leiter", p_leiter, 30, 16), ("turmgeraet", p_turmgeraet, 30, 12), ("tunnel", p_tunnel, 28, 10), ("schild", p_schild, 34, 10), ("hoehe", p_hoehe, 60, 6), ("tor", p_tor, 30, 10), ("oel", p_oel, 24, 6))


def starttruppen_abwarten(l):
    rest = STARTTRUPPEN_TAKT - l.s.takt()
    if rest > 0:
        lk.aufnahme_im_stand_ohne(l, lf.TEMPO_LAUF)
        l.warte_takte(rest)
        lk.anhalten(l)


def szene_sonder(l, name, posten, frei_maske=None, rand=SONDER_ABSTAND, raeumen=False):
    """Die Sonderfaelle, weit auseinander. Jeder Posten bekommt seine Befehle in drei Stufen: Spielbefehle davor, Befehle beim Start, Befehle nach dem Einsteigen. Ein Posten, der keinen Platz findet oder dessen Gebaeude nicht steht, ist ein Fund und haelt die anderen nicht auf."""
    k, s = l.k, l.s
    lk.anhalten(l)
    if raeumen:
        starttruppen_abwarten(l)
        abraeumen(l)  # die Starttruppen schiessen sonst auf alles
    frei, _, _ = s.raster()
    frei_kontrolle = frei  # fern von allem, auch wenn die Posten im Ring um eine Burg liegen und ihn belegen (Lauf 22:30)
    if frei_maske:
        fern, s.fern = s.fern, 0
        frei, _, _ = s.raster()
        s.fern = fern
        frei = frei_maske(frei)
    orte = packen(frei, [(b, h) for _, _, b, h in posten], rand=rand)
    gebaeude, einheiten, davor, jetzt, stufen, karte, fehlt = [], [], [], [], [], [], []
    for (n, f, b, h), o in zip(posten, orte):
        if o is None:
            fehlt.append(n)
            continue
        g, e, d, j, sp, *felder = f(*o)
        for z in g + e:
            z["posten"] = n
        gebaeude += g
        einheiten += e
        davor += d
        jetzt.append(j)
        if sp:
            stufen += sp if isinstance(sp, list) else [(SONDER_BEMANNEN, sp)]
        karte.append({"posten": n, "x": o[0], "y": o[1], "breite": b, "hoehe": h, "felder": [[x, y, s.kachel(x, y)] for x, y in felder[0]] if felder else []})
    if l.gefecht:
        for z in gebaeude:
            ort = erlaubte_stelle(l, z)
            if ort:
                z["x"], z["y"] = ort
    nicht_gesetzt = gebaeude_setzen(l, gebaeude)
    for _ in range(GEBAEUDE_VERSUCHE):
        if not nicht_gesetzt:
            break
        lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
        l.warte_takte(SONDER_SPIELER_TAKTE)
        lk.anhalten(l)
        nicht_gesetzt = gebaeude_setzen(l, nicht_gesetzt)
    if l.gefecht:
        davor = [{"player": p, "ware": {"typ": t, "menge": m}} for p in SPIELER_S for t, m in SONDER_WAREN] + davor
    boden = s.raster()[1]
    mauer_fehlt, mauer_wiederholt = [], 0
    for sp_ in sorted({c.get("player", 1) for c in davor}):
        offen = [c for c in davor if c.get("player", 1) == sp_]
        for versuch in range(MAUER_VERSUCHE):
            k.liste(offen, lf.KANAL)
            lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
            l.warte_takte(SONDER_SPIELER_TAKTE)
            lk.anhalten(l)
            offen = linien_fehlen(s, offen, boden)
            if not offen:
                break
            mauer_wiederholt += 1
        mauer_fehlt += [c["spielbefehl"]["werte"] for c in offen]
    einheiten = mit_kontrolle(einheiten, frei_kontrolle)
    setzen(l, einheiten)
    k.liste([c for j in jetzt for c in j()], lf.KANAL)
    vorher = verluste_lesen(l)
    a = lk.aufnahme_im_stand(l, name, 100, False)
    gewartet = 0
    for nach, f in sorted(stufen, key=lambda z: z[0]):
        l.warte_takte(nach - gewartet)
        k.liste(f(), lf.KANAL)
        gewartet = nach
    l.warte_takte(GRENZE_SONDER)
    b = lk.anhalten(l)
    pfad = l.rek.pfad
    stand = l.rek.beenden()
    graben = len(s.felder_mit_bit(lf.BIT_GRABEN)) if hasattr(s, "felder_mit_bit") else None
    with open(pfad + ".plan.json", "w", encoding="utf-8") as f:
        json.dump({"szene": name, "von": a, "bis": b, "tempo": 100, "einheiten": einheiten, "gebaeude": gebaeude, "karte": karte, "nicht_gesetzt": [z["name"] for z in nicht_gesetzt], "kein_platz": fehlt, "graben_felder_am_ende": graben, "verluste": {"vorher": vorher, "nachher": verluste_lesen(l)}, "mauer_fehlt": mauer_fehlt, "mauer_wiederholt": mauer_wiederholt}, f, ensure_ascii=False)
    abr = abraeumen(l)
    return {"szene": name, "von": a, "bis": b, "einheiten": len(einheiten), "nicht_gesetzt": [z["name"] for z in nicht_gesetzt], "kein_platz": fehlt, "abraeumen_takte": abr, "stand": stand, "pfad": pfad}


def befehle_gebaeude_nah(plan):
    ziele = {z["fall"]: z["nr"] for z in plan["gebaeude"] if "nr" in z}
    return [{"player": 1, "angriff": {"einheiten": [e["nr"]], "gebaeude": ziele[e["fall"]]}} for e in plan["einheiten"] if e["rolle"] == "angreifer"]


def szene_geraete(l, name, aufbau, befehle, tempo, grenze):
    """Erst steigen die Ingenieure ein, dann kommt der Befehl fuer alle, auch fuer die Geraete mit einem Mann zu wenig. Wer sich dann nicht ruehrt, zeigt die Besatzungsregel."""
    k, s = l.k, l.s
    lk.anhalten(l)
    plan = aufbau(l)
    setzen(l, plan["einheiten"])
    k.liste(befehle_einsteigen(plan), lf.KANAL)
    a = lk.aufnahme_im_stand(l, name, tempo, False)
    voll = [e for e in plan["einheiten"] if e["rolle"] == "geraet" and e["mann"] == e["soll"]]
    plan["bemannt"] = l.warte_takte(GRENZE_BEMANNEN, lambda: all(s.besatzung(e["nr"]) >= e["soll"] for e in voll))
    plan["bemannt_nach"] = s.takt() - a
    k.liste(befehle(plan), lf.KANAL)
    l.warte_takte(grenze)
    b = lk.anhalten(l)
    pfad = l.rek.pfad
    stand = l.rek.beenden()
    with open(pfad + ".plan.json", "w", encoding="utf-8") as f:
        json.dump({"szene": name, "von": a, "bis": b, "tempo": tempo, **plan}, f, ensure_ascii=False)
    abr = abraeumen(l)
    return {"szene": name, "von": a, "bis": b, "einheiten": len(plan["einheiten"]), "bemannt": plan["bemannt"], "bemannt_nach": plan["bemannt_nach"], "nicht_gesetzt": plan.get("nicht_gesetzt"), "nicht_gefahren": plan.get("nicht_gefahren"), "abraeumen_takte": abr, "stand": stand, "pfad": pfad}


def szene_haltung(l, faelle=FAELLE_HALTUNG, name="haltung"):
    """Der Radius der Haltung. Erst stehen die Gruppen mit ihrer Haltung, dann erst kommt der Feind, sonst reagiert jemand mit der Grundhaltung. Der Feind hat keine Gruppe, er laeuft also nicht los (tribeID 0, L77)."""
    k, s = l.k, l.s
    lk.anhalten(l)
    frei, hoehe, _ = s.raster()
    orte = gitter(frei, hoehe, 28, 1, HALTUNG_RASTER_X, HALTUNG_RASTER_Y, len(faelle))
    if len(orte) < len(faelle):
        raise Abbruch(f"Nur {len(orte)} Plaetze fuer {len(faelle)} Haltungs-Faelle")
    wachen = [{"rolle": "wache", "fall": i, "haltung": h[0], "wert": h[1], "abstand": h[2], "spieler": 1, "typ": t, "x": x, "y": y} for i, ((t, h), (x, y)) in enumerate(zip(faelle, orte))]
    setzen(l, wachen)
    k.liste([{"player": 1, "angriff": {"einheiten": [e["nr"]], "lauf": [e["x"], e["y"]]}} for e in wachen], lf.KANAL)
    lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)

    def jetzt():
        return {e["nr"]: e for e in s.einheiten_alle()}
    if not l.warte_takte(HALTUNG_TRUPP, lambda: all(jetzt().get(e["nr"], {}).get("trupp") for e in wachen)):
        raise Abbruch("Haltung: Nicht alle stehen in einer Gruppe")
    orte_jetzt = jetzt()
    for e in wachen:
        e["trupp"] = orte_jetzt[e["nr"]]["trupp"]
    k.liste([{"player": 1, "spielbefehl": {"nr": 70, "werte": [e["trupp"], e["wert"]]}} for e in wachen], lf.KANAL)
    if not l.warte_takte(HALTUNG_BEFEHL, lambda: all(s.haltung(e["trupp"]) == e["wert"] for e in wachen)):
        raise Abbruch(f"Haltung: Befehl 70 wirkt nicht: {[(e['trupp'], e['wert'], s.haltung(e['trupp'])) for e in wachen][:5]}")
    lk.anhalten(l)
    orte_jetzt = jetzt()
    for e in wachen:
        e["x"], e["y"] = orte_jetzt[e["nr"]]["x"], orte_jetzt[e["nr"]]["y"]
    feinde = [{"rolle": "feind", "fall": e["fall"], "spieler": 2, "typ": 24, "x": e["x"] + e["abstand"], "y": e["y"]} for e in wachen]
    einheiten = mit_kontrolle(wachen + feinde, frei)
    setzen(l, feinde + einheiten[-1:])
    a = lk.aufnahme_im_stand(l, name, 200, False)
    l.warte_takte(GRENZE_HALTUNG)
    b = lk.anhalten(l)
    pfad = l.rek.pfad
    stand = l.rek.beenden()
    with open(pfad + ".plan.json", "w", encoding="utf-8") as f:
        json.dump({"szene": name, "von": a, "bis": b, "tempo": 200, "einheiten": einheiten}, f, ensure_ascii=False)
    abr = abraeumen(l)
    return {"szene": name, "von": a, "bis": b, "einheiten": len(einheiten), "abraeumen_takte": abr, "stand": stand, "pfad": pfad}


def freie_mitte(frei, x, y, rand=2, mindestens=6):
    """Das naechste Feld, um das herum alles frei ist, nicht zu nah an (x, y). None, wenn es keins gibt."""
    ys, xs = np.nonzero(frei)
    d = np.maximum(np.abs(xs - x), np.abs(ys - y))
    for i in np.argsort(d, kind="stable"):
        ax, ay = int(xs[i]), int(ys[i])
        if d[i] >= mindestens and rand <= ay < frei.shape[0] - rand and rand <= ax < frei.shape[1] - rand and frei[ay - rand:ay + rand + 1, ax - rand:ax + rand + 1].all():
            return ax, ay
    return None


def szene_lord(l, name="lord_g", selbst=False):
    """P313, P362, P306: Der Lord steht auf der Burg, Ritter finden dorthin keinen Weg (Lauf 20:25). Darum geht er erst vor die Burg, mitten in einen Ring aus 8 Rittern von Spieler 1, und der Nahkampf beginnt von selbst (Umkreis 2 Felder). Ein Direktbefehl (einheit_ziel) liess ihn dort nicht hin (Lauf 20:29), darum der Truppenbefehl. Bleibt er trotzdem oben, faellt er per Befehl: Die Niederlage-Pruefung soll in jedem Fall gemessen werden, und per_befehl sagt es dazu. Danach ist das Gefecht vorbei, darum kommt diese Szene zuletzt. Fertig ist sie, wenn das Spiel das Ende gemerkt hat oder NACH_LORD Takte um sind."""
    k, s = l.k, l.s
    lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
    l.warte_takte(LORD_RUHE)
    lk.anhalten(l)
    lord = next((e for e in s.einheiten_alle() if e["typ"] == 55 and e["besitzer"] == 2), None)
    if lord is None:
        raise Abbruch("Kein Lord von Spieler 2")
    fern, s.fern = s.fern, 0
    frei = s.raster()[0]
    s.fern = fern
    mitte = freie_mitte(frei, lord["x"], lord["y"])
    if mitte is None:
        raise Abbruch("Kein freier Platz fuer den Ring um den Lord")
    mx, my = mitte
    plan = {"einheiten": [{"rolle": "ritter", "spieler": 1, "typ": 28, "x": mx + dx, "y": my + dy} for dx, dy in ((-2, -2), (0, -2), (2, -2), (-2, 0), (2, 0), (-2, 2), (0, 2), (2, 2))], "mitte": mitte}
    setzen(l, plan["einheiten"])
    k.liste([{"player": 2, "angriff": {"einheiten": [lord["nr"]], "lauf": [mx, my]}}], lf.KANAL)
    a = lk.aufnahme_im_stand(l, name, lf.TEMPO_JEDER_TAKT, False)

    def lebt():
        return any(e["nr"] == lord["nr"] and e["uid"] == lord["uid"] and e["leben"] > 0 for e in s.einheiten_alle())

    def im_ring():
        return any(e["nr"] == lord["nr"] and max(abs(e["x"] - mx), abs(e["y"] - my)) <= 2 for e in s.einheiten_alle())
    per_befehl = not selbst and not l.warte_takte(LORD_WEG, lambda: im_ring() or not lebt())
    if per_befehl:
        k.liste([{"toeteAlle": {"spieler": 2, "typen": [55]}}], lf.KANAL)
    gefallen = l.warte_takte(LORD_SELBST if selbst else LORD_GRENZE, lambda: not lebt())  # selbst: P362 braucht einen echten Toeter, der Testbefehl gibt kein Gold
    tod = s.takt()
    ende = gefallen and l.warte_takte(NACH_LORD, lambda: k.peek(lf.GAMEOVER)[0] != 0)
    lage = {"per_befehl": per_befehl, "gefallen": gefallen, "tod": tod, "ende_gemerkt": ende, "gameover": k.peek(lf.GAMEOVER)[0], "ansicht": k.peek(lf.ANSICHT)[0]}
    b = lk.anhalten(l)
    pfad = l.rek.pfad
    stand = l.rek.beenden()
    with open(pfad + ".plan.json", "w", encoding="utf-8") as f:
        json.dump({"szene": name, "von": a, "bis": b, "tempo": lf.TEMPO_JEDER_TAKT, "lord": lord, **plan, **lage}, f, ensure_ascii=False)
    k.befehl({"menue": HAUPTMENUE}, 1.5)  # eine haengende Partie wird ueber den Kanal zurueckgesetzt, nicht beendet
    return {"szene": name, "von": a, "bis": b, **lage, "stand": stand, "pfad": pfad}


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
    "laufen_trupp": Szene("laufen_trupp", 200, False, GRENZE_TRUPP, aufbau_laufen, befehle_laufen_trupp, alle_am_ziel, treffer_noetig=False),
    "reichweite": Szene("reichweite", 200, False, GRENZE_BAHN, aufbau_reichweite, befehle_auf_partner),
    "schussweite": Szene("schussweite", 200, False, GRENZE_SCHUSSWEITE, aufbau_schussweite, befehle_auf_partner),
    "schussweite_pfeil": Szene("schussweite_pfeil", 200, False, GRENZE_SCHUSSWEITE, lambda l: aufbau_schussweite(l, FAELLE_PFEIL), befehle_auf_partner),
    "laufziel": Szene("laufziel", 100, False, GRENZE_PENDEL, aufbau_laufziel, befehle_laufziel, pendeln, treffer_noetig=False, am_ende_am_ziel=False),  # Tempo 100: fast jeder Takt (2 von 498 fehlten), ohne Abbruch bei einem gemischten Rahmen. Streng brach es 03.11. 20:37 nach 630 Takten ab
    "haltung": lambda l: szene_haltung(l, FAELLE_HALTUNG[:10], "haltung"),
    "haltung2": lambda l: szene_haltung(l, FAELLE_HALTUNG[10:], "haltung2"),
    "besatzung": lambda l: szene_geraete(l, "besatzung", aufbau_besatzung, befehle_besatzung, 200, GRENZE_GERAET),
    "belagerung": lambda l: szene_geraete(l, "belagerung", aufbau_belagerung, befehle_belagerung, 500, GRENZE_BELAGERUNG),
    "geraete_weite": lambda l: szene_geraete(l, "geraete_weite", aufbau_geraete_weite, befehle_auf_geraet, 500, GRENZE_GERAETE_WEITE),
    "punkt": szene_punkt,
    "sonder1": lambda l: szene_sonder(l, "sonder1", SONDER1),
    "sonder2": lambda l: szene_sonder(l, "sonder2", SONDER2),
    "sonder_g": lambda l: szene_sonder(l, "sonder_g", SONDER_G),
    "sonder2_g": lambda l: szene_sonder(l, "sonder2_g", sonder_g2(l)),
    "sonder3": lambda l: szene_sonder(l, "sonder3", sonder3(l)),
    "sonder3_g": lambda l: szene_sonder(l, "sonder3_g", sonder3_g(l), frei_maske=burgbereich(l), rand=10, raeumen=True),
    "sonder4_g": lambda l: szene_sonder(l, "sonder4_g", sonder4_g(l), frei_maske=burgbereich(l), rand=10, raeumen=True),
    "sonder5": lambda l: szene_sonder(l, "sonder5", sonder5(l)),
    "sonder5_g": lambda l: szene_sonder(l, "sonder5_g", sonder5_g(l), frei_maske=burgbereich(l), rand=10, raeumen=True),
    "sonder6_g": lambda l: szene_sonder(l, "sonder6_g", sonder6_g(l), frei_maske=burgbereich(l, sp=2), rand=10, raeumen=True),
    "sonder8": lambda l: szene_sonder(l, "sonder8", sonder8(l), rand=15),
    "sonder10": lambda l: szene_sonder(l, "sonder10", sonder10(l), rand=15),
    "sonder10_g": lambda l: szene_sonder(l, "sonder10_g", sonder10_g(l), frei_maske=burgbereich(l), rand=10, raeumen=True),
    "sonder12": lambda l: szene_sonder(l, "sonder12", sonder12(l), rand=15),
    "sonder13": lambda l: szene_sonder(l, "sonder13", sonder13(l), rand=15),
    "sonder14": lambda l: szene_sonder(l, "sonder14", sonder14(l), rand=15),
    "sonder17": lambda l: szene_sonder(l, "sonder17", sonder17(l), rand=15),
    "sonder15_g": lambda l: szene_sonder(l, "sonder15_g", sonder15_g(l), rand=15, raeumen=True),
    "sonder16_g": lambda l: szene_sonder(l, "sonder16_g", sonder16_g(l), rand=15, raeumen=True),
    "sonder11_g": lambda l: szene_sonder(l, "sonder11_g", sonder11_g(l), frei_maske=burgbereich(l), rand=10, raeumen=True),
    "sonder8_g": lambda l: szene_sonder(l, "sonder8_g", sonder8_g(l), rand=15, raeumen=True),
    "sonder9_g": lambda l: szene_sonder(l, "sonder9_g", sonder9_g(l), frei_maske=burgbereich(l), rand=10, raeumen=True),
    "lord2_g": lambda l: szene_lord(l, "lord2_g", True),
    "sonder7_g": lambda l: szene_sonder(l, "sonder7_g", tuple(z for z in sonder6_g(l) if z[0] in ("mauer", "abbruch")), frei_maske=burgbereich(l, sp=2), rand=10, raeumen=True),  # die Graeber fielen vor dem Graben durch die Starttruppen (Lauf 22:41)
    "gebaeude_nah": Szene("gebaeude_nah", lf.TEMPO_JEDER_TAKT, True, GRENZE_NAH_GEBAEUDE, aufbau_gebaeude_nah, befehle_gebaeude_nah, treffer_noetig=False),
    "laufen_trupp_g": Szene("laufen_trupp_g", 200, False, GRENZE_TRUPP, lambda l: aufbau_laufen(l, OHNE_LORD), befehle_laufen_trupp, alle_am_ziel, treffer_noetig=False),
    "reichweite_g": Szene("reichweite_g", 200, False, GRENZE_BAHN, lambda l: aufbau_reichweite(l, OHNE_LORD), befehle_auf_partner),
    "laufen_g": Szene("laufen_g", 200, False, GRENZE_LAUF, lambda l: aufbau_laufen(l, OHNE_LORD), befehle_laufen, alle_am_ziel, treffer_noetig=False),
    "nahkampf_g": Szene("nahkampf_g", lf.TEMPO_JEDER_TAKT, True, GRENZE_NAH_G, lambda l: aufbau_nahkampf(l, OHNE_LORD)),
    "beschuss_g": Szene("beschuss_g", lf.TEMPO_JEDER_TAKT, True, GRENZE_SCHUSS, lambda l: aufbau_beschuss(l, OHNE_LORD, dy=10)),  # im Gefecht ist weniger frei; der Abstand der Reihen ist hier nicht die Pruefgroesse, Schuetzen schiessen ohnehin weiter
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
    if not sz.treffer_noetig and fertig and not am_ziel and not sz.masse and sz.am_ende_am_ziel:
        l.wirkung(f"Szene {sz.name}: nicht alle am Ziel", False, takte=b - a)
    with open(pfad + ".plan.json", "w", encoding="utf-8") as f:
        json.dump({"szene": sz.name, "von": a, "bis": b, "tempo": sz.tempo, **plan}, f, ensure_ascii=False)
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
