// ================= unitIsSelectedByPlayer @ 00522550 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

BOOLEnum __thiscall
_HoldStrong::Map::Units::TribesState::unitIsSelectedByPlayer(TribesState *this,uint tribeID)

{
  uint uVar1;
  
  uVar1 = tribeID & 0x8000000f;
  if ((int)uVar1 < 0) {
    uVar1 = (uVar1 - 1 | 0xfffffff0) + 1;
  }
  return (uint)((DAT_UnitSelectionDefinedData.DAT_BitMaskHelper[uVar1] &
                *(ushort *)
                 (DAT_UnitsState.DAT_SelectedUnitsBitFlags +
                 ((int)(tribeID + ((int)tribeID >> 0x1f & 0xfU)) >> 4) * 2)) != 0);
}



