# Ergebnis Lauf S (B-142)

Plan: `docs/plans/Plan_Lauf_S.md`. Wird je Szene fortgeschrieben. Instanz 2, `Liga_Grumpy Neighbors` im Karteneditor, Spielart `currentGameMode` 0, `gameMode_2` 1.

## Was die erste Szene über den Aufbau gezeigt hat

| Frage aus dem Plan | Antwort |
|---|---|
| Steht die Karte in der Editor-Liste? | Ja, Eintrag 5 von 92, keine Kopie nötig |
| Hängt das Laden? | Nein |
| `currentGameMode` im Editor nach frischem Start | 0, `gameMode_2` 1 |
| Freie Felder im laufenden Spiel | 57.174 (aus der Kartendatei gerechnet: 57.247) |
| Abräumen | Einheiten der Karte 274 Takte, Szene 321 Takte. Steintod, nicht die alte Wartezeit von 400. 132 Einheiten bleiben stehen, sie gehören keinem der 8 Spieler (vermutlich Tiere, die Kontrolle blieb unberührt) |
| Setzen | 381 Einheiten in 1,33 s im angehaltenen Spiel |

## Szene Nahkampf, 03.11. 19:15

190 Paare, je Paar direkt nebeneinander, kein Befehl. 509 Rahmen in 508 Takten, Tempo 40, kein Takt fehlt, keiner gemischt. Kontrolle unberührt. Beleg: `nahkampf.regeln.json`, Befehl `python -m selfaware.tools.analysis.auge_regeln <aufzeichnung>`, Aufzeichnung `laeufe/lauf_s_20261103_191555_nahkampf.auge` (lokal).

| Urteil | Zeilen von 361 | |
|---|---|---|
| Bestätigt: Verlust genau der Tabellenwert | 320 | |
| Schlägt nicht, wie vorhergesagt | 38 | Leiterträger (E_LADDER 29), Ingenieur (E_ENGINEER 30): `DAT_UNIT_CAN_MELEE` 0 |
| Weicht ab, erklärt | 3 | siehe unten |

- **Der Nahkampf trifft jeden Takt, bei allen Arten.** 81.689 Abstände zwischen zwei Treffern, alle genau 1 Takt.
- **Er beginnt sofort.** Erster Treffer nach 1 oder 2 Takten, bei jedem Paar, ohne Befehl und ohne auf die Prüfrunde zu warten. Die Grenze von 507 Takten war viel zu groß.
- **Schützen schlagen direkt nebeneinander zu,** statt zu schießen, mit dem Tabellenwert (112 von 114 Zeilen, die 2 anderen stehen unten).
- **3 Fremdgeschosse** im selben Takt wie ein Schlag (1.420 = 20 + Pfeil 1.400): Vermutlich haben Schützen ein anderes Paar beschossen, der Täter ist nicht nachgewiesen. Der Prüfer rechnet solche Fälle heraus.

Die 3 Abweichungen:

| Paar | Befund | Erklärung |
|---|---|---|
| Tunnelgräber (TUNNELER 5) gegen Berittenen Bogenschützen (A_HARCHER 74), beide Richtungen | 132 und 130 Takte lang 37 mehr je Takt, einmal 75 mehr | Vermutet: Feuer eines benachbarten Feuerwerfers. 17.10. gemessen: Brand rund 37 je Takt (Handbuch). Der Täter ist nicht nachgewiesen |
| Feuerwerfer (A_FIRETHROWER 76) gegen arabischen Bogenschützen (A_ARCHER 70) | Der letzte Treffer nahm mehr als den Tabellenwert: 442 Schläge zu 30, dann der Rest | Offen. Möglich ist der Brandtod, das gehört in die Szene Sonderfälle |
