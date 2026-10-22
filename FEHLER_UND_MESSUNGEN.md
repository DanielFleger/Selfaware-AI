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
