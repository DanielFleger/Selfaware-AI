# Plan Wegführung für alle Einheiten (B-182)

Erstellt: 11.11.2026 00:06 (SRE)

## Auftrag

Daniel 10.11. 23:42: „alle s klaven laufen einfach in den sicheren tod ohne rücksicht auf verluste ich dachte wir haben pathing schon gemacht?“
Daniel 11.11. 00:01: „warum nur für sklaven das hört sich schon ieder so an als würdest du das nur für eine einheit machen.“
Daniel 11.11. 00:04 auf den Vorschlag „gemeinsame Wegführung für jede Einheit, die wir bewegen“: „Ja, so bauen“.

## Ziel

Jede eigene Einheit, die ein Modul zu einem Ziel schickt, läuft über **eine** Stelle: die Wegführung. Die Module sagen, **was** sie wollen
(dieses Gebäude, diesen Arbeiter, diesen Ort), die Wegführung entscheidet, **wie** die Einheit hinkommt. Kein Modul gibt mehr selbst
einen Lauf- oder Angriffsbefehl zu einem Ziel.

## Regeln des Spiels, gemessen (nicht änderbar, darum herum bauen)

- Ein Fernkämpfer mit Angriffsziel außer Reichweite bekommt **keinen Weg** und bleibt stehen (S114: Berittener, Ziel in 155 Feldern;
  Lauf 1 vom 10.11.: Bogenschützen bei 40,9 bis 46 Feldern Luftlinie). Mit Ziel in 33 Feldern schießt er.
- Schießen prüft die **Luftlinie**, Bögen bis 40 Felder (S9, `services/spielwerte.erfassen`).
- Nahkämpfer mit Gebäudeangriff bekommen einen Weg und laufen (S114: Sklave, Arabischer Schwertkämpfer, Weg 146 Felder).
- Ein Laufbefehl (`angriff` mit `lauf`) bewegt jede Einheit (Flucht der Reiterjagd, Vorstoß, Wegpunkte des Nahkampf-Raids).
- Zwei Gruppenbefehle im selben Takt können verschmelzen (S57) – die Wegführung gibt Einzelbefehle je Einheit.
- Das Spiel vergibt Nummern toter Einheiten neu (Fehlerwache 10.11.) – ein Ziel gilt nur, solange seine Nummer dieselbe Art und denselben
  Besitzer trägt.

## Bau

1. **`micro/wegfuehrung.py`, Klasse `Wegfuehrung(sp, gelaende)`** (neu geschrieben, Muster aus `micro/tasks/nahkampf.py`):
   - `fuehre(nr, ziel, zweck)` – Ziel ist `("einheit", nr)`, `("gebaeude", nr)` oder `("ort", (x, y))`; merkt den Auftrag.
     `loslassen(nr)` beendet ihn.
   - `schritt(L, G, befehl)` je Runde, für jede geführte Einheit:
     - Ziel weg oder Nummer neu vergeben → Status `ziel_weg`, kein Befehl.
     - **In Reichweite** → Angriffsbefehl: Fernkämpfer, wenn die Luftlinie zum Ziel höchstens Reichweite minus 2 ist;
       Nahkämpfer und Gebäudeangriffe, wenn das Ziel höchstens 4 Felder (Schach) entfernt ist (wie Brandtrupp und Nahkampf-Raid).
     - **Sonst laufen**: Standplatz ist bei Fernkämpfern der Punkt in Reichweite minus 4 vor dem Ziel, bei Nahkämpfern das Ziel.
       Weg mit `services/schussfeld.sicherer_weg`, Laufbefehl zum nächsten Wegpunkt. Neu geplant wird, wenn der Weg älter als
       `NEU_PLANEN` Runden ist oder das Ziel weitergezogen ist.
     - **Gefahr am Standplatz** (ein gegnerischer Schütze erreicht ihn mit freier Linie, `wegfuehrung.Gefahr` seit 11.11. 21:50)
       → Status `gefahr`, kein Befehl;
       das Modul wählt ein anderes Ziel. Ausnahme nur für Zwecke, die Daniel ausdrücklich freigibt (seit 11.11. 19:40 nur der
       Nahkampf-Raid, siehe Stand).
   - Gibt `{nr: status}` zurück: `unterwegs`, `greift_an`, `gefahr`, `ziel_weg`.
2. **Umzug der Module**, je eins mit Test: Brandtrupp (Sklaven), Reiterjagd (Berittene), Vorstoß (Bogenschützen), danach
   Nahkampf-Raid, Deckung (Schleuderer; nachgetragen 11.11. 19:55, der Sperrtest fand sie), Assassinen, Feldzug, Wächter und die
   Stellen im Lenker. Ihre Zielwahl bleibt, nur der Weg geht an die Wegführung.
3. **Sperrtest** `tests/test_wegfuehrung_sperre.py`: zählt jeden Lauf- oder Angriffsbefehl außerhalb der Wegführung. Erlaubt sind nur
   aufgezählte Stellen mit Grund (Flucht, Halten, Graben, Abwehr am eigenen Lord). Die Zahl der übrigen Stellen darf nur sinken,
   bis sie 0 ist.
4. **Fehlerwache F5 „stirbt ohne Wirkung“**: Ein beobachteter Söldner stirbt, ohne je gekämpft zu haben (kein Schuss, kein Nahkampf,
   nicht am Gebäude) – Fehler, Partie anhalten.
5. **Prüfen**: je Regel ein Test mit Gegenprobe; danach eine Partie mit Wache nach Daniels Ablauf (bis zum ersten Fehler, beheben,
   neu starten).

## Nachtrag 11.11. 00:07: Daniels Anforderungen

- „was genau ist ein sicherer weg?“ - **Definition**: der Weg zum Ziel, auf dem die Einheit am wenigsten in die Reichweite
  gegnerischer Waffen kommt; unter gleich sicheren Wegen der kürzeste. Liegt das Ziel selbst in Gefahr, ist kein Weg sicher - dann
  gilt ein Standplatz in eigener Reichweite außerhalb der feindlichen, oder ein anderes Ziel.
- „er sollte immer adjustieren sollte im lauf eine gefahr in den weg kommen ... es sollte nicht einfach nur mit einem befehl im
  stich gelassen werden.“ - **Neu rechnen jede Runde**, solange die Wegführung die Einheit führt, gegen die aktuelle Lage.
- „das sollten doch alle einheiten knenne genauso wie die aktuelle position aller arbeiter/einheiten sowie terrain“ - **eine
  Gefahrenkarte für alle**: alle sichtbaren gegnerischen Einheiten (Fernkämpfer mit Reichweite, Nahkämpfer mit ihrem Bereich),
  Türme, Gelände (FAIRNESS R3, F9, F11 erlauben alles Sichtbare). **Fallgruben** nur, wenn sie für einen Spieler sichtbar sind -
  das ist nicht festgehalten; Frage an Daniel. Hinweis: `raids.gefaehrlich` nutzt gegnerische Gruben schon heute.

## Nachtrag 11.11. 00:07: Antworten auf den Frage-Agenten (Ampel gelb)

1. **Gefahr am Standplatz lässt die Einheit nicht stehen.** Erst sucht die Wegführung einen anderen Standplatz in eigener
   Reichweite außerhalb der feindlichen (Bögen 40 gegen Schleuderer 22 geht, gegen Bögen 44 nicht). Gibt es keinen, meldet sie
   `gefahr`, das Modul wählt ein anderes Ziel; gibt es keins, wartet die Einheit an einem sicheren Sammelplatz. Türme, Nahkämpfer und
   die Deckung (B-129, Daniel 19.10.) kommen aus `raids.gefaehrlich` in dieselbe Gefahrenkarte.
2. **Ein Führer je Einheit.** Solange die Wegführung eine Einheit führt, gibt ihr kein Modul und kein Kernweg Befehle; das Ausweichen
   im Zickzack (Kern) ruft die Wegführung selbst, wenn die Einheit unter Beschuss gerät. Budget: höchstens 8 Einzelbefehle je Runde
   (S82), dringende zuerst, gesendet nur bei Änderung. Ohne Wegpunkte (gerader Weg nicht gefährlicher) läuft die Einheit direkt zum
   Standplatz.
3. **Beleg vor dem Umzug:** Sandkasten auf Instanz 2 wie S114 - ein Berittener und ein Bogenschütze werden aus 150 Feldern geführt;
   Erfolg = Standplatz erreicht, Schussziel gesetzt, Leben des Ziels sinkt. Die Abstände (Reichweite minus 2 und minus 4) sind
   Startwerte und werden dort gemessen. „Steht und schießt nicht“ fängt die Wache mit F2.

## Nachtrag 11.11. 20:45: Gefahr mit Schusslinie und Tarnung (gebaut 11.11. 21:50, siehe Stand)

Daniel 11.11. 20:30 auf meine Erklärung, der tote Winkel seien die Lücken zwischen den Reichweiten und die Tarnung rechne der Code
nicht ein: „tarnung ist doch DAS ding von Assassinen“; „toter winkel hat JEDE einheit, wie wurde denn sonst bisher die
Gefahrenberechnung gemacht? wurde es einfach so behandelt als gäbe es kein Terrain/Gebäude?“

**Befund (nachgesehen 20:40):**
- Meine Aussage war falsch: Die Assassinen rechnen seit 17.10. mit Tarnung und Schusslinie (`services/sicht.py`, über
  `schussfeld.Gitter(..., sicht=...)`): Ein Schütze nimmt eine Assassine nur, wenn sie höchstens ~20 Felder von einem wählbaren
  Feind steht (L75, abgelesen in acquireShootTarget), und nur mit freier Linie - ein nicht flaches Gebäude dazwischen sperrt, wer
  auf Turm, Torhaus oder Bergfried steht, schießt frei (L79). Gemessen 17.10.: 1,352 Leben je Takt bei freier Linie, 0,070 bei
  versperrter.
- Die Wegführung (Sklaven, Reiter, Bogenschützen, Nahkampf-Raid) rechnet dagegen nur Kreise um jeden Schützen, dazu Kreise um
  Türme und Nahkämpfer. Gelände zählt nur für die Begehbarkeit; Gebäude, Höhe und Tarnung zählen nicht. Genauso grob: die Zielwahl
  von Brandtrupp und Reiterjagd (`raids.gefaehrlich`, Quadrat), der Vorstoß (`_schussfeld`, Quadrat) und die Deckung in der
  Wirkungsrechnung (`spielwerte.in_gefahr`, Kreis). Auch S115 (99 % der Ziele in Gefahr) ist mit Kreisen gezählt.
- Mauern fehlen überall, auch in `sicht.py` (S63: ein Pfeil, der an eine Mauer fliegt, trifft nicht mehr). Die Karte, mit der wir
  rechnen, ist die Rohstoffkarte vom Partiebeginn - darin stehen noch keine Mauern.

**Bau (Vorschlag):**
1. Die Wegführung rechnet je Runde eine `sicht.Lage`. Gefahr an einem Ort = gegnerische Schützen in Reichweite
   (`spielwerte.gefahr`) mit freier Linie (`Lage.linie_frei`, erhöhte Schützen immer frei); für Assassinen nur, wenn sie sichtbar
   wären (`Lage.sichtbar` mit Rand). Nahkämpfer wie bisher.
2. Türme zählen nicht mehr selbst, sondern die Schützen darauf (erhöht, freie Linie). Zu prüfen: Belagerungsgeräte auf Türmen
   (Ballista 68 Felder, S9) stehen bisher in keiner Gefahrenliste.
3. Gitter: Gefahr je Zelle nach derselben Regel, nur Zellen in Reichweite eines Schützen.
4. Tests mit Gegenprobe: Gebäude zwischen Schütze und Ziel - keine Gefahr; erhöhter Schütze - Gefahr; Assassine außer Sicht - keine
   Gefahr. Danach S115 mit derselben Regel neu zählen.
5. Später, eigener Schritt: dieselbe Regel für `raids.gefaehrlich`, den Vorstoß und die Wirkungsrechnung; Mauern über die Höhe der
   Mauerkacheln im laufenden Spiel (erst messen).

## Nicht dazu

Zielwahl der Module, Kauf nach Wirkung, Eichung, Obergrenze.

## Offen, nicht gemessen

- Ab welcher Entfernung zwischen 33 und 155 Feldern ein Fernkämpfer keinen Weg mehr bekommt. Für die Wegführung ist das egal:
  Sie führt ihn immer erst bis in Reichweite.
- `NEU_PLANEN` (Runden) ist ein selbst gesetzter Startwert.
- Gefahr durch getarnte Assassinen (schussfeld.py: „ungemessen“).

## Stand

| Zeit | Schritt | Ergebnis |
|---|---|---|
| 11.11. 00:06 | Plan geschrieben, Frage-Agent beauftragt | Ampel gelb, drei Fragen beantwortet (Nachtrag 00:07) |
| 11.11. 00:07 | Daniels Anforderungen eingearbeitet (Definition, Neu rechnen jede Runde, alles Sichtbare) | Frage offen: Fallgruben sichtbar? |
| 11.11. 00:12 | Daniel 00:10: „das einzige was verborgen ist sind holfallen und wo das pech ist“ - als FAIRNESS F12 eingetragen; `raids.gefaehrlich` las gegnerische Fallgruben (Verstoß gegen R3), herausgenommen, Test mit Gegenprobe | erledigt |
| 11.11. 00:25 | **Kern gebaut**: `micro/wegfuehrung.py` - Gefahrenkarte jede Runde aus allen sichtbaren Schützen, Nahkämpfern und Türmen (keine Fallen, F12); Standplatz in Reichweite, bei Gefahr der sicherste auf dem Kreis um das Ziel, sonst `gefahr` ohne Befehl; neu geplant, sobald auf dem restlichen Weg mehr Gefahr liegt als beim Planen; Angriff erst in Reichweite; höchstens 8 Befehle je Runde. 8 Tests (`tests/test_wegfuehrung.py`), Gegenproben: Nachsteuern aus, Gefahr am Standplatz aus, Budget aus - je rot. Noch kein Modul umgezogen. | erledigt |
| nächster Schritt | **Brandtrupp umziehen**: eine gemeinsame `Wegfuehrung` je Partie im Raid-Einsatz (`baukasten/raid.py`), an Brandtrupp, Reiterjagd, Vorstoß und Nahkampf-Raid gegeben; jedes Modul ruft je Einheit `fuehre(...)` und liest `status(...)` der Vorrunde (gefahr/kein_weg/ziel_weg -> anderes Ziel); der Raid-Einsatz ruft `weg.schritt(L, G, befehl)` einmal je Runde nach den Modulen. Eigene Angriffs- und Ausweichbefehle der Module nur noch ohne Wegführung (alte Tests). Danach Reiterjagd, Vorstoß, Sperrtest, Wache F5, Sandkasten-Beleg, Partie mit Wache. | **Brandtrupp erledigt 11.11. 00:35**: gemeinsame Wegführung im Raid-Einsatz; der Brandtrupp gibt keine eigenen Befehle mehr, bei gefahr/kein_weg/ziel_weg sperrt er das Gebäude für 10 Runden (Startwert) und nimmt ein anderes. Test mit Gegenprobe. Offen: Reiterjagd, Vorstoß, Nahkampf-Raid, Sperrtest, F5, Sandkasten, Partie. |
| 11.11. 00:40 | **Reiterjagd und Vorstoß umgezogen** (Daniel 11.11. 00:25: „mach weiter mit reiterjagd und vorstoß“): Berittene Bogenschützen (A_HARCHER 74) und Bogenschützen des Vorstoßes (E_ARCHER 22, Typ 23, A_ARCHER 70) bekommen keine eigenen Angriffsbefehle mehr, die Wegführung führt jeden bis in seine Reichweite (S114: ein Angriffsbefehl auf ein fernes Ziel bewegt einen Fernkämpfer nicht). **Reiterjagd**: meldet die Wegführung `gefahr` oder `kein_weg`, gibt der Reiter den Arbeiter ab und nimmt einen anderen; die Sperre (10 Runden, Startwert) gilt nur für diesen Reiter. Ein Abschuss zählt nur noch, wenn dieser Reiter in Reichweite auf das Opfer angesetzt war (S110: vorher zählte jeder verschwundene Arbeiter) - ob sein Pfeil traf, prüft weiter die Wache (F4). Flucht vor Nahkämpfern bleibt bei der Reiterjagd, die Wegführung lässt den Reiter dafür los. **Vorstoß**: vor eigenem Vorrücken, Ausweichen und Abziehen, beim Alarm an der Burg und am Ende lässt die Wegführung die Schützen los, der Zickzack des Kerns gibt sie vorher her; melden alle Schützen `gefahr` oder `kein_weg`, gibt er das Ziel ab. **Wegführung**: gleiche Befehle mehrerer Einheiten (selbes Ziel, selber Wegpunkt) gehen als ein Befehl hinaus wie beim Vorstoß bisher - ob ein Gruppenbefehl so schnell ankommt wie ein Einzelbefehl, ist ungemessen; eine wiedervergebene Nummer wird neu geführt, wenn das Modul sie will. 9 neue Tests, 13 Gegenproben (jede neue Regel einzeln abgeschaltet) je rot; drei Wirkungstests der Reiterjagd (`tests/test_wirkung.py`) prüfen die Zielwahl jetzt über die Wegführung, gleiche Erwartungen, Gegenprobe rot. (Berichtigt 00:50: in der Commit-Nachricht bb6df41 steht falsch 8.) | erledigt |
| nächster Schritt | Nahkampf-Raid umziehen; dann Sperrtest, Wache F5 („stirbt ohne Wirkung“), Sandkasten-Beleg auf Instanz 2 (geführte Schützen und Reiter erreichen den Standplatz und das Leben des Ziels sinkt), danach eine Partie mit Wache - Sandkasten und Partie nur mit Daniels Ja. | **Nahkampf-Raid erledigt 11.11. 01:00** (nächste Zeile); der Rest offen |
| 11.11. 01:00 | **Nahkampf-Raid umgezogen** (Daniel 11.11. 00:48 auf die Frage, ob ich als Nächstes den Nahkampf-Raid umziehen soll: „Ja, Nahkampf-Raid“): Er wählt das Ziel weiter nach Wirkung (`baukasten/wirkung.py`), Weg und Befehle kommen von der Wegführung; der einmal berechnete Weg (`schussfeld.sicherer_weg`) entfällt mit ihr. Bei `gefahr` oder `kein_weg` nimmt die Einheit ein anderes Ziel (Sperre 10 Runden nur für sie); ein Erfolg zählt nur nach `greift_an` am Ziel, eine wiedervergebene Nummer gilt als gefallenes Ziel. Nebenbei behoben: Ziele toter Teilnehmer blieben belegt - für die anderen Teilnehmer und für den Kauf (Lenker `belegt_r`). **Gemessen dabei (S115):** 793 von 803 Zielen des Nahkampf-Raids vom 10.11. lagen bei der Zuweisung in Gefahr nach der Regel dieser Wegführung, weil sein Standplatz das Ziel selbst ist; ein freies Ziel mit Wirkung gab es daneben in 429 von 803 Fällen, meist nur eins (Median 1). Ohne Freigabe weicht er also auf wenige freie Ziele aus oder wartet (berichtigt 01:03: zuerst stand hier „greift fast nichts an“ - das war nicht gezählt). Die Freigabe ist ein Schalter (`baukasten/raid.py` `TROTZ_GEFAHR`, steht auf leer) und **liegt Daniel als Frage vor**. 6 neue Tests, 9 Gegenproben je rot. | erledigt; Frage beantwortet 11.11. 19:40 (übernächste Zeile) |
| nächster Schritt | Daniels Antwort zur Freigabe des Nahkampf-Raids einbauen; dann Sperrtest, Wache F5 („stirbt ohne Wirkung“), Sandkasten-Beleg auf Instanz 2, danach eine Partie mit Wache - Sandkasten und Partie nur mit Daniels Ja. Ebenfalls offen aus dem Plan: der sichere Sammelplatz für Einheiten ohne Ziel (Nachtrag 00:07, Punkt 1) - bis jetzt behalten sie ihren letzten Befehl. | **Freigabe erledigt 11.11. 19:45** (nächste Zeile); der Rest offen |
| 11.11. 19:45 | **Freigabe Nahkampf-Raid**: Daniel 11.11. 19:40 auf die Frage „Darf der Nahkampf-Raid Ziele unter Beschuss angreifen?“: „Gerne freigeben“. `baukasten/raid.py` `TROTZ_GEFAHR = ("nahkampfraid",)`: Am Ziel greift er auch unter Beschuss an; den Weg dorthin führt die Wegführung weiter um Gefahr herum, seine Zielwahl nach Wirkung zieht den Beschuss am Ziel ab. Nur er (Grundgesetz P1.37: die Antwort gilt im Rahmen ihrer Frage) - Brandtrupp, Reiterjagd und Vorstoß bleiben ohne Freigabe. Test mit Gegenprobe. Nebenbei nach P1.37 die Frage zu zwei Zitaten nachgetragen („Ja, Nahkampf-Raid“, „Ja, so bauen“). | erledigt |
| nächster Schritt | Sperrtest, Wache F5 („stirbt ohne Wirkung“), Sandkasten-Beleg auf Instanz 2, danach eine Partie mit Wache - Sandkasten und Partie nur mit Daniels Ja. Offen aus dem Plan: der sichere Sammelplatz für Einheiten ohne Ziel (Nachtrag 00:07, Punkt 1). | **Sperrtest erledigt 11.11. 19:55** (nächste Zeile); der Rest offen |
| 11.11. 19:55 | **Sperrtest gebaut** (`tests/test_wegfuehrung_sperre.py`; Daniel 11.11. 19:47 auf die Frage „Als Nächstes den Sperrtest bauen?“: „Ja, Sperrtest“): Im Live-Code (ohne `tools/`, ohne die Kanäle zum Spiel und zum Kern) bauen 37 Stellen selbst einen Lauf-, Angriffs- oder Zickzack-Befehl. **9 sind erlaubt** und im Code mit `# Wegfuehrung frei: <Grund>` markiert: Flucht 5 (Reiterjagd, Assassinen, Vorstoß weichen und abziehen, Wächter-Schützen), Abwehr am eigenen Lord 3 (Wächter-Schild, Sammeln am Bergfried, Lordwache), Graben 1. **28 stehen in der Altliste**, die nur kürzer werden darf (`HOECHSTENS`): Assassinen 9, alter Weg ohne Wegführung 7 (Nahkampf-Raid 3, Brandtrupp 2, Reiterjagd 1, Vorstoß-Schuss 1 - im Spiel setzt der Raid-Einsatz die Wegführung immer), Feldzug 5, Deckung 2, Vorstoß-Vorrücken und Zickzack 2, Wächter 2, Lenker 1. **Neu gefunden:** Die Deckung der Schleuderer (A_SLINGER 72) gibt eigene Befehle und stand in keiner Umzugsliste - oben nachgetragen. 6 Gegenproben je rot (neue Stelle ohne Grund, fehlende Markierung, Grund nicht im Plan, verschwundene Stelle bei ungekürzter Liste, Höchstzahl, blinder Sammler). | erledigt |
| nächster Schritt | Altliste abbauen, Vorschlag der Reihenfolge: alter Weg ohne Wegführung (7, nur alte Tests umstellen), Deckung (2), Vorstoß-Vorrücken (2), Wächter (2), Feldzug (5), Assassinen (9), Lenker (1). Dann Wache F5 („stirbt ohne Wirkung“), Sandkasten-Beleg auf Instanz 2 und eine Partie mit Wache - Sandkasten und Partie nur mit Daniels Ja. Offen: der sichere Sammelplatz. | **vorgezogen: Gefahr mit Schusslinie 11.11. 21:50** (nächste Zeile); der Rest offen |
| 11.11. 21:50 | **Gefahr mit Schusslinie und Tarnung gebaut** (Daniel 11.11. 21:32 auf die Frage „Erst die Gefahrenrechnung umbauen, dann Wächter und Vorstoß?“: „Ja, erst Gefahr“): `wegfuehrung.Gefahr` nutzt die Regeln aus `sicht.py` für Standplatz und Wegegitter - ein Schütze zählt nur mit freier Linie (ein nicht flaches Gebäude dazwischen sperrt, erhöhte Schützen schießen frei), eine Assassine nur, wenn sie sichtbar wäre (L75); leere Türme zählen nicht mehr, die Schützen darauf schon; das Zielgebäude sperrt keine Linie zu sich selbst. Fallgruben gelten als flach: in `sicht.py` nachgetragen - dort zählte eine feindliche Grube vorher als Deckung, gegen FAIRNESS F12. Gemessen in 16 Runden einer Partie vom 10.11. (32 Schützen, 111 Gebäude): rund 1 ms je Runde, Gitter rund 7 ms. 5 neue Tests, 2 angepasst (leerer Turm ist keine Gefahr), 7 Gegenproben je rot; `sicht_pruefen` 10 von 10. Nachgezählt (S116): mit Schusslinie lagen weiter 146 von 148 Gebäude- und 638 von 655 Arbeiter-Zielen des Nahkampf-Raids in Gefahr - die Schützen standen frei daneben; freie Ziele mit Wirkung gab es in 556 statt 429 von 803 Fällen. | erledigt |
| nächster Schritt | Wächter und Vorstoß-Vorrücken umziehen (Daniel 11.11. 20:30 auf die Frage „Als Nächstes Wächter und Vorstoß-Vorrücken umziehen?“: „ja gerne“); dann dieselbe Regel für `raids.gefaehrlich`, den Vorstoß (`_schussfeld`) und die Wirkungsrechnung; Mauern über die Höhe der Mauerkacheln (erst messen); Wache F5; Sandkasten und Partie nur mit Daniels Ja. | offen |
