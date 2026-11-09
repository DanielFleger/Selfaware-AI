"""Formationen: Wer steht wo. Reine Rechnung, von jedem Einsatz nutzbar (B-176).

Heute nutzt sie der Vorstoss. Breit aufgestellt wurden im Gefecht 4,5 % der Pfeile zu Treffern, dicht 38 bis 61 %
(data/research/auge_plan/zickzack_20261108/Ergebnis_Zickzack.md).
"""


def querachse(von, ziel):
    """Die Achse quer zum Weg: Nach ihr werden die Einheiten auf die Plaetze verteilt, damit keine quer durch die Gruppe laeuft."""
    return "y" if abs(ziel[0] - von[0]) >= abs(ziel[1] - von[1]) else "x"


def breit(von, ziel, n, luecke, spalten):
    """Ein Feld je Platz 0 bis n-1 um das Ziel: nebeneinander quer zum Weg, hintereinander in Reihen, mit luecke Feldern Abstand."""
    dx, dy = ziel[0] - von[0], ziel[1] - von[1]
    x_haupt = abs(dx) >= abs(dy)
    vor = (1 if dx >= 0 else -1) if x_haupt else (1 if dy >= 0 else -1)
    reihen = (n + spalten - 1) // spalten
    nebeneinander = (n + reihen - 1) // reihen
    felder = []
    for p in range(n):
        q = (2 * (p // reihen) - (nebeneinander - 1)) * luecke // 2
        h = -(p % reihen) * luecke * vor
        felder.append((ziel[0] + h, ziel[1] + q) if x_haupt else (ziel[0] + q, ziel[1] + h))
    return felder
