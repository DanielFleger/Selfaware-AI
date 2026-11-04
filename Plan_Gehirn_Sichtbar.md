# Plan: Gehirn mit Menschen-Wissen, Allwissen als eigener Schalter (B-288)

Daniel 04.11.2026 21:18: "Gerne kann die Trefferquote etwas darunter sein, aber möglichst perfekt was Menschen möglich wäre."
Und: "solange wir wissen, dass es möglich ist. Es erlauben ist ein anderer Schalter."

## Ziel

Der Simulator (`werkzeug/simulator.py`) sagt die nächsten Takte aus Einheiten und Spielregeln voraus. Heute liest er bei Feinden
auch Verborgenes. Künftig gibt es einen Schalter `wissen`:

- `mensch`: Feinde nur aus dem, was ein Spieler sieht oder durch Spielen lernt. Das ist der Standard und der einzige Weg in den
  Spielweg.
- `alles`: wie heute. Bleibt für Messungen und eine spätere "perfekte KI" (Daniel und Krari) erhalten, im Spielweg aus.

Das Wissen selbst wird weiter gesammelt (SRE); FAIRNESS.md regelt nur, was der faire Spielweg nutzt.

## Bau

Der Simulator bleibt, wie er ist. Davor kommt EINE Stelle, `gehirn_sicht.py`: `sichtbar(einheiten, vorgeschichte, ich)` gibt die
Einheitenliste zurück, in der bei Feinden alles Verborgene entfernt oder durch eine Schätzung aus Sichtbarem ersetzt ist. Eigene und
verbündete Einheiten bleiben roh (`parteien.freunde_von`, wie der Sichtfilter). Geschosse läuft dasselbe.

| Feld bei Feinden | Heute | `mensch` |
|---|---|---|
| Lage, Leben, Art, Besitzer, Blick | gelesen | gelesen (sichtbar) |
| Zustand (Tätigkeit) | gelesen | gelesen (sichtbar) |
| Schussphase `sre_naechster_schuss_takte` | gespeichert/abgeleitet | aus Zustand + Animationsbild + Phasentabelle (Daniel 04.11. 21:39: erlaubt, das Bild ist sichtbar; Genauigkeit über Mensch ist schnelles Rechnen) |
| Schussziel `shootTargetedUnit` | gelesen | Zielwahl-Regel P14 auf sichtbare Lagen (die hat der Simulator schon), Blick als Prüfung |
| Nahkampfziel `attackedUnitID` | gelesen | nur, wenn Zustand 106 und das Ziel wirklich Leben verliert (Regel wie `waechter.sichtfilter`), sonst Regel AU18 |
| Wegplan, Laufziel `sre_wegpunkte`, `destination` | gelesen | aus der beobachteten Bewegung (letzte Lagen, Richtung), geradeaus weiter |
| Zugphase (+848/+852) | Feld oder Vorgeschichte | nur Vorgeschichte der sichtbaren Lagen, sonst Mitte |
| Suchtakt `fixedRng`, `closestEnemyMicroDistance`, `lastEnemy…` | gelesen | entfällt: Abstand aus Lagen, Suchtakt unbekannt (angenommen: sofort) |
| Tempo `calculatedMovementSpeed`, `moveDelay`, `stateBasedSpeed` | gelesen | aus Art + Befehlsart gemessen (S8, S39), Gelände P13 |
| Unsichtbare Assassine (`assassinsMicroDistance…` > 160) | gesehen | **fehlt ganz in der Liste** |
| Geschoss `targetX/Y`, `unitID`, Rest-Schritte | gelesen | Linie aus Start und jetziger Stelle, Tempo S10, Ziel unbekannt: fliegt bis Treffer oder Reichweite |

Alle anderen Felder werden bei Feinden gelöscht (Erlaubt-Liste, nicht Verbots-Liste). Was der Simulator dann nicht findet, nimmt er
als unbekannt, und das fällt in der Prüfung auf.

## Prüfungen (vorher festgelegt, alles offline auf den vorhandenen Prüfläufen, kein Spiel)

1. **Dichtheitsprobe (die entscheidende):** In einem Prüflauf werden alle verborgenen Felder der Feinde mit Müll überschrieben. Im
   Modus `mensch` muss die Vorhersage Takt für Takt genau gleich bleiben. Gegenprobe: Im Modus `alles` muss sie sich ändern.
   Widerlegt, sobald ein Unterschied auftritt: Dann liest noch etwas Verborgenes mit.
2. **Preisliste:** Jedes verborgene Feld wird einzeln entzogen, immer nur eines. Das zeigt, wie viele Punkte es kostet. Besser
   geschätzt wird zuerst, wo es am meisten kostet, und nur so lange, wie die Quote noch steigt.
3. **Gesamtwert:** `gehirn_pruefen.py` mit `mensch` gegen `alles` auf 200603, 191847, 201153, 202133, 213104, aus Sicht beider
   Spieler, mit Opfer-Quote, Präzision und neuen Begegnungen.
   - Startgrenzen (UNGEMESSEN, aus den alten Grenzen übernommen): Opfer-Quote mindestens 80 %, neue Begegnungen mindestens 75 %.
   - Darunter: Lücke je Feld zerlegen, keine Werte nachstellen.
4. **Fairness:** `fairness_pruefen.py` wird rot, wenn der Spielweg den Simulator mit `alles` ruft oder der Standard nicht `mensch` ist.
   Gegenprobe im Lauf.
5. Rust-Kern: nicht betroffen, R1 und R3 lesen schon nur Sichtbares.

## Nicht dabei

Kein neuer Prüflauf (Daniel 26.10. "vorerst kein neuer Prüfstein-Lauf"), keine Partie, keine Änderung an der App, kein Einbau in den
Lenker. Hände und "ein Befehlsweg" warten auf SREs Messung.

## Grenzen der Messung

Die Prüfläufe sind Sandkasten-Gefechte ohne neue Befehle von außen; neue Befehle eines Gegners kann auch ein Mensch nicht
vorhersehen, sie bleiben Restfehler. Die Prüfläufe stammen vom 25./26.10., der Liga-Stand von damals. "Menschen möglich" wird hier
als "nur sichtbare Felder plus erlernbare Regeln" gefasst, nicht als gemessene Leistung eines Menschen.

## Rückweg

`wissen="alles"` liefert den alten Stand. `gehirn_sicht.py` ist eine einzelne Datei.
