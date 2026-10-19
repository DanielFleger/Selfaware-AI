# Arbeitsregel fuer dieses Repo

Nach jeder echten Partie: Mitschrift (mit START-BEFEHL-Zeile), neu angelegte Karten-/Plan-Dateien,
Lageprotokoll (unter 50 MB) und geaenderte Umgebung committen und pushen.
Einzelheiten: README.md, Abschnitt "Pflicht nach jeder Partie" (Daniel 17.10.2026).

Backlog (Daniel 19.10.2026: nichts vergessen, wissen was gebaut ist und wo es steht): EINE Liste, `backlog.json`,
Ansicht `Backlog.html`. Neue Arbeit zuerst als Punkt anlegen (`python werkzeug/backlog.py neu ...`), jeder Commit nennt
seinen Punkt (B-Nummer) in der Nachricht, danach Stand setzen (`stand B-n gebaut --commit ...`) und `backlog.py bauen`.
Nie loeschen, nur den Stand aendern. "Commits ohne Punkt" in Backlog.html muss 0 sein.
