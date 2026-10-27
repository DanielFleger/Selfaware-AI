# Plan: Assassinen-Risiko mit Treffer-Verzug, Hit & Run und lernender Eichung (B-278)

Daniel 27.10.2026 23:23 (Bild: Farm rechts nie angegriffen, neue Farmen nie angegriffen), 23:27 „und natürlich mit dem Delay
selbst nach Erkennung, weil dadurch wird ein Hit and Run möglich“, „aber finde dein lernender Ansatz auch gut, bitte kombinieren“.

## Messung vorher (Partie 232139, gemessen 23:25)

- 72 von 73 Ablehnungen: „lohnt nicht (Saldo -70, Todesrisiko 100 %)“; 0 × „kein Rasterweg“; 21 NEUBAU-Meldungen (erkannt, aber
  verworfen).
- Nachgerechnet (`scratchpad/risiko_nachrechnen.py`, Lage Takt 6875, Assassine 219 → Weizenfarm 97, 12 Felder):
  Weg 58.669 + Ziel 489/Takt × 202 Takte = 98.778 → × 0,33 = 51.957 gegen 11.720 Leben → P(Tod) 1,00.
  43 Schützen in 44 Feldern; die Zellen am Ziel zählen als „gesehen“ nur über den Sicherheitsrand (Sicht-Abstand 184–211
  Feinmaß, Sicht 160).
- Ursache im Modell (`sicht.zellsatz`): jeder freie Schütze in Reichweite mit Linie schießt ab dem ersten Takt
  (Editor-Raten L81: Bogen 9,3, Armbrust 26,3 je Takt).
- Gemessen dagegen:
  - L81: Erkennen → erster Treffer 64–170 Takte.
  - 1018q: 44 Entdeckungen, 34 davon ohne Treffer.
  - Lernprofil der App (`verlust_raten.json`, Typ 73): 0,36–0,48 Leben je Schütze in Reichweite und Takt bis 15 Felder,
    0,02 bei 44.

## Was ich nicht ändern kann

Erkennen und Zielen der Schützen macht das Spiel. Die Sicht beträgt 160 Feinmaß (`acquireShootTarget`). Verborgene Ziele der
Schützen werden nicht gelesen (FAIRNESS.md). „Entdeckt“ gilt nur aus sichtbaren Dingen: wer ihn sichtbar anvisiert oder trifft
(B-234, Sichtfilter).

## Teil 1 — Treffer-Verzug (Hit & Run)

- In der Zielwahl zählt Beschuss am Ziel erst nach `VERZUG = 64` Takten (L81, untere Grenze, also die vorsichtige Seite):
  Ziel-Schaden = Beschuss × max(0, Arbeit − VERZUG).
- **Hit & Run:** Ist der volle Aufenthalt zu teuer, rechnet die Zielwahl zusätzlich „bis zur Entdeckung + VERZUG arbeiten, dann
  weg“: Aufenthalt = VERZUG, Wert = Wert × VERZUG / Arbeit. Die Annahme dahinter: Gebäude bleiben beschädigt. Das ist UNGEMESSEN
  und in der Meldung gekennzeichnet. Gewählt wird die bessere Variante je Zeit; die Meldung nennt „HIT&RUN“.
- Das Weglaufen gibt es schon: ENTDECKT → Flucht außer Reichweite, und mit `FERTIG_TAKTE` 120 macht er eine Restarbeit noch
  fertig. Neu ist nur, dass die Zielwahl damit **rechnet**.

## Teil 2 — Lernende Eichung (Vorhersage-Tagebuch, Meta 4)

- Jeder Angriff (ZIELWAHL bis Ziel zerstört, Abbruch oder Tod) schreibt die Vorhersage (Weg + Ziel, ohne Eichung) und den
  echten Lebensverlust dieser Assassine.
- `KALIB = (echt + 0,33 × PRIOR) / (vorhergesagt + PRIOR)`, mit PRIOR = Vorhersage von 3 typischen Angriffen. Der Startwert
  0,33 stammt aus B-204 (gemessen 1017h–j). Gespeichert wird je Lernprofil (`daten/lernprofile/<id>/assassinen_eichung.json`,
  wie `verlust_raten.json`).
- Die Meldung je Partie lautet: „EICHUNG Assassinen: n Angriffe, vorhergesagt X, echt Y → KALIB z“.

## Teil 3 — Probe-Assassine

- Scheitern **alle** freien Ziele nur am Todesrisiko (nicht an „belegt“, „bewacht“ oder „kein Weg“) und läuft keine Probe,
  geht **eine** Assassine mit dem meisten Leben (≥ 6.500) als PROBE auf das beste verworfene Ziel. Sie greift als Hit & Run
  an.
- Abbruch wie bei jedem Angriff (ENTDECKT → weg). Ihr Ergebnis geht in Teil 2 ein.
- Höchstens eine Probe alle `PROBE_PAUSE` = 1.500 Takte. Das ist ein Startwert, UNGEMESSEN.

## Prüfungen (Soll vorher, je mit Negativlauf)

`risiko_lernen_pruefen.py`:
1. Fall 219/97 aus der Lage nachgestellt (synthetisch): ohne Verzug P(Tod) 1; mit Verzug und Hit & Run eine wählbare Variante
   unter der Grenze, oder ehrlich „zu gefährlich“, wenn auch Hit & Run zu teuer ist.
2. Ein Ziel ohne Beschuss bleibt wie vorher.
3. Die Eichung lernt: vorhergesagt 10.000, echt 1.000 → KALIB sinkt; echt 20.000 → KALIB steigt; Datei geschrieben und
   wieder gelesen.
4. Probe nur, wenn alle Ziele am Risiko scheitern; nie zwei gleichzeitig; nicht unter 6.500 Leben.

Dazu alle bestehenden Prüfungen grün (besonders `funde_pruefen` 58 Fälle zur Zielwahl), `fairness_pruefen` GRÜN.

## NICHT dabei

Lord-Anlauf (`KALIB_LORD` bleibt 1,0), Wege-Dijkstra (der Weg-Schaden bleibt, nur die Eichung wirkt), Raids der Sklaven und
Reiter.

## Rückweg

`VERZUG = 0`, `HIT_RUN = False`, `PROBE = False`, `KALIB_LERNEN = False` → altes Verhalten. App-Sicherungen `.vor-B278-20261027`.
