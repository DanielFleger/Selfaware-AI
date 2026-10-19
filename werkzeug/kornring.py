# -*- coding: utf-8 -*-
"""Kornspeicher einmauern wie der Nomade (Daniel 18.10. 22:45: "machs doch einfach wie Nomade und bau den Kornspeicher ein
bis auf die Ecken, problem geloest").

Anlass 1018d/e: die Assassinen des Gegners rissen den Kornspeicher von Spieler 1 ein (1018e: 4-mal), mit ihm ging der
Vorrat verloren (Tick 14.953: Aepfel 16 -> 0 in einer Runde), danach fiel die Beliebtheit bis unter 50.

Vorbild (gelesen aus Nomade1.aiv, Ascension-AI-Tournament 3.0.7 und Mod-KI-Team-Liga 2.0.2 gleich): der Kornspeicher (4x4)
ist an allen vier Seiten direkt von hoher Zinnenmauer umgeben, je Seite 4 Kacheln; die 4 Ecken bleiben frei (dort setzt
der Nomade erst ganz am Ende Fallgruben, Schritte 987-990); die Mauer kommt im Bauplan VOR dem Kornspeicher (Schritte 3, 6
vor 9).

Gebaut wird wie ein Mensch ueber Spielbefehl 25 (ClickPlaceWall: x1, y1, x2, y2, Mapper, Kachelzahl), gemessen in
werkzeug/mauer_pruefen.py (Spielstand "Gute Wirtschaft", 18.10.):
  - hohe Steinmauer (Mapper 25): Hoehe 98, 4 Kacheln = 2 Stein; niedrige Mauer (46): 4 Kacheln = 1 Stein, kein Holz
    (abgelesen processWallBuildingLoss: hohe Kachel 2 Viertel, niedrige 1 Viertel Stein, Rest wird uebertragen)
  - Zinnenmauer (26) laesst sich so NICHT setzen (frei und auf Steinmauer gemessen) - darum hohe Steinmauer
  - mit 0 Stein setzt das Spiel trotzdem EINE Kachel kostenlos (getWallTilesThatCanBeBuilt 0, die Schleife prueft erst nach
    der ersten Kachel) - deshalb sendet dieser Baustein nur, wenn der Stein die ganze Strecke bezahlt (keine Gratismauer)
  - eine Strecke scheitert GANZ, wenn auf einer Kachel jemand steht, ein Feind naeher als 15 Felder oder ein feindliches
    Gebaeude naeher als 7 Felder ist (abgelesen validateWallBuildPath) - dann einzeln Kachel fuer Kachel nachholen

MOERDERLOECHER (Daniel 18.10. 23:05 "Burggraben mit eins Abstand mit Moerderloechern? Stein kommt viel zu spaet rein"; 23:07
"4 Holz ist ja wohl sehr wenig, wenn es einem Assassinen das Leben nimmt"): Fallgrube Typ 67 / Mapper 98, gebaut ueber den
normalen Baubefehl. Abgelesen (daten/dekomp_fallgrube.c, processDamageFromKillingPit): eine SCHARFE Grube (Zustand 0) zieht
jeder feindlichen Einheit auf ihrem Feld 18.000 Leben ab (Assassine 12.500 -> tot), danach ist sie ausgeloest (Zustand 1 -> 2)
und verschwindet spaeter (UpdateKillingPit); eigene Einheiten trifft sie nie (Teamvergleich). Gemessen (werkzeug/
grube_pruefen.py, 18.10.): erste feindliche Assassine starb auf dem Grubenfeld, die zweite lief heil darueber (verbraucht),
die eigene Assassine blieb heil; Preis im Spiel kosten(67) = 4 Holz (Ascension); setzen nur nahe der eigenen Gebaeude/Burg
(Platzsuche Spieler 2: (208,75) und (190,110) ja, (211,150) und (211,196) nein).
Gruben kommen zuerst auf die 4 offenen Ecken (wie der Nomade), solange die Mauer einer Seite fehlt und kein Stein fuer sie da
ist auch auf diese Seite (die dem Gegner naechsten Felder zuerst); ausgeloeste/verschwundene werden nachgebaut.
Pruefung ohne Spiel: werkzeug/kornring_pruefen.py."""

MAUER = 25              # M_MAPPER_WALL (hohe Steinmauer)
VIERTEL_JE_KACHEL = 2   # hohe Mauer: 2 Viertel Stein je Kachel (processWallBuildingLoss)
MAUERBIT = 0x100        # LogicLayer L_WALL_OR_GATEHOUSE
ABSTAND = 100           # Ticks zwischen zwei Pruefungen des Rings
GRUBE_HOLZ = 4          # Fallgrube: kosten(67) im laufenden Spiel (Ascension), gelesen 18.10.
HOLZ_RESERVE = 5        # ein Kornspeicher-Nachbau (kosten(19) = 5 Holz) geht vor
GRUBEN_JE_SCHRITT = 4
GESPERRT_TICKS = 1000   # lehnt das Spiel ein Grubenfeld ab (Platzsuche), so lange nicht erneut versuchen


def seiten(gx, gy):
    """Die vier Ringseiten um einen Kornspeicher mit linker oberer Ecke (gx, gy): je (Name, (x1, y1), (x2, y2), Kacheln).
    Die Ecken (gx-1, gy-1) usw. gehoeren NICHT dazu - dort bleibt der Zugang frei."""
    return [("oben", (gx, gy - 1), (gx + 3, gy - 1), [(x, gy - 1) for x in range(gx, gx + 4)]),
            ("unten", (gx, gy + 4), (gx + 3, gy + 4), [(x, gy + 4) for x in range(gx, gx + 4)]),
            ("links", (gx - 1, gy), (gx - 1, gy + 3), [(gx - 1, y) for y in range(gy, gy + 4)]),
            ("rechts", (gx + 4, gy), (gx + 4, gy + 3), [(gx + 4, y) for y in range(gy, gy + 4)])]


def kasten(gx, gy):
    """Flaeche, die fuer andere Bauten frei bleibt: Kornspeicher, Ring und Ecken (x0, y0, x1, y1 einschliesslich)."""
    return (gx - 1, gy - 1, gx + 4, gy + 4)


def ecken(gx, gy):
    return [(gx - 1, gy - 1), (gx + 4, gy - 1), (gx - 1, gy + 4), (gx + 4, gy + 4)]


def bezahlbar(stein, kacheln):
    """Stein deckt <kacheln> hohe Kacheln ganz - mit einem Stein Reserve fuer einen angefangenen Viertel-Rest (der
    Uebertrag kann die Rechnung um eins verschieben). Nie bei 0 Stein (Gratiskachel)."""
    return stein >= 1 and stein * 4 >= kacheln * VIERTEL_JE_KACHEL + 4


class Kornring:
    """ort: linke obere Ecke des Kornspeichers, um den der Ring entsteht. lies_mauer(kacheln) -> {kachel: True/False};
    setze(x1, y1, x2, y2, n) sendet Spielbefehl 25."""

    def __init__(self, ort, lies_mauer, setze, abstand=ABSTAND, setze_grube=None, feind=None):
        self.ort = tuple(ort)
        self.lies_mauer, self.setze, self.abstand = lies_mauer, setze, abstand
        self.setze_grube = setze_grube          # (x, y) -> True, wenn gesendet (das Spiel nahm den Platz an)
        self.feind = tuple(feind) if feind else None
        self.gesperrt = {}                       # Grubenfeld -> Tick der Ablehnung
        self.tor = []                            # Eingang im Burggraben (Graben.tor) - Gruben dort gleich nach den Ecken
        self.gruben_gesetzt = 0
        self.zuletzt = -10 ** 9
        self.versucht = {}          # Seite -> wie oft die ganze Strecke gesendet wurde, ohne dass sie stand
        self.fehlt = 16
        self.fertig_gemeldet = False
        self.gesendet = 0
        self.gewartet = None        # zuletzt gemeldeter Wartegrund - "wartet auf Stein" nur bei einer Aenderung melden

    def stein_bedarf(self):
        """So viel Stein soll der Verkauf zuruecklassen, solange der Ring nicht steht."""
        return 0 if self.fehlt == 0 else (self.fehlt * VIERTEL_JE_KACHEL + 3) // 4 + 1

    def schritt(self, t, stein, holz=0, gruben=()):
        """Je Runde aufrufen. gruben: Felder mit einer eigenen Fallgrube. Gibt Ereignistexte."""
        if t - self.zuletzt < self.abstand:
            return []
        self.zuletzt = t
        gruben = set(gruben)
        s = seiten(*self.ort)
        alle = [k for _, _, _, ks in s for k in ks]
        steht = self.lies_mauer(alle)
        # ein Feld mit Grube bekommt (vorerst) keine Mauer - das Spiel lehnt Mauern auf Gebaeuden ab
        fehlen = {name: [k for k in ks if not steht.get(k) and k not in gruben] for name, _, _, ks in s}
        self.fehlt = sum(len(v) for v in fehlen.values())
        ev = self._gruben(t, stein, holz, gruben, steht) if self.setze_grube else []
        if self.fehlt == 0:
            if not self.fertig_gemeldet:
                self.fertig_gemeldet = True
                ev.append("KORNRING um %s steht: %d Mauerkacheln, %d Gruben (Ecken), %d Befehle gesendet" % (
                    self.ort, sum(1 for k in alle if steht.get(k)), len(gruben), self.gesendet))
            return ev
        self.fertig_gemeldet = False
        rest, warten = stein, []
        for name, a, b, ks in s:
            offen = fehlen[name]
            if not offen:
                self.versucht.pop(name, None)
                continue
            if self.versucht.get(name, 0) == 0 and len(offen) == len(ks):
                # ganze Seite in einem Befehl (wie ein Mensch zieht)
                if not bezahlbar(rest, len(ks)):
                    warten.append(name)
                    continue
                self.setze(a[0], a[1], b[0], b[1], len(ks))
                self.versucht[name] = 1
                self.gesendet += 1
                rest -= (len(ks) * VIERTEL_JE_KACHEL + 3) // 4
                ev.append("KORNRING Seite %s gesendet (%d Kacheln, %s-%s)" % (name, len(ks), a, b))
            else:
                # Strecke stand nicht (jemand stand darauf, Feind nah) oder nur Teile fehlen: Kachel fuer Kachel
                for k in offen:
                    if not bezahlbar(rest, 1):
                        warten.append("%s %s" % (name, k))
                        break
                    self.setze(k[0], k[1], k[0], k[1], 1)
                    self.gesendet += 1
                    rest -= 1
                    ev.append("KORNRING Kachel %s (Seite %s) einzeln gesendet" % (k, name))
                self.versucht[name] = self.versucht.get(name, 0) + 1
        grund = (tuple(warten), self.fehlt) if warten else None
        if grund and grund != self.gewartet:
            ev.append("KORNRING wartet auf Stein: %s (%d Stein da, %d Kacheln fehlen, Bedarf %d)" % (
                ", ".join(warten), rest, self.fehlt, self.stein_bedarf()))
        self.gewartet = grund
        return ev

    def grubenplaetze(self, stein, gruben, steht):
        """Reihenfolge der Felder, die eine Grube bekommen sollen: die 4 Ecken, der Eingang im Burggraben, dann - nur wenn der Stein nicht einmal
        fuer eine Mauerkachel reicht - die freien Seitenfelder, die dem Gegner naechsten zuerst."""
        ziele = list(ecken(*self.ort)) + [k for k in self.tor if k not in ecken(*self.ort)]
        if not bezahlbar(stein, 1):
            seite = [k for _, _, _, ks in seiten(*self.ort) for k in ks if not steht.get(k)]
            if self.feind:
                seite.sort(key=lambda k: max(abs(k[0] - self.feind[0]), abs(k[1] - self.feind[1])))
            ziele += seite
        return [k for k in ziele if k not in gruben]

    def _gruben(self, t, stein, holz, gruben, steht):
        ev, gesetzt, rest = [], [], holz
        for k in self.grubenplaetze(stein, gruben, steht):
            if len(gesetzt) >= GRUBEN_JE_SCHRITT or rest < GRUBE_HOLZ + HOLZ_RESERVE:
                break
            if t - self.gesperrt.get(k, -10 ** 9) < GESPERRT_TICKS:
                continue
            if self.setze_grube(k[0], k[1]):
                gesetzt.append(k)
                rest -= GRUBE_HOLZ
                self.gruben_gesetzt += 1
            else:
                self.gesperrt[k] = t
                ev.append("KORNRING Grube bei %s vom Spiel abgelehnt (Platzsuche) - %d Ticks Pause" % (k, GESPERRT_TICKS))
        if gesetzt:
            ev.append("KORNRING Gruben gesetzt %s (Holz %d -> ~%d, stehen schon %d)" % (gesetzt, holz, rest, len(gruben)))
        return ev


# ---------------------------------------------------------------------------------------------------------------------
# BURGGRABEN um den Kornspeicher (Daniel 19.10. 10:31 "gerne" zum Vorschlag: Graben mit einem Feld Abstand, ein Eingang auf
# der vom Gegner abgewandten Seite, Moerderloecher in den Eingang). Gemessen/abgelesen (Wissensregister L126):
#   planen  = Spielbefehl 21 (x, y, Pinsel, L_MOAT 0x40000000, Flag 2): immer ein 3x3-Block um (x, y); Flag 2 = 0 plant
#             (LogicLayer-Bit 0x4000), = 1 loescht die Planung. Flag 2 = 2 (fertiger Graben ohne Kosten) NIE.
#   ausheben = angriff mit "graben": [x, y] (Befehl 36 Art 6); Graeber arbeiten danach von selbst alle geplanten Felder ab.
# Weil der Pinsel 3x3 ist: Bloecke mit der Mitte auf Abstand 3 planen (deckt 2..4), dann Bloecke auf Abstand 4 loeschen
# (deckt 3..5) - stehen bleibt genau der Ring auf Abstand 2. Der Eingang: ein Loesch-Block auf Abstand 2 mitten auf der
# vom Gegner abgewandten Seite (3 Felder breit). Abstand = Felder vom 4x4-Speicher (Schachbrett-Abstand).
GRABEN_D = 2
GEPLANT, GEGRABEN = 0x4000, 0x40000000
L_MOAT = 0x40000000
GRAEBER_TYPEN = (24, 25, 71, 22, 30)     # Speer, Pike, Sklave, Bogen, Ingenieur - Streitkolben (26) gehoeren dem Feldzug
GRAEBER_ZAHL = 4
GRAEBER_UMKREIS = 80                     # nur Einheiten so nah am Speicher (sonst laufen sie durch die halbe Karte)
GRABEN_NEU_TICKS = 300                   # so oft die Graeber erneut schicken, solange Felder fehlen
PLAN_NEU_TICKS = 1000                    # so oft fehlende Planung nachholen (scheitert z. B. an Feinden naeher als 15)
PLAN_GLEICH_TICKS = 5000                 # fehlen nach dem Planen dieselben Felder (bebaut), erst so spaet wieder versuchen


def ring(gx, gy, d):
    """Felder im Schachbrett-Abstand d um den 4x4-Speicher (linke obere Ecke gx, gy), im Uhrzeigersinn ab oben links."""
    x0, y0, x1, y1 = gx - d, gy - d, gx + 3 + d, gy + 3 + d
    oben = [(x, y0) for x in range(x0, x1 + 1)]
    rechts = [(x1, y) for y in range(y0 + 1, y1 + 1)]
    unten = [(x, y1) for x in range(x1 - 1, x0 - 1, -1)]
    links = [(x0, y) for y in range(y1 - 1, y0, -1)]
    return oben + rechts + unten + links


def eingang(gx, gy, feind):
    """Mitte und 3 Felder des Eingangs auf Abstand GRABEN_D, auf der Seite, die dem Gegner abgewandt ist."""
    mx, my = gx + 1.5, gy + 1.5
    dx, dy = (feind[0] - mx, feind[1] - my) if feind else (0, -1)
    d = GRABEN_D
    if abs(dx) >= abs(dy):
        x = gx - d if dx > 0 else gx + 3 + d          # Gegner rechts -> Eingang links
        mitte = (x, gy + 1)
        felder = [(x, gy + 1 + k) for k in (-1, 0, 1)]
    else:
        y = gy - d if dy > 0 else gy + 3 + d          # Gegner unten -> Eingang oben
        mitte = (gx + 1, y)
        felder = [(gx + 1 + k, y) for k in (-1, 0, 1)]
    return mitte, felder


def graben_soll(gx, gy, feind):
    _, tor = eingang(gx, gy, feind)
    return [k for k in ring(gx, gy, GRABEN_D) if k not in tor]


def _mitten(gx, gy, d):
    r = ring(gx, gy, d)
    x0, y0, x1, y1 = gx - d, gy - d, gx + 3 + d, gy + 3 + d
    ecke = {(x0, y0), (x1, y0), (x0, y1), (x1, y1)}
    return [k for i, k in enumerate(r) if i % 3 == 0 or k in ecke]


def plan_befehle(gx, gy, feind):
    """Befehlsfolge (x, y, flag2) fuer Spielbefehl 21: planen auf Abstand 3, loeschen auf Abstand 4, Eingang loeschen."""
    mitte, _ = eingang(gx, gy, feind)
    return ([(x, y, 0) for x, y in _mitten(gx, gy, GRABEN_D + 1)] +
            [(x, y, 1) for x, y in _mitten(gx, gy, GRABEN_D + 2)] +
            [(mitte[0], mitte[1], 1)])


def pinsel(befehle, frei=lambda k: True):
    """Ergebnis einer Befehlsfolge auf einer leeren Karte (fuer die Pruefung ohne Spiel): Menge der geplanten Felder."""
    geplant = set()
    for x, y, f2 in befehle:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                k = (x + dx, y + dy)
                if not frei(k):
                    continue
                if f2 == 0:
                    geplant.add(k)
                elif f2 == 1:
                    geplant.discard(k)
    return geplant


def graeber_waehlen(L, sp, ort, ausgenommen=(), n=GRAEBER_ZAHL):
    """Die n naechsten eigenen grabfaehigen Einheiten am Speicher, ohne ausgenommene (Feldzug, Wache, Assassinen-Trupp)."""
    mx, my = ort[0] + 1, ort[1] + 1
    kand = [(max(abs(e["x"] - mx), abs(e["y"] - my)), nr) for nr, e in L.items()
            if e["besitzer"] == sp and e["typ"] in GRAEBER_TYPEN and nr not in ausgenommen and e.get("leben", 1) > 0]
    return [nr for d, nr in sorted(kand) if d <= GRAEBER_UMKREIS][:n]


class Graben:
    """ort: Kornspeicher (linke obere Ecke). lies_logik(kacheln) -> {kachel: LogicLayer-Wert}; plane(x, y, flag2);
    schicke(einheiten, (x, y)) = angriff graben."""

    def __init__(self, ort, feind, lies_logik, plane, schicke):
        self.ort, self.feind = tuple(ort), tuple(feind) if feind else None
        self.lies_logik, self.plane, self.schicke = lies_logik, plane, schicke
        self.soll = graben_soll(self.ort[0], self.ort[1], self.feind)
        self.tor = eingang(self.ort[0], self.ort[1], self.feind)[1]
        self.geplant_tick = -10 ** 9
        self.geschickt_tick = -10 ** 9
        self.graeber = set()
        self.fertig = False
        self.stand = {"geplant": 0, "gegraben": 0}
        self.zuletzt = -10 ** 9
        self.offen_vorher = None                 # fehlende Planfelder beim letzten Planen (bebaute bleiben bebaut)
        self.wiederholt = 0                      # wie oft hintereinander mit gleich vielen fehlenden Feldern geplant

    def kasten(self):
        """Flaeche fuer andere Bauten tabu: Speicher bis einschliesslich Grabenring."""
        d = GRABEN_D
        return (self.ort[0] - d, self.ort[1] - d, self.ort[0] + 3 + d, self.ort[1] + 3 + d)

    def schritt(self, t, L, sp, ausgenommen=()):
        ev = []
        if self.fertig or t - self.zuletzt < ABSTAND:
            return ev
        self.zuletzt = t
        werte = self.lies_logik(self.soll)
        gegraben = [k for k in self.soll if werte.get(k, 0) & GEGRABEN]
        geplant = [k for k in self.soll if werte.get(k, 0) & GEPLANT and not werte.get(k, 0) & GEGRABEN]
        offen = [k for k in self.soll if not werte.get(k, 0) & (GEPLANT | GEGRABEN)]
        self.stand = {"geplant": len(geplant), "gegraben": len(gegraben), "offen": len(offen)}
        if len(gegraben) == len(self.soll):
            self.fertig = True
            self.graeber = set()
            ev.append("GRABEN um %s fertig: %d Felder ausgehoben, Eingang %s" % (self.ort, len(gegraben), self.tor))
            return ev
        # 19.10. (Walltest 4: 7 bebaute Felder liessen alle ~1.370 Ticks 30 Planbefehle laufen): bleibt die Zahl der fehlenden
        # Felder gleich, EIN schneller Wiederholversuch (ein Feind kann nur vorbeigelaufen sein), dann PLAN_GLEICH_TICKS
        gleich = len(offen) == self.offen_vorher
        warte = PLAN_GLEICH_TICKS if gleich and self.wiederholt >= 1 else PLAN_NEU_TICKS
        if offen and t - self.geplant_tick >= warte:
            self.wiederholt = self.wiederholt + 1 if gleich else 0
            self.geplant_tick = t
            self.offen_vorher = len(offen)
            befehle = plan_befehle(self.ort[0], self.ort[1], self.feind)
            for x, y, f2 in befehle:
                self.plane(x, y, f2)
            ev.append("GRABEN um %s geplant (%d Befehle; %d Felder fehlten in der Planung)" % (self.ort, len(befehle), len(offen)))
        if geplant and t - self.geschickt_tick >= GRABEN_NEU_TICKS:
            noch = [nr for nr in self.graeber if nr in L and L[nr].get("leben", 1) > 0]
            neu = graeber_waehlen(L, sp, self.ort, set(ausgenommen) | set(noch), GRAEBER_ZAHL - len(noch))
            self.graeber = set(noch) | set(neu)
            if self.graeber:
                ziel = min(geplant, key=lambda k: abs(k[0] - self.ort[0]) + abs(k[1] - self.ort[1]))
                self.schicke(sorted(self.graeber), ziel)
                self.geschickt_tick = t
                ev.append("GRABEN %d Graeber %s nach %s (geplant %d, ausgehoben %d von %d)" % (
                    len(self.graeber), sorted(self.graeber), ziel, len(geplant), len(gegraben), len(self.soll)))
        return ev
