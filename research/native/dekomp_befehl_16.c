// ================= MakeUnitSelection @ 00480E60 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Commands::MakeUnitSelection(void)

{
  DAT_GameSynchronyState.DAT_CommandSize = 0x192;
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_SCHEDULE_AND_SEND) {
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,DAT_UnitsState.DAT_SelectedUnitsBitFlags,400,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    return;
  }
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_EXECUTE) {
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,DAT_UnitsState.DAT_SelectedUnitsBitFlags,400,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    DAT_GameSynchronyState.DAT_GameCommandParam0 = 0;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    Map::Units::UnitsState::playerMakeUnitSelection
              (&DAT_UnitsState,DAT_GameSynchronyState.protocolInvokerPlayerID,
               DAT_GameSynchronyState.DAT_GameCommandParam0);
  }
  return;
}



