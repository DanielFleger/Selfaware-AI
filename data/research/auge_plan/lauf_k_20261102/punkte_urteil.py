# -*- coding: utf-8 -*-
"""B-142: Urteil je Einzelpunkt nach Lauf K (02.11.2026 23:49). Die Urteile sind von Hand aus den Belegen geschrieben, die Rechnungen dazu stehen in punkte_rechnen*.py, ihre Ausgaben in punkte_rechnung*.txt.

Schreibt Punkte_Lauf_K.md und punkte_urteil.json, traegt bestaetigte und widerlegte Punkte als live_ergebnis ins Funktionswissen ein,
vergleicht die Punkte mit Marke [Spielart] mit Lauf F (Spielart_Lauf_K.md), legt die Feldluecken offen (feldluecken_lauf_k.csv), haengt sie an die Feldliste an und schreibt die Restliste nie_gesehen_lauf_f_und_k.csv.
Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/punkte_urteil.py
"""
import collections
import csv
import json
import os

HIER = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(HIER, "..")
B = os.path.join(PLAN, "laeufe", "lauf_k_20261102_234952")
F = os.path.join(PLAN, "lauf_f_20261102")
FW = os.path.join(HIER, "..", "..", "funktionswissen", "funktionen_spiel.jsonl")
LAUF = "Lauf K 02.11.2026 23:49, Instanz 2, Green Haven, 8 KI, Liga-Balance"

B_, W_, G_, L_, O_ = "bestaetigt", "widerlegt", "gemessen", "Lage fehlte", "offen"
NICHT_GEFECHT = "Läuft im Gefecht nicht: `aiControlNonSkirmishUnitMovement` 0x00520F70 schließt `gameMode_2` 3 aus, alle Felder blieben 0. Zuständig: Kampagnenmission oder Burgenbau mit Angriffswellen (Invasion)."
U = {
    "P242": (B_, "Die Arten 10, 12, 11 sind `ET_FLAG_1`, `_2`, `_4`. 814 von 814 Flaggenwechseln im Kampf passen: Wert 3 nur mit gesetztem Nervositäts- oder Abriss-Merker (28 von 28), die anderen nie (786 von 786). In den strengen Fenstern 100 von 100 auf 0, 1, 2 nach der Rekrutier-Wahl, 4 bis 126 Takte nach deren Wechsel: Das ist das Ende der Flaggen-Animation."),
    "P243": (B_, "Vier Bauten der laufenden Welle standen am Wellenende noch (Spieler 3 bei 125.803, Spieler 1 bei 150.201): alle im selben Takt auf `BLS_REMOVE`. 29 weitere wurden vorher zerstört. Die 12 Bauten mit Welle 0 (Belästigung, Ballisten) bleiben stehen, der Code verlangt `0 < attackWave`: Ein Katapult von Spieler 2 überlebte das Wellenende bei 48.804 bis 50.826."),
    "P244": (L_, "Keine Außenposten auf `Green Haven`, die Arten 106 und 107 kamen nicht vor. Zuständig: Karte mit Außenposten (Lauf S)."),
    "P245": (B_, "240 Neuaufbauten in t1, t6, t8 (`gameTicksLoadBalancer` 0x47 bis 0x4E): Index gleich eigener Zählung in 240 von 240, 0 Einträge ausgeschlossener Arten, 0 aus dem eigenen Team. Je Aufbau fallen 133 bis 180 Bauten durch den Filter."),
    "P246": (B_, "Geklärt: `noRubble` heißt falsch, es steht auf 1, wenn **Schutt bleibt**. `destroyBuildings` setzt `showNoRubble = (Tabelle == 0)`, `destroyBuilding` setzt das Feld, wenn `showNoRubble` 0 ist. 143 von 146 Fällen haben Tabelle ungleich 0. Die 3 anderen sind verbundene Bauten, die mitfallen (gleiches `uidWhenPlaced`, gelesen): Steinbruch 20 mit Halde 21, Söldnerposten 8 mit den Arten 56, 57, 58. 47 zerstörte Bauten mit Tabelle 0 blieben auf 0."),
    "P247": (W_, "Die Liga ersetzt die Namen im Spiel; die Formel 0x67 + 8 x Typ + Variante trifft 1 von 8. Geschrieben wird ab Eintrag 1 über 8 Plätze, Variante 0."),
    "P248": (B_, "`startGoods` ist Zeile 0 der Tabelle plus Gold 2000 = Startgold; Truppen = Zeile der KI, erste Intensitäts-Spalte, x 75 % (`fairness` 2; KI 14: 16 auf 12, KI 1: 14, 5, 9 auf 10, 3, 6); TicksLeft 12000 = NoRushTicks[1]. Werte in `punkte_start.txt`."),
    "P249": (B_, "KI 2000 = Tabelle[27], Mensch 4000. `popularity` 10000 = 1000 x 10."),
    "P250": (B_, "36 von 36 lesbaren neuen Bauten: alle 8 Nachbarn frei, Höhenunterschied 0. Abstand zur Auswahl-Einheit 7 bis 29 Felder in 22 Fällen; Luftlinie ist die untere Grenze der Wegschritte, also mindestens 5. Bei 9 Bauten war die Karte schon neuer als der Bau, sie zählen nicht."),
    "P251": (W_, "Werte 0, 1, 10; keine 2 und keine 8. Zone 1: 1.905 bis 2.001 Felder, Zone 10: 100 bis 110."),
    "P252": (B_, "Bis zu 50 Einträge je angegriffenem Spieler (7 Spieler 50, Spieler 8: 9), der erste ist in 8 von 8 Fällen der Burgeingang des Ziels, Gruppe immer 0. Die erste Lesung war falsch: Die Zeile hat 800 Bytes, die Feldkarte nennt nur 16."),
    "P253": (B_, "Beim gerechneten Ziel Spieler 4 haben 1.916 von 1.916 Feldern der Zone 1 den Wert 1. Werte 2 bis 6 für die Ziele 1 bis 4: 4.519 von 4.519 Feldern haben einen Nachbarn in den vier Richtungen mit Wert minus 1."),
    "P254": (L_, "Keine Verbündeten, der Befehl kommt nur vom Spieler (`SendPlayerToPlayerRequestOrResponse`). Zuständig: Partie mit Mensch und Bündnis."),
    "P255": (G_, "Gefecht: `currentGameMode` 99, `gameMode_2` 3, `eventsCount` 0. Der Ereignismotor arbeitet im Gefecht nicht."),
    "P256": (L_, "Nur Außenposten-Gruppen rufen die Funktion (`aiRegisterTribeAndAssignTarget` aus `UpdateOutpostBuilding`), keine auf der Karte. Zuständig: Karte mit Außenposten (Lauf S)."),
    "P257": (B_, "20 von 20 Lesungen mit Vorlauf (der Datenblock wird alle 250 Takte gelesen) treffen die Rechnung Ist kleiner Max eines Spielers mit Wahl Angriff, mit den Sonderregeln Welle x 4 und `moatsOwned` größer 5 in der Rechnung. Die 3 ersten Lesungen je Fenster haben keinen Vorlauf und zählen nicht."),
    "P258": (W_, "Nicht 30, sondern 50 wie in Lauf F (Liga). Das Gold fällt, wenn der Bauer die neue Art bekommt, nicht wenn der Ingenieur erscheint (`nonEuroRecruit`). Spieler 7 bei Takt 71.486 (Fenster t6): Speerträger, Bogenschütze und Ingenieur zusammen 70, die beiden anderen kosten allein je 10. `isEngineerRequired` wechselte im ganzen Kampf nur einmal, bei 0 Gold ohne Kauf; die anderen Ingenieure kommen über `aiRecruitUnits`. Preise allein gemessen: Art 22 10, 23 30, 24 10, 25 40, 28 120, 37 10, 70 60, 71 10, 72 15, 75 100."),
    "P259": (B_, "Spieler 2 (KI 15, Max 1): Index 0 auf 1 bei Takt 37.203. Bauern tragen 0x16 auf dem Weg zum Ingenieur (17), Katapulte 0x15 (6). Das Katapult zeigt in 12 von 12 Fällen auf `attackedPlayerID`, 4 davon sind einen Augenblick früher da als der Wert im selben Monatstakt."),
    "P260": (B_, "Einheiten mit Verhalten 6 sind nur Art 22 (Spieler 2, +0x150 = 22) und Art 70 (Spieler 8, +0x150 = 70). 561 von 561 Anstiegen unter der Grenze. Die anderen werben nicht: +0x150 = 5 ist Tunnelgräber und ausgeschlossen (Spieler 5), keine Kaserne (Spieler 4, 6), +0x150 = 37 kam in diesem Lauf bei keinem (Spieler 1, 3, 7 hatten Kaserne und Bedarf): Mönche laufen hier über `euroRecruit`, ihr Preis steht in `nonEuroRecruit`; der Grund ist damit vermutet, nicht gemessen."),
    "P261": (B_, "Verhalten 7: Art 75, 28, 24, 72, 24 bei den Spielern 1, 2, 3, 5, 7, gleich +0x158. 1.481 von 1.481 Anstiegen unter der Grenze; der Höchstwert ist genau +0x154: 16, 4, 8, 15, 9."),
    "P262": (G_, "Die drei Listen ausgelesen, Werte in `punkte_rechnung1.txt`."),
    "P263": (B_, "Erstwellen 59 mindestens 58, 10 mindestens 10, 31 mindestens 30, 84 mindestens 84. Spätere Wellen starten früher, weil die Stärke bei einem schwachen Ziel zurückgesetzt wird."),
    "P264": (W_, "UCP ersetzt die Formel (`ai_addattack` relativ, `ai_attacklimit` 3000): Stärke = AttForceBase x Welle + 5, ohne Zufall, ohne Deckel 200. Gemessen KI 14: 63, 121, 179, 237, 295, 353, 411, 469; KI 15: 15 bis 55; KI 1: 35 bis 155; KI 9: 89, 173, 257."),
    "P265": (B_, "21 von 21 Wellenstarts passen: Ziel unter 500 Gold ergibt -(Base / 2) x Zufall (-1 bei KI 1 und 9), KI unter 1000 Gold ergibt 0, sonst 0 bis RaidUnitsRandom (+3, +2 bei KI 15). Beim Start -3, -2, -1 bei den Spielern 6, 7, 8: Das Ziel ist dort noch Spieler 0 ohne Gold."),
    "P266": (B_, "`shortestDistance` gleich `signpostEntryData[ki-1]` bei jeder Welle: 154,261; 317,210; 251,164; 212,354 und weitere."),
    "P267": (B_, "Spieler 3 ist der einzige mit Gruppe 0x11: Bei `moat2` größer 0 wird sie im Zustand 5 am vierten Wochenaufruf aggressiv (96.607 auf 97.403). Alle 5 Einheiten mit Ziel 1015 haben `moat2` größer 0 und stehen in der Grabenliste."),
    "P268": (L_, "Kein Ziel brannte beim Wechsel: 300 Zielwechsel, 0 mit Feuer; im ganzen Kampf brannten nur je eine Eisenmine oder Apfelfarm. 4 Wechsel im Zustand 6, davon 2 mit verschwundenem Ziel. Zuständig: Lauf S mit Feuerwerfern."),
    "P269": (B_, "Rammen: Ziel 1014 (Tor) nur mit `gate2` ungleich 0, 8 von 8. Ziel 1043 nur mit `gate2` 0 und `wide3` ungleich 0, 6 von 6."),
    "P270": (W_, "Stufen 0, 1, 2 ja. Höhere Stufe wird nicht häufiger: Spieler 1 bleibt immer 0, Spieler 3 geht 2, 1, 0, 2."),
    "P271": (L_, "Vor Takt 12.000 läuft die Friedenszeit, kein Feind mit Fernkämpfern. Danach bestätigt: 8 von 8 Nervositätsbeginnen mit relativer Stärke unter 75 (7 bis 65) und Fernkampfwert ab 100. Zuständig: Gefecht ohne Friedenszeit."),
    "P272": (B_, "Truppen stehen an der Wunschzahl Parameter + RaidUnitsBase: KI 14: 3, KI 15: 16, KI 1: 3, KI 4: 4. Über der Zahl nur 5 von 1.663 Lesungen bei Spieler 3, direkt nach dem Wellenende bei 125.803, wenn Angriffstruppen zurückkommen."),
    "P273": (L_, "`decideOnTribeAttackLocation` ruft nur `makeOutpostTribesAttack`; `counter` und `randomNumber` bleiben 0. Keine Außenposten. Zuständig: Karte mit Außenposten (Lauf S)."),
    "P274": (B_, "Spieler 1: delay 1, 2, 3 je 50 Takte, dann Erzeugen, +0x11c = 4. UCP hebt die Grenze von 3 Geräten auf (0x004D20A2)."),
    "P275": (B_, "14 Jahreswechsel, Ziele der Raubzug-Gruppen: 19 bleiben, 0 werden 0, 0 ändern sich. `yearChanged` steht nur bei Tagestakt 0, die KI ist bei 1 bis 8 am Zug."),
    "P276": (B_, "52 von 52 Monatsaufrufen: Zustand und Gefühl stimmen mit der Rechnung. Genau auf einer Grenze lagen Gold 200 und Truppen 8; Volk 15 und Nahrung 20 kamen nicht vor, sie stehen so im Code (`0xe <`, `0x13 <`). UCP ändert hier nur den Start: `ai_recruitstate_initialtimer` 0 statt 4800 Takte Verteidigung."),
    "P277": (B_, "52 von 52 Monatsaufrufen: `isNotNervousByEnemyTroopValue` folgt der Rechnung Feindwert + Zuschlag gegen Truppenwert in Burgnähe. Bei Feindwert 150 ergibt das die erwarteten 170; dieser Wert selbst kam nicht vor."),
    "P278": (B_, "52 von 52 Monatsaufrufen in den strengen Fenstern, alle drei Wahlarten; Wahl 2 ist der kleinste größte Achsenabstand (Spieler 4: 7, 6, 1). Dazu `ai_assaultswitch` (0x004D477B): Ab Zustand 3 bleibt das Ziel, solange dessen Lord lebt. Im ganzen Kampf kein Verstoß: Die 5 scheinbaren Fälle sind 3 x Zustand 9 auf 0 im selben Takt und 2 x ein sterbender Lord, den `getAliveLordForPlayer` schon nicht mehr zählt."),
    "P279": (B_, "Nur 0, 2, 3, 4, 5, 6, 7, 9 sichtbar, Folge 0, 2, 3, 4, 5 oder 6, 9. Wechsel bei Takt modulo 200 gleich Spieler."),
    "P280": (B_, "Ausrichtung 0, 2, 4, 6, alle Versätze = Burg minus 43."),
    "P281": (L_, NICHT_GEFECHT), "P282": (L_, NICHT_GEFECHT), "P283": (L_, NICHT_GEFECHT), "P284": (L_, NICHT_GEFECHT), "P285": (L_, NICHT_GEFECHT), "P286": (L_, NICHT_GEFECHT), "P287": (L_, NICHT_GEFECHT), "P288": (L_, NICHT_GEFECHT),
    "P289": (B_, "134 Berechnungen im Kampf: `wide(-8)` = `wide(-0xc)` 134 von 134, `scale(-0x10)` = `hack(-0xc)` 133 von 134, `wide` + `hack` gleich eigener Mauerzählung 127 von 134, bis 3 daneben 131. Auf Tempo 1000 liest die Aufzeichnung auch mitten in der Rechnung und die Karte ist bis 45 Takte alt; beides erklärt vermutlich den Rest, einzeln nachgesehen sind die 7 nicht."),
    "P290": (L_, NICHT_GEFECHT), "P291": (L_, NICHT_GEFECHT), "P292": (L_, NICHT_GEFECHT), "P293": (L_, NICHT_GEFECHT),
    "P294": (W_, "Vorgekommen: 1010, 1012, 1014, 1015, 1019, 1043. 1012 (0x3F4, Leiternträger) fehlt in der erwarteten Liste, `assignAttackTargetsForTribe` schreibt ihn ebenso."),
    "P295": (W_, "Mit UCP sagt der Wert nicht mehr das Ziel: `ai_attackwave` (Stufe 7) lässt Ziel 1010 reihum 4 x Mauern, 2 x Türme und Tore, 1 x Gebäude suchen. Gemessen 548, 192, 155 von 896 (Platz 0 ist ein Merkplatz und zählt nicht). Die anderen stimmen: 1012 Mauerliste 6 von 6, 1014 Torliste 8 von 8, 1015 Grabenliste 5 von 5, 1043 Breitenliste 6 von 6. 1013 und 1021 kamen nicht vor."),
    "P296": (B_, "Wellen bei Takt 202, 404, 603, 822; die erste nichtleere Art sinkt um höchstens 9: 12 auf 3, 10 auf 1, 22 auf 13, 24 auf 15."),
}
# Die Punkte, die das Urteil von Lauf F auf Lauf K verschoben hat; Rechnung punkte_f_nach_k.py, p053_aiv_orte.txt
UF = {
    "P001": (L_, "Jeder gegen jeden: `playerTeams` 8, 1, 2, 3, 4, 5, 6, 7, keine gleiche Nummer. Zuständig: Gefecht mit Bündnis."),
    "P007": (B_, "8 von 8: maxHealth = 150.000 x Faktor der Tabelle mit Index aiType minus 1: KI 15 120 % = 180.000, KI 1 50 % = 75.000, KI 9 110 % = 165.000, KI 2 70 % = 105.000, die anderen 100 %."),
    "P021": (B_, "25 von 25 Preisen gleich dem Burgenbau aus Lauf F, also nicht aus der Karte. Es sind die Liga-Preise."),
    "P052": (B_, "Alle 8 KI: Zähler 11 bis 24, Cooldown 0. Der Zweig ohne Eisen in Reichweite kam nicht vor."),
    "P053": (B_, "Nur Status 0 und 1. 1.634 von 1.634 Bau-Schritten liegen im 100x100-Feld ab dem Versatz. Bei den 593 Wand-Schritten ist `location` keine Kachel, sondern der Anfang in `locationsArray`; davon je Spieler 9 Felder geprüft, alle im Feld."),
    "P054": (G_, "Eisen in 62 Zellen, Summe 595; Felsbrocken in 147 Zellen, Summe 1.729; Öl 0. Mit den Vorkommen der Karte nicht verglichen."),
    "P181": (B_, "Unter der kritischen Beliebtheit steht die Steuer im Wochentakt auf 2: 1.056 von 1.058 Lesungen (Spieler 6 und 8, die einzigen unter ihrer Grenze). Die 2 anderen zeigen 3 bei Spieler 8, nicht einzeln nachgesehen."),
    "P182": (B_, "Direkt gerufen, echte KI: 5 Hütten: Wert 30 nein, 31 ja. 6 und 7 Hütten: 90 nein, 91 ja. Gezählt wird mit Filter: Spieler 1 hat 7, gezählt 5. Decke je KI 1 bis 10. `rufen_*.json`."),
    "P183": (W_, "Direkt gerufen, echte KI: Zähler +1 je Aufruf stimmt. Der Wunsch 5 entsteht aber bei Zähler 3, nicht bei 37. War er schon 3, bleibt er. Die Funktion weicht im Speicher ab (14 Befehle). `rufen_*.json`."),
    "P184": (B_, "Schritt +1 (52 von 60 Wechseln), Höchstwert 100. Dazu -1 (8 Wechsel): `getTargetableBuildingForPlayerID` zieht ab."),
    "P185": (L_, "Kein Team. Zuständig: Gefecht mit Bündnis."),
    "P186": (B_, "Stichprobe: Spieler 3 verkauft Ware 13 bei 56 auf 50, Grenze 52 mit Spielraum. In 54 Fällen fiel eine Ware über ihrer Grenze im Verkaufstakt; je Aufruf wird nur eine Ware verkauft, die übrigen gezählten Fälle sind Verbrauch im selben Takt."),
    "P187": (L_, "Kein Bündnis. Zuständig: Gefecht mit Bündnis."),
    "P188": (G_, "12 von 47 neuen Warenwünschen im Wert +0x9c der KI, 15 weitere gehören zum Holz. Die anderen stammen aus anderen Wegen; `euroUnitAcquisitionFailReason` ist nicht mitgelesen, die Lage ist daher nicht eindeutig."),
    "P189": (B_, "`willBuy` wechselt nur im Tagestakt des Spielers: 764 von 768, sonst 0 von 38.065. Die 4 ohne Wechsel sind nicht einzeln nachgesehen."),
    "P191": (B_, "Im Lauf, Gold alle 5 Takte gesetzt: 20.000: +2 (17 Sprünge), 10.000: +1 (19), je rund alle 50 Takte. 3.000: +1 nur rund alle 100 Takte (Wartezeit 2). Direkt gerufen endete das Spiel mit Absturz bei 0x42E812, Ursache nicht geklärt. `rufen_*.json`."),
    "P192": (W_, "Feindgebäude: nur das angrenzende Feld ist verboten, Turm, Hütte und Lager gleich. 4 Felder Abstand sind erlaubt. Die Grenze 5 gilt für Feind-Einheiten: Abstand 1 bis 4 verboten, ab 5 frei. `rufen_*.json`."),
    "P194": (B_, "`moatsOwned` gleich eigener Zählung der Grabenfelder in `moats[]`: 448 von 448 Monatstakten."),
    "P199": (B_, "Direkt, Einzelfeld: Lager des Gegners (Art 10): unter 7 Felder vom Rand verboten mit Grund 0x13. Hütte und Turm zählen nicht. Feind-Einheit: unter 15 Felder verboten, Grund 0x11. Außerhalb der Reichweite: Grund 0x12. `rufen_*.json`."),
    "P201": (B_, "Direkt gerufen: Reichweite 45, 50, 60, 70 je Kartengröße 160, 200, 300, 400, um den Punkt 140, 268 bei Burg 138, 262. Karte 200: entferntestes Feld 50 geht, 51 Grund 0x12. Käfige ab 10 Grund 1000. Farm: Grund 0x16 an 742 Stellen, 0x17 (unter 50 Gras) an einer. `rufen_*.json`."),
}
STANDARD = {"gemessen": (G_, "Einmal gelesen, Werte in punkte.json."), "nicht gesehen": (L_, "Feld hat sich nicht geändert."), "nicht zuordenbar": (O_, "Kein Feld erkannt.")}

punkte = json.load(open(B + ".punkte.json", encoding="utf-8"))["punkte"]
aus = []
for x in punkte:
    u, g = U.get(x["nr"], STANDARD.get(x["urteil"], (O_, "Kein Urteil geschrieben.")))
    aus.append({"nr": x["nr"], "funktion": x["funktion"], "urteil": u, "grund": g, "lauf_k_werkzeug": x["urteil"]})
z = collections.Counter(a["urteil"] for a in aus)
funktion_f = {p["nr"]: p["funktion"] for p in json.load(open(os.path.join(F, "punkte_urteil.json"), encoding="utf-8"))["punkte"]}
aus_f = [{"nr": nr, "funktion": funktion_f[nr], "urteil": u, "grund": g} for nr, (u, g) in UF.items()]
z_f = collections.Counter(a["urteil"] for a in aus_f)
fehlt = [a["nr"] for a in aus if a["nr"] not in U]
with open(os.path.join(HIER, "punkte_urteil.json"), "w", encoding="utf-8") as f:
    json.dump({"lauf": LAUF, "zaehlung": z, "punkte": aus, "aus_lauf_f_zaehlung": z_f, "aus_lauf_f": aus_f}, f, ensure_ascii=False, indent=0)

zeilen = ["# Einzelpunkte Lauf K", "", f"{LAUF}. Geschrieben von SRE aus den Belegen, Rechnungen in `punkte_rechnen*.py`.", "",
          "**Worte:** bestätigt und widerlegt heißen: Die Lage kam vor und die Rechnung ist gemacht. gemessen: einmal gelesen, Erwartung war \"notieren\". Lage fehlte: Die Lage kam in diesem Lauf nicht vor, der zuständige Lauf steht dabei.", "",
          "| Urteil | Punkte |", "|---|---|"] + [f"| {k} | {z[k]} |" for k in (B_, W_, G_, L_, O_)] + [""]
for k, titel in ((W_, "Widerlegt"), (B_, "Bestätigt"), (G_, "Gemessen"), (L_, "Lage fehlte"), (O_, "Offen")):
    zeilen += [f"## {titel} ({z[k]})", "", "| Punkt | Funktion | Beleg |", "|---|---|---|"]
    zeilen += [f"| {a['nr']} | `{a['funktion']}` | {a['grund']} |" for a in aus if a["urteil"] == k]
    zeilen.append("")
zeilen += ["## Aus Lauf F verschoben (" + str(len(aus_f)) + ")", "", "Das Urteil von Lauf F schob diese Punkte auf Lauf K. " + ", ".join(f"{k}: {z_f[k]}" for k in (B_, W_, G_, L_) if z_f[k]) + ".", "", "| Punkt | Funktion | Urteil | Beleg |", "|---|---|---|---|"]
zeilen += [f"| {a['nr']} | `{a['funktion']}` | {a['urteil']} | {a['grund']} |" for a in aus_f] + [""]
open(os.path.join(HIER, "Punkte_Lauf_K.md"), "w", encoding="utf-8").write("\n".join(zeilen))
print(dict(z), sum(z.values()), "ohne Urteil", fehlt)

# Funktionswissen: bestaetigt und widerlegt je Funktion
je = collections.defaultdict(list)
for a in aus + aus_f:
    if a["urteil"] in (B_, W_):
        je[a["funktion"]].append({"lauf": LAUF, "punkt": a["nr"], "urteil": a["urteil"], "befund": a["grund"]})
roh = open(FW, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in roh else "\n"
neu, treffer = [], set()
for z_ in roh.split(nl):
    if not z_.strip():
        neu.append(z_)
        continue
    e = json.loads(z_)
    if e["name"] in je:
        alt = [x for x in e.get("live_ergebnis", []) if x.get("lauf") != LAUF]
        e["live_ergebnis"] = alt + je[e["name"]]
        treffer.add(e["name"])
        z_ = json.dumps(e, ensure_ascii=False)
    neu.append(z_)
open(FW, "w", encoding="utf-8", newline="").write(nl.join(neu))
print("Funktionswissen ergaenzt:", len(treffer), "von", len(je), "Funktionen; ohne Treffer:", sorted(set(je) - treffer)[:6])

# Punkte mit Marke [Spielart]: Sagt das Werkzeug in beiden Spielarten dasselbe?
sp = json.load(open(B + ".spielart.json", encoding="utf-8"))["punkte"]
pf = {p["nr"]: p for p in json.load(open(os.path.join(F, "lauf_f_214240.punkte.json"), encoding="utf-8"))["punkte"]}
uf = {p["nr"]: p for p in json.load(open(os.path.join(F, "punkte_urteil.json"), encoding="utf-8"))["punkte"]}
zeilen = ["# Punkte mit Marke [Spielart]: Burgenbau gegen Gefecht", "", f"{len(sp)} Punkte. Lauf F war Burgenbau (`currentGameMode` 0, `gameMode_2` 2), Lauf K Gefecht (99, 3). Die Spalte Lauf F ist das Urteil von Hand, die Spalte Lauf K das Werkzeug: Wo die Zahl aus Lauf F auch im Gefecht vorkommt, steht \"zahl passt\". Nachgerechnet von Hand sind nur die Punkte der Liste Lauf K.", "",
          "| Punkt | Funktion | Lauf F | Lauf F Werkzeug | Lauf K Werkzeug | Beleg Lauf K |", "|---|---|---|---|---|---|"]
wechsel = collections.Counter()
for p in sp:
    a, b = pf.get(p["nr"], {}).get("urteil"), p["urteil"]
    wechsel[(a, b)] += 1
    zeilen.append(f"| {p['nr']} | `{p['funktion']}` | {uf.get(p['nr'], {}).get('urteil', '')} | {a} | {b} | {str(p.get('grund', ''))[:160].replace('|', '/')} |")
zeilen += ["", "## Zählung (Werkzeug Lauf F, Werkzeug Lauf K)", ""] + [f"- {k[0]} / {k[1]}: {v}" for k, v in sorted(wechsel.items(), key=str)] + [""]
open(os.path.join(HIER, "Spielart_Lauf_K.md"), "w", encoding="utf-8").write("\n".join(zeilen))
print("Spielart", len(sp), sorted(wechsel.items(), key=str))

# Feldluecken und Restliste
from selfaware.tools.analysis.auge_feldkarte import TECHNIK  # noqa: E402

e = json.load(open(B + ".ergebnis.json", encoding="utf-8"))
A1 = [x["daten"] for x in e["proben"] if x["nr"].split()[0] == "A1"]
luecken = {}
gesehen_k = set()
for d in A1:
    gesehen_k.update(tuple(y) for y in d["gesehen"])
    for y in d["luecken"]:
        k = (y["global"], y["feld"])
        a = luecken.setdefault(k, [0, y["erster_takt"]])
        a[0] += y["aenderungen"]
        a[1] = min(a[1], y["erster_takt"])
with open(os.path.join(HIER, "feldluecken_lauf_k.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["global", "feld", "aenderungen", "erster_takt", "art"])
    for (g, fe), (n, t) in sorted(luecken.items()):
        w.writerow([g, fe, n, t, "technik" if TECHNIK.search(g) else ("ohne_name" if "+0x" in fe else "mit_name")])
LISTE = os.path.join(PLAN, "zustand_felder.csv")
roh = open(LISTE, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in roh else "\n"
schon = {(z_.split(";")[1], z_.split(";")[2]) for z_ in roh.split(nl)[1:] if z_.count(";") >= 2}
dazu = []
# Die Listen der Spieler 1 bis 8 liegen je 0x177BC weiter in attackInfo, die Struktur benennt dort tausende Felder falsch oder gar nicht: eine Zeile fuer alle
zusammen = sorted({(g, "attackInfo" if g == "DAT_TroopValueState" and fe.startswith("attackInfo.") else fe) for g, fe in luecken})
for g, fe in zusammen:
    if TECHNIK.search(g) or (g, fe) in schon:
        continue
    dazu.append(f"{g};{g};{fe};lauf_k;0;;nein;{'ja' if '+0x' in fe or 'field' in fe or 'Unk' in fe else 'nein'}")
if dazu:
    open(LISTE, "w", encoding="utf-8", newline="").write(roh.rstrip("\r\n") + nl + nl.join(dazu) + nl)
print("Feldluecken", len(luecken), "davon Technik", sum(1 for k in luecken if TECHNIK.search(k[0])), "neu in der Liste", len(dazu))
A2 = next(x["daten"] for x in e["proben"] if x["nr"].split()[0] == "A2")
nie_k = {tuple(y) for y in A2["nie"]}
with open(os.path.join(F, "nie_gesehen_lauf_f.csv"), encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter=";")
    next(r)
    nie_f = {tuple(y) for y in r}
beide = sorted(nie_f & nie_k)
with open(os.path.join(HIER, "nie_gesehen_lauf_f_und_k.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["global", "feld"])
    w.writerows(beide)
print("nie gesehen: F", len(nie_f), "K", len(nie_k), "beide", len(beide))
je_global = collections.Counter(g for g, _ in beide)
print("je Bereich", je_global.most_common(20))
