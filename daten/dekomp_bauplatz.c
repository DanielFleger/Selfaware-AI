// ================= _HoldStrong::Map::Buildings::BuildingsState::processPlacementResourceLossForBuildingType @ 0041bfd0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Buildings::BuildingsState::processPlacementResourceLossForBuildingType
          (BuildingsState *this,int playerID,BuildingType buildingType,int param_3)

{
  short *psVar1;
  int amount;
  int iVar2;
  GameMode2Int GVar3;
  int playerID_00;
  BuildingType buildingType_00;
  short sVar4;
  uint uVar5;
  int amount_00;
  int iVar6;
  int local_4;
  
  buildingType_00 = buildingType;
  playerID_00 = playerID;
  GVar3 = DAT_GameCore.gameMode_2;
  local_4 = (int)&DAT_BuildingsState;
  if ((((DAT_GameCore.solitaryAllBuildingsAreFree == FALSE) &&
       (DAT_GameCore.gameMode_2 != GM_EDITOR)) &&
      ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY ||
       ((((buildingType != BT_MANORHOUSE && (buildingType != BT_STONEKEEP)) &&
         (buildingType != BT_STRONGHOLD)) &&
        ((buildingType != BT_KEEPFOUR && (buildingType != BT_KEEPFIVE)))))))) &&
     (uVar5 = hasLessWoodThanTheCostOfAWoodcuttersHutAndNoWoodcutters
                        (&DAT_BuildingsState,playerID,buildingType), iVar6 = param_3, uVar5 == 0)) {
    if (GVar3 == GM_SIEGE_THAT) {
      if (buildingType_00 == BT_PITCHDITCH) {
        return;
      }
    }
    else if (buildingType_00 == BT_PITCHDITCH) {
      psVar1 = &DAT_GameState.playerDataArray[playerID].pitchDitchCounterTo4;
      if (*psVar1 == 0) {
        processResourceLoss(&DAT_BuildingsState,playerID,RT_PITCH,1,param_3);
        if (iVar6 != 0) {
          return;
        }
        *psVar1 = 1;
        return;
      }
      if (param_3 != 0) {
        return;
      }
      sVar4 = *psVar1 + 1;
      *psVar1 = sVar4;
      if (sVar4 != 4) {
        return;
      }
      *psVar1 = 0;
      return;
    }
    buildingType = DAT_BuildingsState.buildingCosts[buildingType_00].requiredStone_0x4;
    amount = DAT_BuildingsState.buildingCosts[buildingType_00].requiredWood;
    amount_00 = DAT_BuildingsState.buildingCosts[buildingType_00].requiredIron_0x8;
    iVar2 = DAT_BuildingsState.buildingCosts[buildingType_00].requiredPitch_0xc;
    local_4 = DAT_BuildingsState.buildingCosts[buildingType_00].requiredGold;
    if (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) {
      amount_00 = 0;
      playerID = 0;
      resourceGainForKillingPitAndPitchDitch
                (&DAT_BuildingsState,buildingType_00,(int *)&buildingType,&local_4);
      iVar6 = param_3;
      iVar2 = playerID;
    }
    else if (amount != 0) {
      processResourceLoss(&DAT_BuildingsState,playerID,RT_WOOD,amount,param_3);
    }
    playerID = iVar2;
    if (buildingType != 0) {
      processResourceLoss(&DAT_BuildingsState,playerID_00,RT_STONE,buildingType,iVar6);
    }
    if (amount_00 != 0) {
      processResourceLoss(&DAT_BuildingsState,playerID_00,RT_IRON,amount_00,iVar6);
    }
    if (playerID != 0) {
      processResourceLoss(&DAT_BuildingsState,playerID_00,RT_PITCH,playerID,iVar6);
    }
    if (local_4 != 0) {
      processResourceLoss(&DAT_BuildingsState,playerID_00,RT_GOLD,local_4,iVar6);
    }
  }
  return;
}


// ================= _HoldStrong::Global::PlayPlacementWarning @ 004380e0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl _HoldStrong::Global::PlayPlacementWarning(BuildingFailReasonEnum param_1)

{
  switch(param_1) {
  case BFRE_NOT_ADJ_STOCKPILE:
                    /* "Needs to be placed adjacent to the stockpile" */
    Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"placement_warning2.wav");
    return;
  case BFRE_NOT_ADJ_ARMORY:
                    /* "Needs to be placed adjacent to the armory" */
    Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"placement_warning3.wav");
    return;
  case BFRE_NOT_IRON_ORE:
                    /* "Iron mine must be built on iron ore" */
    Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"placement_warning4.wav");
    return;
  case BFRE_NOT_OIL_MARSH:
                    /* "Pitch rig must be built on oil in the marsh" */
    Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"placement_warning5.wav");
    return;
  case BFRE_NOT_ADJ_GRANARY:
                    /* "Needs to be placed adjacent to the granary" */
    Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"placement_warning6.wav");
    return;
  case BFRE_MISSING5:
    Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"placement_warning20.wav");
    return;
  case BFRE_MISSING4:
    Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"placement_warning19.wav");
    return;
  case BFRE_MUST_BE_PLACED_ON_OASES:
                    /* "Farms must be placed on oases" */
    Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"placement_warning18.wav");
    return;
  case BFRE_MISSING2:
    Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"placement_warning21.wav");
    return;
  default:
                    /* "Can't place that there my lord" */
    Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"placement_warning16.wav");
    return;
  }
}


// ================= _HoldStrong::UI::Rendering::RenderAndPlayKeepAndGranaryPlacementInfoDisplayElement @ 004b1c30 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::UI::Rendering::RenderAndPlayKeepAndGranaryPlacementInfoDisplayElement
          (int posX,int posY,DWORD whichBuildingIsMissing)

{
  int numInGroup;
  BOOLEnum BVar1;
  char *pcVar2;
  int iVar3;
  int iVar4;
  int maxWidth;
  uint color1;
  uint color2;
  int fontSize;
  int blendStrength;
  
  BVar1 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
  if ((BVar1 == FALSE) || (DAT_GameCore.gameMode_2 == GM_CRUSADER_TUTORIAL)) {
    Global::CheckDisplayElementByIDAndSetForUnlimitedDisplay(DEID_KEEP_AND_GRANERY_PLACEMENT_INFO,0)
    ;
    return;
  }
  numInGroup = whichBuildingIsMissing + 9;
  pcVar2 = Text::TextManager::getTextStringInGroupAtOffset
                     (&DAT_TextManagerObject,TEXT_FEEDBACK,numInGroup);
  iVar3 = Text::FontSizeClass::renderMultilineTextUnk
                    (DAT_TextManagerObject.fontSizeClassArray + 0x12,pcVar2,0,0,0x244,0,0,1);
  pcVar2 = Text::TextManager::getTextStringInGroupAtOffset
                     (&DAT_TextManagerObject,TEXT_FEEDBACK,numInGroup);
  iVar4 = Text::FontSizeClass::renderMultilineTextUnk
                    (DAT_TextManagerObject.fontSizeClassArray + 0x12,pcVar2,0,0,0x244,0,0,2);
  blendStrength = 0;
  fontSize = 0x12;
  color2 = 0;
  color1 = 0xccfaff;
  maxWidth = 0x244;
  iVar3 = posY - iVar3;
  iVar4 = posX - iVar4;
  pcVar2 = Text::TextManager::getTextStringInGroupAtOffset
                     (&DAT_TextManagerObject,TEXT_FEEDBACK,numInGroup);
  Text::TextManager::renderMultilineText6Unk
            (&DAT_TextManagerObject,pcVar2,iVar4,iVar3,maxWidth,color1,color2,fontSize,blendStrength
            );
  if (whichBuildingIsMissing == 1) {
    if (BOOL_RelatedToInitialGranaryAndKeepPlacement != FALSE) {
      return;
    }
                    /* "Place a keep to site your castle my liege" */
    pcVar2 = "other_warning1.wav";
  }
  else {
    if (whichBuildingIsMissing != 2) {
      return;
    }
    if (BOOL_RelatedToInitialGranaryAndKeepPlacement != FALSE) {
      return;
    }
                    /* "Site your granary sire" */
    pcVar2 = "other_warning2.wav";
  }
  Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,pcVar2);
  BOOL_RelatedToInitialGranaryAndKeepPlacement = TRUE;
  return;
}


// ================= _HoldStrong::AI::AIVState::computeAIVPlacementFit @ 004ef8c0 =================

/* WARNING: Enum "MappersEnumShort": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* returns 999999 if perfect fit, if fit is lower, than worse fit
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall _HoldStrong::AI::AIVState::computeAIVPlacementFit(AIVState *this,int playerID)

{
  AIVBuildingType2 AVar1;
  MappersEnum commandBuildingType;
  int iVar2;
  uint x;
  uint y;
  int iVar3;
  int _tile;
  AIVBuildingType2Short *_construction;
  int *_ptrStep;
  int _y;
  int _minSteps;
  
  _minSteps = 1000000;
  DAT_TileMapState.buildingPlacementProperty_7 = 0;
  DAT_TileMapState.buildingPlacementProperty_6 = 0;
  DAT_TileMapState.buildingPlacementProperty_5 = 0;
  DAT_TileMapState.buildingPlacementProperty_3 = 0;
  _y = 0;
                    /* 100x100 matrix */
  _tile = 0;
  do {
    _ptrStep = DAT_AIVState.steps[0] + _tile;
    _construction = DAT_AIVState.constructions + _tile;
    iVar3 = 0;
    do {
      AVar1 = (AIVBuildingType2)(short)*_construction;
      if (AVar1 != 0) {
        if (AVar1 == 1) {
                    /* = 1 */
          DAT_AIVState.isHandled[_tile] = (byte)*_construction;
        }
        else {
          commandBuildingType = convertAIVBuildingTypeToCommandBuildingType(&DAT_AIVState,AVar1);
          iVar2 = Map::Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType
                            (commandBuildingType);
          DAT_TileMapState.buildingHeightLimit =
               DAT_BuildingDefinedData.DAT_BuildingPlacement_HeightLimit[iVar2];
          iVar2 = Map::Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType
                            (commandBuildingType);
          DAT_TileMapState.buildingMaxHeightDifference =
               DAT_BuildingDefinedData.DAT_BuildingPlacement_MaxHeightDifference[iVar2];
          DAT_AIVState.buildingCounter = DAT_AIVState.buildingCounter + 1;
          y = DAT_AIVState.aivs[playerID].keepYOffset + _y;
          x = DAT_AIVState.aivs[playerID].keepXOffset + iVar3;
          if (((x < 400) && (y < 400)) && (*(char *)(y * 400 + 0x21aec98 + x) != '\0')) {
            iVar2 = DAT_ViewportRenderState.translationMatrix[y].addXgetTile;
            Map::TileMapState::storeMinAndMaxHeightOfArea(&DAT_TileMapState,x,y,1);
            iVar2 = Map::TileMapState::isBuildingPlacementAllowedAtTile
                              (&DAT_TileMapState,iVar2 + x,0,commandBuildingType,0);
            if (iVar2 != 0) {
              DAT_AIVState.isHandled[_tile] = 1;
              if (*_ptrStep < _minSteps) {
                _minSteps = *_ptrStep;
              }
              DAT_AIVState.invalidTileCounter = DAT_AIVState.invalidTileCounter + 1;
            }
          }
        }
      }
      _construction = _construction + 1;
      _ptrStep = _ptrStep + 1;
      iVar3 = iVar3 + 1;
      _tile = _tile + 1;
    } while (iVar3 < 100);
    _y = _y + 1;
  } while (_y < 100);
  return _minSteps + -1;
}


// ================= _HoldStrong::Map::TileMapState::validateWallPlacementAtTile @ 004f94a0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::validateWallPlacementAtTile
          (TileMapState *this,int playerID,uint x,uint y,MappersEnum param_4)

{
  uint uVar1;
  BOOLEnum BVar2;
  int iVar3;
  int iVar4;
  
  DAT_TileMapState.illegalBuild = TRUE;
  iVar4 = DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x;
  uVar1 = DAT_TileMapState.LogicLayer[iVar4];
  if ((((((uVar1 & 0x100) == 0) || ('\v' < (char)DAT_TileMapState.DamageLayer[iVar4])) &&
       ((uVar1 & 0x400) == 0)) &&
      ((DAT_TileMapState.BuildingLayer[iVar4] == 0 && ((uVar1 & 0x14) == 0)))) &&
     ((uVar1 & 0x60300081) == 0)) {
    BVar2 = Navigation::PathFindingState::isEnemyTooCloseUnk(&DAT_PathFindingState,playerID,x,y,5);
    if (BVar2 == FALSE) {
      iVar3 = Navigation::PathFindingState::findSomeSuitableLocationUnk
                        (&DAT_PathFindingState,playerID,x,y,2);
      if (iVar3 == 0) {
                    /* crenelations? */
        if ((DAT_TileMapState.UnitLayer[iVar4] != 0) &&
           ((DAT_TileMapState.LogicLayer[iVar4] & 0x100U) == 0)) {
          if (((undefined2)param_4 == M_MAPPER_CRENAL) || ((undefined2)param_4 == M_MAPPER_CRENAL2))
          {
            DAT_UnitsState.units[(short)DAT_TileMapState.UnitLayer[iVar4]].logicalState = ULS_REMOVE
            ;
          }
        }
        DAT_TileMapState.illegalBuild = FALSE;
      }
    }
  }
  return;
}


// ================= _HoldStrong::Map::TileMapState::isBuildingPlacementAllowedAtTile @ 004f9a60 =================

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


// ================= _HoldStrong::Map::TileMapState::validateBuildingPlacementAtTile @ 004f9df0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Map::TileMapState::validateBuildingPlacementAtTile
               (int param_1,int param_2,int param_3)

{
  BuildingTypeShort BVar1;
  int iVar2;
  
  DAT_TileMapState.buildingPlacementFail = FALSE;
  param_2 = DAT_ViewportRenderState.translationMatrix[param_3].addXgetTile + param_2;
  iVar2 = (int)(short)DAT_TileMapState.BuildingLayer[param_2];
  if ((iVar2 < 1) || ((DAT_BuildingsState.buildings[iVar2].owner != param_1 && (param_1 != 0)))) {
    DAT_TileMapState.buildingPlacementFail = TRUE;
  }
  if (((DAT_TileMapState.LogicLayer[param_2] & 0x100U) != 0) &&
     (DAT_TileMapState.BuildingLayer[param_2] == 0)) {
    if ((DAT_TileMapState.WallOwnerLayer[param_2] & 7) + 1 != param_1) {
      return;
    }
    DAT_TileMapState.buildingPlacementFail = FALSE;
  }
  if ((((((DAT_TileMapState.LogicLayer[param_2] & 0x10000400U) == 0) &&
        (BVar1 = DAT_BuildingsState.buildings[iVar2].buildingType, BVar1 != BT_GATEHOUSELARGE)) &&
       (BVar1 != BT_GATEHOUSESMALL)) &&
      (((BVar1 != BT_WOODGATE1 && (BVar1 != BT_WOODGATE2)) &&
       ((BVar1 != BT_KEEPDOOR && ((BVar1 != BT_DRAWBRIDGE && (BVar1 != BT_CAMPGROUND)))))))) &&
     ((BVar1 != BT_PARADEGROUND &&
      (((((BVar1 != BT_PARADEGROUND2 && (BVar1 != BT_PARADEGROUND3)) && (BVar1 != BT_PARADEGROUND4))
        && ((BVar1 != BT_PARADEGROUND5 && (BVar1 != BT_CAMPFIRE)))) && (BVar1 != BT_KILLINGPIT))))))
  {
    DAT_TileMapState.buildingPlacementFail = TRUE;
  }
  DAT_TileMapState.field131_0x554954 = iVar2;
  return;
}


// ================= _HoldStrong::Map::TileMapState::determineBuildingPlacementRotation @ 004fa000 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Map::TileMapState::determineBuildingPlacementRotation(int param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  int *piVar4;
  int *local_14;
  int local_10 [4];
  
  if (DAT_TileMapState.buildingPlacementFail != FALSE) {
    DAT_TileMapState.uiBuildingRotation = 8;
    DAT_TileMapState.field127_0x554944 = 0x80;
    return;
  }
  local_14 = local_10;
  piVar4 = DAT_TerrainDefinedData.field2465_0x1e4c;
  do {
    *local_14 = 0;
    uVar3 = piVar4[1] + param_2;
    uVar1 = *piVar4 + param_1;
    if ((((uVar1 < 400) && (uVar3 < 400)) && (*(char *)(uVar1 + 0x21aec98 + uVar3 * 400) != '\0'))
       && (((DAT_TileMapState.LogicLayer
             [DAT_ViewportRenderState.translationMatrix[uVar3].addXgetTile + *piVar4 + param_1] &
            0x100U) != 0 &&
           ((DAT_TileMapState.LogicLayer
             [DAT_ViewportRenderState.translationMatrix[uVar3].addXgetTile + *piVar4 + param_1] &
            0x802U) == 0)))) {
      *local_14 = 1;
    }
    uVar3 = piVar4[3] + param_2;
    uVar1 = piVar4[2] + param_1;
    if (((uVar1 < 400) && (uVar3 < 400)) &&
       ((*(char *)(uVar1 + 0x21aec98 + uVar3 * 400) != '\0' &&
        (((DAT_TileMapState.LogicLayer
           [DAT_ViewportRenderState.translationMatrix[uVar3].addXgetTile + piVar4[2] + param_1] &
          0x100U) != 0 &&
         ((DAT_TileMapState.LogicLayer
           [DAT_ViewportRenderState.translationMatrix[uVar3].addXgetTile + piVar4[2] + param_1] &
          0x802U) == 0)))))) {
      *local_14 = *local_14 + 1;
    }
    uVar3 = piVar4[5] + param_2;
    uVar1 = piVar4[4] + param_1;
    if ((((uVar1 < 400) && (uVar3 < 400)) && (*(char *)(uVar1 + 0x21aec98 + uVar3 * 400) != '\0'))
       && (((DAT_TileMapState.LogicLayer
             [DAT_ViewportRenderState.translationMatrix[uVar3].addXgetTile + piVar4[4] + param_1] &
            0x100U) != 0 &&
           ((DAT_TileMapState.LogicLayer
             [DAT_ViewportRenderState.translationMatrix[uVar3].addXgetTile + piVar4[4] + param_1] &
            0x802U) == 0)))) {
      *local_14 = *local_14 + 1;
    }
    uVar3 = piVar4[7] + param_2;
    uVar1 = piVar4[6] + param_1;
    if (((uVar1 < 400) && (uVar3 < 400)) &&
       ((*(char *)(uVar1 + 0x21aec98 + uVar3 * 400) != '\0' &&
        (((DAT_TileMapState.LogicLayer
           [DAT_ViewportRenderState.translationMatrix[uVar3].addXgetTile + piVar4[6] + param_1] &
          0x100U) != 0 &&
         ((DAT_TileMapState.LogicLayer
           [DAT_ViewportRenderState.translationMatrix[uVar3].addXgetTile + piVar4[6] + param_1] &
          0x802U) == 0)))))) {
      *local_14 = *local_14 + 1;
    }
    local_14 = local_14 + 1;
    piVar4 = piVar4 + 8;
  } while ((int)piVar4 < 0xb4ae20);
  if (local_10[0] == 4) {
    if (local_10[3] == 4) {
      DAT_TileMapState.uiBuildingRotation = 7;
      goto LAB_004fa291;
    }
    if (local_10[1] == 4) {
      DAT_TileMapState.uiBuildingRotation = 1;
      goto LAB_004fa291;
    }
  }
  if (local_10[2] == 4) {
    if (local_10[3] == 4) {
      DAT_TileMapState.uiBuildingRotation = 5;
      goto LAB_004fa291;
    }
    if (local_10[1] == 4) {
      DAT_TileMapState.uiBuildingRotation = 3;
      goto LAB_004fa291;
    }
  }
  if (local_10[0] == 4) {
    DAT_TileMapState.uiBuildingRotation = 0;
  }
  else if (local_10[1] == 4) {
    DAT_TileMapState.uiBuildingRotation = 2;
  }
  else if (local_10[2] == 4) {
    DAT_TileMapState.uiBuildingRotation = 4;
  }
  else if (local_10[3] == 4) {
    DAT_TileMapState.uiBuildingRotation = 6;
  }
  else {
    DAT_TileMapState.uiBuildingRotation = 8;
  }
LAB_004fa291:
  if (DAT_TileMapState.uiBuildingRotation == 8) {
    iVar2 = 8;
  }
  else {
    iVar2 = DAT_TileMapState.uiBuildingRotation - DAT_TileMapState.mapOrientation;
    if (iVar2 < 0) {
      DAT_TileMapState.field127_0x554944 = (iVar2 + 8) * 0x10;
      return;
    }
  }
  DAT_TileMapState.field127_0x554944 = iVar2 << 4;
  return;
}


// ================= _HoldStrong::Map::TileMapState::checkDrawbridgePlacement @ 004fa2d0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::checkDrawbridgePlacement(TileMapState *this,int x,int y)

{
  uint uVar1;
  BuildingTypeShort BVar2;
  short sVar3;
  uint uVar4;
  int iVar5;
  XYPair *pXVar6;
  int iVar7;
  int iVar8;
  int local_2c;
  XYPair *local_28;
  int _buildings [9];
  
  if (DAT_TileMapState.buildingPlacementFail != FALSE) {
    return;
  }
  DAT_TileMapState.buildingPlacementFail = TRUE;
  local_2c = 0;
  local_28 = DAT_TerrainDefinedData.drawBridgeOffsets[0];
  do {
    iVar8 = 0;
    pXVar6 = local_28;
    do {
      uVar4 = pXVar6->y + y;
      iVar5 = ((XYPair *)&pXVar6->x)->x;
      uVar1 = iVar5 + x;
      _buildings[iVar8] = 0;
      if ((((399 < uVar1) || (399 < uVar4)) || (*(char *)(uVar4 * 400 + 0x21aec98 + uVar1) == '\0'))
         || (iVar5 = DAT_ViewportRenderState.translationMatrix[uVar4].addXgetTile + iVar5 + x,
            (DAT_TileMapState.LogicLayer[iVar5] & 0x30) != 0)) break;
      _buildings[iVar8] = (int)(short)DAT_TileMapState.BuildingLayer[iVar5];
      iVar8 = iVar8 + 1;
      pXVar6 = pXVar6 + 1;
    } while (iVar8 < 9);
    if ((_buildings[0] != 0) &&
       (DAT_BuildingsState.buildings[_buildings[0]].logicalState == BLS_NORMAL)) {
      BVar2 = DAT_BuildingsState.buildings[_buildings[0]].buildingType;
      if (BVar2 == BT_GATEHOUSELARGE) {
        iVar8 = 7;
      }
      else {
        if (BVar2 != BT_GATEHOUSESMALL) goto LAB_004fa405;
        iVar8 = 5;
      }
      sVar3 = DAT_BuildingsState.buildings[_buildings[0]].buildingVariation;
      if (sVar3 == 0x51) {
        if ((local_2c != 1) && (local_2c != 3)) {
LAB_004fa3e9:
          iVar5 = 0;
          iVar7 = 0;
          if (iVar8 != 0) {
            do {
              if (_buildings[iVar5] == _buildings[0]) {
                iVar7 = iVar7 + 1;
              }
              iVar5 = iVar5 + 1;
            } while (iVar5 < iVar8);
          }
          if (iVar7 == iVar8) {
            DAT_TileMapState.buildingPlacementFail = FALSE;
            DAT_TileMapState.uiBuildingRotation = local_2c * 2;
            DAT_TileMapState.field127_0x554944 = local_2c * 0x32;
            return;
          }
        }
      }
      else if ((sVar3 != 0x50) || ((local_2c != 0 && (local_2c != 2)))) goto LAB_004fa3e9;
    }
LAB_004fa405:
    local_2c = local_2c + 1;
    local_28 = local_28 + 9;
    if (0xb4af3f < (int)local_28) {
      return;
    }
  } while( true );
}


// ================= _HoldStrong::Map::TileMapState::renderWallPlacementPreview @ 004fb9e0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::renderWallPlacementPreview
          (TileMapState *this,uint x,uint y,short param_3)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int extraout_ECX;
  int extraout_ECX_00;
  short sVar4;
  short sVar5;
  int iVar6;
  
  iVar6 = 0;
  sVar4 = 0;
  sVar5 = 0;
  if (399 < x) {
    return;
  }
  if (399 < y) {
    return;
  }
  if (*(char *)(y * 400 + 0x21aec98 + x) == '\0') {
    return;
  }
  DAT_TileMapState.buildingPlacementFail = FALSE;
  if (param_3 == 0) {
    sVar5 = 1;
    sVar4 = 0x211;
  }
  else if (param_3 == 1) {
    sVar5 = 1;
    sVar4 = 0x215;
  }
  else if (param_3 == 2) {
    sVar5 = 1;
    sVar4 = 0x219;
  }
  else if (param_3 == 3) {
    sVar5 = 1;
    sVar4 = 0x21d;
  }
  else if (param_3 == 4) {
    sVar5 = 2;
    sVar4 = 0x1d1;
  }
  else if (param_3 == 5) {
    sVar5 = 2;
    sVar4 = 0x1e1;
  }
  else if (param_3 == 6) {
    sVar5 = 2;
    sVar4 = 0x1f1;
  }
  else if (param_3 == 7) {
    sVar5 = 2;
    sVar4 = 0x201;
  }
  else if (param_3 == 8) {
    sVar5 = 3;
    sVar4 = 0x141;
  }
  else if (param_3 == 9) {
    sVar5 = 3;
    sVar4 = 0x165;
  }
  else if (param_3 == 10) {
    sVar5 = 3;
    sVar4 = 0x189;
  }
  else if (param_3 == 0xb) {
    sVar5 = 3;
    sVar4 = 0x1ad;
  }
  else {
    if (param_3 == 0xc) {
      sVar4 = 0x41;
    }
    else if (param_3 == 0xd) {
      sVar4 = 0x81;
    }
    else if (param_3 == 0xe) {
      sVar4 = 0xc1;
    }
    else {
      if (param_3 != 0xf) goto LAB_004fbb47;
      sVar4 = 0x101;
    }
    sVar5 = 4;
  }
LAB_004fbb47:
  iVar2 = DAT_TileMapState.rockOrientation + DAT_TileMapState.mapOrientation;
  if (DAT_TileMapState.field80_0x554894 == 5) {
    iVar2 = DAT_TileMapState.mapOrientation;
  }
  if (7 < iVar2) {
    iVar2 = iVar2 + -8;
  }
  do {
    getBuildingSizeIndexMappingData(iVar6,sVar5);
    iVar3 = DAT_ViewportRenderState.translationMatrix[*(int *)(extraout_ECX + 0x554990) + y].
            addXgetTile + *(int *)(extraout_ECX + 0x55498c) + x;
    uVar1 = *(uint *)(extraout_ECX + 0x165160 + iVar3 * 4);
    if ((uVar1 & 0x30) != 0) {
      return;
    }
    if ((uVar1 & 0x400) != 0) {
      return;
    }
    if (*(short *)(extraout_ECX + 0x1db590 + iVar3 * 2) != 0) {
      return;
    }
    iVar6 = iVar6 + 1;
  } while (iVar6 < *(int *)(extraout_ECX + 0x554984));
  iVar6 = 0;
  do {
    getBuildingSizeIndexMappingData(iVar6,sVar5);
    iVar6 = iVar6 + 1;
    *(short *)(extraout_ECX_00 + 0xa0cc0 +
              (DAT_ViewportRenderState.translationMatrix[*(int *)(extraout_ECX_00 + 0x554990) + y].
               addXgetTile + *(int *)(extraout_ECX_00 + 0x55498c) + x) * 2) =
         *(short *)(extraout_ECX_00 + 0x554994) + (short)GMTotalPicturesProcessed[0x38] +
         (short)(iVar2 / 2) * sVar5 * sVar5 + sVar4 + -1;
  } while (iVar6 < *(int *)(extraout_ECX_00 + 0x554984));
  return;
}


// ================= _HoldStrong::Map::TileMapState::isTileSuitableForBrushPlacement @ 004fbe70 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::TileMapState::isTileSuitableForBrushPlacement
          (TileMapState *this,int tile,uint x,uint y)

{
  uint uVar1;
  uint uVar2;
  byte bVar3;
  BOOLEnum BVar4;
  
  bVar3 = DAT_TileMapState.HeightLayer[tile];
  uVar1 = y - 1;
  if ((((((399 < x) || (399 < uVar1)) || (*(char *)(uVar1 * 400 + 0x21aec98 + x) == '\0')) ||
       ((uint)bVar3 ==
        (uint)DAT_TileMapState.HeightLayer
              [DAT_ViewportRenderState.translationMatrix[y - 1].addXgetTile + x] ||
        (int)((uint)bVar3 -
             (uint)DAT_TileMapState.HeightLayer
                   [DAT_ViewportRenderState.translationMatrix[y - 1].addXgetTile + x]) < 0)) &&
      ((uVar2 = x + 1, 399 < uVar2 ||
       ((((399 < uVar1 || (*(char *)(uVar1 * 400 + 0x21aec98 + uVar2) == '\0')) ||
         ((uint)bVar3 ==
          (uint)DAT_TileMapState.HeightLayer
                [DAT_ViewportRenderState.translationMatrix[y - 1].addXgetTile + x + 1] ||
          (int)((uint)bVar3 -
               (uint)DAT_TileMapState.HeightLayer
                     [DAT_ViewportRenderState.translationMatrix[y - 1].addXgetTile + x + 1]) < 0))
        && (((399 < uVar2 || (399 < y)) ||
            ((*(char *)(y * 400 + 0x21aec98 + uVar2) == '\0' ||
             ((uint)bVar3 ==
              (uint)DAT_TileMapState.HeightLayer
                    [DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x + 1] ||
              (int)((uint)bVar3 -
                   (uint)DAT_TileMapState.HeightLayer
                         [DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x + 1]) < 0))))
           )))))) &&
     ((((((uVar1 = y + 1, 399 < uVar2 || (399 < uVar1)) ||
         (*(char *)(uVar1 * 400 + 0x21aec98 + uVar2) == '\0')) ||
        ((uint)bVar3 ==
         (uint)DAT_TileMapState.HeightLayer
               [DAT_ViewportRenderState.translationMatrix[y + 1].addXgetTile + x + 1] ||
         (int)((uint)bVar3 -
              (uint)DAT_TileMapState.HeightLayer
                    [DAT_ViewportRenderState.translationMatrix[y + 1].addXgetTile + x + 1]) < 0)) &&
       (((399 < x || (399 < uVar1)) ||
        ((*(char *)(uVar1 * 400 + 0x21aec98 + x) == '\0' ||
         ((uint)bVar3 ==
          (uint)DAT_TileMapState.HeightLayer
                [DAT_ViewportRenderState.translationMatrix[y + 1].addXgetTile + x] ||
          (int)((uint)bVar3 -
               (uint)DAT_TileMapState.HeightLayer
                     [DAT_ViewportRenderState.translationMatrix[y + 1].addXgetTile + x]) < 0))))))
      && ((uVar2 = x - 1, 399 < uVar2 ||
          ((((399 < uVar1 || (*(char *)(uVar1 * 400 + 0x21aec98 + uVar2) == '\0')) ||
            ((uint)bVar3 ==
             (uint)(byte)DAT_TileMapState.EntityLayerLT25
                         [DAT_ViewportRenderState.translationMatrix[y + 1].addXgetTile + x + 0x13a0f
                         ] ||
             (int)((uint)bVar3 -
                  (uint)(byte)DAT_TileMapState.EntityLayerLT25
                              [DAT_ViewportRenderState.translationMatrix[y + 1].addXgetTile + x +
                               0x13a0f]) < 0)) &&
           ((((399 < uVar2 || (399 < y)) || (*(char *)(y * 400 + 0x21aec98 + uVar2) == '\0')) ||
            ((uint)bVar3 ==
             (uint)(byte)DAT_TileMapState.EntityLayerLT25
                         [DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x + 0x13a0f] ||
             (int)((uint)bVar3 -
                  (uint)(byte)DAT_TileMapState.EntityLayerLT25
                              [DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x +
                               0x13a0f]) < 0)))))))))) {
    BVar4 = Rendering::ViewportRenderState::xyAreValid(&DAT_ViewportRenderState,uVar2,y - 1);
    if ((BVar4 == FALSE) ||
       ((int)((uint)bVar3 -
             (uint)(byte)DAT_TileMapState.EntityLayerLT25
                         [DAT_ViewportRenderState.translationMatrix[y - 1].addXgetTile + x + 0x13a0f
                         ]) < 1)) {
      return FALSE;
    }
  }
  return TRUE;
}


// ================= _HoldStrong::Map::WallAndPitchState::resetWallPlacementInfo @ 00500d30 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Map::WallAndPitchState::resetWallPlacementInfo(WallAndPitchState *this)

{
  if ((DAT_GameCore.gameMode_2 != GM_SKIRMISH_AND_MULTIPLAYER) &&
     (DAT_GameCore.gameMode_2 != GM_SIEGE_THAT)) {
    DAT_WallAndPitchState.state = 3;
    DAT_WallAndPitchState.countdown = 400;
    DAT_WallAndPitchState.index = 0;
    DAT_WallAndPitchState.counter = 0;
    DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
  }
  return;
}


// ================= _HoldStrong::Map::WallAndPitchState::addWallPlacementInfoForTile @ 00500d60 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::WallAndPitchState::addWallPlacementInfoForTile(WallAndPitchState *this,int tile)

{
  if (((DAT_GameCore.gameMode_2 != GM_SKIRMISH_AND_MULTIPLAYER) &&
      (DAT_GameCore.gameMode_2 != GM_SIEGE_THAT)) && (DAT_WallAndPitchState.index < 100)) {
    DAT_WallAndPitchState.wallPlacementInfoArray[DAT_WallAndPitchState.index].tile_OR_pitchID = tile
    ;
    DAT_WallAndPitchState.wallPlacementInfoArray[DAT_WallAndPitchState.index].height =
         DAT_TileMapState.HeightLayer[tile];
    DAT_WallAndPitchState.wallPlacementInfoArray[DAT_WallAndPitchState.index].logic =
         DAT_TileMapState.LogicLayer[tile] & 0x470b00;
    DAT_WallAndPitchState.wallPlacementInfoArray[DAT_WallAndPitchState.index].damage =
         DAT_TileMapState.DamageLayer[tile];
    DAT_WallAndPitchState.index = DAT_WallAndPitchState.index + 1;
  }
  return;
}


// ================= _HoldStrong::Map::TileMapState::spreadFlagPlacementAlgorithm @ 00501180 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::spreadFlagPlacementAlgorithm
          (TileMapState *this,int param_1,uint param_2,uint param_3)

{
  Navigation::PathFindingState::spreadAlgorithmForFlagsAndBraziersUnk
            (&DAT_PathFindingState,param_1,param_2,param_3,4,0);
  return;
}


// ================= _HoldStrong::Map::TileMapState::spreadBrazierPlacementAlgorithm @ 005011a0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::spreadBrazierPlacementAlgorithm
          (TileMapState *this,int playerID,uint x,uint y)

{
  Navigation::PathFindingState::spreadAlgorithmForFlagsAndBraziersUnk
            (&DAT_PathFindingState,playerID,x,y,4,1);
  return;
}


// ================= _HoldStrong::Map::TileMapState::evaluateBuildingPlacementAtCursor @ 00504a30 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::evaluateBuildingPlacementAtCursor
          (TileMapState *this,int playerID,uint x,uint y)

{
  BuildingTypeShort BVar1;
  BOOLEnum BVar2;
  uint uVar3;
  int iVar4;
  int local_4;
  
  uVar3 = x;
  local_4 = 0;
  if (((399 < x) || (399 < y)) || (*(char *)(y * 400 + 0x21aec98 + x) == '\0')) {
    DAT_TileMapState.buildingPlacementFail = TRUE;
    return;
  }
  DAT_TileMapState.buildingPlacementFail = FALSE;
  if (DAT_ViewportRenderState.viewportState.field15_0x3c != 0) {
    local_4 = DAT_ViewportRenderState.viewportState.field24_0x60;
    DAT_TileMapState.field153_0x5549a0 = DAT_ViewportRenderState.viewportState.field24_0x60;
  }
  if (DAT_TileMapState.flatViewToggleValue1 == 0) {
    x = DAT_ViewportRenderState.viewportState.mouseRayBuildingID;
    iVar4 = DAT_ViewportRenderState.viewportState.field21_0x54;
LAB_00504ae2:
    if (x != 0) goto LAB_00504ae6;
  }
  else {
    x = (uint)(short)DAT_TileMapState.BuildingLayer[DAT_ViewportRenderState.viewportState.mouseTile]
    ;
    iVar4 = 0;
    if ((DAT_TileMapState.LogicLayer[DAT_ViewportRenderState.viewportState.mouseTile] & 0x100U) == 0
       ) goto LAB_00504ae2;
    if (((DAT_TileMapState.LogicLayer[DAT_ViewportRenderState.viewportState.mouseTile] & 2U) == 0)
       || (x == 0)) {
      DAT_ViewportRenderState.viewportState.field21_0x54 =
           DAT_ViewportRenderState.viewportState.mouseTile;
      iVar4 = DAT_ViewportRenderState.viewportState.mouseTile;
      goto LAB_00504ae2;
    }
LAB_00504ae6:
    uVar3 = (uint)(short)DAT_BuildingsState.buildings[x].x;
    y = (uint)(short)DAT_BuildingsState.buildings[x].y;
  }
  if (((DAT_GameCore.gameMode_2 != GM_EDITOR) && (DAT_GameCore.gameMode_2 != GM_SIEGE_THAT)) &&
     (BVar2 = Navigation::PathFindingState::isEnemyTooCloseUnk
                        (&DAT_PathFindingState,playerID,uVar3,y,
                         (-(uint)(DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &
                         0xfffffff1) + 0x1e), BVar2 != FALSE)) {
    DAT_TileMapState.field194_0x554a20 = 1;
    DAT_TileMapState.buildingPlacementFail = TRUE;
    DAT_TileMapState.buildingPlacementFailReason = 0x14;
    if (x != 0) {
      if (DAT_BuildingsState.buildings[x].owner == playerID) {
        DAT_TileMapState.buildingPlacementFail = TRUE;
        DAT_TileMapState.buildingPlacementFailReason = 0x14;
        DAT_TileMapState.field194_0x554a20 = 1;
        return;
      }
      if (playerID != 0) {
        DAT_TileMapState.buildingPlacementFailReason = BFRE_DEFAULT_CANT_PLACE_THAT_THERE;
        return;
      }
      DAT_TileMapState.buildingPlacementFail = TRUE;
      DAT_TileMapState.buildingPlacementFailReason = 0x14;
      DAT_TileMapState.field194_0x554a20 = 1;
      return;
    }
    if (0 < iVar4) {
      if ((DAT_TileMapState.LogicLayer[iVar4] & 0x100U) == 0) {
        DAT_TileMapState.buildingPlacementFail = TRUE;
        DAT_TileMapState.buildingPlacementFailReason = 0x14;
        DAT_TileMapState.field194_0x554a20 = 1;
        return;
      }
      if ((DAT_TileMapState.WallOwnerLayer[iVar4] & 7) + 1 != playerID) {
        DAT_TileMapState.buildingPlacementFailReason = BFRE_DEFAULT_CANT_PLACE_THAT_THERE;
        return;
      }
      DAT_TileMapState.buildingPlacementFail = TRUE;
      DAT_TileMapState.buildingPlacementFailReason = 0x14;
      DAT_TileMapState.field194_0x554a20 = 1;
      return;
    }
    if ((0 < local_4) && ((DAT_TileMapState.LogicLayer[local_4] & 0x40000000U) != 0)) {
      iVar4 = returnOwnedMoatAtTile(&DAT_TileMapState,local_4);
      if (iVar4 == 0) {
        return;
      }
      if (DAT_GameState.mapAndTime.playerTeams[(char)DAT_TileMapState.moats[iVar4].owner] ==
          DAT_GameState.mapAndTime.playerTeams[playerID]) {
        return;
      }
    }
    DAT_TileMapState.buildingPlacementFailReason = BFRE_DEFAULT_CANT_PLACE_THAT_THERE;
    return;
  }
  if (DAT_ViewportRenderState.viewportState.somePitchDitchID != 0) {
    if (DAT_TileMapState.pitchDitches[DAT_ViewportRenderState.viewportState.somePitchDitchID].owner
        != DAT_GameSynchronyState.currentPlayerSlotID) {
      DAT_TileMapState.buildingPlacementFail = TRUE;
      return;
    }
    DAT_TileMapState.field131_0x554954 = -DAT_ViewportRenderState.viewportState.somePitchDitchID;
    return;
  }
  if (((int)x < 1) || ((DAT_BuildingsState.buildings[x].owner != playerID && (playerID != 0)))) {
    DAT_TileMapState.buildingPlacementFail = TRUE;
  }
  if (iVar4 < 1) {
LAB_00504d0f:
    if (((local_4 < 1) || ((DAT_TileMapState.LogicLayer[local_4] & 0x40000000U) == 0)) || (x != 0))
    {
      if ((DAT_TileMapState.field151_0x554998 != 0) || (DAT_TileMapState.field152_0x55499c != 0))
      goto LAB_00504da2;
    }
    else if (DAT_TileMapState.field151_0x554998 == 0) {
      iVar4 = returnOwnedMoatAtTile(&DAT_TileMapState,local_4);
      if (iVar4 == 0) {
        return;
      }
      if (DAT_GameState.mapAndTime.playerTeams[(char)DAT_TileMapState.moats[iVar4].owner] !=
          DAT_GameState.mapAndTime.playerTeams[playerID]) {
        return;
      }
      DAT_TileMapState.field152_0x55499c = 1;
      DAT_TileMapState.buildingPlacementFail =
           (BOOLEnum)((DAT_TileMapState.MiscDisplayLayer[local_4] & 0x400) != 0);
      iVar4 = local_4;
    }
    else {
LAB_00504da2:
      DAT_TileMapState.buildingPlacementFail = TRUE;
    }
  }
  else {
    uVar3 = DAT_TileMapState.LogicLayer[iVar4] & 0x100;
    if ((uVar3 != 0) && ((DAT_TileMapState.LogicLayer[iVar4] & 2U) != 0)) {
      DAT_TileMapState.buildingPlacementFail = TRUE;
      return;
    }
    if (((uVar3 == 0) || (DAT_TileMapState.BuildingLayer[iVar4] != 0)) ||
       (DAT_TileMapState.field152_0x55499c != 0)) goto LAB_00504d0f;
    if ((DAT_TileMapState.WallOwnerLayer[iVar4] & 7) + 1 != playerID) {
      return;
    }
    DAT_TileMapState.buildingPlacementFail = FALSE;
    DAT_TileMapState.field151_0x554998 = 1;
    if ((DAT_TileMapState.MiscDisplayLayer[iVar4] & 0x400) != 0) {
      DAT_TileMapState.buildingPlacementFail = TRUE;
    }
  }
  if ((0 < iVar4) && (DAT_TileMapState.UnitLayer[iVar4] != 0)) {
    DAT_TileMapState.buildingPlacementFail = TRUE;
  }
  if (x == 0) goto LAB_00504e15;
  if (DAT_GameCore.gameMode_2 != GM_EDITOR) {
    if (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) {
      if (DAT_BuildingsState.buildings[x].buildingType == BT_SIGNPOST)
      goto switchD_00504ded_caseD_27;
    }
    else {
      switch(DAT_BuildingsState.buildings[x].buildingType) {
      case BT_UNKNOWN1:
      case BT_MANORHOUSE:
      case BT_STONEKEEP:
      case BT_STRONGHOLD:
      case BT_SIGNPOST:
      case BT_CAMPGROUND:
      case BT_KEEPDOOR_LEFT:
      case BT_KEEPDOOR_RIGHT:
      case BT_KEEPDOOR:
      case BT_POND:
switchD_00504ded_caseD_27:
        DAT_TileMapState.buildingPlacementFail = TRUE;
      }
    }
  }
  if ((int)x < 0) {
    DAT_TileMapState.field131_0x554954 = x;
    return;
  }
LAB_00504e15:
  if ((((((((DAT_TileMapState.LogicLayer
             [DAT_BuildingsState.buildings[x].currentTilePositionAdjusted] & 0x10000400U) == 0) &&
          (BVar1 = DAT_BuildingsState.buildings[x].buildingType, BVar1 != BT_GATEHOUSELARGE)) &&
         (BVar1 != BT_GATEHOUSESMALL)) && ((BVar1 != BT_WOODGATE1 && (BVar1 != BT_WOODGATE2)))) &&
       ((BVar1 != BT_KEEPDOOR && ((BVar1 != BT_DRAWBRIDGE && (BVar1 != BT_KILLINGPIT)))))) &&
      (DAT_TileMapState.field151_0x554998 == 0)) && (DAT_TileMapState.field152_0x55499c == 0)) {
    DAT_TileMapState.buildingPlacementFail = TRUE;
  }
  DAT_TileMapState.field131_0x554954 = x;
  return;
}


// ================= _HoldStrong::Map::TileMapState::updateBuildingPlacementRotationPreview @ 00504ee0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::updateBuildingPlacementRotationPreview
          (TileMapState *this,int param_1,int param_2)

{
  BOOLEnum BVar1;
  int extraout_ECX;
  
  BVar1 = DAT_TileMapState.buildingPlacementFail;
  DAT_TileMapState.buildingPlacementFail = FALSE;
  determineBuildingPlacementRotation(param_1,param_2);
  *(BOOLEnum *)(extraout_ECX + 0x554934) = BVar1;
  return;
}


// ================= _HoldStrong::Map::TileMapState::setConstructionGFXLayerBasedOnPlacementChecks @ 00504f10 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::TileMapState::setConstructionGFXLayerBasedOnPlacementChecks
          (TileMapState *this,int x,int y,MappersEnum type,int size)

{
  int iVar1;
  undefined2 uVar7;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  ushort uVar8;
  TileMapState *this_00;
  XYPair *pXVar9;
  int *piVar10;
  int iVar11;
  MappersEnum commandBuildingType;
  int iVar12;
  int iVar13;
  int iVar14;
  bool bVar15;
  undefined8 uVar16;
  int local_14;
  
  iVar13 = x;
  iVar11 = DAT_TileMapState.field188_0x554a14;
  bVar15 = DAT_TileMapState.field188_0x554a14 == 0;
  local_14 = 0;
  DAT_TileMapState.field188_0x554a14 = 0;
  if (bVar15) {
    if (DAT_TileMapState.buildingPlacementFail == 2) {
      DAT_TileMapState.field188_0x554a14 = 0;
      return 2;
    }
    if (DAT_TileMapState.buildingPlacementFail != FALSE) {
      do {
        getBuildingSizeIndexMappingData(local_14,size);
        iVar11 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + y].
                 addXgetTile + DAT_TileMapState.buildingX + x;
        if ((DAT_TileMapState.LogicLayer[iVar11] & 0x10000500U) == 0) {
          iVar1 = isBuildingPlacementAllowedAtTile
                            (&DAT_TileMapState,iVar11,DAT_GameSynchronyState.currentPlayerSlotID,
                             (int)(short)(undefined2)type,0);
          DAT_TileMapState.ConstructionGFXLayer[iVar11] = (-(ushort)(iVar1 != 0) & 0xfff9) + 0x3e;
        }
        local_14 = local_14 + 1;
      } while (local_14 < DAT_TileMapState.constructionTileCount);
      uVar7 = (undefined2)((uint)local_14 >> 0x10);
      if ((((undefined2)type == M_MAPPER_KEEP1) || ((undefined2)type == M_MAPPER_KEEP2)) ||
         ((undefined2)type == M_MAPPER_KEEP3)) {
        piVar10 = (int *)((int)&DAT_TerrainDefinedData +
                         ((short)(undefined2)type + -0x3c) * 0x60 + 0x264);
        x = 3;
        do {
          iVar11 = DAT_ViewportRenderState.translationMatrix[piVar10[1] + y].addXgetTile + *piVar10
                   + iVar13;
          if ((DAT_TileMapState.LogicLayer[iVar11] & 0x10000500U) == 0) {
            iVar1 = isBuildingPlacementAllowedAtTile
                              (&DAT_TileMapState,iVar11,DAT_GameSynchronyState.currentPlayerSlotID,
                               (int)(short)(undefined2)type,0);
            DAT_TileMapState.ConstructionGFXLayer[iVar11] = (-(ushort)(iVar1 != 0) & 0xfff9) + 0x3e;
          }
          piVar10 = piVar10 + 2;
          x = x + -1;
        } while (x != 0);
        iVar12 = ((short)(undefined2)type + -0x3c) * 0x20;
        iVar11 = *(int *)((int)&DAT_TerrainDefinedData + iVar12 + 900);
        iVar1 = *(int *)((int)&DAT_TerrainDefinedData + iVar12 + 0x388);
        local_14 = 0;
        do {
          getBuildingSizeIndexMappingData(local_14,7);
          iVar2 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + y + iVar1].
                  addXgetTile + DAT_TileMapState.buildingX + iVar13 + iVar11;
          if ((DAT_TileMapState.LogicLayer[iVar2] & 0x10000500U) == 0) {
            iVar3 = isBuildingPlacementAllowedAtTile
                              (&DAT_TileMapState,iVar2,DAT_GameSynchronyState.currentPlayerSlotID,
                               (int)(short)(undefined2)type,0);
            DAT_TileMapState.ConstructionGFXLayer[iVar2] = (-(ushort)(iVar3 != 0) & 0xfff9) + 0x3e;
          }
          local_14 = local_14 + 1;
        } while (local_14 < DAT_TileMapState.constructionTileCount);
        iVar11 = *(int *)((int)&DAT_TerrainDefinedData + iVar12 + 0x3e4);
        iVar1 = *(int *)((int)&DAT_TerrainDefinedData + iVar12 + 1000);
        iVar12 = 0;
        do {
          getBuildingSizeIndexMappingData(iVar12,5);
          iVar2 = DAT_TileMapState.buildingY + iVar1 + y;
          iVar3 = DAT_ViewportRenderState.translationMatrix[iVar2].addXgetTile +
                  DAT_TileMapState.buildingX + iVar11 + iVar13;
          if ((DAT_TileMapState.LogicLayer[iVar3] & 0x10000500U) == 0) {
            iVar2 = isBuildingPlacementAllowedAtTile
                              (this_00,iVar3,DAT_GameSynchronyState.currentPlayerSlotID,
                               (int)(short)(undefined2)type,0);
            iVar2 = (-(uint)(iVar2 != 0) & 0xfffffff9) + 0x3e;
            DAT_TileMapState.ConstructionGFXLayer[iVar3] = (ushort)iVar2;
          }
          uVar7 = (undefined2)((uint)iVar2 >> 0x10);
          iVar12 = iVar12 + 1;
        } while (iVar12 < DAT_TileMapState.constructionTileCount);
      }
      if ((((undefined2)type == M_MAPPER_GATE_WOOD1A) || ((undefined2)type == M_MAPPER_GATE_WOOD1B))
         || (((undefined2)type == M_MAPPER_GATE_WOOD1C || ((undefined2)type == M_MAPPER_GATE_WOOD1D)
             ))) {
        commandBuildingType = (MappersEnum)(short)(undefined2)type;
        iVar11 = commandBuildingType * 3 + -0x1a4;
        iVar1 = *(int *)((int)&DAT_TerrainDefinedData + iVar11 * 8 + 0x56c);
        iVar11 = iVar11 * 8;
        iVar12 = *(int *)((int)&DAT_TerrainDefinedData + iVar11 + 0x570);
        iVar2 = 0;
        do {
          getBuildingSizeIndexMappingData(iVar2,3);
          iVar4 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + iVar12 + y]
                  .addXgetTile + DAT_TileMapState.buildingX + iVar1 + iVar13;
          iVar3 = isBuildingPlacementAllowedAtTile
                            (&DAT_TileMapState,iVar4,DAT_GameSynchronyState.currentPlayerSlotID,
                             commandBuildingType,0);
          iVar2 = iVar2 + 1;
          DAT_TileMapState.ConstructionGFXLayer[iVar4] = (-(ushort)(iVar3 != 0) & 0xfff9) + 0x3e;
        } while (iVar2 < DAT_TileMapState.constructionTileCount);
        iVar1 = *(int *)((int)&DAT_TerrainDefinedData + iVar11 + 0x578);
        iVar11 = *(int *)((int)&DAT_TerrainDefinedData + iVar11 + 0x57c);
        iVar12 = 0;
        do {
          getBuildingSizeIndexMappingData(iVar12,3);
          iVar3 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + iVar11 + y]
                  .addXgetTile + DAT_TileMapState.buildingX + iVar1 + iVar13;
          iVar2 = isBuildingPlacementAllowedAtTile
                            (&DAT_TileMapState,iVar3,DAT_GameSynchronyState.currentPlayerSlotID,
                             commandBuildingType,0);
          iVar12 = iVar12 + 1;
          DAT_TileMapState.ConstructionGFXLayer[iVar3] = (-(ushort)(iVar2 != 0) & 0xfff9) + 0x3e;
        } while (iVar12 < DAT_TileMapState.constructionTileCount);
        piVar10 = (int *)((int)&DAT_TerrainDefinedData +
                         (commandBuildingType * 3 + -0x1a4) * 0x10 + 0x5cc);
        type = M_MAPPER_FOREST;
        do {
          iVar1 = DAT_ViewportRenderState.translationMatrix[piVar10[1] + y].addXgetTile + *piVar10 +
                  iVar13;
          iVar11 = isBuildingPlacementAllowedAtTile
                             (&DAT_TileMapState,iVar1,DAT_GameSynchronyState.currentPlayerSlotID,
                              commandBuildingType,0);
          iVar11 = (-(uint)(iVar11 != 0) & 0xfffffff9) + 0x3e;
          piVar10 = piVar10 + 2;
          type = type - M_MAPPER_AREA;
          DAT_TileMapState.ConstructionGFXLayer[iVar1] = (ushort)iVar11;
        } while (type != M_MAPPER_NULL);
        return iVar11;
      }
      if (((undefined2)type == M_MAPPER_BARRACKS_EURO) ||
         ((undefined2)type == M_MAPPER_BARRACKS_ARAB)) {
        iVar11 = 0;
        do {
          getBuildingSizeIndexMappingData(iVar11,5);
          iVar12 = DAT_TileMapState.buildingX;
          iVar1 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + y].
                  addXgetTile;
          if ((DAT_TileMapState.LogicLayer[iVar13 + DAT_TileMapState.buildingX + iVar1 + 5] &
              0x10000500U) == 0) {
            iVar2 = isBuildingPlacementAllowedAtTile
                              (&DAT_TileMapState,iVar1 + DAT_TileMapState.buildingX + iVar13 + 5,
                               DAT_GameSynchronyState.currentPlayerSlotID,
                               (int)(short)(undefined2)type,0);
            DAT_TileMapState.ConstructionGFXLayer[iVar13 + iVar12 + iVar1 + 5] =
                 (-(ushort)(iVar2 != 0) & 0xfff9) + 0x3e;
          }
          iVar11 = iVar11 + 1;
        } while (iVar11 < DAT_TileMapState.constructionTileCount);
        iVar11 = 0;
        do {
          getBuildingSizeIndexMappingData(iVar11,5);
          iVar1 = DAT_ViewportRenderState.translationMatrix[y + DAT_TileMapState.buildingY + 5].
                  addXgetTile + DAT_TileMapState.buildingX + iVar13;
          if ((DAT_TileMapState.LogicLayer[iVar1] & 0x10000500U) == 0) {
            iVar12 = isBuildingPlacementAllowedAtTile
                               (&DAT_TileMapState,iVar1,DAT_GameSynchronyState.currentPlayerSlotID,
                                (int)(short)(undefined2)type,0);
            DAT_TileMapState.ConstructionGFXLayer[iVar1] = (-(ushort)(iVar12 != 0) & 0xfff9) + 0x3e;
          }
          iVar11 = iVar11 + 1;
        } while (iVar11 < DAT_TileMapState.constructionTileCount);
        iVar11 = 0;
        do {
          getBuildingSizeIndexMappingData(iVar11,5);
          iVar12 = DAT_TileMapState.buildingX;
          iVar2 = DAT_TileMapState.buildingY + y + 5;
          iVar1 = DAT_ViewportRenderState.translationMatrix[y + DAT_TileMapState.buildingY + 5].
                  addXgetTile;
          if ((DAT_TileMapState.LogicLayer[iVar13 + DAT_TileMapState.buildingX + iVar1 + 5] &
              0x10000500U) == 0) {
            iVar2 = isBuildingPlacementAllowedAtTile
                              (&DAT_TileMapState,iVar1 + DAT_TileMapState.buildingX + iVar13 + 5,
                               DAT_GameSynchronyState.currentPlayerSlotID,
                               (int)(short)(undefined2)type,0);
            iVar2 = (-(uint)(iVar2 != 0) & 0xfffffff9) + 0x3e;
            DAT_TileMapState.ConstructionGFXLayer[iVar13 + iVar12 + iVar1 + 5] = (ushort)iVar2;
          }
          iVar11 = iVar11 + 1;
        } while (iVar11 < DAT_TileMapState.constructionTileCount);
        return iVar2;
      }
      if (((undefined2)type != M_MAPPER_ENGINEERS_GUILD) &&
         ((undefined2)type != M_MAPPER_TUNNELERS_GUILD)) {
        if ((undefined2)type != M_MAPPER_OIL_SMELTER) {
          return CONCAT22(uVar7,(undefined2)type);
        }
        iVar11 = 0;
        do {
          getBuildingSizeIndexMappingData(iVar11,4);
          iVar1 = DAT_TileMapState.buildingY + y + 4;
          iVar12 = DAT_ViewportRenderState.translationMatrix[y + DAT_TileMapState.buildingY + 4].
                   addXgetTile + DAT_TileMapState.buildingX + iVar13;
          if ((DAT_TileMapState.LogicLayer[iVar12] & 0x10000500U) == 0) {
            iVar1 = isBuildingPlacementAllowedAtTile
                              (&DAT_TileMapState,iVar12,DAT_GameSynchronyState.currentPlayerSlotID,
                               M_MAPPER_OIL_SMELTER,0);
            iVar1 = (-(uint)(iVar1 != 0) & 0xfffffff9) + 0x3e;
            DAT_TileMapState.ConstructionGFXLayer[iVar12] = (ushort)iVar1;
          }
          iVar11 = iVar11 + 1;
        } while (iVar11 < DAT_TileMapState.constructionTileCount);
        return iVar1;
      }
      iVar11 = 0;
      do {
        getBuildingSizeIndexMappingData(iVar11,5);
        iVar1 = (DAT_TileMapState.buildingY + y + 5) * 3;
        iVar12 = DAT_ViewportRenderState.translationMatrix[y + DAT_TileMapState.buildingY + 5].
                 addXgetTile + DAT_TileMapState.buildingX + iVar13;
        if ((DAT_TileMapState.LogicLayer[iVar12] & 0x10000500U) == 0) {
          iVar1 = isBuildingPlacementAllowedAtTile
                            (&DAT_TileMapState,iVar12,DAT_GameSynchronyState.currentPlayerSlotID,
                             (int)(short)(undefined2)type,0);
          iVar1 = (-(uint)(iVar1 != 0) & 0xfffffff9) + 0x3e;
          DAT_TileMapState.ConstructionGFXLayer[iVar12] = (ushort)iVar1;
        }
        iVar11 = iVar11 + 1;
      } while (iVar11 < DAT_TileMapState.constructionTileCount);
      return iVar1;
    }
  }
  else {
    iVar1 = Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType
                      ((int)(short)(undefined2)type);
    DAT_TileMapState.buildingSpriteSheetID_1 =
         DAT_BuildingDefinedData.DAT_Building_SpriteSheet_ID_Array_1[iVar1];
    DAT_TileMapState.buildingSpriteID1 =
         Buildings::BuildingsState::getSpriteID(&DAT_BuildingsState,(int)(short)(undefined2)type);
    DAT_TileMapState.buildingSpriteID2 =
         Buildings::BuildingsState::getSpriteID2(&DAT_BuildingsState,(int)(short)(undefined2)type);
  }
  if ((undefined2)type == M_MAPPER_WHEATFARM) {
    size = 3;
  }
  else if ((undefined2)type == M_MAPPER_HOPSFARM) {
    size = 3;
  }
  else if ((undefined2)type == M_MAPPER_APPLEFARM) {
    size = 3;
  }
  else if ((undefined2)type == M_MAPPER_CATTLEFARM) {
    size = 3;
  }
  else if (((((undefined2)type == M_MAPPER_GATE_WOOD1A) ||
            ((undefined2)type == M_MAPPER_GATE_WOOD1C)) ||
           ((undefined2)type == M_MAPPER_GATE_STONE1A)) ||
          ((undefined2)type == M_MAPPER_GATE_STONE2A)) {
    DAT_TileMapState.field78_0x55488c = 0x51;
  }
  else if ((((undefined2)type == M_MAPPER_GATE_WOOD1B) || ((undefined2)type == M_MAPPER_GATE_WOOD1D)
           ) || (((undefined2)type == M_MAPPER_GATE_STONE1B ||
                 ((undefined2)type == M_MAPPER_GATE_STONE2B)))) {
    DAT_TileMapState.field78_0x55488c = 0x50;
  }
  iVar1 = (int)(short)(undefined2)type;
  do {
    getBuildingSizeIndexMappingData(local_14,size);
    iVar2 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + y].addXgetTile +
            DAT_TileMapState.buildingX + iVar13;
    iVar12 = DAT_TileMapState.uiBuildingRotation;
    if (((DAT_TileMapState.uiBuildingRotation != 0xf) && (DAT_TileMapState.uiBuildingRotation != 8))
       && (iVar12 = DAT_TileMapState.uiBuildingRotation - DAT_TileMapState.mapOrientation,
          iVar12 < 0)) {
      iVar12 = iVar12 + 8;
    }
    x._0_2_ = (short)DAT_TileMapState.buildingSpriteID1;
    if ((DAT_TileMapState.mapOrientation == 2) || (DAT_TileMapState.mapOrientation == 6)) {
      if (DAT_TileMapState.field78_0x55488c != 0x51) goto LAB_00505714;
    }
    else if (DAT_TileMapState.field78_0x55488c == 0x51) {
LAB_00505714:
      x._0_2_ = (short)DAT_TileMapState.buildingSpriteID2;
    }
    if (((undefined2)type == M_MAPPER_DRAWBRIDGE) && (iVar12 != 0)) {
      if (iVar12 == 2) {
        iVar12 = 3;
      }
      else if (iVar12 == 4) {
        iVar12 = 2;
      }
      else if (iVar12 == 6) {
        iVar12 = 1;
      }
    }
    iVar3 = Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType(iVar1);
    if (iVar3 == 0x27) {
      x._0_2_ = (short)x + (short)(&DAT_BuildingDefinedData.field209_0x976c[9].y)[iVar1];
    }
    else {
      iVar3 = Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType(iVar1);
      if (iVar3 == 1) {
        x._0_2_ = (short)DAT_BuildingDefinedData.DAT_SomeSpriteArray1
                         [DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                          hovelCountUpToEight];
      }
    }
    if (DAT_TileMapState.uiBuildingRotation == 0xf) {
      DAT_TileMapState.ConstructionGFXLayer[iVar2] =
           ((short)GMTotalPicturesProcessed[DAT_TileMapState.buildingSpriteSheetID_1] + (short)x +
           (short)DAT_TileMapState.buildingRotationRelatedValue) - 1;
    }
    else {
      DAT_TileMapState.ConstructionGFXLayer[iVar2] =
           ((short)(iVar12 * size * size) +
            (short)GMTotalPicturesProcessed[DAT_TileMapState.buildingSpriteSheetID_1] + (short)x +
           (short)DAT_TileMapState.buildingRotationRelatedValue) - 1;
    }
    if (iVar11 != 0) {
      DAT_TileMapState.MiscDisplayLayer[iVar2] = DAT_TileMapState.MiscDisplayLayer[iVar2] | 0x8000;
    }
    local_14 = local_14 + 1;
    if (DAT_TileMapState.constructionTileCount <= local_14) {
      iVar12 = CONCAT22((short)((uint)local_14 >> 0x10),(undefined2)type);
      if (((((undefined2)type == M_MAPPER_GATE_WOOD1A) || ((undefined2)type == M_MAPPER_GATE_WOOD1B)
           ) || ((undefined2)type == M_MAPPER_GATE_WOOD1C)) ||
         ((undefined2)type == M_MAPPER_GATE_WOOD1D)) {
                    /* 0 3 6 9 */
        iVar12 = iVar1 * 3 + -0x1a4;
        iVar2 = *(int *)((int)&DAT_TerrainDefinedData + iVar12 * 8 + 0x50c);
        iVar3 = *(int *)((int)&DAT_TerrainDefinedData + iVar12 * 8 + 0x510);
                    /* 0 24 48 72 */
        iVar12 = iVar12 * 8;
        iVar4 = *(int *)((int)&DAT_TerrainDefinedData + iVar12 + 0x514);
        iVar14 = 0;
        do {
          getBuildingSizeIndexMappingData(iVar14,2);
          iVar5 = DAT_ViewportRenderState.translationMatrix[iVar3 + y + DAT_TileMapState.buildingY].
                  addXgetTile + DAT_TileMapState.buildingX + iVar2 + iVar13;
          DAT_TileMapState.ConstructionGFXLayer[iVar5] =
               (short)DAT_TileMapState.buildingRotationRelatedValue +
               (short)GMTotalPicturesProcessed[0x34];
          if (iVar11 != 0) {
            DAT_TileMapState.MiscDisplayLayer[iVar5] =
                 DAT_TileMapState.MiscDisplayLayer[iVar5] | 0x8000;
          }
          iVar14 = iVar14 + 1;
        } while (iVar14 < DAT_TileMapState.constructionTileCount);
        pXVar9 = &DAT_TerrainDefinedData.field555_0x68c + iVar4 * 5;
        iVar14 = 0;
        do {
          iVar5 = DAT_ViewportRenderState.translationMatrix[pXVar9->y + iVar3 + y].addXgetTile +
                  pXVar9->x + iVar2 + iVar13;
          if (iVar14 < 1) {
            DAT_TileMapState.ConstructionGFXLayer[iVar5] =
                 (short)GMTotalPicturesProcessed[0x34] + 0x60e + (short)iVar14;
          }
          else {
            iVar6 = *(int *)(&DAT_TerrainDefinedData.field_0x7c8 + (iVar14 + iVar4 * 4) * 4) -
                    DAT_TileMapState.mapOrientation;
            if (iVar6 < 0) {
              iVar6 = iVar6 + 8;
            }
            DAT_TileMapState.ConstructionGFXLayer[iVar5] =
                 (short)GMTotalPicturesProcessed[0x34] + (short)(iVar6 / 2) * 4 + 0x60e +
                 (short)iVar14;
          }
          if (iVar11 != 0) {
            DAT_TileMapState.MiscDisplayLayer[iVar5] =
                 DAT_TileMapState.MiscDisplayLayer[iVar5] | 0x8000;
          }
          iVar14 = iVar14 + 1;
          pXVar9 = pXVar9 + 1;
        } while (iVar14 < 5);
        iVar2 = *(int *)((int)&DAT_TerrainDefinedData + iVar12 + 0x518);
        iVar3 = *(int *)((int)&DAT_TerrainDefinedData + iVar12 + 0x51c);
        iVar12 = *(int *)((int)&DAT_TerrainDefinedData + iVar12 + 0x520);
        iVar4 = 0;
        do {
          getBuildingSizeIndexMappingData(iVar4,2);
          iVar14 = DAT_ViewportRenderState.translationMatrix[iVar3 + y + DAT_TileMapState.buildingY]
                   .addXgetTile + DAT_TileMapState.buildingX + iVar2 + iVar13;
          DAT_TileMapState.ConstructionGFXLayer[iVar14] =
               (short)DAT_TileMapState.buildingRotationRelatedValue +
               (short)GMTotalPicturesProcessed[0x34];
          if (iVar11 != 0) {
            DAT_TileMapState.MiscDisplayLayer[iVar14] =
                 DAT_TileMapState.MiscDisplayLayer[iVar14] | 0x8000;
          }
          iVar4 = iVar4 + 1;
        } while (iVar4 < DAT_TileMapState.constructionTileCount);
        pXVar9 = &DAT_TerrainDefinedData.field555_0x68c + iVar12 * 5;
        iVar4 = 0;
        do {
          iVar14 = DAT_ViewportRenderState.translationMatrix[pXVar9->y + iVar3 + y].addXgetTile +
                   pXVar9->x + iVar2 + iVar13;
          if (iVar4 < 1) {
            DAT_TileMapState.ConstructionGFXLayer[iVar14] =
                 (short)GMTotalPicturesProcessed[0x34] + 0x60e + (short)iVar4;
          }
          else {
            iVar5 = *(int *)(&DAT_TerrainDefinedData.field_0x7c8 + (iVar4 + iVar12 * 4) * 4) -
                    DAT_TileMapState.mapOrientation;
            if (iVar5 < 0) {
              iVar5 = iVar5 + 8;
            }
            DAT_TileMapState.ConstructionGFXLayer[iVar14] =
                 (short)GMTotalPicturesProcessed[0x34] + (short)(iVar5 / 2) * 4 + 0x60e +
                 (short)iVar4;
          }
          if (iVar11 != 0) {
            DAT_TileMapState.MiscDisplayLayer[iVar14] =
                 DAT_TileMapState.MiscDisplayLayer[iVar14] | 0x8000;
          }
          iVar4 = iVar4 + 1;
          pXVar9 = pXVar9 + 1;
        } while (iVar4 < 5);
        piVar10 = (int *)((int)&DAT_TerrainDefinedData + (iVar1 * 3 + -0x1a4) * 0x10 + 0x5cc);
        type = M_MAPPER_FOREST;
        do {
          iVar12 = DAT_ViewportRenderState.translationMatrix[piVar10[1] + y].addXgetTile + iVar13 +
                   *piVar10;
          DAT_TileMapState.ConstructionGFXLayer[iVar12] =
               ((byte)DAT_TileMapState.RandomLayer[iVar12] & 3) + 0x138 +
               (short)GMTotalPicturesProcessed[6];
          if (iVar11 != 0) {
            DAT_TileMapState.MiscDisplayLayer[iVar12] =
                 DAT_TileMapState.MiscDisplayLayer[iVar12] | 0x8000;
          }
          piVar10 = piVar10 + 2;
          type = type - M_MAPPER_AREA;
        } while (type != M_MAPPER_NULL);
      }
      else {
        if ((undefined2)type == M_MAPPER_WHEATFARM) {
          iVar1 = 0;
          do {
            iVar12 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                     unkWheatFarmOrientation;
            iVar12 = DAT_ViewportRenderState.translationMatrix
                     [DAT_TerrainDefinedData.WheatFarmTiles[iVar12][iVar1].y + y].addXgetTile +
                     DAT_TerrainDefinedData.WheatFarmTiles[iVar12][iVar1].x + iVar13;
            DAT_TileMapState.ConstructionGFXLayer[iVar12] =
                 ((byte)DAT_TileMapState.RandomLayer[iVar12] & 3) +
                 (short)GMTotalPicturesProcessed[0xe];
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar12] =
                   DAT_TileMapState.MiscDisplayLayer[iVar12] | 0x8000;
            }
            iVar1 = iVar1 + 1;
          } while (iVar1 < 0x24);
          return iVar12;
        }
        if ((undefined2)type == M_MAPPER_HOPSFARM) {
          iVar1 = 0;
          do {
            iVar12 = *(int *)&DAT_GameState.playerDataArray
                              [DAT_GameSynchronyState.currentPlayerSlotID].unkHopFarmVariation;
            iVar12 = DAT_ViewportRenderState.translationMatrix
                     [DAT_TerrainDefinedData.HopFarmProperty1[iVar12][iVar1].y + y].addXgetTile +
                     DAT_TerrainDefinedData.HopFarmProperty1[iVar12][iVar1].x + iVar13;
            DAT_TileMapState.ConstructionGFXLayer[iVar12] =
                 ((byte)DAT_TileMapState.RandomLayer[iVar12] & 1) * 9 + 0x25 +
                 (short)GMTotalPicturesProcessed[0xe];
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar12] =
                   DAT_TileMapState.MiscDisplayLayer[iVar12] | 0x8000;
            }
            iVar1 = iVar1 + 1;
          } while (iVar1 < 0x18);
          return iVar12;
        }
        if ((undefined2)type == M_MAPPER_CATTLEFARM) {
          iVar13 = 0;
          do {
            uVar16 = getRubbleGraphicStageForDamageLevel
                               (DAT_TerrainDefinedData.field1009_0xf5c
                                [DAT_GameState.playerDataArray
                                 [DAT_GameSynchronyState.currentPlayerSlotID].dairyFarmVariationMod4
                                ][iVar13 + 4].property);
            iVar12 = (int)((ulonglong)uVar16 >> 0x20);
            iVar1 = (int)uVar16 + 0x37 + GMTotalPicturesProcessed[0xe];
            DAT_TileMapState.ConstructionGFXLayer[iVar12] = (ushort)iVar1;
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar12] =
                   DAT_TileMapState.MiscDisplayLayer[iVar12] | 0x8000;
            }
            iVar13 = iVar13 + 1;
          } while (iVar13 < 0x17);
          return iVar1;
        }
        if ((undefined2)type == M_MAPPER_APPLEFARM) {
          pXVar9 = DAT_TerrainDefinedData.AppleFarmOffsets;
          do {
            iVar1 = DAT_ViewportRenderState.translationMatrix[pXVar9->y + y].addXgetTile + pXVar9->x
                    + iVar13;
            DAT_TileMapState.ConstructionGFXLayer[iVar1] =
                 (short)GMTotalPicturesProcessed[0xe] + 0x3d;
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar1] =
                   DAT_TileMapState.MiscDisplayLayer[iVar1] | 0x8000;
            }
            pXVar9 = pXVar9 + 1;
          } while ((int)pXVar9 < 0xb49eb0);
          return iVar1;
        }
        if (((undefined2)type == M_MAPPER_BARRACKS_EURO) ||
           ((undefined2)type == M_MAPPER_BARRACKS_ARAB)) {
          iVar1 = 0;
          do {
            getBuildingSizeIndexMappingData(iVar1,5);
            iVar2 = DAT_TileMapState.buildingX;
            iVar12 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + y].
                     addXgetTile;
            DAT_TileMapState.ConstructionGFXLayer[iVar13 + DAT_TileMapState.buildingX + iVar12 + 5]
                 = (short)DAT_TileMapState.buildingRotationRelatedValue +
                   (short)GMTotalPicturesProcessed[6] + 0x48;
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar13 + iVar2 + iVar12 + 5] =
                   DAT_TileMapState.MiscDisplayLayer[iVar13 + iVar2 + iVar12 + 5] | 0x8000;
            }
            iVar1 = iVar1 + 1;
          } while (iVar1 < DAT_TileMapState.constructionTileCount);
          iVar1 = 0;
          do {
            getBuildingSizeIndexMappingData(iVar1,5);
            iVar12 = DAT_ViewportRenderState.translationMatrix[y + DAT_TileMapState.buildingY + 5].
                     addXgetTile + DAT_TileMapState.buildingX + iVar13;
            DAT_TileMapState.ConstructionGFXLayer[iVar12] =
                 (short)DAT_TileMapState.buildingRotationRelatedValue +
                 (short)GMTotalPicturesProcessed[6] + 0x7a;
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar12] =
                   DAT_TileMapState.MiscDisplayLayer[iVar12] | 0x8000;
            }
            iVar1 = iVar1 + 1;
          } while (iVar1 < DAT_TileMapState.constructionTileCount);
          iVar1 = 0;
          do {
            getBuildingSizeIndexMappingData(iVar1,5);
            iVar2 = DAT_TileMapState.buildingX;
            iVar12 = DAT_ViewportRenderState.translationMatrix[y + DAT_TileMapState.buildingY + 5].
                     addXgetTile;
            iVar3 = iVar12 + DAT_TileMapState.buildingX;
            DAT_TileMapState.ConstructionGFXLayer[iVar13 + DAT_TileMapState.buildingX + iVar12 + 5]
                 = (short)DAT_TileMapState.buildingRotationRelatedValue +
                   (short)GMTotalPicturesProcessed[6] + 0x61;
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar13 + iVar2 + iVar12 + 5] =
                   DAT_TileMapState.MiscDisplayLayer[iVar13 + iVar2 + iVar12 + 5] | 0x8000;
            }
            iVar1 = iVar1 + 1;
          } while (iVar1 < DAT_TileMapState.constructionTileCount);
          return iVar3 + iVar13 + 5;
        }
        if ((undefined2)type == M_MAPPER_ENGINEERS_GUILD) {
          iVar1 = 0;
          do {
            getBuildingSizeIndexMappingData(iVar1,5);
            iVar12 = DAT_ViewportRenderState.translationMatrix[y + DAT_TileMapState.buildingY + 5].
                     addXgetTile + DAT_TileMapState.buildingX + iVar13;
            DAT_TileMapState.ConstructionGFXLayer[iVar12] =
                 (short)DAT_TileMapState.buildingRotationRelatedValue +
                 (short)GMTotalPicturesProcessed[6] + 0x93;
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar12] =
                   DAT_TileMapState.MiscDisplayLayer[iVar12] | 0x8000;
            }
            iVar1 = iVar1 + 1;
          } while (iVar1 < DAT_TileMapState.constructionTileCount);
          return iVar12;
        }
        if ((undefined2)type == M_MAPPER_TUNNELERS_GUILD) {
          iVar1 = 0;
          do {
            getBuildingSizeIndexMappingData(iVar1,5);
            iVar12 = DAT_ViewportRenderState.translationMatrix[y + DAT_TileMapState.buildingY + 5].
                     addXgetTile + DAT_TileMapState.buildingX + iVar13;
            DAT_TileMapState.ConstructionGFXLayer[iVar12] =
                 (short)DAT_TileMapState.buildingRotationRelatedValue +
                 (short)GMTotalPicturesProcessed[6] + 0xac;
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar12] =
                   DAT_TileMapState.MiscDisplayLayer[iVar12] | 0x8000;
            }
            iVar1 = iVar1 + 1;
          } while (iVar1 < DAT_TileMapState.constructionTileCount);
          return iVar12;
        }
        if ((undefined2)type == M_MAPPER_OIL_SMELTER) {
          iVar1 = 0;
          do {
            getBuildingSizeIndexMappingData(iVar1,4);
            iVar12 = DAT_ViewportRenderState.translationMatrix[y + DAT_TileMapState.buildingY + 4].
                     addXgetTile + DAT_TileMapState.buildingX + iVar13;
            DAT_TileMapState.ConstructionGFXLayer[iVar12] =
                 (short)DAT_TileMapState.buildingRotationRelatedValue +
                 (short)GMTotalPicturesProcessed[6] + 0x128;
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar12] =
                   DAT_TileMapState.MiscDisplayLayer[iVar12] | 0x8000;
            }
            iVar1 = iVar1 + 1;
          } while (iVar1 < DAT_TileMapState.constructionTileCount);
          return iVar12;
        }
        if ((undefined2)type == M_MAPPER_KEEP1) {
          uVar8 = (ushort)(DAT_TileMapState.mapOrientation == 2);
          iVar1 = DAT_ViewportRenderState.translationMatrix
                  [DAT_TerrainDefinedData.field130_0x264[0][0].y + y].addXgetTile +
                  DAT_TerrainDefinedData.field130_0x264[0][0].x + iVar13;
          DAT_TileMapState.ConstructionGFXLayer[iVar1] =
               (short)GMTotalPicturesProcessed[0x34] + 0x523 + uVar8;
          if (iVar11 != 0) {
            DAT_TileMapState.MiscDisplayLayer[iVar1] =
                 DAT_TileMapState.MiscDisplayLayer[iVar1] | 0x8000;
          }
          iVar1 = DAT_ViewportRenderState.translationMatrix
                  [DAT_TerrainDefinedData.field130_0x264[0][1].y + y].addXgetTile +
                  DAT_TerrainDefinedData.field130_0x264[0][1].x + iVar13;
          DAT_TileMapState.ConstructionGFXLayer[iVar1] =
               (short)GMTotalPicturesProcessed[0x34] + 0x52e + uVar8;
          if (iVar11 != 0) {
            DAT_TileMapState.MiscDisplayLayer[iVar1] =
                 DAT_TileMapState.MiscDisplayLayer[iVar1] | 0x8000;
          }
          iVar1 = DAT_ViewportRenderState.translationMatrix
                  [DAT_TerrainDefinedData.field130_0x264[0][2].y + y].addXgetTile +
                  DAT_TerrainDefinedData.field130_0x264[0][2].x + iVar13;
          DAT_TileMapState.ConstructionGFXLayer[iVar1] =
               (short)GMTotalPicturesProcessed[0x34] + 0x527 + uVar8;
          if (iVar11 != 0) {
            DAT_TileMapState.MiscDisplayLayer[iVar1] =
                 DAT_TileMapState.MiscDisplayLayer[iVar1] | 0x8000;
          }
          iVar12 = iVar13 + DAT_TerrainDefinedData.unkXYOffsets_0x384[0].xOffset;
          iVar2 = y + DAT_TerrainDefinedData.unkXYOffsets_0x384[0].yOffset;
          iVar1 = 0;
          do {
            getBuildingSizeIndexMappingData(iVar1,7);
            iVar3 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + iVar2].
                    addXgetTile + DAT_TileMapState.buildingX + iVar12;
            DAT_TileMapState.ConstructionGFXLayer[iVar3] =
                 (short)DAT_TileMapState.buildingRotationRelatedValue +
                 (short)GMTotalPicturesProcessed[6] + 0x17;
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar3] =
                   DAT_TileMapState.MiscDisplayLayer[iVar3] | 0x8000;
            }
            iVar1 = iVar1 + 1;
          } while (iVar1 < DAT_TileMapState.constructionTileCount);
          iVar13 = DAT_TerrainDefinedData.field132_0x3c4[4].xOffset + iVar13;
          iVar1 = DAT_TerrainDefinedData.field132_0x3c4[4].yOffset + y;
          iVar12 = 0;
          do {
            getBuildingSizeIndexMappingData(iVar12,5);
            iVar2 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + iVar1].
                    addXgetTile + DAT_TileMapState.buildingX + iVar13;
            DAT_TileMapState.ConstructionGFXLayer[iVar2] =
                 (short)DAT_TileMapState.buildingRotationRelatedValue +
                 (short)GMTotalPicturesProcessed[7] + 0x19;
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar2] =
                   DAT_TileMapState.MiscDisplayLayer[iVar2] | 0x8000;
            }
            iVar12 = iVar12 + 1;
          } while (iVar12 < DAT_TileMapState.constructionTileCount);
          return iVar2;
        }
        if (((undefined2)type == M_MAPPER_KEEP2) || ((undefined2)type == M_MAPPER_KEEP3)) {
          uVar8 = (ushort)(DAT_TileMapState.mapOrientation == 2);
          iVar12 = (iVar1 + -0x3c) * 0x60;
          iVar2 = DAT_ViewportRenderState.translationMatrix
                  [*(int *)((int)&DAT_TerrainDefinedData + iVar12 + 0x268) + y].addXgetTile +
                  *(int *)((int)&DAT_TerrainDefinedData + iVar12 + 0x264) + iVar13;
          DAT_TileMapState.ConstructionGFXLayer[iVar2] =
               (short)GMTotalPicturesProcessed[0x34] + 0x521 + uVar8;
          if (iVar11 != 0) {
            DAT_TileMapState.MiscDisplayLayer[iVar2] =
                 DAT_TileMapState.MiscDisplayLayer[iVar2] | 0x8000;
          }
          iVar2 = DAT_ViewportRenderState.translationMatrix
                  [*(int *)((int)&DAT_TerrainDefinedData + iVar12 + 0x270) + y].addXgetTile +
                  *(int *)((int)&DAT_TerrainDefinedData + iVar12 + 0x26c) + iVar13;
          DAT_TileMapState.ConstructionGFXLayer[iVar2] =
               (short)GMTotalPicturesProcessed[0x34] + 0x529 + uVar8;
          if (iVar11 != 0) {
            DAT_TileMapState.MiscDisplayLayer[iVar2] =
                 DAT_TileMapState.MiscDisplayLayer[iVar2] | 0x8000;
          }
          iVar12 = DAT_ViewportRenderState.translationMatrix
                   [*(int *)((int)&DAT_TerrainDefinedData + iVar12 + 0x278) + y].addXgetTile +
                   *(int *)((int)&DAT_TerrainDefinedData + iVar12 + 0x274) + iVar13;
          DAT_TileMapState.ConstructionGFXLayer[iVar12] =
               (short)GMTotalPicturesProcessed[0x34] + 0x525 + uVar8;
          if (iVar11 != 0) {
            DAT_TileMapState.MiscDisplayLayer[iVar12] =
                 DAT_TileMapState.MiscDisplayLayer[iVar12] | 0x8000;
          }
          iVar2 = (iVar1 + -0x3c) * 0x20;
          iVar1 = *(int *)((int)&DAT_TerrainDefinedData + iVar2 + 900);
          iVar12 = *(int *)((int)&DAT_TerrainDefinedData + iVar2 + 0x388);
          iVar3 = 0;
          do {
            getBuildingSizeIndexMappingData(iVar3,7);
            iVar4 = DAT_ViewportRenderState.translationMatrix
                    [DAT_TileMapState.buildingY + y + iVar12].addXgetTile +
                    DAT_TileMapState.buildingX + iVar13 + iVar1;
            DAT_TileMapState.ConstructionGFXLayer[iVar4] =
                 (short)DAT_TileMapState.buildingRotationRelatedValue +
                 (short)GMTotalPicturesProcessed[6] + 0x17;
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar4] =
                   DAT_TileMapState.MiscDisplayLayer[iVar4] | 0x8000;
            }
            iVar3 = iVar3 + 1;
          } while (iVar3 < DAT_TileMapState.constructionTileCount);
          iVar1 = *(int *)((int)&DAT_TerrainDefinedData + iVar2 + 0x3e4);
          iVar12 = *(int *)((int)&DAT_TerrainDefinedData + iVar2 + 1000);
          iVar2 = 0;
          do {
            getBuildingSizeIndexMappingData(iVar2,5);
            iVar3 = DAT_ViewportRenderState.translationMatrix
                    [DAT_TileMapState.buildingY + iVar12 + y].addXgetTile +
                    DAT_TileMapState.buildingX + iVar1 + iVar13;
            DAT_TileMapState.ConstructionGFXLayer[iVar3] =
                 (short)DAT_TileMapState.buildingRotationRelatedValue +
                 (short)GMTotalPicturesProcessed[7] + 0x19;
            if (iVar11 != 0) {
              DAT_TileMapState.MiscDisplayLayer[iVar3] =
                   DAT_TileMapState.MiscDisplayLayer[iVar3] | 0x8000;
            }
            iVar2 = iVar2 + 1;
          } while (iVar2 < DAT_TileMapState.constructionTileCount);
          return iVar3;
        }
      }
      return iVar12;
    }
  } while( true );
}


// ================= _HoldStrong::Map::TileMapState::prepareAreaForBuildingPlacement @ 005160c0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::TileMapState::prepareAreaForBuildingPlacement
          (TileMapState *this,int playerID,uint x,uint y,MappersEnum commandBuildingType,
          int buildingWidthOrHeight)

{
  BuildingTypeShort BVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  BOOLEnum _result;
  
  iVar3 = 0;
  _result = FALSE;
  storeMinAndMaxHeightOfArea(&DAT_TileMapState,x,y,buildingWidthOrHeight);
  do {
    getBuildingSizeIndexMappingData(iVar3,buildingWidthOrHeight);
    uVar4 = y + DAT_TileMapState.buildingY;
                    /* Any border is hit */
    if ((((399 < x + DAT_TileMapState.buildingX) || (399 < uVar4)) ||
        (*(char *)(uVar4 * 400 + 0x21aec98 + x + DAT_TileMapState.buildingX) == '\0')) ||
       (iVar2 = DAT_ViewportRenderState.translationMatrix[uVar4].addXgetTile +
                DAT_TileMapState.buildingX + x, (DAT_TileMapState.LogicLayer[iVar2] & 0x30) != 0)) {
      return FALSE;
    }
    iVar2 = isBuildingPlacementAllowedAtTile
                      (&DAT_TileMapState,iVar2,playerID,(int)(short)(undefined2)commandBuildingType,
                       1);
    if (iVar2 == 1) {
      return FALSE;
    }
    iVar3 = iVar3 + 1;
  } while (iVar3 < DAT_TileMapState.constructionTileCount);
  commandBuildingType = M_MAPPER_NULL;
  do {
    getBuildingSizeIndexMappingData(commandBuildingType,buildingWidthOrHeight);
    iVar3 = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + y].addXgetTile +
            x + DAT_TileMapState.buildingX;
    uVar4 = (uint)(short)DAT_TileMapState.BuildingLayer[iVar3];
    if (uVar4 == 0) {
      if (((DAT_TileMapState.LogicLayer[iVar3] & 0x4000000U) != 0) &&
         (uVar4 = Buildings::BuildingsState::getFarmThatHasTile(&DAT_BuildingsState,iVar3),
         uVar4 != 0)) {
        Buildings::BuildingsState::giveBackResourceForDestroyedBuilding
                  (&DAT_BuildingsState,uVar4,playerID,0x32);
        clearBuildingFromTerrain(&DAT_TileMapState,uVar4);
        Game::GameStateStructures::updatePrimaryBuildingPlayerDataReferences(&DAT_GameState,uVar4);
        goto _HoldStrong_Map_TileMapState_prepareAreaForBuildingPlacement_LAB_ClearBuilding;
      }
    }
    else {
      BVar1 = DAT_BuildingsState.buildings[uVar4].buildingType;
      if (((BVar1 == BT_WOODCUTTERSHUT) || (BVar1 == BT_OXTETHER)) ||
         ((BVar1 == BT_QUARRY ||
          ((((BVar1 == BT_IRONMINE || (BVar1 == BT_WHEATFARM)) || (BVar1 == BT_HOPFARM)) ||
           ((BVar1 == BT_APPLEFARM || (BVar1 == BT_DAIRYFARM)))))))) {
        Buildings::BuildingsState::giveBackResourceForDestroyedBuilding
                  (&DAT_BuildingsState,uVar4,playerID,0x32);
        clearBuildingFromTerrain(&DAT_TileMapState,uVar4);
        Game::GameStateStructures::updatePrimaryBuildingPlayerDataReferences(&DAT_GameState,uVar4);
_HoldStrong_Map_TileMapState_prepareAreaForBuildingPlacement_LAB_ClearBuilding:
        IO::LowLevelMemory::fillMemory_ByteValue
                  (&DAT_LowLevelMemory,0x32c,'\0',DAT_BuildingsState.buildings + uVar4);
        _result = TRUE;
      }
    }
    commandBuildingType = commandBuildingType + M_MAPPER_AREA;
    if (DAT_TileMapState.constructionTileCount <= (int)commandBuildingType) {
      return _result;
    }
  } while( true );
}


// ================= _HoldStrong::Map::TileMapState::placeBuilding @ 005162d0 =================

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


// ================= _HoldStrong::Map::Units::UnitsState::isWorkplaceBuildingOnAdjacentTile @ 00534380 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Units::UnitsState::isWorkplaceBuildingOnAdjacentTile(UnitsState *this,int param_1)

{
  ushort uVar1;
  int (*paiVar2) [8];
  int iVar3;
  
  uVar1 = DAT_UnitsState.units[param_1].workplaceBuildingID_1;
  if (uVar1 == 0) {
    return 0;
  }
  iVar3 = 0;
  paiVar2 = DAT_TileMapState.directionTranslationMatrix + DAT_UnitsState.units[param_1].y;
  do {
    if (DAT_TileMapState.BuildingLayer[(*paiVar2)[0] + DAT_UnitsState.units[param_1].tile] == uVar1)
    {
      return 1;
    }
    iVar3 = iVar3 + 1;
    paiVar2 = (int (*) [8])(*paiVar2 + 1);
  } while (iVar3 < 8);
  return 0;
}


// ================= _HoldStrong::Map::Units::UnitsState::setWorkplaceBuildingEntryAsTarget @ 005343f0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Units::UnitsState::setWorkplaceBuildingEntryAsTarget
          (UnitsState *this,int unitID,int entryAngleUnk)

{
  int buildingID;
  int iVar1;
  
  buildingID = (int)DAT_UnitsState.units[unitID].workplaceBuildingID_1;
  if (DAT_BuildingsState.buildings[buildingID].uid ==
      DAT_UnitsState.units[unitID].workplaceBuildingUID) {
    iVar1 = Buildings::BuildingsState::buildingIsAccessible
                      (&DAT_BuildingsState,buildingID,entryAngleUnk);
    if (iVar1 != 0) {
      DAT_UnitsState.units[unitID].targetX_2 =
           DAT_BuildingsState.buildings[buildingID].buildingEntryX;
      DAT_UnitsState.units[unitID].targetY_2 =
           DAT_BuildingsState.buildings[buildingID].buildingEntryY;
      return 1;
    }
  }
  return 0;
}


// ================= _HoldStrong::Global::Init::CreateKeepAndGranaryPlacementInfoDisplayElement @ 0059c5a0 =================

void _HoldStrong::Global::Init::CreateKeepAndGranaryPlacementInfoDisplayElement(void)

{
  UI::DisplayElement::Constructor_DisplayElement
            (&KeepAndGranaryPlacementInfoDisplayElement,OST_KEEP_MESSAGE,0x2d5,0x1bf,0,
             UI::Rendering::RenderAndPlayKeepAndGranaryPlacementInfoDisplayElement,
             DEPM_TOWARDS_MID_Y);
  return;
}


