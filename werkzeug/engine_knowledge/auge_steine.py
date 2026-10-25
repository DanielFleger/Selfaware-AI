# -*- coding: utf-8 -*-
"""B-252 / B-251 AU3: Stein-Flugbahn messen. Katapult (S_CATAPULT 39) + 2 Baumeister (E_ENGINEER 30) setzen, bemannen
({"angriff": {"einheiten": [...], "bemannen": nr}} - logik.lua 25.10., SAI), Gebaeude angreifen, Protokoll, dann je Stein
die Vorhersage sre_bahn (Landetakt, Landefeld, Hoehen) gegen die echten Werte halten.
Totschlagtest: Landetakt daneben > 3 Takte oder Landefeld > 1 Feld bei der Mehrheit der Steine = Stein-Formel falsch.
"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HIER))
sys.path.insert(0, HIER)
import auge  # noqa: E402
import shc  # noqa: E402
from laden import befehl  # noqa: E402
from auge_pruefen import freie_reihe  # noqa: E402

DATEN = os.path.join(os.path.dirname(os.path.dirname(HIER)), "daten")


def takt_vor(n=5):
    befehl({"pause": False, "tempo": 40}, 0.2)
    time.sleep(n / 100.0 + 0.2)
    befehl({"pause": True}, 0.2)


def main():
    dauer = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
    z = shc.zustand()
    print("Zustand:", z["text"])
    if z.get("gameover") or not z.get("pause"):
        print("FEHLER: nicht bespielbar/angehalten", z)
        return 1
    s = auge.Schnappschuss()
    ziel = sorted(s.gebaeude_liste((2,)), key=lambda g: (g["buildingType"] != 11, g["id"]))[0]
    print("Zielgebaeude", ziel["id"], "Typ", ziel["buildingType"], "bei", ziel["feld"], "Leben", ziel["currentHealth"])
    # setzeEinheit stellt die Einheit ein Feld weiter (x+1, y+1, gemessen 17.10.); updateUnits 0x00579300 raeumt Einheiten
    # auf Feldern ohne Wegnetz-Gebiet still ab (Lauf 155856: Katapult nach ~1000 Takten weg) - deshalb BEIDE Reihen pruefen
    import speicher
    k = speicher.wegkarte()
    reihe = None
    for versuch in range(40):
        r = freie_reihe((ziel["feld"][0], ziel["feld"][1] + 12 + versuch), 6, suchweite=25)
        if r and (k["gebiet"][r[1]:r[1] + 6, r[2] + 1] > 0).all() and (k["gebaeude"][r[1]:r[1] + 6, r[2] + 1] == 0).all():
            reihe = r
            break
    print("freie Reihe (beide Zeilen)", reihe)
    _, x0, y = reihe
    print(shc.setze("1", "39", str(x0), str(y), "1"))
    print(shc.setze("1", "30", str(x0 + 2), str(y), "2"))
    takt_vor(5)
    s = auge.Schnappschuss()
    for u in s.einheiten_liste((1,)):
        if u["unitType"] in (39, 30):
            fx, fy = u["feld"]
            print("  Einheit", u["id"], "Art", u["unitType"], "steht auf", (fx, fy), "Gebiet", int(k["gebiet"][fx, fy]), "Gebaeude", int(k["gebaeude"][fx, fy]))
    kat = [u for u in s.einheiten_liste((1,)) if u["unitType"] == 39]
    bau = [u for u in s.einheiten_liste((1,)) if u["unitType"] == 30]
    print("Katapult", [(u["id"], u["feld"]) for u in kat], "Baumeister", [(u["id"], u["feld"]) for u in bau])
    if not kat or len(bau) < 2:
        print("FEHLER: Einheiten fehlen")
        return 1
    k = kat[0]["id"]
    print("bemannen:", befehl({"angriff": {"einheiten": [u["id"] for u in bau], "bemannen": k}}, 1.0))
    befehl({"pause": False, "tempo": 40}, 0.2)
    time.sleep(4.0)
    befehl({"pause": True}, 0.2)
    import struct
    import speicher
    raw = speicher.lies(auge.UNITS + k * auge.UNIT_GROESSE, auge.UNIT_GROESSE)
    print("Katapult nach 400 Takten: countManning", struct.unpack_from("<h", raw, 948)[0], "manningEngineerRef",
          struct.unpack_from("<4h", raw, 788), "animationSpeed", struct.unpack_from("<i", raw, 68)[0])
    print("angriff:", befehl({"angriff": {"einheiten": [k], "gebaeude": ziel["id"]}}, 1.0))
    befehl({"pause": False, "tempo": 40}, 0.2)
    pfad, p = auge.protokollieren(dauer, (1, 2))
    befehl({"pause": True}, 0.2)
    print("Protokoll", len(p.takte), "Takte", min(p.takte), "..", max(p.takte), "->", pfad)
    return auswerten(pfad, k)


def auswerten(pfad, k=None):
    L = auge.Protokoll.laden(pfad)
    steine = {}
    for sn in L:
        for g in sn.geschosse():
            if g["entityType"] in (2, 3, 4):
                steine.setdefault(g["uid"], []).append((sn.takt, g))
    print("Steine gesehen", len(steine))
    erg = []
    for uid, r in steine.items():
        t0, g0 = r[0]
        bahn = g0.get("sre_bahn") or []
        land = bahn[-1] if bahn else None
        liegt = next(((t, x) for t, x in r if x["sre_zustand"] == "liegt"), None)
        letzt = r[-1]
        abw = []
        for t, x in r[1:]:
            b = next((b for b in bahn if b[0] == t - t0), None)
            if b and x["sre_zustand"] == "fliegt":
                abw.append((t - t0, x["jetzt_mikro"][2] - b[3], x["jetzt_mikro"][0] - b[1], x["jetzt_mikro"][1] - b[2]))
        e = {"uid": uid, "art": g0["sre_art"], "erst_takt": t0, "trav0": g0["travelledDistance"], "velocityUnk": g0["velocityUnk"],
             "startingAngle": g0["startingAngle"], "vCos": g0["vCos"], "vSin": g0["vSin"], "dt": g0["sre_mikroschritte_je_takt"],
             "start": g0["start"], "ziel_feld": g0["ziel_feld"], "gesamt": g0["field58_0x8c"],
             "landung_vorher": [t0 + land[0], land[4], land[5], land[6]] if land else None,
             "liegt_echt": [liegt[0], liegt[1]["jetzt_feld"][0], liegt[1]["jetzt_feld"][1], liegt[1]["jetzt_mikro"][2]] if liegt else None,
             "letzt": [letzt[0], letzt[1]["sre_zustand"], letzt[1]["jetzt_feld"], letzt[1]["jetzt_mikro"][2], letzt[1]["logicalState"]],
             "abweichung_takte": ((t0 + land[0]) - liegt[0]) if (land and liegt) else None,
             "abw_k_dh_dx_dy": abw[:3] + abw[-3:]}
        erg.append(e)
        print(json.dumps(e, ensure_ascii=False))
    aus = pfad.replace(".npz", "_steine.json")
    json.dump({"protokoll": os.path.basename(pfad), "katapult": k, "steine": erg}, open(aus, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("->", aus)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--nur_auswerten":
        sys.exit(auswerten(sys.argv[2]))
    sys.exit(main())
