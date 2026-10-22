# -*- coding: utf-8 -*-
"""Raids mit Sklaven und berittenen Bogenschuetzen (Daniel 19.10. 16:49 "ausserdem fehlen noch Raids mit Sklaven und
berittenen Bogenschuetzen"; 16:57 "gesteuerte berittene Bogenschuetzen, die ja im Reiten schiessen koennen, koennten sehr
pervers sein ... Sklaven waeren als Raid besonders am Anfang einer Partie richtig OP - kosten wenig, und wenn Feuer erkannt
werden kann, koenntest du so gut wie alles anzuenden ... billiger als Assassinen"; 17:13 "eine Waffenkammer sollte fast
immer hoeher sein"; 17:14 "das Ziel ist immer noch den gegnerischen Lord zu killen - wenn jemand sieht, dass er jemanden
eindeutig killen oder snipen kann, sollte er angreifen").

GEMESSEN 19.10. (werkzeug/raid_messen.py, Spielstand "Walltest 4", daten/raid_messung_20261019_17*.json):
  - Sklave (5 Gold, 6.000 Leben, L63) greift eine Holzfaellerhuette (60 Leben) an: nach ~165 Ticks brennt sie
    (fireDuration > 0, Verursacher = Spieler des Sklaven), nach ~485 Ticks ist sie weg - so schnell wie ein Speertraeger
    (12.500 Leben). Laeuft der Sklave nach dem Anzuenden weg, brennt sie ALLEIN ab (60 -> 52 -> 36 -> 20 -> 4 -> weg bei 489).
    Vier Nachbarn bis 3 Felder fingen kein Feuer (ein Fall).
  - Pferdebogen (75 Gold, 15.000 Leben) toetet einen Holzfaeller aus 12 Feldern mit dem ersten Pfeil (<= 44 Ticks).
    Ob er im Reiten schiesst: NICHT gemessen (Versuch gegen einen Speer im Spielstand mit Burg unbrauchbar).
  - Feuer lesen: Gebaeudedatensatz 0xF98520 + nr*0x32C, fireDuration bei +0x14+702 (short), Verursacher bei +0x14+734.

BRANDTRUPP (Sklaven): B-168 (22.10.) - Ziel und Weg mit Risikoabwaegung aus gefahrenschutz.py (siehe Klasse); brennt es,
zieht er sofort weiter. Bis 21.10. galt: das wertvollste ungefaehrliche Gebaeude (Wert je Weg), Gefahr nur am Ziel gesehen. Gefaehrlich = feindlicher Schuetze oder Turm
bis GEFAHR_FERN Felder, feindlicher Nahkaempfer/Assassine bis GEFAHR_NAH, feindliche Fallgrube bis GRUBE_R.
REITERJAGD (Pferdebogen): Nahkaempfer/Assassine naeher als FLUCHT_R -> 12 Felder weg von ihm; sonst den naechsten
ungeschuetzten Arbeiter bis JAGD_R angreifen (Holzfaeller zuerst - 1018j: liefernde Holzfaeller entschieden die Partie);
gibt es dort keinen, zum naechsten ungeschuetzten Arbeiter irgendwo reiten (19.10. 17:41, Daniel: "hier stehen bei Orange
Berittene - die sollten im besten Fall immer beim Gegner raiden und in Bewegung sein").
Werbung nur aus Gold ueber der Ruecklage und nur, solange mindestens FEUER_MIN Bauern am Feuer stehen.
STARTWERTE (nicht gemessen, je Partie mitgeschrieben): SKLAVEN_SOLL, REITER_SOLL, WERT.
Pruefung ohne Spiel: werkzeug/raids_pruefen.py."""
from parteien import freunde_von   # B-133: Freund/Feind aus den Mannschaften des Spiels (2v2)

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
from gebaeudeziele import angreifbar, zielwerte
WERT = zielwerte(WERT)
# Arbeiter-Einheiten (ablaufanalyse.EINHEIT): Holzfaeller zuerst
# 19.10. 17:58 (Punkt 8, Daniel 17:42 "immer ein Jackpot, das Pennerlager zu belagern, da an der Bauern-Spawnrate bestimmt
# wird, ob man noch Bauern hat, um zu rekrutieren"; 17:58 "ja mach Punkt 8"): Bauern (Typ 1, am Lagerfeuer) zuerst - jeder tote
# Bauer fehlt dem Gegner beim Anwerben und als Arbeiter
ARBEITER = {1: 12, 3: 10, 13: 6, 31: 5, 8: 4, 7: 4, 14: 3, 19: 3, 21: 3, 6: 2, 12: 2, 11: 2}
FEUER_NACHBAR_R = 3      # B-189: so nah stehende feindliche Gebaeude koennen mitbrennen (Startwert, UNGEMESSEN - 19.10. sprang
                         # eine Huette mit Nachbarn bis 3 Felder NICHT ueber, Daniels Bild 1018n zeigte Ueberspringen im Huettenhof)
FEUER_NACHBAR_ANTEIL = 0.5  # B-189: Anteil ihres Werts, der dem Ziel zugerechnet wird (Startwert, UNGEMESSEN)
ARBEITSPLATZ_DRIN = {4, 5, 10, 20, 21}   # B-178: Ochsenkarren, Eisenmine, Lager, Steinbruch, Steinhaufen - dort arbeiten sie am/im Gebaeude
ARBEITSPLATZ_R = 3       # B-178: Abstand zur Gebaeudemitte, bis zu dem ein Arbeiter als "am Arbeitsplatz" gilt (Startwert, UNGEMESSEN)
KITE_FELDER = 8         # B-188: so weit reitet ein beschossener Reiter weg, bevor er wieder angreift (Startwert, UNGEMESSEN)
IMMUN_RUNDEN = 3        # B-196: so viele Runden Beschuss ohne Lebensverlust -> Ziel gesperrt (Startwert, UNGEMESSEN)
SCHUETZE_WERT = 10      # B-175: feindlicher Schuetze am Boden als Reiterziel - wie ein Holzfaeller (Startwert, UNGEMESSEN)


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def feinde(L, sp):
    return [(e["typ"], (e["x"], e["y"])) for e in L.values() if e.get("besitzer") not in freunde_von(sp) and e.get("leben", 1) > 0]


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
        if g.get("besitzer") in freunde_von(sp):
            continue
        if g["typ"] in TUERME and schach(ort, (g["x"], g["y"])) <= GEFAHR_FERN:
            return "Turm in %d" % schach(ort, (g["x"], g["y"]))
        if g["typ"] == GRUBE and schach(ort, (g["x"], g["y"])) <= GRUBE_R:
            return "Fallgrube in %d" % schach(ort, (g["x"], g["y"]))
    return None


# B-150 (Daniel 21.10.2026 18:29 Bild: eigene Sklaven zuendeten eine Mine an, das Heer lief durch das Feuer; 19:45: "es muss
# auch berechnet werden, ob das Feuer bis dahin schon geloescht wurde oder das Gebaeude zerstoert oder das Feuer aus einem
# anderen Grund nicht mehr brennt"). Gemessen L177/L179: eine Plantage (Leben 100) brannte in ~500 Takten ab (~5 Takte je
# Lebenspunkt), ihr Boden brennt danach weiter; Sklave ~12 Takte je Feld (L80), Streitkolben aehnlich. Ein Ziel naeher als
# sein Feuer-Abstand (feldzug.FEUER_*_R) an der Strecke Heer -> Lord wird nur angezuendet, wenn das Feuer nach dieser
# Schaetzung samt NACHGLUT aus ist, bevor das Heer dort ankommt. Die eigentliche Reaktion bleibt beim Auge: der Feldzug
# rechnet seinen Weg jede Runde aus den Feuern, die wirklich brennen - ist eins frueher aus, geht es geradeaus weiter.
TAKTE_JE_LEBEN = 5          # Abbrennen (L177: Plantage 100 Leben -> ~500 Takte)
NACHGLUT = 600              # Bodenfeuer nach dem Abbrennen (L179: Boden brannte weiter) - Schaetzung, ungemessen
HEER_TAKTE_JE_FELD = 12     # L80 (Sklave); Streitkolben gleich angenommen - ungemessen


def brennt_noch_bei_ankunft(g, heerwege):
    """Schaetzung: brennt Gebaeude g (angezuendet jetzt), wenn das eigene Heer dort ankommt? heerwege: [(von, nach)] aus
    Feldzug._heerwege - wo das Heer steht (von == nach, Ankunft sofort) und wohin es befohlen ist."""
    import feldzug as FZ
    p = (g["x"], g["y"])
    r = FZ.FEUER_FELD_R if g.get("typ") in FZ.FELD_TYPEN else FZ.FEUER_GEBAEUDE_R
    aus_nach = max(g.get("leben", 0), 1) * TAKTE_JE_LEBEN + NACHGLUT
    return any(FZ._abstand_strecke(p, von, nach) <= r and schach(von, p) * HEER_TAKTE_JE_FELD < aus_nach
               for von, nach in heerwege or ())


def _lage_fuer(sp, L, G, raten=None, ohne=(), wegkarte=None):
    """B-168: Gefahrenlage aus dem Lagebild, wenn der Lenker keine mitgibt (Pruefungen); ohne = Einheiten, die nicht zaehlen
    (gedeckte Schuetzen, B-129)."""
    import gefecht
    import gefahrenschutz as GS
    L_ = {n: e for n, e in L.items() if n not in ohne} if ohne else L
    return GS.Lage(L_, G, lambda b: b not in freunde_von(sp), gefecht.FERN_REICH, raten=raten, wegkarte=wegkarte)


def _nahkampf_bei(p, L, sp):
    """Feindlicher Nahkaempfer/Assassine bis GEFAHR_NAH an p - die Gefahrenkarte zaehlt nur Schuetzen (22.10.: Sklaven starben
    beim Anzuenden neben Streitkolben-Gruppen)."""
    return any(typ in NAH and schach(p, q) <= GEFAHR_NAH for typ, q in feinde(L, sp))


def _rueckzug(lage, o):
    """Naechstes Feld ohne Beschuss (kleinste Kosten der Wegsuche ab o) - wer kein vertretbares Ziel hat und im Feuer steht."""
    import numpy as np
    _, kum = lage.suche(o)
    sicher = (lage.s <= 1e-9) & np.isfinite(kum)
    if not sicher.any():
        return None
    k = np.where(sicher, kum, np.inf)
    i = int(k.argmin())
    return (i // lage.n, i % lage.n)


class Brandtrupp:
    """B-168 (Daniel 22.10. 08:09 "sie muessen ausholen und den richtigen Pfad zum Ziel finden und auf dem Weg noch moegliche
    andere Dinge mitnehmen"; gemessen: 28 von 38 Sklaven starben, unterwegs - gefahrenschutz.py): jeder Sklave nimmt das Ziel mit
    dem besten Rang aus gefahrenschutz.bewerte (Wert x (1 - P(Tod)) / Takte; erwarteter Verlust >= Leben = nie), laeuft die
    Wegkette mit dem wenigsten Beschuss und greift erst an der Ankunft an. Neu gerankt wird, sobald er REPLAN_FELDER weiter ist -
    liegt dann ein anderes Ziel besser (er kommt gerade daran vorbei), nimmt er es mit. Ohne vertretbares Ziel im Beschuss: Rueckzug
    auf das naechste sichere Feld."""
    REPLAN_FELDER = 5            # neu ranken, wenn der Sklave so weit gelaufen ist (eine Suche ~60 ms, gemessen 22.10.)
    ANGRIFF_R = 4                # so nah an der Ankunft greift er an (wie die Wegkette von logik.lua: Mehrheit bis 4 Felder)

    def __init__(self, sp, feuer, raten=None):
        """feuer(nr) -> fireDuration des Gebaeudes nr (0 = brennt nicht); raten: fuer Pruefungen (sonst die Datei)."""
        self.sp, self.feuer, self.raten = sp, feuer, raten
        self.ziel = {}              # Sklave -> Gebaeude
        self.plan = {}              # Sklave -> {"an", "ort" (wo geplant), "art" lauf/angriff, "runde"}
        self.brennt = set()         # Gebaeude, die wir brennen sahen
        self.angezuendet = 0
        self.runde = 0
        self.schutz = []            # B-129: Orte der Deckungs-Schuetzen, setzt der Lenker je Runde
        self.heerwege = []          # B-150: [(von, nach)] des eigenen Heeres (Feldzug._heerwege), setzt der Lenker je Runde
        self.abgelehnt = 0          # Ziele, die nur wegen des Risikos nicht genommen wurden (letzte Planung)
        self._rang = []
        self.rueckzug = {}          # Sklave -> (Feld, Runde) des letzten Rueckzugsbefehls

    def einheiten(self, L):
        return {n for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] == SKLAVE and e.get("leben", 1) > 0}

    def _gedeckt(self, L):
        """B-129: feindliche Kaempfer, neben denen ein eigener Deckungs-Schuetze steht (DECK_R) - zaehlen nicht als Gefahr."""
        if not self.schutz:
            return set()
        return {n for n, e in L.items() if e.get("besitzer") not in freunde_von(self.sp)
                and any(schach((e["x"], e["y"]), q) <= DECK_R for q in self.schutz)}

    def _kandidaten(self, L, G, belegt):
        kand = []
        for n, g in G.items():
            if g.get("besitzer") in freunde_von(self.sp) or g["typ"] not in WERT or n in belegt or n in self.brennt:
                continue
            p = (g["x"], g["y"])
            if any(h.get("besitzer") not in freunde_von(self.sp) and h["typ"] == GRUBE and schach(p, (h["x"], h["y"])) <= GRUBE_R
                   for h in G.values()):
                continue                                      # Fallgrube: toetet sofort, steht in keiner Schadenskarte
            if _nahkampf_bei(p, L, self.sp):
                continue
            if brennt_noch_bei_ankunft(g, getattr(self, '_wege', self.heerwege)):
                continue                                      # B-150: wuerde auf dem eigenen Heerweg noch brennen
            # B-189 (Daniel 18:14 "ein Feuer kann ueberspringen - ein perfekt platziertes Feuer kann eine komplette Wirtschaft
            # abfackeln"): feindliche Nachbargebaeude bis FEUER_NACHBAR_R zaehlen mit FEUER_NACHBAR_ANTEIL ihres Werts dazu
            nachbarn = sum(WERT.get(h["typ"], 1) for hn, h in G.items() if hn != n and h.get("besitzer") not in freunde_von(self.sp)
                           and angreifbar(h) and schach(p, (h["x"], h["y"])) <= FEUER_NACHBAR_R)
            kand.append((WERT[g["typ"]] + FEUER_NACHBAR_ANTEIL * nachbarn, p, n))
        return kand

    def _ziele(self, L, G, ort, belegt, lage=None, leben=6000):
        """Gebaeude nach Rang (bester zuerst) - nur die mit vertretbarem Risiko."""
        if lage is None or self.schutz:
            lage = _lage_fuer(self.sp, L, G, self.raten, ohne=self._gedeckt(L),
                             wegkarte=getattr(lage, "wegkarte", None))
        import gefahrenschutz as GS
        kand = self._kandidaten(L, G, belegt)
        r = GS.bewerte(lage, ort, SKLAVE, leben, kand)
        if getattr(lage, "links", None) is not None:
            r = []
            for wert, zielort, nr in kand:
                p = lage.plan(ort, zielort, SKLAVE, leben, gebaeude=nr)
                if p is not None and p["p_tod"] <= GS.RISIKO_MAX:
                    r.append((wert*(1-p["p_tod"])/max(1,p["takte"]+GS.VERWEILEN[SKLAVE]),nr,p))
            r.sort(key=lambda v:-v[0])
        self.abgelehnt = len(kand) - len(r)
        self._rang = r
        return [(k, p) for _, k, p in r]

    def _alle_heerwege(self, L):
        """B-183 (Daniel 22.10. 17:55/17:57: das Heer verbrennt in Haeusern, die eigene oder Partner-Sklaven anzuendeten): zu den
        Heerwegen des eigenen Feldzugs die Kaempfer ALLER Verbuendeten - wo sie stehen und wohin sie laufen (Lagebild laufx/y)."""
        from feldzug import HEER
        wege = list(self.heerwege or ())
        for e in L.values():
            if (e.get("besitzer") in freunde_von(self.sp) and e.get("besitzer") not in (0, self.sp) and e.get("typ") in HEER
                    and e.get("leben", 1) > 0):
                o = (e["x"], e["y"])
                ziel = (e["laufx"], e["laufy"]) if e.get("laufx", 0) > 0 and e.get("laufy", 0) > 0 else o
                wege.append((o, ziel))
        return wege

    def schritt(self, L, G, befehl, lage=None):
        import gefahrenschutz as GS
        self.runde += 1
        aus = []
        meine = self.einheiten(L)
        self._wege = self._alle_heerwege(L)
        if lage is None or self.schutz:
            lage = _lage_fuer(self.sp, L, G, self.raten, ohne=self._gedeckt(L), wegkarte=getattr(lage, "wegkarte", None))
        for s in list(self.ziel):
            if s not in meine or self.ziel[s] not in G or not angreifbar(G[self.ziel[s]]):
                self.ziel.pop(s, None)
                self.plan.pop(s, None)
        # brennt ein Ziel, zieht der Sklave weiter (gemessen: es brennt allein ab). Gelesen wird nur, wenn der Sklave hoechstens
        # 4 Felder davor steht - jede Abfrage ist ein Weg durch den Kanal
        for s, nr in list(self.ziel.items()):
            # B-189 (Daniel 22.10. 18:13: "nachdem ein Sklave ein Ziel bekommen hat, hat er einfach nur gewartet"): auch wer gerade
            # angreift (Zustand 106/107) wird geprueft - an groesseren Gebaeuden steht er weiter als 4 Felder von der Mitte
            if schach((L[s]["x"], L[s]["y"]), (G[nr]["x"], G[nr]["y"])) <= 4 or L[s].get("zustand") in (106, 107):
                f = self.feuer(nr)
                if f > 0:
                    self.brennt.add(nr)
                    self.angezuendet += 1
                    self.ziel.pop(s)
                    self.plan.pop(s, None)
                    aus.append("BRANDTRUPP: Sklave %d hat Gebaeude %d (Typ %d) angezuendet (Feuer %d) - weiter" % (
                        s, nr, G[nr]["typ"], f))
        # B-150: ein noch nicht brennendes Ziel wird jede Runde gegen die Heerwege geprueft; ohne neues Ziel bleibt der Sklave stehen
        halt = set()
        for s, nr in list(self.ziel.items()):
            if nr not in self.brennt and brennt_noch_bei_ankunft(G[nr], getattr(self, '_wege', self.heerwege)):
                self.ziel.pop(s)
                self.plan.pop(s, None)
                halt.add(s)
                aus.append("BRANDTRUPP: Sklave %d laesst Gebaeude %d - es liegt jetzt am eigenen Heer" % (s, nr))
        for s in sorted(meine):
            e = L[s]
            o = (e["x"], e["y"])
            pl = self.plan.get(s)
            neu_ranken = s not in self.ziel or pl is None or schach(o, pl["ort"]) >= self.REPLAN_FELDER or e.get("zustand") in (0, 1)
            if neu_ranken:
                belegt = {z for k, z in self.ziel.items() if k != s}
                r = self._ziele(L, G, o, belegt, lage, e.get("leben", 6000))
                alt_z = self.ziel.get(s)
                if not r and alt_z is not None and alt_z in G and alt_z not in self.brennt:
                    # B-171 (2v2 22.10. 17:48: Sklave 345 liess 8 Felder vor der Huette das Ziel fallen und starb auf dem Rueckweg
                    # durch denselben Beschuss): ohne vertretbares NEUES Ziel bleibt das alte, solange der Rest des Wegs weniger
                    # Verlust erwarten laesst als der Rueckzug
                    p_c = lage.plan(o, (G[alt_z]["x"], G[alt_z]["y"]), SKLAVE, e.get("leben", 6000))
                    q_r = _rueckzug(lage, o) if lage.schaden(o) > 0 else None
                    p_r = lage.plan(o, q_r, SKLAVE, e.get("leben", 6000)) if q_r is not None and q_r != o else None
                    if p_c is not None and p_r is not None and p_c["verlust"] <= p_r["verlust"]:
                        r = [(alt_z, p_c)]
                        self._rang = [(0.0, alt_z, p_c)]
                        aus.append("BRANDTRUPP: Sklave %d bleibt bei Gebaeude %d - Rest %d Takte, erwarteter Verlust %d, Rueckzug "
                                   "%d" % (s, alt_z, p_c["takte"], p_c["verlust"], p_r["verlust"]))
                if not r:
                    alt = self.ziel.pop(s, None)
                    self.plan.pop(s, None)
                    if alt is not None:
                        aus.append("BRANDTRUPP: Sklave %d laesst Gebaeude %d - kein Ziel mit vertretbarem Risiko (%d abgelehnt)" % (
                            s, alt, self.abgelehnt))
                    if s in halt:
                        befehl({"angriff": {"einheiten": [s], "lauf": [o[0], o[1]]}}, 1.0, bis="ANGRIFF")
                    rz = self.rueckzug.get(s)
                    if lage.schaden(o) > 0 and (rz is None or self.runde - rz[1] >= NEU_ALLE):
                        q = _rueckzug(lage, o)
                        if q is not None and q != o:
                            p_r = lage.plan(o, q, SKLAVE, e.get("leben", 6000))
                            if p_r:
                                befehl(GS.lauf_befehl(lage, s, p_r), 1.0, bis="ANGRIFF")
                                self.rueckzug[s] = (q, self.runde)
                                aus.append("BRANDTRUPP: Sklave %d zieht sich aus dem Beschuss nach %s zurueck" % (s, q))
                    continue
                self.rueckzug.pop(s, None)
                alt = self.ziel.get(s)
                nr, p, wahl_art = GS.waehle(self._rang, alt)
                if alt != nr:
                    g = G[nr]
                    art = {"mitnehmen": "nimmt unterwegs mit", "wechsel": "wechselt zu"}.get(wahl_art, "->")
                    aus.append("BRANDTRUPP: Sklave %d %s Gebaeude %d (Typ %d) bei (%d, %d): %d Takte, erwarteter Verlust %d von %d "
                               "Leben (P(Tod) %.2f)%s" % (s, art, nr, g["typ"], g["x"], g["y"], p["takte"], p["verlust"],
                                                          e.get("leben", 0), p["p_tod"], " statt %d" % alt if alt is not None else ""))
                self.ziel[s] = nr
                if alt != nr or pl is None:
                    pl = self.plan[s] = {"an": p["an"], "ort": o, "art": None, "runde": -99, "weg": p}
                else:
                    pl.update({"an": p["an"], "ort": o, "weg": p})
            # Befehl: an der Ankunft angreifen, sonst Wegkette; neu senden bei neuem Ziel, im Stillstand oder alle NEU_ALLE Runden
            an = pl["an"]
            nah = schach(o, an) <= self.ANGRIFF_R or schach(o, (G[self.ziel[s]]["x"], G[self.ziel[s]]["y"])) <= self.ANGRIFF_R
            if getattr(lage, "links", None) is not None:
                # Geometrische Naehe ueber eine Klippe hinweg loest keinen Angriff aus.
                rest = lage.plan(o, (G[self.ziel[s]]["x"], G[self.ziel[s]]["y"]), SKLAVE,
                                 e.get("leben",6000), gebaeude=self.ziel[s])
                nah = rest is not None and len(rest["weg"]) <= self.ANGRIFF_R+1
                if rest is not None:
                    pl["weg"] = rest
            art = "angriff" if nah else "lauf"
            if art != pl["art"] or self.runde - pl["runde"] >= NEU_ALLE or e.get("zustand") in (0, 1):
                if art == "angriff":
                    befehl({"angriff": {"einheiten": [s], "gebaeude": self.ziel[s]}}, 1.0, bis="ANGRIFF")
                else:
                    befehl(GS.lauf_befehl(lage, s, pl["weg"]), 1.0, bis="ANGRIFF")
                pl["art"], pl["runde"] = art, self.runde
        return aus

    def bericht(self):
        return "Brandtrupp: %d Gebaeude angezuendet" % self.angezuendet


def reichweitenposition(lage, ort, ziel, eigene_reichweite, feind_reichweite, leben=15000):
    """Nur bei echtem Reichweitenvorteil: ausserhalb Feindreichweite, innerhalb eigener Schussweite.
    Vier Felder Puffer, eigene obere Modellgrenze um fuenf Felder verkuerzt.
    Jeder Punkt wird gegen ALLE Schuetzen der Lage und gegen den wirklichen Weg geprueft.
    """
    unten,oben=max(feind_reichweite+4, eigene_reichweite-12 if feind_reichweite == 0 else 0),eigene_reichweite-5
    if feind_reichweite<0 or unten>=oben:return None
    if feind_reichweite == 0 and schach(ort,ziel)<=oben and lage.schaden(ort)<=0:
        return {'an':tuple(ort),'weg':[tuple(ort)],'takte':0,'verlust':0,'p_tod':0}
    if unten<=schach(ort,ziel)<=oben and lage.schaden(ort)<=0:
        return {'an':tuple(ort),'weg':[tuple(ort)],'takte':0,'verlust':0,'p_tod':0}
    radius=min(oben-1,unten+2)
    dx,dy=ort[0]-ziel[0],ort[1]-ziel[1];norm=max(abs(dx),abs(dy),1)
    kandidaten={(ziel[0]+radius*dx//norm,ziel[1]+radius*dy//norm)}
    kandidaten.update((ziel[0]+radius*x,ziel[1]+radius*y) for x,y in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)))
    plaene=[]
    for q in kandidaten:
        if not lage.drin(q) or lage.schaden(q)>0:continue
        p=lage.plan(ort,q,PFERDEBOGEN,leben)
        if p and tuple(p['an'])==q and unten<=schach(q,ziel)<=oben and p['p_tod']<1:
            plaene.append(p)
    return min(plaene,key=lambda p:(p['verlust'],p['takte'],tuple(p['an'])),default=None)


class Reiterjagd:
    """B-168 (Daniel 22.10. 08:08 "warum macht einer Berittene, wenn diese eh nicht genutzt werden? er soll sie nutzen";
    gemessen: der Reiter von Spieler 2 stand 11.700 Takte auf einem Feld - ein Angriffsbefehl auf 166-215 Felder bewegt ihn nicht;
    der von Spieler 1 fand nie ein Ziel ohne Schuetzen bis 20 Felder): Nahkaempfer naeher als FLUCHT_R -> ausweichen; sonst der
    Arbeiter mit dem besten Rang aus gefahrenschutz.bewerte (Wert x (1 - P(Tod)) / Takte, nur vertretbares Risiko). Bis JAGD_R
    Felder: Angriffsbefehl; weiter weg: Wegkette mit dem wenigsten Beschuss zu ihm. Neu gerankt wird jede Runde (die Arbeiter
    laufen) - kommt der Reiter an einem anderen vorbei, nimmt er ihn mit. Ohne vertretbares Ziel im Beschuss: Rueckzug."""
    KANDIDATEN = 40              # so viele naechste Arbeiter werden je Reiter bewertet (je Weg eine Rueckverfolgung)

    def __init__(self, sp, raten=None):
        self.sp, self.raten = sp, raten
        self.befohlen = {}          # Reiter -> (Art, Ziel, Runde)
        self.getoetet = 0
        self.runde = 0
        self.wirkung = {}           # B-196: (Reiter, Ziel) -> (Leben des Ziels, Runde) seit dem letzten Lebensverlust unter Beschuss
        self.immun = {}             # B-196: Ziel -> Feld, auf dem ihm unser Beschuss nichts anhaben konnte

    def einheiten(self, L):
        return {n for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] == PFERDEBOGEN and e.get("leben", 1) > 0}

    def _wirkung_messen(self, r, L, aus):
        """B-196 (gemessen 22.10., Laeufe 18:08/18:27: Reiter 646 schoss 21.000 Takte auf Arbeiter 516 (Typ 31) in seinem Gebaeude,
        Reiter 661 2.000 Takte auf 721 - beide blieben bei 2.500 Leben; die Feld-Regel aus B-178 erkannte das nicht): wer schiesst
        (Zustand 4) und dessen Ziel IMMUN_RUNDEN Runden lang kein Leben verliert, sperrt das Ziel, solange es auf diesem Feld
        steht - gelernt aus der Wirkung, nicht aus einer Liste von Typen."""
        e = L[r]
        z = e.get("zieleinheit")
        if e.get("zustand") != 4 or z not in L or L[z].get("besitzer") in freunde_von(self.sp):
            return
        w = self.wirkung.get((r, z))
        if w is None or L[z].get("leben", 0) < w[0]:
            self.wirkung[(r, z)] = (L[z].get("leben", 0), self.runde)
        elif self.runde - w[1] >= IMMUN_RUNDEN:
            self.immun[z] = (L[z]["x"], L[z]["y"])
            self.wirkung.pop((r, z), None)
            self.befohlen.pop(r, None)
            aus.append("REITERJAGD: Ziel %d (Typ %d) bei %s verliert unter Beschuss von Reiter %d seit %d Runden kein Leben (%d) - "
                       "gesperrt, solange es dort steht" % (z, L[z]["typ"], self.immun[z], r, self.runde - w[1], w[0]))

    def schritt(self, L, G, befehl, lage=None):
        import gefahrenschutz as GS
        self.runde += 1
        aus = []
        self._abschuesse(L)
        reiter = sorted(self.einheiten(L))
        if not reiter:
            return aus
        if lage is None:
            lage = _lage_fuer(self.sp, L, G, self.raten)
        # B-175/B-178 (Daniel 22.10. 17:52/17:54: Reiter zielten auf eine Steinablage und eine Eisenmine): nur Arbeiter im
        # FREIEN - wer auf einem Gebaeudefeld steht (Steinmetz am Haufen, Bergmann an der Mine), macht den Angriff zum
        # Gebaeudeangriff. Dazu feindliche Schuetzen am Boden (kein Gebaeude, nicht auf der Mauer) - wer uns beschiesst, wird
        # bekaempft statt ignoriert
        bau = getattr(lage, "bau", None)
        # (Lauf 18:08 gemessen: die Reiter hatten nie ein Gebaeude als Ziel - sie schossen auf Arbeiter, die an/in ihrem Arbeitsplatz
        # standen, die Pfeile trafen sichtbar Mine und Steinablage; Daniel 18:15): auch wer bis 1 Feld an Mine, Steinbruch, Lager oder
        # Ochsenkarren steht, ist kein Reiterziel
        arbeitsplatz = [(g["x"], g["y"]) for g in G.values() if g.get("typ") in ARBEITSPLATZ_DRIN]
        im_freien = lambda a: ((bau is None or not lage.drin((a["x"], a["y"])) or int(bau[a["x"], a["y"]]) == 0)
                               and not any(schach((a["x"], a["y"]), q) <= ARBEITSPLATZ_R for q in arbeitsplatz))
        import gefecht
        for r in reiter:
            self._wirkung_messen(r, L, aus)
        arbeiter = [(k, a) for k, a in L.items() if a["besitzer"] not in freunde_von(self.sp) and a.get("leben", 1) > 0
                    and self.immun.get(k) != (a["x"], a["y"])
                    and ((a["typ"] in ARBEITER and im_freien(a))
                         or (a["typ"] in gefecht.FERN_REICH and im_freien(a) and a["typ"] != PFERDEBOGEN))]
        arbeiter_nr = {k for k, _ in arbeiter}
        self._ziel_nr = arbeiter_nr
        for r in reiter:
            e = L[r]
            o = (e["x"], e["y"])
            alt = self.befohlen.get(r)
            # Nicht erst auf den ersten Treffer warten: kuerzer reichende Feinde aktiv auf Abstand halten.
            nahe_fern=sorted((schach(o,(f['x'],f['y'])),k,f) for k,f in L.items()
                             if f.get('besitzer') not in freunde_von(self.sp) and f.get('leben',1)>0
                             and 0<gefecht.FERN_REICH.get(f.get('typ'),0)<gefecht.FERN_REICH[PFERDEBOGEN]
                             and schach(o,(f['x'],f['y']))<gefecht.FERN_REICH[f['typ']]+4)
            if nahe_fern:
                d,k,f=nahe_fern[0]
                p_ab=reichweitenposition(lage,o,(f['x'],f['y']),gefecht.FERN_REICH[PFERDEBOGEN],gefecht.FERN_REICH[f['typ']],e.get('leben',15000))
                if p_ab and tuple(p_ab['an'])!=o:
                    ziel_ab=tuple(p_ab['an'])
                    if alt is None or alt[:2]!=('abstand',ziel_ab) or self.runde-alt[2]>=NEU_ALLE:
                        befehl(GS.lauf_befehl(lage,r,p_ab),1.0,bis='ANGRIFF')
                        self.befohlen[r]=('abstand',ziel_ab,self.runde)
                        aus.append('REITER REICHWEITENVORTEIL: %d weicht Typ %d vor Beschuss aus, Abstand %d, Ziel %s'%(r,f['typ'],d,ziel_ab))
                    continue
                # Kein sicherer Punkt zum Schiessen: niemals in die normale Jagd durchfallen.
                q = _rueckzug(lage, o)
                p_r = lage.plan(o, q, PFERDEBOGEN, e.get('leben',15000)) if q is not None and q != o else None
                if p_r:
                    befehl(GS.lauf_befehl(lage,r,p_r),1.0,bis='ANGRIFF')
                    self.befohlen[r]=('rueckzug',tuple(p_r['an']),self.runde)
                    aus.append('REITER SICHERHEIT: %d ohne sicheren Schusspunkt - Rueckzug statt weiterer Jagd'%r)
                else:
                    befehl({'angriff':{'einheiten':[r],'lauf':list(o)}},1.0,bis='ANGRIFF')
                    self.befohlen[r]=('halt',o,self.runde)
                continue
            # B-188/B-201 (Daniel 22.10. 18:12 "sie muessen ausweichen, immerhin sind sie die einzige Einheit, die im Lauf auch
            # schiessen kann"; 18:45 "stehen beim Angriff, statt zu patrouillieren", "gehen in den Nahkampf"; gemessen 18:40:
            # 1.325 von 2.800 Reiter-Proben standen schiessend still): wer gerade beschossen wird, reitet KITE_FELDER vom Schuetzen
            # weg und greift in der naechsten Runde wieder an - angreifen, wegreiten, angreifen
            auf_mich = sorted((schach(o, (f["x"], f["y"])), k) for k, f in L.items()
                              if f.get("besitzer") not in freunde_von(self.sp) and f.get("zieleinheit") == r
                              and f.get("typ") in gefecht.FERN_REICH and f.get("leben", 1) > 0)
            if auf_mich and (alt is None or alt[0] != "kite" or self.runde - alt[2] >= 2):
                f = L[auf_mich[0][1]]
                dx, dy = o[0] - f["x"], o[1] - f["y"]
                n = max(abs(dx), abs(dy), 1)
                ziel = (o[0] + KITE_FELDER * dx // n, o[1] + KITE_FELDER * dy // n)
                p_flucht = lage.plan(o, ziel, PFERDEBOGEN, e.get("leben",15000))
                if p_flucht is None:
                    continue
                befehl(GS.lauf_befehl(lage, r, p_flucht), 1.0, bis="ANGRIFF")
                self.befohlen[r] = ("kite", ziel, self.runde)
                aus.append("REITERJAGD: Reiter %d wird von %d (Typ %d, %d Felder) beschossen - reitet nach %s, dann wieder Angriff" % (
                    r, auf_mich[0][1], f["typ"], auf_mich[0][0], ziel))
                continue
            if alt is not None and alt[0] == "kite" and self.runde - alt[2] < 1:
                continue
            # Flucht vor Nahkaempfern/Assassinen
            nah = min(((schach(o, (f["x"], f["y"])), k) for k, f in L.items()
                       if f["besitzer"] not in freunde_von(self.sp) and f["typ"] in NAH and f.get("leben", 1) > 0), default=None)
            if nah and nah[0] < FLUCHT_R:
                f = L[nah[1]]
                dx, dy = o[0] - f["x"], o[1] - f["y"]
                n = max(abs(dx), abs(dy), 1)
                ziel = (o[0] + 12 * dx // n, o[1] + 12 * dy // n)
                if alt is None or alt[0] != "flucht" or self.runde - alt[2] >= NEU_ALLE:
                    p_flucht = lage.plan(o, ziel, PFERDEBOGEN, e.get("leben",15000))
                    if p_flucht is None:
                        continue
                    befehl(GS.lauf_befehl(lage, r, p_flucht), 1.0, bis="ANGRIFF")
                    self.befohlen[r] = ("flucht", ziel, self.runde)
                    aus.append("REITERJAGD: Reiter %d weicht Typ %d in %d Feldern aus -> %s" % (r, f["typ"], nah[0], ziel))
                continue
            # (22.10. 2v2 082947: auf dem langen Anritt wechselte der Reiter jede Runde zwischen gleich fernen Holzfaellern, jede
            # Wahl schickte eine neue Wegkette) - unterwegs nur alle NEU_ALLE Runden neu ranken, ausser ein Arbeiter ist schon in
            # Jagdweite (den nimmt er mit), das Ziel ist weg oder der Reiter steht
            if alt is not None and alt[0] == "anritt" and alt[1] in arbeiter_nr \
                    and self.runde - alt[2] < NEU_ALLE and e.get("zustand") not in (0, 1) \
                    and not any(schach(o, (a["x"], a["y"])) <= JAGD_R for _, a in arbeiter):
                continue
            naechste = sorted(arbeiter, key=lambda ka: schach(o, (ka[1]["x"], ka[1]["y"])))[:self.KANDIDATEN]
            # (22.10. 2v2 082947: "RAIDS FEHLER KeyError(22)" - das Spiel vergibt Einheitennummern neu, die Nummer des Ziels
            # gehoerte jetzt einem Bogenschuetzen) nur ein Ziel, das noch ein feindlicher Arbeiter ist
            if alt is not None and alt[0] in ("jagd", "anritt") and alt[1] in arbeiter_nr and all(k_ != alt[1] for k_, _ in naechste):
                naechste.append((alt[1], L[alt[1]]))         # das jetzige Ziel bleibt im Vergleich, auch wenn es fern ist
            zielpunkte=[]
            for k_a,a in naechste:
                punkt=(a['x'],a['y']);reich=gefecht.FERN_REICH.get(a['typ'],0)
                if 0<=reich<gefecht.FERN_REICH[PFERDEBOGEN]:
                    p_a=reichweitenposition(lage,o,punkt,gefecht.FERN_REICH[PFERDEBOGEN],reich,e.get('leben',15000))
                    if p_a is None:continue
                    punkt=tuple(p_a['an'])
                zielpunkte.append((ARBEITER.get(a['typ'],SCHUETZE_WERT),punkt,k_a))
            rang=GS.bewerte(lage,o,PFERDEBOGEN,e.get('leben',15000),zielpunkte)
            rang.sort(key=lambda v:(-v[0],schach(o,(L[v[1]]['x'],L[v[1]]['y']))))
            if not rang:
                if lage.schaden(o) > 0 and (alt is None or alt[0] != "rueckzug" or self.runde - alt[2] >= NEU_ALLE):
                    q = _rueckzug(lage, o)
                    p_r = lage.plan(o, q, PFERDEBOGEN, e.get("leben", 15000)) if q is not None and q != o else None
                    if p_r:
                        befehl(GS.lauf_befehl(lage, r, p_r), 1.0, bis="ANGRIFF")
                        self.befohlen[r] = ("rueckzug", q, self.runde)
                        aus.append("REITERJAGD: Reiter %d - kein Arbeiter mit vertretbarem Risiko, Rueckzug nach %s" % (r, q))
                continue
            k, p, _ = GS.waehle(rang, alt[1] if alt is not None and alt[0] in ("jagd", "anritt") else None)
            d = schach(o, (L[k]["x"], L[k]["y"]))
            feind_reich=gefecht.FERN_REICH.get(L[k]['typ'],0)
            schussgrenze=JAGD_R
            if 0<=feind_reich<gefecht.FERN_REICH[PFERDEBOGEN]:
                p_ab=reichweitenposition(lage,o,(L[k]['x'],L[k]['y']),gefecht.FERN_REICH[PFERDEBOGEN],feind_reich,e.get('leben',15000))
                if p_ab is None:
                    continue  # Kein sicherer Schusspunkt: keinen Angriff in den Feind hinein ausloesen.
                p=p_ab
                schussgrenze=gefecht.FERN_REICH[PFERDEBOGEN]-5
            art = "jagd" if d <= schussgrenze and lage.schaden(o)<=0 else "anritt"
            if alt is None or alt[:2] != (art, k) or self.runde - alt[2] >= NEU_ALLE or e.get("zustand") in (0, 1):
                if art == "jagd":
                    befehl({"angriff": {"einheiten": [r], "ziel": k}}, 1.0, bis="ANGRIFF")
                else:
                    befehl(GS.lauf_befehl(lage, r, p), 1.0, bis="ANGRIFF")
                self.befohlen[r] = (art, k, self.runde)
                if alt is None or alt[1] != k:
                    aus.append("REITERJAGD: Reiter %d %s Arbeiter %d (Typ %d) in %d Feldern, %d Takte, erwarteter Verlust %d von %d (P(Tod) %.2f)" % (
                        r, "jagt" if art == "jagd" else "reitet ueber %d Wegpunkte zu" % len(lage.wegpunkte(p["weg"])),
                        k, L[k]["typ"], d, p["takte"], p["verlust"], e.get("leben", 0), p["p_tod"]))
        return aus

    def _abschuesse(self, L):
        """Ein gejagtes Ziel, das nicht mehr lebt, zaehlt genau einmal; der Reiter ist danach frei."""
        for r, v in list(self.befohlen.items()):
            if v[0] in ("jagd", "anritt") and (v[1] not in L or L[v[1]].get("leben", 1) <= 0 or L[v[1]]["besitzer"] in freunde_von(self.sp)
                                               or v[1] not in getattr(self, "_ziel_nr", {v[1]})):   # Nummer neu vergeben/kein Ziel mehr
                if v[0] == "jagd":
                    self.getoetet += 1
                self.befohlen.pop(r)

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
                for g in G.values() if g.get("besitzer") not in freunde_von(self.sp) and g["typ"] in WERT and g["typ"] not in TUERME]
        return max(kand)[1] if kand else None

    def schritt(self, L, G, befehl, brand=None):
        self.runde += 1
        aus = []
        for r, v in list(self.befohlen.items()):
            if v[0] == "ziel" and (v[1] not in L or L[v[1]].get("leben", 1) <= 0 or L[v[1]]["besitzer"] in freunde_von(self.sp)):
                self.getoetet += 1
                self.befohlen.pop(r)
        f = self.front(G, brand)
        for r in sorted(self.einheiten(L)):
            o = (L[r]["x"], L[r]["y"])
            kand = []
            for k, a in L.items():
                if a["besitzer"] in freunde_von(self.sp) or a.get("leben", 1) <= 0:
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
