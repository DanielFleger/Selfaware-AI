// ================= placeWorkshopOrHovel @ 00506bd0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::placeWorkshopOrHovel
          (TileMapState *this,int playerID,uint x,uint y,BuildingType type,uint size,int orientation
          ,undefined4 averageHeight)

{
  int buildingID;
  int iVar1;
  TileMapState *this_00;
  int iVar2;
  
  iVar2 = 0;
  buildingID = Buildings::BuildingsState::setupBuildingData
                         (&DAT_BuildingsState,playerID,x,y,averageHeight,
                          (int)(short)(undefined2)type,size,playerID,orientation);
  *(short *)&DAT_BuildingsState.buildings[buildingID].hovelVisualStyle =
       (short)DAT_GameState.playerDataArray[playerID].hovelCountUpToEight;
  DAT_TileMapState.placedBuildingID = buildingID;
  if ((undefined2)type == BT_HOVEL) {
                    /* hovel */
    DAT_GameState.playerDataArray[playerID].hovelCountUpToEight =
         (DAT_GameState.playerDataArray[playerID].hovelCountUpToEight + 1) % 7;
  }
  do {
    getBuildingSizeIndexMappingData(iVar2,size);
    iVar1 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + y].addXgetTile +
            DAT_TileMapState.buildingX + x;
    if (iVar2 < 0x24) {
                    /* set tileref */
      *(int *)(DAT_BuildingsState.buildings[buildingID].workers + iVar2 * 2 + 8) = iVar1;
    }
    DAT_TileMapState.HeightLayer[iVar1] = (byte)averageHeight;
    DAT_TileMapState.LogicLayer[iVar1] = DAT_TileMapState.LogicLayer[iVar1] | 0x400;
    DAT_TileMapState.BuildingLayer[iVar1] = (ushort)buildingID;
    iVar2 = iVar2 + 1;
    DAT_TileMapState.BuildingWasLayer[iVar1] = (undefined1)type;
    DAT_TileMapState.ChangedLayer[iVar1] = 2;
  } while (iVar2 < DAT_TileMapState.constructionTileCount);
  setMiscDisplayLayer(buildingID);
  updatePathLinkagesForBuilding(this_00,buildingID);
  if (((playerID == DAT_GameSynchronyState.currentPlayerSlotID) &&
      (DAT_GameState.playerDataArray[playerID].availablePeasantsAtFire <
       (int)DAT_BuildingsState.buildings[buildingID].buildingTypeBasedEmployeeCount)) &&
     ((DAT_GameState.playerDataArray[playerID].populationCap <=
       DAT_GameState.playerDataArray[playerID].currentPopulation ||
      (DAT_GameState.playerDataArray[playerID].popularity < 5000)))) {
    UI::BottomLeftTextDisplayState::setBottomLeftTextDisplayText
              (&DAT_BottomLeftTextDisplayState,1,0x4d,1,(TextMessageBLLookupStructUnion)0x0,100,6000
              );
  }
  return;
}



// ================= updateWalkAndPathLayer @ 0049aad0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Navigation::PathFindingState::updateWalkAndPathLayer
          (PathFindingState *this,int param_1,uint xPosition,uint yPosition)

{
  short sVar1;
  short sVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  short *psVar6;
  int *piVar7;
  int iVar8;
  
  if (((xPosition < 400) && (yPosition < 400)) &&
     (*(char *)(yPosition * 400 + 0x21aec98 + xPosition) != '\0')) {
    DAT_PathFindingState.searchGeneration = DAT_PathFindingState.searchGeneration + 1;
    if (32000 < DAT_PathFindingState.searchGeneration) {
      DAT_PathFindingState.searchGeneration = 1;
      IO::LowLevelMemory::fillMemory_ByteValue
                (&DAT_LowLevelMemory,0x27420,'\0',DAT_TileMapState.WalkLayer);
    }
    DAT_PathFindingState.searchQueue.readIndex = 0;
    DAT_PathFindingState.searchQueue.writeIndex = 1;
    DAT_PathFindingState.searchQueue.currentDistance = 1;
    DAT_PathFindingState.searchQueue.yQueue[0] = (short)yPosition;
    DAT_PathFindingState.searchQueue.xQueue[0] = (short)xPosition;
    DAT_PathFindingState.searchQueue.tilesQueue[0] =
         DAT_ViewportRenderState.translationMatrix[yPosition].addXgetTile + xPosition;
    DAT_TileMapState.CertainPathLayer[DAT_PathFindingState.searchQueue.tilesQueue[0]] = 1;
    DAT_TileMapState.WalkLayer[DAT_PathFindingState.searchQueue.tilesQueue[0]] =
         (short)DAT_PathFindingState.searchGeneration;
    if (DAT_PathFindingState.searchQueue.readIndex != DAT_PathFindingState.searchQueue.writeIndex) {
      do {
        uVar3 = DAT_PathFindingState.searchQueue.tilesQueue
                [DAT_PathFindingState.searchQueue.readIndex];
        if (0x13a0f < uVar3) break;
        sVar1 = DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.readIndex];
        iVar8 = (int)sVar1;
        sVar2 = DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.readIndex];
        if (iVar8 < DAT_PathFindingState.mappingYRelated) {
          DAT_PathFindingState.mappingYRelated = iVar8;
        }
        if (DAT_PathFindingState.yLimit < iVar8) {
          DAT_PathFindingState.yLimit = iVar8;
        }
        iVar4 = (int)sVar2 / 10;
        iVar5 = iVar8 / 10;
        *(undefined1 *)(iVar4 + 0x1f93438 + iVar5 * 0x28) = 2;
        if (iVar4 < DAT_TileMapState.someYLike) {
          DAT_TileMapState.someYLike = iVar4;
        }
        if (DAT_TileMapState.someYLikeLimit < iVar4) {
          DAT_TileMapState.someYLikeLimit = iVar4;
        }
        if (iVar5 < DAT_TileMapState.someIndex) {
          DAT_TileMapState.someIndex = iVar5;
        }
        if (DAT_TileMapState.someLimit < iVar5) {
          DAT_TileMapState.someLimit = iVar5;
        }
        DAT_PathFindingState.searchQueue.currentDistance =
             (int)DAT_TileMapState.CertainPathLayer[uVar3];
        if (param_1 < DAT_PathFindingState.searchQueue.currentDistance) break;
        piVar7 = DAT_TileMapState.directionTranslationMatrix[iVar8] + 1;
        DAT_TileMapState.ChangedLayer[uVar3] = 2;
        psVar6 = &DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[0].short.yOffset;
        do {
          iVar8 = (*(int (*) [8])(piVar7 + -1))[0] + uVar3;
          if ((DAT_TileMapState.WalkLayer[iVar8] != DAT_PathFindingState.searchGeneration) &&
             ((DAT_TileMapState.LogicLayer[iVar8] & 0x30) == 0)) {
            DAT_TileMapState.CertainPathLayer[iVar8] =
                 (short)DAT_PathFindingState.searchQueue.currentDistance + 1;
            DAT_TileMapState.WalkLayer[iVar8] = (short)DAT_PathFindingState.searchGeneration;
            DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 ((Point8ShortXY *)(psVar6 + -2))->xOffset + sVar2;
            DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 *psVar6 + sVar1;
            DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.writeIndex]
                 = iVar8;
            DAT_PathFindingState.searchQueue.writeIndex =
                 DAT_PathFindingState.searchQueue.writeIndex + 1;
            if (0x13a0f < DAT_PathFindingState.searchQueue.writeIndex) {
              DAT_PathFindingState.searchQueue.writeIndex = 0;
            }
          }
          iVar8 = *piVar7 + uVar3;
          if ((DAT_TileMapState.WalkLayer[iVar8] != DAT_PathFindingState.searchGeneration) &&
             ((DAT_TileMapState.LogicLayer[iVar8] & 0x30) == 0)) {
            DAT_TileMapState.CertainPathLayer[iVar8] =
                 (short)DAT_PathFindingState.searchQueue.currentDistance + 1;
            DAT_TileMapState.WalkLayer[iVar8] = (short)DAT_PathFindingState.searchGeneration;
            DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 psVar6[2] + sVar2;
            DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 psVar6[4] + sVar1;
            DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.writeIndex]
                 = iVar8;
            DAT_PathFindingState.searchQueue.writeIndex =
                 DAT_PathFindingState.searchQueue.writeIndex + 1;
            if (0x13a0f < DAT_PathFindingState.searchQueue.writeIndex) {
              DAT_PathFindingState.searchQueue.writeIndex = 0;
            }
          }
          iVar8 = piVar7[1] + uVar3;
          if ((DAT_TileMapState.WalkLayer[iVar8] != DAT_PathFindingState.searchGeneration) &&
             ((DAT_TileMapState.LogicLayer[iVar8] & 0x30) == 0)) {
            DAT_TileMapState.CertainPathLayer[iVar8] =
                 (short)DAT_PathFindingState.searchQueue.currentDistance + 1;
            DAT_TileMapState.WalkLayer[iVar8] = (short)DAT_PathFindingState.searchGeneration;
            DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 psVar6[6] + sVar2;
            DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 psVar6[8] + sVar1;
            DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.writeIndex]
                 = iVar8;
            DAT_PathFindingState.searchQueue.writeIndex =
                 DAT_PathFindingState.searchQueue.writeIndex + 1;
            if (0x13a0f < DAT_PathFindingState.searchQueue.writeIndex) {
              DAT_PathFindingState.searchQueue.writeIndex = 0;
            }
          }
          iVar8 = piVar7[2] + uVar3;
          if ((DAT_TileMapState.WalkLayer[iVar8] != DAT_PathFindingState.searchGeneration) &&
             ((DAT_TileMapState.LogicLayer[iVar8] & 0x30) == 0)) {
            DAT_TileMapState.CertainPathLayer[iVar8] =
                 (short)DAT_PathFindingState.searchQueue.currentDistance + 1;
            DAT_TileMapState.WalkLayer[iVar8] = (short)DAT_PathFindingState.searchGeneration;
            DAT_PathFindingState.searchQueue.xQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 psVar6[10] + sVar2;
            DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.writeIndex] =
                 psVar6[0xc] + sVar1;
            DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.writeIndex]
                 = iVar8;
            DAT_PathFindingState.searchQueue.writeIndex =
                 DAT_PathFindingState.searchQueue.writeIndex + 1;
            if (0x13a0f < DAT_PathFindingState.searchQueue.writeIndex) {
              DAT_PathFindingState.searchQueue.writeIndex = 0;
            }
          }
          piVar7 = piVar7 + 4;
          psVar6 = psVar6 + 0x10;
        } while ((int)psVar6 < 0xb4908c);
        DAT_PathFindingState.searchQueue.readIndex = DAT_PathFindingState.searchQueue.readIndex + 1;
        if (0x13a0f < DAT_PathFindingState.searchQueue.readIndex) {
          DAT_PathFindingState.searchQueue.readIndex = 0;
        }
      } while (DAT_PathFindingState.searchQueue.readIndex !=
               DAT_PathFindingState.searchQueue.writeIndex);
    }
    DAT_TileMapState.forceUpdateLogicalAndMiscDisplayLayers = 1;
    DAT_TileMapState.forceUpdateTextureTilemap = 1;
    DAT_TileMapState.forceUpdateGFXLayers = 1;
  }
  return;
}



// ================= stampBuildingOntoTileMap @ 00507060 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::stampBuildingOntoTileMap
          (TileMapState *this,int param_1,uint param_2,uint param_3,undefined4 param_4,
          undefined4 param_5,uint param_6,undefined4 param_7,undefined4 param_8)

{
  int buildingID;
  int iVar1;
  TileMapState *this_00;
  int iVar2;
  
  iVar2 = 0;
  buildingID = Buildings::BuildingsState::setupBuildingData
                         (&DAT_BuildingsState,param_1,param_2,param_3,param_8,(int)(short)param_4,
                          param_6,param_1,(int)(short)param_5);
  DAT_TileMapState.placedBuildingID = buildingID;
  do {
    getBuildingSizeIndexMappingData(iVar2,param_6);
    iVar1 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + param_3].
            addXgetTile + DAT_TileMapState.buildingX + param_2;
    if (iVar2 < 0x24) {
      *(int *)(DAT_BuildingsState.buildings[buildingID].workers + iVar2 * 2 + 8) = iVar1;
    }
    DAT_TileMapState.HeightLayer[iVar1] = (byte)param_8;
    DAT_TileMapState.LogicLayer[iVar1] = DAT_TileMapState.LogicLayer[iVar1] | 0x400;
    DAT_TileMapState.BuildingLayer[iVar1] = (ushort)buildingID;
    iVar2 = iVar2 + 1;
    DAT_TileMapState.ChangedLayer[iVar1] = 2;
  } while (iVar2 < DAT_TileMapState.constructionTileCount);
  setMiscDisplayLayer(buildingID);
  updatePathLinkagesForBuilding(this_00,buildingID);
  return;
}



// ================= placeStockpile @ 00508540 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::placeStockpile
          (TileMapState *this,int playerID,int x,int y,undefined4 buildingType,undefined4 param_5,
          int variation,int averageHeight)

{
  short sVar1;
  byte bVar2;
  int buildingID;
  int iVar3;
  int iVar4;
  byte bVar5;
  int iVar6;
  XYPair *pXVar7;
  
  iVar4 = DAT_GameCore.uniqueGameObjectTracker;
  bVar2 = (char)averageHeight + 10;
  bVar5 = (char)playerID - 1;
  sVar1 = 0;
                    /* building parts */
  pXVar7 = DAT_TerrainDefinedData.DAT_Stockpile_BuildingPartsOffsets;
  do {
    buildingID = Buildings::BuildingsState::setupBuildingData
                           (&DAT_BuildingsState,playerID,pXVar7->x + x,pXVar7->y + y,
                            averageHeight + 10,(int)(short)buildingType,2,playerID,variation);
    DAT_BuildingsState.buildings[buildingID].uidWhenPlaced = iVar4;
    DAT_BuildingsState.buildings[buildingID].field148_0x190 = sVar1 + 1;
    iVar6 = 0;
    do {
      getBuildingSizeIndexMappingData(iVar6,2);
      iVar6 = iVar6 + 1;
      iVar3 = DAT_ViewportRenderState.translationMatrix[pXVar7->y + DAT_TileMapState.buildingY + y].
              addXgetTile + pXVar7->x + x + DAT_TileMapState.buildingX;
      DAT_TileMapState.HeightLayer[iVar3] = bVar2;
                    /* Not walkable */
      DAT_TileMapState.LogicLayer[iVar3] = DAT_TileMapState.LogicLayer[iVar3] | 0x502;
      DAT_TileMapState.WallOwnerLayer[iVar3] = DAT_TileMapState.WallOwnerLayer[iVar3] & 0xf8 | bVar5
      ;
      DAT_TileMapState.BuildingLayer[iVar3] = (ushort)buildingID;
      DAT_TileMapState.BuildingWasLayer[iVar3] = (uchar)buildingType;
      DAT_TileMapState.ChangedLayer[iVar3] = 2;
    } while (iVar6 < DAT_TileMapState.constructionTileCount);
    updatePathLinkagesForBuilding(&DAT_TileMapState,buildingID);
    sVar1 = sVar1 + 1;
    pXVar7 = pXVar7 + 1;
  } while ((int)pXVar7 < 0xb49130);
                    /* Pathable parts */
  pXVar7 = DAT_TerrainDefinedData.StockpilePathableOffsets;
  DAT_TileMapState.placedBuildingID = buildingID;
  do {
    iVar4 = DAT_ViewportRenderState.translationMatrix[pXVar7->y + y].addXgetTile + pXVar7->x + x;
                    /* increment array pointer */
    pXVar7 = pXVar7 + 1;
                    /* Walkable */
    DAT_TileMapState.LogicLayer[iVar4] = DAT_TileMapState.LogicLayer[iVar4] | 0x102;
    DAT_TileMapState.HeightLayer[iVar4] = bVar2;
    DAT_TileMapState.AlphaGFXLayer[iVar4] = (ushort)buildingID;
    DAT_TileMapState.BuildingWasLayer[iVar4] = (uchar)buildingType;
    DAT_TileMapState.WallOwnerLayer[iVar4] = DAT_TileMapState.WallOwnerLayer[iVar4] & 0xf8 | bVar5;
    DAT_TileMapState.ChangedLayer[iVar4] = 2;
  } while ((int)pXVar7 < 0xb49178);
  if (((playerID == DAT_GameSynchronyState.currentPlayerSlotID) &&
      (DAT_GameState.playerDataArray[playerID].availablePeasantsAtFire <
       (int)DAT_BuildingsState.buildings[buildingID].buildingTypeBasedEmployeeCount)) &&
     ((DAT_GameState.playerDataArray[playerID].populationCap <=
       DAT_GameState.playerDataArray[playerID].currentPopulation ||
      (DAT_GameState.playerDataArray[playerID].popularity < 5000)))) {
    UI::BottomLeftTextDisplayState::setBottomLeftTextDisplayText
              (&DAT_BottomLeftTextDisplayState,1,0x4d,1,(TextMessageBLLookupStructUnion)0x0,100,6000
              );
  }
  return;
}



// ================= placeBarracks @ 005076a0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::placeBarracks
          (TileMapState *this,int playerID,uint xPosition,int *yPosition_param,
          undefined4 buildingType,uint buildingSize,int buildingOrientation,undefined4 param_7)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  TileMapState *this_00;
  TileMapState *this_01;
  TileMapState *this_02;
  TileMapState *this_03;
  TileMapState *this_04;
  uint uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int local_c;
  
  piVar1 = yPosition_param;
  iVar8 = DAT_GameCore.uniqueGameObjectTracker;
  iVar6 = 0;
  if (buildingOrientation == 0xf) {
    local_c = 0;
  }
  else {
    local_c = buildingOrientation / 2;
  }
  iVar2 = Buildings::BuildingsState::setupBuildingData
                    (&DAT_BuildingsState,playerID,xPosition,(uint)yPosition_param,param_7,
                     (int)(short)buildingType,buildingSize,playerID,0xf);
  iVar3 = (int)(short)(ushort)iVar2;
  DAT_TileMapState.placedBuildingID = iVar3;
  DAT_BuildingsState.buildings[iVar3].uidWhenPlaced = iVar8;
  yPosition_param = &DAT_BuildingsState.buildings[iVar3].tileRef1;
  do {
    getBuildingSizeIndexMappingData(iVar6,buildingSize);
    iVar4 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + (int)piVar1].
            addXgetTile + DAT_TileMapState.buildingX + xPosition;
    *yPosition_param = iVar4;
    DAT_TileMapState.HeightLayer[iVar4] = (byte)param_7;
    DAT_TileMapState.LogicLayer[iVar4] = DAT_TileMapState.LogicLayer[iVar4] | 0x400;
    DAT_TileMapState.BuildingLayer[iVar4] = (ushort)iVar2;
    iVar6 = iVar6 + 1;
    yPosition_param = yPosition_param + 1;
    DAT_TileMapState.BuildingWasLayer[iVar4] = (uchar)buildingType;
    DAT_TileMapState.ChangedLayer[iVar4] = 2;
  } while (iVar6 < DAT_TileMapState.constructionTileCount);
  setMiscDisplayLayer(iVar3);
  updatePathLinkagesForBuilding(this_00,iVar3);
  uVar7 = (int)piVar1 + DAT_TerrainDefinedData.BuildingPartsOffsets[local_c][0].y;
  uVar5 = xPosition + DAT_TerrainDefinedData.BuildingPartsOffsets[local_c][0].x;
  iVar6 = Buildings::BuildingsState::setupBuildingData
                    (&DAT_BuildingsState,playerID,uVar5,uVar7,param_7,BT_PARADEGROUND3,5,playerID,
                     0xf);
  iVar2 = (int)(short)(ushort)iVar6;
  DAT_BuildingsState.buildings[iVar2].uidWhenPlaced = iVar8;
  DAT_BuildingsState.buildings[iVar2].quarryStockpileID =
       (undefined2)DAT_TileMapState.placedBuildingID;
  buildingSize = 0;
  do {
    getBuildingSizeIndexMappingData(buildingSize,DAT_BuildingsState.buildings[iVar2].widthOrHeight);
    iVar3 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + uVar7].
            addXgetTile + DAT_TileMapState.buildingX + uVar5;
    resetTileAndClearMoat(&DAT_TileMapState,iVar3);
    DAT_TileMapState.HeightLayer[iVar3] = (byte)param_7;
    if ((DAT_TileMapState.buildingX == 2) && (DAT_TileMapState.buildingY == 2)) {
      DAT_TileMapState.LogicLayer[iVar3] = DAT_TileMapState.LogicLayer[iVar3] | 0x400;
    }
    DAT_TileMapState.BuildingLayer[iVar3] = (ushort)iVar6;
    buildingSize = buildingSize + 1;
    DAT_TileMapState.BuildingWasLayer[iVar3] = (uchar)buildingType;
    DAT_TileMapState.ChangedLayer[iVar3] = 2;
  } while ((int)buildingSize < DAT_TileMapState.constructionTileCount);
  setMiscDisplayLayer(iVar2);
  updatePathLinkagesForBuilding(this_01,iVar2);
  Navigation::PathFindingState::updateWalkAndPathLayer(&DAT_PathFindingState,8,uVar5,uVar7);
  uVar7 = DAT_TerrainDefinedData.BuildingPartsOffsets[local_c][1].y + (int)piVar1;
  uVar5 = DAT_TerrainDefinedData.BuildingPartsOffsets[local_c][1].x + xPosition;
  iVar6 = Buildings::BuildingsState::setupBuildingData
                    (&DAT_BuildingsState,playerID,uVar5,uVar7,param_7,BT_PARADEGROUND4,5,playerID,
                     0xf);
  iVar2 = (int)(short)(ushort)iVar6;
  DAT_BuildingsState.buildings[iVar2].uidWhenPlaced = iVar8;
  DAT_BuildingsState.buildings[iVar2].quarryStockpileID =
       (undefined2)DAT_TileMapState.placedBuildingID;
  buildingSize = 0;
  do {
    getBuildingSizeIndexMappingData(buildingSize,DAT_BuildingsState.buildings[iVar2].widthOrHeight);
    iVar3 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + uVar7].
            addXgetTile + DAT_TileMapState.buildingX + uVar5;
    resetTileAndClearMoat(&DAT_TileMapState,iVar3);
    DAT_TileMapState.HeightLayer[iVar3] = (byte)param_7;
    if ((DAT_TileMapState.buildingX == 2) && (DAT_TileMapState.buildingY == 2)) {
      DAT_TileMapState.LogicLayer[iVar3] = DAT_TileMapState.LogicLayer[iVar3] | 0x400;
    }
    DAT_TileMapState.BuildingLayer[iVar3] = (ushort)iVar6;
    buildingSize = buildingSize + 1;
    DAT_TileMapState.BuildingWasLayer[iVar3] = (uchar)buildingType;
    DAT_TileMapState.ChangedLayer[iVar3] = 2;
  } while ((int)buildingSize < DAT_TileMapState.constructionTileCount);
  setMiscDisplayLayer(iVar2);
  updatePathLinkagesForBuilding(this_02,iVar2);
  Navigation::PathFindingState::updateWalkAndPathLayer(&DAT_PathFindingState,8,uVar5,uVar7);
  uVar7 = DAT_TerrainDefinedData.BuildingPartsOffsets[local_c][2].y + (int)piVar1;
  uVar5 = DAT_TerrainDefinedData.BuildingPartsOffsets[local_c][2].x + xPosition;
  iVar6 = Buildings::BuildingsState::setupBuildingData
                    (&DAT_BuildingsState,playerID,uVar5,uVar7,param_7,BT_PARADEGROUND2,5,playerID,
                     0xf);
  iVar2 = (int)(short)(ushort)iVar6;
  DAT_BuildingsState.buildings[iVar2].uidWhenPlaced = iVar8;
  DAT_BuildingsState.buildings[iVar2].quarryStockpileID =
       (undefined2)DAT_TileMapState.placedBuildingID;
  buildingSize = 0;
  do {
    getBuildingSizeIndexMappingData(buildingSize,DAT_BuildingsState.buildings[iVar2].widthOrHeight);
    iVar8 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + uVar7].
            addXgetTile + DAT_TileMapState.buildingX + uVar5;
    resetTileAndClearMoat(this_03,iVar8);
    DAT_TileMapState.HeightLayer[iVar8] = (byte)param_7;
    if ((DAT_TileMapState.buildingX == 2) && (DAT_TileMapState.buildingY == 2)) {
      DAT_TileMapState.LogicLayer[iVar8] = DAT_TileMapState.LogicLayer[iVar8] | 0x400;
    }
    DAT_TileMapState.BuildingLayer[iVar8] = (ushort)iVar6;
    DAT_TileMapState.BuildingWasLayer[iVar8] = (uchar)buildingType;
    buildingSize = buildingSize + 1;
    DAT_TileMapState.ChangedLayer[iVar8] = 2;
  } while ((int)buildingSize < DAT_TileMapState.constructionTileCount);
  setMiscDisplayLayer(iVar2);
  updatePathLinkagesForBuilding(this_04,iVar2);
  Navigation::PathFindingState::updateWalkAndPathLayer(&DAT_PathFindingState,8,uVar5,uVar7);
  if ((short)buildingType == 8) {
    Buildings::BuildingsState::setupMercenaryPostCampgroundPositions(&DAT_BuildingsState,playerID);
  }
  else {
    Buildings::BuildingsState::setupBarracksCampgroundPositions(&DAT_BuildingsState,playerID);
  }
  if (((playerID == DAT_GameSynchronyState.currentPlayerSlotID) &&
      (DAT_GameState.playerDataArray[playerID].availablePeasantsAtFire <
       (int)DAT_BuildingsState.buildings[iVar2].buildingTypeBasedEmployeeCount)) &&
     ((DAT_GameState.playerDataArray[playerID].populationCap <=
       DAT_GameState.playerDataArray[playerID].currentPopulation ||
      (DAT_GameState.playerDataArray[playerID].popularity < 5000)))) {
    UI::BottomLeftTextDisplayState::setBottomLeftTextDisplayText
              (&DAT_BottomLeftTextDisplayState,1,0x4d,1,(TextMessageBLLookupStructUnion)0x0,100,6000
              );
  }
  return;
}



// ================= placeDairyfarm @ 005154d0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::placeDairyfarm
          (TileMapState *this,int param_1,uint param_2,uint param_3,undefined4 param_4,
          undefined4 param_5,int *param_6,undefined4 param_7)

{
  int iVar1;
  uint uVar2;
  int buildingID;
  TileMapState *this_00;
  int iVar3;
  int *piVar4;
  int iVar5;
  
  uVar2 = param_3;
  iVar3 = 0;
  buildingID = Buildings::BuildingsState::setupBuildingData
                         (&DAT_BuildingsState,param_1,param_2,param_3,param_7,(int)(short)param_4,3,
                          param_1,(int)param_6);
  DAT_TileMapState.placedBuildingID = buildingID;
  markBuildingFootprintFlag(&DAT_TileMapState,param_2,param_3,10);
  iVar5 = 0;
  param_6 = &DAT_BuildingsState.buildings[buildingID].tileRef1;
  do {
    iVar1 = DAT_GameState.playerDataArray[param_1].dairyFarmVariationMod4;
                    /* 0 to 3*27 + 26 = 107 */
    iVar1 = DAT_ViewportRenderState.translationMatrix
            [DAT_TerrainDefinedData.field1009_0xf5c[iVar1][iVar5].offset.y + param_3].addXgetTile +
            DAT_TerrainDefinedData.field1009_0xf5c[iVar1][iVar5].offset.x + param_2;
    *param_6 = iVar1;
    resetTileAndClearMoat(&DAT_TileMapState,iVar1);
    if (3 < iVar5) {
      DAT_TileMapState.DamageLayer[*param_6] =
           (byte)DAT_TerrainDefinedData.field1009_0xf5c
                 [DAT_GameState.playerDataArray[param_1].dairyFarmVariationMod4][iVar5].property;
    }
    param_6 = param_6 + 1;
    iVar5 = iVar5 + 1;
  } while (iVar5 < 0x1b);
  piVar4 = &DAT_GameState.playerDataArray[param_1].dairyFarmVariationMod4;
  *piVar4 = *piVar4 + 1;
  if (3 < DAT_GameState.playerDataArray[param_1].dairyFarmVariationMod4) {
    DAT_GameState.playerDataArray[param_1].dairyFarmVariationMod4 = 0;
  }
  do {
    getBuildingSizeIndexMappingData(iVar3,3);
    param_3._0_2_ = (ushort)buildingID;
    iVar5 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + uVar2].
            addXgetTile + DAT_TileMapState.buildingX + param_2;
    DAT_TileMapState.HeightLayer[iVar5] = (byte)param_7;
    DAT_TileMapState.LogicLayer[iVar5] = DAT_TileMapState.LogicLayer[iVar5] | 0x400;
    DAT_TileMapState.BuildingLayer[iVar5] = (ushort)param_3;
    DAT_TileMapState.BuildingWasLayer[iVar5] = (uchar)param_4;
    DAT_TileMapState.ChangedLayer[iVar5] = 2;
    setTerrain(&DAT_TileMapState,param_1,iVar5,DAT_TileMapState.buildingY + uVar2,2,L_NONE,
               L2_THICK_SCRUB);
    iVar3 = iVar3 + 1;
  } while (iVar3 < DAT_TileMapState.constructionTileCount);
  piVar4 = &DAT_BuildingsState.buildings[buildingID].tileRef5;
  iVar3 = 0x17;
  do {
    iVar5 = *piVar4;
    DAT_TileMapState.LogicLayer[iVar5] = DAT_TileMapState.LogicLayer[iVar5] | 0x8000000;
    DAT_TileMapState.BuildingLayer[iVar5] = (ushort)param_3;
    Navigation::PathFindingState::updatePathLinkagesInAllEightDirections
              (&DAT_PathFindingState,
               (int)DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar5],iVar5);
    piVar4 = piVar4 + 1;
    iVar3 = iVar3 + -1;
    DAT_TileMapState.BuildingWasLayer[iVar5] = (uchar)param_4;
    DAT_TileMapState.ChangedLayer[iVar5] = 2;
  } while (iVar3 != 0);
  setMiscDisplayLayer(buildingID);
  updatePathLinkagesForBuilding(this_00,buildingID);
  if (((param_1 == DAT_GameSynchronyState.currentPlayerSlotID) &&
      (DAT_GameState.playerDataArray[param_1].availablePeasantsAtFire <
       (int)DAT_BuildingsState.buildings[buildingID].buildingTypeBasedEmployeeCount)) &&
     ((DAT_GameState.playerDataArray[param_1].populationCap <=
       DAT_GameState.playerDataArray[param_1].currentPopulation ||
      (DAT_GameState.playerDataArray[param_1].popularity < 5000)))) {
    UI::BottomLeftTextDisplayState::setBottomLeftTextDisplayText
              (&DAT_BottomLeftTextDisplayState,1,0x4d,1,(TextMessageBLLookupStructUnion)0x0,100,6000
              );
  }
  return;
}



