# Plan: Assassinen nach Entdeckungsregeln steuern (17.10.2026)

Auftrag Daniel 09:41 / 10:05 "ja": schlau und dynamisch gegen 2 Nomaden; Assassinen erhalten durch Beachten der
"beobachtet"-Trigger, Verstecken hinter Gebaeuden, Lauftempo, Ausweichen, Arbeiter auf dem Weg.
Grundlage: Wissensregister L75-L80 (17.10.), Messungen daten/angriff_raten.json, daten/gebaeude_arbeit.json.

## Gemessen / abgelesen (Grundlage, keine Schaetzung)
- Sichtbar fuer Schuetzen nur bei waehlbarem Feind (Soldat, Lord, Sklave, Moench, Belagerung) <= 160 Feinmass
  (Naeherung max + 0,4 min^2/max, 8 je Feld). Arbeiter zaehlen nicht. Pruefung alle 128 Takte, Phase = fixedRng & 127
  (Einheit +900), Takt = 0x0117CADC (gleich unserem TICK). Gebaeudeangriff enttarnt fuer Schuetzen nicht (0/2.425).
- Schuetze trifft sichtbare Assassine mit 1,35 je Takt bei freier Linie, 0,07 bei versperrter (Gebaeude dazwischen);
  Reichweite Kreis: Bogen/arab. Bogen/Pferdebogen 54, Armbrust 40, Schleuder 18, Feuerwerfer 11. Auf Turm: nie versperrt.
- Nahkaempfer verfolgen nach Haltung des Trupps: Verteidigung 5 Felder um Standplatz, Angriff 25, Stehen 0, ohne Trupp 0.
  Haltung: Tribe 0x01667F78 + 40 + Gruppe*0x334 + 0x2B8 (0 Stehen, 1 Verteidigung, 2 Angriff).
- Lauftempo Takte/Feld: Bogen 11,5, Sklave 12, arab. Bogen 12,2, Speer 13,5, Assassine 14,6, Schleuder 15, Lord 19,
  arab. Schwert 19,5, Armbrust 21, Feuerwerfer 21,5, Pike 24.
- Arbeit bis zerstoert (Assassinen-Takte, Median): Apfel 96, Holzfaeller 94, Ochse 87, Huette 194, Soeldnerposten 202,
  Markt 161, Lager 395, Eisenmine 482, Steinbruch 516, Kaserne 666. Zeit = Arbeit / Zahl (Daniel 10:10: Leben / Schaden).
- Arbeiter: Assassine nimmt ~250 Leben je Takt (Holzfaeller 10.000 -> ~40 Takte).

## Bau (neu schreiben statt flicken)
1. NEU `werkzeug/sicht.py` (ersetzt den Schadenssatz L73 in schussfeld.Gitter):
   - `Lage(L, G, sp, haltung)`: waehlbare Feinde, Schuetzen (Ort, Reichweite, erhoeht), Gebaeude-Felder (Grundflaeche aus
     VillageStudio/lib/gebaeude.json, flach = Lager/Felder), Verfolger (Ort, Art, Radius aus Haltung, Tempo).
   - `sichtbar(feld)`, `beschuss(feld)` (nur wenn sichtbar: Summe ueber Schuetzen in Reichweite, frei 1,35 / versperrt 0,07),
     `verfolgt(feld)` (Nahkaempfer, deren Radius das Feld deckt und die schneller sind -> NAH_GEFAHR-Gewicht).
   - Zellwert fuer Dijkstra = beschuss + Verfolger-Gefahr; schussfeld.Gitter nimmt die Funktion statt SCHADEN_SATZ.
   - `weg_bewerten(route, phase, tick)`: Route mit 14,6 Takten/Feld ablaufen; an jedem Pruefungstakt der Assassine
     sichtbar? -> sichtbar bis zur naechsten Pruefung; Summe Schaden. `bester_start`: Verzoegerung 0..112 in 16er-Schritten,
     kleinster Schaden (warten, bis die Pruefung vorbei ist, dann in die Zone).
2. `assassinen.py` (Einzeln) umstellen:
   - `_gitter` -> sicht.Lage; Zielwahl: Risiko = weg_bewerten + beschuss(Ziel) x Arbeit(Typ)/Zahl (statt VERWEILEN 300);
     Wegzeit 14,6 statt 15 Takte/Feld.
   - "sicher" (Warten, Rueckzug 4, Ausweichen 4b) = nicht sichtbar und kein Verfolger-Radius - statt fester Umkreise
     (SICHER_FERN 40, VORAUS_FERN 10/3 Schuetzen, RUECKZUG_FERN 40). Wartende warten nah am naechsten Ziel statt zuhause.
   - Flucht vor Nahkaempfern nur vor langsameren; vor schnelleren (Bogen, Sklave, Speer) nicht wegrennen, sondern
     kaempfen oder in Deckung/zu eigenen Truppen (Daniel 12.10. 01:37).
   - Phase je Assassine: einmal je neuer Assassine peek +900 (eingespeiste Funktion wie wegtest).
   - Lord: Beschuss am Lord fuer lord_machbar aus sicht.beschuss.
3. NICHT in diesem Bau: Arbeiter gezielt jagen/durchlaufen (erst messen, ob ein Laufbefehl vor Arbeitern stoppt),
   Flugzeit der Pfeile (Ausweichen), Gebaeudehoehen (Sperre = jedes nicht flache Gebaeude), logik.lua (nicht anfassen).

## Pruefung (vorher festgelegt)
- `sicht_pruefen.py` ohne Spiel: (a) Arbeiter neben Assassine -> nicht sichtbar, Speertraeger 19 Felder -> sichtbar,
  21 -> nicht; (b) Gebaeude zwischen Schuetze und Ziel -> beschuss = 0,07 statt 1,35; Schuetze auf Turm -> 1,35;
  (c) Route durch 6 Felder Sichtzone mit Pruefung kurz vor Eintritt -> sichtbar, mit Start nach der Pruefung -> nicht;
  (d) Gegenprobe: mit abgeschalteter Sichtregel muss (a) rot werden.
- Bestehende Proben wieder gruen: wege_pruefen, tausch_pruefen, lordanlauf_pruefen, beute_pruefen, schussfeld_pruefen
  (dort, wo sie den alten Schadenssatz pruefen, bewusst angepasst und benannt).
- Danach Partie gegen 2 Nomaden (plaetze=0,1,7, gegner=2), Mitschrift laeuft vorher; bewaehrt/nicht bewaehrt-Zeile.
  Messpunkte: Verluste je zerstoertem Gebaeude, Tode ohne waehlbaren Feind in 20 Feldern (soll ~0), Raids je 1.000 Takte.
