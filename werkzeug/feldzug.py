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
    TRUPP = 5                 # B-158: Angriffe auf Bresche und Lord in Trueppchen zu 5 (gemessen: halbe Zeit gegenueber der Gruppe)
    MAUER_R = 30              # B-147: so weit um den Lord sucht logik.lua die Mauerkachel (Burgradius wie BURG_R-Groessenordnung)
    SICHER = 50               # Felder Abstand des Sammelpunkts zu feindlichen Fernkaempfern (Reichweite 44 + Rand)
    GEB_ABSTAND = 30          # ... und zu feindlichen Gebaeuden (Tuerme, Mauern mit Schuetzen)
    AM_PUNKT = 10             # so nah am Sammelpunkt gilt als "da"
    VERTEIDIGEN = 18          # Feind so nah am Sammelpunkt -> angreifen
    WIEDERHOLEN = 5           # Runden zwischen zwei Angriffsbefehlen
    ANGRIFF_NAH = 4           # so nah am Lord: Angriffsbefehl statt Laufbefehl
    WEGPUNKT_NAH = 4          # so nah am Wegpunkt (Mitte des Haufens): naechster Wegpunkt
    MIN_ANGRIFF = 8           # 19.10.: so viele am Sammelpunkt mindestens, dann entscheidet die Gefechtsrechnung
    LORD_UMKREIS = 25         # 19.10.: feindliche Truppen so nah am Lord kaempfen mit (Gefechtsrechnung)
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
    BRESCHE_ZAEH = 1000       # (B-140 22:16: 3.000 liess 35 Mann unter Beschuss stehen)
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
    WIRKUNG_TAKTE = 300       # B-165: so lange ohne Fortschritt am Ziel, obwohl TOR_MIN daneben stehen -> umplanen (UNGEMESSEN)
    WIRKUNG_NAH = 8           # B-165: "daneben" = so nah am Gebaeude (bis 7x7) bzw. bis 3 Felder an einer erreichbaren Mauer
    SCHREDDER_PAUSE = 1500    # B-165: Schredder ohne Wirkung -> so lange Bresche (Turm/Torhaus) statt Mauer

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
        self._wirkung_stand = {}    # B-165: Ziel -> (Wert, Takt seit dem letzten Fortschritt)
        self._lord_frei_alt = None  # B-163: letzter gemeldeter Stand "Lord zu Fuss erreichbar"
        self.vorposten = None       # B-139: (Bresche, erreichbarer Punkt vor ihr)
        self.lord_vp = None         # B-139: (Lord-Ort, erreichbarer Punkt am Lord oder None, Runde der Pruefung)
        self._lagebild = None       # B-140: Lagebild der laufenden Runde (Schuetzen fuer die Wahl der Angriffsstelle)
        self.angriff_ab = None      # B-140 Versuchsreihe (Daniel 22:09 "so viele Variablen ... dafuer die Tests"): fester
        #                             Angriffszeitpunkt ab so vielen Truppen statt der Gefechtsrechnung (Schalter angriff_ab)
        self.bresche_leben = None   # B-138: (niedrigstes Leben der Bresche, seit Tick)
        self.verworfen = set()      # B-138: zaehe Breschen - nicht noch einmal waehlen
        self._bresche_pruef = (None, -99)   # B-140: (Bresche, Runde) der letzten Pruefung mit dem Wegfinder
        self.mauer_seit = None      # B-147: Tick, seit dem die Mauer am eingemauerten Lord aufgehackt wird
        self._spur = {}             # B-146: je Nahkaempfer (Ort, Leben, still seit Tick, letzter Schaden bei Tick)

    NACHBAR_RINGE = (1, 2, 3)  # B-140: so nah am Gebaeude muss ein Feld erreichbar sein, sonst ist es nicht angreifbar
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
            hackt = befohlen.get(n, (None,))[0] == "mauer" and e.get("zustand") not in (0, 1)
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

    def _lage_lord(self, L, lp, nah_kampf, besitzer):
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
        if g_lord in (g, 0):
            for r in self.LORD_RINGE:
                ring = [(lp[0] + dx, lp[1] + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                        if max(abs(dx), abs(dy)) == r]
                ring = [q for q in ring if k.drin(q) and geb[q[0], q[1]] == g]
                if ring:
                    frei = min(ring)
                    break
            if frei is None and g_lord == g:
                frei = tuple(lp)
        aus = {"gebiet": g, "gebiet_lord": g_lord, "frei": frei, "mauern": 0, "hoehe": None, "nah": None}
        if frei is None and self.mauerkarte is not None:
            try:
                m, h = self.mauerkarte(besitzer)
            except Exception as ex:                      # Spiel nicht lesbar: ohne Schredder wie vorher
                self.wegkarte_fehler = "Mauerkarte: %s" % str(ex)[:100]
                return aus
            fen = np.zeros(m.shape, bool)
            fen[max(0, lp[0] - self.MAUER_R):lp[0] + self.MAUER_R + 1, max(0, lp[1] - self.MAUER_R):lp[1] + self.MAUER_R + 1] = True
            ziel_m = m & fen & self._breit(geb == g, 1)
            aus.update(mauern=int(ziel_m.sum()), hoehe=int(np.asarray(h)[m & fen].sum()), nah=self._breit(ziel_m, 3))
        return aus

    def _wirkung(self, ziel, wert, nah, t):
        """B-165 Wirkungswaechter: Fortschritt am Ziel je Runde (wert sinkt = Wirkung: Leben, Mauerhoehe). Stehen mindestens
        TOR_MIN eigene Nahkaempfer daneben (nah) und sinkt wert WIRKUNG_TAKTE lang nicht, Rueckgabe = Takte ohne Wirkung (und der
        Zaehler beginnt neu), sonst None. Wer nicht daneben steht, zaehlt nicht - Laufen ist keine fehlende Wirkung."""
        alt = self._wirkung_stand.get(ziel)
        if alt is None or wert < alt[0] or nah < self.TOR_MIN:
            self._wirkung_stand[ziel] = (wert, t)
            return None
        if t - alt[1] >= self.WIRKUNG_TAKTE:
            del self._wirkung_stand[ziel]
            return t - alt[1]
        return None

    def _zustaende(self, L, ns):
        z = {}
        for n in ns:
            z[L[n].get("zustand")] = z.get(L[n].get("zustand"), 0) + 1
        return ", ".join("%s: %d" % (k, v) for k, v in sorted(z.items(), key=lambda kv: -kv[1]))

    def _neue_karte(self, bed):
        """B-157/B-161: Gefahrenkarte dieser Runde - mit den Gebieten des Spiels, wenn die Wegkarte lesbar ist."""
        geb = None
        if self.wegkarte is not None:
            try:
                geb = self.wegkarte()["gebiet"]
                self.wegkarte_fehler = None
            except Exception as ex:                      # Spiel nicht lesbar: wie vorher ohne Gebiete, Grund merken
                self.wegkarte_fehler = str(ex)[:120]
        return GF.Karte(bed, feuer=self._orte_f, gebiete=geb)

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
        er = {b[4] for b in GF.erreichbare_schuetzen(start, self._karte)}
        frei = [n for n in nah_kampf if not any(n in v for v in auftraege.values())]
        rest = len(nah_kampf) // self.ABFANG_ANTEIL - sum(len(v) for v in auftraege.values())
        for treffer, art, ort in GF.schuetzen_am_weg(start, weg, self._karte):
            k = int(art.split()[1])
            if art not in er or k in auftraege or k not in L:
                continue
            noetig = GF.mindestzahl(L[k].get("leben", 1), self.ABFANG_TAKTE)
            if noetig > rest or noetig > len(frei):
                aus.append("FELDZUG ABFANG ZU TEUER: Schuetze %d bei %s braucht %d, frei %d (Anteil-Rest %d)" % (
                    k, ort, noetig, len(frei), rest))
                continue
            frei.sort(key=lambda n: schach((L[n]["x"], L[n]["y"]), ort))
            auftraege[k], frei, rest = frei[:noetig], frei[noetig:], rest - noetig
            aus.append("FELDZUG ABFANG: %d Nahkaempfer auf Schuetze %d (Typ %d, Leben %d) bei %s - bestreicht %d Wegfelder, zu "
                       "Fuss erreichbar (Gebiet %d); Mindestzahl bei %d Takten (Schaden je Takt %d UNGEMESSEN)" % (
                           noetig, k, L[k]["typ"], L[k].get("leben", 0), ort, treffer, self._karte.gebiet_bei(start),
                           self.ABFANG_TAKTE, GF.NAHKAMPF_SCHADEN))
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
                    self._karte = self._neue_karte(bed_ or [])
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
        Leben, bei Gleichstand der naechste an unserer Spitze. Setzt self.bresche; False, wenn es keinen gibt."""
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

    def _erreichbar_bei(self, ziel, nr, mitte, ringe, gefahr=None):
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
        treffer = [q for q, g in zip(punkte, gut) if g]
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
                                    gefahr=lambda q: sum(1 for f, r in schuetzen if schach(q, f) <= r))

    def _lords(self, L):
        return {n: e for n, e in L.items() if e["typ"] == LORD and e["besitzer"] not in freunde_von(self.sp) and e["leben"] > 0}

    def _sammelpunkt(self, L, G, lord):
        """Auf der Linie Heim -> Lord von vorn nach hinten der erste Punkt, der SICHER Felder von jedem feindlichen
        Fernkaempfer und GEB_ABSTAND von jedem feindlichen Gebaeude entfernt ist."""
        fern = [(e["x"], e["y"]) for e in L.values() if e["besitzer"] not in freunde_von(self.sp) and e["typ"] in FERN]
        geb = [(g["x"], g["y"]) for g in G.values() if g["besitzer"] not in freunde_von(self.sp)]
        h, z = self.heim, (lord["x"], lord["y"])
        d = max(1, schach(h, z))
        for k in range(d, -1, -2):
            q = (h[0] + (z[0] - h[0]) * k // d, h[1] + (z[1] - h[1]) * k // d)
            if all(schach(q, f) > self.SICHER for f in fern) and all(schach(q, b) > self.GEB_ABSTAND for b in geb):
                return q
        return h

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
        self._karte = self._neue_karte(self._bed) if self._bed or self.wegkarte is not None else None
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
            if da and "lauf" in an:
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
        aus = []
        befehl = self._feuer_lenken(st, L, G, befehl, aus)     # B-150: Feuer meiden, jede Runde neu
        t = st.get("t", 0)
        lords = self._lords(L)
        kolben = sorted(self.einheiten(L))
        if self.ziel is not None and self.ziel not in lords:
            self.tote_lords.append((self.ziel, t))
            aus.append("FELDZUG: Lord %d tot bei Tick %d - %d Streitkolben ueberlebten, naechstes Ziel" % (self.ziel, t, len(kolben)))
            self.ziel, self.phase, self.punkt = None, "sammeln", None
            self._stau, self.staus, self.direkt = (None, 0), 0, False
            self.bresche, self.bresche_leben, self.lord_versuch = None, None, None
        if not lords:
            return aus
        if self.ziel is None:
            self.ziel = min(lords, key=lambda n: (schach(self.heim, (lords[n]["x"], lords[n]["y"])), n))
            self.phase = "sammeln"
            aus.append("FELDZUG: Ziel Lord %d (Spieler %d) bei (%d, %d), %d Felder vom Bergfried" % (
                self.ziel, lords[self.ziel]["besitzer"], lords[self.ziel]["x"], lords[self.ziel]["y"],
                schach(self.heim, (lords[self.ziel]["x"], lords[self.ziel]["y"]))))
        lord = lords[self.ziel]
        lp = (lord["x"], lord["y"])
        if not kolben:
            return aus
        if self.phase == "sammeln":
            if self.punkt is None or self.runde % 20 == 0:
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
            ll = self._lage_lord(L, lp, [n for n in kolben if L[n]["typ"] not in FERN_REICH], lord["besitzer"])
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
                elif ll["mauern"] and t >= self.schredder_aus_bis:
                    if not self.schredder:
                        aus.append("FELDZUG SCHREDDER: Lord %d hinter Mauern - %d seiner Mauerkacheln bis %d Felder um ihn sind "
                                   "erreichbar, die Nahkaempfer hacken einzeln (Trupp %d) die naechste am Lord auf%s" % (
                                       self.ziel, ll["mauern"], self.MAUER_R, self.MAUER_TRUPP,
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
            if len(stehen) >= self.RUECKZUG_MIN:
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
                    self.vorposten = None
                    aus.append("FELDZUG VORPOSTEN ABGESCHNITTEN: %s vor Gebaeude %d nicht mehr erreichbar - neu suchen" % (
                        vp_alt, b_alt))
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
                leben_b = G[bresche].get("leben", -1)
                if (self.bresche_leben is None or self.bresche_leben[2] != bresche or leben_b < self.bresche_leben[0]
                        or len(am_tor) < self.TOR_MIN):
                    self.bresche_leben = (leben_b, t, bresche)
                # B-165 (Siegpartie 21:57: Torhaus 240 1.125 Takte bei 1.500 Leben mit 52 Mann "davor"): Wirkung messen statt
                # 1.000 Takte warten - stehen TOR_MIN bis WIRKUNG_NAH daneben und das Leben sinkt WIRKUNG_TAKTE lang nicht, weg
                nah_b = [n for n in nah_kampf if schach((L[n]["x"], L[n]["y"]), tor) <= self.WIRKUNG_NAH]
                ohne_b = self._wirkung(("bresche", bresche), leben_b, len(nah_b), t)
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
                # B-139: am erreichbaren Punkt (oder schon am Lord) -> Angriff; alle anderen laufen dorthin (einmal; erneut nur,
                # wer untaetig und nicht dort ist)
                am_lord = [n for n in nah_kampf if schach((L[n]["x"], L[n]["y"]), lp) <= self.ANGRIFF_NAH
                           or schach((L[n]["x"], L[n]["y"]), lord_ziel) <= self.AM_PUNKT]
                hin_l = [n for n in nah_kampf if n not in am_lord
                         and (befohlen.get(n) != ("zum_lord", lord_ziel) or L[n]["zustand"] in (0, 1))]
                if hin_l:
                    befehl({"angriff": {"einheiten": hin_l, "lauf": [lord_ziel[0], lord_ziel[1]]}}, 1.0, bis="ANGRIFF")
                    for n in hin_l:
                        befohlen[n] = ("zum_lord", lord_ziel)
                belegt |= set(nah_kampf) - set(am_lord)
            # B-147 (Daniel 21.10. 00:47 "ja, Mauer einreissen bauen und wieder messen"; L172: nach "Lord eingemauert" lief das
            # Heer immer wieder auf den unerreichbaren Lord, stand unter Beschuss und zog sich zurueck): ist der Lord eingemauert
            # und keine Bresche (Turm/Torhaus) mehr da, hacken alle Nahkaempfer, die es koennen, die naechste erreichbare Mauer
            # am Lord auf (logik.lua waehlt die Kachel, Spielbefehl 36 Art 23); jede 3. Runde wird geprueft, ob der Lord jetzt
            # erreichbar ist - dann geht es wie gehabt auf ihn
            if (lord_ziel is None and (self.schredder or self.lord_vp is not None) and (self.bresche is None or self.bresche not in G)
                    and self.ziel in L):
                wand = [n for n in nah_kampf if L[n]["typ"] in MAUER_TYPEN]
                if wand and self.schredder and ll is not None and ll["nah"] is not None:
                    # B-165: Wirkung des Schredders = die Mauern des Lord-Besitzers bis MAUER_R werden niedriger
                    nah_w = [n for n in wand if ll["nah"][L[n]["x"], L[n]["y"]]]
                    ohne_w = self._wirkung(("schredder", self.ziel), ll["hoehe"], len(nah_w), t)
                    if ohne_w is not None:
                        self.schredder, self.schredder_aus_bis = False, t + self.SCHREDDER_PAUSE
                        aus.append("FELDZUG KEINE WIRKUNG: Schredder %d Takte ohne niedrigere Mauer (Hoehe %d), %d Mann an der Mauer "
                                   "(Zustaende %s) - %d Takte Bresche statt Mauer" % (ohne_w, ll["hoehe"], len(nah_w),
                                                                                    self._zustaende(L, nah_w), self.SCHREDDER_PAUSE))
                        self._schwachstelle(G, lp, orte, aus, "Schredder ohne Wirkung")
                        wand = []
                if wand:
                    if self.mauer_seit is None:
                        self.mauer_seit = t
                        aus.append("FELDZUG MAUER: Lord %d eingemauert%s - %d Nahkaempfer hacken die Mauer bis %d Felder um den Lord "
                                   "auf, je %d" % (self.ziel, " (Schredder)" if self.schredder else ", kein Turm erreichbar", len(wand),
                                                   self.MAUER_R, self.MAUER_TRUPP))
                    neu_w = [n for n in wand if befohlen.get(n) != ("mauer", lp) or L[n]["zustand"] in (0, 1)]
                    if neu_w:
                        befehl({"angriff": {"einheiten": neu_w, "mauer": [lp[0], lp[1], L[self.ziel]["besitzer"], self.MAUER_R],
                                            "trupp": self.MAUER_TRUPP}}, 1.0, bis="ANGRIFF")
                        for n in neu_w:
                            befohlen[n] = ("mauer", lp)
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
            unterwegs = [n for n in kolben if n not in am_lord and n not in schiessen and n not in belegt
                         and (befohlen.get(n) != ("lauf", p) or L[n]["zustand"] in (0, 1))]
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
        if not sie and wir:
            return True, "keine Verteidiger an der Angriffsstelle (%d eigene)" % len(wir)   # B-140: dann lohnt es erst recht
        try:
            # B-140 (Pruefstand 22:04: 115 gegen 84 "offen nach 1500 Takten", mit 167 Sieg nach 1.460): am Ziel bis ZIEL_BIS rechnen
            return gefecht.bewerte(wir, sie, bis=self.ZIEL_BIS if am_ziel else gefecht.BIS)
        except Exception as ex:
            return False, "Rechnung fehlgeschlagen (%s)" % ex
