// ================= SetBuildingProductionType @ 004652a0 =================

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void __cdecl
_HoldStrong::Global::SetBuildingProductionType
          (undefined4 playerID,int buildingID,ushort producedItemType,int buildingUID)

{
  if (DAT_BuildingsState.buildings[buildingID].uid == buildingUID) {
    DAT_BuildingsState.buildings[buildingID].producedItemType = producedItemType;
  }
  return;
}



