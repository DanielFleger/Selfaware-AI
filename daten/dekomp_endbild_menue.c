##### Constructor_Menu_MissionFinishedTransition @ 0x0059ad10

/* WARNING: Enum "MappersEnum": Some values do not have unique names */

void _HoldStrong::Global::Init::Constructor_Menu_MissionFinishedTransition(void)

{
  UI::Menu::Constructor_Menu
            (&Menu_MissionFinishedTransition,
             DAT_RenderingDefinedData.MenuItems_MissionFinishedTransition);
  return;
}


##### Constructor_MenuView_MissionFinishedTransition @ 0x0059a640

void _HoldStrong::Global::Init::Constructor_MenuView_MissionFinishedTransition(void)

{
  UI::MenuView::Constructor_MenuView
            (&MenuView_MissionFinishedTransition,MVT_MISSION_FINISHED_TRANSITION,
             UI::MenuView_MissionFinishedTransition_Prepare,
             UI::MenuView_General_DoInitial_DefaultMainMenuStructure,
             UI::MenuView_MissionFinishedTransition_DoEveryFrame);
  OS::_atexit(Destructor_MenuView_MissionFinishedTransition);
  return;
}


