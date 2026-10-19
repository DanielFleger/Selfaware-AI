// ================= playerMakeUnitSelection @ 00535bc0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::UnitsState::playerMakeUnitSelection
          (UnitsState *this,int playerID,int tribeID)

{
  UnitTypeShort UVar1;
  BOOLEnum BVar2;
  int iVar3;
  UnitType unitType;
  int unitID;
  
  DAT_UnitsState.unitCountOfSelection[playerID] = 0;
  DAT_CurrentUnitSlotID = 1;
  if (1 < (int)DAT_UnitsState.maxUnitCount) {
    do {
      if ((((DAT_UnitsState.units[DAT_CurrentUnitSlotID].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[DAT_CurrentUnitSlotID].dying == 0)) &&
          (DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner == playerID)) &&
         (BVar2 = TribesState::unitIsSelectedByPlayer(&DAT_TribesState,DAT_CurrentUnitSlotID),
         BVar2 != FALSE)) {
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].ifSelectedThenPlayerID = (short)playerID;
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].selectionRelatedFlag = 1;
        DAT_UnitsState.unitCountOfSelection[playerID] =
             DAT_UnitsState.unitCountOfSelection[playerID] + 1;
      }
      DAT_CurrentUnitSlotID = DAT_CurrentUnitSlotID + 1;
    } while ((int)DAT_CurrentUnitSlotID < (int)DAT_UnitsState.maxUnitCount);
  }
  TribesState::snapshotSelectionTribeAndComputeStance(&DAT_TribesState,playerID);
  TribesState::removeSelectedUnitsFromTheirCurrentTribes(&DAT_TribesState,playerID);
  iVar3 = TribesState::createPlayerTribe(&DAT_TribesState,playerID,1,tribeID);
  TribesState::addUnitsToTribeAndComputeMovementSpeed(&DAT_TribesState,playerID,iVar3);
  TribesState::importStoredInfoFromSlot0(&DAT_TribesState,playerID,iVar3);
  if (DAT_TribesState.tribes[iVar3].owner == DAT_GameSynchronyState.currentPlayerSlotID) {
    unitType = TribesState::getMajoritySelectedUnitType(&DAT_TribesState,iVar3,(int *)0x0);
    if ((((unitType == UT_S_CATAPULT) || (unitType == UT_S_TOWER)) ||
        ((unitType == UT_S_BATTERINGRAM ||
         ((unitType == UT_S_SHIELD || (unitType == UT_S_BALLISTA)))))) ||
       ((unitType == UT_S_FBALLISTA || ((unitType == UT_S_TREBUCHET || (unitType == UT_S_MANGONEL)))
        ))) {
      unitID = (int)DAT_TribesState.tribes[iVar3].selectionTargetUnitID;
      iVar3 = getRemainingRequiredEngineers(&DAT_UnitsState,unitID);
      if (0 < iVar3) {
        if ((DAT_UnitsState.units[unitID].
             digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 0) ||
           (3 < iVar3)) {
          Audio::SFX::SFXState::playUnitSpeechEffect(&DAT_SFXState,0xe);
          DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
          return;
        }
        if (iVar3 == 1) {
          Audio::SFX::SFXState::playUnitSpeechEffect(&DAT_SFXState,0xb);
          DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
          return;
        }
        if (iVar3 != 2) {
          if (iVar3 != 3) {
            DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
            return;
          }
          Audio::SFX::SFXState::playUnitSpeechEffect(&DAT_SFXState,0xd);
          DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
          return;
        }
        Audio::SFX::SFXState::playUnitSpeechEffect(&DAT_SFXState,0xc);
        DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
        return;
      }
      if ((unitType == UT_S_CATAPULT) || (unitType == UT_S_TREBUCHET)) {
        UVar1 = DAT_UnitsState.units[unitID].unitType;
        if (((UVar1 == UT_S_CATAPULT) || (UVar1 == UT_S_TREBUCHET)) &&
           (DAT_UnitsState.units[unitID].stoneAmmunition < 1)) {
          Audio::SFX::SFXState::playSpeechSFX(&DAT_SFXState,SEID_RESOURCE_NEED25);
          DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
          return;
        }
      }
    }
    Audio::SFX::SFXState::playUnitSpeech(&DAT_SFXState,unitType,0);
  }
  DAT_UIDragDropDefinedData.DAT_MenuView_TriggerInitial = TRUE;
  return;
}



