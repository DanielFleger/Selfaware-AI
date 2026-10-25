# -*- coding: utf-8 -*-
"""Spielwerte aus dem Spiel lesen - Stammwerte (B-242, SRE 25.10.2026, Auftrag Daniel ueber SAI 08:27).

Alles, was das Spiel ueber Einheiten, Gebaeude, Waren und Geschosse "weiss", steht als feste Tabellen im Programm
(Abschnitt .data der exe). Dieses Werkzeug liest sie EINMAL je Partie und schreibt daten/spielwerte_<stempel>.json,
damit kein Wert davon in unserem Code steht (Daniel: gilt fuer jede Balance, jeden Mod).

Zwei Quellen, gleiche Adressen:
  live   - aus dem laufenden Spiel (speicher.lies, nur lesen) - das ist der Stand MIT allen Patches (UCP3, Mods)
  datei  - aus der Programmdatei (Referenz-exe C:\\Users\\danie\\shc-ref\\StrongholdCrusader.exe oder --exe <pfad>) -
           der Stand OHNE Patches. Laeuft kein Spiel, wird die Datei genommen und das steht im Ergebnis.
Beide stimmen Byte fuer Byte ueberein, solange kein Patch die Tabelle anfasst - der Vergleich (--vergleich) zeigt
jede Abweichung, und genau die sind die Balance-Aenderungen eines Mods.

Herkunft der Adressen und Aufbauten: OpenSHC-Ghidra-Projekt (Codex-Index 23.10.2026, exports/reference/types.json
und symbols.json). Je Tabelle steht die Ghidra-Struktur dabei. Marke je Wert: "abgelesen" (aus der Datei gelesen,
Aufbau aus Ghidra), bis ein Test im Spiel ihn bestaetigt (Wissensregister).

Aufruf: python werkzeug/spielwerte.py [--exe <pfad>] [--spiel <ordner>] [--vergleich] [--still]
Anzeigenamen (Einheiten, Waren) kommen aus cr.tex im Spielordner, nicht aus der exe (A7).
"""
import argparse
import json
import os
import struct
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
D = os.path.join(HIER, "..", "daten")
REFERENZ_EXE = r"C:\Users\danie\shc-ref\StrongholdCrusader.exe"

# --- Aufzaehlungen (OpenSHC, types.json) ----------------------------------------------------------------------------
UT = {1: "PEASANT", 2: "BURNINGMAN", 3: "WOODCUTTER", 4: "FLETCHER", 5: "TUNNELER", 6: "HUNTER", 7: "QUARRYMASON",
      8: "QUARRYWORKER", 9: "QUARRYOX", 10: "PITCHMAN", 11: "WHEATFARMER", 12: "HOPSFARMER", 13: "APPLEFARMER",
      14: "DAIRYFARMER", 15: "MILLER", 16: "BAKER", 17: "BREWER", 18: "POLETURNER", 19: "SMITH", 20: "ARMORER",
      21: "TANNER", 22: "E_ARCHER", 23: "E_XBOW", 24: "E_SPEAR", 25: "E_PIKE", 26: "E_MACE", 27: "E_SWORD",
      28: "E_KNIGHT", 29: "E_LADDER", 30: "E_ENGINEER", 31: "MINER", 32: "TRANSPORTMINER", 33: "PRIEST", 34: "HEALER",
      35: "DRUNK", 36: "INNKEEPER", 37: "E_MONK", 38: "E_ARCHER_DEBUG", 39: "S_CATAPULT", 40: "S_TREBUCHET",
      41: "S_MANGONEL", 42: "TRADER", 43: "TRADERHORSE", 44: "ANTELOPESHDEER", 45: "LIONSHWOLF", 46: "RABBIT",
      47: "CAMELSHBEAR", 48: "CROW", 49: "SEAGULL", 50: "S_SIEGETENT", 51: "COW", 52: "HUNTERDOG", 53: "FIREFIGHTER",
      54: "GHOST", 55: "LORD", 56: "LADY", 57: "JESTER", 58: "S_TOWER", 59: "S_BATTERINGRAM", 60: "S_SHIELD",
      61: "S_BALLISTA", 62: "CHICKEN", 63: "MOTHER", 64: "CHILD", 65: "JUGGLER", 66: "FIREEATER", 67: "CAGEDOG",
      68: "BURNING_ANIMAL_BIG", 69: "BURNING_ANIMAL_SMALL", 70: "A_ARCHER", 71: "A_SLAVE", 72: "A_SLINGER",
      73: "A_ASSASSIN", 74: "A_HARCHER", 75: "A_SWORDSMAN", 76: "A_FIRETHROWER", 77: "S_FBALLISTA", 78: "UNKNOWN2",
      79: "UNKNOWN3"}
BT = {1: "HOVEL", 2: "HOUSE", 3: "WOODCUTTERSHUT", 4: "OXTETHER", 5: "IRONMINE", 6: "PITCHRIG", 7: "HUNTERSHUT",
      8: "MERCENARYPOST", 9: "BARRACKS", 10: "STOCKPILE", 11: "ARMORY", 12: "FLETCHER", 13: "BLACKSMITH", 14: "POLETURNER",
      15: "ARMOURER", 16: "TANNER", 17: "BAKERY", 18: "BREWERY", 19: "GRANARY", 20: "QUARRY", 21: "QUARRYSTOCKPILE",
      22: "INN", 23: "APOTHECARY", 24: "ENGINEERSGUILD", 25: "TUNNELERSGUILD", 26: "MARKETPLACE", 27: "WELL",
      28: "OILSMELTER", 29: "SIEGETENT", 30: "WHEATFARM", 31: "HOPFARM", 32: "APPLEFARM", 33: "DAIRYFARM", 34: "MILL",
      35: "STABLES", 36: "CHAPEL", 37: "CHURCH", 38: "CATHEDRAL", 39: "UNKNOWN1", 40: "MANORHOUSE", 41: "STONEKEEP",
      42: "STRONGHOLD", 43: "KEEPFOUR", 44: "KEEPFIVE", 45: "GATEHOUSELARGE", 46: "GATEHOUSESMALL", 47: "WOODGATE1",
      48: "WOODGATE2", 49: "DRAWBRIDGE", 50: "TUNNEL", 51: "CAMPFIRE", 52: "SIGNPOST", 53: "PARADEGROUND",
      54: "FIREBALLISTA", 55: "CAMPGROUND", 56: "PARADEGROUND2", 57: "PARADEGROUND3", 58: "PARADEGROUND4",
      59: "PARADEGROUND5", 60: "GATEHOUSE", 61: "TOWER", 62: "GALLOWS", 63: "STOCKS", 64: "WITCHHOIST", 65: "MAYPOLE",
      66: "GARDEN", 67: "KILLINGPIT", 68: "PITCHDITCH", 69: "SIEGETOWER_PLACED", 70: "WATERPOT", 71: "KEEPDOOR_LEFT",
      72: "KEEPDOOR_RIGHT", 73: "KEEPDOOR", 74: "TOWER1", 75: "TOWER2", 76: "TOWER3", 77: "TOWER4", 78: "TOWER5",
      79: "UNKNOWN3", 80: "CATAPULT", 81: "TREBUCHET", 82: "BATTERINGRAM", 83: "SIEGETOWER", 84: "SHIELD", 85: "UNKNOWN4",
      86: "MANGONEL", 87: "BALLISTA", 88: "UNKNOWN5", 89: "UNKNOWN6", 90: "UNKNOWN7", 91: "CESSPIT", 92: "BURNINGSTAKE",
      93: "GIBBET", 94: "DUNGEON", 95: "STRETCHINGRACK", 96: "RACKFLOGGING", 97: "CHOPPINGBLOCK", 98: "DUNKINGSTOOL",
      99: "DOGCAGE", 100: "STATUE", 101: "SHRINE", 102: "BEEHIVE", 103: "DANCINGBEAR", 104: "POND", 105: "BEARCAVE",
      106: "OUTPOST", 107: "OUTPOST_ARABIAN"}
RT = {1: "LOGS", 2: "WOOD", 3: "HOPS", 4: "STONE", 5: "PARTIALSTONE", 6: "IRON", 7: "PITCH", 8: "PARTIALPITCH", 9: "WHEAT",
      10: "BREAD", 11: "CHEESE", 12: "MEAT", 13: "APPLE", 14: "ALE", 15: "GOLD", 16: "FLOUR", 17: "BOW", 18: "CROSSBOW",
      19: "SPEAR", 20: "PIKE", 21: "MACE", 22: "SWORD", 23: "LEATHERARMOR", 24: "IRONARMOR"}
ET = {0: "UNKNOWN", 1: "ARROW_AND_DEFAULT", 2: "CATAPULT", 3: "TREBUCHET", 4: "MANGONEL", 7: "CROSSBOWARROW", 9: "FIRE",
      10: "FLAG_1", 11: "FLAG_4", 12: "FLAG_2", 13: "FLAG_3", 14: "BRAZIER", 15: "HEADS_ON_SPIKES", 20: "BALLISTA",
      21: "DUST_CLOUD", 22: "COW_POISON_CLOUD", 23: "COW_FLYING", 29: "SEAGULL", 33: "SLINGER", 34: "FIRETHROWER",
      36: "FIRETHROWER_UNTARGETED", 37: "FIREBALLISTA"}

# --- Tabellen: (Adresse, Anzahl, Format, Form, Bedeutung) ------------------------------------------------------------
# Adresse = Struktur-Basis + Offset laut Ghidra-Struktur; Form = Index-Bedeutung.
U = 0x00B4DF4C      # DAT_UnitPropertiesDefinedData (Laenge 74348)
E = 0x005B6004      # DAT_EntityDefinedData (Geschosse, Laenge 6500)
T = 0x00AB8E14      # DAT_TroopDefinedData (Laenge 852)
B = 0x005B7974      # DAT_BuildingDefinedData
S = 0x00B3EB34      # DAT_SkirmishDefinedData
TABELLEN = {
    # Einheiten (Index = Einheitenart UT 0..79)
    "einheit.sprite_id":          (U + 340, 80, "i", "UT", "Sprite-Satz je Art"),
    "einheit.graphic_size":       (U + 660, 80, "i", "UT", "Groesse auf dem Feld (1, 2, 3, 4 Felder)"),
    "einheit.computer_controlled": (U + 980, 80, "i", "UT", "1 = Spiel steuert die Art selbst (Arbeiter)"),
    "einheit.computer_managed":   (U + 1300, 80, "i", "UT", "1 = vom Spiel verwaltet"),
    "einheit.movement_speed":     (U + 1620, 80, "i", "UT", "Geschwindigkeitsstufe 1..6 (Umrechnung in Takte je Feld: calculateUnitMovementSpeed 0x0052F7E0, offen)"),
    "einheit.able_to_climb_towers": (U + 1940, 80, "i", "UT", "1 = darf auf Tuerme"),
    "einheit.unit_movable":       (U + 2260, 80, "i", "UT", "1 = Spieler kann die Art bewegen"),
    "einheit.base_hp":            (U + 2580, 80, "i", "UT", "Leben zu Beginn (Lord 150.000; Skirmish-KIs mit MaxLordHealthMapping multipliziert)"),
    "einheit.arrow_damage":       (U + 2900, 80, "i", "UT", "Schaden, den EIN Pfeil (Bogen, arab. Bogen, Pferdebogen) an dieser ZIELART macht"),
    "einheit.stone_damage":       (U + 3220, 80, "i", "UT", "Schaden eines Schleuderstein an dieser Zielart"),
    "einheit.bolt_damage":        (U + 3540, 80, "i", "UT", "Schaden eines Armbrustbolzens an dieser Zielart"),
    "einheit.melee_damage":       (U + 3860, 6400, "i", "UTxUT", "Nahkampf [Angreifer][Ziel] je Treffer (Ghidra: 'not 100% sure if order is correct'; Gegenprobe Streitkolben->Lord 75 passt zu gemessen ~70)"),
    "einheit.euro_resource_costs": (U + 29460, 28, "i", "7x4", "Waffe/Ruestung/-/Pferd(-1) je Kasernen-Einheit (Reihen: Bogen, Armbrust, Speer, Pike, Streitkolben, Schwert, Ritter; Werte = RT-Nummern)"),
    "einheit.unit_climb":         (U + 29620, 80, "i", "UT", "1 = klettert (Leitern/Mauer)"),
    "einheit.stat_matrix4":       (U + 29940, 80, "i", "UT", "unbenannt (SomeUnitStatMatrix4)"),
    "einheit.field65":            (U + 30260, 80, "i", "UT", "unbenannt"),
    "einheit.field66":            (U + 30580, 80, "i", "UT", "unbenannt"),
    "einheit.stat_matrix5":       (U + 30900, 80, "i", "UT", "unbenannt (SomeUnitStatMatrix5)"),
    "einheit.not_blessable":      (U + 31220, 80, "i", "UT", "1 = nicht segnbar"),
    "einheit.can_melee":          (U + 31540, 80, "i", "UT", "1 = kann Nahkampf"),
    "einheit.enemy_notice_range": (U + 31860, 80, "i", "UT", "Feind-Bemerk-Reichweite (0, 63, 127, 255; Feinmass?)"),
    "einheit.climb_state_flags":  (U + 32180, 560, "i", "7xUT", "7 Flaggenreihen je Art (Reihe 0 = anfaellig fuer Kuh-Seuche, processEntityDamageToUnit)"),
    "einheit.sprite_dimensions":  (U + 34420, 160, "i", "UTx2", "Sprite-Breite/Hoehe"),
    "einheit.vision_bonus":       (U + 74004, 10, "i", "10", "Sichtbonus-Stufen"),
    # Truppen / Preise (TroopDefinedData)
    "truppe.peasant_spawn_solitary_bis100": (T + 4, 21, "i", "Beliebtheit 0..20?", "Zuzugs-Uhr Einzelspieler bis 100 Leute"),
    "truppe.peasant_spawn_solitary_ab101":  (T + 92, 21, "i", "Beliebtheit", "Zuzugs-Uhr Einzelspieler ab 101"),
    "truppe.peasant_spawn_skirmish":        (T + 180, 21, "i", "Beliebtheit", "Zuzugs-Uhr Gefecht"),
    "truppe.kaserne_gold":        (T + 768, 7, "I", "7", "Gold je Kasernen-Einheit: Bogen, Armbrust, Speer, Pike, Streitkolben, Schwert, Ritter (euroRecruit 0x0052E960)"),
    "truppe.soeldner_gold":       (T + 808, 11, "i", "11", "Gold Soeldnerposten UI: arab. Bogen, Sklave, Schleuderer, Assassine, Pferdebogen, arab. Schwert, Feuerwerfer, ... (nonEuroRecruit 0x0052EC10 hat dieselben Werte fest im Code: 75, 5, 12, 60, 80, 80, 100; Ingenieur/Tunnelbauer 30, Leiter 4, Moench 10)"),
    # Geschosse (EntityDefinedData)
    "geschoss.reichweite":        (E + 852, 38, "I", "ET", "Reichweite je Geschossart (Pfeil 54, Katapult 75, Tribok 85, Mangonel 70, Bolzen 54, Balliste 85, Schleuder 22, Feuerwerfer 11)"),
    "geschoss.kurventyp":         (E + 1060, 45, "i", "ET", "Flugkurve je Geschossart"),
    "geschoss.geschwindigkeit":   (E + 1268, 45, "i", "ET", "Fluggeschwindigkeit je Geschossart"),
    "geschoss.property1":         (E + 212, 45, "i", "ET", "unbenannt (Sprite?)"),
    "geschoss.property2":         (E + 428, 45, "i", "ET", "unbenannt"),
    # Gebaeude (BuildingDefinedData, Index = Gebaeudeart BT 0..109)
    "gebaeude.kosten":            (0x005C21D0, 550, "i", "BTx5", "Baukosten je Art: Holz, Stein, ?, ?, Gold (initBuildingCosts 0x00419780 kopiert nach BuildingsState.buildingCosts)"),
    "gebaeude.arbeiter_art":      (B + 620, 110, "i", "BT", "Arbeiter-Einheitenart je Gebaeudeart"),
    "gebaeude.arbeiter_zahl":     (B + 4580, 110, "i", "BT", "Arbeiter je Gebaeude"),
    "gebaeude.leben":             (B + 10404, 110, "i", "BT", "Gebaeudeleben (Rohwert)"),
    "gebaeude.bevoelkerung":      (B + 10948, 110, "i", "BT", "Wohnplaetze je Art (Huette 8, Bergfriede 8-16)"),
    "gebaeude.hoehe":             (B + 16284, 110, "i", "BT", "Gebaeudehoehe (fuer Schusslinie L79)"),
    "gebaeude.max_hoehenunterschied": (B + 1940, 110, "i", "BT", "Bauplatz: erlaubter Hoehenunterschied"),
    "gebaeude.ist_torhaus":       (B + 7324, 110, "i", "BT", "1 = Torhaus"),
    "gebaeude.ist_bergfried":     (B + 7764, 110, "i", "BT", "1 = Bergfried"),
    "gebaeude.ist_tor_oder_turm": (B + 8204, 110, "i", "BT", "1 = Tor oder Turm"),
    "gebaeude.hat_leben":         (B + 6884, 110, "i", "BT", "1 = kann beschaedigt werden"),
    "gebaeude.ecksperre":         (B + 6004, 110, "i", "BT", "1 = Ecksperre fuer schraege Schritte (W4)"),
    "gebaeude.lagergrenze_je_ware": (B + 5020, 26, "i", "RT", "Hoechstmenge je Ware je Lagerteil (Lager 48, Kornspeicher 250, Waffenlager 50)"),
    "gebaeude.lagerart_je_ware":  (B + 10844, 26, "i", "RT", "Welches Gebaeude die Ware lagert (10 Lager, 19 Kornspeicher, 11 Waffenlager, 40 Gold im Bergfried)"),
    # Markt (RenderingDefinedData, beim Kartenladen nach GameState kopiert; Preis je 5 Stueck, Spiel teilt durch 5)
    "markt.kaufpreis_je5":        (0x006171C0, 26, "i", "RT", "Kaufpreis fuer 5 Stueck (getBuyPrice: /5 * Menge)"),
    "markt.verkaufspreis_je5":    (0x00617228, 26, "i", "RT", "Verkaufspreis fuer 5 Stueck"),
    "markt.startgold":            (0x005C2A6C, 3, "i", "3", "Startgold je Stufe"),
    # Gefecht (SkirmishDefinedData)
    "gefecht.lord_leben_je_ki":   (S + 28, 34, "i", "17x2", "MaxLordHealthMapping je KI-Art: (aiTypeA, Prozent) - Lord-Leben = base_hp * Prozent / 100 (UpgradeMapUnitsLordHealthTo_169)"),
    "gefecht.ranged_and_armored": (S + 0, 7, "i", "7", "RangedAndArmoredUnits"),
}


SPIELORDNER = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz5"


def namen(spielordner=SPIELORDNER):
    """Anzeigenamen aus cr.tex (TextManager::loadCRTex 0x00473870): 260 int32 Gruppen-Offsets (in UTF-16-Zeichen),
    danach der Text UTF-16-LE, Eintraege mit NUL getrennt, je Eintrag eine Leerzeile. Gruppe 88 (eTextSections, OpenSHC) =
    Einheitenarten in UT-Reihenfolge (Eintrag 2*UT), Gruppe 2 = Waren (2*RT). Sprache = Gruppe 6."""
    pfad = os.path.join(spielordner, "cr.tex")
    if not os.path.exists(pfad):
        return {"fehler": "cr.tex nicht gefunden: %s" % pfad}
    d = open(pfad, "rb").read()
    offs = list(struct.unpack("<260i", d[:0x410]))
    txt = d[0x410:]

    def gruppe(i):
        a = offs[i]
        b = next((o for o in offs[i + 1:] if o > a), len(txt) // 2)
        return txt[a * 2:b * 2].decode("utf-16-le", errors="replace").split("\x00")
    g88, g2, g64 = gruppe(88), gruppe(2), gruppe(64)
    # Gruppe 88 endet bei UT 66 (Stronghold-1-Liste). Die Crusader-Araber (70-76) stehen in cr.tex nur im Plural im
    # Aussenposten-Menue (Gruppe 64): 20 Bogenschuetzen, 22 Schwertkaempfer, 24 Sklaven, 26 Berittene Bogenschuetzen,
    # 28 Feuerwerfer, 30 Schleuderschuetzen, 32 Arab. Ballisten; der Assassine hat dort keinen Eintrag.
    einheit = {ut: g88[2 * ut] for ut in range(1, 80) if 2 * ut < len(g88) and g88[2 * ut]}
    for ut, k in ((70, 20), (75, 22), (71, 24), (74, 26), (76, 28), (72, 30), (77, 32)):
        if k < len(g64) and g64[k]:
            einheit[ut] = g64[k] + " (Plural, Aussenposten-Menue)"
    return {"datei": pfad, "sprache": gruppe(6)[0], "einheit": einheit,
            "ware": {rt: g2[2 * rt] for rt in range(1, 25) if 2 * rt < len(g2) and g2[2 * rt]}}


# --- Schussrhythmus: Animationstabellen (1 Byte je Bild, 0 = Ende) der Zustaende Nachladen (4) / Zielen (5) / Schiessen (6).
# Ein Bild dauert (animationSpeed + 1) Takte (updateUnits 0x00579300: animationTicker > animationSpeed + leap -> naechstes
# Bild). Takte je Zustand = Bilder x (Speed + 1). Das Geschoss entsteht beim Bild "schuss_bei" (animationFrame bzw.
# animationCycleNumber laut Update-Funktion). Tabellen aus den Update-Funktionen abgelesen (SRE 25.10.):
#   Bogen 0x0055A800, Armbrust 0x0055C7B0, arab. Bogen 0x00570400, Schleuderer 0x00572E80, Feuerwerfer 0x005769F0.
ANIM = 0x00B56AC4   # DAT_UnitPropertiesDefinedData.ANIM_Frames_Shared_UnitClimbingUp (AnimationFrameData)
SCHUSS = {   # UT: Phasen (Name, Adresse der Bildtabelle, animationSpeed), Geschoss-Moment
    22: {"phasen": [("nachladen", ANIM + 0xBF4, 2), ("zielen", ANIM + 0xC1C, 2), ("schiessen", ANIM + 0xC74, 2)], "schuss_bei": "Bild 6"},
    23: {"phasen": [("nachladen", ANIM + 0x154C, 2), ("zielen", ANIM + 0x1590, 2), ("schiessen", ANIM + 0x15E4, 2)], "schuss_bei": "Zyklus 2"},
    70: {"phasen": [("nachladen", 0x00B59250, 2), ("zielen", 0x00B59270, 2), ("schiessen", 0x00B59288, 2)], "schuss_bei": "Zyklus 0"},
    72: {"phasen": [("nachladen", 0x00B596EC, 2), ("zielen", 0x00B59708, 0), ("schiessen", ANIM + 0x2C7C, 1)], "schuss_bei": "Zyklus 0"},
    76: {"phasen": [("nachladen", ANIM + 0x34D4, 6), ("zielen", ANIM + 0x34EC, 1), ("schiessen", ANIM + 0x3510, 2)], "schuss_bei": "Zyklus 0"},
    # Berittener Bogenschuetze (HorseArcher_DoShooting 0x00575820): drei Tabellen, Speed 1 (Bild = 2 Takte), Pfeil bei Bild 27
    74: {"phasen": [("nachladen", ANIM + 0x30E4, 1), ("zielen", ANIM + 0x314C, 1), ("schiessen", ANIM + 0x31A4, 1)], "schuss_bei": "Bild 27"},
    # Belagerungsgeraete (UpdateCatapult 0x00568320, Trebuchet 0x00569410, Mangonel 0x0056A3F0, Ballista 0x0056ECD0,
    # FireBallista 0x00577CC0): zwei Bildtabellen je Zyklus (Spannen, Schuss), Speed 2; unbemannt Speed 10000 = steht.
    39: {"phasen": [("spannen", ANIM + 0x1784, 2), ("schiessen", ANIM + 0x17D4, 2)], "schuss_bei": "Bild 23 (Index 9 der Schusstabelle)"},
    40: {"phasen": [("spannen", ANIM + 0x183C, 2), ("schiessen", ANIM + 0x196C, 2)], "schuss_bei": "Bild 27 (Index 3 der Schusstabelle)"},
    41: {"phasen": [("spannen", ANIM + 0x1A24, 2), ("schiessen", ANIM + 0x1A9C, 2)], "schuss_bei": "offen"},
    61: {"phasen": [("spannen", ANIM + 0x1B14, 2), ("schiessen", ANIM + 0x1B8C, 2)], "schuss_bei": "offen"},
    77: {"phasen": [("spannen", ANIM + 0x35DC, 2), ("schiessen", ANIM + 0x3654, 2)], "schuss_bei": "offen"},
}


# Schlagtakt gegen Gebaeude/Mauer (Zustand 107 US_MELEE_ATTACK_WALL): ein Treffer je Durchlauf der Hack-Animation,
# Dauer = Bilder x (animationSpeed + 1). Tabellen je Art aus den Update-Funktionen (SRE 25.10. 10:00). Der Burgherr (55,
# UpdateLord 0x0056C560) wechselt je Schlag durch vier Hieb-Animationen (Tabellen 17/14/12/14 Bilder) - Mittel der vier.
HACKEN = {22: [(ANIM + 0xF84, 3)], 23: [(ANIM + 0x152C, 3)], 24: [(ANIM + 0x1C04, 3)], 25: [(ANIM + 0x11F8, 3)],
          26: [(ANIM + 0x1388, 3)], 27: [(ANIM + 0x1E7C, 3)], 28: [(ANIM + 0x2290, 3)], 37: [(ANIM + 0x172C, 3)],
          55: [(ANIM + 0x6124, 3), (ANIM + 0x614C, 3), (ANIM + 0x6170, 3), (ANIM + 0x614C, 3)],
          70: [(0x00B592B0, 3)], 71: [(ANIM + 0x2538, 2)], 72: [(0x00B594E8, 3)], 73: [(ANIM + 0x2C94, 2)],
          74: [(ANIM + 0x2FC0, 3)], 75: [(0x00B59CD0, 3)], 76: [(ANIM + 0x33F4, 3)]}


def hacken(lies):
    aus = [0] * 80
    for ut, tabellen in HACKEN.items():
        takte = []
        for adr, speed in tabellen:
            roh = lies(adr, 200)
            bilder = next((i for i, b in enumerate(roh) if (b if b < 128 else b - 256) < 1), 200)
            takte.append(bilder * (speed + 1))
        aus[ut] = int(round(sum(takte) / len(takte)))
    return aus


def schuss(lies):
    """Je Schuetzenart: Bilder und Takte je Phase und der ganze Zyklus (ohne Zielsuche/Laufen/Drehen)."""
    aus = {}
    for ut, z in SCHUSS.items():
        e = {"schuss_bei": z["schuss_bei"], "phasen": {}}
        gesamt = 0
        for name, adr, speed in z["phasen"]:
            roh = lies(adr, 200)
            bilder = next((i for i, b in enumerate(roh) if (b if b < 128 else b - 256) < 1), 200)
            e["phasen"][name] = {"adresse": "0x%08X" % adr, "bilder": bilder, "speed": speed, "takte": bilder * (speed + 1)}
            gesamt += bilder * (speed + 1)
        e["zyklus_takte"] = gesamt
        e["schuesse_je_1000_takte"] = round(1000.0 / gesamt, 1) if gesamt else None
        aus[ut] = e
    return aus


# --- Werte, die fest im Code stehen (nicht als Tabelle lesbar; abgelesen SRE 25.10., Datei-Stand) --------------------
CODE_KONSTANTEN = {
    "nahkampf_je_takt": "processMeleeInitiation 0x00549C70 laeuft jeden Takt je Einheit (updateUnits) und ruft bei "
                        "anliegendem Gegner jedes Mal processUnitAttackOtherUnit: melee_damage ist Schaden je TAKT "
                        "(Daniel gemessen: Streitkolben 70/Takt am Lord = live-Tabelle 70)",
    "gebaeude_schaden_je_schlag": {
        # (Gebaeude, Tor/Turm, Mauer) - Update-Funktionen, Zustand 107 US_MELEE_ATTACK_WALL
        "E_ARCHER": (4, 1, 2), "E_XBOW": (4, 2, 2), "E_SPEAR": (8, 3, 4), "E_PIKE": (20, 4, 6), "E_MACE": (35, 4, 6),
        "E_SWORD": (70, 6, 10), "E_KNIGHT": (70, 6, 10), "E_MONK": (20, 4, 4), "LORD": (70, 6, 10),
        "A_ARCHER": (4, 1, 2), "A_SLINGER": (4, 1, 2), "A_HARCHER": (4, 1, 2), "A_FIRETHROWER": (4, 1, 2),
        "A_ASSASSIN": (70, 6, 10), "A_SWORDSMAN": (70, 6, 10), "A_SLAVE": "8 nur an nicht brennbaren Gebaeuden, sonst Feuer",
        "TUNNELER": "10 + 10 Umfeld beim Einsturz", "S_BATTERINGRAM": 50,
        "Geschoss Pfeil/Bolzen an Gebaeude": 1, "Geschoss Balliste": 2, "Geschoss Feuerballiste": 10, "Stein Katapult/Tribok/Mangonel": "10 am Feld + 10 Umfeld (processEntityHitBuildingOrUnit 0x00407190); an Mauer = 10 Hoehenpunkte",
        "Feuer": "alle 20 Takte 1; Huette/Holzfaeller/Jaeger/Farmen 4",
    },
    "mauer": "Schaden = Hoehenabbau in Punkten (HeightLayer -1 je Punkt bis Bodenhoehe, dann Mauer weg); einzeln "
             "stehendes Mauerstueck (unter 2 Nachbarn) x1,5, von 3+ Seiten umgeben x0,5 (processDamageToBuilding 0x00516B80)",
    "kuh_nachspawn": "Milchhof: 32 Takte nach Ende der Melk-Animation eine neue Kuh in den naechsten freien Platz (bis 3)",
    "ochse_nachspawn": "Ochsenpfahl: 100 Takte nach Verlust ein neuer Ochse, solange ein Arbeiter zugeteilt ist",
}


def abgeleitet(w, sch, hk):
    """Zusaetzliche Tabellen im selben Format (adresse/form/bedeutung/werte), fuer SAIs Kaufrechnung und Anschluss
    (SAI 25.10. 09:52). Quelle: Code-Stellen (abgelesen) und aus den gelesenen Tabellen gerechnet."""
    stufe = w["einheit.movement_speed"]["werte"]
    hp = w["einheit.base_hp"]["werte"]
    aus = {}
    aus["takt.nahkampf_je_treffer"] = {
        "adresse": "Code 0x00549C70 processMeleeInitiation, 0x00579300 updateUnits", "form": "UT",
        "bedeutung": "Takte zwischen zwei Nahkampftreffern bei anliegendem Gegner: 1 fuer jede Art, die can_melee hat "
                     "(Schlag jeden Takt, Schaden = melee_damage[Angreifer][Ziel] je Takt; Daniel gemessen Streitkolben 70/Takt)",
        "werte": [1 if w["einheit.can_melee"]["werte"][ut] else 0 for ut in range(80)]}
    aus["takt.schuss_zyklus"] = {
        "adresse": "Animationstabellen, siehe schuss_phasen", "form": "UT",
        "bedeutung": "Takte zwischen zwei Geschossen (Nachladen + Zielen + Schiessen bzw. Spannen + Schuss), ohne Zielsuche/"
                     "Drehen/Laufen; 0 = kein Schuetze",
        "werte": [sch[ut]["zyklus_takte"] if ut in sch else 0 for ut in range(80)]}
    aus["takt.schuss_phasen"] = {"adresse": "Animationstabellen (1 Byte je Bild, Bild = Speed+1 Takte)", "form": "UT -> Phasen",
                                 "bedeutung": "Bilder, Speed und Takte je Phase, Geschoss-Moment", "werte": sch}
    aus["bewegung.takte_je_feld"] = {
        "adresse": "Code 0x00578C40 processUnitMove (8 Mikroschritte je Feld), 0x00579300 (Schritt alle Stufe+1 Takte)",
        "form": "UT",
        "bedeutung": "Takte je Feld auf ebenem Boden = 8 x (movement_speed + 1); schraeg = gerade. Zuschlaege je Takt-Schritt: "
                     "Steigen +1..+5 (Hoehenunterschied 2/4/8/12/16), Gelaende-Bit 0x200000 +2, Bit 0x20000000 +4/+6, "
                     "Gedraenge moveDelay, Trupp = langsamste Einheit (Trupp-Takte = 8 x (max Stufe + 1)). Tiere/Arbeiter "
                     "setzen die Stufe in ihren Update-Funktionen zeitweise um (Flucht Hirsch/Loewe/Kamel Stufe 20 = 168 Takte, "
                     "Hase 40, Ochse 1/3, Kuh 2, Jaeger 1-10, Betrunkener 6-9) - dann gilt 8 x (Stufe + 1) mit dieser Stufe",
        "werte": [8 * (int(st) + 1) if st > 0 else 0 for st in stufe]}
    GEB = CODE_KONSTANTEN["gebaeude_schaden_je_schlag"]
    namen = {v: k for k, v in UT.items()}
    werte = [None] * 80
    for name, v in GEB.items():
        if name in namen and isinstance(v, tuple):
            werte[namen[name]] = list(v)
    werte[71] = [8, 0, 0]; werte[5] = [10, 10, 10]; werte[59] = [0, 50, 0]
    aus["gebaeude_schaden.je_schlag"] = {
        "adresse": "Code der Update-Funktionen (Zustand 107), z. B. Streitkolben 0x00560700, Schwert 0x00561C10",
        "form": "UT -> [Gebaeude, Tor/Turm, Mauer]",
        "bedeutung": "Schadenspunkte je Schlag an Wirtschaftsgebaeude / Torhaus+Turm / Mauer (Mauer: Hoehenpunkte). "
                     "Sklave 8 nur an nicht brennbaren Gebaeuden (sonst Feuer), Tunnelbauer 10 + 10 Umfeld, Ramme 50 ans Tor. "
                     "Gebaeudeleben = gebaeude.leben. Bergfried: nicht beschaedigbar (hat_leben 0). Schlagtakt gegen Gebaeude offen "
                     "(nextAttackHurtsWall wechselt je Schlag, Animationstakt nicht gelesen)",
        "werte": werte}
    aus["gebaeude_schaden.takt_je_schlag"] = {
        "adresse": "Animationstabellen Zustand 107 je Art (HACKEN in spielwerte.py), Update-Funktionen", "form": "UT",
        "bedeutung": "Takte zwischen zwei Schlaegen gegen Gebaeude/Mauer (ein Treffer je Hack-Animation). Schaden je Takt = "
                     "gebaeude_schaden.je_schlag / takt_je_schlag. 0 = hackt nicht (Arbeiter) oder nicht gelesen; Burgherr = Mittel seiner vier Hiebe",
        "werte": hk}
    aus["gebaeude_schaden.geschosse"] = {
        "adresse": "Code 0x00407190 processEntityHitBuildingOrUnit, 0x00422E20 updateBuildings (Feuer)", "form": "Text",
        "bedeutung": "Pfeil/Bolzen 1, Balliste 2, Feuerballiste 10, Stein (Katapult/Tribok/Mangonel) 10 am Feld + 10 Umfeld, an "
                     "Mauer 10 Hoehenpunkte; Feuer: alle 20 Takte 1 Punkt, Huette/Holzfaeller/Jaeger/Farmen 4 Punkte; Mauer-Faktor: "
                     "Stueck mit unter 2 Mauer-Nachbarn x1,5, mit 3+ Nachbarn x0,5. Zuendwahrscheinlichkeit/Brenndauer/Ausbreitung "
                     "nicht gelesen (getBuildingFlammabilityFactor, fireDuration)",
        "werte": {"pfeil": 1, "bolzen": 1, "balliste": 2, "feuerballiste": 10, "stein": 10, "stein_umfeld": 10,
                  "feuer_je_20_takte": 1, "feuer_holzbau_je_20_takte": 4}}
    aus["belagerung.gesamt"] = {
        "adresse": "zusammengefuehrt aus gebaeude.kosten (BT 80-87), base_hp, geschoss.reichweite, takt.schuss_zyklus",
        "form": "UT -> dict",
        "bedeutung": "Belagerungsgeraet auf einen Blick; Bauzeit siehe belagerung.bauzeit",
        "werte": {UT[ut]: {"leben": hp[ut], "kosten_gold": w["gebaeude.kosten"]["werte"][bt][4],
                           "kosten_holz": w["gebaeude.kosten"]["werte"][bt][0],
                           "reichweite_felder": w["geschoss.reichweite"]["werte"][et] if et else None,
                           "zyklus_takte": sch[ut]["zyklus_takte"] if ut in sch else None}
                  for ut, bt, et in ((39, 80, 2), (40, 81, 3), (41, 86, 4), (61, 87, 20), (77, 54, 37), (59, 82, 0), (58, 83, 0), (60, 84, 0))}}
    rc = w["einheit.euro_resource_costs"]["werte"]
    aus["belagerung.bauzeit"] = {
        "adresse": "Code Update*Building 0x0041F3B0 (Katapult), 0x0041F7C0 (Tribok), 0x0041FC90 (Turm), 0x00420120 (Ramme), "
                   "0x004205B0 (Schild), 0x0041E240 (Feuerballiste)", "form": "BT -> dict",
        "bedeutung": "Baustelle (BT 80-87/54) zaehlt je Takt die anwesenden Baumeister (E_ENGINEER 30) auf buildingProgress; ist die "
                     "Schwelle ueberschritten, entsteht das Geraet und die Baumeister werden Bediener. Bauzeit in Takten = Schwelle / "
                     "Baumeister vor Ort. Bedienerzahl steht nicht in einer Tabelle (arbeiter_zahl 0); Katapult: bei genau 2 werden beide "
                     "Bediener (Code), die uebrigen Zahlen sind Spielwissen (ungeprueft)",
        "werte": {"CATAPULT": {"schwelle": 320, "baumeister_angenommen": 2, "takte": 160},
                  "TREBUCHET": {"schwelle": 640, "baumeister_angenommen": 3, "takte": 213},
                  "SIEGETOWER": {"schwelle": 1280, "baumeister_angenommen": 4, "takte": 320},
                  "BATTERINGRAM": {"schwelle": 640, "baumeister_angenommen": 4, "takte": 160},
                  "SHIELD": {"schwelle": 120, "baumeister_angenommen": 1, "takte": 120},
                  "FIREBALLISTA": {"schwelle": 320, "baumeister_angenommen": 2, "takte": 160},
                  "MANGONEL/BALLISTA": "Turmgeraete, kein Zeltbau - Code nicht gelesen"}}
    aus["feuer.regeln"] = {
        "adresse": "Code 0x00410920 getBuildingFlammabilityFactor, 0x0041C810 lightUpBuilding, 0x004052E0 IgniteFireAtMiniTile, "
                   "0x00405680 UpdateFireEntity, 0x00422E20 updateBuildings, 0x00571C00 UpdateSlave, 0x00422C60", "form": "Text",
        "bedeutung": "Brennbarkeit je Gebaeudeart: 0 = brennt nicht (Lager, Bergfriede, Torhaeuser, Tuerme, Mauern, Markt? nein: Markt 1), "
                     "1 = normal (Huetten, Werkstaetten, Hoefe, Kaserne, Soeldnerposten, Waffenlager, Kornspeicher, Kirchen), 5 = sehr "
                     "(Schmiede, Baeckerei, Gasthaus, Pechkocher), 4 = Exerzier-/Lagerplatz. ZUENDUNG ist KEIN Zufall: Sklave zuendet ein "
                     "brennbares Fremdgebaeude bei jedem zweiten Hieb (alle ~186 Takte) sicher, ausser es wurde gerade geloescht "
                     "(cooldownTimer); an nicht brennbaren macht er 8 Schaden je Hieb. Brand: fireDuration zaehlt je Takt hoch, alle 20 "
                     "Takte 1 Schaden (Huette/Holzfaeller/Jaeger/Farmen 4); auf jedem Gebaeudefeld entsteht ein Feuer (Staerke 2) mit "
                     "zufaelliger Verzoegerung 0-120 Takte. AUSBREITUNG: ein Feuer mit Staerke >= 2 zuendet zufaellig versetzte "
                     "Nachbar-Minifelder (Hoehenunterschied <= 24) mit Staerke-1, Gebaeude dort werden angezuendet, Baeume auch; "
                     "Torhaeuser/Tuerme nie. ENDE: keine feste Brenndauer gefunden - brennt bis zerstoert oder geloescht (Feuerwache "
                     "UpdateFireWatch 0x00543340, Brunnen); Zufalls-Ausbreitung auf andere Gebaeude des Spielers nur als KI-Ereignis "
                     "(spreadFireRandomlyToBuildings, Gewicht 1, sehr brennbare 5)",
        "werte": {"brennbarkeit": {"0": "Lager, Bergfriede, Torhaeuser, Tuerme, Mauern, Brunnen, Stall? (siehe Code)",
                                   "1": "Huetten, Werkstaetten, Hoefe, Kaserne, Soeldnerposten, Waffenlager, Kornspeicher, Markt, Kirchen",
                                   "4": "Exerzierplatz, Lagerplatz", "5": "Schmiede, Baeckerei, Gasthaus, Pechkocher"},
                  "zuendung_sklave_takte": 186, "schaden_je_20_takte": 1, "schaden_holzbau_je_20_takte": 4,
                  "feuer_staerke_gebaeude": 2, "verzoegerung_takte_max": 120, "ausbreitung_hoehenunterschied_max": 24,
                  "brenndauer": "unbegrenzt bis Loeschen/Zerstoerung (nicht gefunden)"}}
    aus["anwerben.voraussetzung"] = {
        "adresse": "Code 0x00464EF0 ProcessRecruitUnit, 0x0052E960 euroRecruit, 0x0052EC10 nonEuroRecruit, 0x00464DA0",
        "form": "UT -> dict",
        "bedeutung": "Gebaeude (BT), Gold, Waffe/Ruestung (RT aus dem Waffenlager BT 11), Pferd (Stall BT 35); immer: ein freier "
                     "Bauer am Lagerfeuer (sonst Fehlgrund 3) und Heer unter armySizeLimit; Soeldner nur Gold + Bauer. Anwerben "
                     "wandelt den Bauern um (Bevoelkerung -1 am Feuer, kein Beliebtheitseffekt im Code gesehen)",
        "werte": {**{UT[22 + i]: {"gebaeude": 9, "gold": w["truppe.kaserne_gold"]["werte"][i],
                                  "waffen_rt": [x for x in rc[i] if x > 0], "pferd": rc[i][3] == -1} for i in range(7)},
                  **{UT[ut]: {"gebaeude": 8, "gold": w["truppe.soeldner_gold"]["werte"][k], "waffen_rt": [], "pferd": False}
                     for k, ut in enumerate((70, 71, 72, 73, 74, 75, 76))},
                  "E_ENGINEER": {"gebaeude": 24, "gold": 30}, "TUNNELER": {"gebaeude": 25, "gold": 30},
                  "E_LADDER": {"gebaeude": 24, "gold": 4}, "E_MONK": {"gebaeude": 37, "gold": 10}}}
    aus["sicht.feind_takt"] = {
        "adresse": "Code 0x00579300 updateUnits (Maske enemy_notice_range gegen Spieltakt), 0x0054A7B0", "form": "UT",
        "bedeutung": "Alle wie viele Takte eine Art nach Feinden sucht (enemy_notice_range + 1); 0 = sucht nie (Arbeiter)",
        "werte": [n + 1 if n else 0 for n in w["einheit.enemy_notice_range"]["werte"]]}
    aus["sicht.assassine"] = {
        "adresse": "Code 0x0054A7B0 findNearestEnemyAndHeadTowardsIt (misst), 0x00579300 updateUnits (speichert alle 128 Takte), "
                   "0x0054B0D0 acquireShootTarget (> 160 -> kein Ziel), 0x004E7810 renderUnits (< 161 sichtbar, 120-160 verblasst)",
        "form": "Text",
        "bedeutung": "Ein Meuchelmoerder (A_ASSASSIN 73) ist fuer Schuetzen zielbar und auf dem Bildschirm sichtbar, wenn sein "
                     "gespeicherter Abstand zur naechsten feindlichen NAHKAMPF-/BELAGERUNGS-Einheit <= 160 Mikroschritte ist. "
                     "Gemessen wird nur gegen Einheiten mit Flag isSelectable (gesetzt in UpdateSpearman/Pikeman/Maceman/Swordsman/"
                     "Knight/Monk/Lord/Slave/Assassin/ArabianSwordsman/HorseArcher/Engineer/alle Belagerungsgeraete - NICHT in "
                     "UpdateCrusaderArcher/Crossbowman/ArabianArcher/Slinger/FireThrower): Fussschuetzen decken ihn also nicht durch "
                     "Naehe auf, Nahkaempfer, Berittene Bogenschuetzen, Baumeister und Geraete schon. Abstand = Pythagoras-Naeherung "
                     "max(dx,dy) + 0,4*min^2/max in Mikroschritten (8 je Feld): gerade 20 Felder, schraeg ~14. Der Wert wird nur beim "
                     "eigenen Feind-Takt des Meuchelmoerders (alle 128 Takte) neu gesetzt, Startwert 32000 = unsichtbar. Der Schuetze "
                     "braucht zusaetzlich: Ziel in seiner Reichweite (54 Felder), freie Schusslinie, eigener Feind-Takt (64 Takte). "
                     "SAI-Gegenprobe 25.10. (6.172 Proben): alle 30 Beschuss-Faelle hatten eine Feindtruppe <= 10 Felder, 989 Proben "
                     "mit Truppe <= 20 ohne Beschuss - passt zur Lesart, dass nur Nahkaempfer/Geraete zaehlen und der Wert alle 128 Takte "
                     "hinterherlaeuft; noch nicht gegen die Einheitenart der naechsten Truppe geprueft",
        "werte": {"sichtbar_ab_mikroschritte": 160, "sichtbar_ab_felder_gerade": 20, "sichtbar_ab_felder_schraeg": 14,
                  "verblasst_ab_mikroschritte": 120, "aktualisierung_takte": 128, "startwert": 32000,
                  "aufdecker": ["E_SPEAR", "E_PIKE", "E_MACE", "E_SWORD", "E_KNIGHT", "E_MONK", "LORD", "A_SLAVE", "A_ASSASSIN",
                                "A_SWORDSMAN", "A_HARCHER", "E_ENGINEER", "S_*"],
                  "keine_aufdecker": ["E_ARCHER", "E_XBOW", "A_ARCHER", "A_SLINGER", "A_FIRETHROWER"]}}
    aus["zustand.dauer"] = {
        "adresse": "Zustandsnummern UnitState; Dauern teils gemessen (SAI), teils aus Tabellen", "form": "Text",
        "bedeutung": "101 Gehen: 8 x (Stufe+1) Takte je Feld; 106 Nahkampf: Schlag jeden Takt; 4/5/6 Nachladen/Zielen/Schiessen: "
                     "takt.schuss_phasen; 127 Assassine klettert: gemessen 291 Takte am Torhaus (SAI lage_20261024_222651_i5), "
                     "Tabelle nicht gelesen; 107 Mauer hacken: Schlagtakt offen; 125 graben, 109/110/122 Umwandeln/Verschwinden/"
                     "Erscheinen: Dauern offen",
        "werte": {"klettern_torhaus_gemessen": 291}}
    aus["nachspawn.tiere"] = {
        "adresse": "Code 0x0041CA00 UpdateOxTether, 0x004167E0 UpdateDairyFarm, 0x005261B0 respawnDeer, 0x00525F20", "form": "Text",
        "bedeutung": "Ochse: 100 Takte nach Verlust neu (Arbeiter noetig); Kuh: 32 Takte nach Melk-Animation in freien Platz (bis 3); "
                     "Rehe: Nachwuchs NUR Einzelspieler, im Gefecht keiner; Loewen/Rehe/Hasen vermehren sich je Rudel mit Zufall; "
                     "Flucht/Verhalten: die Update-Funktionen setzen Stufen 1/2/3 und zeitweise 20 (Hirsch, Loewe, Kamel, Kaefighund) - "
                     "Stufe 20 waere nach der Formel 168 Takte je Feld, also Stillstand/Warten, nicht Sprint; Flucht-Logik selbst nicht gelesen",
        "werte": {"ochse_takte": 100, "kuh_takte": 32, "rehe_gefecht": 0}}
    return aus


def quelle_live():
    import speicher
    speicher.griff()
    return ("live", lambda adr, n: speicher.lies(adr, n))


def quelle_datei(pfad):
    data = open(pfad, "rb").read()
    off = struct.unpack_from("<I", data, 0x3C)[0]
    count = struct.unpack_from("<H", data, off + 6)[0]
    size = struct.unpack_from("<H", data, off + 20)[0]
    opt = off + 24
    base = struct.unpack_from("<I", data, opt + 28)[0]
    sek = []
    for i in range(count):
        s = opt + size + i * 40
        vs, va, rs, rp = struct.unpack_from("<IIII", data, s + 8)
        sek.append((va, rs, rp))

    def lies(adr, n):
        rva = adr - base
        for va, rs, rp in sek:
            if 0 <= rva - va and rva - va + n <= rs:
                return data[rp + rva - va: rp + rva - va + n]
        raise ValueError("0x%08X nicht in der Datei abgebildet" % adr)
    return ("datei:" + pfad, lies)


def lesen(lies):
    aus = {}
    for name, (adr, n, fmt, form, bedeutung) in TABELLEN.items():
        roh = lies(adr, n * 4)
        werte = list(struct.unpack("<%d%s" % (n, fmt), roh))
        if form == "UTxUT":
            werte = [werte[i * 80:(i + 1) * 80] for i in range(80)]
        elif form == "BTx5":
            werte = [werte[i * 5:(i + 1) * 5] for i in range(110)]
        elif form == "7xUT":
            werte = [werte[i * 80:(i + 1) * 80] for i in range(7)]
        elif form in ("7x4", "17x2", "UTx2"):
            b = int(form.split("x")[1])
            werte = [werte[i * b:(i + 1) * b] for i in range(len(werte) // b)]
        aus[name] = {"adresse": "0x%08X" % adr, "form": form, "bedeutung": bedeutung, "werte": werte}
    return aus


def gegenproben(w):
    g = w["einheit.base_hp"]["werte"]
    m = w["einheit.melee_damage"]["werte"]
    return {
        "lord_leben_150000": g[55] == 150000,
        "streitkolben_gegen_lord": m[26][55],
        "assassine_gold": w["truppe.soeldner_gold"]["werte"][3],
        "pfeil_reichweite_54": w["geschoss.reichweite"]["werte"][1],
        "bogenschuetze_gold_12": w["truppe.kaserne_gold"]["werte"][0],
        "huette_8_plaetze": w["gebaeude.bevoelkerung"]["werte"][1],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=REFERENZ_EXE)
    ap.add_argument("--spiel", default=SPIELORDNER, help="Spielordner mit cr.tex (Anzeigenamen)")
    ap.add_argument("--vergleich", action="store_true", help="live UND Datei lesen und Abweichungen zeigen")
    ap.add_argument("--still", action="store_true")
    a = ap.parse_args()
    quellen = []
    try:
        quellen.append(quelle_live())
    except Exception as e:  # kein Spiel - Datei
        if not a.still:
            print("kein laufendes Spiel (%s) - lese die Programmdatei" % e)
    if not quellen or a.vergleich:
        quellen.append(quelle_datei(a.exe))
    ergebnisse = [(q, lesen(l)) for q, l in quellen]
    q, w = ergebnisse[0]
    sch = schuss(quellen[0][1])
    w.update(abgeleitet(w, sch, hacken(quellen[0][1])))
    aus = {"erstellt": time.strftime("%Y-%m-%d %H:%M:%S"), "quelle": q, "marke": "abgelesen (Datei/Speicher, Aufbau aus Ghidra OpenSHC)",
           "aufzaehlungen": {"UT": UT, "BT": BT, "RT": RT, "ET": ET}, "namen": namen(a.spiel), "tabellen": w,
           "schuss": sch, "code_konstanten": CODE_KONSTANTEN, "gegenproben": gegenproben(w)}
    if len(ergebnisse) > 1:
        q2, w2 = ergebnisse[1]
        abw = {k: {"live": w[k]["werte"], "datei": w2[k]["werte"]} for k in w if k in w2 and w[k]["werte"] != w2[k]["werte"]}
        aus["vergleich"] = {"gegen": q2, "abweichende_tabellen": sorted(abw), "abweichungen": abw}
    ziel = os.path.join(D, time.strftime("spielwerte_%Y%m%d_%H%M%S.json"))
    json.dump(aus, open(ziel, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if not a.still:
        print("Quelle:", q)
        print("Gegenproben:", json.dumps(aus["gegenproben"]))
        n = aus["namen"]
        print("Namen (%s): %s" % (n.get("sprache", "?"), {k: n["einheit"].get(k) for k in (22, 26, 55, 73)} if "einheit" in n else n))
        if "vergleich" in aus:
            print("Abweichende Tabellen live/Datei:", aus["vergleich"]["abweichende_tabellen"] or "keine")
        for ut, e in aus["schuss"].items():
            print("Schuss %-14s %s -> Zyklus %3d Takte (%s je 1.000), Geschoss bei %s" % (
                UT[ut], " + ".join("%s %d" % (n, ph["takte"]) for n, ph in e["phasen"].items()), e["zyklus_takte"],
                e["schuesse_je_1000_takte"], e["schuss_bei"]))
        print("Geschrieben:", ziel)
    return ziel


if __name__ == "__main__":
    main()
