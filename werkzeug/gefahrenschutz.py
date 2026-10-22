# -*- coding: utf-8 -*-
"""B-168 Gefahrenschutz mit Risikoabwaegung fuer jede gesteuerte Einheit (Daniel 22.10.2026 08:09: "alle Einheiten brauchen
einen Gefahrenschutz mit Risikoabwaegung, sonst schickt die KI ihre Einheiten in den sicheren Tod so wie die Sklaven im Moment -
sie muessen ausholen und den richtigen Pfad zum Ziel finden und auf dem Weg noch moegliche andere Dinge mitnehmen").

GEMESSEN 22.10. (2v2 liga2v2_20261022_080557, Lageprotokoll lage_20261022_080637_i5, 390 Runden bis Tick 13.775):
  - 28 von 38 Sklaven starben; laufend (Zustand 101) verloren sie unter Beschuss 172.855 Leben, die Assassinen-Raten L73
    sagten 8.506 voraus -> Faktor 20,3 (Sklaven haben keine Ruestung wie die Assassinen); ohne Schuetzen in Reichweite 0.
  - Die alte Pruefung sah nur das ZIEL an (Schuetze bis 20 Felder) - Armbrueste reichen 44 (gefecht.FERN_REICH); die Sklaven
    starben unterwegs, der Pfadsucher des Spiels nimmt den kuerzesten Weg.
  - Reiter von Spieler 2 stand von Tick 1.869 bis 13.593 auf (231,296): ein Angriffsbefehl auf einen Arbeiter 166-215 Felder
    weit bewegte ihn nicht; Reiter von Spieler 1 fand nie ein "ungefaehrliches" Ziel.

Baustein:
  Lage           - Schaden je Takt je Feld aus allen feindlichen Fernkaempfern (Baender L73, Reichweite gefecht.FERN_REICH),
                   einmal je Runde; je Startpunkt EINE Kostensuche (skimage MCP) ueber die ganze Karte: zuerst wenig Beschuss,
                   dann kurz (wie sturm.py - "Beschuss-Last zuerst"); mit Wegkarte nur im Gebiet des Startpunkts
  plan           - Weg, Takte und erwarteter Verlust (Weg + Verweilen am Ziel) fuer Einheit -> Ziel; Wegpunkte fuer die
                   Wegkette von logik.lua ("lauf" + "danach")
  bewerte        - Risikoabwaegung: P(Tod) = erwarteter Verlust / Leben; nur Ziele mit erwartetem Verlust < Leben; Rang =
                   Wert x (1 - P) / Takte. Weil jede Runde neu gerankt wird, gewinnt ein Ziel, an dem die Einheit gerade
                   vorbeikommt (kurze Takte) - so werden Dinge auf dem Weg mitgenommen
  Lerner         - lernt jede Runde selbst nach: Verlust je Typ gegen die Vorhersage (Faktor) und Takte je Feld; Datei
                   daten/verlust_raten.json; ohne eigene Messung fuer einen Typ gilt der vorsichtigste bekannte Faktor
                   (UNGEMESSEN, steht so im Ereignis)
Offline lernen aus einem Lageprotokoll: python werkzeug/gefahrenschutz.py lernen <lage.jsonl.gz> <spieler,...> <feinde,...>
"""
import json
import os
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
RATEN = os.path.join(HIER, "..", "daten", "verlust_raten.json")
SCHADEN_BAENDER = ((3, 2.10), (8, 1.37), (15, 0.56))     # L73: Schaden je Schuetze und Takt nach Abstand (an Assassinen)
SCHADEN_WEIT = 0.06                                      # L73: weiter als 15 Felder, bis zur Reichweite
GROESSE = 400
ZIEL_UMKREIS = 8                 # wie gefahr.ZIEL_UMKREIS: ist das Ziel nicht begehbar, das naechste erreichbare Feld bis so weit
LAUF = 101                       # Zustand "laeuft" (Lagebild; Sklaven unterwegs, 22.10.)
# Verweilen am Ziel (gemessen 19.10. raid_messen.py): Sklave - Holzfaellerhuette brennt nach ~165 Takten; Pferdebogen - erster
# Pfeil toetet einen Holzfaeller in <= 44 Takten
VERWEILEN = {71: 165, 74: 44}
RISIKO_MAX = 0.5                 # vertretbar: eher ueberleben als sterben (Startwert, UNGEMESSEN - Trockentest 22.10.: ohne
                                 # Grenze ging ein Sklave bei P(Tod) 0,85 auf einen Hopfenhof)
WECHSEL = 0.9                    # ein ferneres Ziel loest das jetzige erst ab, wenn das jetzige unter 90 % seines Rangs faellt
                                 # (Startwert; Trockentest 22.10.: Ziele flackerten zwischen fernen Arbeitern hin und her)
WEGPUNKT_ABSTAND = 10            # Wegpunkte hoechstens so weit auseinander - dazwischen nimmt das Spiel den kuerzesten Weg
                                 # (sturm.py 15: "teilweise laufen sie vorne rum" verschwand damit); Startwert


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def schaden_je_schuetze(d, reich):
    if d > reich:
        return 0.0
    return next((w for r, w in SCHADEN_BAENDER if d <= r), SCHADEN_WEIT)


# ---- gelernte Raten ------------------------------------------------------------------------------------------------------
def raten_laden():
    try:
        return {int(k): v for k, v in json.load(open(RATEN, encoding="utf-8")).get("typen", {}).items()}
    except (OSError, ValueError):
        return {}


def raten_schreiben(r, quelle):
    json.dump({"quelle": quelle, "erklaerung": "je Einheitentyp: verlust/vorhersage = Faktor gegen die Assassinen-Raten L73 "
               "(laufend unter Beschuss), takte/felder = Takte je Feld beim Laufen", "typen": {str(k): v for k, v in sorted(r.items())}},
              open(RATEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def faktor(raten, typ):
    """(Faktor, gemessen?) - ohne eigene Messung (Vorhersage unter 500) der groesste bekannte Faktor: lieber zu vorsichtig."""
    r = raten.get(typ)
    if r and r.get("vorhersage", 0) >= 500:
        return r["verlust"] / float(r["vorhersage"]), True
    bekannt = [v["verlust"] / float(v["vorhersage"]) for v in raten.values() if v.get("vorhersage", 0) >= 500]
    return (max(bekannt) if bekannt else 1.0), False


def takte_je_feld(raten, typ):
    """(Takte je Feld, gemessen?) - ohne eigene Messung 12 (L80, Sklave; sturm.py Streitkolben gleich gemessen)."""
    r = raten.get(typ)
    if r and r.get("felder", 0) >= 50:
        return r["takte"] / float(r["felder"]), True
    return 12.0, False


# ---- Lage einer Runde ----------------------------------------------------------------------------------------------------
class Lage:
    def __init__(self, L, G, ist_feind, fern_reich, gebiete=None, n=GROESSE, raten=None, wegkarte=None):
        """wegkarte (speicher.wegkarte(): gebiet, gebaeude, link) - 22.10. 2v2 082947: ohne Gebaeude-Ebene legte die Suche den
        ersten Wegpunkt eines Reiters auf das Lagerfeuer (224,282, link 28, Gebaeude 10) - er stand 2.600 Takte still."""
        self.n = n
        d = np.zeros((n + 1, n + 1))

        def quadrat(x, y, r, w):
            x0, x1, y0, y1 = max(0, x - r), min(n - 1, x + r), max(0, y - r), min(n - 1, y + r)
            if x0 > x1 or y0 > y1:
                return
            d[x0, y0] += w
            d[x1 + 1, y0] -= w
            d[x0, y1 + 1] -= w
            d[x1 + 1, y1 + 1] += w
        self.schuetzen = 0
        for e in L.values():
            if ist_feind(e.get("besitzer")) and e.get("typ") in fern_reich and e.get("leben", 1) > 0:
                x, y, reich = e["x"], e["y"], fern_reich[e["typ"]]
                self.schuetzen += 1
                quadrat(x, y, reich, SCHADEN_WEIT)
                vorher = SCHADEN_WEIT
                for r, w in reversed(SCHADEN_BAENDER):
                    quadrat(x, y, min(r, reich), w - vorher)       # kurze Reichweite (Schleuder 17, Feuer 11): Band endet dort
                    vorher = w
        self.s = np.maximum(d.cumsum(0).cumsum(1)[:n, :n], 0.0)    # Schaden je Takt (Assassinen-Einheiten) je Feld
        if wegkarte is not None:
            gebiete = wegkarte["gebiet"]
        self.gebiete = None if gebiete is None else np.asarray(gebiete)
        self.bau = None if wegkarte is None else np.asarray(wegkarte["gebaeude"])
        self.raten = raten_laden() if raten is None else raten
        mn = self.s[self.s > 1e-9].min() if (self.s > 1e-9).any() else SCHADEN_WEIT
        # Vorrang: jedes Feld unter Beschuss kostet mehr als jeder Umweg ohne Beschuss (2 x Kartenbreite Felder)
        self.vorrang = 2.0 * n / mn
        self._suche = {}

    def drin(self, p):
        return 0 <= p[0] < self.n and 0 <= p[1] < self.n

    def schaden(self, p):
        return float(self.s[p[0], p[1]]) if self.drin(p) else 0.0

    def gebiet_bei(self, p):
        if self.gebiete is None or not self.drin(p):
            return 0
        g = int(self.gebiete[p[0], p[1]])
        if g:
            return g
        fen = self.gebiete[max(0, p[0] - 2):p[0] + 3, max(0, p[1] - 2):p[1] + 3]
        werte, zahl = np.unique(fen[fen > 0], return_counts=True)
        return int(werte[zahl.argmax()]) if len(werte) else 0

    def suche(self, start):
        """(MCP, kumulierte Kosten) ab start - einmal je Startpunkt und Runde."""
        start = tuple(start)
        if start not in self._suche:
            from skimage.graph import MCP_Geometric as MCP     # Schraegschritt kostet Wurzel 2 - ohne Beschuss gerade statt Zickzack
            kosten = 1.0 + self.vorrang * self.s
            g = self.gebiet_bei(start)
            if self.gebiete is not None and g:
                kosten = np.where(self.gebiete == g, kosten, -1.0)
            if self.bau is not None and self.drin(start):
                # Gebaeudefelder sind gesperrt - ausser dem Gebaeude, auf dem die Einheit steht (Bergfried, Posten)
                eigen = int(self.bau[start])
                kosten = np.where((self.bau == 0) | ((self.bau == eigen) & (eigen != 0)), kosten, -1.0)
            if self.drin(start):
                kosten[start] = max(kosten[start], 1.0)
            m = MCP(kosten, fully_connected=True)
            kum, _ = m.find_costs([start])
            self._suche[start] = (m, kum)
        return self._suche[start]

    def ankunft(self, start, ziel):
        _, kum = self.suche(start)
        for r in range(ZIEL_UMKREIS + 1):
            bester = None
            for x in range(ziel[0] - r, ziel[0] + r + 1):
                for y in range(ziel[1] - r, ziel[1] + r + 1):
                    if schach((x, y), ziel) != r or not self.drin((x, y)) or not np.isfinite(kum[x, y]):
                        continue
                    if bester is None or kum[x, y] < kum[bester]:
                        bester = (x, y)
            if bester is not None:
                return bester
        return None

    def plan(self, start, ziel, typ, leben):
        """Weg start -> ziel fuer eine Einheit vom Typ typ mit leben: dict(weg, takte, verlust, p_tod, an) oder None (nicht
        erreichbar). Verlust = Faktor x (Schaden entlang des Wegs x Takte je Feld + Schaden am Ankunftsfeld x Verweilen)."""
        start, ziel = tuple(start), tuple(ziel)
        an = self.ankunft(start, ziel)
        if an is None:
            return None
        m, _ = self.suche(start)
        weg = [tuple(int(v) for v in q) for q in m.traceback(an)]
        f, _ = faktor(self.raten, typ)
        tpf, _ = takte_je_feld(self.raten, typ)
        beschuss = sum(self.s[q[0], q[1]] for q in weg[1:])
        verlust = f * (beschuss * tpf + self.s[an[0], an[1]] * VERWEILEN.get(typ, 0))
        return {"weg": weg, "takte": len(weg) * tpf, "verlust": verlust, "p_tod": min(1.0, verlust / float(max(1, leben))),
                "an": an}

    def wegpunkte(self, weg):
        """Wegpunkte fuer logik.lua: Richtungswechsel und mindestens alle WEGPUNKT_ABSTAND Felder, letzter = Ankunft."""
        if len(weg) < 2:
            return [tuple(weg[-1])] if weg else []
        pkt, letzter = [], 0
        for i in range(1, len(weg) - 1):
            if self.bau is not None and self.bau[weg[i][0], weg[i][1]] != 0:
                continue                                     # kein Wegpunkt auf einem Gebaeude (auch nicht dem eigenen)
            knick = (weg[i][0] - weg[i - 1][0], weg[i][1] - weg[i - 1][1]) != (weg[i + 1][0] - weg[i][0], weg[i + 1][1] - weg[i][1])
            if (knick and i - letzter >= 3) or i - letzter >= WEGPUNKT_ABSTAND:
                pkt.append(weg[i])
                letzter = i
        pkt.append(weg[-1])
        return pkt


def bewerte(lage, start, typ, leben, ziele):
    """ziele: [(wert, ziel_ort, kennung)]. Gibt [(rang, kennung, plan)] - nur Ziele mit P(Tod) <= RISIKO_MAX, bester zuerst.
    Rang = Wert x (1 - P(Tod)) / (Takte Weg + Verweilen)."""
    aus = []
    for wert, ort, k in ziele:
        p = lage.plan(start, ort, typ, leben)
        if p is None or p["p_tod"] > RISIKO_MAX:
            continue
        aus.append((wert * (1.0 - p["p_tod"]) / float(max(1.0, p["takte"] + VERWEILEN.get(typ, 0))), k, p))
    return sorted(aus, key=lambda z: -z[0])


def waehle(rang, alt):
    """(kennung, plan, art) aus bewerte(): art "neu" (kein altes Ziel), "bleibt", "mitnehmen" (ein besseres Ziel liegt naeher als
    das jetzige - die Einheit kommt gerade daran vorbei), "wechsel" (das jetzige ist nicht mehr vertretbar oder ein ferneres ist
    deutlich besser, WECHSEL); None ohne vertretbares Ziel."""
    if not rang:
        return None
    beste = rang[0]
    if alt is None:
        return beste[1], beste[2], "neu"
    alt_r = next((z for z in rang if z[1] == alt), None)
    if alt_r is None:
        return beste[1], beste[2], "wechsel"
    if beste[1] == alt:
        return alt, alt_r[2], "bleibt"
    if beste[2]["takte"] < alt_r[2]["takte"]:
        return beste[1], beste[2], "mitnehmen"
    if alt_r[0] >= WECHSEL * beste[0]:
        return alt, alt_r[2], "bleibt"
    return beste[1], beste[2], "wechsel"


def lauf_befehl(lage, einheit, p):
    """Angriffsbefehl fuer logik.lua: Wegkette entlang des Plans."""
    pk = lage.wegpunkte(p["weg"])
    a = {"einheiten": [einheit], "lauf": [pk[0][0], pk[0][1]], "trupp": 1}
    if len(pk) > 1:
        a["danach"] = [[q[0], q[1]] for q in pk[1:]]
    return {"angriff": a}


# ---- Lernen --------------------------------------------------------------------------------------------------------------
class Lerner:
    """Je Runde: eigene Einheiten der Typen, die in beiden Runden liefen - Lebensverlust gegen die Vorhersage (Schaden am alten
    Feld x Takte) und Felder gegen Takte. Schreibt alle SCHREIB_ALLE Runden in die Datei (Summe aus Datei + neu)."""
    SCHREIB_ALLE = 20

    def __init__(self, sp, typen):
        self.sp, self.typen = sp, set(typen)
        self.vorher = {}
        self.neu = {}
        self.runden = 0

    def runde(self, t, L, lage):
        jetzt = {n: (t, e) for n, e in L.items() if e.get("besitzer") == self.sp and e.get("typ") in self.typen and e.get("leben", 0) > 0}
        for n, (t1, e1) in jetzt.items():
            if n not in self.vorher:
                continue
            t0, e0 = self.vorher[n]
            dt = t1 - t0
            if dt <= 0 or e0.get("zustand") != LAUF or e1.get("zustand") != LAUF:
                continue
            z = self.neu.setdefault(e1["typ"], {"verlust": 0.0, "vorhersage": 0.0, "felder": 0, "takte": 0})
            v = lage.schaden((e0["x"], e0["y"])) * dt
            if v > 0:
                z["verlust"] += max(0, e0["leben"] - e1["leben"])
                z["vorhersage"] += v
            d = schach((e0["x"], e0["y"]), (e1["x"], e1["y"]))
            if d > 0:
                z["felder"] += d
                z["takte"] += dt
        self.vorher = jetzt
        self.runden += 1
        if self.runden % self.SCHREIB_ALLE == 0:
            self.schreiben()

    def schreiben(self):
        """Lesen-Addieren-Schreiben unter einer Sperrdatei: im 2v2 schreiben zwei Lenker in dieselbe Datei."""
        if not self.neu:
            return
        import time
        sperre = RATEN + ".sperre"
        for _ in range(40):
            try:
                fd = os.open(sperre, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                break
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(sperre) > 10:     # liegengeblieben (Lenker abgebrochen)
                        os.remove(sperre)
                        continue
                except OSError:
                    pass
                time.sleep(0.05)
        else:
            return                                   # diesmal nicht - die Zahlen bleiben in self.neu fuer das naechste Mal
        try:
            r = raten_laden()
            for typ, z in self.neu.items():
                a = r.setdefault(typ, {"verlust": 0.0, "vorhersage": 0.0, "felder": 0, "takte": 0})
                for k in z:
                    a[k] = round(a.get(k, 0) + z[k], 2)
            tmp = RATEN + ".neu%d" % self.sp
            json.dump({"quelle": "gefahrenschutz.Lerner, Spieler %d, zuletzt %s" % (self.sp, time.strftime("%Y-%m-%d %H:%M")),
                       "erklaerung": "je Einheitentyp: verlust/vorhersage = Faktor gegen die Assassinen-Raten L73 (laufend unter "
                       "Beschuss), takte/felder = Takte je Feld beim Laufen", "typen": {str(k): v for k, v in sorted(r.items())}},
                      open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            os.replace(tmp, RATEN)
            self.neu = {}
        finally:
            try:
                os.remove(sperre)
            except OSError:
                pass


def lernen_aus_protokoll(pfad, spieler, feinde):
    """Offline: dasselbe Lernen ueber ein Lageprotokoll (alle Runden), fuer die eigenen spieler gegen feinde."""
    import gefecht
    from lageprotokoll import runden
    lerner = {sp: Lerner(sp, (71, 74, 72, 70, 75, 26)) for sp in spieler}
    for ln in lerner.values():
        ln.SCHREIB_ALLE = 10 ** 9
    for t, st, E, G in runden(pfad):
        L = {e["nr"]: e for e in E}
        lage = Lage(L, {}, lambda b: b in feinde, gefecht.FERN_REICH, raten={})
        for ln in lerner.values():
            ln.runde(t, L, lage)
    for ln in lerner.values():
        print("Spieler %d: %s" % (ln.sp, {k: {kk: round(vv, 1) for kk, vv in v.items()} for k, v in ln.neu.items()}))
        ln.schreiben()
    print("Datei:", os.path.abspath(RATEN), raten_laden())


if __name__ == "__main__":
    sys.path.insert(0, HIER)
    if sys.argv[1:2] == ["lernen"]:
        lernen_aus_protokoll(sys.argv[2], [int(v) for v in sys.argv[3].split(",")], {int(v) for v in sys.argv[4].split(",")})
