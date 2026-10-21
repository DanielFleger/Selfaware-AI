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
    #    ohne Feuer -> geradeaus. Dazu im Feldzug: ein Laufbefehl wird durch den Umweg ersetzt (Meldung FEUER MEIDEN).
    orte31 = F.feuerorte({19: {"x": 201, "y": 99, "feuer": 50}}, [(201, 98), (203, 102)])
    w31 = F.feuerfreier_weg((201, 125), (201, 75), orte31)
    w31g = F.feuerfreier_weg((201, 125), (201, 75), [])
    frei31 = len(w31) == 2 and all(F._abstand_strecke((x, y), a, b) > r for x, y, r in orte31
                                   for a, b in (((201, 125), w31[0]), (w31[0], (201, 75))))
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
        frei31 and w31g == [(201, 75)] and laeufe31 and not nah31 and any("FEUER MEIDEN" in m for m in m31))
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
    #    anderen Befehl dieser Runde; der Angriff von 10, 11, 12 auf Turm 241 bei (133,152) (im Feuer) wird fuer 11 zu
    #    "daneben warten", der Bogen 12 behaelt den Angriff. Runde 2: das Feuer ist aus (egal warum) -> niemand wird geholt,
    #    derselbe Angriffsbefehl geht unveraendert durch.
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
    warte36 = [x["angriff"]["lauf"] for x in b36.liste if x["angriff"]["einheiten"] == [11] and "lauf" in x["angriff"]]
    schuss36 = [x for x in b36.liste if x["angriff"]["einheiten"] == [12] and x["angriff"].get("gebaeude") == 241]
    mit10 = [x for x in b36.liste if 10 in x["angriff"]["einheiten"] and "lauf" not in x["angriff"]]
    G36[291]["feuer"] = 0
    b36b = Befehle()
    f36._feuer_lenken({"t": 12100, "bodenfeuer": []}, L36, G36, b36b, [])(an36, 1.0, bis="ANGRIFF")
    pruefe(36, "Feuer: raus %s, warten %s, Bogen schiesst %s, 10 sonst %d Befehle | Feuer aus: %s" % (
        raus36, warte36, bool(schuss36), len(mit10), b36b.liste),
        raus36 and not F.im_feuer(tuple(raus36[0]), orte36) and warte36
        and not F.im_feuer(tuple(warte36[0]), orte36, rand=2) and schuss36 and not mit10 and b36b.liste == [an36])
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
