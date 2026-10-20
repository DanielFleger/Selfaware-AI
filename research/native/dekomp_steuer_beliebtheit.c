// ================= _HoldStrong::Map::Buildings::BuildingsState::displayPopularityAndGoldPopups @ 0040a060 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Buildings::BuildingsState::displayPopularityAndGoldPopups
          (BuildingsState *this,int buildingID,int param_2,int param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  BOOLEnum BVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  EntityType entityType;
  
  iVar3 = buildingID;
  iVar8 = (int)DAT_BuildingsState.buildings[buildingID].owner;
  if (iVar8 == DAT_GameSynchronyState.currentPlayerSlotID) {
    return;
  }
  switch(DAT_BuildingsState.buildings[buildingID].buildingType) {
  case BT_MARKETPLACE:
    buildingID = 0x50;
    entityType = (param_2 != 0) + 0x2a;
    break;
  case BT_WELL:
  case BT_OILSMELTER:
  case BT_SIEGETENT:
  case BT_WHEATFARM:
  case BT_HOPFARM:
  case BT_APPLEFARM:
  case BT_DAIRYFARM:
  case BT_MILL:
  case BT_STABLES:
  case BT_CHAPEL:
  case BT_CHURCH:
  case BT_CATHEDRAL:
  case BT_UNKNOWN1:
  case BT_KEEPFOUR:
  case BT_KEEPFIVE:
  case BT_GATEHOUSELARGE:
  case BT_GATEHOUSESMALL:
  case BT_WOODGATE1:
  case BT_WOODGATE2:
  case BT_DRAWBRIDGE:
  case BT_TUNNEL:
  case BT_CAMPFIRE:
  case BT_SIGNPOST:
  case BT_PARADEGROUND:
  case BT_FIREBALLISTA:
    goto switchD_0040a09e_caseD_1b;
  case BT_MANORHOUSE:
  case BT_STONEKEEP:
  case BT_STRONGHOLD:
    entityType = 0x28;
    buildingID = 0x78;
    break;
  case BT_CAMPGROUND:
    entityType = 0x29;
    buildingID = 0x28;
    break;
  default:
    return;
  }
  BVar4 = Entities::EntityState::playerHasEntityOfType
                    (&DAT_EntityState,(int)DAT_BuildingsState.buildings[iVar3].owner,entityType);
  if (BVar4 == FALSE) {
    iVar7 = (int)(short)DAT_BuildingsState.buildings[iVar3].x;
    iVar5 = (int)DAT_BuildingsState.buildings[iVar3].widthOrHeight / 2;
    iVar2 = (short)DAT_BuildingsState.buildings[iVar3].y + iVar5;
    uVar6 = Entities::EntityState::spawnProjectileEntity
                      (&DAT_EntityState,0,(int)DAT_BuildingsState.buildings[iVar3].owner,0,
                       (iVar7 + iVar5) * 8,iVar2 * 8,
                       (uint)DAT_TileMapState.HeightLayer
                             [DAT_ViewportRenderState.translationMatrix[iVar2].addXgetTile + iVar7 +
                              iVar5] + buildingID,0,0,0,entityType,0);
    if (uVar6 != 0) {
      if (entityType == 0x28) {
        iVar3 = DAT_GameState.playerDataArray[iVar8].currentResources[0xf];
        piVar1 = &DAT_EntityState.entityArray[uVar6].displayValue;
        *piVar1 = iVar3;
        if (iVar3 < 0) {
          *piVar1 = 0;
          return;
        }
      }
      else {
        if (entityType == 0x29) {
          DAT_EntityState.entityArray[uVar6].displayValue =
               DAT_GameState.playerDataArray[iVar8].popularity / 100;
          return;
        }
        if (entityType == 0x2a) {
          DAT_EntityState.entityArray[uVar6].displayValue = param_3;
          DAT_EntityState.entityArray[uVar6].field83_0xc0 = (short)param_4 * 2 + 0x8d;
          return;
        }
        if (entityType == 0x2b) {
          DAT_EntityState.entityArray[uVar6].displayValue = param_3;
          DAT_EntityState.entityArray[uVar6].field83_0xc0 = (short)param_4 * 2 + 0x8d;
        }
      }
    }
  }
switchD_0040a09e_caseD_1b:
  return;
}


// ================= _HoldStrong::UI::Helpers::SetTaxesSetting_unknown @ 00433560 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl _HoldStrong::UI::Helpers::SetTaxesSetting_unknown(int taxesSettingUnk)

{
  if (DAT_GameCore.taxesSettingUnk == 0) {
    DAT_GameCore.taxesSettingUnk = taxesSettingUnk;
    DAT_GameCore.unknownScribeRelatedFlag_0x130 = TRUE;
    DAT_GameCore.taxestimeUnk = timeGetTime();
    DAT_GameCore.scribeAnimationFrame2 = 0;
  }
  return;
}


// ================= _HoldStrong::UI::Helpers::SomePopularityRelatedComputation @ 0043e540 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int _HoldStrong::UI::Helpers::SomePopularityRelatedComputation(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].popularity / 100
  ;
  if (99 < iVar1) {
    return 0xc;
  }
  if (iVar1 < 1) {
    return 2;
  }
  iVar2 = iVar1 >> 0x1f;
  iVar3 = iVar1 / 10 + iVar2;
  if (iVar1 < 0x32) {
    return (iVar3 + 3) - iVar2;
  }
  return (iVar3 + 2) - iVar2;
}


// ================= _HoldStrong::UI::Rendering::RenderStatusMenu_Popularity @ 0043e6c0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::UI::Rendering::RenderStatusMenu_Popularity(void)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  int iVar7;
  char *pcVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  byte bVar13;
  TextAlignment TVar14;
  BGR24 BVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  BOOLEnum BVar20;
  int iVar21;
  int iVar22;
  int local_2c;
  int local_1c;
  uint local_18;
  uint local_14;
  uint local_10;
  uint local_c;
  uint local_8;
  uint local_4;
  
  iVar12 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
           currentResources[0xf];
  iVar21 = 0;
  BVar20 = FALSE;
  iVar16 = 0x11;
  BVar15 = 0;
  TVar14 = TTA_LEFT;
  iVar7 = DAT_MenuHandlerState.y + 0x1d3;
  iVar9 = DAT_MenuHandlerState.x + 0x19;
  DAT_TextureRenderCoreObject.drawBufferChoiceValue = RT_SCREEN_MENU;
                    /* added by script: "Popularity" */
  pcVar8 = Text::TextManager::getTextStringInGroupAtOffset(&DAT_TextManagerObject,TEXT_REPORTS,1);
  Text::TextManager::renderTextToScreen
            (&DAT_TextManagerObject,pcVar8,iVar9,iVar7,TVar14,BVar15,iVar16,BVar20,iVar21);
  BVar20 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
           areCarnivalUnitsPresent;
  bVar13 = BVar20 != FALSE;
  if ((bool)bVar13) {
    local_1c = 0;
  }
  uVar11 = (uint)bVar13;
  sVar1 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].someCount58;
  uVar10 = uVar11;
  if (sVar1 != 0) {
    bVar13 = bVar13 + 1;
    uVar10 = uVar11 + 1;
    local_18 = uVar11;
  }
  sVar2 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].someCount59;
  uVar11 = uVar10;
  if (sVar2 != 0) {
    bVar13 = bVar13 + 1;
    uVar11 = uVar10 + 1;
    local_14 = uVar10;
  }
  sVar3 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].someCount54;
  uVar10 = uVar11;
  if (sVar3 != 0) {
    bVar13 = bVar13 + 1;
    uVar10 = uVar11 + 1;
    local_10 = uVar11;
  }
  sVar4 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].someCount55;
  uVar11 = uVar10;
  if (sVar4 != 0) {
    bVar13 = bVar13 + 1;
    uVar11 = uVar10 + 1;
    local_c = uVar10;
  }
  sVar5 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].someCount56;
  uVar10 = uVar11;
  if (sVar5 != 0) {
    bVar13 = bVar13 + 1;
    uVar10 = uVar11 + 1;
    local_8 = uVar11;
  }
  sVar6 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].someCount57;
  if (sVar6 != 0) {
    bVar13 = bVar13 + 1;
    local_4 = uVar10;
  }
  DAT_GameCore.field81_0x148 = (2 < bVar13) + 1;
  if (DAT_GameCore.field81_0x148 <= DAT_GameCore.field80_0x144) {
    DAT_GameCore.field80_0x144 = 0;
  }
  local_2c = (int)sVar6 + (int)sVar5 + (int)sVar4 + (int)sVar3 + (int)sVar2 + (int)sVar1;
  if (BVar20 != FALSE) {
    local_2c = local_2c + 400;
  }
  if (DAT_GameCore.field80_0x144 == 0) {
    iVar21 = 0x12;
    iVar9 = DAT_MenuHandlerState.y + 0x1db;
    iVar16 = DAT_MenuHandlerState.x + 0xc1;
    TVar14 = DAT_GameCore.field80_0x144;
    BVar15 = DAT_GameCore.field80_0x144;
    BVar20 = DAT_GameCore.field80_0x144;
    iVar7 = DAT_GameCore.field80_0x144;
                    /* added by script: "Food" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset(&DAT_TextManagerObject,TEXT_REPORTS,5);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar16,iVar9,TVar14,BVar15,iVar21,BVar20,iVar7);
  }
  if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].currentPopulation ==
      0) {
    uVar10 = 0;
  }
  else if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
           foodTypesInStock == 0) {
    uVar10 = 0xffffff38;
  }
  else {
    iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].rationsSetting
    ;
    if (iVar7 == 4) {
      uVar10 = 200;
    }
    else if (iVar7 == 3) {
      uVar10 = 100;
    }
    else if (iVar7 == 2) {
      uVar10 = 0;
    }
    else if (iVar7 == 1) {
      uVar10 = 0xffffff9c;
    }
    else {
      uVar10 = 0xffffff38;
      if (iVar7 != 0) {
        uVar10 = local_4;
      }
    }
  }
  iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
          foodTypesCurrentlyEaten;
  if ((iVar7 != 0) && (iVar7 != 1)) {
    if (iVar7 == 2) {
      uVar10 = uVar10 + 0x19;
    }
    else if (iVar7 == 3) {
      uVar10 = uVar10 + 0x32;
    }
    else if (iVar7 == 4) {
      uVar10 = uVar10 + 0x4b;
    }
  }
  if (DAT_GameCore.field80_0x144 == 0) {
    TransformAndRenderPercentage
              (DAT_MenuHandlerState.x + 0xab,DAT_MenuHandlerState.y + 0x1da,uVar10,FALSE);
  }
  if (DAT_GameCore.field80_0x144 == 0) {
    iVar21 = 0x12;
    iVar9 = DAT_MenuHandlerState.y + 499;
    iVar16 = DAT_MenuHandlerState.x + 0xc1;
    TVar14 = DAT_GameCore.field80_0x144;
    BVar15 = DAT_GameCore.field80_0x144;
    BVar20 = DAT_GameCore.field80_0x144;
    iVar7 = DAT_GameCore.field80_0x144;
                    /* added by script: "Tax" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset(&DAT_TextManagerObject,TEXT_REPORTS,6);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar16,iVar9,TVar14,BVar15,iVar21,BVar20,iVar7);
  }
  if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].currentPopulation ==
      0) {
    iVar12 = 0;
  }
  else if ((DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSliderUI
            < 3) && (iVar12 < 1)) {
    iVar12 = 0x19;
  }
  else {
    iVar12 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSetting;
    if (iVar12 == 0) {
      iVar12 = 0xaf;
    }
    else if (iVar12 == 1) {
      iVar12 = 0x7d;
    }
    else if (iVar12 == 2) {
      iVar12 = 0x4b;
    }
    else if (iVar12 == 3) {
      iVar12 = 0x19;
    }
    else if (iVar12 == 4) {
      iVar12 = -0x32;
    }
    else if (iVar12 == 5) {
      iVar12 = -100;
    }
    else if (iVar12 == 6) {
      iVar12 = -0x96;
    }
    else if (iVar12 == 7) {
      iVar12 = -200;
    }
    else if (iVar12 == 8) {
      iVar12 = -300;
    }
    else if (iVar12 == 9) {
      iVar12 = -400;
    }
    else {
      iVar12 = (-(uint)(iVar12 != 10) & 0xffffff9c) - 500;
    }
  }
  if (DAT_GameCore.field80_0x144 == 0) {
    TransformAndRenderPercentage
              (DAT_MenuHandlerState.x + 0xab,DAT_MenuHandlerState.y + 0x1f2,iVar12,FALSE);
  }
  if (DAT_GameCore.field80_0x144 == 0) {
    iVar21 = 0x12;
    iVar9 = DAT_MenuHandlerState.y + 0x20b;
    iVar16 = DAT_MenuHandlerState.x + 0xc1;
    TVar14 = DAT_GameCore.field80_0x144;
    BVar15 = DAT_GameCore.field80_0x144;
    BVar20 = DAT_GameCore.field80_0x144;
    iVar7 = DAT_GameCore.field80_0x144;
                    /* added by script: "Crowding" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset(&DAT_TextManagerObject,TEXT_REPORTS,7);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar16,iVar9,TVar14,BVar15,iVar21,BVar20,iVar7);
  }
  if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].currentPopulation ==
      0) {
    iVar7 = 0;
  }
  else {
    iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].crowding;
    if (iVar7 < 0x65) {
      iVar7 = 0;
    }
    else if (iVar7 < 0x79) {
      iVar7 = -0x32;
    }
    else if (iVar7 < 0x8d) {
      iVar7 = -100;
    }
    else if (iVar7 < 0xa1) {
      iVar7 = -0x96;
    }
    else {
      iVar7 = ((0xb4 < iVar7) - 1 & 0x32) - 0xfa;
    }
  }
  if (DAT_GameCore.field80_0x144 == 0) {
    TransformAndRenderPercentage
              (DAT_MenuHandlerState.x + 0xab,DAT_MenuHandlerState.y + 0x20a,iVar7,FALSE);
  }
  if (DAT_GameCore.field80_0x144 == 0) {
    iVar17 = 0x12;
    iVar16 = DAT_MenuHandlerState.y + 0x223;
    iVar21 = DAT_MenuHandlerState.x + 0xc1;
    TVar14 = DAT_GameCore.field80_0x144;
    BVar15 = DAT_GameCore.field80_0x144;
    BVar20 = DAT_GameCore.field80_0x144;
    iVar9 = DAT_GameCore.field80_0x144;
                    /* added by script: "Fear Factor" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset
                       (&DAT_TextManagerObject,TEXT_REPORTS,0xc);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar21,iVar16,TVar14,BVar15,iVar17,BVar20,iVar9);
  }
  uVar11 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].fearFactorLevel
  ;
  if ((int)uVar11 < 1) {
    if (uVar11 < 0x80000000) {
      iVar9 = 0;
    }
    else {
      iVar9 = uVar11 * 0x19;
    }
  }
  else {
    iVar9 = uVar11 * 0x19;
  }
  if (DAT_GameCore.field80_0x144 == 0) {
    TransformAndRenderPercentage
              (DAT_MenuHandlerState.x + 0xab,DAT_MenuHandlerState.y + 0x222,iVar9,FALSE);
  }
  if (DAT_GameCore.field80_0x144 == 0) {
    iVar18 = 0x12;
    iVar21 = DAT_MenuHandlerState.y + 0x1db;
    iVar17 = DAT_MenuHandlerState.x + 0x163;
    TVar14 = DAT_GameCore.field80_0x144;
    BVar15 = DAT_GameCore.field80_0x144;
    BVar20 = DAT_GameCore.field80_0x144;
    iVar16 = DAT_GameCore.field80_0x144;
                    /* added by script: "Religion" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset(&DAT_TextManagerObject,TEXT_REPORTS,10)
    ;
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar17,iVar21,TVar14,BVar15,iVar18,BVar20,iVar16);
  }
  iVar16 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
           blessedPeoplePercentage;
  if (iVar16 < 0x19) {
    iVar16 = 0;
  }
  else if (iVar16 < 0x32) {
    iVar16 = 0x32;
  }
  else if (iVar16 < 0x4b) {
    iVar16 = 100;
  }
  else {
    iVar16 = ((0x5e < iVar16) - 1 & 0xffffffce) + 200;
  }
  if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].ownsChurchUnk != 0)
  {
    iVar16 = iVar16 + 0x19;
  }
  if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].ownsCathedralUnk !=
      0) {
    iVar16 = iVar16 + 0x32;
  }
  if (DAT_GameCore.field80_0x144 == 0) {
    TransformAndRenderPercentage
              (DAT_MenuHandlerState.x + 0x14d,DAT_MenuHandlerState.y + 0x1da,iVar16,FALSE);
  }
  if (DAT_GameCore.field80_0x144 == 0) {
    iVar19 = 0x12;
    iVar17 = DAT_MenuHandlerState.y + 499;
    iVar18 = DAT_MenuHandlerState.x + 0x163;
    TVar14 = DAT_GameCore.field80_0x144;
    BVar15 = DAT_GameCore.field80_0x144;
    BVar20 = DAT_GameCore.field80_0x144;
    iVar21 = DAT_GameCore.field80_0x144;
                    /* added by script: "Ale coverage" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset
                       (&DAT_TextManagerObject,TEXT_REPORTS,0xb);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar18,iVar17,TVar14,BVar15,iVar19,BVar20,iVar21);
  }
  iVar21 = Game::GameStateStructures::computeAleCoverage
                     (&DAT_GameState,DAT_GameSynchronyState.currentPlayerSlotID);
  if (iVar21 < 0x19) {
    iVar21 = 0;
  }
  else if (iVar21 < 0x32) {
    iVar21 = 0x32;
  }
  else if (iVar21 < 0x4b) {
    iVar21 = 100;
  }
  else {
    iVar21 = ((99 < iVar21) - 1 & 0xffffffce) + 200;
  }
  if (DAT_GameCore.field80_0x144 == 0) {
    TransformAndRenderPercentage
              (DAT_MenuHandlerState.x + 0x14d,DAT_MenuHandlerState.y + 0x1f2,iVar21,FALSE);
  }
  if ((DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
       areCarnivalUnitsPresent != FALSE) &&
     (DAT_RenderingDefinedData.field1049_0x556cc[local_1c][0] == DAT_GameCore.field80_0x144)) {
    iVar17 = DAT_RenderingDefinedData.field1049_0x556cc[local_1c][2] + DAT_MenuHandlerState.y;
    iVar18 = DAT_RenderingDefinedData.field1049_0x556cc[local_1c][1] + DAT_MenuHandlerState.x;
    iVar22 = 0;
    BVar20 = FALSE;
    iVar19 = 0x12;
    BVar15 = 0;
    TVar14 = TTA_LEFT;
                    /* added by script: "Fair" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset(&DAT_TextManagerObject,TEXT_REPORTS,9);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar18,iVar17,TVar14,BVar15,iVar19,BVar20,iVar22);
    TransformAndRenderPercentage
              (DAT_MenuHandlerState.x + -0x16 +
               DAT_RenderingDefinedData.field1049_0x556cc[local_1c][1],
               DAT_MenuHandlerState.y + -1 + DAT_RenderingDefinedData.field1049_0x556cc[local_1c][2]
               ,400,FALSE);
  }
  if ((DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].someCount58 != 0)
     && (DAT_RenderingDefinedData.field1049_0x556cc[local_18][0] == DAT_GameCore.field80_0x144)) {
    iVar17 = DAT_RenderingDefinedData.field1049_0x556cc[local_18][2] + DAT_MenuHandlerState.y;
    iVar18 = DAT_RenderingDefinedData.field1049_0x556cc[local_18][1] + DAT_MenuHandlerState.x;
    iVar22 = 0;
    BVar20 = FALSE;
    iVar19 = 0x12;
    BVar15 = 0;
    TVar14 = TTA_LEFT;
                    /* added by script: "Marriage" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset
                       (&DAT_TextManagerObject,TEXT_SCENARIO,0x95);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar18,iVar17,TVar14,BVar15,iVar19,BVar20,iVar22);
    TransformAndRenderPercentage
              (DAT_RenderingDefinedData.field1049_0x556cc[local_18][1] + -0x16 +
               DAT_MenuHandlerState.x,
               DAT_RenderingDefinedData.field1049_0x556cc[local_18][2] + -1 + DAT_MenuHandlerState.y
               ,(int)DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                     someCount58,FALSE);
  }
  if ((DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].someCount59 != 0)
     && (DAT_RenderingDefinedData.field1049_0x556cc[local_14][0] == DAT_GameCore.field80_0x144)) {
    iVar17 = DAT_RenderingDefinedData.field1049_0x556cc[local_14][2] + DAT_MenuHandlerState.y;
    iVar18 = DAT_RenderingDefinedData.field1049_0x556cc[local_14][1] + DAT_MenuHandlerState.x;
    iVar22 = 0;
    BVar20 = FALSE;
    iVar19 = 0x12;
    BVar15 = 0;
    TVar14 = TTA_LEFT;
                    /* added by script: "Jester" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset
                       (&DAT_TextManagerObject,TEXT_SCENARIO,0x96);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar18,iVar17,TVar14,BVar15,iVar19,BVar20,iVar22);
    TransformAndRenderPercentage
              (DAT_RenderingDefinedData.field1049_0x556cc[local_14][1] + -0x16 +
               DAT_MenuHandlerState.x,
               DAT_RenderingDefinedData.field1049_0x556cc[local_14][2] + -1 + DAT_MenuHandlerState.y
               ,(int)DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                     someCount59,FALSE);
  }
  if ((DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].someCount54 != 0)
     && (DAT_RenderingDefinedData.field1049_0x556cc[local_10][0] == DAT_GameCore.field80_0x144)) {
    iVar17 = DAT_RenderingDefinedData.field1049_0x556cc[local_10][2] + DAT_MenuHandlerState.y;
    iVar18 = DAT_RenderingDefinedData.field1049_0x556cc[local_10][1] + DAT_MenuHandlerState.x;
    iVar22 = 0;
    BVar20 = FALSE;
    iVar19 = 0x12;
    BVar15 = 0;
    TVar14 = TTA_LEFT;
                    /* added by script: "Plague" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset
                       (&DAT_TextManagerObject,TEXT_SCENARIO,0x8b);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar18,iVar17,TVar14,BVar15,iVar19,BVar20,iVar22);
    TransformAndRenderPercentage
              (DAT_RenderingDefinedData.field1049_0x556cc[local_10][1] + -0x16 +
               DAT_MenuHandlerState.x,
               DAT_RenderingDefinedData.field1049_0x556cc[local_10][2] + -1 + DAT_MenuHandlerState.y
               ,(int)DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                     someCount54,FALSE);
  }
  if ((DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].someCount55 != 0)
     && (DAT_RenderingDefinedData.field1049_0x556cc[local_c][0] == DAT_GameCore.field80_0x144)) {
    iVar17 = DAT_RenderingDefinedData.field1049_0x556cc[local_c][2] + DAT_MenuHandlerState.y;
    iVar18 = DAT_RenderingDefinedData.field1049_0x556cc[local_c][1] + DAT_MenuHandlerState.x;
    iVar22 = 0;
    BVar20 = FALSE;
    iVar19 = 0x12;
    BVar15 = 0;
    TVar14 = TTA_LEFT;
                    /* added by script: "Lion Attack" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset
                       (&DAT_TextManagerObject,TEXT_SCENARIO,0x91);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar18,iVar17,TVar14,BVar15,iVar19,BVar20,iVar22);
    TransformAndRenderPercentage
              (DAT_MenuHandlerState.x + -0x16 +
               DAT_RenderingDefinedData.field1049_0x556cc[local_c][1],
               DAT_MenuHandlerState.y + -1 + DAT_RenderingDefinedData.field1049_0x556cc[local_c][2],
               (int)DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                    someCount55,FALSE);
  }
  if ((DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].someCount56 != 0)
     && (DAT_RenderingDefinedData.field1049_0x556cc[local_8][0] == DAT_GameCore.field80_0x144)) {
    iVar17 = DAT_RenderingDefinedData.field1049_0x556cc[local_8][2] + DAT_MenuHandlerState.y;
    iVar18 = DAT_RenderingDefinedData.field1049_0x556cc[local_8][1] + DAT_MenuHandlerState.x;
    iVar22 = 0;
    BVar20 = FALSE;
    iVar19 = 0x12;
    BVar15 = 0;
    TVar14 = TTA_LEFT;
                    /* added by script: "Bandits" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset
                       (&DAT_TextManagerObject,TEXT_SCENARIO,0x92);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar18,iVar17,TVar14,BVar15,iVar19,BVar20,iVar22);
    TransformAndRenderPercentage
              (DAT_RenderingDefinedData.field1049_0x556cc[local_8][1] + -0x16 +
               DAT_MenuHandlerState.x,
               DAT_RenderingDefinedData.field1049_0x556cc[local_8][2] + -1 + DAT_MenuHandlerState.y,
               (int)DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                    someCount56,FALSE);
  }
  if ((DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].someCount57 != 0)
     && (DAT_RenderingDefinedData.field1049_0x556cc[local_4][0] == DAT_GameCore.field80_0x144)) {
    iVar17 = DAT_RenderingDefinedData.field1049_0x556cc[local_4][2] + DAT_MenuHandlerState.y;
    iVar18 = DAT_RenderingDefinedData.field1049_0x556cc[local_4][1] + DAT_MenuHandlerState.x;
    iVar22 = 0;
    BVar20 = FALSE;
    iVar19 = 0x12;
    BVar15 = 0;
    TVar14 = TTA_LEFT;
                    /* added by script: "Fire!" */
    pcVar8 = Text::TextManager::getTextStringInGroupAtOffset
                       (&DAT_TextManagerObject,TEXT_SCENARIO,0xb3);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,pcVar8,iVar18,iVar17,TVar14,BVar15,iVar19,BVar20,iVar22);
    TransformAndRenderPercentage
              (DAT_RenderingDefinedData.field1049_0x556cc[local_4][1] + -0x16 +
               DAT_MenuHandlerState.x,
               DAT_RenderingDefinedData.field1049_0x556cc[local_4][2] + -1 + DAT_MenuHandlerState.y,
               (int)DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                    someCount57,FALSE);
  }
  iVar22 = 0;
  BVar20 = FALSE;
  iVar19 = 0x12;
  BVar15 = 0;
  TVar14 = TTA_LEFT;
  iVar17 = DAT_MenuHandlerState.y + 0x241;
  iVar18 = DAT_MenuHandlerState.x + 0xdc;
                    /* added by script: "In the coming month" */
  pcVar8 = Text::TextManager::getTextStringInGroupAtOffset(&DAT_TextManagerObject,TEXT_REPORTS,4);
  Text::TextManager::renderTextToScreen
            (&DAT_TextManagerObject,pcVar8,iVar18,iVar17,TVar14,BVar15,iVar19,BVar20,iVar22);
  TransformAndRenderPercentage
            (DAT_TextManagerObject.currentXOffset_0x0 + 0xfa + DAT_MenuHandlerState.x,
             DAT_MenuHandlerState.y + 0x241,
             local_2c + uVar10 + iVar12 + iVar7 + iVar9 + iVar16 + iVar21,TRUE);
  DAT_TextureRenderCoreObject.drawBufferChoiceValue = RT_MAP_GAME;
  return;
}


// ================= _HoldStrong::UI::MenuItemActionHandler_BuildingAndStatusMenu_PopularityMenuSwitchButtonUnk @ 0043f2b0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::UI::MenuItemActionHandler_BuildingAndStatusMenu_PopularityMenuSwitchButtonUnk(void)

{
  DAT_GameCore.field80_0x144 = DAT_GameCore.field80_0x144 ^ 1;
  return;
}


// ================= _HoldStrong::UI::MenuItemRenderFunction_BuildingAndStatusMenu_PopularityMenuSwitchButton @ 0043f2c0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::UI::MenuItemRenderFunction_BuildingAndStatusMenu_PopularityMenuSwitchButton
          (int param_1,...)

{
  if (DAT_GameCore.field81_0x148 != 1) {
    if (DAT_GameCore.field80_0x144 == 1) {
      DAT_CurrentButtonGmDataIndex = 0x73;
    }
    MenuItemRenderFunction_General_RenderCurrentButtonWithPossibleAlphaTexOnScreenMenuSurface();
    return;
  }
  return;
}


// ================= _HoldStrong::Game::GameStateStructures::calculateTaxIncomeForPlayer @ 00459080 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* Note that this income gets divided by 10 before being added to the players current gold
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Game::GameStateStructures::calculateTaxIncomeForPlayer
          (GameStateStructures *this,int playerIndex,int taxStep,int currentPeasants)

{
  int iVar1;
  
  iVar1 = ((taxStep + -1) * currentPeasants) / 2;
                    /* Is Skirmish */
  if (DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) {
                    /* Is NOT Player */
    if (DAT_GameSynchronyState.currentPlayerFullIDArray[playerIndex] == -1) {
                    /* Is AI */
      if (DAT_GameSynchronyState.currentAIArray[playerIndex] != 0) {
                    /* balance is towards ai players */
        if (DAT_GameSynchronyState.skirmishCurrentAdvantageBalance == 4) goto LAB_004590f4;
        if (DAT_GameSynchronyState.skirmishCurrentAdvantageBalance == 5) {
                    /* multiply by 250, divide by 100 */
          return (iVar1 * 0xfa) / 100;
        }
      }
    }
    else {
                    /* balance is towards human players */
      if (DAT_GameSynchronyState.skirmishCurrentAdvantageBalance == 1) {
LAB_004590f4:
                    /* multiply by 150, divide by 100 */
        return (iVar1 * 0x96) / 100;
      }
      if (DAT_GameSynchronyState.skirmishCurrentAdvantageBalance == 2) {
                    /* multiply by 120, divide by 100 */
        iVar1 = (iVar1 * 0x78) / 100;
      }
    }
  }
  return iVar1;
}


// ================= _HoldStrong::Game::GameStateStructures::calculateTaxBribeExpenseForPlayer @ 00459140 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Game::GameStateStructures::calculateTaxBribeExpenseForPlayer
          (GameStateStructures *this,int playerIndex,int taxStep,int currentPopulation)

{
  int iVar1;
  
  iVar1 = ((5 - taxStep) * currentPopulation) / 2;
  if (DAT_GameState.playerDataArray[playerIndex].currentResources[0xf] < 1) {
    iVar1 = 0;
  }
  return iVar1;
}


// ================= _HoldStrong::Game::GameStateStructures::getNumberToDisplayPlayerTaxIncome @ 00459170 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Game::GameStateStructures::getNumberToDisplayPlayerTaxIncome
          (GameStateStructures *this,int playerIndex,int taxStep,int currentPopulation)

{
  int iVar1;
  
  iVar1 = 0;
  if (3 < taxStep) {
    iVar1 = calculateTaxIncomeForPlayer(&DAT_GameState,playerIndex,taxStep,currentPopulation);
    iVar1 = iVar1 * 4;
  }
  return iVar1 / 10;
}


// ================= _HoldStrong::Map::Version::initPopularityAndRecruitableDefaults @ 0045ad10 =================

/* Initialises default values for all 8 players after a map version upgrade. Copies each player's
   storedPopularityPercent into someCount44, and sets all euro and merc recruitable flags to 1
   (enabled) across both the primary and copy arrays in mapAndTime. Called as part of the map
   versioning/upgrade pipeline.
   
   renamed by: Claude Sonnet 4.6 */

void _HoldStrong::Map::Version::initPopularityAndRecruitableDefaults(void)

{
  DAT_GameState.playerDataArray[1].someCount44 =
       (short)DAT_GameState.playerDataArray[1].storedPopularityPercent;
  DAT_GameState.playerDataArray[2].someCount44 =
       (short)DAT_GameState.playerDataArray[2].storedPopularityPercent;
  DAT_GameState.playerDataArray[4].someCount44 =
       (short)DAT_GameState.playerDataArray[4].storedPopularityPercent;
  DAT_GameState.playerDataArray[3].someCount44 =
       (short)DAT_GameState.playerDataArray[3].storedPopularityPercent;
  DAT_GameState.playerDataArray[5].someCount44 =
       (short)DAT_GameState.playerDataArray[5].storedPopularityPercent;
  DAT_GameState.playerDataArray[7].someCount44 =
       (short)DAT_GameState.playerDataArray[7].storedPopularityPercent;
  DAT_GameState.playerDataArray[6].someCount44 =
       (short)DAT_GameState.playerDataArray[6].storedPopularityPercent;
  DAT_GameState.playerDataArray[8].someCount44 =
       (short)DAT_GameState.playerDataArray[8].storedPopularityPercent;
  DAT_GameState.mapAndTime.euroRecruitable[0] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[0] = 1;
  DAT_GameState.mapAndTime.euroRecruitable[1] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[1] = 1;
  DAT_GameState.mapAndTime.euroRecruitable[2] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[2] = 1;
  DAT_GameState.mapAndTime.euroRecruitable[3] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[3] = 1;
  DAT_GameState.mapAndTime.euroRecruitable[4] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[4] = 1;
  DAT_GameState.mapAndTime.euroRecruitable[5] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[5] = 1;
  DAT_GameState.mapAndTime.euroRecruitable[6] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[6] = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_0 = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_1_b = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_2 = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_3_b = 1;
  DAT_GameState.mapAndTime.field2257_0xda8 = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_6_a = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_1_a = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_3_a_and_6_b = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_6_c = 1;
  return;
}


// ================= _HoldStrong::Game::GameStateStructures::updatePopularity @ 0045b830 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Game::GameStateStructures::updatePopularity(GameStateStructures *this)

{
  int *piVar1;
  int *piVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  BOOLEnum BVar7;
  uint uVar8;
  SpeechEffectID speechID;
  uint local_10;
  uint local_c;
  int _playerID;
  uint _popChangeFearFactor;
  
  _popChangeFearFactor = 0;
  if (DAT_GameState.mapAndTime.weekChanged != 0) {
    recomputeReligionBonuses(&DAT_GameState);
    _playerID = 1;
    do {
      if ((0 < DAT_GameState.playerDataArray[_playerID].keep.id) &&
         (0 < DAT_GameState.playerDataArray[_playerID].campground.id)) {
        if ((DAT_GameCore.gameMode_2 == GM_BUILDERUnk) &&
           (DAT_MapPropertiesState.SEC_U3_MapType2_1 == MT_SIEGE)) {
          DAT_GameState.playerDataArray[_playerID].popularity =
               -(uint)(DAT_GameSynchronyState.currentPlayerSlotID != 2) & 10000;
        }
        else {
          iVar4 = DAT_GameState.playerDataArray[_playerID].currentPopulation;
          if ((iVar4 < 4) && (DAT_GameState.playerDataArray[_playerID].popularity < 5000)) {
                    /* 75(00) */
            DAT_GameState.playerDataArray[_playerID].popularity = 0x1d4c;
          }
          else {
            iVar5 = DAT_GameState.playerDataArray[_playerID].currentResources[0xf];
            piVar1 = &DAT_GameState.playerDataArray[_playerID].popularity;
            DAT_GameState.playerDataArray[_playerID].storedPopularityPercent =
                 DAT_GameState.playerDataArray[_playerID].popularity;
            iVar6 = DAT_GameState.playerDataArray[_playerID].foodTypesInStock;
            local_10 = 0;
            if (iVar6 < 1) {
              piVar2 = &DAT_GameState.playerDataArray[_playerID].weeksWithoutFood;
              *piVar2 = *piVar2 + 1;
            }
            else {
              DAT_GameState.playerDataArray[_playerID].weeksWithoutFood = 0;
            }
            if (iVar4 < 1) {
              uVar8 = 200;
            }
            else if (iVar6 < 1) {
                    /* -200 */
              uVar8 = 0xffffff38;
            }
            else {
              iVar4 = DAT_GameState.playerDataArray[_playerID].rationsSetting;
              if (iVar4 == 0) {
                    /* -200 */
                uVar8 = 0xffffff38;
              }
              else if (iVar4 == 1) {
                    /* -101? */
                uVar8 = 0xffffff9c;
              }
              else if (iVar4 == 2) {
                uVar8 = 0;
              }
              else if (iVar4 == 4) {
                uVar8 = 200;
              }
              else {
                uVar8 = 100;
                if (iVar4 != 3) {
                    /* different way of saying 0 */
                  uVar8 = _popChangeFearFactor;
                }
              }
            }
            iVar4 = DAT_GameState.playerDataArray[_playerID].foodTypesCurrentlyEaten;
            if (iVar4 == 2) {
              uVar8 = uVar8 + 0x19;
            }
            else if (iVar4 == 3) {
              uVar8 = uVar8 + 0x32;
            }
            else if (iVar4 == 4) {
              uVar8 = uVar8 + 0x4b;
            }
                    /* sets popularity */
            *piVar1 = *piVar1 + uVar8;
            DAT_GameState.playerDataArray[_playerID].popularityChangeBasedOnFood = uVar8;
            if ((int)uVar8 < 0) {
              local_10 = uVar8;
            }
            local_c = (uint)((int)uVar8 < 0);
            iVar4 = DAT_GameState.playerDataArray[_playerID].crowding;
            if (iVar4 < 0x65) {
              uVar8 = 0;
            }
            else if (iVar4 < 0x79) {
                    /* -50 */
              uVar8 = 0xffffffce;
            }
            else if (iVar4 < 0x8d) {
                    /* -100 */
              uVar8 = 0xffffff9c;
            }
            else if (iVar4 < 0xa1) {
                    /* -150 */
              uVar8 = 0xffffff6a;
            }
            else {
                    /* -200 or -250 */
              uVar8 = ((0xb4 < iVar4) - 1 & 0x32) - 0xfa;
            }
            *piVar1 = *piVar1 + uVar8;
            DAT_GameState.playerDataArray[_playerID].popularityChangeBasedOnCrowding = uVar8;
            if ((int)uVar8 < (int)local_10) {
              local_c = 2;
              local_10 = uVar8;
            }
            iVar4 = DAT_GameState.playerDataArray[_playerID].taxesSetting;
            if ((iVar4 < 3) && (iVar5 < 1)) {
              uVar8 = 0x19;
            }
            else if (iVar4 == 0) {
              uVar8 = 0xaf;
            }
            else if (iVar4 == 1) {
              uVar8 = 0x7d;
            }
            else if (iVar4 == 2) {
              uVar8 = 0x4b;
            }
            else if (iVar4 == 3) {
              uVar8 = 0x19;
            }
            else if (iVar4 == 4) {
                    /* -50 */
              uVar8 = 0xffffffce;
            }
            else if (iVar4 == 5) {
                    /* -100 */
              uVar8 = 0xffffff9c;
            }
            else if (iVar4 == 6) {
                    /* -150 */
              uVar8 = 0xffffff6a;
            }
            else if (iVar4 == 7) {
                    /* -200 */
              uVar8 = 0xffffff38;
            }
            else if (iVar4 == 8) {
                    /* -300 */
              uVar8 = 0xfffffed4;
            }
            else if (iVar4 == 9) {
                    /* -400 */
              uVar8 = 0xfffffe70;
            }
            else {
                    /* True is always 1, False is 0
                       -100
                       so if _taxes == 11: -600! */
              uVar8 = (-(uint)(iVar4 != 10) & 0xffffff9c) - 500;
            }
            *piVar1 = *piVar1 + uVar8;
            iVar4 = *piVar1;
            DAT_GameState.playerDataArray[_playerID].popularityChangeBasedOnTax = uVar8;
            if ((int)uVar8 < (int)local_10) {
              local_c = 4;
              local_10 = uVar8;
            }
            DAT_GameState.playerDataArray[_playerID].field642_0x2168 = 0;
            if (0 < (int)local_10) {
              local_10 = 0;
              local_c = 3;
            }
            uVar8 = -(uint)(DAT_GameState.playerDataArray[_playerID].areCarnivalUnitsPresent !=
                           FALSE) & 400;
            *piVar1 = iVar4 + uVar8;
            DAT_GameState.playerDataArray[_playerID].popularityChangeBasedOnFair = uVar8;
            if ((int)uVar8 < (int)local_10) {
              local_c = 5;
              local_10 = uVar8;
            }
            iVar4 = DAT_GameState.playerDataArray[_playerID].blessedPeoplePercentage;
            if (iVar4 < 0x19) {
              uVar8 = 0;
            }
            else if (iVar4 < 0x32) {
              uVar8 = 0x32;
            }
            else if (iVar4 < 0x4b) {
              uVar8 = 100;
            }
            else {
                    /* -50 */
                    /* < 95? => 150
                       >= 95? 200 */
              uVar8 = ((0x5e < iVar4) - 1 & 0xffffffce) + 200;
            }
            if (DAT_GameState.playerDataArray[_playerID].ownsChurchUnk != 0) {
              uVar8 = uVar8 + 0x19;
            }
            if (DAT_GameState.playerDataArray[_playerID].ownsCathedralUnk != 0) {
              uVar8 = uVar8 + 0x32;
            }
            if ((int)uVar8 < 0) {
              uVar8 = 0;
            }
            *piVar1 = *piVar1 + uVar8;
            piVar2 = &DAT_GameState.playerDataArray[_playerID].popularityReligionBasedDiv25;
            *piVar2 = *piVar2 + (int)uVar8 / 0x19;
            DAT_GameState.playerDataArray[_playerID].popularityChangeBasedOnReligion = uVar8;
            if ((int)uVar8 < (int)local_10) {
              local_c = 6;
              local_10 = uVar8;
            }
            uVar8 = computeAleCoverage(&DAT_GameState,_playerID);
            DAT_GameState.playerDataArray[_playerID].beerPercentage = uVar8;
            if ((int)uVar8 < 0x19) {
              uVar8 = 0;
            }
            else if ((int)uVar8 < 0x32) {
              uVar8 = 0x32;
            }
            else if ((int)uVar8 < 0x4b) {
              uVar8 = 100;
            }
            else {
                    /* if aleCoverage > 99: 200; else: 150 */
              uVar8 = ((99 < (int)uVar8) - 1 & 0xffffffce) + 200;
            }
            *piVar1 = *piVar1 + uVar8;
            DAT_GameState.playerDataArray[_playerID].popularityChangeAleBased = uVar8;
            if ((int)uVar8 < (int)local_10) {
              local_c = 7;
              local_10 = uVar8;
            }
            _popChangeFearFactor = DAT_GameState.playerDataArray[_playerID].fearFactorLevel;
            if ((int)_popChangeFearFactor < 1) {
              if (_popChangeFearFactor < 0x80000000) {
                _popChangeFearFactor = 0;
              }
              else {
                    /* 25 */
                _popChangeFearFactor = _popChangeFearFactor * 0x19;
              }
            }
            else {
              _popChangeFearFactor = _popChangeFearFactor * 0x19;
            }
            *piVar1 = *piVar1 + _popChangeFearFactor;
            iVar4 = *piVar1;
            DAT_GameState.playerDataArray[_playerID].popularityChangeFearFactorBased =
                 _popChangeFearFactor;
            if ((int)_popChangeFearFactor < (int)local_10) {
              local_c = 8;
            }
            sVar3 = DAT_GameState.playerDataArray[_playerID].someCount48;
            if (sVar3 == 0) {
              DAT_GameState.playerDataArray[_playerID].someCount54 = 0;
              DAT_GameState.playerDataArray[_playerID].someCount60 = 0;
            }
            else {
              DAT_GameState.playerDataArray[_playerID].someCount48 = sVar3 + -1;
              iVar5 = DAT_GameState.playerDataArray[_playerID].someCount60;
              if (iVar5 != 0) {
                DAT_GameState.playerDataArray[_playerID].someCount60 = iVar5 + 1;
              }
              iVar5 = DAT_GameState.playerDataArray[_playerID].someCount60;
              if (iVar5 < 1) {
                *piVar1 = iVar4 + -0x96;
                    /* 150 */
                DAT_GameState.playerDataArray[_playerID].someCount54 = -0x96;
              }
              else if (iVar5 < 6) {
                *piVar1 = iVar4 + -0x7d;
                    /* 125 */
                DAT_GameState.playerDataArray[_playerID].someCount54 = -0x7d;
              }
              else if (iVar5 < 0xb) {
                *piVar1 = iVar4 + -100;
                DAT_GameState.playerDataArray[_playerID].someCount54 = -100;
              }
              else if (iVar5 < 0x10) {
                *piVar1 = iVar4 + -0x4b;
                DAT_GameState.playerDataArray[_playerID].someCount54 = -0x4b;
              }
              else if (iVar5 < 0x15) {
                *piVar1 = iVar4 + -0x32;
                DAT_GameState.playerDataArray[_playerID].someCount54 = -0x32;
              }
              else {
                    /* 25 or 0 */
                uVar8 = (0x19 < iVar5) - 1 & 0xffffffe7;
                *piVar1 = iVar4 + uVar8;
                DAT_GameState.playerDataArray[_playerID].someCount54 = (short)uVar8;
              }
            }
            sVar3 = DAT_GameState.playerDataArray[_playerID].someCount49;
            if (sVar3 == 0) {
              DAT_GameState.playerDataArray[_playerID].someCount55 = 0;
            }
            else {
              *piVar1 = *piVar1 + -0x4b;
              DAT_GameState.playerDataArray[_playerID].someCount49 = sVar3 + -1;
              DAT_GameState.playerDataArray[_playerID].someCount55 = -0x4b;
            }
            sVar3 = DAT_GameState.playerDataArray[_playerID].someCount50;
            if (sVar3 == 0) {
              DAT_GameState.playerDataArray[_playerID].someCount56 = 0;
            }
            else {
              *piVar1 = *piVar1 + -0x7d;
              DAT_GameState.playerDataArray[_playerID].someCount50 = sVar3 + -1;
              DAT_GameState.playerDataArray[_playerID].someCount56 = -0x7d;
            }
            sVar3 = DAT_GameState.playerDataArray[_playerID].someCount51;
            if (sVar3 == 0) {
              DAT_GameState.playerDataArray[_playerID].someCount57 = 0;
            }
            else {
              *piVar1 = *piVar1 + -0x32;
              DAT_GameState.playerDataArray[_playerID].someCount51 = sVar3 + -1;
              DAT_GameState.playerDataArray[_playerID].someCount57 = -0x32;
            }
            sVar3 = DAT_GameState.playerDataArray[_playerID].someCount52;
            if (sVar3 == 0) {
              DAT_GameState.playerDataArray[_playerID].someCount58 = 0;
            }
            else {
              *piVar1 = *piVar1 + 200;
              DAT_GameState.playerDataArray[_playerID].someCount52 = sVar3 + -1;
              DAT_GameState.playerDataArray[_playerID].someCount58 = 200;
            }
            sVar3 = DAT_GameState.playerDataArray[_playerID].someCount53;
            if (sVar3 == 0) {
              DAT_GameState.playerDataArray[_playerID].someCount59 = 0;
            }
            else {
              *piVar1 = *piVar1 + 0x32;
              DAT_GameState.playerDataArray[_playerID].someCount53 = sVar3 + -1;
              DAT_GameState.playerDataArray[_playerID].someCount59 = 0x32;
            }
            iVar4 = *piVar1;
            DAT_GameState.playerDataArray[_playerID].someCount40 = local_c;
            if (iVar4 < 0) {
              *piVar1 = 0;
            }
            if (10000 < *piVar1) {
              *piVar1 = 10000;
            }
            iVar4 = DAT_GameState.playerDataArray[_playerID].storedPopularityPercent;
            iVar5 = *piVar1;
            if (iVar5 < iVar4) {
              if (((iVar5 + 500 < (int)DAT_GameState.playerDataArray[_playerID].someCount44) &&
                  (3 < DAT_GameState.playerDataArray[_playerID].currentPopulation)) &&
                 (DAT_GameState.playerDataArray[_playerID].field25_0x40 == 0)) {
                iVar4 = *piVar1;
                DAT_GameState.playerDataArray[_playerID].field25_0x40 = 1;
                DAT_GameState.playerDataArray[_playerID].someCount44 = (short)iVar4;
                if ((_playerID == DAT_GameSynchronyState.currentPlayerSlotID) &&
                   (BVar7 = Audio::MSS::SoundSystem::shouldSoundXNotBePlaying(&DAT_SoundSystemState)
                   , BVar7 == FALSE)) {
                  speechID = SEID_POP_FALLING;
LAB_0045bf23:
                  Audio::SFX::SFXState::playSpeechSFX(&DAT_SFXState,speechID);
                }
              }
            }
            else if ((((iVar4 < iVar5) &&
                      ((int)DAT_GameState.playerDataArray[_playerID].someCount44 < iVar5 + -500)) &&
                     (3 < DAT_GameState.playerDataArray[_playerID].currentPopulation)) &&
                    (DAT_GameState.playerDataArray[_playerID].field25_0x40 == 1)) {
              DAT_GameState.playerDataArray[_playerID].field25_0x40 = 0;
              DAT_GameState.playerDataArray[_playerID].someCount44 = (short)*piVar1;
              if ((_playerID == DAT_GameSynchronyState.currentPlayerSlotID) &&
                 (BVar7 = Audio::MSS::SoundSystem::shouldSoundXNotBePlaying(&DAT_SoundSystemState),
                 BVar7 == FALSE)) {
                speechID = SEID_POP_RISING;
                goto LAB_0045bf23;
              }
            }
          }
        }
      }
      _playerID = _playerID + 1;
    } while (_playerID < 9);
  }
  return;
}


// ================= _HoldStrong::Game::GameStateStructures::updateTaxing @ 0045bf50 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Game::GameStateStructures::updateTaxing(GameStateStructures *this)

{
  int *piVar1;
  int iVar2;
  int *piVar3;
  int playerIndex;
  
  playerIndex = 1;
  piVar3 = &DAT_GameState.playerDataArray[1].taxesSetting;
  do {
    if ((0 < ((BuildingEntryInfo *)(piVar3 + -0x83d))->id) &&
       (0 < ((BuildingEntryInfo *)(piVar3 + -0x7ed))->id)) {
      iVar2 = *piVar3;
      if (iVar2 < 3) {
        iVar2 = calculateTaxBribeExpenseForPlayer(&DAT_GameState,playerIndex,iVar2,piVar3[-2]);
        piVar3[-0x11] = piVar3[-0x11] + iVar2;
      }
      else if (3 < iVar2) {
        iVar2 = calculateTaxIncomeForPlayer(&DAT_GameState,playerIndex,iVar2,piVar3[-2]);
        piVar3[-0xc] = piVar3[-0xc] + iVar2;
      }
      if (DAT_GameState.mapAndTime.monthChanged != 0) {
        piVar3[-0x11] = piVar3[-0x11] / 10;
        iVar2 = piVar3[-0xc] / 10;
        piVar3[-0x71f] = piVar3[-0x71f] + iVar2;
        piVar3[-0xc] = iVar2;
        piVar1 = DAT_GameSynchronyState.finalResults.finalGold + playerIndex;
        *piVar1 = *piVar1 + iVar2;
        piVar1 = piVar3 + -0x71f;
        *piVar1 = *piVar1 - piVar3[-0x11];
        if (*piVar1 < 0) {
          piVar3[-0x71f] = 0;
        }
        piVar3[-0x12] = piVar3[-0x11];
        piVar3[-0xd] = piVar3[-0xc];
        piVar3[-0xc] = 0;
        piVar3[-0x11] = 0;
        *(short *)((int)piVar3 + 0xc2) = *(short *)(piVar3 + 0x30);
        *(short *)(piVar3 + 0x30) = (short)piVar3[-0x71f];
        piVar3[-0x84d] = 0;
      }
    }
    playerIndex = playerIndex + 1;
    piVar3 = piVar3 + 0xe7d;
  } while (playerIndex < 9);
  return;
}


// ================= _HoldStrong::UI::MenuItemActionHandler_BuildingAndStatusMenu_TaxSlider @ 00465560 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::UI::MenuItemActionHandler_BuildingAndStatusMenu_TaxSlider
          (int param_1,int param_2,int *minValue,int *maxValue,int *currentValue)

{
  int *piVar1;
  int iVar2;
  
  switch(param_2) {
  case 1:
    *minValue = 0;
    *maxValue = 0xb;
  case 4:
    *currentValue =
         DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSliderUI;
    return;
  case 2:
  case 3:
    DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSliderUI =
         *currentValue;
    return;
  case 5:
    iVar2 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSliderUI;
    piVar1 = &DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
              taxesSliderUI;
    if (0 < iVar2) {
      *piVar1 = iVar2 + -1;
    }
    *currentValue = *piVar1;
    return;
  case 6:
    iVar2 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSliderUI;
    piVar1 = &DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
              taxesSliderUI;
    if (iVar2 < 0xb) {
      *piVar1 = iVar2 + 1;
    }
    *currentValue = *piVar1;
  default:
    return;
  }
}


// ================= _HoldStrong::UI::MenuItemActionHandler_BuildingAndStatusMenu_TaxArrowButtons @ 004656a0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::UI::MenuItemActionHandler_BuildingAndStatusMenu_TaxArrowButtons(int param_1,...)

{
  int iVar1;
  
  if (param_1 == -2) {
    iVar1 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSliderUI;
    if (iVar1 < 0xb) {
      DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSliderUI =
           iVar1 + 1;
    }
  }
  else if (param_1 == -1) {
    iVar1 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSliderUI;
    if (0 < iVar1) {
      DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSliderUI =
           iVar1 + -1;
      return;
    }
  }
  return;
}


// ================= _HoldStrong::Commands::QueueChangeTaxes @ 00465700 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Commands::QueueChangeTaxes(void)

{
  int iVar1;
  BOOLEnum BVar2;
  DWORD DVar3;
  
  iVar1 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSliderUI;
  if (iVar1 != DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
               taxesSetting2) {
    if (DAT_GameCore.gameMode_2 == GM_CRUSADER_TUTORIAL) {
      BVar2 = Game::Tutorial_IsActionAllowed(4,iVar1);
      if (BVar2 == FALSE) {
        DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSliderUI =
             DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].taxesSetting2
        ;
        Global::SetTutorialHintActiveWithTimestamp();
        return;
      }
      Global::SetTutorialBuildingActionState
                (0xd,DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                     taxesSliderUI);
    }
    iVar1 = DAT_GameSynchronyState.currentPlayerSlotID;
    DVar3 = timeGetTime();
    DAT_GameState.playerDataArray[iVar1].timeTaxesOrRationsChange = DVar3;
    DAT_GameState.playerDataArray[iVar1].taxesSetting2 =
         DAT_GameState.playerDataArray[iVar1].taxesSliderUI;
    DAT_GameSynchronyState.DAT_GameCommandParam0 =
         DAT_GameState.playerDataArray[iVar1].taxesSliderUI;
    Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_CHANGE_TAXES);
  }
  return;
}


// ================= _HoldStrong::UI::MenuItemRenderFunction_BuildingAndStatusMenu_TaxArrowButtons @ 004657b0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::UI::MenuItemRenderFunction_BuildingAndStatusMenu_TaxArrowButtons(int param_1,...)

{
  int xParam;
  char *textAddress;
  int yParam;
  TextAlignment alignment;
  BGR24 color;
  int fontSize;
  BOOLEnum keepOffsetX;
  int blendStrength;
  
  MenuItemRenderFunction_General_RenderCurrentButtonWithPossibleAlphaTexOnScreenMenuSurface();
  if (-1 < param_1) {
    blendStrength = 0;
    keepOffsetX = FALSE;
    fontSize = 0x11;
    color = 0;
    alignment = TTA_CENTER;
    yParam = DAT_ButtonY + 4;
    xParam = DAT_ButtonW / 2 + DAT_ButtonX;
    textAddress = Text::TextManager::getTextStringInGroupAtOffset
                            (&DAT_TextManagerObject,TEXT_IN_KEEP,param_1);
    Text::TextManager::renderTextToScreen
              (&DAT_TextManagerObject,textAddress,xParam,yParam,alignment,color,fontSize,keepOffsetX
               ,blendStrength);
  }
  return;
}


// ================= _HoldStrong::Global::ChangeTaxes @ 00465800 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl _HoldStrong::Global::ChangeTaxes(int playerID,int taxesSetting)

{
  DAT_GameState.playerDataArray[playerID].taxesSetting = taxesSetting;
  return;
}


// ================= _HoldStrong::Map::Navigation::DirectionAlgorithmState::setAxisBasedDistanceResult @ 0046cc80 =================

/* Sets a low value and high value, depending on which axis is further away
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::Navigation::DirectionAlgorithmState::setAxisBasedDistanceResult
          (DirectionAlgorithmState *this,int destinationXPosition,int destinationYPosition,
          int fromXPosition,int fromYPosition)

{
  if (fromXPosition < destinationXPosition) {
    DAT_DirectionAlgorithmState.distanceX = destinationXPosition - fromXPosition;
  }
  else {
    DAT_DirectionAlgorithmState.distanceX = fromXPosition - destinationXPosition;
  }
  if (fromYPosition < destinationYPosition) {
    DAT_DirectionAlgorithmState.distanceY = destinationYPosition - fromYPosition;
  }
  else {
    DAT_DirectionAlgorithmState.distanceY = fromYPosition - destinationYPosition;
  }
  if (DAT_DirectionAlgorithmState.distanceX < DAT_DirectionAlgorithmState.distanceY) {
    DAT_DirectionAlgorithmState.distanceLow = DAT_DirectionAlgorithmState.distanceX;
    DAT_DirectionAlgorithmState.distanceHigh = DAT_DirectionAlgorithmState.distanceY;
    return DAT_DirectionAlgorithmState.distanceX + DAT_DirectionAlgorithmState.distanceY;
  }
  DAT_DirectionAlgorithmState.distanceHigh = DAT_DirectionAlgorithmState.distanceX;
  DAT_DirectionAlgorithmState.distanceLow = DAT_DirectionAlgorithmState.distanceY;
  return DAT_DirectionAlgorithmState.distanceX + DAT_DirectionAlgorithmState.distanceY;
}


// ================= _HoldStrong::Commands::ClickChangeTaxes @ 00482360 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Commands::ClickChangeTaxes(void)

{
  DAT_GameSynchronyState.DAT_CommandSize = 1;
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_SCHEDULE_AND_SEND) {
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    return;
  }
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_EXECUTE) {
    DAT_GameSynchronyState.DAT_GameCommandParam0 = DAT_GameSynchronyState.DAT_CommandActionPlan;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    Global::ChangeTaxes(DAT_GameSynchronyState.protocolInvokerPlayerID,
                        DAT_GameSynchronyState.DAT_GameCommandParam0);
  }
  return;
}


// ================= _HoldStrong::AI::AICState::aiUpdateTaxesAndRations @ 004caea0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::AI::AICState::aiUpdateTaxesAndRations(AICState *this,int playerID)

{
  AITypeInt AVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  AVar1 = DAT_GameState.playerDataArray[playerID].aiType;
  if (AVar1 == AIT_NULL) {
    return;
  }
  iVar2 = (AVar1 + ~AIT_NULL) * 0x2a4;
  iVar4 = DAT_GameState.playerDataArray[playerID].popularity;
                    /* criticalPopularity */
  if (*(int *)((int)&DAT_AICState + iVar2 + 0x18) < iVar4) {
                    /* lowestPopularity */
    if (*(int *)((int)&DAT_AICState + iVar2 + 0x1c) < iVar4) {
                    /* highestPopularity */
      if (*(int *)((int)&DAT_AICState + iVar2 + 0x20) <= iVar4) {
        DAT_GameState.playerDataArray[playerID].aiPopularityDecisionValue = 0;
      }
    }
    else {
      DAT_GameState.playerDataArray[playerID].aiPopularityDecisionValue = 1;
    }
  }
  else {
    DAT_GameState.playerDataArray[playerID].aiPopularityDecisionValue = 2;
  }
  iVar5 = DAT_GameState.playerDataArray[playerID].aiPopularityDecisionValue;
  if (iVar5 == 2) {
    iVar4 = DAT_GameState.playerDataArray[playerID].totalFood;
    DAT_GameState.playerDataArray[playerID].taxesSetting = 2;
    if (iVar4 < 1) {
      DAT_GameState.playerDataArray[playerID].rationsSetting = 0;
    }
    else if (iVar4 < 5) {
      DAT_GameState.playerDataArray[playerID].rationsSetting = 2;
    }
    else {
      DAT_GameState.playerDataArray[playerID].rationsSetting = (8 < iVar4) + 3;
    }
    goto LAB_004cb010;
  }
  if (iVar5 == 1) {
    iVar4 = DAT_GameState.playerDataArray[playerID].taxesSetting;
                    /* taxesMin */
    iVar5 = *(int *)((int)&DAT_AICState + iVar2 + 0x24);
    if (iVar5 < iVar4) {
      DAT_GameState.playerDataArray[playerID].taxesSetting = iVar4 + -1;
    }
    else {
      DAT_GameState.playerDataArray[playerID].taxesSetting = iVar5;
    }
    iVar4 = DAT_GameState.playerDataArray[playerID].totalFood;
    if (iVar4 < 1) {
      DAT_GameState.playerDataArray[playerID].rationsSetting = 0;
    }
    else {
      if (iVar4 < 0xb) goto LAB_004caff1;
      DAT_GameState.playerDataArray[playerID].rationsSetting = 3;
    }
  }
  else {
    if (iVar5 != 0) goto LAB_004cb010;
    iVar5 = DAT_GameState.playerDataArray[playerID].taxesSetting;
    iVar3 = *(int *)((int)&DAT_AICState + iVar2 + 0x28);
    if (iVar5 < iVar3) {
      iVar3 = DAT_GameState.playerDataArray[playerID].previousAvailablePeasants;
      if (iVar3 < 0xf) {
        iVar3 = (9 < iVar3) + 4;
      }
      else {
        iVar3 = 6;
      }
      if (iVar4 < DAT_GameState.playerDataArray[playerID].storedPopularityPercent) {
        if (iVar5 <= iVar3) goto LAB_004cafcd;
        iVar5 = iVar5 + -1;
      }
      else {
        iVar5 = iVar5 + 1;
      }
      DAT_GameState.playerDataArray[playerID].taxesSetting = iVar5;
    }
    else {
      DAT_GameState.playerDataArray[playerID].taxesSetting = iVar3;
    }
LAB_004cafcd:
    iVar4 = DAT_GameState.playerDataArray[playerID].totalFood;
    if (iVar4 < 0xb) {
      DAT_GameState.playerDataArray[playerID].rationsSetting = 0;
      goto LAB_004cb010;
    }
LAB_004caff1:
    DAT_GameState.playerDataArray[playerID].rationsSetting = 2;
  }
  iVar2 = *(int *)((int)&DAT_AICState + iVar2 + 0xa8);
  if ((iVar2 != 0) && (iVar2 <= iVar4)) {
    DAT_GameState.playerDataArray[playerID].rationsSetting = 4;
  }
LAB_004cb010:
  if (DAT_GameState.playerDataArray[playerID].taxesSetting < 0) {
    DAT_GameState.playerDataArray[playerID].taxesSetting = 0;
  }
  if (0xb < DAT_GameState.playerDataArray[playerID].taxesSetting) {
    DAT_GameState.playerDataArray[playerID].taxesSetting = 0xb;
  }
  if (DAT_GameState.playerDataArray[playerID].rationsSetting < 0) {
    DAT_GameState.playerDataArray[playerID].rationsSetting = 0;
  }
  if (4 < DAT_GameState.playerDataArray[playerID].rationsSetting) {
    DAT_GameState.playerDataArray[playerID].rationsSetting = 4;
  }
  return;
}


// Treffer: 20
