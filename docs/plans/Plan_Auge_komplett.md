# Plan: das komplette Auge

Erstellt 02.11.2026 von SRE (B-142), rein aus Export und Code, ohne das Spiel anzusehen. Gebaut sind bisher Feldliste, Checkliste, Aufzeichnung und Auswerter; nichts davon lief bisher am echten Spiel.

**Ziel (Daniel):** Das Auge sieht alles, was im Spiel stattfindet, nicht nur eine Liste bestellter Punkte. Kontrolle über eine Checkliste, die sich in wenigen Läufen bestätigen oder widerlegen lässt.

**Läufe (Daniels Aufteilung vom 02.11.2026):**
- **F, friedlich:** Burgenbau, Karte „Prächtige Oase“, keine Gegner, unbegrenzt Zeit.
- **K, Krieg:** Gefecht mit 8 verschiedenen KI-Lords und 5 Minuten Friedenszeit.
- **S, Versuche:** Karte aus den eigenen Szenarien, z. B. „Liga_Grumpy Neighbors“, ungestört: Belagerung gegen alle Gebäude, Reichweiten, Tempo, Reaktionen, Massenschlachten, Angriffe auf einen Punkt.

**Maßstab:** Das Auge ist komplett, wenn sich im Lauf nichts Spielrelevantes ändert, was es nicht kennt, und wenn gleicher Stand plus gleiche Eingänge denselben Verlauf ergeben. Das prüft nicht das Gefühl, sondern die Gesamtproben A1 bis A13 in `data/research/auge_plan/Checkliste_Auge.md`.

## Was gemessen ist

Alle Zahlen erzeugt `python data/research/auge_plan/zustand_ableiten.py` (Ergebnis `zustand_felder.csv`).

| Größe | Wert | Bedeutung |
|---|---|---|
| Vom Spieltakt erreichbare Funktionen | 2.288 von 4.581 | ab `processGameTick`, über Aufrufe und Funktionstabellen |
| Felder, die spielrelevante Funktionen davon schreiben | 2.694 | das ist der bewegliche Spielzustand laut Code |
| Davon nennt `auge.py` beim Namen | 467 | grobe Zählung nach Feldnamen |
| Davon mit unklarem Namen | 824 | Ghidra-Platzhalter wie `field123` oder `...Unk` |
| Im Takt nur gelesen, nie geschrieben | 1.528 | Tabellen und Einstellungen: einmal lesen reicht |
| Datenblock des Spiels | 31,9 MB | feste Adressen, davon 17,1 MB in 15 Hauptstrukturen |

| Bereich | Felder | Nennt das Auge |
|---|---|---|
| Spielerdaten | 433 | 89 |
| Einheiten | 292 | 98 |
| Gleichlauf und Befehle (`GameSynchronyState`) | 250 | 5 |
| Gebäude | 247 | 71 |
| Karte und Zeit (`mapAndTime`) | 222 | 25 |
| KI-Angriffsdaten (`TroopValueState`) | 207 | 36 |
| Kartenebenen (`TileMapState`) | 140 | 17 |
| Geschosse und Effekte | 118 | 54 |
| Trupps | 108 | 32 |
| Wegfindung | 91 | 4 |
| Karteneigenschaften | 79 | 2 |
| Spielkern | 78 | 2 |
| KI-Bauplätze (`AIVState`) | 72 | 2 |
| Bäume, Felsen, Wind (`LandscapeState`) | 59 | 19 |
| Wildtiere | 57 | 0 |

**Grenzen der Zählung:**
- Schreibzugriffe über Zeiger sieht die Ableitung teils nicht. 278 spielrelevante Funktionen sind vom Takt aus nicht erreicht, darunter Aufbau und Eingaben, aber auch `canUnitReachAdjacentTile`. Die Liste kann also Lücken haben; dafür gibt es die Probe A1.
- Die Funktionstabellen können zu viel einschließen (55 Menü-Funktionen sind dabei).
- „Nennt das Auge“ zählt nur Namen. Das Auge liest manche Blöcke ganz, hat die Daten also, ohne sie zu entschlüsseln. Kurze Namen können zufällig treffen.
- 192 Felder haben nur einen Versatz und noch keinen Namen.

## Was das komplette Auge braucht

1. **Feldliste:** vorhanden (`zustand_felder.csv`), wird durch A1 ergänzt.
2. **Vollständiges Lesen:** alle Bereiche aus dem Export erzeugt statt von Hand gepflegt. Kartenebenen und seltene Bereiche nur bei Änderung, falls A4 das verlangt.
3. **Änderungsmelder:** vergleicht den ganzen Datenblock mit der Feldliste. Das ist die Kontrolle, die auch Unbekanntes findet.
4. **Einmalwerte:** die 1.528 nur gelesenen Felder beim Start einmal lesen und ablegen, UCP-Änderungen damit eingeschlossen.
5. **Eingänge und Zufall:** Befehlsliste und `SEC_RNG` jeden Takt. Ohne beides lässt sich kein Verlauf erklären.
6. **Aufzeichnung und Auswertung:** Der Lauf schreibt alles mit, ein Auswerter prüft danach Teil A und die Einzelpunkte. Der Auswerter wird vor dem ersten Lauf an künstlichen Daten mit eingebauten Fehlern getestet.
7. **Bedeutung:** 824 unklare Namen und die 3.340 offenen Punkte aus dem Funktionswissen. Das Auge sieht sie auch ohne Namen; die Läufe liefern die Belege.
8. **Sichtschranke:** Das Auge liest alles, aber SamurAI darf im echten Spiel nur bekommen, was erlaubt ist. Jedes Feld bekommt die Marke „für den Spielentscheid erlaubt“ oder „nur Forschung“ (fremde Lager, Gegner-KI, Zufall). Die Marken sind ein Vorschlag an Daniel.

9. **Versuchsskript für Lauf S:** Aufstellen, Befehl, Messen, Abräumen aus `versuche_szenario.csv`. `setze` und `sandkasten` gibt es schon im alten Werkzeug `werkzeug/shc.py`.
10. **Gefecht mit Friedenszeit:** Das Werkzeug `gefecht` kennt bisher keine Friedenszeit und muss 8 KI-Lords ohne eigenen Spieler starten können. Ob das geht, ist noch nicht nachgesehen, außer dass es einen Selbstspiel-Weg gab.

**Stand Baustein 6 (02.11.2026):**
- `selfaware.tools.experiments.auge_aufzeichnung` zeichnet auf, nur lesend, und lehnt Instanz 5 ab.
- `selfaware.tools.analysis.auge_auswertung` wertet A1 bis A7, A9, A10, A12 und A13 aus.
- `selfaware.tools.analysis.auge_feldkarte` ordnet Adressen den Feldern zu.
- `tests/test_auge_werkzeug.py` prüft sie an einem künstlichen Spiel mit eingebauten Fehlern.
- Noch nicht gebaut: A8 (Buchführung), A11 (Prüfsummen), die Auswertung der Einzelpunkte und Versuche.

Damit sind auch 2, 3, 4 und 5 in der ersten Fassung abgedeckt: Die Aufzeichnung liest die Hauptstrukturen jeden Takt, Kartenebenen alle 25 Takte und den ganzen Datenblock alle 250 Takte. Ob das Tempo das trägt, zeigt erst A4.

**Stand Lauf F (02.11.2026):** `selfaware.tools.experiments.auge_lauf_f` startet ohne Maus den Burgenbau auf `A Mighty Oasis.map`, nimmt auf und fährt das Programm. Die Trockenprobe ist grün, gelaufen ist es noch nicht. Ansage: `data/research/auge_plan/Ansage_Lauf_F.md`.

**Reihenfolge:** 1 und 6 sind fertig. Dann Lauf F, Fehler beheben, 10, Lauf K, Fehler beheben, 9, Lauf S. 7 läuft dabei mit, 8 kommt vor der Übergabe an das Gehirn.

## Was vorher zu klären ist

- **Wo das Auge lebt:** `werkzeug/auge.py`, `werkzeug/shc.py` und `werkzeug/sandkasten.py` stehen nicht auf `origin/main`, sondern nur im alten lokalen Stand, `auge.py` in neuester Fassung auf dem Zweig `codex/auge`. Dort arbeitet auch Codex, mit nicht committeten Änderungen. Das neue Auge sollte erst darauf aufbauen, wenn das geklärt ist.
- **Spielart:** Burgenbau und Szenario laufen vermutlich nach anderen Regeln als das Gefecht, in dem SamurAI spielt. Betroffene Punkte tragen die Marke [Spielart] und zählen erst nach der Gegenprobe im Gefecht.
- **Karten:** „Eine prächtige Oase“ ist `maps/A Mighty Oasis.map`, belegt nur per Ausschluss über die Namensliste in `cr.tex`. „Liga_Grumpy Neighbors“ liegt nicht unter diesem Namen in `Documents\Stronghold Crusader\Maps`; der Dateiort wird vor Lauf K gesucht.
- **Jeder Lauf** braucht Daniels Ja und eine freie Instanz.

## Was das danach ermöglicht

Bestehen A5 und A6, ist belegt, dass Stand und Eingänge den Verlauf festlegen. Erst dann lohnt ein Rechner, der den Verlauf wirklich vorausberechnet. Das ist ein eigener Schritt, das Auge liefert ihm die Grundlage und den Maßstab.
