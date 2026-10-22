# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer feldzug.py (Daniel 18.10.2026: 30 Streitkolben je Nomade, gestackt, eins nach dem anderen).
Vorher festgelegt, was gelten muss:
  1. 10 Streitkolben am Bergfried, Lord weit weg, Schuetzen um den Lord -> Phase sammeln, Laufbefehl an den Sammelpunkt;
     der Sammelpunkt liegt mehr als 50 Felder von jedem Schuetzen und mehr als 30 von jedem feindlichen Gebaeude
  2. 30 Streitkolben am Sammelpunkt, Tick nach dem Lord-Schutz -> ANGRIFF: ein LAUF-Befehl mit allen 30 (19.10.: laufen
     an Feinden vorbei, klettern), noch kein Angriffsbefehl - der Lord ist weit weg
  3. dieselben 30 vor dem Lord-Schutz -> KEIN Angriff
  4. der Ziel-Lord ist tot -> naechstes Ziel ist der andere Lord, Phase sammeln (Ueberlebende sammeln neu)
  5. feindlicher Speer 12 Felder vor dem Sammelpunkt -> die dort stehenden Streitkolben greifen ihn an
  6. (19.10., Gefechtsrechnung statt fester 30) 8 Streitkolben am Sammelpunkt, am Lord 20 arab. Schwertkaempfer -> kein
     Angriff (die Rechnung verliert)
  7. (19.10.) im Angriff: 10 Streitkolben 3 Felder neben dem Lord -> Angriffsbefehl auf den Lord fuer genau diese 10
  8. (19.10., Daniel: "obenrum haetten die Bogenschuetzen sie erst am Ende erkannt") Wegplaner liefert einen Umweg ->
     der erste Laufbefehl geht an den ersten Wegpunkt, nicht an den Lord
  9. (Daniel 19.10.: "danach besser verteilen um auch zu raiden"; 1019f: 26 arab. Schwertkaempfer standen am Bergfried) 12
     arab. Schwertkaempfer am Sammelpunkt, der Lord mit 2 Schuetzen -> ANGRIFF (das Heer sind alle Truppen, nicht nur
     Streitkolben; die Rechnung gewinnt)
 10. dieselben 12, davon 4 in der Heimwache -> das Heer hat 8, die 4 bekommen keinen Befehl
 11. (1019h: 79 Mann 6-22 Felder vor dem Lord, Wegpunkt 14/15, am Lord 0 - beschossen, ohne anzugreifen) Angriff laeuft, die
     Spitze 20 Felder vor dem Lord, die Mitte nicht am Wegpunkt -> alle Nahkaempfer bekommen den Angriffsbefehl auf den Lord
 12. (Daniel: "arabische Bogenschuetzen sollten eher schiessen, wenn sie koennen") Schuetzen im Heer, ein feindlicher Bogen
     30 Felder vor ihnen -> sie greifen ihn an statt zu laufen
 13. (1019h: Laufbefehle jede Runde neu) zwei Runden hintereinander, niemand ist angekommen -> in der zweiten kein neuer
     Laufbefehl
Aufruf: python werkzeug/feldzug_pruefen.py   (Rueckgabe 0 = gruen)
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import feldzug as F
import parteien
parteien.setzen(1, {1})   # B-133: ohne Spiel - nur Spieler 1 ist Freund

ok = []
ende_ = lambda a: (a.get("danach") or [a["lauf"]])[-1]     # B-157: Laufziel = Ende der Wegkette (sicherster Weg ueber Wegpunkte)


def pruefe(nr, text, bed):
    ok.append(bool(bed))
    print("%s %3d %s" % ("OK  " if bed else "ROT ", nr, text))


def einheit(typ, sp, x, y, leben=10000):
    return {"typ": typ, "besitzer": sp, "x": x, "y": y, "leben": leben, "laufx": x, "laufy": y, "zustand": 1}


def lage(n_kolben, bei, lord2=True):
    L = {500: einheit(55, 2, 300, 100, 30000), 600: einheit(23, 2, 295, 105), 601: einheit(22, 2, 305, 95)}
    if lord2:
        L[700] = einheit(55, 3, 330, 330, 30000)
    for i in range(n_kolben):
        L[10 + i] = einheit(26, 1, bei[0] + i % 3, bei[1] + i // 10)
    G = {900: {"besitzer": 2, "typ": 3, "x": 290, "y": 110, "leben": 100}}
    return L, G


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, warte=1.0, bis=None):
        self.liste.append(b)
        return []


def main():
    heim = (80, 260)
    # 1 (B-140: Lord-Schutz bis 12.040 - ohne ihn gewinnt die Gefechtsrechnung schon mit 10 gegen den Lord mit 2 Schuetzen)
    f = F.Feldzug(1, heim, lord_schutz_bis=12040, n=30)
    L, G = lage(10, heim)
    b = Befehle()
    aus = f.schritt({"t": 12000}, L, G, b)
    p = f.punkt
    abst = min(F.schach(p, (e["x"], e["y"])) for e in L.values() if e["besitzer"] == 2 and e["typ"] in F.FERN) if p else -1
    lauf = [x for x in b.liste if "lauf" in x.get("angriff", {})]
    pruefe(1, "Phase %s, Sammelpunkt %s, %d Felder zum naechsten Schuetzen, Laufbefehl %s" % (f.phase, p, abst, bool(lauf)),
           f.phase == "sammeln" and p is not None and abst > 50 and F.schach(p, (290, 110)) > 30 and lauf)
    # 2
    L, G = lage(30, p)
    b = Befehle()
    f.schritt({"t": 12100}, L, G, b)
    angr = [x for x in b.liste if x.get("angriff", {}).get("ziel") == 500]
    lauf2 = [x for x in b.liste if "lauf" in x.get("angriff", {})]
    pruefe(2, "30 am Punkt nach dem Lord-Schutz: Phase %s, Laufbefehl mit %s Einheiten, Angriffsbefehle %d" % (
        f.phase, len(lauf2[-1]["angriff"]["einheiten"]) if lauf2 else 0, len(angr)),
        f.phase == "angriff" and lauf2 and len(lauf2[-1]["angriff"]["einheiten"]) == 30 and not angr)
    # 3
    f3 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f3.schritt({"t": 5000}, *lage(10, heim), Befehle())
    L, G = lage(30, f3.punkt)
    b = Befehle()
    f3.schritt({"t": 5100}, L, G, b)
    pruefe(3, "30 am Punkt vor dem Lord-Schutz: Phase %s" % f3.phase, f3.phase == "sammeln" and not [x for x in b.liste if x.get("angriff", {}).get("ziel") == 500])
    # 4
    L, G = lage(18, p)
    del L[500]
    aus = f.schritt({"t": 13000}, L, G, Befehle())
    pruefe(4, "Lord 500 tot: Ziel jetzt %s, Phase %s, Meldungen %s" % (f.ziel, f.phase, [a[:40] for a in aus][:2]),
           f.ziel == 700 and any("Ziel Lord 700" in a for a in aus))      # (B-140: die Phase entscheidet die Gefechtsrechnung)
    # 5
    f5 = F.Feldzug(1, heim, lord_schutz_bis=13000, n=30)   # B-140: unter Lord-Schutz wird gesammelt
    f5.schritt({"t": 12000}, *lage(10, heim), Befehle())
    q = f5.punkt
    L, G = lage(10, q)
    L[800] = einheit(24, 2, q[0] + 12, q[1])
    b = Befehle()
    f5.schritt({"t": 12050}, L, G, b)
    pruefe(5, "Speer 12 Felder vor dem Sammelpunkt: Angriff auf ihn %s" % [x for x in b.liste if x.get("angriff", {}).get("ziel") == 800][:1],
           any(x.get("angriff", {}).get("ziel") == 800 for x in b.liste))
    # 6
    f6 = F.Feldzug(1, heim, lord_schutz_bis=12040, n=30)   # B-140: Schritt 1 unter Lord-Schutz
    f6.schritt({"t": 12000}, *lage(10, heim), Befehle())
    L, G = lage(8, f6.punkt)
    L[500]["leben"] = 150000                # B-207 Lord-Wettlauf: echter Lord (150.000) - 8 schaffen ihn nicht vor den 20
    for i in range(20):
        L[900 + i] = einheit(75, 2, 300 + i % 5, 102 + i // 5, 28000)
    b = Befehle()
    f6.schritt({"t": 12050}, L, G, b)
    pruefe(6, "8 am Punkt, 20 arab. Schwertkaempfer am Lord: Phase %s" % f6.phase, f6.phase == "sammeln")
    # 7
    f7 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f7.schritt({"t": 12000}, *lage(10, heim), Befehle())
    f7.schritt({"t": 12050}, *lage(30, f7.punkt), Befehle())
    L, G = lage(10, (298, 98))
    b = Befehle()
    f7.schritt({"t": 12100}, L, G, b)
    angr7 = [x for x in b.liste if x.get("angriff", {}).get("ziel") == 500]
    pruefe(7, "10 Streitkolben 3 Felder neben dem Lord: Angriffsbefehl %s" % (angr7[:1],),
           angr7 and sorted(angr7[0]["angriff"]["einheiten"]) == list(range(10, 20)))
    # 8
    f8 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f8.wegplaner = lambda L_, G_, s, z: [(240, 60), (290, 80), z]
    f8.schritt({"t": 12000}, *lage(10, heim), Befehle())
    L, G = lage(30, f8.punkt)
    b = Befehle()
    f8.schritt({"t": 12050}, L, G, b)
    lauf8 = [x["angriff"]["lauf"] for x in b.liste if "lauf" in x.get("angriff", {})]
    pruefe(8, "Umweg (240,60) -> (290,80) -> Lord: Laufbefehle %s" % lauf8, lauf8 and lauf8[-1] == [240, 60])
    # 9 / 10
    def heer(heimwache):
        f9 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        f9.heimwache = set(heimwache)
        f9.schritt({"t": 12000}, *lage(10, heim), Befehle())
        L, G = lage(0, f9.punkt)
        for i in range(12):
            L[10 + i] = einheit(75, 1, f9.punkt[0] + i % 3, f9.punkt[1] + i // 3, 28000)
        b = Befehle()
        aus = f9.schritt({"t": 12050}, L, G, b)
        befohlen = {n for x in b.liste for n in x.get("angriff", {}).get("einheiten", [])}
        return f9.phase, befohlen, [a[:110] for a in aus if "ANGRIFF" in a][:1]
    ph9, bef9, m9 = heer(())
    pruefe(9, "12 arab. Schwertkaempfer am Punkt, Lord mit 2 Schuetzen: Phase %s %s" % (ph9, m9), ph9 == "angriff")
    ph10, bef10, _ = heer((10, 11, 12, 13))
    pruefe(10, "4 davon Heimwache: Befehle an %s" % sorted(bef10), not bef10 & {10, 11, 12, 13} and bef10)
    # 11
    f11 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f11.wegplaner = lambda L_, G_, s, z: [(240, 60), (290, 80), z]
    f11.schritt({"t": 12000}, *lage(10, heim), Befehle())
    f11.schritt({"t": 12050}, *lage(30, f11.punkt), Befehle())
    L, G = lage(0, heim)
    for i in range(20):
        L[10 + i] = einheit(75, 1, 300 - 20 + i % 5, 100 + i // 5, 28000)
    b = Befehle()
    f11.schritt({"t": 12100}, L, G, b)
    angr11 = [x for x in b.liste if x.get("angriff", {}).get("ziel") == 500]
    n11 = len(angr11[0]["angriff"]["einheiten"]) if angr11 else 0
    pruefe(11, "Spitze 20 Felder vor dem Lord: Angriffsbefehl auf den Lord fuer %d von 20" % n11, n11 == 20)
    # 12
    f12 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f12.schritt({"t": 12000}, *lage(10, heim), Befehle())
    f12.schritt({"t": 12050}, *lage(30, f12.punkt), Befehle())
    L, G = lage(0, heim)
    for i in range(6):
        L[40 + i] = einheit(70, 1, 200 + i, 150, 15000)
    L[777] = einheit(22, 2, 200, 180)
    b = Befehle()
    f12.schritt({"t": 12100}, L, G, b)
    schuss = [x for x in b.liste if x.get("angriff", {}).get("ziel") == 777]
    pruefe(12, "6 arab. Bogen, feindlicher Bogen 30 Felder: Angriff auf ihn %s" % (schuss[:1],),
           schuss and set(schuss[0]["angriff"]["einheiten"]) == set(range(40, 46)))
    # 13
    f13 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    L, G = lage(10, heim)
    for n in L:
        if L[n]["besitzer"] == 1:
            L[n]["zustand"] = 101
    b1 = Befehle()
    f13.schritt({"t": 12000}, L, G, b1)
    b2 = Befehle()
    f13.schritt({"t": 12050}, L, G, b2)
    lauf1 = [x for x in b1.liste if "lauf" in x.get("angriff", {})]
    lauf2 = [x for x in b2.liste if "lauf" in x.get("angriff", {})]
    pruefe(13, "Laufbefehle Runde 1: %d, Runde 2: %d" % (len(lauf1), len(lauf2)), lauf1 and not lauf2)
    # 14 (19.10., 1018l: Endspurt-Angriff 10.000 Ticks bei "Wegpunkt 2/20", Spitze immer 157 Felder vor dem Lord): im Angriff
    # bewegt sich niemand -> nach 1.500 Ticks Wegpunkt uebersprungen, nach weiteren 1.500 alle mit Angriffsbefehl auf den Lord
    f14 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f14.wegplaner = lambda L_, G_, s, z: [(150, 200), (200, 150), (250, 120), z]
    f14.schritt({"t": 12000}, *lage(10, heim), Befehle())
    f14.schritt({"t": 12050}, *lage(30, f14.punkt), Befehle())
    L14, G14 = lage(0, heim)
    for i in range(20):
        L14[10 + i] = einheit(75, 1, 100 + i % 5, 240 + i // 5, 28000)
    meld, lord14 = [], []
    for t in range(12100, 15400, 100):
        b14 = Befehle()
        meld += [m for m in f14.schritt({"t": t}, L14, G14, b14) if "STAU" in m]
        if len(meld) == 2:            # ab dem zweiten Stau: Angriffsbefehle auf den Lord (alle 5 Runden neu)
            lord14 += [x for x in b14.liste if x.get("angriff", {}).get("ziel") == 500]
    pruefe(14, "Stau: Meldungen %s; am Ende Angriff auf den Lord fuer %d" % (
        [m[:60] for m in meld], len(lord14[0]["angriff"]["einheiten"]) if lord14 else 0),
           len(meld) == 2 and "uebersprungen" in meld[0] and "direkt" in meld[1] and lord14
           and len(lord14[0]["angriff"]["einheiten"]) == 20)
    # 15 (B-139 Schwachstelle, Daniel 20.10. 20:52: "sei aggressiver, gehe aufs Torhaus oder die groesste Schwachstelle"): ein
    #    Torhaus 6 Felder vom Lord -> im ersten Angriffsschritt laufen ALLE 30 Nahkaempfer los (Weg zum Lord - ein Laufbefehl
    #    auf das Torfeld selbst blieb 21:35 wirkungslos), vor dem Tor bekommen sie den Gebaeudeangriff; faellt es -> "BRESCHE
    #    gefallen", Angriff auf den Lord.
    #    Gegenprobe: ohne Torhaus kein Gebaeudeangriff und keine SCHWACHSTELLE.
    def burg(mit_tor):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        f.schritt({"t": 12000}, *lage(10, heim), Befehle())
        L_, G_ = lage(30, f.punkt)
        if mit_tor:
            G_[901] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 1500}
        b = Befehle()
        m_ = f.schritt({"t": 12050}, L_, G_, b)
        lauf_ = [x for x in b.liste if "lauf" in x.get("angriff", {})]
        tor_ = []
        if mit_tor:                                   # angekommen: 30 stehen vor dem Tor -> Gebaeudeangriff
            for i in range(30):
                L_[10 + i]["x"], L_[10 + i]["y"] = 300 + i % 5, 112 + i // 10
            b1 = Befehle()
            f.schritt({"t": 12060}, L_, G_, b1)
            tor_ = [x for x in b1.liste if x.get("angriff", {}).get("gebaeude") == 901]
        fall_, lord_ = [], []
        if mit_tor:
            del G_[901]
            for k, t in enumerate(range(12100, 12700, 100)):
                b2 = Befehle()
                fall_ += [m for m in f.schritt({"t": t}, L_, G_, b2) if "BRESCHE" in m]
                lord_ += [x for x in b2.liste if x.get("angriff", {}).get("ziel") == 500 or "lauf" in x.get("angriff", {})]
        return m_, tor_, lauf_, fall_, lord_
    m15, tor15, lauf15, fall15, lord15 = burg(True)
    m15o, tor15o, _, _, _ = burg(False)
    pruefe(15, "Schwachstelle sofort: %s; vor dem Tor Angriff fuer %d, Laufbefehle %s; gefallen %s, danach Befehle %d | ohne Tor: %s" % (
        [m[:60] for m in m15 if "SCHWACHSTELLE" in m], len(tor15[0]["angriff"]["einheiten"]) if tor15 else 0,
        [(x["angriff"]["lauf"], len(x["angriff"]["einheiten"])) for x in lauf15],
        [m[:40] for m in fall15], len(lord15), [m[:40] for m in m15o if "SCHWACHSTELLE" in m or "ANGRIFF" in m]),
           any("SCHWACHSTELLE (Angriff)" in m for m in m15) and tor15 and len(tor15[0]["angriff"]["einheiten"]) == 30
           and [(x["angriff"]["lauf"], len(x["angriff"]["einheiten"])) for x in lauf15] == [([300, 100], 30)]
           and fall15 and lord15 and not tor15o and not any("SCHWACHSTELLE" in m for m in m15o))
    # 16 (B-137, 20.10. Revanche Tick 104.000: 77 arab. Bogen standen 154 Felder vom Lord zu Hause am Wegpunkt 9/25, nur 7
    #    Schwertkaempfer vor dem Tor): nach "alle direkt auf den Lord" laufen auch die Schuetzen auf den Lord, nicht weiter an
    #    den alten Wegpunkt. Gegenprobe: vor dem Stau laufen sie an den Wegpunkt (der Umweg aus Pruefung 8 bleibt).
    f16 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f16.wegplaner = lambda L_, G_, s, z: [(150, 200), (200, 150), (250, 120), z]
    f16.schritt({"t": 12000}, *lage(10, heim), Befehle())
    f16.schritt({"t": 12050}, *lage(30, f16.punkt), Befehle())
    L16, G16 = lage(0, heim)
    for i in range(20):
        L16[10 + i] = einheit(75, 1, 100 + i % 5, 240 + i // 5, 28000)
    for i in range(6):
        L16[40 + i] = einheit(70, 1, 70 + i, 270, 15000)
    ziele16 = {}
    for t in range(12100, 15400, 100):
        b16 = Befehle()
        f16.schritt({"t": t}, L16, G16, b16)
        for x in b16.liste:
            if "lauf" in x.get("angriff", {}) and set(x["angriff"]["einheiten"]) & set(range(40, 46)):
                ziele16[t] = ende_(x["angriff"])
        for n in range(40, 46):
            L16[n]["zustand"] = 1                   # stehen still -> jede Runde neu befehlbar
    vor16 = [z for t, z in sorted(ziele16.items()) if not f16.direkt or t < 15000][:1]
    nach16 = [z for t, z in sorted(ziele16.items())][-1:]
    pruefe(16, "Schuetzen: erster Laufbefehl %s, letzter nach 'direkt' %s (direkt=%s)" % (vor16, nach16, f16.direkt),
           f16.direkt and vor16 and vor16[0] != [300, 100] and nach16 == [[300, 100]])

    # 17 (B-139 "groesste Schwachstelle"): zwei Torhaeuser am Lord mit 1.500 und 400 Leben, dazu ein Turm mit 100 Leben 40 Felder
    #    vom Lord (ausserhalb BURG_R) -> Ziel ist das Torhaus mit 400; die 10 Nahkaempfer stehen weit weg zu Hause und laufen
    #    sofort los - mit dem Bogen zusammen den Weg zum Lord (Gebaeudeangriff und Lauf aufs Torfeld bewegten Entfernte nicht);
    #    in der naechsten Runde kein neuer Laufbefehl an Laufende (Zustand 105).
    f17 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
    f17.schritt({"t": 12000}, *lage(5, heim), Befehle())
    L17, G17 = lage(0, heim)
    for i in range(10):
        L17[10 + i] = einheit(75, 1, 100 + i % 5, 240 + i // 5, 28000)
    L17[60] = einheit(70, 1, 90, 250, 15000)
    G17[901] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 1500}
    G17[902] = {"typ": 46, "besitzer": 2, "x": 294, "y": 96, "leben": 400}
    G17[903] = {"typ": 74, "besitzer": 2, "x": 300, "y": 140, "leben": 100}
    f17.phase = "angriff"                            # (B-140: der Zeitpunkt ist Sache von Pruefung 20 - hier die Torwahl)
    b17 = Befehle()
    m17 = f17.schritt({"t": 12050}, L17, G17, b17)
    tor17 = [x for x in b17.liste if "gebaeude" in x.get("angriff", {})]
    lauf17 = [x for x in b17.liste if "lauf" in x.get("angriff", {})]
    nk17 = [x for x in lauf17 if set(x["angriff"]["einheiten"]) & set(range(10, 20))]
    bogen17 = [ende_(x["angriff"]) for x in lauf17 if 60 in x["angriff"]["einheiten"]]
    for i in range(10):
        L17[10 + i]["zustand"] = 105                 # 21:31 gemessen: so sehen sie nach dem Laufbefehl aus
    b17b = Befehle()
    f17.schritt({"t": 12150}, L17, G17, b17b)
    nochmal17 = [x for x in b17b.liste if "lauf" in x.get("angriff", {}) and set(x["angriff"]["einheiten"]) & set(range(10, 20))]
    pruefe(17, "Schwaechste Stelle: Ziel %s, Torangriffe %d, Laufbefehle an Nahkaempfer %s (naechste Runde nochmal: %d), Bogen laeuft nach %s" % (
        f17.bresche, len(tor17), [(ende_(x["angriff"]), len(x["angriff"]["einheiten"])) for x in nk17], len(nochmal17), bogen17),
           f17.bresche == 902 and not tor17 and [(ende_(x["angriff"]), len(x["angriff"]["einheiten"])) for x in nk17] == [([300, 100], 11)]
           and bogen17 == [[300, 100]] and not nochmal17)
    # 18 (B-138): ein Stau, waehrend die gewaehlte Bresche noch steht, waehlt kein anderes Tor - auch wenn eines schwaecher ist.
    #    Gegenprobe: ist die Bresche gefallen und kommt danach niemand weiter, waehlt schon der erste Stau danach das andere
    #    Tor (vorher keine Stau-Stufe wie Wegpunkt ueberspringen oder 'direkt').
    f18 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=20)
    f18.schritt({"t": 12000}, *lage(10, heim), Befehle())
    L18, G18 = lage(0, heim)
    G18[901] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 1000}
    for i in range(20):
        L18[10 + i] = einheit(75, 1, 280 + i % 3, 120 + i // 10, 28000)
    f18.schritt({"t": 12050}, L18, G18, Befehle())          # Angriff, Ziel 901
    G18[902] = {"typ": 46, "besitzer": 2, "x": 301, "y": 101, "leben": 50}      # neues, schwaecheres Tor
    m18 = []
    for t in range(12100, 12100 + F.Feldzug.STAU_TICKS + 200, 100):
        G18[901]["leben"] -= 1                       # sinkt langsam - nicht "zaeh"
        m18 += f18.schritt({"t": t}, L18, G18, Befehle())
    bleibt = f18.bresche == 901
    del G18[901]
    m18b = []
    for t in range(13900, 13900 + F.Feldzug.STAU_TICKS + 300, 100):
        m18b += f18.schritt({"t": t}, L18, G18, Befehle())
    pruefe(18, "Stau bei stehender Bresche: Ziel bleibt 901 %s; nach dem Fall: %s, Ziel %s" % (
        bleibt, [m[:55] for m in m18b if "SCHWACHSTELLE" in m or "BRESCHE" in m], f18.bresche),
           bleibt and not any("SCHWACHSTELLE" in m for m in m18) and f18.bresche == 902
           and any("SCHWACHSTELLE (Stau" in m for m in m18b)
           and not any("STAU" in m for m in m18b[:next(i for i, m in enumerate(m18b) if "SCHWACHSTELLE" in m)]))
    # 19 (B-138, 20.10. gegen Franz: Zugbruecke 420 blieb trotz Sturm bei 100 Leben): 20 Nahkaempfer stehen am Tor, sein Leben
    #    sinkt BRESCHE_ZAEH Ticks lang nicht -> "ZAEH", verworfen, sofort die naechste Schwachstelle.
    #    Gegenprobe: sinkt das Leben zwischendurch, wird nichts verworfen.
    #    (B-165, 21.10. 22:15: seit dem Wirkungswaechter reicht "alle 1.000 Takte 5 Leben" nicht mehr als Fortschritt - nach
    #    WIRKUNG_TAKTE ohne Schaden kommt "KEINE WIRKUNG"; die Gegenprobe senkt das Leben darum alle 200 Takte, und ohne Schaden
    #    laeuft die Pruefung nur WIRKUNG_TAKTE + 200 Takte - danach waere auch 901 ohne Wirkung verworfen, richtig so)
    def zaeh(sinkt):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=20)
        f.schritt({"t": 12000}, *lage(10, heim), Befehle())
        L_, G_ = lage(0, heim)
        G_[900] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 100}
        G_[901] = {"typ": 46, "besitzer": 2, "x": 301, "y": 110, "leben": 1500}
        for i in range(20):
            L_[10 + i] = einheit(75, 1, 300 + i % 3, 108 + i // 10, 28000)
        m_ = []
        dauer = F.Feldzug.BRESCHE_ZAEH + 300 if sinkt else F.Feldzug.WIRKUNG_TAKTE + 200
        for k, t in enumerate(range(12050, 12050 + dauer, 100)):
            if sinkt and k % 2 == 1:
                G_[900]["leben"] -= 5
            f._stau = (0, t)                          # kein Stau in dieser Pruefung
            m_ += f.schritt({"t": t}, L_, G_, Befehle())
        return m_, f
    m19, f19 = zaeh(False)
    m19g, f19g = zaeh(True)
    pruefe(19, "Zaehe Bresche: %s, danach Ziel %s | Leben sinkt: verworfen %s, Ziel %s" % (
        [m[:50] for m in m19 if "ZAEH" in m or "KEINE WIRKUNG" in m], f19.bresche, sorted(f19g.verworfen), f19g.bresche),
        any("ZAEH" in m or "KEINE WIRKUNG" in m for m in m19) and f19.verworfen == {900} and f19.bresche == 901
        and not f19g.verworfen and f19g.bresche == 900)
    # 20 (B-139/B-140): 30 arab. Schwertkaempfer irgendwo (nicht am Sammelpunkt), der Lord mit 2 Schuetzen, Lord-Schutz vorbei
    #    -> die Gefechtsrechnung mit dem ganzen Heer gewinnt -> sofort ANGRIFF (kein Rueckweg zum Sammelpunkt).
    #    Gegenprobe (B-140, Pruefstand T40126: 30 gegen Franz' 86): dieselben 30, am Lord stehen 80 arab. Schwertkaempfer -> sammeln.
    # B-207 (Daniel 22.10. 18:58 "du musst ja nur den Lord killen"): Lord-Wettlauf statt Schlacht gegen alle - Gegenprobe
    # jetzt: nur 6 eigene gegen den echten Lord (150.000) und 80 Verteidiger -> sammeln
    def neustart(verteidiger, eigene=30):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        L_, G_ = lage(0, heim)
        L_[500]["leben"] = 150000
        for i in range(eigene):
            L_[10 + i] = einheit(75, 1, 250 + i % 5, 160 + i // 5, 28000)
        for i in range(verteidiger):
            L_[1000 + i] = einheit(75, 2, 296 + i % 9, 96 + i // 9, 28000)
        m_ = f.schritt({"t": 12000}, L_, G_, Befehle())
        return f.phase, [m[:50] for m in m_ if "ANGRIFF" in m]
    ph20, m20 = neustart(0)
    ph20g, _ = neustart(80, eigene=6)
    pruefe(20, "30 verstreut gegen Lord + 2 Schuetzen: Phase %s %s | 6 gegen Lord + 80: %s" % (ph20, m20, ph20g),
           ph20 == "angriff" and ph20g == "sammeln")
    # 21 (B-139, 20.10. gegen Franz: 72.000 Takte Stillstand, Ziel 1.500 Leben, Truppen 150+ Felder weg): Stau, die Bresche steht,
    #    weniger als TOR_MIN Nahkaempfer davor -> "UNERREICHBAR", verworfen, naechste Schwachstelle.
    #    Gegenprobe: 20 stehen davor und ihr Leben sinkt -> die Bresche bleibt.
    def unerreichbar(davor):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=20)
        f.schritt({"t": 12000}, *lage(10, heim), Befehle())
        L_, G_ = lage(0, heim)
        G_[901] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 1500}
        G_[902] = {"typ": 75, "besitzer": 2, "x": 290, "y": 95, "leben": 1500}
        for i in range(20):
            x_, y_ = (300 + i % 3, 108 + i // 10) if davor else (100 + i % 5, 240 + i // 5)
            L_[10 + i] = einheit(75, 1, x_, y_, 28000)
        f.phase = "angriff"                          # (B-140: der Zeitpunkt ist Sache von Pruefung 20)
        f.schritt({"t": 12050}, L_, G_, Befehle())
        erst = f.bresche
        m_ = []
        for t in range(12100, 12100 + F.Feldzug.STAU_TICKS + 300, 100):
            if davor:
                G_[erst]["leben"] -= 1
            m_ += f.schritt({"t": t}, L_, G_, Befehle())
        return erst, f.bresche, sorted(f.verworfen), [m[:60] for m in m_ if "UNERREICHBAR" in m or "SCHWACHSTELLE" in m]
    e21, z21, v21, m21 = unerreichbar(False)
    e21g, z21g, v21g, _ = unerreichbar(True)
    pruefe(21, "Niemand kommt hin: erst %s, dann %s, verworfen %s %s | 20 davor: %s bleibt %s, verworfen %s" % (
        e21, z21, v21, m21, e21g, z21g, v21g),
           v21 == [e21] and z21 not in (None, e21) and any("UNERREICHBAR" in m for m in m21) and z21g == e21g and not v21g)
    # 22 (B-139, 21:39 mit dem Wegtest des Spiels gemessen: Turm 596 nur von Sueden erreichbar, Laufbefehle aufs Turmfeld liessen
    #    die Einheiten untaetig): Wegtest meldet nur Punkte suedlich der Bresche erreichbar -> Vorposten = 4 Felder suedlich,
    #    alle 10 Nahkaempfer (weit weg) laufen dorthin, der Bogen auch; in der naechsten Runde (laufend, Zustand 105) kein neuer
    #    Befehl; am Vorposten (4 Felder vom Tor) -> Gebaeudeangriff. Gegenprobe: Wegtest findet nichts -> Weg zum Lord (300,100).
    def vorposten(findet):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
        f.wegtest = lambda nr, punkte: [findet and q[1] > 106 for q in punkte]
        f.schritt({"t": 12000}, *lage(5, heim), Befehle())
        L_, G_ = lage(0, heim)
        for i in range(10):
            L_[10 + i] = einheit(75, 1, 100 + i % 5, 240 + i // 5, 28000)
        L_[60] = einheit(70, 1, 90, 250, 15000)
        G_[901] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 1500}
        f.phase = "angriff"                          # (B-140: der Zeitpunkt ist Sache von Pruefung 20)
        b = Befehle()
        m_ = f.schritt({"t": 12050}, L_, G_, b)
        lauf_ = [(ende_(x["angriff"]), len(x["angriff"]["einheiten"])) for x in b.liste if "lauf" in x.get("angriff", {})]
        for i in range(10):
            L_[10 + i]["zustand"] = 105
        b2 = Befehle()
        f.schritt({"t": 12100}, L_, G_, b2)
        nochmal = [x for x in b2.liste if "lauf" in x.get("angriff", {}) and set(x["angriff"]["einheiten"]) & set(range(10, 20))]
        bogen2 = [ende_(x["angriff"]) for x in b2.liste if "lauf" in x.get("angriff", {}) and 60 in x["angriff"]["einheiten"]]
        vp = f.vorposten[1] if f.vorposten else None
        for i in range(10):
            L_[10 + i]["x"], L_[10 + i]["y"], L_[10 + i]["zustand"] = 306, 110, 1
        b3 = Befehle()
        f.schritt({"t": 12200}, L_, G_, b3)
        tor_ = [len(x["angriff"]["einheiten"]) for x in b3.liste if x.get("angriff", {}).get("gebaeude") == 901]
        mauer_ = [len(x["angriff"]["einheiten"]) for x in b.liste if "mauer" in x.get("angriff", {})]
        return [m[:60] for m in m_ if "VORPOSTEN" in m or "SCHWACHSTELLE" in m], lauf_, len(nochmal), tor_, vp, bogen2, mauer_
    m22, l22, n22, t22, vp22, bg22, w22 = vorposten(True)
    m22g, l22g, _, _, vp22g, _, w22g = vorposten(False)
    # (B-147, Daniel 21.10. 00:47 "Mauer einreissen": ohne Treffer ist auch der Lord eingemauert - die 10 arab. Schwertkaempfer
    #  hacken die Mauer auf statt zum Lord zu laufen; der Bogenschuetze laeuft wie bisher. Vorher: alle 11 zum Lord.)
    pruefe(22, "Vorposten %s: %s, Laufbefehle %s, naechste Runde %d, Bogen dann %s, am Tor Angriff %s, Mauer %s | ohne Treffer: %s %s "
           "Mauer %s" % (vp22, m22, l22, n22, bg22, t22, w22, m22g, l22g, w22g),
           vp22 and F.schach(vp22, (306, 106)) == 4 and vp22[1] > 106 and ([list(vp22), 10] in [list(x) for x in l22])
           and n22 == 0 and bg22 == [list(vp22)] and t22 == [10] and w22 == []
           and vp22g is None and l22g == [([300, 100], 1)] and w22g == [10])     # (B-140: ohne erreichbares Nachbarfeld kein Ziel)
    # 23 (B-139, Daniel 21:44, Bild: nach dem ersten zerstoerten Turm standen alle vor der Burg und wurden abgeschossen): zwei
    #    Tore, das erste faellt, der Wegtest findet am Lord (Ringe 1-3) nichts -> "eingemauert" und SOFORT die naechste
    #    Schwachstelle (kein Stau abwarten). Gegenprobe: Lord erreichbar (Feld 2 suedlich) -> alle Nahkaempfer laufen dorthin,
    #    keine neue Schwachstelle; dort angekommen -> Angriffsbefehl auf den Lord.
    def lord_frei(erreichbar):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
        lp_ = (300, 100)
        def wt(nr, punkte):
            return [(q[1] > 106 and abs(q[0] - 306) <= 4) or (q[1] > 96 and abs(q[0] - 290) <= 3 and q[1] <= 99)
                    or (erreichbar and q == (lp_[0], lp_[1] + 2)) for q in punkte]
        f.wegtest = wt
        f.schritt({"t": 12000}, *lage(5, heim), Befehle())
        L_, G_ = lage(0, heim)
        for i in range(10):
            L_[10 + i] = einheit(75, 1, 304 + i % 3, 110 + i // 5, 28000)
        G_[901] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 1500}
        G_[902] = {"typ": 46, "besitzer": 2, "x": 290, "y": 96, "leben": 1500}
        f.schritt({"t": 12050}, L_, G_, Befehle())          # Ziel 901 (naeher an der Spitze)
        erst = f.bresche
        del G_[erst]
        for i in range(10):                            # die Truppen sind (zurueck)gewichen - weit weg vom Lord
            L_[10 + i]["x"], L_[10 + i]["y"] = 250 + i % 3, 160 + i // 5
        b = Befehle()
        m_ = f.schritt({"t": 12100}, L_, G_, b)
        lauf_ = [(ende_(x["angriff"]), len(x["angriff"]["einheiten"])) for x in b.liste if "lauf" in x.get("angriff", {})]
        for i in range(10):
            L_[10 + i]["x"], L_[10 + i]["y"], L_[10 + i]["zustand"] = 300 + i % 3, 102 + i // 5, 1
        # Die Zwischenposition zwei Felder daneben ist noch keine Ankunft.
        # Neu: erst einzeln zum gemeinsamen Lord-Feld, dann angreifen.
        for i in range(10):
            L_[10+i]['x'],L_[10+i]['y']=300,100
        lord_ = []
        for k in range(6):                             # Angriffsbefehle hoechstens alle WIEDERHOLEN Runden
            b2 = Befehle()
            f.schritt({"t": 12200 + 50 * k}, L_, G_, b2)
            lord_ += [len(x["angriff"]["einheiten"]) for x in b2.liste if x.get("angriff", {}).get("ziel") == 500]
        return erst, f.bresche, [m[:70] for m in m_ if "LORD" in m or "SCHWACHSTELLE" in m], lauf_, lord_
    e23, z23, m23, l23, _ = lord_frei(False)
    e23g, z23g, m23g, l23g, lord23g = lord_frei(True)
    pruefe(23, "Lord eingemauert: erst %s, dann %s %s | Lord erreichbar: Ziel %s %s, Laufbefehle %s, dort Angriff %s" % (
        e23, z23, m23, z23g, m23g, l23g, lord23g),
           e23 == 901 and z23 == 902 and any("eingemauert" in m for m in m23) and any("SCHWACHSTELLE (Lord eingemauert)" in m for m in m23)
           and z23g is None and any("erreichbar bei (300, 102)" in m for m in m23g) and ([300, 102], 10) in [tuple(x) for x in l23g]
           and lord23g and all(x == 10 for x in lord23g))   # (B-140: Lord-Befehle alle WIEDERHOLEN Runden, in 6 Runden auch zwei)
    # 24 (B-140, Daniel 21:47 "die beste Position auswaehlen"): zwei Torhaeuser am Lord - eines mit 400 Leben im Schussfeld
    #    beider Feindschuetzen, eines mit 1.500 Leben ausserhalb jeder Reichweite -> Ziel ist das ungedeckte (wenigster Beschuss
    #    vor wenigsten Leben). Gegenprobe: liegen beide im Schussfeld, gewinnt wieder das mit weniger Leben.
    def seite(beide_gedeckt):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
        f.schritt({"t": 12000}, *lage(5, heim), Befehle())
        L_, G_ = lage(0, heim)
        for i in range(10):
            L_[10 + i] = einheit(75, 1, 280 + i % 3, 130 + i // 5, 28000)
        L_[600]["x"], L_[600]["y"] = 300, 92            # Armbrust nordwestlich, Bogen nordoestlich des Lords
        L_[601]["x"], L_[601]["y"] = 304, 90
        G_[901] = {"typ": 46, "besitzer": 2, "x": 298, "y": 96, "leben": 400}
        G_[902] = {"typ": 46, "besitzer": 2, "x": 300, "y": 126 if not beide_gedeckt else 110, "leben": 1500}
        if not beide_gedeckt:
            for n in (600, 601):
                L_[n]["y"] = 60                         # Schuetzen weit noerdlich: 902 (y 126) ausser Reichweite
        m_ = f.schritt({"t": 12050}, L_, G_, Befehle())
        return f.bresche, [m[:90] for m in m_ if "SCHWACHSTELLE" in m]
    z24, m24 = seite(False)
    z24g, m24g = seite(True)
    pruefe(24, "Angriffsstelle: %s %s | beide gedeckt: %s" % (z24, m24, z24g), z24 == 902 and z24g == 901)
    # 25 (B-140, Daniel 22:07 "schlau angestellt werden vielleicht nur 20-30 % der gegnerischen Einheiten ueberhaupt genutzt"):
    #    80 arab. Schwertkaempfer stehen 40 Felder noerdlich des Lords, das Torhaus liegt 20 Felder suedlich -> an der
    #    Angriffsstelle kaempft keiner von ihnen mit, 30 eigene greifen an. Gegenprobe: die 80 stehen am Torhaus -> sammeln.
    def stelle(am_tor, eigene=30):           # B-207: Gegenprobe mit 6 eigenen gegen den echten Lord
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        L_, G_ = lage(0, heim)
        L_[500]["leben"] = 150000
        for i in range(eigene):
            L_[10 + i] = einheit(75, 1, 250 + i % 5, 160 + i // 5, 28000)
        for i in range(80):
            L_[1000 + i] = einheit(75, 2, 296 + i % 9, (116 if am_tor else 56) + i // 9, 28000)
        G_[901] = {"typ": 46, "besitzer": 2, "x": 300, "y": 120, "leben": 1500}
        m_ = f.schritt({"t": 12000}, L_, G_, Befehle())
        return f.phase, [m[:60] for m in m_ if "ANGRIFF" in m]
    ph25, m25 = stelle(False)
    ph25g, _ = stelle(True, eigene=6)
    pruefe(25, "80 Verteidiger 40 Felder hinter dem Lord, Tor vorn: Phase %s %s | 6 eigene, 80 am Tor: %s" % (ph25, m25, ph25g),
           ph25 == "angriff" and ph25g == "sammeln")
    # 26 (B-140, Daniel 22:27 "sofort erkennen, wenn jemand einen Burggraben setzt - dann ... einen anderen Weg"): Bresche 901
    #    gewaehlt, dann meldet der Wegfinder kein Feld bis 3 daneben mehr (Graben) -> in der NAECHSTEN Runde
    #    "ABGESCHNITTEN", 901 verworfen, Ziel 902. Zweiter Fall: nur der Vorposten wird abgeschnitten -> Bresche bleibt, neuer
    #    Vorposten. Gegenprobe: nichts aendert sich -> 901 bleibt, Vorposten bleibt, keine Meldung.
    def graben(was):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
        zu = set()
        f.wegtest = lambda nr, punkte: [q not in zu for q in punkte]
        f.schritt({"t": 12000}, *lage(5, heim), Befehle())
        L_, G_ = lage(0, heim)
        for i in range(10):
            L_[10 + i] = einheit(75, 1, 304 + i % 3, 120 + i // 5, 28000)
        G_[901] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 1500}
        G_[902] = {"typ": 46, "besitzer": 2, "x": 290, "y": 96, "leben": 1500}
        f.phase = "angriff"
        f.schritt({"t": 12050}, L_, G_, Befehle())
        erst, vp_erst = f.bresche, (f.vorposten[1] if f.vorposten else None)
        if was == "graben":
            zu.update(f._nachbar_punkte(G_, erst))
        elif was == "vorposten" and vp_erst:
            zu.add(tuple(vp_erst))
        m_ = []
        m_ += f.schritt({"t": 12100}, L_, G_, Befehle())
        return erst, f.bresche, sorted(f.verworfen), vp_erst, (f.vorposten[1] if f.vorposten else None), \
            [m[:70] for m in m_ if "ABGESCHNITTEN" in m]
    e26, z26, v26, _, _, m26 = graben("graben")
    e26v, z26v, v26v, vp26v, vpn26v, m26v = graben("vorposten")
    e26g, z26g, v26g, vp26g, vpn26g, m26g = graben("nichts")
    pruefe(26, "Graben: %s -> %s, verworfen %s %s | Vorposten zu: %s bleibt %s, Vorposten %s -> %s %s | nichts: %s bleibt %s, %s, %s" % (
        e26, z26, v26, m26, e26v, z26v, vp26v, vpn26v, m26v, e26g, z26g, m26g, vpn26g),
           e26 == 901 and z26 == 902 and v26 == [901] and any("BRESCHE ABGESCHNITTEN" in m for m in m26)
           and z26v == 901 and vp26v and vpn26v and tuple(vpn26v) != tuple(vp26v) and any("VORPOSTEN ABGESCHNITTEN" in m for m in m26v)
           and not v26v and z26g == 901 and not v26g and not m26g and vpn26g == vp26g)
    # 27 (B-146, Daniel 21.10. 00:34 Rueckzugsregel; L170/L171): 10 Streitkolben stehen ueber RUECKZUG_TAKTE auf demselben Feld
    #    vor Tor 901, verlieren Leben, ohne Ziel und ohne Nahkampfgegner -> "FELDZUG RUECKZUG", 901 verworfen, Laufbefehl zum
    #    Sammelpunkt. Gegenprobe: dieselben, aber im Nahkampf (nahziel > 0) -> kein Rueckzug.
    def rueckzug(nahkampf):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
        f.wegtest = lambda nr, punkte: [True for q in punkte]
        f.schritt({"t": 12000}, *lage(5, heim), Befehle())
        L_, G_ = lage(0, heim)
        for i in range(10):
            L_[10 + i] = einheit(26, 1, 304 + i % 3, 112 + i // 5, 28000)
            L_[10 + i]["nahziel"] = 600 if nahkampf else 0
        G_[901] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 1500}
        G_[902] = {"typ": 46, "besitzer": 2, "x": 290, "y": 96, "leben": 1500}
        f.phase = "angriff"
        f.schritt({"t": 12050}, L_, G_, Befehle())
        erst = f.bresche
        m_, b_ = [], Befehle()
        for k, t_ in enumerate((12400, 12800)):
            for i in range(10):
                L_[10 + i]["leben"] -= 500
            b_ = Befehle()
            m_ += f.schritt({"t": t_}, L_, G_, b_)
        zur = [x["angriff"]["lauf"] for x in b_.liste if "lauf" in x.get("angriff", {}) and len(x["angriff"]["einheiten"]) == 10]
        return erst, sorted(f.verworfen), [m[:60] for m in m_ if "RUECKZUG" in m], zur
    e27, v27, m27, z27 = rueckzug(False)
    e27g, v27g, m27g, z27g = rueckzug(True)
    pruefe(27, "steht nur: Tor %s verworfen %s %s Laufbefehl %s | im Nahkampf: verworfen %s %s" % (e27, v27, m27, z27, v27g, m27g),
           e27 is not None and e27 in v27 and m27 and z27 and not m27g)
    # 28 (B-146, L171): Vorposten - zwei erreichbare Punkte im selben Ring vor Turm 901, einer im Schussfeld von 25 Schuetzen,
    #    der andere von keinem -> der ohne Schuetzen; Gegenprobe ohne Schuetzen: der naechste an der Heeresmitte (wie vorher).
    #    Dazu der Fehler des ersten Pruefstand-Laufs (21.10. 00:37): die einzige Angriffsstelle mit 25 Schuetzen muss trotzdem
    #    gewaehlt werden - sonst steht das Heer ohne Ziel.
    def vorposten(n_schuetzen):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
        f.wegtest = lambda nr, punkte: [q in ((300, 110), (300, 102)) for q in punkte]
        L_, G_ = lage(0, heim)
        L_[10] = einheit(26, 1, 300, 140, 28000)
        for i in range(n_schuetzen):
            L_[800 + i] = einheit(22, 2, 300 + i % 5, 150 + i // 5)   # (300,110) in Reichweite 44, (300,102) nicht
        return f._vorposten(L_, (300, 106), [10], (300, 140))
    def einzige_stelle():
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
        L_, G_ = lage(0, heim)
        for i in range(25):
            L_[800 + i] = einheit(22, 2, 300 + i % 5, 100 + i // 5)
        G_[901] = {"typ": 46, "besitzer": 2, "x": 300, "y": 106, "leben": 1500}
        f._lagebild = L_
        return f._beste_stelle(G_, (300, 100), [(280, 130)])
    v28, v28g, b28 = vorposten(25), vorposten(0), einzige_stelle()
    pruefe(28, "Vorposten mit 25 Schuetzen im Sueden: %s | ohne Schuetzen: %s | einzige Stelle im Kreuzfeuer: %s" % (v28, v28g, b28),
           v28 == (300, 102) and v28g == (300, 110) and b28 is not None and b28[3] == 901)
    # 29 (B-147, Daniel 21.10. 00:47 "Mauer einreissen"; L172): Lord 500 (Spieler 2) bei (300,100) eingemauert (Wegtest
    #    ueberall nein), kein Turm -> die 8 Streitkolben bekommen den Mauerbefehl [300, 100, 2, MAUER_R], die 2 Bogenschuetzen
    #    nicht. Gegenprobe: Lord bei (300,102) erreichbar -> kein Mauerbefehl.
    def mauer(erreichbar):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
        f.wegtest = lambda nr, punkte: [erreichbar and q == (300, 102) for q in punkte]
        f.schritt({"t": 12000}, *lage(5, heim), Befehle())
        L_, G_ = lage(0, heim)
        for i in range(10):
            L_[10 + i] = einheit(26 if i < 8 else 22, 1, 300 + i % 3, 125 + i // 5, 28000)
        f.phase = "angriff"
        b_ = Befehle()
        m_ = f.schritt({"t": 12050}, L_, G_, b_)
        return ([(x["angriff"]["mauer"], sorted(x["angriff"]["einheiten"])) for x in b_.liste if "mauer" in x.get("angriff", {})],
                [m[:40] for m in m_ if "MAUER" in m])
    w29, m29 = mauer(False)
    w29g, m29g = mauer(True)
    pruefe(29, "eingemauert: %s %s | erreichbar: %s %s" % (w29, m29, w29g, m29g),
           w29 == [([300, 100, 2, F.Feldzug.MAUER_R], list(range(10, 18)))] and m29 and not w29g and not m29g)
    # 30 (B-147, L175: im Pruefstand zog die Rueckzugsregel die Mauerhacker 4-mal ab - wer hackt, hat zielart 0 und kein Nahziel):
    #    Lord eingemauert, kein Turm, 10 Streitkolben mit Mauerauftrag stehen > RUECKZUG_TAKTE an der Mauer und verlieren Leben,
    #    Zustand 107 (beschaeftigt) -> kein Rueckzug. Gegenprobe: dieselben untaetig (Zustand 1) -> Rueckzug.
    def hacker(zustand):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
        f.wegtest = lambda nr, punkte: [False for q in punkte]
        f.schritt({"t": 12000}, *lage(5, heim), Befehle())
        L_, G_ = lage(0, heim)
        for i in range(10):
            L_[10 + i] = einheit(26, 1, 300 + i % 3, 108 + i // 5, 28000)
        f.phase = "angriff"
        f.schritt({"t": 12050}, L_, G_, Befehle())          # Mauerauftrag
        m_ = []
        for t_ in (12400, 12800, 13200):
            for i in range(10):
                L_[10 + i]["leben"] -= 500
                L_[10 + i]["zustand"] = zustand
            m_ += f.schritt({"t": t_}, L_, G_, Befehle())
        return [m[:40] for m in m_ if "RUECKZUG" in m], [m[:30] for m in m_ if "MAUER" in m]
    r30, w30 = hacker(107)
    r30g, w30g = hacker(1)
    pruefe(30, "hacken (Zustand 107): Rueckzug %s, Mauer %s | untaetig (1): Rueckzug %s" % (r30, w30, r30g), not r30 and r30g)
    # 31 (B-150, Daniel 19:29 "Feldzug soll Feuer meiden"): Plantage brennt bei (201,99), Laufbefehl von (201,125) nach
    #    (201,75) quer hindurch -> feuerfreier_weg legt einen Umweg, der mehr als 4 Felder am Feuer vorbeifuehrt; Gegenprobe:
    #    ohne Feuer -> geradeaus. Dazu im Feldzug: ein Laufbefehl wird durch den Umweg ersetzt (Meldung FEUER MEIDEN), die
    #    Punkte danach gehen als "danach" mit (logik.lua schickt die Truppe ohne Pause weiter - Daniel 20:23).
    orte31 = F.feuerorte({19: {"x": 201, "y": 99, "feuer": 50}}, [(201, 98), (203, 102)])
    w31 = F.feuerfreier_weg((201, 125), (201, 75), orte31)
    w31g = F.feuerfreier_weg((201, 125), (201, 75), [])
    kette31 = [(201, 125)] + list(w31)
    frei31 = len(w31) >= 2 and w31[-1] == (201, 75) and all(F._frei(a, b, orte31) for a, b in zip(kette31, kette31[1:]))
    f31 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
    L31, G31 = lage(0, heim)
    for i in range(10):
        L31[10 + i] = einheit(26, 1, 201 + i % 3, 125 + i // 5, 28000)
    L31[500]["x"], L31[500]["y"] = 201, 70          # Franz' Lord noerdlich - der Marsch fuehrt quer durch die Plantage
    G31[19] = {"typ": 32, "besitzer": 2, "x": 201, "y": 99, "leben": 80, "feuer": 50}
    b31 = Befehle()
    m31 = []
    f31.phase = "angriff"
    for t_ in (12000, 12050):
        m31 += f31.schritt({"t": t_, "bodenfeuer": [(201, 98)]}, L31, G31, b31)
    laeufe31 = [x["angriff"]["lauf"] for x in b31.liste if "lauf" in x.get("angriff", {})]
    nah31 = [l for l in laeufe31 if max(abs(l[0] - 201), abs(l[1] - 99)) <= 4]
    pruefe(31, "Umweg %s (frei %s) | ohne Feuer %s | Feldzug: %d Laufbefehle, davon im Feuer %s, Meldungen %s" % (
        w31, frei31, w31g, len(laeufe31), nah31, [m[:50] for m in m31 if "FEUER" in m][:2]),
        frei31 and w31g == [(201, 75)] and laeufe31 and not nah31 and any("FEUER MEIDEN" in m or "SICHERER WEG" in m for m in m31)
        and any((x["angriff"].get("danach") or [[0, 0]])[-1] == [201, 70] for x in b31.liste if "lauf" in x.get("angriff", {})))
    # 32 (B-150, Daniel 19:45): Brandtrupp zuendet nichts auf dem eigenen Heerweg an, wenn es bei Ankunft des Heeres noch
    #    brennt. Heer bei (201,125) -> Lord (201,70): Plantage 19 (Leben 100) bei (201,99) liegt am Weg, 26 Felder entfernt
    #    (Ankunft ~312 Takte, Feuer aus ~1.100) -> nein; dieselbe Plantage 60 Felder seitlich -> ja; Gegenprobe ohne Heerweg -> ja.
    import raids as RA
    g32 = {"typ": 32, "besitzer": 2, "x": 201, "y": 99, "leben": 100}
    a32 = RA.brennt_noch_bei_ankunft(g32, [((201, 125), (201, 70))])
    b32 = RA.brennt_noch_bei_ankunft(dict(g32, x=261), [((201, 125), (201, 70))])
    c32 = RA.brennt_noch_bei_ankunft(g32, [])
    weit32 = RA.brennt_noch_bei_ankunft(dict(g32, leben=10), [((201, 400), (201, 70))])
    pruefe(32, "am Weg: brennt noch %s | seitlich: %s | ohne Heerweg: %s | weit weg + fast abgebrannt: %s" % (a32, b32, c32, weit32),
           a32 and not b32 and not c32 and not weit32)
    # 33 (B-150): ein Ziel im Feuer wird auf den naechsten Punkt verschoben, der in KEINEM Feuer liegt. Zwei Feuer (100,100)
    #    und (100,106), Ziel (100,102) dazwischen, Start (100,80): das alte Verschieben schob es aus dem ersten Feuer mitten
    #    ins zweite und von dort zurueck ins erste (100,100). Der neue Punkt liegt hoechstens 8 Felder vom Ziel (der naechste
    #    freie ist 5 weg) - nicht etwa am Start (Sabotage 21.10.: ohne Verschieben blieb man am Start stehen, und die
    #    Pruefung war trotzdem gruen). Gegenprobe: ein freies Ziel bleibt, wie es ist.
    orte33 = [(100, 100, 4), (100, 106, 4)]
    w33 = F.feuerfreier_weg((100, 80), (100, 102), orte33)
    g33 = F.feuerfreier_weg((100, 80), (100, 120), orte33)
    pruefe(33, "Ziel zwischen zwei Feuern -> %s (im Feuer: %s) | freies Ziel (100,120) -> %s" % (
        w33, F.im_feuer(w33[-1], orte33), g33), not F.im_feuer(w33[-1], orte33) and F.schach(w33[-1], (100, 102)) <= 8
        and g33[-1] == (100, 120))
    # 34 (B-150, Pruefstand 21.10. 19:50: Sklave 208 zuendete Gebaeude 291 bei (130,155) an, waehrend das Heer zum Vorposten
    #    (128,151) befohlen war - die Linie Heer -> Lord (151,218)->(173,114) lag 30 Felder daneben): mit den Heerwegen des
    #    Feldzugs (wer steht, wohin er befohlen ist) gilt 291 als "brennt noch bei Ankunft"; Gegenprobe nur mit der Linie zum
    #    Lord -> nicht. Dazu im Brandtrupp: ein schon vergebenes Ziel, an dem jetzt das Heer steht, wird fallen gelassen und
    #    der Sklave angehalten.
    g34 = {"typ": 5, "besitzer": 2, "x": 130, "y": 155, "leben": 300}
    f34 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
    L34 = {500: einheit(55, 2, 173, 114, 30000)}
    for i in range(10):
        L34[10 + i] = einheit(26, 1, 132 + i % 3, 153 + i // 5)
    f34._befohlen = {10 + i: ("vorposten", (128, 151)) for i in range(10)}
    f34.heerweg = ((151, 218), (173, 114), 45000)
    wege34 = f34._heerwege(L34)
    a34 = RA.brennt_noch_bei_ankunft(g34, wege34)
    b34 = RA.brennt_noch_bei_ankunft(g34, [((151, 218), (173, 114))])
    bt34 = RA.Brandtrupp(1, lambda nr: 0)
    L34[800] = einheit(71, 1, 100, 200)
    bt34.ziel, bt34.befohlen, bt34.heerwege = {800: 291}, {800: 0}, wege34
    bf34 = Befehle()
    m34 = bt34.schritt(L34, {291: g34}, bf34)
    halt34 = [x for x in bf34.liste if x["angriff"].get("einheiten") == [800] and "lauf" in x["angriff"]]
    pruefe(34, "Heerwege %d: brennt noch bei Ankunft %s | nur Linie zum Lord: %s | Brandtrupp: Ziel %s, angehalten %s, %s" % (
        len(wege34), a34, b34, bt34.ziel.get(800), bool(halt34), [m[:45] for m in m34]),
        a34 and not b34 and 800 not in bt34.ziel and halt34 and any("laesst" in m for m in m34))
    # 35 (B-150, Pruefstand: Vorposten (128,151) lag 4 Felder neben dem brennenden Gebaeude 298): brennt es am Punkt, den
    #    die Vorposten-Wahl ohne Feuer nimmt, waehlt sie einen anderen, der nicht im Feuer liegt.
    f35 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
    f35.wegtest = lambda nr, punkte: [True] * len(punkte)
    L35 = {10: einheit(26, 1, 140, 170), 500: einheit(55, 2, 173, 114, 30000)}
    ohne35 = f35._vorposten(L35, (150, 129), [10], (140, 170))
    f35._orte_f = [(ohne35[0], ohne35[1], 4)] if ohne35 else []
    mit35 = f35._vorposten(L35, (150, 129), [10], (140, 170))
    pruefe(35, "Vorposten ohne Feuer %s | dort brennt es -> %s (im Feuer: %s)" % (
        ohne35, mit35, mit35 is not None and F.im_feuer(mit35, f35._orte_f)),
        ohne35 and mit35 and not F.im_feuer(mit35, f35._orte_f))
    # 36 (B-150, Daniel 19:45 "darauf muss man reagieren koennen"): Gebaeude 291 brennt bei (130,155). Streitkolben 10 steht
    #    1 Feld daneben, 11 weit weg, Bogen 12 weit weg. Runde 1: 10 wird an einen freien Punkt geholt und steckt in keinem
    #    anderen Befehl dieser Runde; der Angriff von 10, 11, 12 auf Turm 241 geht fuer 11 und 12 unveraendert durch (Daniel
    #    20:23: niemand wartet daneben - brennt die Bresche selbst, wechselt der Feldzug, Pruefung 38). Runde 2: das Feuer ist
    #    aus (egal warum) -> niemand wird geholt, derselbe Angriffsbefehl geht unveraendert durch.
    f36 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
    L36 = {10: einheit(26, 1, 130, 154), 11: einheit(26, 1, 160, 160), 12: einheit(22, 1, 165, 160),
           500: einheit(55, 2, 173, 114, 30000)}
    G36 = {291: {"typ": 5, "besitzer": 2, "x": 130, "y": 155, "leben": 300, "feuer": 40},
           241: {"typ": 76, "besitzer": 2, "x": 133, "y": 152, "leben": 2000}}
    an36 = {"angriff": {"einheiten": [10, 11, 12], "gebaeude": 241}}
    b36, m36 = Befehle(), []
    f36._feuer_lenken({"t": 12000, "bodenfeuer": []}, L36, G36, b36, m36)(an36, 1.0, bis="ANGRIFF")
    orte36 = F.feuerorte(G36, [])
    raus36 = [x["angriff"]["lauf"] for x in b36.liste if x["angriff"]["einheiten"] == [10] and "lauf" in x["angriff"]]
    weiter36 = [x for x in b36.liste if x["angriff"]["einheiten"] == [11, 12] and x["angriff"].get("gebaeude") == 241]
    mit10 = [x for x in b36.liste if 10 in x["angriff"]["einheiten"] and "lauf" not in x["angriff"]]
    G36[291]["feuer"] = 0
    b36b = Befehle()
    f36._feuer_lenken({"t": 12100, "bodenfeuer": []}, L36, G36, b36b, [])(an36, 1.0, bis="ANGRIFF")
    pruefe(36, "Feuer: raus %s, Angriff 11+12 unveraendert %s, 10 sonst %d Befehle | Feuer aus: %s" % (
        raus36, bool(weiter36), len(mit10), b36b.liste),
        raus36 and not F.im_feuer(tuple(raus36[0]), orte36) and weiter36 and not mit10 and b36b.liste == [an36])
    # 37 (B-150, Daniel 20:23 "aussen herum laufen"): eine Feuerwand 47 Felder breit (Bodenfeuer x 80-120 bei y 100) zwischen
    #    (100,80) und (100,120) - der Weg fuehrt um die Wand herum, jede Strecke frei, am Ende das Ziel (der alte Umweg mit
    #    einem Punkt seitlich fand hier nichts und blieb stehen). Abwaegen (Daniel 20:27), wenn es KEINEN Weg gibt (Ziel in
    #    einem geschlossenen Feuerring): ausser Reichweite der Schuetzen -> warten am Start; unter Beschuss -> direkt durch.
    wand37 = [(x, 100, 3) for x in range(80, 121, 2)]
    w37 = F.feuerfreier_weg((100, 80), (100, 120), wand37)
    k37 = [(100, 80)] + list(w37)
    frei37 = w37[-1] == (100, 120) and all(F._frei(a, b, wand37) for a, b in zip(k37, k37[1:]))
    ring37 = [(100 + dx, 140 + dy, 2) for dx in range(-8, 9, 2) for dy in range(-8, 9, 2) if max(abs(dx), abs(dy)) == 8]
    sicher37 = F.feuerfreier_weg((100, 100), (100, 140), ring37, gefahr=lambda q: 0)
    beschuss37 = F.feuerfreier_weg((100, 100), (100, 140), ring37, gefahr=lambda q: 5)
    pruefe(37, "Feuerwand: Weg %s (frei %s) | geschlossener Ring: sicher -> %s, unter Beschuss -> %s" % (
        w37, frei37, sicher37, beschuss37), frei37 and sicher37 == [(100, 100)] and beschuss37 == [(100, 140)])
    # 38 (B-150, Daniel 20:23): die Bresche (Turm 900, 100 Leben) beginnt zu brennen -> "BRESCHE BRENNT", sofort die naechste
    #    Schwachstelle 901, niemand bekommt einen Befehl auf 900; ist das Feuer aus, darf 900 wieder gewaehlt werden.
    f38 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=20)
    f38.schritt({"t": 12000}, *lage(10, heim), Befehle())
    L38, G38 = lage(0, heim)
    G38[900] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 100}
    G38[901] = {"typ": 46, "besitzer": 2, "x": 301, "y": 116, "leben": 1500}
    for i in range(20):
        L38[10 + i] = einheit(75, 1, 300 + i % 3, 118 + i // 10, 28000)
    f38._stau = (0, 12050)
    f38.schritt({"t": 12050, "bodenfeuer": []}, L38, G38, Befehle())
    erst38 = f38.bresche
    G38[900]["feuer"] = 30
    b38 = Befehle()
    f38._stau = (0, 12150)
    m38 = f38.schritt({"t": 12150, "bodenfeuer": []}, L38, G38, b38)
    dann38 = f38.bresche
    auf900 = [x for x in b38.liste if x.get("angriff", {}).get("gebaeude") == 900]
    G38[900]["feuer"] = 0
    f38._stau = (0, 12250)
    f38.schritt({"t": 12250, "bodenfeuer": []}, L38, G38, Befehle())
    wieder38 = f38._beste_stelle(G38, (300, 100), [(L38[n]["x"], L38[n]["y"]) for n in range(10, 30)])
    pruefe(38, "Bresche erst %s, brennt -> %s %s, Befehle auf 900: %d | Feuer aus: beste Stelle %s" % (
        erst38, dann38, [m[:40] for m in m38 if "BRENNT" in m], len(auf900), wieder38 and wieder38[3]),
        erst38 == 900 and dann38 == 901 and any("BRESCHE BRENNT" in m for m in m38) and not auf900
        and wieder38 and wieder38[3] == 900)
    # 41 (B-161, Franz' Burg 21.10. Takt 74.036: 4 von 9 Angriffsstellen lagen hinter Mauern, die alte Wahl nahm eine davon):
    #    Lord (300,100) im Hof (Gebiet 39) hinter einem 10 Felder dicken Mauerring (Gebiet 0, 275-325); Turm 900 im Hof
    #    (300,112), Turm 901 draussen (330,100); Spitze bei (300,140) im Gebiet 1. Mit Wegkarte -> 901, 900 faellt weg.
    #    Ohne Schuetzen (Gefahr ueberall 0), damit nur die Erreichbarkeit entscheidet. Gegenprobe im selben Test: ohne Wegkarte
    #    nimmt die Wahl 900 (gleiche Leben, naeher an der Spitze).
    import numpy as np41
    import gefahr as GF41
    geb41 = np41.ones((400, 400), np41.int32)
    geb41[275:326, 75:126] = 0
    geb41[285:316, 85:116] = 39
    L41, G41 = lage(0, heim)
    del L41[600], L41[601]
    G41[900] = {"typ": 46, "besitzer": 2, "x": 300, "y": 112, "leben": 1500}
    G41[901] = {"typ": 46, "besitzer": 2, "x": 330, "y": 100, "leben": 1500}
    wahl41 = {}
    for mit in (True, False):
        f41 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
        f41.wegkarte = (lambda: {"gebiet": geb41}) if mit else None
        f41._bed = GF41.bedrohungen(L41, G41, lambda b: b == 2, __import__("gefecht").FERN_REICH)
        f41._karte = None
        w41 = f41._beste_stelle(G41, (300, 100), [(300, 140)])
        wahl41[mit] = (w41 and w41[3], f41._karte is not None and f41._karte.gebiete is not None)
    pruefe(41, "mit Wegkarte: Stelle %s (Gebiete %s) | ohne: Stelle %s" % (wahl41[True][0], wahl41[True][1], wahl41[False][0]),
           wahl41[True] == (901, True) and wahl41[False][0] == 900)
    # 42 (B-162 Abfangen, Daniel 21:16/21:40). Vorher festgelegt: 12 Streitkolben bei (150,200), Ziel (150,100). Schuetze A
    #    (150,160) im Gebiet 1 auf dem Weg, Schuetze B (170,110) auf einer Mauer (Gebiet 31) - das Ziel liegt in seiner
    #    Reichweite, kein Weg fuehrt an ihm vorbei (erste Fassung mit B seitlich blieb im Gegenlauf gruen: der Weg umging B),
    #    Schuetze C (300,300) weit weg. -> genau EIN Abfangbefehl: auf A, mit gefahr.mindestzahl Mann (10.000 Leben in 100
    #    Takten -> 1), der naechste Streitkolben; B und C nichts. Zweite Runde (Abfaenger laeuft, Zustand 2): kein neuer Befehl.
    #    A tot -> Auftrag weg, niemand mehr belegt. Gegenprobe im selben Test: ohne Gebiete (Karte ohne Wegkarte) kein Abfangen.
    geb42 = np41.ones((400, 400), np41.int32)
    geb42[169:172, 109:112] = 31
    L42 = {10 + i: dict(einheit(26, 1, 150 + i % 3, 200 + i // 3), zustand=2) for i in range(12)}
    L42[801] = einheit(22, 2, 150, 160)
    L42[802] = einheit(22, 2, 170, 110)
    L42[803] = einheit(22, 2, 300, 300)
    nah42 = sorted(n for n in L42 if n < 800)
    bed42 = GF41.bedrohungen(L42, {}, lambda b: b == 2, __import__("gefecht").FERN_REICH)
    f42 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=12)
    f42._karte = GF41.Karte(bed42, gebiete=geb42)
    b42, m42, bef42 = Befehle(), [], {}
    ab42 = f42._abfangen(L42, nah42, (151, 201), (150, 100), bef42, b42, m42)
    erst42 = [x["angriff"] for x in b42.liste]
    for n in ab42:
        L42[n]["zustand"] = 2
    b42b = Befehle()
    ab42b = f42._abfangen(L42, nah42, (151, 201), (150, 100), bef42, b42b, [])
    del L42[801]
    ab42c = f42._abfangen(L42, nah42, (151, 201), (150, 100), bef42, Befehle(), [])
    f42o = F.Feldzug(1, heim, lord_schutz_bis=9600, n=12)
    f42o._karte = GF41.Karte(bed42)
    b42o = Befehle()
    ab42o = f42o._abfangen(L42 | {801: einheit(22, 2, 150, 160)}, nah42, (151, 201), (150, 100), {}, b42o, [])
    pruefe(42, "Abfangen: %s %s | 2. Runde %d Befehle | A tot: belegt %s | ohne Gebiete: %d Befehle" % (
        erst42, [m[:50] for m in m42], len(b42b.liste), sorted(ab42c), len(b42o.liste)),
           len(erst42) == 1 and erst42[0].get("ziel") == 801 and erst42[0]["einheiten"] == [10] and ab42 == {10}
           and not b42b.liste and ab42b == {10} and not ab42c and not b42o.liste and not ab42o)
    # 43-45 (B-163/B-164/B-165, Daniel 21.10. 21:59 + 22:04 + 22:07). Vorher festgelegt (22:15), Lord (300,100), Heer am
    #    Sammelpunkt (Gebiet 1), Angriff beginnt im Schritt 12.050:
    #  43. Wegkarte: alles Gebiet 1 (Lord frei), Turm 901 am Lord -> keine SCHWACHSTELLE, Meldung "zu Fuss erreichbar", die
    #      Laufbefehle enden bis 3 Felder am Lord; danach Bresche 901 von Hand gesetzt -> naechste Runde "FREIE FAHRT", Bresche
    #      weg. Gegenprobe: ohne Wegkarte SCHWACHSTELLE (Angriff) auf 901.
    #  44. Wegkarte mit Mauerring (Gebiet 0, 275-325 / 75-125) um den Hof (Gebiet 39) mit dem Lord, Mauerkarte = der Ring,
    #      Turm 901 draussen (330,100) -> "SCHREDDER", EIN Mauerbefehl [300,100,2,30,kx,ky] mit trupp 1 fuer alle 30 - (kx,ky)
    #      eine Ringkachel 25 Felder vom Lord mit Nachbarfeld in Gebiet 1 (22:20: Python waehlt die eine Kachel, Daniel 22:15
    #      "keine Kompression"), kein Gebaeudebefehl, keine SCHWACHSTELLE. Gegenprobe: ohne Mauerkarte SCHWACHSTELLE auf 901.
    #  45. wie 44, die 30 stehen bis 3 Felder an DER Kachel (hacken, Zustand 107): ihre Hoehe bleibt WIRKUNG_TAKTE + 200 Takte
    #      gleich -> "KEINE WIRKUNG: Mauerkachel", sie wird verworfen, eine ANDERE Kachel kommt dran, Schredder bleibt an, keine
    #      SCHWACHSTELLE (22:20: Torhaus/Turm erst, wenn keine Kachel mehr da ist). Gegenprobe: Hoehe sinkt jede Runde um 1.
    #  46. offenes feindliches Tor (Daniel 22:15 "zuerst aufs Torhaus, das war zu, als die Einheiten da waren"): der Ring hat
    #      eine Luecke (298-302 / 116-125) mit Torhaus 905 darauf, Hof und Feld sind beide Gebiet 1 -> mit Gebaeude-Ebene ist
    #      der Lord NICHT frei, Schredder auf eine Aussenkachel. Gegenprobe: ohne Gebaeude-Ebene "zu Fuss erreichbar".
    #      46b (22:27 gemessen: der Durchgang liegt NEBEN dem 4x4-Grundriss, ohne Gebaeudenummer): Grundriss 298-301/119-122,
    #      Durchgang x 302 ohne Nummer -> trotzdem nicht frei (Rand TOR_RAND um den Grundriss).
    def burg43(wk=None, mk=None, runden=(), stand=None, turm=(306, 106)):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        f.schritt({"t": 12000}, *lage(10, heim), Befehle())
        L_, G_ = lage(30, f.punkt)
        G_[901] = {"typ": 46, "besitzer": 2, "x": turm[0], "y": turm[1], "leben": 1500}
        f.wegkarte = (lambda: {"gebiet": wk}) if wk is not None else None
        f.mauerkarte = mk
        b = Befehle()
        m_ = f.schritt({"t": 12050}, L_, G_, b)
        weitere = []
        for k, t in enumerate(runden):
            if stand:
                stand(k, f, L_, G_)
            b2 = Befehle()
            weitere.append((f.schritt({"t": t}, L_, G_, b2), b2.liste))
        return f, m_, b.liste, weitere

    geb43 = np41.ones((400, 400), np41.int32)
    f43, m43, b43, _ = burg43(geb43)
    enden43 = [ende_(x["angriff"]) for x in b43 if "lauf" in x.get("angriff", {})]
    f43.bresche = 901
    L43, G43 = lage(30, f43.punkt)
    G43[901] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 1500}
    m43b = f43.schritt({"t": 12150}, L43, G43, Befehle())
    _, m43o, _, _ = burg43(None)
    pruefe(43, "frei: %s, Laufziele %s | Bresche gesetzt -> %s, Bresche %s | ohne Wegkarte: %s" % (
        [m[:45] for m in m43 if "LORD" in m or "SCHWACHSTELLE" in m], enden43[:3], [m[:45] for m in m43b if "FREIE" in m],
        f43.bresche, [m[:45] for m in m43o if "SCHWACHSTELLE" in m]),
           not any("SCHWACHSTELLE" in m for m in m43) and any("zu Fuss erreichbar" in m for m in m43) and enden43
           and all(F.schach(tuple(e), (300, 100)) <= 3 for e in enden43) and any("FREIE FAHRT" in m for m in m43b)
           and f43.bresche is None and any("SCHWACHSTELLE (Angriff): Gebaeude 901" in m for m in m43o))
    geb44 = np41.ones((400, 400), np41.int32)
    geb44[275:326, 75:126] = 0
    geb44[285:316, 85:116] = 39
    ring44 = (geb44 == 0)
    ring44[:275, :] = False
    ring44[326:, :] = False
    hoehe44 = {"h": np41.where(ring44, 10, 0)}
    mk44 = lambda sp: (ring44.copy(), hoehe44["h"]) if sp == 2 else (np41.zeros((400, 400), bool), np41.zeros((400, 400), int))
    f44, m44, b44, _ = burg43(geb44, mk44, turm=(330, 100))
    mauer44 = [x["angriff"] for x in b44 if "mauer" in x.get("angriff", {})]
    _, m44o, b44o, _ = burg43(geb44, None, turm=(330, 100))
    pruefe(44, "Schredder: %s, Mauerbefehle %s | ohne Mauerkarte: %s, Mauerbefehle %d" % (
        [m[:40] for m in m44 if "SCHREDDER" in m or "SCHWACHSTELLE" in m],
        [(a_["mauer"], a_.get("trupp"), len(a_["einheiten"])) for a_ in mauer44],
        [m[:45] for m in m44o if "SCHWACHSTELLE" in m], sum(1 for x in b44o if "mauer" in x.get("angriff", {}))),
           any("SCHREDDER" in m for m in m44) and not any("SCHWACHSTELLE" in m for m in m44)
           and [(a_["mauer"][:4], a_.get("trupp"), len(a_["einheiten"])) for a_ in mauer44] == [([300, 100, 2, 30], 1, 30)]
           and len(mauer44[0]["mauer"]) == 6 and ring44[tuple(mauer44[0]["mauer"][4:])]
           and F.schach(tuple(mauer44[0]["mauer"][4:]), (300, 100)) == 25
           and not any("gebaeude" in x.get("angriff", {}) for x in b44)
           and any("SCHWACHSTELLE (Angriff): Gebaeude 901" in m for m in m44o)
           and not any("mauer" in x.get("angriff", {}) for x in b44o))

    def an_der_mauer(sinkt):
        def stand(k, f, L_, G_):
            kq = f.mauer_kachel or (275, 100)
            kacheln45.append(kq)
            for i in range(30):
                L_[10 + i].update(x=kq[0] - 1 - i % 3, y=kq[1] - 1 + (i // 3) % 3, zustand=107)
            if sinkt:
                hoehe44["h"] = np41.where(ring44, 10 - (k + 1), 0)
        hoehe44["h"] = np41.where(ring44, 10, 0)
        runden = list(range(12150, 12150 + F.Feldzug.WIRKUNG_TAKTE + 300, 100))
        f, _, _, weitere = burg43(geb44, mk44, runden, stand, turm=(330, 100))
        return f, [m for ms, _ in weitere for m in ms]
    kacheln45 = []
    f45, m45 = an_der_mauer(False)
    k45 = list(dict.fromkeys(kacheln45))
    kacheln45 = []
    f45g, m45g = an_der_mauer(True)
    pruefe(45, "Mauer bleibt: %s, Kacheln %s, Schredder %s | Mauer sinkt: %s, Kacheln %s, Schredder %s" % (
        [m[:60] for m in m45 if "KEINE WIRKUNG" in m or "SCHWACHSTELLE" in m], k45, f45.schredder,
        [m[:40] for m in m45g if "KEINE WIRKUNG" in m], list(dict.fromkeys(kacheln45)), f45g.schredder),
           any("KEINE WIRKUNG: Mauerkachel" in m for m in m45) and len(k45) >= 2 and f45.schredder
           and k45[0] in f45.mauer_verworfen and not any("SCHWACHSTELLE" in m for m in m45)
           and not any("KEINE WIRKUNG" in m for m in m45g) and f45g.schredder and len(set(kacheln45)) == 1)
    geb46 = np41.ones((400, 400), np41.int32)
    geb46[275:326, 75:126] = 0
    geb46[285:316, 85:116] = 1                       # Hof: Gebiet 1 wie draussen - das Tor steht offen
    geb46[298:303, 116:126] = 1                      # Durchgang durchs Tor
    bau46 = np41.zeros((400, 400), np41.int32)
    bau46[298:303, 116:126] = 905
    ring46 = (geb46 == 0)
    ring46[:275, :] = False
    ring46[326:, :] = False
    mk46 = lambda sp: (ring46.copy(), np41.where(ring46, 10, 0)) if sp == 2 else (np41.zeros((400, 400), bool), np41.zeros((400, 400), int))

    bau46b = np41.zeros((400, 400), np41.int32)
    bau46b[298:302, 119:123] = 905

    def tor46(mit_bau, bau=None):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        f.schritt({"t": 12000}, *lage(10, heim), Befehle())
        L_, G_ = lage(30, f.punkt)
        G_[905] = {"typ": 75, "besitzer": 2, "x": 300, "y": 120, "leben": 1500}
        f.wegkarte = lambda: dict({"gebiet": geb46}, **({"gebaeude": bau46 if bau is None else bau} if mit_bau else {}))
        f.mauerkarte = mk46
        b = Befehle()
        return f, f.schritt({"t": 12050}, L_, G_, b), b.liste
    f46, m46, b46 = tor46(True)
    f46o, m46o, _ = tor46(False)
    f46b, m46b, _ = tor46(True, bau46b)
    mauer46 = [x["angriff"]["mauer"] for x in b46 if "mauer" in x.get("angriff", {})]
    pruefe(46, "offenes Tor, mit Gebaeude-Ebene: %s, Mauerbefehle %s | ohne: %s" % (
        [m[:50] for m in m46 if "LORD" in m or "SCHREDDER" in m], mauer46, [m[:50] for m in m46o if "LORD" in m]),
           any("hinter Mauern" in m for m in m46) and any("SCHREDDER" in m for m in m46) and mauer46
           and len(mauer46[0]) == 6 and ring46[tuple(mauer46[0][4:])] and geb46[mauer46[0][4] - 1:mauer46[0][4] + 2,
                                                                                 mauer46[0][5] - 1:mauer46[0][5] + 2].any()
           and not (285 <= mauer46[0][4] <= 315 and 85 <= mauer46[0][5] <= 115)
           and any("zu Fuss erreichbar" in m for m in m46o) and any("hinter Mauern" in m for m in m46b)
           and not any("zu Fuss erreichbar" in m for m in m46b))
    # 47/48 (B-164 Durchbruch, Daniel 22:24 "er muss wirklich durch die ganze Mauer, nicht nur durch eine Schicht"; "rennt
    #    wieder aufs Torhaus"). Vorher festgelegt (22:30), Lord (300,100):
    #  47. zwei Mauerbaender (Schach-Abstand 23-25 und 13-15 vom Lord, Hoehe 50), dazwischen Hof (Gebiet 41), innen Gebiet 39.
    #      SCHREDDER meldet einen Durchbruch-Weg mit 6 Mauerkacheln; faellt die gewaehlte Kachel (Hoehe 0, begehbar), kommt die
    #      naechste AUF DER LINIE: Abstaende zum Lord 25, 24, 23, dann 15, 14, 13 und jede neue Kachel hoechstens 1 Feld neben
    #      der alten (der Sprung durch den Hof hoechstens 8). Gegenlauf (Sabotage im Gegenlauf-Skript): alte Wahl "naechste
    #      Kachel am Lord mit Nachbarfeld in unserem Gebiet" -> rot.
    #  48. Kachel gewaehlt, das Heer bleibt weit weg (Zustand 2, kommt nie bis 3 heran): nach ANKUNFT_TAKTE "KOMMT NICHT AN",
    #      die Kachel ist verworfen, eine andere wird gewaehlt. Gegenprobe: 30 Mann bis 3 an der Kachel, Hoehe sinkt -> keine
    #      Meldung.
    def baender47():
        dx = np41.abs(np41.arange(400)[:, None] - 300)
        dy = np41.abs(np41.arange(400)[None, :] - 100)
        d = np41.maximum(dx, dy)
        geb = np41.ones((400, 400), np41.int32)
        wand = ((d >= 23) & (d <= 25)) | ((d >= 13) & (d <= 15))
        geb[wand] = 0
        geb[(d >= 16) & (d <= 22)] = 41
        geb[d <= 12] = 39
        return geb, wand
    geb47, wand47 = baender47()
    zust47 = {"m": wand47.copy(), "h": np41.where(wand47, 50, 0), "geb": geb47.copy()}
    mk47 = lambda sp: (zust47["m"].copy(), zust47["h"]) if sp == 2 else (np41.zeros((400, 400), bool), np41.zeros((400, 400), int))
    folge47 = []

    def faellt47(k, f, L_, G_):
        f._stau = (0, 12150 + 100 * k)
        kq = f.mauer_kachel
        if kq is None:
            return
        folge47.append(kq)
        zust47["m"][kq] = False
        zust47["h"][kq] = 0
        zust47["geb"][kq] = 1
    f47 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f47.schritt({"t": 12000}, *lage(10, heim), Befehle())
    L47, G47 = lage(30, f47.punkt)
    G47[901] = {"typ": 46, "besitzer": 2, "x": 340, "y": 100, "leben": 1500}
    f47.wegkarte = lambda: {"gebiet": zust47["geb"]}
    f47.mauerkarte = mk47
    m47 = f47.schritt({"t": 12050}, L47, G47, Befehle())
    for k, t in enumerate(range(12150, 12150 + 100 * 8, 100)):
        faellt47(k, f47, L47, G47)
        m47 += f47.schritt({"t": t}, L47, G47, Befehle())
    abst47 = [F.schach(q, (300, 100)) for q in folge47]
    schritte47 = [F.schach(a_, b_) for a_, b_ in zip(folge47, folge47[1:])]
    pruefe(47, "Durchbruch: %s | Kacheln %s, Abstaende %s, Schritte %s" % (
        [m[m.find("Durchbruch-Weg"):m.find("Durchbruch-Weg") + 40] for m in m47 if "SCHREDDER: " in m][:1], folge47, abst47,
        schritte47),
           any("Durchbruch-Weg: 6 Mauerkacheln" in m for m in m47) and abst47[:6] == [25, 24, 23, 15, 14, 13]
           and all(s_ <= 1 for i, s_ in enumerate(schritte47[:5]) if i != 2) and schritte47[2] <= 8)

    def kommt48(nah):
        def stand(k, f, L_, G_):
            f._stau = (0, 12150 + 100 * k)
            kq = f.mauer_kachel or kacheln48[-1]
            kacheln48.append(kq)
            for i in range(30):
                if nah:
                    L_[10 + i].update(x=kq[0] - 1 - i % 3, y=kq[1] - 1 + (i // 3) % 3, zustand=107)
                else:
                    L_[10 + i].update(zustand=2)
            if nah:
                hoehe44["h"] = np41.where(ring44, 20 - k, 0)
        hoehe44["h"] = np41.where(ring44, 20, 0)
        runden = list(range(12150, 12150 + F.Feldzug.ANKUNFT_TAKTE + 400, 100))
        f, _, _, weitere = burg43(geb44, mk44, runden, stand, turm=(330, 100))
        return f, [m for ms, _ in weitere for m in ms]
    kacheln48 = [(275, 100)]
    f48, m48 = kommt48(False)
    k48 = list(dict.fromkeys(kacheln48[1:]))
    kacheln48 = [(275, 100)]
    f48g, m48g = kommt48(True)
    pruefe(48, "fern: %s, Kacheln %s | nah: %s" % ([m[:70] for m in m48 if "KOMMT NICHT AN" in m], k48,
                                                    [m[:50] for m in m48g if "KOMMT NICHT AN" in m]),
           any("KOMMT NICHT AN" in m for m in m48) and len(k48) >= 2 and k48[0] in f48.mauer_verworfen
           and not any("KOMMT NICHT AN" in m for m in m48g))
    # 49 (B-166, 21.10. 22:45 im Spielcode abgelesen: handleUnitMovementWhenTargetingBuildings prueft bei einer Mauerkachel nur
    #    N/O/S/W - schraeg daneben beginnt nie ein Mauerangriff; Messung 22:41: 1 Mann schraeg an Kachel (171,121), 5.945 Takte
    #    kein Schlag). Vorher festgelegt: Ring aus Test 44, das Heer kommt schraeg (Suedwest, (240,170)) - auf dem Durchbruch-Weg ist
    #    der Schritt vom Feld vor JEDER Mauerkachel gerade (|dx|+|dy| = 1). Gegenlauf (8 Nachbarn erlaubt) -> rot.
    f49 = F.Feldzug(1, heim, n=10)
    plan49 = f49._durchbruch(geb44, ring44, np41.where(ring44, 50, 0), (240, 170), (300, 100))
    weg49 = plan49["weg"]
    schritte49 = [(abs(weg49[i][0] - weg49[i - 1][0]) + abs(weg49[i][1] - weg49[i - 1][1])) for i in range(1, len(weg49))
                  if ring44[weg49[i]]]
    pruefe(49, "Durchbruch von Suedwest: erste Kachel %s, Schritte auf Mauerkacheln %s" % (plan49["kachel"], schritte49),
           plan49["kachel"] is not None and schritte49 and all(s_ == 1 for s_ in schritte49))
    # 39 (B-150, Pruefstand 20:32: die Umleitung schickte je Einheit einen Befehl zum naechsten Wegknoten des Spiels): 10
    #    Streitkolben laufen (Zustand 2) zum befohlenen Vorposten (150,133), ihr naechstes Wegstueck fuehrt durch ein Feuer
    #    -> EIN Befehl fuer alle 10, Ziel am Ende der Vorposten (nicht ihr Wegknoten); Gegenprobe: ein Angreifer (Bresche) mit
    #    demselben Wegstueck wird nicht umgeleitet.
    f39 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
    L39 = {500: einheit(55, 2, 173, 114, 30000), 30: dict(einheit(26, 1, 140, 160), zustand=2, laufx=140, laufy=140)}
    for i in range(10):
        L39[10 + i] = dict(einheit(26, 1, 140 + i % 3, 160 + i // 5), zustand=2, laufx=140, laufy=140)
    f39._befohlen = {10 + i: ("vorposten", (150, 133)) for i in range(10)}
    f39._befohlen[30] = ("bresche", 900)
    G39 = {291: {"typ": 5, "besitzer": 2, "x": 140, "y": 150, "leben": 300, "feuer": 40}}
    b39 = Befehle()
    f39._feuer_lenken({"t": 12000, "bodenfeuer": []}, L39, G39, b39, [])
    um39 = [x["angriff"] for x in b39.liste if "lauf" in x["angriff"]]
    ziel39 = [(a_.get("danach") or [a_["lauf"]])[-1] for a_ in um39]
    pruefe(39, "Umleitungen %d %s, Ziele am Ende %s, Angreifer 30 dabei: %s" % (
        len(um39), [len(a_["einheiten"]) for a_ in um39], ziel39, any(30 in a_["einheiten"] for a_ in um39)),
        len(um39) == 1 and len(um39[0]["einheiten"]) == 10 and ziel39 == [[150, 133]] and not any(30 in a_["einheiten"] for a_ in um39))
    # 40 (B-157, Daniel 21:11 "maximale Sicherheit, dann minimaler Widerstand"): 10 Streitkolben bei (100,200), ein feindlicher
    #    Bogen (Reichweite 44) bei (100,120), Laufbefehl nach (100,40) quer durchs Schussfeld -> der Befehl geht ueber die
    #    Wegkette ("SICHERER WEG"), die Gefahr ist kleiner als auf der Geraden. Gegenprobe (Sabotage): gefahr.K = 0 -> rot.
    import gefahr as GF40
    f40 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
    L40 = {500: einheit(55, 2, 300, 300, 30000), 600: einheit(22, 2, 100, 120)}
    for i in range(10):
        L40[10 + i] = einheit(26, 1, 100 + i % 3, 200 + i // 5)
    b40, m40 = Befehle(), []
    f40._feuer_lenken({"t": 12000, "bodenfeuer": []}, L40, {}, b40, m40)({"angriff": {"einheiten": list(range(10, 20)),
                                                                                    "lauf": [100, 40]}}, 1.0, bis="ANGRIFF")
    a40 = [x["angriff"] for x in b40.liste if "lauf" in x["angriff"]]
    weg40 = [tuple(a40[0]["lauf"])] + [tuple(q) for q in a40[0].get("danach", [])] if a40 else []
    g_neu, g_alt = (GF40.weg_gefahr((101, 200), weg40, f40._bed) if weg40 else -1), GF40.weg_gefahr((101, 200), [(100, 40)], f40._bed)
    pruefe(40, "Weg %s, Gefahr %d statt %d (gerade), Meldung %s" % (weg40[:5], g_neu, g_alt, [m[:40] for m in m40][:1]),
           weg40 and weg40[-1] == (100, 40) and 0 <= g_neu < g_alt and any("SICHERER WEG" in m for m in m40))
    # 50/51 (B-170, Daniel 22.10. 08:39 "er geht immer noch gegen Tuerme und einsame Mauern statt die aufzumachen, die zum Lord
    #    fuehren"): hinter Mauern entscheidet der Durchbruch-Planer (hier ein fester Plan statt durchbruch.plane).
    #  50. Plan "Torhaus 905 auf dem Weg", Turm 901 abseits (330,100) -> Bresche 905, Meldung "DURCHBRUCH", nie 901.
    #      Gegenprobe ohne Planer (nur Mauerkarte): kein Torhaus aus dem Plan (Schredder wie in 44).
    #  51. Plan "Mauerkachel (275,100), Zugang (274,100)": Runde 1 (alle am Sammelpunkt) -> Laufbefehl (274,100) mit trupp 1
    #      fuer alle 30, kein Mauerbefehl; Runde 2 (alle bis 1 Feld am Zugang) -> mauerziel halten (Schluessel sp1, Feld 4242,
    #      30 Einheiten) und EIN Mauerbefehl mit 7 Werten [300,100,2,30,275,100,3] (Blick aus dem Planer). Gegenprobe ohne
    #      Planer: kein mauerziel, Mauerbefehl mit 6 Werten.
    def burg50(plan, runde2=None, mit_planer=True):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        f.schritt({"t": 12000}, *lage(10, heim), Befehle())
        L_, G_ = lage(30, f.punkt)
        G_[901] = {"typ": 46, "besitzer": 2, "x": 330, "y": 100, "leben": 1500}
        G_[905] = {"typ": 75, "besitzer": 2, "x": 300, "y": 124, "leben": 1500}
        f.wegkarte = lambda: {"gebiet": geb44}
        f.mauerkarte = mk44
        if mit_planer:
            f.durchbruch = lambda sp, start, maenner, lord, verworfen=(): dict(plan)
            f.blick = lambda kachel, sp: ((275, 100), 3)
            f.feldnr = lambda xy: 4242
        b1 = Befehle()
        m1 = f.schritt({"t": 12050}, L_, G_, b1)
        m2, b2 = [], Befehle()
        if runde2:
            runde2(L_)
            m2 = f.schritt({"t": 12150}, L_, G_, b2)
        return f, m1, b1.liste, m2, b2.liste

    hoehe44["h"] = np41.where(ring44, 10, 0)
    plan50 = {"art": "tor", "ziel": 905, "zug": (300, 128), "weg": [(300, 140), (300, 128), (300, 124), (300, 100)],
              "takte": 999, "belastung": 0, "kandidaten": [("tor", 905, 0, 999)]}
    f50, m50, b50, _, _ = burg50(plan50)
    f50o, m50o, _, _, _ = burg50(plan50, mit_planer=False)
    pruefe(50, "Torhaus auf dem Weg: Bresche %s, %s | ohne Planer: Bresche %s, %s" % (
        f50.bresche, [m[:60] for m in m50 if "DURCHBRUCH" in m or "SCHWACHSTELLE" in m], f50o.bresche,
        [m[:40] for m in m50o if "SCHREDDER" in m or "SCHWACHSTELLE" in m]),
           f50.bresche == 905 and any("DURCHBRUCH" in m for m in m50) and not any("901" in m for m in m50)
           and f50o.bresche != 905)

    plan51 = {"art": "mauer", "ziel": (275, 100), "zug": (274, 100), "weg": [(260, 100), (274, 100), (275, 100), (300, 100)],
              "takte": 500, "belastung": 0, "kandidaten": [("mauer", None, 0, 500)]}

    def am_zug(L_):
        for i in range(30):
            L_[10 + i].update(x=273 + i % 2, y=99 + i % 3, zustand=1)
    f51, m51, b51, m51b, b51b = burg50(plan51, am_zug)
    lauf51 = [x["angriff"] for x in b51 if "lauf" in x.get("angriff", {}) and tuple(ende_(x["angriff"])) == (274, 100)]
    mauer51 = [x["angriff"] for x in b51 if "mauer" in x.get("angriff", {})]
    mz51 = [x["mauerziel"] for x in b51b if "mauerziel" in x]
    mauer51b = [x["angriff"] for x in b51b if "mauer" in x.get("angriff", {})]
    _, _, b51o, _, b51ob = burg50(plan51, am_zug, mit_planer=False)
    mauer51o = [x["angriff"]["mauer"] for x in b51o + b51ob if "mauer" in x.get("angriff", {})]
    pruefe(51, "Runde 1: Lauf zum Zugang %s, Mauerbefehle %d | Runde 2: mauerziel %s, Mauerbefehl %s | ohne Planer: mauerziel %d, "
               "Mauerbefehle %s" % (
                   [(len(a_["einheiten"]), a_.get("trupp")) for a_ in lauf51], len(mauer51),
                   [(z["schluessel"], z["feld"], z.get("halten"), len(z["einheiten"])) for z in mz51],
                   [(a_["mauer"], len(a_["einheiten"])) for a_ in mauer51b],
                   sum(1 for x in b51o + b51ob if "mauerziel" in x), [len(m_) for m_ in mauer51o]),
           lauf51 and sum(len(a_["einheiten"]) for a_ in lauf51) == 30 and all(a_.get("trupp") == 1 for a_ in lauf51)
           and not mauer51 and len(mz51) == 1 and mz51[0]["schluessel"] == "sp1" and mz51[0]["feld"] == 4242
           and mz51[0]["halten"] is True and len(mz51[0]["einheiten"]) == 30
           and [a_["mauer"] for a_ in mauer51b] == [[300, 100, 2, 30, 275, 100, 3]] and len(mauer51b[0]["einheiten"]) == 30
           and not any("mauerziel" in x for x in b51o + b51ob) and mauer51o and all(len(m_) == 6 for m_ in mauer51o))
    # 52-55 (B-176/179/180/184/185, 2v2 22.10. 17:5x)
    #  52. Plan bleibt: 12 Runden, die Kachel steht -> der Planer wird genau 1-mal gerufen; Kachel verworfen -> neu geplant
    #  53. Stau mit aktivem Plan (Mauer): STAU_TICKS + 500 Takte ohne Fortschritt -> keine SCHWACHSTELLE, kein "alle direkt"
    #  54. Lord zu Fuss erreichbar (Wegkarte Gebiet 1 ueberall) + _schwachstelle -> False, Meldung "KEINE SCHWACHSTELLE", keine
    #      Bresche
    #  55. mechanik.durchbruch_schritte: Mauerriegel, gesperrte Kachel auf der Geraden -> der Weg hackt sie nicht; Gegenprobe
    #      ohne Sperre: er hackt genau sie
    aufrufe52 = []

    def planer52(sp, start, maenner, lord, verworfen=()):
        aufrufe52.append(set(verworfen))
        return dict(plan51)
    f52 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f52.schritt({"t": 12000}, *lage(10, heim), Befehle())
    L52, G52 = lage(30, f52.punkt)
    f52.wegkarte, f52.mauerkarte = (lambda: {"gebiet": geb44}), mk44
    f52.durchbruch, f52.blick, f52.feldnr = planer52, (lambda k, sp: ((275, 100), 3)), (lambda xy: 4242)
    m53 = []
    for i in range(12):
        m53 += f52.schritt({"t": 12050 + 100 * i}, L52, G52, Befehle())
    n52 = len(aufrufe52)
    f52.mauer_verworfen.add((275, 100))
    f52.schritt({"t": 13300}, L52, G52, Befehle())
    for i in range(int(F.Feldzug.STAU_TICKS / 100) + 6):
        m53 += f52.schritt({"t": 13400 + 100 * i}, L52, G52, Befehle())
    pruefe(52, "Planer-Aufrufe in 12 Runden: %d, nach Verwerfen: %d (verworfen mitgegeben: %s)" % (
        n52, len(aufrufe52), (275, 100) in (aufrufe52[n52] if len(aufrufe52) > n52 else set())),
           n52 == 1 and len(aufrufe52) > n52 and (275, 100) in aufrufe52[n52])
    pruefe(53, "Stau mit Plan: %s" % [m[:50] for m in m53 if "SCHWACHSTELLE" in m or "STAU" in m or "direkt" in m],
           not any("SCHWACHSTELLE (" in m or "alle direkt" in m for m in m53))
    f54 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f54._lord_frei_alt = True
    m54 = []
    L54, G54 = lage(30, (280, 100))
    G54[901] = {"typ": 46, "besitzer": 2, "x": 330, "y": 100, "leben": 1500}
    r54 = f54._schwachstelle(G54, (300, 100), [(280, 100)], m54, "Stau 1")
    pruefe(54, "Lord frei: Schwachstelle %s, Bresche %s, %s" % (r54, f54.bresche, m54), r54 is False and f54.bresche is None
           and any("KEINE SCHWACHSTELLE" in m for m in m54))
    import mechanik as MK
    n55 = 40
    link55 = np41.full((n55, n55), 255, np41.uint8)
    logik55 = np41.zeros((n55, n55), np41.int64)
    logik55[20, 5:35] = 0x100
    hoehe55 = np41.zeros((n55, n55), int)
    hoehe55[20, 5:35] = 10
    boden55 = np41.zeros((n55, n55), int)
    besitz55 = np41.full((n55, n55), 1, np41.int64)            # (1 & 7) + 1 = Spieler 2
    bau55 = np41.zeros((n55, n55), np41.int32)
    sperre55 = np41.zeros((n55, n55), bool)
    mk55 = {"mauer": 5, "tor_turm": 15, "takte_je_treffer": 96}       # gemessen (Streitkolben, Wissensregister) - ohne Spiel
    arg55 = (link55, logik55, bau55, besitz55, hoehe55, boden55, 1, 10, (10, 20), (30, 20), mk55)
    logik55[20, :] = 0x100                                      # durchgehender Riegel - ohne Hacken kein Weg
    hoehe55[20, :] = 10
    r55o = MK.durchbruch_schritte(*arg55)
    k55 = tuple(r55o["mauern"][0]) if r55o.get("mauern") else None
    if k55:
        sperre55[k55] = True
    r55 = MK.durchbruch_schritte(*arg55, sperre=sperre55)
    pruefe(55, "ohne Sperre gehackt %s | mit dieser Kachel gesperrt: Mauern auf dem Weg %s" % (k55, r55.get("mauern")),
           k55 and r55["weg"] and k55 not in [tuple(q) for q in r55["mauern"]])
    # 56 (B-177/B-182): Feuerballiste (Typ 77) im Gebiet 1 greift Einheit 10 an -> Abfang mit 2 Mann; dieselbe auf einer Mauer
    #    (Gebiet 0) -> niemand
    import gefahr as GF56
    geb56 = np41.ones((400, 400), np41.int32)
    geb56[150, 150] = 0
    def abfang56(ort):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        f._karte = GF56.Karte([], gebiete=geb56)
        L_ = {10 + i: einheit(26, 1, 140 + i % 5, 140 + i // 5) for i in range(20)}
        L_[777] = dict(einheit(77, 2, ort[0], ort[1], 5000), zieleinheit=10)
        aus_ = []
        return f._abfangen(L_, sorted(k for k in L_ if k < 777), (140, 140), (300, 300), {}, Befehle(), aus_), aus_
    a56, m56 = abfang56((145, 150))
    a56o, m56o = abfang56((150, 150))
    pruefe(56, "Ballista im Feld: %d Jaeger %s | auf der Mauer: %d" % (len(a56), [m[:50] for m in m56], len(a56o)),
           len(a56) >= 2 and any("Feuerballiste 777" in m for m in m56) and len(a56o) == 0)
    # 62 (B-205, Daniel 22.10. 18:47 "Streitkolben gehen nicht auf die Feuerballiste"): Ballista zielt auf KEINE Einheit
    #    (Gebaeudebeschuss), 10 Felder neben den Nahkaempfern, nur 2 Nahkaempfer (Anteil 2 // 3 = 0) -> trotzdem 2 Jaeger;
    #    Gegenprobe: 80 Felder weit -> niemand
    def abfang62(ort):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        f._karte = GF56.Karte([], gebiete=geb56)
        L_ = {10: einheit(26, 1, 140, 140), 11: einheit(26, 1, 141, 140)}
        L_[777] = dict(einheit(77, 2, ort[0], ort[1], 5000), zieleinheit=0)
        aus_ = []
        return f._abfangen(L_, [10, 11], (140, 140), (300, 300), {}, Befehle(), aus_), aus_
    a62, m62 = abfang62((140, 130))
    a62f, _ = abfang62((220, 140))
    pruefe(62, "Ballista auf Gebaeude 10 Felder weit, 2 Nahkaempfer: %d Jaeger %s | 80 Felder weit: %d" % (
        len(a62), [m[:45] for m in m62], len(a62f)), len(a62) == 2 and len(a62f) == 0)
    # 63 (B-207, Daniel 22.10. 18:49 "Sicherheitsabstand viel zu gross"; 2v2 184103: Sp1 13 gegen 20 wartete, Sp2 27 gegen 22):
    #    13 eigene Streitkolben gegen 20 Speere am Lord verlieren; dazu 27 Streitkolben des Verbuendeten (Spieler 2) 20 Felder
    #    vor der Stelle -> Sieg; Gegenprobe: dieselben 27 stehen 100 Felder weit weg (nicht beim Angriff) -> Niederlage
    import parteien as P63
    P63._FEST[1] = frozenset((0, 1, 2))
    def lohnt63(abstand):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        L_ = {10 + i: einheit(26, 1, 300, 300) for i in range(13)}
        L_.update({100 + i: einheit(24, 3, 200 + i % 5, 100 + i // 5) for i in range(20)})
        L_.update({300 + i: einheit(26, 2, 200 + i % 5, 100 + abstand + i // 5) for i in range(27)})
        lord = einheit(55, 3, 200, 100, 150000)
        return f._lohnt(L_, sorted(k for k in L_ if k < 100), lord, am_ziel=True, ort=(200, 100))
    ok63, t63 = lohnt63(20)
    ok63f, t63f = lohnt63(100)
    del P63._FEST[1]
    pruefe(63, "mit Verbuendetem 20 Felder vor: %s %s | 100 Felder weit: %s %s" % (ok63, t63[:70], ok63f, t63f[:50]), ok63 and not ok63f)
    # 57 (B-191): Heer 1 plant (275,100), Heer 2 mit derselben Absprache-Datei uebernimmt den Plan ohne eigenen Planer-Aufruf;
    #    ohne Datei plant Heer 2 selbst
    import tempfile
    datei57 = os.path.join(tempfile.mkdtemp(), "absprache.json")

    def heer57(mit_datei, planer):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        f.schritt({"t": 12000}, *lage(10, heim), Befehle())
        L_, G_ = lage(30, f.punkt)
        f.wegkarte, f.mauerkarte = (lambda: {"gebiet": geb44}), mk44
        f.durchbruch, f.blick, f.feldnr = planer, (lambda k, sp: ((275, 100), 3)), (lambda xy: 4242)
        f.absprache = datei57 if mit_datei else None
        m_ = f.schritt({"t": 12050}, L_, G_, Befehle())
        return f, m_
    aufrufe57 = []
    f57a, _ = heer57(True, lambda sp, st, ma, lo, verworfen=(): dict(plan51))
    f57b, m57b = heer57(True, lambda sp, st, ma, lo, verworfen=(): aufrufe57.append(1) or dict(plan51, ziel=(276, 100), zug=(277, 100)))
    n57 = len(aufrufe57)
    f57c, _ = heer57(False, lambda sp, st, ma, lo, verworfen=(): aufrufe57.append(1) or dict(plan51, ziel=(276, 100), zug=(277, 100)))
    pruefe(57, "Heer 2 mit Absprache: Ziel %s, Planer-Aufrufe %d, %s | ohne Datei: Ziel %s" % (
        (f57b.dplan or {}).get("ziel"), n57, [m[:45] for m in m57b if "Absprache" in m], (f57c.dplan or {}).get("ziel")),
           (f57b.dplan or {}).get("ziel") == (275, 100) and n57 == 0 and (f57c.dplan or {}).get("ziel") == (276, 100))
    # 58 (B-193/B-181): Plan aktiv, 6 stehen untaetig im Beschuss -> "STEHT NUR -> ARBEIT", Wegkette zum Zugang, kein RUECKZUG;
    #    ohne Planer (Mauerkarte allein) -> alter RUECKZUG
    def steht58(mit_planer):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        f.schritt({"t": 12000}, *lage(10, heim), Befehle())
        L_, G_ = lage(30, f.punkt)
        f.wegkarte, f.mauerkarte = (lambda: {"gebiet": geb44}), mk44
        if mit_planer:
            f.durchbruch, f.blick, f.feldnr = (lambda sp, st, ma, lo, verworfen=(): dict(plan51)), (lambda k, sp: ((275, 100), 3)), (lambda xy: 4242)
        f.schritt({"t": 12050}, L_, G_, Befehle())
        f._steht_nur = lambda L__, nk, t__: sorted(nk)[:6]
        b = Befehle()
        return f.schritt({"t": 12150}, L_, G_, b), b.liste
    m58, b58 = steht58(True)
    m58o, _ = steht58(False)
    pruefe(58, "mit Plan: %s | ohne Planer: %s" % ([m[:45] for m in m58 if "STEHT NUR" in m or "RUECKZUG" in m],
                                                   [m[:30] for m in m58o if "RUECKZUG" in m]),
           any("STEHT NUR -> ARBEIT" in m for m in m58) and not any("FELDZUG RUECKZUG" in m for m in m58)
           and any("FELDZUG RUECKZUG" in m for m in m58o))
    # 59 (B-192): Feuer am bisherigen Sammelpunkt -> _sammelpunkt waehlt einen Punkt ausserhalb des Feuers; ohne Feuer derselbe
    f59 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    L59, G59 = lage(10, heim)
    f59._orte_f = []
    p59 = f59._sammelpunkt(L59, G59, L59[500])
    f59._orte_f = [(p59[0], p59[1], 4)]
    p59f = f59._sammelpunkt(L59, G59, L59[500])
    pruefe(59, "Sammelpunkt ohne Feuer %s, mit Feuer dort %s" % (p59, p59f), p59f != p59 and not F.im_feuer(p59f, f59._orte_f))
    # 60 (B-190): Lord 500 faellt (verschwindet aus dem Lagebild) -> Meldung "NACH DEM SIEG", ein Laufbefehl fuer alle Kolben
    #    zu einem Punkt, kein festgehaltener Plan mehr
    f60 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f60.schritt({"t": 12000}, *lage(10, heim), Befehle())
    L60, G60 = lage(30, f60.punkt)
    f60.schritt({"t": 12050}, L60, G60, Befehle())
    del L60[500]
    b60 = Befehle()
    m60 = f60.schritt({"t": 12150}, L60, G60, b60)
    lauf60 = [x["angriff"] for x in b60.liste if "lauf" in x.get("angriff", {}) and len(x["angriff"]["einheiten"]) >= 30]
    pruefe(60, "nach dem Fall: %s, Laufbefehle fuer alle %d, Plan %s" % ([m[:40] for m in m60 if "SIEG" in m], len(lauf60), f60.dplan),
           any("NACH DEM SIEG" in m for m in m60) and lauf60 and f60.dplan is None)
    # 61 (B-177): Streitkolben 10 steht untaetig, feindlicher Bogen 3 Felder daneben -> Angriffsbefehl auf ihn; Bogen 10 Felder
    #    weg -> keiner
    def nah61(abstand):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        L_ = {500: einheit(55, 2, 300, 100, 30000), 10: einheit(26, 1, 100, 100), 900: einheit(22, 2, 100 + abstand, 100)}
        b = Befehle()
        m_ = f.schritt({"t": 12000}, L_, {}, b)
        return [x["angriff"] for x in b.liste if x.get("angriff", {}).get("ziel") == 900], m_
    a61, m61 = nah61(3)
    a61o, _ = nah61(10)
    pruefe(61, "Bogen 3 daneben: %s | 10 weg: %s" % (a61, a61o), a61 and 10 in a61[0]["einheiten"] and not a61o)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
