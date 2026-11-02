# -*- coding: utf-8 -*-
"""B-142 Auswerter: prueft eine Aufzeichnung des Auges gegen die Gesamtproben aus Checkliste_Auge.md.

Jede Aussage gilt nur fuer die ausgewertete Aufzeichnung. Der Aenderungsmelder sieht nur, was sich zwischen zwei
Lesungen unterscheidet; was im Takt hin und zurueck wechselt, sieht er nicht.
Noch nicht gebaut: A8 (Buchfuehrung), A11 (Pruefsummen), Einzelpunkte und Versuche.
Aufruf: python -m selfaware.tools.analysis.auge_auswertung lauf_f.auge [--zweite lauf_k2.auge --t1 T --t2 T --takte 2000]
"""
import argparse
import collections
import json
import statistics
import struct
import zlib
from dataclasses import dataclass, field

from selfaware.tools.experiments.auge_aufzeichnung import KENNUNG, RAHMEN, REIN, VOLL

BESTAETIGT, WIDERLEGT, NICHT_GESEHEN, GEMESSEN = "bestaetigt", "widerlegt", "nicht gesehen", "gemessen"


@dataclass
class Ergebnis:
    nr: str
    status: str
    text: str
    daten: dict = field(default_factory=dict)


@dataclass
class Rahmen:
    art: int
    bereich: int
    merker: int
    takt: int
    takt_nach: int
    zeit: float
    dauer: float
    nutz: bytes

    @property
    def rein(self):
        return bool(self.merker & REIN) and self.takt == self.takt_nach


class Aufzeichnung:
    def __init__(self, pfad):
        self.pfad = pfad
        self.beschaedigt = 0
        with open(pfad, "rb") as f:
            if f.read(len(KENNUNG)) != KENNUNG:
                raise ValueError(f"{pfad}: keine Aufzeichnung des Auges")
            n = struct.unpack("<I", f.read(4))[0]
            self.kopf = json.loads(f.read(n).decode("utf-8"))
            self._start = f.tell()
        self.bereiche = self.kopf["bereiche"]
        self.namen = [b[0] for b in self.bereiche]

    def rahmen(self):
        """Alle Rahmen in Reihenfolge; ein abgeschnittenes oder falsches Ende stoppt und wird gezaehlt."""
        with open(self.pfad, "rb") as f:
            f.seek(self._start)
            while True:
                k = f.read(RAHMEN.size)
                if not k:
                    return
                if len(k) < RAHMEN.size:
                    self.beschaedigt += 1
                    return
                art, b, merker, vor, nach, zeit, dauer, rohl, zl = RAHMEN.unpack(k)
                z, c = f.read(zl), f.read(4)
                if len(z) < zl or len(c) < 4 or zlib.crc32(z) != struct.unpack("<I", c)[0]:
                    self.beschaedigt += 1
                    return
                yield Rahmen(art, b, merker, vor, nach, zeit, dauer, zlib.decompress(z))

    def staende(self):
        """(Rahmen, aktueller Puffer des Bereichs, Liste geaenderter Abschnitte) je Rahmen."""
        puffer = {}
        for r in self.rahmen():
            if r.art == VOLL:
                alt = puffer.get(r.bereich)
                puffer[r.bereich] = bytearray(r.nutz)
                yield r, puffer[r.bereich], alt
            else:
                p, i, teile = puffer[r.bereich], 0, []
                while i < len(r.nutz):
                    o, l = struct.unpack_from("<II", r.nutz, i)
                    i += 8
                    p[o:o + l] = r.nutz[i:i + l]
                    teile.append((o, l))
                    i += l
                yield r, p, teile

    def stand_bei(self, takt):
        """{Bereich: Puffer} genau zu diesem Takt; nur Bereiche, die in diesem Takt gelesen wurden."""
        aus = {}
        for r, p, _ in self.staende():
            if r.takt == takt:
                aus.setdefault(self.namen[r.bereich], bytes(p))
        return aus


def _voll_diff(alt, neu):
    teile, n = [], min(len(alt), len(neu))
    i = 0
    while i < n:
        if alt[i] != neu[i]:
            j = i
            while j < n and alt[j] != neu[j]:
                j += 1
            teile.append((i, j - i))
            i = j
        else:
            i += 1
    return teile


def a1_aenderungsmelder(auf, karte):
    zaehler = {"bekannt": collections.Counter(), "technik": collections.Counter(), "luecke": collections.Counter()}
    zuerst = {}
    rahmen = 0
    cache = {}
    for r, p, teile in auf.staende():
        rahmen += 1
        if r.art == VOLL:
            if teile is None:
                continue
            teile = _voll_diff(teile, p)  # nach dem Laden: Unterschied zum vorigen Stand
        basis = auf.bereiche[r.bereich][1]
        for o, l in teile:
            felder = cache.get((basis + o, l))
            if felder is None:
                felder = cache[(basis + o, l)] = [(g, f, karte.klasse(g, f)) for g, f in karte.felder_einer_aenderung(basis + o, l)]
            for g, f, k in felder:
                zaehler[k][(g, f)] += 1
                if k == "luecke":
                    zuerst.setdefault((g, f), r.takt)
    daten = {k: len(v) for k, v in zaehler.items()}
    daten["luecken"] = [{"global": g, "feld": f, "aenderungen": n, "erster_takt": zuerst[(g, f)]} for (g, f), n in zaehler["luecke"].most_common()]
    daten["gesehen"] = sorted(list(k) for k in zaehler["bekannt"])
    if not rahmen:
        return Ergebnis("A1", NICHT_GESEHEN, "keine Rahmen in der Aufzeichnung", daten)
    if zaehler["luecke"]:
        return Ergebnis("A1", WIDERLEGT, f"{len(zaehler['luecke'])} geaenderte Felder stehen nicht in der Feldliste", daten)
    return Ergebnis("A1", BESTAETIGT, f"keine Aenderung ausserhalb der Feldliste in dieser Aufzeichnung ({daten['bekannt']} bekannte, {daten['technik']} Technikfelder geaendert)", daten)


def a2_nie_gesehen(karte, gesehen):
    """gesehen: (global, pfad) aus A1, ueber alle Laeufe vereint."""
    g = {tuple(x) for x in gesehen}
    rest = []
    for k in sorted(karte.bekannte):
        if k in g or any(a == k[0] and (b.startswith(k[1] + ".") or b.startswith(k[1] + "[")) for a, b in g):
            continue
        rest.append(list(k))
    return Ergebnis("A2", GEMESSEN, f"{len(rest)} von {len(karte.bekannte)} Feldern der Liste haben sich in den ausgewerteten Laeufen nie geaendert; das heisst nur: nicht gesehen", {"nie": rest})


def a3_takttreue(auf):
    letzter, je_bereich, unrein, zurueck, n = {}, collections.Counter(), 0, 0, 0
    unrein_selten = 0
    luecken = []
    erster = {}
    for r in auf.rahmen():
        n += 1
        alle = auf.bereiche[r.bereich][3]
        if not r.rein:
            # selten gelesene Bereiche dienen dem Aenderungsmelder, dort sagt eine gemischte Lesung nichts ueber die Takt-Treue
            if alle == 1:
                unrein += 1
            else:
                unrein_selten += 1
        v = letzter.get(r.bereich)
        erster.setdefault(r.bereich, r.takt)
        if v is not None:
            d = r.takt - v
            if d < 0:
                zurueck += 1
            elif d > 1 and alle == 1:
                je_bereich[r.bereich] += d - 1
                luecken.append([v, r.takt])
        letzter[r.bereich] = r.takt
    fehlend = max(je_bereich.values(), default=0)
    daten = {"rahmen": n, "spanne": max((letzter[b] - erster[b] for b in letzter), default=0), "fehlende_takte": fehlend, "unreine_rahmen": unrein, "unrein_selten": unrein_selten, "rueckspruenge": zurueck, "luecken": luecken[:50], "beschaedigt": auf.beschaedigt}
    if not n:
        return Ergebnis("A3", NICHT_GESEHEN, "keine Rahmen", daten)
    tempo = auf.kopf.get("tempo") or 0
    if tempo > 100 and not auf.beschaedigt:
        return Ergebnis("A3", GEMESSEN, f"Auf Tempo {tempo} geht das Tempo vor: {fehlend} Takte ausgelassen, {unrein} Rahmen gemischt. Wie viele Takte je Stufe lesbar sind, zeigt die Tempotreppe", daten)
    if fehlend or unrein or auf.beschaedigt:
        return Ergebnis("A3", WIDERLEGT, f"{fehlend} Takte fehlen, {unrein} Rahmen sind gemischt, {auf.beschaedigt} Stellen beschaedigt", daten)
    return Ergebnis("A3", BESTAETIGT, f"kein Takt fehlt und kein Rahmen ist gemischt in dieser Aufzeichnung ({n} Rahmen)", daten)


def a4_lesedauer(auf):
    je_takt = collections.defaultdict(float)
    zeiten = {}
    for r in auf.rahmen():
        je_takt[r.takt] += r.dauer
        zeiten.setdefault(r.takt, r.zeit)
    if len(zeiten) < 2:
        return Ergebnis("A4", NICHT_GESEHEN, "zu wenige Takte", {})
    w = sorted(je_takt.values())
    takte = sorted(zeiten)
    # Median je Folgetakt statt Gesamtdauer: Pausen im Lauf sind kein Bremsen durch das Lesen
    abstaende = [zeiten[b] - zeiten[a] for a, b in zip(takte, takte[1:]) if b == a + 1 and zeiten[b] > zeiten[a]]
    tempo = 1 / statistics.median(abstaende) if abstaende else 0.0
    # Der Median trifft wegen der Bildgrenzen nur Vielfache eines Bildes (gemessen 37,5 bei 40,0 gesamt), darum beides nennen
    dauer = zeiten[takte[-1]] - zeiten[takte[0]]
    gesamt = (takte[-1] - takte[0]) / dauer if dauer > 0 else 0.0
    daten = {"takte": len(w), "median_s": statistics.median(w), "p95_s": w[int(len(w) * 0.95) - 1], "max_s": w[-1], "takte_je_s": tempo, "gesamt_je_s": gesamt, "ohne_lesen": auf.kopf.get("tempo_ohne_lesen")}
    ohne = daten["ohne_lesen"]
    text = f"Lesen je Takt: Median {daten['median_s'] * 1000:.1f} ms, Hoechstwert {daten['max_s'] * 1000:.1f} ms; {gesamt:.1f} Takte/s gesamt, Median-Abstand {tempo:.1f}"
    return Ergebnis("A4", GEMESSEN, text + (f", ohne Lesen {ohne:.1f}" if ohne else "; kein Vergleichswert ohne Lesen"), daten)


def a4_tempotreppe(zeilen):
    """Daniel 02.11.2026: auf Tempo 1 bis 1000 darf das Lesen kein Tempo abziehen. Je Stufe: ohne Lesen, mit Lesen, ohne Lesen.
    Als Messrauschen gilt nur, was die beiden Laeufe ohne Lesen selbst unterscheidet, plus der Ablesefehler: je Zaehlung ein
    Takt an beiden Enden, zwei Zaehlungen werden verglichen, also vier Takte."""
    if not zeilen:
        return Ergebnis("A4", NICHT_GESEHEN, "keine Tempotreppe gemessen", {})
    abzug, nicht_gemessen = [], []
    for z in zeilen:
        rauschen = abs(z["ohne_1"] - z["ohne_2"]) + 4 / z["sekunden"]
        z["abzug"] = max(0.0, min(z["ohne_1"], z["ohne_2"]) - z["mit"] - rauschen)
        if z["abzug"] > 0:
            abzug.append(z["tempo"])
        # Lauf F 02.11.2026: Stufe 1 hatte durch eine Pause nur einen Takt und galt trotzdem als bestaetigt, das war ein hohles Gruen
        if "soll" in z and z["gezaehlt"] < z["soll"]:
            nicht_gemessen.append(z["tempo"])
    fehlend = [z["tempo"] for z in zeilen if z["gelesen"] < z["gesamt"]]
    text = f"Stufen {[z['tempo'] for z in zeilen]}; Takte ausgelassen auf {fehlend or 'keiner Stufe'}"
    if abzug:
        return Ergebnis("A4", WIDERLEGT, f"Das Lesen zieht Tempo ab auf Stufe {abzug}. {text}", {"zeilen": zeilen})
    if nicht_gemessen:
        return Ergebnis("A4", NICHT_GESEHEN, f"Stufe {nicht_gemessen} hat zu wenige Takte und ist nicht gemessen. {text}", {"zeilen": zeilen})
    return Ergebnis("A4", BESTAETIGT, f"kein Tempoabzug ueber das Messrauschen hinaus in dieser Messung. {text}", {"zeilen": zeilen})


def _felder_diff(a, b, auf, karte):
    aus = collections.Counter()
    for name, puffer in a.items():
        if name not in b:
            continue
        basis = auf.bereiche[auf.namen.index(name)][1]
        for o, l in _voll_diff(puffer, b[name]):
            for g, f in karte.felder_einer_aenderung(basis + o, l):
                aus[(g, f)] += 1
    return aus


def a5_laden_gleich_sichern(auf1, t1, auf2, t2, karte):
    a, b = auf1.stand_bei(t1), auf2.stand_bei(t2)
    gemein = sorted(set(a) & set(b))
    if not gemein:
        return Ergebnis("A5", NICHT_GESEHEN, "die Aufzeichnungen haben zu diesen Takten keinen gemeinsamen Bereich", {})
    d = _felder_diff(a, b, auf1, karte)
    spiel = {k: n for k, n in d.items() if karte.klasse(*k) != "technik"}
    daten = {"bereiche": gemein, "abweichend": [[g, f, n] for (g, f), n in sorted(spiel.items())], "technik": len(d) - len(spiel)}
    if spiel:
        return Ergebnis("A5", WIDERLEGT, f"{len(spiel)} Spielfelder weichen nach dem Laden ab, sie werden nicht gespeichert oder sind flüchtig", daten)
    return Ergebnis("A5", BESTAETIGT, f"alle Spielfelder in {len(gemein)} Bereichen gleich", daten)


def _je_takt(auf, von, bis):
    """Nur Bereiche, die jeden Takt gelesen werden: seltenere liegen je Aufzeichnung auf anderen Takten."""
    for r, p, _ in auf.staende():
        if von <= r.takt <= bis and auf.bereiche[r.bereich][3] == 1:
            yield r, p


def a6_gleicher_verlauf(auf1, t1, auf2, t2, takte, karte):
    z1, z2 = _je_takt(auf1, t1, t1 + takte), _je_takt(auf2, t2, t2 + takte)
    verglichen = gemischt = 0
    for (r1, p1), (r2, p2) in zip(z1, z2):
        if r1.takt - t1 != r2.takt - t2 or r1.bereich != r2.bereich:
            return Ergebnis("A6", WIDERLEGT, f"die Aufzeichnungen laufen auseinander: Takt {r1.takt} Bereich {r1.bereich} gegen Takt {r2.takt} Bereich {r2.bereich}", {"gleich_bis": verglichen})
        if not (r1.rein and r2.rein):
            gemischt += 1  # gemischte Lesung sagt nichts; A3 meldet sie
        elif p1 != p2:
            name = auf1.namen[r1.bereich]
            basis = auf1.bereiche[r1.bereich][1]
            felder = []
            for o, l in _voll_diff(p1, p2):
                felder += karte.felder_einer_aenderung(basis + o, l)
            felder = [list(f) for f in dict.fromkeys(felder)]
            spiel = [f for f in felder if karte.klasse(*f) != "technik"]
            if spiel:
                return Ergebnis("A6", WIDERLEGT, f"erste Abweichung {r1.takt - t1} Takte nach dem Start in {name}: {spiel[:5]}", {"takt": r1.takt - t1, "bereich": name, "felder": spiel[:200]})
        verglichen += 1
    if not verglichen:
        return Ergebnis("A6", NICHT_GESEHEN, "kein gemeinsamer Abschnitt", {})
    return Ergebnis("A6", BESTAETIGT, f"{verglichen - gemischt} Rahmen gleich in diesem Abschnitt, {gemischt} gemischte uebersprungen", {"rahmen": verglichen, "gemischt": gemischt})


def a7_zufall(auf, name="SEC_RNG"):
    """currentNumber = randomNumbers[index - 1], Umlauf bei 20.000 (nextRandomNumber1, nextRandomNumber2)."""
    if name not in auf.namen:
        return Ergebnis("A7", NICHT_GESEHEN, "Zufallsbereich nicht aufgezeichnet", {})
    b = auf.namen.index(name)
    alt, gezogen, falsch = None, 0, []
    for r, p, _ in auf.staende():
        if r.bereich != b:
            continue
        c1, c2 = struct.unpack_from("<hh", p, 0)
        i2, i1 = struct.unpack_from("<ii", p, 40008)
        if alt is not None:
            for nr, i, c, vor in ((1, i1, c1, alt[0]), (2, i2, c2, alt[1])):
                if i != vor:
                    gezogen += 1
                    if not 0 <= i < 20000 or c != struct.unpack_from("<h", p, 8 + 2 * ((i - 1) % 20000))[0]:
                        falsch.append([r.takt, nr, i, c])
        alt = (i1, i2)
    daten = {"gezogen": gezogen, "falsch": falsch[:50]}
    if not gezogen:
        return Ergebnis("A7", NICHT_GESEHEN, "keine Zufallszahl gezogen", daten)
    if falsch:
        return Ergebnis("A7", WIDERLEGT, f"{len(falsch)} von {gezogen} Lesungen passen nicht zur Tabelle", daten)
    return Ergebnis("A7", BESTAETIGT, f"{gezogen} Lesungen passen zur Tabelle in dieser Aufzeichnung", daten)


def a9_befehle(auf, gesendet=None, name="befehle", groesse=1272):
    """Geaenderte Plaetze im Befehlsring je Takt; gesendet: {takt: Anzahl} prueft die eigenen Befehle."""
    if name not in auf.namen:
        return Ergebnis("A9", NICHT_GESEHEN, "Befehlsring nicht aufgezeichnet", {})
    b = auf.namen.index(name)
    je_takt = collections.Counter()
    for r, _, teile in auf.staende():
        if r.bereich != b or r.art == VOLL:
            continue
        je_takt[r.takt] = len({o // groesse for o, _ in teile})
    daten = {"takte_mit_befehl": sum(1 for v in je_takt.values() if v), "plaetze": sum(je_takt.values())}
    if gesendet is None:
        return Ergebnis("A9", GEMESSEN, f"{daten['plaetze']} Plaetze geaendert, ohne Liste der eigenen Befehle nicht vergleichbar", daten)
    falsch = [[t, n, sum(je_takt[x] for x in range(t, t + 3))] for t, n in gesendet.items() if sum(je_takt[x] for x in range(t, t + 3)) != n]
    daten["falsch"] = falsch[:50]
    if falsch:
        return Ergebnis("A9", WIDERLEGT, f"{len(falsch)} eigene Befehle kommen nicht genau einmal im Ring an", daten)
    return Ergebnis("A9", BESTAETIGT, f"{len(gesendet)} eigene Befehle jeweils einmal im Ring", daten)


def a10_lebenslauf(auf, listen, grenzen=()):
    """listen: (Name, Adresse von uid des ersten Elements, Schritt, Anzahl, erster echter Platz); grenzen: (Name, Adresse, Format, kleinste, groesste)."""
    verstoesse, belegt = [], {}
    wechsel = 0
    gesehen = {}
    for r, p, teile in auf.staende():
        bname, badr, blen, _ = auf.bereiche[r.bereich]
        for name, adr, schritt, anzahl, erster in listen:
            if not (badr <= adr and adr + schritt * anzahl <= badr + blen):
                continue
            # nur Plaetze, die sich in diesem Rahmen geaendert haben; nach einem vollen Rahmen alle
            if r.art == VOLL:
                plaetze = range(anzahl)
            else:
                plaetze = set()
                for o, l in teile:
                    if badr + o < adr + schritt * anzahl and badr + o + l > adr:
                        plaetze.update(range(max(0, (badr + o - adr) // schritt), min(anzahl - 1, (badr + o + l - 1 - adr) // schritt) + 1))
            for i in plaetze:
                if i < erster:
                    continue
                u = struct.unpack_from("<i", p, adr - badr + i * schritt)[0]
                k = (name, i)
                if belegt.get(k) != u:
                    if u and gesehen.get((name, u), i) != i:
                        verstoesse.append([r.takt, name, i, f"uid {u} schon auf Platz {gesehen[(name, u)]}"])
                    if u:
                        gesehen[(name, u)] = i
                    belegt[k] = u
                    wechsel += 1
        for name, adr, fmt, klein, gross in grenzen:
            if badr <= adr < badr + blen:
                w = struct.unpack_from(fmt, p, adr - badr)[0]
                if not klein <= w <= gross:
                    verstoesse.append([r.takt, name, w, f"ausserhalb {klein} bis {gross}"])
    daten = {"wechsel": wechsel, "verstoesse": verstoesse[:100], "anzahl": len(verstoesse)}
    if not wechsel:
        return Ergebnis("A10", NICHT_GESEHEN, "keine Plaetze gesehen", daten)
    if verstoesse:
        return Ergebnis("A10", WIDERLEGT, f"{len(verstoesse)} Verstoesse, zuerst {verstoesse[0]}", daten)
    return Ergebnis("A10", BESTAETIGT, f"{wechsel} Platzwechsel ohne Verstoss in dieser Aufzeichnung", daten)


def a12_fluechtig(auf, merker):
    """merker: (Name, Adresse, Format). Zaehlt Wertewechsel am Taktende; ob sie Zustand tragen, entscheidet A6."""
    z = collections.Counter()
    letzte = {}
    for r, p, _ in auf.staende():
        _, badr, blen, _ = auf.bereiche[r.bereich]
        for name, adr, fmt in merker:
            if badr <= adr < badr + blen:
                w = struct.unpack_from(fmt, p, adr - badr)[0]
                if name in letzte and letzte[name] != w:
                    z[name] += 1
                letzte[name] = w
    return Ergebnis("A12", GEMESSEN, f"Wechsel am Taktende: {dict(z)}", {"wechsel": dict(z), "gelesen": sorted(letzte)})


def a13_spielart(aufzeichnungen):
    """{Lauf: Aufzeichnung}. Erwartung (Vermutung): F und S gleich, K anders."""
    werte = {k: a.kopf.get("spielart") for k, a in aufzeichnungen.items()}
    if not all(werte.values()) or not {"F", "K", "S"} <= set(werte):
        return Ergebnis("A13", GEMESSEN, f"Spielart: {werte}", {"werte": werte})
    if werte["F"] == werte["S"] and werte["F"] != werte["K"]:
        return Ergebnis("A13", BESTAETIGT, f"F und S gleich, K anders: {werte}", {"werte": werte})
    return Ergebnis("A13", WIDERLEGT, f"anders als vermutet: {werte}", {"werte": werte})


def echte_listen(karte):
    """Einheiten ab Platz 1: setDestinationForUnit (0x0053d3d0) und computeLadderClimbPath (0x00533a10) kopieren die Einheit vor der Wegsuche
    auf Platz 0, dort steht also immer wieder eine uid doppelt (Probe 02.11.2026: 19 Kopien in 1.900 Takten, jede hatte ihr Original)."""
    aus = []
    for name, g, p, erster in (("Einheiten", "DAT_UnitsState", "units[].uid", 1), ("Gebaeude", "DAT_BuildingsState", "buildings[].uid", 0), ("Geschosse", "DAT_EntityState", "entityArray[].uid", 0)):
        adr, _, schritt, anzahl = karte.adresse(g, p)
        aus.append((name, adr, schritt, anzahl, erster))
    return aus


def echte_grenzen(karte):
    """Grenzen aus dem Funktionswissen: Monat 0 bis 11, Geschossplaetze unter 25 mit uid 0."""
    aus = [("Monat", karte.adresse("DAT_GameState", "mapAndTime.month")[0], "<i", 0, 11)]
    adr, _, schritt, _ = karte.adresse("DAT_EntityState", "entityArray[].uid")
    aus += [(f"Geschossplatz {i} uid", adr + i * schritt, "<i", 0, 0) for i in range(25)]
    return aus


# A8: Spielerdaten und Tabellen des Spiels, Herkunft siehe zustand_felder.csv
SPIELERDATEN, SPIELER_SCHRITT = 0x0115BDF8, 0x39F4
FELD_START, FELD_BESTAND = 0x46C, 0x4D0
FELD_STEUER = 0x2144, 0x2158  # taxBribeMonthlyAccumulator, taxIncomeMonthlyAccumulator
GEBAEUDE_SCHRITT, GEBAEUDE_TYP = 0x32C, 0xE6
LAGERARTEN = {10, 11, 19, 21}  # Lager, Waffenlager, Kornspeicher, Steinhalde: Ihr Bestand IST die Summe, er ist keine Ursache
WARE_NAMEN = {2: "Holz", 3: "Hopfen", 4: "Stein", 6: "Eisen", 7: "Pech", 9: "Weizen", 10: "Brot", 11: "Kaese", 12: "Fleisch", 13: "Aepfel", 14: "Bier", 15: "Gold", 16: "Mehl",
              17: "Bogen", 18: "Armbrust", 19: "Speer", 20: "Pike", 21: "Keule", 22: "Schwert", 23: "Lederruestung", 24: "Eisenruestung"}


def _ursache(ware, start_aenderung, steuer_aenderung, befehl_vor, felder, betrieb):
    if start_aenderung:
        return "Startwaren"
    # updateTaxing (0x0045bf50) leert im Monatswechsel die Sammelfelder und bucht sie im selben Takt aufs Gold
    if ware == 15 and steuer_aenderung:
        return "Steuer"
    if befehl_vor:
        return "Befehl"
    if ware in (10, 11, 12, 13) and any("food" in f.lower() for f in felder):
        return "Essen"
    # Gold ist keine Ware, die Arbeiter tragen: Ein Betrieb in der Naehe erklaert es nicht. Gibt es doch so einen Weg, faellt er als "ohne Ursache" auf
    if ware != 15 and (betrieb or any("resourceToDeposit" in f for f in felder)):
        return "Arbeiter"
    return None


def a8_buchfuehrung(auf, karte, sp=1, fenster=3):
    """Jede Bestandsaenderung von Gold und Waren einer moeglichen Ursache zuordnen. Geht nur, wenn jeder Takt gelesen ist (Tempo-40-Jahr).
    Ursachen im selben Takt oder bis zu fenster Takte davor; ein Befehl wirkt erst Takte nach dem Eintrag im Ring.
    Zugeordnet wird zeitlich, nicht Stueck fuer Stueck: "Arbeiter" heisst, ein Betrieb aenderte in dem Fenster seine Ware."""
    namen = auf.namen
    if "DAT_GameState" not in namen:
        return Ergebnis("A8", NICHT_GESEHEN, "Spielerdaten nicht aufgezeichnet", {})
    g = namen.index("DAT_GameState")
    gb = auf.bereiche[g][1]
    start_o, best_o = SPIELERDATEN + sp * SPIELER_SCHRITT + FELD_START - gb, SPIELERDATEN + sp * SPIELER_SCHRITT + FELD_BESTAND - gb
    steuer_o = [SPIELERDATEN + sp * SPIELER_SCHRITT + f - gb for f in FELD_STEUER]

    def stand(p):
        return struct.unpack_from("<25i", p, best_o), struct.unpack_from("<25i", p, start_o), [struct.unpack_from("<i", p, o)[0] for o in steuer_o]
    alt_best = alt_start = alt_steuer = None
    letzte = {"befehl": -10 ** 9, "betrieb": -10 ** 9}
    felder_je = collections.defaultdict(set)
    zaehler = collections.defaultdict(collections.Counter)
    rest = []
    cache = {}
    bestand_takt = {}
    for r, p, teile in auf.staende():
        name = namen[r.bereich]
        basis = auf.bereiche[r.bereich][1]
        if r.art == VOLL or not r.rein:
            if name == "DAT_GameState":
                alt_best, alt_start, alt_steuer = stand(p)
            continue
        if name == "befehle" and teile:
            letzte["befehl"] = r.takt
        elif name == "DAT_BuildingsState":
            for o, l in teile:
                typ = struct.unpack_from("<h", p, o // GEBAEUDE_SCHRITT * GEBAEUDE_SCHRITT + GEBAEUDE_TYP)[0] if o // GEBAEUDE_SCHRITT else 0
                if typ and typ not in LAGERARTEN:
                    f = cache.setdefault((basis + o, l), karte.felder_einer_aenderung(basis + o, l))
                    if any(".resource" in x[1] for x in f):
                        letzte["betrieb"] = r.takt
        elif name in ("DAT_UnitsState", "DAT_GameState"):
            for o, l in teile:
                f = cache.setdefault((basis + o, l), karte.felder_einer_aenderung(basis + o, l))
                felder_je[r.takt].update(x[1] for x in f)
        if name == "DAT_GameState":
            best, start, steuer = stand(p)
            if alt_best is not None and best != alt_best:
                naehe = set()
                for t in range(r.takt - fenster, r.takt + 1):
                    naehe |= felder_je.get(t, set())
                for w in range(25):
                    d = best[w] - alt_best[w]
                    if d and w in WARE_NAMEN:
                        ursache = _ursache(w, start[w] != alt_start[w], steuer != alt_steuer, r.takt - letzte["befehl"] <= fenster + 40, naehe, r.takt - letzte["betrieb"] <= fenster)
                        zaehler[WARE_NAMEN[w]][ursache or "ohne Ursache"] += 1
                        if ursache is None and len(rest) < 200:
                            rest.append([r.takt, WARE_NAMEN[w], d])
            alt_best, alt_start, alt_steuer = best, start, steuer
            for t in [t for t in felder_je if t < r.takt - fenster - 1]:
                del felder_je[t]
    gesamt = sum(sum(c.values()) for c in zaehler.values())
    ohne = sum(c["ohne Ursache"] for c in zaehler.values())
    daten = {"je_ware": {k: dict(v) for k, v in zaehler.items()}, "ohne_ursache": rest, "aenderungen": gesamt, "anzahl_ohne": ohne}
    if not gesamt:
        return Ergebnis("A8", NICHT_GESEHEN, "keine Bestandsaenderung in dieser Aufzeichnung", daten)
    if ohne:
        return Ergebnis("A8", WIDERLEGT, f"{ohne} von {gesamt} Bestandsaenderungen ohne Ursache, zuerst {rest[0]}", daten)
    je_ursache = collections.Counter()
    for c in zaehler.values():
        je_ursache.update(c)
    return Ergebnis("A8", BESTAETIGT, f"alle {gesamt} Bestandsaenderungen fallen mit einer moeglichen Ursache zusammen: {dict(je_ursache)}. Zeitlich zugeordnet, nicht Stueck fuer Stueck", daten)


def echte_merker(karte):
    """Fluechtige Werte fuer A12, soweit das Spiel sie benennt."""
    aus = []
    for a, n in karte.labels.items():
        if n in ("DAT_CurrentUnitSlotID", "DAT_UnitHasBecomeIdle", "DAT_CurrentBuildingID", "DAT_CurrentEntityID"):
            aus.append((n, a, "<i"))
    return aus


def bericht(ergebnisse):
    z = ["| Probe | Ergebnis | Aussage |", "|---|---|---|"]
    z += [f"| {e.nr} | {e.status} | {e.text} |" for e in ergebnisse]
    return "\n".join(z) + "\n"


def main(argv=None):
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("aufzeichnung")
    p.add_argument("--zweite")
    p.add_argument("--t1", type=int)
    p.add_argument("--t2", type=int)
    p.add_argument("--takte", type=int, default=2000)
    p.add_argument("--ausgabe")
    a = p.parse_args(argv)
    karte = Feldkarte.laden(feldliste=FELDLISTE)
    auf = Aufzeichnung(a.aufzeichnung)
    e1 = a1_aenderungsmelder(auf, karte)
    aus = [e1, a2_nie_gesehen(karte, e1.daten["gesehen"]), a3_takttreue(auf), a4_lesedauer(auf), a7_zufall(auf), a9_befehle(auf),
           a10_lebenslauf(auf, echte_listen(karte), echte_grenzen(karte))]
    if a.zweite:
        zw = Aufzeichnung(a.zweite)
        aus += [a5_laden_gleich_sichern(auf, a.t1, zw, a.t2, karte), a6_gleicher_verlauf(auf, a.t1, zw, a.t2, a.takte, karte)]
    print(bericht(aus))
    if a.ausgabe:
        json.dump([e.__dict__ for e in aus], open(a.ausgabe, "w", encoding="utf-8"), ensure_ascii=False, indent=0)


if __name__ == "__main__":
    main()
