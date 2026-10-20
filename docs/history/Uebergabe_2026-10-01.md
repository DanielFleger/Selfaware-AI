# Uebergabe 01.10.2026, 00:20 - Selfaware-AI

Stand fuer die naechste Sitzung. Einzelheiten und Belege: `Meilensteine.md` (Laeufe 7-11), VillageStudio `doku/Wissensstand.md` Abschnitte 13b-13f.

## Was jetzt geht (alles ohne Maus, per Befehl)

| Faehigkeit | Werkzeug | Stand |
|---|---|---|
| Spielstand speichern (auch ueberschreiben) | `werkzeug/speichern.py "<Name>"` | M7.01 belegt |
| Spielstand laden per Name, im Spiel und im Hauptmenue, Halt beim ersten Tick | `werkzeug/laden.py "<Name>"` | M7.02 abgenommen |
| Verlusttest Speichern/Laden | `werkzeug/verlusttest.py`, `verlust_eingrenzen.py` | M7.03 abgenommen als "wiederholbar statt verlustfrei" (geladene Welt ist 1 Tick weiter) |
| Kamera, Leiste, Drehen, Abflachen, Zoom | `werkzeug/navigation.py`; Modulbefehle `kamera`, `leiste`, `drehen`, `grundriss`, `zoom` | M9.01-M9.05 belegt, Live-Abnahme offen |
| Lords finden, befehligen, Ziel gegen die KI halten, Treffer/Tod melden und anhalten | `werkzeug/lordduell.py`; Modulbefehle `lords`, `lordwacht`, `zielsuche` | M4.04 belegt |
| Spielende und Sieger aus dem Speicher | `werkzeug/spielende.py` | M4.03/M4.05 belegt |

## Trainingslagen (M7.04)

- `M7-01 Speichertest Grumpy T1100` - Selbstspiel-Start, Tick 1100.
- `M7-03 Verlusttest Grumpy T1200` - dasselbe, Tick 1200.
- `M4-04 Lordduell Treffer T3354` - beide Lords in der Kartenmitte beim ersten Treffer; von dort stirbt Lord 137 (Spieler 3) immer bei Tick 4353.

## Offen, naechste Schritte

1. Live-Abnahme durch Daniel: M7.01, M9.01-M9.05, M4.03-M4.05.
2. M9.06 abgesenkte Ansicht: nur Halte-Ansicht - klaeren, ob gebraucht.
3. Drehrichtung im Bild ("rechts" = im Uhrzeigersinn?) bestimmen.
4. Modulbefehle `woSind` und `dichteste` rechnen den Ort vermutlich falsch (Kachel +0xD4 statt Mikro-Position / 8) - pruefen und angleichen.
5. Gleichstand im Lord-Duell: entscheidet die Einheitennummer, wer zuerst schlaegt? (Vermutung)
6. Weitere Trainingslagen ("erste Belagerung", "Gold knapp") und dann M8: Ansicht der KI je Tick + erste Reaktionsregel mit Reaktionszeit in Ticks.

## Betrieb

- Spiel starten: `VillageStudio/werkzeug/bis_menue.py` (10 s bis Hauptmenue); dann `laden.py "<Name>"`.
- Testsperre: `VillageStudio/werkzeug/sperre.py holen|freigeben villagestudio`.
- Deployte Modul-Logik: Kopie in `werkzeug/logik_stand_20260930.lua`.
