# Ergebnis Lauf K (B-142)

Lauf 02.11.2026 23:49 bis 23:55, Instanz 2, Karte `Green Haven` („Der grüne Punkt“), 8 KI ohne Menschen: Spieler 1 bis 8 = KI 14, 15, 1, 9, 2, 5, 7, 4 (Mirza, Marschall, Rotkäppchen, David, Rattenfänger, Bauer, Gardist, Karl von Festenberg). Liga-Balance aktiv. Basis `laeufe/lauf_k_20261102_234952`.

**Der Lauf ist gültig:** 8 Lords am Start, je Spieler einer, Friedenszeit 12.000 Takte zu Ende, alle drei Fenster je 2.002 Takte ohne fehlenden oder gemischten Takt, zweimal auf denselben Takt 15.039 geladen, kein Abzug in der Bremsprobe. Der Kampf lief bis zum letzten Lord.

## Der Kampf

Lords fallen bei Takt 24.186 (Spieler 7), 50.403 (6), 71.245 (5), 88.069 (8), 113.407 (4), 132.010 (3), 150.497 (2). Sieger ist Spieler 1, Mirza (KI 14). Der Kampf dauerte 133.512 Takte in 174 Sekunden.

Angegriffen haben nur die KI 14, 15, 1 und 9. Die KI 2, 5, 7 und 4 sammeln nie genug Angriffstruppen (höchstens 0 bis 3, nötig wären `AttForceBase` 50, 60, 46, 42). **Das liegt an der KI, nicht am Platz:** In umgekehrter Reihenfolge griffen genau dieselben vier an, jetzt auf den Plätzen 5 bis 8 (`platz_oder_ki.py`).

**Warum diese vier nicht (Monatswahl `updateAIStrengthState`, Werte aus dem Satz der KI):**

| KI | Wahrscheinlichkeit Angriff bei normal, schwach, stark | Gefühl im Lauf | Zeitanteil Wahl Angriff | Warum keine Welle |
|---|---|---|---|---|
| 2 (Rattenfänger) | 0, 0, 25 | nie stark, Stärke höchstens 6, stark ab 8 | 0 % | Wirbt ohne Stärke nie Angriffstruppen |
| 5 (Bauer) | 0, 0, 25 | nie stark, Stärke höchstens 5 | 0 % | Dasselbe |
| 7 (Gardist) | 20, 0, 64 | immer normal | 18 % | Gold in 42 % der Zeit über der Grenze 30, Lord fällt schon bei Takt 24.186 |
| 4 (Karl von Festenberg) | 20, 80, 70 | normal und schwach | 50 % | Will, kann aber nicht: Gold in 3 % der Zeit über 100, `canStartSpending` in 23 % |

Zum Vergleich die Angreifer: KI 14 mit 0, 0, 75 ist 80 % der Zeit stark, KI 9 mit 100, 69, 79 will immer. Liga-Sätze, nicht Grundwerte.

## Laden und Festgelegtheit (A5, A6)

| Frage | Antwort | Beleg |
|---|---|---|
| Ist der Stand nach dem Laden gleich dem gespeicherten? | **Nein, aus drei Gründen im Spiel selbst** | siehe unten |
| Läuft das Spiel nach dem Laden gleich weiter wie ohne Laden? | **Nein** | Einheiten sind einen Schritt voraus, Lords haben andere Werte |
| Rechnet das Spiel festgelegt? | **Ja, gemessen über 2.000 Takte im Frieden und 2.000 Takte im Kampf** | Zwei Ladevorgänge, Byte für Byte gleich in den Bytes der Spiel-Prüfsumme |

**Was das Laden ändert (`prepareMap` 0x00512450):**
1. **Ein Schritt ohne Takt:** `processGameTick` läuft einmal mit `gamePausedLogical = -1`: Einheiten und Gebäude rechnen, Taktzähler und Zufall stehen. Gemessen: `t2[T+1]` passt auf `t1[T+2]` (193 statt 3.140 abweichende Bytes).
2. **Werte aus den Tabellen:** `upgradeMapFormatForUnits` 0x0053E390 ruft bei jedem Laden `UpgradeMapUnitsTo_UnknownVersion1`, `_117` und `_UnknownVersion2` auf. Tempo, Grafik und Reichweite kommen aus den Tabellen, Einheiten mit vollem Leben bekommen den Tabellenwert. **Das Leben von KI-Lords geht dadurch verloren:** vorher 75.000 bis 180.000 je nach KI, danach alle 150.000 (Faktor aus `MaxLordHealthMapping` weg). Verwundete behalten ihr Leben.
3. **Neu berechnet:** Bäume, Zonenkarten, `keepPositions` und mehr.

**Die zwei Eingänge von außen (A6):**
- `mapAndTime.counterForUpdatingSeparateAreaTileMaps`: läuft auch in der Pause weiter (`updateSeparateAreaTileMap` im Pausenteil von `processGameTick`), je nach echter Pausendauer stand er nach dem Laden bei 12, 36 oder 43. Er entscheidet, in welchem Takt die Zonenkarte neu entsteht.
- `DAT_EntityState.every10Ticks`: **irreführender Name, das ist der Suchzeiger für den nächsten freien Geschossplatz** (`spawnProjectileEntity` 0x00404AE0). Das Laden setzt ihn nicht zurück. Andere Plätze heißen andere Reihenfolge in der Rechnung.

| Vergleich | Ergebnis |
|---|---|
| Zweimal geladen, nichts gesetzt (t2, t3) | Ab Takt 19 Ziel einer Einheit anders, ab Takt 988 Verhalten, ab Takt 1.651 Zufall |
| Zweimal geladen, Zähler gleich, Frieden (t4, t5) | **2.001 Takte gleich.** Nur der Zähler im ersten Rahmen vor dem Setzen und der erste Zufallsstrom weichen ab |
| Zweimal geladen, Zähler gleich, Kampf (t6, t7) | Ab dem ersten Rahmen 25 Geschosse auf anderen Plätzen, sonst dieselben 573 |
| Zweimal geladen, Zähler und Zeiger gleich, Kampf (t8, t9) | **2.001 Takte gleich, zwei Lesungen erwischten einen Takt mitten in der Rechnung.** Takt 605: An 457 der 458 abweichenden Bytes hat t9 noch den Wert des Takts davor. Takt 203: `someCounter2` zählt im Takt von 65 auf 75, t8 las 71, t9 las 70. Beim nächsten Takt ist wieder alles gleich (`a6_einzelne_takte.py`). 14.007 Rahmen, 1.996 Lebenswert-Wechsel, der Zufall nie anders |

**Erster Zufallsstrom:** Ihn ziehen Ton, Musik, Oberfläche, Möwen und Feuereffekte je Bild, er hängt also an der echten Zeit. Spielfunktionen lesen ihn auch (`UpdateSwordsman`, `UpdateLord`, `processFireDamageToUnit` und andere). In den gemessenen Fenstern hat das nichts geändert; die Prüfsumme des Spiels enthält ihn nicht. Der zweite Strom ist der Spielstrom.

## Lesen: Wann ist ein Takt fertig?

Der Zähler steigt am Anfang von `processGameTick`, Einheiten und Gebäude rechnen danach. Wer sofort liest, sieht einen halben Takt. Gemessen auf Tempo 40 (`takt_dauer_messen.py`): Die Spielfelder ändern sich in den ersten 5 ms, die Takte liegen 26 ms auseinander. Die strengen Fenster warten deshalb 5 ms. Über den ganzen Takt schreiben nur `units[].drawX`, `drawY`, `drawWidth`, `drawHeight1` und `buildings[].surfaceAreaUnk`: das Zeichnen. Auf Tempo 1000 lässt sich das nicht einhalten, dort ist jede Lesung möglicherweise ein halber Takt.

## Prüfsummen (A11)

Bestätigt: `HASH_HashTotal` wechselt im Gefecht nie, das Spiel rechnet sie nur beim Start (`processSingleTimeTick` prüft die Spielart). Aus Takt 0 nachgerechnet: Einheiten 2.500 von 2.500 (1 nicht 0), Gebäude 2.000 von 2.000 (72 nicht 0), Bäume 2.000 von 2.000 (1.150 nicht 0), Gruppen 1.250 von 1.250 (0 nicht 0), Spieler 9 von 9 (9 nicht 0). Damit sind auch die Byte-Masken für den A6-Vergleich bestätigt: Sie sagen, welche Bytes das Spiel selbst als Zustand ansieht.

## Fehler dieser Sitzung, die der Lauf gefunden hat

| Fehler | Ursache | Behoben |
|---|---|---|
| Höchstens 7 Lords | Startliste trägt Spieler minus 1 ein (`GetPlayerPosition` 0x0042AC60) | Liste 0 bis 7, Test |
| Erster strenger Takt gemischt | Erst weiter, dann Tempo: 0,3 s auf Tempo 1000 | Tempo im Stand setzen, Test |
| Falscher Abbruch nach dem Laden | Vergleich ohne den Schritt beim Laden | Laden erst nach dem Kampf |
| Keine Friedenszeit in der Probe | Stufe 6 ist 0, die 500 stehen auf Stufe 7 | Stufe 1 auch in der Probe, Prüfung am Start |
| „Letzter Lord“ bei 3 Lebenden | `updateUnits` setzt `maxUnitCount` in jedem Takt auf 0 | Zähler über alle Plätze, Test |
| Laden hing im Hauptmenü | Das Ladefenster läuft dort nicht weiter, erst eine Partie lässt es fertig werden | Laden aus einer frisch gestarteten Partie |
| Halbe Takte im Vergleich | Zähler steigt vor der Rechnung | 5 ms warten in den strengen Fenstern |

## Gesamtproben

Aus `laeufe/lauf_k_20261102_234952.ergebnis.json`, Auswertung neu gerechnet 03.11.2026 08:29 bis 09:08.

| Probe | Ergebnis |
|---|---|
| A1 Felder außerhalb der Liste | haupt 50, t1 bis t9 48 bis 58, danach 4.307. Davon 4.062 in `DAT_TroopValueState`: Die Listen der Spieler 1 bis 8 liegen je 0x177BC weiter in `attackInfo`, die Struktur benennt dort tausende Felder falsch oder gar nicht. 246 Zeilen neu in `zustand_felder.csv`, `attackInfo` als eine Zeile; Liste `feldluecken_lauf_k.csv` |
| A2 nie geändert | Von 3.318 Feldern der Liste in Lauf K 1.499, in Lauf F 1.482, in beiden 1.091 (`nie_gesehen_lauf_f_und_k.csv`). Das heißt nur: nicht gesehen. Lauf S kommt noch |
| A3 Takttreue | t1 bis t9 bestätigt: kein Takt fehlt, kein Rahmen gemischt, je rund 22.360 Rahmen. Tempo 1000 liest nicht jeden Takt: im Kampf 114.319 Takte ausgelassen, das ist erwartet |
| A5 Laden | Widerlegt: gespeichert gegen geladen 519 Spielfelder anders, zweimal geladen 118. Gründe oben |
| A6 Festgelegt | Ohne gleiche Zähler anders, mit gleichen Zählern gleich, siehe oben |
| A7 Zufall | 4.002 Lesungen in t1 passen zur Tabelle |
| A9 Befehlsring | 0 Plätze geändert in haupt und danach: Die KI gibt ihre Befehle in diesem Lauf nicht über den Ring |
| A10 Lebenslauf | t1 36.236 und danach 3.097.716 Platzwechsel ohne Verstoß |
| A11 Prüfsummen | Bestätigt, siehe oben |
| A12 Flüchtige Merker | Je 7 Wechsel am Taktende in t1 |
| A13 Spielart | K: `currentGameMode` 99, `gameMode_2` 3. F: 0, 2. Die dritte Spielart bringt Lauf S |

## Einzelpunkte

Alle Urteile mit Beleg: `Punkte_Lauf_K.md`. **Liste Lauf K, 55 Punkte:** 28 bestätigt, 7 widerlegt, 2 gemessen, 18 Lage fehlte, 0 offen. **Aus Lauf F verschoben, 20 Punkte:** 9 bestätigt, 2 gemessen, 9 Lage fehlte. 44 Funktionen haben ein `live_ergebnis` im Funktionswissen bekommen.

**Punkte mit Marke [Spielart]:** 77 Punkte, Vergleich `Spielart_Lauf_K.md`. In 74 sagt das Werkzeug im Gefecht dasselbe wie im Burgenbau. Anders nur P184 und P188 (KI-Felder, in Lauf F keine KI) und P216 (die 20 kommt im Gefecht vor).

### Was das Spiel im Speicher anders rechnet als die Datei

| Stelle | Schalter in `ucp-config.yml` | Wirkung | Beleg |
|---|---|---|---|
| `setCurrentAttackStrength` | `ai_addattack` relativ, `ai_attacklimit` 3000 | Stärke = AttForceBase x Welle + 5, ohne Zufall, ohne Deckel 200 | P264 |
| 0x004D477B `selectAttackTarget` | `ai_assaultswitch` | Ab Zustand 3 kein Zielwechsel, solange der Lord lebt | P278 |
| 0x00524633 `assignAttackTargetsForTribe` | `ai_attackwave` Stufe 7 | Ziel 1010 sucht reihum 4 x Mauern, 2 x Türme und Tore, 1 x Gebäude | P295 |
| 0x004D34B1 `updateAIStrengthState` | `ai_recruitstate_initialtimer` 0 | Keine 4.800 Takte Pflicht-Verteidigung | P276 |
| 0x004D20A2 `aiCreateSiegeUnits` | nicht zugeordnet | Grenze von 3 Geräten aufgehoben | P274 |
| `nonEuroRecruit` | Rebalancer der Liga | Preise aus der Tabelle: Ingenieur 50 statt 30 | P258 |

Alle 309 Stellen: `code_aenderungen.csv`. Zerlegt: `ucp_sprungziele.txt`.

## Wofür dieser Lauf die falsche Lage hatte

Kein Punkt ist ohne Grund offen. Das sind die 27 Punkte mit „Lage fehlte“ und der Lauf, der sie beantworten kann:

| Lage | Punkte | Zuständig |
|---|---|---|
| Wellen-System außerhalb des Gefechts | P281 bis P288, P290 bis P293 | Kampagnenmission oder Burgenbau mit Invasion; `aiControlNonSkirmishUnitMovement` schließt `gameMode_2` 3 aus |
| Außenposten | P244, P256, P273 | Karte mit Außenposten |
| Bündnis | P001, P185, P187, P254 | Gefecht mit Bündnis |
| Baubefehl von uns | P192, P199, P201 | Lauf S |
| Brennendes Ziel | P268 | Lauf S mit Feuerwerfern |
| Früher Druck | P271 | Gefecht ohne Friedenszeit |
| Wenig Holz, viel Gold, Holzwunsch 0 | P182, P183, P191 | Karte mit wenig Holz, Startgold hoch |

## Was aus Lauf F noch aussteht

Nicht Teil dieses Laufs, aber noch nicht erledigt: 8 offene Punkte (P041, P058, P059, P065, P070, P071, P134, P215) und 27 Punkte „gesehen, nicht nachgerechnet“. Dazu A4, die Lesedauer in der Massenschlacht: Lauf S.
