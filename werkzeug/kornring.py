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
Pruefung ohne Spiel: werkzeug/kornring_pruefen.py."""

MAUER = 25              # M_MAPPER_WALL (hohe Steinmauer)
VIERTEL_JE_KACHEL = 2   # hohe Mauer: 2 Viertel Stein je Kachel (processWallBuildingLoss)
MAUERBIT = 0x100        # LogicLayer L_WALL_OR_GATEHOUSE
ABSTAND = 100           # Ticks zwischen zwei Pruefungen des Rings


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


def bezahlbar(stein, kacheln):
    """Stein deckt <kacheln> hohe Kacheln ganz - mit einem Stein Reserve fuer einen angefangenen Viertel-Rest (der
    Uebertrag kann die Rechnung um eins verschieben). Nie bei 0 Stein (Gratiskachel)."""
    return stein >= 1 and stein * 4 >= kacheln * VIERTEL_JE_KACHEL + 4


class Kornring:
    """ort: linke obere Ecke des Kornspeichers, um den der Ring entsteht. lies_mauer(kacheln) -> {kachel: True/False};
    setze(x1, y1, x2, y2, n) sendet Spielbefehl 25."""

    def __init__(self, ort, lies_mauer, setze, abstand=ABSTAND):
        self.ort = tuple(ort)
        self.lies_mauer, self.setze, self.abstand = lies_mauer, setze, abstand
        self.zuletzt = -10 ** 9
        self.versucht = {}          # Seite -> wie oft die ganze Strecke gesendet wurde, ohne dass sie stand
        self.fehlt = 16
        self.fertig_gemeldet = False
        self.gesendet = 0
        self.gewartet = None        # zuletzt gemeldeter Wartegrund - "wartet auf Stein" nur bei einer Aenderung melden

    def stein_bedarf(self):
        """So viel Stein soll der Verkauf zuruecklassen, solange der Ring nicht steht."""
        return 0 if self.fehlt == 0 else (self.fehlt * VIERTEL_JE_KACHEL + 3) // 4 + 1

    def schritt(self, t, stein):
        """Je Runde aufrufen. Gibt Ereignistexte."""
        if t - self.zuletzt < self.abstand:
            return []
        self.zuletzt = t
        s = seiten(*self.ort)
        alle = [k for _, _, _, ks in s for k in ks]
        steht = self.lies_mauer(alle)
        fehlen = {name: [k for k in ks if not steht.get(k)] for name, _, _, ks in s}
        self.fehlt = sum(len(v) for v in fehlen.values())
        if self.fehlt == 0:
            if not self.fertig_gemeldet:
                self.fertig_gemeldet = True
                return ["KORNRING um %s steht: 16 von 16 Mauerkacheln (Ecken frei), %d Befehle gesendet" % (self.ort, self.gesendet)]
            return []
        self.fertig_gemeldet = False
        ev, rest, warten = [], stein, []
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
