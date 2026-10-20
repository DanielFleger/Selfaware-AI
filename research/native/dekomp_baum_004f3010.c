// ================= damageTreeAndTriggerDeathIfDepleted @ 004f3010 =================

/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

undefined4 __thiscall
_HoldStrong::Map::LandscapeState::damageTreeAndTriggerDeathIfDepleted
          (LandscapeState *this,int treeID,undefined4 param_2,int param_3)

{
  undefined2 *puVar1;
  
  if (((DAT_LandscapeState.trees[treeID].uid == param_3) &&
      (DAT_LandscapeState.trees[treeID].zeroUpTo2 == 0)) &&
     (puVar1 = &DAT_LandscapeState.trees[treeID].stageRelated1, *puVar1 = *puVar1 + (short)param_2,
     (short)DAT_LandscapeState.trees[treeID].stageRelated1 < 1)) {
    DAT_LandscapeState.trees[treeID].stageRelated1 = 0;
    DAT_LandscapeState.trees[treeID].zeroUpTo2 = 1;
    DAT_LandscapeState.trees[treeID].animationFrameIndex = 0;
    TileMapState::applyTreeBrushToLogicalLayer(&DAT_TileMapState,treeID,1);
    return 1;
  }
  return 0;
}



