// ================= arrowShootingRelated @ 00404a10 =================

/* decompilerscript: committed: 2025-01-30 21:56:35.138000 */

int __thiscall
_HoldStrong::Map::Entities::EntityState::arrowShootingRelated
          (EntityState *this,int microX,int microY,int height,int destMicroX,int destMicroY,
          int destHeight)

{
  uint uVar1;
  
  uVar1 = computeLineOfSightDistance
                    (&DAT_EntityState,microX,microY,height,destMicroX,destMicroY,destHeight,0);
  if (uVar1 == 0) {
    uVar1 = computeLineOfSightDistance
                      (&DAT_EntityState,destMicroX,destMicroY,destHeight,microX,microY,height,0);
  }
  return uVar1;
}



// ================= computeLineOfSightDistance @ 00402e20 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:56:35.138000 */

uint __thiscall
_HoldStrong::Map::Entities::EntityState::computeLineOfSightDistance
          (EntityState *this,int x,int y,int height,int targetX,int targetY,int targetHeight,
          int param_7)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  bool bVar4;
  bool bVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  int iVar13;
  int iVar14;
  int *piVar15;
  uint local_44;
  uint local_40;
  int local_3c;
  int local_38;
  uint local_30;
  int local_1c;
  
  iVar9 = y;
  local_1c = -1;
  uVar12 = 0;
  local_44 = 100000;
  local_30 = 0;
  local_40 = 0;
  bVar4 = true;
  bVar5 = false;
  if (targetHeight + 0x36 < height) {
    uVar12 = 100;
    local_40 = 100;
  }
  iVar6 = (int)(y + (y >> 0x1f & 7U)) >> 3;
  iVar10 = (int)((x >> 0x1f & 7U) + x) >> 3;
  iVar7 = DAT_ViewportRenderState.translationMatrix[iVar6].addXgetTile + iVar10;
  local_3c = x;
  local_38 = y;
  if ((DAT_TileMapState.LogicLayer[iVar7] & 0x10000000U) != 0) {
    height = height + 10;
  }
  uVar3 = 0xffff;
  if (DAT_TileMapState.BuildingLayer[iVar7] != 0) {
    uVar3 = DAT_TileMapState.BuildingLayer[iVar7];
  }
  if (targetY < y) {
    iVar7 = y - targetY;
  }
  else {
    iVar7 = targetY - y;
  }
  if (targetX < x) {
    iVar11 = x - targetX;
  }
  else {
    iVar11 = targetX - x;
  }
  iVar1 = (uint)(x <= targetX) * 2 + -1;
  iVar2 = (uint)(y <= targetY) * 2 + -1;
  if (iVar11 == 0) {
    if (iVar7 != 0) {
      if (0x1b < uVar12) {
        uVar12 = 0x1c;
      }
      uVar8 = 0;
      local_40 = uVar12 / 2;
      local_44 = 0;
      iVar9 = -1;
      DAT_EntityState.lineOfSightClearanceSteps = uVar12;
      do {
        local_38 = local_38 + iVar2;
        iVar6 = iVar9;
        if (((local_44 & 1) != 0) && (param_7 == 0)) {
          iVar6 = DAT_ViewportRenderState.translationMatrix
                  [(int)(local_38 + (local_38 >> 0x1f & 7U)) >> 3].addXgetTile + iVar10;
          if ((DAT_TileMapState.LogicLayer[iVar6] & 0x400300U) == 0) {
            bVar4 = false;
            DAT_EntityState.lineOfSightClearanceSteps = local_44;
          }
          if (local_40 == 0) {
            if (iVar9 == iVar6) {
              if (bVar5) {
                uVar12 = local_38 - y >> 0x1f;
                iVar9 = ((local_38 - y ^ uVar12) - uVar12) * (targetHeight - height);
                goto LAB_004033cf;
              }
            }
            else {
              bVar5 = false;
              if (((char)DAT_TileMapState.LogicLayer[iVar6] < '\0') ||
                 ((uVar3 != DAT_TileMapState.BuildingLayer[iVar6] &&
                  ((!bVar4 || ((DAT_TileMapState.LogicLayer[iVar6] & 0x400200U) == 0)))))) {
                bVar5 = true;
                uVar8 = TileMapState::returnSomeHeight(&DAT_TileMapState,iVar6,1);
                uVar12 = local_38 - y >> 0x1f;
                iVar9 = ((local_38 - y ^ uVar12) - uVar12) * (targetHeight - height);
LAB_004033cf:
                if (iVar9 / iVar7 + height < (int)uVar8) {
                  return 0;
                }
              }
            }
          }
          else {
            local_40 = local_40 - 1;
          }
        }
        if ((x == targetX) && (local_38 == targetY)) {
          return local_44;
        }
        local_44 = local_44 + 1;
        iVar9 = iVar6;
        if (999 < (int)local_44) {
          return local_44;
        }
      } while( true );
    }
  }
  else {
    if (iVar7 == 0) {
      if (0x1b < uVar12) {
        uVar12 = 0x1c;
      }
      uVar8 = uVar12 / 2;
      local_44 = 0;
      DAT_EntityState.lineOfSightClearanceSteps = uVar12;
      while( true ) {
        local_3c = local_3c + iVar1;
        if (((local_44 & 1) != 0) && (param_7 == 0)) {
          iVar9 = ((int)(local_3c + (local_3c >> 0x1f & 7U)) >> 3) +
                  DAT_ViewportRenderState.translationMatrix[iVar6].addXgetTile;
          if ((DAT_TileMapState.LogicLayer[iVar9] & 0x400300U) == 0) {
            bVar4 = false;
            DAT_EntityState.lineOfSightClearanceSteps = local_44;
          }
          if (uVar8 == 0) {
            if (local_1c == iVar9) {
              local_1c = iVar9;
              if ((bVar5) &&
                 (uVar12 = local_3c - x >> 0x1f,
                 (int)(((local_3c - x ^ uVar12) - uVar12) * (targetHeight - height)) / iVar11 +
                 height < (int)local_30)) {
                return 0;
              }
            }
            else {
              bVar5 = false;
              if (((char)DAT_TileMapState.LogicLayer[iVar9] < '\0') ||
                 ((local_1c = iVar9, uVar3 != DAT_TileMapState.BuildingLayer[iVar9] &&
                  ((!bVar4 || ((DAT_TileMapState.LogicLayer[iVar9] & 0x400200U) == 0)))))) {
                bVar5 = true;
                local_30 = TileMapState::returnSomeHeight(&DAT_TileMapState,iVar9,1);
                uVar12 = local_3c - x >> 0x1f;
                local_1c = iVar9;
                if ((int)(((local_3c - x ^ uVar12) - uVar12) * (targetHeight - height)) / iVar11 +
                    height < (int)local_30) {
                  return 0;
                }
              }
            }
          }
          else {
            uVar8 = uVar8 - 1;
            local_1c = iVar9;
          }
        }
        if ((local_3c == targetX) && (y == targetY)) break;
        local_44 = local_44 + 1;
        if (999 < (int)local_44) {
          return local_44;
        }
      }
      return local_44;
    }
    if (iVar7 <= iVar11) {
      iVar7 = iVar7 * 2;
      iVar6 = iVar7 - iVar11;
      if ((targetHeight < height) && (uVar12 != 0)) {
        uVar8 = targetX - x >> 0x1f;
        iVar10 = (targetX - x ^ uVar8) - uVar8;
        iVar10 = ((int)(iVar10 + (iVar10 >> 0x1f & 7U)) >> 3) + -1;
        if (4 < iVar10) {
          iVar10 = 4;
        }
        if (1 < iVar10) {
          y = iVar10 + -1;
          iVar10 = iVar1;
          do {
            local_30 = TileMapState::returnSomeHeight
                                 (&DAT_TileMapState,
                                  (((int)(targetX + (targetX >> 0x1f & 7U)) >> 3) - iVar10) +
                                  DAT_ViewportRenderState.translationMatrix
                                  [(int)(targetY + (targetY >> 0x1f & 7U)) >> 3].addXgetTile,1);
            if (targetHeight < (int)local_30) {
              uVar12 = 0x1c;
            }
            iVar10 = iVar10 + iVar1;
            y = y + -1;
          } while (y != 0);
        }
      }
      local_40 = uVar12 / 2;
      local_44 = 0;
      iVar10 = x;
      iVar14 = -1;
      DAT_EntityState.lineOfSightClearanceSteps = uVar12;
      while( true ) {
        iVar10 = iVar10 + iVar1;
        iVar13 = iVar7;
        if (0 < iVar6) {
          iVar9 = iVar9 + iVar2;
          iVar13 = iVar7 + iVar11 * -2;
          local_38 = iVar9;
        }
        iVar6 = iVar6 + iVar13;
        iVar13 = iVar14;
        if (((local_44 & 1) != 0) && (param_7 == 0)) {
          iVar13 = ((int)(iVar10 + (iVar10 >> 0x1f & 7U)) >> 3) +
                   DAT_ViewportRenderState.translationMatrix
                   [(int)(iVar9 + (iVar9 >> 0x1f & 7U)) >> 3].addXgetTile;
          if ((DAT_TileMapState.LogicLayer[iVar13] & 0x400300U) == 0) {
            bVar4 = false;
            DAT_EntityState.lineOfSightClearanceSteps = local_44;
          }
          if (local_40 == 0) {
            if (iVar14 == iVar13) {
              if ((bVar5) &&
                 (uVar12 = iVar10 - x >> 0x1f,
                 (int)(((iVar10 - x ^ uVar12) - uVar12) * (targetHeight - height)) / iVar11 + height
                 < (int)local_30)) {
                return 0;
              }
            }
            else {
              bVar5 = false;
              if (((char)DAT_TileMapState.LogicLayer[iVar13] < '\0') ||
                 ((uVar3 != DAT_TileMapState.BuildingLayer[iVar13] &&
                  ((!bVar4 || ((DAT_TileMapState.LogicLayer[iVar13] & 0x400200U) == 0)))))) {
                bVar5 = true;
                local_30 = TileMapState::returnSomeHeight(&DAT_TileMapState,iVar13,1);
                uVar12 = iVar10 - x >> 0x1f;
                iVar9 = local_38;
                if ((int)(((iVar10 - x ^ uVar12) - uVar12) * (targetHeight - height)) / iVar11 +
                    height < (int)local_30) {
                  return 0;
                }
              }
            }
          }
          else {
            local_40 = local_40 - 1;
          }
        }
        if ((iVar10 == targetX) && (iVar9 == targetY)) break;
        local_44 = local_44 + 1;
        iVar14 = iVar13;
        if (999 < (int)local_44) {
          return local_44;
        }
      }
      return local_44;
    }
    iVar11 = iVar11 * 2;
    iVar9 = iVar11 - iVar7;
    if ((targetHeight < height) && (local_40 != 0)) {
      uVar12 = targetY - y >> 0x1f;
      iVar6 = (targetY - y ^ uVar12) - uVar12;
      iVar6 = ((int)(iVar6 + (iVar6 >> 0x1f & 7U)) >> 3) + -1;
      if (4 < iVar6) {
        iVar6 = 4;
      }
      if (1 < iVar6) {
        piVar15 = (int *)((int)&DAT_ViewportRenderState +
                         (((int)(targetY + (targetY >> 0x1f & 7U)) >> 3) - iVar2) * 0xc + 0x188728);
        iVar6 = iVar6 + -1;
        do {
          local_30 = TileMapState::returnSomeHeight
                               (&DAT_TileMapState,
                                *piVar15 + ((int)(targetX + (targetX >> 0x1f & 7U)) >> 3),1);
          if (targetHeight < (int)local_30) {
            local_40 = 0x1c;
          }
          piVar15 = piVar15 + iVar2 * -3;
          iVar6 = iVar6 + -1;
        } while (iVar6 != 0);
      }
    }
    DAT_EntityState.lineOfSightClearanceSteps = local_40;
    local_40 = local_40 / 2;
    local_44 = 0;
    iVar6 = y;
    iVar10 = -1;
    do {
      iVar6 = iVar6 + iVar2;
      iVar14 = iVar11;
      if (0 < iVar9) {
        x = x + iVar1;
        iVar14 = iVar11 + iVar7 * -2;
        local_3c = x;
      }
      iVar9 = iVar9 + iVar14;
      iVar14 = iVar10;
      if (((local_44 & 1) != 0) && (param_7 == 0)) {
        iVar14 = ((int)(x + (x >> 0x1f & 7U)) >> 3) +
                 DAT_ViewportRenderState.translationMatrix[(int)(iVar6 + (iVar6 >> 0x1f & 7U)) >> 3]
                 .addXgetTile;
        if ((DAT_TileMapState.LogicLayer[iVar14] & 0x400300U) == 0) {
          bVar4 = false;
          DAT_EntityState.lineOfSightClearanceSteps = local_44;
        }
        if (local_40 == 0) {
          if (iVar10 == iVar14) {
            if ((bVar5) &&
               (uVar12 = iVar6 - y >> 0x1f,
               (int)(((iVar6 - y ^ uVar12) - uVar12) * (targetHeight - height)) / iVar7 + height <
               (int)local_30)) {
              return 0;
            }
          }
          else {
            bVar5 = false;
            if (((char)DAT_TileMapState.LogicLayer[iVar14] < '\0') ||
               ((uVar3 != DAT_TileMapState.BuildingLayer[iVar14] &&
                ((!bVar4 || ((DAT_TileMapState.LogicLayer[iVar14] & 0x400200U) == 0)))))) {
              bVar5 = true;
              local_30 = TileMapState::returnSomeHeight(&DAT_TileMapState,iVar14,1);
              uVar12 = iVar6 - y >> 0x1f;
              x = local_3c;
              if ((int)(((iVar6 - y ^ uVar12) - uVar12) * (targetHeight - height)) / iVar7 + height
                  < (int)local_30) {
                return 0;
              }
            }
          }
        }
        else {
          local_40 = local_40 - 1;
        }
      }
    } while (((x != targetX) || (iVar6 != targetY)) &&
            (local_44 = local_44 + 1, iVar10 = iVar14, (int)local_44 < 1000));
  }
  return local_44;
}



// ================= updateUnits @ 00579300 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Map::Units::UnitsState::updateUnits(UnitsState *this)

{
  int *piVar1;
  undefined1 *puVar2;
  short *psVar3;
  UnitLogicStateShort *pUVar4;
  byte bVar5;
  ushort uVar6;
  BuildingTypeShort BVar7;
  UnitTypeShort UVar8;
  short sVar9;
  UnitStateShort UVar10;
  int iVar11;
  uint uVar12;
  int *piVar13;
  dword dVar14;
  byte *pbVar15;
  uint y;
  byte bVar16;
  short sVar17;
  uint uVar18;
  uint uVar19;
  
  uVar19 = (int)SEC_RNG.currentNumber2 & 0x8000000f;
  if ((int)uVar19 < 0) {
    uVar19 = (uVar19 - 1 | 0xfffffff0) + 1;
  }
  IO::LowLevelMemory::fillMemory_ByteValue
            (&DAT_LowLevelMemory,0x13a10,'\0',DAT_TileMapState.OccupancyLayer);
  DAT_GameState.playerDataArray[0].healerCount = 0;
  DAT_GameState.playerDataArray[1].healerCount = 0;
  DAT_GameState.playerDataArray[2].healerCount = 0;
  DAT_GameState.playerDataArray[3].healerCount = 0;
  DAT_GameState.playerDataArray[4].healerCount = 0;
  DAT_GameState.playerDataArray[5].healerCount = 0;
  DAT_GameState.playerDataArray[6].healerCount = 0;
  DAT_GameState.playerDataArray[7].healerCount = 0;
  DAT_GameState.playerDataArray[8].healerCount = 0;
  DAT_UnitsState.DAT_UnitCount = 0;
  DAT_UnitsState.maxUnitCount = 0;
  DAT_CurrentUnitSlotID = 1;
  do {
    uVar18 = DAT_CurrentUnitSlotID;
    if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].logicalState != ULS_INVISIBLE) {
      DAT_UnitsState.maxUnitCount = DAT_CurrentUnitSlotID + 1;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].field250_0x39a = 0;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].attackedBy = 0;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].huntedBy = 0;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].field282_0x3dc = 0;
      DAT_UnitsState.units[DAT_CurrentUnitSlotID].field46_0x64 = 0;
                    /* This literally does nothing, this variable is not used elsewhere, what the
                       hell? */
      psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetShootRelated;
      if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetShootRelated != 0) {
        *psVar3 = *psVar3 + -1;
      }
      uVar18 = DAT_CurrentUnitSlotID;
      if ((DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic == US_DETERMINE_NEXT_STATEUnk)
         && (iVar11 = isUnitRegisteredOnItsOwnTile(&DAT_UnitsState,DAT_CurrentUnitSlotID),
            iVar11 == 0)) {
        DAT_UnitsState.DAT_LostChimps = DAT_UnitsState.DAT_LostChimps + 1;
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].logicalState = ULS_REMOVE;
        uVar18 = DAT_CurrentUnitSlotID;
      }
      sVar17 = DAT_UnitsState.units[uVar18].owner;
      if (DAT_GameSynchronyState.currentPlayerFullIDArray[sVar17] == -1) {
        DAT_UnitsState.units[uVar18].siegeTargetPlayerID =
             (short)DAT_GameState.playerDataArray[sVar17].attackedPlayerID;
      }
      else {
        DAT_UnitsState.units[uVar18].siegeTargetPlayerID = 0;
      }
      if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].blessedAmount == 0) {
        uVar18 = DAT_CurrentUnitSlotID;
        if (DAT_UnitPropertiesDefinedData.DAT_NotBlessableUnits
            [(short)DAT_UnitsState.units[DAT_CurrentUnitSlotID].unitType] == 0) {
          piVar13 = &DAT_GameState.playerDataArray[sVar17].unblessedPeopleCountUnk;
          goto LAB_005794f3;
        }
      }
      else {
        piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].blessedAmount;
        *piVar13 = *piVar13 + -1;
        piVar13 = &DAT_GameState.playerDataArray[sVar17].blessedPeopleCountUnk;
LAB_005794f3:
        uVar18 = DAT_CurrentUnitSlotID;
        *piVar13 = *piVar13 + 1;
      }
      uVar12 = uVar18 & 0x8000000f;
      if ((int)uVar12 < 0) {
        uVar12 = (uVar12 - 1 | 0xfffffff0) + 1;
      }
      if (uVar12 == uVar19) {
        iVar11 = DAT_UnitsState.units[uVar18].tile;
        if (((((DAT_TileMapState.PathConnectionLayer[iVar11] == 0) &&
              ((DAT_TileMapState.LogicLayer[iVar11] & 0x40000000U) == 0)) &&
             (DAT_UnitsState.units[uVar18].moveRelatedFlag != 1)) &&
            ((uVar6 = DAT_TileMapState.BuildingLayer[iVar11], uVar6 == 0 ||
             (((DAT_BuildingsState.buildings[(short)uVar6].logicalState == BLS_NORMAL &&
               (BVar7 = DAT_BuildingsState.buildings[(short)uVar6].buildingType,
               DAT_BuildingDefinedData.DAT_BuildingIsGateHouseArray[(short)BVar7] == 0)) &&
              (BVar7 != BT_DRAWBRIDGE)))))) &&
           (DAT_UnitsState.units[uVar18].state.generic != US_DISAPPEAR)) {
          if (DAT_UnitsState.units[uVar18].unitType == UT_CHICKEN) {
            Audio::SFX::SFXState::playSFXAtLocation
                      (&DAT_SFXState,(int)DAT_UnitsState.units[uVar18].x,
                       (int)DAT_UnitsState.units[uVar18].y,FX_CHICKEN_FLAP);
            uVar18 = DAT_CurrentUnitSlotID;
          }
          if ((999 < (int)(DAT_GameCore.mapTimeInTicks - DAT_UnitsState.units[uVar18].time)) &&
             (UVar8 = DAT_UnitsState.units[uVar18].unitType, UVar8 != UT_S_TOWER)) {
            if (UVar8 == UT_LORD) {
              y = (uint)DAT_UnitsState.units[uVar18].targetY_2;
              uVar12 = (uint)DAT_UnitsState.units[uVar18].targetX_2;
              setPositionOfUnit(&DAT_UnitsState,uVar18,uVar12,y,
                                (uint)*(byte *)(DAT_ViewportRenderState.translationMatrix[y].
                                                addXgetTile + 0x1d32c38 + uVar12));
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic = US_IDLEUnk;
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].destinationNeeded =
                   DNE_DESTINATION_HAS_BEEN_SET;
              uVar18 = DAT_CurrentUnitSlotID;
            }
            else {
              DAT_UnitsState.units[uVar18].state.generic = US_DISAPPEAR;
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].updateTickTracker = 0;
              uVar18 = DAT_CurrentUnitSlotID;
            }
          }
        }
        UVar8 = DAT_UnitsState.units[uVar18].unitType;
        if (((UVar8 == UT_S_CATAPULT) || (UVar8 == UT_S_FBALLISTA)) &&
           ((DAT_TileMapState.LogicLayer[DAT_UnitsState.units[uVar18].tile] & 0x50000000U) != 0)) {
          DAT_UnitsState.units[uVar18].state.generic = US_DISAPPEAR;
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].updateTickTracker = 0;
          uVar18 = DAT_CurrentUnitSlotID;
        }
      }
      if ((DAT_UnitsState.units[uVar18].logicalState == ULS_NORMAL) &&
         (((DAT_UnitsState.units[uVar18].x == 0 || (DAT_UnitsState.units[uVar18].y == 0)) ||
          (DAT_UnitsState.units[uVar18].tile < 0)))) {
        DAT_UnitsState.units[uVar18].state.generic = US_DISAPPEAR;
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].updateTickTracker = 0;
        uVar18 = DAT_CurrentUnitSlotID;
      }
    }
    DAT_CurrentUnitSlotID = uVar18 + 1;
  } while ((int)DAT_CurrentUnitSlotID < 0x9c4);
  DAT_CurrentUnitSlotID = 1;
  if (1 < (int)DAT_UnitsState.maxUnitCount) {
    do {
      if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].logicalState != ULS_INVISIBLE) {
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic == US_MELEE_ATTACK) {
          sVar17 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].attackedUnitID;
          psVar3 = &DAT_UnitsState.units[sVar17].attackedBy;
          *psVar3 = *psVar3 + 1;
          if ((int)DAT_UnitsState.units[sVar17].attackedUnitID != DAT_CurrentUnitSlotID) {
            psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].attackedBy;
            *psVar3 = *psVar3 + 1;
          }
          if ((DAT_UnitsState.units[sVar17].attackedBy == 1) &&
             (DAT_UnitsState.units[sVar17].unknownTestAgainst0_1 == 0)) {
            DAT_GameCore.cowPoisonTrackerUnk = DAT_GameCore.cowPoisonTrackerUnk + 1;
          }
        }
        sVar17 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].movementType_OR_targetUnitID;
        if (sVar17 != 0) {
          psVar3 = &DAT_UnitsState.units[sVar17].huntedBy;
          *psVar3 = *psVar3 + 1;
        }
        sVar17 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].field283_0x3de;
        if (sVar17 != 0) {
          psVar3 = &DAT_UnitsState.units[sVar17].field282_0x3dc;
          *psVar3 = *psVar3 + 1;
        }
        psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].field100_0xd0;
        if (0 < DAT_UnitsState.units[DAT_CurrentUnitSlotID].field100_0xd0) {
          *psVar3 = *psVar3 + -1;
        }
      }
      DAT_CurrentUnitSlotID = DAT_CurrentUnitSlotID + 1;
    } while ((int)DAT_CurrentUnitSlotID < (int)DAT_UnitsState.maxUnitCount);
  }
  uVar19 = DAT_GameCore.mapTimeInTicks & 0x3f;
  piVar13 = &DAT_GameState.playerDataArray[1].idlePeasantsCount;
  do {
    piVar13[0x15e] = 0;
    *piVar13 = 0;
    piVar13[0x15f] = 0;
    piVar13[0x160] = 0;
    piVar13[0x161] = 0;
    piVar13[0x374] = 0;
    piVar13[0x376] = 0;
    piVar13[-5] = 0;
    piVar13[-4] = 0;
    piVar13[0xf] = 0;
    piVar13[0x398] = 0;
    piVar13[0x10] = 0;
    piVar13[0x11] = 0;
    piVar13[0x12] = 0;
    piVar13[0x13] = 0;
    piVar13[0x14] = 0;
    piVar13[0x15] = 0;
    piVar13[0x16] = 0;
    piVar13[0x17] = 0;
    piVar13[0x18] = 0;
    piVar13[0x19] = 0;
    piVar13[0x36c] = 0;
    if (uVar19 == 0) {
      piVar13[0x35f] = 0;
    }
    piVar13 = piVar13 + 0xe7d;
  } while ((int)piVar13 < 0x117f2f8);
  DAT_CurrentUnitSlotID = 1;
  if (1 < (int)DAT_UnitsState.maxUnitCount) {
    do {
      if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].logicalState != ULS_INVISIBLE) {
        DAT_UnitsState.DAT_UnitCount = DAT_UnitsState.DAT_UnitCount + 1;
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].field67_0x90 != 0) {
          stampOccupancyFlagOnSurroundingTiles(&DAT_UnitsState,DAT_CurrentUnitSlotID);
        }
        uVar19 = DAT_CurrentUnitSlotID;
        DAT_TileMapState.OccupancyLayer[DAT_UnitsState.units[DAT_CurrentUnitSlotID].tile] =
             DAT_TileMapState.OccupancyLayer[DAT_UnitsState.units[DAT_CurrentUnitSlotID].tile] |
             DAT_UnitsState.units[DAT_CurrentUnitSlotID].occupancyOrFlag;
        piVar13 = DAT_UnitsState.unitCountOfSelection + uVar19 * 0x124 + -9;
        if (DAT_UnitsState.units[uVar19].isSelectable_OR_matchTime == 0) {
switchD_00579a5d_caseD_3:
        }
        else {
          sVar17 = DAT_UnitsState.units[uVar19].owner;
          if ((DAT_GameCore.mapTimeInTicks & 0x3f) == 0) {
            piVar13 = &DAT_GameState.playerDataArray[sVar17].totalTroopValue;
            iVar11 = TroopValueState::getValueOfTroopType
                               (&DAT_TroopValueState,
                                (int)(short)DAT_UnitsState.units[uVar19].unitType);
            *piVar13 = *piVar13 + iVar11;
            uVar19 = DAT_CurrentUnitSlotID;
            if ((char)DAT_UnitsState.units[DAT_CurrentUnitSlotID].firstNameIndex < '\x01') {
                    /* Every 0x3f ticks, assign names to citizen units */
              assignNameToUnit(&DAT_UnitsState,DAT_CurrentUnitSlotID);
              uVar19 = DAT_CurrentUnitSlotID;
            }
          }
          UVar8 = DAT_UnitsState.units[uVar19].unitType;
          if (UVar8 == UT_A_HARCHER) {
            DAT_TileMapState.SEC_TileMap1104[DAT_UnitsState.units[uVar19].tile] = '\x06';
          }
          else if (UVar8 == UT_A_FIRETHROWER) {
            writeSixToTileMap1104InAllDirections(&DAT_UnitsState,uVar19,6);
            uVar19 = DAT_CurrentUnitSlotID;
          }
          UVar8 = DAT_UnitsState.units[uVar19].unitType;
          piVar13 = DAT_UnitsState.unitCountOfSelection + uVar19 * 0x124 + -9;
          if (UVar8 == UT_LORD) goto switchD_00579a5d_caseD_3;
          sVar9 = DAT_UnitsState.units[uVar19].aiUnitBehaviourType;
          if (sVar9 == 10) {
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAttackingEngineerTroops;
            *piVar1 = *piVar1 + 1;
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAttackTroops;
            *piVar1 = *piVar1 + 1;
            goto LAB_00579bff;
          }
          if (UVar8 == UT_E_ENGINEER) goto switchD_00579a5d_caseD_3;
                    /* fixme: TODO, review this bit, cannot be true! */
          switch(sVar9) {
          case 0:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalTroopsType0;
            *piVar1 = *piVar1 + 1;
            break;
          case 1:
          case 4:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalDefensiveTroopsUnk;
            *piVar1 = *piVar1 + 1;
            break;
          case 2:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalRaidingTroopsUnk;
            *piVar1 = *piVar1 + 1;
            break;
          default:
            goto switchD_00579a5d_caseD_3;
          case 6:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalTroopsType6;
            *piVar1 = *piVar1 + 1;
            break;
          case 7:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalTroopsType7;
            *piVar1 = *piVar1 + 1;
            break;
          case 0xb:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalDiggingUnitTroops;
            *piVar1 = *piVar1 + 1;
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAttackTroops;
            *piVar1 = *piVar1 + 1;
            break;
          case 0xc:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAssassinTroops;
            *piVar1 = *piVar1 + 1;
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAttackTroops;
            *piVar1 = *piVar1 + 1;
            break;
          case 0xd:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalUnit2Troops;
            *piVar1 = *piVar1 + 1;
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAttackTroops;
            *piVar1 = *piVar1 + 1;
            break;
          case 0xe:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalLaddermenTroops;
            *piVar1 = *piVar1 + 1;
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAttackTroops;
            *piVar1 = *piVar1 + 1;
            break;
          case 0xf:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalTunnelerTroops;
            *piVar1 = *piVar1 + 1;
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAttackTroops;
            *piVar1 = *piVar1 + 1;
            break;
          case 0x10:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalUnitPatrolTroops;
            *piVar1 = *piVar1 + 1;
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAttackTroops;
            *piVar1 = *piVar1 + 1;
            break;
          case 0x11:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalUnitBackupTroops;
            *piVar1 = *piVar1 + 1;
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAttackTroops;
            *piVar1 = *piVar1 + 1;
            break;
          case 0x12:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalUnitEngageTroops;
            *piVar1 = *piVar1 + 1;
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAttackTroops;
            *piVar1 = *piVar1 + 1;
            break;
          case 0x13:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalUnitSiegeDefTroops;
            *piVar1 = *piVar1 + 1;
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAttackTroops;
            *piVar1 = *piVar1 + 1;
            break;
          case 0x14:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalMaxDefaultTroops;
            *piVar1 = *piVar1 + 1;
            piVar1 = &DAT_GameState.playerDataArray[sVar17].totalAttackTroops;
            *piVar1 = *piVar1 + 1;
            break;
          case 0x15:
            piVar1 = &DAT_GameState.playerDataArray[sVar17].harassingSiegeEnginesCountUnk;
            *piVar1 = *piVar1 + 1;
          }
        }
LAB_00579bff:
        if ((((*(short *)((int)piVar13 + 0x6a2) == 0x16) ||
             (*(short *)((int)piVar13 + 0x6a2) == 0x46)) &&
            (((short)piVar13[0x235] == 5 || ((short)piVar13[0x235] == 6)))) &&
           ((iVar11 = (int)(short)piVar13[0x256], 0 < iVar11 &&
            (DAT_UnitsState.units[iVar11].uid == piVar13[0x1ad])))) {
          DAT_UnitsState.units[iVar11].field250_0x39a = 1;
          uVar19 = DAT_CurrentUnitSlotID;
        }
        if ((DAT_UnitsState.units[uVar19].enemyNoticeFrequencyUnk != 0) &&
           (uVar18 = DAT_UnitsState.units[uVar19].enemyNoticeFrequencyUnk,
           (DAT_GameState.mapAndTime.totalGameTicksUnk & uVar18) ==
           (DAT_UnitsState.units[uVar19].fixedRng & uVar18))) {
          if (DAT_UnitsState.units[uVar19].owner == 0) {
            iVar11 = computeDistanceToNearestEnemyForLegacyMissions(&DAT_UnitsState,uVar19);
            DAT_UnitsState.units[uVar19].closestEnemyMicroDistance = (short)iVar11;
            uVar19 = DAT_CurrentUnitSlotID;
          }
          else {
            dVar14 = findNearestEnemyAndHeadTowardsIt(&DAT_UnitsState,uVar19);
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].closestEnemyMicroDistance = (short)dVar14;
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].assassinsMicroDistanceToEnemyUnk =
                 DAT_UnitsState.unitDistanceComputationResultUnk;
            uVar19 = DAT_CurrentUnitSlotID;
          }
        }
        psVar3 = &DAT_UnitsState.units[uVar19].lookForEnemy;
        if (DAT_UnitsState.units[uVar19].lookForEnemy < 0) {
          *psVar3 = *psVar3 + 1;
        }
        else {
          *psVar3 = 0;
        }
        psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].unknownMovementRelated_0x2d2;
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].unknownMovementRelated_0x2d2 < 0) {
          *psVar3 = *psVar3 + 1;
        }
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].SA = 0;
        if (DAT_TileMapState.refreshRelatedOne != 0) {
          bVar16 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].heightDiv10;
          if (bVar16 != 0) {
            puVar2 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].field_0x83;
            *puVar2 = *puVar2 - *(char *)((int)&DAT_UnitPropertiesDefinedData +
                                         (DAT_UpdateUnitsTracker - (uint)bVar16) * 4 + 0x11a24);
            if (100 < (byte)DAT_UnitsState.units[DAT_CurrentUnitSlotID].field_0x83) {
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].field_0x83 = 0;
            }
            if ((int)((byte)DAT_UnitsState.units[DAT_CurrentUnitSlotID].heightDiv10 + 0xd) <=
                DAT_UpdateUnitsTracker) {
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].heightDiv10 = 0;
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].field_0x83 = 0;
            }
          }
        }
      }
      DAT_CurrentUnitSlotID = DAT_CurrentUnitSlotID + 1;
    } while ((int)DAT_CurrentUnitSlotID < (int)DAT_UnitsState.maxUnitCount);
  }
  Entities::EntityState::recountActiveFires(&DAT_EntityState);
  Entities::EntityState::flagUnitsWithActiveEntity(&DAT_EntityState);
  DAT_CurrentUnitSlotID = 1;
  if (1 < (int)DAT_UnitsState.maxUnitCount) {
    do {
      pUVar4 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].logicalState;
      switch(DAT_UnitsState.units[DAT_CurrentUnitSlotID].logicalState) {
      case ULS_INVISIBLE:
        break;
      case 1:
        *pUVar4 = ULS_NORMAL;
      default:
        goto switchD_00579e2c_caseD_2;
      case ULS_REMOVE:
        deleteUnit(&DAT_UnitsState,DAT_CurrentUnitSlotID);
        break;
      case ULS_TRANSITIONING:
        changeUnitType(&DAT_UnitsState,DAT_CurrentUnitSlotID);
switchD_00579e2c_caseD_2:
        piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationTicker;
        *piVar13 = *piVar13 + 1;
        iVar11 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationTicker;
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSpeed +
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationLeapTicksTotal < iVar11) {
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationLeapTicksTotal = iVar11;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber;
          *piVar13 = *piVar13 + 1;
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumberHasJustIncremented = TRUE;
          uVar19 = DAT_CurrentUnitSlotID;
          if (999 < DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber) {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber = 0;
          }
        }
        else {
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumberHasJustIncremented = FALSE
          ;
          uVar19 = DAT_CurrentUnitSlotID;
        }
        sVar17 = (short)DAT_TileMapState.mapOrientation;
        if (DAT_UnitsState.units[uVar19].field42_0x58 == 0) {
          if (DAT_UnitsState.units[uVar19].state.generic != US_MELEE_ATTACK) {
            sVar17 = DAT_UnitsState.units[uVar19].facingDirection - sVar17;
            goto LAB_00579f48;
          }
          DAT_UnitsState.units[uVar19].facingDirectionMapOrientationCorrected =
               *(short *)&DAT_UnitsState.units[uVar19].field_0x2b6 - sVar17;
        }
        else {
          sVar17 = (short)DAT_TileMapState.field84_0x5548a4 - sVar17;
LAB_00579f48:
          DAT_UnitsState.units[uVar19].facingDirectionMapOrientationCorrected = sVar17;
        }
        psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].facingDirectionMapOrientationCorrected
        ;
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].facingDirectionMapOrientationCorrected < 0)
        {
          *psVar3 = *psVar3 + 8;
        }
        uVar19 = DAT_CurrentUnitSlotID;
        sVar17 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].owner;
        piVar13 = &DAT_GameState.playerDataArray[sVar17].countEntities;
        *piVar13 = *piVar13 + 1;
        if (DAT_UnitPropertiesDefinedData.DAT_COMPUTER_MANAGED
            [(short)DAT_UnitsState.units[uVar19].unitType] != 0) {
          piVar13 = &DAT_GameState.playerDataArray[sVar17].currentPopulation_2;
          *piVar13 = *piVar13 + 1;
        }
        DAT_UnitHasBecomeIdle = 0;
        if (((((DAT_UnitsState.units[uVar19].dying != 0) &&
              (UVar10 = DAT_UnitsState.units[uVar19].state.generic, UVar10 != US_DISAPPEAR)) &&
             (UVar8 = DAT_UnitsState.units[uVar19].unitType, UVar8 != UT_BURNINGMAN)) &&
            ((UVar8 != UT_BURNING_ANIMAL_BIG && (UVar8 != UT_BURNING_ANIMAL_SMALL)))) &&
           (((short)UVar10 < 0x6f || (0x75 < (short)UVar10)))) {
          DAT_UnitsState.units[uVar19].state.generic = US_DEATH_01;
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationCycleNumber = 0;
          uVar19 = DAT_CurrentUnitSlotID;
        }
        if (DAT_UnitPropertiesDefinedData.DAT_COMPUTER_CONTROLLED
            [(short)DAT_UnitsState.units[uVar19].unitType] != 0) {
          sVar17 = DAT_UnitsState.units[uVar19].workplaceBuildingID_1;
          if (DAT_BuildingsState.buildings[sVar17].uid ==
              DAT_UnitsState.units[uVar19].workplaceBuildingUID) {
            if (DAT_BuildingsState.buildings[sVar17].sleeping != false) {
              makeUnitStopWalkingByClearingPathProgressState(uVar19);
              if (7 < DAT_UnitsState.units[DAT_CurrentUnitSlotID].movementRelated) {
                DAT_UnitsState.units[DAT_CurrentUnitSlotID].logicalState = ULS_TRANSITIONING;
                DAT_UnitsState.units[DAT_CurrentUnitSlotID].unitTypeToChangeInto = UT_PEASANT;
                DAT_UnitsState.units[DAT_CurrentUnitSlotID].state_2 = 0;
                DAT_UnitsState.units[DAT_CurrentUnitSlotID].workplaceBuildingID_1 = 0;
                clearHiddenFlagAndUpdatePosition(&DAT_UnitsState,DAT_CurrentUnitSlotID);
              }
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].disappearFadeAlphaCountdown = 0;
              uVar19 = DAT_CurrentUnitSlotID;
            }
          }
          else {
            makeUnitStopWalkingByClearingPathProgressState(uVar19);
            uVar19 = DAT_CurrentUnitSlotID;
            if (7 < DAT_UnitsState.units[DAT_CurrentUnitSlotID].movementRelated) {
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].logicalState = ULS_TRANSITIONING;
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].unitTypeToChangeInto = UT_PEASANT;
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].state_2 = 0;
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].workplaceBuildingID_1 = 0;
              clearHiddenFlagAndUpdatePosition(&DAT_UnitsState,DAT_CurrentUnitSlotID);
              uVar19 = DAT_CurrentUnitSlotID;
            }
          }
        }
        DAT_UnitsState.units[uVar19].field134_0x2ac = 0;
        processMeleeInitiation(&DAT_UnitsState,DAT_CurrentUnitSlotID);
        DAT_UnitsState.units[DAT_CurrentUnitSlotID].field147_0x2c4 =
             (short)DAT_UnitsState.units[DAT_CurrentUnitSlotID].state;
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].logicalState != ULS_TRANSITIONING) {
                    /* Update unit state */
          (**(code **)(DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingDown +
                      (short)DAT_UnitsState.units[DAT_CurrentUnitSlotID].unitType * 4 + 0x14))();
        }
        uVar19 = DAT_CurrentUnitSlotID;
        UVar10 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].field147_0x2c4;
        if (((UVar10 != DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic) &&
            ((UVar10 == (US_DEATH_02|US_STAND_UPUnk|US_RELOAD_WEAPONUnk) || (UVar10 == US_DIG)))) &&
           (iVar11 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].digTileTarget,
           DAT_TileMapState.moats[iVar11].owner != 0)) {
          pbVar15 = &DAT_TileMapState.moats[iVar11].someCountDown;
          *pbVar15 = *pbVar15 - 0x14;
        }
        DAT_UnitsState.units[uVar19].field44_0x5c = 0;
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].usingTeleport == 0) {
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].field216_0x354;
                    /* Not climbing */
          *piVar13 = *piVar13 + 1;
          iVar11 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].field216_0x354;
          if ((int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].calculatedMovementSpeed +
              (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].stateBasedSpeed +
              (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].moveDelay <
              iVar11 - DAT_UnitsState.units[DAT_CurrentUnitSlotID].field215_0x350) {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].field215_0x350 = iVar11;
            psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].movementRunUpTime;
            if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].movementRunUpTime < 1) {
              *psVar3 = 0;
            }
            else {
              *psVar3 = *psVar3 + -1;
            }
            iVar11 = processUnitMove(&DAT_UnitsState,DAT_CurrentUnitSlotID,
                                     (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                                          stateBasedSpeed);
            if (iVar11 != 0) {
              if (((DAT_UnitsState.units[DAT_CurrentUnitSlotID].state.generic ==
                    US_MOVE_TO_DESTINATION) &&
                  (DAT_UnitsState.units[DAT_CurrentUnitSlotID].disappearFadeAlphaCountdown != 0)) &&
                 (DAT_UnitsState.units[DAT_CurrentUnitSlotID].fadeType == 0)) {
                DAT_UnitsState.units[DAT_CurrentUnitSlotID].disappearFadeAlphaCountdown = 0;
              }
              psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].field234_0x37e;
              *psVar3 = *psVar3 + 1;
              if (0xf < DAT_UnitsState.units[DAT_CurrentUnitSlotID].field234_0x37e) {
                DAT_UnitsState.units[DAT_CurrentUnitSlotID].field234_0x37e = 0;
              }
              psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].field233_0x37c;
              *psVar3 = *psVar3 + 2;
              if (0xd < DAT_UnitsState.units[DAT_CurrentUnitSlotID].field233_0x37c) {
                DAT_UnitsState.units[DAT_CurrentUnitSlotID].field233_0x37c = 0;
              }
              psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].field231_0x378;
              *psVar3 = *psVar3 + 2;
              if (0xf < DAT_UnitsState.units[DAT_CurrentUnitSlotID].field231_0x378) {
                DAT_UnitsState.units[DAT_CurrentUnitSlotID].field231_0x378 = 0;
              }
              psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].field271_0x3c6;
              *psVar3 = *psVar3 + 1;
              if (0x11 < DAT_UnitsState.units[DAT_CurrentUnitSlotID].field271_0x3c6) {
                DAT_UnitsState.units[DAT_CurrentUnitSlotID].field271_0x3c6 = 0;
              }
              psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].field329_0x428;
              *psVar3 = *psVar3 + 1;
              if (0x17 < DAT_UnitsState.units[DAT_CurrentUnitSlotID].field329_0x428) {
                DAT_UnitsState.units[DAT_CurrentUnitSlotID].field329_0x428 = 0;
              }
            }
            psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].field232_0x37a;
            *psVar3 = *psVar3 + 1;
            if (0xb < DAT_UnitsState.units[DAT_CurrentUnitSlotID].field232_0x37a) {
              DAT_UnitsState.units[DAT_CurrentUnitSlotID].field232_0x37a = 0;
            }
            calculateUnitMovementSpeed(&DAT_UnitsState,DAT_CurrentUnitSlotID);
          }
        }
        else {
                    /* Climbing */
          unitClimbing(&DAT_UnitsState,DAT_CurrentUnitSlotID);
        }
        recomputeUnitStandingHeight(&DAT_UnitsState,DAT_CurrentUnitSlotID);
        switch(DAT_UnitsState.units[DAT_CurrentUnitSlotID].field_0x30_animRelated) {
        case 8:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber =
               (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                    facingDirectionMapOrientationCorrected +
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
          *piVar13 = *piVar13 + DAT_UnitsState.units[DAT_CurrentUnitSlotID].field231_0x378 * 8;
          if (((DAT_UnitsState.units[DAT_CurrentUnitSlotID].unitType == UT_A_HARCHER) &&
              (sVar17 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].horseArcherShootingVariation,
              sVar17 != 4)) && ((sVar17 != 5 && (sVar17 != 6)))) {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageIDUnk =
                 DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
          }
          break;
        case 9:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber =
               (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                    facingDirectionMapOrientationCorrected +
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
          *piVar13 = *piVar13 + (DAT_UnitsState.units[DAT_CurrentUnitSlotID].field231_0x378 * 8) / 2
          ;
          break;
        case 0xc:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber =
               (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                    facingDirectionMapOrientationCorrected +
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
          *piVar13 = *piVar13 + DAT_UnitsState.units[DAT_CurrentUnitSlotID].field232_0x37a * 8;
          break;
        case 0xe:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber =
               (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                    facingDirectionMapOrientationCorrected +
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
          *piVar13 = *piVar13 + DAT_UnitsState.units[DAT_CurrentUnitSlotID].field233_0x37c * 8;
          break;
        case 0x10:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber =
               (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                    facingDirectionMapOrientationCorrected +
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
          *piVar13 = *piVar13 + DAT_UnitsState.units[DAT_CurrentUnitSlotID].field234_0x37e * 8;
          if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].unitType == UT_A_HARCHER) {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageIDUnk =
                 DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
          }
          if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].unitType == UT_E_KNIGHT) {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageIDUnk =
                 DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
            if ((DAT_CurrentUnitSlotID & 1) == 0) {
              if (((DAT_UnitsState.units[DAT_CurrentUnitSlotID].stateBasedSpeed != 0) &&
                  ((DAT_UnitsState.units[DAT_CurrentUnitSlotID].movementType_OR_targetUnitID != 0 ||
                   (DAT_UnitsState.units[DAT_CurrentUnitSlotID].targetingType ==
                    UIT_UNIT_ATTACK_UNIT)))) &&
                 (DAT_UnitsState.units[DAT_CurrentUnitSlotID].totalSizeOfPathPlan + -0x10 <=
                  (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].currentIndexInPathPlan)) {
                piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageIDUnk;
                *piVar13 = *piVar13 + 0x80;
              }
            }
            else {
              piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageIDUnk;
              *piVar13 = *piVar13 + 0x270;
            }
          }
          break;
        case 0x11:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber =
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].facingDirectionMapOrientationCorrected *
               0x10 + DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
          *piVar13 = *piVar13 + (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].field234_0x37e;
          break;
        case 0x12:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber =
               (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                    facingDirectionMapOrientationCorrected +
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
          *piVar13 = *piVar13 + DAT_UnitsState.units[DAT_CurrentUnitSlotID].field271_0x3c6 * 8;
          break;
        case 0x13:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageIDUnk =
               (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                    facingDirectionMapOrientationCorrected +
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
          goto LAB_0057a907;
        case 0x14:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageIDUnk =
               (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                    facingDirectionMapOrientationCorrected +
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
LAB_0057a907:
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageIDUnk;
          *piVar13 = *piVar13 +
                     ((int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].field231_0x378 / 2) * 8;
          break;
        case 0x15:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber =
               (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                    facingDirectionMapOrientationCorrected +
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
          *piVar13 = *piVar13 + DAT_UnitsState.units[DAT_CurrentUnitSlotID].field234_0x37e * 8;
          iVar11 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                   facingDirectionMapOrientationCorrected + 0x80 +
                   DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
          goto LAB_0057a7de;
        case 0x16:
          uVar19 = (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                        facingDirectionMapOrientationCorrected + 4U & 0x80000007;
          if ((int)uVar19 < 0) {
            uVar19 = (uVar19 - 1 | 0xfffffff8) + 1;
          }
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber = uVar19 + 0x151;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
          *piVar13 = *piVar13 +
                     ((byte)DAT_UnitsState.units[DAT_CurrentUnitSlotID].field234_0x37e & 3) * 8;
          uVar19 = (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                        facingDirectionMapOrientationCorrected + 4U & 0x80000007;
          if ((int)uVar19 < 0) {
            uVar19 = (uVar19 - 1 | 0xfffffff8) + 1;
          }
          iVar11 = uVar19 + 0x1d1;
LAB_0057a7de:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageIDUnk = iVar11;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageIDUnk;
          *piVar13 = *piVar13 + DAT_UnitsState.units[DAT_CurrentUnitSlotID].field234_0x37e * 8;
          break;
        case 0x18:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber =
               (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                    facingDirectionMapOrientationCorrected +
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].gfxNumber;
          *piVar13 = *piVar13 + DAT_UnitsState.units[DAT_CurrentUnitSlotID].field329_0x428 * 8;
          break;
        case 99:
          DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageID2 =
               (int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].
                    facingDirectionMapOrientationCorrected +
               DAT_UnitsState.units[DAT_CurrentUnitSlotID].animationSheetFrameOffset;
          piVar13 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].imageID2;
          *piVar13 = *piVar13 +
                     ((int)DAT_UnitsState.units[DAT_CurrentUnitSlotID].field231_0x378 / 2) * 8;
        }
        psVar3 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].unitSpeedMatchingRelatedUnk;
        if (DAT_UnitsState.units[DAT_CurrentUnitSlotID].unitSpeedMatchingRelatedUnk != 0) {
          *psVar3 = *psVar3 + -1;
        }
        bVar16 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].fadeType;
        if (bVar16 != 0) {
          if (bVar16 == 1) {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].disappearFadeAlphaCountdown =
                 (byte)DAT_UnitPropertiesDefinedData.ANIM_FadeAlpha_Values_1_2
                       [(char)DAT_UnitsState.units[DAT_CurrentUnitSlotID].fadeCounter];
          }
          else {
            if (bVar16 == 2) {
              bVar16 = (byte)DAT_UnitPropertiesDefinedData.ANIM_FadeAlpha_Values_1_2
                             [(char)DAT_UnitsState.units[DAT_CurrentUnitSlotID].fadeCounter];
            }
            else {
              bVar5 = DAT_UnitsState.units[DAT_CurrentUnitSlotID].fadeCounter;
              if (bVar16 == 3) {
                bVar16 = (byte)DAT_UnitPropertiesDefinedData.ANIM_FadeAlpha_Values_3[(char)bVar5];
              }
              else {
                bVar16 = (byte)DAT_UnitPropertiesDefinedData.ANIM_FadeAlpha_Values_4[(char)bVar5];
              }
            }
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].disappearFadeAlphaCountdown = bVar16;
          }
          pbVar15 = &DAT_UnitsState.units[DAT_CurrentUnitSlotID].fadeCounter;
          *pbVar15 = *pbVar15 + 1;
          if ((char)DAT_UnitsState.units[DAT_CurrentUnitSlotID].disappearFadeAlphaCountdown < '\x01'
             ) {
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].fadeType = 0;
            DAT_UnitsState.units[DAT_CurrentUnitSlotID].fadeCounter = 0;
          }
        }
        break;
      case 5:
        *pUVar4 = 1;
      }
      DAT_CurrentUnitSlotID = DAT_CurrentUnitSlotID + 1;
    } while ((int)DAT_CurrentUnitSlotID < (int)DAT_UnitsState.maxUnitCount);
  }
  if (DAT_TileMapState.refreshRelatedOne == 0) {
    DAT_UpdateUnitsTracker = 0;
    return;
  }
  DAT_UpdateUnitsTracker = DAT_UpdateUnitsTracker + 1;
  return;
}



