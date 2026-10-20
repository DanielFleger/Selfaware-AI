# -*- coding: utf-8 -*-
"""Einheiten aufloesen und ersetzen - nachpruefen (04.10.2026, Daniel: "sollten schon gehen,
aber verifiziere das noch").

Aufloesen = Modulbefehl "aufloesen" (ruft disbandUnit des Spiels).
Ersetzen  = Modulbefehl "wandle" (Umwandlungsweg des Spiels, belegt 02.09. mit Bild).
Vorher festgelegt:
  AUFLOESEN gilt, wenn die Zahl des Typs beim Spieler um genau N sinkt und die N Plaetze
            danach Bauern (Typ 1) sind oder leer / neu belegt.
  ERSETZEN  gilt, wenn alle Einheiten des Typs beim Spieler zum Zieltyp werden und ihre
            Hoechst-Lebenspunkte (+0x3CC) sich aendern.
Beides gemessen nach 300 Ticks; dazu ein Bild nach dem Ersetzen.

Aufruf:  uv run python -m selfaware.tools.experiments.aufloesen_ersetzen "<Spielstand>" <sp>:<typ>:<anzahl> <sp>:<von>:<nach>
         z. B. "Walltest 4" 2:22:3 1:72:27
"""

from selfaware import workspace as _workspace
import io, json, os, re, sys, time

from selfaware.game.ucp.laden import lade_stand, befehl, peek
from selfaware.game.ucp.steuerkarte import laufe
from selfaware.tools.experiments.einheiten_steuern import liste
from selfaware.tools.experiments.navigation import bild

def anzahl(sp, typ):
    m = re.search(r"S%d:T%d=(\d+)" % (sp, typ), " ".join(befehl({"typen": {"spieler": sp}}, 1.0)))
    return int(m.group(1)) if m else 0

def einheit(nr):
    b = 0x0138854C + nr * 1168
    w = peek(b + 0x8C)[0]
    return {"zustand": w & 0xFFFF, "typ": (w >> 16) & 0xFFFF, "kennung": peek(b + 0x98)[0],
            "leben": peek(b + 0x3C8)[0], "max": peek(b + 0x3CC)[0]}

def main():
    stand = sys.argv[1]
    a_sp, a_typ, a_n = (int(v) for v in sys.argv[2].split(":"))
    e_sp, e_von, e_nach = (int(v) for v in sys.argv[3].split(":"))
    lade_stand(stand, mit_bild=False)
    bericht = {"stand": stand}
    # Aufloesen
    vor = anzahl(a_sp, a_typ)
    opfer = [nr for nr, _, _, _ in liste(spieler=a_sp, typ=a_typ)][:a_n]
    vorher = {nr: einheit(nr) for nr in opfer}
    print(befehl({"aufloesen": {"nr": opfer}}, 1.0))
    # Ersetzen
    e_vor, e_ziel_vor = anzahl(e_sp, e_von), anzahl(e_sp, e_nach)
    e_nr = [nr for nr, _, _, _ in liste(spieler=e_sp, typ=e_von)]
    e_vorher = {nr: einheit(nr) for nr in e_nr[:3]}
    print(befehl({"wandle": {"von": e_von, "nach": e_nach, "spieler": e_sp}}, 1.0))
    befehl({"tempo": 1000}, 0.5)
    laufe(300)
    nach = anzahl(a_sp, a_typ)
    nachher = {nr: einheit(nr) for nr in opfer}
    plaetze_ok = sum(1 for nr in opfer if nachher[nr]["typ"] == 1 or nachher[nr]["zustand"] == 0
                     or nachher[nr]["kennung"] != vorher[nr]["kennung"])
    a_gilt = (vor - nach) == a_n and plaetze_ok == a_n
    print("AUFLOESEN: Typ %d bei Spieler %d %d -> %d (soll -%d); Plaetze danach %s -> %s" % (
        a_typ, a_sp, vor, nach, a_n, [(nr, nachher[nr]["typ"], nachher[nr]["zustand"]) for nr in opfer],
        "GILT" if a_gilt else "NICHT"), flush=True)
    e_nach_von, e_nach_ziel = anzahl(e_sp, e_von), anzahl(e_sp, e_nach)
    e_nachher = {nr: einheit(nr) for nr in e_vorher}
    max_anders = all(e_nachher[nr]["max"] != e_vorher[nr]["max"] for nr in e_vorher)
    e_gilt = e_nach_von == 0 and e_nach_ziel - e_ziel_vor == e_vor and max_anders
    print("ERSETZEN: Typ %d %d -> %d, Typ %d %d -> %d; Hoechstleben vorher/nachher %s -> %s" % (
        e_von, e_vor, e_nach_von, e_nach, e_ziel_vor, e_nach_ziel,
        [(e_vorher[nr]["max"], e_nachher[nr]["max"]) for nr in e_vorher], "GILT" if e_gilt else "NICHT"), flush=True)
    befehl({"kamera": list(liste(nr=e_nr[:1])[0][2:4])}, 1.0)
    bild("ersetzen_nachher", vorsilbe="m10")
    bericht.update(aufloesen={"vorher": vor, "nachher": nach, "plaetze": nachher, "gilt": a_gilt},
                   ersetzen={"von": [e_vor, e_nach_von], "nach": [e_ziel_vor, e_nach_ziel],
                             "einheiten": {nr: [e_vorher[nr], e_nachher[nr]] for nr in e_vorher}, "gilt": e_gilt})
    io.open(os.path.join(_workspace.DATA, 'aufloesen_ersetzen_%s.json' % time.strftime('%H%M%S')), "w", encoding="utf-8").write(
        json.dumps(bericht, indent=1, default=str))

if __name__ == "__main__":
    main()
