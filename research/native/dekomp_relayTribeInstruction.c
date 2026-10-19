// ================= relayTribeInstruction @ 005371e0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __thiscall
_HoldStrong::Map::Units::UnitsState::relayTribeInstruction
          (UnitsState *this,int tribeID,UnitInstructionType instructionType,int targetID_1,
          int targetID_2,int param_5)

{
  TribesState::giveTribeAnInstruction
            (&DAT_TribesState,tribeID,instructionType,targetID_1,targetID_2,param_5);
  return;
}



