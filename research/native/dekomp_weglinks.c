// ================= updatePathLinkagesInAllEightDirections @ 004a5f90 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Navigation::PathFindingState::updatePathLinkagesInAllEightDirections
          (PathFindingState *this,int y,int tile)

{
  bool bVar1;
  BOOLEnum BVar2;
  int (*paiVar3) [8];
  int *piVar4;
  
  bVar1 = false;
  updatePathLinkageLayerBasedOnBuildingsUnk(&DAT_PathFindingState,y,tile);
  paiVar3 = DAT_TileMapState.directionTranslationMatrix + y;
  piVar4 = &DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[0].int.yOffset;
  do {
    BVar2 = updatePathLinkageLayerBasedOnBuildingsUnk
                      (&DAT_PathFindingState,*piVar4 + y,(*paiVar3)[0] + tile);
    if (BVar2 != FALSE) {
      bVar1 = true;
    }
    piVar4 = piVar4 + 2;
    paiVar3 = (int (*) [8])(*paiVar3 + 1);
  } while ((int)piVar4 < 0xb4908c);
  if (bVar1) {
    DAT_BuildingsState.pathLinkageKeepWasUpdatedUnk = 1;
  }
  return;
}



// ================= updatePathLinkageLayerAtTileForSomeLogicalReason @ 00499dc0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Navigation::PathFindingState::updatePathLinkageLayerAtTileForSomeLogicalReason
          (PathFindingState *this,int tile,int y)

{
  byte bVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  iVar2 = tile;
  uVar6 = 4;
  bVar1 = DAT_TileMapState.PathLinkageLayer[tile];
  piVar3 = DAT_TileMapState.directionTranslationMatrix[y] + 1;
  tile = 2;
  do {
    iVar4 = (*(int (*) [8])(piVar3 + -1))[0] + iVar2;
    if (((DAT_TileMapState.LogicLayer[iVar4] & 0x30U) == 0) &&
       ((DAT_TileMapState.LogicLayer[iVar4] & 0x4a5014b1U) == 0)) {
      if ((bVar1 & DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[uVar6 - 4]) == 0) {
        uVar5 = uVar6 & 0x80000007;
        if ((int)uVar5 < 0) {
          uVar5 = (uVar5 - 1 | 0xfffffff8) + 1;
        }
        DAT_TileMapState.PathLinkageLayer[iVar4] =
             DAT_TileMapState.PathLinkageLayer[iVar4] &
             ~DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[uVar5];
      }
      else {
        uVar5 = uVar6 & 0x80000007;
        if ((int)uVar5 < 0) {
          uVar5 = (uVar5 - 1 | 0xfffffff8) + 1;
        }
        DAT_TileMapState.PathLinkageLayer[iVar4] =
             DAT_TileMapState.PathLinkageLayer[iVar4] |
             DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[uVar5];
      }
    }
    iVar4 = *piVar3 + iVar2;
    if (((DAT_TileMapState.LogicLayer[iVar4] & 0x30U) == 0) &&
       ((DAT_TileMapState.LogicLayer[iVar4] & 0x4a5014b1U) == 0)) {
      if ((bVar1 & DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[uVar6 - 3]) == 0) {
        uVar5 = uVar6 + 1 & 0x80000007;
        if ((int)uVar5 < 0) {
          uVar5 = (uVar5 - 1 | 0xfffffff8) + 1;
        }
        DAT_TileMapState.PathLinkageLayer[iVar4] =
             DAT_TileMapState.PathLinkageLayer[iVar4] &
             ~DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[uVar5];
      }
      else {
        uVar5 = uVar6 + 1 & 0x80000007;
        if ((int)uVar5 < 0) {
          uVar5 = (uVar5 - 1 | 0xfffffff8) + 1;
        }
        DAT_TileMapState.PathLinkageLayer[iVar4] =
             DAT_TileMapState.PathLinkageLayer[iVar4] |
             DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[uVar5];
      }
    }
    iVar4 = piVar3[1] + iVar2;
    if (((DAT_TileMapState.LogicLayer[iVar4] & 0x30U) == 0) &&
       ((DAT_TileMapState.LogicLayer[iVar4] & 0x4a5014b1U) == 0)) {
      if ((bVar1 & DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[uVar6 - 2]) == 0) {
        uVar5 = uVar6 + 2 & 0x80000007;
        if ((int)uVar5 < 0) {
          uVar5 = (uVar5 - 1 | 0xfffffff8) + 1;
        }
        DAT_TileMapState.PathLinkageLayer[iVar4] =
             DAT_TileMapState.PathLinkageLayer[iVar4] &
             ~DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[uVar5];
      }
      else {
        uVar5 = uVar6 + 2 & 0x80000007;
        if ((int)uVar5 < 0) {
          uVar5 = (uVar5 - 1 | 0xfffffff8) + 1;
        }
        DAT_TileMapState.PathLinkageLayer[iVar4] =
             DAT_TileMapState.PathLinkageLayer[iVar4] |
             DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[uVar5];
      }
    }
    iVar4 = piVar3[2] + iVar2;
    if (((DAT_TileMapState.LogicLayer[iVar4] & 0x30U) == 0) &&
       ((DAT_TileMapState.LogicLayer[iVar4] & 0x4a5014b1U) == 0)) {
      if ((bVar1 & DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[uVar6 - 1]) == 0) {
        uVar5 = uVar6 + 3 & 0x80000007;
        if ((int)uVar5 < 0) {
          uVar5 = (uVar5 - 1 | 0xfffffff8) + 1;
        }
        DAT_TileMapState.PathLinkageLayer[iVar4] =
             DAT_TileMapState.PathLinkageLayer[iVar4] &
             ~DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[uVar5];
      }
      else {
        uVar5 = uVar6 + 3 & 0x80000007;
        if ((int)uVar5 < 0) {
          uVar5 = (uVar5 - 1 | 0xfffffff8) + 1;
        }
        DAT_TileMapState.PathLinkageLayer[iVar4] =
             DAT_TileMapState.PathLinkageLayer[iVar4] |
             DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[uVar5];
      }
    }
    piVar3 = piVar3 + 4;
    uVar6 = uVar6 + 4;
    tile = tile + -1;
  } while (tile != 0);
  return;
}



