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

## Gemessen und gefunden (28.10. 01:33–01:36)

- **Der Kern läuft in jedem Takt.** Das Protokoll `ucp/villagestudio/samurai_kern.log` auf Instanz 5 zählt 15.340 Blöcke zu
  500 Takten mit Aufrufen = Takten. Abweichungen gibt es nur nach oben (Pause, keine Partie), nie einen ausgelassenen Takt.
  Ein Aufruf kostet 85 µs im Mittel, höchstens ~365 µs; ein Takt dauert ~5 ms.
- **Der aktive Kern** ist `samurai_kern_19.dll` (`kern_aktuell.txt`). Die Quelle liegt in `distribution/kernel/src/`:
  `lib.rs`, `haende.rs`, `welt.rs`, `wege.rs`, `leitung.rs`, `beschuss.rs`, `feuer.rs`, `waechter.rs`.
- **Vorhanden je Takt:**
  - Weltbild aller Einheiten aus dem Speicher (`welt.rs`, mit zieleinheit, zustand, laufx/y);
  - Hände, die Befehle absetzen: `haende::absetzen`, LAUF 17, ANGRIFF_EINHEIT 4, ANGRIFF_GEBAEUDE 9;
  - Auftragsbuch: Python übergibt Einheiten (`samurai_uebernehmen`) und Aufträge (`samurai_auftrag`, Ring `leitung`);
  - ein echter Reflex: `grabenreflex` (neues Ziel im selben Takt);
  - Wachen für Beschuss und Feuer, die bisher nur protokollieren.
- Eine neue Kern-Fassung lässt sich im laufenden Spiel laden: `{"kern": {"laden": "samurai_kern_N.dll"}}`, dann
  `kern_aktuell.txt`.
- **Es fehlt:**
  - Die Assassinen-Steuerung (Python) übergibt ihre Einheiten nicht an den Kern.
  - Es gibt keine Reflexe gegen Schützen.
  - Der Befehl im nächsten Takt ist noch nicht gemessen.

## Stand 28.10. 02:10 (Kern 23, Register L202)

- **R1 gebaut, nur aus Sichtbarem:** Schütze zielt oder schießt (Zustand 5/6) und blickt nach der Richtungsregel des Spiels
  auf unsere Einheit (+692), in Reichweite → im selben Takt Laufbefehl quer zur Linie. Gespeicherte Ziele (+926, +836) liest
  der Kern nicht — FAIRNESS verbietet es.
- **Reaktion belegt** (`werkzeug/r1_pruefen.py`): 194 Lagen, alle mit 0 Takten; 568 Befehle, alle spätestens 1 Takt später im
  Spiel; Gegenprobe (R1 aus) 0 Befehle.
- **Wirkung rot:** Quer ausweichen spart keinen Schaden — der Schütze dreht mit und hält vor. Nächster Schritt ist R3:
  Ausweichen am Schusstakt.
- **Kennung:** Das Buch prüft jeden Takt UID und Besitzer. Nie wieder steuert der Kern eine Einheit, deren Nummer das Spiel
  neu vergeben hat.

## Nächste Schritte (konkret)

1. **Reflex R1 „anvisiert → raus“ im Kern.** Je Takt, für jede Kern-Einheit: Ein feindlicher Schütze hat `zieleinheit` = sie
   und `zustand` 4, 5 oder 106. Das ist sichtbares Anlegen oder Schießen und laut FAIRNESS erlaubt (ANGRIFF_SICHTBAR). Dann
   gibt der Kern sofort einen LAUF auf das erreichbare Feld (`wege`) weg vom Schützen, außer Reichweite. Protokoll: Takt des
   Anlegens gegen Takt des Befehls.
2. **Reaktionszeit-Prüfung:** aus dem Protokoll, ≤ 1 Takt bei ≥ 100 Ereignissen. Gegenprobe: Reflex aus.
3. **Übergabe:** Die Assassinen-Steuerung gibt Einheiten mit Ziel und Rückzugspunkt an den Kern (`samurai_auftrag`). Python
   befiehlt übergebene Einheiten nicht mehr selbst (Besitzbuch).
4. **Danach:**
   - R2 Hit & Run: arbeiten bis kurz vor dem ersten Treffer;
   - R3 Ausweichen beim Abschuss (erst nach der Ausweich-Messung);
   - R4 Neuwahl aus der Zielliste, wenn das Ziel fällt;
   - Übergabe der Reiter, Sklaven und des Heers.

**Ergebnis 02:47 (L203):** R3 wirkt - Trefferquote 1-3 % mit Haken gegen 9-10 % ohne; Gesamtprobe R1+R3 an: 28.920 statt 100.000 Leben verloren, 0 statt 8 Tote. Naechster Schritt: Uebergabe der Assassinen an den Kern.

## R3 Haken beim Schuss (Daniel 28.10. 02:12 "ja"; Ziel: weniger Schaden als ohne Reflex)

**Sichtbar und erlaubt (FAIRNESS):** der fliegende Pfeil/Bolzen selbst - Entity-Art 1/7/24/25/33, Zustand 2, noch nicht am
Boden; seine Startstelle (x_2/y_2, wo er erschien), seine jetzige Stelle (microX/Y) und der Schuetze, aus dem er kam.
**Nicht gelesen:** der gespeicherte Zielpunkt des Geschosses (targetX/Y = Vorhalt) und das gespeicherte Ziel des Schuetzen.

**Mechanik (Auge AU24/AU25, gemessen):** Der Schuetze zielt auf die Stelle, an der die Einheit sein wird, wenn sie in ihrer
Laufrichtung weiterlaeuft (Vorhalt). Der Pfeil fliegt geradeaus zu dieser Stelle und trifft jede Einheit auf den Feldern, die er
ueberfliegt (Fremdtreffer). Flug ~1,6 Takte je Feld.

**Regel R3 (erste Fassung):** Ein Geschoss erscheint neu (UID zum ersten Mal gesehen). Seine Linie geht von der Startstelle durch die jetzige
Stelle; ist sie noch dieselbe, gilt die Blickrichtung des Schuetzen. Fuer jede Kern-Einheit wird geprueft: Steht sie vor dem
Geschoss bis 44 Felder weit und hoechstens 1,5 Felder neben der Linie? Dann schlaegt sie im selben Takt einen **Haken**: Sie laeuft
R3_WEG = 3 Felder quer zur Linie, und zwar zur Seite GEGEN ihre bisherige Laufrichtung (der Vorhalt zeigt in die alte Richtung).
Steht sie, nimmt sie die erreichbare Seite. R3 hat Vorrang vor R1. Es gibt einen Befehl je Takt.

**Messung (vorher festgelegt):** Je Haken merkt sich der Kern, wie viel Leben die Einheit hat. Ist das Geschoss weg (UID nicht
mehr fliegend), wird "getroffen" (Leben weniger) oder "verfehlt" protokolliert. Mit R3 aus prueft der Kern dieselbe Lage und
zaehlt "getroffen/verfehlt", ohne zu befehlen. Das ist die Vergleichsgruppe.
- Soll 1: Mit R3 an liegt die Trefferquote je bedrohtem Geschoss deutlich unter der Quote mit R3 aus (mindestens ein Drittel
  weniger), bei mindestens 100 Geschossen je Seite.
- Soll 2: Die Speertraeger verlieren mit R1+R3 je Takt weniger Leben als ohne Reflex (r1_pruefen 2b gruen).
- Soll 3: Reaktion auf das neue Geschoss im selben Takt.
- Widerlegt, wenn die Trefferquote mit R3 nicht sinkt. Dann ist die Annahme falsch, dass der Vorhalt einen Haken verfehlt
  oder dass nur Felder auf der Linie getroffen werden.

**GEAENDERT nach Frage-Agent (gelb, 02:14):**
- **Linie aus dem Flug:** Entschieden wird einen Takt nach dem Abschuss. Dann ist die Flugrichtung des Pfeils sichtbar und
  mikrogenau (Startstelle -> jetzige Stelle). Die 8-stufige Blickrichtung wuerde auf 20 Felder bis 8 Felder danebenliegen.
- **Seite:** Die Einheit nimmt den kuerzesten Weg aus dem Streifen (+-1,5 Felder), also zur Seite, auf der sie schon steht,
  R3_WEG = 3 Felder quer.
- **Physik offen ausgewiesen:** Protokolliert werden je Pfeil die Resttakte bis zur Einheit und der Abstand zur Linie. Die
  Auswertung erfolgt je Abstand (aus der Naehe geht es nicht: ~1,6 Takte je Feld Pfeil gegen ~13-16 Takte je Feld Laeufer).
- **Messung im selben Gefecht:** Per Zufall je Pfeil (gerade/ungerade UID) wird ausgewichen oder nur gezaehlt (Vergleichsgruppe).
  R1 ist dabei aus. "Getroffen" zaehlt nur, wenn die Einheit in dem Takt Leben verliert, in dem DIESER Pfeil verschwindet
  (+-1 Takt). Mehrere Pfeile im selben Takt sind moeglich, je Pfeil ein Befehl. Ob jeder ankommt, zeigt R1 ANGEKOMMEN.
- **Fairness-Pruefung** meldet auch das Lesen von Pfeil-Zielpunkt (targetX/Y) und Pfeil-Zieleinheit (unitID).
- Soll 1 neu: Bei Pfeilen mit >= 12 Resttakten bis zur Einheit liegt die Trefferquote mit Haken mindestens ein Drittel unter der
  der Vergleichsgruppe, bei >= 60 Pfeilen je Gruppe. Die Grundquote wird erst gemessen und dann genannt.

**Rueckweg:** Der Schalter zur Laufzeit (Einheit -2, wie R1 -1); Kern 23 bleibt im Paket.

**Stand 04.11.:** Frage-Agent ROT (28.10. 02:50): Flucht ohne Vorrang, zwei Befehlsschlangen, Schleife Haken/Fortsetzen. Nicht gebaut, Frage an Daniel offen (ein Befehlsweg). Berichtigung: Die Annahme 'nur ein Gruppenbefehl je Takt' ist nicht belegt (L203), Messbitte bei SRE; davon haengt ab, ob Warteschlange und Buendelung noetig sind.

## Uebergabe der Assassinen an den Kern (Daniel 28.10. 02:12 "ja", Schritt 3)

**Ziel:** Assassinen bekommen ihre Ziele weiter vom Lenker (Gehirn, ~100 Takte). Ausfuehren und Ausweichen macht der Kern, und
zwar jeden Takt. Danach setzen sie ihren Auftrag selbst fort.

1. **Lenker** (`erstes_spiel.py`, an der Stelle, wo die Assassinen-Befehle gesendet werden): Schalter `KERN_ASSASSINEN`
   (Rueckweg False).
   - Ist ein Kern ab Version 27 geladen (Abfrage `{"kern": {"status": true}}` beim Start), uebergibt der Lenker jede neue
     Assassine (`uebernehmen`; der Kern prueft UID und Besitzer).
   - Ihre Befehle gehen dann als Kern-Auftraege raus:
     - `angriff gebaeude` -> Kern Art 9;
     - `angriff ziel` -> Art 4;
     - `angriff lauf` und `halten` (mit Ort) -> Art 17 Laufen. Das Festhalten von logik.lua entfaellt fuer sie, der Kern laesst
       sie dort stehen.
   - `halten los` entfaellt. Einheiten anderer Steuerungen bleiben auf dem alten Weg.
2. **Kern 27, Fortsetzen:** Das Buch merkt sich je Einheit den letzten Auftrag des Lenkers. Nach einem Reflex (R1/R3) stellt der
   Kern diesen Auftrag wieder in die Schlange, sobald die Einheit am Ausweichpunkt steht oder R_FORTSETZEN = 40 Takte vorbei sind
   und keine neue Bedrohung wartet. So wird ein Gebaeudeabriss nach dem Haken weitergemacht, ohne auf die naechste Lenker-Runde
   zu warten.
3. **Der Lenker merkt den Reflex** nur an der Lage (die Einheit steht anders). Seine eigenen Fluchtregeln (Rueckzug,
   Hit&Run, Deckung) bleiben und gehen als Kern-Auftraege raus.
4. **Pruefung (vorher festgelegt):** Testgefecht mit Assassinen gegen ein feindliches Gebaeude, Armbrueste daneben (KI aus).
   Zwei frische Gefechte: Uebergabe an und aus.
   - Soll: Mit Uebergabe ist das Gebaeude mit weniger Leben-Verlust zerstoert oder es gibt weniger Tote.
   - Soll: Jede Assassine setzt nach dem Reflex ihren Angriff fort (Protokoll "FORTSETZEN"), und das Gebaeude faellt.
   - Widerlegt, wenn die Assassinen nach dem Haken stehen bleiben oder das Gebaeude spaeter oder gar nicht faellt.
   - Alte Pruefungen gruen (funde 58, risiko_lernen, zielboerse, marsch, feldzug), Fairness GRUEN.
5. **Danach in Daniels App:** Kern 27 wird zur Standard-Fassung (`samurai_kern.dll` im Laufzeit-Paket, Sicherung), und
   `erstes_spiel.py` kommt in die App-Kopie (Sicherung `.vor-B287-20261028`).

**Rueckweg:** `KERN_ASSASSINEN = False`. Die alte samurai_kern.dll (Fassung 19) liegt in der Sicherung des Zips.

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
