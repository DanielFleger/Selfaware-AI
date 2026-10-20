// ================= triggerLoweredView @ 0x004f6fd0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Map::TileMapState::triggerLoweredView(TileMapState *this,int param_1)

{
  UnitTypeShort UVar1;
  int iVar2;
  UnitTypeShort *pUVar3;
  int iVar4;
  
  iVar4 = 2;
  if (DAT_TileMapState.flatViewToggleValue2 == 0) {
    iVar4 = param_1;
  }
  if ((((DAT_TileMapState.refreshCertainTileMap_old != iVar4) &&
       (DAT_TileMapState.counter1 = 0, DAT_TileMapState.refreshCertainTileMap = iVar4, iVar4 == 3))
      && (DAT_GameCore.gamePausedLogical == 0)) && (iVar4 = 1, 1 < (int)DAT_UnitsState.maxUnitCount)
     ) {
    pUVar3 = &DAT_UnitsState.units[1].unitType;
    do {
      if ((pUVar3[-1] != ULS_INVISIBLE) &&
         (((((UVar1 = *pUVar3, UVar1 == UT_DRUNK || (UVar1 == UT_RABBIT)) ||
            ((UVar1 == UT_HUNTERDOG || ((UVar1 == UT_JESTER || (UVar1 == UT_CHICKEN)))))) ||
           (UVar1 == UT_CHILD)) || ((UVar1 == UT_JUGGLER || (UVar1 == UT_FIREEATER)))))) {
        iVar2 = ((int)(short)pUVar3[0x17] + (int)(short)pUVar3[0x16]) / 10;
        if (0xe < iVar2) {
          iVar2 = 0xe;
        }
        *(char *)(pUVar3 + -6) = (char)iVar2;
        *(undefined1 *)((int)pUVar3 + -0xb) = 0;
      }
      iVar4 = iVar4 + 1;
      pUVar3 = pUVar3 + 0x248;
    } while (iVar4 < (int)DAT_UnitsState.maxUnitCount);
  }
  return;
}



// ================= getAreWeInAInGameMenu @ 0x0046bb60 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall _HoldStrong::Game::GameCore::getAreWeInAInGameMenu(GameCore *this)

{
  if (((DAT_GameCore.currentMenuViewType != MVT_MAP_EDITOR_LANDSCAPING) &&
      (DAT_GameCore.currentMenuViewType != MVT_BUILD_MENU)) &&
     (DAT_GameCore.currentMenuViewType != MVT_BUILDING_AND_STATUS_MENU)) {
    return FALSE;
  }
  return TRUE;
}



