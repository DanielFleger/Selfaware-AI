# Selfaware AI

Lokale Entwicklungsfassung, derzeit kein Store-Modul. Einrichtung und Start
erfolgen ueber die separate Selfaware-Anwendung. Diese startet das Spiel und
den Controller; SamurAI steuert die ausgewaehlten Plaetze in frischen Gefechten.
Keine zusaetzliche Python-Einrichtung, kein KI-Abonnement, keine betreuende KI.

Die KI protokolliert Beobachtungen und belegte Partieausgaenge. Ihr vorhandener
Lerner speichert gemessene Verluste und Laufzeiten und nutzt sie fuer folgende
Entscheidungen. Dieser Forschungsstand verspricht weder selbststaendige
Quellcode-Umbauten noch eine nachgewiesene Verbesserung der Spielstaerke.

Benoetigt Windows mit 64 Bit, UCP 3.0.7 und Stronghold Crusader 1.41.
SamurAI belegt den Abt-Platz. Lernstand und Startfehler liegen unter Dokumente/Selfaware AI.
Unter Customisations -> Selfaware AI: Starteinheiten lassen sich die Starttruppen
einstellen. Standard: 4 Assassinen und 6 arabische Bogenschuetzen anstelle der
Abt-Truppen. Die Einstellung gilt ab dem naechsten Spielstart fuer neue Gefechte.
Die alte Dateikommunikation und feste Spieladressen verhindern derzeit eine
Store-Freigabe. Eine Signatur allein behebt diese Grenzen nicht.
