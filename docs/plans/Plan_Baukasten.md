# Plan Baukasten: Alle Spielteile als Steckmodule (B-176)

Auftrag Daniel 09.11.2026: Alles, was Gehirn und Hände können, den Spielteilen zuordnen und als Steckmodule bauen, so dass mehrere Versionen gegeneinander antreten können. Zuerst das Early Game mit Raids, alles andere hintenan.

## Stand (gemessen 09.11.)

`src/selfaware/runtime/live/erstes_spiel.py` hat 3.801 Zeilen und rund 90 Schalter, die Funktion `phase2` allein 1.460 Zeilen. 14 Teile sind schon Klassen mit `schritt`, der Rest steht als Fließtext in `phase2`. Einheiten werden an 9 Stellen rekrutiert, keine davon kennt die Art der Bestellung.

## Die Zuordnung

| Spielteil | Was es heute gibt | Stelle | Zustand |
|---|---|---|---|
| **Apfelwirtschaft** | Plantagen, Nahrungswahl, Packen und Mischen der Höfe | `macro/nahrungswahl.py`, `farmen_mischen.py`, `farmen_packen.py`, `ertragsplaner.py`, Teile von `wirtschaft.py` | eigene Dateien, aber nach Lage verstreut |
| **Brotwirtschaft** | Weizen, Mühle, Bäcker | `macro/brotbau.py`, `nahrungsmodell.py` | Klasse |
| **Bierwirtschaft** | Hopfen, Brauerei, Schenke | `macro/bierkette.py` | Klasse |
| **Waffenwirtschaft** | Eisen, Pech, Schmiede, Gerber | `Produktion`, `LederKette`, `ruestung_kaufen`, `waffenlager_*` in `erstes_spiel.py` | im Lenker |
| Grundwirtschaft | Holz, Stein, Häuser, Lager, Markt, Beliebtheit | `macro/wirtschaft.py`, `aufbau_planer.py`, `eroeffnung.py`, `haushalt.py`, `kornring.py` (Schutz), Funktionen im Lenker | gemischt |
| **Bestellung Raid** | Sklaven (A_SLAVE 71), Berittene Bogenschützen (A_HARCHER 74), Schleuderer (A_SLINGER 72), Assassinen (A_ASSASSIN 73) | `raids.werbung`, Lenker Zeile 432 und 3052 | Stellen verstreut |
| **Bestellung Angriff** | Streitkolbenkämpfer (E_MACEMAN 26), Heer aus Schwertkämpfern und Bogenschützen (75, 70) | `ruestung_kaufen`, `anwerbewelle`, Schub, Heer-Werbung im Lenker | im Lenker |
| **Bestellung Verteidigung** | Notwerbung | Lenker Zeile 2529 | im Lenker |
| Einsatz Raid | Brandtrupp, Reiterjagd, Deckung, Vorstoß, Assassinen beim Raiden | `micro/tasks/raids.py`, `vorstoss.py`, `assassinen.py` | Klassen |
| Einsatz Angriff | Feldzug, Lord-Anlauf der Assassinen | `feldzug.py`, `assassinen.py` | Klassen, `assassinen.py` hat 2.880 Zeilen und mischt Raid und Angriff |
| Einsatz Verteidigung | Wächter, Lordwache, Fallenwache, Kornring, Burggraben | `waechter.py`, `lordwache.py`, `fallenwache.py`, `kornring.py` | Klassen |
| **Werkzeugkasten** (für alle Einsätze) | Ausweichen, breite Aufstellung, Stapeln | Kern `ausweichen.rs`, `Vorstoss._aufstellung`, `assassinen.py` | teils fest in einem Einsatz verbaut |
| **Scaling** | Sollzahlen, Heereskasse, Ziel der Produktion, Bevölkerungsziel | über alle Dateien als Schalter und Konstanten | nicht vorhanden als eigenes Teil |
| **Acceleration** | Eröffnung, Reihenfolge des Aufbaus, Kausal-Entscheider | `eroeffnung.py`, `aufbau_planer.py`, `learning/kausal.py` | nicht vorhanden als eigenes Teil |
| Hände | Befehlsweg, Auftragsbuch, Kern | `execution/kernweg.py`, `auftragsbuch.py`, Kern `haende.rs`, `leitung.rs` | sauber getrennt |
| Augen | Lagebild, Weltbild des Kerns | `runde_lesen`, Kern `welt.rs`, `beschuss.rs`, `feuer.rs` | sauber getrennt |

Offene Einordnung für Daniel: Assassinen zählen hier zu Raid, weil der Lenker sie schon „Raid zuerst“ nennt und Plan_Gehirn sie unter frühen Raids führt.

## Wie die Module aussehen

- Paket `selfaware.baukasten`.
- **Modulkarte:** Jedes Modul steht mit Spielteil, Name, Version, Schaltern und Tests in einer Tabelle. Beziehung in beiden Richtungen: Das Modul nennt seinen Spielteil, der Spielteil listet seine Module.
- **Aufstellung:** Eine Datei legt fest, welche Module in welcher Version mit welchen Reglern laufen (`aufstellung=raid_frueh`). Sie ersetzt die lange Schalterliste und steht in der Mitschrift jeder Partie.
- **Scaling und Acceleration** sind Regler je Modul in der Aufstellung, keine verstreuten Konstanten.
- **Versionen gegeneinander:** Zwei Aufstellungen fahren nacheinander dieselbe Partie, das Werkzeug legt die Kennzahlen nebeneinander. Zusätzlich lässt `eins_gegen_eins` zwei Aufstellungen gegeneinander spielen.

## Reihenfolge

1. **Bestellung:** Ein Tor für alle 9 Rekrutierstellen, `bestellung=raid` schaltet Angriff und Verteidigung ab.
2. **Ausweichen:** Zickzack heißt Ausweichen, ist ein Werkzeug für jeden Einsatz und läuft nur, wenn auf die Einheit geschossen wird.
3. **Aufstellung und Modulkarte:** Schalter in Aufstellungen bündeln, Partien damit starten, zwei Aufstellungen vergleichen.
4. **Raid als erstes echtes Modul:** Bestellung und Einsatz aus dem Lenker ziehen.
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
| Alte Schalter wie `produktion=ja` | gelten weiter, die Aufstellung setzt nur dieselben Schalter | Test: Aufstellung ergibt genau die Schalterliste |

Absichtlich wegfallen soll in diesen Schritten nichts.

## Offen

- Sollzahlen der Raids: Sklaven 5, Berittene 3 sind Startwerte, kein Messwert. Sie werden zum Scaling-Regler.
- Tiefe der Trennung: Schritt 3 bündelt nur Schalter. Echte Steckmodule entstehen ab Schritt 4 Stück für Stück, weil `phase2` je Umzug eine eigene Probe braucht.
