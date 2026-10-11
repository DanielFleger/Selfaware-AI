# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer 4a "Ausweichen bei Uebermacht" (Daniel 05.10. 22:16: erst weggehen, bis sie nicht mehr
verfolgen, dann weiter angreifen). Vorher festgelegt, was gelten muss:
  1. 1 eigener gegen 3 feindliche Assassinen (2 Felder) -> AUSWEICHEN als echter Laufbefehl (Spielbefehl 17) weiter weg, KEIN Ziel
  2. naechste Runde, Verfolger weiter dicht dran -> in DIESER Runde wieder ein Laufbefehl, naeher an Heim, kein Ziel
  3. Verfolger 15 Felder weg (> SICHER_NAH): nach FLUCHT_RUHE Runden "AUSWEICHEN vorbei" und wieder eine ZIELWAHL
  4. 3 eigene gegen 3 feindliche -> kein Ausweichen (nicht unterlegen)
  5. 1 gegen 1 -> kein Ausweichen
Aufruf: python werkzeug/ausweichen_pruefen.py [andere_assassinen.py]   (Rueckgabe 0 = gruen)
"""
import importlib.util, os, sys
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
if len(sys.argv) > 1:                                   # Gegenprobe gegen eine andere Fassung
    spec = importlib.util.spec_from_file_location("assassinen", sys.argv[1])
    A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
else:
    import assassinen as A

ORTE = [(94, 280), (141, 269)]


def einheit(typ, besitzer, x, y, leben=12500, **k):
    e = {"typ": typ, "besitzer": besitzer, "x": x, "y": y, "leben": leben, "zustand": 0, "zielart": 0, "zieleinheit": 0,
         "zieluid": 0, "zielgebaeude": 0, "ziel": 0, "zielx": 0, "ziely": 0, "laufx": x, "laufy": y, "auswahlvon": 0,
         "auswahlmarke": 0, "gruppe": 0, "gruppenuid": 0, "ladung": 0, "arbeitsplatz": 0, "erreichbar": 1}
    e.update(k)
    return e


def neu():
    return A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda n, p: [True] * len(p))


def hat(ereignis, wort, n):
    return any(z.startswith(wort) and (" %d:" % n in z or " %d " % n in z or z.split()[1].rstrip(":") == str(n)) for z in ereignis)


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    G = {900: {"besitzer": 2, "typ": 32, "x": 200, "y": 270, "leben": 100, "uid": 1, "erreichbar": 1}}
    # 1.-3. einer gegen drei
    t = neu()
    L = {100: einheit(73, 1, 198, 270), 501: einheit(73, 2, 200, 270), 502: einheit(73, 2, 200, 271), 503: einheit(73, 2, 199, 272)}
    t.aufnehmen([100])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    flucht = getattr(t, "flucht", {})
    lauf = [b["angriff"]["lauf"] for b in bef if "lauf" in b.get("angriff", {}) and 100 in b["angriff"]["einheiten"]]
    pruefe(1, "1 gegen 3: ausweichen per Laufbefehl %s, weiter weg, kein Ziel (Flucht %s, Ziel %s)" % (
        lauf, 100 in flucht, t.ziel.get(100)),
        100 in flucht and lauf and max(abs(lauf[0][0] - 200), abs(lauf[0][1] - 270)) > 5 and 100 not in t.ziel)
    L[100].update(x=192, y=268)                                    # ein Stueck gelaufen, Verfolger dicht dahinter
    for f, (x, y) in zip((501, 502, 503), ((194, 268), (194, 269), (193, 270))):
        L[f].update(x=x, y=y)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    # Flucht muss ein echter Laufbefehl sein (angriff mit lauf = Spielbefehl 17), kein halten - halten bricht den Nahkampf
    # nicht ab (abgelesen logik.lua, gemessen raidzuerst_2: er kaempfte am Warteplatz 1 gegen 3 bis zum Tod)
    flieh = [b["angriff"]["lauf"] for b in bef if "lauf" in b.get("angriff", {}) and 100 in b["angriff"]["einheiten"]]
    heim = min(max(abs(192 - h[0]), abs(268 - h[1])) for h in ORTE)
    neu_heim = min(max(abs(flieh[0][0] - h[0]), abs(flieh[0][1] - h[1])) for h in ORTE) if flieh else 999
    # (seit 22:37: zu Hause steht hier niemand - also NICHT zur Burg, mindestens HEIM_ABSTAND weg; Fall 14/15 pruefen das genauer)
    pruefe(2, "Verfolger bleiben nah: in DIESER Runde neuer Fluchtbefehl (%s, Abstand Heim %d -> %d), kein Ziel" % (
        flieh, heim, neu_heim), 100 in getattr(t, "flucht", {}) and 100 not in t.ziel and flieh)
    # 6./7. kein Stop-and-go (raidzuerst_3: neuer Befehl je Runde = neue Gruppe = kurzer Halt, 3 Felder in 60 Ticks)
    o = t.warte.get(100)
    L[100].update(x=185, y=268, zustand=101, laufx=o[0] if o else 0, laufy=o[1] if o else 0)
    for f, (x, y) in zip((501, 502, 503), ((190, 268), (190, 269), (189, 270))):
        L[f].update(x=x, y=y)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    fuer100 = [b for b in bef if 100 in b.get("angriff", {}).get("einheiten", []) or 100 in b.get("halten", {}).get("nr", [])]
    pruefe(6, "laeuft schon zu seinem Fluchtpunkt %s, Verfolger 5 Felder hinter ihm: KEIN neuer Befehl (%s)" % (o, fuer100),
           o and not fuer100 and 100 in getattr(t, "flucht", {}))
    L[100].update(zustand=106)                                    # eingeholt, kaempft
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    lauf = [b["angriff"]["lauf"] for b in bef if "lauf" in b.get("angriff", {}) and 100 in b["angriff"]["einheiten"]]
    pruefe(7, "eingeholt und im Nahkampf: sofort neuer Laufbefehl weg (%s)" % lauf, bool(lauf))
    for f in (501, 502, 503):                                     # Verfolger geben auf: 15+ Felder weg
        L[f].update(x=L[f]["x"] + 40)                              # (40: auch nicht mehr am Zielgebaeude - sonst gilt es als bewacht)
    L[100].update(x=180, y=270)
    runden = []
    for _ in range(getattr(A.Einzeln, "FLUCHT_RUHE", 2) + 1):
        erg, bef = t.schritt(L, G, sichere_orte=ORTE)
        runden.append((100 in getattr(t, "flucht", {}), 100 in t.ziel, [z for z in erg if "AUSWEICHEN vorbei" in z or "ZIELWAHL 100" in z]))
    pruefe(3, "Verfolger weg -> nach FLUCHT_RUHE Runden wieder angreifen: %s" % runden,
           runden and not runden[-1][0] and runden[-1][1] and any("AUSWEICHEN vorbei" in z for r in runden for z in r[2]))
    # 4. drei gegen drei
    t = neu()
    L = {100: einheit(73, 1, 198, 270), 101: einheit(73, 1, 198, 271), 102: einheit(73, 1, 197, 270),
         501: einheit(73, 2, 200, 270), 502: einheit(73, 2, 200, 271), 503: einheit(73, 2, 199, 272)}
    t.aufnehmen([100, 101, 102])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    pruefe(4, "3 gegen 3: kein Ausweichen", not any("AUSWEICHEN" in z for z in erg))
    # 5. einer gegen einen
    t = neu()
    L = {100: einheit(73, 1, 198, 270), 501: einheit(73, 2, 200, 270)}
    t.aufnehmen([100])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    pruefe(5, "1 gegen 1: kein Ausweichen", not any("AUSWEICHEN" in z for z in erg))
    # 8. frueh erkennen: 2 feindliche Nahkaempfer 8 Felder weg, noch kein Kontakt -> schon jetzt ausweichen
    t = neu()
    L = {100: einheit(73, 1, 190, 270), 501: einheit(73, 2, 198, 270), 502: einheit(24, 2, 198, 272)}
    t.aufnehmen([100])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    pruefe(8, "Uebermacht 8 Felder weg (noch kein Kontakt): schon ausweichen", any(z.startswith("AUSWEICHEN 100") for z in erg))
    # 9. blockiert: Zustand laeuft, Laufziel = Fluchtpunkt, aber gleiches Feld wie letzte Runde -> andere Richtung
    # 9a. normales Gehen (raidzuerst_5): eine Runde auf demselben Feld, dann ein Feld weiter -> NICHT blockiert, kein neuer Befehl
    o = t.warte.get(100)
    L[100].update(zustand=101, laufx=o[0] if o else 0, laufy=o[1] if o else 0)
    neu_befohlen = []
    for x in (190, 189, 189, 188):                               # Feld wechselt jede zweite Runde
        L[100].update(x=x)
        erg, bef = t.schritt(L, G, sichere_orte=ORTE)
        neu_befohlen += [b for b in bef if 100 in b.get("angriff", {}).get("einheiten", [])]
    pruefe(91, "normales Gehen (jede 2. Runde ein Feld weiter): kein neuer Befehl, kein Zickzack (%s)" % neu_befohlen, o and not neu_befohlen)
    # 9b. echt blockiert: drei Runden dasselbe Feld trotz Laufbefehl -> neuer Fluchtpunkt, nie zurueck in eine blockierte Richtung
    punkte = [t.warte.get(100)]
    for _ in range(2):
        o = punkte[-1]
        L[100].update(zustand=101, laufx=o[0] if o else 0, laufy=o[1] if o else 0)
        lauf = []
        for _ in range(3):
            erg, bef = t.schritt(L, G, sichere_orte=ORTE)
            lauf = lauf or [b["angriff"]["lauf"] for b in bef if "lauf" in b.get("angriff", {}) and 100 in b["angriff"]["einheiten"]]
            if lauf:
                break
        punkte.append(tuple(lauf[0]) if lauf else None)
    weit = lambda a, b: a and b and max(abs(a[0] - b[0]), abs(a[1] - b[1])) > 6
    pruefe(9, "zweimal blockiert (je 2 Runden auf demselben Feld): jedes Mal neuer Fluchtpunkt, nie zurueck %s" % punkte,
           bool(weit(punkte[1], punkte[0]) and weit(punkte[2], punkte[1]) and weit(punkte[2], punkte[0])))
    # 10. Leute im Weg: der ohne Arbeiter gewaehlte Punkt ist zugestellt (Arbeiter stehen/laufen dort) -> anderer Punkt
    def lauf_einer(L):
        t = neu()
        t.aufnehmen([100])
        t.schritt(L, G, sichere_orte=ORTE)
        return t.warte.get(100)
    basis = {100: einheit(73, 1, 190, 270), 501: einheit(73, 2, 192, 270), 502: einheit(73, 2, 192, 271)}
    frei = lauf_einer({k: dict(v) for k, v in basis.items()})
    L = {k: dict(v) for k, v in basis.items()}
    if frei:
        for i, k in enumerate((4, 7, 10)):                       # drei Arbeiter (Typ 3) auf der Strecke
            L[700 + i] = einheit(3, 2, 190 + (frei[0] - 190) * k // 15, 270 + (frei[1] - 270) * k // 15)
        L[710] = einheit(3, 0, 150, 300, laufx=190 + (frei[0] - 190) // 2, laufy=270 + (frei[1] - 270) // 2)   # laeuft dorthin
    zugestellt = lauf_einer(L)
    pruefe(10, "Arbeiter auf der Strecke nach %s: anderer Fluchtpunkt %s" % (frei, zugestellt), bool(frei and zugestellt and zugestellt != frei))
    # 11. bewachtes Ziel: 2 feindliche Nahkaempfer 6 Felder neben dem Gebaeude, wir allein 30 Felder weg -> nicht als Ziel
    t = neu()
    L = {100: einheit(73, 1, 170, 270), 501: einheit(24, 2, 206, 270), 502: einheit(24, 2, 206, 271)}
    t.aufnehmen([100])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    pruefe(11, "Ziel mit 2 Wachen, wir allein: kein Angriff darauf (Ziel %s)" % t.ziel.get(100), t.ziel.get(100) != 900)
    # 12./13. schlagende Arbeiter (Daniel 22:37): 1 feindliche Assassine + 2 Holzfaeller direkt neben ihm = 1,16 > 1 ->
    #         ausweichen; dieselben Holzfaeller 6 Felder weg schlagen nicht -> 1 gegen 1, kein Ausweichen.
    #         (12.10. 01:39: vorher 1 Speertraeger - unter Ascension ist er 0,2 Assassinen stark, Massstab NAH_GEFAHR)
    for nr, abst, soll in ((12, 1, True), (13, 6, False)):
        t = neu()
        L = {100: einheit(73, 1, 190, 270), 501: einheit(73, 2, 192, 270),
             601: einheit(3, 2, 190 + abst, 271), 602: einheit(3, 2, 190 + abst, 269)}
        t.aufnehmen([100])
        erg, bef = t.schritt(L, G, sichere_orte=ORTE)
        aus = any(z.startswith("AUSWEICHEN 100") for z in erg)
        pruefe(nr, "1 Assassine + 2 Holzfaeller %d Felder weg: ausweichen %s (soll %s)" % (abst, aus, soll), aus == soll)
    # 14./15. Heim nur, wenn stark genug: 3 Verfolger-Assassinen; zu Hause 2 Speertraeger (zu schwach) bzw. 3 Schwertkaempfer
    def fluchtziel(verteidiger_typ, anzahl):
        t = neu()
        L = {100: einheit(73, 1, 190, 270), 501: einheit(73, 2, 192, 270), 502: einheit(73, 2, 192, 271), 503: einheit(73, 2, 191, 272)}
        for i in range(anzahl):
            L[800 + i] = einheit(verteidiger_typ, 1, 140 + i, 269)
        t.aufnehmen([100])
        t.schritt(L, G, sichere_orte=ORTE)
        p = t.warte.get(100)
        return p, (min(max(abs(p[0] - h[0]), abs(p[1] - h[1])) for h in ORTE) if p else -1)
    schwach, staerke = fluchtziel(24, 2), fluchtziel(27, 3)
    abstand = getattr(A.Einzeln, "HEIM_ABSTAND", 25)
    pruefe(14, "Heim zu schwach (2 Speer gegen 3 Assassinen): Fluchtpunkt %s bleibt >= %d von der Burg weg (%d)" % (
        schwach[0], abstand, schwach[1]), schwach[0] and schwach[1] >= abstand)
    pruefe(15, "Heim stark (3 Schwertkaempfer): Fluchtpunkt %s naeher an der Burg (%d) als bei zu schwach (%d)" % (
        staerke[0], staerke[1], schwach[1]), staerke[0] and staerke[1] < schwach[1])
    # 16. Verfolger 12 Felder hinter ihm (ausserhalb 10, innerhalb FLUCHT_FREI 15), zu Hause nur Speer/Bogen -> NICHT zur Burg
    t = neu()
    L = {100: einheit(73, 1, 190, 270), 501: einheit(73, 2, 192, 270), 502: einheit(73, 2, 192, 271),
         801: einheit(24, 1, 140, 269), 802: einheit(22, 1, 141, 270)}
    t.aufnehmen([100])
    t.schritt(L, G, sichere_orte=ORTE)                            # Flucht beginnt
    L[100].update(x=175, y=268, zustand=106)                     # eingeholt? nein: Verfolger 12 hinter ihm, er steht
    for f, x in ((501, 187), (502, 187)):
        L[f].update(x=x)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    lauf = [b["angriff"]["lauf"] for b in bef if "lauf" in b.get("angriff", {}) and 100 in b["angriff"]["einheiten"]]
    d = min(max(abs(lauf[0][0] - h[0]), abs(lauf[0][1] - h[1])) for h in ORTE) if lauf else -1
    pruefe(16, "Verfolger 12 Felder hinter ihm, zu Hause nur Speer/Bogen: Fluchtpunkt %s bleibt >= %d von der Burg (%d)" % (
        lauf, getattr(A.Einzeln, "HEIM_ABSTAND", 25), d), lauf and d >= getattr(A.Einzeln, "HEIM_ABSTAND", 25))
    # 17. am Kartenrand steckengeblieben (raidzuerst_9): Zustand 1 (steht), Laufziel = eigenes Feld, Fluchtpunkt unerreichbar
    #     -> nach 2 Runden ohne Feldwechsel ein Fluchtpunkt in ANDERER Richtung (nicht immer wieder derselbe)
    t = neu()
    L = {100: einheit(73, 1, 190, 270), 501: einheit(73, 2, 192, 270), 502: einheit(73, 2, 192, 271)}
    t.aufnehmen([100])
    t.schritt(L, G, sichere_orte=ORTE)
    o = t.warte.get(100)
    L[100].update(x=180, y=268, zustand=1, laufx=180, laufy=268)
    for f, x in ((501, 191), (502, 191)):
        L[f].update(x=x)
    gesehen = []
    for _ in range(4):
        erg, bef = t.schritt(L, G, sichere_orte=ORTE)
        gesehen += [tuple(b["angriff"]["lauf"]) for b in bef if "lauf" in b.get("angriff", {}) and 100 in b["angriff"]["einheiten"]]
    pruefe(17, "steht 4 Runden fest (Zustand 1) mit Fluchtbefehl: wechselt die Richtung %s" % gesehen, len(set(gesehen)) >= 2)
    # 18. Im Kreis fuehren (T2, Daniel 22:49): zu Hause zu schwach, 2 Verfolger bleiben 10 Felder hinter ihm. 10 Runden lang
    #     laeuft er zu seinem Fluchtpunkt, die Verfolger folgen. Er soll in der Gegend kreisen (nie > 60 Felder vom Start,
    #     raidzuerst_9: geradeaus bis zum Kartenrand) und nie naeher als HEIM_ABSTAND an die Burg.
    t = neu()
    start = (190, 250)
    L = {100: einheit(73, 1, *start), 501: einheit(73, 2, 196, 250), 502: einheit(73, 2, 196, 251)}
    t.aufnehmen([100])
    weg_pkt = [start]
    for _ in range(10):
        erg, bef = t.schritt(L, G, sichere_orte=ORTE)
        ziel = t.warte.get(100)
        if not ziel:
            break
        x0, y0 = L[100]["x"], L[100]["y"]
        L[100].update(x=ziel[0], y=ziel[1], zustand=0, laufx=ziel[0], laufy=ziel[1])   # dort angekommen
        dx, dy = ziel[0] - x0, ziel[1] - y0
        lang = max(abs(dx), abs(dy), 1)
        for f, k in ((501, 10), (502, 11)):                              # Verfolger 10-11 Felder hinter ihm
            L[f].update(x=int(round(ziel[0] - dx * k / lang)), y=int(round(ziel[1] - dy * k / lang)))
        weg_pkt.append(ziel)
    weit = max(max(abs(p[0] - start[0]), abs(p[1] - start[1])) for p in weg_pkt)
    heim = min(min(max(abs(p[0] - h[0]), abs(p[1] - h[1])) for h in ORTE) for p in weg_pkt[1:]) if len(weg_pkt) > 1 else -1
    pruefe(18, "im Kreis: %d Fluchtpunkte, weitester %d Felder vom Start (soll <= 60), naechster an der Burg %d (soll >= %d): %s" % (
        len(weg_pkt) - 1, weit, heim, getattr(A.Einzeln, "HEIM_ABSTAND", 25), weg_pkt[1:]),
        len(weg_pkt) >= 8 and weit <= 60 and heim >= getattr(A.Einzeln, "HEIM_ABSTAND", 25))
    # 19. dieselbe Kreisflucht, aber 3 feindliche Bogenschuetzen stehen auf der Kreisbahn (205,280) -> kein Fluchtpunkt
    #     naeher als 12 Felder an ihnen (ohne Schuetzen lief der Kreis durch (207,279))
    t = neu()
    L = {100: einheit(73, 1, *start), 501: einheit(73, 2, 196, 250), 502: einheit(73, 2, 196, 251),
         521: einheit(22, 2, 205, 280), 522: einheit(22, 2, 206, 281), 523: einheit(22, 2, 204, 281)}
    t.aufnehmen([100])
    pkt = []
    for _ in range(10):
        t.schritt(L, G, sichere_orte=ORTE)
        ziel = t.warte.get(100)
        if not ziel:
            break
        x0, y0 = L[100]["x"], L[100]["y"]
        L[100].update(x=ziel[0], y=ziel[1], zustand=0, laufx=ziel[0], laufy=ziel[1])
        dx, dy = ziel[0] - x0, ziel[1] - y0
        lang = max(abs(dx), abs(dy), 1)
        for f, k in ((501, 10), (502, 11)):
            L[f].update(x=int(round(ziel[0] - dx * k / lang)), y=int(round(ziel[1] - dy * k / lang)))
        pkt.append(ziel)
    nah_schuetzen = min((max(abs(p[0] - 205), abs(p[1] - 280)) for p in pkt), default=-1)
    pruefe(19, "Schuetzen auf der Kreisbahn: naechster Fluchtpunkt %d Felder von ihnen (soll > 12): %s" % (nah_schuetzen, pkt),
           len(pkt) >= 8 and nah_schuetzen > 12)
    # 20. schnelle Runden (live_4: 2-4 Ticks je Runde): Runde alle 3 Ticks, er geht 1 Feld je 15 Ticks Richtung Fluchtpunkt
    #     -> nie "blockiert", kein neuer Befehl (vorher: blockiert nach 2 Runden = 6 Ticks, staendige Richtungswechsel)
    t = neu()
    L = {100: einheit(73, 1, 190, 270), 501: einheit(73, 2, 196, 270), 502: einheit(73, 2, 196, 271)}
    t.aufnehmen([100])
    t.schritt(L, G, sichere_orte=ORTE, tick=1000)
    o = t.warte.get(100)
    neu_bef, x = [], 190
    for i in range(1, 31):                                         # 90 Ticks, alle 3 Ticks eine Runde
        if i % 5 == 0:
            x -= 1                                                 # ein Feld je 15 Ticks
        L[100].update(x=x, zustand=101, laufx=o[0] if o else 0, laufy=o[1] if o else 0)
        for f in (501, 502):
            L[f].update(x=x + 6)
        erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=1000 + 3 * i)
        neu_bef += [b for b in bef if 100 in b.get("angriff", {}).get("einheiten", [])]
    pruefe(20, "Runden alle 3 Ticks, 1 Feld je 15 Ticks: kein BLOCKIERT, kein neuer Befehl (%d neue)" % len(neu_bef),
           o and not neu_bef)
    print("\n%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
