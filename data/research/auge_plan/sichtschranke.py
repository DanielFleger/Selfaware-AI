"""Sichtschranke (P2): jedes Feld des Spielzustands bekommt eine Marke nach docs/FAIRNESS.md.

Eingabe:  zustand_felder.csv (Feldliste des Auges, B-142)
Ausgabe:  sichtschranke.csv  (bereich;feld;eigen;fremd;regel;sicher)
          sichtschranke_zweifel.md (Zusammenfassung und Zweifelsfälle für Daniel und Krari)

Marken:  erlaubt   - ein Spieler sieht es oder kennt es als Spielregel
         schaetzen - nur schätzen, nicht lesen (F4); gelesen nur mit Allwissen-Schalter (R6)
         verboten  - verborgen: fremde Ziele/Wege (R3), Zufall (F1), innere Zähler (R4), Gegner-KI (R3, F5)
         technik   - Darstellung, Netz, Menüs, Rechenhilfen der Engine: kein Spielwissen, für Entscheidungen nicht lesen
         unbekannt - Ghidra-Platzhaltername ohne Bedeutung: im fairen Spiel ungenutzt, bis benannt (fremd: verboten)
"eigen" gilt für Felder der eigenen Einheiten, Gebäude, Trupps und Spielerdaten, "fremd" für die aller anderen Spieler.
Globale Felder haben in beiden Spalten dieselbe Marke. Die Regeln greifen in der Reihenfolge der Liste, die erste gewinnt.
Vor den Mustern stehen die Einzelkorrekturen aus der Feldliste (B-168, Daniel 08.11.2026): Muster treffen auch Namen, die sie
nicht meinen ("ally" in "Rally"), und erkennen nicht jeden Platzhalternamen.
"""

import collections
import csv
import os
import re

from feldliste_gehirn import E_, G_, M_, P_, Q_, T_, zuordnung, zusatz

HIER = os.path.dirname(os.path.abspath(__file__))

# (Bereich-Muster, Feld-Muster, eigen, fremd, Regel, sicher)
R = [
    # --- Zufall, überall (F1)
    (r".", r"rng|random|Rng|Random|fixedRng", "verboten", "verboten", "F1 Zufallsstand", "ja"),
    (r"^SEC_RNG$", r".", "verboten", "verboten", "F1 Zufallsstand", "ja"),
    # --- Technik: Darstellung, Video, Menü, Laufzeiger der Engine
    (r"^(DAT_VideoBikQueue|RECT_|DAT_BlendFilterArrays|DAT_BitmapsFaces|DAT_TextureRenderCoreObject|DAT_MenuTextInputState"
     r"|TIME_LastGhostSoundMoment|CHAR_ARRAY_|DAT_UpdateUnitsTracker|DAT_UnitHasBecomeIdle|DAT_Tribe_HighestID|DAT_Current\w*ID"
     r"|DAT_CurrentUnitSlotID|DAT_DirectionAlgorithmState|DAT_MapSurfaceHeightRangeUnk|SEC_Section\d+)", r".",
     "technik", "technik", "Darstellung/Laufzeiger der Engine", "ja"),
    (r"^DAT_GameCore$", r".", "technik", "technik", "Spielkern (Takt, Fenster, Laden)", "ja"),
    # --- Gegner-KI (R3, F5): SamurAI spielt auf einem Menschen-Platz, eigene KI-Felder gibt es nicht
    (r"^(DAT_AIVState|DAT_AIVPlacementFit|DAT_AICState|DAT_TroopValueState)$", r".", "verboten", "verboten",
     "R3/F5 Innenleben der Gegner-KI", "ja"),
    (r"^GameState\.playerDataArray$", r"(^|\.)(ai|aiv|algo)[A-Z_]|aiTribe|aiSiege", "verboten", "verboten",
     "R3/F5 Innenleben der Gegner-KI", "ja"),
    (r"^GameState\.mapAndTime$", r"attackVectors|emenyHitArray", "verboten", "verboten", "R3 Angriffsplanung der KI", "ja"),
    (r"^DAT_TileMapState$", r"AIZone|AIInfo|MacroLayer|SEC_PathfindingCost", "verboten", "verboten", "R3 KI-Karten", "ja"),
    # --- Gleichlauf, Netz, Befehle
    (r"^DAT_GameSynchronyState$", r"HASH_|DPLAY|Packet|Lag|HostAnnounced|HostPlayer|MapFile|MapSelection|TwoIfNotHost|"
     r"MultiplayerGameVersions|SomeTime|TimeRelated|SomePlayerID|PlayerIDReceiver|RoundTable|ReceivedAIV",
     "technik", "technik", "Netz/Prüfsummen", "ja"),
    (r"^DAT_GameSynchronyState$", r"Chat|PlayerNames|PlayerGroupArray|PlayerMatchTimes|currentPlayerFullID|currentAIArray",
     "erlaubt", "erlaubt", "sichtbar: Chat, Namen, Teams, Plätze", "ja"),
    (r"^DAT_GameSynchronyState$", r"finalResults|final[A-Z]", "erlaubt", "erlaubt", "öffentliche Statistik: theoretisch mitzählbar (Daniel 08.11.)", "ja"),
    (r"^DAT_GameSynchronyState$", r"Command|command|Param\d|ActionPlan|queue|Queue", "technik", "verboten",
     "eigener Befehlsweg; fremde Befehle verborgen (R3)", "ja"),
    (r"^DAT_GameSynchronyState$", r".", "technik", "technik", "Gleichlauf der Engine", "ja"),
    # --- Wegfindung: Rechenhilfe der Engine, fremde Wege verborgen (R3)
    (r"^DAT_PathFindingState$", r".", "technik", "verboten", "Rechenhilfe; fremde Wege verborgen (R3)", "ja"),
    # --- Einheiten (DAT_UnitsState und DAT_GameState.units)
    (r"^DAT_UnitsState$", r"^DAT_EuroUnit|LastSelectedUnit", "erlaubt", "verboten",
     "eigene Anwerbe-Rückmeldung und Auswahl; fremde verborgen", "ja"),
    (r"^DAT_UnitsState$", r"DAT_UnitCount|DAT_LostChimps", "technik", "technik", "Laufzeiger", "ja"),
    (r"^DAT_UnitsState$", r"destination|Destination|target|Target|attackAt|attackedUnit|PathPlan|path|Path|rally|Rally|goTo|"
     r"digTile|movementType|huntedBy|aiUnitBehaviour|workplace|engineerManning|siegeTarget",
     "erlaubt", "verboten", "R3 Laufziele und Ziele: eigene Befehle bekannt, fremde verborgen (Ausnahme sichtbarer Angriff)", "ja"),
    (r"^DAT_UnitsState$", r"attackedBy", "erlaubt", "verboten", "R3: eigener Angreifer bekannt, sobald der Treffer sichtbar ist", "ja"),
    (r"^DAT_UnitsState$", r"[Cc]ooldown|[Tt]icker|[Cc]ountdown|[Tt]racker|[Tt]imer|reload|Reload|[Cc]ounter|vclock|Vclock",
     "erlaubt", "verboten", "eigene innere Zähler: ein guter Spieler schätzt sie (Daniel 08.11.); fremde R4", "ja"),
    (r"^DAT_UnitsState$", r"(^|[.\]])(x|y|xPosition|yPosition|tile|Tile|micro|Micro|height|Height|health|Health|unitType|owner|"
     r"displayColor|facing|animation|Animation|dying|logicalState|draw|gfx|graphic|healthbar|banked|climb|Climb|horse|"
     r"blessed|firstNameIndex|fade|Fade|disappear|isSelect)", "erlaubt", "erlaubt", "sichtbar: Ort, Art, Leben, Bild", "ja"),
    (r"^DAT_UnitsState$", r"state|State", "erlaubt", "erlaubt", "Zustand: an der Animation sichtbar (Daniel 08.11.)", "ja"),
    (r"^DAT_UnitsState$", r"(^|[.\]])(maxUnitCount|totalUnitsInSelection|unitCountOfSelection|nextUnitOnTheSameTile|unitOrderWhenOnSameTile|occupancyOrFlag|unusedUnitIDArrayIndex|unusedUnitIDArray|selectionRelatedFlag|ifSelectedThenPlayerID|SA|av|leftover)(\[\])*$", "technik", "technik", "Laufzeiger und Auswahl der Engine", "ja"),
    (r"^DAT_UnitsState$", r"(^|[.\]])(uid|maxHealth|maxHealthRatingLord|seated|vanish|spriteID|imageID2|someDrawYOffset|tunnelerFrame|terrainOrClimbHeight|buildingHeight|negativeHeight|unitCanClimb|cannotClimb|working|idle|previousTilePosition|orientationRelatedPositionX|orientationRelatedPositionY)(\[\])*$", "erlaubt", "erlaubt", "sichtbar oder Spielregel je Art", "ja"),
    (r"^DAT_UnitsState$", r".", "erlaubt", "verboten", "eigene Daten erlaubt (F8); fremdes Innenleben nicht sichtbar", "ja"),
    (r"^DAT_GameState$", r"^units\[\]", "technik", "technik", "Einheitenverweise", "ja"),
    # --- Gebäude
    (r"^DAT_BuildingsState$", r"resource|Resource|stored|Stored|flagons|appleCount", "erlaubt", "schaetzen",
     "F4 fremde Vorräte nur schätzen", "ja"),
    (r"^DAT_BuildingsState$", r"INT_Selected|DAT_Dragged|DAT_Temp|DAT_IsBuilding|NeedPeasants|DAT_Count", "technik", "technik",
     "Menü/Laufzeiger", "ja"),
    (r"^DAT_BuildingsState$", r"[Cc]ooldown|[Tt]imer|[Cc]ountdown|[Tt]racker|[Cc]ounter|vclock|Vclock|throttle|Throttle",
     "erlaubt", "verboten", "eigene innere Zähler: ein guter Spieler schätzt sie (Daniel 08.11.); fremde R4", "ja"),
    (r"^DAT_BuildingsState$", r"farmerDestination|hopFarmer|entranceAttempt|insideUnit|responsible|Responsible|attackWave",
     "erlaubt", "verboten", "innere Verweise, fremd verborgen", "ja"),
    (r"^DAT_BuildingsState$", r"(^|[.\]])(buildingType|\w*Variation|owner|\w*Owner|\w*[xyXY]$|\w*Entry|tile|\w*Tile|\w*[Hh]ealth|fire|\w*Fire|\w*[Pp]rogress|"
     r"gate|\w*Gate|drawBridge|drawbridge|animation|\w*Animation|gfx|\w*Visual|\w*EmployeeCount|campfire|hasUnitsOntop|hovel|"
     r"containsSiege|growCounter|buildMonth|\w*Height|height)", "erlaubt", "erlaubt", "sichtbar: Art, Ort, Leben, Brand, Bau, Tor",
     "ja"),
    (r"^DAT_BuildingsState$", r"(^|[.\]])(maxBuildingsCount|isFirstTickInLoop|structCount)(\[\])*$", "technik", "technik", "Laufzeiger der Engine", "ja"),
    (r"^DAT_BuildingsState$", r"(^|[.\]])(uid|uidWhenPlaced|logicalState|orientation|xPosition|yPosition|noRubble|shouldRenderRoof|sleeping|spriteID|spriteID2|spriteSheetID|visuallyActiveSpriteID|statueCommemoratingPlayerID|wheatGrowStateRelated|numberOfPopulationProvided|numberOfAnimals)(\[\])*$", "erlaubt", "erlaubt", "sichtbar oder Spielregel je Gebaeudeart", "ja"),
    (r"^DAT_BuildingsState$", r".", "erlaubt", "verboten", "eigene Daten erlaubt (F8); fremdes Innenleben nicht sichtbar", "ja"),
    # --- Trupps
    (r"^DAT_TribesState$", r"target|Target|rally|Rally|support|Support|selectionTarget|attack|siege|behavior|Behavior|"
     r"tribeState|stance|Stance|ALG_", "erlaubt", "verboten", "R3 Trupp-Ziele und Haltung: eigene bekannt, fremde verborgen",
     "ja"),
    (r"^DAT_TribesState$", r"owner|size|unitType|tribeType|orientation|facing|Speed|speed|unitsHealth", "erlaubt", "verboten",
     "fremde Trupps: nicht wissbar, nur aus gemeinsamer Bewegung erahnen (Daniel 08.11.)", "ja"),
    (r"^DAT_TribesState$", r"(^|[.\]])(DAT_CurrentTribeID|highestID|fcn_mtribe|someIndex|someUpdateUpperLimit|tribeCopiedToSlot0|unitSelectionBitMasked)(\[\])*$", "technik", "technik", "Laufzeiger und Auswahl der Engine", "ja"),
    (r"^DAT_TribesState$", r".", "erlaubt", "verboten", "eigene Trupps erlaubt; fremde Trupps nicht wissbar (F10)", "ja"),
    # --- Geschosse und Effekte
    (r"^DAT_EntityState$", r"target|Target", "verboten", "verboten",
     "F1/R3 Zielpunkt aus dem Zufall; aus der sichtbaren Flugbahn schätzen ist erlaubt", "ja"),
    (r"^DAT_EntityState$", r"[Cc]ount[Dd]own|[Tt]racker|every10Ticks|someCountDown|totalEntity|maxEntity|nextEntity|unused",
     "technik", "technik", "Laufzeiger/innere Zähler", "ja"),
    (r"^DAT_EntityState$", r"(^|[.\]])(x\w*|y\w*|xPosition|yPosition|\w*[Mm]icro\w*|\w*[Hh]eight\w*|\w*[Aa]ngle\w*|entityType\w*|"
     r"owner|fire\w*|imageID|graphic\w*|orientation|tile|travelled\w*|vCos|vSin|logicalState|origin\w*|starting\w*|_elapsed\w*)$",
     "erlaubt", "erlaubt",
     "sichtbar: Geschoss, Feuer, Flug", "ja"),
    (r"^DAT_EntityState$", r"(^|[.\]])(uid)(\[\])*$", "erlaubt", "erlaubt", "Kennung eines sichtbaren Objekts", "ja"),
    (r"^DAT_EntityState$", r"(^|[.\]])(unitID|unitUID|uidRef|unitID_healer)(\[\])*$", "erlaubt", "verboten", "Verweis auf die Einheit: eigene bekannt, fremde verborgen (R3)", "ja"),
    (r"^DAT_EntityState$", r".", "technik", "technik", "Bild- und Rechenhilfen der Effekte, Moewen", "ja"),
    # --- Spielerdaten
    (r"^GameState\.playerDataArray$", r"alive|Alive|team|Team|ally|Ally|color|Color|keep|Keep|lord|Lord|name|Name|"
     r"barracks|Barracks|armory|granary|stockpile|market|church|cathedral|Guild|mercenaryPost|engineers",
     "erlaubt", "erlaubt", "sichtbar: Lord, Bergfried, Team, Lage der Gebäude", "ja"),
    (r"^GameState\.playerDataArray$", r".", "erlaubt", "schaetzen", "F4 fremde Wirtschaft, Steuer, Rationen nur schätzen", "ja"),
    # --- Karte und Zeit
    (r"^GameState\.mapAndTime$", r"Price|price|month|Month|day|Day|year|Year|armySizeLimit|[Rr]ecruitable|Tradeable|difficulty|"
     r"gameOver|playerIsAlive|deerCount|cathedral", "erlaubt", "erlaubt", "Spielregeln, Zeit, Preise", "ja"),
    (r"^GameState\.mapAndTime$", r"counterForUpdating|countUpTo|newOrganisms|Copy|copy|editScenario|migrate", "technik",
     "technik", "Laufzeiger/Kopien", "ja"),
    (r"^GameState\.mapAndTime$", r"(^|[.\]])(noCowThrowing|noDogs|playerGroupArray|playerTeams|startGoods|startingPopularity|startingTroops|strongWalls2|totalNoRushTicks|week|weekChanged|weekTicks|skirmishFogOfWar|singlePlayerHasKeepAndGranary|rawDeerCount|playerPopulationStatistics)(\[\])*$", "erlaubt", "erlaubt", "Spieleinstellung, Zeit, oeffentliche Statistik", "ja"),
    (r"^GameState\.mapAndTime$", r"(^|[.\]])(playerBuildingInfoIndex|playerEnemenyUnitUIDShortList|playerEnemyBuildingIDs|playerEnemyBuildingUID|archers|x|y|somePlayerID)(\[\])*$", "verboten", "verboten", "R3 Angriffsplanung der KI", "ja"),
    (r"^GameState\.mapAndTime$", r".", "technik", "technik", "Spawnpunkte, Wegweiser, Haendler, Laufzeiger", "ja"),
    # --- Kartenebenen
    (r"^DAT_TileMapState$", r"Gfx|GFX|Alpha|Luminesence|Pillar|MiscDisplay|ShowHi|Changed|Floating|Sprite|flatView|"
     r"FutureMapOrientation|forceUpdate|Display|display", "technik", "technik", "Darstellung", "ja"),
    (r"^DAT_TileMapState$", r"buildingPlacement|DAT_Temp|DAT_Wall|DAT_Some|DAT_Cardinal|constructionTileCount|buildingX|buildingY|"
     r"buildingRotation|currentMapperCommand|ALG_|counter", "erlaubt", "technik",
     "eigene Bauplatzprüfung (die Oberfläche zeigt rot/grün)", "ja"),
    (r"^DAT_TileMapState$", r"Layer|Moat|moat|height|Height|direction", "erlaubt", "erlaubt",
     "sichtbare Karte; Begehbarkeit aus Sichtbarem ableitbar (Daniel 08.11.: ja)", "ja"),
    (r"^DAT_TileMapState$", r"pitchDitches\[\]|(^|[.\]])(mapOrientation|mapSize|maxPitchDitchCount|rockOrientation)$", "erlaubt", "erlaubt", "sichtbar: Pechgraeben, Kartengroesse, Drehung", "ja"),
    (r"^DAT_TileMapState$", r"unitDeathHeatMap", "verboten", "verboten", "R3 KI-Karte", "ja"),
    (r"^DAT_TileMapState$", r"(^|[.\]])(illegalBuild|placementWarning|wallPlacementCost|placedBuildingID)$", "erlaubt", "technik", "eigene Bauplatzpruefung", "ja"),
    (r"^DAT_TileMapState$", r".", "technik", "technik", "Laufzeiger und Zwischenspeicher der Karte", "ja"),
    # --- Landschaft, Wild, Mauern, Karte, Lobby
    (r"^DAT_LandscapeState$", r"wind", "technik", "technik", "Wind: nur Bildfolge für Flaggen und Bäume, feste Tabelle (updateWind)", "ja"),
    (r"^DAT_LandscapeState$", r".", "erlaubt", "erlaubt", "sichtbar: Bäume, Felsen", "ja"),
    (r"^DAT_WildlifeState$", r".", "erlaubt", "erlaubt", "sichtbar: Tiere", "ja"),
    (r"^DAT_WallAndPitchState$", r".", "erlaubt", "erlaubt", "sichtbar: Mauern, Pech", "ja"),
    (r"^DAT_MapPropertiesState$", r"[Ee]vent|[Ss]cenario|[Mm]ission", "verboten", "verboten",
     "Szenario-Auslöser: im Gefecht leer, in Szenarien verborgen (Daniel 08.11.: für Partien egal)", "ja"),
    (r"^DAT_MapPropertiesState$", r".", "erlaubt", "erlaubt", "Karteneigenschaften", "ja"),
    (r"^SEC_SkirmishLobbySetupStructure$", r".", "erlaubt", "erlaubt", "Lobby-Einstellungen sind bekannt", "ja"),
    (r"^DAT_GameState$", r"partialWoodCounter|timeTaxesOrRationsChange|releaseDogsFlag", "erlaubt", "schaetzen", "eigene Daten; fremde nur schaetzen (F4)", "ja"),
    (r"^DAT_GameState$", r".", "technik", "technik", "Laufzeiger, Schnellgruppen, Aufstellplaetze der Engine", "ja"),
    (r"^(DAT_SoundSystemState|DAT_ViewportRenderState|DAT_ResourceManager|DAT_BlendingDefinedData|DAT_MenuHandlerState"
     r"|DAT_MinimapViewState|DAT_MouseState|DAT_UIDragDropDefinedData|DAT_WindowAndDirectDraw|DAT_Button\w*"
     r"|DAT_MissionDefinedData|BOOL_\w*)$", r".", "technik", "technik", "Oberfläche, Ton, Dateien", "ja"),
    (r"^DAT_SkirmishDefinedData$", r".", "verboten", "verboten", "R3/F5 Regeln der Gegner-KI", "ja"),
    (r".", r".", "zweifel", "zweifel", "keine Regel", "zweifel"),
]
R = [(re.compile(b), re.compile(f), e, fr, t, s) for b, f, e, fr, t, s in R]


# Auffangregeln fuer benannte Felder: Platzhalternamen bleiben "unbekannt", nicht "technik"
AUFFANG = {
    "Bild- und Rechenhilfen der Effekte, Moewen",
    "Spawnpunkte, Wegweiser, Haendler, Laufzeiger",
    "Laufzeiger und Zwischenspeicher der Karte",
    "Laufzeiger, Schnellgruppen, Aufstellplaetze der Engine",
}


B168 = "(B-168)"
F4 = f"F4 fremde Wirtschaft nur schaetzen {B168}"
R4 = f"R4 innerer Zaehler: eigen erlaubt (F8), fremd nicht sichtbar {B168}"
R3 = f"R3 Ziel oder Weg: eigen bekannt, fremd verborgen {B168}"
INNEN = f"eigene Daten erlaubt (F8), fremdes Innenleben nicht sichtbar {B168}"
ZIEL = f"sichtbar: Ort, Sterben, Bild {B168}"
TECHNIK = f"Laufzeiger und Bild der Engine {B168}"


def _e(text):
    return [E_ + n for n in text.split()]


def _p(text):
    return [P_ + n for n in text.split()]


# (eigen, fremd, Regel, Felder). Geht vor den Mustern. Name in der Liste, der nicht existiert: Abbruch in main().
EINZELN_ROH = [
    # Muster passte zufaellig, fremd war erlaubt
    ("erlaubt", "schaetzen", F4, _p("marketGold granaryIsAlmostFilledUp")),
    ("erlaubt", "verboten", f"aus Sichtbarem selbst rechnen, fremd nicht lesen {B168}", _p("closestEnemyDistanceToTheLord")),
    ("erlaubt", "verboten", R4, _p("keepEnclosementRelatedCountdown")),
    ("technik", "technik", TECHNIK, _p("rallySearchOffset")),
    # Innere Zaehler und gemerkte Zustaende: an der Animation nicht sichtbar (F9 meint: kaempft, laeuft, laedt nach)
    ("erlaubt", "verboten", R4, _e("banked idle blessedAmount horseArcherShootCheckInterval horseArcherShootingVariation")),
    ("erlaubt", "verboten", f"gemerkter oder kommender Zustand: fremd nicht sichtbar (R3) {B168}",
     _e("cachedState state_2 state_3 unitType_3 unitTypeToChangeInto")),
    ("erlaubt", "verboten", f"Auswahl eines anderen Spielers ist nicht sichtbar {B168}", _e("isSelected")),
    ("erlaubt", "verboten", f"R3 Sammelpunkte: eigen bekannt, fremd verborgen {B168}",
     _p("""barracksAssemblyPoints[].x barracksAssemblyPoints[].y cathedralAssemblyPointX cathedralAssemblyPointY
        engineersAssemblyPoints[].x engineersAssemblyPoints[].y tunnelersGuildAssemblyPointX tunnelersGuildAssemblyPointY""")),
    # Nur wegen des Namens "unbekannt"; die Bedeutung zeigen Name und schreibende Funktionen
    ("erlaubt", "verboten", R3, _e("""targetID_OR_targetBuildingID targetedUnitID__OR__engineerMannedSiegeEngineRef
        targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID nextTileUnk destinationX_2Unk destinationY_2Unk
        digTileY__OR__countLifeCycleEngineersSentToManSiegeEngine lastEncounteredEnemyUnitIDUnk movementType_OR_targetUnitID""")),
    ("erlaubt", "verboten", R4, _e("assassinsMicroDistanceToEnemyUnk idleCounterUnk friendlyFireCounterUnk unitSpeedMatchingRelatedUnk")
     + [G_ + "idleTimerUnk"]),
    ("erlaubt", "verboten", INNEN, _e("horseOriginStableIDUnk horseOriginStablesBuildingIndexUnk isSelectable_OR_matchTime")),
    ("erlaubt", "erlaubt", ZIEL, _e("killedFlagUnk isDisappearingUnk currentTilePosition_2Unk gmIDUnk imageIDUnk spriteHeightUnk spriteWidthUnk")
     + [G_ + n for n in ("terrainHeightUnk", "playerColorUnk", "surfaceAreaUnk")] + ["trees[].animationFrameUnk", "trees[].animationFrame2Unk"]
     + _p("ladyIDUnk jesterIDUnk")),
    ("erlaubt", "erlaubt", f"Spielregel je Art {B168}", _e("someUnitStat2_meleeDamageUnk enemyNoticeFrequencyUnk moveableUnk")),
    ("erlaubt", "erlaubt", f"Zeit und Friedenszeit {B168}", [M_ + "totalGameTicksUnk", M_ + "noRushTicksLeftUnk"]),
    ("erlaubt", "erlaubt", f"sichtbar: Geschoss, Flug {B168}", [Q_ + "velocityUnk", Q_ + "speedUnk"]),
    ("erlaubt", "erlaubt", f"Statistik: das Spiel zaehlt hier nur den eigenen Platz (processUnitLossStatistic) {B168}", """DAT_CurrentPlayerUnitLosses DAT_UnitValueLossesPerEnemyPlayer
        DAT_UnitValueLossesPerEnemyPlayer[] DAT_DestroyedBuildingsCountHistory DAT_DestroyedBuildingsCountHistory[]""".split()),
    ("erlaubt", "verboten", f"F10 fremde Trupps nicht wissbar {B168}",
     [T_ + n for n in "percentageAttackingUnk percentageDyingUnk percentageMovingUnk percentageShootingUnk isRallyingUnk size2Unk".split()]),
    ("erlaubt", "schaetzen", F4, _p("""blessedPeopleCountUnk unblessedPeopleCountUnk averagePopulationGrowthUnk populationRelatedCrowdingCountUnk
        priestCountUnk nonInteractiveCitizenCountUnk ownsCathedralUnk ownsChurchUnk fearFactorProductivityUnk""")),
    ("erlaubt", "verboten", f"Buendnisanfragen: eigene bekannt, fremde verborgen {B168}",
     _p("requestStateUnk requestedAttackTargetUnk requestedGoodsArray1Unk[] requestedGoodsArray2Unk[] playerID_askerUnk")),
    ("technik", "technik", TECHNIK, _p("childTargetIDUnk rallySearchOffsetsUnk[]") + ["pathLinkageKeepWasUpdatedUnk", "DAT_CounterFoodWarningInterval"]
     + [Q_ + n for n in "hasDoneEffectUnk colorUnk graphicRotationUnk someCounter_OR_hitGround unitID_OR_seaGullID".split()]),
]
EINZELN = {n: (e, f, t) for e, f, t, namen in EINZELN_ROH for n in namen}
assert len(EINZELN) == sum(len(z[3]) for z in EINZELN_ROH), "Feld doppelt in den Einzelkorrekturen"
# Marke folgt aus dem Bedarf der Feldliste; dieselben Texte wie die Muster, damit gleiche Faelle gleich heissen
NACH_BEDARF = {
    "ki": ("verboten", "verboten", "R3/F5 Innenleben der Gegner-KI", "ja"),
    "zufall": ("verboten", "verboten", "F1 Zufallsstand", "ja"),
    "unklar": ("unbekannt", "verboten", "Bedeutung unbekannt (Ghidra-Platzhalter)", "unbekannt"),
}
LISTE, NACHGEHOLT = zuordnung(), zusatz()


def korrigiere(bereich, feld, e, fr, text, sicher):
    if feld in EINZELN:
        return (*EINZELN[feld], "ja")
    return NACH_BEDARF.get(LISTE.get((bereich, feld)) or NACHGEHOLT.get(feld), (e, fr, text, sicher))


def marke(bereich, feld, unklar):
    for rb, rf, e, fr, text, sicher in R:
        if not (rb.search(bereich) and rf.search(feld)):
            continue
        if unklar == "ja" and (not ({e, fr} <= {"technik", "verboten"}) or text in AUFFANG):
            # Ghidra-Platzhaltername: Bedeutung unbekannt, also auch nicht erlaubt. Im fairen Spiel bleibt das Feld
            # ungenutzt, bis es benannt ist; dann greift die passende Regel. Keine Frage an Daniel/Krari.
            return "unbekannt", "verboten", "Bedeutung unbekannt (Ghidra-Platzhalter)", "unbekannt"
        return e, fr, text, sicher
    raise AssertionError("letzte Regel greift immer")


def main():
    zeilen = list(csv.DictReader(open(os.path.join(HIER, "zustand_felder.csv"), encoding="utf-8"), delimiter=";"))
    aus, korrigiert, vorhanden = [], [], set()
    for z in zeilen:
        feld = z["feld"] or z["global"]
        unklar = z["name_unklar"]
        if re.search(r"(^|[.\]])(\+0x[0-9a-f]+|field\d+_0x[0-9a-f]+|_\d+_\d+_|[0-9a-f]{8})(\[\])?$", feld):
            unklar = "ja"  # reine Versatz- oder Adressnamen zählen ebenfalls als Platzhalter
        roh = marke(z["bereich"], feld, unklar)
        e, fr, text, sicher = korrigiere(z["bereich"], feld, *roh)
        if (e, fr) != roh[:2]:
            korrigiert.append({"feld": feld, "muster": f"{roh[0]} / {roh[1]}", "jetzt": f"{e} / {fr}", "regel": text})
        vorhanden.add(feld)
        aus.append({"bereich": z["bereich"], "feld": feld, "eigen": e, "fremd": fr, "regel": text, "sicher": sicher})
    fehlt = set(EINZELN) - vorhanden
    assert not fehlt, f"Einzelkorrektur ohne Feld: {sorted(fehlt)}"
    with open(os.path.join(HIER, "sichtschranke.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(aus[0]), delimiter=";")
        w.writeheader()
        w.writerows(aus)

    def zaehle(schl):
        return collections.Counter(x[schl] for x in aus)

    zw = [x for x in aus if x["sicher"] == "zweifel"]
    unb = [x for x in aus if x["sicher"] == "unbekannt"]
    fein = [x for x in zw if x["regel"].startswith(("unklares", "keine Regel"))]
    zw = [x for x in zw if x not in fein]
    gruppen = collections.Counter((x["bereich"], x["regel"]) for x in zw)
    fein_gr = collections.Counter(x["bereich"] for x in fein)
    with open(os.path.join(HIER, "sichtschranke_zweifel.md"), "w", encoding="utf-8") as f:
        f.write("# Sichtschranke: Ergebnis und Zweifelsfälle (P2)\n\n")
        f.write("Erzeugt von `sichtschranke.py` aus `zustand_felder.csv` nach den Regeln in `docs/FAIRNESS.md`.\n\n")
        f.write(f"**{len(aus)} Felder.** Eigene Daten: " + ", ".join(f"{k} {v}" for k, v in zaehle("eigen").most_common())
                + ". Fremde Daten: " + ", ".join(f"{k} {v}" for k, v in zaehle("fremd").most_common()) + ".\n\n")
        f.write(f"- **Sicher eingeordnet:** {len(aus) - len(zw) - len(unb) - len(fein)}\n"
                f"- **Bedeutung unbekannt** (Ghidra-Platzhalter, im fairen Spiel ungenutzt, bis benannt): {len(unb)}\n"
                f"- **Feinarbeit** (benannt, aber noch ohne passende Regel; im fairen Spiel vorerst ungenutzt): {len(fein)} in "
                + ", ".join(f"{b} {n}" for b, n in fein_gr.most_common()) + "\n"
                f"- **Fragen an Daniel und Krari:** {len(zw)} Felder in {len(gruppen)} Gruppen. Je Gruppe reicht eine "
                "Entscheidung, sie gilt dann für alle Felder darin.\n\n")
        liste, titel = (zw, "Offene Fragen") if gruppen else (fein, "Feinarbeit (alle Grundsatzfragen entschieden, Daniel 08.11.2026)")
        f.write(f"## {titel}\n\n| Bereich | Regel | Felder | eigen | fremd | Beispiele |\n|---|---|---|---|---|---|\n")
        for (b, t), n in collections.Counter((x["bereich"], x["regel"]) for x in liste).most_common():
            bsp = [x for x in liste if x["bereich"] == b and x["regel"] == t]
            f.write(f"| {b} | {t} | {n} | {bsp[0]['eigen']} | {bsp[0]['fremd']} | "
                    + ", ".join(sorted({x['feld'] for x in bsp})[:6]).replace("|", "/") + " |\n")
        f.write(f"\n## Korrekturen nach der Feldliste (B-168, Daniel 08.11.2026)\n\n{len(korrigiert)} Felder, bei denen die Muster allein "
                "eine andere Marke ergeben. Marke als eigen / fremd.\n\n| Regel | Muster sagten | jetzt | Felder | Beispiele |\n|---|---|---|---|---|\n")
        gr = collections.defaultdict(list)
        for x in korrigiert:
            gr[(x["regel"], x["muster"], x["jetzt"])].append(x["feld"])
        for (t, m, j), namen in sorted(gr.items(), key=lambda kv: -len(kv[1])):
            f.write(f"| {t} | {m} | {j} | {len(namen)} | " + ", ".join(f"`{n}`" for n in sorted(namen)[:5]) + " |\n")
    print(len(aus), "Felder; eigen", dict(zaehle("eigen")), "; fremd", dict(zaehle("fremd")), "; unbekannt", len(unb), "; Zweifel", len(zw),
          "in", len(gruppen), "Gruppen")


if __name__ == "__main__":
    main()
