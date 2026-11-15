# Arbeitsregel fuer dieses Repo

**VOR JEDEM SPIELSTART (Daniel 15.11.2026):** erst Daniel fragen - Karte, Gegner, Teams, Positionen, Gold. Fragebogen und Weg:
`../VillageStudio/doku/Partie-starten.md`. Nie per Skript starten; die Startsperre in `befehl.sende` verwirft `eigenesGefecht`
ohne `data/research/partie_freigabe.json` mit Daniels Wortlaut.

Nach jeder echten Partie: Mitschrift (mit START-BEFEHL-Zeile), neu angelegte Karten-/Plan-Dateien,
Lageprotokoll (unter 50 MB) und geaenderte Umgebung committen und pushen.
Einzelheiten: README.md, Abschnitt "Pflicht nach jeder Partie" (Daniel 17.10.2026).

Backlog = die GitHub-Issues dieses Repos (Daniel 15.11.2026 19:49: "wie ein klassischer Backlog in GitHub ... sofort von ueberall
und egal welcher Sitzung"; 19:53: nur noch die Punkte mit hoechstem Impact). EINE Liste: https://github.com/DanielFleger/Selfaware-AI/issues
- die fruehere docs/backlog/backlog.json ist dort als Issues uebernommen (Titel beginnt mit der alten B-Nummer) und liegt nur noch in der
Git-Geschichte. Neue Arbeit zuerst als Issue anlegen (`uv run selfaware run backlog neu --kategorie ... --unter ... ...`, Kategorien in
`docs/backlog/kategorien.json`: Spielstart/Bedienung, Kampf, Wirtschaft, Struktur, KI-Denken), jeder Commit nennt seinen Punkt (`#n` oder
die alte `B-n`) in der Nachricht, danach Stand setzen (`uv run selfaware run backlog stand #n gebaut --commit ...`); `backlog pruefen`
muss 0 Commits ohne Punkt melden. Nie loeschen, nur schliessen. Daniel 19:53: "wir machen nur noch die Punkte mit hoechstem impact
value" - welche das sind, traegt das Etikett "Impact: hoch", vergeben nur mit Daniels Ja; was gerade dran ist, traegt "Fokus" bzw. "in Arbeit". Vor jedem Schritt und jedem Bericht `uv run selfaware run backlog fokus`.
Jede Partie wird Trainingsdaten (Daniel 19.10.2026 22:48): nach jeder Partie `uv run selfaware run partie_lernen <konsole> <lage>`
(die SamurAI-Wache startet es am Partieende selbst) - eine Zeile je Partie in `data/research/lernen/partien.jsonl`; Lehren ins
Wissensregister, offene Folgen ins Backlog.

Read [AGENTS.md](AGENTS.md), [docs/HANDOFF.md](docs/HANDOFF.md), and
[docs/ORGANIZATION.md](docs/ORGANIZATION.md). Direct user instructions determine
the active task; register that task before changing focus.
