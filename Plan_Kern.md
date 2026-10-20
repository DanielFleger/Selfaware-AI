# Plan: der Kern - absolute Kontrolle in jedem Takt (Stand 20.10.2026, 22:45)

> **Ab 20.10. 23:30 fortgefuehrt im Zweig `kern-s0` (Arbeitsordner `../Selfaware-AI-kern`, Krarilotus' Aufbau):
> `docs/plans/Plan_Kern.md`. Diese Fassung hier wird nicht mehr gepflegt.**

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
| 1 | Der Kern verpasst keinen Takt: im Protokoll liegen 2.238 von 2.238 Abstaenden bei genau 500 Takten, auch bei Tempo 300. **Korrektur 23:05 (Frage-Agent):** der Haken ruft ERST den ganzen Takt (`originalGameTick`) und DANACH unseren Kern (init.lua Z. 783-788) - der Kern laeuft also nach Gebaeuden und Einheiten, nicht davor. Und er wird auch in der Pause und bei leerer Welt gerufen (logik.lua Z. 956: "Taktgeber laeuft auch in der Pause"; 40 von 2.346 Protokollzeilen mit leerer Welt) - ein Aufruf ist also NICHT immer ein neuer Takt. | gemessen (Luecken) / abgelesen (Reihenfolge) | `python werkzeug/takt_messen.py kern 5`; init.lua Z. 783-788 |
| 2 | Der Python-Lenker sieht das Spiel nur alle 187-1.069 Takte (Tempo 300, Median 424-586). | gemessen | `python werkzeug/takt_messen.py runden daten/pruefstand_20261020_22*_konsole.txt` (4 Laeufe, alle Tempo 300; andere Tempi nicht gemessen) |
| 3 | Unser Rust (1.99.1, i686-pc-windows-gnu) uebersetzt `extern "thiscall"` - Spielfunktionen sind direkt aufrufbar. Im Spiel noch NICHT aufgerufen. | gemessen (Uebersetzen) | Probe `thiscall_probe.rs` |
| 4 | Eine geladene DLL-Datei ist bis Spielende gesperrt. **Nicht gemessen (Frage-Agent 23:05):** ob eine neue Fassung unter einem NEUEN Dateinamen ohne Neustart laedt - UCP3 prueft nur den Ordner (ucp/code oder ucp/modules), nicht den Namen (core.lua Z. 658-659). | gemessen 19.10. (Sperre) / offen (neuer Name) | VillageStudio `doku/Betriebsregeln.md` Z. 552-554 |
| 7 | Krarilotus hat den Kern auf origin schon nach `crates/samurai-kern` verschoben (20.10. 09:28, Inhalt = B-115), gebaut mit dem Microsoft-Ziel i686-pc-windows-msvc und CI; hier ist nur das GNU-Ziel installiert, keine MSVC-Werkzeuge. Seine Regel: "do not create a second writer" (docs/plans/STRATEGY_DESIGN.md Z. 270). | abgelesen | `git show origin/main:crates/samurai-kern/README.md` |
| 5 | Graben im Kartenbild: geplant = LogicLayer-Bit 0x4000, ausgehoben = 0x40000000; an Franz' Burg liegt 0x40000000 genau dort, wo das Bild Wasser neben der Zugbruecke zeigt. Mauer 0x100 (gemessen 18.10.); gedeutet aus je zwei Grundflaechen: Gebaeudeflaeche 0x10000000, Zugbruecke 0. | gemessen (L126) + gedeutet (20.10.) | Wissensregister L126, L154 |
| 6 | Alle Felder von Einheit, Gebaeude, Spielerdaten sind benannt und gegen das Lagebild geprueft. | abgelesen + geprueft | `Spielkarte.md` Abschnitt 2 |

## Was wir nicht aendern koennen (Plattform-Regeln)

- UCP3 laedt DLLs nur aus einem Modulordner (`core.openLibraryHandle`); Lua ohne globale Variablen; Dateien nur im Spielordner.
- 32-Bit-Prozess, ein Faden: alles, was der Kern in einem Takt tut, haelt diesen Takt auf. Zu viel Rechnen macht das Spiel
  langsamer - es verpasst aber nie einen Takt (das ist der Vorteil gegenueber Python).
- `panic = abort`: ein Rust-Absturz reisst das Spiel mit - eine kaputte Fassung kann also nicht "abgelehnt" werden, sie
  stirbt im ersten Takt (Betriebsregeln Z. 495-503: falsche Aufrufart toetete das Spiel zweimal ohne Meldung). Also: kein
  `unwrap`, jeder Speicherzugriff mit Grenzpruefung; zu messen in S0: `panic = unwind` mit Auffangen an jeder Export-Grenze,
  damit ein Fehler den Kern abschaltet statt das Spiel.
- Mehrspieler und Fairness (Blick 3 Jahre: echte Spieler): **lesen darf der Kern alles, handeln nur ueber Spielbefehle**
  (`queueCommand` mit Absender-Stempel, B-94) - nie Spielzustand direkt beschreiben. Sonst laeuft ein Mehrspielerspiel
  auseinander, und die KI waere kein ehrlicher Gegner.

## Der Aufbau - neu geschrieben, nicht aus Python uebersetzt

Python bleibt als Vergleich stehen, bis der Kern-Baustein dieselbe Pruefung besteht; dann wird der Python-Teil abgehakt,
nicht geloescht.

| Stufe | Was | Pruefpunkt (mit Gegenprobe) | Rueckweg |
|---|---|---|---|
| **S0 Tausch + Taktwaechter** | (a) ZUERST messen: laedt `core.openLibraryHandle` eine neue Fassung unter neuem Namen (`samurai_kern_2.dll`) ohne Neustart? Ja -> kein Stecker noetig, logik.lua laedt einfach den neuesten Namen. Nein -> Stecker-DLL, die den Kern per LoadLibraryW tauscht. (b) Taktwaechter im Kern: unterscheidet neuer Takt (+1) / Pause (Takt steht) / Laden oder neue Partie (Sprung, leere Welt) - nur ein neuer Takt loest Arbeit aus, ein Laden leert das Gedaechtnis. (c) Messbasis: Dauer eines Takts und des Kerns je Takt. (d) Auffangen von Fehlern an der Export-Grenze. | Version 2 ohne Neustart aktiv; im Protokoll: Pause zaehlt nicht als Takt, ein Laden wird als Laden erkannt; Gegenprobe: absichtlicher Fehler in Version 3 schaltet den Kern ab, das Spiel laeuft weiter | logik.lua laedt den Kern wie heute direkt |
| **S1 Augen** | Weltbild jeden Takt: alle Einheiten, Gebaeude, Spielerdaten, Kartenschichten (Mauer, Wasser, Graben geplant/ausgehoben, Gebaeudeflaeche). | Weltbild = Python-Lagebild im selben Takt, 0 Abweichungen; Gegenprobe: ein Feld falsch gelesen -> Abweichungen | Kern liest nur, nichts haengt daran |
| **S2 Haende** | Befehle aus dem Kern ueber den Befehlsweg des Spiels: laufen, Einheit/Gebaeude angreifen, anwerben, bauen, Graben planen/zuschuetten. **Ein Schreiber je Einheit:** wer eine Einheit fuehrt (Kern ODER Python), ist eingetragen; der andere befiehlt ihr nicht. **Neu befehlen nur bei Aenderung** - jeder neue Befehl an eine laufende Einheit startet ihre Wegsuche neu (L152 Punkt 4: "niemand kommt vom Fleck"). Der Kern befiehlt nur, wenn der Absender-Umbau von logik.lua (B-94, 0x00489387) eingebaut ist - sonst gingen seine Befehle an Daniel. | je Befehl: im naechsten Takt steht das Laufziel/der Auftrag in der Einheit; laufende Einheit bekommt in 100 Takten keinen zweiten gleichen Befehl; ohne Absender-Umbau verweigert der Kern; Gegenproben je Fall | Schalter "kern_haende aus" |
| **S3 Wege** | Wegfinder des Spiels aus dem Kern; Grabenwache je Takt: neues 0x4000/0x40000000 auf unserem Weg oder an unserem Ziel -> sofort anderes Ziel/anderer Weg. | Erreichbarkeit = Python-Wegtest an denselben Punkten; Graben wird im Takt des Planens gemeldet | Wache aus, Wege wie heute |
| **S4 Leitung** | Kern <-> Python ueber eine geteilte Speicherdatei: Python liest das Weltbild, wann es will, und setzt Stellschrauben; der Kern schreibt ein Takt-Tagebuch (Trainingsdaten). | Python sieht jeden Takt (nicht nur jede Runde); Tagebuch einer Partie vollstaendig | Leitung aus, Kern arbeitet allein |
| **S5 Gehirn** | Entscheidungen wandern Baustein fuer Baustein in den Kern (zuerst Feldzug), jede Regel mit Stellschrauben statt fester Zahlen (Weg 3). | Baustein schlaegt die Python-Fassung auf den Pruefstand-Spielstaenden | Python-Baustein wieder an |
| **S6 Pruefung** | Pruefstand-Bibliothek: feste Spielstaende + automatische Bewertung - die Pruefung, an der jede KI-Fassung gemessen wird; darauf laeuft der Lernkreis. | dieselbe Fassung bekommt zweimal dieselbe Note | - |

**Warum S0 zuerst:** Jede spaetere Stufe wird dutzendfach gebaut und probiert, und jede braucht den Taktwaechter (sonst
gehen Befehle in der Pause doppelt raus, und ein Graben-Vergleich schlaegt nach jedem Laden Fehlalarm). Ob der Tausch ohne
Neustart einen Stecker braucht, entscheidet die erste Messung in S0 - vielleicht genuegt ein neuer Dateiname.

**Zwei SamurAIs in einem Spiel (2v2, B-133):** ein Kern je Instanz lenkt ALLE SamurAI-Plaetze; Gedaechtnis, Befehls-Stempel
und Leitung sind je Platz getrennt. (Heute kennt `samurai_takt(tick, spieler)` nur "ich".)

**Wo gebaut wird:** in `crates/samurai-kern` (Krarilotus' Aufbau auf origin) - nicht in einer zweiten Kopie. Offen: Daniels
Ja dazu und ob wir dafuer die Microsoft-Werkzeuge installieren oder mit dem GNU-Ziel bauen (Frage 23:05).

**Gedaechtnis ueber einen Tausch hinweg:** Der Kern baut sein Weltbild jeden Takt neu aus dem Spielspeicher; was er sich
merken muss (Plaene, gelernte Werte), liegt in einem Block, der dem Stecker gehoert, oder in einer Datei. So verliert ein
Austausch nichts.

## Beziehungen (beide Richtungen)

- Spiel -> Kern: ruft ihn nach jedem Takt UND in der Pause (Haken nach `processGameTick`). Kern -> Spiel: liest Strukturen, handelt nur ueber Spielbefehle.
- Kern -> logik.lua: braucht deren Absender-Umbau (B-94), bevor er befiehlt. logik.lua -> Kern: baut ihn beim Laden ein; Rueckweg "absender aus" schaltet auch die Haende des Kerns ab.
- logik.lua -> Stecker: laedt ihn einmal, ruft jeden Takt `takt()`. Stecker -> logik.lua: nur Rueckgabewerte und Protokoll.
- Stecker -> Kern: laedt, tauscht, haelt das Gedaechtnis. Kern -> Stecker: meldet Version und Gesundheit.
- Python -> Kern: Stellschrauben und Auftraege (S4). Kern -> Python: Weltbild und Takt-Tagebuch.

## Ausdruecklich NICHT in diesem Plan

- Streit um Einzelregeln des Feldzugs (Tuerme, Tore, Zeitpunkt) - die werden in S5 als Stellschrauben gelernt, nicht von Hand gesetzt.
- Der Umzug unserer Python-Commits in Krarilotus' `src/selfaware` - eigener Punkt; die Leitung (S4) wird so gebaut, dass
  jedes Python-Gehirn, auch seins, darauf aufsetzen kann.
- Selbstspiel-Lernen von null (Weg 1) - erst wenn S6 steht und der Durchsatz gemessen ist.
