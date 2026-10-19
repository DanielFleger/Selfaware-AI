// ================= giveBackResourceForDestroyedBuilding @ 00421d70 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Buildings::BuildingsState::giveBackResourceForDestroyedBuilding
          (BuildingsState *this,int buildingIDORIfNegResourceType,int playerID,int param_3)

{
  int *piVar1;
  short *psVar2;
  BuildingTypeShort BVar3;
  Building *pBVar4;
  int iVar5;
  BOOLEnum BVar6;
  short sVar7;
  int iVar8;
  int iVar9;
  int amount;
  int playerID_00;
  int amount_00;
  
  playerID_00 = playerID;
  if (param_3 != 0) {
    iVar5 = param_3;
    if (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) {
      iVar5 = 100;
    }
    if (buildingIDORIfNegResourceType == -1) {
      if (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) {
        piVar1 = DAT_GameState.playerDataArray[playerID].startResources + 4;
                    /* return DAT_PlayerDataArray[playerID].field_0x47c */
        *piVar1 = *piVar1 + 1;
        return;
      }
      psVar2 = &DAT_GameState.playerDataArray[playerID].stoneGainedFraction;
      iVar5 = iVar5 * 2;
                    /* Compiler magic for division by 100 and a signed divide by 4 */
      sVar7 = (((short)(iVar5 / 100) + (short)(iVar5 >> 0x1f)) -
              (short)((longlong)iVar5 * 0x51eb851f >> 0x3f)) + *psVar2;
      iVar5 = (int)((int)sVar7 + ((int)sVar7 >> 0x1f & 3U)) >> 2;
      *psVar2 = sVar7 + (short)iVar5 * -4;
      BVar6 = processResourceGain(&DAT_BuildingsState,playerID,RT_STONE,iVar5);
      if (BVar6 == FALSE) {
        Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID_00);
        return;
      }
    }
    else if (buildingIDORIfNegResourceType == -2) {
      psVar2 = &DAT_GameState.playerDataArray[playerID].woodGainedFraction;
      iVar5 = iVar5 * 2;
      sVar7 = (((short)(iVar5 / 100) + (short)(iVar5 >> 0x1f)) -
              (short)((longlong)iVar5 * 0x51eb851f >> 0x3f)) + *psVar2;
      iVar5 = (int)((int)sVar7 + ((int)sVar7 >> 0x1f & 3U)) >> 2;
      *psVar2 = sVar7 + (short)iVar5 * -4;
      BVar6 = processResourceGain(&DAT_BuildingsState,playerID,RT_WOOD,iVar5);
      if (BVar6 == FALSE) {
        Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID_00);
        return;
      }
    }
    else {
      if (buildingIDORIfNegResourceType == -3) {
                    /* Tower mangonel? */
        iVar8 = DAT_BuildingsState.buildingCosts[0x56].requiredStone_0x4 * iVar5;
        iVar9 = DAT_BuildingsState.buildingCosts[0x56].requiredIron_0x8 * iVar5;
        amount_00 = (DAT_BuildingsState.buildingCosts[0x56].requiredPitch_0xc * iVar5) / 100;
        amount = (DAT_BuildingsState.buildingCosts[0x56].requiredGold * iVar5) / 100;
        BVar6 = processResourceGain(&DAT_BuildingsState,playerID,RT_WOOD,
                                    (DAT_BuildingsState.buildingCosts[0x56].requiredWood * iVar5) /
                                    100);
        if (BVar6 == FALSE) {
          Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID);
        }
        playerID_00 = playerID;
        BVar6 = processResourceGain(&DAT_BuildingsState,playerID,RT_STONE,iVar8 / 100);
        if (BVar6 == FALSE) {
          Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID_00);
        }
        BVar6 = processResourceGain(&DAT_BuildingsState,playerID_00,RT_IRON,iVar9 / 100);
        if (BVar6 == FALSE) {
          Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID_00);
        }
      }
      else if (buildingIDORIfNegResourceType == -4) {
                    /* Tower ballista? */
        iVar8 = DAT_BuildingsState.buildingCosts[0x57].requiredStone_0x4 * iVar5;
        iVar9 = DAT_BuildingsState.buildingCosts[0x57].requiredIron_0x8 * iVar5;
        amount_00 = (DAT_BuildingsState.buildingCosts[0x57].requiredPitch_0xc * iVar5) / 100;
        amount = (DAT_BuildingsState.buildingCosts[0x57].requiredGold * iVar5) / 100;
        BVar6 = processResourceGain(&DAT_BuildingsState,playerID,RT_WOOD,
                                    (DAT_BuildingsState.buildingCosts[0x57].requiredWood * iVar5) /
                                    100);
        if (BVar6 == FALSE) {
          Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID);
        }
        playerID_00 = playerID;
        BVar6 = processResourceGain(&DAT_BuildingsState,playerID,RT_STONE,iVar8 / 100);
        if (BVar6 == FALSE) {
          Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID_00);
        }
        BVar6 = processResourceGain(&DAT_BuildingsState,playerID_00,RT_IRON,iVar9 / 100);
        if (BVar6 == FALSE) {
          Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID_00);
        }
      }
      else {
        BVar3 = DAT_BuildingsState.buildings[buildingIDORIfNegResourceType].buildingType;
        pBVar4 = DAT_BuildingsState.buildings + buildingIDORIfNegResourceType;
        iVar9 = (DAT_BuildingsState.buildingCosts[(short)BVar3].requiredStone_0x4 * iVar5) / 100;
        iVar8 = DAT_BuildingsState.buildingCosts[(short)BVar3].requiredIron_0x8;
        amount_00 = (DAT_BuildingsState.buildingCosts[(short)BVar3].requiredPitch_0xc * iVar5) / 100
        ;
        amount = (DAT_BuildingsState.buildingCosts[(short)BVar3].requiredGold * iVar5) / 100;
        buildingIDORIfNegResourceType = amount;
        param_3 = iVar9;
        if (DAT_GameCore.gameMode_2 == GM_SIEGE_THAT) {
          resourceGainForKillingPitAndPitchDitch
                    (&DAT_BuildingsState,(int)(short)pBVar4->buildingType,&param_3,
                     &buildingIDORIfNegResourceType);
          piVar1 = DAT_GameState.playerDataArray[playerID].startResources + 4;
          *piVar1 = *piVar1 + param_3;
          piVar1 = DAT_GameState.playerDataArray[playerID].startResources + 0xf;
          *piVar1 = *piVar1 + buildingIDORIfNegResourceType;
          return;
        }
        BVar6 = processResourceGain(&DAT_BuildingsState,playerID,RT_WOOD,
                                    (DAT_BuildingsState.buildingCosts[(short)BVar3].requiredWood *
                                    iVar5) / 100);
        if (BVar6 == FALSE) {
          Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID_00);
        }
        BVar6 = processResourceGain(&DAT_BuildingsState,playerID_00,RT_STONE,iVar9);
        if (BVar6 == FALSE) {
          Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID_00);
        }
        BVar6 = processResourceGain(&DAT_BuildingsState,playerID_00,RT_IRON,(iVar8 * iVar5) / 100);
        if (BVar6 == FALSE) {
          Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID_00);
        }
      }
      BVar6 = processResourceGain(&DAT_BuildingsState,playerID_00,RT_PITCH,amount_00);
      if (BVar6 == FALSE) {
        Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID_00);
      }
      BVar6 = processResourceGain(&DAT_BuildingsState,playerID_00,RT_GOLD,amount);
      if (BVar6 == FALSE) {
        Game::GameStateStructures::playSFXNoSpaceInTheStockPile(&DAT_GameState,playerID_00);
      }
    }
  }
  return;
}



