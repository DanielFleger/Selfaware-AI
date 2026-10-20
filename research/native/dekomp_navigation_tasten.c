// ================= MenuItemActionHandler_InGameMenu_PeasantBuildAndRightClickMenuSelection @ 0x00434350 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::UI::MenuItemActionHandler_InGameMenu_PeasantBuildAndRightClickMenuSelection
          (int param_1,...)

{
  DWORD DVar1;
  int iVar2;
  BOOLEnum BVar3;
  dword elementState;
  
  if (DAT_GameSynchronyState.syncStatus != 0) {
    return;
  }
  if (DAT_GameSynchronyState.saveRelated != 0) {
    return;
  }
  if (((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
      (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER)) &&
     (DAT_00b960f8 != 0x42)) {
    if (INT_00b960f0 == 0) {
      DVar1 = timeGetTime();
      INT_00b960f0 = DVar1 + 20000;
    }
    else {
      DVar1 = timeGetTime();
      if (0x5dc < (int)(DVar1 - INT_00b960f0)) {
        DAT_GameSynchronyState.DAT_GameCommandParam0 = DAT_00b960f8;
        DAT_GameSynchronyState.DAT_GameCommandParam1 = DAT_GameSynchronyState.currentPlayerSlotID;
        INT_00b960f0 = DVar1;
        Synchrony::GameSynchronyState::queueCommand
                  (&DAT_GameSynchronyState,GCT_UPDATE_LOBBY_FACE_BITMAPSPECIALTRANSMITLOGIC);
        DAT_00b960f8 = DAT_00b960f8 + 1;
      }
    }
  }
  if (DAT_GameCore.gameMode_2 == GM_EDITOR) {
LAB_004344b0:
    Global::CheckDisplayElementByIDAndSetForUnlimitedDisplay
              (DEID_PEOPLE_LEFT_TO_PLACE,(uint)(0x8fb < (int)DAT_UnitsState.DAT_UnitCount));
  }
  else if (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) {
LAB_004344a8:
    if (DAT_GameCore.gameMode_2 == GM_EDITOR) goto LAB_004344b0;
  }
  else if ((DAT_GameCore.gameMode_2 != GM_BUILDERUnk) ||
          (DAT_MapPropertiesState.SEC_U3_MapType2_1 != MT_SIEGE)) {
    if (DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU) {
      iVar2 = Map::Units::UnitsState::getArmySize(DAT_GameSynchronyState.currentPlayerSlotID);
      if (iVar2 == 0) {
        if (DAT_GameCore.activeMenuTab.tabType == BASMTT_FLETCHER) {
          if (DAT_GameCore.menuSwitchDelay == -1) {
            iVar2 = Game::GameStateStructures::singlePlayerHasKeepAndGranaryCheck(&DAT_GameState);
            if (iVar2 == 1) {
              Global::CheckDisplayElementByIDAndSetForUnlimitedDisplay
                        (DEID_KEEP_AND_GRANERY_PLACEMENT_INFO,0);
              DAT_GameCore.buildmenuMenuTabToSwitchTo.tabType = BASMTT_HUNTERSHUT;
              Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
              goto LAB_004344a8;
            }
            elementState = 1;
            goto LAB_00434498;
          }
        }
        else if (DAT_GameCore.activeMenuTab.tabType == BASMTT_UNUSED_WITCHHOIST) goto LAB_00434497;
        DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
        Global::CheckDisplayElementByIDAndSetForUnlimitedDisplay
                  (DEID_KEEP_AND_GRANERY_PLACEMENT_INFO,0);
      }
      else if (DAT_GameCore.activeMenuTab.tabType == BASMTT_UNUSED_WITCHHOIST) {
LAB_00434497:
        elementState = 2;
LAB_00434498:
        Global::CheckDisplayElementByIDAndSetForUnlimitedDisplay
                  (DEID_KEEP_AND_GRANERY_PLACEMENT_INFO,elementState);
        DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
      }
    }
    goto LAB_004344a8;
  }
  if (DAT_MouseState.mouseBasedEvent == 1) {
    Map::TileMapState::triggerLoweredView(&DAT_TileMapState,3);
    DAT_GameCore.field86_0x15c = 1;
    if (DAT_GameCore.gameMode_2 != GM_CRUSADER_TUTORIAL) goto LAB_004345e4;
    iVar2 = 4;
  }
  else if ((((DAT_MouseState.rightClickState == FALSE) || (DAT_MouseState.mouseBasedEvent == 2)) &&
           ((DAT_ModifierKeyState.ctrl == 0 || (DAT_ModifierKeyState.downArrow == 0)))) &&
          (DAT_ModifierKeyState.v == 0)) {
    Map::TileMapState::triggerLoweredView(&DAT_TileMapState,4);
    if (DAT_GameCore.gameMode_2 != GM_CRUSADER_TUTORIAL) goto LAB_004345e4;
    iVar2 = 5;
  }
  else if (DAT_MouseState.mouseBasedEvent == 3) {
    Map::TileMapState::setMapRotation(&DAT_TileMapState,DAT_MouseState.mapOrientationCopy3);
    DAT_GameCore.field86_0x15c = 1;
    if (DAT_GameCore.gameMode_2 != GM_CRUSADER_TUTORIAL) goto LAB_004345e4;
    iVar2 = 2;
  }
  else if (DAT_MouseState.mouseBasedEvent == 4) {
    DAT_MouseState.field51_0x198 = 2;
    _HoldStrong::Rendering::ViewportRenderState::resetupViewport
              (&DAT_ViewportRenderState,
               (uint)(DAT_ViewportRenderState.viewportState.isZoomedOutUnk == 0));
    DAT_WindowAndDirectDraw.unk_resetViewportRelated = 2;
    DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
    DAT_GameCore.field86_0x15c = 1;
    if (DAT_GameCore.gameMode_2 != GM_CRUSADER_TUTORIAL) goto LAB_004345e4;
    iVar2 = 3;
  }
  else {
    if (DAT_MouseState.mouseBasedEvent != 5) goto LAB_004345e4;
    DAT_MouseState.field52_0x19c = 2;
    Map::TileMapState::toggleFlatView(&DAT_TileMapState,DAT_TileMapState.flatViewToggleValue1 ^ 1);
    DAT_GameCore.field86_0x15c = 1;
    if (DAT_GameCore.gameMode_2 != GM_CRUSADER_TUTORIAL) goto LAB_004345e4;
    iVar2 = 0x11;
  }
  recordTutorialPlayerAction(iVar2);
LAB_004345e4:
  if (DAT_ViewportRenderState.viewportState.field0_0x0 == 0) {
    if (DAT_MouseState.rightClickStart != 0) {
      DAT_TileMapState.currentMapperCommand = M_MAPPER_NULL;
      DAT_GameCore.field86_0x15c = 0;
    }
    Input::MouseState::storeXYAndResetMouseState(&DAT_MouseState);
    return;
  }
  if (DAT_MouseState.rightClickStart == 0) {
    if (((DAT_MouseState.rightClickStop != 0) &&
        (DAT_TileMapState.currentMapperCommand == M_MAPPER_MOAT)) &&
       (DAT_GameCore.field86_0x15c == 0)) {
      DAT_TileMapState.currentMapperCommand = M_MAPPER_NULL;
    }
    Map::TileMapState::noop1(&DAT_TileMapState,DAT_ViewportRenderState.viewportState.mouseTile);
    if (DAT_MouseState.leftClickState == FALSE) {
      if (DAT_UnitsState.unitCountOfSelection[DAT_GameSynchronyState.currentPlayerSlotID] < 1) {
        Rendering::AlphaAndButtonSurface::ProcessBuildingClickBonus
                  (&AlphaAndButtonSurfaceObj,
                   DAT_ViewportRenderState.viewportState.mouseRayBuildingID);
      }
      if (DAT_MouseState.draggingStopped == FALSE) {
        return;
      }
      if (DAT_TileMapState.currentMapperCommand != M_MAPPER_NULL) {
        return;
      }
    }
    else if (DAT_TileMapState.currentMapperCommand != M_MAPPER_NULL) {
      if ((DAT_MouseState.leftClickStart == 0) &&
         (DAT_ViewportRenderState.viewportState.field4_0x10 ==
          DAT_ViewportRenderState.viewportState.mouseTile)) {
        return;
      }
      DAT_ViewportRenderState.viewportState.field4_0x10 =
           DAT_ViewportRenderState.viewportState.mouseTile;
      _HoldStrong::Rendering::ViewportRenderState::setupMouseTileXY();
      return;
    }
    if (((((DAT_UnitsState.unitCountOfSelection[DAT_GameSynchronyState.currentPlayerSlotID] < 1) &&
          (DAT_UnitsState.totalUnitsInSelection < 1)) &&
         ((DVar1 = timeGetTime(), DAT_MouseState.draggingStopped != FALSE &&
          ((((DAT_MouseState.field31_0x94 == 0 && (DAT_MouseState._152_4_ == 0)) &&
            (BVar3 = Rendering::AlphaAndButtonSurface::SelectUnitAndOpenStatusMenu
                               (&AlphaAndButtonSurfaceObj,
                                DAT_ViewportRenderState.viewportState.mouseRayUnitID),
            BVar3 == FALSE)) &&
           ((199 < (int)(DVar1 - DAT_ViewportRenderState.viewportState.field13_0x34) ||
            (BVar3 = Rendering::AlphaAndButtonSurface::SelectUnitAndOpenStatusMenu
                               (&AlphaAndButtonSurfaceObj,
                                DAT_ViewportRenderState.viewportState.mouseRayLastUnitID),
            BVar3 == FALSE)))))))) &&
        ((BVar3 = Rendering::AlphaAndButtonSurface::openBuildingStatusMenuForBuildingID
                            (&AlphaAndButtonSurfaceObj,
                             DAT_ViewportRenderState.viewportState.mouseRayBuildingID),
         BVar3 == FALSE &&
         (((DAT_TileMapState.LogicLayer[DAT_ViewportRenderState.viewportState.mouseAtomRefFloorTile]
           & 2) != 0 &&
          ((DAT_TileMapState.WallOwnerLayer
            [DAT_ViewportRenderState.viewportState.mouseAtomRefFloorTile] & 7) + 1 ==
           DAT_GameSynchronyState.currentPlayerSlotID)))))) &&
       (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].stockpile.id != 0)
       ) {
      DAT_GameCore.buildingandstatusmenuMenuTabToSwitchTo = 0xb;
      Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_BUILDING_AND_STATUS_MENU,0);
      DAT_BuildingsState.newSelectedUnitID = 0;
      DAT_BuildingsState.newSelectedBuildingID =
           DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].stockpile.id;
      return;
    }
  }
  else {
    if (DAT_TileMapState.currentMapperCommand != M_MAPPER_MOAT) {
      DAT_TileMapState.currentMapperCommand = M_MAPPER_NULL;
    }
    DAT_GameCore.field86_0x15c = 0;
  }
  return;
}



// ================= WindowMsgProcessingFunc @ 0x004b2ae0 =================

/* WARNING: Enum "GeneralWindowsMessage": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "UnsortedBinkFlagInt": Some values do not have unique names */
/* This is the WindowProc
   LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
   https://docs.microsoft.com/en-us/previous-versions/windows/desktop/legacy/ms633573(v=vs.85)
   
   It handles input and is in theory the main communication point with the OS. SHC however also
   gathers input data using other C functions. - TheRedDaemon
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

LRESULT _HoldStrong::Global::WindowMsgProcessingFunc
                  (HWND windowHandle,GeneralWindowsMessage message,WindowsVirtualKey wParam,
                  LPARAM lParam)

{
  char cVar1;
  ushort uVar2;
  ushort uVar3;
  int iVar4;
  XYPairShort tile;
  short sVar5;
  uint uVar6;
  int iVar7;
  BOOLEnum BVar8;
  int iVar9;
  char *pcVar10;
  LRESULT LVar11;
  char *pcVar12;
  uint uVar13;
  int iVar14;
  HBINK *ppFVar15;
  int *piVar16;
  short yMousePos;
  MouseClickInteraction clickType;
  HWND _hwnd;
  PAINTSTRUCT _paintstruct;
  
  iVar7 = DAT_GameSynchronyState.currentPlayerSlotID;
  uVar6 = MSVC_SecurityCookie ^ (uint)&_hwnd;
  _hwnd = windowHandle;
  if (WM_KEYDOWN < message) {
                    /* param_4 >> 0x10 == y */
    sVar5 = (short)lParam;
    yMousePos = (short)((uint)lParam >> 0x10);
    if (message < WM_LBUTTONDOWN) {
      if (message == WM_MOUSEMOVE) {
        Input::MouseState::updateMousePositionAndClicks(&DAT_MouseState,sVar5,yMousePos,MCI_MOVE);
        goto switchD_004b4d0c_doDefWindowProcA;
      }
      switch(message) {
      case WM_KEYUP:
                    /* WM_KEYUP */
        switch(wParam) {
        case VK_LEFT:
                    /* VK_LEFT */
          DAT_ScrollingHandler.leftKeyDown_0x1c = FALSE;
          break;
        case VK_UP:
                    /* VK_UP */
          DAT_ScrollingHandler.upKeyDown_0x24 = FALSE;
          break;
        case VK_RIGHT:
                    /* VK_RIGHT */
          DAT_ScrollingHandler.rightKeyDown_0x18 = FALSE;
          break;
        case VK_DOWN:
                    /* VK_DOWN */
          DAT_ModifierKeyState.downArrow = 0;
          DAT_ScrollingHandler.downKeyDown_0x20 = FALSE;
        }
        break;
      case WM_CHAR:
                    /* **** Note that keydown events are translated in char events if not swalloed
                       ****
                       WM_CHAR */
        Text::UserTextHandler::handleCharacterCode(&DAT_UserTextHandlerState,(byte)wParam);
        Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,wParam);
        break;
      case WM_SYSKEYDOWN:
                    /* WM_SYSKEYDOWN (ALT + ?) */
        DAT_ModifierKeyState.keyDownUnk = 1;
        switch(wParam) {
        case VK_ALT:
                    /* VK_MENU (ALT key) */
          LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
          return LVar11;
        case VK_ZERO:
        case VK_ONE:
        case VK_TWO:
        case VK_THREE:
        case VK_FOUR:
        case VK_FIVE:
        case VK_SIX:
        case VK_SEVEN:
        case VK_EIGHT:
        case VK_NINE:
          goto switchD_004b482b_caseD_30;
        case VK_C:
                    /* c was pressed */
          if ((DAT_GameCore.cheatModeFlag != FALSE) &&
             (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE)) {
            DAT_GameCore.unlockAllHistoricalCampaigns = 1;
          }
          break;
        case VK_D:
                    /* key: D */
          if ((DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_LANDSCAPING) ||
             ((DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU &&
              (DAT_GameCore.gameMode_2 == GM_EDITOR)))) {
            DAT_ViewportRenderState.DAT_MapEditorDisplayLayer =
                 DAT_ViewportRenderState.DAT_MapEditorDisplayLayer + 1;
            if (2 < (int)DAT_ViewportRenderState.DAT_MapEditorDisplayLayer) {
              DAT_ViewportRenderState.DAT_MapEditorDisplayLayer = 0;
            }
            CheckDisplayElementByIDAndSetForUnlimitedDisplay
                      (DEID_CONNECT_AND_PATH_LINKAGE_INFO_TEXT,
                       DAT_ViewportRenderState.DAT_MapEditorDisplayLayer);
          }
          break;
        case VK_E:
                    /* key E */
          if (((DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_PROPERTIES) ||
              (DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_LANDSCAPING)) ||
             ((DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU &&
              (DAT_GameCore.gameMode_2 == GM_EDITOR)))) {
            Map::Units::UnitsState::killAllUnownedUnits(&DAT_UnitsState);
          }
          break;
        case VK_H:
                    /* H */
          if (DAT_GameCore.gameMode_2 == GM_EDITOR) {
            DAT_GameCore.isTimeHalted = (BOOLEnum)(DAT_GameCore.isTimeHalted2 == 0);
            DAT_GameCore.isTimeHalted2 = DAT_GameCore.isTimeHalted;
          }
          break;
        case VK_K:
                    /* K */
          if ((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) &&
             (DAT_GameCore.cheatModeFlag != FALSE)) {
            DAT_GameCore.solitaryAllBuildingsAreFree =
                 (BOOLEnum)(DAT_GameCore.solitaryAllBuildingsAreFree == FALSE);
          }
          break;
        case VK_Q:
                    /* Q */
          BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
          if (BVar8 != FALSE) {
            UI::Rendering::WindowAndDirectDraw::takeScreenshot
                      (&DAT_WindowAndDirectDraw,
                       DAT_ShortcutDefinedData.DAT_ScreenshotFilenameVariant);
            DAT_ShortcutDefinedData.DAT_ScreenshotFilenameVariant =
                 DAT_ShortcutDefinedData.DAT_ScreenshotFilenameVariant + 1;
          }
          break;
        case VK_R:
                    /* R */
          DAT_GameCore.altRToggleMinimapHideWildlife =
               DAT_GameCore.altRToggleMinimapHideWildlife == 0;
          break;
        case VK_T:
          if ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
             (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER)) {
            UI::Rendering::TogglePlayerPingDisplayElementUnk(DEID_PLAYER_PING_Unk_19,1);
          }
          break;
        case VK_U:
                    /* U */
          if (((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) &&
              (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU)) &&
             (DAT_BuildingsState.buildings[DAT_BuildingsState.menuSelectedBuildingID].buildingType
              == BT_DUNGEON)) {
            DAT_GameCore.solitaryAltUDungeon = TRUE;
          }
          break;
        case VK_V:
                    /* V */
          if (DAT_GameCore.gameMode_2 == GM_EDITOR) {
            iVar9 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].lordID
            ;
            if (iVar9 != 0) {
              iVar4 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                      lordUID;
              iVar14 = DAT_UnitsState.units[iVar9].uid;
              DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].lordID = 0;
              DAT_GameState.playerDataArray[iVar7].lordUID = 0;
              if (iVar4 == iVar14) {
                DAT_UnitsState.units[iVar9].logicalState = ULS_REMOVE;
              }
            }
            DAT_GameState.playerDataArray[iVar7].lordKilledByPlayerID = 0;
          }
          break;
        case VK_X:
                    /* X */
          if ((DAT_GameSynchronyState.currentGameMode != GM_MULTIPLAYER) &&
             (DAT_GameCore.cheatModeFlag != FALSE)) {
            DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].popularity =
                 10000;
            piVar16 = DAT_GameState.playerDataArray[iVar7].currentResources + 0xf;
            *piVar16 = *piVar16 + 1000;
          }
          break;
        case VK_NUMPAD0:
        case VK_NUMPAD1:
        case VK_NUMPAD2:
        case VK_NUMPAD3:
        case VK_NUMPAD4:
        case VK_NUMPAD5:
        case VK_NUMPAD6:
        case VK_NUMPAD7:
        case VK_NUMPAD8:
        case VK_NUMPAD9:
          wParam = wParam - VK_ZERO;
switchD_004b482b_caseD_30:
                    /* 0 - 9 */
                    /* ? basically, pressing a number above the letters on keyboard or on the numpad
                        */
          BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
          if (BVar8 == FALSE) break;
          goto LAB_004b4af5;
        case VK_F10:
          goto switchD_004b2d9a_caseD_72;
        case VK_F11:
        case VK_F12:
          goto switchD_004b482b_caseD_7a;
        case VK_OEM_COMMA:
                    /* COMMA */
          if (DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_PROPERTIES) {
            if (DAT_MenuModalComposition1.activeModalDialogID == MMT_EDITOR_MAP_TYPE_QUICK_CHANGE) {
              UI::MenuModalComposition::activateModalDialog
                        (&DAT_MenuModalComposition1,MMT_NONE,FALSE);
            }
            else if (DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE) {
              UI::MenuModalComposition::activateModalDialog
                        (&DAT_MenuModalComposition1,MMT_EDITOR_MAP_TYPE_QUICK_CHANGE,FALSE);
            }
          }
          break;
        case VK_OEM3:
        case VK_OEM7:
                    /* ~ or single quote ` */
          if (DAT_GameCore.currentMenuViewType == MVT_EDIT_SCENARIO) {
            DAT_GameState.mapAndTime.editScenarioExtraOptions =
                 DAT_GameState.mapAndTime.editScenarioExtraOptions ^ 1;
          }
        }
      }
      goto switchD_004b4d0c_doDefWindowProcA;
    }
    switch(message) {
    case WM_LBUTTONDOWN:
      Input::MouseState::updateMousePositionAndClicks(&DAT_MouseState,sVar5,yMousePos,MCI_LEFTDOWN);
      break;
    case WM_LBUTTONUP:
      clickType = MCI_LEFTUP;
      goto LAB_004b4d15;
    case WM_RBUTTONDOWN:
      Input::MouseState::updateMousePositionAndClicks(&DAT_MouseState,sVar5,yMousePos,MCI_RIGHTDOWN)
      ;
      break;
    case WM_RBUTTONUP:
      clickType = MCI_RIGHTUP;
      goto LAB_004b4d15;
    case WM_MBUTTONDOWN:
      Input::MouseState::updateMousePositionAndClicks(&DAT_MouseState,sVar5,yMousePos,MCI_MIDDOWN);
      break;
    case WM_MBUTTONUP:
      clickType = MCI_MIDUP;
LAB_004b4d15:
      Input::MouseState::updateMousePositionAndClicks(&DAT_MouseState,sVar5,yMousePos,clickType);
      break;
    case WM_MOUSEWHEEL:
      Input::MouseState::updateMouseWheelStatus(&DAT_MouseState,(int)(short)(wParam >> 0x10));
    }
    goto switchD_004b4d0c_doDefWindowProcA;
  }
  if (message != WM_KEYDOWN) {
    switch(message) {
    case WM_CREATE:
    case WM_MOVE:
      if (DAT_WindowAndDirectDraw.runGameAsExclusiveFullscreen != FALSE) break;
      DAT_WindowAndDirectDraw.windowMoveEventBlitCountdown = 10;
      goto LAB_004b2b45;
    case WM_DESTROY:
      DAT_WindowAndDirectDraw.postWindowCloseMessage = 3;
      DAT_WindowAndDirectDraw.windowHandle = (HWND)0x0;
      PostQuitMessage(0);
      break;
    case WM_SIZE:
      if (DAT_WindowAndDirectDraw.runGameAsExclusiveFullscreen != FALSE) {
        iVar7 = GetSystemMetrics(1);
        iVar9 = GetSystemMetrics(0);
        SetRect(&DAT_WindowAndDirectDraw.clientOnScreenCoords,0,0,iVar9,iVar7);
        break;
      }
LAB_004b2b45:
      UI::Rendering::WindowAndDirectDraw::reinitWindow(&DAT_WindowAndDirectDraw);
                    /* The following three calls fill the RECT structure with coords that describe
                       the client in screen coordinates.  */
      GetClientRect(windowHandle,&DAT_WindowAndDirectDraw.clientOnScreenCoords);
      ClientToScreen(windowHandle,(LPPOINT)&DAT_WindowAndDirectDraw.clientOnScreenCoords);
      ClientToScreen(windowHandle,(LPPOINT)&DAT_WindowAndDirectDraw.clientOnScreenCoords.right);
      break;
    case WM_SETFOCUS:
      Audio::MSS::SoundSystem::resumeAudioSample(&DAT_SoundSystemState);
      ppFVar15 = DAT_BinkControlState.binkObjPtrArray;
      do {
        if (*ppFVar15 != (HBINK)0x0) {
          BinkPause(*ppFVar15,0);
        }
        ppFVar15 = ppFVar15 + 1;
      } while ((int)ppFVar15 < 0x2157570);
      break;
    case WM_KILLFOCUS:
      Audio::MSS::SoundSystem::pauseAudioSample(&DAT_SoundSystemState);
      ppFVar15 = DAT_BinkControlState.binkObjPtrArray;
      do {
        if (*ppFVar15 != (HBINK)0x0) {
          BinkPause(*ppFVar15,1);
        }
        ppFVar15 = ppFVar15 + 1;
      } while ((int)ppFVar15 < 0x2157570);
      break;
    case WM_PAINT:
      BeginPaint(windowHandle,&_paintstruct);
      EndPaint(windowHandle,&_paintstruct);
      BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
      if (BVar8 == FALSE) {
        DAT_WindowAndDirectDraw.unk_resetViewportRelated = 2;
        UI::Rendering::WindowAndDirectDraw::renderBltAndFlip(&DAT_WindowAndDirectDraw,1);
      }
      goto LAB_004b2cfd;
    case WM_CLOSE:
    case WM_QUIT:
      DAT_WindowAndDirectDraw.postWindowCloseMessage = 3;
      break;
    case WM_ACTIVATEAPP:
      sVar5 = (short)wParam;
      if (sVar5 == 1) {
        DAT_WindowAndDirectDraw.gameFocused = TRUE;
      }
      else if (sVar5 == 2) {
        DAT_WindowAndDirectDraw.gameFocused = TRUE;
      }
      else if (sVar5 == 0) {
                    /* app is being deactivated */
        DAT_WindowAndDirectDraw.gameFocused = FALSE;
        DAT_WindowAndDirectDraw.isNotProcessingInputEvents = TRUE;
        Audio::MSS::SoundSystem::endSpeechSoundStreams(&DAT_SoundSystemState);
      }
      if ((DAT_WindowAndDirectDraw.isNotProcessingInputEvents != FALSE) &&
         (DAT_WindowAndDirectDraw.gameFocused != FALSE)) {
                    /* restore everything */
        BVar8 = UI::Rendering::WindowAndDirectDraw::restoreDXSurfaces(&DAT_WindowAndDirectDraw);
        if (BVar8 != FALSE) {
                    /* Restoring DirectX succeeded */
          UI::Rendering::WindowAndDirectDraw::reinitWindow(&DAT_WindowAndDirectDraw);
        }
        Input::MouseState::resetMouseState2(&DAT_MouseState);
        Input::MouseState::storeXYAndResetMouseState(&DAT_MouseState);
      }
      DAT_WindowAndDirectDraw.unk_resetViewportRelated = 1;
      break;
    case WM_DISPLAYCHANGE:
      DAT_WindowAndDirectDraw.screenHorizontalResolutionInPixels = lParam & 0xffff;
      DAT_WindowAndDirectDraw.screenVerticalResolutionInPixels = (uint)lParam >> 0x10;
      DAT_WindowAndDirectDraw.depthBitsPerPixel = wParam;
    }
    goto switchD_004b4d0c_doDefWindowProcA;
  }
                    /* cheat mode activation check */
                    /* assuming WM_KEYDOWN */
  DAT_ModifierKeyState.keyDownUnk = 1;
  if ((((DAT_GameCore.currentMenuViewType == MVT_MAIN_MENU) && (DAT_ModifierKeyState.ctrl != 0)) &&
      (DAT_GameCore.cheatModeFlag == FALSE)) &&
     (wParam == (byte)DAT_ShortcutDefinedData.cheatCode[DAT_CheatCodeStringTrackerIndex])) {
    iVar9 = DAT_CheatCodeStringTrackerIndex + 1;
    iVar7 = DAT_CheatCodeStringTrackerIndex + 1;
    DAT_CheatCodeStringTrackerIndex = iVar9;
    if (DAT_ShortcutDefinedData.cheatCode[iVar7] == '\0') {
      DAT_GameCore.cheatModeFlag = TRUE;
    }
  }
  else {
    DAT_CheatCodeStringTrackerIndex = 0;
  }
  switch(wParam) {
  case VK_BACKSPACE:
                    /* VK_BACK (Backspace) */
    Text::UserTextHandler::handleBackspace(&DAT_UserTextHandlerState);
    Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xf8);
    break;
  case VK_TAB:
                    /* VK_TAB */
    if ((lParam & 0x40000000U) == 0) {
      Game::GameCore::hideOrUnhideUI(&DAT_GameCore);
    }
    break;
  case VK_ENTER:
                    /* VK_RETURN */
    Text::UserTextHandler::handleReturnKey(&DAT_UserTextHandlerState);
    Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xf1);
    if ((((DAT_GameCore.gameMode_2 == GM_SKIRMISH_AND_MULTIPLAYER) &&
         (DAT_MenuModalComposition1.activeModalDialogID == MMT_CHAT)) &&
        (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER)) ||
       (DAT_GameCore.currentMenuViewType == MVT_LOBBY_MENU)) {
      if (DAT_UserTextHandlerState.textArrayIndex == 4) {
        pcVar10 = Text::UserTextHandler::getCurrentText(&DAT_UserTextHandlerState);
        pcVar12 = pcVar10;
        do {
          cVar1 = *pcVar12;
          pcVar12 = pcVar12 + 1;
        } while (cVar1 != '\0');
        iVar7 = 0;
        if (0 < (int)pcVar12 - (int)(pcVar10 + 1)) {
          do {
            if (pcVar10[iVar7] != ' ') {
              DAT_GameSynchronyState.DAT_ChatTauntOrMessage = 0;
              Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_TAUNT_OR_CHAT)
              ;
              Text::UserTextHandler::clearTextAndCursor(&DAT_UserTextHandlerState);
              if (DAT_GameCore.currentMenuViewType != MVT_LOBBY_MENU) {
                UI::MenuModalComposition::activateModalDialog
                          (&DAT_MenuModalComposition1,MMT_NONE,FALSE);
              }
              break;
            }
            iVar7 = iVar7 + 1;
          } while (iVar7 < (int)pcVar12 - (int)(pcVar10 + 1));
        }
      }
    }
    else if (((DAT_GameCore.gameMode_2 == GM_SKIRMISH_AND_MULTIPLAYER) &&
             (DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE)) &&
            (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 != FALSE)) {
      if (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_SINGLE_PLAYER) {
        UI::MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition1,MMT_ALLIES,FALSE);
      }
      else {
        UI::MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition1,MMT_CHAT,FALSE);
        DAT_UserTextHandlerState.allowUserTextInput = 0;
        Text::UserTextHandler::resetToTextIndex(&DAT_UserTextHandlerState,4);
        Text::UserTextHandler::clearTextAndCursor(&DAT_UserTextHandlerState);
      }
    }
    else if (DAT_MenuModalComposition1.activeModalDialogID == MMT_IDENTITY_OPTIONS) {
      UI::MenuItemActionHandler_IdentityOptions_Confirm(0x11);
    }
    break;
  case VK_ESCAPE:
                    /* ESC */
    if ((lParam & 0x40000000U) != 0) break;
    if ((DAT_GameCore.currentMenuViewType == MVT_UNKNOWN_26_CAMPAIGN_RELATEDUnk) ||
       (DAT_GameCore.currentMenuViewType == MVT_INTRO_VIDEO)) {
      Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_GAME_START_ENTER_NAME,0);
      goto LAB_004b38a3;
    }
    if (DAT_MenuModalComposition1.activeModalDialogID == MMT_QUIT_DIALOG) {
      if (DAT_MenuTextInputState.DAT_MenuOptionsActionParameter == 0x2f) goto LAB_004b38a3;
    }
    else {
      if (DAT_MenuModalComposition1.activeModalDialogID == MMT_ONLINE_VOTE_QUIT_GAME) {
        DAT_GameSynchronyState.DAT_GameCommandParam0 = 1;
                    /* Escape ally switching */
        Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SEND_QUIT_GAME_VOTE)
        ;
        goto LAB_004b33a8;
      }
      if (DAT_MenuModalComposition1.activeModalDialogID == MMT_NEW_EVENT_CONDITION) {
        UI::MenuItemActionHandler_NewEventCondition_Main(0x25);
        LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
        return LVar11;
      }
      if ((DAT_MenuModalComposition1.activeModalDialogID == MMT_CHAT) ||
         (DAT_MenuModalComposition1.activeModalDialogID == MMT_SKIRMISH_CONNECTION_OPTIONS))
      goto LAB_004b33a8;
    }
    if (DAT_MenuTextInputState.currentModalDialog != MMT_NO_MENU) {
      if (DAT_MenuModalComposition1.activeModalDialogID == MMT_QUIT_DIALOG) {
        if (DAT_MenuTextInputState.DAT_MenuOptionsActionParameter == 2000) {
          DAT_GameSynchronyState.DAT_GameCommandParam0 = 1;
          Synchrony::GameSynchronyState::queueCommand
                    (&DAT_GameSynchronyState,GCT_START_OR_STOP_SEND_MAP_FILEUnk);
        }
      }
      else if (DAT_MenuModalComposition1.activeModalDialogID == MMT_IDENTITY_OPTIONS) {
        UI::MenuItemActionHandler_IdentityOptions_Confirm(0x11);
        LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
        return LVar11;
      }
      UI::MenuTextInputState::popModalDialog(&DAT_MenuTextInputState);
      LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
      return LVar11;
    }
    if (DAT_GameCore.currentMenuViewType == MVT_UNUSED_HELP_TEXT_EDITOR) {
      Text::TextEditorState::openUnusedHelpTextEditorDialog(&DAT_TextEditorState,-1);
      LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
      return LVar11;
    }
    if (DAT_GameCore.currentMenuViewType == MVT_CREDITS) {
      Text::TextEditorState::closeHelpDialogAndReturnToMenu(&DAT_TextEditorState);
    }
    else {
      if ((DAT_TextEditorState.helpDialogVariant != 0) &&
         (DAT_GameCore.currentMenuViewType != MVT_SCENARIO_DESCRIPTION)) {
        Text::TextEditorState::closeHelpDialogAndReturnToMenu(&DAT_TextEditorState);
        LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
        return LVar11;
      }
      if (DAT_GameCore.currentMenuViewType == MVT_SELECT_CRUSADE) goto LAB_004b34ae;
      if (DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_LANDSCAPING) {
        UI::MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition1,MMT_NONE,FALSE);
LAB_004b3517:
        Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_MAP_EDITOR_PROPERTIES,0);
        LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
        return LVar11;
      }
      BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
      if (BVar8 != FALSE) {
        if (DAT_GameCore.gameMode_2 != GM_EDITOR) {
          if (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) {
            Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_UNUSED_CREATE_SIEGE,0);
            LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
            return LVar11;
          }
          if (DAT_GameCore.specialMultiplayerState != 0) {
            Synchrony::GameSynchronyState::disconnectDPlay(&DAT_GameSynchronyState);
            DAT_WindowAndDirectDraw.postWindowCloseMessage = 1;
            LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
            return LVar11;
          }
          if (((DAT_GameCore.menuSwitchDelay == -1) ||
              (DAT_GameCore.menuViewToSwitchTo == MVT_BUILD_MENU)) ||
             (DAT_GameCore.menuViewToSwitchTo == MVT_BUILDING_AND_STATUS_MENU)) {
            UI::MenuTextInputState::activateModalDialogAndClearText
                      (&DAT_MenuTextInputState,MMT_PAUSE_MENU);
            LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
            return LVar11;
          }
          goto LAB_004b38a3;
        }
        goto LAB_004b3517;
      }
      if ((DAT_GameCore.currentMenuViewType == MVT_MP_CONNECTION) ||
         (DAT_GameCore.currentMenuViewType == MVT_LOBBY_MENU)) {
        UI::MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition1,MMT_NONE,FALSE);
        Synchrony::GameSynchronyState::disconnectDPlay(&DAT_GameSynchronyState);
        Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_MAIN_MENU,0);
        LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
        return LVar11;
      }
      if (DAT_GameCore.currentMenuViewType != MVT_SINGLEPLAYER_MAP_CHOICE) {
        if (DAT_GameCore.currentMenuViewType == MVT_GAME_START_ENTER_NAME) goto LAB_004b38a3;
        if (((DAT_GameCore.currentMenuViewType != MVT_HISTORIC_CAMPAIGN_SELECT) &&
            (DAT_GameCore.currentMenuViewType != MVT_UNUSED_ECONOMIC_GAMETYPE_SELECT)) &&
           (DAT_GameCore.currentMenuViewType != MVT_CUSTOM_SCENARIOS)) {
          if (DAT_GameCore.currentMenuViewType ==
              (MVT_UNUSED_HELP_TEXT_EDITOR|MVT_UNUSED_OLD_TITLE_MENU)) {
            if (DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE) {
              Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_INTRO_LOGOS,0);
              LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
              return LVar11;
            }
            UI::MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition1,MMT_NONE,FALSE)
            ;
            LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
            return LVar11;
          }
          if (DAT_GameCore.currentMenuViewType == 0x18) {
            UI::MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition1,MMT_NONE,FALSE)
            ;
            Game::GameCore::switchToMenuView
                      (&DAT_GameCore,MVT_UNUSED_HELP_TEXT_EDITOR|MVT_UNUSED_OLD_TITLE_MENU,0);
            LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
            return LVar11;
          }
          if (DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_PROPERTIES) {
LAB_004b33a8:
            UI::MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition1,MMT_NONE,FALSE)
            ;
            LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
            return LVar11;
          }
          if ((DAT_GameCore.currentMenuViewType != MVT_HISTORIC_MISSION_SELECT) &&
             (DAT_GameCore.currentMenuViewType != MVT_UNUSED_ECONOMIC_MISSION_SELECTUnk)) {
            if (DAT_GameCore.currentMenuViewType == MVT_NEW_MAP_MAPTYPE) {
              UI::MenuModalComposition::activateModalDialog
                        (&DAT_MenuModalComposition1,MMT_NONE,FALSE);
              Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_CUSTOM_SCENARIOS,0);
              LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
              return LVar11;
            }
            if (DAT_GameCore.currentMenuViewType == MVT_NEW_MAP_MAPSIZE) {
              UI::MenuModalComposition::activateModalDialog
                        (&DAT_MenuModalComposition1,MMT_NONE,FALSE);
              Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_NEW_MAP_MAPTYPE,0);
              LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
              return LVar11;
            }
            if (DAT_GameCore.currentMenuViewType == MVT_UNUSED_CHOOSE_AVAILABLE_KEEPS) {
              UI::MenuModalComposition::activateModalDialog
                        (&DAT_MenuModalComposition1,MMT_NONE,FALSE);
LAB_004b3756:
              Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_NEW_MAP_MAPSIZE,0);
              LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
              return LVar11;
            }
            if ((((((DAT_GameCore.currentMenuViewType != MVT_UNUSED_SOME_MISSION_STARTUnk) &&
                   (DAT_GameCore.currentMenuViewType != MVT_UNKNOWN_26_CAMPAIGN_RELATEDUnk)) &&
                  (DAT_GameCore.currentMenuViewType != MVT_UNKNOWN_27_CAMPAIGNUnk)) &&
                 ((DAT_GameCore.currentMenuViewType != MVT_SCENARIO_DESCRIPTION &&
                  (DAT_GameCore.currentMenuViewType != MVT_MISSION_FINISHED_TRANSITION)))) &&
                (DAT_GameCore.currentMenuViewType != MVT_GAME_LOSTUnk)) &&
               (DAT_GameCore.currentMenuViewType != MVT_EDIT_SCENARIO)) {
              if (DAT_GameCore.currentMenuViewType == MVT_HISTORIC_CAMPAIGN_INTRO) {
                Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_HISTORIC_MISSION_PICTURE,0);
                Audio::MSS::SoundSystem::endSpeechStreamsAndResetLoopFlags(&DAT_SoundSystemState);
                LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
                return LVar11;
              }
              if ((DAT_GameCore.currentMenuViewType == MVT_HISTORIC_MISSION_PICTURE) ||
                 (DAT_GameCore.currentMenuViewType == MVT_HISTORIC_MISSION_INTRO)) {
                Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_SCENARIO_DESCRIPTION,0);
                Audio::MSS::SoundSystem::endSpeechStreamsAndResetLoopFlags(&DAT_SoundSystemState);
                LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
                return LVar11;
              }
              if (DAT_GameCore.currentMenuViewType == MVT_UNUSED_CHOOSE_GAME_TYPE)
              goto LAB_004b3756;
              if (DAT_GameCore.currentMenuViewType == MVT_MAIN_MENU) {
                UI::MenuTextInputState::activateModalDialogAndClearText
                          (&DAT_MenuTextInputState,MMT_MAIN_MENU_OPTIONS);
                LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
                return LVar11;
              }
            }
LAB_004b38a3:
            LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
            return LVar11;
          }
        }
      }
    }
    UI::MenuModalComposition::activateModalDialog(&DAT_MenuModalComposition1,MMT_NONE,FALSE);
LAB_004b34ae:
    Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_MAIN_MENU,0);
    LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
    return LVar11;
  case VK_SPACE:
                    /* VK_SPACE */
    if ((lParam & 0x40000000U) == 0) {
      if (DAT_GameCore.gameMode_2 == GM_CRUSADER_TUTORIAL) {
        iVar7 = Input::GetCurrentTutorialStep();
        if (0x1c < iVar7) {
          Map::TileMapState::toggleFlatView
                    (&DAT_TileMapState,DAT_TileMapState.flatViewToggleValue1 ^ 1);
        }
      }
      else {
        BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
        if ((BVar8 != FALSE) && (DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE)) {
          Map::TileMapState::toggleFlatView
                    (&DAT_TileMapState,DAT_TileMapState.flatViewToggleValue1 ^ 1);
        }
      }
    }
    break;
  case VK_PAGE_UP:
                    /* VK_PRIOR (Page Up) */
    Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xfa);
    break;
  case VK_PAGE_DOWN:
                    /* VK_NEXT (Page Down) */
    Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xfb);
    break;
  case VK_END:
                    /* VK_END */
    Text::UserTextHandler::moveCursorToEnd(&DAT_UserTextHandlerState);
    Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xf7);
    break;
  case VK_HOME:
                    /* VK_HOME */
    Text::UserTextHandler::resetCursorToStart(&DAT_UserTextHandlerState);
    Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xf6);
    break;
  case VK_LEFT:
                    /* VK_LEFT */
    Text::UserTextHandler::handleLeftKey(&DAT_UserTextHandlerState);
    BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
    if ((((BVar8 == FALSE) || (DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE)) ||
        (DAT_ModifierKeyState.ctrl == 0)) || (DAT_MouseState.rightClickState != FALSE)) {
      if ((DAT_GameCore.gameMode_2 != GM_SKIRMISH_AND_MULTIPLAYER) ||
         (DAT_MenuModalComposition1.activeModalDialogID != MMT_CHAT)) {
        DAT_ScrollingHandler.leftKeyDown_0x1c = TRUE;
      }
      Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xf2);
    }
    else {
      uVar13 = DAT_TileMapState.mapOrientation + 2U & 0x80000007;
      if ((int)uVar13 < 0) {
        uVar13 = (uVar13 - 1 | 0xfffffff8) + 1;
      }
      Map::TileMapState::setMapRotation(&DAT_TileMapState,uVar13);
      Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xf2);
    }
    break;
  case VK_UP:
                    /* VK_UP */
    BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
    if (((BVar8 != FALSE) && (DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE)) &&
       ((DAT_ModifierKeyState.ctrl != 0 && (DAT_MouseState.rightClickState == FALSE)))) {
                    /* zoom */
      Rendering::ViewportRenderState::resetupViewport
                (&DAT_ViewportRenderState,
                 (uint)(DAT_ViewportRenderState.viewportState.isZoomedOutUnk == 0));
      DAT_WindowAndDirectDraw.unk_resetViewportRelated = 2;
      DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
    }
    if ((DAT_GameCore.gameMode_2 != GM_SKIRMISH_AND_MULTIPLAYER) ||
       (DAT_MenuModalComposition1.activeModalDialogID != MMT_CHAT)) {
      DAT_ScrollingHandler.upKeyDown_0x24 = TRUE;
    }
    Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xf4);
    break;
  case VK_RIGHT:
                    /* VK_RIGHT */
    Text::UserTextHandler::handleRightKey(&DAT_UserTextHandlerState);
    BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
    if ((((BVar8 == FALSE) || (DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE)) ||
        (DAT_ModifierKeyState.ctrl == 0)) || (DAT_MouseState.rightClickState != FALSE)) {
      if ((DAT_GameCore.gameMode_2 != GM_SKIRMISH_AND_MULTIPLAYER) ||
         (DAT_MenuModalComposition1.activeModalDialogID != MMT_CHAT)) {
        DAT_ScrollingHandler.rightKeyDown_0x18 = TRUE;
      }
      Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xf3);
    }
    else {
      uVar13 = DAT_TileMapState.mapOrientation + 6U & 0x80000007;
      if ((int)uVar13 < 0) {
        uVar13 = (uVar13 - 1 | 0xfffffff8) + 1;
      }
      Map::TileMapState::setMapRotation(&DAT_TileMapState,uVar13);
      Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xf3);
    }
    break;
  case VK_DOWN:
                    /* VK_DOWN */
    BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
    if (((BVar8 == FALSE) || (DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE)) ||
       ((DAT_ModifierKeyState.ctrl == 0 || (DAT_MouseState.rightClickState != FALSE)))) {
      if ((DAT_GameCore.gameMode_2 != GM_SKIRMISH_AND_MULTIPLAYER) ||
         (DAT_MenuModalComposition1.activeModalDialogID != MMT_CHAT)) {
        DAT_ScrollingHandler.downKeyDown_0x20 = TRUE;
      }
      Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xf5);
    }
    else {
      Map::TileMapState::triggerLoweredView(&DAT_TileMapState,3);
      DAT_ModifierKeyState.downArrow = 1;
      Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xf5);
    }
    break;
  case VK_INSERT:
                    /* VK_INSERT */
    DAT_InsertKeyState.insert = DAT_InsertKeyState.insert ^ 1;
    break;
  case VK_DELETE_KEY:
                    /* VK_DELETE */
    Text::UserTextHandler::handleDeleteKey(&DAT_UserTextHandlerState);
    Text::UserTextHandler::handleCharacterIntoInputBuffer(&DAT_UserTextHandlerState,0xf9);
    break;
  case VK_ZERO:
  case VK_ONE:
  case VK_TWO:
  case VK_THREE:
  case VK_FOUR:
  case VK_FIVE:
  case VK_SIX:
  case VK_SEVEN:
  case VK_EIGHT:
  case VK_NINE:
    goto switchD_004b2d9a_caseD_30;
  case VK_A:
                    /* A */
    if ((((lParam & 0x40000000U) != 0) ||
        (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE)) ||
       (DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE)) break;
    if (DAT_ModifierKeyState.shift != 0) {
      if (DAT_GameCore.viewportFocusBeforeArmoryHotkey != -1) {
        Rendering::ViewportRenderState::focusOnTile
                  (&DAT_ViewportRenderState,DAT_GameCore.viewportFocusBeforeArmoryHotkey);
        if (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU) {
          Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
        }
        DAT_GameCore.viewportFocusBeforeArmoryHotkey = -1;
      }
      break;
    }
    if (DAT_ModifierKeyState.ctrl != 0) {
      iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].armory.id;
      if (iVar7 != 0) {
        UI::Rendering::AlphaAndButtonSurface::openBuildingStatusMenuForBuildingID
                  (&AlphaAndButtonSurfaceObj,iVar7);
      }
      break;
    }
    iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].armory.id;
    if (iVar7 == 0) break;
    DAT_GameCore.viewportFocusBeforeArmoryHotkey = Rendering::ViewportBasedTileNumber();
    goto LAB_004b3b12;
  case VK_B:
                    /* B */
    if ((((lParam & 0x40000000U) != 0) ||
        (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE)) ||
       (DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE)) break;
    if (DAT_ModifierKeyState.shift != 0) {
      if (DAT_GameCore.viewportFocusBeforeBarracksHotkey != -1) {
        Rendering::ViewportRenderState::focusOnTile
                  (&DAT_ViewportRenderState,DAT_GameCore.viewportFocusBeforeBarracksHotkey);
        if (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU) {
          Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
        }
        DAT_GameCore.viewportFocusBeforeBarracksHotkey = -1;
      }
      break;
    }
    if (DAT_ModifierKeyState.ctrl != 0) {
      iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].barracks.id;
      if (iVar7 != 0) {
        UI::Rendering::AlphaAndButtonSurface::openBuildingStatusMenuForBuildingID
                  (&AlphaAndButtonSurfaceObj,iVar7);
      }
      break;
    }
    iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].barracks.id;
    if (iVar7 == 0) break;
    DAT_GameCore.viewportFocusBeforeBarracksHotkey = Rendering::ViewportBasedTileNumber();
    goto LAB_004b3b12;
  case VK_C:
                    /* C */
    BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
    if (((BVar8 != FALSE) && (DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE)) &&
       (DAT_MouseState.rightClickState == FALSE)) {
      uVar13 = DAT_TileMapState.mapOrientation + 6U & 0x80000007;
      if ((int)uVar13 < 0) {
        uVar13 = (uVar13 - 1 | 0xfffffff8) + 1;
      }
      Map::TileMapState::setMapRotation(&DAT_TileMapState,uVar13);
    }
    break;
  case VK_E:
                    /* E */
    if (((DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE) &&
        (DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU)) &&
       ((DAT_GameCore.activeMenuTab.tabType == BASMTT_SIEGETENT_BATTERINGRAM ||
        (DAT_GameCore.activeMenuTab.tabType == BASMTT_SIEGETENT_SHIELD)))) {
      Map::Units::TribesState::queueUnitStance
                (&DAT_TribesState,DAT_TribesState.DAT_CurrentTribeID,2);
    }
    break;
  case VK_G:
                    /* G */
    if ((((lParam & 0x40000000U) != 0) ||
        (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE)) ||
       (DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE)) break;
    if (DAT_ModifierKeyState.shift != 0) {
      if (DAT_GameCore.viewportFocusBeforeGranaryHotkey != -1) {
        Rendering::ViewportRenderState::focusOnTile
                  (&DAT_ViewportRenderState,DAT_GameCore.viewportFocusBeforeGranaryHotkey);
        if (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU) {
          Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
        }
        DAT_GameCore.viewportFocusBeforeGranaryHotkey = -1;
      }
      break;
    }
    if (DAT_ModifierKeyState.ctrl != 0) {
      iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].granary.id;
      if (iVar7 != 0) {
        UI::Rendering::AlphaAndButtonSurface::openBuildingStatusMenuForBuildingID
                  (&AlphaAndButtonSurfaceObj,iVar7);
      }
      break;
    }
    iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].granary.id;
    if (iVar7 == 0) break;
    DAT_GameCore.viewportFocusBeforeGranaryHotkey = Rendering::ViewportBasedTileNumber();
    goto LAB_004b3a17;
  case VK_H:
                    /* H */
    if ((((lParam & 0x40000000U) != 0) ||
        (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE)) ||
       (DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE)) break;
    if (DAT_ModifierKeyState.shift != 0) {
      if (DAT_GameCore.viewportFocusBeforeKeepHotkey != -1) {
        Rendering::ViewportRenderState::focusOnTile
                  (&DAT_ViewportRenderState,DAT_GameCore.viewportFocusBeforeKeepHotkey);
        if (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU) {
          Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
        }
        DAT_GameCore.viewportFocusBeforeKeepHotkey = -1;
      }
      break;
    }
    if (DAT_ModifierKeyState.ctrl != 0) {
      iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].keep.id;
      if (iVar7 != 0) {
        UI::Rendering::AlphaAndButtonSurface::openBuildingStatusMenuForBuildingID
                  (&AlphaAndButtonSurfaceObj,iVar7);
      }
      break;
    }
    iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].keep.id;
    if (iVar7 == 0) break;
    DAT_GameCore.viewportFocusBeforeKeepHotkey = Rendering::ViewportBasedTileNumber();
    goto LAB_004b3a17;
  case VK_I:
                    /* I */
    if ((((lParam & 0x40000000U) != 0) ||
        (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE)) ||
       (DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE)) break;
    if (DAT_ModifierKeyState.shift != 0) {
      if (DAT_GameCore.viewportFocusBeforeEngineersGuildHotkey != -1) {
        Rendering::ViewportRenderState::focusOnTile
                  (&DAT_ViewportRenderState,DAT_GameCore.viewportFocusBeforeEngineersGuildHotkey);
        if (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU) {
          Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
        }
        DAT_GameCore.viewportFocusBeforeEngineersGuildHotkey = -1;
      }
      break;
    }
    if (DAT_ModifierKeyState.ctrl != 0) {
      iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
              engineersGuild.id;
      if (iVar7 != 0) {
        UI::Rendering::AlphaAndButtonSurface::openBuildingStatusMenuForBuildingID
                  (&AlphaAndButtonSurfaceObj,iVar7);
      }
      break;
    }
    iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].engineersGuild
            .id;
    if (iVar7 == 0) break;
    DAT_GameCore.viewportFocusBeforeEngineersGuildHotkey = Rendering::ViewportBasedTileNumber();
    goto LAB_004b3a17;
  case VK_L:
                    /* L */
    if ((((lParam & 0x40000000U) == 0) &&
        (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 != FALSE)) &&
       (DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE)) {
      if (DAT_ModifierKeyState.shift == 0) {
        iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].lordID;
        if (((iVar7 != 0) && (DAT_UnitsState.units[iVar7].unitType == UT_LORD)) &&
           ((DAT_UnitsState.units[iVar7].owner == DAT_GameSynchronyState.currentPlayerSlotID &&
            (DAT_UnitsState.units[iVar7].logicalState == ULS_NORMAL)))) {
          Rendering::ViewportRenderState::focusOnTile
                    (&DAT_ViewportRenderState,DAT_UnitsState.units[iVar7].tile);
        }
      }
      else {
        iVar7 = 0;
        do {
          iVar9 = DAT_ShortcutDefinedData.DAT_CyclingLordID;
          DAT_ShortcutDefinedData.DAT_CyclingLordID = DAT_ShortcutDefinedData.DAT_CyclingLordID + 1;
          if (DAT_ShortcutDefinedData.DAT_CyclingLordID == 9) {
            DAT_ShortcutDefinedData.DAT_CyclingLordID = 1;
          }
          iVar9 = Map::Units::UnitsState::getAliveLordForPlayer(&DAT_UnitsState,iVar9);
          if (iVar9 != 0) {
            Rendering::ViewportRenderState::focusOnTile
                      (&DAT_ViewportRenderState,DAT_UnitsState.units[iVar9].tile);
            break;
          }
          iVar7 = iVar7 + 1;
        } while (iVar7 < 8);
      }
    }
    break;
  case VK_M:
                    /* M */
    if ((((lParam & 0x40000000U) != 0) ||
        (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE)) ||
       (DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE)) break;
    if (DAT_ModifierKeyState.shift != 0) {
      if (DAT_GameCore.viewportFocusBeforeMarketHotkey != -1) {
        Rendering::ViewportRenderState::focusOnTile
                  (&DAT_ViewportRenderState,DAT_GameCore.viewportFocusBeforeMarketHotkey);
        if (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU) {
          Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
        }
        DAT_GameCore.viewportFocusBeforeMarketHotkey = -1;
      }
      break;
    }
    if (DAT_ModifierKeyState.ctrl != 0) {
      iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].marketplace.
              id;
      if (iVar7 != 0) {
        UI::Rendering::AlphaAndButtonSurface::openBuildingStatusMenuForBuildingID
                  (&AlphaAndButtonSurfaceObj,iVar7);
      }
      break;
    }
    iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].marketplace.id
    ;
    if (iVar7 == 0) break;
    DAT_GameCore.viewportFocusBeforeMarketHotkey = Rendering::ViewportBasedTileNumber();
    goto LAB_004b3b12;
  case VK_N:
                    /* N */
    if ((((lParam & 0x40000000U) != 0) ||
        (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE)) ||
       (DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE)) break;
    if (DAT_ModifierKeyState.shift != 0) {
      if (DAT_GameCore.viewportFocusBeforeMercenaryHotkey != -1) {
        Rendering::ViewportRenderState::focusOnTile
                  (&DAT_ViewportRenderState,DAT_GameCore.viewportFocusBeforeMercenaryHotkey);
        if (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU) {
          Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
        }
        DAT_GameCore.viewportFocusBeforeMercenaryHotkey = -1;
      }
      break;
    }
    if (DAT_ModifierKeyState.ctrl != 0) {
      iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
              mercenaryPost.id;
      if (iVar7 != 0) {
        UI::Rendering::AlphaAndButtonSurface::openBuildingStatusMenuForBuildingID
                  (&AlphaAndButtonSurfaceObj,iVar7);
      }
      break;
    }
    iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].mercenaryPost.
            id;
    if (iVar7 == 0) break;
    DAT_GameCore.viewportFocusBeforeMercenaryHotkey = Rendering::ViewportBasedTileNumber();
LAB_004b3b12:
                    /* b press */
    uVar2 = DAT_BuildingsState.buildings[iVar7].y;
    uVar3 = DAT_BuildingsState.buildings[iVar7].x;
LAB_004b3a35:
    Rendering::ViewportRenderState::focusOnCoordinate
              (&DAT_ViewportRenderState,(short)uVar3 + 2,(short)uVar2 + 2);
    UI::Rendering::AlphaAndButtonSurface::openBuildingStatusMenuForBuildingID
              (&AlphaAndButtonSurfaceObj,iVar7);
    break;
  case VK_P:
                    /* P */
    BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
    if ((((BVar8 != FALSE) && (DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE)) &&
        (DAT_GameCore.gameMode_2 != GM_EDITOR)) &&
       ((DAT_GameCore.gameMode_2 != GM_SIEGE_THAT &&
        (DAT_GameSynchronyState.currentGameMode != GM_MULTIPLAYER)))) {
      DAT_GameCore.gamePausedLogical = DAT_GameCore.gamePausedLogical ^ 1;
      if (DAT_GameCore.gamePausedLogical == 0) {
        if (DAT_GameCore.genieVoiceActive != FALSE) {
                    /* "Game running" */
          Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"game_running.wav");
        }
      }
      else {
        CheckDisplayElementByIDAndSetForUnlimitedDisplay(DEID_GAME_PAUSED_TEXT,1);
        DAT_TileMapState.currentMapperCommand = M_MAPPER_NULL;
        if (DAT_GameCore.genieVoiceActive != FALSE) {
                    /* "Game paused" */
          Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"game_paused.wav");
        }
      }
    }
    break;
  case VK_Q:
                    /* Q */
    if (((DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE) &&
        (DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU)) &&
       ((DAT_GameCore.activeMenuTab.tabType == BASMTT_SIEGETENT_BATTERINGRAM ||
        (DAT_GameCore.activeMenuTab.tabType == BASMTT_SIEGETENT_SHIELD)))) {
      Map::Units::TribesState::queueUnitStance
                (&DAT_TribesState,DAT_TribesState.DAT_CurrentTribeID,0);
    }
    break;
  case VK_S:
                    /* S */
    if ((((lParam & 0x40000000U) == 0) &&
        (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 != FALSE)) &&
       (DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE)) {
      iVar7 = DAT_GameState.mapAndTime.signpostIDs[DAT_00df5538];
      if (iVar7 != 0) {
        Rendering::ViewportRenderState::focusOnCoordinate
                  (&DAT_ViewportRenderState,(short)DAT_BuildingsState.buildings[iVar7].x + 1,
                   (short)DAT_BuildingsState.buildings[iVar7].y + 1);
      }
      DAT_00df5538 = DAT_00df5538 + 1;
      if (7 < DAT_00df5538) {
        DAT_00df5538 = 0;
      }
      iVar9 = 1;
      iVar7 = DAT_GameState.mapAndTime.signpostIDs[DAT_00df5538];
      while (iVar7 == 0) {
        DAT_00df5538 = DAT_00df5538 + 1;
        if (7 < DAT_00df5538) {
          DAT_00df5538 = 0;
        }
        iVar9 = iVar9 + 1;
        if (7 < iVar9) break;
        iVar7 = DAT_GameState.mapAndTime.signpostIDs[DAT_00df5538];
      }
    }
    break;
  case VK_T:
                    /* T */
    if ((((lParam & 0x40000000U) != 0) ||
        (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE)) ||
       (DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE)) break;
    if (DAT_ModifierKeyState.shift != 0) {
      if (DAT_GameCore.field168_0x2364 != -1) {
        Rendering::ViewportRenderState::focusOnTile
                  (&DAT_ViewportRenderState,DAT_GameCore.field168_0x2364);
        if (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU) {
          Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
        }
        DAT_GameCore.field168_0x2364 = -1;
      }
      break;
    }
    if (DAT_ModifierKeyState.ctrl != 0) {
      iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
              tunnelersGuild.id;
      if (iVar7 != 0) {
        UI::Rendering::AlphaAndButtonSurface::openBuildingStatusMenuForBuildingID
                  (&AlphaAndButtonSurfaceObj,iVar7);
      }
      break;
    }
    iVar7 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].tunnelersGuild
            .id;
    if (iVar7 == 0) break;
    DAT_GameCore.field168_0x2364 = Rendering::ViewportBasedTileNumber();
LAB_004b3a17:
    uVar2 = DAT_BuildingsState.buildings[iVar7].y;
    uVar3 = DAT_BuildingsState.buildings[iVar7].x;
    goto LAB_004b3a35;
  case VK_V:
                    /* V */
    BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
    if (((BVar8 != FALSE) && (DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE)) &&
       (DAT_MouseState.rightClickState == FALSE)) {
      Map::TileMapState::triggerLoweredView(&DAT_TileMapState,3);
      DAT_ModifierKeyState.v = 1;
    }
    break;
  case VK_W:
                    /* W */
    if (((DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE) &&
        (DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU)) &&
       ((DAT_GameCore.activeMenuTab.tabType == BASMTT_SIEGETENT_BATTERINGRAM ||
        (DAT_GameCore.activeMenuTab.tabType == BASMTT_SIEGETENT_SHIELD)))) {
      Map::Units::TribesState::queueUnitStance
                (&DAT_TribesState,DAT_TribesState.DAT_CurrentTribeID,1);
    }
    break;
  case VK_X:
                    /* X */
    BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
    if (((BVar8 != FALSE) && (DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE)) &&
       (DAT_MouseState.rightClickState == FALSE)) {
      uVar13 = DAT_TileMapState.mapOrientation + 2U & 0x80000007;
      if ((int)uVar13 < 0) {
        uVar13 = (uVar13 - 1 | 0xfffffff8) + 1;
      }
      Map::TileMapState::setMapRotation(&DAT_TileMapState,uVar13);
    }
    break;
  case VK_Z:
                    /* Z */
    if (((((lParam & 0x40000000U) != 0) ||
         (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE)) ||
        (DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE)) ||
       (DAT_MouseState.rightClickState != FALSE)) break;
    if (DAT_ViewportRenderState.viewportState.isZoomedOutUnk == 0) {
      Rendering::ViewportRenderState::resetupViewport(&DAT_ViewportRenderState,1);
    }
    else {
      Rendering::ViewportRenderState::resetupViewport(&DAT_ViewportRenderState,0);
    }
LAB_004b2cfd:
    DAT_WindowAndDirectDraw.unk_resetViewportRelated = 2;
    DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
    break;
  case VK_NUMPAD0:
  case VK_NUMPAD1:
  case VK_NUMPAD2:
  case VK_NUMPAD3:
  case VK_NUMPAD4:
  case VK_NUMPAD5:
  case VK_NUMPAD6:
  case VK_NUMPAD7:
  case VK_NUMPAD8:
  case VK_NUMPAD9:
                    /* numpad numbers */
    wParam = wParam - VK_ZERO;
switchD_004b2d9a_caseD_30:
                    /* 0-9 */
    if ((((lParam & 0x40000000U) == 0) &&
        (DAT_MenuModalComposition1.activeModalDialogID == MMT_NONE)) &&
       (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore),
       iVar7 = DAT_TribesState.DAT_CurrentTribeID, BVar8 != FALSE)) {
      if (DAT_ModifierKeyState.ctrl == 0) {
        if (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU) {
          if (DAT_GameCore.activeMenuTab.tabType == BASMTT_BARRACKS_OR_MPMENU_MODEM) {
            switch(wParam) {
            case VK_ONE:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed(M_MAPPER_PLACE_ASSEMBLY_POINT1)
              ;
              break;
            case VK_TWO:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed(M_MAPPER_PLACE_ASSEMBLY_POINT3)
              ;
              break;
            case VK_THREE:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed(M_MAPPER_PLACE_ASSEMBLY_POINT4)
              ;
              break;
            case VK_FOUR:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed(M_MAPPER_PLACE_ASSEMBLY_POINT2)
              ;
              break;
            case VK_FIVE:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed(M_MAPPER_PLACE_ASSEMBLY_POINT5)
              ;
              break;
            case VK_SIX:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed(M_MAPPER_PLACE_ASSEMBLY_POINT6)
              ;
              break;
            case VK_SEVEN:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed(M_MAPPER_PLACE_ASSEMBLY_POINT7)
              ;
            }
            break;
          }
          if (DAT_GameCore.activeMenuTab.tabType == BASMTT_MERCENARYPOST) {
            switch(wParam) {
            case VK_ONE:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed
                        (M_MAPPER_PLACE_ASSEMBLY_POINTM1);
              break;
            case VK_TWO:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed
                        (M_MAPPER_PLACE_ASSEMBLY_POINTM3);
              break;
            case VK_THREE:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed
                        (M_MAPPER_PLACE_ASSEMBLY_POINTM5);
              break;
            case VK_FOUR:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed
                        (M_MAPPER_PLACE_ASSEMBLY_POINTM4);
              break;
            case VK_FIVE:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed
                        (M_MAPPER_PLACE_ASSEMBLY_POINTM2);
              break;
            case VK_SIX:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed
                        (M_MAPPER_PLACE_ASSEMBLY_POINTM7);
              break;
            case VK_SEVEN:
              UI::MenuItemActionHandler_General_ToolbarButtonPressed
                        (M_MAPPER_PLACE_ASSEMBLY_POINTM6);
            }
            break;
          }
          if (DAT_GameCore.activeMenuTab.tabType == BASMTT_ENGINEERSGUILD) {
            if (wParam - VK_ONE < 2) {
              UI::MenuItemActionHandler_General_ToolbarButtonPressed(wParam + 0x13e);
            }
            break;
          }
          if (DAT_GameCore.activeMenuTab.tabType == BASMTT_TUNNELERSGUILD) {
            if (wParam == VK_ONE) {
              UI::MenuItemActionHandler_General_ToolbarButtonPressed
                        (M_MAPPER_PLACE_ASSEMBLY_POINTT1);
            }
            break;
          }
          if (DAT_GameCore.activeMenuTab.tabType == BASMTT_CATHEDRAL) {
            if (wParam == VK_ONE) {
              UI::MenuItemActionHandler_General_ToolbarButtonPressed
                        (M_MAPPER_PLACE_ASSEMBLY_POINTK1);
            }
            break;
          }
        }
        iVar7 = wParam - VK_ZERO;
        BVar8 = Map::Units::UnitsState::isUnitShortcutAvailable(&DAT_UnitsState,iVar7);
        if (BVar8 == FALSE) {
          Map::Units::UnitsState::queueStopCommand(&DAT_UnitsState);
          Map::Units::UnitsState::makeSelectionBasedOnShortcut(&DAT_UnitsState,iVar7);
          if (0 < DAT_UnitsState.totalUnitsInSelection) {
            if (DAT_GameCore.buildmenuMenuTabToSwitchTo.tabType != BASMTT_SIEGETENT_BATTERINGRAM) {
              DAT_GameCore.tabTypeSiegeSubset = DAT_GameCore.buildmenuMenuTabToSwitchTo.buildMenuTab
              ;
            }
            DAT_GameCore.buildmenuMenuTabToSwitchTo.tabType = BASMTT_SIEGETENT_BATTERINGRAM;
            Game::GameCore::switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
            DAT_TileMapState.shiftRelated0or3 = 1;
            DAT_UnitsState.field5_0x14 = TRUE;
            DAT_UnitsState.unitControlsRelated = 1;
            DAT_UnitsState.hasEngineerSelected = FALSE;
            DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
          }
        }
        else {
          iVar9 = *(int *)((int)&DAT_GameState + iVar7 * 20000);
          iVar14 = 0;
          if (iVar9 == -1) {
            piVar16 = (int *)((int)&DAT_GameState + iVar7 * 20000);
            do {
              iVar14 = iVar14 + 1;
              piVar16 = piVar16 + 2;
              if (0x9c3 < iVar14) break;
              iVar9 = *piVar16;
            } while (iVar9 == -1);
          }
          if (0 < iVar9) {
            Rendering::ViewportRenderState::focusOnCoordinate
                      (&DAT_ViewportRenderState,(int)DAT_UnitsState.units[iVar9].x,
                       (int)DAT_UnitsState.units[iVar9].y);
          }
        }
      }
      else if (DAT_ModifierKeyState.alt == 0) {
        if (((DAT_TribesState.DAT_CurrentTribeID != 0) && (DAT_TileMapState.shiftRelated0or3 == 1))
           && (DAT_TribesState.DAT_CurrentTribeID != 0)) {
          Game::GameStateStructures::clearTribeHotKey(&DAT_GameState,wParam - VK_ZERO);
          Game::GameStateStructures::assignSelectionToKey(&DAT_GameState,wParam - VK_ZERO,iVar7);
        }
      }
      else {
LAB_004b4af5:
                    /* basically we pressed a number on the keypad or above the letters */
        if (DAT_ModifierKeyState.ctrl == 0) {
          tile = DAT_GameState.playerDataArray[8].engineersAssemblyPoints
                 [wParam - VK_EXTRA_MOUSE_BUTTON2];
          if (-1 < (int)tile) {
            Rendering::ViewportRenderState::focusOnTile(&DAT_ViewportRenderState,(int)tile);
          }
        }
        else {
          iVar7 = 8;
          if (DAT_TileMapState.mapOrientation != 0) {
            if (DAT_TileMapState.mapOrientation == 6) {
              iVar7 = 0x13a18;
            }
            else if (DAT_TileMapState.mapOrientation == 4) {
              iVar7 = 0x27428;
            }
            else if (DAT_TileMapState.mapOrientation == 2) {
              iVar7 = 0x3ae38;
            }
          }
          DAT_GameState.playerDataArray[8].engineersAssemblyPoints[wParam - VK_EXTRA_MOUSE_BUTTON2]
               = *(XYPairShort *)
                  (DAT_ViewportRenderState.screenPointToTileNumber +
                  ((int)(DAT_ViewportRenderState.viewportState.viewportX +
                        (DAT_ViewportRenderState.viewportState.viewportX >> 0x1f & 0x1fU)) >> 5) +
                  ((int)DAT_ViewportRenderState.viewportState.mbr_0xb0 / 2 +
                  ((int)(DAT_ViewportRenderState.viewportState.viewportY +
                        (DAT_ViewportRenderState.viewportState.viewportY >> 0x1f & 0xfU)) >> 4)) *
                  0x191 + DAT_ViewportRenderState.viewportState.mbr_0xac + iVar7 + -8);
        }
      }
    }
    break;
  case VK_ADD:
                    /* VK_ADD */
    if ((((lParam & 0x40000000U) != 0) ||
        (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE)) ||
       (((DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE ||
         ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY &&
          (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER)))) ||
        (0x59 < (int)DAT_GameCore.gameSpeedLevel)))) break;
    DAT_GameCore.gameSpeedLevel = DAT_GameCore.gameSpeedLevel + 5;
    if (0x5a < (int)DAT_GameCore.gameSpeedLevel) {
      DAT_GameCore.gameSpeedLevel = 0x5a;
    }
    goto LAB_004b4768;
  case VK_SUBTRACT:
                    /* VK_SUBTRACT */
    if ((((lParam & 0x40000000U) != 0) ||
        (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 == FALSE)) ||
       ((DAT_MenuModalComposition1.activeModalDialogID != MMT_NONE ||
        (((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY &&
          (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER)) ||
         ((int)DAT_GameCore.gameSpeedLevel < 0xb)))))) break;
    DAT_GameCore.gameSpeedLevel = DAT_GameCore.gameSpeedLevel - 5;
    if ((int)DAT_GameCore.gameSpeedLevel < 0x14) {
      DAT_GameCore.gameSpeedLevel = 0x14;
    }
LAB_004b4768:
    ActivateGameSpeedAndResourceLackDisplayElementUnk(DEID_GAME_SPEED_TEXT,1,5000);
    break;
  case VK_F1:
                    /* VK_F1 */
    if (DAT_ModifierKeyState.shift != 0) {
      if (((((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) ||
            (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
             playerDeathRelated == 0)) && (DAT_GameCore.gameMode_2 != GM_EDITOR)) &&
          (((((DAT_GameCore.gameMode_2 != GM_SIEGE_THAT &&
              (DAT_MenuTextInputState.currentModalDialog == MMT_NO_MENU)) &&
             ((DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU ||
              (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU)))) &&
            ((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY ||
             (DAT_GameSynchronyState.isHost != FALSE)))) && (DAT_GameCore.field27_0x6c == 0)))) &&
         (DAT_GameCore.gameMode_2 != GM_CRUSADER_TUTORIAL)) {
        UI::MenuTextInputState::loadOrSaveGame(&DAT_MenuTextInputState,10);
      }
      break;
    }
  case VK_F3:
  case VK_F4:
  case VK_F5:
  case VK_F6:
  case VK_F7:
  case VK_F8:
  case VK_F9:
  case VK_F10:
switchD_004b2d9a_caseD_72:
                    /* F1-F10 without F2 */
    DAT_ModifierKeyState.keyDownUnk = 1;
    if ((DAT_GameCore.gameMode_2 == GM_SKIRMISH_AND_MULTIPLAYER) &&
       (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 != FALSE)) {
      DAT_GameSynchronyState.DAT_ChatMessageReceiverArray[1] = 1;
      DAT_GameSynchronyState.DAT_ChatMessageReceiverArray[2] = 1;
      DAT_GameSynchronyState.DAT_ChatMessageReceiverArray[3] = 1;
      DAT_GameSynchronyState.DAT_ChatMessageReceiverArray[4] = 1;
      DAT_GameSynchronyState.DAT_ChatMessageReceiverArray[5] = 1;
      DAT_GameSynchronyState.DAT_ChatMessageReceiverArray[6] = 1;
      DAT_GameSynchronyState.DAT_ChatMessageReceiverArray[7] = 1;
      DAT_GameSynchronyState.DAT_ChatMessageReceiverArray[8] = 1;
      if (DAT_ModifierKeyState.ctrl != 0) {
        wParam = wParam + (VK_BACKSPACE|VK_RIGHT_MOUSE_BUTTON);
      }
      DAT_GameSynchronyState.DAT_ChatTauntOrMessage = wParam - VK_DIVIDE;
      Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_TAUNT_OR_CHAT);
      if ((DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_SINGLE_PLAYER) &&
         (DAT_GameSynchronyState.DAT_ChatTauntOrMessage != 6)) {
        AI::AICState::setTriggerForAITauntResponse(&DAT_AICState);
      }
    }
    else if (((wParam < VK_F2) &&
             (((DAT_GameCore.gameMode_2 == GM_BUILDERUnk &&
               (DAT_MapPropertiesState.SEC_U3_MapType2_1 == MT_JUST_BUILD)) &&
              (BVar8 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore), BVar8 != FALSE)))) &&
            (DAT_ModifierKeyState.shift == 0)) {
      Map::MapPropertiesState::openEventTriggerMenu(&DAT_MapPropertiesState,wParam - VK_F1);
      break;
    }
switchD_004b482b_caseD_7a:
                    /* F11 or F12 */
    wParam = VK_SPACE;
    break;
  case VK_F2:
                    /* VK_F2 */
    if (DAT_ModifierKeyState.shift != 0) {
      if ((((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) ||
           (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
            playerDeathRelated == 0)) &&
          ((DAT_GameCore.gameMode_2 != GM_EDITOR &&
           ((DAT_GameCore.gameMode_2 != GM_SIEGE_THAT &&
            (DAT_MenuTextInputState.currentModalDialog == MMT_NO_MENU)))))) &&
         ((DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU ||
          (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU)))) {
        if (DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) {
          if ((DAT_GameCore.field27_0x6c == 0) && (DAT_GameCore.gameMode_2 != GM_CRUSADER_TUTORIAL))
          {
            UI::MenuTextInputState::loadOrSaveGame(&DAT_MenuTextInputState,9);
          }
        }
        else if (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_SINGLE_PLAYER) {
          UI::MenuTextInputState::loadOrSaveGame(&DAT_MenuTextInputState,9);
        }
      }
      break;
    }
    goto switchD_004b2d9a_caseD_72;
  }
switchD_004b4d0c_doDefWindowProcA:
  DefWindowProcA(_hwnd,message,wParam,lParam);
  LVar11 = HoldStrong_lib::__security_check_cookie(uVar6 ^ (uint)&_hwnd);
  return LVar11;
}



