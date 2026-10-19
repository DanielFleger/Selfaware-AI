// ================= UpdateAppleTree @ 0x004f26c0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Map::Trees::UpdateAppleTree(void)

{
  int *piVar1;
  byte bVar2;
  short sVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  
  iVar4 = DAT_CurrentTreeID;
  if (DAT_LandscapeState.trees[DAT_CurrentTreeID].stage < 6) {
    piVar1 = &DAT_LandscapeState.trees[DAT_CurrentTreeID].stageTracker;
    *piVar1 = *piVar1 + 1;
    if (DAT_OrganismDefinedData.DAT_TreeStageLevels[0xf][DAT_LandscapeState.trees[iVar4].stage + 1]
        <= DAT_LandscapeState.trees[iVar4].stageTracker) {
      DAT_LandscapeState.trees[iVar4].stageTracker = 0;
      piVar1 = &DAT_LandscapeState.trees[iVar4].stage;
                    /* This updates the apple tree season state */
      *piVar1 = *piVar1 + 1;
      if (5 < DAT_LandscapeState.trees[iVar4].stage) {
        DAT_LandscapeState.trees[iVar4].stage = 0;
      }
    }
    uVar5 = DAT_LandscapeState.trees[iVar4].rng1 & 7;
    DAT_LandscapeState.trees[iVar4].appleTreeColorVariation = uVar5;
    iVar6 = DAT_LandscapeState.trees[iVar4].stage;
    if ((iVar6 == 0) && (DAT_LandscapeState.trees[iVar4].stageTracker < 0xfa)) {
      if (uVar5 == 0) {
        DAT_LandscapeState.trees[iVar4].appleTreeColorVariation = 2;
      }
      else {
LAB_004f274d:
        if (uVar5 == 1) {
          DAT_LandscapeState.trees[iVar4].appleTreeColorVariation = 4;
        }
        else {
          DAT_LandscapeState.trees[iVar4].appleTreeColorVariation = (uint)(uVar5 != 3) * 2 + 5;
        }
      }
    }
    else if (iVar6 == 5) {
      if (uVar5 != 0) goto LAB_004f274d;
      DAT_LandscapeState.trees[iVar4].appleTreeColorVariation = 2;
    }
    else if (uVar5 == 2) {
      DAT_LandscapeState.trees[iVar4].appleTreeColorVariation = 0;
    }
    else if (uVar5 == 4) {
      DAT_LandscapeState.trees[iVar4].appleTreeColorVariation = 1;
    }
    else {
      DAT_LandscapeState.trees[iVar4].appleTreeColorVariation = (-(uint)(uVar5 != 5) & 3) + 3;
    }
  }
  else {
    DAT_LandscapeState.trees[DAT_CurrentTreeID].appleTreeColorVariation = 0;
    piVar1 = &DAT_LandscapeState.trees[iVar4].stageTracker;
    *piVar1 = *piVar1 + 1;
    if (0x4b0 < DAT_LandscapeState.trees[iVar4].stageTracker) {
      DAT_LandscapeState.trees[iVar4].state = 3;
    }
  }
  sVar3 = DAT_LandscapeState.trees[iVar4].animationFrameIndex;
  if (DAT_LandscapeState.trees[iVar4].flag == FALSE) {
    bVar2 = DAT_OrganismDefinedData.ANIM_Tree_1_A[sVar3];
  }
  else {
    bVar2 = DAT_OrganismDefinedData.ANIM_Tree_1_B[sVar3];
  }
  if ((char)bVar2 < '\x01') {
    DAT_LandscapeState.trees[iVar4].animationFrameIndex = 0;
    DAT_LandscapeState.trees[iVar4].flag = (uint)(DAT_LandscapeState.trees[iVar4].one == 2);
  }
  switch(DAT_LandscapeState.trees[iVar4].stage) {
  case 0:
  case 6:
    sVar3 = DAT_LandscapeState.trees[iVar4].animationFrameIndex;
    if (DAT_LandscapeState.trees[iVar4].flag == FALSE) {
      iVar6 = (int)(char)DAT_OrganismDefinedData.ANIM_Tree_1_A[sVar3];
    }
    else {
      iVar6 = (int)(char)DAT_OrganismDefinedData.ANIM_Tree_1_B[sVar3];
    }
    break;
  case 1:
    sVar3 = DAT_LandscapeState.trees[iVar4].animationFrameIndex;
    if (DAT_LandscapeState.trees[iVar4].flag == FALSE) {
      iVar6 = (char)DAT_OrganismDefinedData.ANIM_Tree_1_A[sVar3] + 0x19;
    }
    else {
      iVar6 = (char)DAT_OrganismDefinedData.ANIM_Tree_1_B[sVar3] + 0x19;
    }
    break;
  case 2:
  case 4:
  case 5:
    sVar3 = DAT_LandscapeState.trees[iVar4].animationFrameIndex;
    if (DAT_LandscapeState.trees[iVar4].flag == FALSE) {
      iVar6 = (char)DAT_OrganismDefinedData.ANIM_Tree_1_A[sVar3] + 0x4b;
    }
    else {
      iVar6 = (char)DAT_OrganismDefinedData.ANIM_Tree_1_B[sVar3] + 0x4b;
    }
    break;
  case 3:
    sVar3 = DAT_LandscapeState.trees[iVar4].animationFrameIndex;
    if (DAT_LandscapeState.trees[iVar4].flag == FALSE) {
      bVar2 = DAT_OrganismDefinedData.ANIM_Tree_1_A[sVar3];
    }
    else {
      bVar2 = DAT_OrganismDefinedData.ANIM_Tree_1_B[sVar3];
    }
    iVar6 = (char)bVar2 + 0x32;
    break;
  default:
    goto switchD_004f281e_caseD_7;
  }
  DAT_LandscapeState.trees[iVar4].animationFrameUnk = iVar6;
switchD_004f281e_caseD_7:
  if (DAT_LandscapeState.field0_0x0 != 0) {
    DAT_LandscapeState.trees[iVar4].animationFrameUnk = 0;
  }
  return;
}



// ================= UpdateAppleFarmer @ 0x00553ae0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Global::UpdateAppleFarmer(void)

{
  byte *pbVar1;
  short *psVar2;
  int *piVar3;
  short sVar4;
  UnitStateShort UVar5;
  short sVar6;
  BOOLEnum BVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  bool bVar11;
  undefined6 uVar12;
  
  uVar9 = DAT_CurrentUnitSlotID;
  iVar10 = DAT_CurrentUnitSlotID * 0x490;
  sVar4 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].workplaceBuildingID_1;
  DAT_UnitsState.units[DAT_CurrentUnitSlotID].field171_0x300 = 1;
  UVar5 = DAT_UnitsState.units[uVar9].state.generic;
  if (UVar5 == US_DETERMINE_NEXT_STATEUnk) {
    if (DAT_UnitsState.units[uVar9].isDisappearingUnk != 0) {
      DAT_UnitsState.units[uVar9].gfxNumber = 1;
    }
    DAT_UnitsState.units[uVar9].resourcesGatheredCount = 0;
    sVar6 = DAT_UnitsState.units[uVar9].isDisappearingUnk;
    DAT_BuildingsState.buildings[sVar4].workers[DAT_UnitsState.units[uVar9].workerIndex] =
         (short)uVar9;
    if (sVar6 == 0) {
      if (DAT_UnitsState.units[uVar9].goToRallyPoint != 0) {
        DAT_UnitsState.units[uVar9].goToRallyPoint = 0;
LAB_00553b7c:
        DAT_UnitsState.units[uVar9].state.generic = US_AIM_WEAPONUnk;
        DAT_UnitsState.units[uVar9].destinationNeeded = 2;
        return;
      }
      iVar10 = Map::LandscapeState::selectClosestTree
                         (&DAT_LandscapeState,(int)DAT_UnitsState.units[uVar9].x,
                          (int)DAT_UnitsState.units[uVar9].y,0);
      uVar9 = DAT_CurrentUnitSlotID;
      if (iVar10 == 0) {
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_IDLEUnk;
        return;
      }
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = 2;
      DAT_UnitsState.units[uVar9].workplaceBuildingTilePosition = (short)iVar10;
      BVar7 = Map::Units::UnitsState::setDestinationForUnit
                        (&DAT_UnitsState,uVar9,DAT_LandscapeState.x,DAT_LandscapeState.y,0);
      if (BVar7 == FALSE) {
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_IDLEUnk;
        return;
      }
    }
    else {
      pbVar1 = &DAT_UnitsState.units[uVar9].disappearFadeAlphaCountdown;
      *pbVar1 = *pbVar1 - 1;
      if ((char)*pbVar1 < '\0') {
        DAT_UnitsState.units[uVar9].disappearFadeAlphaCountdown = 0;
        DAT_UnitsState.units[uVar9].isDisappearingUnk = 0;
        return;
      }
    }
  }
  else if (UVar5 == US_IDLEUnk) {
    DAT_UnitsState.units[uVar9].animationSpeed = 2;
    DAT_UnitsState.units[uVar9].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar9].field42_0x58 = 1;
    DAT_UnitsState.units[uVar9].field134_0x2ac = 1;
    iVar8 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                       DAT_AnimationAppleFarm[DAT_UnitsState.units[uVar9].animationCycleNumber];
    DAT_BuildingsState.buildings[sVar4].workers[DAT_UnitsState.units[uVar9].workerIndex] =
         (short)uVar9;
    DAT_UnitsState.units[uVar9].animationFrame = iVar8;
    iVar10 = DAT_UnitHasBecomeIdle;
    if (iVar8 < 1) {
      DAT_UnitsState.units[uVar9].gfxNumber = 0x301;
      DAT_UnitHasBecomeIdle = 1;
      iVar10 = 1;
    }
    else {
      DAT_UnitsState.units[uVar9].gfxNumber = iVar8 + 0x300;
    }
    iVar8 = SetStateToFreetimeWalking(uVar9,iVar10,0);
    if ((iVar8 == 0) && (iVar10 != 0)) {
      DAT_UnitsState.units[uVar9].animationCycleNumber = 0;
      DAT_UnitsState.units[uVar9].state.generic = US_DETERMINE_NEXT_STATEUnk;
      return;
    }
  }
  else if (UVar5 == 2) {
    IncrementAndOptionalUpdateAVValueRelated(uVar9,FALSE);
    DAT_UnitsState.units[uVar9].animationSheetFrameOffset = 1;
    DAT_UnitsState.units[uVar9].field_0x30_animRelated = 0x10;
    DAT_UnitsState.units[uVar9].animationCycleNumber = 0;
    BVar7 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,uVar9);
    if (BVar7 != FALSE) {
      if (DAT_LandscapeState.trees[DAT_UnitsState.units[uVar9].workplaceBuildingTilePosition].stage
          != 3) goto LAB_00553b7c;
LAB_00553d17:
      DAT_UnitsState.units[uVar9].state.generic = 3;
      return;
    }
  }
  else if (UVar5 == US_STAND_UPUnk) {
                    /* Gathering apples */
    IncrementAndOptionalUpdateAVValueRelated(uVar9,FALSE);
    DAT_UnitsState.units[uVar9].animationSheetFrameOffset = 0x411;
    DAT_UnitsState.units[uVar9].field_0x30_animRelated = 0x10;
    DAT_UnitsState.units[uVar9].animationCycleNumber = 0;
    BVar7 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,uVar9);
    if (BVar7 != FALSE) {
                    /* Do not gather fruits if the apple farm's season state is not 3 */
      if (DAT_LandscapeState.trees[DAT_UnitsState.units[uVar9].workplaceBuildingTilePosition].stage
          != 3) {
        DAT_UnitsState.units[uVar9].state.generic = US_RELOAD_WEAPONUnk;
        DAT_UnitsState.units[uVar9].destinationNeeded = 2;
        return;
      }
      goto LAB_00553d17;
    }
  }
  else {
    if (UVar5 == 3) {
      DAT_UnitsState.units[uVar9].field_0x30_animRelated = 0;
      IncrementAndOptionalUpdateAVValueRelated(uVar9,FALSE);
      iVar10 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          field261_0x4f40[DAT_UnitsState.units[uVar9].animationCycleNumber];
      DAT_UnitsState.units[uVar9].animationFrame = iVar10;
      if (iVar10 < 1) {
        DAT_UnitsState.units[uVar9].gfxNumber =
             DAT_UnitsState.units[uVar9].facingDirectionMapOrientationCorrected + 0x491;
        DAT_UnitHasBecomeIdle = 1;
      }
      else {
        bVar11 = DAT_UnitHasBecomeIdle == 0;
        DAT_UnitsState.units[uVar9].gfxNumber =
             DAT_UnitsState.units[uVar9].facingDirectionMapOrientationCorrected + 0x489 + iVar10 * 8
        ;
        if (bVar11) {
          return;
        }
      }
      DAT_UnitsState.units[uVar9].animationCycleNumber = 0;
      psVar2 = &DAT_UnitsState.units[uVar9].resourcesGatheredCount;
      *psVar2 = *psVar2 + 1;
      sVar4 = DAT_UnitsState.units[uVar9].resourcesGatheredCount;
      if (sVar4 < 4) {
        iVar10 = Map::LandscapeState::selectClosestTree
                           (&DAT_LandscapeState,(int)DAT_UnitsState.units[uVar9].x,
                            (int)DAT_UnitsState.units[uVar9].y,(int)sVar4);
        uVar9 = DAT_CurrentUnitSlotID;
        if (iVar10 != 0) {
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_STAND_UPUnk;
          DAT_UnitsState.units[uVar9].workplaceBuildingTilePosition = (short)iVar10;
          Map::Units::UnitsState::setDestinationForUnit
                    (&DAT_UnitsState,uVar9,DAT_LandscapeState.x,DAT_LandscapeState.y,0);
          return;
        }
      }
      else {
        DAT_UnitsState.units[uVar9].updateTickTracker = 0;
        iVar10 = Map::Buildings::BuildingsState::getBuildingThatCanStoreThisResource
                           (&DAT_BuildingsState,RT_APPLE,1,(int)DAT_UnitsState.units[uVar9].owner);
        if ((iVar10 == 0) &&
           (DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner ==
            DAT_GameSynchronyState.currentPlayerSlotID)) {
          WarnIfPlayersGranaryIsFull();
        }
        iVar8 = Map::Buildings::BuildingsState::buildingIsAccessible(&DAT_BuildingsState,iVar10,1);
        uVar9 = DAT_CurrentUnitSlotID;
        if (iVar8 != 0) {
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetID_OR_targetBuildingID = (short)iVar10;
          DAT_UnitsState.units[uVar9].targetUID = DAT_BuildingsState.buildings[iVar10].uid;
          BVar7 = Map::Units::UnitsState::setDestinationForUnit
                            (&DAT_UnitsState,uVar9,
                             (int)DAT_BuildingsState.buildings[iVar10].buildingEntryX,
                             (int)DAT_BuildingsState.buildings[iVar10].buildingEntryY,0);
          uVar9 = DAT_CurrentUnitSlotID;
          if (BVar7 != FALSE) {
LAB_00554170:
                    /* DAT_UnitsState.SEC_Units[0].state */
            DAT_UnitsState.units[uVar9].state.generic = US_LOOK_AROUNDUnk;
            iVar10 = ComputeGoodsProduced(uVar9,3,TRUE);
                    /* DAT_UnitsState.SEC_Units[0].resourceToDeposit */
            DAT_UnitsState.units[uVar9].resourceToDeposit = (short)iVar10;
            return;
          }
        }
      }
      uVar9 = DAT_CurrentUnitSlotID;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_RELOAD_WEAPONUnk;
      DAT_UnitsState.units[uVar9].destinationNeeded = DNE_DESTINATION_NEEDED;
      return;
    }
    if (UVar5 == US_RELOAD_WEAPONUnk) {
      IncrementAndOptionalUpdateAVValueRelated(uVar9,FALSE);
      if (DAT_UnitsState.units[uVar9].destinationNeeded != DNE_DESTINATION_HAS_BEEN_SET) {
        Map::Units::UnitsState::setDestinationForUnit
                  (&DAT_UnitsState,uVar9,(int)DAT_UnitsState.units[uVar9].targetX_2,
                   (int)DAT_UnitsState.units[uVar9].targetY_2,0);
        uVar9 = DAT_CurrentUnitSlotID;
        iVar10 = DAT_CurrentUnitSlotID * 0x490;
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].destinationNeeded = DNE_DESTINATION_HAS_BEEN_SET
        ;
      }
      *(undefined4 *)((int)&DAT_UnitsState.units[0].animationSheetFrameOffset + iVar10) = 0x411;
      *(undefined4 *)((int)&DAT_UnitsState.units[0].field_0x30_animRelated + iVar10) = 0x10;
      *(undefined4 *)((int)DAT_UnitsState.units[0].manningEngineerRef + iVar10 + -100) = 0;
      BVar7 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,uVar9);
      if (BVar7 != FALSE) {
        *(undefined2 *)((int)DAT_UnitsState.units[0].manningEngineerRef + iVar10 + -0x54) = 6;
        return;
      }
    }
    else if (UVar5 == US_AIM_WEAPONUnk) {
                    /* Going to workplace */
      IncrementAndOptionalUpdateAVValueRelated(uVar9,FALSE);
      if (DAT_UnitsState.units[uVar9].destinationNeeded != DNE_DESTINATION_HAS_BEEN_SET) {
        BVar7 = ConsiderTakingABreakUnk(uVar9);
        if (BVar7 != FALSE) {
          return;
        }
        BVar7 = Map::Units::UnitsState::setDestinationForUnit
                          (&DAT_UnitsState,uVar9,(int)DAT_UnitsState.units[uVar9].targetX_2,
                           (int)DAT_UnitsState.units[uVar9].targetY_2,0);
        uVar9 = DAT_CurrentUnitSlotID;
        if (BVar7 == FALSE) {
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_DISAPPEAR;
          DAT_UnitsState.units[uVar9].updateTickTracker = 0;
          return;
        }
        iVar10 = DAT_CurrentUnitSlotID * 0x490;
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].destinationNeeded = DNE_DESTINATION_HAS_BEEN_SET
        ;
      }
      *(undefined4 *)((int)&DAT_UnitsState.units[0].animationSheetFrameOffset + iVar10) = 1;
      *(undefined4 *)((int)&DAT_UnitsState.units[0].field_0x30_animRelated + iVar10) = 0x10;
      *(undefined4 *)((int)DAT_UnitsState.units[0].manningEngineerRef + iVar10 + -100) = 0;
      BVar7 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,uVar9);
      if (BVar7 != FALSE) {
        *(undefined2 *)((int)DAT_UnitsState.units[0].manningEngineerRef + iVar10 + -0x54) = 0;
        return;
      }
    }
    else if (UVar5 == US_FIRE_WEAPONUnk) {
      DAT_UnitsState.units[uVar9].animationSheetFrameOffset = 0x411;
      DAT_UnitsState.units[uVar9].field_0x30_animRelated = 0x10;
      DAT_UnitsState.units[uVar9].field134_0x2ac = 1;
      psVar2 = &DAT_UnitsState.units[uVar9].updateTickTracker;
      *psVar2 = *psVar2 + 1;
      if (10 < DAT_UnitsState.units[uVar9].updateTickTracker) {
        DAT_UnitsState.units[uVar9].updateTickTracker = 0;
        iVar10 = Map::Buildings::BuildingsState::getBuildingThatCanStoreThisResource
                           (&DAT_BuildingsState,RT_APPLE,1,(int)DAT_UnitsState.units[uVar9].owner);
        if ((iVar10 == 0) &&
           (DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner ==
            DAT_GameSynchronyState.currentPlayerSlotID)) {
          WarnIfPlayersGranaryIsFull();
        }
        iVar8 = Map::Buildings::BuildingsState::buildingIsAccessible(&DAT_BuildingsState,iVar10,1);
        if ((iVar8 != 0) &&
           (BVar7 = Map::Units::UnitsState::setDestinationForUnit
                              (&DAT_UnitsState,DAT_CurrentUnitSlotID,
                               (int)DAT_BuildingsState.buildings[iVar10].buildingEntryX,
                               (int)DAT_BuildingsState.buildings[iVar10].buildingEntryY,0),
           uVar9 = DAT_CurrentUnitSlotID, BVar7 != FALSE)) {
          iVar8 = DAT_BuildingsState.buildings[iVar10].uid;
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetID_OR_targetBuildingID = (short)iVar10;
          DAT_UnitsState.units[uVar9].targetUID = iVar8;
          goto LAB_00554170;
        }
      }
    }
    else if (UVar5 == US_LOOK_AROUNDUnk) {
                    /* Taking resource to granary */
      IncrementAndOptionalUpdateAVValueRelated(uVar9,FALSE);
      DAT_UnitsState.units[uVar9].animationSheetFrameOffset = 0x411;
      DAT_UnitsState.units[uVar9].field_0x30_animRelated = 0x10;
      psVar2 = &DAT_UnitsState.units[uVar9].updateTickTracker;
      *psVar2 = *psVar2 + 1;
      if ((4 < DAT_UnitsState.units[uVar9].updateTickTracker) &&
         (BVar7 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,uVar9),
         BVar7 != FALSE)) {
        DAT_UnitsState.units[uVar9].updateTickTracker = 0;
        iVar10 = Map::Buildings::BuildingsState::getResourceCountThatCanBeDeposited
                           ((int)DAT_UnitsState.units[uVar9].targetID_OR_targetBuildingID,0xd,0xfa);
        if (iVar10 == 0) {
                    /* building ID for storage building */
          iVar10 = Map::Buildings::BuildingsState::getBuildingThatCanStoreThisResource
                             (&DAT_BuildingsState,RT_APPLE,1,
                              (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner);
          iVar8 = Map::Buildings::BuildingsState::buildingIsAccessible(&DAT_BuildingsState,iVar10,1)
          ;
          uVar9 = DAT_CurrentUnitSlotID;
          if (iVar8 == 0) {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].resourceToDeposit = 0;
          }
          else {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetID_OR_targetBuildingID = (short)iVar10
            ;
            DAT_UnitsState.units[uVar9].targetUID = DAT_BuildingsState.buildings[iVar10].uid;
            BVar7 = Map::Units::UnitsState::setDestinationForUnit
                              (&DAT_UnitsState,uVar9,
                               (int)DAT_BuildingsState.buildings[iVar10].buildingEntryX,
                               (int)DAT_BuildingsState.buildings[iVar10].buildingEntryY,0);
            if (BVar7 == FALSE) {
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].resourceToDeposit = 0;
            }
          }
        }
        else {
          Map::Buildings::BuildingsState::addResourceToStockpile
                    (&DAT_BuildingsState,
                     (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetID_OR_targetBuildingID,
                     DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetUID,RT_APPLE,1,0xfa,1);
          uVar9 = DAT_CurrentUnitSlotID;
          piVar3 = DAT_GameSynchronyState.finalResults.finalFoodProduced +
                   DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner;
          *piVar3 = *piVar3 + 1;
          psVar2 = &DAT_UnitsState.units[uVar9].resourceToDeposit;
          *psVar2 = *psVar2 + -1;
          Audio::SFX::SFXState::playSFXAtLocation
                    (&DAT_SFXState,(int)DAT_UnitsState.units[uVar9].x,
                     (int)DAT_UnitsState.units[uVar9].y,FX_STOCK_FOOD);
        }
        uVar9 = DAT_CurrentUnitSlotID;
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].resourceToDeposit < 1) {
          IncrementAndOptionalUpdateAVValueRelated(DAT_CurrentUnitSlotID,TRUE);
          DAT_UnitsState.units[uVar9].state.generic = US_AIM_WEAPONUnk;
          DAT_UnitsState.units[uVar9].destinationNeeded = DNE_DESTINATION_NEEDED;
          return;
        }
      }
    }
    else {
      if (UVar5 == (US_DEATH_02|US_STAND_UPUnk|US_IDLEUnk)) {
        DAT_UnitsState.units[uVar9].animationSheetFrameOffset = 1;
        DAT_UnitsState.units[uVar9].field_0x30_animRelated = 0x10;
        SetRestingForUnit(uVar9);
        return;
      }
      if (UVar5 == 0x6c) {
        DAT_UnitsState.units[uVar9].stateBasedSpeed = 0;
        DAT_UnitsState.units[uVar9].field_0x30_animRelated = 0;
        DAT_UnitsState.units[uVar9].animationSheetFrameOffset = 1;
        return;
      }
      if (UVar5 == US_DEATH_01) {
        DAT_UnitsState.units[uVar9].facingDirection = 0;
        DAT_UnitsState.units[uVar9].animationSpeed = 2;
        DAT_UnitsState.units[uVar9].field_0x30_animRelated = 0;
        iVar10 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                            ANIM_Worker_Shared1[DAT_UnitsState.units[uVar9].animationCycleNumber];
        DAT_UnitsState.units[uVar9].animationFrame = iVar10;
        if (iVar10 < 1) {
          DAT_UnitsState.units[uVar9].gfxNumber = 0x5a0;
          DAT_UnitsState.units[uVar9].state.generic = US_DISAPPEAR;
          DAT_UnitHasBecomeIdle = 1;
          return;
        }
        iVar10 = iVar10 + 0x588;
      }
      else {
        uVar12 = Map::Units::UnitsState::checkIfCitizenUnitIsAliveBasedOnState(uVar9);
        if ((int)uVar12 == 0) {
          if ((short)((uint6)uVar12 >> 0x20) != 0x6e) {
            DAT_UnitsState.units[uVar9].state.generic = US_DETERMINE_NEXT_STATEUnk;
            Map::Units::UnitsState::makeUnitStopWalkingByClearingPathProgressState(uVar9);
            return;
          }
          pbVar1 = &DAT_UnitsState.units[uVar9].disappearFadeAlphaCountdown;
          *pbVar1 = *pbVar1 + 1;
          if (' ' < (char)DAT_UnitsState.units[uVar9].disappearFadeAlphaCountdown) {
            DAT_UnitsState.units[uVar9].disappearFadeAlphaCountdown = 0x20;
          }
          psVar2 = &DAT_UnitsState.units[uVar9].updateTickTracker;
          *psVar2 = *psVar2 + 1;
          if ((0x20 < DAT_UnitsState.units[uVar9].updateTickTracker) &&
             (DAT_UnitsState.units[uVar9].logicalState = ULS_REMOVE,
             DAT_UnitsState.units[uVar9].killedFlagUnk == 0)) {
            Game::GameStateStructures::setLastEncounteredTroopUnit
                      (&DAT_GameState,(int)DAT_UnitsState.units[uVar9].owner,uVar9);
            uVar9 = DAT_CurrentUnitSlotID;
          }
          DAT_BuildingsState.buildings[DAT_UnitsState.units[uVar9].workplaceBuildingID_1].
          idleTimerUnk = 4000;
          return;
        }
        DAT_UnitsState.units[uVar9].facingDirection = 0;
        DAT_UnitsState.units[uVar9].animationSpeed = 2;
        DAT_UnitsState.units[uVar9].field_0x30_animRelated = 0;
        iVar10 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                            ANIM_Worker_Shared1[DAT_UnitsState.units[uVar9].animationCycleNumber];
        DAT_UnitsState.units[uVar9].animationFrame = iVar10;
        if (iVar10 < 1) {
          DAT_UnitsState.units[uVar9].gfxNumber = 0x588;
          DAT_UnitsState.units[uVar9].state.generic = US_DISAPPEAR;
          DAT_UnitHasBecomeIdle = 1;
          return;
        }
        iVar10 = iVar10 + 0x570;
      }
      bVar11 = DAT_UnitHasBecomeIdle != 0;
      DAT_UnitsState.units[uVar9].gfxNumber = iVar10;
      if (bVar11) {
        DAT_UnitsState.units[uVar9].state.generic = US_DISAPPEAR;
        return;
      }
    }
  }
  return;
}



// ================= placeAppleTree @ 0x004f3560 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Map::LandscapeState::placeAppleTree
               (int buildingID,undefined4 treeX,undefined4 treeY)

{
  int iVar1;
  uint uVar2;
  int treeID;
  
  treeID = createTree(&DAT_LandscapeState,treeX,treeY,TT_APPLEUnk,1,0,0,0);
  if (treeID != 0) {
    DAT_LandscapeState.trees[treeID].appleFarmID = (short)buildingID;
    iVar1 = DAT_BuildingsState.buildings[buildingID].uid;
    DAT_LandscapeState.trees[treeID].stageTracker = DAT_LandscapeState.trees[treeID].rng1 & 0x1f;
    uVar2 = DAT_LandscapeState.trees[treeID].tile;
    DAT_TileMapState.LogicLayer[uVar2] = DAT_TileMapState.LogicLayer[uVar2] | 0x1000;
    DAT_TileMapState.OrganismLayer[uVar2] = (ushort)treeID;
    DAT_LandscapeState.trees[treeID].appleFarmUID = iVar1;
    TileMapState::applyTreeBrushToLogicalLayer(&DAT_TileMapState,treeID,0);
    Navigation::PathFindingState::updatePathLinkagesInAllEightDirections
              (&DAT_PathFindingState,(int)(short)DAT_LandscapeState.trees[treeID].yPosition,
               DAT_LandscapeState.trees[treeID].tile);
    DAT_PathFindingState.toggleUpdateSeparateAreaTileMap = 1;
  }
  return;
}



// ================= UpdateAppleFarm @ 0x00416720 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Global::UpdateAppleFarm(void)

{
  int *piVar1;
  short sVar2;
  int iVar3;
  bool bVar4;
  
  iVar3 = DAT_CurrentBuildingID;
  sVar2 = DAT_BuildingsState.buildings[DAT_CurrentBuildingID].owner;
  piVar1 = &DAT_GameState.playerDataArray[sVar2].countFarms;
  *piVar1 = *piVar1 + 1;
  if (DAT_BuildingsState.buildings[iVar3].workers[0] == 0) {
    piVar1 = &DAT_GameState.playerDataArray[sVar2].farmsWithoutWorkers;
    *piVar1 = *piVar1 + 1;
  }
  AI::AICState::addBuildingToTargetableBuildings(&DAT_AICState,iVar3);
  Game::GameStateStructures::addBuildingInRegistry(&DAT_GameState,DAT_CurrentBuildingID);
  iVar3 = DAT_CurrentBuildingID;
  bVar4 = DAT_GameSynchronyState.currentGameMode != GM_SOLITARY;
  DAT_BuildingsState.buildings[DAT_CurrentBuildingID].renderAnimation = 0;
  if (bVar4) {
    DAT_BuildingsState.buildings[iVar3].displayOwnerFlag = 1;
    piVar1 = &DAT_BuildingsState.buildings[iVar3].ownerFlagFrame;
    *piVar1 = *piVar1 + 1;
    if ((char)DAT_BuildingDefinedData.field177_0x7e1c
              [DAT_BuildingsState.buildings[iVar3].ownerFlagFrame / 2] < '\x01') {
      DAT_BuildingsState.buildings[iVar3].ownerFlagFrame = 0;
    }
    DAT_BuildingsState.buildings[iVar3].field39_0x84 =
         (int)(char)DAT_BuildingDefinedData.field177_0x7e1c
                    [DAT_BuildingsState.buildings[iVar3].ownerFlagFrame / 2];
    return;
  }
  DAT_BuildingsState.buildings[iVar3].field39_0x84 = 0;
  return;
}



// ================= setBuildingToAppleFarm @ 0x0040f3d0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Buildings::BuildingsState::setBuildingToAppleFarm
          (BuildingsState *this,int buildingID)

{
  DAT_BuildingsState.buildings[buildingID].field66_0xbe = 0x20;
  return;
}



