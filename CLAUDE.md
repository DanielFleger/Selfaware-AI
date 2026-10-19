# Arbeitsregel fuer dieses Repo

Nach jeder echten Partie: Mitschrift (mit START-BEFEHL-Zeile), neu angelegte Karten-/Plan-Dateien,
Lageprotokoll (unter 50 MB) und geaenderte Umgebung committen und pushen.
Einzelheiten: README.md, Abschnitt "Pflicht nach jeder Partie" (Daniel 17.10.2026).

Backlog (Daniel 19.10.2026: nichts vergessen, wissen was gebaut ist und wo es steht): EINE Liste, `backlog.json`,
Ansicht `Backlog.html`. Neue Arbeit zuerst als Punkt anlegen (`python werkzeug/backlog.py neu ...`), jeder Commit nennt
seinen Punkt (B-Nummer) in der Nachricht, danach Stand setzen (`stand B-n gebaut --commit ...`) und `backlog.py bauen`.
Nie loeschen, nur den Stand aendern. "Commits ohne Punkt" in Backlog.html muss 0 sein.
Reihenfolge (Daniel 19.10. 22:02): das Wichtigste - das, woran gerade gearbeitet wird - steht oben (`backlog.py rang B-n 1`,
Stand `in_arbeit`). Vor jedem Schritt und jedem Bericht `python werkzeug/backlog.py fokus`: passt die eigene Arbeit nicht
zum obersten Punkt, zurueck dorthin. Was dabei erledigt wird, sofort im Backlog abhaken.
Jede Partie wird Trainingsdaten (Daniel 19.10.2026 22:48): nach jeder Partie `python werkzeug/partie_lernen.py <konsole> <lage>`
(die SamurAI-Wache startet es am Partieende selbst) - eine Zeile je Partie in `daten/lernen/partien.jsonl`; Lehren ins
Wissensregister, offene Folgen ins Backlog.
