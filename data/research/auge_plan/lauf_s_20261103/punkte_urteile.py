# -*- coding: utf-8 -*-
"""B-142 Lauf S: Urteil je Einzelpunkt, von SRE aus den Rechnungen punkte_rechnung1 bis 5, belege_sonderfaelle.txt und den .regeln.json. Schreibt Punkte_Lauf_S.md und prueft, dass kein Punkt fehlt.

  python data/research/auge_plan/lauf_s_20261103/punkte_urteile.py
"""
import collections
import json
import os

HIER = os.path.dirname(os.path.abspath(__file__))
B, W, T, G, L, O = "bestätigt", "widerlegt", "teils", "gemessen", "Lage fehlte", "offen"
U = {
    "P297": (W, "7 von 7 Giftwolken: logicalState 3 nach 828 Takten, nicht 808. Im Code läuft ab rng_2 800 eine Ausblendung, sie dauert 28 Takte statt der angenommenen 8."),
    "P298": (B, "Solange die Hütte brennt: someTracker 1 mit Zähler 0 in 24.785 von 24.785 Rahmen, nie 2. Danach steigt erst der Zähler, dann 2 (1.596 Rahmen), also nicht sofort. Neue Feuer: 240 von 309 haben einen Nachbarn mit Stufe plus 1, 51 einen anderen, 18 keinen."),
    "P299": (B, "4 von 4 Gräbern: Flag 2 im selben Takt wie Zustand 3 (1.001, 1.012, 1.003, 1.005)."),
    "P300": (B, "Werkzeug: Zahl passt. Dazu sonder1: 3 Gruben, 3 x 18.000, je 24 Takte auseinander."),
    "P301": (B, "Abklingzeit der Hütten bis Takt 360. 3 Feuerstrahlen flogen davor, fireDuration blieb 0 bis Takt 553. Beides zugleich in 0 Rahmen."),
    "P302": (L, "Der Laufbefehl auf den großen Turm wirkte nicht, die Einheit blieb unten stehen (sonder8). hasUnitsOntop blieb in diesem Versuch 0."),
    "P303": (W, "Bei einem Feind 24 und 26 Felder vor dem Tor geschah in 4.500 Takten nichts (sonder8), die Grenze 25 stimmt so nicht. Reaktion kam bei 3 bis 16 Feldern. gateState2 springt auf 100, nicht auf 1.200. Auf die Torfelder kam der Feind nicht, sein Laufbefehl wirkte nicht."),
    "P304": (T, "21 Tore: pathLinkageRelated2 0, 1, 2 mit gateState 12, von 1 auf 2 in 27 bis 50 Takten, meist 47 oder 48. gateState 10 kam in keinem Rahmen vor, nur 0 und 12. Reaktion bei 3 bis 16 Feldern, bei 24 keine. Entwarnung und Durchgang fehlen."),
    "P305": (O, "Das Feld steht nicht in der Aufzeichnung."),
    "P306": (O, "Einheiten fielen durch Gegner, finalKillMatrix änderte sich in keinem Lauf, auch nicht bei Spielende. Vermutlich erst beim Ergebnisbildschirm, nicht nachgesehen."),
    "P307": (L, "Kein Gefecht 2 gegen 1."),
    "P308": (T, "Das Nachladen gilt laut Code nur für die KI (isAIPlayer). Gemessen beim Menschen: 200 Stein im Lager, Munition bleibt 0, kein Schuss mehr (sonder8_g). Die +20 der KI sind nicht gefahren."),
    "P309": (O, "Spielbefehl 86 mit dem Trupp abgesetzt (Log), 200 Stein im Lager: Munition blieb 10, Stein unverändert. Warum, ist ungeklärt."),
    "P310": (L, "Kein Mausklick, unser Laufbefehl geht über Anweisung 17."),
    "P311": (G, "Param0 Gruppe, Param1 Anweisung, Param2 und 3 das Ziel (Nummer und uid, x und y oder Feldnummer), Param4 0. In allen Läufen so benutzt, auch Zuschütten wirkte mit 0, das Menü sendet dort 1000."),
    "P312": (L, "Anderer Spielmodus."),
    "P313": (B, "3 von 3 Läufen, davon einer mit echtem Töter: Feld des Gegners wird 1, gameOver 1, playerIsAlive[1] = 1 und [2] = 0, rund 305 Takte nach dem Sterben des Lords."),
    "P314": (L, "5 Gegner liefen quer am brennenden Pech vorbei, bis 1 Feld ans Feuer, auf kein Feuerfeld (sonder9_g). counter und field312 blieben 0."),
    "P315": (B, "(Wert, Anzahl) = (12, 3) bei 3 Speerträgern, (32, 8) bei 8, (16, 4) bei 4 lebenden. Wert 4 je Speerträger."),
    "P316": (B, "Editor, nahkampf: 45 Felder +3, 356 +2, 705 +1. Gefecht, nahkampf_g: 0 Änderungen bei Toten von Menschen. In beschuss_g 3 Fälle mit genau diesem Muster, wer dort starb, ist nicht zugeordnet."),
    "P317": (B, "2 von 2 Leitern: Richtung 2, Blick des Trägers 2."),
    "P318": (B, "schlacht_20: Trupp mit Schläger, Anteil über 10 in 1.384 von 1.412 Rahmen, die übrigen 28 mit Anteil 0."),
    "P319": (L, "Keine KI in Lauf S, gehört zu Lauf K."),
    "P320": (L, "Keine KI in Lauf S."),
    "P321": (B, "sonder5_g, 2 von 2: Zustand 2 bei Takt 501, 3 bei 526, weg bei 729. Auf 25 Takte genau."),
    "P322": (B, "Mitte der Mauer: Schaden +20, Höhe -20, erster Treffer -40. Ende (1 Nachbar): +30, 1,5-fach. Kreuzung (3 Nachbarn): Pikenier 2 statt 5, also halb, abgerundet."),
    "P323": (W, "Öl beim Träger ab Takt 361 bis 370, eigener Trupp, Haltung aggressiv, defensiv und stehen, ein Feind 2 bis 3 Felder daneben: In keiner Haltung ein Wurf, Anweisung blieb 3. Der Feind erschlug den Träger (Trupp weg ab Takt 1.182 bis 1.190). Ob der Code beim Menschen überhaupt gerufen wird, ist nicht nachgelesen."),
    "P324": (B, "Speerträger auf 39 Feldern zählt, Bogenschütze auf 41 nicht: Wert 4 ab Takt 195 (sonder8_g, 2 Läufe). Vorher: 6 Bogenschützen 36, 8 Speerträger 32."),
    "P325": (L, "Der Schwertkämpfer 2 Felder neben dem Feind kämpfte beim Marschbefehl (Takt 150) noch nicht. So kam die Lage nicht zustande."),
    "P326": (W, "6 Schwertkämpfer: Zielfelder eng um den Punkt, kleinster Abstand 1 (schräg), größter 3. Nicht 2 auseinander."),
    "P327": (B, "Anteil zwischen 0 und 100, bei Kampf über 0."),
    "P328": (B, "Gebäudeangriff: Rammen mit 1, 2, 3 Mann bleiben stehen, nur die mit 4 fährt und schlägt (sonder8)."),
    "P329": (T, "Zähler +1 je Takt, field93 läuft ab 51 bis 59 und fällt auf 0. Der Abstand zur Leit-Einheit ist nicht gemessen."),
    "P330": (T, "Eben: 19 Arten, berechnet gleich movementSpeed (Werte 1, 2, 3). Einen Hang (8 Höhe auf 14 Felder) gab es auf der Karte nicht."),
    "P331": (L, "Rush-Schutz nicht eingestellt."),
    "P332": (L, "Angstfaktor nicht geändert."),
    "P333": (B, "10 von 10 Wechseln im Fenster (Lastverteiler 12, 13, 14, 103, 163). Der Teil über Fernkämpfer ist nicht getrennt geprüft."),
    "P334": (W, "Der Zähler steigt nicht je Ingenieur, er springt: Schild 0 auf 1, Katapult 0 auf 2, Trebuchet 0 auf 3, Belagerungsturm 0 auf 4."),
    "P335": (B, "2 von 2: Zustand 3 ab Takt 136."),
    "P336": (B, "Werkzeug: Zahl passt."),
    "P337": (W, "Mit zu wenig Ingenieuren bleibt das Feld 0, in 5 Gerätearten mit 1 Mann zu wenig. Der Ingenieur wartet 2 Felder daneben."),
    "P338": (L, "Der Laufbefehl auf den Wachturm wirkte nicht: 8 von 8 blieben unten (sonder8). Die Obergrenze ist so nicht geprüft."),
    "P339": (W, "Beim Angriffsbefehl bleibt huntedBy 0 (19 von 19 Zielen, reichweite). Bei Zielen, die der Hund selbst wählt, geht es von 0 auf 1."),
    "P340": (B, "16 Brennende in 4 Szenen: Besitzer 0 und dying 1 in allen Rahmen."),
    "P341": (B, "Takt 39: Zähler 1, Schild von Zustand 6 auf 0, Ingenieur 109 (0x6D)."),
    "P342": (B, "Eigenes Katapult, nicht gegnerisch: 10 Schüsse, Munition 0, letzter bei Takt 1.695, danach keiner bis 1.978."),
    "P343": (B, "Ziel im geschlossenen Mauerring: Die Einheit bleibt stehen, sie verschwindet nicht (sonder8)."),
    "P344": (B, "Mit Anweisung 23: Zustand 6, dann 0 mit Bemannung 4, fährt Takt 415 bis 698, dann Zustand 8 und 9, Bemannung 0, neues Gebäude Art 69 bei Takt 699 (sonder8)."),
    "P345": (W, "125 je Treffer, 12 von 12 Treffern am Tor (1.500 Leben), rund alle 80 Takte, dazu Hütte und Turm. Der Code übergibt 50. Woher der Faktor kommt, ist nicht nachgesehen."),
    "P346": (B, "11 von 11 Nahkämpfern: erster Schlag bei 1,6 bis 2,0 Feldern."),
    "P347": (B, "Aggressiv auf 24 Felder: -220 und -221. Defensiv auf 4: -59 und -60. Das passt zu -30 minus Abstand in Mikro (192 und 32), bis auf 3."),
    "P348": (B, "6 von 6 Steigern: climbingState 1 bis 5, je 96 Takte, field219 höchstens 95."),
    "P349": (B, "Frame steigt bis 23, dann 0. Zustand 4: 5 x 50 Schaden bei Frame 60 bis 64, Ende bei 65. Die Höhe steigt im Gang von 8 auf bis 22, die einzelnen Schritte 6, 12, 18, 24 kann das Raster von 25 Takten nicht zeigen."),
    "P350": (L, "Kein Steinbruch."),
    "P351": (B, "Weit weg sitzen sie: 21.411 Rahmen über 400. Fast alle Wechsel zum Hinsetzen liegen an der Grenze (902 bei 390 bis 399, 17 bei 400 bis 409), dort wechselt es ständig."),
    "P352": (G, "Im Marsch kein Schuss, bei beiden Armbrustschützen. Am Ziel je 6 Schüsse, alle 228 Takte, auch mit Haltung stehen (sonder8)."),
    "P353": (B, "Speerträger: Mauer 2 je Schlag, alle 100 Takte. Hütte 10, Tor 2. Zu 8 und 3 aus dem Code passt das nicht, die Rangfolge schon."),
    "P354": (B, "Pikenier: Mauer 5 je Schlag, 15 Schläge je Stück. Turm 10 (50 Schläge), Tor 5 (300 Schläge). Die Mauer fällt also am schnellsten."),
    "P355": (B, "Keulenträger: Mauer 5 je Schlag, Hütte 80, Tor 5. Die Werte weichen von 35 und 4 ab."),
    "P356": (B, "Schwertkämpfer: Mauer 10 je Schlag (8 Schläge je Stück), Hütte 100, Tor und Turm 10. Die Werte weichen von 70 und 6 ab."),
    "P357": (B, "Ritter: Mauer 15 je Schlag (5 Schläge je Stück), Hütte 100, Tor und Turm 10."),
    "P358": (L, "Keine Kathedrale."),
    "P359": (B, "Verbrauch gleich Schüsse: 10 von 10, 7 von 7 bei 5 Katapulten."),
    "P360": (B, "Verbrauch gleich Schüsse: 5 von 5, 3 von 3, 1 von 1. Der Kuhwurf lässt die Munition unverändert."),
    "P361": (B, "11 Salven mit je 7 Geschossen."),
    "P362": (B, "8 Ritter töten den Lord (Takt 889): Spieler 1 bekommt 1.000 Gold, 25 % von 4.000, bei Takt 890. Das Gold von Spieler 2 bleibt gleich (lord2_g)."),
    "P363": (B, "Werkzeug: Zahl passt."),
    "P364": (B, "Bei 8 Feinden wechseln die Hunde bei Takt 8 bis 33 von 0xD2 auf 109, bei 3 Feinden nicht."),
    "P365": (W, "Das Feld zählt nicht die lebenden, es summiert sie je Takt: 720 nach 10 Takten mit 72 Bogenschützen, am Ende 22.280 bei 0 lebenden."),
    "P366": (W, "Sklave: geht an die Mauer, kein Schaden in 4.500 Takten. Tor und Turm 1 je Schlag, Hütte nichts."),
    "P367": (W, "Assassine: nimmt den Mauerbefehl nicht an, geht nicht hin, kein Schaden. Hütte 75, Turm 5, Tor 3 je Schlag."),
    "P368": (B, "Arabischer Schwertkämpfer: Mauer 10 je Schlag, alle rund 190 Takte. Hütte 100, Tor und Turm 10."),
    "P369": (B, "Werkzeug: Zahl passt."),
    "P370": (L, "Assassinen standen in vielen Szenen, aber kein KI-Angriff. Die Felder blieben 0."),
    "P371": (B, "Schießt auch im Laufen: Schüsse bei Takt 120, 218, 320, alle 92 bis 102 Takte. Im Stand alle 77 bis 79 (sonder8)."),
}
WORTE = (W, B, T, G, L, O)
FEHLT_TEXT = [("Oben auf einen Turm: Der Laufbefehl wirkt nicht, der Weg über Mauer oder Treppe fehlt noch", "P302, P338"), ("Tor: Feind auf den Feldern, Entwarnung, Durchgang", "P304"), ("Trupp mit einem, der wirklich kämpft", "P325"), ("Über ein Feuerfeld laufen", "P314"), ("Hang", "P330"), ("KI oder anderer Modus", "P307, P308, P310, P312, P319, P320, P331, P332, P350, P358, P370")]


def schreiben():
    d = json.load(open(os.path.join(HIER, "punkte_lauf_s.json"), encoding="utf-8"))
    p = {x["nr"]: x for x in d["punkte"]}
    assert set(p) == set(U), (set(p) ^ set(U))
    z = collections.Counter(u[0] for u in U.values())
    roh = open(os.path.join(HIER, "punkte_lauf_s.txt"), encoding="utf-8").read()
    aus = ["# Punkte Lauf S", "", "75 Punkte der Checkliste (Abschnitt Lauf S). Das Werkzeug `auge_punkte` sagt nur, ob sich ein Feld ändert (`punkte_lauf_s.py`, `punkte_lauf_s.txt`, 38 Aufzeichnungen). Die Urteile hier sind je Punkt gegen die Erwartung gerechnet: `punkte_rechnen1.py` bis `punkte_rechnen7.py`, Ausgaben in `punkte_rechnung1.txt` bis `punkte_rechnung7.txt`, dazu `belege_sonderfaelle.txt` und die `.regeln.json`. Die Tabelle erzeugt `punkte_urteile.py`.", "", "**Worte:** bestätigt und widerlegt heißen: Die Lage kam vor und die Rechnung ist gemacht. teils: Ein Teil ist gerechnet, der Rest der Lage fehlte. gemessen: Erwartung war nur „notieren“. Lage fehlte: Die Lage kam in Lauf S nicht vor. offen: Lage kam vor, Feld nicht lesbar oder ungeklärt.", "", "| Urteil | Punkte |", "|---|---|"]
    for w in WORTE:
        aus.append(f"| {w} | {z[w]} |")
    aus += ["", "## Was die Lauf-S-Lagen noch brauchen", "", "| Versuch | Punkte |", "|---|---|"]
    aus += [f"| {a} | {b} |" for a, b in FEHLT_TEXT]
    for w in WORTE:
        aus += ["", f"## {w.capitalize()} ({z[w]})", "", "| Punkt | Funktion | Beleg |", "|---|---|---|"]
        aus += [f"| {n} | `{p[n]['funktion']}` | {U[n][1]} |" for n in sorted(U) if U[n][0] == w]
    aus += ["", "## Gesamtproben an drei Szenen", "", "| Probe | Punkt | Einzel Gefecht | 1.000 gegen 1.000 |", "|---|---|---|---|", "| A1 Felder außerhalb der Liste | 241 | 10 | 3 |", "| A3 Takte | Tempo 200, nicht streng | Tempo 100: 848 fehlen, 782 gemischt. Das Werkzeug schreibt „widerlegt“, weil es Tempo 100 als streng behandelt; die Szene war absichtlich nicht streng | Tempo 1000, nicht streng |", "| A4 Lesen je Takt, Median und Höchstwert | 1,2 und 15,3 ms | 2,6 und 14,6 ms | 0,6 und 15,3 ms |", "| A7 Zufallsfolge passt zur Tabelle | 2.315 von 2.315 | 5.120 von 5.120 | **2.173 von 2.174** |", "| A10 Platzwechsel ohne Verstoß | 7.776 | 17.912 | 9.745 |", "", "A1: Die ersten 14 der 241 Felder gehören zum Befehlsring `DAT_GameCommand...`, weil hier viele Befehle liefen. Alle 241 sind nicht einzeln angesehen. A7: Der eine Fall auf Tempo 1000 ist nicht geklärt, vermutlich ein Rahmen über die Taktgrenze."]
    with open(os.path.join(HIER, "Punkte_Lauf_S.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(aus) + "\n")
    print("geschrieben", dict(z), "Summe", sum(z.values()))
    print("Werkzeug:", d["zaehlung"])


if __name__ == "__main__":
    schreiben()
