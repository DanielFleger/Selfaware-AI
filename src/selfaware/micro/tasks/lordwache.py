# -*- coding: utf-8 -*-
"""Lord-Schutz mit Rechnung (Rang 3 der Rangliste L135; Daniel 19.10. 17:51: "du brauchst keine Verteidigung, wenn du
weisst, dass der Gegner nur 4 Einheiten hat und dein Lord full live ist. Wenn du weisst, wo alle Einheiten beim Gegner stehen,
kannst du sogar berechnen, dass es nicht reichen wird, deinen Lord zu killen").

Anlass: 4 von 10 Partien 1018e-n endeten mit dem Tod des Lords (immer Spieler 2); Daniel 17:45: "schwach wieder von Orange,
nicht zu verteidigen gegen diesen offensichtlichen Angriff".

Je Runde: feindliche Truppen, die auf den Lord zukommen, gegen den Lord und unsere Truppen bis LORD_R Felder bei ihm -
gerechnet mit gefecht.simuliere. Faellt in der Rechnung der LORD, ist er in Gefahr. Dann (abwehr) die KLEINSTE Gruppe, mit
der er die Rechnung ueberlebt - zuerst die Heimwache, dann die naechsten (zuweisung.kleinste_gruppe), nicht das ganze Heer.

19.10. 18:20 NEU nach 1018o (Lordwache 195-mal ausgeloest, schon bei 2 Assassinen; das ganze Heer jagte die naechste
Assassine - Daniel 18:07, Bild "40 Schwertkaempfer, die nur einen Assassinen abwehren wollen"):
  - der Lord fehlte in den Editor-Duellen (Ersatz 20 je Takt) - jetzt gemessen aus 271 Partien (lord_messen.py): Lord an
    Assassine 150 je Takt (175 Proben), Assassine an Lord 100 (50 Proben);
  - Gefahr = der LORD stirbt in der Rechnung (vorher: unsere ganze Seite);
  - es zaehlen nur Feinde im Anmarsch: hoechstens NAH_R Felder vom Lord ODER Laufziel hoechstens ZIEL_R Felder vom Lord
    (vorher jeder Feind bis 60 Felder, auch Raider in der Wirtschaft);
  - Abwehr mit der kleinsten Gruppe, die reicht.
ANMARSCH_R = 60: ein arab. Schwertkaempfer braucht fuer 60 Felder ~1.170 Takte (L80: 19,5 je Feld). Pruefung ohne Spiel:
src/selfaware/tools/checks/lordwache_pruefen.py."""
import selfaware.services.gefecht as gefecht
import selfaware.micro.zuweisung as zuweisung

LORD = 55
TRUPPE = {22, 23, 24, 25, 26, 27, 28, 70, 71, 72, 73, 74, 75, 76}
ANMARSCH_R = 60
NAH_R = 25
ZIEL_R = 30
LORD_R = 15


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def einheit(e, steht=False, nr=None):
    return dict(typ=e["typ"], leben=e["leben"], x=e["x"], y=e["y"], steht=steht, nr=nr)


def lord_von(L, sp):
    return next(((n, e) for n, e in L.items() if e["besitzer"] == sp and e["typ"] == LORD and e.get("leben", 1) > 0), None)


def im_anmarsch(e, lp):
    d = schach((e["x"], e["y"]), lp)
    if d > ANMARSCH_R:
        return False
    z = (e.get("laufx", 0), e.get("laufy", 0))
    return d <= NAH_R or (z[0] > 0 and schach(z, lp) <= ZIEL_R)


def bedrohung(L, sp):
    """(Gefahr, Text, Feinde im Anmarsch [nr] nach Abstand, Lord-Nr). Gefahr = in der Rechnung faellt der Lord."""
    lord = lord_von(L, sp)
    if lord is None:
        return False, "kein Lord", [], None
    ln, le = lord
    lp = (le["x"], le["y"])
    feinde = [n for n, e in L.items() if e.get("besitzer") not in (0, sp) and e["typ"] in TRUPPE and e.get("leben", 1) > 0
              and im_anmarsch(e, lp)]
    if not feinde:
        return False, "kein Feind im Anmarsch", [], ln
    wir = [einheit(le, steht=True)] + [einheit(e, steht=True) for n, e in L.items() if e["besitzer"] == sp
                                       and e["typ"] in TRUPPE and e.get("leben", 1) > 0 and schach((e["x"], e["y"]), lp) <= LORD_R]
    sie = [einheit(L[n]) for n in feinde]
    rest = []
    r_wir, r_sie, t, sieg = gefecht.simuliere(wir, sie, rest_aus=rest)
    gefahr = rest[0] <= 0
    ug = zuweisung.ungemessen(wir, sie)
    text = "%d Feinde im Anmarsch (%d Leben) gegen Lord + %d eigene (%d Leben): %s nach %d Takten%s" % (
        len(sie), sum(e["leben"] for e in sie), len(wir) - 1, sum(e["leben"] for e in wir),
        "LORD FAELLT" if gefahr else ("Feinde fallen" if sieg else "Lord lebt"), t,
        (" - UNGEMESSEN %s" % sorted(ug)) if ug else "")
    return gefahr, text, sorted(feinde, key=lambda n: schach((L[n]["x"], L[n]["y"]), lp)), ln


def abwehr(L, sp, feinde, kandidaten, vorrang=()):
    """Kleinste Gruppe aus kandidaten [nr], mit der der Lord die Rechnung ueberlebt. (gewaehlt [nr], reicht, Text)."""
    lord = lord_von(L, sp)
    if lord is None or not feinde:
        return [], True, "nichts zu tun"
    ln, le = lord
    lp = (le["x"], le["y"])
    fest = [einheit(le, steht=True, nr=ln)] + [einheit(e, steht=True, nr=n) for n, e in L.items() if e["besitzer"] == sp
                                                and e["typ"] in TRUPPE and n not in kandidaten and e.get("leben", 1) > 0
                                                and schach((e["x"], e["y"]), lp) <= LORD_R]
    kand = [einheit(L[n], nr=n) for n in kandidaten if n in L and L[n]["besitzer"] == sp and L[n]["typ"] != LORD]
    sie = [einheit(L[n], nr=n) for n in feinde if n in L]
    # sie kommen zum Lord - einholen muss sie niemand (ziel_steht)
    return zuweisung.kleinste_gruppe(kand, sie, fest=fest, ziel_steht=True, vorrang=set(vorrang))


# 19.10. 19:02 FEUER (1018q/r/s gemessen: Feuer neben dem Lord kostete ihn 20.750-51.000 Leben; Gegenprobe 1018s: ohne Brand bis
# 6 Felder 0 von 290 Proben mit Verlust, mit Brand 5 von 11): verliert der Lord Leben ohne Angreifer und brennt ein Gebaeude bis
# BRAND_R Felder, geht er FLUCHT_FELDER weg - in die Richtung (8 Richtungen), die am weitesten von jedem Brand ist und auf
# keinem Gebaeudefeld endet; ist BRAND_FREI_RUNDEN Runden kein Brand mehr bis BRAND_R um seinen alten Platz, geht er zurueck.
# Daniels Regel "der Lord weicht nicht vor einem Heer" (12.10.) bleibt unberuehrt - das hier ist nur Feuer.
BRAND_R = 6
FLUCHT_FELDER = 8
BRAND_FREI_RUNDEN = 10


def fluchtpunkt(lord, braende, belegt=()):
    """lord (x, y); braende [(x, y)] brennender Gebaeude; belegt: Felder mit Gebaeuden. Gibt den Punkt FLUCHT_FELDER weit
    (8 Richtungen), dessen naechster Brand am weitesten weg ist; None ohne Brand."""
    if not braende:
        return None
    belegt = set(belegt)
    beste = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            p = (lord[0] + dx * FLUCHT_FELDER, lord[1] + dy * FLUCHT_FELDER)
            if p in belegt or p[0] < 1 or p[1] < 1:
                continue
            d = min(schach(p, b) for b in braende)
            if beste is None or d > beste[0]:
                beste = (d, p)
    return beste[1] if beste else None
