# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer raids.py (19.10., B-168 neu am 22.10.). Raten fest (nicht aus der Datei): Sklave Faktor 20,3 gegen L73
und 12 Takte je Feld (gemessen 22.10.), Pferdebogen ungemessen -> vorsichtigster Faktor (20,3), 12 Takte je Feld.
Vorher festgelegt (wir = Spieler 1, Sklave bei (100, 100), Leben 6.000):
  1. Waffenlager 30 Felder weg, Holzfaeller 25 weg, Soeldnerposten 10 weg mit feindlichem Bogen 3 Felder daneben -> der Posten
     faellt weg (am Ziel allein 2,10 x 165 Takte x 20,3 = 7.034 > 6.000 Leben), Ziel ist das Waffenlager
  2. zwei Sklaven -> zwei verschiedene Ziele (Waffenlager und Holzfaeller)
  3. das Waffenlager brennt (Feuer 40), der Sklave steht davor -> Meldung "angezuendet", er bekommt das naechste Ziel, das
     Waffenlager kommt nie wieder dran
  4. feindliche Fallgrube 2 Felder neben dem Waffenlager -> es wird gemieden, Ziel ist der Holzfaeller
  5. Reiter: feindlicher Holzfaeller 15 Felder weg, keine Gefahr -> Angriffsbefehl auf ihn; feindlicher Speer 6 Felder neben
     dem Reiter -> Laufbefehl, das Ziel liegt weiter vom Speer weg als der Reiter
  6. der gejagte Holzfaeller ist weg -> genau ein Abschuss gezaehlt, auch nach drei weiteren Runden
  8. (22.10.: Reiter stand 11.700 Takte nach einem Angriffsbefehl auf 166-215 Felder) Holzfaeller 60 Felder weg -> KEIN
     Angriffsbefehl, sondern eine Wegkette (lauf + danach), letzter Punkt hoechstens 8 Felder vom Holzfaeller
  9. Huette und Waffenlager gleich weit -> der Sklave nimmt die Huette (Pennerhof)
 10. feindlicher Bauer (Lagerfeuer) und Holzfaeller gleich weit -> der Reiter jagt den Bauern
  7. Werbung: 100 Gold / 10 am Feuer -> 5 Sklaven, 1 Reiter; 20 Gold / 3 am Feuer -> 1 Sklave (2 bleiben am Feuer)
 11. (B-129) Bogen 5 Felder neben dem Waffenlager: ohne Deckung zu teuer (Rechnung ~7.150 > 6.000); ein eigener Schleuderer
     3 Felder neben dem Bogen deckt ihn -> Waffenlager; Fallgrube bleibt gesperrt
 12. Deckung greift Kaempfer vor Arbeitern an, ohne Feind laeuft sie zur Front
 13. Werbung mit DECKUNG_SOLL 4
 14. (B-133) Waffenlager des Verbuendeten ist kein Ziel
 15. (B-168 "ausholen") Huette 60 Felder weg, Armbrust 4 Felder neben der geraden Strecke -> der Plan hat weniger Beschuss als die
     Gerade UND ein Wegpunkt liegt mindestens 10 Felder neben ihr
 16. (B-168 "auf dem Weg mitnehmen") Huette (200,100), Holzfaeller (170,100): von (100,100) aus die Huette (12/1365 > 5/1005);
     bei (165,100) der Holzfaeller (Meldung "nimmt unterwegs mit"); brennt er, wieder die Huette
 17. (B-168 Risiko) Reiter (100,100), einziger Arbeiter (110,100) mit 10 Armbruesten 2 Felder daneben (am Ziel allein
     10 x 2,10 x 44 x 20,3 = 18.757 > 15.000) -> keine Jagd; der Reiter steht im Beschuss -> Rueckzug, letzter Punkt ohne Beschuss
     (mehr als 44 Felder von den Armbruesten)
Gegenprobe "alt": Faktor 0 (kein Risiko) und kein Vorrang fuer Beschuss -> 1, 11, 15, 17 rot.
Aufruf: python werkzeug/raids_pruefen.py [alt]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import gefahrenschutz as GS
import raids as R
import parteien
parteien.setzen(1, {1})   # B-133: ohne Spiel - nur Spieler 1 ist Freund

ALT = len(sys.argv) > 1 and sys.argv[1] == "alt"
RATEN = {71: {"verlust": 20300.0, "vorhersage": 1000.0, "felder": 1000, "takte": 12000}}
if ALT:
    RATEN = {71: {"verlust": 0.0, "vorhersage": 1000.0, "felder": 1000, "takte": 12000}}
    _init = GS.Lage.__init__

    def _ohne_vorrang(self, *a, **k):
        _init(self, *a, **k)
        self.vorrang = 0.0
    GS.Lage.__init__ = _ohne_vorrang


def einheit(typ, sp, x, y, zustand=1, leben=None):
    return {"typ": typ, "besitzer": sp, "x": x, "y": y, "leben": leben or (15000 if typ == 74 else 6000), "zustand": zustand}


def geb(typ, sp, x, y):
    return {"typ": typ, "besitzer": sp, "x": x, "y": y}


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, warte=1.0, bis=None):
        self.liste.append(b)
        return []


G0 = {1: geb(11, 2, 130, 100), 2: geb(3, 2, 125, 100), 3: geb(8, 2, 100, 110)}


def L0(*sklaven):
    L = {900: einheit(22, 2, 100, 113)}
    for i, o in enumerate(sklaven):
        L[10 + i] = einheit(71, 1, o[0], o[1])
    return L


def BT():
    return R.Brandtrupp(1, lambda nr: 0, raten=RATEN)


def RJ():
    return R.Reiterjagd(1, raten=RATEN)


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed))
        print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)

    feuer = {}
    bt = R.Brandtrupp(1, lambda nr: feuer.get(nr, 0), raten=RATEN)
    bt.schritt(L0((100, 100)), G0, Befehle())
    pruefe(1, "Ziel des Sklaven: %s (abgelehnt %d)" % (bt.ziel, bt.abgelehnt), bt.ziel.get(10) == 1)

    bt2 = BT()
    bt2.schritt(L0((100, 100), (100, 101)), G0, Befehle())
    pruefe(2, "zwei Sklaven: %s" % bt2.ziel, sorted(bt2.ziel.values()) == [1, 2])

    feuer[1] = 40
    aus3 = []
    for _ in range(R.NEU_ALLE):
        aus3 = bt.schritt(L0((129, 100)), G0, Befehle())
        if any("angezuendet" in a for a in aus3):
            break
    pruefe(3, "Waffenlager brennt: Meldungen %s, neues Ziel %s, verbrannt %s" % ([a[:50] for a in aus3], bt.ziel, bt.brennt),
           any("angezuendet" in a for a in aus3) and bt.ziel.get(10) not in (1, None) and 1 in bt.brennt)

    G4 = dict(G0)
    G4[50] = geb(67, 2, 132, 100)
    bt4 = BT()
    bt4.schritt(L0((100, 100)), G4, Befehle())
    pruefe(4, "Grube am Waffenlager: Ziel %s" % bt4.ziel, bt4.ziel.get(10) == 2)

    rj = RJ()
    L5 = {20: einheit(74, 1, 100, 100), 700: einheit(3, 2, 115, 100)}
    b5 = Befehle()
    rj.schritt(L5, {}, b5)
    jagd = [x for x in b5.liste if x["angriff"].get("ziel") == 700]
    L5b = {20: einheit(74, 1, 100, 100), 700: einheit(3, 2, 115, 100), 701: einheit(24, 2, 106, 100)}
    b5b = Befehle()
    RJ().schritt(L5b, {}, b5b)
    lauf = [x["angriff"]["lauf"] for x in b5b.liste if "lauf" in x["angriff"]]
    pruefe(5, "Jagd %s; mit Speer daneben Lauf %s" % (bool(jagd), lauf),
           jagd and lauf and R.schach(lauf[0], (106, 100)) > R.schach((100, 100), (106, 100)))

    L6 = {20: einheit(74, 1, 100, 100)}
    for _ in range(4):
        rj.schritt(L6, {}, Befehle())
    pruefe(6, "Abschuesse nach Verschwinden + 3 Runden: %d" % rj.getoetet, rj.getoetet == 1)

    b8 = Befehle()
    RJ().schritt({20: einheit(74, 1, 100, 100), 800: einheit(3, 2, 160, 100)}, {}, b8)
    a8 = [x["angriff"] for x in b8.liste]
    letzter = (a8[0].get("danach") or [a8[0].get("lauf")])[-1] if a8 else None
    pruefe(8, "Holzfaeller 60 Felder weg: Befehle %s" % [{k: (v if k != "danach" else len(v)) for k, v in a.items()} for a in a8],
           a8 and "ziel" not in a8[0] and "danach" in a8[0] and letzter and R.schach(letzter, (160, 100)) <= 8)

    bt9 = BT()
    bt9.schritt({10: einheit(71, 1, 100, 100)}, {1: geb(11, 2, 120, 100), 2: geb(1, 2, 100, 120)}, Befehle())
    pruefe(9, "Huette und Waffenlager 20 Felder: Ziel %s" % bt9.ziel, bt9.ziel.get(10) == 2)
    b10 = Befehle()
    RJ().schritt({20: einheit(74, 1, 100, 100), 900: einheit(3, 2, 115, 100), 901: einheit(1, 2, 100, 115)}, {}, b10)
    pruefe(10, "Bauer und Holzfaeller 15 Felder: Ziel %s" % [x["angriff"].get("ziel") for x in b10.liste],
           any(x["angriff"].get("ziel") == 901 for x in b10.liste))
    w = (R.werbung(100, 10, 0, 0), R.werbung(20, 3, 0, 0))
    pruefe(7, "Werbung 100/10: %s, 20/3: %s" % w, w[0] == [(71, 5), (74, 1)] and w[1] == [(71, 1)])

    L11 = {1: einheit(71, 1, 100, 100), 50: einheit(22, 2, 135, 100)}
    G11 = {7: geb(11, 2, 130, 100)}
    ohne = [k for k, _ in BT()._ziele(L11, G11, (100, 100), set())]
    b_mit = BT()
    b_mit.schutz = [(138, 100)]
    mit = [k for k, _ in b_mit._ziele(L11, G11, (100, 100), set())]
    G11g = {7: geb(11, 2, 130, 100), 8: geb(67, 2, 131, 101)}
    grube = [k for k, _ in b_mit._ziele(L11, G11g, (100, 100), set())]
    pruefe(11, "Deckung: ohne %s, mit Schleuderer %s, mit Fallgrube %s" % (ohne, mit, grube), ohne == [] and mit == [7] and grube == [])

    d = R.Deckung(1, (50, 50))
    L12 = {3: einheit(72, 1, 100, 100), 60: einheit(24, 2, 108, 100), 61: einheit(3, 2, 106, 100)}
    bf = Befehle()
    d.schritt(L12, {}, bf)
    b_sk = BT()
    b_sk.ziel = {1: 7}
    bf2 = Befehle()
    R.Deckung(1, (50, 50)).schritt({3: einheit(72, 1, 100, 100)}, {7: geb(11, 2, 160, 100)}, bf2, b_sk)
    a12 = [c["angriff"] for c in bf.liste if "angriff" in c]
    a12b = [c["angriff"] for c in bf2.liste if "angriff" in c]
    pruefe(12, "Deckung greift %s an, ohne Feind laeuft sie %s" % (a12, a12b),
           a12 and a12[0].get("ziel") == 60 and a12b and a12b[0].get("lauf") == [160, 100])
    R.DECKUNG_SOLL = 4
    w13 = R.werbung(100, 10, 0, 0, 0)
    R.DECKUNG_SOLL = 0
    pruefe(13, "Werbung mit Deckung 100/10: %s" % w13, w13 == [(71, 5), (72, 3)])

    L14 = {1: einheit(71, 1, 100, 100)}
    G14 = {7: geb(11, 2, 110, 100), 8: geb(11, 3, 140, 100)}
    parteien.setzen(1, {1, 2})
    mit_v = [k for k, _ in BT()._ziele(L14, G14, (100, 100), set())]
    parteien.setzen(1, {1})
    ohne_v = [k for k, _ in BT()._ziele(L14, G14, (100, 100), set())]
    pruefe(14, "Verbuendeter Spieler 2: Ziele %s (ohne Verbuendete %s)" % (mit_v, ohne_v), mit_v == [8] and ohne_v[:1] == [7])

    # 15. ausholen
    L15 = {10: einheit(71, 1, 100, 100), 950: einheit(23, 2, 130, 104)}
    G15 = {1: geb(1, 2, 160, 100)}
    b15 = Befehle()
    bt15 = BT()
    bt15.schritt(L15, G15, b15)
    lage15 = R._lage_fuer(1, L15, G15, RATEN)
    gerade = [(x, 100) for x in range(101, 161)]
    s_gerade = sum(lage15.schaden(q) for q in gerade)
    pl15 = bt15.plan.get(10)
    s_plan = sum(lage15.schaden(q) for q in pl15["weg"]["weg"][1:]) if pl15 else None
    wp = lage15.wegpunkte(pl15["weg"]["weg"]) if pl15 else []
    pruefe(15, "ausholen: Beschuss Plan %s gegen Gerade %.1f, Wegpunkte %s" % (None if s_plan is None else round(s_plan, 1), s_gerade, wp[:8]),
           pl15 and s_plan < s_gerade and max(abs(q[1] - 100) for q in wp) >= 10)

    # 16. mitnehmen
    feuer16 = {}
    G16 = {1: geb(1, 2, 200, 100), 3: geb(3, 2, 170, 100)}
    bt16 = R.Brandtrupp(1, lambda nr: feuer16.get(nr, 0), raten=RATEN)
    bt16.schritt({10: einheit(71, 1, 100, 100, zustand=101)}, G16, Befehle())
    z_a = bt16.ziel.get(10)
    aus16 = bt16.schritt({10: einheit(71, 1, 165, 100, zustand=101)}, G16, Befehle())
    z_b = bt16.ziel.get(10)
    feuer16[3] = 30
    bt16.schritt({10: einheit(71, 1, 169, 100, zustand=106)}, G16, Befehle())
    bt16.schritt({10: einheit(71, 1, 169, 100, zustand=101)}, G16, Befehle())
    z_c = bt16.ziel.get(10)
    pruefe(16, "mitnehmen: Ziel von (100,100) %s, bei (165,100) %s (%s), nach dem Brand %s" % (
        z_a, z_b, [a[:60] for a in aus16 if "mit" in a], z_c),
        z_a == 1 and z_b == 3 and any("nimmt unterwegs mit" in a for a in aus16) and z_c == 1)

    # 17. Risiko: kein vertretbares Ziel -> Rueckzug aus dem Beschuss
    L17 = {20: einheit(74, 1, 100, 100), 700: einheit(3, 2, 110, 100)}
    for i in range(10):
        L17[960 + i] = einheit(23, 2, 112, 100 + (i % 3) - 1)
    b17 = Befehle()
    aus17 = RJ().schritt(L17, {}, b17)
    a17 = [x["angriff"] for x in b17.liste]
    end17 = (a17[0].get("danach") or [a17[0].get("lauf")])[-1] if a17 else None
    pruefe(17, "Risiko: Befehle %s, Meldung %s, Endpunkt %s" % ([{k: (v if k != "danach" else len(v)) for k, v in a.items()} for a in a17],
                                                               [a[:70] for a in aus17], end17),
           a17 and "ziel" not in a17[0] and end17 and R.schach(end17, (112, 100)) > 44)
    # 18. (22.10. 2v2 082947: Reiter auf dem Bergfried, erster Wegpunkt auf dem Lagerfeuer - 2.600 Takte Stillstand) Reiter auf
    #     dem eigenen Gebaeude 14, fremdes Gebaeude 10 als Riegel dazwischen -> kein Wegfeld und kein Wegpunkt auf Gebaeude 10;
    #     Gegenprobe ohne Gebaeude-Ebene: der Weg geht hindurch
    import numpy as np
    wk = {"gebiet": np.ones((400, 400), np.int32), "gebaeude": np.zeros((400, 400), np.int32),
          "link": np.full((400, 400), 255, np.uint8)}
    wk["gebaeude"][98:103, 98:103] = 14
    wk["gebaeude"][104:108, 85:116] = 10
    L18 = {20: einheit(74, 1, 100, 100), 700: einheit(3, 2, 130, 100)}
    mit18 = GS.Lage(L18, {}, lambda b: b not in (0, 1), {}, raten=RATEN, wegkarte=wk).plan((100, 100), (130, 100), 74, 15000)
    ohne18 = GS.Lage(L18, {}, lambda b: b not in (0, 1), {}, raten=RATEN).plan((100, 100), (130, 100), 74, 15000)
    auf10 = lambda w: sum(1 for q in w if wk["gebaeude"][q[0], q[1]] == 10)
    wp18 = GS.Lage(L18, {}, lambda b: b not in (0, 1), {}, raten=RATEN, wegkarte=wk).wegpunkte(mit18["weg"]) if mit18 else []
    pruefe(18, "Gebaeudesperre: Wegfelder auf Gebaeude 10 mit %s, ohne Ebene %s; Wegpunkte auf Gebaeuden %d" % (
        auf10(mit18["weg"]) if mit18 else None, auf10(ohne18["weg"]), sum(1 for q in wp18 if wk["gebaeude"][q[0], q[1]])),
        mit18 and auf10(mit18["weg"]) == 0 and auf10(ohne18["weg"]) > 0 and all(wk["gebaeude"][q[0], q[1]] == 0 for q in wp18))

    # 19. (22.10.: Reiter flackerte zwischen gleich fernen Holzfaellern) Anritt auf A (70 Felder); naechste Runde unterwegs taucht B
    #     2 Felder naeher auf -> kein neuer Befehl, Ziel bleibt A
    rj19 = RJ()
    b19 = Befehle()
    rj19.schritt({20: einheit(74, 1, 100, 100), 700: einheit(3, 2, 170, 100)}, {}, b19)
    n1 = len(b19.liste)
    rj19.schritt({20: einheit(74, 1, 102, 100, zustand=101), 700: einheit(3, 2, 170, 100), 701: einheit(3, 2, 168, 101)}, {}, b19)
    pruefe(19, "Anritt: Befehle Runde 1 %d, Runde 2 %d, Ziel %s" % (n1, len(b19.liste) - n1, rj19.befohlen.get(20)),
           n1 == 1 and len(b19.liste) == n1 and rj19.befohlen.get(20, (None, None))[1] == 700)
    # 20. (22.10. RAIDS FEHLER KeyError(22)) die Nummer des gejagten Arbeiters gehoert jetzt einem feindlichen Bogenschuetzen
    #     (Typ 22, weit weg) -> kein Fehler, der Reiter nimmt den anderen Arbeiter
    rj20 = RJ()
    rj20.schritt({20: einheit(74, 1, 100, 100), 700: einheit(3, 2, 170, 100)}, {}, Befehle())
    try:
        rj20.schritt({20: einheit(74, 1, 102, 100, zustand=0), 700: einheit(22, 2, 180, 180), 701: einheit(3, 2, 160, 100)}, {}, Befehle())
        fehler20 = None
    except Exception as ex:
        fehler20 = repr(ex)
    pruefe(20, "Zielnummer neu vergeben: Fehler %s, Ziel %s" % (fehler20, rj20.befohlen.get(20)),
           fehler20 is None and rj20.befohlen.get(20, (None, None))[1] == 701)
    # 21. (B-183) ein Kaempfer des Partners (Spieler 2, verbuendet) laeuft zu einem Punkt 2 Felder neben der Huette -> kein Ziel;
    #     ohne ihn ist sie Ziel
    parteien.setzen(1, {1, 2})
    G21 = {1: geb(1, 3, 130, 100)}
    L21 = {10: einheit(71, 1, 100, 100), 50: dict(einheit(26, 2, 128, 120), laufx=131, laufy=102)}
    b21 = BT()
    b21.schritt(L21, G21, Befehle())
    b21o = BT()
    b21o.schritt({10: einheit(71, 1, 100, 100)}, G21, Befehle())
    parteien.setzen(1, {1})
    pruefe(21, "Partner-Heer an der Huette: Ziel %s | ohne: %s" % (b21.ziel, b21o.ziel), 10 not in b21.ziel and b21o.ziel.get(10) == 1)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
