// ================= isTreeAdult @ 004f2fe0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::LandscapeState::isTreeAdult(LandscapeState *this,int treeID,int treeUID)

{
  if (DAT_LandscapeState.trees[treeID].uid != treeUID) {
    return FALSE;
  }
  return (uint)(0 < (short)DAT_LandscapeState.trees[treeID].treeAdultHoodStageRelatedVisual3);
}



