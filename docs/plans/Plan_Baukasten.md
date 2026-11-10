# Plan Baukasten: Alle Spielteile als Steckmodule (B-176)

Auftrag Daniel 09.11.2026: Alles, was Gehirn und Hände können, den Spielteilen zuordnen und als Steckmodule bauen, so dass mehrere Versionen gegeneinander antreten können. Zuerst das Early Game mit Raids, alles andere hintenan.

## Stand

Die Zuordnung und die Messwerte stehen in [Modulkarte.md](Modulkarte.md). Die Datei wird aus dem Code erzeugt, ein Test sperrt, dass sie veraltet, etwas auslässt oder etwas nennt, das es nicht gibt.

Der wichtigste Befund: Viele Teile sind schon eigene Klassen, aber fast jede wird anders aufgerufen, und vieles steht noch als Fließtext in `phase2`. Eine neue Version desselben Moduls lässt sich trotzdem tauschen, weil sie denselben Aufruf hat wie ihre Vorgängerin. Ein Modul durch ein ganz anderes zu ersetzen, geht erst mit einem gemeinsamen Aufruf.

Offene Einordnung für Daniel: Assassinen zählen zu Raid, weil der Lenker sie schon „Raid zuerst“ nennt und Plan_Gehirn sie unter frühen Raids führt.

## Wie die Module aussehen

- Paket `selfaware.baukasten`.
- **Modulkarte** (`karte.py`): Jedes Modul steht mit Spielteil, Name, Stelle im Code und Schaltern in einer Tabelle. Beziehung in beiden Richtungen: `module_von(teil)` und `teil_von(modul)`. Ihr Stand wird aus dem Quelltext gelesen.
- **Aufstellung** (`configs/aufstellungen/<name>.json`, Start mit `aufstellung=<name>`): nennt Schalter und Versionen. Mit `basis` baut sie auf einer anderen auf und muss jede Änderung unter `gruende` begründen, sonst startet sie nicht. Die Befehlszeile gilt vor der Datei. Die Mitschrift nennt jeden Schalter.
- **Steckplätze** (`aufstellung.Steckplaetze`): Der Lenker holt seine Klassen über `STECK.klasse("name")`. Ohne Eintrag läuft die Klasse von heute. Eine neue Version ist eine eigene Klasse, am einfachsten erbt sie von der alten, und steht in der Aufstellung unter `versionen`. Vor dem Start wird geprüft, ob sie alles anbietet, was die alte kann.
- **Formationen** (`formation.py`): reine Rechnung, von jedem Einsatz nutzbar. Heute nutzt sie der Vorstoß.
- **Scaling und Acceleration** sind Regler in der Aufstellung, siehe die beiden Abschnitte der Modulkarte. Neu für die Raids: `sklaven_soll`, `reiter_soll`.
- **Versionen gegeneinander:** `python -m selfaware.tools.experiments.aufstellung_vergleich --instanz 2 raid_frueh vorstoss_laptop` fährt die Aufstellungen nacheinander und stellt die Kennzahlen nebeneinander. Zusätzlich lässt `eins_gegen_eins` zwei Lenker gegeneinander spielen.

## Reihenfolge

1. **Bestellung** (B-177, Code fertig): Ein Tor für alle 9 Rekrutierstellen, `bestellung=raid` schaltet Angriff und Verteidigung ab.
2. **Ausweichen** (B-178, Code fertig): Zickzack heißt Ausweichen, ist ein Werkzeug für jeden Einsatz und läuft nur, wenn auf die Einheit geschossen wird.
3. **Aufstellung, Modulkarte, Steckplätze, Vergleich** (B-176, Code fertig).
4. **Raid als eigenes Modul** (B-179, Code fertig): `baukasten/raid.py` enthält `RaidBestellung` (was gekauft wird) und `RaidEinsatz` (was die Einheiten tun). Beide sind Steckplätze. Steuerung, Werbung und Bierkette stehen nicht mehr im Angriffszweig. Drei Aufstellungen trennen die Wirkung: `raid_frueh` (Reihenfolge wie bisher), `raid_kasse` (dazu eine Kasse: Sklaven, Schleuderer, Berittene, Assassinen), `raid_ohne_angriff` (dazu kein Feldzug und kein Streitkolben-Ziel, Schalter `ohne_angriff=ja`).
4b. **Kauf nach Wirkung und Nahkampf-Raid** (B-181, Code fertig, Daniel 10.11.: keine feste Reihenfolge, „nach Wirkung, schlaues Pathing, maximaler Effekt“): `baukasten/einheiten.py` kennt alle 18 Arten und den Lord (nur Verteidigung). `baukasten/wirkung.py` rechnet je Art, was sie gegen die sichtbaren Ziele bewirkt, aus Duellen, Partien und Spielwerten; Ungemessenes heißt Ersatz. `RaidBestellungNachWirkung` kauft je Runde die Art mit dem meisten Wert je Gold. `micro/tasks/nahkampf.py` führt bestellte Nahkämpfer einzeln: Ziel nach Wirkung, sicherer Weg, Angriff. Aufstellung `raid_wirkung`.
5. Danach Apfel, Brot, Bier, Waffen, dann Angriff und Verteidigung, je Modul ein eigener Schritt mit Partie.
6. `assassinen.py` in Raid und Angriff teilen.

## Was der alte Weg leistet (Regel P3.12)

Vor jedem Umzug steht hier je Modul, was es heute tut, und der Test dafür. Stand für Schritt 1 bis 3:

| Heute | Muss bleiben | Beleg |
|---|---|---|
| Ohne Schalter werben alle 9 Stellen wie bisher | `bestellung` hat als Standard „alle“ | Test: Standard erlaubt jede Art; Quelltext-Test: keine Werbestelle ohne Tor |
| Notwerbung nur, wenn die Rechnung sagt, dass die Truppen nicht reichen | unverändert hinter dem Tor | Tor steht vor dem alten Block, der Block bleibt |
| Bei Hunger keine Werbung | unverändert | Bedingung bleibt |
| Assassinen brauchen Posten, Gold, Bauern, Abstand | unverändert | Bedingung bleibt |
| Mit Kern geht jeder Sklaven-Befehl über den Kern | bleibt | `tests/test_brandtrupp.py` |
| Ausweichen endet beim Angriffsbefehl und bei Freigabe | bleibt | Kern-Tests, `tests/test_brandtrupp.py` |
| Die lange Befehlszeile des Laptop-Laufs | steckt vollständig in `vorstoss_laptop` | Test gegen die Mitschrift des Laufs |
| Der Lenker baut 15 Klassen selbst | ohne Aufstellung genau diese 15 | Test mit festen Namen; Test über den Syntaxbaum: kein direkter Bau mehr |
| Die Code-Kennung sieht alle Dateien | die import-Zeilen bleiben stehen | Test gegen `kennung.python_dateien()` |
| Die Mitschrift nennt den Startbefehl | ohne Aufstellung wie eingegeben, mit Aufstellung jeder Schalter | Test `startzeile` |
| Der Vorstoß stellt breit auf | dieselben Felder | Test mit festen Werten, `tests/test_vorstoss.py` |
| Raid steuert Vorstoß, Deckung, Brandtrupp, Reiter in dieser Reihenfolge | gleiche Reihenfolge in `RaidEinsatz` | Test mit Attrappen |
| Ein Fehler im Raid oder in der Bierkette beendet die Partie nie | `try` bleibt, jetzt auch um die Assassinen-Werbung | Test über den Syntaxbaum |
| Ohne Schalter läuft der Raid nur mit Feldzug | `raid_laeuft` | Test auf die Zeile |
| Assassine zuerst, Söldner nur in ungeraden Runden und nicht im Endspurt, jeder mit dem Gold vom Rundenanfang | `RaidBestellung` ist genau das, und `raid_frueh` nutzt sie | `tests/test_raid.py` |
| Assassine braucht Posten, Abstand, Ziele, Gold, Bauern, freien Planer, keine Löwen, keine offenen Höfe, keinen Hunger | Bedingungen stehen weiter im Lenker, das Ergebnis geht als `assassine_erlaubt` in die Bestellung | Bedingung bleibt |
| Wächter lassen Raid-Einheiten in Ruhe, Feldzug leiht Vorstoß-Schützen, Bericht am Ende | die Namen `brand`, `reiter`, `deckung`, `vorstoss` bleiben im Lenker | Zuweisung aus `raid_e` |
| Bierkette alle 5 Runden, nicht im Endspurt | gleiche Bedingung, außerhalb des Zweigs | Test über den Syntaxbaum |
| Im Feldzug greifen Assassinen den Lord nicht an | gilt auch mit `ohne_angriff=ja` | steht im selben Block |
| Starttruppen bleiben bei Wächtern und Vorstoß | Der Nahkampf-Raid nimmt nur, was für den Raid bestellt wurde | `tests/test_wirkung.py` |
| Ohne Aufstellung kauft der Raid wie bisher | Der Kauf nach Wirkung ist eine eigene Version, nur `raid_wirkung` steckt sie | Test auf die Aufstellung |

Absichtlich weggefallen ist in diesen Schritten nichts. Eine Kleinigkeit ändert sich auch ohne Aufstellung: Die Assassine wird jetzt nach der Steuerung derselben Runde bestellt, nicht davor.

## Offen

- Erste Partie mit `raid_frueh` am 09.11.: nur Raid-Einheiten geworben, siehe `data/research/raid_frueh_20261109/Ergebnis_Raid_frueh.md`. Sie zeigte zwei Aufgaben: die gemeinsame Raid-Kasse (B-179, gebaut, im Spiel noch nicht geprüft) und Sollzahlen, die mit dem Gold mitwachsen (B-180, offen).
- Kauf nach Wirkung: Europäische Arten brauchen Kaserne und Waffen und sind darum noch nicht kaufbar. Die Gebäuderate anderer Nahkämpfer ist ein Ersatz nach der Assassine. Ob Feuer auf Nachbarn überspringt, ist offen (einmal gemessen: nein) und deshalb nicht eingerechnet.
- Sollzahlen der Raids: Sklaven 5, Berittene 3 sind Startwerte, kein Messwert. Die Regler sind da, die Zahlen fehlen.
- Tiefe der Trennung: Schritt 3 macht 15 Klassen austauschbar. Was noch im Lenker steht, zeigt die Modulkarte, und jeder Umzug braucht eine eigene Probe.
