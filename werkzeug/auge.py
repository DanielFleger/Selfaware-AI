# -*- coding: utf-8 -*-
"""B-251 Das Auge - ein Takt-treuer Schnappschuss des ganzen Spielzustands, nur lesend (speicher.lies).

Auftrag SAI/Daniel 25.10.2026 15:10: alles sehen, was das Lagebild (villagestudio logik.lua: Tabellen einheiten/gebaeude)
nicht sieht - Geschosse in der Luft, Zustandsphasen und Restdauer, Sichtwert des Meuchelmoerders, vorausberechnetes
Zielfeld, Wegpunkte und Restweg, Hoehe, Treffer-Historie; Gegner-KI-Absicht; Felder; Gebaeude-Innenleben; Gegnerwirtschaft.

Bauweise: je Schnappschuss werden die grossen Bloecke mit wenigen ReadProcessMemory-Aufrufen am Stueck gelesen
(Einheiten, Geschosse, Gebaeude, Spieler, Trupps, Zeit), davor und danach die Taktnummer; stimmen beide ueberein, ist
der Schnappschuss "rein" (innerhalb eines Takts gelesen). Die Felder werden mit numpy-Strukturtypen ohne Kopie gelesen.

Alle Feldnamen sind die Namen aus dem Programm (Codex-Pipeline types.json, Ghidra-Analyse der Referenz-Exe); eigene
Uebersetzungen gibt es nur als Zusatzspalten mit dem Vorsatz "sre_" und sind im Wissensregister (B-251) erklaert.

Adressen (Referenz-Exe 1.41, Image-Base 0x400000; UCP3 aendert sie nicht):
  DAT_GameState 0x0112B0B8  playerDataArray +200000 (9 x 14836), mapAndTime +333524 (MapAndTimeState)
  totalGameTicksUnk 0x0117CADC (= mapAndTime+848; logik.lua TICKZAEHLER), DAT_GameCore.mapTimeInTicks 0x01FE7DA8
  DAT_UnitsState 0x01387F38  maxUnitCount +0, units +1556 (2500 x 1168)
  DAT_EntityState 0x02350300 maxEntityCount +0, fireCount +16, entityArray +20 (3000 x 232)
  DAT_BuildingsState 0x00F98520 structCount +0, maxBuildingsCount +8, buildings +20 (2000 x 812)
  DAT_TribesState 0x01667F78 tribes +40 (1250 x 820)
  DAT_TileMapState 0x01A93208 UnitLayer +2349024, EntityLayer +2509824, DamageLayer +3313824, pitchDitches +5501060
"""
import json
import math
import os
import struct
import sys
import time

import numpy as np
import numpy.lib.recfunctions  # noqa: F401  (repack_fields)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import speicher  # noqa: E402

TAKT = 0x0117CADC
TAKT_KERN = 0x01FE7DA8                 # DAT_GameCore.mapTimeInTicks (Abschuss-Takt der Geschosse)
GAME_STATE = 0x0112B0B8
SPIELER = GAME_STATE + 200000
SPIELER_GROESSE, SPIELER_ANZAHL = 14836, 9
ZEIT = GAME_STATE + 333524
UNITS_STATE = 0x01387F38
UNITS = UNITS_STATE + 1556
UNIT_GROESSE, UNITS_MAX = 1168, 2500
ENTITY_STATE = 0x02350300
ENTITIES = ENTITY_STATE + 20
ENTITY_GROESSE, ENTITIES_MAX = 232, 3000
BUILDINGS_STATE = 0x00F98520
BUILDINGS = BUILDINGS_STATE + 20
BUILDING_GROESSE, BUILDINGS_MAX = 812, 2000
TRIBES_STATE = 0x01667F78
TRIBES = TRIBES_STATE + 40
TRIBE_GROESSE, TRIBES_MAX = 820, 1250
TILEMAP = 0x01A93208
UNIT_LAYER = TILEMAP + 2349024          # ushort je Feld: erste Einheit auf dem Feld (Kette ueber nextUnitOnTheSameTile)
ENTITY_LAYER = TILEMAP + 2509824        # short je Feld: erstes Geschoss/Feuer auf dem Feld (Kette nextEntityOnThisTileByID)
DAMAGE_LAYER = TILEMAP + 3313824        # byte je Feld
PITCH = TILEMAP + 5501060               # PitchDitch[4000] x 20 Byte
PITCH_ANZAHL = TILEMAP + 5581060
FELDER = 80400

# Flugbahn (initializeProjectileVelocities 0x00403A20, moveProjectileEntity 0x004084A0): Winkel in Grad, Geschwindigkeit
# aus Tabelle; je Takt waechst speedUnk um den Zeitschritt (field43_0x5c4, z. B. Pfeil 0,18), zurueckgelegte Strecke in
# Mikroschritten = vCos * speedUnk * 0,25. Gesamtstrecke = field58_0x8c (Sichtlinien-Schritte, computeLineOfSightDistance).
FLUG_FAKTOR = 0.25
GRAVITY_DIV_2 = 9.812 / 2


def _dtype(felder, groesse):
    namen, formate, offsets = zip(*felder)
    return np.dtype({"names": namen, "formats": formate, "offsets": offsets, "itemsize": groesse})


# Unit (types.json /_HoldStrong/Map/Units/Unit, 1168 Byte) - nur die Felder, die das Auge braucht
UNIT = _dtype([
    ("animationTicker", "<i4", 64), ("animationSpeed", "<i4", 68), ("animationFrame", "<i4", 72),
    ("logicalState", "<i2", 140), ("unitType", "<i2", 142), ("owner", "<i2", 150), ("uid", "<i4", 152),
    ("targetUID", "<i4", 160), ("microXPosition", "<i2", 182), ("microYPosition", "<i2", 184),
    ("terrainOrClimbHeight", "<i2", 186), ("buildingHeight", "<i2", 188),
    ("shootTargetMicroX", "<i2", 190), ("shootTargetMicroY", "<i2", 192), ("shootTargetZ", "<i2", 194),
    ("x", "<i2", 196), ("y", "<i2", 198), ("destinationXPosition", "<i2", 200), ("destinationYPosition", "<i2", 202),
    ("tile", "<i4", 212), ("destinationTilePosition", "<i4", 216), ("moveDelay", "<i2", 244),
    ("tunnelerFinishedDigging", "<i2", 246), ("currentIndexInPathPlan", "<i2", 250), ("totalSizeOfPathPlan", "<i2", 252),
    ("pathPlanStart", "u1", (400,), 254) if False else ("pathPlanStart", ("u1", (400,)), 254),
    ("climbDataID", "<i2", 660), ("dying", "<i2", 672), ("nextUnitOnTheSameTile", "<u2", 674),
    ("isSelectable_OR_matchTime", "<i2", 676), ("closestEnemyMicroDistance", "<i2", 678),
    ("animationCycleNumber", "<i4", 688), ("facingDirection", "<i2", 692), ("stateBasedSpeed", "<i2", 702),
    ("state", "<i2", 704), ("cachedState", "<i2", 706), ("state_2", "<i2", 716), ("healthPercentage", "<i2", 724),
    ("tribeID", "<i2", 728), ("plannedDestinationX", "<i2", 732), ("plannedDestinationY", "<i2", 734),
    ("idle", "<i2", 778), ("targetID_OR_targetBuildingID", "<i2", 822), ("attackedUnitID", "<i2", 830),
    ("shootTargetedUnit", "<i2", 836), ("calculatedMovementSpeed", "<i2", 842), ("movementSpeed", "<i2", 844),
    ("stoneAmmunition", "<i2", 866), ("workplaceBuildingUID", "<i4", 872), ("substate", "<i2", 896),
    ("fixedRng", "<u4", 900), ("buildingID", "<i2", 920), ("targetingType", "<i2", 924),
    ("targetedUnitID__OR__engineerMannedSiegeEngineRef", "<i2", 926), ("targetedBuildingTile", "<u4", 936),
    ("lookForEnemy", "<i2", 940), ("attackedBy", "<i2", 942), ("huntedBy", "<i2", 946),
    ("health", "<i4", 968), ("maxHealth", "<i4", 972), ("attackAtTileX", "<i2", 1000), ("attackAtTileY", "<i2", 1002),
    ("nextAttackHurtsWall", "i1", 1006), ("lastEncounteredEnemyPlayerID", "<i2", 1024),
    ("aiUnitBehaviourType", "<i2", 1066), ("siegeTargetPlayerID", "<i2", 1074),
    ("lastEncounteredEnemyUnitIDUnk", "<i2", 1078), ("assassinsMicroDistanceToEnemyUnk", "<i4", 1080),
    ("enemyNoticeFrequencyUnk", "<i4", 1084), ("idleCounterUnk", "<i2", 1092),
], UNIT_GROESSE)

# Entity (/_HoldStrong/Map/Entities/Entity, 232 Byte): Geschosse, Feuer, Fahnen, Staub ...
ENTITY = _dtype([
    ("logicalState", "<i2", 40), ("entityType", "<i2", 42), ("owner", "<i2", 44), ("uid", "<i4", 48),
    ("field21_0x34", "<i4", 52), ("microX", "<i2", 56), ("microY", "<i2", 58), ("height", "<i2", 60),
    ("targetX", "<i2", 62), ("targetY", "<i2", 64), ("targetZ", "<i2", 66), ("xPosition", "<i2", 68),
    ("yPosition", "<i2", 70), ("tile", "<i4", 76), ("x_2", "<i2", 80), ("y_2", "<i2", 82),
    ("startingHeight", "<i2", 88), ("someCounter_OR_hitGround", "<i2", 108), ("speedUnk", "<f4", 120),
    ("vCos", "<f4", 124), ("vSin", "<f4", 128), ("travelledDistance", "<i2", 132), ("field58_0x8c", "<i2", 140),
    ("velocityUnk", "<i2", 150), ("_elapsedTimeOrGravityAccumulator", "<f4", 152), ("startingAngle", "<i2", 156),
    ("unitID", "<i2", 160), ("unitID_OR_seaGullID", "<i2", 162), ("hasDoneEffectUnk", "<i2", 178),
    ("field80_0xba", "<i2", 186), ("rng_2", "<i2", 188), ("field90_0xd0", "<i2", 206), ("unitUID", "<i4", 212),
    ("fireIntensity", "<i2", 216),
    # Luft-Stopp der Steine (B-252): Kandidatenfelder mitlesen
    ("unknownAnimationFrameRelated", "<i2", 20), ("field37_0x5a", "<i2", 90), ("field50_0x74", "<i2", 116),
    ("orientation", "<i4", 136), ("field58_0x8c_b", "<i2", 140), ("heightDifference", "<i4", 144), ("field72_0xa8", "<i2", 168),
    ("hasDoneEffectUnk_b", "<i2", 178), ("someTracker", "<i2", 180), ("field82_0xbe", "<i2", 190), ("field83_0xc0", "<i2", 192),
    ("displayValue", "<i4", 196), ("unknownDistanceRelatedValue", "<i2", 218),
], ENTITY_GROESSE)

# Building (/_HoldStrong/Map/Buildings/Building, 812 Byte)
BUILDING = _dtype([
    ("recruitTimer", "<i2", 192), ("logicalState", "<i2", 208), ("buildingType", "<i2", 210), ("owner", "<i2", 214),
    ("uid", "<i4", 216), ("x", "<i2", 238), ("y", "<i2", 240), ("currentHealth", "<i2", 268), ("maxHealth", "<i2", 270),
    ("state", "<i2", 280), ("resources", ("<i4", (23,)), 296), ("currentNumberOfResource", "<u4", 388),
    ("currentLimitOfResource", "<u4", 392), ("currentStoredResourceType", "<i2", 396),
    ("buildingTypeBasedEmployeeCount", "<i2", 408), ("currentEmployeeCount", "<i2", 410),
    ("currentlyNeededEmployeeCount", "<i2", 412), ("workerID", ("<i2", (4,)), 414), ("buildingProgress", "<i4", 632),
    ("timeAlive", "<u4", 636), ("producedItemType", "<i2", 656), ("drawbridgeState2", "u1", 659),
    ("drawBridgeState1", "u1", 660), ("containsSiegeMangonel1OrBallista2", "u1", 661), ("gateState", "u1", 675),
    ("gateCloseOpenTimer", "<i2", 696), ("fireDuration", "<i2", 702), ("gateState2", "<i2", 704),
    ("cooldownTimer", "<i2", 708), ("ifFireThenResponsiblePlayer", "<u2", 734), ("insideUnitID", ("<i2", (4,)), 736),
    ("hasUnitsOntop", "<i2", 760),
], BUILDING_GROESSE)

# PlayerData (/_HoldStrong/Game/Player/PlayerData, 14836 Byte)
PLAYER = _dtype([
    ("popularity", "<i4", 96), ("populationCap", "<i4", 116), ("availablePeasantsAtFire", "<i4", 136),
    ("currentResources", ("<i4", (25,)), 1232), ("armySize", "<i4", 1340), ("totalFood", "<i4", 8348),
    ("foodTypesInStock", "<i4", 8352), ("weeksWithoutFood", "<i4", 8356), ("currentCrossbowmen", "<i4", 8380),
    ("currentSpearmen", "<i4", 8384), ("currentPikemen", "<i4", 8388), ("currentMacemen", "<i4", 8392),
    ("currentSwordsmen", "<i4", 8396), ("countArabSwordsman", "<i4", 8436), ("fearFactorLevel", "<i4", 8500),
    ("totalEnemyUnitsCount", "<i4", 8520), ("currentPopulation", "<i4", 8576), ("taxesSetting", "<i4", 8584),
    ("rationsSetting", "<i4", 8588), ("lordID", "<i4", 8696), ("lordUID", "<i4", 8700), ("troopsLost", "<i4", 8752),
    ("troopsKilled", "<i4", 8756), ("aivID", "<i4", 8956), ("aiType", "<i4", 8960),
    ("countAssassinsAndArabianSwordsman", "<i4", 10804), ("resourcesToAcquireArray", ("<i4", (24,)), 10864),
    ("closestEnemyDistanceToTheLord", "<i4", 11108), ("idlePeasantsCount", "<i4", 11116),
    ("aiStrengthState", "<i4", 11124), ("aiPlayerState", "<i4", 11172), ("totalAssassinTroops", "<i4", 11184),
    ("totalLaddermenTroops", "<i4", 11192), ("totalTunnelerTroops", "<i4", 11196), ("totalUnitPatrolTroops", "<i4", 11200),
    ("totalUnitBackupTroops", "<i4", 11204), ("totalUnitEngageTroops", "<i4", 11208),
    ("totalUnitSiegeDefTroops", "<i4", 11212), ("attackedPlayerID", "<i4", 11224),
    ("totalDefensiveTroopsUnk", "<i4", 12520), ("totalRaidingTroopsUnk", "<i4", 12524), ("totalAttackTroops", "<i4", 12528),
    ("aiStrengthFeeling", "<i4", 12532), ("aiRecruitUnitChoiceState", "<i4", 12536),
    ("aiRecruitIntervalTracker", "<i4", 12540), ("aiTribeIDs", ("<i2", (200,)), 12556),
    ("top100TargetableBuildings", ("<i2", (100,)), 13756), ("attackAssaultDelayRelatedValue", "<i4", 14364),
    ("isNotNervousByEnemyTroopValue", "<i4", 14368), ("requestedAttackTargetUnk", "<i4", 14416),
    ("currentWaveRandomAttackingStrength", "<i4", 14496), ("totalEnemyTroopValueByPlayerID", ("<i4", (9,)), 14520),
    ("totalEnemyTroopValue", "<i4", 14560), ("totalTroopValue", "<i4", 14568), ("currentAttackRaidParameter", "<i4", 14580),
    ("totalEnemyRangedTroopValue", "<i4", 14608), ("currentAttackWave", "<i4", 14628),
    ("aiCoordinatedAttackPatience", "<i4", 14640), ("attackTicker", "<i4", 14704),
    ("relativeStrengthOfTeamComparedToEnemy", "<i2", 14784), ("aiStateCounter", "<i2", 14786),
], SPIELER_GROESSE)

# Tribe (/_HoldStrong/Map/Units/Tribe, 820 Byte) - KI-Trupps
TRIBE = _dtype([
    ("owner", "<i4", 4), ("tribeState", "<i2", 24), ("tribeType", "<i2", 26), ("tribeBehaviorType", "<i2", 40),
    ("selectionTargetUnitID", "<i2", 50), ("size", "<i2", 52), ("countdown2", "<i2", 488), ("isRallyingUnk", "<i2", 518),
    ("targetX", "<i2", 526), ("targetY", "<i2", 528), ("unitType", "<i2", 552), ("rallyPointArray", ("<i2", (9, 2)), 568),
    ("currentRallyPointIndex", "<i2", 608), ("rallyPointCount", "<i2", 610), ("countdown", "<i2", 654),
    ("attackWave", "<i2", 660), ("unitStance", "<i2", 696), ("targetPlayer_outpost", "<i2", 718),
    ("targetBuildingID", "<i2", 720), ("targetBuildingUID", "<i4", 724),
], TRIBE_GROESSE)

# AICSpecification (676 Byte, 20 Stueck ab DAT_AICState 0x023FC8E8): die "Persoenlichkeit" je KI-Art (aiType 1..16 -> Index aiType-1)
BUILDING_HEIGHTS = 0x005BB910    # DAT_BuildingHeights, 100 int je Gebaeudeart (Dachhoehe fuer returnSomeHeight 0x004FF990)
BUILDING_LAYER = 0x01C95BB8
_bauhoehen = None


def bauhoehen():
    global _bauhoehen
    if _bauhoehen is None:
        _bauhoehen = np.frombuffer(speicher.lies(BUILDING_HEIGHTS, 400), dtype="<i4").copy()
    return _bauhoehen


# getBuildingHeightForBuildingID 0x00409DB0: feste Hoehen fuer Herrenhaus/Bergfriede/Torhaeuser/Tuerme, sonst 0
FESTE_BAUHOEHE = {11: 0x40, 12: 0x5C, 13: 0xBE, 40: 0x80, 41: 0x80, 74: 0x128, 75: 0x94, 76: 0xB4, 77: 0xC0, 78: 0xC0}


def boden_hoehe(hoehe, logik, btyp, organism=0):
    """returnSomeHeight(tile, 0) nachgerechnet: die Hoehe, unter der ein Geschoss aufschlaegt. btyp = Gebaeudeart auf dem
    Feld (0 = keins). Gemessen 25.10. (B-252): Steine stoppen genau dort, wo Hoehe < HeightLayer + BuildingHeights[Art]."""
    if logik & 0x10000000:
        return hoehe + FESTE_BAUHOEHE.get(btyp, 0)
    if (logik & 0x400) == 0:
        if (logik & 0x80) and (logik & 0x100) == 0 and organism > 1999:
            return hoehe + 0x32
        return hoehe
    if btyp in (40, 41, 42, 43, 44):
        return hoehe + FESTE_BAUHOEHE.get(btyp, 0)
    if btyp in (45, 46, 61, 74, 75, 76, 77, 78):
        return hoehe + FESTE_BAUHOEHE.get(btyp, 0) + 10
    if btyp == 7:
        return hoehe
    bh = bauhoehen()
    return hoehe + int(bh[btyp]) if 0 <= btyp < len(bh) else hoehe


AIC_STATE = 0x023FC8E8
AIC = _dtype([
    ("criticalPopularity", "<i4", 24), ("lowestPopularity", "<i4", 28), ("highestPopularity", "<i4", 32),
    ("taxesMin", "<i4", 36), ("taxesMax", "<i4", 40), ("buildInterval", "<i4", 120), ("recruitGoldThreshold", "<i4", 196),
    ("RaidRetargetDelay", "<i4", 496), ("AttForceBase", "<i4", 500), ("AttForceRandom", "<i4", 504),
    ("AttForceSupportAllyThreshold", "<i4", 508), ("AttForceRallyPercentage", "<i4", 512), ("AttMovingTribesThreshold", "<i4", 516),
    ("AttAssaultDelay", "<i4", 520), ("AttUnitPatrolRecommandDelay", "<i4", 524), ("AttCoordinationPreference", "<i4", 528),
    ("SiegeEngine", ("<i4", (8,)), 532), ("CowThrowInterval", "<i4", 564), ("AttMaxEngineers", "<i4", 572),
    ("AttDiggingUnit", "<i4", 576), ("AttDiggingUnitMax", "<i4", 580), ("AttUnit2", "<i4", 584), ("AttUnit2Max", "<i4", 588),
    ("AttMaxAssassins", "<i4", 592),
], 676)


def aic_lesen():
    """[20] AICSpecification live (UCP3 kann sie aendern - deshalb nicht aus der Datei)."""
    return np.frombuffer(speicher.lies(AIC_STATE, 20 * 676), dtype=AIC)


BUILDING_PACKED = np.lib.recfunctions.repack_fields(BUILDING)   # nur die gelesenen Felder, dicht gepackt (fuer Protokolle)

PITCH_DTYPE = _dtype([("tile", "<i4", 0), ("uid", "<i4", 4), ("owner", "<i2", 8), ("x", "<i2", 10), ("y", "<i2", 12),
                      ("state", "<i2", 16)], 20)

# Aufzaehlungen aus types.json
UNIT_STATE = {0: "US_DETERMINE_NEXT_STATE", 1: "US_IDLE", 4: "US_RELOAD_WEAPON", 5: "US_AIM_WEAPON", 6: "US_FIRE_WEAPON",
              7: "US_LOOK_AROUND", 8: "US_STAND_UP", 11: "US_SIT_DOWN", 101: "US_MOVE_TO_DESTINATION", 106: "US_MELEE_ATTACK",
              107: "US_MELEE_ATTACK_WALL", 109: "US_JESTER_ROAM_TO", 110: "US_DISAPPEAR", 111: "US_DEATH_01",
              112: "US_DEATH_02", 113: "US_DEATH_03", 114: "US_STONE_DEATH_01", 115: "US_STONE_DEATH_02",
              116: "US_STONE_DEATH_03", 122: "US_APPEAR", 125: "US_DIG", 126: "US_ASSASSIN_THROWING_HOOK",
              127: "US_ASSASSIN_CLIMBING_UP", 128: "US_ASSASSIN_START_CLIMBING_DOWN", 129: "US_ASSASSIN_CLIMBING_DOWN"}
INSTRUCTION = {3: "UIT_NO_INSTRUCTION_OR_MOVE", 4: "UIT_UNIT_ATTACK_UNIT", 5: "UIT_ATTACK_LAND", 6: "UIT_DIG_MOAT",
               7: "UIT_FILL_MOAT", 9: "UIT_ATTACK_BUILDING", 15: "UIT_CONSTRUCT_SIEGE_EQUIPMENT", 16: "UIT_MAN_SIEGE_EQUIPMENT",
               17: "UIT_EXIT_SIEGE_EQUIPMENT", 20: "UIT_THROW_OIL", 22: "UIT_THROW_COW", 23: "UIT_ATTACK_WALL",
               24: "UIT_SET_LADDER", 30: "UIT_DISBAND", 31: "UIT_STOP", 33: "UIT_SHOOT_TARGET", 34: "UIT_LIGHT_PITCH"}
ENTITY_TYPE = {0: "ET_UNKNOWN", 1: "ET_ARROW_AND_DEFAULT", 2: "ET_CATAPULT", 3: "ET_TREBUCHET", 4: "ET_MANGONEL",
               7: "ET_CROSSBOWARROW", 9: "ET_FIRE", 10: "ET_FLAG_1", 11: "ET_FLAG_4", 12: "ET_FLAG_2", 13: "ET_FLAG_3",
               14: "ET_BRAZIER", 15: "ET_HEADS_ON_SPIKES", 20: "ET_BALLISTA", 21: "ET_DUST_CLOUD", 22: "ET_COW_POISON_CLOUD",
               23: "ET_COW_FLYING", 29: "ET_SEAGULL", 33: "ET_SLINGER", 34: "ET_FIRETHROWER", 36: "ET_FIRETHROWER_UNTARGETED",
               37: "ET_FIREBALLISTA"}
GESCHOSSE = {1, 2, 3, 4, 7, 20, 22, 23, 33, 34}
AI_STRENGTH = {0: "AIST_DEFAULT", 1: "AIST_WEAK", 2: "AIST_STRONG"}
AI_RECRUIT = {0: "AIRUC_DEFENSIVE", 1: "AIRUC_RAIDING", 2: "AIRUC_ATTACKING"}
STANCE = {0: "USE_STAND_GROUND", 1: "USE_DEFENSIVE", 2: "USE_AGGRESSIVE"}
TRIBE_TYPE = {2: "AITT_TUNNELERS", 3: "AITT_ARCHERS", 4: "AITT_LADDERMEN", 5: "AITT_SPEARMEN", 6: "AITT_PIKEMEN",
              7: "AITT_CROSSBOWMEN", 8: "AITT_SWORDSMEN", 9: "AITT_MACEMEN", 10: "AITT_KNIGHTS", 11: "AITT_ENGINEERS"}
RT = {1: "LOGS", 2: "WOOD", 3: "HOPS", 4: "STONE", 5: "PARTIALSTONE", 6: "IRON", 7: "PITCH", 8: "PARTIALPITCH", 9: "WHEAT",
      10: "BREAD", 11: "CHEESE", 12: "MEAT", 13: "APPLE", 14: "ALE", 15: "GOLD", 16: "FLOUR", 17: "BOW", 18: "CROSSBOW",
      19: "SPEAR", 20: "PIKE", 21: "MACE", 22: "SWORD", 23: "LEATHERARMOR", 24: "IRONARMOR"}
# Richtungen wie facingDirection (prepareProjectileTarget 0x0053CBD0: 0 = y-1, 1 = x+1/y-1, 2 = x+1 ... im Uhrzeigersinn)
RICHTUNG = {0: (0, -1), 1: (1, -1), 2: (1, 0), 3: (1, 1), 4: (0, 1), 5: (-1, 1), 6: (-1, 0), 7: (-1, -1)}


# --- Phasen-Tabellen (Bild je Animationsschritt) aus spielwerte.SCHUSS/HACKEN: live, sonst aus der Referenz-Exe ------------
# Gemessen 25.10. (Lauf 153627, Bogenschuetze 96): state = Phase (4 nachladen, 5 zielen, 6 schiessen), animationCycleNumber
# = Schritt in der Phase ab 0, Bild = Tabelle[Schritt], Schritt alle (speed+1) Takte, Phase endet nach dem letzten Schritt,
# dazwischen 1 Takt state 0. Der Pfeil entsteht im Schritt, in dem die Tabelle zum ersten Mal das "schuss_bei"-Bild zeigt
# (Bogenschuetze: Bild 6 = Schritt 15 = 46 Takte nach Phasenstart). animationTicker zaehlt je Takt, ist aber nicht an den
# Phasenstart gebunden - der Rest im laufenden Schritt ist deshalb nur auf +-speed Takte bekannt (Mitte angenommen).
PHASEN_ZUSTAND = {4: "nachladen", 5: "zielen", 6: "schiessen"}
_phasen = {}


def _phasen_tabellen():
    """{UT: {"phasen": {name: (schritte, speed, tabelle)}, "schuss_schritt": n}} fuer die Schuetzen mit drei Phasen; {UT: (schritte, speed)}
    fuer Hacken (Zustand 107) unter dem Schluessel "hacken"."""
    if _phasen:
        return _phasen
    try:
        import spielwerte
    except Exception:  # noqa: BLE001
        return _phasen
    lies = None
    try:
        speicher.griff()
        lies = speicher.lies
    except Exception:  # noqa: BLE001
        try:
            lies = spielwerte.quelle_datei(spielwerte.REFERENZ_EXE)
        except Exception:  # noqa: BLE001
            return _phasen

    def tabelle(adr):
        roh = lies(adr, 200)
        b = [(x if x < 128 else x - 256) for x in roh]
        n = next((i for i, v in enumerate(b) if v < 1), 200)
        return b[:n]
    for ut, z in spielwerte.SCHUSS.items():
        if len(z["phasen"]) != 3:
            continue
        ph = {}
        for name, adr, speed in z["phasen"]:
            t = tabelle(adr)
            ph[name] = (len(t), speed, t)
        sb = z["schuss_bei"]
        schritt = None
        if sb.startswith("Bild "):
            bild = int(sb.split()[1])
            schritt = next((i for i, v in enumerate(ph["schiessen"][2]) if v == bild), None)
        elif sb.startswith("Zyklus "):
            schritt = int(sb.split()[1])
        _phasen[ut] = {"phasen": ph, "schuss_schritt": schritt}
    hk = {}
    for ut, tabellen in spielwerte.HACKEN.items():
        n = [len(tabelle(adr)) for adr, sp in tabellen]
        hk[ut] = (int(round(sum(n) / float(len(n)))), tabellen[0][1])
    _phasen["hacken"] = hk
    return _phasen


def phase_rest(ut, zustand, schritt, ticker=None):
    """(rest_takte_der_phase, schritte_der_phase, takte_bis_naechster_schuss) oder (None, None, None).
    Mitte des laufenden Schritts angenommen: Unsicherheit +-speed Takte."""
    tab = _phasen_tabellen()
    if ut in tab and zustand in PHASEN_ZUSTAND:
        ph = tab[ut]["phasen"]
        name = PHASEN_ZUSTAND[zustand]
        n, sp, _ = ph[name]
        rest = max(0, (n - schritt - 1)) * (sp + 1) + (sp + 1) // 2 + 1
        ss = tab[ut]["schuss_schritt"]
        schuss = None
        if ss is not None:
            n_l, sp_l, _ = ph["nachladen"]
            n_z, sp_z, _ = ph["zielen"]
            n_s, sp_s, _ = ph["schiessen"]
            bis_schuss_in_schiessen = ss * (sp_s + 1)
            if zustand == 6:
                if schritt < ss:
                    schuss = (ss - schritt - 1) * (sp_s + 1) + (sp_s + 1) // 2 + 1
                elif schritt == ss:
                    schuss = 0          # der Schuss faellt im ersten Takt dieses Schritts (gemessen: Bogenschuetze Schritt 15)
                else:
                    schuss = rest + 1 + n_l * (sp_l + 1) + n_z * (sp_z + 1) + bis_schuss_in_schiessen
            elif zustand == 4:
                schuss = rest + n_z * (sp_z + 1) + bis_schuss_in_schiessen
            else:
                schuss = rest + bis_schuss_in_schiessen
        return rest, n, schuss
    if zustand == 107 and "hacken" in tab and ut in tab["hacken"]:
        n, sp = tab["hacken"][ut]
        return max(0, (n - schritt - 1)) * (sp + 1) + (sp + 1) // 2 + 1, n, None
    return None, None, None


_feldnr_karte = None


def feldnummern():
    """int32 [x, y] -> Feldnummer (-1 ausserhalb der Raute), einmal aus der translationMatrix gelesen."""
    global _feldnr_karte
    if _feldnr_karte is None:
        xs, ys, ks = speicher.felder()
        fn = np.full((400, 400), -1, np.int32)
        fn[xs, ys] = ks
        _feldnr_karte = fn
    return _feldnr_karte


def _i4(adr):
    return struct.unpack("<i", speicher.lies(adr, 4))[0]


def _u4(adr):
    return struct.unpack("<I", speicher.lies(adr, 4))[0]


class Schnappschuss(object):
    """Ein Lesevorgang. rein = Taktnummer vor und nach dem Lesen gleich."""

    def __init__(self, versuche=3, mit_trupps=True, mit_feldern=True):
        for versuch in range(1, versuche + 1):
            t0 = time.perf_counter()
            self.takt = _u4(TAKT)
            self.takt_kern = _u4(TAKT_KERN)
            n_u = min(max(_i4(UNITS_STATE), 0), UNITS_MAX)
            n_e = ENTITIES_MAX   # maxEntityCount (+0) haengt hinterher - immer alle 3000 lesen (0,7 MB, < 1 ms)
            n_b = min(max(_i4(BUILDINGS_STATE + 8), 0), BUILDINGS_MAX)
            self.einheiten = np.frombuffer(speicher.lies(UNITS, n_u * UNIT_GROESSE), dtype=UNIT) if n_u else np.zeros(0, UNIT)
            self.entities = np.frombuffer(speicher.lies(ENTITIES, n_e * ENTITY_GROESSE), dtype=ENTITY) if n_e else np.zeros(0, ENTITY)
            self.gebaeude = np.frombuffer(speicher.lies(BUILDINGS, n_b * BUILDING_GROESSE), dtype=BUILDING) if n_b else np.zeros(0, BUILDING)
            self.spieler = np.frombuffer(speicher.lies(SPIELER, SPIELER_ANZAHL * SPIELER_GROESSE), dtype=PLAYER)
            zeit = speicher.lies(ZEIT + 804, 48)
            self.woche, self.monat, self.jahr = struct.unpack_from("<iii", zeit, 0)
            self.teams = list(struct.unpack("<9i", speicher.lies(ZEIT + 3516, 36)))
            if mit_trupps:
                self.trupps = np.frombuffer(speicher.lies(TRIBES, TRIBES_MAX * TRIBE_GROESSE), dtype=TRIBE)
            else:
                self.trupps = np.zeros(0, TRIBE)
            if mit_feldern == "hoehe":
                self.hoehe = np.frombuffer(speicher.lies(speicher.HOEHE, FELDER), dtype="u1")
                self.bau = np.frombuffer(speicher.lies(BUILDING_LAYER, FELDER * 2), dtype="<u2")
                self.logik = np.frombuffer(speicher.lies(speicher.LOGIK, FELDER * 4), dtype="<u4")
            elif mit_feldern:
                n_p = min(max(_i4(PITCH_ANZAHL), 0), 4000)
                self.pech = np.frombuffer(speicher.lies(PITCH, n_p * 20), dtype=PITCH_DTYPE) if n_p else np.zeros(0, PITCH_DTYPE)
                self.schaden = np.frombuffer(speicher.lies(DAMAGE_LAYER, FELDER), dtype="u1")
                self.hoehe = np.frombuffer(speicher.lies(speicher.HOEHE, FELDER), dtype="u1")
                self.bau = np.frombuffer(speicher.lies(BUILDING_LAYER, FELDER * 2), dtype="<u2")
                self.logik = np.frombuffer(speicher.lies(speicher.LOGIK, FELDER * 4), dtype="<u4")
            takt_danach = _u4(TAKT)
            self.dauer_ms = (time.perf_counter() - t0) * 1000.0
            self.rein = takt_danach == self.takt
            self.versuch = versuch
            if self.rein:
                break

    def behalten(self, spieler=None):
        """Kompakte Kopie fuer Aufnahmen (Serialisierung spaeter): Geschosse/Feuer, Einheiten der Spieler, Spielerdaten."""
        u = self.einheiten
        m = u["logicalState"] == 2
        if spieler is not None:
            m &= np.isin(u["owner"], list(spieler))
        e = self.entities
        me = (e["logicalState"] != 0)
        t = self.trupps
        mt = (t["size"] > 0) if len(t) else np.zeros(0, bool)
        g = self.gebaeude
        mg = (g["logicalState"] == 2) if len(g) else np.zeros(0, bool)
        gp = np.lib.recfunctions.repack_fields(g[mg]) if mg.any() else np.zeros(0, BUILDING_PACKED)
        return {"takt": self.takt, "takt_kern": self.takt_kern, "rein": self.rein, "dauer_ms": self.dauer_ms,
                "trupps": t[mt].copy(), "trupps_idx": np.flatnonzero(mt), "gebaeude": gp, "gebaeude_idx": np.flatnonzero(mg),
                "einheiten": u[m].copy(), "einheiten_idx": np.flatnonzero(m), "entities": e[me].copy(),
                "entities_idx": np.flatnonzero(me), "spieler": self.spieler.copy(), "hoehe": getattr(self, "hoehe", None),
                "feldnr": feldnummern() if getattr(self, "hoehe", None) is not None else None,
                "bau": getattr(self, "bau", None), "logik": getattr(self, "logik", None)}

    def treffer(self):
        return treffer_folge(self)

    @classmethod
    def aus_behalten(cls, d):
        s = cls.__new__(cls)
        s.takt, s.takt_kern, s.rein, s.dauer_ms, s.versuch = d["takt"], d["takt_kern"], d["rein"], d["dauer_ms"], 1
        s.einheiten, s.entities, s.spieler = d["einheiten"], d["entities"], d["spieler"]
        s._einheiten_idx, s._entities_idx = d["einheiten_idx"], d["entities_idx"]
        s.trupps = d.get("trupps", np.zeros(0, TRIBE))
        s._trupps_idx = d.get("trupps_idx")
        s.gebaeude = d.get("gebaeude", np.zeros(0, BUILDING_PACKED))
        s._gebaeude_idx = d.get("gebaeude_idx")
        s.hoehe = d.get("hoehe")
        s.bau = d.get("bau")
        s.logik = d.get("logik")
        s._feldnr = d.get("feldnr")
        s.woche = s.monat = s.jahr = 0
        s.teams = [0] * 9
        return s

    def _id(self, art, i):
        idx = getattr(self, "_%s_idx" % art, None)
        return int(idx[i]) if idx is not None else int(i)

    # ----------------------------------------------------------------------------------------------- Geschosse (Punkt 2)
    def geschosse(self):
        """Alles, was fliegt oder gerade aufgeschlagen ist (Entity-Arten Pfeil, Bolzen, Stein, Balliste, Schleuder,
        Feuertopf, Kuh, Seuchenwolke). Ankunft = Rest-Mikroschritte / Mikroschritte je Takt (Flugformel)."""
        e = self.entities
        aus = []
        maske = np.isin(e["entityType"], list(GESCHOSSE)) & (e["logicalState"] > 0) & (e["logicalState"] < 3)
        for i in np.flatnonzero(maske):
            r = e[i]
            je_takt = abs(float(r["vCos"])) * float(r["_elapsedTimeOrGravityAccumulator"]) * FLUG_FAKTOR
            rest = int(r["field58_0x8c"]) - int(r["travelledDistance"])
            liegt = int(r["someCounter_OR_hitGround"]) != 0
            aus.append({
                "id": self._id("entities", i), "uid": int(r["uid"]), "entityType": int(r["entityType"]),
                "sre_art": ENTITY_TYPE.get(int(r["entityType"]), str(int(r["entityType"]))), "owner": int(r["owner"]),
                "logicalState": int(r["logicalState"]),
                "unitID_OR_seaGullID": int(r["unitID_OR_seaGullID"]),      # Schuetze (spawnProjectileEntity: unitID-Parameter)
                "unitID": int(r["unitID"]),                                # anvisierte Einheit (shootTargetedUnit), 0 = Feld/Gebaeude
                "field21_0x34": int(r["field21_0x34"]),                    # Abschuss-Takt (GameCore.mapTimeInTicks)
                "sre_flugtakte": int(self.takt_kern) - int(r["field21_0x34"]),
                "start": [int(r["x_2"]) // 8, int(r["y_2"]) // 8, int(r["startingHeight"])],
                "jetzt_mikro": [int(r["microX"]), int(r["microY"]), int(r["height"])],
                "jetzt_feld": [int(r["xPosition"]), int(r["yPosition"])], "tile": int(r["tile"]),
                "ziel_mikro": [int(r["targetX"]), int(r["targetY"]), int(r["targetZ"])],
                "ziel_feld": [int(r["targetX"]) // 8, int(r["targetY"]) // 8],
                "field58_0x8c": int(r["field58_0x8c"]), "travelledDistance": int(r["travelledDistance"]),
                "sre_rest_mikroschritte": rest, "sre_mikroschritte_je_takt": round(je_takt, 3),
                "sre_rest_takte": (int(math.ceil(rest / je_takt)) if je_takt > 0 and rest > 0 else 0),
                "velocityUnk": int(r["velocityUnk"]), "startingAngle": int(r["startingAngle"]),
                "vCos": round(float(r["vCos"]), 3), "vSin": round(float(r["vSin"]), 3), "speedUnk": round(float(r["speedUnk"]), 4),
                "sre_bahn": self._bahn(r),
                "field80_0xba": int(r["field80_0xba"]), "rng_2": int(r["rng_2"]),                 # rng_2 1 = Feuerpfeil, 2 = Pech-Zuender
                "field90_0xd0": int(r["field90_0xd0"]),                                           # 1 = Feuerballiste
                "someCounter_OR_hitGround": int(r["someCounter_OR_hitGround"]),
                "sre_zustand": "liegt" if liegt else "fliegt",
            })
        return aus

    def _bahn(self, r, max_takte=400):
        """Vorhersage je Takt ab jetzt: [takt_offset, mikroX, mikroY, hoehe, feld_x, feld_y, boden] bis der Pfeil unter die
        Bodenhoehe seines Feldes faellt (processEntityHitBuildingOrUnit: Aufschlag erst nach der halben Strecke; Treffer an
        einer Einheit, wenn hoehe in [Einheitenhoehe, +42]). Formeln aus moveProjectileEntity 0x004084A0:
        T = speedUnk - Zeitschritt (speedUnk wird erst NACH dem Schritt erhoeht), je Takt T += Zeitschritt,
        Strecke = 0,25 * vCos * T (Mikroschritte, Zaehlung wie travelledDistance), Hoehe = startingHeight + 2 * (vSin * T -
        4,906 * T^2). Gemessen 25.10. (Lauf 153231, 20 Pfeile, alle Stuetzstellen auf +-1 Mikroschritt/Hoehenpunkt).
        Pfeil, Bolzen, Balliste, Schleuder (Kurventyp 0/6, gemessen) und Steine/Kuh (Kurventyp 1/2: gleiche Bewegungsformel,
        Winkel aus Tabelle, Geschwindigkeit per computeVelocity - Landung sobald unter Bodenhoehe; UNGEMESSEN bis Katapult-Lauf)."""
        art = int(r["entityType"])
        if art not in (1, 7, 20, 33, 2, 3, 4, 23) or int(r["someCounter_OR_hitGround"]) != 0:
            return []
        stein = art in (2, 3, 4, 23)   # Katapult/Tribok/Mangonel/Kuh: Aufschlag sobald unter Bodenhoehe, ohne Halbstrecken-Regel
        dt = float(r["_elapsedTimeOrGravityAccumulator"])
        vcos, vsin = float(r["vCos"]), float(r["vSin"])
        if dt <= 0 or vcos == 0:
            return []
        sx, sy, sh = int(r["x_2"]), int(r["y_2"]), int(r["startingHeight"])
        tx, ty = int(r["targetX"]), int(r["targetY"])
        gesamt = max(int(r["field58_0x8c"]), 1)
        ex, ey = (tx - sx) / float(gesamt), (ty - sy) / float(gesamt)
        T = float(r["speedUnk"]) - dt
        aus = []
        for k in range(1, max_takte + 1):
            T += dt
            d = FLUG_FAKTOR * vcos * T
            h = sh + 2.0 * (vsin * T - GRAVITY_DIV_2 * T * T)
            mx, my = int(round(sx + ex * d)), int(round(sy + ey * d))
            fx, fy = mx // 8, my // 8
            boden = self._boden(fx, fy)
            aus.append([k, mx, my, int(round(h)), fx, fy, boden])
            if (boden is not None and h < boden and (stein or d > gesamt / 2.0)) or h < -50 or not (0 <= fx < 400 and 0 <= fy < 400):
                break
        return aus

    def _boden(self, fx, fy):
        if getattr(self, "hoehe", None) is None or not len(self.hoehe):
            return None
        if getattr(self, "_feldnr", None) is None:
            self._feldnr = feldnummern()
        if not (0 <= fx < 400 and 0 <= fy < 400):
            return None
        k = int(self._feldnr[fx, fy])
        if k < 0:
            return None
        h = int(self.hoehe[k])
        bau, logik = getattr(self, "bau", None), getattr(self, "logik", None)
        if bau is None or logik is None or not len(bau) or not len(logik):
            return h
        bid = int(bau[k])
        btyp = 0
        if bid:
            g = self.gebaeude
            idx = getattr(self, "_gebaeude_idx", None)
            if idx is not None:
                w = np.flatnonzero(idx == bid)
                if len(w):
                    btyp = int(g[w[0]]["buildingType"])
            elif bid < len(g):
                btyp = int(g[bid]["buildingType"])
        return boden_hoehe(h, int(logik[k]), btyp)

    def feuer(self):
        e = self.entities
        maske = (e["entityType"] == 9) & (e["logicalState"] > 0) & (e["logicalState"] < 3)
        return [{"id": self._id("entities", i), "tile": int(e[i]["tile"]), "feld": [int(e[i]["xPosition"]), int(e[i]["yPosition"])],
                 "owner": int(e[i]["owner"]), "fireIntensity": int(e[i]["fireIntensity"]),
                 "logicalState": int(e[i]["logicalState"])} for i in np.flatnonzero(maske)]

    # ----------------------------------------------------------------------------------------------- Einheiten (Punkt 1)
    def einheiten_liste(self, nur_spieler=None):
        u = self.einheiten
        maske = u["logicalState"] == 2
        if nur_spieler is not None:
            maske &= np.isin(u["owner"], list(nur_spieler))
        angst = {p: int(self.spieler[p]["fearFactorLevel"]) for p in range(SPIELER_ANZAHL)}
        aus = []
        for i in np.flatnonzero(maske):
            r = u[i]
            aus.append(self._einheit(self._id("einheiten", i), r, angst))
        return aus

    def _einheit(self, i, r, angst):
        zustand = int(r["state"])
        rest, schritte, schuss = phase_rest(int(r["unitType"]), zustand, int(r["animationCycleNumber"]))
        idx, n = int(r["currentIndexInPathPlan"]), int(r["totalSizeOfPathPlan"])
        rest_weg = self._wegpunkte(r, idx, n)
        return {
            "id": i, "uid": int(r["uid"]), "unitType": int(r["unitType"]), "owner": int(r["owner"]),
            "feld": [int(r["x"]), int(r["y"])], "tile": int(r["tile"]),
            "mikro": [int(r["microXPosition"]), int(r["microYPosition"])],
            "terrainOrClimbHeight": int(r["terrainOrClimbHeight"]), "buildingHeight": int(r["buildingHeight"]),
            "health": int(r["health"]), "maxHealth": int(r["maxHealth"]), "healthPercentage": int(r["healthPercentage"]),
            "dying": int(r["dying"]),
            # Phase
            "state": zustand, "sre_state_name": UNIT_STATE.get(zustand, str(zustand)), "substate": int(r["substate"]),
            "cachedState": int(r["cachedState"]), "state_2": int(r["state_2"]),
            "animationFrame": int(r["animationFrame"]), "animationTicker": int(r["animationTicker"]),
            "animationSpeed": int(r["animationSpeed"]), "animationCycleNumber": int(r["animationCycleNumber"]),
            "idle": int(r["idle"]), "idleCounterUnk": int(r["idleCounterUnk"]),
            "sre_phase_schritte": schritte, "sre_phase_rest_takte": rest,
            "sre_naechster_schuss_takte": (schuss if int(r["shootTargetedUnit"]) or zustand in (4, 5, 6) else None),
            # Zielwahl / Vorhalt
            "targetingType": int(r["targetingType"]), "sre_targeting_name": INSTRUCTION.get(int(r["targetingType"]), ""),
            "targetUID": int(r["targetUID"]), "shootTargetedUnit": int(r["shootTargetedUnit"]),
            "attackedUnitID": int(r["attackedUnitID"]),
            "targetedUnitID__OR__engineerMannedSiegeEngineRef": int(r["targetedUnitID__OR__engineerMannedSiegeEngineRef"]),
            "targetID_OR_targetBuildingID": int(r["targetID_OR_targetBuildingID"]),
            "targetedBuildingTile": int(r["targetedBuildingTile"]),
            "shootTarget_mikro": [int(r["shootTargetMicroX"]), int(r["shootTargetMicroY"]), int(r["shootTargetZ"])],
            "shootTarget_feld": [int(r["shootTargetMicroX"]) // 8, int(r["shootTargetMicroY"]) // 8],
            "attackAtTile": [int(r["attackAtTileX"]), int(r["attackAtTileY"])],
            "lookForEnemy": int(r["lookForEnemy"]), "enemyNoticeFrequencyUnk": int(r["enemyNoticeFrequencyUnk"]),
            # Sicht
            "closestEnemyMicroDistance": int(r["closestEnemyMicroDistance"]),
            "assassinsMicroDistanceToEnemyUnk": int(r["assassinsMicroDistanceToEnemyUnk"]),
            "isSelectable_OR_matchTime": int(r["isSelectable_OR_matchTime"]),
            # Treffer-Historie
            "attackedBy": int(r["attackedBy"]), "huntedBy": int(r["huntedBy"]),
            "lastEncounteredEnemyPlayerID": int(r["lastEncounteredEnemyPlayerID"]),
            "lastEncounteredEnemyUnitIDUnk": int(r["lastEncounteredEnemyUnitIDUnk"]),
            # Weg
            "destination": [int(r["destinationXPosition"]), int(r["destinationYPosition"])],
            "plannedDestination": [int(r["plannedDestinationX"]), int(r["plannedDestinationY"])],
            "currentIndexInPathPlan": idx, "totalSizeOfPathPlan": n, "sre_wegpunkte": rest_weg,
            "sre_restweg_felder": len(rest_weg),
            "wegplan_roh": (bytes(r["pathPlanStart"][idx // 2:(n + 1) // 2]).hex() if 0 <= idx < n <= 800 else ""),
            "wegplan_roh_ab": idx // 2, "moveDelay": int(r["moveDelay"]), "facingDirection": int(r["facingDirection"]),
            "movementSpeed": int(r["movementSpeed"]), "calculatedMovementSpeed": int(r["calculatedMovementSpeed"]),
            "stateBasedSpeed": int(r["stateBasedSpeed"]), "tunnelerFinishedDigging": int(r["tunnelerFinishedDigging"]),
            "climbDataID": int(r["climbDataID"]),
            # Sonstiges
            "sre_fearFactorLevel_owner": angst.get(int(r["owner"])), "tribeID": int(r["tribeID"]),
            "aiUnitBehaviourType": int(r["aiUnitBehaviourType"]), "siegeTargetPlayerID": int(r["siegeTargetPlayerID"]),
            "stoneAmmunition": int(r["stoneAmmunition"]), "nextAttackHurtsWall": int(r["nextAttackHurtsWall"]),
            "workplaceBuildingUID": int(r["workplaceBuildingUID"]), "buildingID": int(r["buildingID"]),
            "fixedRng": int(r["fixedRng"]), "nextUnitOnTheSameTile": int(r["nextUnitOnTheSameTile"]),
        }

    @staticmethod
    def _wegpunkte(r, idx, n):
        """pathPlanStart: 400 Byte, je Byte zwei Schritte: tiefes Halbbyte = gerader Index, hohes = ungerader; Wert 0-7 =
        Richtung N, NO, O, SO, S, SW, W, NW (wie facingDirection). Gemessen 25.10. (Lauf 152725, 2.082 Schritte: je
        Halbbyte 85-92 % die genannte Richtung, der Rest Neuplanungen zwischen zwei Schnappschuessen)."""
        if n <= 0 or idx < 0 or idx >= n or n > 800:
            return []
        plan = r["pathPlanStart"]
        x, y = int(r["x"]), int(r["y"])
        aus = []
        for k in range(idx, min(n, idx + 400)):
            b = int(plan[k // 2])
            d = (b & 0xF) if k % 2 == 0 else (b >> 4)
            dx, dy = RICHTUNG.get(d & 7, (0, 0))
            x, y = x + dx, y + dy
            aus.append([x, y])
        return aus

    # ------------------------------------------------------------------------------------------------- Gebaeude (Punkt 4)
    def gebaeude_liste(self, nur_spieler=None):
        g = self.gebaeude
        maske = g["logicalState"] == 2
        if nur_spieler is not None:
            maske &= np.isin(g["owner"], list(nur_spieler))
        aus = []
        for i in np.flatnonzero(maske):
            r = g[i]
            lager = {RT.get(k + 2, str(k + 2)): int(v) for k, v in enumerate(r["resources"]) if int(v)}   # 296 = resourceWood (RT 2) ... 384 = resourceIronArmor (RT 24)
            aus.append({
                "id": self._id("gebaeude", i), "uid": int(r["uid"]), "buildingType": int(r["buildingType"]), "owner": int(r["owner"]),
                "feld": [int(r["x"]), int(r["y"])], "currentHealth": int(r["currentHealth"]), "maxHealth": int(r["maxHealth"]),
                "state": int(r["state"]), "buildingProgress": int(r["buildingProgress"]), "timeAlive": int(r["timeAlive"]),
                "cooldownTimer": int(r["cooldownTimer"]), "fireDuration": int(r["fireDuration"]),
                "ifFireThenResponsiblePlayer": int(r["ifFireThenResponsiblePlayer"]),
                "buildingTypeBasedEmployeeCount": int(r["buildingTypeBasedEmployeeCount"]),
                "currentEmployeeCount": int(r["currentEmployeeCount"]),
                "currentlyNeededEmployeeCount": int(r["currentlyNeededEmployeeCount"]),
                "workerID": [int(w) for w in r["workerID"]], "lager": lager,
                "currentNumberOfResource": int(r["currentNumberOfResource"]),
                "currentLimitOfResource": int(r["currentLimitOfResource"]),
                "currentStoredResourceType": int(r["currentStoredResourceType"]), "producedItemType": int(r["producedItemType"]),
                "recruitTimer": int(r["recruitTimer"]), "gateState": int(r["gateState"]), "gateState2": int(r["gateState2"]),
                "gateCloseOpenTimer": int(r["gateCloseOpenTimer"]), "drawBridgeState1": int(r["drawBridgeState1"]),
                "drawbridgeState2": int(r["drawbridgeState2"]),
                "containsSiegeMangonel1OrBallista2": int(r["containsSiegeMangonel1OrBallista2"]),
                "insideUnitID": [int(w) for w in r["insideUnitID"]], "hasUnitsOntop": int(r["hasUnitsOntop"]),
            })
        return aus

    # -------------------------------------------------------------------------------------------------- Spieler (Punkt 5/6)
    def spieler_liste(self):
        aus = []
        lord_leben = {}
        u = self.einheiten
        for p in range(1, SPIELER_ANZAHL):
            r = self.spieler[p]
            lid = int(r["lordID"])
            if 0 < lid < len(u) and int(u[lid]["logicalState"]) == 2:
                lord_leben = {"id": lid, "health": int(u[lid]["health"]), "maxHealth": int(u[lid]["maxHealth"]),
                              "feld": [int(u[lid]["x"]), int(u[lid]["y"])]}
            else:
                lord_leben = {"id": lid}
            waren = {RT.get(k, str(k)): int(v) for k, v in enumerate(r["currentResources"]) if k in RT}
            ziele = [int(b) for b in r["top100TargetableBuildings"] if int(b)]
            aus.append({
                "spieler": p, "team": self.teams[p] if p < len(self.teams) else None, "aiType": int(r["aiType"]),
                "aivID": int(r["aivID"]), "gold": waren.get("GOLD"), "waren": waren,
                "popularity": int(r["popularity"]), "currentPopulation": int(r["currentPopulation"]),
                "populationCap": int(r["populationCap"]), "availablePeasantsAtFire": int(r["availablePeasantsAtFire"]),
                "idlePeasantsCount": int(r["idlePeasantsCount"]), "totalFood": int(r["totalFood"]),
                "foodTypesInStock": int(r["foodTypesInStock"]), "weeksWithoutFood": int(r["weeksWithoutFood"]),
                "rationsSetting": int(r["rationsSetting"]), "taxesSetting": int(r["taxesSetting"]),
                "fearFactorLevel": int(r["fearFactorLevel"]), "armySize": int(r["armySize"]),
                "soldaten": {"currentCrossbowmen": int(r["currentCrossbowmen"]), "currentSpearmen": int(r["currentSpearmen"]),
                             "currentPikemen": int(r["currentPikemen"]), "currentMacemen": int(r["currentMacemen"]),
                             "currentSwordsmen": int(r["currentSwordsmen"]), "countArabSwordsman": int(r["countArabSwordsman"]),
                             "countAssassinsAndArabianSwordsman": int(r["countAssassinsAndArabianSwordsman"])},
                "troopsLost": int(r["troopsLost"]), "troopsKilled": int(r["troopsKilled"]), "lord": lord_leben,
                "totalEnemyUnitsCount": int(r["totalEnemyUnitsCount"]),
                "ki": {
                    "aiPlayerState": int(r["aiPlayerState"]), "aiStateCounter": int(r["aiStateCounter"]),
                    "aiStrengthState": int(r["aiStrengthState"]), "aiStrengthFeeling": AI_STRENGTH.get(int(r["aiStrengthFeeling"]), int(r["aiStrengthFeeling"])),
                    "aiRecruitUnitChoiceState": AI_RECRUIT.get(int(r["aiRecruitUnitChoiceState"]), int(r["aiRecruitUnitChoiceState"])),
                    "aiRecruitIntervalTracker": int(r["aiRecruitIntervalTracker"]),
                    "attackedPlayerID": int(r["attackedPlayerID"]), "requestedAttackTargetUnk": int(r["requestedAttackTargetUnk"]),
                    "currentAttackWave": int(r["currentAttackWave"]), "attackTicker": int(r["attackTicker"]),
                    "attackAssaultDelayRelatedValue": int(r["attackAssaultDelayRelatedValue"]),
                    "aiCoordinatedAttackPatience": int(r["aiCoordinatedAttackPatience"]),
                    "currentAttackRaidParameter": int(r["currentAttackRaidParameter"]),
                    "currentWaveRandomAttackingStrength": int(r["currentWaveRandomAttackingStrength"]),
                    "totalAttackTroops": int(r["totalAttackTroops"]), "totalDefensiveTroopsUnk": int(r["totalDefensiveTroopsUnk"]),
                    "totalRaidingTroopsUnk": int(r["totalRaidingTroopsUnk"]), "totalUnitEngageTroops": int(r["totalUnitEngageTroops"]),
                    "totalUnitBackupTroops": int(r["totalUnitBackupTroops"]), "totalUnitPatrolTroops": int(r["totalUnitPatrolTroops"]),
                    "totalUnitSiegeDefTroops": int(r["totalUnitSiegeDefTroops"]), "totalAssassinTroops": int(r["totalAssassinTroops"]),
                    "totalLaddermenTroops": int(r["totalLaddermenTroops"]), "totalTunnelerTroops": int(r["totalTunnelerTroops"]),
                    "totalTroopValue": int(r["totalTroopValue"]), "totalEnemyTroopValue": int(r["totalEnemyTroopValue"]),
                    "totalEnemyRangedTroopValue": int(r["totalEnemyRangedTroopValue"]),
                    "totalEnemyTroopValueByPlayerID": [int(v) for v in r["totalEnemyTroopValueByPlayerID"]],
                    "isNotNervousByEnemyTroopValue": int(r["isNotNervousByEnemyTroopValue"]),
                    "relativeStrengthOfTeamComparedToEnemy": int(r["relativeStrengthOfTeamComparedToEnemy"]),
                    "closestEnemyDistanceToTheLord": int(r["closestEnemyDistanceToTheLord"]),
                    "top100TargetableBuildings": ziele[:20],
                    "aiTribeIDs": [int(t) for t in r["aiTribeIDs"] if int(t)],
                    "resourcesToAcquireArray_index_ungeprueft": {RT.get(k + 1, str(k + 1)): int(v) for k, v in enumerate(r["resourcesToAcquireArray"]) if int(v)},
                },
            })
        return aus

    # ---------------------------------------------------------------------------------------------------- Trupps (Punkt 6)
    def trupps_liste(self, nur_spieler=None):
        t = self.trupps
        if not len(t):
            return []
        maske = t["size"] > 0
        if nur_spieler is not None:
            maske &= np.isin(t["owner"], list(nur_spieler))
        aus = []
        for i in np.flatnonzero(maske):
            r = t[i]
            k = int(r["rallyPointCount"])
            aus.append({
                "id": self._id("trupps", i), "owner": int(r["owner"]), "tribeState": int(r["tribeState"]), "tribeType": int(r["tribeType"]),
                "sre_tribeType_name": TRIBE_TYPE.get(int(r["tribeType"]), ""), "tribeBehaviorType": int(r["tribeBehaviorType"]),
                "unitType": int(r["unitType"]), "size": int(r["size"]), "unitStance": STANCE.get(int(r["unitStance"]), int(r["unitStance"])),
                "target": [int(r["targetX"]), int(r["targetY"])], "targetBuildingID": int(r["targetBuildingID"]),
                "targetBuildingUID": int(r["targetBuildingUID"]), "targetPlayer_outpost": int(r["targetPlayer_outpost"]),
                "attackWave": int(r["attackWave"]), "countdown": int(r["countdown"]), "countdown2": int(r["countdown2"]),
                "isRallyingUnk": int(r["isRallyingUnk"]), "selectionTargetUnitID": int(r["selectionTargetUnitID"]),
                "rallyPoints": [[int(a), int(b)] for a, b in r["rallyPointArray"][:max(0, min(k, 9))]],
                "currentRallyPointIndex": int(r["currentRallyPointIndex"]),
            })
        return aus

    # ---------------------------------------------------------------------------------------------------- Felder (Punkt 3)
    def felder(self):
        """Je Feld, was Einheiten nicht sehen: Pechgraeben (Liste), Schadensebene, Feuer-Entities; Hoehe und Logik-Bits
        als Rohfelder (80.400) fuer numpy-Auswertung. Fallgruben: kein eigenes Feld gefunden - offen."""
        pech = [{"tile": int(p["tile"]), "feld": [int(p["x"]), int(p["y"])], "owner": int(p["owner"]), "state": int(p["state"])}
                for p in self.pech if int(p["tile"])]
        return {"pech": pech, "feuer": self.feuer(), "schaden_felder": int(np.count_nonzero(self.schaden)),
                "hoehe": self.hoehe, "logik": self.logik, "schaden": self.schaden}

    # --------------------------------------------------------------------------------------------------------- Ausgabe
    def kopf(self):
        return {"takt": int(self.takt), "takt_kern": int(self.takt_kern), "rein": bool(self.rein), "versuch": self.versuch,
                "dauer_ms": round(self.dauer_ms, 2), "datum": {"woche": self.woche, "monat": self.monat, "jahr": self.jahr},
                "anzahl": {"einheiten": int(np.count_nonzero(self.einheiten["logicalState"] == 2)),
                           "entities": int(len(self.entities)), "gebaeude": int(np.count_nonzero(self.gebaeude["logicalState"] == 2)),
                           "trupps": int(np.count_nonzero(self.trupps["size"] > 0)) if len(self.trupps) else 0}}

    def alles(self, teile=("geschosse", "einheiten", "gebaeude", "spieler", "trupps", "felder"), nur_spieler=None):
        aus = {"kopf": self.kopf()}
        if "geschosse" in teile:
            aus["geschosse"] = self.geschosse()
        if "einheiten" in teile:
            aus["einheiten"] = self.einheiten_liste(nur_spieler)
        if "gebaeude" in teile:
            aus["gebaeude"] = self.gebaeude_liste(nur_spieler)
        if "spieler" in teile:
            aus["spieler"] = self.spieler_liste()
        if "trupps" in teile:
            aus["trupps"] = self.trupps_liste(nur_spieler)
        if "felder" in teile:
            f = self.felder()
            aus["felder"] = {"pech": f["pech"], "feuer": f["feuer"], "schaden_felder": f["schaden_felder"]}
        return aus


class Protokoll(object):
    """SAI 25.10. 15:40: Schnappschuesse als Protokoll ablegen (Takt + Rohbloecke, gepackt), damit das Gehirn seine Vorhersage
    spaeter gegen echte Folgetakte pruefen kann, ohne dass das Spiel laeuft. Je Takt werden die Einheiten der gewaehlten
    Spieler, alle belegten Entity-Slots und die 9 Spielerdatensaetze als Rohbytes behalten; Hoehen-Ebene einmal.
    Datei: npz (zlib) mit zusammenhaengenden Strukturfeldern und Grenzen je Takt; `laden()` gibt die Schnappschuesse zurueck."""

    def __init__(self, spieler=None):
        self.spieler = spieler
        self.takte, self.kern, self.rein, self.dauer = [], [], [], []
        self.einheiten, self.einheiten_idx, self.entities, self.entities_idx, self.spieler_bloecke = [], [], [], [], []
        self.trupps, self.trupps_idx = [], []
        self.gebaeude, self.gebaeude_idx = [], []
        self.hoehe = None          # erste Hoehen-Ebene (Rueckwaertskompatibel)
        self.hoehen = []           # Hoehen-Ebene je Takt (Mauern fallen, Gebaeude brennen ab)
        self.bauten, self.logiken = [], []   # Gebaeude-/Logik-Ebene je Takt (Daecher = Aufschlaghoehe)
        self.feldnr = None

    def aufnehmen(self, s):
        d = s.behalten(self.spieler)
        self.takte.append(d["takt"]); self.kern.append(d["takt_kern"]); self.rein.append(d["rein"]); self.dauer.append(d["dauer_ms"])
        self.einheiten.append(d["einheiten"]); self.einheiten_idx.append(d["einheiten_idx"])
        self.entities.append(d["entities"]); self.entities_idx.append(d["entities_idx"])
        self.spieler_bloecke.append(d["spieler"])
        self.trupps.append(d.get("trupps", np.zeros(0, TRIBE))); self.trupps_idx.append(d.get("trupps_idx", np.zeros(0, np.int64)))
        self.gebaeude.append(d.get("gebaeude", np.zeros(0, BUILDING_PACKED))); self.gebaeude_idx.append(d.get("gebaeude_idx", np.zeros(0, np.int64)))
        if d.get("hoehe") is not None:
            self.hoehen.append(np.array(d["hoehe"]))
            if d.get("bau") is not None:
                self.bauten.append(np.array(d["bau"]))
            if d.get("logik") is not None:
                self.logiken.append(np.array(d["logik"]))
            if self.hoehe is None:
                self.hoehe = self.hoehen[0]
                self.feldnr = d.get("feldnr")

    def schreiben(self, pfad):
        def grenzen(liste):
            g = np.zeros(len(liste) + 1, np.int64)
            g[1:] = np.cumsum([len(x) for x in liste])
            return g
        np.savez_compressed(
            pfad, takt=np.array(self.takte, np.int64), takt_kern=np.array(self.kern, np.int64),
            rein=np.array(self.rein, bool), dauer_ms=np.array(self.dauer, np.float32),
            einheiten=np.concatenate(self.einheiten) if self.einheiten else np.zeros(0, UNIT),
            einheiten_idx=np.concatenate(self.einheiten_idx) if self.einheiten_idx else np.zeros(0, np.int64),
            einheiten_grenzen=grenzen(self.einheiten),
            entities=np.concatenate(self.entities) if self.entities else np.zeros(0, ENTITY),
            entities_idx=np.concatenate(self.entities_idx) if self.entities_idx else np.zeros(0, np.int64),
            entities_grenzen=grenzen(self.entities),
            spieler=np.stack(self.spieler_bloecke) if self.spieler_bloecke else np.zeros((0, SPIELER_ANZAHL), PLAYER),
            trupps=np.concatenate(self.trupps) if self.trupps else np.zeros(0, TRIBE),
            trupps_idx=np.concatenate(self.trupps_idx) if self.trupps_idx else np.zeros(0, np.int64),
            trupps_grenzen=grenzen(self.trupps),
            gebaeude=np.concatenate(self.gebaeude) if self.gebaeude else np.zeros(0, BUILDING_PACKED),
            gebaeude_idx=np.concatenate(self.gebaeude_idx) if self.gebaeude_idx else np.zeros(0, np.int64),
            gebaeude_grenzen=grenzen(self.gebaeude),
            hoehe=self.hoehe if self.hoehe is not None else np.zeros(0, np.uint8),
            feldnr=self.feldnr if self.feldnr is not None else np.zeros((0, 0), np.int32),
            hoehen=np.stack(self.hoehen) if len(self.hoehen) == len(self.takte) else np.zeros((0, 0), np.uint8),
            bauten=np.stack(self.bauten) if len(self.bauten) == len(self.takte) else np.zeros((0, 0), np.uint16),
            logiken=np.stack(self.logiken) if len(self.logiken) == len(self.takte) else np.zeros((0, 0), np.uint32),
            spieler_filter=np.array(self.spieler or [], np.int64))
        return pfad

    @staticmethod
    def laden(pfad):
        """[Schnappschuss, ...] aus einer Protokolldatei - ohne Spiel, mit allen Ableitungen (geschosse(), einheiten_liste() ...)."""
        with np.load(pfad, allow_pickle=False) as npz:
            z = {k: npz[k] for k in npz.files}     # jedes Feld EINMAL entpacken (npz[k] entpackt sonst bei jedem Zugriff neu)
        aus = []
        eg, gg = z["einheiten_grenzen"], z["entities_grenzen"]
        tg = z["trupps_grenzen"] if "trupps_grenzen" in z else None
        bg = z["gebaeude_grenzen"] if "gebaeude_grenzen" in z else None
        hoehe = z["hoehe"] if len(z["hoehe"]) else None
        feldnr = z["feldnr"] if ("feldnr" in z and z["feldnr"].size) else None
        hoehen = z["hoehen"] if ("hoehen" in z and z["hoehen"].size) else None
        bauten = z["bauten"] if ("bauten" in z and z["bauten"].size) else None
        logiken = z["logiken"] if ("logiken" in z and z["logiken"].size) else None
        for i, takt in enumerate(z["takt"]):
            if hoehen is not None:
                hoehe = hoehen[i]
            bau_i = bauten[i] if bauten is not None else None
            logik_i = logiken[i] if logiken is not None else None
            d = {"takt": int(takt), "takt_kern": int(z["takt_kern"][i]), "rein": bool(z["rein"][i]), "dauer_ms": float(z["dauer_ms"][i]),
                 "einheiten": z["einheiten"][eg[i]:eg[i + 1]], "einheiten_idx": z["einheiten_idx"][eg[i]:eg[i + 1]],
                 "entities": z["entities"][gg[i]:gg[i + 1]], "entities_idx": z["entities_idx"][gg[i]:gg[i + 1]],
                 "spieler": z["spieler"][i], "hoehe": hoehe, "feldnr": feldnr,
                 "trupps": z["trupps"][tg[i]:tg[i + 1]] if tg is not None else np.zeros(0, TRIBE),
                 "trupps_idx": z["trupps_idx"][tg[i]:tg[i + 1]] if tg is not None else np.zeros(0, np.int64),
                 "gebaeude": z["gebaeude"][bg[i]:bg[i + 1]] if bg is not None else np.zeros(0, BUILDING_PACKED),
                 "gebaeude_idx": z["gebaeude_idx"][bg[i]:bg[i + 1]] if bg is not None else np.zeros(0, np.int64),
                 "bau": bau_i, "logik": logik_i}
            aus.append(Schnappschuss.aus_behalten(d))
        return aus


def treffer(a, b):
    """Lebensverluste zwischen zwei aufeinanderfolgenden Schnappschuessen a -> b und ihre Quelle (SAI 25.10. 19:15).
    Je Einheit mit weniger health in b: Quelle 'geschoss' wenn in a ein Geschoss flog, das in b weg/eingeschlagen ist und
    (a) auf diese Einheit zielte (unitID) oder (b) zuletzt auf/neben ihrem Feld war; 'nahkampf' wenn in a/b ein Gegner im
    Zustand 106 (US_MELEE_ATTACK) mit attackedUnitID == Einheit anliegt (oder attackedBy der Einheit auf ihn zeigt);
    sonst 'unbekannt' (Feuer, Belagerungsgeraet-Stein ohne Ziel, Seuche ...). Mehrere Quellen moeglich -> Liste."""
    ua, ub = a.einheiten, b.einheiten
    ida, idb = a._einheiten_idx if a._einheiten_idx is not None else np.arange(len(ua)), b._einheiten_idx if b._einheiten_idx is not None else np.arange(len(ub))
    pos_a = {int(ua[i]["uid"]): i for i in range(len(ua)) if int(ua[i]["logicalState"]) == 2}
    # Geschosse, die in a flogen und in b nicht mehr fliegen (weg, Zustand 3/7 oder liegen)
    ea, eb = a.entities, b.entities
    flog = {int(ea[i]["uid"]): i for i in range(len(ea)) if int(ea[i]["entityType"]) in GESCHOSSE and int(ea[i]["logicalState"]) == 2 and int(ea[i]["someCounter_OR_hitGround"]) == 0}
    noch = {int(eb[i]["uid"]): i for i in range(len(eb)) if int(eb[i]["entityType"]) in GESCHOSSE and int(eb[i]["logicalState"]) == 2 and int(eb[i]["someCounter_OR_hitGround"]) == 0}
    eingeschlagen = [i for u, i in flog.items() if u not in noch]
    # Nahkaempfer in b (und a) im Zustand 106 mit Opfer
    def schlaeger(u, idx):
        aus = {}
        for i in range(len(u)):
            if int(u[i]["logicalState"]) == 2 and int(u[i]["state"]) == 106 and int(u[i]["attackedUnitID"]) > 0:
                aus.setdefault(int(u[i]["attackedUnitID"]), []).append((int(idx[i]), int(u[i]["uid"]), int(u[i]["unitType"]), int(u[i]["owner"]), int(u[i]["x"]), int(u[i]["y"])))
        return aus
    sb, sa = schlaeger(ub, idb), schlaeger(ua, ida)
    aus = []
    for j in range(len(ub)):
        r = ub[j]
        if int(r["logicalState"]) != 2:
            continue
        uid = int(r["uid"])
        i = pos_a.get(uid)
        if i is None:
            continue
        verlust = int(ua[i]["health"]) - int(r["health"])
        if verlust <= 0:
            continue
        nr, x, y, owner = int(idb[j]), int(r["x"]), int(r["y"]), int(r["owner"])
        quellen = []
        for k in eingeschlagen:
            g = ea[k]
            if int(g["owner"]) == owner:
                continue
            nah = max(abs(int(g["xPosition"]) - x), abs(int(g["yPosition"]) - y)) <= 1
            if int(g["unitID"]) == nr or nah:
                quellen.append({"quelle": "geschoss", "geschoss_uid": int(g["uid"]), "entityType": int(g["entityType"]),
                                "sre_art": ENTITY_TYPE.get(int(g["entityType"]), ""), "schuetze": int(g["unitID_OR_seaGullID"]),
                                "gezielt": int(g["unitID"]) == nr, "nah": nah})
        for liste in (sb.get(nr, []), sa.get(nr, [])):
            for (anr, auid, aut, aown, ax, ay) in liste:
                if aown != owner and max(abs(ax - x), abs(ay - y)) <= 2 and not any(q.get("angreifer") == anr for q in quellen):
                    quellen.append({"quelle": "nahkampf", "angreifer": anr, "angreifer_uid": auid, "angreifer_art": aut, "gezielt": True})
        # Nahkampf wirkt jeden Takt (P4): jeder Gegner im Zustand 106 bis 2 Felder (Mikro-Position an der Feldgrenze; gemessen
        # Lauf 191847: Angreifer stehen in x/y oft 2 Felder vom Opfer) ist ein Kandidat, auch ohne attackedUnitID
        for u, idx in ((ub, idb), (ua, ida)):
            m = (u["logicalState"] == 2) & (u["state"] == 106) & (u["owner"] != owner) & (np.abs(u["x"].astype(int) - x) <= 2) & (np.abs(u["y"].astype(int) - y) <= 2)
            for w in np.flatnonzero(m):
                anr = int(idx[w])
                if not any(q.get("angreifer") == anr for q in quellen):
                    quellen.append({"quelle": "nahkampf", "angreifer": anr, "angreifer_uid": int(u[w]["uid"]), "angreifer_art": int(u[w]["unitType"]), "gezielt": False,
                                    "abstand_mikro": int(max(abs(int(u[w]["microXPosition"]) - int(r["microXPosition"])), abs(int(u[w]["microYPosition"]) - int(r["microYPosition"]))))})
        ab = int(r["attackedBy"])
        if ab > 0 and not quellen and not any(q.get("angreifer") == ab for q in quellen):   # nur als Notnagel: attackedBy veraltet, wenn der Platz neu vergeben wurde
            # attackedBy (+942) nennt die Einheitennummer des letzten Angreifers - Art und uid aus b (sonst a) nachschlagen
            q = {"quelle": "attackedBy", "angreifer": ab}
            for u, idx in ((ub, idb), (ua, ida)):
                w = np.flatnonzero(idx == ab)
                if len(w):
                    q.update(angreifer_uid=int(u[w[0]]["uid"]), angreifer_art=int(u[w[0]]["unitType"]), angreifer_state=int(u[w[0]]["state"]),
                             angreifer_abstand=int(max(abs(int(u[w[0]]["x"]) - x), abs(int(u[w[0]]["y"]) - y))))
                    break
            quellen.append(q)
        aus.append({"takt": int(b.takt), "takt_vorher": int(a.takt), "id": nr, "uid": uid, "unitType": int(r["unitType"]), "owner": owner,
                    "feld": [x, y], "health": int(r["health"]), "verlust": verlust, "quellen": quellen or [{"quelle": "unbekannt"}]})
    return aus


def treffer_folge(schnappschuesse):
    aus = []
    for a, b in zip(schnappschuesse, schnappschuesse[1:]):
        aus.extend(treffer(a, b))
    return aus


class Taktring(object):
    """Leser fuer den Taktring des Moduls (werkzeug/engine_knowledge/taktring.lua): das Modul kopiert JEDEN Spieltakt
    Einheiten + Geschosse in einen Ring im Spielspeicher; hier werden die Plaetze gelesen, die seit dem letzten Mal neu sind -
    auch die Takte, die das Spiel innerhalb eines Bilds doppelt rechnet. Basisadresse aus ucp/villagestudio/taktring.txt."""

    MAGIC = 0x54414B54

    def __init__(self, spielordner=None):
        from befehl import SPIEL
        pfad = os.path.join(spielordner or SPIEL, "ucp", "villagestudio", "taktring.txt")
        self.basis = int(open(pfad).read().strip())
        kopf = struct.unpack("<5i", speicher.lies(self.basis, 20))
        if kopf[0] != self.MAGIC:
            raise RuntimeError("Taktring: Kennung fehlt bei 0x%X (%r)" % (self.basis, kopf))
        self.slots, self.slot, self.kopf = kopf[1], kopf[2], 32
        self.letzter_takt = None

    def _slot(self, i):
        roh = speicher.lies(self.basis + self.kopf + i * self.slot, self.slot)
        takt, takt_kern, max_units, max_geb = struct.unpack_from("<4i", roh, 0)
        n_u = min(max(max_units, 0), UNITS_MAX)
        u = np.frombuffer(roh, dtype=UNIT, count=n_u, offset=16)
        e = np.frombuffer(roh, dtype=ENTITY, count=ENTITIES_MAX, offset=16 + UNITS_MAX * UNIT_GROESSE)
        n_b = min(max(max_geb, 0), BUILDINGS_MAX)
        o = 16 + UNITS_MAX * UNIT_GROESSE + ENTITIES_MAX * ENTITY_GROESSE
        g = np.frombuffer(roh, dtype=BUILDING, count=n_b, offset=o) if n_b else np.zeros(0, BUILDING)
        o += BUILDINGS_MAX * BUILDING_GROESSE
        ebenen = None
        if len(roh) >= o + FELDER * 7:
            ebenen = (np.frombuffer(roh, dtype="u1", count=FELDER, offset=o).copy(),
                      np.frombuffer(roh, dtype="<u2", count=FELDER, offset=o + FELDER).copy(),
                      np.frombuffer(roh, dtype="<u4", count=FELDER, offset=o + FELDER * 3).copy())
        return takt, takt_kern, u, e, g, ebenen

    def neue(self, spieler=None):
        """[Schnappschuss, ...] aller Takte seit dem letzten Aufruf (aufsteigend); Spielerdaten/Hoehe aus dem Jetzt-Stand."""
        index, letzter = struct.unpack("<2i", speicher.lies(self.basis + 12, 8))
        if index < 0 or letzter == self.letzter_takt:
            return []
        jetzt = Schnappschuss(mit_trupps=False, mit_feldern="hoehe")
        aus = []
        for k in range(self.slots):
            i = (index - k) % self.slots
            takt, takt_kern, u, e, g, ebenen = self._slot(i)
            if takt <= 0 or (self.letzter_takt is not None and takt <= self.letzter_takt):
                break
            m = (u["logicalState"] == 2)
            if spieler is not None:
                m &= np.isin(u["owner"], list(spieler))
            me = e["logicalState"] != 0
            d = {"takt": takt, "takt_kern": takt_kern, "rein": True, "dauer_ms": 0.0,
                 "einheiten": u[m].copy(), "einheiten_idx": np.flatnonzero(m), "entities": e[me].copy(), "entities_idx": np.flatnonzero(me),
                 "spieler": jetzt.spieler.copy(), "hoehe": ebenen[0] if ebenen else jetzt.hoehe, "feldnr": feldnummern(), "trupps": np.zeros(0, TRIBE),
                 "bau": ebenen[1] if ebenen else getattr(jetzt, "bau", None), "logik": ebenen[2] if ebenen else getattr(jetzt, "logik", None),
                 "trupps_idx": np.zeros(0, np.int64)}
            mg = (g["logicalState"] == 2) if len(g) else np.zeros(0, bool)
            d["gebaeude"] = np.lib.recfunctions.repack_fields(g[mg]) if mg.any() else np.zeros(0, BUILDING_PACKED)
            d["gebaeude_idx"] = np.flatnonzero(mg)
            aus.append(Schnappschuss.aus_behalten(d))
        aus.reverse()
        if aus:
            self.letzter_takt = aus[-1].takt
        return aus


def protokollieren(sekunden, spieler=None, pfad=None, alle_ms=0.0, mit_trupps=False, alle_takte=1):
    """Sekunden lang jeden neuen Takt behalten (kein JSON unterwegs), dann als npz schreiben. Gibt (pfad, Protokoll) zurueck."""
    p = Protokoll(spieler)
    letzter, ende, hoehe_da = None, time.time() + sekunden, False
    ring = None
    if alle_takte == 1 and not mit_trupps:
        try:
            ring = Taktring()        # Modul-Ring vorhanden -> wirklich jeder Takt
        except Exception:  # noqa: BLE001
            ring = None
    while time.time() < ende:
        if ring is not None:
            for s in ring.neue(spieler):
                p.aufnehmen(s)
                letzter = s.takt
            time.sleep(0.002)
            continue
        s = Schnappschuss(mit_trupps=mit_trupps, mit_feldern="hoehe")
        if s.takt != letzter and (letzter is None or s.takt - letzter >= alle_takte):
            p.aufnehmen(s)
            letzter = s.takt
        if alle_ms > 0:
            time.sleep(alle_ms / 1000.0)
    if pfad is None:
        daten = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "daten")
        pfad = os.path.join(daten, "auge_protokoll_%s.npz" % time.strftime("%Y%m%d_%H%M%S"))
    return p.schreiben(pfad), p


def main():
    import argparse
    ap = argparse.ArgumentParser(description="B-251 Das Auge - Takt-Schnappschuss aus dem Spielspeicher (nur lesen)")
    ap.add_argument("--teile", default="geschosse,einheiten,gebaeude,spieler,trupps,felder")
    ap.add_argument("--spieler", default="", help="nur diese Besitzer, z. B. 1,2")
    ap.add_argument("--serie", type=float, default=0.0, help="Sekunden lang alle --alle ms einen Schnappschuss (JSONL)")
    ap.add_argument("--alle", type=float, default=50.0)
    ap.add_argument("--ziel", default="")
    ap.add_argument("--protokoll", type=float, default=0.0, help="Sekunden lang jeden Takt als Rohblock behalten -> npz (fuer das Gehirn)")
    ap.add_argument("--alle_takte", type=int, default=1, help="Protokoll: nur jeden n-ten Takt behalten (Langzeit)")
    ap.add_argument("--still", action="store_true")
    a = ap.parse_args()
    teile = tuple(a.teile.split(","))
    nur = [int(s) for s in a.spieler.split(",") if s.strip()] or None
    stempel = time.strftime("%Y%m%d_%H%M%S")
    daten = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "daten")
    if a.protokoll > 0:
        pfad, p = protokollieren(a.protokoll, nur, a.ziel or None, mit_trupps="trupps" in teile, alle_takte=a.alle_takte)
        print("OK: Protokoll %d Takte (%d..%d), %d unrein, Datei %.1f MB -> %s" % (
            len(p.takte), min(p.takte) if p.takte else 0, max(p.takte) if p.takte else 0, sum(1 for r in p.rein if not r),
            os.path.getsize(pfad) / 1e6, pfad))
        return 0
    if a.serie > 0:
        pfad = a.ziel or os.path.join(daten, "auge_serie_%s.jsonl" % stempel)
        ende = time.time() + a.serie
        n = 0
        letzter = None
        with open(pfad, "w", encoding="utf-8") as f:
            while time.time() < ende:
                s = Schnappschuss(mit_trupps="trupps" in teile, mit_feldern="felder" in teile)
                if s.takt != letzter:
                    f.write(json.dumps(s.alles(teile, nur), ensure_ascii=False) + "\n")
                    n += 1
                    letzter = s.takt
                time.sleep(a.alle / 1000.0)
        print("OK: %d Schnappschuesse -> %s" % (n, pfad))
        return 0
    s = Schnappschuss(mit_trupps="trupps" in teile, mit_feldern="felder" in teile)
    aus = s.alles(teile, nur)
    pfad = a.ziel or os.path.join(daten, "auge_%s.json" % stempel)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(aus, f, ensure_ascii=False, indent=1)
    if not a.still:
        print("OK: Takt %d (Kern %d), rein=%s, Versuch %d, %.1f ms; %s -> %s" % (
            s.takt, s.takt_kern, s.rein, s.versuch, s.dauer_ms, json.dumps(aus["kopf"]["anzahl"]), pfad))
        print("    Geschosse %d, Feuer %d, Pech %d" % (len(aus.get("geschosse", [])), len(aus.get("felder", {}).get("feuer", [])),
                                                       len(aus.get("felder", {}).get("pech", []))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
