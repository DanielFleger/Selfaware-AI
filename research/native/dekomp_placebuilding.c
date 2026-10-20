// ================= placeBuilding @ 0x005162d0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::placeBuilding
          (TileMapState *this,PlayerID playerID,int x,int y,MappersEnum cbt,int buildingSize,
          int buildingOrientation)

{
  int x_00;
  int yPosition_param;
  ushort uVar1;
  BuildingType type;
  BOOLEnum BVar2;
  int treeID;
  uint uVar3;
  BuildingType buildingType;
  int iVar4;
  int iVar5;
  int *piVar6;
  int local_4;
  
  yPosition_param = y;
  x_00 = x;
  iVar4 = (int)(short)cbt;
  local_4 = 0;
  if (DAT_TileMapState.field122_0x554930 == 0) {
    if (buildingOrientation == 0xf) {
      DAT_TileMapState.DAT_TempBuildingRotation = 0;
    }
    else {
      DAT_TileMapState.DAT_TempBuildingRotation = buildingOrientation / 2;
    }
    checkBuildingCanBePlacedHere(&DAT_TileMapState,playerID,x,y,cbt,buildingSize);
    if (DAT_TileMapState.buildingPlacementFail != FALSE) {
      return;
    }
  }
  DAT_TileMapState.field122_0x554930 = 0;
  uVar1 = Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType(iVar4);
  type = (BuildingType)uVar1;
  if (DAT_GameCore.gameMode_2 == GM_CRUSADER_TUTORIAL) {
    BVar2 = Game::Tutorial_IsActionAllowed(2,(int)(short)uVar1);
    if (BVar2 == FALSE) {
      Global::SetTutorialHintActiveWithTimestamp();
      return;
    }
    Global::SetTutorialBuildingActionState(7,(int)(short)uVar1);
  }
  y = 0;
  do {
    getBuildingSizeIndexMappingData(y,buildingSize);
    iVar5 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + yPosition_param].
            addXgetTile + DAT_TileMapState.buildingX + x;
    if ((DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) &&
       ((DAT_TileMapState.LogicLayer[iVar5] & 0x100U) != 0)) {
      piVar6 = DAT_GameState.playerDataArray[playerID].startResources + 4;
      *piVar6 = *piVar6 + 1;
    }
    if (((DAT_TileMapState.LogicLayer[iVar5] & 0x80) != 0) &&
       (1999 < (short)DAT_TileMapState.OrganismLayer[iVar5])) {
      LandscapeState::removeRock
                (&DAT_LandscapeState,(short)DAT_TileMapState.OrganismLayer[iVar5] + -2000);
      getBuildingSizeIndexMappingData(y,buildingSize);
      Navigation::PathFindingState::updateWalkAndPathLayer
                (&DAT_PathFindingState,8,DAT_TileMapState.buildingX + x,
                 DAT_TileMapState.buildingY + yPosition_param);
    }
    DAT_TileMapState.LogicLayer[iVar5] = DAT_TileMapState.LogicLayer[iVar5] & 0xffbef4f7;
    DAT_TileMapState.HeightLayer[iVar5] = DAT_TileMapState.DefaultHeightLayer[iVar5];
    DAT_TileMapState.DamageLayer[iVar5] = 0;
    if (((DAT_TileMapState.LogicLayer[iVar5] & 0x1000U) != 0) &&
       (treeID = (int)(short)DAT_TileMapState.OrganismLayer[iVar5], treeID < 2000)) {
      switch(DAT_LandscapeState.trees[treeID].treeType) {
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
        LandscapeState::removeTree(&DAT_LandscapeState,treeID);
        Navigation::PathFindingState::updateWalkAndPathLayer
                  (&DAT_PathFindingState,3,x,yPosition_param);
        break;
      default:
        LandscapeState::removeTree(&DAT_LandscapeState,treeID);
        Navigation::PathFindingState::updateWalkAndPathLayer
                  (&DAT_PathFindingState,3,x,yPosition_param);
      }
      getBuildingSizeIndexMappingData(y,buildingSize);
    }
    if ((int)(short)DAT_TileMapState.UnitLayer[iVar5] != 0) {
      switch(uVar1) {
      case 0x2d:
      case 0x2e:
      case 0x31:
      case 0x33:
      case 0x35:
      case 0x37:
      case 0x38:
      case 0x39:
      case 0x3a:
      case 0x3b:
      case 0x43:
      case 0x44:
      case 0x45:
      case 0x4a:
      case 0x4b:
      case 0x4c:
      case 0x4d:
      case 0x4e:
        break;
      default:
        Units::UnitsState::deleteUnit(&DAT_UnitsState,(int)(short)DAT_TileMapState.UnitLayer[iVar5])
        ;
      }
    }
    if ((DAT_TileMapState.LogicLayer[iVar5] & 0x40004000U) != 0) {
      clearMoatDataAtTile(&DAT_TileMapState,DAT_TileMapState.buildingX + x,
                          DAT_TileMapState.buildingY + yPosition_param);
      DAT_TileMapState.LogicLayer[iVar5] = DAT_TileMapState.LogicLayer[iVar5] & 0xbfffbfff;
    }
    DAT_TileMapState.MiscDisplayLayer[iVar5] = DAT_TileMapState.MiscDisplayLayer[iVar5] & 0xfc3f;
    y = y + 1;
    DAT_PathFindingState.toggleUpdateSeparateAreaTileMap = 1;
    DAT_TileMapState.field204_0x554a30 = 1;
  } while (y < DAT_TileMapState.constructionTileCount);
  iVar5 = 0;
                    /* /* 
                       These parameters now become min and max height on the terrain covered by the
                       building 
                       */ */
  y = 1000;
  x = 0;
  do {
    getBuildingSizeIndexMappingData(iVar5,buildingSize);
    uVar3 = (uint)DAT_TileMapState.HeightLayer
                  [DAT_ViewportRenderState.translationMatrix
                   [DAT_TileMapState.buildingY + yPosition_param].addXgetTile +
                   DAT_TileMapState.buildingX + x_00];
    if ((uint)x < uVar3) {
      x = uVar3;
    }
    if (uVar3 < (uint)y) {
      y = uVar3;
    }
    iVar5 = iVar5 + 1;
  } while (iVar5 < DAT_TileMapState.constructionTileCount);
  piVar6 = (int *)((x - y) / 2 + y);
  if ((uVar1 == 0x32) && (playerID == DAT_GameSynchronyState.currentPlayerSlotID)) {
    Units::TribesState::playTunnelerCommandSpeech(&DAT_TribesState);
  }
  buildingType = (BuildingType)(short)uVar1;
  switch(buildingType) {
  case BT_MERCENARYPOST:
  case BT_BARRACKS:
    placeBarracks(&DAT_TileMapState,playerID,x_00,(int *)yPosition_param,type,buildingSize,
                  buildingOrientation,piVar6);
    break;
  case BT_STOCKPILE:
    placeStockpile(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,
                   buildingOrientation,(int)piVar6);
    break;
  default:
    placeWorkshopOrHovel
              (&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,buildingOrientation
               ,piVar6);
    break;
  case BT_QUARRY:
    placeQuarry(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,
                buildingOrientation,(uint)piVar6);
    break;
  case BT_ENGINEERSGUILD:
    placeEngineersguild(&DAT_TileMapState,playerID,(int *)x_00,yPosition_param,type,buildingSize,
                        buildingOrientation,piVar6);
    break;
  case BT_TUNNELERSGUILD:
    placeTunnelersguild(&DAT_TileMapState,playerID,(int *)x_00,yPosition_param,type,buildingSize,
                        buildingOrientation,piVar6);
    break;
  case BT_OILSMELTER:
    placeOilsmelter(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,
                    buildingOrientation,piVar6);
    break;
  case BT_WHEATFARM:
    placeWheatfarm(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,
                   buildingOrientation,piVar6);
    break;
  case BT_HOPFARM:
    placeHopfarm(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,
                 buildingOrientation,(int)piVar6);
    break;
  case BT_APPLEFARM:
    placeApplefarm(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,
                   buildingOrientation,piVar6);
    break;
  case BT_DAIRYFARM:
    placeDairyfarm(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,
                   (int *)buildingOrientation,piVar6);
    break;
  case BT_UNKNOWN1:
    stampBuildingOntoTileMap
              (&DAT_TileMapState,playerID,x_00,yPosition_param,type,iVar4 + -0xf8,buildingSize,
               buildingOrientation,piVar6);
    break;
  case BT_MANORHOUSE:
  case BT_STONEKEEP:
  case BT_STRONGHOLD:
  case BT_KEEPFOUR:
  case BT_KEEPFIVE:
    placeKeep(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,buildingOrientation,
              (int)piVar6);
    break;
  case BT_GATEHOUSELARGE:
    placeGatehouseLarge(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,
                        buildingOrientation,piVar6);
    break;
  case BT_GATEHOUSESMALL:
    placeGatehouseSmall(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,
                        buildingOrientation,piVar6);
    break;
  case BT_WOODGATE1:
    break;
  case BT_DRAWBRIDGE:
    placeDrawbridge(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,
                    (int *)buildingOrientation,piVar6);
    break;
  case BT_FIREBALLISTA:
  case BT_CATAPULT:
  case BT_TREBUCHET:
  case BT_BATTERINGRAM:
  case BT_SIEGETOWER:
  case BT_SHIELD:
    placeSiegeTent(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,
                   buildingOrientation,piVar6);
    break;
  case BT_GARDEN:
    placePositiveFearfactor
              (&DAT_TileMapState,playerID,x_00,yPosition_param,type,iVar4 + -0xa0,buildingSize,
               buildingOrientation,piVar6);
    break;
  case BT_KILLINGPIT:
    placeKillingPit(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,
                    buildingOrientation,(int)piVar6);
    break;
  case BT_PITCHDITCH:
    local_4 = placePitchDitch(&DAT_TileMapState,playerID,x_00,yPosition_param);
    break;
  case BT_SIEGETOWER_PLACED:
    placeSiegetowerPlaced
              (&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,buildingOrientation
               ,piVar6);
    break;
  case BT_TOWER1:
  case BT_TOWER2:
  case BT_TOWER3:
  case BT_TOWER4:
  case BT_TOWER5:
    placeTower(&DAT_TileMapState,playerID,x_00,yPosition_param,type,buildingSize,buildingOrientation
               ,piVar6);
    break;
  case BT_CESSPIT:
    placePositiveFearfactor
              (&DAT_TileMapState,playerID,x_00,yPosition_param,type,iVar4 + -0x12d,buildingSize,
               buildingOrientation,piVar6);
    break;
  case BT_STATUE:
    placePositiveFearfactor
              (&DAT_TileMapState,playerID,x_00,yPosition_param,type,iVar4 + -0x139,buildingSize,
               buildingOrientation,piVar6);
    break;
  case BT_SHRINE:
    placePositiveFearfactor
              (&DAT_TileMapState,playerID,x_00,yPosition_param,type,iVar4 + -0x13e,buildingSize,
               buildingOrientation,piVar6);
    break;
  case BT_POND:
    placePositiveFearfactor
              (&DAT_TileMapState,playerID,x_00,yPosition_param,type,iVar4 + -0x145,buildingSize,
               buildingOrientation,piVar6);
  }
                    /* /*** Now PlacedBuildingID has been set ***/ */
  if (playerID == DAT_GameSynchronyState.currentPlayerSlotID) {
    if (uVar1 == 0x44) {
      if (local_4 != 0) {
        WallAndPitchState::placePitchDitch(&DAT_WallAndPitchState,local_4);
      }
    }
    else {
      WallAndPitchState::startBuildingDestructionConfirmation
                (&DAT_WallAndPitchState,DAT_TileMapState.placedBuildingID);
    }
  }
  Buildings::BuildingsState::processPlacementResourceLossForBuildingType
            (&DAT_BuildingsState,playerID,buildingType,0);
  uVar3 = Buildings::BuildingsState::hasLessWoodThanTheCostOfAWoodcuttersHutAndNoWoodcutters
                    (&DAT_BuildingsState,playerID,buildingType);
  if (uVar3 != 0) {
    DAT_BuildingsState.buildings[DAT_TileMapState.placedBuildingID].field230_0x288 = 1;
  }
  UI::MinimapViewState::triggerMinimapRedraw(&DAT_MinimapViewState);
  if (buildingSize < 6) {
    iVar4 = 9;
  }
  else {
    iVar4 = buildingSize + 5;
  }
  Navigation::PathFindingState::updateWalkAndPathLayer
            (&DAT_PathFindingState,iVar4,x_00,yPosition_param);
  DAT_PathFindingState.toggleUpdateSeparateAreaTileMap = 1;
  DAT_TileMapState.field204_0x554a30 = 1;
  if (DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) {
    DAT_TileMapState.forceUpdateMacroLayerFlag = 1;
    DAT_TileMapState.field68_0x55487c = 200;
  }
  return;
}



