# -*- coding: utf-8 -*-
"""Fallenwache (Daniel 19.10. 11:00: "du bist eine KI - wenn du siehst, dass etwas ein Angriffsziel bekommt, eine Holzfalle
da hin"): laeuft eine feindliche Einheit auf einen Punkt zu, der hoechstens NAH Felder neben einem unserer Gebaeude liegt,
und ist sie noch mindestens ABSTAND_MIN Felder davon weg, kommt GENAU auf diesen Punkt eine Fallgrube (Typ 67, 4 Holz) -
sie laeuft hinein (18.000 Schaden, Wissensregister L125).

Gemessen 19.10. (Lageprotokoll 1018h): die Lagebild-Spalten laufx/laufy sind der Punkt, auf den die Einheit gerade zulaeuft
(bei unseren Assassinen der naechste Wegpunkt); zielgebaeude ist NICHT das angegriffene Gebaeude (laufende Assassinen: der
eigene Kornspeicher; Assassinen im Gebaeudeangriff, Zustand 107: 0) - darum entscheidet hier das Laufziel.
Pruefung ohne Spiel: src/selfaware/tools/checks/fallenwache_pruefen.py."""

NAH = 2                 # Laufziel hoechstens so weit neben einem eigenen Gebaeude
ABSTAND_MIN = 4         # die Einheit muss noch so weit weg sein (sonst steht sie gleich drauf - dort baut das Spiel nicht)
JE_RUNDE = 2
HOLZ = 4                # kosten(67) im laufenden Spiel (Ascension)
HOLZ_RESERVE = 5        # ein Kornspeicher-Nachbau geht vor
WIEDER_TICKS = 2000     # dasselbe Feld fruehestens so spaet erneut versuchen
# Daniel 19.10. 11:38: "du brauchst nur die minimale Anzahl, weil jede meist einen Soldaten toetet, und am wichtigsten sind
# Assassinen - Sklaven z. B. koennen mit Bogenschuetzen besiegt werden": nur Assassinen, hoechstens EINE Falle je Assassine
FEIND_TYPEN = {73}
GROESSE = {}            # Gebaeudetyp -> Kantenlaenge (vom Lenker aus bauen.NACH_TYP gesetzt)


def abstand_zu_gebaeude(p, g):
    b = GROESSE.get(g["typ"], 1)
    dx = max(g["x"] - p[0], 0, p[0] - (g["x"] + b - 1))
    dy = max(g["y"] - p[1], 0, p[1] - (g["y"] + b - 1))
    return max(dx, dy)


def kandidaten(L, G, sp):
    """[(Laufziel, Einheit)] fuer feindliche Truppen, deren Laufziel neben einem eigenen Gebaeude liegt."""
    eigen = [g for g in G.values() if g["besitzer"] == sp and g["typ"] != 67]
    aus, gesehen = [], set()
    for nr, e in sorted(L.items()):
        if e.get("besitzer") in (0, sp) or e.get("typ") not in FEIND_TYPEN or e.get("leben", 1) <= 0:
            continue
        ziel = (e.get("laufx", 0), e.get("laufy", 0))
        if ziel == (0, 0) or ziel in gesehen:
            continue
        if max(abs(ziel[0] - e["x"]), abs(ziel[1] - e["y"])) < ABSTAND_MIN:
            continue
        if not eigen or min(abstand_zu_gebaeude(ziel, g) for g in eigen) > NAH:
            continue
        if any(abstand_zu_gebaeude(ziel, g) == 0 for g in eigen):
            continue                                     # Laufziel auf einem Gebaeude (Feld/Hof) - dort geht keine Grube
        gesehen.add(ziel)
        aus.append((ziel, nr))
    return aus


class Fallenwache:
    def __init__(self, sp, setze_grube):
        self.sp, self.setze_grube = sp, setze_grube
        self.versucht = {}          # Feld -> Tick
        self.bedient = set()        # Einheiten, fuer die schon eine Falle steht (eine je Assassine)
        self.gesetzt = 0

    def schritt(self, t, L, G, holz):
        ev, rest = [], holz
        gruben = {(g["x"], g["y"]) for g in G.values() if g["besitzer"] == self.sp and g["typ"] == 67}
        for ziel, nr in kandidaten(L, G, self.sp):
            if sum(1 for e in ev if e.startswith("FALLE gesetzt")) >= JE_RUNDE or rest < HOLZ + HOLZ_RESERVE:
                break
            if nr in self.bedient or ziel in gruben or t - self.versucht.get(ziel, -10 ** 9) < WIEDER_TICKS:
                continue
            self.versucht[ziel] = t
            e = L[nr]
            if self.setze_grube(ziel[0], ziel[1]):
                self.bedient.add(nr)
                rest -= HOLZ
                self.gesetzt += 1
                ev.append("FALLE gesetzt auf %s - Laufziel von Einheit %d (Typ %d, Spieler %d, noch %d Felder weg)" % (
                    ziel, nr, e["typ"], e["besitzer"], max(abs(ziel[0] - e["x"]), abs(ziel[1] - e["y"]))))
        return ev
