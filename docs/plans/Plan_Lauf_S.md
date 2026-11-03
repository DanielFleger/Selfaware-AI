# Plan: Lauf S (B-142)

Erstellt 03.11.2026 von SRE nach Daniels "Ja, Lauf S planen", am selben Tag neu gefasst nach dem Frage-Agenten (Ampel Rot, siehe unten). **Noch nichts gebaut, nichts gestartet.** Grundlage: `data/research/auge_plan/Checkliste_Auge.md` (Teil B, C, D), `versuche_szenario.csv`, die Lehren aus Lauf F und K. Jede Zahl hier hat ihren Befehl in `data/research/auge_plan/lauf_s_plan/`, oben in jedem Skript.

## Frage des Laufs

Rechnet das Spiel im Kampf wirklich das, was in seinen Tabellen steht: Leben, Tempo, Reichweite, Schaden, Reaktion, jede Einheit gegen jede Einheit und jedes Gebäude, ohne dass etwas stört? Und sieht das Auge das alles, auch in der größten Schlacht, ohne das Spiel zu bremsen?

## Ansage

| | |
|---|---|
| **Was wird getestet** | Das Auge und die Kampfregeln des Spiels. Nicht SamurAI |
| **Erhofft** | Leben, Schaden und Besatzung passen zu den Tabellen im Speicher. Die Prüfrunde liegt auf den Takt genau, wo der Code sie vorhersagt. Das Auge verliert auf Tempo 40 keinen Takt, und mit 2.400 Einheiten zieht das Lesen auf keiner Stufe Tempo ab. Der Schaden ist im Editor und im Gefecht gleich |
| **Was es widerlegt** | Eine Messung passt nicht zur Tabelle, ein Takt fehlt, die Wechselprobe zeigt einen Abzug, die Stichprobe im Gefecht weicht vom Editor ab. Jede Vorhersage steht einzeln unten, vor dem Lauf |
| **Wie** | Instanz 2. Editor auf `Liga_Grumpy Neighbors`: aufstellen, einen Befehl geben, messen, abräumen, in Durchgängen mit mehreren Versuchen gleichzeitig, je Durchgang eine Kontrolle. Massenschlachten zuletzt. Dann Gegenprobe im Gefecht. Instanz 5 bleibt unberührt |
| **Wie lange** | Grenze in Takten je Durchgang, zusammen gerechnet höchstens 102 Minuten ohne Setzen und Laden (`rechnung_dauer.txt`). Ein Durchgang endet, sobald seine Zellen fertig sind. Offen: wie schnell das Spiel mit 2.400 Einheiten läuft. Das misst die Probe, die Zahl bekommst du vor deinem Ja zum Lauf |
| **Nutzen fürs Ziel** | Danach ist das Auge in allen drei Lagen geprüft: Frieden (F), KI im Kampf (K), jede Kampflage einzeln (S) |
| **Nutzen fürs 3-Jahres-Ziel** | SamurAI soll selbst lernen, mit Werten aus dem Spiel statt aus Annahmen. Dieser Lauf liefert die Grundwerte, gegen die das Gehirn seine Vorhersagen prüft |

## Karte und Spielart

**Hauptbank E: `Liga_Grumpy Neighbors` im Karteneditor** (Daniel 02.11.: "eine karte laden aus eigenen szenarien ... grumpy neighbors weil dort eben alles möglich ist"). Weg laut Code: Eigene Szenarien, `CustomScenarios_Main` Knopf 1 öffnet die Kartenliste (`activateLoadOrSaveMapUI`, 0x00440770). Das Laden von dort setzt `gameMode_2 = GM_EDITOR` (0x004950B0). Knopf 4 wäre "Szenario spielen" mit `gameMode_2` 2, also nicht der Editor. Keine KI, keine Arbeiter.

Gemessen aus der Kartendatei (`karte_flaeche.txt`): Typ 1, 4 Spieler, 57.247 von 80.400 Feldern eben und frei. **Die Karte bringt 36 Gebäude und 136 Einheiten mit:** je Startplatz 9 Gebäude und einen Lord, dazu Tierherden. Das wird zuerst abgeräumt und das Abräumen geprüft. Die Fläche reicht für den Plan, und die Karte hat Hügel für P330 (Höhe bis 130, Median 8). Kein Grund, von deiner Wahl abzuweichen.

**Gegenbank G: dieselbe Karte als Gefecht** (`currentGameMode` 99, `gameMode_2` 3). Dort spielt SamurAI, also müssen die Werte dort gelten. Spieler 2 wird nach dem Start zum Mensch-Platz, die KI ist aus (L119, gemessen: Die Partie läuft weiter, Spieler 2 baut nichts mehr). So bleibt die Spielart echt, und keine KI greift in gesetzte Einheiten ein. Beide Lords bleiben stehen: Abgeräumt wird mit `toeteAlle` "ohneLord" (B-149), denn das einfache `toeteAlle` nimmt auch den Lord (`killUnits` 0x00530390), und das wäre das Ende der Partie.

**Bank K: geladener Stand `AugeK 000735 T70029` aus Lauf K.** Nur für die Punkte, die eine laufende KI brauchen. Dort schießt ein Katapult schon (`kampf_takt_t9.txt`). Ob die KI dort noch baut, liest die Probe.

### Was der Code über Editor und Gefecht sagt

Darum reicht der Editor allein nicht. Beleg: `spielart_im_code.txt`. Das ist die Datei, im Speicher kann UCP es ändern.

| Stelle | Regel | Folge |
|---|---|---|
| `processUnitAttackOtherUnit`, `processEntityDamageToUnit`, `processDamageToBuilding` | Sie fragen die Spielart nur für Töne ab | **Vorhersage:** Schaden im Editor gleich Gefecht. Die Stichprobe in G prüft das |
| `UpdateMaceman` Zeile 405 bis 410 | Im Einzelspiel geht der Streitkolbenkämpfer (E_MACE 26), solange kein Feind näher als 0xC0 Mikropunkte (24 Felder) ist, sonst rennt er. UCP hat genau diese Stelle mit einem Sprung umgebaut (0x560B4F) | Gehtempo in beiden Banken, alle Arten |
| `spawnUnit` Zeile 71 bis 108 | Katapult und Trebuchet: 40 Steine im Einzelspiel auf Plätzen ohne Menschen, 20 im Gefecht, auf Mensch-Plätzen 20. UCP macht aus der letzten Zahl 10 (0x53E5DE, `mov ..., 0x14`, das Byte 0x53E5E5). Im Editor zählt jeder Platz außer dem eigenen als ohne Menschen (0x004950B0) | Munition lesen, nie annehmen. P216 in E und G |
| `processDamageFromKillingPit` Zeile 18 bis 24 | Im Editor löst die Mordgrube nur aus, wenn Grube oder Einheit dem eigenen Platz gehört | So aufstellen (V7.004) |
| `giveTribeAnInstruction` Zeile 481 | Im Gefecht fallen Mauerbefehle weg, wenn "starke Mauern" an ist (`strongWalls2`) | In G den Schalter lesen |
| `UpdateLord` (12 Stellen), `UpdateOutpostBuilding` Zeile 54 | Lord-Tod und Außenposten laufen im Editor anders oder gar nicht | Nur in G oder K |
| `MenuView_CustomScenarios_Prepare` Zeile 25 bis 30 | Setzt `gameMode_2`, aber nicht `currentGameMode` | `currentGameMode` hängt daran, was vorher lief. E startet nach frischem Spielstart und liest ihn (A13) |

**Keine Spielart-Stelle** haben `updateUnits` an der Prüfrunde und `acquireShootTarget`. Darum in G nur eine Stichprobe für Reaktion und Reichweite. Der Sonderweg in `processMeleeInitiation` trifft keine der 27 Arten: Seine Tabelle ist überall 0 (`tabellen.txt`).

**A13 in der Checkliste ("F und S gleich") passt so nicht mehr:** F lief mit `gameMode_2` 2, E läuft mit 1. Das Ergebnis schreibe ich als Berichtigung auf.

## Aufbau: Zellen

Warum nicht einer nach dem anderen: Jeder Versuch hieße einmal abräumen. Die Karte hat Platz für mehrere ungestörte Versuche gleichzeitig.

**Eine Zelle ist ein Rechteck, in dem alles liegt: Aufstellung, Laufweg, Ziel.** Es ist ganz eben und frei. Der Abstand zwischen zwei Zellen gilt von Rand zu Rand, also auch vom Laufweg aus. Gezählt aus der Karte (`zellen_je_art.txt`, gierig gepackt, also eher zu wenig). Im Gefecht halten die Zellen auch Abstand zu den Startplätzen; dort steht das schlechteste Paar, wo die Lords wirklich stehen, liest der Lauf.

| Zellenart | Größe | Abstand | Zellen Editor | Zellen Gefecht | Für | Grund des Abstands |
|---|---|---|---|---|---|---|
| nah | 12 x 12 | 60 | 11 | 6 | V1 Reaktion nah, V2, V3 Fußschützen, V4b | Bogenschütze (E_ARCHER 22) trifft aus 35 Feldern, aus 45 nicht (L82); Tabelle Pfeil 54 |
| bahn | 32 x 32 | 60 | 4 | 2 | V1 Gehtempo, 30 Felder schräg und 30 gerade; Reaktion weit | wie oben |
| weit | 8 x 64 | 60 | 5 | 2 | V1 Reichweite Fußschützen | wie oben |
| lauf | 24 x 24 | 60 | 6 | 4 | V3 laufendes Ziel | wie oben |
| gerät | 24 x 24 | 80 | 5 | 2 | V1 Reaktion Geräte, V3 Geräte, V4 | Größter Tabellenwert aller Geschosse: 75 |
| gerät-bahn | 32 x 32 | 80 | 4 | 2 | V1 Gehtempo Geräte | wie oben |
| gerät-weit | 8 x 88 | 80 | 4 | 2 | V1 Reichweite Geräte | wie oben |

**Je Durchgang ist eine Zelle die Kontrolle:** eine Einheit allein, ohne Befehl. Verliert sie Leben oder läuft sie los, stört etwas, das ich nicht kenne.

**Ob wirklich nichts stört, wird nachgerechnet, nicht angenommen.** Jeder Versuch gilt erst als ungestört, wenn seine Einheiten in ihrer Zelle blieben, jeder Treffer einem Täter derselben Zelle zugeordnet ist und kein Leben ohne Täter fiel. Sonst heißt er "gestört" und wird einmal allein wiederholt. Bleibt er gestört, steht das so in der Liste.

**Aufgestellt wird im angehaltenen Spiel,** damit alle Zellen im selben Takt anfangen und die erste Lesung den Anfang sieht.

**Nach jedem Durchgang wird die Zelle geprüft:** keine Einheit, kein Gebäude, Logik und Höhe wie vorher. Ist sie es nicht, wird sie gesperrt. Bleibt zu wenig für einen Versuch und die Kontrolle, wird die Karte neu geladen.

## Warum welches Tempo

Daniels Frage vom 02.11. "warum nicht gleich 1000?": Es gilt immer die höchste Stufe, bei der die Messung noch stimmt.

| Messung | Tempo | Warum |
|---|---|---|
| Nahkampf, Reaktion, Flugzeit, Zähler je Takt | 40, jeder Takt gelesen | Nahkampf trifft jeden Takt: 567 von 705 Abständen zwischen zwei Lebensverlusten sind genau 1 Takt (`kampf_takt_t9.txt`). 40 ist die höchste Stufe, die jeden Takt liest (Lauf F) |
| Beschuss ohne Flugzeit, Gehtempo, Marsch | 200 | Treffer höchstens alle 56 Takte (Handbuch), ein Feld dauert mindestens rund 11 Takte (L80). Gerechnet aus Lauf K: Eine Lesung dauert rund 9 ms, das sind rund 2 Takte |
| Belagerung | 1000 | Katapult alle 123 Takte (`kampf_takt_t9.txt`). Auf 1000 liest das Auge rund jeden 7. Takt (Lauf K: 19.193 Lesungen in 133.512 Takten). Das reicht, wenn nur Lebensstufen zählen |
| Massenschlacht | 1000 und die Wechselprobe | Deine Vorgabe: 1 bis 1000 ohne Abzug |

Alles in Takten. Die Uhr zählt nur dort, wo kein Takt läuft: Spiel hängt, Laden, Kanal. Und dort, wo Takte je Sekunde die Messgröße sind.

## A4: Zieht das Lesen Tempo ab?

**Der alte Vergleich taugt in der Schlacht nicht.** Er misst ohne, mit, ohne Lesen und nimmt den Unterschied der beiden Läufe ohne Lesen als Rauschen (`a4_tempotreppe`). In einer Schlacht sterben Einheiten, das Tempo ändert sich schon dadurch, und alles das zählt dann als Rauschen. In Lauf K: 827, 812,7, 800,1 Takte je Sekunde. Das hätte erst ab rund 5 Prozent Abzug angeschlagen. **"Kein Abzug in der Bremsprobe" aus Lauf K ist also nur auf rund 5 Prozent genau.** Lauf F lief im ruhigen Dorf (824,2, 825,2, 825,5), dort hält die Aussage auf unter 1 Prozent.

**Neu: die Wechselprobe.** Je Stufe abwechselnd ohne und mit Lesen, 5 Mal mit, 6 Mal ohne. Jede Phase mit Lesen wird mit den beiden Phasen ohne Lesen links und rechts verglichen. So fällt ein langsames Abfallen der Last heraus. Abzug ist der Median dieser Unterschiede, Rauschen der Median der Unterschiede zweier benachbarter Phasen ohne Lesen. **Jede Messung nennt, ab welchem Abzug sie angeschlagen hätte.**

| Stufe | Takte je Phase | Phasen | Grund |
|---|---|---|---|
| 1, 10 | 20, 100 | 3 | Wie Lauf F. So wenig Takte je Sekunde, dass das Lesen fertig ist, bevor der nächste kommt |
| 40, 100, 200 | 80, 200, 400 | 11 | Je rund 2 Sekunden, so ist der Ablesefehler von rund 10 ms unter 1 Prozent |
| 500, 1000 | 1.000, 1.000 | 11 | Bis zu 11 Takte kommen je Bild, 1.000 Takte halten den Ablesefehler bei rund 1 Prozent |

Zusammen 29.840 Takte, 189 s, je einmal auf der leeren Karte und unter Last.

**Die Last bleibt gleich, weil niemand stirbt.** 1.000 Pikeniere (E_PIKE 25) gegen 1.000, je 200 Bogenschützen dahinter, zusammen 2.400. Der Nahkampfschaden Pikenier gegen Pikenier wird für diesen Abschnitt in der Tabelle von 30 auf 1 gesetzt: Sie kämpfen und rechnen jeden Takt wie sonst auch, aber 80.000 Leben halten 80.000 Takte. Die Schützen sind nicht gebremst, gerechnet töten sie rund einen Pikenier je 26 Takte. Die Einheitenzahl steht je Phase im Protokoll, und unter 2.000 wird vor der nächsten Stufe nachgesetzt. Den Schreibzugriff gibt es nur in diesem Messlauf, danach wird der alte Wert zurückgeschrieben und nachgelesen.

Die echten Schlachten V5 laufen ohne jede Änderung und liefern zusätzlich Takte je Sekunde je Einheitenzahl.

## Abschnitte

Grenze heißt: So lange höchstens, ein Durchgang endet früher, wenn alle Zellen fertig sind. Dazu kommen je Durchgang höchstens 400 Takte Abräumen. Das ist noch nicht gemessen, nur die Wartezeit des alten Werkzeugs `shc.py`; die Probe misst es.

| # | Abschnitt | Tempo | Versuche, Zellenart | Grenze je Durchgang | Grund der Grenze |
|---|---|---|---|---|---|
| 0 | Frisch starten, Spielart lesen, alle Tabellen lesen, Karte laden, abräumen | | | | Tabellen beim Laufstart, damit UCP zählt (Checkliste). Die Zahlen hier aus Lauf K dienen nur der Planung |
| 1 | A4 auf der leeren Karte | Wechsel | | 29.840 Takte | Lauf F hat das leere Spiel nicht gemessen |
| 2 | **V1 Gehtempo** je lauffähiger Art, 30 Felder schräg, 30 gerade | 200 | 24, bahn und gerät-bahn | 60 x Tempo-Wert x 12 x 2 Takte, gleiche Werte zusammen | Rund 12 Takte je Feld je Stufe (L80, Stufe 1 und 2), das mal 2. **Annahme** ab Stufe 3. Trebuchet, Mangonel, Ballista laufen laut Tabelle nicht |
| 3 | **V1 Reaktion**, je Art 5 Fälle: Haltung aggressiv in 24 und 26 Feldern, defensiv in 4 und 6, stehen in 4 | 40 | 57 nah, 38 bahn, 25 gerät | 2 x Prüfrunde der Art, also 128, 256 oder 512 Takte | `findNearestEnemyAndHeadTowardsIt`: aggressiv 200 Mikropunkte (25 Felder), defensiv 40 (5 Felder), dazwischen liegen die Fälle. Gemessen wird das Erkennen, nicht das Ankommen. Der Gegner ist ein Speerträger (E_SPEAR 24) mit der Haltung "stehen", er bleibt am Platz. Turm, Ramme, Schild haben keine Prüfrunde |
| 4 | **V1 Reichweite**: Befehl auf ein Ziel 60 Felder entfernt, Geräte 84. Das Ziel ist **keine** Assassine | 200 | 6 weit, 2 gerät-weit, 3 x 6 Abstände stehend | Weg x Takte je Feld aus Abschnitt 2, plus 411 | Am 17.10. war das Ziel immer eine Assassine: Die "20 Felder" sind ihre Tarnregel (`acquireShootTarget`), nicht die Reichweite |
| | **Tor:** Leben und Besatzung gegen Tabelle, Prüfrunde gegen Vorhersage | | | | Stimmt der Steckbrief nicht, hält der Lauf hier an (Checkliste). Erst erklären, dann weiter |
| 5 | **V2 Duelle**: beide bekommen den Befehl, Abstand 1 Feld, bis eine ganze Prüfrunde nach dem ersten Treffer um ist oder einer tot | 40 | 190, nah | 507 Takte | Ein Duell füllt zwei Zeilen, also 190 statt 361. Eine Prüfrunde, weil die Einheit dort ihr Ziel neu wählen kann; so sieht die Zeile auch, was danach geschieht. Grenze: größter erster Treffer vom 18.10. (251, `alte_schuesse.txt`) plus größte Prüfrunde (256) |
| 6 | **V3 Beschuss**, Abstand 8, 3 Treffer. Je Schütze ein Ziel auf Tempo 40 für die Flugzeit, die übrigen auf 200 | 40 und 200 | 114 nah, 57 gerät | 867 Takte, nach V1 neu | 8 Felder, weil der Feuerwerfer (A_FIRETHROWER 76) nur bis 10 reicht und der Schaden von 4 bis 20 Feldern gleich ist (Handbuch). Treffer 1 Schaden, 2 Schusstakt, 3 Gegenprobe. Grenze: erster Treffer 411 plus 2 x 228. Stehendes Ziel: 0 Lücken in 370 Schussabständen (`alte_schuesse.txt`) |
| 7 | **V3 laufendes Ziel** je Schütze, 10 Schuss. Das Ziel pendelt auf 20 Feldern, in 8 Feldern Abstand vorbei | 40 | 6 lauf, 3 gerät | 2.463 Takte | Noch nie gemessen (Handbuch: "noch zu messen"), wichtig fürs Ausweichen. Das Programm gibt an jedem Ende den nächsten Laufbefehl |
| 8 | **V4b Fußtruppen** gegen Tore, Türme, Mauern | 40 | 80, nah | 507 Takte | Wie V2 |
| 9 | **V4 Belagerung**, echt bemannt, bis zerstört oder Munition leer | 1000 | 492, gerät | 4.920 Takte, nach V1 neu | Höchstens 40 Steine x 123 Takte. Das ist das Katapult; den Schusstakt der anderen misst V1. Mehr Steine als Munition (Turm 5: 201): Rest gerechnet und so gekennzeichnet |
| 10 | **V6 Angriff auf einen Punkt**, 60 Felder Marsch | 200 | 8, ganze Karte | 5.000 Takte | Langsamster Fußsoldat (Tempo-Wert 3, rund 36 Takte je Feld), mal 2 für den Stau. **Annahme**, Abschnitt 2 misst das Tempo, V6 selbst den Stau |
| 11 | **V7 Sonderfälle** und die Punkte dazu, auch Steigen über die Leiter | 40 | 11, ganze Karte | 3.000 Takte | Längster aus dem Code bekannter Ablauf 808 Takte (Giftwolke, P297), dazu Anmarsch. **Annahme** für den Brand |
| 12 | **V5 Massenschlachten** von klein nach groß, unverändert | 1000 | 8, ganze Karte | 30.000 Takte | Längste Tötung laut Tabelle unter den Hauptkämpfern 3.200 Takte (Speer gegen Pikenier), mit Sklaven 8.000. Bei 1.000 gegen 1.000 mehrere Runden. Kein Ende ist ein Ergebnis, kein Scheitern |
| 13 | **A4 unter Last** | Wechsel | 2.400 Einheiten | 29.840 Takte | Siehe oben |
| 14 | **G Gefecht:** Tabellen neu lesen. Friedenszeit Stufe 1, P331. Dann KI aus. V1 Gehtempo ganz, Reaktion je Prüfrunde eine Art, Reichweite Bogenschütze und Katapult, je Art gegen Schwertkämpfer (19), je Schütze gegen Speer (9), je Gerät gegen Hütte (6), je Fußtruppe gegen Steinmauer (10), die G-Punkte. Lord-Tod zuletzt, er beendet das Spiel | wie oben | | wie oben | **Weicht die Stichprobe ab, gelten die Editor-Werte dieser Gruppe nicht fürs Gefecht:** Die Gruppe wird in G neu gefahren, bevor der Lauf als gültig zählt |
| 15 | **K:** Stand laden, Punkte der laufenden KI | 1000 | | 30.000 Takte | Bis nach dem übernächsten Lord-Fall in Lauf K (88.069 minus 70.029 = 18.040 Takte). Das Laden ändert den Stand (K1), also kein Takt-Vergleich mit Lauf K |

## Vorher festgelegt: was als widerlegt gilt

Quelle der Sollwerte ist immer die Tabelle, die der Lauf beim Start liest. Die Zahlen hier stammen aus Lauf K (`tabellen.txt`).

| # | Vorhersage | Woher | Widerlegt, wenn |
|---|---|---|---|
| 1 | Leben gleich `DAT_BASE_HP`, Pikenier 80.000 | Tabelle. Am 18.10. waren es 100.000 (L109), also andere Einstellung | Ein Wert weicht ab |
| 2 | **Prüfrunde auf den Takt genau:** Die Einheit prüft dort, wo `totalGameTicksUnk & Maske` gleich `fixedRng & Maske` ist | `updateUnits` Zeile 369. Beide Werte lese ich beim Setzen, darum reicht eine Probe je Fall | Sie prüft auf einem anderen Takt |
| 3 | Haltung: aggressiv reagiert in 24 Feldern, in 26 nicht. Defensiv in 4, in 6 nicht. Stehen geht nicht los | `findNearestEnemyAndHeadTowardsIt` Zeile 61 bis 66 | Anderer Rand. Schützen schießen womöglich trotzdem, das ist dann der Befund |
| 4 | Nahkampf je Takt genau `DAT_MELEE_DAMAGE`. Leiterträger und Ingenieur schlagen gar nicht, obwohl die Tabelle ihnen 2 gibt | Tabelle, `DAT_UNIT_CAN_MELEE` 0, Lauf K | Anderer Wert oder anderer Rhythmus. Schützen, die statt zu schlagen schießen, sind ein Fund für ihre Zeile |
| 5 | Angstfaktor: 5 Prozent je Stufe | Datei. **Im Speicher umgebaut** (0x531200), Lauf K sah 162 und 324 statt 150 und 300 | Regel danach aufschreiben (P332) |
| 6 | Pfeil und Bolzen gleich Tabelle je Ziel | 17.10.: Assassine 1.200 und 6.000 passen | Wert weicht ab. **Schleuderer (A_SLINGER 72) ausgenommen:** gemessen 400, die Tabelle sagt anderes, der Code ist auf 297 Byte ersetzt (0x531DFF). Dort wird nur gemessen |
| 7 | Stehendes Ziel: jeder Schuss trifft | 0 Lücken in 370 | Eine Lücke |
| 8 | Laufendes Ziel: Pfeile verfehlen | L79, feste Stelle | Quote 100 Prozent |
| 9 | Reichweite Bogenschütze zwischen 35 und 45 Feldern, nicht Tabelle 54 | L82, Sprung im Code (0x54B201) | Außerhalb. Regel danach aufschreiben |
| 10 | Katapult 20, Trebuchet 60, Mangonel 5 je Stein, Leben aus `DAT_BUILDING_HP`: Hütte 11 Steine, Turm 5 201 | `processEntityHitBuildingOrUnit`, Tabelle | Andere Stufen. **Teil C sagt: Beobachtung, keine Bestätigung,** die Regel entsteht hier |
| 11 | Kein Schaden an Lager, Bergfried, Zugbrücke, Mordgrube, Pechgraben, Teich | `DAT_BuildingTypeHasHealth` 0 | Leben fällt |
| 12 | Besatzung: Trebuchet 3, Katapult, Mangonel, Ballista, Feuerballiste je 2, Ramme und Turm 4, Schild 1 | `getRemainingRequiredEngineers` | Gerät schießt oder fährt mit weniger |
| 13 | Mauer: bei höchstens 1 Nachbarn 1,5-fach, bei mehr als 2 halb | P322 | Andere Stufen |
| 14 | Schaden in G gleich E. Gehtempo Streitkolbenkämpfer verschieden | Code oben | Schaden weicht ab, Tempo gleich. Das zweite wäre der Umbau durch UCP |
| 15 | A3: Auf Tempo 40 fehlt kein Takt. A4: In der Wechselprobe kein Abzug über dem Rauschen, auf jeder Stufe, leer und unter Last | Checkliste, Daniels Vorgabe | Takt fehlt, Abzug |
| 16 | Kontrolle: Die Einheit allein verliert kein Leben und läuft nicht los | Abstand der Zellen | Sie tut es: Dann gilt der ganze Durchgang als gestört |

## Abbruch

**Keine Frist in Sekunden.** Jeder Durchgang hat seine Grenze in Takten. Die Uhr zählt nur gegen Hängen: 5 s kein Takt im laufenden Spiel (wie Lauf K; das Aufstellen läuft im angehaltenen Spiel, die Wache ruht dann), Warten auf Kanal und Laden. Damit kein Abschnitt endlos läuft, gibt es einen Boden fürs Tempo: Bleibt ein Durchgang auf Tempo 200 oder 1000 über 1.000 Takte unter einem Zehntel seiner Stufe, endet er und wird als Fund notiert.

Abbruch des Laufs: von Hand gestoppt, Spiel weg, Aufzeichnung weg. Modul nicht aktiv laut `ucp3.log`. Karte nicht ladbar, Spielart anders als erwartet oder sie ändert sich im Abschnitt. Takt fehlt oder ist gemischt in einem jeden Takt gelesenen Durchgang. Tor nach V1. **Ein ganzer Durchgang ohne einen einzigen Treffer:** Dann stimmt der Aufbau nicht, das darf nicht 19 Mal laufen.

**Kein Abbruch, sondern Fund:** eine widerlegte Zeile, eine Einheit greift nicht an, ein Gebäude lässt sich nicht setzen (Status mit Grund), eine einzelne gesperrte Zelle, Abzug in der Wechselprobe, keine Schlacht zu Ende, Tempo unter dem Boden.

**Nach jedem Ende:** Das Ende wird sofort gemeldet, Nachprüfung danach. Tabellenwert zurückschreiben, Spiel anhalten, nachlesen, dass der Takt steht, Aufzeichnung beenden, Sperre frei. Hängt die Instanz: `{"menue": 41}`, nicht abschießen. Kein zweiter Lauf von selbst.

## Erfolg

Heißt nicht "alles bestätigt". Heißt: Jede der 1.158 Zeilen hat einen Status mit Beleg (bestätigt, widerlegt, gemessen, nicht möglich mit Grund, gestört), kein Takt fehlt in den jeden Takt gelesenen Durchgängen, die Wechselprobe lief unter Last und nennt ihre Grenze, die Gegenprobe ist gefahren.

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

1. Das ganze Programm gegen ein künstliches Spiel, jeder Abbruchgrund, mit Sabotage (`lauf_negativ.py "S:"`). Dazu eigens: Ein fremder Treffer muss "gestört" ergeben, die Kontrolle muss anschlagen, eine schmutzige Zelle muss gesperrt werden, ein Durchgang ohne Treffer muss abbrechen. **Die Wechselprobe muss 1 Prozent Abzug bei 10 Prozent fallender Last finden,** wo der alte Vergleich "bestätigt" sagt.
2. Kleine Probe am echten Spiel, nur mit Instanz 2, mit Ansage. Sie beantwortet die Fragen unten, **darunter eine kurze Schlacht mit 2.400 Einheiten und ein ganzer Durchgang im Gefecht.** Was erst nach über einer Stunde auffiele, soll hier auffallen.
3. Erst danach rechne ich die Grenzen mit den gemessenen Werten neu, nenne dir die Dauer, und du sagst, ob er startet.

## Noch nicht geprüft: Das klärt die Probe

| Frage | Warum offen | Wenn nein |
|---|---|---|
| Steht die Karte in der Liste? | Der Editor sucht `maps\*.map`, die Karte liegt nur im Plugin-Ordner. In `Instanz2\maps` fehlt sie. Ob `maploader` das ändert, ist nicht geprüft | Kopie nach `Instanz2\maps`, Rückweg: wieder herausnehmen |
| Sind die gezählten Zellen begehbar? | Gezählt ist "wie die große Fläche", was die Logik-Bits heißen, ist nicht entschieden | Andere Zellen, neu rechnen |
| Hängt das Laden? | In Lauf K hing Laden im Hauptmenü (Modal 14) | Weg wie Lauf K |
| Welcher `currentGameMode` im Editor, welche Ansicht, läuft die Zeit? | Am 17.10. nur auf neuer Karte gemessen | Melden, nicht umdeuten |
| Wie lange dauert Abräumen? Gehen Gebäude, Lords und Tiere weg? | `killUnits` ist gemessen, sein Steintod in Takten nicht. Tiere gehören Spieler 0, Gebäude abreißen im Editor nie geprüft | Karte neu laden statt abräumen |
| Lassen sich alle 82 Ziele setzen? | 63 haben eine Bauzeile, 19 nicht: Mauern, Holztore, Burg-Stufen, Außenposten, Bienenstock und andere (`tabellen.txt`). `setzeGebaeude` meldet immer ok, darum lese ich die Gebäudeliste nach. Apfelplantage ging am 17.10. nicht | Status "nicht setzbar", mit Grund |
| Wirken Befehle an Spieler 2? | Am 18.10. "quittiert, wirkt aber nicht" (L109), seit 19.10. über `alsSpieler` | Anderer Weg, sonst nur Spieler 1 greift an |
| Wie setze ich die Haltung einer gesetzten Einheit? | Die Regel gilt nur mit Trupp (`tribeID` ungleich 0), gesetzte Fußtruppen haben vielleicht keinen | Trupp bilden, sonst Fälle ohne Haltung melden |
| Bemannen, Tor, Kuh werfen, Pech anzünden, Öl per Befehl? | Teils nie per Befehl gemacht | Einzeln in `spielbefehl` suchen |
| Stehen Mangonel und Ballista ohne Turm? | `spawnUnit` trägt sie in den Turm ein, wenn einer da ist. Am Boden nie probiert | Turm darunter setzen |
| Was passiert, wenn im Editor ein Lord fällt? | `UpdateLord` zweigt ab | Lord-Zeilen in eigenen Durchgang am Ende |
| **Schlacht mit 2.400 Einheiten:** Wie schnell gehen sie aufs Feld, wie schnell läuft das Spiel, greift die Wechselprobe, wirkt der Schreibzugriff auf die Schadenstabelle? | Nie gemacht. Lauf K hatte höchstens rund 1.400 belegte Plätze. Höchstens 2.498 Plätze laut `spawnUnit` (0x9C2), die Spalte "2.500" der Liste ist also knapp zu hoch | Über mehrere Takte setzen, Grenzen und Dauer neu rechnen. Geht das Tempo stark zurück, sage ich es dir vor dem Lauf |
| **Ein Durchgang im Gefecht:** Start, KI aus, setzen, Befehl, Abräumen ohne Lord, Kontrolle | G käme sonst erst nach dem ganzen Editor-Teil. `toeteAlle` "ohneLord" fehlt im Modul von Instanz 2, es liegt in `logik_stand_20261025.lua` | Weg ändern, bevor der Lauf startet |

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
- `src/selfaware/tools/experiments/auge_versuche.py`: Liste in Durchgänge, Aufbau je Art, Grenzen aus den gelesenen Tabellen und aus V1. Zellen aus der Karte des laufenden Spiels.
- `src/selfaware/tools/analysis/auge_versuche_auswertung.py`: je Versuch die Werte und die Stör-Prüfung.
- `a4_wechselprobe` in `auge_auswertung.py`. Der alte Vergleich bleibt für Lauf F und K lesbar.
- `toeteAlle` "ohneLord" in die Modul-Ergänzung von `auge_lauf_f.py` (aus `logik_stand_20261025.lua`, B-149). Sonst Modul nur, wenn die Probe es verlangt, und nur auf Instanz 2.
- `tests/test_auge_lauf_s.py`, Fälle `"S:"` in `lauf_negativ.py`.

Setzen, Abräumen und Schreiben im Speicher gibt es nur in diesem Messlauf. Nichts davon geht in SamurAI (Fairness).

## Was dieser Lauf nicht beantwortet

- Bündnis (P001, P185, P187, P254, P307), `GM_SIEGE_THAT` (P312), Wellen-System (P281 bis P288, P290 bis P293): braucht andere Spielart oder Mission.
- Außenposten (P244, P256, P273), wenig Holz bei viel Gold (P182, P183, P191), P271: andere Lage im Gefecht. Was davon in G nebenbei vorkommt, wird mitgelesen, ist aber kein Ziel.
- Die Karte aus P373 bis P376 und die Maus.
- Aus Lauf F 8 offene und 27 nur gesehene Punkte (P041, P058, P059, P065, P070, P071, P134, P215).
- Was die KI mit Geräten tut (Kuhwurf, Stein nachkaufen): nur soweit es in Bank K vorkommt.
- Ob SamurAI die Werte richtig nutzt: Das ist das Gehirn, danach.

## Fremde Grenzen (Regel 5, Schritt 0)

Die Websuche fand keine belastbare Grenze des Editors, nur Forenzahlen zur Einheitenobergrenze, die sich widersprechen (10.000, 3.000) und andere Fassungen meinen. Gezählt wird darum aus dem Code dieser Fassung: 2.498 Plätze.

## Was der Frage-Agent gefunden hat

Prüfung 03.11. mit dem ersten Stand dieses Plans, **Ampel Rot.** Ich habe jeden Befund selbst nachgesehen, alle stimmen.

| Befund | Beleg | Behoben durch |
|---|---|---|
| Wer 60 Felder läuft, verlässt seinen 12 x 12 großen Kern. Die eigene Stör-Regel hätte jeden Geh-Versuch "gestört" genannt, und daran hing das Tor | Plan, erster Stand | Zelle als Rechteck samt Laufweg, Abstand von Rand zu Rand |
| Geräte in V1 standen in den Zellen mit Abstand 60, obwohl sie 80 brauchen | `rechnung_dauer.py`, erster Stand | Eigene Zellenarten für Geräte |
| Das laufende Ziel wäre über 200 Felder gelaufen, ohne Ort dafür | 2.463 Takte bei 11,5 Takten je Feld | Es pendelt auf 20 Feldern |
| Grenze 406 passte nicht zum Schwertkämpfer, und die Haltung fehlte ganz | `findNearestEnemyAndHeadTowardsIt` Zeile 61 bis 66 | Fünf Fälle je Art, gemessen wird das Erkennen, Grenze aus der Prüfrunde |
| A4 hätte in der schrumpfenden Schlacht einen Abzug nicht gesehen: Der Lastrückgang zählte als Rauschen | `a4_tempotreppe`, Lauf K 827, 812,7, 800,1 | Wechselprobe, gleichbleibende Last, Probe schon vorher |
| Die Frist in Sekunden rechnete mit 766 Takten je Sekunde, auch bei 2.400 Einheiten, und passte nicht zu deinem "alles in Takten" | `rechnung_dauer.py`, erster Stand | Keine Frist, Grenzen in Takten, Tempo-Boden |
| Abräumen in G hätte den Lord getötet und die Partie beendet, und die KI hätte in gesetzte Einheiten eingreifen können | `killUnits` 0x530390, `UpdateCatapult` Zeile 572 | "ohneLord", KI aus, ein Durchgang G schon in der Probe |

**Was ich dabei selbst noch gefunden habe:** Die Prüfrunde lässt sich auf den Takt genau vorhersagen. Die "20 Felder" sind die Tarnregel der Assassine, nicht die Reichweite. Leiterträger und Ingenieur können nicht schlagen, trotz Eintrag in der Schadenstabelle. Die Startplätze im Kartenkopf sind ein anderes Maß als die Felder; gerechnet wird mit den Gebäudehaufen. Der Frage-Agent hat einen früheren Stand gesehen, nicht diesen.

## Belege

Alle in `data/research/auge_plan/lauf_s_plan/`:

| Datei | Was | Befehl |
|---|---|---|
| `karte_flaeche.txt`, `karte_zellen.json` | Fläche der Karte, ebene Quadrate | `karte_flaeche.py` |
| `zellen_je_art.txt`, `.json` | Zellen je Versuchsart, Editor und Gefecht | `zellen_je_art.py` |
| `tabellen.txt` | Leben, Tempo, Maske, Schaden, Reichweite, Laufen, Schlagen, Gebäude | `tabellen.py` |
| `kampf_takt_t9.txt` | Trefferrhythmus und Katapult aus Lauf K | `kampf_takt.py t9` |
| `alte_schuesse.txt` | Trefferquote stehendes Ziel 17.10., erster Treffer in den Duellen 18.10. | `alte_schuesse.py` |
| `spielart_im_code.txt` | Spielart im Kampfcode, Prüfrunde, Haltung, UCP-Stellen | `spielart_im_code.py` |
| `rechnung_dauer.txt` | Obergrenzen, mit Liste des Ungemessenen | `rechnung_dauer.py` |
| `punkte_zuteilung.csv`, `.txt` | Welcher Punkt wo | `punkte_zuteilung.py` |
