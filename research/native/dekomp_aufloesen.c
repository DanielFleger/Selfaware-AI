// ================= disbandUnit @ 0x0052edc0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall _HoldStrong::Map::Units::UnitsState::disbandUnit(UnitsState *this,int unitID)

{
  int *piVar1;
  short sVar2;
  UnitTypeShort UVar3;
  int iVar4;
  BOOLEnum BVar5;
  
  iVar4 = unitID;
  if ((DAT_UnitsState.units[unitID].unitType == UT_E_KNIGHT) &&
     (sVar2 = DAT_UnitsState.units[unitID].horseOriginStablesBuildingIndexUnk, sVar2 != 0)) {
    if (*(int *)&DAT_UnitsState.units[unitID].horseOriginStableIDUnk ==
        DAT_BuildingsState.buildings[sVar2].uid) {
      Buildings::BuildingsState::removeTetheredUnitFromBuilding
                (&DAT_BuildingsState,(int)sVar2,unitID);
    }
  }
  if (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) {
    UVar3 = DAT_UnitsState.units[iVar4].unitType;
    DAT_UnitsState.units[iVar4].logicalState = ULS_REMOVE;
                    /* note &unitID ! */
    Buildings::BuildingsState::getPriceForDisbandedUnitType
              (&DAT_BuildingsState,(int)(short)UVar3,&unitID);
    iVar4 = DAT_GameSynchronyState.currentPlayerSlotID * 0x39f4;
    piVar1 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
             startResources + 0xf;
    *piVar1 = *piVar1 + unitID;
    return iVar4 + 0x115c2a0;
  }
  BVar5 = Game::GameStateStructures::playerHasACampground
                    (&DAT_GameState,(int)DAT_UnitsState.units[iVar4].owner);
  DAT_UnitsState.units[iVar4].disappearFadeAlphaCountdown = 0;
  if (BVar5 != FALSE) {
    DAT_UnitsState.units[iVar4].state_2 = 0;
    DAT_UnitsState.units[iVar4].cachedState = US_DETERMINE_NEXT_STATEUnk;
    DAT_UnitsState.units[iVar4].unitTypeToChangeInto = UT_PEASANT;
    DAT_UnitsState.units[iVar4].state.generic = US_JESTER_ROAM_TO;
    DAT_UnitsState.units[iVar4].engineerManningSiegeStateRef_checkType = 1;
    DAT_UnitsState.units[iVar4].isDisappearingUnk = 1;
    return 1;
  }
  DAT_UnitsState.units[iVar4].updateTickTracker = 0;
  DAT_UnitsState.units[iVar4].state.generic = US_DISAPPEAR;
  DAT_UnitsState.units[iVar4].killedFlagUnk = 1;
  return 0;
}



