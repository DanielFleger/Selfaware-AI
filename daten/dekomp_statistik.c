##### resetCountsAndStatistics @ 0x004560f0

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Game::GameStateStructures::resetCountsAndStatistics(GameStateStructures *this)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  short *psVar4;
  
  DAT_GameState.mapAndTime.field193_0x198 = 0;
  DAT_GameState.mapAndTime.field1447_0xa3c = 0;
  DAT_GameState.mapAndTime.field3166_0x277c = 0;
  DAT_GameState.mapAndTime.field3168_0x2790 = 0;
  DAT_GameState.mapAndTime.field3170_0x27a4 = 0;
  DAT_GameState.mapAndTime.field3172_0x27ac = 0;
  piVar2 = &DAT_GameState.playerDataArray[1].someCountdown01;
  iVar3 = 8;
  do {
    if (0 < *piVar2) {
      *piVar2 = *piVar2 + -1;
    }
    piVar2[-0x388] = piVar2[-0xe28];
    piVar2[-0xd5d] = piVar2[-0xcfc];
    piVar2[-0xd5b] = piVar2[-0xd5c];
    *(short *)((int)piVar2 + -0x16ae) = (short)piVar2[-0x5bb];
    piVar2[-0xe31] = 0;
    piVar2[-0xe2e] = 0;
    piVar2[-0xe2a] = 0;
    piVar2[-0xe29] = 0;
    piVar2[-0xe28] = 0;
    piVar2[-0xe27] = 0;
    piVar2[-0xe2d] = 0;
    piVar2[-0x5ec] = 0;
    piVar2[-0x5c4] = 0;
    piVar2[-0x5b6] = 0;
    piVar2[-0x5b5] = 0;
    piVar2[-0xcfd] = 0;
    piVar2[-0xcfc] = 0;
    piVar2[-10] = 0;
    piVar2[-0xd5c] = 0;
    piVar2[-0x602] = 0;
    piVar2[-0x597] = 0;
    piVar2[-0x5ee] = 0;
    piVar2[-0x5bd] = 0;
    piVar2[-0x5bc] = 0;
    piVar2[-0x5a5] = 0;
    piVar2[-0x628] = 0;
    piVar2[-0x627] = 0;
    piVar2[-0x626] = 0;
    piVar2[-0x625] = 0;
    piVar2[-0x624] = 0;
    piVar2[-0x623] = 0;
    piVar2[-0x5bb] = 0;
    piVar2[-0xd36] = 0;
    piVar2[-0x5c1] = FALSE;
    piVar2[-0x395] = TRUE;
    piVar2[-0x394] = 1;
    piVar2[-0x386] = 0;
    piVar2[-1] = 0;
    piVar2[-0x385] = 0;
    piVar2[-900] = 0;
    piVar2[-899] = 0;
    piVar2[-0x382] = 0;
    piVar2[0x18] = 0;
    piVar2[0x19] = 0;
    piVar2[0x1a] = 0;
    piVar2[-0x37b] = 0;
    piVar2[-0x37a] = 0;
    piVar2[-0x369] = 0;
    piVar2[-0x368] = 0;
    piVar2[-0x367] = 0;
    piVar2[-0x366] = 0;
    psVar4 = (short *)(piVar2 + -0xdc);
    for (iVar1 = 0x32; iVar1 != 0; iVar1 = iVar1 + -1) {
      psVar4[0] = 0;
      psVar4[1] = 0;
      psVar4 = psVar4 + 2;
    }
    piVar2[-0xaa] = 0;
    piVar2[-0x3cb] = 0;
    piVar2[-0x3ca] = 0;
    piVar2[-0x3c9] = 0;
    piVar2[-0x3c8] = 0;
    piVar2[-0x3c7] = 0;
    piVar2[-0x3c6] = 0;
    piVar2[-0x3c5] = 0;
    piVar2[-0x3c4] = 0;
    piVar2[-0x3c3] = 0;
    piVar2[-0x3c2] = 0;
    piVar2[-0x3c1] = 0;
    piVar2[-0x3c0] = 0;
    piVar2[-0x3bf] = 0;
    piVar2[-0x3be] = 0;
    piVar2[-0x3bd] = 0;
    piVar2[-0x3bc] = 0;
    piVar2[-0x3bb] = 0;
    piVar2[-0x3ba] = 0;
    piVar2[-0x3b9] = 0;
    piVar2[-0x3b8] = 0;
    piVar2[-0x61d] = 0;
    piVar2[-0x61c] = 0;
    piVar2[-0x61b] = 0;
    piVar2[-0x61a] = 0;
    piVar2[-0x619] = 0;
    piVar2[-0x618] = 0;
    piVar2[-0x617] = 0;
    piVar2[-0x616] = 0;
    piVar2[-0x615] = 0;
    piVar2[-0x614] = 0;
    piVar2[-0xb28] = 0;
    *(undefined2 *)(piVar2 + 0x23) = 0;
    piVar2[-0xb0c] = 0;
    *(undefined2 *)((int)piVar2 + 0x8e) = 0;
    *(undefined2 *)((int)piVar2 + 0x92) = 0;
    piVar2[-0xd17] = 1;
    if (piVar2[-0x601] < 1) {
      piVar2[-0x601] = 0x1e;
    }
    if (*(short *)((int)piVar2 + -0x38e2) != 0) {
      *(short *)((int)piVar2 + -0x38e2) = *(short *)((int)piVar2 + -0x38e2) + -1;
    }
    if ((short)piVar2[-0xe38] != 0) {
      *(short *)(piVar2 + -0xe38) = (short)piVar2[-0xe38] + -1;
    }
    piVar2 = piVar2 + 0xe7d;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  return;
}


##### resetVariousCountsAndStatisticsAndStartGoodsAndResources @ 0x00455e10

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Game::GameStateStructures::resetVariousCountsAndStatisticsAndStartGoodsAndResources
          (GameStateStructures *this)

{
  int *piVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  int playerID;
  int *piVar5;
  
  playerID = 1;
  piVar5 = &DAT_GameState.playerDataArray[1].foodTypesCurrentlyEaten;
  do {
    piVar5[-1] = 0;
    *piVar5 = 0;
    piVar5[0x31] = 0;
    *(short *)((int)piVar5 + 0x1a6) = 0;
    *(short *)(piVar5 + 0x69) = 0;
    piVar5[-0x80f] = 2000;
    piVar5[0x32] = 0;
    iVar4 = DAT_GameState.mapAndTime.startingPopularity * 10;
    piVar5[-0x812] = iVar4;
    piVar5[-0x73d] = iVar4;
    *(short *)(piVar5 + 0x6a) = (short)iVar4;
    piVar5[0x38] = 3;
    piVar5[0x39] = 2;
    iVar4 = DAT_GameState.playerDataArray[DAT_GameSynchronyState.currentPlayerSlotID].rationsSetting
    ;
    piVar5[-0x821] = iVar4;
    piVar5[-0x824] = iVar4;
    piVar5[-0x81c] = 1;
    piVar5[0x63d] = 1;
    piVar5[-0x81d] = 0;
    piVar5[-0x81b] = 0x3c;
    piVar5[0x621] = 0;
    piVar5[0x67] = 0;
    *(short *)((int)piVar5 + 0x1d6) = 0;
    piVar5[0x7b] = 0;
    *(short *)(piVar5 + 0x81) = 0;
    *(short *)((int)piVar5 + 0x206) = 0;
    *(short *)(piVar5 + 0x82) = 0;
    *(short *)((int)piVar5 + 0x20a) = 0;
    *(short *)(piVar5 + 0x83) = 0;
    *(short *)((int)piVar5 + 0x20e) = 0;
    *(short *)(piVar5 + 0x84) = 0;
    *(short *)((int)piVar5 + 0x212) = 0;
    *(short *)(piVar5 + 0x85) = 0;
    *(short *)((int)piVar5 + 0x216) = 0;
    *(short *)(piVar5 + 0x86) = 0;
    *(short *)((int)piVar5 + 0x21a) = 0;
    piVar5[0x87] = 0;
    *(short *)(piVar5 + 0x63e) = 0;
    *(short *)((int)piVar5 + 0x18fa) = 0;
    piVar3 = piVar5 + -0x70f;
    piVar1 = DAT_GameState.mapAndTime.startGoods;
    iVar4 = 0x19;
    do {
      *piVar3 = *piVar1;
      piVar1 = piVar1 + 1;
      piVar3 = piVar3 + 1;
      iVar4 = iVar4 + -1;
    } while (iVar4 != 0);
    OS::_memset(piVar5 + 0x3b,0,100);
    piVar5[99] = 0;
    piVar5[0x62] = 0;
    piVar5[0x7e] = 0;
    *(short *)(piVar5 + -0x81a) = 0;
    *(short *)((int)piVar5 + -0x2066) = 0;
    if (DAT_GameState.mapAndTime.editScenarioExtraOptions != 0) {
      piVar5[0x38] = (int)DAT_GameState.mapAndTime.scenarioTaxesSetting;
      iVar4 = (int)DAT_GameState.mapAndTime.scenarioRationsSetting;
      piVar5[-0x821] = iVar4;
      piVar5[-0x824] = iVar4;
      piVar5[0x39] = iVar4;
      piVar5[-0x6e7] = (int)DAT_GameState.mapAndTime.scenarioGold;
    }
    if (DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) {
      iVar4 = 1;
      if (((DAT_GameCore.gameMode_2 == GM_SKIRMISH_AND_MULTIPLAYER) &&
          (DAT_GameCore.isSkirmishTrail == TRUE)) && (DAT_GameCore.currentTrailType == TT_EXTREME))
      {
        iVar4 = 3;
      }
      if (DAT_GameSynchronyState.currentPlayerFullIDArray[playerID] == -1) {
        if (DAT_GameSynchronyState.currentAIArray[playerID] == 0) goto LAB_00456069;
        iVar2 = DAT_RenderingDefinedData.field451_0x53bb4
                [(DAT_GameSynchronyState.skirmishCurrentAdvantageBalance +
                 DAT_GameSynchronyState.skirmishGameIntensityType * 5) * 2 + 0xd];
      }
      else {
        iVar2 = DAT_RenderingDefinedData.field451_0x53bb4
                [(DAT_GameSynchronyState.skirmishCurrentAdvantageBalance +
                 DAT_GameSynchronyState.skirmishGameIntensityType * 5) * 2 + 0xc];
      }
      piVar5[-0x700] = iVar2 * iVar4;
    }
LAB_00456069:
    DAT_GameState.mapAndTime.populationIndex = 0;
    *(short *)((int)piVar5 + 0x1a2) = (short)piVar5[-0x6e7];
    *(short *)(piVar5 + 0x68) = (short)piVar5[-0x6e7];
    piVar5[0x73] = -1000;
    *(short *)((int)(piVar5 + 0x76) + 0) = 0;
    *(short *)((int)(piVar5 + 0x76) + 2) = 0;
    *(short *)((int)(piVar5 + 0x77) + 0) = 0;
    *(short *)((int)(piVar5 + 0x77) + 2) = 0;
    AI::AICState::setCurrentAttackStrength(&DAT_AICState,playerID);
    AI::AICState::setCurrentAttackRaidParameter(&DAT_AICState,playerID);
    piVar5[0x5fd] = 0x30;
    piVar5[0x64b] = 0;
    piVar5[0x64c] = 0;
    playerID = playerID + 1;
    piVar5 = piVar5 + 0xe7d;
    if (8 < playerID) {
      return;
    }
  } while( true );
}


##### processUnitLossStatistic @ 0x004563d0

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Game::GameStateStructures::processUnitLossStatistic
          (GameStateStructures *this,int playerID,int unitID)

{
  int *piVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  
  if (playerID - 1U < 8) {
    switch(DAT_UnitsState.units[unitID].unitType) {
    case UT_S_CATAPULT:
    case UT_S_TREBUCHET:
    case UT_S_MANGONEL:
    case UT_S_TOWER:
    case UT_S_BATTERINGRAM:
    case UT_S_SHIELD:
    case UT_S_BALLISTA:
    case UT_S_FBALLISTA:
      piVar1 = &DAT_GameState.playerDataArray[playerID].troopsLost;
      *piVar1 = *piVar1 + (int)DAT_UnitsState.units[unitID].
                               digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300
      ;
      iVar3 = Map::Units::TroopValueState::getValueOfTroopType(&DAT_TroopValueState,UT_E_ENGINEER);
      iVar3 = iVar3 * DAT_UnitsState.units[unitID].
                      digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300;
      break;
    default:
      piVar1 = &DAT_GameState.playerDataArray[playerID].troopsLost;
      *piVar1 = *piVar1 + 1;
      iVar3 = Map::Units::TroopValueState::getValueOfTroopType
                        (&DAT_TroopValueState,(int)(short)DAT_UnitsState.units[unitID].unitType);
    }
    piVar1 = &DAT_GameState.playerDataArray[playerID].weightedLosses;
    *piVar1 = *piVar1 + iVar3;
    if (0 < iVar3) {
      if (playerID == DAT_GameSynchronyState.currentPlayerSlotID) {
        Map::Version::UpdateUnitLossData
                  (-iVar3,(int)DAT_UnitsState.units[unitID].lastEncounteredEnemyPlayerID);
      }
      if (DAT_UnitsState.units[unitID].lastEncounteredEnemyPlayerID ==
          DAT_GameSynchronyState.currentPlayerSlotID) {
        UpdateUnitValueLoss(iVar3);
      }
    }
    sVar2 = DAT_UnitsState.units[unitID].lastEncounteredEnemyPlayerID;
    if (sVar2 != 0) {
      DAT_GameState.playerDataArray[playerID].lastlastEncounteredEnemyPlayerID = (int)sVar2;
      sVar2 = DAT_UnitsState.units[unitID].lastEncounteredEnemyPlayerID;
      if ((1 < sVar2) && (sVar2 < 6)) {
        *(undefined1 *)
         ((int)DAT_GameState.playerDataArray[playerID].barracksAssemblyPoints + sVar2 + -10) = 1;
      }
    }
    if (DAT_GameSynchronyState.currentGameMode != GM_SOLITARY) {
      iVar4 = (int)DAT_UnitsState.units[unitID].lastEncounteredEnemyPlayerID;
      piVar1 = DAT_GameSynchronyState.finalResults.finalKillMatrix[iVar4] + playerID;
      *piVar1 = *piVar1 + 1;
      if (DAT_GameState.mapAndTime.playerTeams[iVar4] !=
          DAT_GameState.mapAndTime.playerTeams[playerID]) {
        if (DAT_UnitsState.units[unitID].field340_0x442 == 0) {
          piVar1 = DAT_GameSynchronyState.finalResults.finalTroopsKilledWeighted + iVar4;
          *piVar1 = *piVar1 + iVar3;
        }
        else {
          piVar1 = DAT_GameSynchronyState.finalResults.finalTroopsKilledWeighted + iVar4;
          *piVar1 = *piVar1 + ((int)(iVar3 + (iVar3 >> 0x1f & 3U)) >> 2);
        }
      }
      piVar1 = (int *)(iVar4 * 0x20 + 0x115e9dc + playerID * 0x39f4);
      *piVar1 = *piVar1 + 1;
    }
    if (DAT_UnitsState.units[unitID].isSelected != 0) {
      DAT_GameCore.countdown = 1;
    }
  }
  return;
}


##### MenuView_CrusadeEndscreen_Prepare @ 0x004df2e0

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::UI::MenuView_CrusadeEndscreen_Prepare(void)

{
  char *pcVar1;
  undefined4 uVar2;
  
  DAT_TextureRenderCoreObject.totalLoadedGfx = 0;
  Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"sktrail_win.tgx");
  Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"endframe1.tgx");
  Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"endframe2.tgx");
  Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"endframe3.tgx");
  Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"endframe4.tgx");
  Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"endframe5.tgx");
  Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"endframe6.tgx");
  Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"endframe7.tgx");
  Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"endframe8.tgx");
  Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"jesterlast.tgx");
  resetCredits();
  DAT_NumberOfStoredMenuStrings = 0;
                    /* added by script: "Congratulations!" */
  pcVar1 = Text::TextManager::getTextStringInGroupAtOffset
                     (&DAT_TextManagerObject,TEXT_SKTRAIL_WIN,0);
  Global::StoreStringInMenuStringArray(pcVar1);
                    /* added by script: "Many have set out..." */
  pcVar1 = Text::TextManager::getTextStringInGroupAtOffset
                     (&DAT_TextManagerObject,TEXT_SKTRAIL_WIN,1);
  Global::StoreStringInMenuStringArray(pcVar1);
                    /* added by script: "...but few will have survived this journey." */
  pcVar1 = Text::TextManager::getTextStringInGroupAtOffset
                     (&DAT_TextManagerObject,TEXT_SKTRAIL_WIN,2);
  Global::StoreStringInMenuStringArray(pcVar1);
                    /* added by script: "You have bested the Crusader Trail!" */
  pcVar1 = Text::TextManager::getTextStringInGroupAtOffset
                     (&DAT_TextManagerObject,TEXT_SKTRAIL_WIN,3);
  Global::StoreStringInMenuStringArray(pcVar1);
                    /* added by script: "You have bested the Crusader Extreme Trail!" */
  pcVar1 = Text::TextManager::getTextStringInGroupAtOffset
                     (&DAT_TextManagerObject,TEXT_SKTRAIL_WIN,4);
  Global::StoreStringInMenuStringArray(pcVar1);
  AppendCreditsSoundEntry(1,0);
  AppendCreditsShowImageCommand(0x29,0,0xe6,0xcb,0x150,0xa8,0,1);
  AppendCreditsTextCommand(0xf,0,0xf,1,0x192,0xea,0,1);
  AppendCreditsTextCommand(0xf,0,0xf,0,400,0xe8,0,1);
  AppendCreditsImageTransitionCommand(5,1,0x6a,0x35,4);
  AppendCreditsBinkVideoCommand(0xc,"rt_vict1.bik",0x6a,0x35,0,0);
  AppendCreditsBinkVideoWithAudioCommand("fx\\speech\\rt_anger_04.wav",3,0,100);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(4,3);
  AppendCreditsImageTransitionCommand(5,2,0x14b,0x18,4);
  AppendCreditsBinkVideoCommand(0xc,"sn_vict2.bik",0x14b,0x18,0,0);
  AppendCreditsBinkVideoWithAudioCommand("fx\\speech\\sn_add_player.wav",3,0,100);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(4,3);
  AppendCreditsImageTransitionCommand(5,3,0x22d,0x35,4);
  AppendCreditsBinkVideoCommand(0xc,"pg_taunt2.bik",0x22d,0x35,0,0);
  AppendCreditsBinkVideoWithAudioCommand("fx\\speech\\pg_add_player.wav",3,0,100);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(4,3);
  AppendCreditsImageTransitionCommand(5,4,0x280,0xdf,4);
  AppendCreditsBinkVideoCommand(0xc,"wf_anger1.bik",0x280,0xdf,0,0);
  AppendCreditsBinkVideoWithAudioCommand("fx\\speech\\wf_anger_04.wav",3,0,100);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(4,3);
  AppendCreditsImageTransitionCommand(5,5,0x22d,0x18a,4);
  AppendCreditsBinkVideoCommand(0xc,"saladin_angry.bik",0x22d,0x18a,0,0);
  AppendCreditsBinkVideoWithAudioCommand("fx\\speech\\sa_extra_01.wav",3,0,100);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(4,3);
  AppendCreditsImageTransitionCommand(5,6,0x14c,0x1b4,4);
  AppendCreditsBinkVideoCommand(0xc,"sultan_natural.bik",0x14c,0x1b4,0,0);
  AppendCreditsBinkVideoWithAudioCommand("fx\\speech\\su_congrats_01.wav",3,0,100);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(4,3);
  AppendCreditsImageTransitionCommand(5,7,0x6a,0x18a,4);
  AppendCreditsBinkVideoCommand(0xc,"richard_taunting.bik",0x6a,0x18a,0,0);
  AppendCreditsBinkVideoWithAudioCommand("fx\\speech\\ri_congrats_01.wav",3,0,100);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(4,3);
  AppendCreditsImageTransitionCommand(5,8,0x23,0xdf,4);
  AppendCreditsBinkVideoCommand(0xc,"bad_arab_taunt.bik",0x23,0xdf,0,0);
  AppendCreditsBinkVideoWithAudioCommand("fx\\speech\\ca_add_player_01.wav",3,0,100);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(4,3);
  uVar2 = 0x10;
  if (DAT_TextManagerObject.gameLanguage == GL_ITALIAN) {
    uVar2 = 0x11;
  }
  AppendCreditsTextEndCommand(0x10,0);
  AppendCreditsSoundStreamCommand(3,0);
  AppendCreditsTextCommand(0xf,1,uVar2,1,0x106,0xee,0x11a,0);
  AppendCreditsTextCommand(0xf,1,uVar2,0,0x104,0xec,0x11a,0);
  AppendCreditsSoundStreamCommand(3,1);
  AppendCreditsSoundStreamCommand(1,0x5a);
  AppendCreditsTextEndCommand(0x10,1);
  AppendCreditsSoundStreamCommand(3,1);
  AppendCreditsTextCommand(0xf,2,uVar2,1,0x106,0xee,0x11a,0);
  AppendCreditsTextCommand(0xf,2,uVar2,0,0x104,0xec,0x11a,0);
  AppendCreditsSoundStreamCommand(3,2);
  AppendCreditsSoundStreamCommand(1,0x5a);
  AppendCreditsTextEndCommand(0x10,2);
  AppendCreditsSoundStreamCommand(3,2);
  if (DAT_GameCore.currentTrailType == TT_EXTREME) {
    AppendCreditsTextCommand(0xf,4,uVar2,1,0x106,0xee,0x11a,0);
    AppendCreditsTextCommand(0xf,4,uVar2,0,0x104,0xec,0x11a,0);
    uVar2 = 4;
  }
  else {
    AppendCreditsTextCommand(0xf,3,uVar2,1,0x106,0xee,0x11a,0);
    AppendCreditsTextCommand(0xf,3,uVar2,0,0x104,0xec,0x11a,0);
    uVar2 = 3;
  }
  AppendCreditsSoundStreamCommand(3,uVar2);
  AppendCreditsSoundStreamCommand(8,1);
  AppendCreditsImageTransitionCommand(5,9,0x6a,0x35,4);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x6a,0x35,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(8,2);
  AppendCreditsImageTransitionCommand(5,9,0x14b,0x18,4);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x14b,0x18,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(8,3);
  AppendCreditsImageTransitionCommand(5,9,0x22d,0x35,4);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x22d,0x35,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(8,4);
  AppendCreditsImageTransitionCommand(5,9,0x280,0xdf,4);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x280,0xdf,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(8,5);
  AppendCreditsImageTransitionCommand(5,9,0x22d,0x18a,4);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x22d,0x18a,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(8,6);
  AppendCreditsImageTransitionCommand(5,9,0x14c,0x1b4,4);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x14c,0x1b4,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(8,7);
  AppendCreditsImageTransitionCommand(5,9,0x6a,0x18a,4);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x6a,0x18a,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsSoundStreamCommand(8,8);
  AppendCreditsImageTransitionCommand(5,9,0x23,0xdf,4);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x23,0xdf,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsImageEndCommand(0x2a,0);
  AppendCreditsTextEndCommand(0x10,3);
  AppendCreditsSegmentEndCommand();
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x6a,0x35,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x14b,0x18,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x22d,0x35,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x280,0xdf,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x22d,0x18a,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x14c,0x1b4,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x6a,0x18a,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsBinkVideoCommand(0xc,"action_jester.bik",0x23,0xdf,0,0);
  AppendCreditsSoundStreamCommand(0x18,0);
  AppendCreditsClearImageCommand();
  _HoldStrong::Rendering::TicksStartCounter();
  Global::LoadTGX_shc_back();
  return;
}


##### MenuItemRenderFunction_General_CrusadeMapAndEndscreen @ 0x004d8df0

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl _HoldStrong::UI::MenuItemRenderFunction_General_CrusadeMapAndEndscreen(int param_1,...)

{
  int yParam;
  char *textAddress;
  int xParam;
  TextAlignment alignment;
  BGR24 color;
  int fontSize;
  BOOLEnum keepOffsetX;
  int blendStrength;
  
  if (param_1 == 1000) {
    DAT_00ed2bdc = (uint)(DAT_ButtonCurrentlyInteracting != FALSE);
    MenuItemRenderFunction_General_RenderCurrentButtonWithPossibleAlphaTexOnScreenMenuSurface();
    Text::TextManager::renderNumber2
              (&DAT_TextManagerObject,DAT_SkirmishTrailRelated1,DAT_ButtonX + 0x35,
               DAT_ButtonY + 0x62,TTA_RIGHT,0xc2f0eb,0,0xf,FALSE,0);
    if (DAT_00ed2bdc != 0) {
      blendStrength = 0;
      keepOffsetX = FALSE;
      fontSize = 0x12;
      color = 0xccfaff;
      yParam = DAT_WindowAndDirectDraw.mainMenuBorderHeight + 0x247;
      alignment = TTA_CENTER;
      xParam = DAT_WindowAndDirectDraw.mainMenuBorderWidth + 400;
                    /* added by script: "Skip Current Mission" */
      textAddress = Text::TextManager::getTextStringInGroupAtOffset
                              (&DAT_TextManagerObject,TEXT_CHEATS,
                               (uint)(DAT_SkirmishTrailRelated1 < 1));
      Text::TextManager::renderTextToScreen
                (&DAT_TextManagerObject,textAddress,xParam,yParam,alignment,color,fontSize,
                 keepOffsetX,blendStrength);
    }
  }
  else if (((param_1 == 10) || (param_1 == 0xb)) || (param_1 == 99)) {
    MenuItemRenderFunction_General_RenderCurrentButtonWithPossibleAlphaTexOnScreenMenuSurface();
    return;
  }
  return;
}


##### ComputePlayerRanking @ 0x0044b680

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* variable _playerPointsArray made by gynt
   decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __cdecl _HoldStrong::Global::ComputePlayerRanking(int playerID)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int _highestPointsUnk;
  undefined4 _deadPlayerList [10];
  int _playerPointsArray [9] [2];
  
  _playerPointsArray[0][0] = 0;
  _playerPointsArray[1][0] = 0;
  _playerPointsArray[2][0] = 0;
  _playerPointsArray[3][0] = 0;
  _playerPointsArray[4][0] = 0;
  _playerPointsArray[5][0] = 0;
  _playerPointsArray[6][0] = 0;
  _playerPointsArray[7][0] = 0;
  _playerPointsArray[8][0] = 0;
  iVar4 = 0;
  iVar3 = 1;
  do {
    if (DAT_GameSynchronyState.finalResults.active[iVar3] != 0) {
      _playerPointsArray[iVar4][0] = iVar3;
      iVar1 = Map::Units::UnitsState::getAliveLordForPlayer(&DAT_UnitsState,iVar3);
      if (iVar1 == 0) {
        if (iVar3 == playerID) {
          return 0;
        }
        _deadPlayerList[iVar3] = 1;
        _playerPointsArray[iVar4][1] = 0;
      }
      else {
        iVar1 = ComputePlayerPoints1(iVar3);
        _playerPointsArray[iVar4][1] = iVar1;
      }
      iVar4 = iVar4 + 1;
    }
    iVar3 = iVar3 + 1;
  } while (iVar3 < 9);
  iVar3 = 0;
  if (0 < iVar4) {
    do {
      iVar1 = -1;
      iVar2 = 0;
      do {
        if ((_playerPointsArray[iVar2][0] != 0) &&
           ((iVar1 == -1 || (_highestPointsUnk < _playerPointsArray[iVar2][1])))) {
          _highestPointsUnk = _playerPointsArray[iVar2][1];
          iVar1 = iVar2;
        }
        iVar2 = iVar2 + 1;
      } while (iVar2 < iVar4);
      if (iVar1 < 0) {
        return 0;
      }
      if (_playerPointsArray[iVar1][0] == playerID) {
        return iVar3 + 1;
      }
      iVar3 = iVar3 + 1;
      _playerPointsArray[iVar1][0] = 0;
    } while (iVar3 < iVar4);
  }
  return 0;
}


