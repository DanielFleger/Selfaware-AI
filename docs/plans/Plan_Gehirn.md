# Plan: Das Gehirn (B-170)

Stand 08.11.2026. Nichts davon ist gebaut. Am Ende steht, was belegt, was Annahme und was offen ist.

## 1. Das Ziel

> Der Gegner soll so wenig wie möglich zum Spielen kommen, bei kurz- und langfristig größtem Gewinn und kleinstem Verlust für uns.
> (Daniel, 08.11.2026)

Eingerechnet werden Spielzeit, Truppen, Gegnerstärke, Einheiten, Bevölkerung und Ressourcen, für uns und Verbündete gegen alle Gegner.

**Das größte Ziel ist die Gewichtung:** ein Gespür dafür, wann sich was am meisten lohnt. Das haben sonst nur die besten Spieler. Steht sie, ist der Rest Härtung: wiederholte Tests gegen möglichst verschiedene Gegner und Strategien.

## 2. Wo wir am schlechtesten sind: Skalierung

Median aus 88 aufgezeichneten Partien, überwiegend gegen Nomaden:

| Takt | | Arbeiter | Soldaten | davon bis 30 Felder an der Burg | Gold |
|---|---|---|---|---|---|
| 10.000 | wir | 78 | 19 | 2 | 36 |
| | Gegner | 49 | 31 | 20 | nicht lesbar |
| 30.000 | wir | 84 | 42 | 10 | 74 |
| | Gegner | 38 | 36 | 23 | nicht lesbar |

- **Arbeiter haben wir genug.** Daraus wird aber zu wenig: Das Gold bleibt bis Takt 30.000 unter 100.
- **Die Burg steht leer.** Wir haben einen Bruchteil der Verteidiger des Gegners an der Burg.
- **Keine Burganlagen.** In den letzten 30 Partien stand am Ende kein Turm und kein Tor, nur Fallen. Wir spielen, wie Daniel sagt, ein Zeltdorf.
- **So brechen wir ein:** In den 4 verlorenen 1v1 gegen die eigene KI (beide Seiten aufgezeichnet) blieb der Verlierer bei 5 bis 34 Soldaten und 1 bis 13 Mann an der Burg, der Sieger hatte zuletzt 33 bis 101 Soldaten.

Gegen einen voll ausgebauten Gegner, der ständig raidet, fehlen Aufzeichnungen. Genau dort brechen wir laut Daniel sofort ein, deshalb steht das im Bauplan.

Skalierung (Burg, Wirtschaft, Verteidigungsanlagen) ist Kraris Gebiet, siehe Abschnitt 7. Das Gehirn liefert ihr die Mittel.

### Ausgangswert: Wirkung je Einheit (Schritt 1)

Gemessen mit `tools/analysis/wirkung_je_einheit.py`, Ergebnis in `data/research/wirkung_je_einheit.json`. Je 1.000 Takte einer eingesetzten Einheit:

| | Partien | Soldaten getötet je eigenem toten Soldaten | Soldaten und Arbeiter getötet | Gebäude zerstört | eigene Soldaten tot |
|---|---|---|---|---|---|
| SamurAI gegen KI | 60 | 0,80 | 0,068 | 0,088 | 0,037 |
| KI gegen SamurAI | 60 | 0,88 | 0,026 | 0,005 | 0,026 |
| Daniel gegen SamurAI | 1 | 4,2 | 0,175 | 0,049 | 0,027 |
| SamurAI gegen Daniel | 1 | 0,16 | 0,042 | 0,034 | 0,244 |

- Wir sind 2,6-mal tödlicher als die KI und zerstören 18-mal so viele Gebäude je Einheit, verlieren aber mehr Soldaten als wir töten.
- Die Assassinen stellen 43 % der eingesetzten Zeit, 86 % der Wirkung und 73 % unserer toten Soldaten.
- Speerträger und Bogenschützen stellen 28 % der Zeit und 2 % der Wirkung. Ob sie durch ihre Anwesenheit schützen, misst das nicht.

Grenzen: Die Gebäude sind nur nach Nähe zugeordnet. Getötete Arbeiter sind eine Untergrenze: In der Partie gegen Daniel sind 33 belegt, weitere 280 verschwanden unverletzt, durch Massenbeschuss, verlorene Hütten oder Abwanderung. Gegen Daniel gibt es nur eine Partie mit einem alten Stand.

## 3. Unsere Stärke

| | KI im Spiel | Guter Mensch | SamurAI |
|---|---|---|---|
| Truppen auf Raid, Verteidigung, Angriff | fester Prozentwert der kommenden Truppen | nach Gefühl, oft auf eine Strategie festgelegt | frei, jederzeit, Einheit für Einheit |
| Einheiten umsetzen | kaum | mit Aufmerksamkeit bezahlt | beliebig, auch mitten im Einsatz |
| Angreifen | sammeln, frontal stürmen | Schwerpunkte | in Schüben, an kritischen Stellen, geknubbelt |
| Ausweichen | nein | selten | pixelgenau |
| Mehrere Dinge zugleich | getrennte Abläufe | begrenzt | Raid, Verteidigung und Angriff gleichzeitig |

**Daraus folgt die Grundregel: So wenig Einheiten wie möglich einsetzen, damit möglichst viel bewirken, alles Übrige fließt in die Skalierung.** Weil wir jede Einheit besser nutzen können, brauchen wir weniger davon. Das muss sich laufend mit der Lage ändern. Macht Verteidigen keinen Sinn, gehen die Einheiten woandershin, und das gilt für jeden Fall.

## 4. Nichts hat einen festen Wert

Listen wie „Kornspeicher vor Markt" gibt es nicht. Auch Einheiten zählen nicht nach Menge: 100 Ritter sind nichts wert, wenn sie falsch stehen.

- Der Bauer mit Last ist mehr wert als der ohne, der Ochse mit 7 Steinen mehr als der leere.
- Von zwei Holzfällerhütten zählt die, deren Holz früher im Lager wäre. Ist ihr Holzfäller gerade gestorben, ist es vielleicht die andere.
- 18 Holz sind nichts wert, wenn der Gegner Überfluss hat, und viel, wenn genau dieses Holz seine neue Kaserne bezahlt.
- Bringt unser Gold in Verteidigern mehr, geht es dorthin.

Es gibt nur eine Rechnung: **Was wäre mit dieser Handlung, was wäre ohne sie?** Für beide Seiten, bis zu einem Zeithorizont. `learning/kausal.py` rechnet schon so, aber nur für den eigenen Bau und nur in Gold.

## 5. Die Gewichtung

### 5.1 Was sie entscheidet

- **Produktion:** Wohin fließt das Gold: Skalierung, Verteidiger, Raid-Einheiten, Angriff?
- **Einsatz:** Was tut jede vorhandene Einheit gerade?

Beides ist kein eingestellter Prozentwert, sondern das Ergebnis der Rechnung, und es ändert sich mit der Lage.

### 5.2 Der kleinste Einsatz

Für jede Aufgabe wird zuerst gefragt: **Wie wenig reicht?** Vorhanden: `zuweisung.kleinste_gruppe`.

1. Wie wenig reicht, um nicht zu verlieren (Lord, Kornspeicher, wichtigste Ketten)?
2. Mit wie wenig Einheiten hindern wir den Gegner am stärksten am Wachsen?
3. Alles Übrige geht in die Skalierung.

Der Maßstab für gute Nutzung ist die **Wirkung je Einheit**: Was hat eine eingesetzte Einheit in ihrer Zeit beim Gegner bewirkt, und was kostete sie uns? Das wird gegen die KI-Gegner gemessen.

### 5.3 Die Bewertung

**Vorsprung = Lage (wir und Verbündete) minus Lage (Gegner)**, für drei Zeiträume:

| Zeitraum | Takte | Was dort zählt |
|---|---|---|
| kurz | bis 500 | Wer gewinnt das Gefecht in dieser Aufstellung? |
| mittel | bis 5.000 | Was kann an Truppen, Waffen und Gold entstehen? |
| lang | bis Partieende | Wachstum, Bevölkerung, Beliebtheit, Burg, Lord |

Zur Lage gehören:

- **Kampfkraft nach Einsatz:** Wer steht wo und wen kann er tatsächlich schlagen, nach Paarungen (S1, S5, L109). Nicht die Summe der Leben.
- **Nachschub:** Hängt an Kaserne oder Söldnerposten, Waffen, Bauern und Gold. Fehlt ein Glied, ist er null.
- **Wachstum, Vorräte, Lord und Spielzeit:** Früh zählt Wachstum, spät das, was steht. Ein Gegner ohne Lord zählt nicht mehr.

### 5.4 Die Vorausrechnung

Drei einfache Modelle statt einer Spielkopie:

- **Kampf:** `gefecht.simuliere` mit gemessenen Schäden und Lauftempi, dazu die Geschossdaten. Die Vorhersage für 90 Takte vom anderen PC, sobald sie nur noch Sichtbares liest.
- **Wirtschaftsketten** je Spieler: Quelle, Arbeiter, Träger oder Ochse, Lager, Werkstatt, Waffenkammer, Kaserne. Jede Last zählt mit ihrem Weg (Holzfäller 18 Holz je Gang laut `kausal.py`, Ochse 6 bis 7 Steine, L71). Ein Toter wird nur ersetzt, wenn Bauern am Feuer warten: Das Spiel teilt einmal in 200 Takten zu und nimmt den ersten nach Nummer, nicht den nächsten.
- **Bevölkerung:** Nahrung, Beliebtheit, Zuzug und Abwanderung, davon Arbeiter, Rekruten und Steuern. Darüber wirkt ein zerstörter Kornspeicher, obwohl er nur 5 Holz kostet.

Die Ketten werden zuerst an der eigenen Seite geprüft. Beim Gegner laufen sie auf Schätzwerten.

### 5.5 Gegenrechnen

Jedes knappe Gut (Gold, Holz, Waffen, Bauern, freie Einheiten, Befehle) zählt so viel wie seine beste andere Verwendung. Das gilt auch beim Gegner: Waffen ohne Kaserne sind im Moment fast nichts wert.

**Chirurgisch** heißt: das Glied treffen, ohne das seine Kette steht. Dort ist der Unterschied zwischen „mit" und „ohne" am größten. Zum Deadlock kommt es, wenn er ein Glied weder hat noch ersetzen kann.

### 5.6 Wie das Gespür entsteht

1. **Von Hand gesetzte Regler** auf der Rechnung oben ergeben einen ersten Stand.
2. **Gelernte Regler:** Partien entscheiden, welche Gewichte besser sind. Dazu gehört auch die Risikofreude je Aufgabe und Einheitenart.
3. **Gelernte Bewertung:** Aus sehr vielen Lagen und ihrem Ausgang lernt das Gehirn, was eine Lage wert ist, ohne alles durchzurechnen. Das ist die Intuition.

Jede Entscheidung wird mit ihrer Erwartung protokolliert und nachgemessen.

**Härtung:** Eine Liga aus möglichst verschiedenen Gegnern (alle KIs, eigene ältere Fassungen, verschiedene Strategien gegeneinander, Karten, Plätze, Gold). Der Durchsatz begrenzt das: Bei Tempo 200 dauern 40.000 Takte rund 3,4 Minuten. Bei Tempo 825 wären es 48 Sekunden, das ist aber noch nicht gefahren.

## 6. Einsatz der Einheiten

### 6.1 Vorhaben und Rollen

Alle paar hundert Takte entsteht eine Liste von Vorhaben, zum Beispiel: Arbeiter mit Last an Strecke X töten, Kaserne anzünden, Gegner A kaltstellen und B hinhalten, Lord stapeln und töten, Heimat halten. Jedes hat Wert, Bedarf, Ankunftszeit und Risiko.

Rollen sind das Ergebnis, so steht es schon im Plan Einheitenlenker:

- Jede Einheit ist ständig Kandidat für jedes Vorhaben. Raids werden laufend mitgerechnet: **Reicht es gestapelt zum Kill, mit wenig Schaden, möglichst schnell?**
- Wechsel nur bei deutlich besserem Angebot, sonst pendelt die Truppe, und jeder neue Befehl startet die Wegsuche neu.
- Der Kern führt die Besitzliste mit Leihe, bisher nur für Assassinen. Sie muss für alle gelten.
- **Opfern** und **Ablenken** sind kein Sonderfall: Einheiten dürfen fallen oder binden, wenn der Gewinn insgesamt größer ist.

### 6.2 Pixelgenau statt frontal

- **In Schüben** kommen statt gesammelt zu stürmen.
- **Knubbeln an kritischen Punkten** (bis 54 auf einem Feld, S15, nach R5 erlaubt). Das macht aber anfällig für Steine und Feuer, die Kampfrechnung kennt beides.
- **Kritische Stellen angreifen**, die die Rechnung aus 5.5 nennt.
- **Sammeln oder sofort:** Beide Wege werden gerechnet. Warten kostet das, was der Gegner in der Zeit tut, und bringt, dass langsame Einheiten mit ankommen (Lauftempi L80, Lauf S).
- **Alles gleichzeitig:** Raid, Verteidigung und Angriff laufen nebeneinander, Einheiten wechseln bei Bedarf.

### 6.3 Ausweichen

Gefahr ist, was nach dem Ausweichen noch trifft. Gemessen am 08.11. (Schritt 4, B-173, `data/research/auge_plan/ausweichen_20261108/Ergebnis_Ausweichen.md`): Sklave mit dem Befehl eines Spielers, Bogenschützen, Anteil der Pfeile, die treffen, wenn jeder Takt ein Schuss sein könnte:

| Laufweg | 8 Felder | 12 Felder | 16 Felder | Felder je 1.000 Takte |
|---|---|---|---|---|
| gerade auf den Schützen zu und zurück | 92 % | 86 % | 78 % | 81 |
| gerade quer | 89 % | 58 % | 35 % | 83 |
| Zickzack quer, Wechsel je Feld | 55 % | 33 % | 16 % | 79 |
| Zickzack auf den Schützen zu, Wechsel je 2 Felder | 51 % | 20 % | 6 % | 80 |
| Zickzack auf den Schützen zu, Wechsel je Feld | 25 % | 2 % | 1 % | 78 |

- Das Spiel zielt auf die Feldmitte plus Vorhalt in Blickrichtung, bei einer vom Spieler befohlenen Einheit doppelt so weit wie bei einer gehenden. Wer nach dem Schuss die Richtung wechselt, steht woanders.
- Zickzack kostet fast keine Strecke (94 bis 97 %), weil ein schräges Feld genauso lang dauert wie ein gerades.
- **Entscheidung (Daniel 08.11.2026): der Wert, der am besten ausweicht, also Richtungswechsel je Feld.** Schneller geht nicht: Eine Einheit liest ein neues Ziel erst in der Feldmitte.
- **Eingebaut (B-174, B-175):** Der Rust-Kern führt den Zickzack je Feld, Schalter `zickzack=ja`, aus ist der Standard. Er wirkt beim Vorstoß (`vorstoss=ja`) beim Vorrücken und Abziehen und beim Brandtrupp auf dem Weg zum Gebäude.
- **Ganze Gruppen, gemessen im Gefecht** (`data/research/auge_plan/zickzack_20261108/Ergebnis_Zickzack.md`, 8 Sklaven, 8 Bogenschützen, Treffer ab 12 Feldern je möglichem Schusstakt): gerade 87 %, Zickzack dicht 38 bis 61 %, Zickzack breit 4,5 %, bei gleicher Strecke. Breit heißt: bis zu 8 Plätze in 2 Reihen, 5 Felder Abstand, je Platz ein eigener Befehl. Dicht fängt der Nachbar den verfehlten Pfeil: Quer zur Schussrichtung liegen 2 bis 3 Felder neben dem Ziel die gefährlichen Stellen (bis 23 %), ab 5 Feldern sind es unter 2 %.
- Der Preis ist ein Befehl je Platz und Feld. 8 Einzelbefehle je Feld kamen alle rechtzeitig, ein neunter daneben in 18 % statt 6 % der Fälle zu spät.
- **Brandtrupp, gemessen im Gefecht:** 8 Sklaven je Muster an 8 Bogenschützen vorbei, die seitlich stehen: bis zur Ankunft 6,0 Treffer je Sklave gerade, 2,6 im Zickzack, tot wären 8 von 8 gegen 5 von 8, gleich schnell. Schützen von der Seite sind der schlechtere Fall für den Zickzack.
- Noch nicht im Zickzack: Nahkämpfer. Schützen im Vorstoß bleiben bei 38 Feldern stehen, beim Vorrücken trifft sie der Zickzack selten unter Beschuss.
- Der Preis ist ein Befehl je Gruppe und Feld. Bei 12 Takten je Feld reicht der eine Gruppenbefehl je Takt (S57) für höchstens 12 Gruppen.
- Nicht gemessen: andere Schützen und Läufer, Steine und Feuer, Wechsel erst beim gesehenen Schuss.
- Den Abschuss sehen wir am Animationsbild (R4), fliegende Pfeile liefert der Kern jetzt jeden Takt.

### 6.4 Die Grenzen

| Ebene | Wie oft (Vorschlag) | Wo |
|---|---|---|
| Lagebild | jeden Takt | Kern |
| Vorausrechnung, Vorhaben, Gewichtung | alle 100 bis 500 Takte | Python |
| Rollen | alle 20 bis 100 Takte | erst Python, dann Kern |
| Einheit, Reflex | alle 1 bis 10 Takte, jeden Takt | Kern |

Python packt bei Tempo 200 nur rund 1.400 Einheiten rechtzeitig aus (gemessen, offline). Außerdem kommt nur ein Gruppenbefehl je Takt durch (S57). Befehle werden deshalb wie jedes knappe Gut nach Wert vergeben: Für einen Richtungswechsel je Feld reicht das für 12 bis 16 Gruppen gleichzeitig.

## 7. Skalierung (Krari)

Burg bauen und Verteidigung sind etwas für Krari und andere, Daniel hilft dort nur sporadisch. Bei frühen Raids und beim Knubbeln hilft Daniel gerne mit (Daniel, 08.11.2026). Das Gehirn legt für die Skalierung nur die Schnittstelle fest:

- Es meldet laufend, **wie wenig Einheiten und Gold es gerade braucht**. Der Rest steht der Skalierung zu.
- Es meldet, wo die Burg gerade gefährdet ist.
- Es bekommt zurück, was gebaut wird und wann es steht.

Für Krari die Ausgangswerte aus Abschnitt 2: kein Turm, kein Tor, kaum Gold, leere Burg. Offen ist, wie weit das Gehirn in Burgbau eingreift.

## 8. Fairness

Das Gehirn rechnet nur mit dem, was ein Mensch sehen oder wissen kann (`docs/FAIRNESS.md`).

- Fremde Vorräte werden geschätzt (F4), fremde Trupps aus gemeinsamer Bewegung erahnt (F10). Unbekannt ist nicht null.
- Wie die Gegner-KI plant und ob sie wieder aufbaut, lernen wir nur aus beobachteten Partien (R3, F5).
- Die Sperre muss vor dem ersten fairen Lauf im Code sitzen. Bisher gehen sieben alte Felder ungefiltert an Python.

**Zu entscheiden:** Was eine fremde Einheit trägt, ist heute gesperrt (`resourceToDeposit`). Ein Spieler sieht die Last aber am Bild. Vorschlag: für Gegner freigeben (F9).

## 9. Was die Feldliste dadurch ändert

- **Fehlt bei Python:** Last und Arbeitsplatz der Einheiten, Besetzung, Fortschritt und Waren der Gebäude, Beliebtheit, Bauern am Feuer, Heeresgröße. Das kann der Kern langsamer und gebündelt liefern.
- **Kann raus aus „jeden Takt":** Einheitenziel `target`, Getötet-Merker, Trupp-Ziel x und y (Lauf vom 08.11.).

## 10. Bauplan

Jeder Schritt hat eine Probe, die scheitern kann.

| Schritt | Was | Probe |
|---|---|---|
| 1 | Wirkung je Einheit aus den Aufzeichnungen messen, für uns und die KI-Gegner (erledigt, siehe Abschnitt 2) | Ausgangswert steht, an zwei Partien von Hand nachgerechnet: tote eigene Assassinen laut Werkzeug gegen Todesakten 21 zu 21 in beiden Partien |
| 2 | Partien gegen voll ausgebaute, ständig raidende Gegner | Der Einbruch lässt sich wiederholen und ist in Zahlen beschrieben |
| 3 | Laufende Rollen und kleinster Einsatz, zuerst Sklaven und Assassinen, hinter einem Schalter | Gleiche Partien mit und ohne: mehr Wirkung je Einheit, weniger Einheiten gebunden |
| 4 | Messlauf Ausweichen im Editor: gerade, schräg, Zickzack je Abstand (erledigt, siehe Abschnitt 6.3) | Zickzack muss Treffer spürbar senken, sonst fliegt es raus. Gemessen: ab 12 Feldern 19 bis 84 Punkte weniger bei 94 bis 97 % der Strecke |
| 5 | Schübe, Knubbeln und kritische Stellen | Schlägt frontales Stürmen in gleichen Gefechten |
| 6 | Sperre im Code und fehlende Felder | Fremdes kommt nicht an, Probe wie am 08.11. |
| 7 | Gewichtung: Produktion und Einsatz als Regler, Wirtschaftsketten beider Seiten | Vorhersage des eigenen Bestands weicht um höchstens 20 % ab, frei gewordene Mittel fließen wirklich in Skalierung |
| 8 | Liga und gelernte Regler | Bessere Regler gewinnen auch gegen Gegner, gegen die nicht gelernt wurde |
| 9 | Ziele Z1 bis Z3 messen | 2v2, 1v2, 1v7 |

Parallel: Skalierung (Krari). Vorschlag: Das ersetzt P6 und P8 der bisherigen Reihenfolge, P9 und P10 gehen in Schritt 8 auf.

## 11. Was belegt ist und was nicht

**Belegt:** Die Zahlen aus Abschnitt 2. Schaden, Lauftempo und Reichweite sind gemessen (S1, S5, S9, L80, L109). Pfeilflug 5,75 Achtelfelder je Takt, gerade und schräg gleich schnell (Lauf S). Ein Gruppenbefehl je Takt (S57). Ausweichen gegen Bogenschützen (Schritt 4, Abschnitt 6.3). Die Ketten von Holzfäller, Ochse und Bauernzuteilung stehen im Spielcode, die Raten sind gemessen (L71). Die neuen Felder kommen richtig an (Lauf 08.11.).

**Annahme:**
- Dass bessere Nutzung wirklich Mittel für die Skalierung freimacht, ist die Grundthese und noch unbewiesen. Schritt 1 und 3 prüfen sie.
- Mauern sind in den Aufzeichnungen nicht erfasst, nur Türme, Tore und Fallen. „Keine Burganlagen" gilt für diese.
- Die Takte je Ebene sind Vorschläge.

**Offen:**
- Die Rechnung nimmt anfangs an, dass der Gegner so weitermacht. Für gute Ablenkung reicht das nicht auf Dauer.
- Die Rechenzeit der Ketten ist nicht gemessen.
- Die Daten stammen fast nur aus Partien gegen Nomaden und gegen die eigene KI.
