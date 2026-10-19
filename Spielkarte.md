# Spielkarte Stronghold Crusader - Grundverständnis für das Framework

Angelegt 19.10.2026 (Backlog B-95/B-114). Anlass: Krari über Daniel, 19.10. 21:52: erst den Code des Spiels wirklich
verstehen, dann von Grund auf nach Sharky bauen. Jeder Abschnitt nennt Adressen, Marke und Beleg.

**Referenz:** Ghidra-Projekt `OpenSHC-ref` (OpenSHC-SARIF, 4.765 benannte Funktionen) auf `StrongholdCrusader.exe`
(sha1 `012e9d55…`). Gemessen 19.10.: Instanz 1 ist byte-gleich, Instanz 2-5 weichen in genau einem Byte ab (Instanzname,
`instanz_anlegen.py`). Alle Adressen gelten also für jede Instanz. Skripte: `werkzeug/ghidra/*.java`, headless:

```
JAVA_HOME="C:\Program Files\Eclipse Adoptium\jdk-21.0.12.8-hotspot" DUMP_AUS=<datei> DUMP_NAMEN=<name1,name2> \
  ~/ghidra/ghidra_12.1.2_PUBLIC/support/analyzeHeadless.bat C:\Users\danie\ghidra-projects OpenSHC-ref \
  -process StrongholdCrusader.exe -noanalysis -readOnly -scriptPath <werkzeug/ghidra> -postScript DumpFunktionen.java
```

## 1. Wie das Spiel einen Befehl für einen Spieler ausführt (B-114, 19.10.2026)

Marke: **abgelesen** (Dekompilat). Passt zur Messung vom 18.10. (logik.lua: Befehle laufen für den Platz, der bei der
Ausführung in `currentPlayerSlotID` steht).

| Schritt | Funktion / Feld | Was passiert |
|---|---|---|
| 1. Absetzen | `queueCommand` `0x00489100` (thiscall auf `GameSynchronyState` `0x0191D768`) | Werte stehen vorher in `GameCommandParam0..5` (`0x01997FB8…`). Neuer Eintrag in `GameCommandArray` (200 Plätze): `commandType`, `time = jetzt + commandDelay`, **`playerUnk = DPLAYX_PlayerHandle`** (die eigene Netzkennung). Der Ausführer packt die Werte im Modus `GCS_SCHEDULE_AND_SEND` in den Eintrag. Sofort-Befehle (`time < 1`) laufen gleich, dann mit Auslöser = `currentPlayerSlotID`. |
| 1b. Befehl eines anderen Spielers | `scheduleReceivedCommand` `0x00480210` (Typ, **Absender-Kennung**, Zeit, Werte) | Derselbe Eintrag, aber mit der mitgegebenen Absender-Kennung. So kommen im Mehrspieler die Befehle der anderen herein. |
| 2. Ausführen | `processWaitingCommands` `0x004892F0`, jeder Takt | Für jeden fälligen Eintrag: **`protocolInvokerPlayerID`** (`GSS+0x109E70` = `0x01A275D8`) = `translateMultiplayerIDsIntoPlayerIDs(eintrag.playerUnk)`, dann der Ausführer im Modus `GCS_EXECUTE`. |
| 3. Übersetzen | `translateMultiplayerIDsIntoPlayerIDs` `0x0047EAF0` | **Mehrspieler:** Absender → Platz über `currentPlayerFullIDArray[1..8]` (`0x0191DE10 + 4·Platz`). **Einzelspieler** (`GM_SOLITARY`, `GM_SKIRMISH_SINGLE_PLAYER`): gibt immer `currentPlayerSlotID` (`GSS+0x109E74` = `0x01A275DC`) zurück - **der Absender wird nicht beachtet.** |
| 4. Wirkung | die Ausführer (Tabelle `0x00B38E10 + 4·Nr`) | lesen den Auslöser, nicht „ich“: `ClickRecruitUnit` → `ProcessRecruitUnit(protocolInvokerPlayerID, Typ, Gebäude)`; ebenso Bauen, Abreißen, Kaufen/Verkaufen, Steuern, Rationen, Mauern, Gelände, Tore, Belagerungszelt (43 Funktionen unter `Commands::` lesen `protocolInvokerPlayerID`, gezählt in `daten/dekomp_befehl_ausfuehren.c`). |

**Folge:** Im Gefecht gegen den Computer gilt jeder Befehl für den, der bei der Ausführung „ich“ ist. Deshalb setzt
der Mod (`logik.lua`, `alsSpieler`) „ich“ einen Takt lang auf SamurAIs Platz. In diesem Takt gehen auch Daniels Klicks
an SamurAI; wird „ich“ vor der Ausführung zurückgesetzt, ginge SamurAIs Befehl an Daniel. Das widerspricht B-94.

**Weg zur Trennung (Vorschlag für B-94, nicht gebaut):** Das Spiel kennt den richtigen Weg schon - im Mehrspieler trägt
jeder Befehl seinen Absender. Im Einzelspieler-Zweig der Übersetzung muss nur ein Befehl mit SamurAIs Absender-Kennung
für SamurAIs Platz gelten; jeder andere Befehl (Daniels Klicks) bleibt bei „ich“. SamurAI setzt seine Befehle dann
mit eigener Absender-Kennung ab (`scheduleReceivedCommand` oder `playerUnk` des Eintrags nach `queueCommand`), und
„ich“ wird nie mehr angefasst.

Belege: `daten/dekomp_queuecommand.c`, `daten/dekomp_befehl_ausfuehren.c` (alle Zugriffe auf Auslöser und „ich“ +
die drei Setzer), `daten/dekomp_absender.c` (Übersetzung, Ausführer Anwerben, Platzvergabe). Skripte:
`werkzeug/ghidra/DumpBefehlAusfuehren.java`, `werkzeug/ghidra/DumpFunktionen.java`.

## Offen (nächste Abschnitte, B-95)

- Spielerdaten (`PlayerData` `0x0115BDF8 + 0x39F4·Platz`): welche Felder das Framework braucht.
- Einheiten und Gebäude: Arrays, Felder für Besitzer, Typ, Ort, Leben, Ziel - Grundlage für das Lagebild je Takt.
- Karte: Gelände, Begehbarkeit, Bauplatzprüfung.
- Takt: wo `processWaitingCommands` im Spieltakt sitzt und wo ein Modul sicher einhängen kann.
