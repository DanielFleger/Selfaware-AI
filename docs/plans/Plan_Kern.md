# Plan: der Kern - absolute Kontrolle in jedem Takt (Stand 20.10.2026, 22:45)

Anlass (woertlich):
- Daniel 22:30: "du musst immer 3 Jahre in die Zukunft denken ... wenn du das fertige Programm haettest und es einfach nur
  abschreiben muesstest, mit was wuerdest du anfangen, was haette den groessten Hebel?"
- Daniel 22:34: "ja bitte ... alles, was nur Tage oder Wochen, selbst Monate in die Zukunft denkt, ist zu kurz gedacht ...
  wir brauchen absolute Kontrolle in jedem Tick des Spiels."
- Daniel 22:27: "sofort erkennen koennen, wenn jemand einen Burggraben setzt - dann soll darauf nicht gegangen werden,
  sondern einen anderen Weg."

Wissenseintraege ab L150: `docs/research/Wissensregister_Fortsetzung.md` (das alte Register ist eingefroren).

Baut auf: B-115 (Rust-Kern Stufe 1, laeuft), `Spielkarte.md` (Strukturen, Befehlsweg, Takt), `Plan-selbstlernende-KI.md`
(Weg 3: Stellschrauben lernen). Ersetzt nichts davon - dieser Plan ist die Schicht darunter.

## Das Ziel in einem Satz

Die KI spielt vollstaendig IM Spiel, in jedem Takt: der Kern sieht alles und handelt in demselben Takt; Python ist nur
noch Trainer (Partien starten, Stellschrauben setzen, auswerten). Dann ist das Tempo wirklich egal - bei 10 wie bei 1.000.

## Was gemessen ist (Grundlage, 20.10.2026)

| # | Befund | Marke | Beleg |
|---|---|---|---|
| 1 | Der Kern verpasst keinen Takt: im Protokoll liegen 2.238 von 2.238 Abstaenden bei genau 500 Takten, auch bei Tempo 300. **Korrektur 23:05 (Frage-Agent):** der Haken ruft ERST den ganzen Takt (`originalGameTick`) und DANACH unseren Kern (init.lua Z. 783-788) - der Kern laeuft also nach Gebaeuden und Einheiten, nicht davor. Und er wird auch in der Pause und bei leerer Welt gerufen (logik.lua Z. 956: "Taktgeber laeuft auch in der Pause"; 40 von 2.346 Protokollzeilen mit leerer Welt) - ein Aufruf ist also NICHT immer ein neuer Takt. | gemessen (Luecken) / abgelesen (Reihenfolge) | `python -m selfaware.tools.experiments.takt_messen kern 5`; init.lua Z. 783-788 |
| 2 | Der Python-Lenker sieht das Spiel nur alle 187-1.069 Takte (Tempo 300, Median 424-586). | gemessen | `python -m selfaware.tools.experiments.takt_messen runden daten/pruefstand_20261020_22*_konsole.txt` (4 Laeufe, alle Tempo 300; andere Tempi nicht gemessen) |
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

## Stand S0 (20.10.2026, 23:30) - im Spiel geprueft, Instanz 5, Zweig `kern-s0`

| Pruefpunkt | Ergebnis | Beleg |
|---|---|---|
| Neue Fassung ohne Neustart | **JA - ein neuer Dateiname genuegt, ein Stecker ist unnoetig.** `{"kern": {"laden": "samurai_kern_2.dll"}}` -> "geladen samurai_kern_2.dll, Version 2 (vorher: samurai_kern.dll Version 1)", Spiel lief weiter | ucp3.log 23:16:38 |
| Rueckweg | `{"kern": {"laden": "samurai_kern.dll"}}` -> wieder Version 1 | ucp3.log 23:18:02 |
| Taktwaechter: jeder Takt | 8.000 von 8.000 Takten als "neuer Takt" gezaehlt (55.966 -> 63.966), 0 Spruenge, genau 1 Aufruf je Takt | samurai_kern.log `waechter`-Zeilen |
| Taktwaechter: Pause | 2.954 Aufrufe in der Pause als Pause gezaehlt, nicht als Takt | dito |
| Taktwaechter: Laden | Spielstand geladen -> "epoche 2 tick 40470 von 64286 (Sprung -23816)" | dito |
| Messbasis | Kern im Mittel 1,9-3,5 Mikrosekunden je Aufruf (Hoechstwert ~290-360 inkl. Protokollschreiben); ein Spieltakt dauerte bei diesem Tempo 3,0 ms - der Kern braucht etwa ein Tausendstel | dito |
| Fehlerfang (Gegenprobe) | `{"kern": {"test_fehler": true}}` -> "KERN AUS: Fehler in samurai_test_fehler ... Spiel laeuft weiter"; Takt lief weiter 41.815 -> 42.824; danach liefert der Kern -2 | dito, ucp3.log 23:17:49 |
| Offline | `cargo test`: 5 von 5 gruen; Gegenlaeufe rot (Pause-Zweig sabotiert -> 1 rot; ohne Fehlerfang bricht der Testprozess ab) | crates/samurai-kern |

**Noch nicht geprueft:** "keine Partie" (Menue) im echten Spiel; Laden eines SPAETEREN Stands (Sprung vorwaerts); beim Neuladen von
logik.lua startet wieder samurai_kern.dll (Version 1) - die neueste Fassung muss dann neu geladen werden (naechster Schritt:
logik.lua liest den Namen der aktuellen Fassung aus einer Datei).

**Folge fuer den Plan:** S0 ist erfuellt ohne Stecker. Jede weitere Stufe kann jetzt im laufenden Spiel in Sekunden ausgetauscht
werden: bauen -> unter neuem Namen in den Modulordner -> `{"kern": {"laden": ...}}`.

## Stand S1 (20.10.2026, 23:31) - Augen, im Spiel geprueft (Kern Version 3-5, Instanz 5)

| Pruefpunkt | Ergebnis | Beleg |
|---|---|---|
| Weltbild = Lagebild im selben Takt | Takt 42.824: 694 Einheiten, 313 Gebaeude, **0 Abweichungen** in allen Spalten (ausser "erreichbar" = S3) | `python -m selfaware.tools.experiments.kern_vergleich` -> GLEICH |
| Gegenprobe | Fassung mit falschem Feld fuer "leben" (+972 statt +968): 7 Abweichungen, UNGLEICH; zurueck auf die richtige Fassung: GLEICH | dito |
| Kosten je Takt | Einheiten + Gebaeude 7,3 us, Grabenwache (alle 80.400 Felder) 96-121 us, Kern gesamt ~106-131 us bei 3,0 ms je Takt (~4 %) | `waechter`-Zeilen, samurai_kern.log |
| Graben im selben Takt | Planbefehl eingereiht in Takt 47.989 -> Kern meldet "neu geplant" in Takt 47.990 (= Ausfuehrungstakt); ebenso 48.343->48.344, 48.699->48.700; mit Feldkoordinaten | samurai_kern.log `graben`-Zeilen, ucp3.log SPIELBEFEHL |
| Gegner beim Graben gesehen | Franz hob waehrenddessen seinen Graben aus: "neu ausgehoben (195,113)", (184,70), (177,70) ... jede Zelle im Takt | dito |
| Planung geloescht | Version 4: Planen und Loeschen live - "neu geplant 7" (Takt 58.152), "Planung geloescht 9" (Takt 58.829) | dito |
| Nach dem Laden kein Fehlalarm | jede neue Epoche beginnt mit "Aufnahme der Epoche - geplant n ausgehoben m", ohne "neu"-Meldung | dito; offline-Test `neue_epoche_gibt_keinen_alarm` |
| Offline | `cargo test` 10/10; Gegenlaeufe rot (Alarmsperre nach Laden, Ortsrechnung, Zuschuetten); `tests/test_kern_vergleich.py` 2/2 | crates/samurai-kern, tests |

**Offen / nicht geprueft:** "zugeschuettet" nur offline geprueft (kein Zuschuetten im Spiel beobachtet); Version 5 (nur Zeilenformat)
im Spiel nicht mehr mit Grabenmeldung gesehen - die Partie endete bei Takt 60.861; das Loeschen der Planung entfernte im ersten
Versuch nur 10 von 22 Feldern (warum, ungeklaert - fuer den Kern unerheblich).

**Naechste Verbesserung Grabenwache:** statt 80.400 Felder je Takt die Zaehler des Spiels pruefen (`moatTileCount`,
`currentMoatCount`, Spielkarte-Strukturen) und nur bei Aenderung voll lesen - das spart die ~100 us je Takt.

## Bauplan S2 Haende (20.10.2026, 23:40) - vor dem ersten Bau

Quelle: der heutige Befehlsweg in logik_stand_20261020.lua (befehlAbsetzen Z. ~1855, angriff Z. ~2304, angriffSchlangeTick,
absenderAktiv) - nachgelesen, nicht erinnert. Der Kern geht denselben Weg in Rust, damit es keinen zweiten gibt:

1. **Befehl absetzen** (wie befehlAbsetzen): 6 Werte nach GameCommandParam (GSS 0x0191D768 + 0x7A850), queueCommand
   0x00489100 (thiscall, this = GSS, 1 Argument), dann den eben eingereihten Eintrag (Nr bei GSS+0x2D824, Eintrag
   GSS+0x3C67C + Nr*0x4F8: +8 Art, +9 Zustand 1) mit Absender 0x53414D00 + Platz stempeln. Waehrend des Einreihens steht
   "ich" (0x01A275DC) auf dem Platz der Einheiten, danach sofort zurueck (wie alsSpieler).
2. **Laufen/Angreifen** (wie angriff): Auswahl des Menschen (UnitsState+116, 100 Worte) sichern, Auswahlmarken (+178/+180)
   der eigenen Einheiten loeschen, die Einheiten auswaehlen, freie Gruppe suchen (Gruppentabelle 0x01667F78+40, je 0x334,
   +24 = belegt), Befehl 16 {Gruppe}, Auswahl zurueck, dann 17 {Gruppe, x, y} oder 36 {Gruppe, Art 4/9, Ziel, uid}.
   **Gruppen sucht der Kern von 1 aufwaerts**, logik.lua von 1249 abwaerts - so greifen beide im selben Takt nie dieselbe.
3. **Ein Gruppenbefehl je Takt**, naechster erst, wenn die Einheiten in ihrer Gruppe stehen oder 20 Takte vorbei sind
   (gemessen 04.10.: mehrere Auswahlbefehle im selben Takt landeten in der letzten Gruppe).
4. **Ein Schreiber je Einheit:** der Kern befiehlt nur Einheiten, die ihm uebergeben wurden ({"kern": {"uebernehmen": [...]}},
   Rueckweg "freigeben"). **Kein Dauer-Neubefehl:** derselbe Auftrag an dieselbe Einheit wird nicht wiederholt.
5. **Ohne Absender-Umbau kein Befehl** (Byte an 0x00489387 != 0xE8 -> verweigert und gemeldet) - sonst gingen die Befehle an
   den Menschen.

Pruefpunkt: Kern-Laufbefehl -> im naechsten Takt steht die Einheit in der neuen Gruppe und ihr Laufziel ist (x, y)
(Lagebild). Gegenproben: nicht uebernommene Einheit -> abgelehnt; derselbe Auftrag zweimal -> einmal abgesetzt; Absender-
Umbau aus -> verweigert. Risiko: falsche Aufrufart toetet das Spiel (Betriebsregeln Z. 495-503) - queueCommand ist mit
denselben Werten seit 04.10. aus Lua belegt (exposeCode(0x00489100, 2, 1) = thiscall, this + 1 Argument).

## Stand S2 (20.10.2026, 23:38) - Haende, im Spiel geprueft (Kern Version 6, Instanz 5, Pruefstand B140)

| Pruefpunkt | Ergebnis | Beleg |
|---|---|---|
| Kern setzt selbst einen Gruppenbefehl ab | Takt 40.471: "Gruppe 16, 3 von 3 Einheiten von Spieler 1, Laufen (163,192) - abgesetzt"; Rust -> queueCommand (thiscall) lief, das Spiel lief weiter | samurai_kern.log `haende`-Zeile |
| Einheiten folgen | alle 3 in Gruppe 16 (vorher 1245/1242/1249); Arab. Bogen 85 und Streitkolben 91 liefen hin und stehen auf (163,192)/(162,191) - das Spiel verteilt eine Gruppe in Formation um das Ziel; Bogenschuetze 145 (Zustand 8, 40 Felder weg) blieb an seinem Platz | `python -m selfaware.tools.experiments.kern_haende_pruefen` + Weltbild ueber 3 Zeitpunkte |
| Gegenprobe A: nicht uebergeben | Auftrag fuer Einheit 146 -> -4, ihr Laufziel blieb (204,242) | dito |
| Gegenprobe B: kein Dauer-Neubefehl | derselbe Auftrag an die laufenden drei -> 0 0 0 | dito |
| Gegenprobe C: ohne Absender-Umbau | `{"absender": "aus"}` -> Kern Takt 42.348 "VERWEIGERT - Absender-Umbau fehlt"; danach `{"absender": "an"}` wieder eingebaut | samurai_kern.log, ucp3.log |
| Offline | `cargo test` 14/14; Gegenlaeufe rot (Schreiber-Regel, Dauer-Neubefehl-Regel) | crates/samurai-kern |

**Offen:** Stempel fuer einen Platz, der nicht "ich" ist (2v2) - hier war der Kern selbst Spieler 1; Angriffsauftraege (Art 4/9)
im Spiel noch nicht abgesetzt (gleicher Weg, Befehl 36); warum Bogenschuetze 145 nicht lief (Zustand 8) - im Feldzug wichtig;
Pruefpunkt "Laufziel = Auftrag" muss die Formation zulassen (Abstand statt Gleichheit).

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
