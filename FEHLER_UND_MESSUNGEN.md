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
