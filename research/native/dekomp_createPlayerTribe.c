// ================= createPlayerTribe @ 00522950 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __thiscall
_HoldStrong::Map::Units::TribesState::createPlayerTribe
          (TribesState *this,int playerID,undefined4 one,int tribeID)

{
  IO::LowLevelMemory::fillMemory_ByteValue
            (&DAT_LowLevelMemory,0x334,'\0',DAT_TribesState.tribes + tribeID);
  DAT_TribesState.tribes[tribeID].tribeState = 2;
  DAT_TribesState.tribes[tribeID].owner = playerID;
  DAT_TribesState.tribes[tribeID].uid = DAT_GameCore.uniqueGameObjectTracker;
  DAT_GameCore.uniqueGameObjectTracker = DAT_GameCore.uniqueGameObjectTracker + 1;
  DAT_TribesState.tribes[tribeID].tribeType = 0;
  DAT_TribesState.tribes[tribeID].field19_0x1c = 0;
  DAT_TribesState.tribes[tribeID].field20_0x1e = 0;
  DAT_TribesState.tribes[tribeID].tribeBehaviorType = 0;
  DAT_TribesState.tribes[tribeID].field30_0x30 = 0;
  DAT_TribesState.tribes[tribeID].selectionTargetUnitID = 0;
  DAT_TribesState.tribes[tribeID].size = 0;
  return tribeID;
}



