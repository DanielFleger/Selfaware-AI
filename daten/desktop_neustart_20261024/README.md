# Desktop-Neustart: normaler Benutzeraufruf bestaetigt — 24.10.2026

Endgueltiger Beleg: Daniel hat nach der Umstellung der unveraendert benannten
Desktop-Verknuepfung geantwortet: "Ja, jetzt startet es". Dieser Doppelklick
(kein von Codex ausgeloester Prozessstart) steht im Dokumente-Startprotokoll:
16:59:14 Launcher10124 -> PowerShell26004 -> erhoehter Starter34788 -> Spiel11500.
worker-11500.log bestaetigt ausserdem den Controllerstart und die spaetere
SamurAI-Auswahl auf Liga_Green Trench. Das laufende Benutzerspiel blieb unberuehrt.

## Ursache und Gegenproben

Die fruehere Zusicherung war zu weitgehend: Starts aus Codex bewiesen nicht,
dass der Explorer-Doppelklick dieselbe Laufzeit sah. Die alte LNK-Datei enthielt
nachweislich LocalCache/Local/Packages/OpenAI.Codex bzw. den tatsaechlichen
Codex-Paketcache als Ziel/Arbeitsverzeichnis statt der normalen Installation.
AppData war deshalb kein belastbarer gemeinsamer Einstieg fuer Paketprozess und
normalen Desktop. Auch stabile LNK-Pfade allein loesten Daniels Ausfall nicht:
er meldete nach diesem Zwischenversuch erneut, dass der Desktop-Link nicht ging.

Gemeinsame Regel: Programmdateien, Einstieg und Lernstand liegen unter dem mit
Explorer geteilten Dokumente/Selfaware AI; kein notwendiger Startpfad liegt im
privaten AppData-Paketoverlay. Windows Shell erstellt den Link mit festen Pfaden,
abgeschalteter KnownFolder-Alias-/Verfolgungslogik; gespeicherte relative
Cache-Ziele werden abgewiesen. Es ist weiterhin ein fensterloses pythonw-Programm.

- Vor Umstellung: Codex-Start31284 erreichte Hauptmenue41, anschliessend wurden
  Testspiel und beide zugehoerigen Helfer kontrolliert beendet. Ein zweiter
  Codex-Start30548 war KEIN ausreichender Explorer-Neustartbeleg. Die gesicherte
  native Folgeprobe schlug fehl; sie wird nicht als bestandener Test verkauft.
- Nach Umstellung: normaler Benutzer-Doppelklick erfolgreich, von Daniel
  bestaetigt und zeitgleich im Dokumente-Protokoll eingetragen. Fuer die neue
  Dokumente-Fassung wurde noch kein zweiter Benutzer-Neustart behauptet.
- Migration: vorhandene AppData-Laufzeit einschliesslich ALLER Daten kopiert,
  gleiche vorher/nachher-Pruefsummen im Installationsbeleg. Original erhalten,
  keine Loeschung, kein Zuruecksetzen der gemessenen Modelle.
- python werkzeug/distribution_boundary_pruefen.py:5 bestanden, darunter
  AppData-zu-Dokumente-Uebernahme mit erhaltenem altem Modell als Gegenprobe.
- python werkzeug/desktop_shortcut_pruefen.py:2 bestanden: zwei unabhaengige
  Windows-Shell-Leseprozesse, Unicode-/Leerzeichenpfade, unveraenderter Link,
  abgeweisene relative und Codex-Cache-Ziele.
- python werkzeug/local_launcher_pruefen.py:3 bestanden: erfolgreicher Start,
  fehlende Startdatei sowie fehlgeschlagene Prozessuebergabe sichtbar behandelt.
- PowerShell-Syntaxpruefung von setup.ps1 bestanden.

completed-user-match/ sichert die zwischenzeitlich abgeschlossene Partie aus
der alten Laufzeit, mit START-BEFEHL-Konsolen, Lageprotokoll und unbestaetigten
Lernbuch-Eintraegen. Bereits vorhandene unveraenderte Karten-/Plan-Dateien liegen
in den frueheren Partiebelegen. Kein Sieg aus einem Abbruch abgeleitet.

Kein taktischer Umbau, keine Store-Freigabe. Die Dateischnittstellen-Umstellung
ist weiterhin offen; dieser Auftrag repariert den normalen lokalen Einstieg.
