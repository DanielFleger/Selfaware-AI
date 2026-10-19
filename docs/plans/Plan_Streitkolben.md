# Plan: 10-20-30-40-50 Streitkolbenkaempfer so schnell wie moeglich (Stand 06.10.2026, 19:50)

## Auftrag (Daniel 06.10. 19:45, woertlich)
"mach danach die Streitkolbenkaempfer 10-20-30-40-50 und hier bitte maximal aufpassen auf die Waffenproduktion,
Ausbildungslager naeher zum Vorratslager, minimale Laufwege fuer die Wirtschaft, erst bauen wenn Ressourcen im
Vorratslager ankommen fuer maximale Effektivitaet. Bitte kreative Loesungen finden, wenn Gold zu viel ueber ist (was ich
bezweifle) gerne auch Essen kaufen. Du brauchst Lederharnische und Harnischmacher etc. Berechne wie produktiv alle
Gebaeude sind, also wie viele Kuehe wann generieren, wie viele Lederharnische aus einer Kuh gemacht werden koennen, wie
viele Streitis aus einem Eisen gebraucht werden etc."
Vorher (19:21): Testpartie gegen eine leere KI - am schnellsten 10.000 Gold, dann 10-20-30-40-50 Streitkolbenkaempfer,
dann jede Einheit. Grundsatz (19:33): gegen mehrere Gegner braucht es stabiles Wachstum, Rohstoffverkauf reicht nicht.

## Challenge-Regeln (Daniel 06.10. 19:49)
- Es zaehlt die genaue Anzahl, so schnell wie moeglich - wie ein TAS-Run (Speedrun mit Werkzeug).
- Fuer die letzten Kaempfer duerfen nicht mehr gebrauchte Waffen verkauft werden; Abreissen bringt tendenziell die
  Haelfte der investierten Ressourcen als verkaufbare Produkte -> theoretisch alles abreissen bis auf das, was die
  Rekrutierung braucht, und die letzten rauspressen.
- Reihenfolge: erst Recherche, dann Aufbau, dann Benchmark, dann immer weniger Zeit. "Ich glaube, es ist schneller als
  ich denke."
- Arbeitsweise (19:49): selbst herausfinden, aber Daniel hat viel Spielerfahrung - nicht ALLE Fehler selbst machen;
  stoppt er, ihm vertrauen und die richtigen Infos sammeln.

## Testumgebung (steht)
`erstes_spiel.py assassinen=0 leere_ki=ja gold_ziel=N bis_tick=60000` - Rotkaeppchen mit Waren/Gold jede Runde 0.
Ausgangswert Gold (gold10k_2, 06.10.): 1.000 bei 15.975, 10.000 bei 36.226; verkauft vor allem Holz, Fleisch, Aepfel, Stein.

## Was feststeht (Liga-Balance liga_ai.json, abgelesen)
| | Wert |
|---|---|
| Streitkolbenkaempfer | 20 Gold + Keule + Lederharnisch; 25.000 Leben |
| Kaserne | Kosten [0, 12, 0, 0, 0] |
| Schmiede (Keulen/Schwerter) | [20, 8, 0, 0, 0] |
| Gerberei (Lederharnisch) | [15, 3, 0, 0, 75] |
| Milchviehhof (Kuehe) | [7, 0, 0, 0, 15] |
| Eisenmine | [20, 6, 0, 0, 0]; Eisen doppelt abgeholt (enable_iron_double_pickup) |
| Markt | Keule Kauf 300 / Verkauf 150; Leder 160 / 50; Eisen 270 / 135 (je Los) |
Kosten-Reihenfolge vermutlich [Holz, Stein, Eisen, Pech, Gold] (so liest der Planer die Baukosten aus dem Spiel) - im
Spiel gegenpruefen.

## Was gemessen werden muss (nichts schaetzen)
1. Milchviehhof: Kuehe je 1.000 Ticks, wann die erste Kuh, wie viele gleichzeitig.
2. Gerberei: Lederharnische je Kuh, Ticks je Harnisch.
3. Schmiede: Keulen je Eisen, Ticks je Keule.
4. Eisenmine: 0,588 Eisen je 1.000 Ticks; 8-91 Felder Weg waren gleich schnell, weil der Bergmann begrenzt (L40).
5. Laufwege: Werkstatt <-> Lager <-> Waffenlager <-> Kaserne in Feldern; Zeit vom fertigen Gegenstand bis im Waffenlager.

## Schritte
1. Messpartie: je eine Kette (2 Milchviehhoefe, 1 Gerberei, 2 Eisenminen, 1 Schmiede, Waffenlager + Kaserne direkt am
   Lager) in der Testumgebung; jede Runde Bestand (Keule, Leder, Eisen) und Arbeiterzustand mitschreiben.
2. Aus den Messwerten die Verhaeltnisse rechnen (Hoefe je Gerberei, Minen je Schmiede) - mit Befehl und Quelle.
3. Lenker "Streitkolben": Werkstaetten nah am Lager, Kaserne/Waffenlager am Lager, bauen erst wenn die Ware im Lager ist,
   anwerben sobald Keule + Harnisch + 20 Gold da sind; Marken 10/20/30/40/50 mit Tick.
4. Gegenprobe: dieselben Marken mit Kauf am Markt (Keule 300 + Leder 160 + 20 je Kaempfer) - was ist schneller?
5. Ueberschuessiges Gold: Essen kaufen (Beliebtheit -> hoehere Steuern) - erst wenn gemessen ist, dass Gold uebrig ist.

## Messergebnisse (Messpartie 3, 06.10. 19:55, `daten/streitkolben_messung_20261006_195508.json`)
- Gesetzte Zahlen wirken nur bei Gold. Stein/Holz/Eisen/Waffen liegen in Lagern; ein gesetzter Zaehler wird neu
  gezaehlt (Stein 0 -> 300 gesetzt, kurz darauf 0). Darum fehlten Kaserne (12 Stein), Schmiede (8), Gerberei (3) -
  Daniel 19:54: "du brauchst gewisse Gueter, siehe Balance". Waren echt am Markt kaufen.
- Markt (je Kauf/Verkauf): 5 Keulen 300 / 150 Gold; 5 Leder 160 / 50; 5 Stein 50.
- Kaserne: ein Streitkolbenkaempfer zieht 20 Gold + 1 Keule + 1 Lederharnisch ab (+1 Einheit Typ 26).
- Gerberei: +3 Lederharnische je Kuh (zwei Spruenge 4->7 bei Tick 5.615, 7->10 bei 7.450; 2 Milchviehhoefe + 1 Gerberei).
- Offen: Keulen je Eisen (Eisenkauf scheiterte, Gold blieb gleich - warum?), Holzkauf scheiterte ebenso;
  Abriss einer frisch gebauten Schmiede gab in 10 Ticks nichts zurueck (zu frueh gemessen? im Bau?).
- Eisen-/Holzkauf geklaert (19:58): alle 4 Lagerteile belegt (Holz 13+48, Stein 17+2) - ein Teil fasst nur eine
  Warenart (48). Vor neuer Warenart freies Teil schaffen.
- Naechster Schritt: Schmiede mit Eisen messen, Abriss nach
  Fertigstellung und laengerer Wartezeit messen; dann Kette dimensionieren und erster Benchmark 10 Kaempfer.

## Messpartie 4 (06.10. 20:00, `daten/streitkolben_messung_20261006_195917.json`)
- Mit angebautem Lagerblock klappt der Eisenkauf: 4 Kaeufe = 20 Eisen fuer 1.080 Gold (270 je 5).
- Schmiede (bei (90,280), Lager am Bergfried (145,264), ~55 Felder): holte je 1 Eisen bei Tick 4.654 und 8.745 -
  ~4.100 Ticks je Stueck, der Weg zum Lager dominiert (Daniel: Werkstaetten nah ans Lager).
- Die Schmiede macht ohne Umstellung SCHWERTER: Vorrat danach Schwert 1, Keule unveraendert. Im Spiel wird sie per
  Klick auf Keulen umgestellt -> den Spielbefehl dafuer finden (nicht Speicher setzen).
- Naechste Schritte: (1) Umstell-Befehl der Schmiede finden; (2) Werkstaetten, Waffenlager und Kaserne direkt ans Lager;
  (3) Zeit je Keule und je Harnisch bei kurzem Weg messen; (4) Abriss-Rueckgabe messen (diesmal keine 2. Schmiede gebaut).

## Messpartien 5/6 (06.10. 20:02-20:04)
- Spielbefehl 33 `ClickSetBuildingProductionType` (Gebaeude, Art, UID) -> `SetBuildingProductionType` setzt
  producedItemType, wenn die UID passt (`daten/dekomp_produktionstyp*.c`, Befehlstabelle `daten/befehlstabelle_namen.txt`).
  Art 21 = Keule: danach 3 Keulen aus 3 Eisen (belegt: 1 Eisen = 1 Keule).
- Lager zuerst vergroessern! Messpartie 5 baute alles direkt ans Lager -> kein Anbau moeglich, Eisenkauf scheiterte.
  Messpartie 6: erst zwei Lagerbloecke, dann der Rest -> Eisen (20 fuer 1.080) und Holz (bis 195) kaufbar.
- Schmiede ~6 Felder vom Lager: holt alle ~2.100 Ticks 1 Eisen (3.151 / 5.256 / 7.364), Keulen bei 5.124 und 7.231.
  Bei ~55 Feldern Weg waren es ~4.100 Ticks.
- Gerberei: erste Harnische bei ~6.500 (Milchviehhoefe ~40 Felder weg, bei (174,296)/(178,240)); 1 Kuh = 3 Harnische.
- Abriss einer Schmiede: auch nach 150 Ticks und mit Lagerplatz 0 zurueck - offen (fertig gebaut? andere Art Rueckgabe?).
- Vergleich: Markt 1 Keule 60 Gold, 1 Harnisch 32 Gold -> ein Kaempfer 112 Gold; selbst gemacht: Eisen 54 Gold je Stueck
  (Kauf) + ~2.100 Ticks je Schmiede. Gold ist der Engpass (Ausgangswert: 1.000 Gold erst bei Tick 15.975).
- Naechster Schritt: erster Benchmark 10 Kaempfer ab Tick 0 ohne gesetztes Gold - Weg A nur Markt, Weg B Markt +
  eigene Kette; Marken 1..10 mit Tick.

## Daniel 06.10. 20:05 (Bild: Lager mit Gebaeuden drumherum) - als Naechstes
Woertlich: "ich verstehe nicht genau warum du es so baust, weil der Weg vom Streitimacher gesperrt ist. PS: wenn du
sie genau aufeinanderliegend machst, koennen sie durchlaufen. PS PS: es macht sehr viel Sinn zu schauen, wie du die
Laufwege sehen kannst und natuerlich wie das Spiel sie berechnet, und dann eine moeglichst effektive Aufstellung
erstellst - das wird besonders wichtig, wenn du skalierst, sagen wir 30 Schwertmacher und 30 Lederharnischmacher etc.
bzw. dynamisch anpassend je nachdem wie viele du von was brauchst. Aber bitte gerne testen wie viel Streitis wie viel
Eisen, wie viele Kuehe wie viele Lederharnische."
Daraus:
1. Laufwege sichtbar machen: Arbeiter-Positionen je Runde mitschreiben (Lagebild: x, y, laufx, laufy, zustand) und als
   Karte auswerten; Begehbarkeit/Wegnetz des Spiels lesen (Modulbefehle begehbar, wegtest, rohstoffkarte).
2. Wie das Spiel Wege berechnet (Wegfinder, Wegnetz-Gebiete) im Spielcode nachlesen (Ghidra, findPath...).
3. Aufstellung: Werkstaetten so, dass kein Weg zum Lager/Waffenlager versperrt ist; Gebaeude genau aneinander, damit
   man durchlaufen kann (Daniel) - im Spiel pruefen.
4. Skalierbar und dynamisch: Zahl der Schmieden/Gerbereien/Milchhoefe nach Bedarf (z. B. 30/30) - Verhaeltnisse
   messen: Keulen je Eisen (bisher 1:1, 3 Stueck), Harnische je Kuh (bisher 3, 2 Kuehe) - mit mehr Stueckzahl bestaetigen.

## Daniel 06.10. 20:06 zum Abriss
"sie bekommen nicht mehr Wert, nur weil sie laenger stehen. Sie geben normalerweise die Haelfte ab, egal in welchem
Zustand. Gleiches gilt fuer Torhaeuser oder Tuerme, weshalb es manchmal effektiver sein kann, sie abzureissen und mit der
Haelfte ein neues zu bauen, anstatt sie zu reparieren." - Meine 0-Messungen widersprechen dem: der Modulbefehl abreissen
hat einen Parameter rueckgabe (Standard 0, Spielbefehl 29 {nr, rueckgabe, uid}) - nie gesetzt. Naechster Test: rueckgabe=1.
- Messpartie 7 (20:07): Abriss mit rueckgabe=1 -> wieder 0 Holz/Stein/Gold nach 150 Ticks. Offen; zu pruefen: wurde die
  zweite Schmiede ueberhaupt fertig/abgerissen (Gebaeudeliste vorher/nachher), war das Holz-Lager voll (195 = 4 Teile),
  was param_3 in giveBackResourceForDestroyedBuilding bedeutet (daten/dekomp_abriss_rueckgabe.c ganz lesen).
- GELOEST 20:10: param_3 ist ein Prozentwert (Kosten * Prozent / 100); der Abriss-Knopf schickt 50 (Ghidra
  QueueAufrufe.java: MenuItemActionHandler_BuildMenu_DeleteAction 0x00438ad9 MOV [Param1], 0x32). Modul logik.lua:
  abreissen jetzt Standard 50, gedeckelt bei 50 (Sicherung logik.lua.bak-abriss50-20261006). Messpartie 8: Schmiede
  20/8 -> 10 Holz / 4 Stein zurueck - Daniel bestaetigt.
- Daniel 20:11 "schau mal bei geraden/ungeraden Ressourcen/Abriss": abriss_messen.py (Erwartung vorher im Kopf der
  Datei) - Gerberei 15/3/75 -> 7/1/37 (zweimal gleich, kein gemerkter Rest), Milchviehhof 7/0/15 -> 3/0/7, Kaserne
  0/12 -> 6, Huette 5 -> 2. Es wird ABGERUNDET. daten/abriss_messung_20261006_201248.json.
  Aus dem Code (nicht gemessen): kein Lagerplatz -> Rueckgabe verloren; Mauern sammeln Bruchteile ueber Abrisse.

## Haertetest ab Tick 0 (Daniel 06.10. 20:52/20:54)
Daniel: "immer direkt von 0 anfangen ... dann kann ich zuschauen"; erster Haertetest = Zeit von Tick 0 bis zu den ersten
10 ausgebildeten Streitkolbenkaempfern, realistische Startbedingungen (0 Gold, normale Ressourcen). Reihenfolge (B1):
Lager zu schnellem Holz umsetzen -> Stein -> Eisen -> Waffenproduktion, Zeitpunkt so, dass moeglichst alle
Lederharnische produziert werden. Bauregeln (B3/B4): Kornspeicher/Huetten/Kaserne/Markt weit weg, Werkstaetten 1 Feld
vom Lager.

Gemessen vor dem Start (20:56-20:58, `erkunden.py`, Start ohne Eingriff):
- Startholz kommt nach und nach: 30 bei Tick 120, +~28 je 110 Ticks, 150 ab Tick ~650; Bauern 2 -> 10 bis Tick 566;
  Beliebtheit startet bei 100 und sinkt ohne Essen (97,75 bei 231, 93,25 bei 678).
- Karte (Bergfried 141,265): Wald knapp (76 Baeume im Umkreis 75), Waelder O (191,265) und SO (163,311); Hof ab 27
  Feldern (172,297); Mine ab 48 (141,317); Steinbruch nur im Westen ab 56 (81,267).
- Kosten (Spieltabelle): Huette 5 H, Holzfaeller 5 H, Eisenmine 20 H 6 S, Kaserne 12 S, Waffenlager 5 H, Schmiede
  20 H 8 S, Gerberei 15 H 3 S 75 G, Kornspeicher 5 H, Steinbruch 25 H, Ochsenjoch 5 H, Markt 0, Milchviehhof 7 H 15 G.
- Verkauf (verkaufspreise_liga.txt): Kaese 6, Brot 4, Aepfel 3, Fleisch 1, Holz 1 Gold je Stueck.

Bauordnung v1 (`haertetest.py`, Grundlinie - Lager bleibt am Bergfried, Test 2 versetzt es und misst den Gewinn):
Kornspeicher + Markt -> Kaese/Brot verkaufen (+150) -> 2 Milchviehhoefe -> Steinbruch + Ochsenjoch -> 2 Huetten ->
Gerberei / Eisenmine / Waffenlager / Schmiede (Aufbauplaner) -> Kaserne. Bedarf: 109 Holz, 29 Stein, 305 Gold.
- v1 abgebrochen 21:01 (Daniel): nicht optimiert - es fehlen Apfelplantagen, Holzfaeller, Jaeger; der schnellste Weg
  zu einer einzelnen Streitkolben-Werkstatt ist nicht der schnellste zu 10; Kaese kommt als Nahrung zu langsam (B7/B8).
  Gemessen bis dahin: erster Stein 5.246, erstes Eisen 11.823, keine Keule/kein Leder bis 20.845 (B9).

## Bewertungskette fuer "unter 1 Jahr" (Daniel 21:58/21:59: 5 Versuche; "keine Bewertungskette oder kritische Befragung")
Stand 21:59, Bestzeit v5 11.930 (Endspiel 11.416). Ziel < 9.600 -> Endspiel bei ~9.400 mit Bedarf ~1.185 Gold-Wert;
v5 hatte bei 9.400 erst ~900 -> es fehlen ~30 %.
1. Schnellere Eroeffnung (v11/v12: Seasoning B 1.215 statt 1.720) + schnelleres Endspiel -> grob 11.000. Reicht NICHT.
2. Groesster Hebel = Bedarf senken: von 1.120 gehen 600 an Keulen, 320 an Leder.
   - eigenes Leder: 2 Hoefe + 1 Gerberei direkt nach dem Seasoning (~105 Gold) spart 320 (0,46 Kuehe/Hof/1000, 3 Leder/Kuh).
   - ~~eigene Keulen aus GEKAUFTEM Eisen: 7 Eisen x 54 = 378 spart ~220~~ FALSCH (22:03, Daniels Frage "macht eine
     Schmiede bei 10 Sinn?"): Eisen gibt es nur in 5er-Losen -> 10 Eisen = 540 statt 600 fuer 2 Lose Keulen = 60 gespart;
     Schmiede 20 H 8 S (Wert 60), Abriss gibt 10 H 4 S zurueck -> netto ~30. Ergebnis ~0, dazu Arbeiter, Platz und
     ~6.500 Ticks (7 Eisen x 927). Bei 10 Kaempfern: KEINE Schmiede. Bei 30: 6 Lose Keulen 1.800 gegen 4 Lose Eisen
     1.080 -> spart ~720, dann lohnt sie (mehrere Schmieden wegen der Zeit).
   - Leder netto: 2 Hoefe + Gerberei = 29 H 3 S 105 G (Wert ~149), Abriss gibt ~69 zurueck -> netto ~80, spart 320.
     Zeit: Gerberei ~1.550 Ticks je Kuh -> 4 Kuehe (12 Leder) ~6.200 Ticks, ab ~1.500 fertig um ~7.700.
   -> Luecke bei 9.400: ohne Leder 1.185 - 900 = ~285; mit Leder 865 - ~820 = ~45 (+ unbekannter Verlust, weil die
      105 Gold frueh nicht in die Wirtschaft gehen). Reicht nur zusammen mit der schnelleren Eroeffnung. Gerechnet, ungeprueft.
3. Gleiche Fassung mehrfach laufen lassen ist KEIN Weg (Daniel) - erst Aenderung mit Rechnung, dann Versuch.
Naechster Schritt v14: weg=bilanz + fruehe Leder-Kette, Keulen weiter kaufen; Bilanz rechnet eigenes Leder gegen.

## Plan 25 Streitkolbenkaempfer (Daniel 06.10. 23:15: "der Plan fuer 25 Streitis steht")
Stand 23:20. Grundlage: nur gemessene Werte (Register), Rechnungen als solche markiert. Der Lernkreis (werkzeug/lernen.py)
waehlt die Stellgroessen selbst; dieser Plan gibt ihm die Knoepfe und die Rechnung, nicht feste Regeln.

### 1. Bedarf: Kaufen gegen Selbermachen (Marktpreise gemessen, Messpartie 8 / L11)
| Posten | Kaufen | Selbst | Rechnung |
|---|---|---|---|
| 25 Lederharnische | 5 Lose x 160 = 800 | 9 Kuehe (3 Leder je Kuh, S3) | 4 Hoefe (28 H, 60 G) + 3 Gerbereien (45 H, 9 S, 225 G) ~ 330 Wert, Abriss gibt die Haelfte zurueck -> netto ~165, spart ~635 |
| 25 Keulen | 5 Lose x 300 = 1.500 | Schmiede mit Markt-Eisen (54 G je Eisen) | 1:1 (S4, 3 Stueck): 5 Lose Eisen 1.350; 1,5 je Eisen (Daniel): 17 Eisen = 4 Lose 1.080 (5 Keulen uebrig). OFFEN: S4 mit groesserer Zahl messen |
| Anwerben | 25 x 20 = 500 | - | - |
| Kaserne + Waffenlager | 12 Stein + 5 Holz | eigener Stein | - |
Kaufen gesamt ~2.800 Gold. Mit eigenem Leder + Keulen aus Markt-Eisen (1,5-Fall) ~1.080 + 500 + ~165 + Schmieden netto ~120 = ~1.870.

### 2. Zeit der Ketten (gemessen)
- Kuh: 0,46 je Hof und 1.000 Ticks; erste Kuh ~1.400-2.000 Ticks nach dem Hof (v15b: Hoefe 1.269 -> Kuh 2.701). 9 Kuehe mit 4 Hoefen ~4.900 Ticks.
- Gerber: ~1.550 Ticks je Kuh -> 9 Kuehe = 14.000 Gerber-Ticks -> 3 Gerbereien ~4.700 Ticks.
- Schmied: 927 Ticks je Keule (G3), Rundgang Schmiede -> Lager -> Waffenlager (G4: nah 588 Ticks). 25 Keulen = 23.200 Schmied-Ticks -> 5 Schmieden ~4.700 Ticks.
- Neuer Arbeitsplatz: erster Ertrag erst ~4.000 Ticks nach der Vergabe (L10, Weg vom Feuer am Bergfried). -> Leder-Kette
  muss VOR ~Tick 2.000 stehen, Schmieden spaetestens ~5.000 Ticks vor dem Ziel.

### 3. Ablauf (Stellgroessen fuer den Lernkreis, Werte waehlt er)
1. Eroeffnung wie die beste 10er-Strategie des Lernkreises (Holz, Seasoning, Steinbrueche, Huetten voraus).
2. Direkt nach dem Seasoning: N_hoefe (2/4/6) Milchviehhoefe; Gerbereien (1/2/3) mit der ersten Kuh; Waffenlager mit dem ersten Leder.
3. Ab Gold-Schwelle G_eisen: Eisen in 5er-Losen kaufen, N_schmieden (0/2/4/5) Schmieden 1 Feld vom Lager (B4), Waffenlager daneben.
4. Bilanz rechnet eigenes Leder und eigene Keulen gegen (wie v14 "kommt"); Endspiel sobald Rest-Bedarf gedeckt.
5. Anwerben laufend, sobald je 1 Keule + 1 Leder + 20 Gold + Bauer da sind (bei 25 lohnt es, nicht alles ans Ende zu legen).

### 4. Pruefpunkte (Fruehabbruch, Lernkreis-Note)
- Bis Tick 2.000: N_hoefe Hoefe stehen und sind besetzt; bis 3.500 erste Kuh.
- Bis 6.000: erste Keule aus eigener Schmiede (falls N_schmieden > 0).
- Note = Tick des 25. Kaempfers (sonst geschaetzt wie beim 10er).
### 5. Offen (vor dem ersten 25er-Lauf messen)
- Keulen je Eisen (S4 1:1 aus 3 Stueck gegen Daniels 1,5) - entscheidet 1.080 gegen 1.350.
- Waffenlager-Groesse (~50, Indiz) - bei 25 + 25 reicht eins?

## Stand 07.10.2026 01:57 (Ende der Nacht-Sitzung) - Weiter morgen mit 25 Streitkolbenkaempfern

**Ergebnis 10 Streitis:** bester sicherer Lauf 64 = 9.718 Ticks (Ziel 70 Leute, Kasse -40 ohne Grenze, Schub 5, Aufloesen
nach Bedarf, Abwander-Schutz); unter 1 Jahr nur einmal (Lauf 38 = 9.395, Kontrolle verfehlt). Letzter Massstab Lauf 69 = 10.006
(aufloesen=ende, abriss=nein, schub=ja, kasse_grenze=0, bevoelkerung_ziel=70, penner=20).

**Was wirkt (Wissensregister L21-L33):** Steuer ohne Beliebtheits-Bedingung (4 Gold/Kopf/Monat bei -40, Monat ~800 Ticks);
Wachstum bis 70, dann Kasse -40 + Essen-Stopp; Start-Soldaten (5 Bogen + 7 Speer) als Bauern; Anwerben eines nach dem anderen und
nie, wenn der Bauer mit der kleinsten Nummer abwandert (Zustand 110, Spielcode euroRecruit); Endspiel ohne Abriss
(Abriss verlor ~190 Holz unterwegs).

**Offen / naechste Hebel:**
1. Einzelkauf wie die KI: AICState::buyGoods(Spieler, Ware, Menge) (0x004cc000 Grundversion) - braucht neuen Befehl im
   villagestudio-Modul (gehoert der VillageStudio-Sitzung - Daniel fragen). Speicher-Gutschrift wirkt NICHT (L33).
2. Bauern beim Anwerben gezielt waehlen (Modul-Befehl statt werbe) - spart die Wartezeit bei Beliebtheit 0 (250-600 Ticks).
3. Endspiel zaehlt Holz unterwegs (Ladung der Holzfaeller) noch nicht mit.
4. Grosse Streuung zwischen Laeufen gleicher Strategie (54: 9.796 / 57: verfehlt) - je Strategie mehrere Laeufe noetig.

**Fuer 25 Streitis:** gleiche Kette, aber 25 x (60+32 Waffen + 20 Anwerben) = 2.800 Gold - Kasse mit mehr Leuten/laenger;
Anwerben ueber mehrere Schuebe solange Beliebtheit hoch (L30/L32).

## Strategie-Rat 25 Streitkolbenkaempfer, Beliebtheit NIE unter 50 (Daniel 07.10. 23:34, Rat 23:50)
Bedingung: 25 ausgebildete Streitkolbenkaempfer ab Tick 0, kuerzeste Zeit gewinnt, Beliebtheit faellt nie unter 50.
Marken: gemessen (Register) / abgelesen (liga_ai.json) / gerechnet / offen.

**Was die Bedingung aendert**
- Die Kasse der 10er-Laeufe (Stufe 11 bis Beliebtheit 0, L31) ist verboten.
- Unter 50 wandert niemand ab: Zuzug 50-54 = +5, ab 95 = +40 (abgelesen, L22) -> L30/L32 (verlorene Kaempfer) faellt weg,
  der Modul-Befehl "Bauer gezielt waehlen" wird unnoetig.
- 25 = 5 x 5: Keulen und Leder gehen genau in 5er-Kaeufen auf, Einzelkauf (L33) unnoetig.
- Bedarf alles gekauft: 5x300 Keulen + 5x160 Leder + 25x20 Anwerben = 2.800 Gold (abgelesen).
- Beliebtheit je Woche (Anzeige = Tabelle/25, abgelesen): Steuer Stufe 2 +1 (0 Gold), 6 -8 (1,00/Kopf/Monat), 8 -15 (1,65),
  9 -20 (2,00), 10 -30 (2,75), 11 -40 (4,00); Rationen extra +5, doppelt +10; 2/3/4 Nahrungssorten +1/+3/+5;
  Gute Dinge bis +7 (Maibaum/Garten/Tanzbaer 30 G, Statue/Schrein 40 G; Leistung der Arbeiter sinkt bis 60 %);
  Bier (Schwellen 20/40/80/100) und Kirche (Bonus 30) - Bedeutung offen.
- Gemessen ist nur: Stufe 11 ohne Extras = -6 Punkte je 100 Ticks, Wochenschritt ~12 (L24).
- **Kernsatz (gerechnet):** Ohne Beliebtheits-Quellen haelt nur Stufe 2 (+1) - und die zahlt 0 Gold. Dauersteuer gibt es
  nur so hoch, wie Quellen sie tragen. Einnahme = Leute x Gold je Kopf (Stufe) / 800 Ticks + Verkauf; 70 Leute bei Stufe 9
  = 175 Gold je 1.000 Ticks.

### Hauptstrategie "Haushalt" (Vorsitz)
1. Tick 0-1.500: Eroeffnung wie Lauf 64/69 (Holzfaeller, Steinbrueche, Huetten, Aepfel) + 4 Milchviehhoefe vor ~1.500 (L14).
2. Wachstum: Steuer Stufe 2, Beliebtheit hoch halten (Zuzug +40), Wohnraum so gross wie Arbeitsplaetze erlauben (L27: max 24 am Feuer).
   Kaese aus den Hoefen = 2. Sorte; 3 Gerbereien spaetestens mit der ersten Kuh (~1.400-2.000 nach dem Hof); Leder selbst spart ~500 Gold.
3. Kasse ab Wohnraum-Ziel: Gute Dinge sofort (kein Arbeiter, kein Vorlauf), doppelte Rationen solange der Vorrat reicht.
   Regler: Stufe 11, solange die Beliebtheit nach dem naechsten Wochenschritt noch >= 62 ist (Konto 100 -> 62 abheben),
   danach die hoechste Stufe, die haelt. Der Regler misst seine Steigung je Stufe selbst (Wochenschritte) statt sie zu raten.
4. Anwerben laufend: je 5 Keulen kaufen, sobald bezahlbar; Leder eigenes, Rest kaufen; Bauern vom Feuer, sonst Start-Soldaten aufloesen.
5. Kein Abriss am Ende (Lauf 69). Lauf ungueltig, sobald einmal Beliebtheit < 50 gemessen (vorher festgelegt).

### Fuenf Gegenentwuerfe
- Skeptiker "Sicherheitsabstand": nur gemessene Ketten (Aepfel doppelt), Band >= 70, alles kaufen; doppelt +10, 2 Sorten +1
  -> Stufe 6 haelt (70 Leute: ~88 G je 1.000 Ticks). Warnt: B9 (6 Kuehe, kein Leder, Ursache nie gesucht), Streuung 54/57.
- Grundsatz-Denker "Weniger brauchen": Leder selbst (4 Hoefe 28 H 60 G + 3 Gerbereien 45 H 9 S 225 G statt 800 G);
  Schmiede verworfen (Eisen 54 G gegen Keule 60 G, Mine erst ~6.500 Ticks nach Bau, B9).
- Visionaer "Bierkoenig": Hopfen (10 H 35 G) + Brauerei (16 H) + Gasthaus (16 H 12 S 50 G); Bier traegt Steuer UND verkauft
  sich fuer 24 G je Fass (Aepfel 3, Kaese 6). Ertrag und Bierwirkung ungemessen, ~4.000 Ticks Vorlauf (L10).
- Aussenstehender "Arbeit statt Steuer": 2 Steinbrueche = 12 Stein je 1.000 Ticks (L4) = 60 G beim Verkauf (5 je Stein) -
  pro Arbeiter mehr als Dauersteuer Stufe 9 (2,5 je Kopf und 1.000 Ticks). So viele Steinbrueche, wie Stein liegt.
- Macher "Gute Dinge sofort": Lauf-64-Kette, Kasse ersetzt durch Regler + Gute Dinge + doppelte Rationen; einziger Hebel ohne Vorlauf.

### Urteil
- Einig: Gold ist der Engpass; ohne Quellen keine Dauersteuer; der Regler muss den Wochenschritt (~12) vorausschauen.
- Streit: neue Ketten (Leder, Bier) gegen nur Gemessenes; Gute Dinge senken die Leistung der Gerber/Holzfaeller.
- Fast uebersehen: Leute sind der staerkste Hebel (Einnahme waechst linear); doppelte Rationen kosten Nahrung je Kopf - ungemessen.
- Empfehlung: Haushalt, gebaut in der Reihenfolge der Belege: Regler + Gute Dinge + Rationen zuerst, Leder/Bier/Stein als
  Knoepfe fuer den Lernkreis.
- Erster Schritt: Beliebtheits-Regler in erstes_spiel.py (Vorschau Wochenschritt, Steigung je Stufe gemessen, Protokoll "nie unter 50"), dann Lauf 1.

## Plan 25 Streitkolbenkaempfer in hoechstens 24 Monaten (Daniel 08.10.2026)

### Ziel und ehrlicher Ausgangspunkt

- 1 Monat = 800 Ticks, 16 Monate = 12.800 Ticks, 18 Monate = 14.400 Ticks und 24 Monate = 19.200 Ticks
  (`Wissensstand.md`, Kalender gemessen).
- Daniels Wertung vom 08.10.: Der 25. Streitkolbenkaempfer muss spaetestens bei Tick 19.200 stehen. Tick 14.400
  oder frueher ist **sehr gut**; alles unter Tick 12.800 ist **sehr sehr gut**. Schnellste gueltige Zeit gewinnt.
- Der beste bisherige Lauf erreichte 25 bei Tick 16.753 = 20,94 Monaten. Er liegt sicher unter 24 Monaten, aber nur
  einmal. Die anderen Haushalt-Laeufe lagen bei 21.348, 19.205, 17.716 und 16.966 Ticks; dabei wurden mehrere
  Stellgroessen geaendert. Der Rekord ist deshalb ein Startwert, noch kein belastbarer Normalwert.
- Die Kontrolllaeufe 6 sind nicht wertbar: eine B-Plantage blieb bis zu 1.459 Ticks nach A offen. Vor jedem Vergleich
  muss dieselbe Beststrategie drei gueltige Laeufe absolvieren. Gueltig: keine Beliebtheit unter 50 und keine B-Plantage
  mehr als 200 Ticks nach A offen. Rekord und Median werden getrennt gefuehrt.

### Gemeinsame Regel: Das spaeteste Glied entscheidet

Die KI minimiert nicht Gold, Holz oder die Zeit einer einzelnen Werkstatt. Sie minimiert jede Runde diese Zielzeit:

`Zielzeit = max(25. Keule, 25. Lederharnisch, Gold fuer die noch fehlenden Anwerbungen, noch fehlende Bauern, Kaserne/Waffenlager bereit)`

Gebaut wird nur das Glied, das diese Zielzeit im Moment am weitesten nach hinten schiebt. Fuer die Vorhersage zaehlen
nicht nur fertige Waren, sondern die ganze laufende Kette: Eisen im Minenvorrat und beim Traeger, Eisen/Keulen beim
Schmied, lebende und laufende Kuehe, Arbeit beim Gerber sowie Waren auf dem Weg zum Waffenlager. Erst der danach
verbleibende Rest wird am Markt gekauft. So kauft die KI nicht kurz vor einer eigenen Lieferung doppelt.

### Harte Reihenfolge

1. **Ressourcen vor Grundlinie (08.10. gemessen):** Ein Steinbruch erzeugt 4,1-5,2 Stein je 1.000 Ticks. Der Ochse traegt
   12; ein kurzer Hin-/Rueckumlauf braucht rund 500, ein 54-58-Felder-Weg rund 1.900-2.000 Ticks. Zusaetzliche
   Abholpausen machen die reine Gehzeit zu optimistisch: zwei Joche lieferten im selben Zeitfenster fast doppelt so viel
   wie eines. Daher zwei je fruehem Bruch, ein drittes nur bei weiter wachsendem Haufen. Eisen: eine gueltige Mine liefert
   bei 8-91 Feldern Weg stabil 0,588 Eisen je 1.000, eine satte Schmiede braucht 0,664 und macht 1,49 Keulen je Eisen;
   5 Minen tragen rund 4,4 Schmieden. Eine Messanordnung gilt nur, wenn die nach dem Bau neu gelesene Wegkarte jeden Eingang
   ueber einen freien Korridor mit dem richtigen Lagerteil und dem Waffenlager verbindet; Luftlinie oder dichtes
   Aneinanderbauen ohne Weg macht den Lauf ungueltig. Markt, Kornspeicher und Huetten stehen ausserhalb dieses Kerns.
   Die Gegenproben 5:8 (deutlich zu viele Schmieden) und 5:5 (leicht zu viele) sind abgeschlossen. Der Produktionslauf
   beginnt mit 5:4; eine fuenfte Schmiede ist nur mit gekauftem Eisen oder gemessenem Eisenstau erlaubt.
2. **Belegbare Grundlinie:** Die jetzige 16.753-Strategie drei gueltige Male mit den neuen Ressourcenwerten laufen lassen. Ziel fuer die
   Grundlinie: jeder Lauf unter 19.200; Bestzeit und Median notieren.
3. **Stein frueh freimachen:** Die beiden Steinbrueche stehen schon frueh, aber im Rekordlauf kam der erste Stein erst
   bei Tick 7.640, weil die Ochsenjoche erst nach dem ersten Holzschub kamen. Direkt nach dem neuen Lager werden deshalb
   zwei Joche je aktivem fruehem Bruch vorgesehen. Erstes Zwischenziel: erster gelieferter Stein vor Tick 3.500. Ohne
   diesen Beleg startet keine grosse Waffenbau-Variante.
4. **Leder zuerst:** Vier Milchviehhoefe und zwei Gerbereien sind der erste Produktionsversuch. Das bindet sechs
   Arbeiterplaetze, braucht 58 Holz, 6 Stein und 210 Gold und kann nach L39 ungefaehr 25 Leder bis vor Tick 14.400
   liefern, wenn die Hoefe bis etwa Tick 1.500 und die Gerbereien mit den ersten Kuehen stehen. Fehlendes Leder wird
   erst am Endpunkt in Fuenferlosen gekauft.
5. **Keulen nur hinter dem Stein-Tor:** Danach beginnt die Eisenkette mit fuenf Minen und vier Schmieden. Die Startwerte
   folgen L40: Mine 0,588 Eisen je 1.000 Ticks, Schmiede bei voller Versorgung 0,664 Eisen und rund 1 Keule je 1.000;
   gemessen sind 1,49 Keulen je Eisen. Eine fuenfte Schmiede kommt nur bei Eisenstau oder geplantem Markteisen hinzu;
   acht Schmieden auf fuenf Minen sind als Hunger-Gegenprobe widerlegt. Gekauftes Eisen ist kein Standardweg: ein Fuenferlos spart
   gegen fertige Keulen nur 30 Gold und kostet zusaetzlich Schmiedezeit.
6. **Arbeiter umschichten statt Bevoelkerung aufblasen:** Ziel 90 bleibt der Startwert; 110 war mit 16.966 langsamer.
   Spaete Holzfaeller mit nur 0,3-0,4 Holz je 1.000 Ticks werden nicht weiter gebaut, sobald Mine, Schmiede oder Gerber
   die Zielzeit staerker senken. Die 90 Leute werden zuerst in Nahrung, dann in die aktuelle Engpasskette gesetzt.
7. **Erst Wirtschaft, dann Armee:** Solange eine Mine, Schmiede, Gerberei oder ein Transporter die Zielzeit noch senkt,
   wird kein Streitkolbenkaempfer angeworben. Keulen und Leder werden gesammelt, das Gold arbeitet weiter. Erst wenn die
   Wirtschaftsrechnung keine rechtzeitig amortisierte Erweiterung mehr findet, beginnt das Anwerben am Stueck.
8. **Markt als Ziellinien-Werkzeug:** Ab Tick 12.000 werden keine Betriebe mehr gebaut, deren erste echte Lieferung vor
   Tick 14.400 nicht sicher ist. Die Bilanz reserviert 20 Gold je noch fehlendem Kaempfer und kauft nur den aufgerundeten Rest
   an Keulen und Leder. Ab Tick 17.500 gilt die 24-Monats-Sicherung: alles Verkaufbare in Gold umwandeln und jeden noch
   fehlenden Fuenferblock kaufen; keine neue Langfrist-Investition.

### Messmarken und Abbruchregeln

| Marke | Soll fuer den 18-Monats-Versuch | Wenn sie verfehlt wird |
|---|---:|---|
| B-Plantagen nach A | hoechstens 200 Ticks | Lauf als technisch verfaelscht markieren |
| erster Stein im Lager | vor Tick 3.500 | Joch-/Holz-Reihenfolge verbessern, keine Vollkette werten |
| 4 Hoefe + 2 Gerbereien | bis Tick 3.000 | Leder-Variante abbrechen oder Restkauf vorrechnen |
| 5 Minen + 4 Schmieden | nur wenn Rohstoffe und Arbeiter reichen, spaetestens Tick 5.500 | kleiner starten; keine Gebaeude auf Kredit planen |
| 10 Keulen + 10 Leder | bis Tick 9.000 | Restbedarf neu rechnen und Marktpfad vorbereiten |
| Kaufentscheidung | Tick 12.000 | unfertige Arbeit mitzaehlen, nur echten Rest kaufen |
| Sehr-sehr-gut-Marke | vor Tick 12.800 | verpasst nur diese Wertung; Lauf fuer 18-Monats-Ziel fortsetzen |
| Sehr-gut-Marke | Tick 14.400 | Lauf ist sehr gut; danach nur noch Bestzeit oder 24-Monats-Sicherung |
| Sicherungsumschaltung | Tick 17.500 | investieren stoppen, Endkauf und Anwerben |
| Harte Grenze | Tick 19.200 | Lauf gescheitert |

### Versuchsfolge

1. Drei Wiederholungen der Grundlinie 16.753, nachdem die B-Plantage nicht mehr haengen kann.
2. Nur fruehe Ochsenjoche aendern; drei Laeufe. Damit wird belegt, ob frueher Stein wirklich die Endzeit senkt.
3. Auf dem besseren Stand Lederkette zuschalten; drei Laeufe.
4. Erst danach Eisen/Schmieden zuschalten; drei Laeufe. Die kleinste voll versorgte Variante beginnt 5/4, weitere Gebaeude nur nach
   der laufenden Zielzeitrechnung.
5. Sieger ist die kleinste Regel, deren drei gueltige Laeufe alle unter 19.200 bleiben; der schnellste Einzellauf ist
   der Rekord. Die Wertung **sehr gut** ist bei hoechstens 14.400 erreicht; **sehr sehr gut** nur unter 12.800.

### Mehrere Instanzen und kluger Fruehabbruch

- Die vorhandene `werkzeug/serie.py` verteilt Laeufe ueber `SHC_INSTANZ`. Mehrere Instanzen sind bereits belegt, aber
  nicht gleich schnell im Entscheiden: Instanz 3 hatte parallel weniger Lenker-Runden als Instanz 1. Deshalb bekommt
  jede Variante gleich viele Laeufe auf jeder verwendeten Instanz; verglichen wird zuerst innerhalb derselben Instanz
  und erst danach gemeinsam. Instanznummer, Code-Kennung, Tempo und Lenker-Runden gehoeren zu jedem Ergebnis.
- Jeder Lauf verfolgt nacheinander drei Ziellinien: unter 12.800, hoechstens 14.400, hoechstens 19.200. Wird die
  optimistische Obergrenze fuer eine Ziellinie unterschritten, faellt der Lauf nur auf die naechste Ziellinie zurueck;
  er wird nicht vorschnell ganz verworfen.
- Fuer jede Ziellinie rechnet der Abbruchwaechter absichtlich zu Daniels Gunsten:

  `Gold maximal = Gold jetzt + verkaufbarer Ueberschuss im Lager + rechtzeitig fertiger Ueberschuss + bestmoegliche Steuern und Produktion bis zur Ziellinie + sichere Abrissrueckgabe`

  `Gold noetig = 20 x noch fehlende Kaempfer + Marktpreis der bis dahin fehlenden Keulen und Leder + noch zwingende Baukosten`

  Nur wenn selbst `Gold maximal < Gold noetig` ist, ist die Ziellinie wirklich unmoeglich. Fuer Keulen, Leder und
  Pflichtbauten reservierte Waren sind kein verkaufbarer Ueberschuss. Laufende Ware in Mine, Transport, Schmiede, Kuh
  und Gerberei zaehlt dabei genau einmal; unsichere kuenftige Ertraege werden mit der besten
  bisher gemessenen Rate angesetzt, damit der Waechter keinen noch rettbaren Lauf abbricht.
- Ein Lauf endet vollstaendig, wenn auch Tick 19.200 rechnerisch nicht mehr erreichbar ist oder eine technische
  Bedingung verletzt wurde. Reine Suchlaeufe duerfen ausserdem enden, sobald sie die aktuelle Bestzeit selbst unter
  optimaler Rechnung nicht mehr schlagen koennen; die drei Bestaetigungslaeufe einer Siegerstrategie laufen trotzdem
  bis zum 25. Kaempfer oder zur harten Unmoeglichkeit.
- Gegenprobe fuer den Waechter: Ein kuenstlich goldarmer Stand muss abbrechen; derselbe Stand mit genau einem noch
  rechtzeitig eintreffenden verkaufbaren Los darf nicht abbrechen. Erst dann darf der Waechter Serienzeit sparen.

### Gegenprobe vor dem Bauen

- **Ueberladung:** Die geplante 4-Minen-/6-Schmieden-Kette samt 4 Hoefen und 2 Gerbereien kostet 258 Holz, 78 Stein
  und 20 Arbeiterplaetze; mit Waffenlager und Kaserne sind es 263 Holz und 90 Stein. Sie darf nicht als fester Bauplan
  starten, bevor die reale Lage diese Mittel zeigt; sonst wird nur Rohstoffmangel gemessen.
- **Doppelkauf:** Die Restbilanz muss laufende Ware mitzählen. Kann sie das noch nicht, darf sie im Versuch erst kaufen,
  wenn keine eigene Lieferung vor der Zielmarke mehr moeglich ist.
- **Glueck:** Ein einzelner 16.753-Lauf beweist nur den Rekord. Fuer eine belastbare 24-Monats-Strategie muessen drei
  gueltige Wiederholungen unter 19.200 liegen.

## Skalierung auf 50 und 100 (09.10.)

- Der letzte gueltige 50er-Lauf erreichte das Ziel bei Tick 24.625. Die gruppierte, rueckgemeldete Ochsenregel brauchte
  dabei 12 Joche statt der fehlerhaften 22. Ein 100er-Lauf wird erst nach Daniels Startsignal wieder ausgefuehrt.
- Die Waffenbetriebe werden nun als gemeinsame Folge geplant: Waffenlager, Gerber, Schmiede, Gerber, Schmiede. Fehlt
  die erste Kuh noch, darf genau eine Schmiede vorziehen; der Gerber verschwindet nicht aus dem Plan. Bereits gebaute
  Werkstatteingaenge bleiben bei jeder Neuplanung geschuetzt.
- Der Produktionslauf hat harte Lagerobergrenzen von 150 Holz, 50 Stein und 10 Eisen sowie hoechstens acht Lagerteile.
  Strengere unmittelbare Baureserven gelten weiter. Ueberschuss wird gebuendelt verkauft, damit die Produktion den
  Verkauf nicht ueberholt.
- Das Endspiel leert und zerlegt die Wirtschaft erst, wenn verkaufbare Waren und nur 70 Prozent des berechneten
  Abrisswertes den gesamten Restbedarf plus 50 Gold decken und nach dem Abriss genug Bauern vorhanden sind. Nahrung,
  die im Haushaltslauf nicht verkauft wird, zaehlt auch in der Vorpruefung nicht als Gold.
- Rekrutierung erfolgt in sicheren Wellen bis fuenf: `euroRecruit` setzt den gewaehlten Bauern noch im selben Aufruf um,
  daher nimmt der naechste Befehl eine andere Einheiten-Nummer. Die echte Feuerzahl begrenzt die Menge; das Feld
  `arbeitsplatz` darf sie nicht nochmals filtern, denn Wartende tragen dort die wechselnde Bergfriednummer. Zustand 109
  gehoert zu einer bereits laufenden Umwandlung und wird ignoriert; bei irgendeinem sichtbaren Abwanderer 110 wartet die
  ganze neue Welle. Die naechste beginnt erst nach vollstaendig erreichter Sollzahl, nie nach blosser Teilankunft erneut.
  Reparaturlauf `1010c`: komplette Produktion 8/7/6, Endspiel 24.002, erste Fuenferwelle 5/5 bestaetigt; danach deckte
  der falsche Arbeitsplatzfilter die 48 Wartenden nicht mehr auf und der Lauf blieb bei 14/50 bis Tick 40.033 stehen.
- Der erste freigegebene 50er-Lauf dieses Standes endete technisch bei Tick 14.257: Alle sechs gebauten Milchviehhoefe
  lagen ausserhalb des festen 71x71-Kartenausschnitts um das Vorratslager. Der Planer bekam dadurch eine Hofliste,
  aber kein einziges sichtbares Hoftor und lehnte jeden Waffenlagerplatz ab. Neue Regel: Der Kartenrahmen umfasst den
  Vorrats-/Waffenlageranker und die vollstaendigen Grundrisse aller tatsaechlich gebauten Hoefe plus 35 Felder Rand;
  die 400x400-Spielkarte ist die feste Obergrenze. Die Gegenprobe bildet den alten Fernhof-Fehler, den reparierten
  Fernhof und einen unveraenderten Nahhof ab. Ein neuer echter Lauf beginnt erst nach Daniels neuem Startsignal.
- Der naechste freigegebene 50er-Lauf war technisch gueltig, aber mit Tick 30.331 klar zu langsam. Das Endspiel begann
  bei 25.615; der Werkstattbau dagegen erst bei 14.927. Ein vom Spiel abgelehnter Schmiedeplatz wurde trotz neuer
  Wegkarte immer wieder gewaehlt, ebenso derselbe Platz der fuenften Eisenmine. Darum standen am Endspiel nur eine von
  sieben Schmieden, sechs Gerber und vier von acht Minen; der Markt ersetzte die fehlende Produktion. Neue Regel:
  Hof plus Minenkern startet den Werkstattplan schon vor dem ersten abgelieferten Eisen. Nach zwei echten
  Platzablehnungen wird die gesamte ueberlappende 4x4-Werkstattflaeche beziehungsweise der Minenort fuer diese Partie
  gesperrt; Rohstoffmangel darf keine Sperre erzeugen. Gegenprobe des Werkstattplaners: 4/4 gruen.
