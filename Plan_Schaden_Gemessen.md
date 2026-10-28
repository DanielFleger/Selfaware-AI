# Plan: Schaden gemessen statt geschätzt + Deckung vorausdenken (B-286)

Daniel 28.10.2026 01:15: „das Problem scheint eher zu sein, dass der erwartete Schaden noch nicht richtig berechnet ist … nicht
richtig geeicht“; 01:17: „warum weiß die KI nicht, dass Gebäude schützen? … dann mache daraus das Gehirn“.

## Stand (gemessen 01:16)

- **Auge:** `sicht.linie_frei` sperrt Linien durch nicht flache Gebäude. Die Raten aus dem Editor sind gemessen
  (L75–L81): RATE_FREI 1,352 und RATE_ZU 0,070 je Schütze und Takt; je Art Bogen 9,3, Armbrust 26,3, arab. Bogen 13,3 bei
  einem zugeteilten Schützen. Das Modell `zellsatz` nimmt an, dass jeder freie Schütze in Reichweite ab Takt 1 schießt.
- **Gemessen im Spiel:** Die App-Lerndatei `verlust_raten.json` (gefahrenschutz.Lerner, je Lernprofil) hält für Typ 73 den
  Verlust je Schütze in Reichweite und Takt fest. Nach dem Abstand zum nächsten Schützen: 3 Felder 0,34, 8 Felder 0,36,
  15 Felder 0,48, 44 Felder 0,02. Das Modell rechnet sichtbar 9–26; ein Fall nachgerechnet: Farm 97 mit 489 je Takt.
- **Folge:** Die Eichung (ein einziger Faktor) wurde dreimal falsch gelernt. Proben, Routenabbruch und die 25-%-Grenze
  bauen auf diesem Fehler auf.

## GEÄNDERT nach Frage-Agent (rot, 01:20) — Daniel 01:21 „ok“

Die Lerner-Raten messen etwas anderes (jeder Schütze in Reichweite, auch hinter Gebäuden und unsichtbar, auch Nahkampf;
gemiedene Felder fehlen). Gebaut ist stattdessen (Teil 1 neu, B-286): **Schadens-Tagebuch** `schadens_tagebuch.py` — je
Runde und Einheit die Vorhersage des Modells an ihrem Ort (`sicht.beschuss(ort, nr=n)`: Sicht, freie Linie, Zuteilung)
gegen den echten Verlust, ohne Nahkampf-Runden; daraus eine **Eichkurve je Vorhersagestufe** und **je Einheitentyp**
(Datei je Typ im Lernprofil; Assassine zuerst, derselbe Baustein für Reiter/Sklaven/Heer). Unter 3.000 Takten je Stufe gilt
der bisherige Wert (sichtbar als Ersatz). Prüfung `werkzeug/schaden_kurve_pruefen.py` 6/6, 2 Gegenproben rot.
Teil 2 (Deckung vorausdenken) folgt danach, mit eigenem Zwischenspeicher und Kostengrenze (Frage 3).

## Teil 1 (ALT, verworfen) — Schaden aus den Spielmessungen

- Erwarteter Schaden je Takt an einem Feld = (Zahl der feindlichen Schützen, die es erreichen) × gemessene Rate für das Band
  des nächsten Schützen. Das ist genau so, wie der Lerner zählt (`b["schuss_takte"] += len(in_reich) * dt`, Band = Abstand
  zum nächsten).
- Die Rate kommt aus der Lerndatei des Profils. Ein Band mit weniger als MIN_TAKTE Schützen-Takten fällt auf das nächste
  gemessene Band zurück; gibt es gar keines, gilt das alte Modell × 0,33. Die Meldung nennt die Quelle („gemessen/Ersatz“,
  Regel *Ersatzwerte sichtbar*).
- Das gilt in `zellsatz` (Weg-Raster), `_beschuss_angriff` (am Ziel) und der Routen-Prüfung (B-285) — überall dieselbe
  Funktion. Der Korrekturfaktor KALIB entfällt für diese Rechnung (= 1); die Eichung bleibt nur als Gegenprobe im
  Protokoll.
- Gemessen wird weiter in jeder Partie (Lerner läuft schon) — die KI wird mit jeder Partie genauer.

## Teil 2 — Deckung vorausdenken (Gehirn)

- Beim Angriff auf Gebäude B: Beschuss am Arbeitsfeld **mit** B (jetzt) und **ohne** B (nach dem Fall). Steigt er ohne B über
  DECKUNG_SPRUNG, merkt sich die Assassine einen sicheren Punkt (wie beim Ausweichen) und läuft im selben Zug, in dem B fällt,
  dorthin. So wird nicht in offenem Feuer das nächste Ziel gewählt. Meldung: „DECKUNG FÄLLT n: Gebäude B schützt vor k
  Schützen – nach dem Abriss sofort nach P“.
- In der Zielwahl zählt der Weg weg vom Ziel (ohne B) zum Risiko, damit ein Abriss, nach dem man nicht mehr wegkommt, nicht
  gewählt wird.

## Prüfungen (Soll vorher, je Gegenprobe)

1. Lerndatei mit Bändern → Schaden je Takt = Schützen × Rate. Ohne Band → Ersatz, Meldung „Ersatz“.
2. Farm 97 (Lage Takt 6875 nachgestellt) mit den gemessenen Raten: Risiko deutlich unter 100 %.
3. Gebäude B zwischen Schütze und Arbeitsfeld: vorher versperrt, ohne B frei. Fällt B, bekommt die Assassine im selben Zug
   den Laufbefehl zum sicheren Punkt.
4. Ohne Schützen hinter B: keine DECKUNG-Meldung.
5. Alle alten Prüfungen grün (funde 58, risiko_lernen 15, zielboerse 11, marsch 7, feldzug 80); fairness GRÜN.

## NICHT dabei

Lord-Anlauf (KALIB_LORD), Reiter- und Sklaven-Gefahrenmodell (eigene Lerner-Raten, gefahrenschutz), Heer.

## Rückweg

`sicht.GEMESSEN = False` (altes Modell), `DECKUNG_VORAUS = False`. App-Sicherungen `.vor-B286-20261028`.
