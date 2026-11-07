# Sichtschranke: Ergebnis und Zweifelsfälle (P2)

Erzeugt von `sichtschranke.py` aus `zustand_felder.csv` nach den Regeln in `docs/FAIRNESS.md`.

**3564 Felder.** Eigene Daten: unbekannt 983, erlaubt 901, technik 779, verboten 616, zweifel 285. Fremde Daten: verboten 2131, technik 543, erlaubt 470, schaetzen 301, zweifel 119.

- **Sicher eingeordnet:** 2296
- **Bedeutung unbekannt** (Ghidra-Platzhalter, im fairen Spiel ungenutzt, bis benannt): 983
- **Feinarbeit** (benannt, aber noch ohne passende Regel; im fairen Spiel vorerst ungenutzt): 285 in DAT_UnitsState 89, GameState.mapAndTime 50, DAT_BuildingsState 48, DAT_TileMapState 37, DAT_TribesState 29, DAT_GameState 17, DAT_EntityState 15
- **Fragen an Daniel und Krari:** 0 Felder in 0 Gruppen. Je Gruppe reicht eine Entscheidung, sie gilt dann für alle Felder darin.

## Feinarbeit (alle Grundsatzfragen entschieden, Daniel 08.11.2026)

| Bereich | Regel | Felder | eigen | fremd | Beispiele |
|---|---|---|---|---|---|
| DAT_UnitsState | unklares Einheitenfeld | 89 | zweifel | verboten | maxUnitCount, totalUnitsInSelection, unitCountOfSelection[], units[].SA, units[]._someX_2, units[]._someY_2 |
| GameState.mapAndTime | unklares Karten-/Zeitfeld | 50 | zweifel | zweifel | mapAndTime.camelSpawnXY[], mapAndTime.deerSpawnLocationsXY[], mapAndTime.gameEventRelatedCountdown, mapAndTime.noCowThrowing, mapAndTime.noDogs, mapAndTime.playerBuildingInfoIndex[] |
| DAT_BuildingsState | unklares Gebäudefeld | 48 | zweifel | verboten | buildings[].field_0x2a5, buildings[].field_0x314, buildings[].flag1, buildings[].flag2, buildings[].killingPitField, buildings[].laddermanDataID |
| DAT_TileMapState | unklares Kartenfeld | 37 | zweifel | zweifel | SEC_Section1052, SEC_Section1053, SEC_Section1054, SEC_TileMap1104[], bitFlag, illegalBuild |
| DAT_TribesState | unklares Truppfeld | 29 | zweifel | verboten | DAT_CurrentTribeID, clans, fcn_mtribe, someUnitIDArrayCount, tribeCopiedToSlot0, tribes[].archerRelated |
| DAT_GameState | unklares Spielzustandsfeld | 17 | zweifel | zweifel | first500BuildingsCurrentIndexCounter[], first500BuildingsPerPlayer[], gameTicksLoadBalancer, hotkeyTribes[].units[].id, hotkeyTribes[].units[].uid, playerDataArray[].barracksParadegroundLocations[].x |
| DAT_EntityState | unklares Geschossfeld | 15 | zweifel | zweifel | entityArray[].displayValue, entityArray[].gmID, entityArray[].gmLookupValue, entityArray[].uid, entityArray[].uidRef, entityArray[].unitID |
