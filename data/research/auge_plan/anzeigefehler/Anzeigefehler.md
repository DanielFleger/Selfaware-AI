# Anzeigefehler: Gebäude stimmen nur in der Standardansicht (B-144, 02.11.2026)

Erstellt: 02.11.2026. Daniel, 19:31: "es soll aus egal welchem Winkel normal aussehen", Spielstand `Anzeigebug`.

Marken: **gemessen** (Spiel, Speicher, Bild), **Code** (Ghidra-Export).

## Ursache

| Stufe | Befund | Marke | Beleg |
|---|---|---|---|
| Sichtbar | In Drehung 0 alles normal, in 2, 4 und 6 zerfallene Gebäude und bunte Flächen | gemessen | `vorher_nah.jpg` (oben links Drehung 0) |
| Warum | `buildings[].buildingVariation` (+0x116) stand bei 44 Gebäuden auf 0. Bei 15 zeichnet das Spiel normal. Bei anderen Werten rechnet `updateBuildingGraphicsLayer` je Kartendrehung einen Bildversatz, und das Bild landet auf fremden Bildern | gemessen + Code | `vorher_gebaeude.json` |
| Warum 0 | Meine Bau-Befehle schickten `"richtung": 0`, das Modul setzt ohne Angabe ebenfalls 0. Der Mausklick schickt 15 | gemessen + Code | `MenuItemActionHandler_InGameMenu_TriggerPlaceBuildingCommand` |
| Warum nochmal | Der Fehler war am 27.10. schon gefunden (Wissensstand 13y, B-271), die Behebung liegt aber nur im Altstand `Selfaware-AI`, nicht auf `main` | gemessen | `git log` |

## Behebung

- **Neue Gebäude:** `src/selfaware/game/ucp/drehwert.py` liefert den Wert des Mausklicks: 15, Tore 0x50/0x51 und 0/2/4/6, Zugbrücke 0. Alle festen Bau-Befehle im Code nutzen ihn oder 15.
- **Modul:** Nicht-Tore gehen immer mit 15 raus, auch wenn ein Aufrufer etwas anderes schickt. `auge_lauf_f.logik_text` spielt das in die Laufinstanz ein. Gleicher Block wie B-271.
- **Alte Spielstände:** `python -m selfaware.tools.experiments.anzeige_reparieren "<Stand>"`. Setzt den Wert, dreht einmal im Kreis, speichert unter neuem Namen, lädt neu und prüft. Der alte Stand bleibt liegen.
- **Ausgenommen:** Werkstätten rechnen ihren Wert selbst aus (alle 256 Takte, `Update...Workshop`), Tore und Zugbrücke haben eigene Regeln. Sie sahen in allen Bildern richtig aus.

## Proben, mit Vorhersage vorher

| Vorhersage | Ergebnis | |
|---|---|---|
| Wert auf 15 setzen, dann sehen alle vier Drehungen normal aus | Drehung 6 blieb zuerst falsch, weil das Spiel erst beim Drehen neu zeichnet. Nach dem Kreis alle vier normal | bestätigt, Kreis nötig |
| Überlebt Speichern und Laden, auch das erste Bild nach dem Laden stimmt | `werkzeug_nah.jpg`, vom fertigen Werkzeug erzeugt | bestätigt |
| Originaldatei bleibt unverändert | SHA-256 beginnt vor und nach allen Proben mit `b29c0c0bf66eafeb` | bestätigt |
| Frisches Spiel: alle Arten stehen mit dem richtigen Wert und sehen normal aus | 61 Arten stehen, Pechgrube hat keine Stelle. 4 Drehungen in `neu_r0.jpg` bis `neu_r6.jpg` | bestätigt |
| Außer dem Bildwert hängt kein Feld am Wert (je Art 15, 15, 0 im selben Takt, 323 Felder je Eintrag) | Bei 43 Arten trennt nur `buildingVariation`, bei 6 Arten setzt das Spiel selbst immer 15. Eingang und `surfaceAreaUnk` fielen zuerst auf, die Nachprobe mit je 6 Kopien zeigt: Zufall der Stelle | bestätigt |
| Tests werden rot, wenn man den Fix sabotiert | 6 von 6 Sabotagen erkannt, `anzeige_negativ.py` | bestätigt |

Der erste Vergleich in `neubau.json` ist **ungültig**: Das neue Modul machte aus der 0 eine 15. Gültig sind `vergleich.json` und `vergleich2.json`, per Rohbefehl.

## Nicht geprüft

- Söldnerposten, Kaserne, die beiden Gilden und der Marktplatz ließen sich nur einmal setzen, der direkte Vergleich entfiel. Sie sahen im frischen Spiel und im reparierten Stand richtig aus. Söldnerposten, Kaserne und Gilden trugen auch bei Befehl 0 schon 15.
- Alles im Burgenbau gemessen. Im Gefecht hat GRA am 27.10. die Hütte gemessen (Wissensstand 13y), die übrigen Arten dort nicht.
- Instanz 4 hat noch die alte `logik.lua` (`b.richtung or 0`). Sie gehört der Sitzung SAI und bleibt unberührt. Instanz 5 hat den Fix laut Wissensstand 13y seit 27.10., heute nicht nachgesehen.

## Nebenbei gemessen

- Eine Drehung lässt auch im angehaltenen Spiel genau 1 Takt laufen: 4 Drehungen, Takt 532.360 auf 532.364.
- Nach dem Laden steht der eigene Platz auf 0, Bau-Befehle gehen dann still ins Leere. `{"eigenerPlatz": 1}` behebt das (war schon bekannt, hat mich hier eine Probe gekostet).
