# -*- coding: utf-8 -*-
"""Lord-Schutz mit Rechnung (Rang 3 der Rangliste L135; Daniel 19.10. 17:51: "du brauchst keine Verteidigung, wenn du
weisst, dass der Gegner nur 4 Einheiten hat und dein Lord full live ist. Wenn du weisst, wo alle Einheiten beim Gegner stehen,
kannst du sogar berechnen, dass es nicht reichen wird, deinen Lord zu killen").

Anlass: 4 von 10 Partien 1018e-n endeten mit dem Tod des Lords (immer Spieler 2); Daniel 17:45: "schwach wieder von Orange,
nicht zu verteidigen gegen diesen offensichtlichen Angriff".

Je Runde: alle feindlichen Truppen bis ANMARSCH_R Felder um unseren Lord (der Anmarsch) gegen den Lord und unsere Truppen bis
LORD_R Felder bei ihm - gerechnet mit gefecht.simuliere (Editor-Duelle). Stirbt unsere Seite in der Rechnung, ist der Lord in
Gefahr: ALARM - das Heer greift den naechsten Feind am Lord an, der Feldzug ruht so lange. Sonst nichts (keine Verteidigung
"auf Verdacht").
ANMARSCH_R = 60 (Startwert): ein arab. Schwertkaempfer braucht fuer 60 Felder ~1.170 Takte (L80: 19,5 je Feld) - Zeit, das
Heer heimzuholen. Pruefung ohne Spiel: werkzeug/lordwache_pruefen.py."""
import gefecht

LORD = 55
TRUPPE = {22, 23, 24, 25, 26, 27, 28, 70, 71, 72, 73, 74, 75, 76}
ANMARSCH_R = 60
LORD_R = 15


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def einheit(e, steht=False):
    return dict(typ=e["typ"], leben=e["leben"], x=e["x"], y=e["y"], steht=steht)


def bedrohung(L, sp):
    """(Gefahr, Text, Feinde im Anmarsch [nr], Lord-Nr). Gefahr = in der Rechnung faellt unsere Seite (mit dem Lord)."""
    lord = next(((n, e) for n, e in L.items() if e["besitzer"] == sp and e["typ"] == LORD and e.get("leben", 1) > 0), None)
    if lord is None:
        return False, "kein Lord", [], None
    ln, le = lord
    lp = (le["x"], le["y"])
    feinde = [n for n, e in L.items() if e.get("besitzer") not in (0, sp) and e["typ"] in TRUPPE and e.get("leben", 1) > 0
              and schach((e["x"], e["y"]), lp) <= ANMARSCH_R]
    if not feinde:
        return False, "kein Feind bis %d Felder" % ANMARSCH_R, [], ln
    wir = [einheit(le, steht=True)] + [einheit(e, steht=True) for n, e in L.items() if e["besitzer"] == sp
                                       and e["typ"] in TRUPPE and e.get("leben", 1) > 0 and schach((e["x"], e["y"]), lp) <= LORD_R]
    sie = [einheit(L[n]) for n in feinde]
    r_wir, r_sie, t, sieg = gefecht.simuliere(wir, sie)
    gefahr = r_wir <= 0
    text = "%d Feinde bis %d Felder (%d Leben) gegen Lord + %d eigene (%d Leben): %s nach %d Takten" % (
        len(sie), ANMARSCH_R, sum(e["leben"] for e in sie), len(wir) - 1, sum(e["leben"] for e in wir),
        "LORD FAELLT" if gefahr else ("Feinde fallen" if sieg else "offen"), t)
    return gefahr, text, sorted(feinde, key=lambda n: schach((L[n]["x"], L[n]["y"]), lp)), ln
