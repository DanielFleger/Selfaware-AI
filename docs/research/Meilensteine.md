# Meilensteine - Selfaware-AI

Der Katalog aller Meilensteine auf dem Weg zur selbstlernenden KI. Ein Meilenstein gilt erst als **erreicht**, wenn (1) er im Speicher oder Log belegt ist UND (2) Daniel ihn am laufenden Spiel gesehen und abgenommen hat. Ausnahme: was sich nicht sichtbar pruefen laesst, wird im Hintergrund abgenommen. Alle Dauern in **Ticks**.

Zwei Spalten, zwei Abnahmen: **Definition** = Daniel hat festgelegt, *was* geprueft wird. **Erreicht** = Daniel hat es am Spiel gesehen. Jede Abnahme wird hier mit Datum eingetragen; die Messung dazu steht in `doku/Wissensstand.md` des Village-Studio-Repos.

Diese Datei ist die eine Quelle des Katalogs und wird direkt gepflegt. Werkzeuge zu den Meilensteinen liegen in `werkzeug/`.

Lieferung 1 (30.09.2026): Bloecke M1 Grundlagen, M2 Spiel starten, M3 Gefecht steuern, M4 Spielende und Lord-Tod, M5 Ticks. Folgen: Mods und eigene KI, Einheiten, Wirtschaft, Burg, Ausloeser, die Ansicht der KI, Zuschauen, Lernschleife.

## Uebersicht

| ID | Meilenstein | Stand | Definition | Erreicht |
|---|---|---|---|---|
| M1.01 | Ziel und Endbild in einem Satz | Grundlage | abgenommen 30.09.2026 | - |
| M1.02 | Was 'abgenommen' heisst | Grundlage | abgenommen 30.09.2026 | - |
| M1.03 | Die Grundregeln der Plattform | Grundlage | abgenommen 30.09.2026 | - |
| M1.04 | Ein Tick ist die Einheit fuer alles | Grundlage | abgenommen 30.09.2026 | - |
| M2.01 | Spiel starten, ohne dass du etwas anfasst | gemessen | abgenommen 30.09.2026 | - |
| M2.02 | Pruefen, dass unser Modul wirklich laeuft | gemessen | abgenommen 30.09.2026 | - |
| M2.03 | Befehl hinein, Antwort heraus | gemessen | abgenommen 30.09.2026 | - |
| M2.04 | Spiel per Befehl beenden | belegt | abgenommen 30.09.2026 | - |
| M2.05 | Absturz und Haengen erkennen | offen | abgenommen 30.09.2026 | - |
| M2.06 | Mehrere Spiele gleichzeitig | offen | abgenommen 30.09.2026 | - |
| M2.07 | UCP3-GUI schliessen, ohne die Config zu beruehren | gemessen | Daniels Wunsch 30.09.2026 | Hintergrund belegt 30.09., 20:59 - live offen |
| M2.08 | Wann die GUI die Config schreibt | gemessen | Daniels Wunsch 30.09.2026 | - |
| M2.09 | UCP3-GUI oeffnen, ohne die Config zu beruehren | Werkzeug gebaut, ungetestet | Daniels Wunsch 30.09.2026 | - |
| M2.10 | Ein Spiel ohne unser Modul beenden | UEBERHOLT durch M2.11/M2.12 | Daniels Wunsch 30.09.2026 | - |
| M2.11 | Stronghold schliessen - in drei Stufen | gemessen | Daniels Wunsch 30.09.2026 | Hintergrund belegt 30.09., 21:06 - live offen |
| M2.12 | Hohe Rechte ohne Klick anfordern | gemessen | Daniels Wunsch 30.09.2026 | Hintergrund belegt 30.09., 21:04 - live offen |
| M2.13 | Config herrichten: Modul + weiterlaufen ohne Fokus | gemessen | Daniels Wunsch 30.09.2026 | Hintergrund belegt 30.09., 21:10 |
| M2.14 | Befehle mit Nummern, die nie doppelt vorkommen | gemessen | M2.03 | Hintergrund belegt 30.09., 21:10 |
| M3.01 | Zurueck ins Hauptmenue per Befehl | gemessen | abgenommen 30.09.2026 | - |
| M3.02 | Eigenes Spiel ohne Maus starten | gemessen (Lauf 1) | abgenommen 30.09.2026 | Hintergrund belegt 21:10; von Daniel live gesehen 21:14 - Aufbau noch falsch |
| M3.03 | Kampagne und eigenes Spiel sicher unterscheiden | halb gemessen (Lauf 1) | abgenommen 30.09.2026 | - |
| M3.04 | Karte waehlen: Liga_Grumpy Neighbors | gemessen (Lauf 1) | abgenommen 30.09.2026 | Hintergrund belegt 21:10; von Daniel live gesehen 21:14 |
| M3.05 | Selfaware auf beide KI-Plaetze | im Speicher ja, im Spiel NEIN (Lauf 1) | abgenommen 30.09.2026 | - |
| M3.06 | Feste Startplaetze: oben und unten | offen, Spur gefunden (Lauf 1) | abgenommen 30.09.2026 | - |
| M3.07 | Kein Mensch im Selbstspiel | offen: unser Startbefehl setzt einen echten Menschen ein (Lauf 1) | abgenommen 30.09.2026 | - |
| M3.08 | Startgold und Startgueter wie in der Team-Liga | offen | abgenommen 30.09.2026 | - |
| M3.09 | Tempo setzen | gemessen | abgenommen 30.09.2026 | - |
| M3.10 | Neues Spiel ohne Neustart des Programms | teils gemessen | abgenommen 30.09.2026 | - |
| M3.11 | Spiel pausieren und fortsetzen per Befehl | gemessen (Lauf 1) | Daniel 30.09.: "du kannst das Spiel pausieren" | Hintergrund belegt 21:10 |
| M3.12 | Tempo erst NACH dem Start setzen | gemessen (Lauf 1) | Lauf 1 | Hintergrund belegt 21:10 |
| M4.01 | Die Lords im Gefecht finden | gemessen | abgenommen 30.09.2026 | - |
| M4.02 | Lord-Tod erkennen | gemessen | abgenommen 30.09.2026 | - |
| M4.03 | Was nach dem Lord-Tod wirklich passiert | **gemessen 01.10.** (Lauf 11) | abgenommen 30.09.2026 | - |
| M4.04 | Der einfachste echte Tod: zwei Lords laufen aufeinander zu | **gemessen 01.10.** (Lauf 10), Live-Abnahme offen | abgenommen 30.09.2026 | - |
| M4.05 | Den Sieger aus dem Speicher lesen | **gemessen 01.10.** (Lauf 10/11: `playerIsAlive` 0x0117EF40) | abgenommen 30.09.2026 | - |
| M4.06 | Den Endbildschirm erkennen | gemessen | abgenommen 30.09.2026 | - |
| M4.07 | Zeitlimit: die ersten X Ticks | offen | abgenommen 30.09.2026 | - |
| M5.01 | Was ein Tick ist und wo er steht | belegt | abgenommen 30.09.2026 | - |
| M5.02 | Die Grenze: hoechstens 11 Ticks je Bild | abgelesen | abgenommen 30.09.2026 | - |
| M5.03 | Greift unser Modul jeden Tick ein oder nur jedes Bild? | offen | abgenommen 30.09.2026 | - |
| M5.04 | Wie lange Ereignisse dauern (Katalog) | teils belegt | abgenommen 30.09.2026 | - |
| M5.05 | Veraendert das Tempo das Spiel? | offen | abgenommen 30.09.2026 | - |

## Die Meilensteine im Einzelnen

### M1.01 Ziel und Endbild in einem Satz

*Stand beim Anlegen: Grundlage*

ZIEL: Eine KI 'Selfaware', die sich im Selbstspiel verbessert. Endbild: du schaust zu und fliegst frei ueber die Karte, waehrend die KI jeden Tick ihre eigene Ansicht des Spielfelds hat.  
STAND: steht im Plan (Selfaware-AI/Plan-selbstlernende-KI.md), mit dir abgestimmt am 30.09.  
DU SIEHST: den Plan im Repo.  
WIDERLEGT, WENN: du das Endbild anders beschreibst.  

**Vorschlag:** Abnehmen, wenn der Satz so stimmt.  

### M1.02 Was 'abgenommen' heisst

*Stand beim Anlegen: Grundlage*

ZIEL: Ein Meilenstein gilt erst als erreicht, wenn (1) ich ihn im Speicher oder Log belegt habe UND (2) du ihn am laufenden Spiel gesehen und abgenommen hast.  
STAND: deine Regel vom 30.09.  
ABLAGE: Jede Abnahme bekommt eine Zeile mit Datum im Meilenstein-Katalog im Selfaware-Repo; die Messung dazu steht im Wissensstand.  
WIDERLEGT, WENN: ein Punkt als erreicht gilt, ohne dass beides vorliegt.  

**Vorschlag:** So festhalten.  
**Daniel, 30.09.:** Ausnahme: Dinge, die sich nicht sichtbar pruefen lassen, werden im Hintergrund abgenommen.  

### M1.03 Die Grundregeln der Plattform

*Stand beim Anlegen: Grundlage*

ZIEL: Die vier Dinge, gegen die man nicht bauen kann, sind jedem Schritt klar: (1) nur das Modul im Spiel darf ans Spiel, von aussen ist alles gesperrt; (2) ein Spiel faehrt immer nur eine Sitzung (Testsperre); (3) die ucp-config.yml hat einen Schreiber; (4) die UCP3-GUI bleibt beim Testen zu - sie wirft unser Modul aus der Config (heute gemessen).  
STAND: belegt, Betriebsregeln und Wissensstand 13.  
WIDERLEGT, WENN: ein Testlauf ohne Sperre oder mit offener GUI als gueltig gezaehlt wird.  

**Vorschlag:** So festhalten.  

### M1.04 Ein Tick ist die Einheit fuer alles

*Stand beim Anlegen: Grundlage*

ZIEL: Jede Dauer, jedes Zeitlimit und jede Messung wird in Ticks angegeben; Sekunden und Spielzeit werden nur daraus umgerechnet.  
STAND: deine Entscheidung vom 30.09.; die Umrechnung ist belegt (Tag = 50 Ticks, Jahr = 9.600; Ticks je Sekunde = Tempo).  
WIDERLEGT, WENN: irgendwo eine Dauer nur in Sekunden steht.  

**Vorschlag:** So festhalten.  

### M2.01 Spiel starten, ohne dass du etwas anfasst

*Stand beim Anlegen: gemessen*

ZIEL: Das Spiel startet per Befehl im Hintergrund, dein Fenster bleibt vorn.  
STAND: gemessen am 30.09. mit werkzeug/starte_spiel.py (Meldung: 'Dein Fenster ist wieder vorn, das Spiel liegt dahinter').  
ICH PRUEFE: genau ein Crusader-Prozess, Fenstertitel 'Crusader'.  
DU SIEHST: Stronghold laeuft, du hast nichts geklickt und dein Fenster ist vorn geblieben.  
WIDERLEGT, WENN: du klicken musst oder zwei Prozesse laufen.  

**Vorschlag:** Beim naechsten Start live abnehmen.  

### M2.02 Pruefen, dass unser Modul wirklich laeuft

*Stand beim Anlegen: gemessen*

ZIEL: Vor jedem Test steht fest, dass das Modul geladen ist - sonst ist jede Beobachtung wertlos.  
STAND: gemessen am 30.09. (Logzeile 'villagestudio aktiv' um 19:53, nachdem ich das Modul wieder eingetragen hatte).  
ICH PRUEFE: 3 Eintraege 'villagestudio' in der Config UND die Logzeile.  
DU SIEHST: die Logzeile, die ich dir zeige.  
WIDERLEGT, WENN: ein Befehl wirkt, obwohl die Zeile fehlt, oder umgekehrt.  

**Vorschlag:** Abnehmen.  

### M2.03 Befehl hinein, Antwort heraus

*Stand beim Anlegen: gemessen*

ZIEL: Jeder Befehl kommt an und hinterlaesst eine Antwort im Log.  
STAND: gemessen am 30.09. - mit einer Falle: Befehle mit einer schon benutzten Nummer (id) werden uebersprungen. Zwei Messlaeufe waren deshalb wirkungslos. Loesung: Nummern aus der Uhrzeit, stetig steigend.  
ICH PRUEFE: zu jeder Befehlsnummer genau eine Antwortzeile.  
DU SIEHST: ich schicke 'Tempo 100', das Spiel wird sichtbar langsamer.  
WIDERLEGT, WENN: ein Befehl ohne Antwortzeile wirkt oder eine Antwort ohne Wirkung kommt.  

**Vorschlag:** Nummern-Regel fest ins Werkzeug einbauen, dann abnehmen.  

### M2.04 Spiel per Befehl beenden

*Stand beim Anlegen: belegt*

ZIEL: Das Spiel laesst sich ohne dich beenden - von aussen ist das gesperrt.  
STAND: belegt laut Betriebsregeln ({ "beenden": true } ruft ExitProcess im Spiel).  
ICH PRUEFE: danach kein Crusader-Prozess mehr.  
DU SIEHST: das Fenster verschwindet.  
WIDERLEGT, WENN: der Prozess bleibt.  

**Vorschlag:** Live abnehmen.  

### M2.05 Absturz und Haengen erkennen

*Stand beim Anlegen: offen*

ZIEL: Die Schleife merkt selbst, wenn das Spiel abstuerzt oder haengt, und startet neu - sonst steht nachts alles still.  
STAND: offen. Drei Merkmale sind denkbar: Prozess weg, Uhr steht, Log waechst nicht mehr.  
ICH PRUEFE: je Merkmal einen absichtlich herbeigefuehrten Fall.  
DU SIEHST: nach einem erzwungenen Ende startet das Spiel von selbst wieder.  
WIDERLEGT, WENN: ein stehendes Spiel laenger als eine Minute unbemerkt bleibt.  

**Vorschlag:** Vor der Lernschleife bauen, nicht jetzt.  

### M2.06 Mehrere Spiele gleichzeitig

*Stand beim Anlegen: offen*

ZIEL: 2, dann 5, dann mehr Spielkopien laufen nebeneinander.  
STAND: offen. Die 'laeuft schon'-Sperre greift je Installation; ob Kopien sich Config, Log und Befehlsdatei teilen, ist ungeprueft.  
WIDERLEGT, WENN: eine zweite Kopie im 'laeuft schon'-Dialog haengt.  

**Vorschlag:** Erst nach dem ersten durchgespielten Spiel (deine Regel).  

### M2.07 UCP3-GUI schliessen, ohne die Config zu beruehren

*Stand: gemessen 30.09.2026. Daniel: "es gibt keinen zu kleinen Schritt".*

ANLEITUNG: `python werkzeug/gui.py schliessen` (im Selfaware-AI-Repo). Das Werkzeug bittet die GUI zu schliessen - dieselbe Nachricht wie ein Klick aufs X - und wartet bis zu 15 s. Erzwungen wird nie.  
ERKLAERUNG: Die GUI muss zu sein, bevor wir testen, weil sie beim Spielstart die Config ueberschreibt (M2.08). Sie laeuft auf derselben Rechtestufe wie Claude und darf deshalb von hier geschlossen werden (Pfad lesbar: `%LOCALAPPDATA%\UCP3-GUI\UCP3-GUI.exe`).  
TEST, EINGEBAUT: geschafft = kein GUI-Prozess mehr UND Pruefsumme der Config vorher = nachher. Nicht geschafft = Prozess lebt nach 15 s noch; das Werkzeug nennt den wahrscheinlichen Grund (offener Dialog, z. B. ungespeicherte Aenderungen) und verwirft nichts.  
GEMESSEN 30.09., 20:59: GUI (PID 30528) geschlossen, Config-Pruefsumme `58591298a2e027cc` vorher wie nachher, Rueckgabe 0.  
DU SIEHST: das GUI-Fenster verschwindet, ohne dass du klickst.  
WIDERLEGT, WENN: die GUI weiterlaeuft oder die Pruefsumme sich aendert.  

### M2.08 Wann die GUI die Config schreibt

*Stand: gemessen 30.09.2026.*

ERGEBNIS: Die GUI schreibt die Config **beim Spielstart aus der GUI** - Aenderungszeit der Config 20:21:34 = Startzeit des Spiels, auf die Sekunde. **Beim Schliessen schreibt sie nicht** (Pruefsumme gleich, M2.07). Beim Oeffnen: noch offen, prueft M2.09.  
FOLGE: Das Spiel nie aus der GUI starten, solange getestet wird. Wer es doch tut, verliert `villagestudio` in der Config und bekommt ein Spiel ohne unser Modul (M2.10).  
WIDERLEGT, WENN: die Config sich aendert, ohne dass aus der GUI gestartet wurde.  

### M2.09 UCP3-GUI oeffnen, ohne die Config zu beruehren

*Stand: Werkzeug gebaut, noch nicht ausgefuehrt.*

ANLEITUNG: `python werkzeug/gui.py oeffnen`. Startet die GUI, wartet auf ihren Prozess und vergleicht die Pruefsumme der Config 10 s spaeter.  
TEST, EINGEBAUT: geschafft = GUI-Prozess da UND Config unveraendert. Meldet ausdruecklich, falls schon das Oeffnen schreibt.  
WIDERLEGT, WENN: die Pruefsumme sich beim blossen Oeffnen aendert.  

### M2.10 Ein Spiel ohne unser Modul beenden

*Stand: UEBERHOLT am 30.09.2026, 21:06 - geloest durch M2.11 und M2.12. Daniel: "das soll kein Blocker sein". Der alte Text bleibt als Sicherung stehen.*

WARUM NICHT: Das aus der GUI gestartete Spiel (PID 15208) laeuft auf hoeherer Rechtestufe - schon sein Programmpfad ist von hier aus nicht lesbar. Von aussen beenden scheitert daran (Betriebsregeln: Fehler 5). Der einzige Weg von innen ist unser Modul (`{ "beenden": true }`, M2.04) - und genau das fehlt in einem Spiel, das aus der GUI kam.  
ANLEITUNG: Daniel schliesst dieses eine Spiel selbst. Vorbeugung: das Spiel nur ueber `werkzeug/starte_spiel.py` (VillageStudio) bzw. die Entwicklermodus-Verknuepfung starten - dann ist das Modul drin und das Beenden geht per Befehl.  
TEST: `python werkzeug/gui.py status` meldet "hoehere Rechtestufe, von hier NICHT beendbar" oder "laeuft nicht".  
WIDERLEGT, WENN: sich ein aus der GUI gestartetes Spiel doch von hier beenden laesst.  

### M2.11 Stronghold schliessen - in drei Stufen

*Stand: gemessen 30.09.2026, 21:06.*

ANLEITUNG: `python werkzeug/spiel.py beenden` (Status vorher/nachher: `python werkzeug/spiel.py status`).  
ERKLAERUNG: Drei Stufen, von sanft nach hart: (1) ist unser Modul geladen, beendet es das Spiel von innen (`{ "beenden": true }`, M2.04); (2) sonst bittet ein still erhoehter Helfer (M2.12) das Fenster zu schliessen, wie ein Klick aufs X; (3) erst wenn das nach 10 s nichts bewirkt, beendet der Helfer den Prozess hart. Das Werkzeug sagt, welche Stufe gewirkt hat.  
TEST, EINGEBAUT: geschafft = kein Crusader-Prozess mehr. Nicht geschafft = nach allen drei Stufen laeuft er noch; das Werkzeug nennt die moeglichen Gruende.  
GEMESSEN 30.09., 21:06: das aus der GUI gestartete Spiel (PID 15208, ohne Modul) - Stufe 1 entfiel, **Stufe 2 hat gewirkt**; Gegenprobe mit `tasklist`: kein Crusader-Prozess mehr.  
DU SIEHST: das Stronghold-Fenster verschwindet, ohne dass du klickst.  
WIDERLEGT, WENN: das Spiel weiterlaeuft oder nur mit Stufe 3 zu beenden ist, obwohl es auf Stufe 2 reagieren muesste.  

### M2.12 Hohe Rechte ohne Klick anfordern

*Stand: gemessen 30.09.2026, 21:04.*

ERKLAERUNG: Das Spiel laeuft auf hoher Rechtestufe, diese Sitzung auf mittlerer - daher kam jede Sperre "von aussen" (Fehler 5). Gemessen: Windows ist hier auf **"Erhoehen ohne Nachfrage"** eingestellt (`ConsentPromptBehaviorAdmin = 0`), und Daniels Konto ist in der Gruppe Administratoren. Ein Helfer, der hohe Rechte anfordert (`Start-Process -Verb RunAs`), bekommt sie also still - ohne Dialog, ohne Klick. Es wird dabei **keine Einstellung geaendert**; genutzt werden nur die Rechte, die das Konto ohnehin hat, und nur fuer den einen Befehl.  
TEST: `scratchpad`-Probe schrieb aus dem erhoehten Helfer "Hohe Verbindlichkeitsstufe (S-1-16-12288)", fertig nach 0,3 s, und konnte den Programmpfad des Spiels lesen - den eine normale Sitzung NICHT lesen kann.  
FOLGE: Was bisher "von aussen gesperrt" hiess (Spiel beenden, vermutlich auch Fenster verschieben, Tasten schicken, Speicher lesen), ist mit einem erhoehten Helfer erreichbar. Einzeln zu messen, bevor es behauptet wird.  
OFFEN: Warum das Spiel ueberhaupt hoch laeuft - es hat weder das Kompatibilitaets-Haekchen "Als Administrator ausfuehren" noch ein Manifest, das Rechte verlangt.  
WIDERLEGT, WENN: der Helfer mit mittlerer Stufe laeuft oder Windows einen Dialog zeigt.  

### M3.01 Zurueck ins Hauptmenue per Befehl

*Stand beim Anlegen: gemessen*

ZIEL: Aus jedem Bildschirm zurueck ins Hauptmenue.  
STAND: gemessen ({ "menue": 41 }, zuletzt am 30.09. aus dem Endbildschirm).  
DU SIEHST: das Hauptmenue erscheint, ohne Klick.  
WIDERLEGT, WENN: das Spiel im alten Bildschirm stehen bleibt.  

**Vorschlag:** Live abnehmen.  

### M3.02 Eigenes Spiel ohne Maus starten

*Stand beim Anlegen: teils gemessen*

ZIEL: Ein 'Eigenes Spiel' (nicht Kampagne) startet per Befehl.  
STAND: Der Befehl 'eigenesGefecht' im Modul ist am 01.09. gelaufen, aber noch NIE mit der Team-Liga und der Liga-Karte.  
ICH PRUEFE: Spielmodus 'Gefecht', keine Kampagnen-Mission, Uhr laeuft.  
DU SIEHST: das Spiel startet auf der Liga-Karte, du hast nichts geklickt.  
WIDERLEGT, WENN: wieder eine Kampagnen-Mission kommt (mein Fehler von heute).  

**Vorschlag:** Als erstes live messen.  

### M3.03 Kampagne und eigenes Spiel sicher unterscheiden

*Stand beim Anlegen: offen*

ZIEL: Die Schleife weiss aus dem Speicher, ob ein eigenes Spiel laeuft - nicht aus einem Bild.  
STAND: offen. Anhaltspunkt im Modul: isSkirmishTrail = 0 beim eigenen Spiel.  
WIDERLEGT, WENN: das Merkmal bei der Kampagnen-Mission denselben Wert hat.  

**Vorschlag:** Bei M3.02 gleich mitmessen.  

### M3.04 Karte waehlen: Liga_Grumpy Neighbors

*Stand beim Anlegen: offen*

ZIEL: Die Karte ist per Befehl waehlbar.  
STAND: offen. Der Befehl nimmt einen Kartennamen ohne '.map'; die Datei liegt im Plugin-Ordner der Team-Liga, der Kartenlader ist darauf eingestellt. Ob der Name von dort gefunden wird, ist nicht gemessen.  
DU SIEHST: die Liga-Karte mit ihrer Form.  
WIDERLEGT, WENN: eine andere Karte oder die Vorgabekarte erscheint.  

**Vorschlag:** Mit M3.02 zusammen messen.  

### M3.05 Selfaware auf beide KI-Plaetze

*Stand beim Anlegen: abgelesen*

ZIEL: Beide Computergegner sind unsere KI.  
STAND: abgelesen - der Befehl setzt alle KI-Plaetze auf denselben Typ; 'ki: 1' ist der Rattenplatz (in diesem Mod Rotkaeppchen). Solange Selfaware noch nicht angelegt ist, spielen dort zwei Rotkaeppchen.  
ICH PRUEFE: KI-Liste im Speicher zeigt zweimal Typ 1.  
DU SIEHST: zwei Rotkaeppchen im Spiel.  
WIDERLEGT, WENN: eine andere Figur auftaucht.  

**Vorschlag:** Zuerst mit Rotkaeppchen abnehmen, Selfaware folgt in Lieferung 2.  

### M3.06 Feste Startplaetze: oben und unten

*Stand beim Anlegen: offen*

ZIEL: Unsere zwei KIs stehen immer oben und unten - wie in deinem Bild.  
STAND: offen. Das Modul verteilt die Plaetze heute ZUFAELLIG (abgelesen im Code). Die Platzliste liegt bei 0x01A275D0; wie man dort feste Plaetze eintraegt, ist ungeklaert.  
DU SIEHST: in drei Starts hintereinander stehen die Burgen jedes Mal an denselben Stellen.  
WIDERLEGT, WENN: sich die Plaetze zwischen zwei Starts aendern.  

**Vorschlag:** Das ist die erste echte Forschungsaufgabe - klein, aber noetig.  

### M3.07 Der Mensch auf Platz 1

*Stand beim Anlegen: offen*

ZIEL: Klaeren, was der Mensch im Selbstspiel tut, ohne das Ergebnis zu verfaelschen.  
STAND: offen. Das Modul setzt immer einen Menschen ('Daniel') auf Platz 1. Ohne Menschen war ein frueherer Versuch nach 87 Ticks entschieden. Greifen die KIs zuerst den Menschen an, misst das Spiel etwas anderes als 'Selfaware gegen Selfaware'.  
WIDERLEGT, WENN: ein Spiel endet, weil der Mensch faellt.  

**Vorschlag:** Siehe Frage 1.  
**Daniel, 30.09.:** ERLEDIGT durch Daniel: Einen Menschen auf Platz 1 gibt es in eigenen Gefechten der Team-Liga 2 nicht - der Mensch ist dort nur ein Geist. Genau dafuer wurde der Mod gewaehlt. Es spielen nur die zwei Selfaware-KIs gegeneinander, wie im StarCraft-Vorbild. Pruefen im ersten Lauf: Platz 1 hat keinen Lord. Wenn es spaeter auch in Vanilla ohne Menschen geht: gerne.  

### M3.08 Startgold und Startgueter wie in der Team-Liga

*Stand beim Anlegen: offen*

ZIEL: Das Spiel startet mit den Liga-Regeln, z. B. 0 Gold.  
STAND: offen. Das Modul setzt Ausgleich 2 und Startstufe 1 (am 01.09. gemessen, fuer die alte Config). Was das unter der Team-Liga ergibt, ist ungeprueft.  
ICH PRUEFE: Gold und Waren beider KIs im ersten Tick.  
DU SIEHST: die Gold-Anzeige.  
WIDERLEGT, WENN: eine KI mit Gold startet.  

**Vorschlag:** Mit M3.02 zusammen messen.  
**Daniel, 30.09.:** Die Balances gehoeren dazu. Quelle: SBAs Balance-Daten (shc-vergleichstabelle/daten, README zuerst); fuer Team-Liga ist liga_ai.json die Wahrheit. GEMESSEN 30.09.: die im Spiel installierte liga_ai.json (Mod-KI-Team-Liga-2.0.2) ist inhaltlich identisch mit SBAs Quelle (Commit 5e9a83f) - 942 von 942 Werten gleich, nur die Schreibweise der Datei weicht ab. Das Startgold steht NICHT in liga_ai.json, sondern in der Erweiterung startResources (ucp-config.yml) - welcher ihrer Werte im eigenen Gefecht greift, wird im ersten Lauf gemessen.  

### M3.09 Tempo setzen

*Stand beim Anlegen: gemessen*

ZIEL: Das Tempo ist per Befehl einstellbar.  
STAND: gemessen am 30.09.: Tempo 40 = 40 Ticks/s, 1000 = rund 1100 Ticks/s.  
DU SIEHST: ich schalte zwischen 40 und 1000 um, das Spiel wird sichtbar schnell und wieder langsam.  
WIDERLEGT, WENN: sich die Ticks je Sekunde nicht aendern.  

**Vorschlag:** Live abnehmen.  

### M3.10 Neues Spiel ohne Neustart des Programms

*Stand beim Anlegen: teils gemessen*

ZIEL: Nach einem Spiel sofort das naechste - ohne Stronghold neu zu starten.  
STAND: gemessen nur fuer die Kampagnen-Mission (Hauptmenue, dann Start mit 'trotzdem' - die Uhr sprang auf 3470). Fuer das eigene Spiel noch nicht.  
DU SIEHST: zwei Spiele hintereinander, ohne dass das Fenster verschwindet.  
WIDERLEGT, WENN: das zweite Spiel den Zustand des ersten erbt (Uhr, Einheiten, Gold).  

**Vorschlag:** Nach M3.02 messen.  

### M4.01 Die Lords im Gefecht finden

*Stand beim Anlegen: gemessen*

ZIEL: Fuer jeden Spieler seinen Lord im Speicher finden.  
STAND: gemessen am 05.09.: Lord = Einheitentyp 55, je aktivem Spieler genau einer, Leben 150.000-165.000.  
ICH PRUEFE: in einem eigenen Spiel genau zwei KI-Lords plus dein Lord.  
DU SIEHST: ich nenne dir die Lords und ihre Leben; du findest sie im Spiel an den Burgen.  
WIDERLEGT, WENN: ein aktiver Spieler null oder zwei Lords hat.  

**Vorschlag:** Im ersten eigenen Spiel live abnehmen.  

### M4.02 Lord-Tod erkennen

*Stand beim Anlegen: gemessen*

ZIEL: Die Schleife merkt, wann ein Lord stirbt.  
STAND: gemessen am 05.09.: der Ausloeser ist das Leben (<= 0), nicht der Zustand der Einheit - bei Leben 0 bleibt die Einheit zunaechst stehen.  
WIDERLEGT, WENN: ein Lord im Spiel faellt, ohne dass sein Leben auf 0 steht.  

**Vorschlag:** Zusammen mit M4.04 live abnehmen.  

### M4.03 Was nach dem Lord-Tod wirklich passiert

*Stand beim Anlegen: offen*

ZIEL: Die echte Kette verstehen: Lord stirbt -> was passiert mit Einheiten, Gebaeuden, Anzeige, Uhr?  
STAND: offen. Bekannt ist nur: die Kampagnen-Mission endet mit Endbildschirm und stehender Uhr.  
ICH PRUEFE: den Zustand in den 500 Ticks nach dem Tod.  
DU SIEHST: den Moment, in dem der Lord faellt, und was danach geschieht.  
WIDERLEGT, WENN: das Spiel nach dem Tod normal weiterlaeuft, als waere nichts.  

**Vorschlag:** Wichtigster offener Punkt dieses Blocks.  

### M4.04 Der einfachste echte Tod: zwei Lords laufen aufeinander zu

*Stand beim Anlegen: offen*

ZIEL: Dein Vorschlag - beide Lords per Befehl aufeinander zuschicken, bis einer stirbt. Der kuerzeste echte Spielausgang.  
STAND: offen. Eine Einheit per Befehl bewegen ist belegt (05.09.); zwei Lords gegeneinander noch nie.  
ICH PRUEFE: Leben beider Lords je Tick, bis einer bei 0 ist.  
DU SIEHST: die zwei Lords laufen los, treffen sich, kaempfen, einer faellt.  
WIDERLEGT, WENN: sie aneinander vorbeilaufen oder nicht kaempfen.  

**Vorschlag:** Nach M4.01 - das ist der erste Punkt, der richtig Spass macht zu zeigen.  

### M4.05 Den Sieger aus dem Speicher lesen

*Stand beim Anlegen: offen*

ZIEL: Die Schleife liest selbst, wer gewonnen hat.  
STAND: offen; die Regel steht (Zettel Grundbedingungen): Sieger = der Spieler, dessen Lord als einziger noch lebt.  
WIDERLEGT, WENN: der gelesene Sieger nicht zu dem passt, was du am Bildschirm siehst.  

**Vorschlag:** Mit M4.04 abnehmen.  

### M4.06 Den Endbildschirm erkennen

*Stand beim Anlegen: gemessen*

ZIEL: Erkennen, dass das Spiel auf dem Endbildschirm steht.  
STAND: gemessen am 31.08.: Ansicht 30 = verloren. Achtung: der Wert 'Spielmodus' zeigt auch dann noch 'laeuft' - er taugt nicht als Anzeige.  
WIDERLEGT, WENN: der Endbildschirm zu sehen ist, die Ansicht aber nicht 30 (oder 58) meldet.  

**Vorschlag:** Im eigenen Spiel neu abnehmen.  

### M4.07 Zeitlimit: die ersten X Ticks

*Stand beim Anlegen: offen*

ZIEL: Kein Spiel laeuft ewig. Nach X Ticks endet es, gewertet wird nach Belohnung.  
STAND: offen - X ist noch nicht festgelegt.  
WIDERLEGT, WENN: ein Spiel ueber X Ticks hinaus laeuft.  

**Vorschlag:** Siehe Frage 2.  

### M5.01 Was ein Tick ist und wo er steht

*Stand beim Anlegen: belegt*

ZIEL: Ein Tick ist ein Rechenschritt der Spiellogik. Die Anzahl seit Spielbeginn steht im Speicher.  
STAND: belegt (Tickzaehler 0x0117CADC; Tag, Woche und Monat daraus vorhergesagt, 6 Messpunkte ohne Abweichung).  
DU SIEHST: ich lese den Tick, du vergleichst mit der Spieluhr (1 Tag = 50 Ticks).  
WIDERLEGT, WENN: Tick und Spielkalender auseinanderlaufen.  

**Vorschlag:** Live abnehmen.  

### M5.02 Die Grenze: hoechstens 11 Ticks je Bild

*Stand beim Anlegen: abgelesen*

ZIEL: Wissen, wann das Tempo nicht mehr steigt.  
STAND: abgelesen im Code - hoechstens 11 Ticks je gezeichnetem Bild. Bei 1.100 Ticks/s heisst das: rund 100 Bilder je Sekunde noetig. Faellt die Bildrate, faellt das Tempo mit.  
ICH PRUEFE: Ticks je Sekunde bei Tempo 1000, 2000 und 5000.  
WIDERLEGT, WENN: 2000 deutlich mehr als 1100 Ticks/s bringt.  

**Vorschlag:** Messen - bestimmt, wie viele Spiele pro Stunde gehen.  

### M5.03 Greift unser Modul jeden Tick ein oder nur jedes Bild?

*Stand beim Anlegen: offen*

ZIEL: Dein Endbild verlangt, dass die KI JEDEN Tick sieht. Dafuer muss das Modul je Tick laufen, nicht je Bild - bei Tempo 1000 liegen bis zu 11 Ticks zwischen zwei Bildern.  
STAND: offen. Laut Betriebsregeln haengt die Befehlsabfrage an der Tick-Funktion; die Zustandsmeldungen zaehlen aber Bilder.  
ICH PRUEFE: ein Zaehler im Modul je Aufruf, verglichen mit dem Tickzaehler.  
WIDERLEGT, WENN: der Modul-Zaehler langsamer steigt als der Tickzaehler.  

**Vorschlag:** Frueh klaeren - davon haengt die ganze 'Ansicht der KI' ab.  

### M5.04 Wie lange Ereignisse dauern (Katalog)

*Stand beim Anlegen: teils belegt*

ZIEL: Ein wachsender Katalog: Ereignis -> Dauer in Ticks -> beeinflussbar ja/nein.  
STAND: belegt ist erst ein Eintrag: ein Bauschritt der KI dauert genau 50 Ticks (445 von 445 Schritten). Offen: Rekrutieren, Laufen je Feld, Pfeilflug, Produktion, Nahrung.  
WIDERLEGT, WENN: ein gemessener Wert bei Wiederholung abweicht.  

**Vorschlag:** Den Katalog anlegen und mit jeder Messung fuellen - nicht alles vorab.  

### M5.05 Veraendert das Tempo das Spiel?

*Stand beim Anlegen: offen*

ZIEL: Sicher sein, dass ein Spiel bei Tempo 1000 genauso ausgeht wie bei Tempo 40 - sonst lernt die KI etwas, das im echten Spiel nicht gilt.  
STAND: offen.  
ICH PRUEFE: dieselbe Partie 5x bei Tempo 100 und 5x bei 1000, Ausgang und Tick des Lord-Todes vergleichen.  
WIDERLEGT, WENN: sich die Ausgaenge zwischen den Tempi klar unterscheiden.  

**Vorschlag:** Vor der Lernschleife messen.  

## Entscheidungen aus Lieferung 1

- **Frage 1 - Was macht der Mensch auf Platz 1?** Entfaellt - siehe M3.07 (kein Mensch in TL2-Gefechten).
- **Frage 2 - Wie gross ist X beim Zeitlimit?** Angenommen: X wird gemessen (drei Spiele ohne Limit, X = das Anderthalbfache des laengsten, auf Spieljahre gerundet). Daniel: alle Liga-KIs sind gut ausbalanciert; toetet unsere KI frueher, umso besser.
- **Frage 3 - Bei welchem Tempo nimmst du ab?** Zuschau-Tempo 90 (Daniel: da sieht man noch, wie die KI einzelne Befehle erteilt). Gelernt wird bei 1000.

## Laufprotokoll

### Lauf 1 - 30.09.2026, 21:10 - erstes eigenes Spiel

Aufbau: `werkzeug/config.py eintragen` -> `starte_spiel.py --links` -> `{"eigenesGefecht": true, "karte": "Liga_Grumpy Neighbors", "ki": 1, "gegner": 2}` -> sofort `{"pause": true}` -> messen -> Tempo 90. Alle Befehle ueber `werkzeug/befehl.py`.

**Was geklappt hat (im Hintergrund belegt, Daniel hat das Spiel live gesehen):**
- Eigenes Spiel per Befehl, Karte "Liga_Grumpy Neighbors" (Kartenname im Speicher), Kampagnen-Kennzeichen isSkirmishTrail = 0, Spielmodus 99, Ansicht 14 (im Spiel). Fuer M3.03 fehlt noch der Vergleichswert einer Kampagnen-Mission.
- Beide KI-Plaetze tragen Typ 1 (Rotkaeppchen): KI-Liste `[0, 0, 1, 1, 0, 0, 0, 0, 0]`.
- Pause per Befehl haelt: Tick 4691 vor und nach dem Messen gleich (M3.11). Fortsetzen ebenso.
- Einheiten-Array im Spiel erneut bestaetigt (fuenf Totschlagtests gruen, 241 belegte Plaetze).

**Was dabei gelernt wurde (Pannen als Gewinn):**
- Die GUI hatte `continueOutOfFocus` auf `pause` gesetzt -> im Hintergrund hielt das Spiel an, kein Befehl kam an. Jetzt prueft und repariert `config.py` das mit (M2.13). Hin- und Rueckweg: `pause` = angehalten, `render` = laeuft weiter.
- Ein Tempo-Befehl VOR dem Start verpufft: nach dem Start stand das Tempo auf 3000 (M3.12). Das Spiel lief damit nur rund 780 Ticks/s - ein weiterer Hinweis auf die Grenze von 11 Ticks je Bild (M5.02).
- `peek` liefert negative Speicherwoerter 16-stellig statt 8-stellig; beim Auswerten auf 32 Bit kuerzen.

**Was noch nicht stimmt (Daniel, 21:14: "du bist ein Spieler unten, Rotkaeppchen ist rechts statt oben, beide sollten Rotkaeppchen sein"):**
- **Ein echter Mensch spielt mit:** Spieler 1 hat einen Lord, 12 Einheiten, 4000 Gold und eine Burg unten links. Daniels Weg ueber die Lobby macht den Menschen in der Team-Liga zum Geist - unser nachgebauter Startbefehl `eigenesGefecht` setzt ihn dagegen ausdruecklich ein (M3.07 wieder offen).
- **Nur eine Rotkaeppchen ist im Spiel:** Spieler 3 hat Lord, 84 Einheiten, 1467 Gold; Spieler 2 hat KEINEN Lord, 0 Gold, 0 Holz, 4 Einheiten.
- **Startplaetze zufaellig und vermutlich ungueltig:** Startplatz-Liste `[246, 0, 246, 2, 1, 246, 246, 246]` (246 = frei). Vermutung, ungeprueft: Index = Startplatz auf der Karte, Wert = Spieler. Dann stuende Spieler 2 auf Startplatz 4 - die Karte hat aber nur vier Plaetze. Das wuerde erklaeren, warum er weder Burg noch Lord hat.
- Startgold nicht gemessen: pausiert wurde erst bei Tick 4691. Naechstes Mal sofort nach dem Start.

### Lauf 2 - 30.09.2026, ab 21:18 - Daniels richtiger Aufbau als Referenz

Daniel hat das Gefecht ueber die Lobby so aufgebaut, wie es sein soll: Liga_Grumpy Neighbors, zwei Rotkaeppchen oben und unten, kein Mensch. `werkzeug/aufbau.py` hat diesen Aufbau aus dem Speicher gelesen - **das Rezept fuer unseren Startbefehl, gemessen statt geraten:**

| Feld | Lobby (richtig) | unser `eigenesGefecht` |
|---|---|---|
| Spieler-IDs (fullID) | alle -1 | Platz 1 = Mensch |
| Mannschaft des Menschen | 255 = nicht dabei (Geist) | 0 = spielt mit |
| Mannschaft der KIs | 0 und 0 | 1 und 2 |
| Startplatz-Liste | `[246, 2, 1, 246, ...]` -> Plaetze 1 und 2 | zufaellig, u. a. 4 |
| KI-Variante | 0 und 1 (Grossmutter / Jaegersmann) | nicht gesetzt |
| Lords | Spieler 2 und 3 je einer, Spieler 1 nichts | Mensch mit Lord, Spieler 2 ohne |

Beide KIs hatten bei Tick 114 je 1850 Gold. Beobachter-Daten: `daten/lauf2_daniels_aufbau.jsonl` (rund 90 Ticks/s, beide Lords lebten bis mindestens Tick 28.160).

### Sammeln statt raten - das Verfahren (30.09.2026, Daniel: "erst alles sammeln, dann etwas Klares rausfischen und damit testen")

- **M6.01 Schnappschuss** `{ "abzug": "<name>" }` (logik.lua): 11 Speicherbereiche roh in Dateien - Spieler, Einheiten, Gebaeude, Bauplaene, Spielzustand, Kern, fuenf Kartenschichten. **Gemessen: 3,6 MB in 0,2 s** - schnell genug fuer jede Pause.
- **M6.02 Vergleich** `werkzeug/vergleich.py <A> <B>`: welche Stellen sich bewegt haben, bei Tabellen je Feld zusammengefasst, Uhr-Felder markiert. **Gegenprobe bestanden:** die eigene Tempo-Aenderung 90 -> 50 erscheint genau bei Kern +0xC8 = der bekannten Tempo-Adresse.
- Erstes Paar (Tick 28.058 -> 28.160): rund 12.000 geaenderte Woerter. Zeitstempel-Felder (Einheit +0x3C/+0x40/+0x350/+0x354, Gebaeude +0x27C, Kern +0x98), bewegte Einheiten (+0xC4/+0xD4 bei 173 von 682), ein gemeinsamer Gebaeude-Zaehler (+0xC0 bei allen 207: 57 -> 59), 36 Kartenkacheln verlieren ein Bit, wachsende Spielerfelder (+0x2088, +0x2148/+0x22DC). Bericht: `daten/vergleich_p1.json`.
- Naechster Schritt je Kandidat: **Steuerbarkeitstest** - Wert schreiben, laufen lassen, zuruecklesen: gehalten (steuerbar) oder ueberschrieben (vom Spiel berechnet).
- **M6.03 Steuerbarkeitstest** `werkzeug/steuertest.py <adresse> <wert> [ticks] [tempo]` - pausieren, schreiben, sofort zuruecklesen, N Ticks laufen lassen, einordnen, Original wiederherstellen (Rueckweg). Erste drei Laeufe, je rund 100 Ticks bei Tempo 100 (30.09.2026, Daniels Lobby-Gefecht):
  - **Gold Spieler 2** (Eichung, belegt schreibbar): 77777 geschrieben -> 77772 nach 102 Ticks -> **steuerbar**, das Spiel rechnet vom geschriebenen Wert weiter (5 Gold ausgegeben).
  - **Kern +0x98** (gedacht als Negativlauf, weil es mit der Uhr tickt): 5 geschrieben -> 106 nach 101 Ticks. **Meine Annahme war falsch:** ein Zaehler, der je Tick um 1 waechst, uebernimmt den geschriebenen Wert und zaehlt von dort weiter - er ist also schreibbar. Das Werkzeug hat richtig geurteilt, der Negativlauf war schlecht gewaehlt.
  - **Spieler 2 +0x2148** (Kandidat aus dem Vergleich): 999 geschrieben -> 110 nach 100 Ticks (Original 108). **Das Spiel berechnet den Wert selbst neu** - nicht direkt steuerbar; steuern ginge nur ueber seine Zutaten. Vermutet, ungeprueft: Bevoelkerung (dieselben Werte stehen bei +0x22DC).
  - Damit hat das Werkzeug beide Ergebnisarten gezeigt: "steuerbar" und "wird berechnet". Der echte Negativfall kam aus dem Kandidaten, nicht aus dem geplanten Negativlauf.

### Lauf 3 - 30.09.2026, 21:30 - wiederholbarer Selbstspiel-Start und Pause auf den Tick genau

- **M3.13 Selbstspiel-Start** `{ "eigenesGefecht": true, "selbstspiel": true, "karte": "Liga_Grumpy Neighbors", "ki": 1, "gegner": 2 }` schreibt die an Daniels Lobby gemessenen Werte (kein Mensch, Mannschaft 255/0/0, Startliste `[246,2,1,...]`, Varianten 0/1) und laesst die Zufallsplatzierung weg. **Test `werkzeug/selbstspiel.py 3` - GESCHAFFT:** drei Starts hintereinander identisch - Burgen immer bei (162,104) und (224,282), je ein Lord bei Spieler 2 und 3, Spieler 1 ohne Einheit, sogar gleiche Einheitenzahlen (22/23). Loest M3.05, M3.06, M3.07 fuer unseren Startweg.
- **M5.06 Pause auf den Tick genau** `{ "tickpause": { "bei": N, "alle": K, "bis": M } }` - ein Waechter im Taktgeber `everyTick()`, der jeden Tick laeuft. **Test `werkzeug/tickpause_test.py`:** bei Tempo 100 UND 1000 haelt das Spiel exakt beim Ziel-Tick an (+0), danach laeuft kein Tick mehr durch. Damit ist auch **M5.03 beantwortet: unser Modul laeuft wirklich jeden Tick mit.**
- **M5.07 Pause bei Tick 1 eines neuen Spiels** `"startpause": 1` im Startbefehl. Zweimal exakt bei Tick 1. Zwei Funde auf dem Weg: (a) **Im Hauptmenue kommen nur Startbefehle durch** - `tickpause` und `pause` im Menue werden stillschweigend verworfen; (b) **waehrend des Gefechtsaufbaus liefert der Tickzaehler kurz Unsinn** (7.807.163) - der Waechter ignoriert jetzt Werte weit ueber dem Ziel.
- **Erster Blick in den Spielbeginn, tick-genau:** Tick 1-25 nur neutrale Einheiten; Tick 50 je Spieler 1 Einheit ohne Lord; **Tick 100 je ein Lord** (4 bzw. 5 Einheiten); Tick 400 rund 20 Einheiten. Die Lords erscheinen zwischen Tick 50 und 100.

### Lauf 4 - 30.09.2026, 21:40 - Steuerkarte der Spielerfelder

- **M6.04 Steuerkarte** `werkzeug/steuerkarte.py <ausgabe.json> [start] [schritt] [spieler]`: frisches Selbstspiel, Pause genau bei Tick 1000, Schnappschuss, 100 Ticks weiter, zweiter Schnappschuss; Kandidaten = die Felder von Spieler 2, die sich bewegt haben. Je Feld: Original + 1000 schreiben, **genau 100 Ticks** (Tick-Pause), zuruecklesen, einordnen, Original zurueck. Werte mit Betrag >= 100.000 nicht angefasst (vermutlich Zeiger).
- Umfang: 45 bewegte Felder, 4 nicht angefasst, **41 getestet in rund 2,5 Minuten** (41 Schritte zu je 100 Ticks; die Zeit geht in die Befehle, nicht in die Ticks).
- **Ergebnis: 13 steuerbar, 28 vom Spiel berechnet.**
  - gehalten (8): +0x444 (100), +0x448 (1850), +0x44C (0), **+0x4D8 Holz** (Ware 2), +0x20AC (3), +0x2A54 (4), +0x2AFC (6), +0x389C (24)
  - weitergerechnet (5): **+0x50C Gold** (Ware 15; 2826 -> 2726, 100 ausgegeben), +0x20EC (11976, +600 je 100 Ticks), +0x2B38 (79), +0x2B3C (81), +0x39D4 (5100, +100 je 100 Ticks - zaehlt mit den Ticks)
  - zurueckgesetzt (10): +0x8C, **+0x500 (Ware 12, Fleisch)**, +0x2094, +0x2180, +0x2190, +0x223C, +0x2B14, +0x2B78, +0x3684, +0x3928
  - neu berechnet (18): +0x78, +0x84, +0x88, +0x450, +0x2088, +0x209C, +0x20B0, +0x20B4, +0x2188, +0x2AE4, +0x2AF8, +0x2B08, +0x2B0C, +0x2B50, +0x2B6C, +0x2B70, +0x3100, +0x3860
- Auffaellig: Holz bleibt stehen, **Fleisch wird zurueckgesetzt** - Nahrung zaehlt das Spiel offenbar aus dem Kornspeicher nach, Holz nicht. Ungeprueft.
- Was die Felder bedeuten, ist bis auf Holz, Fleisch und Gold **nicht gedeutet** - die Karte sagt nur, WAS steuerbar ist. Rohdaten: `daten/steuerkarte_spieler2.json`.

### Lauf 5 - 30.09.2026, 21:46 - Wirkungstest der 13 steuerbaren Felder

- **M6.05 Wirkungstest** `werkzeug/wirkung.py`: zwei Kontroll-Laeufe ohne Eingriff (Selbstspiel, Tick 1000 -> genau 1100), dann je Feld ein Lauf mit Wert + 5000 bei Tick 1000; Vergleich mit Kontrolle 1 = **Fussabdruck** des Felds.
- **Rauschen:** auch die zwei Kontrollen unterscheiden sich an 4-5 Stellen (Kern +0x8 und +0xBC - wachsen wie Echtzeit-Zaehler; Kern +0x8C, +0xAC; Spieler 1 +0x34 beim Geist). Diese Stellen gehoeren kuenftig in eine Ausnahmeliste des Vergleichs.
- **Daniel, 30.09.:** zwei gleiche Kontrollen im Fenster Tick 1000-1100 sagen NICHTS darueber, ob das Spiel deterministisch ist - "wie wenn man bei Schach aus den ersten zwei Zuegen schliesst, das Spiel sei deterministisch". Verschiedene Kontrollen wuerden es dagegen widerlegen.
- **Fussabdruecke (Rauschen abgezogen):**
  - **+0x2A54** (4 -> 5004, gehalten): **458 Stellen** - 230 Einheitenfelder, 77 Gebaeudefelder, 100 Kacheln der Logikschicht, Grafik, Holz und Gold von Spieler 2. Der groesste Hebel; Bedeutung offen.
  - **+0x20AC** (1 -> 5001, nach 100 Ticks 0): Brot und Fleisch (Ware 10 und 12) verschieben sich, dazu ein Gebaeude (+0x148/+0x150). Vermutet: Kornspeicher/Nahrungsverteilung.
  - **+0x50C Gold** -> **+0x448 zieht mit** (1880 -> 6880): +0x448 ist ein Spiegel des Golds.
  - +0x444, +0x448, +0x44C, +0x4D8, +0x2AFC, +0x389C, +0x20EC, +0x2B38, +0x2B3C, +0x39D4: **in diesem Fenster keine Wirkung ueber das Rauschen hinaus** - nicht "wirkungslos", manche wirken vielleicht spaeter.
- Rohdaten: `daten/wirkung_spieler2.json`.

## Leitsatz (Daniel, 30.09.2026)

Das Ziel ist kein wiederholbares Spiel, sondern eine KI, die **jeden Tick auf spontane Entscheidungen reagiert** - spaeter gegen Menschen. Wiederholbarkeit ist ein **Pruefstand** (gleicher Start, eine Aenderung, vergleichen) und ein **Trainingswerkzeug**: ueber Spielstaende laesst sich eine bestimmte Lage beliebig oft laden und gezielt ueben. Immer opportunistisch denken.

## Naechste Kette: Spielstaende als Trainingslagen (M7, Definition offen fuer Daniel)

- **M7.01** Spielstand speichern per Befehl, ohne Maus. - **Im Hintergrund belegt 30.09., 22:03** (Lauf 7), Live-Abnahme durch Daniel offen.
- **M7.02** Spielstand laden per Befehl. - **Abgenommen von Daniel 30.09., 22:23** ("ja nehme ab"; Lauf 8).
- **M7.03** Gegenprobe: Schnappschuss direkt nach dem Speichern und direkt nach dem Laden - gleich bis auf das bekannte Rauschen = verlustfrei. - **30.09., 23:28-23:33 gemessen (Lauf 9): so wie definiert NICHT erfuellt** - der geladene Stand ist die Welt einen Tick weiter, der Tickzaehler zeigt aber den gespeicherten Wert; wiederholbar ist das Laden dagegen (zweimal laden = gleich). **Abgenommen von Daniel 30.09., 23:40 als "wiederholbar statt verlustfrei"** ("ja passt"): Startpunkt einer Trainingslage ist der geladene Stand.
- **M7.04** Szenario-Bibliothek: benannte Spielstaende fuer Sonderfaelle (Lord in Gefahr, Belagerung, Wirtschaftskrise); jeder Trainingslauf startet exakt dort.
- Danach **M8** Ansicht der KI je Tick und erste Reaktions-Regel mit gemessener Reaktionszeit in Ticks.

### Stand M7 nach Nachsehen (30.09.2026, 21:52 - Daniels Hinweis "schau, ob das schon beantwortet ist")

- **M7.02 Laden: SCHON GELOEST (gemessen 02.09.2026)** - VillageStudio `doku/Menue-Handbuch.md` ("Einen bestimmten Spielstand laden") und `doku/Uebergabe_2026-09-02.md`: Lade-Dialog per Menueknopf, dann in EINEM Auftrag (`befehle`) Scrollstand `0x01126628` und markierte Zeile `0x01126624` setzen und `{"laden": 2}` - 1,5 s. Fallen: Laden hebt die Pause auf (danach pausieren und Flag `0x01FEA054` pruefen); zwei Befehle kurz nacheinander loeschen einander (Poll alle 20 Bilder). **Wird uebernommen, nicht neu gebaut.**
- **M7.01 Speichern: OFFEN** ("noch nicht angefasst" laut Uebergabe 02.09.). Zwei Wege gefunden, Entschluesselung in `daten/dekomp_speichern_laden.c`:
  - (a) **Menueweg wie beim Laden** - im Lade-/Speicher-Dialog ist Knopf 3 "Speichern" (bisher nur abgelesen); braucht zusaetzlich den Dateinamen im Eingabefeld.
  - (b) `AutoSaveTriggered` (0x00489880) ist **kein einfacher Speicherknopf**, sondern ein netzwerk-synchronisierter Spielbefehl (verpackt Parameter, merkt je Spieler die Ankuendigung). Direkt rufen moeglich, aber riskanter.
  - Vorschlag: (a) zuerst - derselbe, schon belegte Mechanismus wie beim Laden.
- Nebenbei: `{"kamera": [x, y]}` gibt es schon (Uebergabe 02.09.) - Kamera an eine Kartenstelle, nuetzlich fuers Zuschauen (M12).

### Lauf 6 - 30.09.2026, 21:55 - erster Speicherversuch (M7.01), nicht geschafft - was wir dabei gelernt haben

- Speicherordner: `Documents\Stronghold Crusader\Saves` (neuester Stand vorher: "Walltest 4", 30.08.2026).
- Im laufenden Selbstspiel (Tick 1100): `{"optionen": 3}` (Speichern) und `{"laden": 3}` (Knopf Speichern) melden beide `ok=true` - **aber keine neue Datei**, und die **Ansichtsnummer bleibt 14** (im Spiel). **Befund:** im laufenden Spiel oeffnen die Knopf-Befehle keinen Dialog; vermutlich muss das Spieloptionen-Fenster (Esc) erst offen sein, bevor seine Knoepfe wirken. Ungeprueft.
- Die Bilder (`{"bild": "menue"}`) zeigen das bekannte **Mischbild** (oben altes Hauptmenue, unten Statusleiste) - kein Beweis in die eine oder andere Richtung. `"blt": true` in dieser Form loeste das Umkopieren NICHT aus (Logzeile fehlt) - die richtige Form des Schalters ist zu klaeren.
- **Naechster Schritt:** die Funktion finden, die im Spiel das Optionen-Fenster oeffnet (wie Esc), dann Speichern + Dateiname; Beweis ist allein die neue .sav-Datei im Ordner, nicht das Bild.

**Korrektur zu Lauf 6 (21:58):** `{"bild": "karte"}` liefert das echte Spielbild (das `"menue"`-Bild ist im Spiel das Mischbild mit pinkem Streifen - Daniel hat es erkannt). Darauf ist zu sehen: **der Speichern-Dialog IST offen** (Liste der Spielstaende, Knoepfe Speichern/Zurueck, **leeres Namensfeld**). Die Aussage "der Dialog geht im Spiel nicht auf" war falsch - gemessen war die Ansichtsnummer, geurteilt ueber den Dialog; ein Dialog, der sich darueberlegt, aendert die Ansicht nicht. Vermutlich speicherte der Knopf nur wegen des leeren Namens nicht. **M12.01 Bild vom laufenden Spiel: `{"bild": "karte"}` - belegt** (Bild `daten/bilder/bild_karte_1.png`, nicht im Repo).

**Spur zum Namensfeld (22:00, fuer M7.01):**
- `MenuTextInputState` beginnt bei **0x011265A8** (Groesse 0x1828): markierte Zeile `0x01126624` = Feld +0x7C, Scrollstand `0x01126628` = +0x80 (aus der Lade-Messung vom 02.09. zurueckgerechnet).
- Knopf 3 "Speichern" (`MenuItemActionHandler_SaveLoadMap_Buttons` 0x004943B0, case 3) holt den Dateinamen ueber `UserTextHandler::getCurrentText(&DAT_UserTextHandlerState)`; ist `textContentLengthArray[textArrayIndex]` leer, passiert nichts - **deshalb speicherte Lauf 6 nicht** (Dekompilat: `daten/dekomp_speichern_knopf.c`).
- Beim Oeffnen leert das Spiel das Feld (`activateModalDialogAndClearText`, MMT_SAVE_MAP). **Korrektur 22:06 - gemessen falsch:** nach einem Speichern stand beim erneuten Oeffnen der alte Name noch im Feld (Laenge 31). Das leere Feld beim allerersten Oeffnen hiess nur: es war noch nie etwas drin.
- Kandidaten zum Setzen des Namens: `getCurrentText` 0x004697C0, `getTextArrayPointer` 0x004697E0, **`setTextEntryAndUpdateCursor` 0x00469800** (this, p1, p2), `resetToTextIndex` 0x00469790. Naechster Schritt: diese entschluesseln (Adresse von DAT_UserTextHandlerState + Aufbau der Textablage), Namen schreiben, Knopf 3, Beweis = neue .sav im Ordner.
- **Live gesehen von Daniel (30.09., 21:58, eigener Screenshot):** Speichern-Dialog im laufenden Spiel offen, geoeffnet per `{"optionen": 3}` - Liste der Spielstaende, Knoepfe Speichern/Zurueck, leeres Namensfeld. Teilschritt "Dialog oeffnen per Befehl" damit abgenommen; offen bleibt nur der Name.
- **Namensregel fuer Spielstaende (Daniel, 30.09., 22:00: "klarerer Name, am besten was du testen willst"):** `<Meilenstein> <Was getestet wird> <Karte> T<Tick>`, Punkte als Bindestrich, hoechstens 32 Zeichen (das Spiel kuerzt Kartennamen auf 33). Erster Test: **`M7-01 Speichertest Grumpy T1100`**. Spaetere Trainingslagen z. B. `M7-04 Lord in Gefahr Grumpy T8000`.
- **Textablage entschluesselt (22:03, `daten/dekomp_textfeld.c`):** 16 Textfelder zu je 250 Byte ab **0x01652890** (`getTextArrayPointer`: Feld*0xFA + 0x1652890). `setTextEntryAndUpdateCursor` (0x00469800, thiscall, this ungenutzt, Argumente Feld und char*) kopiert einen Text ins Feld und setzt `textContentLengthArray[Feld]` und `textCursorIndexArray[Feld]` - genau die Laenge, die der Speichern-Knopf prueft. `getCurrentText` liefert `textArray[textArrayIndex]` (nur wenn `unknown01` != 0). **Plan:** Name `M7-01 Speichertest Grumpy T1100` ins aktive Feld schreiben (poke), dann `setTextEntryAndUpdateCursor(aktivesFeld, Zeiger auf dieses Feld)` rufen, damit Laenge/Cursor stimmen, dann `{"laden": 3}`. Offen: Adresse von `DAT_UserTextHandlerState` (fuer textArrayIndex).

### Lauf 7 - 30.09.2026, 22:03-22:09 - M7.01 Speichern ohne Klick: GESCHAFFT (im Hintergrund belegt)

Werkzeug: `werkzeug/speichern.py "<Name>"`. Selbstspiel Grumpy, pausiert bei Tick 1100 (Pause-Flag 1, Ansicht 14 - blieb die ganze Zeit so).

- **Weg (gemessen):** `{"optionen": 3}` oeffnet den Speichern-Dialog -> aktives Textfeld lesen (`0x01652740` = 2, also ist **DAT_UserTextHandlerState = 0x01652740 bestaetigt**, nicht mehr nur abgeleitet) -> Name wortweise ins Feld `0x01652890 + Feld*250` schreiben, Laenge nach `0x016527D0 + Feld*4`, Cursor nach `0x01652810 + Feld*4` -> `{"laden": 3}` (Knopf Speichern).
- **Beweis:** neue Datei `Documents\Stronghold Crusader\Saves\M7-01 Speichertest Grumpy T1100.sav`, 1.056.101 Byte, 22:03. Im Dialog oben in der Liste sichtbar ("M7-01 Speichertest Grump", 30/09/26 20:08 - **das Spiel zeigt Weltzeit**, zwei Stunden hinter der Ortszeit; "Walltest 4" genauso: Datei 21:32, Liste 19:32). Bild: `daten/bilder/m7-01_dialog_liste_t1100.png` (nicht im Repo).
- **Speichern geht in der Pause:** Der Knopf reicht einen Spielbefehl (`GCT_SAVE`, mit Tick und Pruefsumme der Einheiten) in die Warteschlange - er wird trotz Pause sofort ausgefuehrt, der Tick bleibt 1100.
- **Gegenlauf (22:07, gueltig):** Name "M7-01 Gegenlauf leer" steht sichtbar im Feld, Laenge aber 0 -> Knopf Speichern -> **keine Datei** (31 Dateien vorher, 31 nachher), Dialog bleibt offen. Damit ist belegt: die Laenge bei `0x016527D0` ist genau die Sperre, die der Knopf prueft - und die neue Datei kam vom Namen, nicht von allein.
- **Erster Gegenlauf-Versuch war ungueltig (22:05):** Ich wollte "ohne Namen" speichern, aber das Feld hatte noch den alten Namen (siehe Korrektur oben) -> das Spiel fragte **"Datei ueberschreiben?"**. Opportunistisch genutzt:
- **Ueberschreiben per Befehl (gemessen):** `{"dialogJa": true}` beantwortet die Ueberschreib-Frage - Dateizeit 22:03 -> 22:07. `speichern.py` macht das jetzt selbst, wenn es den Namen schon gibt; im Werkzeug-Durchlauf 22:08 bestaetigt.
- **Nebenbefund zum Sammeln:** Derselbe pausierte Stand, dreimal gespeichert: 1.056.101 / 1.056.104 / 1.056.104 Byte. Ein gespeicherter Stand ist also nicht Byte fuer Byte immer gleich lang - fuer M7.03 den Vergleich im Speicher machen (Schnappschuss nach Laden), nicht an der Datei.
- **Verlust bemerkt:** Die erste Fassung (22:03) ist durch das Ueberschreiben weg. Seitdem kopiert `speichern.py` jede gespeicherte Fassung mit Uhrzeit nach `daten/spielstaende/` (nicht im Repo, 1 MB je Stand).
- **Offen:** Live-Abnahme durch Daniel (Dialog steht offen, Eintrag oben in der Liste).

### Lauf 8 - 30.09.2026, 22:12-22:22 - M7.02 Laden per Name (Daniels Auftrag: Walltest 4, Waffengebaeude_test, den aeltesten)

Werkzeug: `werkzeug/laden.py "<Name>"` (oder `--liste`). Rezept aus dem Menue-Handbuch (02.09.) uebernommen, dazu zwei neue Teile:

- **Liste im Speicher gelesen statt geraten (gemessen):** Das Spiel sortiert nach einem eigenen Datum, das nicht immer zur Dateizeit passt (Walltest 3: Datei 19:21, Liste 17:28 Weltzeit). Anzahl bei `0x0112661C` (30); Eintrag n (0 = oben) = Namensnummer k bei `0x01126E28 + 4n`; Name bei `0x11BFCF8 + k*0x3E9` (`getLoadedMapNameForIndex` 0x0046C2E0, `daten/dekomp_kartenliste.c`). Geladen wird n = markierte Zeile + Scrollstand. (Die Strukturliste nennt `DAT_ArrayOfMapIndices` bei +0x884 = `0x01126E2C`; das Spiel liest aber Feld[n-1], also beginnt die Liste effektiv 4 Byte davor.) Aeltester Stand in der Liste = letzter Eintrag = **Tiberias 4 LUL** (Datei 12.04.2020) - nach Dateizeit ebenfalls der aelteste.
- **Neue Lade-Pause im Modul (`{"ladepause": true}`):** haelt beim ersten Tick an, an dem die Spielzeit springt - in beide Richtungen. Anlass (Panne, opportunistisch genutzt): die erste Fassung nutzte die Tick-Pause "jetzt + 1"; die greift nur, wenn der geladene Stand SPAETER liegt als der alte. Beim Laden eines frueheren Stands waere das Spiel ungebremst weitergelaufen.

| Stand | Eintrag | erster Tick nach dem Laden | Beleg |
|---|---|---|---|
| Walltest 4 | 1 | **18.988** | Bild `m7-02_Walltest_4_t18988.png` - Bergfried im Mauerring, rote Truppen (wie Bild vom 02.09.) |
| M7-01 Speichertest Grumpy T1100 (Probe mit bekannter Loesung) | 0 | **1.100** = gespeicherte Spielzeit | Sprung -17.888 erkannt, sofort angehalten |
| Waffengebaeude_test | 15 | **24.604** | anderes Gelaende (Oase, Felder, Bergfried mit Truppen); Waffenwerkstaetten im Bildausschnitt nicht eindeutig zu sehen |
| Tiberias 4 LUL (aeltester, 2020) | 29 (Scrollstand 14, Zeile 15) | **83.339** | grosse Burg mit Wassergraben; laedt ohne Absturz |

- **Gegenprobe vorher festgelegt, einmal nicht bestanden:** Fuer Walltest 4 hatte ich aus dem Handbuch 40.524 Ticks vorhergesagt - es waren 18.988. Vermutung (ungeprueft): das Handbuch hat die Zeit gemessen, nachdem das Spiel schon weitergelaufen war (dort steht, die Pause kam zu spaet). Die harte Probe lieferte dann M7-01: geladen = gespeichert = 1.100, auf den Tick.
- **Laden ist tick-genau:** der erste Tick nach dem Laden ist die gespeicherte Spielzeit selbst (M7-01: 1.100).
- **Beobachtung, Ursache offen:** Nach dem Anhalten kamen noch drei Tick-Aufrufe an, alle mit derselben Spielzeit - der Taktgeber laeuft kurz weiter, ohne dass die Zeit vorrueckt.
- **Beobachtung:** Nach dem Laden von Tiberias stand das Tempo auf 20 (vorher 1000er-Bereich) - vermutlich bringt der Spielstand sein Tempo mit. Danach auf Daniels Zuschauertempo 90 gesetzt.
- **Offen:** Live-Abnahme durch Daniel (Tiberias steht pausiert im Spiel); M7.03 = Schnappschuss nach Speichern gegen Schnappschuss nach Laden.

### Lauf 9 - 30.09.2026, 23:21-23:34 - M7.03 Verlusttest: verliert Speichern und Wiederladen etwas?

Vorlauf: Das Spiel war um 22:24 zu (Log endet 8 s nach dem Laden eines Stands mit Tick 25.194; kein Absturz in der Windows-Ereignisanzeige). Neu gestartet per `VillageStudio/werkzeug/bis_menue.py` (10 s bis Hauptmenue, Config unveraendert).

**Zwei Pannen, beide opportunistisch zu Faehigkeiten gemacht:**
- **Laden aus dem Hauptmenue:** dort reicht das Modul nur Listen (`{"befehle": [...]}`) und wenige Einzelbefehle durch - `optionen`, `laden`, `ladepause` einzeln kaemen nie an. `laden.py`/`speichern.py` schicken jetzt jeden Befehl als Liste; im Hauptmenue oeffnet `laden.py` erst die Einstellungen (`hauptmenue: 8`). Gemessen: Spielstart + Laden = Tick 1100 in rund 20 s.
- **Wiederladen mit gleicher Spielzeit (23:26:00, Log):** M7-01 ueber M7-01 geladen -> kein Zeitsprung -> die Lade-Pause merkte nichts, das Spiel lief bis Tick 1564. **Gemessen dazu (23:26:48):** der Taktgeber des Moduls laeuft auch in der Pause (Tick-Pause auf den aktuellen Tick loeste im pausierten Spiel aus, Spielzeit blieb stehen). Die Lade-Pause erkennt ein Laden jetzt an **Zeitsprung ODER aufgehobener Pause** (scharf gemacht wird im pausierten Spiel; Laden hebt die Pause auf). Proben: scharf im pausierten Spiel, 3 s nichts geladen -> loest nicht aus; zweimal M7-01 hintereinander -> "Laden erkannt (Pause aufgehoben) bei Tick 1100".

**Der Verlusttest** (`werkzeug/verlusttest.py`, Bericht `daten/verlusttest_232853.json`): M7-01 laden, genau 100 Ticks -> A (Tick 1200); speichern als `M7-03 Verlusttest Grumpy T1200` -> A2; M7-01 laden (Speicher ueberschrieben) -> Z; M7-03 laden -> B. Je Schnappschuss 11 Bereiche, 3,6 MB.

**Eingrenzung** (`werkzeug/verlust_eingrenzen.py`, Bericht `daten/verlust_eingrenzen_233135.json`):

| Vergleich | abweichende Woerter (ausser Rauschen) | heisst |
|---|---|---|
| A gegen A2 | 0 | Speichern veraendert nichts |
| A gegen Z (Gegenprobe) | 3.917 | der Vergleich misst etwas |
| B gegen B2 (zweimal dieselbe Datei laden) | 1 (Kern +0xB0, 1 -> 2) | **Laden ist wiederholbar** |
| A gegen A' (zweimal "M7-01 + 100 Ticks") | 2 (Kern +0xB4/+0xB8) | der Lauf ist wiederholbar (in diesem Fenster) |
| **A gegen B** (vorher festgelegter Massstab) | **1.655** | **nicht verlustfrei wie definiert** |
| B gegen A'1 (A plus ein Tick) | **60** | B ist die Welt **einen Tick weiter** |
| B1 gegen A'2 (einen Tick spaeter) | 76 | der Versatz bleibt bei einem Tick |

- **Befund:** Nach dem Laden steht der Tickzaehler auf dem gespeicherten Wert (1200), Einheiten, Gebaeude und Spieler sind aber schon einen Tick weiter (z. B. Gebaeude-Zeitstempel 1201 statt 1200). Ob das Speichern oder das Laden den Tick dazugibt, ist **offen** (A2 = A, der laufende Stand aendert sich beim Speichern also nicht).
- **Die 60 Reststellen:** Gebaeudeliste-Kopf +0x8 (nach jedem Laden 2000, im Lauf 69) und +0x10; vier Gebaeude (Nr. 3, 5, 12, 14) mit Zaehlern um einen Schritt anders; bei allen Spielern +0x2AE4 (2 statt 1); Spieler 2/3 +0x6C, +0x2AEC, +0x2B08; ein Einheitenfeld; Kern +0x98/+0xA0/+0xB8; 23 Stellen in der Grafikschicht. **Gold, Vorraete und die uebrigen Einheitendaten: gleich.**
- **Kern +0xA0** = Tick des letzten Ladens + 1 (A: 1101 nach Laden bei 1100; B: 1201 nach Laden bei 1200) - ein Lade-Merker, kein Spielzustand.
- **Was das fuer das Training heisst (Vorschlag, Daniels Entscheidung):** Fuer die Szenario-Bibliothek zaehlt, dass jeder Trainingslauf aus einem Spielstand **gleich** startet - das ist belegt (B = B2). Der Startpunkt einer Lage ist dann "der geladene Stand", nicht "der Moment des Speicherns".

## M9 Navigation auf der Karte (Daniels Auftrag 30.09.2026, 23:40)

Daniels Bedienung: Tab = Leiste weg; C/X = drehen; Leertaste = abflachen; Rechtsklick gedrueckt halten = Menue (links abflachen, unten abgesenkt mit Gebaeuden offen, rechts zoomen - "die weiter raus Zoomstufe empfohlen" -, oben drehen); Pfeiltasten und Raender = scrollen. "Nichts ist besser, nur so nutze ich das."

**Weg:** keine Tasten druecken (Daniel arbeitet daneben), sondern die Spielfunktionen dahinter per Befehl rufen. Abgelesen aus `WindowMsgProcessingFunc` (Tasten) und `MenuItemActionHandler_InGameMenu_PeasantBuildAndRightClickMenuSelection` (Rechtsklick-Menue), Dekompilate `daten/dekomp_navigation*.c`. Werkzeug `werkzeug/navigation.py` (Bericht `daten/navigation_*.json`, Bilder `daten/bilder/m9_*`).

| Nr | Befehl | Spielfunktion | Stand 30.09., 23:50 |
|---|---|---|---|
| M9.01 | `{"kamera": [x, y]}` | `focusOnCoordinate` 0x004E8CA0 | **belegt** - Bild 68 % anders |
| M9.02 | `{"leiste": true}` (Umschalter) | `hideOrUnhideUI` 0x00471AA0 (Tab) | **belegt** - Menuereiter 48 <-> 60, sichtbare Breite 246 <-> 278 Felder; im Kartenbild verschwindet die Kapuze des Beraters unten und kommt beim Rueckweg wieder (gleicher Ausschnitt: oben 0,0 %, unten 1,7 % anders) |
| M9.03 | `{"drehen": "rechts" \| "links"}` (auch 0/2/4/6) | `setMapRotation` 0x004F70E0 (Strg+Pfeil, Rechtsklick oben) | **belegt** - Ausrichtung 0 -> 6 -> 0, Bild je ueber 60 % anders. Welche Richtung im Bild "im Uhrzeigersinn" ist: noch nicht bestimmt |
| M9.04 | `{"grundriss": true \| false}` | `toggleFlatView` 0x004F70B0 (Leertaste, Rechtsklick links) | **belegt** - 0 -> 1 -> 0, Bild je 14 % anders; dabei stellt das Spiel die Absenk-Stufe selbst auf 2 und zurueck auf 4 |
| M9.05 | `{"zoom": "raus" \| "rein"}` | `resetupViewport` 0x004E7770 (Strg+Hoch, Rechtsklick rechts) | **belegt** - raus = 246 x 130 Felder sichtbar, rein = 123 x 65; das Spiel stand schon auf "raus" |
| M9.06 | `{"absenken": true \| false}` | `triggerLoweredView` 0x004F6FD0 (Rechtsklick unten, Strg+Runter) | **offen** - greift nur einen Augenblick: das Rechtsklick-Menue setzt die Ansicht in jedem Bild auf normal zurueck, solange nichts gedrueckt gehalten wird (abgelesen); gemessen: Modul las 3, danach wieder 4. Eine Halte-Ansicht wie Daniels Maustaste |
| M9.07 | Scrollen wie Pfeiltasten | `ScrollingHandler` 0x0112B070 | nicht gebaut - `kamera` springt direkt |

- Gegenlaeufe: Jeder Schalter ging vom **echten** Startzustand ins Gegenteil und zurueck; am Ende stand jedes Feld wieder auf dem Ausgang. (Erster Lauf 23:44 war fehlerhaft: Grundriss und Zoom standen schon auf an/raus, und die Absenk-Stufe las ich am falschen Feld - das Spiel verbraucht 0x01FE7AC0 sofort, der Stand steht in 0x01FE7AC4.)
- Das Speicherbild `{"bild": "menue"}` zeigt im Spiel nur die zuletzt gezeichnete Leiste - als Beleg fuer die Leiste taugt es nicht; das Kartenbild nach einem Kamera-Anstoss schon.
- Die Kamerafelder 0x021AEC74/78 sind nicht dieselben Koordinaten wie im `kamera`-Befehl (Befehl (162,104) -> Felder (138,133)).
- **Offen:** Live-Abnahme durch Daniel fuer M9.01-M9.05; Drehrichtung im Bild; ob M9.06 gebraucht wird.

### Lauf 10 - 01.10.2026, 00:00-00:14 - M4.04 Lord-Duell (Daniels Auftrag: beide Lords befehligen, gleichzeitig in der Mitte treffen, kaempfen, Sieg, Schadens-Ausloeser, speichern/laden)

Werkzeug `werkzeug/lordduell.py` (Mitschriften `daten/lordduell_*.txt`), neue Modulbefehle `lords`, `lordwacht`, `zielsuche`. Start immer aus `M7-01 Speichertest Grumpy T1100`.

**Unterwegs gelernt (gemessen):**
- **Ort einer Einheit = Mikro-Position / 8** (+0xB6/+0xB8) - dasselbe System wie `einheit_ziel` und das Ziel (+0xC8/+0xCA). Das Kachelfeld +0xD4 ist nicht y*400+x (so gelesen "sprang" ein Lord in 50 Ticks um 270 Felder).
- **Die KI holt ihre Lords heim:** ein einmaliger Befehl haelt nur kurz, dann steht wieder die Burg als Ziel. Die Lord-Wacht haelt das Ziel fest (setzt nach, hoechstens alle 10 Ticks, nur im laufenden Spiel) bis zum Treffen und laesst dann los.
- **In der Pause trug das Spiel das Ziel nicht ein** - die erste Wacht setzte deshalb ueber 21.000 Mal nach, das Spiel stand bei Tick 1106 still. Seitdem nur im laufenden Spiel.
- **Platz 0** der Einheitenliste hielt eine Lord-Kopie (Typ 55) - kein echter Lord; die Liste beginnt jetzt bei 1.
- **Die Kartenmitte (200,199) ist kein gueltiges Ziel** (Oase); `zielsuche` fand das naechste gueltige Feld **(194,193)**.
- Burgen/Lords: Spieler 2 Lord 3 bei (172,113), Spieler 3 Lord 137 bei (227,284).

**Gleichzeitig ankommen:** Probelaeufe - Lord 137 braucht 1.917 Ticks bis zur Mitte (Ankunft 3017), Lord 3 allein 2.277 (Ankunft 3377, Umweg um Felsen). Echter Lauf mit Lord 137 **360 Ticks spaeter**: Treffen bei Tick 3329, Lord 3 drei Felder und Lord 137 zwei Felder vor dem Ziel.

**Der Kampf:**
| Tick | Ereignis |
|---|---|
| 3329 | Treffen (Abstand 3) |
| 3354 | **Erster Treffer - beide zugleich**, je 150.000 -> 149.850. Ausloeser haelt an, Bild, **gespeichert als `M4-04 Lordduell Treffer T3354`** (erste Trainingslage "Lord in Gefahr", M7.04) |
| 3354-4353 | beide verlieren **150 Leben je Tick**, im Gleichschritt |
| 4353 | **Lord 137 (Spieler 3) tot**; Lord 3 (Spieler 2) lebt mit **150 Leben** - Sieg um genau einen Schlag. Vermutung: Lord 3 ist im selben Tick zuerst dran (kleinere Nummer) - ungeprueft |
| 11.259 | Ansicht 14 -> **30: Endbildschirm "Maechtigster Fuerst"** (Auswertung beider Rotkaeppchen, Grabplatte, Totenkopf mit Datum Dez. 1181) - **6.906 Ticks nach dem Tod**; warum so spaet, ist offen |

- **Wiederholung aus dem Spielstand (M7.03/M7.04 angewandt):** `M4-04 Lordduell Treffer T3354` geladen, laufen lassen -> Lord 137 stirbt wieder bei **Tick 4353**, dieselben Stufen im selben Tick. Die Lage ist als Trainingsstart brauchbar.
- **Sieger aus dem Speicher (M4.05, ein Fall):** Sieger = der Spieler, dessen Lord noch lebt (Lord 3: Zustand 2, Typ 55, Leben 150); der Platz des toten Lords wird neu vergeben (spaeter Typ 44).
- **Beweisbilder** (nicht im Repo, `daten/bilder/`): `m4-04_BEWEIS_lords_kaempfen_t4023.png` (+ `_nah`), `m4-04_BEWEIS_endbildschirm_maechtigster_fuerst.png`.
- **Offen:** Live-Abnahme durch Daniel; warum der Endbildschirm erst 6.906 Ticks nach dem Tod kommt (M4.03); ob die Reihenfolge der Einheitennummern den Gleichstand entscheidet.

### Lauf 11 - 01.10.2026, 00:16-00:20 - M4.03 Was nach dem Lord-Tod passiert

Werkzeug `werkzeug/spielende.py` (Mitschrift `daten/spielende_lauf.txt`, Bericht `daten/spielende_*.json`), Dekompilat `daten/dekomp_spielende.c`. Start aus `M4-04 Lordduell Treffer T3354`.

- **Abgelesen:** `checkSkirmishGameDefeat` (0x00486600, aus `processGameTick`) zaehlt je Team die toten Lords (`lordKilledByPlayerID`). Lebt hoechstens noch ein Team, setzt es **sofort** `gameOver` (0x0117D500) = 1, `gameOverTime` (0x0117C888) = **Rechneruhr** (`timeGetTime`, ms), `playerIsAlive[9]` (short, ab 0x0117EF40) und blendet das Sieg/Niederlage-Fenster ein.
- **Gemessen:** der Endbildschirm (Ansicht 30, "Maechtigster Fuerst") kommt **rund 9-10 s Rechnerzeit** nach "Spiel vorbei" - Tempo 1000: 4.844 Ticks / 9.245 ms; Tempo 300: 1.799 Ticks / 9.698 ms. Die Ticks schrumpfen mit dem Tempo (0,37), die Zeit bleibt - Vermutung "feste Zeit" gehalten. (Tick-Angaben grob: ich habe etwa jede Sekunde nachgefragt; genau ist nur die Spieluhr.) Das erklaert die 6.906 Ticks aus Lauf 10: dort stand das Spiel beim Tod in der Pause, die Uhr lief weiter.
- **Sieger aus dem Speicher:** `playerIsAlive` = [0, 0, 1, 0, ...] -> Spieler 2. Das Fenster im Spiel sagt dasselbe: "Niederlage - Rotkaeppchen, & die Grossmutter gewinnt" (Niederlage aus Sicht des Geist-Menschen), Meldungen "... toetete Rotkaeppchen, & der Jaegersmann" und "... erhaelt 500 Gold". Bild `daten/bilder/m4-04_BEWEIS_sieg_fenster_im_spiel.png`.
- **Fuer die Lernschleife:** "gewonnen" ist mit `gameOver` = 1 sofort im Speicher ablesbar - auf den Endbildschirm muss niemand warten.

### Nachtrag 01.10.2026, 00:23 - Daniels Frage: waren die ersten Ticks in den 15 Versuchen gleich?

Ausgewertet aus `daten/wirkung_spieler2.json` (Wirkungstest 30.09.: 15 Laeufe, jeder aus frischem Selbstspiel-Start, Schnappschuss der 11 Speicherbereiche bei Tick 1100; in 13 Laeufen wurde bei Tick 1000 je ein Feld von Spieler 2 veraendert).

- **Kontrolle 1 gegen 2:** gleich bis auf 4 Woerter - Kern +0x8 und +0xBC (laufen wie eine Uhr in Millisekunden), Kern +0x8C (1044 -> 1046), Spieler 1 +0x34.
- **10 der 13 Laeufe mit Eingriff:** gegen Kontrolle 1 ausser genau diesen Uhr-Feldern (und dem veraenderten Feld selbst) **keine einzige** Abweichung.
- **+0x50C (Gold):** zusaetzlich nur +0x448 - das Spiegelfeld des Golds, also Folge des Eingriffs.
- **+0x20AC (Nahrung) und +0x2A54:** weichen ab (11 bzw. 458 Woerter) - Wirkung des Eingriffs; ob der Start gleich war, laesst sich aus diesen zwei nicht ablesen.
- **Ergebnis:** 13 von 15 Laeufen standen bei Tick 1100 gleich da (ausser Uhr-Feldern); kein Lauf zeigt eine Abweichung, die nicht vom Eingriff kommt. **Grenze:** verglichen wurde nur der Stand bei Tick 1100, nicht jeder fruehe Tick einzeln; und es zeigt nur, dass sich der Anfang wiederholt - nicht, dass das ganze Spiel deterministisch ist (Daniels Schach-Vergleich).

## M10 Einheiten steuern (Daniels Fragen 01.10.2026; gemessen 04.10.2026, 18:45-19:40)

Neue Modulbefehle: `gruppe`, `gebaeude`, `typen`, `einheitwacht` (Zielwechsel je Tick, erkennt neu belegte Plaetze), `halten` (festhalten / einfrieren / loslassen: frei, zurueck, arbeit), `arbeitsplatz`, `aufloesen`, `zickzack`. Werkzeuge: `einheiten_steuern.py` (v2), `gruppe_halten.py` (v2), `arbeit_pruefen.py`, `aufloesen_ersetzen.py`, `zickzack.py`. Neue Trainingslage: `M7-04 Mensch Grumpy T600` (echter Mensch auf Platz 1, eine Rotkaeppchen-KI).

| Nr | Frage | Ergebnis |
|---|---|---|
| M10.01 | Alle Einheitenarten bewegen? | **32 von 32 Typen nehmen den Befehl an** (Walltest 4: Soldaten, Arbeiter, Bauern, Lords, Narren, Tiere). 24 kommen binnen 600 Ticks an. Umgelenkt: beide Lords (nach 65/135 Ticks zur Burg), der Steinochse. Unterwegs, aber nach 600 Ticks noch 3-10 Felder vor dem Ziel: Narren, Bogenmacher, Jaeger. Ein Huhn verschwand (kein Steuerbefund). **Korrektur zu v1 (01.10.):** der Endpunkt-Test hielt z. B. den Bogenschuetzen fuer ungehorsam - er kam an und wurde 51 Ticks spaeter von der KI zurueckgeschickt. |
| M10.02 | Einheiten des Menschen bewegen? | **Ja** (M7-04 Mensch): Bauer, Bogenschuetze, Speertraeger, Narr kommen an und **bleiben**. **Vorhersage widerlegt:** auch dein Lord laeuft nach 101 Ticks von selbst zur Burg zurueck - das macht der Lord, nicht die gegnerische KI. Nebenbefund: KI-Lord dort 75.000 Leben, deiner 150.000. |
| M10.03 | Gruppe pausieren / zurueckrufen? | **Einfrieren gilt** (23 von 24 Apfelbauern stehen 300 Ticks still; ohne Halten bewegen sich alle). **Zurueckrufen gilt** (23 von 24 binnen 1200 Ticks am Kornspeicher; ferne Plantagen bis 85 Felder). **Halten gilt.** Loslassen: frei 1 von 24 arbeitet wieder, altes Ziel 17 von 24 (7 trugen gerade Aepfel - ihr altes Ziel war der Kornspeicher), **zum eigenen Arbeitsgebaeude (+0x338) 24 von 24**. Ablieferungen je 600 Ticks danach: 0, 1, 6, 7, 7, 3 gegen ohne Eingriff 8, 4, 8, 4, 6, 4 - **nach ~1200 Ticks wieder im Takt**; ein Rueckruf mit 1200 Ticks Halten kostet diese KI rund 20 Apfel-Lieferungen. |
| M10.04 | Aufloesen und ersetzen? | **Aufloesen gilt** (`disbandUnit` des Spiels: 3 Bogenschuetzen sofort weg, wurden Bauern - die KI hat ein Lagerfeuer). **Die KI ersetzt Verluste:** nach 100 und 200 Ticks je ein neuer Bogenschuetze; ohne Verlust wirbt sie im selben Fenster keinen an. **Ersetzen gilt** (`wandle`: 32 Schleuderer -> Schwertkaempfer, Hoechstleben 9.000 -> 40.000). |
| M10.05 | Wie schnell befehlen - jeden Tick? | **Eine laufende Einheit liest ihr Ziel nur an Feldgrenzen** (Bogenschuetze: alle 16 Ticks = ein Feld). Wechsel jeden Tick oder alle 2/8 Ticks: **keine Umkehr**, sie laeuft stur geradeaus. Alle 16 Ticks: Umkehr an jeder Feldgrenze. Totschlagtest vorher aufgeschrieben (K=8: 0 Umkehrungen, K=16: an jeder Grenze, K=3: unregelmaessig) - **bestanden**. Reaktionszeit also 0-16 Ticks je nach Lage im Feld. Nach dem Laden setzte die Bewegung erst bei Tick 50 ein (Ursache offen). |

**Opportunistisch mitgenommen:** Die KI ersetzt verlorene Truppen in ~100 Ticks je Einheit; verteilt Arbeit nach Zurueckrufen nicht neu; holt ihre Lords heim. Fuer saubere Steuer-Messungen stoert sie - siehe Daniels Vorschlag unten.

**Daniels Vorschlag (04.10., 19:31):** "warum laesst du die KI ueberhaupt was machen? ... live AIC bearbeiten, sodass nichts mehr produziert wird ... alternativ ein Spiel, wo du den Spieler 1 kontrollierst ... eigentlich musst du gar keine AIV/AIC haben ... im besten Fall schreibst du dir deine eigene AIV/AIC live oder du lernst, was am besten funktioniert, in dem du Notizzettel machst, in dem du als Spieler gegen eine echte KI im Spiel antrittst." -> **Vorschlag zur Umsetzung:** unsere KI spielt auf dem Menschenplatz (ohne AIV/AIC, nur Befehle), Gegner ist eine echte KI; wo deren Reaktionen eine Messung verfaelschen, ihre Produktion gezielt stilllegen. Das aendert die Grundbedingung vom 30.09. (zwei Selfaware-KIs auf Platz 1) - Daniels Entscheidung.

**Offen:** Lord-Wacht und `halten` halten beide Ziele fest (zwei Wege zum selben Ziel) - zusammenlegen. Bewegungsbeginn erst 50 Ticks nach dem Laden. Ausweichen/Hit-and-run: an die Feldgrenzen-Regel gebunden (ein Richtungswechsel je Feld).

## Grundbedingung geaendert (Daniel, 04.10.2026, 19:45): unsere KI spielt auf dem MENSCHENPLATZ
"ja gerne. dann bauen und anwerben lernen" - ohne AIV/AIC, nur ueber unsere Befehle, gegen eine echte KI (Ziel: gegen das Rotkaeppchen gewinnen). Daniels Tipps stehen in `Spielwissen.md` (Notizzettel der KI).

## M11 Bauen / M12 Anwerben (04.10.2026, 19:45-19:55)

Werkzeug `werkzeug/bauen.py` (Bausteine `baue_irgendwo`, `werbe`, `vorrat`, `kosten` + Probe). Modulbefehle `baue`, `werbe`, `vorrat`, `eigenerPlatz`. Dekompilate `daten/dekomp_bauen_anwerben.c`, `dekomp_anwerben_click.c`, `dekomp_queuecommand.c`; Bau-Nummern `daten/enum_mapper.txt`.

- **Weg (abgelesen):** wie ein Klick des Menschen - Parameter nach `GameCommandParam0..5` (GameSynchronyState + 0x7A850, je 4 Byte), dann `queueCommand` (0x00489100). Bauen = Befehl 28 (`ClickPlaceBuilding`: x, y, Bau-Nummer, Groesse, Drehung, Trupp), Anwerben = Befehl 31 (`ClickRecruitUnit` -> `ProcessRecruitUnit(Spieler, Typ, Gebaeude)`). Das Spiel prueft Platz und Kosten selbst - nichts geschummelt.
- **Die Falle (gemessen):** Nach unserem eigenen Gefecht steht "eigener Spieler" (`currentPlayerSlotID`, GameSynchronyState + 0x109E74) auf **0** - jeder Bau-/Anwerbebefehl lief still fuer den neutralen Spieler 0. Mit `{"eigenerPlatz": 1}` laeuft er als Spieler 1. Nach jedem Laden/Start setzen.
- **M11 Bauen gilt:** 5 Holzfaellerhuetten -> Holz 150 -> 125 (genau 5 x 5 laut Kostentabelle); Huetten sofort mit Holzfaellern besetzt (5 Bauern wurden Typ 3). Eingang = (x+1, y+3). Gegenlauf: auf belegtem Platz (Lager) nichts gebaut, nichts abgezogen.
- **M12 Anwerben gilt:** Soeldnerposten (120 Gold) gebaut, 1 arabischer Bogenschuetze (Typ 70) angeworben (0 -> 1). Genauer Einheitenpreis noch aus der Balance nachzulesen (Gold sank in 50 Ticks um 48, Steuern liefen mit).
- Probe wiederholbar: `python werkzeug/bauen.py "M7-04 Mensch Grumpy T600"` - alle Urteile GILT (daten/bauen_probe.txt).
- **Offen / naechste Schritte:** Kaserne (12 Stein) + Waffen fuer europaeische Truppen; Plaetze finden statt probieren (freie Flaeche, Baeume neben Holzfaeller, Steinbruch/Ochsen, Wild fuer Jaeger); Gold-Buch (Einnahmen/Ausgaben je Tick); Steuern/Rationen/Verkaufen steuern; dann der erste eigene Spielplan gegen das Rotkaeppchen.

**Spielregeln fuer unsere KI (Daniel, 04.10.2026, 19:56):** keine kostenlosen Mauern (alles kostet wie beim Menschen); Kaufen/Verkaufen in beliebiger Menge auf einmal erlaubt (Menschen: mindestens 5). Stehen ausfuehrlich in `Spielwissen.md`.

## M13 Freie Bauplaetze finden (begonnen 04.10.2026, 19:58) - Stand: Pruefung noch NICHT verlaesslich

- Daniel: "ja gerne. bitte kornspeicher nicht vergessen. beliebtheit ist das wichtigste, wenn deine beliebtheit unter 95 faellt reduziert sich deine bauernspawnrate bis sie bei 50 fast steht und unter 50 leute AUS deinem dorf gehen" (in `Spielwissen.md` uebernommen).
- **Beliebtheit** steht bei PlayerData + 0x60 in Hundertsteln (abgelesen + plausibel: Mensch in M7-04 9325 = 93,25 - also schon unter 95; Rotkaeppchen 98,25). Gegen die Anzeige im Spiel noch nicht verglichen.
- **Platzpruefung des Spiels** gefunden: `checkBuildingCanBePlacedHere` (0x005037B0, thiscall TileMapState, Spieler, x, y, Bau-Nummer, Groesse) -> `buildingPlacementFail` (0x01FE7B3C), Grund (0x01FE7B40). Modulbefehle `platz` (eine Stelle) und `platzsuche` (ringweise, naechste freie Stellen) - bauen nichts, kosten nichts.
- **Gegenprobe NICHT bestanden (19:59):** Die Pruefung meldet (178,112) als frei - dort hat das Spiel um 19:51 als Spieler 1 nicht gebaut; und sie meldet Stellen direkt am Lager (172,111), (174,109) als frei fuer einen Kornspeicher. Der Grund bleibt bei jeder Abfrage 22 (vermutlich ein Rest). Ich lese das Ergebnis falsch/unvollstaendig, oder `placeBuilding` prueft mehr bzw. rechnet x/y anders (Mitte statt Ecke). **Nicht verwenden, bis die Gegenprobe gilt.** Naechster Schritt: `placeBuilding` (0x005162D0) lesen - wie entscheidet es selbst?

**M13 Update (20:00-20:04): Platzpruefung GILT.** Zwei Fehler behoben: (1) wie `placeBuilding` vorher die Bau-Drehung setzen (TileMapState+0x5549B4 = 0) - ohne sie pruefte das Spiel einen anderen Grundriss; (2) mein Testaufbau: alle Stellen vorab geprueft, dann der Reihe nach gebaut - eine frisch gebaute Huette blockierte die naechste Stelle (der eine "Widerspruch"). Gegenprobe mit Pruefung direkt vor jedem Bauversuch: **12 von 12 Stellen stimmen** (Pruefung "geht" = Spiel baut, "nicht" = baut nicht und zieht nichts ab), darunter knappe Stellen am Lager und an der eben gebauten Huette (`daten/platzpruefung_gegenprobe.txt`). Damit sind `platz` und `platzsuche` benutzbar. Drehung bleibt immer 0 (Gebaeude lassen sich nicht drehen - Daniel).
Naechste Schritte M13: Plaetze nach Daniels Regeln waehlen - nah am Lager; Holzfaeller-Eingang neben einem Baum; Ochsen neben den Steinbruch; Jaeger nur bei Wild (Rehe = Typ 44); Kornspeicher; dazu Beliebtheit (+0x60) immer im Blick.

### M13a Beliebtheit ueber 95 (Daniel 20:05: "ja gerne, beliebtheit zuerst ueber 95") - Messung der Ursache
Beliebtheits-Teilwerte im Spielerdatensatz (PlayerData + Offset): Bier +0x2110, Religion +0x2114, Angst +0x2118, Steuer +0x215C, Essen +0x2160, Enge +0x2164, Jahrmarkt +0x222C; Steuerstufe +0x2188, Rationen +0x218C, Vorrat-Stufe +0x2190; Bevoelkerung +0x2180.
Gemessen in `M7-04 Mensch Grumpy T600`: **Mensch (Spieler 1) Beliebtheit 93,25 - Essen -250, Steuer +25, sonst 0, Rationen 2, Kornspeicher leer.** Rotkaeppchen (Spieler 2): 98,25 - Essen +250, Steuer +25, Rationen 4. -> **Der einzige Grund ist das fehlende Essen.**
Plan: (1) Essen in den Kornspeicher - am schnellsten kaufen (Marktplatz + Handelsbefehl, Daniel erlaubt beliebige Mengen), parallel Apfelplantage nah am Lager (platzsuche); (2) falls noetig Steuern senken/Bestechung als Bruecke (3930 Gold); (3) spaeter Bier. Gegenprobe: Essenswert wird positiv, Beliebtheit steigt ueber 95 und bleibt.
- **20:08:** Allgemeiner Modulbefehl `spielbefehl` (Nr + Werte). Befehlsnummern aus der Handler-Tabelle (0x00B38E10 + 4*Nr): 34 Steuern, 35 Rationen, 38 Kaufen/Verkaufen (`daten/dekomp_handel_steuer.c`). Marktplatz an gepruefter Stelle (172,111) gebaut (Kostentabelle meldet 0 - nachpruefen). **Apfelkauf mit Werten (13,0) und (13,1): keine Wirkung** - Deutung der Werte falsch; naechster Schritt `ProcessBuyOrSell` lesen.
- **Spaeterer Test (Daniel 20:09):** Bauern-Zuzugsrate je Beliebtheit - schaltet sie stufenweise? Dafuer auf dem Pruefstand die Beliebtheit ueber einen ganzen Zuzugs-Zyklus festhalten, Stufe fuer Stufe.
- **20:10 - M13a GILT: Beliebtheit ueber 95.** `ProcessBuyOrSell(Spieler, kaufen=0/verkaufen=1, Ware)` - ein Kauf = 5 Stueck, nur mit Gold UND freiem Lager (fuer Essen: Kornspeicher!). Der Mensch hatte **keinen Kornspeicher** - gebaut an gepruefter Stelle (169,116), 5 Holz. 10 Kaeufe Aepfel (`spielbefehl` 38 [0,13]): Gold 3934 -> 3535 (~8 Gold je Apfel), Aepfel -> 65. Verlauf (Tempo 1000): Beliebtheit 93,25 -> 93,50 (300 Ticks) -> **95,25 (600)** -> 96,75 -> 99,75 -> **100,00 (1500) und bleibt**; Essenswert -250 -> 0 -> +125. Mitschrift `daten/beliebtheit_95.txt`. Gegenprobe vorher festgelegt (Essenswert positiv, Beliebtheit > 95 und bleibt) - bestanden.

### M13b Gruenland messen, Farmen rechnen (Daniel 20:13: "finde erstmal heraus wo gruenflaeche ist und wie man farmland messen kann ... wie viele farmen kannst du maximal bauen und optimal platzoptimiert bauen moeglichst nahe am bergfried/kornspeicher") - Apfel GILT (21:22)
- **Farmland-Regel (abgelesen 20:15, `daten/dekomp_platzpruefung.c`):** je Feld des Grundrisses: `LogicLayer` & 0x30 = blockiert; ist `LogicLayer` & 0x100000 NICHT gesetzt, zaehlt `Logic2Layer` (Byte): 0x10 Gras und 0x80 dichtes Gestruepp = Gruenland + fruchtbar, 0x01 Gestruepp = nur fruchtbar. Farmen (Weizen, Hopfen, Apfel, Kuehe) gehen nur, wenn **jedes** Feld fruchtbar ist (sonst Grund 22) **und** mindestens 50 Felder Gruenland sind (sonst Grund 23). Die Platzpruefung (`platz`/`platzsuche` mit Bau-Nummer der Farm) prueft das also schon mit. Naechster Schritt: Gruenland-Karte als Datei -> rechnen, wie viele Farmen maximal und wo am naechsten an Kornspeicher/Bergfried.
- **20:15 Gruenland-Karte:** Modulbefehl `gruenland` schreibt eine Textkarte (G Gruenland, s Gestruepp, # blockiert, x unfruchtbar). Um den Bergfried (130,70)-(230,170): 1913 G, 2585 s; das zusammenhaengende Gruenland liegt als Band oestlich (etwa x 186-220, y 105-122). Datei `daten/gruenland_M7-04_130-70_230-170.txt`. (Erste Fassung hatte einen Syntaxfehler durch echte Zeilenumbrueche in Lua-Zeichenketten - sofort behoben.)
- **20:21 Platzkarte statt Einzelfragen:** Modulbefehl `platzkarte` fragt die Spielpruefung fuer JEDE Stelle eines Rechtecks und schreibt `+` (geht) bzw. den Grund. Ganze Karte (400 x 400 = 160.000 Stellen) in unter 1 s (gemessen 20:46, `bauen.platzkarte()` wartet auf die Fertig-Zeile). Wiederholung im selben Ausschnitt: 658 = 658 Stellen, deckungsgleich. Dateien `daten/platzkarte_apfel_M7-04_{basis,gross,ganz}.txt`.
- **Grundriss abgelesen:** Die Stelle ist die obere linke Ecke, die Farm reicht 10 Felder nach rechts und unten: nur dieser Versatz (0,0) passt zur Farmland-Regel (0 Stellen, die das Spiel erlaubt und die Regel verbietet; alle anderen Versaetze 40+ Abweichungen). Zusaetzlich sperrt das Spiel (81 Stellen): **Baeume** (LogicLayer 0x3000 + Baum im OrganismLayer), Hoehe/Hang, Gebaeude, Wasser/Fluss und **jede stehende Einheit ausser Huehnern** (`daten/dekomp_feld_bauerlaubnis.c`, isBuildingPlacementAllowedAtTile 0x004F9A60). Achtung: der Grund-Speicher (0x01FE7B40) wird bei diesen Sperren NICHT neu gesetzt - er zeigt dann einen alten Wert.
- **20:33 Einheit auf dem Feld (Daniels Frage, ob der Feldteil ueber Einheiten geht):** Speertraeger steht auf (207,116) mitten in der Flaeche von (203,112) -> Pruefung "geht nicht" UND echter Bau: keine Farm (`daten/farm_ueber_einheit.txt`). Daniel bestaetigt im Spiel (20:44): geht in dieser Fassung nicht, nur in der Definitive Edition. Gegenprobe ohne Einheit: dieselbe Stelle wird im Lauf 21:20 gebaut.
- **Hoechstzahl - bewiesen fuer diese Karte und Regel** (`werkzeug/farmen_packen.py`: Suche mit Schranke; Schranke = Gitter mit Maschenweite 10, jede Farm trifft genau einen Gitterpunkt; erst hoechste Anzahl, dann kuerzester Weg). Um die Kornspeicher-Mitte (170,5/117,5), Umkreis = Schachbrett-Abstand der Farm-Mitte (`daten/apfelfarmen_packung_tabelle.txt`):
  bis 30 Felder: **0** (das naechste Gruenland liegt 36,7 Felder weg) | 35: 3 | 40: 6 | 45: 7 | 50: 10 | 60: 21 | 70: 25 | 80: 27. Die gierige Wahl (immer die naechste) liegt 1-3 darunter.
  Gerechnet ueber die Platzkarte EINES Zeitpunkts: wo gerade eine Einheit stand, fehlt die Stelle; Holzfaeller koennen spaeter Baeume wegnehmen.
- **21:20 Bau-Probe GILT:** die berechneten 9 Stellen (Umkreis 45 um die Ecke (169,116)) - darunter 5 Paare, die sich lueckenlos beruehren - **alle 9 im ersten Versuch gebaut**. Holz 145 -> 118 (9 x 3), Gold 3932 -> 3809 (Soll 9 x 15 = 135; die 12 Gold Unterschied fallen in die 45 Ticks des Bauens - vermutlich Steuern, nicht nachgeprueft). Farmen brauchen also KEINEN Abstand.
- **21:20 Aepfel kommen an** (`werkzeug/plantagen_lauf.py`, nichts zugekauft, `daten/apfel_lauf_9_gepackt.txt`): 9 Apfelbauern sofort besetzt (10 freie Leute -> 1). Aepfel im Kornspeicher 14 (Startgut) -> erste Ernte bei ~Tick 2.655 (gut 2.000 Ticks nach dem Bau) -> 50 (3.255) -> 94 (5.255) -> 93 (6.655), gleichzeitig wird gegessen. Beliebtheit 93,25 -> 95,25 (Tick 1.255) -> **100,00 ab Tick 2.055 bis zum Ende (6.655)**, Essenswert -250 -> +125. Stand gesichert: `M13b 9 Apfel 100 Grumpy T6655`.
- **FEHLER GEFUNDEN 21:02-21:20 (Daniels Fehlerkontrolle: laeuft das Spiel? sind die Bedingungen gegeben? laeuft genau dieser Test?):** Ein geladener Spielstand traegt den Menschen NICHT in `currentPlayerFullIDArray` (0x0191DE10, alles -1) ein. Platz 1 gilt dann weder als Mensch noch als KI; `checkSkirmishGameDefeat` sieht nur Rotkaeppchens Mannschaft und beendet das Spiel im ersten Takt (gameOver 0x0117D500 = 1). Nachgestellt 3 von 3 Mal (gameOver 0 nach dem Laden, 1 nach 5 Ticks), beide Lords leben, "getoetet von" = 0. **Behoben:** `eigenerPlatz` traegt jetzt auch den Menschen ein (fullID = 1, wie unser eigener Gefechtsstart) -> 2.020 Ticks ohne Spielende. **Folge fuer fruehere Laeufe:** M11, M12, M13, M13a und der gierige Farm-Lauf liefen in einem Spiel, das intern schon als beendet galt (gesichert `M13b 9 Apfelfarmen gierig` hat gameOver 1 - NICHT mehr verwenden). Die Zeit lief dort weiter; der Beliebtheitsverlauf aus M13a stimmt mit dem sauberen Lauf 21:20 ueberein (+600 Ticks -> 95,25, +1.400 -> 100), weitere Abweichungen nicht geprueft. Ab jetzt: `laufe()` bricht laut ab, wenn die Spielzeit steht (mit Ansicht/gameOver im Text), und `plantagen_lauf.py` prueft vorab Ansicht 14, gameOver 0, Mensch eingetragen (Negativlauf: ohne `eigenerPlatz` -> Abbruch "TESTBEDINGUNG FEHLT").
- Neuer Grundstand: `M13b Basis Speicher Grumpy T610` (Kornspeicher (169,116), Markt (172,111)); nach dem Laden IMMER `eigenerPlatz` schicken.
- **Naechste Schritte (Daniel 20:51):** Rechnung so leicht und schnell wie moeglich, fuer alle Farmarten (Weizen 9, Hopfen 9, Apfel 10, Kuehe 10) und Mischungen, fuer jede Karte. Vorschlag: Loeser OR-Tools (CP-SAT) - wartet auf Daniels Ja zum Herunterladen. Ausserdem: Kornspeicher naeher ans Gruenland (Daniels Tipp) - die Rechnung zeigt, dass bis 30 Felder um den jetzigen Speicher gar keine Farm passt.

### M13c Mischrechnung fuer alle Farmarten, jede Karte (Daniel 20:51: "so leicht ... so schnell wie moeglich, auch fuer andere Plantagenarten und Mixturen ... egal welche Karte man hat, damit das optimalst ist") - GILT (21:55)
- Daniels Ja zu OR-Tools 21:31; installiert ortools 9.15 (PyPI). Werkzeug `werkzeug/farmen_mischen.py` (CP-SAT): je Feld hoechstens eine Farm; Stufe 1 hoechster Gesamtwert (Wert je Sorte, Mindest-/Hoechstmengen), Stufe 2 bei diesem Wert kuerzester Weg - je Sorte zu ihrem Abgabeort (Aepfel/Kuehe -> Kornspeicher (170,5/117,5), Weizen/Hopfen -> Lager (171,5/108,5)). Eingabe: die vier Platzkarten (ganze Karte, je < 1 s).
- **Regel fuer 9x9 nachgeprueft:** Bau-Stelle oben links und 50-Gras-Regel gelten auch fuer Weizen/Hopfen (0 Stellen, die das Spiel erlaubt und das Modell verbietet). Weizen = Hopfen: 3.527 Stellen; Apfel = Kuehe: 2.845 (ganze Karte, Grundstand).
- **Gegenprobe zweier unabhaengiger Rechenwege:** nur Aepfel, Umkreis 45/50/60/70/80 -> CP-SAT und `farmen_packen.py` liefern 5 von 5 Mal dieselbe Anzahl UND denselben Gesamtweg; CP-SAT je <= 0,4 s (`daten/mischen_gegenprobe_apfel.txt`).
- **Ergebnisse Umkreis 50 um den Kornspeicher** (`daten/mischen_szenarien.txt`, alle OPTIMAL = fuer diese Platzkarten nachweislich nichts Besseres):
  nur Aepfel 10 | Sorte egal, moeglichst viele 14 (9er-Farmen passen in mehr Luecken) | Aepfel zuerst, Luecken mit Hopfen (Wert 0,6): 10 Aepfel + 3 Hopfen | genau 3 Hopfen + 2 Kuehe + Rest Aepfel: 8 + 3 + 2. Zeiten 0,2-0,8 s.
- **Tempo ganze Karte:** 12.744 moegliche Stellen, alle vier Sorten -> 85 Farmen, OPTIMAL in 2,7 s.
- **21:45 Bau-Probe Mischung GILT** (`plantagen_lauf.py --plan daten/mischung_apfel_hopfen_r50.json`): 13 von 13 im ersten Versuch, 9er- und 10er-Farmen lueckenlos nebeneinander. Holz 145 -> 85 (Soll 10x3 + 3x10 = 60, genau). Gold 3932 -> 3694 (Soll 255; 17 Unterschied in den Bau-Ticks - vermutlich Steuern, nicht nachgeprueft).
- **Ertrag** (`daten/mischung_apfel_hopfen_lauf.txt`): 10 Apfel- + 3 Hopfenbauern sofort besetzt (dann 0 freie Leute). Aepfel 15 -> 53 (Tick 3.275) -> 226 (Tick 12.675), Beliebtheit 100 ab Tick 1.875. **Hopfen kommt viel spaeter:** erster Hopfen zwischen Tick 7.675 und 8.675 (gut 7.000 Ticks nach dem Bau), dann 16 bis Tick 12.675. Gesichert: `M13c Apfel Hopfen Grumpy T12675`.
- Offen: Huetten-Lage je Farm (Daniels Bild: obere Ecke) fuer den Weg statt der Farm-Mitte; Wege ueber Gelaende statt Luftlinie; Kornspeicher-/Lager-Platz mitrechnen (Daniels Tipp: Speicher naeher ans Gruenland).

### M13d Kornspeicher, Lager, Haeuser, Abreissen, Holzfaeller - Grundlagen fuer das erste Spiel (Daniel 21:54, 21:58, 22:04)
Auftraege (21:54), gezaehlt: 1 Kornspeicher und Lager mitrechnen, 2 erstes Spiel (Nahrung, Holz, dann Stein, dann Eisen), 3 Haeuser automatisch, 4 Soeldnerlager + Assassinen ohne Verlust, 5 Echtzeit ab Tempo 40. Dazu Daniels Lager-Regel (Spielwissen): erst 150 Holz verbauen, dann leeres Lager abreissen und nah ans Holz setzen, spaeter zu Stein/Eisen.
- **Kornspeicher/Lager (gemessen 21:58, `daten/speicher_lager_haus_regeln.txt`):** ohne Kornspeicher 50.378 erlaubte Plaetze, mit einem nur 12 (anliegend). Lager: 16 Plaetze (nur anliegend), Lagerteile kosten 0. Ohne Lager (alles abgerissen) 47.019 Plaetze; ein neues Lager kommt als 4er-Block.
- **Haus:** Huette 5 Holz, Wohnplaetze 10 -> 18 (PlayerData +116 populationCap; Bevoelkerung +8576, am Feuer +136, untaetig +11116; `daten/struktur_PlayerData.txt`). 450 Ticks spaeter 18 Leute.
- **Abreissen = Spielbefehl 29** (`ClickDestroyBuilding`: Nummer, Rueckgabe-Prozent, uid; `daten/dekomp_abreissen.c`, `befehlstabelle.txt` mit allen 128 Befehlsnummern). Das Spiel prueft den Besitzer nicht -> Modulbefehl `abreissen` laesst nur eigene Gebaeude zu (Negativlauf: Rotkaeppchens Lager abgelehnt, steht weiter). Rueckgabe 0 % (den Wert des Mensch-Klicks nicht gefunden).
- **Lager-Umzug (gemessen 22:01, `daten/lager_verlegen_probe.txt`):** Abreissen vernichtet den Inhalt (150 Holz -> 0). Holz verkaufen 1 Gold/Stueck, kaufen 3 Gold/Stueck; Verkaufen-Abreissen-Zurueckkaufen kostete 88 Gold + 70 Holz -> Daniels Weg (erst verbauen) ist besser.
- **Rohstoffkarte:** Modulbefehl `rohstoffkarte` (Steine b, Eisen i, Pech o, Gebaeude B, Gruenland; Baumliste aus LandscapeState 0x00F2CC38, Baum 156 Byte: Art +70, Zustand +68, x +98, y +100). Grumpy Start: 1.102 Baeume, 2.861 Stein-, 2.489 Eisen-, 48 Pechfelder. **Im Umkreis 30 um den Bergfried kein einziger Baum**; Haine westlich (x 122-140) und oestlich (x 203-207), 37-46 Felder weit.
- **Holzfaeller (gemessen 22:10-22:20, `daten/holzfaeller_probe.txt`):** Huette (129,91), Groesse 3. Ueblicher Eingang waere (x+1, y+3) wie bei Kornspeicher/Markt/Bergfried (x + Groesse/2, y + Groesse); dort steht ein Baum -> Eingang rutschte auf (129,94), direkt neben den Baum (Daniels Regel bestaetigt). Kreislauf: hacken am Eingang, dann **18 Holz je Gang** zum Lager am Bergfried: Hinweg ~1.250 Ticks, Rueckweg ~1.000 (rund 26 Ticks je Feld), Hacken ~2.000-3.000 Ticks. **Mehr als die Haelfte der Zeit ist Weg** - ein Lager am Hain bringt fast doppelt so viel Holz.
- Offen: welche Baumarten fallbar sind und woran man einen angehackten Baum erkennt (in 7.000 Ticks verschwand keiner nahe der Huette). Arbeitsannahme (VERMUTET): nur die grossen Arten 1-4 (die den Bau sperren); 5-19 sind Strauecher.

## M14 Erstes Spiel: Holz und Nahrung, dann Stein, dann Eisen (Daniel 21:54) - laeuft
- **Lager-Hoechstmenge (gemessen 22:20, `daten/lager_hoechstmenge.txt`):** 4 Lagerteile fassen 190 Holz (~48 je Teil, Daniel: 48); alle Teile mit Holz belegt -> kein Stein mehr kaufbar; ein angebautes Lager ist wieder ein 4er-Block (+190 Holz).
- **Baum-Holzmenge (gemessen 22:15, `daten/baum_holzmenge_probe.txt`):** Baum +120 zaehlt beim Hacken 3 -> 2 -> 1 herunter, bei 0 verschwindet der Baum. Start: Arten 1-4 ausgewachsen 9 (jung 1-4), Arten 5-19 immer 0 = nicht faellbar. 3 Einheiten je Gang = 18 Holz -> ~54 Holz je grossem Baum (abgeleitet).
- **Eroeffnungsplaner `werkzeug/eroeffnung.py`:** Lager + Holzfaeller nach Holz, das in 20.000 Ticks ankommt (eigene Baeume je Huette, Weg gemessen), Lager hoechstens 45 Felder vom Bergfried; dann Kornspeicher + Apfelplantagen (OR-Tools, abwechselnd), Steinbruch am naechsten Stein mit Ochsenjoch daneben, Huetten am Bergfried. Rechenzeit 71 s (gierig, nicht bewiesen).
- **Vergleich altes/neues Lager (`daten/eroeffnung_vergleich.txt`):** 6 Huetten 495 -> 703 Holz (+42 %), 10 Huetten 783 -> 1.076 (+37 %), 14 Huetten 1.053 -> 1.368 (+30 %) in 20.000 Ticks.
- **Plan (`daten/eroeffnung_plan.json`), 150 Holz genau verbaut:** 14 Holzfaeller (70), Kornspeicher (106,151) (5), 10 Apfelplantagen (30 Holz, 150 Gold), Steinbruch (93,130) + Ochsenjoch (100,137) (30), 3 Huetten (15); dann altes Lager abreissen, neues bei (122,152). Eisen liegt 5 Felder neben dem neuen Lager, Stein 36.
- Daniels Gedanken fuer spaeter (22:23, 22:26): Gewichte (Holzmenge gegen Weg, Naehe zum Gegner, Sicherheit) durch selbstlernendes Spielen belohnen und einstellen; Lager genau in dem Tick versetzen, in dem ein Holzfaeller abliefern will (Arbeiterzustand 8 = traegt zum Lager).
- **22:30-22:41 Erstes Spiel (`werkzeug/erstes_spiel.py`, Protokoll `daten/erstes_spiel_log.txt`):** Phase 1 (Spiel steht): 30 von 30 Bauten im ersten Versuch, 150 Holz -> 0; altes Lager (leer) abgerissen, neues 4er-Block bei (122,152) (im Spiel-Log belegt). Gesichert `M14 Eroeffnung Grumpy T756`. Phase 2 Echtzeit Tempo 40: Tick 849 14/34 Leute; Tick 2.447 alle 34 Plaetze voll, 14 Holzfaeller + 10 Apfelbauern arbeiten, Beliebtheit 100; erstes Holz ab ~Tick 5.000; Tick 7.240 Lager automatisch angebaut (Holz 144 + Stein 12); Tick 11.417 zweiter Anbau; Ende Tick 14.719: 390 Holz, 36 Stein.
- **Was schiefging:** Rotkaeppchens Speertraeger rissen den Kornspeicher ab (Daniel 22:38) - Aepfel/Brot 0, Beliebtheit 100 -> 46, 2 Holzfaeller + 3 Apfelbauern weniger. Wir haben 8 Speertraeger + 6 Bogenschuetzen, aber keine Abwehr und kein Lagebild. Ein Holzfaeller lief an vier Baeumen der Stufe 4 vorbei (findTree nimmt nur Stufe < 4) - Planer korrigiert.
- **Lagebild (Modulbefehl `lagebild`, `daten/lagebild_T14719.txt`):** 407 Einheiten; Rotkaeppchen 39 Speertraeger, 32 Bogenschuetzen, 6 Assassinen. KI-Angriffe stehen NICHT in den Befehlsfeldern (+924/+926/+928 = 0), sondern im Laufziel (+0xC8/+0xCA): die zwei Angreifer liefen auf (101,123)/(100,122) - 2-3 Felder neben unsere Apfelplantage (101,120). Zustaende: 101 = laeuft zum Ziel, 106 = Nahkampf (`daten/enum_einheitenzustaende.txt`).
- **Fuer Auftrag 4 gelesen:** Truppenbefehle wie der Mensch: Befehl 16 Auswahl (Auswahl-Bits UnitsState 0x01387F38 +116, Bit je Einheit; Param0 = Gruppennummer, die createPlayerTribe direkt so anlegt), dann Befehl 36 (Gruppe, Art 4 Einheit angreifen / 9 Gebaeude angreifen / 31 Halt, Ziel-Nr, Ziel-uid). Assassine = Einheitentyp 73.
- **Daniels Punkte (22:38-22:39):** alle Einheiten verfolgen, besonders Angriffe auf uns; Lager vorausschauend anbauen (Lieferungen aller Traeger vorhersagen, nicht erst bei vollem Lager); Essen verkaufen kann mehr Gold bringen als Steuern (nachrechnen).

## M15 Waechter: Angriffe erkennen und abwehren (Daniel 22:42: "erst waechter dann assassinen")
- **Modulbefehl `angriff` (22:44):** eigene Einheiten auswaehlen wie der Mensch (Auswahl-Bits + Spielbefehl 16 mit freier Gruppennummer), dann Spielbefehl 36 (Art 4 Einheit / 9 Gebaeude / 31 Halt). Nur eigene Einheiten (Fairness).
- **Probe GILT (22:45-22:47, `daten/angriff_probe.txt`), Kriterium vorher festgelegt:** 8 Speertraeger (am Bergfried) gegen den verletzten Angreifer 290 in unserer Wirtschaft: sofort Zielart 4, Zustand 101 (laufen), Abstand 83 -> 13 Felder in 700 Ticks; Kampf ab Tick 15.540, beide Angreifer (282, 290) tot bis Tick 15.720, **keiner von uns verloren** (schwaechster 10.225 / 12.500). Der zweite Angreifer wurde von selbst mit angegriffen.
- **Waechter `werkzeug/waechter.py`:** Bedrohung = feindliche Truppe mit Laufziel <= 6 oder Standort <= 8 Felder an einem unserer Gebaeude; je Bedrohung 2 naechste freie Nahkaempfer + alle Fernkaempfer im Umkreis 25; Lord (Daniel 22:43) nur ueber 60 % Leben, unter 50 % zurueck zum Bergfried; zu Beginn alle Truppen zum Posten an der Lagermitte. Trockenprobe ohne Spiel: Erkennung am Laufziel und Befehlsfolge richtig.
- **22:48-22:53 Waechter Fassung 1 (gleiche Partie ab `M14 Eroeffnung Grumpy T756`, Tempo 40, `daten/waechter_spiel1_konsole.txt`) - Kriterium (vorher): Kornspeicher steht, Beliebtheit > 90 bei ~Tick 14.700.** Gestoppt bei Tick 12.636 (fuer Fassung 2): Kornspeicher steht, 14 Holzfaeller + 10 Apfelplantagen stehen, Aepfel 157, Beliebtheit 100 (ohne Waechter bei Tick 13.190: Kornspeicher weg, Aepfel 0, Beliebtheit 55). Erkannt 6 Angreifer, 2 getoetet, 1 eigener Speertraeger verloren. Die Angreifer wurden schon im feindlichen Lager am Laufziel erkannt (Tick 6.707: drei Speertraeger bei (200,275), Laufziel (107,170) = unsere Apfelplantage). Schwaechen: eine Runde dauerte ~20 s (~800 Ticks) und die Verteidiger wurden zu je 2 aufgeteilt - Daniel 22:52: "perfektes Stacken ist unglaublich wichtig".
- **Fassung 2:** Modulbefehl `status` (alles in einer Zeile) + Gebaeudeliste im `lagebild` -> eine Runde = ein Aufruf. Waechter buendelt ALLE Verteidiger auf EIN Ziel und faengt weit entfernte Angreifer gebuendelt an ihrem Laufziel ab (Trockenprobe gut).
- **22:55-23:00 Tempo (Daniel 22:55: Tests mit Hoechstgeschwindigkeit):** `befehl.sende(..., bis=...)` wartet nur bis zur Antwortzeile statt fest -> eine Lenker-Runde 1,1 s -> 0,04 s (gemessen, 10 Runden). Erster Lauf mit Tempo 1000 SCHEITERTE: das alte Bauwerkzeug (feste Wartezeit + Warten auf einen genauen Tick) blockierte beim Lager-Anbau die Schleife ~20.000 Ticks, der Waechter erkannte 0 Bedrohungen, Kornspeicher und 9 Apfelplantagen fielen (`daten/waechter_spiel3_konsole.txt`). Behoben: Bauen im laufenden Spiel blockiert nicht mehr (`baue_schnell`), `laufe()` wartet auf >= statt ==, Runden ueber 400 Ticks werden als WARNUNG geschrieben.
- **23:00 Waechter Fassung 2 GILT (Tempo 1000 bis Tick 20.024, 866 Runden, `daten/waechter_spiel4_konsole.txt`):** Kornspeicher, 14 Holzfaeller, 10 Apfelplantagen stehen, Beliebtheit durchgehend 100, 248 Aepfel, 828 Holz; keine WARNUNG; 32 Angreifer erkannt, 17 getoetet, gebuendelt und am Laufziel abgefangen. Preis: 8 eigene Verluste (alle 8 Speertraeger). Gesichert `M15 Waechter Grumpy T20024`.

## M16 Angriff mit Assassinen (Auftrag 4) - erster Versuch GESCHEITERT (23:01-23:03)
- Kriterium vorher: kein Assassine stirbt UND mindestens ein feindliches Gebaeude faellt. Ab `M15 Waechter Grumpy T20024`, Waechter an, Soeldnerlager + 6 Assassinen, Tempo 1000 (`daten/angriff_spiel1_konsole.txt`).
- Ablauf: Soeldnerlager erst nach ~1.400 Ticks gesetzt (Platzsuche Umkreis 12 fand lange nichts), bei (137,143); 6 Assassinen geworben (Gold 3850 -> 3380, ~58 je Stueck inkl. Lager 120 - nicht einzeln nachgeprueft). 1 feindliche Apfelplantage zerstoert. Verletzte gingen allein "heim" - heim war unser Lager, wo Rotkaeppchens Hauptheer angriff: **alle 6 Assassinen tot**. Lord zog sich bei 49 % zum Bergfried zurueck und fiel dort -> **Spiel bei Tick 29.820 verloren**. Rotkaeppchen am Ende: 46 Bogenschuetzen, 24 Speertraeger, 6 Assassinen.
- Gelernt: (1) Rueckzugsort darf nicht fest sein - er muss dort liegen, wo gerade KEIN Feind ist; Verletzte nie allein durch Gefahr schicken. (2) Ab ~Tick 25.000 kommt Rotkaeppchens Hauptheer; mit 14 Starttruppen und ohne Mauern/Tuerme/Nachschub ist der Lord nicht zu halten - Gold (3.380) und Holz (1.100+) lagen ungenutzt. (3) Der Lord gehoert weg von jedem Kampf, sobald das Hauptheer kommt (sein Tod = Niederlage).
- **23:06 Preise (gemessen, `daten/preise_probe.txt`):** Soeldnerlager 120 Gold; Assassine 70, arab. Bogenschuetze 60, arab. Schwertkaempfer 100 Gold, je 1 Mensch vom Feuer. Verkauf: 50 Aepfel = 150 Gold (3/Stueck), 50 Holz = 50 (1/Stueck), 10 Stein = 50 (5/Stueck) - warum ein Verkauf mal 50, mal 10 Stueck nimmt, ist offen.
- **Daniel 23:06:** Nahrung und Rohstoffe bis auf ein Minimum verkaufen, alles in Assassinen, die raiden - so schnell wie moeglich. Eingebaut: Verkauf ueber Reserven (Essen 60, Holz 15), laufendes Anwerben, Huetten fuer Nachschub, Lord geht beim Hauptheer (>= 8 Feinde nah) an den sichersten Ort; Eroeffnung baut alle 30 Bauten in EINEM Aufruf (30 von 30, Gold genau -150).
- **Partie 2 (23:07-23:12, Tempo 1000, `daten/partie2_konsole.txt`):** 90 Assassinen geworben, EIN grosser Trupp: 11 Gebaeude zerstoert (5 Holzfaeller, 6 Apfelplantagen), **76 Assassinen verloren**. Die Ziele 5-28 Felder weit gingen gut; die Verluste begannen nach Zielen 90-212 Felder tief im Feindgebiet und beim Rueckzug quer durchs Feindheer zum "sichersten" Ort am anderen Kartenende. Eigene Wirtschaft unversehrt, Beliebtheit 100, kein Angriff auf uns.
- **Daniel 23:13/23:14:** aufteilen und moeglichst viele Gebaeude zerstoeren, besonders auf Bogenschuetzen aufpassen; nach einer Zerstoerung sofort das naechste. Umbau `assassinen.py`: Trupps zu 6, je eigenes Ziel; Gefahr Fernkaempfer 16 Felder, Nahkaempfer 8; Ziel und Weg (alle 4 Felder) geprueft; Suchkreis 30/45/60; ohne freies Ziel beim naechsten Trupp mithelfen; Rueckzug zum NAECHSTEN sicheren Ort. Trockenprobe gut.
- **Daniel 23:16:** zugebaute Gebaeude (z. B. Rotkaeppchens Kornspeicher) erkennen. Eingebaut: Spalte `erreichbar` in `abzug/gebaeude.txt` - irgendein Feld rund um den Grundriss liegt in einem Wegnetz-Gebiet (PathConnectionLayer 0x01DF6FD8), das Spieler 1 vom Bergfried-Eingang aus erreicht (Spielpruefung calculateCanPlayerUnitsNavigateToAreaFromArea 0x004A5320, wie in findTree). Gemessen: 2 von 91 feindlichen Gebaeuden unerreichbar. (Noch nicht in die Zielwahl verdrahtet.)
- **Partie 3 (23:14-23:17, Tempo 1000, `daten/partie3_konsole.txt`):** aufgeteilt in Trupps zu 6, Bogenschuetzen-Abstand 16. Ergebnis bis Tick 28.730: **1 Gebaeude zerstoert, 2 Assassinen verloren** (Partie 2: 11 zerstoert, 76 verloren). 90 geworben, 15 Trupps, aber nur 5 Zielvergaben - die meisten Trupps standen am Soeldnerlager, 50-100 Felder von Rotkaeppchens Wirtschaft, und fanden in 60 Feldern keinen bogenschuetzenfreien Weg. Waechter: 33 Angreifer erkannt, alle 33 getoetet, 8 eigene Speertraeger verloren; Lord ging bei Tick 19.423 (8 Feinde nah) mit vollem Leben in Sicherheit und lebte am Ende. Wirtschaft unversehrt, Beliebtheit 100.
- **Naechster Schritt:** Mittelweg zwischen Partie 2 (zu kuehn) und 3 (zu vorsichtig): Trupps ohne Ziel rücken sicher bis an einen Bereitstellungsraum am Rand der feindlichen Wirtschaft (kein Fernkaempfer naeher als 20) vor und waehlen dort Ziele im Umkreis 30; Bogenschuetzen-Reichweite messen statt schaetzen (Abstand des naechsten Bogenschuetzen bei jeder Verletzung mitschreiben); `erreichbar` in die Zielwahl.
- **Daniel 23:18:** Assassinen nicht am Soeldnerlager sammeln (es gibt Sammelpunkte), ab 6 sofort nach vorne, je frueher desto besser. Eingebaut: Trupp geht ab 6 Mann los; ohne Ziel in Reichweite rueckt er sicher bis 12 Felder vor das naechste ungeschuetzte, ERREICHBARE feindliche Gebaeude vor (Bereitstellungsplatz); unerreichbare Gebaeude nie als Ziel. Sammelpunkt des Soeldnerlagers (Spielbefehl 71) noch offen.
- **Partie 4 (23:18-23:21, Tempo 1000, `daten/partie4_konsole.txt`):** bis Tick 28.725 **29 Gebaeude zerstoert** (24 Apfelplantagen, 2 Holzfaeller, 3 Jaegerhuetten), **39 von 90 Assassinen verloren**, 11 Trupps. Vergleich: Partie 2 11/76, Partie 3 1/2 -> Partie 4 0,74 Gebaeude je Verlust (Partie 2: 0,14). Verluste nach Zeit: bis Tick 12.000 nur 2, Tick 12.000-24.000 23, danach 7; Rueckzuege gingen meist nach (137,168). Wirtschaft unversehrt, Beliebtheit 100, kein Angriff auf uns.
- Naechste Schritte: beim Verletzen den naechsten Feind (Art, Abstand) mitschreiben -> echte Bogenschuetzen-Reichweite; Rueckzug weg vom Angreifer statt zu einem festen eigenen Gebaeude; Sammelpunkt (Befehl 71) setzen.
- **Merkliste (Daniel 23:25, "jetzt nicht wichtig, aber im Hinterkopf"):** Bier (Hopfen -> Brauerei -> Wirtshaus), Jagd (nur bei Wild), Waffenwirtschaft, Pech, Brot (Weizen -> Muehle -> Baeckerei) vorbereiten, Essensvielfalt (Beliebtheit). Immer noch offen und von Daniel zum zweiten Mal angemahnt: Apfel-Seasoning und Lager erst setzen, wenn der erste Traeger abliefern will.
- **Partie 5 (23:22-23:26, `daten/partie5_konsole.txt`):** Trupps zu 4, verschiedene Ziele, Rueckzug weg vom Angreifer: **29 Gebaeude zerstoert (19 Holzfaeller, 8 Apfelplantagen, 2 Maerkte), nur 5 Assassinen verloren**, 23 Trupps - bestes Ergebnis bisher (5,8 Gebaeude je Verlust).
- **Fehler im Modul gefunden (23:26, Daniels Bild: alle auf einem Ziel):** `angriff` nahm die erste freie Gruppennummer, die Gruppe entsteht aber erst im naechsten Takt - zwei Angriffe in derselben Runde bekamen DIESELBE Nummer, die zweite Auswahl ueberschrieb die erste, alle Trupps liefen auf ein Ziel. Behoben: in einem Takt vergebene Nummern werden reserviert. Damit sind auch Einzelbefehle je Assassine moeglich (1.250 Gruppenplaetze, nicht 10).
- **Partie 6/7 (23:27-23:32):** nach dem Fix nur 1 bzw. 3 Gebaeude, 1 Verlust: die Trupps laufen hin und weichen sofort aus - Partie 7: 19 von 20 Rueckzuegen wegen feindlicher Speertraeger 4-9 Felder nah (Rotkaeppchen bewacht ihre Wirtschaft). Verletzungen kamen oft bei Feinden 17-29 Felder weg (Quelle offen, vermutlich Tuerme). Runden langsamer (0,2 s, 161-218 Runden) - Ursache offen.
- **Naechste Schritte (Daniel 23:29-23:32):** (1) jeden Assassinen EINZELN und gleichzeitig befehligen (je eigene Gruppe); (2) nicht immer ausweichen - Fernkaempfer direkt daneben erledigen, bei Ueberzahl kaempfen; (3) danach Apfel-Seasoning und Lager erst bei Lieferbedarf; (4) Holzfaeller: 3 je Baum (Planer haeuft noch nicht - Modell bestraft geteiltes Holz, Vorteil "Baum vor der Tuer" fehlt); (5) Merkliste Bier/Jagd/Waffen/Pech/Brot.
- **Partie 8 (23:33-23:38, `daten/partie8_konsole.txt`) GESCHEITERT:** jeder Assassine einzeln (51 Trupps) + kaempfen statt fliehen (Fernkaempfer <= 6 Felder, Nahkaempfer bei 2:1). Jeder Trupp schickt seine Befehle EINZELN und wartet je auf die Antwort -> eine Runde 0,7 s (~550 Ticks), nur 62 Runden, **0 Gebaeude, 6 Verluste**. Naechster Schritt: alle Befehle einer Runde sammeln und in EINEM Aufruf (Befehlsliste) schicken - wie die Eroeffnung (30 Bauten in einem Aufruf). Erst danach Kaempfen-statt-Fliehen bewerten; dann Seasoning und Lager bei Lieferbedarf (Daniel 23:32).
- **Daniel 23:35:** je Assassine ein Befehl auf das naechste Wirtschaftsgebaeude, ist es belegt, sofort das naechste. Gebaut: `assassinen.Einzeln` (hoechstens 3 je Gebaeude, nur erreichbare, Befehle einer Runde gesammelt in EINEM Aufruf). Trockenprobe gut (10 Assassinen auf 3 Gebaeude zu je 3, unerreichbares ausgelassen).
- **Partie 9 (23:36-23:40) - "sie sammeln sich nur und machen nichts" (Daniel 23:38), Ursache gefunden:** Die Angriffsbefehle kommen an (Spiel-Log: ANGRIFF ... Art 9 Befehl=true), aber die **Halte-Wache des Moduls zieht die Einheiten sofort zurueck** ("152 nachgesetzt (fremdes Ziel war (124,119))"). Ihre Liste ueberlebt das Laden einer neuen Partie, neue Einheiten mit alten Nummern wurden festgehalten. Abhilfe 1 (`halten: false` zu Beginn) reichte nicht: der Waechter haelt seine Truppen wieder mit "halten", die Wache setzte 9.554-mal nach, flutete das Log, eine Runde dauerte 1,1 s (25 Runden), bei Tick 21.883 war unsere Wirtschaft weg.
- **Naechster Schritt (zuerst):** Die Halte-Wache darf Einheiten mit einem Angriffsziel (Zielart != 0) nicht zuruecksetzen, und sie muss beim Laden einer Partie geleert werden (im Modul, nicht im Lenker); ihre "nachgesetzt"-Zeilen nur zaehlen statt jede ins Log. Danach Partie 9 wiederholen. Dann: Kaempfen statt Fliehen, Seasoning, Lager bei Lieferbedarf (Daniel 23:32).
- **23:47 WAHRE URSACHE fuer Partie 6-9 gefunden (Daniels Hinweis: "finde den Grund, warum sie einfach rumstehen"):** Meine Gruppen-Reservierung von 23:26 war eine GLOBALE Lua-Variable; das UCP-Modul verbietet globale Variablen -> jeder `angriff` brach mit "global assignment not permitted ... angriffReserve" ab ("0 von 3 Befehlen ausgefuehrt"). Seit Partie 6 kam KEIN Angriffsbefehl mehr an: Assassinen standen am Soeldnerlager (Zustand 105 = warten), der Waechter konnte nicht abwehren (Wirtschaft verloren), jede Runde wartete 1 s vergeblich auf "ANGRIFF" (daher 1,1 s je Runde). Die Halte-Wache war nur ein Nebenbefund. Behoben (modul-lokal) und belegt: 3 Angriffe im selben Aufruf -> 3 von 3 ausgefuehrt, Gruppen 1249/1247/1246, alle drei laufen zu ihrem eigenen Ziel (Zustand 101).
- **Lehre:** Fehlerzeilen des Moduls ("global assignment", "0 von N Befehlen ausgefuehrt") muessen den Lenker sofort anhalten - sie standen die ganze Zeit im Log. Die Trockenproben liefen ohne Modul und konnten das nicht finden.
- **Partie 9c (04.10. 23:51-23:54, `daten/partie9c_konsole.txt`):** mit repariertem Modul und lautem Abbruch bei Modulfehlern (`befehl.pruefe`: Lua-Fehlerzeile oder "k von N Befehlen" mit k < N -> Spiel anhalten, ABBRUCH). Kein Modulfehler. Ergebnis bis Tick 28.773: **20 Gebaeude zerstoert, 13 Assassinen verloren** - schlechter als Partie 5 (29/5). Daniels Bilder (00:00): ein Klumpen von rund 30 Assassinen auf einem Fleck, "immer noch mehr als 6 auf ein Gebaeude".
- **05.10. 00:00 ZWEI weitere Ursachen gefunden (gemessen, nicht vermutet):**
  1. **Auswahlmarken blieben stehen.** Lagebild mit neuen Spalten (auswahlvon +178, auswahlmarke +180, gruppe +728, gruppenuid +740): am Ende steckten **78 Assassinen, alle 6 Bogenschuetzen, 5 Speertraeger und der Lord in Gruppe 1249**, alle mit Marke "ausgewaehlt von Spieler 1"; nur der frisch Angeworbene nicht. Der letzte Befehl galt EINEM Assassinen (Gebaeude 113 bei (222,205)) - alle 78 liefen hin. playerMakeUnitSelection (0x00535BC0) setzt die Marken, nichts loescht sie; jede je befohlene Einheit rutschte in jede neue Gruppe. Die "gleichzeitig angegriffen: 29" des Lenkers war nur seine Planliste, im Spiel hatte kein Assassine mehr ein eigenes Ziel. Behoben im Modul: vor jeder Auswahl werden die Marken aller eigenen Einheiten geloescht.
  2. **Mehrere Angriffe im selben Takt landen in EINER Gruppe.** Totschlagtest `werkzeug/pruefe_einzelbefehl.py` (3 Assassinen, je einer, ein Paket, 3 Gebaeude): ROT - alle drei in Gruppe 1245, alle zum letzten Ziel (das Spiel arbeitet Befehl 16 spaeter ab und liest dann die Auswahl des letzten Befehls). Die Aussage von 23:47 ("alle drei laufen zu ihrem eigenen Ziel") war damit **falsch** - damals nur Zustand 101 gesehen, nicht Gruppe und Laufziel verglichen. Behoben: das Modul reiht Angriffe in eine Warteschlange und setzt den naechsten erst ab, wenn die Einheiten des vorigen in ihrer Gruppe stehen (+728), hoechstens 20 Ticks Wartezeit. Gegenprobe GRUEN: Gruppen 1247/1246/1244 in den Ticks 28.874/875/876, jeder 1-2 Felder vor seinem eigenen Gebaeude, von den uebrigen 136 eigenen Einheiten keine mitgerissen.
- Dazu im Lenker: hoechstens **6** Assassinen je Gebaeude (Daniel 00:00); je Assassine ein eigener Befehl; **Gegenprobe je Runde** - laeuft einer laut Lagebild nicht zu seinem Gebaeude (Laufziel weiter als 8 Felder), bekommt er den Befehl neu; die gemeldete Zahl "gleichzeitig angelaufen" ist jetzt im Spiel gemessen. Der Waechter nimmt keine Assassinen mehr zur Abwehr (wie schon in seiner Grundstellung).
- **Lehre:** Ein Befehl ist erst angekommen, wenn die Einheit im Spiel dorthin laeuft (Gruppe und Laufziel), nicht wenn das Modul "Befehl=true" meldet. Ein Lenker, der nur seine eigene Liste zaehlt, sieht das nie.
- **Partie 9d (05.10. 00:01-00:03, `daten/partie9d_konsole.txt`) mit beiden Behebungen:** bis Tick 28.715 **74 Gebaeude zerstoert** (33 Holzfaellerhuetten, 20 Apfelplantagen, 5 Huetten, 5 Ochsenjoche, 4 Kornspeicher, 4 Marktplaetze, 2 Jaegerhuetten, 1 Steinbruch), **53 von 90 Assassinen verloren**. Vergleich: Partie 5 29/5, Partie 9c 20/13. Im Spiel gemessen gleichzeitig angelaufene Gebaeude je Runde: bis 12, Gegenprobe musste nur 4-mal neu befehlen. Waechter: kein Angriff auf uns, Beliebtheit 100, kein Modulfehler.
- **Offen (naechster Schritt):** Die Einzelsteuerung hat keine Gefahrenpruefung - sie laeuft in Bogenschuetzen. Ziel nach Daniels Auftrag ist zerstoeren OHNE Verluste. Erst messen, wo die 53 starben (naechster Feind bei Verletzung/Tod), dann: Ziele im Bereich feindlicher Fernkaempfer meiden, Fernkaempfer direkt daneben erledigen statt fliehen (Daniel 23:4x).

## M17 Messen, Gefahr, Lager, Seasoning (Daniel 05.10. 00:06: "ja, mach so weiter beachte gleich auch seasoning/vorratslager etc.")
- **Messung Partie 9e** (gleiches Verhalten wie 9d, `daten/partie9e_konsole.txt`): 72 zerstoert / 25 verloren. **21 von 25 Toten hatten KEIN Ziel** und standen untaetig (Zustand 1) im Schussfeld, meist ~10 Bogenschuetzen 9-19 Felder weg. Ursache: die meisten Wirtschaftsgebaeude galten als unerreichbar, die erreichbaren waren mit je 6 voll - wer leer ausging, blieb stehen, wo sein letztes Ziel fiel. Bei 223 Verletzungen stand der naechste Fernkaempfer meist 9-30 Felder weg.
- Partie 9d endete mit Rotkaeppchens Wirtschaft praktisch weg: 23 Gebaeude uebrig, davon ein einziges Wirtschaftsgebaeude (zugebaut).
- **Partie 9f** (Warten ausser Reichweite, Rueckzug bei Verletzung, Fernkaempfer direkt daneben angreifen, Ziele mit >2 Fernkaempfern im Umkreis 20 meiden): **66 / 17** - bestes Verhaeltnis seit Partie 5. Rest: 11 von 17 ohne Ziel; Ende: 57-66 Assassinen warten, weil alle Ziele bewacht.
- **Partie 9g** 38 / 78 und **9h** 51 / 60 - schlechter. Ursachen gemessen: (9g) Warteplaetze waren Gebaeudemitten, nicht begehbar - 289-mal "warten klappt nicht", die Wartenden blieben im Schussfeld; (9h) 210 Rueckzuege quer ueber die Karte nach Hause, 37 starben im Laufen; der erste Stapel (15) griff einen Bogenschuetzen an, um den 17 weitere standen. **Lehre (wie Partie 2/5): kurz vom Angreifer weg, nicht heimlaufen; Stapel nur auf einsame Schuetzen.** Daniels Bilder 00:30: "da stehen einfach Bogenschuetzen und farmen unsere Assassinen ab", "oben stehen noch so 30 Assassinen, die nichts machen".
- **Widerlegt (05.10. 00:40):** die Wegnetz-Pruefung (PathConnectionLayer + calculateCanPlayerUnitsNavigateToAreaFromArea) meldet Wasser, Kartenrand und Gebaeudefelder als erreichbar - sie taugt NICHT als Begehbarkeits- oder Erreichbarkeitspruefung. Damit ist auch die Spalte `erreichbar` (Gebaeude 04.10., Einheiten 05.10.) NICHT belegt - das Erkennen zugebauter Gebaeude (Daniel 04.10. 23:16) ist offen. Ersatz fuer Begehbarkeit: Rohstoffkarte (nur G/s/. samt Nachbarn), Gegenprobe gruen (0 von 10 Wasser/Rand/Gebaeude).
- **Seasoning belegt** (Spielcode + Messung, `werkzeug/wirtschaft.py`): Apfelbaum-Stufen 500/300/200/**1000**/40/40 Ticks (Tabelle 0x00B484C0, 1 Schritt je Tick gemessen), geerntet nur in Stufe 3; Baeume beim Bau gepflanzt, Start Stufe 0; der Apfelbauer nimmt JEDEN reifen Apfelbaum naeher als 30 Felder (selectClosestTree prueft weder Plantage noch Besitzer). Umsetzung: Gruppe A (6) in der Eroeffnung, Gruppe B (4) wenn A reif wird. **Gemessen: Apfelbauern untaetig ohne Seasoning 40 % (Tick 5000-12000, Vergleichsspiel), mit Seasoning 11 % (Partie 9h ab Tick 4610)** - rund 1,5-mal so viel Arbeitszeit. Aepfel je Zeit noch nicht direkt gemessen. Rest: B wurde in 9g/9h spaet gesetzt (Markt verbaute das B-Holz) - jetzt kauft der Lenker Holz nach.
- **Lager bei Lieferwunsch belegt** (UpdateWoodcutter abgelesen: ohne Lager wartet der Holzfaeller in Zustand 7, fragt alle 21 Ticks): erster Lieferwunsch am Eroeffnungsstand bei Tick ~4.500 gemessen; in 9h altes Lager leer abgerissen bei 3.610, neues Lager bei 4.279 gesetzt, als der erste Holzfaeller abliefern wollte. Holzfaeller tragen **18 Holz je Gang** (gemessen). Erweitern: die Platzsuche fand neben dem Lager keinen Platz ("erweitert None") - offen.
- Eroeffnung wird nur neu gebaut, wenn sich Plan oder Code aendern (Fingerabdruck, Daniel 00:18); Spielstand "M17 Eroeffnung Saison T602". Befehlskanal hat jetzt eine Sperre im Werkzeug (`.lauf`): eine Nebenabfrage aus einem zweiten Prozess wird abgelehnt, solange ein Lauf aktiv ist.
- **Partie 9i (05.10. 00:38-00:39) - SIEG bei Tick 9.161** (`daten/partie9i_konsole.txt`): kurzer Rueckzug (15-25 Felder weg vom Feind, begehbar laut Rohstoffkarte), Stapel nur auf einsame Schuetzen. Bis dahin **48 Gebaeude zerstoert** (17 Holzfaellerhuetten, 17 Apfelplantagen, 5 Ochsenjoche, 5 Huetten, 1 Kornspeicher bei Tick 9.090, 1 Markt, 1 Jaegerhuette, 1 Steinbruch), **11 Assassinen verloren**. Belegt: Spieler 2 `lordKilledBy = 1`, playerIsAlive nur noch Spieler 1, gameOver 1. KEIN Befehl galt dem Lord (0 Angriffe auf Nr. 137) - vermutet: unsere Assassinen am Kornspeicher neben ihrer Burg, ihr Lord hat nur Staerke 0,5. Seasoning: B bei 1.784 gesetzt (258 Ticks nach A-Reife), Apfelbauern untaetig 17 % im festen Fenster (ohne Seasoning 40 %).
- Fehler in 9i: das neue Lager kam erst bei Tick 9.035 - Markt und Soeldnerlager standen auf dem Lagerplatz, 14 Holzfaeller warteten ab ~4.500. Behoben: beide jetzt beim Bergfried, Lager-Suchkreis 8.
- **Partie 9j (05.10. 00:42-00:43, Wiederholung von 9i) - wieder SIEG, bei Tick 9.036** (`daten/partie9j_konsole.txt`): 45 Gebaeude zerstoert, 12 Assassinen verloren; Spieler 2 `lordKilledBy = 1`. Der Sieg ist damit zweimal in Folge da (9i, 9j). Lager diesmal rechtzeitig: gesetzt bei Tick 4.328, als der erste Holzfaeller abliefern wollte; Erweiterung klappte ("Lager erweitert (124, 114)", 0 Fehlversuche) - beides war in 9i am Markt gescheitert. Seasoning: Apfelbauern untaetig 21 % im festen Fenster (ohne Seasoning 40 %). Offen bleibt, WIE der Lord fiel - kein Befehl galt ihm.
- **Partie 9k (00:45, Pruefung der neuen Meldungen):** kein Sieg - lief bis Tick 28.741, 72 Gebaeude zerstoert. Die neue Lord-Messung zeigt, WIE der Lord in 9i/9j vermutlich fiel: unsere Assassinen auf dem Weg zu Zielen in ihrer Burg standen 3-11 Mann in 5 Feldern um ihn (bei (230,287)) und trafen ihn ohne Befehl; in 9k sank sein Leben nur von 150.000 auf 108.600, dann zogen sie weiter. Folgerung fuer morgen: ein gezielter Stapel auf den Lord (Daniel: "irgendwann auch direkt auf den Lord") koennte das zuverlaessig machen. Sieg/Niederlage stehen jetzt als SIEG/NIEDERLAGE-Zeile in der Konsole statt "ABBRUCH".

## M18 Lord-Trupp (Daniel 05.10. 00:52 Regel, 00:53 "ja, morgen damit anfangen") - GILT (05.10. 18:37)
- **Schritt 0, Erreichbarkeit belegt:** neuer Modulbefehl `wegtest` fragt den Wegfinder des Spiels (setDestinationForUnit 0x0053D3D0 gibt FALSE ohne Weg; danach bekommt die Einheit ihr altes Laufziel zurueck). Gegenprobe gruen: Wasser (2) und Gebaeudefelder (2) -> kein Weg, freies Feld -> Weg. Ersetzt die widerlegte Wegnetz-Pruefung. Offen: ob Assassinen ueber Mauern duerfen (bei Tick 602 stand ihre Mauer noch nicht; in 9l/9m fand der Wegtest jedes Mal einen Weg zum Lord).
- **Lord-Trupp** (`assassinen.Einzeln`, Startwerte nach Daniels Regel): alle 5 Runden pruefen; noetig 5 wenn der Lord allein steht, sonst 10 + 2 je Fernkaempfer + 1 je Nahkaempfer im Umkreis 15; nur losschicken, wenn so viele frei sind UND der Wegtest einen Weg findet; bei hoechstens 5 Feindtruppen alle Freien mit; ein gebuendelter Befehl, Gegenprobe "greift er wirklich den Lord an" (Zielart 4, Zieleinheit = Lord), unter 3 aufloesen.
- **Partie 9l:** SIEG bei Tick 11.318 - aber der erste Trupp ging mit 7 statt der noetigen 15 los ("wenig Feinde" ueberging die Groesse), 5 starben, Lord 150.000 -> 79.200; der zweite (25) erledigte ihn. Fehler behoben: die Truppgroesse gilt immer.
- **Partie 9m (nach der Korrektur): SIEG bei Tick 10.278** - EIN Trupp (26, noetig 13) bei Tick 9.267, 2 Verluste im Trupp; Partie gesamt 47 zerstoert / 16 verloren. Die SIEG-Zeile in der Konsole ist damit auch belegt.
- Vergleich: 9i/9j siegten bei ~9.000-9.200 durch Zufall (Assassinen trafen den Lord im Vorbeilaufen), 9k gar nicht; 9l/9m gezielt.

## M19 Liga-Start mit 0 Gold (Daniel 05.10. 00:55) - Messungen 05.10. 18:38-18:45
- **Ursache der 3.930 Gold:** unsere Starts nahmen nicht die Liga-Bedingung. Gemessen mit `eigenesGefecht` (Grumpy, 1 Rotkaeppchen): Ausgleich 3 -> **Mensch 0 Gold, Rotkaeppchen 50** (Tick 20; 45 bei Tick 600); Ausgleich 2 -> beide 500. Die Liga-Konfiguration nennt "noAdvantage": Mensch 0, Computer 150.
- **Neuer Startstand `M19 Liga Start Grumpy T600`:** 0 Gold, 150 Holz, 7 Speertraeger, 5 Bogenschuetzen, 10 Leute, Beliebtheit 93,25. Die Start-Nahrung (je 15 Brot, Kaese, Fleisch, Aepfel = 4 Sorten) erscheint erst mit einem Kornspeicher (gemessen: 200 Ticks nach dem Bau da).
- **Steuern gemessen** (`werkzeug/steuern_messen.py`, `daten/steuern_messung.txt`; 10 Leute, je 600 Ticks ohne Kornspeicher): Stufe 0-2 (Bestechung) ohne Gold wirkungslos (+0 Gold, Steuerteil +25); Stufe 3 +0 Gold, Steuerteil -25; Stufe 4-11 +1 bis +10 Gold in 600 Ticks bei Steuerteil -75 bis -1.000 (Beliebtheit 93,25 -> 83,5 ... 55,75). **Am Anfang bringen Steuern fast nichts** - sie wachsen mit der Zahl der Leute.
- **Kosten (Liga-Balance, aus dem Spiel gelesen):** Holzfaeller 5 Holz; Markt 0; Apfelplantage 3 Holz + 15 Gold; Jaegerhuette 3 Holz + **60 Gold**; Soeldnerlager 120 Gold. Naechstes Wild 57-61 Felder vom Bergfried (bei (106,137), neben unseren Apfelplantagen).
- Folgerung: die alte Eroeffnung (10 Apfelplantagen sofort = 150 Gold) geht so nicht mehr; sie muss neu gerechnet werden.
- **Nahrung auf Kante** (Daniel 18:51): Verkaufspreise Kaese 6, Brot 4, Aepfel 3, Fleisch 1, Holz 1 (gemessen); Verbrauch 10 Leute ~1 Stueck in 1.000 Ticks (gemessen). Eroeffnung: Kornspeicher + Markt, Start-Nahrung bis auf den Puffer (3 + 1 je 10 Leute) verkaufen, teuerste zuerst -> **205 Gold** (Partie 9n gemessen), davon die Apfelplantagen; laufend alles ueber dem Puffer verkaufen.
- **Partie 9n abgebrochen** (Daniels Bild 18:55): der Plan war fuer den Bergfried des alten Starts (165,111) gerechnet - im Liga-Start steht er bei (141,269). Behoben: `karten_holen.py` (Bergfried-Eingang aus dem Spiel, Gegenprobe im alten Start = (165,111)), Planer je Start (`eroeffnung.py start=M19`) und nur auf unserer Kartenhaelfte; feste (165,111) aus Lenker und Wachter entfernt. Neuer Plan M19: Wirtschaft westlich vom Bergfried, mindestens 50 Felder von Rotkaeppchen; 6 statt 10 Apfelplantagen (mehr passten nicht).
- **Partie 9o (Liga-Start, Plan fuer den echten Bergfried):** 79 Feindgebaeude zerstoert (61 Apfelplantagen) / 26 verloren, kein Sieg; das neue Lager kam nie - das alte (26 Holz Rest) wurde nur "wenn leer" abgerissen, die Holzfaeller trugen alles 50-80 Felder zum Bergfried. Behoben: Rest verkaufen, bei hoechstens 20 trotzdem abreissen.
- **Partie 9p:** altes Lager bei Tick 1.867 abgerissen (7 Holz Rest), neues Lager beim Holz bei 4.018 (erster Lieferwunsch). **99 Feindgebaeude zerstoert** (45 Apfelplantagen, 37 Holzfaellerhuetten) / 31 verloren, 40 Assassinen angeworben, **kein Lord-Trupp** (nie genug frei bei Liga-Gold), kein Sieg. Gemessen: Leute = Wohnplatz in 424 von 433 Zeilen (Wohnraum ist die Grenze); Beliebtheit 100 in 255 von 433 Zeilen (Spielraum fuer Steuern ungenutzt); Apfelbauern untaetig 29 % im festen Fenster.
- **Zielwahl nach Wert (Daniel 19:05):** Ausbildungslager/Kornspeicher 100, Steinbruch 80, Waffenbauer/Eisen 70, Huetten 60 ... Apfel 30; gewaehlt nach Wert je Weg, abgeschwaecht durch Fernkaempfer am Ziel. **Partie 9q:** 83 zerstoert, darunter 10 Steinbrueche, 9 Ochsenjoche, 2 Kasernen, 5 Pechgruben, 4 Eisenminen / 27 verloren.
- **Ausbau-Regeln (19:07):** Huetten vor der Wohngrenze (9q: Leute 26 -> 56), Steuern nach Beliebtheit, Jagd an Rehen, Nachbauen, 2. Steinbruch + Ochsenjoch, Eisenmine. Gefunden (Daniel 19:09): das alte Lager blieb bis Tick 6.175 stehen, weil B auf Gold wartete - Soeldnerlager und Ausbau hatten es ausgegeben; Jaeger 166 Felder weit weg. Geflickt (Lager weg beim ersten Lieferwunsch: 9r gemessen Tick 4.004, neues Lager im selben Takt; B vor Gold; Jagd hoechstens 70 Felder).
- **Daniel 19:11: "keine Fixes, sondern ein schlaues System, das wirklich abhaengig von der Umgebung handelt; beliebig mit Gebaeuden erweitern; am meisten Geld geben Stein und Eisen."** -> naechster Schritt: Ertrags-Planer statt Einzelregeln (siehe Vorschlag im Chat 19:12).

## M20 Ertragstabelle (Messpartie, Daniel 19:14) - 05.10. 19:25
- Pruefstand `werkzeug/messpartie.py` (nur Gold gesetzt; Holz, Stein, 50 Aepfel am Markt gekauft; je ein Gebaeude), 8.000 Ticks, `daten/ertrag_messung.{txt,json}`. Drei Fehlversuche vorher, gemessen: gesetzte Waren-Zaehler verschwinden mit dem abgerissenen Lager (es zaehlt das physische Lager); Kornspeicher bei 0 Holz entsteht nicht (die "Gebaut"-Liste zeigt nur den Platz - jetzt Gegenprobe im Spiel); zwei Laeufe gleichzeitig im Befehlskanal -> Messpartie jetzt mit Kanalsperre.
- **Verkaufspreise neu:** Stein 5, **Eisen 27** Gold je Stueck.
- **Ertrag je 1.000 Ticks ab erster Lieferung** (wenige Lieferungen - Richtwerte, nicht geeicht): Stein 5,6 (Steinbruch 8 Felder vom Lager, 1 Ochse, 12 je Ochsengang, erste bei 3.750) = ~28 Gold; Eisen 1,1 (Mine 61 Felder vom Lager!, erste bei 6.250) = ~30 Gold; Fleisch 7,0 (Jaeger 53 Felder vom Kornspeicher) = 7 Gold; Aepfel 2,9 (eine Plantage ohne Seasoning, 5 Felder) = ~9 Gold; Holz 6,0 (1 Lieferung zu 18, 17 Felder) = 6 Gold.
- Folgerung (vorlaeufig): Eisen ist je Stueck am wertvollsten und bringt trotz 61 Feldern Weg so viel wie Stein; mit Lager an der Mine deutlich mehr. Stein und Eisen vorne, wie Daniel vermutete. Fuer den Planer fehlen laengere Laeufe (mehr Lieferungen) und Werte je Weglaenge.
- **Lange Messpartie (20.000 Ticks, Daniel 19:27; `daten/ertrag_messung.*`, `messpartie2_konsole.txt`):** je 1.000 Ticks ab erster Lieferung - Holz 5,4 (Holzfaeller 6 Felder vom Lager); Stein 2,4 (Steinbruch 23 Felder, 1 Ochse) = 12 Gold - **ab Tick ~12.000 stand der Stein bei 48 = ein volles Lagerteil, der Bruch lieferte nicht mehr: Wert durch Lagerplatz gedeckelt, nicht durch den Bruch**; Eisen 0,7 (Mine 31 Felder) = 19 Gold; Fleisch 5,5 (Jaeger 53 Felder vom Kornspeicher); Aepfel 2,2 (eine Plantage, 5 Felder). Preise bestaetigt: Stein 5, Eisen 27. Rangfolge Gold je 1.000 Ticks: Eisen > Stein (gedeckelt) > Aepfel > Fleisch ~ Holz. Streuung zwischen Lauf 1 und 2 gross (Eisen 1,1 bei 61 Feldern vs 0,7 bei 31) - wenige Lieferungen.
- **Ertrags-Planer gebaut (`werkzeug/ertragsplaner.py`, Daniel 19:33):** jede 10. Runde Kandidaten (Eisenmine, Steinbruch+Ochsenjoch, Apfelplantage, Jaeger, Holzfaeller) an ihrem besten Platz; Wert = Ertrag (Messpartie, Wegkorrektur vermutet) * Preis; Amortisation = Kosten (Holz 3, Stein 5) / Gold je Tick; baut die schnellste bezahlbare, spart sonst; Huette zuerst bei fehlenden Leuten, Lager anbauen bei fast vollem Teil; Holzwert nach Lage (3 bei Mangel, 1 bei Ueberfluss). **Partie 9s (abgebrochen):** baute 10+ Holzfaeller (billig, Amortisation ~2.000), aber die Eisenmine scheiterte >20-mal an Nachbarfeldern (Eisen-Felder der Rohstoffkarte sind keine gueltigen Bauplaetze); der erste Holzfaeller richtete sich am alten Startlager aus. Behoben im Code (noch nicht im Spiel geprueft): Fehlschlag sperrt Umkreis 8; gueltige Anker aus Platzkarten (karten_holen holt jetzt auch "eisenmine"); Ziel ist das kuenftige Lager. **Naechster Schritt:** `python karten_holen.py "M19 Liga Start Grumpy T600" M19` (holt die Eisenminen-Karte), dann Partie mit dem Planer.
- **Partie 9t (05.10. 19:40, Ertrags-Planer mit Ankerkarten):** Eisenminen-Karte zeigt: die 'i'-Felder nahe dem Lager sind Einzelflecken, die echte Lagerstaette liegt bei (135,323), 43 Felder vom Lager. Planer baute 14 Holzfaeller, 8 Eisenminen (alle an gueltigen Ankern, kein Fehlschlag), 2 Steinbrueche, 26 Jaegerhuetten, 0 Apfelplantagen (alle Versuche "-> None": das Apfel-Raster ist kein gueltiger Platz). Vergleich mit 9r (gleiche Laenge, je EINE Partie): Assassinen 50 statt 45, zerstoerte Feindgebaeude 82 statt 75, kein Sieg (Lord-Trupps 0). Verkaeufe gezaehlt aus den "verkauft:"-Zeilen x gemessener Losgroesse: Eisen 12 Lose = 1.620 Gold (9r: 270), Holz 2.960 (3.040), Stein 725 (1.350), Fleisch 120 (0). **Befund:** Eisen traegt, wie Daniel sagte; die 26 Jaegerhuetten kosteten 1.560 Gold und brachten 120 - der Planer glaubte 9-15 Gold/1000, weil er den Ertrag nach Weg hochrechnet (vermutet, nie gemessen) und keinen Zeithorizont kennt (Amortisation 7.000-12.000 Ticks in einer Partie von 28.000). Dasselbe Baum-Ziel (41,209) wurde 6-mal bebaut (Ort landet bis 10 Felder daneben, das Ziel bleibt "frei").

## M21 Planer lernt im Spiel - erster Liga-Sieg (Daniel 19:44 "ja, bau das so") - 05.10. 20:10
- **Auftrag:** Planer misst im Spiel, was jede Gebaeudeart liefert, baut nur, was sich bis Partieende bezahlt macht; Aepfel und Holzfaeller ueber Platzkarten. Dazu Daniels Hinweis: Holz/Stein nie kaufen (Wert = Verkaufspreis), Stein bis auf den Bedarf der Eisenminen verkaufen.
- **Gemessen statt angenommen:** Baukosten aus der Tabelle im laufenden Spiel (Eisenmine 20 Holz + 6 Stein; Daniel schrieb "1 Stein" - das Spiel sagt 6). Platzkarten jetzt ueber die ganze Karte (vorher Bergfried +-80: die meisten Baeume unserer Seite lagen ausserhalb; jede Karte 0-2 s).
- **Ertragsmesser** (`werkzeug/ertragsplaner.py`): Zugang je Ware = Bestand + Verkauft + Verbaut (neue Gebaeude x Baukosten), je Runde; Protokoll `daten/ertrag_live_*.jsonl`, Ergebnis `daten/ertrag_gelernt_*.json`. **Widerlegung vorher festgelegt** (>5 % negative Runden oder >10 % negative Summe = Buchfuehrung falsch): nicht widerlegt in 9u/9v/9w - Holz je 1 negative Runde von 652-756 (12-17 von ~2.400 Holz), Stein und Eisen 0. Gegenprobe ohne Rechnung (abgegebene Ladung der Arbeiter / gebuchter Zugang): Eisen 0,91-0,96, Aepfel 0,78-0,87 - Holz 0,10-0,17 und Jaeger 0,29-0,46 (deren Abgaben sieht das Lagebild nur zum Teil). Teil (b) der Widerlegung (Bau gegen den eigenen Horizont) ist durch die Bauweise ausgeschlossen - das ist kein Messbeleg.
- **Drei eigene Fehler unterwegs, je an einer Partie erkannt:** 9u - Holzfaeller der Eroeffnung zaehlten ab Tick 729, ihre erste Ladung kam bei ~4.600 -> Planer hielt Holz fuer wertlos (Uhr startet jetzt bei erster Abgabe oder nach dem Anlauf); 9u - meine Regel "kein zweiter Betrieb vor der ersten Lieferung" schob die Minen 2-6 um ~6.000 Ticks (gestrichen; Startwerte zaehlen stattdessen mit ihrer Messdauer); 9v - Reihenfolge nach kuerzester Amortisation baute 7 ferne Holzfaeller (~2 Gold/1000) und 3 ferne Steinbrueche vor der ersten Mine (jetzt: zuerst der groesste Gewinn bis Partieende, Ausweichbau nur ohne dem besten etwas wegzunehmen). Dazu im Trockenlauf gefunden: ein alter Feldname in der Beleg-Pruefung haette die Partie beim ersten Bau abstuerzen lassen.
- **Gemessen im Liga-Spiel** (je 1.000 Ticks je besetztem Betrieb, auf Messweg): Eisen 0,55-0,63 @ 31, Anlauf 6.500-6.700; Stein 6,5-6,9 @ 8; Aepfel 3,2-3,7 @ 5, Anlauf 2.200-2.500; Jaeger 3,2-3,8 @ 53; Holz im Schnitt ~5,6 je Holzfaeller, kaum vom Weg abhaengig (die Wegformel ist dort zu streng).
- **Vergleich, je EINE Partie, gleiche Laenge (bis Tick 28.700):**

| Partie | Planer | Assassinen | zerstoerte Feindgebaeude | Gold aus Verkaeufen (Lose x gemessene Losgroesse) | Gold in Jaeger/Aepfel | Ergebnis |
|---|---|---|---|---|---|---|
| 9t | Stand 1 (feste Werte) | 50 | 82 | 6.485 | 1.560 | kein Sieg |
| 9u | Stand 2 (lernt, Beleg-Regel) | 55 | 44 | 5.530 | 315 | kein Sieg, 10 Feindangriffe |
| 9v | Stand 3 (Uhr, Gewicht) | 60 | 103 | 5.585 | 165 | kein Sieg |
| 9w | Stand 4 (Gewinn bis Ende) | 70 | 79 | 5.960 | 270 | **SIEG bei Tick 27.349** |

- **Der Sieg (9w):** Rotkaeppchens Lord starb bei seinem Bergfried (230,287) durch 5-8 Assassinen, die dort Ziele angriffen - nicht durch den Lord-Trupp (Lord-Trupps 0). Erste Eisenmine bei Tick 6.137, 8 Minen bis 14.557.
- **Offen** (Backlog): Wegformel je Art aus den Messdaten statt vermutet (Holz, Jaeger); Steinbruch-Gegenprobe ueber den Ochsen; Horizont in echten Partien ohne festes Ende; Startwerte aus frueheren Partien statt nur aus der Messpartie; eine Partie ist kein Beweis - mehrere Laeufe je Stand.

## M22 Serie x: 8 Laeufe mit Planer Stand 4 auf zwei Instanzen (Daniel 20:12 "ja, mach mehrere Laeufe mit beiden Instanzen") - 05.10. 20:22
- **Werkzeug `werkzeug/serie.py`:** holt die Testsperre (eigener Name "SAI", Instanz ueber SHC_INSTANZ), setzt eine fertige Partie ueber {"menue": 41} ins Hauptmenue (Fehlerhub mp-18), pausiert, spielt erstes_spiel.py bis Tick 28.700, schreibt je Lauf eine Zeile (`daten/serie_x.txt`); `serie.py auswerten name=x auch=9w` fasst zusammen. Gegenprobe der Auswertung an 9t-9w: dieselben Zahlen wie von Hand.
- **Instanz 2 war belegt** (andere Sitzung, "Tastenprobe"/"gefecht.py pruefen") - zweite Serie darum auf Instanz 3 (frei, mit start_hinten.ps1 im Hintergrund gestartet, danach mit spiel.py wieder beendet).
- **Zwei Pannen, beide behoben:** (1) Fehlversuch auf frischer Instanz 3: ohne Pause liefen nach dem Laden einige Takte, die Niederlage-Pruefung setzte gameOver = 1 vor eigenerPlatz (bekannt seit 30.09.) - serie.py pausiert jetzt vor jedem Lauf. (2) Sperre: mit dem Standardnamen "villagestudio2" galt die Sperre einer anderen Sitzung als eigene; eine Gegenprobe an der echten Sperre ueberschrieb deren Eintrag "gefecht.py pruefen" - sofort wiederhergestellt, kein Schaden. Konstruktionsfehler der Sperre als Auftrag "SPR - Sperre je Sitzung" weitergegeben.
- **Ergebnis (8 gueltige Laeufe, Auswertung `serie.py auswerten`):** **0 Siege** - der Sieg aus 9w kam nicht wieder. Mittel: Assassinen 66,9 (55-75), zerstoerte Feindgebaeude 71 (53-82), Gold aus Verkaeufen 6.075 (5.340-6.650), erste Eisenmine bei Tick 6.124 (5.789-6.540). Buchfuehrung in allen 8 Laeufen: Holz 1 negative Runde, Stein/Eisen 0.
- **Befund 1 - der Lord-Trupp bildet sich nie:** in keinem der 8 Laeufe eine einzige LORD-PRUEFUNG (sie wird erst geschrieben, wenn genug freie Assassinen da sind: 10 + 2 je Bogenschuetze + 1 je Nahkaempfer um den Lord). Treffer auf den Lord 0-4 je Lauf, beilaeufig. Auch der Sieg in 9w kam ohne Trupp. Die Neuen werden sofort auf Gebaeude verteilt; ein Vorrat sammelt sich nie. Wie viele gebraucht und wie viele frei waren, schreibt der Code bisher nicht mit - das ist die naechste Messung.
- **Befund 2 - Takt bei zwei Spielen:** Instanz 3 (parallel) schaffte 458-505 Lenker-Runden je Partie, Instanz 1 654-774; Instanz 3 lag bei Assassinen (62,5 gegen 71,3) und Zerstoerten (67 gegen 75) darunter. Parallele Laeufe sind nicht ganz gleichwertig - Vergleiche nur innerhalb gleicher Bedingungen.
- **Befund 3 - Jaeger-Startwert zu hoch:** in x4 baute der Planer 9 Jaegerhuetten (Startwert 5,5 mit Gewicht 15.000; gemessen in 9u-9w 3,2-3,8). Startwerte aus frueheren Partien wuerden das beheben (Backlog).

## M23 Ochsen nach Stau, Startwerte aus Partien, Lord-Trupp Stand 2, Code-Kennung, Wegpruefung (Daniel 20:24-20:50) - 05.10. 20:58
- **Ochsenjoche nach Stau** (Daniel 20:26, Bild): Vorrat im Gebaeude gemessen (+0x184/+0x188 ab Datensatz = 0xF98520+0x14+i*0x32C); Steinbruch -> Steinhaufen Typ 21 (+0x192). Ende x4: Haufen 47/42/34 von 48 an den fernen Bruechen mit je 1 Ochsen. Lagebild liefert jetzt `vorrat grenze verbund` (logik.lua; Kopie `werkzeug/logik_stand_20260930.lua`). Regel: Haufen >= 12 (eine Ochsenladung) und nicht schrumpfend -> ein Joch mehr, hoechstens 3 je Steinbruch, danach 3 Planungsrunden beobachten. Serie y (4 Laeufe): 6-8 Joche je Partie, Haufen am Ende 1-27 statt bis 47; Stein-Lose 75-80 statt 43-64.
- **Startwerte aus 10 frueheren Partien** (`daten/ertrag_startwerte_M19.json`, `python ertragsplaner.py startwerte M19 <dateien>`): Eisen 0,61, Stein 6,72, Aepfel 3,25, Jaeger 3,07 (statt 5,5 -> in y keine Jaegerhuetten). Nebenwirkung y: Steinbrueche vor der ersten Mine (Tick ~8.000 statt ~6.000), Gold 6.062 statt 6.450 im Mittel (je 4 Laeufe, Spannen ueberschneiden sich nicht).
- **Lord-Trupp** Messung (20:35): noetig nach meiner alten Umrechnung 36 (12 Bogenschuetzen + 2 Nahkaempfer um den Lord), frei 0 - darum nie ein Trupp. Daniel 20:39: "mit minimal 5 Assassinen einen Lord killen" (stapeln, Schwache zurueck, sofort wieder drauf). Stand 2 gebaut (Sammelpunkt, Welle ab 5 mit EINEM Befehl, Rueckzug + Wiederangriff; Test `werkzeug/lordtrupp_pruefen.py` 7/7, gegen die alte Fassung rot). Serie z1: 0 Wellen (Gebaeude-Vergabe nahm alle Freien; Sammelpunkt einmal bestimmt, 13 starben dort stehend) -> korrigiert. Serie l (3 gueltige Laeufe, Tempo 1000): 2-4 Wellen je Partie, Lord-Leben hoechstens auf 140.200 von 150.000 (l2), sonst unberuehrt; Feinde um den Lord 14-17 Fern / 7-18 Nah; zerstoerte Gebaeude 20-33 statt 75-87. **Befund: bei Tempo 1000 (~25 Lenker-Runden je 1.000 Ticks) gelingt das Stapeln und Wechseln nicht** - naechste Probe Tempo 200 (Serie t).
- **Code-Kennung** (Daniel 20:46): `werkzeug/kennung.py` - Fingerabdruck ueber alle von erstes_spiel.py erreichbaren Python-Dateien (Importe im Quelltext, rekursiv), die logik.lua der Instanz und die Startwerte. Jede Partie schreibt `CODE-KENNUNG xxxxxxxx` als erste Zeile; serie.py rechnet die erwartete vorher aus und bricht bei Abweichung laut ab. Gegenprobe: eine Kommentarzeile aendert sie (a7dec9cc -> 4606a67e), zurueck = gleich. Instanz 3 zeigte sofort eine andere Kennung (alte logik.lua).
- **Nie unerreichbar bauen** (Daniel 20:50, Bild: Holzfaeller jenseits des Flusses): Wegtest des Spiels vom Lord zu jedem Bauplatz, Ergebnis je Punkt gemerkt. Gemessen: 6 von 7 Orten, an denen in l/y/z Holzfaeller standen, hatten KEINEN Weg; von 197 Holzfaeller-Plaetzen an Baeumen 29 ohne Weg (Westrand am Wasser).
- **Sofort loslegen** (Daniel 20:50): Planer plant ab Runde 1 (vorher erst Runde 10 = Tick 1.634 in l1). Laden: gelegentlich gameOver 1 nach dem Laden (l1, l4) -> bis zu 3-mal neu laden statt den Lauf zu verwerfen; vor jedem Lauf ueber das Hauptmenue.
- **Serie t (Tempo 200, Kennung 35dc280b, 2 Laeufe, 05.10. 21:00):** Lenker ~87 Runden je 1.000 Ticks (Tempo 1000: ~25), Spiel ~200 Ticks/s (eine Partie ~2,5 min). t1: kein Sieg, 90 Assassinen, Verkaufsgold 8.340 (Tempo 1000 sonst ~6.000), 14 Bauplaetze ohne Weg verworfen. **t2: Lord-Trupp brachte Rotkaeppchens Lord von 150.000 auf 54.900 (5 Wellen, 72 Rueckzuege, 61 Wiederangriffe) - dann NIEDERLAGE bei Tick 20.990 (unser Lord fiel).** Zwei Laeufe sind kein Beweis, aber der Unterschied zu Tempo 1000 (Lord hoechstens -7 %) ist gross.

## AUFTRAG FUER MORGEN (Daniel 05.10.2026 00:26, woertlich)
> "besieh mal das rotkäppchen, morgen will ich dass du die wirtschaft optimierst -holzfäller, apfelfarmen seasonen, steinochsenjoche hinzufügen wenn abführung zu langsam ist und erwartbar schlau davor. einheiten besser optimieren. angreiffen sinnvoller, angriffsarmeen sammeln. erweitern der wirtschaft - maximale eisen/stein/pech etc. sowie brotwrritschaft, bier, religion, positiven/negativen angsfaktor etc. mauern bauen lord schützen etc."
>
> "außerdem auch nahrung optimal verkaufne, momentan haben wir noch zu  viel äpfel dabei sollen versucht werden maximal viele sorten zu haben, außerdem fehlen noch hunter UND es fehlt noch steuern das wird besonders wichtig bei bier und besserer narhcungversorgung"

**Entschieden (Daniel 05.10. 00:53: "ja, morgen damit anfangen"): ZUERST Punkt 13, der Lord-Trupp** - ERLEDIGT 05.10. 18:37 (M18) - Schritt 0 ist eine Pruefung, die zugebaute Stellen wirklich erkennt (die Wegnetz-Pruefung ist widerlegt).

Als Liste (Reihenfolge noch offen, Daniel entscheidet morgen):
1. Holzfaeller optimieren (3 je Baum, Clusterung - siehe M14).
2. Apfelplantagen seasonen (Grundlage steht seit 05.10., `werkzeug/wirtschaft.py`).
3. Ochsenjoche am Steinbruch hinzufuegen, wenn das Abtragen zu langsam ist - und vorausschauend schon davor.
4. Einheiten besser optimieren.
5. Sinnvoller angreifen; Angriffsarmeen sammeln.
6. Wirtschaft erweitern: Eisen, Stein, Pech usw. bis zum Maximum.
7. Brotwirtschaft, Bier, Religion.
8. Angstfaktor positiv/negativ.
9. Mauern bauen, Lord schuetzen.
10. Nahrung optimal verkaufen - heute zu viele Aepfel; moeglichst viele Sorten (Beliebtheit).
11. Jaeger fehlen.
12. Steuern fehlen - besonders wichtig mit Bier und besserer Nahrungsversorgung.
13. Lord-Trupp (Daniel 05.10. 00:52, Regel im Spielwissen): nebenher pruefen, freie Raid-Assassinen gestapelt auf den Lord - 5 wenn er allein steht, ~10 normal, bei Bogenschuetzen und vielen Feinden mehr; zugebaut -> erst freilegen. Messgrundlage steht: Lord-Zeilen in der Konsole (Partie 9k: 3-11 Assassinen trafen ihn nebenbei, 150.000 -> 108.600).
14. **Startgeld wie in der Liga: 0 Gold** (Daniel 05.10. 00:55: "die Balance faengt eigentlich mit 0 Gold an und nicht mit 2-4k"). Unsere Testpartien starten mit ~3.930 Gold (Stand "M7-04 Mensch Grumpy T600") - alle bisherigen Ergebnisse (Assassinen-Anwerben!) haengen daran. Morgen: Startstand mit Liga-Bedingungen herstellen und die Eroeffnung neu rechnen.
15. Alle frueher angesprochenen offenen Punkte (Daniel 00:55: "die restlichen Punkte, die schonmal angesprochen wurden"): Bier, Jagd, Waffenwirtschaft, Pech, Brot, Essensvielfalt (Merkliste 04.10. 23:25); 3 Holzfaeller je Baum und Holzfaeller/Lager live umsetzen; Sammelpunkt (Spielbefehl 71); Steinbrueche und Eisen; Echtzeit ab Tempo 40 und hoeher (Auftrag 04.10. 21:54); zugebaute Gebaeude erkennen (Wegnetz-Pruefung widerlegt); Lager erweitern pruefen.
16. **SPAETER: echtes Selbstlernen** (Daniel 05.10. 00:57: "momentan ist das nur ein du machst Codeanpassungen - eigentlich sollte das Programm selbst durch tausende Partien besser werden, aber das spaeter"). Heute vorbereitet: Startwerte stehen als benannte Groessen (z. B. SICHER_FERN, STAPEL_AB, JE_GEBAEUDE) und jede Entscheidung schreibt ihre Messzeile (ZIELWAHL, MESSUNG, STAPEL) - daraus kann ein Lernlauf spaeter selbst Werte waehlen und bewerten (Belohnung z. B. zerstoerte Gebaeude je Verlust, Sieg-Tick).
