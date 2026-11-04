# -*- coding: utf-8 -*-
"""B-142: Urteil je Einzelpunkt nach Lauf F (02.11.2026 21:42). Die Urteile sind von Hand aus den Belegen geschrieben, die Rechnungen dazu stehen in punkte_rechnen*.py.

Schreibt Punkte_Lauf_F.md und punkte_urteil.json, traegt bestaetigte und widerlegte Punkte als live_ergebnis ins Funktionswissen ein,
legt die Feldluecken offen (feldluecken_lauf_f.csv), haengt sie an die Feldliste an und schreibt die Restliste nie_gesehen_lauf_f.csv.
Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_f_20261102/punkte_urteil.py
"""
import collections
import csv
import json
import os
import re

HIER = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(HIER, "..")
B = os.path.join(PLAN, "laeufe", "lauf_f_20261102_214240")
FW = os.path.join(HIER, "..", "..", "funktionswissen", "funktionen_spiel.jsonl")
LAUF = "Lauf F 02.11.2026 21:42, Instanz 2, Burgenbau, Liga-Balance"

B_, W_, G_, L_, S_, O_ = "bestaetigt", "widerlegt", "gemessen", "Lage fehlte", "gesehen", "offen"
U = {
    "P001": (L_, "Kein Bündnis im Burgenbau. Lauf K."),
    "P007": (G_, "Tabelle gelesen; Vergleich mit der KI braucht Lauf K."),
    "P014": (B_, "armySize fällt mitten im Takt auf 0 und steht danach wieder auf 18, 384 Wechsel."),
    "P016": (G_, "Alle 25 Waren handelbar. Mit dem Marktfenster nicht verglichen."),
    "P017": (G_, "Reihenfolge 12, 11, 13, 10, 9, 16, 2, 4, 6, 8, 19, 17, 21, 18, 20, 22, 23, 24, 14, 3, Ende -1."),
    "P018": (B_, "20 Einträge vor -1."),
    "P019": (B_, "Tabelle gelesen. Kauf aller Waren kostete -3.420 Gold, Verkauf brachte +1.610: beides stimmt auf das Gold mit der Tabelle (Verkauf: Preis je 5 Stück)."),
    "P020": (B_, "euroRecruitable und mercRecruitable alle 1, someCount44 = storedPopularityPercent = 9000."),
    "P021": (B_, "Lauf K: 25 von 25 Preisen gleich dem Burgenbau aus Lauf F, also nicht aus der Karte. Es sind die Liga-Preise."),
    "P023": (B_, "Kopie gleich der Preistabelle. Die Werte sind die der Liga, nicht die Grundwerte."),
    "P025": (G_, "Satz gelesen, die Liga hat ihn ersetzt."),
    "P026": (G_, "Satz gelesen, die Liga hat ihn ersetzt."),
    "P027": (G_, "aics[3]: 75, 110, 52, 1 statt Grundwert 10, 40, 0, 0. Liga-KI."),
    "P028": (G_, "aics[4]: 42, 130, 100, 2 statt 40, 100, 8, 2. Liga-KI."),
    "P029": (G_, "aics[5]: 0, 60, 40, 2 statt 5, 50, 50, 0. Liga-KI."),
    "P030": (G_, "aics[6]: 5, 0, 1, 1 statt 30, 30, 5, 1. Liga-KI."),
    "P031": (G_, "aics[7]: 39, 8, 9, 1 statt 0, 0, 120, 2. Liga-KI."),
    "P032": (G_, "aics[8]: 60, 0, 52, 1 statt 90, 3, 0, 2. Liga-KI."),
    "P033": (G_, "aics[9]: 84, 0, 17, 2 statt 30, 18, -999, 0. Liga-KI."),
    "P034": (G_, "aics[10]: 80, 107, 39 statt 10, 20, 0. Liga-KI."),
    "P035": (G_, "aics[11]: 74, 70, 190 statt 40, 90, 358. Liga-KI."),
    "P036": (G_, "aics[12]: 8, 1, 2 statt 16, 0, 0. Liga-KI."),
    "P037": (G_, "aics[13]: 20, 2, 1 statt 40, 0, 2. Liga-KI."),
    "P038": (G_, "aics[14]: 58, 100, 0 statt 50, 6, 10. Liga-KI."),
    "P039": (B_, "aics[15]: 10, 4000, 1, gleich dem Grundwert."),
    "P040": (B_, "aics[16]: 50, 12, 37, gleich dem Grundwert."),
    "P041": (G_, "Aus dem Speicher gelesen (Tabelle 0xb3eb34): UT_E_ARCHER, UT_E_XBOW, UT_E_PIKE, UT_E_SWORD, UT_A_ARCHER, UT_A_FIRETHROWER, UT_A_SWORDSMAN, gleich wie in der Programmdatei: ja. `punkte_rechnung5.txt`."),
    "P042": (G_, "28, 74, 22, 23, 70, 72, 76, 24, 26, 37, 71, 73, 25, 27, 75, 39, 58, 59, 60, 77."),
    "P046": (G_, "Ingenieure je Gerät 2, 3, 4, 4, 1, 2; Gerätetypen 39, 40, 58, 59, 60, 77."),
    "P048": (G_, "Tabelle gelesen. Der Vergleich zeigt: Die Liga ersetzt fast alle Sätze, siehe P027 bis P040."),
    "P052": (B_, "Lauf K: Alle 8 KI: Zähler 11 bis 24, Cooldown 0. Der Zweig ohne Eisen in Reichweite kam nicht vor."),
    "P053": (B_, "Lauf K: Nur Status 0 und 1. 1.634 von 1.634 Bau-Schritten liegen im 100x100-Feld ab dem Versatz. Bei den 593 Wand-Schritten ist `location` keine Kachel, sondern der Anfang in `locationsArray`; davon je Spieler 9 Felder geprüft, alle im Feld."),
    "P054": (G_, "Lauf K: Eisen in 62 Zellen, Summe 595; Felsbrocken in 147 Zellen, Summe 1.729; Öl 0. Mit den Vorkommen der Karte nicht verglichen."),
    "P056": (B_, "400, 300, 200, 160, 100, -1: absteigend mit Ende -1."),
    "P057": (G_, "Im ersten gelesenen Rahmen (Takt 1342) nur Nullen. Wann das Spiel sie füllt, ist offen."),
    "P058": (B_, "Die Sprungtabelle ab 0x4fa5e8 ist im Speicher gleich wie in der Programmdatei, UCP3 ändert hier nichts. `punkte_rechnung5.txt`."),
    "P059": (L_, "Kein Sumpffeld auf den gefahrenen Karten: Lauf F 0, Lauf K 0 Felder mit Bit 0x20000000."),
    "P061": (B_, "Beträge 0 oder 5."),
    "P065": (G_, "Gelesen, gleich wie in der Programmdatei. Türen 2,7 / 3,7 / 4,7 / 7,4 / 7,3 / 7,2 und gegenüber. Lagerstelle 0,8 / 8,0 / 0,-8 / -8,0. Lagerplatz 7,2 / 2,-5 / -5,0 / 0,7."),
    "P070": (B_, "Ganze Rangtabelle (2160 Byte) gleich wie in der Programmdatei, 0xb4c880 beginnt mit 10, 9, 5, 3 wie erwartet."),
    "P071": (B_, "Zeltart 190, 191, 193, 192, 194, an Platz 8: 358. Ingenieure 2, 3, 4, 4, 1, an Platz 8: 2. Gleich wie in der Programmdatei."),
    "P085": (G_, "Tabelle gelesen: 0, 0, 1, 0, 2, 0, 3, 0, ... Keine Flamme im Lauf."),
    "P086": (B_, "Lauf K: Art 83 ergibt die Ramme (9 Mal Art 59), Art 84 den Schild (8 Mal Art 60). Der Name BT_SIEGETOWER für 83 im Typ-Verzeichnis stimmt also nicht, BT_S_BATTERINGRAM schon. Art 82 baute keine KI. `punkte_rechnung_k.txt`."),
    "P087": (B_, "Zweiter Bogenmacher fertigt wieder Bogen (17): Das neue Gebäude wird mitgezählt."),
    "P088": (B_, "+0x2C8 war in 20.909 Lesungen je Gebäude immer 0. Der Sonderzustand kam nicht vor."),
    "P089": (B_, "Humpen sinken, Lieferung füllt auf, vor der ersten Lieferung 0."),
    "P090": (B_, "Formel stimmt bei allen 7 Stufenwechseln, Stufen -3 bis 0."),
    "P091": (B_, "Kauf bei vollem Waffenlager: Speere 11 und 11, Gold 95.255 und 95.255."),
    "P092": (L_, "Geld zurück gibt es laut Code nur in Siege That (`disbandUnit`), das kommt in unseren Partien nicht vor."),
    "P093": (S_, "Stufe 121 kommt vor, farmGrowState fehlt in der Feldkarte."),
    "P094": (B_, "Total 72. Ob die Einheiten dort stehen, ist nicht nachgerechnet."),
    "P095": (B_, "structureRelated1 72. Ob die Söldner dort stehen, ist nicht nachgerechnet."),
    "P096": (S_, "Stufen kommen vor, farmGrowState fehlt in der Feldkarte."),
    "P097": (B_, "Werte 0 bis 3, je Art die Zahl der Plätze."),
    "P098": (B_, "sleeping 0, 1, 0 bei beiden Bogenmachern. Die Bestände dabei sind nicht geprüft."),
    "P099": (B_, "Offene Plätze 0 am Ende der Bauern, einzeln nicht nachgezählt."),
    "P100": (L_, "Kein Gebäude beschädigt, die Felder gehören zur Anzeige."),
    "P101": (B_, "countWoodcutters 1 bei 1 Hütte."),
    "P102": (L_, "Karte ohne Pechvorkommen."),
    "P103": (B_, "someCount04 15 = Söldnerposten 5 + Kaserne 10, je Takt neu."),
    "P104": (B_, "someCount04 15 = Söldnerposten 5 + Kaserne 10, je Takt neu."),
    "P105": (B_, "1 bis 3: zwei Bogenmacher und ein Lanzenmacher."),
    "P106": (B_, "2: eine Schmiede und ein Rüstungsschmied."),
    "P107": (B_, "1 und 1 bei einer Bäckerei."),
    "P108": (B_, "1 und 1 bei einer Brauerei."),
    "P109": (L_, "Keine Nahrungsart gesperrt."),
    "P110": (B_, "Im Jahr sinken die Humpen in 263 von 273 Schritten genau alle 36 Takte, aleRate 36."),
    "P111": (L_, "Ölbrennerei steht, aber kein Ingenieur wurde zugewiesen."),
    "P112": (B_, "Zählt je Takt +1 bis 150, dann auf 0 (63 Rücksprünge im Jahr)."),
    "P113": (B_, "Zählt je Takt +1 bis 400, dann auf 0 (24 Rücksprünge im Jahr)."),
    "P114": (B_, "Zähler bis 400, dann 0, 3 Kühe."),
    "P115": (B_, "4 Pferde im Abstand von zusammen 3 x 551 Takten."),
    "P116": (L_, "Gold kam direkt, nicht über Startgold."),
    "P117": (W_, "vclock folgt nicht der Beliebtheit: Es ist die Zuzugsuhr. Sie läuft von 2000 bis 4000, je Takt um gathering_rate/4 (gemessen +9 bei Beliebtheit 90 bis 94, +10 ab 95). Über 4000 kommt ein Bewohner und sie fällt um 2000. Also 1 Bewohner je 8000/gathering_rate Takte. Kein Platz frei: Sie steht auf 4000."),
    "P118": (W_, "4 Pechgräben kosteten 2 Pech, nicht 1: 16 auf 15 beim ersten, 14 beim dritten."),
    "P119": (S_, "Je 13 Felder kosteten -1 und -3 Stein, die Zuordnung zu niedrig und hoch ist nicht geklärt."),
    "P120": (B_, "Offen 11 mit Timer 600 und abwärts, zu Timer -1. Danach wird der Zustand 12, siehe P132."),
    "P121": (S_, "Eisen kommt an (finalIronProduced 23), Zustände nicht nachgerechnet."),
    "P122": (S_, "Stein kommt an, Zustände nicht nachgerechnet."),
    "P123": (G_, "Lauf K: 2 Zelte der Feuerballiste, Art 54, Fortschritt bis 312, +1 je Takt."),
    "P124": (B_, "Lauf K: 9 Zelte, Art 80, Fortschritt höchstens 319, dann Katapult (6 Mal bis 40 Takte danach gesehen). +1 oder +2 je Takt."),
    "P125": (B_, "Lauf K: 12 Zelte, Art 81, Fortschritt höchstens 639, +1 je Takt, dann Trebuchet (9 Mal gesehen)."),
    "P126": (L_, "Art 82 baute keine KI in Lauf K."),
    "P127": (B_, "Lauf K: 10 Zelte, Art 83, Fortschritt höchstens 644, +2 je Takt, dann Ramme (9 Mal gesehen)."),
    "P128": (B_, "Lauf K: 12 Zelte, Art 84, Fortschritt höchstens 121, +1 je Takt, dann Schild (8 Mal gesehen)."),
    "P129": (B_, "currentGameMode 0, cooldownTimer höchstens 400."),
    "P130": (B_, "Mit Param1 50 genau die Hälfte: Bogenmacher (Liga 18 Holz, 100 Gold) gab 9 und 50, Galgen (40 Gold) gab 20."),
    "P131": (W_, "Bis 15 statt 6: Im Speicher steht 15 (`UpdateHunter`, UCP3). Gemessen: Jäger trägt bis 18, das ist 15 mal Produktivität. Fleisch im Lager +1 je Stück."),
    "P132": (B_, "gateState 11 dann 12, pathLinkageRelated2 0, 2, 1."),
    "P133": (B_, "Skala bestätigt: 100 angezeigt = 10000, 50 = 5000 (Spielcode). Mitten in der Wochenrechnung steht kurz bis 10375."),
    "P134": (G_, "Der Zähler liegt bei 0xb95f70 und wird nur von dieser Anzeige-Funktion gefüllt (`CountPlayerUnitsByType`, sie löscht ihn zuerst). Einträge 67 bis 69 sind 0. Der Vergleich mit einem bekannten Heer ist nicht gefahren."),
    "P135": (L_, "Anzeige, nicht gemessen."),
    "P136": (B_, "Monat höchstens 11, danach Jahr +1."),
    "P137": (B_, "Alte Kaserne 44 ist weg, neue 104."),
    "P138": (L_, "Bauanzeige, nicht gemessen."),
    "P139": (B_, "Code: unter 50 Stück 5, unter 100 Stück 10, unter 200 Stück 20, sonst 50. Gemessen: Holz 106 -20, Essen 60 -10, Stein 43 -5."),
    "P140": (L_, "Immer 0, 1 oder 4 Sorten. Das Werkzeug fand die 2 zufällig im Warenfeld."),
    "P141": (B_, "foodClockSpeed je Kopf bei Ration 0 bis 4: 0; 1,5; 3; 4,5; 6. Bei 40 Leuten und Ration 3 also 180."),
    "P142": (B_, "36 ab der ersten Woche, davor 30."),
    "P143": (W_, "Stufe +3 ergibt laut Speicher 76, nicht 70 (UCP3). Gemessen: +5 ergibt 60, +2 ergibt 84, -5 ergibt 180 (sonder10_g), dazu -1: 116, -2: 132, -3: 148 aus Lauf F."),
    "P144": (B_, "religionVar1 0 auf 1 bei der Kapelle."),
    "P145": (B_, "Formel bestätigt: je Woche Leute x Gold-Tabelle x 2,5 aufs Sammelfeld (Stufe 5: 58 Leute, +101), je Monat ein Zehntel aufs Gold. Die erwarteten 80 sind der Grundwert, die Liga gibt 70."),
    "P146": (B_, "Dieselbe Formel: Stufe 1, 54 Leute, +67 je Woche. Die erwarteten 80 sind der Grundwert, die Liga gibt 50."),
    "P147": (L_, "Bevölkerung nicht verringert."),
    "P148": (B_, "4 auf 3 beim Ritter."),
    "P149": (B_, "Statistik[Index-1] = Leute am Monatswechsel: 12 bei Index 3, 16 bei Index 4 und so weiter."),
    "P150": (B_, "Stufe 10: -750, Stufe 11: -1000 (Liga). Crowding blieb 0."),
    "P151": (B_, "3 von 3 Monaten: Gold +38, +111, +116 = lastMonthsIncomeTax. Bei Bestechung +3 -26 = -23."),
    "P152": (B_, "weekChanged alle 200 Takte."),
    "P153": (B_, "Steigt im Lauf um 1 je Schritt, in der Pause steht er, nachgelesen."),
    "P154": (L_, "Limit 1.160. Der gesetzte Wert steht im Log, in der Aufzeichnung blieb 1.160 und das Anwerben ging weiter (sonder19_g). Bis 1.160 Mann ist nicht gefahren."),
    "P155": (L_, "Wie P154: Das Limit war nicht zu erreichen."),
    "P156": (L_, "Nicht mit 3 und 4 Gold versucht. Die Liga verlangt 20."),
    "P157": (B_, "Mönch 10: Das ganze Anwerben von 18 Einheiten kostete -850, genau die Summe der Tabelle."),
    "P158": (B_, "Liga 25 statt 30: Das ganze Anwerben kostete -850, genau die Summe der Tabelle."),
    "P159": (B_, "11 mit Timer 600, zu mit Timer -1. Danach wird der Zustand 12, siehe P132."),
    "P160": (G_, "Spielbefehl 34 setzt taxesSetting: 2 auf 7, Takt 205 (sonder19_g). Die beiden Felder der Erwartung gehören zum Schieber, der nicht benutzt wurde, sie blieben 0."),
    "P161": (B_, "Rohwerte 0 bis 11."),
    "P162": (B_, "Rohwerte 0 bis 4."),
    "P163": (W_, "Kauf bei vollem Waffenlager über Befehl 38 wird abgelehnt, das Feld bleibt aber 0. Der Grund wird über diesen Weg nicht gesetzt."),
    "P164": (B_, "Alle Waren +5, Gold -3.420 = Summe von getBatchBuyPrice."),
    "P165": (B_, "Byte 0, 1, 0 beim Ein- und Ausschalten."),
    "P166": (B_, "Turm von 200 zurück auf 500 bei Takt 293, Holz -5 wie der Befehlswert (sonder19_g). Stein ist nicht zu sehen, der Bestand wird aus dem Lager neu gerechnet."),
    "P167": (G_, "Befehl 29 mit Param1 50: Rückgabe genau die Hälfte, siehe P130."),
    "P168": (B_, "Param0 Einheitentyp, Param1 Gebäude: 18 von 18 Einheiten erschienen."),
    "P169": (B_, "Param0 0 ist Kauf, 1 ist Verkauf."),
    "P170": (B_, "Spielbefehl 70, Werte Gruppe und Haltung, wirkt (Lauf S, Szene Haltung)."),
    "P171": (L_, "Kein Gerät entfernt."),
    "P172": (B_, "Spielbefehl 102 (0, x, y): barracksAssemblyPoints[0].x auf den Befehlswert bei Takt 209 (sonder19_g)."),
    "P173": (B_, "39,9 Takte je Sekunde im vollen Dorf."),
    "P174": (W_, "commandDelay steht im Einzelspiel auf 0, nicht auf 35. Vom Befehl bis zum Gebäude vergehen gemessen 2 bis 6 Takte."),
    "P175": (G_, "Zähler läuft 1 bis 50."),
    "P176": (B_, "Tor schließt: Außenfeld oben verliert Bit 0x10, unten Bit 1. Tor öffnet: Beide kommen wieder (sonder10, Takt 100 und 1.253)."),
    "P177": (L_, "Kein Tunnel. Lauf S."),
    "P178": (B_, "Platzkarte in der Probe: Käfig und Wachturm außerhalb des Burgbereichs zeigen Zeichen i, das ist Grund 18 = 0x12 (`probe_befehle_gefecht.txt`)."),
    "P179": (L_, "Keine Taste gedrückt, das Tempo kam über das Modul."),
    "P180": (L_, "Karte mit Wild."),
    "P181": (B_, "Lauf K: Unter der kritischen Beliebtheit steht die Steuer im Wochentakt auf 2: 1.056 von 1.058 Lesungen (Spieler 6 und 8, die einzigen unter ihrer Grenze). Die 2 anderen zeigen 3 bei Spieler 8, nicht einzeln nachgesehen."),
    "P182": (L_, "Keine KI. Lauf K."),
    "P183": (L_, "Keine KI. Lauf K."),
    "P184": (B_, "Lauf K: Schritt +1 (52 von 60 Wechseln), Höchstwert 100. Dazu -1 (8 Wechsel): `getTargetableBuildingForPlayerID` zieht ab."),
    "P185": (L_, "Kein Verbündeter. Lauf K."),
    "P186": (B_, "Lauf K: Stichprobe: Spieler 3 verkauft Ware 13 bei 56 auf 50, Grenze 52 mit Spielraum. In 54 Fällen fiel eine Ware über ihrer Grenze im Verkaufstakt; je Aufruf wird nur eine Ware verkauft, die übrigen gezählten Fälle sind Verbrauch im selben Takt."),
    "P187": (L_, "Kein Verbündeter. Lauf K."),
    "P188": (G_, "Lauf K: 12 von 47 neuen Warenwünschen im Wert +0x9c der KI, 15 weitere gehören zum Holz. Die anderen stammen aus anderen Wegen; `euroUnitAcquisitionFailReason` ist nicht mitgelesen, die Lage ist daher nicht eindeutig."),
    "P189": (B_, "Lauf K: `willBuy` wechselt nur im Tagestakt des Spielers: 764 von 768, sonst 0 von 38.065. Die 4 ohne Wechsel sind nicht einzeln nachgesehen."),
    "P190": (B_, "Tag 50, Woche 200, Monat 800 Takte."),
    "P191": (L_, "Keine KI. Lauf K."),
    "P192": (L_, "Kein Feindgebäude. Lauf K."),
    "P193": (L_, "Nicht versucht, Grenze 200 gelesen."),
    "P194": (B_, "Lauf K: `moatsOwned` gleich eigener Zählung der Grabenfelder in `moats[]`: 448 von 448 Monatstakten."),
    "P195": (B_, "Der Graben wurde fertig: stage 2, fillProgress 4."),
    "P196": (B_, "fillProgress 0 bis 4, dann stage 2."),
    "P197": (S_, "Immer 0, der Abwärtslauf war nicht zu sehen."),
    "P198": (G_, "Spielbefehl 41 (Feldnummer, 100): Das Mauerstück ist bei Takt 225 weg (sonder19_g). Der Stein ist nicht zu sehen, der Bestand wird aus dem Lager neu gerechnet."),
    "P199": (L_, "Kein Feindgebäude. Lauf K."),
    "P200": (B_, "3 Stein, 15 Felder verlangt: 7 Felder gebaut, also 2S+1 (sonder19_g)."),
    "P201": (L_, "Nicht im Gefecht versucht. Lauf K."),
    "P202": (B_, "Sechs Hütten 0, 1, 2, 3, 4, 5 in Bau-Reihenfolge."),
    "P203": (B_, "Steinbruch 55 zeigt auf Halde 56, Typ 21."),
    "P204": (B_, "stage 2, fillProgress 4."),
    "P205": (B_, "Spielbefehl 29 (Nummer, 100, uid): Hütte weg bei Takt 295 (sonder19_g)."),
    "P206": (B_, "Genau 36 Felder mit Bit 0x1000000 bei einer Getreidefarm."),
    "P207": (B_, "Genau 24 Felder mit Bit 0x2000000 bei einer Hopfenfarm."),
    "P208": (B_, "0, 1, 2, 3 bei drei Milchviehhöfen."),
    "P209": (L_, "Holz reichte."),
    "P210": (B_, "0 auf 224 nach dem Anwerben."),
    "P211": (B_, "tribes[].unitStance folgt dem Befehl (Lauf S, Szene Haltung): Werte 1 und 2 gesehen."),
    "P212": (B_, "Liga 50 statt 30: Das ganze Anwerben kostete -850, genau die Summe der Tabelle."),
    "P213": (L_, "Produktivität 120 gibt es in der Liga-Tabelle nicht."),
    "P214": (L_, "Kein Tunnel. Lauf S."),
    "P215": (O_, "Rückgabewert, nicht in der Aufzeichnung."),
    "P216": (B_, "Aus dem Zelt 20: Lauf K, 15 von 15 Katapulten und Trebuchets. Von mir gesetzte Katapulte haben 10 (sonder10_g)."),
    "P217": (B_, "count bis 2, count_2 18 nach 18 Anwerbungen."),
    "P218": (W_, "Ladung 12, nicht 8: Im Speicher steht 12 (`UpdateQuarryWorker`, UCP3)."),
    "P219": (B_, "healerCount 1."),
    "P220": (W_, "Füllstand steigt um 120 je Bier, nicht um 160: Die Liga setzt flagons_per_beer 120."),
    "P221": (S_, "Höchstens 16 Mütter und Kinder in Lauf F. Die Grenze 75 wurde nicht erreicht."),
    "P227": (B_, "Ladung 2 und 3, wie erwartet ab 2 bei Produktivität 100. Weizen +1 je Stück (21 Mal)."),
    "P228": (W_, "Hopfenbauer trägt im Einzelspiel bis 6, nicht 1."),
    "P229": (B_, "Ladung 3 und 4, im Burgenbau wie erwartet ab 3. Apfel +1 je Stück (66 Mal)."),
    "P240": (B_, "Höchstwert 8000."),
    "P241": (W_, "countSlingers2 zählt keine Schleuderer: Es steigt seit Takt 16.541 je Takt um 1 auf 32.261, ohne einen einzigen Schleuderer zu Beginn. Der Name ist falsch."),
    "P222": (B_, "Holz steigt je Stück um 1 (68 Mal, 2 und 3 sind mehrere in einem Rahmen). Der Holzfäller trägt 13 bis 15."),
    "P223": (S_, "Bogen und Armbrust steigen je Stück um 1. Das Holz je Durchlauf ist von anderen Verbrauchern nicht getrennt."),
    "P224": (B_, "Fleisch +1 je Stück (32 Mal). Ladung bis 18, siehe P131."),
    "P225": (W_, "Der Bruch füllt bis 12, nicht bis 8, siehe P218. Stein im Lager +1 je Stück (23 Mal), 2 und 3 sind mehrere in einem Rahmen."),
    "P230": (B_, "Käse +1 je Stück (42 Mal). Ladung 4 und 5: Im Speicher steht 4 statt 3 (`UpdateDairyFarmer`, UCP3)."),
    "P231": (B_, "Weizen -1 (60 Mal), Mehl +1 (61 Mal)."),
    "P232": (B_, "Mehl -1 (8 Mal), Brot +1 je Stück (36 Mal). Der Bäcker trägt 8 bis 10."),
    "P233": (B_, "Hopfen -1 (8 Mal), Ale +1 (8 Mal)."),
    "P234": (S_, "Piken steigen je Stück um 1. Das Holz je Durchgang ist von anderen Verbrauchern nicht getrennt."),
    "P235": (B_, "Schwert +1 je Stück (8 Mal), Keule 2 Mal."),
    "P236": (B_, "Eisenrüstung +1 (6 Mal), Eisen -1 (9 Mal)."),
    "P237": (B_, "Lederrüstung +1 je Stück, 2 sind mehrere in einem Rahmen. Der Gerber trägt 2 und 3."),
    "P239": (B_, "Eisen +1 je Stück (15 Mal). Der Träger trägt 2 und 3."),
}
STANDARD = {"gemessen": (G_, "Einmal gelesen, Werte in punkte.json."), "gesehen": (S_, "Feld ändert sich, nicht nachgerechnet."), "zahl passt": (S_, "Zahl kommt vor, Lage nicht geprüft."), "zahl weicht ab": (S_, "Zahl kommt nicht vor, Lage nicht geprüft."),
            "nicht gesehen": (L_, "Feld hat sich nicht geändert."), "nicht zuordenbar": (O_, "Kein Feld erkannt.")}
LIGA_ZEILEN = {"P019", "P023"}

punkte = json.load(open(B + ".punkte.json", encoding="utf-8"))["punkte"]
aus = []
for x in punkte:
    u, g = U.get(x["nr"], STANDARD[x["urteil"]])
    aus.append({"nr": x["nr"], "funktion": x["funktion"], "urteil": u, "grund": g, "lauf_f_werkzeug": x["urteil"], "spielart": x["spielart"]})
z = collections.Counter(a["urteil"] for a in aus)
with open(os.path.join(HIER, "punkte_urteil.json"), "w", encoding="utf-8") as f:
    json.dump({"lauf": LAUF, "zaehlung": z, "punkte": aus}, f, ensure_ascii=False, indent=0)

zeilen = ["# Einzelpunkte Lauf F", "", f"{LAUF}. Geschrieben von SRE aus den Belegen, Rechnungen in `punkte_rechnen*.py`.", "",
          "**Worte:** bestätigt und widerlegt heißen: Die Lage kam vor und die Rechnung ist gemacht. gemessen: einmal gelesen, Erwartung war \"notieren\". gesehen: Die Lage kam vor, das Feld änderte sich, nachgerechnet ist es nicht. Lage fehlte: kommt in Lauf K oder S. offen: von hier aus nicht zu beantworten.", "",
          "| Urteil | Punkte |", "|---|---|"] + [f"| {k} | {z[k]} |" for k in (B_, W_, G_, S_, L_, O_)] + [""]
for k, titel in ((W_, "Widerlegt"), (B_, "Bestätigt"), (G_, "Gemessen"), (S_, "Gesehen, nicht nachgerechnet"), (L_, "Lage fehlte"), (O_, "Offen")):
    zeilen += [f"## {titel} ({z[k]})", "", "| Punkt | Funktion | Beleg |", "|---|---|---|"]
    zeilen += [f"| {a['nr']} | `{a['funktion']}` | {a['grund']} |" for a in aus if a["urteil"] == k]
    zeilen.append("")
open(os.path.join(HIER, "Punkte_Lauf_F.md"), "w", encoding="utf-8").write("\n".join(zeilen))
print(dict(z), sum(z.values()))

# Funktionswissen: bestaetigt und widerlegt je Funktion
je = collections.defaultdict(list)
for a in aus:
    if a["urteil"] in (B_, W_):
        je[a["funktion"]].append({"lauf": LAUF, "punkt": a["nr"], "urteil": a["urteil"], "befund": a["grund"]})
roh = open(FW, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in roh else "\n"
neu, treffer = [], 0
for z_ in roh.split(nl):
    if not z_.strip():
        neu.append(z_)
        continue
    e = json.loads(z_)
    if e["name"] in je:
        alt = [x for x in e.get("live_ergebnis", []) if x.get("lauf") != LAUF]
        e["live_ergebnis"] = alt + je[e["name"]]
        treffer += 1
        z_ = json.dumps(e, ensure_ascii=False)
    neu.append(z_)
open(FW, "w", encoding="utf-8", newline="").write(nl.join(neu))
print("Funktionswissen ergaenzt:", treffer, "von", len(je), "Funktionen; ohne Treffer:", [k for k in je if not re.search(r'"name": "%s"' % re.escape(k), roh)][:6])

# Feldluecken und Restliste
from selfaware.tools.analysis.auge_feldkarte import TECHNIK  # noqa: E402

e = json.load(open(B + ".ergebnis.json", encoding="utf-8"))
A1 = [x["daten"] for x in e["proben"] if x["nr"] == "A1"]
luecken = {}
for d in A1:
    for y in d["luecken"]:
        k = (y["global"], y["feld"])
        a = luecken.setdefault(k, [0, y["erster_takt"]])
        a[0] += y["aenderungen"]
        a[1] = min(a[1], y["erster_takt"])
with open(os.path.join(HIER, "feldluecken_lauf_f.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["global", "feld", "aenderungen", "erster_takt", "art"])
    for (g, fe), (n, t) in sorted(luecken.items()):
        w.writerow([g, fe, n, t, "technik" if TECHNIK.search(g) else ("ohne_name" if "+0x" in fe else "mit_name")])
LISTE = os.path.join(PLAN, "zustand_felder.csv")
roh = open(LISTE, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in roh else "\n"
schon = {tuple(r[:2]) for r in ((z_.split(";")[1], z_.split(";")[2]) for z_ in roh.split(nl)[1:] if z_.count(";") >= 2) for r in [r]}
dazu = []
for (g, fe), _ in sorted(luecken.items()):
    if TECHNIK.search(g) or (g, fe) in schon:
        continue
    dazu.append(f"{g};{g};{fe};lauf_f;0;;nein;{'ja' if '+0x' in fe or 'field' in fe or 'Unk' in fe else 'nein'}")
if dazu:
    open(LISTE, "w", encoding="utf-8", newline="").write(roh.rstrip("\r\n") + nl + nl.join(dazu) + nl)
print("Feldluecken", len(luecken), "davon Technik", sum(1 for k in luecken if TECHNIK.search(k[0])), "neu in der Liste", len(dazu))
A2 = next(x["daten"] for x in e["proben"] if x["nr"] == "A2")
with open(os.path.join(HIER, "nie_gesehen_lauf_f.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["global", "feld"])
    for y in A2["nie"]:
        w.writerow(y if isinstance(y, list) else [y])
print("nie gesehen", len(A2["nie"]))
