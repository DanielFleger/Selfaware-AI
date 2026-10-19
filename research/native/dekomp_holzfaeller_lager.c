// ================= UpdateWoodcutter @ 0x0054c710 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum _HoldStrong::Global::UpdateWoodcutter(void)

{
  byte *pbVar1;
  int *piVar2;
  undefined1 *puVar3;
  short *psVar4;
  UnitStateShort UVar5;
  short sVar6;
  ushort uVar7;
  BOOLEnum BVar8;
  BOOLEnum extraout_EAX;
  BOOLEnum BVar9;
  BOOL BVar10;
  uint uVar11;
  BOOLEnum extraout_EAX_00;
  BOOLEnum extraout_EAX_01;
  BOOLEnum extraout_EAX_02;
  BOOLEnum extraout_EAX_03;
  ushort uVar12;
  short sVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  bool bVar17;
  undefined6 uVar18;
  eSFX sfxOffsetInArray;
  
  uVar11 = DAT_CurrentUnitSlotID;
  iVar16 = DAT_CurrentUnitSlotID * 0x490;
  iVar15 = (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].workplaceBuildingTilePosition;
  iVar14 = (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].workplaceBuildingID_1;
  DAT_UnitsState.units[DAT_CurrentUnitSlotID].field171_0x300 = 10;
  UVar5 = DAT_UnitsState.units[uVar11].state.generic;
  BVar8 = FALSE;
  if (UVar5 == US_DETERMINE_NEXT_STATEUnk) {
    DAT_UnitsState.units[uVar11].gfxNumber = 0x3d8;
    DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0;
    if (DAT_UnitsState.units[uVar11].isDisappearingUnk != 0) {
      pbVar1 = &DAT_UnitsState.units[uVar11].disappearFadeAlphaCountdown;
      *pbVar1 = *pbVar1 - 1;
      if (-1 < (char)*pbVar1) {
        return FALSE;
      }
      DAT_UnitsState.units[uVar11].disappearFadeAlphaCountdown = 0;
      DAT_UnitsState.units[uVar11].isDisappearingUnk = 0;
      return BVar8;
    }
    if (DAT_UnitsState.units[uVar11].goToRallyPoint != 0) {
      DAT_UnitsState.units[uVar11].goToRallyPoint = 0;
      DAT_UnitsState.units[uVar11].state.generic = US_STAND_UPUnk|US_IDLEUnk;
      DAT_UnitsState.units[uVar11].destinationNeeded = 2;
      return BVar8;
    }
    piVar2 = &DAT_UnitsState.units[uVar11].animationCycleNumber;
    *piVar2 = *piVar2 + 1;
    if (DAT_UnitsState.units[uVar11].animationCycleNumber < 10) {
      return FALSE;
    }
    iVar14 = (int)DAT_UnitsState.units[uVar11].workplaceBuildingID_1;
    iVar14 = Map::Buildings::BuildingsState::getBuildingResourceAmountByUid
                       (&DAT_BuildingsState,iVar14,DAT_BuildingsState.buildings[iVar14].uid,RT_LOGS)
    ;
    if (2 < iVar14) {
      Map::Units::UnitsState::commitUnitLocation(&DAT_UnitsState,uVar11);
      DAT_UnitsState.units[uVar11].state.generic = US_FIRE_WEAPONUnk;
      DAT_UnitsState.units[uVar11].updateTickTracker = 0;
      return extraout_EAX;
    }
    iVar14 = Map::LandscapeState::findTree
                       (&DAT_LandscapeState,(int)DAT_UnitsState.units[uVar11].owner,
                        (int)DAT_UnitsState.units[uVar11].x,(int)DAT_UnitsState.units[uVar11].y);
    uVar11 = DAT_CurrentUnitSlotID;
    if (iVar14 == 0) {
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = 10;
      return FALSE;
    }
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].workplaceBuildingTilePosition = (short)iVar14;
    DAT_UnitsState.units[uVar11].woodcutterTreeUID = DAT_LandscapeState.trees[iVar14].uid;
    Map::Navigation::PathFindingState::findBestAdjacentClimbTileToTarget
              (&DAT_PathFindingState,(int)DAT_UnitsState.units[uVar11].owner,
               (int)DAT_UnitsState.units[uVar11].x,(int)DAT_UnitsState.units[uVar11].y,
               (int)(short)DAT_LandscapeState.trees[iVar14].xPosition,
               (int)(short)DAT_LandscapeState.trees[iVar14].yPosition);
    uVar11 = DAT_CurrentUnitSlotID;
    if ((DAT_PathFindingState.climbX == (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].x) &&
       (DAT_PathFindingState.climbY == (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].y)) {
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_IDLEUnk;
      BVar8 = Map::Units::UnitsState::makeUnitStopWalkingByClearingPathProgressState(uVar11);
      return BVar8;
    }
    BVar8 = Map::Units::UnitsState::setDestinationForUnit
                      (&DAT_UnitsState,DAT_CurrentUnitSlotID,DAT_PathFindingState.climbX,
                       DAT_PathFindingState.climbY,0);
    uVar11 = DAT_CurrentUnitSlotID;
    if (BVar8 == FALSE) {
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = 10;
      return FALSE;
    }
    iVar14 = DAT_CurrentUnitSlotID * 0x490;
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_IDLEUnk;
    sVar13 = DAT_UnitsState.units[uVar11].totalSizeOfPathPlan;
    DAT_BuildingsState.buildings[DAT_UnitsState.units[uVar11].workplaceBuildingID_1].field273_0x2d4
         = sVar13;
    return CONCAT22((short)((uint)iVar14 >> 0x10),sVar13);
  }
  if (UVar5 == US_IDLEUnk) {
    IncrementAndOptionalUpdateAVValueRelated(uVar11,FALSE);
    BVar9 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,uVar11);
    BVar8 = FALSE;
    if (BVar9 != FALSE) {
      DAT_UnitsState.units[uVar11].animationCycleNumber = 0;
      if (DAT_UnitsState.units[uVar11].unitOrderWhenOnSameTile == 0) {
        BVar8 = Map::LandscapeState::isTreeAliveAndMatchingUID
                          (&DAT_LandscapeState,iVar15,DAT_UnitsState.units[uVar11].woodcutterTreeUID
                          );
        uVar11 = DAT_CurrentUnitSlotID;
        if (BVar8 == FALSE) {
          BVar8 = Map::LandscapeState::isTreeAdult
                            (&DAT_LandscapeState,iVar15,
                             DAT_UnitsState.units[DAT_CurrentUnitSlotID].woodcutterTreeUID);
          uVar11 = DAT_CurrentUnitSlotID;
          iVar16 = DAT_CurrentUnitSlotID * 0x490;
          if (BVar8 == FALSE) {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_DETERMINE_NEXT_STATEUnk;
          }
          else {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = 3;
            *(undefined4 *)&DAT_UnitsState.units[uVar11].field_0x4c = 0;
          }
        }
        else {
          iVar16 = DAT_CurrentUnitSlotID * 0x490;
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = 2;
          *(undefined4 *)&DAT_UnitsState.units[uVar11].field_0x4c = 0;
        }
      }
      else {
        BVar10 = Map::Navigation::PathFindingState::
                 findNeighbourTileThatCanServeAsClimbPointClosestToXY
                           (&DAT_PathFindingState,(int)DAT_UnitsState.units[uVar11].x,
                            (int)DAT_UnitsState.units[uVar11].y,
                            (int)(short)DAT_LandscapeState.trees[iVar15].xPosition,
                            (int)(short)DAT_LandscapeState.trees[iVar15].yPosition);
        if (BVar10 == 0) {
          iVar16 = DAT_CurrentUnitSlotID * 0x490;
          BVar8 = FALSE;
        }
        else {
          BVar8 = Map::Units::UnitsState::setDestinationForUnit
                            (&DAT_UnitsState,DAT_CurrentUnitSlotID,DAT_PathFindingState.climbX,
                             DAT_PathFindingState.climbY,0);
          iVar16 = DAT_CurrentUnitSlotID * 0x490;
          if (BVar8 != FALSE) {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_IDLEUnk;
            goto LAB_0054ca95;
          }
        }
        *(undefined2 *)((int)DAT_UnitsState.units[0].manningEngineerRef + iVar16 + -0x54) = 9;
        *(undefined2 *)((int)DAT_UnitsState.units[0].manningEngineerRef + iVar16 + 0x60) = 1;
      }
    }
LAB_0054ca95:
    *(undefined4 *)((int)&DAT_UnitsState.units[0].animationSheetFrameOffset + iVar16) = 1;
    *(undefined4 *)((int)&DAT_UnitsState.units[0].field_0x30_animRelated + iVar16) = 0x10;
    return BVar8;
  }
  if (UVar5 == 2) {
    DAT_UnitsState.units[uVar11].animationSpeed = 2;
    DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0;
    IncrementAndOptionalUpdateAVValueRelated(uVar11,FALSE);
    Map::Navigation::DirectionAlgorithmState::calculateOrientation
              (&DAT_DirectionAlgorithmState,(int)DAT_UnitsState.units[uVar11].x,
               (int)DAT_UnitsState.units[uVar11].y,
               (int)(short)DAT_LandscapeState.trees[iVar15].xPosition,
               (int)(short)DAT_LandscapeState.trees[iVar15].yPosition);
    uVar11 = DAT_CurrentUnitSlotID;
    if (DAT_DirectionAlgorithmState.orientation == 0xf) {
      DAT_DirectionAlgorithmState.orientation = 4;
    }
    iVar14 = DAT_DirectionAlgorithmState.orientation + 2;
    if (7 < iVar14) {
      iVar14 = DAT_DirectionAlgorithmState.orientation + -6;
    }
    DAT_DirectionAlgorithmState.orientation = iVar14;
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].facingDirection = (short)iVar14;
    iVar14 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field213_0x3ff4[DAT_UnitsState.units[uVar11].animationCycleNumber];
    DAT_UnitsState.units[uVar11].animationFrame = iVar14;
    if ((iVar14 == 0xc) &&
       (DAT_UnitsState.units[uVar11].animationCycleNumberHasJustIncremented != FALSE)) {
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_UnitsState.units[uVar11].x,
                 (int)DAT_UnitsState.units[uVar11].y,FX_CHOP);
    }
    uVar11 = DAT_CurrentUnitSlotID;
    BVar8 = DAT_CurrentUnitSlotID * 0x490;
    iVar14 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationFrame;
    if (iVar14 < 1) {
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationFrame = 1;
      DAT_UnitsState.units[uVar11].animationCycleNumber = 0;
      DAT_UnitsState.units[uVar11].gfxNumber =
           DAT_UnitsState.units[uVar11].facingDirectionMapOrientationCorrected + 0x359;
      uVar11 = Map::LandscapeState::isTreeAliveAndMatchingUID
                         (&DAT_LandscapeState,iVar15,DAT_UnitsState.units[uVar11].woodcutterTreeUID)
      ;
      if (uVar11 == 0) {
        BVar8 = Map::LandscapeState::isTreeAdult
                          (&DAT_LandscapeState,iVar15,
                           DAT_UnitsState.units[DAT_CurrentUnitSlotID].woodcutterTreeUID);
        if (BVar8 == FALSE) {
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_DETERMINE_NEXT_STATEUnk;
          return FALSE;
        }
      }
      else {
        iVar14 = Map::LandscapeState::damageTreeAndTriggerDeathIfDepleted
                           (&DAT_LandscapeState,iVar15,0xffffffff,
                            DAT_UnitsState.units[DAT_CurrentUnitSlotID].woodcutterTreeUID);
        if (iVar14 == 0) {
          return FALSE;
        }
        if (DAT_LandscapeState.trees[iVar15].stage < 2) {
          sVar13 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].y;
          sVar6 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].x;
          sfxOffsetInArray = FX_LILTREE_FALL;
        }
        else {
          sVar13 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].y;
          sVar6 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].x;
          sfxOffsetInArray = FX_TREE_FALL;
        }
        Audio::SFX::SFXState::playSFXAtLocation
                  (&DAT_SFXState,(int)sVar6,(int)sVar13,sfxOffsetInArray);
      }
      uVar11 = DAT_CurrentUnitSlotID;
      BVar8 = DAT_CurrentUnitSlotID * 0x490;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = 3;
      *(undefined4 *)&DAT_UnitsState.units[uVar11].field_0x4c = 0;
      return BVar8;
    }
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber =
         DAT_UnitsState.units[DAT_CurrentUnitSlotID].facingDirectionMapOrientationCorrected + 0x2f9
         + iVar14 * 8;
    return BVar8;
  }
  if (UVar5 == 3) {
    uVar12 = DAT_LandscapeState.trees[iVar15].yPosition;
    uVar7 = DAT_LandscapeState.trees[iVar15].xPosition;
    DAT_UnitsState.units[uVar11].animationSpeed = 2;
    DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0;
    Map::Navigation::DirectionAlgorithmState::calculateOrientation
              (&DAT_DirectionAlgorithmState,(int)DAT_UnitsState.units[uVar11].x,
               (int)DAT_UnitsState.units[uVar11].y,(int)(short)uVar7,(int)(short)uVar12);
    uVar11 = DAT_CurrentUnitSlotID;
    if (DAT_DirectionAlgorithmState.orientation == 0xf) {
      DAT_DirectionAlgorithmState.orientation = 4;
    }
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].facingDirection =
         (short)DAT_DirectionAlgorithmState.orientation;
    IncrementAndOptionalUpdateAVValueRelated(uVar11,FALSE);
    if (*(int *)&DAT_UnitsState.units[uVar11].field_0x4c == 0) {
      DAT_UnitsState.units[uVar11].animationFrame =
           (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                      field214_0x4020[DAT_UnitsState.units[uVar11].animationCycleNumber];
    }
    else {
      DAT_UnitsState.units[uVar11].animationFrame =
           (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                      field215_0x404c[DAT_UnitsState.units[uVar11].animationCycleNumber];
    }
    if ((DAT_UnitsState.units[uVar11].animationFrame == 7) &&
       (DAT_UnitsState.units[uVar11].animationCycleNumberHasJustIncremented != FALSE)) {
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_UnitsState.units[uVar11].x,
                 (int)DAT_UnitsState.units[uVar11].y,FX_CHOP);
      uVar11 = DAT_CurrentUnitSlotID;
    }
    iVar14 = DAT_UnitsState.units[uVar11].animationFrame;
    if (0 < iVar14) {
      DAT_UnitsState.units[uVar11].gfxNumber =
           DAT_UnitsState.units[uVar11].facingDirectionMapOrientationCorrected + 0x359 + iVar14 * 8;
      return uVar11 * 0x490;
    }
    DAT_UnitsState.units[uVar11].animationFrame = 1;
    DAT_UnitsState.units[uVar11].animationCycleNumber = 0;
    DAT_UnitsState.units[uVar11].gfxNumber =
         DAT_UnitsState.units[uVar11].facingDirectionMapOrientationCorrected + 0x3b1;
    BVar8 = Map::LandscapeState::isTreeAdult
                      (&DAT_LandscapeState,iVar15,DAT_UnitsState.units[uVar11].woodcutterTreeUID);
    uVar11 = DAT_CurrentUnitSlotID;
    if (BVar8 == FALSE) {
      BVar8 = DAT_CurrentUnitSlotID * 0x490;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_DETERMINE_NEXT_STATEUnk;
      return BVar8;
    }
    BVar8 = DAT_CurrentUnitSlotID * 0x490;
    puVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].field_0x4c;
    *(int *)puVar3 = *(int *)puVar3 + 1;
    if (*(int *)&DAT_UnitsState.units[uVar11].field_0x4c < 4) {
      return BVar8;
    }
    Map::LandscapeState::advanceTreeDecayState
              (&DAT_LandscapeState,iVar15,DAT_UnitsState.units[uVar11].woodcutterTreeUID);
    iVar14 = Map::Units::UnitsState::setWorkplaceBuildingEntryAsTarget
                       (&DAT_UnitsState,DAT_CurrentUnitSlotID,1);
    if (iVar14 == 0) {
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].logicalState = ULS_REMOVE;
      return FALSE;
    }
    BVar8 = Map::Units::UnitsState::setDestinationForUnit
                      (&DAT_UnitsState,DAT_CurrentUnitSlotID,
                       (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetX_2,
                       (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetY_2,0);
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_RELOAD_WEAPONUnk;
    return BVar8;
  }
  if (UVar5 == US_RELOAD_WEAPONUnk) {
    IncrementAndOptionalUpdateAVValueRelated(uVar11,FALSE);
    BVar9 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,uVar11);
    BVar8 = FALSE;
    if (BVar9 != FALSE) {
      DAT_UnitsState.units[uVar11].animationCycleNumber = 10;
      DAT_UnitsState.units[uVar11].state.generic = US_DETERMINE_NEXT_STATEUnk;
      iVar14 = (int)DAT_UnitsState.units[uVar11].workplaceBuildingID_1;
      Map::Buildings::BuildingsState::addResourceToStockpile
                (&DAT_BuildingsState,iVar14,DAT_BuildingsState.buildings[iVar14].uid,RT_LOGS,1,3,1);
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].x,
                 (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].y,FX_DROP_LOG);
      BVar8 = extraout_EAX_00;
      uVar11 = DAT_CurrentUnitSlotID;
    }
    DAT_UnitsState.units[uVar11].animationSheetFrameOffset = 0x101;
    if (DAT_UnitsState.units[uVar11].movementRunUpTime != 0) {
      DAT_UnitsState.units[uVar11].animationSheetFrameOffset = 0x181;
    }
    DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0x10;
    return BVar8;
  }
  if (UVar5 == US_AIM_WEAPONUnk) {
    IncrementAndOptionalUpdateAVValueRelated(uVar11,FALSE);
    iVar14 = Map::Buildings::BuildingsState::updateBuildingSignpostCounter
                       (&DAT_BuildingsState,(int)DAT_UnitsState.units[uVar11].workplaceBuildingID_1,
                        1);
    if (iVar14 == 0) {
      return FALSE;
    }
    iVar14 = (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].workplaceBuildingID_1;
    Map::Buildings::BuildingsState::addResourceToStockpile
              (&DAT_BuildingsState,iVar14,DAT_BuildingsState.buildings[iVar14].uid,RT_WOOD,1,3,1);
    BVar8 = DAT_CurrentUnitSlotID * 0x490;
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_FIRE_WEAPONUnk;
    return BVar8;
  }
  if (UVar5 == US_FIRE_WEAPONUnk) {
    IncrementAndOptionalUpdateAVValueRelated(uVar11,FALSE);
    psVar4 = &DAT_UnitsState.units[uVar11].updateTickTracker;
    *psVar4 = *psVar4 + 1;
    if (DAT_UnitsState.units[uVar11].updateTickTracker < 0x30) {
      BVar8 = Map::Buildings::BuildingsState::updateBuildingSignpostCounter
                        (&DAT_BuildingsState,(int)DAT_UnitsState.units[uVar11].workplaceBuildingID_1
                         ,3);
      return BVar8;
    }
    iVar16 = (int)DAT_UnitsState.units[uVar11].workplaceBuildingID_1;
    iVar14 = DAT_BuildingsState.buildings[iVar16].uid;
    iVar15 = Map::Buildings::BuildingsState::getBuildingResourceAmountByUid
                       (&DAT_BuildingsState,iVar16,iVar14,RT_LOGS);
    if (iVar15 < 1) {
      Map::Buildings::BuildingsState::addResourceToStockpile
                (&DAT_BuildingsState,iVar16,iVar14,RT_WOOD,-3,0,1);
      Map::Buildings::BuildingsState::updateBuildingSignpostCounter
                (&DAT_BuildingsState,
                 (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].workplaceBuildingID_1,0);
      Map::Units::UnitsState::resetUnitMovementState(&DAT_UnitsState,DAT_CurrentUnitSlotID);
      uVar11 = DAT_CurrentUnitSlotID;
      BVar8 = DAT_CurrentUnitSlotID * 0x490;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].updateTickTracker = 0;
      DAT_UnitsState.units[uVar11].state.generic = US_LOOK_AROUNDUnk;
      return BVar8;
    }
    Map::Buildings::BuildingsState::addResourceToStockpile
              (&DAT_BuildingsState,iVar16,iVar14,RT_LOGS,-1,3,1);
    Map::Buildings::BuildingsState::updateBuildingSignpostCounter
              (&DAT_BuildingsState,
               (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].workplaceBuildingID_1,2);
    uVar11 = DAT_CurrentUnitSlotID;
    BVar8 = DAT_CurrentUnitSlotID * 0x490;
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].updateTickTracker = 0;
    DAT_UnitsState.units[uVar11].state.generic = US_AIM_WEAPONUnk;
    return BVar8;
  }
  if (UVar5 == US_LOOK_AROUNDUnk) {
    DAT_UnitsState.units[uVar11].animationSheetFrameOffset = 0x201;
    DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0x10;
    DAT_UnitsState.units[uVar11].field134_0x2ac = 1;
    psVar4 = &DAT_UnitsState.units[uVar11].updateTickTracker;
    *psVar4 = *psVar4 + 1;
    uVar12 = DAT_UnitsState.units[uVar11].updateTickTracker;
    if ((short)uVar12 < 0x15) {
      return (uint)uVar12;
    }
    DAT_UnitsState.units[uVar11].updateTickTracker = 0;
    iVar14 = Map::Buildings::BuildingsState::getBuildingThatCanStoreThisResource
                       (&DAT_BuildingsState,RT_WOOD,1,(int)DAT_UnitsState.units[uVar11].owner);
    if ((iVar14 == 0) &&
       (DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner ==
        DAT_GameSynchronyState.currentPlayerSlotID)) {
      PlayStockpileIsFullWarning();
    }
    iVar15 = Map::Buildings::BuildingsState::buildingIsAccessible(&DAT_BuildingsState,iVar14,1);
    if (iVar15 == 0) {
      return FALSE;
    }
    BVar8 = Map::Units::UnitsState::setDestinationForUnit
                      (&DAT_UnitsState,DAT_CurrentUnitSlotID,
                       (int)DAT_BuildingsState.buildings[iVar14].buildingEntryX,
                       (int)DAT_BuildingsState.buildings[iVar14].buildingEntryY,0);
    uVar11 = DAT_CurrentUnitSlotID;
    if (BVar8 == FALSE) {
      return FALSE;
    }
    iVar15 = DAT_BuildingsState.buildings[iVar14].uid;
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetID_OR_targetBuildingID = (short)iVar14;
    DAT_UnitsState.units[uVar11].targetUID = iVar15;
    DAT_UnitsState.units[uVar11].state.generic = US_STAND_UPUnk;
    BVar8 = ComputeGoodsProduced(uVar11,0xc,TRUE);
    DAT_UnitsState.units[uVar11].resourceToDeposit = (short)BVar8;
    return BVar8;
  }
  if (UVar5 == US_STAND_UPUnk) {
    IncrementAndOptionalUpdateAVValueRelated(uVar11,FALSE);
    DAT_UnitsState.units[uVar11].animationSheetFrameOffset = 0x201;
    if (DAT_UnitsState.units[uVar11].movementRunUpTime != 0) {
      DAT_UnitsState.units[uVar11].animationSheetFrameOffset = 0x281;
    }
    DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0x10;
    psVar4 = &DAT_UnitsState.units[uVar11].updateTickTracker;
    *psVar4 = *psVar4 + 1;
    uVar12 = DAT_UnitsState.units[uVar11].updateTickTracker;
    if ((short)uVar12 < 5) {
      return (uint)uVar12;
    }
    BVar8 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,uVar11);
    if (BVar8 == FALSE) {
      return FALSE;
    }
    DAT_UnitsState.units[uVar11].updateTickTracker = 0;
    iVar14 = Map::Buildings::BuildingsState::canBuildingStoreTheAmount
                       (&DAT_BuildingsState,
                        (int)DAT_UnitsState.units[uVar11].targetID_OR_targetBuildingID,RT_WOOD,0x30)
    ;
    if (iVar14 == 0) {
      iVar14 = Map::Buildings::BuildingsState::getBuildingThatCanStoreThisResource
                         (&DAT_BuildingsState,RT_WOOD,1,
                          (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner);
      iVar15 = Map::Buildings::BuildingsState::buildingIsAccessible(&DAT_BuildingsState,iVar14,1);
      uVar11 = DAT_CurrentUnitSlotID;
      if (iVar15 == 0) {
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].resourceToDeposit = 0;
        BVar8 = FALSE;
      }
      else {
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetID_OR_targetBuildingID = (short)iVar14;
        DAT_UnitsState.units[uVar11].targetUID = DAT_BuildingsState.buildings[iVar14].uid;
        BVar8 = Map::Units::UnitsState::setDestinationForUnit
                          (&DAT_UnitsState,uVar11,
                           (int)DAT_BuildingsState.buildings[iVar14].buildingEntryX,
                           (int)DAT_BuildingsState.buildings[iVar14].buildingEntryY,0);
        uVar11 = DAT_CurrentUnitSlotID;
      }
    }
    else {
      Map::Buildings::BuildingsState::addResourceToStockpile
                (&DAT_BuildingsState,
                 (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetID_OR_targetBuildingID,
                 DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetUID,RT_WOOD,1,0x30,1);
      uVar11 = DAT_CurrentUnitSlotID;
      piVar2 = DAT_GameSynchronyState.finalResults.finalWoodProduced +
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner;
      *piVar2 = *piVar2 + 1;
      psVar4 = &DAT_UnitsState.units[uVar11].resourceToDeposit;
      *psVar4 = *psVar4 + -1;
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_UnitsState.units[uVar11].x,
                 (int)DAT_UnitsState.units[uVar11].y,FX_STOCK_WOOD);
      BVar8 = extraout_EAX_01;
      uVar11 = DAT_CurrentUnitSlotID;
    }
    if (0 < DAT_UnitsState.units[uVar11].resourceToDeposit) {
      return BVar8;
    }
    IncrementAndOptionalUpdateAVValueRelated(uVar11,TRUE);
    iVar14 = Map::Units::UnitsState::setWorkplaceBuildingEntryAsTarget(&DAT_UnitsState,uVar11,1);
    uVar11 = DAT_CurrentUnitSlotID;
    if (iVar14 == 0) {
      BVar8 = DAT_CurrentUnitSlotID * 0x490;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].logicalState = ULS_REMOVE;
      return BVar8;
    }
    BVar8 = DAT_CurrentUnitSlotID * 0x490;
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_STAND_UPUnk|US_IDLEUnk;
    DAT_UnitsState.units[uVar11].destinationNeeded = DNE_DESTINATION_NEEDED;
    DAT_UnitsState.units[uVar11].animationSheetFrameOffset = 1;
    return BVar8;
  }
  if (UVar5 == (US_STAND_UPUnk|US_IDLEUnk)) {
    DAT_UnitsState.units[uVar11].animationSheetFrameOffset = 1;
    DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0x10;
    IncrementAndOptionalUpdateAVValueRelated(uVar11,FALSE);
    if (DAT_UnitsState.units[uVar11].destinationNeeded != DNE_DESTINATION_HAS_BEEN_SET) {
      BVar8 = ConsiderTakingABreakUnk(uVar11);
      if (BVar8 != FALSE) {
        return BVar8;
      }
      BVar8 = Map::Units::UnitsState::setDestinationForUnit
                        (&DAT_UnitsState,uVar11,(int)DAT_UnitsState.units[uVar11].targetX_2,
                         (int)DAT_UnitsState.units[uVar11].targetY_2,0);
      uVar11 = DAT_CurrentUnitSlotID;
      if (BVar8 == FALSE) {
        BVar8 = DAT_CurrentUnitSlotID * 0x490;
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_DISAPPEAR;
        DAT_UnitsState.units[uVar11].updateTickTracker = 0;
        return BVar8;
      }
      iVar16 = DAT_CurrentUnitSlotID * 0x490;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].destinationNeeded = DNE_DESTINATION_HAS_BEEN_SET;
    }
    BVar8 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,uVar11);
    if (BVar8 == FALSE) {
      return FALSE;
    }
    uVar12 = (ushort)(byte)DAT_GameCore.mapTimeInTicks;
    *(undefined4 *)((int)DAT_UnitsState.units[0].manningEngineerRef + iVar16 + -100) = 10;
    *(ushort *)((int)DAT_UnitsState.units[0].manningEngineerRef + iVar16 + 0x6c) = (uVar12 & 1) + 2;
    *(undefined2 *)((int)DAT_UnitsState.units[0].manningEngineerRef + iVar16 + -0x54) = 10;
    return 10;
  }
  if (UVar5 == (US_DEATH_02|US_STAND_UPUnk|US_IDLEUnk)) {
    DAT_UnitsState.units[uVar11].animationSheetFrameOffset = 1;
    DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0x10;
    BVar8 = SetRestingForUnit(uVar11);
    return BVar8;
  }
  if (UVar5 != 10) {
    if (UVar5 == 0x6c) {
      DAT_UnitsState.units[uVar11].stateBasedSpeed = 0;
      DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0;
      DAT_UnitsState.units[uVar11].animationSheetFrameOffset = 1;
      return BVar8;
    }
    if (UVar5 == US_DEATH_01) {
      DAT_UnitsState.units[uVar11].facingDirection = 0;
      DAT_UnitsState.units[uVar11].animationSpeed = 2;
      DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0;
      BVar8 = (BOOLEnum)
              (char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                    ANIM_Worker_Shared1[DAT_UnitsState.units[uVar11].animationCycleNumber];
      DAT_UnitsState.units[uVar11].animationFrame = BVar8;
      if ((int)BVar8 < 1) {
        DAT_UnitsState.units[uVar11].gfxNumber = 0x3f0;
        DAT_UnitsState.units[uVar11].state.generic = US_DISAPPEAR;
        DAT_UnitHasBecomeIdle = 1;
        return BVar8;
      }
      BVar8 = BVar8 + 0x3d8;
      bVar17 = DAT_UnitHasBecomeIdle == 0;
      DAT_UnitsState.units[uVar11].gfxNumber = BVar8;
      if (bVar17) {
        return BVar8;
      }
      DAT_UnitsState.units[uVar11].state.generic = US_DISAPPEAR;
      return BVar8;
    }
    uVar18 = Map::Units::UnitsState::checkIfCitizenUnitIsAliveBasedOnState(uVar11);
    sVar13 = (short)((uint6)uVar18 >> 0x20);
    if ((int)uVar18 == 0) {
      if (sVar13 != 0x6a) {
        if (sVar13 != 0x6e) {
          DAT_UnitsState.units[uVar11].state.generic = US_DETERMINE_NEXT_STATEUnk;
          BVar8 = Map::Units::UnitsState::makeUnitStopWalkingByClearingPathProgressState(uVar11);
          return BVar8;
        }
        pbVar1 = &DAT_UnitsState.units[uVar11].disappearFadeAlphaCountdown;
        *pbVar1 = *pbVar1 + 1;
        if (' ' < (char)DAT_UnitsState.units[uVar11].disappearFadeAlphaCountdown) {
          DAT_UnitsState.units[uVar11].disappearFadeAlphaCountdown = 0x20;
        }
        psVar4 = &DAT_UnitsState.units[uVar11].updateTickTracker;
        *psVar4 = *psVar4 + 1;
        uVar12 = DAT_UnitsState.units[uVar11].updateTickTracker;
        BVar8 = (BOOLEnum)uVar12;
        if (0x20 < (short)uVar12) {
          psVar4 = &DAT_BuildingsState.buildings[iVar14].unknownTickRelatedValue;
          *psVar4 = *psVar4 + 10;
          BVar8 = iVar14 * 0x32c + 0xf98810;
          DAT_UnitsState.units[uVar11].logicalState = ULS_REMOVE;
          if (DAT_UnitsState.units[uVar11].killedFlagUnk == 0) {
            BVar8 = Game::GameStateStructures::setLastEncounteredTroopUnit
                              (&DAT_GameState,(int)DAT_UnitsState.units[uVar11].owner,uVar11);
            uVar11 = DAT_CurrentUnitSlotID;
          }
        }
        DAT_BuildingsState.buildings[DAT_UnitsState.units[uVar11].workplaceBuildingID_1].
        idleTimerUnk = 4000;
        return BVar8;
      }
      DAT_UnitsState.units[uVar11].animationSpeed = 3;
      DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0;
      BVar8 = (BOOLEnum)
              (char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.field216_0x4070
                    [DAT_UnitsState.units[uVar11].animationCycleNumber];
      DAT_UnitsState.units[uVar11].animationFrame = BVar8;
      if ((int)BVar8 < 1) {
        DAT_UnitsState.units[uVar11].gfxNumber =
             DAT_UnitsState.units[uVar11].facingDirectionMapOrientationCorrected + 0x361;
        DAT_UnitHasBecomeIdle = 1;
      }
      else {
        BVar8 = DAT_UnitsState.units[uVar11].facingDirectionMapOrientationCorrected + 0x359 +
                BVar8 * 8;
        DAT_UnitsState.units[uVar11].gfxNumber = BVar8;
      }
      if (((DAT_UnitsState.units[uVar11].attackedUnitID != 0) &&
          (DAT_UnitsState.units[uVar11].animationCycleNumberHasJustIncremented != FALSE)) &&
         (DAT_UnitsState.units[uVar11].animationCycleNumber == 5)) {
        Audio::SFX::SFXState::playSFXAtLocation
                  (&DAT_SFXState,(int)DAT_UnitsState.units[uVar11].x,
                   (int)DAT_UnitsState.units[uVar11].y,FX_SWISH);
        BVar8 = extraout_EAX_02;
        uVar11 = DAT_CurrentUnitSlotID;
      }
      if (DAT_UnitHasBecomeIdle == 0) {
        return BVar8;
      }
      DAT_UnitsState.units[uVar11].animationCycleNumber = 0;
      Map::Units::UnitsState::resumeMovementIfNoAttackTarget(&DAT_UnitsState,uVar11);
      return extraout_EAX_03;
    }
    DAT_UnitsState.units[uVar11].facingDirection = 0;
    DAT_UnitsState.units[uVar11].animationSpeed = 2;
    DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0;
    BVar8 = (BOOLEnum)
            (char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                  ANIM_Worker_Shared1[DAT_UnitsState.units[uVar11].animationCycleNumber];
    DAT_UnitsState.units[uVar11].animationFrame = BVar8;
    if ((int)BVar8 < 1) {
      DAT_UnitsState.units[uVar11].gfxNumber = 0x408;
      DAT_UnitsState.units[uVar11].state.generic = US_DISAPPEAR;
      DAT_UnitHasBecomeIdle = 1;
      return BVar8;
    }
    BVar8 = BVar8 + 0x3f0;
    bVar17 = DAT_UnitHasBecomeIdle == 0;
    DAT_UnitsState.units[uVar11].gfxNumber = BVar8;
    if (bVar17) {
      return BVar8;
    }
    DAT_UnitsState.units[uVar11].state.generic = US_DISAPPEAR;
    return BVar8;
  }
                    /* -- Freetime at good things -- */
  DAT_UnitsState.units[uVar11].animationSpeed = 2;
  DAT_UnitsState.units[uVar11].field_0x30_animRelated = 0;
  DAT_UnitsState.units[uVar11].field42_0x58 = 1;
  DAT_UnitsState.units[uVar11].field134_0x2ac = 1;
  sVar13 = DAT_UnitsState.units[uVar11].substate;
  if (sVar13 == 0) {
    iVar14 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field206_0x3d70[DAT_UnitsState.units[uVar11].animationCycleNumber];
  }
  else if (sVar13 == 1) {
    iVar14 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field207_0x3da4[DAT_UnitsState.units[uVar11].animationCycleNumber];
  }
  else if (sVar13 == 2) {
    iVar14 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field208_0x3e20[DAT_UnitsState.units[uVar11].animationCycleNumber];
  }
  else if (sVar13 == 3) {
    iVar14 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field209_0x3e54[DAT_UnitsState.units[uVar11].animationCycleNumber];
  }
  else if (sVar13 == 4) {
    iVar14 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field210_0x3e84[DAT_UnitsState.units[uVar11].animationCycleNumber];
  }
  else if (sVar13 == 5) {
    iVar14 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field211_0x3f04[DAT_UnitsState.units[uVar11].animationCycleNumber];
  }
  else {
    if (sVar13 != 6) goto LAB_0054d5cd;
    iVar14 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field212_0x3f5c[DAT_UnitsState.units[uVar11].animationCycleNumber];
  }
  DAT_UnitsState.units[uVar11].animationFrame = iVar14;
LAB_0054d5cd:
  iVar15 = DAT_UnitHasBecomeIdle;
  iVar14 = DAT_UnitsState.units[uVar11].animationFrame;
  if (iVar14 < 1) {
    iVar15 = 1;
    DAT_UnitsState.units[uVar11].gfxNumber = 0x3d8;
    DAT_UnitHasBecomeIdle = 1;
  }
  else {
    DAT_UnitsState.units[uVar11].gfxNumber = iVar14 + 0x3c0;
  }
  BVar8 = SetStateToFreetimeWalking(uVar11,iVar15,7);
  if ((BVar8 == FALSE) && (iVar15 != 0)) {
    psVar4 = &DAT_UnitsState.units[uVar11].substate;
    *psVar4 = *psVar4 + 1;
    uVar12 = DAT_UnitsState.units[uVar11].substate;
    if (6 < (short)uVar12) {
      DAT_UnitsState.units[uVar11].substate = 0;
    }
    DAT_UnitsState.units[uVar11].animationCycleNumber = 0;
    DAT_UnitsState.units[uVar11].state.generic = US_DETERMINE_NEXT_STATEUnk;
    return (uint)uVar12;
  }
  return BVar8;
}



// ================= getBuildingThatCanStoreThisResource @ 0x00422230 =================

/* param_1 is 0xd (13) for apple farms. index in resource array of building?
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::Buildings::BuildingsState::getBuildingThatCanStoreThisResource
          (BuildingsState *this,ResourceType resourceType,int amount,int playerID)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  BuildingTypeShort *pBVar4;
  int *piVar5;
  
                    /* get the building we are looking for for this resource type:
                       granary or stockpile? */
  iVar1 = getBuildingStorageTypeForResourceType(resourceType);
                    /* check if we are looking for a stockpile */
  if (iVar1 == 10) {
    iVar1 = 1;
    if (1 < DAT_BuildingsState.maxBuildingsCount) {
      pBVar4 = &DAT_BuildingsState.buildings[1].buildingType;
      piVar5 = DAT_BuildingsState.buildings[1].resourceArray_resourceTypePlus1 + resourceType;
      do {
                    /* check if the building type is a stockpile, and whether it is owned by the
                       right person, and whether it already has resources on it, but is not full yet
                        */
        if (((pBVar4[-1] == BLS_NORMAL) && (*pBVar4 == BT_STOCKPILE)) &&
           (((short)pBVar4[2] == playerID &&
            ((*piVar5 != 0 &&
             (*piVar5 < DAT_BuildingDefinedData.DAT_StorageLimitResourceTypeArray[resourceType])))))
           ) {
          return iVar1;
        }
        iVar1 = iVar1 + 1;
        pBVar4 = pBVar4 + 0x196;
        piVar5 = piVar5 + 0xcb;
      } while (iVar1 < DAT_BuildingsState.maxBuildingsCount);
    }
    iVar1 = 1;
    if (1 < DAT_BuildingsState.maxBuildingsCount) {
      pBVar4 = &DAT_BuildingsState.buildings[1].buildingType;
      do {
        if ((((pBVar4[-1] == BLS_NORMAL) && (*pBVar4 == BT_STOCKPILE)) &&
            ((short)pBVar4[2] == playerID)) && ((int)*(uint *)(pBVar4 + 0x59) < 1)) {
          return iVar1;
        }
        iVar1 = iVar1 + 1;
        pBVar4 = pBVar4 + 0x196;
      } while (iVar1 < DAT_BuildingsState.maxBuildingsCount);
    }
  }
  else if ((iVar1 == 0x13) && (iVar1 = 1, 1 < DAT_BuildingsState.maxBuildingsCount)) {
    pBVar4 = &DAT_BuildingsState.buildings[1].buildingType;
    while ((((pBVar4[-1] != BLS_NORMAL || (*pBVar4 != BT_GRANARY)) || ((short)pBVar4[2] != playerID)
            ) || ((uVar2 = computeResourceSumForBuilding(&DAT_BuildingsState,iVar1),
                  0xf9 < (int)uVar2 ||
                  (iVar3 = buildingIsAccessible(&DAT_BuildingsState,iVar1,0), iVar3 == 0))))) {
      iVar1 = iVar1 + 1;
      pBVar4 = pBVar4 + 0x196;
      if (DAT_BuildingsState.maxBuildingsCount <= iVar1) {
        return 0;
      }
    }
                    /* land here if the building was a granary, and owned by the right player, not
                       filled over 249, and ... accessibility?? */
    return iVar1;
  }
  return 0;
}



// ================= addResourceToStockpile @ 0x0041bb30 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Buildings::BuildingsState::addResourceToStockpile
          (BuildingsState *this,int buildingID,int buildingUID,ResourceType resourceType,int amount,
          int maxCapacity,int recomputeResources)

{
  int *piVar1;
  BuildingTypeShort BVar2;
  int iVar3;
  BuildingsState *this_00;
  int playerID;
  
  playerID = (int)DAT_BuildingsState.buildings[buildingID].owner;
  iVar3 = DAT_BuildingsState.buildings[buildingID].resourceArray_resourceTypePlus1[resourceType] +
          amount;
  piVar1 = DAT_BuildingsState.buildings[buildingID].resourceArray_resourceTypePlus1 + resourceType;
  if (DAT_BuildingsState.buildings[buildingID].uid == buildingUID) {
    if (maxCapacity == 0) {
      *piVar1 = 0;
    }
    else if ((-1 < iVar3) && (iVar3 <= maxCapacity)) {
      if (recomputeResources != 0) {
        *piVar1 = iVar3;
        BVar2 = DAT_BuildingsState.buildings[buildingID].buildingType;
        if ((9 < (short)BVar2) && (((short)BVar2 < 0xc || (BVar2 == BT_GRANARY)))) {
          piVar1 = DAT_GameState.playerDataArray[playerID].currentResources + resourceType;
          *piVar1 = *piVar1 + amount;
        }
        extendResourceCountdownForPlayerBuildingsOfType
                  (&DAT_BuildingsState,
                   (int)(short)DAT_BuildingsState.buildings[buildingID].buildingType,600,
                   DAT_GameSynchronyState.currentPlayerSlotID);
        computeResourceSumForBuilding(this_00,buildingID);
        countPlayerResources(&DAT_BuildingsState,playerID);
        TileMapState::updateBuildingGraphicsLayer(&DAT_TileMapState,buildingID);
      }
      return 1;
    }
  }
  return 0;
}



