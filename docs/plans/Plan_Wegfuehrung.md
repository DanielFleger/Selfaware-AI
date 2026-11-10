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
     - **Gefahr am Standplatz** (ein gegnerischer Schütze erreicht ihn, `schussfeld.gefahr_am`) → Status `gefahr`, kein Befehl;
       das Modul wählt ein anderes Ziel. Ausnahme nur für Zwecke, die Daniel ausdrücklich freigibt (keiner bis jetzt).
   - Gibt `{nr: status}` zurück: `unterwegs`, `greift_an`, `gefahr`, `ziel_weg`.
2. **Umzug der Module**, je eins mit Test: Brandtrupp (Sklaven), Reiterjagd (Berittene), Vorstoß (Bogenschützen), danach
   Nahkampf-Raid, Assassinen, Feldzug, Wächter und die Stellen im Lenker. Ihre Zielwahl bleibt, nur der Weg geht an die Wegführung.
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
| nächster Schritt | **Brandtrupp umziehen**: eine gemeinsame `Wegfuehrung` je Partie im Raid-Einsatz (`baukasten/raid.py`), an Brandtrupp, Reiterjagd, Vorstoß und Nahkampf-Raid gegeben; jedes Modul ruft je Einheit `fuehre(...)` und liest `status(...)` der Vorrunde (gefahr/kein_weg/ziel_weg -> anderes Ziel); der Raid-Einsatz ruft `weg.schritt(L, G, befehl)` einmal je Runde nach den Modulen. Eigene Angriffs- und Ausweichbefehle der Module nur noch ohne Wegführung (alte Tests). Danach Reiterjagd, Vorstoß, Sperrtest, Wache F5, Sandkasten-Beleg, Partie mit Wache. | offen |
