# Ausweichen: Senkt Zickzack die Treffer? (B-173, Plan_Gehirn Schritt 4)

Stand 08.11.2026. Zwei Läufe im Editor auf Instanz 2, jeder Takt aufgezeichnet, 1.600 Takte Beschuss je Lauf.

## Ergebnis

**Ja, Zickzack bleibt drin.** Ein Sklave (A_SLAVE, 71), der über den Befehl eines Spielers im Zickzack auf Bogenschützen (E_ARCHER, 22) zuläuft und jedes Feld die Richtung wechselt, wird ab 12 Feldern Abstand fast nicht mehr getroffen. Er schafft dabei 94 bis 97 % der Felder eines geraden Laufs.

Anteil der Pfeile, die treffen, wenn jeder Takt ein Schuss sein könnte (Lauf 2, alles über den Befehl eines Spielers, 5.640 gerechnete Schüsse je Zelle):

| Laufweg | 8 Felder | 12 Felder | 16 Felder | Felder je 1.000 Takte |
|---|---|---|---|---|
| steht | | 100 % | | 0 |
| gerade auf den Schützen zu und zurück | 92 % | 86 % | 78 % | 81 |
| gerade quer | 89 % | 58 % | 35 % | 83 |
| schräg | 69 % | 49 % | 32 % | 81 |
| Zickzack quer, Wechsel alle 2 Felder | 54 % | 35 % | 16 % | 80 |
| Zickzack quer, Wechsel je Feld | 55 % | 33 % | 16 % | 79 |
| Zickzack auf den Schützen zu, alle 2 Felder | 51 % | 20 % | 6 % | 80 |
| Zickzack auf den Schützen zu, je Feld | 25 % | 2 % | 1 % | 78 |

Die Probe, vorher festgelegt (mindestens 15 Punkte weniger als gerade ab 12 Feldern, mindestens drei Viertel der Felder): bestanden. Quer minus 24 und minus 19 Punkte, auf den Schützen zu minus 84 und minus 77 Punkte, Strecke 94 bis 97 %.

An den wirklich abgefeuerten Pfeilen (je Zelle nur 44 Schuss, siehe unten) ist es dasselbe Bild, mit einer Ausnahme: Zickzack quer je Feld bei 16 Feldern liegt nur 2 Punkte unter dem geraden Lauf (16 gegen 18 %). Gerechnet über alle Takte sind es 19 Punkte.

## Warum

Das Spiel zielt auf die Feldmitte des Läufers plus einen Vorhalt in seiner Blickrichtung (`prepareProjectileTarget`). Bei einer vom Spieler befohlenen Einheit (`stateBasedSpeed` 1) hält es doppelt so weit vor wie bei einer gehenden. Das stimmt für einen geraden Weg ungefähr. Wer nach dem Schuss die Richtung wechselt, steht nicht mehr dort.

Getroffen wird jede Einheit im Feld, durch das der Pfeil unter Boden + 42 fliegt. Wer geradewegs auf den Schützen zuläuft, bleibt in diesem Streifen, darum hilft Vorhalt-Fehler dort wenig: 86 und 78 %.

Schräg dauert ein Feld genauso lang wie gerade, darum kostet Zickzack fast keine Strecke.

## Der Preis

Je Gruppe ein Befehl je Feld. Das Spiel liest ein neues Ziel in der Feldmitte (Wissensstand 13h). Bei 12 Takten je Feld und einem Gruppenbefehl je Takt (S57) reicht das für höchstens 12 Gruppen, die jedes Feld wechseln. Im Lauf gingen 1.333 Laufbefehle auf 1.500 Takte über die Schlange des Moduls: 0 nachgeschickt, 0 Warnungen.

## Wie gut das belegt ist

| Prüfung | Ergebnis |
|---|---|
| Flug-Nachbau gegen Lauf 1 | 1.284 Pfeile, 25.106 Flugtakte, keine Abweichung, 1.248 Enden richtig, 36 enden erst nach der Aufnahme |
| Rechnung gegen die echten Pfeile, Lauf 1 | 1.144 von 1.144: Zielpunkt und Ergebnis gleich |
| Rechnung gegen die echten Pfeile, Lauf 2 | 968 von 968 Ergebnis gleich, Zielpunkt 964 |
| Eingebaute Fehler | 3 von 3 rot |

**Warum nicht einfach die 44 Schüsse:** Die Schützen schießen alle 129 Takte und alle vier gleichzeitig. Bei 12 Takten je Feld sind das nur 4 verschiedene Lagen im Feld. Die wirklichen Quoten hängen darum an der Lage und sind keine 44 unabhängigen Proben. Deshalb die Rechnung über jeden Takt, mit der echten Spur des Läufers.

**Die Vorausrechnung vor dem Lauf war zu grob:** Sie lag für Lauf 1 um bis zu 57 Punkte daneben. Sie nahm einen Schützen an, der mitgeht, und alle Lagen gleich oft. Die vorher gesetzte Grenze von 25 Punkten hat sie gerissen, sie ist damit als Rechnung widerlegt. Die Richtung stimmte.

**Der erste Lauf maß überwiegend den falschen Weg.** 22 von 26 Bahnen bekamen den Direktbefehl (`einheit_ziel`). Damit geht der Sklave nur (16 Takte je Feld, `stateBasedSpeed` 0), der Vorhalt ist halb so groß. Dass Direkt- und Truppenbefehl verschieden schnell sind, stand seit Lauf S fest, ich hatte es beim Bau nicht beachtet. Lauf 2 ist darum komplett über den Truppenbefehl gefahren, nur dessen Zahlen gelten oben. Lauf 1 steht in `ausweichen_alle_takte.txt`.

## Grenzen

- Nur Bogenschützen gegen Sklaven, ebener Boden, freies Feld, ein Läufer je Bahn.
- Nicht geprüft: Armbrust, Schleuder, Steine, Feuer, andere Läufer. Eine Assassine läuft mit Truppenbefehl 16 Takte je Feld, also langsamer als der Sklave, und wird auf Abstand gar nicht beschossen.
- Nicht geprüft: Richtungswechsel erst, wenn der Schuss gesehen wird. Das Muster hier wechselt stur.
- Mehrere Läufer nebeneinander: Ein Pfeil trifft den ersten auf seinem Weg, auch wenn er nicht gemeint war.

## Dateien

Alle unter `data/research/auge_plan/ausweichen_20261108/`: `ausweichen_rechnen.py` (Vorausrechnung), `ausweichen_auswerten.py` und `ausweichen_ergebnis.txt`, `ausweichen2_ergebnis.txt` (wirkliche Schüsse), `ausweichen_alle_takte.py` und `ausweichen_alle_takte.txt`, `ausweichen2_alle_takte.txt` (jeder Takt), `ausweichen_gegenprobe.py`, `flug_pruefung_ausweichen.txt`, `lauf_ausweichen.log`, `lauf_ausweichen2.log`. Die Szenen heißen `ausweichen` und `ausweichen2` in `src/selfaware/tools/experiments/auge_lauf_s.py`.
