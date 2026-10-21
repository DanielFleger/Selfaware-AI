##### MissionFinishedTransition_Prepare @ 0x004e1b30

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "UnsortedBinkFlagInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::UI::MenuView_MissionFinishedTransition_Prepare(void)

{
  Menu *pMVar1;
  DWORD DVar2;
  int iVar3;
  int xPos;
  char cVar4;
  char *pcVar5;
  char local_104 [256];
  uint local_4;
  
  local_4 = MSVC_SecurityCookie ^ (uint)local_104;
  DVar2 = timeGetTime();
  DAT_GameCore.gameDuration = DVar2 - DAT_GameCore.timeSum_2;
  DAT_00ed279c = 0;
  DAT_FinalResultsOrderByColumn = 0;
  DAT_00eb9af8 = 0;
  DAT_GameCore.currentlyInGameUnk_0xa4 = FALSE;
  if (DAT_WindowAndDirectDraw.currentGameResolution == SRE_800x600) {
    DAT_GameCore.activeMenuTab.tabType = 0;
    DAT_00ec082c = 0;
  }
  else {
    DAT_GameCore.activeMenuTab.tabType = BASMTT_KEEP_OR_MPMENU_IPX;
    DAT_00ec082c = 2;
  }
  DAT_VideoBikQueue.storedMessages_0x924 = 0;
  DAT_00ed27b4 = 0;
  MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition1,MMT_NONE,FALSE);
  MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition2,MMT_NONE,FALSE);
  MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition3,MMT_NONE,FALSE);
  INT_00eb0e44._0_1_ = 0;
  Global::StoreTime();
  DAT_MenuHandlerState.y = DAT_WindowAndDirectDraw.mainMenuBorderHeight;
  DAT_MenuHandlerState.x = DAT_WindowAndDirectDraw.mainMenuBorderWidth;
  pMVar1 = DAT_MenuHandlerState.currentMenu;
  (DAT_MenuHandlerState.currentMenu)->xPosition = DAT_WindowAndDirectDraw.mainMenuBorderWidth;
  pMVar1->yPosition = DAT_MenuHandlerState.y;
  Rendering::PencilRenderCore::drawColorBox
            (&DAT_PencilRenderCore,0,0,DAT_WindowAndDirectDraw.resolutionX,
             DAT_WindowAndDirectDraw.resolutionY,COL_BLACK.shortValue);
  if (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_END_OF_GAME_SINGLE_PLAYER) {
LAB_004e1cdd:
    DAT_TextureRenderCoreObject.totalLoadedGfx = 0;
    Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,CHAR_ARRAY_00eb9ac8);
    if (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_END_OF_GAME_SINGLE_PLAYER)
    goto LAB_004e1da4;
  }
  else {
    if (DAT_GameCore.gameMode_2 == GM_CAMPAIGN_MISSION) {
      if (DAT_GameCore.missionNumber1to20 - 7U < 5) {
        iVar3 = DAT_MenuHandlerState.y + 0x3c;
        xPos = DAT_MenuHandlerState.x + 0x50;
        pcVar5 = "arabian_win.bik";
      }
      else {
LAB_004e1cbd:
        iVar3 = DAT_MenuHandlerState.y + 0x3c;
        xPos = DAT_MenuHandlerState.x + 0x50;
        pcVar5 = "crusader_win.bik";
      }
    }
    else {
      iVar3 = Synchrony::GameSynchronyState::getLordTypeForPlayer
                        (&DAT_GameSynchronyState,DAT_GameSynchronyState.currentPlayerSlotID);
      if (iVar3 != 1) goto LAB_004e1cbd;
      iVar3 = DAT_MenuHandlerState.y + 0x3c;
      xPos = DAT_MenuHandlerState.x + 0x50;
      pcVar5 = "arabian_win.bik";
    }
    _HoldStrong::Rendering::Bink::BinkControlClass::playBINK
              (&DAT_BinkControlState,0,pcVar5,0,0,xPos,iVar3,2);
    if (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_END_OF_GAME_SINGLE_PLAYER)
    goto LAB_004e1cdd;
  }
  cVar4 = DAT_GameState.mapAndTime.playerIsAlive[1] != 0;
  if (DAT_GameState.mapAndTime.playerIsAlive[2] != 0) {
    cVar4 = cVar4 + '\x01';
  }
  if (DAT_GameState.mapAndTime.playerIsAlive[3] != 0) {
    cVar4 = cVar4 + '\x01';
  }
  if (DAT_GameState.mapAndTime.playerIsAlive[4] != 0) {
    cVar4 = cVar4 + '\x01';
  }
  if (DAT_GameState.mapAndTime.playerIsAlive[5] != 0) {
    cVar4 = cVar4 + '\x01';
  }
  if (DAT_GameState.mapAndTime.playerIsAlive[6] != 0) {
    cVar4 = cVar4 + '\x01';
  }
  if (DAT_GameState.mapAndTime.playerIsAlive[7] != 0) {
    cVar4 = cVar4 + '\x01';
  }
  if (DAT_GameState.mapAndTime.playerIsAlive[8] != 0) {
    cVar4 = cVar4 + '\x01';
  }
  if ((DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_SINGLE_PLAYER) || (cVar4 != '\0')) {
    if ((int)SEC_RNG.currentNumber1 % 3 == 0) {
                    /* "We are victorious sire!" */
      pcVar5 = "general_victory2.wav";
    }
    else {
                    /* "Victory!" */
      pcVar5 = "general_victory1.wav";
    }
    Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,pcVar5);
  }
  Audio::MSS::SoundSystem::playWinMusicVariation(&DAT_SoundSystemState);
LAB_004e1da4:
  DAT_MenuTextInputState.DAT_SomeTextArrayIndex = 9;
  MenuTextInputState::clearAnyOtherModalDialogs(&DAT_MenuTextInputState);
  if (DAT_GameCore.gameMode_2 != GM_SKIRMISH_AND_MULTIPLAYER) {
    _DAT_00ec0828 = 0;
    Map::MapPropertiesState::computeMissionCompletionScore(&DAT_MapPropertiesState);
    IO::LowLevelMemory::putFileNameAndAppendFileExtension
              (&DAT_LowLevelMemory,(char *)&DAT_MapPropertiesState,local_104,"sco");
    IO::ResourceManager::resolveResourceFileName(&DAT_ResourceManager,FRT_SCORES,local_104);
    pcVar5 = IO::ResourceManager::getFileNameOfCurrentActiveResource(&DAT_ResourceManager);
    Global::WriteMissionToScoresFile(pcVar5,DAT_MapPropertiesState.field140_0x14554);
  }
  Global::LoadTGX_shc_back();
  HoldStrong_lib::__security_check_cookie(local_4 ^ (uint)local_104);
  return;
}


##### MissionFinishedTransition_DoEveryFrame @ 0x004dc500

/* WARNING: Enum "UnsortedBinkFlagInt": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::UI::MenuView_MissionFinishedTransition_DoEveryFrame(void)

{
  short sVar1;
  DWORD DVar2;
  int iVar3;
  dword dVar4;
  MenuViewType menuID;
  
  if (DAT_GameCore.gameMode_2 == GM_SKIRMISH_AND_MULTIPLAYER) {
    if (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_END_OF_GAME_SINGLE_PLAYER) {
      Rendering::TextureRenderCore::drawGfxOnFlaggedSurface
                (&DAT_TextureRenderCoreObject,0,
                 (DAT_WindowAndDirectDraw.resolutionX -
                 DAT_TextureRenderCoreObject.loadedGfxArray[0].width) / 2,
                 (DAT_WindowAndDirectDraw.resolutionY -
                 DAT_TextureRenderCoreObject.loadedGfxArray[0].height) / 2);
    }
    Rendering::RenderGreatestLordScreen();
  }
  else if (DAT_BinkControlState.binkObjPtrArray[0] == (HBINK)0x0) {
    DAT_MouseState.draggingStopped = TRUE;
  }
  if (((DAT_GameCore.gameMode_2 == GM_CAMPAIGN_MISSION) &&
      (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_END_OF_GAME_SINGLE_PLAYER)) &&
     (DAT_BinkControlState.unknown02_zero[0] != 0)) {
    if (DAT_00ed27b4 == 0) {
      DAT_00ed27b4 = timeGetTime();
      goto LAB_004dc5a5;
    }
    DVar2 = timeGetTime();
    if (DVar2 - DAT_00ed27b4 < 0x1389) goto LAB_004dc5a5;
  }
  else {
LAB_004dc5a5:
    if (((DAT_MouseState.draggingStopped == FALSE) ||
        (DAT_GameCore.gameMode_2 == GM_SKIRMISH_AND_MULTIPLAYER)) && (DAT_00ed279c == 0)) {
      return;
    }
  }
  DAT_SoundSystemState.streamFlagsUnkAndLoopCount_0x34[4] = 0;
  DAT_SoundSystemState.streamFlagsUnkAndLoopCount_0x34[3] = 0;
  Audio::MSS::SoundSystem::endSoundStream(&DAT_SoundSystemState,SND_STR_SPEECH_1);
  Audio::MSS::SoundSystem::endSoundStream(&DAT_SoundSystemState,SND_STR_SPEECH_2);
  _HoldStrong::Rendering::Bink::BinkControlClass::stopAllBinkPlayback(&DAT_BinkControlState);
  if (DAT_GameCore.gameMode_2 != GM_SKIRMISH_AND_MULTIPLAYER) {
    if (DAT_GameCore.gameMode_2 == GM_CAMPAIGN_MISSION) {
      DAT_GameCore.field25_0x64 = 0;
      if (DAT_GameCore.missionNumber1to20 <= (int)(DAT_GameCore.historicCampaignNumber * 5)) {
        Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_HISTORIC_MISSION_PICTURE,0);
        DAT_GameCore.skipStoreSKMasters = 0;
        return;
      }
      Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_HISTORIC_CAMPAIGN_OUTRO,0);
      DAT_GameCore.skipStoreSKMasters = 0;
      return;
    }
    if (DAT_GameCore.gameMode_2 == GM_ECONOMIC_CAMPAIGN_SH1) {
      DAT_GameCore.field25_0x64 = 0;
      if (DAT_GameCore.missionNumber1to20 < 0x26) {
        Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_SCENARIO_DESCRIPTION,0);
        DAT_GameCore.skipStoreSKMasters = 0;
        return;
      }
      Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_MAIN_MENU,0);
      DAT_GameCore.skipStoreSKMasters = 0;
      return;
    }
    if (DAT_GameCore.gameMode_2 == GM_BUILDERUnk) {
      if (DAT_MapPropertiesState.SEC_U3_MapType2_1 == MT_ECONOMIC) {
        MenuItemActionHandler_MainMenu_Main(3);
        DAT_GameCore.skipStoreSKMasters = 0;
        return;
      }
      MenuItemActionHandler_CustomScenarios_Main(4);
      DAT_GameCore.skipStoreSKMasters = 0;
      return;
    }
    menuID = MVT_MAIN_MENU;
    goto LAB_004dc9bd;
  }
  if (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER) {
    if (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_END_OF_GAME_SINGLE_PLAYER) {
      DAT_MenuTextInputState.DAT_MenuOptionsActionParameter = 7;
      MenuItemActionHandler_General_LaunchOrQuitMultiplayerGameUnk(0x16);
      if (DAT_GameSynchronyState.isHost == FALSE) {
        DAT_GameCore.skipStoreSKMasters = 0;
        return;
      }
      Game::Skirmish::SkirmishLobbySetupStructure::restoreSkirmishLobbySetup
                (&SEC_SkirmishLobbySetupStructure);
      Synchrony::GameSynchronyState::queueCommand
                (&DAT_GameSynchronyState,GCT_HOST_SHARE_LOBBY_STATE);
      DAT_GameCore.skipStoreSKMasters = 0;
      return;
    }
    DAT_GameSynchronyState.currentGameMode = GM_SKIRMISH_SINGLE_PLAYER;
    menuID = MVT_RANKING_GAMES;
    goto LAB_004dc9bd;
  }
  if (DAT_GameCore.isSkirmishTrail == FALSE) {
    if (DAT_GameCore.skipStoreSKMasters == 0) {
      Global::StoreGameIntoSKMasters(0);
    }
    MenuItemActionHandler_SelectCrusade_Main(2);
    Game::Skirmish::SkirmishLobbySetupStructure::restoreSkirmishLobbySetup
              (&SEC_SkirmishLobbySetupStructure);
  }
  if (DAT_GameCore.isSkirmishTrail != TRUE) {
    DAT_GameCore.skipStoreSKMasters = 0;
    return;
  }
  if (DAT_GameCore.skipStoreSKMasters == 0) {
    if (DAT_GameCore.currentTrailType == TT_EXTREME) {
      iVar3 = DAT_GameCore.extremeTrailProgress + 0x51;
    }
    else if (DAT_GameCore.currentTrailType == TT_WARCHEST) {
      iVar3 = DAT_GameCore.warchestTrailProgress + 0x33;
    }
    else {
      iVar3 = DAT_GameCore.skirmishTrailProgress + 1;
    }
    Global::StoreGameIntoSKMasters(iVar3);
  }
  dVar4 = DAT_GameCore.extremeTrailProgress;
  if ((DAT_GameCore.currentTrailType != TT_EXTREME) &&
     (dVar4 = DAT_GameCore.skirmishTrailProgress, DAT_GameCore.currentTrailType == TT_WARCHEST)) {
    dVar4 = DAT_GameCore.warchestTrailProgress;
  }
  if (DAT_GameState.mapAndTime.playerIsAlive[DAT_GameSynchronyState.currentPlayerSlotID] == 0) {
LAB_004dc763:
    if (DAT_GameCore.currentTrailType == TT_EXTREME) {
LAB_004dc768:
      sVar1 = DAT_GameState.mapAndTime.playerIsAlive[DAT_GameSynchronyState.currentPlayerSlotID];
      if (sVar1 == 0) {
LAB_004dc7be:
        MenuItemActionHandler_SelectCrusade_Main(4);
        DAT_GameCore.skipStoreSKMasters = 0;
        return;
      }
      if (DAT_GameCore.extremeTrailProgress < DAT_GameCore.furthestExtremeTrailMission) {
        if (sVar1 == 0) goto LAB_004dc7be;
      }
      else {
        DAT_GameCore.furthestExtremeTrailMission = DAT_GameCore.extremeTrailProgress + 1;
      }
      if (DAT_GameCore.extremeTrailProgress < 0x13) {
        DAT_GameCore.extremeTrailProgress = DAT_GameCore.extremeTrailProgress + 1;
      }
      if (((sVar1 == 0) || (DAT_GameCore.extremeTrailProgress != 0x13)) || (dVar4 != 0x13))
      goto LAB_004dc7be;
    }
    else {
      if (DAT_GameCore.currentTrailType == TT_WARCHEST) goto LAB_004dc7d9;
      sVar1 = DAT_GameState.mapAndTime.playerIsAlive[DAT_GameSynchronyState.currentPlayerSlotID];
      if (sVar1 == 0) {
LAB_004dc88c:
        MenuItemActionHandler_SelectCrusade_Main(1);
        DAT_GameCore.skipStoreSKMasters = 0;
        return;
      }
      if ((int)DAT_GameCore.skirmishTrailProgress < DAT_GameCore.furthestSkirmishTrailMission) {
        if (sVar1 == 0) goto LAB_004dc88c;
      }
      else {
        DAT_GameCore.furthestSkirmishTrailMission = DAT_GameCore.skirmishTrailProgress + 1;
      }
      if ((int)DAT_GameCore.skirmishTrailProgress < 0x31) {
        DAT_GameCore.skirmishTrailProgress = DAT_GameCore.skirmishTrailProgress + 1;
      }
      if (((sVar1 == 0) || (DAT_GameCore.skirmishTrailProgress != 0x31)) || (dVar4 != 0x31))
      goto LAB_004dc88c;
    }
  }
  else {
    iVar3 = DAT_GameState.mapAndTime.month + DAT_GameState.mapAndTime.year * 0xc;
    if (DAT_GameCore.currentTrailType == TT_EXTREME) {
      if (((int)(iVar3 - DAT_GameCore.extremeTrailStartDateMonths) <
           DAT_GameCore.extremeTrailMonthsTakenOrChicken[DAT_GameCore.extremeTrailProgress]) ||
         (DAT_GameCore.extremeTrailMonthsTakenOrChicken[DAT_GameCore.extremeTrailProgress] < 0)) {
        DAT_GameCore.extremeTrailMonthsTakenOrChicken[DAT_GameCore.extremeTrailProgress] =
             iVar3 - DAT_GameCore.extremeTrailStartDateMonths;
        iVar3 = 3;
        goto LAB_004dc741;
      }
      goto LAB_004dc768;
    }
    if (DAT_GameCore.currentTrailType != TT_WARCHEST) {
      if ((DAT_GameCore.skirmishTrailMonthsTakenOrChicken[DAT_GameCore.skirmishTrailProgress] <=
           (int)(iVar3 - DAT_GameCore.skirmishTrailStartDateMonths)) &&
         (-1 < DAT_GameCore.skirmishTrailMonthsTakenOrChicken[DAT_GameCore.skirmishTrailProgress]))
      goto LAB_004dc763;
      DAT_GameCore.skirmishTrailMonthsTakenOrChicken[DAT_GameCore.skirmishTrailProgress] =
           iVar3 - DAT_GameCore.skirmishTrailStartDateMonths;
      iVar3 = 1;
LAB_004dc741:
      Game::GameCore::setStartDateUnk(&DAT_GameCore,iVar3);
      goto LAB_004dc763;
    }
    if (((int)(iVar3 - DAT_GameCore.warchestTrailStartDateMonths) <
         DAT_GameCore.warchestTrailMonthsTakenOrChicken[DAT_GameCore.warchestTrailProgress]) ||
       (DAT_GameCore.warchestTrailMonthsTakenOrChicken[DAT_GameCore.warchestTrailProgress] < 0)) {
      DAT_GameCore.warchestTrailMonthsTakenOrChicken[DAT_GameCore.warchestTrailProgress] =
           iVar3 - DAT_GameCore.warchestTrailStartDateMonths;
      iVar3 = 2;
      goto LAB_004dc741;
    }
LAB_004dc7d9:
    sVar1 = DAT_GameState.mapAndTime.playerIsAlive[DAT_GameSynchronyState.currentPlayerSlotID];
    if (sVar1 == 0) {
LAB_004dc826:
      MenuItemActionHandler_SelectCrusade_Main(3);
      DAT_GameCore.skipStoreSKMasters = 0;
      return;
    }
    if ((int)DAT_GameCore.warchestTrailProgress < DAT_GameCore.furthestWarchestTrailMission) {
      if (sVar1 == 0) goto LAB_004dc826;
    }
    else {
      DAT_GameCore.furthestWarchestTrailMission = DAT_GameCore.warchestTrailProgress + 1;
    }
    if ((int)DAT_GameCore.warchestTrailProgress < 0x1d) {
      DAT_GameCore.warchestTrailProgress = DAT_GameCore.warchestTrailProgress + 1;
    }
    if (((sVar1 == 0) || (DAT_GameCore.warchestTrailProgress != 0x1d)) || (dVar4 != 0x1d))
    goto LAB_004dc826;
  }
  menuID = MVT_CRUSADE_ENDSCREEN;
LAB_004dc9bd:
  Game::GameCore::switchToMenuView(&DAT_GameCore,menuID,0);
  DAT_GameCore.skipStoreSKMasters = 0;
  return;
}


##### GameLost_Prepare @ 0x004d55d0

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "UnsortedBinkFlagInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::UI::MenuView_GameLost_Prepare(void)

{
  Menu *pMVar1;
  DWORD DVar2;
  int iVar3;
  int xPos;
  char *binkFileName;
  
  DVar2 = timeGetTime();
  DAT_GameCore.gameDuration = DVar2 - DAT_GameCore.timeSum_2;
  DAT_00ed279c = 0;
  DAT_FinalResultsOrderByColumn = 0;
  DAT_00eb9af8 = 0;
  INT_00eb0e44._0_1_ = 0;
  DAT_VideoBikQueue.storedMessages_0x924 = 0;
  MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition1,MMT_NONE,FALSE);
  MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition2,MMT_NONE,FALSE);
  MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition3,MMT_NONE,FALSE);
  if (DAT_WindowAndDirectDraw.currentGameResolution == SRE_800x600) {
    DAT_GameCore.activeMenuTab.tabType = 0;
    DAT_00ec082c = 0;
  }
  else {
    DAT_GameCore.activeMenuTab.tabType = BASMTT_KEEP_OR_MPMENU_IPX;
    DAT_00ec082c = 2;
  }
  Global::StoreTime();
  DAT_00ed27b4 = 0;
  Audio::MSS::SoundSystem::setupLossMusic(&DAT_SoundSystemState);
  DAT_MenuHandlerState.y = DAT_WindowAndDirectDraw.mainMenuBorderHeight;
  DAT_MenuHandlerState.x = DAT_WindowAndDirectDraw.mainMenuBorderWidth;
  pMVar1 = DAT_MenuHandlerState.currentMenu;
  (DAT_MenuHandlerState.currentMenu)->xPosition = DAT_WindowAndDirectDraw.mainMenuBorderWidth;
  pMVar1->yPosition = DAT_MenuHandlerState.y;
  Rendering::PencilRenderCore::drawColorBox
            (&DAT_PencilRenderCore,0,0,DAT_WindowAndDirectDraw.resolutionX,
             DAT_WindowAndDirectDraw.resolutionY,COL_BLACK.shortValue);
  if (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_END_OF_GAME_SINGLE_PLAYER)
  goto LAB_004d575f;
  if (DAT_GameCore.gameMode_2 == GM_CAMPAIGN_MISSION) {
    if (DAT_GameCore.missionNumber1to20 - 6U < 5) {
      iVar3 = DAT_MenuHandlerState.y + 0x3c;
      xPos = DAT_MenuHandlerState.x + 0x50;
      binkFileName = "arabian_lose.bik";
    }
    else {
LAB_004d574d:
      iVar3 = DAT_MenuHandlerState.y + 0x3c;
      xPos = DAT_MenuHandlerState.x + 0x50;
      binkFileName = "crusader_lose.bik";
    }
  }
  else {
    iVar3 = Synchrony::GameSynchronyState::getLordTypeForPlayer
                      (&DAT_GameSynchronyState,DAT_GameSynchronyState.currentPlayerSlotID);
    if (iVar3 != 1) goto LAB_004d574d;
    iVar3 = DAT_MenuHandlerState.y + 0x3c;
    xPos = DAT_MenuHandlerState.x + 0x50;
    binkFileName = "arabian_lose.bik";
  }
  _HoldStrong::Rendering::Bink::BinkControlClass::playBINK
            (&DAT_BinkControlState,0,binkFileName,0,0,xPos,iVar3,2);
LAB_004d575f:
  Global::LoadTGX_shc_back();
  DAT_MenuTextInputState.DAT_SomeTextArrayIndex = 9;
  MenuTextInputState::clearAnyOtherModalDialogs(&DAT_MenuTextInputState);
  return;
}


