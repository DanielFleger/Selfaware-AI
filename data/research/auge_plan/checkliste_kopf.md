# Checkliste Auge: was zwei Läufe bestätigen oder widerlegen

Erstellt 02.11.2026 von SRE (B-142), rein aus dem Code, ohne das Spiel anzusehen. Gebaut mit `python data/research/auge_plan/checkliste_bauen.py`.
Kein Punkt ist bisher im Spiel geprüft. Jeder Lauf braucht vorher Daniels Ja.

**So wird gelesen:** Stimmt die Messung nicht mit „Erwartet“ überein, ist die Aussage widerlegt und wird im Funktionswissen berichtigt. Kam die Lage im Lauf nicht vor, heißt der Punkt „nicht gesehen“, das ist weder bestätigt noch widerlegt.

**Rahmen für beide Läufe:** freie Instanz, nie Instanz 5. Start nur über das vorhandene Werkzeug, ohne Maus. Der Lauf wird komplett aufgezeichnet, ausgewertet wird danach aus der Aufzeichnung. Nach Lauf 1 werden Fehler behoben, dann erst Lauf 2. Im Sandkasten darf gesetzt werden (z. B. Gold oder volles Lager), im echten Spielentscheid nie.

## Teil A: Ist das Auge vollständig? Zwölf Gesamtproben

Diese Proben zählen mehr als alle Einzelpunkte, weil sie auch finden, wonach niemand gesucht hat.

| Nr | Probe | Erwartet aus dem Code | Widerlegt, wenn | Lauf |
|---|---|---|---|---|
| A1 | **Änderungsmelder:** den ganzen Datenblock `0x005B6000` bis `0x0242923F` in festen Abständen sichern und vergleichen | Jedes geänderte Byte eines Spielbereichs liegt in einem Feld aus `zustand_felder.csv` | Ein Byte ändert sich außerhalb der Liste: Die Liste hat eine Lücke, das Feld kommt dazu | 1 und 2 |
| A2 | **Nie gesehen:** Felder der Liste, die sich in beiden Läufen nie ändern | Bleibt als Restliste stehen | Nicht widerlegbar; zeigt, welche Lage noch fehlt | 1 und 2 |
| A3 | **Takt-Treue:** Taktnummer vor und nach jedem Lesen | Kein ausgelassener Takt, jeder Schnappschuss liegt innerhalb eines Takts | Ein Takt fehlt oder ein Schnappschuss ist gemischt | 1 und 2 |
| A4 | **Lesedauer:** Zeit für einen vollen Schnappschuss, Spieltempo mit und ohne Lesen, gleich zu Beginn | Wird gemessen; bekannt sind nur 31,9 MB Datenblock, davon 17,1 MB in den 15 Hauptstrukturen | Das Lesen bremst das Spiel: Dann werden Bereiche seltener oder nur bei Änderung gelesen | 1 |
| A5 | **Laden gleich Sichern:** Spielstand bei Takt T speichern, in Lauf 2 laden, alle Felder vergleichen | Spielbereiche sind gleich | Ein Feld weicht ab: Es wird nicht gespeichert, also aus anderem berechnet oder nur flüchtig | Ende 1, Start 2 |
| A6 | **Gleicher Stand, gleicher Verlauf:** nach T in beiden Läufen 2.000 Takte keine eigenen Befehle, Takt für Takt vergleichen | Vermutung: alles gleich, das Spiel rechnet festgelegt | Erste Abweichung nennt den fehlenden Eingang (z. B. Uhrzeit), oder das Spiel rechnet nicht festgelegt | 2 |
| A7 | **Zufall:** `SEC_RNG` lesen, die nächste Zahl aus der Tabelle vorhersagen | Zwei Zeiger mit Umlauf bei 20.000 (`nextRandomNumber1`, `nextRandomNumber2`) | Die gezogene Zahl weicht von der Vorhersage ab | 1 |
| A8 | **Buchführung Gold und Waren:** jede Bestandsänderung einer Ursache zuordnen (Befehl, Arbeiter, Steuer, Handel) | Keine Änderung ohne Ursache | Rest ohne Ursache: Ein Weg fehlt im Wissen | 1 |
| A9 | **Eingänge:** Befehlsliste (Ring mit 200 Plätzen) jeden Takt mitschreiben | Jeder eigene Befehl erscheint genau einmal und wirkt | Befehl verloren, doppelt, oder eine Wirkung ohne Befehl | 1 und 2 |
| A10 | **Lebenslauf:** je Einheit, Geschoss und Gebäude Anfang und Ende über die `uid` verfolgen | Keine Lücke, Grenzen wie berichtigt: Geschossplätze unter 25 mit `uid` 0, Gruppen 1 bis 1249, Monat 0 bis 11 | Ein Platz oder Wert liegt außerhalb | 1 und 2 |
| A11 | **Prüfsummen des Spiels:** `HASH_HashTotal` lesen und mit `computeHash` über dieselben Bereiche nachrechnen | Offen, ob sie im Einzelspiel überhaupt laufen; dann sind sie gleich | Summe weicht ab: Bereich falsch verstanden. Bleibt sie 0, entfällt die Probe | 1 |
| A12 | **Flüchtige Werte:** Merker wie `DAT_CurrentUnitSlotID` und `DAT_UnitHasBecomeIdle` am Taktende ansehen | Ändern sich innerhalb des Takts, am Taktende ohne Aussage | Ein solcher Wert trägt doch Zustand über den Takt: Er kommt in die Pflichtliste | 1 und 2 |

## Teil B: Ablauf

Jeder Lauf wird vorher angesagt: Ziel, erhofftes Ergebnis, Abbruch.

**Lauf 1: alles Friedliche, und der Spielstand für Lauf 2**
- Ziel: A1 bis A5, A7 bis A12 und alle Punkte „Lauf 1“.
- Ablauf: Gefecht gegen eine KI auf derselben Karte starten, einmal alle Tabellen lesen, dann Lager, Kornspeicher, Waffenkammer, alle Betriebe, Bauernhöfe, Waffenbau und Kaserne bauen. Handeln, auch bei vollem Lager. Steuern und Rationen ändern. Mauer, Tor und Graben bauen, abreißen, anwerben. Über einen Jahreswechsel laufen lassen. Am Ende bei Takt T speichern und 2.000 Takte ohne eigene Befehle weiterlaufen lassen.
- Abbruch: Fehlen Takte (A3), bremst das Lesen (A4) oder entsteht kein Spielstand, wird sofort beendet, die Ursache behoben und neu gestartet.

**Lauf 2: alles Kriegerische**
- Ziel: A5, A6 und alle Punkte „Lauf 2“.
- Ablauf: Spielstand laden, vergleichen, wieder 2.000 Takte ohne eigene Befehle. Danach eigene Armee aus allen Einheitenarten gegen die KI-Wellen, Belagerung, Feuer, Pech, Fallen, Hunde, bis ein Lord fällt.
- Abbruch: Weicht schon A5 stark ab, wird nicht weitergespielt, sondern zuerst geklärt, warum.

## Teil C: Einzelpunkte

{{GESAMT}} Punkte aus dem Funktionswissen: {{S}} zum einmaligen Auslesen, {{L1}} in Lauf 1, {{L2}} in Lauf 2, {{H}} nur mit Aufruf-Haken, {{N}} außerhalb dieser Läufe. {{OHNE}} davon haben noch keine klare Erwartung und müssen vor dem Lauf geschärft werden.
Die Zuteilung geht nach Art und Stichworten des Punkts, sie ist ein Vorschlag. 1.536 der 1.912 Erklärungen haben gar keinen Einzelpunkt, für sie gelten nur die Gesamtproben aus Teil A. In einem Lauf kommen nicht alle Lagen von selbst vor, was fehlt, wird im Sandkasten nachgestellt oder bleibt „nicht gesehen“.
