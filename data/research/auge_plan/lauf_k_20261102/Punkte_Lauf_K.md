# Einzelpunkte Lauf K

Lauf K 02.11.2026 23:49, Instanz 2, Green Haven, 8 KI, Liga-Balance. Geschrieben von SRE aus den Belegen, Rechnungen in `punkte_rechnen*.py`.

**Worte:** bestätigt und widerlegt heißen: Die Lage kam vor und die Rechnung ist gemacht. gemessen: einmal gelesen, Erwartung war "notieren". Lage fehlte: Die Lage kam in diesem Lauf nicht vor, der zuständige Lauf steht dabei.

| Urteil | Punkte |
|---|---|
| bestaetigt | 28 |
| widerlegt | 7 |
| gemessen | 2 |
| Lage fehlte | 18 |
| offen | 0 |

## Widerlegt (7)

| Punkt | Funktion | Beleg |
|---|---|---|
| P247 | `SetAIPlayerNickNames` | Die Liga ersetzt die Namen im Spiel; die Formel 0x67 + 8 x Typ + Variante trifft 1 von 8. Geschrieben wird ab Eintrag 1 über 8 Plätze, Variante 0. |
| P251 | `computeAIZoneLayer` | Werte 0, 1, 10; keine 2 und keine 8. Zone 1: 1.905 bis 2.001 Felder, Zone 10: 100 bis 110. |
| P258 | `aiRecruitEngineers` | Nicht 30, sondern 50 wie in Lauf F (Liga). Das Gold fällt, wenn der Bauer die neue Art bekommt, nicht wenn der Ingenieur erscheint (`nonEuroRecruit`). Spieler 7 bei Takt 71.486 (Fenster t6): Speerträger, Bogenschütze und Ingenieur zusammen 70, die beiden anderen kosten allein je 10. `isEngineerRequired` wechselte im ganzen Kampf nur einmal, bei 0 Gold ohne Kauf; die anderen Ingenieure kommen über `aiRecruitUnits`. Preise allein gemessen: Art 22 10, 23 30, 24 10, 25 40, 28 120, 37 10, 70 60, 71 10, 72 15, 75 100. |
| P264 | `setCurrentAttackStrength` | UCP ersetzt die Formel (`ai_addattack` relativ, `ai_attacklimit` 3000): Stärke = AttForceBase x Welle + 5, ohne Zufall, ohne Deckel 200. Gemessen KI 14: 63, 121, 179, 237, 295, 353, 411, 469; KI 15: 15 bis 55; KI 1: 35 bis 155; KI 9: 89, 173, 257. |
| P270 | `setAttackCoordinationLevel` | Stufen 0, 1, 2 ja. Höhere Stufe wird nicht häufiger: Spieler 1 bleibt immer 0, Spieler 3 geht 2, 1, 0, 2. |
| P294 | `moveUnitToBehaviorTarget` | Vorgekommen: 1010, 1012, 1014, 1015, 1019, 1043. 1012 (0x3F4, Leiternträger) fehlt in der erwarteten Liste, `assignAttackTargetsForTribe` schreibt ihn ebenso. |
| P295 | `assignAttackTargetsForTribe` | Mit UCP sagt der Wert nicht mehr das Ziel: `ai_attackwave` (Stufe 7) lässt Ziel 1010 reihum 4 x Mauern, 2 x Türme und Tore, 1 x Gebäude suchen. Gemessen 548, 192, 155 von 896 (Platz 0 ist ein Merkplatz und zählt nicht). Die anderen stimmen: 1012 Mauerliste 6 von 6, 1014 Torliste 8 von 8, 1015 Grabenliste 5 von 5, 1043 Breitenliste 6 von 6. 1013 und 1021 kamen nicht vor. |

## Bestätigt (28)

| Punkt | Funktion | Beleg |
|---|---|---|
| P242 | `UpdateFlag_1_2_4_Entity` | Die Arten 10, 12, 11 sind `ET_FLAG_1`, `_2`, `_4`. 814 von 814 Flaggenwechseln im Kampf passen: Wert 3 nur mit gesetztem Nervositäts- oder Abriss-Merker (28 von 28), die anderen nie (786 von 786). In den strengen Fenstern 100 von 100 auf 0, 1, 2 nach der Rekrutier-Wahl, 4 bis 126 Takte nach deren Wechsel: Das ist das Ende der Flaggen-Animation. |
| P243 | `removeSiegeBuildings` | Vier Bauten der laufenden Welle standen am Wellenende noch (Spieler 3 bei 125.803, Spieler 1 bei 150.201): alle im selben Takt auf `BLS_REMOVE`. 29 weitere wurden vorher zerstört. Die 12 Bauten mit Welle 0 (Belästigung, Ballisten) bleiben stehen, der Code verlangt `0 < attackWave`: Ein Katapult von Spieler 2 überlebte das Wellenende bei 48.804 bis 50.826. |
| P245 | `updateEnemyBuildings` | 240 Neuaufbauten in t1, t6, t8 (`gameTicksLoadBalancer` 0x47 bis 0x4E): Index gleich eigener Zählung in 240 von 240, 0 Einträge ausgeschlossener Arten, 0 aus dem eigenen Team. Je Aufbau fallen 133 bis 180 Bauten durch den Filter. |
| P246 | `destroyBuildings` | Geklärt: `noRubble` heißt falsch, es steht auf 1, wenn **Schutt bleibt**. `destroyBuildings` setzt `showNoRubble = (Tabelle == 0)`, `destroyBuilding` setzt das Feld, wenn `showNoRubble` 0 ist. 143 von 146 Fällen haben Tabelle ungleich 0. Die 3 anderen sind verbundene Bauten, die mitfallen (gleiches `uidWhenPlaced`, gelesen): Steinbruch 20 mit Halde 21, Söldnerposten 8 mit den Arten 56, 57, 58. 47 zerstörte Bauten mit Tabelle 0 blieben auf 0. |
| P248 | `LaunchSkirmishGame` | `startGoods` ist Zeile 0 der Tabelle plus Gold 2000 = Startgold; Truppen = Zeile der KI, erste Intensitäts-Spalte, x 75 % (`fairness` 2; KI 14: 16 auf 12, KI 1: 14, 5, 9 auf 10, 3, 6); TicksLeft 12000 = NoRushTicks[1]. Werte in `punkte_start.txt`. |
| P249 | `resetVariousCountsAndStatisticsAndStartGoodsAndResources` | KI 2000 = Tabelle[27], Mensch 4000. `popularity` 10000 = 1000 x 10. |
| P250 | `findAppropriateLocationForSiegeTent` | 36 von 36 lesbaren neuen Bauten: alle 8 Nachbarn frei, Höhenunterschied 0. Abstand zur Auswahl-Einheit 7 bis 29 Felder in 22 Fällen; Luftlinie ist die untere Grenze der Wegschritte, also mindestens 5. Bei 9 Bauten war die Karte schon neuer als der Bau, sie zählen nicht. |
| P252 | `computeAttackVectorsBasedOnXAndY` | Bis zu 50 Einträge je angegriffenem Spieler (7 Spieler 50, Spieler 8: 9), der erste ist in 8 von 8 Fällen der Burgeingang des Ziels, Gruppe immer 0. Die erste Lesung war falsch: Die Zeile hat 800 Bytes, die Feldkarte nennt nur 16. |
| P253 | `updateWalkLayerAndAIPathCostLayer` | Beim gerechneten Ziel Spieler 4 haben 1.916 von 1.916 Feldern der Zone 1 den Wert 1. Werte 2 bis 6 für die Ziele 1 bis 4: 4.519 von 4.519 Feldern haben einen Nachbarn in den vier Richtungen mit Wert minus 1. |
| P257 | `randomlySelectAttackUnitTypeToRecruit` | 20 von 20 Lesungen mit Vorlauf (der Datenblock wird alle 250 Takte gelesen) treffen die Rechnung Ist kleiner Max eines Spielers mit Wahl Angriff, mit den Sonderregeln Welle x 4 und `moatsOwned` größer 5 in der Rechnung. Die 3 ersten Lesungen je Fenster haben keinen Vorlauf und zählen nicht. |
| P259 | `recruitHarrassingSiegeEngines` | Spieler 2 (KI 15, Max 1): Index 0 auf 1 bei Takt 37.203. Bauern tragen 0x16 auf dem Weg zum Ingenieur (17), Katapulte 0x15 (6). Das Katapult zeigt in 12 von 12 Fällen auf `attackedPlayerID`, 4 davon sind einen Augenblick früher da als der Wert im selben Monatstakt. |
| P260 | `aiRecruitSortieRangedUnits` | Einheiten mit Verhalten 6 sind nur Art 22 (Spieler 2, +0x150 = 22) und Art 70 (Spieler 8, +0x150 = 70). 561 von 561 Anstiegen unter der Grenze. Die anderen werben nicht: +0x150 = 5 ist Tunnelgräber und ausgeschlossen (Spieler 5), keine Kaserne (Spieler 4, 6), +0x150 = 37 kam in diesem Lauf bei keinem (Spieler 1, 3, 7 hatten Kaserne und Bedarf): Mönche laufen hier über `euroRecruit`, ihr Preis steht in `nonEuroRecruit`; der Grund ist damit vermutet, nicht gemessen. |
| P261 | `aiRecruitSortieMeleeUnits` | Verhalten 7: Art 75, 28, 24, 72, 24 bei den Spielern 1, 2, 3, 5, 7, gleich +0x158. 1.481 von 1.481 Anstiegen unter der Grenze; der Höchstwert ist genau +0x154: 16, 4, 8, 15, 9. |
| P263 | `aiShouldAttackOrWaitForTeamCoordination` | Erstwellen 59 mindestens 58, 10 mindestens 10, 31 mindestens 30, 84 mindestens 84. Spätere Wellen starten früher, weil die Stärke bei einem schwachen Ziel zurückgesetzt wird. |
| P265 | `setCurrentAttackRaidParameter` | 21 von 21 Wellenstarts passen: Ziel unter 500 Gold ergibt -(Base / 2) x Zufall (-1 bei KI 1 und 9), KI unter 1000 Gold ergibt 0, sonst 0 bis RaidUnitsRandom (+3, +2 bei KI 15). Beim Start -3, -2, -1 bei den Spielern 6, 7, 8: Das Ziel ist dort noch Spieler 0 ohne Gold. |
| P266 | `computeEnemyKeepApproachTile` | `shortestDistance` gleich `signpostEntryData[ki-1]` bei jeder Welle: 154,261; 317,210; 251,164; 212,354 und weitere. |
| P267 | `setTribe0x11ToAggressiveAndAttackIfConditionMet` | Spieler 3 ist der einzige mit Gruppe 0x11: Bei `moat2` größer 0 wird sie im Zustand 5 am vierten Wochenaufruf aggressiv (96.607 auf 97.403). Alle 5 Einheiten mit Ziel 1015 haben `moat2` größer 0 und stehen in der Grabenliste. |
| P269 | `aiCommandSiegeEngineTribes` | Rammen: Ziel 1014 (Tor) nur mit `gate2` ungleich 0, 8 von 8. Ziel 1043 nur mit `gate2` 0 und `wide3` ungleich 0, 6 von 6. |
| P272 | `getCurrentDesiredAttackRaidUnitCount` | Truppen stehen an der Wunschzahl Parameter + RaidUnitsBase: KI 14: 3, KI 15: 16, KI 1: 3, KI 4: 4. Über der Zahl nur 5 von 1.663 Lesungen bei Spieler 3, direkt nach dem Wellenende bei 125.803, wenn Angriffstruppen zurückkommen. |
| P274 | `aiCreateSiegeUnits` | Spieler 1: delay 1, 2, 3 je 50 Takte, dann Erzeugen, +0x11c = 4. UCP hebt die Grenze von 3 Geräten auf (0x004D20A2). |
| P275 | `aiGiveRaidInstructions` | 14 Jahreswechsel, Ziele der Raubzug-Gruppen: 19 bleiben, 0 werden 0, 0 ändern sich. `yearChanged` steht nur bei Tagestakt 0, die KI ist bei 1 bis 8 am Zug. |
| P276 | `updateAIStrengthState` | 52 von 52 Monatsaufrufen: Zustand und Gefühl stimmen mit der Rechnung. Genau auf einer Grenze lagen Gold 200 und Truppen 8; Volk 15 und Nahrung 20 kamen nicht vor, sie stehen so im Code (`0xe <`, `0x13 <`). UCP ändert hier nur den Start: `ai_recruitstate_initialtimer` 0 statt 4800 Takte Verteidigung. |
| P277 | `computeNervousness` | 52 von 52 Monatsaufrufen: `isNotNervousByEnemyTroopValue` folgt der Rechnung Feindwert + Zuschlag gegen Truppenwert in Burgnähe. Bei Feindwert 150 ergibt das die erwarteten 170; dieser Wert selbst kam nicht vor. |
| P278 | `selectAttackTarget` | 52 von 52 Monatsaufrufen in den strengen Fenstern, alle drei Wahlarten; Wahl 2 ist der kleinste größte Achsenabstand (Spieler 4: 7, 6, 1). Dazu `ai_assaultswitch` (0x004D477B): Ab Zustand 3 bleibt das Ziel, solange dessen Lord lebt. Im ganzen Kampf kein Verstoß: Die 5 scheinbaren Fälle sind 3 x Zustand 9 auf 0 im selben Takt und 2 x ein sterbender Lord, den `getAliveLordForPlayer` schon nicht mehr zählt. |
| P279 | `updateAIPlayerState` | Nur 0, 2, 3, 4, 5, 6, 7, 9 sichtbar, Folge 0, 2, 3, 4, 5 oder 6, 9. Wechsel bei Takt modulo 200 gleich Spieler. |
| P280 | `setKeepOffsetAndOrientation` | Ausrichtung 0, 2, 4, 6, alle Versätze = Burg minus 43. |
| P289 | `recomputeAttackInfo` | 134 Berechnungen im Kampf: `wide(-8)` = `wide(-0xc)` 134 von 134, `scale(-0x10)` = `hack(-0xc)` 133 von 134, `wide` + `hack` gleich eigener Mauerzählung 127 von 134, bis 3 daneben 131. Auf Tempo 1000 liest die Aufzeichnung auch mitten in der Rechnung und die Karte ist bis 45 Takte alt; beides erklärt vermutlich den Rest, einzeln nachgesehen sind die 7 nicht. |
| P296 | `spawnQueuedReinforcementWaves` | Wellen bei Takt 202, 404, 603, 822; die erste nichtleere Art sinkt um höchstens 9: 12 auf 3, 10 auf 1, 22 auf 13, 24 auf 15. |

## Gemessen (2)

| Punkt | Funktion | Beleg |
|---|---|---|
| P255 | `processSingleplayerEvents` | Gefecht: `currentGameMode` 99, `gameMode_2` 3, `eventsCount` 0. Der Ereignismotor arbeitet im Gefecht nicht. |
| P262 | `selectBuildingFromAListOfBuildingTypes` | Die drei Listen ausgelesen, Werte in `punkte_rechnung1.txt`. |

## Lage fehlte (18)

| Punkt | Funktion | Beleg |
|---|---|---|
| P244 | `UpdateOutpostBuilding` | Keine Außenposten auf `Green Haven`, die Arten 106 und 107 kamen nicht vor. Zuständig: Karte mit Außenposten (Lauf S). |
| P254 | `ProcessAllyRequestAttackDefense` | Keine Verbündeten, der Befehl kommt nur vom Spieler (`SendPlayerToPlayerRequestOrResponse`). Zuständig: Partie mit Mensch und Bündnis. |
| P256 | `setTargetForTribeBasedOnTargetChoiceLogic` | Nur Außenposten-Gruppen rufen die Funktion (`aiRegisterTribeAndAssignTarget` aus `UpdateOutpostBuilding`), keine auf der Karte. Zuständig: Karte mit Außenposten (Lauf S). |
| P268 | `giveSomeRaidCommand` | Kein Ziel brannte beim Wechsel: 300 Zielwechsel, 0 mit Feuer; im ganzen Kampf brannten nur je eine Eisenmine oder Apfelfarm. 4 Wechsel im Zustand 6, davon 2 mit verschwundenem Ziel. Zuständig: Lauf S mit Feuerwerfern. |
| P271 | `teamIsWeakRelativeToEnemy` | Vor Takt 12.000 läuft die Friedenszeit, kein Feind mit Fernkämpfern. Danach bestätigt: 8 von 8 Nervositätsbeginnen mit relativer Stärke unter 75 (7 bis 65) und Fernkampfwert ab 100. Zuständig: Gefecht ohne Friedenszeit. |
| P273 | `decideOnTribeAttackLocation` | `decideOnTribeAttackLocation` ruft nur `makeOutpostTribesAttack`; `counter` und `randomNumber` bleiben 0. Keine Außenposten. Zuständig: Karte mit Außenposten (Lauf S). |
| P281 | `searchTribeWithProperties` | Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion). |
| P282 | `isAttackWaveComplete` | Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion). |
| P283 | `isLessThanPercentageOfTribesInAttackDying` | Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion). |
| P284 | `computeAttackWaveTroopComposition` | Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion). |
| P285 | `assignMacemenAndKnightsNotFromPlayer1ToTribes` | Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion). |
| P286 | `trySendMacemenTribeToAttack` | Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion). |
| P287 | `advanceAttackWaveStaging` | Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion). |
| P288 | `updateActiveAttackWaveState` | Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion). |
| P290 | `scanForSiegeTentPoints` | Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion). |
| P291 | `recountAttackTroopValue` | Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion). |
| P292 | `executeDelayedAttackWaveTargetAssignment` | Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion). |
| P293 | `aiControlNonSkirmishUnitMovement` | Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion). |

## Offen (0)

| Punkt | Funktion | Beleg |
|---|---|---|

## Aus Lauf F verschoben (20)

Das Urteil von Lauf F schob diese Punkte auf Lauf K. bestaetigt: 9, gemessen: 2, Lage fehlte: 9.

| Punkt | Funktion | Urteil | Beleg |
|---|---|---|---|
| P001 | `isSameTeam` | Lage fehlte | Jeder gegen jeden: `playerTeams` 8, 1, 2, 3, 4, 5, 6, 7, keine gleiche Nummer. Zuständig: Gefecht mit Bündnis. |
| P007 | `updateLordLadyJesterAndGhostUnits` | bestaetigt | 8 von 8: maxHealth = 150.000 x Faktor der Tabelle mit Index aiType minus 1: KI 15 120 % = 180.000, KI 1 50 % = 75.000, KI 9 110 % = 165.000, KI 2 70 % = 105.000, die anderen 100 %. |
| P021 | `initializeGameStateAfterMapLoad` | bestaetigt | 25 von 25 Preisen gleich dem Burgenbau aus Lauf F, also nicht aus der Karte. Es sind die Liga-Preise. |
| P052 | `recomputeAIAvailableGridTiles` | bestaetigt | Alle 8 KI: Zähler 11 bis 24, Cooldown 0. Der Zweig ohne Eisen in Reichweite kam nicht vor. |
| P053 | `applyAIV` | bestaetigt | Nur Status 0 und 1. 1.634 von 1.634 Bau-Schritten liegen im 100x100-Feld ab dem Versatz. Bei den 593 Wand-Schritten ist `location` keine Kachel, sondern der Anfang in `locationsArray`; davon je Spieler 9 Felder geprüft, alle im Feld. |
| P054 | `recomputeHeatmaps` | gemessen | Eisen in 62 Zellen, Summe 595; Felsbrocken in 147 Zellen, Summe 1.729; Öl 0. Mit den Vorkommen der Karte nicht verglichen. |
| P181 | `aiUpdateTaxesAndRations` | bestaetigt | Unter der kritischen Beliebtheit steht die Steuer im Wochentakt auf 2: 1.056 von 1.058 Lesungen (Spieler 6 und 8, die einzigen unter ihrer Grenze). Die 2 anderen zeigen 3 bei Spieler 8, nicht einzeln nachgesehen. |
| P182 | `aiShouldBuildWoodcutter` | Lage fehlte | `mapExtraInfo.totalWoodAvailable` fiel nie unter 435, die Grenzen 31 und 91 griffen nicht. Zuständig: Karte mit wenig Holz. |
| P183 | `planToBuyWhenLowOnResourceAndSnoozeBuildings` | Lage fehlte | Der Zähler steigt je Aufruf um 1 (4 Schritte in den strengen Fenstern). Bei 37 stand der Holzwunsch in 63 Lesungen schon auf 17 oder 22; der Fall Wunsch vorher 0 kam nicht vor. |
| P184 | `addBuildingToTargetableBuildings` | bestaetigt | Schritt +1 (52 von 60 Wechseln), Höchstwert 100. Dazu -1 (8 Wechsel): `getTargetableBuildingForPlayerID` zieht ab. |
| P185 | `shareGoldAmongTeamMembers` | Lage fehlte | Kein Team. Zuständig: Gefecht mit Bündnis. |
| P186 | `sellExcessGoods` | bestaetigt | Stichprobe: Spieler 3 verkauft Ware 13 bei 56 auf 50, Grenze 52 mit Spielraum. In 54 Fällen fiel eine Ware über ihrer Grenze im Verkaufstakt; je Aufruf wird nur eine Ware verkauft, die übrigen gezählten Fälle sind Verbrauch im selben Takt. |
| P187 | `requestGoods` | Lage fehlte | Kein Bündnis. Zuständig: Gefecht mit Bündnis. |
| P188 | `aiRecruitUnits` | gemessen | 12 von 47 neuen Warenwünschen im Wert +0x9c der KI, 15 weitere gehören zum Holz. Die anderen stammen aus anderen Wegen; `euroUnitAcquisitionFailReason` ist nicht mitgelesen, die Lage ist daher nicht eindeutig. |
| P189 | `aiBuyAndSellGoods` | bestaetigt | `willBuy` wechselt nur im Tagestakt des Spielers: 764 von 768, sonst 0 von 38.065. Die 4 ohne Wechsel sind nicht einzeln nachgesehen. |
| P191 | `aiDecideOnNewBuildings` | Lage fehlte | Gold über 16.000 kam nicht vor. Bei Gold bis 16.000 steigt das Ziel je Lesung um 1 (8.162 Fälle); die Wartezeit `aivPoorLimit` ist nicht nachgerechnet. |
| P192 | `validateWallPlacementAtTile` | Lage fehlte | Braucht einen Baubefehl neben einem Feindgebäude. Zuständig: Lauf S. |
| P194 | `countMoatsOwnedByEachPlayer` | bestaetigt | `moatsOwned` gleich eigener Zählung der Grabenfelder in `moats[]`: 448 von 448 Monatstakten. |
| P199 | `validateWallBuildPath` | Lage fehlte | Gründe im Lauf 17, 23, 22, 3; 0x13 kam nicht vor. Braucht einen Mauerbefehl dicht am Gegner. Zuständig: Lauf S. |
| P201 | `checkBuildingCanBePlacedHere` | Lage fehlte | Grund 23 (0x17) kam vor, die Lage dazu ist nicht geprüft; 0x12 und 1000 nicht. Braucht gezielte Baubefehle. Zuständig: Lauf S. |
