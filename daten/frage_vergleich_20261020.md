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

## Ergebnis des Agenten

(wird nach seiner Rueckmeldung eingetragen)
