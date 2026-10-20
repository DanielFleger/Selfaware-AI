> **ABGELOEST am 19.10.2026 durch `backlog.json` / `Backlog.html`** (erzeugt mit `python werkzeug/backlog.py bauen`). Alle Punkte dieser Datei sind dort als B-1 bis B-58 uebernommen, mit Stand und Verlauf; hier wird nichts mehr gepflegt. Daniel 19.10. 21:52: eine wachsende Liste, was wann wie gebaut wurde, wo es steht und was fehlt.

# Backlog Selfaware-AI

Eine Stelle fuer alles Offene (Daniel 05.10.2026 19:14: "schreib dir das in den Backlog und picke dann daraus immer das
passende"). Vor jedem neuen Schritt hier den passenden Punkt waehlen; Erledigtes wird abgehakt und bleibt stehen.
Herkunft je Punkt in Klammern. Einzelheiten und Messwerte stehen in `Meilensteine.md`.

Lernstufen je Sache (Daniel 05.10. 19:18) - ein Prozess, kein Schritt ist fest, aber jeder muss irgendwann beantwortet
werden (und viele weitere Fragen): **1.** bauen koennen - **2.** es wirksam machen - **3.** wissen, warum man es NICHT
bauen muss - **4.** wissen, warum und WANN man es bauen sollte - **5.** selbstaendig situativ auf kreative Loesungen kommen.

## Jetzt dran
- [ ] **Nur noch 50/100 Streitkolben optimieren** (Daniel 09.10.): 25 ist vorerst nicht Aufgabe. Naechster echter Lauf erst nach Daniels ausdruecklichem Startsignal; bis dahin bleibt `werkzeug/STOP` gesetzt.
- [ ] **Produktionslauf 50/100 bestaetigen:** Der zweite freigegebene 50er-Lauf erreichte das Ziel gueltig bei Tick 30.331 (Endspiel 25.615), war aber deutlich langsamer als 24.625. Der Reparaturlauf `1010c` baute erstmals die komplette Zielkette (8/8 Minen, 7/7 Schmieden, 6/6 Gerber), Endspiel bei 24.002, blieb danach aber bei 14/50 stehen: 48 Bauern am Feuer trugen als Arbeitsplatz die Bergfriednummer 5 und wurden deshalb faelschlich aussortiert. Repariert und offline 7/7 geprueft: Die echte Feuerzahl begrenzt die Welle; Arbeitsplatz wird nicht doppelt gefiltert, Zustand 109 wird ignoriert, bei irgendeinem Abwanderer 110 wartet die ganze neue Welle. Naechster echter Lauf nur nach Daniels erneutem Startsignal.
- [ ] **25 Streitkolben in hoechstens 24 Monaten** (zurueckgestellt): harte Grenze Tick 19.200; hoechstens 14.400 (18 Monate) ist sehr gut, unter 12.800 (16 Monate) sehr sehr gut.
- [x] **Vorher Ressourcentests:** Eisen mit Wegen 8-91, Verhaeltnissen 5:8 und 5:5 sowie voller Schmiedekette gemessen; Ergebnis 0,588 Eisen/Mine/1.000, 0,664 Verbrauch/Schmied/1.000, 1,49 Keulen/Eisen -> sicherer Start 5:4. Stein getrennt als Erzeugung und Ochsenleistung gemessen: 4,1-5,2 Stein/Bruch/1.000, zwei Joche bringen in der Zielzeit deutlich mehr ins Lager als eines. Korridor-, Lager-, Waffenlager- und Kornspeicher-Gegenproben bestanden; Markt/Haeuser ausserhalb des Kerns.
- [x] **Rekrutierung erst nach Wirtschaftsaufbau:** `schub=nein` ist fuer s25 fest und ueberschreibt auch alte Beststrategien; Keulen/Leder sammeln, Gold bis zur letzten rentablen Erweiterung in die Wirtschaft stecken.
- [x] **25er-Serie ueber mehrere Instanzen:** `streitkolben_serie.py` startet dieselbe Strategie gleich oft je Instanz, schreibt Instanz/Code-Kennung/Tempo/Lenker-Runden mit und vergleicht wegen des belegten Instanzunterschieds zuerst innerhalb derselben Instanz.
- [x] **25er-Abbruchwaechter:** `zielwaechter.py` prueft je Ziellinie eine absichtlich grosszuegige Goldobergrenze gegen 20 Gold je noch fehlendem Kaempfer + Restkaeufe + Pflichtbauten. Er stuft erst die Wertung herunter und bricht nur bei unmoeglicher 24-Monats-Grenze ab; Negativfall und rettbarer Grenzfall sind als Gegenproben gebaut.
- [ ] **Restbedarf mit laufender Produktion rechnen:** Eisen in Mine/Transport/Schmiede und Kuehe/Gerberarbeit mitzählen, bevor Keulen oder Leder gekauft werden; sonst Doppelkauf kurz vor Lieferung.
- [ ] **Frueher Stein fuer den 25er:** pro fruehem Steinbruch zwei Joche einplanen; zweites nicht erst nach langem Stau. Ziel bleibt erster Stein vor Tick 3.500 statt im Rekordlauf Tick 7.640. Drittes Joch nur bei weiter wachsendem Haufen trotz zweier aktiver Ochsen.
- [ ] **B-Plantage als Gueltigkeitsbedingung:** Kontrolllauf nur werten, wenn alle B-Plantagen hoechstens 200 Ticks nach A stehen; Lauf 6 war mit bis zu 1.459 Ticks verfaelscht.
- [x] **Ertrags-Planer** (Daniel 19:11/19:14; Stand 4 seit 05.10. 20:10, M21): erst Messpartie (Ertrag je Gebaeude je 1.000 Ticks, Verkaufspreis Stein/Eisen, Weglaenge), dann jede Runde die Aktion mit der schnellsten Amortisation bauen, ohne feste Stueckzahlen; Umgebung bestimmt alles. Stein und Eisen vermutlich vorne.
- [x] **Planer lernt im Spiel** (Befund 9t; erledigt 05.10. 20:10, M21): Ertrag je Gebaeudeart aus dem laufenden Spiel messen (Bestand + Verkauf + Verbrauch je Ware, geteilt durch Zahl der Betriebe) und die Startwerte ersetzen - dann hoert er von selbst auf, Jaegerhuetten zu bauen, die nichts bringen.
- [x] **Zeithorizont fuer Investitionen** (Befund 9t; erledigt 05.10. 20:10: Gewinn bis Partieende, M21): nur bauen, was sich innerhalb des Horizonts bezahlt macht; sonst geht das Gold in Truppen.
- [x] Apfelplantage und Holzfaeller ueber Platzkarten statt Raster/Baumliste (erledigt 05.10. 20:10, Karten ueber die ganze Karte) (Befund 9t: 0 Apfelplantagen, Baum-Ziel 6-mal bebaut)
- [ ] Wegformel je Art aus den Messdaten statt vermutet (M21: Holz haengt kaum am Weg, Jaeger unklar)
- [x] Mehrere Laeufe je Planer-Stand (erledigt 05.10. 20:22: `serie.py`, Serie x 8 Laeufe, M22)
- [ ] Startwerte aus frueheren Partien (`daten/ertrag_gelernt_*.json`) - erster Schritt zum Selbstlernen
- [ ] Horizont in echten Partien ohne festes Ende (bis zum geplanten Angriff?) - Daniel fragen

## Angriff (Daniel 06.10., Uebergabe Codex)
- [x] Gemeinsamer Lord-Angriff statt zwei Wellen (Codex 06.10.; gemeinsam_1: 3 Siege, Verluste 10-18, aber ~3.000 Ticks spaeter)
- [x] Trainingsstand + Lord-Minimum-Messung (Codex 06.10.; diese Lage: 19 stabil, 15-18 unsicher)
- [x] Angriffsprotokoll ohne Vorfilter: alle Einheiten, Gebaeude, Gelaende (Codex 06.10.)
- [ ] Echtes Zielfeld der KI-Einheiten lesen (Zielart 3: Ziel nicht im gelesenen Feld) - Voraussetzung fuer den Fingerabdruck
- [ ] Bedrohungs-/Einfluss-Fingerabdruck aus gemessenem Schaden, Weg, Sicht, Gebaeuden, Gelaende
- [ ] Kleinste ausreichend sichere Truppe, nicht auf Nachzuegler warten; unbekannte Lage: vorlaeufiger Ersatzwert
- [ ] Erster Assassine frueher (gewinn_6 3.778, Trainingslauf 3.207)
- [ ] Warum ihr Lord in ganzen Partien 75.000 Leben meldet, im Trainingsstand 150.000

## Wirtschaft
- [ ] Holzfaeller: 3 je Baum, Clusterung; Holzfaeller/Lager live umsetzen (04.10.)
- [x] Altes Lager: Holz in 5er-Losen verkaufen statt mit abreissen (Codex 06.10.; nur Rest 1-4 geht verloren)
- [x] B-Plantage erst bestaetigt, wenn das Gebaeude steht (Codex 06.10.)
- [ ] Zusaetzliche Holzfaeller nur, wenn sie den Ausbau beschleunigen; sonst Holz verkaufen (Daniel 06.10.)
- [x] Apfel-Seasoning (05.10., `wirtschaft.py`; untaetig 40 % -> 11-35 %)
- [x] Ochsenjoche vorausschauend nach gemessener Kettenrate: zwei je fruehem Steinbruch, weiteres nur bei wachsendem Haufen trotz zweier aktiver Ochsen (08.10.)
- [ ] Wirtschaft erweitern: Stein, Eisen, Pech bis zum Maximum (05.10. 00:26, 19:05, 19:11)
- [ ] Wirtschaft nachbauen: Holzfaeller, Apfelplantagen, Haeuser (05.10. 19:06)
- [ ] Waffenproduktion, Bier (05.10. 19:06), Brot, Religion, Essensvielfalt (04.10. 23:25, 05.10. 00:26)
- [ ] Angstfaktor positiv/negativ (05.10. 00:26)
- [ ] Jagd an Rehen (05.10. 19:05) - erste Regel steht, geht im Ertrags-Planer auf
- [ ] Steuern nach Beliebtheit (05.10. 00:26) - erste Regel steht, geht im Ertrags-Planer auf
- [x] Nahrung auf Kante verkaufen (05.10. 18:51)
- [x] Lager erst beim ersten Lieferwunsch, altes Lager dann weg (04.10., 05.10. 19:09)
- [ ] Lager rechtzeitig erweitern - vorausschauend nach Ladung unterwegs (04.10.)
- [x] Start mit 0 Gold wie in der Liga (05.10. 00:55, M19)
- [x] Nie blind starten: Bergfried aus dem Spiel, Plan je Start, nur eigene Seite (05.10. 18:55)

## Kampf
- [ ] Wirksames Minimum je Lord-Welle aus den Wellen-Daten lernen (Groesse, Fern/Nah am Lord, Schaden, Verluste) - Daniel 21:05
- [ ] Weitere Parameter messen: Moerderloecher, Feuer, Hunde, Bevoelkerung im Weg (Daniel 21:05)
- [ ] Eigenen Lord schuetzen, wenn Rotkaeppchens Grossangriff kommt (Serie t2: Niederlage bei Tick 20.990)
- [ ] Mehr Eisen: erste Mine wieder frueher (mit Startwerten aus Partien rueckte sie auf Tick ~8.000)
- [ ] **Lord-Trupp bildet sich nie** (M22: 0 Pruefungen in 8 Laeufen): erst messen, wie viele frei sind vs. noetig; dann Assassinen sammeln statt sofort verteilen (Daniel 05.10. 00:26: "Angriffsarmeen sammeln")
- [x] Lord-Trupp nach Daniels Regel (05.10. 00:52, M18)
- [ ] Zugebauten Lord freilegen (05.10. 00:52) - Wegtest steht, Freilegen fehlt
- [ ] Sinnvoller angreifen, Angriffsarmeen sammeln (05.10. 00:26)
- [x] Zielwahl nach Wert: Ausbildungslager, Steinbrueche, Haeuser vor Apfelplantagen (05.10. 19:05)
- [ ] Einheiten besser optimieren (05.10. 00:26)
- [ ] Mauern bauen, Lord schuetzen (05.10. 00:26)
- [ ] Sammelpunkt des Soeldnerlagers (Spielbefehl 71) (04.10.)
- [ ] Echtzeit ab Tempo 40 und hoeher (04.10. 21:54)

## Spaeter
- [ ] **Echtes Selbstlernen** ueber tausende Partien statt Codeaenderungen (05.10. 00:57)
- [ ] **Challenges** (05.10. 19:14): kein Markt; keine arabischen Einheiten; schnellste Kathedrale; schnellster Kill; weitere nach Daniels Wahl

## 06.10.2026 21:10 - B-Apfelplantagen werden nicht gesetzt (gefunden in Haertetest v2)
Gemessen (`daten/haertetest_v2_20261006.txt`): "Seasoning: A 3 / B 3 Plantagen, A reif bei 1699, B gesetzt bei None";
die Wirtschaft kaufte mehrmals "Holz fuer B" (Tick 3.781 Gold 181, 3.808 Gold 166 ...), das Holz wurde anderswo verbaut,
B nie gesetzt. Folge: ausbau.braucht_gold die ganze Partie True (Seasoning-B hat Vorrang) - blockierte den Waffenkauf
(in v2b umgangen durch den Kipppunkt) und haelt Gold als Ruecklage fest. Zu klaeren: warum B nicht gesetzt wird
(Platz? Holz-Reservierung gegen den Ertragsplaner?), Holzkauf fuer B nur, wenn B danach sicher gesetzt wird.
