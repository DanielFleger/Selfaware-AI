# Ansage Lauf F

Erstellt 02.11.2026 von SRE (B-142). Der Lauf ist noch nicht gestartet, er braucht Daniels Ja.

## Was wird getestet

Das Auge, nicht das Spiel und nicht SamurAI: Liest die Aufzeichnung lückenlos mit, und stimmen unser Wissen und die Feldliste für alles Friedliche?

## Was ich erhoffe, und was es widerlegt

| Probe | Erhofft | Widerlegt, wenn |
|---|---|---|
| A1 | Jede Änderung liegt in einem Feld der Liste | Ein Byte eines Spielbereichs ändert sich außerhalb. Das erwarte ich sogar: Die Liste kennt Zeigerzugriffe nur teilweise, jede Lücke ist ein Gewinn |
| A3 | Kein Takt fehlt, kein Schnappschuss ist gemischt | Ein Takt fehlt oder ein Rahmen ist gemischt |
| A4 | Auf den Stufen 1 bis 1000 zieht das Lesen kein Tempo ab (Daniels Vorgabe, keine Prozentgrenze) | Mit Lesen weniger Takte als ohne Lesen, über das Messrauschen hinaus. Auf hohen Stufen darf das Lesen Takte auslassen, das Tempo geht vor |
| A7 | Jede gezogene Zufallszahl steht in der Tabelle | Eine Zahl passt nicht |
| A10 | Keine `uid` doppelt, Monat 0 bis 11, Geschossplätze unter 25 mit `uid` 0 | Ein Wert liegt außerhalb. Die Monatsgrenze ist heute am Code berichtigt worden, hier zeigt sich zum ersten Mal, ob das stimmt |
| A13 | Spielart im Burgenbau: `gameMode_2` = 2 | Ein anderer Wert. Dann muss die Spielart-Marke neu bewertet werden |
| Einzelpunkte | Aus der Aufzeichnung lassen sich die 84 Tabellenpunkte und möglichst viele der 157 Punkte aus Lauf F später auswerten | Punkte bleiben „nicht gesehen“, das ist die Restliste |

## Wie getestet wird

- **Wo:** Instanz 2, frei laut Sperre, Karte `A Mighty Oasis.map`. Instanz 5 bleibt unberührt, das Werkzeug lehnt sie ab.
- **Änderung an Instanz 2:** Ihre `logik.lua` vom 05.10. kennt die nötigen Knöpfe nicht. Sie bekommt die Fassung von Instanz 4 plus einen neuen Knopf für den Kartenstart. Instanz 5 nutzt ein anderes Modul mit Übernahme-Logik und taugt nicht als Vorlage. Außerdem kommt das Modul `villagestudio` zurück in die Ladeliste von `ucp-config.yml`, die Startreparatur vom 24.10. hatte es entfernt. Beide alten Dateien bleiben mit Datum daneben liegen, das ist der Rückweg.
- **Ablauf:** Spiel starten ohne Maus, Burgenbau, Karte wählen, Aufzeichnung an. Dann Waren setzen, Bergfried, jedes Gebäude einmal, 6.000 Takte Warenketten, Handeln auch bei vollem Lager, alle Steuer- und Rationsstufen, Mauer und Graben, jede Einheit anwerben, 5 Gebäude abreißen, zwei Jahreswechsel.
- **Tempo und Zeit:** Spieltempo 1000, dort erreicht das Spiel etwa 825 Takte je Sekunde. Das Programm hat höchstens 15 Minuten, die Bauphase davon höchstens 5, die Treppe danach höchstens 4. Kommen 30 s lang keine neuen Takte, ist das Spiel weg oder die Aufzeichnung tot, endet der Lauf sofort und wertet aus, was da ist.
- **Messgrößen:** alle Hauptstrukturen jeden Takt (9,0 MB), Kartenebenen alle 25 Takte, der ganze Datenblock (31,9 MB) alle 250 Takte.
- **Tempotreppe:** vor dem Programm im leeren und danach im bebauten Spiel je 7 Stufen, je Stufe ohne Lesen, mit Lesen, ohne Lesen; je Messung 20 s auf Stufe 1, 10 s auf Stufe 10, sonst 5 s. Sie zeigt auch, bis zu welchem Tempo jeder Takt lesbar ist.
- **Abbruch:** Frist um, 30 s Stillstand, Spiel oder Aufzeichnung weg. Ausgelassene Takte beenden den Lauf auf Tempo 1000 nicht. Dieselbe Wache läuft vor jedem Abschnitt. Scheitert nur ein Abschnitt, wird er notiert und der Lauf geht weiter.

**Das Programm hält das Spiel nicht an.** Daniels Vorgabe vom 02.11.2026: Auch beim Bauen läuft das Spiel im vollen Tempo. Das Protokoll nennt je Abschnitt die erreichten Takte je Sekunde.

**Was vermutlich beim ersten Mal hakt:** Das Bauprogramm kennt die Karte nicht, es probiert Stellen in Ringen um den Bergfried. Bauernhöfe, Mine, Steinbruch und Pechgrube brauchen besonderen Boden und bleiben deshalb vielleicht ungesetzt. Der Lauf schreibt auf, was fehlt, das wird danach gezielt nachgeholt. Die Knopf-Nummer für den Kartenstart stammt aus dem Code und ist im Spiel noch nie gedrückt worden.

## Nutzen fürs aktuelle Ziel

Es entscheidet, ob die Aufzeichnung so bleiben kann, wie viel Lesen das Spiel verträgt und welche Felder der Liste noch fehlen. Danach kommen Lauf K und Lauf S.

## Nutzen fürs große Ziel in 3 Jahren

SamurAI soll in jedem Takt alles wissen, was es wissen darf, und selbst lernen. Das geht nur auf einem Auge, dessen Vollständigkeit gemessen ist. Die Aufzeichnungen sind zugleich der Maßstab für einen späteren Rechner, der den Verlauf vorausberechnet.

## Befehl

```bash
PYTHONPATH=src python -m selfaware.tools.experiments.auge_lauf_f los --instanz 2 --daniel-ja
```

Trockenprobe, die nichts startet und nichts ändert:

```bash
PYTHONPATH=src python -m selfaware.tools.experiments.auge_lauf_f pruefen --instanz 2
```
