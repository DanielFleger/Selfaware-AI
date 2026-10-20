# -*- coding: utf-8 -*-
"""Bauen und Anwerben wie ein Klick des Menschen - Bausteine und Probe (M11/M12, 04.10.2026).

Modulbefehle: "eigenerPlatz" (ohne ihn baut man still fuer den neutralen Spieler 0!), "baue",
"werbe", "vorrat", "gebaeude", "typen". Bau-Nummer und Groesse je Gebaeude aus
VillageStudio lib/gebaeude.json, Kosten aus der Tabelle im Spiel (0x01124CF4, int[110][5]:
Holz, Stein, Eisen, Pech, Gold; Index = Gebaeudetyp).
Gemessen 04.10.: 5 Holzfaellerhuetten -> Holz 150 -> 125 (5 x 5 laut Tabelle); Soeldnerposten
-> Gold -120; angeworben 1 arabischer Bogenschuetze (Typ 70). Belegter Platz -> nichts, kein Abzug.

Aufruf (Probe):  uv run python -m selfaware.game.ucp.bauen "<Spielstand>" [spieler=1]
Als Baustein:    from bauen import baue_irgendwo, werbe, vorrat, kosten
"""

from selfaware import workspace as _workspace
import io, json, os, re, sys

from selfaware.game.ucp.laden import lade_stand, befehl, peek
from selfaware.game.ucp.steuerkarte import laufe

GEBAEUDE = json.load(io.open(os.path.join(_workspace.VILLAGE_STUDIO, 'lib', 'gebaeude.json'), encoding="utf-8"))["gebaeude"]
NACH_TYP = {g["laufzeit"]: g for g in GEBAEUDE.values() if "laufzeit" in g and "mapper" in g}

def kosten(typ):
    return dict(zip(("holz", "stein", "eisen", "pech", "gold"), peek(0x01124CF4 + typ * 20, 5)))

def vorrat(sp=1):
    z = " ".join(befehl({"vorrat": sp}, 1.0))
    return {k.lower(): int(v) for k, v in re.findall(r"(\w+)=(-?\d+)", z.split(": ", 2)[-1])}

def gebaeude_von(sp, typ):
    z = " ".join(befehl({"gebaeude": {"spieler": sp, "typ": typ}}, 1.0))
    return [(int(n), int(x), int(y)) for n, x, y in re.findall(r"GEBAEUDE (\d+): Typ \d+, Spieler \d+, Ort \((\d+),(\d+)\)", z)]

def baue_irgendwo(typ, kandidaten, sp=1):
    """Versucht die Stellen der Reihe nach, bis das Spiel baut. Gibt (Nummer, x, y) oder None."""
    g = NACH_TYP[typ]
    vorher = {n for n, _, _ in gebaeude_von(sp, typ)}
    for x, y in kandidaten:
        befehl({"baue": {"mapper": g["mapper"], "x": x, "y": y, "groesse": g["b"], "richtung": 0}}, 0.8)
        laufe(5)
        neu = [e for e in gebaeude_von(sp, typ) if e[0] not in vorher]
        if neu:
            return neu[0]
    return None

def baue_viele(auftraege, sp=1, live=False):
    """Viele Bauten in EINER Befehlsliste (das Modul arbeitet eine Liste in einem Takt ab), dann eine Kontrolle
    je Gebaeudeart: gebaut = neues Gebaeude dieser Art genau an der Stelle. auftraege: [(typ, x, y), ...].
    Gibt (gebaut, fehl) - fehl z. B. weil gerade eine Einheit auf der Flaeche steht oder Holz fehlt."""
    from selfaware.game.ucp.befehl import sende, neue_id
    arten = sorted({t for t, _, _ in auftraege})
    vorher = {t: {n for n, _, _ in gebaeude_von(sp, t)} for t in arten}
    liste = []
    for t, x, y in auftraege:
        g = NACH_TYP[t]
        liste.append({"player": 1, "id": neue_id(), "baue": {"mapper": g["mapper"], "x": x, "y": y, "groesse": g["b"], "richtung": 0}})
    sende({"befehle": liste}, 1.0)
    if live:                    # Live-Partie (Daniel 05.10. 22:54 "ohne komische Pausen"): 2 Ticks abwarten, nicht anhalten
        import time
        from selfaware.game.ucp.steuerkarte import tick
        t0, ende = tick(), time.time() + 10
        while tick() < t0 + 2 and time.time() < ende:
            time.sleep(0.02)
    else:
        laufe(2)
    neu = {t: {(x, y): n for n, x, y in gebaeude_von(sp, t) if n not in vorher[t]} for t in arten}
    gebaut = [(t, x, y, neu[t][(x, y)]) for t, x, y in auftraege if (x, y) in neu[t]]
    fehl = [(t, x, y) for t, x, y in auftraege if (x, y) not in neu[t]]
    return gebaut, fehl

def platzkarte(typ, x0, y0, x1, y1, ziel, sp=1, hoechstens=900):
    """Spielpruefung fuer jede Stelle im Rechteck (Modulbefehl "platzkarte"); wartet auf die
    Fertig-Zeile im Log statt einer festen Zeit, kopiert die Karte nach ziel. Gibt (gut, alle, sekunden)."""
    import shutil, time
    from selfaware.game.ucp.befehl import LOG, SPIEL
    g = NACH_TYP[typ]
    vorher, t0 = os.path.getsize(LOG), time.time()
    befehl({"platzkarte": {"spieler": sp, "mapper": g["mapper"], "groesse": g["b"],
                           "x0": x0, "y0": y0, "x1": x1, "y1": y1}}, 0.5)
    while time.time() - t0 < hoechstens:
        with io.open(LOG, encoding="utf-8", errors="replace") as f:
            f.seek(vorher)
            m = re.search(r"PLATZKARTE .*?: (\d+) von (\d+) gehen", f.read())
        if m:
            from selfaware.game.ucp.befehl import ABZUG     # 19.10. (1v1): Abzug je Spieler (abzug_sp<N>)
            shutil.copy(os.path.join(ABZUG, "platzkarte.txt"), ziel)
            return int(m.group(1)), int(m.group(2)), round(time.time() - t0, 1)
        time.sleep(1.0)
    raise RuntimeError("platzkarte: keine Fertig-Zeile nach %d s" % hoechstens)

def werbe(einheitentyp, gebaeude_nr):
    befehl({"werbe": {"typ": einheitentyp, "gebaeude": gebaeude_nr}}, 0.8)

def probe(stand, sp):
    lade_stand(stand, mit_bild=False)
    befehl({"eigenerPlatz": sp}, 0.8)
    befehl({"tempo": 300}, 0.5)
    v0 = vorrat(sp)
    k = kosten(3)
    print("Holzfaellerhuette kostet %s; Holz vorher %d" % (k, v0["holz"]))
    # Gegenlauf: belegter Platz (Lager) - darf nichts bauen und nichts kosten
    lager = gebaeude_von(sp, 10)
    if lager:
        befehl({"baue": {"mapper": 51, "x": lager[0][1], "y": lager[0][2], "groesse": 3, "richtung": 0}}, 0.8)
        laufe(10)
        print("GEGENLAUF (auf dem Lager): Holz %d -> %d, Huetten %d -> %s" % (
            v0["holz"], vorrat(sp)["holz"], 0, len(gebaeude_von(sp, 3))))
    v1 = vorrat(sp)
    h = baue_irgendwo(3, [(186, 116), (190, 105), (180, 125)], sp)
    v2 = vorrat(sp)
    print("BAUEN: Huette %s; Holz %d -> %d (Soll -%d) -> %s" % (h, v1["holz"], v2["holz"], k["holz"],
          "GILT" if h and v1["holz"] - v2["holz"] == k["holz"] else "NICHT"))
    p = baue_irgendwo(8, [(195, 100), (200, 116), (170, 128)], sp)
    print("SOELDNERPOSTEN: %s, Gold %d -> %d" % (p, v2["gold"], vorrat(sp)["gold"]))
    if p:
        t0 = re.search(r"S%d:T70=(\d+)" % sp, " ".join(befehl({"typen": {"spieler": sp}}, 1.0)))
        werbe(70, p[0])
        laufe(50)
        t1 = re.search(r"S%d:T70=(\d+)" % sp, " ".join(befehl({"typen": {"spieler": sp}}, 1.0)))
        a, b = int(t0.group(1)) if t0 else 0, int(t1.group(1)) if t1 else 0
        print("ANWERBEN: arabische Bogenschuetzen %d -> %d -> %s" % (a, b, "GILT" if b == a + 1 else "NICHT"))

if __name__ == "__main__":
    probe(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1)
