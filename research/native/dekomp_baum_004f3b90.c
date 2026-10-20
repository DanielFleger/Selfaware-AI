// ================= findTree @ 004f3b90 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::LandscapeState::findTree
          (LandscapeState *this,int playerID,uint unitXPosition,uint unitYPosition)

{
  byte bVar1;
  ushort uVar2;
  BOOLEnum BVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  short *psVar8;
  int local_18;
  int local_14;
  int local_10;
  
  if (((unitXPosition < 400) && (unitYPosition < 400)) &&
     (*(char *)(unitYPosition * 400 + 0x21aec98 + unitXPosition) != '\0')) {
    uVar2 = DAT_TileMapState.PathConnectionLayer
            [DAT_ViewportRenderState.translationMatrix[unitYPosition].addXgetTile + unitXPosition];
    local_14 = 10000;
    local_10 = 0;
    if (0 < (short)uVar2) {
      local_18 = 1;
      if (1 < DAT_LandscapeState.maxTreeCount) {
        psVar8 = &DAT_LandscapeState.trees[1].state;
        do {
          if (((*(int *)(psVar8 + 0x1e) < 4) && (*psVar8 == 2)) &&
             (BVar3 = isTreeAdult(&DAT_LandscapeState,local_18,*(int *)(psVar8 + 4)), BVar3 != FALSE
             )) {
            bVar1 = DAT_TileMapState.HeightLayer[*(uint *)(psVar8 + 0x12)];
            iVar6 = 0;
            do {
              iVar7 = DAT_TileMapState.directionTranslationMatrix[psVar8[0x10]][iVar6] +
                      *(uint *)(psVar8 + 0x12);
              uVar5 = (uint)DAT_TileMapState.HeightLayer[iVar7];
              if (DAT_TileMapState.BuildingLayer[iVar7] != 0) {
                iVar4 = Buildings::BuildingsState::getBuildingHeightForBuildingID
                                  ((int)(short)DAT_TileMapState.BuildingLayer[iVar7]);
                uVar5 = uVar5 + iVar4;
              }
              if ((((int)(uint)bVar1 <= (int)(uVar5 + 0x10)) &&
                  ((int)(uVar5 - 0x10) <= (int)(uint)bVar1)) &&
                 (iVar7 = Navigation::PathFindingState::
                          calculateCanPlayerUnitsNavigateToAreaFromArea
                                    (&DAT_PathFindingState,playerID,(int)(short)uVar2,
                                     (int)(short)DAT_TileMapState.PathConnectionLayer[iVar7],0),
                 iVar7 != 0)) {
                if ((iVar6 < 8) &&
                   (Navigation::DirectionAlgorithmState::setAxisBasedDistanceResult
                              (&DAT_DirectionAlgorithmState,unitXPosition,unitYPosition,
                               (int)psVar8[0xf],(int)psVar8[0x10]),
                   DAT_DirectionAlgorithmState.distanceHigh < local_14)) {
                  local_14 = DAT_DirectionAlgorithmState.distanceHigh;
                  local_10 = local_18;
                }
                break;
              }
              iVar6 = iVar6 + 1;
            } while (iVar6 < 8);
          }
          local_18 = local_18 + 1;
          psVar8 = psVar8 + 0x4e;
        } while (local_18 < DAT_LandscapeState.maxTreeCount);
      }
      return local_10;
    }
  }
  return 0;
}



