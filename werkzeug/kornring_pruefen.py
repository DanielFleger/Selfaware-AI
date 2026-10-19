# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer kornring.py und den Ringabstand in nahrungswahl.speicherplatz (18.10.). Vorher festgelegt:
  1. Ring um (100, 50): 16 Kacheln, je Seite 4, alle direkt am 4x4-Speicher, keine der 4 Ecken
  2. leerer Ring, 8 Stein: genau 3 Seiten gesendet (je 3 Stein noetig, 2 verbraucht), die vierte wartet auf Stein;
     bleibt der Wartegrund gleich, kommt keine zweite Wartemeldung (Lauf 1018f: 4 Zeilen alle 100 Ticks)
  3. leerer Ring, 0 Stein: NICHTS gesendet (das Spiel wuerde eine Gratiskachel setzen)
  4. eine ganze Seite gesendet, stand danach nicht (jemand stand darauf): beim naechsten Blick (100 Ticks spaeter) wird
     diese Seite Kachel fuer Kachel gesendet, die anderen nicht
  5. alles steht: eine Meldung "steht", kein Befehl, Steinbedarf 0
  6. zweiter Aufruf nach 50 Ticks: keine Pruefung, kein Befehl
  7. Kornspeicherplatz beider 1v1-Plaetze auf Close Encounters: keine geplante Apfelplantage auf dem Ring
Moerderloecher (Gegner oben links, Speicher (100, 50)):
  8. 20 Holz, 0 Stein, keine Mauer: genau 3 Gruben, alle auf Ecken (5 Holz Reserve fuer den Speicher bleiben)
  9. 100 Holz, 0 Stein: erster Schritt die 4 Ecken; zweiter Schritt (100 Ticks spaeter, Ecken stehen) 4 Seitenfelder,
     alle auf den Seiten oben/links (dem Gegner zugewandt)
 10. Mauer steht ganz (16), 100 Holz: nur die 4 Ecken, keine Seite
 11. 20 Stein, keine Mauer, 100 Holz: Gruben nur auf die Ecken, die Seiten bekommen Mauer (4 Seiten gesendet)
 12. das Spiel lehnt ein Eckfeld ab: 100 Ticks spaeter kein neuer Versuch dort, nach 1000 Ticks wieder
Burggraben (19.10., Gegner links bei (60, 52), Speicher (100, 50)):
 13. Soll = Ring auf Abstand 2 (28 Felder) ohne die 3 Eingangsfelder; der Eingang liegt auf der dem Gegner abgewandten
     (rechten) Seite, x = 105
 14. die Befehlsfolge (planen Abstand 3, loeschen Abstand 4, Eingang loeschen) ergibt auf leerer Karte GENAU das Soll -
     kein Feld auf Abstand 1 (Ring/Gruben) und keins auf Abstand 3
 15. erster Schritt: plant (Befehle gesendet) und schickt die 4 naechsten grabfaehigen Einheiten - nie Streitkolben (Feldzug),
     Assassinen, den Lord oder ausgenommene; 100 Ticks spaeter (Felder geplant, nichts gegraben) kein neues Schicken (unter
     300 Ticks); alles ausgehoben -> "fertig", keine Graeber mehr
 16. Grubenplaetze: erst die 4 Ecken, dann die 3 Eingangsfelder
 17. bleiben nach dem Planen dieselben Felder unplanbar (bebaut), plant der Graben nicht alle 1.000 Ticks neu, sondern nach
     dem zweiten Versuch (Zahl gleich) erst nach 5.000 Ticks: Planen bei Tick 1.000, 2.000, 7.000
Gegenprobe: mit "alt" sendet der Baustein ohne Steinpruefung, die Platzwahl ohne Ringabstand, die Gruben ohne Holzreserve
und der Graben ohne Loeschbloecke -> Faelle 2, 3, 7, 8 und 14 rot.
Aufruf: python werkzeug/kornring_pruefen.py [alt]"""
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import kornring as KR
import nahrungswahl as N

if len(sys.argv) > 1 and sys.argv[1] == "alt":
    KR.bezahlbar = lambda stein, kacheln: True
    N.RING_RAND = 0
    KR.HOLZ_RESERVE = 0
    _alt_plan = KR.plan_befehle
    KR.plan_befehle = lambda gx, gy, feind: [b for b in _alt_plan(gx, gy, feind) if b[2] == 0]


def neu(stehen=()):
    gesendet = []
    stehen = set(stehen)
    r = KR.Kornring((100, 50), lambda ks: {k: k in stehen for k in ks},
                    lambda x1, y1, x2, y2, n: gesendet.append((x1, y1, x2, y2, n)))
    return r, gesendet, stehen


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))

    s = KR.seiten(100, 50)
    alle = [k for _, _, _, ks in s for k in ks]
    ecken = {(99, 49), (104, 49), (99, 54), (104, 54)}
    innen = {(x, y) for x in range(100, 104) for y in range(50, 54)}
    am_speicher = all(any(abs(k[0] - i[0]) + abs(k[1] - i[1]) == 1 for i in innen) for k in alle)
    pruefe(1, "16 Kacheln %s, je Seite %s, Ecken drin %s, alle am Speicher %s" % (
        len(set(alle)), [len(ks) for _, _, _, ks in s], bool(ecken & set(alle)), am_speicher),
           len(set(alle)) == 16 and all(len(ks) == 4 for _, _, _, ks in s) and not ecken & set(alle) and am_speicher)
    r, g, _ = neu()
    ev = r.schritt(1000, 8)
    ev2 = r.schritt(1100, 0)       # gleicher Wartegrund? nein - jetzt fehlen weniger Kacheln nicht (nichts stand), 0 Stein
    ev3 = r.schritt(1200, 0)       # derselbe Grund wie eben -> keine neue Meldung
    pruefe(2, "8 Stein: %d Seiten gesendet, wartet: %s; gleicher Grund erneut gemeldet: %s" % (
        len(g), [e for e in ev if "wartet" in e], [e for e in ev3 if "wartet" in e]),
           len(g) == 3 and all(x[4] == 4 for x in g) and sum("wartet" in e for e in ev) == 1
           and not any("wartet" in e for e in ev3))
    r, g, _ = neu()
    r.schritt(1000, 0)
    pruefe(3, "0 Stein: %d Befehle" % len(g), len(g) == 0)
    r, g, stehen = neu()
    r.schritt(1000, 20)
    erste = list(g)
    stehen |= {k for _, _, _, ks in KR.seiten(100, 50)[1:] for k in ks}      # alle Seiten ausser "oben" stehen jetzt
    del g[:]
    r.schritt(1100, 20)
    pruefe(4, "zuerst %d ganze Seiten; danach einzeln: %s" % (len(erste), g),
           len(erste) == 4 and len(g) == 4 and all(x[4] == 1 and x[1] == 49 and x[3] == 49 for x in g))
    r, g, _ = neu(alle)
    ev = r.schritt(1000, 20)
    pruefe(5, "alles steht: %s, Befehle %d, Steinbedarf %d" % (ev, len(g), r.stein_bedarf()),
           len(ev) == 1 and "steht" in ev[0] and not g and r.stein_bedarf() == 0)
    r, g, _ = neu()
    r.schritt(1000, 20)
    n1 = len(g)
    r.schritt(1050, 20)
    pruefe(6, "nach 50 Ticks: %d neue Befehle" % (len(g) - n1), len(g) == n1)
    erg = []
    for kurz in ("CloseEncounters_pl3-2_1v1", "CloseEncounters_pl2-3_1v1"):
        plan = json.load(open(os.path.join(HIER, "..", "daten", "eroeffnung_plan_%s.json" % kurz), encoding="utf-8"))
        w = N.waehle(kurz, plan, bev_ziel=90, ration="doppelt", horizont=80000)
        gx, gy = w["kornspeicher"]
        ring = {k for _, _, _, ks in KR.seiten(gx, gy) for k in ks}
        auf = sum(len({(x + i, y + j) for i in range(10) for j in range(10)} & ring) for x, y in (w["aepfel"] or []))
        erg.append((kurz.split("_")[1], (gx, gy), auf))
    pruefe(7, "Plantagen-Kacheln auf dem Ring je Platz: %s" % erg, all(a == 0 for _, _, a in erg))
    # Moerderloecher
    def mit_gruben(stehen=(), ablehnen=()):
        mauer, gruben = [], []
        stehen = set(stehen)
        def grube(x, y):
            if (x, y) in ablehnen:
                return False
            gruben.append((x, y))
            return True
        r = KR.Kornring((100, 50), lambda ks: {k: k in stehen for k in ks},
                        lambda x1, y1, x2, y2, n: mauer.append((x1, y1, x2, y2, n)), setze_grube=grube, feind=(60, 10))
        return r, mauer, gruben
    eck = set(KR.ecken(100, 50))
    r, m, g = mit_gruben()
    r.schritt(1000, 0, holz=20)
    pruefe(8, "20 Holz: Gruben %s" % g, len(g) == 3 and all(k in eck for k in g))
    r, m, g = mit_gruben()
    r.schritt(1000, 0, holz=100)
    erste = list(g)
    r.schritt(1100, 0, holz=100, gruben=erste)
    zweite = g[len(erste):]
    pruefe(9, "100 Holz: erst %s, dann %s" % (erste, zweite),
           set(erste) == eck and len(zweite) == 4 and all(k[1] == 49 or k[0] == 99 for k in zweite))
    r, m, g = mit_gruben(stehen=alle)
    r.schritt(1000, 0, holz=100)
    pruefe(10, "Mauer steht: Gruben %s" % g, set(g) == eck)
    r, m, g = mit_gruben()
    r.schritt(1000, 20, holz=100)
    pruefe(11, "20 Stein: Gruben %s, Mauerbefehle %d" % (g, len(m)), set(g) == eck and len(m) == 4)
    ecke = (99, 49)
    r, m, g = mit_gruben(stehen=alle, ablehnen={ecke})
    r.schritt(1000, 0, holz=100)
    n1 = sum(1 for k in g if k == ecke)
    r.schritt(1100, 0, holz=100, gruben=list(g))
    r.schritt(2100, 0, holz=100, gruben=list(g))
    pruefe(12, "abgelehnte Ecke: gesetzt %d, gesperrt bis Tick %s, Versuche danach angenommen? %s" % (
        n1, r.gesperrt.get(ecke), ecke in g), n1 == 0 and r.gesperrt.get(ecke) == 2100)
    # Burggraben
    feind = (60, 52)
    soll = KR.graben_soll(100, 50, feind)
    mitte, tor = KR.eingang(100, 50, feind)
    r2 = set(KR.ring(100, 50, 2))
    pruefe(13, "Soll %d Felder, Ring 2 hat %d, Eingang %s" % (len(soll), len(r2), tor),
           len(r2) == 28 and len(soll) == 25 and set(soll) | set(tor) == r2 and all(k[0] == 105 for k in tor))
    erg = KR.pinsel(KR.plan_befehle(100, 50, feind))
    zu_nah = erg & set(KR.ring(100, 50, 1))
    zu_weit = erg & set(KR.ring(100, 50, 3))
    pruefe(14, "Planung ergibt %d Felder, = Soll %s, auf Abstand 1: %d, auf Abstand 3: %d" % (
        len(erg), erg == set(soll), len(zu_nah), len(zu_weit)), erg == set(soll) and not zu_nah and not zu_weit)
    logik = {}
    geplant_cmds, geschickt = [], []
    def plane(x, y, f2):
        geplant_cmds.append((x, y, f2))
    gr = KR.Graben((100, 50), feind, lambda ks: {k: logik.get(k, 0) for k in ks}, plane,
                   lambda einh, ziel: geschickt.append((list(einh), ziel)))
    L = {1: {"besitzer": 1, "typ": 24, "x": 101, "y": 60, "leben": 100}, 2: {"besitzer": 1, "typ": 22, "x": 102, "y": 61, "leben": 100},
         3: {"besitzer": 1, "typ": 26, "x": 101, "y": 58, "leben": 100}, 4: {"besitzer": 1, "typ": 73, "x": 101, "y": 57, "leben": 100},
         5: {"besitzer": 1, "typ": 55, "x": 101, "y": 56, "leben": 100}, 6: {"besitzer": 1, "typ": 71, "x": 99, "y": 62, "leben": 100},
         7: {"besitzer": 1, "typ": 24, "x": 103, "y": 63, "leben": 100}, 8: {"besitzer": 1, "typ": 25, "x": 104, "y": 64, "leben": 100},
         9: {"besitzer": 2, "typ": 24, "x": 101, "y": 55, "leben": 100}, 10: {"besitzer": 1, "typ": 24, "x": 100, "y": 59, "leben": 100}}
    gr.schritt(1000, L, 1, ausgenommen={10})
    n_plan = len(geplant_cmds)
    for k in soll:
        logik[k] = KR.GEPLANT
    gr.schritt(1100, L, 1, ausgenommen={10})
    erst = geschickt[0][0] if geschickt else []
    n_schick_1100 = len(geschickt)
    for k in soll:
        logik[k] = KR.GEGRABEN
    ev = gr.schritt(1400, L, 1, ausgenommen={10})
    pruefe(15, "geplant %d Befehle; geschickt %s (bei 1100: %d Sendungen); fertig %s, Graeber danach %s" % (
        n_plan, erst, n_schick_1100, gr.fertig, gr.graeber),
           n_plan > 0 and sorted(erst) == [1, 2, 6, 7] and n_schick_1100 == 1 and gr.fertig and not gr.graeber)
    # 17: dieselben 7 Felder bleiben unplanbar (bebaut) -> nach dem ersten Planen erst nach 5.000 Ticks wieder planen
    plan17 = []
    gr17 = KR.Graben((100, 50), feind, lambda ks: {k: (KR.GEPLANT if i >= 7 else 0) for i, k in enumerate(ks)},
                     lambda x, y, f2: plan17.append(t), lambda e, z: None)
    for t in range(1000, 7200, 100):
        gr17.schritt(t, {}, 1)
    zeiten17 = sorted(set(plan17))
    pruefe(17, "gleich viele fehlende Felder: geplant bei Tick %s" % zeiten17, zeiten17 == [1000, 2000, 7000])
    k16 = KR.Kornring((100, 50), lambda ks: {}, lambda *a: None, setze_grube=lambda x, y: True, feind=feind)
    k16.tor = list(tor)
    pl = k16.grubenplaetze(20, set(), {})
    pruefe(16, "Grubenreihenfolge %s" % pl[:7], pl[:4] == KR.ecken(100, 50) and pl[4:7] == tor)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
