// ================= _HoldStrong::UI::MenuView_UnusedDemoBuyItScreen_Prepare @ 00426570 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::UI::MenuView_UnusedDemoBuyItScreen_Prepare(void)

{
  DAT_TextureRenderCoreObject.totalLoadedGfx = 0;
  Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"demo buy it screen.tgx");
  Rendering::PencilRenderCore::drawColorBox
            (&DAT_PencilRenderCore,0,0,DAT_WindowAndDirectDraw.resolutionX,
             DAT_WindowAndDirectDraw.resolutionY,COL_BLACK.shortValue);
  INT_00b95b34 = timeGetTime();
  INT_00b960e0 = 0;
  if (DAT_WindowAndDirectDraw.currentGameResolution == SRE_800x600) {
    INT_00b960e0 = 0x18;
  }
  Audio::MSS::SoundSystem::shutdownSoundSystem(&DAT_SoundSystemState);
  if (DAT_GameSynchronyState.openOnClose != FALSE) {
    DAT_WindowAndDirectDraw.postWindowCloseMessage = 1;
  }
  return;
}


// ================= _HoldStrong::UI::MenuView_UnusedDemoBuyItScreen_DoInitial @ 00426600 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::UI::MenuView_UnusedDemoBuyItScreen_DoInitial(void)

{
  Menu *pMVar1;
  int iVar2;
  bool bVar3;
  
  Rendering::PencilRenderCore::drawColorBox
            (&DAT_PencilRenderCore,0,0,DAT_WindowAndDirectDraw.resolutionX,
             DAT_WindowAndDirectDraw.resolutionY,COL_BLACK.shortValue);
  iVar2 = 0;
  INT_00b960e0 = 0;
  if (DAT_WindowAndDirectDraw.currentGameResolution == SRE_800x600) {
    iVar2 = 0x18;
    INT_00b960e0 = 0x18;
  }
  Rendering::TextureRenderCore::drawGfxOnFlaggedSurface
            (&DAT_TextureRenderCoreObject,0,
             (DAT_WindowAndDirectDraw.resolutionX -
             DAT_TextureRenderCoreObject.loadedGfxArray[0].width) / 2 + iVar2,
             (DAT_WindowAndDirectDraw.resolutionY -
             DAT_TextureRenderCoreObject.loadedGfxArray[0].height) / 2);
  DAT_MenuHandlerState.y = DAT_WindowAndDirectDraw.mainMenuBorderHeight;
  DAT_MenuHandlerState.x = DAT_WindowAndDirectDraw.mainMenuBorderWidth;
  pMVar1 = DAT_MenuHandlerState.currentMenu;
  bVar3 = DAT_WindowAndDirectDraw.currentGameResolution == SRE_800x600;
  (DAT_MenuHandlerState.currentMenu)->yPosition = DAT_WindowAndDirectDraw.mainMenuBorderHeight;
  if (bVar3) {
    DAT_MenuHandlerState.x = DAT_MenuHandlerState.x + 0x18;
  }
  pMVar1->xPosition = DAT_MenuHandlerState.x;
  return;
}


// ================= _HoldStrong::UI::MenuView_UnusedDemoBuyItScreen_DoEveryFrame @ 004266a0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::UI::MenuView_UnusedDemoBuyItScreen_DoEveryFrame(void)

{
  Rendering::TextureRenderCore::drawGfxOnFlaggedSurface
            (&DAT_TextureRenderCoreObject,0,
             (DAT_WindowAndDirectDraw.resolutionX -
             DAT_TextureRenderCoreObject.loadedGfxArray[0].width) / 2 + INT_00b960e0,
             (DAT_WindowAndDirectDraw.resolutionY -
             DAT_TextureRenderCoreObject.loadedGfxArray[0].height) / 2);
  return;
}


// ================= _HoldStrong::Game::GameStateStructures::checkRequiredResourcesForBuildingOrPlanToBuy @ 00457b80 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* buttonID = building Type
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Game::GameStateStructures::checkRequiredResourcesForBuildingOrPlanToBuy
          (GameStateStructures *this,MappersEnum commandBuildingType,int playerID,
          BOOLEnum playResourceLackMsgUnk)

{
  int iVar1;
  bool bVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  bVar2 = false;
  iVar3 = Map::Buildings::BuildingsState::convertCommandBuildingTypeToBuildingType
                    (commandBuildingType);
  iVar5 = DAT_BuildingsState.buildingCosts[iVar3].requiredIron_0x8;
  iVar6 = DAT_BuildingsState.buildingCosts[iVar3].requiredPitch_0xc;
  iVar7 = DAT_BuildingsState.buildingCosts[iVar3].requiredWood;
  iVar8 = DAT_BuildingsState.buildingCosts[iVar3].requiredStone_0x4;
  iVar1 = DAT_BuildingsState.buildingCosts[iVar3].requiredGold;
  if ((DAT_GameCore.solitaryAllBuildingsAreFree != FALSE) || (DAT_GameCore.gameMode_2 == GM_EDITOR))
  {
    return 1;
  }
  if (DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) {
    if (commandBuildingType == M_MAPPER_KEEP1) {
      return 1;
    }
    if (commandBuildingType == M_MAPPER_KEEP2) {
      return 1;
    }
    if (commandBuildingType == M_MAPPER_KEEP3) {
      return 1;
    }
  }
  else if ((DAT_GameSynchronyState.currentPlayerFullIDArray[playerID] == -1) &&
          (DAT_GameSynchronyState.currentAIArray[playerID] != 0)) {
    bVar2 = true;
  }
  uVar4 = Map::Buildings::BuildingsState::hasLessWoodThanTheCostOfAWoodcuttersHutAndNoWoodcutters
                    (&DAT_BuildingsState,playerID,iVar3);
  if (uVar4 != 0) {
    return 1;
  }
  if (DAT_GameState.playerDataArray[playerID].currentResources[6] < iVar5) {
    if (playResourceLackMsgUnk != FALSE) {
      Audio::MissingResourceState::playResourceLackSFX(&DAT_MissingResourceState,1,RLSFX_IRON);
    }
    if (!bVar2) {
      return 0;
    }
    iVar5 = iVar5 - DAT_GameState.playerDataArray[playerID].currentResources[6];
    if (iVar5 <= DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[6]) {
      return 0;
    }
    DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[6] = iVar5;
    return 0;
  }
  if (DAT_GameState.playerDataArray[playerID].currentResources[7] < iVar6) {
    if ((iVar3 == 0x44) && (DAT_GameState.playerDataArray[playerID].pitchDitchCounterTo4 != 0)) {
      return 1;
    }
    if (playResourceLackMsgUnk != FALSE) {
      Audio::MissingResourceState::playResourceLackSFX(&DAT_MissingResourceState,1,RLSFX_PITCH);
    }
    if (!bVar2) {
      return 0;
    }
    iVar6 = iVar6 - DAT_GameState.playerDataArray[playerID].currentResources[7];
    if (iVar6 <= DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[7]) {
      return 0;
    }
    DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[7] = iVar6;
    return 0;
  }
  if (DAT_GameState.playerDataArray[playerID].currentResources[0xf] < iVar1) {
    if (playResourceLackMsgUnk == FALSE) {
      return 0;
    }
    Audio::MissingResourceState::playResourceLackSFX(&DAT_MissingResourceState,1,RLSFX_GOLD);
    return 0;
  }
  iVar5 = DAT_GameState.playerDataArray[playerID].currentResources[2];
  if (iVar5 < iVar7) {
    if (DAT_GameState.playerDataArray[playerID].currentResources[4] < iVar8) {
      if (playResourceLackMsgUnk != FALSE) {
        Audio::MissingResourceState::playResourceLackSFX
                  (&DAT_MissingResourceState,1,RLSFX_PARTIAL_STONEUnk);
      }
      if (!bVar2) {
        return 0;
      }
      iVar7 = iVar7 - DAT_GameState.playerDataArray[playerID].currentResources[2];
      if ((0 < iVar7) &&
         (DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[2] < iVar7)) {
        DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[2] = iVar7;
      }
      goto LAB_00457e46;
    }
    if (iVar5 < iVar7) {
      if (playResourceLackMsgUnk != FALSE) {
        Audio::MissingResourceState::playResourceLackSFX(&DAT_MissingResourceState,1,RLSFX_WOOD);
      }
      if (!bVar2) {
        return 0;
      }
      iVar7 = iVar7 - DAT_GameState.playerDataArray[playerID].currentResources[2];
      if (iVar7 < 1) {
        return 0;
      }
      if (iVar7 <= DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[2]) {
        return 0;
      }
      DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[2] = iVar7;
      return 0;
    }
  }
  if (iVar8 <= DAT_GameState.playerDataArray[playerID].currentResources[4]) {
    return 1;
  }
  if (playResourceLackMsgUnk != FALSE) {
    Audio::MissingResourceState::playResourceLackSFX(&DAT_MissingResourceState,1,RLSFX_STONE);
  }
  if (!bVar2) {
    return 0;
  }
LAB_00457e46:
  iVar8 = iVar8 - DAT_GameState.playerDataArray[playerID].currentResources[4];
  if ((0 < iVar8) && (DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[4] < iVar8)) {
    DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[4] = iVar8;
  }
  return 0;
}


// ================= _HoldStrong::Game::GameStateStructures::getBatchBuyPrice @ 00458890 =================

/* batch is 5
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Game::GameStateStructures::getBatchBuyPrice
          (GameStateStructures *this,undefined4 playerID,int resourceType)

{
  return DAT_GameState.mapAndTime.buyAndSalesPriceArray[resourceType].buyPrice;
}


// ================= _HoldStrong::Game::GameStateStructures::getBuyPrice @ 004588a0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Game::GameStateStructures::getBuyPrice
          (GameStateStructures *this,undefined4 playerID,int resourceType,int amount)

{
  return (DAT_GameState.mapAndTime.buyAndSalesPriceArray[resourceType].buyPrice / 5) * amount;
}


// ================= _HoldStrong::Game::GameStateStructures::getBuyPriceForOneUnit @ 004588d0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Game::GameStateStructures::getBuyPriceForOneUnit(GameStateStructures *this,int param_1)

{
  return DAT_GameState.mapAndTime.buyAndSalesPriceArray[param_1].buyPrice / 5;
}


// ================= _HoldStrong::UI::MenuItemRenderFunction_BuildingAndStatusMenu_SelectBuySellGoods @ 00465950 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::UI::MenuItemRenderFunction_BuildingAndStatusMenu_SelectBuySellGoods(int param_1,...)

{
  BOOLEnum BVar1;
  int imageID;
  eGM *extraout_ECX;
  int drawX;
  int drawY;
  
  DAT_TextureRenderCoreObject.drawBufferChoiceValue = RT_SCREEN_MENU;
  BVar1 = Game::GameStateStructures::isResourceTypeTradeable(&DAT_GameState,param_1);
  if (BVar1 == FALSE) {
    DAT_ButtonCurrentlyInteracting = BVar1;
    DAT_TextureRenderCoreObject.drawBufferChoiceValue = RT_MAP_GAME;
    return;
  }
  drawX = DAT_ButtonX;
  drawY = DAT_ButtonY;
  imageID = Rendering::ButtonGmData::getPictureNumberInGm(DAT_ButtonCurrentlyInteracting);
  Rendering::TextureRenderCore::renderGM
            (&DAT_TextureRenderCoreObject,*extraout_ECX,imageID,drawX,drawY);
  DAT_CurrentButtonPictureInGm =
       DAT_UIButtonDefinedData.DAT_ButtonGmDataArray[DAT_CurrentButtonGmDataIndex].pictureInGm_0x4;
  DAT_TextureRenderCoreObject.drawBufferChoiceValue = RT_MAP_GAME;
  return;
}


// ================= _HoldStrong::UI::MenuItemActionHandler_BuildingAndStatusMenu_SelectBuySellGoods @ 004659e0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::UI::MenuItemActionHandler_BuildingAndStatusMenu_SelectBuySellGoods(int param_1,...)

{
  BOOLEnum BVar1;
  
  BVar1 = Game::GameStateStructures::isResourceTypeTradeable(&DAT_GameState,param_1);
  if (BVar1 != FALSE) {
    DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
    marketSelectedResourceType = param_1;
    DAT_GameCore.buildingandstatusmenuMenuTabToSwitchTo = 0x39;
    Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_BUILDING_AND_STATUS_MENU,0);
  }
  return;
}


// ================= _HoldStrong::UI::MenuItemRenderFunction_BuildingAndStatusMenu_BuySellMenuButtonsAndHands @ 00465a20 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::UI::MenuItemRenderFunction_BuildingAndStatusMenu_BuySellMenuButtonsAndHands
          (int param_1,...)

{
  ResourceTypeInt RVar1;
  char *pcVar2;
  int iVar3;
  int iVar4;
  DWORD DVar5;
  int iVar6;
  TextAlignment TVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  BOOLEnum BVar11;
  int iVar12;
  int iVar13;
  
  if ((param_1 == 2) || (param_1 == 3)) {
    DAT_ButtonUnknownZero = 1;
    BVar11 = Game::GameStateStructures::anyGoodsAreAllowedForSale(&DAT_GameState);
    if (BVar11 != FALSE) {
      DAT_ButtonUnknownZero = 0;
      if ((DAT_ButtonCurrentlyInteracting != FALSE) && (param_1 == 2)) {
        DAT_ButtonX = DAT_ButtonX + -4;
      }
      MenuItemRenderFunction_General_RenderCurrentButtonWithPossibleAlphaTexOnScreenMenuSurface();
      return;
    }
  }
  else {
    MenuItemRenderFunction_General_RenderCurrentButtonWithPossibleAlphaTexOnScreenMenuSurface();
    iVar4 = param_1 + 5;
    if (DAT_ButtonCurrentlyInteracting == FALSE) {
      iVar12 = 0x11;
      pcVar2 = Text::TextManager::getTextStringInGroupAtOffset
                         (&DAT_TextManagerObject,TEXT_IN_TRADEPOST,iVar4);
      iVar12 = Text::TextManager::computeTextWidth(&DAT_TextManagerObject,pcVar2,iVar12);
      iVar13 = 0;
      BVar11 = FALSE;
      iVar10 = 0x11;
      uVar9 = 0;
      uVar8 = 0xffffff;
      TVar7 = TTA_LEFT;
      iVar6 = DAT_ButtonY + 0xb;
      iVar3 = (DAT_ButtonW - (iVar12 + 0x35)) / 2 + DAT_ButtonX;
      pcVar2 = Text::TextManager::getTextStringInGroupAtOffset
                         (&DAT_TextManagerObject,TEXT_IN_TRADEPOST,iVar4);
      Text::TextManager::renderInGameTextWithShadow
                (&DAT_TextManagerObject,pcVar2,iVar3,iVar6,TVar7,uVar8,uVar9,iVar10,BVar11,iVar13);
      RVar1 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
              marketSelectedResourceType;
      if (param_1 == 0) {
        iVar4 = Game::GameStateStructures::getBatchBuyPrice
                          (&DAT_GameState,DAT_GameSynchronyState.currentPlayerSlotID,RVar1);
      }
      else {
        iVar4 = Game::GameStateStructures::getSalesPrice
                          (&DAT_GameState,DAT_GameSynchronyState.currentPlayerSlotID,RVar1);
      }
      Text::TextManager::renderNumberToScreen2
                (&DAT_TextManagerObject,iVar4,
                 (DAT_ButtonW - (iVar12 + 0x35)) / 2 + 0x14 + DAT_ButtonX,DAT_ButtonY + 10,TTA_LEFT,
                 0,0x11,TRUE,0);
      return;
    }
    iVar12 = 0x11;
    pcVar2 = Text::TextManager::getTextStringInGroupAtOffset
                       (&DAT_TextManagerObject,TEXT_IN_TRADEPOST,iVar4);
    iVar12 = Text::TextManager::computeTextWidth(&DAT_TextManagerObject,pcVar2,iVar12);
    iVar13 = 0;
    BVar11 = FALSE;
    iVar10 = 0x11;
    uVar9 = 0;
    uVar8 = 0xffffff;
    TVar7 = TTA_LEFT;
    iVar6 = DAT_ButtonY + 0xb;
    iVar3 = (DAT_ButtonW - (iVar12 + 0x35)) / 2 + DAT_ButtonX;
    pcVar2 = Text::TextManager::getTextStringInGroupAtOffset
                       (&DAT_TextManagerObject,TEXT_IN_TRADEPOST,iVar4);
    Text::TextManager::renderInGameTextWithShadow
              (&DAT_TextManagerObject,pcVar2,iVar3,iVar6,TVar7,uVar8,uVar9,iVar10,BVar11,iVar13);
    RVar1 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
            marketSelectedResourceType;
    if (param_1 == 0) {
      iVar3 = Game::GameStateStructures::getBatchBuyPrice
                        (&DAT_GameState,DAT_GameSynchronyState.currentPlayerSlotID,RVar1);
    }
    else {
      iVar3 = Game::GameStateStructures::getSalesPrice
                        (&DAT_GameState,DAT_GameSynchronyState.currentPlayerSlotID,RVar1);
    }
    Text::TextManager::renderNumberToScreen2
              (&DAT_TextManagerObject,iVar3,(DAT_ButtonW - (iVar12 + 0x35)) / 2 + 0x14 + DAT_ButtonX
               ,DAT_ButtonY + 10,TTA_LEFT,0,0x11,TRUE,0);
    if (param_1 == 1) {
      iVar12 = Game::GameStateStructures::getSellResourceAmount
                         (DAT_GameSynchronyState.currentPlayerSlotID,
                          DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                          marketSelectedResourceType);
    }
    else {
      iVar12 = 5;
    }
    iVar6 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
            storageMarketFailState;
    if (iVar6 == 0) {
      Text::TextManager::renderText2
                (&DAT_TextManagerObject,TEXT_IN_TRADEPOST,iVar4,DAT_MenuHandlerState.x + 0xdc,
                 DAT_MenuHandlerState.y + 0x243,TTA_LEFT,0,0x12,FALSE);
      Text::TextManager::renderNumberToScreen2
                (&DAT_TextManagerObject,iVar12,DAT_MenuHandlerState.x + 0xde,
                 DAT_MenuHandlerState.y + 0x243,TTA_LEFT,0,0x12,TRUE,0);
      Text::TextManager::renderText2
                (&DAT_TextManagerObject,TEXT_GOODS,
                 DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                 marketSelectedResourceType,DAT_MenuHandlerState.x + 0xe0,
                 DAT_MenuHandlerState.y + 0x243,TTA_LEFT,0,0x12,TRUE);
      Text::TextManager::renderNumberToScreen2
                (&DAT_TextManagerObject,iVar3,DAT_MenuHandlerState.x + 0xf0,
                 DAT_MenuHandlerState.y + 0x243,TTA_LEFT,0,0x12,TRUE,0);
                    /* added by script: "gold" */
      Text::TextManager::renderText2
                (&DAT_TextManagerObject,TEXT_IN_TRADEPOST,0xc,DAT_MenuHandlerState.x + 0xf4,
                 DAT_MenuHandlerState.y + 0x243,TTA_LEFT,0,0x12,TRUE);
      return;
    }
    Text::TextManager::renderText2
              (&DAT_TextManagerObject,TEXT_IN_TRADEPOST,iVar6 + 8,DAT_MenuHandlerState.x + 0xdc,
               DAT_MenuHandlerState.y + 0x243,TTA_LEFT,0,0x12,FALSE);
    DVar5 = timeGetTime();
    if (1000 < (int)(DVar5 - DAT_GameState.playerDataArray
                             [DAT_GameSynchronyState.currentPlayerSlotID].timeStorageMarketFailState
                    )) {
                    /* Resets the market fail state after 1 second */
      DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
      storageMarketFailState = 0;
    }
  }
  return;
}


// ================= _HoldStrong::Global::ProcessBuyOrSell @ 00465e60 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::Global::ProcessBuyOrSell(int playerID,int buyOrSell,ResourceType resourceType)

{
  int *piVar1;
  int iVar2;
  BOOLEnum BVar3;
  int iVar4;
  
  if (buyOrSell == 0) {
                    /* buying? */
    iVar2 = Game::GameStateStructures::getBatchBuyPrice(&DAT_GameState,playerID,resourceType);
    if ((iVar2 <= DAT_GameState.playerDataArray[playerID].currentResources[0xf]) &&
       (BVar3 = Map::Buildings::BuildingsState::processResourceGain
                          (&DAT_BuildingsState,playerID,resourceType,5), BVar3 != FALSE)) {
      piVar1 = DAT_GameState.playerDataArray[playerID].currentResources + 0xf;
      *piVar1 = *piVar1 - iVar2;
      piVar1 = &DAT_GameState.playerDataArray[playerID].marketGold;
      *piVar1 = *piVar1 - iVar2;
    }
  }
  else if ((buyOrSell == 1) &&
          (-1 < DAT_GameState.playerDataArray[playerID].currentResources[resourceType])) {
    iVar2 = Game::GameStateStructures::getSellResourceAmount(playerID,resourceType);
                    /* selling? */
    iVar4 = Game::GameStateStructures::getSalesPrice(&DAT_GameState,playerID,resourceType);
    piVar1 = DAT_GameSynchronyState.finalResults.finalGold + playerID;
    *piVar1 = *piVar1 + iVar4;
    piVar1 = DAT_GameState.playerDataArray[playerID].currentResources + 0xf;
    *piVar1 = *piVar1 + iVar4;
    piVar1 = &DAT_GameState.playerDataArray[playerID].marketGold;
    *piVar1 = *piVar1 + iVar4;
    Map::Buildings::BuildingsState::processResourceLoss
              (&DAT_BuildingsState,playerID,resourceType,iVar2,0);
    return;
  }
  return;
}


// ================= _HoldStrong::Global::TryAcquireAmmunitionOrPlanToBuyStone @ 00465f20 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl _HoldStrong::Global::TryAcquireAmmunitionOrPlanToBuyStone(int param_1,int param_2)

{
  short *psVar1;
  
  if (9 < DAT_GameState.playerDataArray[param_1].currentResources[4]) {
    Map::Buildings::BuildingsState::processResourceLoss(&DAT_BuildingsState,param_1,RT_STONE,10,0);
    psVar1 = &DAT_UnitsState.units[param_2].stoneAmmunition;
    *psVar1 = *psVar1 + 0x14;
    return;
  }
  if (((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
      (DAT_GameSynchronyState.currentPlayerFullIDArray[param_1] == -1)) &&
     (DAT_GameSynchronyState.currentAIArray[param_1] != 0)) {
    DAT_GameState.playerDataArray[param_1].resourcesToAcquireArray[4] = 10;
  }
  return;
}


// ================= _HoldStrong::UI::MenuItemActionHandler_BuildingAndStatusMenu_BuySellMenuButtonsAndHands @ 00467040 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::UI::MenuItemActionHandler_BuildingAndStatusMenu_BuySellMenuButtonsAndHands
          (int param_1,...)

{
  ResourceType resource;
  int iVar1;
  
  if (param_1 == 2) {
    iVar1 = Game::GameStateStructures::getPreviousGoodsFilteringUnallowed
                      (&DAT_GameState,
                       DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                       marketSelectedResourceType);
    if (iVar1 == 8) {
      iVar1 = 7;
    }
    MenuItemActionHandler_BuildingAndStatusMenu_SelectBuySellGoods(iVar1);
    return;
  }
  if (param_1 == 3) {
    iVar1 = Game::GameStateStructures::getNextGoodFilteringUnallowed
                      (&DAT_GameState,
                       DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                       marketSelectedResourceType);
    if (iVar1 == 8) {
      iVar1 = 7;
    }
    MenuItemActionHandler_BuildingAndStatusMenu_SelectBuySellGoods(iVar1);
    return;
  }
  BOOL_CurrentMenuClickState = FALSE;
  if (param_1 == 0) {
                    /* Buying */
    iVar1 = Game::GameStateStructures::getBatchBuyPrice
                      (&DAT_GameState,DAT_GameSynchronyState.currentPlayerSlotID,
                       DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                       marketSelectedResourceType);
    if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].currentResources
        [0xf] < iVar1) {
      Global::SetStorageMarketFailState
                (1,DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                   marketSelectedResourceType);
                    /* "Not enough gold" */
      Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"space_warning8.wav");
      return;
    }
    iVar1 = Map::Buildings::BuildingsState::getResourceSpace
                      (&DAT_BuildingsState,DAT_GameSynchronyState.currentPlayerSlotID,
                       (int *)DAT_GameState.playerDataArray
                              [DAT_GameSynchronyState.currentPlayerSlotID].
                              marketSelectedResourceType);
    if (iVar1 == -1) {
      Global::SetStorageMarketFailState
                (3,DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                   marketSelectedResourceType);
      if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
          storageMarketFailState == 6) {
                    /* "No stockpile built" */
        Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"space_warning2.wav");
      }
      if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
          storageMarketFailState == 5) {
                    /* "No Granary built" */
        Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"space_warning1.wav");
      }
      if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
          storageMarketFailState != 7) {
        return;
      }
                    /* "No Armory built" */
      Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"space_warning3.wav");
      return;
    }
    if (iVar1 < 5) {
      Global::SetStorageMarketFailState
                (4,DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                   marketSelectedResourceType);
      if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
          storageMarketFailState == 9) {
                    /* "No space in the stockpile" */
        Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"space_warning5.wav");
      }
      if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
          storageMarketFailState == 8) {
                    /* "No space in the granary" */
        Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"space_warning4.wav");
      }
      if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
          storageMarketFailState != 10) {
        return;
      }
                    /* "No space in the armory" */
      Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"space_warning6.wav");
      return;
    }
  }
  else {
    iVar1 = DAT_GameSynchronyState.currentPlayerSlotID;
                    /* Selling */
    if (param_1 != 1) goto LAB_004672c0;
    resource = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
               marketSelectedResourceType;
    if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].currentResources
        [resource] < 1) {
      Global::SetStorageMarketFailState(2,resource);
                    /* "Not enough goods" */
      Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"space_warning7.wav");
      return;
    }
  }
  Audio::SFX::SFXState::setUpSFXToPlayUnk(&DAT_SFXState,SEID_DRAWBRIDGE_CONTROL);
  iVar1 = DAT_GameSynchronyState.currentPlayerSlotID;
  DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].storageMarketFailState =
       0;
LAB_004672c0:
  DAT_GameSynchronyState.DAT_GameCommandParam1 =
       DAT_GameState.playerDataArray[iVar1].marketSelectedResourceType;
  DAT_GameSynchronyState.DAT_GameCommandParam0 = param_1;
  Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_BUY_OR_SELL);
  return;
}


// ================= _HoldStrong::Commands::ClickBuyOrSell @ 00482620 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Commands::ClickBuyOrSell(void)

{
  DAT_GameSynchronyState.DAT_CommandSize = 2;
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_SCHEDULE_AND_SEND) {
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam1,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    return;
  }
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_EXECUTE) {
    DAT_GameSynchronyState.DAT_GameCommandParam0 = DAT_GameSynchronyState.DAT_CommandActionPlan;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    DAT_GameSynchronyState.DAT_GameCommandParam1 = 0;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam1,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    Global::ProcessBuyOrSell
              (DAT_GameSynchronyState.protocolInvokerPlayerID,
               DAT_GameSynchronyState.DAT_GameCommandParam0,
               DAT_GameSynchronyState.DAT_GameCommandParam1);
  }
  return;
}


// ================= _HoldStrong::AI::AICState::setFoodBuyPlan @ 004cb060 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::AI::AICState::setFoodBuyPlan(AICState *this,int playerID)

{
  AITypeInt AVar1;
  int iVar2;
  int iVar3;
  
  AVar1 = DAT_GameState.playerDataArray[playerID].aiType;
  if (AVar1 != AIT_NULL) {
    iVar3 = (AVar1 + ~AIT_NULL) * 0x2a4;
    iVar2 = *(int *)((int)&DAT_AICState + iVar3 + 0x84);
    if ((-1 < iVar2) && (DAT_GameState.playerDataArray[playerID].currentResources[0xd] < iVar2)) {
      DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[0xd] =
           *(int *)((int)&DAT_AICState + iVar3 + 0x98);
    }
    iVar2 = *(int *)((int)&DAT_AICState + iVar3 + 0x88);
    if ((0 < iVar2) && (DAT_GameState.playerDataArray[playerID].currentResources[0xb] < iVar2)) {
      DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[0xb] =
           *(int *)((int)&DAT_AICState + iVar3 + 0x98);
    }
    iVar2 = *(int *)((int)&DAT_AICState + iVar3 + 0x8c);
    if ((0 < iVar2) && (DAT_GameState.playerDataArray[playerID].currentResources[10] < iVar2)) {
      DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[10] =
           *(int *)((int)&DAT_AICState + iVar3 + 0x98);
    }
    iVar2 = *(int *)((int)&DAT_AICState + iVar3 + 0x90);
    if ((0 < iVar2) && (DAT_GameState.playerDataArray[playerID].currentResources[9] < iVar2)) {
      DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[9] =
           *(int *)((int)&DAT_AICState + iVar3 + 0x98);
    }
    iVar2 = *(int *)((int)&DAT_AICState + iVar3 + 0x94);
    if ((0 < iVar2) && (DAT_GameState.playerDataArray[playerID].currentResources[3] < iVar2)) {
      DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[3] =
           *(int *)((int)&DAT_AICState + iVar3 + 0x98);
    }
  }
  return;
}


// ================= _HoldStrong::AI::AICState::planToBuyWhenLowOnResourceAndSnoozeBuildings @ 004cba50 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::AI::AICState::planToBuyWhenLowOnResourceAndSnoozeBuildings(AICState *this,int playerID)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  bool bVar9;
  bool bVar10;
  bool bVar11;
  bool bVar12;
  int iVar13;
  int iVar14;
  
  iVar14 = playerID * 0x39f4;
  if (DAT_GameState.playerDataArray[playerID].aiType != AIT_NULL) {
    bVar11 = true;
    bVar12 = true;
    bVar10 = true;
    iVar13 = Map::Buildings::BuildingsState::playerHasBurningBuilding(&DAT_BuildingsState,playerID);
    iVar2 = DAT_GameState.playerDataArray[playerID].currentResources[2];
    if (iVar2 < 1) {
      piVar1 = &DAT_GameState.playerDataArray[playerID].noWoodTracker;
      *piVar1 = *piVar1 + 1;
    }
    else {
      DAT_GameState.playerDataArray[playerID].noWoodTracker = 0;
    }
    if (DAT_GameState.playerDataArray[playerID].currentResources[6] < 1) {
      piVar1 = &DAT_GameState.playerDataArray[playerID].noIronTracker;
      *piVar1 = *piVar1 + 1;
    }
    else {
      DAT_GameState.playerDataArray[playerID].noIronTracker = 0;
    }
    if (DAT_GameState.playerDataArray[playerID].currentResources[0x10] < 1) {
      piVar1 = &DAT_GameState.playerDataArray[playerID].noFlourTracker;
      *piVar1 = *piVar1 + 1;
    }
    else {
      DAT_GameState.playerDataArray[playerID].noFlourTracker = 0;
    }
    if (DAT_GameState.playerDataArray[playerID].currentResources[3] < 1) {
      piVar1 = &DAT_GameState.playerDataArray[playerID].noHopsTracker;
      *piVar1 = *piVar1 + 1;
    }
    else {
      DAT_GameState.playerDataArray[playerID].noHopsTracker = 0;
    }
    if (DAT_GameState.playerDataArray[playerID].currentResources[0xe] < 1) {
      piVar1 = &DAT_GameState.playerDataArray[playerID].noBeerCounterUnk;
      *piVar1 = *piVar1 + 1;
    }
    else {
      DAT_GameState.playerDataArray[playerID].noBeerCounterUnk = 0;
    }
    piVar1 = &DAT_GameState.playerDataArray[playerID].someResourceCounter;
    *piVar1 = *piVar1 + 1;
    if (DAT_GameState.playerDataArray[playerID].countFletchersPoleturners < 1) {
      DAT_GameState.playerDataArray[playerID].noWoodTracker = 0;
    }
    if (DAT_GameState.playerDataArray[playerID].countArmorersAndBlacksmiths < 1) {
      DAT_GameState.playerDataArray[playerID].noIronTracker = 0;
    }
    if (DAT_GameState.playerDataArray[playerID].countBakers < 1) {
      DAT_GameState.playerDataArray[playerID].noFlourTracker = 0;
    }
    if (DAT_GameState.playerDataArray[playerID].countBrewers < 1) {
      DAT_GameState.playerDataArray[playerID].noHopsTracker = 0;
    }
    iVar3 = DAT_GameState.playerDataArray[playerID].currentPopulation;
    if ((iVar3 < 10) &&
       ((DAT_GameState.playerDataArray[playerID].farmsWithoutWorkers != 0 ||
        (2 < DAT_GameState.playerDataArray[playerID].countWoodcutters)))) {
      bVar11 = false;
    }
    if ((((0x13 < iVar2) && (iVar3 < 10)) &&
        (DAT_GameState.playerDataArray[playerID].farmsWithoutWorkers != 0)) &&
       (DAT_GameState.playerDataArray[playerID].totalFood < 8)) {
      bVar12 = false;
    }
    if (((iVar13 == 0) &&
        (DAT_GameState.playerDataArray[playerID].countFarms <=
         DAT_GameState.playerDataArray[playerID].farmsWithoutWorkers)) &&
       (DAT_GameState.playerDataArray[playerID].currentResources[0xf] < 500)) {
      bVar10 = false;
    }
    iVar2 = DAT_GameState.playerDataArray[playerID].armory.id;
    iVar13 = DAT_GameState.playerDataArray[playerID].noWoodTracker;
    iVar3 = DAT_GameState.playerDataArray[playerID].noIronTracker;
    iVar4 = DAT_GameState.playerDataArray[playerID].someResourceCounter;
    iVar5 = DAT_GameState.playerDataArray[playerID].noFlourTracker;
    iVar6 = DAT_GameState.playerDataArray[playerID].noHopsTracker;
    iVar7 = DAT_GameState.playerDataArray[playerID].noBeerCounterUnk;
    iVar8 = DAT_GameState.playerDataArray[playerID].aiNervousActionsTracker;
    bVar9 = iVar8 < 1;
    if (!bVar9) {
      bVar11 = false;
      bVar12 = false;
    }
    if (bVar10) {
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x1b] = false;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x46] = false;
    }
    else {
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x1b] = true;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x46] = true;
    }
    if (bVar11) {
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x14] = false;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[4] = false;
    }
    else {
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x14] = true;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[4] = true;
    }
    *(bool *)(iVar14 + 0x115df8f) = !bVar12;
    *(bool *)(iVar14 + 0x115df91) = !bVar9;
    *(bool *)(iVar14 + 0x115df92) = !bVar9;
    *(bool *)(iVar14 + 0x115df98) = iVar8 < 1 && (0x24 < iVar13 || iVar2 == 0);
    *(bool *)(iVar14 + 0x115df9a) = iVar8 < 1 && (0x24 < iVar13 || iVar2 == 0);
    *(bool *)(iVar14 + 0x115df99) = bVar9 && (0x24 < iVar3 || iVar2 == 0);
    *(bool *)(iVar14 + 0x115df9b) = bVar9 && (0x24 < iVar3 || iVar2 == 0);
    *(bool *)(iVar14 + 0x115df9c) = bVar9 && (0x24 < iVar4 || iVar2 == 0);
    *(bool *)(iVar14 + 0x115df9d) = !bVar9 || 0x24 < iVar5;
    *(bool *)(iVar14 + 0x115df9e) = !bVar9 || 0x48 < iVar6;
    *(bool *)(iVar14 + 0x115dfa2) = !bVar9 || 0x48 < iVar7;
    if (bVar9) {
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x1e] = false;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x1f] = false;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x20] = false;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x21] = false;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[7] = false;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x22] = false;
    }
    else {
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x1e] = true;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x1f] = true;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x20] = true;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x21] = true;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[7] = true;
      DAT_GameState.playerDataArray[playerID].snoozedBuildings[0x22] = true;
    }
    if (DAT_GameState.playerDataArray[playerID].canStartSpending != 0) {
      if ((0x24 < DAT_GameState.playerDataArray[playerID].noWoodTracker) &&
         (DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[2] == 0)) {
        DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[2] = 5;
      }
      if ((0x24 < DAT_GameState.playerDataArray[playerID].noIronTracker) &&
         (DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[6] == 0)) {
        DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[6] = 2;
      }
      if ((0x24 < DAT_GameState.playerDataArray[playerID].noFlourTracker) &&
         (DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[0x10] == 0)) {
        DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[0x10] = 2;
      }
      if ((0x48 < DAT_GameState.playerDataArray[playerID].noHopsTracker) &&
         (DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[3] == 0)) {
        DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[3] = 2;
      }
    }
  }
  return;
}


// ================= _HoldStrong::AI::AICState::buyGoods @ 004cc000 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::AI::AICState::buyGoods
          (AICState *this,int playerID,ResourceType resourceType,int amount)

{
  int *piVar1;
  int iVar2;
  BOOLEnum BVar3;
  
  iVar2 = Game::GameStateStructures::getBuyPrice(&DAT_GameState,playerID,resourceType,amount);
  BVar3 = Map::Buildings::BuildingsState::processResourceGain
                    (&DAT_BuildingsState,playerID,resourceType,amount);
  if (BVar3 != FALSE) {
    piVar1 = DAT_GameState.playerDataArray[playerID].currentResources + 0xf;
    *piVar1 = *piVar1 - iVar2;
    piVar1 = &DAT_GameState.playerDataArray[playerID].marketGold;
    *piVar1 = *piVar1 - iVar2;
    Game::GameStateStructures::displayPlayerTradeVisualEffect
              (&DAT_GameState,playerID,0,amount,resourceType);
    return TRUE;
  }
  return FALSE;
}


// ================= _HoldStrong::AI::AICState::buyRequiredGoods @ 004d39b0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* Walks the AIC resource acquisition preference order (up to 25 entries in
   DAT_ResourceAcquisitionPreferenceOrder) and attempts to buy the first resource for which the
   player has a non-zero resourcesToAcquireArray entry and meets one of the spending conditions:
   popularity is below the AIC minimum threshold (only checked for the first 4 entries), the AI is
   nervous, or the canStartSpending flag is set. If the AI is nervous, entries 0-11 (non-weapon
   resources) are skipped entirely so it only buys weapons. A special override fires first inside
   the loop: if the building-destroy tracker is non-zero AND the player has fewer than 20 wood, the
   resource type is forced to RT_WOOD regardless of the preference order. Before calling buyGoods()
   the required gold is computed via getBuyPrice(); if the AI cannot afford the purchase it calls
   requestGoods() from a teammate at double the desired amount instead. On a successful purchase
   resourcesToAcquireArray for that resource is cleared and the function returns immediately,
   buying at most one resource type per call. */

void __thiscall _HoldStrong::AI::AICState::buyRequiredGoods(AICState *this,int param_1)

{
  AITypeInt AVar1;
  int amount;
  int playerID;
  int iVar2;
  BOOLEnum BVar3;
  ResourceTypeInt resourceType;
  
  playerID = param_1;
                    /* buying */
  AVar1 = DAT_GameState.playerDataArray[param_1].aiType;
  if (AVar1 == AIT_NULL) {
    return;
  }
                    /* reused! playerID now means a counter */
  param_1 = 0;
  do {
    resourceType = DAT_SkirmishDefinedData.ResourceAcquisitionPreferenceOrder[param_1];
                    /* If nervous, only buy from entry 12 onwards, which are weapons */
    if ((DAT_GameState.playerDataArray[playerID].aiNervousActionsTracker < 1) || (0xb < param_1)) {
      if ((DAT_GameState.playerDataArray[playerID].aiBuildingDestroyChoiceTracker != 0) &&
         (DAT_GameState.playerDataArray[playerID].currentResources[2] < 0x14)) {
                    /* if short on wood, buy wood! */
        resourceType = RT_WOOD;
      }
      amount = DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[resourceType];
      if ((amount != 0) &&
         ((((param_1 < 4 &&
            (DAT_GameState.playerDataArray[playerID].popularity <
             *(int *)((int)&DAT_AICState + (AVar1 + ~AIT_NULL) * 0x2a4 + 0x18))) ||
           (0 < DAT_GameState.playerDataArray[playerID].aiNervousActionsTracker)) ||
          (DAT_GameState.playerDataArray[playerID].canStartSpending != 0)))) {
        iVar2 = Game::GameStateStructures::getBuyPrice(&DAT_GameState,playerID,resourceType,amount);
        if (DAT_GameState.playerDataArray[playerID].currentResources[0xf] < iVar2) {
          requestGoods(&DAT_AICState,playerID,resourceType,amount * 2);
        }
        else {
          BVar3 = buyGoods(&DAT_AICState,playerID,resourceType,amount);
          if (BVar3 != FALSE) {
            DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[resourceType] = 0;
            return;
          }
        }
      }
    }
    param_1 = param_1 + 1;
  } while (param_1 < 0x19);
  return;
}


// ================= _HoldStrong::AI::AICState::aiBuyAndSellGoods @ 004d48f0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::AI::AICState::aiBuyAndSellGoods(AICState *this,int playerID)

{
  BOOLEnum *pBVar1;
  int iVar2;
  
  iVar2 = DAT_GameState.playerDataArray[playerID].marketplace.id;
  DAT_GameState.playerDataArray[playerID].hasMarketUnk = 0;
  if (iVar2 != 0) {
    DAT_GameState.playerDataArray[playerID].hasMarketUnk = 1;
  }
  if (DAT_GameState.playerDataArray[playerID].hasMarketUnk != 0) {
    pBVar1 = &DAT_GameState.playerDataArray[playerID].willBuy;
    *pBVar1 = *pBVar1 ^ TRUE;
    if (*pBVar1 == FALSE) {
      sellExcessGoods(&DAT_AICState,playerID);
      return;
    }
    buyRequiredGoods(&DAT_AICState,playerID);
    return;
  }
  return;
}


// ================= _HoldStrong::Global::Init::Constructor_MenuView_UnusedDemoBuyItScreen @ 0059a820 =================

void _HoldStrong::Global::Init::Constructor_MenuView_UnusedDemoBuyItScreen(void)

{
  UI::MenuView::Constructor_MenuView
            (&MenuView_UnusedDemoBuyItScreen,MVT_UNUSED_DEMO_BUY_IT_SCREEN,
             UI::MenuView_UnusedDemoBuyItScreen_Prepare,UI::MenuView_UnusedDemoBuyItScreen_DoInitial
             ,UI::MenuView_UnusedDemoBuyItScreen_DoEveryFrame);
  OS::_atexit(Meta::Destructor_MenuView_UnusedDemoBuyItScreen);
  return;
}


// ================= _HoldStrong::Global::Init::Constructor_Menu_UnusedDemoBuyItScreen @ 0059afa0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2026-05-02 18:15:17.059000 */

void _HoldStrong::Global::Init::Constructor_Menu_UnusedDemoBuyItScreen(void)

{
  UI::Menu::Constructor_Menu
            (&Menu_UnusedDemoBuyItScreen,DAT_RenderingDefinedData.MenuItems_UnusedDemoBuyItScreen);
  return;
}


// ================= _HoldStrong::Meta::Destructor_MenuView_UnusedDemoBuyItScreen @ 0059cf70 =================

void __cdecl _HoldStrong::Meta::Destructor_MenuView_UnusedDemoBuyItScreen(void)

{
  Global::DoNothing();
  return;
}


// Treffer: 22
