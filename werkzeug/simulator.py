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
Nicht enthalten: neue Befehle (Absicht der Gegner-KI), neue Einheiten, freie Schusslinie, Zufalls-Fehlschuss
(AU25, SEC_RNG), alte Feindliste nach Lastverteiler (alte Protokolle ohne ihn), Feuer, Gebaeude.
Stand 26.10. 00:05 mit AU23-AU25 (Suche vor allen Bewegungen, Eilen zur Feldmitte, Gegenzuweisung mit Blick, Fremdtreffer
je ueberflogenem Feld ueber auge.bahn_neu / sre_bahn, Schuetzen-Drehung nur im Zielen je Takt ein Achtel, Vorhalt 133/100)
- gehirn_pruefen ... 90 30 ... sim: 200603 neue Begegnungen 95,2 %, Opfer-Quote 98,8 %, Praezision 98,7 %, Menge 1,000,
Geschoss-Zeit +-5 91,5 %; Gegenprobe 191847 87,1 % / 96,2 % / 96,7 % (Baustein 2: 54 % bzw. 51 %). Daniels Ziel: 100 %.
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
MARKIEREN = (22, 70)
JAEGER = 6                                             # AU27: Jaeger schiesst Wild (Art 44) mit Pfeilen
SCHUSS_TAB_UT = dict(gehirn.GESCHOSS_TABELLE_UT)
SCHUSS_TAB_UT[JAEGER] = "einheit.arrow_damage"
GESCHOSS_ET[JAEGER] = 1                                   # AU20: nur Bogen und arab. Bogen markieren ihr Ziel


def _richtung8(dx, dy):
    """Naechste der 8 Blickrichtungen nach Winkel (0 = N, im Uhrzeigersinn) - gemessen: so blicken Schuetzen beim Zielen
    (237 von 277) und Schiessen (1.973 von 2.162 Takten) auf ihr Ziel."""
    import math
    if not dx and not dy:
        return None
    return int(round(math.atan2(dx, -dy) / (math.pi / 4))) % 8


def _zielrichtung(x, y, tx, ty):
    """AU25 calculatePreferredRelativeOrientation 0x0046C9E0 (aus FELDERN): None = gleiches Feld."""
    dx, dy = abs(tx - x), abs(ty - y)
    if not dx and not dy:
        return None
    if 2 * dy < dx:
        return 6 if tx < x else 2
    if 2 * dx < dy:
        return 0 if ty < y else 4
    if ty < y:
        return 1 if x <= tx else 7
    return 5 if tx < x else 3


def _drehe(blick, ziel):
    """AU25 setUnitFacingDirectionTowardsTarget 0x0052FD00: je Takt ein Achtel, kuerzester Weg, bei Gegenrichtung +1."""
    d = (ziel - blick) % 8
    if d == 0:
        return blick
    return (blick + 1) % 8 if d <= 4 else (blick - 1) % 8


def _fein(dx, dy):
    dx, dy = abs(dx), abs(dy)
    mx, mn = max(dx, dy), min(dx, dy)
    return mx + (0.4 * mn * mn / mx if mx else 0.0)


_RICHTUNG = {0: (0, -1), 1: (1, -1), 2: (1, 0), 3: (1, 1), 4: (0, 1), 5: (-1, 1), 6: (-1, 0), 7: (-1, -1)}   # auge.RICHTUNG
_RICHTUNG_NR = {v: k for k, v in _RICHTUNG.items()}


class _E(object):
    __slots__ = ("id", "typ", "own", "mx", "my", "h", "leben", "tot", "zustand", "ziel", "start_ziel", "fr", "msk", "cemd",
                 "sel", "sbs", "tpm", "weg", "dest", "blick", "zaehler", "nah", "sicht", "schuss_n", "schuss_ziel", "letzt", "hz",
                 "versteckt", "klettert", "schritt", "leer_n", "leer_art")

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
    GEGEN_STOPPT = False            # AU23: Opfer laufen bis zur Feldmitte weiter (14/14); Stopp mass 191847 +1,1 Punkte (offen)
    SCHUETZEN_BLICK = True
    SUCHE_ZUERST = True             # AU23: Feindsuche im ersten Durchgang von updateUnits, alle Lagen vom Vortakt
    EILEN = True                    # AU23: mit Ziel im Laufen +978 = 1 -> je Zug ein Mikroschritt mehr bis zur Feldmitte
    GEGEN_BLICK = True
    FREMDTREFFER = True
    VORHALT = True
    LEERLAUF = True                 # AU28: untaetige Schuetzen ohne Trupp suchen am Ende jeder Leerlauf-Animation                  # AU25: Vorhalt bei laufendem Ziel             # AU4/AU24: Geschoss prueft je Takt das ueberflogene Feld (auge.bahn_neu / sre_bahn)              # AU23: Gegenzuweisung setzt beim Opfer attackedUnitID UND Blickrichtung          # Schuetzen drehen beim Zielen/Schiessen zum Ziel (gemessen, 91 % der Schiess-Takte)        # je Einheit: n = Nahkampf, s = Feindsuche, l = Laufen (gemessen, s. Register L190)

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
        self._liste, self._geister, self._teams = None, {}, None
        self.jaeger = self._jaeger_tabelle()
        self.phasen = {}
        for ut, z in auge._phasen_tabellen().items():
            if ut == "hacken" or z.get("schuss_schritt") is None:
                continue
            ph = z["phasen"]
            if "zielen" not in ph or "schiessen" not in ph or "nachladen" not in ph:
                continue                            # einphasige Tabellen (Jaeger, Geraete) - eigener Weg
            n_z, sp_z, _ = ph["zielen"]
            n_s, sp_s, _ = ph["schiessen"]
            ss = z["schuss_schritt"]
            n_l, sp_l, _ = ph["nachladen"]
            self.phasen[ut] = {"vor": ss * (sp_s + 1), "zielen": n_z * (sp_z + 1), "nach": (n_s - ss) * (sp_s + 1),
                               "laden": n_l * (sp_l + 1)}

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
            u.hz = u.h + (e.get("buildingHeight") or 0)          # AU4: Einheitenhoehe fuer Geschoss-Treffer
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
            u.schritt = e.get("animationCycleNumber", 0)
            u.leer_n, u.leer_art = None, None
            u.versteckt = bool(e.get("unknownTestAgainst0_2_versteckt") or 0)      # +856 (AU21/AU23)
            u.klettert = bool(e.get("usingTeleport") or 0)                          # +670: Zaehler steht (AU22)
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

    def _team(self, o):
        t = self._teams
        return int(t[o]) if t and o < len(t) else o

    def _liste_bauen(self, U, p):
        """AU23 recomputeTroopValuesForPlayer: lebend, nicht versteckt, anderes Team (Besitzer 0 zaehlt mit), ohne Haendler & Co."""
        tp = self._team(p)
        return {v.id for v in U.values() if not v.tot and not v.versteckt and v.typ not in self.ohne_liste and self._team(v.own) != tp}

    def _suche(self, U, u):
        """AU19-AU23/AU26: kleinster Abstand (ganzzahlig) zur Feindliste des Spielers; mit Lastverteiler die ALTE Liste
        (Mitglieder vom letzten Neubau, Tote mit ihrer letzten Lage, ohne Lebenspruefung), sonst alle lebenden Feinde."""
        best = None
        if self._liste is not None:
            ids = self._liste.get(u.own)
            if ids is None:
                ids = self._liste[u.own] = self._liste_bauen(U, u.own)
            lagen = [(U[i].mx, U[i].my) for i in ids if i in U] + [self._geister[i] for i in ids if i not in U and i in self._geister]
        else:
            lagen = [(v.mx, v.my) for v in U.values() if not v.tot and v.own not in (0, u.own) and v.typ not in self.ohne_liste]
        for vx, vy in lagen:
            d = self.auge._spiel_abstand(vx - u.mx, vy - u.my)
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
        if self._liste is not None:                    # AU20: Kandidaten = Feindliste des Spielers (aufsteigend)
            ids = self._liste.get(u.own)
            if ids is None:
                ids = self._liste[u.own] = self._liste_bauen(U, u.own)
            menge = [U[i] for i in sorted(ids) if i in U and not U[i].tot]
        else:
            menge = [v for v in sorted(U.values(), key=lambda x: x.id) if self._feind(u, v)]
        for v in menge:
            if not v.id:                               # Nummer 0 heisst im Spiel "kein Ziel"
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

    # AU28: Leerlauf untaetiger Schuetzen ohne Trupp - Dauer der Animation bis zum naechsten Zustand 0 (gemessen von SRE)
    #   Bogen 22: Zustand 8, Speed 5, gerade Nummer 34 / ungerade 42 Bilder (203 / 251 Takte); Feind > 400 -> 11 (sitzt)
    #   Armbrust 23: Zustand 2 (Feind <= 400) 102 / 122 Takte, Zustand 1 (Feind > 400) 327 / 211, nach fixedRng gerade/ungerade;
    #               Zustand 1 bricht ab, sobald der Feind <= 400 ist
    #   arab. Bogen 70: Zustand 8, 173 Takte
    LEER_SUCHE = 400

    def _leer_dauer(self, u, zustand):
        if u.typ == 22:
            return (34 if u.id % 2 == 0 else 42) * 6, 6
        if u.typ == 23:
            g = u.fr % 2 == 0
            return ((102 if g else 122), 4) if zustand == 2 else ((327 if g else 211), 4)
        if u.typ == 70:
            return 173, 6
        return None, None

    def _leer_start(self, u, k):
        """Neuer Leerlauf ab Takt k (Zustand 0 ohne Ziel) - setzt u.leer_n auf den naechsten Versuch."""
        if u.typ == 22 and u.cemd > self.LEER_SUCHE:
            u.leer_n, u.leer_art = None, 11            # sitzt (Rueckweg unbekannt)
            return
        z = 2 if (u.typ != 23 or u.cemd <= self.LEER_SUCHE) else 1
        d, _ = self._leer_dauer(u, z)
        u.leer_n, u.leer_art = (k + d, z) if d else (None, None)

    def _jaeger_tabelle(self):
        """AU27 UpdateHunter: Zustand 10 = EINE Bildtabelle (spielwerte.SCHUSS[6]), Speed 2, Pfeil im ersten Takt des Schritts mit
        Bild 22. Gelesen wie auge._phasen_tabellen (live, sonst Referenz-Exe). -> {n, sp, ss} oder None."""
        try:
            import spielwerte
            z = spielwerte.SCHUSS[JAEGER]
            name, adr, sp = z["phasen"][0]
            try:
                self.auge.speicher.griff()
                lies = self.auge.speicher.lies
            except Exception:  # noqa: BLE001
                lies = spielwerte.quelle_datei(spielwerte.REFERENZ_EXE)[1]
            roh = lies(adr, 200)
            b = [(x if x < 128 else x - 256) for x in roh]
            n = next((i for i, v in enumerate(b) if v < 1), 200)
            bild = int(z["schuss_bei"].split()[1])
            ss = next(i for i, v in enumerate(b[:n]) if v == bild)
            return {"n": n, "sp": sp, "ss": ss}
        except Exception:  # noqa: BLE001
            return None

    def _jaeger_bis_schuss(self, u, z):
        """AU27: Zustand 9 dreht je Takt ein Achtel (AU25), ausgerichtet -> 10 ab Schritt 0; Zustand 10 Schritt c."""
        j = self.jaeger
        tsch = j["sp"] + 1
        if u.zustand == 10:
            c = u.schritt
            if c < j["ss"]:
                return (j["ss"] - c - 1) * tsch + tsch // 2 + 1
            return None if c > j["ss"] else 1
        # AU29: Zustand 9 wartet, bis der Jaeger in der Feldmitte steht (Zugregel AU22, Schleichtempo), dann ein Achtel je Takt
        cx, cy = u.feld[0] * 8 + 4, u.feld[1] * 8 + 4
        rest = max(abs(cx - u.mx), abs(cy - u.my))
        warten = max(0, rest * u.tpm - u.zaehler) if rest else 0
        r = _zielrichtung(u.feld[0], u.feld[1], z.feld[0], z.feld[1])
        dreh = 0 if r is None else min((r - u.blick) % 8, (u.blick - r) % 8)
        return warten + dreh + 1 + j["ss"] * tsch

    def _bahn(self, u, z):
        """AU24: Flugbahn des geplanten Schusses von u auf z (Feldmitte des Ziels, Zielhoehe Boden + 30; Vorhalt fehlt)."""
        et = GESCHOSS_ET.get(u.typ)
        if et is None or et not in self.auge.SCHUSS_KURVE:
            return []
        plus = self.auge.ABSCHUSS_HOEHE_PFERD if u.typ == 72 else self.auge.ABSCHUSS_HOEHE.get(et, 30)
        zx, zy = z.feld
        tx, ty = zx * 8 + 4, zy * 8 + 4
        if self.VORHALT and z.weg:
            # AU25 prepareProjectileTarget 0x0053CBD0: laufendes Ziel + v Mikroschritte in SEINER Blickrichtung,
            # i = Strecke * 133 // 100 (Strecke = Sichtlinie max(|dx|,|dy|) - 1), v nach Tempo
            i = (max(abs(tx - u.mx), abs(ty - u.my)) - 1) * 133 // 100
            cms = z.tpm - 1 - z.sbs
            v = i // 8 if z.sbs else (i // 16 if cms < 2 else i // (cms * 16))
            ddx, ddy = _RICHTUNG.get(z.blick, (0, 0))
            tx, ty = tx + ddx * v, ty + ddy * v
        return self.auge.bahn_neu((u.mx, u.my), u.hz + plus, (tx, ty), z.hz + 30, et)

    def _laufen_alle(self, U, felder):
        """L190 (P13 + Messung): Zug alle tpm Takte um (stateBasedSpeed + 1) Mikroschritte zur Wegpunkt-Mitte."""
        for u in U.values():
            self._laufen(u, felder)

    def _laufen(self, u, felder):
        """AU22: jede lebende Einheit zaehlt je Takt hoch; ist der Abstand > cMS + sBS + moveDelay, ist Zug-Gelegenheit - der
        Merker springt auch dann, wenn sie nicht laeuft."""
        if u.tot or u.klettert:
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
        for _ in range(u.sbs + 1 + (1 if self.EILEN and u.ziel else 0)):
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

    def prognose(self, s, horizont=90, einheiten=None, protokoll=False, vorgeschichte=None, teams=None):
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
        fluege = []
        for g in s.geschosse():
            tab = gehirn.GESCHOSS_TABELLE_ET.get(g.get("entityType"))
            if tab is None or g.get("sre_zustand") not in (None, "fliegt"):
                continue
            rest = g.get("sre_rest_takte")
            if rest is None or rest > horizont:
                continue
            if self.FREMDTREFFER and g.get("sre_bahn"):
                fluege.append({"bahn": {int(b[0]): b for b in g["sre_bahn"]}, "ende": int(g["sre_bahn"][-1][0]), "own": g.get("owner"),
                               "tab": tab, "quelle": {"art": "geschoss", "uid": g.get("uid"), "schuetze": g.get("unitID_OR_seaGullID")}})
                continue
            landen.setdefault(max(1, int(rest)), []).append(("luft", g, tab))
        # Schuetzen: naechster Schuss (Phasenrest, AU6)
        entscheid = {}
        for u in U.values():
            if u.typ == JAEGER and self.jaeger and u.zustand in (9, 10) and u.schuss_ziel and u.schuss_ziel in U:
                if u.schuss_n is None:          # AU29: in Zustand 10 vor dem Schuss liefert das Auge ihn exakt, sonst selbst
                    u.schuss_n = self._jaeger_bis_schuss(u, U[u.schuss_ziel])
                u.schuss_n = max(1, int(u.schuss_n)) if u.schuss_n is not None else None
                continue
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
            elif self.LEERLAUF and u.typ in (22, 23, 70) and not u.weg and u.zustand in (0, 1, 2, 8):
                # AU28: untaetig - naechster Versuch am Ende der laufenden Leerlauf-Animation (Rest aus dem Schritt)
                if u.zustand == 0:
                    u.leer_n, u.leer_art = 1, 0
                else:
                    d, tsch = self._leer_dauer(u, u.zustand)
                    if d:
                        u.leer_n, u.leer_art = max(1, d - u.schritt * tsch), u.zustand

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
            if neu and v.nah and not v.ziel:          # AU18 (6) / AU23 Gegenzuweisung: Ziel + Blick zum Waehlenden
                v.ziel = u.id
                if self.GEGEN_BLICK:
                    r = _richtung8(u.mx - v.mx, u.my - v.my)
                    if r is not None:
                        v.blick = r
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
        # AU20/AU26: Feindlisten je Spieler, neu gebaut nur bei Lastverteiler = Spieler + 10/60/100/160
        lv0 = getattr(s, "lastverteiler", None)
        lv0 = None if lv0 is None or int(lv0) < 0 else int(lv0)
        t_ = getattr(s, "teams", None)
        self._teams = list(teams) if teams else (list(t_) if t_ and any(int(x) for x in t_) else None)
        self._liste = None if lv0 is None else {}
        self._geister = {}
        spieler = sorted(set(u.own for u in U.values() if u.own))
        if self._liste is not None:
            kette = list(vorgeschichte or []) + [s]
            for p in spieler:
                for back in range(len(kette)):
                    # gebaut im Takt t0-back aus dem Stand des Vortakts (kette[-2-back])
                    if self.auge.feindliste_neu((lv0 - back) % 200, p) and len(kette) >= back + 2:
                        alt = kette[-2 - back]
                        ids = self.auge.feindliste(alt, p, teams=self._teams)
                        self._liste[p] = set(ids)
                        for e in alt.einheiten_liste():
                            if e["id"] in self._liste[p] and e["id"] not in U:
                                self._geister[e["id"]] = tuple(e["mikro"])
                        break
        for k in range(1, horizont + 1):
            t = t0 + k
            if self._liste is not None:
                for p in spieler:
                    if self.auge.feindliste_neu((lv0 + k) % 200, p):
                        self._liste[p] = self._liste_bauen(U, p)
            if self.SUCHE_ZUERST:
                for i in reihe:
                    u = U[i]
                    if not u.tot and u.msk and self.auge.sucht_im_takt(t, u.fr, u.msk):
                        self._suche(U, u)
            if self.EINHEIT_FUER_EINHEIT:
                # AU21: updateUnits aufsteigend je Einheit (Nahkampf vor dem eigenen Laufen, gemessen)
                for i in reihe:
                    u = U[i]
                    for schritt in self.REIHE_IN_EINHEIT:
                        if schritt == "s" and self.SUCHE_ZUERST:
                            continue
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
            # 4 Schuetzen - AU25: nur im Zielen (5) je Takt ein Achtel zur Zielrichtung (aus Feldern); Schiessen/Nachladen
            #   halten die Richtung
            if self.SCHUETZEN_BLICK:
                for u in U.values():
                    p = self.phasen.get(u.typ)
                    if u.tot or u.schuss_n is None or not p or not u.schuss_ziel:
                        continue
                    if u.schuss_n - p["vor"] - p["zielen"] <= k < u.schuss_n - p["vor"]:
                        z = U.get(u.schuss_ziel)
                        if z is not None and not z.tot:
                            r = _zielrichtung(u.feld[0], u.feld[1], z.feld[0], z.feld[1])
                            if r is not None:
                                u.blick = _drehe(u.blick, r)
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
                bahn = self._bahn(u, z) if self.FREMDTREFFER else []
                if bahn:
                    fluege.append({"bahn": {k + int(b[0]): b for b in bahn[1:]}, "ende": k + int(bahn[-1][0]), "own": u.own,
                                   "tab": SCHUSS_TAB_UT[u.typ], "quelle": {"art": "schuss", "schuetze": u.id}})
                else:
                    flug = int(round(max(abs(u.feld[0] - z.feld[0]), abs(u.feld[1] - z.feld[1])) / gehirn.FELDER_JE_TAKT))
                    landen.setdefault(k + max(1, flug), []).append(("schuss", u, z))
                if spur is not None:
                    spur.append(("schuss", k, u.id, z.id))
                u.letzt = k
                zyk = self.G.zyklus[u.typ] if u.typ < len(self.G.zyklus) and self.G.zyklus[u.typ] else None
                if u.typ == JAEGER:
                    # AU29: nie zweimal dasselbe Wild (getroffenes stirbt), danach Anschleichen zum naechsten (2-480 Takte) -
                    # der naechste Pfeil faellt fruehestens 75 + 1 + 2 + 83 + 62 Takte spaeter: nicht im Fenster
                    zyk = None
                u.schuss_n = k + zyk if zyk else None
                if self.NEUWAHL and p:                 # AU20: Neuwahl am Ende des Schiess-Durchgangs
                    entscheid.setdefault(k + p["nach"], []).append(u)
            for u in entscheid.pop(k, ()):
                if not u.tot and u.zustand != NAH:
                    u.schuss_ziel = self._neuwahl(U, u, k) or u.schuss_ziel
            # AU28: Leerlauf - Zustand 0 sucht, wenn der naechste Feind <= 400 ist; sonst neue Animation
            if self.LEERLAUF:
                for u in U.values():
                    if u.leer_n is None or u.tot or u.zustand == NAH:
                        continue
                    if u.leer_art == 1 and u.typ == 23 and u.cemd <= self.LEER_SUCHE:
                        u.leer_n = k                      # Zustand 1 bricht ab, sobald der Feind nah ist
                    if u.leer_n != k:
                        continue
                    z = self._neuwahl(U, u, k) if u.cemd <= self.LEER_SUCHE else 0
                    p = self.phasen.get(u.typ)
                    if z and p:
                        # gemessen 200603: nach der Wahl Nachladen (4), Zielen (5), Schiessen bis zum Pfeil
                        u.schuss_ziel, u.leer_n = z, None
                        u.schuss_n = k + p["laden"] + p["zielen"] + p["vor"]
                    else:
                        self._leer_start(u, k)
            # 5a Geschosse im Flug: erstes fremdes Ziel auf dem ueberflogenen Feld (Kette aufsteigend, Hoehe [Einheit, +42])
            for f in list(fluege):
                b = f["bahn"].get(k)
                if b is not None:
                    h, fx, fy = b[3], b[4], b[5]
                    for i in felder.get((fx, fy), ()):
                        v = U[i]
                        if v.tot or v.own == f["own"]:
                            continue
                        if v.hz <= h <= v.hz + 42:
                            q = dict(f["quelle"], takt=k)
                            schaden(v, self.G._geschoss_schaden(f["tab"], v.typ), q)
                            fluege.remove(f)
                            break
                    else:
                        if k >= f["ende"]:
                            fluege.remove(f)
                elif k > f["ende"]:
                    fluege.remove(f)
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
                        schaden(z, self.G._geschoss_schaden(SCHUSS_TAB_UT[u.typ], z.typ),
                                {"art": "schuss", "schuetze": u.id, "takt": k})
        if protokoll:
            return aus, spur, U
        return aus
