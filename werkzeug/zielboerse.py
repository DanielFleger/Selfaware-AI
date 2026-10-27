# -*- coding: utf-8 -*-
"""Zielboerse (B-277, Meta 1 Feldherr, erster Teil; Daniel 27.10. 23:00 "nicht schnell erkannt, wenn neue Gebaeude gebaut
wurden, und die Verteilung war nicht optimal"; Plan_Haende_Zielboerse.md, nach Frage-Agent rot ueberarbeitet, Daniel 23:16 "ja").

runde(G, ist_feind): Feindgebaeude mit der Vorrunde vergleichen (uid, sonst Nummer+Typ+Ort) - NEU = in dieser Runde neu
aufgetaucht. Die erste Runde meldet nichts (alles waere "neu"). Gebaeude sieht jeder Spieler (FAIRNESS.md: sichtbar).
Module lesen NEU in derselben Runde: Assassinen pruefen bei einem Neubau auch Jaeger neu (assassinen.py), Reiter verteilen
sich auf verschiedene Ziele (raids.Reiterjagd).
Rueckweg: AN = False -> keine Meldung, NEU bleibt leer."""

AN = True
NEU = []                 # [(nr, typ, x, y)] dieser Runde
MELDUNGEN = []           # Zeilen dieser Runde fuer die Mitschrift
_VOR = [None]            # Schluessel der Vorrunde (None = noch keine Runde)


def reset():
    NEU[:] = []
    MELDUNGEN[:] = []
    _VOR[0] = None


def _schluessel(nr, g):
    u = g.get("uid")
    return ("uid", u) if u else ("ort", nr, g.get("typ"), g.get("x"), g.get("y"))


def runde(G, ist_feind):
    """Je Lenker-Runde einmal, vor den Modulen. Gibt NEU zurueck. Wirft nie."""
    NEU[:] = []
    MELDUNGEN[:] = []
    if not AN:
        return NEU
    try:
        jetzt = {}
        for nr, g in (G or {}).items():
            if ist_feind(g.get("besitzer")):
                jetzt[_schluessel(nr, g)] = (nr, g.get("typ"), g.get("x"), g.get("y"))
        if _VOR[0] is not None:
            NEU.extend(v for k, v in sorted(jetzt.items(), key=lambda kv: kv[1][0]) if k not in _VOR[0])
        _VOR[0] = set(jetzt)
        if NEU:
            MELDUNGEN.append("NEUBAU beim Feind: %s - Jaeger und Freie pruefen in dieser Runde neu" % ", ".join(
                "Gebaeude %d (Typ %d) bei (%d, %d)" % v for v in NEU[:8]) + (" (+%d)" % (len(NEU) - 8) if len(NEU) > 8 else ""))
    except Exception as ex:
        MELDUNGEN.append("ZIELBOERSE FEHLER %r" % (ex,))
    return NEU
