# -*- coding: utf-8 -*-
"""Brotkette im Lenker bauen, wie die Nahrungswahl sie geplant hat (SAI 11.10. 23:20; nahrungswahl.py, Daniel 22:53/23:05).

Ab plan["brot"]["ab_tick"] je Runde hoechstens EIN Bau, in dieser Reihenfolge: Getreidefarm(en) auf dem geplanten Platz,
Muehle(n) am Lager (Weizen und Mehl liegen im Lager), Baeckereien zwischen Lager und Kornspeicher (Mehl holen, Brot
bringen). Gezaehlt wird, was im Spiel steht (eigene Gebaeude), dazu offene Auftraege der letzten SPERRE Ticks - so wird
nichts doppelt bestellt. Gebaut wird nur mit genug Holz und Gold laut Preisen im laufenden Spiel.
Ein volles Lager haelt die Kette an - dafuer sorgt der Stillstand-Waechter (stillstand.py)."""

SPERRE = 300
TYPEN = (30, 34, 17)          # Getreidefarm, Muehle, Baeckerei
NAME = {30: "Getreidefarm", 34: "Muehle", 17: "Baeckerei"}


class BrotBau:
    def __init__(self, brot, sp, lager, kornspeicher, baue, kosten):
        self.brot, self.sp, self.lager, self.ks = brot, sp, tuple(lager), tuple(kornspeicher)
        self.baue, self.kosten = baue, kosten
        self.offen = {}               # typ -> Tick des letzten Auftrags
        self.fertig = False

    def ziel(self):
        n = len(self.brot["getreide"])
        return {30: n, 34: n, 17: self.brot["baeckereien"]}

    def bedarf(self, t, G):
        """Holz/Gold fuer den naechsten fehlenden Bau - die Wirtschaft haelt es frei (Ruecklage). Lauf 23:16 auf Two Montains:
        ohne Ruecklage wartete die Muehle von Tick 2.027 bis 6.049 auf Holz, die Kette stand erst bei 9.604."""
        if not self.brot or self.fertig or t < self.brot.get("ab_tick", 0):
            return {}
        steht = {typ: sum(1 for g in G.values() if g["besitzer"] == self.sp and g["typ"] == typ) for typ in TYPEN}
        ziel = self.ziel()
        for typ in TYPEN:
            if steht[typ] < ziel[typ]:
                k = self.kosten(typ)
                return {"holz": k.get("holz", 0), "gold": k.get("gold", 0)}
        return {}

    def schritt(self, t, st, G):
        if not self.brot or self.fertig or t < self.brot.get("ab_tick", 0):
            return []
        steht = {typ: sum(1 for g in G.values() if g["besitzer"] == self.sp and g["typ"] == typ) for typ in TYPEN}
        ziel = self.ziel()
        if all(steht[typ] >= ziel[typ] for typ in TYPEN):
            self.fertig = True
            return ["BROTKETTE steht bei Tick %d: %d Getreidefarm(en), %d Muehle(n), %d Baeckerei(en)" % (
                t, steht[30], steht[34], steht[17])]
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
            else:
                mitte = ((self.lager[0] + self.ks[0]) // 2, (self.lager[1] + self.ks[1]) // 2)
                ort = self.baue(17, mitte[0], mitte[1], 12)
            self.offen[typ] = t
            return ["BROTKETTE %s bestellt bei %s (Tick %d, steht %d von %d)" % (NAME[typ], ort, t, steht[typ], ziel[typ])]
        return []
