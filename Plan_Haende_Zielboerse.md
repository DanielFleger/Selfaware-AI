# Plan: Hände für alle Einheiten, Zielbörse, ehrliche Ablehnungsgründe (B-275 / B-277)

Daniel 27.10.2026 23:00: „Anfang besser, aber immer noch nicht schnell erkannt, wenn neue Gebäude gebaut wurden, und die
Verteilung war nicht optimal … alles auch auf alle Einheiten übertragen, nur Assassinen hilft nicht allzu viel.“ — 23:07 „ja“
zu A–C.

## GEAENDERT nach Frage-Agent (rot, 27.10. 23:12) - Daniel 23:16 "ja"

Was unten unter A steht, gilt NICHT mehr; gebaut ist:
- **A neu:** Endpunkte werden NIE verschoben (Lordtrupp `assassinen.py:2835`, `lord_sturm.py:63`, Klettern `klettertest.py` laufen
  absichtlich in ein anderes Gebiet). Kein zentraler Gelaendefilter (Reiter/Feldzug planen schon im Startgebiet,
  `gefahrenschutz.py:195`). Gebaut: nach abgelehnter WEGKETTE geht die naechste Kette dieser Einheit als Direktlauf zum selben
  Endpunkt (`besitzbuch.KETTE_ABGELEHNT`, `_direktlauf`); jede Ablehnung nennt, was auffaellt (`besitzbuch.ursache`: Gebiet
  Einheit/Ziel, Ziel an einem Gebaeude) - Auge vor Hand. Ort aus dem frischen Lagebild in `steh_runde`, kein eigenes ORT.
- **B:** wie unten (Neubau ab Runde 2, nur Gegner ohne Neutrale; Reiter verteilen sich; Jaeger pruefen bei Neubau neu).
- **C:** `r_weg >= 1e9` heisst "kein Weg im groben Gefahrenraster" (nicht "Gelaende getrennt" - der Ersatzwert gilt fuer jede
  Zelle, die der Dijkstra nicht erreicht); Zaehlung "kein Rasterweg" in der Ohne-Ziel-Zeile. Verhalten unveraendert: die naechste
  Partie misst, ob die Farmen daran oder am echten Risiko scheiterten.
- Pruefung: `werkzeug/zielboerse_pruefen.py` 11/11, je Teil ein Negativlauf rot (Verteilung, Neubau, Haende, C).

## Messung vorher (Partie 225742, App-Kopie, gemessen 27.10. ~23:05)

| Was | Zahl | Quelle |
|---|---|---|
| BEFEHL ABGELEHNT (alle Einheiten) | 31 (Vorpartie 225249: 68) | Konsole, grep |
| davon Reiter (Art 74) | 4 (310, 311: `angriff 369`, `angriff [171,200]`, `angriff [152,194]`) | Konsole |
| Wegpunkte auf Fels verworfen (nur Assassinen) | 18 | Konsole |
| neue Feindgebäude / je in einer Zielmeldung | 59 / 36 | Lage (107 Proben, grob) + Konsole, `scratchpad/neubau_messen.py` |
| Verzug > 3.000 Takte | 5 (Weizenfarmen 86/97/109, Holzfäller 91/95) — alle „lohnt nicht (Saldo -70, Todesrisiko 100 %)“ | Konsole |
| zwei Reiter auf demselben Arbeiter | Runde 9048: 310 und 311 jagen beide 369 | Konsole |

## Was ich nicht ändern kann (Plattform)

- Das Spiel lehnt einen Laufbefehl ab, dessen Feld nicht begehbar/erreichbar ist (Einheit bleibt stehen, Laufziel = eigenes
  Feld). Gesehen, nicht nachgelesen (L-Eintrag 27.10.).
- Die Wegkarte des Spiels (`speicher.wegkarte()["gebiet"]`) sagt je Feld, zu welchem begehbaren Gebiet es gehört — Lesen ist
  erlaubt (eigene Karte, sichtbar für jeden Spieler; FAIRNESS.md: Gelände ist Spielerwissen).
- logik.lua nimmt `{"angriff": {"einheiten", "lauf": [x,y], "danach": [[x,y],…]}}` (Wegkette) oder `ziel`/`gebaeude`.

## A — Hände an EINER Stelle für alle Module (`befehl.sende` → `besitzbuch.haende`)

Neu schreiben statt flicken: die Assassinen-eigene Gelände- und Direktlogik (B-275, `_gelaende_filter`, `_direkt`) bleibt als
Spezialfall stehen, aber jeder Befehl jedes Moduls läuft zusätzlich durch dieselbe Prüfung:

1. **Gelände:** je Laufbefehl (`lauf` + `danach`) werden Zwischenpunkte, die NICHT im selben Gebiet wie die Einheit liegen,
   verworfen; der Endpunkt wird, falls er außerhalb liegt, auf das nächste Feld des eigenen Gebiets bis `SCHNAPP_R = 6` Felder
   gezogen (sonst bleibt er, Meldung). Ort der Einheit: `besitzbuch.ORT` aus `steh_runde` (jede Runde gesetzt); Gebiet: einmal
   je Runde `speicher.wegkarte()`. Ohne Ort oder Karte: unverändert (nie schlechter als heute).
2. **Direktlauf nach Ablehnung:** wurde eine Wegkette der Einheit abgelehnt, geht die nächste Wegkette nur als Endpunkt
   (`lauf` = letzter Punkt, ohne `danach`) — das Spiel sucht den Weg selbst. Wird auch das abgelehnt, greift die vorhandene
   Wiederholungssperre (5 Runden).
3. **Meldung je Eingriff** (eine Zeile, Modul genannt): `HAENDE n (Modul): k Wegpunkte auf fremdem Gebiet verworfen …`,
   `HAENDE n: Ziel (x,y) auf Fels -> (x',y')`, `HAENDE n: Direktlauf nach Ablehnung`.

Beziehungen, beide Richtungen:
- besitzbuch → befehl: besitzbuch kennt Ort und Ablehnung; befehl ruft `haende()` vor `filtern()`.
- Module → besitzbuch: Module erfahren nichts davon (müssen nichts ändern); ihre Steh-Zeile zeigt den Eingriff.

## B — Zielbörse je Runde (`zielboerse.py`, Meta 1 Feldherr, erster Teil)

1. **Neubau-Erkennung:** je Runde Feindgebäude (über `uid`, Rückfall `nr`+Ort) mit der Vorrunde vergleichen →
   `NEUBAU Gebäude n Typ t bei (x,y)` und Menge `NEU` dieser Runde. Nur sichtbare Gebäude (Gebäude sieht jeder Spieler).
2. **Belegung:** Module melden ihre Ziele an (`beanspruchen(ziel, einheit, modul)`); `belegt(ziel, ohne=einheit)` zählt.
3. **Reiter:** Reiter wählen zuerst unter Zielen, die kein anderer Reiter dieser Runde hat; nur wenn alle belegt sind, ein
   belegtes (Meldung „teilt Ziel mit …, weil kein freies“).
4. **Assassinen bei Neubau:** gibt es `NEU`, werden in DIESER Runde auch Jäger (Arbeiterjagd, nicht im Nahkampf) und Wartende
   neu bewertet: Zielwahl wie für Freie; findet sie ein Gebäude mit Saldo > 0, wechseln sie (`NEUBAU-WECHSEL n: Jagd auf a ->
   Gebäude g`), sonst behalten sie ihre Jagd. Der bestehende Zielwechsel für Gebäude-Angreifer bleibt.
5. **Sklaven (Brandtrupp):** melden ihre Ziele an; bei `NEU` prüft jeder Sklave ohne Ziel sofort (heute schon jede Runde) —
   nur Anmeldung, keine Verhaltensänderung.

## C — Ablehnungsgründe ehrlich trennen

In der Zielwahl der Assassinen: liefert das Gefahrengitter keinen Weg (`r_weg >= 1e9`), heißt der Grund „kein Weg im
Gefahrengitter (Gelände getrennt)“ statt „lohnt nicht (Saldo -70, Todesrisiko 100 %)“, und dieses Ziel zählt nicht als
„gefährlich“. Am Verhalten ändert sich nichts (das Ziel bleibt unwählbar) — nur die Wahrheit im Protokoll.

## Prüfungen (Soll vorher, je mit Negativlauf)

`haende_pruefen.py`: (1) Zwischenpunkt auf fremdem Gebiet fällt weg, (2) Endpunkt auf Fels wird auf eigenes Gebiet gezogen,
(3) ohne Karte unverändert, (4) nach Ablehnung einer Kette geht die nächste als Direktlauf, (5) Befehle ohne `lauf` unberührt,
(6) Assassinen-Einzelpunkt-Lauf bleibt ein Einzelpunkt.
`zielboerse_pruefen.py`: (1) neues Gebäude wird in der ersten Runde gemeldet, (2) altes nicht, (3) zwei Reiter, zwei Ziele →
verschiedene Ziele, (4) zwei Reiter, ein Ziel → teilen mit Meldung, (5) Jäger wechselt bei Neubau mit Saldo > 0,
(6) Jäger behält Jagd, wenn der Neubau nicht lohnt.
Dazu alle bestehenden Prüfungen grün, `fairness_pruefen` GRÜN (neue Leser in LESER eintragen).

## Was ausdrücklich NICHT dazugehört

Kaufentscheidung ändern (B-276 hat nur geloggt), Gruppen/Formationen (Meta 2), Taktring je Tick (B-145), Heer-Aufstellung.

## Rückweg

Je Teil ein Schalter: `besitzbuch.HAENDE = False`, `zielboerse.AN = False` → altes Verhalten. App-Kopie mit
`.vor-B277-20261027`-Sicherungen.
