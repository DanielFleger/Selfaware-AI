# Auftrag an Codex: Das Auge vollständig machen (B-267, Schritt 2)

Erstellt: 27.10.2026 18:05 von Claude (Sitzung SAI) auf Daniels Wunsch. Daniel: "im Endeffekt darf im Code keine Zeile
unerklärt sein".

## Wo du arbeitest
- Dieser Ordner: `Tools/Selfaware-AI-auge` = eigener git-Arbeitsbaum, Zweig `codex/auge` (vom Stand `main` 209cadf).
  Nur hier arbeiten. `Tools/Selfaware-AI` (main) gehört der Claude-Sitzung SAI (Gehirn) - dort nichts ändern.
- Commits lokal auf `codex/auge`. **Nicht pushen, nicht mergen** - das entscheidet Daniel.
- Ghidra-Projekt mit der benannten Spielanalyse: `C:\Users\danie\ghidra-projects\OpenSHC-ref` (Basis OpenSHC).
- Daniels Spiel auf Instanz 5 (`...\Stronghold Crusader Extreme Instanz5`) nie anfassen. Eigene Messungen nur in einer
  freien Instanz und nur mit Daniels Ja.

## Was schon gemessen ist (Schritt 1, Sitzung SRE, Commit d0f09dc)
- `daten/auge_abdeckung_funktionen.csv` (4.581 Funktionen), `daten/auge_abdeckung_felder.csv` (1.666 Felder),
  `daten/auge_abdeckung.json` (Zahlen + Regel). Neu erzeugen: `python werkzeug/engine_knowledge/auge_abdeckung.py`
- Stand 27.10. 17:54: Funktionen 171/4.581 erklärt, **Spiellogik 163/1.938 (8,4 %)**; Felder **285/1.666 (17 %)**;
  das Auge (`werkzeug/auge.py`) liest 296 Felder, **101 davon unerklärt**.
- Je Struktur erklärt/Felder: Einheit 114/275, Gebäude 41/239, Geschoss 34/93, Trupp 19/89, Spieler 42/388,
  KI-Vorgaben 11/169, Karte/Zeit 6/230, Weltkarte 18/183.
- Regel "erklärt": eine Zeile im `Wissensregister.md` (AU/P/L/W/B/G/S/A) nennt Adresse oder Namen; "widerlegt" zählt nicht.

## Ziel und Abnahme (berichtigt 29.10.2026)
Jede Funktion und jedes Feld nachvollziehbar erklaeren. Eine Registererwaehnung oder Teilbeschreibung ist keine
vollstaendige semantische Abnahme. Historische Zahlen oben stammen aus der alten Wort-/Adresssuche.
- Funktion: feste Adresse, Hash der tatsaechlichen Exportdatei, Eingaben, Rueckgaben, Schreibfelder, Bedingungen,
  Grenzwerte, Sonderfaelle, Aufrufer-/Hilfsabhaengigkeiten, offene Fragen und konkrete Gegenprobe festhalten.
- Nur ausdruecklicher Status abgenommen mit allen Pflichtangaben, keiner offenen Frage und passenden Quell- und
  Registerhashes zaehlt semantisch. Geaenderte Quellen, entfernte Belege oder fehlende Gegenprobe machen ihn ungueltig.
- Felder: eindeutige Bindung aus Struktur, Offset, Groesse und Feldname in daten/auge_feldbelege.csv; zusaetzlich
  Registermarke und deren Hash. Namens- oder Offsettreffer allein bleiben blosse Erwaehnungen.
- Die 1.938 als Spiellogik benannten Funktionen sind ein vorlaeufiger Nenner. Funktionen ohne Namensraum bleiben
  unklassifiziert; auch unter Global gezaehlte reine Menue-/Grafikfunktionen (00424BD0/00424BE0, PK311) und technische Ausschluesse muessen fachlich geprueft werden, bevor Vollstaendigkeit behauptet wird.
- Paketgegenproben pruefen die Zuordnung, nicht die Wahrheit der Erklaerung. Fachliche Gegenfaelle (Grenze daneben,
  invertierte Bedingung, Nullfall, Seiteneffekt) gehoeren gesondert zur Abnahme.
- Kein Prozentziel darf offene Rekonstruktionen in sichere Bedeutungen verwandeln.
- Die technische Sperre prueft Pflichtangaben und Pruefsummen; ob ein eingetragener Gegenprobentext fachlich traegt, muss der Pruefer weiterhin am Original entscheiden. Ein gefuelltes Formular ist kein automatischer Wahrheitsbeweis.

## Feste Pruefreihenfolge (29.10.2026)
Die alten Positionsbereiche sind nicht fortschreibbar: erste300 bei48d9545 und301-450 bei0bd66ea enthalten
146 Doppelungen und nur304 verschiedene Adressen. daten/pruefung_20261028/historische_pruefadressen.csv belegt die
Vereinigung; prueflos_003.csv haelt die naechsten150 bisher ungeprueften Adressen samt Exporthash fest.
Nach jedem Los: Befunde in der bestehenden Hauptaussage korrigieren, offene Rekonstruktionen kennzeichnen,
Registerstand und Gegenproben sichern, danach das naechste Los aus ungeprueften Adressen bilden.
Zusammenhaengende Ketten gemeinsam verfolgen: Einheitenlauf -> Artaktualisierung -> Ziel/Bewegung/Schaden;
Lagerbuchung -> Gesamtbestand -> Einkauf/Rekrutierung; Eingang -> Gebietsabfrage -> Wegplan.

## Fachliche Schwerpunkte (Vorschlag SAI, Daniel kann umstellen)
1. Die bereits gelesenen Felder brauchen eindeutige Strukturbelege; die fruehere Zahl101 ist historisch. Die aktuelle Messung trennt explizite Bindung und Erwaehnung (z. B. microXPosition, dying, substate,
   attackAtTileX). Felder ohne sichere Bedeutung bleiben offen; Umbenennungen erst nach Beleg und gesondertem Umsetzungsauftrag. Keine Spiel-/SamurAI-Logikaenderung durch diese Pruefung.
2. **Kampf und Einheiten**: Seuche (Wolke Entity 22 - Schaden, Ausbreitung, Dauer, Heilung), Viehwurf (Kuh Entity 23 -
   Einschlag), Belagerungsgeräte-Phasen inkl. Rammbock, Belagerungsturm, Schutzschild, Fallgruben, Zustandsübergänge je
   Einheitenart (PTR_UpdateUnitFunctions 0x00B4DF60), Nahkampf-Höhenvorteil.
3. Gebäude und Wirtschaft (inkl. Gebäude-Eingänge).
4. KI-Vorgaben, Spieler, Karte/Zeit, Weltkarte.

## Arbeitsweise (Daniels Regeln)
- Erst messen, dann behaupten; jede Zahl mit dem Befehl, der sie erzeugt. Ableitungen als "vermutet" markieren.
- Jeder Fund in derselben Runde ins `Wissensregister.md` (neue Zeilen AU37 ff., Datum, Marke).
- Neue Lesefelder in `werkzeug/auge.py` immer mit Prüfung (Gegenprobe: Feld falsch -> Prüfung rot).
- Backlog-Punkt B-267 nennen in jedem Commit.
- Kurze Berichte an Daniel auf Deutsch: was erklärt wurde, neue Abdeckungszahl, was als Nächstes.
