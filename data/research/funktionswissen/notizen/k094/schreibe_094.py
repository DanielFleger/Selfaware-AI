# -*- coding: utf-8 -*-
# Hilfsskript fuer Paket korr_094 (UpdateArmorer): schreibt die eine JSON-Zeile in korrektur/ergebnisse/korr_094.teil1.jsonl
import json, os, sys

BASIS = r"C:\Users\danie\Documents\PC_Affe\Games\Stronghold_Crusader\Stronghold Crusader Modding\Tools\Selfaware-AI-fw\data\research\funktionswissen\korrektur\ergebnisse"
ZIEL = os.path.join(BASIS, "korr_094.teil1.jsonl")

d = {
    "adr": "0x00558cb0",
    "name": "UpdateArmorer",
    "quelle": "ghidra",
    "p1": {
        "bereich": "Spielablauf",
        "zweck": "Taktschritt (Zustandsautomat) des Rüstungsschmied-Arbeiters: ein Eisen aus einem Lager holen, in die Werkstatt tragen, dort verarbeiten und die fertige Rüstung (RT_IRONARMOR) Stück für Stück in eine Waffenkammer legen; dazu Warten, Pause, Verschwinden und Tod."
    },
    "p2": {
        "ein": "- (kein Parameter; der Arbeiter ist DAT_CurrentUnitSlotID, das nur gelesen und nie geschrieben wird; verzweigt nach units[].state.generic)",
        "aus": "-",
        "liest": [
            "units[].state.generic/owner/workplaceBuildingID_1/targetID_OR_targetBuildingID/targetUID/targetX_2/targetY_2/x/y/resourceToDeposit/destinationNeeded/isDisappearingUnk/goToRallyPoint/animationCycleNumber/updateTickTracker/disappearFadeAlphaCountdown/cachedState/substate",
            "units[].engineerManningSiegeStateRef_checkType (hier als Schrittweite des Ein-/Ausblendens benutzt)",
            "buildings[].uid/buildingEntryX/buildingEntryY (Lager, Werkstatt, Waffenkammer)",
            "Eisenbestand von Lager und Werkstatt (getBuildingResourceAmountByUid mit RT_IRON)",
            "Platz in Waffenkammern (getArmoryWithSpaceLeft)",
            "DAT_GameSynchronyState.currentGameMode und currentPlayerSlotID",
            "DAT_UnitHasBecomeIdle",
            "Animationstabellen Frames_Shared_UnitClimbingUp.field276_0x55c4, field277_0x5674 (Zustand 9) und field6_0x6d4 (Tod); der Strukturname täuscht, es sind Warte- und Todesanimationen"
        ],
        "schreibt": [
            "units[].movementSpeed (=2, nur wenn currentGameMode != GM_SOLITARY) und unitTypeSpecificRestingState (=9, bei jedem Aufruf)",
            "units[].state.generic/cachedState/goToRallyPoint/destinationNeeded/isDisappearingUnk/disappearFadeAlphaCountdown/engineerManningSiegeStateRef_checkType/updateTickTracker/animationCycleNumber/resourceToDeposit/targetID_OR_targetBuildingID/targetUID/substate/logicalState (ULS_REMOVE = 3)",
            "units[] Darstellung: animationSheetFrameOffset, animationSpeed, animationFrame, gfxNumber, facingDirection, stateBasedSpeed, field_0x30_animRelated, field131_0x2ac (+0x2ac) und field39_0x58 (+0x58) (die beiden letzten ungesichert)",
            "DAT_UnitHasBecomeIdle",
            "Bestände über addResourceToStockpile: Lager-Eisen -1; Werkstatt-Eisen +1 und -1; Werkstatt-RT_IRONARMOR +1 und -1; Waffenkammer-RT_IRONARMOR +1",
            "DAT_GameSynchronyState.finalResults.finalWeaponsProduced[owner]",
            "buildings[Werkstatt].idleTimerUnk (=4000, nur im Zustand US_DISAPPEAR) und die Werkstatt-Animation über updateBuildingSignpostCounter",
            "indirekt: productivityDiv100/productivityMod100 (ComputeGoodsProduced), Arbeitszeitzähler und av (IncrementAndOptionalUpdateAVValueRelated), Weg- und Positionsdaten (commitUnitLocation, resetUnitMovementState, makeUnitStopWalkingByClearingPathProgressState)"
        ],
        "ruft": [
            "IncrementAndOptionalUpdateAVValueRelated",
            "getStorageBuildingForResourceTypeAndAmount",
            "buildingIsAccessible",
            "setDestinationForUnit",
            "hasUnitReachedDestination",
            "getBuildingResourceAmountByUid",
            "setWorkplaceBuildingEntryAsTarget",
            "addResourceToStockpile",
            "updateBuildingSignpostCounter",
            "ComputeGoodsProduced",
            "resetUnitMovementState",
            "commitUnitLocation",
            "getArmoryWithSpaceLeft",
            "PlayArmoryIsFullWarning",
            "playSFXAtLocation",
            "ConsiderHavingABreakNowUnk",
            "UpdateWorker_ConsiderTakingABreakUnk",
            "SetStateToFreetimeWalking",
            "SetRestingForUnit",
            "checkIfCitizenUnitIsAliveBasedOnState",
            "makeUnitStopWalkingByClearingPathProgressState"
        ],
        "regeln": [
            "Jeder Aufruf: movementSpeed = 2, aber nur wenn currentGameMode != GM_SOLITARY (0), also in allen anderen Modi (GM_MULTIPLAYER 1, Skirmish 99 usw.); unitTypeSpecificRestingState = 9. Dann Verzweigung nach units[].state.generic in der Reihenfolge 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0x79, 0x6c, 0x6d, 0x6f, sonst. Die Namen US_RELOAD_WEAPONUnk (4), US_AIM_WEAPONUnk (5), US_FIRE_WEAPONUnk (6), US_LOOK_AROUNDUnk (7), US_STAND_UPUnk (8) und US_JESTER_ROAM_TO (0x6d) sind hier nur Zahlen der Schmied-Schleife: 1 Warten, 2 zum Lager gehen, 3 Eisen zur Werkstatt tragen, 0x6d Ein-/Ausblenden, 6 und 5 Arbeit in der Werkstatt, 7 Waffenkammer suchen, 8 hingehen und abliefern, 4 zurück zur Werkstatt, 9 Warte-/Pausenanimation.",
            "Zustand 0: Ist isDisappearingUnk == 0, passiert nur bei goToRallyPoint != 0 etwas (goToRallyPoint = 0, destinationNeeded = 2, state = 4); bei goToRallyPoint == 0 nichts. Ist isDisappearingUnk != 0, sinkt disappearFadeAlphaCountdown je Aufruf um 1; wird er als Byte negativ, werden Countdown und isDisappearingUnk auf 0 gesetzt (state bleibt 0).",
            "Zustand 1 (Warten): bei jedem Aufruf field_0x30_animRelated = 0, field131_0x2ac = 1, resourceToDeposit = 0 und animationCycleNumber +1; erst ab animationCycleNumber >= 0x14 (20) geht es weiter (Zähler dann 0). Dann getStorageBuildingForResourceTypeAndAmount(RT_IRON = 6, 1, owner): ein Lager des Besitzers mit mindestens 1 Eisen (die Suche läuft laut Export von der höchsten Gebäudenummer abwärts und nimmt den ersten Treffer; 0 = keins). Ist es nicht erreichbar (buildingIsAccessible = 0) oder scheitert setDestinationForUnit zu seinem Eingang: state = 9. Sonst state = 2; targetID_OR_targetBuildingID und targetUID sind dann schon vor dem Wegversuch geschrieben.",
            "Zustand 2 (zum Lager), jeder Aufruf: animationSheetFrameOffset = 1, field_0x30_animRelated = 0x10, Arbeitszeitzähler +1; weiter erst bei hasUnitReachedDestination, dann animationCycleNumber = 0. Hat das Zielgebäude (gleiche uid) mehr als 0 Eisen: resourceToDeposit = 1 (wird vor der nächsten Prüfung geschrieben) und setWorkplaceBuildingEntryAsTarget(…, 1); scheitert das, logicalState = ULS_REMOVE (3). Sonst state = 3 und setDestinationForUnit(targetX_2, targetY_2) (Werkstatt-Eingang): gelingt es, wird erst jetzt 1 Eisen im Lager abgebucht (addResourceToStockpile(…, RT_IRON, -1, 0x30, 1)); scheitert es, state = US_DISAPPEAR (0x6e), updateTickTracker = 0 und es wird kein Eisen abgebucht.",
            "Zustand 2, Lager hat bei Ankunft kein Eisen (oder die uid passt nicht mehr): neues Lager suchen wie in Zustand 1. Erreichbar: Ziel neu setzen (Ergebnis von setDestinationForUnit wird nicht geprüft), state = 2. Nicht erreichbar: setWorkplaceBuildingEntryAsTarget(…, 1); gelingt es, state = 4 und destinationNeeded = DNE_DESTINATION_NEEDED (1), sonst ULS_REMOVE. Dasselbe Ende (Lager suchen, sonst zurück zur Werkstatt, sonst ULS_REMOVE) benutzt auch Zustand 8 nach der Ablieferung, dort aber ohne das Warten aus Zustand 1.",
            "Zustand 3 (Eisen tragen): animationSheetFrameOffset = 0x101, field_0x30_animRelated = 0x10, Arbeitszeitzähler +1; bei Ankunft in der Werkstatt: animationCycleNumber = 0, state = 0x6d, disappearFadeAlphaCountdown = 0, Schrittweite (engineerManningSiegeStateRef_checkType) = 2, cachedState = 6, Werkstatt-Eisen +1 (addResourceToStockpile(Werkstatt, RT_IRON, 1, 0x30, 1)), resourceToDeposit = 0, updateTickTracker = 0.",
            "Zustand 0x6d (Ein-/Ausblenden): disappearFadeAlphaCountdown += Schrittweite (unter 0 wird 0, ab 0x20 wird 0x1f), updateTickTracker +1; solange der Tracker <= 16 (0x10) ist, passiert sonst nichts. Beim 17. Aufruf: Tracker = 0, Countdown = 0, state = cachedState; commitUnitLocation nur bei Schrittweite > 0 (Betreten der Werkstatt, +2), nicht beim Verlassen (0xfe = -2); danach immer updateBuildingSignpostCounter(Werkstatt, 2).",
            "Zustand 6 (Werkstattarbeit): Arbeitszeitzähler +1, field131_0x2ac = 1, updateTickTracker +1. Unter 30 (0x1e): nur updateBuildingSignpostCounter(Werkstatt, 3). Ab 30 entscheidet das Werkstatt-Eisen (entweder-oder): bei >= 1 wird 1 Werkstatt-Eisen abgebucht (0x30, 1), updateBuildingSignpostCounter(…, 2), Tracker = 0, state = 5; bei 0 wird Werkstatt-RT_IRONARMOR -1 gebucht, updateBuildingSignpostCounter(…, 0), animationCycleNumber = 0, state = 0x6d mit Countdown 0x20, Schrittweite 0xfe (-2), cachedState = 7, Tracker = 0, resourceToDeposit = ComputeGoodsProduced(Arbeiter, 1, TRUE), field39_0x58 = 1, resetUnitMovementState, animationSheetFrameOffset = 0x81, field_0x30_animRelated = 0x10.",
            "Zustand 5: Arbeitszeitzähler +1, field131_0x2ac = 1, updateBuildingSignpostCounter(Werkstatt, 1); sie liefert den Zähler field14_0x2c der Werkstatt, und solange er 0 ist, passiert nichts (die 1 ist der Anzeigemodus, nicht der erwartete Zählerwert). Danach Werkstatt-RT_IRONARMOR +1 (0x30, 1) und state = 6 (der Tracker steht seit Zustand 6 auf 0, die zweite Wartezeit von 30 beginnt neu). Menge aus Zustand 6: ComputeGoodsProduced(Arbeiter, 1, TRUE) = 1 + Bonus; Produktivität des Besitzers <= 100 zählt als 100, außer in GM_SOLITARY kommen +50 dazu, der Bruchteil wird in productivityMod100 mitgeführt: bei Produktivität 100 also in GM_SOLITARY immer 1 Stück, sonst abwechselnd 1 und 2 (im Mittel 1,5) je Eisen.",
            "Zustand 7 (nach dem Verlassen der Werkstatt): animationSheetFrameOffset = 0x81, field_0x30_animRelated = 0x10, field131_0x2ac = 1, updateTickTracker +1; erst ab Tracker >= 11 (> 0xa) weiter, Tracker dann 0. getArmoryWithSpaceLeft(0, 0x18 = RT_IRONARMOR, owner, resourceToDeposit): erste erreichbare Waffenkammer des Besitzers mit Platz für alle resourceToDeposit Stück. Ist keine gefunden und owner == currentPlayerSlotID: PlayArmoryIsFullWarning (Warnton). Ist die Kammer nicht erreichbar (auch bei keiner) oder scheitert setDestinationForUnit: nichts, der Arbeiter bleibt in Zustand 7 und versucht es nach 11 Aufrufen erneut (derweil keine Weiterarbeit). Sonst targetID_OR_targetBuildingID und targetUID setzen, state = 8.",
            "Zustand 8 (abliefern): animationSheetFrameOffset = 0x81, field_0x30_animRelated = 0x10, Arbeitszeitzähler +1, updateTickTracker +1; weiter erst ab Tracker >= 5 und bei hasUnitReachedDestination, Tracker dann 0. Hat die Zielkammer Platz für 1 Stück (getArmoryWithSpaceLeft(Ziel, 0x18, owner, 1)): Kammer-RT_IRONARMOR +1 (addResourceToStockpile mit Obergrenze 0x32 = 50 je Ware), finalWeaponsProduced[owner] +1, resourceToDeposit -1, Ton FX_STOCK_WEAPON an der Einheit. Sonst eine andere Kammer mit Platz für alle Reststücke suchen (getArmoryWithSpaceLeft(0, 0x18, owner, resourceToDeposit)): erreichbar, dann Ziel wechseln und state 8 behalten; sonst resourceToDeposit = 0, der Rest der Rüstung verfällt.",
            "Zustand 8, wenn danach resourceToDeposit <= 0: destinationNeeded = 1, Arbeitszeit-Durchschnitt av neu berechnen (IncrementAndOptionalUpdateAVValueRelated mit TRUE), ConsiderHavingABreakNowUnk(…, 4) (kann bei Produktivität < 100 eine Pause einlegen: state 0x79, danach state 4; Rückgabe TRUE beendet den Aufruf). Sonst Lager suchen (RT_IRON, 1, owner) und gleich state = 2 (ohne das Warten aus Zustand 1), Fallbacks wie in Regel 5. Ist resourceToDeposit noch > 0, bleibt state 8 und die nächste Ablieferung folgt nach weiteren 5 Aufrufen.",
            "Zustand 4 (zurück zur Werkstatt): animationSheetFrameOffset = 1, field_0x30_animRelated = 0x10, Arbeitszeitzähler +1. Ist destinationNeeded != 0 (nicht DNE_DESTINATION_HAS_BEEN_SET): erst UpdateWorker_ConsiderTakingABreakUnk (TRUE beendet den Aufruf), dann setDestinationForUnit(targetX_2, targetY_2) (Ergebnis ungeprüft) und destinationNeeded = 0. Bei hasUnitReachedDestination: animationCycleNumber = 0, state = 1.",
            "Zustand 9 (Warte-/Pausenanimation): animationSpeed = 2, field_0x30_animRelated = 0, field39_0x58 = 1, field131_0x2ac = 1; animationFrame aus field276_0x55c4[animationCycleNumber] bei substate == 0, sonst aus field277_0x5674; Frame <= 0 setzt gfxNumber = 0x181 und DAT_UnitHasBecomeIdle = 1, sonst gfxNumber = Frame + 0x180. SetStateToFreetimeWalking liefert 1 (und setzt state 0x79), wenn gerade eine Pause läuft und die Animation zu Ende ist: dann Ende. Sonst bei Animationsende: substate +1 (über 1 wieder 0), animationCycleNumber = 0, state = 1. Zustand 0x79: animationSheetFrameOffset = 1, field_0x30_animRelated = 0x10, SetRestingForUnit (Pause). Zustand 0x6c (ohne Namen): stateBasedSpeed = 0, field_0x30_animRelated = 0, animationSheetFrameOffset = 1.",
            "Tod und Verschwinden: Zustand 0x6f (US_DEATH_01): facingDirection = 0, animationSpeed = 2, field_0x30_animRelated = 0, Frame aus field6_0x6d4[animationCycleNumber]; Frame <= 0: gfxNumber = 0x1a8, DAT_UnitHasBecomeIdle = 1, ULS_REMOVE; sonst gfxNumber = Frame + 0x190 und ULS_REMOVE, sobald DAT_UnitHasBecomeIdle != 0. Alle anderen Zustände: checkIfCitizenUnitIsAliveBasedOnState liefert 1 für 0x6f bis 0x74 (trotz des Namens heißt 1 hier Todeszustand); für 0x70 bis 0x74 läuft dieselbe Logik mit Frame + 0x1a8 und Ende bei gfxNumber 0x1c0. Bei Rückgabe 0: Zustand US_DISAPPEAR (0x6e): Countdown +1 (höchstens 0x20), Tracker +1, ab Tracker > 0x20 ULS_REMOVE, dabei jedes Mal Werkstatt-idleTimerUnk = 4000; jeder andere Zustand: state = 1 und makeUnitStopWalkingByClearingPathProgressState."
        ],
        "offen": [
            "Bedeutung von field_0x30_animRelated, field131_0x2ac und field39_0x58 (alle ungesichert); wer goToRallyPoint setzt und wer animationCycleNumber in den Zuständen 9 und 0x6f weiterzählt, steht nicht in dieser Funktion",
            "Was updateBuildingSignpostCounter genau anzeigt: aus dem Export abgeleitet Modus 1 = Animation läuft, 3 = angehalten, 2 = zurücksetzen, 0 = aus; Name und die Länge der Wartezeit in Zustand 5 sind ungesichert. Ist unknownStockpileOrSignpostRelated der Werkstatt 0, bleibt der Zähler dauerhaft 0 und der Arbeiter hinge in Zustand 5",
            "Warum die Werkstatt Eisen +1/-1 und RT_IRONARMOR +1/-1 bucht (vermutlich nur die Anzeige der Werkstatt, denn jede Buchung löst updateBuildingGraphicsLayer aus); die tatsächliche Rüstung entsteht erst bei der Ablieferung in der Waffenkammer",
            "Ob das Ein-/Ausblenden (Zustand 0x6d) bei Schrittweite +2 ein Ausblenden beim Betreten und bei -2 ein Einblenden beim Verlassen ist, und was commitUnitLocation gegenüber resetUnitMovementState genau bedeutet, ist nur aus Namen abgeleitet",
            "Der Lagertyp für RT_IRON kommt aus der Tabelle DAT_StorageBuildingTypeArray (vermutlich BT_STOCKPILE); die Rückgaben von addResourceToStockpile werden nirgends geprüft"
        ]
    },
    "p3": {
        "erklaerung": "Der Rüstungsschmied holt ein Eisen aus einem Lager, trägt es in die Werkstatt, arbeitet dort und legt die fertige Rüstung einzeln in eine Waffenkammer mit Platz. Je Eisen kommen im Solo-Modus 1, sonst abwechselnd 1 und 2 Stück heraus (bei Produktivität 100).",
        "gehirn": "Rüstung braucht Eisen im Lager und freien Platz in einer erreichbaren Waffenkammer (50 Stück insgesamt, alle Waren zusammen, für das ganze Los). Fehlt der Platz beim Verlassen der Werkstatt, wartet der Schmied in Zustand 7 (Warnton nur für den aktuellen Spieler) und macht nicht weiter; Rüstung verfällt nur, wenn sich die Zielkammer erst auf dem Weg füllt. Feste Zeiten je Runde: 17 + 30 + 30 + 17 + 11 + 5 = 110 Aufrufe plus Wege und die unbekannte Wartezeit in Zustand 5.",
        "beleg": "code",
        "live": "Rüstungsschmied liefert ab → RT_IRONARMOR der Waffenkammer und finalWeaponsProduced[Spieler] vorher/nachher → beide steigen je Ablieferung um 1; über mehrere Runden sinkt das Lager-Eisen um 1 je Runde, und außer in GM_SOLITARY kommen abwechselnd 1 und 2 Stück je Eisen an",
        "live_art": "wirtschaft"
    },
    "korrigiert": "ja",
    "aenderung": "Zustand 5 wartet auf den Rückgabewert ungleich 0 (nicht auf den Zählerwert 1), Zustand 6 entscheidet entweder-oder nach dem Werkstatt-Eisen, commitUnitLocation läuft nur bei Schrittweite +2 (Betreten), bei voller Waffenkammer wartet der Arbeiter in Zustand 7 (nur auf dem Weg verfällt Rüstung), und die Zustände 0, 4, 7, 8, 9, 0x79, 0x6c, Tod/Verschwinden sowie die Mengenformel fehlten."
}

zeile = json.dumps(d, ensure_ascii=False)
assert "\n" not in zeile
if os.path.exists(ZIEL) and "--ueberschreiben" not in sys.argv:
    print("existiert schon, nichts geschrieben:", ZIEL)
    sys.exit(1)
with open(ZIEL, "w", encoding="utf-8", newline="\n") as f:
    f.write(zeile + "\n")
back = json.loads(open(ZIEL, encoding="utf-8").read())
print("ok", ZIEL, len(zeile), "Zeichen;", len(back["p2"]["regeln"]), "Regeln")
