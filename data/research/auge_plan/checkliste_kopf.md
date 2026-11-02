# Checkliste Auge: was die Läufe bestätigen oder widerlegen

Erstellt 02.11.2026 von SRE (B-142), rein aus dem Code, ohne das Spiel anzusehen. Aufteilung der Läufe nach Daniels Vorschlag vom 02.11.2026. Gebaut mit `python data/research/auge_plan/checkliste_bauen.py`.
Kein Punkt ist bisher im Spiel geprüft. Jeder Lauf braucht vorher Daniels Ja.

**So wird gelesen:** Stimmt die Messung nicht mit „Erwartet“ überein, ist die Aussage widerlegt und wird im Funktionswissen berichtigt. Kam die Lage im Lauf nicht vor, heißt der Punkt „nicht gesehen“, das ist weder bestätigt noch widerlegt.

**Rahmen für alle Läufe:** freie Instanz, nie Instanz 5. Start nur über das Werkzeug, ohne Maus. Jeder Lauf wird komplett aufgezeichnet, ausgewertet wird danach aus der Aufzeichnung. Nach jedem Lauf werden Fehler behoben, dann erst der nächste. Im Sandkasten darf gesetzt werden, im echten Spielentscheid nie.

## Die drei Läufe

| Lauf | Wo | Wofür |
|---|---|---|
| **F, friedlich** | Burgenbau, Karte „Prächtige Oase“ | Wirtschaft, Bauen, Markt, Anwerben, alle Tabellen. Keine Gegner, unbegrenzt Zeit |
| **K, Krieg** | Gefecht, 8 verschiedene KI-Lords, 5 Minuten Friedenszeit | Was die KI selbst tut: Aufbau, Wellen, Belagerung, Lord-Tod. Dazu die Probe, ob das Spiel festgelegt rechnet |
| **S, Versuche** | Eigene Szenarien, z. B. „Liga_Grumpy Neighbors“ | Gezielte, ungestörte Versuche: Einheiten-Steckbrief, Belagerung gegen alle Gebäude, Duelle, Massenschlachten, Angriffe auf einen Punkt |

**Wichtig, aus dem Code:** Die Spielart ändert Regeln. In `MenuItemActionHandler_MainMenu_Main` und `MenuItemActionHandler_CustomScenarios_Main` wird `GM_BUILDERUnk` gesetzt, im Gefecht `GM_SKIRMISH_AND_MULTIPLAYER`. Dazu kommt `currentGameMode` (0 `GM_SOLITARY`, 99 `GM_SKIRMISH_SINGLE_PLAYER`). Beispiel `UpdateAppleFarmer`: Die Ladung ist in `GM_SOLITARY` mindestens 3, sonst mindestens 4. Burgenbau und Szenario laufen also vermutlich nach anderen Regeln als das Gefecht, in dem SamurAI spielt. Deshalb Probe A13 und die Marke **[Spielart]** an den {{SPIELART}} betroffenen Punkten: Sie zählen erst als bestätigt, wenn sie auch im Gefecht stimmen.

## Teil A: Ist das Auge vollständig? Dreizehn Gesamtproben

Diese Proben zählen mehr als alle Einzelpunkte, weil sie auch finden, wonach niemand gesucht hat.

| Nr | Probe | Erwartet aus dem Code | Widerlegt, wenn | Lauf |
|---|---|---|---|---|
| A1 | **Änderungsmelder:** den ganzen Datenblock `0x005B6000` bis `0x0242923F` in festen Abständen sichern und vergleichen | Jedes geänderte Byte eines Spielbereichs liegt in einem Feld aus `zustand_felder.csv` | Ein Byte ändert sich außerhalb der Liste: Die Liste hat eine Lücke, das Feld kommt dazu | F, K, S |
| A2 | **Nie gesehen:** Felder der Liste, die sich in allen Läufen nie ändern | Bleibt als Restliste stehen | Nicht widerlegbar; zeigt, welche Lage noch fehlt | F, K, S |
| A3 | **Takt-Treue:** Taktnummer vor und nach jedem Lesen | Kein ausgelassener Takt, jeder Schnappschuss liegt innerhalb eines Takts | Ein Takt fehlt oder ein Schnappschuss ist gemischt | F, K, S |
| A4 | **Lesedauer:** Zeit für einen vollen Schnappschuss, Spieltempo mit und ohne Lesen, einmal leer und einmal in der größten Massenschlacht | Wird gemessen; bekannt sind nur 31,9 MB Datenblock, davon 17,1 MB in den 15 Hauptstrukturen | Das Lesen bremst das Spiel: Dann werden Bereiche seltener oder nur bei Änderung gelesen | F, S |
| A5 | **Laden gleich Sichern:** bei Takt T nach der Friedenszeit speichern, wieder laden, alle Felder vergleichen | Spielbereiche sind gleich | Ein Feld weicht ab: Es wird nicht gespeichert, also aus anderem berechnet oder nur flüchtig | K |
| A6 | **Gleicher Stand, gleicher Verlauf:** nach T 2.000 Takte ohne eigene Befehle, dann denselben Stand laden und dieselben 2.000 Takte wiederholen | Vermutung: alles gleich, das Spiel rechnet festgelegt | Erste Abweichung nennt den fehlenden Eingang (z. B. Uhrzeit), oder das Spiel rechnet nicht festgelegt | K |
| A7 | **Zufall:** `SEC_RNG` lesen, die nächste Zahl aus der Tabelle vorhersagen | Zwei Zeiger mit Umlauf bei 20.000 (`nextRandomNumber1`, `nextRandomNumber2`) | Die gezogene Zahl weicht von der Vorhersage ab | F |
| A8 | **Buchführung Gold und Waren:** jede Bestandsänderung einer Ursache zuordnen (Befehl, Arbeiter, Steuer, Handel) | Keine Änderung ohne Ursache | Rest ohne Ursache: Ein Weg fehlt im Wissen | F |
| A9 | **Eingänge:** Befehlsliste (Ring mit 200 Plätzen) jeden Takt mitschreiben | Jeder eigene Befehl erscheint genau einmal und wirkt | Befehl verloren, doppelt, oder eine Wirkung ohne Befehl | F, K, S |
| A10 | **Lebenslauf:** je Einheit, Geschoss und Gebäude Anfang und Ende über die `uid` verfolgen | Keine Lücke, Grenzen wie berichtigt: Geschossplätze unter 25 mit `uid` 0, Gruppen 1 bis 1249, Monat 0 bis 11 | Ein Platz oder Wert liegt außerhalb | F, K, S |
| A11 | **Prüfsummen des Spiels:** `HASH_HashTotal` lesen und mit `computeHash` über dieselben Bereiche nachrechnen | Offen, ob sie außerhalb des Mehrspielers überhaupt laufen; dann sind sie gleich | Summe weicht ab: Bereich falsch verstanden. Bleibt sie 0, entfällt die Probe | K |
| A12 | **Flüchtige Werte:** Merker wie `DAT_CurrentUnitSlotID` und `DAT_UnitHasBecomeIdle` am Taktende ansehen | Ändern sich innerhalb des Takts, am Taktende ohne Aussage | Ein solcher Wert trägt doch Zustand über den Takt: Er kommt in die Pflichtliste | F, K, S |
| A13 | **Spielart:** `currentGameMode` und `gameMode_2` zu Beginn jedes Laufs lesen; die Punkte mit Marke **[Spielart]** zwischen den Läufen vergleichen | Vermutung: F und S gleich, K anders | Eine Regel gilt anders als im Spielart-Zweig des Codes beschrieben | F, K, S |

## Teil B: Ablauf

Jeder Lauf wird vorher angesagt: Ziel, erhofftes Ergebnis, Abbruch.

**Lauf F: Burgenbau, keine Gegner, unbegrenzt Zeit**
- Ziel: A1 bis A4, A7 bis A10, A12, A13 und alle Punkte „Lauf F“.
- Ablauf: Spielart lesen, alle Tabellen einmal lesen. Dann jedes Gebäude einmal bauen und besetzen, jede Warenkette bis ins Lager laufen lassen. Handeln, auch bei vollem Lager. Steuern, Rationen, Bier, Religion und Furchtfaktor durchschalten. Mauern, Tore und Gräben bauen und abreißen, jede Einheit einmal anwerben. Über mehrere Jahreswechsel laufen lassen. Was im Burgenbau gesperrt ist, wird notiert und in K beobachtet.
- Abbruch: Fehlen Takte (A3) oder bremst das Lesen (A4), wird sofort beendet und die Ursache behoben.

**Lauf K: Gefecht mit 8 KI-Lords, 5 Minuten Friedenszeit**
- Ziel: A1 bis A3, A5, A6, A9 bis A13 und alle Punkte „Lauf K“. Zugleich die Gegenprobe für alle Punkte mit Marke **[Spielart]**, soweit die KI sie auslöst.
- Ablauf: 8 möglichst verschiedene aus den 16 KI-Lords, alle von der KI gesteuert, damit kein eigener Befehl dazwischenkommt. Die Friedenszeit vergleicht Aufbau und Einhaltung. Nach ihrem Ende bei Takt T speichern, 2.000 Takte laufen lassen, Stand laden, Vergleich A5, dieselben 2.000 Takte wiederholen, Vergleich A6. Danach bis zum letzten Lord weiterlaufen. Die übrigen 8 KI-Lords sind nur über ihre Tabellen erfasst.
- Abbruch: Weicht A5 stark ab, wird nicht weitergespielt, sondern zuerst geklärt, warum.

**Lauf S: Versuche im Szenario, ungestört**
- Ziel: A1 bis A4, A9, A10, A12, A13, alle Punkte „Lauf S“ und die Versuche aus Teil C.
- Ablauf: Karte laden, Sandkasten leeren, Versuche der Reihe nach per Skript: aufstellen, einen Befehl geben, messen, abräumen. Mit Massenschlachten erst am Ende, weil sie A4 unter Last prüfen.
- Abbruch: Stimmt schon der Steckbrief nicht mit den Tabellen überein, werden die teureren Versuche erst danach gefahren.

## Teil C: Versuche im Szenario

{{VERSUCHE}} Versuche, einzeln in `versuche_szenario.csv`. Erwartet wird jeweils der Wert aus der genannten Spieltabelle, die beim Laufstart gelesen wird, damit UCP-Änderungen mitzählen. Widerlegt ist der Versuch, wenn Messung und Tabelle nicht zusammenpassen.

{{VERSUCHSTABELLE}}

**Noch nicht aus dem Code belegt:** Der Schaden gegen Gebäude (V4) läuft über `processDamageToBuilding` und `processEntityDamageToBuildingCollateral`, die Tabelle je Waffe und Gebäude ist noch nicht herausgelesen. Dort wird im ersten Durchgang gemessen und die Regel danach aufgeschrieben. Das ist Beobachtung, keine Bestätigung.

## Teil D: Einzelpunkte

{{GESAMT}} Punkte aus dem Funktionswissen: {{F0}} zum einmaligen Auslesen, {{F}} in Lauf F, {{K}} in Lauf K, {{S}} in Lauf S, {{H}} nur mit Aufruf-Haken, {{N}} außerhalb dieser Läufe. {{OHNE}} davon haben noch keine klare Erwartung und müssen vor dem Lauf geschärft werden.
Die Zuteilung geht nach Art und Stichworten des Punkts, sie ist ein Vorschlag. 1.536 der 1.912 Erklärungen haben gar keinen Einzelpunkt, für sie gelten nur die Gesamtproben aus Teil A. In einem Lauf kommen nicht alle Lagen von selbst vor, was fehlt, wird im Szenario nachgestellt oder bleibt „nicht gesehen“.
