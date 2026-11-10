# Fairness: Was SamurAI darf

**Stand:** Entwurf vom 07.11.2026 (P1), ergänzt um Daniels Antworten vom 08.11. (F7 bis F12). Grundlage:
- das Entscheidungsblatt `SamurAI_Entscheidungen.html` vom 04.11.,
- der Chat zwischen Daniel und Krari vom 05.11.,
- die Festlegungen im Wissensstand 13ag/13ah.

Krari hat das Blatt nicht ausgefüllt. Im Chat schrieb er aber: „denke ich stimme im allgemeinen deinem assessment zu“. Wo er einzelne Punkte kommentiert hat, steht das dabei.

## Grundsatz

SamurAI darf schneller handeln als ein Mensch. Dabei darf sie aber nur **Aktionen nutzen, die ein Spieler hat**, und nur **Informationen, die ein Spieler sehen kann**.
Kurz (Daniel, 04.11.): „SamurAI darf alles, was ein Mensch kann.“

Das gilt für jede Partie, die zählt. In Testgefechten und Messläufen sind Ausnahmen erlaubt (siehe R2, R6).

## Festgelegt

| Nr | Regel | Herkunft |
|---|---|---|
| R1 | **Schnell steuern ist erlaubt.** Jeden Takt, jede Einheit einzeln, beliebig viele Befehle, solange ein Spieler dieselbe Aktion auslösen kann. Je Takt kommt nur ein Befehl an (gemessen), deshalb braucht es eine Reihenfolge (P4). | Daniel |
| R2 | **Das Spiel verändern ist verboten.** Keine Werte in den Speicher schreiben, kein Gold oder Waren gutschreiben, keine Preise ändern, keine Einheiten setzen oder töten. Erlaubt nur in Testgefechten und Messläufen, nie in einer Partie, die zählt. | Daniel |
| R3 | **Verborgenes Gegnerwissen ist verboten.** Nicht lesen: Laufziele und gespeicherte Ziele fremder Einheiten, fremde Lager, Regeln der Gegner-KI aus Code oder Dateien. Erlaubt: alles Sichtbare und Spielregeln, die man durch Spielen lernen kann. **Ausnahme:** Das Angriffsziel einer fremden Einheit gilt als bekannt, sobald der Angriff sichtbar ist und die Einheit Leben verliert. | Daniel |
| R4 | **Schusstakt aus dem Animationsbild ist erlaubt.** Aus dem sichtbaren Bild und einer gemessenen Tabelle darf sie den Schuss genau berechnen. Den gespeicherten Zählerwert zu lesen bleibt verboten. | Daniel |
| R5 | **Stapeln ist erlaubt, ebenso mehr als 5 Mann auf einem Turm.** Einheiten auf einen Punkt packen darf ein Mensch auch, zum Beispiel mit einem Befehl je Takt. Per Befehl mehr als 5 Mann auf einen Wachturm ist ausdrücklich erlaubt, obwohl beim Mausklick eine Grenze greift. | Daniel; Krari 05.11.: „Ja ich denke das ist fair“ |
| R6 | **Allwissen ist ein eigener Schalter.** Verborgenes wird weiter erforscht, daraus kann später eine „perfekte KI“ werden. Im fairen Spiel steht der Schalter fest auf Menschen-Wissen. | Daniel |

## Einzelfälle

| Nr | Fall | Entscheidung | Herkunft |
|---|---|---|---|
| F1 | Zufallsstand auslesen (wo der Stein landet) | **Verboten.** Die gemessene Streuung als Wahrscheinlichkeit nutzen ist erlaubt. | Daniel |
| F2 | Grenzen, die nur die Maus prüft | **Je Fall Daniel oder Krari fragen**, nicht selbst entscheiden. Entschieden ist bisher nur der Turm (R5). Kostenwerte zu kennen ist erlaubt, auch gemoddete, zum Beispiel Leiterträger 20 Gold mit UCP. Ein Spieler kann sie nachschlagen. | Daniel; Krari 05.11. zu den Kosten: „das ist ja alles fair game“ |
| F3 | Gold und Waren schicken (Befehl 113) | **An Verbündete erlaubt**, an Nicht-Verbündete verboten. Diese Option hat ein Mensch nicht. | Daniel |
| F4 | Fremde Vorräte | **Nur schätzen, nicht lesen.** Ein Mensch sieht, was hineinkommt (Arbeiter, Lieferungen), was angeworben wird und das Verkaufsgold in der Statistik. Steuerstufe, Rationen und Verkäufe einzelner Waren sieht er nicht. | Daniel; Krari 05.11.: „hier kann man abschätzen, das reicht in der Regel“ |
| F5 | Burgplan des KI-Gegners aus der AIV-Datei | **Verboten.** Aus beobachteten Partien lernen ist erlaubt. | Daniel |
| F6 | Befehle in der Pause | **Verboten.** Im Mehrspieler gibt es keine Pause, und gegen eine KI kann ein Mensch in der Pause nichts tun. | Daniel |
| F7 | Öffentliche Statistik (zerstörte und verbrannte Gebäude, Verluste usw.) | **Erlaubt.** Man kann sie theoretisch mitzählen. | Daniel 08.11. |
| F8 | Eigene innere Zähler (Nachladen, Abklingzeit, Taktzähler eigener Einheiten und Gebäude) | **Erlaubt.** Ein guter Spieler kann sie schätzen und könnte sie wissen. Fremde innere Zähler bleiben verboten (R4). | Daniel 08.11. |
| F9 | Zustand fremder Einheiten (kämpft, läuft, lädt nach) | **Erlaubt**, weil man ihn an der Animation sieht. | Daniel 08.11. |
| F10 | Welche fremden Einheiten einen Trupp bilden | **Verboten.** Man kann es nicht wirklich wissen. Aus gemeinsamer Bewegung erahnen ist erlaubt. | Daniel 08.11. |
| F11 | Weg- und Begehbarkeits-Ebenen der Engine | **Erlaubt.** Sie lassen sich aus der sichtbaren Karte ableiten. | Daniel 08.11. |
| F12 | Gegnerische Holzfallen (Fallgruben, Typ 67) und Pech | **Verboten.** Im Spiel verborgen: „das einzige was verborgen ist sind holfallen und wo das pech ist“. Alles andere auf der Karte ist sichtbar: Türme, Gebäude, Einheiten und Arbeiter mit ihrer aktuellen Position, Gelände. | Daniel 11.11. |
| F12 | Szenario-Ereignisse der Karte | Für Partien egal, im Gefecht gibt es keine. In Szenarien sind sie verborgene Auslöser und deshalb **verboten**. | Daniel 08.11. |

Der „Wind“ im Spielzustand ist keine Spielmechanik. Er schaltet nach einer festen Tabelle die Bildfolge von Flaggen und Bäumen weiter (`updateWind`, `UpdateFlag3Entity`; gelesen aus dem Code, nicht im Spiel geprüft). Für Entscheidungen ist er bedeutungslos.

## Was daraus für das Lesen folgt (Grundlage für P2)

Jedes Feld des Spielzustands bekommt genau eine Marke:

- **erlaubt:**
  - eigene Daten, auch eigene innere Zähler (F8),
  - alles, was auf dem Bildschirm sichtbar ist (Position, Art, Leben, Zustand und Animation fremder Einheiten (F9) und Gebäude, Gelände, sichtbare Geschosse),
  - Weg- und Begehbarkeits-Ebenen (F11),
  - Spielregeln und Tabellen, die man durch Spielen oder Nachschlagen kennt, auch gemoddete Werte,
  - die öffentliche Statistik (F7).
- **nur schätzen:**
  - fremde Lager und Vorräte,
  - fremde Steuer, Rationen und Beliebtheit.

  Gelesen werden sie nur im Allwissen-Modus. Im fairen Spiel schätzt SamurAI sie aus erlaubten Feldern.
- **verboten:**
  - Laufziele und gespeicherte Ziele fremder Einheiten (Ausnahme R3),
  - fremde Trupp-Zugehörigkeit (F10),
  - Zufallsstand (F1) und fremde innere Zähler wie Nachladezähler (R4),
  - Innenleben der Gegner-KI (Angriffspläne, Wellenzustand, AIV/AIC) und Szenario-Auslöser (F12).
- **nur Test:** Schreiben in den Speicher (R2).

Umgesetzt ist das in `data/research/auge_plan/sichtschranke.py`, das Ergebnis steht in `sichtschranke.csv` und `sichtschranke_zweifel.md`. Felder mit Ghidra-Platzhalternamen bleiben im fairen Spiel ungenutzt, bis ihre Bedeutung geklärt ist. Die Muster allein waren zu grob: Einzelkorrekturen nach der Feldliste (B-168) gehen vor und stehen Feld für Feld in `sichtschranke_zweifel.md`.

## Noch offen

- **Krari hat das Blatt nicht förmlich bestätigt.** Er stimmt allgemein zu. Seine Ampel fehlt für Z1 bis Z6, R1 bis R4, R6, F1, F3, F5 und F6.
- **Krari-Idee zu R5:** Eine freiwillige Grenze, etwa höchstens 10 Einheitengruppen, könnte zeigen, ob SamurAI auch ohne Massenstapel gewinnt. Er fragte, „wie cheaty sich das anfühlt mit 10 Schilden und 200 berittenen Bogis auf einem Punkt“. Das ist ein Kandidat für die Handicaps (Z5), keine Regel.
- **F2, weitere Fälle:** Das Auge listet Grenzen, die nur die Oberfläche prüft. Jeder neue Fall kommt hier hinein, mit Entscheidung von Daniel oder Krari.
