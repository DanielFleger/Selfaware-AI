# Plan: der Kern - absolute Kontrolle in jedem Takt (Stand 20.10.2026, 22:45)

Anlass (woertlich):
- Daniel 22:30: "du musst immer 3 Jahre in die Zukunft denken ... wenn du das fertige Programm haettest und es einfach nur
  abschreiben muesstest, mit was wuerdest du anfangen, was haette den groessten Hebel?"
- Daniel 22:34: "ja bitte ... alles, was nur Tage oder Wochen, selbst Monate in die Zukunft denkt, ist zu kurz gedacht ...
  wir brauchen absolute Kontrolle in jedem Tick des Spiels."
- Daniel 22:27: "sofort erkennen koennen, wenn jemand einen Burggraben setzt - dann soll darauf nicht gegangen werden,
  sondern einen anderen Weg."

Baut auf: B-115 (Rust-Kern Stufe 1, laeuft), `Spielkarte.md` (Strukturen, Befehlsweg, Takt), `Plan-selbstlernende-KI.md`
(Weg 3: Stellschrauben lernen). Ersetzt nichts davon - dieser Plan ist die Schicht darunter.

## Das Ziel in einem Satz

Die KI spielt vollstaendig IM Spiel, in jedem Takt: der Kern sieht alles und handelt in demselben Takt; Python ist nur
noch Trainer (Partien starten, Stellschrauben setzen, auswerten). Dann ist das Tempo wirklich egal - bei 10 wie bei 1.000.

## Was gemessen ist (Grundlage, 20.10.2026)

| # | Befund | Marke | Beleg |
|---|---|---|---|
| 1 | Der Kern wird in JEDEM Takt aufgerufen: im Protokoll liegen 2.238 von 2.238 Abstaenden bei genau 500 Takten, auch bei Tempo 300. Der Haken sitzt am Anfang von `processGameTick` (init.lua: hookCode 0x45CD10) - nach `processWaitingCommands`, vor Gebaeuden und Einheiten. | gemessen | `python werkzeug/takt_messen.py kern 5`; init.lua Z. 101/519 |
| 2 | Der Python-Lenker sieht das Spiel nur alle 187-1.069 Takte (Tempo 300, Median 424-586). | gemessen | `python werkzeug/takt_messen.py runden daten/pruefstand_20261020_22*_konsole.txt` (4 Laeufe, alle Tempo 300; andere Tempi nicht gemessen) |
| 3 | Unser Rust (1.99.1, i686-pc-windows-gnu) uebersetzt `extern "thiscall"` - Spielfunktionen sind direkt aufrufbar. Im Spiel noch NICHT aufgerufen. | gemessen (Uebersetzen) | Probe `thiscall_probe.rs` |
| 4 | Eine geladene DLL ist bis Spielende gesperrt - heute heisst jede neue Fassung: Instanz neu starten. | gemessen 19.10. | VillageStudio `doku/Betriebsregeln.md` |
| 5 | Graben im Kartenbild: geplant = LogicLayer-Bit 0x4000, ausgehoben = 0x40000000; an Franz' Burg liegt 0x40000000 genau dort, wo das Bild Wasser neben der Zugbruecke zeigt. Mauer 0x100 (gemessen 18.10.); gedeutet aus je zwei Grundflaechen: Gebaeudeflaeche 0x10000000, Zugbruecke 0. | gemessen (L126) + gedeutet (20.10.) | Wissensregister L126, L154 |
| 6 | Alle Felder von Einheit, Gebaeude, Spielerdaten sind benannt und gegen das Lagebild geprueft. | abgelesen + geprueft | `Spielkarte.md` Abschnitt 2 |

## Was wir nicht aendern koennen (Plattform-Regeln)

- UCP3 laedt DLLs nur aus einem Modulordner (`core.openLibraryHandle`); Lua ohne globale Variablen; Dateien nur im Spielordner.
- 32-Bit-Prozess, ein Faden: alles, was der Kern in einem Takt tut, haelt diesen Takt auf. Zu viel Rechnen macht das Spiel
  langsamer - es verpasst aber nie einen Takt (das ist der Vorteil gegenueber Python).
- `panic = abort`: ein Rust-Absturz reisst das Spiel mit. Also: kein `unwrap`, jeder Speicherzugriff mit Grenzpruefung.
- Mehrspieler und Fairness (Blick 3 Jahre: echte Spieler): **lesen darf der Kern alles, handeln nur ueber Spielbefehle**
  (`queueCommand` mit Absender-Stempel, B-94) - nie Spielzustand direkt beschreiben. Sonst laeuft ein Mehrspielerspiel
  auseinander, und die KI waere kein ehrlicher Gegner.

## Der Aufbau - neu geschrieben, nicht aus Python uebersetzt

Python bleibt als Vergleich stehen, bis der Kern-Baustein dieselbe Pruefung besteht; dann wird der Python-Teil abgehakt,
nicht geloescht.

| Stufe | Was | Pruefpunkt (mit Gegenprobe) | Rueckweg |
|---|---|---|---|
| **S0 Stecker** | Kleine feste DLL `samurai_stecker.dll` im Modulordner; sie laedt den eigentlichen Kern aus einer Kopie (LoadLibraryW), reicht jeden Takt weiter und tauscht ihn aus, wenn eine neue Fassung daliegt - ohne Neustart. Dazu die Messbasis: Dauer eines Takts und Dauer des Kerns je Takt (QueryPerformanceCounter). | neue Fassung (Version 2) ist ohne Neustart aktiv, das Spiel laeuft weiter; Gegenprobe: kaputte Fassung wird abgelehnt, alte bleibt | logik.lua laedt den Kern wie heute direkt |
| **S1 Augen** | Weltbild jeden Takt: alle Einheiten, Gebaeude, Spielerdaten, Kartenschichten (Mauer, Wasser, Graben geplant/ausgehoben, Gebaeudeflaeche). | Weltbild = Python-Lagebild im selben Takt, 0 Abweichungen; Gegenprobe: ein Feld falsch gelesen -> Abweichungen | Kern liest nur, nichts haengt daran |
| **S2 Haende** | Befehle aus dem Kern ueber den Befehlsweg des Spiels: laufen, Einheit/Gebaeude angreifen, anwerben, bauen, Graben planen/zuschuetten. | je Befehl: im naechsten Takt steht das Laufziel/der Auftrag in der Einheit; Gegenprobe ohne Befehl | Schalter "kern_haende aus" |
| **S3 Wege** | Wegfinder des Spiels aus dem Kern; Grabenwache je Takt: neues 0x4000/0x40000000 auf unserem Weg oder an unserem Ziel -> sofort anderes Ziel/anderer Weg. | Erreichbarkeit = Python-Wegtest an denselben Punkten; Graben wird im Takt des Planens gemeldet | Wache aus, Wege wie heute |
| **S4 Leitung** | Kern <-> Python ueber eine geteilte Speicherdatei: Python liest das Weltbild, wann es will, und setzt Stellschrauben; der Kern schreibt ein Takt-Tagebuch (Trainingsdaten). | Python sieht jeden Takt (nicht nur jede Runde); Tagebuch einer Partie vollstaendig | Leitung aus, Kern arbeitet allein |
| **S5 Gehirn** | Entscheidungen wandern Baustein fuer Baustein in den Kern (zuerst Feldzug), jede Regel mit Stellschrauben statt fester Zahlen (Weg 3). | Baustein schlaegt die Python-Fassung auf den Pruefstand-Spielstaenden | Python-Baustein wieder an |
| **S6 Pruefung** | Pruefstand-Bibliothek: feste Spielstaende + automatische Bewertung - die Pruefung, an der jede KI-Fassung gemessen wird; darauf laeuft der Lernkreis. | dieselbe Fassung bekommt zweimal dieselbe Note | - |

**Warum S0 zuerst:** Jede spaetere Stufe wird dutzendfach gebaut und probiert. Heute kostet jeder Versuch einen Neustart
der Instanz - das ist der muede Esel. Mit dem Stecker ist ein Versuch Sekunden.

**Gedaechtnis ueber einen Tausch hinweg:** Der Kern baut sein Weltbild jeden Takt neu aus dem Spielspeicher; was er sich
merken muss (Plaene, gelernte Werte), liegt in einem Block, der dem Stecker gehoert, oder in einer Datei. So verliert ein
Austausch nichts.

## Beziehungen (beide Richtungen)

- Spiel -> Kern: ruft ihn jeden Takt (Haken am Takt-Anfang). Kern -> Spiel: liest Strukturen, handelt nur ueber Spielbefehle.
- logik.lua -> Stecker: laedt ihn einmal, ruft jeden Takt `takt()`. Stecker -> logik.lua: nur Rueckgabewerte und Protokoll.
- Stecker -> Kern: laedt, tauscht, haelt das Gedaechtnis. Kern -> Stecker: meldet Version und Gesundheit.
- Python -> Kern: Stellschrauben und Auftraege (S4). Kern -> Python: Weltbild und Takt-Tagebuch.

## Ausdruecklich NICHT in diesem Plan

- Streit um Einzelregeln des Feldzugs (Tuerme, Tore, Zeitpunkt) - die werden in S5 als Stellschrauben gelernt, nicht von Hand gesetzt.
- Der Umzug unserer Python-Commits in Krarilotus' `src/selfaware` - eigener Punkt; die Leitung (S4) wird so gebaut, dass
  jedes Python-Gehirn, auch seins, darauf aufsetzen kann.
- Selbstspiel-Lernen von null (Weg 1) - erst wenn S6 steht und der Durchsatz gemessen ist.
