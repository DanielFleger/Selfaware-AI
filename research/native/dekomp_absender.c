// ================= _HoldStrong::Synchrony::GameSynchronyState::translateMultiplayerIDsIntoPlayerIDs @ 0047eaf0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* in multiplayer, player IDS are unique numbers of some sort
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

uint _HoldStrong::Synchrony::GameSynchronyState::translateMultiplayerIDsIntoPlayerIDs(int param_1)

{
  uint uVar1;
  
  if ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
     (DAT_GameSynchronyState.currentGameMode != GM_SKIRMISH_SINGLE_PLAYER)) {
                    /* if in multiplayer */
    uVar1 = (uint)(DAT_GameSynchronyState.currentPlayerFullIDArray[1] == param_1);
    if (DAT_GameSynchronyState.currentPlayerFullIDArray[2] == param_1) {
      uVar1 = 2;
    }
    if (DAT_GameSynchronyState.currentPlayerFullIDArray[3] == param_1) {
      uVar1 = 3;
    }
    if (DAT_GameSynchronyState.currentPlayerFullIDArray[4] == param_1) {
      uVar1 = 4;
    }
    if (DAT_GameSynchronyState.currentPlayerFullIDArray[5] == param_1) {
      uVar1 = 5;
    }
    if (DAT_GameSynchronyState.currentPlayerFullIDArray[6] == param_1) {
      uVar1 = 6;
    }
    if (DAT_GameSynchronyState.currentPlayerFullIDArray[7] == param_1) {
      uVar1 = 7;
    }
    if (DAT_GameSynchronyState.currentPlayerFullIDArray[8] == param_1) {
      uVar1 = 8;
    }
    return uVar1;
  }
                    /* Used in singleplayer */
  return DAT_GameSynchronyState.currentPlayerSlotID;
}


// ================= _HoldStrong::Synchrony::GameSynchronyState::getCommandIDFromCommandSelectionStuff @ 00480440 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Synchrony::GameSynchronyState::getCommandIDFromCommandSelectionStuff
          (GameSynchronyState *this)

{
  int iVar1;
  int iVar2;
  int iVar3;
  bool bVar4;
  int *piVar5;
  GameCommandStateByte *pGVar6;
  int iVar7;
  int iVar8;
  
  DAT_GameSynchronyState.MBR_someIndex = 0;
  IO::LowLevelMemory::fillMemory_ByteValue
            (&DAT_LowLevelMemory,800,'\0',DAT_GameSynchronyState.MBR_SelectedGameCommands);
  if (DAT_GameSynchronyState.MBR_GameCommandID < 200) {
    pGVar6 = &DAT_GameSynchronyState.DAT_GameCommandArray[DAT_GameSynchronyState.MBR_GameCommandID].
              stateUnk;
    iVar8 = DAT_GameSynchronyState.MBR_GameCommandID;
    do {
                    /* stateAddress - 9 = time address */
      if (((*pGVar6 != 0) && ((char)*pGVar6 < '\n')) &&
         ((int)((GameCommand *)(pGVar6 + -9))->time <= (int)DAT_GameCore.mapTimeInTicks)) {
                    /* if this command has not been processed, but should be processed, and it has
                       been its time
                       state address - 5 = player */
        DAT_GameSynchronyState.protocolInvokerPlayerID =
             translateMultiplayerIDsIntoPlayerIDs(*(int *)(pGVar6 + -5));
        DAT_GameSynchronyState.MBR_SelectedGameCommands[DAT_GameSynchronyState.MBR_someIndex][0] =
             iVar8;
        DAT_GameSynchronyState.MBR_SelectedGameCommands[DAT_GameSynchronyState.MBR_someIndex][1] =
             DAT_GameSynchronyState.protocolInvokerPlayerID;
        DAT_GameSynchronyState.MBR_someIndex = DAT_GameSynchronyState.MBR_someIndex + 1;
        if (99 < DAT_GameSynchronyState.MBR_someIndex) break;
      }
      iVar8 = iVar8 + 1;
                    /* move to next command */
      pGVar6 = pGVar6 + 0x4f8;
    } while (iVar8 < 200);
  }
                    /* reorder the selected commands list so that player ids with a lower number are
                       processed first. */
  iVar8 = 0;
  if (0 < DAT_GameSynchronyState.MBR_someIndex) {
    bVar4 = true;
    do {
      if (!bVar4) break;
      iVar7 = 1;
      iVar8 = iVar8 + 1;
      bVar4 = false;
      if (1 < DAT_GameSynchronyState.MBR_someIndex) {
        piVar5 = DAT_GameSynchronyState.MBR_SelectedGameCommands[0] + 1;
        do {
          iVar1 = piVar5[2];
          iVar2 = (*(int (*) [2])(piVar5 + -1))[0];
          iVar3 = *piVar5;
          if (iVar1 == 0) {
            return 0;
          }
          if (iVar1 < iVar3) {
            (*(int (*) [2])(piVar5 + -1))[0] = piVar5[1];
            *piVar5 = iVar1;
            piVar5[1] = iVar2;
            piVar5[2] = iVar3;
            bVar4 = true;
          }
          iVar7 = iVar7 + 1;
          piVar5 = piVar5 + 2;
        } while (iVar7 < DAT_GameSynchronyState.MBR_someIndex);
      }
    } while (iVar8 < 100);
    iVar8 = 1;
  }
  return iVar8;
}


// ================= _HoldStrong::Commands::ClickRecruitUnit @ 004821e0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Commands::ClickRecruitUnit(void)

{
  DAT_GameSynchronyState.DAT_CommandSize = 3;
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_SCHEDULE_AND_SEND) {
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam1,2,
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
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam1,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    Global::ProcessRecruitUnit
              (DAT_GameSynchronyState.protocolInvokerPlayerID,
               DAT_GameSynchronyState.DAT_GameCommandParam0,
               DAT_GameSynchronyState.DAT_GameCommandParam1);
  }
  return;
}


// ================= _HoldStrong::Commands::AskForPlayerSlotAssignment @ 0048f870 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* also called on Option menu
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Commands::AskForPlayerSlotAssignment(void)

{
  int iVar1;
  char _commandSenderIsHost;
  
  DAT_GameSynchronyState.DAT_CommandSize = 1;
  DAT_GameSynchronyState.DAT_GameCommandArray[DAT_GameSynchronyState.DAT_CurrentGameCommandID].time
       = 0;
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_SCHEDULE_AND_SEND) {
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.isHost,1,
               GCPL_FIXED_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    DAT_GameSynchronyState.DAT_CommandActionPlan = GCS_EXECUTE;
    return;
  }
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_EXECUTE) {
    if (DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) {
      DAT_GameSynchronyState.currentPlayerFullIDArray[0] = -1;
      DAT_GameSynchronyState.currentPlayerFullIDArray[2] = -1;
      DAT_GameSynchronyState.currentPlayerFullIDArray[3] = -1;
      DAT_GameSynchronyState.currentPlayerFullIDArray[4] = -1;
      DAT_GameSynchronyState.currentPlayerFullIDArray[5] = -1;
      DAT_GameSynchronyState.currentPlayerFullIDArray[6] = -1;
      DAT_GameSynchronyState.currentPlayerFullIDArray[7] = -1;
      DAT_GameSynchronyState.currentPlayerFullIDArray[8] = -1;
      DAT_GameSynchronyState.currentPlayerSlotID = 1;
      DAT_GameSynchronyState.currentPlayerFullIDArray[1] = 1;
      OS::_memcpy((void *)((int)DAT_TextureRenderCoreObject.bitmapsFaces_0x94 + 0x29400),
                  (void *)((DAT_GameCore.lordIconUnk + -2) * 0x2100 +
                          (int)DAT_TextureRenderCoreObject.bitmapsFaces_0x94),0x2100);
      DAT_TextureRenderCoreObject.field69_0x98[DAT_GameSynchronyState.currentPlayerSlotID + 0x13] =
           0x2100;
      return;
    }
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&_commandSenderIsHost,1,GCPL_FIXED_COMMAND_DATA_ADDRESS,
               GCPRW_DESERIALIZE_FROM_PARAM1);
    if (_commandSenderIsHost != '\0') {
      DAT_GameSynchronyState.DAT_TwoIfNotHost = 2;
    }
    if (DAT_GameSynchronyState.isHost != FALSE) {
      iVar1 = DAT_GameSynchronyState.DPLAYX_ReceivedPlayerID;
      if (DAT_GameSynchronyState.currentGameMode == GM_SKIRMISH_SINGLE_PLAYER) {
        iVar1 = 1;
      }
      DAT_GameSynchronyState.protocolInvokerPlayerID =
           Synchrony::GameSynchronyState::addPlayerToCurrentPlayerArray
                     (&DAT_GameSynchronyState,iVar1);
      Global::PutPlayerIntoRandomSlot(DAT_GameSynchronyState.protocolInvokerPlayerID);
      iVar1 = DAT_GameSynchronyState.protocolInvokerPlayerID;
      Synchrony::GameSynchronyState::clearGameCommandEntry
                (&DAT_GameSynchronyState,DAT_GameSynchronyState.DAT_CurrentGameCommandID);
      DAT_GameSynchronyState.protocolInvokerPlayerID = iVar1;
      if (DAT_GameSynchronyState.currentPlayerSlotID == 0) {
        DAT_GameSynchronyState.currentPlayerSlotID = iVar1;
        if (1 < DAT_GameCore.lordIconUnk) {
          Synchrony::GameSynchronyState::queueCommand(&DAT_GameSynchronyState,GCT_SHARE_AIV_HASH);
        }
        OS::_memcpy((void *)((DAT_GameSynchronyState.currentPlayerSlotID + 0x13) * 0x2100 +
                            (int)DAT_TextureRenderCoreObject.bitmapsFaces_0x94),
                    (void *)((DAT_GameCore.lordIconUnk + -2) * 0x2100 +
                            (int)DAT_TextureRenderCoreObject.bitmapsFaces_0x94),0x2100);
        DAT_TextureRenderCoreObject.field69_0x98[DAT_GameSynchronyState.currentPlayerSlotID + 0x13]
             = 0x2100;
      }
      else {
        Synchrony::GameSynchronyState::queueCommand
                  (&DAT_GameSynchronyState,GCT_ASSIGN_PLAYERID_TO_PLAYER_SLOT);
      }
      DAT_GameSynchronyState.DAT_PlayerSlotArraySomeValue[iVar1] = 0;
      Synchrony::GameSynchronyState::queueCommand
                (&DAT_GameSynchronyState,GCT_HOST_SHARE_LOBBY_STATE);
      DAT_GameSynchronyState.DAT_GameCommandParam0 = 1;
      Synchrony::GameSynchronyState::queueCommand
                (&DAT_GameSynchronyState,GCT_TRIGGER_LOBBY_PLAYER_INFORMATION_REFRESH);
      if ((DAT_GameCore.currentMenuViewType != MVT_CRUSADE_MISSION_INTRO) ||
         (-1 < DAT_GameCore.menuSwitchDelay)) {
        Synchrony::GameSynchronyState::queueCommand
                  (&DAT_GameSynchronyState,GCT_CHANGE_MAP_SELECTION);
      }
      Synchrony::GameSynchronyState::queueCommand
                (&DAT_GameSynchronyState,GCT_CHANGE_GAME_INTENSITY_OR_BALANCE);
      Synchrony::GameSynchronyState::reorderTeamsAndPositions(&DAT_GameSynchronyState);
      DAT_GameSynchronyState.reparseMaps = TRUE;
    }
  }
  return;
}


