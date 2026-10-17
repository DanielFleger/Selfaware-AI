// ================= UpdateArrowEntity @ 00401ba0 =================

/* decompilerscript: committed: 2025-01-30 21:56:35.138000 */

void _HoldStrong::Map::Entities::UpdateArrowEntity(void)

{
  short sVar1;
  uint uVar2;
  
  uVar2 = DAT_CurrentEntityID;
  DAT_EntityState.entityArray[DAT_CurrentEntityID].graphicType2 =
       DAT_EntityState.entityArray[DAT_CurrentEntityID].field45_0x6a * 0x10 +
       (int)DAT_EntityState.entityArray[DAT_CurrentEntityID].field12_0x1c +
       (int)DAT_EntityState.entityArray[DAT_CurrentEntityID].graphicType2RelatedOffset;
  sVar1 = DAT_EntityState.entityArray[uVar2].someCounter_OR_hitGround;
  if (sVar1 != 0) {
    DAT_EntityState.entityArray[uVar2].someCounter_OR_hitGround = sVar1 + -1;
    if (DAT_EntityState.entityArray[uVar2].rng_2 != 0) {
      DAT_EntityState.entityArray[uVar2].someCounter_OR_hitGround = 0;
    }
    if (DAT_EntityState.entityArray[uVar2].someCounter_OR_hitGround < 1) {
      DAT_EntityState.entityArray[uVar2].logicalState = 7;
    }
  }
  if (DAT_EntityState.entityArray[uVar2].orientation == 0x4c) {
    DAT_EntityState.entityArray[uVar2].orientation = 0x3c;
    DAT_EntityState.entityArray[uVar2].logicalState = 7;
  }
  return;
}



// ================= updateProjectileHeightAndCollision @ 004081e0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Entities::EntityState::updateProjectileHeightAndCollision
          (EntityState *this,uint entityID,undefined4 param_2,int param_3,int param_4)

{
  short sVar1;
  short extraout_DX;
  
  sVar1 = DAT_EntityState.entityArray[entityID].startingHeight + (short)param_2;
  DAT_EntityState.entityArray[entityID].height = sVar1;
  if ((sVar1 < 3) && (param_4 == 0)) {
    doSomethingWithOtherEntitiesOnTile(&DAT_EntityState,entityID);
    processEntityHitBuildingOrUnit(&DAT_EntityState,entityID);
  }
  if (10000 < DAT_EntityState.entityArray[entityID].height) {
    markEntityDestroyed(&DAT_EntityState,entityID);
    return;
  }
  sVar1 = angleToRotationFrameIndex(param_3);
  DAT_EntityState.entityArray[entityID].field45_0x6a = sVar1;
  DAT_EntityState.entityArray[entityID].height_2 = extraout_DX;
  return;
}



// ================= moveProjectileEntity @ 004084a0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000
   
   Note that Ghidra is bad at x87 extended precision instructions.
   This function likely does:
   
   float dx = vCos * speed * 0.25f;
   float dy = vSin * speed * 0.25f;
   
   float t = vSin - gravityAccum;
   
   float slope =
       (height - (4.906f * t - t * t * velocity)) /
       (distance - dx * t);
   
   float angle = atan(slope) * 180.0f / PI; */

BOOLEnum __thiscall
_HoldStrong::Map::Entities::EntityState::moveProjectileEntity(EntityState *this,int entityID)

{
  short *psVar1;
  float fVar2;
  float fVar3;
  short sVar4;
  EntityTypeShort EVar5;
  short sVar6;
  int entityID_00;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  float10 fVar11;
  float10 fVar12;
  float10 fVar13;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 extraout_ST1;
  float10 extraout_ST1_00;
  float10 fVar14;
  int iVar15;
  int local_10;
  
  entityID_00 = entityID;
  fVar2 = (float)DAT_EntityState.entityArray[entityID].speedUnk;
  fVar3 = DAT_EntityState.entityArray[entityID].vCos;
  fVar11 = (float10)DAT_EntityState.entityArray[entityID].vSin;
  iVar10 = (int)DAT_EntityState.entityArray[entityID].height -
           (int)DAT_EntityState.entityArray[entityID].startingHeight;
  local_10 = 0;
  if (DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround != 0) {
    return FALSE;
  }
  if (DAT_EntityState.entityArray[entityID].field50_0x74 == 0) {
    DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround = 0x28;
  }
  fVar12 = (float10)fVar3 * (float10)fVar2;
                    /* 9.812 / 2 (gravity!) */
  fVar13 = (float10)GRAVITY_DIV_2;
  iVar7 = HoldStrong_lib::__ftol2(fVar12 * (float10)DOUBLE_0059e890);
  fVar14 = extraout_ST1;
  iVar8 = HoldStrong_lib::__ftol2(extraout_ST0 + extraout_ST0);
  if ((float10)0 == fVar11) {
    fVar11 = (float10)(int)DAT_EntityState.entityArray[entityID].startingAngle;
  }
  else {
    fVar11 = fVar11 - (float10)DAT_EntityState.entityArray[entityID].
                               _elapsedTimeOrGravityAccumulator;
    fVar11 = HoldStrong_lib::_math_atan_FUN_0057ee10
                       (((extraout_ST0_00 - (fVar13 * fVar11 - fVar11 * fVar11 * extraout_ST1_00)) /
                        (fVar14 - fVar12 * fVar11)) * (float10)DOUBLE_0059e880);
    fVar11 = (fVar11 * (float10)DOUBLE_0059e850) / (float10)DOUBLE_0059e848;
  }
  iVar9 = HoldStrong_lib::__ftol2(fVar11);
  fVar2 = DAT_EntityState.entityArray[entityID]._elapsedTimeOrGravityAccumulator;
  fVar3 = (float)DAT_EntityState.entityArray[entityID].speedUnk;
  DAT_EntityState.entityArray[entityID].graphicRotationUnk = (word)iVar9;
  iVar9 = iVar7 - DAT_EntityState.entityArray[entityID].travelledDistance;
  DAT_EntityState.entityArray[entityID].speedUnk = (int)(fVar2 + fVar3);
  if (iVar9 != 0) {
    local_10 = (iVar8 - iVar10) / iVar9;
  }
  sVar4 = DAT_EntityState.entityArray[entityID].travelledDistance;
  while (sVar4 < iVar7) {
    psVar1 = &DAT_EntityState.entityArray[entityID].travelledDistance;
    *psVar1 = *psVar1 + 1;
    psVar1 = &DAT_EntityState.entityArray[entityID].field80_0xba;
    *psVar1 = *psVar1 + -1;
    if (entityID != 0) {
      doSomethingWithOtherEntitiesOnTile(&DAT_EntityState,entityID);
    }
    updateEntityMicroMovement(&DAT_EntityState,entityID);
    if ((DAT_EntityDefinedData.DAT_EntityArrayCurveTypeForProjectileType
         [(short)DAT_EntityState.entityArray[entityID].entityType] != 9) &&
       (DAT_EntityDefinedData.DAT_EntityArrayCurveTypeForProjectileType
        [(short)DAT_EntityState.entityArray[entityID].entityType] != 10)) {
      iVar10 = iVar10 + local_10;
      iVar15 = 1;
      iVar9 = HoldStrong_lib::__ftol2((float10)(double)fVar11);
      updateProjectileHeightAndCollision(&DAT_EntityState,entityID,iVar10,iVar9,iVar15);
    }
    iVar9 = processEntityHitBuildingOrUnit(&DAT_EntityState,entityID);
    if (iVar9 == 0) {
      calculateEntityDrawOffset(&DAT_EntityState,entityID);
      return TRUE;
    }
    calculateEntityDrawOffset(&DAT_EntityState,entityID);
    if (DAT_EntityState.entityArray[entityID].someCounter_OR_hitGround != 0) break;
    sVar4 = DAT_EntityState.entityArray[entityID].travelledDistance;
  }
  EVar5 = DAT_EntityState.entityArray[entityID].entityType;
  entityID._0_2_ = (short)iVar7;
  DAT_EntityState.entityArray[entityID_00].travelledDistance = (short)entityID;
  if (DAT_EntityDefinedData.DAT_EntityArrayCurveTypeForProjectileType[(short)EVar5] == 9) {
    sVar4 = DAT_EntityState.entityArray[entityID_00].height;
    sVar6 = DAT_EntityState.entityArray[entityID_00].targetZ;
    if (sVar4 < sVar6) {
      DAT_EntityState.entityArray[entityID_00].height = sVar4 + 1;
      return TRUE;
    }
    if ((sVar6 < sVar4) &&
       (DAT_EntityState.entityArray[entityID_00].height = sVar4 + -8, (short)(sVar4 + -8) < 1)) {
      iVar10 = (int)DAT_EntityState.entityArray[entityID_00].microY;
      iVar7 = (int)DAT_EntityState.entityArray[entityID_00].microX;
      DAT_EntityState.entityArray[entityID_00].someMicroY = 0;
      DAT_EntityState.entityArray[entityID_00].someMicroX = 0;
      DAT_EntityState.entityArray[entityID_00].height = 0;
      spawnProjectileEntity(&DAT_EntityState,0,0,0,iVar7,iVar10,0,iVar7,iVar10,0,0x1f,0);
      Audio::SFX::SFXState::playSFXAtLocation
                (&DAT_SFXState,(int)DAT_EntityState.entityArray[entityID_00].xPosition,
                 (int)DAT_EntityState.entityArray[entityID_00].yPosition,FX_GULL_DIVE);
      return TRUE;
    }
  }
  else {
    if (DAT_EntityDefinedData.DAT_EntityArrayCurveTypeForProjectileType[(short)EVar5] == 10) {
      psVar1 = &DAT_EntityState.entityArray[entityID_00].height;
      *psVar1 = *psVar1 + 1;
      return TRUE;
    }
    iVar7 = 0;
    iVar10 = HoldStrong_lib::__ftol2((float10)(double)fVar11);
    updateProjectileHeightAndCollision(&DAT_EntityState,entityID_00,iVar8,iVar10,iVar7);
  }
  return TRUE;
}



// ================= shootProjectile @ 00532700 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::UnitsState::shootProjectile
          (UnitsState *this,int unitID,EntityType projectileType,int targetX,int targetY,
          int targetZUnk)

{
  short sVar1;
  short sVar2;
  short sVar3;
  int iVar4;
  int playerID1;
  int iVar5;
  int *piVar6;
  int iVar7;
  uint ownerColorUnk;
  int iVar8;
  
  iVar4 = 0;
  iVar5 = 0;
  if (projectileType == ET_TREBUCHET) {
    piVar6 = DAT_UnitsState.unitCountOfSelection + unitID * 0x124 + -9;
    iVar8 = 0;
    if (DAT_UnitsState.units[unitID].field260_0x3b0 == 0) {
      projectileType = ET_TREBUCHET;
      iVar7 = DAT_UnitsState.units[unitID].buildingHeight + 0x82 +
              (int)DAT_UnitsState.units[unitID].terrainOrClimbHeight;
      iVar5 = (int)DAT_UnitsState.units[unitID].microYPosition;
      iVar4 = (int)DAT_UnitsState.units[unitID].microXPosition;
      ownerColorUnk = DAT_UnitsState.units[unitID].calculatedOwnerPlayerIndex;
      playerID1 = (int)DAT_UnitsState.units[unitID].owner;
    }
    else {
      projectileType = ET_COW_FLYING;
      iVar7 = DAT_UnitsState.units[unitID].buildingHeight + 0x82 +
              (int)DAT_UnitsState.units[unitID].terrainOrClimbHeight;
      iVar5 = (int)DAT_UnitsState.units[unitID].microYPosition;
      iVar4 = (int)DAT_UnitsState.units[unitID].microXPosition;
      ownerColorUnk = DAT_UnitsState.units[unitID].calculatedOwnerPlayerIndex;
      playerID1 = (int)DAT_UnitsState.units[unitID].owner;
    }
    goto LAB_00532b15;
  }
  if (projectileType == ET_CATAPULT) {
    piVar6 = DAT_UnitsState.unitCountOfSelection + unitID * 0x124 + -9;
    switch(DAT_UnitsState.units[unitID].facingDirection) {
    case 0:
      iVar5 = -7;
      break;
    case 1:
      iVar4 = 4;
      iVar5 = -4;
      break;
    case 2:
      iVar4 = 7;
      break;
    case 3:
      iVar4 = 4;
      iVar5 = 4;
      break;
    case 4:
      iVar5 = 7;
      break;
    case 5:
      iVar4 = -4;
      iVar5 = 4;
      break;
    case 6:
      iVar4 = -7;
      break;
    case 7:
      iVar4 = -4;
      iVar5 = -4;
    }
    iVar7 = (int)DAT_UnitsState.units[unitID].terrainOrClimbHeight;
    iVar8 = 0;
    if (DAT_UnitsState.units[unitID].field260_0x3b0 == 0) {
      projectileType = ET_CATAPULT;
      iVar7 = DAT_UnitsState.units[unitID].buildingHeight + 0x38 + iVar7;
      iVar5 = DAT_UnitsState.units[unitID].microYPosition + iVar5;
      playerID1 = (int)DAT_UnitsState.units[unitID].owner;
      iVar4 = DAT_UnitsState.units[unitID].microXPosition + iVar4;
      ownerColorUnk = DAT_UnitsState.units[unitID].calculatedOwnerPlayerIndex;
    }
    else {
      projectileType = ET_COW_FLYING;
      iVar7 = DAT_UnitsState.units[unitID].buildingHeight + 0x38 + iVar7;
      iVar5 = DAT_UnitsState.units[unitID].microYPosition + iVar5;
      playerID1 = (int)DAT_UnitsState.units[unitID].owner;
      iVar4 = DAT_UnitsState.units[unitID].microXPosition + iVar4;
      ownerColorUnk = DAT_UnitsState.units[unitID].calculatedOwnerPlayerIndex;
    }
    goto LAB_00532b15;
  }
  if (projectileType == ET_MANGONEL) {
    piVar6 = DAT_UnitsState.unitCountOfSelection + unitID * 0x124 + -9;
    switch(DAT_UnitsState.units[unitID].facingDirection) {
    case 0:
      iVar5 = -2;
      break;
    case 1:
    case 4:
      iVar4 = 0;
      iVar5 = 0;
      break;
    case 2:
    case 6:
      iVar4 = 0;
      break;
    case 3:
      iVar4 = -1;
      iVar5 = 1;
      break;
    case 5:
      iVar4 = -2;
      iVar5 = 2;
      break;
    case 7:
      iVar4 = 1;
      iVar5 = -1;
    }
    iVar8 = 0;
    projectileType = ET_MANGONEL;
    iVar7 = DAT_UnitsState.units[unitID].buildingHeight + 0x40 +
            (int)DAT_UnitsState.units[unitID].terrainOrClimbHeight;
    iVar5 = DAT_UnitsState.units[unitID].microYPosition + iVar5;
    playerID1 = (int)DAT_UnitsState.units[unitID].owner;
    iVar4 = DAT_UnitsState.units[unitID].microXPosition + iVar4;
    ownerColorUnk = DAT_UnitsState.units[unitID].calculatedOwnerPlayerIndex;
    goto LAB_00532b15;
  }
  if ((projectileType == ET_BALLISTA) || (projectileType == ET_FIREBALLISTA)) {
    piVar6 = DAT_UnitsState.unitCountOfSelection + unitID * 0x124 + -9;
    iVar8 = 0;
    iVar7 = DAT_UnitsState.units[unitID].buildingHeight + 0x19 +
            (int)DAT_UnitsState.units[unitID].terrainOrClimbHeight;
LAB_00532af4:
    sVar1 = (short)piVar6[0x1b3];
    sVar2 = *(short *)((int)piVar6 + 0x6ca);
    ownerColorUnk = piVar6[0x189];
    sVar3 = *(short *)((int)piVar6 + 0x6aa);
LAB_00532b14:
    iVar5 = (int)sVar1;
    iVar4 = (int)sVar2;
    playerID1 = (int)sVar3;
    goto LAB_00532b15;
  }
  if ((projectileType != 8) && (projectileType != ~ET_UNKNOWN)) {
    piVar6 = DAT_UnitsState.unitCountOfSelection + unitID * 0x124 + -9;
    if (DAT_UnitsState.units[unitID].unitType == UT_A_HARCHER) {
      iVar8 = (int)DAT_UnitsState.units[unitID].shootTargetedUnit;
      iVar7 = DAT_UnitsState.units[unitID].buildingHeight + 0x2d +
              (int)DAT_UnitsState.units[unitID].terrainOrClimbHeight;
      goto LAB_00532af4;
    }
    iVar8 = (int)DAT_UnitsState.units[unitID].shootTargetedUnit;
                    /* This limits the range of arrow type projectiles */
    iVar7 = DAT_UnitsState.units[unitID].buildingHeight + 0x1e +
            (int)DAT_UnitsState.units[unitID].terrainOrClimbHeight;
    sVar1 = DAT_UnitsState.units[unitID].microYPosition;
    sVar2 = DAT_UnitsState.units[unitID].microXPosition;
    ownerColorUnk = DAT_UnitsState.units[unitID].calculatedOwnerPlayerIndex;
    sVar3 = DAT_UnitsState.units[unitID].owner;
    goto LAB_00532b14;
  }
  piVar6 = DAT_UnitsState.unitCountOfSelection + unitID * 0x124 + -9;
  switch(DAT_UnitsState.units[unitID].facingDirection) {
  case 0:
    goto switchD_00532a3f_caseD_0;
  case 1:
    iVar4 = 10;
switchD_00532a3f_caseD_0:
    iVar5 = -4;
    break;
  case 2:
    iVar4 = 10;
    break;
  case 3:
    iVar4 = 10;
  case 4:
    iVar5 = 4;
    break;
  case 5:
    iVar5 = 4;
  case 6:
switchD_00532a3f_caseD_6:
    iVar4 = -10;
    break;
  case 7:
    iVar5 = -4;
    goto switchD_00532a3f_caseD_6;
  }
  iVar8 = 0;
  iVar7 = DAT_UnitsState.units[unitID].buildingHeight + 0xc +
          (int)DAT_UnitsState.units[unitID].terrainOrClimbHeight;
  iVar5 = DAT_UnitsState.units[unitID].microYPosition + iVar5;
  playerID1 = (int)DAT_UnitsState.units[unitID].owner;
  iVar4 = DAT_UnitsState.units[unitID].microXPosition + iVar4;
  ownerColorUnk = DAT_UnitsState.units[unitID].calculatedOwnerPlayerIndex;
LAB_00532b15:
  Entities::EntityState::spawnProjectileEntity
            (&DAT_EntityState,unitID,playerID1,ownerColorUnk,iVar4,iVar5,iVar7,targetX,targetY,
             targetZUnk,projectileType,iVar8);
  if (*(short *)(piVar6 + 0x23b) != 0) {
    DAT_TribesState.tribes[*(short *)(piVar6 + 0x23b)].countdown2 = 500;
  }
  return;
}



// ================= setProjectileTargetPosition @ 00405cf0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Entities::EntityState::setProjectileTargetPosition
          (EntityState *this,int entityID,int x,int y,int height,int targetX,int targetY,int targetZ
          )

{
  short sVar1;
  
  DAT_EntityState.entityArray[entityID].targetZ = (short)targetZ;
  DAT_EntityState.entityArray[entityID].targetY = (short)targetY;
  DAT_EntityState.entityArray[entityID].microX = (short)x;
  DAT_EntityState.entityArray[entityID].x_2 = (short)x;
  DAT_EntityState.entityArray[entityID].microY = (short)y;
  DAT_EntityState.entityArray[entityID].y_2 = (short)y;
  sVar1 = (short)height;
  DAT_EntityState.entityArray[entityID].height = sVar1;
  DAT_EntityState.entityArray[entityID].startingHeight_2 = sVar1;
  DAT_EntityState.entityArray[entityID].height_2 = sVar1;
  DAT_EntityState.entityArray[entityID].startingHeight = sVar1;
  DAT_EntityState.entityArray[entityID].targetX = (short)targetX;
  DAT_EntityState.entityArray[entityID].heightDifference = targetZ - height;
  Navigation::DirectionAlgorithmState::somethingWithProjectileDistance
            (&DAT_DirectionAlgorithmState,x,y,targetX,targetY);
  DAT_EntityState.entityArray[entityID].orientation = DAT_DirectionAlgorithmState.orientation;
  initializeProjectileVelocities(&DAT_EntityState,entityID,x,y,height,targetX,targetY,targetZ);
  return;
}



// ================= initializeProjectileVelocities @ 00403a20 =================

/* decompilerscript: committed: 2025-01-30 21:56:35.138000 */

void __thiscall
_HoldStrong::Map::Entities::EntityState::initializeProjectileVelocities
          (EntityState *this,int entityID,int x,int y,int height,int targetX,int targetY,int targetZ
          )

{
  float fVar1;
  short sVar2;
  ushort uVar3;
  EntityTypeShort EVar4;
  double dVar5;
  short sVar6;
  uint uVar7;
  int iVar8;
  short sVar9;
  short sVar10;
  int iVar11;
  float10 fVar12;
  float10 fVar13;
  
  sVar6 = (short)targetY;
  if (targetY < y) {
    DAT_EntityState.entityArray[entityID].field42_0x64 = (short)y - sVar6;
  }
  else {
    DAT_EntityState.entityArray[entityID].field42_0x64 = sVar6 - (short)y;
  }
  sVar10 = (short)targetX;
  if (targetX < x) {
    sVar9 = (short)x - sVar10;
  }
  else {
    sVar9 = sVar10 - (short)x;
  }
  sVar2 = DAT_EntityState.entityArray[entityID].targetZ;
  DAT_EntityState.entityArray[entityID].field39_0x5e = sVar9;
  sVar9 = DAT_EntityState.entityArray[entityID].height;
  if (sVar9 < sVar2) {
    DAT_EntityState.entityArray[entityID].field44_0x68 = sVar2 - sVar9;
  }
  else {
    DAT_EntityState.entityArray[entityID].field44_0x68 = sVar9 - sVar2;
  }
  sVar9 = DAT_EntityState.entityArray[entityID].field39_0x5e;
  DAT_EntityState.entityArray[entityID].field38_0x5c = sVar10;
  DAT_EntityState.entityArray[entityID].field41_0x62 = sVar6;
  DAT_EntityState.entityArray[entityID].someMicroX = (ushort)(x <= targetX) * 2 + -1;
  DAT_EntityState.entityArray[entityID].someMicroY = (ushort)(y <= targetY) * 2 + -1;
  if (sVar9 == 0) {
    if (DAT_EntityState.entityArray[entityID].field42_0x64 == 0) {
      DAT_EntityState.entityArray[entityID].field50_0x74 = 0;
    }
    else {
      DAT_EntityState.entityArray[entityID].field50_0x74 = 1;
    }
  }
  else {
    sVar6 = DAT_EntityState.entityArray[entityID].field42_0x64;
    if (sVar6 == 0) {
      DAT_EntityState.entityArray[entityID].field50_0x74 = 2;
    }
    else if (sVar9 < sVar6) {
      DAT_EntityState.entityArray[entityID].field50_0x74 = 3;
    }
    else {
      DAT_EntityState.entityArray[entityID].field50_0x74 = 4;
    }
  }
  sVar6 = DAT_EntityState.entityArray[entityID].field50_0x74;
  if (sVar6 == 3) {
    sVar10 = sVar9 * 2;
    sVar9 = DAT_EntityState.entityArray[entityID].field42_0x64;
    DAT_EntityState.entityArray[entityID].field47_0x6e = sVar10;
    sVar6 = DAT_EntityState.entityArray[entityID].field42_0x64;
    DAT_EntityState.entityArray[entityID].field48_0x70 = sVar10 + sVar9 * -2;
LAB_00403b64:
    DAT_EntityState.entityArray[entityID].field49_0x72 = sVar10 - sVar6;
  }
  else if (sVar6 == 4) {
    sVar10 = DAT_EntityState.entityArray[entityID].field42_0x64 * 2;
    DAT_EntityState.entityArray[entityID].field47_0x6e = sVar10;
    sVar6 = DAT_EntityState.entityArray[entityID].field39_0x5e;
    DAT_EntityState.entityArray[entityID].field48_0x70 = sVar10 + sVar9 * -2;
    goto LAB_00403b64;
  }
  iVar8 = DAT_EntityDefinedData.DAT_EntityArrayCurveTypeForProjectileType
          [(short)DAT_EntityState.entityArray[entityID].entityType];
  if (iVar8 == 0) {
    uVar7 = computeLineOfSightDistance(&DAT_EntityState,x,y,height,targetX,targetY,targetZ,1);
    sVar6 = (short)uVar7;
    DAT_EntityState.entityArray[entityID].field62_0x94 = sVar6;
    DAT_EntityState.entityArray[entityID].field58_0x8c = sVar6;
    DAT_EntityState.entityArray[entityID].field80_0xba =
         (short)DAT_EntityState.lineOfSightClearanceSteps;
    sVar10 = DAT_EntityState.entityArray[entityID].velocityUnk;
  }
  else {
    if (iVar8 == 1) {
      uVar7 = computeLineOfSightDistance(&DAT_EntityState,x,y,height,targetX,targetY,targetZ,1);
      iVar8 = DAT_EntityState.entityArray[entityID].heightDifference;
      sVar6 = (short)uVar7;
      DAT_EntityState.entityArray[entityID].field62_0x94 = sVar6;
      DAT_EntityState.entityArray[entityID].field58_0x8c = sVar6;
      DAT_EntityState.entityArray[entityID].field80_0xba =
           (short)DAT_EntityState.lineOfSightClearanceSteps;
      iVar8 = computeVelocity(&DAT_EntityState,
                              (int)(short)DAT_EntityState.entityArray[entityID].entityType,
                              (double)(int)DAT_EntityState.entityArray[entityID].startingAngle,
                              (int)sVar6,iVar8);
      DAT_EntityState.entityArray[entityID].velocityUnk = (short)iVar8;
      goto LAB_00403f37;
    }
    if (iVar8 == 2) {
      uVar7 = computeLineOfSightDistance(&DAT_EntityState,x,y,height,targetX,targetY,targetZ,1);
      sVar6 = DAT_EntityState.entityArray[entityID].height;
      sVar10 = DAT_EntityState.entityArray[entityID].targetZ;
      sVar9 = (short)uVar7;
      DAT_EntityState.entityArray[entityID].field62_0x94 = sVar9;
      DAT_EntityState.entityArray[entityID].field58_0x8c = sVar9;
      DAT_EntityState.entityArray[entityID].field80_0xba =
           (short)DAT_EntityState.lineOfSightClearanceSteps;
      if (sVar10 < sVar6) {
        DAT_EntityState.entityArray[entityID].startingAngle = 3;
      }
      iVar8 = DAT_EntityState.entityArray[entityID].heightDifference;
      iVar11 = computeVelocity(&DAT_EntityState,
                               (int)(short)DAT_EntityState.entityArray[entityID].entityType,
                               (double)(int)DAT_EntityState.entityArray[entityID].startingAngle,
                               (int)sVar9,iVar8);
      DAT_EntityState.entityArray[entityID].velocityUnk = (short)iVar11;
      dVar5 = DOUBLE_0059e878;
      if ((short)iVar11 < 1) {
        EVar4 = DAT_EntityState.entityArray[entityID].entityType;
        DAT_EntityState.entityArray[entityID].startingAngle = 0xf;
        iVar8 = computeVelocity(&DAT_EntityState,(int)(short)EVar4,dVar5,(int)sVar9,iVar8);
        DAT_EntityState.entityArray[entityID].velocityUnk = (short)iVar8;
      }
      goto LAB_00403f37;
    }
    if (iVar8 == 3) {
      uVar3 = (ushort)DAT_EntityState.entityArray[entityID].rng_1;
      DAT_EntityState.entityArray[entityID].startingAngle = (uVar3 & 0xf) + 8;
      DAT_EntityState.entityArray[entityID].velocityUnk = (uVar3 & 7) + 0x15;
      goto LAB_00403f37;
    }
    if (iVar8 == 4) {
      uVar7 = DAT_EntityState.entityArray[entityID].rng_1;
      sVar6 = (short)((int)uVar7 % 0x14) + 0x10;
      DAT_EntityState.entityArray[entityID].startingAngle = sVar6;
      if ((char)uVar7 < '\0') {
        DAT_EntityState.entityArray[entityID].startingAngle = -sVar6;
      }
      sVar6 = (short)(((int)uVar7 >> 8) % 0x14) + 0x10;
      DAT_EntityState.entityArray[entityID].velocityUnk = sVar6;
      if ((uVar7 & 0x8000) == 0) {
        return;
      }
      DAT_EntityState.entityArray[entityID].velocityUnk = -sVar6;
      return;
    }
    if (iVar8 == 5) {
      iVar11 = DAT_EntityState.entityArray[entityID].rng_1;
      iVar8 = DAT_EntityState.entityArray[entityID].rng_1;
      DAT_EntityState.entityArray[entityID].velocityUnk = 0;
      DAT_EntityState.entityArray[entityID].startingAngle = (byte)iVar11 & 7;
      DAT_EntityState.entityArray[entityID].graphicRotationUnk = (ushort)((uint)iVar8 >> 8) & 0x3f;
      return;
    }
    if (iVar8 != 6) {
      if (iVar8 == 7) {
        return;
      }
      if (iVar8 == 10) {
        return;
      }
      if (iVar8 == 8) {
        sVar6 = DAT_EntityState.entityArray[entityID].unitID_OR_seaGullID;
        if (sVar6 == 0) {
          DAT_EntityState.entityArray[entityID].startingAngle =
               (short)(DAT_EntityState.entityArray[entityID].rng_1 % 0x3c) + 8;
          DAT_EntityState.entityArray[entityID].velocityUnk =
               ((byte)DAT_EntityState.entityArray[entityID].rng_1 & 7) + 0x23;
        }
        else {
          if (sVar6 == 4) {
            DAT_EntityState.entityArray[entityID].startingAngle =
                 (short)(DAT_EntityState.entityArray[entityID].rng_1 % 0x1e) + 0xf;
            sVar6 = ((byte)DAT_EntityState.entityArray[entityID].rng_1 & 7) + 0xf;
          }
          else {
            iVar8 = DAT_EntityState.entityArray[entityID].rng_1;
            if (sVar6 == 5) {
              DAT_EntityState.entityArray[entityID].startingAngle = (short)(iVar8 % 0x1e) + 0x2d;
              DAT_EntityState.entityArray[entityID].velocityUnk =
                   ((byte)DAT_EntityState.entityArray[entityID].rng_1 & 7) + 0x23;
              goto LAB_00403f37;
            }
            DAT_EntityState.entityArray[entityID].startingAngle = (short)(iVar8 % 0x23) + 0x14;
            sVar6 = ((byte)DAT_EntityState.entityArray[entityID].rng_1 & 7) + 0x19;
          }
          fVar1 = DAT_EntityState.entityArray[entityID]._elapsedTimeOrGravityAccumulator;
          DAT_EntityState.entityArray[entityID].velocityUnk = sVar6;
          DAT_EntityState.entityArray[entityID]._elapsedTimeOrGravityAccumulator =
               fVar1 * (float)DOUBLE_0059e870;
        }
      }
      else if (iVar8 == 9) {
        DAT_EntityState.entityArray[entityID].startingAngle = 0;
      }
      goto LAB_00403f37;
    }
    uVar7 = computeLineOfSightDistance(&DAT_EntityState,x,y,height,targetX,targetY,targetZ,1);
    sVar6 = (short)uVar7;
    DAT_EntityState.entityArray[entityID].field62_0x94 = sVar6;
    DAT_EntityState.entityArray[entityID].field58_0x8c = sVar6;
    DAT_EntityState.entityArray[entityID].field80_0xba =
         (short)DAT_EntityState.lineOfSightClearanceSteps;
    if (0x96 < sVar6) {
      DAT_EntityState.entityArray[entityID].velocityUnk = 0x7d;
    }
    sVar10 = DAT_EntityState.entityArray[entityID].velocityUnk;
  }
  iVar8 = math_atan_1(&DAT_EntityState,(int)(short)DAT_EntityState.entityArray[entityID].entityType,
                      (double)(int)sVar10,(int)sVar6,
                      DAT_EntityState.entityArray[entityID].heightDifference);
  DAT_EntityState.entityArray[entityID].startingAngle = (short)iVar8;
LAB_00403f37:
  EVar4 = DAT_EntityState.entityArray[entityID].entityType;
  if ((((EVar4 == ET_ARROW_AND_DEFAULT) || (EVar4 == ET_CROSSBOWARROW)) && (height + 0x36 < targetZ)
      ) && (DAT_EntityState.entityArray[entityID].rng_1 % 10 == 5)) {
    DAT_EntityState.entityArray[entityID].hasDoneEffectUnk = 1;
  }
  iVar11 = (int)DAT_EntityState.entityArray[entityID].startingAngle;
  DAT_EntityState.entityArray[entityID].speedUnk = 0;
  iVar8 = (int)DAT_EntityState.entityArray[entityID].velocityUnk;
  DAT_EntityState.entityArray[entityID].travelledDistance = 0;
  fVar12 = ((float10)iVar11 * (float10)DOUBLE_0059e848) / (float10)DOUBLE_0059e850;
  fVar13 = HoldStrong_lib::_math_cos(fVar12);
  DAT_EntityState.entityArray[entityID].vCos = (float)(fVar13 * (float10)iVar8);
  fVar12 = HoldStrong_lib::_math_sin((float10)(double)fVar12);
  DAT_EntityState.entityArray[entityID].vSin = (float)(fVar12 * (float10)iVar8);
  sVar6 = angleToRotationFrameIndex(iVar11);
  DAT_EntityState.entityArray[entityID].field45_0x6a = sVar6;
  return;
}



