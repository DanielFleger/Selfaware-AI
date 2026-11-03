# Plan: Lauf S (B-142)

Erstellt 03.11.2026 von SRE nach Daniels "Ja, Lauf S planen". **Noch nichts gebaut, nichts gestartet.** Grundlage: `data/research/auge_plan/Checkliste_Auge.md` (Teil B, C, D), `versuche_szenario.csv`, die Lehren aus Lauf F und K. Jede Zahl hier hat ihren Befehl in `data/research/auge_plan/lauf_s_plan/`, oben in jedem Skript.

## Frage des Laufs

Rechnet das Spiel im Kampf wirklich das, was in seinen Tabellen steht: Leben, Tempo, Reichweite, Schaden, Reaktion, jede Einheit gegen jede Einheit und jedes Gebäude, ohne dass etwas stört? Und sieht das Auge das alles, auch in der größten Schlacht, ohne das Spiel zu bremsen?

## Ansage

| | |
|---|---|
| **Was wird getestet** | Das Auge und die Kampfregeln des Spiels. Nicht SamurAI |
| **Erhofft** | Leben, Schaden und Besatzung passen zu den Tabellen im Speicher. Das Auge verliert auf Tempo 40 keinen Takt, die Treppe bis 1000 zeigt auch mit 2.400 Einheiten keinen Abzug durchs Lesen. Der Schaden ist im Editor und im Gefecht gleich |
| **Was es widerlegt** | Eine Messung passt nicht zur Tabelle, ein Takt fehlt, mit Lesen weniger Takte als ohne, die Stichprobe im Gefecht weicht vom Editor ab. Jede Vorhersage steht einzeln unten, vor dem Lauf |
| **Wie** | Instanz 2. Editor auf `Liga_Grumpy Neighbors`: aufstellen, einen Befehl geben, messen, abräumen, in Durchgängen mit bis zu 10 Versuchen gleichzeitig. Massenschlachten zuletzt. Dann Gegenprobe im Gefecht. Instanz 5 bleibt unberührt |
| **Wie lange** | Obergrenze 86 Minuten ohne Setzen und Laden (`rechnung_dauer.txt`). Ein Durchgang endet, sobald seine Zellen fertig sind, also wird es weniger. Wie viel weniger, misst die Probe, die Zahl bekommst du vor dem Start |
| **Nutzen fürs Ziel** | Danach ist das Auge in allen drei Lagen geprüft: Frieden (F), KI im Kampf (K), jede Kampflage einzeln (S) |
| **Nutzen fürs 3-Jahres-Ziel** | SamurAI soll selbst lernen, mit Werten aus dem Spiel statt aus Annahmen. Dieser Lauf liefert die Grundwerte, gegen die das Gehirn seine Vorhersagen prüft |

## Karte und Spielart

**Hauptbank E: `Liga_Grumpy Neighbors` im Karteneditor** (Daniel 02.11.: "eine karte laden aus eigenen szenarien ... grumpy neighbors weil dort eben alles möglich ist"). Weg laut Code: Eigene Szenarien, `CustomScenarios_Main` Knopf 1 öffnet die Kartenliste (`activateLoadOrSaveMapUI`, 0x00440770). Das Laden von dort setzt `gameMode_2 = GM_EDITOR` (0x004950B0). Knopf 4 wäre "Szenario spielen" mit `gameMode_2` 2, also nicht der Editor. Keine KI, keine Arbeiter.

Gemessen aus der Kartendatei (`karte_flaeche.txt`): Typ 1, 4 Spieler, 57.247 von 80.400 Feldern eben und frei, sechs ganz ebene Flächen von 40 x 40. **Die Karte bringt 36 Gebäude und 136 Einheiten mit**, die werden zuerst abgeräumt und das Abräumen geprüft. Die Fläche reicht für den Plan, und die Karte hat Hügel für P330 (Höhe bis 130, Median 8). Kein Grund, von deiner Wahl abzuweichen.

**Gegenbank G: dieselbe Karte als Gefecht** (`currentGameMode` 99, `gameMode_2` 3), Spieler 1 und eine KI ohne Waren. Dort spielt SamurAI, also müssen die Werte dort gelten.

**Bank K: geladener Stand `AugeK 000735 T70029` aus Lauf K.** Nur für die Punkte, die eine laufende KI brauchen. Dort schießt ein Katapult schon (Lauf K, Fenster t9). Ob die KI dort noch baut, liest die Probe.

### Was der Code über Editor und Gefecht sagt

Darum reicht der Editor allein nicht. Beleg: `spielart_im_code.txt`, Export der Datei, im Speicher kann UCP es ändern.

| Stelle | Regel | Folge |
|---|---|---|
| `processUnitAttackOtherUnit`, `processEntityDamageToUnit`, `processDamageToBuilding` | Sie fragen die Spielart nur für Töne ab | **Vorhersage:** Schaden im Editor gleich Gefecht. Die Stichprobe in G prüft das |
| `UpdateMaceman` Zeile 405 bis 410 | Im Einzelspiel geht der Keulenträger, solange kein Feind näher als 0xC0 Mikropunkte (24 Felder) ist, sonst rennt er. UCP hat diese Stelle mit einem Sprung umgebaut (0x560B4F) | Gehtempo in beiden Banken |
| `processMeleeInitiation` Zeile 50 bis 57 | Sonderweg für Einheiten mit `unknownTestAgainst0_1` ungleich 0: nur alle 16 Takte, nur im Gefecht oder ab 101 Einheiten. Was das Feld genau ist, ist offen | Reaktion in beiden Banken |
| `spawnUnit` Zeile 71 bis 108 | Katapult und Trebuchet: 40 Steine im Einzelspiel auf Plätzen ohne Menschen, 20 im Gefecht, sonst 20. UCP macht aus dieser letzten Zahl 10 (0x53E5E5). Im Editor zählt jeder Platz außer dem eigenen als ohne Menschen (0x004950B0) | Munition lesen, nie annehmen. P216 in E und G |
| `processDamageFromKillingPit` Zeile 18 bis 24 | Im Editor löst die Mordgrube nur aus, wenn Grube oder Einheit dem eigenen Platz gehört | So aufstellen (V7.004) |
| `giveTribeAnInstruction` Zeile 481 | Im Gefecht fallen Mauerbefehle weg, wenn "starke Mauern" an ist (`strongWalls2`) | In G den Schalter lesen |
| `UpdateLord` (12 Stellen), `UpdateOutpostBuilding` Zeile 54 | Lord-Tod und Außenposten laufen im Editor anders oder gar nicht | Nur in G oder K |
| `MenuView_CustomScenarios_Prepare` Zeile 25 bis 30 | Setzt `gameMode_2`, aber nicht `currentGameMode` | `currentGameMode` hängt daran, was vorher lief. E startet nach frischem Spielstart und liest ihn (A13) |

**A13 in der Checkliste ("F und S gleich") passt so nicht mehr:** F lief mit `gameMode_2` 2, E läuft mit 1. Das Ergebnis schreibe ich als Berichtigung auf.

## Aufbau: Zellen

Warum nicht einer nach dem anderen: Jeder Versuch hieße einmal abräumen. Die Karte hat Platz für mehrere ungestörte Versuche gleichzeitig.

| Zellen | Kern | Abstand zwischen zwei Kernen | Für | Grund des Abstands |
|---|---|---|---|---|
| 11 | 12 x 12 | mindestens 60 Felder | V1, V2, V3 Fußschützen, V4b | Bogen trifft aus 35 Feldern, aus 45 nicht (L82); Tabelle Pfeil 54 |
| 5 | 24 x 24 | mindestens 80 Felder | V3 Geräte, V4 | Größter Tabellenwert aller Geschosse: 75 (`tabellen.txt`) |
| 1 | ganze Karte | | V5, V6, V7 | Schlachten und Märsche brauchen die Fläche |

Gezählt aus der Karte: `karte_zellen.json`. Eben heißt: Höhenspanne im Kern höchstens 4, sonst misst das Gehtempo den Hang mit.

**Je Durchgang ist eine Zelle die Kontrolle:** eine Einheit allein, ohne Befehl. Verliert sie Leben oder läuft sie los, stört etwas, das ich nicht kenne. Darum 10 und 4 Versuche je Durchgang, nicht 11 und 5.

**Aufgestellt wird im angehaltenen Spiel,** damit alle Zellen im selben Takt anfangen und die erste Lesung den Anfang sieht.

**Ob wirklich nichts stört, wird nachgerechnet, nicht angenommen.** Jeder Versuch gilt erst als ungestört, wenn seine Einheiten in der Zelle blieben, jeder Treffer einem Schützen oder Schläger derselben Zelle zugeordnet ist und kein Leben ohne Täter fiel. Sonst heißt er "gestört" und wird einmal allein wiederholt. Bleibt er gestört, steht das so in der Liste.

**Nach jedem Durchgang wird die Zelle geprüft:** keine Einheit, kein Gebäude, Logik und Höhe wie vorher. Ist sie es nicht, wird sie gesperrt. Bleibt weniger als die Hälfte der Zellen, wird die Karte neu geladen.

## Warum welches Tempo

Daniels Frage vom 02.11. "warum nicht gleich 1000?": Es gilt immer die höchste Stufe, bei der die Messung noch stimmt.

| Messung | Tempo | Warum |
|---|---|---|
| Nahkampf, Reaktion, Flugzeit, Zähler je Takt | 40, jeder Takt gelesen | Nahkampf trifft jeden Takt: 567 von 705 Abständen zwischen zwei Lebensverlusten sind genau 1 Takt (`kampf_takt_t9.txt`). 40 ist die höchste Stufe, die jeden Takt liest (Lauf F) |
| Gehtempo, Marsch | 200 | Ein Feld dauert mindestens rund 11 Takte (L80). Gerechnet aus Lauf K: Eine Lesung dauert rund 9 ms, das sind rund 2 Takte |
| Belagerung | 1000 | Katapult alle 123 Takte (`kampf_takt_t9.txt`). Auf 1000 liest das Auge rund jeden 7. Takt (Lauf K: 19.193 Lesungen in 133.512 Takten). Das reicht, wenn nur Lebensstufen zählen |
| Massenschlacht | 1000 und die Treppe | Deine Vorgabe: 1 bis 1000 ohne Abzug |

Alles in Takten. Die Uhr zählt nur dort, wo kein Takt läuft: Spiel hängt, Laden.

## Abschnitte

Grenze heißt: So lange höchstens, ein Durchgang endet früher, wenn alle Zellen fertig sind. Dazu kommen je Durchgang höchstens 400 Takte Abräumen. Das ist noch nicht gemessen, nur die Wartezeit des alten Werkzeugs `shc.py`; die Probe misst es.

| # | Abschnitt | Tempo | Versuche, je Durchgang | Grenze je Durchgang | Grund der Grenze |
|---|---|---|---|---|---|
| 0 | Frisch starten, Spielart lesen, alle Tabellen lesen, Karte laden, abräumen | | | | Tabellen beim Laufstart, damit UCP zählt (Checkliste). Die Zahlen hier aus Lauf K dienen nur der Planung |
| 1 | A4 auf der leeren Karte | Treppe | | 219 s | Stufen und Takte wie Lauf F. Lauf F hat das leere Spiel nicht gemessen |
| 2 | **V1 Reaktion**, je Art 3 Mal | 40 | 81, 10 | 406 Takte | Größte Prüfrunde 256 (Maske 255, L78), dazu 10 Felder Anmarsch. 3 Mal, weil die Runde vom Takt abhängt |
| 3 | **V1 Gehtempo und Reichweite**: Befehl auf ein Ziel 60 Felder entfernt | 200 | 27, 10 | 4.320 Takte | 30 Felder eben. Tempo-Wert 6 (Katapult), je Stufe rund 12 Takte je Feld (L80), das mal 2. **Annahme**, Katapult ist nicht gemessen. Trebuchet und Geräte, die nicht laufen: je 6 Abstände |
| | **Tor:** Leben und Besatzung gegen Tabelle, Reaktion gegen Prüfrunde | | | | Stimmt der Steckbrief nicht, hält der Lauf hier an (Checkliste). Erst erklären, dann weiter |
| 4 | **V2 Duelle**: beide bekommen den Befehl, Abstand 1 Feld, je Seite 16 Treffer oder ein Tod | 40 | 190, 10 | 502 Takte | Ein Duell füllt zwei Zeilen, also 190 statt 361. 16 Treffer, weil der längste bekannte Rhythmus im Nahkampf 16 Takte ist. Grenze: 2 x größter erster Treffer vom 18.10. (251, `alte_schuesse.txt`) |
| 5 | **V3 Beschuss**, Abstand 8, 3 Treffer | 40 | 114, 10 und 57, 4 | 867 Takte, nach V1 neu | 8 Felder, weil der Feuerwerfer nur bis 10 entdeckt und der Schaden von 4 bis 20 Feldern gleich ist (Handbuch 17.10.). Treffer 1 Schaden, 2 Schusstakt, 3 Gegenprobe. Grenze: erster Treffer 411 plus 2 x 228 (Armbrust, langsamster gemessener Schütze). Stehendes Ziel: 0 Lücken in 370 Schussabständen (`alte_schuesse.txt`) |
| 6 | **V3 laufendes Ziel** je Schütze, 10 Schuss | 40 | 9, 4 | 2.463 Takte | Noch nie gemessen (Handbuch: "noch zu messen"), wichtig fürs Ausweichen |
| 7 | **V4b Fußtruppen** gegen Tore, Türme, Mauern | 40 | 80, 10 | 502 Takte | Wie V2 |
| 8 | **V4 Belagerung**, echt bemannt, bis zerstört oder Munition leer | 1000 | 492, 4 | 4.920 Takte, nach V1 neu | Höchstens 40 Steine x 123 Takte. Das ist das Katapult; das Trebuchet ist nicht gemessen, V1 misst es. Mehr Steine als Munition (Turm 5: 201): Rest gerechnet und so gekennzeichnet |
| 9 | **V6 Angriff auf einen Punkt**, 60 Felder Marsch | 200 | 8, 1 | 5.000 Takte | Langsamster Fußsoldat (Tempo-Wert 3, rund 36 Takte je Feld), mal 2 für den Stau. **Annahme**, die Probe misst den Stau nicht, V6 selbst schon |
| 10 | **V7 Sonderfälle** und die Punkte dazu | 40 | 11, 1 | 3.000 Takte | Längster aus dem Code bekannter Ablauf 808 Takte (Giftwolke, P297), dazu Anmarsch. **Annahme** für den Brand |
| 11 | **V5 Massenschlachten** von klein nach groß | 1000 | 8, 1 | 30.000 Takte | Längste Tötung laut Tabelle unter den Hauptkämpfern 3.200 Takte (Speer gegen Pike), mit Sklaven 8.000 (Sklave gegen Pike), bei 1.000 gegen 1.000 mehrere Runden. Kein Ende ist ein Ergebnis, kein Scheitern |
| 12 | **A4 in der größten Schlacht**, 1.200 gegen 1.200 | Treppe | | 219 s | Die Schlacht darf während der Treppe nicht ausbrennen: Die Art mit der längsten Kampfdauer aus V2 nehmen, Einheitenzahl je Stufe mitschreiben. Unter 2.000 Einheiten heißt die Stufe "nicht unter Last" und wird nach neuem Aufstellen wiederholt |
| 13 | **G Gefecht:** Friedenszeit Stufe 1, P331. Dann V1 ganz, je Art gegen Schwertkämpfer (19), je Schütze gegen Speer (9), je Gerät gegen Hütte (6), je Fußtruppe gegen Steinmauer (10), die G-Punkte. Lord-Tod zuletzt, er beendet das Spiel | wie oben | | wie oben | **Weicht die Stichprobe ab, gelten die Editor-Werte dieser Gruppe nicht fürs Gefecht:** Die Gruppe wird in G neu gefahren, bevor der Lauf als gültig zählt |
| 14 | **K:** Stand laden, Punkte der laufenden KI | 1000 | | 30.000 Takte | Bis nach dem übernächsten Lord-Fall in Lauf K (88.069 minus 70.029 = 18.040 Takte). Das Laden ändert den Stand (K1), also kein Takt-Vergleich mit Lauf K |

## Vorher festgelegt: was als widerlegt gilt

Quelle der Sollwerte ist immer die Tabelle, die der Lauf beim Start liest. Die Zahlen hier stammen aus Lauf K (`tabellen.txt`).

| # | Vorhersage | Woher | Widerlegt, wenn |
|---|---|---|---|
| 1 | Leben gleich `DAT_BASE_HP`, Pike 80.000 | Tabelle. Am 18.10. waren es 100.000 (L109), also andere Einstellung | Ein Wert weicht ab |
| 2 | Nahkampf je Takt genau `DAT_MELEE_DAMAGE`, kein Paar ohne Schaden | Tabelle, Lauf K | Anderer Wert oder anderer Rhythmus. Schützen, die statt zu schlagen schießen, sind ein Fund für ihre Zeile |
| 3 | Angstfaktor: 5 Prozent je Stufe | Datei. **Im Speicher umgebaut** (0x531200), Lauf K sah 162 und 324 statt 150 und 300 | Regel danach aufschreiben (P332) |
| 4 | Pfeil und Bolzen gleich Tabelle je Ziel | 17.10.: Assassine 1.200 und 6.000 passen | Wert weicht ab. **Schleuder ausgenommen:** gemessen 400, Tabelle sagt anderes, der Code ist auf 297 Byte ersetzt (0x531DFF). Dort wird nur gemessen |
| 5 | Stehendes Ziel: jeder Schuss trifft | 0 Lücken in 370 | Eine Lücke |
| 6 | Laufendes Ziel: Pfeile verfehlen | L79, feste Stelle | Quote 100 Prozent |
| 7 | Reichweite Bogen zwischen 35 und 45 Feldern, nicht Tabelle 54 | L82, Sprung im Code (0x54B201) | Außerhalb. Regel danach aufschreiben |
| 8 | Reaktion höchstens Prüfrunde plus Weg (64, 128, 256) | L78, Tabelle | Später als das |
| 9 | Katapult 20, Trebuchet 60, Mangonel 5 je Stein, Leben aus `DAT_BUILDING_HP`: Hütte 11 Steine, Turm 5 201 | `processEntityHitBuildingOrUnit`, Tabelle | Andere Stufen. **Teil C sagt: Beobachtung, keine Bestätigung,** die Regel entsteht hier |
| 10 | Kein Schaden an Lager, Bergfried, Zugbrücke, Mordgrube, Pechgraben, Teich | `DAT_BuildingTypeHasHealth` 0 | Leben fällt |
| 11 | Besatzung: Trebuchet 3, Katapult, Mangonel, Ballista, Feuerballiste je 2, Ramme und Turm 4, Schild 1 | `getRemainingRequiredEngineers` | Gerät schießt oder fährt mit weniger |
| 12 | Mauer: bei höchstens 1 Nachbarn 1,5-fach, bei mehr als 2 halb | P322 | Andere Stufen |
| 13 | Schaden in G gleich E. Gehtempo Keule verschieden | Code oben | Schaden weicht ab, Keule gleich. Das zweite wäre der Umbau durch UCP |
| 14 | A3: Auf Tempo 40 fehlt kein Takt, A4: mit Lesen nicht weniger Takte als ohne, über das Rauschen der beiden Läufe ohne Lesen hinaus | Checkliste | Takt fehlt, Abzug |

## Abbruch

Frist je Abschnitt: gerechnete Obergrenze mal 1,5, nach der Probe mit dem gemessenen Setzen neu gerechnet. Von Hand gestoppt, Spiel weg, Aufzeichnung weg, 5 s kein Takt (Grenze wie Lauf K, das Setzen von 2.400 Einheiten misst die Probe). Modul nicht aktiv laut `ucp3.log`. Karte nicht ladbar, Spielart anders als erwartet oder sie ändert sich im Abschnitt. Takt fehlt oder ist gemischt in einem jeden Takt gelesenen Durchgang. Tor nach V1. **Ein ganzer Durchgang ohne einen einzigen Treffer:** Dann stimmt der Aufbau nicht, das darf nicht 18 Mal laufen.

**Kein Abbruch, sondern Fund:** eine widerlegte Zeile, eine Einheit greift nicht an, ein Gebäude lässt sich nicht setzen (Status mit Grund), eine einzelne gesperrte Zelle, Abzug in der Treppe, keine Schlacht zu Ende.

**Nach jedem Ende:** Das Ende wird sofort gemeldet, Nachprüfung danach. Spiel anhalten, nachlesen, dass der Takt steht, Aufzeichnung beenden, Sperre frei. Hängt die Instanz: `{"menue": 41}`, nicht abschießen. Kein zweiter Lauf von selbst.

## Erfolg

Heißt nicht "alles bestätigt". Heißt: Jede der 1.158 Zeilen hat einen Status mit Beleg (bestätigt, widerlegt, gemessen, nicht möglich mit Grund, gestört), kein Takt fehlt in den jeden Takt gelesenen Durchgängen, die Treppe lief unter Last, die Gegenprobe ist gefahren.

## Auswertung

A1, A2, A3, A4, A9, A10, A12, A13, die 89 Punkte aus `punkte_zuteilung.csv`, alle Zeilen. Wiederaufnehmbar wie in Lauf K, sie läuft nach der Meldung. Ergebnis: `Ergebnis_Lauf_S.md`, `Punkte_Lauf_S.md`, Steckbrief, Duell- und Beschussmatrix, Belagerungstabelle als CSV, Status in `versuche_szenario.csv`. Dann Handbuch, Wissensregister, Wissensstand, Backlog. Am Ende der Ton.

## Zuteilung der Punkte

89 Punkte: 75 aus der Liste Lauf S, 10 aus Lauf F, 4 aus Lauf K (`punkte_zuteilung.txt`, Prüfung: keiner fehlt, keiner doppelt).

| Wo | Punkte |
|---|---|
| E V1 Steckbrief | 9 |
| E V2 Duell | 5 |
| E V4 Belagerung, Bemannen, Munition | 12 |
| E V4b Fußtruppen gegen Gebäude | 8 |
| E V5 Massenschlacht | 1 |
| E V6 Marsch | 6 |
| E V7 Sonderfälle, Zelte, Tunnel | 29 |
| G Gefecht | 8 |
| K laufende KI | 9 |
| Nicht in diesem Lauf: P307 (braucht Bündnis), P312 (braucht `GM_SIEGE_THAT`) | 2 |

5 Punkte sind noch unscharf (P123, P350, P351, P352, P353). Sie werden beim Bauen geschärft, sonst bleiben sie "gesehen". P201 nennt Karte 200: Die Größe von Grumpy Neighbors lese ich im Lauf und rechne die Grenze nach P375 um.

## Trockenlauf

1. Das ganze Programm gegen ein künstliches Spiel, jeder Abbruchgrund, mit Sabotage (`lauf_negativ.py "S:"`). Dazu eigens: Ein fremder Treffer muss "gestört" ergeben, die Kontrolle muss anschlagen, eine schmutzige Zelle muss gesperrt werden, ein Durchgang ohne Treffer muss abbrechen.
2. Kleine Probe am echten Spiel, nur mit Instanz 2, mit Ansage. Sie beantwortet die Fragen unten.
3. Erst danach nenne ich dir die gerechnete Dauer, und du sagst, ob er startet.

## Noch nicht geprüft: Das klärt die Probe

| Frage | Warum offen | Wenn nein |
|---|---|---|
| Steht die Karte in der Liste? | Der Editor sucht `maps\*.map`, die Karte liegt nur im Plugin-Ordner. In `Instanz2\maps` fehlt sie. Ob `maploader` das ändert, ist nicht geprüft | Kopie nach `Instanz2\maps`, Rückweg: wieder herausnehmen |
| Sind die gezählten Zellen begehbar? | Gezählt ist "wie die große Fläche", was die Logik-Bits heißen, ist nicht entschieden | Andere Zellen, neu rechnen |
| Hängt das Laden? | In Lauf K hing Laden im Hauptmenü (Modal 14) | Weg wie Lauf K |
| Welcher `currentGameMode` im Editor, welche Ansicht, läuft die Zeit? | Am 17.10. nur auf neuer Karte gemessen | Melden, nicht umdeuten |
| Wie lange dauert Abräumen? Gehen die 36 Gebäude weg? | `killUnits` ist gemessen, sein Steintod in Takten nicht. Gebäude abreißen im Editor nie geprüft | Karte neu laden statt abräumen |
| Lassen sich alle 82 Ziele setzen? | 63 haben eine Bauzeile, 19 nicht: Mauern, Holztore, Burg-Stufen, Außenposten, Bienenstock und andere (`tabellen.txt`). `setzeGebaeude` meldet immer ok, darum lese ich die Gebäudeliste nach. Apfelplantage ging am 17.10. nicht | Status "nicht setzbar", mit Grund |
| Wirken Befehle an Spieler 2? | Am 18.10. "quittiert, wirkt aber nicht" (L109), seit 19.10. über `alsSpieler` | Anderer Weg, sonst nur Spieler 1 greift an |
| Bemannen, Haltung, Tor, Kuh werfen, Pech anzünden, Öl per Befehl? | Teils nie per Befehl gemacht | Einzeln in `spielbefehl` suchen |
| Stehen Mangonel und Ballista ohne Turm? | `spawnUnit` trägt sie in den Turm ein, wenn einer da ist. Am Boden nie probiert | Turm darunter setzen |
| Was passiert, wenn im Editor ein Lord fällt? | `UpdateLord` zweigt ab | Lord-Zeilen in eigenen Durchgang am Ende |
| Wie schnell gehen 2.400 Einheiten aufs Feld? | Nie gemacht. Höchstens 2.498 Plätze laut `spawnUnit` (0x9C2), die Spalte "2.500" der Liste ist also knapp zu hoch | Über mehrere Takte setzen |

## Was aus Lauf F und K eingebaut ist

Tempo setzen, solange das Spiel steht. Lesen 5 ms nach dem Taktsprung; im großen Kampf reicht das nicht immer (K3), darum haben die jeden Takt gelesenen Durchgänge wenige Einheiten, und A3 zählt es nach. Platz 0 der Einheiten zählt nie. Einheiten über alle 2.500 Plätze zählen, nicht bis `maxUnitCount`. Sperre mit eigenem Namen, Instanz 5 lehnt das Programm ab. `ucp3.log` vor dem Start. Auswertung sparsam (`Bytekarte`) und wiederaufnehmbar. Hintergrundjobs gehen mit der Sitzung verloren: Der Lauf schreibt nach jedem Durchgang mit und geht nach einem Abbruch, auf dein Ja, beim nächsten Durchgang weiter. Tabellen gelten erst, wenn sie beim Start gelesen sind. Wer eine Formel aus dem Export nimmt, prüft zuerst `code_aenderungen.csv`.

## Beziehungen

- Versuch und Zelle: Ein Versuch liegt in genau einer Zelle je Durchgang, eine Zelle hält je Durchgang genau einen Versuch.
- Einheit und Versuch: Jede Einheit gehört über Nummer und `uid` zu genau einem Versuch, jeder Versuch nennt seine Einheiten.
- Durchgang und Aufzeichnung: Jeder Durchgang liegt mit Takt von und bis in genau einer Aufzeichnung, jede Aufzeichnung nennt ihre Durchgänge.
- Zeile und Beleg: Jede Zeile der Liste nennt Durchgang und Takte, jeder Durchgang nennt seine Zeilen.

## Zu bauen

Neu, nicht geflickt: Das alte `editor_messen.py` misst mit Schlafzeiten in Sekunden und liest nur rund alle 7 Takte.

- `src/selfaware/tools/experiments/auge_lauf_s.py`: Abschnitte, Durchgänge, Zellen, Tor, Abbruch, auf den Bausteinen von Lauf F und K.
- `src/selfaware/tools/experiments/auge_versuche.py`: Liste in Durchgänge, Aufbau je Art, Grenzen aus den gelesenen Tabellen und aus V1.
- `src/selfaware/tools/analysis/auge_versuche_auswertung.py`: je Versuch die Werte und die Stör-Prüfung.
- `tests/test_auge_lauf_s.py`, Fälle `"S:"` in `lauf_negativ.py`.
- Modul nur, wenn die Probe es verlangt, und nur auf Instanz 2.

Setzen, Abräumen und Schreiben im Speicher gibt es nur in diesem Messlauf. Nichts davon geht in SamurAI (Fairness).

## Was dieser Lauf nicht beantwortet

- Bündnis (P001, P185, P187, P254, P307), `GM_SIEGE_THAT` (P312), Wellen-System (P281 bis P288, P290 bis P293): braucht andere Spielart oder Mission.
- Außenposten (P244, P256, P273), wenig Holz bei viel Gold (P182, P183, P191), P271: andere Lage im Gefecht. Was davon in G nebenbei vorkommt, wird mitgelesen, ist aber kein Ziel.
- Die Karte aus P373 bis P376 und die Maus.
- Aus Lauf F 8 offene und 27 nur gesehene Punkte (P041, P058, P059, P065, P070, P071, P134, P215).
- Ob SamurAI die Werte richtig nutzt: Das ist das Gehirn, danach.

## Fremde Grenzen (Regel 5, Schritt 0)

Die Websuche fand keine belastbare Grenze des Editors, nur Forenzahlen zur Einheitenobergrenze, die sich widersprechen (10.000, 3.000) und andere Fassungen meinen. Gezählt wird darum aus dem Code dieser Fassung: 2.498 Plätze.

## Belege

Alle in `data/research/auge_plan/lauf_s_plan/`:

| Datei | Was | Befehl |
|---|---|---|
| `karte_flaeche.txt`, `karte_zellen.json` | Fläche und Zellen der Karte | `karte_flaeche.py` |
| `tabellen.txt` | Leben, Tempo, Maske, Schaden, Reichweite, Gebäude | `tabellen.py` |
| `kampf_takt_t9.txt` | Trefferrhythmus und Katapult aus Lauf K | `kampf_takt.py t9` |
| `alte_schuesse.txt` | Trefferquote stehendes Ziel 17.10., erster Treffer in den Duellen 18.10. | `alte_schuesse.py` |
| `spielart_im_code.txt` | Spielart im Kampfcode, UCP-Stellen | `spielart_im_code.py` |
| `rechnung_dauer.txt` | Obergrenzen, mit Liste des Ungemessenen | `rechnung_dauer.py` |
| `punkte_zuteilung.csv`, `.txt` | Welcher Punkt wo | `punkte_zuteilung.py` |
