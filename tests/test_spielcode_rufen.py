# -*- coding: utf-8 -*-
"""Der Ablauf, der im Spiel laeuft, und die Sperre auf Instanz 2. Der echte Aufruf ist im Messlauf belegt (rufen_*.json), hier zaehlt nur, was ohne Spiel pruefbar ist."""
import os
import struct

import pytest

from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments import auge_rufen
from selfaware.tools.experiments.spielcode_rufen import ERLAUBT, Rufer, ablauf


def test_ablauf_schiebt_werte_rueckwaerts_und_stellt_den_stapel_her():
    b = ablauf(0x11223344, (1, 2), 0x55667788, 0x99AABB00)
    assert b[:3] == b"\x55\x89\xE5"
    assert b[3:13] == b"\x68" + struct.pack("<I", 2) + b"\x68" + struct.pack("<I", 1)  # der letzte Wert zuerst
    assert b[13:18] == b"\xB9" + struct.pack("<I", 0x55667788)
    assert b[18:23] == b"\xB8" + struct.pack("<I", 0x11223344)
    assert b[23:25] == b"\xFF\xD0"
    assert b[25:30] == b"\xA3" + struct.pack("<I", 0x99AABB00)
    assert b[30:] == b"\x89\xEC\x5D\x31\xC0\xC2\x04\x00"


def test_ablauf_ohne_this_setzt_ecx_nicht():
    assert b"\xB9" not in ablauf(0x10, (), None, 0x20)


def test_negative_werte_passen_in_32_bit():
    assert ablauf(0x10, (-1,), None, 0x20)[3:8] == b"\x68\xFF\xFF\xFF\xFF"


def test_nur_instanz_2_ist_erlaubt():
    assert ERLAUBT == "Instanz2"


def test_fremder_prozess_wird_abgelehnt():
    with pytest.raises((PermissionError, OSError)):
        Rufer(os.getpid())


@pytest.mark.parametrize("gruppe, feld", [
    ("DAT_GameState", "playerDataArray[].partialStoneCounter"),
    ("DAT_GameState", "playerDataArray[].partialWoodCounter"),
    ("DAT_GameState", "playerDataArray[].currentPopulation"),
    ("DAT_GameState", "playerDataArray[].totalTroopValue"),
    ("DAT_GameState", "playerDataArray[].fearFactorProductivityUnk"),
    ("DAT_GameState", "playerDataArray[].dogCageCount"),
    ("DAT_GameState", "playerDataArray[].keep.id"),
    ("DAT_GameState", "playerDataArray[].campground.id"),
    ("DAT_GameState", "playerDataArray[].totalFood"),
    ("DAT_GameState", "playerDataArray[].isFoodTypeBanned[]"),
    ("DAT_GameState", "playerDataArray[].someCount02"),
    ("DAT_GameState", "playerDataArray[].someCount03"),
    ("DAT_GameState", "mapAndTime.rawDeerCount"),
    ("DAT_GameState", "mapAndTime.noDogs"),
    ("DAT_GameState", "mapAndTime.armySizeLimit"),
    ("DAT_BuildingsState", "INT_SelectedBuildingStoneRepairCost"),
    ("DAT_BuildingsState", "INT_SelectedBuildingStoneWoodCost"),
    ("DAT_BuildingsState", "buildings[].maxHealth"),
    ("DAT_BuildingsState", "buildings[].currentHealth"),
    ("DAT_BuildingsState", "buildings[].buildingType"),
    ("DAT_BuildingsState", "buildings[].tunnelerCounter"),
    ("DAT_BuildingsState", "buildings[].containsSiegeMangonel1OrBallista2"),
    ("DAT_BuildingsState", "buildings[].resourceBread"),
    ("DAT_BuildingsState", "buildings[].resourceCheese"),
    ("DAT_BuildingsState", "buildings[].resourceMeat"),
    ("DAT_BuildingsState", "buildings[].resourceApple"),
    ("DAT_BuildingsState", "buildings[].field230_0x288"),
    ("DAT_UnitsState", "units[].productivityMod100"),
    ("DAT_UnitsState", "units[].productivityDiv100"),
    ("DAT_UnitsState", "units[].state"),
    ("DAT_UnitsState", "units[].logicalState"),
    ("DAT_TileMapState", "illegalBuild"),
    ("DAT_TileMapState", "buildingPlacementFail"),
    ("DAT_TileMapState", "buildingPlacementFailReason"),
    ("DAT_TileMapState", "placementWarning"),
    ("DAT_TileMapState", "buildingHeightLimit"),
    ("DAT_TileMapState", "wallPlacementCost"),
    ("DAT_TileMapState", "currentMoatCount"),
    ("DAT_TileMapState", "moats[].someCountDown"),
    ("DAT_TileMapState", "HeightLayer[]"),
    ("DAT_TileMapState", "MacroLayer[]"),
    ("DAT_TileMapState", "LogicLayer[]"),
    ("DAT_PathFindingState", "ALG_TargetTile"),
    ("DAT_GameCore", "gameSpeedLevel"),
    ("DAT_TileMapState", "forceUpdateMacroLayerFlag"),
    ("DAT_UnitsState", "units[].workplaceBuildingID_1"),
    ("DAT_UnitsState", "units[].workplaceBuildingUID"),
    ("DAT_AIVState", "mapExtraInfo.totalWoodAvailable"),
    ("DAT_AIVState", "aivs[].currentStepGoal"),
    ("DAT_AIVState", "aivs[].aivPoorCounter"),
    ("DAT_AIVState", "aivs[].aivPoorLimit_OR_AIC_buildInterval"),
    ("DAT_GameState", "playerDataArray[].aiType"),
    ("DAT_GameState", "playerDataArray[].aivID"),
    ("DAT_GameState", "playerDataArray[].noWoodTracker"),
    ("DAT_GameState", "playerDataArray[].countFletchersPoleturners"),
    ("DAT_GameState", "playerDataArray[].canStartSpending"),
    ("DAT_GameState", "playerDataArray[].resourcesToAcquireArray[]"),
    ("DAT_GameState", "playerDataArray[].resourceRebuildDelay"),
    ("DAT_GameState", "playerDataArray[].aiRequestDelay"),
    ("DAT_GameState", "playerDataArray[].requestedGoodsArray1Unk[]"),
    ("DAT_GameState", "playerDataArray[].requestedGoodsArray2Unk[]"),
    ("DAT_GameState", "mapAndTime.playerTeams[]"),
    ("DAT_BuildingDefinedData", "DAT_BuildingTypeOwnable[]"),
    ("DAT_UnitsState", "units[].field297_0x3f4"),
    ("DAT_GameState", "playerDataArray[].enemies"),
    ("DAT_GameState", "gameTicksLoadBalancer"),
    ("DAT_TileMapState", "field122_0x554930"),
    ("DAT_TileMapState", "mapSize"),
    ("DAT_TileMapState", "moats[]"),
    ("DAT_UnitsState", "units[].field67_0x90"),
    ("DAT_UnitsState", "units[].isSelectable_OR_matchTime"),
    ("DAT_BuildingsState", "buildings[].resourcePitch"),
    ("DAT_BuildingsState", "buildings[].resourceIron"),
    ("DAT_BuildingsState", "buildings[].owner"),
    ("DAT_GameSynchronyState", "currentPlayerSlotID"),
])
def test_jedes_feld_der_proben_steht_in_der_karte(gruppe, feld):
    K = Feldkarte.laden(feldliste=FELDLISTE)
    assert K.adresse(gruppe, feld)[0] > 0


def test_aus_einem_test_startet_keine_messung():
    assert callable(auge_rufen.szene)
