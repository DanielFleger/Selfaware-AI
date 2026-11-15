# Plan: Das Gehirn in fuenf Meta-Ebenen (B-273)

Erstellt 27.10.2026 20:15 (SAI) nach Daniels Vorgaben 19:36-19:52. Entworfen von oben (5) nach unten (1), gebaut wird von
unten nach oben. Jede Ebene haelt sich an [FAIRNESS.md](FAIRNESS.md): uebermenschlich schnell ja, Spiel veraendern und
verborgenes Gegnerwissen nein.

**Die Leiter:** jede Stufe denkt ueber etwas anderes nach, nicht ueber mehr Einheiten.

| Stufe | denkt ueber | Kernfrage |
|---|---|---|
| 5 Zielsetzer | das Ziel und die Waehrung | Spiele ich auf das Richtige hin - und messe ich in der richtigen Einheit? |
| 4 Selbstpruefer | das eigene Denken ueber die Zeit | Wo lag ich falsch, und wie baue ich mein Denken um? |
| 3 Gegnerdenker | den Gegner, nur aus Beobachtung | Wie entscheidet er, und wie bringe ich ihn zum Fehler? |
| 2 Truppfuehrer | das Zusammenwirken von Einheiten | Was kann die Gruppe, was einer allein nicht kann? |
| 1 Feldherr | die einzelne Einheit | Wem gehoert welche Einheit gerade? |

## Die zwei Leitungen zwischen den Ebenen

- **Auftrag (nach unten):** Ziel, Waehrung (wie wird gezaehlt), Risikobereitschaft, Frist. Jede Ebene gibt der darunter
  einen Auftrag und nimmt ihr nichts aus der Hand, was sie selbst entscheiden kann.
- **Bericht (nach oben):** jede Entscheidung schreibt VORHER ihre Vorhersage auf (was soll passieren, bis wann, was kostet
  es) und NACHHER das Ergebnis. Das ist das **Vorhersage-Tagebuch** - ohne es kann Stufe 4 nichts lernen. Es ist darum der
  allererste Bauschritt, noch vor Stufe 1.

---

## Stufe 5 - Zielsetzer

**Aufgabe:** waehlt den Siegweg und die Waehrung, in der alle darunter rechnen.

- **Siegwege:** Lord-Sturm frueh / Wirtschaft aufbauen, dann Sturm / Aushungern (Wirtschaft des Gegners zerstoeren, bis er
  sich nicht mehr wehrt) / im Team: den Verbuendeten tragen.
- **Waehrung:** heute alles in Gold-Gegenwert. Je nach Lage Gold mit Zeitfaktor (gegen die Uhr), sicherer Sieg vor
  schnellem (Liga), Team-Wert statt eigener Wert (2v2).
- **Eingaenge (fair):** Spielart (1v1, 2v2, Karte), sichtbare Lage (eigene Wirtschaft, sichtbare Gegnermacht, Lord-Leben),
  Zeit, Berichte von Stufe 4 (welcher Siegweg hat bisher gegen diese Art Gegner getragen).
- **Ausgang:** Auftrag an Stufe 4 bis 1 - Siegweg, Waehrung, Risikobereitschaft.
- **Takt:** selten - etwa alle 2.000 Takte und bei Wendepunkten (Heer verloren, Lord des Gegners unter 50 %, Verbuendeter
  faellt). Ein Wechsel muss begruendet im Tagebuch stehen.
- **Steckt schon drin:** Endspurt-Schalter (feldzug), Kausal-Entscheider (Wirtschaft), ZIEL_TICK / gold_ziel. Alles feste
  Schalter - Stufe 5 macht daraus eine Wahl.
- **Erster Bauschritt:** die heutigen Schalter in EINE Stelle sammeln, die den Siegweg nennt und ins Tagebuch schreibt -
  Verhalten zunaechst unveraendert.

## Stufe 4 - Selbstpruefer

**Aufgabe:** vergleicht jede Vorhersage mit dem Ergebnis, findet die Ursache der Abweichung und baut das Denken um.

- **Ursachen, die er unterscheidet:** falsche Spielwerte (Beispiel B-272: die App rechnete den Lord mit 20 statt gemessenen
  Schaden - eine Abweichung Vorhersage/Ergebnis haette das sofort gezeigt), falsches Gegnermodell (Stufe 3), falscher
  Gruppenwert (Stufe 2), Befehl nicht ausgefuehrt (Haende).
- **Was er aendert:** Werte im Gehirn (Schaden, Laufzeiten, Verlustraten), Gewichte der Muster, das **Trick-Buch** (jedes
  Gruppenmuster mit Siegquote je Gegnerart), die Rechenzeit je Stufe (wer gerade die Runde bremst - FELDZUG ZEITEN).
- **Neues erfinden:** Muster neu kombinieren, im Sandkasten erproben (nie im echten Spiel schummeln), behalten was gewinnt.
- **Takt:** nach jeder Entscheidung (Abgleich) und nach jeder Partie (Lernbuch).
- **Steckt schon drin:** lernbuch.py (Verlustraten je Profil), partie_lernen.py, kausal_modell, Wissensregister, FELDZUG
  ZEITEN. Es fehlt: die Vorhersage VOR der Entscheidung und der automatische Abgleich.
- **Erster Bauschritt:** Abgleich fuer den Lord-Wettlauf - vorhergesagter Schaden je Takt gegen gemessenen
  (MESSUNG Feindlord steht schon im Log); Abweichung ueber eine Grenze -> Meldung und Wert nachziehen.

## Stufe 3 - Gegnerdenker (nur aus Beobachtung)

**Aufgabe:** lernt aus dem Sichtbaren, wie dieser Gegner reagiert, und plant Aktionen, die ihn zu Fehlern bringen.

- **Gegnerprofil:** wo stehen seine Schuetzen, wie schnell und mit wie vielen reagiert er auf einen Raid, wann greift er
  an (Rhythmus), repariert er Mauern, wohin zieht er sein Heer, wenn wir an zwei Stellen druecken.
- **Proben:** kleine, billige Aktionen, die etwas ueber ihn verraten (zwei Sklaven an die Ostseite - wer kommt, wie schnell).
- **Gegen Menschen:** ein Mensch hat einen Bildschirm - mehrere gleichzeitige Fronten ueberfordern seine Aufmerksamkeit.
- **Ausgang:** erwartete Reaktion je geplanter Aktion -> fliesst in den Gruppenwert von Stufe 2.
- **Takt:** jede Runde beobachten, Profil alle ~500 Takte verdichten.
- **Steckt schon drin:** bedrohung.py (gemessene Lagen), Waechter (Angriffe erkennen), Sichtfilter (B-274). Es fehlt ein
  Profil, das sich ueber die Partie aufbaut.
- **Erster Bauschritt:** Reaktionsmessung - je Raid: wie viele Feinde kamen, nach wie vielen Takten, von wo.

## Stufe 2 - Truppfuehrer

**Aufgabe:** plant mit einer Gruppe, deren Wert mehr ist als die Summe: Opfer, Koeder, Begleitschutz, Formation.

- **Muster (Startliste):** gebuendelter Sturm (sammeln ausser Schussweite, dann alle zugleich - B-263, ersetzt B-139),
  Koeder + Eindringling (zwei Assassinen), Fackel-Sklaven, Schuetzen-Blitzableiter (billige Bogen ziehen das Feuer, die
  Streitkolben laufen zum Lord), Begleitschutz fuer Assassinen.
- **Gruppenwert:** das Gehirn sagt den Ausgang voraus (Gefechtsrechnung mit nur den Schuetzen, die uns sehen - B-270) -
  Gewinn minus Verluste in der Waehrung von Stufe 5.
- **Vertrag je Befehl (B-216):** "lauf dahin" bekommt eine Erwartung (Ankunft bis Takt X, kaum Beschuss, Ziel noch da);
  jede Runde geprueft, bei Abweichung sofort umplanen: warten, ausweichen, sammeln, anderer Weg.
- **Wachsen, teilen, zusammenlegen:** Trupps aendern sich mit der Lage.
- **Steckt schon drin:** feldzug (Sammeln, Durchbruch, Lord-Wettlauf), raids, assassinen (Stapel), sturm.
- **Erster Bauschritt:** der gebuendelte Sturm als erstes Muster mit Vertrag (Daniel 27.10. 19:59: B-263 ersetzt B-139).
  Achtung: feldzug.py hat schon eine Sammel-Phase (SICHER = 50, Zeile 183) und feldzug_pruefen.py Faelle dazu (3, 6, 20,
  25) - B-263 aendert bestehendes Verhalten, die Faelle werden mit umgestellt.

## Stufe 1 - Feldherr

**Aufgabe:** besitzt jede Einheit genau einmal und verteilt sie jede Runde neu auf die Trupps.

- **Gebote:** jeder Truppfuehrer sagt, was er mit genau diesen Einheiten erreicht (Wert der Gruppe, nicht je Kopf - die
  zweite Assassine kann mehr wert sein als die erste). Der Feldherr gibt Einheiten dorthin, wo sie zusammen am meisten
  bringen.
- **Rollen:** Raid / Angriff / Verteidigung / Reserve - Umschalten in jede Richtung, einzeln oder als ganze Gruppe.
- **Ein Besitzer:** kein Modul befiehlt Einheiten, die ihm nicht gehoeren - das beendet das gegenseitige Aufhaengen
  (heute: feldzug_ruht, Heimwache, Waechter "Stapeln holte sie heim").
- **Takt:** jede Runde.
- **Steckt schon drin:** Sharky-Plan B-97..B-100 (Manager-Liste, Einheiten-Anspruch) - hierin aufgenommen. Heute gibt es
  drei Besitz-Mechanismen (ausgenommen/reserve beim Waechter, Heimwache, feldzug_ruht) plus den Filter `raus` im Feldzug;
  die Reihenfolge der Module in erstes_spiel entscheidet (Waechter vor Feldzug).
- **Erster Bauschritt:** Besitzbuch an der EINEN Stelle, durch die alle Befehle gehen (`laden.befehl`), mit Absender
  (Modul). Es liest die Einheiten aus jedem Befehlsschluessel (angriff, mauerziel, halten, lauf, gruppe ...) und zaehlt
  getrennt: **Uebergabe** (eine Einheit wechselt zwischen zwei Runden den Besitzer - gewollt) und **Doppelbefehl** (zwei
  Module befehlen dieselbe Einheit in derselben Runde - der Fehler). Vorher zaehlen, an welchen Stellen Einheiten-Listen
  gebildet werden. Verhalten unveraendert, Schalter zum Abschalten.

---

## Bau-Reihenfolge

0. Vorhersage-Tagebuch (fuer alle Stufen) - zuerst auf dem, was der Lenker heute schon rechnet: Lord-Wettlauf und
   Gefechtsrechnung (`feldzug._lohnt`, `gefecht.bewerte`) auf dem Lagebild. Mit Schalter (an/aus) und Zeitmessung je
   Runde (heute 0,15-0,27 s je Takt, partner.py:23 - das Tagebuch darf die Runde nicht spuerbar verlaengern).
   Erste Kennzahl: vorhergesagter gegen gemessenen Lord-Schaden je Takt (MESSUNG Feindlord steht schon im Log).
1. Stufe 1: Besitzbuch, dann Gebote und Rollen.
2. Vor Stufe 2 messen: bekommt der Lenker im Spiel jeden Takt genug Daten (Taktring AU15)? Dann gebuendelter Sturm mit
   Vertrag (B-263), dann weitere Muster.
3. Stufe 3: Reaktionsmessung, dann Gegnerprofil und Proben.
4. Stufe 4: Abgleich Vorhersage/Ergebnis, Trick-Buch.
5. Stufe 5: eine Stelle fuer Siegweg und Waehrung, dann echte Wahl.

Jeder Schritt: Messung vorher, Pruefung mit Negativlauf, Fairness-Pruefung gruen, ein Commit mit B-Nummer.

## Fairness des Gehirns (Frage-Agent 27.10. 20:02, Ampel rot - eingearbeitet)

Das Gehirn auf den Speicherbildern des Auges (`gehirn.py`, `simulator.py`) liest von JEDER Einheit das gespeicherte
Schussziel (`shootTargetedUnit`), den Takt des naechsten Schusses und das Nahkampfziel (`attackedUnitID`) - auch von
feindlichen. Zum Erforschen der Mechanik ist das erlaubt, im Spiel nicht. Darum:

- **Mechanik ja, gespeicherter Zustand nein:** fuer feindliche Schuetzen sagt das Gehirn das Ziel mit der Zielwahl-Regel
  des Spiels voraus (naechste Schuetzen zuerst, freie Schusslinie, Reichweite - eine Regel, die fuer alle Einheiten gilt und
  die man durch Spielen lernt), angewendet auf die sichtbaren Positionen. Das gespeicherte Ziel wird nicht gelesen.
- Bevor `gehirn`/`simulator` in den Lenker kommen, bekommen sie einen Sichtmodus mit genau dieser Regel.
- `werkzeug/fairness_pruefen.py` sucht die drei Feldnamen jetzt mit und durchsucht `gehirn.py`/`simulator.py` immer; laedt
  der Lenker eines davon mit rohen Feindfeldern, ist die Pruefung **rot** (Negativlauf 27.10. 20:08).

## Offen

- Ob der Lenker im laufenden Spiel jeden Takt dieselben Daten bekommt wie das Gehirn auf den SRE-Speicherbildern
  (Taktring AU15) - vor Stufe 2 messen.
