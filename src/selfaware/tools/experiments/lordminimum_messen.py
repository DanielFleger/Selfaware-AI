# -*- coding: utf-8 -*-
"""Wiederholbare Messreihe fuer die kleinste wirksame Assassinen-Gruppe.

Jede Groesse startet dreimal aus demselben gespeicherten Stand. Die Gruppen sind ineinander enthalten:
zuerst die gesuendesten Assassinen, bei Gleichstand die kleinste feste Nummer. Alle uebrigen bleiben am sicheren
Sammelpunkt. Ein Ergebnis gilt spaeter nur dann als belegt, wenn alle drei Wiederholungen gleich ausgehen.

Aufruf: uv run python -m selfaware.tools.experiments.lordminimum_messen [stand="SAI Lordminimum Basis 2026-10-06"]
        [groessen=5,10,15,20,25,30,35,40] [wiederholungen=3] [tempo=1000] [ticks=3500]
"""

from selfaware import workspace as _workspace
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))

from selfaware.micro.tasks.assassinen import Einzeln
from selfaware.game.ucp.befehl import neue_id, sende, INSTANZ
import selfaware.game.ucp.befehl as kanal
from selfaware.runtime.live.erstes_spiel import runde_lesen, pruefe_begehbar, wegtest, ROHSTOFFE
from selfaware.game.ucp.laden import lade_stand, befehl, peek

D = os.path.join(_workspace.DATA)
SP = 1


def auswahl(L, groesse):
    alle = [n for n, e in L.items() if e["besitzer"] == SP and e["typ"] == 73]
    return sorted(alle, key=lambda n: (-L[n]["leben"], n))[:groesse]


def vorbereiten(stand, groesse, mindestens=None):
    """Trainingsstand laden, pruefen und die Gruppe freigeben; die uebrigen bleiben ausser Schussweite stehen.
    Gibt (status, einheiten, gebaeude, truppe, lord_nr, lord). Auch von zielfeld_suchen.py benutzt."""
    lade_stand(stand, mit_bild=False)   # 06.10.: die Lade-Pruefung wartet jetzt auf die Lade-Meldung (laden.py)
    befehl({"eigenerPlatz": SP}, 0.8)
    st, L, G = runde_lesen()
    lords = [(n, e) for n, e in L.items() if e["typ"] == 55 and e["besitzer"] not in (0, SP)]
    if st.get("ansicht") != 14 or st.get("over") != 0 or not lords:
        raise RuntimeError("Trainingsstand ungueltig: %s, feindliche Lords %d" % (st, len(lords)))
    vorhanden = [n for n, e in L.items() if e["besitzer"] == SP and e["typ"] == 73]
    if len(vorhanden) < (mindestens or groesse):
        raise RuntimeError("Trainingsstand hat nur %d Assassinen (gebraucht %d)" % (len(vorhanden), mindestens or groesse))
    ln, le = lords[0]
    lp = (le["x"], le["y"])
    truppe = auswahl(L, groesse)
    uebrig = sorted(set(vorhanden) - set(truppe))
    sx = round(sum(L[n]["x"] for n in vorhanden) / len(vorhanden))
    sy = round(sum(L[n]["y"] for n in vorhanden) / len(vorhanden))
    # Die Nichtteilnehmer bleiben ausser Schussweite am identischen Startort; die feste Untermenge wird freigegeben.
    liste = []
    if uebrig:
        liste.append({"halten": {"nr": uebrig, "x": sx, "y": sy}})
    liste.append({"halten": {"los": truppe}})
    sende({"befehle": [dict(x, player=SP, id=neue_id()) for x in liste]}, 1.0, bis="HALTEN")
    return st, L, G, truppe, ln, le


def lauf(stand, groesse, nummer, tempo, dauer):
    st, L, G, truppe, ln, le = vorbereiten(stand, groesse)
    pfad = os.path.join(D, "lordminimum_%02d_%d_%s_i%d.jsonl" % (
        groesse, nummer, time.strftime("%Y%m%d_%H%M%S"), INSTANZ))
    mess = Einzeln(SP, pruefe_begehbar=pruefe_begehbar, wegtest=wegtest)
    mess.mitglieder = set(truppe)
    mess.lordtrupp.update(mitglieder=set(truppe), phase="angriff", lord=ln)
    mess.wellen_protokoll = pfad
    mess.gelaende = open(ROHSTOFFE, encoding="utf-8").read().splitlines()[1:] if os.path.exists(ROHSTOFFE) else []
    mess.angriffe.append({"runde": 0, "groesse": groesse, "lord_vorher": le["leben"], "lord_nachher": le["leben"],
                          "fern": 0, "nah": 0, "weg_min": 0, "weg_max": 0, "am_lord_max": 0,
                          "erreicht_runde": None, "anderes": {}, "truppe": set(truppe), "verluste": 0,
                          "leben_zuletzt": {n: L[n]["leben"] for n in truppe}})
    start, letzter_lord, ursache = st["t"], le["leben"], "Zeitgrenze"
    befehl({"tempo": tempo}, 0.5)
    befehl({"pause": False}, 0.5)
    while True:
        st, L, G = runde_lesen()
        feindlord = next(((n, e) for n, e in L.items() if e["typ"] == 55 and e["besitzer"] not in (0, SP)), None)
        lebend = [n for n in truppe if n in L and L[n]["besitzer"] == SP]
        mess.mitglieder = set(lebend)
        if feindlord is None:
            ursache = "Sieg"
            break
        ln, le = feindlord
        letzter_lord = le["leben"]
        mess.runde += 1
        fern, nah = mess._feinde(L)
        mess._lord_messen(L, G, ln, le, (le["x"], le["y"]), fern, nah)
        if st.get("over") != 0:
            ursache = "Spielende"
            break
        if not lebend:
            ursache = "Angreifer tot"
            break
        if st["t"] - start >= dauer:
            break
        befehl({"angriff": {"einheiten": lebend, "ziel": ln}}, 0.8, bis="ANGRIFF")
    befehl({"pause": True}, 0.5)
    ergebnis = {"groesse": groesse, "wiederholung": nummer, "start_tick": start, "ende_tick": st.get("t"),
                "ausgang": ursache, "sieg": ursache == "Sieg", "lord_start": mess.angriffe[0]["lord_vorher"],
                "lord_ende": 0 if ursache == "Sieg" else letzter_lord, "ueberlebt": len([n for n in truppe if n in L]),
                "auswahl": truppe, "protokoll": os.path.basename(pfad)}
    print(json.dumps(ergebnis, ensure_ascii=False), flush=True)
    return ergebnis


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    stand = arg.get("stand", "SAI Lordminimum Basis 2026-10-06")
    groessen = [int(x) for x in arg.get("groessen", "5,10,15,20,25,30,35,40").split(",")]
    wiederholungen = int(arg.get("wiederholungen", 3))
    tempo, dauer = int(arg.get("tempo", 1000)), int(arg.get("ticks", 3500))
    alle = []
    for groesse in groessen:
        for nummer in range(1, wiederholungen + 1):
            alle.append(lauf(stand, groesse, nummer, tempo, dauer))
    ausgabe = os.path.join(D, "lordminimum_ergebnis_%s_i%d.json" % (time.strftime("%Y%m%d_%H%M%S"), INSTANZ))
    with open(ausgabe, "w", encoding="utf-8") as f:
        json.dump({"stand": stand, "groessen": groessen, "wiederholungen": wiederholungen, "laeufe": alle}, f,
                  ensure_ascii=False, indent=2)
    for groesse in groessen:
        r = [x for x in alle if x["groesse"] == groesse]
        ausgaenge = ["S" if x["sieg"] else "N" for x in r]
        standfest = len(set(ausgaenge)) == 1
        print("%2d: %s -> %s" % (groesse, "".join(ausgaenge), "belegt" if standfest else "OFFEN"))
    print("Ergebnis:", ausgabe)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
