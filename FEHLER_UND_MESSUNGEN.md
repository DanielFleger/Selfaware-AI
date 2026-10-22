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
