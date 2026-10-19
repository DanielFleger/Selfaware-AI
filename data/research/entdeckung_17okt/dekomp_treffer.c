// ================= doSomethingWithOtherEntitiesOnTile @ 00401460 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:56:35.138000 */

void __thiscall
_HoldStrong::Map::Entities::EntityState::doSomethingWithOtherEntitiesOnTile
          (EntityState *this,uint entityID)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  iVar1 = DAT_EntityState.entityArray[entityID].tile;
  iVar5 = 0;
  if (iVar1 != 0) {
    if ((int)entityID < 0x19) {
      uVar4 = (uint)(byte)DAT_TileMapState.EntityLayerLT25[iVar1];
      if (uVar4 == entityID) {
        DAT_TileMapState.EntityLayerLT25[iVar1] =
             (char)DAT_EntityState.entityArray[entityID].nextEntityOnThisTileByID;
        DAT_EntityState.entityArray[entityID].nextEntityOnThisTileByID = 0;
        return;
      }
      uVar2 = uVar4;
      if (uVar4 != 0) {
        while ((uVar3 = uVar2, iVar5 = iVar5 + 1, iVar5 < 100 &&
               (uVar2 = (uint)DAT_EntityState.entityArray[uVar3].nextEntityOnThisTileByID,
               uVar4 = uVar3, uVar2 != entityID))) {
          if (uVar2 == 0) {
            return;
          }
        }
      }
    }
    else {
      uVar4 = (uint)DAT_TileMapState.EntityLayer[iVar1];
      if (uVar4 == entityID) {
        DAT_TileMapState.EntityLayer[iVar1] =
             DAT_EntityState.entityArray[entityID].nextEntityOnThisTileByID;
        DAT_EntityState.entityArray[entityID].nextEntityOnThisTileByID = 0;
        return;
      }
      uVar2 = uVar4;
      if (uVar4 != 0) {
        while ((uVar3 = uVar2, iVar5 = iVar5 + 1, iVar5 < 100 &&
               (uVar2 = (uint)DAT_EntityState.entityArray[uVar3].nextEntityOnThisTileByID,
               uVar4 = uVar3, uVar2 != entityID))) {
          if (uVar2 == 0) {
            return;
          }
        }
      }
    }
    DAT_EntityState.entityArray[uVar4].nextEntityOnThisTileByID =
         DAT_EntityState.entityArray[entityID].nextEntityOnThisTileByID;
    DAT_EntityState.entityArray[entityID].nextEntityOnThisTileByID = 0;
  }
  return;
}



// ================= processEntityHitBuildingOrUnit @ 00407190 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::Entities::EntityState::processEntityHitBuildingOrUnit
          (EntityState *this,int entityID)

{
  int *piVar1;
  short *psVar2;
  EntityTypeShort EVar3;
  ushort uVar4;
  short sVar5;
  BuildingTypeShort BVar6;
  short sVar7;
  short sVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  BOOLEnum BVar12;
  uint uVar13;
  int iVar14;
  Point8IntXY *pPVar15;
  int iVar16;
  EntityState *local_10;
  int local_c;
  int _tile;
  uint local_4;
  
  local_10 = &DAT_EntityState;
  iVar9 = (int)DAT_EntityState.entityArray[entityID].microX;
  iVar10 = (int)DAT_EntityState.entityArray[entityID].microY;
  sVar8 = (short)((int)(iVar10 + (iVar10 >> 0x1f & 7U)) >> 3);
  DAT_EntityState.entityArray[entityID].yPosition = sVar8;
  uVar11 = (uint)sVar8;
  sVar8 = (short)((int)(iVar9 + (iVar9 >> 0x1f & 7U)) >> 3);
  DAT_EntityState.entityArray[entityID].xPosition = sVar8;
  uVar13 = (uint)sVar8;
  EVar3 = DAT_EntityState.entityArray[entityID].entityType;
  iVar9 = DAT_ViewportRenderState.translationMatrix[uVar11].addXgetTile + uVar13;
  local_c = 1;
  DAT_EntityState.entityArray[entityID].tile = iVar9;
  if (EVar3 == ET_SEAGULLUnk) {
    if ((((uVar13 < 400) && (uVar11 < 400)) &&
        (*(char *)(uVar11 * 400 + 0x21aec98 + uVar13) != '\0')) &&
       (((DAT_TileMapState.LogicLayer[iVar9] & 0x30) == 0 &&
        (0 < DAT_EntityState.entityArray[entityID].height)))) {
      DAT_EntityState.entityArray[entityID].nextEntityOnThisTileByID =
           DAT_TileMapState.EntityLayer[iVar9];
      DAT_TileMapState.EntityLayer[iVar9] = (short)entityID;
      return 1;
    }
    DAT_EntityState.entityArray[entityID].tile = 0;
    return 0;
  }
  if (((399 < uVar13) || (399 < uVar11)) || (*(char *)(uVar11 * 400 + 0x21aec98 + uVar13) == '\0'))
  {
    DAT_EntityState.entityArray[entityID].logicalState = 3;
    return 0;
  }
  if ((DAT_TileMapState.LogicLayer[iVar9] & 0x30) != 0) {
    markEntityDestroyed(&DAT_EntityState,entityID);
    return 0;
  }
  _tile = iVar9 * 2;
  if ((int)(short)EVar3 - 10U < 6) {
    DAT_TileMapState.MiscDisplayLayer[iVar9] = DAT_TileMapState.MiscDisplayLayer[iVar9] | 0x1000;
    EVar3 = DAT_EntityState.entityArray[entityID].entityType;
    if ((EVar3 == ET_BRAZIER) || (EVar3 == ET_HEADS_ON_SPIKES)) {
      iVar10 = DAT_EntityState.entityArray[entityID].tile;
      if (DAT_TileMapState.BuildingLayer[iVar10] == 0) {
        if ((DAT_TileMapState.LogicLayer[iVar10] & 0x100U) != 0) {
          if (DAT_TileMapState.DamageLayer[iVar10] == 0) {
            DAT_EntityState.entityArray[entityID].height =
                 (ushort)DAT_TileMapState.HeightLayer[iVar10];
          }
          else {
            DAT_EntityState.entityArray[entityID].height =
                 DAT_TileMapState.HeightLayer[iVar10] + 0xf;
          }
          goto LAB_00408150;
        }
      }
      else {
        switch(DAT_BuildingsState.buildings[(short)DAT_TileMapState.BuildingLayer[iVar10]].
               buildingType) {
        case BT_STONEKEEP:
        case BT_STRONGHOLD:
        case BT_KEEPFOUR:
        case BT_KEEPFIVE:
        case BT_GATEHOUSELARGE:
        case BT_GATEHOUSESMALL:
        case BT_TOWER1:
        case BT_TOWER2:
        case BT_TOWER3:
        case BT_TOWER4:
        case BT_TOWER5:
          uVar11 = TileMapState::getTotalHeightAtTile(&DAT_TileMapState,iVar10);
          DAT_EntityState.entityArray[entityID].height = (short)uVar11;
          goto LAB_00408150;
        }
      }
      if (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) {
        Buildings::BuildingsState::getBuildingCost
                  (&DAT_BuildingsState,M_MAPPER_BRAZIER,(int *)&local_10,(int *)&local_4);
        piVar1 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].
                 startResources + 0xf;
        *piVar1 = *piVar1 + local_4;
      }
      markEntityDestroyed(&DAT_EntityState,entityID);
    }
    else {
      iVar10 = DAT_EntityState.entityArray[entityID].tile;
      uVar11 = DAT_TileMapState.LogicLayer[iVar10];
      if (uVar11 == 0) {
        if (DAT_TileMapState.BuildingLayer[iVar10] == 0) {
          markEntityDestroyed(&DAT_EntityState,entityID);
        }
      }
      else if (DAT_TileMapState.DamageLayer[iVar10] != 0) {
        if ((uVar11 & 0x400000) == 0) {
          if ((uVar11 & 0x200) == 0) {
            DAT_EntityState.entityArray[entityID].height =
                 (ushort)DAT_TileMapState.HeightLayer[iVar10];
          }
          else {
            DAT_EntityState.entityArray[entityID].height = DAT_TileMapState.HeightLayer[iVar10] + 10
            ;
          }
        }
        else {
          DAT_EntityState.entityArray[entityID].height = DAT_TileMapState.HeightLayer[iVar10] + 0x14
          ;
        }
      }
    }
    goto LAB_00408150;
  }
  uVar4 = DAT_TileMapState.UnitLayer[iVar9];
  if ((EVar3 != ET_ARROW_AND_DEFAULT) || (DAT_EntityState.entityArray[entityID].rng_2 != 2)) {
    if (((EVar3 == ET_COW_POISON_CLOUD) ||
        (((EVar3 == ET_TREBUCHET || (EVar3 == ET_CATAPULT)) || (EVar3 == ET_MANGONEL)))) ||
       (0x50 < DAT_EntityState.entityArray[entityID].velocityUnk)) {
      while (iVar10 = (int)(short)uVar4, iVar10 != 0) {
        if ((DAT_EntityState.entityArray[entityID].logicalState == 2) &&
           (BVar12 = Units::UnitsState::processEntityDamageToUnit(&DAT_UnitsState,iVar10,entityID,0)
           , BVar12 != FALSE)) {
          if (DAT_EntityState.entityArray[entityID].entityType != ET_COW_FLYING) {
            markEntityDestroyed(&DAT_EntityState,entityID);
            return 0;
          }
          uVar11 = TileMapState::returnSomeHeight(&DAT_TileMapState,iVar9,0);
          DAT_EntityState.entityArray[entityID].height = (short)uVar11;
          goto LAB_004079b4;
        }
        uVar4 = DAT_UnitsState.units[iVar10].nextUnitOnTheSameTile;
      }
    }
    EVar3 = DAT_EntityState.entityArray[entityID].entityType;
    if (((EVar3 == ET_TREBUCHET) || (EVar3 == ET_CATAPULT)) ||
       ((EVar3 == ET_MANGONEL || (0x50 < DAT_EntityState.entityArray[entityID].velocityUnk)))) {
      iVar10 = 1;
      do {
        uVar4 = DAT_TileMapState.UnitLayer
                [DAT_TileMapState.directionTranslationMatrix
                 [DAT_EntityState.entityArray[entityID].yPosition][iVar10] + iVar9];
        while (iVar16 = (int)(short)uVar4, iVar16 != 0) {
          if (((DAT_UnitsState.units[iVar16].field67_0x90 != 0) &&
              (DAT_EntityState.entityArray[entityID].logicalState == 2)) &&
             (BVar12 = Units::UnitsState::processEntityDamageToUnit
                                 (&DAT_UnitsState,iVar16,entityID,1), BVar12 != FALSE)) {
            markEntityDestroyed(local_10,entityID);
            return 0;
          }
          uVar4 = DAT_UnitsState.units[iVar16].nextUnitOnTheSameTile;
        }
        iVar10 = iVar10 + 2;
      } while (iVar10 < 8);
    }
  }
  if (DAT_EntityState.entityArray[entityID].entityType == ET_COW_POISON_CLOUD) {
    local_4 = TileMapState::getTotalHeightAtTile(&DAT_TileMapState,iVar9);
    iVar10 = 0;
    do {
      iVar16 = DAT_TileMapState.directionTranslationMatrix
               [DAT_EntityState.entityArray[entityID].yPosition][iVar10] + iVar9;
      uVar4 = DAT_TileMapState.UnitLayer[iVar16];
      while (iVar14 = (int)(short)uVar4, iVar14 != 0) {
        uVar11 = TileMapState::getTotalHeightAtTile(&DAT_TileMapState,iVar16);
        uVar13 = (int)(local_4 - uVar11) >> 0x1f;
        if (((int)((local_4 - uVar11 ^ uVar13) - uVar13) < 0x78) &&
           (DAT_EntityState.entityArray[entityID].logicalState == 2)) {
          Units::UnitsState::processEntityDamageToUnit(&DAT_UnitsState,iVar14,entityID,1);
        }
        uVar4 = DAT_UnitsState.units[iVar14].nextUnitOnTheSameTile;
      }
      iVar10 = iVar10 + 1;
    } while (iVar10 < 8);
    pPVar15 = DAT_EntityDefinedData.field55_0xd84;
    do {
      iVar10 = TileMapState::computeTileAlongAxisOffset
                         (&DAT_TileMapState,iVar9,pPVar15->xOffset,pPVar15->yOffset);
      uVar4 = DAT_TileMapState.UnitLayer[iVar10];
      while (iVar16 = (int)(short)uVar4, iVar16 != 0) {
        uVar11 = TileMapState::getTotalHeightAtTile(&DAT_TileMapState,iVar10);
        uVar13 = (int)(local_4 - uVar11) >> 0x1f;
        if (((int)((local_4 - uVar11 ^ uVar13) - uVar13) < 0x78) &&
           (DAT_EntityState.entityArray[entityID].logicalState == 2)) {
          Units::UnitsState::processEntityDamageToUnit(&DAT_UnitsState,iVar16,entityID,2);
        }
        uVar4 = DAT_UnitsState.units[iVar16].nextUnitOnTheSameTile;
      }
      pPVar15 = pPVar15 + 1;
    } while ((int)pPVar15 < 0x5b6e08);
  }
  if ((((DAT_EntityState.entityArray[entityID].entityType == ET_FIRE) &&
       (iVar10 = DAT_EntityState.entityArray[entityID].tile,
       (DAT_TileMapState.LogicLayer[iVar10] & 8) != 0)) &&
      (iVar10 = TileMapState::getPitchDitchIDForTile(&DAT_TileMapState,iVar10), iVar10 != 0)) &&
     (DAT_TileMapState.pitchDitches[iVar10].state == 1)) {
    Global::SetPlaceOnFire
              ((int)DAT_EntityState.entityArray[entityID].owner,
               DAT_TileMapState.pitchDitches[iVar10].x * 8,
               DAT_TileMapState.pitchDitches[iVar10].y * 8,
               (uint)DAT_TileMapState.HeightLayer[DAT_TileMapState.pitchDitches[iVar10].tile],3);
    DAT_TileMapState.pitchDitches[iVar10].state = 2;
  }
  uVar11 = TileMapState::returnSomeHeight(&DAT_TileMapState,iVar9,0);
  iVar10 = (int)*(short *)((int)DAT_TileMapState.BuildingLayer + _tile);
  if (((iVar10 != 0) &&
      ((iVar10 = (int)(short)DAT_BuildingsState.buildings[iVar10].buildingType, iVar10 == 0x3d ||
       (iVar10 - 0x4aU < 5)))) && ((DAT_EntityState.entityArray[entityID].rng_1 & 4) != 0)) {
    uVar11 = uVar11 + 0x14;
  }
  sVar8 = DAT_EntityState.entityArray[entityID].height;
  iVar10 = (int)sVar8;
  if ((int)uVar11 <= iVar10) goto LAB_00408150;
  EVar3 = DAT_EntityState.entityArray[entityID].entityType;
  if (EVar3 == 0x20) {
    if (((iVar10 < (int)(uint)DAT_TileMapState.DefaultHeightLayer[iVar9]) &&
        (DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround = 1,
        (DAT_TileMapState.LogicLayer[iVar9] & 0x10000100U) == 0)) &&
       (((int)(uint)DAT_TileMapState.DefaultHeightLayer[iVar9] <
         DAT_EntityState.entityArray[entityID].startingHeight_2 + 0x32 &&
        ((IgniteFireAtMiniTile_Convenience
                    ((int)DAT_EntityState.entityArray[entityID].owner,
                     (int)DAT_EntityState.entityArray[entityID].microX,
                     (int)DAT_EntityState.entityArray[entityID].microY,
                     DAT_TileMapState.HeightLayer[DAT_EntityState.entityArray[entityID].tile] - 8,2)
         , (DAT_TileMapState.LogicLayer[iVar9] & 8) != 0 &&
         (iVar10 = TileMapState::getPitchDitchIDForTile(&DAT_TileMapState,iVar9), iVar10 != 0))))))
    {
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_EntityState.entityArray[entityID].xPosition,
                 (int)DAT_EntityState.entityArray[entityID].yPosition,FX_IGNITE_PITCH);
      Global::SetPlaceOnFire
                ((int)DAT_EntityState.entityArray[entityID].owner,
                 DAT_TileMapState.pitchDitches[iVar10].x * 8,
                 DAT_TileMapState.pitchDitches[iVar10].y * 8,
                 (uint)DAT_TileMapState.HeightLayer[DAT_TileMapState.pitchDitches[iVar10].tile],3);
      if (DAT_TileMapState.pitchDitches[iVar10].state == 1) {
        DAT_TileMapState.pitchDitches[iVar10].state = 2;
      }
    }
    goto LAB_00408150;
  }
  if (EVar3 == 0x1b) {
    if (((iVar10 <= (int)(uint)DAT_TileMapState.DefaultHeightLayer[iVar9]) &&
        (DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround = 1,
        (DAT_TileMapState.LogicLayer[iVar9] & 0x40100001U) != 0)) &&
       (DAT_EntityState.entityArray[entityID].unitID_OR_seaGullID == 0)) {
      iVar16 = (int)DAT_EntityState.entityArray[entityID].microY;
      iVar14 = (int)DAT_EntityState.entityArray[entityID].microX;
      iVar10 = DAT_TileMapState.HeightLayer[DAT_EntityState.entityArray[entityID].tile] + 2;
      spawnProjectileEntity(local_10,1,0,0,iVar14,iVar16,iVar10,iVar14,iVar16,iVar10,0x1f,0);
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_EntityState.entityArray[entityID].xPosition,
                 (int)DAT_EntityState.entityArray[entityID].yPosition,FX_MED_PLOP);
    }
    goto LAB_00408150;
  }
  if (EVar3 == 8) {
    uVar11 = iVar10 - DAT_EntityState.entityArray[entityID].targetZ;
    uVar13 = (int)uVar11 >> 0x1f;
    if (((int)((uVar11 ^ uVar13) - uVar13) < 0x14) || (sVar8 < 9)) {
      DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround = 1;
    }
    goto LAB_00408150;
  }
  if (((EVar3 == ET_ARROW_AND_DEFAULT) || (EVar3 == ET_CROSSBOWARROW)) ||
     ((EVar3 == ET_BALLISTA || ((EVar3 == ET_SLINGER || (EVar3 == ET_FIRETHROWER)))))) {
    if (DAT_EntityState.entityArray[entityID].rng_2 == 2) {
      iVar10 = 0;
      do {
        iVar16 = DAT_TileMapState.directionTranslationMatrix
                 [DAT_EntityState.entityArray[entityID].yPosition][iVar10] + iVar9;
        if (((DAT_TileMapState.LogicLayer[iVar16] & 8) != 0) &&
           (iVar16 = TileMapState::getPitchDitchIDForTile(&DAT_TileMapState,iVar16), iVar16 != 0))
        goto LAB_00407f73;
        iVar10 = iVar10 + 1;
      } while (iVar10 < 8);
    }
    iVar10 = (int)*(short *)((int)DAT_TileMapState.BuildingLayer + _tile);
    if ((int)DAT_EntityState.entityArray[entityID].travelledDistance <=
        (int)DAT_EntityState.entityArray[entityID].field58_0x8c / 2) goto LAB_00408150;
    uVar11 = DAT_TileMapState.LogicLayer[iVar9];
    if ((uVar11 & 0x40100001) != 0) {
      iVar16 = (int)DAT_EntityState.entityArray[entityID].microY;
      iVar14 = (int)DAT_EntityState.entityArray[entityID].microX;
      iVar10 = DAT_TileMapState.HeightLayer[DAT_EntityState.entityArray[entityID].tile] + 2;
      spawnProjectileEntity(local_10,1,0,0,iVar14,iVar16,iVar10,iVar14,iVar16,iVar10,0x1f,0);
      sVar8 = DAT_EntityState.entityArray[entityID].yPosition;
      sVar5 = DAT_EntityState.entityArray[entityID].xPosition;
      DAT_EntityState.entityArray[entityID].logicalState = 3;
      local_c = 0;
      Audio::SFX::SFXState::playSFXAtLocation(&DAT_SFXState,(int)sVar5,(int)sVar8,FX_LITTLE_PLOP);
      goto LAB_00408150;
    }
    if (((uVar11 & 0x10000100) == 0) &&
       ((iVar10 == 0 ||
        ((((BVar6 = DAT_BuildingsState.buildings[iVar10].buildingType, BVar6 != BT_STONEKEEP &&
           (BVar6 != BT_STRONGHOLD)) && (BVar6 != BT_KEEPFOUR)) && (BVar6 != BT_KEEPFIVE)))))) {
      if ((uVar11 & 8) == 0) {
        if (iVar10 == 0) {
          DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround = 0x28;
        }
        else {
          iVar16 = (int)DAT_EntityState.entityArray[entityID].unitID_OR_seaGullID;
                    /* if buildingtype is a tower (1 to 5) */
          BVar6 = DAT_BuildingsState.buildings[iVar10].buildingType;
          if (((0x49 < (short)BVar6) && ((short)BVar6 < 0x4f)) ||
             ((DAT_BuildingsState.buildings[iVar10].currentHealth == 0 ||
              ((uVar11 & 0xf000000) != 0)))) goto LAB_00408150;
          if (DAT_UnitsState.units[iVar16].unitType == UT_S_FBALLISTA) {
            TileMapState::processDamageToBuilding
                      (&DAT_TileMapState,iVar9,(int)DAT_EntityState.entityArray[entityID].xPosition,
                       (int)DAT_EntityState.entityArray[entityID].yPosition,10,0,
                       (int)DAT_EntityState.entityArray[entityID].owner,FALSE,iVar16);
            iVar10 = TileMapState::getNonFarmFieldBuildingHealthAtTileOr1000
                               (&DAT_TileMapState,iVar9);
            if (iVar10 < 0x32) {
              Global::SetPlaceOnFire
                        ((int)DAT_EntityState.entityArray[entityID].owner,
                         DAT_EntityState.entityArray[entityID].xPosition * 8,
                         DAT_EntityState.entityArray[entityID].yPosition * 8,
                         (uint)DAT_TileMapState.HeightLayer
                               [DAT_EntityState.entityArray[entityID].tile],3);
              DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround = 1;
              goto LAB_00408148;
            }
          }
          else {
            if (DAT_EntityState.entityArray[entityID].entityType == ET_BALLISTA) {
              sVar8 = DAT_EntityState.entityArray[entityID].owner;
              sVar5 = DAT_EntityState.entityArray[entityID].yPosition;
              sVar7 = DAT_EntityState.entityArray[entityID].xPosition;
              iVar10 = 2;
            }
            else {
              sVar8 = DAT_EntityState.entityArray[entityID].owner;
              sVar5 = DAT_EntityState.entityArray[entityID].yPosition;
              sVar7 = DAT_EntityState.entityArray[entityID].xPosition;
              iVar10 = 1;
            }
            TileMapState::processDamageToBuilding
                      (&DAT_TileMapState,iVar9,(int)sVar7,(int)sVar5,iVar10,0,(int)sVar8,FALSE,
                       iVar16);
          }
          DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround = 1;
        }
      }
      else {
        if ((DAT_EntityState.entityArray[entityID].rng_2 == 2) &&
           (iVar16 = TileMapState::getPitchDitchIDForTile(&DAT_TileMapState,iVar9), iVar16 != 0)) {
LAB_00407f73:
          Audio::SFX::SFXState::playSFXAtLocation
                    (&DAT_SFXState,(int)DAT_EntityState.entityArray[entityID].xPosition,
                     (int)DAT_EntityState.entityArray[entityID].yPosition,FX_IGNITE_PITCH);
          Global::SetPlaceOnFire
                    ((int)DAT_EntityState.entityArray[entityID].owner,
                     DAT_TileMapState.pitchDitches[iVar16].x * 8,
                     DAT_TileMapState.pitchDitches[iVar16].y * 8,
                     (uint)DAT_TileMapState.HeightLayer[DAT_TileMapState.pitchDitches[iVar16].tile],
                     3);
          if (DAT_TileMapState.pitchDitches[iVar16].state == 1) {
            DAT_TileMapState.pitchDitches[iVar16].state = 2;
          }
        }
        DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround = 1;
      }
    }
    else {
      if (((DAT_EntityState.entityArray[entityID].field45_0x6a < 3) &&
          (DAT_EntityState.entityArray[entityID].startingAngle < 0)) ||
         ((DAT_EntityState.entityArray[entityID].hasDoneEffectUnk != 0 ||
          (0 < DAT_EntityState.entityArray[entityID].field80_0xba)))) goto LAB_00408150;
      handleProjectileWallBounce(local_10,entityID);
    }
  }
  else if (((EVar3 == ET_TREBUCHET) || (EVar3 == ET_CATAPULT)) || (EVar3 == ET_MANGONEL)) {
    DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround = 1;
    uVar11 = DAT_TileMapState.LogicLayer[iVar9];
    iVar16 = 10;
    local_4 = uVar11 & 0x40100001;
    iVar10 = 10;
    if (local_4 != 0) {
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_EntityState.entityArray[entityID].xPosition,
                 (int)DAT_EntityState.entityArray[entityID].yPosition,FX_ROCK_SPLASH);
    }
    uVar13 = uVar11 & 0x100;
    if (((uVar13 == 0) && ((uVar11 & 0x10000400) == 0)) &&
       (*(short *)((int)DAT_TileMapState.BuildingLayer + _tile) == 0)) {
      psVar2 = &DAT_UnitsState.units[DAT_EntityState.entityArray[entityID].unitID_OR_seaGullID].
                field101_0xd2;
      *psVar2 = *psVar2 + 1;
      if ((uVar11 & 0x4a5014b1) == 0) {
        local_4 = uVar13;
        Audio::SFX::SFXState::playSFXAtLocation
                  (&DAT_SFXState,(int)DAT_EntityState.entityArray[entityID].xPosition,
                   (int)DAT_EntityState.entityArray[entityID].yPosition,FX_ROCK_HIT_GROUND);
        uVar11 = DAT_EntityState.entityArray[entityID].rng_1 & 0x80000007;
        DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround = 0x28;
        local_c = 0;
        if ((int)uVar11 < 0) {
          uVar11 = (uVar11 - 1 | 0xfffffff8) + 1;
        }
        if (uVar11 != 0xfffffffb && -1 < (int)(uVar11 + 5)) {
          do {
            iVar10 = (int)DAT_EntityState.entityArray[entityID].microY;
            iVar16 = (int)DAT_EntityState.entityArray[entityID].microX;
            spawnProjectileEntity
                      (local_10,2,0,0,iVar16,iVar10,
                       DAT_TileMapState.HeightLayer[DAT_EntityState.entityArray[entityID].tile] + 2,
                       (int)SEC_RNG.currentNumber2 % 0x50 + -0x28 + iVar16,
                       ((int)SEC_RNG.currentNumber2 >> 8) % 0x50 + -0x28 + iVar10,8,0x1b,0);
            local_c = local_c + 1;
            uVar11 = DAT_EntityState.entityArray[entityID].rng_1 & 0x80000007;
            if ((int)uVar11 < 0) {
              uVar11 = (uVar11 - 1 | 0xfffffff8) + 1;
            }
          } while (local_c < (int)(uVar11 + 5));
        }
      }
      else if (local_4 != 0) {
        uVar11 = DAT_EntityState.entityArray[entityID].rng_1 & 0x8000000f;
        local_c = 0;
        if ((int)uVar11 < 0) {
          uVar11 = (uVar11 - 1 | 0xfffffff0) + 1;
        }
        local_4 = 0;
        if (uVar11 != 0xfffffff6 && -1 < (int)(uVar11 + 10)) {
          do {
            iVar10 = (int)DAT_EntityState.entityArray[entityID].microY;
            iVar16 = (int)DAT_EntityState.entityArray[entityID].microX;
            spawnProjectileEntity
                      (local_10,1,0,0,iVar16,iVar10,
                       DAT_TileMapState.HeightLayer[DAT_EntityState.entityArray[entityID].tile] + 2,
                       (int)SEC_RNG.currentNumber2 % 0x50 + -0x28 + iVar16,
                       ((int)SEC_RNG.currentNumber2 >> 8) % 0x50 + -0x28 + iVar10,8,0x1b,0);
            local_c = local_c + 1;
            uVar11 = DAT_EntityState.entityArray[entityID].rng_1 & 0x8000000f;
            if ((int)uVar11 < 0) {
              uVar11 = (uVar11 - 1 | 0xfffffff0) + 1;
            }
          } while (local_c < (int)(uVar11 + 10));
        }
        iVar16 = (int)DAT_EntityState.entityArray[entityID].microY;
        iVar14 = (int)DAT_EntityState.entityArray[entityID].microX;
        iVar10 = DAT_TileMapState.HeightLayer[DAT_EntityState.entityArray[entityID].tile] + 2;
        spawnProjectileEntity(local_10,0,0,0,iVar14,iVar16,iVar10,iVar14,iVar16,iVar10,0x1f,0);
      }
    }
    else {
      local_4 = uVar13;
      spawnProjectileImpactDebris(local_10,entityID);
      EVar3 = DAT_EntityState.entityArray[entityID].entityType;
      if (EVar3 == ET_TREBUCHET) {
        iVar16 = 0x3c;
        iVar10 = 0x1e;
      }
      else if (EVar3 == ET_CATAPULT) {
        iVar16 = 0x14;
      }
      else if (EVar3 == ET_MANGONEL) {
        iVar16 = 5;
        iVar10 = 0;
      }
      iVar14 = (int)*(short *)((int)DAT_TileMapState.BuildingLayer + _tile);
      if (iVar14 == 0) {
        if ((local_4 != 0) &&
           (DAT_GameState.mapAndTime.playerTeams[DAT_EntityState.entityArray[entityID].owner] ==
            DAT_GameState.mapAndTime.playerTeams[(DAT_TileMapState.WallOwnerLayer[iVar9] & 7) + 1]))
        {
          iVar16 = 0;
          iVar10 = 0;
        }
      }
      else if (DAT_GameState.mapAndTime.playerTeams[DAT_BuildingsState.buildings[iVar14].owner] ==
               DAT_GameState.mapAndTime.playerTeams[DAT_EntityState.entityArray[entityID].owner]) {
        iVar16 = 0;
        iVar10 = 0;
      }
      if (EVar3 == ET_MANGONEL) {
        TileMapState::processDamageToBuilding
                  (&DAT_TileMapState,iVar9,(int)DAT_EntityState.entityArray[entityID].xPosition,
                   (int)DAT_EntityState.entityArray[entityID].yPosition,iVar16,0,
                   -(int)DAT_EntityState.entityArray[entityID].owner,FALSE,
                   (int)DAT_EntityState.entityArray[entityID].unitID_OR_seaGullID);
        TileMapState::processEntityDamageToBuildingCollateral
                  (&DAT_TileMapState,iVar9,(int)DAT_EntityState.entityArray[entityID].xPosition,
                   (int)DAT_EntityState.entityArray[entityID].yPosition,iVar10,
                   -(int)DAT_EntityState.entityArray[entityID].owner,0,
                   (int)DAT_EntityState.entityArray[entityID].unitID_OR_seaGullID);
      }
      else {
        TileMapState::processDamageToBuilding
                  (&DAT_TileMapState,iVar9,(int)DAT_EntityState.entityArray[entityID].xPosition,
                   (int)DAT_EntityState.entityArray[entityID].yPosition,iVar16,0,
                   (int)DAT_EntityState.entityArray[entityID].owner,FALSE,
                   (int)DAT_EntityState.entityArray[entityID].unitID_OR_seaGullID);
        TileMapState::processEntityDamageToBuildingCollateralThunk
                  (&DAT_TileMapState,iVar9,(int)DAT_EntityState.entityArray[entityID].xPosition,
                   (int)DAT_EntityState.entityArray[entityID].yPosition,iVar10,
                   (int)DAT_EntityState.entityArray[entityID].owner,0);
      }
                    /* woodhit_02.wav ? */
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_EntityState.entityArray[entityID].xPosition,
                 (int)DAT_EntityState.entityArray[entityID].yPosition,FX_ROCK_HIT_WALL);
    }
  }
  else {
    if (EVar3 != ET_COW_FLYING) goto LAB_00408150;
LAB_004079b4:
    if (DAT_EntityState.entityArray[entityID].hasDoneEffectUnk == 0) {
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_EntityState.entityArray[entityID].xPosition,
                 (int)DAT_EntityState.entityArray[entityID].yPosition,FX_COW_SPLAT);
      DAT_EntityState.entityArray[entityID].hasDoneEffectUnk = 1;
      if ((DAT_TileMapState.LogicLayer[iVar9] & 0x401000b1U) == 0) {
        DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround = 0x28;
        DAT_GameCore.cowPoisonTrackerUnk = DAT_GameCore.cowPoisonTrackerUnk + 500;
        iVar10 = (int)SEC_RNG.currentNumber2 % 5 + -2;
        if (iVar10 < 8) {
          iVar10 = 8 - iVar10;
          do {
            spawnProjectileEntity
                      (&DAT_EntityState,0,(int)DAT_EntityState.entityArray[entityID].owner,0,
                       (int)DAT_EntityState.entityArray[entityID].microX,
                       (int)DAT_EntityState.entityArray[entityID].microY,
                       (int)DAT_EntityState.entityArray[entityID].height,0,0,0,ET_COW_POISON_CLOUD,0
                      );
            iVar10 = iVar10 + -1;
          } while (iVar10 != 0);
        }
        Audio::SFX::SFXState::playSFXAtLocation
                  (&DAT_SFXState,(int)DAT_EntityState.entityArray[entityID].xPosition,
                   (int)DAT_EntityState.entityArray[entityID].yPosition,FX_FLIES);
      }
      else {
        DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround = 1;
      }
    }
  }
LAB_00408148:
  local_c = 0;
LAB_00408150:
  if (entityID != 0) {
    if (entityID < 0x19) {
      DAT_EntityState.entityArray[entityID].nextEntityOnThisTileByID =
           (ushort)(byte)DAT_TileMapState.EntityLayerLT25[iVar9];
      DAT_TileMapState.EntityLayerLT25[iVar9] = (char)entityID;
      return local_c;
    }
    DAT_EntityState.entityArray[entityID].nextEntityOnThisTileByID =
         *(short *)((int)DAT_TileMapState.EntityLayer + _tile);
    *(short *)((int)DAT_TileMapState.EntityLayer + _tile) = (short)entityID;
  }
  return local_c;
}



// ================= setRandomShootLocation @ 005330a0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::UnitsState::setRandomShootLocation
          (UnitsState *this,int unitID,int microX,int microY,int z)

{
  UnitTypeShort UVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  
  iVar2 = unitID;
  iVar3 = (int)DAT_UnitsState.units[unitID].microXPosition;
  if (iVar3 < microX) {
    iVar3 = microX - iVar3;
  }
  else {
    iVar3 = iVar3 - microX;
  }
  iVar4 = (int)DAT_UnitsState.units[unitID].microYPosition;
  if (iVar4 < microY) {
                    /* unitID becomes _microYDiff */
    unitID = microY - iVar4;
  }
  else {
    unitID = iVar4 - microY;
  }
  if (unitID <= iVar3) {
    unitID = iVar3;
  }
  uVar8 = (uint)SEC_RNG.currentNumber2;
  Random::RNG::nextRandomNumber2(&SEC_RNG);
  UVar1 = DAT_UnitsState.units[iVar2].unitType;
  uVar5 = (int)uVar8 >> 0x1f;
  if (UVar1 == UT_S_TREBUCHET) {
    iVar6 = 0;
    if ((uVar8 & 3) == 0) {
      iVar6 = (int)uVar8 % 0x60 + -0x30;
    }
    iVar3 = uVar8 + (uVar5 & 0xff);
    iVar3 = (int)(CONCAT44(iVar3 >> 0x1f,iVar3 >> 8) % 0x60) + -0x30;
    uVar5 = (int)(uVar8 + (uVar5 & 0x7f)) >> 7 & 0x8000001f;
    if ((int)uVar5 < 0) {
      uVar5 = (uVar5 - 1 | 0xffffffe0) + 1;
    }
    z = z + -0x10 + uVar5;
  }
  else if (UVar1 == UT_S_CATAPULT) {
    uVar7 = uVar8 & 0x8000007f;
    if ((int)uVar7 < 0) {
      uVar7 = (uVar7 - 1 | 0xffffff80) + 1;
    }
    iVar3 = uVar8 + (uVar5 & 0xff);
    iVar6 = uVar7 - 0x60;
    iVar3 = (int)(CONCAT44(iVar3 >> 0x1f,iVar3 >> 8) % 0x60) + -0x30;
    uVar5 = (int)(uVar8 + (uVar5 & 0x7f)) >> 7 & 0x8000003f;
    if ((int)uVar5 < 0) {
      uVar5 = (uVar5 - 1 | 0xffffffc0) + 1;
    }
    z = z + -0x30 + uVar5;
  }
  else if (UVar1 == UT_S_MANGONEL) {
    iVar6 = (int)uVar8 % 0xe0 + -0x70;
    uVar7 = (int)(uVar8 + (uVar5 & 0xff)) >> 8 & 0x8000007f;
    if ((int)uVar7 < 0) {
      uVar7 = (uVar7 - 1 | 0xffffff80) + 1;
    }
    iVar3 = uVar7 - 0x40;
    uVar5 = (int)(uVar8 + (uVar5 & 0x7f)) >> 7 & 0x8000007f;
    if ((int)uVar5 < 0) {
      uVar5 = (uVar5 - 1 | 0xffffff80) + 1;
    }
    z = z + -0x40 + uVar5;
  }
  else if (UVar1 == UT_S_BALLISTA) {
    if (DAT_UnitsState.units[iVar2].targetingType == UIT_ATTACK_LAND) {
      uVar7 = uVar8 & 0x8000001f;
      if ((int)uVar7 < 0) {
        uVar7 = (uVar7 - 1 | 0xffffffe0) + 1;
      }
      iVar3 = uVar8 + (uVar5 & 0xff);
      iVar6 = uVar7 - 0x18;
      iVar4 = uVar8 + (uVar5 & 0x7f);
      iVar3 = (int)(CONCAT44(iVar3 >> 0x1f,iVar3 >> 8) % 0x28) + -0x14;
      z = z + -0x14 + (int)(CONCAT44(iVar4 >> 0x1f,iVar4 >> 7) % 0x28);
    }
    else {
      iVar6 = 0;
      iVar3 = 0;
    }
  }
  else if ((UVar1 == UT_S_FBALLISTA) &&
          (DAT_UnitsState.units[iVar2].targetingType != UIT_ATTACK_LAND)) {
    iVar4 = uVar8 + (uVar5 & 0x7f);
    iVar6 = 0;
    iVar3 = 0;
    z = z + (int)(CONCAT44(iVar4 >> 0x1f,iVar4 >> 7) % 0x1e);
  }
  else {
    iVar3 = uVar8 + (uVar5 & 0xff);
    iVar6 = (int)uVar8 % 0x60 + -0x30;
    iVar4 = uVar8 + (uVar5 & 0x7f);
    iVar3 = (int)(CONCAT44(iVar3 >> 0x1f,iVar3 >> 8) % 0x50) + -0x28;
    z = z + -0x28 + (int)(CONCAT44(iVar4 >> 0x1f,iVar4 >> 7) % 0x50);
  }
  if (z < 8) {
    z = 8;
  }
  else if (0xfa < z) {
    z = 0xfa;
  }
  if (unitID / 2 < iVar6) {
    iVar6 = iVar6 / 2;
    iVar3 = iVar3 / 2;
  }
  if (unitID < iVar6) {
    iVar6 = -iVar6;
  }
  switch(DAT_UnitsState.units[iVar2].facingDirection) {
  case 0:
    microY = microY + iVar6;
    microX = microX + iVar3;
    break;
  case 1:
    iVar4 = (int)(iVar3 * 3 + (iVar3 * 3 >> 0x1f & 3U)) >> 2;
    iVar3 = (int)(iVar6 * 3 + (iVar6 * 3 >> 0x1f & 3U)) >> 2;
    microX = microX + (iVar4 - iVar3);
    microY = microY + iVar3 + iVar4;
    break;
  case 2:
    microX = microX - iVar6;
    goto LAB_0053344e;
  case 3:
    iVar3 = (int)(iVar3 * 3 + (iVar3 * 3 >> 0x1f & 3U)) >> 2;
    iVar4 = -((int)(iVar6 * 3 + (iVar6 * 3 >> 0x1f & 3U)) >> 2) - iVar3;
    goto LAB_00533440;
  case 4:
    microY = microY - iVar6;
    microX = microX + iVar3;
    break;
  case 5:
    iVar3 = (int)(iVar3 * 3 + (iVar3 * 3 >> 0x1f & 3U)) >> 2;
    iVar4 = ((int)(iVar6 * 3 + (iVar6 * 3 >> 0x1f & 3U)) >> 2) - iVar3;
    iVar3 = -iVar3;
LAB_00533440:
    microX = microX + iVar4;
    iVar3 = iVar3 - ((int)(iVar6 * 3 + (iVar6 * 3 >> 0x1f & 3U)) >> 2);
    goto LAB_0053344e;
  case 6:
    microX = microX + iVar6;
LAB_0053344e:
    microY = microY + iVar3;
    break;
  case 7:
    iVar4 = (int)(iVar3 * 3 + (iVar3 * 3 >> 0x1f & 3U)) >> 2;
    iVar3 = (int)(iVar6 * 3 + (iVar6 * 3 >> 0x1f & 3U)) >> 2;
    microX = microX + iVar3 + iVar4;
    microY = microY + (iVar3 - iVar4);
  }
  DAT_UnitsState.units[iVar2].shootTargetZ = (short)z;
  DAT_UnitsState.units[iVar2].shootTargetMicroY = (short)microY;
  DAT_UnitsState.units[iVar2].shootTargetMicroX = (short)microX;
  return;
}



