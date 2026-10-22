# SAI: Fehler und Gegenproben — 22.10.2026

Ziel von Daniel: erst unter 28.800 Takte (3 Spieljahre), danach weiter senken;
24.000 Takte (2,5 Jahre) sind das naechste Leistungsziel. Ein Sieg ersetzt keine
Wiederholungsserie. Entwicklungslaeufe bleiben von der 20-Partien-Abnahme getrennt.

## Gemeinsame Regeln

* Gemessene Startpositionen bestimmen das eigene Gebiet **vor** jeder Planung.
  Der Baupruefer ist die letzte Absicherung, kein Ersatz fuer richtige Kandidaten.
* Eine Quittung bestaetigt die Bearbeitung eines Befehls, nicht seine Spielwirkung.
* Eine Messung gehoert erst zum neuen Lauf, wenn dessen Startsignal zu dessen
  tatsaechlichem Prozess gehoert. Ein hoher Takt kann noch die vorige Partie sein.
* Sieg: natives Spielende, beide Gegner ausgeschieden, beide eigenen Lords lebend.
  Vor Spielende sind die Lebensflaggen nicht als Todesnachweis verwendbar.

## Befunde

| Befund | Beleg | Bearbeitung / offene Gegenprobe |
|---|---|---|
| Zweiter Spieler hatte nach der Optimierung keine eigenen Apfelplaetze; Kornspeicher-Ersatz war nicht spielgeprueft. | Letzter Claude-Lauf 22.10. 19:12; gesicherte Mitschriften im Kontextordner. | Gebietsfilter vor Optimierung, kein erfundener Ersatz. Negative Platzprobe und beide Nordplaetze bestanden; erste Branching-Partie startete mit beiden Speichern. |
| Laufender Ertragsplaner bot trotzdem Partnerland an, z.B. SP1 (305,260). | `daten/branching_20261022_192955_sp1_konsole.txt`: KAUSAL-Angebote und Bauablehnungen. | Derselbe Gebietsfilter jetzt auch im Ertragsplaner. Beide echten Karten getestet; Ruecksetzen auf alte Regel macht beide Gegenproben rot. Live-Abnahme noch ausstehend. |
| Vorbeugender Kornring verbrauchte frueh Holz und sendete spaeter dieselbe fehlende Mauerkachel wiederholt. | Erste Partie: Grubenbau ab T682; Kachel (196,360) noch ab T31.000 wiederholt. | Vergleichslauf `20261022_194200` mit `kornring=nein`; reaktive Fallenwache bleibt aktiv. Hypothese, noch kein bestaetigter Vorteil. |
| Gefechtsrechnung unterschlaegt Anmarsch und Engpaesse. | SP1 Angriff T25.970: Modell 340 Kampftakte; Lordtod erst T32.131. | Modell gilt nur fuer den hypothetischen Kontaktkampf; gesamte Zeit bis Lordtod gesondert messen. Korrektur offen. |
| Alter Kanal darf eine lebende Sendesperre nach 8 Sekunden entfernen, obwohl bis 20 Sekunden auf Quittung gewartet wird. | `werkzeug/befehl.py`, `_sperren` und `sende`. | Korrektur und Prozess-Gegenprobe offen; keinen als erfolgreich verschluckten Timeout akzeptieren. |
| Partner-Laufmarke wird bei `freigeben` nicht entfernt. | `<pid> partner` wird gegen `<pid>` verglichen; erste Aufraeum-Pause meldete Kanal belegt. | Korrektur offen. Beeinflusst den gemessenen nativen Sieg nicht. |
| Erster Beginn des zweiten Beobachters las noch das alte Spielende. | `branching_20261022_194200_observed.jsonl.gz`: T32.349, Ansicht29, vor neuem Start. | Altbeleg behalten; neuer Beobachter `_active` getrennt gestartet. Starter wartet kuenftig auf passende Prozesskennung im Startsignal. |
| GitHub-main und lokaler Spielzweig haben kollidierende Backlognummern. | B-134 bis B-139 haben unterschiedliche Inhalte. | Getrennte Quellen behalten; keine Aufgaben durch Nummerngleichheit ueberschreiben. Zusammenfuehrung offen (B-208). |

## Erste Partie, unabhaengiger Endnachweis

`20261022_192955`: nativer Endzustand spaetestens T32.347, Gardist und
Kriegsfuerst ausgeschieden, beide eigenen Lords 150.000/150.000 Leben.
219 taktkonsistente Beobachtungen im separaten Nur-Lese-Beobachter.
Ergebnis: dominanter Entwicklungssieg, **Geschwindigkeitsziel verfehlt**.
Die Befehls- und Schreibpruefung sowie vollstaendige Abnahmequalifikation fehlen;
dieser Lauf wird nicht als eine der 20 Abnahmepartien gewertet.

Reproduzierbare Auswertung und Gegenproben:

    python werkzeug/benchmark_pruefen.py
    python werkzeug/benchmark_auswerten.py daten/benchmarks/branching_20261022_192955_observed.jsonl.gz
    python werkzeug/ertragsgebiet_pruefen.py

Quelle fuer die geplante Betriebssystem-Sperre:
https://docs.python.org/3/library/msvcrt.html#msvcrt.locking

## Weitere Entwicklungslaeufe, 22.10.2026

Alle Zeiten sind Entwicklungsdaten, keine qualifizierte Abnahmeserie.

| Lauf | Ergebnis | Schluss |
|---|---|---|
| 194200 | Sieg T39960, beide eigenen Lords voll | Ohne Kornring langsamer; keine Verbesserung. |
| 200302 | Sieg T31447, beide eigenen Lords voll | Bisher schnellster beobachteter Sieg: 3,28 Jahre; Ziel weiterhin offen. |
| 201033 | Sieg T33334, beide eigenen Lords voll | Schnellere Befehlsvergabe allein beschleunigt den Sieg nicht. |
| 201647 | Sieg T36132, beide eigenen Lords voll | Vier Assassinen waren keine harte Grenze: zehn weitere erlaubt. Kein sauberer Vierer-Vergleich. |
| 202608 | Zeitgrenze T96000 ohne Sieg, keine Steuerungsfehler in beiden Konsolen | Harte Vierergrenze plus 50-Prozent-Heerbudget ist keine erfolgreiche Verbesserung. Mehrere Aenderungen: Ursache nicht isoliert. |

Allgemeine Auswertungsregel: Geordnetes Ende an der Spielzeitgrenze ist ein Zeitverlust, ein unerwartetes vorzeitiges Ende bleibt ungueltig. Gegenprobe: Lauf 202608 erreichte nachweislich T96000; Lauf 200050 scheiterte weit davor mit Schreibfehler. Der unabhaengige Beobachter war bisher auf 2000 Schleifendurchlaeufe begrenzt und brach bei langen Partien vor den Steuerungen ab. Er laeuft nun bis Spielende oder eigener dokumentierter Zeitgrenze. Fuer den alten Lauf wird kein fehlender Endnachweis erfunden.

Transport: Betriebssystem-Sperre, exakte eigene Quittung, atomare Veroeffentlichung und reservierte Nummernbloecke inzwischen umgesetzt und mit Gegenproben geprueft. Die vollstaendige Wirkungspruefung bleibt offen. Rueckwirkend sind dadurch alte Laeufe nicht qualifiziert.

Partner-Quittung und Wirkung sind getrennt: `befehl.sende` ueberschrieb einen angeforderten Wirkungsmarker mit der eigenen Empfangsquittung. Dadurch meldete der vorhandene Lader beim tatsaechlich geladenen Spielstand faelschlich einen Ladefehler und startete neu. Die angeforderte Marke bleibt nun zusaetzlich zur eigenen Quittung erforderlich. Sechs Dateikanal-Pruefungen bestanden; gezielter Rueckfall auf altes Verhalten scheitert an der verzoegerten Lademarke. Echte Gegenprobe: Sandkasten geladen bei T40967, Lade-Marke vorhanden, Probelauf erfolgreich, anschliessend fuenf arabische Schwertkaempfer gesetzt. Erste vorlaeufige Schadensmessung 127 statt bisherigem ungemessenem Ersatzwert 180 je Takt/Einheit; Wiederholungen mit Uhr aus demselben nativen Weltbild laufen. Keine Kampfabnahme daraus ableiten.

## Menue und Daniels Gegenproben, 22.10.2026

Verbindlich: keinerlei Maus-, Tastatur-, Fenster- oder Fokussteuerung. Nur Backend-Spielbefehle. Neue Matches ueber Hauptmenue 2, SelectCrusade 2, echte Karten-/KI-/Team-Handler, Lobby-Start 4; keine alten Speicherstaende. `menue_team.py` liest Karte, KI-Nummern, Gruppen und Positionen vor dem Start zurueck. David/Goliath sind KI 9/10, Grossmeister/Knappe 11/12.

SamurAI war im aiSwapper auf Abt (16), die alte Wache suchte Ratte (1) und steuerte nur einen Platz. Die Wache liest jetzt die eindeutige aktive SamurAI-Zuordnung und startet alle ausgewaehlten Plaetze. Sechs Zuordnungs-Gegenproben bestanden; am echten Menue-Match liefen beide Lenker fuer Spieler 1 und 4. Keine Aussage, dass jeder beliebige Windows-Startweg bereits automatisch die neue Wache startet.

Vorratslager: `processDamageToBuilding` 0x00516b80 verwirft Schaden bei `DAT_BuildingTypeHasHealth[type]==0`; aktive Tabelle 0x005b9458 bestaetigt Typ 10 = 0. Steinbruch Typ 20 bleibt angreifbar. Die Steinablage 21 hat in dieser Tabelle zwar 1, wird nach Daniels ausdruecklicher Mechanik-Gegenprobe und bereits dokumentiertem Altbefund separat ausgeschlossen. Gemeinsame Regel in `gebaeudeziele.py`, beide Zielwerttabellen und Altziele folgen ihr. Fuenf gezielte Gegenproben und 28 vorhandene Raid-Pruefungen bestanden.

Berittene: das vorhandene Modell kennt 44 Felder gegen 17 fuer Schleuderer; die alte Regel ritt trotzdem bis zum Zielpunkt, statt einen Schusspunkt zu bewerten. Jetzt wird bei echtem Reichweitenvorteil eine erreichbare Position ausserhalb gegnerischer Reichweite plus vier Feldern und innerhalb der eigenen konservativen Grenze gewaehlt. Alle Gegner der Gefahrenkarte zaehlen mit. Fuenf neue Pruefungen bestanden; drei gezielte Rueckfallproben scheitern am alten Verhalten. Live-Mitschrift 214153 enthaelt vorausschauendes Ausweichen und Beschuss aus 25 Feldern. Langfristiger Erfolg der Regel bleibt zu messen.

Menue-Match 213251: unabhaengiger Sieg spaetestens T43334 (4,51 Jahre), eigene Lords 1/4 je 150000. Wegen Korrekturen waehrend der Partie KEINE Abnahme. Daniels Einwand war berechtigt: Sieg beweist keinen gelungenen Hauptarmeestapel. Bei David T42801-42906 zeigen beide Lageprotokolle den grossen Lebensverlust mit Assassinen-/Bogen-Zielen, ohne Streitkolben-/Schwert-Ziel auf den Lord. Zwei Assassinen stehen im Abstand <=1, Zustand 106. Bei Goliath gab es bereits grossen Lebensverlust mit 2-5 arabischen Schwertkaempfern als Lord-Zielen, spaeter kamen Assassinen hinzu. Keine hitgenaue Schadenszuordnung vorhanden. Details: `daten/kampfnachweis_menue_20261022_213251.json`.

Nahkaempfer: Gruppengroesse war noch 5. Neu sind einzelne native Befehle (`trupp=1`) auf dasselbe Lord-Feld, anschliessend einzelne Angriffe. Nicht bereits zehn Felder daneben als angekommen behandeln. Drei neue Pruefungen und alle 63 Feldzugpruefungen bestanden; Altpruefung 23 simuliert jetzt die tatsaechliche Ankunft. Erst das neue Menue-Match 214858 gegen Grossmeister/Knappe kann die echte Wirkung nachweisen. Noch kein Nachweis fuer dominanten Sieg unter drei bzw. 2,5 Jahren.


## 22.10.2026: naechstes Team und Apfel-Nachpruefung

Grossmeister/Knappe: unabhängiger nativer Endnachweis T36307, beide eigenen Lords 150000/150000. 3,78 Spieljahre; kein qualifizierter Benchmark und kein isolierter Hauptarmee-Wirkungsnachweis.

Gemeinsame Ursache A/B: Platzablehnungen entfernten Sollorte dauerhaft. Jetzt bleiben sie ohne Pflicht-Ruecklage vorgemerkt und werden alle 1500 Ticks bei freiem Budget erneut versucht; nur ein echter Gebaeudebestand bestaetigt den Bau. Gegenfall: dauerhaft gesperrter Platz darf weder jede Runde Auftraege senden noch Anwerben sperren. Fuenf neue Gegenproben und vier bestehende B-Bestaetigungspruefungen bestanden. Dabei auch fehlenden Ressourcenabzug nach erfolgreicher B-Bestellung korrigiert. Die echte Nachpruefung eines spaeter freigewordenen Platzes im Spiel steht noch aus. Der fotografierte freie Platz ist nicht koordinatengenau identifiziert; eine vorherige native Probe am alten SP4-Sollort (325,254) hatte null erlaubte Bauorte gefunden.

Janitschar/Mirza frisch ueber Menuehandler gestartet: 20261022_220150, Starttick9, Spieler1/4 SamurAI, Spieler2/3 Gegner13/14. Beide Lenker melden Codekennung5e592e75 mit wirtschaft.py694bdc. Keine Bedienung von Maus/Tastatur, kein Spielstand. Daniels kurz erbetener Neustart wurde durch sein unmittelbares „nvm das ist schon“ aufgehoben; keine Beendigung/Neuordnung ausgefuehrt.


## 22.10.2026: Gelaende, Sicherheitsabstand, untätige Assassinen

Strukturregel: nur ein gerichteter nativer Weglink erlaubt den naechsten Bodenschritt. Gleiche Gebietsnummer erlaubt keinen Hoehensprung. Primaerquelle: daten/dekomp_weglinks2.c, Routine0x4999c0 liest HeightLayer und prueft Nachbarhoehen (+/-16). speicher.wegkarte lieferte schon Links, aber gefahrenschutz.Lage und gefahr.Karte verwarfen sie zugunsten eines freien 8-Nachbarn-Rasters. Bei Deckung ging zusaetzlich die gesamte Wegkarte verloren. Jetzt gerichtete gewichtete Suche ueber genau diese Links; Glaettung darf keine gesperrte Kante einfuegen; Hoehe/Boden werden mitgelesen. Brandziele brauchen einen tatsaechlich erreichbaren angrenzenden Platz ohne Klippensprung. Wegpunkte der einzelnen Raid-Einheiten werden exakt erreicht, statt schon vier Felder davor oder allein nach300Takten weiterzuschalten. Native Lua vor Installation gesichert und gegen vorherige Version verglichen.

Echte Gegenprobe: daten/hoehen_gegenprobe_20261022.npz und Ergebnis-JSON. Drei gleichgebietige freie Nachbarpaare mit Hoehensprung18-20 waren nativ gesperrt, im alten Raster jedoch moeglich; neue Wege3/3/4Felder benutzen ausschliesslich native Kanten, Suche jeweils~0,03s. Sieben neue Hoehenpruefungen mit Rampe, fehlender Rampe, Einbahn, Glaettung, Flachland, Gebaeude hinter Klippe und exakter Wegpunktankunft bestanden. Das beweist noch nicht das Ende des Pendelns im echten Kampf.

Reiter: fehlender sicherer Schusspunkt liess die Steuerung zur normalen Jagd durchfallen. Jetzt Rueckzug oder Halt statt Jagd; Anritt auf Arbeiter endet mit Abstand32-39 statt8Feldern, ein bereits sicher stehender Reiter darf schiessen. Auch Ausweichbefehle benutzen Wegplanung. Zwei neue Sicherheitsgegenproben und fuenf Reichweitenfaelle bestanden; die Anritt-Gegenprobe8 wurde bewusst auf den neuen Abstand angepasst.

Assassinen: ein festes Veto fuer alle Gruppenziele innerhalb45Feldern um Lords stand vor der Gefechtsrechnung. Es wurde entfernt; Erreichbarkeit, Mindestgruppenstaerke und anschliessende Rechnung mit Mindestrestleben bleiben erforderlich. Drei neue Kandidatengegenproben und zehn bestehende Lordanlaufpruefungen bestanden. Nicht behaupten, diese Modellrechnung garantiere einen echten Sieg.

Gemeinsame Nebenpruefung: Raids28/28, Gefahr8/8, Feldzug63/63 (echte temporaere Dateien ausserhalb der Dateisystemvirtualisierung). Janitschar/Mirza vorheriger Lauf endet nativ40701, beide eigenen Lords150000/150000,4,24Jahre. Frischer gleicher Gegnerlauf20261022_221719 startet mit Korrekturen ueber native Menuehandler, ohne Eingabesimulation/Spielstand. Eigene Spieler1/4 auf Sued-/Westseite, Gegner2/3 auf Ost-/Nordseite. Endwirkung noch offen.
