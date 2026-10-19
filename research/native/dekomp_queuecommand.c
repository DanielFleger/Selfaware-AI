// ================= queueCommand @ 0x00489100 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* juggernaunt: MultiplayerManager_SendCmdAddress
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Synchrony::GameSynchronyState::queueCommand
          (GameSynchronyState *this,GameCommandType commandType)

{
  dword time;
  byte commandCategory;
  
  DAT_GameSynchronyState.DAT_CurrentGameCommandID = DAT_GameSynchronyState.DAT_GameCommandArrayIndex
  ;
  IO::LowLevelMemory::fillMemory_ByteValue
            (&DAT_LowLevelMemory,0x4ec,'\0',
             &DAT_GameSynchronyState.DAT_GameCommandArray
              [DAT_GameSynchronyState.DAT_GameCommandArrayIndex].parameters);
  DAT_GameSynchronyState.DAT_GameCommandArray[DAT_GameSynchronyState.DAT_CurrentGameCommandID].
  stateUnk = GCS_UNPROCESSED;
  DAT_GameSynchronyState.DAT_GameCommandArray[DAT_GameSynchronyState.DAT_CurrentGameCommandID].
  playerUnk = DAT_GameSynchronyState.DPLAYX_PlayerHandle;
  commandCategory = (byte)commandType;
  DAT_GameSynchronyState.DAT_GameCommandArray[DAT_GameSynchronyState.DAT_CurrentGameCommandID].
  commandType = commandCategory;
  if (DAT_GameSynchronyState.mapTimeInTicksSinglePlayer < (int)DAT_GameCore.mapTimeInTicks) {
    DAT_GameSynchronyState.DAT_GameCommandArray[DAT_GameSynchronyState.DAT_CurrentGameCommandID].
    time = DAT_GameSynchronyState.commandDelay + DAT_GameCore.mapTimeInTicks;
  }
  else {
    DAT_GameSynchronyState.DAT_GameCommandArray[DAT_GameSynchronyState.DAT_CurrentGameCommandID].
    time = DAT_GameSynchronyState.commandDelay + DAT_GameSynchronyState.mapTimeInTicksSinglePlayer;
  }
  DAT_GameSynchronyState.DAT_CommandActionPlan = GCS_SCHEDULE_AND_SEND;
  DAT_GameSynchronyState.DAT_PlayerIDReceiver = 0;
  DAT_GameSynchronyState.DAT_CommandParameterOffset = 0;
                    /* Calls the callback function for a specific command. See "GameCommandType" for
                       possible commands. Includes placing buildings, walls, moving units,.. */
  (*(code *)DAT_ProtocolDefinedData.field14_0x240
            [DAT_GameSynchronyState.DAT_GameCommandArray
             [DAT_GameSynchronyState.DAT_CurrentGameCommandID].commandType + 0x15])();
  DAT_GameSynchronyState.DAT_CommandParameterOffset = 0;
  time = DAT_GameSynchronyState.DAT_GameCommandArray
         [DAT_GameSynchronyState.DAT_CurrentGameCommandID].time;
  if ((int)time < 1) {
                    /* time == 0 means it is an immediate (out of game time) command, commands that
                       don't change game state (gold, buildings, units, etc.), but rather operate on
                       a meta level */
    transmitCommand(&DAT_GameSynchronyState,commandCategory,time,
                    (char *)DAT_GameSynchronyState.DAT_GameCommandFixedParameterLocation,
                    DAT_GameSynchronyState.DAT_CommandSize,
                    DAT_GameSynchronyState.DAT_PlayerIDReceiver);
    if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_EXECUTE) {
      DAT_GameSynchronyState.DAT_GameCommandParam5 = 0;
      DAT_GameSynchronyState.DAT_GameCommandParam4 = 0;
      DAT_GameSynchronyState.DAT_GameCommandParam3 = 0;
      DAT_GameSynchronyState.DAT_GameCommandParam2 = 0;
      DAT_GameSynchronyState.DAT_GameCommandParam1 = 0;
      DAT_GameSynchronyState.DAT_GameCommandParam0 = 0;
      DAT_GameSynchronyState.DPLAYX_ReceivedPlayerID = DAT_GameSynchronyState.DPLAYX_PlayerHandle;
      DAT_GameSynchronyState.protocolInvokerPlayerID = DAT_GameSynchronyState.currentPlayerSlotID;
      (*(code *)DAT_ProtocolDefinedData.field14_0x240
                [DAT_GameSynchronyState.DAT_GameCommandArray
                 [DAT_GameSynchronyState.DAT_CurrentGameCommandID].commandType + 0x15])();
    }
    clearGameCommandEntry(&DAT_GameSynchronyState,DAT_GameSynchronyState.DAT_CurrentGameCommandID);
  }
  else {
    transmitCommand(&DAT_GameSynchronyState,commandCategory,time,
                    &DAT_GameSynchronyState.DAT_GameCommandArray
                     [DAT_GameSynchronyState.DAT_CurrentGameCommandID].parameters,
                    DAT_GameSynchronyState.DAT_CommandSize,
                    DAT_GameSynchronyState.DAT_PlayerIDReceiver);
    DAT_GameSynchronyState.DAT_GameCommandArrayIndex =
         DAT_GameSynchronyState.DAT_GameCommandArrayIndex + 1;
    if (199 < DAT_GameSynchronyState.DAT_GameCommandArrayIndex) {
      DAT_GameSynchronyState.DAT_GameCommandArrayIndex = 0;
      return;
    }
  }
  return;
}



