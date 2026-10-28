# Fairness-Regel fuer SamurAI (Selfaware-AI)

Festgelegt von Daniel am 27.10.2026 (19:43 / 19:46 / 19:52). Gilt fuer jeden, der an der KI baut - Menschen wie KI-Sitzungen.
Gepruft wird sie automatisch: `python werkzeug/fairness_pruefen.py` (Backlog B-274).

> **English summary:** SamurAI may perceive and act superhumanly fast (every tick, every unit), but only through actions a
> player could also trigger, and only with information a player could see on screen or learn by playing. It must never
> change the game (set values, prices, gold or goods, kill or spawn units, build for free) and never use hidden opponent
> data (the opponent AI's rules, its units' destinations or stored targets, its stockpiles). Everything must also work
> against human players.

## Der Kern in einem Satz

**Die KI darf unmenschlich schnell sehen, rechnen und steuern - aber sie spielt dasselbe Spiel mit denselben Mitteln und
demselben Wissen wie ein Mensch.**

Warum: Ziel ist eine KI, die auch Menschen schlaegt. Schummeln und verborgenes Wissen gibt es gegen Menschen nicht - ein
Sieg damit beweist nichts.

## Erlaubt

| Was | Beispiel |
|---|---|
| Jede Aktion, die ein Spieler mit Maus und Tastatur ausloesen kann | bauen, abreissen, werben, angreifen, laufen, halten, handeln am Markt, Steuern und Rationen, Truppen aufloesen |
| ... so schnell und oft wie moeglich | jeden Takt, jede Einheit einzeln, hundert Befehle je Sekunde |
| Alles lesen, was auf dem Bildschirm sichtbar ist | Positionen aller Einheiten und Gebaeude, Leben (Lebensbalken), Bewegungsrichtung, eigene Vorraete, Karte und Gelaende |
| Spielregeln, die ein Spieler durch Spielen lernen kann | Reichweiten, Schaden je Treffer, Laufzeiten, Bauzeiten, Preise - gemessen vom "Auge", gerechnet vom "Gehirn" |
| Den eigenen Platz uebernehmen | die eingebaute KI auf dem SamurAI-Platz abschalten, damit SamurAI ihn spielt |

## Verboten (im echten Spiel)

| Was | Beispiel aus dem Code |
|---|---|
| **Das Spiel veraendern** | Werte in den Speicher schreiben (`poke`), Waren oder Gold gutschreiben, Preise aendern, Einheiten setzen (`setzeEinheit`) oder toeten (`toeteAlle`), ohne Kosten bauen. Der fruehere "Einzelkauf" (Waffen einzeln per Speicher statt 5er-Los am Markt) ist darum fest aus. |
| **Verborgenes Gegnerwissen** | das **Laufziel** feindlicher Einheiten (wohin sie gehen - ein Spieler sieht nur die Richtung), ihr **gespeichertes Angriffsziel**, bevor der Angriff sichtbar ist, fremde Lagerbestaende, die Regeln der Gegner-KI aus Spielcode oder AIC-Dateien |
| **Wissen, das nur gegen Programme hilft** | "die Gegner-KI repariert immer bei X" aus dem Code abgelesen. Erlaubt ist nur, was die KI selbst aus Beobachtung lernt - das wirkt auch gegen Menschen. |

## Grenzfaelle und wie sie entschieden sind

- **Angriffsziel einer feindlichen Einheit:** gilt nur, wenn der Angriff **gerade sichtbar** ist - die Einheit schiesst oder
  schlaegt, und unsere Einheit verliert Leben. Vorher nicht (Daniel 27.10. 19:52).
- **Laufziel einer feindlichen Einheit:** nie lesen; stattdessen aus der **beobachteten Bewegung** vorhersagen (letzte
  Positionen, Richtung, Tempo).
- **Lord-Leben:** erlaubt - der Lebensbalken ist sichtbar.
- **Spielregeln vs. gespeicherter Zustand:** die Zielwahl-Regel der Schuetzen (wen ein Schuetze nach Abstand, Schusslinie
  und Reichweite waehlt) ist Spielmechanik und darf zur Vorhersage genutzt werden - angewendet auf sichtbare Positionen.
  Das im Speicher gespeicherte Ziel einer feindlichen Einheit, ihren naechsten Schusstakt oder ihr Nahkampfziel zu LESEN
  ist verboten (`shootTargetedUnit`, `sre_naechster_schuss_takte`, `attackedUnitID` - die Pruefung sucht danach).
- **Testgefechte und Messwerkzeuge** (Sandkasten, `shc.py`, Startwaren angleichen, Messlaeufe): duerfen setzen und toeten,
  aber **nur im eigenen Testaufbau, nie in einer Partie, die als echtes Ergebnis zaehlt**.
- **Reverse Engineering (das "Auge"):** erlaubt, um die Spielmechanik zu verstehen (wie Schaden, Sicht, Wege funktionieren).
  Nicht erlaubt, um im Spiel versteckte Zustaende des Gegners auszulesen.

## Wie die Pruefung arbeitet

`werkzeug/fairness_pruefen.py` durchsucht alle Module, die der Spieler-Lenker laedt:

1. Jeder Befehl, der das Spiel veraendert, muss je Funktion mit Grund freigegeben sein - sonst **rot**.
2. Der Einzelkauf muss fest aus sein - sonst **rot**.
3. Der **Sichtfilter** (`waechter.sichtfilter`) muss angeschlossen sein: Der Lenker liest das Lagebild nur ueber
   `waechter.lies_lagebild`, und dort werden bei feindlichen Einheiten das Laufziel durch die Vorhersage aus der
   beobachteten Bewegung und das Angriffsziel durch "nur wenn sichtbar" ersetzt (eigene Pruefung:
   `werkzeug/sichtfilter_pruefen.py`). Ohne Filter ist die Pruefung **rot**.
4. Jede Funktion, die Laufziel oder Angriffsziel liest, ist von Hand eingeordnet (eigene Einheit / Feind / Filter). Eine
   neue, nicht eingeordnete Stelle macht die Pruefung **rot** - wer sie einordnet, muss diese Regel befolgen.
5. Dasselbe fuer den **Rust-Kern** (`distribution/kernel/src`, entscheidet jeden Takt im Spielprozess): jede Funktion, die
   Laufziel oder Angriffsziel liest (Feld oder Speicherversatz +836/+830/+926/+928), ist eingeordnet - sonst **rot**. Die
   Gegenprobe ist ein Reflex wie Kern 20, der das gespeicherte Ziel feindlicher Schuetzen las (B-287, 28.10.2026).

Neue Funktionen, die feindliche Einheiten auswerten, nutzen nur sichtbare Felder: Position, Leben, Typ, Besitzer,
Zustand (sichtbare Taetigkeit). Fuer Bewegung gibt es die Vorhersage aus der Beobachtung.
