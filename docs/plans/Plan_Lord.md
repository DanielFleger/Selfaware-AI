# Plan: Rotkaeppchens Lord toeten (Stand 05.10.2026, 21:35)

**Handbuch (Daniel 05.10. 23:54: "es soll immer sofort strukturiert eingetragen werden"):** jede neue Messung und jedes
Learning sofort in `Handbuch.html` (Quelle, liegt hier im Projekt) eintragen und als Artifact neu veroeffentlichen:
https://claude.ai/artifact/5Fg23CVXQwntBeSJ8XztYC (aus einer anderen Sitzung mit `url` veroeffentlichen, sonst entsteht ein neues).

Anlass: Daniel 21:30 - "du hast komplett die Kontrolle verloren ... maximal unorganisiert". Zwischen 20:30 und 21:30
neun Aenderungen hintereinander, jeder Fehler erst in einer ganzen Partie gefunden, fast jede Serie mit anderem Code.
Ab jetzt gilt dieser Plan; gebaut wird erst nach Daniels Ja, und dann nur Schritt fuer Schritt.

## NEUE RICHTUNG (Daniel 05.10. 22:09-22:19) - gilt vor allem darunter
Woertlich: "Du solltest dich mehr darauf fokussieren, wie du so schnell wie moeglich am Anfang des Spiels raiden kannst,
dann parallel deine Wirtschaft maximal aufbaust, dann eine Armee aufstellst und mit allen Assassinen moeglichst
gleichzeitig auf den Lord gehst." 22:11: "sobald moeglich anfangen zu raiden ohne Ruecksicht auf Verluste:
1. Soeldnerposten 2. Kornspeicher 3. Markt, Essen verkaufen, Assassinen ausbilden - dann direkt raiden, dabei die
klassische Wirtschaft hoch." (Der Klettertest war unnoetig - Daniel 22:09: "ja koennen sie, glueckwunsch".)

**Schritt R1 - Raid zuerst (gebaut 22:12, Eroeffnung phase1):** Kornspeicher + Markt, ALLES Startessen verkaufen,
Posten, mit dem Rest Assassinen, erst dann die Wirtschaft. (Posten kann nicht vor dem Kornspeicher: 120 Gold, das Gold
kommt nur aus dem Startessen, und das erscheint erst mit dem Kornspeicher.)
Gemessen raidzuerst_1 (Kennung 043d044d, bis Tick 8.000) gegen Serie a (3 Laeufe):
| | Serie a | raidzuerst_1 |
|---|---|---|
| Posten + 1. Assassine | Posten ~833, 1. Raid ~5.930 | beides Tick 737, 1. Raid 1.093 |
| 1. feindliches Gebaeude weg | ~7.750 | 2.007 |
| zerstoert bis 8.000 | 1 | 2 |
| Beliebtheit bei ~7.500 | ~92 | 42 (kein Essen bis ~5.400, nur 1 von 3 Apfelplantagen - Gold 20 nach Posten+Assassine) |
Offen: die Wirtschaft waechst NICHT mit (Daniel fragen, siehe Bericht 22:2x).

**Assassinen-Taktik in drei Stufen (Daniel 22:16 / 22:19):**
- **T1 Ausweichen bei Uebermacht** (gebaut, Abschnitt 4a): mehr feindliche Nahkaempfer als eigene Assassinen im
  Umkreis 5 -> kurz weg, kein Ziel, bis 2 Runden kein Verfolger im Umkreis 10, dann wieder angreifen. Anlass: der erste
  Assassine starb 1 gegen 3 ihrer Verteidigungs-Assassinen (Tick 2.429, Leben 11.720 -> 920 in ~50 Ticks), weil der
  Rueckzug nur Fernkaempfer kannte. Pruefung ohne Spiel `ausweichen_pruefen.py` 5/5 gruen, gegen alten Stand 3 rot.
  Gemessen (je ein Lauf bis Tick 8.000, gleiche Eroeffnung):
  | Lauf | Stand | zerstoert | Assassinen tot | eigene Soldaten tot |
  |---|---|---|---|---|
  | 1 | kein Ausweichen | 2 | 1 | 0 |
  | 2-4 | halten / Laufbefehl je Runde | 2 | 1 | 0 |
  | 5-6 | echter Laufbefehl, frueh (10 Felder), Leute im Weg | 8 | 0 | 1 / 6 |
  | 7-8 | + Arbeiter-Gefahr, Heim nur wenn stark (Lauf 8: Speer/Bogen = 0) | 8 / 7 | 0 | 3 / 1 |
  | 9 | + Verfolger bis 15 Felder, seitlich 60/90 Grad | 1 | 1 | 0 |
  Erkenntnis Lauf 9: 2 Verfolger-Assassinen liefen 4.000 Ticks lang 10-11 Felder hinter ihm her bis an den Kartenrand -
  gleich schnell, sie geben nicht auf. Reine Flucht schuettelt sie nie ab; Burg = eigene Verluste (Speer/Bogen toeten sie
  nicht), ins Leere = Tod am Rand. Aber: 2-3 ihrer Wachen 4.000 Ticks weggelockt = Stufe T2. Stecken-bleiben-Fehler (Zustand 1)
  danach behoben (Pruefung 18/18), im Spiel noch nicht gelaufen.
- **Ganze Partien ab Tick 0, Tempo 300, feste Saat (05.10. 23:2x-23:35):**
  | Partie | Stand | Ergebnis | zerstoert | eigene Verluste | 10. Assassine | Seasoning A reif / B steht |
  |---|---|---|---|---|---|---|
  | gewinn_2 | Burg-Tabu fehlt, Anwerben ab 100 Gold | kein Sieg (Zeit um 28.745), Lord 75.000 -> 75.000 | 84 | 31 | Tick 16.418 | nie / nie |
  | gewinn_3 | + Burg-Tabu, Anwerben ab 70, A-Baum neu suchen | **SIEG Tick 26.081** | 64 (24 Apfel, 18 Holz, 9 Joch, 5 Steinbruch, Kornspeicher) | 29 | Tick 13.443 | 2.325 / 6.601 |
  | gewinn_4 | + B-Holz im Planer zurueckgelegt | kein Sieg (Zeit um 28.744), Lord 75.000 -> 33.200 | 87 | 38 | Tick 12.892 | 2.324 / 5.158 |
  | gewinn_5 | + A-Plantagen mit dem Posten in der Eroeffnung (Daniel 23:41 "Seasoning am Anfang") | **SIEG Tick 24.935** | 69 | 37 | Tick 12.218 | 1.500 / 3.978 |
  | gewinn_6 | + gemeinsame B-Ruecklage (Holz + Gold) fuer Anwerben, Planer, Huetten | **SIEG Tick 23.336** | 61 | 31 | Tick 13.571 | 1.473 / 1.554 |
  gewinn_3 Lord: erste Welle (20) Lord 75.000 -> 58.500, 17 tot; zweite Welle (20) 58.500 -> tot, 3 tot.
  gewinn_6 Lord: erste Welle 75.000 -> 32.700, 17 tot; zweite Welle 32.700 -> tot, 6 tot (Muster wie gewinn_3).
  Beliebtheit bei Tick 5.000 / 10.000 / 20.000 (`serie.werte`): gewinn_3 83 / 77 / 65, gewinn_4 77 / 71 / 61,
  gewinn_5 92 / 86 / 74, gewinn_6 93 / 87 / 80. Preis von Seasoning am Anfang: erster Assassine bei 3.778 statt ~640
  (Gold 30 nach Posten + A). Gleiche Saat, trotzdem schwankt das Ergebnis (gewinn_3 Sieg, gewinn_4 Zeit um) - der Lenker
  laeuft in Echtzeit; Wirtschaftszahlen sind stabiler als Sieg/Niederlage.
- **Naechste Schritte (Daniel 05.10. 23:51: "ja, mach das mit dem gemeinsamen Angriff. ausserdem bitte die Assassine
  trotzdem noch frueh machen. aber das morgen"):**
  1. Gemeinsamer Lord-Angriff statt zwei Wellen: sammeln ausser Schussweite (40) bis klar ueberlegen, dann alle
     gleichzeitig. Anlass: erste Welle (20) opfert jedes Mal 17 (gewinn_3, gewinn_6), erst die zweite toetet ihn.
  2. Erster Assassine trotz Seasoning frueh: gewinn_6 erst bei Tick 3.778 (vorher ~640), weil nach Posten + A-Plantagen
     nur 30 Gold bleiben. Seasoning am Anfang bleibt (Daniel 23:41) - das Gold fuer den Assassinen anders finden.
  Pruefen wie bisher: feste Saat, Tempo 300, `serie.werte` gegen gewinn_6.
  Stand 06.10. 19:05: (1) von Codex gebaut (Sammeln ab 20 ausser Schussweite, Angriff mit allen ab 40 Angekommenen):
  Serie gemeinsam_1 3 Siege (27.347 / 26.666 / 26.385), Verluste 10-18 statt 31, aber ~3.000 Ticks spaeter als
  gewinn_6 und weniger zerstoert (44-54); angegriffen mit 47-60, weil Nachzuegler erst ankommen muessen.
  Trainingsstand (Tick 24.521, 40 gesammelt, Lord 150.000): 5 tot, 10 Zeit um, 15-17 unsicher, 18 2/3, 19-40 je 3/3 -
  gilt NUR fuer diese Lage (`daten/lordminimum_ergebnis_20261006_18*.json`). (2) erster Assassine im Trainingslauf 3.207.
- **Naechste Schritte (Daniel 06.10., Uebergabe von Codex):**
  1. Bedrohungs-/Einfluss-Fingerabdruck aus gemessenem Schaden, Weg, Sicht, Gebaeuden, Gelaende - keine Formel aus
     Lord-Leben oder Fern/Nah-Zahl. Zuerst Messluecke schliessen: KI-Einheiten haben Zielart 3, ihr Ziel steht nicht
     im gelesenen Feld (Lauf 20/1: 123.400 Schaden, 0 einem sichtbar zielenden Feind zuzuordnen).
  2. Unbekannte Lage: keine unbelegte Zahl; vorsichtiger Ersatzwert nur als vorlaeufig gekennzeichnet.
  3. Mit der kleinsten ausreichend sicheren Truppe angreifen, nicht auf Nachzuegler warten.
  4. Holz: zusaetzliche Holzfaeller nur, wenn sie den Ausbau beschleunigen; sonst verkaufen statt verlieren.
  5. Erster Assassine frueher (3.207 / 3.778).
- **T2 Weglocken:** einer lockt die Verteidiger weg (und weicht nach T1 aus), ein anderer greift derweil an.
- **T3 Sammeln bis zur eigenen Uebermacht**, dann gegen die Verteidigung - "dann ist die Tuere frei fuer die anderen".

## Ziel
Die Liga-Partie gegen Rotkaeppchen gewinnen: ihren Lord toeten, ohne unseren zu verlieren.

## Arbeitsweise (gilt fuer jeden Schritt)
1. **Eine Aenderung je Schritt.** Vorher aufgeschrieben: was sie bewirken soll und woran man es misst.
2. **Erst die Attrappe:** Pruefung ohne Spiel (`werkzeug/*_pruefen.py`), gruen - und gegen den alten Stand rot.
3. **Dann eine Serie:** 3 Laeufe, Tempo 200, Instanz 1, eine Code-Kennung fuer alle drei (serie.py bricht sonst ab).
4. **Abnahme gegen das vorher festgelegte Kriterium**, verglichen mit der Basis. Kein Flicken waehrend einer Serie.
5. **Bericht an Daniel nach jedem Schritt**, dann der naechste.

## Ist-Stand (gemessen)
| Bereich | Stand | Beleg |
|---|---|---|
| Wirtschaft | Verkaufsgold 7.935-8.360, erste Mine ~Tick 6.000, Steinhaufen am Ende <= 7 | Serie p (3 Laeufe, Kennung d370a5dd) |
| Takt | Tempo 200: ~87 Lenker-Runden je 1.000 Ticks (Tempo 1000: ~25) | Serien t, o |
| Lord, 5er-Wellen | einmal Lord auf 54.900 (-63 %), danach eigene Niederlage bei Tick 20.990 | Serie t2 |
| Lord, 20er-Wellen | in o und p nie gestartet (Ankunftskreis zu klein, Wegtest auf das Lord-Feld) - beides behoben; q1: 1 Welle, Lord unberuehrt, 4 Verluste - WARUM ist unbekannt | Serien o, p, q1 |
| Sammelpunkt | faellt bis an unseren Bergfried zurueck (6-10 Sperren je Partie) | Serie p |
| Verteidigung | eigener Lord ungeschuetzt (t2 verloren); Rotkaeppchens Leute greifen an unserem Bergfried an | Serien t, p |

## Schritte in dieser Reihenfolge
**S0 - Basis festschreiben.** Code-Stand a393bc8a (q1) wird Basis. Keine Aenderung.

**S1 - Sehen, was eine Welle tut (nur Messung, kein Verhalten aendern).** Je Welle und Runde mitschreiben: wie viele
leben, mittlerer Abstand zum Lord, wer greift wen an, wo stirbt wer. Abnahme: fuer jede Welle in 3 Laeufen ist
beantwortet, ob sie den Lord erreicht, und wenn nein, woran sie scheitert (Weg, Bogenschuetzen, Nahkaempfer, Mauer).

**Aenderung 21:34 (Daniel): "warum jetzt ploetzlich in Wellen? ... du raidest eh schon mit Assassinen, dann wartest du,
bis du eine kritische Menge auf dem kompletten Feld hast, und alle greifen dann gleichzeitig den Lord an."** Sammelpunkt,
Wellen und Rueckzug-Mikro (meine Konstruktion) fallen weg. Neu: raiden wie bisher; sobald 20 Assassinen leben (Daniel
21:05: "lieber 20 auf einmal"), greifen ALLE mit einem Befehl den Lord an; sind davon weniger als 3 uebrig, wieder raiden
bis 20. Die S1-Messung haengt an diesem Angriff. Abnahme: Attrappe (19 -> kein Angriff, 20 verstreute -> ein Befehl mit
allen 20, Raids nehmen keine Angreifer, Ende bei < 3) gruen und gegen den alten Stand rot; Serie mit 3 Laeufen beantwortet
je Angriff: wie viele kamen am Lord an, wann, was hielt die anderen auf, Lord-Schaden.

S1 ausgefuehrt ab 05.10. 21:33 (Daniel: "ja, fang mit S1 an"). Vorher festgelegt:
- Neu: `assassinen.py` schreibt je Welle und Runde eine Zeile nach `daten/wellen_live_<zeit>_i<inst>.jsonl` (leben,
  Abstand zum Lord mittel/kleinster, greifen Lord an, greifen anderes an + Typ, ohne Ziel, Feinde fern/nah um die Welle,
  Lord-Leben). `werkzeug/wellen_auswerten.py` macht daraus je Welle eine Zeile.
- Gegenprobe kein neues Verhalten: Attrappe gibt mit und ohne Protokoll dieselben Befehle aus.
- Abnahme S1: fuer jede Welle in 3 Laeufen steht da, ob sie den Lord erreicht (jemand <= 3 Felder und greift ihn an),
  und sonst die Ursache: kein Weg (Abstand faellt nicht) / abgefangen (Ziel ist ein anderer Feind) / unterwegs
  gestorben / angekommen ohne Schaden.

**S1 ERGEBNIS (Serie a, 3 Laeufe, Kennung 39acda39, 05.10. 21:45):** 5 Angriffe zu je 20. Wegstrecke beim Befehl
12-91 Felder -> sie kommen einzeln an: am Lord gleichzeitig hoechstens 0-2 von 20; Verluste je Angriff 14-17; Lord-Schaden
nur in a2 (150.000 -> 106.300, -29 %), sonst 0. Ursache = **gleichzeitig befohlen ist nicht gleichzeitig angekommen.**
Daniel 21:46 (Bild): Assassinen nehmen nicht das naechste Ziel, sondern folgen "stupide" den anderen; die Wirtschaft
haette man viel frueher abreissen und dann gezielt auf den Lord gehen koennen.

**Daniel 21:46-21:47 (Bilder), woertlich zusammengefasst:**
- "Assassinen bleiben nach dem Auftrag auf den Lord einfach vor den Mauern stehen - das ist falsch, sie sollten aktiv
  versuchen, weiter den Lord zu killen." "Jeder Tick, wo sie rumstehen, ist eine Sekunde mehr, wo der Gegner Einheiten
  rekrutieren kann - und wo gegnerische Einheiten auf unsere schiessen koennen."
- "Es sieht immer noch so aus, als wuerdest du Holz verkaufen, anstatt Eisenminen oder Steinbrueche zu bauen."
  (gemessen frueher: ~90-100 Holz-Lose je Partie verkauft = rund 2.000 Holz)
- Assassinen nehmen nicht das naechste Ziel, sondern folgen anderen; Wirtschaft frueher abreissen, dann gezielt Lord.

**Neue Reihenfolge (je ein Schritt, Pruefung ohne Spiel, Serie, Abnahme - wie oben):**
- **S2a Nie rumstehen beim Lord-Angriff:** wer im Angriff nicht den Lord angreift (steht, laeuft nicht), bekommt den
  Befehl JEDE Runde neu; bleibt er vor einer Mauer haengen -> messen, wie Assassinen hineinkommen (Haken/Mauer
  erklettern), dann diesen Weg nehmen. Abnahme: kein Angreifer laenger als 2 Runden ohne Ziel/Bewegung.
- **S2b Holz investieren statt verkaufen:** messen, warum der Planer bei Holzueberschuss nicht baut (keine Plaetze?
  Arbeiter? Horizont? Stein?), dann die Ursache beheben. Abnahme: Holz-Verkauf deutlich unter Basis, mehr Steinbrueche/Minen.
- **S2c Gleichzeitig ankommen:** Treffpunkt kurz vor dem Lord ausser Schussweite, dann gemeinsam (S1: Weg 12-91 Felder,
  am Lord hoechstens 2 von 20).
- **S2d Raiden: naechstes Ziel, Wirtschaft zuerst** (nicht anderen folgen).

**WISSEN VOR DEM NAECHSTEN TEST (Daniel 21:49: "du machst das jetzt noch vor den Tests und stoppst alle Tests"):**
- Handbuch `Stronghold Crusader Extreme/manual/manual_de.pdf` S. 21: "Meuchelmoerder: Mit Hilfe ihres Kletterhakens
  koennen sie Waelle erklimmen und sind daher sehr nuetzlich beim Einnehmen von Torhaeusern"; unsichtbar, bis eine
  feindliche Einheit sie entdeckt. S. 27: hat eine Einheit das Torhaus erklommen, weht unsere Flagge - Zugang zur Burg.
- SHC-Wiki (stronghold.fandom.com/wiki/Assassin, per Suche): Klettern in Sekunden auf Befehl; oben auf einem Torhaus
  wird es eingenommen und das Tor geoeffnet; beim Klettern bleibt die Tarnung, solange keine Einheiten nah sind; Grenze:
  Mauern verschiedener Hoehe ohne Treppe dazwischen koennen sie nicht erklimmen. Werte wie der Streitkolbenkaempfer.
- Folgerung fuer S2a: vor der Mauer stehen ist der falsche Befehl - erst auf den Wall/das Torhaus (Haken), Torhaus
  einnehmen, dann ist der Weg zum Lord offen. Gemessen haben wir: Lord 150.000 Leben, Assassine voll 12.500, 1-2
  Assassinen am Lord = 1.500-3.000 Schaden je Lenker-Runde (MESSUNG Feindlord).

**EFFEKTIVER TESTEN (vor jedem weiteren Test):**
1. Keine ganzen Partien mehr fuer eine Kampf-Frage: einmal bis kurz vor den Angriff spielen, SPEICHERN, dann nur den
   Angriff (~2.000 Ticks) immer wieder vom selben Stand - Minuten statt einer Viertelstunde je Wiederholung, gleiche
   Ausgangslage, echter Vergleich.
2. Einzelne Mechanik einzeln pruefen, bevor sie in den Lenker kommt: EIN Assassine bekommt den Befehl auf ein Mauerfeld
   - klettert er? auf das Torhaus - wird es unseres? (Sekunden).
3. Werte aus dem Speicher lesen statt schaetzen (Leben/Schaden je Einheitentyp; VillageStudio-Wissensstand pruefen).
4. Erst wenn eine Mechanik belegt ist, kommt sie in den Lenker, dann Szenario-Serie, erst danach ganze Partien.

**S2 - Die eine Ursache aus S1 beheben, die die meisten Wellen stoppt.** Was genau, entscheidet die Messung aus S1 -
nicht vorher raten. Abnahme: Lord-Schaden je Welle im Mittel ueber 3 Laeufe deutlich ueber der Basis (Zahl lege ich
nach S1 fest, bevor gebaut wird).

**S3 - Eigenen Lord schuetzen**, wenn Rotkaeppchens Grossangriff kommt. Abnahme: 0 Niederlagen in 3 Laeufen.

**S4 - Sammelpunkt stabil vor unserer Burg** (nicht am Bergfried). Erst wenn S2 zeigt, dass der Ort zaehlt.

**Spaeter (Backlog, nicht jetzt):** wirksames Minimum je Welle lernen; Holzfaeller naeher (bis 70 Felder verstreut);
mehr Eisen; Moerderloecher, Feuer, Hunde, Bevoelkerung als Messgroessen.

## Was ausdruecklich NICHT passiert
- keine zweite Aenderung, bevor die erste abgenommen ist
- keine Serie mit gemischtem Code
- keine neuen Baustellen (Wirtschaft, Instanzen, Werkzeuge), bis S1-S3 stehen
