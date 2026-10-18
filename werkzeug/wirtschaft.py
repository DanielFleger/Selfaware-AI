# -*- coding: utf-8 -*-
"""Wirtschaft im laufenden Spiel (Daniel 05.10.2026 00:06: "beachte gleich auch seasoning/vorratslager"):

1. Apfel-Seasoning (Daniel 04.10.: nebeneinanderliegende Plantagen genau dann setzen, wenn eine von Fruehling in
   Sommer wechselt - dann holen sie sich gegenseitig Aepfel, fast doppelt so produktiv).
   Belegt am 05.10. (Spielcode + Messung):
     - Ein Apfelbaum durchlaeuft die Stufen 0-5 im Kreis; Dauer je Stufe 500, 300, 200, 1000, 40, 40 Ticks
       (Tabelle 0x00B484C0, ein Schritt je Spieltick gemessen). Geerntet wird NUR in Stufe 3 - 1000 von 2080 Ticks.
     - Die Baeume einer Plantage werden beim Bau gepflanzt und starten in Stufe 0 (Zaehler 0-31 zufaellig).
     - Der Apfelbauer nimmt JEDEN reifen Apfelbaum naeher als 30 Felder (selectClosestTree 0x004F3610 prueft weder
       Plantage noch Besitzer); findet er keinen, steht er untaetig (Zustand 1).
   Darum: Gruppe A in der Eroeffnung, Gruppe B, sobald die Baeume von A in Stufe 3 springen. B braucht dann genau
   1000 Ticks bis zur Reife - so lange, wie A reif ist. Die Gruppen wechseln sich ab, jeder Bauer findet fast immer
   einen reifen Baum.
2. Lager erst, wenn der erste Traeger abliefern WILL (Daniel 04.10.). Abgelesen (UpdateWoodcutter 0x0054C710):
   ein Holzfaeller mit fertigem Holz steht in Zustand 7 und fragt alle 21 Ticks nach einem Lager; ohne Lager bleibt
   er in Zustand 7. Gemessen am Eroeffnungsstand: erster Zustand 7 bei Tick ~4.500.
   Das alte Lager behaelt bis zum Bau von B dessen Holz (3 je Plantage) und wird danach leer abgerissen.
3. Lager rechtzeitig erweitern (Daniel 04.10.: wird es voll, WAEHREND Traeger unterwegs sind, verfallen ihre Waren -
   abgelesen: Ladung wird auf 0 gesetzt). Gezaehlt wird, was die Traeger bringen: Ladung (+904) der Einheiten in
   Zustand 8 plus Holzfaeller in Zustand 7 mal der groessten bisher gemessenen Ladung.
"""
import math
import os
from laden import befehl, peek
from befehl import ABZUG

APFEL, HOLZFAELLER, LAGER, BAUER = 32, 3, 10, 13
APFEL_HOLZ, APFEL_GOLD = 3, 15          # Apfelplantage (Liga, gemessen 05.10.)
A_FEHL_MAX = 3                           # 19.10. (1019b): so oft darf ein A-Platz scheitern, dann wird er aufgegeben
B_FEHL_MAX = 10                          # 19.10. (1019b): B-Plaetze werden oefter versucht (jede Runde) - nach 10 aufgeben
FEHL_TICKS = 1500                        # 19.10. (1019c: alle 5 B nach 10 Versuchen in einer Runde aufgegeben): und erst nach so langer Zeit
SUCHRADIUS_BAUER = 30                       # abgelesen: selectClosestTree nimmt Baeume naeher als 0x1E Felder
BAUM_BASIS, BAUM_SCHRITT, BAUM_STUFE = 0xF2CC54, 156, 0x80
REIF = 3
JE_TEIL = 48                                # Lagerteil fasst je Ware 48 (abgelesen: addResourceToStockpile(..., 0x30))
LAGERWAREN = ("holz", "hopfen", "stein", "eisen", "pech", "weizen", "mehl")


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def apfel_gruppen(orte, radius=SUCHRADIUS_BAUER):
    """Teilt Apfelplantagen (Ankerpunkte) in A (sofort bauen) und B (bauen, wenn A reif wird).
    Haufen = Plantagen, die einander ueber hoechstens <radius> Felder erreichen (Suchkreis des Bauern).
    Im Haufen abwechselnd A/B, vom Haufen-Mittelpunkt nach aussen; Einzelstuecke -> A (kein Partner)."""
    orte = [tuple(o) for o in orte]
    rest, haufen = list(orte), []
    while rest:
        h = [rest.pop(0)]
        neu = True
        while neu:
            neu = False
            for o in list(rest):
                if any(schach(o, p) <= radius for p in h):
                    h.append(o); rest.remove(o); neu = True
        haufen.append(h)
    A, B = [], []
    for h in haufen:
        if len(h) == 1:
            A += h
            continue
        mx, my = sum(o[0] for o in h) / len(h), sum(o[1] for o in h) / len(h)
        for i, o in enumerate(sorted(h, key=lambda o: (abs(o[0] - mx) + abs(o[1] - my), o))):
            (A if i % 2 == 0 else B).append(o)
    return A, B


class Wirtschaft:
    def __init__(self, plan, sp, baue_schnell, alte_lager):
        self.sp, self.baue_schnell = sp, baue_schnell
        self.A, self.B = apfel_gruppen(plan["aepfel"])
        self.B_offen = list(self.B)
        self.b_vergeben = None                  # Plantagen-Nummern, die schon gezaehlt sind (A, frueher, je B eine)
        self.B_erwartet = {}                    # B-Sollplatz -> (gemeldeter Bauort, Tick); erst echtes Gebaeude bestaetigt
        self.lager_ort = tuple(plan["lager"])
        self.alt = set(alte_lager)               # Lagerteile aus der Eroeffnung (behalten B-Holz bis B steht)
        self.apfelbaum, self.B_tick, self.A_reif_tick = None, None, None
        self.lager_tick, self.ladung_max = None, {}
        self.bauern = []                          # (tick, Bauern, untaetig)
        self.versuche_B = 0
        self.a_versucht = {}                 # A-Platz -> Tick des letzten Bauversuchs (nachholen)
        self.holz_verbauen = None            # (st, L, G) -> (ergebnis, text): Holz verkaufen oder Holzfaeller (setzt der Lenker)
        self.baum_gesucht = -999             # Tick der letzten Baumsuche
        self.extra = {}                      # Ruecklage einer Pflicht (v14), vom Lenker gesetzt
        self.umzug_ab = None                 # v14: Tick, ab dem das alte Lager geraeumt wird (Startholz vollstaendig)
        self.lager_genau = False             # v14: neues Lager genau am Plan-Platz (Umkreis 0)
        self.b_versatz = None                # Lernkreis (Daniel 23:30 "Seasoning zu spaet, jede Wartezeit der Apfelbauern ist
                                             # unproduktiv"): B so viele Ticks nach "alle A stehen" statt erst bei A-Reife
        self.a_steht_tick = None
        self.umzug_nach_b = False            # v15: altes Lager erst raeumen, wenn B steht (Daniel 22:29: Seasoning vor der
                                             # ersten Holzlieferung - das B-Holz muss im alten Lager liegen bleiben)
        # Baum gleich jetzt suchen, solange das Spiel noch steht (9g: die Kartensuche mitten im Lauf kostete ~600 Ticks)
        if self.B:
            self.apfelbaum = self._a_baum() or -1

    # ---- Messen ---------------------------------------------------------------------------------------------------
    def _a_baum(self):
        """Einen Apfelbaum einer A-Plantage suchen (einmal, ueber die Baumliste des Moduls)."""
        befehl({"rohstoffkarte": {}}, 5.0, bis="ROHSTOFF")
        datei = os.path.join(ABZUG, "baeume.txt")
        for z in open(datei).read().splitlines()[1:]:
            w = z.split()
            if len(w) >= 6 and w[1] == "15" and any(schach((int(w[3]), int(w[4])), (a[0] + 5, a[1] + 5)) <= 8 for a in self.A):
                return int(w[0])
        return None

    def stufe_a(self):
        if self.apfelbaum is None:
            self.apfelbaum = self._a_baum() or -1
        if self.apfelbaum <= 0:
            return None
        return peek(BAUM_BASIS + self.apfelbaum * BAUM_SCHRITT + BAUM_STUFE)[0]

    # ---- eine Runde -----------------------------------------------------------------------------------------------
    def ruecklage(self, G):
        """Was fuer die offenen B-Plantagen zurueckliegt, sobald alle A stehen (B ist dann spaetestens ~1.000 Ticks
        spaeter dran: Stufen 500 + 300 + 200). Jeder Ausgeber (Anwerben, Planer, Huetten) zieht das ab.
        gewinn_5 (Daniel 23:41 "Seasoning am Anfang"): A stand bei 534, reif bei 1.500, die letzte B-Plantage wartete
        bis 3.978 - Planer (Steinbruch + Joch, "Huette zuerst") und Huettenbau verbauten das Holz."""
        n = 0 if self.a_offen(G) else len(self.B_offen)
        # extra: was eine Pflicht (v14: Steinbrueche + Joche) noch braucht - setzt der Lenker jede Runde
        # brot: naechster fehlender Bau der Brotkette (brotbau.py), vom Lenker jede Runde gesetzt (SAI 11.10. 23:20)
        brot = getattr(self, "brot", {}) or {}
        return {"holz": APFEL_HOLZ * n + self.extra.get("holz", 0) + brot.get("holz", 0),
                "gold": APFEL_GOLD * n + self.extra.get("gold", 0) + brot.get("gold", 0)}

    def _baue_grund(self, typ, x, y, r, **k):
        """19.10.: Bauen mit Grund ("gebaut", "platz", "schutz", "rohstoff"); alte baue-Funktionen ohne Grund -> "platz"."""
        try:
            return self.baue_schnell(typ, x, y, r, mit_grund=True, **k)
        except TypeError:
            o = self.baue_schnell(typ, x, y, r, **k)
            return o, ("gebaut" if o is not None else "platz")

    def _platz_aufgeben(self, art, o, erg, grund, t, grenze=None):
        """19.10. (1019b/1019c): echte Platzablehnungen je Platz zaehlen (nicht "rohstoff"/"schutz"); aufgeben erst nach
        grenze Ablehnungen UND FEHL_TICKS seit der ersten."""
        if erg is not None or grund != "platz":
            return False
        self._fehl = getattr(self, "_fehl", {})
        zahl, seit = self._fehl.get((art, o), (0, t))
        self._fehl[(art, o)] = (zahl + 1, seit)
        return zahl + 1 >= (grenze or A_FEHL_MAX) and t - seit >= FEHL_TICKS

    def a_offen(self, G):
        """A-Plaetze, an denen (noch) keine eigene Apfelplantage steht."""
        stehen = [(g["x"], g["y"]) for g in G.values() if g["besitzer"] == self.sp and g["typ"] == APFEL]
        return [o for o in self.A if not any(schach(o, s) <= 2 for s in stehen)]

    def schritt(self, st, L, G):
        ev = []
        t = st.get("t", 0)
        eigen = {n: g for n, g in G.items() if g["besitzer"] == self.sp}
        einheiten = {n: e for n, e in L.items() if e["besitzer"] == self.sp}
        # Messung: Apfelbauern untaetig?
        bauern = [e for e in einheiten.values() if e["typ"] == BAUER]
        if bauern:
            self.bauern.append((t, len(bauern), sum(1 for e in bauern if e["zustand"] == 1)))
        # 0. A nachholen (Daniel 05.10. 23:09 "bitte nicht Farmen vergessen"): in der Eroeffnung reicht das Gold nach Posten +
        #    Assassine nicht (gemessen live_4/5: 5 Gold, Plantage 15) - ohne A wird A nie reif und B nie gesetzt. Fehlende
        #    A-Plantage bauen, sobald 15 Gold + 3 Holz da sind; derselbe Platz erst nach 50 Ticks wieder (schnelle Runden).
        for o in self.a_offen(G):
            if st.get("gold", 0) >= APFEL_GOLD and st.get("holz", 0) >= APFEL_HOLZ and t - self.a_versucht.get(o, -999) >= 50:
                self.a_versucht[o] = t
                erg, grund = self._baue_grund(APFEL, o[0], o[1], 2)
                ev.append("Apfelplantage A nachgeholt bei %s: %s (Gold %d, Holz %d)" % (o, erg, st.get("gold", 0), st.get("holz", 0)))
                # 19.10. (1019b, Green Haven: der A-Platz (154, 163) wurde 20.000 Ticks lang immer wieder abgelehnt - "A-Farmen
                # offen 1" hielt die ganze Partie das Anwerben an, eine einzige Assassine): nach A_FEHL_MAX echten
                # Platzablehnungen ueber mindestens FEHL_TICKS aufgeben (fehlendes Holz/Gold zaehlt nicht - 1019c)
                if self._platz_aufgeben("A", o, erg, grund, t) and o in self.A:
                    self.A.remove(o)
                    ev.append("A-Platz %s nach %d Platzablehnungen aufgegeben - bremst Anwerben und Seasoning nicht mehr" % (
                        o, self._fehl[("A", o)][0]))
                break
        # A-Baum suchen, sobald eine A-Plantage steht. gewinn_2 (Daniel 23:29 "Seasoning zu langsam"): die Raid-Eroeffnung
        # baut A erst spaeter nach, die Suche beim Start fand keinen Baum, merkte sich -1 - A in 28.700 Ticks nie reif, B nie.
        if (self.apfelbaum or -1) <= 0 and len(self.a_offen(G)) < len(self.A) and t - self.baum_gesucht >= 200:
            self.baum_gesucht = t
            self.apfelbaum = self._a_baum() or -1
            ev.append("A-Baum gesucht: %s" % self.apfelbaum)
        # 1. Seasoning: B setzen, sobald A reif wird
        if self.B_offen:
            stufe = self.stufe_a() if self.B_tick is None else REIF
            if self.a_steht_tick is None and not self.a_offen(G):
                self.a_steht_tick = t
            frueh = self.b_versatz is not None and self.a_steht_tick is not None and t >= self.a_steht_tick + self.b_versatz
            if stufe == REIF or frueh:
                if self.A_reif_tick is None:
                    self.A_reif_tick = t
                    ev.append("Seasoning: A-Plantagen reif bei Tick %d (Baum %d) - setze %d B-Plantagen" % (t, self.apfelbaum, len(self.B_offen)))
                stehen = [(n, (g["x"], g["y"])) for n, g in eigen.items() if g["typ"] == APFEL]
                if self.b_vergeben is None:
                    # Daniel 07.10. (Lauf 14: "eine Apfelplantage oben nicht platziert"): B (89,235) stand nie, galt aber als
                    # bestaetigt - jede Plantage im Umkreis 2 zaehlte, auch eine schon fuer ein anderes B gezaehlte. Jetzt
                    # bestaetigt nur eine NEUE Plantage (Nummer noch nicht vergeben) genau einen B-Platz.
                    self.b_vergeben = {n for n, _ in stehen}
                holz_frei, gold_frei = st.get("holz", 0), st.get("gold", 0)
                for o in list(self.B_offen):
                    erwartet = self.B_erwartet.get(o)
                    treffer = [n for n, s in stehen if n not in self.b_vergeben and (schach(o, s) <= 2 or (
                        erwartet and schach(erwartet[0], s) <= 2))]
                    bestaetigt = bool(treffer)
                    if bestaetigt:
                        self.b_vergeben.add(treffer[0])
                        self.B_offen.remove(o)
                        self.B_erwartet.pop(o, None)
                        continue
                    if erwartet and t - erwartet[1] < 50:
                        continue                         # Auftrag gesendet; naechstes echtes Lagebild abwarten
                    if holz_frei >= APFEL_HOLZ and gold_frei >= APFEL_GOLD:
                        # Ist der Sollplatz dauerhaft belegt, darf die Suche ausweichen - aber nur so weit, dass die
                        # neue Plantage nach der Dreiecksregel weiterhin hoechstens 30 Felder von mindestens einer
                        # A-Plantage liegt. Damit bleibt der gemessene Baum-Suchradius garantiert erhalten.
                        spielraum = max(2, SUCHRADIUS_BAUER - min((schach(o, a) for a in self.A), default=SUCHRADIUS_BAUER - 2))
                        ort, grund = self._baue_grund(APFEL, o[0], o[1], spielraum, zweck="B")
                        if ort is not None:
                            self.B_erwartet[o] = (tuple(ort), t)
                            ev.append("Seasoning: B %s bestellt bei %s" % (o, tuple(ort)))
                            continue
                        # 19.10. (1019b, Green Haven: B (153, 153) ~260-mal "kein Bauplatz" - der live gesuchte Markt stand dort;
                        # B blieb offen, der Planer meldete die ganze Partie "braucht Gold" und es wurde nicht angeworben)
                        if self._platz_aufgeben("B", o, ort, grund, t, B_FEHL_MAX):
                            self.B_offen.remove(o)
                            self.B_erwartet.pop(o, None)
                            ev.append("Seasoning: B %s nach %d Platzablehnungen aufgegeben - bremst Anwerben nicht mehr" % (
                                o, self._fehl[("B", o)][0]))
                            continue
                        if self.versuche_B % 10 == 0:
                            ev.append("Seasoning: B %s kein Bauplatz (Spielraum %d)" % (o, spielraum))
                            holz_frei -= APFEL_HOLZ
                            gold_frei -= APFEL_GOLD
                    elif holz_frei < APFEL_HOLZ and gold_frei >= 60:
                        # 9g: der Markt verbaute das zurueckgelegte B-Holz - dann kaufen (Spielbefehl 38, kaufen = 0, Holz = 2)
                        befehl({"spielbefehl": {"nr": 38, "werte": [0, 2]}}, 1.0, bis="SPIELBEFEHL")
                        ev.append("Holz fuer B gekauft (Holz %d, Gold %d)" % (holz_frei, gold_frei))
                        break
                self.versuche_B += 1
                if not self.B_offen:
                    self.B_tick = t
                    ev.append("Seasoning: alle %d B-Plantagen stehen (Tick %d, %d Ticks nach A-Reife)" % (len(self.B), t, t - self.A_reif_tick))
                elif self.versuche_B % 10 == 0:
                    ev.append("Seasoning: %d B-Plantagen noch offen (Holz %d, Gold %d)" % (len(self.B_offen), st.get("holz", 0), st.get("gold", 0)))
        # 2. Altes Lager abreissen, wenn B steht (oder keins geplant) und es leer ist
        alt_da = [n for n in self.alt if n in eigen]
        # Daniel 05.10. 19:09: in 9q stand das alte Lager bis Tick 6.175 (B wartete auf Gold), die Holzfaeller trugen
        # alles zum Bergfried. Darum weg, sobald B steht ODER der erste Holzfaeller abliefern will - was zuerst kommt.
        will_liefern = any(e["typ"] == HOLZFAELLER and e["zustand"] == 7 for e in einheiten.values())
        # v14: fester Zeitpunkt statt "B steht / Holzfaeller will liefern" - das Startholz ist ab ~650 komplett da (Plan_
        # Streitkolben: 30 bei 120, +28 je 110 Ticks, 150 ab ~650); danach liefern Steinbrueche und Holzfaeller ans neue Lager
        raeumen = (t >= self.umzug_ab) if self.umzug_ab is not None else (not self.B_offen or will_liefern)
        if self.umzug_nach_b:
            raeumen = not self.B_offen
        if alt_da and raeumen:
            inhalt = {k: st.get(k, 0) for k in LAGERWAREN if st.get(k, 0) > 0}
            rest_ok = sum(inhalt.values()) < 5
            if not rest_ok and (self.umzug_nach_b or self.umzug_ab is not None) and set(inhalt) <= {"holz"} and inhalt.get("holz", 0) < 20 and self.holz_verbauen:
                # v15: unter einem 20er-Los und kein Holzfaeller erlaubt/moeglich -> der Rest blockiert den Umzug nicht
                erg, text = self.holz_verbauen(st, L, G)
                if erg is None:
                    ev.append("Altes Lager: Rest %s geht beim Abriss verloren (%s)" % (inhalt, text))
                    rest_ok = True
            if rest_ok:
                # Verkaeufe gehen nur in 5er-Losen, Bauten brauchen mindestens 5 Holz. Darum wird alles Verkaufbare
                # zuerst geleert; nur ein technisch weder verkauf- noch verbaubarer Gesamt-Rest von 1-4 darf fallen.
                for n in alt_da:
                    befehl({"abreissen": {"nr": n}}, 0.8, bis="ABREISSEN")
                ev.append("Altes Lager abgerissen (%d Teile, Rest %s) bei Tick %d" % (len(alt_da), inhalt or "leer", t))
                self.alt.clear()
            else:
                ware = max(inhalt, key=inhalt.get)
                if ware == "holz":
                    # Daniel 06.10.: Holz verkaufen nur, solange Gold das Anwerben bremst, sonst Holzfaeller - entscheidet der
                    # Lenker (holz_verwerten). Geht beides gerade nicht, bleibt das Lager stehen und das Holz liegen.
                    erg, text = self.holz_verbauen(st, L, G) if self.holz_verbauen else (None, "kein Planer")
                    ev.append("Altes Lager leeren (Holz): %s (%s; Inhalt %s)" % (erg, text, inhalt))
                else:
                    befehl({"spielbefehl": {"nr": 38, "werte": [1, {"stein": 4, "eisen": 6, "pech": 7, "weizen": 9,
                                                                   "hopfen": 3, "mehl": 16}[ware]]}}, 1.0, bis="SPIELBEFEHL")
                    ev.append("Altes Lager leeren: %s verkauft (Inhalt %s)" % (ware, inhalt))
        # 3. Neues Lager erst, wenn ein Holzfaeller abliefern will (Zustand 7)
        teile = [n for n, g in eigen.items() if g["typ"] == LAGER and n not in self.alt and n not in alt_da]
        if teile and not alt_da and not getattr(self, "lager_ist_anker", False):
            # Der Planplatz kann im Bautakt kurz belegt sein. Ab jetzt zaehlt der wirklich gebaute, vom Spiel als
            # erreichbar gemeldete Lagerteil als Mittelpunkt; Erweiterungen duerfen nicht zum alten Sollpunkt driften.
            g0 = eigen[teile[0]]
            if g0.get("erreichbar", 0) == 1:
                self.lager_ort = (g0["x"], g0["y"])
                self.lager_ist_anker = True
        wollen = [n for n, e in einheiten.items() if e["typ"] == HOLZFAELLER and e["zustand"] == 7]
        # v14: sofort, sobald das alte weg ist (v12: abgerissen bei 1.314, neues erst bei 3.723 - ohne Lager lieferten die
        # Holzfaeller nicht, Zustand 7 kam nie; Holz 0 von 1.453 bis 4.294)
        jetzt = (not alt_da and not self.alt) if self.lager_genau else bool(wollen)
        if not teile and jetzt and (self.lager_tick is None or t - self.lager_tick > (30 if self.lager_genau else 60)):
            # v15: genau am Plan-Platz nur beim ersten Versuch, danach Umkreis 3 (v15: (87,268) war vom Steinhaufen belegt,
            # 330 Ticks ohne Lager - nie wieder ohne Lager stehen bleiben)
            self.lager_versuche = getattr(self, "lager_versuche", 0) + 1
            r = (0 if self.lager_versuche == 1 else 3) if self.lager_genau else 8
            ort = self.baue_schnell(LAGER, self.lager_ort[0], self.lager_ort[1], r)
            self.lager_tick = t
            ev.append("Lager gesetzt bei %s - %d Holzfaeller wollen abliefern (Tick %d)" % (ort, len(wollen), t))
        # 4. Rechtzeitig erweitern: Bestand + was unterwegs ist
        for e in einheiten.values():
            if e["zustand"] == 8 and e.get("ladung", 0) > 0:
                self.ladung_max[e["typ"]] = max(self.ladung_max.get(e["typ"], 0), e["ladung"])
        if teile and not alt_da and not getattr(self, "lager_stopp", False):
            unterwegs = sum(e.get("ladung", 0) for e in einheiten.values() if e["typ"] == HOLZFAELLER and e["zustand"] == 8)
            bald = len(wollen) * self.ladung_max.get(HOLZFAELLER, 0)
            bestand = {k: st.get(k, 0) for k in LAGERWAREN}
            noetig = sum(math.ceil(v / JE_TEIL) for k, v in bestand.items() if k != "holz") + \
                math.ceil((bestand["holz"] + unterwegs + bald) / JE_TEIL)
            menge = sum(bestand.values())
            # Rueckfall solange keine Ladung gemessen ist: alte Reserve (60) wie bisher
            darf_erweitern = getattr(self, "lager_max_teile", None) is None or len(teile) < self.lager_max_teile
            if darf_erweitern and (noetig > len(teile) or (not self.ladung_max and menge >= JE_TEIL * len(teile) - 60)):
                ort = self.baue_schnell(LAGER, self.lager_ort[0], self.lager_ort[1], 10)
                ev.append("Lager erweitert %s: Bestand %d, Holz unterwegs %d + bald %d, Teile %d -> noetig %d" % (
                    ort, menge, unterwegs, bald, len(teile), noetig))
        return ev

    def bericht(self):
        def anteil(von, bis):
            r = [(n, u) for t, n, u in self.bauern if von <= t < bis]
            n = sum(x[0] for x in r)
            return "%.0f %% (%d Messungen)" % (100.0 * sum(x[1] for x in r) / n, len(r)) if n else "keine Messung"
        b = self.B_tick or 10 ** 9
        return ("Seasoning: A %d / B %d Plantagen, A reif bei %s, B gesetzt bei %s; Apfelbauern untaetig vor B %s, "
                "B bis B+1000 %s, danach %s; FESTES FENSTER Tick 5000-12000 (zum Vergleich zwischen Partien): %s; "
                "Lager gesetzt bei %s, gemessene Ladung je Gang %s" % (
                    len(self.A), len(self.B), self.A_reif_tick, self.B_tick, anteil(0, b), anteil(b, b + 1000),
                    anteil(b + 1000, 10 ** 9), anteil(5000, 12000), self.lager_tick, self.ladung_max or "keine"))


class Ausbau:
    """Wirtschaft im Lauf erweitern und nachbauen (Daniel 05.10. 19:05/19:06: Wirtschaftserweiterung - mehr
    Steinbrueche/Eisen; Jagd - erkennen, dass Rehe da sind; nachbauen - Holzfaeller, Apfelplantagen, Haeuser; dazu
    Haeuser vor der Wohngrenze und Steuern, wenn die Beliebtheit es hergibt). Alle ALLE Runden, in dieser Reihenfolge.
    Solange ein Schritt Gold braucht, setzt er braucht_gold - dann wirbt der Lenker keine Assassinen (erst rollen).
    Alle Schwellen sind STARTWERTE (gemessen sind nur die Kosten: Huette 5 Holz, Steinbruch 25, Ochsenjoch 5,
    Eisenmine 20 Holz + 6 Stein, Jaeger 3 Holz + 60 Gold, Apfelplantage 3 Holz + 15 Gold)."""
    ALLE = 10
    STEUER_HOCH, STEUER_RUNTER, STEUER_MIN, STEUER_MAX = 97, 95, 3, 8
    JAGD_REHE, JAGD_UMKREIS, JAGD_MAX, JAGD_WEG = 5, 15, 3, 70   # 9q: ein Jaeger landete 166 Felder weit weg
    STEINBRUECHE, EISENMINEN = 2, 1

    def __init__(self, plan, sp, baue_schnell, wirt, steuerstufe):
        self.sp, self.plan, self.baue, self.wirt = sp, plan, baue_schnell, wirt
        self.K = tuple(plan.get("bergfried_eingang", (165, 111)))
        self.feinde = []
        if plan.get("start"):
            import json, os
            d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
            info = json.load(open(os.path.join(d, "start_%s.json" % plan["start"]), encoding="utf-8"))
            self.feinde = [tuple(v["eingang"]) for v in info["feind_bergfried"].values()]
            z = open(os.path.join(d, "rohstoffe_%s.txt" % plan["start"])).read().splitlines()[1:]
            self.stein = [(x, y) for y, r in enumerate(z) for x, c in enumerate(r) if c == "b" and self.eigene_seite((x, y))]
            self.eisen = [(x, y) for y, r in enumerate(z) for x, c in enumerate(r) if c == "i" and self.eigene_seite((x, y))]
        else:
            self.stein, self.eisen = [], []
        self.steuer = steuerstufe
        self.steuer_runde = -99
        self.braucht_gold = False
        self.bilanz = {}

    def eigene_seite(self, p):
        d = schach(p, self.K)
        return all(d < schach(p, f) for f in self.feinde)

    def _naechster(self, punkte, zu):
        return min(punkte, key=lambda p: schach(p, zu)) if punkte else None

    def _bau(self, typ, x, y, r, was, ev):
        ort = self.baue(typ, x, y, r)
        ev.append("AUSBAU %s %s" % (was, ort))
        if ort:
            self.bilanz[was] = self.bilanz.get(was, 0) + 1
        return ort

    def schritt(self, st, L, G, runde):
        if runde % self.ALLE:
            return []
        ev, self.braucht_gold = [], False
        eigen = [g for g in G.values() if g["besitzer"] == self.sp]
        b_offen = bool(self.wirt.B_offen)     # 9q: der Ausbau gab das Gold aus, B wartete 4.353 Ticks - B hat Vorrang
        if b_offen:
            self.braucht_gold = True          # 9r: auch Soeldnerlager und Assassinen warten, bis B steht
        zahl = lambda t: sum(1 for g in eigen if g["typ"] == t)
        holz, gold, stein = st.get("holz", 0), st.get("gold", 0), st.get("stein", 0)
        # 1. Huetten vor der Wohngrenze
        if st.get("leute", 0) >= st.get("platz", 0) - 2 and holz >= 5:
            self._bau(1, self.K[0] - 7, self.K[1] - 2, 25, "Huette (Leute %d / Platz %d)" % (st.get("leute", 0), st.get("platz", 0)), ev)
            holz -= 5
        # 2. Steuern nach Beliebtheit
        b = st.get("beliebt", 0) / 100.0
        if runde - self.steuer_runde >= 2 * self.ALLE:
            neu = self.steuer
            if b >= self.STEUER_HOCH and self.steuer < self.STEUER_MAX and st.get("leute", 0) >= 15:
                neu = self.steuer + 1
            elif b < self.STEUER_RUNTER and self.steuer > self.STEUER_MIN:
                neu = self.steuer - 1
            if neu != self.steuer:
                befehl({"spielbefehl": {"nr": 34, "werte": [neu]}}, 1.0, bis="SPIELBEFEHL")
                ev.append("STEUER %d -> %d (Beliebtheit %.2f, Leute %d)" % (self.steuer, neu, b, st.get("leute", 0)))
                self.steuer, self.steuer_runde = neu, runde
        # 3. Jagd: Rehe auf unserer Seite erkennen
        if zahl(7) < self.JAGD_MAX:
            rehe = [(e["x"], e["y"]) for e in L.values() if e["typ"] == 44 and e["besitzer"] == 0 and self.eigene_seite((e["x"], e["y"]))
                    and schach((e["x"], e["y"]), self.K) <= self.JAGD_WEG]
            beste = max(((sum(1 for q in rehe if schach(p, q) <= self.JAGD_UMKREIS), p) for p in rehe), default=(0, None))
            jaeger = [(g["x"], g["y"]) for g in eigen if g["typ"] == 7]
            if beste[0] >= self.JAGD_REHE and not any(schach(beste[1], j) <= self.JAGD_UMKREIS for j in jaeger):
                if gold >= 60 and holz >= 3 and not b_offen:
                    self._bau(7, beste[1][0], beste[1][1], 12, "Jaeger an %d Rehen" % beste[0], ev)
                    gold -= 60
                else:
                    self.braucht_gold = True
        # 4. Nachbauen: Holzfaeller und Apfelplantagen aus dem Plan, die fehlen (Apfel erst, wenn B steht)
        stehen = {t: [(g["x"], g["y"]) for g in eigen if g["typ"] == t] for t in (3, 32)}
        for p in self.plan.get("holzfaeller", []):
            if holz < 5:
                break
            if not any(schach(p, s) <= 2 for s in stehen[3]):
                self._bau(3, p[0], p[1], 4, "Holzfaeller nachgebaut", ev)
                holz -= 5
                break
        if not self.wirt.B_offen:
            for p in self.plan.get("aepfel", []):
                if not any(schach(p, s) <= 2 for s in stehen[32]):
                    if gold >= 15 and holz >= 3:
                        self._bau(32, p[0], p[1], 4, "Apfelplantage nachgebaut", ev)
                        gold -= 15
                    else:
                        self.braucht_gold = True
                    break
        # 5. Steinbrueche + Ochsenjoche, dann Eisen
        q = zahl(20)
        if q < self.STEINBRUECHE and holz >= 25 and self.stein:
            mitte = tuple(self.plan["stein"]["steinbruch"]) if self.plan.get("stein") else self.K
            c = self._naechster(self.stein, mitte)
            if self._bau(20, c[0], c[1], 15, "Steinbruch %d" % (q + 1), ev):
                holz -= 25
        elif zahl(4) < q and holz >= 5:
            bruch = [(g["x"], g["y"]) for g in eigen if g["typ"] == 20]
            self._bau(4, bruch[-1][0] + 3, bruch[-1][1] + 3, 8, "Ochsenjoch", ev)
            holz -= 5
        elif zahl(5) < self.EISENMINEN and holz >= 20 and stein >= 6 and self.eisen:
            c = self._naechster(self.eisen, self.K)
            self._bau(5, c[0], c[1], 12, "Eisenmine", ev)
        return ev

    def bericht(self):
        return "Ausbau: %s, Steuerstufe zuletzt %d" % (self.bilanz or "nichts", self.steuer)
