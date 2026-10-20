# Arbeitsregel fuer dieses Repo

Nach jeder echten Partie: Mitschrift (mit START-BEFEHL-Zeile), neu angelegte Karten-/Plan-Dateien,
Lageprotokoll (unter 50 MB) und geaenderte Umgebung committen und pushen.
Einzelheiten: README.md, Abschnitt "Pflicht nach jeder Partie" (Daniel 17.10.2026).

Backlog (Daniel 19.10.2026: nichts vergessen, wissen was gebaut ist und wo es steht): EINE Liste, `docs/backlog/backlog.json`,
Ansicht `docs/backlog/Backlog.html`. Neue Arbeit zuerst als Punkt anlegen (`uv run selfaware run backlog neu ...`), jeder Commit nennt
seinen Punkt (B-Nummer) in der Nachricht, danach Stand setzen (`stand B-n gebaut --commit ...`) und `uv run selfaware run backlog bauen`.
Nie loeschen, nur den Stand aendern. "Commits ohne Punkt" in Backlog.html muss 0 sein.
Reihenfolge (Daniel 19.10. 22:02): das Wichtigste - das, woran gerade gearbeitet wird - steht oben (`uv run selfaware run backlog rang B-n 1`,
Stand `in_arbeit`). Vor jedem Schritt und jedem Bericht `uv run selfaware run backlog fokus`: passt die eigene Arbeit nicht
zum obersten Punkt, zurueck dorthin. Was dabei erledigt wird, sofort im Backlog abhaken.
Jede Partie wird Trainingsdaten (Daniel 19.10.2026 22:48): nach jeder Partie `uv run selfaware run partie_lernen <konsole> <lage>`
(die SamurAI-Wache startet es am Partieende selbst) - eine Zeile je Partie in `data/research/lernen/partien.jsonl`; Lehren ins
Wissensregister, offene Folgen ins Backlog.

Read [AGENTS.md](AGENTS.md), [docs/HANDOFF.md](docs/HANDOFF.md), and
[docs/ORGANIZATION.md](docs/ORGANIZATION.md). Direct user instructions determine
the active task; register that task before changing focus.
