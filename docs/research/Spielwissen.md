# Spielwissen - Notizzettel fuer die Selfaware-KI

Daniels Tipps (Quelle in Klammern) und spaeter das, was die KI selbst als wirksam gemessen hat.
Jede Zeile ist eine Regel, die die KI pruefen und gewichten soll - nichts davon ist "bewiesen",
bis eine Messung es bestaetigt (Marke dahinter).

## Ziel
- Gegen das Rotkaeppchen gewinnen, unsere KI auf dem Menschenplatz (Daniel, 04.10.2026).

## Regeln fuer unsere KI als Spieler (Daniel, 04.10.2026, 19:56)
- Keine kostenlosen Mauern - Mauern und alle Gebaeude kosten wie beim Menschen. Gebaut wird nur ueber den Spielbefehl (mit Kostenpruefung des Spiels), nie durch direktes Schreiben von Rohstoffen oder Bauten.
- Handel: die KI darf beliebig viel von einer Ware auf einmal kaufen oder verkaufen (Menschen nur in Schritten von mindestens 5) - zum Marktpreis, ueber den Marktplatz.
- Keine anderen Schummeleien (Gold/Waren setzen, Leben aendern, Einheiten wandeln) im echten Spiel - diese Befehle bleiben Werkzeuge fuer Tests und Trainingslagen.

## Geld
- Liga-Bedingung (Daniel 05.10. 00:55): Start mit **0 Gold**, nicht mit 2.000-4.000. Unsere bisherigen Testpartien hatten ~3.930 Gold - ihre Ergebnisse gelten nur fuer diesen Start.
- Gemessen 05.10.: Liga-Start = 0 Gold, 150 Holz, je 15 Brot/Kaese/Fleisch/Aepfel (erst mit Kornspeicher sichtbar). Steuern bringen am Anfang fast nichts (10 Leute: hoechstens 10 Gold in 600 Ticks bei Stufe 11, Beliebtheit faellt dabei stark). Apfelplantage 15 Gold, Jaegerhuette 60 Gold, Soeldnerlager 120 Gold.
- **Verkaufspreise Liga gemessen 05.10.** (ein Verkauf = 5 Nahrung bzw. 20 Holz; `daten/verkaufspreise_liga.txt`): Kaese 6, Brot 4, Aepfel 3, Fleisch 1, Holz 1 Gold je Stueck. Die Start-Nahrung (je 15) ist bis zu 210 Gold wert - **Nahrung verkaufen ist am Anfang die Goldquelle**, nicht Holz und nicht Steuern (Daniel 05.10. 18:48: "weisst du wie viel Gold du bekommst, wenn du Nahrung verkaufst?").
- Immer wissen: wie viel Gold da ist, was hereinkommt, was jede Sache kostet. Passend sparen, genau ausgeben. (Daniel 04.10.)
- Moeglichst viel Geld in Wirtschaft stecken - sie hat den hoechsten Hebel auf Geld und damit Waffen und Truppen. (Daniel 04.10.)
- Beliebtheit erlaubt Steuern = Geld. Rohstoffe verkaufen bringt ebenfalls Geld. (Daniel 04.10.)
- Kosten kommen aus der Balance (Team-Liga): Baukosten int[110][5] (Holz, Stein, Eisen, Pech, Gold) im Spiel bei 0x01124CF4, Index = Gebaeudetyp (VillageStudio lib/kosten.json). (abgelesen)
- **Holz und Stein werden nicht gekauft** (Daniel 05.10. 19:44: "du musst Holz nicht kaufen, in den meisten Faellen baust du ja Holzfaeller, damit du nicht Holz kaufen musst"). Verbautes Holz/Stein kostet darum nur den entgangenen Verkauf: bewertet zum Verkaufspreis (Holz 1, Stein 5), nie zum Kaufpreis.
- **Ochsenjoche frueh, nicht erst bei Bedarf** (Daniel 05.10. 21:05): sobald der erste Ochse beladen zum Lager loszieht, sofort das zweite Joch; sind dann immer noch mehr als 8 neue Steine am Haufen, ein weiteres - keine Obergrenze je Steinbruch.
- **Stein bis auf den Bedarf der geplanten Eisenminen verkaufen** (Daniel 05.10. 19:44). Gemessen 05.10. 19:52 in der Baukostentabelle (Liga): Eisenmine = 20 Holz + **6 Stein**; Holzfaeller, Huette, Ochsenjoch, Kornspeicher je 5 Holz; Steinbruch 25 Holz; Jaeger 3 Holz + 60 Gold; Apfelplantage 3 Holz + 15 Gold; Soeldnerposten 120 Gold; Lager und Markt 0.
- **Ertrag im Liga-Spiel gemessen** (Ertragsmesser, Partien 9u/9v 05.10., je 1.000 Ticks je besetztem Betrieb, auf Messweg umgerechnet): Eisenmine 0,55-0,58 Eisen @ 31 Felder (= ~15 Gold), **Anlauf ~6.500-6.700 Ticks** vom Bau bis zum ersten Eisen; Steinbruch+Ochse 6,5-6,6 Stein @ 8 (= ~33 Gold); Apfelplantage 3,3-3,7 @ 5, Anlauf ~2.300-2.500; Jaeger 3,5-3,8 Fleisch @ 53; Holzfaeller ~5,6 Holz im Schnitt aller Holzfaeller - kaum abhaengig vom Weg. Eine Eisenmine lohnt sich in einer Partie nur, wenn danach noch Anlauf + ~3.500 Ticks bleiben.

## Beliebtheit und Essen
- **Beliebtheit ist das Wichtigste.** Unter 95 sinkt die Rate, mit der neue Bauern kommen; bei 50 kommen fast keine mehr; unter 50 gehen Leute AUS dem Dorf. (Daniel 04.10., 19:57)
- Kornspeicher nicht vergessen. (Daniel 04.10., 19:57)
  - Gemessen 04.10.: Ohne Kornspeicher kann man kein Essen kaufen (Kauf braucht Lagerplatz). Kornspeicher (5 Holz) + 50 Aepfel gekauft (~8 Gold je Apfel) -> Beliebtheit 93,25 -> ueber 95 nach ~600 Ticks, 100 nach ~1500 Ticks. **Essen kaufen ist der schnellste Hebel auf die Beliebtheit am Anfang.**
- Kornspeicher haelt das Essen und ist damit sehr wichtig fuer die Beliebtheit. (Daniel 04.10.)
- Beliebtheit vor allem ueber Bier. (Daniel 04.10.)
- Essen anfangs ueber Aepfel. Jagd nur, wenn Wild (Rehe) da ist - erkennen, sonst kein Holz fuer eine Jaegerhuette ausgeben. Jaeger etwa einen Kathedralenabstand vom Wild. (Daniel 04.10.)
  - Erkennbar: Rehe sind Einheitentyp 44 (UT_ANTELOPESHDEER), Besitzer 0. (gemessen 04.10.: 134 bzw. 200 auf Grumpy)

## Bauen
- **Nie blind starten** (Daniel 05.10. 18:55: "du musst auch schauen, wo dein Keep steht"): Vor jeder Eroeffnung den eigenen Bergfried im Spiel finden (Gebaeudetyp 41, Eingang im Datensatz +0x112/+0x114) und alles um ihn herum planen; keine festen Koordinaten. Werkzeug: `karten_holen.py <Spielstand> <Kurz>` holt Bergfried, Baeume, Rohstoff- und Platzkarten, dann `eroeffnung.py start=<Kurz>`. Gemessen: im Liga-Start steht unser Bergfried bei (141,269), Rotkaeppchens bei (227,289) - im alten Start war es (165,111).
- Sicherheit beim Planen (Daniel 04.10.: "je nach Metrik, z. B. wie nah der Gegner ist"): nur Stellen und Baeume, die naeher an unserem Bergfried liegen als an einem feindlichen.
- Moeglichst nah am Vorratslager bauen. (Daniel 04.10.)
- Ausnahmen, deren Arbeiter erst zur Produktion laufen: Holzfaeller mit dem Eingang direkt neben einem Baum (sie holen erst drei Holzscheite); Ochsenjoche direkt neben den Steinbruch (der Ochse bringt dann 12 Stein zum Lager). (Daniel 04.10.)
- **Gebaeude lassen sich nicht drehen** (keine Ausnahme). Den Ausgang/Eingang kann man nur indirekt lenken: den ueblichen Platz zustellen oder dort bauen, wo etwas anderes ihn blockiert - z. B. beim Steinbruch, wohin der Ochse den Stein bringt; jede Produktion (Baecker usw.) laesst sich ueber Nachbargebaeude/Gelaende am Eingang beeinflussen - aber nur fein abgestimmt. (Daniel 04.10., 20:04)
- Abreissen und naeher an Rohstoffen neu bauen (z. B. wenn das Holz in der Naehe weg ist) lohnt erst im Mittel-/Endspiel, dann aber richtig. (Daniel 04.10.)
- Gebaeude, die nicht fuer die Wirtschaft wichtig sind, ruhig weiter weg bauen (z. B. Markt - den kann man ueberall bauen); das spart Platz am Lager. Der Kornspeicher kann auch weiter weg stehen: naeher am Gruenland hilft bei Aepfeln (die Apfelbauern liefern direkt in den Kornspeicher); spaeter bei Brot naeher an Lager und Baeckereien, von denen das Essen kommt. (Daniel 04.10., 20:13)
- Farmen brauchen Gruenland: messen, wo es ist; daraus rechnen, wie viele Farmen maximal und platzsparend moeglichst nah an Bergfried/Kornspeicher gehen. (Daniel 04.10., 20:13)
  - Gemessen/abgelesen 04.10.: Jedes Feld der Farm muss fruchtbar sein (Gras, dichtes oder duennes Gestruepp) und mindestens 50 der Felder Gruenland (Gras/dichtes Gestruepp). Groessen laut gebaeude.json: Weizen 9x9, Hopfen 9x9, Apfel 10x10, Kuehe 10x10 (Apfel im Spiel gemessen). Die Bau-Stelle ist die obere linke Ecke (Apfel gemessen).
  - Farmen duerfen sich lueckenlos beruehren (9 von 9 gebaut, 04.10.).
  - Baeume, Hang, Wasser und **jede stehende Einheit** (ausser Huehnern) sperren den Bau - auch auf dem Feldteil. Nur in der Definitive Edition darf man ueber Arbeiter bauen. (gemessen + Daniel 04.10., 20:44)
  - Apfelplantage: erste Aepfel gut 2.000 Ticks nach dem Bau; 9 Plantagen fuellten den Kornspeicher in 4.000 Ticks von 14 auf 93 Aepfel und hielten die Beliebtheit bei 100 (Grumpy, 04.10.).
  - 9er-Farmen (Weizen, Hopfen) und 10er-Farmen (Apfel, Kuehe) duerfen lueckenlos nebeneinander (13 von 13 gebaut, 04.10.). 9er-Farmen passen in mehr Luecken: Umkreis 50 um den Kornspeicher auf Grumpy 14 Farmen gemischt statt 10 Apfelplantagen.
  - Hopfen braucht viel laenger als Aepfel: erster Hopfen gut 7.000 Ticks nach dem Bau (Aepfel gut 2.000). Fuer Bier frueh anfangen. (gemessen 04.10., 3 Hopfenfarmen)
  - Werkzeug fuer jede Karte: Platzkarten holen (je < 1 s), dann `farmen_mischen.py` - beste Mischung nachweislich in unter 3 s, auch fuer die ganze Karte.
  - Auf Grumpy liegt das naechste Gruenland 37 Felder vom Kornspeicher am Bergfried - bis 30 Felder passt keine einzige Farm. Darum Kornspeicher naeher ans Gruenland (Daniels Tipp, durch die Rechnung bestaetigt).
- **Lager verlegen (Daniel 04.10., 21:58/22:04):** Das Lager steht beim Start automatisch. Erst die Startrohstoffe (150 Holz) moeglichst wirksam verbauen, dann das leere Lager abreissen (kostet dann nichts) und neu setzen - zuerst moeglichst nah am Holz, spaeter naeher an Stein/Eisen, bis es fest steht; dort die Wirtschaft bauen. Grund: Holz kaufen ist viel teurer als es zu machen, und beim Optimieren zaehlt jedes Gold.
  - Gemessen 04.10.: Abreissen vernichtet alles im Lager (150 Holz -> 0; Gold bleibt, es liegt nicht im Lager). Ohne Lager darf das erste neue ueberall stehen (47.019 Plaetze) und kommt als Block aus 4 Teilen; jedes weitere Lagerteil und jeder weitere Kornspeicher muss am vorhandenen anliegen. Lagerteile kosten nichts.
  - Gemessen 04.10.: Holz verkaufen 1 Gold je Stueck, kaufen 3 Gold je Stueck. Verkaufen-Abreissen-Zurueckkaufen kostete 88 Gold und 70 Holz - darum lieber erst verbauen.
- **Lager fasst nicht unendlich (Daniel 04.10., 22:17):** Jeder Lagerplatz nimmt je Rohstoff hoechstens eine Menge auf (Holz ~48); jeder Rohstoff braucht eigene Plaetze (150 Holz = 3 x 48 + 6). Ist das Lager voll, wenn ein Traeger abliefern will, bleibt er stehen; wird es voll, WAEHREND er unterwegs ist, ist die Ware weg. Kniff: Plaetze mit einem Rohstoff vollmachen und anderswo einen neuen setzen - neue Plaetze muessen anliegen, also Kette bauen und Rest abreissen; hoechstens etwa 8 neue, wenn alle voll sind.
  - **Lagerteile (gemessen 06.10. 19:58, Tipp Daniel):** Jedes Lagerteil hat im Gebaeude-Datensatz (`0xF98520 + 0x14 + nr*0x32C`) die Menge `+0x184`, die Grenze `+0x188` (48) und die Warenart `+0x18C` (2 Holz, 4 Stein). Gemessen: Teile 6/7/8/9 = Holz 13 + 48, Stein 17 + 2 - Summen gleich dem Vorrat (61 Holz, 19 Stein). Das Spiel verteilt eine Ware ungleich auf mehrere Teile (2 Stein blockieren ein ganzes Teil). Sind alle Teile belegt, scheitert jeder Kauf einer neuen Warenart (Eisen) und jeder Kauf einer Ware, deren Teile voll sind (Holz bei 48 + 48) - Gold bleibt gleich, keine Fehlermeldung.
- Gemessen 04.10.: 4 Lagerteile fassen 190 Holz (Kauf in 5er-Schritten; ~48 je Teil). Sind alle Teile mit Holz belegt, passt kein Stein mehr. Ein neues Lager (anliegend) kommt als 4er-Block und fasst weitere 190 Holz. Holz kaufen ~3 Gold je Stueck.
- **Abriss gibt die Haelfte zurueck, abgerundet (Daniel 06.10. 20:06/20:11; gemessen 06.10. 20:12):** Der Abriss-Knopf
  schickt 50 %, je Ware Kosten x 50 / 100 in ganzen Zahlen, ohne Anteil fuer den Zustand. Bei 3 kommt 1 zurueck, bei 15 -> 7;
  ein Rest wird nicht gemerkt (zwei Gerbereien nacheinander je 7/1/37). Kein Lagerplatz fuer die Ware -> Rueckgabe weg
  (nur Code). Torhaus/Turm neu statt reparieren (Daniel): kleines Torhaus 15 Stein -> 7 zurueck.
- **Baeume (gemessen 04.10.):** Faellbar sind nur die Arten 1-4. Ausgewachsen 9 Einheiten (Baum +120), jung 1-4; Arten 5-19 haben 0 (Straeucher). Ein Holzfaeller nimmt 3 Einheiten je Gang und liefert 18 Holz -> etwa 54 Holz je grossem Baum (abgeleitet aus 2 Gaengen). Bei 0 verschwindet der Baum. Darum rechnen: wann lohnt der Holzfaeller noch, wann versetzen oder abreissen (Daniel 22:12).
- **Lager erst bei der ersten Lieferung (Daniel 22:49):** Ein Lager zu frueh zu bauen kostet - Arbeiter werden beim Ueberqueren langsamer. Maximal optimiert: das Lager (und jeden Anbau) genau dann setzen, wenn der erste Traeger abliefern WILL (sich auf den Weg zum Lager macht, Arbeiterzustand 8) - steht dann noch keins, kann er nicht abliefern (Daniel 22:51). Dafuer die Lieferzeitpunkte der Traeger vorhersagen.
- **Welche Baeume der Holzfaeller nimmt (abgelesen 04.10., findTree 0x004F3B90):** nur Zustand 2, Stufe < 4 und Holz (+120) > 0, dazu erreichbar; davon der naechste. Baeume in Stufe 4 werden uebersprungen - darum lief ein Holzfaeller am neuen Lager an vier grossen Baeumen vorbei "nach oben" (Daniels Beobachtung 22:34). Grumpy-Start: 351 faellbare Baeume.
- **Mehrere Holzfaeller um einen Baum (Daniel 22:35):** ein Baum gibt bis zu 3 Lieferungen (passt zur Messung: 9 Einheiten, 3 je Gang). Drei Huetten dicht um einen Baum sind besser als verstreut.
- **Drei Holzfaeller je Baum (Daniel 23:23):** mit drei Huetten um einen Baum faellt er am schnellsten (passt zu 9 Einheiten = 3 Lieferungen). Im Eroeffnungsplaner noch nicht gezielt umgesetzt (dort nur "Baeume teilen") - naechster Umbau.
- **Rote Zeichen ueber Gebaeuden** zu Spielbeginn kommen von der Pause (Daniel 23:23) - keine fehlenden Arbeiter (gemessen: alle 24 Betriebe besetzt). Spiel nach dem Start in festem Tempo laufen lassen.
- **Apfelplantagen-Kniff (Daniel 22:36, nicht gemessen):** Plantagen direkt nebeneinander genau dann setzen, wenn eine gerade vom Fruehling in den Sommer wechselt - dann holen sie sich gegenseitig Aepfel, fast doppelt so produktiv. Braucht: Jahreszeit je Plantage auslesen.
- Huette: 5 Holz, +8 Wohnplaetze (gemessen: 10 -> 18; 450 Ticks spaeter 18 Leute). Bergfried allein: 10 Plaetze.
- Logisch noetige Gebaeude fuer Truppen kennen (Kaserne, Waffenwerkstaetten, Waffenkammer). (Daniel 04.10.)

## Angriff
- **Stapeln ist der Schaden** (Daniel 05.10. 21:05): je gestapelter die Assassinen auf einmal ankommen, desto wirksamer - ihr Schaden addiert sich, der Lord macht viel Schaden, aber immer nur an EINER Einheit. 5 koennen mit maximalem Mikromanagement einen Lord toeten (Schwache zurueck, sofort wieder drauf), mit 20 braucht es das nicht. Darum zuerst 20 auf einmal, dann aus den Daten das wirksame Minimum finden. Es haengt ab von: Leben der eigenen und fremden Einheiten, welche Fern-/Nahkaempfer im Kampf sind, Moerderloecher, Feuer, Hunde, Bevoelkerung im Weg (die auch Schaden machen kann).
- **Ein Lord heilt nicht** (Daniel 05.10. 21:05) - Schaden bleibt; jede Welle zaehlt.
- Ziele mit Wert (Daniel 04.10., 22:54): Bonus fuer den gegnerischen Kornspeicher (meist viel drin), wertvoll auch Steinbrueche, Holzfaeller, Ochsenjoche. Auch ein paar Speertraeger koennen angreifen, nicht nur Assassinen.
- Perfektes Stacken (Daniel 22:52): alle Einheiten gebuendelt auf ein Ziel - in Abwehr und Angriff unglaublich wichtig.
- Lord (Daniel 22:43): darf mitkaempfen und abfangen, wenn er frueh weiss wo angegriffen wird; wichtig sind nur seine letzten Lebenspunkte.
- Lord toeten (Daniel 05.10. 00:52): wann, ist schwer abzuschaetzen - auf jeden Fall, wenn keine oder nur noch wenige Feindeinheiten im Spiel sind. Der Lord muss angreifbar sein; ist er zugebaut ("zugebuddelt"), erst freilegen. Nebenher immer wieder pruefen und Raid-Assassinen, die nichts mehr zu tun haben, gebuendelt und gestapelt auf den Lord schicken: meist reichen 10 locker, steht der Lord allein sogar 5; bei Bogenschuetzen mehr, je nach Feindmenge noch viel mehr.
- Assassinen-Raid (Daniel 04.10. 23:14-23:35, 05.10. 00:00): aufteilen, **hoechstens 6 je Gebaeude**; jeder Assassine einzeln befohlen auf das naechste Wirtschaftsgebaeude, ist es voll, sofort das naechste; nach einer Zerstoerung sofort weiter; kein Sammelpunkt noetig.

## Liga-Balance (abgelesen 05.10.2026 aus `ucp/plugins/Mod-KI-Team-Liga-2.0.2/resources/balance/liga_ai.json`)
Beide Instanzen laden sie (ucp3.log: rebalancer 1.1.3 mit genau dieser Datei). Was NICHT drinsteht, ist Grundspiel.
- **Assassine:** 12.500 Leben, 70 Gold, Grundschaden 250; gegen den **Lord nur 100** je Schlag, gegen Speertraeger 120,
  gegen Bogenschuetzen 225. Pfeile treffen ihn mit 1.200 (Speertraeger 3.000), Armbrust mit 6.000.
- **Lord:** Leben nicht geaendert (gemessen 150.000) -> rund 1.500 Assassinen-Schlaege. Sein Schaden gegen Assassinen
  steht nicht drin (Grundspiel, offen).
- **Schrecken hilft im Kampf:** Kampfkraft je Furchtstufe 80 % (nur Gutes) bis **140 % (nur Schreckliches)**, Reichweite 4.
  Galgen/Pranger/Galgenkaefig je 40 Gold, Kerker/Streckbank 30 Gold.
- **Hunde:** Zwinger laesst los ab 16 Feinden in der Naehe; Hund 20.000 Leben, Schaden 80. Feuer 75.
- **Reichweiten:** alle Bogen 40, Schleuder 18. `reduce_height_advantage` wirkt bei uns NICHT (ucp3.log: "only available
  for SHC Extreme" - wir starten Stronghold Crusader.exe), Hoehe bringt also den vollen Vorteil.
- **Kosten** (Holz, Stein, Eisen, Pech, Gold): Eisenmine 20/6, Steinbruch 25 Holz, Ochsenjoch 5 Holz, Holzfaeller 5 Holz,
  Kaserne 12 Stein, Soeldnerposten 120 Gold, Moerdergrube 4 Holz, Zwinger 5 Holz + 75 Gold.
- **Preise:** Stein 50/25 (Kauf/Verkauf), Eisen 270/135 (doppelte Abholung an), Holz Kauf 15.
- **Klettern:** steht nicht in der Balance - es ist Spielmechanik. Im Spielcode (giveTribeAnInstruction) setzt das Spiel beim
  Angriffsbefehl ein Merkmal "Gruppe besteht nur aus Assassinen" fuer den Wegfinder (abgelesen, Bedeutung vermutet:
  erlaubt Kletterwege). Unser `wegtest` ruft den Wegfinder OHNE dieses Merkmal - darum sagt er beim Lord "kein Weg",
  obwohl Assassinen klettern koennten (vermutet, noch nicht gemessen).

## Replay-Modul als Code-Vorlage (abgelesen 05.10.2026, github.com/Krarilotus/ucp_recorder, Stand df397bb 12.09.2026)
Daniel 23:09: "schau dir den Replay-Mode als Code-Referenz an, um das Spiel noch besser zu machen". Kopie (nur lesen):
`Tools/Referenz/ucp_recorder/` (init.lua, code/recorder.lua). Gilt fuer SHC, nicht Extreme - wie unser Spiel.
- **Gleicher Zufall = gleiche Partie:** Karten-/Partie-Saat 0x01A279C4, Zufallswerte 0x01A279C0/C2, Zaehler 0x01A3160C/08;
  der Haken bei 0x004428B5 (Gefecht startet) setzt sie auf gespeicherte Werte. Mit fester Saat laeuft jede Testpartie
  gleich, bis UNSER Lenker etwas anders macht - echter Vergleich zweier Code-Staende statt Zufallsrauschen.
- **Befehl auf einen genauen Tick planen:** 0x00480210 scheduleCommand(0x0191D768, Art, Spieler, Spielzeit, Daten);
  Spielzeit 0x01FE7DA8. Mitschnitt an 0x00487C50 (gesendet) und 0x00480353 (empfangen), Groesse 0x0194AF98.
- **Mitschnitt + Abspielen:** jeder Spielerbefehl mit Spielzeit in eine Datei; beim Abspielen gleiche Saat, Befehle zur
  gleichen Spielzeit, Gleichlauf-Pruefung (Zufallswerte je Befehl). So koennte Daniel jede unserer Partien spaeter ansehen.

## Gegner Rotkaeppchen (abgelesen 05.10.2026 aus `ucp/plugins/Mod-KI-Team-Liga-2.0.2/resources/ai/Rotkaeppchen/character.json`)
- Start: 9 Assassinen, 14 Bogenschuetzen, 5 Speertraeger; arabischer Lord mit Staerke 0,5 (halb so stark).
- Wirtschaft: NUR Aepfel (8 Plantagen-Plaetze, bis 24 Plantagen, 2 Leute je Plantage), 6 Holzfaeller, 1 Steinbruch, 2 Eisenminen, 2 Pechgruben, bis 5 Ochsen. Steuern 3-11, Beliebtheit 93-99, Essen hoechstens 50, doppelte Rationen ab 50 Essen. Verkauft Weizen, Mehl, Hopfen, Bier, Waffen, Kaese, Brot. -> Ihre Nahrung haengt allein an den Apfelplantagen und dem Kornspeicher.
- Verteidigung: 42 Verteidiger, davon 22 auf den Mauern (Bogenschuetzen-lastig: DefUnit 1-3 Bogen, 4 Speer); **10 Aussen-Patrouillen, die wandern** (Sammelpause 25) - das sind die Gruppen von 7-10 Bogenschuetzen, an denen unsere Assassinen sterben. Ausfaelle: 8 Speertraeger.
- Ueberfaelle: 8 Speertraeger in Gruppen zu 4 (das waren die Angreifer auf unseren Kornspeicher, 04.10.).
- Grossangriff: 30 (+20) Mann, Ziel "Gold", 6 Leitermaenner, 6 Schilde - irgendwann kommt ein Heer von 30-50.
- Folgerung: Patrouillen sind die Gefahr fuer Assassinen (meiden oder mit Ueberzahl gebuendelt erledigen); ihr Essen kommt nur aus Aepfeln - Plantagen und Kornspeicher sind ihr wunder Punkt; gegen den Grossangriff brauchen wir Mauern/Tuerme und den Lord in Sicherheit.

## Arbeitsweise beim Testen
- Lernstufen je Sache (Daniel 05.10. 19:18) - ein Prozess, kein Schritt ist fest, aber jeder muss irgendwann beantwortet werden (und viele weitere Fragen): **1.** bauen koennen - **2.** es wirksam machen - **3.** wissen, warum man es NICHT bauen muss - **4.** wissen, warum und WANN man es bauen sollte - **5.** selbstaendig situativ auf kreative Loesungen kommen.
- Offenes steht an EINER Stelle: `Backlog.md`. Vor jedem Schritt dort den passenden Punkt waehlen, Erledigtes abhaken (Daniel 05.10. 19:14).
- Bei Fehlern immer den passenden Stand laden; nach vielen Neuerungen lieber ganz neu starten, um eine noch bessere Moeglichkeit zu finden (Daniel 04.10., 22:54).

## Vorteil der KI
- Menschen koennen so schnell nicht handeln - eine perfekte KI ist damit effektiver. (Daniel 04.10.)
- Gemessen: Einheiten lesen ein neues Ziel nur an Feldgrenzen (Bogenschuetze alle 16 Ticks); Befehle schneller als ein Feld verpuffen. (M10.05, 04.10.)
- Gemessen: Die KI wirbt Verluste in ~100 Ticks je Einheit nach; holt zurueckgerufene Arbeiter nicht von selbst an die Arbeit (M10.03/M10.04).
