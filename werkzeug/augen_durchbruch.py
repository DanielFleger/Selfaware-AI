# -*- coding: utf-8 -*-
"""B-167 Test C (Daniel 21.10.2026 22:48: "Tests mit 20 Streitkolben - so schnell wie moeglich von der Mauer ab zum Lord und
diesen toeten, also den kuerzesten Weg durch die Mauern und direkt auf den Keep, sobald zugaenglich, gesehen im Code").
Sandkasten (Franz' Burg ohne Soldaten). 20 Streitkolben stehen gestapelt auf dem geraden Zugangsfeld der ersten Mauerkachel des
Durchbruch-Wegs von (150,150). Gesteuert wird JEDEN Takt aus dem Speicher (speicher.py), Befehle nur bei Aenderung:
  Mauer - die erste Mauerkachel auf dem Durchbruch-Weg (nur gerade Schritte, handleUnitMovementWhenTargetingBuildings), alle
          Lebenden einzeln (trupp 1) darauf; neue Kachel, sobald sie faellt (Mauerbit weg) oder der Weg sich aendert;
  Lord  - sobald der Lord im Gebiet der Truppe steht (Gebietsebene des Spiels, feindliche Tore geschnitten): alle einzeln auf ihn.
Abbruch nur aus dem Code: Lord tot; oder STILLSTAND = 2 x takte_je_treffer (mechanik.py) lang aendert sich nichts (keine Kachel
niedriger, kein Leben des Lords weniger, kein Mann auf ein anderes Feld).
Gemessen: je Kachel Takt des Falls, Treffer je 96 Takte (Zahl der Hoehenspruenge), Takt "Lord erreichbar", Lord-Leben ueber die
Zeit, Takt des Todes. Ergebnis: daten/augen_durchbruch.jsonl.   Aufruf: SHC_INSTANZ=5 python werkzeug/augen_durchbruch.py
"""
import json
import os
import re
import sys
import time

os.environ.setdefault("SHC_INSTANZ", "5")
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import numpy as np  # noqa: E402


import mechanik  # noqa: E402
import shc  # noqa: E402
import speicher  # noqa: E402
from laden import befehl  # noqa: E402
from waechter import lies_lagebild  # noqa: E402

AUS = os.path.join(HIER, "..", "daten", "augen_durchbruch.jsonl")
E0, ES = 0x0138854C, 1168
ZAHL = 20                      # Daniel 22:48


def einheit(raw, nr):
    b = nr * ES
    g = lambda o, n=2: int.from_bytes(raw[b + o:b + o + n], "little", signed=True)
    return {"x": g(0xC4), "y": g(0xC6), "zustand": g(0x8C), "leben": g(0x3C8, 4), "typ": g(0x8E), "besitzer": g(0x96),
            "ziel": g(0x3A8, 4), "schalter": raw[b + mechanik.E_TREFFER], "lage": g(0x2C0)}


def ebenen():
    wk = speicher.wegkarte()
    return {"link": wk["link"], "bau": wk["gebaeude"], "logik": speicher.ebene(speicher.LOGIK, 4),
            "besitz": speicher.ebene(speicher.BESITZ), "hoehe": speicher.ebene(speicher.HOEHE).astype(int),
            "boden": speicher.ebene(speicher.BODEN).astype(int)}


def plane(start, ziel, maenner, mk):
    e = ebenen()
    return mechanik.durchbruch_schritte(e["link"], e["logik"], e["bau"], e["besitz"], e["hoehe"], e["boden"], 1, maenner,
                                        start, ziel, mk)


def blick_fuer(kachel):
    """Blickrichtung 0-7, bei der das Spiel fuer die Anfrage kachel genau kachel waehlt (Nachbildung mechanik.spiel_wahl); None ohne."""
    acht, blick = mechanik.richtungen()
    wk = speicher.wegkarte()
    logik, besitz = speicher.ebene(speicher.LOGIK, 4), speicher.ebene(speicher.BESITZ)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        f = (kachel[0] + dx, kachel[1] + dy)
        if wk["gebiet"][f] and not logik[f] & 0x10000300:
            g_mann = int(wk["gebiet"][f])
            break
    else:
        return None
    for i in range(8):
        _, w = mechanik.spiel_wahl(kachel, g_mann, wk["gebiet"], logik, wk["gebaeude"], {}, besitz, 1, acht, blick[i])
        if w == tuple(kachel):
            return i
    return None


def main():
    print("OK:", shc.sandkasten(nur_soldaten="ja"), flush=True)
    befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
    L = lies_lagebild(neu_holen=False)
    lnr, le = next((k, e) for k, e in L.items() if e["typ"] == 55 and e["besitzer"] == 2 and e["leben"] > 0)
    lp = (le["x"], le["y"])

    mk = mechanik.streitkolben()
    pl = plane((150, 150), lp, ZAHL, mk)
    if not pl["weg"]:
        raise SystemExit("UNGUELTIG: kein Weg zum Lord (auch nicht durch Mauern)")
    wand = pl["mauern"]
    zugang = pl["weg"][pl["weg"].index(wand[0]) - 1] if wand else pl["weg"][-2]
    vor = {"takte_gesamt": pl["takte"], "mauern": wand, "weg_felder": len(pl["weg"])}
    print("Lord %d bei %s (Leben %d) | Durchbruch-Weg: %d Mauerkacheln %s | Zugang %s" % (
        lnr, lp, le["leben"], len(wand), wand, zugang), flush=True)
    print("VORHERSAGE (Code + gemessene 12 Takte je Feld, %d Mann):" % ZAHL, vor, flush=True)
    t = shc.setze(spieler=1, typ=26, x=zugang[0] - 1, y=zugang[1] - 1, anzahl=ZAHL)
    nrs = [int(x) for x in re.search(r"Nummern \[([0-9, ]+)\]", t).group(1).split(",")]
    lies = speicher.lies
    xs_, ys_, ks_ = speicher.felder()
    kxy = {int(kk): (int(xx), int(yy)) for xx, yy, kk in zip(xs_, ys_, ks_)}
    kvon = {v: k for k, v in kxy.items()}
    tick0 = int.from_bytes(lies(shc.TICK, 4), "little")
    phase, kachel, ereignisse, spur = "mauer", None, [], []
    letzt_t, still, zustand_alt, neu_planen, gesendet = None, 0, None, True, {}
    befehl({"pause": False, "tempo": 40}, 0.2)
    while True:
        tk = int.from_bytes(lies(shc.TICK, 4), "little")
        if tk == letzt_t:
            continue
        letzt_t = tk
        t_ = tk - tick0
        raw = lies(E0, (max(nrs + [lnr]) + 1) * ES)
        leute = {n: einheit(raw, n) for n in nrs}
        leute = {n: e for n, e in leute.items() if e["leben"] > 0 and e["typ"] == 26}
        lord = einheit(raw, lnr)
        if lord["leben"] <= 0 or lord["typ"] != 55:
            ereignisse.append((t_, "LORD TOT"))
            break
        if not leute:
            ereignisse.append((t_, "ALLE TOT"))
            break
        felder = [(e["x"], e["y"]) for e in leute.values()]
        if phase == "mauer" and kachel is not None:
            k = kvon[kachel]
            if not int.from_bytes(lies(speicher.LOGIK + 4 * k, 4), "little") & 0x100:
                ereignisse.append((t_, "KACHEL %s GEFALLEN" % (kachel,)))
                neu_planen = True
        if phase == "mauer" and neu_planen:
            neu_planen = False
            mitte = (sorted(q[0] for q in felder)[len(felder) // 2], sorted(q[1] for q in felder)[len(felder) // 2])
            beginn = min(felder, key=lambda q: max(abs(q[0] - mitte[0]), abs(q[1] - mitte[1])))
            pl = plane(beginn, lp, len(leute), mk)
            kachel = pl["mauern"][0] if pl["weg"] and pl["mauern"] else None
            h = speicher.ebene(speicher.HOEHE).astype(int) - speicher.ebene(speicher.BODEN).astype(int)
            if kachel is None and not pl["weg"]:
                ereignisse.append((t_, "KEIN WEG zum Lord von %s" % (beginn,)))
                break
            if kachel is None:
                # B-167 (Test C 22:55: Weg frei, aber der Lord stand nie "im Gebiet der Truppe" - Bergfried eigenes Gebiet):
                # keine Mauer mehr auf dem Durchbruch-Weg = auf den Lord
                phase = "lord"
                ereignisse.append((t_, "WEG FREI - alle einzeln auf den Lord"))
                befehl({"angriff": {"einheiten": sorted(leute), "ziel": lnr, "trupp": 1}}, 1.0)
                gesendet = {n: (leute[n]["zustand"], leute[n]["ziel"]) for n in leute}
            else:
                ereignisse.append((t_, "KACHEL %s (Hoehe ueber Boden %d), noch %d Mauerkacheln auf dem Weg, Weg %s Takte" % (
                    kachel, h[kachel], len(pl["mauern"]), pl["takte"])))
                blick_k = blick_fuer(kachel)
                ereignisse.append((t_, "BLICK %s fuer Kachel %s (Nachbildung findFreeSpace...)" % (blick_k, kachel)))
                befehl({"angriff": {"einheiten": sorted(leute), "mauer": [lp[0], lp[1], 2, 30, kachel[0], kachel[1]]
                                    + ([blick_k] if blick_k is not None else []), "trupp": 1}}, 1.0)
                gesendet = {n: (leute[n]["zustand"], leute[n]["ziel"]) for n in leute}
        # Neu senden nur, wenn das Spiel den letzten Befehl dieses Manns sichtbar verarbeitet hat (Zustand oder Ziel anders als
        # beim Senden) und es trotzdem nicht passt - kein fester Takt
        verarbeitet = lambda n: gesendet.get(n) is None or gesendet[n] != (leute[n]["zustand"], leute[n]["ziel"])
        if phase == "mauer" and kachel is not None:
            # Regelung ueber die Messung: wer nicht DIESE Kachel als Ziel hat, bekommt den Befehl neu - je Mann hoechstens einmal
            # je takte_je_treffer (Code: ein Treffer je 96 Takte)
            k = kvon[kachel]
            falsch = [n for n, e in leute.items() if e["ziel"] != k and verarbeitet(n)]
            if falsch:
                befehl({"angriff": {"einheiten": sorted(falsch), "mauer": [lp[0], lp[1], 2, 30, kachel[0], kachel[1]]
                                    + ([blick_k] if blick_k is not None else []), "trupp": 1}}, 1.0)
                for n in falsch:
                    gesendet[n] = (leute[n]["zustand"], leute[n]["ziel"])
        if phase == "lord":
            ohne = [n for n, e in leute.items() if e["zustand"] in (0, 1) and verarbeitet(n)]
            if ohne:
                befehl({"angriff": {"einheiten": sorted(ohne), "ziel": lnr, "trupp": 1}}, 1.0)
                for n in ohne:
                    gesendet[n] = (leute[n]["zustand"], leute[n]["ziel"])
        hk = lies(speicher.HOEHE + kvon[kachel], 1)[0] if kachel is not None else -1
        # (Code: wer im Mauerangriff steht, schwingt alle takte_je_schwung - nextAttackHurtsWall wechselt; wer schwingt, steht
        # nicht still. Stillstand = 96 Takte kein Schwung, kein Feldwechsel, keine Kachel niedriger, kein Lord-Schaden)
        # Code (UpdateMaceman, state.generic +0x2C0): 107 = US_MELEE_ATTACK_WALL - wer darin steht, arbeitet (erster Schwung ohne
        # Schaden, Treffer alle 96 Takte). Stillstand nur, wenn niemand in 107 ist, niemand das Feld wechselt und nichts Schaden nimmt
        hacken = any(e["lage"] == 107 for e in leute.values())
        zustand = (tuple(sorted(felder)), hk, lord["leben"])
        still = still + 1 if zustand == zustand_alt and not hacken else 0
        zustand_alt = zustand
        zz = {}
        for e in leute.values():
            zz[e["ziel"]] = zz.get(e["ziel"], 0) + 1
        spur.append((t_, phase, kachel, hk, lord["leben"], len(leute), sorted(zz.items(), key=lambda kv: -kv[1])[:4]))
        if still > mk["takte_je_treffer"]:
            ereignisse.append((t_, "STILLSTAND %d Takte (Phase %s, Kachel %s, Zustaende %s, Ziele %s)" % (
                still, phase, kachel, sorted({e["zustand"] for e in leute.values()}), spur[-1][6])))
            break
    befehl({"pause": True}, 0.3)
    luecken = sum(1 for a, b in zip(spur, spur[1:]) if b[0] - a[0] != 1)
    erg = {"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "zahl": ZAHL, "lord": lnr, "lord_bei": lp, "zugang": zugang, "code": mk,
           "vorhersage": vor, "ereignisse": ereignisse, "takte": spur[-1][0] if spur else None, "luecken": luecken,
           "spur": spur[::10]}
    xs_, ys_, ks_ = speicher.felder()
    kxy = {int(kk): (int(xx), int(yy)) for xx, yy, kk in zip(xs_, ys_, ks_)}
    alle_ziele = {}
    for r in spur:
        for z_, n_ in r[6]:
            alle_ziele[str(kxy.get(z_, z_))] = alle_ziele.get(str(kxy.get(z_, z_)), 0) + n_
    erg["ziele_mann_takte"] = alle_ziele
    print("TATSAECHLICHE ZIELE (Kachel: Mann-Takte):", sorted(alle_ziele.items(), key=lambda kv: -kv[1])[:12], flush=True)
    for e in ereignisse:
        print("  Takt %6d  %s" % e, flush=True)
    print("Takte %s, Luecken %d, Lebende am Ende %s" % (erg["takte"], luecken, spur[-1][5] if spur else None), flush=True)
    with open(AUS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(erg, ensure_ascii=False, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)) + "\n")


if __name__ == "__main__":
    main()
