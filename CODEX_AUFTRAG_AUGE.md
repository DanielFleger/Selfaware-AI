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

## Ziel
Jede Funktion der Spiellogik und jedes Feld erklärt: Funktion in einem Satz, Adresse, Beleg, Marke
(belegt / gemessen / abgelesen / vermutet). Am Ende 100 % in `auge_abdeckung.json`, nach jedem Paket neu erzeugt.

## Reihenfolge (Vorschlag SAI, Daniel kann umstellen)
1. Die **101 Felder, die das Auge schon liest**, aber unerklärt sind (z. B. microXPosition, dying, substate,
   attackAtTileX) - und in `auge.py` die 40 Felder ohne Funktion im Namen umbenennen (field215_0x350, isRallyingUnk, ...).
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
