// ================= acquireShootTarget @ 0054b0d0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::Units::UnitsState::acquireShootTarget(UnitsState *this,short *unitID)

{
  short *psVar1;
  short *psVar2;
  short *psVar3;
  UnitTypeShort UVar4;
  UnitInstructionTypeShort UVar5;
  int iVar6;
  int iVar7;
  int microY;
  int iVar8;
  int iVar9;
  int iVar10;
  uint y;
  BOOLEnum BVar11;
  int iVar12;
  short sVar13;
  int iVar14;
  uint x;
  int iVar15;
  short sVar16;
  int iVar17;
  UnitInstructionTypeShort *pUVar18;
  undefined8 uVar19;
  int _entityType;
  int local_30;
  int local_2c;
  int _validTargetID;
  int local_10;
  int local_c;
  int local_8;
  
  psVar3 = unitID;
  iVar6 = (int)DAT_UnitsState.units[(int)unitID].owner;
  iVar7 = (int)DAT_UnitsState.units[(int)unitID].microXPosition;
  microY = (int)DAT_UnitsState.units[(int)unitID].microYPosition;
  iVar8 = (int)DAT_UnitsState.units[(int)unitID].buildingHeight +
          (int)DAT_UnitsState.units[(int)unitID].terrainOrClimbHeight;
  iVar17 = 0;
  _validTargetID = 0;
  local_30 = 100000;
  local_8 = 0;
  local_2c = 100000;
  local_10 = 0;
  local_c = 0;
                    /* switch based on unit type */
  switch(DAT_UnitsState.units[(int)unitID].unitType) {
  case UT_E_XBOW:
                    /* crossbow */
    _entityType = 7;
    break;
  default:
                    /* default: */
    _entityType = 1;
    break;
  case UT_S_CATAPULT:
                    /* catapult */
    _entityType = 2;
    if ((DAT_UnitsState.units[(int)unitID].stoneAmmunition < 1) &&
       (DAT_UnitsState.units[(int)unitID].targetingType != UIT_THROW_COW)) {
      DAT_UnitsState.units[(int)unitID].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
      return FALSE;
    }
    break;
  case UT_S_TREBUCHET:
                    /* trebuchet */
    _entityType = 3;
    if ((DAT_UnitsState.units[(int)unitID].stoneAmmunition < 1) &&
       (DAT_UnitsState.units[(int)unitID].targetingType != UIT_THROW_COW)) {
      DAT_UnitsState.units[(int)unitID].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
      return FALSE;
    }
    break;
  case UT_S_MANGONEL:
                    /* mangonel */
    _entityType = 4;
    break;
  case UT_S_BALLISTA:
                    /* ballista */
    _entityType = 0x14;
    break;
  case UT_A_SLINGER:
                    /* slinger */
    _entityType = 0x21;
    break;
  case UT_A_FIRETHROWER:
                    /* fire thrower */
    _entityType = 0x22;
    break;
  case UT_S_FBALLISTA:
                    /* fire ballista */
    _entityType = 0x25;
  }
  iVar9 = DAT_EntityDefinedData.DAT_EntityTypeArrayForProjectileRange[_entityType] *
          DAT_EntityDefinedData.DAT_EntityTypeArrayForProjectileRange[_entityType];
                    /* fetch attacking explicitness */
  if (DAT_UnitsState.units[(int)unitID].targetingType == UIT_UNIT_ATTACK_UNIT) {
                    /* if explicitness = 4 (user selected attack)...
                       fetch the targetedUnitID */
    sVar13 = DAT_UnitsState.units[(int)unitID].targetedUnitID__OR__engineerMannedSiegeEngineRef;
    iVar10 = (int)sVar13;
    if (((DAT_UnitsState.units[iVar10].uid ==
          DAT_UnitsState.units[(int)unitID].
          targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID) &&
        (DAT_UnitsState.units[iVar10].dying == 0)) &&
       (DAT_UnitsState.units[iVar10].logicalState == ULS_NORMAL)) {
      uVar19 = checkIfCitizenUnitIsAliveBasedOnState(iVar10);
      iVar17 = (int)((ulonglong)uVar19 >> 0x20);
      if ((((int)uVar19 == 0) &&
          (DAT_UnitsState.units[iVar10].state.generic != (US_STONE_DEATH_03|US_IDLEUnk))) &&
         (DAT_GameState.mapAndTime.playerTeams[DAT_UnitsState.units[iVar10].owner] !=
          DAT_GameState.mapAndTime.playerTeams[iVar6])) {
        psVar1 = &DAT_UnitsState.units[iVar10].microYPosition;
        psVar2 = &DAT_UnitsState.units[iVar10].microXPosition;
        iVar14 = ((int)(microY + (microY >> 0x1f & 7U)) >> 3) -
                 ((int)((int)*psVar1 + ((int)*psVar1 >> 0x1f & 7U)) >> 3);
        iVar17 = ((int)(iVar7 + (iVar7 >> 0x1f & 7U)) >> 3) -
                 ((int)((int)*psVar2 + ((int)*psVar2 >> 0x1f & 7U)) >> 3);
        if (iVar17 * iVar17 + iVar14 * iVar14 <= iVar9) {
          psVar3 = &DAT_UnitsState.units[iVar10].terrainOrClimbHeight;
          iVar6 = Entities::EntityState::arrowShootingRelated
                            (&DAT_EntityState,iVar7,microY,iVar8 + 0x1e,(int)*psVar2,(int)*psVar1,
                             DAT_UnitsState.units[iVar10].buildingHeight + 0x1a +
                             (int)DAT_UnitsState.units[iVar10].terrainOrClimbHeight);
          if (((iVar6 < 1) ||
              (UVar4 = DAT_UnitsState.units[(int)unitID].unitType, UVar4 == UT_S_MANGONEL)) ||
             (UVar4 == UT_S_BALLISTA)) {
            if (DAT_UnitsState.units[(int)unitID].unitType == UT_HUNTER) {
              return FALSE;
            }
            DAT_UnitsState.units[(int)unitID].shootTargetedUnit = -2;
            DAT_UnitsState.units[(int)unitID].shootTargetMicroX = *psVar2;
            DAT_UnitsState.units[(int)unitID].shootTargetMicroY = *psVar1;
            DAT_UnitsState.units[(int)unitID].shootTargetZ = *psVar3;
            return TRUE;
          }
          DAT_UnitsState.units[(int)unitID].shootTargetedUnit = sVar13;
          DAT_UnitsState.units[(int)unitID].targetUID = DAT_UnitsState.units[iVar10].uid;
          DAT_UnitsState.units[(int)unitID].distanceToEnemyUnitLadders = (short)iVar6;
          DAT_UnitsState.units[(int)unitID].shootTargetMicroX = *psVar2;
          DAT_UnitsState.units[(int)unitID].shootTargetMicroY = *psVar1;
          DAT_UnitsState.units[(int)unitID].shootTargetZ = *psVar3;
          if (100 < iVar6) {
            DAT_UnitsState.units[(int)unitID].jugglerCount = 0;
            DAT_UnitsState.units[iVar10].field250_0x39a = 1;
            return TRUE;
          }
          iVar6 = (int)*psVar3 + (int)DAT_UnitsState.units[iVar10].buildingHeight;
          iVar7 = (int)DAT_UnitsState.units[(int)unitID].buildingHeight +
                  (int)DAT_UnitsState.units[(int)unitID].terrainOrClimbHeight;
          if (iVar6 + 0x46 < iVar7) {
            DAT_UnitsState.units[(int)unitID].jugglerCount = 1;
            DAT_UnitsState.units[iVar10].field250_0x39a = 1;
            return TRUE;
          }
          DAT_UnitsState.units[(int)unitID].jugglerCount = (iVar6 + -0x46 <= iVar7) - 1;
          DAT_UnitsState.units[iVar10].field250_0x39a = 1;
          return TRUE;
        }
        if (DAT_GameSynchronyState.currentPlayerFullIDArray[DAT_UnitsState.units[(int)unitID].owner]
            != -1) {
          return FALSE;
        }
        iVar17 = 0;
      }
    }
                    /* fixme */
    sVar13 = DAT_UnitsState.units[(int)unitID]._someX_2;
    sVar16 = (short)iVar17;
                    /* fixmefixme */
    DAT_UnitsState.units[(int)unitID].targetedUnitID__OR__engineerMannedSiegeEngineRef = sVar16;
    DAT_UnitsState.units[(int)unitID].shootTargetedUnit = sVar16;
    DAT_UnitsState.units[(int)unitID].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
    if (sVar13 != sVar16) {
      setDestinationForUnit
                (&DAT_UnitsState,(int)unitID,(int)sVar13,
                 (int)DAT_UnitsState.units[(int)unitID]._someY_2,0);
      DAT_UnitsState.units[(int)unitID]._someX_2 = 0;
      DAT_UnitsState.units[(int)unitID]._someY_2 = 0;
      DAT_UnitsState.units[(int)unitID].moveDelay = 0;
      DAT_UnitsState.units[(int)unitID].targetedBuildingTile = 0;
      DAT_UnitsState.units[(int)unitID].state.generic = US_MOVE_TO_DESTINATION;
      return TRUE;
    }
  }
  pUVar18 = &DAT_UnitsState.units[(int)unitID].targetingType;
  UVar5 = *pUVar18;
  if (UVar5 == UIT_LIGHT_PITCH) {
                    /* get the workplace building id */
    sVar13 = DAT_UnitsState.units[(int)unitID].targetID_OR_targetBuildingID;
    if ((DAT_TileMapState.pitchDitches[sVar13].uid ==
         DAT_UnitsState.units[(int)unitID].
         targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID) &&
       (iVar6 = Entities::EntityState::isBrazierNearby
                          (&DAT_EntityState,(int)DAT_UnitsState.units[(int)unitID].x,
                           (int)DAT_UnitsState.units[(int)unitID].y,
                           (int)DAT_UnitsState.units[(int)unitID].buildingHeight +
                           (int)DAT_UnitsState.units[(int)unitID].terrainOrClimbHeight), iVar6 != 0)
       ) {
      DAT_UnitsState.units[(int)unitID].shootTargetMicroX =
           DAT_TileMapState.pitchDitches[sVar13].x * 8 + 4;
      DAT_UnitsState.units[(int)unitID].shootTargetMicroY =
           DAT_TileMapState.pitchDitches[sVar13].y * 8 + 4;
      DAT_UnitsState.units[(int)unitID].shootTargetZ =
           (ushort)DAT_TileMapState.HeightLayer[DAT_TileMapState.pitchDitches[sVar13].tile];
      DAT_UnitsState.units[(int)unitID].shootTargetedUnit = -1;
      return TRUE;
    }
  }
  else if (UVar5 == UIT_ATTACK_BUILDING) {
    sVar13 = DAT_UnitsState.units[(int)unitID].targetID_OR_targetBuildingID;
    if (DAT_BuildingsState.buildings[sVar13].uid ==
        DAT_UnitsState.units[(int)unitID].
        targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID) {
      DAT_UnitsState.units[(int)unitID].shootTargetMicroX =
           DAT_BuildingsState.buildings[sVar13].x * 8 +
           (short)((int)(DAT_BuildingsState.buildings[sVar13].widthOrHeight * 8) / 2);
      DAT_UnitsState.units[(int)unitID].shootTargetMicroY =
           DAT_BuildingsState.buildings[sVar13].y * 8 +
           (short)((int)(DAT_BuildingsState.buildings[sVar13].widthOrHeight * 8) / 2);
      DAT_UnitsState.units[(int)unitID].shootTargetZ =
           DAT_BuildingsState.buildings[sVar13].terrainHeightUnk;
      DAT_UnitsState.units[(int)unitID].shootTargetedUnit = -1;
      return TRUE;
    }
  }
  else if (UVar5 == UIT_ATTACK_WALL) {
    y = (uint)DAT_UnitsState.units[(int)unitID].attackAtTileY;
    x = (uint)DAT_UnitsState.units[(int)unitID].attackAtTileX;
    iVar6 = DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x;
    BVar11 = Rendering::ViewportRenderState::xyAreValid(&DAT_ViewportRenderState,x,y);
    if ((BVar11 != FALSE) && ((DAT_TileMapState.LogicLayer[iVar6] & 0x100U) != 0)) {
      DAT_UnitsState.units[(int)unitID].shootTargetMicroX =
           DAT_UnitsState.units[(int)unitID].attackAtTileX * 8;
      DAT_UnitsState.units[(int)unitID].shootTargetMicroY =
           DAT_UnitsState.units[(int)unitID].attackAtTileY * 8;
      DAT_UnitsState.units[(int)unitID].shootTargetZ =
           (short)((int)((uint)DAT_TileMapState.HeightLayer[iVar6] -
                        (uint)DAT_TileMapState.DefaultHeightLayer[iVar6]) / 2) +
           (ushort)DAT_TileMapState.DefaultHeightLayer[iVar6];
      DAT_UnitsState.units[(int)unitID].shootTargetedUnit = -1;
      return TRUE;
    }
  }
  else {
    if ((UVar5 != UIT_ATTACK_LAND) && (UVar5 != UIT_THROW_COW)) {
      if (_entityType == 2) {
        return FALSE;
      }
      if (_entityType == 3) {
        return FALSE;
      }
      if (DAT_GameState.playerDataArray[iVar6].enemies <= iVar17) {
        return FALSE;
      }
      unitID = DAT_GameState.playerDataArray[iVar6].enemyIDArray;
      do {
        iVar10 = (int)*unitID;
        if ((DAT_UnitsState.units[iVar10].dying != 0) ||
           (DAT_UnitsState.units[iVar10].uid != *(int *)(iVar6 * 10000 + 0x11a66f0 + iVar17 * 4)))
        goto switchD_0054ba67_caseD_1f;
        switch(DAT_UnitsState.units[iVar10].unitType) {
        case UT_ANTELOPESHDEER:
          if (DAT_UnitsState.units[(int)psVar3].unitType != UT_HUNTER)
          goto switchD_0054ba67_caseD_1f;
          break;
        case UT_LIONSHWOLF:
          sVar13 = DAT_UnitsState.units[iVar10].tribeID;
          if ((DAT_TribesState.tribes[sVar13].unknownBool02 != 0) ||
             ((DAT_TribesState.tribes[sVar13].unknownBool01 == 0 &&
              ((DAT_UnitsState.units[iVar10].state.generic != 0xcf ||
               (DAT_UnitsState.units
                [DAT_UnitsState.units[iVar10].targetedUnitID__OR__engineerMannedSiegeEngineRef].
                unknownTestAgainst0_1 != 0)))))) goto switchD_0054ba67_caseD_1f;
          break;
        case UT_RABBIT:
          iVar14 = (int)DAT_UnitsState.units[(int)psVar3].tribeID;
          if (((DAT_UnitsState.units[(int)psVar3].unitType == UT_HUNTER) || (iVar14 < 1)) ||
             (DAT_TribesState.tribes[iVar14].field71_0x212 == 0)) goto switchD_0054ba67_caseD_1f;
          break;
        case UT_CAGEDOG:
          if (DAT_GameState.mapAndTime.playerTeams
              [DAT_UnitsState.units[iVar10].displayColorPlayerID] ==
              DAT_GameState.mapAndTime.playerTeams[DAT_UnitsState.units[(int)psVar3].owner])
          goto switchD_0054ba67_caseD_1f;
          break;
        case UT_A_ASSASSIN:
          if (0xa0 < DAT_UnitsState.units[iVar10].assassinsMicroDistanceToEnemyUnk)
          goto switchD_0054ba67_caseD_1f;
        }
        iVar14 = (int)DAT_UnitsState.units[iVar10].microYPosition;
        iVar12 = (int)DAT_UnitsState.units[iVar10].microXPosition;
        iVar15 = ((int)(microY + (microY >> 0x1f & 7U)) >> 3) -
                 ((int)(iVar14 + (iVar14 >> 0x1f & 7U)) >> 3);
        iVar14 = ((int)(iVar7 + (iVar7 >> 0x1f & 7U)) >> 3) -
                 ((int)(iVar12 + (iVar12 >> 0x1f & 7U)) >> 3);
        if (iVar9 < iVar14 * iVar14 + iVar15 * iVar15) goto switchD_0054ba67_caseD_1f;
        iVar14 = (int)DAT_UnitsState.units[iVar10].microXPosition;
        if (iVar14 < iVar7) {
          iVar14 = iVar7 - iVar14;
        }
        else {
          iVar14 = iVar14 - iVar7;
        }
        iVar12 = (int)DAT_UnitsState.units[iVar10].microYPosition;
        if (iVar12 < microY) {
          iVar15 = microY - iVar12;
        }
        else {
          iVar15 = iVar12 - microY;
        }
        if (iVar14 < iVar15) {
          iVar14 = iVar15;
        }
        iVar14 = iVar14 + DAT_UnitsState.units[iVar10].field282_0x3dc * 0x32;
        if (_entityType == 4) {
          switch(DAT_UnitsState.units[iVar10].unitType) {
          case UT_E_ENGINEER:
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
          case UT_S_MANGONEL:
          case UT_S_TOWER:
          case UT_S_BATTERINGRAM:
          case UT_S_SHIELD:
          case UT_S_BALLISTA:
          case UT_S_FBALLISTA:
            break;
          default:
            if (DAT_GameSynchronyState.currentPlayerFullIDArray
                [DAT_UnitsState.units[(int)psVar3].owner] != -1) goto switchD_0054ba67_caseD_1f;
            if (DAT_UnitsState.units[iVar10].isSelectable_OR_matchTime == 0) {
              iVar14 = (iVar14 * 5 + 0x32) * 2;
            }
            else {
              iVar14 = iVar14 * 3 + 100;
            }
          }
          goto joined_r0x0054ba0c;
        }
        if (_entityType == 0x14) {
          switch(DAT_UnitsState.units[iVar10].unitType) {
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_E_SPEAR:
          case UT_E_MACE:
          case UT_E_LADDER:
          case UT_A_ARCHER:
          case UT_A_SLAVE:
          case UT_A_SLINGER:
          case UT_A_ASSASSIN:
          case UT_A_HARCHER:
switchD_0054ba37_caseD_16:
            iVar14 = iVar14 * 5 + 200;
            break;
          case UT_E_PIKE:
          case UT_E_SWORD:
          case UT_E_KNIGHT:
          case UT_A_SWORDSMAN:
            break;
          case UT_E_ENGINEER:
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
          case UT_S_MANGONEL:
          case UT_LORD:
          case UT_S_TOWER:
          case UT_S_BATTERINGRAM:
          case UT_S_SHIELD:
          case UT_S_BALLISTA:
          case UT_A_FIRETHROWER:
          case UT_S_FBALLISTA:
switchD_0054ba37_caseD_1e:
            iVar14 = iVar14 * 2 + 100;
            break;
          default:
switchD_0054ba37_caseD_1f:
            iVar14 = (iVar14 * 5 + 200) * 2;
          }
          goto switchD_0054ba37_caseD_19;
        }
        if (_entityType != 0x25) {
          if ((DAT_UnitsState.units[iVar10].field306_0x3ff != 0) &&
             (DAT_GameSynchronyState.currentPlayerFullIDArray[DAT_UnitsState.units[iVar10].owner] ==
              -1)) {
            iVar14 = iVar14 / 3;
          }
          switch(DAT_UnitsState.units[iVar10].unitType) {
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_A_ARCHER:
          case UT_A_HARCHER:
            iVar14 = iVar14 + 0x4b;
            break;
          case UT_E_SPEAR:
          case UT_E_PIKE:
          case UT_E_MACE:
          case UT_E_SWORD:
          case UT_E_KNIGHT:
          case UT_A_SLAVE:
          case UT_A_SLINGER:
          case UT_A_ASSASSIN:
          case UT_A_SWORDSMAN:
            goto switchD_0054ba37_caseD_16;
          case UT_E_LADDER:
            iVar14 = iVar14 * 7 + 300;
            break;
          case UT_E_ENGINEER:
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
          case UT_LORD:
            goto switchD_0054ba37_caseD_1e;
          default:
            goto switchD_0054ba37_caseD_1f;
          case UT_S_MANGONEL:
          case UT_S_BALLISTA:
          case UT_A_FIRETHROWER:
          case UT_S_FBALLISTA:
            break;
          }
          goto switchD_0054ba37_caseD_19;
        }
        switch(DAT_UnitsState.units[iVar10].unitType) {
        case UT_E_ARCHER:
        case UT_E_XBOW:
        case UT_E_SPEAR:
        case UT_E_MACE:
        case UT_E_LADDER:
        case UT_A_ARCHER:
        case UT_A_SLAVE:
        case UT_A_SLINGER:
        case UT_A_ASSASSIN:
        case UT_A_HARCHER:
switchD_0054ba67_caseD_16:
          iVar14 = iVar14 * 5 + 200;
          break;
        case UT_E_PIKE:
        case UT_E_SWORD:
        case UT_E_KNIGHT:
        case UT_A_SWORDSMAN:
          break;
        case UT_E_ENGINEER:
        case UT_S_CATAPULT:
        case UT_S_TREBUCHET:
        case UT_S_MANGONEL:
        case UT_S_TOWER:
        case UT_S_BATTERINGRAM:
        case UT_S_SHIELD:
        case UT_S_BALLISTA:
        case UT_A_FIRETHROWER:
        case UT_S_FBALLISTA:
          iVar14 = iVar14 * 2 + 100;
          break;
        default:
          goto switchD_0054ba67_caseD_1f;
        case UT_LORD:
          if (DAT_GameSynchronyState.currentPlayerFullIDArray[iVar6] != -1)
          goto switchD_0054ba67_caseD_16;
          goto switchD_0054ba67_caseD_1f;
        }
joined_r0x0054ba0c:
        if (iVar14 != -1) {
switchD_0054ba37_caseD_19:
          if (((iVar14 < local_30) || (iVar14 < local_2c)) &&
             (iVar12 = Entities::EntityState::arrowShootingRelated
                                 (&DAT_EntityState,iVar7,microY,iVar8 + 0x1e,
                                  (int)DAT_UnitsState.units[iVar10].microXPosition,iVar12,
                                  DAT_UnitsState.units[iVar10].buildingHeight + 0x1a +
                                  (int)DAT_UnitsState.units[iVar10].terrainOrClimbHeight),
             0 < iVar12)) {
            if (iVar14 < local_30) {
              local_30 = iVar14;
              _validTargetID = iVar10;
              local_8 = iVar12;
            }
            if ((DAT_UnitsState.units[iVar10].field250_0x39a == 0) && (iVar14 < local_2c)) {
              local_2c = iVar14;
              local_10 = iVar10;
              local_c = iVar12;
            }
          }
        }
switchD_0054ba67_caseD_1f:
        unitID = unitID + 1;
        iVar17 = iVar17 + 1;
        if (DAT_GameState.playerDataArray[iVar6].enemies <= iVar17) {
          if (_validTargetID == 0) {
            return FALSE;
          }
          if ((local_10 != 0) && (local_2c < (local_30 * 3) / 2)) {
            _validTargetID = local_10;
            local_8 = local_c;
          }
          if (_entityType == 4) {
            DAT_UnitsState.units[(int)psVar3].shootTargetedUnit = -2;
            DAT_UnitsState.units[(int)psVar3].shootTargetMicroX =
                 DAT_UnitsState.units[_validTargetID].microXPosition;
            DAT_UnitsState.units[(int)psVar3].shootTargetMicroY =
                 DAT_UnitsState.units[_validTargetID].microYPosition;
            DAT_UnitsState.units[(int)psVar3].shootTargetZ =
                 DAT_UnitsState.units[_validTargetID].terrainOrClimbHeight;
            return TRUE;
          }
          sVar13 = (short)_validTargetID;
          if ((_entityType == 0x25) || (_entityType == 0x14)) {
            DAT_UnitsState.units[(int)psVar3].shootTargetedUnit = sVar13;
            DAT_UnitsState.units[(int)psVar3].targetUID = DAT_UnitsState.units[_validTargetID].uid;
            DAT_UnitsState.units[(int)psVar3].distanceToEnemyUnitLadders = (short)local_8;
            DAT_UnitsState.units[(int)psVar3].shootTargetMicroX =
                 DAT_UnitsState.units[_validTargetID].microXPosition;
            DAT_UnitsState.units[(int)psVar3].shootTargetMicroY =
                 DAT_UnitsState.units[_validTargetID].microYPosition;
            DAT_UnitsState.units[(int)psVar3].shootTargetZ =
                 DAT_UnitsState.units[_validTargetID].terrainOrClimbHeight;
            return TRUE;
          }
          psVar1 = &DAT_UnitsState.units[_validTargetID].field282_0x3dc;
          *psVar1 = *psVar1 + 1;
          DAT_UnitsState.units[(int)psVar3].shootTargetedUnit = sVar13;
          DAT_UnitsState.units[(int)psVar3].field283_0x3de = sVar13;
          DAT_UnitsState.units[(int)psVar3].targetUID = DAT_UnitsState.units[_validTargetID].uid;
          DAT_UnitsState.units[(int)psVar3].distanceToEnemyUnitLadders = (short)local_8;
          if (100 < local_8) {
            DAT_UnitsState.units[(int)psVar3].jugglerCount = 0;
            DAT_UnitsState.units[_validTargetID].field250_0x39a = 1;
            return TRUE;
          }
          iVar6 = (int)DAT_UnitsState.units[_validTargetID].terrainOrClimbHeight +
                  (int)DAT_UnitsState.units[_validTargetID].buildingHeight;
          iVar7 = (int)DAT_UnitsState.units[(int)psVar3].buildingHeight +
                  (int)DAT_UnitsState.units[(int)psVar3].terrainOrClimbHeight;
          if (iVar6 + 0x46 < iVar7) {
            DAT_UnitsState.units[(int)psVar3].jugglerCount = 1;
            DAT_UnitsState.units[_validTargetID].field250_0x39a = 1;
            return TRUE;
          }
          DAT_UnitsState.units[(int)psVar3].jugglerCount = (iVar6 + -0x46 <= iVar7) - 1;
          DAT_UnitsState.units[_validTargetID].field250_0x39a = 1;
          return TRUE;
        }
      } while( true );
    }
    sVar13 = DAT_UnitsState.units[(int)unitID].attackAtTileY;
    sVar16 = DAT_UnitsState.units[(int)unitID].attackAtTileX;
    DAT_UnitsState.units[(int)unitID].jugglerCount = -1;
    BVar11 = Rendering::ViewportRenderState::xyAreValid
                       (&DAT_ViewportRenderState,(int)sVar16,(int)sVar13);
    if (BVar11 != FALSE) {
      sVar16 = DAT_UnitsState.units[(int)unitID].attackAtTileX;
      DAT_UnitsState.units[(int)unitID].shootTargetMicroX = sVar16 * 8;
      DAT_UnitsState.units[(int)unitID].shootTargetedUnit = -1;
      DAT_UnitsState.units[(int)unitID].shootTargetMicroY = sVar13 * 8;
      DAT_UnitsState.units[(int)unitID].shootTargetZ =
           (ushort)*(byte *)(DAT_ViewportRenderState.translationMatrix[sVar13].addXgetTile +
                             0x1d32c38 + (int)sVar16);
      return TRUE;
    }
  }
  *pUVar18 = UIT_NO_INSTRUCTION_OR_MOVEUnk;
  return FALSE;
}



// ================= recomputeTroopValuesForPlayer @ 00532ba0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::UnitsState::recomputeTroopValuesForPlayer(UnitsState *this,int playerID)

{
  int *piVar1;
  UnitTypeShort UVar2;
  short sVar3;
  short sVar4;
  int destinationYPosition;
  int destinationXPosition;
  int iVar5;
  short *psVar6;
  int iVar7;
  UnitTypeShort *pUVar8;
  bool bVar9;
  int _unitID;
  
  destinationYPosition = DAT_GameState.playerDataArray[playerID].campground.yEntry;
  bVar9 = DAT_GameSynchronyState.currentGameMode == GM_SOLITARY;
  DAT_GameState.playerDataArray[playerID].enemies = 0;
  DAT_GameState.playerDataArray[playerID].totalEnemyUnitsCount = 0;
  DAT_GameState.playerDataArray[playerID].sumOfTotalEnemyUnitsCount = 0;
  destinationXPosition = DAT_GameState.playerDataArray[playerID].campground.xEntry;
  DAT_GameState.playerDataArray[playerID].totalEnemyTroopValueByPlayerID[1] = 0;
  DAT_GameState.playerDataArray[playerID].totalEnemyTroopValueByPlayerID[2] = 0;
  DAT_GameState.playerDataArray[playerID].totalEnemyTroopValueByPlayerID[3] = 0;
  DAT_GameState.playerDataArray[playerID].totalEnemyTroopValueByPlayerID[4] = 0;
  DAT_GameState.playerDataArray[playerID].totalEnemyTroopValueByPlayerID[5] = 0;
  DAT_GameState.playerDataArray[playerID].totalEnemyTroopValueByPlayerID[6] = 0;
  DAT_GameState.playerDataArray[playerID].totalEnemyTroopValueByPlayerID[7] = 0;
  DAT_GameState.playerDataArray[playerID].totalEnemyTroopValueByPlayerID[8] = 0;
  DAT_GameState.playerDataArray[playerID].totalEnemyTroopValue = 0;
  DAT_GameState.playerDataArray[playerID].totalTeamTroopValue = 0;
  DAT_GameState.playerDataArray[playerID].totalEnemyRangedTroopValue = 0;
  if ((((bVar9) || (playerID == 0)) ||
      (DAT_GameSynchronyState.currentPlayerFullIDArray[playerID] != -1)) ||
     (DAT_GameSynchronyState.currentAIArray[playerID] != 0)) {
    IO::LowLevelMemory::fillMemory_ByteValue
              (&DAT_LowLevelMemory,5000,'\0',DAT_GameState.playerDataArray[playerID].enemyIDArray);
    _unitID = 1;
    if (1 < (int)DAT_UnitsState.maxUnitCount) {
      psVar6 = &DAT_UnitsState.units[1].dying;
      pUVar8 = &DAT_UnitsState.units[1].unitType;
      do {
                    /* dying[-0x10a] == logicalState */
        if (((psVar6[-0x10a] == ULS_NORMAL) && (*psVar6 == 0)) && (psVar6[0x5c] == 0)) {
                    /* dying[-0x105] == unit playerID */
          if (DAT_GameState.mapAndTime.playerTeams[psVar6[-0x105]] ==
              DAT_GameState.mapAndTime.playerTeams[playerID]) {
            if (psVar6[2] == 0)
            goto 
            _HoldStrong_Map_Units_UnitsState_recomputeTroopValuesForPlayer_CODE_continueToNextUnit;
            Navigation::DirectionAlgorithmState::setAxisBasedDistanceResult
                      (&DAT_DirectionAlgorithmState,destinationXPosition,destinationYPosition,
                       (int)(short)pUVar8[0x1b],(int)(short)pUVar8[0x1c]);
            if (DAT_DirectionAlgorithmState.distanceHigh < 0x3c) {
              iVar7 = TroopValueState::getValueOfTroopType(&DAT_TroopValueState,(int)(short)*pUVar8)
              ;
              piVar1 = &DAT_GameState.playerDataArray[playerID].totalTeamTroopValue;
              *piVar1 = *piVar1 + iVar7;
            }
          }
          else {
                    /* unit not in our team
                       dying[-0x109] == unitType */
            UVar2 = psVar6[-0x109];
            switch(UVar2) {
            case UT_TRADER:
            case UT_TRADERHORSE:
            case UT_CAMELSHBEAR:
            case UT_GHOST:
            case UT_MOTHER:
            case UT_CHILD:
              break;
            default:
              if (psVar6[-0x105] != 0) {
                switch(UVar2) {
                case UT_S_CATAPULT:
                case UT_S_TREBUCHET:
                case UT_S_MANGONEL:
                case UT_S_TOWER:
                case UT_S_SHIELD:
                case UT_S_BALLISTA:
                case UT_S_FBALLISTA:
                    /* count of currently manning engineers */
                  if (psVar6[0x8a] == 0) goto switchD_00532d4a_caseD_2a;
                }
                    /* dying[2] == isSelectable */
                if (psVar6[2] == 0) {
                  if (UVar2 == UT_LORD) {
                    piVar1 = &DAT_GameState.playerDataArray[playerID].totalEnemyUnitsCount;
                    *piVar1 = *piVar1 + 1;
                  }
                }
                else {
                  sVar3 = pUVar8[0x1c];
                  sVar4 = pUVar8[0x1b];
                  piVar1 = &DAT_GameState.playerDataArray[playerID].totalEnemyUnitsCount;
                  *piVar1 = *piVar1 + 1;
                  Navigation::DirectionAlgorithmState::setAxisBasedDistanceResult
                            (&DAT_DirectionAlgorithmState,destinationXPosition,destinationYPosition,
                             (int)sVar4,(int)sVar3);
                    /* unitType[4] == playerID */
                    /* dying[0xc9] == siegeTargetPlayerID */
                  if ((DAT_DirectionAlgorithmState.distanceHigh < 0x3c) &&
                     (((DAT_GameSynchronyState.currentPlayerFullIDArray[(short)pUVar8[4]] != -1 ||
                       (DAT_GameSynchronyState.currentAIArray[(short)pUVar8[4]] == 0)) ||
                      (psVar6[0xc9] == playerID)))) {
                    piVar1 = DAT_GameState.playerDataArray[playerID].totalEnemyTroopValueByPlayerID
                             + (short)pUVar8[4];
                    iVar7 = TroopValueState::getValueOfTroopType
                                      (&DAT_TroopValueState,(int)(short)*pUVar8);
                    *piVar1 = *piVar1 + iVar7;
                    iVar7 = TroopValueState::getValueOfTroopType
                                      (&DAT_TroopValueState,(int)(short)*pUVar8);
                    piVar1 = &DAT_GameState.playerDataArray[playerID].totalEnemyTroopValue;
                    *piVar1 = *piVar1 + iVar7;
                    UVar2 = *pUVar8;
                    if (((((UVar2 != UT_E_ARCHER) && (UVar2 != UT_E_XBOW)) && (UVar2 != UT_A_ARCHER)
                         ) && ((UVar2 != UT_A_SLINGER && (UVar2 != UT_A_HARCHER)))) &&
                       (UVar2 != UT_A_FIRETHROWER)) {
                      iVar7 = TroopValueState::getValueOfTroopType
                                        (&DAT_TroopValueState,(int)(short)UVar2);
                      piVar1 = &DAT_GameState.playerDataArray[playerID].totalEnemyRangedTroopValue;
                      *piVar1 = *piVar1 + iVar7;
                    }
                  }
                }
              }
              iVar7 = DAT_GameState.playerDataArray[playerID].enemies;
              if (iVar7 < 0x9c3) {
                DAT_GameState.playerDataArray[playerID].enemies = iVar7 + 1;
              }
              else {
                iVar7 = (int)SEC_RNG.currentNumber2 % 0x9c4;
                Random::RNG::nextRandomNumber2(&SEC_RNG);
                if (0x9c2 < iVar7) break;
              }
              iVar5 = *(int *)(pUVar8 + 5);
              DAT_GameState.playerDataArray[playerID].enemyIDArray[iVar7] = (short)_unitID;
              DAT_GameState.mapAndTime.playerEnemenyUnitUIDShortList[playerID][iVar7] = iVar5;
            }
          }
switchD_00532d4a_caseD_2a:
        }
_HoldStrong_Map_Units_UnitsState_recomputeTroopValuesForPlayer_CODE_continueToNextUnit:
        _unitID = _unitID + 1;
        psVar6 = psVar6 + 0x248;
        pUVar8 = pUVar8 + 0x248;
      } while (_unitID < (int)DAT_UnitsState.maxUnitCount);
    }
    piVar1 = &DAT_GameState.playerDataArray[playerID].sumOfTotalEnemyUnitsCount;
    *piVar1 = *piVar1 + DAT_GameState.playerDataArray[playerID].totalEnemyUnitsCount;
  }
  return;
}



// ================= processMeleeInitiation @ 00549c70 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::UnitsState::processMeleeInitiation(UnitsState *this,int unitID)

{
  ushort uVar1;
  int *piVar2;
  UnitsState *pUVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined2 extraout_DX;
  int iVar8;
  uint uVar9;
  uint *puVar10;
  bool bVar11;
  uint local_9c [4];
  uint local_8c;
  uint local_88;
  uint local_84;
  uint local_80;
  int _playerID;
  int local_78 [24];
  int *local_18;
  int local_14;
  int _totalHeight;
  UnitsState *local_c;
  int local_8;
  
  local_18 = DAT_UnitsState.unitCountOfSelection + unitID * 0x124 + -9;
  local_c = &DAT_UnitsState;
  if ((((DAT_UnitsState.units[unitID].someUnitStat2_meleeDamageUnk != 0) &&
       (DAT_UnitsState.units[unitID].unknownTestAgainst0_2 == 0)) &&
      (DAT_UnitsState.units[unitID].unknownMovementRelated_0x2d2 == 0)) &&
     (((DAT_UnitsState.units[unitID].logicalState == ULS_NORMAL &&
       (DAT_UnitsState.units[unitID].dying == 0)) &&
      (DAT_UnitsState.units[unitID].moveRelatedFlag != 1)))) {
    if (DAT_UnitsState.units[unitID].stateBasedSpeed < 1) {
                    /* 50 or 150 depending on selectable */
      iVar8 = (-(uint)(DAT_UnitsState.units[unitID].isSelectable_OR_matchTime != 0) & 100) + 0x32;
    }
    else {
      iVar8 = 0x10e;
    }
    if (((DAT_UnitsState.units[unitID].closestEnemyMicroDistance <= iVar8) ||
        (DAT_UnitsState.units[unitID].attackedUnitID != 0)) ||
       ((DAT_UnitsState.units[unitID].unitType == UT_LIONSHWOLF ||
        ((DAT_UnitsState.units[unitID].unknownTestAgainst0_1 != 0 &&
         (((DAT_GameSynchronyState.currentGameMode != GM_SOLITARY ||
           (100 < (int)DAT_UnitsState.DAT_UnitCount)) &&
          (((DAT_UnitsState.units[unitID].fixedRng ^ DAT_GameState.mapAndTime.totalGameTicksUnk) &
           0xf) == 0)))))))) {
      _totalHeight = (int)DAT_UnitsState.units[unitID].buildingHeight +
                     (int)DAT_UnitsState.units[unitID].terrainOrClimbHeight;
      _playerID = (int)DAT_UnitsState.units[unitID].owner;
      DAT_TileMapState.DAT_SomeTile = DAT_UnitsState.units[unitID].tile;
      DAT_TileMapState.DAT_SomeY =
           (int)DAT_ViewportRenderState.tileTranslationMatrix_YComponent
                [DAT_TileMapState.DAT_SomeTile];
      local_14 = 0;
      uVar4 = Game::GameStateStructures::teamToBitFlagsUnk(&DAT_GameState,unitID);
      pUVar3 = local_c;
      piVar2 = local_18;
      DAT_TileMapState.field213_0x554a48 = 0;
      if ((*(uint *)(DAT_TileMapState.ptr_OccupancyLayer + DAT_TileMapState.DAT_SomeTile + 1) &
          uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = 0x20;
      }
      if ((*(uint *)(DAT_TileMapState.ptr_OccupancyLayer + DAT_TileMapState.DAT_SomeTile + -1) &
          uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 2;
      }
      if ((*(uint *)(DAT_TileMapState.ptr_OccupancyLayer + DAT_TileMapState.DAT_SomeTile + 2) &
          uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x80000;
      }
      if ((*(uint *)(DAT_TileMapState.ptr_OccupancyLayer + DAT_TileMapState.DAT_SomeTile + -2) &
          uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x800;
      }
      puVar10 = (uint *)(DAT_TileMapState.ptr_OccupancyLayer +
                        *(int *)(DAT_TileMapState.ptr_MovementDirectionTranslationMatrix +
                                DAT_TileMapState.DAT_SomeY * 0x20) + DAT_TileMapState.DAT_SomeTile);
      if ((*(uint *)((int)puVar10 + -1) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 1;
      }
      if ((*(uint *)((int)puVar10 + 1) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x40;
      }
      if ((*puVar10 & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x80;
      }
      if ((*(uint *)((int)puVar10 + -2) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x400;
      }
      if ((*(uint *)((int)puVar10 + 2) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x100000;
      }
      puVar10 = (uint *)(DAT_TileMapState.ptr_OccupancyLayer +
                        *(int *)((int)(DAT_TileMapState.ptr_MovementDirectionTranslationMatrix +
                                      DAT_TileMapState.DAT_SomeY * 0x20) + 0x10) +
                        DAT_TileMapState.DAT_SomeTile);
      if ((*(uint *)((int)puVar10 + -1) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 4;
      }
      if ((*(uint *)((int)puVar10 + 1) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x10;
      }
      if ((*puVar10 & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 8;
      }
      if ((*(uint *)((int)puVar10 + -2) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x1000;
      }
      if ((*(uint *)((int)puVar10 + 2) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x40000;
      }
      puVar10 = (uint *)(DAT_TileMapState.ptr_OccupancyLayer +
                        *(int *)(DAT_TileMapState.ptr_MovementDirectionTranslationMatrix +
                                DAT_TileMapState.DAT_SomeY * 0x20 + -0x20) +
                        *(int *)(DAT_TileMapState.ptr_MovementDirectionTranslationMatrix +
                                DAT_TileMapState.DAT_SomeY * 0x20) + DAT_TileMapState.DAT_SomeTile);
      if ((*(uint *)((int)puVar10 + -1) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x100;
      }
      if ((*(uint *)((int)puVar10 + 1) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x400000;
      }
      if ((*puVar10 & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x800000;
      }
      if ((*(uint *)((int)puVar10 + -2) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x200;
      }
      if ((*(uint *)((int)puVar10 + 2) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x200000;
      }
      puVar10 = (uint *)(DAT_TileMapState.ptr_OccupancyLayer +
                        *(int *)(DAT_TileMapState.ptr_MovementDirectionTranslationMatrix +
                                DAT_TileMapState.DAT_SomeY * 0x20 + 0x30) +
                        *(int *)(DAT_TileMapState.ptr_MovementDirectionTranslationMatrix +
                                DAT_TileMapState.DAT_SomeY * 0x20 + 0x10) +
                        DAT_TileMapState.DAT_SomeTile);
      if ((*(uint *)((int)puVar10 + -1) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x4000;
      }
      if ((*(uint *)((int)puVar10 + 1) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x10000;
      }
      if ((*puVar10 & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x8000;
      }
      if ((*(uint *)((int)puVar10 + -2) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x2000;
      }
      if ((*(uint *)((int)puVar10 + 2) & uVar4) != 0) {
        DAT_TileMapState.field213_0x554a48 = DAT_TileMapState.field213_0x554a48 | 0x20000;
      }
      uVar1 = DAT_TileMapState.UnitLayer[DAT_TileMapState.DAT_SomeTile];
      while (local_8 = (int)(short)uVar1, 0 < local_8) {
        if (local_8 != unitID) {
          if (*(short *)((int)local_18 + 0x6aa) == 0) {
            bVar11 = *(short *)((int)local_18 + 0x6a2) == local_c->units[local_8].unitType;
          }
          else {
            bVar11 = DAT_GameState.mapAndTime.playerTeams[_playerID] ==
                     DAT_GameState.mapAndTime.playerTeams[local_c->units[local_8].owner];
          }
          if (!bVar11) {
            local_14 = 1;
            break;
          }
        }
        uVar1 = local_c->units[local_8].nextUnitOnTheSameTile;
      }
      if ((DAT_TileMapState.field213_0x554a48 != 0) || (local_14 != 0)) {
        local_78[0] = 0;
        local_78[1] = 0;
        local_78[2] = 0;
        local_78[3] = 0;
        local_78[4] = 0;
        local_78[5] = 0;
        local_78[6] = 0;
        local_78[7] = 0;
        local_78[8] = 0;
        local_78[9] = 0;
        local_78[10] = 0;
        local_78[0xb] = 0;
        local_78[0xc] = 0;
        local_78[0xd] = 0;
        local_78[0xe] = 0;
        local_78[0xf] = 0;
        local_78[0x10] = 0;
        local_78[0x11] = 0;
        local_78[0x12] = 0;
        local_78[0x13] = 0;
        local_78[0x14] = 0;
        local_78[0x15] = 0;
        local_78[0x16] = 0;
        local_78[0x17] = 0;
        if ((DAT_TileMapState.field213_0x554a48 & 1) != 0) {
          local_78[0] = DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][7] +
                        local_18[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 2) != 0) {
          local_78[1] = DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][6] +
                        local_18[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 4) != 0) {
          local_78[2] = DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][5] +
                        local_18[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 8) != 0) {
          local_78[3] = DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][4] +
                        local_18[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x10) != 0) {
          local_78[4] = DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][3] +
                        local_18[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x20) != 0) {
          local_78[5] = DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][2] +
                        local_18[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x40) != 0) {
          local_78[6] = DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][1] +
                        local_18[0x1ba];
        }
        if ((char)DAT_TileMapState.field213_0x554a48 < '\0') {
          local_78[7] = DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][0] +
                        local_18[0x1ba];
        }
        local_9c[0] = TileMapState::getTotalHeightAtTile
                                (&DAT_TileMapState,
                                 DAT_TileMapState.directionTranslationMatrix
                                 [DAT_TileMapState.DAT_SomeY][7] + local_18[0x1ba]);
        local_9c[1] = TileMapState::getTotalHeightAtTile
                                (&DAT_TileMapState,
                                 DAT_TileMapState.directionTranslationMatrix
                                 [DAT_TileMapState.DAT_SomeY][6] + piVar2[0x1ba]);
        local_9c[2] = TileMapState::getTotalHeightAtTile
                                (&DAT_TileMapState,
                                 DAT_TileMapState.directionTranslationMatrix
                                 [DAT_TileMapState.DAT_SomeY][5] + piVar2[0x1ba]);
        local_9c[3] = TileMapState::getTotalHeightAtTile
                                (&DAT_TileMapState,
                                 DAT_TileMapState.directionTranslationMatrix
                                 [DAT_TileMapState.DAT_SomeY][4] + piVar2[0x1ba]);
        local_8c = TileMapState::getTotalHeightAtTile
                             (&DAT_TileMapState,
                              DAT_TileMapState.directionTranslationMatrix
                              [DAT_TileMapState.DAT_SomeY][3] + piVar2[0x1ba]);
        local_88 = TileMapState::getTotalHeightAtTile
                             (&DAT_TileMapState,
                              DAT_TileMapState.directionTranslationMatrix
                              [DAT_TileMapState.DAT_SomeY][2] + piVar2[0x1ba]);
        local_84 = TileMapState::getTotalHeightAtTile
                             (&DAT_TileMapState,
                              DAT_TileMapState.directionTranslationMatrix
                              [DAT_TileMapState.DAT_SomeY][1] + piVar2[0x1ba]);
        local_80 = TileMapState::getTotalHeightAtTile
                             (&DAT_TileMapState,
                              DAT_TileMapState.directionTranslationMatrix
                              [DAT_TileMapState.DAT_SomeY][0] + piVar2[0x1ba]);
        if ((DAT_TileMapState.field213_0x554a48 & 0x100) != 0) {
          local_78[8] = DAT_MinimapViewState.spawnMoment[DAT_TileMapState.DAT_SomeY * 8 + 0x14] +
                        piVar2[0x1ba] +
                        DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][0];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x200) != 0) {
          local_78[9] = DAT_MinimapViewState.spawnMoment[DAT_TileMapState.DAT_SomeY * 8 + 0x13] +
                        DAT_MinimapViewState.spawnMoment[DAT_TileMapState.DAT_SomeY * 8 + 0x14] +
                        piVar2[0x1ba] +
                        DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][0];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x400) != 0) {
          local_78[10] = DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][6]
                         + DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY]
                           [7] + piVar2[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x800) != 0) {
          local_78[0xb] =
               piVar2[0x1ba] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][6] * 2;
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x1000) != 0) {
          local_78[0xc] =
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][5] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][6] +
               piVar2[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x2000) != 0) {
          local_78[0xd] =
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY + 1][6] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY + 1][5] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][4] +
               piVar2[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x4000) != 0) {
          local_78[0xe] =
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY + 1][5] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][4] +
               piVar2[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x8000) != 0) {
          local_78[0xf] =
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY + 1][4] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][4] +
               piVar2[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x10000) != 0) {
          local_78[0x10] =
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY + 1][3] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][4] +
               piVar2[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x20000) != 0) {
          local_78[0x11] =
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY + 1][2] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY + 1][3] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][4] +
               piVar2[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x40000) != 0) {
          local_78[0x12] =
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][2] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][3] +
               piVar2[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x80000) != 0) {
          local_78[0x13] =
               piVar2[0x1ba] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][2] * 2;
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x100000) != 0) {
          local_78[0x14] =
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][1] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][2] +
               piVar2[0x1ba];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x200000) != 0) {
          local_78[0x15] =
               DAT_MinimapViewState.spawnMoment[DAT_TileMapState.DAT_SomeY * 8 + 0xe] +
               DAT_MinimapViewState.spawnMoment[DAT_TileMapState.DAT_SomeY * 8 + 0xf] +
               piVar2[0x1ba] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][0];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x400000) != 0) {
          local_78[0x16] =
               DAT_MinimapViewState.spawnMoment[DAT_TileMapState.DAT_SomeY * 8 + 0xe] +
               piVar2[0x1ba] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][0];
        }
        if ((DAT_TileMapState.field213_0x554a48 & 0x800000) != 0) {
          local_78[0x17] =
               DAT_MinimapViewState.spawnMoment[DAT_TileMapState.DAT_SomeY * 8 + 0xd] +
               piVar2[0x1ba] +
               DAT_TileMapState.directionTranslationMatrix[DAT_TileMapState.DAT_SomeY][0];
        }
                    /* _otherUnitPtr.attackUnitID != 0 */
        if (*(short *)((int)piVar2 + 0x952) != 0) {
          local_8 = (int)*(short *)((int)piVar2 + 0x952);
          if (((pUVar3->units[local_8].uid == piVar2[0x255]) &&
              (pUVar3->units[local_8].logicalState == ULS_NORMAL)) &&
             (pUVar3->units[local_8].dying == 0)) {
            iVar8 = -1;
            do {
              if (iVar8 == -1) {
                if (local_14 != 0) {
                  iVar6 = piVar2[0x1ba];
                  goto LAB_0054a4af;
                }
              }
              else {
                iVar6 = local_78[DAT_UnitPropertiesDefinedData.field117_0x11cf4
                                 [*(short *)(piVar2 + 0x232)][iVar8]];
LAB_0054a4af:
                if (((iVar6 != 0) &&
                    (uVar4 = TileMapState::getTotalHeightAtTile(&DAT_TileMapState,iVar6),
                    uVar9 = (int)(_totalHeight - uVar4) >> 0x1f,
                    (int)((_totalHeight - uVar4 ^ uVar9) - uVar9) < 0x20)) &&
                   (iVar5 = getEnemyUnitIDNearby(local_c,unitID,iVar6,_totalHeight), iVar6 = unitID,
                   iVar7 = local_8, local_8 == iVar5)) goto LAB_0054a6ba;
              }
              iVar8 = iVar8 + 1;
            } while (iVar8 < 0x18);
          }
          *(short *)((int)piVar2 + 0x952) = 0;
          piVar2[0x255] = 0;
          *(undefined2 *)((int)piVar2 + 0x9e6) = 0;
        }
        iVar8 = -1;
        do {
          if (iVar8 == -1) {
            if (local_14 != 0) {
              iVar7 = (int)*(short *)(piVar2 + 0x232);
              iVar6 = piVar2[0x1ba];
              goto LAB_0054a548;
            }
          }
          else {
            iVar7 = DAT_UnitPropertiesDefinedData.field117_0x11cf4[*(short *)(piVar2 + 0x232)]
                    [iVar8];
            iVar6 = local_78[iVar7];
LAB_0054a548:
            if ((iVar6 != 0) &&
               ((iVar7 < 8 ||
                ((uVar4 = (int)(_totalHeight -
                               local_9c[DAT_UnitPropertiesDefinedData.field118_0x12054[iVar7].x]) >>
                          0x1f,
                 (int)((_totalHeight -
                        local_9c[DAT_UnitPropertiesDefinedData.field118_0x12054[iVar7].x] ^ uVar4) -
                      uVar4) < 0x21 &&
                 ((iVar7 = DAT_UnitPropertiesDefinedData.field118_0x12054[iVar7].y, iVar7 == -1 ||
                  (uVar4 = (int)(_totalHeight - local_9c[iVar7]) >> 0x1f,
                  (int)((_totalHeight - local_9c[iVar7] ^ uVar4) - uVar4) < 0x21)))))))) {
              local_8 = getEnemyUnitIDNearby(local_c,unitID,iVar6,_totalHeight);
              if ((0 < local_8) &&
                 (((local_c->units[local_8].logicalState == ULS_NORMAL &&
                   (local_c->units[local_8].dying == 0)) &&
                  ((uVar4 = (_totalHeight - local_c->units[local_8].buildingHeight) -
                            (int)local_c->units[local_8].terrainOrClimbHeight,
                   uVar9 = (int)uVar4 >> 0x1f, (int)((uVar4 ^ uVar9) - uVar9) < 0x21 &&
                   ((((*(short *)((int)piVar2 + 0x6a2) != 0x2d &&
                      (*(short *)((int)piVar2 + 0x6a2) != 0x43)) ||
                     (local_c->units[local_8].unknownTestAgainst0_1 == 0)) || (iVar8 < 8)))))))) {
                    /* _otherUnit.attackUnitID = _unitID */
                *(short *)((int)piVar2 + 0x952) = (short)local_8;
                piVar2[0x255] = local_c->units[local_8].uid;
                setFacingDirectionTowardUnitMicro(&DAT_UnitsState,unitID,local_8);
                break;
              }
            }
          }
          iVar8 = iVar8 + 1;
                    /* -- CHECK 24 TILES AROUND UNIT -- */
        } while (iVar8 < 0x18);
                    /* _otherUnitPtr.attackUnitID != 0 */
        if (*(short *)((int)piVar2 + 0x952) != 0) {
          if (((local_c->units[local_8].someUnitStat2_meleeDamageUnk != 0) &&
              (local_c->units[local_8].attackedUnitID == 0)) &&
             (local_c->units[local_8].unknownMovementRelated_0x2d2 == 0)) {
            local_c->units[local_8].attackedUnitID = (short)unitID;
            local_c->units[local_8].field207_0x340 = piVar2[0x1ab];
            iVar6 = local_8;
            iVar7 = unitID;
LAB_0054a6ba:
            setFacingDirectionTowardUnitMicro(&DAT_UnitsState,iVar6,iVar7);
          }
          if ((short)piVar2[0x235] != 0x6a) {
            if (*(short *)(piVar2 + 0x1c3) == 8) {
              saveUnitStateBeforeInterruption(unitID);
              *(undefined2 *)(piVar2 + 0x1c3) = extraout_DX;
              *(undefined2 *)(piVar2 + 0x235) = 0x6a;
              *(undefined2 *)(piVar2 + 0x284) = 0;
              piVar2[0x231] = 0;
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].substate = 0;
            }
            else {
              *(undefined2 *)((int)piVar2 + 0x9e6) = 1;
            }
          }
                    /* param 3 points to another unit iD */
          processUnitAttackOtherUnit
                    (local_c,DAT_CurrentUnitSlotID,(int)*(short *)((int)piVar2 + 0x952));
          return;
        }
      }
      *(undefined2 *)((int)piVar2 + 0x9e6) = 0;
      *(short *)((int)piVar2 + 0x952) = 0;
      piVar2[0x255] = 0;
      return;
    }
  }
  DAT_UnitsState.units[unitID].field207_0x340 = 0;
  DAT_UnitsState.units[unitID].attackedUnitID = 0;
  DAT_UnitsState.units[unitID].field276_0x3d2 = 0;
  return;
}



// ================= findDistanceOrThreatLevelToUnitUnk @ 004a0b20 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::Navigation::PathFindingState::findDistanceOrThreatLevelToUnitUnk
          (PathFindingState *this,int param_1,int param_2,int param_3,int param_4)

{
  short sVar1;
  uint uVar2;
  int (*paiVar3) [8];
  int iVar4;
  int iVar5;
  short *psVar6;
  int local_c;
  int local_8;
  
  DAT_PathFindingState.calculations = DAT_PathFindingState.calculations + 1;
  DAT_PathFindingState.searchGeneration = DAT_PathFindingState.searchGeneration + 1;
  local_c = 0;
  local_8 = 0;
  if (32000 < DAT_PathFindingState.searchGeneration) {
    DAT_PathFindingState.searchGeneration = 1;
    IO::LowLevelMemory::fillMemory_ByteValue
              (&DAT_LowLevelMemory,0x27420,'\0',DAT_TileMapState.WalkLayer);
  }
  DAT_PathFindingState.searchQueue.yQueue[0] = (short)param_3;
  DAT_PathFindingState.searchQueue.readIndex = 0;
  DAT_PathFindingState.searchQueue.writeIndex = 1;
  DAT_PathFindingState.searchQueue.currentDistance = 1;
  DAT_PathFindingState.searchQueue.tilesQueue[0] =
       DAT_ViewportRenderState.translationMatrix[param_3].addXgetTile + param_2;
  DAT_TileMapState.CertainPathLayer[DAT_PathFindingState.searchQueue.tilesQueue[0]] = 1;
  DAT_TileMapState.WalkLayer[DAT_PathFindingState.searchQueue.tilesQueue[0]] =
       (short)DAT_PathFindingState.searchGeneration;
  if (DAT_PathFindingState.searchQueue.readIndex == DAT_PathFindingState.searchQueue.writeIndex) {
    return 0;
  }
  do {
    uVar2 = DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.readIndex];
    if (0x13a0f < uVar2) {
      return local_c;
    }
    sVar1 = DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.readIndex];
    DAT_PathFindingState.searchQueue.currentDistance = (int)DAT_TileMapState.CertainPathLayer[uVar2]
    ;
    if (0x13a10 < DAT_PathFindingState.searchQueue.currentDistance) {
      return local_c;
    }
    if (param_4 < DAT_PathFindingState.searchQueue.currentDistance) {
      return local_c;
    }
    paiVar3 = DAT_TileMapState.directionTranslationMatrix + sVar1;
    psVar6 = &DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[0].short.yOffset;
    do {
      iVar4 = (*paiVar3)[0] + uVar2;
      if (((DAT_TileMapState.LogicLayer[iVar4] & 0x4a5014b1U) == 0) &&
         (DAT_TileMapState.WalkLayer[iVar4] != DAT_PathFindingState.searchGeneration)) {
        iVar5 = (int)(short)DAT_TileMapState.UnitLayer[iVar4];
        DAT_TileMapState.CertainPathLayer[iVar4] =
             (short)DAT_PathFindingState.searchQueue.currentDistance + 1;
        DAT_TileMapState.WalkLayer[iVar4] = (short)DAT_PathFindingState.searchGeneration;
        DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.writeIndex] =
             *psVar6 + sVar1;
        DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.writeIndex] =
             iVar4;
        DAT_PathFindingState.searchQueue.writeIndex =
             DAT_PathFindingState.searchQueue.writeIndex + 1;
        if (0x13a0f < DAT_PathFindingState.searchQueue.writeIndex) {
          DAT_PathFindingState.searchQueue.writeIndex = 0;
        }
        if ((((iVar5 != 0) &&
             (DAT_GameState.mapAndTime.playerTeams[param_1] !=
              DAT_GameState.mapAndTime.playerTeams[DAT_UnitsState.units[iVar5].owner])) &&
            (DAT_UnitsState.units[iVar5].logicalState != ULS_INVISIBLE)) &&
           ((DAT_UnitsState.units[iVar5].dying == 0 &&
            (DAT_UnitsState.units[iVar5].isSelectable_OR_matchTime != 0)))) {
          switch(DAT_UnitsState.units[iVar5].unitType) {
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_A_ARCHER:
          case UT_A_HARCHER:
          case UT_S_FBALLISTA:
            param_3 = 0xc;
            break;
          case UT_E_SPEAR:
          case UT_E_LADDER:
          case UT_S_TOWER:
          case UT_S_BATTERINGRAM:
          case UT_S_SHIELD:
          case UT_A_SLAVE:
            param_3 = 4;
            break;
          case UT_E_PIKE:
          case UT_E_SWORD:
          case UT_E_KNIGHT:
          case UT_A_ASSASSIN:
          case UT_A_SWORDSMAN:
            param_3 = 0;
            break;
          case UT_E_MACE:
          case UT_E_MONK:
            param_3 = 2;
            break;
          case UT_E_ENGINEER:
          case UT_S_CATAPULT:
          case UT_A_FIRETHROWER:
            param_3 = 0x14;
            break;
          case UT_S_TREBUCHET:
            param_3 = 0x1e;
            break;
          case UT_S_MANGONEL:
          case UT_S_BALLISTA:
            param_3 = 0x28;
            break;
          case UT_LORD:
          case UT_A_SLINGER:
            param_3 = 8;
          }
          param_3 = param_3 + 1 + DAT_PathFindingState.searchQueue.currentDistance;
          if (local_8 < param_3) {
            local_c = iVar5;
            local_8 = param_3;
          }
        }
      }
      paiVar3 = (int (*) [8])(*paiVar3 + 1);
      psVar6 = psVar6 + 4;
    } while ((int)psVar6 < 0xb4908c);
    DAT_PathFindingState.searchQueue.readIndex = DAT_PathFindingState.searchQueue.readIndex + 1;
    if (0x13a0f < DAT_PathFindingState.searchQueue.readIndex) {
      DAT_PathFindingState.searchQueue.readIndex = 0;
    }
  } while (DAT_PathFindingState.searchQueue.readIndex != DAT_PathFindingState.searchQueue.writeIndex
          );
  return local_c;
}



