# Warum Lauf F gescheitert ist (B-142, 02.11.2026)

Erstellt: 02.11.2026. Lauf: `laeufe/lauf_f_20261102_184744.*`. Daniel: "Erkläre, warum dein Run scheitert, solange bis du keinen Grund mehr findest und alles kontrolliert ist."

Marken: **gemessen** (Speicher, Aufzeichnung, Log), **Code** (Ghidra-Export), **abgeleitet** (aus Gemessenem gerechnet), **offen**.

## Ursachenkette

| Befund im Lauf | Warum | Warum dahinter | Marke | Beleg |
|---|---|---|---|---|
| 51 Gebäudearten "nicht gesetzt" | Das Programm probierte nur 12 feste Stellen um die Burg | `kandidaten(hoechstens=12)` war mein Wert ohne Grund, statt das Spiel zu fragen | gemessen | von 686 Befehlen: 12 gebaut, 510 auf schon bebauter Stelle, 129 vom Spiel an freier Stelle abgelehnt, 31 Sonderregeln (siehe unten), 4 Burgsuche; `warum_bauen.py` |
| Kalender stand (Jahr 1196, Monat 1, Woche 1) | Anzeige 20 (`DEID_KEEP_AND_GRANERY_PLACEMENT_INFO`) stand auf 2, dann läuft die Woche nicht | Kornspeicher fehlte, weil er zu den 51 gehörte | gemessen + Code | Speicher: Anzeige 20 = 2; `updateDateAndTime`; Probe: Kornspeicher steht -> Anzeige 0, Woche läuft |
| Waren fielen bei Takt 4.893 von 50 auf 0 | Das Modul schreibt `currentResources`, das ist nur die Summe der Lager | Erste Einbuchung ins Lager ruft `countPlayerResources`, das zählt aus den echten Lagern neu; Gold (Nummer 15) nimmt es aus | gemessen + Code | `zeitreihe.jsonl`: Takt 4.888 Burg + 4 Lagerfelder, Takt 4.893 alle Waren 0, Holz 1 |
| "Lagerplatz 4 stehen" trotz "nicht gesetzt" | Die 4 Lagerfelder legt die Burg selbst an, im selben Takt 4.888 | Meine 12 Befehle haben kein einziges Lagerfeld gebaut | gemessen | `bauten.json`: Nr. 12 bis 15, Takt 4.888 |
| Abschnitte meldeten "ok" | "ok" hieß nur: kein Fehler beim Absetzen | Keine Wirkungsprüfung, kein Abbruch | Code | `auge_lauf_f.py` |
| Tempo 1000 erreicht nur 825 Takte je Sekunde | Das Spiel rechnet höchstens 11 Takte je Bild und läuft mit 75 Bildern je Sekunde | Nicht das Lesen: ohne Lesen ebenfalls 825. Woher die 75 kommen: offen | gemessen | Log: 600 Bilder in 8,004 s, 6.600 Takte |
| Wache meldete 37,7 statt 40 Takte je Sekunde | Der Median misst einzelne Takt-Abstände; Takte liegen auf Bildgrenzen (13,33 ms), meist 26,67 ms Abstand = 37,5 | Gesamt über die Stufe gemessen: 40,0. Kein Fehler im Spiel, nur meine Messart | gemessen + abgeleitet | `voll_tempo40.auge`: Median 37,6, gesamt 40,0 |
| Auf Tempo 1000 fehlen Takte | Lesen dauert länger als ein Takt, 11 Takte kommen gebündelt je Bild | Auf der Tempostufe 1000 gelesen: 27 % der Takte. Im ganzen Lauf meldete die Wache zuletzt 92.559 fehlende Takte und 66.356 gemischte Rahmen | gemessen | `voll_tempo1000.auge`, Wache im Protokoll |

Sonderregeln der 31 Befehle (Spielprüfung, gemessen an der Karte): Eisenmine und Pechgräber nur auf ihrem Boden, Lagerfeld und Waffenlager nur neben dem vorhandenen.

## Eigene Fehler, die dabei auffielen

- **"Spiel angehalten" war falsch.** TaskStop beendete nur die Hülle, das Python-Programm lief weiter, hob die Pause um 18:54:45 auf und fuhr die Tempotreppe zu Ende. Das Spiel lief bis 19:01:02 auf Tempo 1000, und die Sperre war in dieser Zeit schon frei. Log: `ucp3.log`. Seit 19:01:02 steht es, nachgeprüft (Takt ändert sich nicht).
- **Bauten mit Drehwert 0.** Alle Bau-Befehle des Laufs und der Proben tragen Drehung 0. Wissensstand 13y sagt: Normale Gebäude brauchen 15, sonst stimmt das Bild in zwei von vier Ansichten nicht. Das hatte ich beim Bau des Programms nicht beachtet.
- **Vermutung `recomputePlayerDataStocks...` war falsch.** Die läuft nur beim Monatswechsel, der kam nie. Richtig ist `countPlayerResources`.
- **Vermutung "Handel wirkungslos" war falsch.** Kaufen und Verkaufen wirkten, auch ohne Marktplatz (Takt 91.636: Gold -180, Bogen +5).

## Wirkung je Abschnitt (neue Felder in der Aufzeichnung, `wirkung.py`)

| Abschnitt | Wirkung | Marke |
|---|---|---|
| vorrat | nur Gold blieb, Waren überschrieben | gemessen |
| burg | Burg + 4 Lagerfelder, 243 neue Felder | gemessen |
| bauen | 12 Gebäude, 220 neue Felder | gemessen |
| warenketten | **0 neue Felder**, nichts passiert (keine Farmen, keine Waren) | gemessen |
| handel | wirkt | gemessen |
| steuern | Einstellung gesetzt; Wirkung über Zeit nicht zu sehen, Kalender stand | gemessen |
| mauern | Mauerbit auf (236,212) gesetzt, Tore 0 | gemessen |
| anwerben | Söldner angeworben; Kaserne fehlte, Armee nur teilweise | gemessen |
| abreissen | 5 Gebäude + 3 Teile weg | gemessen |

## Proben im eigenen Spiel, mit Vorhersage vorher

| Vorhersage | Ergebnis | |
|---|---|---|
| Kornspeicher auf erlaubter Stelle steht nach höchstens 6 Takten | steht, kostet 5 Holz | bestätigt |
| Kalender bleibt trotzdem stehen, weil der Reiter im Baumenü gleich bleibt | Anzeige 0, Reiter wechselt selbst, Woche läuft (3 Wochen in 600 Takten) | **widerlegt**: Kornspeicher allein genügt |
| Kaserne steht trotz 0 Stein | steht, Stein bleibt 0 (Spielbefehl prüft im Einzelspiel keine Kosten, das macht nur das Menü) | bestätigt |
| Stein über `startResources` fließt mit 1 je 4 Takte | Stein blieb 0 | **widerlegt**: alle 4 Lagerfelder hielten Holz, ein Lagerfeld nimmt nur eine Ware |
| Mit neuem Lager fließt der Stein | 100 Stein da (48 + 48 + 4 auf den neuen Feldern) | bestätigt |
| Jede fehlende Art steht auf erlaubter Stelle, nur der Pechgräber nicht | 51 von 53 stehen; Pechgräber 0 erlaubte Stellen; Pechgraben fehlte in der Gebäudeliste | fast bestätigt |
| (Nachprobe) Pechgraben steht in eigener Liste `pitchDitches` | Eintrag bei (222,221), Bit 8 im Feld gesetzt | bestätigt: **meine Prüfung sah in der falschen Liste nach** |

Damit in dieser Probe: 52 Arten auf erlaubter Stelle, alle 52 gebaut. Die 53. Art hatte keine erlaubte Stelle.

## Daraus abgeleitet

- Ein Spieljahr sind 9.600 Takte (200 je Woche, 4 Wochen je Monat, 12 Monate; Woche gemessen, Rest Code). Der Lauf hatte 284.885 Takte, ohne dass je ein Monat um war.
- Ein Lager-Befehl legt 4 Lagerfelder an, je Feld gemessen höchstens 48 (Stein, Holz). Waren über `startResources` brauchen also je Ware mindestens ein freies Feld.

## Offen

1. **129 Befehle an damals freien Stellen:** Das Spiel lehnt sie heute ab, aber die Stellen sind inzwischen überbaut. Warum es sie damals ablehnte, lässt sich an diesem Spielstand nicht mehr zeigen. Der gemeldete Grund ist unzuverlässig, weil das Spiel ihn nicht zurücksetzt. Kein Fall ist bekannt, in dem eine erlaubte Stelle scheiterte. Schließt sich im neuen Lauf: Vor jedem Bau fragt das Programm das Spiel und bricht ab, wenn "erlaubt" nicht zu "steht" führt.
2. **Woher die 75 Bilder je Sekunde kommen.** Sie begrenzen das Tempo auf 825.
3. **Jeden Takt sehen auf Tempo 1000:** von außen gemessen nur 27 %, weil 11 Takte gebündelt je Bild kommen. Ob es von innen geht, im Takt des Spiels, ist nicht geprüft.
4. Karte "Eine prächtige Oase" ist nur per Ausschluss belegt; `KARTENNAME` bleibt im Burgenbau leer.
5. Pechgräber: In diesem Spielstand erlaubt die Spielprüfung 0 von 160.000 Stellen. Gehört in Lauf K oder S auf eine Karte mit Pechboden.

## Wiederholen

Aus dem Repo-Stamm, Spielstand nötig nur für die Proben:

```
python data/research/auge_plan/ursachen_lauf_f/zeitreihe.py <aus.jsonl>
python data/research/auge_plan/ursachen_lauf_f/bauten.py <aus.json>
python data/research/auge_plan/ursachen_lauf_f/warum_bauen.py <bauten.json> <platz_alle.json>
python data/research/auge_plan/ursachen_lauf_f/wirkung.py <aus.json>
```

## Nachtrag: Bauern, Beliebtheit, Treppe (02.11.2026, 19:18)

- **gemessen:** 1 neuer Bewohner je rund 250 Takte (Takte 5.126, 5.378, 5.628 ...) bei Beliebtheit 87,75 und freiem Wohnplatz. Deckel: 10 mit Burg, 18 nach der ersten Hütte. Im Lauf blieb es bei 18 Leuten.
- **gemessen:** Die Spieltabelle (`DAT_EmployeeCountPerBuildingType`, 0x005B8B58, je Typ 4 Bytes) nennt für die 63 Arten des Laufs 34 Arbeitsplätze. Alle zu besetzen braucht bei 1 je 250 also 8.500 Takte (**abgeleitet**). Selbst mit allen Gebäuden wären die meisten mit 18 Leuten leer geblieben.
- **gemessen:** Beliebtheit stand im Lauf durchgehend bei 87,75, weil der Kalender stand. Nach dem Kornspeicher der Probe war sie 3.480 Takte später 0. Zuletzt im Lauf aufgezeichnet: Essen -250, Steuer +25. **vermutet:** Es liegt am fehlenden Essen, nicht geprüft.
- **gemessen:** Die volle Tempotreppe meldete "bestaetigt", obwohl Stufe 1 nur 1 Takt hatte, weil das Spiel dort durch meine Pause stand. Das ist ein hohles Grün: `a4_tempotreppe` muss eine Stufe mit zu wenig Takten als "nicht gemessen" führen.
- **gemessen:** Jeden Takt gelesen auf Tempo 40 (201 von 201). Auf Tempo 100 fehlen 2 von 498, auf 200 fehlen 262 von 1.000.
- **gemessen:** Längste Lücke bis zum nächsten neuen Takt in der Aufzeichnung: 0,098 s.
