# Gesamtplan SamurAI (Stand 04.11.2026)

Eine Seite. Grundlage: Brainstorming Krari und Daniel 25.10. (massgeblich sind laut Daniel die Ziele unten im Text, der obere Teil war Claude-Text),
Daniels Grundsatz 28.10. ("jeden Takt entscheiden"), Rat 04.11.
Einzelheiten stehen in `Plan_Takt_Kern.md` und `Plan_Gehirn_Sichtbar.md`. Daniel 04.11.: erst planen, Verbrauch ist knapp.

## Was seit dem 25.10. anders ist

- **Auge:** SRE meldet 373 von 376 Prüfpunkten mit Urteil; nur 202 von 1.912 Funktionen haben einen Beleg aus dem laufenden Spiel.
- **Fairness (27.10.):** Der Spielweg nutzt nur Sichtbares. Dazu gehören NICHT: KI-Absicht, fremde Laufziele, Ziele und Lager, die im
  Brainstorming unter "Eye" stehen. Das Wissen bleibt, Allwissen ist ein eigener Schalter (Daniel 04.11.).
- **Hände:** Der Kern läuft jeden Takt, Haken beim Schuss belegt (L203). Je Takt kommt ein Befehl an (SRE 04.11.).
- **Maßstab:** Der Wert "45.690 -> 34.774 Takte bis zum Sieg" stammt von vor der Fairness-Regel. Ob er fair erreicht wurde, ist nicht
  geprüft. Er muss neu gemessen werden.

## Erfolgsmaß (Daniel 04.11. 21:56)

| Stufe | Bedingung | Von wem |
|---|---|---|
| Laufend | 2v2 gegen Gardist und Kriegsfürst, fair gemessen | bisheriger Maßstab |
| **Gut genug** | Gewinnt 1v2 gegen jedes Team der Team-Liga, unter Team-Liga-Voraussetzungen, UND gegen Krari in jedem Szenario, das Krari sich ausdenkt, bei gleich viel Gold | Daniel |
| Perfekt | 1v7 gegen 7 aggressive Wölfe, alle 40.000 Gold, 5 Minuten Friedenszeit, Karte "grüner Punkt" (laut Notiz Green Haven, prüfen) | Krari |
| Zukunft | Ist sie zu gut: Handicaps, z. B. Einheiten sperren, weniger Gold, keine Starteinheiten | Daniel |

Offen: Reicht je ein Sieg oder braucht es eine Serie?

## Fair oder Cheat

F1 bis F6 hat Daniel am 04.11. 22:01 entschieden, Wortlaut in `FAIRNESS.md`. Krari gibt seine Sicht über `SamurAI_Entscheidungen.html` zurück; was er anders sieht, klären die beiden.

## Reihenfolge (die nächsten Punkte)

| # | Punkt | Ziel aus dem Brainstorming | Messung | Größe | Braucht |
|---|---|---|---|---|---|
| 1 | Krari antwortet über `SamurAI_Entscheidungen.html` | Guard Rails | Ausgefüllte Datei zurück, Abweichungen geklärt | klein | - |
| 2 | Feldliste "das sieht ein Mensch" | Guard Rails; "Eye defines the variables" | Daniel und Krari lesen sie gegen | klein | - |
| 3 | Werteabgleich mit `spielwerte_gemessen.json` | Spiel verstehen | Abweichungen je Wert, z. B. Reichweite 44 gegen 40 | klein | - |
| 4 | Befehlsweg auf Papier | Bekannte Lücken: Kampfgehirn je Einheit | Die drei roten Fragen beantwortet | klein | - |
| 5 | Befehlsweg bauen, Assassinen zuerst | Bekannte Lücken | Wartezeit je Befehl bei 40 Befehlen je Runde; Testgefecht | mittel | 4 |
| 6 | Gehirn fair (Erlaubt-Liste) | Brain | Vorhersage gegen Prüfläufe, Preisliste je Feld | mittel | 2 |
| 7 | Fairer Ausgangswert | Maßstab | Partien nach Punkt 1, neu gemessen | mittel, braucht Daniels Ja | 1, 5 |
| 8 | Weitere Einheitenarten | Bekannte Lücken: Bogen, Nahkampf; danach Einkauf wieder an | Je Art ein Sandkasten-Ziel | groß | 5, 6 |
| 9 | Testmatrix | KIs, Gold, Karten, Plätze, Versionen, Teams, Mods | Tabelle Sieg/Takte je Zeile | groß | 7 |
| 10 | Makro-Strategien vergleichen | Wirtschaft, Heer, Raid, Abwehr | Über die Testmatrix | groß | 9 |

## Wartet auf andere

- **Discord (Gynt, Krari):** Beitrag zu OpenSHC und in welcher Form; Recorder-Daten als Testdaten fürs Gehirn. Vorher nichts dazu planen.
- **Krari:** "Understanding Ghidra Assembly -> C#", "Interface mapping": Wer macht das, und braucht SamurAI es? "Crusader Compiler" meint laut
  Daniel wohl nur, wie Crusader die Dinge zusammensetzt.
- **Daniel:** Videos, Sortierung der Ziele.

## Später (Mittel- und Langfrist aus dem Brainstorming)

| Ziel | Woran es hängt |
|---|---|
| Teamspiel, Kombi-Angriffe | Punkt 8; Warenversand Befehl 113 erst messen, was ein Mensch im Menü darf |
| Zufall nutzen (Steine) | Regeln nutzen ist fair. Den Stand des Zufalls auslesen ist verborgen, also Schalter, Daniels Entscheidung |
| Rückwärtskompatibilität | Feste Adressen im Kern (Gynt 24.10.), `code_abgleich.txt`, AOB |
| AIV/AIC dynamisch, eigene Sprache, LLM-Chat | Feldliste (Punkt 2) ist ihr Wortschatz |
| SHC-API, Module im Team | Der Befehlsweg (Punkt 5) ist die Keimzelle; Gynt fragen, bevor eine eigene Schnittstelle entsteht |
| Store-Fassung | Laut Gynt nicht jetzt; Antrag #63 ist zurückgezogen |
| Englische Notizen | B-289, wenn Nachfrage entsteht |

## Offen

- **Langfrist-Ziel** ist im Brainstorming leer.
- Antwort von Krari auf das Blatt.

## Regel beim Planen

Eine Seite statt vieler. Frage-Agent erst vor dem Bauen (gemessen 93.183 und 129.786 Tokens je Prüfung). Kleine Bauschritte mit Offline-Prüflauf
sind erlaubt, wenn sie billiger sind als weiteres Planen.
