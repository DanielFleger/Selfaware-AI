# -*- coding: utf-8 -*-
"""Serie: dieselbe Partie mehrmals spielen und je Lauf eine Zeile auswerten (Daniel 05.10. 20:12: "ja, mach mehrere
Laeufe mit beiden Instanzen"). Eine Partie ist kein Beweis - erst mehrere Laeufe je Planer-Stand zeigen, ob ein Sieg
wiederkommt oder Glueck war.

Instanz waehlt die Umgebung wie ueberall: SHC_INSTANZ=2 -> zweite Spielkopie, Sperre "villagestudio2".
Je Lauf:
  1. Testsperre der Instanz holen (sperre.py); ist sie von einer anderen Sitzung belegt, warten (hoechstens warte=Min.).
  2. Steht das Spiel am Ende-Bildschirm (Partie vorbei), ueber {"menue": 41} ins Hauptmenue (Fehlerhub mp-18: eine
     fertige Instanz wird ueber den Befehlskanal zurueckgesetzt, nicht abgeschossen). Gegenprobe: Ansicht = 41.
  3. erstes_spiel.py mit denselben Einstellungen wie 9t-9w (bis Tick 28.700); Zeitgrenze 25 Minuten, damit bei zwei
     Spielen nebeneinander der Tick das Ende bestimmt, nicht die Uhr.
  4. Zeile in daten/serie_<name>.txt: Ergebnis, Ende-Tick, Assassinen, zerstoerte Gebaeude, Gold aus Verkaeufen
     (Lose x gemessene Losgroesse), erste Eisenmine, gesetzte Bauten, Buchfuehrung (negative Runden).
Am Ende Sperre frei.

Aufruf:   SHC_INSTANZ=2 python serie.py name=x anzahl=4 [warte=60]
Auswerten (alle Konsolen eines Namens, beide Instanzen):  python serie.py auswerten name=x [auch=9t,9u,9v,9w]
"""
import glob, os, re, subprocess, sys, time
HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HIER, "..", "daten")
SPERRE = os.path.join(HIER, "..", "..", "VillageStudio", "werkzeug", "sperre.py")
LOS_GOLD = {"holz": 20, "stein": 25, "eisen": 135, "fleisch": 5, "apfel": 15}   # Gold je Verkauf, gemessen 05.10.
EINSTELLUNG = ["minuten=25", "tempo=1000", "waechter=ja", "assassinen=-1", "bis_tick=28700"]


def werte(pfad):
    """Eine Konsole -> dict mit den Kennzahlen (alles aus den Zeilen der Partie, nichts geschaetzt)."""
    t = open(pfad, encoding="utf-8", errors="replace").read()
    z = {"datei": os.path.basename(pfad)}
    m = re.search(r"SIEG bei Tick (\d+)", t)
    n = re.search(r"NIEDERLAGE bei Tick (\d+)", t)
    z["ergebnis"] = "SIEG %s" % m.group(1) if m else "NIEDERLAGE %s" % n.group(1) if n else "offen"
    m = re.search(r"Ende Phase 2 bei Tick (\d+)", t)
    z["ende"] = int(m.group(1)) if m else None
    a = re.findall(r"(\d+) Assassinen angeworben", t)
    z["assassinen"] = int(a[-1]) if a else 0
    m = re.search(r"Angriff: zerstoert (\d+)", t)
    z["zerstoert"] = int(m.group(1)) if m else None
    m = re.search(r"eigene Verluste (\d+)", t)
    z["verluste"] = int(m.group(1)) if m else None
    gold = 0
    for v in re.findall(r"verkauft: ([a-z, x0-9]+)", t):
        for teil in v.split(","):
            teil = teil.strip()
            w, _, k = teil.partition(" x")
            if w in LOS_GOLD:
                gold += LOS_GOLD[w] * (int(k) if k else 1)
    z["verkaufsgold"] = gold
    m = re.search(r"^ *(\d+) \|[^\n]*PLANER Eisenmine bei", t, re.M)
    z["erste_mine"] = int(m.group(1)) if m else None
    m = re.search(r"gesetzt (\{[^}]*\})", t)
    z["gesetzt"] = m.group(1) if m else "-"
    m = re.search(r"negative Zugaenge: holz (\d+) von (\d+) Runden[^;]*; stein (\d+)[^;]*; eisen (\d+)", t)
    z["negativ"] = "%s/%s/%s von %s" % (m.group(1), m.group(3), m.group(4), m.group(2)) if m else "-"
    # 20:21: der Fehlversuch ohne Pause endete mit "TESTBEDINGUNG FEHLT" und zaehlte als gueltiger Lauf mit 0 Assassinen
    z["fehler"] = "ja" if re.search(r"Traceback|ABBRUCH|TESTBEDINGUNG FEHLT", t) or z["ende"] is None else "nein"
    m = re.search(r"CODE-KENNUNG (\w+)", t)
    z["kennung"] = m.group(1) if m else "-"
    z.update(wirtschaft_werte(t))
    return z


def wirtschaft_werte(t):
    """Seasoning, Anwerben und Beliebtheit aus einer Konsole (Daniel 05.10. 23:41: Seasoning am Anfang, Nahrung fuer
    Beliebtheit und Verkauf). Alles aus den Zeilen der Partie; fehlt eine Zeile, steht None."""
    z = {}
    m = re.search(r"A-Plantagen reif bei Tick (\d+)", t)
    z["a_reif"] = int(m.group(1)) if m else None
    m = re.search(r"alle \d+ B-Plantagen stehen \(Tick (\d+)", t)
    z["b_steht"] = int(m.group(1)) if m else None
    m = re.search(r"SEASONING FRUEH: (\d+) von (\d+) A-Plantagen mit dem Posten bei Tick (\d+)", t)
    z["a_frueh"] = "%s/%s bei %s" % m.groups() if m else "-"
    m = re.search(r"RAID ZUERST:.*?(\d+) Assassinen angeworben.*?Tick (\d+)", t)
    erster = int(m.group(2)) if m and int(m.group(1)) > 0 else None
    zeilen = re.findall(r"^ *(\d+) \|[^\n]*?\| *([0-9.]+) \|[^\n]*", t, re.M)
    if erster is None:
        m = re.search(r"^ *(\d+) \|[^\n]*\b1 Assassinen? angeworben", t, re.M)
        erster = int(m.group(1)) if m else None
    z["assa_1"] = erster
    for n in (10, 20):
        m = re.search(r"^ *(\d+) \|[^\n]*\b%d Assassinen angeworben" % n, t, re.M)
        z["assa_%d" % n] = int(m.group(1)) if m else None
    # Tabellenzeile: Tick | Holz Stein Eisen | Aepfel Brot | Beliebt | ...
    tab = [(int(a), int(b), float(c)) for a, b, c in re.findall(r"^ *(\d+) \| +\d+ +\d+ +\d+ \| +(\d+) +\d+ \| +([0-9.]+) \|", t, re.M)]
    for marke in (5000, 10000, 20000):
        nach = [r for r in tab if r[0] >= marke]
        z["beliebt_%d" % (marke // 1000)] = nach[0][2] if nach else None
    z["aepfel_schnitt"] = round(sum(r[1] for r in tab) / len(tab), 1) if tab else None
    return z


def zeile(z):
    return "%-34s %-8s %-16s %6s %5d %5s %6d %8s  %-12s %-6s %s" % (
        z["datei"], z.get("kennung", "-"), z["ergebnis"], z["ende"], z["assassinen"], z["zerstoert"], z["verkaufsgold"], z["erste_mine"],
        z["negativ"], z["fehler"], z["gesetzt"])

KOPF = "%-34s %-8s %-16s %6s %5s %5s %6s %8s  %-12s %-6s %s" % ("Konsole", "Kennung", "Ergebnis", "Ende", "Assa", "zerst", "Gold", "1.Mine",
                                                        "neg H/S/E", "Fehler", "gesetzt")


def sperre(was, name, zweck=""):
    return subprocess.run([sys.executable, SPERRE, was, name] + ([zweck] if zweck else []), capture_output=True, text=True)


def zuruecksetzen():
    """Vor jedem Lauf: Partie vorbei -> Hauptmenue; dann Spiel PAUSIEREN, damit das Laden im ersten Takt anhaelt.
    (05.10. 20:16, Instanz 3 frisch gestartet: ohne Pause liefen nach dem Laden einige Takte, die Niederlage-Pruefung
    sah noch keinen Menschen und setzte gameOver = 1, bevor eigenerPlatz ankam - Meilensteine 30.09. 21:02.)"""
    import befehl as kanal
    from laden import peek, befehl, ANSICHT, HAUPTMENUE, PAUSE
    kanal.belege()
    try:
        ansicht, vorbei = peek(ANSICHT)[0], peek(0x0117D500)[0]
        text = "Ansicht %d" % ansicht
        # immer ueber das Hauptmenue laden (05.10. 20:46, Lauf l1: aus der laufenden Partie geladen hob das Laden die
        # Pause auf, die Niederlage-Pruefung setzte gameOver 1; aus dem Hauptmenue lief es bisher jedes Mal)
        if ansicht != HAUPTMENUE:
            befehl({"menue": HAUPTMENUE}, 2.0, bis="MENUE")
            # (21.10. 23:45: statt fest 2 s warten, bis die Ansicht wirklich das Hauptmenue ist - 10 s nur als Notbremse)
            ende = time.time() + 10
            neu = peek(ANSICHT)[0]
            while neu != HAUPTMENUE and time.time() < ende:
                time.sleep(0.05)
                neu = peek(ANSICHT)[0]
            if neu != HAUPTMENUE:
                raise RuntimeError("Hauptmenue nicht erreicht (Ansicht %d -> %d)" % (ansicht, neu))
            text = "Ansicht %d (Partie vorbei: %d) -> Hauptmenue" % (ansicht, vorbei)
        befehl({"pause": True}, 0.8)
        if peek(PAUSE)[0] != 1:
            raise RuntimeError("Spiel laesst sich nicht pausieren (Pause %d)" % peek(PAUSE)[0])
        return text + ", pausiert"
    finally:
        kanal.freigeben()


def serie(arg):
    inst = int(os.environ.get("SHC_INSTANZ", "1") or 1)
    # eigener Name, Instanz ueber SHC_INSTANZ (sperre.py): mit "villagestudio2" galt die Sperre einer anderen Sitzung
    # als die eigene - holen haette sie still uebernommen und freigeben sie geloescht (05.10. 20:13)
    os.environ["SHC_INSTANZ"] = str(inst)
    name = "SAI"
    kurz, anzahl, warte = arg.get("name", "x"), int(arg.get("anzahl", 3)), int(arg.get("warte", 60))
    # tempo/minuten einstellbar (05.10. 20:55): bei Tempo 1000 schafft der Lenker nur ~25 Runden je 1.000 Ticks
    global EINSTELLUNG
    EINSTELLUNG = [e for e in EINSTELLUNG if not e.startswith(("tempo=", "minuten="))] + [
        "tempo=%s" % arg.get("tempo", "1000"), "minuten=%s" % arg.get("minuten", "25")]
    aus = os.path.join(D, "serie_%s.txt" % kurz)
    if not os.path.exists(aus):
        open(aus, "w", encoding="utf-8").write("# Serie %s, Einstellung %s\n%s\n" % (kurz, " ".join(EINSTELLUNG), KOPF))
    try:
        for i in range(1, anzahl + 1):
            t0 = time.time()
            while True:
                r = sperre("holen", name, "SAI Serie %s Lauf %d/%d (Instanz %d)" % (kurz, i, anzahl, inst))
                if r.returncode == 0:
                    break
                if time.time() - t0 > 60 * warte:
                    print("ABBRUCH: Instanz %d seit %d Minuten belegt:\n%s" % (inst, warte, r.stdout), flush=True)
                    return
                print("Instanz %d belegt - warte 30 s (%s)" % (inst, r.stdout.strip().replace("\n", " | ")), flush=True)
                time.sleep(30)
            print("Lauf %d/%d auf Instanz %d: %s" % (i, anzahl, inst, zuruecksetzen()), flush=True)
            import kennung
            soll = kennung.kennung()[0]
            print("Lauf %d/%d: erwartete Code-Kennung %s" % (i, anzahl, soll), flush=True)
            konsole = os.path.join(D, "partie%s_%d_i%d_konsole.txt" % (kurz, i, inst))
            with open(konsole, "w", encoding="utf-8") as f:
                rc = subprocess.run([sys.executable, "-u", os.path.join(HIER, "erstes_spiel.py")] + EINSTELLUNG,
                                    stdout=f, stderr=subprocess.STDOUT, cwd=HIER, env=os.environ.copy()).returncode
            z = werte(konsole)
            if rc != 0:
                z["fehler"] = "rc %d" % rc
            if z["kennung"] != soll:
                z["fehler"] = "Kennung %s statt %s" % (z["kennung"], soll)
            open(aus, "a", encoding="utf-8").write(zeile(z) + "\n")
            print(zeile(z), flush=True)
            if z["fehler"] != "nein":
                print("ABBRUCH der Serie: Lauf %d hatte einen Fehler (%s) - Zustand bleibt stehen" % (i, z["fehler"]), flush=True)
                return
    finally:
        sperre("freigeben", name)
        print("Sperre %s frei" % name, flush=True)


def auswerten(arg):
    kurz = arg.get("name", "x")
    pfade = sorted(glob.glob(os.path.join(D, "partie%s_*_konsole.txt" % kurz)))
    for a in [x for x in arg.get("auch", "").split(",") if x]:
        pfade += glob.glob(os.path.join(D, "partie%s_konsole.txt" % a))
    alle = [werte(p) for p in pfade]
    print(KOPF)
    for z in alle:
        print(zeile(z))
    serie = [z for z in alle if z["datei"].startswith("partie%s_" % kurz) and z["fehler"] == "nein"]
    if serie:
        siege = [z for z in serie if z["ergebnis"].startswith("SIEG")]
        mittel = lambda k: sum(z[k] for z in serie if z[k] is not None) / max(1, sum(1 for z in serie if z[k] is not None))
        print("\nSerie %s: %d Laeufe ohne Fehler, %d Siege (%s); Mittel: Assassinen %.1f, zerstoert %.1f, Verkaufsgold %.0f, erste Mine %.0f" % (
            kurz, len(serie), len(siege), ", ".join(z["ergebnis"] for z in siege) or "-",
            mittel("assassinen"), mittel("zerstoert"), mittel("verkaufsgold"), mittel("erste_mine")))


if __name__ == "__main__":
    a = sys.argv[1:]
    befehl_ = a[0] if a and "=" not in a[0] else "serie"
    arg = dict(x.split("=", 1) for x in a if "=" in x)
    (auswerten if befehl_ == "auswerten" else serie)(arg)
