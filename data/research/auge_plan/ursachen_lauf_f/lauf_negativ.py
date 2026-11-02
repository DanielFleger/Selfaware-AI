# -*- coding: utf-8 -*-
"""Negativlauf Lauf F: Jede ausgeschaltete Pruefung muss die Tests rot machen. Danach steht jede Datei wieder wie vorher."""
import os, subprocess, sys

L = "src/selfaware/tools/experiments/auge_lauf_f.py"
A = "src/selfaware/tools/experiments/auge_aufzeichnung.py"
W = "src/selfaware/tools/analysis/auge_auswertung.py"
K = "src/selfaware/tools/experiments/auge_lauf_k.py"
P = "src/selfaware/tools/analysis/auge_punkte.py"
FAELLE = [
    ("Anzeige 20 nicht geprueft", L, "if not l.warte_takte(WOCHE, lambda: s.anzeige_burg_korn() == 0):", "if False:"),
    ("Kalender nicht geprueft", L, "if not l.warte_takte(WOCHE + ABLESEN, lambda: s.kalender() != woche):", "if False:"),
    ("Waren nicht geprueft", L, "        if not ok:\n            raise Abbruch(f\"Waren kommen", "        if False:\n            raise Abbruch(f\"Waren kommen"),
    ("Bewohner nicht geprueft", L, "elif t - self.bewohner[1] > KEIN_BEWOHNER:", "elif False:"),
    ("Beliebtheit nicht geprueft", L, "if not frei and bel < BELIEBTHEIT_UNTEN:", "if False:"),
    ("Stillstand nicht geprueft", L, "elif jetzt - self.puls[1] > self.stillstand_grenze():", "elif False:"),
    ("Frist nicht geprueft", L, "if jetzt > self.ende:", "if False:"),
    ("Handstopp nicht geprueft", L, "if self.stop():", "if False:"),
    ("Aufzeichnung nicht geprueft", L, "        if grund:\n            raise Abbruch(f\"Aufzeichnung", "        if False:\n            raise Abbruch(f\"Aufzeichnung"),
    ("Bremse nicht geprueft", L, "raise Abbruch(f\"Das Lesen bremst {wann}: {e.text}\")", "pass"),
    ("Tempo nicht geprueft", L, "if stufe <= 100 and abs(o1[\"rate\"] - stufe) > max(2.0, 0.2 * stufe):", "if False:"),
    ("Bau ohne Grenze gilt als gebaut", L, "raise Abbruch(f\"Art {typ} ({g.get('name')}): an den erlaubten Stellen", "return None; raise Abbruch(f\"Art {typ} ({g.get('name')}): an den erlaubten Stellen"),
    ("Keine Stelle gilt als in Ordnung", L, "raise Abbruch(f\"Art {typ} ({g.get('name')}): keine vom Spiel erlaubte Stelle\")", "return None"),
    ("Schluss immer gueltig", L, "pruefung[\"gueltig\"] = (not fehlen", "pruefung[\"gueltig\"] = True or (not fehlen"),
    ("Lauf haelt das Spiel an", L, "        self.k.befehl({\"baue\":", "        self.k.befehl({\"pause\": True}, KANAL)\n        self.k.befehl({\"baue\":"),
    ("Jahr auf Tempo 40 nicht streng", L, "l.rek.starten(\"jahr40\", TEMPO_JEDER_TAKT, streng=True)", "l.rek.starten(\"jahr40\", TEMPO_JEDER_TAKT, streng=False)"),
    ("Essen kommt nicht nach", L, "if s.spieler(\"totalFood\") < ESSEN_UNTEN and t >= self.naechstes_essen:", "if False:"),
    ("Spiel weg bleibt ein roher Fehler", L, "        except OSError as e:  # jedes Lesen", "        except ZeroDivisionError as e:  # jedes Lesen"),
    ("Streng: fehlender Takt egal", A, "            if self.streng:\n                raise Streng(f\"Takt", "            if False:\n                raise Streng(f\"Takt"),
    ("Streng: gemischt egal", A, "                    if self.streng:\n                        raise Streng(f\"Bereich", "                    if False:\n                        raise Streng(f\"Bereich"),
    ("Streng: Schlange egal", A, "            if self.streng:\n                raise Streng(\"Die Warteschlange", "            if False:\n                raise Streng(\"Die Warteschlange"),
    ("Seltene Bereiche zaehlen streng", A, "                if b.alle == 1:\n", "                if True:\n"),
    ("Aussetzen zaehlt als fehlend", A, "self.letzter = None  # die ausgesetzten", "pass  # die ausgesetzten"),
    ("Feldwache zaehlt ungelistete", A, "if f not in self.gesehen and self.karte.bekannt(*f):", "if f not in self.gesehen:"),
    ("Stufe ohne Takte gilt als gemessen", W, "    if nicht_gemessen:\n", "    if False:\n"),
    ("A3 selten zaehlt streng", W, "            if alle == 1:\n                unrein += 1", "            if True:\n                unrein += 1"),
    ("A8 ohne Ursache verschwiegen", W, "    if ohne:\n        return Ergebnis(\"A8\", WIDERLEGT", "    if False:\n        return Ergebnis(\"A8\", WIDERLEGT"),
    ("A10 nur volle Rahmen", W, "                        plaetze.update(range(max(0, (badr + o - adr) // schritt), min(anzahl - 1, (badr + o + l - 1 - adr) // schritt) + 1))", "                        pass"),
    ("Punkte: gekappte Liste weicht ab", P, "if not any(b[\"mehr_werte\"] for b in belege):", "if True:"),
    ("Punkte: ruhendes Feld zaehlt nicht", P, "if any(zahl in b[\"werte\"] for b in belege):", "if any(zahl in b[\"werte\"] for b in geaendert):"),
    ("Bewohner: auch ohne offene Plaetze", L, " or offene_plaetze(self) == 0:", ":"),
    ("Bewohner: auch nach den Bauern", L, "    l.bewohner_wache = False  # ob am Ende", "    pass  # ob am Ende"),
    ("Bewohner: Schalter ohne Wirkung", L, "if not self.bewohner_wache or self.bewohner is None", "if self.bewohner is None"),
    ("Gold ohne Ablesefrist", L, "if not l.warte_takte(ABLESEN, lambda: s.waren()[15] == GOLD):", "if s.waren()[15] != GOLD:"),
    ("Gold nicht geprueft", L, "if not l.warte_takte(ABLESEN, lambda: s.waren()[15] == GOLD):", "if False:"),
    ("Waffen passen nicht ins Lager", L, "WAFFEN_WAREN = {w: 5 for w in range(17, 25)}", "WAFFEN_WAREN = {w: 20 for w in range(17, 25)}"),
    ("Handel kauft nicht", L, "    l.k.liste([{\"spielbefehl\": {\"nr\": BEFEHL_HANDEL, \"werte\": [0, w]}} for w in HANDELSWAREN], KANAL)\n", ""),
    ("Handel: Speer bleibt liegen", L, "    if zurueck > 0:\n", "    if False:\n"),
    ("Handel: zu viele Speere zurueck", L, "for _ in range(zurueck)], KANAL)", "for _ in range(lose)], KANAL)"),
    ("Deckel ohne Ablesefrist", L, "if not l.warte_takte(ABLESEN, lambda: s.spieler(\"populationCap\") >= 10 + HUETTEN * 8):", "if s.spieler(\"populationCap\") < 10 + HUETTEN * 8:"),
    ("Deckel nicht geprueft", L, "if not l.warte_takte(ABLESEN, lambda: s.spieler(\"populationCap\") >= 10 + HUETTEN * 8):", "if False:"),
    ("Zweite Kaserne bricht ab", L, "e = l.setze(KASERNE, pflicht=False)", "e = l.setze(KASERNE)"),
    ("Zusatzbau bricht ab", L, "if l.setze(typ, pflicht=False) is None:", "if l.setze(typ) is None:"),
    ("Zusatzbau ohne Fund", L, "            l.wirkung(f\"Zusatzbau Art {typ}\", False)\n", "            pass\n"),
    ("A9: Plaetze als ein Stueck", W, "plaetze.update(range(o // groesse, (o + l - 1) // groesse + 1))", "plaetze.add(o // groesse)"),
    ("A8: neuer Weg nicht erkannt", W, "    if ware != 15 and neuer_weg:\n", "    if False:\n"),
    ("A8: neuer Weg auch fuer Gold", W, "    if ware != 15 and neuer_weg:\n", "    if neuer_weg:\n"),
    ("Tor: 12 gilt als Fund", L, "ist in (zustand, TOR_FERTIG), ist=ist)", "ist == zustand, ist=ist)"),
    ("K: Lords nicht geprueft", K, "if not l.warte_takte(LORDS_STEHEN, lambda: s.lord_besitzer() == SOLL_LORDS):", "if False:"),
    ("K: Lords nur gezaehlt", K, "lambda: s.lord_besitzer() == SOLL_LORDS", "lambda: len(s.lord_besitzer()) == len(SOLL_LORDS)"),
    ("K: Plaetze um eins verschoben", L, "core.writeByte(posArr + i, i) end", "core.writeByte(posArr + i, i + 1) end"),
    ("K: Spielerzahl der Karte egal", K, "    return kopf.get(\"typ\") == 1 and", "    return True or kopf.get(\"typ\") == 1 and"),
    ("K: Kartenkopf einen Abschnitt daneben", K, "for _ in range(3):  # Vorschaubild", "for _ in range(2):  # Vorschaubild"),
    ("K: erst weiter, dann Tempo", K, "    l.k.befehl({\"tempo\": tempo}, lf.KANAL)\n", "    l.k.befehl({\"pause\": False}, lf.KANAL)\n    l.k.befehl({\"tempo\": tempo}, lf.KANAL)\n"),
    ("K: Friedenszeit nicht geprueft", K, "if not l.warte_takte(grenze, lambda: l.s.frieden() == 0):", "if False:"),
    ("K: Takt steht nicht geprueft", K, "    if not steht:\n        raise Abbruch(f\"Der Takt steht", "    if False:\n        raise Abbruch(f\"Der Takt steht"),
    ("K: Fenster nicht streng", K, "a = aufnahme_im_stand(l, name, lf.TEMPO_JEDER_TAKT, streng=True, warte_ms=WARTE_MS)", "a = aufnahme_im_stand(l, name, lf.TEMPO_JEDER_TAKT, streng=False, warte_ms=WARTE_MS)"),
    ("K: Tempomessung im stehenden Spiel", K, "l.rek.starten(name, tempo, streng=streng, messen=False, warte_ms=warte_ms)", "l.rek.starten(name, tempo, streng=streng, messen=True, warte_ms=warte_ms)"),
    ("K: fehlender Takt egal", K, "    if stand.get(\"fehlend\") or stand.get(\"gemischt\"):\n", "    if False:\n"),
    ("K: Friedenszeit am Start egal", K, "    if s.frieden() <= 0:\n", "    if False:\n"),
    ("K: geladener Takt egal", K, "    if t2 != t:\n", "    if False:\n"),
    ("K: Laden vor dem Kampf", K, "(\"bis_zum_ende\", abschnitt_bis_zum_ende), (\"laden_vergleichen\", abschnitt_laden_vergleichen)", "(\"laden_vergleichen\", abschnitt_laden_vergleichen), (\"bis_zum_ende\", abschnitt_bis_zum_ende)"),
    ("K: nur einmal geladen", K, "    f3 = laden_und_fenster(l, g[\"name\"], g[\"t\"], \"t3\")\n", "    f3 = f2\n"),
    ("K: Bremse bricht ab", K, "        if \"bremst\" not in str(e):\n            raise\n        l.wirkung", "        raise\n        l.wirkung"),
    ("K: Ende nur am letzten Lord", K, "        elif l.uhr() >= l.weich:\n", "        elif False:\n"),
    ("K: Endbildschirm nicht erkannt", K, "        if s.ansicht() in ENDE_ANSICHTEN:\n", "        if False:\n"),
    ("K: letzter Lord nicht erkannt", K, "        elif s.lords() <= 1:\n", "        elif False:\n"),
    ("K: Lord-Zaehler nach maxUnitCount", K, "        roh = self.q.lies(lf.EINHEITEN, ALLE_PLAETZE * lf.E_SCHRITT)\n", "        roh = self.q.lies(lf.EINHEITEN, min(self.i32(lf.EINHEITEN_ANZAHL), ALLE_PLAETZE) * lf.E_SCHRITT).ljust(ALLE_PLAETZE * lf.E_SCHRITT, bytes(1))\n"),
    ("K: Laden aus dem Hauptmenue", K, "    gefecht_starten(l.k, l.karte, l.frieden_stufe, ruhe=l.ruhe, startpause=1)\n    t2 = l.laden(name)\n", "    t2 = l.laden(name)\n"),
    ("K: Fenster liest halb gerechnet", K, "streng=True, warte_ms=WARTE_MS)", "streng=True)"),
    ("K: Warten ohne Wirkung", A, "        if self.warte_ms:\n", "        if False:\n"),
    ("K: Gefecht eingefroren", K, "    k.befehl({\"pause\": False}, lf.KANAL)  # sonst", "    pass  # sonst"),
    ("A10: Merkplatz zaehlt mit", W, "                if i < erster:\n                    continue\n", ""),
    ("A10: Einheiten ab Platz 0", W, "\"units[].uid\", 1)", "\"units[].uid\", 0)"),
    ("A8: Gold kommt von Arbeitern", W, "if ware != 15 and (betrieb or", "if (betrieb or"),
    ("A8: Steuer nicht erkannt", W, "if ware == 15 and steuer_aenderung:", "if False:"),
    ("A8: Steuer auch fuer Waren", W, "if ware == 15 and steuer_aenderung:", "if steuer_aenderung:"),
    ("los: Aufzeichnung vor dem Anhalten", L, "        steht = False\n        if k is not None and s is not None:", "        if rek is not None:\n            rek.beenden()\n        steht = False\n        if k is not None and s is not None:"),
    ("los: Sperre frei, obwohl der Takt laeuft", L, "        if steht:\n            sperre_freigeben()\n        else:", "        if True:\n            sperre_freigeben()\n        else:"),
    ("los: alte Schalter bleiben", L, "ALTE_SCHALTER = ({\"tickpause\": \"aus\"}, {\"ladepause\": \"aus\"})", "ALTE_SCHALTER = ()"),
    ("los: alte Logzeile gilt", L, "                    f.seek(log_vorher)\n", "                    f.seek(0)\n"),
    ("Menue: kein Warten auf den Wechsel", L, "warte_auf(lambda: k.peek(ANSICHT)[0] == HAUPTMENUE, 10, \"Hauptmenue (Ansicht 41)\", ruhe=ruhe)", "pass"),
]
FAELLE = [f for f in FAELLE if not sys.argv[1:] or any(a in f[0] for a in sys.argv[1:])]  # Aufruf mit Namensteilen: nur diese Faelle
env = dict(os.environ, PYTHONPATH="src", PYTHONIOENCODING="utf-8")
schlecht = 0
for name, pfad, alt, neu in FAELLE:
    roh = open(pfad, "rb").read()
    text = roh.decode("utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    a, n = alt.replace("\n", nl), neu.replace("\n", nl)
    if text.count(a) != 1:
        print("NICHT GEFUNDEN", name, text.count(a))
        schlecht += 1
        continue
    try:
        open(pfad, "wb").write(text.replace(a, n).encode("utf-8"))
        r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_auge_lauf_f.py", "tests/test_auge_lauf_k.py", "tests/test_auge_werkzeug.py", "-q", "--no-header", "-x", "--tb=no"], capture_output=True, text=True, env=env, encoding="utf-8", errors="replace", timeout=300)
        rot = r.returncode != 0
        zeile = [z for z in r.stdout.splitlines() if z.startswith("FAILED")][:1]
        print(("ROT  " if rot else "GRUEN"), name, "|", (zeile[0][7:100] if zeile else ""), flush=True)
        schlecht += 0 if rot else 1
    finally:
        open(pfad, "wb").write(roh)
print("Sabotage nicht bemerkt:", schlecht, "von", len(FAELLE))
sys.exit(1 if schlecht else 0)
