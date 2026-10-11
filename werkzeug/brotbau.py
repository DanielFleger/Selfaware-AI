# -*- coding: utf-8 -*-
"""Brotkette im Lenker bauen, wie die Nahrungswahl sie geplant hat (SAI 11.10. 23:20; nahrungswahl.py, Daniel 22:53/23:05).

Ab plan["brot"]["ab_tick"] je Runde hoechstens EIN Bau, in dieser Reihenfolge: Getreidefarm(en) auf dem geplanten Platz,
Muehle(n) am Lager (Weizen und Mehl liegen im Lager), Baeckereien zwischen Lager und Kornspeicher (Mehl holen, Brot
bringen). Gezaehlt wird, was im Spiel steht (eigene Gebaeude), dazu offene Auftraege der letzten SPERRE Ticks - so wird
nichts doppelt bestellt. Gebaut wird nur mit genug Holz und Gold laut Preisen im laufenden Spiel.
Ein volles Lager haelt die Kette an - dafuer sorgt der Stillstand-Waechter (stillstand.py)."""

SPERRE = 300
TYPEN = (30, 34, 19, 17)      # Getreidefarm, Muehle, Kornspeicher an den Baeckereien (falls geplant), Baeckerei
NAME = {30: "Getreidefarm", 34: "Muehle", 19: "Kornspeicher (Baeckereien)", 17: "Baeckerei"}


class BrotBau:
    def __init__(self, brot, sp, lager, kornspeicher, baue, kosten):
        self.brot, self.sp, self.lager, self.ks = brot, sp, tuple(lager), tuple(kornspeicher)
        self.baue, self.kosten = baue, kosten
        self.offen = {}               # typ -> Tick des letzten Auftrags
        self.fertig = False

    def ziel(self):
        n = len(self.brot["getreide"])
        return {30: n, 34: n, 19: 1 if self.brot.get("kornspeicher2") else 0, 17: self.brot["baeckereien"]}

    def _steht(self, G):
        """Gebaeude der Kette; Kornspeicher zaehlt nur einer am Lager (der Apfel-Kornspeicher liegt woanders)."""
        eigen = [g for g in G.values() if g["besitzer"] == self.sp]
        s = {typ: sum(1 for g in eigen if g["typ"] == typ) for typ in (30, 34, 17)}
        s[19] = sum(1 for g in eigen if g["typ"] == 19 and max(abs(g["x"] - self.lager[0]), abs(g["y"] - self.lager[1])) <= 12)
        return s

    def bedarf(self, t, G):
        """Holz/Gold fuer den naechsten fehlenden Bau - die Wirtschaft haelt es frei (Ruecklage). Lauf 23:16 auf Two Montains:
        ohne Ruecklage wartete die Muehle von Tick 2.027 bis 6.049 auf Holz, die Kette stand erst bei 9.604."""
        if not self.brot or self.fertig or t < self.brot.get("ab_tick", 0):
            return {}
        steht = self._steht(G)
        ziel = self.ziel()
        for typ in TYPEN:
            if steht[typ] < ziel[typ]:
                k = self.kosten(typ)
                return {"holz": k.get("holz", 0), "gold": k.get("gold", 0)}
        return {}

    def schritt(self, t, st, G):
        if not self.brot or self.fertig or t < self.brot.get("ab_tick", 0):
            return []
        steht = self._steht(G)
        ziel = self.ziel()
        if all(steht[typ] >= ziel[typ] for typ in TYPEN):
            self.fertig = True
            return ["BROTKETTE steht bei Tick %d: %d Getreidefarm(en), %d Muehle(n), %d Baeckerei(en), Kornspeicher am Lager %d" % (
                t, steht[30], steht[34], steht[17], steht[19])]
        for typ in TYPEN:
            if steht[typ] >= ziel[typ]:
                continue
            if t - self.offen.get(typ, -10 ** 9) < SPERRE:
                return []
            k = self.kosten(typ)
            fehlt = [w for w in ("holz", "stein", "eisen", "pech", "gold") if k.get(w, 0) > st.get(w, 0)]
            if fehlt:
                return ["BROTKETTE wartet auf %s fuer %s (Tick %d)" % ("/".join(fehlt), NAME[typ], t)] if t % 1000 < 60 else []
            if typ == 30:
                x, y = self.brot["getreide"][min(steht[30], len(self.brot["getreide"]) - 1)]
                ort = self.baue(30, x, y, 4)
            elif typ == 34:
                ort = self.baue(34, self.lager[0], self.lager[1], 10)
            elif typ == 19 or self.brot.get("kornspeicher2"):
                # Daniel 23:20: Kornspeicher an die Baeckereien - beide ans Lager (Mehl holen, Brot abgeben, kurze Wege)
                ort = self.baue(typ, self.lager[0], self.lager[1], 12)
            else:
                mitte = ((self.lager[0] + self.ks[0]) // 2, (self.lager[1] + self.ks[1]) // 2)
                ort = self.baue(17, mitte[0], mitte[1], 12)
            self.offen[typ] = t
            return ["BROTKETTE %s bestellt bei %s (Tick %d, steht %d von %d)" % (NAME[typ], ort, t, steht[typ], ziel[typ])]
        return []


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


class JagdBau:
    """Jaeger an den Herden, wie die Nahrungswahl sie geplant hat (SAI 11.10. 23:32, Daniel 23:20 "warum nicht hybrid, z.B.
    Rehe"). Je geplanter Herde die Jaegerhuetten; sie liefern zum gemeinsamen Kornspeicher (L62: ein zweiter geht nur
    angrenzend an den ersten). Gebaut wird an der LEBENDEN Herde: die dichteste
    Rehgruppe im Umkreis 25 um die geplante Mitte (das Wild wandert), sonst an der geplanten Mitte. Je Runde hoechstens
    ein Bau, kein zweiter Auftrag derselben Art binnen SPERRE Ticks."""
    UMKREIS_HERDE, NAH_SPEICHER, NAH_JAEGER = 25, 12, 20

    def __init__(self, jaeger, sp, baue, kosten):
        self.jaeger, self.sp, self.baue, self.kosten = jaeger or [], sp, baue, kosten
        self.offen = {}
        self.fertig = not self.jaeger

    def _mitte(self, plan_mitte, L):
        rehe = [(e["x"], e["y"]) for e in L.values() if e.get("typ") == 44 and e.get("besitzer") == 0
                and schach((e["x"], e["y"]), plan_mitte) <= self.UMKREIS_HERDE]
        return max(rehe, key=lambda p: sum(1 for q in rehe if schach(p, q) <= 15)) if rehe else tuple(plan_mitte)

    def _naechster(self, G, L):
        """(Herde-Nr, Typ, Mitte) des naechsten fehlenden Baus oder None."""
        eigen = [(g["typ"], (g["x"], g["y"])) for g in G.values() if g["besitzer"] == self.sp and g["typ"] in (7, 19)]
        for i, j in enumerate(self.jaeger):
            m = self._mitte(tuple(j["herde"]), L)
            # L62 (23:31): weitere Kornspeicher nur angrenzend - Jaeger liefern zum gemeinsamen Kornspeicher, keiner an der Herde
            if sum(1 for t, o in eigen if t == 7 and schach(o, m) <= self.NAH_JAEGER) < j["anzahl"]:
                return i, 7, m
        return None

    def bedarf(self, t, G, L):
        if self.fertig:
            return {}
        n = self._naechster(G, L)
        if not n:
            return {}
        k = self.kosten(n[1])
        return {"holz": k.get("holz", 0), "gold": k.get("gold", 0)}

    def schritt(self, t, st, L, G):
        if self.fertig:
            return []
        n = self._naechster(G, L)
        if not n:
            self.fertig = True
            return ["JAGD steht bei Tick %d: %s" % (t, [(j["herde"], j["anzahl"]) for j in self.jaeger])]
        i, typ, m = n
        if t - self.offen.get((i, typ), -10 ** 9) < SPERRE:
            return []
        k = self.kosten(typ)
        fehlt = [w for w in ("holz", "stein", "eisen", "pech", "gold") if k.get(w, 0) > st.get(w, 0)]
        if fehlt:
            return []
        ort = self.baue(typ, m[0], m[1], 12 if typ == 7 else 8)
        self.offen[(i, typ)] = t
        return ["JAGD %s an Herde %d (%s) bestellt bei %s (Tick %d)" % ("Kornspeicher" if typ == 19 else "Jaegerhuette", i, m, ort, t)]
