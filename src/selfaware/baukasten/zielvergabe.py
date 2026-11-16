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


def waehle(kandidaten, frei, wahl, wert=None, vorzug=0.0):
    """kandidaten: Liste der Ziele, die das Modul ueberhaupt nehmen wuerde; frei(k) -> True, solange k noch Platz hat;
    wahl(liste) -> das beste Ziel daraus oder None (die Bewertung des Moduls, unveraendert).
    vorzug (Regler "Gemeinsam gewirkt", baukasten/regler.dazu_vorzug): so viel mehr zaehlt ein schon besetztes Ziel gegen das beste freie;
    wert(ziel) -> die Zahl, nach der wahl entscheidet. Ohne vorzug wie vorher: ein freies zuerst, ein besetztes nur, wenn kein freies taugt.

    Gibt (Ziel, dazu): dazu=True heisst, das Ziel war schon besetzt und die Einheit stellt sich dazu."""
    kandidaten = list(kandidaten)
    erst = [k for k in kandidaten if frei(k)]
    ziel = wahl(erst) if erst else None
    if ziel is not None and (vorzug <= 0 or wert is None):
        return ziel, False
    besetzt = [k for k in kandidaten if not frei(k)]
    dazu = wahl(besetzt) if besetzt else None
    if ziel is None:
        return dazu, dazu is not None
    if dazu is not None and wert(dazu) > 0 and wert(dazu) * (1.0 + vorzug) > wert(ziel):
        return dazu, True
    return ziel, False


def brennt(g):
    """Daniel 15.11.2026 23:31 ("es brennt und sie verbrennen auch, das ist aber erwartbar, bitte sofort ein neues Gebaeude auswaehlen"):
    ein brennendes Gebaeude (fireDuration > 0, Spalte feuer der Gebaeudeliste; B-150 L177: faellt erst auf 0, wenn es weg ist) ist kein
    Ziel mehr - wer es angreift, nimmt sofort ein anderes. Die EINE Stelle fuer alle Module."""
    return (g.get("feuer") or 0) > 0


def kennung(g):
    """Wer ein Gebaeude ist: (Art, Besitzer, uid). Das Spiel vergibt die Nummer eines zerstoerten Gebaeudes an das naechste neue (Probe 9b:
    Holzfaellerhuette 75 fiel, unter Nummer 75 stand danach ein Lagerplatz, zwei Assassinen schlugen drei Runden auf ihn ein; Probe 10:
    Holzfaellerhuette 83 -> Jaegerhuette 83). Die uid vergibt das Spiel je Gebaeude nur einmal (Daniel 16.11.2026 20:57 "es hoert sich nach
    einem falschen gebaeudenummern mapping an?")."""
    return (g.get("typ"), g.get("besitzer"), g.get("uid"))
