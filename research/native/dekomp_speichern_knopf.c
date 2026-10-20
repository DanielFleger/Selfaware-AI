// ================= MenuItemActionHandler_SaveLoadMap_Buttons @ 0x004943b0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl _HoldStrong::UI::MenuItemActionHandler_SaveLoadMap_Buttons(int param_1,...)

{
  int iVar1;
  char *pcVar2;
  BOOLEnum BVar3;
  undefined4 uVar4;
  char cVar5;
  char *pcVar6;
  char *pcVar7;
  char *pcVar8;
  FileResourceType FVar9;
  MenuModalType dialogID;
  char local_3f4 [4];
  char local_3f0 [1004];
  uint local_4;
  
  pcVar6 = local_3f4;
  pcVar2 = local_3f4;
  pcVar7 = local_3f4;
  pcVar8 = local_3f4;
  local_4 = MSVC_SecurityCookie ^ (uint)local_3f4;
  switch(param_1) {
  case 2:
                    /* "Load" */
    if (DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionIndex == -1) goto LAB_0049461b;
    if (((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
        (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER)) &&
       (DAT_MenuTextInputState.DAT_ArrayOfMapIndices
        [DAT_MenuTextInputState.DAT_ArrayOfMapIndices
         [DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionIndex +
          DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionOffset + -1] + 499] == 0)) break;
    iVar1 = DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionIndex +
            DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionOffset;
    pcVar2 = (char *)IO::ResourceManager::getLoadedMapNameForIndex
                               (DAT_MenuTextInputState.DAT_ArrayOfMapIndices[iVar1 + -1]);
    pcVar6 = local_3f4;
    do {
      cVar5 = *pcVar2;
      *pcVar6 = cVar5;
      pcVar2 = pcVar2 + 1;
      pcVar6 = pcVar6 + 1;
    } while (cVar5 != '\0');
    if (DAT_GameCore.currentMenuViewType == MVT_UNUSED_CREATE_SIEGE) {
      pcVar6 = &stack0xfffffc0b;
      do {
        pcVar2 = pcVar6 + 1;
        pcVar6 = pcVar6 + 1;
        uVar4 = s__tmp_005a75a8._0_4_;
        cVar5 = s__tmp_005a75a8[4];
      } while (*pcVar2 != '\0');
LAB_00494566:
      *(undefined4 *)pcVar6 = uVar4;
      pcVar6[4] = cVar5;
      FVar9 = FRT_MAPS;
    }
    else {
      if (DAT_GameCore.currentMenuViewType == MVT_CUSTOM_SCENARIOS) {
        pcVar6 = &stack0xfffffc0b;
        do {
          pcVar2 = pcVar6 + 1;
          pcVar6 = pcVar6 + 1;
          uVar4 = s__map_005a2294._0_4_;
          cVar5 = s__map_005a2294[4];
        } while (*pcVar2 != '\0');
        goto LAB_00494566;
      }
      if ((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
         (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_SINGLE_PLAYER)) {
        pcVar6 = &stack0xfffffc0b;
        do {
          pcVar2 = pcVar6;
          pcVar6 = pcVar2 + 1;
        } while (pcVar2[1] != '\0');
        *(undefined4 *)(pcVar2 + 1) = s__sav_005a75a0._0_4_;
        pcVar2[5] = s__sav_005a75a0[4];
        FVar9 = FRT_UNKNOWN;
      }
      else {
        pcVar6 = &stack0xfffffc0b;
        do {
          pcVar2 = pcVar6;
          pcVar6 = pcVar2 + 1;
        } while (pcVar2[1] != '\0');
        *(undefined4 *)(pcVar2 + 1) = s__msv_005a7498._0_4_;
        pcVar2[5] = s__msv_005a7498[4];
        FVar9 = FRT_UNKNOWN;
      }
    }
    IO::ResourceManager::resolveResourceFileName(&DAT_ResourceManager,FVar9,local_3f4);
    BVar3 = IO::ResourceManager::doesFileOfActiveResourceExist(&DAT_ResourceManager);
    if (BVar3 != FALSE) {
      if ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
         (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER)) {
        MenuTextInputState::clearAnyOtherModalDialogs(&DAT_MenuTextInputState);
        pcVar6 = (char *)IO::ResourceManager::getLoadedMapNameForIndex
                                   (DAT_MenuTextInputState.DAT_ArrayOfMapIndices[iVar1 + -1]);
        pcVar2 = DAT_GameSynchronyState.shortMapName;
        do {
          cVar5 = *pcVar6;
          *pcVar2 = cVar5;
          pcVar6 = pcVar6 + 1;
          pcVar2 = pcVar2 + 1;
        } while (cVar5 != '\0');
        Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,0x28);
        Input::MouseState::resetMouseState2(&DAT_MouseState);
        HoldStrong_lib::__security_check_cookie(local_4 ^ (uint)local_3f4);
        return;
      }
      DAT_MenuTextInputState.DAT_MenuOptionsActionParameter = 0x1f;
      MenuTextInputState::activateModalDialogAndClearText
                (&DAT_MenuTextInputState,MMT_PROGRESS_BAR_BOX);
      DAT_GameCore.field122_0x1d98 = 1;
    }
LAB_0049461b:
    Input::MouseState::resetMouseState2(&DAT_MouseState);
    HoldStrong_lib::__security_check_cookie(local_4 ^ (uint)local_3f4);
    return;
  case 3:
    if (DAT_UserTextHandlerState.textContentLengthArray[DAT_UserTextHandlerState.textArrayIndex] ==
        0) goto LAB_00494849;
    if (DAT_MenuTextInputState.field49_0xac == 0) {
      if (DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_PROPERTIES) {
        pcVar6 = Text::UserTextHandler::getCurrentText(&DAT_UserTextHandlerState);
        do {
          cVar5 = *pcVar6;
          *pcVar8 = cVar5;
          pcVar6 = pcVar6 + 1;
          pcVar8 = pcVar8 + 1;
        } while (cVar5 != '\0');
        pcVar6 = &stack0xfffffc0b;
        do {
          pcVar2 = pcVar6 + 1;
          pcVar6 = pcVar6 + 1;
          uVar4 = s__map_005a2294._0_4_;
          cVar5 = s__map_005a2294[4];
        } while (*pcVar2 != '\0');
        goto LAB_0049477a;
      }
      if ((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
         (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_SINGLE_PLAYER)) {
        pcVar6 = Text::UserTextHandler::getCurrentText(&DAT_UserTextHandlerState);
        do {
          cVar5 = *pcVar6;
          *pcVar7 = cVar5;
          pcVar6 = pcVar6 + 1;
          pcVar7 = pcVar7 + 1;
        } while (cVar5 != '\0');
        pcVar6 = &stack0xfffffc0b;
        do {
          pcVar2 = pcVar6;
          pcVar6 = pcVar2 + 1;
        } while (pcVar2[1] != '\0');
        *(undefined4 *)(pcVar2 + 1) = s__sav_005a75a0._0_4_;
        pcVar2[5] = s__sav_005a75a0[4];
        FVar9 = FRT_UNKNOWN;
      }
      else {
        pcVar6 = Text::UserTextHandler::getCurrentText(&DAT_UserTextHandlerState);
        do {
          cVar5 = *pcVar6;
          *pcVar2 = cVar5;
          pcVar6 = pcVar6 + 1;
          pcVar2 = pcVar2 + 1;
        } while (cVar5 != '\0');
        pcVar6 = &stack0xfffffc0b;
        do {
          pcVar2 = pcVar6;
          pcVar6 = pcVar2 + 1;
        } while (pcVar2[1] != '\0');
        *(undefined4 *)(pcVar2 + 1) = s__msv_005a7498._0_4_;
        pcVar2[5] = s__msv_005a7498[4];
        FVar9 = FRT_UNKNOWN;
      }
    }
    else {
      pcVar2 = Text::UserTextHandler::getCurrentText(&DAT_UserTextHandlerState);
      do {
        cVar5 = *pcVar2;
        *pcVar6 = cVar5;
        pcVar2 = pcVar2 + 1;
        pcVar6 = pcVar6 + 1;
      } while (cVar5 != '\0');
      pcVar6 = &stack0xfffffc0b;
      do {
        pcVar2 = pcVar6 + 1;
        pcVar6 = pcVar6 + 1;
        uVar4 = s__tmp_005a75a8._0_4_;
        cVar5 = s__tmp_005a75a8[4];
      } while (*pcVar2 != '\0');
LAB_0049477a:
      *(undefined4 *)pcVar6 = uVar4;
      pcVar6[4] = cVar5;
      FVar9 = FRT_MAPS;
    }
    IO::ResourceManager::resolveResourceFileName(&DAT_ResourceManager,FVar9,local_3f4);
    BVar3 = IO::ResourceManager::doesFileOfActiveResourceExist(&DAT_ResourceManager);
    if (BVar3 == FALSE) {
      if ((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
         (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_SINGLE_PLAYER)) {
        DAT_MenuTextInputState.DAT_MenuOptionsActionParameter = 0x20;
        dialogID = MMT_PROGRESS_BAR_BOX;
        goto LAB_0049481f;
      }
      pcVar6 = Text::UserTextHandler::getCurrentText(&DAT_UserTextHandlerState);
      pcVar2 = DAT_GameSynchronyState.shortMapName;
      do {
        cVar5 = *pcVar6;
        *pcVar2 = cVar5;
        pcVar6 = pcVar6 + 1;
        pcVar2 = pcVar2 + 1;
      } while (cVar5 != '\0');
      MenuTextInputState::clearAnyOtherModalDialogs(&DAT_MenuTextInputState);
      DAT_GameSynchronyState.DAT_GameCommandParam0 = DAT_GameCore.mapTimeInTicks;
      DAT_GameSynchronyState.DAT_GameCommandParam1 = Global::ComputeSomeHashOnUnitArray();
      DAT_GameSynchronyState.DAT_GameCommandParam2 = 0;
      Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SAVE);
    }
    else {
      DAT_MenuTextInputState.DAT_MenuOptionsActionParameter = 0x1e;
      dialogID = MMT_YES_NO_DIALOG;
LAB_0049481f:
      MenuTextInputState::activateModalDialogAndClearText(&DAT_MenuTextInputState,dialogID);
    }
    DAT_UserTextHandlerState.allowUserTextInput = 0;
    Text::UserTextHandler::resetToTextIndex(&DAT_UserTextHandlerState,9);
    DAT_UserTextHandlerState.allowUserTextInput = 1;
LAB_00494849:
    Input::MouseState::resetMouseState2(&DAT_MouseState);
    HoldStrong_lib::__security_check_cookie(local_4 ^ (uint)local_3f4);
    return;
  case 0x11:
                    /* "Back" */
    MenuTextInputState::popModalDialog(&DAT_MenuTextInputState);
    DAT_MenuTextInputState._168_4_ = 0xffffffff;
    break;
  case -2:
    if (DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionOffset <
        DAT_MenuTextInputState.field32_0x74 - DAT_MenuTextInputState.field36_0x84) {
      DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionOffset =
           DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionOffset + 1;
      HoldStrong_lib::__security_check_cookie(local_4 ^ (uint)local_3f4);
      return;
    }
    break;
  case -1:
    if (0 < DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionOffset) {
      DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionOffset =
           DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionOffset + -1;
      HoldStrong_lib::__security_check_cookie(local_4 ^ (uint)local_3f4);
      return;
    }
  }
  HoldStrong_lib::__security_check_cookie(local_4 ^ (uint)local_3f4);
  return;
}



// ================= MenuItemActionHandler_SaveMap_ReturnKeySave @ 0x00494920 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl _HoldStrong::UI::MenuItemActionHandler_SaveMap_ReturnKeySave(int param_1,...)

{
  bool bVar1;
  
  bVar1 = DAT_UserTextHandlerState.returnPressed != 0;
  DAT_UserTextHandlerState.returnPressed = 0;
  if (bVar1) {
    MenuItemActionHandler_SaveLoadMap_Buttons(3);
    return;
  }
  return;
}



