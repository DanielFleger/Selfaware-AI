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

Aufruf: python werkzeug/spielwerte.py [--exe <pfad>] [--vergleich] [--still]
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
        "streitkolben_gegen_lord_75": m[26][55],
        "assassine_gold_60_nicht_70": w["truppe.soeldner_gold"]["werte"][3],
        "pfeil_reichweite_54": w["geschoss.reichweite"]["werte"][1],
        "bogenschuetze_gold_12": w["truppe.kaserne_gold"]["werte"][0],
        "huette_8_plaetze": w["gebaeude.bevoelkerung"]["werte"][1],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=REFERENZ_EXE)
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
    aus = {"erstellt": time.strftime("%Y-%m-%d %H:%M:%S"), "quelle": q, "marke": "abgelesen (Datei/Speicher, Aufbau aus Ghidra OpenSHC)",
           "aufzaehlungen": {"UT": UT, "BT": BT, "RT": RT, "ET": ET}, "tabellen": w, "gegenproben": gegenproben(w)}
    if len(ergebnisse) > 1:
        q2, w2 = ergebnisse[1]
        abw = {k: {"live": w[k]["werte"], "datei": w2[k]["werte"]} for k in w if w[k]["werte"] != w2[k]["werte"]}
        aus["vergleich"] = {"gegen": q2, "abweichende_tabellen": sorted(abw), "abweichungen": abw}
    ziel = os.path.join(D, time.strftime("spielwerte_%Y%m%d_%H%M%S.json"))
    json.dump(aus, open(ziel, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if not a.still:
        print("Quelle:", q)
        print("Gegenproben:", json.dumps(aus["gegenproben"]))
        if "vergleich" in aus:
            print("Abweichende Tabellen live/Datei:", aus["vergleich"]["abweichende_tabellen"] or "keine")
        print("Geschrieben:", ziel)
    return ziel


if __name__ == "__main__":
    main()
