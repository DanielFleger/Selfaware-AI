# -*- coding: utf-8 -*-
"""Partievergleich (Daniel 19.10. 16:11: "baue solche Analysetools fuer jede zukuenftige Partie ein, damit man immer
nachvollziehen kann warum und dann auch ab wann jemand im Nachteil ist").

Vorbild: die Handauswertung von 1018j (19.10. 16:03-16:40, Wissensregister 1018j): Spieler 2 hatte bis Tick 15.000 mehr
Holz-Einnahmen, verlor zwischen 15.000 und 18.000 14 von 16 liefernden Holzfaellerhuetten, Spieler 1 dagegen vor allem
frisch nachgebaute, die noch nie geliefert hatten - danach Holz 0, Feuer voll (L27), Leute 50 statt 120.

Liest nach der Partie
  - das Lageprotokoll (lageprotokoll.py; enthaelt Gebaeude und Einheiten ALLER Spieler) - Pflicht,
  - je eigenem Lenker die Statuszeile (st im eigenen Lageprotokoll) und die Ertragsdatei (ertrag_live_*.jsonl) - wenn da,
und rechnet je Spieler und je FENSTER Ticks Kennzahlen, alle "mehr ist besser":
  Leute (st), liefernde Betriebe (Gebaeude, in denen schon einmal Ware lag - GEMESSEN je Gebaeude, keine feste
  Anlaufzeit: 1018j Bau -> erstes Holz Median 3.402 bzw. 2.294 Ticks, 111 Huetten wurden zerstoert, bevor sie je
  lieferten), Holz-Einnahmen (Ertragsdatei), Gebaeude, Assassinen, Truppen.
  Keine Kennzahl "Arbeiter": die Lagebild-Spalte arbeitsplatz ist auch bei Bauern am Feuer und Truppen gesetzt (gemessen
  1018j Tick 60.073: 324 Einheiten mit Wert bei 110 Leuten).
AB WANN, zwei Antworten:
  HINTEN AB    je Bestands-Kennzahl der Tick, ab dem ein Spieler bis zum Ende hinten liegt (gleitendes Mittel ueber
               GLAETTEN Fenster; eine Fuehrung kuerzer als MIN_STRECKE Fenster zaehlt nicht als Aufholen). Mit den Werten
               beider Spieler dort und am Ende - so sieht man, ob der Rueckstand anfangs knapp war.
  EINBRUCH     der Tick, der die Partie je Kennzahl am besten in "vorher" und "nachher" teilt (Abstand je Fenster
               (b - a) / max(a, b); ein Bruchpunkt, Staerke siehe einbruch()); ueber alle Kennzahlen der staerkste, nach
               dem der Spieler hinten liegt. Gezeigt werden die Mittel der UMFELD Fenster davor und danach.
Ausgewertet wird nur, solange alle Bergfriede stehen (danach ist die Partie entschieden).
GESCHEHEN (das Warum, gemessen, als Ursache nicht bewiesen): in den UMFELD Fenstern vor und nach dem Einbruch je Spieler:
verlorene liefernde Betriebe und verlorene Betriebe, in denen nie Ware gesehen wurde (je Art; Aufloesung = eine Runde), wo die liefernden verloren gingen, Neubauten, Holz rein/verbaut, Vorrat, Gold,
Assassinen; dazu L27 ab "hinten ab" (Feuer voll bei freien Plaetzen = es fehlen Arbeitsplaetze, nicht Wohnplaetze).

Pruefung ohne Spiel: werkzeug/partie_vergleich_pruefen.py.
Aufruf: python partie_vergleich.py <lage.jsonl.gz> [<lage_sp2.jsonl.gz> ...] [ertrag=<datei>,<datei>] [json=<ausgabe>]
        Das erste Lageprotokoll liefert Gebaeude und Einheiten aller Spieler; jedes Protokoll und jede Ertragsdatei die
        Werte seines Spielers (Spieler aus dem Dateinamen: _spN, sonst 1)."""
import json
import os
import re
import sys
from collections import Counter, defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)

FENSTER = 1000
GLAETTEN = 3            # Fenster im gleitenden Mittel
MIN_STRECKE = 3         # kuerzere Fuehrungen zaehlen nicht als Aufholen; kuerzere Rueckstaende am Ende nicht als Nachteil
UMFELD = 3              # Fenster vor und nach einem Einbruch (Mittel und Suche nach dem Warum)
FEUER_VOLL = 24         # L27 (Daniel 07.10.; gemessen 19.10.: ab 27 Wartenden kam in 586 Schritten niemand mehr)
BETRIEBE = {3, 4, 5, 6, 7, 12, 13, 14, 15, 16, 17, 18, 20, 28, 30, 31, 32, 33, 34}
TRUPPEN = {22, 23, 24, 25, 26, 27, 28, 70, 71, 72, 73, 74, 75, 76}
ASSASSINE = 73
BERGFRIED = 41
NICHT_ZAEHLEN = {67}    # Fallgruben sind keine Gebaeude im Sinne der Wirtschaft
KENNZAHLEN = ("leute", "liefernd", "holz_rein", "gebaeude", "assassinen", "truppen")
# HINTEN AB nur fuer Bestaende: Fluesse schwanken zu stark (1018j: Spieler 2 lag bei den Holz-Einnahmen um Tick 42.000,
# 51.000, 63.000 und 69.000 je kurz vorn, weil Spieler 1 spaet weniger Holz holte - "hinten ab" wanderte auf 71.000)
NUR_EINBRUCH = {"holz_rein"}
WIRTSCHAFT = ("liefernd", "holz_rein", "gebaeude", "leute")
NAME = {"leute": "Leute", "liefernd": "liefernde Betriebe", "holz_rein": "Holz-Einnahmen",
        "gebaeude": "Gebaeude", "assassinen": "Assassinen", "truppen": "Truppen"}


def _typnamen():
    try:
        pfad = os.path.join(HIER, "..", "..", "VillageStudio", "lib", "gebaeude.json")
        g = json.load(open(pfad, encoding="utf-8"))["gebaeude"]
        return {v["laufzeit"]: v["name"] for v in g.values() if "laufzeit" in v and "mapper" in v}
    except (OSError, ValueError, KeyError):
        return {}


TYPNAME = _typnamen()


def typname(t):
    return TYPNAME.get(t, "Typ %d" % t)


# ---- Sammeln --------------------------------------------------------------------------------------------------------
class Lauf:
    """Sammelt Runde fuer Runde (t, st, E, G) des Haupt-Lageprotokolls; statuszeile/ertrag ergaenzen weitere Spieler."""

    def __init__(self):
        self.gebaeude = {}                    # (besitzer, uid) -> {typ, x, y, erst, zuletzt, liefer}
        self.fenster = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))   # w -> sp -> groesse -> [werte]
        self.summen = defaultdict(lambda: defaultdict(Counter))                      # w -> sp -> groesse -> summe
        self.spieler = set()
        self.mit_st = set()
        self.mit_ertrag = set()
        self.erste_t = self.letzte_t = None
        self.vorbei = None                    # Tick, an dem ein Bergfried verschwand (Partie entschieden)

    def runde(self, t, st, E, G, sp_st=None):
        if t is None or self.vorbei is not None:
            return
        burgen = {g["besitzer"] for g in G if g["typ"] == BERGFRIED}
        if self.spieler and not self.spieler <= burgen:
            # 1018j: nach dem Lord-Tod (Tick 73.194) verschwanden bis 73.254 die Gebaeude des Verlierers - das ist die
            # Niederlage selbst, kein Grund fuer sie; ausgewertet wird nur, solange alle Bergfriede stehen
            self.vorbei = t
            return
        if self.erste_t is None:
            self.erste_t = t
        self.letzte_t = t
        if sp_st is not None and st:
            self.statuszeile(t, st, sp_st)
        anzahl, liefernd = Counter(), Counter()
        for g in G:
            p = g["besitzer"]
            if p == 0 or g["typ"] in NICHT_ZAEHLEN:
                continue
            if g["typ"] == BERGFRIED:
                self.spieler.add(p)
            b = self.gebaeude.get((p, g["uid"]))
            if b is None:
                b = self.gebaeude[(p, g["uid"])] = {"typ": g["typ"], "x": g["x"], "y": g["y"], "erst": t, "zuletzt": t,
                                                     "liefer": None}
            b["zuletzt"] = t
            if b["liefer"] is None and g.get("vorrat", 0) > 0 and g["typ"] in BETRIEBE:
                b["liefer"] = t
            anzahl[p] += 1
            if b["liefer"] is not None:
                liefernd[p] += 1
        ass, trupp = Counter(), Counter()
        for e in E:
            p = e.get("besitzer", 0)
            if p == 0 or e.get("leben", 1) <= 0:
                continue
            if e["typ"] == ASSASSINE:
                ass[p] += 1
            if e["typ"] in TRUPPEN:
                trupp[p] += 1
        w = t // FENSTER
        for p in self.spieler:
            f = self.fenster[w][p]
            f["gebaeude"].append(anzahl[p])
            f["liefernd"].append(liefernd[p])
            f["assassinen"].append(ass[p])
            f["truppen"].append(trupp[p])

    def statuszeile(self, t, st, sp):
        self.mit_st.add(sp)
        f = self.fenster[t // FENSTER][sp]
        for k in ("leute", "platz", "feuer", "gold", "holz"):
            if k in st:
                f[k].append(st[k])
        if "feuer" in st and "leute" in st and "platz" in st:
            f["feuer_voll"].append(1 if st["feuer"] >= FEUER_VOLL and st["leute"] < st["platz"] else 0)

    def ertrag(self, zeilen, sp):
        for d in zeilen:
            if "t" not in d:
                continue
            self.mit_ertrag.add(sp)
            s = self.summen[d["t"] // FENSTER][sp]
            s["holz_rein"] += d.get("zug", {}).get("holz", 0)
            s["holz_verbaut"] += d.get("gebaut", {}).get("holz", 0)


# ---- Reihen, hinten ab, Einbruch ------------------------------------------------------------------------------------
def reihe(lauf, sp, groesse):
    """[(Fenster, Wert)] - Mittel je Fenster (Summe bei holz_rein); None, wenn die Groesse fuer den Spieler fehlt."""
    if groesse == "holz_rein" and sp not in lauf.mit_ertrag:
        return None
    if groesse == "leute" and sp not in lauf.mit_st:
        return None
    aus = []
    for w in range(lauf.erste_t // FENSTER, lauf.letzte_t // FENSTER + 1):
        if groesse == "holz_rein":
            aus.append((w, lauf.summen[w][sp]["holz_rein"] if w in lauf.summen else 0))
            continue
        xs = lauf.fenster[w][sp].get(groesse) if w in lauf.fenster and sp in lauf.fenster[w] else None
        if xs:
            aus.append((w, sum(xs) / float(len(xs))))
        else:
            aus.append((w, aus[-1][1] if aus else 0))        # Fenster ohne Runde: letzter Wert
    return aus


def glatt(r):
    aus = []
    for i, (w, _) in enumerate(r):
        xs = [v for _, v in r[max(0, i - GLAETTEN + 1):i + 1]]
        aus.append((w, sum(xs) / float(len(xs))))
    return aus


def hinten_ab(ra, rb):
    """Erstes Fenster, ab dem a bis zum Ende hinten liegt (geglaettet). Eine Fuehrung kuerzer als MIN_STRECKE Fenster
    unterbricht den Rueckstand nicht. None, wenn a am Ende nicht mindestens MIN_STRECKE Fenster hinten liegt."""
    a, b = glatt(ra), glatt(rb)
    n = min(len(a), len(b))
    hinten = [a[i][1] < b[i][1] for i in range(n)]
    if n < MIN_STRECKE or not all(hinten[n - MIN_STRECKE:]):
        return None
    start, i = n - 1, n - 1
    while i >= 0:
        if hinten[i]:
            start = i
            i -= 1
            continue
        j = i
        while j >= 0 and not hinten[j]:
            j -= 1
        if j < 0 or i - j >= MIN_STRECKE:        # lange Fuehrung (oder Spielbeginn) - der Rueckstand beginnt nach ihr
            break
        i = j
    return a[start][0]


def einbruch(ra, rb):
    """(Fenster, Staerke): der Tick, der die Partie am besten in "vorher" und "nachher" teilt - Abstand je Fenster
    r = (b - a) / max(a, b) (geglaettet, -1 bis 1); Staerke = (Mittel r nachher - Mittel r vorher) * Wurzel(n_vor * n_nach / n)
    (die uebliche Kennzahl fuer EINEN Bruchpunkt; sie wertet Teilungen kurz vor dem Ende von selbst ab - 1018j: eine Holz-
    Spitze bei Tick 70.000 schlug die bloessen 3-Fenster-Mittel). Nur Teilungen, nach denen a im Mittel hinten liegt und die
    beiderseits mindestens UMFELD Fenster haben. None ohne solche Teilung."""
    a, b = glatt(ra), glatt(rb)
    n = min(len(a), len(b))
    r = [(b[i][1] - a[i][1]) / max(a[i][1], b[i][1], 1.0) for i in range(n)]
    best = None
    for i in range(UMFELD, n - UMFELD + 1):
        vor, nach = sum(r[:i]) / i, sum(r[i:]) / (n - i)
        staerke = (nach - vor) * (i * (n - i) / float(n)) ** 0.5
        if nach > 0 and staerke > 0 and (best is None or staerke > best[1]):
            best = (a[i][0], staerke)
    return best


def wert(r, w):
    return dict(glatt(r)).get(w)


def mittel_glatt(r, w0, w1):
    xs = [v for w, v in glatt(r) if w0 <= w <= w1]
    return sum(xs) / float(len(xs)) if xs else None


# ---- Warum ----------------------------------------------------------------------------------------------------------
def verluste(lauf, sp, w0, w1):
    """Gebaeude von sp, die in den Fenstern w0..w1 verschwanden: (liefernde je Art, nie gelieferte Betriebe je Art,
    Orte der liefernden im 20er-Raster)."""
    lief, nie, orte = Counter(), Counter(), Counter()
    for (p, _), b in lauf.gebaeude.items():
        if p != sp or b["zuletzt"] >= lauf.letzte_t or not (w0 <= b["zuletzt"] // FENSTER <= w1):
            continue
        if b["liefer"] is not None:
            lief[b["typ"]] += 1
            orte[(b["x"] // 20 * 20, b["y"] // 20 * 20)] += 1
        elif b["typ"] in BETRIEBE:
            nie[b["typ"]] += 1
    return lief, nie, orte


def neubauten(lauf, sp, w0, w1):
    c = Counter()
    for (p, _), b in lauf.gebaeude.items():
        if p == sp and b["erst"] > lauf.erste_t and w0 <= b["erst"] // FENSTER <= w1:
            c[b["typ"]] += 1
    return c


def mittel(lauf, sp, groesse, w0, w1):
    xs = [x for w in range(w0, w1 + 1) for x in lauf.fenster.get(w, {}).get(sp, {}).get(groesse, [])]
    return sum(xs) / float(len(xs)) if xs else None


def summe(lauf, sp, groesse, w0, w1):
    if sp not in lauf.mit_ertrag:
        return None
    return sum(lauf.summen[w][sp][groesse] for w in range(w0, w1 + 1) if w in lauf.summen)


def _c(c):
    return ", ".join("%s %d" % (typname(t), n) for t, n in c.most_common()) or "keine"


def warum(lauf, p, q, w_einbruch, w_hinten):
    """Textzeilen: was in den UMFELD Fenstern vor und nach dem Einbruch bei p (hinten) und q (vorne) geschah; L27 ab w_hinten."""
    w0, w1 = w_einbruch - UMFELD, w_einbruch + UMFELD - 1
    z = ["GESCHEHEN um den Einbruch (Tick %d bis %d) - gemessen, als Ursache nicht bewiesen:" % (
        max(w0 * FENSTER, lauf.erste_t), min((w1 + 1) * FENSTER, lauf.letzte_t))]
    for s in (p, q):
        lief, nie, orte = verluste(lauf, s, w0, w1)
        zeile = "  Spieler %d verlor liefernde Betriebe: %s; verlor Betriebe ohne je gesehene Ware: %s" % (s, _c(lief), _c(nie))
        if orte:
            zeile += "; liefernde verloren bei %s" % ", ".join(
                "(%d-%d, %d-%d) %d" % (x, x + 19, y, y + 19, n) for (x, y), n in orte.most_common(3))
        z.append(zeile)
        z.append("  Spieler %d baute neu: %s" % (s, _c(neubauten(lauf, s, w0, w1))))
    for s in (p, q):
        teile = []
        hr = summe(lauf, s, "holz_rein", w0, w1)
        if hr is not None:
            teile.append("Holz rein %d, verbaut %d" % (hr, summe(lauf, s, "holz_verbaut", w0, w1)))
        for g, n in (("holz", "Holzvorrat"), ("gold", "Gold"), ("assassinen", "Assassinen"), ("liefernd", "liefernde Betriebe")):
            m = mittel(lauf, s, g, w0, w1)
            if m is not None:
                teile.append("%s im Mittel %.1f" % (n, m))
        z.append("  Spieler %d: %s" % (s, "; ".join(teile)))
    voll = [x for v in range(w_hinten, lauf.letzte_t // FENSTER + 1)
            for x in lauf.fenster.get(v, {}).get(p, {}).get("feuer_voll", [])]
    if voll:
        z.append("  L27 Spieler %d ab Tick %d: in %d von %d Runden Feuer voll (mindestens %d Wartende) bei freien Plaetzen%s" % (
            p, w_hinten * FENSTER, sum(voll), len(voll), FEUER_VOLL,
            " - meistens; dann kommen nach L27 keine neuen Leute: es fehlen Arbeitsplaetze, nicht Wohnplaetze"
            if 2 * sum(voll) >= len(voll) else ""))
    return z


# ---- Gesamt ---------------------------------------------------------------------------------------------------------
def vergleiche(reihen, p, q):
    """(hinten ab je Kennzahl, Einbruch je Kennzahl, Werte) fuer p gegenueber q."""
    ab, bruch, werte = {}, {}, {}
    for g in KENNZAHLEN:
        rp, rq = reihen[p][g], reihen[q][g]
        if rp is None or rq is None:
            continue
        if g not in NUR_EINBRUCH:
            k = hinten_ab(rp, rq)
            if k is not None:
                ab[g] = k
        e = einbruch(rp, rq)
        if e is not None and (g in ab or g in NUR_EINBRUCH):
            bruch[g] = e
        if g in ab or g in bruch:
            werte[g] = {"ende": [glatt(rp)[-1][1], glatt(rq)[-1][1]]}
            if g in ab:
                werte[g]["ab"] = [wert(rp, ab[g]), wert(rq, ab[g])]
            if g in bruch:
                w = bruch[g][0]
                werte[g]["vor"] = [mittel_glatt(rp, w - UMFELD, w - 1), mittel_glatt(rq, w - UMFELD, w - 1)]
                werte[g]["nach"] = [mittel_glatt(rp, w, w + UMFELD - 1), mittel_glatt(rq, w, w + UMFELD - 1)]
    return ab, bruch, werte


def auswerten(lauf, nur=None):
    """Je Spielerpaar und Richtung: hinten ab (je Kennzahl), Einbruch, Werte, Geschehen. nur=sp: nur Paare mit diesem
    Spieler (der Lenker gegen jeden Gegner; ohne: alle Paare)."""
    spieler = sorted(lauf.spieler)
    reihen = {sp: {g: reihe(lauf, sp, g) for g in KENNZAHLEN} for sp in spieler}
    paare = []
    for i, a in enumerate(spieler):
        for b in spieler[i + 1:]:
            if nur is not None and nur not in (a, b):
                continue
            for p, q in ((a, b), (b, a)):
                ab, bruch, werte = vergleiche(reihen, p, q)
                if not ab:
                    continue
                erster = min(ab.values())
                # Ursache wird bei der Wirtschaft gesucht, Truppen und Assassinen sind ihre Folge (Gold aus der Wirtschaft;
                # 1018i/1018j: liefernde Betriebe brachen bei 15.000/17.000, Truppen erst bei 26.000/23.000)
                g_e = max((g for g in bruch if g in WIRTSCHAFT), key=lambda g: bruch[g][1], default=None) or \
                    max(bruch, key=lambda g: bruch[g][1], default=None)
                w_e = bruch[g_e][0] if g_e else erster
                paare.append({"hinten": p, "vorne": q, "ab": ab, "erster": erster, "einbruch": bruch,
                              "entscheidend": [g_e, w_e], "werte": werte, "warum": warum(lauf, p, q, w_e, erster)})
    return {"paare": paare, "reihen": reihen, "spieler": spieler, "mit_st": sorted(lauf.mit_st),
            "mit_ertrag": sorted(lauf.mit_ertrag), "von": lauf.erste_t, "bis": lauf.letzte_t, "vorbei": lauf.vorbei}


def _zahl(x):
    return "-" if x is None else ("%.0f" % x if abs(x) >= 10 else "%.1f" % x)


def _paar(v):
    return "%s zu %s" % (_zahl(v[0]), _zahl(v[1]))


def text(erg):
    z = ["VERGLEICH Spieler %s, Tick %s bis %s%s (Fenster %d Ticks, gleitend ueber %d; Statuszeile fuer %s, Ertrag fuer %s)" % (
        erg["spieler"], erg["von"], erg["bis"], " - bei %s fehlte ein Bergfried" % erg["vorbei"] if erg.get("vorbei") else "",
        FENSTER, GLAETTEN, erg["mit_st"] or "keinen", erg["mit_ertrag"] or "keinen")]
    if not erg["paare"]:
        z.append("VERGLEICH: in keiner der gemessenen Kennzahlen liegt ein Spieler bis zum Ende dauerhaft hinten")
    for pa in sorted(erg["paare"], key=lambda x: (x["erster"], x["hinten"])):
        p, q, wt = pa["hinten"], pa["vorne"], pa["werte"]
        z.append("NACHTEIL Spieler %d gegenueber Spieler %d: hinten ab Tick %d - je Kennzahl ab Tick (Spieler %d zu %d dort -> "
                 "am Ende): %s" % (p, q, pa["erster"] * FENSTER, p, q, "; ".join(
                     "%s %d (%s -> %s)" % (NAME[g], w * FENSTER, _paar(wt[g]["ab"]), _paar(wt[g]["ende"]))
                     for g, w in sorted(pa["ab"].items(), key=lambda kv: kv[1]))))
        g_e, w_e = pa["entscheidend"]
        if g_e:
            z.append("EINBRUCH Spieler %d ab Tick %d: %s - Mittel der %d Ticks davor %s, danach %s (Spieler %d zu %d)" % (
                p, w_e * FENSTER, ("am staerksten brach die Wirtschaft ein: " if g_e in WIRTSCHAFT else "") + NAME[g_e],
                UMFELD * FENSTER, _paar(wt[g_e]["vor"]), _paar(wt[g_e]["nach"]), p, q))
            z.append("KETTE Spieler %d (alle Einbrueche nach Zeit, Staerke in Klammern): %s" % (p, "; ".join(
                "%d %s %s -> %s (%.1f)" % (pa["einbruch"][g][0] * FENSTER, NAME[g], _paar(wt[g]["vor"]), _paar(wt[g]["nach"]),
                                          pa["einbruch"][g][1])
                for g in sorted(pa["einbruch"], key=lambda g: (pa["einbruch"][g][0], g)))))
        z.extend(pa["warum"])
    return "\n".join(z)


# ---- Dateien --------------------------------------------------------------------------------------------------------
def lies_ertrag(pfad):
    aus = []
    for z in open(pfad, encoding="utf-8"):
        try:
            aus.append(json.loads(z))
        except ValueError:
            continue                            # letzte Zeile beim Abbruch halb geschrieben
    return aus


def spieler_aus_name(pfad):
    m = re.search(r"_sp(\d+)\.jsonl", os.path.basename(pfad))
    return int(m.group(1)) if m else 1


def analyse(lage_pfade, ertrag_pfade=(), haupt_sp=None, nur=None):
    """lage_pfade[0] = Haupt-Lageprotokoll (Gebaeude/Einheiten aller); jedes Protokoll liefert die Statuszeile seines Spielers."""
    from lageprotokoll import runden
    lauf = Lauf()
    sp0 = haupt_sp or spieler_aus_name(lage_pfade[0])
    for t, st, E, G in runden(lage_pfade[0]):
        lauf.runde(t, st, E, G, sp_st=sp0)
    for pf in lage_pfade[1:]:
        sp = spieler_aus_name(pf)
        if sp == sp0 or not os.path.exists(pf):
            continue
        for t, st, E, G in runden(pf):
            if t is not None and lauf.erste_t <= t <= lauf.letzte_t:
                lauf.statuszeile(t, st, sp)
    for pf in ertrag_pfade:
        if pf and os.path.exists(pf):
            lauf.ertrag(lies_ertrag(pf), spieler_aus_name(pf))
    return auswerten(lauf, nur)


def sichern(erg, pfad):
    aus = dict(erg)
    aus["reihen"] = {str(sp): d for sp, d in erg["reihen"].items()}
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(aus, f, ensure_ascii=False)
    return pfad


def main():
    lage = [a for a in sys.argv[1:] if "=" not in a]
    arg = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    erg = analyse(lage, [p for p in arg.get("ertrag", "").split(",") if p])
    print(text(erg))
    if arg.get("json"):
        print("gesichert:", sichern(erg, arg["json"]))


if __name__ == "__main__":
    main()
