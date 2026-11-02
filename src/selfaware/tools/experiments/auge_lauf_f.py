# -*- coding: utf-8 -*-
"""B-142 Lauf F: Burgenbau auf "Eine praechtige Oase" (A Mighty Oasis.map), ohne Maus, alles aufgezeichnet.

Frage: Sieht das Auge alles, was im friedlichen Spiel passiert, ohne das Spiel zu bremsen? Plan: docs/plans/Plan_Lauf_F_neu.md.

  python -m selfaware.tools.experiments.auge_lauf_f pruefen --instanz 2     Trockenprobe, startet nichts, aendert nichts
  python -m selfaware.tools.experiments.auge_lauf_f trocken --instanz 2     Bauplan am angehaltenen Spielstand, baut nichts
  python -m selfaware.tools.experiments.auge_lauf_f los --instanz 2 --daniel-ja
  python -m selfaware.tools.experiments.auge_lauf_f stop --instanz 2        Abbruch und warten, bis der Takt wirklich steht

Gerechnet wird in Takten (Daniel 02.11.2026). Echte Zeit nur gegen Haengen (Frist, Stillstand, Kanal) und dort, wo Takte je Sekunde die Messgroesse sind.
Jeder Abschnitt prueft seine Wirkung im Speicher. Ist die Grundlage kaputt, endet der Lauf sofort; eine einzelne Schaltung ohne Wirkung ist ein Fund.
Der Lauf haelt das Spiel nie an (Daniel 02.11.2026 18:39: Bauen darf das Tempo nicht herausnehmen).

Menueweg aus dem Export: Hauptmenue Knopf 3 setzt GM_BUILDERUnk und oeffnet die Kartenwahl (Ansicht 35),
SingleplayerMapChoice_ButtonsAndHands(0x41) startet die markierte Karte (LaunchSinglePlayerGameUnk). Den Knopf-Handler
kennt logik.lua noch nicht; "los" spielt ihn in die Laufinstanz ein, die alte Datei bleibt mit Datum liegen.
Die Laufinstanz bekommt die logik.lua von Instanz 4 (nur gelesen): Sie lief mit demselben Modulordner villagestudio-0.1.0.
Instanz 5 nutzt seit 24.10. ein anderes Modul (selfaware-runtime, mit Uebernahme-Logik) und wird nie angefasst.
Die Ladeliste der Laufinstanz enthaelt das Modul seit der Startreparatur vom 24.10. nicht mehr; "los" traegt es wieder ein.
"""
import argparse
import collections
import json
import os
import shutil
import struct
import subprocess
import sys
import time

from selfaware.game.ucp.drehwert import drehwert

KARTE = "A Mighty Oasis"
STAMM = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme"
DANIELS_INSTANZ = 5
QUELL_INSTANZ = 4
SPERRE_NAME = "SRE_auge"
HAUPTMENUE, KARTENWAHL, IN_PARTIE = 41, 35, 14
ANSICHT, TICK, PAUSE, GAMEOVER = 0x01FE7D1C, 0x0117CADC, 0x01FEA054, 0x0117D500
GESAMT, SCROLL, MARKIERT = 0x01A24A68, 0x01A24A64, 0x01A24A6C  # DAT_MapSelection... in GameSynchronyState
LISTE, NAMEN, NAMENSLAENGE = 0x01126E28, 0x11BFCF8, 0x3E9      # Eintrag n = Zeile + Scrollstand (wie im Ladedialog)
KNOPF_START = 0x41
ANKER = "CustomScenarios_Main = 0x00440770,"
NEU = "SingleplayerMapChoice_ButtonsAndHands = 0x0042D640,"
BAU_ALT = "local ok, err = befehlAbsetzen(28, { b.x, b.y, b.mapper, b.groesse, b.richtung or 0, b.trupp or 0 })"
BAU_NEU = (
    "-- B-144 (Daniel 02.11.2026, wie B-271 im Altstand): Feste Werte nur bei Toren und der Zugbruecke, sonst zieht das Spiel gedreht fremde Bilder",
    "local TOR = { [101] = true, [102] = true, [105] = true, [140] = true, [141] = true, [142] = true,",
    "              [143] = true, [144] = true, [145] = true, [146] = true, [147] = true }",
    "local drehung = TOR[tonumber(b.mapper) or -1] and (b.richtung or 15) or 15",
    "local ok, err = befehlAbsetzen(28, { b.x, b.y, b.mapper, b.groesse, drehung, b.trupp or 0 })",
)
BAU_LOG_ALT = "tostring(b.richtung or 0),"
BAU_LOG_NEU = "tostring(drehung),"
TEMPO_LAUF, TEMPO_JEDER_TAKT = 1000, 40  # 40: hoechste Stufe, auf der jeder Takt gelesen wird (gemessen 201 von 201; auf 100 fehlen 2 von 498)
STUFEN = (1, 10, 40, 100, 200, 500, 1000)  # Daniel 02.11.2026: auf Tempo 1 bis 1000 kein Abzug vom normalen Tempo
TREPPE_TAKTE = {1: 20, 10: 100}  # sonst 1.000: Ablesefehler 4 Takte = 0,4 %. Auf Stufe 1 und 10 kann das Lesen nicht bremsen (Lesen 3 ms je Takt), dort genuegt grob
BREMS_TAKTE = 1000
WOCHE, JAHR = 200, 9600  # Woche gemessen (3 Wochen in 600 Takten), 4 Wochen je Monat und 12 Monate laut updateDateAndTime
ABLESEN = 22  # zwei Bilder zu je 11 Takten: so grob sieht das Programm den Takt auf Stufe 1000
BAU_GRENZE = 20  # gemessen 2 bis 6 Takte vom Befehl bis zum Eintrag
TAKTE_JE_STUECK = 4  # UpdateStockpile, UpdateGranary, UpdateArmory: nur wenn mapTimeInTicks durch 4 teilbar ist
TAKTE_JE_BEWOHNER = 250  # gemessen bei Beliebtheit 87,75
KEIN_BEWOHNER = 4 * TAKTE_JE_BEWOHNER
FEUER_HOECHSTENS = 23  # darueber kommen keine neuen Leute (Wissensstand 13v)
BELIEBTHEIT_UNTEN = 5000  # 100 Punkte = 1 angezeigter Punkt; unter 50 gehen die Leute
FRIST = 600  # Rechnung: Tempo 1000 rund 60 s, Jahr auf Tempo 40 240 s, Treppe 220 s, dazu Start und Kanal
STILLSTAND = 1.0  # rund 10 x die laengste gemessene Luecke (0,098 s); auf langsamen Stufen 10 Takt-Abstaende
POLL = 0.005
KANAL = 0.5  # Hoechstwartezeit auf die Quittung des Moduls
ALTE_SCHALTER = ({"tickpause": "aus"}, {"ladepause": "aus"})  # nichts Scharfes aus frueheren Proben darf den Lauf anhalten
PLATTE_MINDESTENS = 5e9  # der letzte Lauf schrieb 625 MB; das Jahr auf Tempo 40 liest jeden Takt
WERKSTAETTEN = {12, 13, 14, 15, 16, 17, 18}  # rechnen ihren Bildwert selbst aus (Update...Workshop)


class Fehler(RuntimeError):
    pass


class Abbruch(Exception):
    """Beendet den ganzen Lauf: Die Grundlage fuer die Frage des Laufs ist kaputt."""


def ordner(n):
    return STAMM if n == 1 else f"{STAMM} Instanz{n}"


def pruefe_laufinstanz(n):
    if n == DANIELS_INSTANZ:
        raise Fehler("Instanz 5 ist Daniels Spiel und bleibt unberuehrt")
    return n


def logik_text(quelle):
    """Die logik.lua der Quelle mit dem neuen Knopf und Bildwert 15 beim Bauen; Zeilenenden bleiben, wie sie sind."""
    roh = open(quelle, "rb").read().decode("latin-1")
    return _mit_bildwert(_mit_knopf(roh, quelle), quelle)


def _mit_bildwert(roh, quelle):
    if BAU_NEU[3] in roh:
        return roh
    if roh.count(BAU_ALT) != 1 or roh.count(BAU_LOG_ALT) != 1:
        raise Fehler(f"{quelle}: Stelle fuer den Bildwert nicht eindeutig ({roh.count(BAU_ALT)}, {roh.count(BAU_LOG_ALT)} Treffer)")
    i = roh.index(BAU_ALT)
    anfang = roh.rfind("\n", 0, i) + 1
    ende = "\r\n" if "\r\n" in roh[i:i + 200] else "\n"
    block = ende.join(roh[anfang:i] + z for z in BAU_NEU)
    return roh[:anfang] + block + roh[i + len(BAU_ALT):].replace(BAU_LOG_ALT, BAU_LOG_NEU, 1)


def _mit_knopf(roh, quelle):
    if roh.count(NEU):
        return roh
    if roh.count(ANKER) != 1:
        raise Fehler(f"{quelle}: Stelle fuer den neuen Knopf nicht eindeutig ({roh.count(ANKER)} Treffer)")
    i = roh.index(ANKER)
    anfang = roh.rfind("\n", 0, i) + 1
    ende = "\r\n" if "\r\n" in roh[i:i + 200] else "\n"
    return roh[:i + len(ANKER)] + ende + roh[anfang:i] + NEU + roh[i + len(ANKER):]


def logik_einspielen(ziel, quelle, stempel=None):
    """Sichert die alte Datei mit Datum und schreibt die neue. Rueckweg: die Sicherung zurueckkopieren."""
    if "instanz5" in ziel.replace(" ", "").lower():
        raise Fehler("Instanz 5 ist Daniels Spiel und bleibt unberuehrt")
    neu = logik_text(quelle).encode("latin-1")
    if os.path.exists(ziel):
        if open(ziel, "rb").read() == neu:
            return None
        sicherung = f"{ziel[:-4]}.vor_auge_{stempel or time.strftime('%Y%m%d_%H%M%S')}.lua"
        shutil.copy2(ziel, sicherung)
    else:
        sicherung = None
    with open(ziel, "wb") as f:
        f.write(neu)
    return sicherung


def lua_fehler(text):
    """Syntaxfehler der logik.lua, sonst None. Ohne lupa ungeprueft (dann "nicht geprueft")."""
    try:
        import lupa
    except ImportError:
        return "nicht geprueft: lupa fehlt"
    lua = lupa.LuaRuntime(unpack_returned_tuples=True, encoding="latin-1")
    return lua.eval("function(t) local f, e = load(t); return e end")(text)


def modul_eintragen(pfad, stempel=None):
    """Traegt villagestudio in die Ladelisten von ucp-config.yml ein, sichert vorher, prueft danach. Rueckgabe: Sicherung oder None."""
    import yaml

    if "instanz5" in pfad.replace(" ", "").lower():
        raise Fehler("Instanz 5 ist Daniels Spiel und bleibt unberuehrt")
    roh = open(pfad, "rb").read().decode("utf-8")
    alt = yaml.safe_load(roh)
    drin = lambda d, teil: any(e.get("extension") == "villagestudio" for e in d[teil]["load-order"])
    if drin(alt, "config-sparse") and drin(alt, "config-full") and "villagestudio" in (alt["config-sparse"].get("modules") or {}):
        return None
    nl = "\r\n" if "\r\n" in roh else "\n"
    eintrag = f"  - extension: villagestudio{nl}    version: 0.1.0{nl}"
    t = roh
    leer = f"  modules: {{}}{nl}"
    if leer not in t[:t.index("config-full:")]:
        raise Fehler(f"{pfad}: config-sparse.modules ist nicht leer, von Hand ansehen")
    t = t.replace(leer, f"  modules:{nl}    villagestudio:{nl}      config: {{}}{nl}", 1)
    t = t.replace(f"config-full:{nl}", eintrag + f"config-full:{nl}", 1)
    t = t.rstrip("\r\n") + nl + eintrag
    neu = yaml.safe_load(t)
    if not (drin(neu, "config-sparse") and drin(neu, "config-full")):
        raise Fehler(f"{pfad}: Eintrag ist nicht in beiden Ladelisten angekommen")
    for teil in ("config-sparse", "config-full"):
        neu[teil]["load-order"] = [e for e in neu[teil]["load-order"] if e.get("extension") != "villagestudio"]
    neu["config-sparse"]["modules"] = {k: v for k, v in neu["config-sparse"]["modules"].items() if k != "villagestudio"} or {}
    if neu != alt:
        raise Fehler(f"{pfad}: Das Eintragen haette noch etwas anderes geaendert")
    sicherung = f"{pfad}.vor_auge_{stempel or time.strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(pfad, sicherung)
    with open(pfad, "wb") as f:
        f.write(t.encode("utf-8"))
    return sicherung


def warte_auf(bedingung, sekunden, was, schlaf=0.25, uhr=time.time, ruhe=time.sleep):
    ende = uhr() + sekunden
    while uhr() < ende:
        if bedingung():
            return
        ruhe(schlaf)
    raise Fehler(f"nach {sekunden} s nicht erreicht: {was}")


def name_von(k, nummer):
    roh = b"".join(w.to_bytes(4, "little") for w in k.peek(NAMEN + nummer * NAMENSLAENGE, 12))
    return roh.split(b"\0")[0].decode("latin-1")


def warte_auf_modul(k, sekunden=120, ruhe=time.sleep, uhr=time.time):
    """Das Modul meldet "aktiv", bevor das Spiel im Menue ist und Befehle liest (Lauf F 02.11.2026 18:12, gemessen)."""
    def antwortet():
        try:
            k.peek(ANSICHT)
            return True
        except Exception:  # noqa: BLE001  jede Kanalstoerung heisst hier nur: noch nicht
            return False
    warte_auf(antwortet, sekunden, "Modul antwortet auf Befehle", schlaf=2.0, ruhe=ruhe, uhr=uhr)


def burgenbau_starten(k, karte=KARTE, warte=60, ruhe=time.sleep):
    """Hauptmenue -> Burgenbau -> Karte markieren -> Start; jeder Schritt wird an der Menueansicht geprueft."""
    if k.peek(ANSICHT)[0] != HAUPTMENUE:
        k.befehl({"menue": HAUPTMENUE}, 1.5)
        warte_auf(lambda: k.peek(ANSICHT)[0] == HAUPTMENUE, 10, "Hauptmenue (Ansicht 41)", ruhe=ruhe)  # die Quittung kommt vor dem Wechsel
    k.befehl({"hauptmenue": 3}, 1.5)
    warte_auf(lambda: k.peek(ANSICHT)[0] == KARTENWAHL, 10, "Kartenwahl Burgenbau (Ansicht 35)", ruhe=ruhe)
    anzahl = k.peek(GESAMT)[0]
    if not 0 < anzahl <= 500:
        raise Fehler(f"Kartenliste unplausibel: {anzahl} Eintraege")
    namen = [name_von(k, nr) for nr in k.peek(LISTE, anzahl)]
    if karte not in namen:
        raise Fehler(f"'{karte}' steht nicht in der Kartenliste ({anzahl} Eintraege)")
    n = namen.index(karte)
    scroll = max(0, n - 12)
    k.liste([{"poke": SCROLL, "wert": scroll}, {"poke": MARKIERT, "wert": n - scroll},
             {"knopf": "SingleplayerMapChoice_ButtonsAndHands", "nr": KNOPF_START}], 4.0)
    warte_auf(lambda: k.peek(ANSICHT)[0] == IN_PARTIE, warte, "Partie laeuft (Ansicht 14)", ruhe=ruhe)
    k.befehl({"eigenerPlatz": 1}, 0.8)
    return {"karte": karte, "eintrag": n, "von": anzahl}


# --- Lesen: direkt aus dem Spielspeicher. Kostet das Spiel nichts, schreibt nichts ins Log. ---
SPIELER, SPIELER_SCHRITT = 0x0115BDF8, 0x39F4
FELD = {"popularity": 0x60, "populationCap": 0x74, "availablePeasantsAtFire": 0x88, "storageMarketFailState": 0x2C, "armySize": 0x53C, "totalFood": 0x209C,
        "currentPopulation": 0x2180, "taxesSetting": 0x2188, "rationsSetting": 0x218C}
FELD_START, FELD_BESTAND = 0x46C, 0x4D0
GEBAEUDE, G_SCHRITT, G_ANZAHL = 0xF98520, 0x32C, 2000
G_ZUSTAND, G_TYP, G_BESITZER, G_UID, G_X, G_Y, G_BILDWERT, G_OFFEN, G_TOR = 0xE4, 0xE6, 0xEA, 0xEC, 0x102, 0x104, 0x116, 0x1B0, 0x2B7
ARBEITER_TABELLE = 0x005B8B58  # DAT_EmployeeCountPerBuildingType, 4 Bytes je Typ
JAHR_ADR, MONAT_ADR, WOCHE_ADR, HAT_BURG_KORN = 0x0117CAB8, 0x0117CAB4, 0x0117CAB0, 0x0117C790
ANZEIGEN, ANZEIGE_BURG_KORN = 0x00DF42B4, 20  # DAT_PointerToDisplayElementStackTop; updateDateAndTime fragt Nummer 0x14
SCHLAF = 0x0115DF8C  # + Spieler * Schritt + Typ, ProcessBuildingSleepUpdate
PECHGRAEBEN, PG_SCHRITT, PG_ANZAHL, PG_BESITZER = 0x01FD228C, 20, 4000, 8
KARTENMASKE, ZEILEN, LOGIK, KACHELN = 0x021AEC98, 0x023372F8, 0x01BF8368, 81000
EINHEITEN_ANZAHL, EINHEITEN, E_SCHRITT, E_DA, E_TYP, E_BESITZER = 0x01387F38, 0x0138854C, 1168, 0x8C, 0x8E, 0x96
BIT_MAUER, BIT_GRABEN = 0x100, 0x40000000


class Speicher:
    def __init__(self, quelle):
        self.q = quelle

    def i32(self, adr):
        return struct.unpack("<i", self.q.lies(adr, 4))[0]

    def takt(self):
        return self.i32(TICK)

    def pause(self):
        return self.i32(PAUSE)

    def kalender(self):
        return self.i32(JAHR_ADR), self.i32(MONAT_ADR), self.i32(WOCHE_ADR)

    def spieler(self, name, sp=1):
        return self.i32(SPIELER + sp * SPIELER_SCHRITT + FELD[name])

    def waren(self, sp=1):
        return list(struct.unpack("<25i", self.q.lies(SPIELER + sp * SPIELER_SCHRITT + FELD_BESTAND, 100)))

    def startwaren(self, sp=1):
        return list(struct.unpack("<25i", self.q.lies(SPIELER + sp * SPIELER_SCHRITT + FELD_START, 100)))

    def start_adresse(self, ware, sp=1):
        return SPIELER + sp * SPIELER_SCHRITT + FELD_START + ware * 4

    def anzeige_burg_korn(self):
        a = struct.unpack("<I", self.q.lies(ANZEIGEN, 4))[0]
        for _ in range(100):
            if not a:
                return 0
            if self.i32(a + 8) == ANZEIGE_BURG_KORN:
                return self.i32(a + 0xC)
            a = struct.unpack("<I", self.q.lies(a + 0x20, 4))[0]
        return 0

    def gebaeude(self, sp=1):
        roh = self.q.lies(GEBAEUDE, G_SCHRITT * G_ANZAHL)
        aus = []
        h = lambda o: struct.unpack_from("<h", roh, o)[0]  # noqa: E731
        for i in range(1, G_ANZAHL):
            b = i * G_SCHRITT
            z = h(b + G_ZUSTAND)
            if z in (0, 3) or (sp is not None and h(b + G_BESITZER) != sp):  # 0 leer, 3 abgerissen
                continue
            aus.append({"nr": i, "typ": h(b + G_TYP), "x": h(b + G_X), "y": h(b + G_Y), "v": h(b + G_BILDWERT), "offen": h(b + G_OFFEN),
                        "uid": struct.unpack_from("<i", roh, b + G_UID)[0], "tor": roh[b + G_TOR]})
        return aus

    def arbeiter_je_typ(self, typ):
        return struct.unpack("<h", self.q.lies(ARBEITER_TABELLE + typ * 4, 2))[0]

    def pechgraeben(self, sp=1):
        roh = self.q.lies(PECHGRAEBEN, PG_SCHRITT * PG_ANZAHL)
        return sum(1 for i in range(1, PG_ANZAHL) if struct.unpack_from("<h", roh, i * PG_SCHRITT + PG_BESITZER)[0] == sp)

    def schlaeft(self, typ, sp=1):
        return self.q.lies(SCHLAF + sp * SPIELER_SCHRITT + typ, 1)[0]

    def logik(self, x, y):
        b = self.i32(ZEILEN + y * 12 + 8)
        return struct.unpack("<I", self.q.lies(LOGIK + (b + x) * 4, 4))[0]

    def felder_mit_bit(self, bit):
        maske, zeilen, logik = self.q.lies(KARTENMASKE, 400 * 400), self.q.lies(ZEILEN, 400 * 12), self.q.lies(LOGIK, 4 * KACHELN)
        aus = []
        for y in range(400):
            b = struct.unpack_from("<i", zeilen, y * 12 + 8)[0]
            for x in range(400):
                if maske[y * 400 + x] and 0 <= b + x < KACHELN and struct.unpack_from("<I", logik, (b + x) * 4)[0] & bit:
                    aus.append((x, y))
        return aus

    def einheiten(self, sp=1):
        n = min(self.i32(EINHEITEN_ANZAHL), 2500)
        roh = self.q.lies(EINHEITEN, n * E_SCHRITT) if n > 0 else b""
        h = lambda o: struct.unpack_from("<h", roh, o)[0]  # noqa: E731
        z = collections.Counter()
        for i in range(1, n):
            b = i * E_SCHRITT
            if h(b + E_DA) and h(b + E_BESITZER) == sp:
                z[h(b + E_TYP)] += 1
        return z


# --- Der Lauf ---
BURG, KORN, HUETTE, LAGER, WAFFEN, KASERNE, PECHGRUBE, PECHGRABEN, FALLGRUBE = 41, 19, 1, 10, 11, 9, 6, 68, 67
ANKER_BURG = (212, 188)  # dort stand die Burg im letzten Lauf, mitten an der Oase; die Spielpruefung entscheidet
BODEN = {5: 0x80000, 20: 0x20000, PECHGRUBE: 0x80000000}  # Eisen, Fels, Pech (BFRE_NOT_OIL_MARSH)
HUETTEN = 6  # Arbeitsplaetze 34 + rund 24 am Feuer (Wissensstand 13v) = 58 = Burg 10 + 6 x 8
LAGER_BEFEHLE = 3  # je Befehl 4 Felder (gemessen); Holz braucht 4, die 7 anderen Waren je 1, Rest fuer die Warenketten
GOLD = 100000
LAGERWAREN = {2: 96, 3: 16, 4: 48, 6: 48, 7: 16, 9: 32, 14: 16, 16: 32}  # je ein volles Feld laut StorageLimitResourceTypeArray; Holz mehr, die Bauten kosten Holz
ESSEN = {10: 60, 11: 60, 12: 60, 13: 40}  # der Kornspeicher fasst 250, die Karte bringt 20 Aepfel
WAFFENLAGER_FASST, LOS = 50, 5  # getArmoryIDIfSpaceLeft: 50 ueber alle Waffen zusammen (Lauf 21:30: 7+7+6x6, der Rest hing); Handel je 5 Stueck
WAFFEN_WAREN = {w: 5 for w in range(17, 25)}  # Anwerben braucht je Art hoechstens 3 (Eisenruestung), der Rest bleibt frei fuer Handel und Schmieden
ESSEN_UNTEN, ESSEN_NACH = 100, 100
ZUSATZ = (33, 33, 12, 62)  # zwei Milchhoefe mehr (dairyFarmVariationMod4), zweiter Bogenmacher, Galgen zum Abreissen
ZUSATZ_PECHGRAEBEN = 3
ABREISSEN = (12, 62)  # die Zusatz-Kopien; die erste Kopie jeder Art bleibt fuer die Warenketten stehen
ANWERBEN = {9: [22, 23, 24, 25, 26, 27, 28], 8: [70, 71, 72, 73, 74, 75, 76], 24: [29, 30], 25: [5], 38: [37]}
HANDELSWAREN = [w for w in range(2, 25) if w != 15]
SPEER = 19
STEUERSTUFEN, RATIONEN = range(12), range(5)
TOR_ZU, TOR_AUF, TOR_FERTIG = 10, 11, 12  # GateOpenOrClose; UpdateGateHouse macht aus beiden nach dem Umschalten 12 (Lauf F: 11 dann 12)
BEFEHL_MAUER, BEFEHL_GRABEN, BEFEHL_STEUER, BEFEHL_RATION, BEFEHL_HANDEL, BEFEHL_SCHLAF, BEFEHL_TOR = 25, 21, 34, 35, 38, 43, 45


def naechste(zeilen, x0, y0, anker, ausser=()):
    """Die vom Spiel erlaubte Stelle (+) am naechsten zum Anker. zeilen: Spielpruefung des Fensters ab (x0, y0)."""
    best = None
    for j, z in enumerate(zeilen):
        for i, c in enumerate(z):
            if c == "+" and (x0 + i, y0 + j) not in ausser:
                d = max(abs(x0 + i - anker[0]), abs(y0 + j - anker[1]))
                if best is None or d < best[0]:
                    best = (d, x0 + i, y0 + j)
    return best[1:] if best else None


def spirale(mitte, schritt, n):
    """Stellen im Gitter um die Mitte, innen zuerst: Die Bauten stehen auseinander, Arbeiter kommen hin und man sieht jedes."""
    orte = [(mitte[0] + i * schritt, mitte[1] + j * schritt) for i in range(-9, 10) for j in range(-9, 10) if (i, j) != (0, 0)]
    orte = [p for p in orte if 8 <= p[0] <= 391 and 8 <= p[1] <= 391]
    orte.sort(key=lambda p: (max(abs(p[0] - mitte[0]), abs(p[1] - mitte[1])), p))
    return orte[:n]


def freier_streifen(zeilen, x0, y0, breite, hoehe):
    """Linke obere Ecke eines ganz freien Rechtecks, sonst None."""
    for j in range(len(zeilen) - hoehe + 1):
        for i in range(len(zeilen[j]) - breite + 1):
            if all(zeilen[j + k][i:i + breite] == "+" * breite for k in range(hoehe)):
                return x0 + i, y0 + j
    return None


class Lauf:
    def __init__(self, k, s, arten, rek, schreib, frist=FRIST, uhr=time.perf_counter, ruhe=time.sleep, stop=lambda: False):
        self.k, self.s, self.arten, self.rek, self.schreib = k, s, arten, rek, schreib
        self.uhr, self.ruhe, self.stop, self.frist = uhr, ruhe, stop, frist
        self.ende = uhr() + frist
        self.tempo = TEMPO_LAUF
        self.puls = (s.takt(), uhr())
        self.funde, self.gebaut, self.keine_stelle = [], collections.defaultdict(list), []
        self.mitte = ANKER_BURG
        self.anker = iter(())
        self.pruefe_lage = self.frei_bis = 0
        self.lage_an = False
        self.naechste_lage = self.naechstes_essen = 0
        self.bewohner = None
        self.bewohner_wache = True
        self.beliebtheit_frei = False
        self.ergebnis = {}

    # Wache: in jedem Warten
    def stillstand_grenze(self):
        return max(STILLSTAND, 10.0 / self.tempo)

    def wach(self):
        jetzt = self.uhr()
        if jetzt > self.ende:
            raise Abbruch(f"Frist von {self.frist} s ist um")
        if self.stop():
            raise Abbruch("von Hand gestoppt")
        try:
            t = self.s.takt()
        except OSError as e:
            raise Abbruch(f"Spiel laeuft nicht mehr: {e}") from e
        grund = self.rek.fehler()
        if grund:
            raise Abbruch(f"Aufzeichnung: {grund}")
        if t != self.puls[0]:
            self.puls = (t, jetzt)
        elif jetzt - self.puls[1] > self.stillstand_grenze():
            raise Abbruch(f"seit {jetzt - self.puls[1]:.1f} s kein neuer Takt (Takt {t}, Tempo {self.tempo})")
        if self.lage_an and t >= self.naechste_lage:
            self.naechste_lage = t + 50
            self.lage_pruefen(t)

    def lage_pruefen(self, t):
        s = self.s
        bel, pop, deckel, feuer = s.spieler("popularity"), s.spieler("currentPopulation"), s.spieler("populationCap"), s.spieler("availablePeasantsAtFire")
        frei = self.beliebtheit_frei or t < self.frei_bis
        if not frei and bel < BELIEBTHEIT_UNTEN:
            raise Abbruch(f"Beliebtheit {bel / 100:.2f} unter 50 (Takt {t}, Essen {s.spieler('totalFood')}, Steuer {s.spieler('taxesSetting')})")
        if s.spieler("totalFood") < ESSEN_UNTEN and t >= self.naechstes_essen:
            self.naechstes_essen = t + 800
            self.startwaren_geben({13: ESSEN_NACH}, "Essen nachgeliefert, es ist hier nicht die Pruefgroesse")
        # Neue Leute braucht der Lauf nur fuer offene Arbeitsplaetze, und die Rate 1 je 250 Takte ist nur bis zum Steuertest gemessen
        if not self.bewohner_wache or self.bewohner is None or pop > self.bewohner[0] or frei or pop >= deckel or bel < BELIEBTHEIT_UNTEN or feuer > FEUER_HOECHSTENS or offene_plaetze(self) == 0:
            self.bewohner = (pop, t)
        elif t - self.bewohner[1] > KEIN_BEWOHNER:
            raise Abbruch(f"seit {t - self.bewohner[1]} Takten kein neuer Bewohner (Leute {pop} von {deckel}, Feuer {feuer}, Beliebtheit {bel / 100:.2f})")

    def warte_takte(self, n, bed=None):
        """Laeuft n Takte oder bis bed() wahr ist. Rueckgabe: bed wahr geworden (ohne bed: True)."""
        ziel = self.s.takt() + n
        while True:
            self.wach()
            if bed and bed():
                return True
            if self.s.takt() >= ziel:
                return bed is None
            self.ruhe(POLL)

    def messe(self, n):
        """Takte je Sekunde ueber n Takte, von Taktwechsel zu Taktwechsel."""
        a = self.s.takt()
        while self.s.takt() == a:
            self.wach()
            self.ruhe(POLL)
        a, t0 = self.s.takt(), self.uhr()
        while self.s.takt() < a + n:
            self.wach()
            self.ruhe(POLL)
        d, b = self.uhr() - t0, self.s.takt()
        return {"rate": (b - a) / d if d > 0 else 0.0, "takte": b - a, "sekunden": d}

    def wirkung(self, was, ok, **daten):
        self.schreib({"wirkung": was, "ok": bool(ok), **daten})
        if not ok:
            self.funde.append({"was": was, **daten})
        return ok

    def startwaren_geben(self, mengen, grund):
        jetzt = self.s.startwaren()
        self.k.liste([{"poke": self.s.start_adresse(w), "wert": jetzt[w] + m} for w, m in mengen.items()], KANAL)
        self.schreib({"eingang": {str(w): m for w, m in mengen.items()}, "takt": self.s.takt(), "grund": grund})

    def warte_eingebucht(self, mengen):
        """UpdateStockpile bucht 1 Stueck je 4 Takte ins Lager, Kornspeicher und Waffenlager je Art 1 Stueck je 4 Takte."""
        lager = sum(m for w, m in mengen.items() if w in LAGERWAREN) + self.s.startwaren()[2]
        rest = max([lager] + [m for w, m in mengen.items() if w not in LAGERWAREN] + [0])
        grenze = TAKTE_JE_STUECK * rest + 20
        ok = self.warte_takte(grenze, lambda: not any(self.s.startwaren()[w] for w in mengen))
        if not ok:
            raise Abbruch(f"Waren kommen nach {grenze} Takten nicht an, offen: {[(w, self.s.startwaren()[w]) for w in mengen if self.s.startwaren()[w]]}; Bestand {self.s.waren()}")
        return grenze

    # Bauen
    def boden_anker(self, typ):
        felder = self.s.felder_mit_bit(BODEN[typ])
        felder.sort(key=lambda p: max(abs(p[0] - self.mitte[0]), abs(p[1] - self.mitte[1])))
        aus = []
        for p in felder:
            if all(max(abs(p[0] - a), abs(p[1] - b)) >= 20 for a, b in aus):
                aus.append(p)
        return aus[:8]

    def stelle_fuer(self, typ, anker=None, ausser=()):
        g = self.arten[typ]
        anker_liste = self.boden_anker(typ) if typ in BODEN else [anker or next(self.anker, self.mitte)]
        for a in anker_liste:
            for r in (12, 40, 80):
                x0, y0, x1, y1 = max(0, a[0] - r), max(0, a[1] - r), min(399, a[0] + r), min(399, a[1] + r)
                st = naechste(self.k.platzkarte(g["mapper"], g["b"], x0, y0, x1, y1), x0, y0, a, ausser)
                if st:
                    return st
        return None

    def setze(self, typ, anker=None, wert=None, pflicht=True):
        """Baut typ auf eine vom Spiel erlaubte Stelle, ohne das Spiel anzuhalten. Rueckgabe: Eintrag, None wenn keine Stelle erlaubt ist.
        pflicht=False: Der Bau ist keine Grundlage des Laufs, scheitert er, kommt None zurueck statt eines Abbruchs."""
        g = self.arten[typ]
        soll = drehwert(g["mapper"]) if wert is None else wert
        versucht = []
        anker = anker or next(self.anker, self.mitte)
        for _ in range(3):
            st = self.stelle_fuer(typ, anker, versucht)
            if st is None:
                if typ == PECHGRUBE or versucht or not pflicht:
                    break
                raise Abbruch(f"Art {typ} ({g.get('name')}): keine vom Spiel erlaubte Stelle")
            versucht.append(st)
            vorher = {e["nr"] for e in self.s.gebaeude()}
            pech = self.s.pechgraeben() if typ == PECHGRABEN else 0
            self.k.befehl({"baue": {"mapper": g["mapper"], "x": st[0], "y": st[1], "groesse": g["b"], "richtung": soll}}, KANAL)
            neu = []

            def da():
                neu[:] = [e for e in self.s.gebaeude() if e["nr"] not in vorher and e["typ"] == typ]
                return bool(neu) or (typ == PECHGRABEN and self.s.pechgraeben() > pech)
            if self.warte_takte(BAU_GRENZE, da):
                for e in neu:
                    self.gebaut[typ].append(e["nr"])
                if neu and typ not in WERKSTAETTEN and neu[0]["v"] != soll:
                    self.wirkung(f"Bildwert Art {typ}", False, soll=soll, ist=neu[0]["v"])
                return neu[0] if neu else {"nr": 0, "typ": typ, "x": st[0], "y": st[1]}
        if typ == PECHGRUBE and not versucht:
            self.keine_stelle.append(typ)
            return None
        if not pflicht:
            return None
        raise Abbruch(f"Art {typ} ({g.get('name')}): an den erlaubten Stellen {versucht} steht nach je {BAU_GRENZE} Takten kein Gebaeude")


def abschnitt_grundstock(l):
    s = l.s
    l.k.befehl({"gold": GOLD}, KANAL)
    if not l.warte_takte(ABLESEN, lambda: s.waren()[15] == GOLD):
        raise Abbruch(f"Gold kam nicht an: {s.waren()[15]}")
    burg = l.setze(BURG, ANKER_BURG)
    l.mitte = (burg["x"], burg["y"])
    arten_rest = [t for t in l.arten if t != BURG]
    l.anker = iter(spirale(l.mitte, 10, len(arten_rest) + HUETTEN + 40))
    l.setze(KORN)
    if not l.warte_takte(WOCHE, lambda: s.anzeige_burg_korn() == 0):
        raise Abbruch(f"Kornspeicher steht, aber Anzeige 20 bleibt {s.anzeige_burg_korn()}")
    woche = s.kalender()
    if not l.warte_takte(WOCHE + ABLESEN, lambda: s.kalender() != woche):
        raise Abbruch(f"Kalender zaehlt nicht: {woche} nach {WOCHE + ABLESEN} Takten")
    for _ in range(HUETTEN):
        l.setze(HUETTE)
    letzte = l.mitte
    for _ in range(LAGER_BEFEHLE):
        e = l.setze(LAGER, letzte)
        letzte = (e["x"], e["y"])
    l.setze(WAFFEN)
    mengen = {**LAGERWAREN, **ESSEN, **WAFFEN_WAREN}
    l.startwaren_geben(mengen, "Startwaren")
    grenze = l.warte_eingebucht(mengen)
    # updateBuildings rechnet den Deckel in jedem Takt neu auf: Mitten darin steht er kurz auf 0 (Lauf 21:30 Takt 3244)
    if not l.warte_takte(ABLESEN, lambda: s.spieler("populationCap") >= 10 + HUETTEN * 8):
        raise Abbruch(f"Wohnplaetze {s.spieler('populationCap')}, erwartet mindestens {10 + HUETTEN * 8}")
    l.lage_an = True
    return {"burg": l.mitte, "kalender": s.kalender(), "deckel": s.spieler("populationCap"), "eingebucht_grenze": grenze, "waren": s.waren()}


def abschnitt_bauen(l):
    s = l.s
    for typ in sorted(l.arten):
        if not l.gebaut[typ] and typ != BURG:
            l.setze(typ)
    for typ in ZUSATZ + (PECHGRABEN,) * ZUSATZ_PECHGRAEBEN:
        if l.setze(typ, pflicht=False) is None:
            l.wirkung(f"Zusatzbau Art {typ}", False)
    jetzt = s.waren()
    start = s.startwaren()
    nach = {w: m - jetzt[w] - start[w] for w, m in LAGERWAREN.items() if m - jetzt[w] - start[w] > 0}
    if nach:
        l.startwaren_geben(nach, "nachgefuellt: Die Bauten haben Waren gekostet")
        l.warte_eingebucht(nach)
    return {"arten": sum(1 for t in l.arten if l.gebaut[t]), "keine_stelle": l.keine_stelle, "pechgraeben": s.pechgraeben(), "nachgefuellt": nach}


def offene_plaetze(l):
    return sum(e["offen"] for e in l.s.gebaeude())


def abschnitt_bauern(l):
    gesamt = sum(l.s.arbeiter_je_typ(e["typ"]) for e in l.s.gebaeude())
    grenze = gesamt * TAKTE_JE_BEWOHNER
    voll = l.warte_takte(grenze, lambda: offene_plaetze(l) == 0)
    l.bewohner_wache = False  # ob am Ende alle Plaetze besetzt sind, sagt die Schlusspruefung
    bremsprobe(l, "nach den Bauern")
    return {"arbeitsplaetze": gesamt, "grenze": grenze, "voll": voll, "offen": offene_plaetze(l), "leute": l.s.spieler("currentPopulation"), "beliebtheit": l.s.spieler("popularity")}


def _handel(l):
    s = l.s
    # Erst verkaufen: Das Waffenlager fasst 50, jedes Waffen-Los muss beim Kaufen noch hineinpassen
    vor = s.waren()
    l.k.liste([{"spielbefehl": {"nr": BEFEHL_HANDEL, "werte": [1, w]}} for w in HANDELSWAREN], KANAL)
    l.warte_takte(10)
    nach = s.waren()
    l.wirkung("verkaufen", nach[15] > vor[15], gold=[vor[15], nach[15]], ohne_abgang=[w for w in HANDELSWAREN if nach[w] >= vor[w]])
    vor = nach
    l.k.liste([{"spielbefehl": {"nr": BEFEHL_HANDEL, "werte": [0, w]}} for w in HANDELSWAREN], KANAL)
    l.warte_takte(10)
    nach = s.waren()
    fehlt = [w for w in HANDELSWAREN if nach[w] <= vor[w]]
    l.wirkung("kaufen", nach[15] < vor[15] and len(fehlt) < len(HANDELSWAREN), gold=[vor[15], nach[15]], ohne_zuwachs=fehlt)
    # Kauf bei vollem Waffenlager: Das Spiel lehnt ab und nennt den Grund (storageMarketFailState 10)
    lose = (WAFFENLAGER_FASST - sum(WAFFEN_WAREN.values())) // LOS
    l.k.liste([{"spielbefehl": {"nr": BEFEHL_HANDEL, "werte": [0, SPEER]}} for _ in range(lose)], KANAL)
    l.warte_takte(10)
    vor = s.waren()
    l.k.liste([{"spielbefehl": {"nr": BEFEHL_HANDEL, "werte": [0, SPEER]}}], KANAL)
    l.warte_takte(10)
    nach = s.waren()
    l.schreib({"messung": "Kauf bei vollem Waffenlager", "speer": [vor[SPEER], nach[SPEER]], "gold": [vor[15], nach[15]], "fail_state": s.spieler("storageMarketFailState")})
    # wieder Platz schaffen: Die Waffenschmieden sollen abliefern koennen, und fuers Anwerben bleibt die geplante Menge
    zurueck = (s.waren()[SPEER] - WAFFEN_WAREN[SPEER]) // LOS
    if zurueck > 0:
        l.k.liste([{"spielbefehl": {"nr": BEFEHL_HANDEL, "werte": [1, SPEER]}} for _ in range(zurueck)], KANAL)
        l.warte_takte(10)


def _steuern_rationen(l):
    s = l.s
    l.beliebtheit_frei = True
    alt_steuer, alt_ration = s.spieler("taxesSetting"), s.spieler("rationsSetting")
    roh = []
    for st in STEUERSTUFEN:
        l.k.befehl({"spielbefehl": {"nr": BEFEHL_STEUER, "werte": [st]}}, KANAL)
        l.warte_takte(WOCHE)
        roh.append(s.spieler("taxesSetting"))
    l.k.befehl({"spielbefehl": {"nr": BEFEHL_STEUER, "werte": [alt_steuer]}}, KANAL)
    l.wirkung("Steuern", len(set(roh)) == len(STEUERSTUFEN), rohwerte=roh, beliebtheit=s.spieler("popularity"))
    roh = []
    for st in RATIONEN:
        l.k.befehl({"spielbefehl": {"nr": BEFEHL_RATION, "werte": [st]}}, KANAL)
        l.warte_takte(WOCHE)
        roh.append(s.spieler("rationsSetting"))
    l.k.befehl({"spielbefehl": {"nr": BEFEHL_RATION, "werte": [alt_ration]}}, KANAL)
    l.wirkung("Rationen", len(set(roh)) == len(RATIONEN), rohwerte=roh, beliebtheit=s.spieler("popularity"))
    l.warte_takte(ABLESEN)
    l.wirkung("Einstellungen zurueck", s.spieler("taxesSetting") == alt_steuer and s.spieler("rationsSetting") == alt_ration, steuer=s.spieler("taxesSetting"), ration=s.spieler("rationsSetting"))
    l.beliebtheit_frei = False
    l.frei_bis = s.takt() + 10 * WOCHE  # die Beliebtheit steigt wochenweise zurueck, erst danach gilt die Untergrenze wieder


def _mauer_graben(l):
    s = l.s
    a = (l.mitte[0] + 40, l.mitte[1] + 40)
    for r in (20, 40, 60):
        x0, y0, x1, y1 = max(0, a[0] - r), max(0, a[1] - r), min(399, a[0] + r), min(399, a[1] + r)
        st = freier_streifen(l.k.platzkarte(l.arten[FALLGRUBE]["mapper"], 1, x0, y0, x1, y1), x0, y0, 13, 9)  # 1 Feld gross: "erlaubt" heisst hier frei
        if st:
            break
    else:
        l.wirkung("Mauer", False, grund="kein freier Streifen")
        return
    x, y = st
    l.k.befehl({"spielbefehl": {"nr": BEFEHL_MAUER, "werte": [x, y, x + 12, y, 25, 13]}}, KANAL)
    l.k.befehl({"spielbefehl": {"nr": BEFEHL_MAUER, "werte": [x, y + 3, x + 12, y + 3, 46, 13]}}, KANAL)
    l.k.befehl({"spielbefehl": {"nr": BEFEHL_GRABEN, "werte": [x, y + 8, 0, 0x40000000, 2]}}, KANAL)
    l.warte_takte(20)
    l.wirkung("Mauer", s.logik(x, y) & BIT_MAUER, ort=[x, y], stein=s.waren()[4])
    l.wirkung("Graben", s.logik(x, y + 8) & BIT_GRABEN, ort=[x, y + 8])


def _tore(l):
    s = l.s
    for typ in (45, 46):
        nr = l.gebaut[typ][0] if l.gebaut[typ] else None
        e = next((g for g in s.gebaeude() if g["nr"] == nr), None)
        if not e:
            l.wirkung(f"Tor {typ}", False, grund="steht nicht")
            continue
        for zustand in (TOR_AUF, TOR_ZU):
            l.k.befehl({"spielbefehl": {"nr": BEFEHL_TOR, "werte": [nr, zustand, e["uid"]]}}, KANAL)
            l.warte_takte(10)
            ist = next(g for g in s.gebaeude() if g["nr"] == nr)["tor"]
            l.wirkung(f"Tor {typ} auf {zustand}", ist in (zustand, TOR_FERTIG), ist=ist)


def _schlafen(l):
    typ = 12
    vor = l.s.schlaeft(typ)
    l.k.befehl({"spielbefehl": {"nr": BEFEHL_SCHLAF, "werte": [typ]}}, KANAL)
    l.warte_takte(10)
    an = l.s.schlaeft(typ)
    l.k.befehl({"spielbefehl": {"nr": BEFEHL_SCHLAF, "werte": [typ]}}, KANAL)
    l.warte_takte(10)
    l.wirkung("Arbeit ruhen lassen", an != vor and l.s.schlaeft(typ) == vor, vor=vor, an=an, zurueck=l.s.schlaeft(typ))


def _abreissen(l):
    s = l.s
    for typ in ABREISSEN:
        nr = l.gebaut[typ][-1] if len(l.gebaut[typ]) > 1 else None
        if nr is None:
            l.wirkung(f"Abreissen Art {typ}", False, grund="keine Zusatz-Kopie")
            continue
        vor = s.waren()
        l.k.befehl({"abreissen": {"nr": nr}}, KANAL)
        weg = l.warte_takte(100, lambda: nr not in {e["nr"] for e in s.gebaeude()})
        l.gebaut[typ].remove(nr)
        nach = s.waren()
        l.wirkung(f"Abreissen Art {typ}", weg, nr=nr, zurueck={w: nach[w] - vor[w] for w in (2, 4, 6, 7, 15) if nach[w] != vor[w]})


def _anwerben(l):
    s = l.s
    auftraege = [(e, g) for g, es in ANWERBEN.items() for e in es if l.gebaut[g]]
    l.warte_takte(len(auftraege) * TAKTE_JE_BEWOHNER, lambda: s.spieler("availablePeasantsAtFire") >= len(auftraege))
    vor = s.einheiten()
    l.k.liste([{"werbe": {"typ": e, "gebaeude": l.gebaut[g][0]}} for e, g in auftraege], KANAL)
    l.warte_takte(60)  # die Verwandlung dauert rund 33 Takte (UpdatePeasant)
    nach = s.einheiten()
    fehlt = [e for e, _ in auftraege if nach[e] <= vor[e]]
    l.wirkung("Anwerben", not fehlt, versucht=len(auftraege), ohne_einheit=fehlt, feuer=s.spieler("availablePeasantsAtFire"), heer=s.spieler("armySize"))


def _zweite_kaserne(l):
    alt = l.gebaut[KASERNE][0] if l.gebaut[KASERNE] else None
    e = l.setze(KASERNE, pflicht=False)
    l.warte_takte(20)
    da = {g["nr"] for g in l.s.gebaeude()}
    l.wirkung("zweite Kaserne ersetzt die erste", e and e["nr"] in da and alt not in da, alt=alt, neu=e and e["nr"])
    if alt in l.gebaut[KASERNE] and alt not in da:
        l.gebaut[KASERNE].remove(alt)


def abschnitt_schalten(l):
    for schritt in (_handel, _steuern_rationen, _mauer_graben, _tore, _schlafen, _abreissen, _anwerben, _zweite_kaserne):
        schritt(l)
    return {"funde": len(l.funde)}


def abschnitt_ketten(l):
    s = l.s
    a = s.takt()
    jahr0 = s.kalender()[0]

    def fertig():
        t, st = s.takt(), l.rek.felder()
        return t - a >= JAHR and st is not None and t - (st.get("letzter_neuer_takt") or a) >= JAHR
    gemessen = l.warte_takte(2 * JAHR, fertig)
    st = l.rek.felder() or {}
    bremsprobe(l, "nach den Warenketten")
    return {"takte": s.takt() - a, "gemessenes_ende": gemessen, "felder": st.get("felder"), "letzter_neuer_takt": st.get("letzter_neuer_takt"), "jahreswechsel": s.kalender()[0] - jahr0, "offen": offene_plaetze(l), "waren": s.waren()}


def bremsprobe(l, wann):
    """Zieht das Lesen hier Tempo ab? Ohne, mit, ohne Lesen auf Stufe 1000. Ein einzelner Ruckler ist kein Bremsen, darum einmal Wiederholung."""
    from selfaware.tools.analysis.auge_auswertung import WIDERLEGT, a4_tempotreppe

    for versuch in (1, 2):
        l.rek.aussetzen(True)
        o1 = l.messe(BREMS_TAKTE)
        l.rek.aussetzen(False)
        m = l.messe(BREMS_TAKTE)
        l.rek.aussetzen(True)
        o2 = l.messe(BREMS_TAKTE)
        l.rek.aussetzen(False)
        e = a4_tempotreppe([{"tempo": l.tempo, "soll": BREMS_TAKTE, "gezaehlt": min(o1["takte"], m["takte"], o2["takte"]), "sekunden": min(o1["sekunden"], m["sekunden"], o2["sekunden"]),
                             "ohne_1": o1["rate"], "mit": m["rate"], "ohne_2": o2["rate"], "gelesen": 0, "gesamt": 0}])
        l.schreib({"bremsprobe": wann, "versuch": versuch, "ohne_1": round(o1["rate"], 1), "mit": round(m["rate"], 1), "ohne_2": round(o2["rate"], 1), "ergebnis": e.status})
        if e.status != WIDERLEGT:
            return
    raise Abbruch(f"Das Lesen bremst {wann}: {e.text}")


def abschnitt_jahr40(l):
    s = l.s
    l.rek.beenden()
    tempo_setzen(l.k, TEMPO_JEDER_TAKT)
    l.tempo = TEMPO_JEDER_TAKT
    l.rek.starten("jahr40", TEMPO_JEDER_TAKT, streng=True)
    warte_auf(l.rek.laeuft, 60, "Aufzeichnung Tempo 40 laeuft", uhr=l.uhr, ruhe=l.ruhe)
    k0, a = s.kalender(), s.takt()
    l.warte_takte(JAHR)
    stand = l.rek.beenden()
    l.ergebnis["jahr40"] = stand
    return {"von": a, "bis": s.takt(), "kalender": [k0, s.kalender()], "stand": stand}


def abschnitt_treppe(l):
    from selfaware.tools.analysis.auge_auswertung import a4_tempotreppe

    zeilen = []
    for stufe in STUFEN:
        soll = TREPPE_TAKTE.get(stufe, 1000)
        tempo_setzen(l.k, stufe)
        l.tempo = stufe
        o1 = l.messe(soll)
        # bis 100 ist die Bildrate keine Grenze: Stimmt das Tempo nicht, misst die Stufe etwas anderes (Lauf F 18:16: ueberall 200)
        if stufe <= 100 and abs(o1["rate"] - stufe) > max(2.0, 0.2 * stufe):
            raise Abbruch(f"Tempo {stufe} wirkt nicht: {o1['rate']:.1f} Takte je Sekunde")
        r = l.rek.lese_runde(soll, stufe, l.wach)
        o2 = l.messe(soll)
        z = {"tempo": stufe, "soll": soll, "gezaehlt": min(o1["takte"], r["takte"], o2["takte"]), "sekunden": min(o1["sekunden"], r["sekunden"], o2["sekunden"]),
             "ohne_1": o1["rate"], "mit": r["takte_je_s"], "ohne_2": o2["rate"], "gelesen": r["gelesen"], "gesamt": r["takte"]}
        zeilen.append(z)
        l.schreib({"tempostufe": stufe, "ohne_1": round(o1["rate"], 1), "mit": round(r["takte_je_s"], 1), "ohne_2": round(o2["rate"], 1), "gelesen": r["gelesen"], "takte": r["takte"]})
    e = a4_tempotreppe(zeilen)
    l.ergebnis["treppe"] = e
    return {"ergebnis": e.status, "text": e.text, "zeilen": e.daten.get("zeilen")}


ABSCHNITTE = (("grundstock", abschnitt_grundstock), ("bauen", abschnitt_bauen), ("bauern", abschnitt_bauern), ("schalten", abschnitt_schalten),
              ("ketten", abschnitt_ketten), ("jahr_tempo40", abschnitt_jahr40), ("treppe", abschnitt_treppe))


def programm(l, abschnitte=ABSCHNITTE):
    """Die Abschnitte der Reihe nach. Jeder prueft seine Wirkung; Abbruch beendet den ganzen Lauf."""
    aus = []
    for name, f in abschnitte:
        t0, s0 = l.s.takt(), l.uhr()
        l.schreib({"abschnitt": name, "beginn": t0})
        try:
            daten = f(l)
        except OSError as e:  # jedes Lesen kann der Fehler sein, der das Ende des Spiels zeigt
            raise Abbruch(f"Spiel laeuft nicht mehr: {e}") from e
        t1, d = l.s.takt(), l.uhr() - s0
        eintrag = {"abschnitt": name, "takt_von": t0, "takt_bis": t1, "sekunden": round(d, 1), "takte_je_s": round((t1 - t0) / d, 1) if d > 0 else None, "daten": daten}
        l.schreib(eintrag)
        aus.append(eintrag)
    return aus


def schluss(l, kalender_start):
    """Ist der Lauf gueltig? Das sagt, ob er die Frage beantworten konnte. Widerlegte Punkte sind Funde, kein Scheitern."""
    from selfaware.tools.analysis.auge_auswertung import BESTAETIGT

    s = l.s
    stehen = {e["typ"] for e in s.gebaeude()}
    fehlen = [t for t in l.arten if t not in stehen and t != PECHGRUBE and not (t == PECHGRABEN and s.pechgraeben())]
    stand = l.ergebnis.get("jahr40") or {}
    treppe = l.ergebnis.get("treppe")
    pruefung = {"arten_fehlen": fehlen, "offene_arbeitsplaetze": offene_plaetze(l), "jahreswechsel": s.kalender()[0] - kalender_start[0],
                "tempo40_fehlend": stand.get("fehlend"), "tempo40_gemischt": stand.get("gemischt"), "treppe": treppe.status if treppe else None, "funde": l.funde}
    pruefung["gueltig"] = (not fehlen and pruefung["offene_arbeitsplaetze"] == 0 and pruefung["jahreswechsel"] >= 1 and stand.get("fehlend") == 0 and stand.get("gemischt") == 0
                           and treppe is not None and treppe.status == BESTAETIGT)
    return pruefung


def tempo_setzen(k, s):
    """Zwei Befehle: Pause und Tempo im selben Befehl setzt das Tempo nicht (gemessen Lauf F 02.11.2026 18:16)."""
    k.befehl({"pause": False}, 0.3)
    k.befehl({"tempo": s}, 0.5)


def pruefen(n, quell=QUELL_INSTANZ, laeuft_schon=False):
    """Trockenprobe: liest nur. Jede Zeile (Name, ok, Aussage)."""
    from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz, prozesspfade
    aus = []

    def pruef(name, ok, text=""):
        aus.append((name, bool(ok), text))

    pruef("Laufinstanz ist nicht Instanz 5", n != DANIELS_INSTANZ, f"Instanz {n}")
    o = ordner(n)
    pruef("Ordner und Programm da", os.path.exists(os.path.join(o, "Stronghold Crusader.exe")), o)
    pruef("Karte da", os.path.exists(os.path.join(o, "maps", KARTE + ".map")), KARTE + ".map")
    pruef("Modul da", os.path.exists(os.path.join(o, "ucp", "modules", "villagestudio-0.1.0", "init.lua")))
    log = os.path.join(o, "ucp3.log")
    # keine Bedingung: Der Lauf traegt das Modul selbst ein; ob es laeuft, zeigt erst seine Antwort im Spiel
    aktiv = os.path.exists(log) and "villagestudio aktiv" in open(log, encoding="utf-8", errors="replace").read()
    pruef("Stand des letzten Starts bekannt", True, ("Modul war aktiv" if aktiv else "Modul war nicht aktiv") + (time.strftime(", %d.%m. %H:%M", time.localtime(os.path.getmtime(log))) if os.path.exists(log) else ""))
    if laeuft_schon:
        pruef("Instanz laeuft schon, wie angegeben", pid_der_instanz(n) is not None)
    else:
        pruef("Instanz laeuft gerade nicht", pid_der_instanz(n) is None)
    pfade = prozesspfade()
    pruef("UCP3-GUI ist zu", not any("ucp3-gui" in p.lower() or "ucp3 gui" in p.lower() for p in pfade))
    q = os.path.join(ordner(quell), "ucp", "villagestudio", "logik.lua")
    try:
        t = logik_text(q)
        pruef("logik.lua laesst sich ergaenzen", t.count(NEU) == 1 and t.count(ANKER) == 1 and BAU_NEU[3] in t, f"Quelle Instanz {quell}, {len(t)} Zeichen")
        f = lua_fehler(t)
        pruef("logik.lua hat keinen Syntaxfehler", not f or f.startswith("nicht geprueft"), f or "")
    except (OSError, Fehler) as e:
        pruef("logik.lua laesst sich ergaenzen", False, str(e))
    s = subprocess.run([sys.executable, sperre_pfad(), "nachsehen"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=dict(os.environ, SHC_INSTANZ=str(n)), timeout=30)
    pruef("Sperre frei", "FREI" in s.stdout, s.stdout.strip().splitlines()[-1] if s.stdout.strip() else s.stderr[:100])
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
    from selfaware.tools.experiments.auge_aufzeichnung import standard_bereiche
    karte = Feldkarte.laden(feldliste=FELDLISTE)
    bereiche = standard_bereiche(karte)
    pruef("Bereiche aus dem Export", len(bereiche) >= 10, f"{len(bereiche)} Bereiche, jeden Takt {sum(b.laenge for b in bereiche if b.alle == 1) / 1e6:.1f} MB")
    falsch = adressen_gegen_karte(karte)
    pruef("Feste Adressen passen zum Export", not falsch, str(falsch) if falsch else "Spieler, Gebaeude, Kalender")
    frei = shutil.disk_usage(os.path.dirname(os.path.abspath(__file__))).free
    pruef("Plattenplatz reicht", frei > PLATTE_MINDESTENS, f"{frei / 1e9:.0f} GB frei")
    return aus


def adressen_gegen_karte(karte):
    """Die festen Adressen des Programms gegen die Feldnamen des Exports. Rueckgabe: was nicht passt."""
    falsch = []
    basis = SPIELER + SPIELER_SCHRITT
    soll = {**{f"playerDataArray[].{n}": o for n, o in FELD.items()}, "playerDataArray[].startResources[]": FELD_START, "playerDataArray[].currentResources[]": FELD_BESTAND}
    for f, o in soll.items():
        ist = karte.ziel(basis + o)[1]
        if ist != f:
            falsch.append((f, ist))
    gsoll = {"buildingType": G_TYP, "owner": G_BESITZER, "uid": G_UID, "x": G_X, "y": G_Y, "buildingVariation": G_BILDWERT, "currentlyNeededEmployeeCount": G_OFFEN, "gateState": G_TOR}
    for f, o in gsoll.items():
        ist = karte.ziel(GEBAEUDE + G_SCHRITT + o)[1]
        if ist != f"buildings[].{f}":
            falsch.append((f, ist))
    for f, a in (("mapAndTime.year", JAHR_ADR), ("mapAndTime.month", MONAT_ADR), ("mapAndTime.week", WOCHE_ADR), ("mapAndTime.singlePlayerHasKeepAndGranary", HAT_BURG_KORN)):
        if karte.ziel(a)[1] != f:
            falsch.append((f, karte.ziel(a)[1]))
    if karte.adresse("DAT_TileMapState", "pitchDitches")[0] != PECHGRAEBEN:
        falsch.append(("pitchDitches", hex(karte.adresse("DAT_TileMapState", "pitchDitches")[0])))
    return falsch


def sperre_pfad():
    from selfaware import workspace
    return os.path.join(workspace.VILLAGE_STUDIO, "werkzeug", "sperre.py")


def sperre_holen(was):
    r = subprocess.run([sys.executable, sperre_pfad(), "holen", SPERRE_NAME, was], capture_output=True, text=True, env=dict(os.environ), timeout=30)
    if r.returncode != 0:
        raise Fehler(f"Sperre nicht bekommen: {r.stdout} {r.stderr}")


def sperre_freigeben():
    subprocess.run([sys.executable, sperre_pfad(), "freigeben", SPERRE_NAME], capture_output=True, env=dict(os.environ), timeout=30)


class EchterKanal:
    def __init__(self):
        from selfaware.game.ucp import laden
        from selfaware.game.ucp.befehl import ABZUG, neue_id, sende
        self._laden, self._neue_id, self._sende, self._abzug = laden, neue_id, sende, ABZUG

    def befehl(self, cmd, warte=0.8, bis=None):
        return self._laden.befehl(cmd, warte, bis=bis)

    def peek(self, adr, n=1):
        # verpackt: unverpackte Lesebefehle kommen in Menues nicht an (gemessen 21.10.)
        kennung = "PEEK 0x%08X" % adr
        for z in self._sende({"befehle": [{"player": 1, "id": self._neue_id(), "peek": adr, "worte": n}]}, 3.0, bis=kennung):
            if kennung in z:
                return [int(x, 16) & 0xFFFFFFFF for x in z.split(": ", 2)[-1].split()]
        raise Fehler(f"keine Antwort auf {kennung}")

    def liste(self, cmds, warte=1.0):
        return self._sende({"befehle": [dict(c, player=1, id=self._neue_id()) for c in cmds]}, warte)

    def platzkarte(self, mapper, groesse, x0, y0, x1, y1, sp=1):
        """Spielpruefung je Stelle des Fensters: "+" erlaubt. Der Haken wartet auf die Fertig-Zeile im Log, nicht auf eine feste Zeit."""
        z = self.befehl({"platzkarte": {"spieler": sp, "mapper": mapper, "groesse": groesse, "x0": x0, "y0": y0, "x1": x1, "y1": y1}}, 3.0, bis="PLATZKARTE Mapper")
        if not any("PLATZKARTE Mapper" in x for x in z):
            raise Abbruch(f"Spielpruefung antwortet nicht (Mapper {mapper})")
        with open(os.path.join(self._abzug, "platzkarte.txt"), encoding="latin-1") as f:
            return f.read().splitlines()[1:]


class Rekorder:
    """Die Aufzeichnung laeuft als eigener Prozess: Das Lesen soll nicht auf das Programm des Laufs warten."""

    def __init__(self, n, ordner_aus, stempel, quelle, bereiche):
        self.n, self.ordner, self.stempel, self.quelle, self.bereiche = n, ordner_aus, stempel, quelle, bereiche
        self.basis = os.path.join(ordner_aus, f"lauf_f_{stempel}")
        self.stop_datei, self.aus_datei, self.felder_datei = self.basis + ".stop", self.basis + ".aussetzen", self.basis + ".felder.json"
        self.p, self.pfad = None, None

    def starten(self, name, tempo, streng=False, felder=False):
        self.pfad = f"{self.basis}_{name}.auge" if name else self.basis + ".auge"
        for d in (self.stop_datei, self.aus_datei):
            if os.path.exists(d):
                os.remove(d)
        cmd = [sys.executable, "-m", "selfaware.tools.experiments.auge_aufzeichnung", "--instanz", str(self.n), "--ausgabe", self.pfad, "--lauf", "F", "--stop-datei", self.stop_datei,
               "--aussetzen-datei", self.aus_datei, "--tempo-wert", str(tempo), "--tempo-takte", str(tempo)]
        if streng:
            cmd.append("--streng")
        if felder:
            cmd += ["--felder-datei", self.felder_datei]
        self.p = subprocess.Popen(cmd, env=dict(os.environ))

    def laeuft(self):
        return self.pfad is not None and os.path.exists(self.pfad) and os.path.getsize(self.pfad) > 1000

    def stand(self):
        try:
            with open(self.pfad + ".stand", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

    def fehler(self):
        """None, solange die Aufzeichnung laeuft oder gerade keine laufen soll."""
        if self.p is None or self.p.poll() is None:
            return None
        return f"beendet mit {self.p.returncode}: {self.stand().get('grund')}"

    def aussetzen(self, an):
        if an:
            open(self.aus_datei, "w").close()
        elif os.path.exists(self.aus_datei):
            os.remove(self.aus_datei)

    def felder(self):
        try:
            with open(self.felder_datei, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None

    def beenden(self):
        """Endet erst, wenn der Prozess wirklich weg ist."""
        if self.p is None:
            return {}
        p, self.p = self.p, None
        if p.poll() is None:
            open(self.stop_datei, "w").close()
            try:
                p.wait(120)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait(30)
        return self.stand()

    def lese_runde(self, takte, stufe, wach):
        """Liest wie die Aufzeichnung, in eine eigene Datei, in diesem Prozess. Die Haupt-Aufzeichnung ist dann aus."""
        from selfaware.tools.experiments.auge_aufzeichnung import Aufzeichner

        sys.setswitchinterval(0.0005)
        auf = Aufzeichner(self.quelle, self.bereiche, f"{self.basis}_treppe_tempo{stufe}.auge", {"lauf": "Treppe", "tempo": stufe})
        a, t0 = auf.takt(), time.perf_counter()

        def stop():
            wach()
            return False
        n = auf.lauf(bis_takt=a + takte, pause=0.0002, stop=stop)
        e, t1 = auf.takt(), time.perf_counter()
        auf.schliessen()
        return {"takte_je_s": (e - a) / (t1 - t0), "gelesen": n, "takte": e - a, "sekunden": t1 - t0}


def stop_datei(ziel=None):
    from selfaware import workspace
    return os.path.join(ziel or os.path.join(workspace.DATA, "auge_plan", "laeufe"), "STOP_LAUF_F")


def anhalten_und_pruefen(k, s, ruhe=time.sleep):
    """Spiel anhalten und nachlesen, dass der Takt wirklich steht. Rueckgabe: steht ja/nein, Takt."""
    for _ in range(3):
        k.befehl({"pause": True}, 0.5)
        a = s.takt()
        ruhe(0.5)
        b = s.takt()
        if a == b:
            return True, b
    return False, b


def los(n, ziel=None, laeuft_schon=False, frist=FRIST):
    pruefe_laufinstanz(n)
    os.environ["SHC_INSTANZ"] = str(n)
    from selfaware import workspace
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

    ziel = ziel or os.path.join(workspace.DATA, "auge_plan", "laeufe")
    os.makedirs(ziel, exist_ok=True)
    stempel = time.strftime("%Y%m%d_%H%M%S")
    prot = os.path.join(ziel, f"lauf_f_{stempel}.protokoll.jsonl")
    stop = stop_datei(ziel)
    if os.path.exists(stop):
        os.remove(stop)
    fehlt = [z for z in pruefen(n, laeuft_schon=laeuft_schon) if not z[1]]
    if fehlt:
        raise Fehler(f"Trockenprobe rot: {fehlt}")
    sperre_holen("Lauf F Auge (B-142)")

    def schreib(e):
        with open(prot, "a", encoding="utf-8") as f:
            f.write(json.dumps(e, ensure_ascii=False, default=str) + "\n")
        print(json.dumps(e, ensure_ascii=False, default=str)[:400], flush=True)

    rek = k = s = None
    ergebnis = None
    try:
        q = os.path.join(ordner(QUELL_INSTANZ), "ucp", "villagestudio", "logik.lua")
        log = os.path.join(ordner(n), "ucp3.log")
        log_vorher = os.path.getsize(log) if os.path.exists(log) else 0
        sicherung = logik_einspielen(os.path.join(ordner(n), "ucp", "villagestudio", "logik.lua"), q, stempel)
        schreib({"schritt": "logik", "sicherung": sicherung})
        schreib({"schritt": "ladeliste", "sicherung": modul_eintragen(os.path.join(ordner(n), "ucp-config.yml"), stempel)})
        if not laeuft_schon:
            ps = os.path.join(workspace.ROOT, "tools", "windows", "spiel_starten.ps1")
            a = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps, "-Instanz", str(n)], capture_output=True, text=True, timeout=120)
            schreib({"schritt": "start", "ausgabe": a.stdout.strip()[-200:]})
            if a.returncode != 0:
                raise Fehler(f"Spielstart: {a.stdout} {a.stderr}")
        from selfaware.game.ucp import bauen
        from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz, standard_bereiche

        k = EchterKanal()
        warte_auf_modul(k)
        if laeuft_schon and sicherung:
            def nachgeladen():
                with open(log, encoding="utf-8", errors="replace") as f:
                    f.seek(log_vorher)
                    return "logik.lua neu geladen" in f.read()
            warte_auf(nachgeladen, 20, "Modul hat die logik.lua nachgeladen")
        for rest in ALTE_SCHALTER:
            k.befehl(rest, KANAL)
        karte = Feldkarte.laden(feldliste=FELDLISTE)
        quelle = ProzessQuelle(pid_der_instanz(n))
        s = Speicher(quelle)
        rek = Rekorder(n, ziel, stempel, quelle, standard_bereiche(karte))
        schreib({"schritt": "burgenbau", **burgenbau_starten(k)})
        tempo_setzen(k, TEMPO_LAUF)
        rek.starten(None, TEMPO_LAUF, felder=True)
        warte_auf(rek.laeuft, 60, "Aufzeichnung laeuft")
        kalender_start = s.kalender()
        l = Lauf(k, s, bauen.NACH_TYP, rek, schreib, frist=frist, stop=lambda: os.path.exists(stop))
        schreib({"schritt": "spielart", "takt": s.takt(), "kalender": kalender_start, "startwaren": s.startwaren()})
        programm(l)
        ergebnis = schluss(l, kalender_start)
        schreib({"schritt": "schluss", **ergebnis})
    except Abbruch as e:
        schreib({"schritt": "abbruch", "grund": str(e)})
        ergebnis = {"gueltig": False, "abbruch": str(e)}
    finally:
        # Erst das Spiel anhalten: Das Beenden der Aufzeichnung kann dauern oder scheitern, das Spiel darf dabei nicht weiterlaufen
        steht = False
        if k is not None and s is not None:
            try:
                steht, t = anhalten_und_pruefen(k, s)
                schreib({"schritt": "angehalten", "steht": steht, "takt": t})
            except (OSError, RuntimeError) as e:
                schreib({"schritt": "anhalten_fehlgeschlagen", "grund": str(e)})
        else:
            steht = True  # es lief noch kein Spiel an, das anzuhalten waere
        if rek is not None:
            schreib({"schritt": "aufzeichnung_beendet", "stand": rek.beenden()})
        if steht:
            sperre_freigeben()
        else:
            schreib({"schritt": "sperre_bleibt", "grund": "Der Takt steht nicht, die Sperre bleibt, bis das geklaert ist"})
    from selfaware.tools.analysis import auge_ergebnis

    schreib({"schritt": "auswertung", "bericht": auge_ergebnis.auswerten(os.path.join(ziel, f"lauf_f_{stempel}"), ergebnis)})
    return ergebnis


def stoppen(n, ziel=None):
    """Bittet den laufenden Lauf um Abbruch und wartet, bis er wirklich fertig ist: Sperre frei und Takt steht."""
    os.environ["SHC_INSTANZ"] = str(n)
    from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

    open(stop_datei(ziel), "w").close()
    frei = lambda: "FREI" in subprocess.run([sys.executable, sperre_pfad(), "nachsehen"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=dict(os.environ), timeout=30).stdout  # noqa: E731
    warte_auf(frei, 180, "der Lauf hat die Sperre freigegeben", schlaf=1.0)
    s = Speicher(ProzessQuelle(pid_der_instanz(n)))
    a = s.takt()
    time.sleep(1.0)
    return {"takt": [a, s.takt()], "steht": a == s.takt(), "pause": s.pause()}


def trocken(n, mit_probe=0):
    """Trockenlauf am aktuellen Spielstand: Bauplan fuer alle Arten, Felder lesen, nichts bauen. Das Spiel muss angehalten sein.
    mit_probe: so viele Takte strenge Aufzeichnung auf Tempo 40, danach wieder angehalten."""
    os.environ["SHC_INSTANZ"] = str(n)
    pruefe_laufinstanz(n)
    from selfaware import workspace
    from selfaware.game.ucp import bauen
    from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

    sperre_holen("Trockenlauf Auge (B-142)")
    steht = True
    try:
        k, s = EchterKanal(), Speicher(ProzessQuelle(pid_der_instanz(n)))
        aus = {"takt": s.takt(), "pause": s.pause(), "kalender": s.kalender(), "anzeige": s.anzeige_burg_korn(), "beliebtheit": s.spieler("popularity"), "leute": s.spieler("currentPopulation"),
               "deckel": s.spieler("populationCap"), "feuer": s.spieler("availablePeasantsAtFire"), "essen": s.spieler("totalFood"), "steuer": s.spieler("taxesSetting"), "ration": s.spieler("rationsSetting"),
               "waren": s.waren(), "startwaren": s.startwaren(), "pechgraeben": s.pechgraeben(), "einheiten": sum(s.einheiten().values())}
        if s.pause() != 1:
            raise Fehler("Das Spiel laeuft. Trockenlauf nur im angehaltenen Spiel")
        for rest in ALTE_SCHALTER:
            k.befehl(rest, KANAL)
        g = s.gebaeude()
        aus.update(gebaeude=len(g), offene_plaetze=sum(e["offen"] for e in g), arbeitsplaetze=sum(s.arbeiter_je_typ(e["typ"]) for e in g))
        l = Lauf(k, s, bauen.NACH_TYP, _KeinRekorder(), lambda e: None, frist=600)
        burg = [e for e in g if e["typ"] == BURG]
        l.mitte = (burg[0]["x"], burg[0]["y"]) if burg else ANKER_BURG
        l.anker = iter(spirale(l.mitte, 10, 200))
        plan, ohne = {}, []
        t0 = time.perf_counter()
        for typ in sorted(bauen.NACH_TYP):
            st = l.stelle_fuer(typ)
            (plan.__setitem__(typ, st) if st else ohne.append(typ))
        aus.update(bauplan=len(plan), bauplan_sekunden=round(time.perf_counter() - t0, 1), ohne_stelle=ohne, beispiele={t: plan[t] for t in list(plan)[:6]})
        aus["mauer_streifen"] = freier_streifen(k.platzkarte(bauen.NACH_TYP[FALLGRUBE]["mapper"], 1, l.mitte[0], l.mitte[1], l.mitte[0] + 80, l.mitte[1] + 80), l.mitte[0], l.mitte[1], 13, 9)
        if mit_probe:
            from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
            from selfaware.tools.experiments.auge_aufzeichnung import standard_bereiche

            stempel = "trocken_" + time.strftime("%Y%m%d_%H%M%S")
            rek = Rekorder(n, os.path.join(workspace.DATA, "auge_plan", "laeufe"), stempel, ProzessQuelle(pid_der_instanz(n)), standard_bereiche(Feldkarte.laden(feldliste=FELDLISTE)))
            steht = False
            a, grund = s.takt(), "nicht gestartet"
            try:
                tempo_setzen(k, TEMPO_JEDER_TAKT)
                rek.starten(None, TEMPO_JEDER_TAKT, streng=True)
                warte_auf(rek.laeuft, 60, "Aufzeichnung laeuft")
                a = s.takt()
                ende = time.perf_counter() + 2 * mit_probe / TEMPO_JEDER_TAKT + 30  # Schutz gegen Haengen: doppelte Soll-Dauer
                while s.takt() < a + mit_probe and not rek.fehler() and time.perf_counter() < ende:
                    time.sleep(0.05)
                grund = rek.fehler() or (None if s.takt() >= a + mit_probe else "Frist um")
            finally:
                steht, t = anhalten_und_pruefen(k, s)
                stand = rek.beenden()
            aus["probe"] = {"takte": mit_probe, "von": a, "bis": t, "stand": stand, "fehler": grund, "steht": steht, "datei": rek.pfad}
        return aus
    finally:
        if steht:
            sperre_freigeben()


class _KeinRekorder:
    def fehler(self):
        return None


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("was", choices=["pruefen", "trocken", "los", "stop"])
    p.add_argument("--instanz", type=int, required=True)
    p.add_argument("--frist", type=int, default=FRIST, help="Sekunden fuer das Programm, Schutz gegen Haengen")
    p.add_argument("--daniel-ja", action="store_true", help="Lauf nur nach Daniels Ja")
    p.add_argument("--laeuft-schon", action="store_true", help="Die Instanz laeuft schon, nicht neu starten")
    p.add_argument("--probe", type=int, default=0, help="trocken: so viele Takte strenge Aufzeichnung auf Tempo 40")
    a = p.parse_args(argv)
    pruefe_laufinstanz(a.instanz)
    if a.was == "pruefen":
        aus = pruefen(a.instanz, laeuft_schon=a.laeuft_schon)
        for name, ok, text in aus:
            print(("OK:     " if ok else "FEHLER: ") + name + (f" - {text}" if text else ""))
        return 0 if all(z[1] for z in aus) else 1
    if a.was == "trocken":
        print(json.dumps(trocken(a.instanz, a.probe), ensure_ascii=False, indent=0, default=str))
        return 0
    if a.was == "stop":
        print(stoppen(a.instanz))
        return 0
    if not a.daniel_ja:
        raise Fehler("Lauf F startet nur mit --daniel-ja")
    e = los(a.instanz, laeuft_schon=a.laeuft_schon, frist=a.frist)
    print("Lauf gueltig:", e.get("gueltig"))
    return 0 if e.get("gueltig") else 2


if __name__ == "__main__":
    sys.exit(main())
