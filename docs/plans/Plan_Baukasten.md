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
4. **Raid aus dem Angriffszweig lösen:** Steuerung und Werbung der Raids stehen heute in `phase2` unter `if streitkolben:` und `if feldzug is not None:`. Deshalb muss auch `raid_frueh` `streitkolben=30` setzen. Mit `streitkolben=0` fielen Raids und Bierkette still aus. Danach Bestellung und Einsatz als ein Modul.
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

Absichtlich weggefallen ist in diesen Schritten nichts.

## Offen

- Erste Partie mit `raid_frueh` am 09.11.: nur Raid-Einheiten geworben, siehe `data/research/raid_frueh_20261109/Ergebnis_Raid_frueh.md`. Sie zeigt zwei Aufgaben für Schritt 4: eine gemeinsame Raid-Kasse, weil Assassine und Reiter dasselbe Gold ausgeben, und Sollzahlen, die mit dem Gold mitwachsen.
- Sollzahlen der Raids: Sklaven 5, Berittene 3 sind Startwerte, kein Messwert. Die Regler sind da, die Zahlen fehlen.
- Tiefe der Trennung: Schritt 3 macht 15 Klassen austauschbar. Was noch im Lenker steht, zeigt die Modulkarte, und jeder Umzug braucht eine eigene Probe.
