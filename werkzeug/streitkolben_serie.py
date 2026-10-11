# -*- coding: utf-8 -*-
"""Streitkolben-Strategien gleichzeitig auf mehreren SHC-Instanzen pruefen.

Aufruf:
  python streitkolben_serie.py name=grundlinie ziel=50 anzahl=3 instanzen=1,3 strategie=beste

`anzahl` gilt je Instanz. So erhaelt dieselbe Strategie auf jeder Instanz
gleich viele Laeufe; Instanzunterschiede werden nicht mit Strategiewirkung
verwechselt. Jeder Arbeiterprozess besitzt genau eine Spielkopie und deren
Testsperre.
"""

import json
import os
import re
import statistics
import subprocess
import sys
import time


HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.abspath(os.path.join(HIER, "..", "daten"))


def argumente(werte):
    return dict(x.split("=", 1) for x in werte if "=" in x)


def stufen_aus(arg):
    """ziel=50 oder gestuft ziel=50,100 (Daniel 11.10. 14:28: "erst die 50, dann 100 Streitis in einem Run")."""
    stufen = sorted(int(z) for z in str(arg.get("ziel", 25)).split(",") if z.strip())
    if not stufen or stufen[0] <= 0:
        raise ValueError("ziel muss groesser als 0 sein")
    return stufen


def ziel_aus(arg):
    return stufen_aus(arg)[-1]


def strategie_laden(wahl):
    import lernen
    grund = dict(lernen.S25["grund"])
    if wahl == "grund":
        return grund, None
    if wahl != "beste":
        raise ValueError("strategie muss grund oder beste sein")
    pfad = os.path.join(D, lernen.S25["datei"])
    laeufe = []
    if os.path.exists(pfad):
        for zeile in open(pfad, encoding="utf-8"):
            r = json.loads(zeile)
            if not r.get("ungueltig") and r.get("art") == "erreicht":
                laeufe.append(r)
    if not laeufe:
        raise RuntimeError("keine erreichte s25-Strategie gefunden")
    beste = min(laeufe, key=lambda r: int(r["note"]))
    return dict(grund, **beste["strategie"]), beste


def einstellungen(arg):
    import lernen
    ziel = ziel_aus(arg)
    strategie, quelle = strategie_laden(arg.get("strategie", "beste"))
    # Daniel 08.10.: kein Gold in Soldaten binden, solange es die Wirtschaft beschleunigen kann. Alte Bestlaeufe
    # enthalten noch schub=immer; die Versuchsregel hat Vorrang vor diesem historischen Wert.
    strategie["schub"] = "nein"
    # Versuchsknoepfe, die nur fuer gestufte Ziele gelten, direkt durchreichen (11.10.: stufe2_beliebt=hoch/halten)
    for k in ("stufe2_beliebt", "leere_ki", "gegner_ki", "angriff_ab", "gegner_erwartet"):
        if k in arg:
            strategie[k] = arg[k]
    if arg.get("weg") == "produktion":
        # Die historische Beststrategie gewann mit Marktkaeufen und durfte deshalb frueh 20 Holzfaeller plus weitere
        # Kausal-Bauten setzen. Fuer die eigene Waffenkette verbraucht das Bauholz und Arbeiter, bevor Minen und
        # Werkstaetten stehen. Hier entscheidet der Ertragsplaner, die Zielkette selbst erzwingt 5 Minen/4 Hoefe.
        strategie["holz_spam"] = arg.get("holz_spam", "0")
        strategie["entscheider"] = arg.get("entscheider", "regeln")
        strategie["vollbeschaeftigung"] = arg.get("vollbeschaeftigung", "nein")
        strategie["penner"] = arg.get("penner", "99")
        strategie["stein_max"] = arg.get("stein_max", "ja")
    # Versuchsreihen duerfen Kauf-/Bilanz-Grundlinie und die gemessene Produktionskette mit identischer
    # Wirtschaftsstrategie vergleichen. Der Weg ist ein Versuchsname, kein versteckter alter Festwert.
    fest = [x for x in lernen.S25["fest"] if not x.startswith(("minuten=", "weg=", "streitkolben="))]
    ziel_tick = int(arg.get("ziel_tick", quelle["note"] if quelle else 14400))
    fest += [
        "minuten=%s" % arg.get("minuten", "60"),
        "tempo=%s" % arg.get("tempo", "100"),
        "bis_tick=%s" % arg.get("bis_tick", "19200"),
        "ziel_tick=%d" % ziel_tick,
        "streitkolben=%s" % ",".join(str(z) for z in stufen_aus(arg)),
        "weg=%s" % arg.get("weg", "bilanz"),
    ]
    fest += ["%s=%s" % kv for kv in sorted(strategie.items())]
    return fest, quelle


def auswerten_text(text, instanz, nummer, datei, ziel, stufen=None):
    treffer = re.search(r"(?:KAEMPFER %d|ZIEL %d Streitkolbenkaempfer erreicht) bei Tick (\d+)" % (ziel, ziel), text)
    ende = re.search(r"Ende Phase 2 bei Tick (\d+) nach (\d+) Runden", text)
    abbruch = re.search(r"FRUEHABBRUCH bei Tick (\d+): ([^\n]+)", text)
    kennung = re.search(r"CODE-KENNUNG (\w+)", text)
    tick = int(treffer.group(1)) if treffer else None
    if ziel == 25:
        wertung = ("sehr sehr gut" if tick is not None and tick < 12800 else
                   "sehr gut" if tick is not None and tick <= 14400 else
                   "unter 24 Monate" if tick is not None and tick <= 19200 else
                   "verfehlt")
    else:
        wertung = "erreicht" if tick is not None else "nicht erreicht"
    return {
        "ziel": ziel,
        "instanz": instanz,
        "lauf": nummer,
        "datei": os.path.basename(datei),
        "kennung": kennung.group(1) if kennung else None,
        "ziel_tick": tick,
        "wertung": wertung,
        "ende_tick": int(ende.group(1)) if ende else None,
        "lenker_runden": int(ende.group(2)) if ende else None,
        "abbruch_tick": int(abbruch.group(1)) if abbruch else None,
        "abbruch": abbruch.group(2).strip() if abbruch else None,
        "fehler": bool(re.search(r"Traceback|ABBRUCH - Spiel angehalten|TESTBEDINGUNG FEHLT", text)),
        "stufen": {str(s): stufen_tick(text, s) for s in (stufen or [ziel])},
    }


def stufen_tick(text, s):
    m = re.search(r"(?:KAEMPFER %d|ZIEL %d Streitkolbenkaempfer erreicht) bei Tick (\d+)" % (s, s), text)
    return int(m.group(1)) if m else None


def sperre_holen(serie, instanz, name, lauf, anzahl, warte_minuten, ziel):
    t0 = time.time()
    while True:
        r = serie.sperre("holen", "SAI", "%der-Serie %s Lauf %d/%d (Instanz %d)" % (
            ziel, name, lauf, anzahl, instanz))
        if r.returncode == 0:
            return
        if time.time() - t0 > 60 * warte_minuten:
            raise RuntimeError("Instanz %d seit %d Minuten belegt: %s" % (instanz, warte_minuten, r.stdout.strip()))
        time.sleep(30)


def pausieren_sicher():
    """Nach jedem Kindprozess bleibt das Spiel stehen - auch wenn der Lenker hart abbricht oder von aussen endet."""
    import befehl as kanal
    from laden import befehl
    kanal.belege()
    try:
        befehl({"pause": True}, 0.8)
    finally:
        kanal.freigeben()


def arbeiter(arg):
    instanz = int(arg["instanz"])
    ziel = ziel_aus(arg)
    os.environ["SHC_INSTANZ"] = str(instanz)
    # Erst nach SHC_INSTANZ importieren: befehl.py waehlt beim Import die Spielkopie.
    import kennung
    import serie

    name = arg.get("name", "grundlinie")
    anzahl = int(arg.get("anzahl", 3))
    warte = int(arg.get("warte", 60))
    setup, quelle = einstellungen(arg)
    ergebnis_pfad = os.path.join(D, "streitkolben_serie_%s_i%d.jsonl" % (name, instanz))
    if os.path.exists(ergebnis_pfad) and arg.get("fortsetzen", "nein") != "ja":
        raise RuntimeError("Ergebnisdatei existiert schon: %s (anderen Namen waehlen oder fortsetzen=ja)" % ergebnis_pfad)
    try:
        for nr in range(1, anzahl + 1):
            sperre_holen(serie, instanz, name, nr, anzahl, warte, ziel)
            print("Instanz %d Lauf %d/%d: %s" % (instanz, nr, anzahl, serie.zuruecksetzen()), flush=True)
            soll = kennung.kennung()[0]
            konsole = os.path.join(D, "streitkolben_%s_%d_i%d_konsole.txt" % (name, nr, instanz))
            try:
                with open(konsole, "w", encoding="utf-8") as f:
                    rc = subprocess.run([sys.executable, "-u", os.path.join(HIER, "erstes_spiel.py")] + setup,
                                        stdout=f, stderr=subprocess.STDOUT, cwd=HIER, env=os.environ.copy()).returncode
            finally:
                pausieren_sicher()
            text = open(konsole, encoding="utf-8", errors="replace").read()
            erg = auswerten_text(text, instanz, nr, konsole, ziel, stufen_aus(arg))
            erg["rueckgabewert"] = rc
            erg["strategie_quelle"] = quelle.get("nr") if quelle else "grund"
            if erg["kennung"] != soll:
                erg["fehler"] = True
                erg["kennung_fehler"] = "%s statt %s" % (erg["kennung"], soll)
            with open(ergebnis_pfad, "a", encoding="utf-8") as f:
                f.write(json.dumps(erg, ensure_ascii=False) + "\n")
            print("Instanz %d Lauf %d: %s%s" % (
                instanz, nr,
                "Tick %d, %s" % (erg["ziel_tick"], erg["wertung"]) if erg["ziel_tick"] else "kein Ziel",
                "; Abbruch: " + erg["abbruch"] if erg["abbruch"] else ""), flush=True)
            if erg["fehler"] or rc != 0:
                raise RuntimeError("Lauf %d auf Instanz %d fehlerhaft; Zustand bleibt zur Pruefung stehen" % (nr, instanz))
    finally:
        serie.sperre("freigeben", "SAI")


def zusammenfassen(name, instanzen, ziel):
    alle = []
    for instanz in instanzen:
        pfad = os.path.join(D, "streitkolben_serie_%s_i%d.jsonl" % (name, instanz))
        if os.path.exists(pfad):
            alle += [json.loads(z) for z in open(pfad, encoding="utf-8") if z.strip()]
    print("\n%der-Serie %s" % (ziel, name))
    for instanz in instanzen:
        laeufe = [r for r in alle if r["instanz"] == instanz]
        zeiten = [r["ziel_tick"] for r in laeufe if r.get("ziel_tick") is not None and not r.get("fehler")]
        print("Instanz %d: %d Laeufe, Zeiten %s%s" % (
            instanz, len(laeufe), ", ".join(map(str, zeiten)) or "keine",
            "; Median %.0f" % statistics.median(zeiten) if zeiten else ""))
    zeiten = [r["ziel_tick"] for r in alle if r.get("ziel_tick") is not None and not r.get("fehler")]
    if zeiten:
        print("Gesamt nur als Uebersicht: Rekord %d; instanzweise Mediane sind der faire Vergleich." % min(zeiten))
    return alle


def koordinator(arg):
    name = arg.get("name", "grundlinie")
    ziel = ziel_aus(arg)
    instanzen = [int(x) for x in arg.get("instanzen", "1,3").split(",") if x]
    prozesse = []
    for instanz in instanzen:
        befehl = [sys.executable, "-u", __file__, "worker=ja", "instanz=%d" % instanz]
        befehl += ["%s=%s" % kv for kv in arg.items() if kv[0] not in ("worker", "instanz", "instanzen")]
        env = dict(os.environ, SHC_INSTANZ=str(instanz))
        prozesse.append((instanz, subprocess.Popen(befehl, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                   text=True, cwd=HIER, env=env)))
    fehler = []
    for instanz, prozess in prozesse:
        aus, _ = prozess.communicate()
        print("\n--- Instanz %d ---\n%s" % (instanz, aus.rstrip()))
        if prozess.returncode:
            fehler.append(instanz)
    zusammenfassen(name, instanzen, ziel)
    if fehler:
        raise SystemExit("Fehler auf Instanz(en): %s" % ", ".join(map(str, fehler)))


def probe():
    text = "CODE-KENNUNG abc123\nKAEMPFER 25 bei Tick 12799\nEnde Phase 2 bei Tick 12799 nach 811 Runden"
    r = auswerten_text(text, 3, 2, "probe.txt", 25)
    assert r["ziel_tick"] == 12799 and r["wertung"] == "sehr sehr gut" and r["lenker_runden"] == 811
    text = "CODE-KENNUNG abc123\nFRUEHABBRUCH bei Tick 19010: 24-Monats-Grenze rechnerisch unmoeglich\nEnde Phase 2 bei Tick 19010 nach 500 Runden"
    r = auswerten_text(text, 1, 1, "probe.txt", 25)
    assert r["ziel_tick"] is None and r["abbruch_tick"] == 19010 and not r["fehler"]
    setup, quelle = einstellungen({"strategie": "beste", "ziel": "50"})
    assert "streitkolben=50" in setup and "streitkolben=25" not in setup and "bis_tick=19200" in setup and quelle
    text = "CODE-KENNUNG abc123\nZIEL 100 Streitkolbenkaempfer erreicht bei Tick 30123\nEnde Phase 2 bei Tick 30123 nach 2000 Runden"
    r = auswerten_text(text, 1, 1, "probe.txt", 100)
    assert r["ziel"] == 100 and r["ziel_tick"] == 30123 and r["wertung"] == "erreicht"
    setup, _ = einstellungen({"strategie": "beste", "ziel": "50,100"})
    assert "streitkolben=50,100" in setup, setup
    text = "\n".join(["CODE-KENNUNG abc", "ZIEL 50 Streitkolbenkaempfer erreicht bei Tick 26000", "NAECHSTES ZIEL 100",
                      "ZIEL 100 Streitkolbenkaempfer erreicht bei Tick 39000", "Ende Phase 2 bei Tick 39000 nach 900 Runden"])
    r = auswerten_text(text, 1, 1, "probe.txt", 100, [50, 100])
    assert r["stufen"] == {"50": 26000, "100": 39000} and r["ziel_tick"] == 39000, r
    print("OK   Auswertung und Zielweitergabe fuer 25, 50, 100 und gestuft 50,100")


if __name__ == "__main__":
    arg = argumente(sys.argv[1:])
    if arg.get("probe") == "ja":
        probe()
    elif arg.get("worker") == "ja":
        arbeiter(arg)
    else:
        koordinator(arg)
