# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer die Funde der Gegenpruefung vom 17./18.10.2026 (je Fund zwei Skeptiker, Stimmen echt).
Vorher festgelegt:
  1. Lagebild wie im Spiel (waechter.lies_lagebild, OHNE eigenes "nr"-Feld): Armbrust bei (200,200), Assassine 100 acht Felder
     davor, Assassine 101 weit weg und als letzte - Beschuss an 100 > 0 (vorher 0, weil alle eigenen Nummer 0 hatten)
  2. lies_lagebild liefert "nr" und "gruppe"
  3. Bereitstellung: ein Wartender am Platz, neben dem Platz tauchen 4 Armbrustschuetzen auf -> er bekommt einen neuen Platz
     oder verlaesst die Gruppe (vorher: bleibt stehen)
  4. Angriff laeuft, der Lord verschwindet (tot) -> Phase None, kein Befehl auf die tote Nummer
  5. Angriff mit leerer Gruppe -> Phase None (vorher: haengt fuer immer)
  6. Bereitstellung mit 5 Wegpunkten, die Assassine erreicht jeden -> kein "laeuft nicht los" (vorher Rauswurf am 3.)
  7. Abriss: Assassine neben ihrem Zielgebaeude, zielart 0, Laufziel = eigenes Feld, das Gebaeude verliert jede Runde Leben,
     400 Takte lang -> kein "STILLSTAND geloest" (vorher nach 200 Takten)
  8. Raid-Plaetze: eine Assassine bekommt kein Ziel -> _raid_plaetze == Zahl der vergebenen Ziele
  9. Routen-Laeufer, das Stueck bis zum naechsten Wegpunkt liegt im Beschuss -> Ziel aufgegeben ("ROUTE GEFAEHRLICH")
 10. (1017l, Pendeln) nach "ROUTE GEFAEHRLICH" auf Gebaeude 900 nimmt der Zielwechsel 900 nicht sofort wieder, obwohl es
     mehr Wert je Weg bringt als das neue Ziel
 11. (1017l, alle 5 im Anlauf tot) 5 Assassinen 28 Felder vor dem Lord, auf der Strecke 13 Schleuderer und 6 Boegen, der Lord
     selbst ohne freie Linie: KEINE Bereitstellung / kein Angriff; ohne die Schuetzen auf der Strecke: Bereitstellung oder Angriff
 12. (Daniel 18.10. "haelt jede Sekunde an") Runden je 150 Takte, Routen-Laeufer 6 Felder vor dem Wegpunkt: der naechste
     Wegpunkt geht schon jetzt hinaus (vorher erst ab 3 Feldern -> er stand am Wegpunkt bis zur naechsten Runde)
 13. (Daniel 18.10. "von Loewen getoetet") Loewe (Typ 45, Besitzer 0) 3 Felder neben einer Assassine -> sie weicht aus
 14. (Tode 1018n: 25-43 % Todesrisiko auf dem Weg zu unbeobachteten Zielen) einziges Ziel unbeobachtet, der Weg fuehrt durch
     einen Durchgang, den ein Bogen mit Spaeher sieht: ~17 % Todesrisiko -> KEIN Ziel (Grenze ZIEL_RISIKO_WEG 10 %)
 15. (Tode 1018n, Assassine 163 mit 120 Leben) derselbe Weg mit ~9 %: volles Leben -> Ziel; mit 7.000 Leben (schwach, dann ~16 %)
     -> KEIN Ziel (prueft beide Grenzen zusammen)
 16. (Tode 1018n, Assassine 17) Ziel 900 fuer sie gesperrt (ROUTE GEFAEHRLICH) -> die Zielwahl nimmt 900 nicht
Gegenprobe: python funde_pruefen.py <alte assassinen.py> [<alte sicht.py>] - die Faelle muessen dort rot sein.
Aufruf: python werkzeug/funde_pruefen.py"""
import importlib.util
import io
import os
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
ALT_A = sys.argv[1] if len(sys.argv) > 1 else None
ALT_S = sys.argv[2] if len(sys.argv) > 2 else None
sys.argv = sys.argv[:1]


def lade(name, pfad):
    spec = importlib.util.spec_from_file_location(name, pfad)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


import sicht as S
if ALT_S:
    S = lade("sicht", ALT_S)
A = lade("assassinen", ALT_A) if ALT_A else __import__("assassinen")
from ausweichen_pruefen import einheit


def ohne_nr(L):
    """wie waechter.lies_lagebild vor dem 18.10.: Schluessel = Nummer, im Datensatz kein nr/gruppe"""
    return {n: {k: v for k, v in e.items() if k not in ("nr", "gruppe")} for n, e in L.items()}


def neu():
    t = A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda nr, p: [True] * len(p))
    t._lord_bedarf = lambda L, G, ereignis: (5, "belegt", None)
    return t


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))

    # 1
    L = {600: einheit(23, 2, 200, 200, leben=17500), 100: einheit(73, 1, 192, 200), 101: einheit(73, 1, 50, 50)}
    lage = S.Lage(ohne_nr(L), {}, 1)
    b = lage.beschuss((192, 200))          # so fragt der Lenker im Spiel (umgebung, Regel 4, 4b): ohne Nummer
    pruefe(1, "Lagebild ohne nr: Beschuss am Ort von Assassine 100 = %.2f" % b, b > 0)
    # 2
    import waechter
    kopf = "tick 1\nnr besitzer typ x y leben zustand zielart zieleinheit zieluid zielgebaeude ziel zielx ziely laufx laufy auswahlvon auswahlmarke gruppe gruppenuid ladung arbeitsplatz erreichbar nahziel nahangreifer\n"
    zeile = "7 2 24 10 11 9000 1 0 0 0 0 0 0 0 10 11 0 0 33 4711 0 0 1 0 0\n"
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    f.write(kopf + zeile); f.close()
    alt = waechter.LAGEBILD
    waechter.LAGEBILD = f.name
    try:
        Lw = waechter.lies_lagebild(neu_holen=False)
    finally:
        waechter.LAGEBILD = alt
        os.unlink(f.name)
    e7 = Lw.get(7, {})
    pruefe(2, "lies_lagebild: nr %s, gruppe %s" % (e7.get("nr"), e7.get("gruppe")), e7.get("nr") == 7 and e7.get("gruppe") == 33)
    # 3
    LORD = (300, 200)
    t = neu(); t._raid_plaetze = 0
    L = {500: einheit(55, 2, LORD[0], LORD[1], leben=30000)}
    for i in range(6):
        L[200 + i] = einheit(73, 1, LORD[0] - 40, LORD[1] - 10 + 4 * i)
    t.aufnehmen([n for n in L if n != 500])
    t.schritt(L, {}, sichere_orte=[(100, 200)], tick=10000)
    lt = t.lordtrupp
    k0 = sorted(lt["mitglieder"])[0]
    p0 = lt["platz"][k0]
    L[k0].update(x=p0[0], y=p0[1], laufx=p0[0], laufy=p0[1])
    for i in range(4):
        L[700 + i] = einheit(23, 2, p0[0] + 6, p0[1] - 2 + i, leben=17500)
    erg, bef = t.schritt(L, {}, sichere_orte=[(100, 200)], tick=10030)
    neu_platz = lt["platz"].get(k0)
    pruefe(3, "Platz %s unsicher: Mitglied %s, neuer Platz %s, Meldungen %s" % (
        p0, k0 in lt["mitglieder"], neu_platz, [z[:60] for z in erg if "Platz" in z or "raus" in z][:2]),
        (k0 not in lt["mitglieder"]) or (neu_platz is not None and neu_platz != p0))
    # 4 und 5
    t = neu(); t._raid_plaetze = 0
    L = {500: einheit(55, 2, LORD[0], LORD[1], leben=30000), 501: einheit(55, 2, 60, 380, leben=30000)}
    for i in range(5):
        L[200 + i] = einheit(73, 1, LORD[0] - 2, LORD[1] - 2 + i)
    t.aufnehmen([n for n in L if n < 500])
    t.lordtrupp.update(mitglieder=set(range(200, 205)), phase="angriff", lord=500, angriff_tick=9000, seit=1)
    L.pop(500)
    erg, bef = t.schritt(L, {}, sichere_orte=[(100, 200)], tick=10000)
    auf_tot = [b_ for b_ in bef if b_.get("angriff", {}).get("ziel") == 500]
    pruefe(4, "Lord 500 weg: Phase %s, Befehle auf 500: %d" % (t.lordtrupp["phase"], len(auf_tot)),
           t.lordtrupp["phase"] is None and not auf_tot)
    t = neu(); t._raid_plaetze = 99
    L = {500: einheit(55, 2, LORD[0], LORD[1], leben=30000), 200: einheit(73, 1, 100, 100)}
    t.aufnehmen([200])
    t.lordtrupp.update(mitglieder=set(), phase="angriff", lord=500, angriff_tick=9000, seit=1)
    t.schritt(L, {}, sichere_orte=[(100, 200)], tick=10000)
    pruefe(5, "Angriff mit leerer Gruppe: Phase danach %s" % t.lordtrupp["phase"], t.lordtrupp["phase"] is None)
    # 6
    t = neu(); t._raid_plaetze = 0
    L = {500: einheit(55, 2, LORD[0], LORD[1], leben=30000)}
    for i in range(5):
        L[200 + i] = einheit(73, 1, LORD[0] - 100, LORD[1] + i)
    t.aufnehmen([n for n in L if n != 500])
    t.schritt(L, {}, sichere_orte=[(100, 200)], tick=10000)
    lt = t.lordtrupp
    k = 200
    platz = lt["platz"][k]
    start = (L[k]["x"], L[k]["y"])
    lt["weg"][k] = [(start[0] + 15 * i, start[1]) for i in range(1, 5)] + [platz]
    erg_alle = []
    lauf = None
    for r in range(1, 80):
        if k not in lt["mitglieder"] or lt["phase"] != "bereit":
            break
        if lauf:                                   # er folgt dem letzten Laufbefehl, 3 Felder je Runde, dort bleibt er stehen
            x, y = L[k]["x"], L[k]["y"]
            dx, dy = max(-3, min(3, lauf[0] - x)), max(-3, min(3, lauf[1] - y))
            nx, ny = x + dx, y + dy
            sx = (lauf[0] > nx) - (lauf[0] < nx)
            sy = (lauf[1] > ny) - (lauf[1] < ny)
            # wie im Spiel gemessen (1017j): beim Gehen zeigt das Laufziel 1 Feld voraus, angekommen auf das eigene Feld
            L[k].update(x=nx, y=ny, laufx=nx + sx, laufy=ny + sy, zustand=101 if (sx or sy) else 1)
        e, b_ = t.schritt(L, {}, sichere_orte=[(100, 200)], tick=10000 + 30 * r)
        erg_alle += e
        for bb in b_:
            a_ = bb.get("angriff", {})
            if a_.get("lauf") and k in a_.get("einheiten", []):
                lauf = tuple(a_["lauf"])
    raus = [z for z in erg_alle if ("%d laeuft" % k) in z or ("%d raus" % k) in z]
    pruefe(6, "5 Wegpunkte (je 15 Felder), er laeuft jeden Befehl ab: Rauswurf-Meldungen %d, am Platz %s" % (
        len(raus), max(abs(L[k]["x"] - platz[0]), abs(L[k]["y"] - platz[1])) <= 3), not raus)
    # 7
    t = neu(); t._raid_plaetze = 99
    G = {900: {"besitzer": 2, "typ": 20, "x": 150, "y": 150, "leben": 5000, "uid": 1, "erreichbar": 1}}
    L = {100: einheit(73, 1, 149, 149), 500: einheit(55, 2, 390, 390, leben=30000)}
    t.aufnehmen([100])
    t.ziel[100] = 900; t.ziel_typ[900] = 20; t.befohlen[100] = 0
    erg_alle = []
    for r in range(1, 15):
        G[900]["leben"] -= 100
        L[100].update(zielart=0, laufx=149, laufy=149, zustand=107)
        e, b_ = t.schritt(L, G, sichere_orte=[(100, 200)], tick=10000 + 30 * r)
        erg_alle += e
    still = [z for z in erg_alle if z.startswith("STILLSTAND")]
    pruefe(7, "Abriss 420 Takte, Gebaeude verliert Leben: STILLSTAND-Meldungen %d, Ziel %s" % (len(still), t.ziel.get(100)), not still)
    # 8
    t = neu()
    viele = {600 + i: einheit(23, 2, 144 + i % 2, 151 + i // 2, leben=17500) for i in range(6)}
    L = {100: einheit(73, 1, 130, 153), 500: einheit(55, 2, 390, 390, leben=30000)}
    L.update(viele)
    G = {900: {"besitzer": 2, "typ": 3, "x": 152, "y": 152, "leben": 100, "uid": 1, "erreichbar": 1}}
    t.aufnehmen([100])
    t.schritt(L, G, sichere_orte=[(100, 200)], tick=10000)
    pruefe(8, "keiner bekommt ein Ziel: Raid-Plaetze %s, vergebene Ziele %d" % (t._raid_plaetze, len(t.ziel)),
           t._raid_plaetze == len(t.ziel))
    # 9
    t = neu(); t._raid_plaetze = 99
    L = {100: einheit(73, 1, 100, 100), 500: einheit(55, 2, 390, 390, leben=30000),
         600: einheit(23, 2, 112, 104, leben=17500), 601: einheit(24, 2, 112, 106, leben=10000)}
    G = {900: {"besitzer": 2, "typ": 3, "x": 160, "y": 100, "leben": 100, "uid": 1, "erreichbar": 1}}
    t.aufnehmen([100])
    t.ziel[100] = 900; t.ziel_typ[900] = 3; t.befohlen[100] = 0
    t.route[100] = {"punkte": [(115, 100), (140, 100)], "gebaeude": 900, "befohlen": 0}
    L[100].update(laufx=115, laufy=100, zustand=101)
    erg, bef = t.schritt(L, G, sichere_orte=[(50, 50)], tick=10000)
    pruefe(9, "Route durch Beschuss: Meldung %s, Route noch da %s" % (
        [z[:50] for z in erg if "ROUTE" in z][:1], 100 in t.route and t.route[100]["punkte"][:1] == [(115, 100)]),
        any("ROUTE GEFAEHRLICH" in z for z in erg))
    # 10
    if True:
        if hasattr(t, "_route_sperre"):      # so steht es nach ROUTE GEFAEHRLICH (Fall 9) - die alte Fassung kennt keine Sperre
            assert (100, 900) in t._route_sperre, "Fall 9 hat keine Sperre gesetzt"
        G2 = dict(G)
        G2[901] = {"besitzer": 2, "typ": 26, "x": 60, "y": 60, "leben": 100, "uid": 2, "erreichbar": 1}
        L2 = {100: einheit(73, 1, 100, 100), 500: einheit(55, 2, 390, 390, leben=30000)}
        t.route.pop(100, None)
        t.ziel[100] = 901; t.ziel_typ[901] = 26; t.befohlen[100] = t.runde
        L2[100].update(laufx=60, laufy=60, zustand=101)
        erg, bef = t.schritt(L2, G2, sichere_orte=[(50, 50)], tick=10030)
        pruefe(10, "gesperrtes Ziel 900: Zielwechsel-Meldungen %s, Ziel jetzt %s" % (
            [z[:40] for z in erg if "ZIELWECHSEL" in z][:1], t.ziel.get(100)), t.ziel.get(100) != 900)
    # 11
    def lord_lage(mit_schuetzen):
        t = neu(); t._raid_plaetze = 0
        t._lord_bedarf = lambda L, G, ereignis: (5, "belegt", None)
        L = {500: einheit(55, 2, 300, 200, leben=30000)}
        for i in range(5):
            L[200 + i] = einheit(73, 1, 272, 198 + i)
        if mit_schuetzen:
            for i in range(13):
                L[600 + i] = einheit(72, 2, 285 + i % 4, 190 + i // 4 * 2, leben=10000)
            for i in range(6):
                L[620 + i] = einheit(22, 2, 288 + i % 3, 210 + i // 3 * 2, leben=10000)
        t.aufnehmen([n for n in L if 200 <= n < 300])
        erg, bef = t.schritt(L, {}, sichere_orte=[(100, 200)], tick=10000)
        return t.lordtrupp["phase"]
    ph_mit, ph_ohne = lord_lage(True), lord_lage(False)
    pruefe(11, "Anlauf durch 19 Schuetzen: Phase %s; ohne Schuetzen: Phase %s" % (ph_mit, ph_ohne), ph_mit is None and ph_ohne in ("bereit", "angriff"))
    # 12
    t = neu(); t._raid_plaetze = 99
    L = {100: einheit(73, 1, 100, 100), 500: einheit(55, 2, 390, 390, leben=30000)}
    G = {900: {"besitzer": 2, "typ": 3, "x": 180, "y": 100, "leben": 100, "uid": 1, "erreichbar": 1}}
    t.aufnehmen([100])
    t.ziel[100] = 900; t.ziel_typ[900] = 3; t.befohlen[100] = 0
    t.route[100] = {"punkte": [(130, 100), (150, 100)], "gebaeude": 900, "befohlen": 0}
    for i, tk in enumerate((10000, 10150)):
        L[100].update(x=100 + 12 * i, y=100, laufx=130, laufy=100, zustand=101)
        erg, bef = t.schritt(L, G, sichere_orte=[(50, 50)], tick=tk)
    L[100].update(x=124, y=100, laufx=130, laufy=100, zustand=101)          # 6 Felder vor dem Wegpunkt
    erg, bef = t.schritt(L, G, sichere_orte=[(50, 50)], tick=10300)
    naechster = [b_ for b_ in bef if b_.get("angriff", {}).get("lauf") == [150, 100]]
    pruefe(12, "Rundenlaenge 150 Takte, 6 Felder vor dem Wegpunkt: Laufbefehl zum naechsten (150,100) %s" % bool(naechster), naechster)
    # 13
    t = neu(); t._raid_plaetze = 99
    L = {100: einheit(73, 1, 100, 100), 500: einheit(55, 2, 390, 390, leben=30000), 700: einheit(45, 0, 103, 100, leben=20000)}
    G = {900: {"besitzer": 2, "typ": 3, "x": 180, "y": 100, "leben": 100, "uid": 1, "erreichbar": 1}}
    t.aufnehmen([100])
    erg, bef = t.schritt(L, G, sichere_orte=[(50, 50)], tick=10000)
    pruefe(13, "Loewe 3 Felder daneben: Ausweichen %s" % [z[:40] for z in erg if "AUSWEICHEN" in z][:1],
           any("AUSWEICHEN" in z for z in erg) or 100 in t.flucht)
    # 14 - 16: Wand bei x 112-127 mit einem Durchgang y 96-103; ein Bogen mit Spaeher (Speer) noerdlich davon macht ein
    # kurzes Stueck des Weges sichtbar - so liegt das Wegrisiko zwischen den Grenzen (alte Fassung: erst ab ~42 % kein Ziel)
    zeilen = []
    for y in range(400):
        z = ['G'] * 400
        if not (96 <= y <= 103):
            for x in range(112, 128):
                z[x] = 'X'
        zeilen.append(''.join(z))

    def lage_risiko(leben, spaeher_y, sperre=False):
        t = neu(); t._raid_plaetze = 99
        t.gelaende = zeilen
        L = {100: einheit(73, 1, 100, 100, leben=leben), 500: einheit(55, 2, 390, 390, leben=30000)}
        if spaeher_y:
            L[650] = einheit(24, 2, 120, spaeher_y, leben=10000)
            L[600] = einheit(22, 2, 120, spaeher_y - 1, leben=10000)
        G = {900: {"besitzer": 2, "typ": 3, "x": 140, "y": 98, "leben": 100, "uid": 1, "erreichbar": 1}}
        t.aufnehmen([100])
        if sperre and hasattr(t, "_route_sperre"):
            t._route_sperre[(100, 900)] = 10000 + 1500
        erg, bef = t.schritt(L, G, sichere_orte=[(50, 50)], tick=10000)
        return t.ziel.get(100), [z[:90] for z in erg if z.startswith("ZIELWAHL")][:1]
    z14, m14 = lage_risiko(12500, 82)
    pruefe(14, "Weg mit ~17 %% Todesrisiko (Bogen + Spaeher am Durchgang): Ziel %s %s" % (z14, m14), z14 is None)
    z15a, _ = lage_risiko(12500, 78)
    z15, m15 = lage_risiko(7000, 78)
    pruefe(15, "Weg mit ~9 %%: volles Leben Ziel %s (soll 900); mit 7.000 Leben (schwach, ~16 %%): Ziel %s %s" % (z15a, z15, m15),
           z15a == 900 and z15 is None)
    z16, m16 = lage_risiko(12500, None, sperre=True)
    pruefe(16, "Ziel 900 gesperrt: Ziel %s" % z16, z16 != 900)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
