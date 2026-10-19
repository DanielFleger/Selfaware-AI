# -*- coding: utf-8 -*-
"""Raids mit Sklaven und berittenen Bogenschuetzen (Daniel 19.10. 16:49 "ausserdem fehlen noch Raids mit Sklaven und
berittenen Bogenschuetzen"; 16:57 "gesteuerte berittene Bogenschuetzen, die ja im Reiten schiessen koennen, koennten sehr
pervers sein ... Sklaven waeren als Raid besonders am Anfang einer Partie richtig OP - kosten wenig, und wenn Feuer erkannt
werden kann, koenntest du so gut wie alles anzuenden ... billiger als Assassinen"; 17:13 "eine Waffenkammer sollte fast
immer hoeher sein"; 17:14 "das Ziel ist immer noch den gegnerischen Lord zu killen - wenn jemand sieht, dass er jemanden
eindeutig killen oder snipen kann, sollte er angreifen").

GEMESSEN 19.10. (src/selfaware/tools/experiments/raid_messen.py, Spielstand "Walltest 4", data/research/raid_messung_20261019_17*.json):
  - Sklave (5 Gold, 6.000 Leben, L63) greift eine Holzfaellerhuette (60 Leben) an: nach ~165 Ticks brennt sie
    (fireDuration > 0, Verursacher = Spieler des Sklaven), nach ~485 Ticks ist sie weg - so schnell wie ein Speertraeger
    (12.500 Leben). Laeuft der Sklave nach dem Anzuenden weg, brennt sie ALLEIN ab (60 -> 52 -> 36 -> 20 -> 4 -> weg bei 489).
    Vier Nachbarn bis 3 Felder fingen kein Feuer (ein Fall).
  - Pferdebogen (75 Gold, 15.000 Leben) toetet einen Holzfaeller aus 12 Feldern mit dem ersten Pfeil (<= 44 Ticks).
    Ob er im Reiten schiesst: NICHT gemessen (Versuch gegen einen Speer im Spielstand mit Burg unbrauchbar).
  - Feuer lesen: Gebaeudedatensatz 0xF98520 + nr*0x32C, fireDuration bei +0x14+702 (short), Verursacher bei +0x14+734.

BRANDTRUPP (Sklaven): jeder Sklave nimmt das wertvollste ungefaehrliche feindliche Gebaeude (Wert je Weg), das noch nicht
brennt und das kein anderer Sklave hat; brennt es, zieht er sofort weiter. Gefaehrlich = feindlicher Schuetze oder Turm
bis GEFAHR_FERN Felder, feindlicher Nahkaempfer/Assassine bis GEFAHR_NAH, feindliche Fallgrube bis GRUBE_R.
REITERJAGD (Pferdebogen): Nahkaempfer/Assassine naeher als FLUCHT_R -> 12 Felder weg von ihm; sonst den naechsten
ungeschuetzten Arbeiter bis JAGD_R angreifen (Holzfaeller zuerst - 1018j: liefernde Holzfaeller entschieden die Partie);
gibt es dort keinen, zum naechsten ungeschuetzten Arbeiter irgendwo reiten (19.10. 17:41, Daniel: "hier stehen bei Orange
Berittene - die sollten im besten Fall immer beim Gegner raiden und in Bewegung sein").
Werbung nur aus Gold ueber der Ruecklage und nur, solange mindestens FEUER_MIN Bauern am Feuer stehen.
STARTWERTE (nicht gemessen, je Partie mitgeschrieben): SKLAVEN_SOLL, REITER_SOLL, WERT.
Pruefung ohne Spiel: src/selfaware/tools/checks/raids_pruefen.py."""

SKLAVE, PFERDEBOGEN = 71, 74
SKLAVE_GOLD, PFERD_GOLD = 5, 75                  # L63
SKLAVEN_SOLL = 5                                 # Startwert
REITER_SOLL = 3                                  # Startwert
FEUER_MIN = 2                                    # so viele Bauern bleiben am Feuer
GEFAHR_FERN = 20                                 # L81: Schuetzen entdecken bis 20 Felder
GEFAHR_NAH = 10
GRUBE_R = 3
FLUCHT_R = 8
JAGD_R = 20
NEU_ALLE = 5                                     # Runden zwischen zwei Befehlen an dieselbe Einheit
FERN = {22, 23, 70, 72, 74, 76}
NAH = {24, 25, 26, 27, 28, 55, 73, 75}
TUERME = {74, 75, 76, 77, 78}                    # Gebaeudetypen Wach-/Verteidigungs-/Geschuetz-/eckiger/runder Turm
GRUBE = 67
# Wert je Gebaeudeart (Startwerte): Waffenlager fast immer hoeher (Daniel 17:13), Soeldnerposten (dort entstehen die
# Assassinen), Kornspeicher (Nahrung, Beliebtheit), dann die Holzfaeller (1018j), Plantagen, Rest
# 19.10. 17:41 (Daniel, Bilder 1018n: Feuer im Huettenhof am Bergfried, mehrere Huetten brennen nebeneinander - "das ist
# natuerlich ein Jackpot, eigentlich hast du damit schon gewonnen ... wenn der Pennerhof brennt, ist das Spiel fast
# entschieden"): Huetten 2 -> 12, hoechster Wert; dicht stehende Huetten fangen voneinander Feuer (Daniels Bild; die eine
# Messung an einer Holzfaellerhuette mit Nachbarn bis 3 Felder zeigte kein Ueberspringen)
# 17:51 (Daniel: "die groessten Hebel sind Ausbildungen/Markt abreissen/abbrennen, Kornspeicher/Waffenkammer abreissen/
# abbrennen ... auch wenn sie weniger wert ist, kurz Feuer legen"): Kaserne, Soeldnerposten, Markt (fehlte ganz) 11,
# Kornspeicher und Waffenlager 10; kleine Ziele bleiben drin - Wert je Weg nimmt nahe Luecken mit
WERT = {1: 12, 9: 11, 8: 11, 26: 11, 11: 10, 19: 10, 3: 5, 5: 5, 13: 4, 18: 3, 32: 3, 31: 3, 33: 2, 10: 2}
# Arbeiter-Einheiten (ablaufanalyse.EINHEIT): Holzfaeller zuerst
# 19.10. 17:58 (Punkt 8, Daniel 17:42 "immer ein Jackpot, das Pennerlager zu belagern, da an der Bauern-Spawnrate bestimmt
# wird, ob man noch Bauern hat, um zu rekrutieren"; 17:58 "ja mach Punkt 8"): Bauern (Typ 1, am Lagerfeuer) zuerst - jeder tote
# Bauer fehlt dem Gegner beim Anwerben und als Arbeiter
ARBEITER = {1: 12, 3: 10, 13: 6, 31: 5, 8: 4, 7: 4, 14: 3, 19: 3, 21: 3, 6: 2, 12: 2, 11: 2}


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def feinde(L, sp):
    return [(e["typ"], (e["x"], e["y"])) for e in L.values() if e.get("besitzer") not in (0, sp) and e.get("leben", 1) > 0]


def gefaehrlich(ort, L, G, sp):
    for typ, p in feinde(L, sp):
        if typ in FERN and schach(ort, p) <= GEFAHR_FERN:
            return "Schuetze Typ %d in %d" % (typ, schach(ort, p))
        if typ in NAH and schach(ort, p) <= GEFAHR_NAH:
            return "Nahkaempfer Typ %d in %d" % (typ, schach(ort, p))
    for g in G.values():
        if g.get("besitzer") in (0, sp):
            continue
        if g["typ"] in TUERME and schach(ort, (g["x"], g["y"])) <= GEFAHR_FERN:
            return "Turm in %d" % schach(ort, (g["x"], g["y"]))
        if g["typ"] == GRUBE and schach(ort, (g["x"], g["y"])) <= GRUBE_R:
            return "Fallgrube in %d" % schach(ort, (g["x"], g["y"]))
    return None


class Brandtrupp:
    def __init__(self, sp, feuer):
        """feuer(nr) -> fireDuration des Gebaeudes nr (0 = brennt nicht)."""
        self.sp, self.feuer = sp, feuer
        self.ziel = {}              # Sklave -> Gebaeude
        self.befohlen = {}          # Sklave -> Runde
        self.brennt = set()         # Gebaeude, die wir brennen sahen
        self.angezuendet = 0
        self.runde = 0

    def einheiten(self, L):
        return {n for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] == SKLAVE and e.get("leben", 1) > 0}

    def _ziele(self, L, G, ort, belegt):
        kand = []
        for n, g in G.items():
            if g.get("besitzer") in (0, self.sp) or g["typ"] not in WERT or n in belegt or n in self.brennt:
                continue
            p = (g["x"], g["y"])
            if gefaehrlich(p, L, G, self.sp):
                continue
            kand.append((WERT[g["typ"]] / float(max(schach(ort, p), 1)), n))
        return [n for _, n in sorted(kand, reverse=True)]

    def schritt(self, L, G, befehl):
        self.runde += 1
        aus = []
        meine = self.einheiten(L)
        for s in list(self.ziel):
            if s not in meine or self.ziel[s] not in G:
                self.ziel.pop(s, None)
        # brennt ein Ziel, zieht der Sklave weiter (gemessen: es brennt allein ab). Gelesen wird nur, wenn der Sklave hoechstens
        # 4 Felder davor steht - jede Abfrage ist ein Weg durch den Kanal
        for s, nr in list(self.ziel.items()):
            if schach((L[s]["x"], L[s]["y"]), (G[nr]["x"], G[nr]["y"])) <= 4:
                f = self.feuer(nr)
                if f > 0:
                    self.brennt.add(nr)
                    self.angezuendet += 1
                    self.ziel.pop(s)
                    aus.append("BRANDTRUPP: Sklave %d hat Gebaeude %d (Typ %d) angezuendet (Feuer %d) - weiter" % (
                        s, nr, G[nr]["typ"], f))
        belegt = set(self.ziel.values())
        for s in sorted(meine):
            if s in self.ziel and self.runde - self.befohlen.get(s, -99) < NEU_ALLE:
                continue
            e = L[s]
            if s not in self.ziel:
                z = self._ziele(L, G, (e["x"], e["y"]), belegt)
                if not z:
                    continue
                self.ziel[s] = z[0]
                belegt.add(z[0])
                g = G[z[0]]
                aus.append("BRANDTRUPP: Sklave %d -> Gebaeude %d (Typ %d) bei (%d, %d), %d Felder" % (
                    s, z[0], g["typ"], g["x"], g["y"], schach((e["x"], e["y"]), (g["x"], g["y"]))))
            if self.befohlen.get(s, -99) < self.runde - NEU_ALLE or e.get("zustand") in (0, 1):
                befehl({"angriff": {"einheiten": [s], "gebaeude": self.ziel[s]}}, 1.0, bis="ANGRIFF")
                self.befohlen[s] = self.runde
        return aus

    def bericht(self):
        return "Brandtrupp: %d Gebaeude angezuendet" % self.angezuendet


class Reiterjagd:
    def __init__(self, sp):
        self.sp = sp
        self.befohlen = {}          # Reiter -> (Art, Ziel, Runde)
        self.getoetet = 0
        self.ziele_vorher = {}
        self.runde = 0

    def einheiten(self, L):
        return {n for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] == PFERDEBOGEN and e.get("leben", 1) > 0}

    def schritt(self, L, G, befehl):
        self.runde += 1
        aus = []
        self._abschuesse(L)
        for r in sorted(self.einheiten(L)):
            e = L[r]
            o = (e["x"], e["y"])
            # Flucht vor Nahkaempfern/Assassinen
            nah = min(((schach(o, (f["x"], f["y"])), k) for k, f in L.items()
                       if f["besitzer"] not in (0, self.sp) and f["typ"] in NAH and f.get("leben", 1) > 0), default=None)
            if nah and nah[0] < FLUCHT_R:
                f = L[nah[1]]
                dx, dy = o[0] - f["x"], o[1] - f["y"]
                n = max(abs(dx), abs(dy), 1)
                ziel = (o[0] + 12 * dx // n, o[1] + 12 * dy // n)
                if self.befohlen.get(r, (None,))[0] != "flucht" or self.runde - self.befohlen[r][2] >= NEU_ALLE:
                    befehl({"angriff": {"einheiten": [r], "lauf": [ziel[0], ziel[1]]}}, 1.0, bis="ANGRIFF")
                    self.befohlen[r] = ("flucht", ziel, self.runde)
                    aus.append("REITERJAGD: Reiter %d weicht Typ %d in %d Feldern aus -> %s" % (r, f["typ"], nah[0], ziel))
                continue
            kand = []
            for k, a in L.items():
                if a["besitzer"] in (0, self.sp) or a["typ"] not in ARBEITER or a.get("leben", 1) <= 0:
                    continue
                p = (a["x"], a["y"])
                d = schach(o, p)
                if d > JAGD_R or gefaehrlich(p, L, G, self.sp):
                    continue
                kand.append((-ARBEITER[a["typ"]], d, k))
            if not kand:
                # 17:41: nichts in Reichweite -> der naechste ungeschuetzte Arbeiter irgendwo (der Angriffsbefehl reitet hin)
                kand = [(0, schach(o, (a["x"], a["y"])), k) for k, a in L.items()
                        if a["besitzer"] not in (0, self.sp) and a["typ"] in ARBEITER and a.get("leben", 1) > 0
                        and not gefaehrlich((a["x"], a["y"]), L, G, self.sp)]
            if not kand:
                continue
            k = min(kand)[2]
            alt = self.befohlen.get(r)
            if alt is None or alt[:2] != ("jagd", k) or self.runde - alt[2] >= NEU_ALLE:
                befehl({"angriff": {"einheiten": [r], "ziel": k}}, 1.0, bis="ANGRIFF")
                self.befohlen[r] = ("jagd", k, self.runde)
                if alt is None or alt[:2] != ("jagd", k):
                    aus.append("REITERJAGD: Reiter %d jagt Arbeiter %d (Typ %d) in %d Feldern" % (
                        r, k, L[k]["typ"], schach(o, (L[k]["x"], L[k]["y"]))))
        return aus

    def _abschuesse(self, L):
        """Ein gejagtes Ziel, das nicht mehr lebt, zaehlt genau einmal; der Reiter ist danach frei."""
        for r, v in list(self.befohlen.items()):
            if v[0] == "jagd" and (v[1] not in L or L[v[1]].get("leben", 1) <= 0 or L[v[1]]["besitzer"] in (0, self.sp)):
                self.getoetet += 1
                self.befohlen.pop(r)

    def bericht(self):
        return "Reiterjagd: %d Arbeiter getoetet" % self.getoetet


def werbung(gold_frei, feuer, sklaven, reiter):
    """[(typ, anzahl)] - erst Sklaven bis SKLAVEN_SOLL, dann Reiter bis REITER_SOLL; nur Gold ueber der Ruecklage und nur
    so viele, dass FEUER_MIN Bauern am Feuer bleiben."""
    aus, frei, f = [], int(gold_frei), int(feuer) - FEUER_MIN
    n = max(0, min(SKLAVEN_SOLL - sklaven, frei // SKLAVE_GOLD, f))
    if n:
        aus.append((SKLAVE, n))
        frei -= n * SKLAVE_GOLD
        f -= n
    m = max(0, min(REITER_SOLL - reiter, frei // PFERD_GOLD, f))
    if m:
        aus.append((PFERDEBOGEN, m))
    return aus
