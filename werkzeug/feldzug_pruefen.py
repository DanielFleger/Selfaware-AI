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
                ziele16[t] = x["angriff"]["lauf"]
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
    bogen17 = [x["angriff"]["lauf"] for x in lauf17 if 60 in x["angriff"]["einheiten"]]
    for i in range(10):
        L17[10 + i]["zustand"] = 105                 # 21:31 gemessen: so sehen sie nach dem Laufbefehl aus
    b17b = Befehle()
    f17.schritt({"t": 12150}, L17, G17, b17b)
    nochmal17 = [x for x in b17b.liste if "lauf" in x.get("angriff", {}) and set(x["angriff"]["einheiten"]) & set(range(10, 20))]
    pruefe(17, "Schwaechste Stelle: Ziel %s, Torangriffe %d, Laufbefehle an Nahkaempfer %s (naechste Runde nochmal: %d), Bogen laeuft nach %s" % (
        f17.bresche, len(tor17), [(x["angriff"]["lauf"], len(x["angriff"]["einheiten"])) for x in nk17], len(nochmal17), bogen17),
           f17.bresche == 902 and not tor17 and [(x["angriff"]["lauf"], len(x["angriff"]["einheiten"])) for x in nk17] == [([300, 100], 11)]
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
    def zaeh(sinkt):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=20)
        f.schritt({"t": 12000}, *lage(10, heim), Befehle())
        L_, G_ = lage(0, heim)
        G_[900] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 100}
        G_[901] = {"typ": 46, "besitzer": 2, "x": 301, "y": 110, "leben": 1500}
        for i in range(20):
            L_[10 + i] = einheit(75, 1, 300 + i % 3, 108 + i // 10, 28000)
        m_ = []
        for k, t in enumerate(range(12050, 12050 + F.Feldzug.BRESCHE_ZAEH + 300, 100)):
            if sinkt and k % 10 == 9:
                G_[900]["leben"] -= 5
            f._stau = (0, t)                          # kein Stau in dieser Pruefung
            m_ += f.schritt({"t": t}, L_, G_, Befehle())
        return m_, f
    m19, f19 = zaeh(False)
    m19g, f19g = zaeh(True)
    pruefe(19, "Zaehe Bresche: %s, danach Ziel %s | Leben sinkt: verworfen %s, Ziel %s" % (
        [m[:50] for m in m19 if "ZAEH" in m], f19.bresche, sorted(f19g.verworfen), f19g.bresche),
        any("ZAEH" in m for m in m19) and f19.verworfen == {900} and f19.bresche == 901
        and not f19g.verworfen and f19g.bresche == 900)
    # 20 (B-139/B-140): 30 arab. Schwertkaempfer irgendwo (nicht am Sammelpunkt), der Lord mit 2 Schuetzen, Lord-Schutz vorbei
    #    -> die Gefechtsrechnung mit dem ganzen Heer gewinnt -> sofort ANGRIFF (kein Rueckweg zum Sammelpunkt).
    #    Gegenprobe (B-140, Pruefstand T40126: 30 gegen Franz' 86): dieselben 30, am Lord stehen 80 arab. Schwertkaempfer -> sammeln.
    def neustart(verteidiger):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        L_, G_ = lage(0, heim)
        for i in range(30):
            L_[10 + i] = einheit(75, 1, 250 + i % 5, 160 + i // 5, 28000)
        for i in range(verteidiger):
            L_[1000 + i] = einheit(75, 2, 296 + i % 9, 96 + i // 9, 28000)
        m_ = f.schritt({"t": 12000}, L_, G_, Befehle())
        return f.phase, [m[:50] for m in m_ if "ANGRIFF" in m]
    ph20, m20 = neustart(0)
    ph20g, _ = neustart(80)
    pruefe(20, "30 verstreut gegen Lord + 2 Schuetzen: Phase %s %s | gegen 80 am Lord: %s" % (ph20, m20, ph20g),
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
        lauf_ = [(x["angriff"]["lauf"], len(x["angriff"]["einheiten"])) for x in b.liste if "lauf" in x.get("angriff", {})]
        for i in range(10):
            L_[10 + i]["zustand"] = 105
        b2 = Befehle()
        f.schritt({"t": 12100}, L_, G_, b2)
        nochmal = [x for x in b2.liste if "lauf" in x.get("angriff", {}) and set(x["angriff"]["einheiten"]) & set(range(10, 20))]
        bogen2 = [x["angriff"]["lauf"] for x in b2.liste if "lauf" in x.get("angriff", {}) and 60 in x["angriff"]["einheiten"]]
        vp = f.vorposten[1] if f.vorposten else None
        for i in range(10):
            L_[10 + i]["x"], L_[10 + i]["y"], L_[10 + i]["zustand"] = 306, 110, 1
        b3 = Befehle()
        f.schritt({"t": 12200}, L_, G_, b3)
        tor_ = [len(x["angriff"]["einheiten"]) for x in b3.liste if x.get("angriff", {}).get("gebaeude") == 901]
        return [m[:60] for m in m_ if "VORPOSTEN" in m], lauf_, len(nochmal), tor_, vp, bogen2
    m22, l22, n22, t22, vp22, bg22 = vorposten(True)
    m22g, l22g, _, _, vp22g, _ = vorposten(False)
    pruefe(22, "Vorposten %s: %s, Laufbefehle %s, naechste Runde %d, Bogen dann %s, am Tor Angriff %s | ohne Treffer: %s %s" % (
        vp22, m22, l22, n22, bg22, t22, m22g, l22g),
           vp22 and F.schach(vp22, (306, 106)) == 4 and vp22[1] > 106 and ([list(vp22), 10] in [list(x) for x in l22])
           and n22 == 0 and bg22 == [list(vp22)] and t22 == [10]
           and vp22g is None and any("keiner gefunden" in m for m in m22g) and l22g == [([300, 100], 11)])
    # 23 (B-139, Daniel 21:44, Bild: nach dem ersten zerstoerten Turm standen alle vor der Burg und wurden abgeschossen): zwei
    #    Tore, das erste faellt, der Wegtest findet am Lord (Ringe 1-3) nichts -> "eingemauert" und SOFORT die naechste
    #    Schwachstelle (kein Stau abwarten). Gegenprobe: Lord erreichbar (Feld 2 suedlich) -> alle Nahkaempfer laufen dorthin,
    #    keine neue Schwachstelle; dort angekommen -> Angriffsbefehl auf den Lord.
    def lord_frei(erreichbar):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=10)
        lp_ = (300, 100)
        def wt(nr, punkte):
            return [(q[1] > 106 and abs(q[0] - 306) <= 4) or (erreichbar and q == (lp_[0], lp_[1] + 2)) for q in punkte]
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
        lauf_ = [(x["angriff"]["lauf"], len(x["angriff"]["einheiten"])) for x in b.liste if "lauf" in x.get("angriff", {})]
        for i in range(10):
            L_[10 + i]["x"], L_[10 + i]["y"], L_[10 + i]["zustand"] = 300 + i % 3, 102 + i // 5, 1
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
           and lord23g == [10])
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
    def stelle(am_tor):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
        L_, G_ = lage(0, heim)
        for i in range(30):
            L_[10 + i] = einheit(75, 1, 250 + i % 5, 160 + i // 5, 28000)
        for i in range(80):
            L_[1000 + i] = einheit(75, 2, 296 + i % 9, (116 if am_tor else 56) + i // 9, 28000)
        G_[901] = {"typ": 46, "besitzer": 2, "x": 300, "y": 120, "leben": 1500}
        m_ = f.schritt({"t": 12000}, L_, G_, Befehle())
        return f.phase, [m[:60] for m in m_ if "ANGRIFF" in m]
    ph25, m25 = stelle(False)
    ph25g, _ = stelle(True)
    pruefe(25, "80 Verteidiger 40 Felder hinter dem Lord, Tor vorn: Phase %s %s | 80 am Tor: %s" % (ph25, m25, ph25g),
           ph25 == "angriff" and ph25g == "sammeln")
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
