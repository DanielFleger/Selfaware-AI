# Sichtschranke: Ergebnis und Zweifelsfälle (P2)

Erzeugt von `sichtschranke.py` aus `zustand_felder.csv` nach den Regeln in `docs/FAIRNESS.md`.

**3564 Felder.** Eigene Daten: erlaubt 1082, unbekannt 983, technik 865, verboten 634. Fremde Daten: verboten 2094, technik 633, erlaubt 533, schaetzen 304.

- **Sicher eingeordnet:** 2581
- **Bedeutung unbekannt** (Ghidra-Platzhalter, im fairen Spiel ungenutzt, bis benannt): 983
- **Feinarbeit** (benannt, aber noch ohne passende Regel; im fairen Spiel vorerst ungenutzt): 0 in 
- **Fragen an Daniel und Krari:** 0 Felder in 0 Gruppen. Je Gruppe reicht eine Entscheidung, sie gilt dann für alle Felder darin.

## Feinarbeit (alle Grundsatzfragen entschieden, Daniel 08.11.2026)

| Bereich | Regel | Felder | eigen | fremd | Beispiele |
|---|---|---|---|---|---|
