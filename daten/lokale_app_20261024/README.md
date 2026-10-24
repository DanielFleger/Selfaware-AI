# Lokale Anwendung nach Gynts Rueckmeldung — 24.10.2026

Belegstatus: lokaler Funktionstest bestanden; keine Store-Freigabe und kein
Spielstaerke-Benchmark. Store-PR63 wurde geschlossen, nicht als freigegeben gemeldet.

Gemeinsame Regel: UCP-Spielmodule duerfen die externe Laufzeit weder auspacken
noch starten. Installation, Prozesse und Lernstand gehoeren zur separaten lokalen
Anwendung. Die bestehende Dateibruecke bleibt dennoch nicht Store-konform.

Vorher: funktionierende Entwicklungsfassung acbbbca, gesichert als Git-Tag
local-working-20261024-observer-fix. Die neue Verteilung behaelt deren Controller
und Kernel bei; kein taktischer Umbau. OpenSHC nur als gepinnte Quellreferenz,
keine OpenSHC-DLL installiert, kein Anspruch auf vollstaendiges Spielverstaendnis.

## Nachspielbare Pruefungen

- START-BEFEHL: Start-Process -FilePath 'C:/Users/danie/Desktop/Selfaware AI (lokal).lnk' -WindowStyle Hidden
- Installation: distribution/local_setup.py, benannter Instanz5-Spielordner;
  local-install-result.json belegt unveraenderte Pruefsummen ALLER bestehenden
  Daten-Dateien unmittelbar vor/nach Installation; keine Lernstand-Loeschung.
- Gegenproben: python werkzeug/distribution_boundary_pruefen.py (4 bestanden),
  alte eingebettete Laufzeit vor Schreibzugriff abgelehnt, ZIP-Pfadausbruch
  abgelehnt, Installation wiederholt und fremde KI-Konfiguration erhalten.
- python werkzeug/uebernahme_pruefen.py (2 bestanden), einschliesslich normaler
  Senderkennung als Gegenfall zur SamurAI-Kennung.
- Frische Partie: build/final_observer_probe.py ueber native Menuefunktionen,
  !KOphase Map 1, zwei SamurAI, eigener Beobachterplatz 0. Keine Eingabeautomation,
  kein Spielstand, keine direkter-Start-Abkuerzung und keine Platzkorrektur.
- final-observer-probe.json: Uebernahme vor Tick0, Beobachter bleibt0, bei Tick409
  je19 neue Objekte. DARIN sind je14 Steinablagen enthalten; die Zahl bezeichnet
  daher NICHT19 produktive Wirtschaftsgebaeude. Konsolen belegen darueber hinaus
  erste Bauauftraege sowie nachfolgenden Farmbau und Handel beider Controller.
- Beim Verlassen: beide Lobby-KI-Werte wieder16. Partie bewusst unterbrochen;
  Lernbuch-Eintraege unbestaetigt, kein Sieg aus Konsolentext erfunden.
- Normaler erneuter Verknuepfungsstart: neuer Testprozess36916; Hauptmenue41,
  Tick0. Belegt Freigabe der vorigen Startsperre und erneuten Workerstart.
- Nur eigene Testprozesse13864 und36916 nach Programmpfadpruefung beendet.

Die zu dieser Partie neuen/geaenderten Daten liegen unter match/.
changed-files.json nennt sie. ucp3.log ist der erste Lauf (Beginn15:32:16).
Die Startverknuepfung verweist auf AppData/starter/local_start.ps1 und die
unveraenderte Laufzeit A902BEB6E4511A79. Konfiguration und Laufzeitrevision im
Installationsbeleg; kein vorheriger Lernstand in das auslieferbare ZIP kopiert.

## Grenzen

Legacy-Dateikommunikation/Snapshots ausserhalb des Modulpfads und verbliebene
feste Adressen blockieren weiterhin den Store. Auspacken zu verlagern und zu
signieren reicht allein nicht. Das --ucp-no-security-Argument gilt nur fuer den
lokalen Entwicklungsstart, keine globale Sicherheitseinstellung wurde geaendert.
Selfaware bezeichnet persistierte Messmodelle und Beobachtungen, kein Bewusstsein
oder nachgewiesene allgemeine Selbstverbesserung. Gynt wurde nicht automatisch
angeschrieben. Zuerst lokale Funktion, dann kleiner gepruefter Store-Brueckenentwurf.
