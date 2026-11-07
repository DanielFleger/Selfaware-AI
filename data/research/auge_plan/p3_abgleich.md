# P3: Rechenwerte im Code gegen die Messung (B-155)

**Stand:** 08.11.2026. Ohne Spielstart; verglichen wurden nur vorhandene Messungen.

**Messquelle:** `lauf_s_20261103/spielwerte_gemessen.json` und Wissensregister S1 bis S52 (Lauf S, 03./04.11.). Gemessen wurde mit UCP3 und der Team-Liga-2.0.2-Balance (`liga_ai.json`, sha256 205bf284…), im Editor und im Gefecht.

**Code-Stand:** `main` 901460f.

## Ergebnis

| # | Wert | Im Code | Code | Gemessen | Urteil |
|---|---|---|---|---|---|
| 1 | Reichweite Bogen, Armbrust, arab. Bogen, Pferdebogen (22, 23, 70, 74) | `services/sicht.py:31`, `services/schussfeld.py:16`, `services/gefecht.py` `FERN_REICH`, `micro/tasks/feldzug.py:27`; `BAENDER` 45 | 44 | **40**. 41 nicht gefahren, 42 schießt nicht. Auf der Mauer (Höhe 98) 38 ja, 42 nein (S9) | **zu groß**, siehe Hinweis A |
| 2 | Reichweite Schleuder (72) | wie 1; `BAENDER` 18 | 17 | **18**, 19 nein (S9) | 1 Feld zu klein |
| 3 | Reichweite Feuerwerfer (76) | wie 1; `BAENDER` 12 | 11 | 11, 12 nein (S9) | stimmt |
| 4 | Abstandsmaß der Reichweite | überall `max(|dx|,|dy|)` (Schach-Abstand) | Schach | Spiel prüft `dx² + dy² <= R²`, also Luftlinie (`acquireShootTarget`, aus dem Code). Gemessen wurde nur auf gerader Linie | **schräg falsch**: Auf der Diagonalen hält der Code Schützen bis 62 Felder Luftlinie für gefährlich, das Spiel schießt nur bis 40 |
| 5 | Lauftempo je Art (`gefecht.TEMPO_ART`, aus L80: Mediane aus 11 Mitschriften) | `services/gefecht.py:38` | siehe Tabelle unten | S4, S8: hängt am **Befehl**. Direktbefehl 16/24/32, Trupp- oder Angriffsbefehl meist 12 | 6 von 11 Arten weichen über 10 % ab |
| 6 | Anmarsch in der Gefechtsrechnung | `services/gefecht.py:31` `TEMPO` | 15,0 für alle | leichte Arten 12 (Trupp/Angriff) oder 16 (direkt), schwere 24, Schwertkämpfer 32 (S8) | zu grob, je Art und Befehl nötig |
| 7 | Lauftempo Assassine | `micro/tasks/assassinen.py:37` | 14,6 | **16**, direkt und im Trupp (S8) | Code hält sie für 9 % zu schnell |
| 8 | Abstandsmaß beim Laufen | meist Schach-Abstand | Schach | Schach: gerade und schräg gleich viele Takte je Feld (S4) | stimmt |
| 9 | Nahkampfschaden an der Assassine | `micro/tasks/assassinen.py:503` `NAH_SCHADEN` | 60 je Takt und Gegner, pauschal | je Takt ein Treffer in Höhe des Tabellenwerts (S3): Sklave 10, Bogen 10, Speer 25, Pike 30, Keule 70, arab. Schwert 125, Schwert, Ritter, Assassine und Lord 150 | **pauschal falsch**: Speer 2,4-mal zu hoch, Schwert 2,5-mal zu niedrig |
| 10 | Leben des KI-Lords | `services/gefecht.py:35` `LORD_LEBEN` | 150.000 | Im laufenden Spiel je KI 75.000 bis 180.000; 150.000 nur nach dem Laden eines Spielstands (K1) | gilt nur nach Laden; sonst bis Faktor 2 daneben |
| 11 | Schusstakt (steckt in den Schadensraten aus L81, `schussrate_editor.json`) | `services/sicht.py` `RATE` | beruht auf 129 / 228 / 90 / 56 / 78 Takten (Bogen, Armbrust, arab. Bogen, Schleuder, Pferdebogen) | 129 / 228 / 90 / 56 / 78 (Lauf S) | stimmt |
| 12 | Erkennen eines Ziels | `services/sicht.py:34` `SICHT` | 160 Feinmaß = 20 Felder | 20 Felder (L81); in Lauf S nicht neu gemessen | stimmt (alter Beleg) |
| 13 | Haltung: Reaktionsweite | `services/sicht.py:36` `HALTUNG_RADIUS` | defensiv 5, aggressiv 25 | defensiv 4 ja / 6 nein, aggressiv 24 ja / 26 nein (S11) | stimmt, liegt in der Lücke |

### Lauftempo im Einzelnen (Takte je Feld, Zeile 5)

| Art | Code (L80) | Trupp/Angriff (S8) | direkt (S8) | Abweichung zum Trupp |
|---|---|---|---|---|
| 22 Bogenschütze | 11,5 | 12,2 | 16 | -6 % |
| 71 Sklave | 12,0 | 12,0 | 16 | 0 |
| 70 arab. Bogen | 12,2 | 12,2 | 16 | 0 |
| 24 Speerträger | 13,5 | 12,0 | 16 | +12 % |
| 73 Assassine | 14,6 | 16,0 | 16 | -9 % |
| 72 Schleuderer | 15,0 | 12,1 | 16 | +24 % |
| 55 Lord | 19,0 | 24 | 24 | -21 % |
| 75 arab. Schwert | 19,5 | 24 | 24 | -19 % |
| 23 Armbrust | 21,0 | 24 | 24 | -13 % |
| 76 Feuerwerfer | 21,5 | 24 | 24 | -10 % |
| 25 Pikenier | 24,0 | 23,7 | 24 | 0 |

Im Code fehlen: Ritter (28) etwa 10,5 im Trupp, Pferdebogen (74) etwa 11, Schwertkämpfer (27) 32, Keule (26) 12, Mönch (37) 24.

Warum L80 abweicht, ist nicht belegt. Vermutlich mischen die Mitschriften Direkt- und Truppbefehle. Vermutlich wurde dort außerdem mit Luftlinie gerechnet, während das Spiel Schach-Felder zählt.

## Hinweise

**A. 44 war kein Versehen.** Die 44 wurde am 19.10. bewusst gesetzt (Kommentar in `sicht.py`). Anlass: In Partie 1018p löste eine Armbrust bei 42 Feldern aus. Dazu passt L91: Ein Schütze, der ein Ziel erfasst hat, schießt bis etwa 300 Takte weiter, auch wenn das Ziel schon außer Sicht ist. Die Armbrust zielt rund 137 Takte, und eine fliehende Einheit legt in dieser Zeit mehrere Felder zurück.

Es sind also zwei verschiedene Größen:
- **Erfassen:** Luftlinie bis 40 (gemessen, Spielcode).
- **Gefahr für eine fliehende Einheit:** Erfassen plus der Weg, den das Ziel während Zielen und Flug zurücklegt.

Der Code nutzt für beides dieselbe Zahl im Schach-Abstand. Für eigene Angriffe ist das zu weit, für die Flucht auf der Diagonalen viel zu vorsichtig.

**B. Grundwerte und Balance.** Die Messwerte gelten für UCP3 mit Team-Liga 2.0.2. In anderen Einstellungen (Vanilla, Ascension) können sie anders sein. Das gehört zur Testmatrix (P9).

## Vorschlag

1. **Eine Quelle für Spielwerte:** ein Modul `services/spielwerte.py`, das `spielwerte_gemessen.json` liest. Es liefert Reichweite, Tempo je Art und Befehl, Nahkampftabelle und Schusstakt. Die verstreuten Konstanten (Zeilen 1, 2, 5, 6, 7, 9) lesen künftig dort. Das Gehirn (B-152) nutzt dasselbe Modul.
2. **Reichweite aufteilen:** `ERFASSEN` = 40/40/40/40/18/11 als Luftlinie, und `GEFAHR` = Erfassen plus Fluchtweg während Zielen und Flug. Statt fester 44 wird die Gefahr aus Schusstakt, Zielzeit und Geschossflug (S10) gerechnet.
3. **Tempo je Art und Befehl** statt `TEMPO = 15` und `TEMPO_ART`. Die Assassine bekommt 16.
4. **Nahkampfschaden je Angreifer-Art** statt pauschal 60.
5. **Lord-Leben** aus dem sichtbaren Lebensbalken lesen statt fest 150.000. Das ist laut `FAIRNESS.md` erlaubt.

**Noch offen:**
- Ob das Spiel auch schräg nach Luftlinie schießt, ist nur aus dem Code gelesen.
- Die Ritter-Werte im Trupp sind unsicher.

Beides gehört in die Checkliste des nächsten Messlaufs.

## Umsetzung (08.11.2026, Daniel: „Ja, umbauen“)

- **Eine Quelle:** `src/selfaware/services/spielwerte.py` liest `spielwerte_gemessen.json`. Fehlt die Datei, gelten dieselben Messwerte als Ersatz. Es liefert:
  - `ERFASSEN` und `in_reichweite` (Luftlinie),
  - `gefahr` (Erfassen plus Weg während des Zielens, mindestens 4 Felder),
  - `takte_je_feld(typ, befehl)`,
  - `nahkampf_je_takt`, `schusstakt`, `flugzeit`.
- **Umgestellt:**
  - `sicht.REICHWEITE` und `gefecht.FERN_REICH` lesen das Erfassen (40/40/40/40/18/11).
  - `schussfeld.REICHWEITE` liest die Gefahr (44/48,6/44/44/22/15). Das Gefahrengitter zählt jetzt nach Luftlinie.
  - `gefecht.TEMPO_ART` kommt aus der Messung. Die Gefechtsrechnung läuft je Art mit dem Tempo im Angriffsbefehl und schießt nach Luftlinie.
  - `feldzug` und `waechter` prüfen „Schütze erreicht den Ort“ nach Luftlinie.
  - In der Assassinen-Steuerung: Tempo 16, `_drohende` nutzt die Gefahr, Truppen- und Stapelrechnung nutzen Luftlinie, der Nahkampfschaden kommt je Angreifer-Art.
- **Gefunden und behoben:** Die Gefechtsrechnung ließ Seite 0 zuerst ziehen, Seite 1 sah schon die neuen Orte. Wer zuerst zuschlug, hing damit an der Rechenreihenfolge, das machte bis zu 1.480 Leben Unterschied. Jetzt ziehen beide Seiten gleichzeitig. Ein Test prüft, dass ein Duell mit getauschten Seiten dasselbe ergibt.
- **Unverändert:**
  - `assassinen.py` Zeile ~1451 nutzt weiter Erfassen + `ENTDECKT_RAND` (jetzt 40 + 4).
  - `LORD_LEBEN` bleibt Ersatz. Die Rechnungen nehmen das Leben ohnehin aus dem Lagebild.
- **Prüfung:**
  - `tests/test_spielwerte.py`: 11 von 11 grün (ohne pytest gelaufen, pytest ist hier nicht installiert).
  - Die Prüfskripte ohne Spiel, alter Code gegen neuen Code, mit denselben Daten:

    | Prüfskript | Ergebnis |
    |---|---|
    | funde | 51/51 |
    | zuweisung | 10/10 |
    | waechter | 8/8 |
    | ausweichen | 21/21 |
    | schussfeld | 5/5 |
    | sicht | 10/10 |
    | raids | 13/13 |
    | entdeckung | unverändert |
    | tausch, wege | 2/3 und 3/4, wie vorher schon rot |

  - In `zuweisung_pruefen` Fall 1 erwartete der Test vorher: „Streitkolben holt eine laufende Assassine nicht ein (Tempo ungemessen)“. Gemessen läuft er 12 gegen 16. Die Erwartung ist deshalb jetzt JA.
  - `ruff` ist hier nicht installiert. Format und Zeilenlänge der zwei neuen Dateien sind von Hand auf die Regeln gebracht, aber nicht maschinell geprüft.
