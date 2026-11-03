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

## Szene Laufen, 03.11. 19:30

19 Soldaten nebeneinander, ein Besitzer, 20 Felder, gerade und schräg, Tempo 200. Alle am Ziel nach 626 Takten. Beleg: `laufen.regeln.json`.

| Tempo-Wert der Tabelle | Takte je Feld | Arten |
|---|---|---|
| 1 | 16,0 | Bogenschütze, Speerträger, Streitkolbenkämpfer, Ritter, Leiterträger, Ingenieur, Tunnelgräber, arabischer Bogenschütze, Sklave, Schleuderer, Assassine, Berittener Bogenschütze |
| 2 | 23,95 | Armbrustschütze, Pikenier, Mönch, arabischer Schwertkämpfer, Feuerwerfer, Lord |
| 3 | 31,68 | Schwertkämpfer |

- **Regel: Takte je Feld = 8 x (Tempo-Wert + 1).** Innerhalb jeder Stufe sind alle Arten gleich, gerade und schräg kosten je Feld gleich viel. Gelesen wurde rund jeden 3. Takt, die 23,95 und 31,68 sind also 24 und 32 innerhalb des Ablesefehlers.
- **Das ist Gehen im Einzelspiel, ohne Feind.** Lauf-Werte aus echten Partien (L80) sind kleiner: Bogenschütze 11,5, Speerträger 13,5, Pikenier 24. Ob das Rennen ist, zeigt die Gegenprobe im Gefecht. Noch offen.

## Szene Beschuss, 03.11. 19:30

6 Schützenarten gegen alle 19 Arten, Abstand 8, kein Befehl, 868 Takte auf Tempo 40, kein Takt fehlt. Kontrolle unberührt. Beleg: `beschuss.regeln.json`.

**Mein Aufbau war falsch gedacht:** Schützen schießen nicht nur auf den nächsten Feind, sie treffen auch fremde Ziele, und der erste Treffer kommt spät (Takt 185 bis 787). Eine Wertung je Paar sagt darum nichts. **Die Regel hält trotzdem, gewertet nach dem Opfer:**

| Regel | Ergebnis |
|---|---|
| Jeder Verlust ist eine Summe aus Pfeil, Bolzen, Stein des Opfers und Feuer | 19 von 19 Arten: kein Betrag ungeklärt |
| Geschossarten gegen Arten gesehen | 54 von 57. Es fehlen Pfeil und Bolzen gegen Tunnelgräber und Stein gegen Leiterträger, dessen Stein- und Pfeilwert gleich sind |
| Schleuderer | Trifft mit dem Stein-Wert. Am 17.10. stand im Handbuch 400 gegen Assassine, jetzt ist es 900, vermutlich eine andere Einstellung damals |
| Feuer, gemessen | 37,5 je Flamme und Takt, gegen den Lord 12,5, gegen den Feuerwerfer selbst 5. Betrag abgerundet, mehrere Flammen addieren sich (37, 75, 112) |
| Schusstakt, aus den Abständen abgelesen | Bogenschütze 129, Armbrust 228, arabischer Bogenschütze 90, Schleuderer 56, Berittener Bogenschütze 78. Passt zum 17.10. Täter je Treffer ist hier nicht zugeordnet |

**Noch nicht beantwortet:** Trefferquote und Flugzeit (dafür müssen die Geschosse selbst ausgewertet werden), welches Ziel ein Schütze wählt, Reichweite. Das braucht eine Szene, in der jeder Schütze nur ein Ziel hat.

## Szene Lesen unter Last, 03.11. 19:37

**Daniels Vorgabe hält: Mit 2.412 Einheiten im Nahkampf zieht das Lesen auf keiner Stufe messbar Tempo ab, und das Spiel hält trotz der Einheiten rund 825 Takte je Sekunde.** Im Wechsel ohne und mit Lesen. Der Schaden Pikenier gegen Pikenier stand dabei auf 1 und ist zurück, nachgelesen. Beleg: `last.plan.json`.

| Stufe | ohne Lesen | mit Lesen | Einheiten |
|---|---|---|---|
| 1000 | 810,7, 824,8, 811,7, 824,4, 824,9, 827,8 | 771,2, 821,2, 821,5, 825,1, 813,5 | 2.412 |
| 500 | 499,4, 499,6 | 498,1 | 2.407 |
| 200 | 197,5, 199,1 | 199,1 | 2.407 |
| 100 | 98,7, 98,4 | 98,5 | 2.407 |
| 40 | 39,2, 39,8 | 40,0 | 2.390 |

Auswertung `a4_wechselprobe`: Kein Abzug ueber der Grenze. Stufe 40: Abzug -0.51, haette ab 1.99 Takten je Sekunde angeschlagen; Stufe 100: Abzug 0.02, haette ab 1.96 Takten je Sekunde angeschlagen; Stufe 200: Abzug -0.77, haette ab 1.99 Takten je Sekunde angeschlagen; Stufe 500: Abzug 1.37, haette ab 1.99 Takten je Sekunde angeschlagen; Stufe 1000: Abzug -0.41, haette ab 9.05 Takten je Sekunde angeschlagen

Grenze der Aussage: Auf Stufe 500 bis 40 je nur eine Phase mit Lesen. Die Stufen 1 und 10 sind nicht gemessen, dort ist das Lesen fertig, bevor der nächste Takt kommt. Die Einheiten stehen im Nahkampf, Wegsuche belastet erst der Marsch.

## Szenen Schlachten, 03.11. 19:37

Schachbrett, kein Befehl, Tempo 1000. Es zählt die Lage beim Ende, das Ende selbst steht im Protokoll (`schlachten_last.protokoll.jsonl`).

| Szene | Takte bis zum Ende | Takte je Sekunde |
|---|---|---|
| 20 gegen 20, Nahkampf gemischt | 1.667 | 837,5 |
| 1.000 gegen 1.000, Nahkampf gemischt | 5.666 | 747,5 |
| 500 Schützen gegen 500 Nahkampf | 634 | 859,3 |
| 500 Europäer gegen 500 Araber | 635 | 742,7 |

Dass die beiden Schlachten mit Feuerwerfern (A_FIRETHROWER 76) nach rund 635 Takten enden, fällt auf; die Ursache ist nicht ausgewertet, vermutlich das Feuer im dichten Schachbrett. Die Reihen mit 100 Einheiten sind nicht gefahren.

## Noch offen

Gegenprobe im Gefecht, Reichweite, Flugzeit, Trefferquote, Haltung, Geräte und Belagerung, Angriff auf einen Punkt, Sonderfälle, Lauf-K-Stand. A1, A2, A3, A9, A10, A12 über diese Aufzeichnungen sind noch nicht gerechnet.

