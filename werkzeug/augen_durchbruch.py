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
    return {"link": wk["link"], "bau": wk["gebaeude"], "gebiet": wk["gebiet"], "logik": speicher.ebene(speicher.LOGIK, 4),
            "besitz": speicher.ebene(speicher.BESITZ), "hoehe": speicher.ebene(speicher.HOEHE).astype(int),
            "boden": speicher.ebene(speicher.BODEN).astype(int)}


def plane(start, ziel, maenner, mk):
    e = ebenen()
    return mechanik.durchbruch_schritte(e["link"], e["logik"], e["bau"], e["besitz"], e["hoehe"], e["boden"], 1, maenner,
                                        start, ziel, mk)


def anfrage_und_blick(kachel):
    """(Anfrage-Kachel, Blickrichtung), bei denen das Spiel GENAU kachel als Ziel waehlt (Nachbildung mechanik.spiel_wahl von
    findFreeSpaceNextToEnemyDefensiveStructureInSameAreaWithinDistance): kachel selbst zuerst, dann jede Mauerkachel bis 2 Felder
    daneben, je 8 Blickrichtungen. None, wenn es keine gibt - dann geht KEIN Befehl raus (Daniel 23:20 "alle auf eine Mauer,
    nicht random andere Ziele")."""
    acht, blick = mechanik.richtungen()
    wk = speicher.wegkarte()
    logik, besitz = speicher.ebene(speicher.LOGIK, 4), speicher.ebene(speicher.BESITZ)
    kand = [tuple(kachel)] + [(kachel[0] + dx, kachel[1] + dy) for dx in range(-2, 3) for dy in range(-2, 3)
                              if (dx or dy) and logik[kachel[0] + dx, kachel[1] + dy] & 0x10000300]
    for r in kand:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            f = (r[0] + dx, r[1] + dy)
            if wk["gebiet"][f] and not logik[f] & 0x10000300:
                g_mann = int(wk["gebiet"][f])
                break
        else:
            continue
        for i in range(8):
            _, w = mechanik.spiel_wahl(r, g_mann, wk["gebiet"], logik, wk["gebaeude"], {}, besitz, 1, acht, blick[i])
            if w == tuple(kachel):
                return r, i
    return None


def main(wand_typen=None):
    """wand_typen: nur diese Einheitentypen brechen durch die Mauer, alle anderen greifen gleich den Lord an (Fix nach Ausloeser).
    Gibt (Ausloeser ja/nein, Typen, die gehauen haben) zurueck."""
    # (Daniel 21.10. 23:38 "jedes Mal 2-3 Minuten, bis die Streitkolben da sind"): Stoppuhr je Aufbau-Schritt;
    # "aufbau" als Argument haelt nach dem Aufstellen an (Messung des Aufbaus ohne den Angriff)
    uhr = [("start", time.time())]
    # "armee" (Daniel 21.10. 23:55): Grundstand mit beiden Heeren - unsere Soldaten brechen durch, Franz behaelt seine Einheiten
    armee = "armee" in sys.argv[1:]
    # (22.10. 00:00: Kippen beim Laden weiter ungeklaert - Fix A und B widerlegt; NOTLOESUNG, ausdruecklich: ein zweiter Ladeversuch)
    print("OK:", shc.laden(shc.STANDARD_STAND, versuche=2) if armee else shc.sandkasten(nur_soldaten="ja"), flush=True)
    uhr.append(("geladen", time.time()))
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
    # Weg je Feld (21.10. 23:35: der Plan sah jedes Mal nur 1 Mauerkachel, in Wahrheit lagen 4 hintereinander - nachsehen, was
    # der Planer an den Feldern hinter der ersten Kachel liest)
    e_ = ebenen()
    for q in pl["weg"][max(0, pl["weg"].index(zugang) - 1):pl["weg"].index(zugang) + 8]:
        print("  WEG %s logik %s hoehe-boden %d gebiet %d link 0x%02X%s" % (
            q, hex(int(e_["logik"][q])), int(e_["hoehe"][q]) - int(e_["boden"][q]), int(e_["gebiet"][q]), int(e_["link"][q]),
            " MAUER(Plan)" if q in wand else ""), flush=True)
    if armee:
        roh = speicher.lies(E0, 3000 * ES)
        nrs = [n for n in range(1, 3000) if einheit(roh, n)["leben"] > 0 and einheit(roh, n)["typ"] in shc.SOLDATEN
               and int.from_bytes(roh[n * ES + 0x96:n * ES + 0x98], "little") == 1 and int.from_bytes(roh[n * ES + 0x8C:n * ES + 0x8E], "little") != 0]
        print("ARMEE: %d eigene Soldaten" % len(nrs), flush=True)
        if wand_typen:
            andere = [n for n in nrs if einheit(roh, n)["typ"] not in wand_typen]
            nrs = [n for n in nrs if einheit(roh, n)["typ"] in wand_typen]
            print("FIX: Mauer nur Typen %s (%d Mann), %d andere direkt auf den Lord" % (sorted(wand_typen), len(nrs), len(andere)),
                  flush=True)
            if andere:
                befehl({"angriff": {"einheiten": sorted(andere), "ziel": lnr, "trupp": 1}}, 1.0)
    else:
        t = shc.setze(spieler=1, typ=26, x=zugang[0] - 1, y=zugang[1] - 1, anzahl=ZAHL)
        nrs = [int(x) for x in re.search(r"Nummern \[([0-9, ]+)\]", t).group(1).split(",")]
    uhr.append(("aufgestellt", time.time()))
    print("AUFBAU-ZEITEN: " + ", ".join("%s +%.1f s" % (n_, b_ - a_) for (_, a_), (n_, b_) in zip(uhr, uhr[1:])) +
          " | gesamt %.1f s" % (uhr[-1][1] - uhr[0][1]), flush=True)
    if "aufbau" in sys.argv[1:]:
        return
    lies = speicher.lies
    xs_, ys_, ks_ = speicher.felder()
    kxy = {int(kk): (int(xx), int(yy)) for xx, yy, kk in zip(xs_, ys_, ks_)}
    kvon = {v: k for k, v in kxy.items()}
    tick0 = int.from_bytes(lies(shc.TICK, 4), "little")
    phase, kachel, ereignisse, spur = "mauer", None, [], []
    # Sofort-Ausloeser (Daniel 21.10. 23:58 "es braucht einen instant trigger, warum es nicht klappt"): je Kachel die Frist aus dem
    # Code - Weg in Takten (Plan, 12 Takte je Feld gemessen) + 2 Trefferrunden (takte_je_treffer). Kein Hoehenverlust bis dahin =
    # Abbruch mit Grund (wer haut, wer steht, wer fiel - je Typ)
    frist, hk_alt, typen0, hauen_typen = None, None, {}, set()
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
        leute = {n: e for n, e in leute.items() if e["leben"] > 0 and e["typ"] in shc.SOLDATEN}
        lord = einheit(raw, lnr)
        if lord["leben"] <= 0 or lord["typ"] != 55:
            ereignisse.append((t_, "LORD TOT"))
            break
        if not leute:
            ereignisse.append((t_, "ALLE TOT"))
            break
        gold2 = int.from_bytes(lies(0x0115BDF8 + 2 * 0x39F4 + 0x4D0 + 15 * 4, 4), "little", signed=True)
        if gold2 > 0:                         # (Daniel 23:20 "der Gegner bildet Einheiten aus") - ohne Gold keine Anwerbung
            befehl({"player": 2, "gold": 0}, 0.3)
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
                # B-167 (Daniel 23:23): Ziel DIREKT setzen - alle auf das gerade Zugangsfeld des Wegs, targetedBuildingTile +
                # attackAtTileX/Y geschrieben (logik.lua mauerziel); beim Ankommen beginnt laut Code der Angriff auf genau diese Kachel
                # (Test C 23:38: nur Laufbefehl + geschriebenes Ziel -> alle 20 mit richtigem Ziel, aber keiner haut (Zustand 2):
                # erst der Mauer-Angriffsbefehl des Spiels versetzt sie in den Mauerangriff. Darum: Angriffsbefehl wie im Lauf mit
                # 5.090 Takten (je Mann einzeln, Anfrage + Blick so, dass das Spiel genau diese Kachel waehlt) UND logik.lua haelt
                # die Zielkachel in jedem Takt fest - kein Ausweichen auf andere Ziele)
                # Weg bis zur Kachel: Felder davor x 12 Takte (gemessen, augen_laufen) - nicht die Gesamtzeit des Plans
                zug_ = pl["weg"][pl["weg"].index(kachel) - 1]
                weit = max(max(abs(e["x"] - zug_[0]), abs(e["y"] - zug_[1])) for e in leute.values())
                frist = t_ + max(pl["weg"].index(kachel), weit) * mechanik.TAKTE_JE_FELD + 2 * mk["takte_je_treffer"]
                hk_alt = None
                ab = anfrage_und_blick(kachel)
                ereignisse.append((t_, "ANFRAGE %s fuer Kachel %s" % (ab, kachel)))
                anf, blick_k = ab if ab else (kachel, 0)
                befehl({"mauerziel": {"einheiten": sorted(leute), "feld": kvon[kachel], "x": kachel[0], "y": kachel[1],
                                      "halten": True}}, 0.5)
                befehl({"angriff": {"einheiten": sorted(leute), "mauer": [lp[0], lp[1], 2, 30, anf[0], anf[1], blick_k],
                                    "trupp": 1}}, 1.0)
                gesendet = {n: (leute[n]["zustand"], leute[n]["ziel"]) for n in leute}
        # Neu senden nur, wenn das Spiel den letzten Befehl dieses Manns sichtbar verarbeitet hat (Zustand oder Ziel anders als
        # beim Senden) und es trotzdem nicht passt - kein fester Takt
        verarbeitet = lambda n: gesendet.get(n) is None or gesendet[n] != (leute[n]["zustand"], leute[n]["ziel"])
        # (Phase mauer: das Ziel haelt logik.lua mauerzielTick in jedem Takt fest - hier kein zweiter Weg zum selben Ziel)
        if phase == "lord":
            ohne = [n for n, e in leute.items() if e["zustand"] in (0, 1) and verarbeitet(n)]
            if ohne:
                befehl({"angriff": {"einheiten": sorted(ohne), "ziel": lnr, "trupp": 1}}, 1.0)
                for n in ohne:
                    gesendet[n] = (leute[n]["zustand"], leute[n]["ziel"])
        hk = lies(speicher.HOEHE + kvon[kachel], 1)[0] if kachel is not None else -1
        if not typen0:
            for e in leute.values():
                typen0[e["typ"]] = typen0.get(e["typ"], 0) + 1
        if phase == "mauer" and kachel is not None:
            if hk_alt is not None and hk < hk_alt:
                frist = t_ + 2 * mk["takte_je_treffer"]          # Schaden kam: naechste Frist = 2 Trefferrunden
            hk_alt = hk
            if frist is not None and t_ > frist:
                hauen, stehen, jetzt = {}, {}, {}
                for e in leute.values():
                    (hauen if e["lage"] == 107 else stehen)[e["typ"]] = (hauen if e["lage"] == 107 else stehen).get(e["typ"], 0) + 1
                    jetzt[e["typ"]] = jetzt.get(e["typ"], 0) + 1
                gefallen = {t: n - jetzt.get(t, 0) for t, n in typen0.items() if n - jetzt.get(t, 0) > 0}
                hauen_typen = set(hauen)
                ereignisse.append((t_, "AUSLOESER: kein Schaden an Kachel %s bis Takt %d (Frist aus Weg + 2x%d) | haut je Typ %s | "
                                   "steht je Typ %s | gefallen je Typ %s" % (kachel, frist, mk["takte_je_treffer"], hauen, stehen,
                                                                             gefallen)))
                break
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
    return any("AUSLOESER" in e[1] for e in ereignisse), hauen_typen


if __name__ == "__main__":
    # nach einem Ausloeser sofort neu laden und noch einmal (hoechstens 2 Laeufe) - ohne Neustart der Instanz
    # (Daniel 23:59 "mit Fixes, nicht den gleichen Run"): der zweite Lauf nimmt die Typen, die im ersten gehauen haben, fuer die
    # Mauer - alle anderen gleich auf den Lord. Hat keiner gehauen, gibt es keinen Fix aus der Messung -> Abbruch mit Grund
    ausgeloest, hauen = main()
    if ausgeloest and hauen:
        print("NEUSTART DES TESTS mit Fix: Mauer nur Typen %s" % sorted(hauen), flush=True)
        main(wand_typen=hauen)
    elif ausgeloest:
        # keiner hat gehauen: Mauer nur fuer Streitkolben (Typ 26 - Mauerangriff belegt in UpdateMaceman 0x00560700, Fall
        # US_MELEE_ATTACK_WALL), alle anderen gleich auf den Lord
        print("NEUSTART DES TESTS mit Fix: keiner hat gehauen -> Mauer nur Streitkolben (Typ 26, Code UpdateMaceman)", flush=True)
        main(wand_typen={26})
