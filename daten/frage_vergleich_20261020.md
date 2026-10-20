# Vergleich: eigene Fragen vs. Frage-Agent zu Plan_Kern.md (20.10.2026)

Daniel 22:52: "wenn er zurueck ist, schauen wir, ob du mit weniger Tokens auch zu den gleichen Ergebnissen gekommen waerst -
sonst koennen wir uns den Agenten sparen". Diese Datei ist VOR dem Ergebnis des Agenten geschrieben und committet (22:55),
ohne neue Dateien zu lesen - nur aus dem, was ich in dieser Sitzung schon gesehen hatte.

**Was als Ergebnis zaehlt (vorher festgelegt):** Findet der Agent eine Schwaeche, die in meinen drei Fragen fehlt UND die den
Plan aendert (Stufe, Rueckweg, Pruefpunkt), hat er sich gelohnt. Deckt er nur dasselbe ab oder Kleinigkeiten, nicht.

## Meine Ampel: GELB - S0 kann starten, aber Frage 2 gehoert vorher in den Pruefpunkt von S0

1. **Haende haengen an logik.lua.** S2 soll ueber queueCommand mit Absender-Stempel handeln - der Stempel wirkt aber nur,
   weil logik.lua beim Laden einen Sprung in processWaitingCommands einbaut (B-94, 0x00489387, Rueckweg "absender aus").
   Der Plan sagt "Kern ruft Lua nie" - verschweigt aber diese Abhaengigkeit. Was passiert, wenn der Kern Befehle absetzt
   und der Umbau nicht eingebaut ist? (Nach Spielkarte 1: dann gelten sie fuer "ich" - also fuer Daniel.)
2. **Tausch und Laden - ungemessen.** Der Stecker entlaedt einen Rust-Kern (std, Datei-Ein/Ausgabe, windows-gnu) mit
   FreeLibrary mitten im Spiel; ob das im Spielprozess ohne Absturz geht, ist nicht gemessen. Und: woran erkennt der Kern
   einen geladenen Spielstand oder eine neue Partie (im Protokoll 107 Spruenge), damit sein Gedaechtnis (Plaene, Ziele)
   nicht in die naechste Partie mitlaeuft?
3. **Zwei SamurAIs auf einer Instanz.** Im 2v2 spielen zwei SamurAIs in EINEM Spiel (B-133). Der heutige Aufruf
   `samurai_takt(tick, spieler)` kennt einen Spieler ("ich"). Der Plan sagt nicht, ob ein Kern alle eigenen Plaetze lenkt
   oder einer je Platz - davon haengen Gedaechtnis, Befehls-Stempel und Leitung (S4) ab.

## Ergebnis des Agenten (23:03; Sonnet 5.5, Stufe max: 313.807 Tokens, 68 Werkzeugaufrufe, 19 min 46 s)

Ampel GELB. Seine drei Fragen (alle Belege von mir nachgelesen, 23:05):
1. **Wann laeuft der Kern wirklich?** init.lua Z. 783-788 ruft ERST `originalGameTick`, DANN `onTick` - der Kern laeuft nach
   dem Takt, nicht davor; er laeuft auch in der Pause (logik.lua Z. 956); 40 von 2.346 Protokollzeilen mit leerer Welt
   (nachgezaehlt: 40, davon 20 mit Tick 197223). **Meine Aussage in Plan, Spielkarte und L154 war falsch.**
2. **Wer darf einer Einheit befehlen, und was hindert den Kern, laufende Einheiten jeden Takt neu zu befehlen?** L152 Punkt 4
   (eigene Messung: neuer Befehl = Wegsuche neu, niemand kommt vom Fleck); Krarilotus' Regel "do not create a second writer".
3. **Ist gemessen, dass eine neue Fassung einen Neustart braucht - oder nur, dass DIESELBE Datei gesperrt ist?** UCP3 prueft nur
   den Ordner, nicht den Namen; "kaputte Fassung wird abgelehnt" geht mit panic=abort gar nicht.
Dazu gefunden: Krarilotus hat den Kern auf origin schon nach `crates/samurai-kern` verschoben (MSVC-Ziel, CI).

## Vergleich (nach dem vorher festgelegten Massstab)

| | ich (22:52) | Agent (23:03) |
|---|---|---|
| Falsche Tatsache im Plan gefunden (Takt-Reihenfolge) | nein | **ja** |
| Krarilotus' Kern auf origin gefunden | nein | **ja** |
| Ein Schreiber je Einheit / kein Dauer-Neubefehl | nein | **ja** |
| Neustart noetig? (vielleicht kein Stecker) | halb (Entladen ungemessen) | **ja, schaerfer** |
| Laden/neue Partie erkennen | **ja** | ja (als Folge von 1) |
| Absender-Abhaengigkeit von logik.lua | **ja** | nur als Beleg erwaehnt |
| Zwei SamurAIs in einem Spiel (2v2) | **ja** | nein |

**Urteil: Der Agent hat sich diesmal gelohnt** - drei Funde, die bei mir fehlten und den Plan aendern (S0 neu, S2 neu,
Bauort), einer davon eine falsche Tatsache. Meine zwei eigenen Funde (Absender, 2v2) sind ebenfalls in den Plan gegangen.
**Warum er gewann:** nicht klueger, sondern er hat jede Belegzeile, die der Plan nennt, selbst geoeffnet; ich hatte die
Takt-Reihenfolge aus einem Kommentar ("die wir stehlen" = Haken am Anfang) geschlossen, ohne die drei Zeilen darunter zu lesen.
(Korrektur zu oben: die Datei wurde um 22:52:52 committet, nicht 22:55.)
