// ================= selectClosestTree @ 004f3610 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::LandscapeState::selectClosestTree
          (LandscapeState *this,int xPosition,int yPosition,int param_3)

{
  int iVar1;
  int iVar2;
  TreeTypeShort *pTVar3;
  int _selectedTreeID;
  
  iVar1 = 1;
  iVar2 = 1000;
  _selectedTreeID = 0;
  if (1 < DAT_LandscapeState.maxTreeCount) {
    pTVar3 = &DAT_LandscapeState.trees[1].treeType;
    do {
      if (((pTVar3[-1] == 2) && (*pTVar3 == TT_APPLEUnk)) && (*(int *)(pTVar3 + 0x1d) == 3)) {
        Navigation::DirectionAlgorithmState::setAxisBasedDistanceResult
                  (&DAT_DirectionAlgorithmState,xPosition,yPosition,(int)(short)pTVar3[0xe],
                   (int)(short)pTVar3[0xf]);
        if (DAT_DirectionAlgorithmState.distanceHigh < iVar2) {
          iVar2 = DAT_DirectionAlgorithmState.distanceHigh;
          _selectedTreeID = iVar1;
        }
      }
      iVar1 = iVar1 + 1;
      pTVar3 = pTVar3 + 0x4e;
    } while (iVar1 < DAT_LandscapeState.maxTreeCount);
    if ((iVar2 < 0x1e) && (0 < _selectedTreeID)) {
      DAT_LandscapeState.x = (int)(short)DAT_LandscapeState.trees[_selectedTreeID].xPosition;
      DAT_LandscapeState.y = (int)(short)DAT_LandscapeState.trees[_selectedTreeID].yPosition;
      if (param_3 == 0) {
        DAT_LandscapeState.x = DAT_LandscapeState.x + -2;
        return _selectedTreeID;
      }
      if (param_3 == 1) {
        DAT_LandscapeState.y = DAT_LandscapeState.y + 2;
        return _selectedTreeID;
      }
      if (param_3 == 2) {
        DAT_LandscapeState.x = DAT_LandscapeState.x + 2;
        return _selectedTreeID;
      }
      DAT_LandscapeState.y = DAT_LandscapeState.y + -2;
      return _selectedTreeID;
    }
  }
  return 0;
}



