# Anleitung: Funktionen von Stronghold Crusader 1.41 erklären (Phase 1–3)

## Eingabe
Die Eingabe ist eine Datei `eingang/<paket>.txt`. Jede Funktion darin beginnt mit dieser Kopfzeile:

`### <adresse> <name> | quelle=<nachgebaut|ghidra> | bereich=<Bereich>`

Danach folgt ihr Code.
- `nachgebaut` = geprüfter OpenSHC-Nachbau. Er ist verlässlich lesbar.
- `ghidra` = rohe Ghidra-Übersetzung. Die Feldnamen können irreführen; die Ghidra-Kommentare sind Vermutungen des OpenSHC-Teams.

## Ausgabe
Schreibe `ergebnisse/<paket>.jsonl`, **genau eine JSON-Zeile je Funktion**, in der Reihenfolge der Eingabe. Lass keine Funktion aus.

```json
{"adr":"0x...","name":"...","quelle":"nachgebaut|ghidra",
 "p1":{"bereich":"...","zweck":"ein Satz"},
 "p2":{"ein":"Parameter kurz","aus":"Rückgabe kurz","liest":["Felder/Tabellen"],"schreibt":["Felder"],
       "ruft":["aufgerufene Funktionen"],"regeln":["Bedingungen, Zahlen, Grenzen, Fehlergründe"],"offen":["Unklares"]},
 "p3":{"erklaerung":"1–3 Sätze in einfachem Deutsch: was die Funktion im Spiel bedeutet",
       "gehirn":"wie unser Spiel-Lenker das nutzen kann, oder \"-\" wenn ohne Nutzen",
       "beleg":"nachgebaut|code",
       "live":"Prüfpunkt fürs Spiel oder \"-\"",
       "live_art":"markt|anwerben|bauen|kampf|bewegung|ki-welle|wirtschaft|tabelle|sonstiges oder \"-\""}}
```

`live_art` ordnet den Prüfpunkt einer Spielsituation zu. Dann lassen sich in einem Spiellauf viele Punkte gemeinsam abhaken. `tabelle` heißt: Dazu muss nur eine feste Tabelle einmal aus dem Speicher gelesen werden; eine Spielhandlung ist nicht nötig. Diese Art wenn möglich bevorzugen.

## Der Prüfpunkt `live`
Wir erklären zuerst alles **ohne das Spiel zu starten**. Am Ende sammeln wir alle Prüfpunkte in einer Checkliste. Damit wollen wir in nur 1–2 Spielläufen möglichst alles belegen. Daher:
- `live` nur bei Aussagen, die für das Gehirn zählen und im Code nicht sicher sind. Beispiele: Zahlen, die UCP ändern könnte; Feldbedeutungen mit `Unk`/`field…`; Fehlergründe; Schwellen.
- Ein Prüfpunkt soll **im normalen Spielverlauf passiv messbar** sein, also durch Speicher lesen oder Zähler vorher und nachher vergleichen. Er braucht dann keinen eigenen Aufbau.
- Form: `was tun/beobachten → was lesen → erwarteter Wert`. Beispiel: `Befehl 38 verkaufen bei 120 Stein → Steinbestand vorher/nachher → sinkt um 20`.
- Sonst `"-"`. Die meisten Funktionen brauchen keinen Prüfpunkt.

## Regeln
1. **Deutsch, knapp und genau.** Bezeichner wie Feldnamen, Funktionen und Enums bleiben im Original.
2. **Nur behaupten, was im Code steht.** Vermutungen gehören in `offen` oder brauchen das Wort „vermutlich“. Feldnamen mit `Unk`, `field…`, `param_…` sind ungesichert.
3. **Zahlen sind das Wertvollste:** Grenzen, Kosten, Schwellen, Fehlercodes, Takte, Reichweiten. Alle gehören vollständig nach `regeln`. Ausdrücke wie `((a<b)-1 & 0xffffffe2) + 0x32` rechnest du in Klartext-Fälle um.
4. **Täuschende Namen benennen,** zum Beispiel: „prüft nur Kletternde“.
5. **Werte sind Grundwerte.** Der Code zeigt das unveränderte Spiel 1.41. Unser Spiel läuft mit UCP, das manche Werte zur Laufzeit ändert (Beispiel: Söldnerpreise). Feste Zahlen für Einheiten, Preise und KI gelten deshalb als Grundwert, nicht als Live-Wert.
6. **Für reine Hilfsfunktionen** (Destruktoren, Zeichenketten, Speicher, Darstellung) reichen `p1`, ein Satz `erklaerung` und `"gehirn":"-"`. Die Felder in `p2` sind dann leere Listen.
7. **Bei großen Funktionen über 15.000 Zeichen:** Fasse den Ablauf in 3–8 `regeln` zusammen, statt jede Zeile nachzuerzählen.
8. Gültiges JSON: Anführungszeichen in Texten mit `\"` maskieren und keine Zeilenumbrüche innerhalb einer Zeile.

## Beispiele
Siehe `probe_ergebnis.jsonl`, 18 fertige Einträge. Halte dich an deren Länge und Ton.

Zum Schluss nur die Rückmeldung: `<paket>: <Anzahl> Funktionen geschrieben`.
