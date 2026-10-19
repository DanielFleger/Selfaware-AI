// ================= _HoldStrong::UI::Rendering::RenderBuildingMenu_RecruitingBuilding @ 0043a8d0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl _HoldStrong::UI::Rendering::RenderBuildingMenu_RecruitingBuilding(void)

{
  Map::Buildings::BuildingsState::createEntityForAssemblyPointsForActiveTabType(&DAT_BuildingsState)
  ;
  return;
}


// ================= _HoldStrong::Map::Version::initPopularityAndRecruitableDefaults @ 0045ad10 =================

/* Initialises default values for all 8 players after a map version upgrade. Copies each player's
   storedPopularityPercent into someCount44, and sets all euro and merc recruitable flags to 1
   (enabled) across both the primary and copy arrays in mapAndTime. Called as part of the map
   versioning/upgrade pipeline.
   
   renamed by: Claude Sonnet 4.6 */

void _HoldStrong::Map::Version::initPopularityAndRecruitableDefaults(void)

{
  DAT_GameState.playerDataArray[1].someCount44 =
       (short)DAT_GameState.playerDataArray[1].storedPopularityPercent;
  DAT_GameState.playerDataArray[2].someCount44 =
       (short)DAT_GameState.playerDataArray[2].storedPopularityPercent;
  DAT_GameState.playerDataArray[4].someCount44 =
       (short)DAT_GameState.playerDataArray[4].storedPopularityPercent;
  DAT_GameState.playerDataArray[3].someCount44 =
       (short)DAT_GameState.playerDataArray[3].storedPopularityPercent;
  DAT_GameState.playerDataArray[5].someCount44 =
       (short)DAT_GameState.playerDataArray[5].storedPopularityPercent;
  DAT_GameState.playerDataArray[7].someCount44 =
       (short)DAT_GameState.playerDataArray[7].storedPopularityPercent;
  DAT_GameState.playerDataArray[6].someCount44 =
       (short)DAT_GameState.playerDataArray[6].storedPopularityPercent;
  DAT_GameState.playerDataArray[8].someCount44 =
       (short)DAT_GameState.playerDataArray[8].storedPopularityPercent;
  DAT_GameState.mapAndTime.euroRecruitable[0] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[0] = 1;
  DAT_GameState.mapAndTime.euroRecruitable[1] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[1] = 1;
  DAT_GameState.mapAndTime.euroRecruitable[2] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[2] = 1;
  DAT_GameState.mapAndTime.euroRecruitable[3] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[3] = 1;
  DAT_GameState.mapAndTime.euroRecruitable[4] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[4] = 1;
  DAT_GameState.mapAndTime.euroRecruitable[5] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[5] = 1;
  DAT_GameState.mapAndTime.euroRecruitable[6] = 1;
  DAT_GameState.mapAndTime.mercRecruitable[6] = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_0 = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_1_b = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_2 = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_3_b = 1;
  DAT_GameState.mapAndTime.field2257_0xda8 = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_6_a = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_1_a = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_3_a_and_6_b = 1;
  DAT_GameState.mapAndTime.euroRecruitableCopy_index_6_c = 1;
  return;
}


// ================= _HoldStrong::Global::IsEuroUnitRecruitableUnk @ 00464da0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

EuroRecruitableState __cdecl _HoldStrong::Global::IsEuroUnitRecruitableUnk(int barrackUnitIdUnk)

{
  int iVar1;
  ResourceTypeInt RVar2;
  int *piVar3;
  int iVar4;
  bool bVar5;
  
  RVar2 = DAT_TroopDefinedData.MarketResourceCycleArray[barrackUnitIdUnk + -1];
  if ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
     (DAT_GameSynchronyState.skirmishTroopsCostGold == 0)) {
    RVar2 = 0;
  }
  if (DAT_GameState.mapAndTime.euroRecruitable[barrackUnitIdUnk + -0x16] == 0) {
    return ERS_NOT_ALLOWED_TO_RECRUIT;
  }
  if (DAT_GameState.mapAndTime.armySizeLimit <=
      DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].count_2 +
      DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].armySize) {
    return ERS_UNABLE_BECAUSE_MAX_ARMY;
  }
  if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].currentResources
      [0xf] < (int)RVar2) {
    return ERS_CAN_NOT_RECRUIT;
  }
  iVar4 = 0;
  piVar3 = DAT_UnitPropertiesDefinedData.DAT_MELEE_DAMAGE[0x4e] + barrackUnitIdUnk * 4 + 0x48;
  do {
    iVar1 = *piVar3;
    if (iVar1 == -1) {
      bVar5 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
              availableHorses == 0;
LAB_00464e3f:
      if (bVar5) {
        return ERS_CAN_NOT_RECRUIT;
      }
    }
    else if (iVar1 != 0) {
      bVar5 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
              currentResources[iVar1] == 0;
      goto LAB_00464e3f;
    }
    iVar4 = iVar4 + 1;
    piVar3 = piVar3 + 1;
    if (3 < iVar4) {
      iVar4 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
              availablePeasantsOrHousedPeasants;
      iVar1 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].count;
      return ((iVar4 != iVar1 && -1 < iVar4 - iVar1) - 1 & 3) + ERS_CAN_RECRUITUnk;
    }
  } while( true );
}


// ================= _HoldStrong::Global::GetUnitRecruitPermission @ 00464e80 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __cdecl _HoldStrong::Global::GetUnitRecruitPermission(int param_1)

{
  int iVar1;
  int iVar2;
  
  if (*(int *)(DAT_GameState.mapAndTime.playerIsAlive + param_1 * 2 + 0x16) == 0) {
    return 2;
  }
  if (DAT_GameState.mapAndTime.armySizeLimit <=
      DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].count_2 +
      DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].armySize) {
    return 3;
  }
  if (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].currentResources
      [0xf] < DAT_TroopDefinedData.field279_0x210[param_1]) {
                    /* not enough gold */
    return 0;
  }
  iVar1 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
          availablePeasantsOrHousedPeasants;
  iVar2 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].count;
  return ((iVar1 != iVar2 && -1 < iVar1 - iVar2) - 1 & 3) + 1;
}


// ================= _HoldStrong::Global::ProcessRecruitUnit @ 00464ef0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::Global::ProcessRecruitUnit(int playerID,int unitType,undefined4 recruitmentBuildingID)

{
  if (DAT_GameState.playerDataArray[playerID].count_2 +
      DAT_GameState.playerDataArray[playerID].armySize < DAT_GameState.mapAndTime.armySizeLimit) {
    if (unitType == 0x1e) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_E_ENGINEER,
                 DAT_GameState.playerDataArray[playerID].engineersGuild.id,playerID,0);
      return;
    }
    if (unitType == 5) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_TUNNELER,
                 DAT_GameState.playerDataArray[playerID].tunnelersGuild.id,playerID,0);
      return;
    }
    if (unitType == 0x1d) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_E_LADDER,
                 DAT_GameState.playerDataArray[playerID].engineersGuild.id,playerID,0);
      return;
    }
    if (unitType == 0x25) {
                    /* monk */
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_E_MONK,recruitmentBuildingID,playerID,0);
      return;
    }
    if (unitType == 0x46) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_ARCHER,
                 DAT_GameState.playerDataArray[playerID].mercenaryPost.id,playerID,0);
      return;
    }
    if (unitType == 0x47) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_SLAVE,DAT_GameState.playerDataArray[playerID].mercenaryPost.id
                 ,playerID,0);
      return;
    }
    if (unitType == 0x48) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_SLINGER,
                 DAT_GameState.playerDataArray[playerID].mercenaryPost.id,playerID,0);
      return;
    }
    if (unitType == 0x49) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_ASSASSIN,
                 DAT_GameState.playerDataArray[playerID].mercenaryPost.id,playerID,0);
      return;
    }
    if (unitType == 0x4a) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_HARCHER,
                 DAT_GameState.playerDataArray[playerID].mercenaryPost.id,playerID,0);
      return;
    }
    if (unitType == 0x4b) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_SWORDSMAN,
                 DAT_GameState.playerDataArray[playerID].mercenaryPost.id,playerID,0);
      return;
    }
    if (unitType == 0x4c) {
      Map::Units::UnitsState::nonEuroRecruit
                (&DAT_UnitsState,UT_A_FIRETHROWER,
                 DAT_GameState.playerDataArray[playerID].mercenaryPost.id,playerID,0);
      return;
    }
    Map::Units::UnitsState::euroRecruit
              (&DAT_UnitsState,unitType,DAT_GameState.playerDataArray[playerID].barracks.id,playerID
               ,0);
  }
  return;
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


// ================= _HoldStrong::Map::MapPropertiesState::isMercRecruitableForBuildingType @ 004bb0b0 =================

/* Returns 1 always in editor mode. Otherwise returns SEC_MercRecruitable[param_1 - 0x38] from
   MapPropertiesState, indicating whether the mercenary unit type associated with this building
   offset is recruitable in the current map configuration.
   
   renamed by: Claude Sonnet 4.6 */

int __thiscall
_HoldStrong::Map::MapPropertiesState::isMercRecruitableForBuildingType
          (MapPropertiesState *this,int param_1)

{
  int iVar1;
  
  iVar1 = 1;
  if (DAT_GameCore.gameMode_2 != GM_EDITOR) {
    iVar1 = (int)DAT_MapPropertiesState.SEC_MercRecruitable[param_1 + -0x38];
  }
  return iVar1;
}


// ================= _HoldStrong::AI::AICState::randomlySelectAttackUnitTypeToRecruit @ 004cc070 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* doc:
   Determines which AI unit behaviour groups need recruiting because AIC Max units hasn't been
   reached for that category, then randomly selects one of those groups to recruit
   
   @returns AiUnitBehaviourType The selected unit behaviour type
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

AIUnitBehaviourType __thiscall
_HoldStrong::AI::AICState::randomlySelectAttackUnitTypeToRecruit(AICState *this,int playerID)

{
  AITypeInt AVar1;
  int iVar2;
  BOOLEnum *pBVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  AVar1 = DAT_GameState.playerDataArray[playerID].aiType;
  if (AVar1 == AIT_NULL) {
    return AIUBT_ATTUNITMAIN;
  }
  iVar5 = DAT_GameState.playerDataArray[playerID].attackedPlayerID;
  iVar6 = 0;
                    /* clear out flags */
  pBVar3 = &DAT_SkirmishDefinedData.attackUnitRequired[0].required;
  do {
    *pBVar3 = FALSE;
    pBVar3 = pBVar3 + 2;
  } while ((int)pBVar3 < 0xb425ec);
  iVar2 = DAT_AICState.aics[AVar1 + ~AIT_NULL].AttMaxEngineers;
  iVar4 = DAT_GameState.playerDataArray[playerID].currentAttackWave * 4;
  if (iVar2 < iVar4) {
    iVar4 = iVar2;
  }
  if ((iVar2 != 0) && (DAT_GameState.playerDataArray[playerID].totalAttackingEngineerTroops < iVar4)
     ) {
    iVar6 = 1;
    DAT_SkirmishDefinedData.attackUnitRequired[0].required = TRUE;
  }
  iVar2 = DAT_AICState.aics[AVar1 + ~AIT_NULL].AttDiggingUnitMax;
  if (((iVar2 != 0) && (DAT_GameState.playerDataArray[playerID].totalDiggingUnitTroops < iVar2)) &&
     (5 < DAT_GameState.playerDataArray[iVar5].moatsOwned)) {
    iVar6 = iVar6 + 1;
    DAT_SkirmishDefinedData.attackUnitRequired[1].required = TRUE;
  }
  iVar5 = DAT_AICState.aics[AVar1 + ~AIT_NULL].AttMaxAssassins;
  if ((iVar5 != 0) && (DAT_GameState.playerDataArray[playerID].totalAssassinTroops < iVar5)) {
    iVar6 = iVar6 + 1;
    DAT_SkirmishDefinedData.attackUnitRequired[2].required = TRUE;
  }
  iVar5 = DAT_AICState.aics[AVar1 + ~AIT_NULL].AttUnit2Max;
  if ((iVar5 != 0) && (DAT_GameState.playerDataArray[playerID].totalUnit2Troops < iVar5)) {
    iVar6 = iVar6 + 1;
    DAT_SkirmishDefinedData.attackUnitRequired[3].required = TRUE;
  }
  iVar5 = DAT_AICState.aics[AVar1 + ~AIT_NULL].AttMaxLaddermen;
  if ((iVar5 != 0) && (DAT_GameState.playerDataArray[playerID].totalLaddermenTroops < iVar5)) {
    iVar6 = iVar6 + 1;
    DAT_SkirmishDefinedData.attackUnitRequired[4].required = TRUE;
  }
  iVar5 = DAT_AICState.aics[AVar1 + ~AIT_NULL].AttMaxTunnelers;
  if ((iVar5 != 0) && (DAT_GameState.playerDataArray[playerID].totalTunnelerTroops < iVar5)) {
    iVar6 = iVar6 + 1;
    DAT_SkirmishDefinedData.attackUnitRequired[5].required = TRUE;
  }
  iVar5 = DAT_AICState.aics[AVar1 + ~AIT_NULL].AttUnitPatrolMax;
  if ((iVar5 != 0) && (DAT_GameState.playerDataArray[playerID].totalUnitPatrolTroops < iVar5)) {
    iVar6 = iVar6 + 1;
    DAT_SkirmishDefinedData.attackUnitRequired[6].required = TRUE;
  }
  iVar5 = DAT_AICState.aics[AVar1 + ~AIT_NULL].AttUnitBackupMax;
  if ((iVar5 != 0) && (DAT_GameState.playerDataArray[playerID].totalUnitBackupTroops < iVar5)) {
    iVar6 = iVar6 + 1;
    DAT_SkirmishDefinedData.attackUnitRequired[7].required = TRUE;
  }
  iVar5 = DAT_AICState.aics[AVar1 + ~AIT_NULL].AttUnitEngageMax;
  if ((iVar5 != 0) && (DAT_GameState.playerDataArray[playerID].totalUnitEngageTroops < iVar5)) {
    iVar6 = iVar6 + 1;
    DAT_SkirmishDefinedData.attackUnitRequired[8].required = TRUE;
  }
  iVar5 = DAT_AICState.aics[AVar1 + ~AIT_NULL].AttUnitSiegeDefMax;
  if ((iVar5 != 0) && (DAT_GameState.playerDataArray[playerID].totalUnitSiegeDefTroops < iVar5)) {
    iVar6 = iVar6 + 1;
    DAT_SkirmishDefinedData.attackUnitRequired[9].required = TRUE;
  }
  iVar5 = DAT_AICState.aics[AVar1 + ~AIT_NULL].AttMaxDefault;
  if ((iVar5 != 0) && (DAT_GameState.playerDataArray[playerID].totalMaxDefaultTroops < iVar5)) {
    iVar6 = iVar6 + 1;
    DAT_SkirmishDefinedData.attackUnitRequired[10].required = TRUE;
  }
  if (iVar6 != 0) {
    iVar6 = (int)SEC_RNG.currentNumber2 % iVar6;
    Random::RNG::nextRandomNumber2(&SEC_RNG);
    iVar5 = 0;
    do {
      if (DAT_SkirmishDefinedData.attackUnitRequired[iVar5].required != FALSE) {
        if (iVar6 == 0) {
          return DAT_SkirmishDefinedData.attackUnitRequired[iVar5].unitBehaviourType;
        }
        iVar6 = iVar6 + -1;
      }
      iVar5 = iVar5 + 1;
    } while (iVar5 < 0xb);
  }
  return AIUBT_ATTUNITMAIN;
}


// ================= _HoldStrong::AI::AICState::aiRecruitEngineers @ 004cc520 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::AI::AICState::aiRecruitEngineers(AICState *this,int playerID)

{
  AITypeInt AVar1;
  int recruitmentBuilding;
  
  AVar1 = DAT_GameState.playerDataArray[playerID].aiType;
  if ((((AVar1 != AIT_NULL) && (DAT_GameState.playerDataArray[playerID].isEngineerRequired != FALSE)
       ) && (DAT_GameState.playerDataArray[playerID].canStartSpending != 0)) &&
     (((0x1d < *(int *)((int)DAT_EntityState.seagullArray + AVar1 * 0x2a4 + 0x2588) +
               DAT_GameState.playerDataArray[playerID].currentResources[0xf] &&
       (recruitmentBuilding = DAT_GameState.playerDataArray[playerID].engineersGuild.id,
       0 < recruitmentBuilding)) &&
      (DAT_BuildingsState.buildings[recruitmentBuilding].buildingType == BT_ENGINEERSGUILD)))) {
    Map::Units::UnitsState::nonEuroRecruit
              (&DAT_UnitsState,UT_E_ENGINEER,recruitmentBuilding,playerID,0);
    DAT_GameState.playerDataArray[playerID].isEngineerRequired = FALSE;
  }
  return;
}


// ================= _HoldStrong::AI::AICState::recruitHarrassingSiegeEngines @ 004cd2a0 =================

/* WARNING: Enum "MappersEnumShort": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::AI::AICState::recruitHarrassingSiegeEngines(AICState *this,int playerID)

{
  AITypeInt AVar1;
  int iVar2;
  MappersEnum cbt;
  int iVar3;
  uint unitID;
  BOOLEnum BVar4;
  UnitTypeShort *pUVar5;
  int iVar6;
  int iVar7;
  
  AVar1 = DAT_GameState.playerDataArray[playerID].aiType;
  iVar6 = DAT_GameState.playerDataArray[playerID].engineersGuild.id;
  if ((AVar1 != AIT_NULL) && (499 < DAT_GameState.playerDataArray[playerID].currentResources[0xf]))
  {
    iVar3 = AVar1 + ~AIT_NULL;
    iVar7 = *(int *)((int)&DAT_AICState + iVar3 * 0x2a4 + 0x1ec);
    if (0 < iVar7) {
      iVar2 = DAT_GameState.playerDataArray[playerID].harrasingEngineRecruitTimeout;
      if (iVar2 != 0) {
        DAT_GameState.playerDataArray[playerID].harrasingEngineRecruitTimeout = iVar2 + -1;
        return;
      }
      if ((DAT_GameState.playerDataArray[playerID].harassingSiegeEnginesCountUnk < iVar7) &&
         (DAT_GameState.playerDataArray[playerID].unknownHarrassingSiegeRelated < 0x14)) {
        iVar7 = (int)DAT_GameState.playerDataArray[playerID].aiTribeIDs[0xa5];
        if ((iVar7 == 0) ||
           ((DAT_TribesState.tribes[iVar7].uid !=
             DAT_GameState.playerDataArray[playerID].aiTribeUIDs[0xa5] ||
            (DAT_TribesState.tribes[iVar7].size < 2)))) {
          if (DAT_GameState.playerDataArray[playerID].canStartSpending == 0) {
            return;
          }
          if (DAT_GameState.playerDataArray[playerID].currentResources[0xf] < 0x1e) {
            return;
          }
          if (iVar6 < 1) {
            return;
          }
          if (DAT_BuildingsState.buildings[iVar6].buildingType != BT_ENGINEERSGUILD) {
            return;
          }
          unitID = Map::Units::UnitsState::nonEuroRecruit
                             (&DAT_UnitsState,UT_E_ENGINEER,iVar6,playerID,0);
          if (unitID == 0) {
            return;
          }
          if ((iVar7 == 0) ||
             (DAT_TribesState.tribes[iVar7].uid !=
              DAT_GameState.playerDataArray[playerID].aiTribeUIDs[0xa5])) {
            iVar7 = Map::Units::TribesState::createTribeForPlayer(&DAT_TribesState,playerID);
          }
          iVar6 = DAT_TribesState.tribes[iVar7].uid;
          DAT_GameState.playerDataArray[playerID].aiTribeIDs[0xa5] = (short)iVar7;
          DAT_GameState.playerDataArray[playerID].aiTribeUIDs[0xa5] = iVar6;
          Map::Units::TribesState::addUnitToTribe(&DAT_TribesState,unitID,iVar7);
          DAT_UnitsState.units[unitID].aiUnitBehaviourType = 0x16;
        }
        else {
          if (7 < DAT_GameState.playerDataArray[playerID].harrassingSiegeEnginesIndex) {
            DAT_GameState.playerDataArray[playerID].harrassingSiegeEnginesIndex = 0;
          }
          iVar3 = iVar3 * 0xa9;
          if (*(int *)((int)&DAT_AICState +
                      (DAT_GameState.playerDataArray[playerID].harrassingSiegeEnginesIndex + iVar3)
                      * 4 + 0x1cc) == 0) {
            DAT_GameState.playerDataArray[playerID].harrassingSiegeEnginesIndex = 0;
          }
          iVar6 = DAT_GameState.playerDataArray[playerID].harrassingSiegeEnginesIndex;
          cbt = *(MappersEnum *)((int)&DAT_AICState + (iVar3 + iVar6) * 4 + 0x1cc);
          DAT_GameState.playerDataArray[playerID].harrassingSiegeEnginesIndex = iVar6 + 1;
          BVar4 = AIVState::findSpotNearEngineersGuild(&DAT_AIVState,playerID);
          if (BVar4 == FALSE) {
            return;
          }
          iVar6 = DAT_AIVState.buildingAppropriateGridYPosition * 5;
          iVar3 = DAT_AIVState.buildingApproriateGridXPosition * 5;
          DAT_TribesState.tribes[iVar7].tribeType = AITT_ENGINEERS;
          DAT_TribesState.tribes[iVar7].tribeBehaviorType = STBT_0x410_SIEGE_EQUIPMENT_CONSTRUCTION;
                    /* palce siege engine tent? */
          Map::TileMapState::placeBuilding(&DAT_TileMapState,playerID,iVar3,iVar6,cbt,3,0xf);
          iVar6 = DAT_TileMapState.placedBuildingID;
          if (DAT_TileMapState.buildingPlacementFail != FALSE) {
            return;
          }
          DAT_BuildingsState.buildings[DAT_TileMapState.placedBuildingID].attackWave = 0;
          DAT_BuildingsState.buildings[iVar6].unknownSiegeTentRelated01 = 2;
          Map::Units::TribesState::giveTribeAnInstruction
                    (&DAT_TribesState,iVar7,UIT_CONSTRUCT_SIEGE_EQUIPMENTOIL_DUTYENGINEERRELATED,
                     iVar6,DAT_BuildingsState.buildings[iVar6].uid,0);
        }
        iVar6 = 1;
        if (1 < (int)DAT_UnitsState.maxUnitCount) {
          pUVar5 = &DAT_UnitsState.units[1].unitType;
          do {
            if ((((pUVar5[-1] != ULS_INVISIBLE) && (pUVar5[0x109] == 0)) &&
                ((*pUVar5 == UT_S_CATAPULT || (*pUVar5 == UT_S_FBALLISTA)))) &&
               (pUVar5[0x1ce] == 0x15)) {
              pUVar5[0x1d2] = (short)DAT_GameState.playerDataArray[playerID].attackedPlayerID;
            }
            iVar6 = iVar6 + 1;
            pUVar5 = pUVar5 + 0x248;
          } while (iVar6 < (int)DAT_UnitsState.maxUnitCount);
        }
        DAT_GameState.playerDataArray[playerID].harrasingEngineRecruitTimeout = 8;
      }
    }
  }
  return;
}


// ================= _HoldStrong::AI::AICState::aiRecruitSortieRangedUnits @ 004cd560 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::AI::AICState::aiRecruitSortieRangedUnits(AICState *this,int playerID)

{
  AITypeInt AVar1;
  UnitType unitType;
  int iVar2;
  uint unitID;
  int iVar3;
  
  AVar1 = DAT_GameState.playerDataArray[playerID].aiType;
  if (AVar1 != AIT_NULL) {
    iVar2 = (AVar1 + ~AIT_NULL) * 0x2a4;
    iVar3 = *(int *)((int)&DAT_AICState + iVar2 + 0x14c);
                    /* bug: missing != 0? */
    if (((((-1 < iVar3) &&
          (DAT_GameState.playerDataArray[playerID].totalTroopsType6 <
           DAT_GameState.playerDataArray[playerID].unknownCounter_01 / 2 + iVar3)) &&
         (0 < DAT_GameState.playerDataArray[playerID].idlePeasantsCount)) &&
        ((DAT_GameState.playerDataArray[playerID].canStartSpending != 0 &&
         (unitType = *(UnitType *)((int)&DAT_AICState + iVar2 + 0x150), unitType != UT_E_ENGINEER)))
        ) && ((unitType != UT_E_LADDER && (unitType != UT_TUNNELER)))) {
      if ((int)unitType < 0x46) {
        iVar3 = DAT_GameState.playerDataArray[playerID].barracks.id;
      }
      else {
        iVar3 = DAT_GameState.playerDataArray[playerID].mercenaryPost.id;
      }
      if (iVar3 != 0) {
        if ((int)unitType < 0x46) {
          unitID = Map::Units::UnitsState::euroRecruit(&DAT_UnitsState,unitType,iVar3,playerID,0);
        }
        else {
          unitID = Map::Units::UnitsState::nonEuroRecruit(&DAT_UnitsState,unitType,iVar3,playerID,0)
          ;
        }
        if (unitID == 0) {
          iVar3 = *(int *)((int)&DAT_AICState + iVar2 + 0x9c);
          if ((0 < iVar3) && (DAT_UnitsState.DAT_EuroUnitAcquisitionFailReason == 2)) {
            DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray
            [DAT_UnitsState.DAT_EuroUnitRequiredResource] = iVar3;
            return;
          }
        }
        else {
          DAT_UnitsState.units[unitID].aiUnitBehaviourType = 6;
          iVar3 = createTribeForUnitType(&DAT_AICState,playerID,0xa6);
          Map::Units::TribesState::addUnitToTribe(&DAT_TribesState,unitID,iVar3);
        }
      }
    }
  }
  return;
}


// ================= _HoldStrong::AI::AICState::aiRecruitSortieMeleeUnits @ 004cd690 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::AI::AICState::aiRecruitSortieMeleeUnits(AICState *this,int playerID)

{
  AITypeInt AVar1;
  UnitType unitType;
  int iVar2;
  uint unitID;
  int iVar3;
  
  AVar1 = DAT_GameState.playerDataArray[playerID].aiType;
  if (AVar1 != AIT_NULL) {
    iVar2 = (AVar1 + ~AIT_NULL) * 0x2a4;
    iVar3 = *(int *)((int)&DAT_AICState + iVar2 + 0x154);
    if (((((-1 < iVar3) && (DAT_GameState.playerDataArray[playerID].totalTroopsType7 < iVar3)) &&
         (0 < DAT_GameState.playerDataArray[playerID].idlePeasantsCount)) &&
        ((DAT_GameState.playerDataArray[playerID].canStartSpending != 0 &&
         (unitType = *(UnitType *)((int)&DAT_AICState + iVar2 + 0x158), unitType != UT_E_ENGINEER)))
        ) && ((unitType != UT_E_LADDER && (unitType != UT_TUNNELER)))) {
      if ((int)unitType < 0x46) {
        iVar3 = DAT_GameState.playerDataArray[playerID].barracks.id;
      }
      else {
        iVar3 = DAT_GameState.playerDataArray[playerID].mercenaryPost.id;
      }
      if (iVar3 != 0) {
        if ((int)unitType < 0x46) {
          unitID = Map::Units::UnitsState::euroRecruit(&DAT_UnitsState,unitType,iVar3,playerID,0);
        }
        else {
          unitID = Map::Units::UnitsState::nonEuroRecruit(&DAT_UnitsState,unitType,iVar3,playerID,0)
          ;
        }
        if (unitID == 0) {
          iVar3 = *(int *)((int)&DAT_AICState + iVar2 + 0x9c);
          if ((0 < iVar3) && (DAT_UnitsState.DAT_EuroUnitAcquisitionFailReason == 2)) {
            DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray
            [DAT_UnitsState.DAT_EuroUnitRequiredResource] = iVar3;
            return;
          }
        }
        else {
          DAT_UnitsState.units[unitID].aiUnitBehaviourType = 7;
          iVar3 = createTribeForUnitType(&DAT_AICState,playerID,0xa7);
          Map::Units::TribesState::addUnitToTribe(&DAT_TribesState,unitID,iVar3);
        }
      }
    }
  }
  return;
}


// ================= _HoldStrong::AI::AICState::aiRecruitEngineerForOilDuty @ 004d2500 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::AI::AICState::aiRecruitEngineerForOilDuty(AICState *this,int playerID)

{
  int iVar1;
  int iVar2;
  uint unitID;
  int iVar3;
  
  if (((((DAT_GameState.playerDataArray[playerID].aiType != AIT_NULL) &&
        (iVar1 = DAT_GameState.playerDataArray[playerID].engineersGuild.id,
        DAT_GameState.playerDataArray[playerID].canStartSpending != 0)) &&
       (0x1d < DAT_GameState.playerDataArray[playerID].currentResources[0xf])) &&
      ((0 < iVar1 && (DAT_BuildingsState.buildings[iVar1].buildingType == BT_ENGINEERSGUILD)))) &&
     ((iVar1 = DAT_GameState.playerDataArray[playerID].oilSmelter.id, 0 < iVar1 &&
      ((DAT_BuildingsState.buildings[iVar1].buildingType == BT_OILSMELTER &&
       (iVar3 = DAT_GameState.playerDataArray[playerID].aivUnitLocationSlotLocationCount[1] + 1,
       1 < iVar3)))))) {
    if ((DAT_BuildingsState.buildings[iVar1].resourcePitch < 1) &&
       (DAT_GameState.playerDataArray[playerID].currentResources[7] < 1)) {
      DAT_GameState.playerDataArray[playerID].resourcesToAcquireArray[7] = 4;
      return;
    }
    iVar2 = Global::ChecksAndGenerateAITribesForPlayerIfNotExisting(playerID,iVar3,TRUE);
    if (iVar2 != 0) {
      iVar3 = Global::ChecksAndGenerateAITribesForPlayerIfNotExisting(playerID,iVar3,FALSE);
      unitID = Map::Units::UnitsState::nonEuroRecruit
                         (&DAT_UnitsState,UT_E_ENGINEER,
                          DAT_GameState.playerDataArray[playerID].engineersGuild.id,playerID,0);
      Map::Units::TribesState::addUnitToTribe(&DAT_TribesState,unitID,iVar3);
      if (unitID != 0) {
        DAT_UnitsState.units[unitID].engineerRelatedUnk = 1;
        DAT_TribesState.tribes[iVar3].unitStance = USE_DEFENSIVE;
        iVar2 = DAT_BuildingsState.buildings[iVar1].uid;
        DAT_TribesState.tribes[iVar3].tribeType = AITT_ENGINEERS;
        DAT_TribesState.tribes[iVar3].tribeBehaviorType = STBT_0x41d;
        Map::Units::UnitsState::relayTribeInstruction
                  (&DAT_UnitsState,iVar3,UIT_CONSTRUCT_SIEGE_EQUIPMENTOIL_DUTYENGINEERRELATED,iVar1,
                   iVar2,0);
      }
    }
  }
  return;
}


// ================= _HoldStrong::AI::AICState::aiRecruitUnits @ 004d3ae0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::AI::AICState::aiRecruitUnits(AICState *this,int playerID)

{
  int iVar1;
  int *piVar2;
  AITypeInt AVar3;
  int iVar4;
  AIRecruitUnitChoiceInt AVar5;
  bool bVar6;
  bool bVar7;
  int playerID_00;
  int iVar8;
  int iVar9;
  AICState *extraout_ECX;
  AICState *pAVar10;
  UnitType unitType;
  AICState *_pAICState;
  int local_8;
  
  playerID_00 = playerID;
  AVar3 = DAT_GameState.playerDataArray[playerID].aiType;
  unitType = 0;
  pAVar10 = &DAT_AICState;
  _pAICState = &DAT_AICState;
  if (AVar3 != AIT_NULL) {
    bVar6 = false;
    bVar7 = false;
    iVar1 = AVar3 + ~AIT_NULL;
    if (((DAT_GameCore.gameMode_2 == GM_SKIRMISH_AND_MULTIPLAYER) &&
        (DAT_GameCore.isSkirmishTrail == TRUE)) && (DAT_GameCore.currentTrailType == TT_EXTREME)) {
      bVar6 = true;
    }
    iVar8 = iVar1 * 0xa9;
    iVar9 = *(int *)((int)&DAT_AICState +
                    (DAT_GameState.playerDataArray[playerID].aiStrengthFeeling + iVar8) * 4 + 0x164)
    ;
    iVar4 = -(uint)(iVar9 != 0);
    local_8 = iVar4 + 2;
    if (bVar6) {
      local_8 = iVar4 + 3;
    }
    iVar4 = DAT_GameState.playerDataArray[playerID].aiNervousActionsTracker;
    if (iVar4 < 1) {
      piVar2 = &DAT_GameState.playerDataArray[playerID].aiRecruitIntervalTracker;
      *piVar2 = *piVar2 + 1;
      if (DAT_GameState.playerDataArray[playerID].aiRecruitIntervalTracker < iVar9) {
        return;
      }
    }
    else {
      local_8 = 4;
    }
    iVar9 = DAT_GameState.playerDataArray[playerID].idlePeasantsCount;
    DAT_GameState.playerDataArray[playerID].aiRecruitIntervalTracker = 0;
    if ((0 < iVar9) && (DAT_GameState.playerDataArray[playerID].canStartSpending != 0)) {
      AVar5 = DAT_GameState.playerDataArray[playerID].aiRecruitUnitChoiceState;
      if (AVar5 == AIRUC_DEFENSIVE) {
        iVar9 = *(int *)((int)&DAT_AICState + iVar1 * 0x2a4 + 0x170);
        if (bVar6) {
          iVar9 = (iVar9 * 4) / 3;
        }
        pAVar10 = &DAT_AICState;
        if (0 < iVar4) {
          iVar9 = iVar9 * 4;
        }
        if (iVar9 <= DAT_GameState.playerDataArray[playerID].totalDefensiveTroopsUnk) {
          return;
        }
      }
      else if (AVar5 == AIRUC_RAIDING) {
        iVar9 = getCurrentDesiredAttackRaidUnitCount(iVar1,playerID);
        pAVar10 = extraout_ECX;
        if (iVar9 <= DAT_GameState.playerDataArray[playerID].totalRaidingTroopsUnk) {
          return;
        }
      }
      else if ((AVar5 == AIRUC_ATTACKING) &&
              (DAT_GameState.playerDataArray[playerID].aiPlayerState != 0)) {
        return;
      }
                    /* DefDiggingUnitMax */
                    /* DefDiggingUnitMax */
      if (((*(int *)((int)pAVar10 + iVar1 * 0x2a4 + 0x15c) != 0) &&
          (iVar9 = Map::TileMapState::countUnfinishedMoatTilesForPlayer(&DAT_TileMapState,playerID),
          iVar9 != 0)) &&
         ((iVar9 = (int)DAT_GameState.playerDataArray[playerID].aiTribeIDs[10], iVar9 == 0 ||
          ((DAT_GameState.playerDataArray[playerID].aiTribeUIDs[10] !=
            DAT_TribesState.tribes[iVar9].uid ||
           ((int)DAT_TribesState.tribes[iVar9].size < *(int *)((int)pAVar10 + iVar1 * 0x2a4 + 0x15c)
           )))))) {
        bVar7 = true;
      }
      playerID = 0;
      if (0 < local_8) {
        do {
          if (bVar7) {
            if (((byte)SEC_RNG.currentNumber2 & 1) != 0) {
              bVar7 = false;
              goto LAB_004d3cc1;
            }
            if (DAT_GameState.playerDataArray[playerID_00].barracks.id == 0) {
              if (DAT_GameState.playerDataArray[playerID_00].mercenaryPost.id == 0) {
                return;
              }
                    /* DefDiggingUnit */
              unitType = *(UnitType *)((int)pAVar10 + iVar1 * 0x2a4 + 0x160);
            }
            else {
                    /* DefDiggingUnit */
              unitType = *(UnitType *)((int)pAVar10 + iVar1 * 0x2a4 + 0x160);
            }
          }
          else {
LAB_004d3cc1:
            AVar5 = DAT_GameState.playerDataArray[playerID_00].aiRecruitUnitChoiceState;
            if (AVar5 == AIRUC_DEFENSIVE) {
              if (7 < DAT_GameState.playerDataArray[playerID_00].aiDefUnitChoiceIndex) {
                DAT_GameState.playerDataArray[playerID_00].aiDefUnitChoiceIndex = 0;
              }
                    /* DefUnit 1 up to 8 */
              if (*(int *)((int)&DAT_AICState +
                          (DAT_GameState.playerDataArray[playerID_00].aiDefUnitChoiceIndex + iVar8)
                          * 4 + 0x184) == 0) {
                DAT_GameState.playerDataArray[playerID_00].aiDefUnitChoiceIndex = 0;
              }
              iVar9 = DAT_GameState.playerDataArray[playerID_00].aiDefUnitChoiceIndex;
                    /* DefUnit 1 up to 8 */
              unitType = *(UnitType *)((int)&DAT_AICState + (iVar8 + iVar9) * 4 + 0x184);
              DAT_GameState.playerDataArray[playerID_00].aiDefUnitChoiceIndex = iVar9 + 1;
            }
            else if (AVar5 == AIRUC_RAIDING) {
              if (7 < DAT_GameState.playerDataArray[playerID_00].aiRaidUnitChoiceIndex) {
                DAT_GameState.playerDataArray[playerID_00].aiRaidUnitChoiceIndex = 0;
              }
              if (*(int *)((int)&DAT_AICState +
                          (DAT_GameState.playerDataArray[playerID_00].aiRaidUnitChoiceIndex + iVar8)
                          * 4 + 0x1ac) == 0) {
                DAT_GameState.playerDataArray[playerID_00].aiRaidUnitChoiceIndex = 0;
              }
              iVar9 = DAT_GameState.playerDataArray[playerID_00].aiRaidUnitChoiceIndex;
              unitType = *(UnitType *)((int)&DAT_AICState + (iVar8 + iVar9) * 4 + 0x1ac);
              DAT_GameState.playerDataArray[playerID_00].aiRaidUnitChoiceIndex = iVar9 + 1;
            }
            else if (AVar5 == AIRUC_ATTACKING) {
              _pAICState = (AICState *)
                           randomlySelectAttackUnitTypeToRecruit(&DAT_AICState,playerID_00);
              unitType = getUnitTypeForUnitBehaviourType
                                   (&DAT_AICState,playerID_00,(AIUnitBehaviourType)_pAICState);
            }
          }
          if (unitType == 0) {
            return;
          }
          if (unitType == UT_E_ENGINEER) {
            iVar9 = DAT_GameState.playerDataArray[playerID_00].engineersGuild.id;
          }
          else if (unitType == UT_E_LADDER) {
            iVar9 = DAT_GameState.playerDataArray[playerID_00].engineersGuild.id;
          }
          else if (unitType == UT_TUNNELER) {
            iVar9 = DAT_GameState.playerDataArray[playerID_00].tunnelersGuild.id;
          }
          else if (unitType == UT_E_MONK) {
            iVar9 = Map::Buildings::BuildingsState::findFirstBuildingIDForPlayerAndType
                              (&DAT_BuildingsState,playerID_00,BT_CATHEDRAL);
          }
          else if ((int)unitType < 0x46) {
            iVar9 = DAT_GameState.playerDataArray[playerID_00].barracks.id;
          }
          else {
            iVar9 = DAT_GameState.playerDataArray[playerID_00].mercenaryPost.id;
          }
          if (iVar9 == 0) {
            return;
          }
          if ((((unitType == UT_E_ENGINEER) || (unitType == UT_E_LADDER)) ||
              (unitType == UT_TUNNELER)) || ((unitType == UT_E_MONK || (0x45 < (int)unitType)))) {
            iVar9 = Map::Units::UnitsState::nonEuroRecruit
                              (&DAT_UnitsState,unitType,iVar9,playerID_00,0);
          }
          else {
            iVar9 = Map::Units::UnitsState::euroRecruit
                              (&DAT_UnitsState,unitType,iVar9,playerID_00,0);
          }
          if (iVar9 == 0) {
                    /* tradeAmountEquipment */
            iVar1 = *(int *)((int)pAVar10 + iVar1 * 0x2a4 + 0x9c);
            if (iVar1 < 1) {
              return;
            }
            if (DAT_UnitsState.DAT_EuroUnitAcquisitionFailReason != 2) {
              return;
            }
            if (DAT_GameState.playerDataArray[playerID_00].aiNervousActionsTracker < 1) {
              DAT_GameState.playerDataArray[playerID_00].resourcesToAcquireArray
              [DAT_UnitsState.DAT_EuroUnitRequiredResource] = iVar1;
              return;
            }
            DAT_GameState.playerDataArray[playerID_00].resourcesToAcquireArray
            [DAT_UnitsState.DAT_EuroUnitRequiredResource] = 5;
            return;
          }
          if (bVar7) {
                    /* digging units? */
            aiAddUnitToMoatDiggerTribe(&DAT_AICState,iVar9);
          }
          else {
            AVar5 = DAT_GameState.playerDataArray[playerID_00].aiRecruitUnitChoiceState;
                    /* 0 = defensive, 1 = raid, 2 = army */
            if (AVar5 == AIRUC_DEFENSIVE) {
              if (DAT_GameState.playerDataArray[playerID_00].totalDefensiveTroopsUnk <
                  *(int *)((int)pAVar10 + iVar1 * 0x2a4 + 0x180)) {
                assignUnitToATribe(&DAT_AICState,iVar9);
              }
              else {
                addUnitToSmallestPatrolTribe(&DAT_AICState,iVar9);
              }
            }
            else if (AVar5 == AIRUC_RAIDING) {
              aiAssignUnitToDefensiveTribe(&DAT_AICState,iVar9);
            }
            else if (AVar5 == AIRUC_ATTACKING) {
              addUnitToItsTribe(&DAT_AICState,iVar9,(int)_pAICState);
            }
          }
          playerID = playerID + 1;
          if (local_8 <= playerID) {
            return;
          }
        } while( true );
      }
    }
  }
  return;
}


// ================= _HoldStrong::Map::Units::UnitsState::euroRecruit @ 0052e960 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::Units::UnitsState::euroRecruit
          (UnitsState *this,int unitType,undefined4 playersBarracksID,int playerID,int param_4)

{
  int *piVar1;
  UnitStateShort UVar2;
  ResourceType resourceType;
  ResourceType resourceType_00;
  ResourceType resourceType_01;
  int iVar3;
  ResourceType RVar4;
  UnitStateUnion *pUVar5;
  int unitID;
  ResourceTypeInt _unitCost;
  
                    /* archer is unittype 0x16 */
  DAT_UnitsState.DAT_EuroUnitAcquisitionFailReason = 0;
  _unitCost = DAT_TroopDefinedData.MarketResourceCycleArray[unitType + -1];
  resourceType = DAT_UnitPropertiesDefinedData.DAT_MELEE_DAMAGE[0x4e][unitType * 4 + 0x49];
                    /* fixme: always 0 strange */
  resourceType_00 = DAT_UnitPropertiesDefinedData.DAT_MELEE_DAMAGE[0x4e][unitType * 4 + 0x4a];
                    /* bug: if unitType was 0, then it became -0x16, which results in requiring wood
                       for creating this unit. This is nonsensical. It is wood because it will
                       access memory DAT_MELEE_DAMAGE_MATRIX[78][72], which happens to be 2 */
  resourceType_01 = DAT_UnitPropertiesDefinedData.DAT_MELEE_DAMAGE[0x4e][unitType * 4 + 0x48];
  iVar3 = DAT_UnitPropertiesDefinedData.DAT_MELEE_DAMAGE[0x4e][unitType * 4 + 0x4b];
  if ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
     (DAT_GameSynchronyState.skirmishTroopsCostGold == 0)) {
    _unitCost = 0;
  }
  if (DAT_GameState.playerDataArray[playerID].currentResources[0xf] < (int)_unitCost) {
    DAT_UnitsState.DAT_EuroUnitAcquisitionFailReason = 1;
                    /* if we do not have the gold resources */
    return 0;
  }
  if ((0 < DAT_GameState.playerDataArray[playerID].currentResources[resourceType_01]) ||
     (RVar4 = resourceType_01, (int)resourceType_01 < 1)) {
    if ((DAT_GameState.playerDataArray[playerID].currentResources[resourceType] < 1) &&
       (0 < (int)resourceType)) {
      DAT_UnitsState.DAT_EuroUnitAcquisitionFailReason = 2;
      DAT_UnitsState.DAT_EuroUnitRequiredResource = resourceType;
                    /* if we do not own the required armor */
      return 0;
    }
    if ((0 < DAT_GameState.playerDataArray[playerID].currentResources[resourceType_00]) ||
       (RVar4 = resourceType_00, (int)resourceType_00 < 1)) {
      if (iVar3 == -1) {
        Game::GameStateStructures::recountStablesAndHorses(&DAT_GameState);
        if (DAT_GameState.playerDataArray[playerID].availableHorses < 1) {
          DAT_UnitsState.DAT_EuroUnitAcquisitionFailReason = 4;
          return 0;
        }
      }
      unitID = 1;
      if (1 < (int)DAT_UnitsState.maxUnitCount) {
        pUVar5 = &DAT_UnitsState.units[1].state;
        do {
          if ((((pUVar5[-0x119].generic == UT_PEASANT) &&
               ((short)pUVar5[-0x115].generic == playerID)) && (pUVar5[-0x10].generic == 0)) &&
             (pUVar5[-0x11a].generic == ULS_NORMAL)) {
            UVar2 = pUVar5->generic;
            if ((((UVar2 != US_RELOAD_WEAPONUnk) && (UVar2 != US_AIM_WEAPONUnk)) &&
                ((UVar2 != US_JESTER_ROAM_TO && (UVar2 != US_MELEE_ATTACK)))) &&
               ((UVar2 != US_DETERMINE_NEXT_STATEUnk || (pUVar5[0x59].generic == 0)))) {
              if (param_4 != 0) {
                return 1;
              }
              DAT_UnitsState.units[unitID].unitTypeToChangeInto = (UnitTypeShort)unitType;
              DAT_UnitsState.units[unitID].engineerManningSiegeStateRef_checkType = 1;
              DAT_UnitsState.units[unitID].isDisappearingUnk = 1;
              DAT_UnitsState.units[unitID].state_2 = 0;
              DAT_UnitsState.units[unitID].state.generic = US_JESTER_ROAM_TO;
              DAT_UnitsState.units[unitID].disappearFadeAlphaCountdown = 0;
              DAT_UnitsState.units[unitID].cachedState = US_DETERMINE_NEXT_STATEUnk;
              piVar1 = DAT_GameState.playerDataArray[playerID].currentResources + 0xf;
              *piVar1 = *piVar1 - _unitCost;
              Buildings::BuildingsState::processResourceLoss
                        (&DAT_BuildingsState,playerID,resourceType_01,1,0);
              Buildings::BuildingsState::processResourceLoss
                        (&DAT_BuildingsState,playerID,resourceType,1,0);
              Buildings::BuildingsState::processResourceLoss
                        (&DAT_BuildingsState,playerID,resourceType_00,1,0);
              if (iVar3 == -1) {
                iVar3 = Game::GameStateStructures::linkageBetweenHorseUnitAndStableUnk
                                  (&DAT_GameState,playerID,unitID);
                DAT_UnitsState.units[unitID].horseOriginStablesBuildingIndexUnk = (short)iVar3;
                *(int *)&DAT_UnitsState.units[unitID].horseOriginStableIDUnk =
                     DAT_BuildingsState.buildings[iVar3].uid;
              }
              piVar1 = DAT_GameSynchronyState.finalResults.finalTroopsProduced + playerID;
              *piVar1 = *piVar1 + 1;
              TribesState::aiAssignNewUnitToTribe(&DAT_TribesState,playerID,unitType,unitID);
              return unitID;
            }
          }
          unitID = unitID + 1;
                    /* 0x248 = 584, which is half of 1168. basically: go to next unit */
          pUVar5 = pUVar5 + 0x248;
        } while (unitID < (int)DAT_UnitsState.maxUnitCount);
      }
      DAT_UnitsState.DAT_EuroUnitAcquisitionFailReason = 3;
                    /* units not allowed? over max amount units? */
      return 0;
    }
  }
  DAT_UnitsState.DAT_EuroUnitAcquisitionFailReason = 2;
  DAT_UnitsState.DAT_EuroUnitRequiredResource = RVar4;
                    /* we don't own the weapon required */
  return 0;
}


// ================= _HoldStrong::Map::Units::UnitsState::nonEuroRecruit @ 0052ec10 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::Units::UnitsState::nonEuroRecruit
          (UnitsState *this,UnitType unitType,undefined4 recruitmentBuilding,int playerID,
          int param_4)

{
  int *piVar1;
  UnitStateShort UVar2;
  UnitStateUnion *pUVar3;
  int iVar4;
  int unitID;
  
  DAT_UnitsState.DAT_EuroUnitAcquisitionFailReason = 0;
  if (unitType == UT_E_ENGINEER) {
    iVar4 = 0x1e;
  }
  else {
                    /* is not engineer
                       is tunneler */
    if (unitType == UT_TUNNELER) {
      iVar4 = 0x1e;
    }
    else {
                    /* is ladderman */
      if (unitType == UT_E_LADDER) {
        iVar4 = 4;
      }
      else {
                    /* is monk */
        if (unitType == UT_E_MONK) {
          iVar4 = 10;
        }
        else {
                    /* is arabian archer */
          if (unitType == UT_A_ARCHER) {
            iVar4 = 0x4b;
          }
          else {
                    /* is slave */
            if (unitType == UT_A_SLAVE) {
              iVar4 = 5;
            }
            else {
                    /* is slinger */
              if (unitType == UT_A_SLINGER) {
                iVar4 = 0xc;
              }
              else {
                    /* is assassin */
                if (unitType == UT_A_ASSASSIN) {
                  iVar4 = 0x3c;
                }
                else {
                    /* is horse archer */
                  if (unitType == UT_A_HARCHER) {
                    iVar4 = 0x50;
                  }
                  else {
                    /* is arabian swordsman */
                    if (unitType == UT_A_SWORDSMAN) {
                      iVar4 = 0x50;
                    }
                    else {
                    /* is not firethrower */
                      if (unitType != UT_A_FIRETHROWER) {
                        return 0;
                      }
                      iVar4 = 100;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  piVar1 = DAT_GameState.playerDataArray[playerID].currentResources + 0xf;
                    /* Check if player has enough gold, then convert peasant to new unit */
  if (DAT_GameState.playerDataArray[playerID].currentResources[0xf] < iVar4) {
    DAT_UnitsState.DAT_EuroUnitAcquisitionFailReason = 1;
    return 0;
  }
  unitID = 1;
  if (1 < (int)DAT_UnitsState.maxUnitCount) {
    pUVar3 = &DAT_UnitsState.units[1].state;
    do {
      if (((((pUVar3[-0x119].generic == UT_PEASANT) && ((short)pUVar3[-0x115].generic == playerID))
           && (pUVar3[-0x10].generic == 0)) &&
          ((pUVar3[-0x11a].generic == ULS_NORMAL &&
           (UVar2 = pUVar3->generic, UVar2 != US_RELOAD_WEAPONUnk)))) &&
         ((UVar2 != US_AIM_WEAPONUnk && ((UVar2 != US_JESTER_ROAM_TO && (UVar2 != US_MELEE_ATTACK)))
          ))) {
        if (param_4 != 0) {
          return 1;
        }
        DAT_UnitsState.units[unitID].unitTypeToChangeInto = (UnitTypeShort)unitType;
        DAT_UnitsState.units[unitID].state_2 = 0;
        DAT_UnitsState.units[unitID].state.generic = US_JESTER_ROAM_TO;
        DAT_UnitsState.units[unitID].disappearFadeAlphaCountdown = 0;
        DAT_UnitsState.units[unitID].engineerManningSiegeStateRef_checkType = 1;
        DAT_UnitsState.units[unitID].cachedState = US_DETERMINE_NEXT_STATEUnk;
        DAT_UnitsState.units[unitID].isDisappearingUnk = 1;
        DAT_UnitsState.units[unitID].workplaceBuildingID_1 = (short)recruitmentBuilding;
        DAT_UnitsState.units[unitID].resourceToDeposit = 0;
        *piVar1 = *piVar1 - iVar4;
        piVar1 = DAT_GameSynchronyState.finalResults.finalTroopsProduced + playerID;
        *piVar1 = *piVar1 + 1;
        TribesState::aiAssignNewUnitToTribe(&DAT_TribesState,playerID,unitType,unitID);
        return unitID;
      }
      unitID = unitID + 1;
      pUVar3 = pUVar3 + 0x248;
    } while (unitID < (int)DAT_UnitsState.maxUnitCount);
  }
  DAT_UnitsState.DAT_EuroUnitAcquisitionFailReason = 3;
  return 0;
}


// Treffer: 16
