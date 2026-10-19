# Spielkarte Stronghold Crusader - Grundverständnis für das Framework

Angelegt 19.10.2026 (Backlog B-95/B-114). Anlass: Krari über Daniel, 19.10. 21:52: erst den Code des Spiels wirklich
verstehen, dann von Grund auf nach Sharky bauen. Jeder Abschnitt nennt Adressen, Marke und Beleg.

**Referenz:** Ghidra-Projekt `OpenSHC-ref` (OpenSHC-SARIF, 4.765 benannte Funktionen) auf `StrongholdCrusader.exe`
(sha1 `012e9d55…`). Gemessen 19.10.: Instanz 1 ist byte-gleich, Instanz 2-5 weichen in genau einem Byte ab (Instanzname,
`instanz_anlegen.py`). Alle Adressen gelten also für jede Instanz. Skripte: `werkzeug/ghidra/*.java`, headless:

```
JAVA_HOME="C:\Program Files\Eclipse Adoptium\jdk-21.0.12.8-hotspot" DUMP_AUS=<datei> DUMP_NAMEN=<name1,name2> \
  ~/ghidra/ghidra_12.1.2_PUBLIC/support/analyzeHeadless.bat C:\Users\danie\ghidra-projects OpenSHC-ref \
  -process StrongholdCrusader.exe -noanalysis -readOnly -scriptPath <werkzeug/ghidra> -postScript DumpFunktionen.java
```

## 1. Wie das Spiel einen Befehl für einen Spieler ausführt (B-114, 19.10.2026)

Marke: **abgelesen** (Dekompilat). Passt zur Messung vom 18.10. (logik.lua: Befehle laufen für den Platz, der bei der
Ausführung in `currentPlayerSlotID` steht).

| Schritt | Funktion / Feld | Was passiert |
|---|---|---|
| 1. Absetzen | `queueCommand` `0x00489100` (thiscall auf `GameSynchronyState` `0x0191D768`) | Werte stehen vorher in `GameCommandParam0..5` (`0x01997FB8…`). Neuer Eintrag in `GameCommandArray` (200 Plätze): `commandType`, `time = jetzt + commandDelay`, **`playerUnk = DPLAYX_PlayerHandle`** (die eigene Netzkennung). Der Ausführer packt die Werte im Modus `GCS_SCHEDULE_AND_SEND` in den Eintrag. Sofort-Befehle (`time < 1`) laufen gleich, dann mit Auslöser = `currentPlayerSlotID`. |
| 1b. Befehl eines anderen Spielers | `scheduleReceivedCommand` `0x00480210` (Typ, **Absender-Kennung**, Zeit, Werte) | Derselbe Eintrag, aber mit der mitgegebenen Absender-Kennung. So kommen im Mehrspieler die Befehle der anderen herein. |
| 2. Ausführen | `processWaitingCommands` `0x004892F0`, jeder Takt | Für jeden fälligen Eintrag: **`protocolInvokerPlayerID`** (`GSS+0x109E70` = `0x01A275D8`) = `translateMultiplayerIDsIntoPlayerIDs(eintrag.playerUnk)`, dann der Ausführer im Modus `GCS_EXECUTE`. |
| 3. Übersetzen | `translateMultiplayerIDsIntoPlayerIDs` `0x0047EAF0` | **Mehrspieler:** Absender → Platz über `currentPlayerFullIDArray[1..8]` (`0x0191DE10 + 4·Platz`). **Einzelspieler** (`GM_SOLITARY`, `GM_SKIRMISH_SINGLE_PLAYER`): gibt immer `currentPlayerSlotID` (`GSS+0x109E74` = `0x01A275DC`) zurück - **der Absender wird nicht beachtet.** |
| 4. Wirkung | die Ausführer (Tabelle `0x00B38E10 + 4·Nr`) | lesen den Auslöser, nicht „ich“: `ClickRecruitUnit` → `ProcessRecruitUnit(protocolInvokerPlayerID, Typ, Gebäude)`; ebenso Bauen, Abreißen, Kaufen/Verkaufen, Steuern, Rationen, Mauern, Gelände, Tore, Belagerungszelt (43 Funktionen unter `Commands::` lesen `protocolInvokerPlayerID`, gezählt in `daten/dekomp_befehl_ausfuehren.c`). |

**Folge:** Im Gefecht gegen den Computer gilt jeder Befehl für den, der bei der Ausführung „ich“ ist. Deshalb setzt
der Mod (`logik.lua`, `alsSpieler`) „ich“ einen Takt lang auf SamurAIs Platz. In diesem Takt gehen auch Daniels Klicks
an SamurAI; wird „ich“ vor der Ausführung zurückgesetzt, ginge SamurAIs Befehl an Daniel. Das widerspricht B-94.

**GEBAUT 19.10.2026 23:10 (B-94), im Spiel geprüft 8/8 + Gegenprobe** (`werkzeug/absender_live_pruefen.py`, `daten/absender_live_*.txt`; ohne Spiel `werkzeug/absender_pruefen.py` 6/6): logik.lua stempelt SamurAIs Einträge mit `0x53414D00 + Platz`, an `0x00489387` springt `processWaitingCommands` in eigenen Code, der nur für gestempelte Einträge Auslöser und „ich“ für den einen Aufruf setzt und die Auswahl-Leiste sichert. Rückweg `{"absender": "aus"}`. Der ursprüngliche Vorschlag:

**Weg zur Trennung (Vorschlag für B-94):** Das Spiel kennt den richtigen Weg schon - im Mehrspieler trägt
jeder Befehl seinen Absender. Im Einzelspieler-Zweig der Übersetzung muss nur ein Befehl mit SamurAIs Absender-Kennung
für SamurAIs Platz gelten; jeder andere Befehl (Daniels Klicks) bleibt bei „ich“. SamurAI setzt seine Befehle dann
mit eigener Absender-Kennung ab (`scheduleReceivedCommand` oder `playerUnk` des Eintrags nach `queueCommand`), und
„ich“ wird nie mehr angefasst.

Belege: `daten/dekomp_queuecommand.c`, `daten/dekomp_befehl_ausfuehren.c` (alle Zugriffe auf Auslöser und „ich“ +
die drei Setzer), `daten/dekomp_absender.c` (Übersetzung, Ausführer Anwerben, Platzvergabe). Skripte:
`werkzeug/ghidra/DumpBefehlAusfuehren.java`, `werkzeug/ghidra/DumpFunktionen.java`.

## 2. Was das Lagebild liest - jedes Feld mit seinem Namen im Spiel (B-95, 19.10.2026)

Marke: **abgelesen** (OpenSHC-Strukturen, `werkzeug/ghidra/DumpStrukturen.java` -> `daten/strukturen_kern.txt`,
`daten/strukturen_global.txt`), abgeglichen mit jedem Abstand, den logik.lua liest (`werkzeug/spielkarte_felder.py` ->
`daten/spielkarte_felder.txt`). Ergebnis: **jede Spalte des Lagebilds und alle 21 festen Adressen unserer Werkzeuge
treffen ein benanntes Feld, jede Bedeutung stimmt, keine einzige Lesebreite weicht ab.** Die Strukturgroessen sind genau
die Schrittweiten, mit denen der Mod rechnet: Einheit 1.168, Gebaeude 812 (`0x32C`), Spielerdaten 14.836 (`0x39F4`),
Truppe 820 (`0x334`).

Wo die Daten liegen: `DAT_UnitsState` `0x01387F38` (Einheiten ab `+0x614`, 2.500 Plaetze), `DAT_BuildingsState`
`0x00F98520` (Gebaeude ab `+0x14`, 2.000 Plaetze), `DAT_GameState` `0x0112B0B8` (Spielerdaten ab `+0x30D40`, 9 Plaetze;
Zeit und Partieende in `mapAndTime` ab `+0x516D4`), `DAT_GameCore` `0x01FE7D10` (Ansicht, Pause, Takt),
`DAT_TileMapState` `0x01A93208` (Karte, Bauplatzpruefung), `DAT_GameSynchronyState` `0x0191D768` (Befehle, Spieler).

Nebenbei geklaert: der Filter "Abstand 672 == 0" in logik.lua ist `dying` - er heisst "lebt noch". Es gibt zwei
Takt-Zaehler: `mapAndTime.totalGameTicksUnk` (liest der Lenker) und `GameCore.mapTimeInTicks` (nimmt queueCommand).

### Einheit (Unit, 1.168 Byte, Array 0x0138854C)
| Spalte | logik.lua | Feld im Spiel (OpenSHC) | Typ | Breite | Bemerkung |
|---|---|---|---|---|---|
| besitzer | +0x96 | `owner` (+0x96) | short | 2 | Real value |
| typ | +0x8E | `unitType` (+0x8E) | UnitTypeShort | 2 |  |
| x (Feinposition/8) | +0xB6 | `microXPosition` (+0xB6) | short | 2 |  |
| y (Feinposition/8) | +0xB8 | `microYPosition` (+0xB8) | short | 2 |  |
| leben | +0x3C8 | `health` (+0x3C8) | int | 4 |  |
| zustand | +0x2C0 | `state` (+0x2C0) | UnitStateUnion | 2 |  |
| zielart | +0x39C | `targetingType` (+0x39C) | UnitInstructionTypeShort | 2 | 3 if automatic, 4 if user selected attack (explicit) |
| zieleinheit | +0x39E | `targetedUnitID__OR__engineerMannedSiegeEngineRef` (+0x39E) | short | 2 |  |
| zieluid | +0x3A0 | `targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID` (+0x3A0) | int | 4 |  |
| zielgebaeude | +0x336 | `targetID_OR_targetBuildingID` (+0x336) | short | 2 |  |
| ziel | +0x30E | `target` (+0x30E) | short | 2 |  |
| zielx | +0x310 | `targetX` (+0x310) | short | 2 |  |
| ziely | +0x312 | `targetY` (+0x312) | short | 2 |  |
| laufx | +0xC8 | `destinationXPosition` (+0xC8) | short | 2 | j |
| laufy | +0xCA | `destinationYPosition` (+0xCA) | short | 2 | i |
| auswahlvon | +0xB2 | `ifSelectedThenPlayerID` (+0xB2) | short | 2 |  |
| auswahlmarke | +0xB4 | `selectionRelatedFlag` (+0xB4) | short | 2 |  |
| gruppe | +0x2D8 | `tribeID` (+0x2D8) | short | 2 |  |
| gruppenuid | +0x2E4 | `tribeUID` (+0x2E4) | int | 4 |  |
| ladung | +0x388 | `resourceToDeposit` (+0x388) | short | 2 |  |
| arbeitsplatz | +0x338 | `workplaceBuildingID_1` (+0x338) | short | 2 |  |
| nahziel | +0x33E | `attackedUnitID` (+0x33E) | short | 2 |  |
| nahangreifer | +0x3AE | `attackedBy` (+0x3AE) | short | 2 |  |
| Filter 'lebt' (672 == 0) | +0x2A0 | `dying` (+0x2A0) | short | 2 |  |
| Zustand-Existenz (0x8C) | +0x8C | `logicalState` (+0x8C) | UnitLogicStateShort | 2 | 1 moves to 2 (appearing), 3 means removal: dying |
| uid | +0x98 | `uid` (+0x98) | int | 4 |  |

### Gebaeude (Building, 812 Byte, Array BuildingsState+0x14 = 0xF98534)
| Spalte | logik.lua | Feld im Spiel (OpenSHC) | Typ | Breite | Bemerkung |
|---|---|---|---|---|---|
| zustand (G_ZUSTAND) | +0xE4 | `logicalState` (+0xD0) | BuildingLogicalStateShort | 2 |  |
| typ (G_TYP) | +0xE6 | `buildingType` (+0xD2) | BuildingTypeShort | 2 |  |
| besitzer (G_BESITZER) | +0xEA | `owner` (+0xD6) | short | 2 |  |
| leben (G_LEBEN) | +0x120 | `currentHealth` (+0x10C) | short | 2 |  |
| maxleben (G_MAXLEBEN) | +0x122 | `maxHealth` (+0x10E) | short | 2 |  |
| x | +0x102 | `x` (+0xEE) | ushort | 2 | most north-west tile |
| y | +0x104 | `y` (+0xF0) | ushort | 2 |  |
| groesse | +0x10C | `widthOrHeight` (+0xF8) | uint | 4 |  |
| Feld 0x1A0 | +0x1A0 | `currentStoredResourceType` (+0x18C) | short | 2 |  |
| uid (Angriff 0xEC) | +0xEC | `uid` (+0xD8) | int | 4 |  |
| Brandzeit (0x14+702) | +0x2D2 | `fireDuration` (+0x2BE) | short | 2 | goes up until overflows |

### Feste Adressen unserer Werkzeuge
| Bedeutung bei uns | Adresse | Feld im Spiel (OpenSHC) |
|---|---|---|
| Ansicht (Menue/Gefecht) | `0x01FE7D1C` | `DAT_GameCore.currentMenuViewType` |
| Pause | `0x01FEA054` | `DAT_GameCore.gamePausedLogical` |
| Spielzeit in Takten (Lenker) | `0x0117CADC` | `DAT_GameState.mapAndTime.totalGameTicksUnk` |
| Spielzeit in Takten (queueCommand) | `0x01FE7DA8` | `DAT_GameCore.mapTimeInTicks` |
| Partie vorbei | `0x0117D500` | `DAT_GameState.mapAndTime.gameOver` |
| 'ich' | `0x01A275DC` | `DAT_GameSynchronyState.currentPlayerSlotID` |
| Ausloeser | `0x01A275D8` | `DAT_GameSynchronyState.protocolInvokerPlayerID` |
| Spielart | `0x0191DD80` | `DAT_GameSynchronyState.currentGameMode` |
| Mensch-Eintrag Spieler 2 | `0x0191DE18` | `DAT_GameSynchronyState.currentPlayerFullIDArray[2]` |
| KI-Nummer Spieler 2 | `0x0191DE84` | `DAT_GameSynchronyState.currentAIArray[2]` |
| Bauplatz-Pruefung Ergebnis | `0x01FE7B3C` | `DAT_TileMapState.buildingPlacementFail` |
| Bauplatz-Pruefung Grund | `0x01FE7B40` | `DAT_TileMapState.buildingPlacementFailReason` |
| Bau-Drehung | `0x01FE7BBC` | `DAT_TileMapState.DAT_TempBuildingRotation` |
| Spieler 2: Beliebtheit | `0x01163240` | `DAT_GameState.playerDataArray[2].popularity` |
| Spieler 2: Platz | `0x01163254` | `DAT_GameState.playerDataArray[2].populationCap` |
| Spieler 2: Feuer | `0x01163268` | `DAT_GameState.playerDataArray[2].availablePeasantsAtFire` |
| Spieler 2: Leute | `0x01165360` | `DAT_GameState.playerDataArray[2].currentPopulation` |
| Spieler 2: Essen (Beliebtheit) | `0x01165340` | `DAT_GameState.playerDataArray[2].popularityChangeBasedOnFood` |
| Spieler 2: KI-Art | `0x011654E0` | `DAT_GameState.playerDataArray[2].aiType` |
| Spieler 2: Holz | `0x011636B8` | `DAT_GameState.playerDataArray[2].currentResources[2]` |
| Spieler 2: Gold | `0x011636EC` | `DAT_GameState.playerDataArray[2].currentResources[15]` |

## 3. Der Takt - wann was im Spiel passiert (B-95, 20.10.2026)

Abgelesen aus OpenSHC-ref (Ghidra, nur lesen): `werkzeug/ghidra/DumpAufrufer.java` -> `daten/aufrufer_befehle.txt`
(Aufrufkette und Aufrufreihenfolge), `DumpFunktionen.java` -> `daten/dekomp_takt.c` (WinMain, determineGameTicksToPerform,
processGameTick). Marke: **abgelesen** (Programmcode gelesen, nicht im laufenden Spiel gemessen).

**Hauptschleife** (`WinMain` @ 0x0057be10, je Bild):
1. Fenster-Nachrichten, `processMenuViewSwitch`, Musik, `receiveAllTransmittedCommands` (Mehrspieler-Befehle annehmen).
2. `gameTicksThisLoop = determineGameTicksToPerform(...)` - wie viele Spieltakte dieses Bild rechnet (hoeheres Tempo =
   mehr Takte je Bild).
3. Fuer jeden dieser Takte, in genau dieser Reihenfolge (0x0057c375 ...):
   `processWaitingCommands` (0x004892F0, Abschnitt 1) -> `processGameTick` (0x0045CD10) -> `receiveAllTransmittedCommands`
   -> Videos -> `TacticalPowersFill`; Abbruch, wenn `DAT_GameHalted`.
4. Danach Zeichnen (Karte, Menue, Minikarte) - einmal je Bild, nicht je Takt.

**Ein Takt** (`processGameTick`): zuerst Mehrspieler-Abgleich, Kartenschichten; dann - nur wenn kein haltendes Menue offen
ist - in dieser Reihenfolge: Wind, Kletterdaten, **Gebaeude** (`updateBuildings`), Pechgraeben, **Baeume**,
Einzelspieler-Ereignisse, **Niederlage pruefen** (`checkSkirmishGameDefeat`), **KI-Bauentscheidungen**
(`AIVState::updateBuildingsStateAndUpdateAIBuildingDecisions`), KI-Einheitenbewegung (nicht Gefecht), **Einheiten**
(`updateUnits`), Entitaeten, **Verbaende** (`TribesState::updateTribeUnitAssignments`, `updateTribes`), Verstaerkungswellen,
Rehe nachwachsen, Staub, `updateGameRelatedValue`.

**Was das fuer uns heisst:**
- Ein Befehl, den wir senden (queueCommand), wird am **Anfang des naechsten Takts** ausgefuehrt - vor Gebaeuden, KI und
  Einheiten dieses Takts. Mehrere Befehle laufen in der Reihenfolge, in der sie eingereiht wurden.
- Bei hohem Tempo rechnet das Spiel mehrere Takte je Bild; wer je Bild einmal liest, sieht nur jeden n-ten Takt (passt zu
  "der Lenker sieht bei Tempo 100 etwa alle 11 Ticks hin", lernen.py).
- Die Gegner-KI entscheidet ihre Bauten in jedem Takt NACH den Gebaeuden und VOR den Einheiten.

**Noch offen:** an welcher Stelle UCP3 sein `everyTick` (unser logik.lua-Takt, Rust-Kern) einhaengt - das steht nicht im
Spiel, sondern in UCP3; im Lauf messen (Tick-Zaehler vor/nach einem eigenen Befehl).

## 4. Darf hier gebaut werden? (B-95, 20.10.2026)

Abgelesen: `TileMapState::isBuildingPlacementAllowedAtTile` @ 0x004F9A60 (je Feld; Rueckgabe 0 = erlaubt, 1 = nicht erlaubt,
2 = dort steht schon ein Gebaeude), dazu `validateBuildingPlacementAtTile`, `placeBuilding` - `daten/dekomp_bauplatz.c`
(`DumpFunktionen.java`, Namen Placement/placeBuilding/...). Marke: **abgelesen**.

Ein Feld ist NICHT bebaubar, wenn (in dieser Reihenfolge geprueft):
1. es zu hoch liegt (`buildingHeightLimit`; Hoefe/Apfel/Hopfen/Weizen setzen dabei eine eigene Warnung) oder die
   Hoehe ueber `buildingMinHeight + buildingMaxHeightDifference` liegt;
2. schon ein Gebaeude darauf steht (Rueckgabe 2);
3. **eine Einheit darauf steht**: fuer einen MENSCHLICHEN Spieler blockiert JEDE Einheit ausser Huehnern - auch die
   eigenen Arbeiter; fuer einen KI-Spieler nur der Lord oder eine waehlbare fremde Einheit (`isAIPlayer`);
4. es Meer ist (LogicLayer Bit 0x1) oder Fluss (0x100000), oder fremde Mauer (WallOwnerLayer) - auf eigener Mauer nur
   Tore und Tuerme;
5. ein Baum darauf steht - bestimmte Baumarten blockieren immer, die uebrigen nur im Einzelspieler-Modus und fuer
   menschliche Spieler (eine KI im Gefecht darf dort bauen);
6. Sumpf/Graben-Eigenschaften des Gebaeudetyps es verbieten (buildingPlacementProperty_4/6/7).

**Was das fuer uns heisst:** Die SamurAI spielt auf einem Platz, dessen KI wir abschalten - fuer das Spiel ist sie damit
(vermutlich, `isAIPlayer` nicht im Lauf gemessen) ein menschlicher Spieler. Dann blockieren ihre EIGENEN Arbeiter, die gerade
ueber den Bauplatz laufen, jeden Bau dort, und Baeume blockieren wie beim Menschen. Das passt zu den Meldungen "Markt am
festen Platz nicht moeglich (z. B. Einheit drauf)" und zu Bauten, die erst im zweiten Versuch stehen. Zu messen: `isAIPlayer`
fuer den Platz der SamurAI nach der Uebernahme, und wie oft ein Bau an einer Einheit scheitert.

## Offen (nächste Abschnitte, B-95)

- ~~Spielerdaten~~, ~~Einheiten und Gebaeude~~ - Abschnitt 2 (die Felder, die wir lesen; weitere Felder stehen in den Strukturdateien).
- Karte: ~~Bauplatzpruefung~~ (Abschnitt 4); offen: Gelaende- und Begehbarkeits-Schichten im Einzelnen.
- ~~Takt~~ - Abschnitt 3 (offen nur noch: wo UCP3 `everyTick` einhaengt).
