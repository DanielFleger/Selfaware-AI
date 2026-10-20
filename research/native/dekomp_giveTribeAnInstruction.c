// ================= giveTribeAnInstruction @ 00527c80 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* gynt: unitID and x and y and tile are the target of the instruction
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Units::TribesState::giveTribeAnInstruction
          (TribesState *this,int tribeID,UnitInstructionType unitInstructionType,int id_x_tile,
          int unitUID_Y,int param_5)

{
  short *psVar1;
  byte bVar2;
  UnitStateShort UVar3;
  UnitTypeShort UVar4;
  ushort uVar5;
  Unit *pUVar6;
  char cVar7;
  short sVar8;
  short sVar9;
  UnitInstructionType UVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  int iVar14;
  int iVar15;
  undefined3 extraout_var;
  BOOLEnum BVar16;
  uint uVar17;
  uint x;
  int iVar18;
  short sVar19;
  int *piVar20;
  uint y;
  uint uVar21;
  bool bVar22;
  int _unitTribeIndex;
  int _ramOrHorse;
  uint local_8;
  dword _param_4_unitUID_Y_copy;
  
  iVar12 = unitUID_Y;
  iVar11 = id_x_tile;
  iVar18 = tribeID;
  sVar9 = DAT_TribesState.tribes[tribeID].size;
  _param_4_unitUID_Y_copy = unitUID_Y;
  _ramOrHorse = 0;
  local_8 = 0;
  bVar22 = false;
  DAT_TribesState.tribes[tribeID].someUnitID = 0;
  DAT_TribesState.tribes[tribeID].field71_0x212 = 0;
  sVar19 = (short)id_x_tile;
  switch(unitInstructionType) {
  case UIT_NO_INSTRUCTION_OR_MOVEUnk:
    iVar11 = 0;
    if (0 < sVar9) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,iVar18,iVar11);
        iVar11 = iVar11 + 1;
        if ((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[iVar12].dying == 0)) {
          DAT_UnitsState.units[iVar12].field270_0x3c5 = 3;
          DAT_UnitsState.units[iVar12].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
          DAT_UnitsState.units[iVar12].field260_0x3b0 = 0;
        }
      } while (iVar11 < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
    break;
  case UIT_UNIT_ATTACK_UNIT:
                    /* unit attack target */
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    pUVar6 = DAT_UnitsState.units + id_x_tile;
    _unitTribeIndex = 0;
                    /* repurposed parameter: counts amount of melee units */
    id_x_tile = 0;
    if (pUVar6->uid != unitUID_Y) {
      return 0;
    }
    if (0 < sVar9) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if (((DAT_UnitsState.units[iVar12].logicalState != ULS_NORMAL) ||
            (DAT_UnitsState.units[iVar12].dying != 0)) ||
           (DAT_UnitsState.units[iVar12].field320_0x413 != 0)) goto switchD_00527ea5_caseD_6;
        DAT_UnitsState.units[iVar12]._someX_2 = 0;
        DAT_UnitsState.units[iVar12]._someY_2 = 0;
        switch(DAT_UnitsState.units[iVar12].unitType) {
        case UT_TUNNELER:
        case UT_E_SPEAR:
        case UT_E_PIKE:
        case UT_E_MACE:
        case UT_E_SWORD:
        case UT_E_KNIGHT:
        case UT_E_MONK:
        case UT_LORD:
        case UT_A_SLAVE:
        case UT_A_ASSASSIN:
        case UT_A_SWORDSMAN:
                    /* melee units */
          if ((DAT_UnitsState.units[iVar11].unitType != UT_ANTELOPESHDEER) &&
             ((param_5 != 1 || (DAT_UnitsState.units[iVar11].state.generic != US_MELEE_ATTACK)))) {
            id_x_tile = id_x_tile + 1;
          }
          break;
        case UT_E_ARCHER:
        case UT_E_XBOW:
        case UT_A_ARCHER:
        case UT_A_SLINGER:
        case UT_A_HARCHER:
        case UT_A_FIRETHROWER:
                    /* ranged units */
          if (DAT_UnitsState.units[iVar12].state.generic == 0x69) {
            DAT_UnitsState.units[iVar12].state.generic = US_MOVE_TO_DESTINATION;
          }
          DAT_UnitsState.units[iVar12].
          targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
               unitUID_Y;
          DAT_UnitsState.units[iVar12].targetUID = unitUID_Y;
          DAT_UnitsState.units[iVar12].targetingType = UIT_UNIT_ATTACK_UNIT;
          DAT_UnitsState.units[iVar12].targetedUnitID__OR__engineerMannedSiegeEngineRef = sVar19;
          DAT_UnitsState.units[iVar12].shootTargetedUnit = sVar19;
          DAT_UnitsState.units[iVar12].field300_0x3f8 = 0;
          UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
          goto LAB_00527ee1;
        case UT_S_CATAPULT:
        case UT_S_TREBUCHET:
          DAT_UnitsState.units[iVar12].field270_0x3c5 = 5;
          DAT_UnitsState.units[iVar12].targetingType = UIT_ATTACK_LAND;
          DAT_UnitsState.units[iVar12].attackAtTileX = DAT_UnitsState.units[iVar11].x;
          DAT_UnitsState.units[iVar12].attackAtTileY = DAT_UnitsState.units[iVar11].y;
          DAT_UnitsState.units[iVar12].unkAttackRelated = 0xb;
          DAT_UnitsState.units[iVar12].shootBeforeStop = 10;
          break;
        case UT_S_MANGONEL:
        case UT_S_BALLISTA:
        case UT_S_FBALLISTA:
          DAT_UnitsState.units[iVar12].targetingType = UIT_UNIT_ATTACK_UNIT;
          DAT_UnitsState.units[iVar12].targetedUnitID__OR__engineerMannedSiegeEngineRef = sVar19;
          DAT_UnitsState.units[iVar12].
          targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
               unitUID_Y;
          DAT_UnitsState.units[iVar12].field300_0x3f8 = 0;
          UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
          DAT_UnitsState.units[iVar12].shootBeforeStop = 10;
LAB_00527ee1:
          if (DAT_UnitsState.units[iVar11].unitType == UT_RABBIT) {
            DAT_TribesState.tribes[iVar18].field71_0x212 = 1;
          }
        }
switchD_00527ea5_caseD_6:
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
      if (id_x_tile != 0) {
                    /* if there are melee units in the selection */
        iVar12 = (int)DAT_TribesState.tribes[iVar18].selectionTargetUnitID;
        local_8 = (uint)DAT_UnitsState.units[iVar12].x;
        unitInstructionType = (UnitInstructionType)DAT_UnitsState.units[iVar12].y;
        predictUnitInterceptPosition
                  (&DAT_TribesState,iVar12,iVar11,(int *)&local_8,(int *)&unitInstructionType);
        Navigation::PathFindingState::pathPlanningForTribe
                  (&DAT_PathFindingState,tribeID,iVar11,local_8,unitInstructionType,id_x_tile,
                   (int)(short)DAT_TileMapState.PathConnectionLayer
                               [DAT_UnitsState.units[iVar12].tile],
                   (int)DAT_UnitsState.units[iVar12].owner);
        DAT_TribesState.tribes[iVar18].someUnitID = sVar19;
        DAT_TribesState.tribes[iVar18].someUnitUID = unitUID_Y;
        DAT_TribesState.tribes[iVar18].someTile = DAT_UnitsState.units[iVar11].tile;
        iVar12 = 0;
        sVar9 = DAT_TribesState.tribes[iVar18].size;
        DAT_TribesState.tribes[iVar18].someTile2 =
             (int)DAT_UnitsState.units[iVar11].destinationX_2Unk +
             DAT_ViewportRenderState.translationMatrix
             [DAT_UnitsState.units[iVar11].destinationY_2Unk].addXgetTile;
        unitInstructionType = 0;
        if (0 < sVar9) {
          id_x_tile = 0x12d5c6c;
          do {
            iVar11 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar12);
            iVar12 = iVar12 + 1;
            if (((DAT_UnitsState.units[iVar11].logicalState == ULS_NORMAL) &&
                (DAT_UnitsState.units[iVar11].dying == 0)) &&
               (DAT_UnitsState.units[iVar11].field320_0x413 == 0)) {
              UVar4 = DAT_UnitsState.units[iVar11].unitType;
              switch(UVar4) {
              case UT_TUNNELER:
              case UT_E_SPEAR:
              case UT_E_PIKE:
              case UT_E_MACE:
              case UT_E_SWORD:
              case UT_E_KNIGHT:
              case UT_E_MONK:
              case UT_LORD:
              case UT_A_SLAVE:
              case UT_A_ASSASSIN:
              case UT_A_SWORDSMAN:
                if (((param_5 != 1) ||
                    (DAT_UnitsState.units[iVar11].state.generic != US_MELEE_ATTACK)) &&
                   (iVar14 = *(int *)id_x_tile, iVar14 != 0)) {
                  sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar14];
                  uVar13 = iVar14 - DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
                  if (*(int *)(id_x_tile + 4) == 0) {
                    DAT_UnitsState.units[iVar11].targetingType = 0;
                    if (UVar4 == UT_LORD) break;
                  }
                  else {
                    DAT_UnitsState.units[iVar11].targetingType = UIT_UNIT_ATTACK_UNIT;
                    DAT_UnitsState.units[iVar11].targetedUnitID__OR__engineerMannedSiegeEngineRef =
                         sVar19;
                    DAT_UnitsState.units[iVar11].
                    targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID
                         = unitUID_Y;
                  }
                  UVar3 = DAT_UnitsState.units[iVar11].state.generic;
                  DAT_UnitsState.units[iVar11].plannedDestinationX = (short)uVar13;
                  DAT_UnitsState.units[iVar11].plannedDestinationY = sVar9;
                  DAT_UnitsState.units[iVar11].targetedBuildingTile = 0;
                  DAT_UnitsState.units[iVar11].movementType_OR_targetUnitID = 0;
                  if (UVar3 == US_MELEE_ATTACK) {
                    DAT_UnitsState.units[iVar11].unknownMovementRelated_0x2d2 =
                         DAT_UnitsState.units[iVar11].movementSpeed * -4;
                  }
                  DAT_UnitsState.units[iVar11].state.generic = US_MOVE_TO_DESTINATION;
                  BVar16 = isTribeAllAssassins(&DAT_TribesState,tribeID);
                  if (BVar16 == FALSE) {
                    DAT_PathFindingState.notAllAssassinsUnk = 1;
                  }
                  else {
                    DAT_PathFindingState.allAssassinsUnk = 1;
                  }
                  UnitsState::setDestinationForUnit(&DAT_UnitsState,iVar11,uVar13,(int)sVar9,0);
                  UVar10 = (int)DAT_UnitsState.units[iVar11].totalSizeOfPathPlan / 2;
                  DAT_UnitsState.units[iVar11].lookForEnemy = -0x32;
                  if ((int)unitInstructionType < (int)UVar10) {
                    unitInstructionType = UVar10;
                  }
                  id_x_tile = id_x_tile + 0xc;
                  DAT_PathFindingState.notAllAssassinsUnk = 0;
                }
              }
            }
          } while (iVar12 < DAT_TribesState.tribes[iVar18].size);
        }
        iVar11 = unitInstructionType * 8;
        if (iVar11 < 9) {
          iVar11 = 8;
        }
        DAT_TribesState.tribes[iVar18].field168_0x2be = (short)iVar11;
        return 1;
      }
    }
    break;
  case UIT_ATTACK_LAND:
  case UIT_THROW_COW:
    unitUID_Y = DAT_TribesState.tribes[tribeID].owner;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    _unitTribeIndex = 0;
    if (0 < sVar9) {
      do {
        iVar14 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if ((DAT_UnitsState.units[iVar14].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[iVar14].dying == 0)) {
          switch(DAT_UnitsState.units[iVar14].unitType) {
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_E_ARCHER_DEBUG:
          case UT_S_MANGONEL:
          case UT_S_BALLISTA:
          case UT_A_ARCHER:
          case UT_A_SLINGER:
          case UT_A_HARCHER:
          case UT_A_FIRETHROWER:
          case UT_S_FBALLISTA:
            if (DAT_UnitsState.units[iVar14].state.generic == 0x69) {
              DAT_UnitsState.units[iVar14].state.generic = US_MOVE_TO_DESTINATION;
            }
            DAT_UnitsState.units[iVar14].field300_0x3f8 = 0;
            DAT_UnitsState.units[iVar14].targetingType =
                 (UnitInstructionTypeShort)unitInstructionType;
LAB_00528808:
            DAT_UnitsState.units[iVar14].field270_0x3c5 = (byte)unitInstructionType;
            sVar9 = (short)iVar12;
            if ((unitInstructionType == UIT_THROW_COW) &&
               ((UVar4 = DAT_UnitsState.units[iVar14].unitType, UVar4 == UT_S_CATAPULT ||
                (UVar4 == UT_S_TREBUCHET)))) {
              if (DAT_GameState.playerDataArray[unitUID_Y].counter < 1) {
                DAT_UnitsState.units[iVar14].field270_0x3c5 = 5;
              }
              else {
                DAT_UnitsState.units[iVar14].targetingType = UIT_THROW_COW;
                DAT_UnitsState.units[iVar14].shootTargetMicroX = sVar19 * 8;
                DAT_UnitsState.units[iVar14].shootTargetMicroY = sVar9 * 8;
                DAT_UnitsState.units[iVar14].shootTargetZ =
                     (ushort)*(byte *)(DAT_ViewportRenderState.translationMatrix[iVar12].addXgetTile
                                       + 0x1d32c38 + iVar11);
              }
            }
            DAT_UnitsState.units[iVar14].attackAtTileX = sVar19;
            DAT_UnitsState.units[iVar14].attackAtTileY = sVar9;
            DAT_UnitsState.units[iVar14].unkAttackRelated = (short)param_5;
            DAT_UnitsState.units[iVar14]._someX_2 = 0;
            DAT_UnitsState.units[iVar14]._someY_2 = 0;
            UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar14);
            DAT_UnitsState.units[iVar14].shootBeforeStop = 10;
            break;
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
            if (DAT_UnitsState.units[iVar14].
                digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 != 0)
            goto LAB_00528808;
          }
        }
        if (DAT_TribesState.tribes[iVar18].size <= _unitTribeIndex) {
          return 1;
        }
      } while( true );
    }
    break;
  case UIT_FILL_MOAT:
    uVar5 = DAT_TileMapState.PathConnectionLayer
            [DAT_UnitsState.units[DAT_TribesState.tribes[tribeID].selectionTargetUnitID].tile];
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    if ((int)(short)uVar5 != 0) {
      iVar11 = Navigation::PathFindingState::canNavigateFunctionReturnsArea
                         (&DAT_PathFindingState,DAT_TribesState.tribes[tribeID].owner,
                          (int)(short)uVar5,id_x_tile,unitUID_Y);
      if (iVar11 == 0) {
        return 1;
      }
      unitUID_Y = DAT_PathFindingState.climbY;
      iVar11 = DAT_PathFindingState.climbX;
    }
  case UIT_DIG_MOAT:
    iVar12 = unitUID_Y;
    iVar14 = 0;
    DAT_TribesState.tribes[iVar18].isRallyingUnk = 0;
    giveUnitSelectionMoveInstructionNoMatchedSpeed(&DAT_TribesState,tribeID,iVar11,unitUID_Y,0,1);
    if (0 < DAT_TribesState.tribes[iVar18].size) {
      do {
        iVar15 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar14);
        iVar14 = iVar14 + 1;
        if ((DAT_UnitsState.units[iVar15].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[iVar15].dying == 0)) {
          switch(DAT_UnitsState.units[iVar15].unitType) {
          case UT_E_ARCHER:
          case UT_E_SPEAR:
          case UT_E_PIKE:
          case UT_E_MACE:
          case UT_E_ENGINEER:
          case UT_A_SLAVE:
            if (DAT_UnitsState.units[iVar15].state.generic == 0x69) {
              DAT_UnitsState.units[iVar15].state.generic = US_MOVE_TO_DESTINATION;
            }
            DAT_UnitsState.units[iVar15].targetingType = (undefined2)unitInstructionType;
            DAT_UnitsState.units[iVar15].attackAtTileX = (short)iVar11;
            DAT_UnitsState.units[iVar15].attackAtTileY = (short)iVar12;
            DAT_UnitsState.units[iVar15].targetX = sVar19;
            DAT_UnitsState.units[iVar15].targetY = (UnitStateShort)_param_4_unitUID_Y_copy;
            DAT_UnitsState.units[iVar15].targetedBuildingTile = 0;
            DAT_UnitsState.units[iVar15].movementType_OR_targetUnitID = 0;
            DAT_UnitsState.units[iVar15]._someX_2 = 0;
            DAT_UnitsState.units[iVar15]._someY_2 = 0;
          }
        }
      } while (iVar14 < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
    break;
  case UIT_ATTACK_BUILDING:
  case 0x24:
  case 0x26:
    _unitTribeIndex = 0;
    id_x_tile = 0;
    DAT_TribesState.tribes[tribeID].targetBuildingID = sVar19;
    DAT_TribesState.tribes[tribeID].targetBuildingUID = unitUID_Y;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    if (0 < sVar9) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if (((DAT_UnitsState.units[iVar12].logicalState != ULS_NORMAL) ||
            (DAT_UnitsState.units[iVar12].dying != 0)) ||
           (DAT_UnitsState.units[iVar12].field320_0x413 != 0)) goto switchD_00528b77_caseD_6;
        DAT_UnitsState.units[iVar12]._someX_2 = 0;
        DAT_UnitsState.units[iVar12]._someY_2 = 0;
        switch(DAT_UnitsState.units[iVar12].unitType) {
        case UT_E_ARCHER:
        case UT_E_XBOW:
        case UT_A_ARCHER:
        case UT_A_SLINGER:
        case UT_A_FIRETHROWER:
          goto switchD_00528b77_caseD_16;
        case UT_E_KNIGHT:
          if (DAT_BuildingsState.buildings[iVar11].buildingType != BT_PITCHDITCH) {
            _ramOrHorse = _ramOrHorse + 1;
          }
        case UT_TUNNELER:
        case UT_E_SPEAR:
        case UT_E_PIKE:
        case UT_E_MACE:
        case UT_E_SWORD:
        case UT_E_MONK:
        case UT_LORD:
        case UT_A_SLAVE:
        case UT_A_ASSASSIN:
        case UT_A_SWORDSMAN:
switchD_00528b77_caseD_5:
          if (DAT_BuildingsState.buildings[iVar11].buildingType != BT_PITCHDITCH) {
            id_x_tile = id_x_tile + 1;
          }
          break;
        case UT_S_CATAPULT:
        case UT_S_TREBUCHET:
        case UT_S_MANGONEL:
        case UT_S_BALLISTA:
        case UT_S_FBALLISTA:
          if ((unitInstructionType == 0x26) ||
             (DAT_BuildingsState.buildings[iVar11].buildingType == BT_PITCHDITCH)) break;
          DAT_UnitsState.units[iVar12].targetID_OR_targetBuildingID = sVar19;
          DAT_UnitsState.units[iVar12].
          targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
               unitUID_Y;
          goto LAB_00528c46;
        case UT_S_BATTERINGRAM:
          if ((DAT_BuildingsState.buildings[iVar11].buildingType != BT_PITCHDITCH) &&
             (DAT_UnitsState.units[iVar12].
              digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 4)) {
            id_x_tile = id_x_tile + 1;
            _ramOrHorse = _ramOrHorse + 1;
          }
          break;
        case UT_A_HARCHER:
          _ramOrHorse = _ramOrHorse + 1;
switchD_00528b77_caseD_16:
          if (unitInstructionType == 0x24) {
            switch(DAT_BuildingsState.buildings[iVar11].buildingType) {
            case BT_GATEHOUSELARGE:
            case BT_GATEHOUSESMALL:
            case BT_WOODGATE1:
            case BT_WOODGATE2:
            case BT_TOWER1:
            case BT_TOWER2:
            case BT_TOWER3:
            case BT_TOWER4:
            case BT_TOWER5:
              goto switchD_00528bae_caseD_2d;
            }
            goto switchD_00528b77_caseD_5;
          }
          if (unitInstructionType != 0x26) {
switchD_00528bae_caseD_2d:
                    /* attack buildings */
            if (DAT_UnitsState.units[iVar12].state.generic == 0x69) {
              DAT_UnitsState.units[iVar12].state.generic = US_MOVE_TO_DESTINATION;
            }
            sVar8 = (short)((int)(DAT_BuildingsState.buildings[iVar11].widthOrHeight * 8) / 2);
            DAT_UnitsState.units[iVar12].shootTargetMicroX =
                 DAT_BuildingsState.buildings[iVar11].x * 8 + sVar8;
            sVar9 = DAT_BuildingsState.buildings[iVar11].terrainHeightUnk;
            DAT_UnitsState.units[iVar12].shootTargetMicroY =
                 DAT_BuildingsState.buildings[iVar11].y * 8 + sVar8;
            DAT_UnitsState.units[iVar12].shootTargetZ = sVar9;
            DAT_UnitsState.units[iVar12].shootTargetedUnit = -1;
            DAT_UnitsState.units[iVar12].targetID_OR_targetBuildingID = sVar19;
            DAT_UnitsState.units[iVar12].
            targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
                 unitUID_Y;
LAB_00528c46:
            DAT_UnitsState.units[iVar12].field270_0x3c5 = 9;
            DAT_UnitsState.units[iVar12].targetingType = UIT_ATTACK_BUILDING;
            DAT_UnitsState.units[iVar12].field300_0x3f8 = 0;
            UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
            DAT_UnitsState.units[iVar12].shootBeforeStop = 10;
          }
        }
switchD_00528b77_caseD_6:
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
    }
    if ((((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
         (DAT_GameState.mapAndTime.strongWalls2 == 0)) ||
        (4 < (int)(short)DAT_BuildingsState.buildings[iVar11].buildingType - 0x4aU)) &&
       (id_x_tile != 0)) {
      sVar9 = DAT_TribesState.tribes[iVar18].selectionTargetUnitID;
      if ((unitInstructionType == UIT_ATTACK_BUILDING) || (unitInstructionType == 0x26)) {
        iVar12 = (int)DAT_UnitsState.units[sVar9].owner;
      }
      else {
        iVar12 = 0;
      }
      Navigation::PathFindingState::pathfindingForAttacksUnk
                (&DAT_PathFindingState,tribeID,iVar11,id_x_tile,
                 (int)(short)DAT_TileMapState.PathConnectionLayer[DAT_UnitsState.units[sVar9].tile],
                 iVar12);
      sortTribePathDestinationsByCost(&DAT_TribesState,tribeID,_ramOrHorse);
      if ((DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper != 0) &&
         (_unitTribeIndex = 0, 0 < DAT_TribesState.tribes[iVar18].size)) {
        id_x_tile = 0x12d5c70;
        do {
          iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
          _unitTribeIndex = _unitTribeIndex + 1;
          if (((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
              (DAT_UnitsState.units[iVar12].dying == 0)) &&
             (DAT_UnitsState.units[iVar12].field320_0x413 == 0)) {
            UVar4 = DAT_UnitsState.units[iVar12].unitType;
            switch(UVar4) {
            case UT_TUNNELER:
            case UT_E_SPEAR:
            case UT_E_PIKE:
            case UT_E_MACE:
            case UT_E_SWORD:
            case UT_E_KNIGHT:
            case UT_E_MONK:
            case UT_LORD:
            case UT_S_BATTERINGRAM:
            case UT_A_SLAVE:
            case UT_A_ASSASSIN:
            case UT_A_SWORDSMAN:
switchD_00528e3a_caseD_5:
              if (UVar4 != UT_S_BATTERINGRAM) goto LAB_00528f32;
              if (DAT_UnitsState.units[iVar12].
                  digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 != 4)
              break;
              if (bVar22) {
LAB_00528f32:
                iVar14 = *(int *)(id_x_tile + -4);
                if (iVar14 == 0) break;
                sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar14];
                unitUID_Y = iVar14 - DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
                DAT_UnitsState.units[iVar12].targetingType = 0;
                DAT_UnitsState.units[iVar12].plannedDestinationX = (short)unitUID_Y;
                DAT_UnitsState.units[iVar12].plannedDestinationY = sVar9;
                if (DAT_UnitsState.units[iVar12].state.generic == US_MELEE_ATTACK) {
                  DAT_UnitsState.units[iVar12].unknownMovementRelated_0x2d2 =
                       DAT_UnitsState.units[iVar12].movementSpeed * -4;
                }
                DAT_UnitsState.units[iVar12].state.generic = US_MOVE_TO_DESTINATION;
                BVar16 = isTribeAllAssassins(&DAT_TribesState,tribeID);
                if (BVar16 == FALSE) {
                  DAT_PathFindingState.notAllAssassinsUnk = 1;
                }
                else {
                  DAT_PathFindingState.allAssassinsUnk = 1;
                }
                UnitsState::setDestinationForUnit(&DAT_UnitsState,iVar12,unitUID_Y,(int)sVar9,0);
                DAT_UnitsState.units[iVar12].movementType_OR_targetUnitID = 0;
                DAT_PathFindingState.notAllAssassinsUnk = 0;
                uVar13 = *(uint *)id_x_tile;
                DAT_UnitsState.units[iVar12].targetedBuildingTile = uVar13;
                sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[uVar13];
                DAT_UnitsState.units[iVar12].attackAtTileY = sVar9;
                sVar9 = *(short *)id_x_tile -
                        (short)DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
                id_x_tile = id_x_tile + 0xc;
              }
              else {
                iVar14 = Navigation::PathFindingState::findBuildingAccessPoint
                                   (&DAT_PathFindingState,iVar12,iVar11,&param_5);
                bVar22 = true;
                if (iVar14 == 0) goto LAB_00528f32;
                sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar14];
                unitUID_Y = iVar14 - DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
                BVar16 = UnitsState::setDestinationForUnit
                                   (&DAT_UnitsState,iVar12,unitUID_Y,(int)sVar9,0);
                if (BVar16 == FALSE) goto LAB_00528f32;
                DAT_UnitsState.units[iVar12].targetingType = 0;
                DAT_UnitsState.units[iVar12].plannedDestinationX = (short)unitUID_Y;
                DAT_UnitsState.units[iVar12].plannedDestinationY = sVar9;
                if (DAT_UnitsState.units[iVar12].state.generic == US_MELEE_ATTACK) {
                  DAT_UnitsState.units[iVar12].unknownMovementRelated_0x2d2 =
                       DAT_UnitsState.units[iVar12].movementSpeed * -4;
                }
                DAT_UnitsState.units[iVar12].state.generic = US_MOVE_TO_DESTINATION;
                DAT_UnitsState.units[iVar12].movementType_OR_targetUnitID = 0;
                DAT_PathFindingState.notAllAssassinsUnk = 0;
                sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[param_5];
                DAT_UnitsState.units[iVar12].targetedBuildingTile = param_5;
                DAT_UnitsState.units[iVar12].attackAtTileY = sVar9;
                sVar9 = (short)param_5 -
                        (short)DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
              }
              DAT_UnitsState.units[iVar12].attackAtTileX = sVar9;
              break;
            case UT_E_ARCHER:
            case UT_E_XBOW:
            case UT_A_ARCHER:
            case UT_A_SLINGER:
            case UT_A_HARCHER:
            case UT_A_FIRETHROWER:
              if (unitInstructionType == 0x24) goto switchD_00528e3a_caseD_5;
            }
          }
          if (DAT_TribesState.tribes[iVar18].size <= _unitTribeIndex) {
            return 1;
          }
        } while( true );
      }
    }
    break;
  case UIT_CONSTRUCT_SIEGE_EQUIPMENTOIL_DUTYENGINEERRELATED:
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    uVar21 = (uint)DAT_BuildingsState.buildings[id_x_tile].buildingEntryY;
    uVar13 = (uint)DAT_BuildingsState.buildings[id_x_tile].buildingEntryX;
    _unitTribeIndex = 0;
    BVar16 = Rendering::ViewportRenderState::xyAreValid(&DAT_ViewportRenderState,uVar13,uVar21);
    if (BVar16 == FALSE) {
      return 0;
    }
    param_5 = (int)(short)DAT_TileMapState.PathConnectionLayer
                          [DAT_ViewportRenderState.translationMatrix[uVar21].addXgetTile + uVar13];
    unitUID_Y = Buildings::BuildingsState::getRequiredEngineersCount(&DAT_BuildingsState,iVar11);
    if (((unitUID_Y != 0) || (DAT_BuildingsState.buildings[iVar11].buildingType == BT_OILSMELTER))
       && (0 < DAT_TribesState.tribes[iVar18].size)) {
      do {
        uVar13 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        iVar12 = _unitTribeIndex + 1;
        if ((((((DAT_UnitsState.units[uVar13].logicalState == ULS_NORMAL) &&
               (DAT_UnitsState.units[uVar13].dying == 0)) &&
              (DAT_UnitsState.units[uVar13].unitType == UT_E_ENGINEER)) &&
             ((UVar3 = DAT_UnitsState.units[uVar13].state.generic,
              UVar3 != (US_STAND_UPUnk|US_IDLEUnk) && (UVar3 != 10)))) && (UVar3 != US_SIT_DOWNUnk))
           && (((UVar3 != (US_STAND_UPUnk|US_RELOAD_WEAPONUnk) &&
                (UVar3 != (US_STAND_UPUnk|US_AIM_WEAPONUnk))) &&
               ((UVar3 != (US_STAND_UPUnk|US_FIRE_WEAPONUnk) &&
                (UVar3 != (US_STAND_UPUnk|US_LOOK_AROUNDUnk))))))) {
          DAT_UnitsState.units[uVar13]._someX_2 = 0;
          DAT_UnitsState.units[uVar13]._someY_2 = 0;
          cVar7 = Buildings::BuildingsState::resolveBuildingEntryAccessibility
                            (&DAT_BuildingsState,iVar11,1,(int)DAT_UnitsState.units[uVar13].x,
                             (int)DAT_UnitsState.units[uVar13].y);
          if ((CONCAT31(extraout_var,cVar7) != 0) &&
             (iVar14 = Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                                 (&DAT_PathFindingState,(int)DAT_UnitsState.units[uVar13].owner,
                                  param_5,(int)(short)DAT_TileMapState.PathConnectionLayer
                                                      [DAT_UnitsState.units[uVar13].tile],0),
             iVar14 != 0)) {
            sVar9 = DAT_BuildingsState.buildings[iVar11].buildingEntryY;
            sVar8 = DAT_BuildingsState.buildings[iVar11].buildingEntryX;
            iVar14 = DAT_BuildingsState.buildings[iVar11].uid;
            DAT_UnitsState.units[uVar13].targetID_OR_targetBuildingID = sVar19;
            DAT_UnitsState.units[uVar13].targetUID = iVar14;
            UnitsState::setDestinationForUnit(&DAT_UnitsState,uVar13,(int)sVar8,(int)sVar9,0);
            if (DAT_BuildingsState.buildings[iVar11].buildingType == BT_OILSMELTER) {
              DAT_UnitsState.units[uVar13].state.generic = US_STAND_UPUnk|US_IDLEUnk;
              DAT_UnitsState.units[uVar13].workplaceBuildingID_1 = sVar19;
            }
            else {
              DAT_UnitsState.units[uVar13].state.generic = US_STAND_UPUnk;
              DAT_UnitsState.units[uVar13].resourceToDeposit = 0;
              UnitsState::deselectUnit(uVar13);
              UnitsState::clearOrDeselectUnitFromSelection
                        (&DAT_UnitsState,DAT_TribesState.tribes[iVar18].owner,uVar13,0);
              unitUID_Y = unitUID_Y + -1;
              iVar12 = _unitTribeIndex;
              if (unitUID_Y == 0) {
                return 1;
              }
            }
          }
        }
        _unitTribeIndex = iVar12;
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
    break;
  case UIT_MAN_SIEGE_EQUIPMENT:
                    /* manning siege equipment? */
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    if (((DAT_UnitsState.units[id_x_tile].uid == unitUID_Y) &&
        (unitUID_Y = UnitsState::getRemainingRequiredEngineers(&DAT_UnitsState,id_x_tile),
        unitUID_Y != 0)) && (iVar12 = 0, 0 < DAT_TribesState.tribes[iVar18].size)) {
      do {
        uVar13 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar12);
        iVar14 = iVar12 + 1;
        if (((DAT_UnitsState.units[uVar13].logicalState == ULS_NORMAL) &&
            (DAT_UnitsState.units[uVar13].dying == 0)) &&
           (DAT_UnitsState.units[uVar13].unitType == UT_E_ENGINEER)) {
          DAT_UnitsState.units[iVar11]._someX_2 = 0;
          DAT_UnitsState.units[iVar11]._someY_2 = 0;
          param_5 = (int)(short)DAT_TileMapState.PathConnectionLayer
                                [DAT_UnitsState.units[uVar13].tile];
          unitInstructionType = 0;
          do {
            iVar14 = (int)DAT_UnitsState.units[iVar11].
                          digTileY__OR__countLifeCycleEngineersSentToManSiegeEngine;
            x = (int)DAT_AttackInfoDefinedData.field10_0xec[iVar14][0] +
                (int)DAT_UnitsState.units[iVar11].x;
            y = (int)DAT_AttackInfoDefinedData.field10_0xec[iVar14][1] +
                (int)DAT_UnitsState.units[iVar11].y;
            uVar21 = iVar14 + 1U & 0x8000000f;
            if ((int)uVar21 < 0) {
              uVar21 = (uVar21 - 1 | 0xfffffff0) + 1;
            }
            DAT_UnitsState.units[iVar11].digTileY__OR__countLifeCycleEngineersSentToManSiegeEngine =
                 (short)uVar21;
            BVar16 = Rendering::ViewportRenderState::xyAreValid(&DAT_ViewportRenderState,x,y);
            if (BVar16 != FALSE) {
              iVar14 = DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x;
              _param_4_unitUID_Y_copy = (dword)(short)DAT_TileMapState.PathConnectionLayer[iVar14];
              uVar21 = TileMapState::getTotalHeightAtTile(&DAT_TileMapState,iVar14);
              uVar21 = ((int)DAT_UnitsState.units[iVar11].buildingHeight +
                       (int)DAT_UnitsState.units[iVar11].terrainOrClimbHeight) - uVar21;
              uVar17 = (int)uVar21 >> 0x1f;
              if (((int)((uVar21 ^ uVar17) - uVar17) < 0x11) &&
                 (iVar14 = Navigation::PathFindingState::
                           calculateCanPlayerUnitsNavigateToAreaFromArea
                                     (&DAT_PathFindingState,(int)DAT_UnitsState.units[iVar11].owner,
                                      param_5,_param_4_unitUID_Y_copy,0), iVar14 != 0)) break;
            }
            unitInstructionType = unitInstructionType + 1;
          } while ((int)unitInstructionType < 0x10);
          UnitsState::setDestinationForUnit(&DAT_UnitsState,uVar13,x,y,0);
          DAT_UnitsState.units[uVar13].state.generic = US_MOVE_TO_DESTINATION;
          DAT_UnitsState.units[uVar13].targetingType = UIT_MAN_SIEGE_EQUIPMENT;
          DAT_UnitsState.units[uVar13].targetedUnitID__OR__engineerMannedSiegeEngineRef =
               (short)id_x_tile;
          DAT_UnitsState.units[uVar13].resourceToDeposit = 0;
          UnitsState::deselectUnit(uVar13);
          UnitsState::clearOrDeselectUnitFromSelection
                    (&DAT_UnitsState,DAT_TribesState.tribes[iVar18].owner,uVar13,0);
          unitUID_Y = unitUID_Y + -1;
          iVar14 = iVar12;
          if (unitUID_Y == 0) {
            return 1;
          }
        }
        iVar12 = iVar14;
        if (DAT_TribesState.tribes[iVar18].size <= iVar14) {
          return 1;
        }
      } while( true );
    }
    break;
  case UIT_EXIT_SIEGE_EQUIPMENT:
                    /* disband siege engines? */
    _param_4_unitUID_Y_copy = -(uint)(param_5 != 0) & 0x10;
    param_5 = (int)SEC_RNG.currentNumber2 & 0x8000000f;
    if (param_5 < 0) {
      param_5 = (param_5 - 1U | 0xfffffff0) + 1;
    }
    Random::RNG::nextRandomNumber2(&SEC_RNG);
    if (DAT_UnitsState.units[iVar11].uid == unitUID_Y) {
      DAT_UnitsState.units[iVar11].state.generic = US_FIRE_WEAPONUnk;
      unitInstructionType = 0;
      if (0 < DAT_UnitsState.units[iVar11].
              digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300) {
        tribeID = iVar11 * 0x490 + 0x1388860;
        do {
          iVar18 = (int)*(short *)tribeID;
          *(undefined2 *)tribeID = 0;
          DAT_UnitsState.units[iVar18].field266_0x3c0 = 0;
          DAT_UnitsState.units[iVar18].field265_0x3bc = 0;
          DAT_UnitsState.units[iVar18].animationCycleNumber = 0;
          DAT_UnitsState.units[iVar18].state.generic = US_JESTER_ROAM_TO;
          DAT_UnitsState.units[iVar18].disappearFadeAlphaCountdown = 0x20;
          DAT_UnitsState.units[iVar18].engineerManningSiegeStateRef_checkType = 0xfe;
          DAT_UnitsState.units[iVar18].cachedState = (UnitStateShort)_param_4_unitUID_Y_copy;
          UVar4 = DAT_UnitsState.units[iVar11].unitType;
          if ((UVar4 == UT_S_MANGONEL) || (UVar4 == UT_S_BALLISTA)) {
            DAT_UnitsState.units[iVar18].goToRallyPoint = 1;
          }
          DAT_UnitsState.units[iVar18].updateTickTracker = 0;
          DAT_UnitsState.units[iVar18].field42_0x58 = 1;
          unitUID_Y = 0;
LAB_00529da0:
          do {
            uVar21 = (int)DAT_AttackInfoDefinedData.field10_0xec[param_5][0] +
                     (int)DAT_UnitsState.units[iVar11].x;
            uVar13 = (int)DAT_AttackInfoDefinedData.field10_0xec[param_5][1] +
                     (int)DAT_UnitsState.units[iVar11].y;
            param_5 = param_5 + 1U & 0x8000000f;
            if (param_5 < 0) {
              param_5 = (param_5 - 1U | 0xfffffff0) + 1;
            }
            Navigation::PathFindingState::findWalkableTileThatDoesNotContainUnit
                      (&DAT_PathFindingState,id_x_tile,uVar21,uVar13,1);
            if (DAT_PathFindingState.ALG_ResultTile == 0) {
              Navigation::PathFindingState::findWalkableTileThatDoesNotContainUnit
                        (&DAT_PathFindingState,id_x_tile,uVar21,uVar13,0);
              sVar9 = (short)DAT_PathFindingState.ALG_ResultX;
              sVar19 = (short)DAT_PathFindingState.ALG_ResultY;
              iVar12 = DAT_PathFindingState.ALG_ResultTile;
              if (DAT_PathFindingState.ALG_ResultTile != 0) break;
              unitUID_Y = unitUID_Y + 1;
              if (unitUID_Y != 0x10) goto LAB_00529da0;
              sVar9 = DAT_UnitsState.units[iVar11].x;
              sVar19 = DAT_UnitsState.units[iVar11].y;
              iVar12 = DAT_UnitsState.units[iVar11].tile;
            }
            else {
              sVar9 = (short)DAT_PathFindingState.ALG_ResultX;
              sVar19 = (short)DAT_PathFindingState.ALG_ResultY;
              iVar12 = DAT_PathFindingState.ALG_ResultTile;
            }
          } while (iVar12 == 0);
          bVar2 = DAT_TileMapState.HeightLayer[iVar12];
          DAT_UnitsState.units[iVar18].totalSizeOfPathPlan = 0;
          DAT_UnitsState.units[iVar18].x = sVar9;
          DAT_UnitsState.units[iVar18].mimicCurrentXPosition = sVar9;
          DAT_UnitsState.units[iVar18].y = sVar19;
          DAT_UnitsState.units[iVar18].mimicCurrentYPosition = sVar19;
          DAT_UnitsState.units[iVar18].terrainOrClimbHeight = (ushort)bVar2;
          DAT_UnitsState.units[iVar18].tile = iVar12;
          DAT_UnitsState.units[iVar18].nextTileUnk = iVar12;
          DAT_UnitsState.units[iVar18].microXPosition = sVar9 * 8 + 4;
          DAT_UnitsState.units[iVar18].microYPosition = sVar19 * 8 + 4;
          UnitsState::updateMicroPosition(&DAT_UnitsState,iVar18);
          UnitsState::resetUnitMovementState(&DAT_UnitsState,iVar18);
          tribeID = tribeID + 2;
          DAT_UnitsState.units[iVar18].animationSheetFrameOffset = 1;
          DAT_UnitsState.units[iVar18].field_0x30_animRelated = 0x10;
          unitInstructionType = unitInstructionType + 1;
        } while ((int)unitInstructionType <
                 (int)DAT_UnitsState.units[iVar11].
                      digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300);
      }
      DAT_UnitsState.units[iVar11].
      digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 = 0;
      UnitsState::makeUnitStopWalkingByClearingPathProgressState(id_x_tile);
      return 1;
    }
    break;
  case UIT_THROW_OIL:
    iVar11 = 0;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    if (0 < sVar9) {
      do {
        uVar13 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar11);
        iVar11 = iVar11 + 1;
        if (((DAT_UnitsState.units[uVar13].logicalState == ULS_NORMAL) &&
            (DAT_UnitsState.units[uVar13].dying == 0)) &&
           (DAT_UnitsState.units[uVar13].unitType == UT_E_ENGINEER)) {
          DAT_UnitsState.units[uVar13].targetingType = UIT_THROW_OIL;
          DAT_UnitsState.units[uVar13].attackAtTileX = sVar19;
          DAT_UnitsState.units[uVar13].attackAtTileY = (short)unitUID_Y;
          DAT_UnitsState.units[uVar13].plannedDestinationX = sVar19;
          DAT_UnitsState.units[uVar13].plannedDestinationY = (short)unitUID_Y;
          UnitsState::deselectUnit(uVar13);
          UnitsState::clearOrDeselectUnitFromSelection
                    (&DAT_UnitsState,DAT_TribesState.tribes[iVar18].owner,uVar13,0);
          DAT_UnitsState.units[uVar13]._someX_2 = 0;
          DAT_UnitsState.units[uVar13]._someY_2 = 0;
        }
      } while (iVar11 < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
    break;
  case 0x15:
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    uVar13 = (uint)DAT_BuildingsState.buildings[id_x_tile].buildingEntryY;
    _unitTribeIndex = 0;
    BVar16 = Rendering::ViewportRenderState::xyAreValid
                       (&DAT_ViewportRenderState,
                        (int)DAT_BuildingsState.buildings[id_x_tile].buildingEntryX,uVar13);
    if (BVar16 == FALSE) {
      return 0;
    }
    param_5 = (int)(short)DAT_TileMapState.PathConnectionLayer
                          [DAT_ViewportRenderState.translationMatrix[uVar13].addXgetTile +
                           (int)DAT_BuildingsState.buildings[iVar11].buildingEntryX];
    if (0 < sVar9) {
      do {
        uVar13 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if (((DAT_UnitsState.units[uVar13].logicalState == ULS_NORMAL) &&
            (DAT_UnitsState.units[uVar13].dying == 0)) &&
           (DAT_UnitsState.units[uVar13].unitType == UT_TUNNELER)) {
          DAT_UnitsState.units[uVar13]._someX_2 = 0;
          DAT_UnitsState.units[uVar13]._someY_2 = 0;
          iVar12 = Buildings::BuildingsState::buildingIsAccessible(&DAT_BuildingsState,iVar11,1);
          if ((iVar12 != 0) &&
             (iVar12 = Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                                 (&DAT_PathFindingState,(int)DAT_UnitsState.units[uVar13].owner,
                                  param_5,(int)(short)DAT_TileMapState.PathConnectionLayer
                                                      [DAT_UnitsState.units[uVar13].tile],0),
             iVar12 != 0)) {
            sVar9 = DAT_BuildingsState.buildings[iVar11].buildingEntryY;
            sVar8 = DAT_BuildingsState.buildings[iVar11].buildingEntryX;
            iVar11 = DAT_BuildingsState.buildings[iVar11].uid;
            DAT_UnitsState.units[uVar13].workplaceBuildingID_1 = sVar19;
            DAT_UnitsState.units[uVar13].targetID_OR_targetBuildingID = sVar19;
            DAT_UnitsState.units[uVar13].targetUID = iVar11;
            UnitsState::setDestinationForUnit(&DAT_UnitsState,uVar13,(int)sVar8,(int)sVar9,0);
            DAT_UnitsState.units[uVar13].state.generic = US_LOOK_AROUNDUnk;
            DAT_UnitsState.units[uVar13].targetingType = 0x15;
            UnitsState::deselectUnit(uVar13);
            UnitsState::clearOrDeselectUnitFromSelection
                      (&DAT_UnitsState,DAT_TribesState.tribes[iVar18].owner,uVar13,0);
            return 1;
          }
        }
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
    }
    DAT_TileMapState.showNoRubbleWhenDestroyingBuilding = 1;
    Buildings::BuildingsState::destroyBuilding(&DAT_BuildingsState,iVar11);
    break;
  case UIT_ATTACK_WALL:
  case 0x23:
  case 0x25:
    _unitTribeIndex = 0;
    id_x_tile = 0;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    if (0 < sVar9) {
      do {
        uVar13 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if (((DAT_UnitsState.units[uVar13].logicalState != ULS_NORMAL) ||
            (DAT_UnitsState.units[uVar13].dying != 0)) ||
           (DAT_UnitsState.units[uVar13].field320_0x413 != 0)) goto switchD_005290c7_caseD_6;
        DAT_UnitsState.units[uVar13]._someX_2 = 0;
        DAT_UnitsState.units[uVar13]._someY_2 = 0;
        switch(DAT_UnitsState.units[uVar13].unitType) {
        case UT_E_ARCHER:
        case UT_E_XBOW:
        case UT_A_ARCHER:
        case UT_A_SLINGER:
        case UT_A_ASSASSIN:
        case UT_A_FIRETHROWER:
          goto switchD_005290c7_caseD_16;
        case UT_E_KNIGHT:
switchD_005290c7_caseD_1c:
          _ramOrHorse = _ramOrHorse + 1;
        case UT_TUNNELER:
        case UT_E_SPEAR:
        case UT_E_PIKE:
        case UT_E_MACE:
        case UT_E_SWORD:
        case UT_E_MONK:
        case UT_LORD:
        case UT_A_SLAVE:
        case UT_A_SWORDSMAN:
switchD_005290c7_caseD_5:
          id_x_tile = id_x_tile + 1;
          break;
        case UT_S_CATAPULT:
        case UT_S_TREBUCHET:
        case UT_S_MANGONEL:
        case UT_S_BALLISTA:
        case UT_S_FBALLISTA:
          if (unitInstructionType != 0x25) {
            sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar11];
            DAT_UnitsState.units[uVar13].targetID_OR_targetBuildingID = sVar19;
            DAT_UnitsState.units[uVar13].
            targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
                 unitUID_Y;
            DAT_UnitsState.units[uVar13].attackAtTileY = sVar9;
            DAT_UnitsState.units[uVar13].attackAtTileX =
                 sVar19 - (short)DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
            DAT_UnitsState.units[uVar13].field270_0x3c5 = 0x17;
            DAT_UnitsState.units[uVar13].targetingType = UIT_ATTACK_WALL;
            UnitsState::makeUnitStopWalkingByClearingPathProgressState(uVar13);
            DAT_UnitsState.units[uVar13].shootBeforeStop = 10;
          }
          break;
        case UT_S_TOWER:
          uVar21 = UnitsState::findFreeTileNearby(&DAT_UnitsState,uVar13,iVar11);
          if (uVar21 != 0) {
            UnitsState::setDestinationForUnit
                      (&DAT_UnitsState,uVar13,
                       uVar21 - DAT_ViewportRenderState.translationMatrix
                                [DAT_ViewportRenderState.tileTranslationMatrix_YComponent[uVar21]].
                                addXgetTile,
                       (int)DAT_ViewportRenderState.tileTranslationMatrix_YComponent[uVar21],0);
            sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar11];
            DAT_UnitsState.units[uVar13].targetingType = UIT_ATTACK_WALL;
            DAT_UnitsState.units[uVar13].state.generic = US_MOVE_TO_DESTINATION;
            DAT_UnitsState.units[uVar13].targetID_OR_targetBuildingID = sVar19;
            DAT_UnitsState.units[uVar13].targetedBuildingTile = iVar11;
            DAT_UnitsState.units[uVar13].digTileTarget = uVar21;
            DAT_UnitsState.units[uVar13].attackAtTileY = sVar9;
            DAT_UnitsState.units[uVar13].attackAtTileX =
                 sVar19 - (short)DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
          }
          break;
        case UT_S_BATTERINGRAM:
          if (DAT_UnitsState.units[uVar13].
              digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 == 4) {
            local_8 = local_8 + 1;
            goto switchD_005290c7_caseD_1c;
          }
          break;
        case UT_A_HARCHER:
          _ramOrHorse = _ramOrHorse + 1;
switchD_005290c7_caseD_16:
          if (unitInstructionType == 0x23) goto switchD_005290c7_caseD_5;
        }
switchD_005290c7_caseD_6:
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
    }
    if ((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) &&
       (DAT_GameState.mapAndTime.strongWalls2 != 0)) {
      id_x_tile = local_8;
    }
    if (id_x_tile != 0) {
      sVar9 = DAT_TribesState.tribes[iVar18].selectionTargetUnitID;
      if ((unitInstructionType == UIT_ATTACK_WALL) || (unitInstructionType == 0x25)) {
        sVar8 = DAT_UnitsState.units[sVar9].facingDirection;
        iVar12 = (int)DAT_UnitsState.units[sVar9].owner;
      }
      else {
        sVar8 = DAT_UnitsState.units[sVar9].facingDirection;
        iVar12 = 0;
      }
      Navigation::PathFindingState::
      findFreeSpaceNextToEnemyDefensiveStructureInSameAreaWithinDistance
                (&DAT_PathFindingState,iVar11,id_x_tile,
                 (int *)(int)(short)DAT_TileMapState.PathConnectionLayer
                                    [DAT_UnitsState.units[sVar9].tile],iVar12,0,(int)sVar8);
      sortTribePathDestinationsByCost(&DAT_TribesState,tribeID,_ramOrHorse);
      if ((DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper != 0) &&
         (iVar12 = 0, 0 < DAT_TribesState.tribes[iVar18].size)) {
        id_x_tile = 0x12d5c70;
        do {
          iVar14 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar12);
          iVar12 = iVar12 + 1;
          if (((DAT_UnitsState.units[iVar14].logicalState == ULS_NORMAL) &&
              (DAT_UnitsState.units[iVar14].dying == 0)) &&
             (DAT_UnitsState.units[iVar14].field320_0x413 == 0)) {
            UVar4 = DAT_UnitsState.units[iVar14].unitType;
            switch(UVar4) {
            case UT_TUNNELER:
            case UT_E_SPEAR:
            case UT_E_PIKE:
            case UT_E_MACE:
            case UT_E_SWORD:
            case UT_E_KNIGHT:
            case UT_E_MONK:
            case UT_LORD:
            case UT_A_SLAVE:
            case UT_A_SWORDSMAN:
switchD_0052932a_caseD_5:
              if ((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
                 (DAT_GameState.mapAndTime.strongWalls2 == 0)) goto switchD_0052932a_caseD_3b;
              break;
            case UT_E_ARCHER:
            case UT_E_XBOW:
            case UT_A_ARCHER:
            case UT_A_SLINGER:
            case UT_A_ASSASSIN:
            case UT_A_HARCHER:
            case UT_A_FIRETHROWER:
              if (unitInstructionType == 0x23) goto switchD_0052932a_caseD_5;
              break;
            case UT_S_BATTERINGRAM:
switchD_0052932a_caseD_3b:
              if (UVar4 == UT_S_BATTERINGRAM) {
                if (DAT_UnitsState.units[iVar14].
                    digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 != 4)
                break;
                if (!bVar22) {
                  bVar22 = true;
                  iVar15 = Navigation::PathFindingState::
                           findUnitPreferredOrientationBasedConnectedTile
                                     (&DAT_PathFindingState,iVar14,iVar11);
                  if (iVar15 != 0) {
                    sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar15];
                    unitUID_Y = iVar15 - DAT_ViewportRenderState.translationMatrix[sVar9].
                                         addXgetTile;
                    BVar16 = UnitsState::setDestinationForUnit
                                       (&DAT_UnitsState,iVar14,unitUID_Y,(int)sVar9,0);
                    if (BVar16 != FALSE) {
                      DAT_UnitsState.units[iVar14].targetingType = 0;
                      DAT_UnitsState.units[iVar14].plannedDestinationX = (short)unitUID_Y;
                      DAT_UnitsState.units[iVar14].plannedDestinationY = sVar9;
                      if (DAT_UnitsState.units[iVar14].state.generic == US_MELEE_ATTACK) {
                        DAT_UnitsState.units[iVar14].unknownMovementRelated_0x2d2 =
                             DAT_UnitsState.units[iVar14].movementSpeed * -4;
                      }
                      DAT_UnitsState.units[iVar14].state.generic = US_MOVE_TO_DESTINATION;
                      DAT_UnitsState.units[iVar14].movementType_OR_targetUnitID = 0;
                      DAT_PathFindingState.notAllAssassinsUnk = 0;
                      sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar11];
                      DAT_UnitsState.units[iVar14].targetedBuildingTile = iVar11;
                      DAT_UnitsState.units[iVar14].attackAtTileY = sVar9;
                      DAT_UnitsState.units[iVar14].attackAtTileX =
                           sVar19 - (short)DAT_ViewportRenderState.translationMatrix[sVar9].
                                           addXgetTile;
                      break;
                    }
                  }
                }
              }
              iVar15 = *(int *)(id_x_tile + -4);
              if (iVar15 != 0) {
                sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar15];
                uVar13 = iVar15 - DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
                DAT_UnitsState.units[iVar14].targetingType = 0;
                DAT_UnitsState.units[iVar14].plannedDestinationX = (short)uVar13;
                DAT_UnitsState.units[iVar14].plannedDestinationY = sVar9;
                DAT_PathFindingState.notAllAssassinsUnk = 1;
                if (DAT_UnitsState.units[iVar14].state.generic == US_MELEE_ATTACK) {
                  DAT_UnitsState.units[iVar14].unknownMovementRelated_0x2d2 =
                       DAT_UnitsState.units[iVar14].movementSpeed * -4;
                }
                DAT_UnitsState.units[iVar14].state.generic = US_MOVE_TO_DESTINATION;
                UnitsState::setDestinationForUnit(&DAT_UnitsState,iVar14,uVar13,(int)sVar9,0);
                DAT_PathFindingState.notAllAssassinsUnk = 0;
                uVar13 = *(uint *)id_x_tile;
                sVar9 = *(short *)id_x_tile;
                DAT_UnitsState.units[iVar14].movementType_OR_targetUnitID = 0;
                DAT_UnitsState.units[iVar14].targetedBuildingTile = uVar13;
                sVar8 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[uVar13];
                DAT_UnitsState.units[iVar14].attackAtTileY = sVar8;
                id_x_tile = id_x_tile + 0xc;
                DAT_UnitsState.units[iVar14].attackAtTileX =
                     sVar9 - (short)DAT_ViewportRenderState.translationMatrix[sVar8].addXgetTile;
              }
            }
          }
          if (DAT_TribesState.tribes[iVar18].size <= iVar12) {
            return 1;
          }
        } while( true );
      }
    }
    break;
  case UIT_SET_LADDER:
    iVar12 = 0;
    id_x_tile = 0;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    if (0 < sVar9) {
      do {
        iVar14 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar12);
        iVar12 = iVar12 + 1;
        if (((DAT_UnitsState.units[iVar14].logicalState == ULS_NORMAL) &&
            (DAT_UnitsState.units[iVar14].dying == 0)) &&
           (DAT_UnitsState.units[iVar14].unitType == UT_E_LADDER)) {
          id_x_tile = id_x_tile + 1;
          DAT_UnitsState.units[iVar14]._someX_2 = 0;
          DAT_UnitsState.units[iVar14]._someY_2 = 0;
        }
      } while (iVar12 < DAT_TribesState.tribes[iVar18].size);
      if (id_x_tile != 0) {
        sVar9 = DAT_TribesState.tribes[iVar18].selectionTargetUnitID;
        Navigation::PathFindingState::populateDestinationsArrayWithWallTileAndFreeTilePairInSameArea
                  (&DAT_PathFindingState,iVar11,id_x_tile,
                   (int)(short)DAT_TileMapState.PathConnectionLayer
                               [DAT_UnitsState.units[sVar9].tile],
                   (int)DAT_UnitsState.units[sVar9].owner);
        sortTribePathDestinationsByCost(&DAT_TribesState,tribeID,0);
        if ((DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper != 0) &&
           (iVar11 = 0, 0 < DAT_TribesState.tribes[iVar18].size)) {
          piVar20 = &DAT_PathFindingState.searchQueue.destinationsArray[0].tile2OrAHelper;
          do {
            iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar11);
            iVar11 = iVar11 + 1;
            if ((((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
                 (DAT_UnitsState.units[iVar12].dying == 0)) &&
                (DAT_UnitsState.units[iVar12].unitType == UT_E_LADDER)) &&
               (iVar14 = ((PathHelper12 *)(piVar20 + -1))->tile1, iVar14 != 0)) {
                    /* set ladder men destination to free tile next to defensive structure */
              sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar14];
              uVar13 = iVar14 - DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
              DAT_UnitsState.units[iVar12].targetingType = 0;
              DAT_UnitsState.units[iVar12].plannedDestinationX = (short)uVar13;
              DAT_UnitsState.units[iVar12].plannedDestinationY = sVar9;
              DAT_PathFindingState.notAllAssassinsUnk = 1;
              if (DAT_UnitsState.units[iVar12].state.generic == US_MELEE_ATTACK) {
                DAT_UnitsState.units[iVar12].unknownMovementRelated_0x2d2 =
                     DAT_UnitsState.units[iVar12].movementSpeed * -4;
              }
              DAT_UnitsState.units[iVar12].state.generic =
                   (ushort)(*piVar20 != 0) * 2 + US_MOVE_TO_DESTINATION;
              UnitsState::setDestinationForUnit(&DAT_UnitsState,iVar12,uVar13,(int)sVar9,0);
              DAT_PathFindingState.notAllAssassinsUnk = 0;
              uVar13 = *piVar20;
              iVar14 = *piVar20;
                    /* set ladder man ladder target tile */
              DAT_UnitsState.units[iVar12].targetedBuildingTile = uVar13;
              sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[uVar13];
              DAT_UnitsState.units[iVar12].attackAtTileY = sVar9;
              piVar20 = piVar20 + 3;
              DAT_UnitsState.units[iVar12].attackAtTileX =
                   (short)iVar14 -
                   (short)DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
            }
          } while (iVar11 < DAT_TribesState.tribes[iVar18].size);
          return 1;
        }
      }
    }
    break;
  case 0x1a:
    iVar11 = 0;
    if (0 < sVar9) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,iVar18,iVar11);
        iVar11 = iVar11 + 1;
        if (((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
            (DAT_UnitsState.units[iVar12].dying == 0)) &&
           ((int)(short)DAT_UnitsState.units[iVar12].unitType - 0x27U < 2)) {
          DAT_UnitsState.units[iVar12].field260_0x3b0 = 1;
        }
      } while (iVar11 < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
    break;
  case UIT_DISBAND:
                    /* disband? */
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    _unitTribeIndex = 0;
    if (0 < sVar9) {
      do {
        iVar11 = getUnitIDForIndexInTribe(&DAT_TribesState,iVar18,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if ((DAT_UnitsState.units[iVar11].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[iVar11].dying == 0)) {
          switch(DAT_UnitsState.units[iVar11].unitType) {
          case UT_TUNNELER:
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_E_SPEAR:
          case UT_E_PIKE:
          case UT_E_MACE:
          case UT_E_SWORD:
          case UT_E_KNIGHT:
          case UT_E_LADDER:
          case UT_E_ENGINEER:
          case UT_E_MONK:
          case UT_A_ARCHER:
          case UT_A_SLAVE:
          case UT_A_SLINGER:
          case UT_A_ASSASSIN:
          case UT_A_HARCHER:
          case UT_A_SWORDSMAN:
          case UT_A_FIRETHROWER:
            UnitsState::disbandUnit(&DAT_UnitsState,iVar11);
            break;
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
          case UT_S_MANGONEL:
          case UT_S_TOWER:
          case UT_S_BATTERINGRAM:
          case UT_S_SHIELD:
          case UT_S_BALLISTA:
          case UT_S_FBALLISTA:
            giveTribeAnInstruction
                      (&DAT_TribesState,iVar18,UIT_EXIT_SIEGE_EQUIPMENT,iVar11,
                       DAT_UnitsState.units[iVar11].uid,1);
            bVar22 = DAT_GameCore.gameMode_2 == GM_SIEGE_THAT;
            DAT_UnitsState.units[iVar11].state.generic = US_DISAPPEAR;
            if (bVar22) {
              Buildings::BuildingsState::getPriceForDisbandedUnitType
                        (&DAT_BuildingsState,(int)(short)DAT_UnitsState.units[iVar11].unitType,
                         &tribeID);
              piVar20 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                        startResources + 0xf;
              *piVar20 = *piVar20 + tribeID;
            }
          }
        }
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
    }
    UnitsState::deselectAllUnitsOneByOne(&DAT_UnitsState);
    UnitsState::clearOrDeselectUnitFromSelection
              (&DAT_UnitsState,DAT_TribesState.tribes[iVar18].owner,0,0);
    return 1;
  case UIT_STOP:
    iVar11 = 0;
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    DAT_TribesState.tribes[tribeID].someUnitID = 0;
    if (0 < sVar9) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar11);
        iVar11 = iVar11 + 1;
        if (((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
            (DAT_UnitsState.units[iVar12].dying == 0)) &&
           (DAT_UnitsState.units[iVar12].field320_0x413 == 0)) {
          DAT_UnitsState.units[iVar12].field270_0x3c5 = 3;
          DAT_UnitsState.units[iVar12].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
          DAT_UnitsState.units[iVar12].field260_0x3b0 = 0;
          UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
          DAT_UnitsState.units[iVar12].targetedBuildingTile = 0;
          DAT_UnitsState.units[iVar12].movementType_OR_targetUnitID = 0;
        }
      } while (iVar11 < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
    break;
  case 0x20:
  case UIT_SHOOT_TARGETUnk:
    local_8 = id_x_tile * 0x490;
    pUVar6 = DAT_UnitsState.units + id_x_tile;
    _unitTribeIndex = 0;
    id_x_tile = 0;
    if (pUVar6->uid != unitUID_Y) {
      return 0;
    }
    if (0 < sVar9) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if ((((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
             (DAT_UnitsState.units[iVar12].dying == 0)) &&
            (DAT_UnitsState.units[iVar12].field320_0x413 == 0)) &&
           (UVar3 = DAT_UnitsState.units[iVar12].state.generic, UVar3 != US_MELEE_ATTACK)) {
          switch(DAT_UnitsState.units[iVar12].unitType) {
          case UT_TUNNELER:
          case UT_E_SPEAR:
          case UT_E_PIKE:
          case UT_E_MACE:
          case UT_E_SWORD:
          case UT_E_KNIGHT:
          case UT_E_MONK:
          case UT_LORD:
          case UT_A_SLAVE:
          case UT_A_ASSASSIN:
          case UT_A_SWORDSMAN:
            if (unitInstructionType != UIT_SHOOT_TARGETUnk) {
              id_x_tile = id_x_tile + 1;
            }
            break;
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_E_ARCHER_DEBUG:
          case UT_A_ARCHER:
          case UT_A_SLINGER:
          case UT_A_HARCHER:
          case UT_A_FIRETHROWER:
switchD_005282f6_caseD_16:
            if (UVar3 == 0x69) {
              DAT_UnitsState.units[iVar12].state.generic = US_MOVE_TO_DESTINATION;
            }
            DAT_UnitsState.units[iVar12].targetingType = UIT_UNIT_ATTACK_UNIT;
            DAT_UnitsState.units[iVar12].targetedUnitID__OR__engineerMannedSiegeEngineRef = sVar19;
            DAT_UnitsState.units[iVar12].
            targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
                 unitUID_Y;
            DAT_UnitsState.units[iVar12].field300_0x3f8 = 0;
            if (DAT_UnitsState.units[iVar11].unitType == UT_RABBIT) {
              DAT_TribesState.tribes[iVar18].field71_0x212 = 1;
            }
            if (DAT_UnitsState.units[iVar12]._someX_2 == 0) {
              sVar9 = DAT_UnitsState.units[iVar12].destinationY_2Unk;
              DAT_UnitsState.units[iVar12]._someX_2 = DAT_UnitsState.units[iVar12].destinationX_2Unk
              ;
              DAT_UnitsState.units[iVar12]._someY_2 = sVar9;
            }
            UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
            break;
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
            if (unitInstructionType != UIT_SHOOT_TARGETUnk) {
              sVar9 = DAT_UnitsState.units[iVar12]._someX_2;
              DAT_UnitsState.units[iVar12].field270_0x3c5 = 5;
              DAT_UnitsState.units[iVar12].targetingType = UIT_ATTACK_LAND;
              DAT_UnitsState.units[iVar12].attackAtTileX = DAT_UnitsState.units[iVar11].x;
              DAT_UnitsState.units[iVar12].attackAtTileY = DAT_UnitsState.units[iVar11].y;
              DAT_UnitsState.units[iVar12].unkAttackRelated = 0xb;
              if (sVar9 == 0) {
                sVar9 = DAT_UnitsState.units[iVar12].destinationY_2Unk;
                DAT_UnitsState.units[iVar12]._someX_2 =
                     DAT_UnitsState.units[iVar12].destinationX_2Unk;
                DAT_UnitsState.units[iVar12]._someY_2 = sVar9;
              }
              UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
              DAT_UnitsState.units[iVar12].shootBeforeStop = 10;
            }
            break;
          case UT_S_MANGONEL:
          case UT_S_BALLISTA:
          case UT_S_FBALLISTA:
            if (unitInstructionType != UIT_SHOOT_TARGETUnk) {
              DAT_UnitsState.units[iVar12].shootBeforeStop = 10;
              goto switchD_005282f6_caseD_16;
            }
          }
        }
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
      if (id_x_tile != 0) {
        iVar12 = (int)DAT_TribesState.tribes[iVar18].selectionTargetUnitID;
        param_5 = (int)DAT_UnitsState.units[iVar12].x;
        unitInstructionType = (UnitInstructionType)DAT_UnitsState.units[iVar12].y;
        predictUnitInterceptPosition
                  (&DAT_TribesState,iVar12,iVar11,&param_5,(int *)&unitInstructionType);
        Navigation::PathFindingState::pathPlanningForTribe
                  (&DAT_PathFindingState,tribeID,iVar11,param_5,unitInstructionType,id_x_tile,
                   (int)(short)DAT_TileMapState.PathConnectionLayer
                               [DAT_UnitsState.units[iVar12].tile],
                   (int)DAT_UnitsState.units[iVar12].owner);
        DAT_TribesState.tribes[iVar18].someUnitID = sVar19;
        DAT_TribesState.tribes[iVar18].someUnitUID = unitUID_Y;
        DAT_TribesState.tribes[iVar18].someTile = DAT_UnitsState.units[iVar11].tile;
        iVar12 = 0;
        sVar9 = DAT_TribesState.tribes[iVar18].size;
        DAT_TribesState.tribes[iVar18].someTile2 =
             (int)DAT_UnitsState.units[iVar11].destinationX_2Unk +
             DAT_ViewportRenderState.translationMatrix
             [DAT_UnitsState.units[iVar11].destinationY_2Unk].addXgetTile;
        unitInstructionType = 0;
        if (0 < sVar9) {
          id_x_tile = 0x12d5c6c;
          do {
            iVar14 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,iVar12);
            iVar12 = iVar12 + 1;
            if (((DAT_UnitsState.units[iVar14].logicalState == ULS_NORMAL) &&
                (DAT_UnitsState.units[iVar14].dying == 0)) &&
               ((DAT_UnitsState.units[iVar14].field320_0x413 == 0 &&
                (DAT_UnitsState.units[iVar14].state.generic != US_MELEE_ATTACK)))) {
              switch(DAT_UnitsState.units[iVar14].unitType) {
              case UT_TUNNELER:
              case UT_E_SPEAR:
              case UT_E_PIKE:
              case UT_E_MACE:
              case UT_E_SWORD:
              case UT_E_KNIGHT:
              case UT_E_MONK:
              case UT_LORD:
              case UT_A_SLAVE:
              case UT_A_ASSASSIN:
              case UT_A_SWORDSMAN:
                iVar15 = *(int *)id_x_tile;
                if (iVar15 != 0) {
                  sVar9 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar15];
                  uVar13 = iVar15 - DAT_ViewportRenderState.translationMatrix[sVar9].addXgetTile;
                  if (*(int *)(id_x_tile + 4) == 0) {
                    DAT_UnitsState.units[iVar14].targetingType = 0;
                    if (DAT_UnitsState.units[iVar14].unitType == UT_LORD) break;
                  }
                  else {
                    DAT_UnitsState.units[iVar14].targetingType = UIT_UNIT_ATTACK_UNIT;
                    DAT_UnitsState.units[iVar14].targetedUnitID__OR__engineerMannedSiegeEngineRef =
                         sVar19;
                    DAT_UnitsState.units[iVar14].
                    targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID
                         = unitUID_Y;
                  }
                  DAT_UnitsState.units[iVar14].plannedDestinationX = (short)uVar13;
                  DAT_UnitsState.units[iVar14].plannedDestinationY = sVar9;
                  DAT_UnitsState.units[iVar14].targetedBuildingTile = 0;
                  if (DAT_UnitsState.units[iVar14].state.generic == US_MELEE_ATTACK) {
                    DAT_UnitsState.units[iVar14].unknownMovementRelated_0x2d2 =
                         DAT_UnitsState.units[iVar14].movementSpeed * -4;
                  }
                  if (DAT_UnitsState.units[iVar14]._someX_2 == 0) {
                    DAT_UnitsState.units[iVar14]._someX_2 =
                         DAT_UnitsState.units[iVar14].destinationX_2Unk;
                    DAT_UnitsState.units[iVar14]._someY_2 =
                         DAT_UnitsState.units[iVar14].destinationY_2Unk;
                  }
                  DAT_UnitsState.units[iVar14].state.generic = US_MOVE_TO_DESTINATION;
                  BVar16 = isTribeAllAssassins(&DAT_TribesState,tribeID);
                  if (BVar16 == FALSE) {
                    DAT_PathFindingState.notAllAssassinsUnk = 1;
                  }
                  else {
                    DAT_PathFindingState.allAssassinsUnk = 1;
                  }
                  UnitsState::setDestinationForUnit(&DAT_UnitsState,iVar14,uVar13,(int)sVar9,0);
                  DAT_UnitsState.units[iVar14].moveDelay = 0;
                  DAT_UnitsState.units[iVar14].lookForEnemy = -0x32;
                  if (DAT_UnitsState.units[iVar14].movementType_OR_targetUnitID != iVar11) {
                    DAT_UnitsState.units[iVar14].movementType_OR_targetUnitID = sVar19;
                    psVar1 = (short *)((int)&DAT_UnitsState.units[0].huntedBy + local_8);
                    *psVar1 = *psVar1 + 1;
                  }
                  UVar10 = (int)DAT_UnitsState.units[iVar14].totalSizeOfPathPlan / 2;
                  if ((int)unitInstructionType < (int)UVar10) {
                    unitInstructionType = UVar10;
                  }
                  id_x_tile = id_x_tile + 0xc;
                  DAT_PathFindingState.notAllAssassinsUnk = 0;
                }
              }
            }
          } while (iVar12 < DAT_TribesState.tribes[iVar18].size);
        }
        iVar11 = unitInstructionType * 8;
        if (iVar11 < 9) {
          iVar11 = 8;
        }
        DAT_TribesState.tribes[iVar18].field168_0x2be = (short)iVar11;
        return 1;
      }
    }
    break;
  case UIT_LIGHT_PITCH:
    DAT_TribesState.tribes[tribeID].isRallyingUnk = 0;
    _unitTribeIndex = 0;
    if ((DAT_TileMapState.pitchDitches[id_x_tile].uid == unitUID_Y) && (0 < sVar9)) {
      do {
        iVar12 = getUnitIDForIndexInTribe(&DAT_TribesState,tribeID,_unitTribeIndex);
        _unitTribeIndex = _unitTribeIndex + 1;
        if ((DAT_UnitsState.units[iVar12].logicalState == ULS_NORMAL) &&
           (DAT_UnitsState.units[iVar12].dying == 0)) {
          DAT_UnitsState.units[iVar12]._someX_2 = 0;
          DAT_UnitsState.units[iVar12]._someY_2 = 0;
          UVar4 = DAT_UnitsState.units[iVar12].unitType;
          if ((UVar4 == UT_E_ARCHER) || (UVar4 == UT_A_ARCHER)) {
            sVar9 = DAT_TileMapState.pitchDitches[iVar11].y;
            DAT_UnitsState.units[iVar12].shootTargetMicroX =
                 DAT_TileMapState.pitchDitches[iVar11].x * 8 + 4;
            iVar14 = DAT_TileMapState.pitchDitches[iVar11].tile;
            DAT_UnitsState.units[iVar12].shootTargetMicroY = sVar9 * 8 + 4;
            DAT_UnitsState.units[iVar12].shootTargetZ = (ushort)DAT_TileMapState.HeightLayer[iVar14]
            ;
            DAT_UnitsState.units[iVar12].shootTargetedUnit = -1;
            DAT_UnitsState.units[iVar12].targetID_OR_targetBuildingID = sVar19;
            DAT_UnitsState.units[iVar12].
            targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID =
                 unitUID_Y;
            DAT_UnitsState.units[iVar12].field270_0x3c5 = 0x22;
            DAT_UnitsState.units[iVar12].targetingType = UIT_LIGHT_PITCH;
            DAT_UnitsState.units[iVar12].field300_0x3f8 = 0;
            UnitsState::makeUnitStopWalkingByClearingPathProgressState(iVar12);
            DAT_UnitsState.units[iVar12].shootBeforeStop = 10;
          }
        }
      } while (_unitTribeIndex < DAT_TribesState.tribes[iVar18].size);
      return 1;
    }
  }
  return 1;
}



