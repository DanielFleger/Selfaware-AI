// ================= ClickDestroyBuilding @ 00481F40 =================

/* WARNING: Enum "DPSEND_EnumInt": Some values do not have unique names */
/* WARNING: Enum "DPERRInt": Some values do not have unique names */
/* WARNING: Enum "MappersEnum": Some values do not have unique names */
/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

void _HoldStrong::Commands::ClickDestroyBuilding(void)

{
  int iVar1;
  int iVar2;
  short local_4 [2];
  
  DAT_GameSynchronyState.DAT_CommandSize = 7;
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_SCHEDULE_AND_SEND) {
                    /* write parameter in gamecommand entry in events queue */
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam0,2,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam1,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam2,4,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_SERIALIZE_INTO_PARAM_1);
    return;
  }
  if (DAT_GameSynchronyState.DAT_CommandActionPlan == GCS_EXECUTE) {
                    /* read the parameters back into the variables */
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,local_4,2,GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,
               GCPRW_DESERIALIZE_FROM_PARAM1);
    DAT_GameSynchronyState.DAT_GameCommandParam0 = (int)local_4[0];
    DAT_GameSynchronyState.DAT_GameCommandParam1 = 0;
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam1,1,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    Synchrony::GameSynchronyState::serializeOrDeserializeCommandParameter
              (&DAT_GameSynchronyState,&DAT_GameSynchronyState.DAT_GameCommandParam2,4,
               GCPL_DYNAMIC_COMMAND_DATA_ADDRESS,GCPRW_DESERIALIZE_FROM_PARAM1);
    iVar1 = DAT_GameSynchronyState.DAT_GameCommandParam0;
    if (DAT_GameSynchronyState.DAT_GameCommandParam0 < 1) {
      if (*(int *)(&DAT_0053f088 + DAT_GameSynchronyState.DAT_GameCommandParam0 * -0x14 +
                  (int)DAT_TileMapState.directionTranslationMatrix) ==
          DAT_GameSynchronyState.DAT_GameCommandParam2) {
        Map::TileMapState::destroyPitchDitch
                  (&DAT_TileMapState,-DAT_GameSynchronyState.DAT_GameCommandParam0);
        return;
      }
    }
    else if (DAT_BuildingsState.buildings[DAT_GameSynchronyState.DAT_GameCommandParam0].uid ==
             DAT_GameSynchronyState.DAT_GameCommandParam2) {
      iVar2 = Map::Buildings::BuildingsState::findParticularBuilding
                        (&DAT_BuildingsState,
                         (int)DAT_BuildingsState.buildings
                              [DAT_GameSynchronyState.DAT_GameCommandParam0].owner,
                         (int)(short)DAT_BuildingsState.buildings
                                     [DAT_GameSynchronyState.DAT_GameCommandParam0].x,
                         (int)(short)DAT_BuildingsState.buildings
                                     [DAT_GameSynchronyState.DAT_GameCommandParam0].y,
                         DAT_BuildingsState.buildings[DAT_GameSynchronyState.DAT_GameCommandParam0].
                         widthOrHeight,BT_DRAWBRIDGE,0);
      if (iVar2 != 0) {
        DAT_TileMapState.showNoRubbleWhenDestroyingBuilding = 1;
        Map::Buildings::BuildingsState::giveBackResourceForDestroyedBuilding
                  (&DAT_BuildingsState,iVar2,DAT_GameSynchronyState.protocolInvokerPlayerID,
                   DAT_GameSynchronyState.DAT_GameCommandParam1);
        Map::Buildings::BuildingsState::destroyBuilding(&DAT_BuildingsState,iVar2);
        iVar2 = Map::Buildings::BuildingsState::findParticularBuilding
                          (&DAT_BuildingsState,(int)DAT_BuildingsState.buildings[iVar1].owner,
                           (int)(short)DAT_BuildingsState.buildings[iVar1].x,
                           (int)(short)DAT_BuildingsState.buildings[iVar1].y,
                           DAT_BuildingsState.buildings[iVar1].widthOrHeight,BT_DRAWBRIDGE,iVar2);
        if (iVar2 != 0) {
          DAT_TileMapState.showNoRubbleWhenDestroyingBuilding = 1;
          Map::Buildings::BuildingsState::giveBackResourceForDestroyedBuilding
                    (&DAT_BuildingsState,iVar2,DAT_GameSynchronyState.protocolInvokerPlayerID,
                     DAT_GameSynchronyState.DAT_GameCommandParam1);
          Map::Buildings::BuildingsState::destroyBuilding(&DAT_BuildingsState,iVar2);
        }
      }
      DAT_TileMapState.showNoRubbleWhenDestroyingBuilding = 1;
      if (DAT_BuildingsState.buildings[iVar1].field230_0x288 == 0) {
        Map::Buildings::BuildingsState::giveBackResourceForDestroyedBuilding
                  (&DAT_BuildingsState,DAT_GameSynchronyState.DAT_GameCommandParam0,
                   DAT_GameSynchronyState.protocolInvokerPlayerID,
                   DAT_GameSynchronyState.DAT_GameCommandParam1);
      }
      if ((iVar1 != 0) &&
         (DAT_BuildingsState.buildings[iVar1].owner == DAT_GameSynchronyState.currentPlayerSlotID))
      {
        switch(DAT_BuildingsState.buildings[iVar1].buildingType) {
        case BT_GATEHOUSELARGE:
        case BT_GATEHOUSESMALL:
        case BT_TOWER1:
        case BT_TOWER2:
        case BT_TOWER3:
        case BT_TOWER4:
        case BT_TOWER5:
          Audio::SFX::SFXState::playSFXAtLocation
                    (&DAT_SFXState,(int)(short)DAT_BuildingsState.buildings[iVar1].x,
                     (int)(short)DAT_BuildingsState.buildings[iVar1].y,FX_TOWER_SMASH);
          break;
        default:
                    /* Plays building destroy sound */
          Audio::SFX::SFXState::playWAVSFX(&DAT_SFXState,"buildingwreck_01.wav");
        }
      }
      Map::Buildings::BuildingsState::destroyBuilding
                (&DAT_BuildingsState,DAT_GameSynchronyState.DAT_GameCommandParam0);
    }
  }
  return;
}



