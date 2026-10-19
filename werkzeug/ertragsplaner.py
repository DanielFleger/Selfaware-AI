# -*- coding: utf-8 -*-
"""Ertrags-Planer, Stand 3: lernt im Spiel (Daniel 05.10. 19:44 "ja, bau das so" - nach Partie 9t; Stand 3 nach 9u).

Stand 1 (9s/9t) rechnete mit festen Startwerten und einer vermuteten Wegkorrektur; Befund 9t: 26 Jaegerhuetten fuer
1.560 Gold, die 120 Gold brachten. Stand 2 (9u) lernte im Spiel, hatte aber drei Annahmen, die 9u widerlegt hat
(Meilensteine M21). Stand 3:

1. MESSEN (Ertragsmesser, jede Runde): Zugang je Ware = Bestandsaenderung + Verkauftes + Verbautes. Verbautes = neue
   eigene Gebaeude (Zaehler G<typ> der Statuszeile) mal Baukosten. Nahrung wird zusaetzlich gegessen, dort zaehlt nur der
   positive Teil (untere Schranke). 9u: Holz 1 von 756 Runden negativ (17 von 2.521), Stein und Eisen 0 - die Buchfuehrung
   haelt. Geteilt durch die Betriebszeit der BESETZTEN Betriebe, gewichtet mit dem Wegfaktor (d0 + 20) / (d + 20)
   (vermutet; Holz haengt in 9u kaum am Weg) -> Ertrag je 1.000 Ticks auf dem Messweg d0.
   STARTWERTE aus der langen Messpartie (20.000 Ticks, ein Betrieb je Art, daten/ertrag_messung.json) zaehlen so viel wie
   die Ticks, ueber die sie gemessen wurden (ab erster Lieferung) - ein einzelner Lieferbrocken reisst die Schaetzung
   nicht mehr hoch (9u: Jaeger sprang nach der ersten Fleischlieferung auf 25 Gold/1000).
   UHR je Betrieb: startet bei seiner ersten Abgabe (Ladung des Arbeiters faellt auf 0) oder nach der Anlaufzeit, was
   zuerst kommt - auch fuer Betriebe, die beim Start schon standen (9u: die 14 Holzfaeller der Eroeffnung zaehlten ab
   Tick 729, ihre erste Ladung kam erst bei ~4.600; der Messer hielt Holzfaeller fuer wertlos). Die erste beobachtete
   Abgabe jedes Betriebs wird abgezogen (Zaunpfahl: sie beendet den Anlauf, sie ist kein Dauerertrag); ihre Groesse =
   die groesste getragene Ladung der Art (gemessen: Holz 18, Eisen 1).
   ANLAUF je Art: Median Bau -> erste Abgabe, aber nur, wenn die Gegenprobe zeigt, dass die Abgaben der Art sichtbar sind
   (abgegebene Ladung / gebuchter Zugang 0,7-1,3; 9u: Eisen 0,91, Aepfel 0,84 ja - Holz 0,10, Jaeger 0,46 nein).
   Sonst: erste Lieferung der Art minus erster besetzter Betrieb; sonst Startwert.
2. KOSTEN aus der Baukostentabelle des laufenden Spiels (0x01124CF4 + Typ*20: Holz Stein Eisen Pech Gold, Wissensstand
   Abschnitt Baukosten; gelesen 05.10. 19:52: Eisenmine 20 Holz + 6 Stein, Holzfaeller 5 Holz, Jaeger 3 Holz + 60 Gold).
   Bewertet zum VERKAUFSpreis: Holz und Stein werden nie gekauft (Daniel 19:44), verbaut fehlen sie nur dem Verkauf.
3. HORIZONT UND REIHENFOLGE: gebaut wird nur, was sich bis Partieende bezahlt macht, und zuerst, was bis dahin den
   meisten Gewinn bringt: Gewinn = Ertrag in Gold je Tick * (Rest - Anlauf) - Kosten. (Stand 3 reihte nach kuerzester
   Amortisation - 9v: billige, schwache Bauten zuerst, 7 ferne Holzfaeller zu ~2 Gold/1000 und 3 ferne Steinbrueche vor
   der ersten Eisenmine bei Tick 10.826.) Ist der beste Bau nicht bezahlbar, darf ein anderer nur gebaut werden, wenn er
   nichts verbraucht, was der beste braucht. Ohne Partieende (ende=None) gilt die kuerzeste Amortisation.
4. PLAETZE aus den Platzkarten des Starts (karten_holen.py, ganze Karte): Eisenmine, Steinbruch, Apfelplantage direkt;
   Holzfaeller am naechsten gueltigen Platz zu einem Baum, den noch kein Holzfaeller im Umkreis 7 hat.
5. STEIN-RESERVE (Daniel 19:44): Stein wird bis auf den Bedarf der naechsten Eisenmine verkauft, solange sich eine Mine
   noch lohnt (gemessen: 6 Stein je Mine).
Gespart wird nur, was fehlt: Gold-Sparen (keine Assassinen) nur, wenn dem besten Bau Gold fehlt.
(Stand 2 hatte "kein zweiter Betrieb vor der ersten Lieferung" - meine Regel, nicht Daniels; sie schob in 9u die Minen
2-6 um ~6.000 Ticks: 6 statt 12 Eisen-Lose. Gestrichen; die gewichteten Startwerte tragen jetzt die Vorsicht.)

WIDERLEGUNG, vorher festgelegt (05.10. 19:55, gilt weiter):
 a) Buchfuehrung falsch, wenn bei Holz/Stein/Eisen mehr als 5 % der Runden einen negativen Zugang zeigen oder die
    negativen Zugaenge mehr als 10 % des Gesamtzugangs ausmachen (dann fehlt ein Abfluss).
 b) Planer falsch, wenn er eine Art baut, deren Anlauf + Amortisation laut eigener Rechnung ueber das Partieende geht.
"""
import json, os, time
from laden import befehl, peek

_PACK_MERK = {}   # 18.10.: (Groesse, Platzliste) -> Ergebnis von _dicht_packen


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def steinbruch_gruppen(brueche, radius=24):
    """Nahe Steinbrueche zu einem gemeinsamen Abholbereich verbinden.
    Ochsen duerfen benachbarte Haufen bedienen; eine Pro-Bruch-Zaehlung baut sonst fuer denselben Haufen immer wieder
    einen vermeintlich fehlenden zweiten Ochsen. Die transitive Gruppe bildet genau diesen gemeinsam genutzten Bereich."""
    offen, gruppen = set(brueche), []
    while offen:
        gruppe, rand = {offen.pop()}, []
        rand.extend(gruppe)
        while rand:
            n = rand.pop()
            nah = {m for m in offen if schach((brueche[n]["x"], brueche[n]["y"]),
                                              (brueche[m]["x"], brueche[m]["y"])) <= radius}
            offen -= nah
            gruppe |= nah
            rand.extend(nah)
        gruppen.append(tuple(sorted(gruppe)))
    return sorted(gruppen)

KOSTEN_ADR = 0x01124CF4
KOSTEN_WAREN = ("holz", "stein", "eisen", "pech", "gold")
VERKAUF = {"holz": 1, "stein": 5, "eisen": 27, "pech": 0, "apfel": 3, "fleisch": 1, "gold": 1}   # gemessen 05.10. (Liga)
LOS = {"holz": 20}                       # Stueck je Verkauf; alles andere 5 (gemessen 05.10.)
NAHRUNG = ("apfel", "fleisch")
# Typ: (Ware, Startwert je 1000 Ticks, Messweg d0, Gewicht = gemessene Ticks, Anlauf-Startwert, Arbeiter, Ziel)
# Lange Messpartie 05.10. 19:28 (20.000 Ticks, je ein Betrieb); Stein dort ab ~12.000 vom vollen Lagerteil gedeckelt,
# darum Stein aus der ersten Messpartie (8.000 Ticks, erste Lieferung 3.750).
START = {
    5:  ("eisen", 0.588, 31, 60000, 3800, 2, "lager"),  # 08.10.: 0,584-0,591 bei 8-91 Feldern, Weg nicht begrenzend
    20: ("stein", 4.7, 8, 70000, 4000, 5, "lager"),     # 08.10.: Steinbruch + 2 Joche (3 + 2 Arbeiter)
    32: ("apfel", 2.2, 5, 18500, 1500, 1, "kornspeicher"),
    7:  ("fleisch", 5.5, 53, 15000, 5000, 1, "kornspeicher"),
    3:  ("holz", 5.4, 6, 16000, 4000, 1, "lager"),
}
NAME = {5: "Eisenmine", 20: "Steinbruch+Ochsenjoch", 32: "Apfelplantage", 7: "Jaegerhuette", 3: "Holzfaeller"}
JE_TEIL = 48
BAUM_FREI = 7           # ein Baum gilt als vergeben, wenn ein eigener Holzfaeller naeher steht
WALD_R, WALD_JE_HUETTE = 15, 12   # 12.10. Waldgrenze (abgeleitet, 2 Waelder) - Stellgroessen
SIGNAL_GUT = (0.7, 1.3)  # abgegebene Ladung / gebuchter Zugang, in dem die Abgaben einer Art als sichtbar gelten
SIGNAL_AB = 20           # ab so viel gebuchtem Zugang wird die Gegenprobe ausgewertet



def startwerte_aus_partien(dateien):
    """Startwerte aus den gelernten Werten frueherer Partien (daten/ertrag_gelernt_*.json, gleicher Planer-Stand):
    Rate = Mittel der gemessenen Raten auf d0; Gewicht = Median der gewichteten Betriebs-Ticks EINER Partie (eine fruehere
    Partie zaehlt wie eine Partie, sonst lernte die laufende nichts mehr); Anlauf = Mittel, nur wo im Spiel gemessen."""
    import statistics
    sammel = {}
    for f in dateien:
        d = json.load(open(f, encoding="utf-8"))
        for art, v in d["gelernt"].items():
            typ = next(t for t, n in NAME.items() if n == art)
            e = sammel.setdefault(typ, {"rate": [], "gewicht": [], "anlauf": []})
            e["rate"].append(v["gemessen_je_1000_auf_d0"])
            e["gewicht"].append(v["gewichtete_ticks"])
            if v["anlauf_quelle"] != "Startwert":
                e["anlauf"].append(v["anlauf"])
    return {typ: {"rate": round(statistics.mean(e["rate"]), 3), "gewicht": round(statistics.median(e["gewicht"])),
                  "anlauf": round(statistics.mean(e["anlauf"])) if e["anlauf"] else None, "partien": len(e["rate"])}
            for typ, e in sammel.items()}


def startwerte_laden(pfad):
    """Ersetzt Rate, Gewicht und (falls gemessen) Anlauf in START. Gibt Text fuer das Protokoll."""
    if not os.path.exists(pfad):
        return "keine Startwerte-Datei (%s) - Messpartie-Werte" % os.path.basename(pfad)
    w = json.load(open(pfad, encoding="utf-8"))
    teile = []
    for typ_s, v in w["werte"].items():
        typ = int(typ_s)
        ware, r0, d0, gew, anl, arb, ziel = START[typ]
        START[typ] = (ware, v["rate"], d0, v["gewicht"], v["anlauf"] or anl, arb, ziel)
        teile.append("%s %.2f (Gewicht %d, Anlauf %d)" % (NAME[typ], v["rate"], v["gewicht"], v["anlauf"] or anl))
    return "Startwerte aus %d frueheren Partien: %s" % (w["partien"], "; ".join(teile))


def lies_baukosten(typen):
    """Baukosten aus dem laufenden Spiel (erst nach Kartenstart gefuellt). Gibt typ -> {holz, stein, eisen, pech, gold}."""
    return {t: dict(zip(KOSTEN_WAREN, peek(KOSTEN_ADR + t * 20, 5))) for t in typen}

def gold_wert(kosten):
    return sum(VERKAUF[w] * kosten.get(w, 0) for w in KOSTEN_WAREN)


MAX_LAGERTEILE = 8                 # 2 Lagerplaetze zu je 4 Teilen (Daniel 06.10. 21:11)
MAX_AMORT = 6000                   # ohne Partieende nichts mit laengerer Amortisation (v3, 21:20)
STEUER_MIN = 0                     # Bestechung erlaubt (Liga Stufe 0: +225 Beliebtheit, 1,50 Gold je Kopf)


class Ertragsmesser:
    """Buchfuehrung je Ware und Lernwerte je Gebaeudeart (Kopf, Teil 1)."""

    def __init__(self, sp, kosten, groesse, protokoll=None):
        self.sp, self.kosten, self.groesse = sp, kosten, groesse
        self.zugang = {t: 0.0 for t in START}
        self.zeit = {t: 0.0 for t in START}          # gewichtete Betriebs-Ticks mit laufender Uhr
        self.besetzt_zeit = {t: 0.0 for t in START}  # ungewichtet, nur zur Anzeige
        self.gesehen = {}                            # Gebaeude-Nr -> erster beobachteter Tick
        self.beim_start = set()                      # Gebaeude, die bei der ersten Beobachtung schon standen
        self.erst_abgabe = {}                        # Gebaeude-Nr -> Tick der ersten Abgabe seines Arbeiters
        self.anlaeufe = {t: [] for t in START}       # Bau -> erste Abgabe, nur neu gebaute Betriebe
        self.uhr = {t: {} for t in START}            # Gebaeude-Nr -> "abgabe" | "alter" (womit seine Uhr startete)
        self.ladung_max = {}                         # groesste getragene Ladung je Art (= eine Lieferung)
        self.abgaben = {}                            # Art -> abgegebene Ladung (Gegenprobe)
        self.abgaben_einheit = {}                    # "Einheit@Art" -> abgegebene Ladung (zur Anzeige)
        self.typ_besetzt, self.typ_geliefert, self.vorher = {}, {}, set()
        self.vor, self.verk, self.runden, self.letzter = None, {}, 0, {}
        self.neg = {w: [0, 0.0] for w in ("holz", "stein", "eisen")}
        self.ladung_vor = {}
        self.f = open(protokoll, "w", encoding="utf-8") if protokoll else None

    def verkauft(self, ware, lose=1):
        self.verk[ware] = self.verk.get(ware, 0) + lose * LOS.get(ware, 5)

    def wegfaktor(self, typ, d):
        if typ == 5:                         # Eisen: Bergmann begrenzt; 8-91 Felder lieferten gleich viel (L40)
            return 1.0
        return (START[typ][2] + 20.0) / (d + 20.0)

    def signal(self, typ):
        """Gegenprobe: abgegebene Ladung / gebuchter Zugang. None, solange zu wenig Zugang."""
        if self.zugang[typ] < SIGNAL_AB:
            return None
        return self.abgaben.get(typ, 0) / self.zugang[typ]

    def anlauf(self, typ):
        q = self.signal(typ)
        a = sorted(self.anlaeufe[typ])
        if a and q is not None and SIGNAL_GUT[0] <= q <= SIGNAL_GUT[1]:
            return a[len(a) // 2], "gemessen an %d Betrieben" % len(a)
        if typ in self.typ_geliefert and typ in self.typ_besetzt and typ not in self.vorher:
            return self.typ_geliefert[typ] - self.typ_besetzt[typ], "gemessen an der Art"
        return START[typ][4], "Startwert"

    def rate(self, typ):
        """Ertrag je 1.000 Ticks auf dem Messweg d0: Startwert mit seinem Gewicht, dazu die Messung im Spiel."""
        r0, gew = START[typ][1], START[typ][3]
        zaunpfahl = self.ladung_max.get(typ, 0) * sum(1 for nr in self.uhr[typ] if nr in self.erst_abgabe)
        return (r0 * gew + 1000.0 * max(0.0, self.zugang[typ] - zaunpfahl)) / (gew + self.zeit[typ])

    def beobachte(self, st, L, G, ziele):
        """ziele: typ -> Liste Zielorte (Lager bzw. Kornspeicher). Einmal je Runde, VOR Verkaufen und Bauen."""
        t = st.get("t", 0)
        erste = self.vor is None
        for n, g in G.items():
            if g["besitzer"] == self.sp and n not in self.gesehen:
                self.gesehen[n] = t
                if erste:
                    self.beim_start.add(n)
        besetzt = {}
        for nr, e in L.items():
            if e["besitzer"] != self.sp:
                continue
            lv, jetzt = self.ladung_vor.get(nr, 0), e.get("ladung", 0)
            self.ladung_vor[nr] = jetzt
            ap = e.get("arbeitsplatz")
            g = G.get(ap) if ap else None
            if not g or g["besitzer"] != self.sp or g["typ"] not in START:
                continue
            typ = g["typ"]
            besetzt.setdefault(typ, set()).add(ap)
            if jetzt > self.ladung_max.get(typ, 0):
                self.ladung_max[typ] = jetzt
            if lv > 0 and jetzt == 0:                       # Abgabe
                self.abgaben[typ] = self.abgaben.get(typ, 0) + lv
                k = "%d@%d" % (e["typ"], typ)
                self.abgaben_einheit[k] = self.abgaben_einheit.get(k, 0) + lv
                if ap not in self.erst_abgabe:
                    self.erst_abgabe[ap] = t
                    if ap not in self.beim_start and ap in self.gesehen:
                        self.anlaeufe[typ].append(t - self.gesehen[ap])
        gewicht = {}
        for typ, nrs in besetzt.items():
            if typ not in self.typ_besetzt:
                self.typ_besetzt[typ] = t
                if erste:
                    self.vorher.add(typ)
            anl = self.anlauf(typ)[0]
            s = 0.0
            for nr in nrs:
                if nr not in self.uhr[typ]:
                    if nr in self.erst_abgabe:
                        self.uhr[typ][nr] = "abgabe"
                    elif t - self.gesehen.get(nr, t) >= anl:
                        self.uhr[typ][nr] = "alter"
                    else:
                        continue
                g = G[nr]
                b = self.groesse.get(typ, 2) // 2
                s += self.wegfaktor(typ, min(schach((g["x"] + b, g["y"] + b), z) for z in ziele[typ]))
            gewicht[typ] = s
        zug = {}
        if not erste:
            t0, w0, g0, gew0, bes0 = self.vor
            dt = t - t0
            if dt > 0:
                self.runden += 1
                gebaut = {w: 0 for w in KOSTEN_WAREN}
                for k, v in st.items():
                    if k.startswith("G") and k[1:].isdigit() and v > g0.get(k, 0):
                        for w in KOSTEN_WAREN:
                            gebaut[w] += (v - g0.get(k, 0)) * self.kosten.get(int(k[1:]), {}).get(w, 0)
                for typ, (ware, *_r) in START.items():
                    roh = st.get(ware, 0) - w0.get(ware, 0) + self.verk.get(ware, 0) + gebaut.get(ware, 0)
                    if ware in NAHRUNG:
                        roh = max(0, roh)
                    elif roh < 0:
                        self.neg[ware][0] += 1
                        self.neg[ware][1] += -roh
                    zug[ware] = roh
                    self.zugang[typ] += roh
                    self.zeit[typ] += gew0.get(typ, 0.0) * dt
                    self.besetzt_zeit[typ] += bes0.get(typ, 0) * dt
                    if roh > 0 and typ in self.typ_besetzt and typ not in self.typ_geliefert:
                        self.typ_geliefert[typ] = t
                if self.f:
                    self.f.write(json.dumps({"t": t, "dt": dt, "zug": zug, "verk": self.verk, "gebaut": {k: v for k, v in gebaut.items() if v},
                                             "besetzt": {NAME[k]: len(v) for k, v in besetzt.items()},
                                             "gewicht": {NAME[k]: round(v, 2) for k, v in gewicht.items()}}, ensure_ascii=False) + "\n")
                    self.f.flush()
        g_now = {k: v for k, v in st.items() if k.startswith("G") and k[1:].isdigit()}
        self.vor = (t, {w: st.get(w, 0) for w in ("holz", "stein", "eisen", "apfel", "fleisch")}, g_now, gewicht,
                    {k: len(v) for k, v in besetzt.items()})
        self.letzter = g_now
        self.verk = {}
        return zug

    def stand(self):
        aus = {}
        for typ, (ware, r0, d0, gew, *_r) in START.items():
            anl, quelle = self.anlauf(typ)
            q = self.signal(typ)
            aus[NAME[typ]] = {"startwert": r0, "startgewicht": gew, "gemessen_je_1000_auf_d0": round(self.rate(typ), 2),
                              "zugang": round(self.zugang[typ], 1), "lieferung": self.ladung_max.get(typ),
                              "uhr_ab_abgabe": sum(1 for w in self.uhr[typ].values() if w == "abgabe"),
                              "uhr_ab_alter": sum(1 for w in self.uhr[typ].values() if w == "alter"),
                              "betriebs_ticks": round(self.besetzt_zeit[typ]), "gewichtete_ticks": round(self.zeit[typ]),
                              "gegenprobe": None if q is None else round(q, 2), "anlauf": anl, "anlauf_quelle": quelle,
                              "anlaeufe": sorted(self.anlaeufe[typ]), "lief_beim_start": typ in self.vorher}
        return aus

    def bericht(self):
        teile = ["%s %.2f->%.2f (Zugang %.0f, Lieferung %s, Gegenprobe %s, Anlauf %d %s)" % (
            n, v["startwert"], v["gemessen_je_1000_auf_d0"], v["zugang"], v["lieferung"], v["gegenprobe"], v["anlauf"], v["anlauf_quelle"])
            for n, v in self.stand().items()]
        neg = "; ".join("%s %d von %d Runden, Summe %.0f" % (w, n, self.runden, s) for w, (n, s) in self.neg.items())
        return "Ertragsmesser: %s | negative Zugaenge: %s | abgegebene Ladung je Einheit@Art: %s" % (
            "; ".join(teile), neg, self.abgaben_einheit)


class Ertragsplaner:
    PLANEN = 10

    def __init__(self, plan, sp, baue_schnell, wirt, steuerstufe, ende=None, kosten=None, groesse=None, protokoll=None, wegtest=None):
        self.sp, self.plan, self.baue, self.wirt, self.ende = sp, plan, baue_schnell, wirt, ende
        # Daniel 05.10. 20:50: "deine Holzfaeller sind in einer unzugehbaren Position - nirgends bauen, wo es nicht begehbar ist"
        # (Bild: Holzfaeller jenseits des Flusses). Platzkarte = darf man bauen; Wegtest (Wegfinder des Spiels, setDestinationForUnit,
        # Gegenprobe 05.10.: Wasser 2/2 kein Weg) = kommt man hin. Ergebnis je Punkt gemerkt.
        self.wegtest, self.erreichbar_ok, self.unerreichbar = wegtest, set(), set()
        self.K = tuple(plan.get("bergfried_eingang", (165, 111)))
        d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
        kurz = plan["start"]
        info = json.load(open(os.path.join(d, "start_%s.json" % kurz), encoding="utf-8"))
        self.feinde = [tuple(v["eingang"]) for v in info["feind_bergfried"].values()]
        self.startwerte = startwerte_laden(os.path.join(d, "ertrag_startwerte_%s.json" % kurz))
        self.kosten = kosten if kosten is not None else lies_baukosten((1, 3, 4, 5, 7, 10, 19, 20, 31, 32))
        if groesse is None:
            from bauen import NACH_TYP
            groesse = {t: NACH_TYP[t]["b"] for t in (1, 3, 4, 5, 7, 10, 19, 20, 31, 32)}
        self.groesse = groesse
        self.messer = Ertragsmesser(sp, self.kosten, groesse, protokoll)
        from farmen_mischen import lies_karte
        self.platz = {}
        # 12.10.: Hopfenfarm (31, 9x9) auf den Plaetzen der Apfelplantage (10x10) - was 10x10 fasst, fasst 9x9
        for typ, name in ((5, "eisenmine"), (20, "steinbruch"), (32, "apfel"), (3, "holzfaeller"), (31, "apfel")):
            pfad = os.path.join(d, "start_%s_platz_%s.txt" % (kurz, name))
            self.platz[typ] = [p for p in lies_karte(pfad) if self.eigene_seite(p)] if os.path.exists(pfad) else []
        # Holzfaeller: je Baum der naechste gueltige Platz (einmal vorberechnet)
        baeume = []
        self.baeume_faellbar = baeume      # 12.10.: fuer die Waldgrenze (WALD_JE_HUETTE)
        for w in open(os.path.join(d, "baeume_%s.txt" % kurz)).read().splitlines()[1:]:
            w = w.split()
            if len(w) >= 7 and w[2] == "2" and int(w[5]) < 4 and int(w[6]) > 0 and self.eigene_seite((int(w[3]), int(w[4]))):
                baeume.append((int(w[3]), int(w[4])))
        hp = set(self.platz[3])
        self.baum_platz, self.baum_plaetze = {}, {}
        for b in baeume:
            nah = [(b[0] + dx, b[1] + dy) for dx in range(-4, 2) for dy in range(-4, 2) if (b[0] + dx, b[1] + dy) in hp]
            if nah:
                self.baum_platz[b] = min(nah, key=lambda p: schach((p[0] + 1, p[1] + 1), b))
                # v17: ALLE gueltigen Huettenplaetze, deren Mitte hoechstens 3 Felder vom Baum liegt (mehrere Holzfaeller je Baum)
                self.baum_plaetze[b] = sorted(nah, key=lambda p: schach((p[0] + 1, p[1] + 1), b))
        self.huetten_je_baum = None      # v17 (Daniel 22:57: "pro Baum beliebig viele Holzfaeller") - None = alte Regel (BAUM_FREI)
        self.steuer, self.steuer_runde = steuerstufe, -99
        self.braucht_gold, self.letzte_wahl, self.gesetzt = False, None, {}
        self.fehlschlag, self.abgelehnt, self.verstoss = {}, {}, []
        self.stein_reserve = 0
        self.haufen, self.joch_bestellt, self.joch_beladen = {}, {}, set()
        self.joch_bestell_tick, self.joch_ladung_vor = {}, {}
        self.joch_bruch, self.joch_lieferung, self.joch_stau = {}, {}, {}

    def eigene_seite(self, p):
        d = schach(p, self.K)
        return all(d < schach(p, f) for f in self.feinde)

    def kosten_von(self, typ):
        k = dict(self.kosten[typ])
        if typ == 20:                         # gemessen 08.10.: fuer die Zielzeit zwei Joche je Bruch rechnen
            for w in KOSTEN_WAREN:
                k[w] += 2 * self.kosten[4][w]
        return k

    # ---- Ziele und Plaetze ----------------------------------------------------------------------------------------
    def ziele(self, G):
        eigen = [(n, g) for n, g in G.items() if g["besitzer"] == self.sp]
        lager = [(g["x"] + 2, g["y"] + 2) for n, g in eigen if g["typ"] == 10 and n not in self.wirt.alt] or [tuple(self.plan["lager"])]
        speicher = [(g["x"] + 2, g["y"] + 2) for n, g in eigen if g["typ"] == 19] or [tuple(self.plan["kornspeicher"])]
        return {t: (lager if START[t][6] == "lager" else speicher) for t in START}

    def _orte(self, typ, L, G):
        """Kandidaten-Orte ohne gesperrte Flaechen (v14: Steinbrueche, Joche, Lager + Erweiterung, Hoefe, Gerberei,
        Waffenlager haben feste Plaetze - v12/v13 setzte der Planer einen Steinbruch auf (81,268) und nahm beiden den Platz)."""
        orte = self._orte_roh(typ, L, G)
        # 19.10. (gefahrenzone.py): frische eigene Verluste sperren ihren Umkreis fuer neue Betriebe mit
        sperr = list(getattr(self, "sperr", None) or []) + list(getattr(self, "gefahr", None) or [])
        if not sperr:
            return orte
        b = self.groesse.get(typ, 3)
        return [p for p in orte if not any(p[0] <= r[2] and p[0] + b - 1 >= r[0] and p[1] <= r[3] and p[1] + b - 1 >= r[1]
                                           for r in sperr)]

    @staticmethod
    def _dicht_packen(orte, b):
        """Steinbruch/Eisenmine (Daniel 23:24 "warum nur einen Steinbruch, wenn 2 moeglich sind?"): nur Plaetze, nach denen auf
        demselben Rohstofffeld die meisten weiteren Bauten derselben Art noch passen (gierige Packung der uebrigen Plaetze).
        Vorher nahm der Planer (81,268) mitten im Steinfeld - danach passte dort keiner mehr (v12, Lernlauf 3)."""
        if not orte:
            return orte
        # 18.10. (Profil Probepartie: 114 von 207 s hier, 82 Mio. Abstandsrechnungen in 70 Runden): Nachbarn nur aus den
        # umliegenden Rasterzellen (Zelle 3b), Ergebnis je gleicher Platzliste gemerkt. Ergebnis gleich (Vergleich alt/neu).
        schl = (b, tuple(orte))
        if schl in _PACK_MERK:
            return list(_PACK_MERK[schl])
        zelle = 3 * b
        gitter = {}
        for x in orte:
            gitter.setdefault((x[0] // zelle, x[1] // zelle), []).append(x)

        def nachbarn(p, r):
            cx, cy = p[0] // zelle, p[1] // zelle
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for x in gitter.get((cx + dx, cy + dy), ()):
                        if max(abs(x[0] - p[0]), abs(x[1] - p[1])) <= r:
                            yield x

        def packung(p):
            gew = [p]
            for q in sorted(nachbarn(p, 3 * b)):
                if all(max(abs(q[0] - g[0]), abs(q[1] - g[1])) >= b for g in gew):
                    gew.append(q)
            return len(gew)
        wert = {p: packung(p) for p in orte}
        aus = [p for p in orte if wert[p] >= max(wert[q] for q in nachbarn(p, 2 * b))]
        if len(_PACK_MERK) > 64:
            _PACK_MERK.clear()
        _PACK_MERK[schl] = tuple(aus)
        return aus

    def _orte_roh(self, typ, L, G):
        """Kandidaten-Orte fuer typ (Ankerpunkte)."""
        eigen = [g for g in G.values() if g["besitzer"] == self.sp]
        gleich = [(g["x"], g["y"]) for g in eigen if g["typ"] == typ]
        b = self.groesse.get(typ, 3)
        # v17: bei mehreren Holzfaellern je Baum sperrt ein Fehlschlag nur seinen eigenen Platz, nicht 8 Felder rundum
        sperr_r = 0 if (typ == 3 and self.huetten_je_baum) else 8
        gesperrt = lambda p: any(t == typ and schach(p, q) <= sperr_r for (t, q) in self.fehlschlag)
        # v18 (Daniel 23:10 "Holzfaeller sollten alle zugaenglich sein"): Holzfaeller-Huetten mit 1 Feld Gang zueinander
        abstand = b + 1 if (typ == 3 and self.huetten_je_baum) else b
        frei = lambda p: all(schach(p, q) >= abstand for q in gleich) and not gesperrt(p)
        if typ in (5, 20, 32, 31):
            orte = [p for p in self.platz[typ] if frei(p)]
            if typ == 32 and self.wirt.B_offen:
                # Seasoning (v2b, B23): der Planer setzte vor der A-Reife eigene Plantagen auf/neben die B-Plaetze -
                # 2 von 3 B fanden danach keinen Platz, B blieb die ganze Partie offen. B-Plaetze bleiben frei, bis B steht.
                orte = [p for p in orte if all(schach(p, b) > 6 for b in self.wirt.B_offen)]
            if typ in (20, 5):
                orte = self._dicht_packen(orte, b)
            return orte
        if typ == 3:
            hf = [(x + 1, y + 1) for (x, y) in gleich]
            # 12.10. Waldgrenze (L69/L71, abgeleitet aus 2 Waeldern: 19-24 Baeume hielten 1 Huette 18.000 Ticks, 8 Baeume
            # waren unter 2 Huetten nach 12.000 Ticks fast leer): ein Platz nur, wenn im Umkreis WALD_R mindestens
            # WALD_JE_HUETTE faellbare Baeume je Huette (bestehende + diese) stehen
            wald = lambda p: sum(1 for b_ in self.baeume_faellbar if schach(b_, (p[0] + 1, p[1] + 1)) <= WALD_R)
            haelt = lambda p: wald(p) >= WALD_JE_HUETTE * (1 + sum(1 for h in hf if schach(h, (p[0] + 1, p[1] + 1)) <= WALD_R))
            if self.huetten_je_baum:
                # v17: ein Baum nimmt bis zu K Huetten (Daniel 22:57) statt "vergeben, sobald ein Holzfaeller 7 Felder nah steht"
                # (die alte Regel sperrte so auch alle Nachbarbaeume - am neuen Lager blieben 5 Holzfaeller fuer ~400 Holz)
                aus = set()
                for baum, plaetze in self.baum_plaetze.items():
                    if sum(1 for h in hf if schach(baum, h) <= 4) < self.huetten_je_baum:
                        aus.update(p for p in plaetze if frei(p) and haelt(p))
                return list(aus)
            return list({p for baum, p in self.baum_platz.items()
                         if all(schach(baum, h) > BAUM_FREI for h in hf) and frei(p) and haelt(p)})
        rehe = [(e["x"], e["y"]) for e in L.values() if e["typ"] == 44 and e["besitzer"] == 0 and self.eigene_seite((e["x"], e["y"]))]
        # Saettigung (v2b, B22: 59 Jaegerhuetten, meist an derselben Herde): je Huette 5 Rehe im Umkreis 15,
        # bestehende Jaegerhuetten im Umkreis mitgezaehlt
        return [p for p in rehe if sum(1 for q in rehe if schach(p, q) <= 15) >= 5 * (1 + sum(1 for h in gleich if schach(p, h) <= 15))
                and frei(p)]

    # ---- Kandidaten -----------------------------------------------------------------------------------------------
    def _bester_ort(self, typ, L, G, zl=None):
        """Naechster erreichbarer Bauplatz dieser Art zu ihrem Ziel (Lager, Kornspeicher ...): (ort, weg) oder (None, None)."""
        zl = zl or self.ziele(G)
        orte = self._orte(typ, L, G)
        if not orte:
            return None, None
        b = self.groesse.get(typ, 2) // 2
        weg = lambda p: min(schach((p[0] + b, p[1] + b), z) for z in zl[typ])
        # Schachbrett-Abstand allein erzeugt bei Eisenminen viele Gleichstaende. Dann soll
        # nicht die zufaellige Reihenfolge der Platzkarte entscheiden, sondern die wirklich
        # kuerzere Luftlinie zum Lager.
        luft = lambda p: min((p[0] + b - z[0]) ** 2 + (p[1] + b - z[1]) ** 2 for z in zl[typ])
        schluessel = (lambda p: (weg(p), luft(p))) if typ == 5 else weg
        ort = self._erreichbarer(sorted(orte, key=schluessel), L)
        return (ort, weg(ort)) if ort is not None else (None, None)

    def holzfaeller_statt_verkauf(self, st, L, G):
        """Daniel 06.10.: \"statt Holz verkaufen einfach mehr Holzfaeller, weil Holz kann man spaeter immer brauchen\".
        Baut EINEN Holzfaeller am besten Platz, wenn das Holz ueber der B-Ruecklage reicht und ein Arbeiter am Feuer frei
        ist. Gibt (ort, text): ort None -> das Holz bleibt liegen (verkauft wird es nicht mehr)."""
        k = self.kosten_von(3)
        R = self.wirt.ruecklage(G)
        if st.get("holz", 0) - R["holz"] < k["holz"] or st.get("gold", 0) - R["gold"] < k["gold"]:
            return None, "Holz/Gold reicht nach B-Ruecklage nicht"
        if st.get("feuer", 0) < 1:
            return None, "kein freier Arbeiter am Feuer"
        if 3 in getattr(self, "ohne", ()):
            # v15: Holzfaeller bekommen ihre Arbeiter VOR den Steinbruechen (gemessen 06.10. 22:35, Tick 822-1.442: 12 neue
            # Arbeiter, alle zu Holzfaellern, Steinbrueche 0/6) - erst die Steinbrueche besetzen
            return None, "Holzfaeller warten, bis die Steinbrueche besetzt sind"
        # Auf den besten Bau sparen (Daniel 21:52: "entweder fehlen ihm Informationen oder er nutzt sie nicht"): fehlt dem
        # zuletzt gewaehlten besten Bau Holz, darf dieser Holzfaeller es nicht verbauen (v9: Steinbruch wartete 8x auf 3-8 Holz)
        b = self.letzte_wahl
        if b and b["typ"] != 3 and st.get("holz", 0) - R["holz"] - k["holz"] < b["kosten"]["holz"]:
            return None, "Holz fuer %s zurueckgehalten" % NAME[b["typ"]]
        ort, w = self._bester_ort(3, L, G)
        if ort is None:
            return None, "kein erreichbarer Holzfaeller-Platz"
        if getattr(self, "holz_max", None) is not None and w > self.holz_max:
            return None, "naechster Holzfaeller-Platz %d Felder vom Lager (Grenze %d)" % (w, self.holz_max)
        gebaut = self.baue(3, ort[0], ort[1], 3)
        if gebaut:
            self.gesetzt["Holzfaeller statt Verkauf"] = self.gesetzt.get("Holzfaeller statt Verkauf", 0) + 1
        else:
            # wie der Hauptweg: gescheiterten Platz merken, _orte sperrt ihn (holz_partie_1: 1.009 Versuche an (87, 231))
            self.fehlschlag[(3, ort)] = self.fehlschlag.get((3, ort), 0) + 1
        return gebaut, "Platz %s, Weg %d" % (ort, w)

    def kandidaten(self, st, L, G):
        """Alle Arten an ihrem besten Ort, mit Horizont-Pruefung. Sortiert nach Gewinn bis Partieende (ohne Ende: Amortisation)."""
        t = st.get("t", 0)
        rest = (self.ende - t) if self.ende else None
        zl = self.ziele(G)
        aus = []
        for typ, (ware, _r0, _d0, _g, _a, arb, _z) in START.items():
            if typ in getattr(self, "ohne", ()):         # v14: Steinbrueche baut die Pflicht an festen Plaetzen
                continue
            ort, w = self._bester_ort(typ, L, G, zl)
            if ort is None:
                continue
            if w > 70:
                continue
            if typ == 3 and getattr(self, "holz_max", None) is not None and w > self.holz_max:
                continue                     # v16: Holzfaeller weit vom Lager liefern ~3 statt ~11 je 1.000 Ticks (L9)
            rate = self.messer.rate(typ) * self.messer.wegfaktor(typ, w)
            gold_je_tick = rate * VERKAUF[ware] / 1000.0
            k = self.kosten_von(typ)
            amort = gold_wert(k) / gold_je_tick if gold_je_tick > 0 else 10 ** 9
            anl, _q = self.messer.anlauf(typ)
            gewinn = gold_je_tick * (rest - anl) - gold_wert(k) if rest is not None else None
            grund = None
            if rest is not None and anl + amort > rest:
                grund = "Horizont (Anlauf %d + Amortisation %.0f > Rest %d)" % (anl, amort, rest)
            elif rest is None and amort > MAX_AMORT:
                # ohne Partieende baute er alles, was sich irgendwann bezahlt (v3: 25 Jaegerhuetten mit 10.000-18.800 Ticks)
                grund = "Amortisation %.0f > %d" % (amort, MAX_AMORT)
            aus.append({"typ": typ, "ort": ort, "weg": w, "gold_je_1000": round(1000 * gold_je_tick, 1), "amort": amort,
                        "gewinn": gewinn, "anlauf": anl, "rest": rest, "kosten": k, "arbeiter": arb, "grund": grund})
        if getattr(self, "je_arbeiter", False):
            # v16 (06.10. 22:55): Bauern sind der Engpass (1 je 52 Ticks, L7) - Gewinn je ARBEITER entscheidet, nicht je Bau
            if rest is None:
                return sorted(aus, key=lambda k: k["amort"] * max(1, k["arbeiter"]))
            return sorted(aus, key=lambda k: -k["gewinn"] / float(max(1, k["arbeiter"])))
        if rest is None:
            return sorted(aus, key=lambda k: k["amort"])
        return sorted(aus, key=lambda k: -k["gewinn"])

    def _erreichbarer(self, orte, L):
        """Der erste der besten Orte, zu dem unser Lord einen Weg hat (ein Modulaufruf fuer bis zu 8 neue Punkte)."""
        if not self.wegtest:
            return orte[0] if orte else None
        # erst die Verworfenen herausnehmen, DANN die naechsten 8 (Daniel 22:29: "sie findet kein Holz? auf einer Karte voll
        # mit Baeumen? ... das ist ein Berechnungsfehler"): vorher orte[:16] zuerst geschnitten - waren die 16 naechsten
        # verworfen, blieb die Probe leer und es hiess fuer immer "kein erreichbarer Holzfaeller-Platz" (v11, v14: 16 verworfen)
        probe = [p for p in orte if p not in self.unerreichbar][:8]
        neu = [p for p in probe if p not in self.erreichbar_ok]
        if neu:
            lord = next((n for n, e in L.items() if e["typ"] == 55 and e["besitzer"] == self.sp), None)
            if lord is None:
                return probe[0] if probe else None
            for p, ok in zip(neu, self.wegtest(lord, neu)):
                (self.erreichbar_ok if ok else self.unerreichbar).add(p)
        return next((p for p in probe if p in self.erreichbar_ok), None)

    def erreichbare(self, orte, L, n=4):
        """Bis zu n Orte aus der Rangfolge, zu denen der Wegtest des Spiels einen Weg findet (Daniel 08.10. 00:08, Bild:
        Holzfaeller jenseits des Flusses mit rotem Zeichen - der Kausal-Weg nahm die naechsten 4 Plaetze ohne Wegtest;
        Lauf s25/5: 21 Huetten bei x 8-54 nie besetzt)."""
        if not self.wegtest:
            return list(orte)[:n]
        kand = [p for p in orte if p not in self.unerreichbar]
        aus, proben, lord = [], 0, None
        for i in range(0, len(kand), 8):                     # Bloecke zu 8 Punkten = ein Modulaufruf
            block = kand[i:i + 8]
            neu = [p for p in block if p not in self.erreichbar_ok]
            if neu:
                if proben >= 3:                              # hoechstens 3 neue Wegtests je Aufruf (Rundenzeit)
                    break
                lord = lord or next((k for k, e in L.items() if e["typ"] == 55 and e["besitzer"] == self.sp), None)
                if lord is None:
                    return block[:n]
                for q, ok in zip(neu, self.wegtest(lord, neu)):
                    (self.erreichbar_ok if ok else self.unerreichbar).add(q)
                proben += 1
            aus += [q for q in block if q in self.erreichbar_ok][:n - len(aus)]
            if len(aus) >= n:
                break
        return aus

    def reserve(self):
        """Was nicht verkauft werden darf (Daniel 19:44: Stein bis auf den Bedarf der geplanten Eisenmine)."""
        return {"stein": self.stein_reserve}

    # ---- jede Runde -----------------------------------------------------------------------------------------------
    def beobachte(self, st, L, G):
        # Ochsen intern verfolgen: Aufnahme ordnet das Joch anhand der echten Ochsenposition dem naechsten Steinhaufen
        # zu; ein Ladungsabfall ist eine echte Ablieferung. Nur "Joch steht" reichte nicht, weil dann trotz liegendem
        # Stein tote oder falsch zugeordnete Transporte als Leistung galten.
        brueche = {n: g for n, g in G.items() if g["besitzer"] == self.sp and g["typ"] == 20}
        haufen = {}
        for n, g in brueche.items():
            h = G.get(g.get("verbund") or -1)
            haufen[n] = ((h["x"], h["y"]) if h else (g["x"] + 7, g["y"] + 2))
        for e in L.values():
            ap = e.get("arbeitsplatz")
            if e["besitzer"] != self.sp or not ap or G.get(ap, {}).get("typ") != 4:
                continue
            jetzt, vorher = e.get("ladung", 0), self.joch_ladung_vor.get(ap, 0)
            if jetzt > vorher and brueche:
                n = min(haufen, key=lambda q: schach((e["x"], e["y"]), haufen[q]))
                self.joch_bruch[ap] = n
                self.joch_beladen.add(ap)
            if vorher > jetzt:
                self.joch_lieferung[ap] = (st.get("t", 0), vorher - jetzt)
            self.joch_ladung_vor[ap] = jetzt
        return self.messer.beobachte(st, L, G, self.ziele(G))

    def schritt(self, st, L, G, runde):
        # ab Runde 1, dann alle PLANEN Runden (bis 05.10. 20:55 erst ab Runde 10: Lauf l1 plante zum ersten Mal bei Tick
        # 1.634, geladen war Tick 729 - Daniel: "waehrend du noch wartest, hat Rotkaeppchen schon laengst angefangen")
        if (runde - 1) % self.PLANEN:
            return []
        ev = []
        # Seasoning-B hat beim Gold Vorrang - aber erst, wenn A reif und B dran ist (bremse_2: B war die ganze Partie
        # "offen", weil A spaeter kommt; braucht_gold stand immer auf True, in 28.700 Ticks nur 1 Assassine)
        self.braucht_gold = bool(self.wirt.B_offen) and self.wirt.A_reif_tick is not None
        eigen = [dict(g, nr=n) for n, g in G.items() if g["besitzer"] == self.sp]
        holz, stein, gold = st.get("holz", 0), st.get("stein", 0), st.get("gold", 0)
        # Steuern nach Beliebtheit (Regel bleibt, bis der Planer sie mitrechnet)
        bel = st.get("beliebt", 0) / 100.0
        if runde - self.steuer_runde >= 2 * self.PLANEN and not getattr(self, "steuer_extern", False):   # kasse=haushalt: haushalt.py
            # Untergrenze 0 statt 3 (Daniel 21:13, B17: "Beliebtheit wirklich ueber 95 halten, damit die Bevoelkerung schnell
            # genug nachkommt" - v2b fiel bei Stufe 3 auf 59, dann 38): unter 95 bis zur Bestechung herunter
            # Lernkreis (Daniel 23:53 "machen Steuern nochmal gut Geld?"): Schwelle zum Senken ist ein Knopf (steuer_runter)
            runter = getattr(self, "steuer_runter", 95)
            neu = self.steuer + 1 if (bel >= runter + 2 and self.steuer < 8 and st.get("leute", 0) >= 15) else self.steuer - 1 if (bel < runter and self.steuer > STEUER_MIN) else self.steuer
            ende = getattr(self, "steuer_ende", "nein")
            wohnraum_voll = st.get("platz", 0) > 0 and st.get("leute", 0) >= st.get("platz", 0)
            # "wohnraum" (Daniel 07.10. 00:04 "ja, ab vollem Wohnraum Hoechststeuer testen"): voller Wohnraum = kein Zuzug
            # moeglich, Beliebtheit bringt dann nichts - Stufe 11, bis wieder Platz frei ist (neue Huette) oder unter 55
            if getattr(self, "nach_abriss", False):
                # Lauf 43: nach dem Endspiel-Abriss 7 Kaempfer, dann fehlte Gold - keine Produktion mehr, Steuer bei 0 (Grenze 50),
                # die letzten 3 kamen 1.700 Ticks spaeter. Nach dem Abriss gibt es nichts mehr zu schuetzen: immer Stufe 11
                neu = 11
            elif getattr(self, "kasse", False):
                # Kasse (Daniel 07.10. 00:17/00:20): Stufe 11 bis zum Ende, OHNE Beliebtheits-Schutz - der Spielcode zahlt die
                # Steuer unabhaengig von der Beliebtheit (updateTaxing: Stufe x Koepfe, je Monat ~800 Ticks). ABER Lauf 26:
                # Beliebtheit 0 -> Massen-Wegzug (Liga gathering_rate -40 bei 0-4), 50 -> 4 Leute, kein Kaempfer. Darum Grenze
                # (Knopf kasse_grenze): darunter Stufe 2 (keine Steuer, +1/Monat) - Beliebtheit ist ein Vorrat, keiner der nachwaechst
                # Stufe als Knopf (Daniel 01:03 "nicht -40, damit die Kurve nicht so schnell ist, dann laenger laufen lassen")
                neu = getattr(self, "kasse_stufe", 11) if bel >= getattr(self, "kasse_grenze", 50) else 2
            elif getattr(self, "wachstum", False):
                # Daniel 00:38 "die Steuer wird schon VIEL zu frueh genommen" (Lauf 40: Stufe 7 im Wachstum, dann steuer_ende
                # Stufe 11 bei 29/34 Leuten -> Beliebtheit 28, Zuzug weg, bei 38 stehen geblieben): bis zur Ziel-Bevoelkerung
                # keine Steuer (Stufe 2) - Zuzug haengt an der Beliebtheit (Liga gathering_rate +40 bei 95-100, +5 bei 50-54)
                neu = 2
            elif getattr(self, "kasse_modus", "nein") == "nein" and (
                    (ende == "ja" and getattr(self, "endphase", False)) or (ende == "wohnraum" and wohnraum_voll)) and bel >= 55:
                # Daniel 07.10. 00:0x: "wenn du eh keine Produktion mehr baust, weil sie sich nicht mehr amortisiert, kannst du
                # einfach -24 Steuern machen" - Endphase = Kausalmodell findet keine Handlung mit Wert mehr (holz_ueberfluessig);
                # Wohnraum ist dann voll, Zuzug egal; unter 55 Beliebtheit zurueck auf die Regel (unter 50 gehen Leute)
                neu = 11
            if neu != self.steuer:
                befehl({"spielbefehl": {"nr": 34, "werte": [neu]}}, 1.0, bis="SPIELBEFEHL")
                ev.append("STEUER %d -> %d (Beliebtheit %.2f)" % (self.steuer, neu, bel))
                self.steuer, self.steuer_runde = neu, runde
        # Lager: eine Ware nahe am Teil-Deckel (48 je Teil) -> anbauen (kostet nichts)
        teile = sum(1 for g in eigen if g["typ"] == 10)
        if teile and not [n for n in self.wirt.alt if n in G]:
            belegt = sum(-(-st.get(w, 0) // JE_TEIL) for w in ("holz", "stein", "eisen", "pech", "hopfen", "weizen", "mehl"))
            voll = [w for w in ("holz", "stein", "eisen") if st.get(w, 0) % JE_TEIL >= JE_TEIL - 8]
            # hoechstens 2 Lagerplaetze = 8 Teile (Daniel 21:11: "du brauchst nur 3 Plaetze - Holz, Stein, Eisen - wenn du
            # optimal platzierst und verkaufst; bei zwei bist du selbst bei doppelten Plaetzen auf der sicheren Seite")
            if voll and belegt >= teile and teile < MAX_LAGERTEILE and not getattr(self, "lager_stopp", False):
                l = self.ziele(G)[5][0]
                ev.append("PLANER Lager anbauen (%s fast voll, %d Teile) -> %s" % (voll, teile, self.baue(10, l[0], l[1], 10)))
        ev += self.ochsen_nach_stau(st, L, G, holz)
        alle = self.kandidaten(st, L, G)
        for k in alle:
            if k["grund"]:
                schl = (NAME[k["typ"]], k["grund"].split(" (")[0])
                self.abgelehnt[schl] = self.abgelehnt.get(schl, 0) + 1
        kand = [k for k in alle if not k["grund"]]
        if getattr(self, "kausal", False):
            # Entscheider = kausal (23:28): Holzfaeller, Apfel, Jaeger baut nur das Kausalmodell - EIN Entscheider je Sache
            kand = [k for k in kand if k["typ"] not in (3, 32, 7)]
        # Stein-Reserve: Bedarf der naechsten Eisenmine, solange sich eine Mine noch lohnt
        self.stein_reserve = self.kosten[5]["stein"] if any(k["typ"] == 5 for k in kand) else 0
        if (runde - 1) % (5 * self.PLANEN) == 0:
            ev.append("PLANER Lage (Gewinn bis Ende / Amortisation): " + ", ".join("%s %s/%.0f%s" % (
                NAME[k["typ"]], "-" if k["gewinn"] is None else "%.0f" % k["gewinn"], k["amort"], " [%s]" % k["grund"].split(" (")[0] if k["grund"] else "")
                for k in alle) + " | Stein-Reserve %d" % self.stein_reserve)
        if not kand:
            return ev
        beste = kand[0]
        self.letzte_wahl = beste
        R = self.wirt.ruecklage(G)          # B-Plantagen zuerst (gewinn_5: "Huette zuerst" verbaute das B-Holz)
        if st.get("feuer", 0) < beste["arbeiter"] and holz - R["holz"] >= self.kosten[1]["holz"] and st.get("leute", 0) >= st.get("platz", 0) - 2:
            ev.append("PLANER Huette zuerst (Feuer %d, %s braucht %d) -> %s" % (st.get("feuer", 0), NAME[beste["typ"]], beste["arbeiter"],
                                                                              self.baue(1, self.K[0] - 7, self.K[1] - 2, 25)))
            return ev
        # Arbeiterpruefung (v2b, B22): nie einen Betrieb setzen, fuer den kein freier Bauer am Feuer steht - sonst
        # stehen Dutzende Werkstaetten leer (57 Jaegerhuetten bei Feuer 0, Beliebtheit 38)
        if st.get("feuer", 0) < beste["arbeiter"]:
            if (runde - 1) % (5 * self.PLANEN) == 0:
                ev.append("PLANER wartet auf Arbeiter fuer %s (Feuer %d, braucht %d)" % (NAME[beste["typ"]], st.get("feuer", 0), beste["arbeiter"]))
            return ev
        # B-Ruecklage (Holz + Gold je offener B-Plantage) abziehen (Steinbruch-Kosten enthalten das Joch schon: kosten_von)
        habe = {"holz": holz - R["holz"], "stein": stein, "gold": gold - R["gold"]}
        bezahlbar = lambda k: all(habe[w] >= k["kosten"][w] for w in habe)
        # Ausweichbau nur, wenn er nichts verbraucht, was der beste braucht (sonst schiebt er den besten weiter hinaus)
        stiehlt = lambda k: any(beste["kosten"][w] > 0 and habe[w] - k["kosten"][w] < beste["kosten"][w] for w in habe if k["kosten"][w] > 0)
        if self.ende is None:
            wahl = beste if bezahlbar(beste) else next((k for k in kand[1:] if bezahlbar(k) and k["amort"] <= 1.5 * beste["amort"]), None)
        else:
            wahl = beste if bezahlbar(beste) else next((k for k in kand[1:] if bezahlbar(k) and not stiehlt(k)), None)
        if wahl is None:
            # nur sparen, was fehlt: Gold zurueckhalten nur, wenn dem besten Bau Gold fehlt
            if gold < beste["kosten"]["gold"] + R["gold"]:
                self.braucht_gold = True
            if (runde - 1) % (5 * self.PLANEN) == 0:
                ev.append("PLANER wartet auf %s (fehlt: %s)" % (NAME[beste["typ"]], ", ".join(
                    "%s %d" % (w, beste["kosten"][w] - v) for w, v in (("holz", holz), ("stein", stein), ("gold", gold)) if beste["kosten"][w] > v)))
            return ev
        # Widerlegung b) mitschreiben statt nur behaupten: Bau, der laut eigener Rechnung nicht mehr rechnet
        if wahl["rest"] is not None and wahl["anlauf"] + wahl["amort"] > wahl["rest"]:
            self.verstoss.append((st.get("t"), NAME[wahl["typ"]]))
        # Steinbruch: am Stein im Umkreis 8 weitersuchen (v9: bester Platz (80,265) "-> None", danach nur 64-67 Felder weit)
        r = 8 if wahl["typ"] == 20 else 3 if wahl["typ"] in (5, 32, 3) else 10
        ort = self.baue(wahl["typ"], wahl["ort"][0], wahl["ort"][1], r)
        if ort is None:
            self.fehlschlag[(wahl["typ"], wahl["ort"])] = self.fehlschlag.get((wahl["typ"], wahl["ort"]), 0) + 1
        elif wahl["typ"] == 20:
            self.baue(4, ort[0] + 3, ort[1] - 4, 8)                # Ochsenjoch direkt dazu
        if ort:
            self.gesetzt[NAME[wahl["typ"]]] = self.gesetzt.get(NAME[wahl["typ"]], 0) + 1
        ev.append("PLANER %s bei %s (Weg %d, %.1f Gold/1000, Anlauf %d, Amortisation %.0f, Gewinn bis Ende %s)%s -> %s" % (
            NAME[wahl["typ"]], wahl["ort"], wahl["weg"], wahl["gold_je_1000"], wahl["anlauf"], wahl["amort"],
            "-" if wahl["gewinn"] is None else "%.0f" % wahl["gewinn"], "" if wahl is beste else " statt %s" % NAME[beste["typ"]], ort))
        return ev

    def ochsen_nach_stau(self, st, L, G, holz):
        """Ochsenjoche nach Daniels Regel (05.10. 21:05): "nicht erst, wenn es gebraucht wird - nachdem der erste Ochse auf
        dem Weg ist, Stein abliefern zu wollen, direkt den zweiten. Weitere Joche folgen nur auf einen echten
        Lieferstau: Stein am Haufen, bereits beladener Stein und der noch offene Steinbedarf werden gemeinsam gerechnet.
        Ochse unterwegs = sein Treiber (Arbeitsplatz = das Joch) traegt Ladung (Lagebild, jede Runde in beobachte gemerkt).
          - genau 1 Joch und dessen Ochse war beladen unterwegs -> sofort das zweite
          - ab 2 Jochen: das juengste war schon beladen unterwegs; je mehr Stein bereits unterwegs ist, desto hoeher
            liegt die Schwelle. Dringender Bau-Stein senkt sie wieder, reines spaeteres Verkaufsgold nicht.
        Ein bestelltes Joch wird abgewartet, bis es steht. Nahe Brueche bilden einen gemeinsamen Abholbereich, weil
        Ochsen auch Stein von Nachbarhaufen nehmen; gezaehlt und skaliert wird deshalb je Bereich statt je Bruch."""
        t = st.get("t", 0)
        brueche = {n: g for n, g in G.items() if g["besitzer"] == self.sp and g["typ"] == 20}
        gruppen = steinbruch_gruppen(brueche)
        joche = {gruppe: [] for gruppe in gruppen}
        for j, o in G.items():
            if o["besitzer"] == self.sp and o["typ"] == 4 and brueche:
                gruppe = min(gruppen, key=lambda gr: min(
                    schach((o["x"], o["y"]), (brueche[n]["x"], brueche[n]["y"])) for n in gr))
                if min(schach((o["x"], o["y"]), (brueche[n]["x"], brueche[n]["y"])) for n in gruppe) <= 18:
                    joche[gruppe].append(j)
        ladung = {j: sum(e.get("ladung", 0) for e in L.values()
                         if e["besitzer"] == self.sp and e.get("arbeitsplatz") == j)
                  for js in joche.values() for j in js}
        alle_unterwegs = sum(ladung.values())
        dringend = max(0, self.stein_reserve - st.get("stein", 0) - alle_unterwegs)
        ev = []
        for gruppe in gruppen:
            haufen = {}
            for n in gruppe:
                g = brueche[n]
                h = G.get(g.get("verbund") or -1)
                haufen[n] = h.get("vorrat") if h else None
                if haufen[n] is not None:
                    self.haufen[n] = haufen[n]
            v = sum(x or 0 for x in haufen.values())
            js = joche[gruppe]
            bestellt = self.joch_bestellt.get(gruppe, 0)
            if bestellt > len(js):
                # Ein echter Bau erscheint binnen weniger Runden; nach 500 Ticks ohne Gebaeude ist der Auftrag sicher
                # verloren. Vorher kein Doppelauftrag, danach darf derselbe Bedarf erneut geplant werden.
                if t - self.joch_bestell_tick.get(gruppe, t) < 500:
                    continue
                self.joch_bestellt[gruppe] = len(js)
            if not js or holz < self.kosten[4]["holz"]:
                continue
            juengstes = max(js, key=lambda j: (self.messer.gesehen.get(j, 0), j))
            if not (juengstes in self.joch_beladen):
                continue                                              # dessen Ochse war noch nicht beladen unterwegs
            grundbedarf = 2 * len(gruppe)
            if len(js) < grundbedarf:
                grund = "Abholbereich %s: arbeitender Ochse belegt, Grundbedarf %d fuer %d Brueche" % (
                    gruppe, grundbedarf, len(gruppe))
            else:
                unterwegs = sum(ladung.get(j, 0) for j in js)
                # Ohne akuten Baubedarf erst bei 9 plus bereits bewegtem Stein erweitern. Bei mindestens vier
                # fehlenden Bau-Steinen sinkt die Grundschwelle auf 5; beladene Traeger zaehlen weiterhin dagegen.
                schwelle = 9 + unterwegs - min(4, dringend)
                if v is None or v < schwelle:
                    self.joch_stau.pop(gruppe, None)
                    continue
                stau = self.joch_stau.setdefault(gruppe, {"seit": t, "zuletzt": v + unterwegs})
                stau["zuletzt"] = v + unterwegs
                if t - stau["seit"] < 200:
                    continue                                          # kurze Spitze, noch kein dauerhafter Lieferstau
                grund = ("juengster Ochse unterwegs; Haufen %d >= Schwelle %d "
                         "seit %d Ticks (unterwegs %d, Bau-Stein offen %d)") % (
                             v, schwelle, t - stau["seit"], unterwegs, dringend)
            # Innerhalb des gemeinsamen Bereichs an den Bruch mit den wenigsten physisch nahen Jochen anbauen.
            n = min(gruppe, key=lambda q: sum(1 for j in js if schach(
                (G[j]["x"], G[j]["y"]), (brueche[q]["x"], brueche[q]["y"])) <= 15))
            g = brueche[n]
            ort = self.baue(4, g["x"] + 3, g["y"] - 4, 8)
            if ort:
                self.joch_bestellt[gruppe] = len(js) + 1
                self.joch_bestell_tick[gruppe] = t
                self.joch_stau.pop(gruppe, None)
                self.gesetzt["Ochsenjoch (Regel)"] = self.gesetzt.get("Ochsenjoch (Regel)", 0) + 1
            ev.append("PLANER Ochsenjoch fuer Bereich %s: %s (Joche %d, Haufen %s) -> %s" % (
                gruppe, grund, len(js), haufen, ort))
            break                                                     # eins je Planungsrunde
        return ev

    def bericht(self):
        stehen = {NAME[t]: self.messer.letzter.get("G%d" % t, 0) for t in START}
        stehen["Ochsenjoch"] = self.messer.letzter.get("G4", 0)
        stehen["Steinhaufen zuletzt"] = dict(sorted(self.haufen.items()))
        stehen["Bauplaetze ohne Weg verworfen"] = len(self.unerreichbar)
        return "Ertrags-Planer: gesetzt %s, stehen am Ende %s, abgelehnt %s, Verstoesse gegen den Horizont %s, Steuerstufe %d\n%s" % (
            self.gesetzt or "nichts", stehen, {"%s: %s" % k: v for k, v in self.abgelehnt.items()}, self.verstoss or "keine",
            self.steuer, self.messer.bericht())

    def sichern(self, pfad):
        json.dump({"zeit": time.strftime("%d.%m.%Y %H:%M"), "kosten": self.kosten, "gelernt": self.messer.stand(),
                   "gesetzt": self.gesetzt, "verstoesse": self.verstoss}, open(pfad, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    # python ertragsplaner.py startwerte M19 <datei> [<datei> ...]  -> daten/ertrag_startwerte_M19.json
    import sys
    if len(sys.argv) >= 4 and sys.argv[1] == "startwerte":
        kurz, dateien = sys.argv[2], sys.argv[3:]
        w = startwerte_aus_partien(dateien)
        ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten", "ertrag_startwerte_%s.json" % kurz)
        json.dump({"zeit": time.strftime("%d.%m.%Y %H:%M"), "partien": len(dateien), "quellen": [os.path.basename(f) for f in dateien],
                   "werte": {str(t): v for t, v in w.items()}}, open(ziel, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for t, v in w.items():
            print("%-22s %s" % (NAME[t], v))
