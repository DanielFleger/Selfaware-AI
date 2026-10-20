# Plan: modularer Umbau in Engines (Stand 05.10.2026, 23:26)

Anlass (woertlich):
- Daniel 23:14: "immer DRY und modular und funktional".
- Daniel 23:18: Sharky (github.com/sharknice/Sharky) als Architektur-Vorlage.
- Daniel 23:24 (Krari im Call bestaetigt): "das ganze modular machen - eine Micro-Engine fuer Angriffe, eine fuer
  Verteidigung, eine fuer Raids, eine fuer Wirtschaft und dann jeweils zum Scaling."
- Daniel 23:25: "wichtig ist, dass die Ressourcen maximal bringend benutzt werden - nicht nur fuer Raiden, sondern eine
  Balance aus Wirtschaft, die maximales Geld bringt; und dynamisch ueber Zeit: eine Investition wie eine Hopfenfarm
  bringt jetzt nichts, aber spaeter Bier usw."

Gebaut wird erst nach Daniels Ja, Schritt fuer Schritt (eine Engine je Schritt, Pruefung ohne Spiel + Saat-Partie).

## Heute (Ist)
`erstes_spiel.py` ist Lenker UND Eroeffnung UND Anwerben UND Verkaufen; daneben `wirtschaft.py`, `ertragsplaner.py`,
`waechter.py`, `assassinen.py` (Raid, Ausweichen, Kreisen, Stapel, Lord-Angriff in einer Klasse) - jedes mit eigener
Schnittstelle. Gold-Vorrang ist ein Flag (`braucht_gold`), das andere blockiert (bremse_2: 28.700 Ticks, 1 Assassine).

## Ziel (nach Sharky, angepasst)

```
Lenker (eine Schleife je Runde, Spielzeit in Ticks)
 |- Lagebild           ein Objekt je Runde: Einheiten, Gebaeude, Vorrat, Gefahrenkarte (Schussweite 40, Nahkampf)
 |- Haushalt           verteilt Gold/Holz/Stein/Leute je Runde auf die Engines nach erwartetem Ertrag
 |- Engines (gleiche Form: start(), runde(lage, budget) -> befehle + bedarf, bericht())
 |    |- Wirtschaft    Investitionen mit Ertrag ueber die Zeit (auch Ketten: Hopfen -> Brauerei -> Schenke -> Bier)
 |    |- Raid          Assassinen auf Wirtschaftsziele, Ausweichen, Kreisen/Weglocken
 |    |- Verteidigung  eigene Burg und Lord schuetzen (Lord nie in den Kampf gegen Assassinen)
 |    |- Angriff       Sammeln bis Uebermacht, alle gleichzeitig auf den Lord
 |- Einheiten-Befehler letzter Befehl je Einheit; neu nur bei Aenderung/Stillstand (kein Stop-and-go)
 |- Befehlskanal       Quittung statt fester Wartezeit (steht)
```

**Jede Engine meldet ihren Bedarf mit erwartetem Ertrag** ("70 Gold -> 1 Assassine -> ~X Gold Schaden beim Gegner bis
Spielende", "15 Gold + 3 Holz -> Apfelplantage -> Y Essen bis Ende", "Hopfenfarm -> Bier ab Tick T -> Beliebtheit ->
Steuern"). Der **Haushalt** vergleicht die Ertraege je eingesetztem Gold ueber den Rest der Partie (dynamisch: eine
spaete Ernte zaehlt erst ab ihrem Erntezeitpunkt) und teilt zu. Kein Flag blockiert eine andere Engine mehr.

**Scaling je Engine:** Regeln haengen an Zahlen, die mit der Partie wachsen (Zahl der Assassinen, Gold je 1.000
Ticks, Wachen am Ziel) - z. B. Raid ab 1 Assassine, Weglocken ab 2, Uebermacht-Angriff auf Wachen ab N+1, Lord-Angriff
ab kritischer Menge; Wirtschaft von 3 Apfelplantagen bis zu Ketten (Hopfen/Bier, Eisen -> Waffen).

## Schritte (je einer, mit Pruefung ohne Spiel + Saat-Partie gegen den alten Stand)
1. Gemeinsame Engine-Form + Lagebild-Objekt; die vier bestehenden Teile darin verpacken, Verhalten unveraendert
   (Gegenprobe: Saat-Partie bis 8.000 gleiches Ergebnis wie vorher).
2. Haushalt mit Ertrag je Gold ueber die Restzeit; `braucht_gold` faellt weg.
3. Einheiten-Befehler fuer alle Einheiten.
4. Raid-Engine: Weglocken (Stufe 2) und Uebermacht-Angriff auf Wachen (Stufe 3).
5. Verteidigungs-Engine: Lord raus aus dem Kampf gegen Assassinen.
6. Wirtschafts-Engine: Ketten (Hopfen -> Bier), gemessene Ertraege je Gebaeude ueber die Zeit.
7. Angriffs-Engine: Sammeln ausser Schussweite, gleichzeitig auf den Lord.

## Ausdruecklich NICHT in diesem Plan
- AOB / Spielversionen (Extreme, Stronghold 1): eigener Auftrag, betrifft das gemeinsame Modul `logik.lua`.
