// ================= findNearestEnemyAndHeadTowardsIt @ 0054a7b0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

dword __thiscall
_HoldStrong::Map::Units::UnitsState::findNearestEnemyAndHeadTowardsIt(UnitsState *this,int unitID)

{
  short *psVar1;
  short sVar2;
  ushort uVar3;
  short sVar4;
  UnitStanceEnumShort UVar5;
  UnitInstructionTypeShort UVar6;
  short sVar7;
  short sVar8;
  UnitTypeShort UVar9;
  UnitStateShort UVar10;
  bool bVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  uint uVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  dword dVar22;
  dword _triangleDistanceUnk;
  int _foundEnemyID;
  int _stanceBasedRange;
  int local_44;
  int _enemyIndex;
  short *_ptrEnemyIDArray;
  dword _minDistance;
  int local_24;
  int local_20;
  int _minimumValue;
  dword local_14;
  
  iVar17 = (int)DAT_UnitsState.units[unitID].microXPosition;
  sVar2 = DAT_UnitsState.units[unitID].owner;
  iVar18 = (int)DAT_UnitsState.units[unitID].microYPosition;
  uVar3 = DAT_TileMapState.PathConnectionLayer[DAT_UnitsState.units[unitID].tile];
  DAT_UnitsState.unitDistanceComputationResultUnk = 100000;
  _minDistance = 100000;
  local_14 = 0;
  _minimumValue = 100000;
  _foundEnemyID = 0;
  local_44 = 1;
  bVar11 = false;
  _stanceBasedRange = 0;
  sVar4 = 0;
  if (((DAT_UnitsState.units[unitID].SA != 0) ||
      ((DAT_UnitsState.units[unitID].movementType_OR_targetUnitID != 0 &&
       (DAT_UnitsState.units[unitID].state.generic == US_MOVE_TO_DESTINATION)))) &&
     (iVar12 = (int)DAT_UnitsState.units[unitID].tribeID, iVar12 != 0)) {
    sVar4 = DAT_TribesState.tribes[iVar12].isRallyingUnk;
    UVar5 = DAT_TribesState.tribes[iVar12].unitStance;
    if (UVar5 == USE_DEFENSIVE) {
      _stanceBasedRange = 0x28;
    }
    else if (UVar5 == USE_AGGRESSIVE) {
      _stanceBasedRange = 200;
    }
  }
  UVar6 = DAT_UnitsState.units[unitID].targetingType;
  if (UVar6 == UIT_UNIT_ATTACK_UNIT) {
    bVar11 = true;
    switch(DAT_UnitsState.units[unitID].unitType) {
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
      iVar12 = (int)DAT_UnitsState.units[unitID].tribeID;
      bVar11 = false;
      if (iVar12 != 0) {
        iVar13 = (int)DAT_TribesState.tribes[iVar12].someUnitID;
        if ((iVar13 != 0) &&
           (DAT_UnitsState.units[iVar13].uid == DAT_TribesState.tribes[iVar12].someUnitUID))
        goto LAB_0054a9d5;
      }
      DAT_UnitsState.units[unitID].targetingType = UIT_NO_INSTRUCTION_OR_MOVEUnk;
    }
  }
  else if (UVar6 == UIT_ATTACK_LAND) {
    switch(DAT_UnitsState.units[unitID].unitType) {
    case UT_E_SPEAR:
    case UT_E_PIKE:
    case UT_E_MACE:
    case UT_E_SWORD:
    case UT_E_KNIGHT:
    case UT_E_MONK:
    case UT_A_SLAVE:
    case UT_A_ASSASSIN:
    case UT_A_SWORDSMAN:
      if ((-1 < DAT_UnitsState.units[unitID].lookForEnemy) &&
         (DAT_UnitsState.units[unitID].state.generic != US_MELEE_ATTACK)) {
        sVar8 = DAT_UnitsState.units[unitID].attackAtTileX;
        if ((sVar8 == DAT_UnitsState.units[unitID].x) &&
           (DAT_UnitsState.units[unitID].attackAtTileY == DAT_UnitsState.units[unitID].y)) {
          DAT_UnitsState.units[unitID].targetingType = 0;
          break;
        }
        sVar7 = DAT_UnitsState.units[unitID].attackAtTileY;
        DAT_UnitsState.units[unitID].plannedDestinationY = sVar7;
        DAT_UnitsState.units[unitID].plannedDestinationX = sVar8;
        setDestinationForUnit(&DAT_UnitsState,unitID,(int)sVar8,(int)sVar7,0);
        iVar12 = -((int)DAT_UnitsState.units[unitID].totalSizeOfPathPlan / 2);
        DAT_UnitsState.units[unitID].state.generic = US_MOVE_TO_DESTINATION;
        if (-0x33 < iVar12) {
          iVar12 = -0x32;
        }
        DAT_UnitsState.units[unitID].lookForEnemy = (short)iVar12;
      }
LAB_0054a9d5:
      bVar11 = true;
    }
  }
  if (DAT_UnitsState.units[unitID].isSelectable_OR_matchTime == 0) {
    bVar11 = true;
  }
  iVar12 = DAT_GameState.playerDataArray[sVar2].enemies;
  if (iVar12 < 5) {
    local_44 = 5;
  }
  else if (iVar12 < 0xf) {
    local_44 = 2;
  }
  _enemyIndex = 0;
  if (0 < iVar12) {
    _ptrEnemyIDArray = DAT_GameState.playerDataArray[sVar2].enemyIDArray;
    do {
      iVar12 = (int)*_ptrEnemyIDArray;
      iVar13 = (int)DAT_UnitsState.units[iVar12].microXPosition;
      if (iVar13 < iVar17) {
        iVar13 = iVar17 - iVar13;
      }
      else {
        iVar13 = iVar13 - iVar17;
      }
      iVar14 = (int)DAT_UnitsState.units[iVar12].microYPosition;
      if (iVar14 < iVar18) {
        iVar14 = iVar18 - iVar14;
      }
      else {
        iVar14 = iVar14 - iVar18;
      }
      if (iVar13 < iVar14) {
                    /* pythagorean approximation */
        _triangleDistanceUnk = (((iVar13 * 2) / 5) * iVar13) / iVar14 + iVar14;
      }
      else if (iVar13 == 0) {
                    /* fixme: bug: I think this needs to be set not to 0 but to _dY */
        _triangleDistanceUnk = 0;
      }
      else {
        _triangleDistanceUnk = (((iVar14 * 2) / 5) * iVar14) / iVar13 + iVar13;
      }
      if ((int)_triangleDistanceUnk < (int)_minDistance) {
        _minDistance = _triangleDistanceUnk;
      }
      if (((DAT_UnitsState.units[unitID].unitType == UT_A_ASSASSIN) &&
          (DAT_UnitsState.units[iVar12].isSelectable_OR_matchTime != 0)) &&
         ((int)_triangleDistanceUnk < (int)DAT_UnitsState.unitDistanceComputationResultUnk)) {
        DAT_UnitsState.unitDistanceComputationResultUnk = _triangleDistanceUnk;
      }
      if (((!bVar11) && (_stanceBasedRange != 0)) &&
         (-1 < DAT_UnitsState.units[unitID].lookForEnemy)) {
        sVar8 = DAT_UnitsState.units[unitID]._someX_2;
        if (((sVar8 != 0) && (sVar4 == 0)) && (_stanceBasedRange == 0x28)) {
          iVar19 = (int)DAT_UnitsState.units[unitID]._someY_2;
          iVar21 = (int)DAT_UnitsState.units[iVar12].microXPosition;
          iVar13 = sVar8 * 8;
          iVar14 = iVar19 * 8;
          if (iVar13 < iVar21) {
            dVar22 = iVar21 + sVar8 * -8;
          }
          else {
            dVar22 = iVar13 - iVar21;
          }
          iVar13 = (int)DAT_UnitsState.units[iVar12].microYPosition;
          if (iVar14 < iVar13) {
            _triangleDistanceUnk = iVar13 + iVar19 * -8;
          }
          else {
            _triangleDistanceUnk = iVar14 - iVar13;
          }
          if ((int)_triangleDistanceUnk <= (int)dVar22) {
            _triangleDistanceUnk = dVar22;
          }
        }
        dVar22 = _triangleDistanceUnk;
        if ((((int)_triangleDistanceUnk <= _stanceBasedRange) &&
            (DAT_UnitsState.units[iVar12].uid ==
             DAT_GameState.mapAndTime.playerEnemenyUnitUIDShortList[sVar2][_enemyIndex])) &&
           (((_triangleDistanceUnk =
                   _triangleDistanceUnk +
                   DAT_UnitPropertiesDefinedData.DAT_UnitVisionBonus
                   [(int)(DAT_UnitsState.units[unitID].fixedRng + iVar12) % 10] / local_44,
             DAT_UnitsState.units[iVar12].state.generic != US_MELEE_ATTACK ||
             (sVar8 = DAT_UnitsState.units[iVar12].attackedBy,
             _triangleDistanceUnk = (sVar8 * 0x32 + _triangleDistanceUnk) * 2, sVar8 < 3)) &&
            ((((DAT_UnitsState.units[iVar12].huntedBy < 2 ||
               (sVar8 = DAT_UnitsState.units[iVar12].huntedBy,
               _triangleDistanceUnk = _triangleDistanceUnk + sVar8 * 0x32, sVar8 < 3)) ||
              (DAT_UnitsState.units[unitID].movementType_OR_targetUnitID == iVar12)) &&
             (((DAT_UnitsState.units[iVar12].unknownTestAgainst0_1 == 0 ||
               (UVar9 = DAT_UnitsState.units[iVar12].unitType, UVar9 == UT_LIONSHWOLF)) ||
              (UVar9 == UT_CAGEDOG)))))))) {
                    /* unit type switch */
          switch(DAT_UnitsState.units[iVar12].unitType) {
          case UT_PEASANT:
            _triangleDistanceUnk = _triangleDistanceUnk * 8 + 200;
            break;
          default:
            _triangleDistanceUnk = _triangleDistanceUnk * 4 + 200;
            break;
          case UT_E_ARCHER:
          case UT_E_XBOW:
          case UT_A_ARCHER:
          case UT_A_HARCHER:
          case UT_A_FIRETHROWER:
            break;
          case UT_E_SPEAR:
          case UT_E_PIKE:
          case UT_E_MACE:
          case UT_E_SWORD:
          case UT_E_KNIGHT:
          case UT_E_LADDER:
          case UT_E_MONK:
          case UT_A_SLAVE:
          case UT_A_SLINGER:
          case UT_A_ASSASSIN:
          case UT_A_SWORDSMAN:
            _triangleDistanceUnk = _triangleDistanceUnk * 2 + 100;
            break;
          case UT_E_ENGINEER:
          case UT_S_CATAPULT:
          case UT_S_TREBUCHET:
          case UT_S_MANGONEL:
          case UT_S_TOWER:
          case UT_S_BATTERINGRAM:
          case UT_S_SHIELD:
          case UT_S_BALLISTA:
          case UT_S_FBALLISTA:
            _triangleDistanceUnk = _triangleDistanceUnk + 0x19;
            break;
          case UT_LORD:
            _triangleDistanceUnk =
                 (int)(_triangleDistanceUnk + ((int)_triangleDistanceUnk >> 0x1f & 3U)) >> 2;
          }
          if (DAT_UnitsState.units[unitID].movementType_OR_targetUnitID == iVar12) {
            _triangleDistanceUnk = (int)_triangleDistanceUnk / 2;
          }
          if ((int)_triangleDistanceUnk < _minimumValue) {
            iVar13 = DAT_UnitsState.units[iVar12].tile;
            sVar8 = DAT_UnitsState.units[iVar12].y;
            iVar14 = (int)DAT_UnitsState.units[iVar12].buildingHeight +
                     (int)DAT_UnitsState.units[iVar12].terrainOrClimbHeight;
            local_20 = -1;
            local_24 = 10000;
            iVar19 = 0;
            do {
              iVar21 = DAT_TileMapState.directionTranslationMatrix[sVar8]
                       [DAT_UnitPropertiesDefinedData.field84_0x11cb4[iVar19]] + iVar13;
              if (((DAT_TileMapState.UnitLayer[iVar21] == 0) &&
                  (uVar15 = TileMapState::getTotalHeightAtTile(&DAT_TileMapState,iVar21),
                  iVar14 < (int)(uVar15 + 0x10))) && ((int)(uVar15 - 0x10) < iVar14)) {
                iVar16 = (int)DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar21];
                iVar21 = iVar21 - DAT_ViewportRenderState.translationMatrix[iVar16].addXgetTile;
                iVar20 = iVar21 * 8;
                if (iVar20 < iVar17) {
                  iVar20 = iVar17 + iVar21 * -8;
                }
                else {
                  iVar20 = iVar20 - iVar17;
                }
                if (iVar16 * 8 < iVar18) {
                  iVar21 = iVar18 + iVar16 * -8;
                }
                else {
                  iVar21 = iVar16 * 8 - iVar18;
                }
                if (iVar21 <= iVar20) {
                  iVar21 = iVar20;
                }
                if (iVar21 < local_24) {
                  local_24 = iVar21;
                  local_20 = iVar19;
                }
              }
              iVar19 = iVar19 + 1;
            } while (iVar19 < 8);
            if (-1 < local_20) {
              _minimumValue = _triangleDistanceUnk;
              local_14 = dVar22;
              _foundEnemyID = iVar12;
            }
          }
        }
      }
      _ptrEnemyIDArray = _ptrEnemyIDArray + 1;
      _enemyIndex = _enemyIndex + 1;
    } while (_enemyIndex < DAT_GameState.playerDataArray[sVar2].enemies);
  }
  if (_stanceBasedRange == 0) {
LAB_0054af54:
    if ((DAT_UnitsState.units[unitID].lookForEnemy != 0) ||
       (UVar10 = DAT_UnitsState.units[unitID].state.generic,
       DAT_UnitsState.units[unitID].movementType_OR_targetUnitID = 0,
       UVar10 != US_MOVE_TO_DESTINATION)) goto LAB_0054afbf;
  }
  else {
    if (DAT_UnitsState.units[unitID].lookForEnemy < 0) goto LAB_0054afbf;
    if (bVar11) goto LAB_0054af54;
    if (_foundEnemyID != 0) {
      iVar17 = Navigation::PathFindingState::calculateCanPlayerUnitsNavigateToAreaFromArea
                         (&DAT_PathFindingState,(int)DAT_UnitsState.units[unitID].owner,
                          (int)(short)uVar3,
                          (int)(short)DAT_TileMapState.PathConnectionLayer
                                      [DAT_UnitsState.units[_foundEnemyID].tile],
                          (int)DAT_UnitsState.units[unitID].unitCanClimb);
      if (iVar17 != 0) {
        sVar2 = DAT_UnitsState.units[unitID]._someX_2;
        DAT_UnitsState.units[unitID].state.generic = US_MOVE_TO_DESTINATION;
        DAT_UnitsState.units[unitID].animationCycleNumber = 0;
        if (sVar2 == 0) {
          sVar2 = DAT_UnitsState.units[unitID].destinationY_2Unk;
          DAT_UnitsState.units[unitID]._someX_2 = DAT_UnitsState.units[unitID].destinationX_2Unk;
          DAT_UnitsState.units[unitID]._someY_2 = sVar2;
        }
        TileMapState::findNearestValidDigTileNearTarget
                  (&DAT_TileMapState,(int)DAT_UnitsState.units[unitID].x,
                   (int)DAT_UnitsState.units[unitID].y,(int)DAT_UnitsState.units[_foundEnemyID].x,
                   (int)DAT_UnitsState.units[_foundEnemyID].y);
        setDestinationForUnit
                  (&DAT_UnitsState,unitID,DAT_TileMapState.field155_0x5549a8,
                   DAT_TileMapState.field156_0x5549ac,0);
        iVar17 = -0x1e - local_14;
        DAT_UnitsState.units[unitID].moveDelay = 0;
        if (-0x33 < iVar17) {
          iVar17 = -0x32;
        }
        sVar2 = DAT_UnitsState.units[unitID].movementType_OR_targetUnitID;
        DAT_UnitsState.units[unitID].lookForEnemy = (short)iVar17;
        if (sVar2 != _foundEnemyID) {
          DAT_UnitsState.units[unitID].movementType_OR_targetUnitID = (short)_foundEnemyID;
          psVar1 = &DAT_UnitsState.units[_foundEnemyID].huntedBy;
          *psVar1 = *psVar1 + 1;
        }
        goto LAB_0054afbf;
      }
    }
    DAT_UnitsState.units[unitID].lookForEnemy = -8;
    DAT_UnitsState.units[unitID].movementType_OR_targetUnitID = 0;
  }
  sVar2 = DAT_UnitsState.units[unitID]._someX_2;
  if (sVar2 != 0) {
    setDestinationForUnit
              (&DAT_UnitsState,unitID,(int)sVar2,(int)DAT_UnitsState.units[unitID]._someY_2,0);
    DAT_UnitsState.units[unitID].moveDelay = 0;
    DAT_UnitsState.units[unitID]._someY_2 = 0;
    DAT_UnitsState.units[unitID]._someX_2 = 0;
    DAT_UnitsState.units[unitID].state.generic = US_MOVE_TO_DESTINATION;
  }
LAB_0054afbf:
  if (32000 < (int)_minDistance) {
    _minDistance = 32000;
  }
  return _minDistance;
}



// ================= findNearestEnemyUnitWithinDistance @ 004a06b0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* Structurally identical to findNearestEnemyBuildingWithinDistance but checks UnitLayer instead of
   BuildingLayer. BFS from (param_2, param_3) up to distance param_4, returns the unit ID of the
   first reachable live enemy unit (different team to param_1) that is not invisible, not flagged
   for removal, and not dying. Returns 0 if none found.
   
   renamed by: Claude Sonnet 4.6 */

int __thiscall
_HoldStrong::Map::Navigation::PathFindingState::findNearestEnemyUnitWithinDistance
          (PathFindingState *this,int param_1,int param_2,int param_3,int param_4)

{
  short sVar1;
  UnitLogicStateShort UVar2;
  int iVar3;
  int iVar4;
  short *psVar5;
  int (*paiVar6) [8];
  
  DAT_PathFindingState.searchGeneration = DAT_PathFindingState.searchGeneration + 1;
  DAT_PathFindingState.calculations = DAT_PathFindingState.calculations + 1;
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
  if (DAT_PathFindingState.searchQueue.readIndex != DAT_PathFindingState.searchQueue.writeIndex) {
    while ((iVar3 = DAT_PathFindingState.searchQueue.tilesQueue
                    [DAT_PathFindingState.searchQueue.readIndex], -1 < iVar3 && (iVar3 < 0x13a10)))
    {
      sVar1 = DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.readIndex];
      DAT_PathFindingState.searchQueue.currentDistance =
           (int)DAT_TileMapState.CertainPathLayer[iVar3];
      if (0x13a10 < DAT_PathFindingState.searchQueue.currentDistance) {
        return 0;
      }
      if (param_4 < DAT_PathFindingState.searchQueue.currentDistance) {
        return 0;
      }
      psVar5 = &DAT_TerrainDefinedData.clockwiseCardinalTranslationMatrix[0].short.yOffset;
      paiVar6 = DAT_TileMapState.directionTranslationMatrix + sVar1;
      do {
        iVar4 = (*paiVar6)[0] + iVar3;
        if (((DAT_TileMapState.LogicLayer[iVar4] & 0x30) == 0) &&
           (DAT_TileMapState.WalkLayer[iVar4] != DAT_PathFindingState.searchGeneration)) {
          DAT_TileMapState.CertainPathLayer[iVar4] =
               (short)DAT_PathFindingState.searchQueue.currentDistance + 1;
          DAT_TileMapState.WalkLayer[iVar4] = (short)DAT_PathFindingState.searchGeneration;
          DAT_PathFindingState.searchQueue.yQueue[DAT_PathFindingState.searchQueue.writeIndex] =
               *psVar5 + sVar1;
          DAT_PathFindingState.searchQueue.tilesQueue[DAT_PathFindingState.searchQueue.writeIndex] =
               iVar4;
          DAT_PathFindingState.searchQueue.writeIndex =
               DAT_PathFindingState.searchQueue.writeIndex + 1;
          if (0x13a0f < DAT_PathFindingState.searchQueue.writeIndex) {
            DAT_PathFindingState.searchQueue.writeIndex = 0;
          }
          iVar4 = (int)(short)DAT_TileMapState.UnitLayer[iVar4];
          if ((((iVar4 != 0) &&
               (DAT_GameState.mapAndTime.playerTeams[param_1] !=
                DAT_GameState.mapAndTime.playerTeams[DAT_UnitsState.units[iVar4].owner])) &&
              (UVar2 = DAT_UnitsState.units[iVar4].logicalState, UVar2 != ULS_INVISIBLE)) &&
             ((UVar2 != ULS_REMOVE && (DAT_UnitsState.units[iVar4].dying == 0)))) {
            return iVar4;
          }
        }
        psVar5 = psVar5 + 4;
        paiVar6 = (int (*) [8])(*paiVar6 + 1);
      } while ((int)psVar5 < 0xb4908c);
      DAT_PathFindingState.searchQueue.readIndex = DAT_PathFindingState.searchQueue.readIndex + 1;
      if (0x13a0f < DAT_PathFindingState.searchQueue.readIndex) {
        DAT_PathFindingState.searchQueue.readIndex = 0;
      }
      if (DAT_PathFindingState.searchQueue.readIndex == DAT_PathFindingState.searchQueue.writeIndex)
      {
        return 0;
      }
    }
  }
  return 0;
}



// ================= UpdateAssassin @ 005744d0 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Global::UpdateAssassin(void)

{
  int *piVar1;
  short *psVar2;
  byte *pbVar3;
  char *pcVar4;
  byte bVar5;
  short sVar6;
  UnitTypeShort UVar7;
  UnitInstructionTypeShort UVar8;
  BOOLEnum BVar9;
  uint uVar10;
  int extraout_EAX;
  DWORD DVar11;
  uint uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  uint uVar16;
  bool bVar17;
  eSFX sfxOffsetInArray;
  
  uVar10 = DAT_CurrentUnitSlotID;
  iVar15 = (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner;
  piVar1 = &DAT_GameState.playerDataArray[iVar15].armySize;
  *piVar1 = *piVar1 + 1;
  piVar1 = &DAT_GameState.playerDataArray[iVar15].countAssassins;
  *piVar1 = *piVar1 + 1;
  DAT_UnitsState.units[uVar10].gmIDUnk = 0xc6;
  DAT_UnitsState.units[uVar10].imageIDUnk = 0;
  DAT_UnitsState.units[uVar10].isSelectable_OR_matchTime = 1;
  Map::Units::TribesState::addUnitToNewTribe(&DAT_TribesState,uVar10);
  uVar10 = DAT_CurrentUnitSlotID;
  if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic != US_MELEE_ATTACK) {
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageID2 = 0;
    DAT_UnitsState.units[uVar10].drawYOffset = 0;
  }
  uVar12 = DAT_CurrentUnitSlotID;
  switch(DAT_UnitsState.units[uVar10].state.generic) {
  case US_DETERMINE_NEXT_STATEUnk:
    DAT_UnitsState.units[uVar10].substate = -1;
    DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].field320_0x413 = 0;
    psVar2 = &DAT_UnitsState.units[uVar10].idleCounterUnk;
    *psVar2 = *psVar2 + 1;
    uVar12 = DAT_CurrentUnitSlotID;
    if (DAT_UnitsState.units[uVar10].isDisappearingUnk != 0) {
      pbVar3 = &DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown;
      *pbVar3 = *pbVar3 - 1;
      if (-1 < (char)*pbVar3) {
        return;
      }
      DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown = 0;
      DAT_UnitsState.units[uVar10].isDisappearingUnk = 0;
      return;
    }
    if (DAT_UnitsState.units[uVar10].goToRallyPoint == 0) {
      DAT_UnitsState.units[uVar10].state.generic = US_IDLEUnk;
      return;
    }
    DAT_UnitsState.units[uVar10].goToRallyPoint = 0;
    DAT_UnitsState.units[uVar10].state.generic = 0x69;
    iVar13 = Map::Buildings::BuildingsState::getKeepLocationForAIUnit
                       (&DAT_BuildingsState,iVar15,0xd,uVar12);
    goto joined_r0x005746a3;
  case US_IDLEUnk:
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].animationSpeed = 5;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].field134_0x2ac = 10;
    DAT_UnitsState.units[uVar10].SA = 1;
    psVar2 = &DAT_UnitsState.units[uVar10].idleCounterUnk;
    *psVar2 = *psVar2 + 1;
    uVar12 = uVar12 & 3;
    iVar15 = DAT_UnitsState.units[uVar10].animationCycleNumber;
    if (uVar12 == 0) {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          DAT_AssassinAnimationFrames0[iVar15];
    }
    else if (uVar12 == 1) {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          DAT_AssassinAnimationFrames1[iVar15];
    }
    else if (uVar12 == 2) {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          DAT_AssassinAnimationFrames2[iVar15];
    }
    else {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          DAT_AssassinAnimationFrames4[iVar15];
    }
    DAT_UnitsState.units[uVar10].animationFrame = iVar15;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = 0x311;
      DAT_UnitHasBecomeIdle = 1;
    }
    else {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar15 + 0x310;
    }
    uVar12 = DAT_CurrentUnitSlotID;
    UVar8 = DAT_UnitsState.units[uVar10].targetingType;
    if ((UVar8 == UIT_DIG_MOAT) || (UVar8 == UIT_FILL_MOAT)) {
      DAT_UnitHasBecomeIdle = 1;
    }
    else if (DAT_UnitHasBecomeIdle == 0) {
      return;
    }
    DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
    DAT_UnitsState.units[uVar10].state.generic = US_DETERMINE_NEXT_STATEUnk;
    Map::Units::UnitsState::moveToFreeTileNearby(&DAT_UnitsState,uVar12);
    return;
  case US_MOVE_TO_DESTINATION:
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0x10;
    DAT_UnitsState.units[uVar10].animationSheetFrameOffset = 1;
    DAT_UnitsState.units[uVar10].field320_0x413 = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    if (DAT_TribesState.tribes[DAT_UnitsState.units[uVar10].tribeID].isRallyingUnk != 0) {
      DAT_UnitsState.units[uVar10].SA = 1;
    }
    sVar6 = DAT_UnitsState.units[uVar10].moveInstructionSpeedDelayTracker;
    if (sVar6 == 0) {
      if (DAT_UnitsState.units[uVar10].closestEnemyMicroDistance < 0xc1) {
        DAT_UnitsState.units[uVar10].animationSheetFrameOffset = 0x81;
        goto LAB_0057475b;
      }
    }
    else if (sVar6 < 0x47) {
LAB_0057475b:
      DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    }
    else {
      DAT_UnitsState.units[uVar10].stateBasedSpeed = -1;
      DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    }
    uVar12 = DAT_CurrentUnitSlotID;
    BVar9 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,DAT_CurrentUnitSlotID)
    ;
    if (BVar9 != FALSE) {
      DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
      DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
      DAT_UnitsState.units[uVar10].state.generic = US_DETERMINE_NEXT_STATEUnk;
      if (DAT_TribesState.tribes[DAT_UnitsState.units[uVar10].tribeID].tribeBehaviorType ==
          STBT_0x400) {
        DAT_UnitsState.units[uVar10].state.generic = US_DISAPPEAR;
      }
      iVar15 = Map::Units::UnitsState::handleUnitMovementWhenTargetingBuildings
                         (&DAT_UnitsState,uVar12);
      if (0 < iVar15) {
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].unknownDigMoatOrWallAttackFlag1015 != 0x3f7)
        {
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_MELEE_ATTACK_WALL;
          return;
        }
        iVar15 = Map::TileMapState::returnOwnedMoatAtTile
                           (&DAT_TileMapState,
                            DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetedBuildingTile);
        uVar10 = DAT_CurrentUnitSlotID;
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].digTileTarget = iVar15;
        if (iVar15 == 0) {
          DAT_UnitsState.units[uVar10].state.generic = US_DETERMINE_NEXT_STATEUnk;
          return;
        }
        DAT_UnitsState.units[uVar10].state.generic = US_DIG;
        sVar6 = DAT_ViewportRenderState.tileTranslationMatrix_YComponent
                [DAT_UnitsState.units[uVar10].targetedBuildingTile];
        DAT_UnitsState.units[uVar10].digTileY__OR__countLifeCycleEngineersSentToManSiegeEngine =
             sVar6;
        DAT_UnitsState.units[uVar10].
        digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300 =
             (short)DAT_UnitsState.units[uVar10].targetedBuildingTile -
             (short)DAT_ViewportRenderState.translationMatrix[sVar6].addXgetTile;
        return;
      }
    }
    break;
  case 0x68:
    DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    DAT_UnitsState.units[uVar10].animationSheetFrameOffset = 0x181;
    return;
  case 0x69:
                    /* Rally state */
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].SA = 1;
    DAT_UnitsState.units[uVar10].stateBasedSpeed = 1;
    DAT_UnitsState.units[uVar10].animationSheetFrameOffset = 1;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0x10;
    DAT_UnitsState.units[uVar10].calculatedMovementSpeed =
         DAT_UnitsState.units[uVar10].movementSpeed;
    psVar2 = &DAT_UnitsState.units[uVar10].idleCounterUnk;
    *psVar2 = *psVar2 + 1;
    BVar9 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,DAT_CurrentUnitSlotID)
    ;
                    /* At rally point */
    if ((BVar9 == FALSE) ||
       (iVar13 = DAT_GameCore.mapTimeInTicks + DAT_CurrentUnitSlotID,
       DAT_UnitsState.units[uVar10].facingDirection = 4, iVar13 % 0x28 != 0)) goto LAB_005746ce;
    iVar13 = Map::Buildings::BuildingsState::getKeepLocationForAIUnit
                       (&DAT_BuildingsState,iVar15,0xd,DAT_CurrentUnitSlotID);
joined_r0x005746a3:
    if (iVar13 != 0) {
      DAT_PathFindingState.allAssassinsUnk = 1;
      Map::Units::UnitsState::setDestinationForUnit
                (&DAT_UnitsState,DAT_CurrentUnitSlotID,DAT_BuildingsState.DAT_TempXOffset,
                 DAT_BuildingsState.DAT_TempYOffset,0);
    }
LAB_005746ce:
    piVar1 = &DAT_GameState.playerDataArray[iVar15].countAssassinsAndArabianSwordsman;
    *piVar1 = *piVar1 + 1;
    return;
  case US_MELEE_ATTACK:
    iVar15 = DAT_UnitsState.units[uVar10].gfxNumber;
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].animationSpeed = 1;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    sVar6 = DAT_UnitsState.units[uVar10].attackedUnitID;
    if ((sVar6 != 0) &&
       (DAT_UnitsState.units[uVar10].animationCycleNumberHasJustIncremented != FALSE)) {
      if (DAT_UnitsState.units[uVar10].animationCycleNumber == 7) {
        Map::Units::UnitsState::playHurtSFXForUnit(&DAT_UnitsState,(int)sVar6);
      }
      if ((DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber == 5) &&
         (((((UVar7 = DAT_UnitsState.units[sVar6].unitType, UVar7 == UT_E_SPEAR ||
             (UVar7 == UT_E_PIKE)) || (UVar7 == UT_LORD)) ||
           ((UVar7 == UT_E_MACE || (UVar7 == UT_E_SWORD)))) ||
          ((UVar7 == UT_E_KNIGHT || ((UVar7 == UT_A_ASSASSIN || (UVar7 == UT_A_SWORDSMAN)))))))) {
        Audio::SFX::SFXState::playSFXAtLocation
                  (&DAT_SFXState,(int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].x,
                   (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].y,FX_STEEL1);
      }
      if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber == 4) {
        Audio::SFX::SFXState::playSFXAtLocation
                  (&DAT_SFXState,(int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].x,
                   (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].y,FX_ASS_SWISH);
      }
    }
    uVar10 = DAT_CurrentUnitSlotID;
    iVar13 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field151_0x2c94
                        [DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber];
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationFrame = iVar13;
    iVar14 = (int)DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected;
    if (iVar13 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar14 + 0x101;
      DAT_UnitHasBecomeIdle = 1;
    }
    else {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar14 + 0xf9 + iVar13 * 8;
    }
    if (DAT_UnitsState.units[uVar10].gfxNumber != iVar15) {
      DAT_UnitsState.units[uVar10].drawYOffset = (short)DAT_UnitsState.units[uVar10].imageID2;
      DAT_UnitsState.units[uVar10].imageID2 = iVar15;
    }
    if (DAT_UnitHasBecomeIdle != 0) {
      DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
      Map::Units::UnitsState::resumeMovementIfNoAttackTarget(&DAT_UnitsState,DAT_CurrentUnitSlotID);
      return;
    }
    break;
  case US_MELEE_ATTACK_WALL:
    DAT_UnitsState.units[uVar10].animationSpeed = 2;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    Map::Units::UnitsState::setUnitFacingDirectionForTargetXandY
              (&DAT_UnitsState,uVar12,(int)DAT_UnitsState.units[uVar10].attackAtTileX,
               (int)DAT_UnitsState.units[uVar10].attackAtTileY);
    uVar10 = DAT_CurrentUnitSlotID;
    iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field151_0x2c94
                        [DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber];
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationFrame = iVar15;
    iVar13 = (int)DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar13 + 0x101;
      DAT_UnitHasBecomeIdle = 1;
    }
    else {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar13 + 0xf9 + iVar15 * 8;
    }
    if ((DAT_UnitsState.units[uVar10].animationCycleNumberHasJustIncremented != FALSE) &&
       (DAT_UnitsState.units[uVar10].animationCycleNumber == 6)) {
      uVar10 = Map::TileMapState::getBuildingHurtSFXID
                         (&DAT_TileMapState,DAT_UnitsState.units[uVar10].targetedBuildingTile);
      if (uVar10 == 1) {
        sfxOffsetInArray = FX_ATTACK_WOOD;
      }
      else {
        if (uVar10 != 2) goto LAB_00574a2c;
        sfxOffsetInArray = FX_ATTACK_STONE;
      }
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].x,
                 (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].y,sfxOffsetInArray);
    }
LAB_00574a2c:
    uVar12 = DAT_CurrentUnitSlotID;
    uVar10 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetedBuildingTile;
    iVar15 = (int)(short)DAT_TileMapState.BuildingLayer[uVar10];
    if ((iVar15 == 0) && ((DAT_TileMapState.LogicLayer[uVar10] & 0x100U) == 0)) {
      DAT_UnitHasBecomeIdle = 1;
    }
    else if (DAT_UnitHasBecomeIdle == 0) {
      return;
    }
    pcVar4 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].nextAttackHurtsWall;
    *pcVar4 = *pcVar4 + '\x01';
    if ('\x01' < DAT_UnitsState.units[uVar12].nextAttackHurtsWall) {
      DAT_UnitsState.units[uVar12].nextAttackHurtsWall = '\0';
    }
    uVar10 = DAT_UnitsState.units[uVar12].targetedBuildingTile;
    uVar16 = DAT_TileMapState.LogicLayer[uVar10] & 0x100;
    if (uVar16 == 0) {
      iVar15 = (int)(short)DAT_TileMapState.BuildingLayer[uVar10];
      if (iVar15 < 1) {
        DAT_UnitsState.units[uVar12].state.generic = US_DETERMINE_NEXT_STATEUnk;
        return;
      }
                    /* 6 if gate or tower else 70 */
      iVar13 = (-(uint)(DAT_BuildingDefinedData.DAT_IsGateOrTowerArray
                        [(short)DAT_BuildingsState.buildings[iVar15].buildingType] != FALSE) &
               0xffffffc0) + 0x46;
    }
    else {
      iVar13 = 10;
    }
    Map::TileMapState::processDamageToBuildingThunk
              (&DAT_TileMapState,uVar10,(int)DAT_UnitsState.units[uVar12].attackAtTileX,
               (int)DAT_UnitsState.units[uVar12].attackAtTileY,iVar13,
               (int)DAT_UnitsState.units[uVar12].nextAttackHurtsWall,
               (int)DAT_UnitsState.units[uVar12].owner,TRUE);
    if (extraout_EAX == 0) {
      iVar13 = (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner;
      if (DAT_GameSynchronyState.currentPlayerFullIDArray[iVar13] == -1) {
        if (uVar16 == 0) {
          if (((DAT_BuildingDefinedData.DAT_IsGateOrTowerArray
                [(short)DAT_BuildingsState.buildings[iVar15].buildingType] != FALSE) &&
              (*(int *)((int)DAT_TroopValueState.attackInfo.scaleValuesArray +
                       iVar13 * 0x177bc + -0x1c) + 10 <
               (int)(uint)*(byte *)(*(int *)((int)DAT_TroopValueState.attackInfo.hackValuesArray +
                                            iVar13 * 0x177bc + -0x10) * 0x13a10 + 0x1ee2998 +
                                   DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetedBuildingTile)
              )) && (iVar15 = Map::Units::TribesState::moveUnitToBehaviorTarget
                                        (&DAT_TribesState,DAT_CurrentUnitSlotID,
                                         (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                                              unknownDigMoatOrWallAttackFlag1015),
                    uVar10 = DAT_CurrentUnitSlotID, iVar15 == 0)) {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_DETERMINE_NEXT_STATEUnk;
            DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
            return;
          }
        }
        else if (*(int *)((int)DAT_TroopValueState.attackInfo.scaleValuesArray +
                         iVar13 * 0x177bc + -0x1c) + 0xf <
                 (int)(uint)*(byte *)(*(int *)((int)DAT_TroopValueState.attackInfo.hackValuesArray +
                                              iVar13 * 0x177bc + -0x10) * 0x13a10 + 0x1ee2998 +
                                     DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                                     targetedBuildingTile)) {
          iVar15 = Map::Units::TribesState::moveUnitToBehaviorTarget
                             (&DAT_TribesState,DAT_CurrentUnitSlotID,
                              (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                                   unknownDigMoatOrWallAttackFlag1015);
          if (iVar15 != 0) {
            return;
          }
          iVar15 = Map::Units::UnitsState::setDestinationNearTargetedBuilding
                             (&DAT_UnitsState,DAT_CurrentUnitSlotID,1);
          if (iVar15 != 0) {
            return;
          }
          goto LAB_00574b58;
        }
      }
    }
    else {
      if ((uVar16 != 0) &&
         (iVar15 = Map::Units::UnitsState::setDestinationNearTargetedBuilding
                             (&DAT_UnitsState,DAT_CurrentUnitSlotID,1), iVar15 != 0)) {
        return;
      }
      uVar10 = DAT_CurrentUnitSlotID;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetedBuildingTile = 0;
      iVar15 = Map::Units::TribesState::moveUnitToBehaviorTarget
                         (&DAT_TribesState,uVar10,
                          (int)DAT_UnitsState.units[uVar10].unknownDigMoatOrWallAttackFlag1015);
      if (iVar15 == 0) {
LAB_00574b58:
        uVar10 = DAT_CurrentUnitSlotID;
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_DETERMINE_NEXT_STATEUnk;
        DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
        return;
      }
    }
    DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber = 0;
    return;
  case 0x6c:
    DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    DAT_UnitsState.units[uVar10].animationSheetFrameOffset = 1;
    return;
  case US_JESTER_ROAM_TO:
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    pbVar3 = &DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown;
    *pbVar3 = *pbVar3 + DAT_UnitsState.units[uVar10].engineerManningSiegeStateRef_checkType;
    if ((char)*pbVar3 < '\0') {
      DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown = 0;
    }
    else if ('\x1f' < (char)DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown) {
      DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown = 0x1f;
    }
    psVar2 = &DAT_UnitsState.units[uVar10].updateTickTracker;
    *psVar2 = *psVar2 + 1;
    if (0x20 < DAT_UnitsState.units[uVar10].updateTickTracker) {
      DAT_UnitsState.units[uVar10].updateTickTracker = 0;
      DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown = 0;
      DAT_UnitsState.units[uVar10].state = (UnitStateUnion)DAT_UnitsState.units[uVar10].cachedState;
      bVar5 = DAT_UnitsState.units[uVar10].engineerManningSiegeStateRef_checkType;
      if ((char)bVar5 < '\0') {
        if (DAT_UnitsState.units[uVar10].isDisappearingUnk != 0) {
          Map::Buildings::BuildingsState::prepareCampgroundCoords(&DAT_BuildingsState,iVar15);
          Map::Units::UnitsState::setDestinationForUnit
                    (&DAT_UnitsState,DAT_CurrentUnitSlotID,DAT_BuildingsState.DAT_TempXOffset,
                     DAT_BuildingsState.DAT_TempYOffset,0);
          return;
        }
      }
      else if (('\0' < (char)bVar5) && (DAT_UnitsState.units[uVar10].isDisappearingUnk != 0)) {
        DAT_UnitsState.units[uVar10].logicalState = ULS_TRANSITIONING;
        DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown = 0x20;
        return;
      }
    }
    break;
  case US_DISAPPEAR:
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    pbVar3 = &DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown;
    *pbVar3 = *pbVar3 + 1;
    if (' ' < (char)DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown) {
      DAT_UnitsState.units[uVar10].disappearFadeAlphaCountdown = 0x20;
      DAT_UnitsState.units[uVar10].logicalState = ULS_REMOVE;
      if (DAT_UnitsState.units[uVar10].killedFlagUnk == 0) {
        Game::GameStateStructures::processUnitLossStatistic
                  (&DAT_GameState,iVar15,DAT_CurrentUnitSlotID);
        if (iVar15 == DAT_GameSynchronyState.currentPlayerSlotID) {
          piVar1 = DAT_GameState.mapAndTime.emenyHitArray +
                   DAT_UnitsState.units[DAT_CurrentUnitSlotID].lastEncounteredEnemyPlayerID + -9;
          *piVar1 = *piVar1 + 1;
          return;
        }
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].lastEncounteredEnemyPlayerID ==
            DAT_GameSynchronyState.currentPlayerSlotID) {
          piVar1 = DAT_GameState.mapAndTime.emenyHitArray + iVar15;
          *piVar1 = *piVar1 + 1;
        }
      }
    }
    break;
  case US_DEATH_01:
    sVar6 = DAT_UnitsState.units[uVar10].field323_0x418;
    if (sVar6 < 8) {
      DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    }
    else {
      DAT_UnitsState.units[uVar10].field323_0x418 = sVar6 + -8;
    }
    DAT_UnitsState.units[uVar10].facingDirection = 0;
    DAT_UnitsState.units[uVar10].animationSpeed = 2;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].animationFrame =
         (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.field12_0x93c
                    [DAT_UnitsState.units[uVar10].animationCycleNumber];
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    iVar15 = DAT_UnitsState.units[uVar10].animationFrame;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = 0x33c;
      DAT_UnitsState.units[uVar10].state.generic = US_DISAPPEAR;
      DAT_UnitHasBecomeIdle = 1;
      return;
    }
    iVar15 = iVar15 + 0x324;
    goto LAB_005755cb;
  case US_DEATH_03:
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].facingDirection = 0;
    DAT_UnitsState.units[uVar10].animationSpeed = 1;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field12_0x93c[DAT_UnitsState.units[uVar10].animationCycleNumber];
    DAT_UnitsState.units[uVar10].animationFrame = iVar15;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = 0x36a;
      DAT_UnitsState.units[uVar10].state.generic = US_DISAPPEAR;
      DAT_UnitHasBecomeIdle = 1;
      return;
    }
    iVar15 = iVar15 + 0x352;
    goto LAB_005755cb;
  case US_STONE_DEATH_01:
  case US_STONE_DEATH_02:
  case US_STONE_DEATH_03:
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].facingDirection = 0;
    DAT_UnitsState.units[uVar10].animationSpeed = 1;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field11_0x8e4[DAT_UnitsState.units[uVar10].animationCycleNumber];
    DAT_UnitsState.units[uVar10].animationFrame = iVar15;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = 0x352;
      DAT_UnitsState.units[uVar10].state.generic = US_DISAPPEAR;
      DAT_UnitHasBecomeIdle = 1;
      return;
    }
    iVar15 = iVar15 + 0x33c;
LAB_005755cb:
    bVar17 = DAT_UnitHasBecomeIdle != 0;
    DAT_UnitsState.units[uVar10].gfxNumber = iVar15;
    if (bVar17) {
      DAT_UnitsState.units[uVar10].state.generic = US_DISAPPEAR;
      return;
    }
    break;
  case US_APPEAR:
    DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0x10;
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    sVar6 = DAT_UnitsState.units[uVar10].moveInstructionSpeedDelayTracker;
    DAT_UnitsState.units[uVar10].animationSheetFrameOffset = 1;
    if ((sVar6 == 0) || (DAT_UnitsState.units[uVar10].moveInstructionSpeedDelayTracker < 0x47)) {
      DAT_UnitsState.units[uVar10].stateBasedSpeed = 0;
    }
    else {
      DAT_UnitsState.units[uVar10].stateBasedSpeed = -1;
      DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    }
    uVar12 = DAT_CurrentUnitSlotID;
    BVar9 = Map::Units::UnitsState::hasUnitReachedDestination(&DAT_UnitsState,DAT_CurrentUnitSlotID)
    ;
    if (BVar9 != FALSE) {
      iVar15 = DAT_UnitsState.units[uVar10].
               targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID;
      Map::Units::UnitsState::setPositionOfUnit
                (&DAT_UnitsState,uVar12,
                 iVar15 - DAT_ViewportRenderState.translationMatrix
                          [DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar15]].
                          addXgetTile,
                 (int)DAT_ViewportRenderState.tileTranslationMatrix_YComponent[iVar15],
                 (uint)DAT_TileMapState.HeightLayer[iVar15]);
      Map::Units::UnitsState::setDestinationForUnit
                (&DAT_UnitsState,DAT_CurrentUnitSlotID,
                 (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].plannedDestinationX,
                 (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].plannedDestinationY,0);
      uVar10 = DAT_CurrentUnitSlotID;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_MOVE_TO_DESTINATION;
      DAT_UnitsState.units[uVar10].fadeType = 1;
      DAT_UnitsState.units[uVar10].fadeCounter = 0;
      return;
    }
    break;
  case US_ASSASSIN_THROWING_HOOK:
                    /* Throwing the hook */
    DAT_UnitsState.units[uVar10].field320_0x413 = 1;
    DAT_UnitsState.units[uVar10].animationSpeed = 1;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].field323_0x418 = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    sVar6 = DAT_UnitsState.units[uVar10].assassinHeightDifference;
    iVar15 = DAT_UnitsState.units[uVar10].animationCycleNumber;
    if (sVar6 < 0x46) {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          field156_0x2dac[iVar15];
    }
    else if (sVar6 < 0xa0) {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          field157_0x2df4[iVar15];
    }
    else {
      iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                          field158_0x2e4c[iVar15];
    }
    DAT_UnitsState.units[uVar10].animationFrame = iVar15;
    iVar13 = (int)DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar13 + 0x1c1;
      DAT_UnitHasBecomeIdle = 1;
    }
    else {
      DAT_UnitsState.units[uVar10].gfxNumber = iVar13 + 0x1b9 + iVar15 * 8;
    }
    if ((DAT_UnitsState.units[uVar10].animationCycleNumber == 1) &&
       (DAT_UnitsState.units[uVar10].animationCycleNumberHasJustIncremented != FALSE)) {
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_UnitsState.units[uVar10].x,
                 (int)DAT_UnitsState.units[uVar10].y,FX_GH_SWING);
    }
    if (DAT_UnitHasBecomeIdle != 0) {
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].x,
                 (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].y,FX_GH_CATCH);
      iVar15 = DAT_GameSynchronyState.currentPlayerSlotID;
      uVar10 = DAT_CurrentUnitSlotID;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber = 0;
      DAT_UnitsState.units[uVar10].state.generic = US_ASSASSIN_CLIMBING_UP;
      DAT_UnitsState.units[uVar10].field324_0x41a = 0x20;
      if (((DAT_UnitsState.units[uVar10].owner != iVar15) &&
          (iVar15 == (char)DAT_UnitsState.units[uVar10].ownerOfAssassinScaledObject)) &&
         (DVar11 = timeGetTime(), 30000 < DVar11 - DWORD_00ee1064)) {
        if ((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) ||
           (DAT_GameState.mapAndTime.playerTeams[DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner]
            != DAT_GameState.mapAndTime.playerTeams[DAT_GameSynchronyState.currentPlayerSlotID])) {
                    /* "Assassins are scaling the walls sire" */
          Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"General_Warning18.wav");
        }
        DWORD_00ee1064 = timeGetTime();
        return;
      }
    }
    break;
  case US_ASSASSIN_CLIMBING_UP:
                    /* Scaling the wall */
    DAT_UnitsState.units[uVar10].field320_0x413 = 1;
    DAT_UnitsState.units[uVar10].animationSpeed = 2;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    sVar6 = DAT_UnitsState.units[uVar10].field324_0x41a;
    if (0 < sVar6) {
      DAT_UnitsState.units[uVar10].field324_0x41a = sVar6 + -2;
    }
    sVar6 = DAT_UnitsState.units[uVar10].assassinHeightDifference;
    if (sVar6 < 0x46) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 7;
    }
    else if (sVar6 < 100) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 6;
    }
    else if (sVar6 < 0x82) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 5;
    }
    else if (sVar6 < 0xa0) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 4;
    }
    else if (sVar6 < 0xbe) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 3;
    }
    else {
      DAT_UnitsState.units[uVar10].imageIDUnk = (sVar6 < 0xd2) + 1;
    }
    iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field160_0x2ed8[DAT_UnitsState.units[uVar10].animationCycleNumber];
    DAT_UnitsState.units[uVar10].animationFrame = iVar15;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber =
           DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected + 0x271;
      DAT_UnitHasBecomeIdle = 1;
LAB_00574fe5:
      DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
    }
    else {
      bVar17 = DAT_UnitHasBecomeIdle != 0;
      DAT_UnitsState.units[uVar10].gfxNumber =
           DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected + 0x269 + iVar15 * 8;
      if (bVar17) goto LAB_00574fe5;
    }
    if ((DAT_UnitsState.units[uVar10].animationCycleNumberHasJustIncremented != FALSE) &&
       ((iVar15 = DAT_UnitsState.units[uVar10].animationCycleNumber, iVar15 < 10 || (0x10 < iVar15))
       )) {
      psVar2 = &DAT_UnitsState.units[uVar10].field323_0x418;
      *psVar2 = *psVar2 + 1;
    }
    uVar12 = DAT_CurrentUnitSlotID;
    if (DAT_UnitsState.units[uVar10].assassinHeightDifference + -0x23 <=
        (int)DAT_UnitsState.units[uVar10].field323_0x418) {
      DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
      Map::Units::UnitsState::commitMimmicLocation(&DAT_UnitsState,uVar12);
      uVar10 = DAT_CurrentUnitSlotID;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_MOVE_TO_DESTINATION;
      DAT_UnitsState.units[uVar10].field323_0x418 = 0;
      DAT_UnitsState.units[uVar10].field324_0x41a = 0x20;
      DAT_UnitsState.units[uVar10].field320_0x413 = 0;
      return;
    }
    break;
  case US_ASSASSIN_START_CLIMBING_DOWN:
    DAT_UnitsState.units[uVar10].field320_0x413 = 1;
    DAT_UnitsState.units[uVar10].animationSpeed = 1;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    iVar15 = (int)(char)DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp.
                        field159_0x2eb0[DAT_UnitsState.units[uVar10].animationCycleNumber];
    DAT_UnitsState.units[uVar10].animationFrame = iVar15;
    if (iVar15 < 1) {
      DAT_UnitsState.units[uVar10].gfxNumber =
           DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected + 0x1c1;
      DAT_UnitHasBecomeIdle = 1;
    }
    else {
      bVar17 = DAT_UnitHasBecomeIdle == 0;
      DAT_UnitsState.units[uVar10].gfxNumber =
           DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected + 0x1b9 + iVar15 * 8;
      if (bVar17) {
        return;
      }
    }
    DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
    DAT_UnitsState.units[uVar10].state.generic = US_ASSASSIN_CLIMBING_DOWN;
    DAT_UnitsState.units[uVar10].field324_0x41a = 0x20;
    Audio::SFX::SFXState::playSFXAtLocation
              (&DAT_SFXState,(int)DAT_UnitsState.units[uVar10].x,(int)DAT_UnitsState.units[uVar10].y
               ,FX_ROPE_SLIDE);
    return;
  case US_ASSASSIN_CLIMBING_DOWN:
    DAT_UnitsState.units[uVar10].field320_0x413 = 1;
    DAT_UnitsState.units[uVar10].animationSpeed = 2;
    DAT_UnitsState.units[uVar10].field_0x30_animRelated = 0;
    DAT_UnitsState.units[uVar10].idleCounterUnk = 0;
    uVar12 = DAT_CurrentUnitSlotID;
    if (DAT_UnitsState.units[uVar10].field323_0x418 == 0) {
      DAT_UnitsState.units[uVar10].field323_0x418 =
           DAT_UnitsState.units[uVar10].assassinHeightDifference;
      Map::Units::UnitsState::commitMimmicLocation(&DAT_UnitsState,uVar12);
    }
    uVar10 = DAT_CurrentUnitSlotID;
    sVar6 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].field324_0x41a;
    if (0 < sVar6) {
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].field324_0x41a = sVar6 + -2;
    }
    sVar6 = DAT_UnitsState.units[uVar10].assassinHeightDifference;
    if (sVar6 < 0x46) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 7;
    }
    else if (sVar6 < 100) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 6;
    }
    else if (sVar6 < 0x82) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 5;
    }
    else if (sVar6 < 0xa0) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 4;
    }
    else if (sVar6 < 0xbe) {
      DAT_UnitsState.units[uVar10].imageIDUnk = 3;
    }
    else {
      DAT_UnitsState.units[uVar10].imageIDUnk = (sVar6 < 0xd2) + 1;
    }
    uVar12 = (int)DAT_UnitsState.units[uVar10].facingDirectionMapOrientationCorrected + 4U &
             0x80000007;
    if ((int)uVar12 < 0) {
      uVar12 = (uVar12 - 1 | 0xfffffff8) + 1;
    }
    DAT_UnitsState.units[uVar10].gfxNumber = uVar12 + 0x291;
    psVar2 = &DAT_UnitsState.units[uVar10].field323_0x418;
    *psVar2 = *psVar2 + -4;
    if (DAT_UnitsState.units[uVar10].field323_0x418 < 0x1f) {
      DAT_UnitsState.units[uVar10].animationCycleNumber = 0;
      DAT_UnitsState.units[uVar10].state.generic = US_MOVE_TO_DESTINATION;
      DAT_UnitsState.units[uVar10].field323_0x418 = 0;
      DAT_UnitsState.units[uVar10].field324_0x41a = 0x20;
      DAT_UnitsState.units[uVar10].field320_0x413 = 0;
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_UnitsState.units[uVar10].x,
                 (int)DAT_UnitsState.units[uVar10].y,FX_ASS_LAND);
      return;
    }
  }
  return;
}



// ================= updateUnitFadeAndVisibilityNearStructures @ 00533d50 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::UnitsState::updateUnitFadeAndVisibilityNearStructures
          (UnitsState *this,int unitID)

{
  byte bVar1;
  ushort uVar2;
  short sVar3;
  int iVar4;
  uint uVar5;
  bool bVar6;
  byte bVar7;
  byte bVar8;
  byte bVar9;
  
  iVar4 = DAT_UnitsState.units[unitID].tile;
  bVar1 = DAT_UnitsState.units[unitID].unknownCountdown_0x402;
  uVar2 = DAT_TileMapState.BuildingLayer[iVar4];
  uVar5 = DAT_TileMapState.LogicLayer[iVar4];
  bVar9 = 0;
  bVar6 = false;
  bVar8 = 0;
  bVar7 = 0;
  if (bVar1 != 0) {
    DAT_UnitsState.units[unitID].unknownCountdown_0x402 = bVar1 - 1;
  }
  if ((short)uVar2 == 0) {
    if ((uVar5 & 0x100) != 0) {
      bVar6 = true;
    }
  }
  else {
    switch(DAT_BuildingsState.buildings[(short)uVar2].buildingType) {
    case BT_GATEHOUSELARGE:
    case BT_GATEHOUSESMALL:
      bVar9 = 0xb;
      break;
    case BT_WOODGATE1:
      bVar9 = 10;
      break;
    case BT_TOWER1:
      bVar8 = 1;
      break;
    case BT_TOWER2:
      bVar8 = 2;
      break;
    case BT_TOWER3:
      bVar8 = 3;
      break;
    case BT_TOWER4:
    case BT_TOWER5:
      bVar8 = 4;
    }
  }
  sVar3 = DAT_UnitsState.units[unitID].field175_0x308;
  if ((sVar3 == 2) && (bVar6)) {
    bVar7 = 1;
  }
  if ((sVar3 == 1) && (bVar8 != 0)) {
    bVar7 = bVar8;
  }
  if (sVar3 == 0) {
    if (bVar9 == 0) goto LAB_00533eac;
    iVar4 = DAT_UnitsState.units[unitID].destinationTilePosition;
    if (((DAT_TileMapState.LogicLayer[iVar4] & 0x100U) != 0) ||
       (DAT_BuildingDefinedData.DAT_IsGateOrTowerArray
        [(short)DAT_BuildingsState.buildings[(short)DAT_TileMapState.BuildingLayer[iVar4]].
                buildingType] != FALSE)) {
      bVar7 = bVar9;
    }
  }
  if (bVar9 != 0) {
    iVar4 = DAT_UnitsState.units[unitID].destinationTilePosition;
    if (((DAT_TileMapState.LogicLayer[iVar4] & 0x100U) == 0) ||
       ((DAT_TileMapState.LogicLayer[iVar4] & 2U) != 0)) {
      DAT_UnitsState.units[unitID].unknownCountdown_0x402 =
           (DAT_BuildingDefinedData.DAT_IsGateOrTowerArray
            [(short)DAT_BuildingsState.buildings[(short)DAT_TileMapState.BuildingLayer[iVar4]].
                    buildingType] != FALSE) - 1U & 10;
    }
    else {
      DAT_UnitsState.units[unitID].unknownCountdown_0x402 = 0;
    }
  }
LAB_00533eac:
  if (bVar6) {
    DAT_UnitsState.units[unitID].field175_0x308 = 1;
  }
  else if (bVar8 == 0) {
    DAT_UnitsState.units[unitID].field175_0x308 = -(ushort)(bVar9 != 0) & 3;
  }
  else {
    DAT_UnitsState.units[unitID].field175_0x308 = 2;
  }
  if ((DAT_UnitsState.units[unitID].unknownCountdown_0x402 == 0) ||
     ((DAT_TileMapState.MiscDisplayLayer[DAT_UnitsState.units[unitID].nextTileUnk] & 0x10) != 0)) {
    DAT_UnitsState.units[unitID].vanish = 0;
  }
  else if ((DAT_TileMapState.MiscDisplayLayer[DAT_UnitsState.units[unitID].currentTilePosition_2Unk]
           & 0x10) == 0) {
    if (DAT_UnitsState.units[unitID].vanish < 1) {
      DAT_UnitsState.units[unitID].vanish = 1;
    }
  }
  else {
    DAT_UnitsState.units[unitID].vanish = 0xf;
  }
  if (bVar7 != 0) {
    DAT_UnitsState.units[unitID].fadeType = bVar7;
    DAT_UnitsState.units[unitID].fadeCounter = 0;
  }
  return;
}



// ================= clearHiddenFlagAndUpdatePosition @ 0053e8d0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::UnitsState::clearHiddenFlagAndUpdatePosition(UnitsState *this,int unitID)

{
  if (DAT_UnitsState.units[unitID].unknownTestAgainst0_2 != 0) {
    DAT_UnitsState.units[unitID].unknownTestAgainst0_2 = 0;
    commitPendingUnitPosition(&DAT_UnitsState,unitID);
    return;
  }
  return;
}



// ================= setUnitValues @ 0053b8e0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::UnitsState::setUnitValues(UnitsState *this,int unitID,UnitType unitType)

{
  short sVar1;
  int iVar2;
  byte bVar3;
  short sVar4;
  
  DAT_UnitsState.units[unitID].unitType = (UnitTypeShort)unitType;
  DAT_UnitsState.units[unitID].field67_0x90 =
       (short)DAT_UnitPropertiesDefinedData.field65_0x7634[unitType];
  DAT_UnitsState.units[unitID].unknownTestAgainst0_1 =
       (byte)DAT_UnitPropertiesDefinedData.field66_0x7774[unitType];
  sVar4 = (short)DAT_UnitPropertiesDefinedData.DAT_SPRITE_ID[unitType];
  DAT_UnitsState.units[unitID].gmIDUnk = sVar4;
  DAT_UnitsState.units[unitID].spriteID = sVar4;
  DAT_UnitsState.units[unitID].gfxNumber = 1;
  DAT_UnitsState.units[unitID].field22_0x2a =
       (short)DAT_TextureRenderCoreObject.gmFileHeaderColorpaletteArray[sVar4].originX;
  *(short *)&DAT_UnitsState.units[unitID].unknownV =
       (short)DAT_TextureRenderCoreObject.gmFileHeaderColorpaletteArray[sVar4].originY;
  sVar4 = (short)DAT_UnitPropertiesDefinedData.DAT_UNIT_SPRITE_DIMENSIONS[unitType][0];
  DAT_UnitsState.units[unitID].spriteWidthUnk = sVar4;
  DAT_UnitsState.units[unitID].spriteHeightUnk =
       (short)DAT_UnitPropertiesDefinedData.DAT_UNIT_SPRITE_DIMENSIONS[unitType][1];
  iVar2 = DAT_UnitsState.units[unitID].unknownV;
  sVar1 = DAT_UnitsState.units[unitID].spriteHeightUnk;
  DAT_UnitsState.units[unitID].drawXOffset = DAT_UnitsState.units[unitID].field22_0x2a - sVar4 / 2;
  DAT_UnitsState.units[unitID].someDrawYOffset = ((short)iVar2 - sVar1) + 3;
  sVar4 = (short)DAT_UnitPropertiesDefinedData.DAT_UNIT_MOVEMENT_SPEED_ARRAY[unitType];
  DAT_UnitsState.units[unitID].movementSpeed = sVar4;
  DAT_UnitsState.units[unitID].calculatedMovementSpeed = sVar4;
  DAT_UnitsState.units[unitID].field216_0x354 = 0;
  DAT_UnitsState.units[unitID].field215_0x350 = 0;
  iVar2 = DAT_UnitPropertiesDefinedData.DAT_BASE_HP[unitType];
  DAT_UnitsState.units[unitID].maxHealth = iVar2;
  DAT_UnitsState.units[unitID].health = iVar2;
  if (iVar2 == 0) {
    sVar4 = 100;
  }
  else {
    sVar4 = (short)((iVar2 * 100) / iVar2);
  }
  DAT_UnitsState.units[unitID].healthPercentage = sVar4;
  bVar3 = DAT_UnitsState.units[unitID].firstNameIndex;
  DAT_UnitsState.units[unitID].healthbar =
       (sVar4 / 10 + (sVar4 >> 0xf)) - (short)((longlong)(int)sVar4 * 0x66666667 >> 0x3f);
  DAT_UnitsState.units[unitID].unitCanClimb =
       (short)DAT_UnitPropertiesDefinedData.DAT_UNIT_CLIMB[unitType];
  DAT_UnitsState.units[unitID].someUnitStat4 =
       (short)DAT_UnitPropertiesDefinedData.DAT_SomeUnitStatMatrix4[unitType];
  DAT_UnitsState.units[unitID].graphicSize =
       (short)DAT_UnitPropertiesDefinedData.DAT_GRAPHIC_SIZE[unitType];
  DAT_UnitsState.units[unitID].someUnitStat2_meleeDamageUnk =
       (short)DAT_UnitPropertiesDefinedData.DAT_UNIT_CAN_MELEE[unitType];
  DAT_UnitsState.units[unitID].enemyNoticeFrequencyUnk =
       DAT_UnitPropertiesDefinedData.DAT_UNIT_ENEMY_NOTICE_RANGE[unitType];
  DAT_UnitsState.units[unitID].moveableUnk =
       (short)DAT_UnitPropertiesDefinedData.DAT_UNIT_MOVABLE[unitType];
  if ((((((char)bVar3 < '\x01') || (unitType == UT_BREWER)) || (unitType == UT_TANNER)) ||
      ((unitType == UT_LADY || (unitType == UT_MOTHER)))) ||
     ((unitType == UT_JUGGLER || ((unitType == UT_FIREEATER || (unitType == UT_PRIEST)))))) {
    assignNameToUnit(&DAT_UnitsState,unitID);
  }
  sVar4 = DAT_UnitsState.units[unitID].owner;
  if (sVar4 < 1) {
    bVar3 = 0xff;
    DAT_UnitsState.units[unitID].occupancyOrFlag = 0xff;
  }
  else {
    bVar3 = '\x01' << ((char)sVar4 - 1U & 0x1f);
    DAT_UnitsState.units[unitID].occupancyOrFlag = bVar3;
    bVar3 = ~bVar3;
  }
  DAT_UnitsState.units[unitID].field275_0x3d1 = bVar3;
  DAT_UnitsState.units[unitID].isSelectable_OR_matchTime = 0;
  DAT_UnitsState.units[unitID].field333_0x430 = 0;
  if (unitType != UT_CAGEDOG) {
    DAT_UnitsState.units[unitID].unknownBool01 = 500;
  }
                    /* Assassin */
  if (unitType == UT_A_ASSASSIN) {
    DAT_UnitsState.units[unitID].assassinsMicroDistanceToEnemyUnk = 32000;
  }
  return;
}



// ================= registerSpottedEnemyTile @ 0051be60 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::TroopValueState::registerSpottedEnemyTile
          (TroopValueState *this,int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (((((DAT_GameSynchronyState.currentGameMode == GM_SOLITARY) &&
        (DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].keep.id < 1)) &&
       (iVar2 = (int)(short)DAT_TileMapState.UnitLayer[param_1], 0 < iVar2)) &&
      ((DAT_GameSynchronyState.currentPlayerFullIDArray[DAT_UnitsState.units[iVar2].owner] != -1 &&
       (DAT_UnitsState.units[iVar2].isSelectable_OR_matchTime != 0)))) &&
     ((DAT_TileMapState.EntityLayer[param_1] == 0 ||
      (DAT_EntityState.entityArray[DAT_TileMapState.EntityLayer[param_1]].entityType != ET_FIRE))))
  {
    iVar2 = -1;
    iVar3 = 0;
    do {
      iVar1 = DAT_TroopValueState.attackInfo.field127521_0x2b254[iVar3].tile;
      if (iVar1 == param_1) {
        return;
      }
      if ((iVar1 == 0) && (iVar2 == -1)) {
        iVar2 = iVar3;
      }
      iVar3 = iVar3 + 1;
    } while (iVar3 < 100);
    if (-1 < iVar2) {
      DAT_TroopValueState.attackInfo.field127521_0x2b254[iVar2].tile = param_1;
      DAT_TroopValueState.attackInfo.field127521_0x2b254[iVar2].value = 100;
    }
  }
  return;
}



