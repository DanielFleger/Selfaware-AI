// ================= AutoSaveTriggered @ 0x00489880 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Commands::AutoSaveTriggered(void)

{
  WCHAR WVar1;
  int iVar2;
  WCHAR *pWVar3;
  undefined1 auStack_5c [3];
  char local_59;
  Base64State _base64State;
  WCHAR local_4c;
  undefined1 local_4a [70];
  uint local_4;
  
  local_4 = MSVC_SecurityCookie ^ (uint)auStack_5c;
  DAT_GameSynchronyState.DAT_CommandSize = 0x4b;
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_SCHEDULE_AND_SEND) {
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,4,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam1,4,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam2,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Util::WideCharMultiByteState::multiByteToWideCharThunk
              (&DAT_WideCharMultiByteState,&local_4c,DAT_GameSynchronyState.shortMapName,0x21);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&local_4c,0x42,GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,
               GCPRW_SERIALIZE_INTO_PARAM_1);
    iVar2 = 1;
    do {
      if ((DAT_GameSynchronyState.currentPlayerFullIDArray[iVar2] == -1) ||
         (iVar2 == DAT_GameSynchronyState.currentPlayerSlotID)) {
        DAT_GameSynchronyState.announcementReceivedByPlayer[iVar2] = 1;
      }
      else {
        DAT_GameSynchronyState.announcementReceivedByPlayer[iVar2] = 0;
      }
      iVar2 = iVar2 + 1;
    } while (iVar2 < 9);
    HoldStrong_lib::__security_check_cookie(local_4 ^ (uint)auStack_5c);
    return;
  }
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_EXECUTE) {
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,4,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam1,4,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&local_59,1,GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,
               GCPRW_DESERIALIZE_FROM_PARAM1);
    DAT_GameSynchronyState.DAT_GameCommandParam2 = (int)local_59;
    if (DAT_GameSynchronyState.isHost == FALSE) {
      Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
                (&DAT_GameSynchronyState,&local_4c,0x42,GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,
                 GCPRW_DESERIALIZE_FROM_PARAM1);
      IO::Base64EncodeInit(&_base64State);
      IO::LowLevelMemory::fillMemory_IntegerValue
                (&DAT_LowLevelMemory,0x78,0,DAT_GameSynchronyState.shortMapName);
      pWVar3 = &local_4c;
      do {
        WVar1 = *pWVar3;
        pWVar3 = pWVar3 + 1;
      } while (WVar1 != L'\0');
      IO::Base64Encode((byte *)&local_4c,((int)pWVar3 - (int)local_4a >> 1) * 2,
                       DAT_GameSynchronyState.shortMapName,&_base64State);
    }
    else {
      Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
                (&DAT_GameSynchronyState,&local_4c,0x42,GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,
                 GCPRW_DESERIALIZE_FROM_PARAM1);
      Util::WideCharMultiByteState::wideCharToMultiByteWithSize
                (&DAT_WideCharMultiByteState,DAT_GameSynchronyState.shortMapName,&local_4c,1000);
    }
    DAT_GameSynchronyState.savedMapTimeInTicks = DAT_GameSynchronyState.DAT_GameCommandParam0;
    DAT_GameSynchronyState.savedUnitsCRC32Hash = DAT_GameSynchronyState.DAT_GameCommandParam1;
    UI::ShowProgressBarSaveLoadDialog(DAT_GameSynchronyState.DAT_GameCommandParam2);
    DAT_GameSynchronyState.field75_0xbe4 = timeGetTime();
    DAT_GameSynchronyState.saveRelated = 1;
    if (DAT_GameSynchronyState.isHost == FALSE) {
      DAT_GameSynchronyState.shouldSendAnnouncementUnk = 1;
      HoldStrong_lib::__security_check_cookie(local_4 ^ (uint)auStack_5c);
      return;
    }
    DAT_GameSynchronyState.announcementReceiveTime = timeGetTime();
    DAT_GameSynchronyState.announcementReceivedBool = FALSE;
  }
  HoldStrong_lib::__security_check_cookie(local_4 ^ (uint)auStack_5c);
  return;
}



// ================= queueSynchronizedAutosaveProtocol @ 0x0048c660 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Synchrony::GameSynchronyState::queueSynchronizedAutosaveProtocol
          (GameSynchronyState *this)

{
  BOOLEnum BVar1;
  DWORD DVar2;
  
  if ((((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
       (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER)) &&
      (DAT_GameSynchronyState.isHost != FALSE)) &&
     ((DAT_GameSynchronyState.skirmishAutoSaveEveryMinutes != 0 &&
      (DAT_GameSynchronyState.DAT_TimeRelated1 != 0)))) {
    BVar1 = Game::GameCore::getAreWeInAInGameMenu(&DAT_GameCore);
    if ((BVar1 != FALSE) &&
       ((DAT_GameSynchronyState.syncStatus == 0 && (DAT_GameSynchronyState.saveRelated == 0)))) {
      DVar2 = timeGetTime();
      if (DAT_GameSynchronyState.skirmishAutoSaveEveryMinutes * 60000 <
          (int)(DVar2 - DAT_GameSynchronyState.DAT_TimeRelated1)) {
                    /* autosave */
        DAT_GameSynchronyState.shortMapName[0] = s_autosave_005a74b4[0];
        DAT_GameSynchronyState.shortMapName[1] = s_autosave_005a74b4[1];
        DAT_GameSynchronyState.shortMapName[2] = s_autosave_005a74b4[2];
        DAT_GameSynchronyState.shortMapName[3] = s_autosave_005a74b4[3];
        DAT_GameSynchronyState.shortMapName[4] = s_autosave_005a74b4[4];
        DAT_GameSynchronyState.shortMapName[5] = s_autosave_005a74b4[5];
        DAT_GameSynchronyState.shortMapName[6] = s_autosave_005a74b4[6];
        DAT_GameSynchronyState.shortMapName[7] = s_autosave_005a74b4[7];
        DAT_GameSynchronyState.shortMapName[8] = s_autosave_005a74b4[8];
        DAT_GameSynchronyState.DAT_GameCommandParam0 = DAT_GameCore.mapTimeInTicks;
        DAT_GameSynchronyState.field75_0xbe4 = DVar2;
        DAT_GameSynchronyState.DAT_TimeRelated1 = DVar2;
        DAT_GameSynchronyState.DAT_GameCommandParam1 = Global::ComputeSomeHashOnUnitArray();
        DAT_GameSynchronyState.DAT_GameCommandParam2 = 1;
        queueCommand(&DAT_GameSynchronyState,GCT_SAVE);
      }
    }
  }
  return;
}



// ================= loadOrSaveGame @ 0x004968a0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::UI::MenuTextInputState::loadOrSaveGame(MenuTextInputState *this,int action)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int *piVar4;
  undefined4 *puVar5;
  int iVar6;
  StringObject local_48;
  StringObject local_2c;
  uint _cookie_1;
  void *local_c;
  code *pcStack_8;
  undefined4 local_4;
  
  local_4 = 0xffffffff;
  pcStack_8 = HoldStrong_lib::EH_FUN_0059a000;
  local_c = ExceptionList;
  _cookie_1 = MSVC_SecurityCookie ^ (uint)&local_48;
  ExceptionList = &local_c;
  if ((((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
       (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_SINGLE_PLAYER)) ||
      (DAT_GameSynchronyState.saveRelated != 1)) || (action != 10)) {
    DAT_MouseState.waitCursorToggle = 1;
    Global::SetCursorDependingOnProgramState();
    OS::_memset(DAT_MinimapViewState.loadedMiniMap,0,80000);
    INT_00b95b64 = 1;
    if ((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
       (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_SINGLE_PLAYER)) {
      IO::ResourceManager::getSavesPath(&DAT_ResourceManager,&local_48,'\x01');
      local_4 = 1;
      HoldStrong_lib::StringObject::append(&local_48,"*.sav",5);
      uVar3 = local_48.data.pCharArray;
      if (local_48.dataLength < 0x10) {
        uVar3 = &local_48.data;
      }
      IO::ResourceManager::discoverMapFiles(&DAT_ResourceManager,(char *)uVar3);
      DAT_MenuTextInputState.field32_0x74 = DAT_ResourceManager.mapFileCounter;
      iVar6 = 0;
      if (0 < (int)DAT_ResourceManager.mapFileCounter) {
        piVar4 = &DAT_MenuTextInputState.DAT_MapSelectionPreloadMapIndexMapping;
        do {
          *piVar4 = iVar6;
          iVar6 = iVar6 + 1;
          piVar4 = piVar4 + 1;
        } while (iVar6 < (int)DAT_ResourceManager.mapFileCounter);
      }
      local_4 = 0xffffffff;
      if (0xf < local_48.dataLength) {
        OS::_free(local_48.data.pCharArray);
      }
      local_48.dataLength = 0xf;
      local_48.mbr_0x14 = 0;
      local_48.data.pCharArray = local_48.data.pCharArray & 0xffffff00;
    }
    else {
      IO::ResourceManager::getSavesPath(&DAT_ResourceManager,&local_2c,'\x01');
      local_4 = 0;
      HoldStrong_lib::StringObject::append(&local_2c,"*.msv",5);
      uVar3 = local_2c.data.pCharArray;
      if (local_2c.dataLength < 0x10) {
        uVar3 = &local_2c.data;
      }
      IO::ResourceManager::discoverMapFiles(&DAT_ResourceManager,(char *)uVar3);
      DAT_MenuTextInputState.field32_0x74 = DAT_ResourceManager.mapFileCounter;
      iVar6 = 0;
      if (0 < (int)DAT_ResourceManager.mapFileCounter) {
        puVar5 = DAT_MenuTextInputState.DAT_ArrayOfMapIndices + 499;
        do {
          puVar5[-500] = iVar6;
          *puVar5 = 1;
          if (action != 10) {
            DAT_GameSynchronyState.DAT_GameCommandParam0 = iVar6;
            Synchrony::GameSynchronyState::queueCommand
                      (&DAT_GameSynchronyState,
                       GCT_LOAD_MAP_HEADER|GCT_MULTIPLAYER_INITIATE_ANNOUNCE_HOST);
          }
          iVar6 = iVar6 + 1;
          puVar5 = puVar5 + 1;
        } while (iVar6 < (int)DAT_ResourceManager.mapFileCounter);
      }
      local_4 = 0xffffffff;
      if (0xf < local_2c.dataLength) {
        OS::_free(local_2c.data.pCharArray);
      }
    }
    DAT_MouseState.waitCursorToggle = 0;
    DAT_MenuTextInputState.field33_0x78 = 0;
    DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionOffset = 0;
    if (DAT_MenuTextInputState.field32_0x74 == 0) {
      DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionIndex = -1;
    }
    else {
      DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionIndex = 0;
    }
    DAT_MenuTextInputState.field39_0x90 = 0;
    DAT_MenuTextInputState.field38_0x8c = 0xffffffff;
    DAT_MenuTextInputState.field49_0xac = 0;
    DAT_MenuTextInputState.field43_0xa0 = 0xffffffff;
    DAT_MenuTextInputState.field36_0x84 = 0x10;
    if (action == 9) {
      activateModalDialogAndClearText(&DAT_MenuTextInputState,MMT_LOAD_MAP);
      DAT_MenuTextInputState.field0_0x0 = 1;
      iVar6 = DAT_MenuTextInputState.field1_0x4;
      iVar1 = DAT_MenuTextInputState.field2_0x8;
      iVar2 = DAT_MenuTextInputState.field3_0xc;
    }
    else {
      activateModalDialogAndClearText(&DAT_MenuTextInputState,MMT_SAVE_MAP);
      DAT_UserTextHandlerState.allowUserTextInput = 0;
      Text::UserTextHandler::resetToTextIndex(&DAT_UserTextHandlerState,2);
      Text::UserTextHandler::moveCursorToEnd(&DAT_UserTextHandlerState);
      DAT_UserTextHandlerState.allowUserTextInput = 1;
      DAT_MenuTextInputState.field0_0x0 = 3;
      iVar6 = DAT_MenuTextInputState.field4_0x10;
      iVar1 = DAT_MenuTextInputState.field5_0x14;
      iVar2 = DAT_MenuTextInputState.field6_0x18;
    }
    if ((DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionIndex != -1) &&
       (DAT_MenuTextInputState.field33_0x78 = iVar2,
       DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionIndex = iVar1,
       DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionOffset = iVar6,
       (int)DAT_MenuTextInputState.field32_0x74 <= iVar6 + iVar1)) {
      DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionIndex = 0;
      DAT_MenuTextInputState.DAT_MenuLoadGameRelativeSelectionOffset = 0;
    }
    MenuItemActionHandler_SaveLoadMap_TableHeader(-1 - DAT_MenuTextInputState.field33_0x78);
  }
  else {
    clearAnyOtherModalDialogs(&DAT_MenuTextInputState);
  }
  ExceptionList = local_c;
  HoldStrong_lib::__security_check_cookie(_cookie_1 ^ (uint)&local_48);
  return;
}



// ================= getSavesPath @ 0x004779f0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::IO::ResourceManager::getSavesPath
          (ResourceManager *this,StringObject *param_1,char param_2)

{
  undefined4 optimizedParam_2;
  StringObject *otherString;
  undefined4 local_4c;
  StringObject local_48;
  StringObject local_2c;
  uint _someSecurityValueUnk;
  void *_offsetSecurityValueUnk;
  code *_someExceptionFuncPtrUnk;
  int _someStackSecurityValueUnk;
  
  _someStackSecurityValueUnk = -1;
  _someExceptionFuncPtrUnk = HoldStrong_lib::ResourceStringLoadCxxFrameHandlerUnk;
  _offsetSecurityValueUnk = ExceptionList;
  _someSecurityValueUnk = MSVC_SecurityCookie ^ (uint)&local_4c;
  ExceptionList = &_offsetSecurityValueUnk;
  local_4c = 0;
  getDocumentsFolderString(&DAT_ResourceManager,&local_2c,'\0');
  _someStackSecurityValueUnk = 0;
  HoldStrong_lib::StringObject::append(&local_2c,"Saves\\",6);
  local_48.dataLength = 0xf;
  local_48.mbr_0x14 = 0;
  local_48.data.pCharArray = local_48.data.pCharArray & 0xffffff00;
  _someStackSecurityValueUnk = CONCAT31(_someStackSecurityValueUnk._1_3_,1);
  optimizedParam_2 = local_2c.data.pCharArray;
  if (local_2c.dataLength < 0x10) {
    optimizedParam_2 = &local_2c.data;
  }
  HoldStrong_lib::StringObject::string_prependUserPathToString(&local_48,(char *)optimizedParam_2,5)
  ;
  param_1->mbr_0x14 = 0;
  param_1->dataLength = 0xf;
  (param_1->data).charArray[0] = '\0';
  otherString = &local_48;
  if (param_2 == '\0') {
    otherString = &local_2c;
  }
  HoldStrong_lib::StringObject::someStringCopyOperation(param_1,otherString,0,(dword *)0xffffffff);
  if (0xf < local_48.dataLength) {
    OS::_free(local_48.data.pCharArray);
  }
  local_48.data.pCharArray = local_48.data.pCharArray & 0xffffff00;
  local_48.mbr_0x14 = 0;
  local_48.dataLength = 0xf;
  if (0xf < local_2c.dataLength) {
    OS::_free(local_2c.data.pCharArray);
  }
  ExceptionList = _offsetSecurityValueUnk;
  HoldStrong_lib::__security_check_cookie(_someSecurityValueUnk ^ (uint)&local_4c);
  return;
}



