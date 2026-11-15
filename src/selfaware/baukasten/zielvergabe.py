# -*- coding: utf-8 -*-
"""Zielvergabe fuer alle Einheiten - eine Regel fuer jedes Modul (Assassinen, Brandtrupp, Nahkampf-Raid).

Daniel 15.11.2026 22:29: "zielvergabe assassinen und nicht nur assassinen sondern aller einheiten so koennen auch assassinen
und sklaven auf einen steinbruch oder bogenschuetzen und sklaven auf einen holzfaeller etc."

Anlass (gemessen in data/research/erstes_spiel_log2_sp2.txt, Partie ab 22:22:46): bis zu 77 Assassinen ohne Ziel, Grund
"alle gefaehrlich" in 45 von 48 Meldungen - je Gebaeude durfte nur EIN Assassine hin (bei teuren zwei), die sicheren Ziele waren
damit voll, uebrig blieben nur gefaehrliche. Sklaven und Nahkaempfer nahmen je Ziel nur eine Einheit.

Die Regel: erst ein freies Ziel (verteilen - Daniel 12.10. 00:41/00:44: "EIN Assassine je Gebaeude reisst ein", moeglichst viele
Gebaeude zugleich). Ist keins annehmbar, stellt sich die Einheit zu einem schon besetzten Ziel dazu, statt zu warten. Einheiten
anderer Art sperren nie ein Ziel - jedes Modul zaehlt nur seine eigenen, Assassinen und Sklaven koennen zugleich auf demselben
Steinbruch sein.
"""


def waehle(kandidaten, frei, wahl):
    """kandidaten: Liste der Ziele, die das Modul ueberhaupt nehmen wuerde; frei(k) -> True, solange k noch Platz hat;
    wahl(liste) -> das beste Ziel daraus oder None (die Bewertung des Moduls, unveraendert).

    Gibt (Ziel, dazu): dazu=True heisst, das Ziel war schon besetzt und die Einheit stellt sich dazu."""
    kandidaten = list(kandidaten)
    erst = [k for k in kandidaten if frei(k)]
    ziel = wahl(erst) if erst else None
    if ziel is not None:
        return ziel, False
    besetzt = [k for k in kandidaten if not frei(k)]
    ziel = wahl(besetzt) if besetzt else None
    return ziel, ziel is not None


def brennt(g):
    """Daniel 15.11.2026 23:31 ("es brennt und sie verbrennen auch, das ist aber erwartbar, bitte sofort ein neues Gebaeude auswaehlen"):
    ein brennendes Gebaeude (fireDuration > 0, Spalte feuer der Gebaeudeliste; B-150 L177: faellt erst auf 0, wenn es weg ist) ist kein
    Ziel mehr - wer es angreift, nimmt sofort ein anderes. Die EINE Stelle fuer alle Module."""
    return (g.get("feuer") or 0) > 0
