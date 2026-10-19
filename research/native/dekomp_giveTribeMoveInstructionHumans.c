// ================= giveTribeMoveInstructionHumans @ 00537070 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::UnitsState::giveTribeMoveInstructionHumans
          (UnitsState *this,int tribeID,uint x,uint y,int rallyBool,
          MatchSpeedInstructionEnum speedMatching)

{
  short *psVar1;
  
  psVar1 = &DAT_TribesState.tribes[tribeID].freeUnitSpeeds;
  *psVar1 = 0;
  if ((char)speedMatching < '\0') {
    speedMatching = speedMatching & 0xffffff7f;
    *psVar1 = 1;
  }
  TribesState::giveTribeMoveInstruction(&DAT_TribesState,tribeID,x,y,rallyBool,1,speedMatching);
  return;
}



