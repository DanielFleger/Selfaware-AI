# -*- coding: utf-8 -*-
"""B-250 Gehirn, Baustein 3: Takt-fuer-Takt-Simulator (Daniel 25.10.2026 21:53 "ja ... simulator bauen").

Aus EINEM Auge-Schnappschuss wird das Gefecht Takt fuer Takt nach den Regeln des Spiels weitergerechnet - nichts
geschaetzt, jede Regel mit Quelle. Ausgabe wie Gehirn.prognose: {opfer_id: dict(verlust, quellen, art, besitzer, leben)}.

ZIEL (vor dem Bau festgelegt): auf dem Pruefstein 200603 bei H = 90 mindestens 90 % der Verluste aus Kaempfen, die im
Fenster erst beginnen, auf dem richtigen Opfer ("neue_begegnungen_erfasst"), ohne dass Opfer-Quote und Praezision von
Baustein 1/2 fallen. ABBRUCH: bleibt es unter 75 %, fehlt eine Auge-Regel - dann an SRE melden, keine Werte nachstellen.

Regeln je Takt (Reihenfolge wie updateUnits 0x00579300, soweit bekannt):
  1 Laufen      ein Mikroschritt alle (calculatedMovementSpeed + stateBasedSpeed + moveDelay + 1) Takte, 8 je Feld, schraeg
                wie gerade, zur Feldmitte des naechsten Wegpunkts (sre_wegpunkte); Feld = Mikro // 8 (gemessen hier 25.10.:
                Bogen im Trupp 4 Takte je Mikroschritt = 32 je Feld, Armbrust 3, Meuchelmoerder 2). Blick = laufender
                Wegschritt (AU19)
  2 Feindsuche  im Suchtakt (AU19: (Takt & Maske) == (fixedRng & Maske)) neuer closestEnemyMicroDistance = kleinster
                Feinabstand (P15) zu lebenden Soldaten anderer Spieler (NAEHERUNG, siehe FEIND_ARTEN unten)
  3 Nahkampf    processMeleeInitiation (AU18): Ausloeser attackedUnitID != 0 oder closestEnemyMicroDistance <= 50 / 150
                (isSelectable) / 270 (stateBasedSpeed >= 1); Suchraum eigenes Feld + 24 Felder nach Blickrichtung
                (auge.nahkampf_reihenfolge), Hoehe +-32; Behalten, solange das alte Ziel das erste Feind eines Felds ist;
                sonst erstes Feind des ersten besetzten Felds; Gegenzuweisung an ein Opfer ohne Ziel; Schaden melee_damage
                je Takt (P23); ein Kaempfer bleibt stehen (Weg geloescht - gemessen: nach dem Kampf Ziel = eigenes Feld)
  4 Schuesse    Geschosse in der Luft und Schuetzen wie Baustein 1 (Landetakt, naechster Schuss + Flug, je Zyklus) - aber
                nur, solange Schuetze und Ziel im Simulator leben und der Schuetze nicht im Nahkampf steht
  5 Tod         Leben <= 0 -> stirbt, verlaesst sofort die Felder; wer ihn als Ziel hatte, waehlt im naechsten Takt neu
Nicht enthalten: neue Befehle (Absicht der Gegner-KI), neue Einheiten, Zielwechsel der Schuetzen (+44-46 Takte, AU6),
Feuer, Gebaeude.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)

import gehirn  # noqa: E402

# NAEHERUNG (gemessen am Pruefstein 25.10., an SRE als offene Auge-Regel): Nahkampf beginnen nur Soldaten und Art 52 -
# Arbeiter stehen zwar in melee_damage, waren aber nie im Zustand 106 (8.989 Takte). Als Feind fuer den Abstand zaehlen
# Soldaten anderer Spieler, Arbeiter nie (Beispiel Takt 40.987: Arbeiter 425 auf 102 Feinmass, gespeichert 112 = Bogen).
KAEMPFER = set(range(22, 31)) | set(range(70, 80)) | {52}
FEIND_ARTEN = set(range(22, 31)) | set(range(70, 80)) | {52, 55}
MEUCHEL = 73
LAUF_ZUSTAENDE = (101, 105, 120, 124)       # gemessen: in diesen Zustaenden aendert sich das Mikro-Feld
NAH = 106
STERBEN = set(range(110, 117))


def _fein(dx, dy):
    dx, dy = abs(dx), abs(dy)
    mx, mn = max(dx, dy), min(dx, dy)
    return mx + (0.4 * mn * mn / mx if mx else 0.0)


def _richtung(dx, dy):
    sx = (dx > 0) - (dx < 0)
    sy = (dy > 0) - (dy < 0)
    for k, v in _RICHTUNG.items():
        if v == (sx, sy):
            return k
    return None


_RICHTUNG = {0: (0, -1), 1: (1, -1), 2: (1, 0), 3: (1, 1), 4: (0, 1), 5: (-1, 1), 6: (-1, 0), 7: (-1, -1)}   # auge.RICHTUNG


class _E(object):
    __slots__ = ("id", "typ", "own", "mx", "my", "h", "leben", "tot", "zustand", "ziel", "fr", "msk", "cemd", "sel",
                 "sbs", "tpm", "weg", "blick", "zaehler", "kette", "lauf", "kaempfer", "schuss_n", "schuss_ziel",
                 "start_ziel")

    @property
    def feld(self):
        return (self.mx // 8, self.my // 8)


class Simulator(object):
    def __init__(self, sw):
        self.G = gehirn.Gehirn(sw)
        self.sw = sw
        import auge
        self.auge = auge
        self._reihen = {f: auge.nahkampf_reihenfolge(f) for f in range(8)}

    # ------------------------------------------------------------------------------------------------- Aufbau
    def _aufbau(self, s, einheiten):
        U = {}
        for e in einheiten:
            if e.get("dying") or e["state"] in STERBEN:
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
            u.sbs = e.get("stateBasedSpeed", 0)
            u.tpm = e.get("calculatedMovementSpeed", 0) + u.sbs + e.get("moveDelay", 0) + 1
            u.weg = [tuple(p) for p in (e.get("sre_wegpunkte") or [])] if e["state"] in LAUF_ZUSTAENDE else []
            u.lauf = bool(u.weg)
            u.blick = e.get("facingDirection", 0)
            u.zaehler = u.tpm // 2          # Phase des Mikroschritts unbekannt (Restfehler hoechstens tpm Takte)
            u.kaempfer = u.typ in KAEMPFER
            u.schuss_n = e.get("sre_naechster_schuss_takte")
            u.schuss_ziel = e.get("shootTargetedUnit") or 0
            U[u.id] = u
        # Feldkette: Reihenfolge wie UnitLayer -> nextUnitOnTheSameTile (Kopf = auf den keiner zeigt)
        nach = {e["id"]: e.get("nextUnitOnTheSameTile") or 0 for e in einheiten}
        auf = set(v for v in nach.values() if v)
        felder = {}
        for u in U.values():
            felder.setdefault(u.feld, []).append(u.id)
        for f, ids in felder.items():
            if len(ids) > 1:
                kopf = [i for i in ids if i not in auf] or ids[:1]
                reihe, i, ges = [], kopf[0], set()
                while i and i in U and i not in ges and U[i].feld == f:
                    reihe.append(i)
                    ges.add(i)
                    i = nach.get(i, 0)
                reihe += [i for i in ids if i not in ges]
                felder[f] = reihe
        return U, felder

    # ------------------------------------------------------------------------------------------------- Regeln
    def _feind(self, a, b):
        return b.own != a.own and b.own != 0 and not b.tot

    def _suche(self, U, u):
        """Feindsuche (P15/AU19), NAEHERUNG der Feindmenge (s. FEIND_ARTEN)."""
        best = None
        for v in U.values():
            if v.tot or v.own == u.own or v.own == 0 or v.typ not in FEIND_ARTEN:
                continue
            if v.typ == MEUCHEL and not self._aufgedeckt(U, v):
                continue
            d = _fein(u.mx - v.mx, u.my - v.my)
            if best is None or d < best:
                best = d
        if best is not None:
            u.cemd = int(best)

    @staticmethod
    def _aufgedeckt(U, m):
        """P15: Meuchelmoerder sichtbar, wenn ein Aufdecker (isSelectable) der Gegenseite <= 160 Mikroschritte nah ist."""
        for v in U.values():
            if not v.tot and v.own != m.own and v.own != 0 and v.sel and _fein(v.mx - m.mx, v.my - m.my) <= 160:
                return True
        return False

    def _erster_feind(self, U, felder, u, f):
        for i in felder.get(f, ()):
            v = U[i]
            if self._feind(u, v) and abs(v.h - u.h) <= 32:
                return v
        return None

    def _nahkampf_wahl(self, U, felder, u):
        """processMeleeInitiation (AU18) - gibt das Ziel oder None."""
        if not u.kaempfer or u.tot:
            return None
        schwelle = 270 if u.sbs >= 1 else (150 if u.sel else 50)
        if not u.ziel and u.cemd > schwelle:
            return None
        fx, fy = u.feld
        reihe = self._reihen.get(u.blick, [(0, 0)])
        erste = []
        for dx, dy in reihe:
            v = self._erster_feind(U, felder, u, (fx + dx, fy + dy))
            if v is not None:
                erste.append(v)
        if not erste:
            return None
        if u.ziel and u.ziel in U and any(v.id == u.ziel for v in erste):
            return U[u.ziel]
        return erste[0]

    LAUF_ZULETZT = False

    def _laufen_alle(self, U, felder):
        """P13 + Messung 25.10. (Pruefstein 200603, 30.000 Schritte): alle (calculatedMovementSpeed + stateBasedSpeed +
        moveDelay + 1) Takte ein Zug um (stateBasedSpeed + 1) Mikroschritte - Rennen (stateBasedSpeed >= 1) springt 2 bzw.
        4 Mikroschritte je Zug; Ziel jedes Zugs ist die Mitte (x*8+4) des naechsten Wegpunkts."""
        for u in U.values():
            if u.tot or not u.weg:
                continue
            u.zaehler += 1
            if u.zaehler < u.tpm:
                continue
            u.zaehler = 0
            alt = u.feld
            for _ in range(u.sbs + 1):
                if not u.weg:
                    break
                zx, zy = u.weg[0][0] * 8 + 4, u.weg[0][1] * 8 + 4
                dx, dy = (zx > u.mx) - (zx < u.mx), (zy > u.my) - (zy < u.my)
                u.mx += dx
                u.my += dy
                r = _richtung(dx, dy)
                if r is not None:
                    u.blick = r
                if (u.mx, u.my) == (zx, zy):
                    u.weg.pop(0)
            if u.feld != alt:
                try:
                    felder[alt].remove(u.id)
                except (KeyError, ValueError):
                    pass
                felder.setdefault(u.feld, []).insert(0, u.id)      # NAEHERUNG: Neuankoemmling vorn in der Kette

    # ------------------------------------------------------------------------------------------------- Lauf
    def prognose(self, s, horizont=90, einheiten=None, protokoll=False):
        einheiten = einheiten if einheiten is not None else s.einheiten_liste()
        U, felder = self._aufbau(s, einheiten)
        t0 = s.kopf()["takt"]
        aus = {}
        spur = [] if protokoll else None

        def treffer(v, menge, quelle):
            if menge <= 0:
                return
            z = aus.setdefault(v.id, {"verlust": 0.0, "quellen": [], "art": v.typ, "besitzer": v.own,
                                      "leben": v.leben + 0.0})
            z["verlust"] += menge
            z["quellen"].append(quelle)

        def schaden(v, menge, quelle):
            if v.tot:
                return
            m = min(menge, v.leben)
            # Leben zum Start (fuer den Deckel in der Pruefung): erster Eintrag merkt sich das Leben vor dem ersten Treffer
            treffer(v, m, quelle)
            v.leben -= m
            if v.leben <= 0:
                v.tot = True
                try:
                    felder[v.feld].remove(v.id)
                except (KeyError, ValueError):
                    pass

        # Geschosse in der Luft (Baustein 1): Landetakt -> Opfer
        landen = {}
        for g in s.geschosse():
            tab = gehirn.GESCHOSS_TABELLE_ET.get(g.get("entityType"))
            if tab is None or g.get("sre_zustand") not in (None, "fliegt"):
                continue
            rest = g.get("sre_rest_takte")
            if rest is None or rest > horizont:
                continue
            landen.setdefault(max(1, int(rest)), []).append((g, tab))
        # Schuetzen: naechster Schuss -> Flugzeit -> Landung
        schuesse = {}
        for u in U.values():
            tab = gehirn.GESCHOSS_TABELLE_UT.get(u.typ)
            if tab is None or not u.schuss_ziel or u.schuss_ziel not in U or u.schuss_n is None:
                continue
            if U[u.schuss_ziel].own == u.own:
                continue
            schuesse.setdefault(max(1, int(u.schuss_n)), []).append(u.id)

        anfang = {u.id: u.leben for u in U.values()}
        for k in range(1, horizont + 1):
            t = t0 + k
            # 1 Laufen (gemessen am Pruefstein: wer im Takt k ein neues Feld betritt, wird erst ab k+1 gewaehlt - Laufen
            #   steht deshalb hinter dem Nahkampf, s. LAUF_ZULETZT)
            if not self.LAUF_ZULETZT:
                self._laufen_alle(U, felder)
            # 2 Feindsuche
            for u in U.values():
                if not u.tot and u.msk and self.auge.sucht_im_takt(t, u.fr, u.msk):
                    self._suche(U, u)
            # 3 Nahkampf
            for u in list(U.values()):
                if u.tot or not u.kaempfer:
                    continue
                v = self._nahkampf_wahl(U, felder, u)
                if v is None:
                    if u.ziel:
                        u.ziel = 0
                        if u.zustand == NAH:
                            u.zustand = 1
                    continue
                neu = v.id != u.ziel
                u.ziel = v.id
                u.zustand = NAH
                # gemessen (Takt 41.446, Armbrust 157): wer im Laufen ein Ziel waehlt, laeuft noch bis zur Mitte seines
                # Wegpunkts und schlaegt erst dann zu (5 Takte spaeter); Stehende schlagen sofort
                u.weg = u.weg[:1]
                if not u.weg:
                    r = _richtung(v.mx - u.mx, v.my - u.my)
                    if r is not None:
                        u.blick = r
                if neu and v.kaempfer and not v.ziel:          # AU18 (6) Gegenzuweisung
                    v.ziel = u.id
                    rv = _richtung(u.mx - v.mx, u.my - v.my)
                    if rv is not None:
                        v.blick = rv
                if spur is not None:
                    spur.append((k, u.id, v.id))
                if u.weg:
                    continue
                je = self.G._nah({"unitType": u.typ}, {"unitType": v.typ})
                art = "nahkampf" if u.start_ziel == v.id else "begegnung"
                schaden(v, je, {"art": art, "angreifer": u.id, "je_takt": je, "takt": k})
            if self.LAUF_ZULETZT:
                self._laufen_alle(U, felder)
            # 4 Geschosse
            for g, tab in landen.get(k, ()):
                if tab is None:
                    continue
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
            for i in schuesse.pop(k, ()):
                u = U[i]
                z = U.get(u.schuss_ziel)
                if u.tot or u.zustand == NAH or z is None or z.tot:
                    continue
                flug = int(round(max(abs(u.feld[0] - z.feld[0]), abs(u.feld[1] - z.feld[1])) / gehirn.FELDER_JE_TAKT))
                landen.setdefault(k + max(1, flug), []).append(({"entityType": None, "unitID": z.id, "ziel_feld": z.feld,
                                                                  "owner": u.own, "_schuss": u.id}, None))
                zyk = self.G.zyklus[u.typ] if u.typ < len(self.G.zyklus) and self.G.zyklus[u.typ] else None
                if zyk:
                    schuesse.setdefault(k + zyk, []).append(i)
            # Schuesse aus dem Simulator landen (eigene Liste, Tabelle nach Schuetzenart)
            for g, tab in [x for x in landen.get(k, ()) if x[1] is None]:
                u = U[g["_schuss"]]
                z = U.get(g["unitID"])
                if z is None or z.tot:
                    continue
                tabu = gehirn.GESCHOSS_TABELLE_UT.get(u.typ)
                schaden(z, self.G._geschoss_schaden(tabu, z.typ), {"art": "schuss", "schuetze": u.id, "takt": k})
        for i, z in aus.items():
            z["leben"] = anfang.get(i, z["leben"])
        if protokoll:
            return aus, spur, U
        return aus
