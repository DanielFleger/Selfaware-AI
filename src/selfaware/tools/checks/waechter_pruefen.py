# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer den Waechter (19.10.2026, Partie 1019b, Daniel: "die lassen sich einfach angreifen ohne Grund").
Vorher festgelegt:
  1. (1019b, Tick 14.204) 4 feindliche Assassinen, eine schlaegt unseren Bogen 45 (nahziel 45); ein feindlicher Bogen 50
     Felder suedlich an unseren Feldern; unser Bogen 189 hat nahangreifer 1, Bogen 45 nahangreifer 0; feindliche Einheit
     Nr. 1 ist ein Arbeiter weit weg -> Ziel der Abwehr ist die Assassine 156 (vorher: der Arbeiter Nr. 1 oder der Bogen)
  2. eine feindliche Einheit beschiesst unsere Assassine tief in ihrem Gebiet (zieleinheit = Assassine, 120 Felder weg)
     -> kein Angreifer, keine Abwehr dorthin
  Gefechtsbewertung (Daniel 19.10.: "koennen nicht evaluieren, wann ein Counter sich lohnt"; feste Testtabelle, damit die
  Faelle nicht von der Messung abhaengen: Speer 25 je Takt, Streitkolben 140, Sklave 15, Leben 12.500 / 25.000 / 5.000):
  3. 12 Speertraeger 10 Felder neben einem Sklaven an unserem Feld -> Angriff ("Abwehr gebuendelt")
  4. 3 Speertraeger gegen 8 Streitkolben an unserem Feld -> kein Angriff, "ABWEHR VERZICHTET", Sammeln am Bergfried
  5. 12 Speertraeger 130 Felder weg von einem Sklaven an einem fernen Holzfaeller -> kein Angriff (der Weg dauert laenger,
     als das Gefecht gerechnet wird - 1019d: alle 12 liefen 130 Felder einem Sklaven nach)
  6. (Daniel, Bild 1019b: Feinde zerstoeren unsere Felder, unsere Truppen stehen daneben) 6 Streitkolben des Feldzugs als
     Reserve (er sammelt), 2 Sklaven an unserem Feld -> die Reserve greift an; ohne Feind -> kein Befehl an die Reserve
  7. (1019b, Tick 14.204, mit den ECHTEN Editor-Messwerten) 7 arab. Bogen werden von 4 feindlichen Assassinen geschlagen,
     4 Speer + 3 arab. Schwert stehen 15 Felder weg -> Angriff nur mit den Nahkaempfern auf eine Assassine, die Bogen weichen
     zum Bergfried (Rechnung: alle 45 % Rest, nur Nahkampf 69 %)
  8. (1019h: der Waechter jagte mit 38-51 Mann Reserve einzelne feindliche Assassinen) 20 arab. Schwertkaempfer als Reserve
     30 Felder weg, eine feindliche Assassine an unserem Feld -> hoechstens 4 werden geschickt, die anderen bekommen keinen
     Befehl
Aufruf: uv run python -m selfaware.tools.checks.waechter_pruefen [<alte waechter.py>]   (Rueckgabe 0 = gruen)
"""
import importlib.util, os, sys
HIER = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) > 1:
    spec = importlib.util.spec_from_file_location("waechter", sys.argv[1])
    W = importlib.util.module_from_spec(spec); spec.loader.exec_module(W)
else:
    import selfaware.micro.tasks.waechter as W
befehle = []
W.befehl = lambda b, *a, **k: befehle.append(b) or []
ok = []


def pruefe(nr, text, bed):
    ok.append(bool(bed)); print("%s %d %s" % ("OK  " if bed else "ROT ", nr, text))


def e(typ, sp, x, y, **k):
    d = {"typ": typ, "besitzer": sp, "x": x, "y": y, "leben": 10000, "zustand": 1, "laufx": x, "laufy": y, "nahziel": 0,
         "nahangreifer": 0, "zieleinheit": 0}
    d.update(k)
    return d


def main():
    gebaeude = [(150, 160), (145, 215), (150, 200)]
    L = {45: e(70, 1, 139, 168, nahangreifer=0, zustand=106, nahziel=156), 189: e(70, 1, 140, 168, nahangreifer=1),
         60: e(24, 1, 155, 158), 61: e(24, 1, 156, 158), 62: e(75, 1, 156, 159),
         156: e(73, 2, 140, 169, nahziel=45, zustand=106), 166: e(73, 2, 141, 170), 185: e(73, 2, 142, 170),
         295: e(22, 2, 137, 220), 1: e(13, 2, 146, 237)}
    w = W.Waechter(1); w.besetzt = True
    w.schritt(L, gebaeude)
    pruefe(1, "Ziel der Abwehr %s (Assassine 156 schlaegt Bogen 45)" % (w.ziel,), w.ziel == 156)
    # 2
    befehle.clear()
    L2 = {60: e(24, 1, 155, 158), 61: e(24, 1, 156, 158), 300: e(73, 1, 280, 280), 400: e(22, 2, 285, 280, zieleinheit=300)}
    w2 = W.Waechter(1); w2.besetzt = True
    w2.schritt(L2, gebaeude)
    pruefe(2, "Schuetze beschiesst unsere Assassine 120 Felder weg: Ziel %s, Befehle %d" % (w2.ziel, len(befehle)), w2.ziel is None)
    # 3-5: Gefechtsbewertung mit fester Tabelle
    try:
        import selfaware.services.gefecht as gefecht
        gefecht._TABELLE = ({24: {71: 25.0, 26: 25.0}, 26: {24: 140.0, 71: 140.0}, 71: {24: 15.0, 26: 15.0}},
                            {24: 12500, 26: 25000, 71: 5000})
    except ImportError:
        gefecht = None

    def lage_kampf(n_speer, gegner, n_gegner, gx, gy, sx=150, sy=160):
        befehle.clear()
        L = {}
        for i in range(n_speer):
            L[100 + i] = e(24, 1, sx + i % 4, sy + i // 4, leben=12500)
        for i in range(n_gegner):
            L[500 + i] = e(gegner, 2, gx + i % 3, gy + i // 3, leben=5000 if gegner == 71 else 25000)
        w = W.Waechter(1); w.besetzt = True
        erg = w.schritt(L, [(gx - 3, gy), (150, 160)])
        angriff = any(b.get("angriff", {}).get("ziel") in L and L[b["angriff"]["ziel"]]["besitzer"] == 2 for b in befehle)
        return angriff, [x[:90] for x in erg if "ABWEHR" in x or "Abwehr" in x][:1]
    a3, m3 = lage_kampf(12, 71, 1, 160, 160)
    pruefe(3, "12 Speer gegen 1 Sklaven 10 Felder weit: Angriff %s %s" % (a3, m3), a3)
    a4, m4 = lage_kampf(3, 26, 8, 160, 160)
    pruefe(4, "3 Speer gegen 8 Streitkolben: Angriff %s %s" % (a4, m4), not a4 and m4 and "VERZICHTET" in m4[0])
    a5, m5 = lage_kampf(12, 71, 1, 280, 290)
    pruefe(5, "12 Speer, Sklave 130 Felder weit an fernem Holzfaeller: Angriff %s %s" % (a5, m5), not a5)
    # 6
    befehle.clear()
    L6 = {200 + i: e(26, 1, 150 + i, 160, leben=25000) for i in range(6)}
    L6.update({500: e(71, 2, 165, 160, leben=5000), 501: e(71, 2, 166, 161, leben=5000)})
    w6 = W.Waechter(1); w6.besetzt = True
    try:
        w6.schritt(L6, [(162, 160)], reserve=set(range(200, 206)))
        mit = [b for b in befehle if b.get("angriff", {}).get("ziel") in (500, 501)]
        befehle.clear()
        L6b = {200 + i: e(26, 1, 150 + i, 160, leben=25000) for i in range(6)}
        L6b[300] = e(22, 1, 140, 150)
        w6.schritt(L6b, [(162, 160)], reserve=set(range(200, 206)))
        ohne = [b for b in befehle if set(b.get("angriff", {}).get("einheiten", [])) & set(range(200, 206))]
    except TypeError:
        mit, ohne = [], ["alte Fassung ohne Reserve"]
    pruefe(6, "Reserve gegen 2 Sklaven am Feld: Angriffsbefehle %d; ohne Feind Befehle an die Reserve %d" % (len(mit), len(ohne)),
           mit and not ohne)
    # 7
    if gefecht is not None:
        gefecht._TABELLE = None
    befehle.clear()
    L7 = {40 + i: e(70, 1, 140 + i % 3, 168, leben=15000) for i in range(7)}
    L7[40]["nahangreifer"] = 1
    L7.update({60 + i: e(24, 1, 155, 158, leben=12500) for i in range(4)})
    L7.update({64 + i: e(75, 1, 156, 159, leben=28000) for i in range(3)})
    L7.update({156 + i: e(73, 2, 141 + i % 2, 169 + i // 2, leben=12500, nahziel=40 if i == 0 else 0) for i in range(4)})
    w7 = W.Waechter(1); w7.besetzt = True
    erg7 = w7.schritt(L7, [(150, 160)])
    ang = [b for b in befehle if b.get("angriff", {}).get("ziel") in range(156, 160)]
    weg = [b for b in befehle if b.get("angriff", {}).get("lauf") and set(b["angriff"]["einheiten"]) <= set(range(40, 47))]
    nur_nah = bool(ang) and set(ang[-1]["angriff"]["einheiten"]) <= set(range(60, 67))
    pruefe(7, "Bogen von Assassinen geschlagen: Angriff nur Nahkampf %s, Bogen weichen %s %s" % (
        nur_nah, bool(weg), [x[:110] for x in erg7 if "Abwehr" in x or "raus" in x][:2]), nur_nah and weg)
    # 8
    befehle.clear()
    L8 = {300 + i: e(75, 1, 150 + i % 5, 190 + i // 5, leben=28000) for i in range(20)}
    L8[700] = e(73, 2, 152, 160, leben=12500)
    w8 = W.Waechter(1); w8.besetzt = True
    w8.schritt(L8, [(150, 158)], reserve=set(range(300, 320)))
    ang8 = [b for b in befehle if b.get("angriff", {}).get("ziel") == 700]
    n8 = len(ang8[-1]["angriff"]["einheiten"]) if ang8 else 0
    pruefe(8, "eine Assassine am Feld, 20 Reserve: geschickt %d" % n8, 0 < n8 <= 4)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
