# -*- coding: utf-8 -*-
"""Feldzug der Streitkolbenkaempfer (Daniel 18.10.2026: "maximal 20 Assassinen ... den Rest komplett in Wirtschaft und
Waffenproduktion ... 30 Streitkolben pro Nomade (Ueberlebende zaehlen auch) ... gestackt ... eins nach dem anderen ...
alle Einheiten sollten irgendwas Begruendetes machen, nicht nur sinnvoll rumstehen").

Ablauf je Runde (schritt):
  ZIEL     der naechste lebende feindliche Lord (Schach-Abstand zu unserem Bergfried); bleibt, bis er tot ist.
  SAMMELN  alle Streitkolben an einen Sammelpunkt auf der Linie Bergfried -> Ziel-Lord, so weit vorn wie moeglich, aber
           mehr als SICHER Felder von jedem feindlichen Fernkaempfer und Gebaeude (dort schiesst niemand). Wer dort steht und
           einen Feind in VERTEIDIGEN Feldern sieht, greift ihn an (statt zu stehen). Neu befohlen wird nur, wer nicht dort
           ist und nicht dorthin laeuft.
  ANGRIFF  sobald N am Sammelpunkt stehen (Ueberlebende zaehlen) und der Lord Schaden nimmt (ab LORD_SCHUTZ_BIS):
           19.10. (1018y, Daniel: "die Streitkolben lassen sich unnoetig von den Fernkaempfern ablenken und werden die
           ganze Zeit erschossen, weil sie nicht einfach auf den Lord gehen; von der Seite angreifen macht keinen Sinn -
           obenrum haetten die Bogenschuetzen sie erst am Ende erkannt"): als Haufen per LAUF-Befehl (laeuft an Feinden
           vorbei, klettert auf den Bergfried) ueber Wegpunkte des Weges mit dem geringsten Beschuss (wegplaner, wie bei
           den Assassinen); erst wer ANGRIFF_NAH am Lord steht, bekommt den Angriffsbefehl auf ihn.
           Ist der Lord tot: naechstes Ziel, die Ueberlebenden sammeln neu, aufgefuellt wird auf N.
Anwerben/Kaufen macht erstes_spiel.ruestung_kaufen (Ziel N lebende Streitkolben, nur Gold ueber der Ruecklage).
"""
import os
import numpy as np
import gefahr as GF                # B-157: maximale Sicherheit, dann minimaler Widerstand
from parteien import freunde_von   # B-133: Freund/Feind aus den Mannschaften des Spiels (2v2)

STREITKOLBEN = 26
# 19.10. (Daniel, 1019f: 26 arab. Schwertkaempfer und 25 arab. Bogen standen am Bergfried, kein Streitkolben - "nur zum
# Verteidigen ist das Overkill ... danach besser verteilen um auch zu raiden"; "beim naechsten Run sollen beide Nomaden
# sterben"): das Heer sind alle eigenen Truppen dieser Arten, ausser der Heimwache (setzt erstes_spiel)
HEER = {24, 25, 26, 27, 28, 75, 22, 23, 70}
# B-134 Burg knacken: Torhaeuser (45 gross, 46 klein), Tuerme 74-78 (bauen.NACH_TYP). Zugbruecke 49 nicht mehr (20.10. gegen
# Franz: 6 Mal Ziel, ihr Leben blieb bei 100 stehen, keine einzige fiel - gefallen sind nur Torhaeuser 46 und ein Turm 74)
BURG_TEILE = {45, 46, 74, 75, 76, 77, 78}
ZUGBRUECKE = 49                  # B-256: nie Weg, nie Ziel (durchbruch.ZUGBRUECKE)
BALLISTE = 77                    # Einheitentyp Feuerballiste (sturm.py)
FERN_REICH = {22: 44, 23: 44, 70: 44}
LORD = 55
FERN = {22, 23, 70, 72, 74, 76}
# B-147 (abgelesen TribesState::giveTribeAnInstruction 0x00527C80): diese duerfen Mauern aufhacken (Speer, Pike, Streitkolben,
# Schwert, Ritter, Sklave, arab. Schwert) - Bogen, Armbrust, Assassinen, Schleuder, Feuerwerfer nicht
MAUER_TYPEN = {24, 25, 26, 27, 28, 71, 75}
TRUPPE = {22, 23, 24, 25, 26, 27, 28, 37, 55, 70, 71, 72, 73, 74, 75, 76}


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


# B-150 Feuer meiden (Daniel 21.10.2026 18:29 Bild: das Heer lief durch das Feuer der eigenen Brandstiftung; 19:29 "Feldzug soll
# Feuer meiden und dann teste auch wirklich mit Augen, ob es gemieden wird"). Gemessen L177/L178: Gebaeudefeuer schadet bis 3
# Felder, Bodenfeuer auf dem Feld und daneben, der Boden einer Plantage brennt weiter, wenn das Gebaeude aus ist.
FEUER_GEBAEUDE_R = 4       # Sicherheitsabstand um ein brennendes Gebaeude (3 gemessen + 1)
FEUER_BODEN_R = 3          # Sicherheitsabstand um jedes brennende Feld (1 gemessen + 2 fuers Ausbreiten)
# Augen-Test 19:38 (WIDERLEGT mit 4/2): bei einer Plantage brennen Baeume und Boden grossflaechig - das Bodenfeuer lief bis 8
# Felder ueber den Umweg-Punkt hinaus. Felder-Betriebe (Getreide 30, Hopfen 31, Apfel 32, Milch 33) bekommen darum 10.
FEUER_FELD_R = 10
FELD_TYPEN = {30, 31, 32, 33}


def feuerorte(G, boden):
    """[(x, y, r)] aller Feuer: brennende Gebaeude (feuer > 0) und brennende Felder."""
    orte = [(g["x"], g["y"], FEUER_FELD_R if g.get("typ") in FELD_TYPEN else FEUER_GEBAEUDE_R)
            for g in G.values() if g.get("feuer", 0) > 0]
    return orte + [(x, y, FEUER_BODEN_R) for x, y in boden]


def _abstand_strecke(p, a, b):
    """kuerzester Abstand (euklidisch) von Punkt p zur Strecke a-b."""
    ax, ay, bx, by, px, py = a[0], a[1], b[0], b[1], p[0], p[1]
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    qx, qy = ax + t * dx, ay + t * dy
    return ((px - qx) ** 2 + (py - qy) ** 2) ** 0.5


def _frei(a, b, orte):
    return all(_abstand_strecke((x, y), a, b) > r for x, y, r in orte)


def im_feuer(p, orte, rand=0):
    """Liegt p naeher an einem Feuer als dessen Sicherheitsabstand (+ rand)? (Schachabstand)"""
    return any(max(abs(p[0] - x), abs(p[1] - y)) <= r + rand for x, y, r in orte)


def feuerfrei_punkt(p, orte, nach=None, bis=25):
    """Der naechste Punkt um p, der in KEINEM Feuer liegt - Ring fuer Ring (Schachabstand 1, 2, ...), auf einem Ring der
    naechste an nach. p selbst, wenn es frei ist; None, wenn bis `bis` Felder alles brennt. (Das alte Verschieben schob
    ein Ziel aus einem Feuer heraus, ohne die anderen nachzusehen, und konnte so im naechsten landen - Pruefung 33.)"""
    nah = [f for f in orte if max(abs(p[0] - f[0]), abs(p[1] - f[1])) <= bis + f[2] + 1]
    if not im_feuer(p, nah):
        return p
    for d in range(1, bis + 1):
        ring = [(p[0] + dx, p[1] + dy) for dx in range(-d, d + 1) for dy in range(-d, d + 1) if max(abs(dx), abs(dy)) == d]
        frei = [q for q in ring if not im_feuer(q, nah)]
        if frei:
            return min(frei, key=lambda q: (schach(q, nach) if nach else 0, q))
    return None


def feuerweg(start, ziel, orte, schritt=2, rand=12):
    """B-150 (Daniel 21.10. 20:23: "warum sollten sie neben dem Feuer warten? dann verbrennen sie - sie sollten aussen herum
    laufen, gerade beim Angriff zaehlt jede Sekunde"): kuerzester Weg um alle Feuer herum - A* auf einem Raster mit `schritt`
    Feldern (gesperrt ist jeder Rasterpunkt im Feuer), Suchfeld = Rechteck um Start und Ziel plus `rand` und den groessten
    Sicherheitsabstand. Danach geglaettet: von jedem Punkt der weiteste, zu dem die gerade Strecke frei ist.
    Gibt die Wegpunkte bis ziel (ohne start); None, wenn im Suchfeld kein Weg ist."""
    import heapq
    rmax = max(f[2] for f in orte)
    x0, x1 = min(start[0], ziel[0]) - rand - rmax, max(start[0], ziel[0]) + rand + rmax
    y0, y1 = min(start[1], ziel[1]) - rand - rmax, max(start[1], ziel[1]) + rand + rmax
    nah = [f for f in orte if x0 - f[2] <= f[0] <= x1 + f[2] and y0 - f[2] <= f[1] <= y1 + f[2]]
    sx, sy = start
    gesperrt = set()                           # Rasterpunkte (i, j) im Feuer: Punkt = (sx + i*schritt, sy + j*schritt)
    for x, y, r in nah:
        for i in range(-((sx - (x - r)) // schritt), (x + r - sx) // schritt + 1):
            for j in range(-((sy - (y - r)) // schritt), (y + r - sy) // schritt + 1):
                gesperrt.add((i, j))
    i0, i1 = -((sx - x0) // schritt), (x1 - sx) // schritt
    j0, j1 = -((sy - y0) // schritt), (y1 - sy) // schritt
    punkt = lambda k: (sx + k[0] * schritt, sy + k[1] * schritt)
    h = lambda k: schach(punkt(k), ziel) / float(schritt)
    offen, her, kosten, am_ziel = [(h((0, 0)), 0, (0, 0))], {(0, 0): None}, {(0, 0): 0}, None
    while offen:
        _, g, k = heapq.heappop(offen)
        if g > kosten[k]:
            continue
        if schach(punkt(k), ziel) <= schritt and _frei(punkt(k), ziel, nah):
            am_ziel = k
            break
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                q = (k[0] + di, k[1] + dj)
                if q == k or q in gesperrt or not (i0 <= q[0] <= i1 and j0 <= q[1] <= j1):
                    continue
                if g + 1 < kosten.get(q, 1 << 30):
                    kosten[q], her[q] = g + 1, k
                    heapq.heappush(offen, (g + 1 + h(q), g + 1, q))
    if am_ziel is None:
        return None
    pfad = [am_ziel]
    while her[pfad[-1]] is not None:
        pfad.append(her[pfad[-1]])
    pfad = [punkt(k) for k in reversed(pfad)] + [tuple(ziel)]
    weg, i = [], 0
    while i < len(pfad) - 1:
        j = len(pfad) - 1
        while j > i + 1 and not _frei(pfad[i], pfad[j], nah):
            j -= 1
        weg.append(pfad[j])
        i = j
    return weg


def feuerfreier_weg(start, ziel, orte, gefahr=None):
    """Wegpunkte von start nach ziel, die an keinem Feuer naeher als sein Sicherheitsabstand vorbeifuehren: [ziel], wenn die
    gerade Strecke frei ist; sonst der Weg AUSSEN HERUM (feuerweg; Daniel 20:23: nicht neben dem Feuer warten). Liegt das
    Ziel selbst im Feuer, gilt der naechste feuerfreie Punkt daneben; steht der Start im Feuer, geht es zuerst hinaus.
    Gibt es keinen Weg herum, wird abgewogen (Daniel 20:27: "warten und schuetzen, aber potentiell abgeschossen werden,
    oder Schaden durch Feuer"): gefahr(p) = Zahl der Feindschuetzen, die p erreichen - ist der Platz davor sicher, wird
    dort gewartet, bis das Feuer aus ist; sonst (oder ohne gefahr) direkt durch."""
    if not orte:
        return [ziel]
    z = feuerfrei_punkt(ziel, orte, nach=start) or tuple(ziel)
    s, vorweg = start, []
    if im_feuer(start, orte):
        s = feuerfrei_punkt(start, orte, nach=z) or start
        vorweg = [s] if s != start else []
    if _frei(s, z, orte):
        return vorweg + [z]
    for rand in (12, 30, 60):                  # breite Feuerwand: Suchfeld in Stufen groesser (Pruefung 37)
        weg = feuerweg(s, z, orte, rand=rand)
        if weg:
            return vorweg + weg
    if gefahr is not None and gefahr(s) == 0:
        return vorweg or [start]                # in Deckung warten, bis das Feuer aus ist
    return vorweg + [z]


class Feldzug:
    N = 30                    # je Nomade (Daniel)
    TRUPP = 1                 # Daniel 22.10.: jede Einheit einzeln, gleicher Angriffspunkt statt Formation.
    MAUER_R = 30              # B-147: so weit um den Lord sucht logik.lua die Mauerkachel (Burgradius wie BURG_R-Groessenordnung)
    SICHER = 50               # Felder Abstand des Sammelpunkts zu feindlichen Fernkaempfern (Reichweite 44 + Rand)
    SAMMEL_HEIM = 12          # B-247 (Daniel 25.10. 14:51, Lauf 144300: der Einkaeufer kauft 1-2 je Runde, jede lief einzeln zum
                              # Sammelpunkt 48 Felder vor dem Feind-Lord und starb): gesammelt wird so viele Felder vor dem
                              # eigenen Bergfried Richtung Feind; vorgerueckt wird erst, wenn die Gefechtsrechnung lohnt - dann
                              # alle zusammen (Phase angriff, sicherer Weg). Nach einem Sieg gilt die Front des Heeres (Startwert)
    GEB_ABSTAND = 30          # ... und zu feindlichen Gebaeuden (Tuerme, Mauern mit Schuetzen)
    AM_PUNKT = 10             # so nah am Sammelpunkt gilt als "da"
    VERTEIDIGEN = 18          # Feind so nah am Sammelpunkt -> angreifen
    WIEDERHOLEN = 5           # Runden zwischen zwei Angriffsbefehlen
    ANGRIFF_NAH = 4           # so nah am Lord: Angriffsbefehl statt Laufbefehl
    WEGPUNKT_NAH = 4          # so nah am Wegpunkt (Mitte des Haufens): naechster Wegpunkt
    MIN_ANGRIFF = 8           # 19.10.: so viele am Sammelpunkt mindestens, dann entscheidet die Gefechtsrechnung
    LORD_UMKREIS = 25         # 19.10.: feindliche Truppen so nah am Lord kaempfen mit (Gefechtsrechnung)
    PARTNER_R = 60            # B-207: Truppen des Verbuendeten bis hierhin um die Angriffsstelle zaehlen mit (Startwert, UNGEMESSEN)
    RECHNEN_ALLE = 5          # 19.10.: Gefechtsrechnung beim Sammeln je so viele Runden
    # 19.10. (1019h, Daniel: "hier werden einfach 50 Einheiten gesammelt ohne anzugreifen - alle werden nach und nach
    # abgeschossen, ohne sich zu bewegen"; Feldzug-Stand: 79 Mann, naechster 6 Felder vom Lord, Wegpunkt 14/15, am Lord 0 -
    # die Mitte kam nie bis 4 Felder an den vorletzten Wegpunkt vor dem Bergfried): ab SCHLUSS_R Feldern (die Spitze) kein
    # Wegpunkt mehr - alle bekommen den Angriffsbefehl auf den Lord (das Spiel sucht den Weg, auch die Treppe hinauf)
    SCHLUSS_R = 25
    WEGPUNKT_HALB = 10        # 19.10.: naechster Wegpunkt, sobald die Haelfte der Spitzengruppe so nah dran ist
    SPITZE_TIEFE = 25         # 19.10. (1019i): Spitzengruppe = bis so viele Felder hinter dem vordersten
    # 19.10. (Daniel: "es macht keinen Sinn, dass arabische Bogenschuetzen im Team mit Schwertkaempfern laufen - sie sollten
    # eher schiessen, wenn sie koennen"): Schuetzen des Heeres nehmen im Angriff den naechsten Feind in Reichweite (zuerst
    # Schuetzen), statt im Haufen zu laufen
    SCHUETZEN_ZIEL_R = 40
    # 19.10. (1018l: der Endspurt-Angriff hing ab Tick 39.464 ueber 10.000 Ticks bei "Wegpunkt 2/20", der vorderste immer 157
    # Felder vor dem Lord; 1018k Spieler 2 ebenso bei Wegpunkt 2/12): kommt die Spitze STAU_TICKS lang keinen Schritt naeher,
    # wird der Wegpunkt uebersprungen, beim zweiten Stau greifen alle direkt den Lord an (das Spiel sucht den Weg).
    # 1.500 Ticks: ein arab. Schwertkaempfer laeuft darin ~77 Felder (L80: 19,5 Takte je Feld)
    STAU_TICKS = 1500
    # B-139 Schwachstelle (Daniel 20.10. 20:52, Bild: unsere Truppen standen vor Franz' Burg herum - "sei aggressiver, gehe
    # aufs Torhaus oder die groesste Schwachstelle bei der Burg"): steht am Ziel-Lord eine Burg (feindliche Torhaeuser/Tuerme
    # bis BURG_R Felder vom Lord), gehen ab dem ersten Angriffsschritt ALLE Nahkaempfer auf ihren schwaechsten Teil (wenigstes
    # Leben), die Schuetzen ziehen mit und schiessen die Verteidiger. Kein Sammeln davor, kein Warten auf Staus. Faellt er,
    # geht es auf den Lord; kommt die Spitze dann STAU_TICKS lang nicht naeher, sofort der naechste Teil. Ersetzt die
    # Sturmwelle B-138 (Sammeln ausser Reichweite = Herumstehen). Gemessen: Torhaeuser lagen 3-6 Felder vom Lord
    # (Rotkaeppchen 264, Franz 274); 30 deckt auch aeussere Ringe
    BURG_R = 30
    TOR_R = 25                # so nah an der Bresche gilt als "davor"
    # B-138: verliert die Bresche BRESCHE_ZAEH Ticks lang kein Leben, obwohl mindestens TOR_MIN davor stehen, ist sie zaeh
    # (Zugbruecke gegen Franz: Leben blieb bei 100) - verwerfen, naechste Schwachstelle
    BRESCHE_ZAEH = 1200       # (B-140 22:16: 3.000 liess 35 Mann unter Beschuss stehen; 1.000 -> 1.200 s. BRESCHE_WIRKUNG)
    # B-258 (gemessen 27.10., Partien 001937/003034: Tuerme 198 und 213 - erster Schaden 937 bzw. <= 738 Takte nach der Wahl,
    # danach 1.500 -> 410 bzw. gefallen in ~1.500 Takten): so lange ohne jeden Lebenspunkt Schaden, bevor ein Gebaeude verworfen wird
    BRESCHE_WIRKUNG = 1200
    TOR_MIN = 5
    # B-162 Abfangen (Daniel 21.10. 21:16 "Einheiten besiegen, die auf dem Weg sind, z.B. Fernkaempfer - dann nur die minimale
    # Anzahl, die zum Toeten reicht"; 21:40 "erkannt werden, welche Schuetzen ueberhaupt erreichbar sind - viele stehen auf
    # Mauern"): so viele Takte darf das Toeten eines Schuetzen dauern (gefahr.mindestzahl) - UNGEMESSEN
    ABFANG_TAKTE = 100
    ABFANG_ANTEIL = 3         # hoechstens jeder dritte Nahkaempfer faengt ab, der Rest bleibt beim Angriff
    # B-163/B-164/B-165 (Daniel 21.10. 21:59, Bild: "literally freie Fahrt auf den Koenig, aber lieber aufs Torhaus"; "mit
    # jeweils 1er-Stacks auf eine Mauer, mit einem Schredder durch alle Mauern, dann direkt drinnen"; 22:07 "vertraue mir, mit
    # einem Schredder hast du kombinierte Angriffswerte - schon durch den Turm-Test"):
    MAUER_TRUPP = 1           # B-164: jede Einheit ein eigener Mauerbefehl, alle auf dieselbe Kachel - der Schaden addiert sich
    # B-165: so lange ohne Fortschritt am Ziel, obwohl TOR_MIN daneben stehen -> umplanen. Bis 27.10. 300 (UNGEMESSEN); gemessen
    # 27.10. (Selbstspiel gegen den Zeitreisenden): Abstand zwischen zwei Kachel-Plaenen Median 1.083 Takte (99 Faelle, inkl. Laufen),
    # Partie 003727: Kachel (190,83) nach 401 Takten mit 15 Hackenden (107) verworfen - die Hoehe sinkt nicht stetig
    WIRKUNG_TAKTE = 1200
    WIRKUNG_NAH = 8           # B-165: "daneben" = so nah am Gebaeude (bis 7x7) bzw. bis 3 Felder an einer erreichbaren Mauer
    SCHREDDER_PAUSE = 1500    # B-165: Schredder ohne Wirkung -> so lange Bresche (Turm/Torhaus) statt Mauer
    # B-164 Durchbruch (Daniel 22:24 "er muss wirklich durch die ganze Mauer, nicht nur durch eine Schicht"; "rennt wieder aufs
    # Torhaus und laesst sich von der Feuerballiste abschiessen"):
    TORE = {45, 46, 75}       # gemessen 22:27 an Franz' Burg: Typ 75 hat einen Durchgang (4x4, Durchgang daneben ohne
    #                           Gebaeudenummer). B-256 (Partie 230627, bauen.NACH_TYP): 45/46 SIND die Torhaeuser
    #                           (BT_GATEHOUSELARGE/SMALL, je eine Zugbruecke 49 davor), 75 ist BT_TOWER2 - "46 ist ein Turm" war falsch
    TOR_RAND = 2              # so weit um den Torhaus-Grundriss ist fuer uns kein Weg (der Durchgang liegt am Rand)
    WAND_KOSTEN = 5           # Kosten je Hoehenpunkt einer Mauerkachel gegen 1 je gelaufenem Feld - UNGEMESSEN
    ANKUNFT_TAKTE = 1500      # so lange niemand bis 3 an der gewaehlten Kachel -> "KOMMT NICHT AN", verworfen (L80: ~77 Felder)

    def __init__(self, sp, heim, lord_schutz_bis=0, n=None):
        self.sp, self.heim, self.schutz_bis = sp, tuple(heim), lord_schutz_bis
        self._orte_f = []           # B-150: Feuer dieser Runde [(x, y, Sicherheitsabstand)]
        self._karte = None          # B-157: Gefahrenkarte dieser Runde (gefahr.Karte) - eine Wegsuche je Startpunkt
        self.heerweg = None         # B-150: (Mitte, Lord, Takt) im Angriff
        self.heerwege = []          # B-150: [(von, nach)] wo das Heer steht und wohin es laeuft - fuer den Brandtrupp
        if n:
            self.N = n
        self.ziel = None            # Nr des Ziel-Lords
        self.phase = "sammeln"
        self.punkt = None
        self.runde = 0
        self.letzter_befehl = -99
        self.tote_lords = []
        self.verteidigt = {}
        self.wegplaner = None       # (L, G, start, ziel) -> [Wegpunkte, letzter = ziel]; setzt erstes_spiel
        self.weg, self.weg_i, self.weg_ziel = [], 0, None
        self.verteidiger = set()    # 19.10.: Streitkolben, die der Waechter gerade zur Abwehr einsetzt - der Feldzug laesst sie
        self.heimwache = set()      # 19.10.: bleiben zu Hause (Waechter) - gehoeren nicht zum Heer
        self._rechnung = (-99, False, "")
        self._rechnung_alle = (-99, False, "")   # B-140: Gefechtsrechnung mit dem ganzen Heer
        self.endspurt = False       # 19.10. (endspurt.py): Wirtschaft verloren - angreifen, sobald die Haelfte da ist
        self._stau = (None, 0)      # 19.10.: (bester Abstand der Spitze zum Lord, seit Tick)
        self.staus = 0
        self.direkt = False         # 19.10.: nach zwei Staus alle direkt auf den Lord
        self.bresche = None         # B-134: Nr des Tors/Turms, das zuerst fallen muss
        self.lord_versuch = None    # B-139: Tick, seit dem nach einer gefallenen Bresche direkt auf den Lord gegangen wird
        self.wegtest = None         # B-139: (nr, punkte) -> [bool] - der Wegfinder des Spiels; setzt erstes_spiel
        self.wegkarte = None        # B-161: () -> speicher.wegkarte() (Gebiete aus dem Spielspeicher); setzt erstes_spiel
        self.wegkarte_fehler = None  # B-161: letzter Lesefehler der Wegkarte (dann ohne Gebiete wie vorher)
        self.mauerkarte = None      # B-164: besitzer -> (Mauerkacheln bool [x, y], Hoehe ueber Boden [x, y]); setzt erstes_spiel
        self.schredder = False      # B-164: der Lord liegt hinter Mauern - Einer-Stapel hacken die Mauer am Lord auf
        self.schredder_aus_bis = 0  # B-165: bis zu diesem Takt kein Schredder (er hatte keine Wirkung)
        self.mauer_kachel = None    # B-164: die EINE Mauerkachel, auf die alle Einer-Befehle gehen (Daniel 22:15 "keine Kompression")
        self.mauer_verworfen = set()  # B-165: Kacheln ohne Wirkung - die naechste kommt dran, nicht Torhaus/Turm
        self._bau = None            # B-164: Gebaeude-Ebene dieser Runde (speicher.wegkarte) - Burgteile sind fuer uns gesperrt
        self._feindbau = []         # B-164: Nummern feindlicher Burgteile dieser Runde
        self._kachel_an = None      # B-164: (Kachel, Takt, seit dem sie gewaehlt ist oder zuletzt jemand bis 3 daneben stand)
        self._wirkung_stand = {}    # B-165: Ziel -> (Wert, Takt seit dem letzten Fortschritt)
        self._lord_frei_alt = None  # B-163: letzter gemeldeter Stand "Lord zu Fuss erreichbar"
        self.vorposten = None       # B-139: (Bresche, erreichbarer Punkt vor ihr)
        self.lord_vp = None         # B-139: (Lord-Ort, erreichbarer Punkt am Lord oder None, Runde der Pruefung)
        self._lagebild = None       # B-140: Lagebild der laufenden Runde (Schuetzen fuer die Wahl der Angriffsstelle)
        self.angriff_ab = None      # B-140 Versuchsreihe (Daniel 22:09 "so viele Variablen ... dafuer die Tests"): fester
        #                             Angriffszeitpunkt ab so vielen Truppen statt der Gefechtsrechnung (Schalter angriff_ab)
        self.bresche_leben = None   # B-138: (niedrigstes Leben der Bresche, seit Tick)
        self.verworfen = set()      # B-138: zaehe Breschen - nicht noch einmal waehlen
        self.vp_verworfen = set()   # B-248: Vorposten, die der Wegtest spaeter als unerreichbar meldete - nicht noch einmal
        self._bresche_pruef = (None, -99)   # B-140: (Bresche, Runde) der letzten Pruefung mit dem Wegfinder
        self.mauer_seit = None      # B-147: Tick, seit dem die Mauer am eingemauerten Lord aufgehackt wird
        # B-170 (Daniel 22.10. 08:39 "er geht immer noch gegen Tuerme und einsame Mauern statt die aufzumachen, die zum Lord
        # fuehren"): hinter Mauern entscheidet der Durchbruch-Planer von sturm.py (durchbruch.py) - das ERSTE Hindernis auf dem
        # besten Weg zum Lord (Mauerkachel oder Torhaus), gehackt wie im Sturm: Zugangsfeld, Ziel festhalten, Blickrichtung
        self.durchbruch = None      # B-170: (sp, start, maenner, lord, verworfen=...) -> Plan (durchbruch.plane); setzt erstes_spiel
        self.blick = None           # B-170: (kachel, sp) -> (Anfrage-Kachel, Blickrichtung) (durchbruch.anfrage_und_blick)
        self.feldnr = None          # B-170: (x, y) -> Feldnummer des Spiels (durchbruch.feld) fuer logik.lua mauerziel
        self.absprache = None       # B-191: Pfad der gemeinsamen Durchbruch-Datei beider Lenker (setzt erstes_spiel im 2v2)
        self.dplan = None           # B-170: letzter Durchbruch-Plan (art, ziel, zug, weg, ...) mit Runde und Lord
        self.angesetzt = set()      # B-170: wer am Zugangsfeld die Kachel festgehalten bekam
        self._angesetzt_kachel = None
        self._dplan_meldung = None
        self._spur = {}             # B-146: je Nahkaempfer (Ort, Leben, still seit Tick, letzter Schaden bei Tick)

    NACHBAR_RINGE = (1, 2, 3)  # B-140: so nah am Gebaeude muss ein Feld erreichbar sein, sonst ist es nicht angreifbar
    DPLAN_RUNDEN = 10          # B-170: so viele Runden gilt ein Durchbruch-Plan, solange sein Ziel steht (Startwert; eine Planung
    #                            kostet Sekunden - sturm.py: 1-3 s)
    # B-146 (Daniel 21.10. 00:34 "ja bau die Rueckzugsregel und miss gegen die 107"): Stellschrauben, noch nicht gemessen
    RUECKZUG_TAKTE = 300       # so lange auf demselben Feld (Kern-Messung L170: STEHT NUR Median 345 Takte)
    RUECKZUG_SCHADEN = 1000    # Schaden innerhalb dieser Takte zaehlt als "unter Beschuss" (eine Lenker-Runde: 187-1.069 Takte)
    RUECKZUG_MIN = 5           # so viele muessen es sein - einzelne Nachzuegler loesen keinen Rueckzug aus

    def _steht_nur(self, L, nah_kampf, t):
        """B-146: Nahkaempfer, die seit RUECKZUG_TAKTE auf demselben Feld stehen, in den letzten RUECKZUG_SCHADEN Takten
        Leben verloren und weder Ziel noch Nahkampfgegner haben - "STEHT NUR" der Kern-Beschusswache (L169/L170)."""
        neu, stehen = {}, []
        befohlen = getattr(self, "_befohlen", {})
        for n in nah_kampf:
            e = L[n]
            ort = (e["x"], e["y"])
            alt = self._spur.get(n)
            still_seit = alt[2] if alt and alt[0] == ort else t
            schaden = alt[3] if alt else None
            if alt and e["leben"] < alt[1]:
                schaden = t
            neu[n] = (ort, e["leben"], still_seit, schaden)
            # (B-147, L175: wer eine Mauer aufhackt, hat zielart 0 und kein Nahziel - mit Mauerauftrag und nicht untaetig ist er
            # beschaeftigt, kein "steht nur"; in Pruefstand-Lauf 4 zog die Regel die Hacker 4-mal ab)
            hackt = befohlen.get(n, (None,))[0] in ("mauer", "zug") and e.get("zustand") not in (0, 1)
            hackt = hackt or (befohlen.get(n,(None,))[0]=="bresche" and e.get("zustand") in (106,107))
            if (t - still_seit >= self.RUECKZUG_TAKTE and schaden is not None and t - schaden <= self.RUECKZUG_SCHADEN
                    and not e.get("zielart", 0) and e.get("nahziel", 0) <= 0 and not hackt):
                stehen.append(n)
        self._spur = neu
        return stehen

    def _nachbar_punkte(self, G, nr):
        gx, gy = G[nr]["x"], G[nr]["y"]
        return [(gx + dx * r, gy + dy * r) for r in self.NACHBAR_RINGE
                for dx, dy in ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1))]

    @staticmethod
    def _breit(b, r):
        """bool-Feld um r Felder verbreitert (Schach-Abstand) - ohne scipy, die Karte hat einen leeren Rand."""
        aus = b.copy()
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if dx or dy:
                    aus |= np.roll(np.roll(b, dx, 0), dy, 1)
        return aus

    def _lage_lord(self, L, lp, nah_kampf, besitzer, mitte=None):
        """B-163/B-164: mit Wegkarte (Gebiete des Spiels) - None ohne. Gebiet unseres Heeres = das haeufigste der Nahkaempfer.
        frei: Feld bis LORD_RINGE am Lord in unserem Gebiet, wenn der Lord selbst in unserem Gebiet steht (oder auf einem Feld
        ohne Gebiet) - sonst None. Ohne freie Fahrt mit Mauerkarte: Mauerkacheln seines Besitzers bis MAUER_R um ihn, die ein
        Nachbarfeld in unserem Gebiet haben (Schredder), ihre Zahl, die Hoehe aller seiner Mauern dort (Fortschritt) und das
        Feld "bis 3 an einer solchen Kachel" (wer dort steht, hackt)."""
        k = self._karte
        if k is None or k.gebiete is None or not nah_kampf:
            return None
        zahl = {}
        for n in nah_kampf:
            g_ = k.gebiet_bei((L[n]["x"], L[n]["y"]))
            if g_:
                zahl[g_] = zahl.get(g_, 0) + 1
        if not zahl:
            return None
        g = max(zahl, key=lambda x: (zahl[x], -x))
        geb = k.gebiete
        g_lord = int(geb[lp[0], lp[1]]) if k.drin(lp) else 0
        frei = None
        kum = None
        if getattr(k,"links",None) is not None:
            von = min(((L[n]["x"],L[n]["y"]) for n in nah_kampf),key=lambda q:schach(q,mitte or lp))
            _, kum = k.suche(von)
        if g_lord in (g, 0):
            for r in self.LORD_RINGE:
                ring = [(lp[0] + dx, lp[1] + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                        if max(abs(dx), abs(dy)) == r]
                ring = [q for q in ring if k.drin(q) and geb[q[0], q[1]] == g and (kum is None or np.isfinite(kum[q]))]
                if ring:
                    frei = min(ring,key=lambda q:(kum[q],q)) if kum is not None else min(ring)
                    break
            if frei is None and g_lord == g and (kum is None or np.isfinite(kum[lp])):
                frei = tuple(lp)
        aus = {"gebiet": g, "gebiet_lord": g_lord, "frei": frei, "mauern": 0, "hoehe": None, "kachel": None, "hoehe_kachel": None}
        if frei is None and self.mauerkarte is not None:
            try:
                m, h = self.mauerkarte(besitzer)
            except Exception as ex:                      # Spiel nicht lesbar: ohne Schredder wie vorher
                self.wegkarte_fehler = "Mauerkarte: %s" % str(ex)[:100]
                return aus
            h = np.asarray(h)
            fen = np.zeros(m.shape, bool)
            fen[max(0, lp[0] - self.MAUER_R):lp[0] + self.MAUER_R + 1, max(0, lp[1] - self.MAUER_R):lp[1] + self.MAUER_R + 1] = True
            # B-164 (Daniel 22:15 "keine Kompression auf eine Mauer"; 22:24 "durch die ganze Mauer"): EINE Kachel fuer alle - die
            # erste auf dem Durchbruch-Weg vom Heer zum Lord; sie bleibt, solange sie steht und nicht verworfen ist
            if self.durchbruch is not None:
                pruef = min(nah_kampf, key=lambda n: schach((L[n]["x"], L[n]["y"]), mitte or lp))
                dp = self._durchbruch_neu(m, mitte or lp, lp, len(nah_kampf), pruef=pruef)
                if dp is not None and dp["art"] == "lord" and dp.get("weg"):
                    # B-193 (2v2 22.10. 18:19: "frei bis None" - der Planer fand einen Weg ohne Mauer, das Heer tat nichts): ein Weg
                    # ohne Hindernis ist freie Fahrt bis vor den Lord
                    aus.update(frei=tuple(dp["weg"][-2]) if len(dp["weg"]) > 1 else tuple(lp))
                    return aus
                kachel = dp["ziel"] if dp is not None and dp["art"] == "mauer" else None
                self.mauer_kachel = kachel
                wand_w = [q for q in dp["weg"] if m[q]] if dp is not None else []
                aus.update(mauern=len(wand_w), hoehe=int(h[m & fen].sum()), kachel=kachel,
                           hoehe_kachel=int(h[kachel]) if kachel else None, weg_hoehe=int(sum(h[q] for q in wand_w)),
                           zug=dp["zug"] if dp is not None else None,
                           tor=dp["ziel"] if dp is not None and dp["art"] in ("tor", "gebaeude") else None)
                return aus
            plan = self._durchbruch(geb, m, h, mitte or lp, lp)
            kachel = self.mauer_kachel
            if kachel is None or not m[kachel] or kachel in self.mauer_verworfen:
                kachel = plan["kachel"]
            self.mauer_kachel = kachel
            aus.update(mauern=plan["n"], hoehe=int(h[m & fen].sum()), kachel=kachel,
                       hoehe_kachel=int(h[kachel]) if kachel else None, weg_hoehe=plan["hoehe"])
        elif frei is not None:
            if self.dplan is not None and self.dplan.get("art") in ("mauer", "tor", "gebaeude"):
                self._dplan_vor_frei = self.dplan          # B-262: fuer "wieder hinter Mauern"
            self.dplan = None
        return aus

    NAHE_SCHUETZE_R = 4        # B-177: so nah muss ein feindlicher Schuetze stehen, dass ein freier Nahkaempfer ihn sofort angreift

    def _nahe_schuetzen(self, L, kolben, befehl, aus):
        """B-177 (Daniel 22.10. 18:15, Bild: "ein Schwertkaempfer stand einfach nur da und ist nicht auf die Bogenschuetzen
        gegangen, obwohl diese direkt neben ihm waren"): in JEDER Phase greift ein Nahkaempfer, der untaetig ist (Zustand 0/1) und
        keinen Mauer-/Zugang-/Abfang-Auftrag hat, den naechsten feindlichen Fernkaempfer oder die naechste Feuerballiste bis
        NAHE_SCHUETZE_R Felder an - nur im selben Gebiet (zu Fuss erreichbar, nicht auf der Mauer)."""
        import gefecht
        bef = getattr(self, "_befohlen", {})
        self._befohlen = bef
        k = self._karte
        feinde = [(n, e) for n, e in L.items() if e.get("besitzer") not in freunde_von(self.sp) and e.get("leben", 1) > 0
                  and (e.get("typ") in gefecht.FERN_REICH or e.get("typ") == BALLISTE)]
        if not feinde:
            return
        neu = {}
        for n in kolben:
            e = L[n]
            if e.get("typ") in FERN_REICH or e.get("zustand") not in (0, 1) or bef.get(n, (None,))[0] in ("mauer", "zug", "abfang"):
                continue
            o = (e["x"], e["y"])
            nah = [(schach(o, (f["x"], f["y"])), fn) for fn, f in feinde if schach(o, (f["x"], f["y"])) <= self.NAHE_SCHUETZE_R]
            if k is not None and k.gebiete is not None:
                g = k.gebiet_bei(o)
                nah = [(d, fn) for d, fn in nah if k.drin((L[fn]["x"], L[fn]["y"]))
                       and int(k.gebiete[L[fn]["x"], L[fn]["y"]]) == g]
            if nah:
                neu.setdefault(min(nah)[1], []).append(n)
        for fn, ns in neu.items():
            befehl({"angriff": {"einheiten": sorted(ns), "ziel": fn}}, 1.0, bis="ANGRIFF")
            for n in ns:
                bef[n] = ("nah_schuetze", fn)
            aus.append("FELDZUG NAHER SCHUETZE: %d freie Nahkaempfer auf %d (Typ %d) direkt daneben" % (len(ns), fn, L[fn]["typ"]))

    def _abriss_gueltig(self, nr):
        from gebaeudeziele import angreifbar
        g = getattr(self,"_gebaeudebild",{}).get(nr)
        return bool(g and g.get("besitzer") not in freunde_von(self.sp)
                    and g.get("leben",0)>0 and angreifbar(g))

    WEITER_NAH, WEITER_NAH_GEB = 2, 6   # B-260: so nah muss die naechste Kachel am gefallenen Ziel liegen (sonst neu planen)
    LORD_WANDER = 5            # B-264: so weit darf der Lord laufen, ohne dass der Durchbruch-Plan neu berechnet wird (gemessen: 2 Felder)
    PLAN_VERSUCHE = 3          # B-256: so oft wird neu geplant, wenn der Zugang des Plans fuer uns nicht erreichbar ist

    def _durchbruch_neu(self, m, start, lp, maenner, pruef=None):
        """B-170: Durchbruch-Plan (durchbruch.plane) - neu, wenn keiner da ist, das Ziel gefallen/verworfen ist, der Lord woanders
        steht oder DPLAN_RUNDEN um sind; sonst der alte (die Planung kostet Sekunden)."""
        # B-191 (Daniel 22.10. 18:16 "eine Absprache mit dem Teammate beim Angriff, sodass nicht doppelt an zwei Stellen
        # aufgemacht wird"; gemessen 18:16: Sp1 hackte (144,89), Sp2 (135,95)): verworfene Stellen und der Plan des Partners
        # kommen aus der gemeinsamen Datei (self.absprache) - gibt es dort einen gueltigen Plan fuer diesen Lord, gilt er
        geteilt = self._absprache_lesen(lp)
        if geteilt is not None:
            self.mauer_verworfen |= {tuple(q) for q in geteilt.get("verworfen_kacheln", [])}
            self.verworfen |= set(geteilt.get("verworfen_tore", []))
            gp = geteilt.get("plan")
            if gp and gp.get("art") in ("mauer", "tor", "gebaeude") and gp.get("ziel") is not None:
                z_ = tuple(gp["ziel"]) if gp["art"] == "mauer" else gp["ziel"]
                gueltig = (gp["art"] == "mauer" and m[z_] and z_ not in self.mauer_verworfen) or \
                          (gp["art"] in ("tor", "gebaeude") and z_ not in self.verworfen)
                if gueltig and (self.dplan is None or (self.dplan["art"], self.dplan["ziel"]) != (gp["art"], z_)):
                    self.dplan = dict(gp, ziel=z_, zug=tuple(gp["zug"]) if gp.get("zug") else None,
                                      weg=[tuple(q) for q in gp.get("weg") or []], runde=self.runde, lord=tuple(lp))
                    self._dplan_meldung = "FELDZUG DURCHBRUCH (Absprache): Plan von Spieler %s uebernommen - %s %s, Zugang %s" % (
                        geteilt.get("von"), gp["art"], z_, self.dplan["zug"])
        dp = self.dplan
        # B-179 (2v2 22.10. 17:54: alle 10 Runden neu geplant vom wandernden Heer aus - (185,96) -> (147,123) -> (135,95), niemand
        # kam zum Hacken): der Plan bleibt, solange sein Ziel steht und nicht verworfen ist - wie sturm.py (Neuplanung nur nach Fall)
        # B-264 (Partie 010851: Torhaus 209 aufgegeben, weil der Lord von (223,100) nach (225,100) ging): bis LORD_WANDER Felder
        # Lord-Bewegung gilt der Plan weiter
        if dp is not None and schach(tuple(dp["lord"]), tuple(lp)) <= self.LORD_WANDER:
            if dp["art"] == "mauer" and m[dp["ziel"]] and dp["ziel"] not in self.mauer_verworfen:
                return dp
            if dp["art"] in ("tor", "gebaeude") and dp["ziel"] not in self.verworfen and ((dp["art"] == "gebaeude" and self._abriss_gueltig(dp["ziel"])) or (dp["art"] == "tor" and (not self._feindbau or dp["ziel"] in self._feindbau))):
                return dp
        # B-256 (Partie 230627: Gebaeude 109, 146, 145, 149 und Torhaus 180 gewaehlt, je 1-3 s spaeter "BRESCHE ABGESCHNITTEN" -
        # bei 146 erst nach 7.000 Takten Anmarsch): der Wegfinder des Spiels prueft den Zugang, BEVOR der Plan gilt; ist er nicht
        # erreichbar, wird die Stelle verworfen und neu geplant
        # B-260 (Partie 000651: Tunnel West (187..194, 90) nach 8 Kacheln aufgegeben, dann Nord (208, 58..61), dann Ost (239, 88) -
        # jede gefallene Kachel liess den Planer vom wandernden Heer aus neu rechnen und die Burgseite wechseln; Partie 234348
        # ebenso): ist das Ziel gefallen und liegt auf DEMSELBEN Plan-Weg noch eine Mauerkachel, geht es dort weiter - ohne neue
        # Planung (die kostet ~3 s). Neu geplant wird erst, wenn der Weg keine Kachel mehr hat oder sie verworfen ist.
        if dp is not None and schach(tuple(dp["lord"]), tuple(lp)) <= self.LORD_WANDER and dp.get("weg") and dp["art"] in ("mauer", "tor", "gebaeude"):
            gefallen = (not m[dp["ziel"]]) if dp["art"] == "mauer" else (dp["ziel"] not in (getattr(self, "_gebaeudebild", {}) or {}))
            w_ = [tuple(q) for q in dp["weg"]]
            if gefallen:
                zi = w_.index(tuple(dp["zug"])) if dp.get("zug") and tuple(dp["zug"]) in w_ else 0
                weiter = [i for i in range(zi + 1, len(w_)) if m[w_[i]] and w_[i] not in self.mauer_verworfen]
                # (Partie 010851: nach (204,59) sprang WEITER auf (203,65) - dazwischen kein Mauerfeld, aber auch kein Weg; 25-30 Mann
                # standen bei y 57-59 untaetig, "KOMMT NICHT AN" 3-mal): nur die anschliessende Kachel - bis WEITER_NAH Felder vom
                # gefallenen Ziel (nach einem Gebaeude WEITER_NAH_GEB, so breit sind Tor/Turm)
                nah_w = self.WEITER_NAH if dp["art"] == "mauer" else self.WEITER_NAH_GEB
                ref = tuple(dp["ziel"]) if dp["art"] == "mauer" else (tuple(dp["zug"]) if dp.get("zug") else w_[zi])
                weiter = [i for i in weiter if schach(w_[i], ref) <= nah_w]
                if weiter:
                    i = weiter[0]
                    neu = dict(dp, art="mauer", ziel=w_[i], zug=w_[i - 1], runde=self.runde)
                    self._dplan_meldung = ("FELDZUG DURCHBRUCH WEITER: %s %s gefallen - naechste Kachel %s auf demselben Weg (noch %d "
                                           "Kacheln), Zugang %s" % (dp["art"], dp["ziel"], w_[i], len(weiter), w_[i - 1]))
                    self.dplan = neu
                    self._absprache_schreiben(lp)
                    return neu
        if dp is not None:
            # B-264 (Partie 005758: Torhaus 237 nach < 2.000 Takten ohne Verwerf-Meldung durch die Westseite ersetzt): WARUM der
            # alte Plan nicht mehr gilt, steht im Log
            G_d = getattr(self, "_gebaeudebild", {}) or {}
            grund = ("Lord woanders (%s statt %s)" % (tuple(lp), tuple(dp["lord"])) if schach(tuple(dp["lord"]), tuple(lp)) > self.LORD_WANDER else
                     "Kachel gefallen" if dp["art"] == "mauer" and not m[dp["ziel"]] else
                     "Kachel verworfen" if dp["art"] == "mauer" else
                     "verworfen" if dp["ziel"] in self.verworfen else
                     "Gebaeude weg" if dp["ziel"] not in G_d else
                     "kein gueltiges Abrissziel" if dp["art"] == "gebaeude" else
                     "nicht in der Feindbau-Liste (%d Eintraege)" % len(self._feindbau or []) if dp["art"] == "tor" else dp["art"])
            if dp["art"] in ("mauer", "tor", "gebaeude"):
                self._plan_grund = "FELDZUG PLAN AUFGEGEBEN: %s %s - %s" % (dp["art"], dp["ziel"], grund)
        for _v in range(self.PLAN_VERSUCHE):
            try:
                neu = self.durchbruch(self.sp, tuple(start), max(1, maenner), tuple(lp),
                                      verworfen=set(self.mauer_verworfen) | set(self.verworfen))
            except Exception as ex:
                self.wegkarte_fehler = "Durchbruch: %s" % str(ex)[:120]
                neu = None
            if (neu is None or neu.get("art") not in ("mauer", "tor", "gebaeude") or not neu.get("zug")
                    or self.wegtest is None or pruef is None):
                break
            # (Partie 234348: Torhaus 77, 90, Gebaeude 95, 183, 320, 72 bestanden den Zugang-Test und waren 1-3 s spaeter
            # "ABGESCHNITTEN" - die Nachpruefung verlangt ein erreichbares Feld bis 3 um das Gebaeude; hier dieselbe Pruefung)
            G_b = getattr(self, "_gebaeudebild", {}) or {}
            nb = self._nachbar_punkte(G_b, neu["ziel"]) if neu["art"] != "mauer" and neu["ziel"] in G_b else []
            try:
                gut = self.wegtest(pruef, [tuple(neu["zug"])] + nb)
            except Exception:
                gut = None
            if gut is None or (gut[0] and (not nb or any(gut[1:]))):
                break
            if neu["art"] == "mauer":
                self.mauer_verworfen.add(tuple(neu["ziel"]))
            else:
                self.verworfen.add(neu["ziel"])
            self._zugang_verworfen = getattr(self, "_zugang_verworfen", []) + [(neu["art"], neu["ziel"], tuple(neu["zug"]))]
            neu = None
        # B-262 (Partie 004430: "Lord zu Fuss erreichbar" kam und ging 3-mal - Gebiet am Lord 60000, unser 1, Kachel (217,110)
        # stand weiter mit Hoehe 80 - der freie Weg fuehrte offenbar durch ein kurz offenes Tor; nach jeder "freien Fahrt" begann
        # der Durchbruch woanders): ein Hindernis-Plan, der von "frei" abgeloest wurde, gilt wieder, sobald wieder ein Hindernis
        # im Weg ist und sein Ziel noch steht
        vorher = getattr(self, "_dplan_vor_frei", None)
        if (neu is not None and neu.get("art") in ("mauer", "tor", "gebaeude") and vorher is not None
                and schach(tuple(vorher["lord"]), tuple(lp)) <= 3
                and ((vorher["art"] == "mauer" and m[vorher["ziel"]] and vorher["ziel"] not in self.mauer_verworfen)
                     or (vorher["art"] != "mauer" and vorher["ziel"] not in self.verworfen
                         and vorher["ziel"] in (getattr(self, "_gebaeudebild", {}) or {})))):
            self._dplan_meldung = "FELDZUG DURCHBRUCH ZURUECK: wieder hinter Mauern - weiter an %s %s statt neu bei %s %s" % (
                vorher["art"], vorher["ziel"], neu["art"], neu["ziel"])
            self.dplan, self._dplan_vor_frei = dict(vorher, runde=self.runde), None
            self._absprache_schreiben(lp)
            return self.dplan
        if neu is not None and neu.get("art") == "lord" and dp is not None and dp.get("art") in ("mauer", "tor", "gebaeude"):
            self._dplan_vor_frei = dp
        if neu is not None:
            neu = dict({k: neu.get(k) for k in ("art", "ziel", "zug", "weg", "takte", "belastung", "kandidaten")},
                       runde=self.runde, lord=tuple(lp))
            neu["weg"] = [tuple(q) for q in (neu["weg"] or [])]
            if dp is None or (dp["art"], dp["ziel"]) != (neu["art"], neu["ziel"]):
                self._dplan_meldung = ("FELDZUG DURCHBRUCH: bester Weg zum Lord %d - %s %s, Zugang %s, %s Takte, Beschuss-Last %s "
                                       "(Kandidaten Art/Ziel/Last/Takte: %s)" % (
                                           self.ziel, {"mauer": "Mauerkachel", "tor": "Torhaus", "gebaeude": "Gebaeude", "lord": "frei bis"}.get(neu["art"]),
                                           neu["ziel"], neu["zug"], neu["takte"], round(neu["belastung"] or 0), neu["kandidaten"]))
        self.dplan = neu
        self._absprache_schreiben(lp)
        return neu

    def _absprache_lesen(self, lp):
        if not self.absprache:
            return None
        try:
            import json
            d = json.load(open(self.absprache, encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return d if tuple(d.get("lord") or ()) == tuple(lp) else None

    def _absprache_schreiben(self, lp):
        """B-191: Plan und verworfene Stellen fuer den Partner (Lesen-Mischen-Schreiben, ersetzt per os.replace)."""
        if not self.absprache:
            return
        import json
        alt = self._absprache_lesen(lp) or {}
        d = {"lord": list(lp), "von": self.sp,
             "verworfen_kacheln": sorted({tuple(q) for q in alt.get("verworfen_kacheln", [])} | set(self.mauer_verworfen)),
             "verworfen_tore": sorted(set(alt.get("verworfen_tore", [])) | {v for v in self.verworfen if isinstance(v, int)}),
             "plan": None}
        if self.dplan is not None and self.dplan.get("art") in ("mauer", "tor", "gebaeude"):
            d["plan"] = {k: self.dplan.get(k) for k in ("art", "ziel", "zug", "weg", "takte", "belastung", "kandidaten")}
        tmp = "%s.neu%d" % (self.absprache, self.sp)
        try:
            json.dump(d, open(tmp, "w", encoding="utf-8"), default=list)
            os.replace(tmp, self.absprache)
        except OSError:
            pass

    BALLISTE_R = 30            # B-205: Feuerballiste so nah an einem unserer Nahkaempfer -> Ziel (Startwert, UNGEMESSEN)
    BALLISTE_MIN = 2           # B-182: so viele Nahkaempfer mindestens je Feuerballiste (im Sturm abgesprochen, Daniel 22.10.)
    ZUG_STILL = 300            # B-180: so lange nicht naeher am Zugang (und kein Gegner) -> Weg neu (wie RUECKZUG_TAKTE, L170)
    HACK_ANLAUF = 6           # B-147: Hackbefehl schon im Anmarsch so viele Felder vor dem Zugang (SRE AU36: nur aus 101)
    KETTE_DA = 4              # logik.lua wegketteTick: "da" bis 4 Felder um den Kettenpunkt
    KETTE_ABSTAND = 15         # B-180: Wegpunkte entlang des Plans (wie sturm.py NAH)

    def _kette_zum_zug(self, befehl, wer, L, zug):
        """B-180 wie sturm.kette: Wegkette entlang des Durchbruch-Plans (der Weg mit der kleinsten Beschuss-Last) ab dem Wegfeld,
        das jedem am naechsten liegt, bis zum Zugang - Maenner mit gleichem Einstieg als eine Kette. Ohne Plan-Weg direkt."""
        weg = list((self.dplan or {}).get("weg") or [])
        if zug not in weg:
            befehl({"angriff": {"einheiten": sorted(wer), "lauf": [zug[0], zug[1]], "trupp": 1}}, 1.0, bis="ANGRIFF")
            return
        w_ = weg[:weg.index(zug) + 1]
        gruppen = {}
        for n in wer:
            o = (L[n]["x"], L[n]["y"])
            i0 = min(range(len(w_)), key=lambda i: schach(w_[i], o))
            # B-147 (Daniel 26.10. 22:16 "kann noch nicht so schnell einen Eingang finden/freihauen", Partie 220717: Schwertkaempfer 39
            # stand 3.300 Takte auf (219,24) = seinem naechsten Planpunkt; jede Runde kam ein neuer Kettenbefehl ab genau diesem
            # Punkt, der loeste im Spielmodul die alte Kette, bevor sie weiterschalten konnte): steht er schon am naechsten
            # Planpunkt (Radius wie wegketteTick), beginnt seine Kette beim NAECHSTEN Kettenpunkt - jeder Befehl bringt ihn weiter
            if schach(w_[i0], o) <= self.KETTE_DA and i0 < len(w_) - 1:
                i0 = min(i0 + self.KETTE_ABSTAND, len(w_) - 1)
            pk = [tuple(q) for q in w_[i0::self.KETTE_ABSTAND]]
            if not pk or pk[-1] != tuple(zug):
                pk.append(tuple(zug))
            gruppen.setdefault(tuple(pk), []).append(n)
        for pk, ns in gruppen.items():
            a_ = {"einheiten": sorted(ns), "lauf": [pk[0][0], pk[0][1]], "trupp": 1}
            if len(pk) > 1:
                a_["danach"] = [[q[0], q[1]] for q in pk[1:]]
            befehl({"angriff": a_}, 1.0, bis="ANGRIFF")

    def _nicht_zurueck(self, L, ns, p, lp):
        """B-256: nur wer nicht naeher am Lord steht als der Wegpunkt p, darf einen Laufbefehl zu p bekommen."""
        return [n for n in ns if schach((L[n]["x"], L[n]["y"]), lp) >= schach(p, lp)]

    def _rest_weg(self, L, ns, ziel):
        """B-256 (Partie 230627: 5-mal "KOMMT NICHT AN" mit 65-99 Mann im Anmarsch - der sichere Weg fuehrt erst aussen herum,
        die Luftlinie zur Kachel wuchs dabei von 24 auf 32): Fortschritt = Restweg des vordersten Mannes ENTLANG des Plans bis
        ziel (Wegfelder ab seinem naechsten Planfeld plus sein Abstand dazu). Ohne Plan-Weg: die Luftlinie wie bisher."""
        weg = list((self.dplan or {}).get("weg") or [])
        if not ns:
            return 999
        if tuple(ziel) not in weg:
            return min(schach((L[n]["x"], L[n]["y"]), ziel) for n in ns)
        w_ = weg[:weg.index(tuple(ziel)) + 1]
        best = None
        for n in ns:
            o = (L[n]["x"], L[n]["y"])
            i = min(range(len(w_)), key=lambda j: schach(w_[j], o))
            r = len(w_) - 1 - i + schach(w_[i], o)
            best = r if best is None else min(best, r)
        return best

    def _mauerziel_los(self, befehl):
        """B-170: festgehaltenes Mauerziel dieses Lenkers loesen (logik.lua: mauerziel ohne halten -> aus)."""
        k_alt = self._angesetzt_kachel
        if k_alt is not None and self.feldnr is not None:
            k = self.feldnr(k_alt)
            if k is not None:
                befehl({"mauerziel": {"einheiten": [], "feld": k, "x": k_alt[0], "y": k_alt[1], "schluessel": "sp%d" % self.sp}}, 0.3)
        self.angesetzt, self._angesetzt_kachel = set(), None

    def _mauer_am_zug(self, L, wand, kq, zug, lp, befohlen, befehl, aus, t=0):
        """B-170 wie sturm.py (Franz' Burg 5-mal gebrochen): alle zum Zugangsfeld genau vor der Kachel; wer dort steht (bis 1 Feld),
        bekommt die Kachel als festgehaltenes Ziel (logik.lua mauerziel halten, je Lenker ein Schluessel) und den Angriffsbefehl
        mit der Blickrichtung, bei der das Spiel genau diese Kachel waehlt (22.10.: am Lord gewaehlte Kacheln hatten 3-mal "keine
        Wirkung", 2-mal "kommt nicht an")."""
        if self._angesetzt_kachel != kq:
            self._mauerziel_los(befehl)
            self._angesetzt_kachel = kq
        # B-147 (SRE AU36, handleUnitMovementWhenTargetingBuildings 0x0054C4F0): gehackt wird nur, wer LAUFEND (101) mit gesetztem
        # Mauerziel auf einem geraden Nachbarfeld ankommt - wer erst im Stand den Befehl bekommt, bleibt in 0/1 (Partie 220717:
        # 47 von 71 Mann untaetig neben (175,80), Hoehe 447 Takte unveraendert). Darum bekommt den Hackbefehl schon, wer im
        # Anmarsch (101) bis HACK_ANLAUF Felder vor dem Zugang ist; wer schon dort steht, wie bisher
        an = [n for n in wand if schach((L[n]["x"], L[n]["y"]), zug) <= 1
              or (L[n]["zustand"] == 101 and schach((L[n]["x"], L[n]["y"]), zug) <= self.HACK_ANLAUF)]
        # B-180: wer seit ZUG_STILL Takten nicht naeher kommt und niemanden angreift, bekommt den Weg neu
        spur = getattr(self, "_zug_spur", {})
        self._zug_spur = spur
        hin = []
        for n in wand:
            if n in an:
                continue
            d = schach((L[n]["x"], L[n]["y"]), zug)
            alt = spur.get(n)
            if alt is None or alt[2] != zug or d < alt[0]:
                spur[n] = (d, t, zug)
                alt = spur[n]
            still = t - alt[1] >= self.ZUG_STILL and not L[n].get("zielart", 0)
            if befohlen.get(n) != ("zug", zug) or L[n]["zustand"] in (0, 1) or still:
                hin.append(n)
                spur[n] = (d, t, zug)
        if hin:
            self._kette_zum_zug(befehl, hin, L, zug)
            for n in hin:
                befohlen[n] = ("zug", zug)
        neu = [n for n in an if n not in self.angesetzt or L[n]["zustand"] in (0, 1)]
        if not neu:
            return
        self.angesetzt |= set(neu)
        k = self.feldnr(kq)
        if k is not None:
            befehl({"mauerziel": {"einheiten": sorted(self.angesetzt), "feld": k, "x": kq[0], "y": kq[1], "halten": True,
                                  "schluessel": "sp%d" % self.sp}}, 0.3)
        try:
            ab = self.blick(kq, self.sp) if self.blick is not None else None
        except Exception:
            ab = None
        ab = ab or (tuple(kq), 0)
        befehl({"angriff": {"einheiten": sorted(neu), "mauer": [lp[0], lp[1], L[self.ziel]["besitzer"], self.MAUER_R,
                                                                ab[0][0], ab[0][1], ab[1]], "trupp": 1}}, 1.0, bis="ANGRIFF")
        for n in neu:
            befohlen[n] = ("mauer", kq)
        aus.append("FELDZUG MAUER AM ZUGANG: %d Mann an %s - Kachel %s festgehalten (Feld %s), Blick %d, zusammen %d angesetzt" % (
            len(neu), zug, kq, k, ab[1], len(self.angesetzt)))

    def _durchbruch(self, geb, m, h, start, lp):
        """B-164 Durchbruch-Planer: der billigste Weg vom Heer (start) zum Lord, auf dem die Mauerkacheln seines Besitzers (m)
        gehackt werden duerfen - je Kachel WAND_KOSTEN x Hoehe (Hoehe = Leben der Kachel, VillageStudio 5d belegt) plus Gefahr,
        je begehbares Feld 1 + K x Gefahr. Gesperrt: Wasser und alles ohne Gebiet (auch die Tor-Durchgaenge, schon aus geb
        geschnitten), feindliche Burgteile, verworfene Kacheln. Rueckgabe: erste Mauerkachel auf dem Weg (das Ziel), Zahl der
        Mauerkacheln auf dem Weg (Schichten), ihre Hoehe zusammen, der Weg. Ohne Weg: kachel None."""
        from skimage.graph import MCP
        k = self._karte
        boden = k.kosten if k is not None else np.ones(m.shape)
        gefahr_k = (k.k * k.g) if k is not None else 0
        kosten = np.where(geb > 0, boden, -1.0)
        kosten = np.where(m, self.WAND_KOSTEN * np.maximum(h, 1) + gefahr_k, kosten)
        if self._bau is not None and self._feindbau:
            kosten[np.isin(self._bau, self._feindbau)] = -1.0
        for q in self.mauer_verworfen:
            kosten[q[0], q[1]] = -1.0
        start, lp = tuple(start), tuple(lp)
        kosten[start] = max(float(kosten[start]), 1.0)
        kosten[lp] = 1.0
        # (B-166, 21.10. 22:45 abgelesen: handleUnitMovementWhenTargetingBuildings 0x0054C4F0 prueft bei einer MAUERKACHEL nur jede
        # zweite der 8 Richtungen - N, O, S, W; schraeg daneben beginnt nie ein Mauerangriff, Messung 22:41: 5.945 Takte kein Schlag.
        # Darum nur gerade Schritte - jede Kachel auf dem Weg hat ein gerades Zugangsfeld)
        mcp = MCP(kosten, fully_connected=False)
        kum, _ = mcp.find_costs([start], [lp])
        if not np.isfinite(kum[lp]):
            return {"kachel": None, "n": 0, "hoehe": 0, "weg": []}
        weg = [tuple(int(v) for v in q) for q in mcp.traceback(lp)]
        wand = [q for q in weg if m[q]]
        return {"kachel": wand[0] if wand else None, "n": len(wand), "hoehe": int(sum(h[q] for q in wand)), "weg": weg}

    def _ohne_feindtore(self, geb, bau, G):
        """B-164 (Pruefstand 22:13, Daniel 22:15 "zuerst aufs Torhaus, das war logischerweise zu, als die Einheiten da waren"):
        das Spiel zaehlt ein OFFENES feindliches Tor als Durchgang - Hof und offenes Feld waren dasselbe Gebiet, die gewaehlte
        Mauerkachel lag innen. Fuer uns ist kein feindliches Tor und kein Turm ein Weg: ihre Felder (Gebaeude-Ebene) werden aus
        den Gebieten geschnitten; zerfaellt ein Gebiet dadurch, bekommt jeder weitere Teil eine eigene Nummer ab 60000."""
        nrs = [nr for nr, g_ in G.items() if g_.get("besitzer") not in freunde_von(self.sp) and g_.get("typ") in BURG_TEILE]
        self._bau, self._feindbau = bau, nrs
        # B-256 (Daniel 26.10. 23:14 "die Zugbruecke wird ignoriert"): eine feindliche Zugbruecke ist fuer uns kein Weg - das Spiel
        # zaehlt sie heruntergelassen zum Gebiet, oben ist sie zu, wenn wir ankommen
        nrs = nrs + [nr for nr, g_ in G.items() if g_.get("besitzer") not in freunde_von(self.sp) and g_.get("typ") == ZUGBRUECKE]
        if bau is None or not nrs:
            return geb
        # (22:27 gemessen: der Durchgang eines Torhauses liegt NEBEN seinem Grundriss und traegt keine Gebaeudenummer - der
        # erste Schnitt nur ueber die Gebaeude-Ebene liess ihn offen, das Heer lief aufs Tor und unter die Feuerballiste)
        tore = [nr for nr in nrs if G[nr].get("typ") in self.TORE]
        schnitt = np.isin(bau, nrs) | (self._breit(np.isin(bau, tore), self.TOR_RAND) if tore else False)
        if not schnitt.any():
            return geb
        from scipy import ndimage
        neu = np.array(geb, np.int32, copy=True)
        betroffen = np.unique(neu[schnitt & (neu > 0)])
        neu[schnitt] = 0
        nr_frei = 60000
        for g_ in betroffen:
            teile, n = ndimage.label(neu == g_, structure=np.ones((3, 3), int))
            for c in range(2, n + 1):
                neu[teile == c] = nr_frei
                nr_frei += 1
        return neu

    def _wirkung(self, ziel, wert, nah, t, frist=None):
        """B-165 Wirkungswaechter: Fortschritt am Ziel je Runde (wert sinkt = Wirkung: Leben, Mauerhoehe). Stehen mindestens
        TOR_MIN eigene Nahkaempfer daneben (nah) und sinkt wert WIRKUNG_TAKTE lang nicht, Rueckgabe = Takte ohne Wirkung (und der
        Zaehler beginnt neu), sonst None. Wer nicht daneben steht, zaehlt nicht - Laufen ist keine fehlende Wirkung."""
        alt = self._wirkung_stand.get(ziel)
        if alt is None or wert < alt[0] or nah < self.TOR_MIN:
            self._wirkung_stand[ziel] = (wert, t)
            return None
        if t - alt[1] >= (frist or self.WIRKUNG_TAKTE):
            del self._wirkung_stand[ziel]
            return t - alt[1]
        return None

    DRAN_TAKTE = 900           # B-256: so lange TOR_MIN daneben und keiner schlaegt zu -> Ziel verworfen (3 x WIRKUNG_TAKTE, UNGEMESSEN)

    def _nicht_dran(self, ziel, nah, hack, t, wert, frist=None):
        """B-256: stehen TOR_MIN daneben, schlaegt DRAN_TAKTE lang keiner zu und sinkt wert (Leben/Hoehe) nicht, kommen wir nicht an
        das Ziel heran - Takte, sonst None."""
        st = getattr(self, "_dran_stand", {})
        self._dran_stand = st
        alt = st.get(ziel)
        if nah < self.TOR_MIN or hack > 0 or (alt is not None and wert < alt[1]):
            st.pop(ziel, None)
            return None
        if alt is None:
            st[ziel] = alt = (t, wert)
        t0 = alt[0]
        if t - t0 >= (frist or self.DRAN_TAKTE):
            del st[ziel]
            return t - t0
        return None

    def _zustaende(self, L, ns):
        z = {}
        for n in ns:
            z[L[n].get("zustand")] = z.get(L[n].get("zustand"), 0) + 1
        return ", ".join("%s: %d" % (k, v) for k, v in sorted(z.items(), key=lambda kv: -kv[1]))

    def _neue_karte(self, bed, G=None):
        """B-157/B-161: Gefahrenkarte dieser Runde - mit den Gebieten des Spiels, wenn die Wegkarte lesbar ist (B-164: ohne
        feindliche Tore und Tuerme als Durchgang)."""
        geb, links = None, None
        if self.wegkarte is not None:
            try:
                wk = self.wegkarte()
                links = wk.get("link")
                geb = wk["gebiet"] if G is None else self._ohne_feindtore(wk["gebiet"], wk.get("gebaeude"), G)
                self.wegkarte_fehler = None
            except Exception as ex:                      # Spiel nicht lesbar: wie vorher ohne Gebiete, Grund merken
                self.wegkarte_fehler = str(ex)[:120]
        return GF.Karte(bed, feuer=self._orte_f, gebiete=geb, links=links)

    def _abfangen(self, L, nah_kampf, start, ziel, befohlen, befehl, aus):
        """B-162: Schuetzen, deren Reichweite den sichersten Weg start -> ziel trifft UND die zu Fuss erreichbar sind (gleiches
        Gebiet laut Wegkarte des Spiels), bekommen je die kleinste Zahl Nahkaempfer, die sie in ABFANG_TAKTE toetet - die
        naechsten zuerst, zusammen hoechstens jeder ABFANG_ANTEIL-te. Ein Auftrag bleibt, bis der Schuetze tot ist. Ohne
        Wegkarte nichts (dann ist "erreichbar" nicht bekannt). Gibt die Nahkaempfer mit Abfangauftrag zurueck."""
        auftraege = getattr(self, "_abfang", {})
        self._abfang = auftraege
        nah = set(nah_kampf)
        for k in list(auftraege):                       # tot oder ohne Leute -> Auftrag aus, die Leute sind wieder frei
            auftraege[k] = [n for n in auftraege[k] if n in nah]
            if k not in L or L[k].get("leben", 1) <= 0 or not auftraege[k]:
                del auftraege[k]
        if self._karte is None or self._karte.gebiete is None or not nah_kampf:
            return set().union(*auftraege.values()) if auftraege else set()
        weg = GF.sicherer_weg(start, ziel, self._karte) or [ziel]
        # B-224 (Daniel 24.10. 21:41 "Einheiten auf den Mauern bleiben stehen, obwohl Zugang zu den Fernkaempfern besteht";
        # gemessen Lauf 213406: 'ABFANG ZU TEUER' 1.236x/1.447x gegen 52/38 Abfaenge): erreichbar ist ein Schuetze, wenn IRGENDEIN
        # freier Nahkaempfer in seinem Gebiet steht (wer oben auf der Mauer ist, hat das Mauer-Gebiet) - nicht nur vom
        # Startpunkt am Boden aus; und keine Anteil-Grenze mehr - die Mindestzahl je Schuetze begrenzt von selbst
        frei = [n for n in nah_kampf if not any(n in v for v in auftraege.values())]
        gebiete_frei = {self._karte.gebiet_bei((L[n]["x"], L[n]["y"])) for n in frei if n in L} - {0}
        er = {b[4] for b in GF.erreichbare_schuetzen(start, self._karte)}
        import gefecht as GE_a
        for k_e, e_e in L.items():
            if e_e.get("besitzer") not in freunde_von(self.sp) and e_e.get("typ") in GE_a.FERN_REICH                     and self._karte.drin((e_e["x"], e_e["y"])) and int(self._karte.gebiete[e_e["x"], e_e["y"]]) in gebiete_frei:
                er.add("schuetze %d" % k_e)
        rest = len(frei)
        for treffer, art, ort in GF.schuetzen_am_weg(start, weg, self._karte):
            k = int(art.split()[1])
            if art not in er or k in auftraege or k not in L:
                continue
            noetig = GF.mindestzahl(L[k].get("leben", 1), self.ABFANG_TAKTE)
            if noetig > len(frei):
                aus.append("FELDZUG ABFANG ZU TEUER: Schuetze %d bei %s braucht %d, frei %d" % (k, ort, noetig, len(frei)))
                continue
            frei.sort(key=lambda n: schach((L[n]["x"], L[n]["y"]), ort))
            auftraege[k], frei, rest = frei[:noetig], frei[noetig:], rest - noetig
            aus.append("FELDZUG ABFANG: %d Nahkaempfer auf Schuetze %d (Typ %d, Leben %d) bei %s - bestreicht %d Wegfelder, zu "
                       "Fuss erreichbar (Gebiet %d); Mindestzahl bei %d Takten (Schaden je Takt %d UNGEMESSEN)" % (
                           noetig, k, L[k]["typ"], L[k].get("leben", 0), ort, treffer, self._karte.gebiet_bei(start),
                           self.ABFANG_TAKTE, GF.NAHKAMPF_SCHADEN))
        # B-177/B-182 (Daniel 22.10. 17:53/17:55: Bogenschuetzen, die beim Vorbeilaufen sichtbar werden, und Feuerballisten auf
        # dem Weg werden nicht besiegt): nach WIRKUNG wie im Sturm - wer gerade einen von uns angreift (Lagebild zieleinheit) und
        # zu Fuss erreichbar ist (gleiches Gebiet), bekommt die kleinste Zahl Nahkaempfer, eine Feuerballiste mindestens BALLISTE_MIN
        import gefecht
        meine = {n for n, e in L.items() if e.get("besitzer") == self.sp}
        g_start = self._karte.gebiet_bei(start)
        # B-205 (Daniel 22.10. 18:47: "Streitkolben stehen und gehen nicht auf die Feuerballiste"; gemessen: 'ABFANG ZU TEUER ...
        # frei 22 (Anteil-Rest 1)' 22x, NACH WIRKUNG 0x - die Ballista zielte auf Gebaeude, nicht auf Einheiten): eine
        # Feuerballiste bis BALLISTE_R Felder von einem unserer Nahkaempfer ist immer Ziel, und wer uns beschiesst oder eine
        # Ballista ist, zaehlt nicht gegen den Anteil (nur die freien Leute begrenzen)
        nah_orte = [(L[n]["x"], L[n]["y"]) for n in nah_kampf if n in L]
        for k, e in sorted(L.items(), key=lambda ke: schach((ke[1]["x"], ke[1]["y"]), start)):
            ballista_nah = e.get("typ") == BALLISTE and any(schach((e["x"], e["y"]), q) <= self.BALLISTE_R for q in nah_orte)
            if (k in auftraege or e.get("besitzer") in freunde_von(self.sp) or e.get("leben", 1) <= 0
                    or (e.get("typ") not in gefecht.FERN_REICH and e.get("typ") != BALLISTE)
                    or (e.get("zieleinheit") not in meine and not ballista_nah)):
                continue
            p_e = (e["x"], e["y"])
            if not self._karte.drin(p_e) or int(self._karte.gebiete[p_e[0], p_e[1]]) not in (gebiete_frei | {g_start}) - {0}:
                continue                                    # in keinem Gebiet eines freien Nahkaempfers - zu Fuss nicht erreichbar (B-224)
            noetig = GF.mindestzahl(e.get("leben", 1), self.ABFANG_TAKTE)
            if e.get("typ") == BALLISTE:
                noetig = max(noetig, self.BALLISTE_MIN)
            if noetig > len(frei):
                continue
            frei.sort(key=lambda n: schach((L[n]["x"], L[n]["y"]), p_e))
            auftraege[k], frei, rest = frei[:noetig], frei[noetig:], rest - noetig
            aus.append("FELDZUG ABFANG NACH WIRKUNG: %d Nahkaempfer auf %s %d (Typ %d) bei %s - greift Einheit %d an, zu Fuss "
                       "erreichbar" % (noetig, "Feuerballiste" if e.get("typ") == BALLISTE else "Schuetze", k, e["typ"], p_e,
                                       e.get("zieleinheit")))
        for k, ns in auftraege.items():
            neu = [n for n in ns if befohlen.get(n) != ("abfang", k) or L[n].get("zustand") in (0, 1)]
            if neu:
                befehl({"angriff": {"einheiten": neu, "ziel": k}}, 1.0, bis="ANGRIFF")
                for n in neu:
                    befohlen[n] = ("abfang", k)
        return set().union(*auftraege.values()) if auftraege else set()

    def _beste_stelle(self, G, lp, orte, nr_test=None):
        """B-140 (Daniel 21:47 "nicht nur stupide drauf gehen, sondern die beste Position auswaehlen"): (Gefahr, Leben, Abstand,
        Nr) des Torhauses/Turms bis BURG_R vom Lord, auf das die wenigsten feindlichen Schuetzen schiessen koennen (Reichweiten
        wie gefecht.FERN_REICH), dann die wenigsten Leben; None ohne Kandidaten."""
        import gefecht
        spitze_o = min(orte, key=lambda o: schach(o, lp))
        schuetzen_f = [((e["x"], e["y"]), gefecht.FERN_REICH[e["typ"]]) for e in self._lagebild.values()
                       if e["besitzer"] not in freunde_von(self.sp) and e["typ"] in gefecht.FERN_REICH] if self._lagebild else []
        kand = []
        for nr, g in G.items():
            if g["besitzer"] in freunde_von(self.sp) or g["typ"] not in BURG_TEILE or nr in self.verworfen:
                continue
            if self._orte_f and g.get("feuer", 0) > 0:          # B-150: eine brennende Bresche wird nicht gewaehlt
                continue
            ort = (g["x"], g["y"])
            if schach(ort, lp) > self.BURG_R:
                continue
            # B-157 (Daniel 21:11 "maximale Sicherheit, dann minimaler Widerstand"): Widerstand = Gefahr auf dem SICHERSTEN Weg
            # von unserer Spitze bis zur Stelle (Schuetzen-Reichweiten + Todeszone Torhaus); ohne Gefahrenkarte wie bisher die
            # Zahl der Schuetzen an der Stelle
            # Widerstand an der Stelle: so lange steht man dort unter Beschuss - Schuetzen an der Stelle x Leben/100 (UNGEMESSEN)
            bed_ = getattr(self, "_bed", None)
            if bed_ or self.wegkarte is not None:       # B-161: mit Wegkarte auch ohne Bedrohung (alle Schuetzen tot)
                if self._karte is None:
                    self._karte = self._neue_karte(bed_ or [], G)
                weg_ = GF.sicherer_weg(spitze_o, ort, self._karte)
                if weg_ is None and self._karte.gebiete is not None:
                    # B-161 (Franz' Burg 21.10. Takt 74.036: 4 von 9 Stellen liegen hinter Mauern - von aussen kein Feld
                    # daneben im Gebiet unserer Spitze; die alte Wahl nahm eine davon als "sicherste")
                    continue
                weg_ = weg_ or [ort]
                gefahr = GF.weg_gefahr(spitze_o, weg_, self._karte) + GF.gefahr(ort, self._karte) * g.get("leben", 0) // 100
            else:
                gefahr = sum(1 for q, r in schuetzen_f if schach(ort, q) <= r)
            kand.append((gefahr, g.get("leben", 0), schach(ort, spitze_o), nr))
        # B-140 (Daniel 22:11/22:16, Bilder: Truppen standen vor der Mauer und liessen sich abschiessen; Lauf 40: 35 Mann
        # 3.330 Takte vor Torhaus 239, kein Schaden): nur Gebaeude, an die ein Nachbarfeld erreichbar ist - ein Wegtest fuer
        # alle Kandidaten zusammen
        if kand and self.wegtest is not None and nr_test is not None:
            punkte, wem = [], []
            for k in kand:
                for q in self._nachbar_punkte(G, k[3]):
                    punkte.append(q)
                    wem.append(k[3])
            try:
                gut = self.wegtest(nr_test, punkte)
                angreifbar = {w for w, g_ in zip(wem, gut) if g_}
                kand = [k for k in kand if k[3] in angreifbar]
            except Exception:
                pass
        # (B-146: ein Filter "mehr als 10 Schuetzen scheiden aus" stand hier - die Auswahl nimmt ohnehin die Stelle mit den
        # wenigsten Schuetzen, der Filter konnte also nur "gar keine" bewirken; Pruefstand 21.10. 00:37: keine Schwachstelle,
        # das Heer stand 17.000 Takte im STAU. Der Schutz gehoert an den Vorposten, siehe _vorposten.)
        return min(kand) if kand else None

    def _schwachstelle(self, G, lp, orte, aus, anlass):
        """B-139: der schwaechste Teil der Burg am Lord (Torhaus/Turm bis BURG_R Felder vom Lord, nicht verworfen): wenigstes
        Leben, bei Gleichstand der naechste an unserer Spitze. Setzt self.bresche; False, wenn es keinen gibt.
        B-170: gibt es einen Durchbruch-Plan zu diesem Lord, entscheidet er - ein Torhaus nur, wenn es auf dem besten Weg liegt,
        nie ein Turm abseits (22.10.: Turm 327, 2.000 Leben, 25 Felder vom Lord, auf keinem Weg dorthin)."""
        if self.durchbruch is not None and self.dplan is not None and tuple(self.dplan["lord"]) == tuple(lp):
            if self.dplan["art"] in ("tor", "gebaeude") and self.dplan["ziel"] in G and self.dplan["ziel"] not in self.verworfen:
                nr = self.dplan["ziel"]
                self.bresche, self.bresche_leben = nr, None
                self._bresche_pruef = (nr, self.runde)
                aus.append("FELDZUG SCHWACHSTELLE (%s): Gebaeude %d auf dem Durchbruch-Weg zum Lord (Zugang %s)" % (
                    anlass, nr, self.dplan["zug"]))
                return True
            if self.dplan["art"] in ("tor", "gebaeude"):
                self.dplan = None             # das Torhaus ist weg/verworfen - naechste Runde neu planen
            return False                      # Mauer: der Schredder am Zugang arbeitet, kein Turm dazwischen (B-185)
        if self._lord_frei_alt:
            # B-176 (2v2 17:52: Lord 143 zu Fuss erreichbar, Stau -> Turm 412 19 Felder abseits): ist der Lord zu Fuss erreichbar, ist
            # kein Burgteil die Loesung - der Weg zum Lord ist offen
            aus.append("FELDZUG KEINE SCHWACHSTELLE (%s): Lord zu Fuss erreichbar - kein Turm abseits" % anlass)
            return False
        kolben_s = [n for n, e in (self._lagebild or {}).items() if e["besitzer"] == self.sp and e["typ"] in HEER]
        beste = self._beste_stelle(G, lp, orte, nr_test=kolben_s[0] if kolben_s else None)
        if beste is None:
            return False
        gefahr, leben, _, nr = beste
        g = G[nr]
        self.bresche, self.bresche_leben = nr, None
        self._bresche_pruef = (nr, self.runde)      # (die Wahl hat gerade selbst geprueft)
        aus.append("FELDZUG SCHWACHSTELLE (%s): Gebaeude %d (Typ %d, Leben %d, Gefahr auf dem sichersten Weg %d) bei (%d, %d), %d Felder "
                   "vom Lord - alle Nahkaempfer darauf" % (anlass, nr, g["typ"], leben, gefahr, g["x"], g["y"], schach((g["x"], g["y"]), lp)))
        return True

    RINGE = (4, 8, 12, 16, 22, 30)
    # B-139 (Daniel 21:44, Bild: nach dem ersten zerstoerten Turm standen alle vor Franz' Burg, zogen sich zurueck und wurden
    # abgeschossen - der Lord war eingemauert, der Angriffsbefehl auf ihn bewegte niemanden, die naechste Schwachstelle kam
    # erst nach 1.500 Takten Stau): ohne stehende Bresche fragt der Feldzug den Wegfinder, ob ein Feld bis LORD_RINGE am Lord
    # erreichbar ist - ja: alle dorthin, am Lord der Angriff; nein: sofort die naechste Schwachstelle
    LORD_RINGE = (1, 2, 3)
    ZIEL_BIS = 4000           # B-140: Rechengrenze (Takte) fuer die Gefechtsrechnung am Ziel
    LORD_PRUEF_RUNDEN = 20

    def _erreichbar_bei(self, ziel, nr, mitte, ringe, gefahr=None, meiden=()):
        """Der naechste vom Wegfinder des Spiels erreichbare Punkt auf Ringen um ziel (je 8 Richtungen), bei gleichem Ring der
        naechste an mitte; None ohne Wegtest oder ohne Treffer. Mit gefahr (Punkt -> Zahl Feindschuetzen in Reichweite, B-146):
        zuerst Punkte bis TOR_R (dort kommt der Angriffsbefehl), darunter der mit den wenigsten Schuetzen."""
        if self.wegtest is None:
            return None
        punkte = [(ziel[0] + dx * r, ziel[1] + dy * r) for r in ringe
                  for dx, dy in ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1))]
        try:
            gut = self.wegtest(nr, punkte)
        except Exception:
            return None
        treffer = [q for q, g in zip(punkte, gut) if g and q not in meiden]      # B-248: verworfene Vorposten nie wieder
        # B-150 (Pruefstand 21.10.: der Vorposten (128,151) lag 4 Felder neben dem brennenden Gebaeude 298 - dort stand das
        # Heer, als daneben 291 angezuendet wurde): kein Punkt im Feuer, solange es freie gibt
        treffer = [q for q in treffer if not im_feuer(q, self._orte_f)] or treffer
        if gefahr is not None:
            return min(treffer, key=lambda q: (schach(q, ziel) > self.TOR_R, gefahr(q), schach(q, ziel), schach(q, mitte))) if treffer else None
        return min(treffer, key=lambda q: (schach(q, ziel), schach(q, mitte))) if treffer else None

    def _vorposten(self, L, tor, nah_kampf, mitte):
        """B-139 (21:39 gemessen mit dem Wegtest des Spiels: Franz' Turm 596 ist von Sueden bis auf 4 Felder erreichbar, von
        Norden gar nicht; Laufbefehle auf das Turmfeld selbst liessen die Einheiten untaetig): der naechste erreichbare Punkt
        auf Ringen um die Bresche (je 8 Richtungen), bei gleichem Ring der naechste an der Mitte unseres Heeres. Ohne
        Wegtest oder ohne Treffer: None (dann der alte Weg)."""
        if not nah_kampf:
            return None
        # B-146 (Daniel 21.10. 00:34; L171: Vorposten (146,133) vor Turm 241 lag im Schussfeld von 25 Feindschuetzen, die
        # Armee stand dort und wurde abgeschossen): bis TOR_R der Punkt mit den wenigsten Schuetzen in Reichweite
        import gefecht
        schuetzen = [((e["x"], e["y"]), gefecht.FERN_REICH[e["typ"]]) for e in L.values()
                     if e["besitzer"] not in freunde_von(self.sp) and e["typ"] in gefecht.FERN_REICH and e.get("leben", 1) > 0]
        return self._erreichbar_bei(tor, nah_kampf[0], mitte, self.RINGE,
                                    gefahr=lambda q: sum(1 for f, r in schuetzen if schach(q, f) <= r), meiden=self.vp_verworfen)

    def _lords(self, L):
        return {n: e for n, e in L.items() if e["typ"] == LORD and e["besitzer"] not in freunde_von(self.sp) and e["leben"] > 0}

    def _sammelpunkt(self, L, G, lord):
        """Auf der Linie Heim -> Lord von vorn nach hinten der erste Punkt, der SICHER Felder von jedem feindlichen
        Fernkaempfer und GEB_ABSTAND von jedem feindlichen Gebaeude entfernt ist."""
        fern = [(e["x"], e["y"]) for e in L.values() if e["besitzer"] not in freunde_von(self.sp) and e["typ"] in FERN]
        geb = [(g["x"], g["y"]) for g in G.values() if g["besitzer"] not in freunde_von(self.sp)]
        h, z = getattr(self,"_sammel_von",self.heim), (lord["x"], lord["y"])
        d = max(1, schach(h, z))
        if not hasattr(self, "_sammel_von"):
            # B-247: erste Front - daheim sammeln, SAMMEL_HEIM Felder vor dem Bergfried Richtung Feind (nicht im Feuer, nicht
            # im Schussfeld); erst der Angriff fuehrt das Heer geschlossen nach vorn
            for k in range(min(self.SAMMEL_HEIM, d), -1, -2):
                q = (h[0] + (z[0] - h[0]) * k // d, h[1] + (z[1] - h[1]) * k // d)
                if all(schach(q, f) > self.SICHER for f in fern) and not im_feuer(q, self._orte_f or ()):
                    return q
            return h
        for k in range(d, -1, -2):
            q = (h[0] + (z[0] - h[0]) * k // d, h[1] + (z[1] - h[1]) * k // d)
            # B-192 (Daniel 22.10. 18:19: "wenn der Sammelpunkt brennt, sollen sie nicht staendig versuchen, zu diesem zu laufen,
            # sondern in Sicherheit gehen und dort warten, bis das Feuer vorbei ist"): kein Sammelpunkt im Feuer
            if all(schach(q, f) > self.SICHER for f in fern) and all(schach(q, b) > self.GEB_ABSTAND for b in geb)                     and not im_feuer(q, self._orte_f or ()):
                return q
        if hasattr(self,"_sammel_von") and self._karte is not None:
            # Nach einem Sieg kann die aktuelle Front unter Beschuss stehen.
            # Falls die Linie zum neuen Gegner nirgends sicher ist, seitlich
            # ausweichen statt den unsicheren Start zum Sammelpunkt zu erklaeren.
            _, kum = self._karte.suche(h)
            sicher = np.isfinite(kum) & (self._karte.g == 0) & ~self._karte.sperre
            if sicher.any():
                kosten = np.where(sicher,kum,np.inf)
                return tuple(int(v) for v in np.unravel_index(kosten.argmin(),kosten.shape))
        return self.heim

    def _heerwege(self, L):
        """B-150 fuer den Brandtrupp: wo das eigene Heer steht und wohin es befohlen ist - [(von, nach)]: wer steht, je 5x5-Feld
        ein Punkt (von == nach); je befohlenem Punkt die Mitte der Befohlenen -> Punkt; dazu Mitte -> Lord und der Vorposten.
        (Pruefstand 21.10.: die Sklaven-Regel sah nur die Linie zum Lord; Gebaeude 291 lag 30 Felder daneben, aber 4 Felder
        neben dem Vorposten (128,151), zu dem das Heer seit Takt 43.624 befohlen war.)"""
        stehen, ziele = {}, {}
        bef = getattr(self, "_befohlen", {})
        for n, e in L.items():
            if e.get("besitzer") != self.sp or e.get("typ") not in HEER or e.get("leben", 1) <= 0:
                continue
            o = (e["x"], e["y"])
            stehen.setdefault((o[0] // 5, o[1] // 5), []).append(o)
            ziel = bef.get(n, (None, None))[1]
            if isinstance(ziel, tuple) and len(ziel) == 2:
                ziele.setdefault(ziel, []).append(o)
        mitte = lambda os_: (sorted(o[0] for o in os_)[len(os_) // 2], sorted(o[1] for o in os_)[len(os_) // 2])
        wege = [(mitte(os_), mitte(os_)) for os_ in stehen.values()]
        wege += [(mitte(os_), ziel) for ziel, os_ in ziele.items()]
        if self.heerweg:
            wege.append((self.heerweg[0], self.heerweg[1]))
        vp = getattr(self, "vorposten", None)
        if vp and vp[1]:
            wege.append((vp[1], vp[1]))
        return wege

    def _feuer_lenken(self, st, L, G, befehl, aus):
        """B-150 Feuer meiden, jede Runde aus den Feuern, die JETZT brennen (Daniel 19:45: "ob das Feuer bis dahin schon
        geloescht wurde oder das Gebaeude zerstoert oder es aus einem anderen Grund nicht mehr brennt - darauf muss man
        reagieren koennen"): ist ein Feuer aus, egal warum, faellt es aus der Liste und jeder Befehl geht wieder unveraendert
        durch. Gibt den Befehlsweg dieser Runde zurueck:
          - wer im Feuer steht, wird zuerst an den naechsten freien Punkt geholt und bekommt in dieser Runde keinen anderen
            Befehl (Pruefstand 21.10.: 22 Heer-Meldungen IM FEUER am Vorposten, als daneben Gebaeude 291 zu brennen begann -
            wer stand, wurde vorher nie bewegt)
          - Laufbefehle gehen ueber feuerfreier_weg AUSSEN HERUM (Daniel 20:23 "nicht neben dem Feuer warten, jede Sekunde
            zaehlt"); die Wegpunkte nach dem ersten bekommt logik.lua als "danach" und schickt die Truppe ohne Pause weiter;
            nur ohne jeden Weg herum wird abgewogen: ausser Reichweite der Schuetzen warten, sonst durch
          - brennt die Bresche selbst, kommt sofort die naechste Schwachstelle (in schritt)
          - wer gerade laeuft und dessen Laufziel durchs Feuer fuehrt, bekommt den Umweg neu (Augen-Test 19:38)
        Mauer-Befehle (B-147) bleiben - ihr Feld waehlt logik.lua. (Gegenprobe im Pruefstand: FEUER_MEIDEN=nein)"""
        orte_f = feuerorte(G, st.get("bodenfeuer", [])) if os.environ.get("FEUER_MEIDEN", "ja") != "nein" else []
        self._orte_f = orte_f
        self.heerwege = self._heerwege(L)
        # B-157 (Daniel 21.10. 21:11 "du laeufst frontal mit maximalem Beschuss - maximale Sicherheit, dann minimaler Widerstand"):
        # Gefahrenkarte jede Runde neu - jeder Laufbefehl geht ueber den Weg mit der kleinsten Gefahr (gefahr.sicherer_weg)
        import gefecht
        self._bed = GF.bedrohungen(L, G, lambda b: b not in freunde_von(self.sp), gefecht.FERN_REICH)
        # 21.10. (Pruefstand 21:34: Runden bis 4.472 Takte blind, "ruestung" bis 11 s): die Karte einmal je Runde, jede Wegsuche
        # dieser Runde liest daraus (0,02-0,06 s je Ziel statt 0,2-1,2 s am Lagebild Tick 59.105)
        self._karte = self._neue_karte(self._bed, G) if self._bed or self.wegkarte is not None else None
        if not orte_f and not self._bed:
            return befehl
        roh = befehl
        mitte = lambda ns: (sorted(L[n]["x"] for n in ns)[len(ns) // 2], sorted(L[n]["y"] for n in ns)[len(ns) // 2])
        # 1. raus aus dem Feuer - je 5x5-Feld ein Befehl (jeder Befehl wartet bis 1 s auf das Spiel)
        gruppen = {}
        for n, e in L.items():
            if (e.get("besitzer") == self.sp and e.get("typ") in HEER and e.get("leben", 1) > 0
                    and im_feuer((e["x"], e["y"]), orte_f)):
                gruppen.setdefault((e["x"] // 5, e["y"] // 5), []).append(n)
        raus = set()
        for ns in gruppen.values():
            m = mitte(ns)
            w = feuerfrei_punkt(m, orte_f)
            if w is None:
                continue
            roh({"angriff": {"einheiten": sorted(ns), "lauf": [w[0], w[1]]}}, 1.0, bis="ANGRIFF")
            raus |= set(ns)
            aus.append("FELDZUG AUS DEM FEUER: %d Einheiten bei %s -> %s (%d Feuer)" % (len(ns), m, w, len(orte_f)))

        import gefecht
        schuetzen = [((e["x"], e["y"]), gefecht.FERN_REICH[e["typ"]]) for e in L.values()
                     if e["besitzer"] not in freunde_von(self.sp) and e["typ"] in gefecht.FERN_REICH and e.get("leben", 1) > 0]
        gefahr = lambda q: sum(1 for f, r in schuetzen if schach(q, f) <= r)

        def befehl(b, *a, **k):
            an = b.get("angriff", {}) if isinstance(b, dict) else {}
            if not an.get("einheiten"):
                return roh(b, *a, **k)
            ns = [n for n in an["einheiten"] if n not in raus]
            if not ns:
                return []
            an = dict(an, einheiten=ns)
            da = [n for n in ns if n in L]
            if da and "lauf" in an and "danach" not in an:      # B-180: eine fertige Wegkette (Durchbruch-Plan) nicht umleiten
                m, z = mitte(da), tuple(an["lauf"])
                weg = None
                if self._bed and not (orte_f and im_feuer(m, orte_f)):
                    z2 = (feuerfrei_punkt(z, orte_f, nach=m) or z) if orte_f else z
                    weg = GF.sicherer_weg(m, z2, self._karte)
                    if weg and weg != [z]:
                        g_neu, g_alt = GF.weg_gefahr(m, weg, self._karte), GF.weg_gefahr(m, [z], self._karte)
                        am = GF.schuetzen_am_weg(m, weg, self._karte)
                        er = {b[4] for b in GF.erreichbare_schuetzen(m, self._karte)}
                        aus.append("FELDZUG SICHERER WEG: %d Einheiten nach %s ueber %s - Gefahr %d statt %d (gerade); Schuetzen "
                                   "am Weg %d, davon zu Fuss erreichbar %d; %s" % (
                                       len(ns), z, weg[:4], g_neu, g_alt, len(am), sum(1 for a in am if a[1] in er),
                                       "Gebiet %d" % self._karte.gebiet_bei(m) if self._karte.gebiete is not None else
                                       "OHNE Wegkarte (%s)" % (self.wegkarte_fehler or "nicht gesetzt")))
                if weg is None:
                    weg = feuerfreier_weg(m, z, orte_f, gefahr) if orte_f else [z]
                    if weg != [z]:
                        if weg == [m]:
                            aus.append("FELDZUG FEUER WARTEN: %d Einheiten - kein Weg um das Feuer nach %s, bei %s ausser Reichweite "
                                       "der Schuetzen bis es aus ist (%d Feuer)" % (len(ns), z, m, len(orte_f)))
                        else:
                            aus.append("FELDZUG FEUER MEIDEN: %d Einheiten nicht direkt nach %s, sondern aussen herum %s (%d Feuer)" % (
                                len(ns), z, weg[:4], len(orte_f)))
                if weg != [z]:
                    an = dict(an, lauf=[weg[0][0], weg[0][1]])
                    if len(weg) > 1:
                        an["danach"] = [[q[0], q[1]] for q in weg[1:]]    # logik.lua schickt weiter (Wegkette)
            return roh(dict(b, angriff=an), *a, **k)

        # 2. wer gerade laeuft und dessen naechstes Wegstueck (Laufziel des Spiels = naechster Wegknoten) durchs Feuer fuehrt,
        #    bekommt den Weg zu SEINEM befohlenen Punkt neu - je befohlenem Punkt und 8x8-Feld ein Befehl. (Pruefstand 20:32: hier
        #    ging je Einheit ein Befehl zum naechsten Wegknoten des Spiels - 126 Wegketten meist fuer 1 Einheit, und am Knoten
        #    blieben sie bis zur naechsten Runde stehen.) Wer einen Angriffsbefehl hat, wird nicht umgeleitet (raus holt Punkt 1)
        bef = getattr(self, "_befohlen", {})
        ziele = {}
        for n, e in L.items():
            if (n in raus or e.get("besitzer") != self.sp or e.get("typ") not in HEER or e.get("zustand") in (0, 1)
                    or not (e.get("laufx", 0) > 0 and e.get("laufy", 0) > 0)):
                continue
            art, z_ = bef.get(n, (None, None))
            if art not in ("lauf", "vorposten", "zum_lord", "rueckzug") or not (isinstance(z_, (tuple, list)) and len(z_) == 2):
                continue
            if not _frei((e["x"], e["y"]), (e["laufx"], e["laufy"]), orte_f):
                ziele.setdefault((tuple(z_), e["x"] // 8, e["y"] // 8), []).append(n)
        for (z_, _, _), ns in ziele.items():
            befehl({"angriff": {"einheiten": sorted(ns), "lauf": [z_[0], z_[1]]}}, 1.0, bis="ANGRIFF")
        return befehl

    def schritt(self, st, L, G, befehl):
        """Gibt die Meldungen der Runde. befehl(dict, warte, bis=...) schickt einen Modulbefehl."""
        self.runde += 1
        self._lagebild = L
        self._gebaeudebild = G
        aus = []
        befehl = self._feuer_lenken(st, L, G, befehl, aus)     # B-150: Feuer meiden, jede Runde neu
        t = st.get("t", 0)
        lords = self._lords(L)
        kolben = sorted(self.einheiten(L))
        if self.ziel is not None and self.ziel not in lords:
            self.tote_lords.append((self.ziel, t))
            aus.append("FELDZUG: Lord %d tot bei Tick %d - %d Streitkolben ueberlebten, naechstes Ziel" % (self.ziel, t, len(kolben)))
            # B-190 (Daniel 22.10. 18:16: nach dem Fall des Lords blieb das Heer auf dem Bergfried zwischen Feinden und verlor
            # Leben): festgehaltenes Mauerziel loesen, Plan/Schredder weg, alle sofort zum sicheren Punkt auf der Linie vom
            # gefallenen Lord nach Hause - von dort geht es zum naechsten Ziel
            alt_ort = getattr(self, "_ziel_ort", None)
            if self._angesetzt_kachel is not None:
                self._mauerziel_los(befehl)
            self.dplan, self.schredder, self.mauer_kachel = None, False, None
            if lords and kolben:
                # Die neue Front beginnt beim ueberlebenden Heer, nicht zu Hause.
                # Die normale Gefechtsrechnung entscheidet unten sofort ueber Weiterangriff
                # oder ein sicheres Sammelfeld in Richtung des naechsten Gegners.
                self._sammel_von = (sorted(L[n]["x"] for n in kolben)[len(kolben)//2],
                                    sorted(L[n]["y"] for n in kolben)[len(kolben)//2])
                self.weg, self.weg_i, self.weg_ziel = [], 0, None
                self._rechnung = self._rechnung_alle = (-99,False,"")
                self._lord_frei_alt = None
                self.lord_vp, self.vorposten = None, None
                self._befohlen = {}
                aus.append("FELDZUG NACH DEM SIEG: neue Front ab %s - naechster Gegner ohne Heimat-Umweg" % (self._sammel_von,))
            elif alt_ort is not None and kolben:
                sicher_p = self._sammelpunkt(L, G, {"x": alt_ort[0], "y": alt_ort[1]})
                befehl({"angriff": {"einheiten": kolben, "lauf": [sicher_p[0], sicher_p[1]]}}, 1.0, bis="ANGRIFF")
                bef_t = getattr(self, "_befohlen", {})
                self._befohlen = bef_t
                for n in kolben:
                    bef_t[n] = ("lauf", tuple(sicher_p))
                aus.append("FELDZUG NACH DEM SIEG: %d Einheiten aus der Burg zum sicheren Punkt %s" % (len(kolben), tuple(sicher_p)))
            self.ziel, self.phase, self.punkt = None, "sammeln", None
            self._stau, self.staus, self.direkt = (None, 0), 0, False
            self.bresche, self.bresche_leben, self.lord_versuch = None, None, None
        self._nahe_schuetzen(L, kolben, befehl, aus)
        if not lords:
            return aus
        if self.ziel is None:
            self.ziel = min(lords, key=lambda n: (schach(getattr(self,"_sammel_von",self.heim), (lords[n]["x"], lords[n]["y"])), n))
            self.phase = "sammeln"
            aus.append("FELDZUG: Ziel Lord %d (Spieler %d) bei (%d, %d), %d Felder vom Bergfried" % (
                self.ziel, lords[self.ziel]["besitzer"], lords[self.ziel]["x"], lords[self.ziel]["y"],
                schach(self.heim, (lords[self.ziel]["x"], lords[self.ziel]["y"]))))
        lord = lords[self.ziel]
        lp = (lord["x"], lord["y"])
        self._ziel_ort = lp
        if not kolben:
            return aus
        if self.phase == "sammeln":
            if self.punkt is None or self.runde % 20 == 0 or im_feuer(self.punkt, self._orte_f or ()):
                neu = self._sammelpunkt(L, G, lord)
                if neu != self.punkt:
                    self.punkt = neu
                    aus.append("FELDZUG: Sammelpunkt %s (%d Felder vor dem Lord %d)" % (neu, schach(neu, lp), self.ziel))
            p = self.punkt
            da = [n for n in kolben if schach((L[n]["x"], L[n]["y"]), p) <= self.AM_PUNKT]
            # Verteidigen statt stehen: feindliche Einheit nahe am Sammelpunkt -> die, die da sind, greifen sie an
            feind = min(((schach(p, (e["x"], e["y"])), n) for n, e in L.items()
                         if e["besitzer"] not in freunde_von(self.sp) and e["typ"] in TRUPPE and schach(p, (e["x"], e["y"])) <= self.VERTEIDIGEN),
                        default=None)
            if feind and da:
                if self.verteidigt.get(feind[1], -99) < self.runde - self.WIEDERHOLEN:
                    befehl({"angriff": {"einheiten": da, "ziel": feind[1]}}, 1.0, bis="ANGRIFF")
                    self.verteidigt[feind[1]] = self.runde
                    aus.append("FELDZUG: %d Streitkolben greifen Einheit %d (Typ %d) %d Felder vor dem Sammelpunkt an" % (
                        len(da), feind[1], L[feind[1]]["typ"], feind[0]))
            if self.runde % 10 == 0:
                aus.append("FELDZUG sammeln: %d von %d am Sammelpunkt %s, %d Streitkolben leben, Lord %d Leben %d%s" % (
                    len(da), self.N, p, len(kolben), self.ziel, lord["leben"],
                    "" if t >= self.schutz_bis else " (Lord-Schutz bis Tick %d)" % self.schutz_bis))
            # 19.10.: angreifen, sobald N da sind - oder schon frueher, wenn die Gefechtsrechnung gegen den Lord und alles um ihn
            # (Truppen bis LORD_UMKREIS, Schuetzen in Reichweite) einen Sieg mit genug Rest ergibt (gefecht.py, Editor-Duelle)
            lohnt, text = False, ""
            if t >= self.schutz_bis and self.MIN_ANGRIFF <= len(da) < self.N:
                if self.runde - self._rechnung[0] >= self.RECHNEN_ALLE:
                    self._rechnung = (self.runde,) + self._lohnt(L, da, lord)
                lohnt, text = self._rechnung[1], self._rechnung[2]
            # 19.10. (Endspurt, Daniel 16:51 "lass versuchen den Gegner zu rushen"): die Wirtschaft ist verloren - angreifen,
            # sobald die Haelfte des Heeres (mindestens MIN_ANGRIFF) am Sammelpunkt steht, ohne auf die Gefechtsrechnung zu warten
            if self.endspurt and len(da) >= self.MIN_ANGRIFF and 2 * len(da) >= len(kolben):
                lohnt, text = True, "ENDSPURT: %d von %d am Sammelpunkt" % (len(da), len(kolben))
            # B-140 (Daniel 21:56 "die KI soll halt mal bitte schlau angreifen"; Pruefstand T40126: Angriff mit 30 gegen Franz' 86):
            # los, wenn die Gefechtsrechnung mit dem GANZEN Heer (wo es auch steht) gegen den Lord und alles um ihn gewinnt - nicht
            # mehr schon bei N am Sammelpunkt oder irgendwo (B-139). Bis dahin waechst das Heer (B-141: alles Gold ins Heer)
            lohnt_alle, text_alle = False, ""
            if t >= self.schutz_bis and len(kolben) >= self.MIN_ANGRIFF:
                # neu rechnen alle RECHNEN_ALLE Runden - und sofort, wenn sich die Heeresgroesse um 10 % geaendert hat (nicht bei
                # jeder Werbung: die Rechnung mit 160 gegen 60 kostet spuerbar Rundenzeit)
                n_alt = self._rechnung_alle[3] if len(self._rechnung_alle) > 3 else -999
                if self.runde - self._rechnung_alle[0] >= self.RECHNEN_ALLE or abs(len(kolben) - n_alt) * 10 >= max(10, n_alt):
                    lp_k = (lord["x"], lord["y"])
                    beste_k = self._beste_stelle(G, lp_k, [(L[n]["x"], L[n]["y"]) for n in kolben])
                    ort_k = (G[beste_k[3]]["x"], G[beste_k[3]]["y"]) if beste_k else None
                    self._rechnung_alle = (self.runde,) + tuple(self._lohnt(L, kolben, lord, am_ziel=True, ort=ort_k)) + (len(kolben),)
                lohnt_alle, text_alle = self._rechnung_alle[1], self._rechnung_alle[2]
                if lohnt_alle and not text:
                    text = "ganzes Heer: " + text_alle
            if self.runde % 10 == 0 and t >= self.schutz_bis and not (lohnt_alle or lohnt):
                aus.append("FELDZUG WARTET: Gefechtsrechnung mit %d Truppen verliert noch (%s)" % (len(kolben), text_alle[:80]))
            if self.angriff_ab is not None:          # Versuchsreihe: nur die Heeresgroesse entscheidet
                lohnt_alle, lohnt = len(kolben) >= self.angriff_ab, False
                text = "Versuchsreihe: ab %d Truppen" % self.angriff_ab
            if (lohnt_alle or lohnt) and t >= self.schutz_bis:
                self.phase = "angriff"
                self.letzter_befehl = -99
                self._stau, self.staus, self.direkt = (None, 0), 0, False
                self.bresche, self.bresche_leben, self.lord_versuch = None, None, None
                self.weg, self.weg_i, self.weg_ziel = [], 0, None
                aus.append("FELDZUG ANGRIFF: %d Truppen (%d am Sammelpunkt) gemeinsam auf Lord %d (Leben %d) bei Tick %d%s" % (
                    len(kolben), len(da), self.ziel, lord["leben"], t, " - " + text if text else ""))
            else:
                # B-139: der Laufbefehl zum Sammelpunkt erst, wenn feststeht, dass nicht angegriffen wird (vorher bekamen alle im
                # Schritt des Angriffsbeginns noch einen Laufbefehl zum Sammelpunkt, bevor der Torangriff kam)
                befohlen = getattr(self, "_befohlen", {})
                self._befohlen = befohlen
                hin = [n for n in kolben if n not in da and n not in self.verteidiger
                       and (befohlen.get(n) != ("lauf", p) or L[n]["zustand"] in (0, 1))]
                if hin:
                    befehl({"angriff": {"einheiten": hin, "lauf": [p[0], p[1]]}}, 1.0, bis="ANGRIFF")
                    for n in hin:
                        befohlen[n] = ("lauf", p)
        if self.phase == "angriff":
            orte = sorted((L[n]["x"], L[n]["y"]) for n in kolben)
            mitte = (sorted(o[0] for o in orte)[len(orte) // 2], sorted(o[1] for o in orte)[len(orte) // 2])
            # Weg neu, wenn keiner da ist oder der Lord sich weit von seinem Ende entfernt hat
            if not self.weg or self.weg_ziel is None or schach(self.weg_ziel, lp) > 5:
                wp = list(self.wegplaner(L, G, mitte, lp)) if self.wegplaner else [lp]
                if not wp or tuple(wp[-1]) != tuple(lp):
                    wp.append(lp)
                self.weg, self.weg_i, self.weg_ziel = [tuple(p) for p in wp], 0, lp
                aus.append("FELDZUG Weg zum Lord %d: %d Wegpunkte %s" % (self.ziel, len(self.weg), self.weg[:6]))
            spitze = min(schach(o, lp) for o in orte)
            self.heerweg = (mitte, lp, t)        # B-150: fuer den Brandtrupp (nicht auf dem eigenen Weg anzuenden)
            if self._stau[0] is None or spitze < self._stau[0]:
                self._stau = (spitze, t)
            elif t - self._stau[1] >= self.STAU_TICKS and self.dplan is not None and self.dplan.get("art") in ("mauer", "tor", "gebaeude"):
                # B-184/B-185 (2v2 17:56/17:58: "STAU 5", alle wieder raus, aufs Torhaus ohne Zugang): mit Durchbruch-Plan ueberwacht
                # der Schredder den Fortschritt (Ankunft, Wirkung) - kein Wegpunkt-Sprung, kein "alle direkt", keine Schwachstelle
                self._stau = (spitze, t)
            elif t - self._stau[1] >= self.STAU_TICKS:
                self.staus += 1
                if self.bresche is not None and self.bresche in G:
                    # B-138: die gewaehlte Bresche steht noch - nicht umwaehlen ("zaeh" regelt den Wechsel), AUSSER kaum jemand
                    # kommt hin (B-139, 20.10. gegen Franz: 72.000 Takte standen 95 Nahkaempfer 150+ Felder vom Ziel, kein Stau
                    # und kein "zaeh" griff, weil die Torsperre jeden Wechsel verhinderte)
                    tor_s = (G[self.bresche]["x"], G[self.bresche]["y"])
                    davor = sum(1 for n in kolben if L[n]["typ"] not in FERN_REICH and schach((L[n]["x"], L[n]["y"]), tor_s) <= self.TOR_R)
                    if davor < self.TOR_MIN:
                        alt_b = self.bresche
                        self.verworfen.add(alt_b)
                        self.bresche, self.bresche_leben = None, None
                        aus.append("FELDZUG BRESCHE UNERREICHBAR: Gebaeude %d - nach %d Ticks ohne Fortschritt %d Nahkaempfer davor, "
                                   "verworfen" % (alt_b, t - self._stau[1], davor))
                        if not self._schwachstelle(G, lp, orte, aus, "Stau %d" % self.staus):
                            self.lord_versuch = t
                elif self._schwachstelle(G, lp, orte, aus, "Stau %d" % self.staus):
                    self.lord_versuch = None        # B-139: nach gefallener Bresche kein Weg zum Lord -> naechster Teil
                elif self.staus == 1 and self.weg_i < len(self.weg) - 1:
                    self.weg_i += 1
                    aus.append("FELDZUG STAU: Spitze %d Ticks bei %d Feldern vor dem Lord - Wegpunkt uebersprungen, jetzt %d/%d" % (
                        t - self._stau[1], spitze, self.weg_i + 1, len(self.weg)))
                elif not self.direkt:
                    self.direkt = True
                    aus.append("FELDZUG STAU %d: Spitze %d Ticks bei %d Feldern vor dem Lord - alle direkt auf den Lord" % (
                        self.staus, t - self._stau[1], spitze))
                else:
                    aus.append("FELDZUG STAU %d: kein Weg zum Lord und kein feindliches Tor/Turm gefunden" % self.staus)
                self._stau = (spitze, t)
            # B-150 (Daniel 20:23 "warum sollten sie neben dem Feuer warten? ... jede Sekunde zaehlt"): brennt die Bresche
            # selbst, wartet niemand daneben - sofort die naechste Schwachstelle; ist das Feuer aus, darf sie wieder gewaehlt werden
            if self._orte_f and self.bresche is not None and G.get(self.bresche, {}).get("feuer", 0) > 0:
                aus.append("FELDZUG BRESCHE BRENNT: Gebaeude %d - nicht daneben warten, sofort die naechste Schwachstelle" % (
                    self.bresche))
                self.bresche, self.bresche_leben, self.vorposten = None, None, None
                if not self._schwachstelle(G, lp, orte, aus, "Bresche brennt"):
                    self.lord_versuch = t
            if self.bresche is not None and self.bresche not in G:
                aus.append("FELDZUG BRESCHE: Gebaeude %d ist gefallen - auf den Lord" % self.bresche)
                self.bresche, self.bresche_leben, self.lord_versuch, self._stau = None, None, t, (None, t)
            # B-163/B-164 (Daniel 21:59): mit Wegkarte JEDE Runde, auch mit gewaehlter Bresche - steht der Lord in unserem Gebiet,
            # geht er allem vor; sonst der Schredder (Einer-Stapel auf seine Mauer), solange er Wirkung hat (B-165)
            ll = self._lage_lord(L, lp, [n for n in kolben if L[n]["typ"] not in FERN_REICH], lord["besitzer"], mitte)
            if getattr(self, "_plan_grund", None):
                aus.append(self._plan_grund)
                self._plan_grund = None
            if self._dplan_meldung:
                aus.append(self._dplan_meldung)
                self._dplan_meldung = None
            for art_z, ziel_z, zug_z in getattr(self, "_zugang_verworfen", []):
                aus.append("FELDZUG ZUGANG UNERREICHBAR: %s %s - der Wegfinder kommt nicht an den Zugang %s, verworfen vor dem "
                           "Anmarsch" % (art_z, ziel_z, zug_z))
            self._zugang_verworfen = []
            if ll is not None:
                if (ll["frei"] is not None) != self._lord_frei_alt:
                    self._lord_frei_alt = ll["frei"] is not None
                    aus.append("FELDZUG LORD %d %s (Wegkarte: Gebiet am Lord %d, unser Gebiet %d)" % (
                        self.ziel, "zu Fuss erreichbar bei %s" % (ll["frei"],) if ll["frei"] else "hinter Mauern",
                        ll["gebiet_lord"], ll["gebiet"]))
                if ll["frei"] is not None:
                    if self.bresche is not None or self.schredder:
                        aus.append("FELDZUG FREIE FAHRT: Lord %d zu Fuss erreichbar - %s fallen gelassen, alle auf den Lord" % (
                            self.ziel, "Bresche %d" % self.bresche if self.bresche is not None else "Schredder"))
                    self.bresche, self.bresche_leben, self.vorposten, self.schredder = None, None, None, False
                    self.lord_versuch = self.lord_versuch or t
                    if self._angesetzt_kachel is not None:
                        self._mauerziel_los(befehl)
                elif ll.get("tor") is not None:
                    # B-170: das Torhaus liegt auf dem besten Weg zum Lord - es ist die Bresche, kein Schredder
                    if self.bresche != ll["tor"]:
                        aus.append("FELDZUG DURCHBRUCH TOR/GEBAEUDE: Lord %d hinter Hindernissen - Gebaeude %d liegt auf dem besten Weg, alle "
                                   "Nahkaempfer darauf%s" % (self.ziel, ll["tor"], " (statt Bresche %d)" % self.bresche
                                                             if self.bresche is not None else ""))
                        self.bresche, self.bresche_leben, self.vorposten = ll["tor"], None, None
                        if self.dplan and self.dplan.get("art")=="gebaeude" and self.dplan.get("zug"):
                            self.vorposten=(self.bresche,tuple(self.dplan["zug"]))
                        self._bresche_pruef = (ll["tor"], self.runde)
                    if self._angesetzt_kachel is not None:
                        self._mauerziel_los(befehl)
                    self.schredder = False
                elif ll["kachel"] is not None and t >= self.schredder_aus_bis:
                    if not self.schredder or ll["kachel"] != getattr(self, "_kachel_gemeldet", None):
                        self._kachel_gemeldet = ll["kachel"]
                        aus.append("FELDZUG SCHREDDER: Lord %d hinter Mauern - alle Nahkaempfer einzeln (Trupp %d) auf DIE Kachel %s "
                                   "(Hoehe %d, %d Felder vom Lord; Durchbruch-Weg: %d Mauerkacheln, Hoehe zusammen %d)%s" % (
                                       self.ziel, self.MAUER_TRUPP, ll["kachel"], ll["hoehe_kachel"], schach(ll["kachel"], lp),
                                       ll["mauern"], ll.get("weg_hoehe") or 0,
                                       " - Bresche %d fallen gelassen" % self.bresche if self.bresche is not None else ""))
                    self.schredder = True
                    self.bresche, self.bresche_leben, self.vorposten = None, None, None
                else:
                    self.schredder = False
            else:
                self.schredder = False
            if self.bresche is None and self.lord_versuch is None and not self.schredder:
                self._schwachstelle(G, lp, orte, aus, "Angriff")       # B-139: Burg am Lord -> sofort ihr schwaechster Teil
            # 19.10. (1019i: die Spitze stand 2.000 Takte 37 Felder vor dem Lord, die Mitte wanderte von 55 auf 80 Felder
            # zurueck - neu angeworbene Soeldner kamen von zu Hause nach): ueber den Wegpunkt entscheidet nur die Spitzengruppe
            # (hoechstens SPITZE_TIEFE Felder weiter vom Lord als der vorderste)
            vorn = [o for o in orte if schach(o, lp) <= spitze + self.SPITZE_TIEFE] or orte
            mitte_v = (sorted(o[0] for o in vorn)[len(vorn) // 2], sorted(o[1] for o in vorn)[len(vorn) // 2])
            while self.weg_i < len(self.weg) - 1:
                wp_i = self.weg[self.weg_i]
                nah_i = sum(1 for o in vorn if schach(o, wp_i) <= self.WEGPUNKT_HALB)
                # (nicht "die Spitze ist naeher am Lord als der Wegpunkt" - das ueberspringt jeden Umweg, Pruefung 8)
                if schach(mitte_v, wp_i) <= self.WEGPUNKT_NAH or 2 * nah_i >= len(vorn):
                    self.weg_i += 1
                else:
                    break
            # B-137 (20.10. Revanche Tick 104.000: nach "alle direkt" liefen nur die Nahkaempfer los - 77 arab. Bogen warteten
            # 154 Felder vom Lord am Wegpunkt 9/25, den die Spitzengruppe nie mehr erreichte): direkt heisst fuer ALLE auf den Lord
            p = lp if self.direkt else self.weg[self.weg_i] if self.weg_i < len(self.weg) - 1 else lp
            # (B-139: kein Laufziel auf die Bresche selbst - 21:35 gemessen: Laufbefehle auf ein Torhaus-/Turmfeld in der Mauer
            # liessen die Einheiten untaetig stehen; auf dem Weg zum Lord kamen sie bei Rotkaeppchen bis 3-9 Felder heran)
            if self.bresche is not None and self.vorposten and self.vorposten[0] == self.bresche and self.vorposten[1]:
                p = self.vorposten[1]                   # B-139: alle zum erreichbaren Vorposten vor der Bresche
            schluss = spitze <= self.SCHLUSS_R or self.direkt
            nah_kampf = [n for n in kolben if L[n]["typ"] not in FERN_REICH]
            fern = [n for n in kolben if L[n]["typ"] in FERN_REICH]
            # B-146 Rueckzugsregel (Daniel 21.10. 00:34; Grundzahl L170: 107 eigene Einheiten standen in einem Pruefstand-Lauf unter
            # Beschuss herum - am Vorposten im Schussfeld und vor dem Graben nach "Lord eingemauert", L171): stehen mindestens
            # RUECKZUG_MIN Nahkaempfer "STEHT NUR", wird die Angriffsstelle verworfen, sie laufen zum Sammelpunkt (ausser Reichweite
            # der Schuetzen) und die naechste Schwachstelle kommt
            stehen = self._steht_nur(L, nah_kampf, t)
            zug_r = self.dplan.get("zug") if (self.dplan is not None and self.dplan.get("art") in ("mauer", "tor", "gebaeude")) else None
            if len(stehen) >= self.RUECKZUG_MIN and (zug_r is not None or (ll is not None and ll.get("frei"))):
                # B-193/B-181 (Daniel 22.10. 18:19 "Orange ist, obwohl es dann zugaenglich war, einfach umgedreht"; gemessen: RUECKZUG
                # 5/6/19 Mann bei Sp1, Sp2 182 Takte vor "Lord erreichbar"): mit Durchbruch-Plan oder offenem Weg geht, wer untaetig
                # im Beschuss steht, an die Arbeit - zum Zugang bzw. auf den Lord - statt zurueck
                bef_r = getattr(self, "_befohlen", {})
                self._befohlen = bef_r
                if zug_r is not None:
                    self._kette_zum_zug(befehl, sorted(stehen), L, tuple(zug_r))
                    for n in stehen:
                        bef_r[n] = ("zug", tuple(zug_r))
                    ziel_r = "zum Zugang %s" % (tuple(zug_r),)
                else:
                    befehl({"angriff": {"einheiten": sorted(stehen), "lauf": [ll["frei"][0], ll["frei"][1]]}}, 1.0, bis="ANGRIFF")
                    for n in stehen:
                        bef_r[n] = ("zum_lord", tuple(ll["frei"]))
                    ziel_r = "auf den Lord"
                aus.append("FELDZUG STEHT NUR -> ARBEIT: %d Nahkaempfer standen >= %d Takte unter Beschuss ohne Ziel - %s statt "
                           "Rueckzug" % (len(stehen), self.RUECKZUG_TAKTE, ziel_r))
            elif len(stehen) >= self.RUECKZUG_MIN:
                sp_r = self._sammelpunkt(L, G, lord)
                alt_r = self.bresche
                if alt_r is not None:
                    self.verworfen.add(alt_r)
                self.bresche, self.bresche_leben, self.vorposten, self.lord_vp = None, None, None, None
                befehl({"angriff": {"einheiten": sorted(stehen), "lauf": [sp_r[0], sp_r[1]]}}, 1.0, bis="ANGRIFF")
                bef_r = getattr(self, "_befohlen", {})
                self._befohlen = bef_r
                for n in stehen:
                    bef_r[n] = ("rueckzug", sp_r)
                aus.append("FELDZUG RUECKZUG: %d Nahkaempfer standen >= %d Takte unter Beschuss ohne Ziel - Stelle %s verworfen, "
                           "zurueck zum Sammelpunkt %s" % (len(stehen), self.RUECKZUG_TAKTE, alt_r, sp_r))
                if not self.schredder and not (ll and ll["frei"]):
                    self._schwachstelle(G, lp, orte, aus, "Rueckzug")
            # B-140 (Daniel 22:27: "sofort erkennen, wenn jemand einen Burggraben setzt - dann soll darauf nicht gegangen
            # werden, sondern einen anderen Weg"; die KI sieht keine Bilder - ihr Auge ist der Wegfinder des Spiels, der Wasser
            # und Mauern kennt): die gewaehlte Bresche JEDE Runde nachpruefen. Kein Nachbarfeld mehr erreichbar (frischer
            # Graben, neue Mauer) -> verwerfen, sofort die naechste Stelle; ist nur der Vorposten abgeschnitten, wird er neu
            # gesucht. (Daniel 22:30 "was genau ist eine Runde?": ein Durchlauf des Lenkers, gemessen 187-1.069 Takte bei
            # Tempo 300 - "alle 3 Runden" waeren 600-3.200 Takte gewesen, je nach Tempo und Rechnerlast. Der Wegtest kostet
            # 0,03 s, also jede Runde - oefter sieht der Lenker das Spiel nicht)
            if (self.bresche is not None and self.bresche in G and self.wegtest is not None and nah_kampf
                    and self._bresche_pruef != (self.bresche, self.runde)):
                b_alt = self.bresche
                punkte_b = self._nachbar_punkte(G, b_alt)
                vp_alt = self.vorposten[1] if self.vorposten and self.vorposten[0] == b_alt else None
                try:
                    gut_b = self.wegtest(nah_kampf[0], punkte_b + ([vp_alt] if vp_alt else []))
                except Exception:
                    gut_b = None
                self._bresche_pruef = (b_alt, self.runde)
                if gut_b is not None and not any(gut_b[:len(punkte_b)]):
                    self.verworfen.add(b_alt)
                    self.bresche, self.bresche_leben, self.vorposten = None, None, None
                    aus.append("FELDZUG BRESCHE ABGESCHNITTEN: Gebaeude %d - der Wegfinder findet kein Feld bis %d daneben mehr "
                               "(Graben/Mauer), verworfen" % (b_alt, max(self.NACHBAR_RINGE)))
                    if not self._schwachstelle(G, lp, orte, aus, "abgeschnitten"):
                        self.lord_versuch = t
                elif gut_b is not None and vp_alt and not gut_b[-1]:
                    # B-248 (Lauf 144300: 227x dieselbe Meldung, jede Runde derselbe Vorposten neu gewaehlt und wieder verworfen)
                    self.vp_verworfen.add(tuple(vp_alt))
                    self.vorposten = None
                    aus.append("FELDZUG VORPOSTEN ABGESCHNITTEN: %s vor Gebaeude %d nicht mehr erreichbar - neu suchen (%d verworfen)" % (
                        vp_alt, b_alt, len(self.vp_verworfen)))
            lord_ziel = None      # B-139: erreichbarer Punkt am Lord (Wegtest); None = keiner gefunden oder ohne Wegtest
            if ll is not None:
                # B-163: die Wegkarte sagt es jede Runde - kein Wegtest, keine Schwachstelle "Lord eingemauert" (Schredder)
                lord_ziel = ll["frei"]
                self.lord_vp = (lp, lord_ziel, self.runde)
                if lord_ziel is not None:
                    p = lord_ziel
            elif (self.bresche is None or self.bresche not in G) and self.wegtest is not None and nah_kampf:
                # (B-147: waehrend die Mauer aufgehackt wird, jede 3. Runde pruefen, ob der Lord schon erreichbar ist)
                if (self.lord_vp is None or schach(self.lord_vp[0], lp) > 3
                        or self.runde - self.lord_vp[2] >= (3 if self.mauer_seit is not None else self.LORD_PRUEF_RUNDEN)):
                    self.lord_vp = (lp, self._erreichbar_bei(lp, nah_kampf[0], mitte, self.LORD_RINGE), self.runde)
                    aus.append("FELDZUG LORD %d %s" % (self.ziel, "erreichbar bei %s" % (self.lord_vp[1],) if self.lord_vp[1]
                                                         else "eingemauert (kein Feld bis %d erreichbar)" % max(self.LORD_RINGE)))
                lord_ziel = self.lord_vp[1]
                if lord_ziel is None and self._schwachstelle(G, lp, orte, aus, "Lord eingemauert"):
                    self.lord_versuch, self.lord_vp = None, None
                if lord_ziel is not None:
                    p = lord_ziel                       # auch die Schuetzen dorthin
            # Schuetzen: naechster Feind in Reichweite (zuerst Schuetzen) - sonst mit dem Haufen
            feinde_f = [(k, e) for k, e in L.items() if e["besitzer"] not in freunde_von(self.sp) and e["typ"] in TRUPPE]
            schiessen = {}
            for n in fern:
                o = (L[n]["x"], L[n]["y"])
                kand = [(e["typ"] not in FERN, schach(o, (e["x"], e["y"])), k) for k, e in feinde_f
                        if schach(o, (e["x"], e["y"])) <= self.SCHUETZEN_ZIEL_R]
                if kand:
                    schiessen[n] = min(kand)[2]
            # Nahkaempfer: am Lord oder im Schluss -> Angriffsbefehl auf den Lord; sonst zum Wegpunkt
            am_lord = [n for n in nah_kampf if schluss or schach((L[n]["x"], L[n]["y"]), lp) <= self.ANGRIFF_NAH]
            befohlen = getattr(self, "_befohlen", {})
            self._befohlen = befohlen
            # B-162: erreichbare Schuetzen am Weg der Spitze zum Ziel dieser Runde (Vorposten/Bresche, sonst Wegpunkt/Lord) -
            # die kleinste noetige Zahl faengt sie ab, alle anderen machen weiter wie geplant
            ziel_w = self.vorposten[1] if (self.bresche is not None and self.vorposten and self.vorposten[0] == self.bresche
                                           and self.vorposten[1]) else p
            abfang = self._abfangen(L, nah_kampf, mitte_v, ziel_w, befohlen, befehl, aus)
            if abfang:
                nah_kampf = [n for n in nah_kampf if n not in abfang]
                am_lord = [n for n in am_lord if n not in abfang]
            bresche = self.bresche
            belegt = set(abfang)  # B-138: Nahkaempfer mit Torauftrag - kein Laufbefehl zum Lord darueber (der hob bis 20.10.
            #                       jeden Torangriff in derselben Runde wieder auf: Torhaus 264 blieb 6 Staus bei 1.500)
            if bresche is not None and bresche in G:
                tor = (G[bresche]["x"], G[bresche]["y"])
                am_tor = [n for n in nah_kampf if schach((L[n]["x"], L[n]["y"]), tor) <= self.TOR_R]
                if self.dplan and self.dplan.get("art")=="gebaeude" and self.dplan.get("zug"):
                    zug_b=tuple(self.dplan["zug"])
                    self.vorposten=(bresche,zug_b)
                    p=zug_b
                    am_tor=[n for n in nah_kampf if schach((L[n]["x"],L[n]["y"]),zug_b)<=1
                            or (L[n].get("zielgebaeude")==bresche and L[n].get("zustand") in (106,107))]
                leben_b = G[bresche].get("leben", -1)
                if (self.bresche_leben is None or self.bresche_leben[2] != bresche or leben_b < self.bresche_leben[0]
                        or len(am_tor) < self.TOR_MIN):
                    self.bresche_leben = (leben_b, t, bresche)
                # B-165 (Siegpartie 21:57: Torhaus 240 1.125 Takte bei 1.500 Leben mit 52 Mann "davor"): Wirkung messen statt
                # 1.000 Takte warten - stehen TOR_MIN bis WIRKUNG_NAH daneben und das Leben sinkt WIRKUNG_TAKTE lang nicht, weg
                nah_b = [n for n in nah_kampf if schach((L[n]["x"], L[n]["y"]), tor) <= self.WIRKUNG_NAH]
                # B-256 (Partie 230627: Torhaus 268 nach 544 Takten "keine Wirkung", alle 8 Mann daneben liefen noch - 101): es
                # zaehlt, wer zuschlaegt (106/107); wer nur daneben steht, bekommt den Befehl neu, bis DRAN_TAKTE um sind
                # (B-258 korrigiert, Partie 003034/001937: Turm 213 und 198, Typ 75, fielen bzw. sanken auf 410 Leben - KEINER hatte
                # sie als zielgebaeude, der Schaden kam aus Zustand 107; erster Schaden 740-940 Takte nach der Wahl)
                hack_b = [n for n in nah_b if L[n].get("zustand") in (106, 107)]
                ohne_b = self._wirkung(("bresche", bresche), leben_b, len(hack_b), t, frist=self.BRESCHE_WIRKUNG)
                if ohne_b is None:
                    ohne_b = self._nicht_dran(("bresche", bresche), len(nah_b), len(hack_b), t, leben_b, frist=self.BRESCHE_WIRKUNG)
                if ohne_b is not None:
                    aus.append("FELDZUG KEINE WIRKUNG: Gebaeude %d (Typ %d) %d Takte bei %d Leben, %d Mann bis %d Felder daneben "
                               "(Zustaende %s) - verworfen, naechste Stelle" % (bresche, G[bresche]["typ"], ohne_b, leben_b,
                                                                              len(nah_b), self.WIRKUNG_NAH, self._zustaende(L, nah_b)))
                if ohne_b is not None or t - self.bresche_leben[1] >= self.BRESCHE_ZAEH:
                    if ohne_b is None:
                        aus.append("FELDZUG BRESCHE ZAEH: Gebaeude %d (Typ %d) seit %d Ticks bei %d Leben, %d davor - verworfen, "
                                   "naechste Schwachstelle" % (bresche, G[bresche]["typ"], t - self.bresche_leben[1], leben_b,
                                                               len(am_tor)))
                    self.verworfen.add(bresche)
                    self.bresche, self.bresche_leben, self._stau = None, None, (None, t)
                else:
                    # B-134/B-139: alle Nahkaempfer auf das Tor/den Turm, ohne Sammeln davor. 20.10. gegen Franz gemessen: der
                    # Gebaeude-Angriffsbefehl bewegt weit entfernte Truppen NICHT (95 standen 72.000 Takte zu Hause), ein
                    # Laufbefehl auf das Torfeld auch nicht (in der Mauer, unerreichbar). Darum: wer weiter als TOR_R weg ist,
                    # laeuft mit allen anderen den Weg zum Lord (unten "unterwegs"); vor dem Tor kommt der Angriffsbefehl
                    belegt = set(am_tor)
                    if self.vorposten is None or self.vorposten[0] != bresche:
                        vp = self._vorposten(L, tor, nah_kampf, mitte)
                        self.vorposten = (bresche, vp)
                        import gefecht
                        n_sch = (sum(1 for e in L.values() if e["besitzer"] not in freunde_von(self.sp) and e["typ"] in gefecht.FERN_REICH
                                     and schach(vp, (e["x"], e["y"])) <= gefecht.FERN_REICH[e["typ"]]) if vp else 0)
                        aus.append("FELDZUG VORPOSTEN vor Gebaeude %d: %s" % (
                            bresche, "%s, %d Felder davor (Wegtest des Spiels), %d Feindschuetzen in Reichweite" % (vp, schach(vp, tor), n_sch)
                            if vp else "keiner gefunden - Weg zum Lord"))
                    vp = self.vorposten[1]
                    if vp is not None:
                        # B-139: alle Nahkaempfer, die noch nicht am Tor sind, laufen zum Vorposten (einmal; erneut nur, wer
                        # untaetig und nicht dort ist)
                        hin_v = [n for n in nah_kampf if n not in belegt
                                 and (befohlen.get(n) != ("vorposten", vp)
                                      or (L[n]["zustand"] in (0, 1) and schach((L[n]["x"], L[n]["y"]), vp) > self.AM_PUNKT))]
                        if hin_v:
                            befehl({"angriff": {"einheiten": hin_v, "lauf": [vp[0], vp[1]]}}, 1.0, bis="ANGRIFF")
                            for n in hin_v:
                                befohlen[n] = ("vorposten", vp)
                        belegt |= set(nah_kampf)
                    # (B-140: Untaetige am Tor jede Runde neu - mit der WIEDERHOLEN-Sperre bekamen in 3.330 Takten nur 22 von 35
                    # ueberhaupt einen Torbefehl)
                    neu_b = [n for n in am_tor if befohlen.get(n) != ("bresche", bresche) or L[n]["zustand"] in (0, 1)]
                    if neu_b:
                        # B-158 (Daniel 21:26 "alle in ein Feld stacken und einzeln auf die Mauer schicken"; Sandkasten 21:33:
                        # Torhaus 2.000 Leben - als Gruppe 559 Takte, in Fuenfern 280, einzeln 281): Trueppchen zu TRUPP
                        befehl({"angriff": {"einheiten": neu_b, "gebaeude": bresche, "trupp": self.TRUPP}}, 1.0, bis="ANGRIFF")
                        for n in neu_b:
                            befohlen[n] = ("bresche", bresche)
                    am_lord = []
            if lord_ziel is not None and (self.bresche is None or self.bresche not in G):
                # Ein gemeinsames Ziel statt Ankunft im Zehn-Felder-Kreis: im Nahbereich
                # erst einzeln direkt zum Lord-Feld, nach Ankunft einzeln zuschlagen.
                am_lord=[n for n in nah_kampf if schach((L[n]['x'],L[n]['y']),lp)<=1]
                stapeln=[n for n in nah_kampf if 1<schach((L[n]['x'],L[n]['y']),lp)<=12]
                hin_l=[n for n in nah_kampf if n not in am_lord and n not in stapeln
                       and (befohlen.get(n)!=('zum_lord',lord_ziel) or L[n]['zustand'] in (0,1))]
                if hin_l:
                    befehl({'angriff':{'einheiten':hin_l,'lauf':list(lord_ziel),'trupp':1}},1.0,bis='ANGRIFF')
                    for n in hin_l:befohlen[n]=('zum_lord',lord_ziel)
                neu_stapel=[n for n in stapeln if befohlen.get(n)!=('lord_stapel',tuple(lp)) or L[n]['zustand'] in (0,1)]
                if neu_stapel:
                    befehl({'angriff':{'einheiten':neu_stapel,'lauf':list(lp),'trupp':1}},1.0,bis='ANGRIFF')
                    for n in neu_stapel:befohlen[n]=('lord_stapel',tuple(lp))
                    aus.append('FELDZUG EINZELSTAPEL: %d Nahkaempfer einzeln auf denselben Lord-Punkt %s'%(len(neu_stapel),lp))
                belegt|=set(nah_kampf)-set(am_lord)
            # B-147 (Daniel 21.10. 00:47 "ja, Mauer einreissen bauen und wieder messen"; L172: nach "Lord eingemauert" lief das
            # Heer immer wieder auf den unerreichbaren Lord, stand unter Beschuss und zog sich zurueck): ist der Lord eingemauert
            # und keine Bresche (Turm/Torhaus) mehr da, hacken alle Nahkaempfer, die es koennen, die naechste erreichbare Mauer
            # am Lord auf (logik.lua waehlt die Kachel, Spielbefehl 36 Art 23); jede 3. Runde wird geprueft, ob der Lord jetzt
            # erreichbar ist - dann geht es wie gehabt auf ihn
            if (lord_ziel is None and (self.schredder or self.lord_vp is not None) and (self.bresche is None or self.bresche not in G)
                    and self.ziel in L):
                wand = [n for n in nah_kampf if L[n]["typ"] in MAUER_TYPEN]
                kq = ll["kachel"] if self.schredder and ll is not None else None
                if wand and kq is not None:
                    # B-165: Wirkung des Schredders = die Hoehe DER Kachel sinkt (Hoehe = Leben der Mauerkachel, VillageStudio
                    # Wissensstand 5d belegt). Ohne Wirkung: Kachel verwerfen, die naechste - Torhaus/Turm erst, wenn keine mehr da
                    # ist (Daniel 22:15: das Torhaus "war logischerweise zu, als die Einheiten da waren")
                    nah_w = [n for n in wand if schach((L[n]["x"], L[n]["y"]), kq) <= 3]
                    # B-164 (Pruefstand 22:22: 20.000 Takte "0 Mann bis 3 daneben" - der Waechter zaehlte Nicht-Ankommen nicht): kommt
                    # ANKUNFT_TAKTE lang niemand an die Kachel, ist sie fuer uns nicht erreichbar - verwerfen
                    # B-180 (2v2 17:54: 47/54/81 Mann mit Mauerauftrag, nach 1.500 Takten niemand bis 3 daneben - viele waren
                    # noch unterwegs): verworfen wird erst, wenn ANKUNFT_TAKTE lang niemand NAEHER kommt
                    best_w = self._rest_weg(L, wand, tuple(ll.get("zug") or kq))
                    if (nah_w or self._kachel_an is None or self._kachel_an[0] != kq
                            or best_w < (self._kachel_an[2] if len(self._kachel_an) > 2 else 999)):
                        self._kachel_an = (kq, t, best_w)
                    elif t - self._kachel_an[1] >= self.ANKUNFT_TAKTE:
                        self.mauer_verworfen.add(kq)
                        self.mauer_kachel, self._kachel_an = None, None
                        aus.append("FELDZUG KOMMT NICHT AN: Mauerkachel %s - %d Takte niemand bis 3 daneben (%d Mann mit Mauerauftrag) - "
                                   "verworfen, neuer Durchbruch-Weg" % (kq, self.ANKUNFT_TAKTE, len(wand)))
                        wand = []
                    if wand and self.runde % 2 == 0:     # Messreihe Hackrate je Kachel (fuer den Durchbruch-Planer)
                        aus.append("FELDZUG SCHREDDER STAND Tick %d: Kachel %s Hoehe %d, %d Mann bis 3 daneben (Zustaende %s), "
                                   "Mauerhoehe bis %d um den Lord %d" % (t, kq, ll["hoehe_kachel"], len(nah_w),
                                                                       self._zustaende(L, nah_w), self.MAUER_R, ll["hoehe"]))
                    # B-256 (Partie 230627: (188,88) nach 343 und (187,88) nach 390 Takten "keine Wirkung" mit 16/21 Mann daneben -
                    # 13/16 davon liefen noch (101), keiner hackte (107); 10 Minuten spaeter hackten an derselben Mauer 51 Mann, die
                    # Hoehe sank je Kachel 90 -> 60): ohne Wirkung ist eine Kachel nur, wenn TOR_MIN HACKEN und die Hoehe steht
                    hack_w = [n for n in nah_w if L[n].get("zustand") == 107]
                    ohne_w = self._wirkung(("kachel", kq), ll["hoehe_kachel"], len(hack_w), t) if wand else None
                    dran_w = self._nicht_dran(("kachel", kq), len(nah_w), len(hack_w), t, ll["hoehe_kachel"]) if wand and ohne_w is None else None
                    if dran_w is not None:
                        aus.append("FELDZUG KOMMT NICHT DRAN: Mauerkachel %s - %d Takte %d Mann bis 3 daneben, keiner hackt (Zustaende %s) "
                                   "- verworfen" % (kq, dran_w, len(nah_w), self._zustaende(L, nah_w)))
                        self.mauer_verworfen.add(kq)
                        self.mauer_kachel = None
                        wand = []
                    if ohne_w is not None:
                        self.mauer_verworfen.add(kq)
                        self.mauer_kachel = None
                        rest = ll["mauern"] - 1
                        aus.append("FELDZUG KEINE WIRKUNG: Mauerkachel %s %d Takte bei Hoehe %d, %d Mann bis 3 daneben (Zustaende %s) - "
                                   "verworfen, %s" % (kq, ohne_w, ll["hoehe_kachel"], len(nah_w), self._zustaende(L, nah_w),
                                                      "naechste Kachel (%d uebrig)" % rest if rest > 0 else
                                                      "keine Kachel mehr - %d Takte Bresche" % self.SCHREDDER_PAUSE))
                        if rest <= 0:
                            self.schredder, self.schredder_aus_bis = False, t + self.SCHREDDER_PAUSE
                            self.mauer_verworfen.clear()
                            self._schwachstelle(G, lp, orte, aus, "Schredder ohne Wirkung")
                        wand = []
                if wand:
                    if self.mauer_seit is None:
                        self.mauer_seit = t
                        aus.append("FELDZUG MAUER: Lord %d eingemauert%s - %d Nahkaempfer hacken die Mauer bis %d Felder um den Lord "
                                   "auf, je %d" % (self.ziel, " (Schredder)" if self.schredder else ", kein Turm erreichbar", len(wand),
                                                   self.MAUER_R, self.MAUER_TRUPP))
                    ziel_w = kq if kq is not None else lp
                    zug_w = ll.get("zug") if ll is not None else None
                    neu_w = [n for n in wand if befohlen.get(n) != ("mauer", ziel_w) or L[n]["zustand"] in (0, 1)]
                    if kq is not None and zug_w is not None and self.feldnr is not None:
                        self._mauer_am_zug(L, wand, kq, tuple(zug_w), lp, befohlen, befehl, aus, t)
                    elif neu_w:
                        # B-164: mit gewaehlter Kachel bekommt logik.lua sie mit (5./6. Wert) - alle Einer-Befehle auf DIESE
                        befehl({"angriff": {"einheiten": neu_w, "mauer": [lp[0], lp[1], L[self.ziel]["besitzer"], self.MAUER_R]
                                            + ([kq[0], kq[1]] if kq is not None else []), "trupp": self.MAUER_TRUPP}},
                               1.0, bis="ANGRIFF")
                        for n in neu_w:
                            befohlen[n] = ("mauer", ziel_w)
                    belegt |= set(wand)
                    am_lord = [n for n in am_lord if n not in wand]
            elif self.mauer_seit is not None:
                aus.append("FELDZUG MAUER beendet nach %d Ticks: Lord %s" % (
                    t - self.mauer_seit, "erreichbar bei %s" % (lord_ziel,) if lord_ziel else "nicht mehr eingemauert/anderes Ziel"))
                self.mauer_seit = None
            neu_lord = [n for n in am_lord if befohlen.get(n) != ("lord", self.ziel) or L[n]["zustand"] in (0, 1)]
            if neu_lord and self.runde - self.letzter_befehl >= self.WIEDERHOLEN:
                befehl({"angriff": {"einheiten": neu_lord, "ziel": self.ziel, "trupp": self.TRUPP}}, 1.0, bis="ANGRIFF")   # B-153/B-158
                self.letzter_befehl = self.runde
                for n in neu_lord:
                    befohlen[n] = ("lord", self.ziel)
            ziele_s = {}
            for n, k in schiessen.items():
                if befohlen.get(n) != ("schuss", k) or L[n]["zustand"] in (0, 1):
                    ziele_s.setdefault(k, []).append(n)
            for k, ns in ziele_s.items():
                befehl({"angriff": {"einheiten": ns, "ziel": k}}, 1.0, bis="ANGRIFF")
                for n in ns:
                    befohlen[n] = ("schuss", k)
            # 19.10. (1019h: Laufbefehle jede Runde neu - das Spiel meldet als Laufziel seinen naechsten Wegknoten, nicht
            # unseren Punkt): nur, wer noch keinen Befehl zu p hat oder steht
            # B-256 (Partie 230627: 6-mal liefen 65-116 Mann zum Wegpunkt 1 (194,298) neben der eigenen Burg zurueck - jedes Mal in
            # der Runde, in der eine Kachel/Bresche verworfen wurde, fiel das Heer auf den alten Marschweg zurueck): niemand wird
            # zu einem Wegpunkt geschickt, der weiter vom Lord liegt als er selbst - er behaelt seinen Befehl bis zum neuen Plan
            unterwegs = [n for n in self._nicht_zurueck(L, kolben, p, lp) if n not in am_lord and n not in schiessen
                         and n not in belegt and (befohlen.get(n) != ("lauf", p) or L[n]["zustand"] in (0, 1))]
            if unterwegs:
                befehl({"angriff": {"einheiten": unterwegs, "lauf": [p[0], p[1]]}}, 1.0, bis="ANGRIFF")
                for n in unterwegs:
                    befohlen[n] = ("lauf", p)
            if self.runde % 5 == 0:
                abst = sorted(schach(o, lp) for o in orte)
                aus.append("FELDZUG Stand Tick %d: %d Streitkolben, Abstand zum Lord naechster %d / Mitte %d, Wegpunkt %d/%d, "
                           "am Lord %d, Lord %d Leben %d" % (t, len(kolben), abst[0], abst[len(abst) // 2], self.weg_i + 1,
                                                            len(self.weg), len(am_lord), self.ziel, lord["leben"]))
        return aus

    def einheiten(self, L):
        """19.10.: das Heer des Feldzugs - alle eigenen Truppen der Arten HEER ausser der Heimwache; der Waechter laesst sie in
        Ruhe (1018y: sein "Stapeln" holte sie heim), ausser als Reserve beim Sammeln."""
        return {n for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] in HEER and n not in self.heimwache}

    def _lohnt(self, L, da, lord, am_ziel=False, ort=None):
        """19.10.: (lohnt, Text) - unsere am Sammelpunkt gegen den Lord, feindliche Truppen bis LORD_UMKREIS Felder und
        Schuetzen, deren Reichweite den Lord erreicht (alle stehen, wir laufen hin)."""
        import gefecht
        lp = (lord["x"], lord["y"])
        # B-140 (Daniel 22:07: "schlau angestellt werden vielleicht nur 20-30 % der gegnerischen Einheiten ueberhaupt genutzt
        # um zu verteidigen"): mit ort wird an der Angriffsstelle gerechnet - es kaempfen nur Feinde bis LORD_UMKREIS um die
        # Stelle und Schuetzen, deren Reichweite sie trifft (der Lord nur, wenn er dort steht); unser Heer steht an der Stelle
        mitte_k = tuple(ort) if ort else lp
        # (B-140: am Ziel kaempfen die Verteidiger mit - als "stehend" schlugen 30 unserer Schwertkaempfer 80 gleiche nacheinander)
        sie = [dict(typ=e["typ"], leben=e["leben"], x=e["x"], y=e["y"], steht=not am_ziel) for e in L.values()
               if e["besitzer"] not in freunde_von(self.sp) and e["typ"] in TRUPPE and (
                   schach((e["x"], e["y"]), mitte_k) <= self.LORD_UMKREIS
                   or (e["typ"] in gefecht.FERN_REICH and schach((e["x"], e["y"]), mitte_k) <= gefecht.FERN_REICH[e["typ"]]))]
        # B-140 (Pruefstand 22:00: "165 eigene gegen 49: offen nach 1500 Takten" - der Anmarsch von 160+ Feldern frass die
        # ganze Rechenzeit, also kein Angriff): am_ziel=True rechnet den Kampf selbst, als stuende das Heer schon am Lord
        wir = [dict(typ=L[n]["typ"], leben=L[n]["leben"], x=mitte_k[0] if am_ziel else L[n]["x"],
                    y=mitte_k[1] if am_ziel else L[n]["y"]) for n in da]
        # B-207 (Daniel 22.10. 18:49: "der Sicherheitsabstand ist viel zu gross, sie haetten viel frueher rausgehen koennen";
        # gemessen 2v2 184103: Sp1 rechnete 13 gegen 20 und wartete, Sp2 27 gegen 22 - zusammen 40 gegen 22): am Ziel kaempfen
        # die Truppen des Verbuendeten mit, die bis PARTNER_R um die Angriffsstelle stehen oder dorthin laufen - beide Lenker
        # rechnen dieselbe Regel und brechen so gemeinsam los
        partner = []
        if am_ziel:
            for e in L.values():
                # B-226: auch die Assassinen des Verbuendeten (Typ 73) - der Lordtrupp rechnet umgekehrt unser Heer mit
                if (e.get("besitzer") in (0, self.sp) or e.get("besitzer") not in freunde_von(self.sp)
                        or (e.get("typ") not in HEER and e.get("typ") != 73) or e.get("leben", 0) <= 0):
                    continue
                lauf = (e.get("laufx", 0), e.get("laufy", 0))
                if schach((e["x"], e["y"]), mitte_k) <= self.PARTNER_R or (lauf[0] > 0 and schach(lauf, mitte_k) <= self.PARTNER_R):
                    partner.append(dict(typ=e["typ"], leben=e["leben"], x=mitte_k[0], y=mitte_k[1]))
            wir = wir + partner
        if not sie and wir:
            return True, "keine Verteidiger an der Angriffsstelle (%d eigene)" % len(wir)   # B-140: dann lohnt es erst recht
        try:
            # B-140 (Pruefstand 22:04: 115 gegen 84 "offen nach 1500 Takten", mit 167 Sieg nach 1.460): am Ziel bis ZIEL_BIS rechnen
            if am_ziel:
                # B-207 (Daniel 18:58 "gegen so wenige wie moeglich kaempfen - du musst ja nur den Lord killen"): am Ziel zaehlt
                # nur der Wettlauf - alle schlagen auf den Lord, gegen uns kaempfen die Verteidiger bis LORD_UMKREIS um IHN und die
                # Schuetzen, die ihn erreichen; nicht die ganze Burg
                sie_l = [dict(typ=e["typ"], leben=e["leben"], x=e["x"], y=e["y"], steht=False) for e in L.values()
                         if e["besitzer"] not in freunde_von(self.sp) and e["typ"] in TRUPPE and e["typ"] != gefecht.LORD and (
                             schach((e["x"], e["y"]), lp) <= self.LORD_UMKREIS
                             or (e["typ"] in gefecht.FERN_REICH and schach((e["x"], e["y"]), lp) <= gefecht.FERN_REICH[e["typ"]]))]
                sie_l.insert(0, dict(typ=gefecht.LORD, leben=lord.get("leben", gefecht.LORD_LEBEN), x=lp[0], y=lp[1], steht=True))
                # unsere stehen an der Angriffsstelle (mitte_k: Tor/Bresche) und laufen von dort zum Lord - der Weg durch die
                # Verteidiger zaehlt mit (Streitkolben am Lord gemessen 70 je Takt, Sandkasten 22.10., lord_nahkampf.jsonl)
                ok_, text_ = gefecht.lord_rennen(wir, sie_l, 0, bis=self.ZIEL_BIS)
            else:
                ok_, text_ = gefecht.bewerte(wir, sie, bis=gefecht.BIS)
            return ok_, ("mit %d Truppen des Verbuendeten: " % len(partner) if partner else "") + text_
        except Exception as ex:
            return False, "Rechnung fehlgeschlagen (%s)" % ex


# B-259 (Partie 234348: r_feldzug 164 s in 320 Runden; ein Test auf kuenstlicher 400x400-Karte zeigte, dass die Wegsuche des
# Durchbruch-Planers selbst nur ~0,06 s braucht - die Zeit steckt woanders): Zeit je Teilschritt messen, alle ZEIT_RUNDEN
# Runden als "FELDZUG ZEITEN" ausgeben (Werte schliessen die Unteraufrufe ein)
import time as _time
ZEIT_RUNDEN = 20
_GEMESSEN = ("_neue_karte", "_lage_lord", "_durchbruch_neu", "_schwachstelle", "_abfangen", "_mauer_am_zug", "_kette_zum_zug",
             "_steht_nur", "_erreichbar_bei", "_nahe_schuetzen")


def _gemessen(f, name):
    def w(self, *a, **k):
        t0 = _time.perf_counter()
        try:
            return f(self, *a, **k)
        finally:
            z = self.__dict__.setdefault("_zeiten", {})
            z[name] = z.get(name, 0.0) + _time.perf_counter() - t0
    w.__name__ = f.__name__
    return w


def _schritt_gemessen(f):
    def w(self, *a, **k):
        t0 = _time.perf_counter()
        aus = f(self, *a, **k)
        z = self.__dict__.setdefault("_zeiten", {})
        z["schritt"] = z.get("schritt", 0.0) + _time.perf_counter() - t0
        z.update(_GF_ZEIT)
        if self.runde % ZEIT_RUNDEN == 0 and z.get("schritt", 0) > 0 and isinstance(aus, list):
            aus.append("FELDZUG ZEITEN bis Runde %d (s, inkl. Unteraufrufe): %s" % (
                self.runde, ", ".join("%s %.1f%s" % (k_, v_, " (%dx)" % _GF_ZAHL[k_] if k_ in _GF_ZAHL else "")
                                      for k_, v_ in sorted(z.items(), key=lambda kv: -kv[1]) if v_ >= 0.05)))
        return aus
    w.__name__ = f.__name__
    return w


for _n in _GEMESSEN:
    if hasattr(Feldzug, _n):
        setattr(Feldzug, _n, _gemessen(getattr(Feldzug, _n), _n))
Feldzug.schritt = _schritt_gemessen(Feldzug.schritt)


# B-259: die Gefahrenkarten-Aufrufe einzeln messen (in _abfangen 4,5 s in 20 Runden, Partie 000151)
def _gf_gemessen(f, name):
    def w(*a, **k):
        t0 = _time.perf_counter()
        try:
            return f(*a, **k)
        finally:
            _GF_ZEIT[name] = _GF_ZEIT.get(name, 0.0) + _time.perf_counter() - t0
            _GF_ZAHL[name] = _GF_ZAHL.get(name, 0) + 1
    return w


_GF_ZAHL = {}


def _suche_gemessen(f):
    """B-259: echte Suchen (nicht aus dem Rundenspeicher) der Gefahrenkarte zaehlen und messen."""
    def w(self, start):
        neu = tuple(start) not in self._suche
        t0 = _time.perf_counter()
        try:
            return f(self, start)
        finally:
            if neu:
                _GF_ZEIT["Karte.suche neu"] = _GF_ZEIT.get("Karte.suche neu", 0.0) + _time.perf_counter() - t0
                _GF_ZAHL["Karte.suche neu"] = _GF_ZAHL.get("Karte.suche neu", 0) + 1
    w._gemessen = True
    return w


_GF_ZEIT = {}
if hasattr(GF, "Karte") and not getattr(GF.Karte.suche, "_gemessen", False):
    GF.Karte.suche = _suche_gemessen(GF.Karte.suche)
for _n in ("sicherer_weg", "erreichbare_schuetzen", "schuetzen_am_weg", "mindestzahl"):
    if hasattr(GF, _n) and not getattr(getattr(GF, _n), "_gemessen", False):
        _f = _gf_gemessen(getattr(GF, _n), "GF." + _n)
        _f._gemessen = True
        setattr(GF, _n, _f)
