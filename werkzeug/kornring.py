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
        """Reihenfolge der Felder, die eine Grube bekommen sollen: die 4 Ecken, dann - nur wenn der Stein nicht einmal
        fuer eine Mauerkachel reicht - die freien Seitenfelder, die dem Gegner naechsten zuerst."""
        ziele = list(ecken(*self.ort))
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
