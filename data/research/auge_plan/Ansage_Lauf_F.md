# Ansage Lauf F

Erstellt 02.11.2026 von SRE (B-142), neu nach dem gescheiterten Lauf vom selben Tag. Stand 21:45, nach dem Abbruch von 21:30 (Warum-Kette unten). **Der Lauf von 21:42 war gültig, Ergebnis: `lauf_f_20261102/Ergebnis_Lauf_F.md`.**

Plan und Gründe: `docs/plans/Plan_Lauf_F_neu.md`. Warum der alte Lauf scheiterte: `ursachen_lauf_f/Ursachen_Lauf_F.md`.

## Was wird getestet

Das Auge, nicht das Spiel und nicht SamurAI: Sieht es alles, was im friedlichen Spiel passiert, ohne das Spiel zu bremsen?

## Was ich erhoffe, und was es widerlegt

| Probe | Erhofft | Widerlegt, wenn |
|---|---|---|
| A1 | Jede Änderung liegt in einem Feld der Liste | Ein Byte ändert sich außerhalb. Das erwarte ich: Die Jahresprobe fand schon 539 Felder außerhalb, jedes ist ein Gewinn für die Feldliste |
| A3 | Auf Tempo 40 fehlt kein Takt, kein jeden Takt gelesener Bereich ist gemischt | Ein Takt fehlt oder ein Rahmen ist gemischt. Das beendet den Lauf sofort. **Grenze:** "rein" heißt, der Taktzähler ist vor und nach dem Lesen derselbe. Er steigt mitten im Takt, ob das je einen Rahmen verfälscht, ist nicht gemessen |
| A4 | Auf den Stufen 1 bis 1000 zieht das Lesen kein Tempo ab | Mit Lesen weniger Takte als ohne, über das Messrauschen hinaus. Eine Stufe mit zu wenig Takten heißt "nicht gemessen", nicht bestätigt |
| A7 | Jede gezogene Zufallszahl steht in der Tabelle | Eine Zahl passt nicht |
| A8 | Jede Änderung von Gold und Waren fällt mit einer möglichen Ursache zusammen | Rest ohne Ursache. **Grenze:** zeitlich zugeordnet, nicht Stück für Stück. "Arbeiter" heißt nur, dass ein Betrieb im selben Fenster seine Ware änderte |
| A10 | Keine `uid` auf zwei echten Plätzen, Monat 0 bis 11 | Ein Wert liegt außerhalb. Einheiten-Platz 0 zählt nicht: Dort kopiert das Spiel die Einheit vor der Wegsuche hin (belegt im Code und in der Probe) |
| Einzelpunkte | Jeder der 241 Punkte bekommt einen Beleg | Punkte bleiben "nicht gesehen" und gehen an Lauf K oder S. **Grenze:** Das Werkzeug sagt nur "Zahl passt" oder "Zahl weicht ab". Bestätigt oder widerlegt schreibe erst ich, wenn ich die Belege gelesen habe |

## Wie getestet wird

- **Wo:** Instanz 2, Karte `A Mighty Oasis.map`. Instanz 5 lehnt das Werkzeug ab.
- **Tempo und Dauer:** Stufe 1000 (gemessen 825 Takte je Sekunde): Abschnitte bis zu den Warenketten höchstens rund 50.000 Takte, also rund 60 Sekunden. Dann ein Jahr auf Tempo 40: 9.600 Takte, gemessen 242 Sekunden. Dann die Tempotreppe: gerechnet 220 Sekunden. **Ziel rund 9 Minuten, harte Grenze 10 Minuten.**
- **Das Programm hält das Spiel nie an**, auch nicht für den Bauplan.
- **Abschnitte, Grenzen und Abbruchgründe:** siehe Plan.

## Trockenlauf: was schon gemessen ist (02.11.2026 20:51 bis 20:55, Instanz 2, Spielstand "Anzeigebug repariert", ohne Bauen)

| Probe | Ergebnis |
|---|---|
| Strenge Aufzeichnung auf Tempo 40, ein ganzes Jahr | 9.607 Lesungen, 0 fehlend, 0 gemischt, Warteschlange nie voll, 61 MB, 242 s. Gemischt nur im selten gelesenen Datenblock (6 Mal), der zählt nicht als Fehler |
| Anhalten am Ende | Takt steht, nachgelesen |
| Bauplan am Spielstand | 59 Arten mit Stelle in 3,5 s, ohne Stelle: 6 (Pechgrube, kein Boden), 10, 11, 19 (nur neben Vorhandenem, in diesem Stand erwartet) |
| Auswertung der Jahresprobe | A3 und A7 bestätigt, A8 bestätigt im genannten Umfang (12 Steuerbuchungen in 12 Monaten, 2 Essen), A10 bestätigt, A1 widerlegt (539 Felder fehlen in der Liste) |
| Programm gegen ein künstliches Spiel | Ganzer Lauf und jeder Abbruchgrund, Tests grün, jede ausgeschaltete Prüfung macht sie rot (`ursachen_lauf_f/lauf_negativ.py`) |

Die Probe lief in einem kleinen Dorf mit 89 belegten Einheitenplätzen. Das volle Dorf im Lauf kann mehr Daten je Takt ändern, das misst erst der Lauf.

## Warum der Lauf um 21:30 abbrach

1. **Abbruch:** "Waren kommen nach 1604 Takten nicht an", offen waren nur Waffen, je 13 oder 14 Stück.
2. **Warum hingen sie?** Im Waffenlager standen genau 50 Stück: 7+7+6x6. Mehr lässt das Spiel nicht hinein (`getArmoryIDIfSpaceLeft`: 50 über alle Waffen zusammen).
3. **Warum war das geplant?** Ich hatte "Waffen 50" aus der Lagertabelle als Grenze je Art gelesen und 20 je Art geplant, also 160. Falsch abgelesen, nicht gemessen.
4. **Warum fiel es im Trockenlauf nicht auf?** Das künstliche Spiel kannte die Grenze nicht, und im Trockenlauf wird nichts eingebucht.
5. **Behoben:** Waffen je 5 (das Anwerben braucht je Art höchstens 3), der Handel verkauft zuerst und kauft dann, das künstliche Spiel kennt jetzt die Grenze, ein Test prüft die geplanten Mengen gegen die Lager.

Der Abbruch selbst war richtig: Er kam mit seinem Namen, das Spiel stand danach, die Sperre war frei.

## Was der Lauf um 21:30 schon gemessen hat

| Vorher ungeprüft | Ergebnis |
|---|---|
| Weg aus der angehaltenen Partie ins Hauptmenü und in den Burgenbau | geht |
| Gold, Burg, Kornspeicher, Anzeige 20, Kalender | gehen |
| 6 Hütten | 58 Wohnplätze |
| Startwaren alle zugleich | Lagerwaren 1 Stück je 4,1 Takte, Essen vollständig |
| Zuzug bei Beliebtheit 90 bis 99 | 1 Bewohner je rund 222 Takte |
| Beliebtheit mit 4 Essenssorten | +150 je Woche |

Neu gefunden: Der Deckel und andere neu aufgerechnete Felder stehen mitten im Takt kurz auf 0. Das hätte beim Lesen des Deckels zu einem falschen Abbruch führen können, jetzt gibt es eine Ablesefrist. Der Zusatzbau und die zweite Kaserne brechen den Lauf nicht mehr ab, sie sind keine Grundlage.

## Was vermutlich als Nächstes hakt

Das sind die ungeprüften Stellen.

**Beendet den Lauf, wenn es nicht klappt:**

1. Alle 62 Arten bauen. Am Stand des Laufs von 21:30 (Takt 3604, gelesen 21:41) findet die Spielprüfung für 62 von 63 Arten eine Stelle, nur die Pechgrube nicht. Gebaut sind davon bisher nur die Arten des Grundstocks. Eine erlaubte Stelle ohne Gebäude beendet den Lauf.
2. Die erste echte Bremsprobe: zweimal Abzug beendet den Lauf. Live gelaufen ist sie noch nie, auch das Aussetzen der Aufzeichnung nicht.
3. Das volle Dorf auf Tempo 40: Ein einzelner fehlender Takt beendet den Lauf. Das ist so gewollt und wird dann erklärt.
4. Die Frist: Die Rechnung lässt rund eine Minute Luft.
5. Die Beliebtheit: Unter 50 außerhalb des Steuertests beendet den Lauf. Gerechnet mit der Liga-Tabelle und den Wochenposten fällt sie im Steuertest von 100 auf rund 71 und steigt danach wieder. Gemessen ist das nicht. Essen reicht laut Messung vom 11.10. (0,19 je Kopf und 1.000 Takte, 58 Leute also rund 11), die Nachlieferung kann 125 je 1.000 Takte.

**Wird nur ein Fund, der Lauf geht weiter:** Handel, Steuern und Rationen, Tor auf und zu (Befehl 45), Arbeit ruhen lassen (Befehl 43), Abreißen, Anwerben aller Arten in einem Takt, Mauer und Graben an der neuen Stelle, Zusatzbauten, zweite Kaserne.

## Was der Lauf nicht zeigen kann

Kampf und KI-Verhalten. Die Pechgrube, weil diese Karte 0 von 78.804 Feldern mit Pechvorkommen hat. Die 77 Punkte mit Marke [Spielart] brauchen die Gegenprobe in Lauf K.

## Danach

- **Scheitert er:** Spiel anhalten, nachlesen, dass der Takt steht, Aufzeichnung beenden, Sperre frei. Warum-Kette aus der Aufzeichnung, beheben, testen, committen, berichten. Neuer Lauf nur nach Daniels Ja.
- **Gelingt er:** `lauf_f_<stempel>_Ergebnis.md` entsteht von selbst. Die Auswertung dauert: 61 MB brauchten 2 Minuten, die Hauptaufzeichnung wird deutlich größer. Danach lese ich die Belege der Einzelpunkte, trage Widerlegtes ins Funktionswissen und Lücken in die Feldliste ein, "nicht gesehen" geht an Lauf K oder S. Dann schlage ich Lauf K vor.

## Nutzen fürs aktuelle Ziel

Es entscheidet, ob die Aufzeichnung so bleiben kann und welche Felder noch fehlen. Danach kommen Lauf K und Lauf S.

## Nutzen fürs große Ziel in 3 Jahren

SamurAI soll in jedem Takt alles wissen, was es wissen darf, und selbst lernen. Das geht nur auf einem Auge, dessen Vollständigkeit gemessen ist.

## Befehle

```bash
PYTHONPATH=src python -m selfaware.tools.experiments.auge_lauf_f pruefen --instanz 2 --laeuft-schon
```

```bash
PYTHONPATH=src python -m selfaware.tools.experiments.auge_lauf_f los --instanz 2 --daniel-ja --laeuft-schon
```

```bash
PYTHONPATH=src python -m selfaware.tools.experiments.auge_lauf_f stop --instanz 2
```
