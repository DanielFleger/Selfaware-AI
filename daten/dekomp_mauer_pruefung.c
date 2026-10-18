// ================= validateWallBuildPath @ 005029d0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::validateWallBuildPath
          (TileMapState *this,int playerID,uint x1,uint y1,uint x2,uint y2,undefined4 command)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  BOOLEnum BVar4;
  TileMapState *extraout_ECX;
  TileMapState *extraout_ECX_00;
  int extraout_ECX_01;
  TileMapState *pTVar5;
  uint y;
  uint x;
  TileMapState *_tileMapState2;
  int *local_1c;
  int local_18;
  int local_14;
  int local_10;
  int local_c;
  int local_8;
  int local_4;
  
  pTVar5 = &DAT_TileMapState;
  _tileMapState2 = &DAT_TileMapState;
  local_c = 0;
  if (DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) {
    local_8 = 0x1e;
    local_4 = 0x1e;
  }
  else {
    local_8 = 0xf;
    local_4 = 7;
  }
  DAT_TileMapState.buildingPlacementFail = FALSE;
  DAT_TileMapState.illegalBuild = TRUE;
  DAT_TileMapState.field118_0x554920 = 0;
  if (((399 < x1) || (399 < y1)) || (*(char *)(y1 * 400 + 0x21aec98 + x1) == '\0')) {
    DAT_TileMapState.buildingPlacementFail = TRUE;
    return;
  }
  if (((399 < x2) || (399 < y2)) || (*(char *)(y2 * 400 + 0x21aec98 + x2) == '\0')) {
    DAT_TileMapState.buildingPlacementFail = TRUE;
    return;
  }
  local_1c = &DAT_ViewportRenderState.translationMatrix[y1].addXgetTile;
  iVar1 = *local_1c + x1;
  DAT_TileMapState.DAT_SomeY = y1;
  DAT_TileMapState.DAT_SomeTile = iVar1;
  if ((short)command == 0x1b) {
    iVar2 = isTileEnclosedByWallsOrGates(iVar1,y1);
    if (iVar2 == 0) {
      return;
    }
    local_c = getMaxWallHeightInBrushArea(iVar1,y1);
    extraout_ECX->field119_0x554924 = local_c;
    pTVar5 = extraout_ECX;
    if (local_c < 0x11) {
      return;
    }
  }
  else if (((short)command == 0x1a) &&
          (iVar1 = isTileEnclosedByWalls(&DAT_TileMapState,iVar1,y1), pTVar5 = extraout_ECX_00,
          iVar1 == 0)) {
    extraout_ECX_00->buildingPlacementFailReason = 0x13;
    return;
  }
  local_10 = 2;
  local_18 = y1 - y2;
  local_14 = y2 - y1;
  uVar3 = x2 - x1;
  pTVar5->field118_0x554920 = 1;
  y = y1;
  x = x1;
  x1 = x1 - x2;
  y1 = uVar3;
  do {
    iVar1 = *local_1c + x;
    uVar3 = pTVar5->LogicLayer[iVar1];
    if ((uVar3 & 0x14) != 0) {
      return;
    }
    if ((uVar3 & 0x70000401) != 0) {
      return;
    }
    if (pTVar5->BuildingLayer[iVar1] != 0) {
      return;
    }
    if ((((uVar3 & 0x3000) != 0) && (iVar2 = (int)(short)pTVar5->OrganismLayer[iVar1], iVar2 != 0))
       && (iVar2 < 2000)) {
      switch(DAT_LandscapeState.trees[iVar2].treeType) {
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
        break;
      default:
        goto switchD_00502bde_caseD_f;
      }
    }
    if ((uVar3 & 0x300000) != 0) {
      return;
    }
    if ((char)uVar3 < '\0') {
      return;
    }
    if (((pTVar5->UnitLayer[iVar1] != 0) && ((uVar3 & 0x100) == 0)) &&
       (DAT_UnitsState.units[(short)pTVar5->UnitLayer[iVar1]].unitType != UT_CHICKEN)) {
      return;
    }
    if (((DAT_GameCore.gameMode_2 != GM_EDITOR) && (DAT_GameCore.gameMode_2 != GM_SIEGE_THAT)) &&
       (BVar4 = Navigation::PathFindingState::isEnemyTooCloseUnk
                          (&DAT_PathFindingState,playerID,x,y,local_8), BVar4 != FALSE)) {
      DAT_TileMapState.buildingPlacementFailReason = 0x11;
      return;
    }
    if (DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) {
      iVar2 = Navigation::PathFindingState::isOpponentBuildingInRange
                        (&DAT_PathFindingState,playerID,x,y,local_4,-1,-1,-1);
      if (iVar2 != 0) {
        if (DAT_TileMapState.buildingPlacementFailReason == 0x12) {
          return;
        }
        DAT_TileMapState.buildingPlacementFailReason = 0x13;
        return;
      }
      if (DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) {
        iVar2 = getCastleBuildRangeForMapSize(&DAT_TileMapState);
        iVar2 = Navigation::PathFindingState::isTileInRangeOfKeepRange
                          (&DAT_PathFindingState,playerID,x,y,iVar2);
        if (iVar2 != 0) {
          if (DAT_TileMapState.buildingPlacementFailReason == 0x12) {
            return;
          }
          DAT_TileMapState.buildingPlacementFailReason = 0x13;
          return;
        }
      }
    }
    if ((DAT_GameCore.gameMode_2 == GM_EDITOR) &&
       (iVar2 = Navigation::PathFindingState::isOpponentBuildingInRange
                          (&DAT_PathFindingState,playerID,x,y,7,-1,-1,-1), iVar2 != 0)) {
      DAT_TileMapState.buildingPlacementFailReason = 0x11;
      return;
    }
    iVar2 = Navigation::PathFindingState::findSomeSuitableLocationUnk
                      (&DAT_PathFindingState,playerID,x,y,2);
    if (iVar2 != 0) {
      DAT_TileMapState.buildingPlacementFailReason = 0x11;
      return;
    }
    BVar4 = Navigation::PathFindingState::isSignPostWithinDistance
                      (&DAT_PathFindingState,x,y,DAT_GameState.mapAndTime.unk_signpostDistance + 5);
    if (BVar4 != FALSE) {
      DAT_TileMapState.buildingPlacementFailReason = 0x15;
      return;
    }
    if ((short)command == 0x1a) {
      iVar1 = isTileEnclosedByWalls(&DAT_TileMapState,iVar1,y);
      if (iVar1 == 0) {
        *(undefined4 *)(extraout_ECX_01 + 0x554938) = 0x13;
        return;
      }
    }
    else if (((short)command == 0x1b) &&
            ((local_c < 0x11 || ((DAT_TileMapState.LogicLayer[iVar1] & 0x100U) != 0)))) break;
    uVar3 = x1;
    if ((int)x < (int)x2) {
      uVar3 = y1;
    }
    iVar1 = local_18;
    if ((int)y < (int)y2) {
      iVar1 = local_14;
    }
    if ((short)command == 0x1b) {
      if (iVar1 < (int)uVar3) {
        if ((int)x < (int)x2) {
          x1 = x1 + 1;
          x = x + 1;
          y1 = y1 - 1;
        }
        else {
          x1 = x1 - 1;
          x = x - 1;
          y1 = y1 + 1;
        }
      }
      else {
        if (iVar1 < 1) goto LAB_00502e46;
        if ((int)y < (int)y2) {
          local_1c = local_1c + 3;
          local_18 = local_18 + 1;
          y = y + 1;
          local_14 = local_14 + -1;
        }
        else {
          local_1c = local_1c + -3;
          local_18 = local_18 + -1;
          y = y - 1;
          local_14 = local_14 + 1;
        }
      }
    }
    else {
      if (uVar3 != 0) {
        if ((int)x < (int)x2) {
          x1 = x1 + 1;
          x = x + 1;
          y1 = y1 - 1;
        }
        else {
          x1 = x1 - 1;
          x = x - 1;
          y1 = y1 + 1;
        }
      }
      if (iVar1 != 0) {
        if ((int)y < (int)y2) {
          local_1c = local_1c + 3;
          local_18 = local_18 + 1;
          y = y + 1;
          local_14 = local_14 + -1;
        }
        else {
          local_1c = local_1c + -3;
          local_18 = local_18 + -1;
          y = y - 1;
          local_14 = local_14 + 1;
        }
      }
      if ((x == x2) && (y == y2)) {
LAB_00502e46:
        local_10 = local_10 + -1;
      }
    }
    if (0x10 < local_c) {
      local_c = local_c + -0x10;
    }
    pTVar5 = _tileMapState2;
  } while (((x != x2) || (y != y2)) || (local_10 != 0));
  DAT_TileMapState.illegalBuild = FALSE;
switchD_00502bde_caseD_f:
  return;
}



// ================= getWallTilesThatCanBeBuilt @ 00457e80 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Game::GameStateStructures::getWallTilesThatCanBeBuilt
          (GameStateStructures *this,int playerID,int wallMaterial)

{
  int iVar1;
  int iVar2;
  
  if ((DAT_GameCore.solitaryAllBuildingsAreFree == FALSE) && (DAT_GameCore.gameMode_2 != GM_EDITOR))
  {
    if (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) {
      return DAT_GameState.playerDataArray[playerID].startResources[4];
    }
    if (wallMaterial == 4) {
      iVar2 = DAT_GameState.playerDataArray[playerID].currentResources[4];
      iVar1 = *(int *)&DAT_GameState.playerDataArray[playerID].partialStoneCounter;
    }
    else {
      if (wallMaterial != 2) {
        return 0;
      }
      iVar2 = DAT_GameState.playerDataArray[playerID].currentResources[2];
                    /* this is the only leftover of the partial wood stuff from SH1 */
      iVar1 = *(int *)&DAT_GameState.playerDataArray[playerID].partialWoodCounter;
    }
    iVar2 = iVar2 * 2;
    if (iVar1 != 0) {
      iVar2 = iVar2 + -1;
    }
    if (0xfa < iVar2) {
      return 0xfa;
    }
  }
  else {
    iVar2 = 100;
  }
  return iVar2;
}



// ================= processWallBuildingLoss @ 0041c190 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Buildings::BuildingsState::processWallBuildingLoss
          (BuildingsState *this,int playerID,int highCount,int lowCount,int zero)

{
  byte *pbVar1;
  uint uVar2;
  int amount;
  
  if ((DAT_GameCore.solitaryAllBuildingsAreFree == FALSE) && (DAT_GameCore.gameMode_2 != GM_EDITOR))
  {
    if (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) {
      DAT_TileMapState.wallPlacementCost = highCount;
      processResourceLoss(&DAT_BuildingsState,playerID,RT_STONE,highCount,zero);
      return;
    }
    pbVar1 = &DAT_GameState.playerDataArray[playerID].partialStoneCounter;
                    /* total amount is the amount of low wall tiles, the amount of high wall tiles,
                       and the part we should have added last time but wasnt processed because
                       actual cost is divided by 4 */
    uVar2 = lowCount + highCount * 2 + *(int *)pbVar1;
    if (zero == 0) {
      *(uint *)pbVar1 = uVar2 & 3;
    }
                    /* fullAmount / 4 (signed division) */
    amount = (int)(uVar2 + ((int)uVar2 >> 0x1f & 3U)) >> 2;
    DAT_TileMapState.wallPlacementCost = amount;
    processResourceLoss(&DAT_BuildingsState,playerID,RT_STONE,amount,zero);
    if (((playerID == DAT_GameSynchronyState.currentPlayerSlotID) && (zero == 0)) && (amount != 0))
    {
      DAT_WallAndPitchState.flag = zero;
      DAT_WallAndPitchState.counter = amount;
    }
  }
  return;
}



