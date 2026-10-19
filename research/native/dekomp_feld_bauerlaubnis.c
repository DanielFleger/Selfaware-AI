// ================= isBuildingPlacementAllowedAtTile @ 004f9a60 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* @return int 0 if allowed, 1 if not allowed, 2 not allowed because of clashing building placement
   
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::TileMapState::isBuildingPlacementAllowedAtTile
          (TileMapState *this,int tile,int playerID,MappersEnum commandBuildingType,int param_4)

{
  ushort uVar1;
  uint uVar2;
  bool bVar3;
  uint uVar4;
  BOOLEnum BVar5;
  int iVar6;
  uint uVar7;
  
  uVar2 = DAT_TileMapState.LogicLayer[tile];
  uVar7 = uVar2 & 0x100;
  bVar3 = false;
  uVar4 = (uint)DAT_TileMapState.HeightLayer[tile];
  if ((uVar7 != 0) && ((DAT_TileMapState.WallOwnerLayer[tile] & 7) + 1 == playerID)) {
    switch(commandBuildingType) {
    case M_MAPPER_GATEHOUSE:
    case M_MAPPER_GATE_MAIN:
    case M_MAPPER_GATE_INNER:
    case M_MAPPER_GATE_WOOD:
    case M_MAPPER_GATE_POSTERN:
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
      uVar4 = (uint)DAT_TileMapState.DefaultHeightLayer[tile];
    }
  }
  if (DAT_TileMapState.buildingHeightLimit < 0) {
    if ((int)uVar4 < -DAT_TileMapState.buildingHeightLimit) {
      return 1;
    }
  }
  else if (DAT_TileMapState.buildingHeightLimit < (int)uVar4) {
    if (commandBuildingType == M_MAPPER_CATTLEFARM) {
      DAT_TileMapState.placementWarning = 1;
      return 1;
    }
    if (commandBuildingType == M_MAPPER_APPLEFARM) {
      DAT_TileMapState.placementWarning = 2;
      return 1;
    }
    if (commandBuildingType == M_MAPPER_HOPSFARM) {
      DAT_TileMapState.placementWarning = 3;
      return 1;
    }
    if (commandBuildingType != M_MAPPER_WHEATFARM) {
      return 1;
    }
    DAT_TileMapState.placementWarning = 4;
    return 1;
  }
  if (DAT_TileMapState.buildingMaxHeightDifference + DAT_TileMapState.buildingMinHeight < (int)uVar4
     ) {
    return 1;
  }
  if (((uVar2 & 8) != 0) && (commandBuildingType == M_MAPPER_PITCH_DITCH)) {
    return 1;
  }
  if (DAT_TileMapState.BuildingLayer[tile] != 0) {
    return 2;
  }
  uVar1 = DAT_TileMapState.UnitLayer[tile];
  if (uVar1 != 0) {
    BVar5 = Synchrony::GameSynchronyState::isAIPlayer(&DAT_GameSynchronyState,playerID);
    if (BVar5 == FALSE) {
      if (DAT_UnitsState.units[(short)uVar1].unitType != UT_CHICKEN) {
        return 1;
      }
    }
    else {
      if (DAT_UnitsState.units[(short)uVar1].unitType == UT_LORD) {
        return 1;
      }
      if ((DAT_UnitsState.units[(short)uVar1].isSelectable_OR_matchTime != 0) &&
         (DAT_UnitsState.units[(short)uVar1].owner != playerID)) {
        return 1;
      }
    }
  }
                    /* is sea */
  if ((uVar2 & 1) != 0) {
    return 1;
  }
                    /* is any border */
  if ((uVar2 & 0x30) == 0) {
                    /* is river  */
    if ((uVar2 & 0x100000) != 0) {
      return 1;
    }
    if (uVar7 != 0) {
                    /* other people's buildings */
      if ((DAT_TileMapState.WallOwnerLayer[tile] & 7) + 1 != playerID) {
        return 1;
      }
      switch(commandBuildingType) {
      case M_MAPPER_GATEHOUSE:
      case M_MAPPER_GATE_MAIN:
      case M_MAPPER_GATE_INNER:
      case M_MAPPER_GATE_WOOD:
      case M_MAPPER_GATE_POSTERN:
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
        break;
      default:
        return 1;
      }
    }
    if ((((uVar2 & 4) == 0) || (param_4 != 0)) && ((uVar2 & 0x10000400) == 0)) {
                    /* not a keep and not a building */
      if ((((uVar2 & 0x3000) != 0) &&
          (iVar6 = (int)(short)DAT_TileMapState.OrganismLayer[tile], iVar6 != 0)) && (iVar6 < 2000))
      {
                    /* tree or tree_variation */
        switch(DAT_LandscapeState.trees[iVar6].treeType) {
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
          if (DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) {
            return 1;
          }
          BVar5 = Synchrony::GameSynchronyState::isAIPlayer(&DAT_GameSynchronyState,playerID);
          if (BVar5 == FALSE) {
            return 1;
          }
        }
      }
                    /* not any farms or fords */
      if ((((uVar2 & 0xf000000) == 0) || (param_4 != 0)) && ((uVar2 & 0x200000) == 0)) {
        if (((char)uVar2 < '\0') && (uVar7 == 0)) {
          bVar3 = true;
        }
        iVar6 = 1;
        if ((((!bVar3) || (DAT_TileMapState.buildingPlacementProperty_4 != 0)) &&
            (((uVar2 & 0x40000000) == 0 || (DAT_TileMapState.buildingPlacementProperty_7 != 0)))) &&
           (((DAT_TileMapState.buildingPlacementProperty_6 == 2 || ((uVar2 & 0x20000000) == 0)) ||
            (DAT_TileMapState.buildingPlacementProperty_6 != 0)))) {
                    /* not moat and marsh */
          iVar6 = 0;
        }
        return iVar6;
      }
    }
    return 1;
  }
  return 1;
}



