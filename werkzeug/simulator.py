# -*- coding: utf-8 -*-
"""B-250 Gehirn, Baustein 3: Takt-fuer-Takt-Simulator (Daniel 25.10.2026 21:53 "ja ... simulator bauen").

Aus EINEM Auge-Schnappschuss wird das Gefecht Takt fuer Takt nach den Regeln des Spiels weitergerechnet - nichts
geschaetzt, jede Regel mit Quelle. Ausgabe wie Gehirn.prognose: {opfer_id: dict(verlust, quellen, art, besitzer, leben)}.

ZIEL (vor dem Bau festgelegt): auf dem Pruefstein 200603 bei H = 90 mindestens 90 % der Verluste aus Kaempfen, die im
Fenster erst beginnen, auf dem richtigen Opfer ("neue_begegnungen_erfasst"), ohne dass Opfer-Quote und Praezision von
Baustein 1/2 fallen. ABBRUCH: bleibt es unter 75 %, fehlt eine Auge-Regel - dann an SRE melden, keine Werte nachstellen.

Regeln je Takt:
  1 Laufen      L190: ein Zug alle (calculatedMovementSpeed + stateBasedSpeed + moveDelay + 1) Takte um (stateBasedSpeed + 1)
                Mikroschritte zur Mitte (x*8+4) des naechsten Wegpunkts, Feld = Mikro // 8; Blick = Laufrichtung (AU19)
  2 Feindsuche  AU19: im Suchtakt ((Takt & Maske) == (fixedRng & Maske)) closestEnemyMicroDistance = kleinster Feinabstand (P15)
                zur Feindliste (AU20: ganze Liste ohne Artfilter; NAEHERUNG: die Liste selbst - Feld +856, Alter bis 60 Takte -
                kennt das Auge im alten Protokoll nicht)
  3 Nahkampf    AU18 + AU20: nur Arten mit UNIT_CAN_MELEE; Ausloeser attackedUnitID != 0 oder Abstand <= 50 / 150 (isSelectable)
                / 270 (stateBasedSpeed >= 1); eigenes Feld + 24 Felder nach Blickrichtung (auge.nahkampf_reihenfolge), Hoehe +-32;
                auf einem Feld die kleinste Einheitennummer (AU20: Feldkette aufsteigend); Behalten, solange das alte Ziel das
                erste Feind eines Felds ist; Gegenzuweisung an ein Opfer ohne Ziel; Blick dreht NICHT zum Ziel (L190); Laeufer
                laufen bis zur Wegpunkt-Mitte, dann Schaden melee_damage je Takt (P23)
  4 Schuetzen   AU6/AU20/P14: Schuss im Schussschritt der Phasentabelle, je takt.schuss_zyklus; Neuwahl am Ende jedes
                Schiess-Durchgangs und wenn das Ziel tot ist: Feinde im Kreis dx^2+dy^2 <= Reichweite^2 (geschoss.reichweite),
                Meuchelmoerder nur mit Sichtwert <= 160, Punktzahl P14 (groesster Achsabstand in Mikroschritten, je Zielklasse
                umgerechnet), kleinste gewinnt, bei Gleichstand die kleinste Nummer; Bogen und arab. Bogen markieren ihr Ziel
                beim Zielen/Schiessen, ein Neuwaehler nimmt das beste UNMARKIERTE Ziel, wenn dessen Punktzahl < 1,5 x beste;
                neues Ziel nach Tod: Zielen + Schiessen bis zum Schussschritt (Bogen 48 Takte, AU6 gemessen 44-46)
  5 Geschosse   in der Luft: Landetakt (sre_rest_takte) auf die anvisierte Einheit am Zielfeld (+-1), sonst Feind auf dem Feld
  6 Tod         Leben <= 0 -> stirbt, verlaesst sofort die Felder
Nicht enthalten: neue Befehle (Absicht der Gegner-KI), neue Einheiten, freie Schusslinie, Fremdtreffer vor dem Ziel (AU20),
Zug-Phase je Einheit (Zaehler nicht gelesen), Feuer, Gebaeude.
Stand 25.10. 23:15 mit AU22 (Zug-Phase aus der Vorgeschichte) und Schuetzen-Blick (gehirn_pruefen ... 90 30 ... sim):
200603 neue Begegnungen 90,4 % (ZIEL >= 90 erreicht), Opfer-Quote 98,3 %, Praezision 94,6 %; Gegenprobe 191847 83,6 % / 96,0 % /
95,7 % (Baustein 2: 54 % bzw. 51 %). Daniel 22:51 (ueber SRE): Ziel ist 100 %, 95-99 % nur uebergangsweise.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)

import gehirn  # noqa: E402

# AU20 (3): UNIT_CAN_MELEE[Art] (UnitPropertiesDefinedData +31540)
KANN_NAHKAMPF = {3, 5, 6, 7, 19, 21, 22, 23, 24, 25, 26, 27, 28, 35, 37, 45, 52, 55, 57, 67, 70, 71, 72, 73, 74, 75, 76}
MEUCHEL = 73
LAUF_ZUSTAENDE = (101, 105, 120, 124)       # gemessen 200603: in diesen Zustaenden aendert sich das Mikro-Feld
NAH = 106
STERBEN = set(range(110, 117))
# P14 Zielklassen fuer Pfeil/Bolzen: (Faktor, Zuschlag)
_KLASSE = {}
for _a in (22, 23, 70, 74):
    _KLASSE[_a] = (1, 75)
for _a in (24, 25, 26, 27, 28, 71, 72, 73, 75):
    _KLASSE[_a] = (5, 200)
_KLASSE[29] = (7, 300)
for _a in (30, 55):
    _KLASSE[_a] = (2, 100)
_KLASSE[76] = (1, 0)
_SONST = (10, 400)
GESCHOSS_ET = {22: 1, 70: 1, 74: 1, 23: 7, 72: 33}        # Schuetzenart -> Geschossart (gehirn.GESCHOSS_TABELLE_*)
MARKIEREN = (22, 70)                                   # AU20: nur Bogen und arab. Bogen markieren ihr Ziel


def _richtung8(dx, dy):
    """Naechste der 8 Blickrichtungen nach Winkel (0 = N, im Uhrzeigersinn) - gemessen: so blicken Schuetzen beim Zielen
    (237 von 277) und Schiessen (1.973 von 2.162 Takten) auf ihr Ziel."""
    import math
    if not dx and not dy:
        return None
    return int(round(math.atan2(dx, -dy) / (math.pi / 4))) % 8


def _fein(dx, dy):
    dx, dy = abs(dx), abs(dy)
    mx, mn = max(dx, dy), min(dx, dy)
    return mx + (0.4 * mn * mn / mx if mx else 0.0)


_RICHTUNG = {0: (0, -1), 1: (1, -1), 2: (1, 0), 3: (1, 1), 4: (0, 1), 5: (-1, 1), 6: (-1, 0), 7: (-1, -1)}   # auge.RICHTUNG
_RICHTUNG_NR = {v: k for k, v in _RICHTUNG.items()}


class _E(object):
    __slots__ = ("id", "typ", "own", "mx", "my", "h", "leben", "tot", "zustand", "ziel", "start_ziel", "fr", "msk", "cemd",
                 "sel", "sbs", "tpm", "weg", "dest", "blick", "zaehler", "nah", "sicht", "schuss_n", "schuss_ziel", "letzt")

    @property
    def feld(self):
        return (self.mx // 8, self.my // 8)


class Simulator(object):
    # Schalter fuer die Einzelmessung jeder Regel (gehirn_pruefen sim)
    NEUWAHL = True
    FEUERVERTEILUNG = True
    KETTE_AUFSTEIGEND = True
    VERTEILUNG_ALLE = True          # AU21: "unmarkiert bevorzugt" gilt fuer jeden, der acquireShootTarget ruft
    # AU21: Zielflagge = Zaehler +988 = Anzahl Schuetzen, die das Ziel gerade haben (+ je Wahl im Takt) -> Punktzahl + 50 x Anzahl
    ZIELFLAGGE = "anzahl"           # "beschossen" = alte SAI-Lesart Ja/Nein, None = aus
    EINHEIT_FUER_EINHEIT = True     # AU21: updateUnits arbeitet die Einheiten aufsteigend ab
    REIHE_IN_EINHEIT = "nsl"
    # Lesart (SAI, gemessen): wer per Gegenzuweisung ein Ziel bekommt, bleibt sofort stehen - ohne sie verliert die Abarbeitung
    # je Einheit das Fenster 41.458 (Laeufer 160/162/169/170 schlagen bei +80 zurueck), mit ihr gleich der Phasen-Reihenfolge
    GEGEN_STOPPT = True
    SCHUETZEN_BLICK = True          # Schuetzen drehen beim Zielen/Schiessen zum Ziel (gemessen, 91 % der Schiess-Takte)        # je Einheit: n = Nahkampf, s = Feindsuche, l = Laufen (gemessen, s. Register L190)

    def __init__(self, sw):
        self.G = gehirn.Gehirn(sw)
        self.sw = sw
        import auge
        self.auge = auge
        self._reihen = {f: auge.nahkampf_reihenfolge(f) for f in range(8)}
        rt = sw["tabellen"].get("geschoss.reichweite")
        self.reichweite = rt["werte"] if rt else []
        try:
            import spielwerte
            rueck = {v: k for k, v in spielwerte.UT.items()}
            self.ohne_liste = {rueck[n] for n in ("TRADER", "TRADERHORSE", "CAMEL", "GHOST", "MOTHER", "CHILD") if n in rueck}
        except Exception:  # noqa: BLE001
            self.ohne_liste = set()
        self._gewaehlt = {}
        self.phasen = {}
        for ut, z in auge._phasen_tabellen().items():
            if ut == "hacken" or z.get("schuss_schritt") is None:
                continue
            ph = z["phasen"]
            n_z, sp_z, _ = ph["zielen"]
            n_s, sp_s, _ = ph["schiessen"]
            ss = z["schuss_schritt"]
            self.phasen[ut] = {"vor": ss * (sp_s + 1), "zielen": n_z * (sp_z + 1), "nach": (n_s - ss) * (sp_s + 1)}

    # ------------------------------------------------------------------------------------------------- Aufbau
    def _aufbau(self, einheiten, seit=None):
        """seit: {nr: Takte seit der letzten Zug-Gelegenheit} (AU22) - aus den Feldern +848/+852 oder der Vorgeschichte."""
        U = {}
        for e in einheiten:
            if e.get("dying") or e["state"] in STERBEN or not e["id"]:      # AU22: Nr 0 ist keine Einheit
                continue
            u = _E()
            u.id, u.typ, u.own = e["id"], e["unitType"], e["owner"]
            u.mx, u.my = e["mikro"]
            u.h = e.get("terrainOrClimbHeight", 0)
            u.leben = float(e["health"])
            u.tot = False
            u.zustand = e["state"]
            u.ziel = e.get("attackedUnitID") or 0
            u.start_ziel = u.ziel if e["state"] == NAH else 0
            u.fr, u.msk = e.get("fixedRng", 0), e.get("enemyNoticeFrequencyUnk", 0)
            u.cemd = e.get("closestEnemyMicroDistance", 0)
            u.sel = e.get("isSelectable_OR_matchTime", 0) == 1
            u.sicht = e.get("assassinsMicroDistanceToEnemyUnk", 32000)
            u.sbs = e.get("stateBasedSpeed", 0)
            u.tpm = e.get("calculatedMovementSpeed", 0) + u.sbs + e.get("moveDelay", 0) + 1
            u.weg = [tuple(p) for p in (e.get("sre_wegpunkte") or [])] if e["state"] in LAUF_ZUSTAENDE else []
            # NAEHERUNG (191847, Takt 41.291: Meuchelmoerder 172 hatte 4 Wegpunkte bis (152,292), Ziel (151,291) - im Spiel lief
            # er weiter): der Wegplan im Schnappschuss ist nur ein Abschnitt; danach geradeaus zum Ziel
            d = tuple(e.get("destination") or (0, 0))
            u.dest = d if u.weg and d != (0, 0) and d != tuple(e["feld"]) else None
            u.blick = e.get("facingDirection", 0)
            # AU22: Zaehler +852 - Merker +848 = Takte seit der letzten Zug-Gelegenheit; ohne sie Phase unbekannt (Mitte)
            u.zaehler = seit[u.id] if seit and u.id in seit else u.tpm // 2
            u.nah = u.typ in KANN_NAHKAMPF
            u.schuss_n = e.get("sre_naechster_schuss_takte")
            u.schuss_ziel = e.get("shootTargetedUnit") or 0
            u.letzt = None
            U[u.id] = u
        felder = {}
        for u in U.values():
            felder.setdefault(u.feld, []).append(u.id)
        if self.KETTE_AUFSTEIGEND:
            for f in felder:
                felder[f].sort()
        else:                                   # alte Lesart: Reihenfolge der Kette nextUnitOnTheSameTile
            nach = {e["id"]: e.get("nextUnitOnTheSameTile") or 0 for e in einheiten}
            auf = set(v for v in nach.values() if v)
            for f, ids in felder.items():
                if len(ids) > 1:
                    kopf = [i for i in ids if i not in auf] or ids[:1]
                    reihe, i, ges = [], kopf[0], set()
                    while i and i in U and i not in ges and U[i].feld == f:
                        reihe.append(i)
                        ges.add(i)
                        i = nach.get(i, 0)
                    felder[f] = reihe + [i for i in ids if i not in ges]
        return U, felder

    def _feld_rein(self, felder, u):
        liste = felder.setdefault(u.feld, [])
        if self.KETTE_AUFSTEIGEND:
            k = 0
            while k < len(liste) and liste[k] < u.id:
                k += 1
            liste.insert(k, u.id)
        else:
            liste.insert(0, u.id)

    @staticmethod
    def _feld_raus(felder, u, f=None):
        try:
            felder[f or u.feld].remove(u.id)
        except (KeyError, ValueError):
            pass

    # ------------------------------------------------------------------------------------------------- Regeln
    @staticmethod
    def _feind(a, b):
        return b.own != a.own and b.own != 0 and not b.tot

    def _suche(self, U, u):
        """AU19-AU21: kleinster Abstand (ganzzahlig, auge._spiel_abstand) zur Feindliste; NAEHERUNG der Liste: alle lebenden
        Einheiten anderer Spieler ohne Haendler/Pferd/Kamel/Geist/Mutter/Kind - die echte ist bis zu 60 Takte alt und ohne
        versteckte (+856), beides steht nicht im Protokoll."""
        best = None
        for v in U.values():
            if v.tot or v.own == u.own or v.own == 0 or v.typ in self.ohne_liste:
                continue
            d = self.auge._spiel_abstand(v.mx - u.mx, v.my - u.my)
            if best is None or d < best:
                best = d
        if best is not None:
            u.cemd = int(best)

    def _erster_feind(self, U, felder, u, f):
        for i in felder.get(f, ()):
            v = U[i]
            if self._feind(u, v) and abs(v.h - u.h) <= 32:
                return v
        return None

    def _nahkampf_wahl(self, U, felder, u):
        """processMeleeInitiation (AU18) - gibt das Ziel oder None."""
        if not u.nah or u.tot:
            return None
        schwelle = 270 if u.sbs >= 1 else (150 if u.sel else 50)
        if not u.ziel and u.cemd > schwelle:
            return None
        fx, fy = u.feld
        erste = []
        for dx, dy in self._reihen.get(u.blick, [(0, 0)]):
            v = self._erster_feind(U, felder, u, (fx + dx, fy + dy))
            if v is not None:
                erste.append(v)
        if not erste:
            return None
        if u.ziel and any(v.id == u.ziel for v in erste):
            return U[u.ziel]
        return erste[0]

    def _punkte(self, u, v, beschossen=()):
        """P14: groesster Achsabstand in Mikroschritten (+ 50 x Zielflagge), je Zielklasse umgerechnet (Pfeil/Bolzen)."""
        d = max(abs(u.mx - v.mx), abs(u.my - v.my))
        if self.ZIELFLAGGE == "beschossen" and v.id in beschossen:
            d += 50
        elif self.ZIELFLAGGE == "anzahl":
            d += 50 * beschossen.get(v.id, 0)
        f, z = _KLASSE.get(v.typ, _SONST)
        return d * f + z

    def _markiert(self, U, k, ausser):
        """AU20: Ziele, die ein Bogen/arab. Bogen gerade beim Zielen oder Schiessen hat."""
        m = set()
        for w in U.values():
            if w.id == ausser or w.tot or w.typ not in MARKIEREN or not w.schuss_ziel or w.schuss_n is None:
                continue
            p = self.phasen.get(w.typ)
            if not p:
                continue
            start = w.schuss_n - p["vor"] - p["zielen"]
            if start <= k <= w.schuss_n + p["nach"] or (w.letzt is not None and k <= w.letzt + p["nach"]):
                m.add(w.schuss_ziel)
        m |= self._gewaehlt.get(k, set())        # AU21: jeder Schuetze markiert sein neues Ziel im Takt der Wahl
        return m

    def _neuwahl(self, U, u, k):
        """acquireShootTarget (AU20/P14) - gibt die Zielnummer oder 0."""
        et = GESCHOSS_ET.get(u.typ)
        r = self.reichweite[et] if et is not None and et < len(self.reichweite) else 0
        fx, fy = u.feld
        kand = []
        beschossen = {}
        if self.ZIELFLAGGE:
            for w in U.values():
                if w.id != u.id and not w.tot and w.schuss_ziel:
                    beschossen[w.schuss_ziel] = beschossen.get(w.schuss_ziel, 0) + 1
        for v in sorted(U.values(), key=lambda x: x.id):
            if not v.id or not self._feind(u, v):      # Nummer 0 heisst im Spiel "kein Ziel"
                continue
            vx, vy = v.feld
            if (vx - fx) ** 2 + (vy - fy) ** 2 > r * r:
                continue
            if v.typ == MEUCHEL and v.sicht > 160:
                continue
            kand.append((self._punkte(u, v, beschossen), v.id))
        if not kand:
            return 0
        best = min(kand)                       # Gleichstand: kleinste Nummer
        wahl = self._wahl(U, u, k, kand, best)
        if wahl:
            self._gewaehlt.setdefault(k, set()).add(wahl)
        return wahl

    def _wahl(self, U, u, k, kand, best):
        if self.FEUERVERTEILUNG and (u.typ in MARKIEREN or self.VERTEILUNG_ALLE):
            m = self._markiert(U, k, u.id)
            frei = [x for x in kand if x[1] not in m]
            if frei:
                bf = min(frei)
                if bf[0] < 1.5 * best[0]:
                    return bf[1]
        return best[1]

    def _laufen_alle(self, U, felder):
        """L190 (P13 + Messung): Zug alle tpm Takte um (stateBasedSpeed + 1) Mikroschritte zur Wegpunkt-Mitte."""
        for u in U.values():
            self._laufen(u, felder)

    def _laufen(self, u, felder):
        """AU22: jede lebende Einheit zaehlt je Takt hoch; ist der Abstand > cMS + sBS + moveDelay, ist Zug-Gelegenheit - der
        Merker springt auch dann, wenn sie nicht laeuft."""
        if u.tot:
            return
        u.zaehler += 1
        if u.zaehler < u.tpm:
            return
        u.zaehler = 0
        if not u.weg:
            return
        alt = u.feld
        if len(u.weg) == 1 and u.dest and u.weg[0] != u.dest:
            fx, fy = u.weg[0]
            if max(abs(fx - u.dest[0]), abs(fy - u.dest[1])) <= 40:
                u.weg.append((fx + (u.dest[0] > fx) - (u.dest[0] < fx), fy + (u.dest[1] > fy) - (u.dest[1] < fy)))
        for _ in range(u.sbs + 1):
            if not u.weg:
                break
            zx, zy = u.weg[0][0] * 8 + 4, u.weg[0][1] * 8 + 4
            dx, dy = (zx > u.mx) - (zx < u.mx), (zy > u.my) - (zy < u.my)
            u.mx += dx
            u.my += dy
            if (dx, dy) in _RICHTUNG_NR:
                u.blick = _RICHTUNG_NR[(dx, dy)]
            if (u.mx, u.my) == (zx, zy):
                u.weg.pop(0)
        if u.feld != alt:
            self._feld_raus(felder, u, alt)
            self._feld_rein(felder, u)

    # ------------------------------------------------------------------------------------------------- Lauf
    def zug_phasen(self, s, vorgeschichte=None):
        """{nr: Takte seit der letzten Zug-Gelegenheit}: live/neue Protokolle aus +848/+852 (auge.takte_bis_zug), sonst aus der
        Vorgeschichte (auge.zug_gelegenheiten ueber die Schnappschuesse VOR s und s selbst - nichts aus der Zukunft)."""
        aus = {}
        roh = s.einheiten
        idx = s._einheiten_idx if getattr(s, "_einheiten_idx", None) is not None else None
        namen = roh.dtype.names or ()
        if "field216_0x354" in namen and idx is not None:
            for j, nr in enumerate(idx):
                aus[int(nr)] = int(roh[j]["field216_0x354"]) - int(roh[j]["field215_0x350"])
            return aus
        if not vorgeschichte:
            return aus
        kette = list(vorgeschichte) + [s]
        t0 = int(s.takt)
        for nr in (idx if idx is not None else ()):
            g = self.auge.zug_gelegenheiten(kette, int(nr))
            if g:
                aus[int(nr)] = t0 - g[-1]
        return aus

    def prognose(self, s, horizont=90, einheiten=None, protokoll=False, vorgeschichte=None):
        einheiten = einheiten if einheiten is not None else s.einheiten_liste()
        U, felder = self._aufbau(einheiten, self.zug_phasen(s, vorgeschichte))
        t0 = s.kopf()["takt"]
        aus = {}
        spur = [] if protokoll else None
        anfang = {u.id: u.leben for u in U.values()}

        def schaden(v, menge, quelle):
            if v.tot or menge <= 0:
                return
            m = min(menge, v.leben)
            z = aus.setdefault(v.id, {"verlust": 0.0, "quellen": [], "art": v.typ, "besitzer": v.own, "leben": anfang[v.id]})
            z["verlust"] += m
            z["quellen"].append(quelle)
            v.leben -= m
            if v.leben <= 0:
                v.tot = True
                self._feld_raus(felder, v)

        # Geschosse in der Luft: Landetakt -> Opfer
        landen = {}
        for g in s.geschosse():
            tab = gehirn.GESCHOSS_TABELLE_ET.get(g.get("entityType"))
            if tab is None or g.get("sre_zustand") not in (None, "fliegt"):
                continue
            rest = g.get("sre_rest_takte")
            if rest is None or rest > horizont:
                continue
            landen.setdefault(max(1, int(rest)), []).append(("luft", g, tab))
        # Schuetzen: naechster Schuss (Phasenrest, AU6)
        entscheid = {}
        for u in U.values():
            if u.typ not in gehirn.GESCHOSS_TABELLE_UT:
                u.schuss_n = None
                continue
            z = U.get(u.schuss_ziel) if u.schuss_ziel else None
            if z is None or z.own == u.own:
                u.schuss_ziel = 0
            if u.schuss_n is not None:
                u.schuss_n = max(1, int(u.schuss_n))
                # die Neuwahl nach dem LETZTEN Durchgang kann noch im Fenster liegen (Schuss vor t0, Durchgangsende danach)
                p = self.phasen.get(u.typ)
                zyk = self.G.zyklus[u.typ] if u.typ < len(self.G.zyklus) and self.G.zyklus[u.typ] else None
                if self.NEUWAHL and p and zyk:
                    kd = u.schuss_n - zyk + p["nach"]
                    if 1 <= kd < u.schuss_n:
                        u.letzt = u.schuss_n - zyk
                        entscheid.setdefault(kd, []).append(u)
            # untaetige Schuetzen ohne Ziel suchen NICHT von selbst (AU20: Neuwahl nur nach einem Schiess-Durchgang, bei totem
            # Ziel, als Trupp-Anfuehrer alle 32 / am Sammelplatz alle 40 Takte) - gemessen: mit Selbstsuche 3,3-fache Menge

        def nahkampf(u, k):
            if u.tot or not u.nah:
                return
            v = self._nahkampf_wahl(U, felder, u)
            if v is None:
                if u.ziel:
                    u.ziel = 0
                    if u.zustand == NAH:
                        u.zustand = 1
                return
            neu = v.id != u.ziel
            u.ziel = v.id
            u.zustand = NAH
            u.weg = u.weg[:1]
            u.dest = None
            if neu and v.nah and not v.ziel:          # AU18 (6) Gegenzuweisung (ohne Drehen, L190)
                v.ziel = u.id
                if self.GEGEN_STOPPT:
                    v.weg, v.dest = [], None
            if spur is not None:
                spur.append((k, u.id, v.id))
            if u.weg:
                return
            je = self.G._nah({"unitType": u.typ}, {"unitType": v.typ})
            art = "nahkampf" if u.start_ziel == v.id else "begegnung"
            schaden(v, je, {"art": art, "angreifer": u.id, "je_takt": je, "takt": k})

        reihe = sorted(U)
        self._gewaehlt = {}
        for k in range(1, horizont + 1):
            t = t0 + k
            if self.EINHEIT_FUER_EINHEIT:
                # AU21: updateUnits aufsteigend - je Einheit Laufen, Feindsuche, Nahkampf; Kleinere stehen schon am neuen Ort
                for i in reihe:
                    u = U[i]
                    for schritt in self.REIHE_IN_EINHEIT:
                        if schritt == "l":
                            self._laufen(u, felder)
                        elif schritt == "s":
                            if not u.tot and u.msk and self.auge.sucht_im_takt(t, u.fr, u.msk):
                                self._suche(U, u)
                        else:
                            nahkampf(u, k)
            else:
                self._laufen_alle(U, felder)
                for u in U.values():
                    if not u.tot and u.msk and self.auge.sucht_im_takt(t, u.fr, u.msk):
                        self._suche(U, u)
                for i in reihe:
                    nahkampf(U[i], k)
            # 4 Schuetzen - Blick zum Ziel ab Beginn des Zielens (gemessen, s. _richtung8)
            if self.SCHUETZEN_BLICK:
                for u in U.values():
                    p = self.phasen.get(u.typ)
                    if u.tot or u.schuss_n is None or not p or not u.schuss_ziel:
                        continue
                    if u.schuss_n - p["vor"] - p["zielen"] <= k <= u.schuss_n:
                        z = U.get(u.schuss_ziel)
                        if z is not None and not z.tot:
                            r = _richtung8(z.mx - u.mx, z.my - u.my)
                            if r is not None:
                                u.blick = r
            for u in U.values():
                if u.tot or u.schuss_n != k:
                    continue
                if u.zustand == NAH:
                    u.schuss_n = None
                    continue
                p = self.phasen.get(u.typ)
                z = U.get(u.schuss_ziel) if u.schuss_ziel else None    # 0 = kein Ziel (Einheit 0 gibt es trotzdem)
                if (z is None or z.tot) and self.NEUWAHL and p:
                    # Ziel tot/ungueltig: neu waehlen, dann zielen und schiessen bis zum Schussschritt (AU6: 44-46 Takte)
                    u.schuss_ziel = self._neuwahl(U, u, k)
                    u.schuss_n = k + p["zielen"] + p["vor"] if u.schuss_ziel else k + 1
                    continue
                if z is None or z.tot:
                    u.schuss_n = None
                    continue
                flug = int(round(max(abs(u.feld[0] - z.feld[0]), abs(u.feld[1] - z.feld[1])) / gehirn.FELDER_JE_TAKT))
                landen.setdefault(k + max(1, flug), []).append(("schuss", u, z))
                if spur is not None:
                    spur.append(("schuss", k, u.id, z.id))
                u.letzt = k
                zyk = self.G.zyklus[u.typ] if u.typ < len(self.G.zyklus) and self.G.zyklus[u.typ] else None
                u.schuss_n = k + zyk if zyk else None
                if self.NEUWAHL and p:                 # AU20: Neuwahl am Ende des Schiess-Durchgangs
                    entscheid.setdefault(k + p["nach"], []).append(u)
            for u in entscheid.pop(k, ()):
                if not u.tot and u.zustand != NAH:
                    u.schuss_ziel = self._neuwahl(U, u, k) or u.schuss_ziel
            # 5 Geschosse landen
            for art, a, b in landen.pop(k, ()):
                if art == "luft":
                    g, tab = a, b
                    ziel = tuple(g.get("ziel_feld") or ())
                    opfer = U.get(g.get("unitID"))
                    if opfer is None or opfer.tot or not ziel or max(abs(opfer.feld[0] - ziel[0]), abs(opfer.feld[1] - ziel[1])) > 1:
                        opfer = None
                        for i in felder.get(ziel, ()):
                            if U[i].own != g.get("owner") and not U[i].tot:
                                opfer = U[i]
                                break
                    if opfer is not None:
                        schaden(opfer, self.G._geschoss_schaden(tab, opfer.typ),
                                {"art": "geschoss", "uid": g.get("uid"), "schuetze": g.get("unitID_OR_seaGullID"), "takt": k})
                else:
                    u, z = a, b
                    if not z.tot:
                        schaden(z, self.G._geschoss_schaden(gehirn.GESCHOSS_TABELLE_UT[u.typ], z.typ),
                                {"art": "schuss", "schuetze": u.id, "takt": k})
        if protokoll:
            return aus, spur, U
        return aus
