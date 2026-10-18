// ================= _HoldStrong::Map::Buildings::BuildingsState::subtractPitchAndMoatFromStartingGoldInSiegeThatMode @ 0040c9f0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Buildings::BuildingsState::subtractPitchAndMoatFromStartingGoldInSiegeThatMode
          (BuildingsState *this)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  short *psVar4;
  int iVar5;
  int local_8;
  int local_4;
  
  if (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) {
    iVar5 = 0;
    psVar4 = &DAT_TileMapState.pitchDitches[2].owner;
    do {
      if (psVar4[-10] != 0) {
        iVar5 = iVar5 + 1;
      }
      if (*psVar4 != 0) {
        iVar5 = iVar5 + 1;
      }
      if (psVar4[10] != 0) {
        iVar5 = iVar5 + 1;
      }
      psVar4 = psVar4 + 0x1e;
    } while ((int)psVar4 < 0x1fe5b28);
    getBuildingCost(&DAT_BuildingsState,M_MAPPER_MOAT,&local_4,&local_8);
    iVar3 = DAT_TileMapState.moatTileCount;
    iVar2 = DAT_GameSynchronyState.currentPlayerSlotID;
    piVar1 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
             startResources + 0xf;
    *piVar1 = *piVar1 - (DAT_TileMapState.moatTileCount -
                        DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                        moatTileCount) * local_8;
    getBuildingCost(&DAT_BuildingsState,M_MAPPER_PITCH_DITCH,&local_4,&local_8);
    piVar1 = DAT_GameState.playerDataArray[iVar2].startResources + 0xf;
    *piVar1 = *piVar1 - (iVar5 - DAT_GameState.playerDataArray[iVar2].pitchDitchTileCount) * local_8
    ;
    DAT_GameState.playerDataArray[iVar2].pitchDitchTileCount = (short)iVar5;
    DAT_GameState.playerDataArray[iVar2].moatTileCount = (short)iVar3;
  }
  return;
}


// ================= _HoldStrong::Map::Buildings::BuildingsState::hasEnoughGoldForMoat @ 0040cac0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

uint __thiscall
_HoldStrong::Map::Buildings::BuildingsState::hasEnoughGoldForMoat(BuildingsState *this)

{
  int _pGold;
  int local_4;
  
  getBuildingCost(&DAT_BuildingsState,M_MAPPER_MOAT,&local_4,&_pGold);
  return (uint)(((DAT_TileMapState.moatTileCount -
                 DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                 moatTileCount) + 1) * _pGold <=
               DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
               startResources[0xf]);
}


// ================= _HoldStrong::Commands::ResyncMoat @ 0048aa80 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Commands::ResyncMoat(void)

{
  DAT_GameSynchronyState.DAT_GameCommandArray[DAT_GameSynchronyState.DAT_CurrentGameCommandID].time
       = 0;
  DAT_GameSynchronyState.DAT_CommandSize = 0x644;
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_SCHEDULE_AND_SEND) {
    DAT_GameSynchronyState.DAT_CommandActionPlan = GCS_EXECUTE;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,4,
               GCPL_FIXED_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,
               DAT_TileMapState.moats + DAT_GameSynchronyState.DAT_GameCommandParam0 * 100,0x640,
               GCPL_FIXED_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    return;
  }
  if ((DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_EXECUTE) &&
     (DAT_GameSynchronyState.isHost == FALSE)) {
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,4,
               GCPL_FIXED_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    Global::MemCopyFromParameter
              ((char *)(DAT_TileMapState.moats + DAT_GameSynchronyState.DAT_GameCommandParam0 * 100)
               ,0x640,DAT_GameSynchronyState.DAT_GameCommandParam0 * 100);
  }
  return;
}


// ================= _HoldStrong::Map::Navigation::PathFindingState::pathFindingToAttackCastleIncludingMoat @ 004a4140 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

bool __thiscall
_HoldStrong::Map::Navigation::PathFindingState::pathFindingToAttackCastleIncludingMoat
          (PathFindingState *this,undefined4 playerID,int wallOwnerPlayerID,uint x,uint y,
          byte *out_successUnk,int *out_x,int *out_y)

{
  short sVar1;
  short sVar2;
  short sVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int (*paiVar7) [8];
  short *psVar8;
  int playerID_00;
  
  DAT_PathFindingState.calculations = DAT_PathFindingState.calculations + 1;
  IO::LowLevelMemory::fillMemory_ByteValue
            (&DAT_LowLevelMemory,0x27420,'\0',DAT_TileMapState.CertainPathLayer);
  *out_y = 0;
  *out_x = 0;
  if (((x < 400) && (y < 400)) && (*(char *)(y * 400 + 0x21aec98 + x) != '\0')) {
    DAT_PathFindingState.searchGeneration = DAT_PathFindingState.searchGeneration + 1;
    if (32000 < DAT_PathFindingState.searchGeneration) {
      DAT_PathFindingState.searchGeneration = 1;
      IO::LowLevelMemory::fillMemory_ByteValue
                (&DAT_LowLevelMemory,0x27420,'\0',DAT_TileMapState.WalkLayer);
    }
    DAT_PathFindingState.searchQueue.readIndex = 0;
    DAT_PathFindingState.searchQueue.writeIndex = 1;
    DAT_PathFindingState.searchQueue.currentDistance = 1;
    DAT_PathFindingState.searchQueue.yQueue[0] = (short)y;
    DAT_PathFindingState.searchQueue.xQueue[0] = (short)x;
    DAT_PathFindingState.searchQueue.tilesQueue[0] =
         DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x;
    DAT_TileMapState.CertainPathLayer[DAT_PathFindingState.searchQueue.tilesQueue[0]] = 1;
    DAT_TileMapState.WalkLayer[DAT_PathFindingState.searchQueue.tilesQueue[0]] =
         (short)DAT_PathFindingState.searchGeneration;
    if (DAT_PathFindingState.searchQueue.readIndex != DAT_PathFindingState.searchQueue.writeIndex) {
      while ((iVar4 = DAT_PathFindingState.searchQueue.tilesQueue
                      [DAT_PathFindingState.searchQueue.readIndex], -1 < iVar4 && (iVar4 < 0x13a10))
            ) {
        sVar1 = DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.readIndex];
        sVar2 = DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.readIndex];
        if (((DAT_TileMapState.LogicLayer[iVar4] & 0x100U) != 0) &&
           (((DAT_TileMapState.LogicLayer[iVar4] & 2U) == 0 &&
            (wallOwnerPlayerID == (DAT_TileMapState.WallOwnerLayer[iVar4] & 7) + 1)))) {
          *out_successUnk = 1;
          *out_x = (int)sVar1;
          *out_y = (int)sVar2;
          return true;
        }
        DAT_PathFindingState.searchQueue.currentDistance =
             (int)DAT_TileMapState.CertainPathLayer[iVar4];
        psVar8 = &DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[0].short.yOffset;
                    /* Check all directions for movement */
        paiVar7 = DAT_TileMapState.directionTranslationMatrix + sVar2;
        do {
          playerID_00 = (*paiVar7)[0] + iVar4;
          uVar5 = DAT_TileMapState.LogicLayer[playerID_00];
          if (((((DAT_TileMapState.WalkLayer[playerID_00] != DAT_PathFindingState.searchGeneration)
                && ((uVar5 & 0x31) == 0)) &&
               (((uVar5 & 0x100000) == 0 || ((uVar5 & 0x200000) != 0)))) &&
              ((-1 < (char)uVar5 && ((uVar5 & 0x1000) == 0)))) &&
             ((DAT_TileMapState.BuildingLayer[playerID_00] == 0 ||
              ((int)(short)DAT_BuildingsState.buildings
                           [(short)DAT_TileMapState.BuildingLayer[playerID_00]].buildingType - 0x4aU
               < 3)))) {
            if ((uVar5 & 0x40000000) == 0) {
              DAT_TileMapState.CertainPathLayer[playerID_00] =
                   (short)DAT_PathFindingState.searchQueue.currentDistance + 1;
              sVar3 = ((Point8ShortXY *)(psVar8 + -2))->xOffset;
              DAT_TileMapState.WalkLayer[playerID_00] = (short)DAT_PathFindingState.searchGeneration
              ;
              DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                   sVar3 + sVar1;
              DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                   *psVar8 + sVar2;
              DAT_PathFindingState.searchQueue.tilesQueue
              [DAT_PathFindingState.searchQueue.writeIndex] = playerID_00;
              DAT_PathFindingState.searchQueue.writeIndex =
                   DAT_PathFindingState.searchQueue.writeIndex + 1;
              if (0x13a0f < DAT_PathFindingState.searchQueue.writeIndex) {
                DAT_PathFindingState.searchQueue.writeIndex = 0;
              }
            }
            else {
              iVar6 = Global::ReturnMoatIDForPlayerIDs(playerID_00,wallOwnerPlayerID);
              if (iVar6 != 0) {
                *out_successUnk = 0;
                sVar1 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[playerID_00];
                *out_y = (int)sVar1;
                *out_x = playerID_00 - DAT_ViewportRenderState.translationMatrix[sVar1].addXgetTile;
                return true;
              }
            }
          }
          psVar8 = psVar8 + 8;
          paiVar7 = (int (*) [8])(*paiVar7 + 2);
        } while ((int)psVar8 < 0xb4908c);
        DAT_PathFindingState.searchQueue.readIndex = DAT_PathFindingState.searchQueue.readIndex + 1;
        if (0x13a0f < DAT_PathFindingState.searchQueue.readIndex) {
          DAT_PathFindingState.searchQueue.readIndex = 0;
        }
        if (DAT_PathFindingState.searchQueue.readIndex ==
            DAT_PathFindingState.searchQueue.writeIndex) {
          return false;
        }
      }
    }
  }
  return false;
}


// ================= _HoldStrong::AI::AICState::aiAddUnitToMoatDiggerTribe @ 004cc840 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::AI::AICState::aiAddUnitToMoatDiggerTribe(AICState *this,int unitID)

{
  int iVar1;
  int tribeID;
  int playerID;
  
  playerID = (int)DAT_UnitsState.units[unitID].owner;
  DAT_UnitsState.units[unitID].aiUnitBehaviourType = 5;
  tribeID = (int)DAT_GameState.playerDataArray[playerID].aiTribeIDs[10];
  if ((tribeID == 0) ||
     (DAT_TribesState.tribes[tribeID].uid != DAT_GameState.playerDataArray[playerID].aiTribeUIDs[10]
     )) {
    tribeID = Map::Units::TribesState::createTribeForPlayer(&DAT_TribesState,playerID);
    iVar1 = DAT_TribesState.tribes[tribeID].uid;
    DAT_GameState.playerDataArray[playerID].aiTribeIDs[10] = (short)tribeID;
    DAT_GameState.playerDataArray[playerID].aiTribeUIDs[10] = iVar1;
  }
  Map::Units::TribesState::addUnitToTribe(&DAT_TribesState,unitID,tribeID);
  DAT_TribesState.tribes[tribeID].unitStance = USE_DEFENSIVE;
  return;
}


// ================= _HoldStrong::AI::AICState::digNearestMoat @ 004cd160 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::AI::AICState::digNearestMoat(AICState *this,int playerID)

{
  int iVar1;
  BOOLEnum tile;
  int tribeID;
  
  tribeID = (int)DAT_GameState.playerDataArray[playerID].aiTribeIDs[10];
  if ((((tribeID != 0) &&
       (DAT_TribesState.tribes[tribeID].uid ==
        DAT_GameState.playerDataArray[playerID].aiTribeUIDs[10])) &&
      (0 < DAT_TribesState.tribes[tribeID].size)) &&
     (DAT_TribesState.tribes[tribeID].percentageSomething < 0x51)) {
    iVar1 = Map::TileMapState::countUnfinishedMoatTilesForPlayer(&DAT_TileMapState,playerID);
    if (iVar1 < 1) {
      sendUnitsToKeep(&DAT_AICState,tribeID,playerID);
      return;
    }
    iVar1 = (int)DAT_TribesState.tribes[tribeID].selectionTargetUnitID;
    tile = Map::TileMapState::findNearestFriendlyMoatTileForDigging
                     (&DAT_TileMapState,playerID,iVar1,1);
    if (-1 < (int)tile) {
      Map::TileMapState::setXYBasedOnMoatID
                (&DAT_TileMapState,tile,1,(int)DAT_UnitsState.units[iVar1].x,
                 (int)DAT_UnitsState.units[iVar1].y);
      iVar1 = Map::Units::TribesState::updateTribeRallyFlags(&DAT_TribesState,tribeID);
      if (iVar1 == 0) {
        Map::Units::TribesState::giveTribeAnInstruction
                  (&DAT_TribesState,tribeID,UIT_DIG_MOAT,DAT_TileMapState.ALG_MoatXResult,
                   DAT_TileMapState.ALG_MoatYResult,0);
        DAT_TribesState.tribes[tribeID].unitStance = USE_STAND_GROUND;
      }
    }
  }
  return;
}


// ================= _HoldStrong::AI::AICState::hasNoTroopsOrAllAreDiggers @ 004cffd0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::AI::AICState::hasNoTroopsOrAllAreDiggers(AICState *this,int playerID)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_GameState.playerDataArray[playerID].totalUnitPatrolTroops +
          DAT_GameState.playerDataArray[playerID].totalUnit2Troops +
          DAT_GameState.playerDataArray[playerID].totalAssassinTroops;
  iVar3 = 0;
  if (DAT_GameState.playerDataArray[playerID].aiPlayerState == 6) {
    if (DAT_GameState.playerDataArray[playerID].attackTicker < 0x11) {
      iVar1 = DAT_GameState.playerDataArray[playerID].totalUnitBackupTroops;
    }
    else {
      iVar1 = DAT_GameState.playerDataArray[playerID].totalUnitBackupTroops;
      iVar1 = (int)(iVar1 + (iVar1 >> 0x1f & 7U)) >> 3;
    }
    iVar2 = iVar2 + DAT_GameState.playerDataArray[playerID].totalDiggingUnitTroops + iVar1 +
            DAT_GameState.playerDataArray[playerID].totalMaxDefaultTroops +
            DAT_GameState.playerDataArray[playerID].totalUnitSiegeDefTroops +
            DAT_GameState.playerDataArray[playerID].totalUnitEngageTroops;
  }
  else {
    iVar3 = DAT_GameState.playerDataArray[playerID].totalDiggingUnitTroops / 2;
    if (DAT_GameState.playerDataArray[playerID].attackTicker < 0xd) {
      iVar1 = DAT_GameState.playerDataArray[playerID].totalUnitBackupTroops;
    }
    else {
      iVar1 = DAT_GameState.playerDataArray[playerID].totalUnitBackupTroops;
      iVar1 = (int)(iVar1 + (iVar1 >> 0x1f & 7U)) >> 3;
    }
    iVar2 = iVar2 + iVar1 +
            DAT_GameState.playerDataArray[playerID].totalMaxDefaultTroops +
            DAT_GameState.playerDataArray[playerID].totalUnitSiegeDefTroops +
            DAT_GameState.playerDataArray[playerID].totalUnitEngageTroops;
  }
  if ((1 < iVar2) && ((4 < iVar2 || (iVar3 <= iVar2 * 2)))) {
    return FALSE;
  }
  return TRUE;
}


// ================= _HoldStrong::AI::AICState::aiAssignMoatDiggers @ 004d3f20 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::AI::AICState::aiAssignMoatDiggers(AICState *this,int playerID)

{
  UnitTypeShort UVar1;
  AITypeInt AVar2;
  UnitTypeShort *pUVar3;
  int unitID;
  
  AVar2 = DAT_GameState.playerDataArray[playerID].aiType;
  if (((AVar2 != AIT_NULL) && (0 < DAT_GameState.playerDataArray[playerID].totalTroopsType0)) &&
     (unitID = 1, 1 < (int)DAT_UnitsState.maxUnitCount)) {
    pUVar3 = &DAT_UnitsState.units[1].unitType;
    do {
      if ((((((pUVar3[-1] != ULS_INVISIBLE) && ((short)pUVar3[4] == playerID)) &&
            ((pUVar3[0x10b] != 0 && ((pUVar3[0x1ce] == 0 && (pUVar3[0x109] == 0)))))) &&
           (UVar1 = *pUVar3, UVar1 != UT_LORD)) &&
          ((((UVar1 != UT_E_ENGINEER && (UVar1 != UT_TUNNELER)) && (UVar1 != UT_S_CATAPULT)) &&
           ((UVar1 != UT_S_TREBUCHET && (UVar1 != UT_S_MANGONEL)))))) &&
         (((UVar1 != UT_S_TOWER && ((UVar1 != UT_S_BATTERINGRAM && (UVar1 != UT_S_SHIELD)))) &&
          ((UVar1 != UT_S_BALLISTA && (UVar1 != UT_S_FBALLISTA)))))) {
        if ((((*(int *)((int)&DAT_AICState + (AVar2 + ~AIT_NULL) * 0x2a4 + 0x15c) == 0) ||
             (UVar1 == UT_E_ARCHER)) || (UVar1 == UT_E_XBOW)) || (pUVar3[0x170] == 0)) {
          assignUnitToATribe(&DAT_AICState,unitID);
        }
        else {
          aiAddUnitToMoatDiggerTribe(&DAT_AICState,unitID);
        }
      }
      unitID = unitID + 1;
      pUVar3 = pUVar3 + 0x248;
    } while (unitID < (int)DAT_UnitsState.maxUnitCount);
  }
  return;
}


// ================= _HoldStrong::Map::TileMapState::recountTotalOwnedMoats @ 005000a0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Map::TileMapState::recountTotalOwnedMoats(void)

{
  int iVar1;
  byte *pbVar2;
  
  DAT_TileMapState.currentMoatCount = 0;
  iVar1 = 1;
  pbVar2 = &DAT_TileMapState.moats[1].owner;
  do {
    if (*pbVar2 != 0) {
      DAT_TileMapState.currentMoatCount = iVar1 + 1;
    }
    iVar1 = iVar1 + 1;
    pbVar2 = pbVar2 + 0x10;
  } while (iVar1 < 16000);
  return;
}


// ================= _HoldStrong::Map::TileMapState::countMoatsOwnedByEachPlayer @ 005000e0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Map::TileMapState::countMoatsOwnedByEachPlayer(TileMapState *this)

{
  int *piVar1;
  byte *pbVar2;
  int iVar3;
  
  DAT_GameState.playerDataArray[1].moatsOwned = 0;
  DAT_GameState.playerDataArray[2].moatsOwned = 0;
  DAT_GameState.playerDataArray[3].moatsOwned = 0;
  DAT_GameState.playerDataArray[4].moatsOwned = 0;
  DAT_GameState.playerDataArray[5].moatsOwned = 0;
  DAT_GameState.playerDataArray[6].moatsOwned = 0;
  DAT_GameState.playerDataArray[7].moatsOwned = 0;
  DAT_GameState.playerDataArray[8].moatsOwned = 0;
  pbVar2 = &DAT_TileMapState.moats[2].owner;
  iVar3 = 0x14d5;
  do {
    if (pbVar2[-0x10] != '\0') {
      piVar1 = &DAT_GameState.playerDataArray[(char)pbVar2[-0x10]].moatsOwned;
      *piVar1 = *piVar1 + 1;
    }
    if (*pbVar2 != 0) {
      piVar1 = &DAT_GameState.playerDataArray[(char)*pbVar2].moatsOwned;
      *piVar1 = *piVar1 + 1;
    }
    if (pbVar2[0x10] != '\0') {
      piVar1 = &DAT_GameState.playerDataArray[(char)pbVar2[0x10]].moatsOwned;
      *piVar1 = *piVar1 + 1;
    }
    pbVar2 = pbVar2 + 0x30;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  return;
}


// ================= _HoldStrong::Map::TileMapState::countUnfinishedMoatTilesForPlayer @ 00500180 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::TileMapState::countUnfinishedMoatTilesForPlayer(TileMapState *this,int playerID)

{
  int iVar1;
  byte *pbVar2;
  int iVar3;
  
  iVar1 = 0;
  pbVar2 = &DAT_TileMapState.moats[1].owner;
  iVar3 = 0x14d5;
  do {
    if (((*pbVar2 != 0) && ((char)*pbVar2 == playerID)) &&
       ((DAT_TileMapState.LogicLayer[*(int *)(pbVar2 + -0xc)] & 0x40000000U) == 0)) {
      iVar1 = iVar1 + 1;
    }
    if (((pbVar2[0x10] != '\0') && ((char)pbVar2[0x10] == playerID)) &&
       ((DAT_TileMapState.LogicLayer[*(int *)(pbVar2 + 4)] & 0x40000000U) == 0)) {
      iVar1 = iVar1 + 1;
    }
    if (((pbVar2[0x20] != '\0') && ((char)pbVar2[0x20] == playerID)) &&
       ((DAT_TileMapState.LogicLayer[*(int *)(pbVar2 + 0x14)] & 0x40000000U) == 0)) {
      iVar1 = iVar1 + 1;
    }
    pbVar2 = pbVar2 + 0x30;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  return iVar1;
}


// ================= _HoldStrong::Map::TileMapState::getUnownedMoatCount @ 00500210 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall _HoldStrong::Map::TileMapState::getUnownedMoatCount(TileMapState *this)

{
  int iVar1;
  byte *pbVar2;
  int iVar3;
  
  iVar1 = 0;
  pbVar2 = &DAT_TileMapState.moats[2].owner;
  iVar3 = 0x14d5;
  do {
    if (pbVar2[-0x10] == '\0') {
      iVar1 = iVar1 + 1;
    }
    if (*pbVar2 == 0) {
      iVar1 = iVar1 + 1;
    }
    if (pbVar2[0x10] == '\0') {
      iVar1 = iVar1 + 1;
    }
    pbVar2 = pbVar2 + 0x30;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  return iVar1;
}


// ================= _HoldStrong::Map::TileMapState::returnOwnedMoatAtTile @ 00500250 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::TileMapState::returnOwnedMoatAtTile(TileMapState *this,int targetedTile)

{
  Moat *pMVar1;
  int iVar2;
  
  iVar2 = 1;
  if (1 < DAT_TileMapState.currentMoatCount) {
    pMVar1 = DAT_TileMapState.moats;
    do {
      if ((pMVar1[1].owner != 0) && (*(int *)(pMVar1 + 1) == targetedTile)) {
        return iVar2;
      }
      iVar2 = iVar2 + 1;
      pMVar1 = pMVar1 + 1;
    } while (iVar2 < DAT_TileMapState.currentMoatCount);
  }
  return 0;
}


// ================= _HoldStrong::Global::ReturnMoatIDForPlayerIDs @ 00500290 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int _HoldStrong::Global::ReturnMoatIDForPlayerIDs(int playerID,int playerID2)

{
  int iVar1;
  byte *pbVar2;
  
  iVar1 = 1;
  if (1 < DAT_TileMapState.currentMoatCount) {
    pbVar2 = &DAT_TileMapState.moats[1].owner;
    do {
      if ((*(int *)(pbVar2 + -0xc) == playerID) && ((char)*pbVar2 == playerID2)) {
        return iVar1;
      }
      iVar1 = iVar1 + 1;
      pbVar2 = pbVar2 + 0x10;
    } while (iVar1 < DAT_TileMapState.currentMoatCount);
  }
  return 0;
}


// ================= _HoldStrong::Map::TileMapState::clearMoatData @ 005002d0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Map::TileMapState::clearMoatData(TileMapState *this,uint moatID)

{
  if (moatID < 16000) {
    IO::LowLevelMemory::fillMemory_ByteValue
              (&DAT_LowLevelMemory,0x10,'\0',DAT_TileMapState.moats + moatID);
    DAT_TileMapState.moatTileCount = DAT_TileMapState.moatTileCount + -1;
  }
  return;
}


// ================= _HoldStrong::Map::TileMapState::clearMoatDataAtTile @ 00500310 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Map::TileMapState::clearMoatDataAtTile(TileMapState *this,int x,int y)

{
  int iVar1;
  short *psVar2;
  
  iVar1 = 0;
  if (0 < DAT_TileMapState.currentMoatCount) {
    psVar2 = &DAT_TileMapState.moats[0].y;
    do {
      if ((psVar2[-1] == x) && (*psVar2 == y)) {
                    /* clear out moat (instruction?) */
        IO::LowLevelMemory::fillMemory_ByteValue(&DAT_LowLevelMemory,0x10,'\0',psVar2 + -3);
        DAT_TileMapState.moatTileCount = DAT_TileMapState.moatTileCount + -1;
      }
      iVar1 = iVar1 + 1;
      psVar2 = psVar2 + 8;
    } while (iVar1 < DAT_TileMapState.currentMoatCount);
  }
  return;
}


// ================= _HoldStrong::Map::TileMapState::setXYBasedOnMoatID @ 005003d0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::TileMapState::setXYBasedOnMoatID
          (TileMapState *this,int tile,int param_2,uint x,uint y)

{
  int iVar1;
  int iVar2;
  int (*paiVar3) [8];
  int iVar4;
  
  if (((x < 400) && (y < 400)) && (*(char *)(y * 400 + 0x21aec98 + x) != '\0')) {
    iVar1 = DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x;
    if (param_2 == 1) {
      DAT_TileMapState.ALG_MoatXResult = (int)(short)DAT_TileMapState.moats[tile].x;
      DAT_TileMapState.ALG_MoatYResult = (int)(short)DAT_TileMapState.moats[tile].y;
      return DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.ALG_MoatYResult].addXgetTile
             + DAT_TileMapState.ALG_MoatXResult;
    }
    if (param_2 == 2) {
      iVar4 = 0;
      paiVar3 = DAT_TileMapState.directionTranslationMatrix + (short)DAT_TileMapState.moats[tile].y;
      while ((iVar2 = (*paiVar3)[0] + *(int *)(DAT_TileMapState.moats + tile),
             DAT_TileMapState.HeightLayer[iVar1] + 0x10 < (uint)DAT_TileMapState.HeightLayer[iVar2]
             || (DAT_TileMapState.PathConnectionLayer[iVar2] !=
                 DAT_TileMapState.PathConnectionLayer[iVar1]))) {
        iVar4 = iVar4 + 1;
        paiVar3 = (int (*) [8])(*paiVar3 + 1);
        if (7 < iVar4) {
          return 0;
        }
      }
      DAT_TileMapState.someMoatTile = *(int *)(DAT_TileMapState.moats + tile);
      DAT_TileMapState.ALG_MoatXResult =
           (int)(short)DAT_TileMapState.moats[tile].x +
           DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[iVar4].int.xOffset;
      DAT_TileMapState.ALG_MoatYResult =
           (int)(short)DAT_TileMapState.moats[tile].y +
           *(int *)((int)DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix + iVar4 * 8 + 4);
      return iVar2;
    }
  }
  return 0;
}


// ================= _HoldStrong::Map::TileMapState::advanceMoatDigProgress @ 00500500 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::TileMapState::advanceMoatDigProgress(TileMapState *this,int moatID)

{
  Moat *pMVar1;
  byte *pbVar2;
  int iVar3;
  
  pbVar2 = &DAT_TileMapState.moats[moatID].fillProgress;
  *pbVar2 = *pbVar2 + 1;
  if ('\x03' < (char)DAT_TileMapState.moats[moatID].fillProgress) {
    pMVar1 = DAT_TileMapState.moats + moatID;
    iVar3 = *(int *)pMVar1;
    DAT_TileMapState.moats[moatID].someCountDown = 0;
    DAT_TileMapState.moats[moatID].fillProgress = 4;
    DAT_TileMapState.moats[moatID].stage = 2;
    DAT_TileMapState.HeightLayer[iVar3] = 0;
    DAT_TileMapState.LogicLayer[*(int *)pMVar1] =
         DAT_TileMapState.LogicLayer[*(int *)pMVar1] & 0xffffbfff;
    DAT_TileMapState.LogicLayer[*(int *)pMVar1] =
         DAT_TileMapState.LogicLayer[*(int *)pMVar1] & 0xfffffff7;
    DAT_TileMapState.LogicLayer[*(int *)pMVar1] =
         DAT_TileMapState.LogicLayer[*(int *)pMVar1] | 0x40000000;
                    /* fixme: why should undug moat not have any oasis anymore? */
    DAT_TileMapState.Logic2Layer[*(int *)pMVar1] = 0;
    Navigation::PathFindingState::updateWalkAndPathLayer
              (&DAT_PathFindingState,2,(int)(short)DAT_TileMapState.moats[moatID].x,
               (int)(short)DAT_TileMapState.moats[moatID].y);
    Navigation::PathFindingState::updatePathLinkagesInAllEightDirections
              (&DAT_PathFindingState,(int)(short)DAT_TileMapState.moats[moatID].y,*(int *)pMVar1);
    DAT_PathFindingState.toggleUpdateSeparateAreaTileMap = 1;
    UI::MinimapViewState::triggerMinimapRedraw(&DAT_MinimapViewState);
    return 1;
  }
  return 0;
}


// ================= _HoldStrong::Map::TileMapState::clearMoat @ 005005f0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Map::TileMapState::clearMoat(TileMapState *this,int tile)

{
  if ((DAT_TileMapState.LogicLayer[tile] & 0x4000U) != 0) {
    clearMoatDataAtTile(&DAT_TileMapState,
                        tile - DAT_ViewportRenderState.translationMatrix
                               [DAT_ViewportRenderState.tileTranslationMatrix_YComponent[tile]].
                               addXgetTile,
                        (int)DAT_ViewportRenderState.tileTranslationMatrix_YComponent[tile]);
    DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffbfff;
  }
  return;
}


// ================= _HoldStrong::Map::TileMapState::updateMoatCountdownTimers @ 00500640 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Map::TileMapState::updateMoatCountdownTimers(TileMapState *this)

{
  int extraout_ECX;
  char *pcVar1;
  int iVar2;
  
  recountTotalOwnedMoats();
  iVar2 = 0;
                    /* DAT_TotalOwnedMoats */
  if (0 < *(int *)(extraout_ECX + 0x53f070)) {
                    /* SEC_MoatArray[0].field11_0xf */
    pcVar1 = (char *)(extraout_ECX + 0x50087f);
    do {
      if ((pcVar1[-3] != '\0') && ('\0' < *pcVar1)) {
        *pcVar1 = *pcVar1 + -1;
      }
      iVar2 = iVar2 + 1;
      pcVar1 = pcVar1 + 0x10;
    } while (iVar2 < *(int *)(extraout_ECX + 0x53f070));
  }
  return;
}


// ================= _HoldStrong::Map::TileMapState::resetMoatArray @ 00500680 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Map::TileMapState::resetMoatArray(TileMapState *this)

{
  Moat *destination;
  int iVar1;
  
  destination = DAT_TileMapState.moats;
  iVar1 = 16000;
  do {
    IO::LowLevelMemory::fillMemory_ByteValue(&DAT_LowLevelMemory,0x10,'\0',destination);
    destination = destination + 1;
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  DAT_TileMapState.moatTileCount = iVar1;
  return;
}


// ================= _HoldStrong::Map::TileMapState::clearInvalidMoatEntries @ 005006c0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Map::TileMapState::clearInvalidMoatEntries(TileMapState *this)

{
  int iVar1;
  Moat *pMVar2;
  uint moatID;
  
  moatID = 1;
  if (1 < DAT_TileMapState.currentMoatCount) {
    pMVar2 = DAT_TileMapState.moats;
    do {
      if (((pMVar2[1].owner != 0) &&
          (iVar1 = *(int *)(pMVar2 + 1), (DAT_TileMapState.LogicLayer[iVar1] & 0x40004000U) == 0))
         && (DAT_TileMapState.BuildingLayer[iVar1] == 0)) {
        clearMoatData(&DAT_TileMapState,moatID);
      }
      moatID = moatID + 1;
      pMVar2 = pMVar2 + 1;
    } while ((int)moatID < DAT_TileMapState.currentMoatCount);
  }
  return;
}


// ================= _HoldStrong::Map::TileMapState::setMoatVisualStateAtTile @ 00500720 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::setMoatVisualStateAtTile
          (TileMapState *this,int tile,undefined4 zeroOrTwo)

{
  int iVar1;
  
  iVar1 = returnOwnedMoatAtTile(&DAT_TileMapState,tile);
  if (iVar1 != 0) {
    DAT_TileMapState.moats[iVar1].zeroOrTwo = (short)zeroOrTwo;
  }
  return;
}


// ================= _HoldStrong::Map::TileMapState::setMoatOwnerForAllMatching @ 00500750 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::setMoatOwnerForAllMatching
          (TileMapState *this,int param_1,undefined4 param_2)

{
  byte *pbVar1;
  int iVar2;
  
  pbVar1 = &DAT_TileMapState.moats[1].owner;
  iVar2 = 15999;
  do {
    if ((*pbVar1 != 0) && ((char)*pbVar1 == param_1)) {
      *pbVar1 = (byte)param_2;
    }
    pbVar1 = pbVar1 + 0x10;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}


// ================= _HoldStrong::Map::TileMapState::swapMoatOwnership @ 00500790 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::swapMoatOwnership(TileMapState *this,int param_1,int param_2)

{
  byte bVar1;
  byte *pbVar2;
  int iVar3;
  
  pbVar2 = &DAT_TileMapState.moats[1].owner;
  iVar3 = 15999;
  do {
    bVar1 = *pbVar2;
    if (bVar1 != 0) {
      if ((char)bVar1 == param_1) {
        *pbVar2 = (byte)param_2;
      }
      else if ((char)bVar1 == param_2) {
        *pbVar2 = (byte)param_1;
      }
    }
    pbVar2 = pbVar2 + 0x10;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  return;
}


// ================= _HoldStrong::Map::TileMapState::findNearestValidDigTileNearTarget @ 00500980 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::TileMapState::findNearestValidDigTileNearTarget
          (TileMapState *this,uint x1,uint y1,uint x2,uint y2)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int fromYPosition;
  int fromXPosition;
  uint local_10;
  int local_c;
  int local_8;
  
  if (((399 < x1) || (399 < y1)) || (*(char *)(y1 * 400 + 0x21aec98 + x1) == '\0')) {
    return 0;
  }
  if (((x2 < 400) && (y2 < 400)) && (*(char *)(y2 * 400 + 0x21aec98 + x2) != '\0')) {
    uVar1 = DAT_TileMapState.PathConnectionLayer
            [DAT_ViewportRenderState.translationMatrix[y1].addXgetTile + x1];
    iVar2 = DAT_ViewportRenderState.translationMatrix[y2].addXgetTile + x2;
    local_10 = (uint)DAT_TileMapState.HeightLayer[iVar2];
    local_c = 10000;
    local_8 = -1;
    if ((short)DAT_TileMapState.BuildingLayer[iVar2] != 0) {
      iVar2 = Buildings::BuildingsState::getBuildingHeightForBuildingID
                        ((int)(short)DAT_TileMapState.BuildingLayer[iVar2]);
      local_10 = local_10 + iVar2;
    }
    iVar2 = 0;
    do {
      fromXPosition = DAT_TerrainDefinedData.field2478_0x378c[iVar2].x + x2;
      fromYPosition = DAT_TerrainDefinedData.field2478_0x378c[iVar2].y + y2;
      iVar3 = DAT_ViewportRenderState.translationMatrix[fromYPosition].addXgetTile + fromXPosition;
      if (DAT_TileMapState.PathConnectionLayer[iVar3] == uVar1) {
        uVar4 = (uint)DAT_TileMapState.HeightLayer[iVar3];
        if ((short)DAT_TileMapState.BuildingLayer[iVar3] != 0) {
          iVar3 = Buildings::BuildingsState::getBuildingHeightForBuildingID
                            ((int)(short)DAT_TileMapState.BuildingLayer[iVar3]);
          uVar4 = uVar4 + iVar3;
        }
        if ((((int)uVar4 < (int)(local_10 + 0x10)) && ((int)(local_10 - 0x10) < (int)uVar4)) &&
           (Navigation::DirectionAlgorithmState::setAxisBasedDistanceResult
                      (&DAT_DirectionAlgorithmState,x1,y1,fromXPosition,fromYPosition),
           DAT_DirectionAlgorithmState.distanceHigh < local_c)) {
          local_c = DAT_DirectionAlgorithmState.distanceHigh;
          local_8 = iVar2;
        }
      }
      iVar2 = iVar2 + 1;
    } while (iVar2 < 4);
    if ((uint)local_8 < 0x80000000) {
      DAT_TileMapState.field155_0x5549a8 = DAT_TerrainDefinedData.field2478_0x378c[local_8].x + x2;
      DAT_TileMapState.field156_0x5549ac = DAT_TerrainDefinedData.field2478_0x378c[local_8].y + y2;
      return 1;
    }
    DAT_TileMapState.field155_0x5549a8 = x2;
    DAT_TileMapState.field156_0x5549ac = y2;
  }
  return 0;
}


// ================= _HoldStrong::Map::TileMapState::resetTileAndClearMoat @ 00507350 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Map::TileMapState::resetTileAndClearMoat(TileMapState *this,int tile)

{
  short sVar1;
  int iVar2;
  int iVar3;
  
  sVar1 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[tile];
  iVar2 = DAT_ViewportRenderState.translationMatrix[sVar1].addXgetTile;
  DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffbef4f7;
  DAT_TileMapState.HeightLayer[tile] = DAT_TileMapState.DefaultHeightLayer[tile];
  DAT_TileMapState.DamageLayer[tile] = 0;
  if (((DAT_TileMapState.LogicLayer[tile] & 0x1000U) != 0) &&
     (iVar3 = (int)(short)DAT_TileMapState.OrganismLayer[tile], iVar3 < 2000)) {
    switch(DAT_LandscapeState.trees[iVar3].treeType) {
    case 5:
    case 6:
    case 7:
    case 8:
    case 9:
    case 10:
    case 0xb:
    case 0xc:
    case 0xd:
    case 0xe:
    case 0x10:
    case 0x11:
    case 0x12:
    case 0x13:
      DAT_LandscapeState.trees[iVar3].state = 3;
    }
  }
  if ((DAT_TileMapState.LogicLayer[tile] & 0x40004000U) != 0) {
    clearMoatDataAtTile(&DAT_TileMapState,tile - iVar2,(int)sVar1);
    DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xbfffbfff;
  }
  DAT_TileMapState.MiscDisplayLayer[tile] = DAT_TileMapState.MiscDisplayLayer[tile] & 0xfc3f;
  return;
}


// ================= _HoldStrong::Map::TileMapState::clearSizeFiveBuildingFootprintAndMoats @ 00508760 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::clearSizeFiveBuildingFootprintAndMoats
          (TileMapState *this,int param_1,int param_2)

{
  ushort uVar1;
  short sVar2;
  uint moatID;
  TileMapState *this_00;
  int iVar3;
  int targetedTile;
  
  iVar3 = 0;
  do {
    getBuildingSizeIndexMappingData(iVar3,5);
    targetedTile = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + param_2].
                   addXgetTile + DAT_TileMapState.buildingX + param_1;
    uVar1 = DAT_TileMapState.BuildingLayer[targetedTile];
    sVar2 = DAT_BuildingsState.buildings[(short)uVar1].buildingVariation;
    DAT_TileMapState.LogicLayer[targetedTile] =
         DAT_TileMapState.LogicLayer[targetedTile] & 0xfffffbff;
    if (DAT_TerrainDefinedData.DrawbridgeOrientationMapping[(int)sVar2 / 2][iVar3] != 0) {
      moatID = returnOwnedMoatAtTile(this_00,targetedTile);
      if (moatID != 0) {
        if (DAT_BuildingsState.buildings[(short)uVar1].noRubble == 0) {
          clearMoatData(&DAT_TileMapState,moatID);
          DAT_TileMapState.LogicLayer[targetedTile] =
               DAT_TileMapState.LogicLayer[targetedTile] & 0xbfffffff;
          DAT_TileMapState.Logic2Layer[targetedTile] =
               DAT_TileMapState.Logic2Layer[targetedTile] | 2;
          DAT_TileMapState.BuildingWasLayer[targetedTile] = '\0';
          DAT_TileMapState.HeightLayer[targetedTile] = 8;
        }
        else {
          DAT_TileMapState.LogicLayer[targetedTile] =
               DAT_TileMapState.LogicLayer[targetedTile] | 0x40000000;
        }
      }
    }
    if ((DAT_TileMapState.LogicLayer[targetedTile] & 0x40000000U) == 0) {
      DAT_TileMapState.Logic2Layer[targetedTile] = DAT_TileMapState.Logic2Layer[targetedTile] | 2;
      DAT_TileMapState.BuildingWasLayer[targetedTile] = '\0';
    }
    DAT_TileMapState.BuildingLayer[targetedTile] = 0;
    iVar3 = iVar3 + 1;
    DAT_TileMapState.ChangedLayer[targetedTile] = 2;
  } while (iVar3 < DAT_TileMapState.constructionTileCount);
  return;
}


// ================= _HoldStrong::Map::TileMapState::floodMoatUnderRemovedBuilding @ 00508910 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::floodMoatUnderRemovedBuilding(TileMapState *this,int param_1)

{
  uint uVar1;
  int iVar2;
  uint xPosition;
  TileMapState *this_00;
  uint yPosition;
  int (*paiVar3) [25];
  int iVar4;
  int targetedTile;
  
  yPosition = (uint)(short)DAT_BuildingsState.buildings[param_1].y;
  xPosition = (uint)(short)DAT_BuildingsState.buildings[param_1].x;
  uVar1 = DAT_BuildingsState.buildings[param_1].widthOrHeight;
  iVar4 = 0;
  paiVar3 = DAT_TerrainDefinedData.DrawbridgeOrientationMapping +
            (int)DAT_BuildingsState.buildings[param_1].buildingVariation / 2;
  do {
    getBuildingSizeIndexMappingData(iVar4,5);
    targetedTile = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + yPosition]
                   .addXgetTile + DAT_TileMapState.buildingX + xPosition;
    if ((*paiVar3)[0] != 0) {
      iVar2 = returnOwnedMoatAtTile(this_00,targetedTile);
      if (iVar2 != 0) {
        DAT_TileMapState.LogicLayer[targetedTile] =
             DAT_TileMapState.LogicLayer[targetedTile] | 0x40000000;
        setMoatVisualStateAtTile(&DAT_TileMapState,targetedTile,2);
      }
    }
    iVar4 = iVar4 + 1;
    paiVar3 = (int (*) [25])(*paiVar3 + 1);
  } while (iVar4 < DAT_TileMapState.constructionTileCount);
  updateBuildingGraphicsLayer(&DAT_TileMapState,param_1);
  updatePathLinkagesForBuilding(&DAT_TileMapState,param_1);
  Navigation::PathFindingState::updateWalkAndPathLayer
            (&DAT_PathFindingState,uVar1 + 6,xPosition,yPosition);
  DAT_PathFindingState.toggleUpdateSeparateAreaTileMap = 1;
  return;
}


// ================= _HoldStrong::Map::TileMapState::createMoatData @ 005110b0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::TileMapState::createMoatData
          (TileMapState *this,undefined4 playerID,uint x,uint y,int filled)

{
  int iVar1;
  uint uVar2;
  byte *pbVar3;
  
  if (((399 < x) || (399 < y)) || (*(char *)(y * 400 + 0x21aec98 + x) == '\0')) {
    return 0;
  }
  iVar1 = returnOwnedMoatAtTile
                    (&DAT_TileMapState,DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x)
  ;
  if (iVar1 != 0) {
    return iVar1;
  }
  if ((DAT_GameCore.gameMode_2 != GM_SIEGE_THAT) ||
     (uVar2 = Buildings::BuildingsState::hasEnoughGoldForMoat(&DAT_BuildingsState), uVar2 != 0)) {
    iVar1 = 1;
    pbVar3 = &DAT_TileMapState.moats[1].owner;
    do {
      if (*pbVar3 == 0) {
        if (DAT_TileMapState.currentMoatCount <= iVar1) {
          DAT_TileMapState.currentMoatCount = iVar1 + 1;
        }
        DAT_TileMapState.moats[iVar1].owner = (byte)playerID;
        DAT_TileMapState.moats[iVar1].x = (short)x;
        DAT_TileMapState.moats[iVar1].y = (short)y;
                    /* tile */
        *(uint *)(DAT_TileMapState.moats + iVar1) =
             DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x;
        DAT_TileMapState.moats[iVar1].zeroOrTwo = 2;
        if (filled == 0) {
          DAT_TileMapState.moats[iVar1].stage = 1;
          DAT_TileMapState.moats[iVar1].fillProgress = 0;
          DAT_TileMapState.moatTileCount = DAT_TileMapState.moatTileCount + 1;
          return iVar1;
        }
        DAT_TileMapState.moats[iVar1].stage = 2;
        DAT_TileMapState.moats[iVar1].fillProgress = 4;
        DAT_TileMapState.moatTileCount = DAT_TileMapState.moatTileCount + 1;
        return iVar1;
      }
      iVar1 = iVar1 + 1;
      pbVar3 = pbVar3 + 0x10;
    } while (iVar1 < 16000);
  }
  return 0;
}


// ================= _HoldStrong::Map::TileMapState::findNearestFriendlyMoatTileForDigging @ 005111d0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::TileMapState::findNearestFriendlyMoatTileForDigging
          (TileMapState *this,int playerID,int unitID,int number)

{
  byte *pbVar1;
  byte bVar2;
  ushort uVar3;
  short sVar4;
  int iVar5;
  BOOLEnum BVar6;
  int iVar7;
  int iVar8;
  int destinationYPosition;
  int destinationXPosition;
  Moat *pMVar9;
  int _minimumValue;
  BOOLEnum _minimumValueMoatID;
  
  iVar5 = unitID;
  destinationXPosition = (int)DAT_UnitsState.units[unitID].x;
  destinationYPosition = (int)DAT_UnitsState.units[unitID].y;
  uVar3 = DAT_TileMapState.PathConnectionLayer
          [DAT_ViewportRenderState.translationMatrix[destinationYPosition].addXgetTile +
           destinationXPosition];
  _minimumValue = 1000;
  _minimumValueMoatID = ~FALSE;
  unitID = 0;
  BVar6 = ~FALSE;
  if (0 < DAT_TileMapState.currentMoatCount) {
    pMVar9 = DAT_TileMapState.moats;
    do {
      if (number == 1) {
        if (DAT_GameState.mapAndTime.playerTeams[(char)pMVar9->owner] ==
            DAT_GameState.mapAndTime.playerTeams[playerID]) {
LAB_00511287:
                    /* fixme */
          if ((((char)pMVar9->stage == number) &&
              (((iVar8 = *(int *)pMVar9, DAT_TileMapState.BuildingLayer[iVar8] == 0 ||
                (pMVar9->zeroOrTwo != 0)) &&
               ((DAT_TileMapState.LogicLayer[iVar8] & 0x40004000U) != 0)))) &&
             (((char)pMVar9->someCountDown < 'd' &&
              (((DAT_TileMapState.UnitLayer[iVar8] == 0 ||
                (DAT_UnitsState.units[(short)DAT_TileMapState.UnitLayer[iVar8]].someUnitStat4 != 0))
               && ((number != 2 ||
                   (BVar6 = findTileInSameAreaAndNoTooHeightDifference
                                      (&DAT_TileMapState,(int)(short)uVar3,iVar8,
                                       (int)(short)pMVar9->y), BVar6 != FALSE)))))))) {
            bVar2 = *(byte *)((char)pMVar9->owner * 0x13a10 + 0x1ee2998 + iVar8);
            Navigation::DirectionAlgorithmState::setAxisBasedDistanceResult
                      (&DAT_DirectionAlgorithmState,destinationXPosition,destinationYPosition,
                       (int)(short)pMVar9->x,(int)(short)pMVar9->y);
            iVar8 = DAT_DirectionAlgorithmState.distanceHigh;
            sVar4 = DAT_UnitsState.units[iVar5].targetX;
            if (sVar4 < 1) {
              iVar7 = 0;
            }
            else {
              iVar7 = Navigation::DirectionAlgorithmState::setAxisBasedDistanceResult
                                (&DAT_DirectionAlgorithmState,(int)sVar4,
                                 (int)DAT_UnitsState.units[iVar5].targetY,(int)(short)pMVar9->x,
                                 (int)(short)pMVar9->y);
            }
            if (DAT_GameSynchronyState.currentPlayerFullIDArray[playerID] == -1) {
              iVar8 = iVar8 + (uint)bVar2 * 10;
            }
            iVar8 = iVar7 / 2 + (char)pMVar9->someCountDown + iVar8;
            if (iVar8 < _minimumValue) {
              _minimumValueMoatID = unitID;
              _minimumValue = iVar8;
            }
          }
        }
      }
      else if ((number != 2) ||
              (DAT_GameState.mapAndTime.playerTeams[(char)pMVar9->owner] !=
               DAT_GameState.mapAndTime.playerTeams[playerID])) goto LAB_00511287;
      unitID = unitID + 1;
      pMVar9 = pMVar9 + 1;
    } while (unitID < DAT_TileMapState.currentMoatCount);
    BVar6 = _minimumValueMoatID;
    if (_minimumValueMoatID == FALSE) {
      return FALSE;
    }
  }
  pbVar1 = &DAT_TileMapState.moats[BVar6].someCountDown;
  *pbVar1 = *pbVar1 + 0x14;
  return BVar6;
}


// ================= _HoldStrong::Map::TileMapState::removeMoat @ 005113f0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall _HoldStrong::Map::TileMapState::removeMoat(TileMapState *this,uint moatID)

{
  Moat *pMVar1;
  byte *pbVar2;
  int iVar3;
  
  pbVar2 = &DAT_TileMapState.moats[moatID].fillProgress;
  *pbVar2 = *pbVar2 - 1;
  if ((char)DAT_TileMapState.moats[moatID].fillProgress < '\x01') {
    pMVar1 = DAT_TileMapState.moats + moatID;
    DAT_TileMapState.HeightLayer[*(int *)(DAT_TileMapState.moats + moatID)] = 8;
    DAT_TileMapState.LogicLayer[*(int *)pMVar1] =
         DAT_TileMapState.LogicLayer[*(int *)pMVar1] & 0xbfffffff;
    Navigation::PathFindingState::updateWalkAndPathLayer
              (&DAT_PathFindingState,2,(int)(short)DAT_TileMapState.moats[moatID].x,
               (int)(short)DAT_TileMapState.moats[moatID].y);
    Navigation::PathFindingState::updatePathLinkagesInAllEightDirections
              (&DAT_PathFindingState,(int)(short)DAT_TileMapState.moats[moatID].y,*(int *)pMVar1);
    DAT_PathFindingState.toggleUpdateSeparateAreaTileMap = 1;
    iVar3 = *(int *)pMVar1;
    clearMoatData(&DAT_TileMapState,moatID);
    if (DAT_TileMapState.BuildingLayer[iVar3] != 0) {
      updateBuildingGraphicsLayer
                (&DAT_TileMapState,(int)(short)DAT_TileMapState.BuildingLayer[iVar3]);
    }
    UI::MinimapViewState::triggerMinimapRedraw(&DAT_MinimapViewState);
    return 1;
  }
  return 0;
}


// ================= _HoldStrong::Map::TileMapState::planMoat @ 00514480 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::planMoat(TileMapState *this,undefined4 playerID,int tile,uint tileY)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = DAT_TileMapState.LogicLayer[tile];
  if ((((((uVar1 & 0x30) == 0) && (DAT_TileMapState.OrganismLayer[tile] == 0)) &&
       ((uVar1 & 0x10000400) == 0)) &&
      ((DAT_TileMapState.BuildingLayer[tile] == 0 && ((uVar1 & 0x203a0100) == 0)))) &&
     (((uVar1 & 0x85) == 0 &&
      (((uVar1 & 0x40004000) == 0 && (DAT_TileMapState.HeightLayer[tile] < 0xd)))))) {
    iVar2 = createMoatData(&DAT_TileMapState,playerID,
                           tile - DAT_ViewportRenderState.translationMatrix[tileY].addXgetTile,tileY
                           ,0);
    if (iVar2 != 0) {
      DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] | 0x4000;
    }
    Navigation::PathFindingState::updatePathLinkagesInAllEightDirections
              (&DAT_PathFindingState,tileY,tile);
  }
  return;
}


// ================= _HoldStrong::Map::Units::TroopValueState::setMoat3 @ 0051a720 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::TroopValueState::setMoat3
          (TroopValueState *this,int checkAgainstNonZero,int playerID)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  
  iVar3 = playerID * 0x177bc;
  iVar5 = 0;
  iVar2 = *(int *)((int)DAT_TroopValueState.attackInfo.moatValuesArray + iVar3 + -8);
  *(undefined4 *)((int)DAT_TroopValueState.attackInfo.moatValuesArray + iVar3 + -4) = 0;
  if (0 < iVar2) {
    piVar4 = (int *)((int)DAT_TroopValueState.attackInfo.moatValuesArray + iVar3 + 0xc);
    do {
      if ((piVar4[-1] < 5999) && ((*piVar4 == 0 || (checkAgainstNonZero != 0)))) {
        piVar1 = (int *)((int)DAT_TroopValueState.attackInfo.moatValuesArray + iVar3 + -4);
        *piVar1 = *piVar1 + 1;
      }
      iVar5 = iVar5 + 1;
      piVar4 = piVar4 + 4;
    } while (iVar5 < *(int *)((int)DAT_TroopValueState.attackInfo.moatValuesArray + iVar3 + -8));
  }
  return;
}


// ================= _HoldStrong::Map::Units::TroopValueState::calculateTile2MoatValueClosestToUnit @ 0051a780 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Units::TroopValueState::calculateTile2MoatValueClosestToUnit
          (TroopValueState *this,int unitID)

{
  int iVar1;
  int fromXPosition;
  int fromYPosition;
  int *piVar2;
  int local_14;
  int local_10;
  int local_8;
  
  iVar1 = DAT_UnitsState.units[unitID].owner * 0x177bc;
  local_10 = 100000;
  local_8 = -1;
  local_14 = 0;
  if (0 < *(int *)((int)DAT_TroopValueState.attackInfo.moatValuesArray + iVar1 + -8)) {
    piVar2 = (int *)((int)DAT_TroopValueState.attackInfo.moatValuesArray + iVar1 + 4);
    do {
      if ((piVar2[1] < 5999) && (piVar2[2] == 0)) {
        fromYPosition = (int)DAT_ViewportRenderState.tileTranslationMatrix_YComponent[*piVar2];
        fromXPosition =
             *piVar2 - DAT_ViewportRenderState.translationMatrix[fromYPosition].addXgetTile;
        Navigation::DirectionAlgorithmState::setAxisBasedDistanceResult
                  (&DAT_DirectionAlgorithmState,(int)DAT_UnitsState.units[unitID].x,
                   (int)DAT_UnitsState.units[unitID].y,fromXPosition,fromYPosition);
        DAT_DirectionAlgorithmState.distanceHigh =
             DAT_DirectionAlgorithmState.distanceHigh + piVar2[1] * 8;
        if (DAT_DirectionAlgorithmState.distanceHigh < local_10) {
          DAT_TroopValueState.tile = piVar2[-1];
          local_8 = local_14;
          local_10 = DAT_DirectionAlgorithmState.distanceHigh;
          DAT_TroopValueState.x = fromXPosition;
          DAT_TroopValueState.y = fromYPosition;
        }
      }
      local_14 = local_14 + 1;
      piVar2 = piVar2 + 4;
    } while (local_14 < *(int *)((int)DAT_TroopValueState.attackInfo.moatValuesArray + iVar1 + -8));
    if (-1 < local_8) {
      iVar1 = iVar1 + local_8 * 0x10;
      *(int *)((int)DAT_TroopValueState.attackInfo.moatValuesArray + iVar1 + 0xc) = unitID;
      return *(undefined4 *)((int)DAT_TroopValueState.attackInfo.moatValuesArray + iVar1 + 4);
    }
  }
  return 0;
}


// ================= _HoldStrong::Map::Units::TroopValueState::findNearestDiggableMoatPoint @ 0051a8a0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::Units::TroopValueState::findNearestDiggableMoatPoint
          (TroopValueState *this,int param_1)

{
  BOOLEnum tile;
  int iVar1;
  
  tile = TileMapState::findNearestFriendlyMoatTileForDigging
                   (&DAT_TileMapState,(int)DAT_UnitsState.units[param_1].owner,param_1,2);
  if (tile < 0x80000000) {
    iVar1 = TileMapState::setXYBasedOnMoatID
                      (&DAT_TileMapState,tile,2,(int)DAT_UnitsState.units[param_1].x,
                       (int)DAT_UnitsState.units[param_1].y);
    if (0 < iVar1) {
      DAT_TroopValueState.x = DAT_TileMapState.ALG_MoatXResult;
      DAT_TroopValueState.y = DAT_TileMapState.ALG_MoatYResult;
      DAT_TroopValueState.tile = DAT_TileMapState.someMoatTile;
      return iVar1;
    }
  }
  return 0;
}


// ================= _HoldStrong::Map::Units::TroopValueState::findTribeWithMoatAttackBehavior @ 0051a920 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Units::TroopValueState::findTribeWithMoatAttackBehavior(TroopValueState *this)

{
  BOOLEnum BVar1;
  int *piVar2;
  int iVar3;
  
  iVar3 = 1;
  piVar2 = &DAT_TribesState.tribes[1].owner;
  do {
    if (*(short *)(piVar2 + 5) != 0) {
      BVar1 = Game::GameStateStructures::isFullIDEqualsToMinus1(&DAT_GameState,*piVar2);
      if ((BVar1 != FALSE) && (*(SomeTribeBehaviorTypeShort *)(piVar2 + 9) == STBT_0x3f7)) {
        DAT_TroopValueState.x = (int)DAT_TribesState.tribes[iVar3].targetX;
        DAT_TroopValueState.y = (int)DAT_TribesState.tribes[iVar3].targetY;
        DAT_TroopValueState.attackInfo.field127625_0x42744 = iVar3;
        return 1;
      }
    }
    piVar2 = piVar2 + 0xcd;
    iVar3 = iVar3 + 1;
    if (0x176238b < (int)piVar2) {
      return 0;
    }
  } while( true );
}


// ================= _HoldStrong::Map::Units::UnitsState::hasTunnelerNotFinishedDigging @ 005339f0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::Units::UnitsState::hasTunnelerNotFinishedDigging(UnitsState *this,int param_1)

{
  return (uint)(DAT_UnitsState.units[param_1].tunnelerFinishedDigging == 0);
}


// ================= _HoldStrong::Map::Units::UnitsState::unitIsInMoat @ 00534460 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall _HoldStrong::Map::Units::UnitsState::unitIsInMoat(UnitsState *this,int unitID)

{
  return (uint)DAT_TileMapState.LogicLayer[DAT_UnitsState.units[unitID].tile] >> 0x1e & TRUE;
}


// ================= HoldStrong_lib::__isdigit_l @ 0058452e =================

/* Library Function - Single Match
   Name: __isdigit_l
   Library: Visual Studio 2005 Release
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __cdecl HoldStrong_lib::__isdigit_l(int _C,_locale_t _Locale)

{
  uint uVar1;
  _LocaleUpdate local_14;
  
  _LocaleUpdate::_LocaleUpdate(&local_14,_Locale);
  if ((int)(local_14.threadlocinfo)->locale_name[3] < 2) {
    uVar1 = (byte)local_14.threadlocinfo[1].lc_category[0].locale[_C * 2] & 4;
  }
  else {
    uVar1 = __isctype_l(_C,4,(_locale_t)&local_14);
  }
  if (local_14.unknownFlag != 0) {
    (local_14.ptd)->_ownlocale = (local_14.ptd)->_ownlocale & 0xfffffffd;
  }
  return uVar1;
}


// ================= HoldStrong_lib::_isdigit @ 0058457d =================

/* Library Function - Single Match
   Name: _isdigit
   Library: Visual Studio 2005 Release
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __cdecl HoldStrong_lib::_isdigit(int _C)

{
  int iVar1;
  
  if (DAT_02427614 == 0) {
    return (byte)PTR_DAT_00b94d50[_C * 2] & 4;
  }
  iVar1 = __isdigit_l(_C,(_locale_t)0x0);
  return iVar1;
}


// ================= HoldStrong_lib::__wchartodigit @ 00595f8e =================

/* Library Function - Single Match
   Name: __wchartodigit
   Library: Visual Studio 2005 Release
   decompilerscript: committed: 2026-05-02 18:15:17.059000 */

int HoldStrong_lib::__wchartodigit(ushort param_1)

{
  int iVar1;
  bool bVar2;
  
  if (0x2f < param_1) {
    if (param_1 < 0x3a) {
      return param_1 - 0x30;
    }
    iVar1 = 0xff10;
    if (param_1 < 0xff10) {
      iVar1 = 0x660;
      if (param_1 < 0x660) {
        return -1;
      }
      if (param_1 < 0x66a) goto LAB_00595fcc;
      iVar1 = 0x6f0;
      if (param_1 < 0x6f0) {
        return -1;
      }
      if (param_1 < 0x6fa) goto LAB_00595fcc;
      iVar1 = 0x966;
      if (param_1 < 0x966) {
        return -1;
      }
      if (param_1 < 0x970) goto LAB_00595fcc;
      iVar1 = 0x9e6;
      if (param_1 < 0x9e6) {
        return -1;
      }
      if (param_1 < 0x9f0) goto LAB_00595fcc;
      iVar1 = 0xa66;
      if (param_1 < 0xa66) {
        return -1;
      }
      if (param_1 < 0xa70) goto LAB_00595fcc;
      iVar1 = 0xae6;
      if (param_1 < 0xae6) {
        return -1;
      }
      if (param_1 < 0xaf0) goto LAB_00595fcc;
      iVar1 = 0xb66;
      if (param_1 < 0xb66) {
        return -1;
      }
      if (param_1 < 0xb70) goto LAB_00595fcc;
      iVar1 = 0xc66;
      if (param_1 < 0xc66) {
        return -1;
      }
      if (param_1 < 0xc70) goto LAB_00595fcc;
      iVar1 = 0xce6;
      if (param_1 < 0xce6) {
        return -1;
      }
      if (param_1 < 0xcf0) goto LAB_00595fcc;
      iVar1 = 0xd66;
      if (param_1 < 0xd66) {
        return -1;
      }
      if (param_1 < 0xd70) goto LAB_00595fcc;
      iVar1 = 0xe50;
      if (param_1 < 0xe50) {
        return -1;
      }
      if (param_1 < 0xe5a) goto LAB_00595fcc;
      iVar1 = 0xed0;
      if (param_1 < 0xed0) {
        return -1;
      }
      if (param_1 < 0xeda) goto LAB_00595fcc;
      iVar1 = 0xf20;
      if (param_1 < 0xf20) {
        return -1;
      }
      if (param_1 < 0xf2a) goto LAB_00595fcc;
      iVar1 = 0x1040;
      if (param_1 < 0x1040) {
        return -1;
      }
      if (param_1 < 0x104a) goto LAB_00595fcc;
      iVar1 = 0x17e0;
      if (param_1 < 0x17e0) {
        return -1;
      }
      if (param_1 < 0x17ea) goto LAB_00595fcc;
      iVar1 = 0x1810;
      if (param_1 < 0x1810) {
        return -1;
      }
      bVar2 = param_1 < 0x181a;
    }
    else {
      bVar2 = param_1 < 0xff1a;
    }
    if (bVar2) {
LAB_00595fcc:
      return (uint)param_1 - iVar1;
    }
  }
  return -1;
}


// Treffer: 42
