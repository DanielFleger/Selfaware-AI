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
bis GEFAHR_FERN Felder, feindlicher Nahkaempfer/Assassine bis GEFAHR_NAH. Feindliche Fallgruben nicht: im Spiel verborgen (F12).
REITERJAGD (Pferdebogen): Nahkaempfer/Assassine naeher als FLUCHT_R -> 12 Felder weg von ihm; sonst den naechsten
ungeschuetzten Arbeiter bis JAGD_R angreifen (Holzfaeller zuerst - 1018j: liefernde Holzfaeller entschieden die Partie);
gibt es dort keinen, zum naechsten ungeschuetzten Arbeiter irgendwo reiten (19.10. 17:41, Daniel: "hier stehen bei Orange
Berittene - die sollten im besten Fall immer beim Gegner raiden und in Bewegung sein").
Werbung nur aus Gold ueber der Ruecklage und nur, solange mindestens FEUER_MIN Bauern am Feuer stehen.
STARTWERTE (nicht gemessen, je Partie mitgeschrieben): SKLAVEN_SOLL, REITER_SOLL, WERT.
Pruefung ohne Spiel: src/selfaware/tools/checks/raids_pruefen.py.

Schalter ausweichen=ja (B-175, B-178, aus ist der Standard): Unter Beschuss laufen Sklaven im Zickzack auf ihr Gebaeude zu, jeder ein eigener Trupp beim Rust-Kern
(B-174, data/research/auge_plan/zickzack_20261108/Ergebnis_Zickzack.md). Ab AUSWEICH_NAH Feldern kommt der normale Angriffsbefehl: Ein Ziel ist
nur dann eins, wenn bis GEFAHR_FERN kein Schuetze steht, das letzte Stueck liegt also ausserhalb des Feuers."""

from selfaware.baukasten.ausweichen import Schussfeld

SKLAVE, PFERDEBOGEN = 71, 74
SCHLEUDER = 72                                   # B-129: Deckung fuer die Sklaven (Daniel 22:40: 25 Schleuderer)
SCHLEUDER_GOLD = 12                              # SOELDNER_GOLD in erstes_spiel.py (L63, Ascension)
DECKUNG_SOLL = 0                                 # B-129 Knopf deckung_soll: so viele Schleuderer gehen vor (0 = aus)
DECK_R = 10                                      # Startwert, UNGEMESSEN: Feind gilt als gedeckt, steht ein eigener Schleuderer so nah
SCHUSS_R = 12                                    # Startwert, UNGEMESSEN: Schleuderer greifen Feinde bis hier an
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
AUSWEICH_MAX = 8                                     # so viele Einzelbefehle je Feld kamen im Lauf zickzack2_g alle rechtzeitig (B-174, vorstoss.TRUPPS)
AUSWEICH_HALT = 5                                    # Felder vor dem Gebaeude endet der Zickzack: bis 4 Felder gilt der Sklave als am Gebaeude (Abfrage in schritt), dazu 1
AUSWEICH_RUNDE = 6                                   # Felder, die ein Sklave in einer Runde laeuft: 63 Takte Median (lage_20261108_155525_i1) / 12 Takte je Feld, aufgerundet
AUSWEICH_NAH = AUSWEICH_HALT + AUSWEICH_RUNDE                # ab hier der Angriffsbefehl, damit der Sklave nicht bis zur naechsten Runde am Halt wartet
AUSWEICH_TRUPP = 1000                                # Trupp beim Kern = AUSWEICH_TRUPP + Sklave; die Plaetze des Vorstosses haben die Nummern 1 bis 8
FERN = {22, 23, 70, 72, 74, 76}
NAH = {24, 25, 26, 27, 28, 55, 73, 75}
TUERME = {74, 75, 76, 77, 78}                    # Gebaeudetypen Wach-/Verteidigungs-/Geschuetz-/eckiger/runder Turm
GRUBE = 67
SPERRE_RUNDEN = 10   # Startwert: so lange waehlt der Brandtrupp ein aufgegebenes Gebaeude nicht neu (Wegfuehrung)
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


def gefaehrlich(ort, L, G, sp, schutz=()):
    """schutz (B-129, Daniel 19.10. 23:32 \"Bogenschuetzen vor und mit Sklaven abgefackelt\"): Orte eigener Deckungs-
    Schuetzen. Ein feindlicher Kaempfer, neben dem einer von ihnen steht (DECK_R), gilt als gedeckt - Tuerme und Gruben nicht."""
    for typ, p in feinde(L, sp):
        if schutz and any(schach(p, s) <= DECK_R for s in schutz):
            continue
        if typ in FERN and schach(ort, p) <= GEFAHR_FERN:
            return "Schuetze Typ %d in %d" % (typ, schach(ort, p))
        if typ in NAH and schach(ort, p) <= GEFAHR_NAH:
            return "Nahkaempfer Typ %d in %d" % (typ, schach(ort, p))
    for g in G.values():
        if g.get("besitzer") in (0, sp):
            continue
        if g["typ"] in TUERME and schach(ort, (g["x"], g["y"])) <= GEFAHR_FERN:
            return "Turm in %d" % schach(ort, (g["x"], g["y"]))
        # 11.11. (Daniel 00:10 "das einzige was verborgen ist sind holfallen und wo das pech ist", FAIRNESS F12): gegnerische
        # Fallgruben sind im Spiel verborgen - die Pruefung las sie aus der Gebaeudetabelle (Verstoss gegen R3), jetzt nicht mehr
    return None


class Brandtrupp:
    def __init__(self, sp, feuer, kern=None):
        """feuer(nr) -> fireDuration des Gebaeudes nr (0 = brennt nicht). kern = None ohne Zickzack, sonst der Kernweg (B-175)."""
        self.sp, self.feuer = sp, feuer
        self.kern = kern
        self.ausweichend = set()           # Sklaven, die gerade der Kern im Zickzack fuehrt
        self.schuss = Schussfeld(sp)       # B-178: ausgewichen wird nur, wenn auf den Sklaven geschossen werden kann
        self.halt = {}              # Sklave -> (Gebaeude, Punkt, an dem sein Zickzack endet)
        self.ziel = {}              # Sklave -> Gebaeude
        self.befohlen = {}          # Sklave -> Runde
        self.brennt = set()         # Gebaeude, die wir brennen sahen
        self.angezuendet = 0
        self.runde = 0
        self.schutz = []            # B-129: Orte der Deckungs-Schuetzen, setzt der Lenker je Runde
        self.weg = None             # B-182: gemeinsame Wegfuehrung (micro/wegfuehrung.py), setzt der Raid-Einsatz
        self.gesperrt = {}          # Gebaeude -> Runde, bis zu der es nach "gefahr"/"kein_weg" nicht wieder gewaehlt wird

    def einheiten(self, L):
        return {n for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] == SKLAVE and e.get("leben", 1) > 0}

    def moeglich(self, n, L, G):
        """True, wenn der Brandtrupp das Gebaeude n anzuenden wuerde. B-182: Der Kauf nach Wirkung fragt dieselbe Stelle - Reihe 5 (BierKoenig)
        traute die Rechnung den Sklaven gedeckte Gebaeude zu, die der Brandtrupp nie angreift: 224 Sklaven, 2 Gebaeude angezuendet."""
        g = G[n]
        if g.get("besitzer") in (0, self.sp) or g["typ"] not in WERT or n in self.brennt:
            return False
        if self.gesperrt.get(n, -1) > self.runde:
            return False
        return not gefaehrlich((g["x"], g["y"]), L, G, self.sp, self.schutz)

    def _ziele(self, L, G, ort, belegt):
        kand = [(WERT[G[n]["typ"]] / float(max(schach(ort, (G[n]["x"], G[n]["y"])), 1)), n)
                for n in G if n not in belegt and self.moeglich(n, L, G)]
        return [n for _, n in sorted(kand, reverse=True)]

    def schritt(self, L, G, befehl):
        self.runde += 1
        aus = []
        meine = self.einheiten(L)
        self.schuss.neue_runde(L, G)
        if self.kern is not None:
            self.kern.aufraeumen(meine)
        self.ausweichend &= meine
        for s in list(self.ziel):
            if s not in meine or self.ziel[s] not in G:
                self.ziel.pop(s, None)
                self._nicht_im_ausweichen(s, meine)
        # brennt ein Ziel, zieht der Sklave weiter (gemessen: es brennt allein ab). Gelesen wird nur, wenn der Sklave hoechstens
        # 4 Felder davor steht - jede Abfrage ist ein Weg durch den Kanal
        for s, nr in list(self.ziel.items()):
            if schach((L[s]["x"], L[s]["y"]), (G[nr]["x"], G[nr]["y"])) <= 4:
                f = self.feuer(nr)
                if f > 0:
                    self.brennt.add(nr)
                    self.angezuendet += 1
                    self.ziel.pop(s)
                    self._nicht_im_ausweichen(s, meine)
                    if self.weg is not None:
                        self.weg.loslassen(s)
                    aus.append("BRANDTRUPP: Sklave %d hat Gebaeude %d (Typ %d) angezuendet (Feuer %d) - weiter" % (
                        s, nr, G[nr]["typ"], f))
        if self.weg is not None:
            # B-182: was die Wegfuehrung in der Vorrunde meldete - Gefahr am Ziel, kein Weg, Ziel weg: ein anderes Gebaeude
            for s, nr in list(self.ziel.items()):
                st = self.weg.status(s)
                if st in ("gefahr", "kein_weg", "ziel_weg"):
                    self.gesperrt[nr] = self.runde + SPERRE_RUNDEN
                    self.ziel.pop(s)
                    self.weg.loslassen(s)
                    aus.append("BRANDTRUPP: Sklave %d gibt Gebaeude %d auf (%s)" % (s, nr, st))
        belegt = set(self.ziel.values())
        for s in sorted(meine):
            e = L[s]
            mit_weg = self.weg is not None
            feuer = not mit_weg and self.kern is not None and self.schuss.unter_feuer(s, e)
            if not mit_weg and s in self.ziel and s not in self.ausweichend and not feuer and self.runde - self.befohlen.get(s, -99) < NEU_ALLE:
                continue
            if s not in self.ziel:
                z = self._ziele(L, G, (e["x"], e["y"]), belegt)
                if not z:
                    continue
                self.ziel[s] = z[0]
                belegt.add(z[0])
                g = G[z[0]]
                aus.append("BRANDTRUPP: Sklave %d -> Gebaeude %d (Typ %d) bei (%d, %d), %d Felder" % (
                    s, z[0], g["typ"], g["x"], g["y"], schach((e["x"], e["y"]), (g["x"], g["y"]))))
            if mit_weg:
                # B-182 (Plan_Wegfuehrung.md): den Weg fuehrt die Wegfuehrung, jede Runde neu gegen die aktuelle Lage
                self.weg.fuehre(s, "gebaeude", self.ziel[s], "brandtrupp")
                continue
            if s in self.ausweichend or feuer or self.befohlen.get(s, -99) < self.runde - NEU_ALLE or e.get("zustand") in (0, 1):
                if not self._im_ausweichen(s, e, self.ziel[s], G, feuer):
                    self._angreifen(s, self.ziel[s], befehl)
                    self.befohlen[s] = self.runde
        return aus

    @property
    def im_ausweichen(self):
        return len(self.ausweichend)

    def _angreifen(self, s, nr, befehl):
        """Mit Kern geht auch der Angriff ueber den Kern: So fuehrt nur eine Stelle den Sklaven, und zwei Gruppenbefehle im selben Takt
        koennen nicht verschmelzen (S57). Nur was der Ring nicht nimmt, geht ans Modul."""
        b = {"angriff": {"einheiten": [s], "gebaeude": nr}}
        for r in self.kern.senden([b]) if self.kern is not None else [b]:
            befehl(r, 1.0, bis="ANGRIFF")

    def _nicht_im_ausweichen(self, s, meine):
        """Der Sklave hat kein Ziel mehr: Der Kern laesst ihn los, sonst liefe er zu einem Gebaeude, das schon brennt."""
        if s in self.ausweichend and s in meine:
            self.kern.freigeben([s])
        self.ausweichend.discard(s)
        self.halt.pop(s, None)

    def _im_ausweichen(self, s, e, nr, G, feuer):
        """True, wenn der Kern den Lauf dieses Sklaven im Zickzack fuehrt; sonst kommt der Angriffsbefehl, der den Zickzack im Kern beendet.
        Je Runde wird nur nachgesehen, ob der Sklave schon nah genug ist; geschickt wird beim neuen Ziel und danach alle NEU_ALLE Runden."""
        if self.kern is None:
            return False
        ort, ziel = (e["x"], e["y"]), (G[nr]["x"], G[nr]["y"])
        d = schach(ort, ziel)
        if feuer and d > AUSWEICH_NAH and (s in self.ausweichend or len(self.ausweichend) < AUSWEICH_MAX):
            alt = self.halt.get(s)
            neu = alt is None or alt[0] != nr
            if neu:
                alt = (nr, (ziel[0] + (ort[0] - ziel[0]) * AUSWEICH_HALT // d, ziel[1] + (ort[1] - ziel[1]) * AUSWEICH_HALT // d))
                self.halt[s] = alt
            if not neu and s in self.ausweichend and self.runde - self.befohlen.get(s, -99) < NEU_ALLE:
                return True
            if self.kern.ausweichen([s], alt[1], AUSWEICH_TRUPP + s):
                self.ausweichend.add(s)
                self.befohlen[s] = self.runde
                return True
        self.ausweichend.discard(s)
        self.halt.pop(s, None)
        return False

    def bericht(self):
        kern = "; " + self.kern.bericht() if self.kern is not None else ""
        return "Brandtrupp: %d Gebaeude angezuendet%s" % (self.angezuendet, kern)


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
        aus = self._abschuesse(L)
        meine = self.einheiten(L)
        sicher = [k for k in L if self.moeglich(k, L, G)]     # einmal je Runde: haengt nicht vom Reiter ab
        # B-182 Reihe 8: Jeden Reiter auf einen eigenen Arbeiter zu schicken senkte das Gedraenge (14 statt 72 und 81 % geteilte Jagden), aber
        # nicht die Abschuesse je 1.000 Reiter-Takte (0,15 und 0,27 statt 0,20 und 0,52) - zurueckgenommen, mehrere duerfen denselben jagen.
        for r in sorted(meine):
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
            if not sicher:
                continue
            entfernt = [(schach(o, (L[k]["x"], L[k]["y"])), k) for k in sicher]
            in_reichweite = [(-ARBEITER[L[k]["typ"]], d, k) for d, k in entfernt if d <= JAGD_R]
            # 17:41: nichts in Reichweite -> der naechste ungeschuetzte Arbeiter irgendwo (der Angriffsbefehl reitet hin)
            k = min(in_reichweite)[2] if in_reichweite else min(entfernt)[1]
            alt = self.befohlen.get(r)
            if alt is None or alt[:2] != ("jagd", k) or self.runde - alt[2] >= NEU_ALLE:
                befehl({"angriff": {"einheiten": [r], "ziel": k}}, 1.0, bis="ANGRIFF")
                self.befohlen[r] = ("jagd", k, self.runde)
                if alt is None or alt[:2] != ("jagd", k):
                    aus.append("REITERJAGD: Reiter %d jagt Arbeiter %d (Typ %d) in %d Feldern" % (
                        r, k, L[k]["typ"], schach(o, (L[k]["x"], L[k]["y"]))))
        return aus

    def moeglich(self, k, L, G):
        """True, wenn die Reiterjagd den Arbeiter k jagen wuerde (ohne Reichweite: ist keiner in JAGD_R, reitet sie zum naechsten). B-182: Der
        Kauf nach Wirkung fragt dieselbe Stelle."""
        a = L[k]
        if a["besitzer"] in (0, self.sp) or a["typ"] not in ARBEITER or a.get("leben", 1) <= 0:
            return False
        return not gefaehrlich((a["x"], a["y"]), L, G, self.sp)

    def _abschuesse(self, L):
        """Ein gejagtes Ziel, das nicht mehr lebt, zaehlt genau einmal; der Reiter ist danach frei. B-182: Jeder Erfolg kommt in die Mitschrift,
        die Eichung misst daran die Takte von der Jagd bis zum Erfolg."""
        aus = []
        for r, v in list(self.befohlen.items()):
            if v[0] == "jagd" and (v[1] not in L or L[v[1]].get("leben", 1) <= 0 or L[v[1]]["besitzer"] in (0, self.sp)):
                self.getoetet += 1
                self.befohlen.pop(r)
                aus.append("REITERJAGD: Reiter %d hat Arbeiter %d erledigt" % (r, v[1]))
        return aus

    def bericht(self):
        return "Reiterjagd: %d Arbeiter getoetet" % self.getoetet


class Deckung:
    """B-129 (Daniel 19.10. 23:32: "direkt geraidet - Bogenschuetzen vor, mit Sklaven abgefackelt; penetrant vorgestuermt, nie
    lockergelassen"; L147: seine 48 ungedeckten Sklaven kosteten Daniel bis Tick 22.000 nur 3 Plantagen, 3 Holzfaeller).
    Schleuderer (Typ 72, nicht im Heer des Feldzugs) gehen VOR die Sklaven: Front = das Ziel eines Sklaven, sonst das wertvollste
    feindliche Gebaeude (WERT je Weg von unserem Bergfried). Jeder Schleuderer greift den naechsten Feind bis SCHUSS_R an -
    Kaempfer zuerst, dann Arbeiter -, sonst laeuft er zur Front. Seine Orte gehen als Schutz an den Brandtrupp (gefaehrlich)."""
    def __init__(self, sp, heim):
        self.sp, self.heim = sp, tuple(heim)
        self.befohlen = {}
        self.runde = 0
        self.getoetet = 0

    def einheiten(self, L):
        return {n for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] == SCHLEUDER and e.get("leben", 1) > 0}

    def orte(self, L):
        return [(L[n]["x"], L[n]["y"]) for n in self.einheiten(L)]

    def front(self, G, brand):
        z = [G[nr] for nr in (brand.ziel.values() if brand else ()) if nr in G]
        if z:
            return (z[0]["x"], z[0]["y"])
        kand = [(WERT[g["typ"]] / float(max(schach(self.heim, (g["x"], g["y"])), 1)), (g["x"], g["y"]))
                for g in G.values() if g.get("besitzer") not in (0, self.sp) and g["typ"] in WERT and g["typ"] not in TUERME]
        return max(kand)[1] if kand else None

    def schritt(self, L, G, befehl, brand=None):
        self.runde += 1
        aus = []
        for r, v in list(self.befohlen.items()):
            if v[0] == "ziel" and (v[1] not in L or L[v[1]].get("leben", 1) <= 0 or L[v[1]]["besitzer"] in (0, self.sp)):
                self.getoetet += 1
                self.befohlen.pop(r)
        f = self.front(G, brand)
        for r in sorted(self.einheiten(L)):
            o = (L[r]["x"], L[r]["y"])
            kand = []
            for k, a in L.items():
                if a["besitzer"] in (0, self.sp) or a.get("leben", 1) <= 0:
                    continue
                d = schach(o, (a["x"], a["y"]))
                if d > SCHUSS_R:
                    continue
                rang = 0 if a["typ"] in FERN or a["typ"] in NAH else 1 if a["typ"] in ARBEITER else 2
                kand.append((rang, d, k))
            alt = self.befohlen.get(r)
            if kand:
                k = min(kand)[2]
                if alt is None or alt[:2] != ("ziel", k) or self.runde - alt[2] >= NEU_ALLE:
                    befehl({"angriff": {"einheiten": [r], "ziel": k}}, 1.0, bis="ANGRIFF")
                    self.befohlen[r] = ("ziel", k, self.runde)
                    if alt is None or alt[:2] != ("ziel", k):
                        aus.append("DECKUNG: Schleuderer %d greift Typ %d in %d Feldern an" % (r, L[k]["typ"], schach(o, (L[k]["x"], L[k]["y"]))))
            elif f is not None and schach(o, f) > 4:
                if alt is None or alt[0] != "front" or alt[1] != f or self.runde - alt[2] >= NEU_ALLE:
                    befehl({"angriff": {"einheiten": [r], "lauf": [f[0], f[1]]}}, 1.0, bis="ANGRIFF")
                    self.befohlen[r] = ("front", f, self.runde)
        return aus

    def bericht(self):
        return "Deckung: %d Feinde getoetet" % self.getoetet


def werbung(gold_frei, feuer, sklaven, reiter, schleuder=0):
    """[(typ, anzahl)] - erst Sklaven bis SKLAVEN_SOLL, dann Schleuderer bis DECKUNG_SOLL (B-129), dann Reiter bis REITER_SOLL; nur Gold ueber der Ruecklage und nur
    so viele, dass FEUER_MIN Bauern am Feuer bleiben."""
    aus, frei, f = [], int(gold_frei), int(feuer) - FEUER_MIN
    n = max(0, min(SKLAVEN_SOLL - sklaven, frei // SKLAVE_GOLD, f))
    if n:
        aus.append((SKLAVE, n))
        frei -= n * SKLAVE_GOLD
        f -= n
    d = max(0, min(DECKUNG_SOLL - schleuder, frei // SCHLEUDER_GOLD, f))
    if d:
        aus.append((SCHLEUDER, d))
        frei -= d * SCHLEUDER_GOLD
        f -= d
    m = max(0, min(REITER_SOLL - reiter, frei // PFERD_GOLD, f))
    if m:
        aus.append((PFERDEBOGEN, m))
    return aus
