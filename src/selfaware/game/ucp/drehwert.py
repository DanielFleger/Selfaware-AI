# -*- coding: utf-8 -*-
"""Bildwert beim Bauen, wie ihn der Mausklick setzt (B-144, im Altstand B-271).

Befehl 28 traegt den Wert in buildings[].buildingVariation ein. 15 heisst: normal zeichnen. Jeder andere Wert verschiebt das
Bild normaler Gebaeude je nach Kartendrehung (updateBuildingGraphicsLayer): In der Standardansicht stimmt es, in den anderen
drei Drehungen zieht das Spiel fremde Bilder. Eigene Werte haben nur Tore und Zugbruecke
(MenuItemActionHandler_InGameMenu_TriggerPlaceBuildingCommand). Am Eingang aendert 15 statt 0 nichts
(setBuildingInitialEntryTileTry rechnet fuer beide Richtung 4).
"""

NORMAL = 15
EIGENER_WERT = {
    105: 0,  # Zugbruecke: Beim Klick rechnet checkDrawbridgePlacement die Richtung aus dem Torhaus, ohne Torhaus bleibt 0
    140: 0,
    141: 2,
    142: 4,
    143: 6,  # M_MAPPER_GATE_WOOD1A bis 1D
    144: 0x51,
    145: 0x50,
    146: 0x51,
    147: 0x50,  # M_MAPPER_GATE_STONE1A, 1B, 2A, 2B
}


def drehwert(mapper):
    return EIGENER_WERT.get(mapper, NORMAL)
