// ================= _HoldStrong::Map::Buildings::BuildingsState::resourceGainForKillingPitAndPitchDitch @ 0040c9b0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Buildings::BuildingsState::resourceGainForKillingPitAndPitchDitch
          (BuildingsState *this,BuildingType buildingType,int *ptrRequiredStone,int *ptrRequiredGold
          )

{
  *ptrRequiredStone = DAT_BuildingsState.buildingCosts[buildingType].requiredStone_0x4;
  *ptrRequiredGold = DAT_BuildingsState.buildingCosts[buildingType].requiredGold;
  if (buildingType == BT_KILLINGPIT) {
    *ptrRequiredGold = 5;
  }
  else if (buildingType == BT_PITCHDITCH) {
    *ptrRequiredGold = 2;
    return;
  }
  return;
}


// ================= _HoldStrong::Map::Buildings::BuildingsState::processDamageFromKillingPit @ 00419800 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Buildings::BuildingsState::processDamageFromKillingPit
          (BuildingsState *this,int unitID)

{
  int *piVar1;
  UnitTypeShort UVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  
  iVar4 = (int)(short)DAT_TileMapState.BuildingLayer[DAT_UnitsState.units[unitID].tile];
  if (((((iVar4 != 0) && (UVar2 = DAT_UnitsState.units[unitID].unitType, UVar2 != UT_TRADER)) &&
       (UVar2 != UT_TRADERHORSE)) &&
      ((((DAT_GameCore.gameMode_2 == GM_SKIRMISH_AND_MULTIPLAYER ||
         (DAT_BuildingsState.buildings[iVar4].owner == DAT_GameSynchronyState.currentPlayerSlotID))
        || (DAT_UnitsState.units[unitID].owner == DAT_GameSynchronyState.currentPlayerSlotID)) &&
       ((DAT_BuildingsState.buildings[iVar4].buildingType == BT_KILLINGPIT &&
        (DAT_BuildingsState.buildings[iVar4].state == 0)))))) &&
     ((DAT_UnitsState.units[unitID].unknownTestAgainst0_1 == 0 &&
      ((DAT_GameState.mapAndTime.playerTeams[DAT_BuildingsState.buildings[iVar4].owner] !=
        DAT_GameState.mapAndTime.playerTeams[DAT_UnitsState.units[unitID].owner] &&
       (DAT_UnitsState.units[unitID].dying == 0)))))) {
    piVar1 = &DAT_UnitsState.units[unitID].health;
    *piVar1 = *piVar1 + -18000;
    if (DAT_UnitsState.units[unitID].health < 1) {
      DAT_UnitsState.units[unitID].health = 0;
      DAT_UnitsState.units[unitID].state.generic = US_STONE_DEATH_01;
      DAT_UnitsState.units[unitID].animationCycleNumber = 0;
      DAT_UnitsState.units[unitID].dying = 1;
      DAT_UnitsState.units[unitID].tunnelerFinishedDigging = 1;
    }
    iVar5 = Navigation::DirectionAlgorithmState::computeHealthPercentage
                      (&DAT_DirectionAlgorithmState,DAT_UnitsState.units[unitID].health,
                       DAT_UnitsState.units[unitID].maxHealth);
    sVar3 = (short)iVar5;
    DAT_UnitsState.units[unitID].healthPercentage = sVar3;
    DAT_UnitsState.units[unitID].healthbar =
         (sVar3 / 10 + (sVar3 >> 0xf)) - (short)((longlong)(int)sVar3 * 0x66666667 >> 0x3f);
    DAT_BuildingsState.buildings[iVar4].state = 1;
  }
  return;
}


// ================= _HoldStrong::Map::Version::UpgradeKillingPitField @ 0041a5c0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Map::Version::UpgradeKillingPitField(void)

{
  BuildingTypeShort *pBVar1;
  
  pBVar1 = &DAT_BuildingsState.buildings[1].buildingType;
  do {
    if ((pBVar1[-1] != 0) && (*pBVar1 == BT_KILLINGPIT)) {
      pBVar1[0x25] = 0;
    }
    pBVar1 = pBVar1 + 0x196;
  } while ((int)pBVar1 < 0x1124dc6);
  return;
}


// ================= _HoldStrong::Global::UpdateKillingPit @ 0041e650 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Global::UpdateKillingPit(void)

{
  short *psVar1;
  int iVar2;
  int buildingID;
  
  buildingID = DAT_CurrentBuildingID;
  DAT_BuildingsState.buildings[DAT_CurrentBuildingID].renderAnimation = 0;
  DAT_BuildingsState.buildings[buildingID].animationIncrement = 1;
  if ((DAT_TileMapState.BuildingLayer
       [DAT_BuildingsState.buildings[buildingID].currentTilePositionAdjusted] == 0) ||
     ((short)DAT_TileMapState.BuildingLayer
             [DAT_BuildingsState.buildings[buildingID].currentTilePositionAdjusted] != buildingID))
  {
    DAT_TileMapState.showNoRubbleWhenDestroyingBuilding = 1;
    Map::Buildings::BuildingsState::destroyBuilding(&DAT_BuildingsState,buildingID);
    buildingID = DAT_CurrentBuildingID;
  }
  switch(DAT_BuildingsState.buildings[buildingID].state) {
  case 0:
    DAT_BuildingsState.buildings[buildingID].spriteID =
         (DAT_BuildingsState.buildings[buildingID].fireRelatedRNG1 & 7U) + 9;
    DAT_BuildingsState.buildings[buildingID].field117_0x11a = 0;
    DAT_BuildingsState.buildings[buildingID].animationIndex = 0;
    if ((short)DAT_BuildingsState.buildings[buildingID].killingPitField != 0) {
      return;
    }
    Map::TileMapState::updateBuildingGraphicsLayer(&DAT_TileMapState,buildingID);
    *(undefined2 *)&DAT_BuildingsState.buildings[DAT_CurrentBuildingID].killingPitField = 1;
    return;
  case 1:
    DAT_BuildingsState.buildings[buildingID].spriteID =
         (DAT_BuildingsState.buildings[buildingID].fireRelatedRNG1 & 7U) + 1;
    DAT_BuildingsState.buildings[buildingID].renderAnimation = 1;
    iVar2 = DAT_BuildingDefinedData.field418_0xa5a4
            [DAT_BuildingsState.buildings[buildingID].animationIndex];
    if (iVar2 == -1) {
      DAT_BuildingsState.buildings[buildingID].state = 2;
      DAT_BuildingsState.buildings[buildingID].field117_0x11a = 0;
      Map::TileMapState::updateBuildingGraphicsLayer(&DAT_TileMapState,buildingID);
      return;
    }
LAB_0041e704:
    DAT_BuildingsState.buildings[buildingID].animationFrame = iVar2;
    if (iVar2 != 0) {
      DAT_BuildingsState.buildings[buildingID].animationFrame =
           iVar2 + (DAT_BuildingsState.buildings[buildingID].fireRelatedRNG1 & 7U) * 4;
      Map::TileMapState::updateBuildingGraphicsLayer(&DAT_TileMapState,buildingID);
      return;
    }
    break;
  case 2:
    DAT_BuildingsState.buildings[buildingID].renderAnimation = 1;
    psVar1 = &DAT_BuildingsState.buildings[buildingID].field117_0x11a;
    *psVar1 = *psVar1 + 1;
    if (1999 < DAT_BuildingsState.buildings[buildingID].field117_0x11a) {
      DAT_TileMapState.showNoRubbleWhenDestroyingBuilding = 1;
      Map::Buildings::BuildingsState::destroyBuilding(&DAT_BuildingsState,buildingID);
      return;
    }
    break;
  case -2:
    DAT_BuildingsState.buildings[buildingID].spriteID =
         (DAT_BuildingsState.buildings[buildingID].fireRelatedRNG1 & 7U) + 1;
    DAT_BuildingsState.buildings[buildingID].renderAnimation = 1;
    iVar2 = DAT_BuildingDefinedData.field417_0xa53c
            [DAT_BuildingsState.buildings[buildingID].animationIndex];
    if (iVar2 != -1) goto LAB_0041e704;
    DAT_BuildingsState.buildings[buildingID].state = 0;
    break;
  case -1:
    DAT_BuildingsState.buildings[buildingID].spriteID =
         (DAT_BuildingsState.buildings[buildingID].fireRelatedRNG1 & 7U) + 1;
    DAT_BuildingsState.buildings[buildingID].state = -2;
    DAT_BuildingsState.buildings[buildingID].field117_0x11a = 0;
    DAT_BuildingsState.buildings[buildingID].animationIndex = 0;
    DAT_BuildingsState.buildings[buildingID].animationFrame =
         (DAT_BuildingsState.buildings[buildingID].fireRelatedRNG1 & 7U) * 4 + 4;
    DAT_BuildingsState.buildings[buildingID].renderAnimation = 1;
    Map::TileMapState::updateBuildingGraphicsLayer(&DAT_TileMapState,buildingID);
    return;
  default:
    goto switchD_0041e6bd_caseD_5;
  }
  Map::TileMapState::updateBuildingGraphicsLayer(&DAT_TileMapState,buildingID);
switchD_0041e6bd_caseD_5:
  return;
}


// ================= _HoldStrong::UI::Rendering::RenderBuildingMenu_KillingPit @ 0043d790 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::UI::Rendering::RenderBuildingMenu_KillingPit(void)

{
  int yParam;
  char *textAddress;
  int xParam;
  TextAlignment alignment;
  BGR24 color;
  int fontSize;
  BOOLEnum keepOffsetX;
  int blendStrength;
  
  blendStrength = 0;
  keepOffsetX = FALSE;
  fontSize = 0x10;
  color = 0;
  alignment = TTA_LEFT;
  yParam = DAT_MenuHandlerState.y + 0x1d3;
  xParam = DAT_MenuHandlerState.x + 0x19;
                    /* added by script: "Killing Pit" */
  textAddress = Text::TextManager::getTextStringInGroupAtOffset
                          (&DAT_TextManagerObject,TEXT_IN_KILLING_PIT,0);
  Text::TextManager::renderTextToScreen
            (&DAT_TextManagerObject,textAddress,xParam,yParam,alignment,color,fontSize,keepOffsetX,
             blendStrength);
  return;
}


// ================= _HoldStrong::AI::AICState::shouldNotBuildKillingPits @ 004eca90 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "MappersEnumShort": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::AI::AICState::shouldNotBuildKillingPits
          (AICState *this,int playerID,MappersEnum commandBuildingType)

{
  BOOLEnum BVar1;
  
  BVar1 = FALSE;
  if (commandBuildingType == M_MAPPER_KILLING_PIT) {
    BVar1 = (BOOLEnum)(99 < DAT_AIVState.mapExtraInfo.playerTotalKillingPits[playerID]);
  }
  return BVar1;
}


// ================= _HoldStrong::Map::TileMapState::placeKillingPit @ 00514520 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::placeKillingPit
          (TileMapState *this,int param_1,uint param_2,uint param_3,undefined4 param_4,uint param_5,
          int param_6,int param_7)

{
  byte bVar1;
  uint uVar2;
  int buildingID;
  TileMapState *this_00;
  int iVar3;
  int tile;
  Logic2 flags2;
  
  uVar2 = param_3;
  bVar1 = DAT_TileMapState.Logic2Layer
          [DAT_ViewportRenderState.translationMatrix[param_3].addXgetTile + param_2];
  iVar3 = 0;
  buildingID = Buildings::BuildingsState::setupBuildingData
                         (&DAT_BuildingsState,param_1,param_2,param_3,param_7,(int)(short)param_4,
                          param_5,param_1,param_6);
  DAT_TileMapState.placedBuildingID = buildingID;
  if ((short)param_4 != 0x43) {
    param_7 = param_7 + -4;
    if (param_7 < 0) {
      param_7 = 0;
    }
  }
  do {
    getBuildingSizeIndexMappingData(iVar3,param_5);
    tile = DAT_ViewportRenderState.translationMatrix[DAT_TileMapState.buildingY + uVar2].addXgetTile
           + DAT_TileMapState.buildingX + param_2;
    if (iVar3 < 0x24) {
      *(int *)(DAT_BuildingsState.buildings[buildingID].workers + iVar3 * 2 + 8) = tile;
    }
    param_3._0_2_ = (ushort)buildingID;
    DAT_TileMapState.HeightLayer[tile] = (byte)param_7;
    DAT_TileMapState.BuildingLayer[tile] = (ushort)param_3;
    DAT_TileMapState.BuildingWasLayer[tile] = (uchar)(short)param_4;
    if ((short)param_4 != 0x43) {
      if ((bVar1 & 0x90) == 0) {
                    /* thick_scrub nor grass */
        flags2 = L2_EARTH_AND_STONES;
      }
      else {
                    /* bug:fixme: why set thick scrub if it was grass, why not what the original
                       terrain was? */
        flags2 = L2_THICK_SCRUB;
      }
      setTerrain(&DAT_TileMapState,param_1,tile,DAT_TileMapState.buildingY + uVar2,3,L_NONE,flags2);
    }
    iVar3 = iVar3 + 1;
    DAT_TileMapState.ChangedLayer[tile] = 2;
  } while (iVar3 < DAT_TileMapState.constructionTileCount);
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


// Treffer: 7
