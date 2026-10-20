// ================= _HoldStrong::Game::GameStateStructures::processGameTick @ 0045cd10 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "MappersEnumShort": Some values do not have unique names */
/* WARNING: Enum "MappersEnumInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Game::GameStateStructures::processGameTick(GameStateStructures *this)

{
  int *piVar1;
  DWORD DVar2;
  BOOLEnum BVar3;
  int *piVar4;
  int iVar5;
  
  DAT_RotateMapOrPullDownTerrain = 0;
  if (DAT_GameSynchronyState.saveRelated != 0) {
    if (DAT_GameSynchronyState.isHost == FALSE) {
      DAT_RotateMapOrPullDownTerrain = 0;
      return;
    }
    Synchrony::GameSynchronyState::checkGameLagStatusAndKickAccordingly(&DAT_GameSynchronyState);
    return;
  }
  if (DAT_GameSynchronyState.syncStatus != 0) {
    if (DAT_GameSynchronyState.isHost == FALSE) {
      if (DAT_GameSynchronyState.syncStatus == 10) {
        DAT_GameSynchronyState.syncStatus = 0xb;
        Synchrony::GameSynchronyState::queueCommand
                  (&DAT_GameSynchronyState,GCT_SHARE_GAME_STATE_PARTIAL_HASHES);
        return;
      }
      if (DAT_GameSynchronyState.syncStatus != 1) {
        if (DAT_GameSynchronyState.syncStatus != 3) {
          DAT_RotateMapOrPullDownTerrain = 0;
          return;
        }
        DAT_GameSynchronyState.syncStatus = 4;
        Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SEND_KEEP_ALIVE);
        return;
      }
      DAT_GameSynchronyState.syncStatus = 2;
      Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SHARE_DESYNC_HASHES);
      return;
    }
    if (DAT_GameSynchronyState.syncStatus == 10) {
      Synchrony::GameSynchronyState::checkLagAndSyncStatus(&DAT_GameSynchronyState);
      return;
    }
    if (DAT_GameSynchronyState.syncStatus != 1) {
      if (DAT_GameSynchronyState.syncStatus == 2) {
        Synchrony::GameSynchronyState::sendPendingResyncCommandsInBudget(&DAT_GameSynchronyState);
        return;
      }
      if (DAT_GameSynchronyState.syncStatus < 3) {
        DAT_RotateMapOrPullDownTerrain = 0;
        return;
      }
      Synchrony::GameSynchronyState::advanceSyncStatusAndKickLaggers(&DAT_GameSynchronyState);
      return;
    }
    Synchrony::GameSynchronyState::broadcastDesyncResyncCommands(&DAT_GameSynchronyState);
    return;
  }
  if ((DAT_GameSynchronyState.quitGameVoteRelated != 0) &&
     (DVar2 = timeGetTime(), 11000 < DVar2 - DAT_GameSynchronyState.quitGameVoteRequestTime)) {
    DAT_GameSynchronyState.DAT_GameCommandParam0 = 2;
    Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SEND_QUIT_GAME_VOTE);
  }
  BVar3 = GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
  if (BVar3 != FALSE) {
    if ((DAT_GameCore.gamePausedLogical != 0) && (7 < DAT_TileMapState.DAT_FutureMapOrientation))
    goto LAB_0045ce7c;
    BVar3 = GameCore::isGameHaltingMenuOpen(&DAT_GameCore);
    if (BVar3 == FALSE) {
      Random::RNG::nextRandomNumber2(&SEC_RNG);
      Random::RNG::nextRandomNumber1(&SEC_RNG);
      DAT_GameCore.mapTimeInTicks = DAT_GameCore.mapTimeInTicks + 1;
      processSingleTimeTick(&DAT_GameState);
    }
  }
  if (DAT_TileMapState.DAT_FutureMapOrientation < 8) {
    DAT_RotateMapOrPullDownTerrain = 1;
  }
LAB_0045ce7c:
  Map::TileMapState::processMapOrientationChange(&DAT_TileMapState);
  Map::TileMapState::updateShowHiLayerOrResetChangedLayer(&DAT_TileMapState);
  Map::TileMapState::rotateFearFactorBuildingVariations(&DAT_TileMapState);
  Map::Buildings::BuildingsState::updatePathLinkageForGatesKeepsSiegeTowers(&DAT_BuildingsState);
  Map::Navigation::PathFindingState::updateSeparateAreaTileMap(&DAT_PathFindingState,0);
  Map::TileMapState::updateLogicalTileMapRelatedSections(&DAT_TileMapState);
  Map::TileMapState::updateMacroLayer(&DAT_TileMapState);
                    /* called when rotating the screen */
  Map::TileMapState::updateGfxLayer(&DAT_TileMapState);
                    /* also called when rotating the screen */
  Map::TileMapState::updateGFXLayers(&DAT_TileMapState);
  Map::Navigation::PathFindingState::setChangedLayerZeroBasedOn40x40Layer(&DAT_PathFindingState,0);
  Map::Buildings::BuildingsState::subtractPitchAndMoatFromStartingGoldInSiegeThatMode
            (&DAT_BuildingsState);
  UI::MinimapViewState::clearOldSpawnMoment(&DAT_MinimapViewState);
                    /* Game ignores pause if certain right-click actions are made */
  if (DAT_RotateMapOrPullDownTerrain == 0) {
    if (0 < (int)DAT_GameCore.gamePausedLogical) {
      return;
    }
    if (DAT_GameCore.gamePausedLogical == 0) {
      BVar3 = GameCore::isGameHaltingMenuOpen(&DAT_GameCore);
      if (BVar3 != FALSE) {
        return;
      }
    }
    else {
      DAT_GameCore.gamePausedLogical = 0;
    }
  }
  if (((DAT_GameCore.gameMode_2 == GM_EDITOR) && (DAT_GameCore.isTimeHalted2 != 0)) ||
     (BVar3 = GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar3 == FALSE)) {
    return;
  }
                    /* From here on only gets called if game is unpaused */
  resetCountsAndStatistics(&DAT_GameState);
  resetBuildingsCurrentIndexCounter(&DAT_GameState);
  Map::LandscapeState::updateWind(&DAT_LandscapeState);
  DAT_PathFindingState.field48_0x90 = 0;
  Map::Navigation::PathFindingState::updateClimbData(&DAT_PathFindingState);
  Map::Buildings::BuildingsState::updateBuildings(&DAT_BuildingsState);
  Map::TileMapState::updatePitchDitches(&DAT_TileMapState);
  Map::LandscapeState::updateTrees(&DAT_LandscapeState);
  Map::MapPropertiesState::processSingleplayerEvents(&DAT_MapPropertiesState);
  Synchrony::GameSynchronyState::checkSkirmishGameDefeat(&DAT_GameSynchronyState);
  AI::AIVState::updateBuildingsStateAndUpdateAIBuildingDecisions(&DAT_AIVState);
  Map::Units::TroopValueState::aiControlNonSkirmishUnitMovement(&DAT_TroopValueState);
  Map::Units::UnitsState::updateUnits(&DAT_UnitsState);
  Map::Entities::EntityState::updateEntities(&DAT_EntityState);
  Map::Units::UnitsState::removeUnitsSameTileLinkageIfNoLongerApplicable(&DAT_UnitsState);
  processFoodConsumption(&DAT_GameState);
  computePopulationStatistics(&DAT_GameState);
  Map::Units::TribesState::updateTribeUnitAssignments(&DAT_TribesState);
  Map::Units::TribesState::updateTribes(&DAT_TribesState);
  Map::Units::TribesState::spawnQueuedReinforcementWaves(&DAT_TribesState);
  Map::Units::TribesState::respawnDeer(&DAT_TribesState);
  Map::TileMapState::generateDustClouds(&DAT_TileMapState);
  Map::TileMapState::updateGameRelatedValue(&DAT_TileMapState);
  Global::DoNothing();
  Map::WallAndPitchState::updateDestructionConfirmationCountdown(&DAT_WallAndPitchState);
  UI::HoveredState::clearInvalidatedHoverStates(&DAT_HoveredState);
  if (DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) {
    DAT_GameState.mapAndTime.armySizeLimit = 10000;
    return;
  }
  iVar5 = 0;
  piVar4 = &DAT_GameState.playerDataArray[2].lordKilledByPlayerID;
  piVar1 = DAT_GameSynchronyState.currentAIArray + 1;
  do {
                    /* unrolled loop */
    if (((piVar1[-0x1b] != -1) || (*piVar1 != 0)) && (piVar4[-0xe7d] == 0)) {
      iVar5 = iVar5 + 1;
    }
    if (((piVar1[-0x1a] != -1) || (piVar1[1] != 0)) && (*piVar4 == 0)) {
      iVar5 = iVar5 + 1;
    }
    if (((piVar1[-0x19] != -1) || (piVar1[2] != 0)) && (piVar4[0xe7d] == 0)) {
      iVar5 = iVar5 + 1;
    }
    if (((piVar1[-0x18] != -1) || (piVar1[3] != 0)) && (piVar4[0x1cfa] == 0)) {
      iVar5 = iVar5 + 1;
    }
    piVar1 = piVar1 + 4;
    piVar4 = piVar4 + 0x39f4;
  } while ((int)piVar1 < 0x191dea0);
  if (iVar5 != 0) {
    DAT_GameState.mapAndTime.armySizeLimit = (int)(0x960 / (longlong)iVar5) + -0x28;
    return;
  }
  DAT_GameState.mapAndTime.armySizeLimit = 10000;
  return;
}


// ================= _HoldStrong::Synchrony::GameSynchronyState::determineGameTicksToPerform @ 00487a30 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Synchrony::GameSynchronyState::determineGameTicksToPerform
          (GameSynchronyState *this,int currentPlayerSlotID)

{
  int iVar1;
  int extraout_ECX;
  int iVar2;
  dword dVar3;
  int iVar4;
  
  dVar3 = DAT_GameSynchronyState.skirmishGameSpeedLevel;
  if (DAT_GameCore.gameSpeedLevel == 0) {
    DAT_GameCore.gameSpeedLevel = 0x28;
  }
  if ((DAT_GameCore.currentlyInGameUnk_0xa4 != TRUE) || (DAT_GameSynchronyState.DAT_GameHalted != 0)
     ) {
    return 0;
  }
  if ((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
     (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_SINGLE_PLAYER)) {
    DAT_GameSynchronyState.mapTimeInTicksSinglePlayer = DAT_GameCore.mapTimeInTicks;
    dVar3 = DAT_GameCore.gameSpeedLevel;
    iVar2 = DAT_GameSynchronyState.field196_0x101ad4;
  }
  else {
                    /* Calculate multiplayer game speed. */
    DAT_GameCore.gameSpeedMultiplicator = 1;
    DAT_GameSynchronyState.field196_0x101ad4 = 0;
    computeLatencyAdjustmentFromMatchTimes(&DAT_GameSynchronyState,currentPlayerSlotID);
    iVar2 = *(int *)(extraout_ECX + 0x109eac);
    if ((-1 < *(int *)(extraout_ECX + 0x109eac)) &&
       (iVar4 = *(int *)(extraout_ECX + 0x109ea8), iVar2 = DAT_GameSynchronyState.field196_0x101ad4,
       0 < iVar4)) {
      iVar1 = *(int *)(extraout_ECX + 0x109ea8);
      if (*(int *)(extraout_ECX + 0x109ee8) + 0x4b < iVar1) {
        DAT_GameSynchronyState.field196_0x101ad4 = iVar4;
        if (*(int *)(extraout_ECX + 0x109260) < 1) {
          *(undefined4 *)(extraout_ECX + 0x109260) = 1;
        }
        dVar3 = *(dword *)(extraout_ECX + 0x109260);
        iVar2 = DAT_GameSynchronyState.field196_0x101ad4;
        if ((int)*(dword *)(extraout_ECX + 0x106e38) < (int)*(dword *)(extraout_ECX + 0x109260)) {
          dVar3 = *(dword *)(extraout_ECX + 0x106e38);
        }
      }
      else {
        iVar2 = iVar4;
        if ((5 < iVar1) &&
           (dVar3 = ((5 - iVar1) * 2) / 3 + *(int *)(extraout_ECX + 0x106e38), (int)dVar3 < 0xf)) {
          dVar3 = 0xf;
        }
      }
    }
  }
  DAT_GameSynchronyState.field196_0x101ad4 = iVar2;
  if ((int)DAT_GameCore.gameSpeedMultiplicator < 0) {
    iVar2 = (int)(-1000 / (longlong)(int)dVar3) * DAT_GameCore.gameSpeedMultiplicator;
  }
  else {
    iVar2 = (int)(1000 / (longlong)(int)dVar3);
    if (1 < (int)DAT_GameCore.gameSpeedMultiplicator) {
      iVar2 = (int)((longlong)
                    ((ulonglong)(uint)(iVar2 >> 0x1f) << 0x20 |
                    1000 / (longlong)(int)dVar3 & 0xffffffffU) /
                   (longlong)(int)DAT_GameCore.gameSpeedMultiplicator);
    }
  }
  iVar4 = DAT_MillisecCarry + (DAT_GameLoopStopwatch.duration_0x0 - iVar2);
  DAT_MillisecCarry = iVar4;
  if (iVar4 < 0) {
                    /* Wait */
    if (iVar4 < -iVar2) {
      DAT_MillisecCarry = iVar4 + iVar2;
      return 0;
    }
  }
  else {
                    /* Execute game ticks */
    if (((iVar2 < (int)DAT_GameCore.averageTimePerGameTick) && (iVar2 * 2 <= iVar4)) &&
       (iVar2 == (int)(1000 / (longlong)(int)dVar3))) {
                    /* Slow down */
      DAT_MillisecCarry = 0;
      return 2;
    }
    if ((((iVar2 * 7) / 10 < (int)DAT_GameCore.averageTimePerGameTick) && (iVar2 * 2 <= iVar4)) &&
       (iVar2 == (int)(1000 / (longlong)(int)dVar3))) {
                    /* Slow down */
      DAT_MillisecCarry = 0;
      return 3;
    }
    if (iVar2 * 10 < iVar4) {
                    /* Cap game ticks per rendering */
      DAT_MillisecCarry = 0;
      return 0xb;
    }
    if (iVar2 < iVar4) {
      DAT_MillisecCarry = iVar4 - (iVar4 / iVar2) * iVar2;
      return iVar4 / iVar2 + 1;
    }
  }
  return 1;
}


// ================= _HoldStrong::Global::WinMain @ 0057be10 =================

/* WARNING: Enum "MappersEnumShort": Some values do not have unique names */
/* WARNING: Enum "eMusicIDs": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "UnsortedBinkFlagInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnumInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int _HoldStrong::Global::WinMain
              (HINSTANCE hInstance,HINSTANCE hPrevInstance,LPSTR lpCmdLine,int nShowCmd)

{
  char cVar1;
  Menu *pMVar2;
  char *pcVar3;
  HANDLE hObject;
  DWORD DVar4;
  int iVar5;
  MMRESULT MVar6;
  BOOL BVar7;
  BOOLEnum BVar8;
  int extraout_EAX;
  UINT UVar9;
  UINT _timePeriodRes;
  BOOL _timePeriodStarted;
  TIMECAPS _timeCaps;
  tagMSG _networkMessage;
  CHAR _moduleFilenameBuf [260];
  uint local_4;
  
  local_4 = MSVC_SecurityCookie ^ (uint)&_timePeriodRes;
  GetModuleFileNameA((HMODULE)0x0,_moduleFilenameBuf,0x104);
  pcVar3 = _moduleFilenameBuf;
  do {
    cVar1 = *pcVar3;
    pcVar3 = pcVar3 + 1;
  } while (cVar1 != '\0');
  for (pcVar3 = pcVar3 + (-1 - (int)(_moduleFilenameBuf + 1)); -1 < (int)pcVar3;
      pcVar3 = pcVar3 + -1) {
    if (_moduleFilenameBuf[(int)pcVar3] == '\\') {
      _moduleFilenameBuf[(int)pcVar3] = '\0';
      break;
    }
  }
  IO::ResourceManager::loadConfigPathTxt(&DAT_ResourceManager);
  if (DAT_TextureRenderCoreObject.bufferAllocStateUnk_0x0 == 0) {
    hObject = CreateMutexA((LPSECURITY_ATTRIBUTES)0x0,0,"Global\\FireflyStrongholdCrusadersExtreme")
    ;
    if ((hObject == (HANDLE)0x0) || (DVar4 = GetLastError(), DVar4 != 0xb7)) {
      Text::TextManager::loadCRTex(&DAT_TextManagerObject);
      DAT_GameCore.directDrawStatus = DetectDXVersionByLoadingDDRAW();
      _timePeriodStarted = 0;
      MVar6 = timeGetDevCaps(&_timeCaps,8);
      if (MVar6 == 0) {
        _timePeriodStarted = 1;
        UVar9 = _timeCaps.wPeriodMin;
        if (_timeCaps.wPeriodMin < 2) {
          UVar9 = 1;
        }
        if (UVar9 < _timeCaps.wPeriodMax) {
          if (_timeCaps.wPeriodMin < 2) {
            _timePeriodRes = 1;
          }
          else {
            _timePeriodRes = _timeCaps.wPeriodMin;
          }
        }
        else {
          _timePeriodRes = _timeCaps.wPeriodMax;
        }
        timeBeginPeriod(_timePeriodRes);
      }
      IO::SettingsFileState::readUserConfig(&DAT_SettingsFileState);
      IO::readSkMasters2();
      UI::Rendering::WindowAndDirectDraw::createCrusaderWindow
                (&DAT_WindowAndDirectDraw,hInstance,"Crusader",0x65);
      DAT_MouseState.waitCursorToggle = 1;
      SetCursorDependingOnProgramState();
      UI::Rendering::WindowAndDirectDraw::prepareWindowAndDDraw_2Unk
                (&DAT_WindowAndDirectDraw,TRUE,DAT_WindowAndDirectDraw.currentGameResolution);
      Audio::MSS::SoundSystem::initMiles(&DAT_SoundSystemState);
      IO::BitMapState::loadFacesBMP(&DAT_BitMapState);
      AI::AIVState::setAvailableAIV(&DAT_AIVState);
      Input::MouseState::loadAndSetCursor(&DAT_MouseState,0x68,0x69,0x72,0,0,0,0,0);
      DAT_GameCore.canBeginMainLoop = 0;
      UI::MenuHandlerState::initializeUI
                (&DAT_MenuHandlerState,DAT_RenderingDefinedData.DAT_MenuViewIDMenuMapping,
                 DAT_RenderingDefinedData.ARRAY_UCArray,"stronghold.uc");
      UI::MenuHandlerState::setupBuildMenuState(&DAT_MenuHandlerState,0x11,0x204);
                    /* setup the load menu */
      UI::MenuHandlerState::setupMenuForRendering(&DAT_MenuHandlerState,MVT_INTRO_LOGOS);
      DAT_TextureRenderCoreObject.totalLoadedGfx = 0;
      UI::Rendering::TextureRenderCore::loadGfxFile
                (&DAT_TextureRenderCoreObject,"frontend_loading.tgx");
                    /* processExtremeTrailCsv */
      DoNothing();
      DAT_MenuHandlerState.y = DAT_WindowAndDirectDraw.mainMenuBorderHeight;
      DAT_MenuHandlerState.x = DAT_WindowAndDirectDraw.mainMenuBorderWidth;
      pMVar2 = DAT_MenuHandlerState.currentMenu;
      (DAT_MenuHandlerState.currentMenu)->yPosition = DAT_WindowAndDirectDraw.mainMenuBorderHeight;
      pMVar2->xPosition = DAT_MenuHandlerState.x;
      UI::Rendering::TextureRenderCore::drawGfxOnFlaggedSurface
                (&DAT_TextureRenderCoreObject,0,
                 (DAT_WindowAndDirectDraw.resolutionX -
                 DAT_TextureRenderCoreObject.loadedGfxArray[0].width) / 2,
                 (DAT_WindowAndDirectDraw.resolutionY -
                 DAT_TextureRenderCoreObject.loadedGfxArray[0].height) / 2);
      UI::Rendering::PencilRenderCore::drawBlendedBlackBox
                (&DAT_PencilRenderCore,DAT_MenuHandlerState.x + 0xe7,DAT_MenuHandlerState.y + 0x236,
                 DAT_MenuHandlerState.x + 0x239,DAT_MenuHandlerState.y + 0x248,0x14);
      UI::Rendering::PencilRenderCore::drawBorderBox
                (&DAT_PencilRenderCore,DAT_MenuHandlerState.x + 0xe7,DAT_MenuHandlerState.y + 0x236,
                 DAT_MenuHandlerState.x + 0x239,DAT_MenuHandlerState.y + 0x248,COL_BLACK.shortValue)
      ;
      UI::Rendering::WindowAndDirectDraw::renderBltAndFlip(&DAT_WindowAndDirectDraw,0);
      Audio::MSS::SoundSystem::setupVolumeAndSoundID(&DAT_SoundSystemState,MUSIC_TUNE_CHOIR2);
      Audio::MSS::SoundSystem::playRandomAmbientMusic(&DAT_SoundSystemState);
      UI::Rendering::TextureRenderCore::loadGmFiles
                (&DAT_TextureRenderCoreObject,DAT_MapDefinedData.DAT_GMNameArray[0]);
      Text::TextManager::setupFontSizeClassObjects(&DAT_TextManagerObject);
      DAT_GameCore.missionNumber1to20 = 1000;
      Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_INTRO_LOGOS,0);
      Synchrony::GameSynchronyState::handleCommandLineArguments(&DAT_GameSynchronyState,lpCmdLine);
      Audio::SFX::SFXState::loadSFX(&DAT_SFXState,0);
      IO::ResourceManager::loadMapHeaders(&DAT_ResourceManager,TRUE);
      if (DAT_GameSynchronyState.useTCPIP == FALSE) {
        Map::TileMapState::setupAllMapSections(&DAT_TileMapState);
      }
      DAT_TileMapState.mapSize = 400;
      Map::TileMapState::resetHeightAndMapBorders(&DAT_TileMapState,400);
      DAT_PathFindingState.toggleUpdateSeparateAreaTileMap = 1;
      Map::Navigation::PathFindingState::updatePathLinkageLayerForEachBuildingAtEachTile
                (&DAT_PathFindingState);
      Map::Navigation::PathFindingState::updateSeparateAreaTileMap(&DAT_PathFindingState,1);
      Map::Buildings::BuildingsState::updatePathLinkageLayerForAllBuildings(&DAT_BuildingsState);
      Map::TileMapState::forceFullTileMapRedraw(&DAT_TileMapState);
      UI::MinimapViewState::setTileColorsDependingOnMapSize(&DAT_MinimapViewState,0,100);
      UI::MinimapViewState::setMapPropertyDependingOnMapSize(&DAT_MinimapViewState,0,100);
      Rendering::ViewportRenderState::setViewportBasedOnMapSize(&DAT_ViewportRenderState);
      TIME_Sum_1 = timeGetTime();
      INT_00ee2350 = 0;
      FLAG_ChristmasAIMessage01to04 = FALSE;
      INT_00ee2358 = 0;
      INT_00ee235c = 0;
      INT_00ee2360 = 0;
      FLAG_JokeAIMessage05 = FALSE;
      FLAG_JokeAIMessage06 = FALSE;
      INT_00ee236c = 0;
      INT_00ee2370 = 0;
      FLAG_JokeAIMessage09 = FALSE;
      INT_00ee2378 = 0;
      INT_00ee237c = 0;
      FLAG_JokeAIMessage12 = FALSE;
      INT_00ee2384 = 0;
      INT_00ee2388 = 0;
      INT_00ee238c = 0;
      FLAG_JokeAIMessage16 = FALSE;
      TIME_2 = TIME_Sum_1;
      Map::Buildings::BuildingsState::initBuildingCosts(&DAT_BuildingsState);
      DAT_GameCore.canBeginMainLoop = 1;
      DAT_MouseState.waitCursorToggle = 0;
      if (DAT_WindowAndDirectDraw.postWindowCloseMessage == 0) {
LAB_0057c250:
                    /* game loop start */
        BVar7 = PeekMessageA(&_networkMessage,(HWND)0x0,0,0,0);
        if (BVar7 == 0) {
          if (((DAT_WindowAndDirectDraw.isNotProcessingInputEvents == FALSE) &&
              (DAT_WindowAndDirectDraw.gameFocused != FALSE)) ||
             ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY &&
              (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER)))) {
            PlayJokeVideoBasedOnCurrentTimeAndPlayTime();
            AI::AICState::someChatMessageSelection(&DAT_AICState);
            Util::Timing::Stopwatch::start(&DAT_GameLoopStopwatch);
            Input::ModifierKeyState::updateCtrlShiftAltKeyStateMemory(&DAT_ModifierKeyState);
            Game::GameCore::processMenuViewSwitch(&DAT_GameCore);
            Audio::MSS::SoundSystem::playRandomAmbientMusic(&DAT_SoundSystemState);
                    /* receive commands when in multiplayer */
            Synchrony::GameSynchronyState::receiveAllTransmittedCommands(&DAT_GameSynchronyState);
            if ((DAT_WindowAndDirectDraw.isNotProcessingInputEvents == FALSE) &&
               (DAT_WindowAndDirectDraw.gameFocused != FALSE)) {
              Input::MouseState::updateMouseStateBasedOnCursorAndTime(&DAT_MouseState);
              SetCursorDependingOnProgramState();
            }
            DAT_GameCore.gameTicksLastLoop = DAT_GameCore.gameTicksThisLoop;
            DAT_GameCore.gameTicksThisLoop =
                 Synchrony::GameSynchronyState::determineGameTicksToPerform
                           (&DAT_GameSynchronyState,DAT_GameSynchronyState.currentPlayerSlotID);
            Synchrony::GameSynchronyState::queueSynchronizedAutosaveProtocol
                      (&DAT_GameSynchronyState);
            Game::GameCore::viewportAndScrollingRelated(&DAT_GameCore);
            if (DAT_GameCore.gameTicksThisLoop != 0) {
              DAT_GameCore.timeBeforeRunningGameTicksThisLoop = timeGetTime();
            }
            DAT_GameCore.performedGameTicksThisLoop = 0;
            if (0 < (int)DAT_GameCore.gameTicksThisLoop) {
              do {
                Synchrony::GameSynchronyState::processWaitingCommands(&DAT_GameSynchronyState);
                    /* game ticks are done here */
                Game::GameStateStructures::processGameTick(&DAT_GameState);
                Synchrony::GameSynchronyState::receiveAllTransmittedCommands
                          (&DAT_GameSynchronyState);
                Rendering::Bink::BinkControlClass::processBinkFrames(&DAT_BinkControlState);
                TacticalPowersFill();
                if (DAT_GameSynchronyState.DAT_GameHalted != 0) break;
                DAT_GameCore.performedGameTicksThisLoop =
                     DAT_GameCore.performedGameTicksThisLoop + 1;
              } while ((int)DAT_GameCore.performedGameTicksThisLoop <
                       (int)DAT_GameCore.gameTicksThisLoop);
            }
            if (DAT_GameCore.gameTicksThisLoop != 0) {
              DVar4 = timeGetTime();
              DAT_GameCore.averageTimePerGameTick =
                   (DVar4 - DAT_GameCore.timeBeforeRunningGameTicksThisLoop) /
                   DAT_GameCore.gameTicksThisLoop;
            }
            BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
            if (BVar8 != FALSE) {
              Synchrony::GameSynchronyState::checkMultiplayerLaggingPlayers(&DAT_GameSynchronyState)
              ;
            }
            if ((DAT_WindowAndDirectDraw.isNotProcessingInputEvents == FALSE) &&
               (DAT_WindowAndDirectDraw.gameFocused != FALSE)) {
              UI::ScrollingHandler::handleScrolling(&DAT_ScrollingHandler);
              UI::MenuModalComposition::handleActiveModalDialogUnk(&DAT_MenuModalComposition2);
              if ((DAT_MenuModalComposition2.minus1 == 0) &&
                 (UI::MenuModalComposition::handleActiveModalDialogUnk(&DAT_MenuModalComposition3),
                 DAT_MenuModalComposition3.minus1 == 0)) {
                UI::MenuModalComposition::handleActiveModalDialogUnk(&DAT_MenuModalComposition1);
              }
              if (((((DAT_MenuModalComposition1.minus1 == 0) &&
                    (DAT_MenuModalComposition2.minus1 == 0)) &&
                   (DAT_MenuModalComposition3.minus1 == 0)) &&
                  (DAT_GameCore.hasMenuRenderedUnk == 0)) ||
                 (DAT_BinkControlState.unknown01_zero[1] != 0)) {
                UI::Menu::updateMenuButtons(DAT_MenuHandlerState.currentMenu);
              }
              UI::HoveredState::calculateHoveredTile(&DAT_HoveredState);
              BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
              if (BVar8 != FALSE) {
                if (((DAT_GameCore.activeMenuTab.tabType != BASMTT_SIEGETENT_SIEGETOWER) &&
                    (DAT_GameCore.activeMenuTab.tabType != BASMTT_SIEGETENT_SHIELD)) ||
                   (DAT_WindowAndDirectDraw.mbr_0xd0 = 2,
                   DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU)) {
                  DAT_WindowAndDirectDraw.mbr_0xd0 = 1;
                }
                DAT_GameCore.currentlyInGameUnk_0xa4 = TRUE;
                Rendering::ViewportRenderState::renderMap(&DAT_ViewportRenderState);
                UI::Rendering::RenderDisplayElementsUnk();
                Rendering::ViewportRenderState::updateBuildingPreviewPosition
                          (&DAT_ViewportRenderState,DAT_MouseState.screenSpaceX,
                           DAT_MouseState.screenSpaceY);
                Input::MouseState::drawMouseBasedBox(&DAT_MouseState);
                Input::MouseState::renderPreviewAtMouseLocation(&DAT_MouseState);
              }
              Rendering::Bink::BinkControlClass::processBinkFrames(&DAT_BinkControlState);
              DAT_GameCore.hasMenuRenderedUnk = 0;
              if (((DAT_GameCore.gameMode_2 == GM_CRUSADER_TUTORIAL) ||
                  (DAT_GameCore.countdown != 0)) ||
                 (((DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial != FALSE ||
                   (((BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE
                     || (DAT_MenuHandlerState.isBuildMenuTransitioning_0x18 != FALSE)) ||
                    (DAT_GameState.mapAndTime.weekChanged != 0)))) ||
                  (BVar8 = Game::GameCore::isInBuildingTab(&DAT_GameCore), BVar8 != FALSE)))) {
                BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
                if (BVar8 != FALSE) {
                  DAT_WindowAndDirectDraw.unk_resetViewportRelated = 2;
                }
                Rendering::Bink::BinkControlClass::copyBinkToVideoBuffer(&DAT_BinkControlState,2);
                UI::Rendering::RenderCurrentMenuView();
                Rendering::Bink::BinkControlClass::copyBinkToVideoBuffer(&DAT_BinkControlState,1);
                pMVar2 = DAT_MenuHandlerState.currentMenu;
                UI::Menu::handleMenuItems(DAT_MenuHandlerState.currentMenu,MIHS_PREPARE_AND_RENDER);
                UI::Menu::renderConstructionMenu(pMVar2);
              }
              else if (DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_LANDSCAPING) {
                if (DAT_GameCore.activeMenuTab.tabType != BASMTT_SIEGETENT_SIEGETOWER) {
                  DAT_MinimapViewState.field0_0x0 = 1;
                  UI::MinimapViewState::renderMinimapLandscaping
                            (&DAT_MinimapViewState,DAT_MenuHandlerState.x + 0x298,
                             DAT_MenuHandlerState.y + 0x1d0,0x80,0x80);
                  DAT_WindowAndDirectDraw.unk_resetViewportRelated = 4;
                }
              }
              else if (DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU) {
                if ((DAT_GameCore.activeMenuTab.tabType != BASMTT_SIEGETENT_SIEGETOWER) &&
                   (DAT_GameCore.activeMenuTab.tabType != BASMTT_SIEGETENT_SHIELD)) {
LAB_0057c5e0:
                  if ((DAT_BinkControlState.binkObjPtrArray[0] == (HBINK)0x0) &&
                     ((DAT_BinkControlState.binkObjPtrArray[1] == (HBINK)0x0 &&
                      (DAT_GameCore.isBinkVideoPlaying == 0)))) {
                    DAT_RenderMiniMapOrBinkFlag = DAT_RenderMiniMapOrBinkFlag ^ TRUE;
                    if (DAT_RenderMiniMapOrBinkFlag != FALSE) {
                      DAT_MinimapViewState.field0_0x0 = 1;
                      UI::MinimapViewState::renderMinimapMain(&DAT_MinimapViewState);
                      DAT_WindowAndDirectDraw.unk_resetViewportRelated = 3;
                    }
                  }
                  else {
                    Rendering::Bink::BinkControlClass::copyBinkToVideoBuffer
                              (&DAT_BinkControlState,1);
                    DAT_WindowAndDirectDraw.unk_resetViewportRelated = 3;
                    DAT_RenderMiniMapOrBinkFlag = FALSE;
                  }
                }
              }
              else if (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU)
              goto LAB_0057c5e0;
              UI::Menu::handleMenuItems
                        (DAT_MenuHandlerState.currentMenu,MIHS_PREPARE_AND_RENDER_FOR_FLAG_0X800000)
              ;
                    /* draw modal dialogs */
              UI::MenuModalComposition::renderMenuModal(&DAT_MenuModalComposition1);
              UI::MenuModalComposition::renderMenuModal(&DAT_MenuModalComposition3);
              UI::MenuModalComposition::renderMenuModal(&DAT_MenuModalComposition2);
              Rendering::Bink::BinkControlClass::copyBinkToVideoBuffer(&DAT_BinkControlState,0);
              UI::Rendering::TextureRenderCore::moveOverlappingMenuPartsToMapSurface
                        (&DAT_TextureRenderCoreObject);
              Audio::SFX::SFXState::soundRelatedMethod1(&DAT_SFXState);
              UI::Rendering::WindowAndDirectDraw::renderBltAndFlip(&DAT_WindowAndDirectDraw,0);
            }
            Util::Timing::Stopwatch::stop(&DAT_GameLoopStopwatch);
            if (((DAT_GameCore.gamePausedLogical == 0) &&
                (BVar8 = Game::GameCore::isGameHaltingMenuOpen(&DAT_GameCore), BVar8 == FALSE)) &&
               (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 != FALSE)) {
              if (TIME_ReceivedMessage_2 != 0) {
                DVar4 = timeGetTime();
                iVar5 = DVar4 - TIME_ReceivedMessage_2;
                TIME_ReceivedMessage_2 = 0;
                DAT_GameCore.timeSum_2 = DAT_GameCore.timeSum_2 + iVar5;
              }
            }
            else if (TIME_ReceivedMessage_2 == 0) {
              TIME_ReceivedMessage_2 = timeGetTime();
            }
            if (TIME_ReceivedMessage_1 != 0) {
              DVar4 = timeGetTime();
              iVar5 = DVar4 - TIME_ReceivedMessage_1;
              TIME_ReceivedMessage_1 = 0;
              TIME_Sum_1 = TIME_Sum_1 + iVar5;
            }
          }
          else {
            Audio::SFX::SFXState::soundRelatedMethod1(&DAT_SFXState);
            Synchrony::GameSynchronyState::receiveAllTransmittedCommands(&DAT_GameSynchronyState);
            WaitMessage();
            if (TIME_ReceivedMessage_1 == 0) {
              TIME_ReceivedMessage_1 = timeGetTime();
            }
            if (TIME_ReceivedMessage_2 == 0) {
              TIME_ReceivedMessage_2 = timeGetTime();
            }
          }
        }
        else {
          BVar7 = GetMessageA(&_networkMessage,(HWND)0x0,0,0);
          if (BVar7 == 0) goto LAB_0057c7b0;
          TranslateMessage(&_networkMessage);
          DispatchMessageA(&_networkMessage);
        }
        if (DAT_WindowAndDirectDraw.postWindowCloseMessage == 1) {
          PostMessageA(DAT_WindowAndDirectDraw.windowHandle,0x10,0,0);
          DAT_WindowAndDirectDraw.postWindowCloseMessage = 0;
        }
        goto LAB_0057c250;
      }
LAB_0057c7b0:
                    /* game loop end */
      if (_timePeriodStarted == 1) {
        timeEndPeriod(_timePeriodRes);
      }
      Synchrony::GameSynchronyState::disconnectDPlay(&DAT_GameSynchronyState);
      IO::SettingsFileState::writeUserConfig(&DAT_SettingsFileState);
      IO::WriteSkMasters2();
      Audio::MSS::SoundSystem::shutdownSoundSystem(&DAT_SoundSystemState);
      UI::Rendering::WindowAndDirectDraw::finalizeDirectDrawShutdown(&DAT_WindowAndDirectDraw);
      if (DAT_GameSynchronyState.openOnClose != FALSE) {
        ShellExecuteA((HWND)0x0,"open",DAT_GameSynchronyState.shellExecuteTarget,"+svc strongholdce"
                      ,(LPCSTR)0x0,1);
      }
      OS::_exit(0);
      return extraout_EAX;
    }
                    /* only go here if Crusader is already running */
    CloseHandle(hObject);
    MessageBoxA((HWND)0x0,"Stronghold Crusader is already running.","Stronghold Crusader Error",0);
  }
  iVar5 = HoldStrong_lib::__security_check_cookie(local_4 ^ (uint)&_timePeriodRes);
  return iVar5;
}


