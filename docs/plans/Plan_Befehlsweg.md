# Plan: Befehlsweg (P4, B-156)

**Stand:** 08.11.2026. Die Abschnitte 1 bis 6 sind der Plan aus P4. Was davon gebaut ist und was noch fehlt, steht in Abschnitt 7.

**Grundlage:**
- Wissensregister S8, S19, S39, S52, S57,
- Funktionswissen (`queueCommand`, `processWaitingCommands`, `MakeUnitSelection`, `playerMakeUnitSelection`, `ClickMoveUnit`, `ClickGiveUnitsInstruction`, `determineGameTicksToPerform`),
- `bridge/snapshots/logik_stand_20261019.lua`,
- der Rust-Kern auf Zweig `kern-s0` (`haende.rs`, `leitung.rs`, `lib.rs`),
- das Entscheidungsblatt (P4, P5) und `docs/FAIRNESS.md`.

**Ziel (Entscheidungsblatt P4):** Je Takt kommt nur ein Befehl richtig an. Deshalb braucht es eine Reihenfolge: Reflex vor Flucht vor Angriff vor Laufen. Heute senden zwei Stellen, ohne sich abzustimmen.

## 1. Was belegt ist

| # | Befund | Beleg |
|---|---|---|
| B1 | Ein Gruppenbefehl besteht aus zwei Spielbefehlen. Zuerst kommt die **Auswahl** (16, `MakeUnitSelection`): Die Auswahl-Bits des Spielers (400 Byte, ein Bit je Einheit) werden verschickt, beim Ausführen bildet `playerMakeUnitSelection` daraus eine neue Gruppe. Dann kommt die **Anweisung** an diese Gruppe: 17 `ClickMoveUnit` für Laufen, 36 `ClickGiveUnitsInstruction` für Angriff oder Halt. | Funktionswissen; Kommentar in `logik.lua` „Wie der Mensch“ |
| B2 | Jeder Spielbefehl läuft über `queueCommand` in einen Ring mit 200 Plätzen. Er wirkt erst zur Ausführungszeit (`commandDelay` + Spielzeit) in `processWaitingCommands`, im Einzelspiel offenbar im nächsten Takt. | Funktionswissen; `PLATZ_TAKTE = 1` reichte in `logik.lua` |
| B3 | Mehrere Gruppenbefehle im selben Takt, auch mit verschiedenen Gruppennummern, landen **alle in einer Gruppe und laufen zum letzten Ziel**. Von 120 Einzelbefehlen in einem Takt kommt einer richtig an. Ein Befehl je Takt kommt immer an: 36 von 36 und 20 von 20. | S57, gemessen über das Modul (nicht über den Kern) |
| B4 | Die Ursache ist vermutlich diese: Alle Auswahlen eines Takts schreiben in dieselben Auswahl-Bits des Spielers, gelesen wird erst beim Ausführen. Das ist aus Code und Messung geschlossen, nicht einzeln belegt. | B1, B2, B3 |
| B5 | Befehle verschiedener Spieler im selben Takt laufen als der zuletzt gesetzte Spieler. Nur die Angriffe haben eine Warteschlange. | S19, aus dem Modulcode, **ungeprüft** |
| B6 | Ein Truppenbefehl ist schneller als ein Direktbefehl: meist 12 statt 16 Takte je Feld. | S8, S39 |
| B7 | Ein Takt dauert auf Stufe 40 25 ms. Mehr als rund 825 Takte je Sekunde schafft das Spiel nicht. | `determineGameTicksToPerform`, S52 |
| B8 | Ein Pfeil fliegt 5,75 Mikro je Takt, für 40 Felder also rund 56 Takte. Bolzen sind etwas schneller, Feuer langsamer. | S10 |

## 2. Wer heute sendet

| Stelle | Wo | Wie |
|---|---|---|
| **A: Modul `logik.lua`** | `main` (Lua im Spielordner, Stand-Kopie in `bridge/snapshots/`) | Der Python-Lenker schreibt `befehl.json`. Einheitenbefehle (Angriff, Halt, Laufen) kommen in die `angriffSchlange`: je Takt einer, danach wartet das Modul, bis die Einheiten in ihrer Gruppe stehen (höchstens 20 Takte). Flucht (`vorrang`) kommt nach vorn. Gruppennummern sucht es von 1249 abwärts. Bauen, Anwerben und Markt gehen sofort. |
| **B: Rust-Kern** | nur Zweig `kern-s0` (42 Commits, Stand 21.10.), **nicht in `main`** | Die Hände führen ein Auftragsbuch und setzen je neuem Takt einen Gruppenbefehl ab. Sie warten genauso höchstens 20 Takte. Gruppennummern zählen ab 1 aufwärts. Python kann über den Auftragsring im gemeinsamen Speicher Aufträge geben (S4b). |
| Reflexe (Ausweichen) | laut Discord-Update 04.11. im Kern | **Code in keinem Git-Zweig gefunden** |

**Das Problem:**
- A und B kennen sich nicht. Ihre Gruppennummern kollidieren zwar nicht, aber setzen beide im selben Takt eine Auswahl, verschmelzen die Gruppen (B3). Dann laufen die Einheiten beider Stellen zum letzten Ziel.
- Eine Einheit kann außerdem bei beiden Stellen gleichzeitig Aufträge haben. Wem sie gehört, regelt niemand.
- Innerhalb von A ist die Flucht nur „nach vorn“ sortiert. Andere Dringlichkeiten kennt die Schlange nicht.

## 3. Entwurf

**E1. Eine Stelle sendet Einheitenbefehle.**
- Vorschlag: der Kern. Er läuft in jedem Takt im Spiel, Python nur je Lenker-Runde.
- `logik.lua` gibt Einheitenbefehle nur noch über den Auftragsring an den Kern weiter. Selbst sendet es nur Befehle ohne Auswahl (Bauen, Anwerben, Markt, Steuer, Rationen).
- Steht der Kern nicht zur Verfügung, ist `logik.lua` die eine Stelle (der heutige Weg ohne Kern). Wichtig ist nur: **nie zwei**.

**E2. Jede Einheit gehört genau einem Auftraggeber.**
- Auftraggeber sind: Assassinen-Steuerung, Raids, Wächter, Feldzug, Heimwache, Reflex.
- Der Kern führt die Besitzliste. Ein Auftrag für eine fremde Einheit wird abgewiesen, und der Absender erfährt das (Annahme „nicht deine“).
- Der Reflex darf jede Einheit kurz **leihen**: einen Befehl lang, danach geht sie mit ihrem alten Auftrag zurück. Das ist die Idee aus B-98 („Einheiten-Anspruch nach Vorrang“).

**E3. Reihenfolge je Takt nach Vorrangklassen.**

| Klasse | Inhalt | Frist |
|---|---|---|
| 1 Reflex | Ausweichen vor einem sichtbaren Geschoss, Feuer, Graben am Laufziel | Takte bis zum Treffer (aus Flugbahn, S59/S60) |
| 2 Flucht | Rückzug bei Übermacht, Entdeckung | wenige Takte |
| 3 Angriff | Ziel angreifen, Gegenschlag | Takte bis das Ziel wegläuft oder fällt |
| 4 Laufen | Stellung beziehen, Wegpunkte | keine harte |
| 5 Routine | Sammeln, Heimkehr, Wache | keine |

- Innerhalb einer Klasse geht die früheste Frist zuerst, dann der älteste Auftrag.
- Ein Auftrag, dessen Frist abgelaufen ist, verfällt. Ein Ausweichen nach dem Treffer nützt nichts.

**E4. Ein Gruppenbefehl je Takt, aber gebündelt.**
- Aufträge mit gleicher Art und gleichem Ziel (oder gleicher Ausweichrichtung) wandern in **einen** Gruppenbefehl. So reicht ein Takt für viele Einheiten.
- Gebündelt wird nur innerhalb einer Klasse.

**E5. Erst die neue Gruppe abwarten, dann der nächste Befehl.**
- So arbeiten A und B heute schon: höchstens 20 Takte, meist ein Takt.
- Ausnahme: Ein Reflex mit Frist darf nicht warten. Verschmilzt er mit einer gerade entstehenden Gruppe, sind beide verloren. Deshalb gilt: Reflex nur, wenn keine Gruppe im Entstehen ist, sonst verfällt er oder geht in den nächsten Takt. Wie oft das passiert, zeigt erst die Messung M3.

**E6. Vorhandene Gruppen wiederverwenden.**
- Steht eine Einheit schon in einer passenden Gruppe, braucht ein neuer Befehl an diese Gruppe (17 oder 36) **keine neue Auswahl**.
- Dann gäbe es vermutlich mehrere Befehle je Takt, einen je Gruppe. Das ist **nicht gemessen** und der größte Hebel (M1).
- Bis zur Messung gilt: ein Befehl je Takt.

**E7. Rückmeldung in drei Stufen.**
- **angenommen** (eingereiht) → **abgesetzt** (im Spiel-Ring) → **wirkt** (Laufziel oder Zustand im Lagebild geändert).
- Erst „wirkt“ zählt als erledigt. Das entspricht LIVE-01 und B-104 („angenommen ist nicht abgesetzt“).

**E8. Fairness.**
- Keine Befehle in der Pause (F6). Der Kern prüft das vor jedem Absetzen, die Angriffs-Schlange in `logik.lua` tut es heute schon.
- Nur eigene Einheiten (R3).
- So schnell steuern wie möglich ist erlaubt (R1).

**E9. Mehrere Spieler (1v1 mit einem Lenker je Spieler).**
- Je Takt darf nur ein Spieler senden (B5). Der Kern vergibt die Takte reihum an die Spieler, die etwas in der Schlange haben.
- Ein Reflex eines Spielers geht vor der Routine des anderen.
- Heute löst `logik.lua` das mit `platzFest`.

## 4. Durchsatz (Rechnung, nicht gemessen)

- **Bester Fall:** Jede neue Gruppe steht im nächsten Takt. Gemessen ist das über die Schlange: 12 Gruppen in 12 Takten. Auf Stufe 40 sind das bis zu 40 Gruppenbefehle je Sekunde.
- **Schlechtester Fall:** Wartet jede Gruppe 20 Takte, sind es nur 2 je Sekunde.
- **Folge für Reflexe:** Ein Pfeil auf 40 Felder braucht rund 56 Takte (B8). Hinter einer langen Schlange käme ein Reflex zu spät. Deshalb braucht es Vorrang und Fristen (E3), und das Bündeln (E4) entlastet die Schlange.

## 5. Was P5 baut (Vorschlag, nach Daniels Ja)

1. **Kern nach `main` holen:** Zweig `kern-s0` zusammenführen und dabei die Nummern B-145 bis B-151 des Zweigs mit dem Backlog in `main` abgleichen.
2. **Reflex-Code ins Repo:** den Code vom anderen PC einchecken, falls er dort liegt.
3. **Befehlsweg im Kern:**
   - Vorrangschlange mit Klassen und Fristen (E3),
   - Besitzliste mit Leihe (E2),
   - Bündeln (E4) und Warten auf die Gruppe (E5),
   - Rückmeldung in drei Stufen (E7) über den Auftragsring.
4. **`logik.lua`:** Einheitenbefehle nur noch an den Kern (E1).
5. **Assassinen zuerst:** Die Assassinen-Steuerung gibt ihre Einheiten an den Kern ab, so steht es im Entscheidungsblatt.
6. **Tests ohne Spiel:**
   - Reihenfolge und Fristen,
   - Bündeln,
   - fremde Einheit abgewiesen,
   - Leihe und Rückgabe,
   - Gegenprobe „zwei Stellen im selben Takt“: Verschmelzen wird erkannt und verhindert.

## 6. Für den nächsten Messlauf (Checkliste)

| # | Frage | Warum |
|---|---|---|
| M1 | Wie viele Befehle (17/36) an **vorhandene** Gruppen kommen im selben Takt richtig an, ohne neue Auswahl? | entscheidet E6, möglicher Vielfach-Durchsatz |
| M2 | Stört ein Bau-, Anwerbe- oder Marktbefehl einen Gruppenbefehl im selben Takt? | entscheidet, ob E1 Nicht-Einheitenbefehle frei lassen darf |
| M3 | Wie viele Takte vergehen, bis eine neue Gruppe steht (Verteilung)? | Durchsatz, Reflex-Fenster (E5) |
| M4 | Verhält sich der Weg des Kerns (`haende.rs`) wie der des Moduls? | S57 ist nur über das Modul gemessen |
| M5 | Stimmt S19 (Befehle zweier Spieler im selben Takt) im Spiel? | E9 |

## 7. Stand von P5 (B-157)

**Gebaut** (Kern-Fassung 20, Aufbau 4 des gemeinsamen Speichers):

| Teil | Wo |
|---|---|
| Vorrang mit Fristen (E3), Besitzliste mit Leihe (E2), Bündeln (E4), Warten auf die Gruppe (E5), Rückmeldung (E7) | `crates/samurai-kern/src/haende.rs` |
| Auftragsring mit Vorrang, Frist und Auftraggeber; Fortgang im Ergebnisfeld; Abfrage `samurai_sendetakt` | `crates/samurai-kern/src/leitung.rs`, `lib.rs`, `src/selfaware/game/kern_leitung.py` |
| Assassinen-Befehle in Ring-Aufträge übersetzen, Schalter `kernweg=ja` (Standard: aus) | `src/selfaware/execution/kernweg.py`, `src/selfaware/runtime/live/erstes_spiel.py` |

Keine Befehle in der Pause (F6): Der Kern arbeitet Ring und Hände nur in einem neuen Spieltakt ab, in der Pause also nicht.

**Noch nicht gebaut:**
- **E1 nur für die Assassinen:** „halten“ kann der Kern nicht und bleibt beim Modul. Der Kern gibt die betroffene Einheit vorher frei. Alle anderen Auftraggeber senden weiter über das Modul.
- **E6** (vorhandene Gruppen wiederverwenden) wartet auf M1.
- **E9** (Takte reihum an mehrere Spieler) ist nicht gebaut.
- **Reflex-Code:** liegt in keinem Zweig. In den Kern eingebaut ist nur die Vorrangklasse dafür.
- **Nur eigene Einheiten (E8):** Der Kern prüft das nicht, er sendet als Besitzer der Einheit. Heute kommen alle Nummern aus der Mitgliederliste der Assassinen. Vor P8 (weitere Auftraggeber) muss diese Prüfung dazu. Der Verweis auf R3 in E8 war falsch: R3 regelt verborgenes Gegnerwissen, eine Regel zu fremden Einheiten steht noch nicht in `docs/FAIRNESS.md`.
- **`FLUCHT_FRIST` = 60 Takte** ist ein vorläufiger Wert. Ihn soll M3 prüfen.

**Änderung an `logik.lua` (seit 08.11.2026 im Spielordner, Stand-Kopie `bridge/snapshots/logik_stand_20261108.lua`).** Sie verhindert, dass Kern und Modul im selben Takt einen Gruppenbefehl absetzen (B3). `kern.takt` läuft in `everyTick` zuerst, der Wert ist also aktuell. Grundlage ist `bridge/snapshots/logik_stand_20261021.lua`:

```lua
-- in kernLaden, nach dem Block mit k.auftrag:
local as = adresse("samurai_sendetakt")   -- ab Kern 20 (P5, B-157)
if as then k.sendetakt = core.exposeCode(as, 0, 0) end

-- in angriffSchlangeTick, direkt nach "local t = tick()":
if kern ~= nil and kern.sendetakt ~= nil and kern.sendetakt() == t then return end   -- S57
```

**Erste Läufe im Spiel (08.11.2026, Laptop, `kernweg=ja`).** Karte und Gegner („The Killing Plains“, 2 Nomaden) spielen für diese Messung keine Rolle.

- Lauf a, Tempo 40: bei Takt 6.700 von Hand beendet.
- Lauf b, Tempo 200: bis Takt 40.000. Der Kern hat alle 40.000 Takte gesehen und 1.462 Gruppenbefehle abgesetzt, ohne Fehler oder Verweigerung. 7 Aufträge fielen weg, weil die Einheit schon tot war.

| Art (letzte Meldung von Lauf b) | wirkt | wirkt nicht |
|---|---|---|
| Laufen | 1.173 | 0 |
| Angriff auf Einheit | 68 | 0 |
| Angriff auf Gebäude | 0 | 116 |

- „Wirkt nicht“ bei Gebäuden ist vermutlich ein Fehler der Prüfung: Die Einheit stand einen Takt später in der richtigen Gruppe, das Feld für das Zielgebäude war in der Stichprobe bei allen Assassinen 0. Nachgeprüft ist das nicht. Wichtig wird es erst, wenn ein Gehirn darauf baut.
- Tempo 825 ist noch nicht gefahren.
- Belege: `data/research/kernweg_1108b_1_i1_konsole.txt`, `data/research/kernweg_1108b_samurai_kern.log`.
