// ================= setTerrain @ 00512940 =================

/* WARNING: Inlined function: computeTileXOffset */
/* WARNING: Restarted to delay deadcode elimination for space: ram */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::setTerrain
          (TileMapState *this,int playerID,int tile,uint yParam,uint brushType,Logic1 flags1,
          Logic2 flags2)

{
  int baseTile;
  uint y;
  uint x;
  BOOLEnum BVar1;
  int iVar2;
  uint *puVar3;
  int local_1c;
  int local_18;
  int _index;
  int _size;
  
  y = yParam;
  baseTile = tile;
  _size = DAT_TerrainDefinedData.BrushSizeArray[brushType];
  if (DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) {
    local_1c = 0x1e;
    local_18 = 0x1e;
  }
  else {
    local_1c = 0xf;
    local_18 = 7;
  }
  if (((DAT_GameCore.gameMode_2 == GM_EDITOR) && (flags1 != L_MOAT)) &&
     (((flags2 == L2_EARTH_AND_STONES ||
       (((flags2 == L2_OASIS_GRASS || (flags2 == L2_BEACH)) ||
        (flags2 == L2_STONES_OR_DRIVEN_SANDUnk)))) ||
      ((flags2 == L2_SCRUB || (flags2 == L2_THICK_SCRUB)))))) {
                    /* this functions processes all oasis tiles */
    setLand(&DAT_TileMapState,tile,yParam,brushType);
  }
  if (flags1 == L_MOAT) {
    _size = 9;
  }
  _index = 0;
  do {
    if (_size <= _index) {
      return;
    }
    if (flags1 == L_MOAT) {
      getTileForBrush(&DAT_TileMapState,0,_index,&tile,(int *)&yParam,baseTile,y);
    }
    else {
      getTileForBrush(&DAT_TileMapState,1,_index,&tile,(int *)&yParam,baseTile,y);
    }
    if ((DAT_TileMapState.LogicLayer[tile] & 0x10U) == 0) {
      if (flags1 == L_SEA) {
        if (((((DAT_TileMapState.LogicLayer[tile] & 0x10000400U) == 0) &&
             (DAT_TileMapState.BuildingLayer[tile] == 0)) &&
            ((DAT_TileMapState.LogicLayer[tile] & 0x100U) == 0)) &&
           (DAT_TileMapState.OrganismLayer[tile] == 0)) {
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffffbf;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffefffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffdfffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffff7f;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffdffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffbffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfff7ffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xdfffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0x7fffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xbfffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffff7;
          DAT_TileMapState.Logic2Layer[tile] = 0;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] | 1;
          DAT_TileMapState.HeightLayer[tile] = 0;
          DAT_TileMapState.DefaultHeightLayer[tile] = 0;
          DAT_TileMapState.forceUpdateLogicalAndMiscDisplayLayers = 1;
LAB_00514457:
          if (flags1 != L_NONE) {
            Navigation::PathFindingState::updatePathLinkagesInAllEightDirections
                      (&DAT_PathFindingState,yParam,tile);
          }
        }
      }
      else if ((flags1 == L_RIVER) || (flags1 == L_FORD)) {
        if ((((DAT_TileMapState.LogicLayer[tile] & 0x10000400U) == 0) &&
            (((DAT_TileMapState.BuildingLayer[tile] == 0 &&
              ((DAT_TileMapState.LogicLayer[tile] & 0x100U) == 0)) &&
             (DAT_TileMapState.OrganismLayer[tile] == 0)))) &&
           ((flags2 == L2_NONE || ((DAT_TileMapState.LogicLayer[tile] & 0x100000U) != 0)))) {
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffffbf;
          if (flags1 == L_RIVER) {
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffdfffff;
          }
          else {
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffefffff;
          }
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffff7f;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffdffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffbffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfff7ffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xdfffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0x7fffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xbfffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffffe;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffff7;
          DAT_TileMapState.Logic2Layer[tile] = 0;
          if (flags2 != L2_BEACH) {
            DAT_TileMapState.WallGFXLayer[tile] = DAT_TileMapState.RandomLayer[tile] & 7;
          }
          if (flags2 == L2_OASIS_GRASS) {
            DAT_TileMapState.Logic2Layer[tile] = 0x10;
          }
          if (flags2 == L2_BEACH) {
            DAT_TileMapState.Logic2Layer[tile] = 0x20;
            DAT_TileMapState.WallGFXLayer[tile] =
                 ((ushort)DAT_GameCore.mapTimeInTicks & 8) +
                 DAT_TileMapState.WallGFXLayer[tile] * 0x20 +
                 (DAT_TileMapState.RandomLayer[tile] & 7) * 0x400;
          }
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] | flags1;
          if (7 < DAT_TileMapState.HeightLayer[tile]) {
            DAT_TileMapState.HeightLayer[tile] = DAT_TileMapState.DefaultHeightLayer[tile] - 8;
            DAT_TileMapState.forceUpdateLogicalAndMiscDisplayLayers = 1;
          }
          goto LAB_00514457;
        }
      }
      else if (flags1 == L_ROCKY) {
        if ((((DAT_TileMapState.LogicLayer[tile] & 0x10000400U) == 0) &&
            (DAT_TileMapState.BuildingLayer[tile] == 0)) &&
           (((DAT_TileMapState.LogicLayer[tile] & 0x100U) == 0 &&
            (((DAT_TileMapState.LogicLayer[tile] & 0x100000U) == 0 &&
             (DAT_TileMapState.OrganismLayer[tile] == 0)))))) {
          if ((DAT_TileMapState.LogicLayer[tile] & 1U) == 0) {
            if (DAT_TileMapState.HeightLayer[tile] < 8) {
              DAT_TileMapState.HeightLayer[tile] = 8;
              DAT_TileMapState.DefaultHeightLayer[tile] = 8;
            }
          }
          else {
            DAT_TileMapState.HeightLayer[tile] = 0;
            DAT_TileMapState.DefaultHeightLayer[tile] = 0;
          }
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffffe;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffefffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffdfffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffffbf;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffdffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffbffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfff7ffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xdfffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0x7fffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xbfffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffff7;
          DAT_TileMapState.Logic2Layer[tile] = 0;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] | 0x80;
          goto LAB_00514457;
        }
      }
      else if (flags1 == L_IRON) {
        if ((((DAT_TileMapState.LogicLayer[tile] & 0x10000400U) == 0) &&
            (DAT_TileMapState.BuildingLayer[tile] == 0)) &&
           (((DAT_TileMapState.LogicLayer[tile] & 0x100U) == 0 &&
            ((((DAT_TileMapState.LogicLayer[tile] & 1U) == 0 &&
              ((DAT_TileMapState.LogicLayer[tile] & 0x100000U) == 0)) &&
             (DAT_TileMapState.OrganismLayer[tile] == 0)))))) {
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffefffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffdfffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffff7f;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffbffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffdffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xdfffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0x7fffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xbfffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffff7;
          DAT_TileMapState.Logic2Layer[tile] = 0;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] | 0x80000;
          goto LAB_00514457;
        }
      }
      else if (flags1 == L_PEBBLES) {
        if (((((DAT_TileMapState.LogicLayer[tile] & 0x10000400U) == 0) &&
             (DAT_TileMapState.BuildingLayer[tile] == 0)) &&
            ((DAT_TileMapState.LogicLayer[tile] & 0x100U) == 0)) &&
           (((DAT_TileMapState.LogicLayer[tile] & 0x100000U) == 0 &&
            (DAT_TileMapState.OrganismLayer[tile] == 0)))) {
          if ((DAT_TileMapState.LogicLayer[tile] & 1U) == 0) {
            if (DAT_TileMapState.HeightLayer[tile] < 8) {
              DAT_TileMapState.HeightLayer[tile] = 8;
              DAT_TileMapState.DefaultHeightLayer[tile] = 8;
            }
          }
          else {
            DAT_TileMapState.HeightLayer[tile] = 0;
            DAT_TileMapState.DefaultHeightLayer[tile] = 0;
          }
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffffe;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffffbf;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffefffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffdfffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffff7f;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffdffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfff7ffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xdfffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0x7fffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xbfffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffff7;
          DAT_TileMapState.Logic2Layer[tile] = 0;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] | 0x40000;
          goto LAB_00514457;
        }
      }
      else if (flags1 == L_MARSH) {
        if ((((DAT_TileMapState.LogicLayer[tile] & 0x10000400U) == 0) &&
            (DAT_TileMapState.BuildingLayer[tile] == 0)) &&
           (((DAT_TileMapState.LogicLayer[tile] & 0x100U) == 0 &&
            (((DAT_TileMapState.LogicLayer[tile] & 0x100000U) == 0 &&
             (DAT_TileMapState.OrganismLayer[tile] == 0)))))) {
          DAT_TileMapState.HeightLayer[tile] = 8;
          DAT_TileMapState.DefaultHeightLayer[tile] = 8;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffffe;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffffbf;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffefffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffdfffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffff7f;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffdffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfff7ffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0x7fffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xbfffffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffff7;
          DAT_TileMapState.Logic2Layer[tile] = 0;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] | 0x20000000;
          goto LAB_00514457;
        }
      }
      else if (flags1 == L_OIL) {
        if ((((((DAT_TileMapState.LogicLayer[tile] & 0x10000400U) == 0) &&
              (DAT_TileMapState.BuildingLayer[tile] == 0)) &&
             ((DAT_TileMapState.LogicLayer[tile] & 0x100U) == 0)) &&
            (((DAT_TileMapState.LogicLayer[tile] & 0x100000U) == 0 &&
             (DAT_TileMapState.OrganismLayer[tile] == 0)))) &&
           ((DAT_TileMapState.LogicLayer[tile] & 0x20000000U) != 0)) {
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffffe;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffffbf;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffefffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffdfffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffff7f;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffdffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfff7ffff;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffff7;
          DAT_TileMapState.Logic2Layer[tile] = 0;
          DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] | 0x80000000;
          goto LAB_00514457;
        }
      }
      else if (flags1 == L_MOAT) {
        if (((((((DAT_TileMapState.OrganismLayer[tile] == 0) &&
                ((DAT_TileMapState.LogicLayer[tile] & 0x10000400U) == 0)) &&
               (DAT_TileMapState.BuildingLayer[tile] == 0)) &&
              ((((DAT_TileMapState.LogicLayer[tile] & 0x100U) == 0 &&
                ((DAT_TileMapState.LogicLayer[tile] & 1U) == 0)) &&
               (((DAT_TileMapState.LogicLayer[tile] & 0x100000U) == 0 &&
                (((DAT_TileMapState.LogicLayer[tile] & 0x200000U) == 0 &&
                 ((DAT_TileMapState.LogicLayer[tile] & 0x80U) == 0)))))))) &&
             ((DAT_TileMapState.LogicLayer[tile] & 0x20000U) == 0)) &&
            ((((DAT_TileMapState.LogicLayer[tile] & 0x80000U) == 0 &&
              ((DAT_TileMapState.LogicLayer[tile] & 0x20000000U) == 0)) &&
             ((DAT_TileMapState.LogicLayer[tile] & 4U) == 0)))) &&
           (((x = tile - DAT_ViewportRenderState.translationMatrix[yParam].addXgetTile,
             DAT_GameCore.gameMode_2 == GM_EDITOR || (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT)) ||
            (BVar1 = Navigation::PathFindingState::isEnemyTooCloseUnk
                               (&DAT_PathFindingState,playerID,x,yParam,local_1c), BVar1 == FALSE)))
           ) {
          if (DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) {
            iVar2 = getCastleBuildRangeForMapSize(&DAT_TileMapState);
            iVar2 = Navigation::PathFindingState::isOpponentBuildingInRange
                              (&DAT_PathFindingState,playerID,x,yParam,local_18,-1,-1,iVar2 + 5);
            if (iVar2 != 0) goto LAB_005129f2;
          }
          if ((((DAT_TileMapState.LogicLayer[tile] & 0x40000000U) == 0) || (flags2 == L2_MOAT_UNDUG)
              ) && (DAT_TileMapState.HeightLayer[tile] < 0xd)) {
            if (flags2 == L2_NONE) {
              if (((DAT_TileMapState.LogicLayer[tile] & 0x4000U) == 0) &&
                 (iVar2 = createMoatData(&DAT_TileMapState,playerID,x,yParam,0), iVar2 != 0)) {
                DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] | 0x4000;
              }
            }
            else if (flags2 == L2_SCRUB) {
              if ((DAT_TileMapState.LogicLayer[tile] & 0x4000U) != 0) {
                DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffbfff;
                clearMoatDataAtTile(&DAT_TileMapState,x,yParam);
              }
            }
            else {
              DAT_TileMapState.HeightLayer[tile] = 8;
              DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffff7;
              DAT_TileMapState.Logic2Layer[tile] = 0;
              if (flags2 == L2_EARTH_AND_STONES) {
                iVar2 = createMoatData(&DAT_TileMapState,playerID,x,yParam,1);
                if (iVar2 != 0) {
                  DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffbfff
                  ;
                  DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] | 0x40000000
                  ;
                  DAT_TileMapState.HeightLayer[tile] = 0;
                }
              }
              else if (flags2 == L2_MOAT_UNDUG) {
                clearMoatDataAtTile(&DAT_TileMapState,x,yParam);
                DAT_TileMapState.HeightLayer[tile] = 8;
                DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffbfff;
                DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xbfffffff;
              }
            }
            goto LAB_00514457;
          }
        }
      }
      else {
        if (((flags2 != L2_EARTH_AND_STONES) && (flags2 != L2_OASIS_GRASS)) &&
           ((flags2 != L2_BEACH &&
            (((flags2 != L2_STONES_OR_DRIVEN_SANDUnk && (flags2 != L2_SCRUB)) &&
             (flags2 != L2_THICK_SCRUB)))))) {
          if (flags1 == L_BOULDERS) {
            if ((((DAT_TileMapState.LogicLayer[tile] & 0x10000400U) != 0) ||
                (DAT_TileMapState.BuildingLayer[tile] != 0)) ||
               (((DAT_TileMapState.LogicLayer[tile] & 0x100U) != 0 ||
                (((DAT_TileMapState.LogicLayer[tile] & 0x100000U) != 0 ||
                 (DAT_TileMapState.OrganismLayer[tile] != 0)))))) goto LAB_005129f2;
            if ((DAT_TileMapState.LogicLayer[tile] & 1U) == 0) {
              if (DAT_TileMapState.HeightLayer[tile] < 8) {
                DAT_TileMapState.HeightLayer[tile] = 8;
                DAT_TileMapState.DefaultHeightLayer[tile] = 8;
              }
            }
            else {
              DAT_TileMapState.HeightLayer[tile] = 0;
              DAT_TileMapState.DefaultHeightLayer[tile] = 0;
            }
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffffe;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffffbf;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffefffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffdfffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffff7f;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffbffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfff7ffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xdfffffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0x7fffffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xbfffffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffff7;
            DAT_TileMapState.Logic2Layer[tile] = 0;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] | 0x20000;
          }
          else if (flags1 == 0x40) {
            if (((((DAT_TileMapState.LogicLayer[tile] & 1U) == 0) ||
                 ((DAT_TileMapState.LogicLayer[tile] & 0x10000400U) != 0)) ||
                (DAT_TileMapState.BuildingLayer[tile] != 0)) ||
               (((DAT_TileMapState.LogicLayer[tile] & 0x100U) != 0 ||
                (DAT_TileMapState.OrganismLayer[tile] != 0)))) goto LAB_005129f2;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] | 0x40;
          }
          goto LAB_00514457;
        }
        if ((((DAT_TileMapState.LogicLayer[tile] & 0x10000400U) == 0) &&
            (DAT_TileMapState.BuildingLayer[tile] == 0)) &&
           (((DAT_TileMapState.LogicLayer[tile] & 0x100U) == 0 &&
            (((DAT_TileMapState.LogicLayer[tile] & 0x60300001U) == 0 &&
             (DAT_TileMapState.OrganismLayer[tile] == 0)))))) {
          if (flags2 != L2_EARTH_AND_STONES) {
LAB_00513f5f:
            DAT_TileMapState.MiscDisplayLayer[tile] =
                 DAT_TileMapState.MiscDisplayLayer[tile] & 0xffdf;
            if (((flags2 != L2_STONES_OR_DRIVEN_SANDUnk) && (flags2 != L2_SCRUB)) &&
               ((flags2 != L2_THICK_SCRUB &&
                ((flags2 != L2_EARTH_AND_STONES && (flags2 != L2_OASIS_GRASS)))))) {
              if (flags2 == L2_BEACH) {
                DAT_TileMapState.HeightLayer[tile] = 0;
                DAT_TileMapState.DefaultHeightLayer[tile] = 0;
              }
              else {
                DAT_TileMapState.HeightLayer[tile] = 8;
                DAT_TileMapState.DefaultHeightLayer[tile] = 8;
              }
            }
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffffe;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffffbf;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffefffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffdfffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xffffff7f;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffdffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfff7ffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xdfffffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0x7fffffff;
            DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xbfffffff;
            if (flags2 != L2_EARTH_AND_STONES) {
              DAT_TileMapState.LogicLayer[tile] = DAT_TileMapState.LogicLayer[tile] & 0xfffffff7;
            }
            DAT_TileMapState.Logic2Layer[tile] = (undefined1)flags2;
            goto LAB_00514457;
          }
          if ((((DAT_TileMapState.LogicLayer[tile] & 0x80000U) == 0) &&
              ((DAT_TileMapState.LogicLayer[tile] & 0x20000U) == 0)) &&
             ((DAT_TileMapState.Logic2Layer[tile] & 0x20) == 0)) {
            DAT_TileMapState.bitFlag = 0;
            if ((*(uint *)(DAT_TileMapState.ptr_TerrainTypeTileMap +
                          DAT_TileMapState.DAT_SomeTile + 1) & 0x20) != 0) {
              DAT_TileMapState.bitFlag = 0x20;
            }
            if ((*(uint *)(DAT_TileMapState.ptr_TerrainTypeTileMap +
                          DAT_TileMapState.DAT_SomeTile + -1) & 0x20) != 0) {
              DAT_TileMapState.bitFlag = DAT_TileMapState.bitFlag | 2;
            }
            puVar3 = (uint *)(DAT_TileMapState.ptr_TerrainTypeTileMap +
                             *(int *)(DAT_TileMapState.ptr_MovementDirectionTranslationMatrix +
                                     DAT_TileMapState.DAT_SomeY * 0x20) +
                             DAT_TileMapState.DAT_SomeTile);
            if ((*(uint *)((int)puVar3 + -1) & 0x20) != 0) {
              DAT_TileMapState.bitFlag = DAT_TileMapState.bitFlag | 1;
            }
            if ((*(uint *)((int)puVar3 + 1) & 0x20) != 0) {
              DAT_TileMapState.bitFlag = DAT_TileMapState.bitFlag | 0x40;
            }
            if ((*puVar3 & 0x20) != 0) {
              DAT_TileMapState.bitFlag = DAT_TileMapState.bitFlag | 0x80;
            }
            puVar3 = (uint *)(DAT_TileMapState.ptr_TerrainTypeTileMap +
                             *(int *)((int)(DAT_TileMapState.ptr_MovementDirectionTranslationMatrix
                                           + DAT_TileMapState.DAT_SomeY * 0x20) + 0x10) +
                             DAT_TileMapState.DAT_SomeTile);
            if ((*(uint *)((int)puVar3 + -1) & 0x20) != 0) {
              DAT_TileMapState.bitFlag = DAT_TileMapState.bitFlag | 4;
            }
            if ((*(uint *)((int)puVar3 + 1) & 0x20) != 0) {
              DAT_TileMapState.bitFlag = DAT_TileMapState.bitFlag | 0x10;
            }
            if ((*puVar3 & 0x20) != 0) {
              DAT_TileMapState.bitFlag = DAT_TileMapState.bitFlag | 8;
            }
            if (DAT_TileMapState.bitFlag == 0) goto LAB_00513f5f;
          }
        }
      }
    }
LAB_005129f2:
    _index = _index + 1;
  } while( true );
}



// ================= ClickSetTerrain @ 004813c0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* also for moat placement in editor!
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Commands::ClickSetTerrain(void)

{
  DAT_GameSynchronyState.DAT_CommandSize = 10;
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_SCHEDULE_AND_SEND) {
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam1,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam2,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam3,4,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam4,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    return;
  }
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_EXECUTE) {
    DAT_GameSynchronyState.DAT_GameCommandParam0 = DAT_GameSynchronyState.DAT_CommandActionPlan;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    DAT_GameSynchronyState.DAT_GameCommandParam1 = 0;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam1,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    DAT_GameSynchronyState.DAT_GameCommandParam2 = 0;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam2,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam3,4,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    DAT_GameSynchronyState.DAT_GameCommandParam4 = L2_NONE;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam4,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    if (((DAT_GameSynchronyState.DAT_GameCommandParam0 < 400) &&
        (DAT_GameSynchronyState.DAT_GameCommandParam1 < 400)) &&
       (*(char *)(DAT_GameSynchronyState.DAT_GameCommandParam1 * 400 + 0x21aec98 +
                 DAT_GameSynchronyState.DAT_GameCommandParam0) != '\0')) {
      Map::TileMapState::setTerrain
                (&DAT_TileMapState,DAT_GameSynchronyState.protocolInvokerPlayerID,
                 DAT_ViewportRenderState.translationMatrix
                 [DAT_GameSynchronyState.DAT_GameCommandParam1].addXgetTile +
                 DAT_GameSynchronyState.DAT_GameCommandParam0,
                 DAT_GameSynchronyState.DAT_GameCommandParam1,
                 DAT_GameSynchronyState.DAT_GameCommandParam2,
                 DAT_GameSynchronyState.DAT_GameCommandParam3,
                 DAT_GameSynchronyState.DAT_GameCommandParam4);
      Map::Navigation::PathFindingState::updateWalkAndPathLayer
                (&DAT_PathFindingState,9,DAT_GameSynchronyState.DAT_GameCommandParam0,
                 DAT_GameSynchronyState.DAT_GameCommandParam1);
      if (DAT_GameSynchronyState.DAT_GameCommandParam3 != L_MOAT) {
        DAT_TileMapState.forceUpdateMacroLayerFlag = 1;
      }
      UI::MinimapViewState::triggerMinimapRedraw(&DAT_MinimapViewState);
    }
  }
  return;
}



// ================= hasEnoughGoldForMoat @ 0040cac0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

uint __thiscall
_HoldStrong::Map::Buildings::BuildingsState::hasEnoughGoldForMoat(BuildingsState *this)

{
  int _pGold;
  int local_4;
  
  getBuildingCost(&DAT_BuildingsState,M_MAPPER_MOAT,&local_4,&_pGold);
  return (uint)(((DAT_TileMapState.moatTileCount -
                 DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                 moatTileCount) + 1) * _pGold <=
               DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
               startResources[0xf]);
}



