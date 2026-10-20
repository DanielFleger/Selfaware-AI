// ================= updateRightDragCameraControl @ 0x00470bc0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Input::MouseState::updateRightDragCameraControl(MouseState *this)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  DWORD DVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined8 uVar8;
  
  iVar6 = DAT_MouseState.mapOrientationCopy3;
  DAT_MouseState.mouseBasedEvent = 0;
  DAT_MouseState.field44_0x17c = 0;
  DAT_MouseState.field43_0x178 = 0;
  DAT_MouseState.field59_0x1b8 = 0;
  DVar4 = timeGetTime();
  uVar3 = DAT_MouseState.storedScreenSpaceY;
  uVar2 = DAT_MouseState.screenSpaceY;
  uVar1 = DAT_MouseState.screenSpaceX;
  DAT_MouseState.field56_0x1ac = DVar4 - DAT_MouseState.currentTime2;
  DAT_MouseState.field42_0x174 = DAT_MouseState.field42_0x174 + 1;
  if (DAT_MouseState.field57_0x1b0 < DAT_MouseState.field56_0x1ac) {
    DAT_MouseState.field58_0x1b4 = 0;
    DAT_MouseState.field51_0x198 = 0;
    DAT_MouseState.field52_0x19c = 0;
    DAT_MouseState.currentTime2 = DVar4;
  }
  DAT_MouseState.currentTime3 = DVar4;
  uVar8 = Map::Navigation::DirectionAlgorithmState::getMouseVectorLengthBasedOnDirection
                    (DAT_MouseState.storedScreenSpaceX,DAT_MouseState.storedScreenSpaceY,
                     DAT_MouseState.screenSpaceX,DAT_MouseState.screenSpaceY,4);
  iVar7 = (int)((ulonglong)uVar8 >> 0x20);
  iVar5 = (int)uVar8;
  if ((iVar5 < 0xc) || (DAT_MouseState.field61_0x1c0 != 0)) {
    DAT_MouseState.field43_0x178 = 0;
  }
  else if (iVar5 < 0x1c) {
    DAT_MouseState.field43_0x178 = iVar5 / 2;
    DAT_MouseState.mouseBasedEvent = 2;
  }
  else {
    DAT_MouseState.field43_0x178 = 0x28;
    DAT_MouseState.mouseBasedEvent = iVar7;
    DAT_MouseState.field59_0x1b8 = iVar7;
    DAT_MouseState.field60_0x1bc = iVar7;
    DAT_MouseState.field62_0x1c4 = iVar7;
    DAT_MouseState.field63_0x1c8 = iVar7;
  }
  uVar8 = Map::Navigation::DirectionAlgorithmState::getMouseVectorLengthBasedOnDirection
                    (DAT_MouseState.storedScreenSpaceX,uVar3,uVar1,uVar2,0);
  if (((int)uVar8 < 0x16) || (DAT_MouseState.field60_0x1bc != 0)) {
    DAT_MouseState.field42_0x174 = 0;
    DAT_MouseState.field58_0x1b4 = 0;
    if ((DAT_MouseState.field59_0x1b8 == 2) || ((int)uVar8 < 0x16)) {
      DAT_MouseState.currentTime2 = DVar4;
    }
  }
  else {
    DAT_MouseState.field61_0x1c0 = 1;
    DAT_MouseState.field62_0x1c4 = 1;
    DAT_MouseState.field63_0x1c8 = 1;
    DAT_MouseState.field59_0x1b8 = 2;
    DAT_MouseState.field57_0x1b0 = 0x5dc;
    if (DAT_MouseState.field58_0x1b4 == 0) {
      DAT_MouseState.field58_0x1b4 = 1;
      iVar6 = DAT_MouseState.mapOrientationCopy3 + 6;
      if (7 < iVar6) {
        iVar6 = DAT_MouseState.mapOrientationCopy3 + -2;
      }
      DAT_MouseState.field47_0x188 = 0;
    }
    else {
      DAT_MouseState.field47_0x188 = 8;
    }
  }
  if (iVar6 != DAT_MouseState.mapOrientationCopy2) {
                    /* plan a map rotation */
    DAT_MouseState.mouseBasedEvent = 3;
    DAT_MouseState.mapOrientationCopy2 = iVar6;
    DAT_MouseState.mapOrientationCopy3 = iVar6;
  }
  uVar8 = Map::Navigation::DirectionAlgorithmState::getMouseVectorLengthBasedOnDirection
                    ((int)((ulonglong)uVar8 >> 0x20),uVar3,uVar1,uVar2,2);
  if (((int)uVar8 < 0x37) || (DAT_MouseState.field63_0x1c8 != 0)) {
    DAT_MouseState.field42_0x174 = 0;
    if (DAT_MouseState.field59_0x1b8 == 3) {
      DAT_MouseState.currentTime2 = DVar4;
    }
  }
  else {
    DAT_MouseState.field61_0x1c0 = 1;
    DAT_MouseState.field62_0x1c4 = 1;
    DAT_MouseState.field60_0x1bc = 1;
    DAT_MouseState.field57_0x1b0 = 2000;
    DAT_MouseState.field59_0x1b8 = 3;
    if (DAT_MouseState.field51_0x198 != 2) {
      DAT_MouseState.mouseBasedEvent = 4;
      DAT_MouseState.field51_0x198 = 1;
    }
  }
  iVar6 = Map::Navigation::DirectionAlgorithmState::getMouseVectorLengthBasedOnDirection
                    ((int)((ulonglong)uVar8 >> 0x20),uVar3,uVar1,uVar2,6);
  if ((iVar6 < 0x37) || (DAT_MouseState.field62_0x1c4 != 0)) {
    DAT_MouseState.field42_0x174 = 0;
    if (DAT_MouseState.field59_0x1b8 == 4) {
      DAT_MouseState.currentTime2 = DVar4;
    }
  }
  else {
    DAT_MouseState.field61_0x1c0 = 1;
    DAT_MouseState.field63_0x1c8 = 1;
    DAT_MouseState.field60_0x1bc = 1;
    DAT_MouseState.field57_0x1b0 = 2000;
    DAT_MouseState.field59_0x1b8 = 4;
    if (DAT_MouseState.field52_0x19c != 2) {
      DAT_MouseState.mouseBasedEvent = 5;
      DAT_MouseState.field52_0x19c = 1;
      return;
    }
  }
  return;
}



// ================= hideOrUnhideUI @ 0x00471aa0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Game::GameCore::hideOrUnhideUI(GameCore *this)

{
  if (((DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU) ||
      (DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_LANDSCAPING)) &&
     (DAT_MouseState.selectionBoxMode == 0)) {
    if ((DAT_GameCore.activeMenuTab.tabType != BASMTT_SIEGETENT_SIEGETOWER) &&
       (DAT_GameCore.activeMenuTab.tabType != BASMTT_SIEGETENT_SHIELD)) {
      if (DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU) {
        if (DAT_GameCore.activeMenuTab.tabType == BASMTT_SIEGETENT_BATTERINGRAM) {
          DAT_GameCore.buildmenuMenuTabToSwitchTo.tabType = BASMTT_SIEGETENT_SHIELD;
          switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
          return;
        }
        setTabToSwitchTo(&DAT_GameCore);
        DAT_GameCore.buildmenuMenuTabToSwitchTo.tabType = BASMTT_SIEGETENT_SIEGETOWER;
      }
      if (DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_LANDSCAPING) {
        DAT_GameCore.landscapingmenuMenuTabToSwitchTo = 0x3c;
      }
      switchToMenuView(&DAT_GameCore,DAT_GameCore.currentMenuViewType,0);
      return;
    }
    if (DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU) {
      if (DAT_GameCore.activeMenuTab.tabType == BASMTT_SIEGETENT_SHIELD) {
        DAT_GameCore.buildmenuMenuTabToSwitchTo.tabType = BASMTT_SIEGETENT_BATTERINGRAM;
        switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
        return;
      }
      swapBuildMenuTab(&DAT_GameCore);
    }
    if (DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_LANDSCAPING) {
      DAT_GameCore.landscapingmenuMenuTabToSwitchTo =
           DAT_GameCore.secondaryActiveMenuTabToSwitchTo.tabType;
    }
    if (DAT_GameCore.buildmenuMenuTabToSwitchTo.tabType == BASMTT_SIEGETENT_SIEGETOWER) {
      if (DAT_GameCore.currentMenuViewType == MVT_BUILD_MENU) {
        DAT_GameCore.buildmenuMenuTabToSwitchTo.tabType = BASMTT_HUNTERSHUT;
        switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
        return;
      }
      if (DAT_GameCore.currentMenuViewType == MVT_MAP_EDITOR_LANDSCAPING) {
        DAT_GameCore.landscapingmenuMenuTabToSwitchTo = 0xe7;
      }
    }
    switchToMenuView(&DAT_GameCore,DAT_GameCore.currentMenuViewType,0);
    return;
  }
  if (DAT_GameCore.currentMenuViewType == MVT_BUILDING_AND_STATUS_MENU) {
    DAT_GameCore.secondaryActiveMenuTabToSwitchTo = DAT_GameCore.buildmenuMenuTabToSwitchTo;
    DAT_GameCore.buildmenuMenuTabToSwitchTo.tabType = BASMTT_SIEGETENT_SIEGETOWER;
    switchToMenuView(&DAT_GameCore,MVT_BUILD_MENU,0);
  }
  return;
}



// ================= toggleFlatView @ 0x004f70b0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall _HoldStrong::Map::TileMapState::toggleFlatView(TileMapState *this,int param_1)

{
  if (param_1 != DAT_TileMapState.flatViewToggleValue1) {
    DAT_TileMapState.flatViewToggleValue1 = param_1;
    DAT_TileMapState.flatViewToggleValue2 = param_1;
  }
  return;
}



// ================= setMapRotation @ 0x004f70e0 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::TileMapState::setMapRotation(TileMapState *this,undefined4 newRotation)

{
  DAT_TileMapState.DAT_FutureMapOrientation = newRotation;
  return;
}



// ================= resetupViewport @ 0x004e7770 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Rendering::ViewportRenderState::resetupViewport(ViewportRenderState *this,int zoomUnk)

{
  int iVar1;
  ViewportRenderState *this_00;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_ViewportRenderState.viewportState.viewportY +
          DAT_ViewportRenderState.viewportState.mbr_0xb0 * 8;
  iVar3 = DAT_ViewportRenderState.viewportState.mbr_0xac * 0x20 +
          DAT_ViewportRenderState.viewportState.viewportX;
  DAT_ViewportRenderState.viewportState.isZoomedOutUnk = zoomUnk;
  if (((DAT_GameCore.currentMenuViewType != MVT_BUILD_MENU) &&
      (DAT_GameCore.currentMenuViewType != MVT_MAP_EDITOR_LANDSCAPING)) ||
     ((iVar2 = DAT_WindowAndDirectDraw.resolutionY,
      DAT_GameCore.activeMenuTab.tabType != BASMTT_SIEGETENT_SIEGETOWER &&
      (DAT_GameCore.activeMenuTab.tabType != BASMTT_SIEGETENT_SHIELD)))) {
    iVar2 = DAT_WindowAndDirectDraw.resolutionY + -0x80;
  }
  setupViewport(0,0,DAT_WindowAndDirectDraw.resolutionX,iVar2);
  (this_00->viewportState).viewportX = iVar3 + (this_00->viewportState).mbr_0xac * -0x20;
  (this_00->viewportState).viewportY = iVar1 + (this_00->viewportState).mbr_0xb0 * -8;
  setViewportBasedOnMapSize(this_00);
  return;
}



// ================= focusOnCoordinate @ 0x004e8ca0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Rendering::ViewportRenderState::focusOnCoordinate
          (ViewportRenderState *this,int x,int y)

{
  focusOnTile(&DAT_ViewportRenderState,DAT_ViewportRenderState.translationMatrix[y].addXgetTile + x)
  ;
  return;
}



