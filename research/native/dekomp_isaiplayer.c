// ================= _HoldStrong::Synchrony::GameSynchronyState::isAIPlayer @ 004010b0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:56:35.138000 */

BOOLEnum __thiscall
_HoldStrong::Synchrony::GameSynchronyState::isAIPlayer(GameSynchronyState *this,int playerID)

{
  if (DAT_GameSynchronyState.currentPlayerFullIDArray[playerID] != -1) {
    return FALSE;
  }
  return (uint)(DAT_GameSynchronyState.currentAIArray[playerID] != 0);
}


