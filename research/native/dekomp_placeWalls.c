// ================= placeWalls @ 00502f30 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::placeWalls
          (TileMapState *this,int playerID,uint x1,uint y1,uint x2,uint y2,MappersEnum wallType,
          int tileCountUnk)

{
  ushort uVar1;
  bool bVar2;
  bool bVar3;
  BOOLEnum BVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  uint local_28;
  int *local_24;
  int local_20;
  int local_1c;
  uint local_18;
  int local_14;
  int local_10;
  int _normalWallCountUnk;
  int local_8;
  
  local_14 = 0;
  _normalWallCountUnk = 0;
  local_8 = 0;
  validateWallBuildPath(&DAT_TileMapState,playerID,x1,y1,x2,y2,wallType);
  if (DAT_TileMapState.illegalBuild == FALSE) {
    DAT_TileMapState.constructionTileCount =
         Game::GameStateStructures::getWallTilesThatCanBeBuilt(&DAT_GameState,playerID,4);
    local_10 = 2;
    if ((undefined2)wallType == M_MAPPER_STAIR) {
      local_14 = DAT_TileMapState.field119_0x554924;
    }
    if (playerID == DAT_GameSynchronyState.currentPlayerSlotID) {
      WallAndPitchState::resetWallPlacementInfo(&DAT_WallAndPitchState);
    }
    local_20 = y1 - y2;
    local_1c = y2 - y1;
    local_28 = x2 - x1;
    local_24 = &DAT_ViewportRenderState.translationMatrix[y1].addXgetTile;
    local_18 = x1;
    x1 = x1 - x2;
    do {
      if (((undefined2)wallType == M_MAPPER_STAIR) && (local_14 < 0x18)) goto LAB_00503440;
      if ((tileCountUnk <= local_8) ||
         (DAT_TileMapState.constructionTileCount < _normalWallCountUnk)) break;
      local_8 = local_8 + 1;
      iVar6 = *local_24 + local_18;
      bVar3 = false;
      if (((undefined2)wallType == M_MAPPER_STAIR) &&
         ((DAT_TileMapState.LogicLayer[iVar6] & 0x100U) != 0)) goto LAB_00503440;
      bVar2 = false;
      if (((undefined2)wallType == M_MAPPER_WALL) &&
         ((DAT_TileMapState.LogicLayer[iVar6] & 0x200U) != 0)) {
        bVar2 = true;
      }
      if ((((DAT_TileMapState.LogicLayer[iVar6] & 0x100U) == 0) ||
          (DAT_TileMapState.DamageLayer[iVar6] != 0)) || (bVar2)) {
        if (playerID == DAT_GameSynchronyState.currentPlayerSlotID) {
          WallAndPitchState::addWallPlacementInfoForTile(&DAT_WallAndPitchState,iVar6);
        }
        if ((DAT_TileMapState.DamageLayer[iVar6] != 0) || (bVar2)) {
          DAT_TileMapState.DamageLayer[iVar6] = 0;
          DAT_TileMapState.HeightLayer[iVar6] = DAT_TileMapState.DefaultHeightLayer[iVar6];
          if (bVar2) {
            DAT_TileMapState.LogicLayer[iVar6] =
                 DAT_TileMapState.LogicLayer[iVar6] & 0xffbffdffU | 0x100;
          }
        }
        if ((undefined2)wallType == M_MAPPER_WALL) {
          DAT_TileMapState.HeightLayer[iVar6] = DAT_TileMapState.HeightLayer[iVar6] + 0x5a;
LAB_005031c3:
          if (bVar2) goto LAB_005031c7;
          _normalWallCountUnk = _normalWallCountUnk + 1;
          DAT_TileMapState.LogicLayer[iVar6] =
               DAT_TileMapState.LogicLayer[iVar6] & 0xfff0ffffU | 0x100;
          uVar1 = DAT_TileMapState.UnitLayer[iVar6];
          if ((uVar1 != 0) && (DAT_UnitsState.units[(short)uVar1].unitType == UT_CHICKEN)) {
            DAT_UnitsState.units[(short)uVar1].state.generic = US_DISAPPEAR;
            DAT_UnitsState.units[(short)uVar1].updateTickTracker = 0;
            DAT_UnitsState.units[(short)uVar1].disappearFadeAlphaCountdown = 0;
          }
          if ((DAT_TileMapState.LogicLayer[iVar6] & 8U) != 0) {
            DAT_TileMapState.LogicLayer[iVar6] = DAT_TileMapState.LogicLayer[iVar6] & 0xfffffff7;
            DAT_TileMapState.HeightLayer[iVar6] = DAT_TileMapState.HeightLayer[iVar6] + 4;
          }
          if (((DAT_TileMapState.LogicLayer[iVar6] & 0x1000U) != 0) &&
             (iVar7 = (int)(short)DAT_TileMapState.OrganismLayer[iVar6], iVar7 < 2000)) {
            switch(DAT_LandscapeState.trees[iVar7].treeType) {
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
              DAT_LandscapeState.trees[iVar7].state = 3;
            }
          }
          if (((undefined2)wallType == M_MAPPER_WOODWALL) || (bVar3)) {
            DAT_TileMapState.LogicLayer[iVar6] = DAT_TileMapState.LogicLayer[iVar6] | 0x10000;
          }
          DAT_TileMapState.WallOwnerLayer[iVar6] =
               DAT_TileMapState.WallOwnerLayer[iVar6] & 0xf8 | (char)playerID - 1U;
        }
        else {
          if ((undefined2)wallType == M_MAPPER_WOODWALL) {
            DAT_TileMapState.HeightLayer[iVar6] = DAT_TileMapState.HeightLayer[iVar6] + 0x3c;
            goto LAB_005031c3;
          }
          if ((undefined2)wallType == M_MAPPER_CRENAL) {
            DAT_TileMapState.LogicLayer[iVar6] = DAT_TileMapState.LogicLayer[iVar6] | 0x200;
            BVar4 = hasOnlyTowerNeighborsNoWalls(&DAT_TileMapState,iVar6,y1);
            if (BVar4 == FALSE) {
              DAT_TileMapState.HeightLayer[iVar6] = DAT_TileMapState.HeightLayer[iVar6] + 0x62;
            }
            else {
              DAT_TileMapState.HeightLayer[iVar6] = DAT_TileMapState.HeightLayer[iVar6] + 0x44;
            }
            bVar3 = BVar4 != FALSE;
            if (((local_18 & 1) == 0) || ((y1 & 1) != 0)) {
              if (((local_18 & 1) == 0) && ((y1 & 1) != 0)) {
                DAT_TileMapState.LogicLayer[iVar6] = DAT_TileMapState.LogicLayer[iVar6] | 0x400000;
              }
            }
            else {
              DAT_TileMapState.LogicLayer[iVar6] = DAT_TileMapState.LogicLayer[iVar6] | 0x400000;
            }
            goto LAB_005031c3;
          }
          if ((undefined2)wallType != M_MAPPER_STAIR) goto LAB_005031c3;
                    /* --stairs code-- */
          iVar7 = (local_14 - (uint)DAT_TileMapState.HeightLayer[iVar6]) + -0x10;
          if (0 < iVar7) {
                    /* Sets actual steps tiles */
            DAT_TileMapState.LogicLayer[iVar6] = DAT_TileMapState.LogicLayer[iVar6] | 0x800;
            DAT_TileMapState.HeightLayer[iVar6] = DAT_TileMapState.HeightLayer[iVar6] + (char)iVar7;
            goto LAB_005031c3;
          }
LAB_005031c7:
          if (!bVar2) goto LAB_005032fa;
        }
        Navigation::PathFindingState::updatePathLinkagesInAllEightDirections
                  (&DAT_PathFindingState,y1,iVar6);
        clearMoat(&DAT_TileMapState,iVar6);
        Navigation::PathFindingState::updateWalkAndPathLayer(&DAT_PathFindingState,7,local_18,y1);
      }
LAB_005032fa:
      uVar5 = x1;
      if ((int)local_18 < (int)x2) {
        uVar5 = local_28;
      }
      iVar6 = local_20;
      if ((int)y1 < (int)y2) {
        iVar6 = local_1c;
      }
      if ((undefined2)wallType == M_MAPPER_STAIR) {
        if (iVar6 < (int)uVar5) {
          if ((int)local_18 < (int)x2) {
            x1 = x1 + 1;
            local_18 = local_18 + 1;
            local_28 = local_28 - 1;
          }
          else {
            x1 = x1 - 1;
            local_18 = local_18 - 1;
            local_28 = local_28 + 1;
          }
        }
        else if (iVar6 < 1) {
          local_10 = local_10 + -1;
        }
        else if ((int)y1 < (int)y2) {
          y1 = y1 + 1;
          local_24 = local_24 + 3;
          local_20 = local_20 + 1;
          local_1c = local_1c + -1;
        }
        else {
          y1 = y1 - 1;
          local_24 = local_24 + -3;
          local_20 = local_20 + -1;
          local_1c = local_1c + 1;
        }
      }
      else {
        iVar7 = 1;
        if (uVar5 != 0) {
          if ((int)local_18 < (int)x2) {
            x1 = x1 + 1;
            local_28 = local_28 - 1;
          }
          else {
            x1 = x1 - 1;
            iVar7 = -1;
            local_28 = local_28 + 1;
          }
          local_18 = local_18 + iVar7;
        }
        if (iVar6 != 0) {
          if ((int)y1 < (int)y2) {
            y1 = y1 + 1;
            local_24 = local_24 + 3;
            local_20 = local_20 + 1;
            local_1c = local_1c + -1;
          }
          else {
            y1 = y1 - 1;
            local_24 = local_24 + -3;
            local_20 = local_20 + -1;
            local_1c = local_1c + 1;
          }
        }
        if ((local_18 == x2) && (y1 == y2)) {
          local_10 = local_10 + -1;
        }
      }
      if (0xf < local_14) {
        local_14 = local_14 + -0x10;
      }
    } while (((local_18 != x2) || (y1 != y2)) || (local_10 != 0));
    if ((undefined2)wallType == M_MAPPER_WOODWALL) {
      iVar6 = 0;
      iVar7 = _normalWallCountUnk;
    }
    else {
LAB_00503440:
      iVar7 = 0;
      iVar6 = _normalWallCountUnk;
    }
    Buildings::BuildingsState::processWallBuildingLoss(&DAT_BuildingsState,playerID,iVar6,iVar7,0);
    DAT_PathFindingState.toggleUpdateSeparateAreaTileMap = 1;
    DAT_TileMapState.field204_0x554a30 = 1;
    UI::MinimapViewState::triggerMinimapRedraw(&DAT_MinimapViewState);
  }
  return;
}



