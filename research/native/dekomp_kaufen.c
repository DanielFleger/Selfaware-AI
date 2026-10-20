// ================= ProcessBuyOrSell @ 0x00465e60 =================

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



