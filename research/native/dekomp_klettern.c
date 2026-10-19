// ================= _HoldStrong::Map::Navigation::PathFindingState::doMoveFromTileToTile @ 00497280 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::Navigation::PathFindingState::doMoveFromTileToTile
          (PathFindingState *this,int unitID,int tile,int y,int direction,int param_5,
          int ignoreAssassinClimbing)

{
  short *psVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  
  if (param_5 != 0) {
    if (param_5 == 1) {
      if ((DAT_TileMapState.LogicLayer
           [DAT_TileMapState.directionTranslationMatrix[y][direction] + tile] & 0x30U) != 0) {
        return FALSE;
      }
      if ((DAT_TileMapState.LogicLayer
           [DAT_TileMapState.directionTranslationMatrix[y][direction] + tile] & 1U) != 0) {
        return FALSE;
      }
    }
    return TRUE;
  }
                    /* if we cannot move in that direction from the current tile? */
  if ((DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[direction] &
      DAT_TileMapState.PathLinkageLayer[tile]) == 0) {
    iVar6 = DAT_TileMapState.directionTranslationMatrix[y][direction] + tile;
    if (ignoreAssassinClimbing == 0) {
      if (DAT_UnitsState.units[unitID].unitType == UT_A_ASSASSIN) {
        uVar5 = DAT_TileMapState.LogicLayer[iVar6];
        if ((((uVar5 & 0x4a5014b1) == 0) &&
            ((uVar7 = DAT_TileMapState.LogicLayer[tile] & 0x100, uVar7 == 0 ||
             ((uVar5 & 0x100) == 0)))) && ((uVar7 != 0 || ((uVar5 & 0x100) != 0)))) {
          bVar2 = DAT_TileMapState.HeightLayer[tile];
          DAT_UnitsState.units[unitID].animationCycleNumber = 0;
          DAT_UnitsState.units[unitID].field323_0x418 = 0;
          if (uVar7 == 0) {
            bVar3 = DAT_TileMapState.HeightLayer[iVar6];
            bVar4 = DAT_TileMapState.WallOwnerLayer[iVar6];
            DAT_UnitsState.units[unitID].state.generic = US_ASSASSIN_THROWING_HOOK;
            DAT_UnitsState.units[unitID].assassinHeightDifference = (ushort)bVar3 - (ushort)bVar2;
            DAT_UnitsState.units[unitID].assassinClimbingUpUnk_OR_previousFacingDirection = 1;
            DAT_UnitsState.units[unitID].ownerOfAssassinScaledObject = (bVar4 & 7) + 1;
          }
          else {
            bVar3 = DAT_TileMapState.HeightLayer[iVar6];
            DAT_UnitsState.units[unitID].state.generic = US_ASSASSIN_START_CLIMBING_DOWN;
            DAT_UnitsState.units[unitID].assassinHeightDifference = (ushort)bVar2 - (ushort)bVar3;
            DAT_UnitsState.units[unitID].assassinClimbingUpUnk_OR_previousFacingDirection = 0;
          }
          if (DAT_UnitsState.units[unitID].assassinHeightDifference < 0) {
            DAT_UnitsState.units[unitID].assassinHeightDifference = 0;
          }
          return TRUE;
        }
        return FALSE;
      }
    }
    else {
      uVar5 = DAT_TileMapState.LogicLayer[iVar6];
      if ((uVar5 & 0x40000000) != 0) {
        return TRUE;
      }
      if (((DAT_TileMapState.LogicLayer[tile] & 0x40000000U) != 0) && ((uVar5 & 0x4a5014b1) == 0)) {
        return ~(uVar5 >> 8) & TRUE;
      }
    }
  }
  else {
    if ((DAT_EntityState.fireCount == 0) || (DAT_UnitsState.units[unitID].field312_0x40a != 0)) {
      DAT_UnitsState.units[unitID].counter = 0;
      return TRUE;
    }
    if (DAT_TileMapState.EntityLayer
        [DAT_TileMapState.directionTranslationMatrix[y][direction] + tile] == 0) {
      return TRUE;
    }
    if (DAT_EntityState.entityArray
        [DAT_TileMapState.EntityLayer
         [DAT_TileMapState.directionTranslationMatrix[y][direction] + tile]].entityType != ET_FIRE)
    {
      return TRUE;
    }
    if ((DAT_TileMapState.EntityLayer[tile] != 0) &&
       (DAT_EntityState.entityArray[DAT_TileMapState.EntityLayer[tile]].entityType == ET_FIRE)) {
      return TRUE;
    }
    psVar1 = &DAT_UnitsState.units[unitID].counter;
    *psVar1 = *psVar1 + 1;
    DAT_UnitsState.units[unitID].field297_0x3f4 = 5;
    DAT_UnitsState.units[unitID].field312_0x40a = 1;
  }
  return FALSE;
}


// ================= _HoldStrong::Map::Navigation::PathFindingState::pathfindingForAttacksUnk @ 004a75b0 =================

/* WARNING: Type propagation algorithm not settling */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Navigation::PathFindingState::pathfindingForAttacksUnk
          (PathFindingState *this,int tribeID,int buildingID,int param_3,dword param_4,int param_5)

{
  byte bVar1;
  short sVar2;
  int iVar3;
  BOOLEnum BVar4;
  uint uVar5;
  BOOLEnum BVar6;
  uint uVar7;
  XYPair *pXVar8;
  uint uVar9;
  int iVar10;
  int *piVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int tile2;
  int local_28;
  int *local_24;
  int local_20;
  
  iVar3 = (int)(short)DAT_BuildingsState.buildings[buildingID].y;
  uVar7 = DAT_BuildingsState.buildings[buildingID].widthOrHeight;
  iVar10 = (int)(short)DAT_BuildingsState.buildings[buildingID].x;
  bVar1 = DAT_TileMapState.DefaultHeightLayer
          [DAT_BuildingsState.buildings[buildingID].currentTilePositionAdjusted];
  sVar2 = DAT_TribesState.tribes[tribeID].selectionTargetUnitID;
  local_28 = 0;
  BVar4 = Units::TribesState::isTribeAllAssassins(&DAT_TribesState,tribeID);
  param_3 = param_3 * 2;
  if (param_3 < 0x1f5) {
    if (param_3 < 0x32) {
      param_3 = 0x32;
    }
  }
  else {
    param_3 = 500;
  }
  iVar14 = DAT_BuildingDefinedData.DAT_BuildingAccessibleTilesCount[uVar7];
  local_20 = 0;
  tribeID = 0;
  if (0 < iVar14) {
    local_24 = &DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper;
    do {
      Buildings::BuildingsState::setupBuildingEntrancesOffset(uVar7,1,local_20,0);
      iVar12 = DAT_ViewportRenderState.translationMatrix[iVar3 + DAT_BuildingsState.DAT_TempYOffset]
               .addXgetTile + DAT_BuildingsState.DAT_TempXOffset;
      iVar13 = iVar12 + iVar10;
      uVar5 = (uint)bVar1 - (uint)*(byte *)(iVar12 + 0x1d32c38 + iVar10);
      uVar9 = (int)uVar5 >> 0x1f;
      if (((int)((uVar5 ^ uVar9) - uVar9) < 0x20) &&
         (((((int)(short)DAT_TileMapState.PathConnectionLayer[iVar13] == param_4 ||
            (iVar12 = calculateCanPlayerUnitsNavigateToAreaFromArea
                                (&DAT_PathFindingState,param_5,param_4,
                                 (int)(short)DAT_TileMapState.PathConnectionLayer[iVar13],0),
            iVar12 != 0)) ||
           ((BVar4 != FALSE &&
            (BVar6 = calculateCanReachUsingCachedAreaLogic
                               (&DAT_PathFindingState,DAT_UnitsState.units[sVar2].tile,iVar13),
            BVar6 != FALSE)))) &&
          (uVar5 = (int)DAT_BuildingsState.buildings[buildingID].terrainHeightUnk -
                   (uint)DAT_TileMapState.HeightLayer[iVar13], uVar9 = (int)uVar5 >> 0x1f,
          (int)((uVar5 ^ uVar9) - uVar9) < 0x10)))) {
        ((PathHelper12 *)(local_24 + -1))->tile1 = iVar13;
        *local_24 = 0;
        pXVar8 = DAT_ClimbLogicDefinedData.DAT_CardinalHorizontalFirstSearchOrder;
        do {
          iVar12 = DAT_ViewportRenderState.translationMatrix
                   [pXVar8->y + DAT_BuildingsState.DAT_TempYOffset + iVar3].addXgetTile + pXVar8->x
                   + DAT_BuildingsState.DAT_TempXOffset + iVar10;
          if (((DAT_TileMapState.LogicLayer[iVar12] & 0xf000000U) == 0) &&
             ((short)DAT_TileMapState.BuildingLayer[iVar12] == buildingID)) {
            *local_24 = iVar12;
            break;
          }
          pXVar8 = pXVar8 + 1;
        } while ((int)pXVar8 < 0xb39238);
        local_24 = local_24 + 3;
        local_28 = local_28 + 1;
        if (param_3 <= local_28) {
          return;
        }
      }
      local_20 = local_20 + 1;
      if (iVar14 <= local_20) {
        local_20 = 0;
      }
      tribeID = tribeID + 1;
    } while (tribeID < iVar14);
  }
  iVar14 = uVar7 + 1;
  if (iVar14 < 0xe) {
    local_20 = 0x20;
    do {
      iVar12 = DAT_BuildingDefinedData.DAT_BuildingAccessibleTilesCount[iVar14];
      iVar13 = 0;
      tribeID = 0;
      if (0 < iVar12) {
        piVar11 = &((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->
                   destinationsArray[local_28].tile2OrAHelper;
        do {
          Buildings::BuildingsState::setupBuildingEntrancesOffset(iVar14,1,iVar13,0);
          uVar7 = iVar3 + DAT_BuildingsState.DAT_TempYOffset;
          if ((((uint)(DAT_BuildingsState.DAT_TempXOffset + iVar10) < 400) && (uVar7 < 400)) &&
             (*(char *)(uVar7 * 400 + 0x21aec98 + DAT_BuildingsState.DAT_TempXOffset + iVar10) !=
              '\0')) {
            iVar15 = DAT_ViewportRenderState.translationMatrix[uVar7].addXgetTile +
                     DAT_BuildingsState.DAT_TempXOffset;
            tile2 = iVar15 + iVar10;
            uVar7 = (uint)bVar1 - (uint)*(byte *)(iVar15 + 0x1d32c38 + iVar10);
            uVar5 = (int)uVar7 >> 0x1f;
            if ((((int)((uVar7 ^ uVar5) - uVar5) < 0x20) &&
                ((((int)(short)DAT_TileMapState.PathConnectionLayer[tile2] == param_4 ||
                  (iVar15 = calculateCanPlayerUnitsNavigateToAreaFromArea
                                      (&DAT_PathFindingState,param_5,param_4,
                                       (int)(short)DAT_TileMapState.PathConnectionLayer[tile2],0),
                  iVar15 != 0)) ||
                 ((BVar4 != FALSE &&
                  (BVar6 = calculateCanReachUsingCachedAreaLogic
                                     (&DAT_PathFindingState,DAT_UnitsState.units[sVar2].tile,tile2),
                  BVar6 != FALSE)))))) &&
               (uVar7 = (int)DAT_BuildingsState.buildings[buildingID].terrainHeightUnk -
                        (uint)DAT_TileMapState.HeightLayer[tile2], uVar5 = (int)uVar7 >> 0x1f,
               (int)((uVar7 ^ uVar5) - uVar5) < local_20)) {
              local_28 = local_28 + 1;
              ((PathHelper12 *)(piVar11 + -1))->tile1 = tile2;
              *piVar11 = 0;
              piVar11 = piVar11 + 3;
              if (param_3 <= local_28) {
                return;
              }
            }
            iVar13 = iVar13 + 1;
            if (iVar12 <= iVar13) {
              iVar13 = 0;
            }
          }
          tribeID = tribeID + 1;
        } while (tribeID < iVar12);
      }
      local_20 = local_20 + 0x10;
      iVar14 = iVar14 + 1;
    } while (iVar14 < 0xe);
  }
  DAT_PathFindingState.searchQueue.destinationsArray[local_28].tile1 = 0;
  ((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->destinationsArray[local_28].
  tile2OrAHelper = 0;
  return;
}


// ================= _HoldStrong::Map::Navigation::PathFindingState::pathPlanningForTribe @ 004a79a0 =================

/* WARNING: Type propagation algorithm not settling */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Navigation::PathFindingState::pathPlanningForTribe
          (PathFindingState *this,uint tribeID,undefined4 targetUnitID,uint x,uint y,int unitCount,
          dword area,int playerID)

{
  short sVar1;
  short sVar2;
  short sVar3;
  BOOLEnum BVar4;
  int iVar5;
  int iVar6;
  BOOLEnum BVar7;
  uint uVar8;
  uint uVar9;
  int (*paiVar10) [8];
  int *piVar11;
  short *psVar12;
  uint uVar13;
  int iVar14;
  int _destIndex;
  
  _destIndex = 0;
  BVar4 = Units::TribesState::isTribeAllAssassins(&DAT_TribesState,tribeID);
  if (399 < x) {
    return;
  }
  if (399 < y) {
    return;
  }
  if (*(char *)(y * 400 + 0x21aec98 + x) == '\0') {
    return;
  }
  DAT_PathFindingState.searchGeneration = DAT_PathFindingState.searchGeneration + 1;
  if (32000 < DAT_PathFindingState.searchGeneration) {
    DAT_PathFindingState.searchGeneration = 1;
    IO::LowLevelMemory::fillMemory_ByteValue
              (&DAT_LowLevelMemory,0x27420,'\0',DAT_TileMapState.WalkLayer);
  }
  unitCount = unitCount * 2;
  if (unitCount < 0x1f5) {
    if (unitCount < 0x32) {
      unitCount = 0x32;
    }
  }
  else {
    unitCount = 500;
  }
  DAT_PathFindingState.searchQueue.readIndex = 0;
  DAT_PathFindingState.searchQueue.writeIndex = 1;
  DAT_PathFindingState.searchQueue.currentDistance = 1;
  DAT_PathFindingState.searchQueue.yQueue[0] = (short)y;
  DAT_PathFindingState.searchQueue.xQueue[0] = (short)x;
  iVar5 = DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x;
  DAT_PathFindingState.searchQueue.tilesQueue[0] = iVar5;
  DAT_TileMapState.CertainPathLayer[iVar5] = 1;
  DAT_TileMapState.WalkLayer[DAT_PathFindingState.searchQueue.tilesQueue[0]] =
       (short)DAT_PathFindingState.searchGeneration;
  if (DAT_PathFindingState.searchQueue.readIndex != DAT_PathFindingState.searchQueue.writeIndex) {
    while (uVar13 = DAT_PathFindingState.searchQueue.tilesQueue
                    [DAT_PathFindingState.searchQueue.readIndex], uVar13 < 0x13a10) {
      sVar1 = DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.readIndex];
      sVar2 = DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.readIndex];
      DAT_PathFindingState.searchQueue.currentDistance =
           (int)DAT_TileMapState.CertainPathLayer[uVar13];
      if ((0x13a10 < DAT_PathFindingState.searchQueue.currentDistance) ||
         (10 < DAT_PathFindingState.searchQueue.currentDistance)) break;
      psVar12 = &DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[0].short.yOffset;
      paiVar10 = DAT_TileMapState.directionTranslationMatrix + sVar2;
      do {
        iVar14 = (*paiVar10)[0] + uVar13;
        if ((DAT_TileMapState.WalkLayer[iVar14] != DAT_PathFindingState.searchGeneration) &&
           (((area == (int)(short)DAT_TileMapState.PathConnectionLayer[iVar14] ||
             (iVar6 = calculateCanPlayerUnitsNavigateToAreaFromArea
                                (&DAT_PathFindingState,playerID,area,
                                 (int)(short)DAT_TileMapState.PathConnectionLayer[iVar14],0),
             iVar6 != 0)) ||
            ((BVar4 != FALSE &&
             (BVar7 = calculateCanReachUsingCachedAreaLogic(&DAT_PathFindingState,iVar5,iVar14),
             BVar7 != FALSE)))))) {
          sVar3 = ((Point8ShortXY *)(psVar12 + -2))->xOffset;
          DAT_TileMapState.CertainPathLayer[iVar14] =
               (short)DAT_PathFindingState.searchQueue.currentDistance + 1;
          DAT_TileMapState.WalkLayer[iVar14] = (short)DAT_PathFindingState.searchGeneration;
          DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.writeIndex] =
               sVar3 + sVar1;
          DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.writeIndex] =
               *psVar12 + sVar2;
          DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.writeIndex] =
               iVar14;
          DAT_PathFindingState.searchQueue.writeIndex =
               DAT_PathFindingState.searchQueue.writeIndex + 1;
          if (0x13a0f < DAT_PathFindingState.searchQueue.writeIndex) {
            DAT_PathFindingState.searchQueue.writeIndex = 0;
          }
        }
        psVar12 = psVar12 + 4;
        paiVar10 = (int (*) [8])(*paiVar10 + 1);
      } while ((int)psVar12 < 0xb4908c);
      DAT_PathFindingState.searchQueue.readIndex = DAT_PathFindingState.searchQueue.readIndex + 1;
      if (0x13a0f < DAT_PathFindingState.searchQueue.readIndex) {
        DAT_PathFindingState.searchQueue.readIndex = 0;
      }
      if (DAT_PathFindingState.searchQueue.readIndex == DAT_PathFindingState.searchQueue.writeIndex)
      break;
    }
  }
  DAT_PathFindingState.searchQueue.readIndex = 0;
  if (0 < DAT_PathFindingState.searchQueue.writeIndex) {
    piVar11 = &DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper;
    do {
                    /* warning */
      tribeID = (uint)DAT_TileMapState.HeightLayer[iVar5];
      if ((DAT_TileMapState.LogicLayer[iVar5] & 0x10000000U) != 0) {
        iVar14 = Buildings::BuildingsState::getBuildingHeightForBuildingID
                           ((int)(short)DAT_TileMapState.BuildingLayer[iVar5]);
        tribeID = tribeID + iVar14;
      }
      iVar14 = DAT_PathFindingState.searchQueue.tilesQueue
               [DAT_PathFindingState.searchQueue.readIndex];
      uVar13 = (uint)DAT_TileMapState.HeightLayer[iVar14];
      if ((DAT_TileMapState.LogicLayer[iVar14] & 0x10000000U) != 0) {
        iVar14 = Buildings::BuildingsState::getBuildingHeightForBuildingID
                           ((int)(short)DAT_TileMapState.BuildingLayer[iVar14]);
        uVar13 = uVar13 + iVar14;
      }
      uVar8 = y - (int)DAT_PathFindingState.searchQueue.yQueue
                       [DAT_PathFindingState.searchQueue.readIndex];
      uVar9 = (int)uVar8 >> 0x1f;
      iVar6 = (uVar8 ^ uVar9) - uVar9;
      uVar8 = x - (int)DAT_PathFindingState.searchQueue.xQueue
                       [DAT_PathFindingState.searchQueue.readIndex];
      uVar9 = (int)uVar8 >> 0x1f;
      iVar14 = (uVar8 ^ uVar9) - uVar9;
      if (iVar14 <= iVar6) {
        iVar14 = iVar6;
      }
      if ((iVar14 == 2) &&
         (uVar8 = (int)(tribeID - uVar13) >> 0x1f, (int)((tribeID - uVar13 ^ uVar8) - uVar8) < 0x20)
         ) {
        ((PathHelper12 *)(piVar11 + -1))->tile1 =
             DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.readIndex]
        ;
        _destIndex = _destIndex + 1;
        *piVar11 = 1;
        piVar11 = piVar11 + 3;
        if (unitCount <= _destIndex) {
          return;
        }
      }
      DAT_PathFindingState.searchQueue.readIndex = DAT_PathFindingState.searchQueue.readIndex + 1;
    } while (DAT_PathFindingState.searchQueue.readIndex <
             DAT_PathFindingState.searchQueue.writeIndex);
    if (4 < _destIndex) goto LAB_004a7e8c;
  }
  DAT_PathFindingState.searchQueue.readIndex = 0;
  if (0 < DAT_PathFindingState.searchQueue.writeIndex) {
    piVar11 = &((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->destinationsArray
               [_destIndex].tile2OrAHelper;
    do {
      tribeID = (uint)DAT_TileMapState.HeightLayer[iVar5];
      if ((DAT_TileMapState.LogicLayer[iVar5] & 0x10000000U) != 0) {
        iVar14 = Buildings::BuildingsState::getBuildingHeightForBuildingID
                           ((int)(short)DAT_TileMapState.BuildingLayer[iVar5]);
        tribeID = tribeID + iVar14;
      }
      iVar14 = DAT_PathFindingState.searchQueue.tilesQueue
               [DAT_PathFindingState.searchQueue.readIndex];
      uVar13 = (uint)DAT_TileMapState.HeightLayer[iVar14];
      if ((DAT_TileMapState.LogicLayer[iVar14] & 0x10000000U) != 0) {
        iVar14 = Buildings::BuildingsState::getBuildingHeightForBuildingID
                           ((int)(short)DAT_TileMapState.BuildingLayer[iVar14]);
        uVar13 = uVar13 + iVar14;
      }
      uVar8 = y - (int)DAT_PathFindingState.searchQueue.yQueue
                       [DAT_PathFindingState.searchQueue.readIndex];
      uVar9 = (int)uVar8 >> 0x1f;
      iVar6 = (uVar8 ^ uVar9) - uVar9;
      uVar8 = x - (int)DAT_PathFindingState.searchQueue.xQueue
                       [DAT_PathFindingState.searchQueue.readIndex];
      uVar9 = (int)uVar8 >> 0x1f;
      iVar14 = (uVar8 ^ uVar9) - uVar9;
      if (iVar14 <= iVar6) {
        iVar14 = iVar6;
      }
      if ((iVar14 == 1) &&
         (uVar8 = (int)(tribeID - uVar13) >> 0x1f, (int)((tribeID - uVar13 ^ uVar8) - uVar8) < 0x20)
         ) {
        ((PathHelper12 *)(piVar11 + -1))->tile1 =
             DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.readIndex]
        ;
        _destIndex = _destIndex + 1;
        *piVar11 = 1;
        piVar11 = piVar11 + 3;
        if (unitCount <= _destIndex) {
          return;
        }
      }
      DAT_PathFindingState.searchQueue.readIndex = DAT_PathFindingState.searchQueue.readIndex + 1;
    } while (DAT_PathFindingState.searchQueue.readIndex <
             DAT_PathFindingState.searchQueue.writeIndex);
  }
LAB_004a7e8c:
  DAT_PathFindingState.searchQueue.readIndex = 0;
  if (0 < DAT_PathFindingState.searchQueue.writeIndex) {
    piVar11 = &((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->destinationsArray
               [_destIndex].tile2OrAHelper;
    do {
      uVar13 = y - (int)DAT_PathFindingState.searchQueue.yQueue
                        [DAT_PathFindingState.searchQueue.readIndex];
      uVar8 = (int)uVar13 >> 0x1f;
      iVar14 = (uVar13 ^ uVar8) - uVar8;
      uVar13 = x - (int)DAT_PathFindingState.searchQueue.xQueue
                        [DAT_PathFindingState.searchQueue.readIndex];
      uVar8 = (int)uVar13 >> 0x1f;
      iVar5 = (uVar13 ^ uVar8) - uVar8;
      if (iVar5 <= iVar14) {
        iVar5 = iVar14;
      }
      if (2 < iVar5) {
        ((PathHelper12 *)(piVar11 + -1))->tile1 =
             DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.readIndex]
        ;
        _destIndex = _destIndex + 1;
        *piVar11 = 0;
        piVar11 = piVar11 + 3;
        if (unitCount <= _destIndex) {
          return;
        }
      }
      DAT_PathFindingState.searchQueue.readIndex = DAT_PathFindingState.searchQueue.readIndex + 1;
    } while (DAT_PathFindingState.searchQueue.readIndex <
             DAT_PathFindingState.searchQueue.writeIndex);
  }
  DAT_PathFindingState.searchQueue.destinationsArray[_destIndex].tile1 = 0;
  ((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->destinationsArray[_destIndex].
  tile2OrAHelper = 0;
  return;
}


// ================= _HoldStrong::Map::Navigation::PathFindingState::Constructor_PathFindingState @ 004a9760 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

PathFindingState * __thiscall
_HoldStrong::Map::Navigation::PathFindingState::Constructor_PathFindingState(PathFindingState *this)

{
  DAT_PathFindingState.field40_0x70 = 0;
  DAT_PathFindingState.field41_0x74 = 0;
  DAT_PathFindingState.DAT_lWys = 0;
  DAT_PathFindingState.notAllAssassinsUnk = 0;
  DAT_PathFindingState.DAT_Easy = 0;
  DAT_PathFindingState.DAT_Hard = 0;
  DAT_PathFindingState.DAT_Test_likely = 0;
  DAT_PathFindingState.DAT_Test_gatehouse = 0;
  DAT_PathFindingState.searchNonmatchCount = 0;
  DAT_PathFindingState.searchMatchCounter = 0;
  DAT_PathFindingState.DAT_Ass = 0;
  DAT_PathFindingState.calculations = 0;
  DAT_PathFindingState.DAT_Mini_spreads = 0;
  Global::ClearPathFindingTileMaps();
  clearAllLadderManWalledData(&DAT_PathFindingState);
  DAT_PathFindingState.searchGeneration = 1;
  return &DAT_PathFindingState;
}


// ================= _HoldStrong::Map::Navigation::PathFindingState::doPathfinding @ 004a9b20 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

dword __thiscall
_HoldStrong::Map::Navigation::PathFindingState::doPathfinding
          (PathFindingState *this,int param_1,int param_2)

{
  ushort uVar1;
  dword dVar2;
  BOOLEnum BVar3;
  int iVar4;
  
  uVar1 = DAT_TileMapState.PathConnectionLayer
          [DAT_ViewportRenderState.translationMatrix[DAT_PathFindingState.destinationY].addXgetTile
           + DAT_PathFindingState.destinationX];
  if (((DAT_TileMapState.PathConnectionLayer
        [DAT_ViewportRenderState.translationMatrix[DAT_PathFindingState.unitY].addXgetTile +
         DAT_PathFindingState.unitX] != uVar1) && (DAT_PathFindingState.climbIsIllegal == 0)) &&
     (DAT_PathFindingState.allAssassinsUnk == 0)) {
    if (uVar1 == 0) {
      return 0;
    }
    dVar2 = findConnectingAreaBetweenTwoAreas
                      (&DAT_PathFindingState,param_1,
                       (int)(short)DAT_TileMapState.PathConnectionLayer
                                   [DAT_ViewportRenderState.translationMatrix
                                    [DAT_PathFindingState.unitY].addXgetTile +
                                    DAT_PathFindingState.unitX],(int)(short)uVar1);
    if (dVar2 == 0) {
      return 0;
    }
  }
  DAT_PathFindingState.searchQueue.pathPlanIndex = 0;
  DAT_PathFindingState.field43_0x7c = 1;
  if (((DAT_PathFindingState.climbIsIllegal == 0) && (DAT_PathFindingState.allAssassinsUnk == 0)) &&
     (BVar3 = tracePathPlanToDestinationViaUnoccupiedTiles
                        (&DAT_PathFindingState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY
                         ,DAT_PathFindingState.destinationX,DAT_PathFindingState.destinationY),
     BVar3 != FALSE)) {
    DAT_PathFindingState.DAT_Easy = DAT_PathFindingState.DAT_Easy + 1;
    return DAT_PathFindingState.searchQueue.pathPlanIndex;
  }
  DAT_PathFindingState.DAT_Hard = DAT_PathFindingState.DAT_Hard + 1;
  DAT_PathFindingState.field43_0x7c = 0;
  DirectionAlgorithmState::setAxisBasedDistanceResult
            (&DAT_DirectionAlgorithmState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY,
             DAT_PathFindingState.destinationX,DAT_PathFindingState.destinationY);
  iVar4 = (DAT_DirectionAlgorithmState.distanceHigh + 4) *
          (DAT_DirectionAlgorithmState.distanceHigh + 4) * 10;
  DAT_PathFindingState.searchQueue.pathPlanIndex = 0;
  if (DAT_PathFindingState.notAllAssassinsUnk == 0) {
    if (DAT_PathFindingState.allAssassinsUnk == 0) {
      BVar3 = findSuitableSpawnLocationUnk
                        (&DAT_PathFindingState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY
                         ,DAT_PathFindingState.destinationX,DAT_PathFindingState.destinationY,iVar4,
                         0);
    }
    else {
      BVar3 = findLinkageBasedPathOrWalkRadius
                        (&DAT_PathFindingState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY
                         ,DAT_PathFindingState.destinationX,DAT_PathFindingState.destinationY,iVar4,
                         FALSE);
    }
    if (BVar3 != FALSE) goto LAB_004a9cdd;
    if (DAT_PathFindingState.allAssassinsUnk == 0) {
      if (DAT_PathFindingState.climbIsIllegal == 0) goto LAB_004a9cce;
      BVar3 = findPathUsingClimbingWithHeightMargin16
                        (&DAT_PathFindingState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY
                         ,DAT_PathFindingState.destinationX,DAT_PathFindingState.destinationY,100000
                         ,FALSE);
    }
    else {
      BVar3 = pathFindingWithBuildingsIncluded
                        (&DAT_PathFindingState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY
                         ,DAT_PathFindingState.destinationX,DAT_PathFindingState.destinationY,100000
                         ,0);
    }
  }
  else {
LAB_004a9cce:
    BVar3 = findLinkageBasedPathOrWalkRadius
                      (&DAT_PathFindingState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY,
                       DAT_PathFindingState.destinationX,DAT_PathFindingState.destinationY,100000,
                       FALSE);
  }
  if (BVar3 == FALSE) {
    return 0;
  }
LAB_004a9cdd:
  if (DAT_PathFindingState.allAssassinsUnk == 0) {
    if (DAT_PathFindingState.climbIsIllegal == 0) {
      iVar4 = 1;
    }
    else {
      iVar4 = 2;
    }
  }
  else {
    iVar4 = 3;
  }
  traceAndCommitPathPlan
            (&DAT_PathFindingState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY,
             DAT_PathFindingState.destinationX,DAT_PathFindingState.destinationY,iVar4);
  if ((param_2 == 0) && (DAT_PathFindingState.field49_0x94 != 0)) {
    DAT_PathFindingState.searchQueue.pathPlanIndex = 0;
    iVar4 = calculatePathKeepAndWallsGatesNotAllowed
                      (&DAT_PathFindingState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY,
                       DAT_PathFindingState.destinationX,DAT_PathFindingState.destinationY,100000);
    if (iVar4 != 0) {
      traceAndCommitPathPlan
                (&DAT_PathFindingState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY,
                 DAT_PathFindingState.destinationX,DAT_PathFindingState.destinationY,1);
      return DAT_PathFindingState.searchQueue.pathPlanIndex;
    }
    findLinkageBasedPathOrWalkRadius
              (&DAT_PathFindingState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY,
               DAT_PathFindingState.destinationX,DAT_PathFindingState.destinationY,100000,FALSE);
    traceAndCommitPathPlan
              (&DAT_PathFindingState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY,
               DAT_PathFindingState.destinationX,DAT_PathFindingState.destinationY,1);
  }
  return DAT_PathFindingState.searchQueue.pathPlanIndex;
}


// ================= _HoldStrong::Map::Units::TribesState::isTribeAllAssassins @ 00524060 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::Units::TribesState::isTribeAllAssassins(TribesState *this,int tribeID)

{
  int iVar1;
  int iVar2;
  int unitSelectionIndex;
  
  iVar2 = (int)DAT_TribesState.tribes[tribeID].size;
  unitSelectionIndex = 0;
  if (0 < iVar2) {
    do {
      iVar1 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,unitSelectionIndex);
      unitSelectionIndex = unitSelectionIndex + 1;
      if (((DAT_UnitsState.units[iVar1].logicalState == ULS_NORMAL) &&
          (DAT_UnitsState.units[iVar1].dying == 0)) &&
         (DAT_UnitsState.units[iVar1].unitType != UT_A_ASSASSIN)) {
        return FALSE;
      }
    } while (unitSelectionIndex < iVar2);
  }
  return TRUE;
}


// ================= _HoldStrong::Map::Units::TribesState::applyMoveCommandOrRallyCommandToTribe @ 00524340 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Units::TribesState::applyMoveCommandOrRallyCommandToTribe
          (TribesState *this,int tribeID,undefined4 x1,undefined4 y1,undefined4 isRallying,
          int storeAsRallyPoint)

{
  short sVar1;
  BOOLEnum BVar2;
  int unitID;
  int unitSelectionIndex;
  
  unitSelectionIndex = 0;
  BVar2 = isTribeAllAssassins(&DAT_TribesState,tribeID);
  DAT_TribesState.tribes[tribeID].someUnitID = 0;
  if (storeAsRallyPoint != 0) {
    sVar1 = DAT_TribesState.tribes[tribeID].selectionTargetUnitID;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = (short)isRallying;
    DAT_TribesState.tribes[tribeID].rallyPointArray[0][0] = DAT_UnitsState.units[sVar1].x;
    DAT_TribesState.tribes[tribeID].rallyPointArray[0][1] = DAT_UnitsState.units[sVar1].y;
    DAT_TribesState.tribes[tribeID].rallyPointArray[1][0] = (short)x1;
    DAT_TribesState.tribes[tribeID].rallyPointArray[1][1] = (short)y1;
    DAT_TribesState.tribes[tribeID].currentRallyPointIndex = 1;
    DAT_TribesState.tribes[tribeID].rallyPointCount = 2;
  }
  if (0 < DAT_TribesState.tribes[tribeID].size) {
    do {
      unitID = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,unitSelectionIndex);
      unitSelectionIndex = unitSelectionIndex + 1;
      if ((((DAT_UnitsState.units[unitID].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[unitID].dying == 0)) &&
          (DAT_UnitsState.units[unitID].usingTeleport == 0)) &&
         (((DAT_UnitsState.units[unitID].field320_0x413 == 0 &&
           (DAT_UnitsState.units[unitID].state.generic != US_MELEE_ATTACK)) &&
          ((DAT_UnitsState.units[unitID].moveableUnk != 0 &&
           (DAT_UnitsState.units[unitID].moveRelatedFlag != 1)))))) {
        DAT_UnitsState.units[unitID].plannedDestinationX = (short)x1;
        DAT_UnitsState.units[unitID].state.generic = US_MOVE_TO_DESTINATION;
        DAT_UnitsState.units[unitID].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
        DAT_UnitsState.units[unitID]._someX_2 = 0;
        DAT_UnitsState.units[unitID]._someY_2 = 0;
        DAT_UnitsState.units[unitID].plannedDestinationY = (short)y1;
        DAT_UnitsState.units[unitID].moveDelay = 0;
        DAT_UnitsState.units[unitID].moveInstructionSpeedDelayTracker = 0;
        if (BVar2 != FALSE) {
          DAT_PathFindingState.allAssassinsUnk = 1;
        }
        UnitsState::setDestinationForUnit(&DAT_UnitsState,unitID,(int)(short)x1,(int)(short)y1,0);
      }
    } while (unitSelectionIndex < DAT_TribesState.tribes[tribeID].size);
  }
  return 1;
}


// ================= _HoldStrong::Map::Units::TribesState::assignAttackTargetsForTribe @ 005244d0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Units::TribesState::assignAttackTargetsForTribe
          (TribesState *this,int tribeID,SomeTribeBehaviorType targetType)

{
  UnitStateShort UVar1;
  UnitTypeShort UVar2;
  short sVar3;
  BOOLEnum BVar4;
  uint unitID;
  int iVar5;
  uint uVar6;
  BOOLEnum BVar7;
  uint y;
  int unitSelectionIndex;
  uint tile;
  bool bVar8;
  
  unitSelectionIndex = 0;
  BVar4 = isTribeAllAssassins(&DAT_TribesState,tribeID);
  if (DAT_GameSynchronyState.currentPlayerFullIDArray[DAT_TribesState.tribes[tribeID].owner] != -1)
  {
    return 0;
  }
  if (0 < DAT_TribesState.tribes[tribeID].size) {
    do {
      unitID = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,unitSelectionIndex);
      unitSelectionIndex = unitSelectionIndex + 1;
      if ((((DAT_UnitsState.units[unitID].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[unitID].dying == 0)) &&
          (DAT_UnitsState.units[unitID].usingTeleport == 0)) &&
         ((DAT_UnitsState.units[unitID].field320_0x413 == 0 &&
          (DAT_UnitsState.units[unitID].moveableUnk != 0)))) {
                    /* fixme: this is some interesting data happening all over the unit code */
        if (targetType == STBT_0x3fd) {
LAB_00524621:
          if (targetType == STBT_0x3f2) {
            iVar5 = TroopValueState::findEnemyWalls(&DAT_TroopValueState,unitID);
LAB_00524638:
            tile = DAT_TroopValueState.tile;
            y = DAT_TroopValueState.y;
            uVar6 = DAT_TroopValueState.x;
            if (iVar5 != 0) {
              DAT_UnitsState.units[unitID].state.generic = US_MOVE_TO_DESTINATION;
              if (targetType != STBT_0x414) goto LAB_0052471e;
              uVar6 = UnitsState::findFreeTileNearby(&DAT_UnitsState,unitID,tile);
              if (uVar6 != 0) {
                UnitsState::setDestinationForUnit
                          (&DAT_UnitsState,unitID,
                           uVar6 - DAT_ViewportRenderState.translationMatrix
                                   [DAT_ViewportRenderState.tileTranslationMatrix_YComponent[uVar6]]
                                   .addXgetTile,
                           (int)DAT_ViewportRenderState.tileTranslationMatrix_YComponent[uVar6],0);
                sVar3 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[tile];
                DAT_UnitsState.units[unitID].attackAtTileY = sVar3;
                DAT_UnitsState.units[unitID].targetID_OR_targetBuildingID = (short)tile;
                iVar5 = DAT_ViewportRenderState.translationMatrix[sVar3].addXgetTile;
                DAT_UnitsState.units[unitID].targetingType = UIT_ATTACK_WALL;
                DAT_UnitsState.units[unitID].state.generic = US_MOVE_TO_DESTINATION;
                DAT_UnitsState.units[unitID].attackAtTileX = (short)tile - (short)iVar5;
              }
            }
          }
          else {
            if (targetType != STBT_0x3f4) {
              if (targetType == STBT_0x3f3) {
                iVar5 = TroopValueState::findNearestAvailableScalePoint(&DAT_TroopValueState,unitID)
                ;
              }
              else if (targetType == STBT_0x3f5) {
                iVar5 = TroopValueState::findEnemyBuildingsClosestToUnit
                                  (&DAT_TroopValueState,unitID);
              }
              else if (targetType == STBT_0x3fb) {
                iVar5 = TroopValueState::calculateTile2PeoplValueClosestToUnit
                                  (&DAT_TroopValueState,unitID);
              }
              else if (targetType == STBT_0x3fd) {
                iVar5 = TroopValueState::findEnemyLord(&DAT_TroopValueState,unitID);
              }
              else if (targetType == STBT_0x3f6) {
                iVar5 = TroopValueState::findEnemyTowersOrGates(&DAT_TroopValueState,unitID);
              }
              else if ((targetType == STBT_0x413) || (targetType == STBT_0x414)) {
                iVar5 = TroopValueState::getClosestWideValueBasedOnPlayer
                                  (&DAT_TroopValueState,unitID);
              }
              else {
                if (targetType != STBT_0x3f7) goto LAB_005247b0;
                iVar5 = TroopValueState::calculateTile2MoatValueClosestToUnit
                                  (&DAT_TroopValueState,unitID);
              }
              goto LAB_00524638;
            }
            iVar5 = TroopValueState::findNearestAvailableScalePoint(&DAT_TroopValueState,unitID);
            tile = DAT_TroopValueState.tile;
            y = DAT_TroopValueState.y;
            uVar6 = DAT_TroopValueState.x;
            if (iVar5 == 0) goto LAB_005247b0;
            DAT_UnitsState.units[unitID].state.generic = 0x67;
LAB_0052471e:
            sVar3 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[tile];
            DAT_UnitsState.units[unitID].attackAtTileY = sVar3;
            DAT_UnitsState.units[unitID].targetedBuildingTile = tile;
            DAT_UnitsState.units[unitID].attackAtTileX =
                 (short)tile - (short)DAT_ViewportRenderState.translationMatrix[sVar3].addXgetTile;
            DAT_UnitsState.units[unitID].unknownDigMoatOrWallAttackFlag1015 = (undefined2)targetType
            ;
            iVar5 = UnitsState::stopUnitIfNextToTarget(&DAT_UnitsState,unitID);
            if (iVar5 == 0) {
              if (BVar4 != FALSE) {
                DAT_PathFindingState.allAssassinsUnk = 1;
              }
              BVar7 = UnitsState::setDestinationForUnit(&DAT_UnitsState,unitID,uVar6,y,0);
              if (BVar7 == FALSE) {
                DAT_UnitsState.units[unitID].logicalState = ULS_REMOVE;
              }
            }
            if ((int)DAT_UnitsState.units[unitID].selectionTargetUnitID == unitID) {
              DAT_TribesState.tribes[tribeID].targetX = (short)uVar6;
              DAT_TribesState.tribes[tribeID].targetY = (short)y;
            }
          }
        }
        else {
          UVar1 = DAT_UnitsState.units[unitID].state.generic;
          if (((UVar1 != US_MELEE_ATTACK_WALL) && (UVar1 != US_MOVE_TO_DESTINATION)) &&
             (UVar1 != 0x67)) {
            UVar2 = DAT_UnitsState.units[unitID].unitType;
            if (UVar2 == UT_E_SPEAR) {
              bVar8 = UVar1 == US_AIM_WEAPONUnk;
            }
            else if (UVar2 == UT_E_ENGINEER) {
              bVar8 = UVar1 == US_RELOAD_WEAPONUnk;
            }
            else if (UVar2 == UT_E_LADDER) {
              bVar8 = UVar1 == 3;
            }
            else {
              if (UVar2 != UT_TUNNELER) goto LAB_00524621;
              if ((((UVar1 == 2) || (UVar1 == 3)) || (UVar1 == US_RELOAD_WEAPONUnk)) ||
                 (UVar1 == US_STAND_UPUnk)) goto LAB_005247b0;
              bVar8 = UVar1 == (US_STAND_UPUnk|US_IDLEUnk);
            }
            if (!bVar8) goto LAB_00524621;
          }
        }
      }
LAB_005247b0:
    } while (unitSelectionIndex < DAT_TribesState.tribes[tribeID].size);
  }
  return 1;
}


// ================= _HoldStrong::Map::Units::TribesState::sortTribePathDestinationsByCost @ 00524930 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::TribesState::sortTribePathDestinationsByCost
          (TribesState *this,int tribeID,int horseAndRamCount)

{
  short sVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  bool bVar5;
  BOOLEnum BVar6;
  int iVar7;
  int iVar8;
  uint y;
  PathFindingStatePartB *pPVar9;
  uint x;
  int iVar10;
  int *piVar11;
  
  BVar6 = isTribeAllAssassins(&DAT_TribesState,tribeID);
  sVar1 = DAT_TribesState.tribes[tribeID].selectionTargetUnitID;
  x = (uint)DAT_UnitsState.units[sVar1].x;
  if (horseAndRamCount == 0) {
    y = (uint)DAT_UnitsState.units[sVar1].y;
    if (BVar6 == FALSE) {
      Navigation::PathFindingState::findLinkageBasedPathOrWalkRadius
                (&DAT_PathFindingState,x,y,-1,-1,100000,FALSE);
    }
    else {
      Navigation::PathFindingState::pathFindingWithBuildingsIncluded
                (&DAT_PathFindingState,x,y,0xffffffff,0xffffffff,100000,0);
    }
  }
  else {
    Navigation::PathFindingState::calculatePathKeepAndWallsGatesNotAllowed
              (&DAT_PathFindingState,x,(int)DAT_UnitsState.units[sVar1].y,-1,-1,100000);
  }
  if (DAT_PathFindingState.searchQueue.destinationsArray[0].tile1 != 0) {
    pPVar9 = &DAT_PathFindingState.searchQueue;
    iVar7 = 0;
    iVar8 = 0;
    do {
      iVar10 = pPVar9->destinationsArray[0].tile1;
      if (DAT_TileMapState.WalkLayer[iVar10] == DAT_PathFindingState.searchGeneration) {
        *(int *)((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->
                       destinationsArray[0].tile3OrAnotherHelper + iVar7) =
             (int)DAT_TileMapState.CertainPathLayer[iVar10];
      }
      else {
        *(undefined4 *)
         ((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->destinationsArray
                [0].tile3OrAnotherHelper + iVar7) = 10000000;
      }
      iVar7 = iVar8 * 0xc + 0xc;
      iVar10 = iVar8 + 1;
      pPVar9 = (PathFindingStatePartB *)
               (((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->destinationsArray
               + iVar8 + 1);
      iVar8 = iVar8 + 1;
    } while (((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->destinationsArray
             [iVar10].tile1 != 0);
  }
  do {
    tribeID = 0;
    bVar5 = false;
    if (DAT_PathFindingState.searchQueue.destinationsArray[0].tile1 == 0) break;
    iVar7 = 0;
    do {
      iVar8 = *(int *)((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->
                             destinationsArray[0].tile2OrAHelper + iVar7);
      if (((iVar8 == 0) ||
          (iVar10 = *(int *)((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))
                                   ->destinationsArray[1].tile1 + iVar7), iVar10 == 0)) ||
         (iVar2 = *(int *)((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->
                                 destinationsArray[1].tile2OrAHelper + iVar7), iVar2 == 0)) break;
      iVar3 = *(int *)((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->
                             destinationsArray[0].tile3OrAnotherHelper + iVar7);
      iVar4 = *(int *)((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->
                             destinationsArray[1].tile3OrAnotherHelper + iVar7);
      if (iVar4 < iVar3) {
        *(undefined4 *)
         ((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->destinationsArray
                [1].tile1 + iVar7) =
             *(undefined4 *)
              ((int)&DAT_PathFindingState.searchQueue.destinationsArray[0].tile1 + iVar7);
        bVar5 = true;
        *(int *)((int)&DAT_PathFindingState.searchQueue.destinationsArray[0].tile1 + iVar7) = iVar10
        ;
        *(int *)((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->
                       destinationsArray[0].tile2OrAHelper + iVar7) = iVar2;
        *(int *)((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->
                       destinationsArray[1].tile2OrAHelper + iVar7) = iVar8;
        *(int *)((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->
                       destinationsArray[0].tile3OrAnotherHelper + iVar7) = iVar4;
        *(int *)((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->
                       destinationsArray[1].tile3OrAnotherHelper + iVar7) = iVar3;
      }
      iVar7 = tribeID * 0xc + 0xc;
      iVar8 = tribeID + 1;
      tribeID = tribeID + 1;
    } while (((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->destinationsArray
             [iVar8].tile1 != 0);
  } while (bVar5);
  iVar7 = 0;
  if (DAT_PathFindingState.searchQueue.destinationsArray[0].tile1 != 0) {
    pPVar9 = &DAT_PathFindingState.searchQueue;
    iVar8 = 0;
    piVar11 = &DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper;
    iVar10 = 0;
    do {
      if (*(int *)((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->
                         destinationsArray[0].tile3OrAnotherHelper + iVar8) != 10000000) {
        if (iVar10 != iVar7) {
          ((PathHelper12 *)(piVar11 + -1))->tile1 = pPVar9->destinationsArray[0].tile1;
          *piVar11 = *(int *)((int)&((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200)
                                    )->destinationsArray[0].tile2OrAHelper + iVar8);
          piVar11[1] = *(int *)((int)&((PathFindingStatePartB *)
                                      (DAT_PathFindingState.climbData + 200))->destinationsArray[0].
                                      tile3OrAnotherHelper + iVar8);
        }
        iVar7 = iVar7 + 1;
        piVar11 = piVar11 + 3;
      }
      iVar8 = iVar10 * 0xc + 0xc;
      iVar2 = iVar10 + 1;
      pPVar9 = (PathFindingStatePartB *)
               (((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->destinationsArray
               + iVar10 + 1);
      iVar10 = iVar10 + 1;
    } while (((PathFindingStatePartB *)(DAT_PathFindingState.climbData + 200))->destinationsArray
             [iVar2].tile1 != 0);
  }
  DAT_PathFindingState.searchQueue.destinationsArray[iVar7].tile1 = 0;
  return;
}


// ================= _HoldStrong::Map::Units::TribesState::giveTribeMoveInstruction @ 005263a0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Units::TribesState::giveTribeMoveInstruction
          (TribesState *this,int tribeID,uint x1,uint y1,int rallyBool,int storeAsRallyPoint,
          UnitMatchSpeedEnum speedMatching)

{
  ushort uVar1;
  UnitTypeShort UVar2;
  UnitStateShort UVar3;
  short sVar4;
  bool bVar5;
  bool bVar6;
  bool bVar7;
  bool bVar8;
  bool bVar9;
  uint y;
  uint y2;
  int iVar10;
  int iVar11;
  uint uVar12;
  undefined4 uVar13;
  BOOLEnum BVar14;
  uint x2;
  short sVar15;
  dword dVar16;
  int iVar17;
  bool bVar18;
  bool bVar19;
  int _tribeUnitIndex;
  int _algTile2;
  int _algTile;
  
  y = y1;
  bVar6 = false;
  _tribeUnitIndex = 0;
  bVar9 = false;
  _algTile2 = 0;
  _algTile = 0;
  bVar5 = false;
  if (x1 == 0) {
    if (y1 == 0) {
      return 0;
    }
  }
  else {
    if ((int)x1 < 0) {
      return 0;
    }
    if (399 < (int)x1) {
      return 0;
    }
  }
  if ((399 < y1) || (*(char *)(y1 * 400 + 0x21aec98 + x1) == '\0')) {
    return 0;
  }
  iVar17 = (int)DAT_TribesState.tribes[tribeID].selectionTargetUnitID;
  x2 = (uint)DAT_UnitsState.units[iVar17].x;
  y2 = (uint)DAT_UnitsState.units[iVar17].y;
  uVar1 = DAT_TileMapState.PathConnectionLayer
          [DAT_ViewportRenderState.translationMatrix[y2].addXgetTile + x2];
  iVar10 = DAT_ViewportRenderState.translationMatrix[y1].addXgetTile + x1;
  dVar16 = (dword)(short)DAT_TileMapState.PathConnectionLayer[iVar10];
  if ((DAT_TileMapState.LogicLayer[iVar10] & 0x30) == 0) {
    DAT_PathFindingState.field50_0x98 = 0;
    DAT_TribesState.fcn_mtribe = DAT_TribesState.fcn_mtribe + 1;
    iVar11 = getFirstUnitInTribeThatIsOnXTerrain(&DAT_TribesState,tribeID);
    if (iVar17 == iVar11) {
      uVar12 = Navigation::PathFindingState::canNavigateFunctionReturnsArea
                         (&DAT_PathFindingState,DAT_TribesState.tribes[tribeID].owner,dVar16,
                          (int)DAT_UnitsState.units[iVar17].x,(int)DAT_UnitsState.units[iVar17].y);
      if (uVar12 == 0) {
        uVar13 = applyMoveCommandOrRallyCommandToTribe
                           (&DAT_TribesState,tribeID,x1,y1,rallyBool,storeAsRallyPoint);
        return uVar13;
      }
      iVar17 = (int)DAT_TribesState.tribes[tribeID].selectionTargetUnitID;
      bVar6 = true;
    }
    else {
      uVar12 = (int)(short)uVar1;
      if ((int)(short)uVar1 == 0) {
        uVar13 = applyMoveCommandOrRallyCommandToTribe
                           (&DAT_TribesState,tribeID,x1,y1,rallyBool,storeAsRallyPoint);
        return uVar13;
      }
    }
                    /* WARNING: y1 now is area2 */
    y1 = uVar12;
    if (0 < (int)dVar16) {
      BVar14 = isTribeAllAssassins(&DAT_TribesState,tribeID);
      if (BVar14 == FALSE) {
        if (dVar16 != y1) {
          iVar11 = tribeContainsUnitThatCanClimb(&DAT_TribesState,tribeID);
          iVar11 = Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                             (&DAT_PathFindingState,DAT_TribesState.tribes[tribeID].owner,y1,dVar16,
                              iVar11);
          if (iVar11 == 0) {
            iVar11 = Navigation::PathFindingState::someBinaryAlgFunctionPathFinding
                               (&DAT_PathFindingState,iVar17);
            if (iVar11 == 0) {
              return 0;
            }
            iVar11 = Navigation::PathFindingState::findCrossAreaBridgeTileToTarget
                               (&DAT_PathFindingState,iVar17,x1,y);
            if (iVar11 == 0) {
              return 0;
            }
            bVar9 = true;
            _algTile2 = DAT_PathFindingState.ALG_TargetTile;
            _algTile = DAT_PathFindingState.ALG_ResultTile;
          }
          else {
            iVar11 = Navigation::PathFindingState::setClimbBasedOnClosestClimbData
                               (&DAT_PathFindingState,iVar17,y1,iVar11);
            if (iVar11 == 0) {
              return 0;
            }
          }
        }
      }
      else {
        bVar5 = true;
      }
      if (storeAsRallyPoint != 0) {
        DAT_TribesState.tribes[tribeID].isRallyingUnk = (short)rallyBool;
        DAT_TribesState.tribes[tribeID].rallyPointArray[0][0] = DAT_UnitsState.units[iVar17].x;
        DAT_TribesState.tribes[tribeID].rallyPointArray[0][1] = DAT_UnitsState.units[iVar17].y;
        DAT_TribesState.tribes[tribeID].rallyPointArray[1][0] = (short)x1;
        DAT_TribesState.tribes[tribeID].rallyPointArray[1][1] = (short)y;
        DAT_TribesState.tribes[tribeID].currentRallyPointIndex = 1;
        DAT_TribesState.tribes[tribeID].rallyPointCount = 2;
        DAT_TribesState.tribes[tribeID].field71_0x212 = 0;
      }
      DAT_TribesState.ALG_ResultTileIndex = 0;
      DAT_TribesState.field6_0x18 = 0;
      bVar18 = (DAT_TileMapState.LogicLayer[iVar10] & 0x100U) != 0;
      bVar8 = false;
      bVar19 = (DAT_TileMapState.LogicLayer[iVar10] & 0x10000000U) != 0;
      bVar7 = bVar19 || bVar18;
      rallyBool = 1;
      if (bVar5) {
        Navigation::PathFindingState::pathFindingWithBuildingsIncluded
                  (&DAT_PathFindingState,x1,y,0xffffffff,0xffffffff,500,0);
      }
      else if (bVar6) {
        Navigation::PathFindingState::findPathUsingClimbingWithHeightMargin16
                  (&DAT_PathFindingState,x1,y,0xffffffff,0xffffffff,500,FALSE);
      }
      else {
        Navigation::PathFindingState::findLinkageBasedPathOrWalkRadius
                  (&DAT_PathFindingState,x1,y,-1,-1,500,FALSE);
      }
      BVar14 = anyUnitsOfTribeAreOutsideCoverageOfPathFindingAlg
                         (&DAT_TribesState,tribeID,DAT_PathFindingState.searchGeneration);
      if (BVar14 == FALSE) {
        iVar10 = 500;
        do {
          iVar10 = iVar10 + 500;
          if ((0x13a0f < iVar10) || (((bVar6 || (bVar7)) && (7999 < iVar10)))) {
            if (DAT_PathFindingState.field50_0x98 == 0) {
              if (bVar5) {
                BVar14 = Navigation::PathFindingState::pathFindingWithBuildingsIncluded
                                   (&DAT_PathFindingState,x1,y,x2,y2,100000,0);
                if (BVar14 == FALSE) {
                  return 0;
                }
              }
              else if (bVar6) {
                BVar14 = Navigation::PathFindingState::findPathUsingClimbingWithHeightMargin16
                                   (&DAT_PathFindingState,x1,y,x2,y2,100000,FALSE);
                if (BVar14 == FALSE) {
                  return 0;
                }
              }
              else {
                BVar14 = Navigation::PathFindingState::findLinkageBasedPathOrWalkRadius
                                   (&DAT_PathFindingState,x1,y,x2,y2,100000,FALSE);
                if (BVar14 == FALSE) {
                  return 0;
                }
              }
            }
            applyMovementDistanceToUnitsInTribeBasedOnUnitNumberInTribe(&DAT_TribesState,tribeID);
            goto LAB_00526788;
          }
          rallyBool = DAT_PathFindingState.searchQueue.currentDistance;
          if (bVar5) {
            Navigation::PathFindingState::pathFindingWithBuildingsIncluded
                      (&DAT_PathFindingState,x1,y,0xffffffff,0xffffffff,iVar10,1);
          }
          else if (bVar6) {
            Navigation::PathFindingState::findPathUsingClimbingWithHeightMargin16
                      (&DAT_PathFindingState,x1,y,200,0,iVar10,TRUE);
          }
          else {
            Navigation::PathFindingState::findLinkageBasedPathOrWalkRadius
                      (&DAT_PathFindingState,x1,y,-1,-1,iVar10,TRUE);
          }
          BVar14 = anyUnitsOfTribeAreOutsideCoverageOfPathFindingAlg
                             (&DAT_TribesState,tribeID,DAT_PathFindingState.searchGeneration);
        } while (BVar14 == FALSE);
      }
      applyMovementDistanceToUnitsInTribe(&DAT_TribesState,tribeID);
LAB_00526788:
      if (0 < DAT_TribesState.tribes[tribeID].size) {
        do {
                    /* plan x and y for each unit in selection */
          iVar10 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_tribeUnitIndex);
          _tribeUnitIndex = _tribeUnitIndex + 1;
          if (((((((DAT_UnitsState.units[iVar10].logicalState == ULS_NORMAL) &&
                  (DAT_UnitsState.units[iVar10].dying == 0)) &&
                 ((DAT_UnitsState.units[iVar10].usingTeleport == 0 &&
                  ((DAT_UnitsState.units[iVar10].field320_0x413 == 0 &&
                   (DAT_UnitsState.units[iVar10].state.generic != 0xcf)))))) &&
                ((DAT_UnitsState.units[iVar10].rallyRelatedFlag == 0 &&
                 (((((DAT_UnitsState.units[iVar10].moveRelatedFlag != 1 &&
                     (DAT_UnitsState.units[iVar10].moveableUnk != 0)) &&
                    (UVar2 = DAT_UnitsState.units[iVar10].unitType, UVar2 != UT_S_TREBUCHET)) &&
                   ((UVar2 != UT_S_MANGONEL && (UVar2 != UT_S_BALLISTA)))) &&
                  ((UVar2 != UT_S_CATAPULT ||
                   (DAT_UnitsState.units[iVar10].
                    digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 2)))))
                 ))) && ((UVar2 != UT_S_FBALLISTA ||
                         (DAT_UnitsState.units[iVar10].
                          digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 ==
                          2)))) &&
              ((UVar2 != UT_S_TOWER ||
               (DAT_UnitsState.units[iVar10].
                digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 4)))) &&
             (((UVar2 != UT_S_BATTERINGRAM ||
               (DAT_UnitsState.units[iVar10].
                digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 4)) &&
              ((UVar2 != UT_S_SHIELD ||
               (DAT_UnitsState.units[iVar10].
                digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 1)))))) {
            if (UVar2 == UT_E_ENGINEER) {
              DAT_UnitsState.units[iVar10].field269_0x3c4 = 0;
            }
            if (bVar5) {
              if (!bVar19 && !bVar18) {
                if (bVar8) {
                  iVar17 = 3;
                }
                else {
                    /* fixme:ucp:feature?: change formations */
                  dVar16 = Navigation::PathFindingState::
                           findNextTileByModuloAmongPreviousSearchNotOnDefensiveStructure
                                     (&DAT_PathFindingState,3,x1,y);
                  DAT_TribesState.ALG_ResultTileIndex = DAT_TribesState.ALG_ResultTileIndex + 1;
                  if (dVar16 != 0) goto LAB_0052691a;
                  bVar8 = true;
                  DAT_TribesState.ALG_ResultTileIndex = 0;
                  iVar17 = 3;
                }
                goto LAB_0052690c;
              }
              if (bVar8) {
LAB_00526908:
                iVar17 = 1;
                goto LAB_0052690c;
              }
              dVar16 = Navigation::PathFindingState::pathFindingResultBased
                                 (&DAT_PathFindingState,1,x1,y,rallyBool);
              DAT_TribesState.ALG_ResultTileIndex = DAT_TribesState.ALG_ResultTileIndex + 1;
              if (dVar16 == 0) {
                bVar8 = true;
                DAT_TribesState.ALG_ResultTileIndex = 0;
                goto LAB_00526908;
              }
            }
            else {
              if (DAT_TribesState.tribes[tribeID].unkIsAnimalTribe == 0) {
                if ((bVar7) || (bVar6)) goto LAB_00526908;
                if (((UVar2 == UT_S_CATAPULT) ||
                    (((UVar2 == UT_S_FBALLISTA || (UVar2 == UT_S_TOWER)) ||
                     (UVar2 == UT_S_BATTERINGRAM)))) || (UVar2 == UT_S_SHIELD)) {
                  iVar17 = 4;
                }
                else {
                  iVar17 = 2;
                }
              }
              else {
                iVar17 = 3;
              }
LAB_0052690c:
              Navigation::PathFindingState::findNextTileInExistingSearchThatIsModuloDistanceAway
                        (&DAT_PathFindingState,iVar17,x1,y);
              DAT_TribesState.ALG_ResultTileIndex = DAT_TribesState.ALG_ResultTileIndex + 1;
            }
LAB_0052691a:
            if (3999 < DAT_TribesState.ALG_ResultTileIndex) break;
            DAT_UnitsState.units[iVar10].plannedDestinationX = (short)DAT_TribesState.ALG_ResultX;
            DAT_UnitsState.units[iVar10].plannedDestinationY = (short)DAT_TribesState.ALG_ResultY;
          }
        } while (_tribeUnitIndex < DAT_TribesState.tribes[tribeID].size);
      }
      iVar10 = 0;
      if (0 < DAT_TribesState.tribes[tribeID].size) {
        do {
          iVar17 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar10);
          iVar10 = iVar10 + 1;
          if ((((((((DAT_UnitsState.units[iVar17].logicalState == ULS_NORMAL) &&
                   (DAT_UnitsState.units[iVar17].dying == 0)) &&
                  ((DAT_UnitsState.units[iVar17].usingTeleport == 0 &&
                   ((DAT_UnitsState.units[iVar17].field320_0x413 == 0 &&
                    (UVar3 = DAT_UnitsState.units[iVar17].state.generic, UVar3 != 0xcf)))))) &&
                 (DAT_UnitsState.units[iVar17].rallyRelatedFlag == 0)) &&
                (((DAT_UnitsState.units[iVar17].moveRelatedFlag != 1 &&
                  (DAT_UnitsState.units[iVar17].moveableUnk != 0)) &&
                 (UVar2 = DAT_UnitsState.units[iVar17].unitType, UVar2 != UT_S_TREBUCHET)))) &&
               (((UVar2 != UT_S_MANGONEL && (UVar2 != UT_S_BALLISTA)) &&
                ((UVar2 != UT_S_CATAPULT ||
                 (DAT_UnitsState.units[iVar17].
                  digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 2))))))
              && (((UVar2 != UT_S_FBALLISTA ||
                   (DAT_UnitsState.units[iVar17].
                    digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 2)) &&
                  ((UVar2 != UT_S_TOWER ||
                   (DAT_UnitsState.units[iVar17].
                    digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 4)))))
              ) && (((UVar2 != UT_S_BATTERINGRAM ||
                     (DAT_UnitsState.units[iVar17].
                      digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 4))
                    && ((UVar2 != UT_S_SHIELD ||
                        (DAT_UnitsState.units[iVar17].
                         digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 1
                        )))))) {
            if (UVar3 == US_MELEE_ATTACK) {
              DAT_UnitsState.units[iVar17].unknownMovementRelated_0x2d2 =
                   DAT_UnitsState.units[iVar17].movementSpeed * -4;
            }
            DAT_UnitsState.units[iVar17].state.generic = US_MOVE_TO_DESTINATION;
            DAT_UnitsState.units[iVar17].movementType_OR_targetUnitID = 0;
            DAT_UnitsState.units[iVar17].targetedBuildingTile = 0;
            if (bVar5) {
              DAT_PathFindingState.allAssassinsUnk = 1;
            }
            else if (bVar6) {
              DAT_PathFindingState.notAllAssassinsUnk = 0;
            }
            else {
              DAT_PathFindingState.notAllAssassinsUnk = (uint)(DAT_EntityState.fireCount == 0);
            }
            DAT_UnitsState.units[iVar17]._someX_2 = 0;
            DAT_UnitsState.units[iVar17]._someY_2 = 0;
            Synchrony::GameSynchronyState::throttledMultiplayerSyncUpdate(&DAT_GameSynchronyState);
            if ((((UVar3 == US_MELEE_ATTACK) ||
                 (DAT_UnitsState.units[iVar17].plannedDestinationX !=
                  DAT_UnitsState.units[iVar17].destinationXPosition)) ||
                (DAT_UnitsState.units[iVar17].plannedDestinationY !=
                 DAT_UnitsState.units[iVar17].destinationYPosition)) ||
               (DAT_UnitsState.units[iVar17].tunnelerFinishedDigging != 2)) {
              BVar14 = UnitsState::setDestinationForUnit
                                 (&DAT_UnitsState,iVar17,
                                  (int)DAT_UnitsState.units[iVar17].plannedDestinationX,
                                  (int)DAT_UnitsState.units[iVar17].plannedDestinationY,0);
              if (BVar14 == FALSE) {
                if ((bVar9) &&
                   ((DAT_TileMapState.LogicLayer[DAT_UnitsState.units[iVar17].tile] & 0x10000100U)
                    != 0)) {
                    /* teleport? */
                  UnitsState::setDestinationForUnit
                            (&DAT_UnitsState,iVar17,
                             _algTile2 -
                             DAT_ViewportRenderState.translationMatrix
                             [DAT_ViewportRenderState.tileTranslationMatrix_YComponent[_algTile2]].
                             addXgetTile,
                             (int)DAT_ViewportRenderState.tileTranslationMatrix_YComponent
                                  [_algTile2],0);
                  DAT_UnitsState.units[iVar17].state.generic = US_APPEAR;
                  DAT_UnitsState.units[iVar17].
                  targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID
                       = _algTile;
                  goto LAB_00526ce4;
                }
              }
              else {
LAB_00526ce4:
                if (speedMatching != UMSE_0) goto LAB_00526cea;
              }
            }
            else {
LAB_00526cea:
              DAT_UnitsState.units[iVar17].unitSpeedMatchingRelatedUnk = 0x10;
            }
            DAT_PathFindingState.notAllAssassinsUnk = 0;
            if (DAT_PathFindingState.field43_0x7c == 0) {
              DAT_TribesState.field6_0x18 = DAT_TribesState.field6_0x18 + 1;
            }
            else {
              DAT_TribesState.field6_0x18 = DAT_TribesState.field6_0x18 + -1;
            }
          }
        } while (iVar10 < DAT_TribesState.tribes[tribeID].size);
      }
      applyUnitTopSpeedDelayBasedOnTribeSize(&DAT_TribesState,tribeID,FALSE);
      iVar10 = 0;
      sVar4 = DAT_TribesState.tribes[tribeID].size;
      DAT_TribesState.tribes[tribeID].someUnitID = 0;
      if (0 < sVar4) {
        do {
                    /* set move delay */
          iVar17 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar10);
          iVar10 = iVar10 + 1;
          if ((((((DAT_UnitsState.units[iVar17].logicalState == ULS_NORMAL) &&
                 (DAT_UnitsState.units[iVar17].dying == 0)) &&
                ((DAT_UnitsState.units[iVar17].usingTeleport == 0 &&
                 (((DAT_UnitsState.units[iVar17].field320_0x413 == 0 &&
                   (DAT_UnitsState.units[iVar17].state.generic != 0xcf)) &&
                  (DAT_UnitsState.units[iVar17].rallyRelatedFlag == 0)))))) &&
               (((DAT_UnitsState.units[iVar17].moveRelatedFlag != 1 &&
                 (DAT_UnitsState.units[iVar17].moveableUnk != 0)) &&
                ((UVar2 = DAT_UnitsState.units[iVar17].unitType, UVar2 != UT_S_TREBUCHET &&
                 ((((UVar2 != UT_S_MANGONEL && (UVar2 != UT_S_BALLISTA)) &&
                   ((UVar2 != UT_S_CATAPULT ||
                    (DAT_UnitsState.units[iVar17].
                     digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 2))))
                  && ((UVar2 != UT_S_FBALLISTA ||
                      (DAT_UnitsState.units[iVar17].
                       digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 2))
                     )))))))) &&
              ((UVar2 != UT_S_TOWER ||
               (DAT_UnitsState.units[iVar17].
                digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 4)))) &&
             (((UVar2 != UT_S_BATTERINGRAM ||
               (DAT_UnitsState.units[iVar17].
                digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 4)) &&
              ((UVar2 != UT_S_SHIELD ||
               (DAT_UnitsState.units[iVar17].
                digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 1)))))) {
            sVar4 = DAT_UnitsState.units[iVar17].topSpeedDelayIndex;
            sVar15 = (short)DAT_UnitSelectionDefinedData.DAT_UnitInstructionMoveDelay[sVar4];
            if (DAT_TribesState.tribes[tribeID].unkIsAnimalTribe == 0) {
              if (-1 < DAT_TribesState.field6_0x18) {
                sVar15 = sVar15 * 2;
              }
            }
            else {
              sVar15 = sVar15 * 3;
            }
            DAT_UnitsState.units[iVar17].moveInstructionSpeedDelayTracker = sVar15;
            if (DAT_TribesState.field6_0x18 < 0) {
              DAT_UnitsState.units[iVar17].moveDelay = 0;
            }
            else {
              DAT_UnitsState.units[iVar17].moveDelay =
                   (short)(DAT_UnitSelectionDefinedData.DAT_UnitMoveDelay[sVar4] / 2);
            }
            if (DAT_UnitsState.units[iVar17].unknownMovementRelated_0x2d2 != 0) {
              DAT_UnitsState.units[iVar17].moveDelay = 0;
            }
            DAT_UnitsState.units[iVar17].moveInstructionSpeedDelayTracker = 0;
            DAT_UnitsState.units[iVar17].moveDelay = 0;
            DAT_UnitsState.units[iVar17].horseArcherShootingVariation = 0;
            DAT_UnitsState.units[iVar17].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
          }
        } while (iVar10 < DAT_TribesState.tribes[tribeID].size);
      }
      return 1;
    }
  }
  return 0;
}


// ================= _HoldStrong::Map::Units::TribesState::giveTribeAnInstruction @ 00527c80 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* gynt: unitID and x and y and tile are the target of the instruction
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Units::TribesState::giveTribeAnInstruction
          (TribesState *this,int tribeID,UnitInstructionType unitInstructionType,int id_x_tile,
          int unitUID_Y,int param_5)

{
  short *psVar1;
  byte bVar2;
  UnitStateShort UVar3;
  UnitTypeShort UVar4;
  ushort uVar5;
  Unit *pUVar6;
  char cVar7;
  short sVar8;
  short sVar9;
  UnitInstructionType UVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  int iVar14;
  int iVar15;
  undefined3 extraout_var;
  BOOLEnum BVar16;
  uint uVar17;
  uint x;
  int iVar18;
  short sVar19;
  int *piVar20;
  uint y;
  uint uVar21;
  bool bVar22;
  int _unitTribeIndex;
  int _ramOrHorse;
  uint local_8;
  dword _param_4_unitUID_Y_copy;
  
  iVar12 = unitUID_Y;
  iVar11 = id_x_tile;
  iVar18 = tribeID;
  sVar9 = DAT_TribesState.tribes[tribeID].size;
  _param_4_unitUID_Y_copy = unitUID_Y;
  _ramOrHorse = 0;
  local_8 = 0;
  bVar22 = false;
  DAT_TribesState.tribes[tribeID].someUnitID = 0;
  DAT_TribesState.tribes[tribeID].field71_0x212 = 0;
  sVar19 = (short)id_x_tile;
  switch(unitInstructionType) {
  case UIT_NO_INSTRUCTION_OR_MOVEUnk:
    iVar11 = 0;
    if (0 < sVar9) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,iVar18,iVar11);
        iVar11 = iVar11 + 1;
        if ((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[iVar12].dying == 0)) {
          DAT_UnitsState.units[iVar12].field270_0x3c5 = 3;
          DAT_UnitsState.units[iVar12].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
          DAT_UnitsState.units[iVar12].field260_0x3b0 = 0;
        }
      } while (iVar11 < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
    break;
  case UIT_UNIT_ATTACK_UNIT:
                    /* unit attack target */
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    pUVar6 = DAT_UnitsState.units + id_x_tile;
    _unitTribeIndex = 0;
                    /* repurposed parameter: counts amount of melee units */
    id_x_tile = 0;
    if (pUVar6->uid != unitUID_Y) {
      return 0;
    }
    if (0 < sVar9) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if (((DAT_UnitsState.units[iVar12].logicalState != ULS_NORMAL) ||
            (DAT_UnitsState.units[iVar12].dying != 0)) ||
           (DAT_UnitsState.units[iVar12].field320_0x413 != 0)) goto switchD_00527ea5_caseD_6;
        DAT_UnitsState.units[iVar12]._someX_2 = 0;
        DAT_UnitsState.units[iVar12]._someY_2 = 0;
        switch(DAT_UnitsState.units[iVar12].unitType) {
        case UT_TUNNELER:
        case UT_E_SPEAR:
        case UT_E_PIKE:
        case UT_E_MACE:
        case UT_E_SWORD:
        case UT_E_KNIGHT:
        case UT_E_MONK:
        case UT_LORD:
        case UT_A_SLAVE:
        case UT_A_ASSASSIN:
        case UT_A_SWORDSMAN:
                    /* melee units */
          if ((DAT_UnitsState.units[iVar11].unitType != UT_ANTELOPESHDEER) &&
             ((param_5 != 1 || (DAT_UnitsState.units[iVar11].state.generic != US_MELEE_ATTACK)))) {
            id_x_tile = id_x_tile + 1;
          }
          break;
        case UT_E_ARCHER:
        case UT_E_XBOW:
        case UT_A_ARCHER:
        case UT_A_SLINGER:
        case UT_A_HARCHER:
        case UT_A_FIRETHROWER:
                    /* ranged units */
          if (DAT_UnitsState.units[iVar12].state.generic == 0x69) {
            DAT_UnitsState.units[iVar12].state.generic = US_MOVE_TO_DESTINATION;
          }
          DAT_UnitsState.units[iVar12].
          targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
               unitUID_Y;
          DAT_UnitsState.units[iVar12].targetUID = unitUID_Y;
          DAT_UnitsState.units[iVar12].targetingType = UIT_UNIT_ATTACK_UNIT;
          DAT_UnitsState.units[iVar12].targetedUnitID__OR__engineerMannedSiegeEngineRef = sVar19;
          DAT_UnitsState.units[iVar12].shootTargetedUnit = sVar19;
          DAT_UnitsState.units[iVar12].field300_0x3f8 = 0;
          UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
          goto LAB_00527ee1;
        case UT_S_CATAPULT:
        case UT_S_TREBUCHET:
          DAT_UnitsState.units[iVar12].field270_0x3c5 = 5;
          DAT_UnitsState.units[iVar12].targetingType = UIT_ATTACK_LAND;
          DAT_UnitsState.units[iVar12].attackAtTileX = DAT_UnitsState.units[iVar11].x;
          DAT_UnitsState.units[iVar12].attackAtTileY = DAT_UnitsState.units[iVar11].y;
          DAT_UnitsState.units[iVar12].unkAttackRelated = 0xb;
          DAT_UnitsState.units[iVar12].shootBeforeStop = 10;
          break;
        case UT_S_MANGONEL:
        case UT_S_BALLISTA:
        case UT_S_FBALLISTA:
          DAT_UnitsState.units[iVar12].targetingType = UIT_UNIT_ATTACK_UNIT;
          DAT_UnitsState.units[iVar12].targetedUnitID__OR__engineerMannedSiegeEngineRef = sVar19;
          DAT_UnitsState.units[iVar12].
          targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
               unitUID_Y;
          DAT_UnitsState.units[iVar12].field300_0x3f8 = 0;
          UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
          DAT_UnitsState.units[iVar12].shootBeforeStop = 10;
LAB_00527ee1:
          if (DAT_UnitsState.units[iVar11].unitType == UT_RABBIT) {
            DAT_TribesState.tribes[iVar18].field71_0x212 = 1;
          }
        }
switchD_00527ea5_caseD_6:
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
      if (id_x_tile != 0) {
                    /* if there are melee units in the selection */
        iVar12 = (int)DAT_TribesState.tribes[iVar18].selectionTargetUnitID;
        local_8 = (uint)DAT_UnitsState.units[iVar12].x;
        unitInstructionType = (UnitInstructionType)DAT_UnitsState.units[iVar12].y;
        predictUnitInterceptPosition
                  (&DAT_TribesState,iVar12,iVar11,(int *)&local_8,(int *)&unitInstructionType);
        Navigation::PathFindingState::pathPlanningForTribe
                  (&DAT_PathFindingState,tribeID,iVar11,local_8,unitInstructionType,id_x_tile,
                   (int)(short)DAT_TileMapState.PathConnectionLayer
                               [DAT_UnitsState.units[iVar12].tile],
                   (int)DAT_UnitsState.units[iVar12].owner);
        DAT_TribesState.tribes[iVar18].someUnitID = sVar19;
        DAT_TribesState.tribes[iVar18].someUnitUID = unitUID_Y;
        DAT_TribesState.tribes[iVar18].someTile = DAT_UnitsState.units[iVar11].tile;
        iVar12 = 0;
        sVar9 = DAT_TribesState.tribes[iVar18].size;
        DAT_TribesState.tribes[iVar18].someTile2 =
             (int)DAT_UnitsState.units[iVar11].destinationX_2Unk +
             DAT_ViewportRenderState.translationMatrix
             [DAT_UnitsState.units[iVar11].destinationY_2Unk].addXgetTile;
        unitInstructionType = 0;
        if (0 < sVar9) {
          id_x_tile = 0x12d5c6c;
          do {
            iVar11 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar12);
            iVar12 = iVar12 + 1;
            if (((DAT_UnitsState.units[iVar11].logicalState == ULS_NORMAL) &&
                (DAT_UnitsState.units[iVar11].dying == 0)) &&
               (DAT_UnitsState.units[iVar11].field320_0x413 == 0)) {
              UVar4 = DAT_UnitsState.units[iVar11].unitType;
              switch(UVar4) {
              case UT_TUNNELER:
              case UT_E_SPEAR:
              case UT_E_PIKE:
              case UT_E_MACE:
              case UT_E_SWORD:
              case UT_E_KNIGHT:
              case UT_E_MONK:
              case UT_LORD:
              case UT_A_SLAVE:
              case UT_A_ASSASSIN:
              case UT_A_SWORDSMAN:
                if (((param_5 != 1) ||
                    (DAT_UnitsState.units[iVar11].state.generic != US_MELEE_ATTACK)) &&
                   (iVar14 = *(int *)id_x_tile, iVar14 != 0)) {
                  sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar14];
                  uVar13 = iVar14 - DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
                  if (*(int *)(id_x_tile + 4) == 0) {
                    DAT_UnitsState.units[iVar11].targetingType = 0;
                    if (UVar4 == UT_LORD) break;
                  }
                  else {
                    DAT_UnitsState.units[iVar11].targetingType = UIT_UNIT_ATTACK_UNIT;
                    DAT_UnitsState.units[iVar11].targetedUnitID__OR__engineerMannedSiegeEngineRef =
                         sVar19;
                    DAT_UnitsState.units[iVar11].
                    targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID
                         = unitUID_Y;
                  }
                  UVar3 = DAT_UnitsState.units[iVar11].state.generic;
                  DAT_UnitsState.units[iVar11].plannedDestinationX = (short)uVar13;
                  DAT_UnitsState.units[iVar11].plannedDestinationY = sVar9;
                  DAT_UnitsState.units[iVar11].targetedBuildingTile = 0;
                  DAT_UnitsState.units[iVar11].movementType_OR_targetUnitID = 0;
                  if (UVar3 == US_MELEE_ATTACK) {
                    DAT_UnitsState.units[iVar11].unknownMovementRelated_0x2d2 =
                         DAT_UnitsState.units[iVar11].movementSpeed * -4;
                  }
                  DAT_UnitsState.units[iVar11].state.generic = US_MOVE_TO_DESTINATION;
                  BVar16 = isTribeAllAssassins(&DAT_TribesState,tribeID);
                  if (BVar16 == FALSE) {
                    DAT_PathFindingState.notAllAssassinsUnk = 1;
                  }
                  else {
                    DAT_PathFindingState.allAssassinsUnk = 1;
                  }
                  UnitsState::setDestinationForUnit(&DAT_UnitsState,iVar11,uVar13,(int)sVar9,0);
                  UVar10 = (int)DAT_UnitsState.units[iVar11].totalSizeOfPathPlan / 2;
                  DAT_UnitsState.units[iVar11].lookForEnemy = -0x32;
                  if ((int)unitInstructionType < (int)UVar10) {
                    unitInstructionType = UVar10;
                  }
                  id_x_tile = id_x_tile + 0xc;
                  DAT_PathFindingState.notAllAssassinsUnk = 0;
                }
              }
            }
          } while (iVar12 < DAT_TribesState.tribes[iVar18].size);
        }
        iVar11 = unitInstructionType * 8;
        if (iVar11 < 9) {
          iVar11 = 8;
        }
        DAT_TribesState.tribes[iVar18].field168_0x2be = (short)iVar11;
        return 1;
      }
    }
    break;
  case UIT_ATTACK_LAND:
  case UIT_THROW_COW:
    unitUID_Y = DAT_TribesState.tribes[tribeID].owner;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    _unitTribeIndex = 0;
    if (0 < sVar9) {
      do {
        iVar14 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if ((DAT_UnitsState.units[iVar14].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[iVar14].dying == 0)) {
          switch(DAT_UnitsState.units[iVar14].unitType) {
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_E_ARCHER_DEBUG:
          case UT_S_MANGONEL:
          case UT_S_BALLISTA:
          case UT_A_ARCHER:
          case UT_A_SLINGER:
          case UT_A_HARCHER:
          case UT_A_FIRETHROWER:
          case UT_S_FBALLISTA:
            if (DAT_UnitsState.units[iVar14].state.generic == 0x69) {
              DAT_UnitsState.units[iVar14].state.generic = US_MOVE_TO_DESTINATION;
            }
            DAT_UnitsState.units[iVar14].field300_0x3f8 = 0;
            DAT_UnitsState.units[iVar14].targetingType =
                 (UnitInstructionTypeShort)unitInstructionType;
LAB_00528808:
            DAT_UnitsState.units[iVar14].field270_0x3c5 = (byte)unitInstructionType;
            sVar9 = (short)iVar12;
            if ((unitInstructionType == UIT_THROW_COW) &&
               ((UVar4 = DAT_UnitsState.units[iVar14].unitType, UVar4 == UT_S_CATAPULT ||
                (UVar4 == UT_S_TREBUCHET)))) {
              if (DAT_GameState.playerDataArray[unitUID_Y].counter < 1) {
                DAT_UnitsState.units[iVar14].field270_0x3c5 = 5;
              }
              else {
                DAT_UnitsState.units[iVar14].targetingType = UIT_THROW_COW;
                DAT_UnitsState.units[iVar14].shootTargetMicroX = sVar19 * 8;
                DAT_UnitsState.units[iVar14].shootTargetMicroY = sVar9 * 8;
                DAT_UnitsState.units[iVar14].shootTargetZ =
                     (ushort)*(byte *)(DAT_ViewportRenderState.translationMatrix[iVar12].addXgetTile
                                       + 0x1d32c38 + iVar11);
              }
            }
            DAT_UnitsState.units[iVar14].attackAtTileX = sVar19;
            DAT_UnitsState.units[iVar14].attackAtTileY = sVar9;
            DAT_UnitsState.units[iVar14].unkAttackRelated = (short)param_5;
            DAT_UnitsState.units[iVar14]._someX_2 = 0;
            DAT_UnitsState.units[iVar14]._someY_2 = 0;
            UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar14);
            DAT_UnitsState.units[iVar14].shootBeforeStop = 10;
            break;
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
            if (DAT_UnitsState.units[iVar14].
                digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 != 0)
            goto LAB_00528808;
          }
        }
        if (DAT_TribesState.tribes[iVar18].size <= _unitTribeIndex) {
          return 1;
        }
      } while( true );
    }
    break;
  case UIT_FILL_MOAT:
    uVar5 = DAT_TileMapState.PathConnectionLayer
            [DAT_UnitsState.units[DAT_TribesState.tribes[tribeID].selectionTargetUnitID].tile];
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    if ((int)(short)uVar5 != 0) {
      iVar11 = Navigation::PathFindingState::canNavigateFunctionReturnsArea
                         (&DAT_PathFindingState,DAT_TribesState.tribes[tribeID].owner,
                          (int)(short)uVar5,id_x_tile,unitUID_Y);
      if (iVar11 == 0) {
        return 1;
      }
      unitUID_Y = DAT_PathFindingState.climbY;
      iVar11 = DAT_PathFindingState.climbX;
    }
  case UIT_DIG_MOAT:
    iVar12 = unitUID_Y;
    iVar14 = 0;
    DAT_TribesState.tribes[iVar18].isRallyingUnk = 0;
    giveUnitSelectionMoveInstructionNoMatchedSpeed(&DAT_TribesState,tribeID,iVar11,unitUID_Y,0,1);
    if (0 < DAT_TribesState.tribes[iVar18].size) {
      do {
        iVar15 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar14);
        iVar14 = iVar14 + 1;
        if ((DAT_UnitsState.units[iVar15].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[iVar15].dying == 0)) {
          switch(DAT_UnitsState.units[iVar15].unitType) {
          case UT_E_ARCHER:
          case UT_E_SPEAR:
          case UT_E_PIKE:
          case UT_E_MACE:
          case UT_E_ENGINEER:
          case UT_A_SLAVE:
            if (DAT_UnitsState.units[iVar15].state.generic == 0x69) {
              DAT_UnitsState.units[iVar15].state.generic = US_MOVE_TO_DESTINATION;
            }
            DAT_UnitsState.units[iVar15].targetingType = (undefined2)unitInstructionType;
            DAT_UnitsState.units[iVar15].attackAtTileX = (short)iVar11;
            DAT_UnitsState.units[iVar15].attackAtTileY = (short)iVar12;
            DAT_UnitsState.units[iVar15].targetX = sVar19;
            DAT_UnitsState.units[iVar15].targetY = (UnitStateShort)_param_4_unitUID_Y_copy;
            DAT_UnitsState.units[iVar15].targetedBuildingTile = 0;
            DAT_UnitsState.units[iVar15].movementType_OR_targetUnitID = 0;
            DAT_UnitsState.units[iVar15]._someX_2 = 0;
            DAT_UnitsState.units[iVar15]._someY_2 = 0;
          }
        }
      } while (iVar14 < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
    break;
  case UIT_ATTACK_BUILDING:
  case 0x24:
  case 0x26:
    _unitTribeIndex = 0;
    id_x_tile = 0;
    DAT_TribesState.tribes[tribeID].targetBuildingID = sVar19;
    DAT_TribesState.tribes[tribeID].targetBuildingUID = unitUID_Y;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    if (0 < sVar9) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if (((DAT_UnitsState.units[iVar12].logicalState != ULS_NORMAL) ||
            (DAT_UnitsState.units[iVar12].dying != 0)) ||
           (DAT_UnitsState.units[iVar12].field320_0x413 != 0)) goto switchD_00528b77_caseD_6;
        DAT_UnitsState.units[iVar12]._someX_2 = 0;
        DAT_UnitsState.units[iVar12]._someY_2 = 0;
        switch(DAT_UnitsState.units[iVar12].unitType) {
        case UT_E_ARCHER:
        case UT_E_XBOW:
        case UT_A_ARCHER:
        case UT_A_SLINGER:
        case UT_A_FIRETHROWER:
          goto switchD_00528b77_caseD_16;
        case UT_E_KNIGHT:
          if (DAT_BuildingsState.buildings[iVar11].buildingType != BT_PITCHDITCH) {
            _ramOrHorse = _ramOrHorse + 1;
          }
        case UT_TUNNELER:
        case UT_E_SPEAR:
        case UT_E_PIKE:
        case UT_E_MACE:
        case UT_E_SWORD:
        case UT_E_MONK:
        case UT_LORD:
        case UT_A_SLAVE:
        case UT_A_ASSASSIN:
        case UT_A_SWORDSMAN:
switchD_00528b77_caseD_5:
          if (DAT_BuildingsState.buildings[iVar11].buildingType != BT_PITCHDITCH) {
            id_x_tile = id_x_tile + 1;
          }
          break;
        case UT_S_CATAPULT:
        case UT_S_TREBUCHET:
        case UT_S_MANGONEL:
        case UT_S_BALLISTA:
        case UT_S_FBALLISTA:
          if ((unitInstructionType == 0x26) ||
             (DAT_BuildingsState.buildings[iVar11].buildingType == BT_PITCHDITCH)) break;
          DAT_UnitsState.units[iVar12].targetID_OR_targetBuildingID = sVar19;
          DAT_UnitsState.units[iVar12].
          targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
               unitUID_Y;
          goto LAB_00528c46;
        case UT_S_BATTERINGRAM:
          if ((DAT_BuildingsState.buildings[iVar11].buildingType != BT_PITCHDITCH) &&
             (DAT_UnitsState.units[iVar12].
              digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 4)) {
            id_x_tile = id_x_tile + 1;
            _ramOrHorse = _ramOrHorse + 1;
          }
          break;
        case UT_A_HARCHER:
          _ramOrHorse = _ramOrHorse + 1;
switchD_00528b77_caseD_16:
          if (unitInstructionType == 0x24) {
            switch(DAT_BuildingsState.buildings[iVar11].buildingType) {
            case BT_GATEHOUSELARGE:
            case BT_GATEHOUSESMALL:
            case BT_WOODGATE1:
            case BT_WOODGATE2:
            case BT_TOWER1:
            case BT_TOWER2:
            case BT_TOWER3:
            case BT_TOWER4:
            case BT_TOWER5:
              goto switchD_00528bae_caseD_2d;
            }
            goto switchD_00528b77_caseD_5;
          }
          if (unitInstructionType != 0x26) {
switchD_00528bae_caseD_2d:
                    /* attack buildings */
            if (DAT_UnitsState.units[iVar12].state.generic == 0x69) {
              DAT_UnitsState.units[iVar12].state.generic = US_MOVE_TO_DESTINATION;
            }
            sVar8 = (short)((int)(DAT_BuildingsState.buildings[iVar11].widthOrHeight * 8) / 2);
            DAT_UnitsState.units[iVar12].shootTargetMicroX =
                 DAT_BuildingsState.buildings[iVar11].x * 8 + sVar8;
            sVar9 = DAT_BuildingsState.buildings[iVar11].terrainHeightUnk;
            DAT_UnitsState.units[iVar12].shootTargetMicroY =
                 DAT_BuildingsState.buildings[iVar11].y * 8 + sVar8;
            DAT_UnitsState.units[iVar12].shootTargetZ = sVar9;
            DAT_UnitsState.units[iVar12].shootTargetedUnit = -1;
            DAT_UnitsState.units[iVar12].targetID_OR_targetBuildingID = sVar19;
            DAT_UnitsState.units[iVar12].
            targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
                 unitUID_Y;
LAB_00528c46:
            DAT_UnitsState.units[iVar12].field270_0x3c5 = 9;
            DAT_UnitsState.units[iVar12].targetingType = UIT_ATTACK_BUILDING;
            DAT_UnitsState.units[iVar12].field300_0x3f8 = 0;
            UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
            DAT_UnitsState.units[iVar12].shootBeforeStop = 10;
          }
        }
switchD_00528b77_caseD_6:
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
    }
    if ((((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
         (DAT_GameState.mapAndTime.strongWalls2 == 0)) ||
        (4 < (int)(short)DAT_BuildingsState.buildings[iVar11].buildingType - 0x4aU)) &&
       (id_x_tile != 0)) {
      sVar9 = DAT_TribesState.tribes[iVar18].selectionTargetUnitID;
      if ((unitInstructionType == UIT_ATTACK_BUILDING) || (unitInstructionType == 0x26)) {
        iVar12 = (int)DAT_UnitsState.units[sVar9].owner;
      }
      else {
        iVar12 = 0;
      }
      Navigation::PathFindingState::pathfindingForAttacksUnk
                (&DAT_PathFindingState,tribeID,iVar11,id_x_tile,
                 (int)(short)DAT_TileMapState.PathConnectionLayer[DAT_UnitsState.units[sVar9].tile],
                 iVar12);
      sortTribePathDestinationsByCost(&DAT_TribesState,tribeID,_ramOrHorse);
      if ((DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper != 0) &&
         (_unitTribeIndex = 0, 0 < DAT_TribesState.tribes[iVar18].size)) {
        id_x_tile = 0x12d5c70;
        do {
          iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
          _unitTribeIndex = _unitTribeIndex + 1;
          if (((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
              (DAT_UnitsState.units[iVar12].dying == 0)) &&
             (DAT_UnitsState.units[iVar12].field320_0x413 == 0)) {
            UVar4 = DAT_UnitsState.units[iVar12].unitType;
            switch(UVar4) {
            case UT_TUNNELER:
            case UT_E_SPEAR:
            case UT_E_PIKE:
            case UT_E_MACE:
            case UT_E_SWORD:
            case UT_E_KNIGHT:
            case UT_E_MONK:
            case UT_LORD:
            case UT_S_BATTERINGRAM:
            case UT_A_SLAVE:
            case UT_A_ASSASSIN:
            case UT_A_SWORDSMAN:
switchD_00528e3a_caseD_5:
              if (UVar4 != UT_S_BATTERINGRAM) goto LAB_00528f32;
              if (DAT_UnitsState.units[iVar12].
                  digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 != 4)
              break;
              if (bVar22) {
LAB_00528f32:
                iVar14 = *(int *)(id_x_tile + -4);
                if (iVar14 == 0) break;
                sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar14];
                unitUID_Y = iVar14 - DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
                DAT_UnitsState.units[iVar12].targetingType = 0;
                DAT_UnitsState.units[iVar12].plannedDestinationX = (short)unitUID_Y;
                DAT_UnitsState.units[iVar12].plannedDestinationY = sVar9;
                if (DAT_UnitsState.units[iVar12].state.generic == US_MELEE_ATTACK) {
                  DAT_UnitsState.units[iVar12].unknownMovementRelated_0x2d2 =
                       DAT_UnitsState.units[iVar12].movementSpeed * -4;
                }
                DAT_UnitsState.units[iVar12].state.generic = US_MOVE_TO_DESTINATION;
                BVar16 = isTribeAllAssassins(&DAT_TribesState,tribeID);
                if (BVar16 == FALSE) {
                  DAT_PathFindingState.notAllAssassinsUnk = 1;
                }
                else {
                  DAT_PathFindingState.allAssassinsUnk = 1;
                }
                UnitsState::setDestinationForUnit(&DAT_UnitsState,iVar12,unitUID_Y,(int)sVar9,0);
                DAT_UnitsState.units[iVar12].movementType_OR_targetUnitID = 0;
                DAT_PathFindingState.notAllAssassinsUnk = 0;
                uVar13 = *(uint *)id_x_tile;
                DAT_UnitsState.units[iVar12].targetedBuildingTile = uVar13;
                sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[uVar13];
                DAT_UnitsState.units[iVar12].attackAtTileY = sVar9;
                sVar9 = *(short *)id_x_tile -
                        (short)DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
                id_x_tile = id_x_tile + 0xc;
              }
              else {
                iVar14 = Navigation::PathFindingState::findBuildingAccessPoint
                                   (&DAT_PathFindingState,iVar12,iVar11,&param_5);
                bVar22 = true;
                if (iVar14 == 0) goto LAB_00528f32;
                sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar14];
                unitUID_Y = iVar14 - DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
                BVar16 = UnitsState::setDestinationForUnit
                                   (&DAT_UnitsState,iVar12,unitUID_Y,(int)sVar9,0);
                if (BVar16 == FALSE) goto LAB_00528f32;
                DAT_UnitsState.units[iVar12].targetingType = 0;
                DAT_UnitsState.units[iVar12].plannedDestinationX = (short)unitUID_Y;
                DAT_UnitsState.units[iVar12].plannedDestinationY = sVar9;
                if (DAT_UnitsState.units[iVar12].state.generic == US_MELEE_ATTACK) {
                  DAT_UnitsState.units[iVar12].unknownMovementRelated_0x2d2 =
                       DAT_UnitsState.units[iVar12].movementSpeed * -4;
                }
                DAT_UnitsState.units[iVar12].state.generic = US_MOVE_TO_DESTINATION;
                DAT_UnitsState.units[iVar12].movementType_OR_targetUnitID = 0;
                DAT_PathFindingState.notAllAssassinsUnk = 0;
                sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[param_5];
                DAT_UnitsState.units[iVar12].targetedBuildingTile = param_5;
                DAT_UnitsState.units[iVar12].attackAtTileY = sVar9;
                sVar9 = (short)param_5 -
                        (short)DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
              }
              DAT_UnitsState.units[iVar12].attackAtTileX = sVar9;
              break;
            case UT_E_ARCHER:
            case UT_E_XBOW:
            case UT_A_ARCHER:
            case UT_A_SLINGER:
            case UT_A_HARCHER:
            case UT_A_FIRETHROWER:
              if (unitInstructionType == 0x24) goto switchD_00528e3a_caseD_5;
            }
          }
          if (DAT_TribesState.tribes[iVar18].size <= _unitTribeIndex) {
            return 1;
          }
        } while( true );
      }
    }
    break;
  case UIT_CONSTRUCT_SIEGE_EQUIPMENTOIL_DUTYENGINEERRELATED:
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    uVar21 = (uint)DAT_BuildingsState.buildings[id_x_tile].buildingEntryY;
    uVar13 = (uint)DAT_BuildingsState.buildings[id_x_tile].buildingEntryX;
    _unitTribeIndex = 0;
    BVar16 = Rendering::ViewportRenderState::xyAreValid(&DAT_ViewportRenderState,uVar13,uVar21);
    if (BVar16 == FALSE) {
      return 0;
    }
    param_5 = (int)(short)DAT_TileMapState.PathConnectionLayer
                          [DAT_ViewportRenderState.translationMatrix[uVar21].addXgetTile + uVar13];
    unitUID_Y = Buildings::BuildingsState::getRequiredEngineersCount(&DAT_BuildingsState,iVar11);
    if (((unitUID_Y != 0) || (DAT_BuildingsState.buildings[iVar11].buildingType == BT_OILSMELTER))
       && (0 < DAT_TribesState.tribes[iVar18].size)) {
      do {
        uVar13 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        iVar12 = _unitTribeIndex + 1;
        if ((((((DAT_UnitsState.units[uVar13].logicalState == ULS_NORMAL) &&
               (DAT_UnitsState.units[uVar13].dying == 0)) &&
              (DAT_UnitsState.units[uVar13].unitType == UT_E_ENGINEER)) &&
             ((UVar3 = DAT_UnitsState.units[uVar13].state.generic,
              UVar3 != (US_STAND_UPUnk|US_IDLEUnk) && (UVar3 != 10)))) && (UVar3 != US_SIT_DOWNUnk))
           && (((UVar3 != (US_STAND_UPUnk|US_RELOAD_WEAPONUnk) &&
                (UVar3 != (US_STAND_UPUnk|US_AIM_WEAPONUnk))) &&
               ((UVar3 != (US_STAND_UPUnk|US_FIRE_WEAPONUnk) &&
                (UVar3 != (US_STAND_UPUnk|US_LOOK_AROUNDUnk))))))) {
          DAT_UnitsState.units[uVar13]._someX_2 = 0;
          DAT_UnitsState.units[uVar13]._someY_2 = 0;
          cVar7 = Buildings::BuildingsState::resolveBuildingEntryAccessibility
                            (&DAT_BuildingsState,iVar11,1,(int)DAT_UnitsState.units[uVar13].x,
                             (int)DAT_UnitsState.units[uVar13].y);
          if ((CONCAT31(extraout_var,cVar7) != 0) &&
             (iVar14 = Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                                 (&DAT_PathFindingState,(int)DAT_UnitsState.units[uVar13].owner,
                                  param_5,(int)(short)DAT_TileMapState.PathConnectionLayer
                                                      [DAT_UnitsState.units[uVar13].tile],0),
             iVar14 != 0)) {
            sVar9 = DAT_BuildingsState.buildings[iVar11].buildingEntryY;
            sVar8 = DAT_BuildingsState.buildings[iVar11].buildingEntryX;
            iVar14 = DAT_BuildingsState.buildings[iVar11].uid;
            DAT_UnitsState.units[uVar13].targetID_OR_targetBuildingID = sVar19;
            DAT_UnitsState.units[uVar13].targetUID = iVar14;
            UnitsState::setDestinationForUnit(&DAT_UnitsState,uVar13,(int)sVar8,(int)sVar9,0);
            if (DAT_BuildingsState.buildings[iVar11].buildingType == BT_OILSMELTER) {
              DAT_UnitsState.units[uVar13].state.generic = US_STAND_UPUnk|US_IDLEUnk;
              DAT_UnitsState.units[uVar13].workplaceBuildingID_1 = sVar19;
            }
            else {
              DAT_UnitsState.units[uVar13].state.generic = US_STAND_UPUnk;
              DAT_UnitsState.units[uVar13].resourceToDeposit = 0;
              UnitsState::deselectUnit(uVar13);
              UnitsState::clearOrDeselectUnitFromSelection
                        (&DAT_UnitsState,DAT_TribesState.tribes[iVar18].owner,uVar13,0);
              unitUID_Y = unitUID_Y + -1;
              iVar12 = _unitTribeIndex;
              if (unitUID_Y == 0) {
                return 1;
              }
            }
          }
        }
        _unitTribeIndex = iVar12;
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
    break;
  case UIT_MAN_SIEGE_EQUIPMENT:
                    /* manning siege equipment? */
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    if (((DAT_UnitsState.units[id_x_tile].uid == unitUID_Y) &&
        (unitUID_Y = UnitsState::getRemainingRequiredEngineers(&DAT_UnitsState,id_x_tile),
        unitUID_Y != 0)) && (iVar12 = 0, 0 < DAT_TribesState.tribes[iVar18].size)) {
      do {
        uVar13 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar12);
        iVar14 = iVar12 + 1;
        if (((DAT_UnitsState.units[uVar13].logicalState == ULS_NORMAL) &&
            (DAT_UnitsState.units[uVar13].dying == 0)) &&
           (DAT_UnitsState.units[uVar13].unitType == UT_E_ENGINEER)) {
          DAT_UnitsState.units[iVar11]._someX_2 = 0;
          DAT_UnitsState.units[iVar11]._someY_2 = 0;
          param_5 = (int)(short)DAT_TileMapState.PathConnectionLayer
                                [DAT_UnitsState.units[uVar13].tile];
          unitInstructionType = 0;
          do {
            iVar14 = (int)DAT_UnitsState.units[iVar11].
                          digTileY__OR__countLifeCycleEngineersSentToManSiegeEngine;
            x = (int)DAT_AttackInfoDefinedData.field10_0xec[iVar14][0] +
                (int)DAT_UnitsState.units[iVar11].x;
            y = (int)DAT_AttackInfoDefinedData.field10_0xec[iVar14][1] +
                (int)DAT_UnitsState.units[iVar11].y;
            uVar21 = iVar14 + 1U & 0x8000000f;
            if ((int)uVar21 < 0) {
              uVar21 = (uVar21 - 1 | 0xfffffff0) + 1;
            }
            DAT_UnitsState.units[iVar11].digTileY__OR__countLifeCycleEngineersSentToManSiegeEngine =
                 (short)uVar21;
            BVar16 = Rendering::ViewportRenderState::xyAreValid(&DAT_ViewportRenderState,x,y);
            if (BVar16 != FALSE) {
              iVar14 = DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x;
              _param_4_unitUID_Y_copy = (dword)(short)DAT_TileMapState.PathConnectionLayer[iVar14];
              uVar21 = TileMapState::getTotalHeightAtTile(&DAT_TileMapState,iVar14);
              uVar21 = ((int)DAT_UnitsState.units[iVar11].buildingHeight +
                       (int)DAT_UnitsState.units[iVar11].terrainOrClimbHeight) - uVar21;
              uVar17 = (int)uVar21 >> 0x1f;
              if (((int)((uVar21 ^ uVar17) - uVar17) < 0x11) &&
                 (iVar14 = Navigation::PathFindingState::
                           calculateCanPlayerUnitsNavigateToAreaFromArea
                                     (&DAT_PathFindingState,(int)DAT_UnitsState.units[iVar11].owner,
                                      param_5,_param_4_unitUID_Y_copy,0), iVar14 != 0)) break;
            }
            unitInstructionType = unitInstructionType + 1;
          } while ((int)unitInstructionType < 0x10);
          UnitsState::setDestinationForUnit(&DAT_UnitsState,uVar13,x,y,0);
          DAT_UnitsState.units[uVar13].state.generic = US_MOVE_TO_DESTINATION;
          DAT_UnitsState.units[uVar13].targetingType = UIT_MAN_SIEGE_EQUIPMENT;
          DAT_UnitsState.units[uVar13].targetedUnitID__OR__engineerMannedSiegeEngineRef =
               (short)id_x_tile;
          DAT_UnitsState.units[uVar13].resourceToDeposit = 0;
          UnitsState::deselectUnit(uVar13);
          UnitsState::clearOrDeselectUnitFromSelection
                    (&DAT_UnitsState,DAT_TribesState.tribes[iVar18].owner,uVar13,0);
          unitUID_Y = unitUID_Y + -1;
          iVar14 = iVar12;
          if (unitUID_Y == 0) {
            return 1;
          }
        }
        iVar12 = iVar14;
        if (DAT_TribesState.tribes[iVar18].size <= iVar14) {
          return 1;
        }
      } while( true );
    }
    break;
  case UIT_EXIT_SIEGE_EQUIPMENT:
                    /* disband siege engines? */
    _param_4_unitUID_Y_copy = -(uint)(param_5 != 0) & 0x10;
    param_5 = (int)SEC_RNG.currentNumber2 & 0x8000000f;
    if (param_5 < 0) {
      param_5 = (param_5 - 1U | 0xfffffff0) + 1;
    }
    Random::RNG::nextRandomNumber2(&SEC_RNG);
    if (DAT_UnitsState.units[iVar11].uid == unitUID_Y) {
      DAT_UnitsState.units[iVar11].state.generic = US_FIRE_WEAPONUnk;
      unitInstructionType = 0;
      if (0 < DAT_UnitsState.units[iVar11].
              digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300) {
        tribeID = iVar11 * 0x490 + 0x1388860;
        do {
          iVar18 = (int)*(short *)tribeID;
          *(undefined2 *)tribeID = 0;
          DAT_UnitsState.units[iVar18].field266_0x3c0 = 0;
          DAT_UnitsState.units[iVar18].field265_0x3bc = 0;
          DAT_UnitsState.units[iVar18].animationCycleNumber = 0;
          DAT_UnitsState.units[iVar18].state.generic = US_JESTER_ROAM_TO;
          DAT_UnitsState.units[iVar18].disappearFadeAlphaCountdown = 0x20;
          DAT_UnitsState.units[iVar18].engineerManningSiegeStateRef_checkType = 0xfe;
          DAT_UnitsState.units[iVar18].cachedState = (UnitStateShort)_param_4_unitUID_Y_copy;
          UVar4 = DAT_UnitsState.units[iVar11].unitType;
          if ((UVar4 == UT_S_MANGONEL) || (UVar4 == UT_S_BALLISTA)) {
            DAT_UnitsState.units[iVar18].goToRallyPoint = 1;
          }
          DAT_UnitsState.units[iVar18].updateTickTracker = 0;
          DAT_UnitsState.units[iVar18].field42_0x58 = 1;
          unitUID_Y = 0;
LAB_00529da0:
          do {
            uVar21 = (int)DAT_AttackInfoDefinedData.field10_0xec[param_5][0] +
                     (int)DAT_UnitsState.units[iVar11].x;
            uVar13 = (int)DAT_AttackInfoDefinedData.field10_0xec[param_5][1] +
                     (int)DAT_UnitsState.units[iVar11].y;
            param_5 = param_5 + 1U & 0x8000000f;
            if (param_5 < 0) {
              param_5 = (param_5 - 1U | 0xfffffff0) + 1;
            }
            Navigation::PathFindingState::findWalkableTileThatDoesNotContainUnit
                      (&DAT_PathFindingState,id_x_tile,uVar21,uVar13,1);
            if (DAT_PathFindingState.ALG_ResultTile == 0) {
              Navigation::PathFindingState::findWalkableTileThatDoesNotContainUnit
                        (&DAT_PathFindingState,id_x_tile,uVar21,uVar13,0);
              sVar9 = (short)DAT_PathFindingState.ALG_ResultX;
              sVar19 = (short)DAT_PathFindingState.ALG_ResultY;
              iVar12 = DAT_PathFindingState.ALG_ResultTile;
              if (DAT_PathFindingState.ALG_ResultTile != 0) break;
              unitUID_Y = unitUID_Y + 1;
              if (unitUID_Y != 0x10) goto LAB_00529da0;
              sVar9 = DAT_UnitsState.units[iVar11].x;
              sVar19 = DAT_UnitsState.units[iVar11].y;
              iVar12 = DAT_UnitsState.units[iVar11].tile;
            }
            else {
              sVar9 = (short)DAT_PathFindingState.ALG_ResultX;
              sVar19 = (short)DAT_PathFindingState.ALG_ResultY;
              iVar12 = DAT_PathFindingState.ALG_ResultTile;
            }
          } while (iVar12 == 0);
          bVar2 = DAT_TileMapState.HeightLayer[iVar12];
          DAT_UnitsState.units[iVar18].totalSizeOfPathPlan = 0;
          DAT_UnitsState.units[iVar18].x = sVar9;
          DAT_UnitsState.units[iVar18].mimicCurrentXPosition = sVar9;
          DAT_UnitsState.units[iVar18].y = sVar19;
          DAT_UnitsState.units[iVar18].mimicCurrentYPosition = sVar19;
          DAT_UnitsState.units[iVar18].terrainOrClimbHeight = (ushort)bVar2;
          DAT_UnitsState.units[iVar18].tile = iVar12;
          DAT_UnitsState.units[iVar18].nextTileUnk = iVar12;
          DAT_UnitsState.units[iVar18].microXPosition = sVar9 * 8 + 4;
          DAT_UnitsState.units[iVar18].microYPosition = sVar19 * 8 + 4;
          UnitsState::updateMicroPosition(&DAT_UnitsState,iVar18);
          UnitsState::resetUnitMovementState(&DAT_UnitsState,iVar18);
          tribeID = tribeID + 2;
          DAT_UnitsState.units[iVar18].animationSheetFrameOffset = 1;
          DAT_UnitsState.units[iVar18].field_0x30_animRelated = 0x10;
          unitInstructionType = unitInstructionType + 1;
        } while ((int)unitInstructionType <
                 (int)DAT_UnitsState.units[iVar11].
                      digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300);
      }
      DAT_UnitsState.units[iVar11].
      digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 = 0;
      UnitsState::makeUnitStopWalkingByClearingPathProgressState(id_x_tile);
      return 1;
    }
    break;
  case UIT_THROW_OIL:
    iVar11 = 0;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    if (0 < sVar9) {
      do {
        uVar13 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar11);
        iVar11 = iVar11 + 1;
        if (((DAT_UnitsState.units[uVar13].logicalState == ULS_NORMAL) &&
            (DAT_UnitsState.units[uVar13].dying == 0)) &&
           (DAT_UnitsState.units[uVar13].unitType == UT_E_ENGINEER)) {
          DAT_UnitsState.units[uVar13].targetingType = UIT_THROW_OIL;
          DAT_UnitsState.units[uVar13].attackAtTileX = sVar19;
          DAT_UnitsState.units[uVar13].attackAtTileY = (short)unitUID_Y;
          DAT_UnitsState.units[uVar13].plannedDestinationX = sVar19;
          DAT_UnitsState.units[uVar13].plannedDestinationY = (short)unitUID_Y;
          UnitsState::deselectUnit(uVar13);
          UnitsState::clearOrDeselectUnitFromSelection
                    (&DAT_UnitsState,DAT_TribesState.tribes[iVar18].owner,uVar13,0);
          DAT_UnitsState.units[uVar13]._someX_2 = 0;
          DAT_UnitsState.units[uVar13]._someY_2 = 0;
        }
      } while (iVar11 < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
    break;
  case 0x15:
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    uVar13 = (uint)DAT_BuildingsState.buildings[id_x_tile].buildingEntryY;
    _unitTribeIndex = 0;
    BVar16 = Rendering::ViewportRenderState::xyAreValid
                       (&DAT_ViewportRenderState,
                        (int)DAT_BuildingsState.buildings[id_x_tile].buildingEntryX,uVar13);
    if (BVar16 == FALSE) {
      return 0;
    }
    param_5 = (int)(short)DAT_TileMapState.PathConnectionLayer
                          [DAT_ViewportRenderState.translationMatrix[uVar13].addXgetTile +
                           (int)DAT_BuildingsState.buildings[iVar11].buildingEntryX];
    if (0 < sVar9) {
      do {
        uVar13 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if (((DAT_UnitsState.units[uVar13].logicalState == ULS_NORMAL) &&
            (DAT_UnitsState.units[uVar13].dying == 0)) &&
           (DAT_UnitsState.units[uVar13].unitType == UT_TUNNELER)) {
          DAT_UnitsState.units[uVar13]._someX_2 = 0;
          DAT_UnitsState.units[uVar13]._someY_2 = 0;
          iVar12 = Buildings::BuildingsState::buildingIsAccessible(&DAT_BuildingsState,iVar11,1);
          if ((iVar12 != 0) &&
             (iVar12 = Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                                 (&DAT_PathFindingState,(int)DAT_UnitsState.units[uVar13].owner,
                                  param_5,(int)(short)DAT_TileMapState.PathConnectionLayer
                                                      [DAT_UnitsState.units[uVar13].tile],0),
             iVar12 != 0)) {
            sVar9 = DAT_BuildingsState.buildings[iVar11].buildingEntryY;
            sVar8 = DAT_BuildingsState.buildings[iVar11].buildingEntryX;
            iVar11 = DAT_BuildingsState.buildings[iVar11].uid;
            DAT_UnitsState.units[uVar13].workplaceBuildingID_1 = sVar19;
            DAT_UnitsState.units[uVar13].targetID_OR_targetBuildingID = sVar19;
            DAT_UnitsState.units[uVar13].targetUID = iVar11;
            UnitsState::setDestinationForUnit(&DAT_UnitsState,uVar13,(int)sVar8,(int)sVar9,0);
            DAT_UnitsState.units[uVar13].state.generic = US_LOOK_AROUNDUnk;
            DAT_UnitsState.units[uVar13].targetingType = 0x15;
            UnitsState::deselectUnit(uVar13);
            UnitsState::clearOrDeselectUnitFromSelection
                      (&DAT_UnitsState,DAT_TribesState.tribes[iVar18].owner,uVar13,0);
            return 1;
          }
        }
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
    }
    DAT_TileMapState.showNoRubbleWhenDestroyingBuilding = 1;
    Buildings::BuildingsState::destroyBuilding(&DAT_BuildingsState,iVar11);
    break;
  case UIT_ATTACK_WALL:
  case 0x23:
  case 0x25:
    _unitTribeIndex = 0;
    id_x_tile = 0;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    if (0 < sVar9) {
      do {
        uVar13 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if (((DAT_UnitsState.units[uVar13].logicalState != ULS_NORMAL) ||
            (DAT_UnitsState.units[uVar13].dying != 0)) ||
           (DAT_UnitsState.units[uVar13].field320_0x413 != 0)) goto switchD_005290c7_caseD_6;
        DAT_UnitsState.units[uVar13]._someX_2 = 0;
        DAT_UnitsState.units[uVar13]._someY_2 = 0;
        switch(DAT_UnitsState.units[uVar13].unitType) {
        case UT_E_ARCHER:
        case UT_E_XBOW:
        case UT_A_ARCHER:
        case UT_A_SLINGER:
        case UT_A_ASSASSIN:
        case UT_A_FIRETHROWER:
          goto switchD_005290c7_caseD_16;
        case UT_E_KNIGHT:
switchD_005290c7_caseD_1c:
          _ramOrHorse = _ramOrHorse + 1;
        case UT_TUNNELER:
        case UT_E_SPEAR:
        case UT_E_PIKE:
        case UT_E_MACE:
        case UT_E_SWORD:
        case UT_E_MONK:
        case UT_LORD:
        case UT_A_SLAVE:
        case UT_A_SWORDSMAN:
switchD_005290c7_caseD_5:
          id_x_tile = id_x_tile + 1;
          break;
        case UT_S_CATAPULT:
        case UT_S_TREBUCHET:
        case UT_S_MANGONEL:
        case UT_S_BALLISTA:
        case UT_S_FBALLISTA:
          if (unitInstructionType != 0x25) {
            sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar11];
            DAT_UnitsState.units[uVar13].targetID_OR_targetBuildingID = sVar19;
            DAT_UnitsState.units[uVar13].
            targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
                 unitUID_Y;
            DAT_UnitsState.units[uVar13].attackAtTileY = sVar9;
            DAT_UnitsState.units[uVar13].attackAtTileX =
                 sVar19 - (short)DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
            DAT_UnitsState.units[uVar13].field270_0x3c5 = 0x17;
            DAT_UnitsState.units[uVar13].targetingType = UIT_ATTACK_WALL;
            UnitsState::makeUnitStopWalkingByClearingPathProgressState(uVar13);
            DAT_UnitsState.units[uVar13].shootBeforeStop = 10;
          }
          break;
        case UT_S_TOWER:
          uVar21 = UnitsState::findFreeTileNearby(&DAT_UnitsState,uVar13,iVar11);
          if (uVar21 != 0) {
            UnitsState::setDestinationForUnit
                      (&DAT_UnitsState,uVar13,
                       uVar21 - DAT_ViewportRenderState.translationMatrix
                                [DAT_ViewportRenderState.tileTranslationMatrix_YComponent[uVar21]].
                                addXgetTile,
                       (int)DAT_ViewportRenderState.tileTranslationMatrix_YComponent[uVar21],0);
            sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar11];
            DAT_UnitsState.units[uVar13].targetingType = UIT_ATTACK_WALL;
            DAT_UnitsState.units[uVar13].state.generic = US_MOVE_TO_DESTINATION;
            DAT_UnitsState.units[uVar13].targetID_OR_targetBuildingID = sVar19;
            DAT_UnitsState.units[uVar13].targetedBuildingTile = iVar11;
            DAT_UnitsState.units[uVar13].digTileTarget = uVar21;
            DAT_UnitsState.units[uVar13].attackAtTileY = sVar9;
            DAT_UnitsState.units[uVar13].attackAtTileX =
                 sVar19 - (short)DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
          }
          break;
        case UT_S_BATTERINGRAM:
          if (DAT_UnitsState.units[uVar13].
              digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 4) {
            local_8 = local_8 + 1;
            goto switchD_005290c7_caseD_1c;
          }
          break;
        case UT_A_HARCHER:
          _ramOrHorse = _ramOrHorse + 1;
switchD_005290c7_caseD_16:
          if (unitInstructionType == 0x23) goto switchD_005290c7_caseD_5;
        }
switchD_005290c7_caseD_6:
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
    }
    if ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
       (DAT_GameState.mapAndTime.strongWalls2 != 0)) {
      id_x_tile = local_8;
    }
    if (id_x_tile != 0) {
      sVar9 = DAT_TribesState.tribes[iVar18].selectionTargetUnitID;
      if ((unitInstructionType == UIT_ATTACK_WALL) || (unitInstructionType == 0x25)) {
        sVar8 = DAT_UnitsState.units[sVar9].facingDirection;
        iVar12 = (int)DAT_UnitsState.units[sVar9].owner;
      }
      else {
        sVar8 = DAT_UnitsState.units[sVar9].facingDirection;
        iVar12 = 0;
      }
      Navigation::PathFindingState::
      findFreeSpaceNextToEnemyDefensiveStructureInSameAreaWithinDistance
                (&DAT_PathFindingState,iVar11,id_x_tile,
                 (int *)(int)(short)DAT_TileMapState.PathConnectionLayer
                                    [DAT_UnitsState.units[sVar9].tile],iVar12,0,(int)sVar8);
      sortTribePathDestinationsByCost(&DAT_TribesState,tribeID,_ramOrHorse);
      if ((DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper != 0) &&
         (iVar12 = 0, 0 < DAT_TribesState.tribes[iVar18].size)) {
        id_x_tile = 0x12d5c70;
        do {
          iVar14 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar12);
          iVar12 = iVar12 + 1;
          if (((DAT_UnitsState.units[iVar14].logicalState == ULS_NORMAL) &&
              (DAT_UnitsState.units[iVar14].dying == 0)) &&
             (DAT_UnitsState.units[iVar14].field320_0x413 == 0)) {
            UVar4 = DAT_UnitsState.units[iVar14].unitType;
            switch(UVar4) {
            case UT_TUNNELER:
            case UT_E_SPEAR:
            case UT_E_PIKE:
            case UT_E_MACE:
            case UT_E_SWORD:
            case UT_E_KNIGHT:
            case UT_E_MONK:
            case UT_LORD:
            case UT_A_SLAVE:
            case UT_A_SWORDSMAN:
switchD_0052932a_caseD_5:
              if ((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
                 (DAT_GameState.mapAndTime.strongWalls2 == 0)) goto switchD_0052932a_caseD_3b;
              break;
            case UT_E_ARCHER:
            case UT_E_XBOW:
            case UT_A_ARCHER:
            case UT_A_SLINGER:
            case UT_A_ASSASSIN:
            case UT_A_HARCHER:
            case UT_A_FIRETHROWER:
              if (unitInstructionType == 0x23) goto switchD_0052932a_caseD_5;
              break;
            case UT_S_BATTERINGRAM:
switchD_0052932a_caseD_3b:
              if (UVar4 == UT_S_BATTERINGRAM) {
                if (DAT_UnitsState.units[iVar14].
                    digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 != 4)
                break;
                if (!bVar22) {
                  bVar22 = true;
                  iVar15 = Navigation::PathFindingState::
                           findUnitPreferredOrientationBasedConnectedTile
                                     (&DAT_PathFindingState,iVar14,iVar11);
                  if (iVar15 != 0) {
                    sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar15];
                    unitUID_Y = iVar15 - DAT_ViewportRenderState.translationMatrix[sVar9].
                                         addXgetTile;
                    BVar16 = UnitsState::setDestinationForUnit
                                       (&DAT_UnitsState,iVar14,unitUID_Y,(int)sVar9,0);
                    if (BVar16 != FALSE) {
                      DAT_UnitsState.units[iVar14].targetingType = 0;
                      DAT_UnitsState.units[iVar14].plannedDestinationX = (short)unitUID_Y;
                      DAT_UnitsState.units[iVar14].plannedDestinationY = sVar9;
                      if (DAT_UnitsState.units[iVar14].state.generic == US_MELEE_ATTACK) {
                        DAT_UnitsState.units[iVar14].unknownMovementRelated_0x2d2 =
                             DAT_UnitsState.units[iVar14].movementSpeed * -4;
                      }
                      DAT_UnitsState.units[iVar14].state.generic = US_MOVE_TO_DESTINATION;
                      DAT_UnitsState.units[iVar14].movementType_OR_targetUnitID = 0;
                      DAT_PathFindingState.notAllAssassinsUnk = 0;
                      sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar11];
                      DAT_UnitsState.units[iVar14].targetedBuildingTile = iVar11;
                      DAT_UnitsState.units[iVar14].attackAtTileY = sVar9;
                      DAT_UnitsState.units[iVar14].attackAtTileX =
                           sVar19 - (short)DAT_ViewportRenderState.translationMatrix[sVar9].
                                           addXgetTile;
                      break;
                    }
                  }
                }
              }
              iVar15 = *(int *)(id_x_tile + -4);
              if (iVar15 != 0) {
                sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar15];
                uVar13 = iVar15 - DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
                DAT_UnitsState.units[iVar14].targetingType = 0;
                DAT_UnitsState.units[iVar14].plannedDestinationX = (short)uVar13;
                DAT_UnitsState.units[iVar14].plannedDestinationY = sVar9;
                DAT_PathFindingState.notAllAssassinsUnk = 1;
                if (DAT_UnitsState.units[iVar14].state.generic == US_MELEE_ATTACK) {
                  DAT_UnitsState.units[iVar14].unknownMovementRelated_0x2d2 =
                       DAT_UnitsState.units[iVar14].movementSpeed * -4;
                }
                DAT_UnitsState.units[iVar14].state.generic = US_MOVE_TO_DESTINATION;
                UnitsState::setDestinationForUnit(&DAT_UnitsState,iVar14,uVar13,(int)sVar9,0);
                DAT_PathFindingState.notAllAssassinsUnk = 0;
                uVar13 = *(uint *)id_x_tile;
                sVar9 = *(short *)id_x_tile;
                DAT_UnitsState.units[iVar14].movementType_OR_targetUnitID = 0;
                DAT_UnitsState.units[iVar14].targetedBuildingTile = uVar13;
                sVar8 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[uVar13];
                DAT_UnitsState.units[iVar14].attackAtTileY = sVar8;
                id_x_tile = id_x_tile + 0xc;
                DAT_UnitsState.units[iVar14].attackAtTileX =
                     sVar9 - (short)DAT_ViewportRenderState.translationMatrix[sVar8].addXgetTile;
              }
            }
          }
          if (DAT_TribesState.tribes[iVar18].size <= iVar12) {
            return 1;
          }
        } while( true );
      }
    }
    break;
  case UIT_SET_LADDER:
    iVar12 = 0;
    id_x_tile = 0;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    if (0 < sVar9) {
      do {
        iVar14 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar12);
        iVar12 = iVar12 + 1;
        if (((DAT_UnitsState.units[iVar14].logicalState == ULS_NORMAL) &&
            (DAT_UnitsState.units[iVar14].dying == 0)) &&
           (DAT_UnitsState.units[iVar14].unitType == UT_E_LADDER)) {
          id_x_tile = id_x_tile + 1;
          DAT_UnitsState.units[iVar14]._someX_2 = 0;
          DAT_UnitsState.units[iVar14]._someY_2 = 0;
        }
      } while (iVar12 < DAT_TribesState.tribes[iVar18].size);
      if (id_x_tile != 0) {
        sVar9 = DAT_TribesState.tribes[iVar18].selectionTargetUnitID;
        Navigation::PathFindingState::populateDestinationsArrayWithWallTileAndFreeTilePairInSameArea
                  (&DAT_PathFindingState,iVar11,id_x_tile,
                   (int)(short)DAT_TileMapState.PathConnectionLayer
                               [DAT_UnitsState.units[sVar9].tile],
                   (int)DAT_UnitsState.units[sVar9].owner);
        sortTribePathDestinationsByCost(&DAT_TribesState,tribeID,0);
        if ((DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper != 0) &&
           (iVar11 = 0, 0 < DAT_TribesState.tribes[iVar18].size)) {
          piVar20 = &DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper;
          do {
            iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar11);
            iVar11 = iVar11 + 1;
            if ((((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
                 (DAT_UnitsState.units[iVar12].dying == 0)) &&
                (DAT_UnitsState.units[iVar12].unitType == UT_E_LADDER)) &&
               (iVar14 = ((PathHelper12 *)(piVar20 + -1))->tile1, iVar14 != 0)) {
                    /* set ladder men destination to free tile next to defensive structure */
              sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar14];
              uVar13 = iVar14 - DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
              DAT_UnitsState.units[iVar12].targetingType = 0;
              DAT_UnitsState.units[iVar12].plannedDestinationX = (short)uVar13;
              DAT_UnitsState.units[iVar12].plannedDestinationY = sVar9;
              DAT_PathFindingState.notAllAssassinsUnk = 1;
              if (DAT_UnitsState.units[iVar12].state.generic == US_MELEE_ATTACK) {
                DAT_UnitsState.units[iVar12].unknownMovementRelated_0x2d2 =
                     DAT_UnitsState.units[iVar12].movementSpeed * -4;
              }
              DAT_UnitsState.units[iVar12].state.generic =
                   (ushort)(*piVar20 != 0) * 2 + US_MOVE_TO_DESTINATION;
              UnitsState::setDestinationForUnit(&DAT_UnitsState,iVar12,uVar13,(int)sVar9,0);
              DAT_PathFindingState.notAllAssassinsUnk = 0;
              uVar13 = *piVar20;
              iVar14 = *piVar20;
                    /* set ladder man ladder target tile */
              DAT_UnitsState.units[iVar12].targetedBuildingTile = uVar13;
              sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[uVar13];
              DAT_UnitsState.units[iVar12].attackAtTileY = sVar9;
              piVar20 = piVar20 + 3;
              DAT_UnitsState.units[iVar12].attackAtTileX =
                   (short)iVar14 -
                   (short)DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
            }
          } while (iVar11 < DAT_TribesState.tribes[iVar18].size);
          return 1;
        }
      }
    }
    break;
  case 0x1a:
    iVar11 = 0;
    if (0 < sVar9) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,iVar18,iVar11);
        iVar11 = iVar11 + 1;
        if (((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
            (DAT_UnitsState.units[iVar12].dying == 0)) &&
           ((int)(short)DAT_UnitsState.units[iVar12].unitType - 0x27U < 2)) {
          DAT_UnitsState.units[iVar12].field260_0x3b0 = 1;
        }
      } while (iVar11 < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
    break;
  case UIT_DISBAND:
                    /* disband? */
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    _unitTribeIndex = 0;
    if (0 < sVar9) {
      do {
        iVar11 = getUnitIDForIndexInTribe(&DAT_TribesState,iVar18,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if ((DAT_UnitsState.units[iVar11].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[iVar11].dying == 0)) {
          switch(DAT_UnitsState.units[iVar11].unitType) {
          case UT_TUNNELER:
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_E_SPEAR:
          case UT_E_PIKE:
          case UT_E_MACE:
          case UT_E_SWORD:
          case UT_E_KNIGHT:
          case UT_E_LADDER:
          case UT_E_ENGINEER:
          case UT_E_MONK:
          case UT_A_ARCHER:
          case UT_A_SLAVE:
          case UT_A_SLINGER:
          case UT_A_ASSASSIN:
          case UT_A_HARCHER:
          case UT_A_SWORDSMAN:
          case UT_A_FIRETHROWER:
            UnitsState::disbandUnit(&DAT_UnitsState,iVar11);
            break;
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
          case UT_S_MANGONEL:
          case UT_S_TOWER:
          case UT_S_BATTERINGRAM:
          case UT_S_SHIELD:
          case UT_S_BALLISTA:
          case UT_S_FBALLISTA:
            giveTribeAnInstruction
                      (&DAT_TribesState,iVar18,UIT_EXIT_SIEGE_EQUIPMENT,iVar11,
                       DAT_UnitsState.units[iVar11].uid,1);
            bVar22 = DAT_GameCore.gameMode_2 == GM_SIEGE_THAT;
            DAT_UnitsState.units[iVar11].state.generic = US_DISAPPEAR;
            if (bVar22) {
              Buildings::BuildingsState::getPriceForDisbandedUnitType
                        (&DAT_BuildingsState,(int)(short)DAT_UnitsState.units[iVar11].unitType,
                         &tribeID);
              piVar20 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                        startResources + 0xf;
              *piVar20 = *piVar20 + tribeID;
            }
          }
        }
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
    }
    UnitsState::deselectAllUnitsOneByOne(&DAT_UnitsState);
    UnitsState::clearOrDeselectUnitFromSelection
              (&DAT_UnitsState,DAT_TribesState.tribes[iVar18].owner,0,0);
    return 1;
  case UIT_STOP:
    iVar11 = 0;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    DAT_TribesState.tribes[tribeID].someUnitID = 0;
    if (0 < sVar9) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar11);
        iVar11 = iVar11 + 1;
        if (((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
            (DAT_UnitsState.units[iVar12].dying == 0)) &&
           (DAT_UnitsState.units[iVar12].field320_0x413 == 0)) {
          DAT_UnitsState.units[iVar12].field270_0x3c5 = 3;
          DAT_UnitsState.units[iVar12].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
          DAT_UnitsState.units[iVar12].field260_0x3b0 = 0;
          UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
          DAT_UnitsState.units[iVar12].targetedBuildingTile = 0;
          DAT_UnitsState.units[iVar12].movementType_OR_targetUnitID = 0;
        }
      } while (iVar11 < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
    break;
  case 0x20:
  case UIT_SHOOT_TARGETUnk:
    local_8 = id_x_tile * 0x490;
    pUVar6 = DAT_UnitsState.units + id_x_tile;
    _unitTribeIndex = 0;
    id_x_tile = 0;
    if (pUVar6->uid != unitUID_Y) {
      return 0;
    }
    if (0 < sVar9) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if ((((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
             (DAT_UnitsState.units[iVar12].dying == 0)) &&
            (DAT_UnitsState.units[iVar12].field320_0x413 == 0)) &&
           (UVar3 = DAT_UnitsState.units[iVar12].state.generic, UVar3 != US_MELEE_ATTACK)) {
          switch(DAT_UnitsState.units[iVar12].unitType) {
          case UT_TUNNELER:
          case UT_E_SPEAR:
          case UT_E_PIKE:
          case UT_E_MACE:
          case UT_E_SWORD:
          case UT_E_KNIGHT:
          case UT_E_MONK:
          case UT_LORD:
          case UT_A_SLAVE:
          case UT_A_ASSASSIN:
          case UT_A_SWORDSMAN:
            if (unitInstructionType != UIT_SHOOT_TARGETUnk) {
              id_x_tile = id_x_tile + 1;
            }
            break;
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_E_ARCHER_DEBUG:
          case UT_A_ARCHER:
          case UT_A_SLINGER:
          case UT_A_HARCHER:
          case UT_A_FIRETHROWER:
switchD_005282f6_caseD_16:
            if (UVar3 == 0x69) {
              DAT_UnitsState.units[iVar12].state.generic = US_MOVE_TO_DESTINATION;
            }
            DAT_UnitsState.units[iVar12].targetingType = UIT_UNIT_ATTACK_UNIT;
            DAT_UnitsState.units[iVar12].targetedUnitID__OR__engineerMannedSiegeEngineRef = sVar19;
            DAT_UnitsState.units[iVar12].
            targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
                 unitUID_Y;
            DAT_UnitsState.units[iVar12].field300_0x3f8 = 0;
            if (DAT_UnitsState.units[iVar11].unitType == UT_RABBIT) {
              DAT_TribesState.tribes[iVar18].field71_0x212 = 1;
            }
            if (DAT_UnitsState.units[iVar12]._someX_2 == 0) {
              sVar9 = DAT_UnitsState.units[iVar12].destinationY_2Unk;
              DAT_UnitsState.units[iVar12]._someX_2 = DAT_UnitsState.units[iVar12].destinationX_2Unk
              ;
              DAT_UnitsState.units[iVar12]._someY_2 = sVar9;
            }
            UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
            break;
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
            if (unitInstructionType != UIT_SHOOT_TARGETUnk) {
              sVar9 = DAT_UnitsState.units[iVar12]._someX_2;
              DAT_UnitsState.units[iVar12].field270_0x3c5 = 5;
              DAT_UnitsState.units[iVar12].targetingType = UIT_ATTACK_LAND;
              DAT_UnitsState.units[iVar12].attackAtTileX = DAT_UnitsState.units[iVar11].x;
              DAT_UnitsState.units[iVar12].attackAtTileY = DAT_UnitsState.units[iVar11].y;
              DAT_UnitsState.units[iVar12].unkAttackRelated = 0xb;
              if (sVar9 == 0) {
                sVar9 = DAT_UnitsState.units[iVar12].destinationY_2Unk;
                DAT_UnitsState.units[iVar12]._someX_2 =
                     DAT_UnitsState.units[iVar12].destinationX_2Unk;
                DAT_UnitsState.units[iVar12]._someY_2 = sVar9;
              }
              UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
              DAT_UnitsState.units[iVar12].shootBeforeStop = 10;
            }
            break;
          case UT_S_MANGONEL:
          case UT_S_BALLISTA:
          case UT_S_FBALLISTA:
            if (unitInstructionType != UIT_SHOOT_TARGETUnk) {
              DAT_UnitsState.units[iVar12].shootBeforeStop = 10;
              goto switchD_005282f6_caseD_16;
            }
          }
        }
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
      if (id_x_tile != 0) {
        iVar12 = (int)DAT_TribesState.tribes[iVar18].selectionTargetUnitID;
        param_5 = (int)DAT_UnitsState.units[iVar12].x;
        unitInstructionType = (UnitInstructionType)DAT_UnitsState.units[iVar12].y;
        predictUnitInterceptPosition
                  (&DAT_TribesState,iVar12,iVar11,&param_5,(int *)&unitInstructionType);
        Navigation::PathFindingState::pathPlanningForTribe
                  (&DAT_PathFindingState,tribeID,iVar11,param_5,unitInstructionType,id_x_tile,
                   (int)(short)DAT_TileMapState.PathConnectionLayer
                               [DAT_UnitsState.units[iVar12].tile],
                   (int)DAT_UnitsState.units[iVar12].owner);
        DAT_TribesState.tribes[iVar18].someUnitID = sVar19;
        DAT_TribesState.tribes[iVar18].someUnitUID = unitUID_Y;
        DAT_TribesState.tribes[iVar18].someTile = DAT_UnitsState.units[iVar11].tile;
        iVar12 = 0;
        sVar9 = DAT_TribesState.tribes[iVar18].size;
        DAT_TribesState.tribes[iVar18].someTile2 =
             (int)DAT_UnitsState.units[iVar11].destinationX_2Unk +
             DAT_ViewportRenderState.translationMatrix
             [DAT_UnitsState.units[iVar11].destinationY_2Unk].addXgetTile;
        unitInstructionType = 0;
        if (0 < sVar9) {
          id_x_tile = 0x12d5c6c;
          do {
            iVar14 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar12);
            iVar12 = iVar12 + 1;
            if (((DAT_UnitsState.units[iVar14].logicalState == ULS_NORMAL) &&
                (DAT_UnitsState.units[iVar14].dying == 0)) &&
               ((DAT_UnitsState.units[iVar14].field320_0x413 == 0 &&
                (DAT_UnitsState.units[iVar14].state.generic != US_MELEE_ATTACK)))) {
              switch(DAT_UnitsState.units[iVar14].unitType) {
              case UT_TUNNELER:
              case UT_E_SPEAR:
              case UT_E_PIKE:
              case UT_E_MACE:
              case UT_E_SWORD:
              case UT_E_KNIGHT:
              case UT_E_MONK:
              case UT_LORD:
              case UT_A_SLAVE:
              case UT_A_ASSASSIN:
              case UT_A_SWORDSMAN:
                iVar15 = *(int *)id_x_tile;
                if (iVar15 != 0) {
                  sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar15];
                  uVar13 = iVar15 - DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
                  if (*(int *)(id_x_tile + 4) == 0) {
                    DAT_UnitsState.units[iVar14].targetingType = 0;
                    if (DAT_UnitsState.units[iVar14].unitType == UT_LORD) break;
                  }
                  else {
                    DAT_UnitsState.units[iVar14].targetingType = UIT_UNIT_ATTACK_UNIT;
                    DAT_UnitsState.units[iVar14].targetedUnitID__OR__engineerMannedSiegeEngineRef =
                         sVar19;
                    DAT_UnitsState.units[iVar14].
                    targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID
                         = unitUID_Y;
                  }
                  DAT_UnitsState.units[iVar14].plannedDestinationX = (short)uVar13;
                  DAT_UnitsState.units[iVar14].plannedDestinationY = sVar9;
                  DAT_UnitsState.units[iVar14].targetedBuildingTile = 0;
                  if (DAT_UnitsState.units[iVar14].state.generic == US_MELEE_ATTACK) {
                    DAT_UnitsState.units[iVar14].unknownMovementRelated_0x2d2 =
                         DAT_UnitsState.units[iVar14].movementSpeed * -4;
                  }
                  if (DAT_UnitsState.units[iVar14]._someX_2 == 0) {
                    DAT_UnitsState.units[iVar14]._someX_2 =
                         DAT_UnitsState.units[iVar14].destinationX_2Unk;
                    DAT_UnitsState.units[iVar14]._someY_2 =
                         DAT_UnitsState.units[iVar14].destinationY_2Unk;
                  }
                  DAT_UnitsState.units[iVar14].state.generic = US_MOVE_TO_DESTINATION;
                  BVar16 = isTribeAllAssassins(&DAT_TribesState,tribeID);
                  if (BVar16 == FALSE) {
                    DAT_PathFindingState.notAllAssassinsUnk = 1;
                  }
                  else {
                    DAT_PathFindingState.allAssassinsUnk = 1;
                  }
                  UnitsState::setDestinationForUnit(&DAT_UnitsState,iVar14,uVar13,(int)sVar9,0);
                  DAT_UnitsState.units[iVar14].moveDelay = 0;
                  DAT_UnitsState.units[iVar14].lookForEnemy = -0x32;
                  if (DAT_UnitsState.units[iVar14].movementType_OR_targetUnitID != iVar11) {
                    DAT_UnitsState.units[iVar14].movementType_OR_targetUnitID = sVar19;
                    psVar1 = (short *)((int)&DAT_UnitsState.units[0].huntedBy + local_8);
                    *psVar1 = *psVar1 + 1;
                  }
                  UVar10 = (int)DAT_UnitsState.units[iVar14].totalSizeOfPathPlan / 2;
                  if ((int)unitInstructionType < (int)UVar10) {
                    unitInstructionType = UVar10;
                  }
                  id_x_tile = id_x_tile + 0xc;
                  DAT_PathFindingState.notAllAssassinsUnk = 0;
                }
              }
            }
          } while (iVar12 < DAT_TribesState.tribes[iVar18].size);
        }
        iVar11 = unitInstructionType * 8;
        if (iVar11 < 9) {
          iVar11 = 8;
        }
        DAT_TribesState.tribes[iVar18].field168_0x2be = (short)iVar11;
        return 1;
      }
    }
    break;
  case UIT_LIGHT_PITCH:
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    _unitTribeIndex = 0;
    if ((DAT_TileMapState.pitchDitches[id_x_tile].uid == unitUID_Y) && (0 < sVar9)) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if ((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[iVar12].dying == 0)) {
          DAT_UnitsState.units[iVar12]._someX_2 = 0;
          DAT_UnitsState.units[iVar12]._someY_2 = 0;
          UVar4 = DAT_UnitsState.units[iVar12].unitType;
          if ((UVar4 == UT_E_ARCHER) || (UVar4 == UT_A_ARCHER)) {
            sVar9 = DAT_TileMapState.pitchDitches[iVar11].y;
            DAT_UnitsState.units[iVar12].shootTargetMicroX =
                 DAT_TileMapState.pitchDitches[iVar11].x * 8 + 4;
            iVar14 = DAT_TileMapState.pitchDitches[iVar11].tile;
            DAT_UnitsState.units[iVar12].shootTargetMicroY = sVar9 * 8 + 4;
            DAT_UnitsState.units[iVar12].shootTargetZ = (ushort)DAT_TileMapState.HeightLayer[iVar14]
            ;
            DAT_UnitsState.units[iVar12].shootTargetedUnit = -1;
            DAT_UnitsState.units[iVar12].targetID_OR_targetBuildingID = sVar19;
            DAT_UnitsState.units[iVar12].
            targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
                 unitUID_Y;
            DAT_UnitsState.units[iVar12].field270_0x3c5 = 0x22;
            DAT_UnitsState.units[iVar12].targetingType = UIT_LIGHT_PITCH;
            DAT_UnitsState.units[iVar12].field300_0x3f8 = 0;
            UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
            DAT_UnitsState.units[iVar12].shootBeforeStop = 10;
          }
        }
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
  }
  return 1;
}


// ================= _HoldStrong::Map::Units::UnitsState::computeLadderClimbPath @ 00533a10 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Units::UnitsState::computeLadderClimbPath
          (UnitsState *this,int unitID,uint param_2,int param_3,int param_4)

{
  byte *pPathPlan;
  short sVar1;
  short sVar2;
  int iVar3;
  uint uVar4;
  
  DAT_UnitsState.units[unitID].climbDataID = 0;
  DAT_PathFindingState.climbIsIllegal = 0;
  DAT_PathFindingState.allAssassinsUnk = 0;
  DAT_UnitsState.units[unitID].field297_0x3f4 = 0;
  IO::LowLevelMemory::copyData
            (&DAT_LowLevelMemory,0x490,DAT_UnitsState.units + unitID,DAT_UnitsState.units);
  pPathPlan = DAT_UnitsState.units[unitID].pathPlanStart;
  IO::LowLevelMemory::fillMemory_ByteValue(&DAT_LowLevelMemory,400,'\0',pPathPlan);
  Navigation::PathFindingState::bindPathPlanToAlgorithmStateAndReset
            (&DAT_PathFindingState,pPathPlan);
  DAT_PathFindingState.unitX = (int)DAT_UnitsState.units[unitID].x;
  DAT_PathFindingState.unitY = (int)DAT_UnitsState.units[unitID].y;
  uVar4 = Navigation::PathFindingState::commitUnitPathPlanUsingWalkLayer
                    (&DAT_PathFindingState,param_2,param_3,param_4);
  if (0 < (int)uVar4) {
    sVar1 = DAT_UnitsState.units[unitID].y;
    DAT_UnitsState.units[unitID].totalSizeOfPathPlan = (short)uVar4;
    sVar2 = DAT_UnitsState.units[unitID].x;
    DAT_UnitsState.units[unitID].ladderExitYPosition = sVar1;
    DAT_UnitsState.units[unitID].currentIndexInPathPlan = 0;
    DAT_UnitsState.units[unitID].ladderExitXPosition = sVar2;
    DAT_UnitsState.units[unitID].tunnelerFinishedDigging = 2;
    iVar3 = DAT_ViewportRenderState.translationMatrix[sVar1].addXgetTile;
    DAT_UnitsState.units[unitID].cannotClimb = 0;
    DAT_UnitsState.units[unitID].previousTilePosition = sVar2 + iVar3;
    return 1;
  }
  return 0;
}


// ================= _HoldStrong::Map::Units::UnitsState::giveTribeMoveInstructionHumans @ 00537070 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::UnitsState::giveTribeMoveInstructionHumans
          (UnitsState *this,int tribeID,uint x,uint y,int rallyBool,
          MatchSpeedInstructionEnum speedMatching)

{
  short *psVar1;
  
  psVar1 = &DAT_TribesState.tribes[tribeID].freeUnitSpeeds;
  *psVar1 = 0;
  if ((char)speedMatching < '\0') {
    speedMatching = speedMatching & 0xffffff7f;
    *psVar1 = 1;
  }
  TribesState::giveTribeMoveInstruction(&DAT_TribesState,tribeID,x,y,rallyBool,1,speedMatching);
  return;
}


// ================= _HoldStrong::Map::Units::UnitsState::setUnitValues @ 0053b8e0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::UnitsState::setUnitValues(UnitsState *this,int unitID,UnitType unitType)

{
  short sVar1;
  int iVar2;
  byte bVar3;
  short sVar4;
  
  DAT_UnitsState.units[unitID].unitType = (UnitTypeShort)unitType;
  DAT_UnitsState.units[unitID].field67_0x90 =
       (short)DAT_UnitPropertiesDefinedData.field65_0x7634[unitType];
  DAT_UnitsState.units[unitID].unknownTestAgainst0_1 =
       (byte)DAT_UnitPropertiesDefinedData.field66_0x7774[unitType];
  sVar4 = (short)DAT_UnitPropertiesDefinedData.DAT_SPRITE_ID[unitType];
  DAT_UnitsState.units[unitID].gmIDUnk = sVar4;
  DAT_UnitsState.units[unitID].spriteID = sVar4;
  DAT_UnitsState.units[unitID].gfxNumber = 1;
  DAT_UnitsState.units[unitID].field22_0x2a =
       (short)DAT_TextureRenderCoreObject.gmFileHeaderColorpaletteArray[sVar4].originX;
  *(short *)&DAT_UnitsState.units[unitID].unknownV =
       (short)DAT_TextureRenderCoreObject.gmFileHeaderColorpaletteArray[sVar4].originY;
  sVar4 = (short)DAT_UnitPropertiesDefinedData.DAT_UNIT_SPRITE_DIMENSIONS[unitType][0];
  DAT_UnitsState.units[unitID].spriteWidthUnk = sVar4;
  DAT_UnitsState.units[unitID].spriteHeightUnk =
       (short)DAT_UnitPropertiesDefinedData.DAT_UNIT_SPRITE_DIMENSIONS[unitType][1];
  iVar2 = DAT_UnitsState.units[unitID].unknownV;
  sVar1 = DAT_UnitsState.units[unitID].spriteHeightUnk;
  DAT_UnitsState.units[unitID].drawXOffset = DAT_UnitsState.units[unitID].field22_0x2a - sVar4 / 2;
  DAT_UnitsState.units[unitID].someDrawYOffset = ((short)iVar2 - sVar1) + 3;
  sVar4 = (short)DAT_UnitPropertiesDefinedData.DAT_UNIT_MOVEMENT_SPEED_ARRAY[unitType];
  DAT_UnitsState.units[unitID].movementSpeed = sVar4;
  DAT_UnitsState.units[unitID].calculatedMovementSpeed = sVar4;
  DAT_UnitsState.units[unitID].field216_0x354 = 0;
  DAT_UnitsState.units[unitID].field215_0x350 = 0;
  iVar2 = DAT_UnitPropertiesDefinedData.DAT_BASE_HP[unitType];
  DAT_UnitsState.units[unitID].maxHealth = iVar2;
  DAT_UnitsState.units[unitID].health = iVar2;
  if (iVar2 == 0) {
    sVar4 = 100;
  }
  else {
    sVar4 = (short)((iVar2 * 100) / iVar2);
  }
  DAT_UnitsState.units[unitID].healthPercentage = sVar4;
  bVar3 = DAT_UnitsState.units[unitID].firstNameIndex;
  DAT_UnitsState.units[unitID].healthbar =
       (sVar4 / 10 + (sVar4 >> 0xf)) - (short)((longlong)(int)sVar4 * 0x66666667 >> 0x3f);
  DAT_UnitsState.units[unitID].unitCanClimb =
       (short)DAT_UnitPropertiesDefinedData.DAT_UNIT_CLIMB[unitType];
  DAT_UnitsState.units[unitID].someUnitStat4 =
       (short)DAT_UnitPropertiesDefinedData.DAT_SomeUnitStatMatrix4[unitType];
  DAT_UnitsState.units[unitID].graphicSize =
       (short)DAT_UnitPropertiesDefinedData.DAT_GRAPHIC_SIZE[unitType];
  DAT_UnitsState.units[unitID].someUnitStat2_meleeDamageUnk =
       (short)DAT_UnitPropertiesDefinedData.DAT_UNIT_CAN_MELEE[unitType];
  DAT_UnitsState.units[unitID].enemyNoticeFrequencyUnk =
       DAT_UnitPropertiesDefinedData.DAT_UNIT_ENEMY_NOTICE_RANGE[unitType];
  DAT_UnitsState.units[unitID].moveableUnk =
       (short)DAT_UnitPropertiesDefinedData.DAT_UNIT_MOVABLE[unitType];
  if ((((((char)bVar3 < '\x01') || (unitType == UT_BREWER)) || (unitType == UT_TANNER)) ||
      ((unitType == UT_LADY || (unitType == UT_MOTHER)))) ||
     ((unitType == UT_JUGGLER || ((unitType == UT_FIREEATER || (unitType == UT_PRIEST)))))) {
    assignNameToUnit(&DAT_UnitsState,unitID);
  }
  sVar4 = DAT_UnitsState.units[unitID].owner;
  if (sVar4 < 1) {
    bVar3 = 0xff;
    DAT_UnitsState.units[unitID].occupancyOrFlag = 0xff;
  }
  else {
    bVar3 = '\x01' << ((char)sVar4 - 1U & 0x1f);
    DAT_UnitsState.units[unitID].occupancyOrFlag = bVar3;
    bVar3 = ~bVar3;
  }
  DAT_UnitsState.units[unitID].field275_0x3d1 = bVar3;
  DAT_UnitsState.units[unitID].isSelectable_OR_matchTime = 0;
  DAT_UnitsState.units[unitID].field333_0x430 = 0;
  if (unitType != UT_CAGEDOG) {
    DAT_UnitsState.units[unitID].unknownBool01 = 500;
  }
                    /* Assassin */
  if (unitType == UT_A_ASSASSIN) {
    DAT_UnitsState.units[unitID].assassinsMicroDistanceToEnemyUnk = 32000;
  }
  return;
}


// ================= _HoldStrong::Map::Units::UnitsState::setDestinationForUnit @ 0053d3d0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::Units::UnitsState::setDestinationForUnit
          (UnitsState *this,int unitID,uint x,uint y,int reusePathingInfo)

{
  int iVar1;
  short sVar2;
  BOOLEnum BVar3;
  int iVar4;
  uint unitX;
  uint uVar5;
  dword dVar6;
  dword toArea;
  short sVar7;
  uint uVar8;
  
                    /* check by unit type */
  iVar1 = DAT_UnitPropertiesDefinedData.DAT_ABLE_TO_CLIMB_TOWERS
          [(short)DAT_UnitsState.units[unitID].unitType];
  if (((399 < x) || (399 < y)) || (*(char *)(y * 400 + 0x21aec98 + x) == '\0')) {
    DAT_PathFindingState.allAssassinsUnk = 0;
    return FALSE;
  }
  teleportUnitToUnitXAndY(&DAT_UnitsState,unitID);
  BVar3 = unitIsInMoat(&DAT_UnitsState,unitID);
  if (BVar3 != FALSE) {
    DAT_PathFindingState.climbIsIllegal = 1;
  }
  unitX = (uint)DAT_UnitsState.units[unitID].x;
  DAT_UnitsState.units[unitID].climbDataID = 0;
  sVar2 = (short)x;
  DAT_UnitsState.units[unitID].destinationX_2Unk = sVar2;
  sVar7 = (short)y;
  DAT_UnitsState.units[unitID].destinationY_2Unk = sVar7;
  DAT_UnitsState.units[unitID].field297_0x3f4 = 0;
  if ((unitX == x) && (uVar5 = (uint)DAT_UnitsState.units[unitID].y, uVar5 == y)) {
    DAT_UnitsState.units[unitID].destinationYPosition = sVar7;
    DAT_UnitsState.units[unitID].totalSizeOfPathPlan = 0;
    DAT_UnitsState.units[unitID].tunnelerFinishedDigging = 0;
    DAT_UnitsState.units[unitID].currentIndexInPathPlan = 0;
    DAT_UnitsState.units[unitID].destinationXPosition = sVar2;
    iVar1 = DAT_ViewportRenderState.translationMatrix[sVar7].addXgetTile;
    DAT_UnitsState.units[unitID].ladderExitXPosition = DAT_UnitsState.units[unitID].x;
    DAT_UnitsState.units[unitID].ladderExitYPosition = DAT_UnitsState.units[unitID].y;
    DAT_UnitsState.units[unitID].destinationTilePosition = sVar2 + iVar1;
    DAT_UnitsState.units[unitID].previousTilePosition =
         DAT_ViewportRenderState.translationMatrix[uVar5].addXgetTile + unitX;
    DAT_PathFindingState.climbIsIllegal = 0;
    DAT_PathFindingState.allAssassinsUnk = 0;
    return TRUE;
  }
  dVar6 = (dword)(short)DAT_TileMapState.PathConnectionLayer
                        [DAT_ViewportRenderState.translationMatrix[DAT_UnitsState.units[unitID].y].
                         addXgetTile + unitX];
  iVar4 = DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x;
  toArea = (dword)(short)DAT_TileMapState.PathConnectionLayer[iVar4];
  if ((DAT_TileMapState.LogicLayer[iVar4] & 0x30) != 0) {
    DAT_PathFindingState.allAssassinsUnk = 0;
    return FALSE;
  }
  DAT_UnitsState.units[unitID].field132_0x2a8 = DAT_TileMapState.PathConnectionLayer[iVar4];
  if ((iVar1 == 0) && ((DAT_TileMapState.LogicLayer[iVar4] & 0x10000100U) != 0)) {
    DAT_PathFindingState.allAssassinsUnk = 0;
    return FALSE;
  }
  uVar5 = x;
  uVar8 = y;
  if (dVar6 != toArea) {
    if (DAT_PathFindingState.climbIsIllegal == 0) {
      if ((DAT_PathFindingState.allAssassinsUnk == 0) && (reusePathingInfo == 0)) {
        iVar4 = Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                          (&DAT_PathFindingState,(int)DAT_UnitsState.units[unitID].owner,dVar6,
                           toArea,(int)DAT_UnitsState.units[unitID].unitCanClimb);
        sVar2 = (short)iVar4;
        DAT_UnitsState.units[unitID].field132_0x2a8 = sVar2;
        if (sVar2 == 0) goto LAB_0053d63a;
        iVar4 = Navigation::PathFindingState::setClimbBasedOnClosestClimbData
                          (&DAT_PathFindingState,unitID,dVar6,(int)sVar2);
        sVar2 = (short)iVar4;
        DAT_UnitsState.units[unitID].climbDataID = sVar2;
        if (sVar2 == 0) goto LAB_0053d63a;
        iVar4 = Navigation::PathFindingState::registerUnitOnClimbData
                          (&DAT_PathFindingState,(int)sVar2,unitID);
        goto joined_r0x0053d6de;
      }
    }
    else {
      dVar6 = Navigation::PathFindingState::canNavigateFunctionReturnsArea
                        (&DAT_PathFindingState,(int)DAT_UnitsState.units[unitID].owner,toArea,unitX,
                         (int)DAT_UnitsState.units[unitID].y);
      if (dVar6 != toArea) {
        iVar4 = Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                          (&DAT_PathFindingState,(int)DAT_UnitsState.units[unitID].owner,dVar6,
                           toArea,(int)DAT_UnitsState.units[unitID].unitCanClimb);
        sVar2 = (short)iVar4;
        DAT_UnitsState.units[unitID].field132_0x2a8 = sVar2;
        if (sVar2 == 0) goto LAB_0053d63a;
        iVar4 = Navigation::PathFindingState::setClimbBasedOnClosestClimbData
                          (&DAT_PathFindingState,unitID,dVar6,(int)sVar2);
        sVar2 = (short)iVar4;
        DAT_UnitsState.units[unitID].climbDataID = sVar2;
        if (sVar2 == 0) goto LAB_0053d63a;
        iVar4 = Navigation::PathFindingState::registerUnitOnClimbData
                          (&DAT_PathFindingState,(int)sVar2,unitID);
joined_r0x0053d6de:
        uVar5 = DAT_PathFindingState.climbX;
        uVar8 = DAT_PathFindingState.climbY;
        if ((iVar4 != 1) && (uVar5 = x, uVar8 = y, iVar4 == -1)) goto LAB_0053d63a;
      }
    }
  }
  IO::LowLevelMemory::copyData
            (&DAT_LowLevelMemory,0x490,DAT_UnitsState.units + unitID,DAT_UnitsState.units);
  IO::LowLevelMemory::fillMemory_ByteValue
            (&DAT_LowLevelMemory,400,'\0',DAT_UnitsState.units[unitID].pathPlanStart);
  Navigation::PathFindingState::bindPathPlanToAlgorithmStateAndReset
            (&DAT_PathFindingState,DAT_UnitsState.units[unitID].pathPlanStart);
  DAT_PathFindingState.unitX = (int)DAT_UnitsState.units[unitID].x;
  DAT_PathFindingState.unitY = (int)DAT_UnitsState.units[unitID].y;
  if (DAT_UnitsState.units[unitID].isSelectable_OR_matchTime == 0) {
    DAT_PathFindingState.notAllAssassinsUnk = 1;
  }
  if (DAT_UnitsState.units[unitID].field67_0x90 != 0) {
    DAT_PathFindingState.notAllAssassinsUnk = 1;
  }
  DAT_PathFindingState.destinationX = uVar5;
  DAT_PathFindingState.destinationY = uVar8;
  if (reusePathingInfo == 0) {
    dVar6 = Navigation::PathFindingState::doPathfinding
                      (&DAT_PathFindingState,(int)DAT_UnitsState.units[unitID].owner,iVar1);
  }
  else {
    dVar6 = Navigation::PathFindingState::retraceAndCommitPathPlan(&DAT_PathFindingState);
  }
  DAT_PathFindingState.notAllAssassinsUnk = 0;
  if (0 < (int)dVar6) {
    sVar2 = DAT_UnitsState.units[unitID].y;
    DAT_UnitsState.units[unitID].totalSizeOfPathPlan = (short)dVar6;
    DAT_UnitsState.units[unitID].tunnelerFinishedDigging = 2;
    DAT_UnitsState.units[unitID].currentIndexInPathPlan = 0;
    DAT_UnitsState.units[unitID].destinationXPosition = (short)uVar5;
    DAT_UnitsState.units[unitID].destinationYPosition = (short)uVar8;
    iVar1 = DAT_ViewportRenderState.translationMatrix[(short)uVar8].addXgetTile;
    DAT_UnitsState.units[unitID].ladderExitYPosition = sVar2;
    DAT_UnitsState.units[unitID].destinationTilePosition = (short)uVar5 + iVar1;
    sVar7 = DAT_UnitsState.units[unitID].x;
    DAT_UnitsState.units[unitID].ladderExitXPosition = sVar7;
    DAT_UnitsState.units[unitID].previousTilePosition =
         (int)sVar7 + DAT_ViewportRenderState.translationMatrix[sVar2].addXgetTile;
    DAT_UnitsState.units[unitID].cannotClimb = (ushort)(DAT_PathFindingState.climbIsIllegal != 0);
    DAT_PathFindingState.climbIsIllegal = 0;
    DAT_PathFindingState.allAssassinsUnk = 0;
    return TRUE;
  }
LAB_0053d63a:
  DAT_PathFindingState.climbIsIllegal = 0;
  DAT_PathFindingState.allAssassinsUnk = 0;
  DAT_UnitsState.units[unitID].unknownMovementRelated_0x2d2 = 0;
  despawnUnreachableUnit(&DAT_UnitsState,unitID);
  return FALSE;
}


// ================= _HoldStrong::Map::Units::UnitsState::setDestinationNearTargetedBuilding @ 0053dcc0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Units::UnitsState::setDestinationNearTargetedBuilding
          (UnitsState *this,int unitID,int param_2)

{
  short sVar1;
  ushort uVar2;
  short sVar3;
  int iVar4;
  uint uVar5;
  
  sVar1 = DAT_UnitsState.units[unitID].facingDirection;
  uVar2 = DAT_TileMapState.PathConnectionLayer[DAT_UnitsState.units[unitID].tile];
  uVar5 = DAT_UnitsState.units[unitID].targetedBuildingTile;
  sVar3 = DAT_UnitsState.units[unitID].owner;
  DAT_TileMapState.PathConnectionLayer[uVar5] = uVar2;
  Navigation::PathFindingState::findFreeSpaceNextToEnemyDefensiveStructureInSameAreaWithinDistance
            (&DAT_PathFindingState,uVar5,1,(int *)(int)(short)uVar2,(int)sVar3,param_2,(int)sVar1);
  if ((DAT_PathFindingState.searchQueue.destinationsArray[0].tile1 != 0) &&
     (DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper != 0)) {
    sVar1 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent
            [DAT_PathFindingState.searchQueue.destinationsArray[0].tile1];
    uVar5 = DAT_PathFindingState.searchQueue.destinationsArray[0].tile1 -
            DAT_ViewportRenderState.translationMatrix[sVar1].addXgetTile;
    DAT_UnitsState.units[unitID].plannedDestinationX = (short)uVar5;
    DAT_UnitsState.units[unitID].targetingType = 0;
    DAT_PathFindingState.notAllAssassinsUnk = 1;
    DAT_UnitsState.units[unitID].plannedDestinationY = sVar1;
    DAT_UnitsState.units[unitID].state.generic = US_MOVE_TO_DESTINATION;
    setDestinationForUnit(&DAT_UnitsState,unitID,uVar5,(int)sVar1,0);
    if (DAT_UnitsState.units[unitID].field67_0x90 != 0) {
      changeDestinationByAmount(&DAT_UnitsState,unitID,2);
    }
    iVar4 = DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper;
    sVar1 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent
            [DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper];
    DAT_UnitsState.units[unitID].attackAtTileY = sVar1;
    DAT_UnitsState.units[unitID].targetedBuildingTile = iVar4;
    DAT_UnitsState.units[unitID].attackAtTileX =
         (short)iVar4 - (short)DAT_ViewportRenderState.translationMatrix[sVar1].addXgetTile;
    return 1;
  }
  return 0;
}


// ================= _HoldStrong::Map::Units::UnitsState::findNearestEnemyAndHeadTowardsIt @ 0054a7b0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

dword __thiscall
_HoldStrong::Map::Units::UnitsState::findNearestEnemyAndHeadTowardsIt(UnitsState *this,int unitID)

{
  short *psVar1;
  short sVar2;
  ushort uVar3;
  short sVar4;
  UnitStanceEnumShort UVar5;
  UnitInstructionTypeShort UVar6;
  short sVar7;
  short sVar8;
  UnitTypeShort UVar9;
  UnitStateShort UVar10;
  bool bVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  uint uVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  dword dVar22;
  dword _triangleDistanceUnk;
  int _foundEnemyID;
  int _stanceBasedRange;
  int local_44;
  int _enemyIndex;
  short *_ptrEnemyIDArray;
  dword _minDistance;
  int local_24;
  int local_20;
  int _minimumValue;
  dword local_14;
  
  iVar17 = (int)DAT_UnitsState.units[unitID].microXPosition;
  sVar2 = DAT_UnitsState.units[unitID].owner;
  iVar18 = (int)DAT_UnitsState.units[unitID].microYPosition;
  uVar3 = DAT_TileMapState.PathConnectionLayer[DAT_UnitsState.units[unitID].tile];
  DAT_UnitsState.unitDistanceComputationResultUnk = 100000;
  _minDistance = 100000;
  local_14 = 0;
  _minimumValue = 100000;
  _foundEnemyID = 0;
  local_44 = 1;
  bVar11 = false;
  _stanceBasedRange = 0;
  sVar4 = 0;
  if (((DAT_UnitsState.units[unitID].SA != 0) ||
      ((DAT_UnitsState.units[unitID].movementType_OR_targetUnitID != 0 &&
       (DAT_UnitsState.units[unitID].state.generic == US_MOVE_TO_DESTINATION)))) &&
     (iVar12 = (int)DAT_UnitsState.units[unitID].tribeID, iVar12 != 0)) {
    sVar4 = DAT_TribesState.tribes[iVar12].isRallyingUnk;
    UVar5 = DAT_TribesState.tribes[iVar12].unitStance;
    if (UVar5 == USE_DEFENSIVE) {
      _stanceBasedRange = 0x28;
    }
    else if (UVar5 == USE_AGGRESSIVE) {
      _stanceBasedRange = 200;
    }
  }
  UVar6 = DAT_UnitsState.units[unitID].targetingType;
  if (UVar6 == UIT_UNIT_ATTACK_UNIT) {
    bVar11 = true;
    switch(DAT_UnitsState.units[unitID].unitType) {
    case UT_TUNNELER:
    case UT_E_SPEAR:
    case UT_E_PIKE:
    case UT_E_MACE:
    case UT_E_SWORD:
    case UT_E_KNIGHT:
    case UT_E_MONK:
    case UT_LORD:
    case UT_A_SLAVE:
    case UT_A_ASSASSIN:
    case UT_A_SWORDSMAN:
      iVar12 = (int)DAT_UnitsState.units[unitID].tribeID;
      bVar11 = false;
      if (iVar12 != 0) {
        iVar13 = (int)DAT_TribesState.tribes[iVar12].someUnitID;
        if ((iVar13 != 0) &&
           (DAT_UnitsState.units[iVar13].uid == DAT_TribesState.tribes[iVar12].someUnitUID))
        goto LAB_0054a9d5;
      }
      DAT_UnitsState.units[unitID].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
    }
  }
  else if (UVar6 == UIT_ATTACK_LAND) {
    switch(DAT_UnitsState.units[unitID].unitType) {
    case UT_E_SPEAR:
    case UT_E_PIKE:
    case UT_E_MACE:
    case UT_E_SWORD:
    case UT_E_KNIGHT:
    case UT_E_MONK:
    case UT_A_SLAVE:
    case UT_A_ASSASSIN:
    case UT_A_SWORDSMAN:
      if ((-1 < DAT_UnitsState.units[unitID].lookForEnemy) &&
         (DAT_UnitsState.units[unitID].state.generic != US_MELEE_ATTACK)) {
        sVar8 = DAT_UnitsState.units[unitID].attackAtTileX;
        if ((sVar8 == DAT_UnitsState.units[unitID].x) &&
           (DAT_UnitsState.units[unitID].attackAtTileY == DAT_UnitsState.units[unitID].y)) {
          DAT_UnitsState.units[unitID].targetingType = 0;
          break;
        }
        sVar7 = DAT_UnitsState.units[unitID].attackAtTileY;
        DAT_UnitsState.units[unitID].plannedDestinationY = sVar7;
        DAT_UnitsState.units[unitID].plannedDestinationX = sVar8;
        setDestinationForUnit(&DAT_UnitsState,unitID,(int)sVar8,(int)sVar7,0);
        iVar12 = -((int)DAT_UnitsState.units[unitID].totalSizeOfPathPlan / 2);
        DAT_UnitsState.units[unitID].state.generic = US_MOVE_TO_DESTINATION;
        if (-0x33 < iVar12) {
          iVar12 = -0x32;
        }
        DAT_UnitsState.units[unitID].lookForEnemy = (short)iVar12;
      }
LAB_0054a9d5:
      bVar11 = true;
    }
  }
  if (DAT_UnitsState.units[unitID].isSelectable_OR_matchTime == 0) {
    bVar11 = true;
  }
  iVar12 = DAT_GameState.playerDataArray[sVar2].enemies;
  if (iVar12 < 5) {
    local_44 = 5;
  }
  else if (iVar12 < 0xf) {
    local_44 = 2;
  }
  _enemyIndex = 0;
  if (0 < iVar12) {
    _ptrEnemyIDArray = DAT_GameState.playerDataArray[sVar2].enemyIDArray;
    do {
      iVar12 = (int)*_ptrEnemyIDArray;
      iVar13 = (int)DAT_UnitsState.units[iVar12].microXPosition;
      if (iVar13 < iVar17) {
        iVar13 = iVar17 - iVar13;
      }
      else {
        iVar13 = iVar13 - iVar17;
      }
      iVar14 = (int)DAT_UnitsState.units[iVar12].microYPosition;
      if (iVar14 < iVar18) {
        iVar14 = iVar18 - iVar14;
      }
      else {
        iVar14 = iVar14 - iVar18;
      }
      if (iVar13 < iVar14) {
                    /* pythagorean approximation */
        _triangleDistanceUnk = (((iVar13 * 2) / 5) * iVar13) / iVar14 + iVar14;
      }
      else if (iVar13 == 0) {
                    /* fixme: bug: I think this needs to be set not to 0 but to _dY */
        _triangleDistanceUnk = 0;
      }
      else {
        _triangleDistanceUnk = (((iVar14 * 2) / 5) * iVar14) / iVar13 + iVar13;
      }
      if ((int)_triangleDistanceUnk < (int)_minDistance) {
        _minDistance = _triangleDistanceUnk;
      }
      if (((DAT_UnitsState.units[unitID].unitType == UT_A_ASSASSIN) &&
          (DAT_UnitsState.units[iVar12].isSelectable_OR_matchTime != 0)) &&
         ((int)_triangleDistanceUnk < (int)DAT_UnitsState.unitDistanceComputationResultUnk)) {
        DAT_UnitsState.unitDistanceComputationResultUnk = _triangleDistanceUnk;
      }
      if (((!bVar11) && (_stanceBasedRange != 0)) &&
         (-1 < DAT_UnitsState.units[unitID].lookForEnemy)) {
        sVar8 = DAT_UnitsState.units[unitID]._someX_2;
        if (((sVar8 != 0) && (sVar4 == 0)) && (_stanceBasedRange == 0x28)) {
          iVar19 = (int)DAT_UnitsState.units[unitID]._someY_2;
          iVar21 = (int)DAT_UnitsState.units[iVar12].microXPosition;
          iVar13 = sVar8 * 8;
          iVar14 = iVar19 * 8;
          if (iVar13 < iVar21) {
            dVar22 = iVar21 + sVar8 * -8;
          }
          else {
            dVar22 = iVar13 - iVar21;
          }
          iVar13 = (int)DAT_UnitsState.units[iVar12].microYPosition;
          if (iVar14 < iVar13) {
            _triangleDistanceUnk = iVar13 + iVar19 * -8;
          }
          else {
            _triangleDistanceUnk = iVar14 - iVar13;
          }
          if ((int)_triangleDistanceUnk <= (int)dVar22) {
            _triangleDistanceUnk = dVar22;
          }
        }
        dVar22 = _triangleDistanceUnk;
        if ((((int)_triangleDistanceUnk <= _stanceBasedRange) &&
            (DAT_UnitsState.units[iVar12].uid ==
             DAT_GameState.mapAndTime.playerEnemenyUnitUIDShortList[sVar2][_enemyIndex])) &&
           (((_triangleDistanceUnk =
                   _triangleDistanceUnk +
                   DAT_UnitPropertiesDefinedData.DAT_UnitVisionBonus
                   [(int)(DAT_UnitsState.units[unitID].fixedRng + iVar12) % 10] / local_44,
             DAT_UnitsState.units[iVar12].state.generic != US_MELEE_ATTACK ||
             (sVar8 = DAT_UnitsState.units[iVar12].attackedBy,
             _triangleDistanceUnk = (sVar8 * 0x32 + _triangleDistanceUnk) * 2, sVar8 < 3)) &&
            ((((DAT_UnitsState.units[iVar12].huntedBy < 2 ||
               (sVar8 = DAT_UnitsState.units[iVar12].huntedBy,
               _triangleDistanceUnk = _triangleDistanceUnk + sVar8 * 0x32, sVar8 < 3)) ||
              (DAT_UnitsState.units[unitID].movementType_OR_targetUnitID == iVar12)) &&
             (((DAT_UnitsState.units[iVar12].unknownTestAgainst0_1 == 0 ||
               (UVar9 = DAT_UnitsState.units[iVar12].unitType, UVar9 == UT_LIONSHWOLF)) ||
              (UVar9 == UT_CAGEDOG)))))))) {
                    /* unit type switch */
          switch(DAT_UnitsState.units[iVar12].unitType) {
          case UT_PEASANT:
            _triangleDistanceUnk = _triangleDistanceUnk * 8 + 200;
            break;
          default:
            _triangleDistanceUnk = _triangleDistanceUnk * 4 + 200;
            break;
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_A_ARCHER:
          case UT_A_HARCHER:
          case UT_A_FIRETHROWER:
            break;
          case UT_E_SPEAR:
          case UT_E_PIKE:
          case UT_E_MACE:
          case UT_E_SWORD:
          case UT_E_KNIGHT:
          case UT_E_LADDER:
          case UT_E_MONK:
          case UT_A_SLAVE:
          case UT_A_SLINGER:
          case UT_A_ASSASSIN:
          case UT_A_SWORDSMAN:
            _triangleDistanceUnk = _triangleDistanceUnk * 2 + 100;
            break;
          case UT_E_ENGINEER:
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
          case UT_S_MANGONEL:
          case UT_S_TOWER:
          case UT_S_BATTERINGRAM:
          case UT_S_SHIELD:
          case UT_S_BALLISTA:
          case UT_S_FBALLISTA:
            _triangleDistanceUnk = _triangleDistanceUnk + 0x19;
            break;
          case UT_LORD:
            _triangleDistanceUnk =
                 (int)(_triangleDistanceUnk + ((int)_triangleDistanceUnk >> 0x1f & 3U)) >> 2;
          }
          if (DAT_UnitsState.units[unitID].movementType_OR_targetUnitID == iVar12) {
            _triangleDistanceUnk = (int)_triangleDistanceUnk / 2;
          }
          if ((int)_triangleDistanceUnk < _minimumValue) {
            iVar13 = DAT_UnitsState.units[iVar12].tile;
            sVar8 = DAT_UnitsState.units[iVar12].y;
            iVar14 = (int)DAT_UnitsState.units[iVar12].buildingHeight +
                     (int)DAT_UnitsState.units[iVar12].terrainOrClimbHeight;
            local_20 = -1;
            local_24 = 10000;
            iVar19 = 0;
            do {
              iVar21 = DAT_TileMapState.directionTranslationMatrix[sVar8]
                       [DAT_UnitPropertiesDefinedData.field84_0x11cb4[iVar19]] + iVar13;
              if (((DAT_TileMapState.UnitLayer[iVar21] == 0) &&
                  (uVar15 = TileMapState::getTotalHeightAtTile(&DAT_TileMapState,iVar21),
                  iVar14 < (int)(uVar15 + 0x10))) && ((int)(uVar15 - 0x10) < iVar14)) {
                iVar16 = (int)DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar21];
                iVar21 = iVar21 - DAT_ViewportRenderState.translationMatrix[iVar16].addXgetTile;
                iVar20 = iVar21 * 8;
                if (iVar20 < iVar17) {
                  iVar20 = iVar17 + iVar21 * -8;
                }
                else {
                  iVar20 = iVar20 - iVar17;
                }
                if (iVar16 * 8 < iVar18) {
                  iVar21 = iVar18 + iVar16 * -8;
                }
                else {
                  iVar21 = iVar16 * 8 - iVar18;
                }
                if (iVar21 <= iVar20) {
                  iVar21 = iVar20;
                }
                if (iVar21 < local_24) {
                  local_24 = iVar21;
                  local_20 = iVar19;
                }
              }
              iVar19 = iVar19 + 1;
            } while (iVar19 < 8);
            if (-1 < local_20) {
              _minimumValue = _triangleDistanceUnk;
              local_14 = dVar22;
              _foundEnemyID = iVar12;
            }
          }
        }
      }
      _ptrEnemyIDArray = _ptrEnemyIDArray + 1;
      _enemyIndex = _enemyIndex + 1;
    } while (_enemyIndex < DAT_GameState.playerDataArray[sVar2].enemies);
  }
  if (_stanceBasedRange == 0) {
LAB_0054af54:
    if ((DAT_UnitsState.units[unitID].lookForEnemy != 0) ||
       (UVar10 = DAT_UnitsState.units[unitID].state.generic,
       DAT_UnitsState.units[unitID].movementType_OR_targetUnitID = 0,
       UVar10 != US_MOVE_TO_DESTINATION)) goto LAB_0054afbf;
  }
  else {
    if (DAT_UnitsState.units[unitID].lookForEnemy < 0) goto LAB_0054afbf;
    if (bVar11) goto LAB_0054af54;
    if (_foundEnemyID != 0) {
      iVar17 = Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                         (&DAT_PathFindingState,(int)DAT_UnitsState.units[unitID].owner,
                          (int)(short)uVar3,
                          (int)(short)DAT_TileMapState.PathConnectionLayer
                                      [DAT_UnitsState.units[_foundEnemyID].tile],
                          (int)DAT_UnitsState.units[unitID].unitCanClimb);
      if (iVar17 != 0) {
        sVar2 = DAT_UnitsState.units[unitID]._someX_2;
        DAT_UnitsState.units[unitID].state.generic = US_MOVE_TO_DESTINATION;
        DAT_UnitsState.units[unitID].animationCycleNumber = 0;
        if (sVar2 == 0) {
          sVar2 = DAT_UnitsState.units[unitID].destinationY_2Unk;
          DAT_UnitsState.units[unitID]._someX_2 = DAT_UnitsState.units[unitID].destinationX_2Unk;
          DAT_UnitsState.units[unitID]._someY_2 = sVar2;
        }
        TileMapState::findNearestValidDigTileNearTarget
                  (&DAT_TileMapState,(int)DAT_UnitsState.units[unitID].x,
                   (int)DAT_UnitsState.units[unitID].y,(int)DAT_UnitsState.units[_foundEnemyID].x,
                   (int)DAT_UnitsState.units[_foundEnemyID].y);
        setDestinationForUnit
                  (&DAT_UnitsState,unitID,DAT_TileMapState.field155_0x5549a8,
                   DAT_TileMapState.field156_0x5549ac,0);
        iVar17 = -0x1e - local_14;
        DAT_UnitsState.units[unitID].moveDelay = 0;
        if (-0x33 < iVar17) {
          iVar17 = -0x32;
        }
        sVar2 = DAT_UnitsState.units[unitID].movementType_OR_targetUnitID;
        DAT_UnitsState.units[unitID].lookForEnemy = (short)iVar17;
        if (sVar2 != _foundEnemyID) {
          DAT_UnitsState.units[unitID].movementType_OR_targetUnitID = (short)_foundEnemyID;
          psVar1 = &DAT_UnitsState.units[_foundEnemyID].huntedBy;
          *psVar1 = *psVar1 + 1;
        }
        goto LAB_0054afbf;
      }
    }
    DAT_UnitsState.units[unitID].lookForEnemy = -8;
    DAT_UnitsState.units[unitID].movementType_OR_targetUnitID = 0;
  }
  sVar2 = DAT_UnitsState.units[unitID]._someX_2;
  if (sVar2 != 0) {
    setDestinationForUnit
              (&DAT_UnitsState,unitID,(int)sVar2,(int)DAT_UnitsState.units[unitID]._someY_2,0);
    DAT_UnitsState.units[unitID].moveDelay = 0;
    DAT_UnitsState.units[unitID]._someY_2 = 0;
    DAT_UnitsState.units[unitID]._someX_2 = 0;
    DAT_UnitsState.units[unitID].state.generic = US_MOVE_TO_DESTINATION;
  }
LAB_0054afbf:
  if (32000 < (int)_minDistance) {
    _minDistance = 32000;
  }
  return _minDistance;
}


// ================= _HoldStrong::Map::Units::UnitsState::acquireShootTarget @ 0054b0d0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::Units::UnitsState::acquireShootTarget(UnitsState *this,short *unitID)

{
  short *psVar1;
  short *psVar2;
  short *psVar3;
  UnitTypeShort UVar4;
  UnitInstructionTypeShort UVar5;
  int iVar6;
  int iVar7;
  int microY;
  int iVar8;
  int iVar9;
  int iVar10;
  uint y;
  BOOLEnum BVar11;
  int iVar12;
  short sVar13;
  int iVar14;
  uint x;
  int iVar15;
  short sVar16;
  int iVar17;
  UnitInstructionTypeShort *pUVar18;
  undefined8 uVar19;
  int _entityType;
  int local_30;
  int local_2c;
  int _validTargetID;
  int local_10;
  int local_c;
  int local_8;
  
  psVar3 = unitID;
  iVar6 = (int)DAT_UnitsState.units[(int)unitID].owner;
  iVar7 = (int)DAT_UnitsState.units[(int)unitID].microXPosition;
  microY = (int)DAT_UnitsState.units[(int)unitID].microYPosition;
  iVar8 = (int)DAT_UnitsState.units[(int)unitID].buildingHeight +
          (int)DAT_UnitsState.units[(int)unitID].terrainOrClimbHeight;
  iVar17 = 0;
  _validTargetID = 0;
  local_30 = 100000;
  local_8 = 0;
  local_2c = 100000;
  local_10 = 0;
  local_c = 0;
                    /* switch based on unit type */
  switch(DAT_UnitsState.units[(int)unitID].unitType) {
  case UT_E_XBOW:
                    /* crossbow */
    _entityType = 7;
    break;
  default:
                    /* default: */
    _entityType = 1;
    break;
  case UT_S_CATAPULT:
                    /* catapult */
    _entityType = 2;
    if ((DAT_UnitsState.units[(int)unitID].stoneAmmunition < 1) &&
       (DAT_UnitsState.units[(int)unitID].targetingType != UIT_THROW_COW)) {
      DAT_UnitsState.units[(int)unitID].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
      return FALSE;
    }
    break;
  case UT_S_TREBUCHET:
                    /* trebuchet */
    _entityType = 3;
    if ((DAT_UnitsState.units[(int)unitID].stoneAmmunition < 1) &&
       (DAT_UnitsState.units[(int)unitID].targetingType != UIT_THROW_COW)) {
      DAT_UnitsState.units[(int)unitID].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
      return FALSE;
    }
    break;
  case UT_S_MANGONEL:
                    /* mangonel */
    _entityType = 4;
    break;
  case UT_S_BALLISTA:
                    /* ballista */
    _entityType = 0x14;
    break;
  case UT_A_SLINGER:
                    /* slinger */
    _entityType = 0x21;
    break;
  case UT_A_FIRETHROWER:
                    /* fire thrower */
    _entityType = 0x22;
    break;
  case UT_S_FBALLISTA:
                    /* fire ballista */
    _entityType = 0x25;
  }
  iVar9 = DAT_EntityDefinedData.DAT_EntityTypeArrayForProjectileRange[_entityType] *
          DAT_EntityDefinedData.DAT_EntityTypeArrayForProjectileRange[_entityType];
                    /* fetch attacking explicitness */
  if (DAT_UnitsState.units[(int)unitID].targetingType == UIT_UNIT_ATTACK_UNIT) {
                    /* if explicitness = 4 (user selected attack)...
                       fetch the targetedUnitID */
    sVar13 = DAT_UnitsState.units[(int)unitID].targetedUnitID__OR__engineerMannedSiegeEngineRef;
    iVar10 = (int)sVar13;
    if (((DAT_UnitsState.units[iVar10].uid ==
          DAT_UnitsState.units[(int)unitID].
          targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID) &&
        (DAT_UnitsState.units[iVar10].dying == 0)) &&
       (DAT_UnitsState.units[iVar10].logicalState == ULS_NORMAL)) {
      uVar19 = checkIfCitizenUnitIsAliveBasedOnState(iVar10);
      iVar17 = (int)((ulonglong)uVar19 >> 0x20);
      if ((((int)uVar19 == 0) &&
          (DAT_UnitsState.units[iVar10].state.generic != (US_STONE_DEATH_03|US_IDLEUnk))) &&
         (DAT_GameState.mapAndTime.playerTeams[DAT_UnitsState.units[iVar10].owner] !=
          DAT_GameState.mapAndTime.playerTeams[iVar6])) {
        psVar1 = &DAT_UnitsState.units[iVar10].microYPosition;
        psVar2 = &DAT_UnitsState.units[iVar10].microXPosition;
        iVar14 = ((int)(microY + (microY >> 0x1f & 7U)) >> 3) -
                 ((int)((int)*psVar1 + ((int)*psVar1 >> 0x1f & 7U)) >> 3);
        iVar17 = ((int)(iVar7 + (iVar7 >> 0x1f & 7U)) >> 3) -
                 ((int)((int)*psVar2 + ((int)*psVar2 >> 0x1f & 7U)) >> 3);
        if (iVar17 * iVar17 + iVar14 * iVar14 <= iVar9) {
          psVar3 = &DAT_UnitsState.units[iVar10].terrainOrClimbHeight;
          iVar6 = Entities::EntityState::arrowShootingRelated
                            (&DAT_EntityState,iVar7,microY,iVar8 + 0x1e,(int)*psVar2,(int)*psVar1,
                             DAT_UnitsState.units[iVar10].buildingHeight + 0x1a +
                             (int)DAT_UnitsState.units[iVar10].terrainOrClimbHeight);
          if (((iVar6 < 1) ||
              (UVar4 = DAT_UnitsState.units[(int)unitID].unitType, UVar4 == UT_S_MANGONEL)) ||
             (UVar4 == UT_S_BALLISTA)) {
            if (DAT_UnitsState.units[(int)unitID].unitType == UT_HUNTER) {
              return FALSE;
            }
            DAT_UnitsState.units[(int)unitID].shootTargetedUnit = -2;
            DAT_UnitsState.units[(int)unitID].shootTargetMicroX = *psVar2;
            DAT_UnitsState.units[(int)unitID].shootTargetMicroY = *psVar1;
            DAT_UnitsState.units[(int)unitID].shootTargetZ = *psVar3;
            return TRUE;
          }
          DAT_UnitsState.units[(int)unitID].shootTargetedUnit = sVar13;
          DAT_UnitsState.units[(int)unitID].targetUID = DAT_UnitsState.units[iVar10].uid;
          DAT_UnitsState.units[(int)unitID].distanceToEnemyUnitLadders = (short)iVar6;
          DAT_UnitsState.units[(int)unitID].shootTargetMicroX = *psVar2;
          DAT_UnitsState.units[(int)unitID].shootTargetMicroY = *psVar1;
          DAT_UnitsState.units[(int)unitID].shootTargetZ = *psVar3;
          if (100 < iVar6) {
            DAT_UnitsState.units[(int)unitID].jugglerCount = 0;
            DAT_UnitsState.units[iVar10].field250_0x39a = 1;
            return TRUE;
          }
          iVar6 = (int)*psVar3 + (int)DAT_UnitsState.units[iVar10].buildingHeight;
          iVar7 = (int)DAT_UnitsState.units[(int)unitID].buildingHeight +
                  (int)DAT_UnitsState.units[(int)unitID].terrainOrClimbHeight;
          if (iVar6 + 0x46 < iVar7) {
            DAT_UnitsState.units[(int)unitID].jugglerCount = 1;
            DAT_UnitsState.units[iVar10].field250_0x39a = 1;
            return TRUE;
          }
          DAT_UnitsState.units[(int)unitID].jugglerCount = (iVar6 + -0x46 <= iVar7) - 1;
          DAT_UnitsState.units[iVar10].field250_0x39a = 1;
          return TRUE;
        }
        if (DAT_GameSynchronyState.currentPlayerFullIDArray[DAT_UnitsState.units[(int)unitID].owner]
            != -1) {
          return FALSE;
        }
        iVar17 = 0;
      }
    }
                    /* fixme */
    sVar13 = DAT_UnitsState.units[(int)unitID]._someX_2;
    sVar16 = (short)iVar17;
                    /* fixmefixme */
    DAT_UnitsState.units[(int)unitID].targetedUnitID__OR__engineerMannedSiegeEngineRef = sVar16;
    DAT_UnitsState.units[(int)unitID].shootTargetedUnit = sVar16;
    DAT_UnitsState.units[(int)unitID].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
    if (sVar13 != sVar16) {
      setDestinationForUnit
                (&DAT_UnitsState,(int)unitID,(int)sVar13,
                 (int)DAT_UnitsState.units[(int)unitID]._someY_2,0);
      DAT_UnitsState.units[(int)unitID]._someX_2 = 0;
      DAT_UnitsState.units[(int)unitID]._someY_2 = 0;
      DAT_UnitsState.units[(int)unitID].moveDelay = 0;
      DAT_UnitsState.units[(int)unitID].targetedBuildingTile = 0;
      DAT_UnitsState.units[(int)unitID].state.generic = US_MOVE_TO_DESTINATION;
      return TRUE;
    }
  }
  pUVar18 = &DAT_UnitsState.units[(int)unitID].targetingType;
  UVar5 = *pUVar18;
  if (UVar5 == UIT_LIGHT_PITCH) {
                    /* get the workplace building id */
    sVar13 = DAT_UnitsState.units[(int)unitID].targetID_OR_targetBuildingID;
    if ((DAT_TileMapState.pitchDitches[sVar13].uid ==
         DAT_UnitsState.units[(int)unitID].
         targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID) &&
       (iVar6 = Entities::EntityState::isBrazierNearby
                          (&DAT_EntityState,(int)DAT_UnitsState.units[(int)unitID].x,
                           (int)DAT_UnitsState.units[(int)unitID].y,
                           (int)DAT_UnitsState.units[(int)unitID].buildingHeight +
                           (int)DAT_UnitsState.units[(int)unitID].terrainOrClimbHeight), iVar6 != 0)
       ) {
      DAT_UnitsState.units[(int)unitID].shootTargetMicroX =
           DAT_TileMapState.pitchDitches[sVar13].x * 8 + 4;
      DAT_UnitsState.units[(int)unitID].shootTargetMicroY =
           DAT_TileMapState.pitchDitches[sVar13].y * 8 + 4;
      DAT_UnitsState.units[(int)unitID].shootTargetZ =
           (ushort)DAT_TileMapState.HeightLayer[DAT_TileMapState.pitchDitches[sVar13].tile];
      DAT_UnitsState.units[(int)unitID].shootTargetedUnit = -1;
      return TRUE;
    }
  }
  else if (UVar5 == UIT_ATTACK_BUILDING) {
    sVar13 = DAT_UnitsState.units[(int)unitID].targetID_OR_targetBuildingID;
    if (DAT_BuildingsState.buildings[sVar13].uid ==
        DAT_UnitsState.units[(int)unitID].
        targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID) {
      DAT_UnitsState.units[(int)unitID].shootTargetMicroX =
           DAT_BuildingsState.buildings[sVar13].x * 8 +
           (short)((int)(DAT_BuildingsState.buildings[sVar13].widthOrHeight * 8) / 2);
      DAT_UnitsState.units[(int)unitID].shootTargetMicroY =
           DAT_BuildingsState.buildings[sVar13].y * 8 +
           (short)((int)(DAT_BuildingsState.buildings[sVar13].widthOrHeight * 8) / 2);
      DAT_UnitsState.units[(int)unitID].shootTargetZ =
           DAT_BuildingsState.buildings[sVar13].terrainHeightUnk;
      DAT_UnitsState.units[(int)unitID].shootTargetedUnit = -1;
      return TRUE;
    }
  }
  else if (UVar5 == UIT_ATTACK_WALL) {
    y = (uint)DAT_UnitsState.units[(int)unitID].attackAtTileY;
    x = (uint)DAT_UnitsState.units[(int)unitID].attackAtTileX;
    iVar6 = DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x;
    BVar11 = Rendering::ViewportRenderState::xyAreValid(&DAT_ViewportRenderState,x,y);
    if ((BVar11 != FALSE) && ((DAT_TileMapState.LogicLayer[iVar6] & 0x100U) != 0)) {
      DAT_UnitsState.units[(int)unitID].shootTargetMicroX =
           DAT_UnitsState.units[(int)unitID].attackAtTileX * 8;
      DAT_UnitsState.units[(int)unitID].shootTargetMicroY =
           DAT_UnitsState.units[(int)unitID].attackAtTileY * 8;
      DAT_UnitsState.units[(int)unitID].shootTargetZ =
           (short)((int)((uint)DAT_TileMapState.HeightLayer[iVar6] -
                        (uint)DAT_TileMapState.DefaultHeightLayer[iVar6]) / 2) +
           (ushort)DAT_TileMapState.DefaultHeightLayer[iVar6];
      DAT_UnitsState.units[(int)unitID].shootTargetedUnit = -1;
      return TRUE;
    }
  }
  else {
    if ((UVar5 != UIT_ATTACK_LAND) && (UVar5 != UIT_THROW_COW)) {
      if (_entityType == 2) {
        return FALSE;
      }
      if (_entityType == 3) {
        return FALSE;
      }
      if (DAT_GameState.playerDataArray[iVar6].enemies <= iVar17) {
        return FALSE;
      }
      unitID = DAT_GameState.playerDataArray[iVar6].enemyIDArray;
      do {
        iVar10 = (int)*unitID;
        if ((DAT_UnitsState.units[iVar10].dying != 0) ||
           (DAT_UnitsState.units[iVar10].uid != *(int *)(iVar6 * 10000 + 0x11a66f0 + iVar17 * 4)))
        goto switchD_0054ba67_caseD_1f;
        switch(DAT_UnitsState.units[iVar10].unitType) {
        case UT_ANTELOPESHDEER:
          if (DAT_UnitsState.units[(int)psVar3].unitType != UT_HUNTER)
          goto switchD_0054ba67_caseD_1f;
          break;
        case UT_LIONSHWOLF:
          sVar13 = DAT_UnitsState.units[iVar10].tribeID;
          if ((DAT_TribesState.tribes[sVar13].unknownBool02 != 0) ||
             ((DAT_TribesState.tribes[sVar13].unknownBool01 == 0 &&
              ((DAT_UnitsState.units[iVar10].state.generic != 0xcf ||
               (DAT_UnitsState.units
                [DAT_UnitsState.units[iVar10].targetedUnitID__OR__engineerMannedSiegeEngineRef].
                unknownTestAgainst0_1 != 0)))))) goto switchD_0054ba67_caseD_1f;
          break;
        case UT_RABBIT:
          iVar14 = (int)DAT_UnitsState.units[(int)psVar3].tribeID;
          if (((DAT_UnitsState.units[(int)psVar3].unitType == UT_HUNTER) || (iVar14 < 1)) ||
             (DAT_TribesState.tribes[iVar14].field71_0x212 == 0)) goto switchD_0054ba67_caseD_1f;
          break;
        case UT_CAGEDOG:
          if (DAT_GameState.mapAndTime.playerTeams
              [DAT_UnitsState.units[iVar10].displayColorPlayerID] ==
              DAT_GameState.mapAndTime.playerTeams[DAT_UnitsState.units[(int)psVar3].owner])
          goto switchD_0054ba67_caseD_1f;
          break;
        case UT_A_ASSASSIN:
          if (0xa0 < DAT_UnitsState.units[iVar10].assassinsMicroDistanceToEnemyUnk)
          goto switchD_0054ba67_caseD_1f;
        }
        iVar14 = (int)DAT_UnitsState.units[iVar10].microYPosition;
        iVar12 = (int)DAT_UnitsState.units[iVar10].microXPosition;
        iVar15 = ((int)(microY + (microY >> 0x1f & 7U)) >> 3) -
                 ((int)(iVar14 + (iVar14 >> 0x1f & 7U)) >> 3);
        iVar14 = ((int)(iVar7 + (iVar7 >> 0x1f & 7U)) >> 3) -
                 ((int)(iVar12 + (iVar12 >> 0x1f & 7U)) >> 3);
        if (iVar9 < iVar14 * iVar14 + iVar15 * iVar15) goto switchD_0054ba67_caseD_1f;
        iVar14 = (int)DAT_UnitsState.units[iVar10].microXPosition;
        if (iVar14 < iVar7) {
          iVar14 = iVar7 - iVar14;
        }
        else {
          iVar14 = iVar14 - iVar7;
        }
        iVar12 = (int)DAT_UnitsState.units[iVar10].microYPosition;
        if (iVar12 < microY) {
          iVar15 = microY - iVar12;
        }
        else {
          iVar15 = iVar12 - microY;
        }
        if (iVar14 < iVar15) {
          iVar14 = iVar15;
        }
        iVar14 = iVar14 + DAT_UnitsState.units[iVar10].field282_0x3dc * 0x32;
        if (_entityType == 4) {
          switch(DAT_UnitsState.units[iVar10].unitType) {
          case UT_E_ENGINEER:
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
          case UT_S_MANGONEL:
          case UT_S_TOWER:
          case UT_S_BATTERINGRAM:
          case UT_S_SHIELD:
          case UT_S_BALLISTA:
          case UT_S_FBALLISTA:
            break;
          default:
            if (DAT_GameSynchronyState.currentPlayerFullIDArray
                [DAT_UnitsState.units[(int)psVar3].owner] != -1) goto switchD_0054ba67_caseD_1f;
            if (DAT_UnitsState.units[iVar10].isSelectable_OR_matchTime == 0) {
              iVar14 = (iVar14 * 5 + 0x32) * 2;
            }
            else {
              iVar14 = iVar14 * 3 + 100;
            }
          }
          goto joined_r0x0054ba0c;
        }
        if (_entityType == 0x14) {
          switch(DAT_UnitsState.units[iVar10].unitType) {
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_E_SPEAR:
          case UT_E_MACE:
          case UT_E_LADDER:
          case UT_A_ARCHER:
          case UT_A_SLAVE:
          case UT_A_SLINGER:
          case UT_A_ASSASSIN:
          case UT_A_HARCHER:
switchD_0054ba37_caseD_16:
            iVar14 = iVar14 * 5 + 200;
            break;
          case UT_E_PIKE:
          case UT_E_SWORD:
          case UT_E_KNIGHT:
          case UT_A_SWORDSMAN:
            break;
          case UT_E_ENGINEER:
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
          case UT_S_MANGONEL:
          case UT_LORD:
          case UT_S_TOWER:
          case UT_S_BATTERINGRAM:
          case UT_S_SHIELD:
          case UT_S_BALLISTA:
          case UT_A_FIRETHROWER:
          case UT_S_FBALLISTA:
switchD_0054ba37_caseD_1e:
            iVar14 = iVar14 * 2 + 100;
            break;
          default:
switchD_0054ba37_caseD_1f:
            iVar14 = (iVar14 * 5 + 200) * 2;
          }
          goto switchD_0054ba37_caseD_19;
        }
        if (_entityType != 0x25) {
          if ((DAT_UnitsState.units[iVar10].field306_0x3ff != 0) &&
             (DAT_GameSynchronyState.currentPlayerFullIDArray[DAT_UnitsState.units[iVar10].owner] ==
              -1)) {
            iVar14 = iVar14 / 3;
          }
          switch(DAT_UnitsState.units[iVar10].unitType) {
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_A_ARCHER:
          case UT_A_HARCHER:
            iVar14 = iVar14 + 0x4b;
            break;
          case UT_E_SPEAR:
          case UT_E_PIKE:
          case UT_E_MACE:
          case UT_E_SWORD:
          case UT_E_KNIGHT:
          case UT_A_SLAVE:
          case UT_A_SLINGER:
          case UT_A_ASSASSIN:
          case UT_A_SWORDSMAN:
            goto switchD_0054ba37_caseD_16;
          case UT_E_LADDER:
            iVar14 = iVar14 * 7 + 300;
            break;
          case UT_E_ENGINEER:
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
          case UT_LORD:
            goto switchD_0054ba37_caseD_1e;
          default:
            goto switchD_0054ba37_caseD_1f;
          case UT_S_MANGONEL:
          case UT_S_BALLISTA:
          case UT_A_FIRETHROWER:
          case UT_S_FBALLISTA:
            break;
          }
          goto switchD_0054ba37_caseD_19;
        }
        switch(DAT_UnitsState.units[iVar10].unitType) {
        case UT_E_ARCHER:
        case UT_E_XBOW:
        case UT_E_SPEAR:
        case UT_E_MACE:
        case UT_E_LADDER:
        case UT_A_ARCHER:
        case UT_A_SLAVE:
        case UT_A_SLINGER:
        case UT_A_ASSASSIN:
        case UT_A_HARCHER:
switchD_0054ba67_caseD_16:
          iVar14 = iVar14 * 5 + 200;
          break;
        case UT_E_PIKE:
        case UT_E_SWORD:
        case UT_E_KNIGHT:
        case UT_A_SWORDSMAN:
          break;
        case UT_E_ENGINEER:
        case UT_S_CATAPULT:
        case UT_S_TREBUCHET:
        case UT_S_MANGONEL:
        case UT_S_TOWER:
        case UT_S_BATTERINGRAM:
        case UT_S_SHIELD:
        case UT_S_BALLISTA:
        case UT_A_FIRETHROWER:
        case UT_S_FBALLISTA:
          iVar14 = iVar14 * 2 + 100;
          break;
        default:
          goto switchD_0054ba67_caseD_1f;
        case UT_LORD:
          if (DAT_GameSynchronyState.currentPlayerFullIDArray[iVar6] != -1)
          goto switchD_0054ba67_caseD_16;
          goto switchD_0054ba67_caseD_1f;
        }
joined_r0x0054ba0c:
        if (iVar14 != -1) {
switchD_0054ba37_caseD_19:
          if (((iVar14 < local_30) || (iVar14 < local_2c)) &&
             (iVar12 = Entities::EntityState::arrowShootingRelated
                                 (&DAT_EntityState,iVar7,microY,iVar8 + 0x1e,
                                  (int)DAT_UnitsState.units[iVar10].microXPosition,iVar12,
                                  DAT_UnitsState.units[iVar10].buildingHeight + 0x1a +
                                  (int)DAT_UnitsState.units[iVar10].terrainOrClimbHeight),
             0 < iVar12)) {
            if (iVar14 < local_30) {
              local_30 = iVar14;
              _validTargetID = iVar10;
              local_8 = iVar12;
            }
            if ((DAT_UnitsState.units[iVar10].field250_0x39a == 0) && (iVar14 < local_2c)) {
              local_2c = iVar14;
              local_10 = iVar10;
              local_c = iVar12;
            }
          }
        }
switchD_0054ba67_caseD_1f:
        unitID = unitID + 1;
        iVar17 = iVar17 + 1;
        if (DAT_GameState.playerDataArray[iVar6].enemies <= iVar17) {
          if (_validTargetID == 0) {
            return FALSE;
          }
          if ((local_10 != 0) && (local_2c < (local_30 * 3) / 2)) {
            _validTargetID = local_10;
            local_8 = local_c;
          }
          if (_entityType == 4) {
            DAT_UnitsState.units[(int)psVar3].shootTargetedUnit = -2;
            DAT_UnitsState.units[(int)psVar3].shootTargetMicroX =
                 DAT_UnitsState.units[_validTargetID].microXPosition;
            DAT_UnitsState.units[(int)psVar3].shootTargetMicroY =
                 DAT_UnitsState.units[_validTargetID].microYPosition;
            DAT_UnitsState.units[(int)psVar3].shootTargetZ =
                 DAT_UnitsState.units[_validTargetID].terrainOrClimbHeight;
            return TRUE;
          }
          sVar13 = (short)_validTargetID;
          if ((_entityType == 0x25) || (_entityType == 0x14)) {
            DAT_UnitsState.units[(int)psVar3].shootTargetedUnit = sVar13;
            DAT_UnitsState.units[(int)psVar3].targetUID = DAT_UnitsState.units[_validTargetID].uid;
            DAT_UnitsState.units[(int)psVar3].distanceToEnemyUnitLadders = (short)local_8;
            DAT_UnitsState.units[(int)psVar3].shootTargetMicroX =
                 DAT_UnitsState.units[_validTargetID].microXPosition;
            DAT_UnitsState.units[(int)psVar3].shootTargetMicroY =
                 DAT_UnitsState.units[_validTargetID].microYPosition;
            DAT_UnitsState.units[(int)psVar3].shootTargetZ =
                 DAT_UnitsState.units[_validTargetID].terrainOrClimbHeight;
            return TRUE;
          }
          psVar1 = &DAT_UnitsState.units[_validTargetID].field282_0x3dc;
          *psVar1 = *psVar1 + 1;
          DAT_UnitsState.units[(int)psVar3].shootTargetedUnit = sVar13;
          DAT_UnitsState.units[(int)psVar3].field283_0x3de = sVar13;
          DAT_UnitsState.units[(int)psVar3].targetUID = DAT_UnitsState.units[_validTargetID].uid;
          DAT_UnitsState.units[(int)psVar3].distanceToEnemyUnitLadders = (short)local_8;
          if (100 < local_8) {
            DAT_UnitsState.units[(int)psVar3].jugglerCount = 0;
            DAT_UnitsState.units[_validTargetID].field250_0x39a = 1;
            return TRUE;
          }
          iVar6 = (int)DAT_UnitsState.units[_validTargetID].terrainOrClimbHeight +
                  (int)DAT_UnitsState.units[_validTargetID].buildingHeight;
          iVar7 = (int)DAT_UnitsState.units[(int)psVar3].buildingHeight +
                  (int)DAT_UnitsState.units[(int)psVar3].terrainOrClimbHeight;
          if (iVar6 + 0x46 < iVar7) {
            DAT_UnitsState.units[(int)psVar3].jugglerCount = 1;
            DAT_UnitsState.units[_validTargetID].field250_0x39a = 1;
            return TRUE;
          }
          DAT_UnitsState.units[(int)psVar3].jugglerCount = (iVar6 + -0x46 <= iVar7) - 1;
          DAT_UnitsState.units[_validTargetID].field250_0x39a = 1;
          return TRUE;
        }
      } while( true );
    }
    sVar13 = DAT_UnitsState.units[(int)unitID].attackAtTileY;
    sVar16 = DAT_UnitsState.units[(int)unitID].attackAtTileX;
    DAT_UnitsState.units[(int)unitID].jugglerCount = -1;
    BVar11 = Rendering::ViewportRenderState::xyAreValid
                       (&DAT_ViewportRenderState,(int)sVar16,(int)sVar13);
    if (BVar11 != FALSE) {
      sVar16 = DAT_UnitsState.units[(int)unitID].attackAtTileX;
      DAT_UnitsState.units[(int)unitID].shootTargetMicroX = sVar16 * 8;
      DAT_UnitsState.units[(int)unitID].shootTargetedUnit = -1;
      DAT_UnitsState.units[(int)unitID].shootTargetMicroY = sVar13 * 8;
      DAT_UnitsState.units[(int)unitID].shootTargetZ =
           (ushort)*(byte *)(DAT_ViewportRenderState.translationMatrix[sVar13].addXgetTile +
                             0x1d32c38 + (int)sVar16);
      return TRUE;
    }
  }
  *pUVar18 = UIT_NO_INSTRUCTION_OR_MOVEUnk;
  return FALSE;
}


// ================= _HoldStrong::Global::UpdateAssassin @ 005744d0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Global::UpdateAssassin(void)

{
  int *piVar1;
  short *psVar2;
  byte *pbVar3;
  char *pcVar4;
  byte bVar5;
  short sVar6;
  UnitTypeShort UVar7;
  UnitInstructionTypeShort UVar8;
  BOOLEnum BVar9;
  uint uVar10;
  int extraout_EAX;
  DWORD DVar11;
  uint uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  uint uVar16;
  bool bVar17;
  eSFX sfxOffsetInArray;
  
  uVar10 = DAT_CurrentUnitSlotID;
  iVar15 = (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner;
  piVar1 = &DAT_GameState.playerDataArray[iVar15].armySize;
  *piVar1 = *piVar1 + 1;
  piVar1 = &DAT_GameState.playerDataArray[iVar15].countAssassins;
  *piVar1 = *piVar1 + 1;
  DAT_UnitsState.units[uVar10].gmIDUnk = 0xc6;
  DAT_UnitsState.units[uVar10].imageIDUnk = 0;
  DAT_UnitsState.units[uVar10].isSelectable_OR_matchTime = 1;
  Map::Units::TribesState::addUnitToNewTribe(&DAT_TribesState,uVar10);
  uVar10 = DAT_CurrentUnitSlotID;
  if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic != US_MELEE_ATTACK) {
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageID2 = 0;
    DAT_UnitsState.units[uVar10].drawYOffset = 0;
  }
  uVar12 = DAT_CurrentUnitSlotID;
  switch(DAT_UnitsState.units[uVar10].state.generic) {
  case US_DETERMINE_NEXT_STATEUnk:
    DAT_UnitsState.units[uVar10].substate = -1;
    DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].field320_0x413 = 0;
    psVar2 = &DAT_UnitsState.units[uVar10].idleCounterUnk;
    *psVar2 = *psVar2 + 1;
    uVar12 = DAT_CurrentUnitSlotID;
    if (DAT_UnitsState.units[uVar10].isDisappearingUnk != 0) {
      pbVar3 = &DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown;
      *pbVar3 = *pbVar3 - 1;
      if (-1 < (char)*pbVar3) {
        return;
      }
      DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown = 0;
      DAT_UnitsState.units[uVar10].isDisappearingUnk = 0;
      return;
    }
    if (DAT_UnitsState.units[uVar10].goToRallyPoint == 0) {
      DAT_UnitsState.units[uVar10].state.generic = US_IDLEUnk;
      return;
    }
    DAT_UnitsState.units[uVar10].goToRallyPoint = 0;
    DAT_UnitsState.units[uVar10].state.generic = 0x69;
    iVar13 = Map::Buildings::BuildingsState::getKeepLocationForAIUnit
                       (&DAT_BuildingsState,iVar15,0xd,uVar12);
    goto joined_r0x005746a3;
  case US_IDLEUnk:
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].animationSpeed = 5;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].field134_0x2ac = 10;
    DAT_UnitsState.units[uVar10].SA = 1;
    psVar2 = &DAT_UnitsState.units[uVar10].idleCounterUnk;
    *psVar2 = *psVar2 + 1;
    uVar12 = uVar12 & 3;
    iVar15 = DAT_UnitsState.units[uVar10].animationCycleNumber;
    if (uVar12 == 0) {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          DAT_AssassinAnimationFrames0[iVar15];
    }
    else if (uVar12 == 1) {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          DAT_AssassinAnimationFrames1[iVar15];
    }
    else if (uVar12 == 2) {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          DAT_AssassinAnimationFrames2[iVar15];
    }
    else {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          DAT_AssassinAnimationFrames4[iVar15];
    }
    DAT_UnitsState.units[uVar10].animationFrame = iVar15;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = 0x311;
      DAT_UnitHasBecomeIdle = 1;
    }
    else {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar15 + 0x310;
    }
    uVar12 = DAT_CurrentUnitSlotID;
    UVar8 = DAT_UnitsState.units[uVar10].targetingType;
    if ((UVar8 == UIT_DIG_MOAT) || (UVar8 == UIT_FILL_MOAT)) {
      DAT_UnitHasBecomeIdle = 1;
    }
    else if (DAT_UnitHasBecomeIdle == 0) {
      return;
    }
    DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
    DAT_UnitsState.units[uVar10].state.generic = US_DETERMINE_NEXT_STATEUnk;
    Map::Units::UnitsState::moveToFreeTileNearby(&DAT_UnitsState,uVar12);
    return;
  case US_MOVE_TO_DESTINATION:
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0x10;
    DAT_UnitsState.units[uVar10].animationSheetFrameOffset = 1;
    DAT_UnitsState.units[uVar10].field320_0x413 = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    if (DAT_TribesState.tribes[DAT_UnitsState.units[uVar10].tribeID].isRallyingUnk != 0) {
      DAT_UnitsState.units[uVar10].SA = 1;
    }
    sVar6 = DAT_UnitsState.units[uVar10].moveInstructionSpeedDelayTracker;
    if (sVar6 == 0) {
      if (DAT_UnitsState.units[uVar10].closestEnemyMicroDistance < 0xc1) {
        DAT_UnitsState.units[uVar10].animationSheetFrameOffset = 0x81;
        goto LAB_0057475b;
      }
    }
    else if (sVar6 < 0x47) {
LAB_0057475b:
      DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    }
    else {
      DAT_UnitsState.units[uVar10].stateBasedSpeed = -1;
      DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    }
    uVar12 = DAT_CurrentUnitSlotID;
    BVar9 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,DAT_CurrentUnitSlotID)
    ;
    if (BVar9 != FALSE) {
      DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
      DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
      DAT_UnitsState.units[uVar10].state.generic = US_DETERMINE_NEXT_STATEUnk;
      if (DAT_TribesState.tribes[DAT_UnitsState.units[uVar10].tribeID].tribeBehaviorType ==
          STBT_0x400) {
        DAT_UnitsState.units[uVar10].state.generic = US_DISAPPEAR;
      }
      iVar15 = Map::Units::UnitsState::handleUnitMovementWhenTargetingBuildings
                         (&DAT_UnitsState,uVar12);
      if (0 < iVar15) {
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].unknownDigMoatOrWallAttackFlag1015 != 0x3f7)
        {
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_MELEE_ATTACK_WALL;
          return;
        }
        iVar15 = Map::TileMapState::returnOwnedMoatAtTile
                           (&DAT_TileMapState,
                            DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetedBuildingTile);
        uVar10 = DAT_CurrentUnitSlotID;
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].digTileTarget = iVar15;
        if (iVar15 == 0) {
          DAT_UnitsState.units[uVar10].state.generic = US_DETERMINE_NEXT_STATEUnk;
          return;
        }
        DAT_UnitsState.units[uVar10].state.generic = US_DIG;
        sVar6 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent
                [DAT_UnitsState.units[uVar10].targetedBuildingTile];
        DAT_UnitsState.units[uVar10].digTileY__OR__countLifeCycleEngineersSentToManSiegeEngine =
             sVar6;
        DAT_UnitsState.units[uVar10].
        digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 =
             (short)DAT_UnitsState.units[uVar10].targetedBuildingTile -
             (short)DAT_ViewportRenderState.translationMatrix[sVar6].addXgetTile;
        return;
      }
    }
    break;
  case 0x68:
    DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    DAT_UnitsState.units[uVar10].animationSheetFrameOffset = 0x181;
    return;
  case 0x69:
                    /* Rally state */
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].SA = 1;
    DAT_UnitsState.units[uVar10].stateBasedSpeed = 1;
    DAT_UnitsState.units[uVar10].animationSheetFrameOffset = 1;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0x10;
    DAT_UnitsState.units[uVar10].calculatedMovementSpeed =
         DAT_UnitsState.units[uVar10].movementSpeed;
    psVar2 = &DAT_UnitsState.units[uVar10].idleCounterUnk;
    *psVar2 = *psVar2 + 1;
    BVar9 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,DAT_CurrentUnitSlotID)
    ;
                    /* At rally point */
    if ((BVar9 == FALSE) ||
       (iVar13 = DAT_GameCore.mapTimeInTicks + DAT_CurrentUnitSlotID,
       DAT_UnitsState.units[uVar10].facingDirection = 4, iVar13 % 0x28 != 0)) goto LAB_005746ce;
    iVar13 = Map::Buildings::BuildingsState::getKeepLocationForAIUnit
                       (&DAT_BuildingsState,iVar15,0xd,DAT_CurrentUnitSlotID);
joined_r0x005746a3:
    if (iVar13 != 0) {
      DAT_PathFindingState.allAssassinsUnk = 1;
      Map::Units::UnitsState::setDestinationForUnit
                (&DAT_UnitsState,DAT_CurrentUnitSlotID,DAT_BuildingsState.DAT_TempXOffset,
                 DAT_BuildingsState.DAT_TempYOffset,0);
    }
LAB_005746ce:
    piVar1 = &DAT_GameState.playerDataArray[iVar15].countAssassinsAndArabianSwordsman;
    *piVar1 = *piVar1 + 1;
    return;
  case US_MELEE_ATTACK:
    iVar15 = DAT_UnitsState.units[uVar10].gfxNumber;
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].animationSpeed = 1;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    sVar6 = DAT_UnitsState.units[uVar10].attackedUnitID;
    if ((sVar6 != 0) &&
       (DAT_UnitsState.units[uVar10].animationCycleNumberHasJustIncremented != FALSE)) {
      if (DAT_UnitsState.units[uVar10].animationCycleNumber == 7) {
        Map::Units::UnitsState::playHurtSFXForUnit(&DAT_UnitsState,(int)sVar6);
      }
      if ((DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber == 5) &&
         (((((UVar7 = DAT_UnitsState.units[sVar6].unitType, UVar7 == UT_E_SPEAR ||
             (UVar7 == UT_E_PIKE)) || (UVar7 == UT_LORD)) ||
           ((UVar7 == UT_E_MACE || (UVar7 == UT_E_SWORD)))) ||
          ((UVar7 == UT_E_KNIGHT || ((UVar7 == UT_A_ASSASSIN || (UVar7 == UT_A_SWORDSMAN)))))))) {
        Audio::SFX::SFXState::playSFXAtLocation
                  (&DAT_SFXState,(int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].x,
                   (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].y,FX_STEEL1);
      }
      if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber == 4) {
        Audio::SFX::SFXState::playSFXAtLocation
                  (&DAT_SFXState,(int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].x,
                   (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].y,FX_ASS_SWISH);
      }
    }
    uVar10 = DAT_CurrentUnitSlotID;
    iVar13 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field151_0x2c94
                        [DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber];
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationFrame = iVar13;
    iVar14 = (int)DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected;
    if (iVar13 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar14 + 0x101;
      DAT_UnitHasBecomeIdle = 1;
    }
    else {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar14 + 0xf9 + iVar13 * 8;
    }
    if (DAT_UnitsState.units[uVar10].gfxNumber != iVar15) {
      DAT_UnitsState.units[uVar10].drawYOffset = (short)DAT_UnitsState.units[uVar10].imageID2;
      DAT_UnitsState.units[uVar10].imageID2 = iVar15;
    }
    if (DAT_UnitHasBecomeIdle != 0) {
      DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
      Map::Units::UnitsState::resumeMovementIfNoAttackTarget(&DAT_UnitsState,DAT_CurrentUnitSlotID);
      return;
    }
    break;
  case US_MELEE_ATTACK_WALL:
    DAT_UnitsState.units[uVar10].animationSpeed = 2;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    Map::Units::UnitsState::setUnitFacingDirectionForTargetXandY
              (&DAT_UnitsState,uVar12,(int)DAT_UnitsState.units[uVar10].attackAtTileX,
               (int)DAT_UnitsState.units[uVar10].attackAtTileY);
    uVar10 = DAT_CurrentUnitSlotID;
    iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field151_0x2c94
                        [DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber];
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationFrame = iVar15;
    iVar13 = (int)DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar13 + 0x101;
      DAT_UnitHasBecomeIdle = 1;
    }
    else {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar13 + 0xf9 + iVar15 * 8;
    }
    if ((DAT_UnitsState.units[uVar10].animationCycleNumberHasJustIncremented != FALSE) &&
       (DAT_UnitsState.units[uVar10].animationCycleNumber == 6)) {
      uVar10 = Map::TileMapState::getBuildingHurtSFXID
                         (&DAT_TileMapState,DAT_UnitsState.units[uVar10].targetedBuildingTile);
      if (uVar10 == 1) {
        sfxOffsetInArray = FX_ATTACK_WOOD;
      }
      else {
        if (uVar10 != 2) goto LAB_00574a2c;
        sfxOffsetInArray = FX_ATTACK_STONE;
      }
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].x,
                 (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].y,sfxOffsetInArray);
    }
LAB_00574a2c:
    uVar12 = DAT_CurrentUnitSlotID;
    uVar10 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetedBuildingTile;
    iVar15 = (int)(short)DAT_TileMapState.BuildingLayer[uVar10];
    if ((iVar15 == 0) && ((DAT_TileMapState.LogicLayer[uVar10] & 0x100U) == 0)) {
      DAT_UnitHasBecomeIdle = 1;
    }
    else if (DAT_UnitHasBecomeIdle == 0) {
      return;
    }
    pcVar4 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].nextAttackHurtsWall;
    *pcVar4 = *pcVar4 + '\x01';
    if ('\x01' < DAT_UnitsState.units[uVar12].nextAttackHurtsWall) {
      DAT_UnitsState.units[uVar12].nextAttackHurtsWall = '\0';
    }
    uVar10 = DAT_UnitsState.units[uVar12].targetedBuildingTile;
    uVar16 = DAT_TileMapState.LogicLayer[uVar10] & 0x100;
    if (uVar16 == 0) {
      iVar15 = (int)(short)DAT_TileMapState.BuildingLayer[uVar10];
      if (iVar15 < 1) {
        DAT_UnitsState.units[uVar12].state.generic = US_DETERMINE_NEXT_STATEUnk;
        return;
      }
                    /* 6 if gate or tower else 70 */
      iVar13 = (-(uint)(DAT_BuildingDefinedData.DAT_IsGateOrTowerArray
                        [(short)DAT_BuildingsState.buildings[iVar15].buildingType] != FALSE) &
               0xffffffc0) + 0x46;
    }
    else {
      iVar13 = 10;
    }
    Map::TileMapState::processDamageToBuildingThunk
              (&DAT_TileMapState,uVar10,(int)DAT_UnitsState.units[uVar12].attackAtTileX,
               (int)DAT_UnitsState.units[uVar12].attackAtTileY,iVar13,
               (int)DAT_UnitsState.units[uVar12].nextAttackHurtsWall,
               (int)DAT_UnitsState.units[uVar12].owner,TRUE);
    if (extraout_EAX == 0) {
      iVar13 = (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner;
      if (DAT_GameSynchronyState.currentPlayerFullIDArray[iVar13] == -1) {
        if (uVar16 == 0) {
          if (((DAT_BuildingDefinedData.DAT_IsGateOrTowerArray
                [(short)DAT_BuildingsState.buildings[iVar15].buildingType] != FALSE) &&
              (*(int *)((int)DAT_TroopValueState.attackInfo.scaleValuesArray +
                       iVar13 * 0x177bc + -0x1c) + 10 <
               (int)(uint)*(byte *)(*(int *)((int)DAT_TroopValueState.attackInfo.hackValuesArray +
                                            iVar13 * 0x177bc + -0x10) * 0x13a10 + 0x1ee2998 +
                                   DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetedBuildingTile)
              )) && (iVar15 = Map::Units::TribesState::moveUnitToBehaviorTarget
                                        (&DAT_TribesState,DAT_CurrentUnitSlotID,
                                         (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                                              unknownDigMoatOrWallAttackFlag1015),
                    uVar10 = DAT_CurrentUnitSlotID, iVar15 == 0)) {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_DETERMINE_NEXT_STATEUnk;
            DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
            return;
          }
        }
        else if (*(int *)((int)DAT_TroopValueState.attackInfo.scaleValuesArray +
                         iVar13 * 0x177bc + -0x1c) + 0xf <
                 (int)(uint)*(byte *)(*(int *)((int)DAT_TroopValueState.attackInfo.hackValuesArray +
                                              iVar13 * 0x177bc + -0x10) * 0x13a10 + 0x1ee2998 +
                                     DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                                     targetedBuildingTile)) {
          iVar15 = Map::Units::TribesState::moveUnitToBehaviorTarget
                             (&DAT_TribesState,DAT_CurrentUnitSlotID,
                              (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                                   unknownDigMoatOrWallAttackFlag1015);
          if (iVar15 != 0) {
            return;
          }
          iVar15 = Map::Units::UnitsState::setDestinationNearTargetedBuilding
                             (&DAT_UnitsState,DAT_CurrentUnitSlotID,1);
          if (iVar15 != 0) {
            return;
          }
          goto LAB_00574b58;
        }
      }
    }
    else {
      if ((uVar16 != 0) &&
         (iVar15 = Map::Units::UnitsState::setDestinationNearTargetedBuilding
                             (&DAT_UnitsState,DAT_CurrentUnitSlotID,1), iVar15 != 0)) {
        return;
      }
      uVar10 = DAT_CurrentUnitSlotID;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetedBuildingTile = 0;
      iVar15 = Map::Units::TribesState::moveUnitToBehaviorTarget
                         (&DAT_TribesState,uVar10,
                          (int)DAT_UnitsState.units[uVar10].unknownDigMoatOrWallAttackFlag1015);
      if (iVar15 == 0) {
LAB_00574b58:
        uVar10 = DAT_CurrentUnitSlotID;
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_DETERMINE_NEXT_STATEUnk;
        DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
        return;
      }
    }
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber = 0;
    return;
  case 0x6c:
    DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    DAT_UnitsState.units[uVar10].animationSheetFrameOffset = 1;
    return;
  case US_JESTER_ROAM_TO:
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    pbVar3 = &DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown;
    *pbVar3 = *pbVar3 + DAT_UnitsState.units[uVar10].engineerManningSiegeStateRef_checkType;
    if ((char)*pbVar3 < '\0') {
      DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown = 0;
    }
    else if ('\x1f' < (char)DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown) {
      DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown = 0x1f;
    }
    psVar2 = &DAT_UnitsState.units[uVar10].updateTickTracker;
    *psVar2 = *psVar2 + 1;
    if (0x20 < DAT_UnitsState.units[uVar10].updateTickTracker) {
      DAT_UnitsState.units[uVar10].updateTickTracker = 0;
      DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown = 0;
      DAT_UnitsState.units[uVar10].state = (UnitStateUnion)DAT_UnitsState.units[uVar10].cachedState;
      bVar5 = DAT_UnitsState.units[uVar10].engineerManningSiegeStateRef_checkType;
      if ((char)bVar5 < '\0') {
        if (DAT_UnitsState.units[uVar10].isDisappearingUnk != 0) {
          Map::Buildings::BuildingsState::prepareCampgroundCoords(&DAT_BuildingsState,iVar15);
          Map::Units::UnitsState::setDestinationForUnit
                    (&DAT_UnitsState,DAT_CurrentUnitSlotID,DAT_BuildingsState.DAT_TempXOffset,
                     DAT_BuildingsState.DAT_TempYOffset,0);
          return;
        }
      }
      else if (('\0' < (char)bVar5) && (DAT_UnitsState.units[uVar10].isDisappearingUnk != 0)) {
        DAT_UnitsState.units[uVar10].logicalState = ULS_TRANSITIONING;
        DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown = 0x20;
        return;
      }
    }
    break;
  case US_DISAPPEAR:
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    pbVar3 = &DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown;
    *pbVar3 = *pbVar3 + 1;
    if (' ' < (char)DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown) {
      DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown = 0x20;
      DAT_UnitsState.units[uVar10].logicalState = ULS_REMOVE;
      if (DAT_UnitsState.units[uVar10].killedFlagUnk == 0) {
        Game::GameStateStructures::processUnitLossStatistic
                  (&DAT_GameState,iVar15,DAT_CurrentUnitSlotID);
        if (iVar15 == DAT_GameSynchronyState.currentPlayerSlotID) {
          piVar1 = DAT_GameState.mapAndTime.emenyHitArray +
                   DAT_UnitsState.units[DAT_CurrentUnitSlotID].lastEncounteredEnemyPlayerID + -9;
          *piVar1 = *piVar1 + 1;
          return;
        }
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].lastEncounteredEnemyPlayerID ==
            DAT_GameSynchronyState.currentPlayerSlotID) {
          piVar1 = DAT_GameState.mapAndTime.emenyHitArray + iVar15;
          *piVar1 = *piVar1 + 1;
        }
      }
    }
    break;
  case US_DEATH_01:
    sVar6 = DAT_UnitsState.units[uVar10].field323_0x418;
    if (sVar6 < 8) {
      DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    }
    else {
      DAT_UnitsState.units[uVar10].field323_0x418 = sVar6 + -8;
    }
    DAT_UnitsState.units[uVar10].facingDirection = 0;
    DAT_UnitsState.units[uVar10].animationSpeed = 2;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].animationFrame =
         (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.field12_0x93c
                    [DAT_UnitsState.units[uVar10].animationCycleNumber];
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    iVar15 = DAT_UnitsState.units[uVar10].animationFrame;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = 0x33c;
      DAT_UnitsState.units[uVar10].state.generic = US_DISAPPEAR;
      DAT_UnitHasBecomeIdle = 1;
      return;
    }
    iVar15 = iVar15 + 0x324;
    goto LAB_005755cb;
  case US_DEATH_03:
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].facingDirection = 0;
    DAT_UnitsState.units[uVar10].animationSpeed = 1;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field12_0x93c[DAT_UnitsState.units[uVar10].animationCycleNumber];
    DAT_UnitsState.units[uVar10].animationFrame = iVar15;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = 0x36a;
      DAT_UnitsState.units[uVar10].state.generic = US_DISAPPEAR;
      DAT_UnitHasBecomeIdle = 1;
      return;
    }
    iVar15 = iVar15 + 0x352;
    goto LAB_005755cb;
  case US_STONE_DEATH_01:
  case US_STONE_DEATH_02:
  case US_STONE_DEATH_03:
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].facingDirection = 0;
    DAT_UnitsState.units[uVar10].animationSpeed = 1;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field11_0x8e4[DAT_UnitsState.units[uVar10].animationCycleNumber];
    DAT_UnitsState.units[uVar10].animationFrame = iVar15;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = 0x352;
      DAT_UnitsState.units[uVar10].state.generic = US_DISAPPEAR;
      DAT_UnitHasBecomeIdle = 1;
      return;
    }
    iVar15 = iVar15 + 0x33c;
LAB_005755cb:
    bVar17 = DAT_UnitHasBecomeIdle != 0;
    DAT_UnitsState.units[uVar10].gfxNumber = iVar15;
    if (bVar17) {
      DAT_UnitsState.units[uVar10].state.generic = US_DISAPPEAR;
      return;
    }
    break;
  case US_APPEAR:
    DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0x10;
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    sVar6 = DAT_UnitsState.units[uVar10].moveInstructionSpeedDelayTracker;
    DAT_UnitsState.units[uVar10].animationSheetFrameOffset = 1;
    if ((sVar6 == 0) || (DAT_UnitsState.units[uVar10].moveInstructionSpeedDelayTracker < 0x47)) {
      DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    }
    else {
      DAT_UnitsState.units[uVar10].stateBasedSpeed = -1;
      DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    }
    uVar12 = DAT_CurrentUnitSlotID;
    BVar9 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,DAT_CurrentUnitSlotID)
    ;
    if (BVar9 != FALSE) {
      iVar15 = DAT_UnitsState.units[uVar10].
               targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID;
      Map::Units::UnitsState::setPositionOfUnit
                (&DAT_UnitsState,uVar12,
                 iVar15 - DAT_ViewportRenderState.translationMatrix
                          [DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar15]].
                          addXgetTile,
                 (int)DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar15],
                 (uint)DAT_TileMapState.HeightLayer[iVar15]);
      Map::Units::UnitsState::setDestinationForUnit
                (&DAT_UnitsState,DAT_CurrentUnitSlotID,
                 (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].plannedDestinationX,
                 (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].plannedDestinationY,0);
      uVar10 = DAT_CurrentUnitSlotID;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_MOVE_TO_DESTINATION;
      DAT_UnitsState.units[uVar10].fadeType = 1;
      DAT_UnitsState.units[uVar10].fadeCounter = 0;
      return;
    }
    break;
  case US_ASSASSIN_THROWING_HOOK:
                    /* Throwing the hook */
    DAT_UnitsState.units[uVar10].field320_0x413 = 1;
    DAT_UnitsState.units[uVar10].animationSpeed = 1;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    sVar6 = DAT_UnitsState.units[uVar10].assassinHeightDifference;
    iVar15 = DAT_UnitsState.units[uVar10].animationCycleNumber;
    if (sVar6 < 0x46) {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          field156_0x2dac[iVar15];
    }
    else if (sVar6 < 0xa0) {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          field157_0x2df4[iVar15];
    }
    else {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          field158_0x2e4c[iVar15];
    }
    DAT_UnitsState.units[uVar10].animationFrame = iVar15;
    iVar13 = (int)DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar13 + 0x1c1;
      DAT_UnitHasBecomeIdle = 1;
    }
    else {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar13 + 0x1b9 + iVar15 * 8;
    }
    if ((DAT_UnitsState.units[uVar10].animationCycleNumber == 1) &&
       (DAT_UnitsState.units[uVar10].animationCycleNumberHasJustIncremented != FALSE)) {
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_UnitsState.units[uVar10].x,
                 (int)DAT_UnitsState.units[uVar10].y,FX_GH_SWING);
    }
    if (DAT_UnitHasBecomeIdle != 0) {
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].x,
                 (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].y,FX_GH_CATCH);
      iVar15 = DAT_GameSynchronyState.currentPlayerSlotID;
      uVar10 = DAT_CurrentUnitSlotID;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber = 0;
      DAT_UnitsState.units[uVar10].state.generic = US_ASSASSIN_CLIMBING_UP;
      DAT_UnitsState.units[uVar10].field324_0x41a = 0x20;
      if (((DAT_UnitsState.units[uVar10].owner != iVar15) &&
          (iVar15 == (char)DAT_UnitsState.units[uVar10].ownerOfAssassinScaledObject)) &&
         (DVar11 = timeGetTime(), 30000 < DVar11 - DWORD_00ee1064)) {
        if ((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
           (DAT_GameState.mapAndTime.playerTeams[DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner]
            != DAT_GameState.mapAndTime.playerTeams[DAT_GameSynchronyState.currentPlayerSlotID])) {
                    /* "Assassins are scaling the walls sire" */
          Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"General_Warning18.wav");
        }
        DWORD_00ee1064 = timeGetTime();
        return;
      }
    }
    break;
  case US_ASSASSIN_CLIMBING_UP:
                    /* Scaling the wall */
    DAT_UnitsState.units[uVar10].field320_0x413 = 1;
    DAT_UnitsState.units[uVar10].animationSpeed = 2;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    sVar6 = DAT_UnitsState.units[uVar10].field324_0x41a;
    if (0 < sVar6) {
      DAT_UnitsState.units[uVar10].field324_0x41a = sVar6 + -2;
    }
    sVar6 = DAT_UnitsState.units[uVar10].assassinHeightDifference;
    if (sVar6 < 0x46) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 7;
    }
    else if (sVar6 < 100) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 6;
    }
    else if (sVar6 < 0x82) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 5;
    }
    else if (sVar6 < 0xa0) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 4;
    }
    else if (sVar6 < 0xbe) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 3;
    }
    else {
      DAT_UnitsState.units[uVar10].imageIDUnk = (sVar6 < 0xd2) + 1;
    }
    iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field160_0x2ed8[DAT_UnitsState.units[uVar10].animationCycleNumber];
    DAT_UnitsState.units[uVar10].animationFrame = iVar15;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber =
           DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected + 0x271;
      DAT_UnitHasBecomeIdle = 1;
LAB_00574fe5:
      DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
    }
    else {
      bVar17 = DAT_UnitHasBecomeIdle != 0;
      DAT_UnitsState.units[uVar10].gfxNumber =
           DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected + 0x269 + iVar15 * 8;
      if (bVar17) goto LAB_00574fe5;
    }
    if ((DAT_UnitsState.units[uVar10].animationCycleNumberHasJustIncremented != FALSE) &&
       ((iVar15 = DAT_UnitsState.units[uVar10].animationCycleNumber, iVar15 < 10 || (0x10 < iVar15))
       )) {
      psVar2 = &DAT_UnitsState.units[uVar10].field323_0x418;
      *psVar2 = *psVar2 + 1;
    }
    uVar12 = DAT_CurrentUnitSlotID;
    if (DAT_UnitsState.units[uVar10].assassinHeightDifference + -0x23 <=
        (int)DAT_UnitsState.units[uVar10].field323_0x418) {
      DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
      Map::Units::UnitsState::commitMimmicLocation(&DAT_UnitsState,uVar12);
      uVar10 = DAT_CurrentUnitSlotID;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_MOVE_TO_DESTINATION;
      DAT_UnitsState.units[uVar10].field323_0x418 = 0;
      DAT_UnitsState.units[uVar10].field324_0x41a = 0x20;
      DAT_UnitsState.units[uVar10].field320_0x413 = 0;
      return;
    }
    break;
  case US_ASSASSIN_START_CLIMBING_DOWN:
    DAT_UnitsState.units[uVar10].field320_0x413 = 1;
    DAT_UnitsState.units[uVar10].animationSpeed = 1;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field159_0x2eb0[DAT_UnitsState.units[uVar10].animationCycleNumber];
    DAT_UnitsState.units[uVar10].animationFrame = iVar15;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber =
           DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected + 0x1c1;
      DAT_UnitHasBecomeIdle = 1;
    }
    else {
      bVar17 = DAT_UnitHasBecomeIdle == 0;
      DAT_UnitsState.units[uVar10].gfxNumber =
           DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected + 0x1b9 + iVar15 * 8;
      if (bVar17) {
        return;
      }
    }
    DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
    DAT_UnitsState.units[uVar10].state.generic = US_ASSASSIN_CLIMBING_DOWN;
    DAT_UnitsState.units[uVar10].field324_0x41a = 0x20;
    Audio::SFX::SFXState::playSFXAtLocation
              (&DAT_SFXState,(int)DAT_UnitsState.units[uVar10].x,(int)DAT_UnitsState.units[uVar10].y
               ,FX_ROPE_SLIDE);
    return;
  case US_ASSASSIN_CLIMBING_DOWN:
    DAT_UnitsState.units[uVar10].field320_0x413 = 1;
    DAT_UnitsState.units[uVar10].animationSpeed = 2;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    uVar12 = DAT_CurrentUnitSlotID;
    if (DAT_UnitsState.units[uVar10].field323_0x418 == 0) {
      DAT_UnitsState.units[uVar10].field323_0x418 =
           DAT_UnitsState.units[uVar10].assassinHeightDifference;
      Map::Units::UnitsState::commitMimmicLocation(&DAT_UnitsState,uVar12);
    }
    uVar10 = DAT_CurrentUnitSlotID;
    sVar6 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].field324_0x41a;
    if (0 < sVar6) {
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].field324_0x41a = sVar6 + -2;
    }
    sVar6 = DAT_UnitsState.units[uVar10].assassinHeightDifference;
    if (sVar6 < 0x46) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 7;
    }
    else if (sVar6 < 100) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 6;
    }
    else if (sVar6 < 0x82) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 5;
    }
    else if (sVar6 < 0xa0) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 4;
    }
    else if (sVar6 < 0xbe) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 3;
    }
    else {
      DAT_UnitsState.units[uVar10].imageIDUnk = (sVar6 < 0xd2) + 1;
    }
    uVar12 = (int)DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected + 4U &
             0x80000007;
    if ((int)uVar12 < 0) {
      uVar12 = (uVar12 - 1 | 0xfffffff8) + 1;
    }
    DAT_UnitsState.units[uVar10].gfxNumber = uVar12 + 0x291;
    psVar2 = &DAT_UnitsState.units[uVar10].field323_0x418;
    *psVar2 = *psVar2 + -4;
    if (DAT_UnitsState.units[uVar10].field323_0x418 < 0x1f) {
      DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
      DAT_UnitsState.units[uVar10].state.generic = US_MOVE_TO_DESTINATION;
      DAT_UnitsState.units[uVar10].field323_0x418 = 0;
      DAT_UnitsState.units[uVar10].field324_0x41a = 0x20;
      DAT_UnitsState.units[uVar10].field320_0x413 = 0;
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_UnitsState.units[uVar10].x,
                 (int)DAT_UnitsState.units[uVar10].y,FX_ASS_LAND);
      return;
    }
  }
  return;
}


// ================= _HoldStrong::Map::Units::UnitsState::processUnitMove @ 00578c40 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Units::UnitsState::processUnitMove(UnitsState *this,int unitID,int speedCategory)

{
  short *psVar1;
  char cVar2;
  UnitTypeShort UVar3;
  UnitStateShort UVar4;
  ushort uVar5;
  short sVar6;
  BuildingTypeShort BVar7;
  BOOLEnum BVar8;
  int iVar9;
  int iVar10;
  short sVar11;
  uint uVar12;
  uint y;
  int local_8;
  
  UVar3 = DAT_UnitsState.units[unitID].unitType;
  if ((UVar3 == UT_BURNINGMAN) ||
     (((UVar3 != UT_A_ASSASSIN ||
       ((((UVar4 = DAT_UnitsState.units[unitID].state.generic, UVar4 != US_ASSASSIN_THROWING_HOOK &&
          (UVar4 != US_ASSASSIN_START_CLIMBING_DOWN)) && (UVar4 != US_ASSASSIN_CLIMBING_UP)) &&
        (UVar4 != US_ASSASSIN_CLIMBING_DOWN)))) && (DAT_UnitsState.units[unitID].dying == 0)))) {
    sVar11 = DAT_UnitsState.units[unitID].tunnelerFinishedDigging;
    if (sVar11 != 5) {
      if ((sVar11 != 4) && (sVar11 != 2)) {
        DAT_UnitsState.units[unitID].movementRelated = 8;
        updateMicroPosition(&DAT_UnitsState,unitID);
        if ((DAT_UnitsState.units[unitID].climbDataID != 0) &&
           (BVar8 = updateClimbing(&DAT_UnitsState,unitID), BVar8 == FALSE)) {
          setDestinationForUnit
                    (&DAT_UnitsState,unitID,(int)DAT_UnitsState.units[unitID].destinationX_2Unk,
                     (int)DAT_UnitsState.units[unitID].destinationY_2Unk,0);
          changeDestinationByLeftover(&DAT_UnitsState,unitID);
        }
        return 0;
      }
      sVar11 = DAT_UnitsState.units[unitID].moveInstructionSpeedDelayTracker;
      DAT_UnitsState.units[unitID].field42_0x58 = 0;
      if (sVar11 != 0) {
        DAT_UnitsState.units[unitID].moveInstructionSpeedDelayTracker = sVar11 + -1;
      }
      sVar11 = DAT_UnitsState.units[unitID].moveDelay;
      if (sVar11 < 2) {
        DAT_UnitsState.units[unitID].moveDelay = 0;
      }
      else {
        DAT_UnitsState.units[unitID].moveDelay = sVar11 + -2;
      }
      iVar10 = speedCategory + DAT_UnitsState.units[unitID].field276_0x3d2;
      local_8 = 0;
      if (-1 < iVar10) {
        do {
          cVar2 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].field196_0x32d;
          if (cVar2 == '\x01') {
            sVar11 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].field234_0x37e;
            if ((sVar11 < 4) || (0xb < sVar11)) goto LAB_00579081;
LAB_00578dc6:
            psVar1 = &DAT_UnitsState.units[unitID].movementRelated;
            *psVar1 = *psVar1 + 1;
            sVar11 = DAT_UnitsState.units[unitID].movementRelated;
            DAT_UnitsState.units[unitID].field108_0xe8 = 0;
            if (sVar11 < 8) {
              if (DAT_UnitPropertiesDefinedData.field79_0x119cc
                  [DAT_UnitsState.units[unitID].facingDirection] <= (int)sVar11) {
                DAT_UnitsState.units[unitID].field108_0xe8 = 1;
              }
            }
            else {
              uVar5 = DAT_UnitsState.units[unitID].currentIndexInPathPlan;
              if ((DAT_UnitsState.units[unitID].totalSizeOfPathPlan <= (short)uVar5) &&
                 (DAT_UnitsState.units[unitID].field297_0x3f4 == 0)) {
                sVar11 = DAT_UnitsState.units[unitID].x;
                DAT_UnitsState.units[unitID].unknownMovementRelated_0x2d2 = 0;
                DAT_UnitsState.units[unitID].tunnelerFinishedDigging = 0;
                sVar6 = DAT_UnitsState.units[unitID].y;
                DAT_UnitsState.units[unitID].movementRelated = 8;
                DAT_UnitsState.units[unitID].destinationX_2Unk = sVar11;
                DAT_UnitsState.units[unitID].destinationY_2Unk = sVar6;
                return 0;
              }
              DAT_UnitsState.units[unitID].movementRelated = 0;
              uVar12 = (uint)(char)DAT_UnitsState.units[unitID].pathPlanStart[(int)(short)uVar5 / 2]
              ;
              if ((uVar5 & 1) == 0) {
                uVar12 = uVar12 & 0xf;
              }
              else {
                uVar12 = (int)uVar12 >> 4;
              }
              sVar11 = DAT_UnitsState.units[unitID].field297_0x3f4;
              DAT_UnitsState.units[unitID].facingDirection = (short)uVar12;
              if (sVar11 == 0) {
                DAT_UnitsState.units[unitID].currentIndexInPathPlan = uVar5 + 1;
              }
              if (DAT_UnitsState.units[unitID].field276_0x3d2 != 0) {
                saveUnitStateBeforeInterruption(unitID);
                DAT_UnitsState.units[unitID].movementRelated = 8;
                DAT_UnitsState.units[unitID].lookForEnemy = 0;
                DAT_UnitsState.units[unitID].state.generic = US_MELEE_ATTACK;
                DAT_UnitsState.units[unitID].SA = 0;
                DAT_UnitsState.units[unitID].animationCycleNumber = 0;
                return 0;
              }
              sVar6 = DAT_UnitsState.units[unitID].moveRelatedFlag;
              if (sVar6 != 1) {
                if ((sVar11 != 0) ||
                   (BVar8 = Navigation::PathFindingState::doMoveFromTileToTile
                                      (&DAT_PathFindingState,unitID,
                                       DAT_UnitsState.units[unitID].tile,
                                       (int)DAT_UnitsState.units[unitID].y,uVar12,(int)sVar6,
                                       (int)DAT_UnitsState.units[unitID].cannotClimb),
                   BVar8 == FALSE)) {
                  sVar11 = DAT_UnitsState.units[unitID].field297_0x3f4;
                  psVar1 = &DAT_UnitsState.units[unitID].field297_0x3f4;
                  DAT_UnitsState.units[unitID].movementRelated = 8;
                  if ((0 < sVar11) && (sVar11 = sVar11 + -1, *psVar1 = sVar11, 0 < sVar11)) {
                    return 0;
                  }
                  DAT_UnitsState.unknownInitially0_01 = DAT_UnitsState.unknownInitially0_01 + 1;
                  y = (uint)DAT_UnitsState.units[unitID].destinationYPosition;
                  uVar12 = (uint)DAT_UnitsState.units[unitID].destinationXPosition;
                  BVar8 = Rendering::ViewportRenderState::xyAreValid
                                    (&DAT_ViewportRenderState,uVar12,y);
                  if (BVar8 == FALSE) {
                    makeUnitStopWalkingByClearingPathProgressState(unitID);
LAB_005791c7:
                    UVar3 = DAT_UnitsState.units[unitID].unitType;
                    if (UVar3 == UT_LORD) {
                      return 0;
                    }
                    if (DAT_UnitsState.units[unitID].isSelectable_OR_matchTime != 0) {
                      return 0;
                    }
                    if (UVar3 == UT_CAGEDOG) {
                      makeUnitStopWalkingByClearingPathProgressState(unitID);
                      return 0;
                    }
                  }
                  else {
                    if ((int)(short)DAT_TileMapState.PathConnectionLayer
                                    [DAT_ViewportRenderState.translationMatrix[y].addXgetTile +
                                     uVar12] == 0) goto LAB_005791c7;
                    iVar10 = Navigation::PathFindingState::
                             calculateCanPlayerUnitsNavigateToAreaFromArea
                                       (&DAT_PathFindingState,
                                        (int)DAT_UnitsState.units[unitID].owner,
                                        (int)(short)DAT_TileMapState.PathConnectionLayer
                                                    [DAT_UnitsState.units[unitID].tile],
                                        (int)(short)DAT_TileMapState.PathConnectionLayer
                                                    [DAT_ViewportRenderState.translationMatrix[y].
                                                     addXgetTile + uVar12],0);
                    if (iVar10 != 0) goto LAB_0057928b;
                    UVar3 = DAT_UnitsState.units[unitID].unitType;
                    if (UVar3 == UT_LORD) {
                      return 0;
                    }
                    if (DAT_UnitsState.units[unitID].isSelectable_OR_matchTime != 0) {
                      return 0;
                    }
                    if (UVar3 == UT_CAGEDOG) {
                      makeUnitStopWalkingByClearingPathProgressState(unitID);
                      return 0;
                    }
                  }
                  if (DAT_UnitsState.units[unitID].state.generic != US_DISAPPEAR) {
                    DAT_UnitsState.units[unitID].state.generic = US_DISAPPEAR;
                    DAT_UnitsState.units[unitID].updateTickTracker = 0;
                    return 0;
                  }
LAB_0057928b:
                  BVar8 = setDestinationForUnit
                                    (&DAT_UnitsState,DAT_CurrentUnitSlotID,
                                     (int)DAT_UnitsState.units[unitID].destinationXPosition,
                                     (int)DAT_UnitsState.units[unitID].destinationYPosition,0);
                  if (BVar8 == FALSE) {
                    *psVar1 = 0x28;
                    return 0;
                  }
                  changeDestinationByLeftover(&DAT_UnitsState,unitID);
                  return 0;
                }
                LandscapeState::spawnCrowFromNearbyTree(&DAT_LandscapeState,unitID);
              }
              sVar11 = DAT_UnitsState.units[unitID].y;
              iVar9 = DAT_UnitsState.units[unitID].tile;
              DAT_UnitsState.units[unitID].currentTilePosition_2Unk = iVar9;
              sVar6 = DAT_UnitsState.units[unitID].x;
              DAT_UnitsState.units[unitID].nextTileUnk =
                   DAT_TileMapState.directionTranslationMatrix[sVar11][uVar12] + iVar9;
              DAT_UnitsState.units[unitID].mimicCurrentXPosition =
                   DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[uVar12].short.xOffset +
                   sVar6;
              DAT_UnitsState.units[unitID].mimicCurrentYPosition =
                   *(short *)((int)DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix +
                             uVar12 * 8 + 4) + sVar11;
              DAT_UnitsState.units[unitID].microXPosition = sVar6 * 8 + 4;
              DAT_UnitsState.units[unitID].microYPosition = sVar11 * 8 + 4;
            }
            setupUnitSharingCurrentTilePosition(&DAT_UnitsState,unitID);
            switch(DAT_UnitsState.units[unitID].facingDirection) {
            case 0:
              psVar1 = &DAT_UnitsState.units[unitID].microYPosition;
              *psVar1 = *psVar1 + -1;
              break;
            case 1:
              psVar1 = &DAT_UnitsState.units[unitID].microYPosition;
              *psVar1 = *psVar1 + -1;
            case 2:
              psVar1 = &DAT_UnitsState.units[unitID].microXPosition;
              *psVar1 = *psVar1 + 1;
              break;
            case 3:
              psVar1 = &DAT_UnitsState.units[unitID].microYPosition;
              *psVar1 = *psVar1 + 1;
              psVar1 = &DAT_UnitsState.units[unitID].microXPosition;
              *psVar1 = *psVar1 + 1;
              break;
            case 4:
              psVar1 = &DAT_UnitsState.units[unitID].microYPosition;
              *psVar1 = *psVar1 + 1;
              break;
            case 5:
              psVar1 = &DAT_UnitsState.units[unitID].microYPosition;
              *psVar1 = *psVar1 + 1;
            case 6:
              psVar1 = &DAT_UnitsState.units[unitID].microXPosition;
              *psVar1 = *psVar1 + -1;
              break;
            case 7:
              psVar1 = &DAT_UnitsState.units[unitID].microYPosition;
              *psVar1 = *psVar1 + -1;
              psVar1 = &DAT_UnitsState.units[unitID].microXPosition;
              *psVar1 = *psVar1 + -1;
            }
            commitPendingUnitPosition(&DAT_UnitsState,unitID);
            if (DAT_UnitsState.units[unitID].field108_0xe8 == 0) {
              adjustUnitMapOrientationRelatedPositionBasedOnMapOrientationCorrectedFacingDirection
                        (&DAT_UnitsState,unitID);
            }
            else {
              updateMicroPosition(&DAT_UnitsState,unitID);
              Buildings::BuildingsState::processDamageFromKillingPit(&DAT_BuildingsState,unitID);
              iVar9 = (int)(short)DAT_TileMapState.BuildingLayer[DAT_UnitsState.units[unitID].tile];
              if ((iVar9 != 0) &&
                 ((BVar7 = DAT_BuildingsState.buildings[iVar9].buildingType, BVar7 == BT_TOWER1 ||
                  (BVar7 == BT_TOWER4)))) {
                DAT_BuildingsState.buildings[iVar9].hasUnitsOntop = 1;
                DAT_BuildingsState.buildings[iVar9].field288_0x2fa = 100;
              }
            }
            DAT_UnitsState.units[unitID].field108_0xe8 = 0;
            updateUnitFadeAndVisibilityNearStructures(&DAT_UnitsState,unitID);
          }
          else {
            if (cVar2 != '\x02') goto LAB_00578dc6;
            sVar11 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].field234_0x37e;
            if (4 < sVar11) {
              if (sVar11 < 10) goto LAB_00578dc6;
              if (0xb < sVar11) {
                DAT_UnitsState.units[DAT_CurrentUnitSlotID].field234_0x37e = 3;
              }
            }
          }
LAB_00579081:
          local_8 = local_8 + 1;
        } while (local_8 <= iVar10);
      }
      return 1;
    }
    setupUnitSharingCurrentTilePosition(&DAT_UnitsState,unitID);
    commitPendingUnitPosition(&DAT_UnitsState,unitID);
    DAT_UnitsState.units[unitID].field42_0x58 = 0;
  }
  return 0;
}


// geprueft 439 Funktionen, Treffer 20
