# -*- coding: utf-8 -*-
"""Gehorcht jede Einheitenart - und wenn nicht, warum? (v2, 04.10.2026)

v1 (01.10.) mass nur den Ort nach 300 Ticks; "gehorcht nicht" konnte drei Dinge heissen:
Befehl kommt nicht an / kommt an, wird aber ueberschrieben / Einheit zu langsam.
v2 schreibt mit der Einheiten-Wacht des Moduls jede Zielaenderung mit Tick mit.

Je Spieler und Typ eine Einheit (Typen aus dem Modulbefehl "typen", oder als Paare).
Zwei Laeufe aus demselben Spielstand (Laden ist wiederholbar, M7.03):
  Kontrolle: 300 Ticks ohne Befehl - was tut die Einheit von selbst?
  Versuch:   Befehl (naechstes gueltige Feld 12 Felder neben ihr; vier Richtungen), dann 300 Ticks.
Vorher festgelegt, je Einheit im Versuch:
  ANGENOMMEN     das erste Ziel nach dem Befehl ist das befohlene
  UEBERSCHRIEBEN das Ziel wechselt danach weg vom befohlenen, bevor sie ankommt (Tick, neues Ziel)
  ANGEKOMMEN     an einem 10-Tick-Punkt hoechstens 1 Feld vom Ziel
Urteil: GEHORCHT (angenommen + angekommen) / UMGELENKT (angenommen, vorher ueberschrieben) /
        ABGELEHNT (nicht angenommen) / LANGSAM (angenommen, nicht ueberschrieben, nicht angekommen).

Aufruf:  uv run python -m selfaware.tools.experiments.einheiten_steuern "<Spielstand>" [--ticks=600] [spieler:typ ...]
"""

from selfaware import workspace as _workspace
import io, json, os, re, sys, time

from selfaware.game.ucp.befehl import LOG
from selfaware.game.ucp.laden import lade_stand, befehl
from selfaware.game.ucp.steuerkarte import laufe

LAUF, ABSTAND = 300, 12
EINTRAG = re.compile(r"(\d+):T(\d+)@\((\d+),(\d+)\)")
ZIEL = re.compile(r"EW Tick (\d+): (\d+) Ziel \((-?\w+),(-?\w+)\)->\((-?\d+),(-?\d+)\) bei \((\d+),(\d+)\)")
ORTE = re.compile(r"EW Orte Tick (\d+): (.*)")

class Mitleser:
    def __init__(self):
        self.pos = os.path.getsize(LOG)
    def zeilen(self):
        with io.open(LOG, encoding="utf-8", errors="replace") as f:
            f.seek(self.pos); t = f.read(); self.pos = f.tell()
        return [z.split("| ", 1)[-1] for z in t.splitlines() if "EW " in z]

def liste(**g):
    z = " ".join(befehl({"gruppe": g}, 1.0))
    return [(int(a), int(b), int(c), int(d)) for a, b, c, d in EINTRAG.findall(z)]

def abstand(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def lauf_mit_wacht(nummern):
    befehl({"einheitwacht": {"nr": nummern, "alle": 10}}, 0.8)
    ml = Mitleser()
    laufe(LAUF)
    time.sleep(0.5)
    befehl({"einheitwacht": False}, 0.8)
    ziele, orte = {}, {}
    for z in ml.zeilen():
        m = ZIEL.search(z)
        if m:
            t, nr = int(m.group(1)), int(m.group(2))
            ziele.setdefault(nr, []).append((t, (int(m.group(5)), int(m.group(6))), (int(m.group(7)), int(m.group(8)))))
            continue
        m = ORTE.search(z)
        if m:
            t = int(m.group(1))
            for nr, x, y in re.findall(r"(\d+)@\((\d+),(\d+)\)", m.group(2)):
                orte.setdefault(int(nr), []).append((t, (int(x), int(y))))
    return ziele, orte

def main():
    global LAUF
    stand = sys.argv[1]
    rest = [a for a in sys.argv[2:] if not a.startswith("--ticks=")]
    LAUF = next((int(a[8:]) for a in sys.argv[2:] if a.startswith("--ticks=")), LAUF)
    lade_stand(stand, mit_bild=False)
    if rest:
        paare = [tuple(int(v) for v in p.split(":")) for p in rest]
    else:
        z = " ".join(befehl({"typen": {}}, 1.5))
        paare = [(int(s), int(t)) for s, t in re.findall(r"S(\d+):T(\d+)=", z) if int(s) >= 0]
    print("Typen:", paare, flush=True)
    proben = []
    for sp, typ in paare:
        l = liste(spieler=sp, typ=typ)
        if l:
            proben.append({"spieler": sp, "typ": typ, "nr": l[0][0], "start": (l[0][2], l[0][3])})
    nummern = [p["nr"] for p in proben]
    k_ziele, k_orte = lauf_mit_wacht(nummern)                         # Kontrolle
    lade_stand(stand, mit_bild=False)                                  # Versuch
    for p in proben:
        p["ziel"] = None
        for dx, dy in ((ABSTAND, 0), (0, ABSTAND), (-ABSTAND, 0), (0, -ABSTAND)):
            z = " ".join(befehl({"zielsuche": {"nr": p["nr"], "x": p["start"][0] + dx, "y": p["start"][1] + dy, "r": 5}}, 0.8))
            m = re.search(r"\((\d+),(\d+)\) gueltig", z)
            if m:
                p["ziel"] = (int(m.group(1)), int(m.group(2))); break
    v_ziele, v_orte = lauf_mit_wacht(nummern)
    print("%-3s %-4s %-5s %-11s %-11s %-10s %-34s %-8s %-6s %-6s %s" % ("Sp", "Typ", "Nr", "Start", "Ziel", "Kontrolle",
          "Versuch: Zielwechsel", "Ankunft", "Weg", "Rest", "Urteil"))
    for p in proben:
        nr, ziel = p["nr"], p["ziel"]
        kz, vz, vo = k_ziele.get(nr, []), v_ziele.get(nr, []), v_orte.get(nr, [])
        p["kontrolle_zielwechsel"] = len(kz) - 1 if kz else 0
        p["versuch_ziele"], p["versuch_orte"], p["kontrolle_orte"] = vz, vo, k_orte.get(nr, [])
        p["weitester_weg"] = max([abstand(o, p["start"]) for _, o in vo] or [0])
        p["naechster_abstand"] = min([abstand(o, ziel) for _, o in vo] or [None]) if ziel else None
        if ziel is None:
            p["urteil"] = "KEIN ZIEL"
        else:
            angenommen = bool(vz) and vz[0][1] == ziel
            ankunft = next((t for t, o in vo if abstand(o, ziel) <= 1), None)
            weg = next(((t, z) for t, z, _ in vz[1:] if z != ziel and (ankunft is None or t < ankunft)), None)
            p.update(angenommen=angenommen, ankunft=ankunft, umgelenkt=weg)
            p["urteil"] = ("ABGELEHNT" if not angenommen else "UMGELENKT" if weg else
                           "GEHORCHT" if ankunft is not None else "LANGSAM")
        wechsel = "; ".join("T%d->%s" % (t, z) for t, z, _ in vz[:3])
        print("%-3d %-4d %-5d %-11s %-11s %-10s %-34s %-8s %-6s %-6s %s" % (p["spieler"], p["typ"], nr, p["start"], ziel,
              "%d Wechsel" % p["kontrolle_zielwechsel"], wechsel[:34], p.get("ankunft"), p["weitester_weg"],
              p["naechster_abstand"], p["urteil"]), flush=True)
    io.open(os.path.join(_workspace.DATA, 'einheiten_steuern_v2_%s.json' % time.strftime('%H%M%S')), "w", encoding="utf-8").write(
        json.dumps({"stand": stand, "lauf": LAUF, "proben": proben}, indent=1, default=list))

if __name__ == "__main__":
    main()
