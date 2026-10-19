// ================= updateSeparateAreaTileMap @ 004995e0 =================

/* WARNING: Restarted to delay deadcode elimination for space: ram */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::Navigation::PathFindingState::updateSeparateAreaTileMap
          (PathFindingState *this,int forceUpdate)

{
  byte bVar1;
  short sVar2;
  ushort uVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  ushort uVar7;
  int local_20;
  int *local_c;
  int local_8;
  
  uVar7 = 1;
  if (forceUpdate != 0) {
    DAT_PathFindingState.toggleUpdateSeparateAreaTileMap = 1;
    DAT_GameState.mapAndTime.counterForUpdatingSeparateAreaTileMaps = 0;
  }
  DAT_GameState.mapAndTime.counterForUpdatingSeparateAreaTileMaps =
       DAT_GameState.mapAndTime.counterForUpdatingSeparateAreaTileMaps + -1;
  if ((0 < DAT_GameState.mapAndTime.counterForUpdatingSeparateAreaTileMaps) ||
     (DAT_GameState.mapAndTime.counterForUpdatingSeparateAreaTileMaps = 200,
     DAT_PathFindingState.toggleUpdateSeparateAreaTileMap == 0)) {
    return FALSE;
  }
  DAT_PathFindingState.field41_0x74 = DAT_PathFindingState.field41_0x74 + 1;
  DAT_PathFindingState.toggleUpdateSeparateAreaTileMap = 0;
  DAT_PathFindingState.totalZones = 0;
  DAT_PathFindingState.sum = 0;
  uVar3 = 1;
  IO::LowLevelMemory::fillMemory_ByteValue
            (&DAT_LowLevelMemory,0x27420,'\0',DAT_TileMapState.PathConnectionLayer);
  IO::LowLevelMemory::fillMemory_ByteValue
            (&DAT_LowLevelMemory,4000,'\0',DAT_PathFindingState.zoneSizesArray);
  Buildings::BuildingsState::updatePathLinkageTileMap(&DAT_BuildingsState,1);
  sVar2 = 0;
  local_20 = 0;
  local_c = &DAT_ViewportRenderState.translationMatrix[1].firstTileOfRow;
  do {
    if (*local_c <= local_20) {
      sVar2 = sVar2 + 1;
      local_c = local_c + 3;
    }
    if (((char)DAT_TileMapState.PathConnectionLayer[local_20] == '\0') &&
       ((DAT_TileMapState.LogicLayer[local_20] & 0x4a5014b1U) == 0)) {
      DAT_PathFindingState.searchQueue.tilesQueue[0] = local_20;
      forceUpdate = 1;
      local_8 = 0;
      DAT_PathFindingState.searchQueue.yQueue[0] = sVar2;
      DAT_TileMapState.PathConnectionLayer[local_20] = uVar7;
      for (; local_8 != forceUpdate; local_8 = local_8 + 1) {
        DAT_PathFindingState.zoneSizesArray[uVar3] = DAT_PathFindingState.zoneSizesArray[uVar3] + 1;
        iVar6 = DAT_PathFindingState.searchQueue.tilesQueue[local_8];
        uVar7 = DAT_PathFindingState.searchQueue.yQueue[local_8];
        bVar1 = DAT_TileMapState.PathLinkageLayer[iVar6];
        if (((bVar1 & 0x40) != 0) && (DAT_TileMapState.MacroLayer[iVar6 + 0x13a0f] == 0)) {
          DAT_TileMapState.MacroLayer[iVar6 + 0x13a0f] = uVar3;
          DAT_PathFindingState.searchQueue.tilesQueue[forceUpdate] = iVar6 + -1;
          DAT_PathFindingState.searchQueue.yQueue[forceUpdate] = uVar7;
          forceUpdate = forceUpdate + 1;
        }
        if (((bVar1 & 4) != 0) && (DAT_TileMapState.PathConnectionLayer[iVar6 + 1] == 0)) {
          DAT_TileMapState.PathConnectionLayer[iVar6 + 1] = uVar3;
          DAT_PathFindingState.searchQueue.tilesQueue[forceUpdate] = iVar6 + 1;
          DAT_PathFindingState.searchQueue.yQueue[forceUpdate] = uVar7;
          forceUpdate = forceUpdate + 1;
        }
        iVar5 = iVar6 + DAT_TileMapState.directionTranslationMatrix[uVar7][0];
        if (((bVar1 & 0x80) != 0) && (DAT_TileMapState.MacroLayer[iVar5 + 0x13a0f] == 0)) {
          DAT_TileMapState.MacroLayer[iVar5 + 0x13a0f] = uVar3;
          DAT_PathFindingState.searchQueue.tilesQueue[forceUpdate] = iVar5 + -1;
          DAT_PathFindingState.searchQueue.yQueue[forceUpdate] = uVar7 - 1;
          forceUpdate = forceUpdate + 1;
        }
        if (((bVar1 & 1) != 0) && (DAT_TileMapState.PathConnectionLayer[iVar5] == 0)) {
          DAT_TileMapState.PathConnectionLayer[iVar5] = uVar3;
          DAT_PathFindingState.searchQueue.tilesQueue[forceUpdate] = iVar5;
          DAT_PathFindingState.searchQueue.yQueue[forceUpdate] = uVar7 - 1;
          forceUpdate = forceUpdate + 1;
        }
        if (((bVar1 & 2) != 0) && (DAT_TileMapState.PathConnectionLayer[iVar5 + 1] == 0)) {
          DAT_TileMapState.PathConnectionLayer[iVar5 + 1] = uVar3;
          DAT_PathFindingState.searchQueue.tilesQueue[forceUpdate] = iVar5 + 1;
          DAT_PathFindingState.searchQueue.yQueue[forceUpdate] = uVar7 - 1;
          forceUpdate = forceUpdate + 1;
        }
        iVar6 = iVar6 + DAT_TileMapState.directionTranslationMatrix[uVar7][4];
        if (((bVar1 & 0x20) != 0) && (DAT_TileMapState.MacroLayer[iVar6 + 0x13a0f] == 0)) {
          DAT_TileMapState.MacroLayer[iVar6 + 0x13a0f] = uVar3;
          DAT_PathFindingState.searchQueue.tilesQueue[forceUpdate] = iVar6 + -1;
          DAT_PathFindingState.searchQueue.yQueue[forceUpdate] = uVar7 + 1;
          forceUpdate = forceUpdate + 1;
        }
        if (((bVar1 & 0x10) != 0) && (DAT_TileMapState.PathConnectionLayer[iVar6] == 0)) {
          DAT_TileMapState.PathConnectionLayer[iVar6] = uVar3;
          DAT_PathFindingState.searchQueue.tilesQueue[forceUpdate] = iVar6;
          DAT_PathFindingState.searchQueue.yQueue[forceUpdate] = uVar7 + 1;
          forceUpdate = forceUpdate + 1;
        }
        if (((bVar1 & 8) != 0) && (DAT_TileMapState.PathConnectionLayer[iVar6 + 1] == 0)) {
          DAT_TileMapState.PathConnectionLayer[iVar6 + 1] = uVar3;
          DAT_PathFindingState.searchQueue.tilesQueue[forceUpdate] = iVar6 + 1;
          DAT_PathFindingState.searchQueue.yQueue[forceUpdate] = uVar7 + 1;
          forceUpdate = forceUpdate + 1;
        }
      }
      uVar7 = uVar3 + 1;
      uVar3 = uVar7;
      if (999 < (short)uVar7) break;
    }
    local_20 = local_20 + 1;
  } while (local_20 < 0x13a10);
  DAT_PathFindingState.totalZones = (int)(short)uVar7;
  piVar4 = DAT_PathFindingState.zoneSizesArray + 2;
  iVar6 = 0x14d;
  do {
    DAT_PathFindingState.sum = piVar4[1] + DAT_PathFindingState.sum + piVar4[-1] + *piVar4;
    piVar4 = piVar4 + 3;
    iVar6 = iVar6 + -1;
  } while (iVar6 != 0);
  Buildings::BuildingsState::updatePathLinkageTileMap(&DAT_BuildingsState,0);
  return TRUE;
}



// ================= commitUnitPathPlanUsingWalkLayer @ 00498fd0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

uint __thiscall
_HoldStrong::Map::Navigation::PathFindingState::commitUnitPathPlanUsingWalkLayer
          (PathFindingState *this,uint param_1,int param_2,int param_3)

{
  short sVar1;
  bool bVar2;
  uint uVar3;
  int *piVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  int _direction;
  uint local_24;
  int _tile;
  int local_14;
  uint _y;
  
  if (((399 < DAT_PathFindingState.unitX) || (399 < DAT_PathFindingState.unitY)) ||
     (bVar2 = false,
     *(char *)(DAT_PathFindingState.unitY * 400 + 0x21aec98 + DAT_PathFindingState.unitX) == '\0'))
  {
    return 0;
  }
  _tile = DAT_ViewportRenderState.translationMatrix[DAT_PathFindingState.unitY].addXgetTile +
          DAT_PathFindingState.unitX;
  _y = DAT_PathFindingState.unitY;
  if (DAT_TileMapState.PathConnectionLayer[_tile] == 0) {
    return 0;
  }
  if (param_1 == 0) {
    iVar11 = 0x50;
  }
  else if (param_1 == 1) {
    iVar11 = 200;
  }
  else if (param_1 == 2) {
    iVar11 = 500;
  }
  else if (param_1 == 3) {
    iVar11 = 1000;
  }
  else {
    iVar11 = 2000;
  }
  findSuitableSpawnLocationUnk
            (&DAT_PathFindingState,DAT_PathFindingState.unitX,DAT_PathFindingState.unitY,-1,-1,
             iVar11,0);
  sVar1 = DAT_TileMapState.WalkLayer[_tile];
  uVar9 = (uint)SEC_RNG.currentNumber2;
  DAT_PathFindingState.searchQueue.pathPlanIndex = 0;
  iVar11 = 10;
  local_24 = 1;
  local_14 = 10;
  while( true ) {
    while( true ) {
      uVar3 = local_24;
      if ((bVar2) && (local_24 < 2)) {
        return DAT_PathFindingState.searchQueue.pathPlanIndex;
      }
      piVar4 = DAT_TileMapState.directionTranslationMatrix[_y] + 1;
      _direction = 8;
      param_1 = local_24;
      iVar8 = 2;
      do {
        iVar5 = (*(int (*) [8])(piVar4 + -1))[0] + _tile;
        if (DAT_TileMapState.WalkLayer[iVar5] == sVar1) {
          uVar7 = (uint)DAT_TileMapState.CertainPathLayer[iVar5];
          if (bVar2) {
            if ((((uVar7 & 0x4000) == 0) && (uVar7 = uVar7 & 0x3fff, uVar7 <= uVar3)) &&
               ((param_3 == 0 || (uVar7 != uVar3)))) {
              uVar6 = uVar7 - ((DAT_TileMapState.RandomLayer[iVar5] ^ uVar9) & 7);
              uVar10 = uVar6;
              if (iVar8 + -2 == iVar11) {
                uVar10 = uVar6 - 1;
              }
              if ((int)uVar10 < (int)param_1) {
                param_1 = uVar6;
                _direction = iVar8 + -2;
                local_24 = uVar7;
              }
              uVar9 = (int)uVar9 >> 1 & 0x7fffU | (uVar9 & 1) << 0xf;
              iVar11 = local_14;
            }
          }
          else if ((((uVar7 & 0x8000) == 0) && (uVar7 = uVar7 & 0x3fff, uVar3 <= uVar7)) &&
                  ((param_3 == 0 || (uVar7 != uVar3)))) {
            uVar6 = ((DAT_TileMapState.RandomLayer[iVar5] ^ uVar9) & 7) + uVar7;
            uVar10 = uVar6;
            if (iVar8 + -2 == iVar11) {
              uVar10 = uVar6 + 1;
            }
            if ((int)param_1 < (int)uVar10) {
              param_1 = uVar6;
              _direction = iVar8 + -2;
              local_24 = uVar7;
            }
            uVar9 = (int)uVar9 >> 1 & 0x7fffU | (uVar9 & 1) << 0xf;
            iVar11 = local_14;
          }
        }
        iVar5 = *piVar4 + _tile;
        if (DAT_TileMapState.WalkLayer[iVar5] == sVar1) {
          uVar7 = (uint)DAT_TileMapState.CertainPathLayer[iVar5];
          if (bVar2) {
            if ((((uVar7 & 0x4000) == 0) && (uVar7 = uVar7 & 0x3fff, uVar7 <= uVar3)) &&
               ((param_3 == 0 || (uVar7 != uVar3)))) {
              uVar6 = uVar7 - ((DAT_TileMapState.RandomLayer[iVar5] ^ uVar9) & 7);
              uVar10 = uVar6;
              if (iVar8 + -1 == iVar11) {
                uVar10 = uVar6 - 1;
              }
              if ((int)uVar10 < (int)param_1) {
                param_1 = uVar6;
                _direction = iVar8 + -1;
                local_24 = uVar7;
              }
              uVar9 = (int)uVar9 >> 1 & 0x7fffU | (uVar9 & 1) << 0xf;
              iVar11 = local_14;
            }
          }
          else if ((((uVar7 & 0x8000) == 0) && (uVar7 = uVar7 & 0x3fff, uVar3 <= uVar7)) &&
                  ((param_3 == 0 || (uVar7 != uVar3)))) {
            uVar6 = ((DAT_TileMapState.RandomLayer[iVar5] ^ uVar9) & 7) + uVar7;
            uVar10 = uVar6;
            if (iVar8 + -1 == iVar11) {
              uVar10 = uVar6 + 1;
            }
            if ((int)param_1 < (int)uVar10) {
              param_1 = uVar6;
              _direction = iVar8 + -1;
              local_24 = uVar7;
            }
            uVar9 = (int)uVar9 >> 1 & 0x7fffU | (uVar9 & 1) << 0xf;
            iVar11 = local_14;
          }
        }
        iVar5 = piVar4[1] + _tile;
        if (DAT_TileMapState.WalkLayer[iVar5] == sVar1) {
          uVar7 = (uint)DAT_TileMapState.CertainPathLayer[iVar5];
          if (bVar2) {
            if ((((uVar7 & 0x4000) == 0) && (uVar7 = uVar7 & 0x3fff, uVar7 <= uVar3)) &&
               ((param_3 == 0 || (uVar7 != uVar3)))) {
              uVar6 = uVar7 - ((DAT_TileMapState.RandomLayer[iVar5] ^ uVar9) & 7);
              uVar10 = uVar6;
              if (iVar8 == iVar11) {
                uVar10 = uVar6 - 1;
              }
              if ((int)uVar10 < (int)param_1) {
                param_1 = uVar6;
                _direction = iVar8;
                local_24 = uVar7;
              }
              uVar9 = (int)uVar9 >> 1 & 0x7fffU | (uVar9 & 1) << 0xf;
            }
          }
          else if ((((uVar7 & 0x8000) == 0) && (uVar7 = uVar7 & 0x3fff, uVar3 <= uVar7)) &&
                  ((param_3 == 0 || (uVar7 != uVar3)))) {
            uVar6 = ((DAT_TileMapState.RandomLayer[iVar5] ^ uVar9) & 7) + uVar7;
            uVar10 = uVar6;
            if (iVar8 == iVar11) {
              uVar10 = uVar6 + 1;
            }
            if ((int)param_1 < (int)uVar10) {
              param_1 = uVar6;
              _direction = iVar8;
              local_24 = uVar7;
            }
            uVar9 = (int)uVar9 >> 1 & 0x7fffU | (uVar9 & 1) << 0xf;
          }
        }
        iVar5 = piVar4[2] + _tile;
        if (DAT_TileMapState.WalkLayer[iVar5] == sVar1) {
          uVar7 = (uint)DAT_TileMapState.CertainPathLayer[iVar5];
          if (bVar2) {
            if ((((uVar7 & 0x4000) == 0) && (uVar7 = uVar7 & 0x3fff, uVar7 <= uVar3)) &&
               ((param_3 == 0 || (uVar7 != uVar3)))) {
              uVar6 = uVar7 - ((DAT_TileMapState.RandomLayer[iVar5] ^ uVar9) & 7);
              uVar10 = uVar6;
              if (iVar8 + 1 == iVar11) {
                uVar10 = uVar6 - 1;
              }
              if ((int)uVar10 < (int)param_1) {
                param_1 = uVar6;
                _direction = iVar8 + 1;
                local_24 = uVar7;
              }
              uVar9 = (int)uVar9 >> 1 & 0x7fffU | (uVar9 & 1) << 0xf;
              iVar11 = local_14;
            }
          }
          else if ((((uVar7 & 0x8000) == 0) && (uVar7 = uVar7 & 0x3fff, uVar3 <= uVar7)) &&
                  ((param_3 == 0 || (uVar7 != uVar3)))) {
            uVar6 = ((DAT_TileMapState.RandomLayer[iVar5] ^ uVar9) & 7) + uVar7;
            uVar10 = uVar6;
            if (iVar8 + 1 == iVar11) {
              uVar10 = uVar6 + 1;
            }
            if ((int)param_1 < (int)uVar10) {
              param_1 = uVar6;
              _direction = iVar8 + 1;
              local_24 = uVar7;
            }
            uVar9 = (int)uVar9 >> 1 & 0x7fffU | (uVar9 & 1) << 0xf;
            iVar11 = local_14;
          }
        }
        piVar4 = piVar4 + 4;
        iVar5 = iVar8 + 2;
        iVar8 = iVar8 + 4;
      } while (iVar5 < 8);
      if (bVar2) {
        DAT_TileMapState.CertainPathLayer[_tile] = DAT_TileMapState.CertainPathLayer[_tile] | 0x4000
        ;
      }
      else {
        DAT_TileMapState.CertainPathLayer[_tile] = DAT_TileMapState.CertainPathLayer[_tile] | 0x8000
        ;
      }
      if (_direction == 8) break;
      _tile = _tile + DAT_TileMapState.directionTranslationMatrix[_y][_direction];
      _y = _y + *(int *)((int)DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix +
                        _direction * 8 + 4);
      if ((DAT_PathFindingState.searchQueue.pathPlanIndex & 1) == 0) {
        DAT_PathFindingState.searchQueue.ptrPathPlan
        [(int)DAT_PathFindingState.searchQueue.pathPlanIndex / 2] = (byte)_direction;
      }
      else {
        DAT_PathFindingState.searchQueue.ptrPathPlan
        [(int)DAT_PathFindingState.searchQueue.pathPlanIndex / 2] =
             DAT_PathFindingState.searchQueue.ptrPathPlan
             [(int)DAT_PathFindingState.searchQueue.pathPlanIndex / 2] & 0xf;
        DAT_PathFindingState.searchQueue.ptrPathPlan
        [(int)DAT_PathFindingState.searchQueue.pathPlanIndex / 2] =
             DAT_PathFindingState.searchQueue.ptrPathPlan
             [(int)DAT_PathFindingState.searchQueue.pathPlanIndex / 2] + (byte)_direction * '\x10';
      }
      DAT_PathFindingState.searchQueue.pathPlanIndex =
           DAT_PathFindingState.searchQueue.pathPlanIndex + 1;
      iVar11 = _direction;
      local_14 = _direction;
      if (799 < (int)DAT_PathFindingState.searchQueue.pathPlanIndex) {
        return DAT_PathFindingState.searchQueue.pathPlanIndex;
      }
    }
    if (param_2 == 0) {
      return DAT_PathFindingState.searchQueue.pathPlanIndex;
    }
    if (bVar2) break;
    bVar2 = true;
  }
  return DAT_PathFindingState.searchQueue.pathPlanIndex;
}



// ================= doMoveFromTileToTile @ 00497280 =================

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



// ================= pathFindingWithBuildingsIncluded @ 00498400 =================

/* WARNING: Removing unreachable block (ram,0x00498700) */
/* WARNING: Removing unreachable block (ram,0x00498713) */
/* WARNING: Removing unreachable block (ram,0x0049871e) */
/* WARNING: Removing unreachable block (ram,0x0049872d) */
/* WARNING: Removing unreachable block (ram,0x00498739) */
/* WARNING: Removing unreachable block (ram,0x00498745) */
/* WARNING: Removing unreachable block (ram,0x00498749) */
/* WARNING: Removing unreachable block (ram,0x00498907) */
/* WARNING: Removing unreachable block (ram,0x0049891a) */
/* WARNING: Removing unreachable block (ram,0x00498925) */
/* WARNING: Removing unreachable block (ram,0x00498934) */
/* WARNING: Removing unreachable block (ram,0x00498940) */
/* WARNING: Removing unreachable block (ram,0x0049894c) */
/* WARNING: Removing unreachable block (ram,0x00498950) */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::Navigation::PathFindingState::pathFindingWithBuildingsIncluded
          (PathFindingState *this,uint x,uint y,uint x2,uint y2,int maxOptionsToTry,
          int zeroMeansResetAlgorithm)

{
  short sVar1;
  short sVar2;
  ushort uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  uint uVar10;
  uint _tile2;
  
  if (((399 < x) || (399 < y)) || (*(char *)(y * 400 + 0x21aec98 + x) == '\0')) {
    return FALSE;
  }
  if ((x2 == 0xffffffff) ||
     (((x2 < 400 && (y2 < 400)) && (*(char *)(y2 * 400 + 0x21aec98 + x2) != '\0')))) {
    if (zeroMeansResetAlgorithm == 0) {
      DAT_PathFindingState.searchGeneration = DAT_PathFindingState.searchGeneration + 1;
      if (32000 < DAT_PathFindingState.searchGeneration) {
        DAT_PathFindingState.searchGeneration = 1;
        IO::LowLevelMemory::fillMemory_ByteValue
                  (&DAT_LowLevelMemory,0x27420,'\0',DAT_TileMapState.WalkLayer);
      }
      DAT_PathFindingState.searchQueue.writeIndex = 1;
      DAT_PathFindingState.searchQueue.readIndex = 0;
      DAT_PathFindingState.searchQueue.currentDistance = 1;
    }
    DAT_PathFindingState.DAT_Ass = DAT_PathFindingState.DAT_Ass + 1;
    DAT_PathFindingState.searchQueue.yQueue[0] = (short)y;
    DAT_PathFindingState.searchQueue.xQueue[0] = (short)x;
    DAT_PathFindingState.searchQueue.tilesQueue[0] =
         DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x;
    DAT_TileMapState.CertainPathLayer[DAT_PathFindingState.searchQueue.tilesQueue[0]] =
         (short)DAT_PathFindingState.searchQueue.currentDistance;
    DAT_TileMapState.WalkLayer[DAT_PathFindingState.searchQueue.tilesQueue[0]] =
         (short)DAT_PathFindingState.searchGeneration;
    if (x2 == 0xffffffff) {
      _tile2 = 0;
    }
    else {
      _tile2 = DAT_ViewportRenderState.translationMatrix[y2].addXgetTile + x2;
    }
    if (DAT_PathFindingState.searchQueue.readIndex != DAT_PathFindingState.searchQueue.writeIndex) {
      while( true ) {
        uVar4 = DAT_PathFindingState.searchQueue.tilesQueue
                [DAT_PathFindingState.searchQueue.readIndex];
        if (uVar4 == _tile2) {
          return TRUE;
        }
        if ((maxOptionsToTry <= DAT_PathFindingState.searchQueue.readIndex) || (0x13a0f < uVar4))
        break;
        sVar1 = DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.readIndex];
        sVar2 = DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.readIndex];
        DAT_PathFindingState.searchQueue.currentDistance =
             (int)DAT_TileMapState.CertainPathLayer[uVar4];
        if (400 < DAT_PathFindingState.searchQueue.currentDistance) {
          return FALSE;
        }
        uVar3 = DAT_TileMapState.BuildingLayer[uVar4];
        uVar5 = DAT_TileMapState.LogicLayer[uVar4];
        iVar7 = 0;
        piVar8 = DAT_TileMapState.directionTranslationMatrix[sVar2] + 1;
        do {
          iVar9 = (*(int (*) [8])(piVar8 + -1))[0] + uVar4;
                    /* 0x4a5014b1 == check against walkable tiles including keep, walls, and
                       gatehouses */
          if ((DAT_TileMapState.WalkLayer[iVar9] != DAT_PathFindingState.searchGeneration) &&
             (((DAT_TileMapState.PathLinkageLayer[uVar4] &
               DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[iVar7]) != 0 ||
              (((((uVar6 = DAT_TileMapState.LogicLayer[iVar9], (uVar6 & 0x4a5014b1) == 0 &&
                  (uVar3 == 0)) && (DAT_TileMapState.BuildingLayer[iVar9] == 0)) &&
                ((uVar10 = uVar5 & 0x100, uVar10 == 0 || ((uVar6 & 0x100) == 0)))) &&
               ((uVar10 != 0 || ((uVar6 & 0x100) != 0)))))))) {
            DAT_TileMapState.CertainPathLayer[iVar9] =
                 (short)DAT_PathFindingState.searchQueue.currentDistance + 1;
            DAT_TileMapState.WalkLayer[iVar9] = (short)DAT_PathFindingState.searchGeneration;
            DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[iVar7].short.xOffset +
                 sVar1;
            DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 *(short *)((int)DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix +
                           iVar7 * 8 + 4) + sVar2;
            DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.writeIndex]
                 = iVar9;
            DAT_PathFindingState.searchQueue.writeIndex =
                 DAT_PathFindingState.searchQueue.writeIndex + 1;
            if (0x13a0f < DAT_PathFindingState.searchQueue.writeIndex) {
              DAT_PathFindingState.searchQueue.writeIndex = 0;
            }
          }
          iVar9 = *piVar8 + uVar4;
          if ((DAT_TileMapState.WalkLayer[iVar9] != DAT_PathFindingState.searchGeneration) &&
             ((DAT_TileMapState.PathLinkageLayer[uVar4] &
              DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[iVar7 + 1]) != 0)) {
            DAT_TileMapState.CertainPathLayer[iVar9] =
                 (short)DAT_PathFindingState.searchQueue.currentDistance + 1;
            DAT_TileMapState.WalkLayer[iVar9] = (short)DAT_PathFindingState.searchGeneration;
            DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[iVar7 + 1].short.xOffset
                 + sVar1;
            DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 *(short *)((int)DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix +
                           iVar7 * 8 + 0xc) + sVar2;
            DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.writeIndex]
                 = iVar9;
            DAT_PathFindingState.searchQueue.writeIndex =
                 DAT_PathFindingState.searchQueue.writeIndex + 1;
            if (0x13a0f < DAT_PathFindingState.searchQueue.writeIndex) {
              DAT_PathFindingState.searchQueue.writeIndex = 0;
            }
          }
          iVar9 = piVar8[1] + uVar4;
          if ((DAT_TileMapState.WalkLayer[iVar9] != DAT_PathFindingState.searchGeneration) &&
             (((DAT_TileMapState.PathLinkageLayer[uVar4] &
               DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[iVar7 + 2]) != 0 ||
              ((((uVar6 = DAT_TileMapState.LogicLayer[iVar9], (uVar6 & 0x4a5014b1) == 0 &&
                 (uVar3 == 0)) && (DAT_TileMapState.BuildingLayer[iVar9] == 0)) &&
               (((uVar10 = uVar5 & 0x100, uVar10 == 0 || ((uVar6 & 0x100) == 0)) &&
                ((uVar10 != 0 || ((uVar6 & 0x100) != 0)))))))))) {
            DAT_TileMapState.CertainPathLayer[iVar9] =
                 (short)DAT_PathFindingState.searchQueue.currentDistance + 1;
            DAT_TileMapState.WalkLayer[iVar9] = (short)DAT_PathFindingState.searchGeneration;
            DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[iVar7 + 2].short.xOffset
                 + sVar1;
            DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 *(short *)((int)DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix +
                           iVar7 * 8 + 0x14) + sVar2;
            DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.writeIndex]
                 = iVar9;
            DAT_PathFindingState.searchQueue.writeIndex =
                 DAT_PathFindingState.searchQueue.writeIndex + 1;
            if (0x13a0f < DAT_PathFindingState.searchQueue.writeIndex) {
              DAT_PathFindingState.searchQueue.writeIndex = 0;
            }
          }
          iVar9 = piVar8[2] + uVar4;
          if ((DAT_TileMapState.WalkLayer[iVar9] != DAT_PathFindingState.searchGeneration) &&
             ((DAT_TileMapState.PathLinkageLayer[uVar4] &
              DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[iVar7 + 3]) != 0)) {
            DAT_TileMapState.CertainPathLayer[iVar9] =
                 (short)DAT_PathFindingState.searchQueue.currentDistance + 1;
            DAT_TileMapState.WalkLayer[iVar9] = (short)DAT_PathFindingState.searchGeneration;
            DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[iVar7 + 3].short.xOffset
                 + sVar1;
            DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 *(short *)((int)DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix +
                           iVar7 * 8 + 0x1c) + sVar2;
            DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.writeIndex]
                 = iVar9;
            DAT_PathFindingState.searchQueue.writeIndex =
                 DAT_PathFindingState.searchQueue.writeIndex + 1;
            if (0x13a0f < DAT_PathFindingState.searchQueue.writeIndex) {
              DAT_PathFindingState.searchQueue.writeIndex = 0;
            }
          }
          iVar7 = iVar7 + 4;
          piVar8 = piVar8 + 4;
        } while (iVar7 < 8);
        DAT_PathFindingState.searchQueue.readIndex = DAT_PathFindingState.searchQueue.readIndex + 1;
        if (0x13a0f < DAT_PathFindingState.searchQueue.readIndex) {
          DAT_PathFindingState.searchQueue.readIndex = 0;
        }
        if (DAT_PathFindingState.searchQueue.readIndex ==
            DAT_PathFindingState.searchQueue.writeIndex) {
          return FALSE;
        }
      }
    }
  }
  return FALSE;
}



// ================= findDirectNeighbourWalkableTile @ 0049cd60 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::Navigation::PathFindingState::findDirectNeighbourWalkableTile
          (PathFindingState *this,uint x,uint y)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  if (((x < 400) && (y < 400)) && (*(char *)(y * 400 + 0x21aec98 + x) != '\0')) {
    iVar3 = 0;
    do {
      uVar2 = DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[iVar3].int.xOffset + x;
      uVar4 = *(int *)((int)DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix +
                      iVar3 * 8 + 4) + y;
      if (((uVar2 < 400) && (uVar4 < 400)) && (*(char *)(uVar4 * 400 + 0x21aec98 + uVar2) != '\0'))
      {
        iVar1 = DAT_TileMapState.directionTranslationMatrix[y][iVar3] +
                DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x;
        if (((DAT_TileMapState.LogicLayer[iVar1] & 0xb1U) == 0) &&
           ((DAT_TileMapState.LogicLayer[iVar1] & 0x50101400U) == 0)) {
                    /* No sea, borders, rocky, building, tree, river, keep, moat */
          DAT_PathFindingState.ALG_ResultY = uVar4;
          DAT_PathFindingState.ALG_ResultTile = iVar1;
          DAT_PathFindingState.ALG_ResultX = uVar2;
          return TRUE;
        }
      }
      iVar3 = iVar3 + 1;
      if (7 < iVar3) {
        return FALSE;
      }
    } while( true );
  }
  return FALSE;
}



// ================= updatePathLinkagesForBuilding @ 00506ad0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::updatePathLinkagesForBuilding(TileMapState *this,int buildingID)

{
  int y;
  BuildingTypeShort BVar1;
  int iVar2;
  int tile;
  
  iVar2 = 0;
  do {
    getBuildingSizeIndexMappingData(iVar2,DAT_BuildingsState.buildings[buildingID].widthOrHeight);
    y = (short)DAT_BuildingsState.buildings[buildingID].y + DAT_TileMapState.buildingY;
    tile = DAT_ViewportRenderState.translationMatrix[y].addXgetTile +
           (int)(short)DAT_BuildingsState.buildings[buildingID].x + DAT_TileMapState.buildingX;
    Navigation::PathFindingState::updatePathLinkagesInAllEightDirections
              (&DAT_PathFindingState,y,tile);
    clearMoat(&DAT_TileMapState,tile);
    iVar2 = iVar2 + 1;
  } while (iVar2 < DAT_TileMapState.constructionTileCount);
  BVar1 = DAT_BuildingsState.buildings[buildingID].buildingType;
  if (BVar1 == BT_GATEHOUSELARGE) {
    Navigation::PathFindingState::updatePathLinkageTileMapRelatedToGates(buildingID);
    return;
  }
  if (BVar1 == BT_GATEHOUSESMALL) {
    Navigation::PathFindingState::updatePathLinkageTileMapRelatedToGates(buildingID);
    return;
  }
  if (BVar1 == BT_WOODGATE1) {
    Navigation::PathFindingState::updatePathLinkageTileMapRelatedToGates(buildingID);
    return;
  }
  if (BVar1 == BT_STONEKEEP) {
    Navigation::PathFindingState::updatePathLinkageTileMapRelatedToKeeps(buildingID);
    return;
  }
  if (BVar1 == BT_STRONGHOLD) {
    Navigation::PathFindingState::updatePathLinkageTileMapRelatedToKeeps(buildingID);
    return;
  }
  if (BVar1 == BT_KEEPFOUR) {
    Navigation::PathFindingState::updatePathLinkageTileMapRelatedToKeeps(buildingID);
    return;
  }
  if (BVar1 == BT_KEEPFIVE) {
    Navigation::PathFindingState::updatePathLinkageTileMapRelatedToKeeps(buildingID);
    return;
  }
  if (BVar1 == BT_SIEGETOWER_PLACED) {
    Navigation::PathFindingState::updatePathLinkageTileMapRelatedToSiegeTower(buildingID);
    return;
  }
  return;
}



