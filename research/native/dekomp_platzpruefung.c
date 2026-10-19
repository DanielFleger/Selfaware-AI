// ================= checkBuildingCanBePlacedHere @ 0x005037b0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::checkBuildingCanBePlacedHere
          (TileMapState *this,int playerID,uint x,uint y_fertileLandCount,
          MappersEnum commandBuildingType,int buildingSize)

{
  uint uVar1;
  uint uVar2;
  byte bVar3;
  uint y;
  int iVar4;
  BOOLEnum BVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  MappersEnum commandBuildingType_00;
  int *piVar10;
  bool bVar11;
  bool bVar12;
  int _grassCount;
  int _distance;
  int _range;
  int _boulderCount;
  int _ironCount;
  int _oilCount;
  int local_4;
  
  y = y_fertileLandCount;
  uVar1 = x;
  bVar12 = buildingSize < 0;
  local_4 = 0;
  if (bVar12) {
    buildingSize = 2;
  }
  commandBuildingType_00 = (MappersEnum)(short)(undefined2)commandBuildingType;
  DAT_TileMapState.buildingPlacementFail = FALSE;
  DAT_TileMapState.placementWarning = 0;
  DAT_TileMapState.field127_0x554944 = 0;
  DAT_TileMapState.uiBuildingRotation = 0xf;
  iVar4 = Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType
                    (commandBuildingType_00);
  DAT_TileMapState.buildingSpriteSheetID_1 =
       DAT_BuildingDefinedData.DAT_Building_SpriteSheet_ID_Array_1[iVar4];
  DAT_TileMapState.buildingSpriteID1 =
       Buildings::BuildingsState::getSpriteID(&DAT_BuildingsState,commandBuildingType_00);
  DAT_TileMapState.buildingSpriteID2 =
       Buildings::BuildingsState::getSpriteID2(&DAT_BuildingsState,commandBuildingType_00);
  iVar4 = Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType
                    (commandBuildingType_00);
  DAT_TileMapState.buildingHeightLimit =
       DAT_BuildingDefinedData.DAT_BuildingPlacement_HeightLimit[iVar4];
  iVar4 = Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType
                    (commandBuildingType_00);
  DAT_TileMapState.buildingMaxHeightDifference =
       DAT_BuildingDefinedData.DAT_BuildingPlacement_MaxHeightDifference[iVar4];
  iVar4 = Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType
                    (commandBuildingType_00);
  DAT_TileMapState.buildingPlacementProperty_3 =
       DAT_BuildingDefinedData.DAT_BuildingPlacement_Property_3[iVar4];
  iVar4 = Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType
                    (commandBuildingType_00);
  DAT_TileMapState.buildingPlacementProperty_4 =
       DAT_BuildingDefinedData.DAT_BuildingPlacement_Property_4[iVar4];
  if (((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
      (DAT_GameSynchronyState.currentPlayerFullIDArray[playerID] != -1)) ||
     (DAT_GameSynchronyState.currentAIArray[playerID] == 0)) {
    DAT_TileMapState.buildingPlacementProperty_4 = 0;
  }
  iVar4 = Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType
                    (commandBuildingType_00);
  DAT_TileMapState.buildingPlacementProperty_5 =
       DAT_BuildingDefinedData.DAT_BuildingPlacement_Property_5[iVar4];
  iVar4 = Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType
                    (commandBuildingType_00);
  DAT_TileMapState.buildingPlacementProperty_6 =
       DAT_BuildingDefinedData.DAT_BuildingPlacement_Property_6[iVar4];
  iVar4 = Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType
                    (commandBuildingType_00);
  DAT_TileMapState.buildingPlacementProperty_7 =
       DAT_BuildingDefinedData.DAT_BuildingPlacement_Property_7[iVar4];
  if ((undefined2)commandBuildingType == M_MAPPER_SIEGE_TOWER_BASE) {
    return;
  }
  _boulderCount = 0;
  _ironCount = 0;
  _oilCount = 0;
  y_fertileLandCount = 0;
  _grassCount = 0;
  storeMinAndMaxHeightOfArea(&DAT_TileMapState,x,y,buildingSize);
  if (bVar12) goto switchD_0050397c_caseD_33;
  if (0x138 < (int)commandBuildingType_00) {
    if (0x144 < (int)commandBuildingType_00) {
      if ((int)commandBuildingType_00 < 0x149) goto switchD_0050397c_caseD_33;
      if (commandBuildingType_00 == M_MAPPER_ARAB_BALLISTA) goto switchD_0050397c_caseD_be;
    }
switchD_0050397c_caseD_35:
    if ((DAT_GameCore.gameMode_2 != GM_EDITOR) && (DAT_GameCore.gameMode_2 != GM_SIEGE_THAT)) {
      bVar11 = DAT_GameSynchronyState.currentGameMode != GM_SOLITARY;
      bVar12 = true;
      x = 0;
      do {
        getBuildingSizeIndexMappingData(x,buildingSize);
        BVar5 = Navigation::PathFindingState::isEnemyTooCloseUnk
                          (&DAT_PathFindingState,playerID,DAT_TileMapState.buildingX + uVar1,
                           DAT_TileMapState.buildingY + y,(-(uint)bVar11 & 0xfffffff1) + 0x1e);
        if (BVar5 != FALSE) {
          DAT_TileMapState.buildingPlacementFailReason = 0x11;
          bVar12 = false;
          break;
        }
        x = x + 1;
      } while ((int)x < DAT_TileMapState.constructionTileCount);
      BVar5 = Navigation::PathFindingState::isSignPostWithinDistance
                        (&DAT_PathFindingState,uVar1,y,
                         DAT_GameState.mapAndTime.unk_signpostDistance + 5);
      if (BVar5 == FALSE) {
        if (bVar12) goto LAB_00503d46;
      }
      else {
        DAT_TileMapState.buildingPlacementFailReason = 0x15;
      }
LAB_00503d3c:
      DAT_TileMapState.buildingPlacementFail = TRUE;
    }
    goto LAB_00503d46;
  }
  if (commandBuildingType_00 == M_MAPPER_DOG_CAGE) {
    if (9 < DAT_GameState.playerDataArray[playerID].dogCageCount) {
      DAT_TileMapState.buildingPlacementFail = TRUE;
      DAT_TileMapState.buildingPlacementFailReason = 1000;
      return;
    }
switchD_0050397c_caseD_62:
    local_4 = 5;
switchD_0050397c_caseD_64:
    if (DAT_GameCore.gameMode_2 == GM_EDITOR) {
      iVar4 = 0;
      do {
        getBuildingSizeIndexMappingData(iVar4,buildingSize);
        iVar6 = Navigation::PathFindingState::isOpponentBuildingInRange
                          (&DAT_PathFindingState,playerID,DAT_TileMapState.buildingX + x,
                           DAT_TileMapState.buildingY + y,7,-1,-1,-1);
        if (iVar6 != 0) goto LAB_005039d6;
        iVar4 = iVar4 + 1;
      } while (iVar4 < DAT_TileMapState.constructionTileCount);
    }
    else if (DAT_GameCore.gameMode_2 != GM_SIEGE_THAT) {
      if (DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) {
        _distance = 0x1e;
        _range = 0x1e;
      }
      else {
        Synchrony::GameSynchronyState::isAIPlayer(&DAT_GameSynchronyState,playerID);
        _distance = 0xf;
        _range = 7;
      }
      x = 0;
      do {
        getBuildingSizeIndexMappingData(x,buildingSize);
        BVar5 = Navigation::PathFindingState::isEnemyTooCloseUnk
                          (&DAT_PathFindingState,playerID,DAT_TileMapState.buildingX + uVar1,
                           DAT_TileMapState.buildingY + y,_distance);
        if (BVar5 != FALSE) {
LAB_00503b32:
          DAT_TileMapState.buildingPlacementFailReason = 0x11;
LAB_00503b48:
          bVar12 = false;
          break;
        }
        if (DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) {
          iVar4 = Navigation::PathFindingState::isOpponentBuildingInRange
                            (&DAT_PathFindingState,playerID,DAT_TileMapState.buildingX + uVar1,
                             DAT_TileMapState.buildingY + y,_range,-1,-1,-1);
          if (iVar4 != 0) goto LAB_00503b32;
          iVar4 = getCastleBuildRangeForMapSize(&DAT_TileMapState);
          iVar4 = Navigation::PathFindingState::isTileInRangeOfKeepRange
                            (&DAT_PathFindingState,playerID,DAT_TileMapState.buildingX + uVar1,
                             DAT_TileMapState.buildingY + y,iVar4 + local_4);
          if (iVar4 == 0) goto LAB_00503b11;
          DAT_TileMapState.buildingPlacementFailReason = 0x12;
          goto LAB_00503b48;
        }
LAB_00503b11:
        x = x + 1;
        bVar12 = true;
      } while ((int)x < DAT_TileMapState.constructionTileCount);
      BVar5 = Navigation::PathFindingState::isSignPostWithinDistance
                        (&DAT_PathFindingState,uVar1,y,
                         DAT_GameState.mapAndTime.unk_signpostDistance + 5);
      if (BVar5 == FALSE) {
        if (bVar12) goto LAB_00503d46;
      }
      else {
        DAT_TileMapState.buildingPlacementFailReason = 0x15;
      }
      DAT_TileMapState.buildingPlacementFail = TRUE;
      if (DAT_TileMapState.buildingPlacementFailReason == BFRE_DEFAULT_CANT_PLACE_THAT_THERE) {
        DAT_TileMapState.buildingPlacementFailReason = 0x12;
      }
    }
  }
  else {
    switch(commandBuildingType_00) {
    case M_MAPPER_WOODSMAN:
    case M_MAPPER_OXENBASE:
    case M_MAPPER_QUARRY:
    case M_MAPPER_TUNNEL:
    case M_MAPPER_TUNNEL_CONSTRUCTION:
    case M_MAPPER_WHEATFARM:
    case M_MAPPER_HOPSFARM:
    case M_MAPPER_APPLEFARM:
    case M_MAPPER_CATTLEFARM:
    case M_MAPPER_IRON_MINE:
    case M_MAPPER_PITCH_WORKINGS:
    case M_MAPPER_QUARRYPILE:
      goto switchD_0050397c_caseD_33;
    case M_MAPPER_STORES:
    case M_MAPPER_GRANARY:
    case M_MAPPER_ARMOURY:
      if (DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) {
        iVar4 = 0;
        do {
          getBuildingSizeIndexMappingData(iVar4,buildingSize);
          BVar5 = Navigation::PathFindingState::isEnemyTooCloseUnk
                            (&DAT_PathFindingState,playerID,DAT_TileMapState.buildingX + x,
                             DAT_TileMapState.buildingY + y,3);
          if (BVar5 != FALSE) goto LAB_005039d6;
          iVar4 = iVar4 + 1;
        } while (iVar4 < DAT_TileMapState.constructionTileCount);
      }
      break;
    default:
      goto switchD_0050397c_caseD_35;
    case M_MAPPER_KILLING_PIT:
    case M_MAPPER_PITCH_DITCH:
    case M_MAPPER_DRAWBRIDGE:
      goto switchD_0050397c_caseD_62;
    case M_MAPPER_GATEHOUSE:
    case M_MAPPER_GATE_MAIN:
    case M_MAPPER_GATE_INNER:
    case M_MAPPER_GATE_WOOD:
    case M_MAPPER_GATE_POSTERN:
    case M_MAPPER_MOAT:
    case M_MAPPER_ANTIMOAT:
    case M_MAPPER_TOWER1:
    case M_MAPPER_TOWER2:
    case M_MAPPER_TOWER3:
    case M_MAPPER_TOWER4:
    case M_MAPPER_TOWER5:
    case M_MAPPER_GATE_WOOD1A:
    case M_MAPPER_GATE_WOOD1B:
    case M_MAPPER_GATE_WOOD1C:
    case M_MAPPER_GATE_WOOD1D:
    case M_MAPPER_GATE_STONE1A:
    case M_MAPPER_GATE_STONE1B:
    case M_MAPPER_GATE_STONE2A:
    case M_MAPPER_GATE_STONE2B:
      goto switchD_0050397c_caseD_64;
    case M_MAPPER_CATAPULT:
    case M_MAPPER_TREBUCHET:
    case M_MAPPER_SIEGE_TOWER:
    case M_MAPPER_BATTERING_RAM:
    case M_MAPPER_PORTABLE_SHIELD:
switchD_0050397c_caseD_be:
      if ((DAT_GameCore.gameMode_2 != GM_EDITOR) && (DAT_GameCore.gameMode_2 != GM_SIEGE_THAT)) {
        iVar4 = 0;
        do {
          getBuildingSizeIndexMappingData(iVar4,buildingSize);
          BVar5 = Navigation::PathFindingState::isEnemyTooCloseUnk
                            (&DAT_PathFindingState,playerID,DAT_TileMapState.buildingX + x,
                             DAT_TileMapState.buildingY + y,3);
          if (BVar5 != FALSE) goto LAB_005039d6;
          iVar4 = iVar4 + 1;
        } while (iVar4 < DAT_TileMapState.constructionTileCount);
      }
    }
  }
LAB_00503d46:
  if (DAT_TileMapState.buildingPlacementFail == FALSE) {
    iVar4 = 0;
    do {
      getBuildingSizeIndexMappingData(iVar4,buildingSize);
      iVar6 = Navigation::PathFindingState::findSomeSuitableLocationUnk
                        (&DAT_PathFindingState,playerID,DAT_TileMapState.buildingX + uVar1,
                         DAT_TileMapState.buildingY + y,2);
      if (iVar6 != 0) {
        DAT_TileMapState.buildingPlacementFailReason = 0x11;
        DAT_TileMapState.buildingPlacementFail = TRUE;
        break;
      }
      iVar4 = iVar4 + 1;
    } while (iVar4 < DAT_TileMapState.constructionTileCount);
  }
switchD_0050397c_caseD_33:
  if (((undefined2)commandBuildingType == M_MAPPER_DRAWBRIDGE) &&
     (0xc < DAT_TileMapState.buildingMaxHeight)) {
    DAT_TileMapState.buildingPlacementFail = TRUE;
  }
  x = 0;
  do {
    getBuildingSizeIndexMappingData(x,buildingSize);
    uVar7 = DAT_TileMapState.buildingY + y;
    if (399 < DAT_TileMapState.buildingX + uVar1) {
      DAT_TileMapState.buildingPlacementFail = 2;
      return;
    }
    if (399 < uVar7) {
      DAT_TileMapState.buildingPlacementFail = 2;
      return;
    }
    if (*(char *)(uVar7 * 400 + 0x21aec98 + DAT_TileMapState.buildingX + uVar1) == '\0') {
      DAT_TileMapState.buildingPlacementFail = 2;
      return;
    }
    iVar4 = DAT_ViewportRenderState.translationMatrix[uVar7].addXgetTile +
            DAT_TileMapState.buildingX + uVar1;
    uVar7 = DAT_TileMapState.LogicLayer[iVar4];
    if ((uVar7 & 0x30) != 0) {
      DAT_TileMapState.buildingPlacementFail = 2;
      return;
    }
    if ((uVar7 & 0x20000) != 0) {
      _boulderCount = _boulderCount + 1;
    }
    if ((uVar7 & 0x80000) != 0) {
      _ironCount = _ironCount + 1;
    }
    if ((int)uVar7 < 0) {
      _oilCount = _oilCount + 1;
    }
    if ((uVar7 & 0x100000) == 0) {
      bVar3 = DAT_TileMapState.Logic2Layer[iVar4];
      if ((bVar3 & 0x10) != 0) {
                    /* grass */
        y_fertileLandCount = y_fertileLandCount + 1;
        _grassCount = _grassCount + 1;
      }
      if ((char)bVar3 < '\0') {
                    /* thick scrub */
        y_fertileLandCount = y_fertileLandCount + 1;
        _grassCount = _grassCount + 1;
      }
      if ((bVar3 & 1) != 0) {
                    /* scrub */
        y_fertileLandCount = y_fertileLandCount + 1;
      }
    }
    iVar4 = isBuildingPlacementAllowedAtTile
                      (&DAT_TileMapState,iVar4,playerID,commandBuildingType_00,0);
    if (iVar4 != 0) {
      DAT_TileMapState.buildingPlacementFail = TRUE;
    }
    x = x + 1;
  } while ((int)x < DAT_TileMapState.constructionTileCount);
  if (((((undefined2)commandBuildingType == M_MAPPER_CATTLEFARM) ||
       ((undefined2)commandBuildingType == M_MAPPER_WHEATFARM)) ||
      ((undefined2)commandBuildingType == M_MAPPER_HOPSFARM)) ||
     ((undefined2)commandBuildingType == M_MAPPER_APPLEFARM)) {
    if ((int)y_fertileLandCount < DAT_TileMapState.constructionTileCount) {
      DAT_TileMapState.buildingPlacementFailReason = 0x16;
      DAT_TileMapState.buildingPlacementFail = TRUE;
      return;
    }
    if (_grassCount < 0x32) {
      DAT_TileMapState.buildingPlacementFailReason = 0x17;
      DAT_TileMapState.buildingPlacementFail = TRUE;
    }
  }
  else {
    if ((undefined2)commandBuildingType != M_MAPPER_QUARRY) {
      if ((((undefined2)commandBuildingType == M_MAPPER_KEEP1) ||
          ((undefined2)commandBuildingType == M_MAPPER_KEEP2)) ||
         ((undefined2)commandBuildingType == M_MAPPER_KEEP3)) {
        buildingSize = (commandBuildingType_00 - M_MAPPER_KEEP1) * 0x60 + 0xb491b8;
        commandBuildingType = M_MAPPER_NULL;
        do {
          uVar7 = *(int *)(buildingSize + 4) + y;
          BVar5 = Rendering::ViewportRenderState::xyAreValid
                            (&DAT_ViewportRenderState,*(int *)buildingSize + uVar1,uVar7);
          if (BVar5 == FALSE) {
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          iVar4 = DAT_ViewportRenderState.translationMatrix[uVar7].addXgetTile +
                  *(int *)buildingSize + uVar1;
          if ((DAT_TileMapState.LogicLayer[iVar4] & 0x30) != 0) {
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          iVar4 = isBuildingPlacementAllowedAtTile
                            (&DAT_TileMapState,iVar4,playerID,commandBuildingType_00,0);
          if (iVar4 != 0) {
            DAT_TileMapState.buildingPlacementFail = TRUE;
          }
          buildingSize = buildingSize + 8;
          commandBuildingType = commandBuildingType + M_MAPPER_AREA;
        } while ((int)commandBuildingType < 3);
        iVar6 = (commandBuildingType_00 - M_MAPPER_KEEP1) * 0x20;
        iVar8 = uVar1 + *(int *)((int)&DAT_TerrainDefinedData + iVar6 + 900);
        iVar4 = *(int *)((int)&DAT_TerrainDefinedData + iVar6 + 0x388);
        x = 0;
        do {
          getBuildingSizeIndexMappingData(x,7);
          uVar7 = DAT_TileMapState.buildingY + y + iVar4;
          uVar2 = DAT_TileMapState.buildingX + iVar8;
          if (399 < uVar2) {
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          if (399 < uVar7) {
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          if (*(char *)(uVar7 * 400 + 0x21aec98 + uVar2) == '\0') {
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          iVar9 = DAT_ViewportRenderState.translationMatrix[uVar7].addXgetTile +
                  DAT_TileMapState.buildingX + iVar8;
          if ((DAT_TileMapState.LogicLayer[iVar9] & 0x30) != 0) {
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          iVar9 = isBuildingPlacementAllowedAtTile
                            (&DAT_TileMapState,iVar9,playerID,commandBuildingType_00,0);
          if (iVar9 != 0) {
            DAT_TileMapState.buildingPlacementFail = TRUE;
          }
          x = x + 1;
        } while ((int)x < DAT_TileMapState.constructionTileCount);
        iVar4 = *(int *)((int)&DAT_TerrainDefinedData + iVar6 + 1000);
        iVar6 = *(int *)((int)&DAT_TerrainDefinedData + iVar6 + 0x3e4) + uVar1;
        x = 0;
        while( true ) {
          getBuildingSizeIndexMappingData(x,5);
          iVar8 = DAT_TileMapState.buildingX;
          uVar1 = DAT_TileMapState.buildingY + iVar4 + y;
          BVar5 = Rendering::ViewportRenderState::xyAreValid
                            (&DAT_ViewportRenderState,iVar6 + DAT_TileMapState.buildingX,uVar1);
          if ((BVar5 == FALSE) ||
             (iVar8 = DAT_ViewportRenderState.translationMatrix[uVar1].addXgetTile + iVar8 + iVar6,
             (DAT_TileMapState.LogicLayer[iVar8] & 0x30) != 0)) break;
          iVar8 = isBuildingPlacementAllowedAtTile
                            (&DAT_TileMapState,iVar8,playerID,commandBuildingType_00,0);
          if (iVar8 != 0) {
            DAT_TileMapState.buildingPlacementFail = TRUE;
          }
          x = x + 1;
          if (DAT_TileMapState.constructionTileCount <= (int)x) {
            return;
          }
        }
      }
      else {
        if (((((undefined2)commandBuildingType != M_MAPPER_GATE_WOOD1A) &&
             ((undefined2)commandBuildingType != M_MAPPER_GATE_WOOD1B)) &&
            ((undefined2)commandBuildingType != M_MAPPER_GATE_WOOD1C)) &&
           ((undefined2)commandBuildingType != M_MAPPER_GATE_WOOD1D)) {
          if ((undefined2)commandBuildingType == M_MAPPER_IRON_MINE) {
            if (3 < _ironCount) {
              return;
            }
            DAT_TileMapState.buildingPlacementFailReason = BFRE_NOT_IRON_ORE;
            DAT_TileMapState.buildingPlacementFail = TRUE;
            return;
          }
          if ((undefined2)commandBuildingType == M_MAPPER_PITCH_WORKINGS) {
            if (0 < _oilCount) {
              return;
            }
            DAT_TileMapState.buildingPlacementFailReason = BFRE_NOT_OIL_MARSH;
            DAT_TileMapState.buildingPlacementFail = TRUE;
            return;
          }
          if ((undefined2)commandBuildingType == M_MAPPER_STORES) {
            if (DAT_GameState.playerDataArray[playerID].stockpile.id == 0) {
              return;
            }
            iVar4 = Buildings::BuildingsState::getEmptyBuildingCount
                              (&DAT_BuildingsState,playerID,BT_STOCKPILE);
            if (iVar4 < 0x20) {
              BVar5 = Buildings::BuildingsState::hasBuildingAsNeighbour
                                (&DAT_BuildingsState,playerID,uVar1,y,buildingSize,BT_STOCKPILE);
              if (BVar5 != FALSE) {
                return;
              }
              DAT_TileMapState.buildingPlacementFail = TRUE;
              DAT_TileMapState.buildingPlacementFailReason = BFRE_NOT_ADJ_STOCKPILE;
              return;
            }
            DAT_TileMapState.buildingPlacementFail = TRUE;
            return;
          }
          if ((undefined2)commandBuildingType == M_MAPPER_GRANARY) {
            if (DAT_GameState.playerDataArray[playerID].granary.id == 0) {
              return;
            }
            iVar4 = Buildings::BuildingsState::getEmptyBuildingCount
                              (&DAT_BuildingsState,playerID,BT_GRANARY);
            if (iVar4 < 8) {
              BVar5 = Buildings::BuildingsState::hasBuildingAsNeighbour
                                (&DAT_BuildingsState,playerID,uVar1,y,buildingSize,BT_GRANARY);
              if (BVar5 != FALSE) {
                return;
              }
              DAT_TileMapState.buildingPlacementFail = TRUE;
              DAT_TileMapState.buildingPlacementFailReason = BFRE_NOT_ADJ_GRANARY;
              return;
            }
            DAT_TileMapState.buildingPlacementFail = TRUE;
            return;
          }
          if ((undefined2)commandBuildingType == M_MAPPER_ARMOURY) {
            if (DAT_GameState.playerDataArray[playerID].armory.id == 0) {
              return;
            }
            iVar4 = Buildings::BuildingsState::getEmptyBuildingCount
                              (&DAT_BuildingsState,playerID,BT_ARMORY);
            if (iVar4 < 8) {
              BVar5 = Buildings::BuildingsState::hasBuildingAsNeighbour
                                (&DAT_BuildingsState,playerID,uVar1,y,buildingSize,BT_ARMORY);
              if (BVar5 != FALSE) {
                return;
              }
              DAT_TileMapState.buildingPlacementFail = TRUE;
              DAT_TileMapState.buildingPlacementFailReason = BFRE_NOT_ADJ_ARMORY;
              return;
            }
            DAT_TileMapState.buildingPlacementFail = TRUE;
            return;
          }
          if (((undefined2)commandBuildingType == M_MAPPER_BARRACKS_EURO) ||
             ((undefined2)commandBuildingType == M_MAPPER_BARRACKS_ARAB)) {
            iVar6 = uVar1 + DAT_TerrainDefinedData.BuildingPartsOffsets
                            [DAT_TileMapState.DAT_TempBuildingRotation][0].x;
            iVar4 = DAT_TerrainDefinedData.BuildingPartsOffsets
                    [DAT_TileMapState.DAT_TempBuildingRotation][0].y;
            x = 0;
            while( true ) {
              getBuildingSizeIndexMappingData(x,5);
              uVar7 = DAT_TileMapState.buildingY + y + iVar4;
              BVar5 = Rendering::ViewportRenderState::xyAreValid
                                (&DAT_ViewportRenderState,DAT_TileMapState.buildingX + iVar6,uVar7);
              if (BVar5 == FALSE) {
                DAT_TileMapState.buildingPlacementFail = 2;
                return;
              }
              iVar8 = DAT_ViewportRenderState.translationMatrix[uVar7].addXgetTile +
                      DAT_TileMapState.buildingX + iVar6;
              if ((DAT_TileMapState.LogicLayer[iVar8] & 0x30) != 0) break;
              iVar8 = isBuildingPlacementAllowedAtTile
                                (&DAT_TileMapState,iVar8,playerID,commandBuildingType_00,0);
              if (iVar8 != 0) {
                DAT_TileMapState.buildingPlacementFail = TRUE;
              }
              x = x + 1;
              if (DAT_TileMapState.constructionTileCount <= (int)x) {
                iVar6 = DAT_TerrainDefinedData.BuildingPartsOffsets
                        [DAT_TileMapState.DAT_TempBuildingRotation][1].x + uVar1;
                iVar4 = DAT_TerrainDefinedData.BuildingPartsOffsets
                        [DAT_TileMapState.DAT_TempBuildingRotation][1].y;
                x = 0;
                while( true ) {
                  getBuildingSizeIndexMappingData(x,5);
                  iVar8 = DAT_TileMapState.buildingX;
                  uVar7 = DAT_TileMapState.buildingY + iVar4 + y;
                  BVar5 = Rendering::ViewportRenderState::xyAreValid
                                    (&DAT_ViewportRenderState,DAT_TileMapState.buildingX + iVar6,
                                     uVar7);
                  if (BVar5 == FALSE) {
                    DAT_TileMapState.buildingPlacementFail = 2;
                    return;
                  }
                  iVar8 = DAT_ViewportRenderState.translationMatrix[uVar7].addXgetTile + iVar8 +
                          iVar6;
                  if ((DAT_TileMapState.LogicLayer[iVar8] & 0x30) != 0) break;
                  iVar8 = isBuildingPlacementAllowedAtTile
                                    (&DAT_TileMapState,iVar8,playerID,commandBuildingType_00,0);
                  if (iVar8 != 0) {
                    DAT_TileMapState.buildingPlacementFail = TRUE;
                  }
                  x = x + 1;
                  if (DAT_TileMapState.constructionTileCount <= (int)x) {
                    iVar6 = DAT_TerrainDefinedData.BuildingPartsOffsets
                            [DAT_TileMapState.DAT_TempBuildingRotation][2].x + uVar1;
                    iVar4 = DAT_TerrainDefinedData.BuildingPartsOffsets
                            [DAT_TileMapState.DAT_TempBuildingRotation][2].y;
                    x = 0;
                    while( true ) {
                      getBuildingSizeIndexMappingData(x,5);
                      iVar8 = DAT_TileMapState.buildingX;
                      uVar1 = DAT_TileMapState.buildingY + iVar4 + y;
                      BVar5 = Rendering::ViewportRenderState::xyAreValid
                                        (&DAT_ViewportRenderState,DAT_TileMapState.buildingX + iVar6
                                         ,uVar1);
                      if (BVar5 == FALSE) {
                        DAT_TileMapState.buildingPlacementFail = 2;
                        return;
                      }
                      iVar8 = DAT_ViewportRenderState.translationMatrix[uVar1].addXgetTile + iVar8 +
                              iVar6;
                      if ((DAT_TileMapState.LogicLayer[iVar8] & 0x30) != 0) break;
                      iVar8 = isBuildingPlacementAllowedAtTile
                                        (&DAT_TileMapState,iVar8,playerID,commandBuildingType_00,0);
                      if (iVar8 != 0) {
                        DAT_TileMapState.buildingPlacementFail = TRUE;
                      }
                      x = x + 1;
                      if (DAT_TileMapState.constructionTileCount <= (int)x) {
                        return;
                      }
                    }
                    DAT_TileMapState.buildingPlacementFail = 2;
                    return;
                  }
                }
                DAT_TileMapState.buildingPlacementFail = 2;
                return;
              }
            }
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          if (((undefined2)commandBuildingType == M_MAPPER_ENGINEERS_GUILD) ||
             ((undefined2)commandBuildingType == M_MAPPER_TUNNELERS_GUILD)) {
            iVar6 = uVar1 + DAT_TerrainDefinedData.BuildingPartsOffsets
                            [DAT_TileMapState.DAT_TempBuildingRotation][1].x;
            iVar4 = DAT_TerrainDefinedData.BuildingPartsOffsets
                    [DAT_TileMapState.DAT_TempBuildingRotation][1].y;
            x = 0;
            while( true ) {
              getBuildingSizeIndexMappingData(x,5);
              uVar1 = DAT_TileMapState.buildingY + y + iVar4;
              BVar5 = Rendering::ViewportRenderState::xyAreValid
                                (&DAT_ViewportRenderState,DAT_TileMapState.buildingX + iVar6,uVar1);
              if (BVar5 == FALSE) {
                DAT_TileMapState.buildingPlacementFail = 2;
                return;
              }
              iVar8 = DAT_ViewportRenderState.translationMatrix[uVar1].addXgetTile +
                      DAT_TileMapState.buildingX + iVar6;
              if ((DAT_TileMapState.LogicLayer[iVar8] & 0x30) != 0) break;
              iVar8 = isBuildingPlacementAllowedAtTile
                                (&DAT_TileMapState,iVar8,playerID,commandBuildingType_00,0);
              if (iVar8 != 0) {
                DAT_TileMapState.buildingPlacementFail = TRUE;
              }
              x = x + 1;
              if (DAT_TileMapState.constructionTileCount <= (int)x) {
                return;
              }
            }
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          if ((undefined2)commandBuildingType == M_MAPPER_OIL_SMELTER) {
            iVar6 = uVar1 + DAT_TerrainDefinedData.field63_0x19c
                            [DAT_TileMapState.DAT_TempBuildingRotation].x;
            iVar4 = DAT_TerrainDefinedData.field63_0x19c[DAT_TileMapState.DAT_TempBuildingRotation].
                    y;
            x = 0;
            while( true ) {
              getBuildingSizeIndexMappingData(x,4);
              uVar1 = DAT_TileMapState.buildingY + y + iVar4;
              BVar5 = Rendering::ViewportRenderState::xyAreValid
                                (&DAT_ViewportRenderState,DAT_TileMapState.buildingX + iVar6,uVar1);
              if (BVar5 == FALSE) {
                DAT_TileMapState.buildingPlacementFail = 2;
                return;
              }
              iVar8 = DAT_ViewportRenderState.translationMatrix[uVar1].addXgetTile +
                      DAT_TileMapState.buildingX + iVar6;
              if ((DAT_TileMapState.LogicLayer[iVar8] & 0x30) != 0) break;
              iVar8 = isBuildingPlacementAllowedAtTile
                                (&DAT_TileMapState,iVar8,playerID,M_MAPPER_OIL_SMELTER,0);
              if (iVar8 != 0) {
                DAT_TileMapState.buildingPlacementFail = TRUE;
              }
              x = x + 1;
              if (DAT_TileMapState.constructionTileCount <= (int)x) {
                return;
              }
            }
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          if ((undefined2)commandBuildingType != M_MAPPER_TUNNEL_CONSTRUCTION) {
            return;
          }
          Navigation::PathFindingState::algTunnelerFindTarget
                    (&DAT_PathFindingState,playerID,0,0x4c,uVar1,y);
          if (DAT_PathFindingState.ALG_TargetTile != 0) {
            return;
          }
          DAT_TileMapState.buildingPlacementFail = TRUE;
          return;
        }
        iVar4 = commandBuildingType_00 * 3 + -0x1a4;
        iVar8 = uVar1 + *(int *)((int)&DAT_TerrainDefinedData + iVar4 * 8 + 0x56c);
        iVar4 = iVar4 * 8;
        iVar6 = *(int *)((int)&DAT_TerrainDefinedData + iVar4 + 0x570);
        x = 0;
        do {
          getBuildingSizeIndexMappingData(x,3);
          uVar7 = DAT_TileMapState.buildingY + y + iVar6;
          BVar5 = Rendering::ViewportRenderState::xyAreValid
                            (&DAT_ViewportRenderState,DAT_TileMapState.buildingX + iVar8,uVar7);
          if (BVar5 == FALSE) {
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          iVar9 = DAT_ViewportRenderState.translationMatrix[uVar7].addXgetTile +
                  DAT_TileMapState.buildingX + iVar8;
          if ((DAT_TileMapState.LogicLayer[iVar9] & 0x30) != 0) {
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          iVar9 = isBuildingPlacementAllowedAtTile
                            (&DAT_TileMapState,iVar9,playerID,commandBuildingType_00,0);
          if (iVar9 != 0) {
            DAT_TileMapState.buildingPlacementFail = TRUE;
          }
          x = x + 1;
        } while ((int)x < DAT_TileMapState.constructionTileCount);
        iVar6 = *(int *)((int)&DAT_TerrainDefinedData + iVar4 + 0x57c);
        iVar4 = *(int *)((int)&DAT_TerrainDefinedData + iVar4 + 0x578) + uVar1;
        x = 0;
        do {
          getBuildingSizeIndexMappingData(x,3);
          iVar8 = DAT_TileMapState.buildingX;
          uVar7 = DAT_TileMapState.buildingY + iVar6 + y;
          BVar5 = Rendering::ViewportRenderState::xyAreValid
                            (&DAT_ViewportRenderState,iVar4 + DAT_TileMapState.buildingX,uVar7);
          if (BVar5 == FALSE) {
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          iVar8 = DAT_ViewportRenderState.translationMatrix[uVar7].addXgetTile + iVar8 + iVar4;
          if ((DAT_TileMapState.LogicLayer[iVar8] & 0x30) != 0) {
            DAT_TileMapState.buildingPlacementFail = 2;
            return;
          }
          iVar8 = isBuildingPlacementAllowedAtTile
                            (&DAT_TileMapState,iVar8,playerID,commandBuildingType_00,0);
          if (iVar8 != 0) {
            DAT_TileMapState.buildingPlacementFail = TRUE;
          }
          x = x + 1;
        } while ((int)x < DAT_TileMapState.constructionTileCount);
        commandBuildingType = M_MAPPER_NULL;
        piVar10 = (int *)((int)&DAT_TerrainDefinedData +
                         (commandBuildingType_00 * 3 + -0x1a4) * 0x10 + 0x5cc);
        while( true ) {
          iVar4 = piVar10[1];
          iVar6 = *piVar10;
          BVar5 = Rendering::ViewportRenderState::xyAreValid
                            (&DAT_ViewportRenderState,uVar1 + iVar6,iVar4 + y);
          if ((BVar5 == FALSE) ||
             (iVar4 = DAT_ViewportRenderState.translationMatrix[iVar4 + y].addXgetTile + iVar6 +
                      uVar1, (DAT_TileMapState.LogicLayer[iVar4] & 0x30) != 0)) break;
          iVar4 = isBuildingPlacementAllowedAtTile
                            (&DAT_TileMapState,iVar4,playerID,commandBuildingType_00,0);
          if (iVar4 != 0) {
            DAT_TileMapState.buildingPlacementFail = TRUE;
          }
          commandBuildingType = commandBuildingType + M_MAPPER_AREA;
          piVar10 = piVar10 + 2;
          if (5 < (int)commandBuildingType) {
            return;
          }
        }
      }
      DAT_TileMapState.buildingPlacementFail = 2;
      return;
    }
    if (_boulderCount < 8) {
      DAT_TileMapState.buildingPlacementFail = TRUE;
      return;
    }
  }
  return;
LAB_005039d6:
  DAT_TileMapState.buildingPlacementFailReason = 0x11;
  goto LAB_00503d3c;
}



