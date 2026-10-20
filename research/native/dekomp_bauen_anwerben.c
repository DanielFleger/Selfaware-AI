// ================= MenuItemActionHandler_InGameMenu_TriggerPlaceBuildingCommand @ 0x004451c0 =================

/* WARNING: Type propagation algorithm not settling */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "MappersEnumInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::UI::MenuItemActionHandler_InGameMenu_TriggerPlaceBuildingCommand(int param_1,...)

{
  BuildingTypeShort BVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  DWORD DVar5;
  BOOLEnum BVar6;
  GmID GVar7;
  uint uVar8;
  GmID imageY;
  int iVar9;
  MappersEnum MVar10;
  GmID imageX;
  bool bVar11;
  int local_8;
  GmID local_4;
  
  if (DAT_GameSynchronyState.syncStatus != 0) {
    return;
  }
  if (DAT_GameSynchronyState.saveRelated != 0) {
    return;
  }
  if (DAT_GameCore.gamePausedLogical != 0) {
    return;
  }
  DAT_TileMapState.DAT_BuildingSize =
       Map::TileMapState::getBuildingSizeForCommandBuildingType
                 (&DAT_TileMapState,DAT_TileMapState.currentMapperCommand);
  if (DAT_TileMapState.DAT_BuildingSize < 0) {
    DAT_TileMapState.DAT_BuildingSize = 0;
    return;
  }
  BottomLeftTextDisplayState::setBottomLeftTextDisplayText
            (&DAT_BottomLeftTextDisplayState,2,-1,0,
             (TextMessageBLLookupStructUnion)DAT_TileMapState.currentMapperCommand,0x32,-1);
  if (DAT_ViewportRenderState.viewportState.field0_0x0 == 0) {
    return;
  }
  DAT_TileMapState.buildingPlacementFailReason = BFRE_DEFAULT_CANT_PLACE_THAT_THERE;
  if (DAT_TileMapState.flatViewToggleValue1 == 0) {
    _HoldStrong::Rendering::ViewportRenderState::setupMouseTileXY();
  }
  else {
    _HoldStrong::Rendering::ViewportRenderState::setupMouseTileXY2();
  }
  if ((DAT_MouseState.leftClickStart == 0) && (DAT_ScrollingHandler.isScrolling_0x0 != FALSE)) {
    return;
  }
  DAT_TileMapState.DAT_ClickedTileY = DAT_ViewportRenderState.viewportState.mouseTileY;
  DAT_TileMapState.DAT_ClickedTileX = DAT_ViewportRenderState.viewportState.mouseTileX;
  if (DAT_TileMapState.currentMapperCommand == M_MAPPER_MANGONEL) {
    iVar2 = DAT_ViewportRenderState.translationMatrix
            [DAT_ViewportRenderState.viewportState.mouseTileY].addXgetTile +
            DAT_ViewportRenderState.viewportState.mouseTileX;
    iVar9 = (int)(short)DAT_TileMapState.BuildingLayer[iVar2];
    if (DAT_MouseState.draggingStopped == FALSE) {
      if ((((iVar9 != 0) &&
           (DAT_BuildingsState.buildings[iVar9].owner == DAT_GameSynchronyState.currentPlayerSlotID)
           ) && ((BVar1 = DAT_BuildingsState.buildings[iVar9].buildingType, BVar1 == BT_TOWER4 ||
                 (BVar1 == BT_TOWER5)))) &&
         ((((DAT_TileMapState.LogicLayer[iVar2] & 0x10000000U) != 0 &&
           (DAT_TileMapState.UnitLayer[iVar2] == 0)) &&
          (DAT_BuildingsState.buildings[iVar9].containsSiegeMangonel1OrBallista2 == 0)))) {
        _HoldStrong::Rendering::ViewportRenderState::createFloatingLayerElement
                  (&DAT_ViewportRenderState,GID_BODY_MANGONEL,1,0,0,iVar2,5);
        return;
      }
      _HoldStrong::Rendering::ViewportRenderState::createFloatingLayerElement
                (&DAT_ViewportRenderState,GID_BODY_MANGONEL,1,0,0,iVar2,0x100005);
      return;
    }
    if (iVar9 == 0) {
      return;
    }
    if (DAT_BuildingsState.buildings[iVar9].owner != DAT_GameSynchronyState.currentPlayerSlotID) {
      return;
    }
    BVar1 = DAT_BuildingsState.buildings[iVar9].buildingType;
    if ((BVar1 != BT_TOWER4) && (BVar1 != BT_TOWER5)) {
      return;
    }
    if ((DAT_TileMapState.LogicLayer[iVar2] & 0x10000000U) == 0) {
      return;
    }
    if (DAT_TileMapState.UnitLayer[iVar2] != 0) {
      return;
    }
    if (DAT_BuildingsState.buildings[iVar9].containsSiegeMangonel1OrBallista2 != 0) {
      return;
    }
    iVar2 = Game::GameStateStructures::checkRequiredResourcesForBuildingOrPlanToBuy
                      (&DAT_GameState,M_MAPPER_MANGONEL,DAT_GameSynchronyState.currentPlayerSlotID,
                       TRUE);
    if (iVar2 == 0) {
      return;
    }
    HoveredState::createHoverStateElement
              (&DAT_HoveredState,DAT_TileMapState.DAT_ClickedTileX,DAT_TileMapState.DAT_ClickedTileY
               ,DAT_TileMapState.currentMapperCommand,DAT_TileMapState.DAT_BuildingSize,0);
    iVar2 = (int)(short)DAT_BuildingsState.buildings[iVar9].y;
    DAT_TileMapState.DAT_ClickedTileX = (short)DAT_BuildingsState.buildings[iVar9].x + 2;
    DAT_TileMapState.DAT_ClickedTileY = iVar2 + 2;
    DAT_GameSynchronyState.DAT_GameCommandParam0 = DAT_TileMapState.DAT_ClickedTileX * 8 + 4;
    DAT_GameSynchronyState.DAT_GameCommandParam1 = DAT_TileMapState.DAT_ClickedTileY * 8 + 4;
    DAT_GameSynchronyState.DAT_GameCommandParam2 =
         (GmID)*(byte *)(DAT_ViewportRenderState.translationMatrix[iVar2 + 2].addXgetTile +
                         0x1d32c38 + DAT_TileMapState.DAT_ClickedTileX);
    DAT_GameSynchronyState.DAT_GameCommandParam3 = 0x29;
    Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SIEGE_TENT);
    return;
  }
  if (DAT_TileMapState.currentMapperCommand == M_MAPPER_BALLISTA) {
    iVar2 = DAT_ViewportRenderState.translationMatrix
            [DAT_ViewportRenderState.viewportState.mouseTileY].addXgetTile +
            DAT_ViewportRenderState.viewportState.mouseTileX;
    iVar9 = (int)(short)DAT_TileMapState.BuildingLayer[iVar2];
    if (DAT_MouseState.draggingStopped == FALSE) {
      if ((((iVar9 != 0) &&
           (DAT_BuildingsState.buildings[iVar9].owner == DAT_GameSynchronyState.currentPlayerSlotID)
           ) && ((BVar1 = DAT_BuildingsState.buildings[iVar9].buildingType, BVar1 == BT_TOWER4 ||
                 (BVar1 == BT_TOWER5)))) &&
         ((((DAT_TileMapState.LogicLayer[iVar2] & 0x10000000U) != 0 &&
           (DAT_TileMapState.UnitLayer[iVar2] == 0)) &&
          (DAT_BuildingsState.buildings[iVar9].containsSiegeMangonel1OrBallista2 == 0)))) {
        _HoldStrong::Rendering::ViewportRenderState::createFloatingLayerElement
                  (&DAT_ViewportRenderState,GID_BODY_BALLISTA,1,0,0,iVar2,5);
        return;
      }
      _HoldStrong::Rendering::ViewportRenderState::createFloatingLayerElement
                (&DAT_ViewportRenderState,GID_BODY_BALLISTA,1,0,0,iVar2,0x100005);
      return;
    }
    if (iVar9 == 0) {
      return;
    }
    if (DAT_BuildingsState.buildings[iVar9].owner != DAT_GameSynchronyState.currentPlayerSlotID) {
      return;
    }
    BVar1 = DAT_BuildingsState.buildings[iVar9].buildingType;
    if ((BVar1 != BT_TOWER4) && (BVar1 != BT_TOWER5)) {
      return;
    }
    if ((DAT_TileMapState.LogicLayer[iVar2] & 0x10000000U) == 0) {
      return;
    }
    if (DAT_TileMapState.UnitLayer[iVar2] != 0) {
      return;
    }
    if (DAT_BuildingsState.buildings[iVar9].containsSiegeMangonel1OrBallista2 != 0) {
      return;
    }
    iVar2 = Game::GameStateStructures::checkRequiredResourcesForBuildingOrPlanToBuy
                      (&DAT_GameState,M_MAPPER_BALLISTA,DAT_GameSynchronyState.currentPlayerSlotID,
                       TRUE);
    if (iVar2 == 0) {
      return;
    }
    HoveredState::createHoverStateElement
              (&DAT_HoveredState,DAT_TileMapState.DAT_ClickedTileX,DAT_TileMapState.DAT_ClickedTileY
               ,DAT_TileMapState.currentMapperCommand,DAT_TileMapState.DAT_BuildingSize,0);
    iVar2 = (int)(short)DAT_BuildingsState.buildings[iVar9].y;
    DAT_TileMapState.DAT_ClickedTileX = (short)DAT_BuildingsState.buildings[iVar9].x + 2;
    DAT_TileMapState.DAT_ClickedTileY = iVar2 + 2;
    DAT_GameSynchronyState.DAT_GameCommandParam0 = DAT_TileMapState.DAT_ClickedTileX * 8 + 4;
    DAT_GameSynchronyState.DAT_GameCommandParam1 = DAT_TileMapState.DAT_ClickedTileY * 8 + 4;
    DAT_GameSynchronyState.DAT_GameCommandParam2 =
         (GmID)*(byte *)(DAT_ViewportRenderState.translationMatrix[iVar2 + 2].addXgetTile +
                         0x1d32c38 + DAT_TileMapState.DAT_ClickedTileX);
    DAT_GameSynchronyState.DAT_GameCommandParam3 = 0x3d;
    Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SIEGE_TENT);
    return;
  }
  if (((DAT_TileMapState.currentMapperCommand != M_MAPPER_FLAG_TYPE0) &&
      (DAT_TileMapState.currentMapperCommand != M_MAPPER_FLAG_TYPE1)) &&
     ((DAT_TileMapState.currentMapperCommand != M_MAPPER_FLAG_TYPE2 &&
      (DAT_TileMapState.currentMapperCommand != M_MAPPER_FLAG_TYPE3)))) {
    if (DAT_TileMapState.currentMapperCommand == M_MAPPER_HEADS) {
      iVar2 = DAT_ViewportRenderState.translationMatrix
              [DAT_ViewportRenderState.viewportState.mouseTileY].addXgetTile +
              DAT_ViewportRenderState.viewportState.mouseTileX;
      iVar9 = DAT_TileMapState.field193_0x554a1c + 1;
      if (DAT_MouseState.draggingStopped == FALSE) {
        iVar3 = Map::TileMapState::getTotalHeightAt
                          (&DAT_TileMapState,iVar2,DAT_GameSynchronyState.currentPlayerSlotID);
        if ((-1 < iVar3) && ((DAT_TileMapState.MiscDisplayLayer[iVar2] & 0x1000) == 0)) {
          _HoldStrong::Rendering::ViewportRenderState::createFloatingLayerElement
                    (&DAT_ViewportRenderState,GID_ANIM_HEADS,iVar9,0xf,7,iVar2,0x1d);
          return;
        }
        _HoldStrong::Rendering::ViewportRenderState::createFloatingLayerElement
                  (&DAT_ViewportRenderState,GID_ANIM_HEADS,iVar9,0xf,7,iVar2,0x18001d);
        return;
      }
      iVar9 = Map::TileMapState::getTotalHeightAt
                        (&DAT_TileMapState,iVar2,DAT_GameSynchronyState.currentPlayerSlotID);
      if (iVar9 < 0) {
        return;
      }
      if ((DAT_TileMapState.MiscDisplayLayer[iVar2] & 0x1000) != 0) {
        return;
      }
      iVar2 = DAT_TileMapState.DAT_ClickedTileY * 8;
      iVar3 = DAT_TileMapState.DAT_ClickedTileX * 8;
      HoveredState::createHoverStateElement
                (&DAT_HoveredState,DAT_TileMapState.DAT_ClickedTileX,
                 DAT_TileMapState.DAT_ClickedTileY,DAT_TileMapState.currentMapperCommand,
                 DAT_TileMapState.field193_0x554a1c,0);
      DAT_GameSynchronyState.DAT_GameCommandParam5 = DAT_TileMapState.field193_0x554a1c;
      DAT_GameSynchronyState.DAT_GameCommandParam0 = DAT_GameSynchronyState.currentPlayerSlotID;
      DAT_GameSynchronyState.DAT_GameCommandParam4 = 0xf;
      DAT_GameSynchronyState.DAT_GameCommandParam1 = iVar3;
      DAT_GameSynchronyState.DAT_GameCommandParam2 = iVar2;
      DAT_GameSynchronyState.DAT_GameCommandParam3 = iVar9;
      Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SPAWN_ENTITY);
      DAT_TileMapState.field193_0x554a1c = (int)SEC_RNG.currentNumber1 % 7;
      Random::RNG::nextRandomNumber1(&SEC_RNG);
      return;
    }
    if (DAT_TileMapState.currentMapperCommand == M_MAPPER_BRAZIER) {
      iVar2 = DAT_ViewportRenderState.translationMatrix
              [DAT_ViewportRenderState.viewportState.mouseTileY].addXgetTile +
              DAT_ViewportRenderState.viewportState.mouseTileX;
      bVar11 = true;
      if ((DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) &&
         (Map::Buildings::BuildingsState::getBuildingCost
                    (&DAT_BuildingsState,M_MAPPER_BRAZIER,&local_8,(int *)&local_4),
         DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].startResources
         [0xf] < (int)local_4)) {
        bVar11 = false;
      }
      if (DAT_MouseState.draggingStopped == FALSE) {
        uVar4 = Map::TileMapState::getHeightAtTileIncludingOwnersBuildings
                          (&DAT_TileMapState,iVar2,DAT_GameSynchronyState.currentPlayerSlotID);
        if ((uVar4 == 0) || (!bVar11)) {
          iVar9 = 0x10001d;
        }
        else {
          iVar9 = 0x1d;
        }
        _HoldStrong::Rendering::ViewportRenderState::createFloatingLayerElement
                  (&DAT_ViewportRenderState,GID_BODY_BRAZIER,1,0xf,7,iVar2,iVar9);
        return;
      }
      uVar4 = Map::TileMapState::getHeightAtTileIncludingOwnersBuildings
                        (&DAT_TileMapState,iVar2,DAT_GameSynchronyState.currentPlayerSlotID);
      if (uVar4 == 0) {
        return;
      }
      if (!bVar11) {
        return;
      }
      HoveredState::createHoverStateElement
                (&DAT_HoveredState,DAT_TileMapState.DAT_ClickedTileX,
                 DAT_TileMapState.DAT_ClickedTileY,DAT_TileMapState.currentMapperCommand,
                 DAT_TileMapState.DAT_BuildingSize,0);
      imageX = DAT_TileMapState.DAT_ClickedTileX * 8;
      imageY = DAT_TileMapState.DAT_ClickedTileY * 8;
      DAT_GameSynchronyState.DAT_GameCommandParam3 =
           Map::TileMapState::getTotalHeightAtTile(&DAT_TileMapState,iVar2);
      if (DAT_TileMapState.mapOrientation == 2) {
        imageX = imageX + GID_TILE_BUILDINGS_2;
      }
      else if (DAT_TileMapState.mapOrientation == 4) {
        imageX = imageX + GID_TILE_BUILDINGS_2;
        imageY = imageY + GID_TILE_BUILDINGS_2;
      }
      else if (DAT_TileMapState.mapOrientation == 6) {
        imageY = imageY + GID_TILE_BUILDINGS_2;
      }
      DAT_GameSynchronyState.DAT_GameCommandParam4 = GID_TILE_FARMLAND;
      goto LAB_004467a9;
    }
    if ((((((DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINT1) ||
           (DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINT2)) ||
          (DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINT3)) ||
         ((DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINT4 ||
          (DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINT5)))) ||
        (DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINT6)) ||
       (DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINT7)) {
      Map::Buildings::BuildingsState::createEntityForAssemblyPointsForActiveTabType
                (&DAT_BuildingsState);
      iVar9 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.DAT_ClickedTileY].
              addXgetTile + DAT_TileMapState.DAT_ClickedTileX;
      iVar2 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].barracks.id;
      if (iVar2 < 1) {
        bVar11 = false;
      }
      else {
        iVar3 = Map::Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                          (&DAT_PathFindingState,DAT_GameSynchronyState.currentPlayerSlotID,
                           (int)(short)DAT_TileMapState.PathConnectionLayer
                                       [(int)DAT_GameState.playerDataArray
                                             [DAT_GameSynchronyState.currentPlayerSlotID].
                                             barracksParadegroundLocations[0][0].x +
                                        DAT_ViewportRenderState.translationMatrix
                                        [DAT_GameState.playerDataArray
                                         [DAT_GameSynchronyState.currentPlayerSlotID].
                                         barracksParadegroundLocations[0][0].y].addXgetTile],
                           (int)(short)DAT_TileMapState.PathConnectionLayer[iVar9],0);
        bVar11 = iVar3 != 0;
        if ((short)DAT_TileMapState.BuildingLayer[iVar9] == iVar2) {
          bVar11 = true;
        }
      }
      if (DAT_MouseState.draggingStopped != FALSE) {
        if (!bVar11) {
          return;
        }
        DAT_GameSynchronyState.DAT_GameCommandParam0 =
             DAT_TileMapState.currentMapperCommand - M_MAPPER_PLACE_ASSEMBLY_POINT1;
LAB_004465a6:
        DAT_GameSynchronyState.DAT_GameCommandParam1 = DAT_TileMapState.DAT_ClickedTileX;
        DAT_GameSynchronyState.DAT_GameCommandParam2 = DAT_TileMapState.DAT_ClickedTileY;
        Synchrony::GameSynchronyState::queueCommand
                  (&DAT_GameSynchronyState,
                   GCT_SHARE_GAME_STATE_PARTIAL_HASHES|GCT_MULTIPLAYER_INITIATE_ANNOUNCE_HOST);
        DAT_TileMapState.currentMapperCommand = M_MAPPER_NULL;
        return;
      }
LAB_0044654b:
      if (bVar11) {
        iVar2 = 0xd;
        goto LAB_0044655d;
      }
LAB_00446558:
      iVar2 = 0x18000d;
LAB_0044655d:
      _HoldStrong::Rendering::ViewportRenderState::createFloatingLayerElement
                (&DAT_ViewportRenderState,GID_FLOATS_NEW,0x61,0xf,7,iVar9,iVar2);
      return;
    }
                    /* These mappers are likely wrong in SHC */
    if ((((DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINTM1) ||
         (DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINTM2)) ||
        ((DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINTM3 ||
         (((DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINTM4 ||
           (DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINTM5)) ||
          (DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINTM6)))))) ||
       (DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINTM7)) {
      Map::Buildings::BuildingsState::createEntityForAssemblyPointsForActiveTabType
                (&DAT_BuildingsState);
      iVar9 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.DAT_ClickedTileY].
              addXgetTile + DAT_TileMapState.DAT_ClickedTileX;
      iVar2 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
              mercenaryPost.id;
      if (iVar2 < 1) {
        bVar11 = false;
      }
      else {
        iVar3 = Map::Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                          (&DAT_PathFindingState,DAT_GameSynchronyState.currentPlayerSlotID,
                           (int)(short)DAT_TileMapState.PathConnectionLayer
                                       [(int)DAT_GameState.playerDataArray
                                             [DAT_GameSynchronyState.currentPlayerSlotID].structure.
                                             mercenaryOutpostCampgroundLocations[0].x +
                                        DAT_ViewportRenderState.translationMatrix
                                        [DAT_GameState.playerDataArray
                                         [DAT_GameSynchronyState.currentPlayerSlotID].structure.
                                         mercenaryOutpostCampgroundLocations[0].y].addXgetTile],
                           (int)(short)DAT_TileMapState.PathConnectionLayer[iVar9],0);
        bVar11 = iVar3 != 0;
        if ((short)DAT_TileMapState.BuildingLayer[iVar9] == iVar2) {
          bVar11 = true;
        }
      }
      if (DAT_MouseState.draggingStopped != FALSE) {
        if (!bVar11) {
          return;
        }
        DAT_GameSynchronyState.DAT_GameCommandParam0 =
             DAT_TileMapState.currentMapperCommand - M_MAPPER_PEOPLE_ARAB_BOW;
        goto LAB_004465a6;
      }
      goto LAB_0044654b;
    }
    if ((DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINTE1) ||
       (DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINTE2)) {
      Map::Buildings::BuildingsState::createEntityForAssemblyPointsForActiveTabType
                (&DAT_BuildingsState);
      iVar9 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.DAT_ClickedTileY].
              addXgetTile + DAT_TileMapState.DAT_ClickedTileX;
      iVar2 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
              engineersGuild.id;
      if (iVar2 < 1) {
        bVar11 = false;
      }
      else {
        iVar3 = Map::Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                          (&DAT_PathFindingState,DAT_GameSynchronyState.currentPlayerSlotID,
                           (int)(short)DAT_TileMapState.PathConnectionLayer
                                       [(int)DAT_GameState.playerDataArray
                                             [DAT_GameSynchronyState.currentPlayerSlotID].
                                             engineersParadegroundLocations[0].x +
                                        DAT_ViewportRenderState.translationMatrix
                                        [DAT_GameState.playerDataArray
                                         [DAT_GameSynchronyState.currentPlayerSlotID].
                                         engineersParadegroundLocations[0].y].addXgetTile],
                           (int)(short)DAT_TileMapState.PathConnectionLayer[iVar9],0);
        bVar11 = iVar3 != 0;
        if ((short)DAT_TileMapState.BuildingLayer[iVar9] == iVar2) {
          bVar11 = true;
        }
      }
      if (DAT_MouseState.draggingStopped != FALSE) {
        if (!bVar11) {
          return;
        }
        DAT_GameSynchronyState.DAT_GameCommandParam0 =
             DAT_TileMapState.currentMapperCommand - M_MAPPER_SUB_MENU_GOOD;
        goto LAB_004465a6;
      }
      goto LAB_0044654b;
    }
    if (DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINTT1) {
      Map::Buildings::BuildingsState::createEntityForAssemblyPointsForActiveTabType
                (&DAT_BuildingsState);
      iVar9 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.DAT_ClickedTileY].
              addXgetTile + DAT_TileMapState.DAT_ClickedTileX;
      iVar2 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
              tunnelersGuild.id;
      if (iVar2 < 1) {
        bVar11 = false;
      }
      else {
        iVar3 = Map::Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                          (&DAT_PathFindingState,DAT_GameSynchronyState.currentPlayerSlotID,
                           (int)(short)DAT_TileMapState.PathConnectionLayer
                                       [(int)DAT_GameState.playerDataArray
                                             [DAT_GameSynchronyState.currentPlayerSlotID].
                                             tunnelersGuildParadegroundLocations[0].x +
                                        DAT_ViewportRenderState.translationMatrix
                                        [DAT_GameState.playerDataArray
                                         [DAT_GameSynchronyState.currentPlayerSlotID].
                                         tunnelersGuildParadegroundLocations[0].y].addXgetTile],
                           (int)(short)DAT_TileMapState.PathConnectionLayer[iVar9],0);
        bVar11 = iVar3 != 0;
        if ((short)DAT_TileMapState.BuildingLayer[iVar9] == iVar2) {
          bVar11 = true;
        }
      }
      if (DAT_MouseState.draggingStopped != FALSE) {
        if (!bVar11) {
          return;
        }
        DAT_GameSynchronyState.DAT_GameCommandParam0 = 0x1e;
        goto LAB_004465a6;
      }
      goto LAB_0044654b;
    }
    if (DAT_TileMapState.currentMapperCommand == M_MAPPER_PLACE_ASSEMBLY_POINTK1) {
      Map::Buildings::BuildingsState::createEntityForAssemblyPointsForActiveTabType
                (&DAT_BuildingsState);
      iVar9 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.DAT_ClickedTileY].
              addXgetTile + DAT_TileMapState.DAT_ClickedTileX;
      iVar2 = Map::Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                        (&DAT_PathFindingState,DAT_GameSynchronyState.currentPlayerSlotID,
                         (int)(short)DAT_TileMapState.PathConnectionLayer
                                     [DAT_ViewportRenderState.translationMatrix
                                      [DAT_GameState.playerDataArray
                                       [DAT_GameSynchronyState.currentPlayerSlotID].campground.
                                       yEntry].addXgetTile +
                                      DAT_GameState.playerDataArray
                                      [DAT_GameSynchronyState.currentPlayerSlotID].campground.xEntry
                                     ],(int)(short)DAT_TileMapState.PathConnectionLayer[iVar9],0);
      bVar11 = DAT_BuildingsState.buildings[(short)DAT_TileMapState.BuildingLayer[iVar9]].
               buildingType == BT_CATHEDRAL;
      if (DAT_MouseState.draggingStopped != FALSE) {
        if (!bVar11 && iVar2 == 0) {
          return;
        }
        DAT_GameSynchronyState.DAT_GameCommandParam0 = 0x28;
        goto LAB_004465a6;
      }
      if (bVar11 || iVar2 != 0) {
        iVar2 = 0xd;
        goto LAB_0044655d;
      }
      goto LAB_00446558;
    }
    if (DAT_TileMapState.currentMapperCommand - M_MAPPER_PEOPLE_ARCHERS < 0x11) {
      Global::PlaceUnit();
      return;
    }
    if (DAT_TileMapState.currentMapperCommand - M_MAPPER_PEOPLE_ARAB_BOW < 8) {
      Global::PlaceUnit();
      return;
    }
    DAT_TileMapState.DAT_ClickedTileX =
         DAT_ViewportRenderState.viewportState.mouseTileX - DAT_TileMapState.DAT_BuildingSize / 2;
    DAT_TileMapState.DAT_ClickedTileY =
         DAT_ViewportRenderState.viewportState.mouseTileY - DAT_TileMapState.DAT_BuildingSize / 2;
    DAT_TileMapState.DAT_TempBuildingRotation = 0;
    MVar10 = DAT_TileMapState.currentMapperCommand;
    if (DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_LANDSCAPING) {
      if (DAT_TileMapState.currentMapperCommand != M_MAPPER_KEEP1) {
        if (DAT_TileMapState.currentMapperCommand != M_MAPPER_KEEP2) {
          if (DAT_TileMapState.currentMapperCommand != M_MAPPER_KEEP3) goto LAB_00445c46;
          if (DAT_GameCore.field106_0x1540 != 0) {
            Map::TileMapState::checkBuildingCanBePlacedHere
                      (&DAT_TileMapState,DAT_GameSynchronyState.currentPlayerSlotID,
                       DAT_TileMapState.DAT_ClickedTileX,DAT_TileMapState.DAT_ClickedTileY,
                       M_MAPPER_KEEP3,DAT_TileMapState.DAT_BuildingSize);
          }
        }
        if (DAT_GameCore.field105_0x153c != 0) {
          Map::TileMapState::checkBuildingCanBePlacedHere
                    (&DAT_TileMapState,DAT_GameSynchronyState.currentPlayerSlotID,
                     DAT_TileMapState.DAT_ClickedTileX,DAT_TileMapState.DAT_ClickedTileY,
                     M_MAPPER_KEEP2,DAT_TileMapState.DAT_BuildingSize);
        }
      }
      if (DAT_GameCore.mapU2MiddleBytes != 0) {
        MVar10 = M_MAPPER_KEEP1;
        goto LAB_00445c46;
      }
    }
    else {
LAB_00445c46:
      Map::TileMapState::checkBuildingCanBePlacedHere
                (&DAT_TileMapState,DAT_GameSynchronyState.currentPlayerSlotID,
                 DAT_TileMapState.DAT_ClickedTileX,DAT_TileMapState.DAT_ClickedTileY,MVar10,
                 DAT_TileMapState.DAT_BuildingSize);
    }
    switch(DAT_TileMapState.currentMapperCommand) {
    case M_MAPPER_FLETCHER:
    case M_MAPPER_BAKER:
    case M_MAPPER_BREWER:
    case M_MAPPER_POLETURNER:
    case M_MAPPER_BLACKSMITH:
    case M_MAPPER_ARMOURER:
    case M_MAPPER_TANNER:
      Map::TileMapState::determineBuildingPlacementRotation
                (DAT_TileMapState.DAT_ClickedTileX,DAT_TileMapState.DAT_ClickedTileY);
      break;
    case M_MAPPER_DRAWBRIDGE:
      Map::TileMapState::checkDrawbridgePlacement
                (&DAT_TileMapState,DAT_TileMapState.DAT_ClickedTileX,
                 DAT_TileMapState.DAT_ClickedTileY);
    }
    uVar8 = DAT_ViewportRenderState.viewportState.mouseTileY;
    uVar4 = DAT_ViewportRenderState.viewportState.mouseTileX;
    MVar10 = DAT_TileMapState.currentMapperCommand;
    if (((DAT_TileMapState.currentMapperCommand == M_MAPPER_MOAT) ||
        (DAT_TileMapState.currentMapperCommand == M_MAPPER_ANTIMOAT)) ||
       ((DAT_TileMapState.currentMapperCommand == M_MAPPER_DUGMOAT ||
        (DAT_TileMapState.currentMapperCommand == M_MAPPER_UNDUGMOAT)))) {
      DAT_TileMapState.editorActiveBrush = 2;
      BVar6 = _HoldStrong::Rendering::ViewportRenderState::xyAreValid
                        (&DAT_ViewportRenderState,DAT_ViewportRenderState.viewportState.mouseTileX,
                         DAT_ViewportRenderState.viewportState.mouseTileY);
      if (BVar6 == FALSE) {
        return;
      }
      iVar2 = DAT_ViewportRenderState.translationMatrix[uVar8].addXgetTile + uVar4;
      if (((MVar10 == M_MAPPER_MOAT) || (MVar10 == M_MAPPER_DUGMOAT)) &&
         (iVar9 = Map::TileMapState::getUnownedMoatCount(&DAT_TileMapState),
         uVar4 = DAT_ViewportRenderState.viewportState.mouseTileX,
         MVar10 = DAT_TileMapState.currentMapperCommand,
         uVar8 = DAT_ViewportRenderState.viewportState.mouseTileY, iVar9 < 0xf)) {
        DAT_TileMapState.buildingPlacementFail = TRUE;
        Map::TileMapState::renderPreviewMapperWithBrush
                  (&DAT_TileMapState,DAT_ViewportRenderState.viewportState.mouseTileX,
                   DAT_ViewportRenderState.viewportState.mouseTileY,
                   DAT_TileMapState.currentMapperCommand);
        BottomLeftTextDisplayState::setBottomLeftTextDisplayText
                  (&DAT_BottomLeftTextDisplayState,1,8,0x14d,(TextMessageBLLookupStructUnion)0x0,100
                   ,6000);
        return;
      }
      if (((DAT_MouseState.leftClickState == FALSE) || (iVar2 == DAT_00b96110)) &&
         (iVar2 = DAT_00b96110, DAT_MouseState.draggingStopped == FALSE)) {
        Map::TileMapState::renderPreviewMapperWithBrush(&DAT_TileMapState,uVar4,uVar8,MVar10);
        return;
      }
      DAT_00b96110 = iVar2;
      BVar6 = Map::Navigation::PathFindingState::isSignPostWithinDistance
                        (&DAT_PathFindingState,uVar4,uVar8,
                         DAT_GameState.mapAndTime.unk_signpostDistance + 5);
      if (BVar6 != FALSE) {
        BottomLeftTextDisplayState::setBottomLeftTextDisplayText
                  (&DAT_BottomLeftTextDisplayState,1,0x4d,0x15,(TextMessageBLLookupStructUnion)0x0,
                   100,6000);
        return;
      }
      if (((DAT_TileMapState.currentMapperCommand == M_MAPPER_MOAT) ||
          (DAT_TileMapState.currentMapperCommand == M_MAPPER_ANTIMOAT)) &&
         (BVar6 = Map::TileMapState::isValidCastleSiteLocation
                            (&DAT_TileMapState,DAT_ViewportRenderState.viewportState.mouseTileX,
                             DAT_ViewportRenderState.viewportState.mouseTileY,
                             DAT_TileMapState.currentMapperCommand), BVar6 == FALSE)) {
        return;
      }
      DVar5 = DAT_00b98450;
      if ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
         (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER)) {
        DVar5 = timeGetTime();
        if (DAT_00b98450 == 0) {
          DVar5 = timeGetTime();
        }
        else if (DVar5 - DAT_00b98450 < 0xc9) {
          return;
        }
      }
      DAT_00b98450 = DVar5;
      DAT_GameSynchronyState.DAT_GameCommandParam0 =
           DAT_ViewportRenderState.viewportState.mouseTileX;
      DAT_GameSynchronyState.DAT_GameCommandParam1 =
           DAT_ViewportRenderState.viewportState.mouseTileY;
      DAT_GameSynchronyState.DAT_GameCommandParam2 = 2;
      DAT_GameSynchronyState.DAT_GameCommandParam3 = 0x40000000;
      if (DAT_TileMapState.currentMapperCommand != M_MAPPER_MOAT) {
        if (DAT_TileMapState.currentMapperCommand == M_MAPPER_ANTIMOAT) {
          DAT_GameSynchronyState.DAT_GameCommandParam4 = 1;
          Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SET_TERRAIN);
          return;
        }
        DAT_GameSynchronyState.DAT_GameCommandParam4 =
             (DAT_TileMapState.currentMapperCommand != M_MAPPER_DUGMOAT) + 2;
        Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SET_TERRAIN);
        return;
      }
      DAT_GameSynchronyState.DAT_GameCommandParam4 = 0;
      Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SET_TERRAIN);
      return;
    }
    if (DAT_TileMapState.currentMapperCommand == M_MAPPER_PITCH_DITCH) {
      iVar2 = Map::TileMapState::countUnownedPitchDitches(&DAT_TileMapState);
      if (iVar2 < 0xf) {
LAB_00445d3d:
        DAT_TileMapState.buildingPlacementFail = TRUE;
        BottomLeftTextDisplayState::setBottomLeftTextDisplayText
                  (&DAT_BottomLeftTextDisplayState,1,8,0x14d,(TextMessageBLLookupStructUnion)0x0,100
                   ,6000);
      }
    }
    else if ((DAT_BuildingsState.unknownCountdown01 < 3) ||
            (((DAT_BuildingsState.unknownCountdown01 < 0xb ||
              (((((DAT_TileMapState.currentMapperCommand != M_MAPPER_CATAPULT &&
                  (DAT_TileMapState.currentMapperCommand != M_MAPPER_TREBUCHET)) &&
                 (DAT_TileMapState.currentMapperCommand != M_MAPPER_SIEGE_TOWER)) &&
                ((DAT_TileMapState.currentMapperCommand != M_MAPPER_BATTERING_RAM &&
                 (DAT_TileMapState.currentMapperCommand != M_MAPPER_PORTABLE_SHIELD)))) &&
               (DAT_TileMapState.currentMapperCommand != M_MAPPER_ARAB_BALLISTA)))) &&
             ((DAT_TileMapState.currentMapperCommand != M_MAPPER_TUNNEL_CONSTRUCTION &&
              (DAT_BuildingsState.unknownCountdown01 < 0x14)))))) goto LAB_00445d3d;
    if (DAT_MouseState.leftClickStart != 0) {
      DAT_00b96110 = 0;
    }
    if (((DAT_MouseState.leftClickState != FALSE) &&
        (DAT_TileMapState.buildingPlacementFail == FALSE)) &&
       (DAT_TileMapState.currentMapperCommand == M_MAPPER_PITCH_DITCH)) {
      DVar5 = DAT_00b98454;
      if ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
         (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER)) {
        DVar5 = timeGetTime();
        if (DAT_00b98454 == 0) {
          DVar5 = timeGetTime();
        }
        else if (DVar5 - DAT_00b98454 < 0xc9) {
          return;
        }
      }
      DAT_00b98454 = DVar5;
      iVar2 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.DAT_ClickedTileY].
              addXgetTile + DAT_TileMapState.DAT_ClickedTileX;
      if (DAT_00b96110 == iVar2) goto LAB_00445e6f;
      if (DAT_00b96110 == 0) {
        Map::WallAndPitchState::resetWallAndPitchState(&DAT_WallAndPitchState);
      }
LAB_00445e0c:
      DAT_00b96110 = iVar2;
      iVar2 = Game::GameStateStructures::checkRequiredResourcesForBuildingOrPlanToBuy
                        (&DAT_GameState,DAT_TileMapState.currentMapperCommand,
                         DAT_GameSynchronyState.currentPlayerSlotID,TRUE);
      if (iVar2 == 0) {
        return;
      }
      DAT_GameSynchronyState.DAT_GameCommandParam0 = DAT_TileMapState.DAT_ClickedTileX;
      DAT_GameSynchronyState.DAT_GameCommandParam1 = DAT_TileMapState.DAT_ClickedTileY;
      DAT_GameSynchronyState.DAT_GameCommandParam2 = DAT_TileMapState.currentMapperCommand;
      DAT_GameSynchronyState.DAT_GameCommandParam3 = DAT_TileMapState.DAT_BuildingSize;
      DAT_GameSynchronyState.DAT_GameCommandParam4 = DAT_TileMapState.field78_0x55488c;
      if ((DAT_TileMapState.currentMapperCommand != M_MAPPER_GATE_MAIN) &&
         (DAT_TileMapState.currentMapperCommand != M_MAPPER_GATE_INNER)) {
        if (DAT_TileMapState.currentMapperCommand == M_MAPPER_GATE_WOOD1A) {
          DAT_GameSynchronyState.DAT_GameCommandParam4 = 0;
        }
        else if (DAT_TileMapState.currentMapperCommand == M_MAPPER_GATE_WOOD1B) {
          DAT_GameSynchronyState.DAT_GameCommandParam4 = 2;
        }
        else if (DAT_TileMapState.currentMapperCommand == M_MAPPER_GATE_WOOD1C) {
          DAT_GameSynchronyState.DAT_GameCommandParam4 = 4;
        }
        else if (DAT_TileMapState.currentMapperCommand == M_MAPPER_GATE_WOOD1D) {
          DAT_GameSynchronyState.DAT_GameCommandParam4 = 6;
        }
        else if (DAT_TileMapState.currentMapperCommand == M_MAPPER_GATE_STONE1B) {
          DAT_GameSynchronyState.DAT_GameCommandParam4 = 0x50;
        }
        else if (DAT_TileMapState.currentMapperCommand == M_MAPPER_GATE_STONE1A) {
          DAT_GameSynchronyState.DAT_GameCommandParam4 = 0x51;
        }
        else if (DAT_TileMapState.currentMapperCommand == M_MAPPER_GATE_STONE2B) {
          DAT_GameSynchronyState.DAT_GameCommandParam4 = 0x50;
        }
        else {
          DAT_GameSynchronyState.DAT_GameCommandParam4 = 0x51;
          if (DAT_TileMapState.currentMapperCommand != M_MAPPER_GATE_STONE2A) {
            DAT_GameSynchronyState.DAT_GameCommandParam4 = DAT_TileMapState.uiBuildingRotation;
          }
        }
      }
      HoveredState::createHoverStateElement
                (&DAT_HoveredState,DAT_TileMapState.DAT_ClickedTileX,
                 DAT_TileMapState.DAT_ClickedTileY,DAT_TileMapState.currentMapperCommand,
                 DAT_TileMapState.DAT_BuildingSize,DAT_GameSynchronyState.DAT_GameCommandParam4);
      DAT_GameSynchronyState.DAT_GameCommandParam5 = DAT_TribesState.DAT_CurrentTribeID;
                    /* called when placing a woodcutter */
      Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_PLACE_BUILDING);
      if (0x144 < (int)DAT_TileMapState.currentMapperCommand) {
        switch(DAT_TileMapState.currentMapperCommand) {
        case M_MAPPER_POND1:
        case M_MAPPER_POND2_SMALL:
        case M_MAPPER_POND3_LARGE1:
        case M_MAPPER_POND4_LARGE2:
        case M_MAPPER_WELL:
          goto switchD_00446116_caseD_145;
        default:
          return;
        case M_MAPPER_ARAB_BALLISTA:
          goto switchD_00446116_caseD_166;
        }
      }
      if (DAT_TileMapState.currentMapperCommand != M_MAPPER_DANCING_BEAR) {
        if (0xc2 < (int)DAT_TileMapState.currentMapperCommand) {
          switch(DAT_TileMapState.currentMapperCommand) {
          case M_MAPPER_CESS_PIT1:
          case M_MAPPER_CESS_PIT2:
          case M_MAPPER_CESS_PIT3:
          case M_MAPPER_CESS_PIT4:
          case M_MAPPER_BURNING_STAKE:
          case M_MAPPER_GIBBET:
          case M_MAPPER_DUNGEON:
          case M_MAPPER_RACK_STRETCHING:
          case M_MAPPER_CHOPPING_BLOCK:
          case M_MAPPER_DUNKING_STOOL:
switchD_004460d6_caseD_12d:
            Helpers::SetTaxesSetting_unknown(3);
            return;
          default:
            return;
          case M_MAPPER_STATUE1:
          case M_MAPPER_STATUE2:
          case M_MAPPER_STATUE3:
          case M_MAPPER_STATUE4:
          case M_MAPPER_STATUE5:
          case M_MAPPER_SHRINE1:
          case M_MAPPER_SHRINE2:
          case M_MAPPER_SHRINE3:
          case M_MAPPER_SHRINE4:
          case M_MAPPER_SHRINE5:
            goto switchD_00446116_caseD_145;
          }
        }
        if ((int)DAT_TileMapState.currentMapperCommand < 0xbe) {
          switch(DAT_TileMapState.currentMapperCommand) {
          case M_MAPPER_TUNNEL_CONSTRUCTION:
            goto switchD_004460ba_caseD_42;
          default:
            return;
          case M_MAPPER_GARDEN1:
          case M_MAPPER_GARDEN2:
          case M_MAPPER_GARDEN3:
          case M_MAPPER_GARDEN4:
          case M_MAPPER_GARDEN5:
          case M_MAPPER_GARDEN6:
          case M_MAPPER_GARDEN7:
          case M_MAPPER_GARDEN8:
          case M_MAPPER_GARDEN9:
          case M_MAPPER_GARDEN10:
          case M_MAPPER_GARDEN11:
          case M_MAPPER_GARDEN12:
          case M_MAPPER_MAYPOLE:
            goto switchD_00446116_caseD_145;
          case M_MAPPER_GALLOWS:
          case M_MAPPER_STOCKS:
            goto switchD_004460d6_caseD_12d;
          }
        }
switchD_00446116_caseD_166:
        Audio::SFX::SFXState::playUnitSpeechEffect(&DAT_SFXState,0x15);
switchD_004460ba_caseD_42:
        DAT_TileMapState.currentMapperCommand = M_MAPPER_NULL;
        return;
      }
switchD_00446116_caseD_145:
      Helpers::SetTaxesSetting_unknown(2);
      return;
    }
LAB_00445e6f:
    if (DAT_MouseState.draggingStopped != FALSE) {
      iVar2 = DAT_00b96110;
      if (DAT_TileMapState.buildingPlacementFail != FALSE) {
        if (DAT_TileMapState.buildingPlacementFailReason == 1000) {
                    /* added by script: "Too many dog cages" */
          BottomLeftTextDisplayState::setBottomLeftTextDisplayText
                    (&DAT_BottomLeftTextDisplayState,1,0x101,2,(TextMessageBLLookupStructUnion)0x0,
                     100,6000);
          return;
        }
        if (DAT_TileMapState.buildingPlacementFailReason != BFRE_DEFAULT_CANT_PLACE_THAT_THERE) {
          BottomLeftTextDisplayState::setBottomLeftTextDisplayText
                    (&DAT_BottomLeftTextDisplayState,1,0x4d,
                     DAT_TileMapState.buildingPlacementFailReason,
                     (TextMessageBLLookupStructUnion)0x0,100,6000);
          Global::PlayPlacementWarning(DAT_TileMapState.buildingPlacementFailReason);
          return;
        }
        if (DAT_TileMapState.placementWarning != 0) {
          Global::PlayPlacementWarning
                    (BFRE_DEFAULT_CANT_PLACE_THAT_THERE1 - DAT_TileMapState.placementWarning);
          return;
        }
        if ((DAT_TileMapState.currentMapperCommand == M_MAPPER_PITCH_DITCH) && (DAT_00b96110 != 0))
        {
          return;
        }
        Global::PlayPlacementWarning(BFRE_DEFAULT_CANT_PLACE_THAT_THERE1);
        return;
      }
      goto LAB_00445e0c;
    }
    if (((int)DAT_TileMapState.currentMapperCommand < 0xbe) ||
       (((0xc2 < (int)DAT_TileMapState.currentMapperCommand &&
         (DAT_TileMapState.currentMapperCommand != M_MAPPER_ARAB_BALLISTA)) ||
        (DAT_TileMapState.buildingPlacementFail != FALSE)))) {
                    /* special check for some types? */
      Map::TileMapState::setConstructionGFXLayerBasedOnPlacementChecks
                (&DAT_TileMapState,DAT_TileMapState.DAT_ClickedTileX,
                 DAT_TileMapState.DAT_ClickedTileY,DAT_TileMapState.currentMapperCommand,
                 DAT_TileMapState.DAT_BuildingSize);
      return;
    }
                    /* Do for the 5 siege engines */
    iVar9 = 0;
    iVar2 = 0;
    uVar4 = DAT_TileMapState.DAT_ClickedTileY;
    uVar8 = DAT_TileMapState.DAT_ClickedTileX;
    switch(DAT_TileMapState.mapOrientation) {
    case 0:
      iVar9 = 0xd;
      uVar8 = DAT_TileMapState.DAT_ClickedTileX + 1;
      uVar4 = DAT_TileMapState.DAT_ClickedTileY + 1;
      iVar2 = 2;
      break;
    case 2:
      iVar9 = 0x2d;
      uVar8 = DAT_TileMapState.DAT_ClickedTileX - 1;
      uVar4 = DAT_TileMapState.DAT_ClickedTileY + 1;
      iVar2 = -0xe;
      break;
    case 4:
      iVar9 = 0xd;
      uVar8 = DAT_TileMapState.DAT_ClickedTileX - 1;
      iVar2 = -0x1e;
      goto LAB_00445eed;
    case 6:
      iVar9 = -0x13;
      uVar8 = DAT_TileMapState.DAT_ClickedTileX + 1;
      iVar2 = -0xc;
LAB_00445eed:
      uVar4 = DAT_TileMapState.DAT_ClickedTileY - 1;
    }
    _HoldStrong::Rendering::ViewportRenderState::createFloatingLayerElement
              (&DAT_ViewportRenderState,GID_BODY_TENT,1,iVar9,iVar2,
               DAT_ViewportRenderState.translationMatrix[uVar4].addXgetTile + uVar8,5);
    return;
  }
  iVar2 = DAT_ViewportRenderState.translationMatrix
          [DAT_ViewportRenderState.viewportState.mouseTileY].addXgetTile +
          DAT_ViewportRenderState.viewportState.mouseTileX;
  imageY = local_4;
  imageX = local_4;
  switch(DAT_TileMapState.currentMapperCommand) {
  case M_MAPPER_FLAG_TYPE0:
    local_8 = 9;
    imageY = GID_TILE_BUILDINGS_2;
    imageX = GID_TILE_GOODS;
    break;
  case M_MAPPER_FLAG_TYPE1:
    local_8 = 0x29;
    imageY = ~GID_TILE_NULL_1;
    imageX = GID_TILE_GOODS;
    break;
  case M_MAPPER_FLAG_TYPE2:
    local_8 = 0x49;
    imageY = GID_TILE_BUILDINGS_1;
    imageX = GID_TILE_BUILDINGS_1;
    break;
  case M_MAPPER_FLAG_TYPE3:
    local_8 = 1;
    imageY = GID_TILE_BUILDINGS_2;
    imageX = GID_TILE_BUILDINGS_1;
  }
  if (DAT_MouseState.draggingStopped == FALSE) {
    local_4 = GID_ANIM_FLAGS;
    if (DAT_TileMapState.currentMapperCommand == M_MAPPER_FLAG_TYPE3) {
      local_4 = GID_ANIM_CRUSADER_FLAG;
    }
    iVar9 = Map::TileMapState::getTotalHeightAt
                      (&DAT_TileMapState,iVar2,DAT_GameSynchronyState.currentPlayerSlotID);
    if ((-1 < iVar9) && ((DAT_TileMapState.MiscDisplayLayer[iVar2] & 0x1000) == 0)) {
      _HoldStrong::Rendering::ViewportRenderState::createFloatingLayerElement
                (&DAT_ViewportRenderState,local_4,local_8,imageX,imageY,iVar2,0xd);
      return;
    }
    _HoldStrong::Rendering::ViewportRenderState::createFloatingLayerElement
              (&DAT_ViewportRenderState,local_4,local_8,imageX,imageY,iVar2,0x18000d);
    return;
  }
  GVar7 = Map::TileMapState::getTotalHeightAt
                    (&DAT_TileMapState,iVar2,DAT_GameSynchronyState.currentPlayerSlotID);
  if ((int)GVar7 < 0) {
    return;
  }
  if ((DAT_TileMapState.MiscDisplayLayer[iVar2] & 0x1000) != 0) {
    return;
  }
  local_4 = GVar7;
  switch(DAT_TileMapState.currentMapperCommand) {
  case M_MAPPER_FLAG_TYPE0:
    GVar7 = GID_TILE_WALLS;
    break;
  case M_MAPPER_FLAG_TYPE1:
    imageY = DAT_TileMapState.DAT_ClickedTileY * 8;
    imageX = DAT_TileMapState.DAT_ClickedTileX * 8;
    Audio::SFX::SFXState::playSFXAtLocation
              (&DAT_SFXState,DAT_TileMapState.DAT_ClickedTileX,DAT_TileMapState.DAT_ClickedTileY,
               FX_LARGE_FLAG);
    GVar7 = GID_TILE_NULL_11;
    goto switchD_004466e9_caseD_4;
  case M_MAPPER_FLAG_TYPE2:
    GVar7 = GID_TILE_LAND_3;
    break;
  case M_MAPPER_FLAG_TYPE3:
    GVar7 = GID_TILE_NULL_13;
    break;
  default:
    goto switchD_004466e9_caseD_4;
  }
  imageY = DAT_TileMapState.DAT_ClickedTileY * 8;
  imageX = DAT_TileMapState.DAT_ClickedTileX * 8;
  Audio::SFX::SFXState::playSFXAtLocation
            (&DAT_SFXState,DAT_TileMapState.DAT_ClickedTileX,DAT_TileMapState.DAT_ClickedTileY,
             FX_SMALL_FLAG);
switchD_004466e9_caseD_4:
  HoveredState::createHoverStateElement
            (&DAT_HoveredState,DAT_TileMapState.DAT_ClickedTileX,DAT_TileMapState.DAT_ClickedTileY,
             DAT_TileMapState.currentMapperCommand,DAT_TileMapState.DAT_BuildingSize,0);
  DAT_GameSynchronyState.DAT_GameCommandParam3 = local_4;
  DAT_GameSynchronyState.DAT_GameCommandParam5 = DAT_GameSynchronyState.currentPlayerSlotID;
  DAT_GameSynchronyState.DAT_GameCommandParam4 = GVar7;
LAB_004467a9:
  DAT_GameSynchronyState.DAT_GameCommandParam0 = DAT_GameSynchronyState.currentPlayerSlotID;
  DAT_GameSynchronyState.DAT_GameCommandParam1 = imageX;
  DAT_GameSynchronyState.DAT_GameCommandParam2 = imageY;
  Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SPAWN_ENTITY);
  return;
}



// ================= ClickPlaceBuilding @ 0x00481d90 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Commands::ClickPlaceBuilding(void)

{
  int iVar1;
  
  DAT_GameSynchronyState.DAT_CommandSize = 10;
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_SCHEDULE_AND_SEND) {
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam1,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam2,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam3,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam4,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam5,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    return;
  }
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_EXECUTE) {
    DAT_GameSynchronyState.DAT_GameCommandParam0 = 0;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    DAT_GameSynchronyState.DAT_GameCommandParam1 = 0;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam1,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    DAT_GameSynchronyState.DAT_GameCommandParam2 = M_MAPPER_NULL;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam2,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    DAT_GameSynchronyState.DAT_GameCommandParam3 = 0;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam3,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    DAT_GameSynchronyState.DAT_GameCommandParam4 = 0;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam4,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    DAT_GameSynchronyState.DAT_GameCommandParam5 = 0;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam5,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    if ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
       (iVar1 = Game::GameStateStructures::checkRequiredResourcesForBuildingOrPlanToBuy
                          (&DAT_GameState,DAT_GameSynchronyState.DAT_GameCommandParam2,
                           DAT_GameSynchronyState.protocolInvokerPlayerID,FALSE), iVar1 == 0)) {
      return;
    }
    DAT_BuildingsState.DAT_DraggedTileCountVerified = DAT_GameSynchronyState.DAT_GameCommandParam5;
    iVar1 = DAT_GameSynchronyState.field302_0x109e7c;
    if (DAT_GameCore.currentMenuViewType != MVT_MAP_EDITOR_LANDSCAPING) {
      iVar1 = DAT_GameSynchronyState.protocolInvokerPlayerID;
    }
    Map::TileMapState::placeBuilding
              (&DAT_TileMapState,iVar1,DAT_GameSynchronyState.DAT_GameCommandParam0,
               DAT_GameSynchronyState.DAT_GameCommandParam1,
               DAT_GameSynchronyState.DAT_GameCommandParam2 & 0xffff,
               DAT_GameSynchronyState.DAT_GameCommandParam3,
               DAT_GameSynchronyState.DAT_GameCommandParam4);
  }
  return;
}



// ================= ProcessRecruitUnit @ 0x00464ef0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::Global::ProcessRecruitUnit(int playerID,int unitType,undefined4 recruitmentBuildingID)

{
  if (DAT_GameState.playerDataArray[playerID].count_2 +
      DAT_GameState.playerDataArray[playerID].armySize < DAT_GameState.mapAndTime.armySizeLimit) {
    if (unitType == 0x1e) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_E_ENGINEER,
                 DAT_GameState.playerDataArray[playerID].engineersGuild.id,playerID,0);
      return;
    }
    if (unitType == 5) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_TUNNELER,
                 DAT_GameState.playerDataArray[playerID].tunnelersGuild.id,playerID,0);
      return;
    }
    if (unitType == 0x1d) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_E_LADDER,
                 DAT_GameState.playerDataArray[playerID].engineersGuild.id,playerID,0);
      return;
    }
    if (unitType == 0x25) {
                    /* monk */
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_E_MONK,recruitmentBuildingID,playerID,0);
      return;
    }
    if (unitType == 0x46) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_ARCHER,
                 DAT_GameState.playerDataArray[playerID].mercenaryPost.id,playerID,0);
      return;
    }
    if (unitType == 0x47) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_SLAVE,DAT_GameState.playerDataArray[playerID].mercenaryPost.id
                 ,playerID,0);
      return;
    }
    if (unitType == 0x48) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_SLINGER,
                 DAT_GameState.playerDataArray[playerID].mercenaryPost.id,playerID,0);
      return;
    }
    if (unitType == 0x49) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_ASSASSIN,
                 DAT_GameState.playerDataArray[playerID].mercenaryPost.id,playerID,0);
      return;
    }
    if (unitType == 0x4a) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_HARCHER,
                 DAT_GameState.playerDataArray[playerID].mercenaryPost.id,playerID,0);
      return;
    }
    if (unitType == 0x4b) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_SWORDSMAN,
                 DAT_GameState.playerDataArray[playerID].mercenaryPost.id,playerID,0);
      return;
    }
    if (unitType == 0x4c) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_FIRETHROWER,
                 DAT_GameState.playerDataArray[playerID].mercenaryPost.id,playerID,0);
      return;
    }
    Map::Units::UnitsState::euroRecruit
              (&DAT_UnitsState,unitType,DAT_GameState.playerDataArray[playerID].barracks.id,playerID
               ,0);
  }
  return;
}



