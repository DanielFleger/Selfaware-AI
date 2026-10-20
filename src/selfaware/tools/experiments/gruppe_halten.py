# -*- coding: utf-8 -*-
"""Gruppe zurueckrufen, festhalten, loslassen, einfrieren (v2, 04.10.2026).

Daniel: "alle Apfelbauern pausieren jetzt und laufen zurueck zum Kornspeicher - koennte
spaeter relevant sein, wenn ein Bogenschuetze kommt."
v1 (18:55) zeigte: Einfrieren und Halten gelten; Zurueckrufen in 600 Ticks zu kurz fuer ferne
Plantagen; nach blossem Loslassen nahmen 18 von 24 keine Arbeit wieder auf.
v2: Phasen 1200 Ticks, Tempo fest 1000, zwei Arten loszulassen nebeneinander, Orte gespeichert.

Modulbefehle: "halten" (festhalten, "hier", "zu", false, "zurueck"), "einheitwacht".
Vorher festgelegt (Anteil der Gruppe):
  EINFRIEREN    >= 90 % bewegen sich in 300 Ticks hoechstens 1 Feld; ohne Halten die meisten mehr
  ZURUECKRUFEN  >= 90 % stehen binnen 1200 Ticks hoechstens 3 Felder vom Gebaeude-Eingang
  HALTEN        wer ankam, steht am Ende der Haltezeit noch dort
  ARBEITET WIEDER (je Loslass-Art, 1200 Ticks danach): ein Ziel ungleich Eingang UND am Ende
                >= 3 Felder vom Eingang - gilt, wenn >= 90 %
Vermutung vorher: blosses Loslassen scheitert, "zurueck" (altes Ziel wiederherstellen) gelingt.

Aufruf:  uv run python -m selfaware.tools.experiments.gruppe_halten "<Spielstand>" <spieler> <einheitentyp> <gebaeudetyp> [frei|zurueck|arbeit]
         (letztes Argument: nur diese Loslass-Art, ohne Einfrieren)
"""

from selfaware import workspace as _workspace
import io, json, os, re, sys, time

import selfaware.tools.experiments.einheiten_steuern as es
from selfaware.game.ucp.laden import lade_stand, befehl
from selfaware.tools.experiments.einheiten_steuern import liste, abstand

def phase(nummern, ticks):
    befehl({"tempo": 1000}, 0.5)
    alt, es.LAUF = es.LAUF, ticks
    try:
        return es.lauf_mit_wacht(nummern)
    finally:
        es.LAUF = alt

def ende(orte, nr):
    o = orte.get(nr)
    return o[-1][1] if o else None

def anteil(n, von):
    return "%d von %d" % (n, von)

def zurueckrufen(stand, sp, typ, gtyp, gruppe, eingang, start):
    lade_stand(stand, mit_bild=False)
    print(befehl({"halten": {"spieler": sp, "typ": typ, "zu": gtyp}}, 1.0), flush=True)
    _, orte = phase(gruppe, 1200)
    ankunft = {nr: next((t for t, o in orte.get(nr, []) if abstand(o, eingang) <= 3), None) for nr in gruppe}
    return ankunft, orte

def loslassen(art, gruppe, eingang):
    los = {"frei": {"halten": False}, "zurueck": {"halten": {"zurueck": True}}, "arbeit": {"halten": {"zurueck": "arbeit"}}}[art]
    z = " ".join(befehl(los, 1.0))
    print("  " + z, flush=True)
    ziele, orte = phase(gruppe, 1200)
    arbeitet = {}
    for nr in gruppe:
        anderes = any(zz != eingang for _, zz, _ in ziele.get(nr, []))
        e = ende(orte, nr)
        arbeitet[nr] = bool(anderes and e and abstand(e, eingang) >= 3)
    return arbeitet, ziele, orte

def main():
    stand, sp, typ, gtyp = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    lade_stand(stand, mit_bild=False)
    gruppe = [nr for nr, _, _, _ in liste(spieler=sp, typ=typ)]
    start = {nr: (x, y) for nr, _, x, y in liste(nr=gruppe)}
    m = re.search(r"Eingang \((\d+),(\d+)\)", " ".join(befehl({"gebaeude": {"spieler": sp, "typ": gtyp}}, 1.0)))
    eingang = (int(m.group(1)), int(m.group(2)))
    n = len(gruppe)
    print("Gruppe: %d Einheiten Typ %d von Spieler %d; Eingang Gebaeude Typ %d bei %s; Entfernung %d-%d Felder" % (
        n, typ, sp, gtyp, eingang, min(abstand(s, eingang) for s in start.values()),
        max(abstand(s, eingang) for s in start.values())), flush=True)
    bericht = {"stand": stand, "spieler": sp, "typ": typ, "gebaeude": gtyp, "eingang": eingang, "start": start}

    arten = [sys.argv[5]] if len(sys.argv) > 5 else ["frei", "zurueck"]
    if len(sys.argv) <= 5:
        einfrieren(stand, sp, typ, gruppe, start, n, bericht)
    for art in arten:
        lauf_art(art, stand, sp, typ, gtyp, gruppe, eingang, start, n, bericht)
    io.open(os.path.join(_workspace.DATA, 'gruppe_halten_v2_%s.json' % time.strftime('%H%M%S')), "w", encoding="utf-8").write(
        json.dumps(bericht, indent=1, default=str))

def einfrieren(stand, sp, typ, gruppe, start, n, bericht):
    _, k_orte = phase(gruppe, 300)
    lade_stand(stand, mit_bild=False)
    befehl({"halten": {"spieler": sp, "typ": typ, "hier": True}}, 1.0)
    _, f_orte = phase(gruppe, 300)
    befehl({"halten": False}, 0.8)
    still = sum(1 for nr in gruppe if max([abstand(o, start[nr]) for _, o in f_orte.get(nr, [])] or [0]) <= 1)
    bewegt = sum(1 for nr in gruppe if max([abstand(o, start[nr]) for _, o in k_orte.get(nr, [])] or [0]) > 1)
    print("EINFRIEREN: mit Halten %s hoechstens 1 Feld bewegt, ohne Halten %s mehr -> %s" % (
        anteil(still, n), anteil(bewegt, n), "GILT" if still >= 0.9 * n and bewegt > n / 2 else "NICHT"), flush=True)
    bericht["einfrieren"] = {"still": still, "ohne_bewegt": bewegt}

def lauf_art(art, stand, sp, typ, gtyp, gruppe, eingang, start, n, bericht):
        ankunft, r_orte = zurueckrufen(stand, sp, typ, gtyp, gruppe, eingang, start)
        da = sum(1 for v in ankunft.values() if v is not None)
        noch = sum(1 for nr in gruppe if ende(r_orte, nr) and abstand(ende(r_orte, nr), eingang) <= 3)
        print("[%s] ZURUECKRUFEN: %s binnen 1200 Ticks <= 3 Felder vom Eingang -> %s; HALTEN: am Ende %s dort -> %s" % (
            art, anteil(da, n), "GILT" if da >= 0.9 * n else "NICHT", anteil(noch, n),
            "GILT" if noch >= da and da > 0 else "NICHT"), flush=True)
        arbeitet, l_ziele, l_orte = loslassen(art, gruppe, eingang)
        w = sum(arbeitet.values())
        print("[%s] ARBEITET WIEDER nach 1200 Ticks: %s -> %s" % (art, anteil(w, n), "GILT" if w >= 0.9 * n else "NICHT"), flush=True)
        bericht[art] = {"angekommen": da, "ankunft": ankunft, "am_ende_dort": noch, "arbeitet_wieder": w,
                        "arbeitet": arbeitet, "ziele_nach_loslassen": l_ziele, "orte_rueckruf": r_orte, "orte_nach": l_orte}

if __name__ == "__main__":
    main()
