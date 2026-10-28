# Plan: SamurAI entscheidet jeden Takt (B-145 neu, „SAK – Takt-Kern“)

Daniel 28.10.2026 01:28: „sie soll literally jeden Takt entscheiden. Das ist der Grundsatz, sonst kannst du alles andere
vergessen.“ 01:29: „ich werde kein neues Spiel starten, bis du mir versprechen kannst, dass wirklich die SamurAI jeden
einzelnen Tick entscheiden kann.“

## Ist-Stand (gemessen 28.10. 01:30)

- Entschieden wird nur im Python-Lenker (`werkzeug/erstes_spiel.py`, Phase 2). Eine Runde dauert etwa 100 Takte (Partie
  232139: 94 Runden auf 9.957 Takte; „0,7 s je Runde“ in 005506).
- Jeden Takt im Spiel läuft schon:
  - `takeover.lua` (vor jedem Takt);
  - `taktring.lua` (kopiert Einheiten, Geschosse und Gebäude in einen Ring, B-251);
  - `samurai_kern.dll` (Rust, `samurai_kern/src`). Sie hat heute nur `samurai_takt(tick, spieler)` und Zähler, keine
    Entscheidung.
  - Der Arbeitsordner `Selfaware-AI-kern` (Zweig kern-s0) steht auf dem Stand vom 21.10.
- Gemessene Schuss-Kette (L81): Anlegen, dann Abschuss nach 56/137/28/20 Takten, Treffer 64–170 Takte nach dem Anlegen,
  Flug ~1,6 Takte je Feld.

## Was „jeden Takt entscheiden“ technisch heißt

Python kann keinen Takt treffen: Eine Runde braucht heute rund 0,7 s, ein Takt bei Tempo 40 etwa 25 ms. Entschieden werden
muss deshalb **im Spielprozess**, also im Kern (Rust-DLL), aufgerufen in jedem Takt aus `logik.lua`.

**Zwei Ebenen (Meta-Leiter):**
- **Kern = Hände und Reflexe, JEDEN Takt, für JEDE eigene Einheit.** Er liest den Takt direkt aus dem Speicher, ohne Umweg
  über Dateien. Er entscheidet und befiehlt im selben Takt:
  - Ausweichen vor einem sichtbar angelegten Schuss;
  - Rückzug, sobald ein Schütze sie anvisiert;
  - Hit & Run: arbeiten bis kurz vor dem ersten Treffer, dann weg;
  - Weiterlaufen der Route;
  - Neuwahl aus der Zielliste, wenn ein Ziel fällt, Deckung wegfällt oder ein Neubau auftaucht;
  - Lord-Wettlauf-Abbruch.
- **Python-Lenker = Gehirn, alle ~100 Takte.** Er macht Wirtschaft, Kaufentscheidungen, Feldzugsplan, Zielranglisten und
  die Eichkurve. Er schreibt **Absichten** in einen Speicherblock: je Einheit Ziel, Route und Risikogrenze, dazu
  Zielranglisten. Der Kern liest sie jeden Takt.

## Messbares Versprechen (die Prüfung, die es belegt)

- **Reaktionszeit-Prüfung im Sandkasten (freie Instanz 3):** Ereignis-Takt (Schütze legt an, Gebäude fällt) gegen den Takt,
  in dem der Befehl des Kerns im Spiel ankommt. Soll: **≤ 1 Takt**, über 100 Ereignisse, mit Protokoll.
- Gegenprobe: Kern aus → die Reaktion kommt erst mit der Lenker-Runde (~100 Takte) → rot.
- Erst wenn diese Prüfung grün ist, gilt „SamurAI entscheidet jeden Takt“ als belegt, und Daniel startet eine Partie.

## Schritte

1. **Messen:**
   - Laufen `samurai_takt` und `taktring` wirklich in jedem Takt? Gibt es Takte, die das Spiel innerhalb eines Bilds doppelt
     rechnet (B-251: bei 100 Takten/s jedes vierte Bild zwei Takte)? Der Kern muss im Takt-Haken hängen, nicht im
     Bild-Haken.
   - Wie lange darf der Kern je Takt rechnen (Kostengrenze)?
   - Kann ein Befehl aus dem Kern im selben Takt wirken (Laufbefehl wie ein Klick)?
2. **Kern-Grundgerüst:** Absichten-Speicher (Python → Kern), Einheiten-Lagebild je Takt aus dem Speicher und
   Befehlsausgabe im Takt, alles mit Takt-Protokoll.
3. **Erste Reflexe:** Rückzug bei Anvisieren, Ausweichen beim Abschuss (erst nach der Ausweich-Messung) und Neuwahl,
   wenn das Ziel fällt.
4. **Reaktionszeit-Prüfung grün**, dann Partie.
5. Danach Schritt für Schritt mehr in den Kern: Wegverfolgung, Wettlauf, Sammeln. Alles bleibt fair, nur sichtbare Dinge,
   FAIRNESS.md.

## Nicht dabei

Wirtschaft und Kaufen bleiben im Lenker. Die Zielwahl-Rechnung bleibt in Python und liefert nur Ranglisten.

## Rückweg

Kern-Reflexe sind je Schalter abschaltbar; der Lenker funktioniert weiter wie heute.
