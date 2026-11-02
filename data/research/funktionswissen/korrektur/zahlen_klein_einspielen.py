# -*- coding: utf-8 -*-
"""B-141: Berichtigt Grenzen kleinerer Funktionen direkt in funktionen_spiel.jsonl.
Die Rohuebersetzung im Paketcode (quelle=ghidra) liegt an diesen Stellen um eins neben Export und Assembly.
Je Funktion muss die Belegzeile im Export stehen und jeder alte Text genau einmal vorkommen, sonst bleibt sie unveraendert.
Lauf aus dem Ordner funktionswissen; ein zweiter Lauf aendert nichts mehr, weil die alten Texte dann fehlen."""
import json, re, sys
sys.path.insert(0, "korrektur")
from gegenprobe import lade_export

# Adresse: (Belege im Export, Vergleichszahlen im Assembly, Ersetzungen, zu entfernende Eintraege in offen)
F = {
    "0x00401150": ([r"0x18 < iVar2"], [0x18, 0x19], [
        ("durchsucht nur die ersten 25 Plätze", "durchsucht nur die Plätze 1 bis 24"),
        ("Gesucht wird nur auf den Plätzen 1 bis 25 von entityArray; Platz 0 und alles ab 26 wird nie geprüft", "Gesucht wird nur auf den Plätzen 1 bis 24 von entityArray; Platz 0 und alles ab 25 wird nie geprüft"),
        ("sonst werden nur die ersten 25 Objektplätze durchsucht", "sonst werden nur die Objektplätze 1 bis 24 durchsucht"),
        ("Warum nur 25 Plätze durchsucht werden", "Warum nur 24 Plätze durchsucht werden")], []),
    "0x00402180": ([r"0x77 < "], [0x77, 0x78], [("auf 100 bis 120 begrenzt (über 120 wird 0x77)", "auf 100 bis 119 begrenzt (über 119 wird 0x77)")], []),
    "0x00402580": ([r"0xf < "], [0xf, 0x10], [("ist f über 16, wird", "ist f über 15, wird")], []),
    "0x00406650": ([r"0x62 < ID_1077"], [0x62, 0x63], [("Höchstens 99 Möwen (Plätze 1-99), sonst 0", "Höchstens 98 Möwen (Plätze 1-98), sonst 0")], []),
    "0x00440360": ([r"iVar2 < 0x43", r"0x45 < iVar2"], [0x43, 0x45, 0x46], [
        ("die Typen 66 bis 70 werden nicht gezählt", "die Typen 67 bis 69 werden nicht gezählt"),
        ("ohne die Typen 66 bis 70.", "ohne die Typen 67 bis 69."),
        ("Einträge 66 bis 70 bleiben 0", "Einträge 67 bis 69 bleiben 0"),
        ("Welche Einheitentypen 66 bis 70 sind", "Welche Einheitentypen 67 bis 69 sind")], []),
    "0x00456670": ([r"0xb < DAT_GameState\.mapAndTime\.month"], [0xb, 0xc], [
        ("Ist month dann größer als 12:", "Ist month dann größer als 11:"),
        ("month läuft 0 bis 12", "month läuft 0 bis 11"),
        ("month erreicht höchstens 12, danach", "month erreicht höchstens 11, danach"),
        ("Ob month wirklich 13 Werte hat (0 bis 12) oder die Anzeige anders zählt", "Ob die Anzeige month anders zählt als 0 bis 11")], []),
    "0x004bc110": ([r"0xb < DAT_GameState\.mapAndTime\.month", r"month \+ -0xc"], [0xc], [
        ("ist month > 12, wird month + 12 und year + 1 gesetzt", "ist month > 11, wird month - 12 und year + 1 gesetzt"),
        ("Die Überlaufprüfung nimmt month statt monthCopy und addiert 12 statt 12 abzuziehen; sieht wie ein Fehler des Spiels oder der Ghidra-Übersetzung aus", "Die Überlaufprüfung nimmt month statt monthCopy; ob das Absicht ist, zeigt der Code nicht")], []),
    "0x00487c50": ([r"size < 0xc9"], [0xc8, 0xc9], [("Daten unter 200 Byte oder", "Daten bis 200 Byte oder")], []),
    "0x00490480": ([r"0xb3 < "], [0xb3, 0xb4], [("Alle 180 ms (mehr als) sendSomeMultiplayerSyncMessageWithType(0)", "Alle 180 ms (mindestens) sendSomeMultiplayerSyncMessageWithType(0)")], []),
    "0x0049b940": ([r"0x31 < DAT_GameState\.mapAndTime\.signpostsMapEdgeDataCounter"], [0x31, 0x32], [
        ("> 50 ist, also nach 51 Einträgen (Zähler 0 bis 50)", "> 49 ist, also nach 50 Einträgen (Zähler 0 bis 49)"),
        ("bis zu 51 davon", "bis zu 50 davon"),
        (" (bei nur 50 Plätzen würde der 51. Eintrag überlaufen)", "")], []),
    "0x0049be60": ([r"0x13a0f < "], [0x13a0f, 0x13a10], [("die Umlaufgrenze im Code ist aber 80400", "die Umlaufgrenze im Code ist aber 0x13a0f (80399)")], []),
    "0x004a6520": ([r"0x27 < iVar2", r"0x13a0f < "], [0x27, 0x28], [
        ("bis zu 41 Zielpunkte", "bis zu 40 Zielpunkte"),
        ("Abbruch, sobald mehr als 40 Paare gespeichert sind, also nach 41", "Abbruch, sobald mehr als 39 Paare gespeichert sind, also nach 40"),
        ("Die Warteschlange läuft nach 80400 über (bei den Nachbarfunktionen schon bei 0x13a0f = 79375)", "Die Warteschlange läuft nach Index 0x13a0f (80399) über")], []),
    "0x004a65e0": ([r"0x27 < iVar3"], [0x27, 0x28], [("Abbruch, sobald mehr als 40 Paare gespeichert sind, also nach 41", "Abbruch, sobald mehr als 39 Paare gespeichert sind, also nach 40")], []),
    "0x004ac650": ([r"section1127\) < 0x191"], [0x190, 0x191], [("ausgenommen in den ersten 400 Ticks (mapTimeInTicks minus section1127 kleiner als 400)", "ausgenommen bis einschließlich Tick 400 (mapTimeInTicks minus section1127 kleiner als 401)")], []),
    "0x004cb290": ([r"totalWoodAvailable < 0x5b", r"totalWoodAvailable < 0x1f"], [0x5a, 0x5b, 0x1e, 0x1f], [
        ("totalWoodAvailable < 90 → FALSE", "totalWoodAvailable < 91 → FALSE"),
        ("totalWoodAvailable < 30 → FALSE", "totalWoodAvailable < 31 → FALSE"),
        ("ab der 3. Hütte mindestens 30, ab der 6. mindestens 90.", "ab der 3. Hütte mindestens 31, ab der 6. mindestens 91."),
        ("bei Wert < 30", "bei Wert < 31")], []),
    "0x004ccbe0": ([r"0x13 < iVar3"], [0x13, 0x14], [
        ("Index 15-20 → 0xb9", "Index 15-19 → 0xb9"),
        ("Findet sich kein Treffer, bleibt der Index 20 und die Einheit landet ebenfalls in 0xb9; der Fall Index über 20 mit Rückgabe 0 tritt nie ein", "Findet sich kein Treffer, bleibt der Index 20 und die Rückgabe ist 0")], []),
    "0x004cdcf0": ([r"totalTroopValue < 0x65", r"aiCoordinatedAttackPatience < 0x31"], [0x64, 0x65, 0x30, 0x31], [
        ("totalTroopValue < 100, wird", "totalTroopValue < 101, wird"),
        ("erreicht sie 48, wird trotzdem", "erreicht sie 49, wird trotzdem"),
        ("höchstens bis ihre Geduld 48 erreicht", "höchstens bis ihre Geduld 49 erreicht")], []),
    "0x004d2500": ([r"0x1d < "], [0x1d, 0x1e], [("mehr als 30 Gold (currentResources[0xf])", "mindestens 30 Gold (currentResources[0xf])")], []),
    "0x004d39b0": ([r"0xb < param_1"], [0xb, 0xc], [("nur Einträge ab Index 13 (Waffen); der Kommentar im Code sagt 12, die Bedingung ist 12 < Index", "nur Einträge ab Index 12 (Waffen), die Bedingung ist 11 < Index")], ["Kommentar 'ab Eintrag 12' widerspricht der Bedingung ab 13"]),
    "0x004f1860": ([r"0x1e < "], [0x1e, 0x1f], [("(nach 31 zurück auf 0)", "(über 30 zurück auf 0)")], []),
    "0x004f2140": ([r"0xf9e < iVar2"], [0xf9e, 0xf9f], [("Sucht ab Nummer 1 bis 3999", "Sucht ab Nummer 1 bis 3998"), ("höchstens 3999 Felsen", "höchstens 3998 Felsen")], []),
    "0x004f3730": ([r"0x27 < DAT_LandscapeState\.wind\.index"], [0x27, 0x28], [
        ("größer 40 beginnt wieder bei 0, die Tabelle hat also mindestens 41 Einträge", "größer 39 beginnt wieder bei 0, die Tabelle hat also mindestens 40 Einträge"),
        ("Ob die Tabelle genau 41 Einträge hat", "Ob die Tabelle genau 40 Einträge hat")], []),
    "0x004f9980": ([r"x < 400"], [0x190], [("x und y unter 399 liegen", "x und y unter 400 liegen")], []),
    "0x004fbd80": ([r"0x24 < index", r"0x2f < iVar2"], [0x24, 0x25, 0x2f, 0x30], [
        ("Sonst Index über 37 wird", "Sonst Index über 36 wird"),
        ("Wert 28-48: drei Schritte (Richtung aus Tabellen); über 48: keine Änderung", "Wert 28-47: drei Schritte (Richtung aus Tabellen); über 47: keine Änderung")], []),
    "0x00518bb0": ([r"leDyingPerc < 0x65"], [0x64, 0x65], [("TRUE, wenn leDyingPerc kleiner als 100 ist", "TRUE, wenn leDyingPerc kleiner als 101 ist")], []),
    "0x0051bf70": ([r"iVar7 < 0x9c5"], [0x9c4, 0x9c5], [("muss kleiner 2500 sein (Radius 50 Felder)", "muss kleiner 2501 sein (Radius 50 Felder)")], []),
    "0x0051ccb0": ([r"iVar2 < 0x13"], [0x12, 0x13], [("ab 18 Ritter 6, 13 bis 17 Ritter 4", "ab 19 Ritter 6, 13 bis 18 Ritter 4")], []),
    "0x0051fa70": ([r"distanceHigh < 0x29"], [0x28, 0x29], [("kleiner als 40 ist", "kleiner als 41 ist"), ("bei weniger als 40 Feldern Abstand", "bei höchstens 40 Feldern Abstand")], []),
    "0x0052b860": ([r"0x4e1 < \(int\)DAT_CurrentTribeID"], [0x4e1, 0x4e2], [("Schleife über Gruppen-ID 1 bis 1250 (einschließlich)", "Schleife über Gruppen-ID 1 bis 1249 (einschließlich)"), ("alle 1250 Gruppen", "die Gruppen 1 bis 1249")], []),
    "0x0052dd20": ([r"0x63f < "], [0x63f, 0x640], [("Warteschlange fasst bis 1601 Einträge", "Warteschlange fasst bis 1600 Einträge")], []),
    "0x0052f730": ([r"0x31 < DAT_GameState\.mapAndTime\.field45_0xf8", r"0x9c3 < iVar1"], [0x31, 0x32, 0x9c3, 0x9c4], [("über 50 springt es auf 0", "über 49 springt es auf 0"), ("oder über 2500 wird 0", "oder über 2499 wird 0")], []),
    "0x00532f80": ([r"DAT_UnitCount < 0x65"], [0x64, 0x65], [("bei unitCount unter 100, sonst", "bei unitCount unter 101, sonst")], []),
    "0x00539df0": ([r"'3' < "], [0x33, 0x34], [("mit Byte-Wert ueber 52", "mit Byte-Wert ueber 51"), ("Grenzen 51 und 52", "Grenze 51")], []),
}


def zaehlen(o, s):
    if isinstance(o, str): return o.count(s)
    if isinstance(o, list): return sum(zaehlen(v, s) for v in o)
    if isinstance(o, dict): return sum(zaehlen(v, s) for v in o.values())
    return 0


def ersetze(o, a, b):
    if isinstance(o, str): return o.replace(a, b)
    if isinstance(o, list): return [ersetze(v, a, b) for v in o]
    if isinstance(o, dict): return {k: ersetze(v, a, b) for k, v in o.items()}
    return o


zeilen = [json.loads(z) for z in open("funktionen_spiel.jsonl", encoding="utf-8") if z.strip()]
ges = {x["adr"].lower(): x for x in zeilen}
fertig, stellen, abgelehnt, ohne_asm = [], 0, [], []
for a, (belege, zahlen, ers, weg) in F.items():
    e = lade_export(a)
    fehlt = [b for b in belege if not re.search(b, e["pseudocode"])]
    if fehlt:
        abgelehnt.append((a, "Beleg fehlt", fehlt))
        continue
    cmp = {int(m.group(1), 16) for z in e["assembly"] for m in [re.search(r"^CMP .*,(0x[0-9a-f]+)$", z["text"])] if m}
    if not cmp & set(zahlen):
        ohne_asm.append(a)
    x = ges[a]
    teil = {k: x[k] for k in ("p1", "p2", "p3")}
    nicht = [t for t, _ in ers if zaehlen(teil, t) != 1]
    if nicht:
        abgelehnt.append((a, "Text nicht genau einmal", nicht))
        continue
    for t, n in ers:
        teil = ersetze(teil, t, n)
    for t in weg:
        teil["p2"]["offen"] = [o for o in teil["p2"]["offen"] if o != t]
    x.update(teil)
    x["zahlen_korrektur"] = "B-141: Grenzen gegen Export und Assembly berichtigt, der Paketcode lag um eins daneben"
    fertig.append(a)
    stellen += len(ers) + len(weg)
with open("funktionen_spiel.jsonl", "w", encoding="utf-8") as f:
    for x in zeilen:
        f.write(json.dumps(x, ensure_ascii=False) + "\n")
print("berichtigt", len(fertig), "Funktionen,", stellen, "Stellen; abgelehnt", len(abgelehnt), abgelehnt, "; ohne passendes CMP im Assembly", ohne_asm)
