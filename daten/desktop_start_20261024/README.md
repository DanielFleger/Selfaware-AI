# Desktop-Start ohne kurzes Terminal — 24.10.2026

Belegt: Die bestehende Desktop-Verknuepfung heisst weiterhin Selfaware AI (lokal)
und traegt das Crusader-Symbol. Ihr Ziel ist jetzt das installierte pythonw.exe
(PE-Subsystem2, Fensterprogramm). Argumente sind nur der externe Starter und
seine Installationsdatei. Kein direkter Terminal-Aufruf mehr.

Ausgang: Daniel meldete Terminalblitz und anschliessend kein Spiel, ohne
Windows-Abfrage. Zum gemeldeten Klick gab es keinen Startprotokoll-Eintrag.
Dieser konkrete Abbruch liess sich bei meinem Befehlsaufruf nicht reproduzieren;
die vorigen Funktionsproben waren deshalb keine ausreichende Gegenprobe fuer
Daniels Doppelklick. Keine erfundene genaue Ursache fuer den gemeldeten Abbruch.

Gemeinsame Regel: Der Einstieg muss VOR jeder Prozessuebergabe protokollieren,
fensterlos sein und Fehler vom Kind bis zur sichtbaren Meldung zurueckgeben.
Vorher beendete sich der nicht erhoehte PowerShell-Starter sofort mit0 nach dem
Anfordern des erhoehten Kindes. Jetzt wartet er und uebernimmt dessen Ergebnis.
Der vorgelagerte pythonw-Starter faengt auch Interpreter- und fehlende-Datei-
Fehler auf. Fehler werden sichtbar gemeldet, nicht als Erfolg verschluckt.

Pruefungen:
- python werkzeug/local_launcher_pruefen.py:3 bestanden; positiver Start mit
  Leerzeichen in Pfaden, fehlendes Startskript VOR Prozessstart, gescheiterter
  Prozessuebergang mit sichtbarer Fehlermeldung (Benachrichtigung im Test ersetzt).
- python werkzeug/distribution_boundary_pruefen.py:4 bestanden, insbesondere
  unveraenderte Lerndaten und fremde KI-Einstellungen bei erneuter Einrichtung.
- PowerShell-Syntaxpruefung von local_start.ps1 bestanden.
- START-BEFEHL: Start-Process -FilePath 'C:/Users/danie/Desktop/Selfaware AI (lokal).lnk' -WindowStyle Hidden
- Tatsaechlicher Windows-Verknuepfungsaufruf: pythonw36880 -> PowerShell22044 ->
  erhoehter Starter3788 -> Spiel29424 -> externer SamurAI-Controller.
  launcher.log, local-start.log, bootstrap-29424.log und worker-29424.log belegen
  die Uebergaben. native-probe: Hauptmenue41, Tick0, exakter Instanz5-Programmpfad.
- Installation: alle vorher vorhandenen Datenpruefsummen erhalten, siehe
  install-preserved-learning.json. Keine taktischen Aenderungen.

Das neu gestartete Spiel wurde fuer Daniels Test OFFEN gelassen. Keine Maus-,
Tastatur-, Fokus- oder Fenstersteuerung. Kein neues Gefecht automatisch begonnen.
Die Dateischnittstellen-Umstellung wurde fuer diesen gemeldeten Startfehler
unterbrochen; sie ist mit dieser Starteraenderung NICHT erledigt oder Store-geprueft.
