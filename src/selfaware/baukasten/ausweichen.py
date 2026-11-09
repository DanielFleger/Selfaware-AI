"""Ausweichen: ein Werkzeug fuer jeden Einsatz, kein Dauerzustand (B-178, docs/plans/Plan_Baukasten.md).

Daniel 09.11.2026: "Nur in Schussweite wenn auf sie geschossen wird, aber er soll dennoch nicht ausweichen vergessen."
Gemessen (data/research/auge_plan/zickzack_20261108/Ergebnis_Zickzack.md): Der Lauf im Zickzack senkt die Treffer, kostet aber je Einheit
und Feld einen Befehl, und nur 8 je Feld kommen rechtzeitig an. Wo niemand schiessen kann, bringt er nichts.

Eine Einheit weicht aus, solange ein feindlicher Schuetze oder Turm sie erreichen kann oder sie gerade Leben verliert, und noch
NACHLAUF Runden danach. Gesehen wird nur, was ein Spieler auch sieht: Feinde auf der Karte und das Leben der eigenen Einheiten.
"""

SCHUSSWEITE = 26  # L81: Schuetzen entdecken bis 20 Felder; dazu 6 Felder, die eine Einheit in einer Runde des Lenkers laeuft
NACHLAUF = 2  # Runden, rund 130 Takte: die Schussfolge eines Bogens (129 Takte); so lange kann der naechste Pfeil noch kommen
FERN = {
    22,
    23,
    70,
    72,
    74,
    76,
}  # Bogen, Armbrust, arabischer Bogen, Schleuder, Berittener Bogen, Feuerwerfer
TUERME = {
    74,
    75,
    76,
    77,
    78,
}  # Gebaeudetypen: Wach-, Verteidigungs-, Geschuetz-, eckiger und runder Turm


def _schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


class Schussfeld:
    """Merkt sich je Runde, wo Feinde schiessen koennen, und je Einheit, wann sie zuletzt in Gefahr war."""

    def __init__(self, sp):
        self.sp = sp
        self.runde = 0
        self.orte = []
        self.leben = {}
        self.gefahr_bis = {}

    def neue_runde(self, L, G):
        self.runde += 1
        self.orte = [
            (e["x"], e["y"])
            for e in L.values()
            if e.get("besitzer") not in (0, self.sp) and e["typ"] in FERN and e.get("leben", 1) > 0
        ]
        self.orte += [
            (g["x"], g["y"])
            for g in G.values()
            if g.get("besitzer") not in (0, self.sp) and g["typ"] in TUERME
        ]

    def unter_feuer(self, nr, e):
        """Soll die eigene Einheit nr mit dem Lagebild e jetzt ausweichen?"""
        ort, leben = (e["x"], e["y"]), e.get("leben", 0)
        alt = self.leben.get(nr)
        self.leben[nr] = leben
        getroffen = alt is not None and leben < alt
        if getroffen or any(_schach(ort, p) <= SCHUSSWEITE for p in self.orte):
            self.gefahr_bis[nr] = self.runde + NACHLAUF
        return self.gefahr_bis.get(nr, -1) >= self.runde
