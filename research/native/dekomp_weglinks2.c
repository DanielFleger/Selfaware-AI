// ================= updatePathLinkageLayerBasedOnBuildingsUnk @ 004999c0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::Navigation::PathFindingState::updatePathLinkageLayerBasedOnBuildingsUnk
          (PathFindingState *this,int yUnk,int tile)

{
  byte bVar1;
  BuildingTypeShort BVar2;
  bool bVar3;
  bool bVar4;
  bool bVar5;
  bool bVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  byte bVar10;
  int (*paiVar11) [8];
  uint uVar12;
  int iVar13;
  bool bVar14;
  bool bVar15;
  bool bVar16;
  byte _linkageResult;
  BOOLEnum _result;
  int local_28;
  uint local_24;
  uint local_20 [8];
  
  uVar8 = DAT_TileMapState.LogicLayer[tile];
  uVar12 = (uint)DAT_TileMapState.HeightLayer[tile];
  iVar13 = (int)(short)DAT_TileMapState.BuildingLayer[tile];
  _result = FALSE;
  if ((uVar8 & 0x10000000) != 0) {
    iVar7 = Buildings::BuildingsState::getBuildingHeightForBuildingID(iVar13);
    uVar12 = uVar12 + iVar7;
  }
  local_24 = uVar12 + 0x10;
  local_28 = uVar12 - 0x10;
  if ((iVar13 != 0) &&
     (BVar2 = DAT_BuildingsState.buildings[iVar13].buildingType,
     _result = (BOOLEnum)(DAT_BuildingDefinedData.DAT_BuildingIsGateHouseArray[(short)BVar2] != 0),
     DAT_BuildingDefinedData.DAT_BuildingIsKeepArray[(short)BVar2] != 0)) {
    _result = TRUE;
  }
  bVar3 = false;
  bVar5 = false;
  bVar4 = false;
  bVar6 = false;
  bVar10 = 0;
  iVar13 = 0;
  _linkageResult = 0;
  DAT_TileMapState.PathLinkageLayer[tile] = '\0';
  if ((uVar8 & 0x800000) == 0) {
    if ((uVar8 & 0x10000000) == 0) {
      if (((uVar8 & 2) == 0) && ((uVar8 & 0x200000) == 0)) {
        if ((uVar8 & 0x800) != 0) {
          bVar5 = true;
          goto LAB_00499ada;
        }
        if ((uVar8 & 0x400000) != 0) {
          return _result;
        }
        if ((uVar8 & 0x100) != 0) {
          bVar4 = true;
          if (DAT_TileMapState.BuildingLayer[tile] != 0) {
            iVar13 = 2;
          }
          goto LAB_00499ada;
        }
        if ((uVar8 & 0x4a5014b1) != 0) {
          return _result;
        }
      }
      bVar6 = true;
    }
    else {
      bVar3 = true;
      iVar13 = 1;
    }
  }
LAB_00499ada:
  iVar7 = 0;
  paiVar11 = DAT_TileMapState.directionTranslationMatrix + yUnk;
  do {
    iVar9 = (*paiVar11)[0] + tile;
    uVar8 = DAT_TileMapState.LogicLayer[iVar9];
    local_20[iVar7] = uVar8;
    if ((uVar8 & 0x200000) == 0) {
      if ((uVar8 & 0x800) != 0) {
        if ((iVar13 == 1) || ('\x14' < (char)DAT_TileMapState.DamageLayer[iVar9]))
        goto LAB_00499c4b;
        goto LAB_00499bce;
      }
      if ((uVar8 & 2) == 0) {
        if ((uVar8 & 0x400) == 0) {
          if ((uVar8 & 0x10000000) != 0) {
            bVar10 = bVar10 + DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[iVar7];
            goto LAB_00499bce;
          }
          if ((uVar8 & 0x400000) == 0) {
            if ((uVar8 & 0x100) != 0) {
              bVar10 = bVar10 + DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[iVar7];
              goto LAB_00499bce;
            }
            if ((uVar8 & 0x30) == 0) {
              bVar14 = (uVar8 & 0x4a5014b1) == 0;
              goto LAB_00499bcc;
            }
            bVar10 = bVar10 + DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[iVar7];
          }
          else {
            bVar10 = bVar10 + DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[iVar7];
          }
        }
        else if (DAT_BuildingDefinedData.field17_0x1774
                 [(short)DAT_BuildingsState.buildings[(short)DAT_TileMapState.BuildingLayer[iVar9]].
                         buildingType] != FALSE) {
          bVar10 = bVar10 + DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[iVar7];
        }
      }
      else if (!bVar3) {
        if ((uVar8 & 0x400) != 0) {
          bVar14 = DAT_TileMapState.BuildingLayer[iVar9] == 0;
LAB_00499bcc:
          if (!bVar14) goto LAB_00499c4b;
        }
        goto LAB_00499bce;
      }
    }
    else {
LAB_00499bce:
      if ((uVar8 & 0x10000000) == 0) {
        if (((uVar8 & 0x100) == 0) || (iVar13 == 0)) {
          if (((bVar4) || (bVar5)) &&
             (((uVar8 & 0x100) != 0 && (DAT_TileMapState.BuildingLayer[iVar9] != 0)))) {
            bVar1 = DAT_TileMapState.DamageLayer[tile];
            bVar16 = SBORROW1(bVar1,'\x14');
            bVar15 = (char)(bVar1 - 0x14) < '\0';
            bVar14 = bVar1 == 0x14;
          }
          else {
            uVar8 = (uint)DAT_TileMapState.HeightLayer[iVar9];
            if ((int)uVar8 < local_28) goto LAB_00499c4b;
            bVar16 = SBORROW4(uVar8,local_24);
            bVar15 = (int)(uVar8 - local_24) < 0;
            bVar14 = uVar8 == local_24;
          }
        }
        else {
          bVar1 = DAT_TileMapState.DamageLayer[iVar9];
          bVar16 = SBORROW1(bVar1,'\x14');
          bVar15 = (char)(bVar1 - 0x14) < '\0';
          bVar14 = bVar1 == 0x14;
        }
LAB_00499c3f:
        if (!bVar14 && bVar16 == bVar15) goto LAB_00499c4b;
      }
      else if (!bVar3) {
        if (!bVar4) goto LAB_00499c4b;
        bVar1 = DAT_TileMapState.DamageLayer[tile];
        bVar16 = SBORROW1(bVar1,'\x14');
        bVar15 = (char)(bVar1 - 0x14) < '\0';
        bVar14 = bVar1 == 0x14;
        goto LAB_00499c3f;
      }
      _linkageResult =
           _linkageResult | DAT_ClimbLogicDefinedData.DAT_BitFlagHelperForPathLinkage[iVar7];
    }
LAB_00499c4b:
    iVar7 = iVar7 + 1;
    paiVar11 = (int (*) [8])(*paiVar11 + 1);
    if (7 < iVar7) {
      if (bVar6) {
        if (((_linkageResult & 1) == 0) && ((bVar10 & 1) != 0)) {
          if (((_linkageResult & 4) == 0) && ((bVar10 & 4) != 0)) {
            _linkageResult = _linkageResult & 0xfd;
          }
          if (((_linkageResult & 0x40) == 0) && ((bVar10 & 0x40) != 0)) {
            _linkageResult = _linkageResult & 0x7f;
          }
        }
        if (((_linkageResult & 0x10) == 0) && ((bVar10 & 0x10) != 0)) {
          if (((_linkageResult & 4) == 0) && ((bVar10 & 4) != 0)) {
            _linkageResult = _linkageResult & 0xf7;
          }
          if (((_linkageResult & 0x40) == 0) && ((bVar10 & 0x40) != 0)) {
            _linkageResult = _linkageResult & 0xdf;
          }
        }
      }
      else {
        if ((((((local_20[0] & 0x10000100) != 0) && ((local_20[2] & 0x10000100) != 0)) &&
             ((local_20[1] & 0x10000100) == 0)) &&
            (((local_20[1] & 2) == 0 && ((local_20[0] & 0x800) == 0)))) &&
           ((local_20[2] & 0x800) == 0)) {
          _linkageResult = _linkageResult & 0xfd;
        }
        if ((((local_20[0] & 0x10000100) != 0) && ((local_20[6] & 0x10000100) != 0)) &&
           (((local_20[7] & 0x10000100) == 0 &&
            ((((local_20[7] & 2) == 0 && ((local_20[0] & 0x800) == 0)) &&
             ((local_20[6] & 0x800) == 0)))))) {
          _linkageResult = _linkageResult & 0x7f;
        }
        if (((((local_20[4] & 0x10000100) != 0) && ((local_20[2] & 0x10000100) != 0)) &&
            (((local_20[3] & 0x10000100) == 0 &&
             (((local_20[3] & 2) == 0 && ((local_20[4] & 0x800) == 0)))))) &&
           ((local_20[2] & 0x800) == 0)) {
          _linkageResult = _linkageResult & 0xf7;
        }
        if (((((local_20[4] & 0x10000100) != 0) && ((local_20[6] & 0x10000100) != 0)) &&
            ((local_20[5] & 0x10000100) == 0)) &&
           ((((local_20[5] & 2) == 0 && ((local_20[4] & 0x800) == 0)) &&
            ((local_20[6] & 0x800) == 0)))) {
          _linkageResult = _linkageResult & 0xdf;
        }
      }
      DAT_TileMapState.PathLinkageLayer[tile] = _linkageResult;
      return _result;
    }
  } while( true );
}



