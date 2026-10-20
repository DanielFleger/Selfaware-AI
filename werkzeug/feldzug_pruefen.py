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
    # 1
    f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
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
    pruefe(4, "Lord 500 tot: Ziel jetzt %s, Phase %s, Meldungen %s" % (f.ziel, f.phase, [a[:40] for a in aus][:2]), f.ziel == 700 and f.phase == "sammeln")
    # 5
    f5 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
    f5.schritt({"t": 12000}, *lage(10, heim), Befehle())
    q = f5.punkt
    L, G = lage(10, q)
    L[800] = einheit(24, 2, q[0] + 12, q[1])
    b = Befehle()
    f5.schritt({"t": 12050}, L, G, b)
    pruefe(5, "Speer 12 Felder vor dem Sammelpunkt: Angriff auf ihn %s" % [x for x in b.liste if x.get("angriff", {}).get("ziel") == 800][:1],
           any(x.get("angriff", {}).get("ziel") == 800 for x in b.liste))
    # 6
    f6 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=30)
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
    # 15 (B-134 Burg knacken, 20.10.: 2v2 gegen Rotkaeppchen, 37.000 Ticks Stau vor der Burg): auch "direkt" bringt niemanden
    #    naeher -> beim dritten Stau Angriff auf das feindliche Tor (Typ 46) am Lord; faellt es, wieder auf den Lord.
    #    Gegenprobe: ohne Tor/Turm nur die Meldung "kein feindliches Tor/Turm", kein Gebaeude-Angriff.
    def burg(mit_tor):
        # B-138: mit Sturmwelle - N = 20, die 20 Schwertkaempfer erreichen den Sturmpunkt, dann geht es aufs Tor
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=20)
        f.wegplaner = lambda L_, G_, s, z: [(150, 200), (200, 150), (250, 120), z]
        f.schritt({"t": 12000}, *lage(10, heim), Befehle())
        f.schritt({"t": 12050}, *lage(30, f.punkt), Befehle())
        L_, G_ = lage(0, heim)
        for i in range(20):
            L_[10 + i] = einheit(75, 1, 100 + i % 5, 240 + i // 5, 28000)
        lp = (L_[500]["x"], L_[500]["y"])
        if mit_tor:
            G_[900] = {"typ": 46, "besitzer": 2, "x": lp[0] + 6, "y": lp[1] + 6, "leben": 1000}
        m_, tor_ = [], []
        for t in range(12100, 17000, 100):
            b = Befehle()
            m_ += [m for m in f.schritt({"t": t}, L_, G_, b) if "STAU" in m or "BURG" in m or "BRESCHE" in m]
            tor_ += [x for x in b.liste if x.get("angriff", {}).get("gebaeude") == 900]
            if f.sturm_punkt and f.sturm_los is None:
                for i in range(20):
                    L_[10 + i]["x"], L_[10 + i]["y"] = f.sturm_punkt[0] + i % 3, f.sturm_punkt[1] + i // 10
        fallen = []
        if mit_tor:
            del G_[900]
            fallen = [m for m in f.schritt({"t": 17100}, L_, G_, Befehle()) if "BRESCHE" in m]
        return m_, tor_, fallen
    m15, tor15, fall15 = burg(True)
    m15o, tor15o, _ = burg(False)
    pruefe(15, "Burg knacken: %s; Tor-Angriffe %d, gefallen %s | ohne Tor: %s" % (
        [m[:50] for m in m15 if "BURG" in m][:1], len(tor15), [m[:40] for m in fall15], [m[:50] for m in m15o][-1:]),
           any("BURG KNACKEN" in m for m in m15) and tor15 and len(tor15[0]["angriff"]["einheiten"]) == 20 and fall15
           and not tor15o and any("kein feindliches Tor" in m for m in m15o))
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
    # 17 (B-138 Sturmwelle, 20.10. L151: Nahkaempfer kamen einzeln ans Torhaus und starben; dazu hob der Laufbefehl zum Lord
    #    jeden Torangriff in derselben Runde wieder auf). Vorher festgelegt:
    #    a) Bresche steht, 10 von N=20 Nahkaempfern weit weg -> Laufbefehl an den Sturmpunkt, KEIN Torangriff; der Sturmpunkt
    #       ist der Standort des eigenen Bogens (240,160) - sicher (mehr als SICHER Felder von jedem Feindschuetzen) und dem
    #       Tor am naechsten (20.10.: ein gedachter Punkt war unerreichbar)
    #    b) 20 am Sturmpunkt -> STURM LOS, Torangriff fuer alle 20, und in dieser und der naechsten Runde KEIN Laufbefehl an sie
    #    c) STURM_ABWEHR Ticks nach dem Losgehen weniger als STURM_REST am Tor -> ABGEWEHRT, wieder Laufbefehl zum Sturmpunkt
    f17 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=20)
    f17.schritt({"t": 12000}, *lage(10, heim), Befehle())
    f17.schritt({"t": 12050}, *lage(30, f17.punkt), Befehle())
    L17, G17 = lage(0, heim)
    G17[900] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 1000}
    for i in range(10):
        L17[10 + i] = einheit(75, 1, 100 + i % 5, 240 + i // 5, 28000)
    L17[60] = einheit(70, 1, 240, 160, 15000)     # ein eigener Bogen steht sicher vor dem Tor (55 Felder vom naechsten Feindbogen)
    f17.phase, f17.direkt, f17.bresche, f17.weg, f17.weg_i, f17.weg_ziel = "angriff", True, 900, [(300, 100)], 0, (300, 100)
    f17._stau = (0, 12100)                           # kein neuer Stau waehrend der Pruefung
    b = Befehle()
    m17 = f17.schritt({"t": 12100}, L17, G17, b)
    sp17 = f17.sturm_punkt
    fern17 = [(e["x"], e["y"]) for e in L17.values() if e["besitzer"] == 2 and e["typ"] in F.FERN]
    nk = set(range(10, 30))
    lauf_a = [x["angriff"]["lauf"] for x in b.liste if "lauf" in x.get("angriff", {}) and set(x["angriff"]["einheiten"]) & nk]
    tor_a = [x for x in b.liste if x.get("angriff", {}).get("gebaeude") == 900]
    ok_a = sp17 == (240, 160) and lauf_a == [list(sp17)] and not tor_a and min(F.schach(sp17, q) for q in fern17) > F.Feldzug.SICHER
    for i in range(20):
        L17[10 + i] = einheit(75, 1, sp17[0] + i % 3, sp17[1] + i // 10, 28000)
    b1, b2 = Befehle(), Befehle()
    m17 += f17.schritt({"t": 12200}, L17, G17, b1) + f17.schritt({"t": 12300}, L17, G17, b2)
    tor_b = [x for x in b1.liste if x.get("angriff", {}).get("gebaeude") == 900]
    lauf_b = [x for x in b1.liste + b2.liste if "lauf" in x.get("angriff", {}) and set(x["angriff"]["einheiten"]) & set(range(10, 30))]
    ok_b = any("STURM LOS" in m for m in m17) and tor_b and len(tor_b[0]["angriff"]["einheiten"]) == 20 and not lauf_b
    for i in range(17):
        del L17[10 + i]                              # die Welle stirbt: 3 bleiben auf halber Strecke (31 Felder vom Tor)
    for n in (27, 28, 29):
        L17[n]["x"], L17[n]["y"] = (sp17[0] + 306) // 2, (sp17[1] + 106) // 2
    b3 = Befehle()
    m17 += f17.schritt({"t": 12300 + F.Feldzug.STURM_ABWEHR}, L17, G17, b3)
    lauf_c = [x["angriff"]["lauf"] for x in b3.liste if "lauf" in x.get("angriff", {}) and set(x["angriff"]["einheiten"]) & nk]
    ok_c = any("ABGEWEHRT" in m for m in m17) and f17.sturm_los is None and lauf_c == [list(sp17)]
    pruefe(17, "Sturmwelle: Punkt %s (a %s: Lauf %s, Tor %d) (b %s: Tor %s, Lauf danach %d) (c %s: %s)" % (
        sp17, bool(ok_a), lauf_a, len(tor_a), bool(ok_b), len(tor_b[0]["angriff"]["einheiten"]) if tor_b else 0, len(lauf_b),
        bool(ok_c), [m[:40] for m in m17 if "ABGEWEHRT" in m]), ok_a and ok_b and ok_c)
    # 18 (B-138, 20.10. Partie gegen Franz+Karl: beim Sammeln und Stuermen kommt die Spitze nicht naeher -> neuer Stau): ein Stau
    #    waehrend der laufenden Welle waehlt KEIN anderes Tor, auch wenn eines naeher am Lord liegt - die Welle laeuft weiter.
    #    Gegenprobe: ist die Bresche gefallen, waehlt der naechste Stau das andere Tor.
    f18 = F.Feldzug(1, heim, lord_schutz_bis=9600, n=20)
    f18.schritt({"t": 12000}, *lage(10, heim), Befehle())
    f18.schritt({"t": 12050}, *lage(30, f18.punkt), Befehle())
    L18, G18 = lage(0, heim)
    G18[900] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 1000}
    for i in range(20):
        L18[10 + i] = einheit(75, 1, 280 + i % 3, 120 + i // 10, 28000)
    f18.phase, f18.direkt, f18.bresche, f18.staus = "angriff", True, 900, 3
    f18.weg, f18.weg_i, f18.weg_ziel = [(300, 100)], 0, (300, 100)
    f18.sturm_fuer, f18.sturm_punkt, f18.sturm_seit, f18.sturm_los = 900, (250, 150), 12000, 12050
    G18[901] = {"typ": 46, "besitzer": 2, "x": 301, "y": 101, "leben": 1000}      # neues Tor, naeher am Lord
    f18._stau = (20, 12100)
    m18 = f18.schritt({"t": 12100 + F.Feldzug.STAU_TICKS}, L18, G18, Befehle())
    bleibt = f18.bresche == 900 and f18.sturm_los == 12050 and not any("STURM:" in m for m in m18)
    del G18[900]
    f18.schritt({"t": 13700}, L18, G18, Befehle())
    f18._stau = (20, 13700)
    m18b = f18.schritt({"t": 13700 + F.Feldzug.STAU_TICKS}, L18, G18, Befehle())
    pruefe(18, "Stau waehrend der Welle: Bresche %s bleibt %s; nach dem Fall neu: %s" % (
        900, bleibt, [m[:60] for m in m18b if "BURG" in m]), bleibt and f18.bresche == 901)
    # 19 (B-138, 20.10. gegen Franz: Zugbruecke 420 blieb trotz Sturm bei 100 Leben): 20 Nahkaempfer stehen am Tor, sein Leben
    #    sinkt BRESCHE_ZAEH Ticks lang nicht -> "ZAEH", verworfen, der naechste Stau waehlt das andere Tor.
    #    Gegenprobe: sinkt das Leben zwischendurch, wird nichts verworfen.
    def zaeh(sinkt):
        f = F.Feldzug(1, heim, lord_schutz_bis=9600, n=20)
        f.schritt({"t": 12000}, *lage(10, heim), Befehle())
        f.schritt({"t": 12050}, *lage(30, f.punkt), Befehle())
        L_, G_ = lage(0, heim)
        G_[900] = {"typ": 46, "besitzer": 2, "x": 306, "y": 106, "leben": 100}
        G_[901] = {"typ": 46, "besitzer": 2, "x": 301, "y": 110, "leben": 1500}
        for i in range(20):
            L_[10 + i] = einheit(75, 1, 300 + i % 3, 108 + i // 10, 28000)
        f.phase, f.direkt, f.bresche, f.staus = "angriff", True, 900, 3
        f.weg, f.weg_i, f.weg_ziel = [(300, 100)], 0, (300, 100)
        f.sturm_fuer, f.sturm_punkt, f.sturm_seit, f.sturm_los = 900, (250, 150), 12000, 12050
        f._stau = (0, 99999)
        m_ = []
        for k, t in enumerate(range(12100, 12100 + F.Feldzug.BRESCHE_ZAEH + 200, 100)):
            if sinkt and k % 10 == 9:
                G_[900]["leben"] -= 5
            m_ += f.schritt({"t": t}, L_, G_, Befehle())
        f._stau = (0, t)
        m_ += f.schritt({"t": t + F.Feldzug.STAU_TICKS}, L_, G_, Befehle())
        return m_, f
    m19, f19 = zaeh(False)
    m19g, f19g = zaeh(True)
    pruefe(19, "Zaehe Bresche: %s, danach Ziel %s | Leben sinkt: verworfen %s, Ziel %s" % (
        [m[:50] for m in m19 if "ZAEH" in m], f19.bresche, sorted(f19g.verworfen), f19g.bresche),
        any("ZAEH" in m for m in m19) and f19.verworfen == {900} and f19.bresche == 901
        and not f19g.verworfen and f19g.bresche == 900)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
