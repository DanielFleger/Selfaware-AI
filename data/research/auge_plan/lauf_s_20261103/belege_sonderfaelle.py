# -*- coding: utf-8 -*-
"""Belege fuer die Zahlen der Sonderfaelle in Ergebnis_Lauf_S.md, die nicht schon in den .regeln.json stehen: Graben-Zeiten, Pech-Zustand, Steiger-Hoehe, Schussweite auf der Mauer, Kochoel, Tunnel. Liest die Aufzeichnungen (bleiben lokal in laeufe/).

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/belege_sonderfaelle.py > data/research/auge_plan/lauf_s_20261103/belege_sonderfaelle.txt
"""
import collections
import glob
import json
import os
import struct

import numpy as np

from selfaware.tools.analysis import auge_regeln as ar
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

L = "data/research/auge_plan/laeufe/"
karte = Feldkarte.laden(feldliste=FELDLISTE)


def neueste(szene):
    return sorted(glob.glob(L + f"*_{szene}.auge"), key=os.path.getmtime)[-1]


def plan_von(pfad):
    return json.load(open(pfad + ".plan.json", encoding="utf-8"))


def feld_verlauf(pfad, feld, nummern):
    """Wert von units[].<feld> je Einheit, nur die Wechsel: (Takt ab Beginn, Wert)."""
    auf = Aufzeichnung(pfad)
    iu = auf.namen.index("DAT_UnitsState")
    bu = auf.bereiche[iu][1]
    a = karte.adresse("DAT_UnitsState", "units[]." + feld)
    typ = {1: "<B", 2: "<h", 4: "<i"}[a[1]]
    aus = {n: [] for n in nummern}
    start = None
    for r, p, _ in auf.staende():
        if r.bereich != iu or not r.rein:
            continue
        start = r.takt if start is None else start
        b = bytes(p)
        for n in nummern:
            w = struct.unpack_from(typ, b, a[0] - bu + n * a[2])[0]
            if not aus[n] or aus[n][-1][1] != w:
                aus[n].append((r.takt - start, w))
    return aus, start


def alle(szene, n=3):
    return sorted(glob.glob(L + f"*_{szene}.auge"), key=os.path.getmtime)[-n:]


def graben():
    """21:41: eigene Sklaven schuetten bei Takt 2000 zu. 23:06: Spieler 2 ab 1500, die Graeber stehen noch da. 23:16: Spieler 2 ab 1500, die Graeber gehen bei 1000 weg."""
    for p in alle("sonder3_g"):
        plan = plan_von(p)
        k = next(z for z in plan["karte"] if z["posten"] == "graben")
        v = ar.logik_verlauf(p, karte, [z[2] for z in k["felder"]])
        start = plan["von"]
        print("== Graben", os.path.basename(p), "Felder", len(k["felder"]), "Beginn", start, "Ende", plan["bis"] - start)
        fertig, zu = [], []
        for z, verlauf in v.items():
            t = next((t - start for t, w in verlauf if w & 0x40000000), None)
            fertig.append(t)
            if t is not None:
                zu.append(next((a - start for a, w in verlauf if a - start > t and not w & 0x40000000), None))
        print("  ausgehoben bei", sorted(x for x in fertig if x is not None), "nicht ausgehoben", sum(x is None for x in fertig))
        print("  zugeschuettet bei", sorted(x for x in zu if x is not None), "nicht zugeschuettet", sum(x is None for x in zu))
        print("  Graben-Felder im Plan am Ende:", plan.get("graben_felder_am_ende"))
        for e in plan["einheiten"]:
            if e.get("posten") == "graben" and e["rolle"] == "fueller" and "nr" in e:
                reihen, _ = ar.reihen_lesen(p, karte)
                print("  Zuschuetter", e["nr"], "Leben Anfang, Ende:", int(reihen[0][1]["leben"][e["nr"]]), int(reihen[-1][1]["leben"][e["nr"]]) if reihen[-1][1]["da"][e["nr"]] and reihen[-1][1]["typ"][e["nr"]] == 71 else "weg")


def hunde():
    """21:41: Befehl 74, 3 Opfer, die Starttruppen schiessen. 23:06: Befehl 74, 3 Opfer, geraeumt. 23:16: kein Befehl, 8 Opfer, geraeumt."""
    for p in alle("sonder3_g"):
        plan = plan_von(p)
        reihen, _ = ar.reihen_lesen(p, karte)
        start = reihen[0][0]
        g = ar.geschosse_lesen(p, karte)
        k = next(z for z in plan["gebaeude"] if z["typ"] == 99)
        print("== Hunde", os.path.basename(p), "Kaefig bei", (k["x"], k["y"]))
        opfer = [e for e in plan["einheiten"] if e.get("posten") == "hunde" and e["rolle"] == "opfer"]
        for e in opfer:
            v, null = [], None
            for t, s in reihen:
                le = int(s["leben"][e["nr"]]) if s["da"][e["nr"]] and s["typ"][e["nr"]] == 24 else 0
                if not v or v[-1][1] != le:
                    v.append((t - start, le))
                if le == 0 and null is None:
                    null = t - start
            pf = [x for x in g if x["ziel"] == e["nr"] and x["art"] == "pfeil"]
            print("   Opfer", e["nr"], "erster Verlust", v[1][0] if len(v) > 1 else None, "Leben 0 bei", null, "Pfeile darauf", len(pf), "Schritte", v[1:4])
        h = {}
        for t, s in reihen:
            for i in np.nonzero((s["da"] != 0) & (s["typ"] == 67))[0]:
                i = int(i)
                if i == 0:  # Platz 0 ist die Kopie der gerade laufenden Einheit
                    continue
                z = h.setdefault(i, {"von": t - start, "ort": (int(s["mx"][i]) // 8, int(s["my"][i]) // 8), "zu": [], "ziele": collections.Counter(), "erster": None, "leben": None})
                z["bis"], z["ende"], z["leben"] = t - start, (int(s["mx"][i]) // 8, int(s["my"][i]) // 8), int(s["leben"][i])
                w = int(s["zustand"][i])
                if len(z["zu"]) < 5 and (not z["zu"] or z["zu"][-1][1] != w):
                    z["zu"].append((t - start, w))
                if s["schlaegt"][i]:
                    z["ziele"][int(s["schlaegt"][i])] += 1
                    z["erster"] = z["erster"] if z["erster"] is not None else t - start
        print("   Hunde:", len(h))
        for i, z in sorted(h.items()):
            print("    Nr", i, "von", z["von"], "bis", z["bis"], "Ort", z["ort"], "Ende", z["ende"], "Leben am Ende", z["leben"], "Ziele", len(z["ziele"]), "erster Biss", z["erster"], "Zustaende", z["zu"])
        r = json.load(open(p + ".regeln.json", encoding="utf-8"))["zeilen"]
        print("   Kaefig:", [(x["leben"], x["weg"]) for z in r if z["posten"] == "hunde" for x in z["gebaeude"]], "fremd:", [z.get("fremd") for z in r if z["posten"] == "hunde"])


def pech():
    for szene in ("sonder4_g", "sonder5_g"):
        p = neueste(szene)
        plan = plan_von(p)
        auf = Aufzeichnung(p)
        ib = auf.namen.index("DAT_TileMapState")
        b0 = auf.bereiche[ib][1]
        a = {n: karte.adresse("DAT_TileMapState", "pitchDitches[]." + n) for n in ("uid", "x", "y", "owner", "state")}
        k = next(z for z in plan["karte"] if z["posten"] == "pech")
        verlauf = collections.defaultdict(list)
        for r, roh, _ in auf.staende():
            if r.bereich != ib:
                continue
            b = bytes(roh)
            for i in range(1, a["uid"][3]):
                u = struct.unpack_from("<i", b, a["uid"][0] - b0 + i * a["uid"][2])[0]
                if not u:
                    if i in verlauf and verlauf[i][-1][1] is not None:
                        verlauf[i].append((r.takt - plan["von"], None))
                    continue
                x = struct.unpack_from("<h", b, a["x"][0] - b0 + i * a["x"][2])[0]
                y = struct.unpack_from("<h", b, a["y"][0] - b0 + i * a["y"][2])[0]
                if not (k["x"] - 2 <= x <= k["x"] + k["breite"] + 2 and k["y"] - 2 <= y <= k["y"] + k["hoehe"] + 2):
                    continue
                w = struct.unpack_from("<h", b, a["state"][0] - b0 + i * a["state"][2])[0]
                if not verlauf[i] or verlauf[i][-1][1] != w:
                    verlauf[i].append((r.takt - plan["von"], w))
        print("==", szene, os.path.basename(p), "Pechgraeben im Posten:", len(verlauf))
        for i, v in sorted(verlauf.items()):
            print("  Nr", i, "(Takt, Zustand; None = weg):", v[:8])


def steiger():
    p = neueste("sonder3")
    plan = plan_von(p)
    wer = [e for e in plan["einheiten"] if e.get("posten") == "leiter" and e["rolle"] == "steiger" and "nr" in e]
    v, _ = feld_verlauf(p, "terrainOrClimbHeight", [e["nr"] for e in wer])
    print("== Steiger", os.path.basename(p), "Laufbefehl bei Takt 500")
    for e in wer:
        s = v[e["nr"]]
        print("  Einheit", e["nr"], "Hoehe-Wechsel:", len(s), "Anfang", s[:2], "hoechste", max(w for _, w in s), "erstmals bei", next((t for t, w in s if w == max(w2 for _, w2 in s)), None))


def schussweite():
    p = neueste("sonder5")
    plan = plan_von(p)
    wer = [e for e in plan["einheiten"] if e["rolle"] == "laeufer" and "nr" in e]
    ziele = {e["paar"]: e for e in plan["einheiten"] if e["rolle"] == "ziel" and "nr" in e}
    v, _ = feld_verlauf(p, "terrainOrClimbHeight", [e["nr"] for e in wer])
    g = ar.geschosse_lesen(p, karte)
    reihen, _ = ar.reihen_lesen(p, karte)
    start = reihen[0][0]
    print("== Schussweite auf der Mauer", os.path.basename(p), "Schussbefehl bei Takt 1500")
    for e in wer:
        s = v[e["nr"]]
        hoehe = [w for t, w in s if t <= 1500][-1] if [w for t, w in s if t <= 1500] else None
        z = ziele[e["paar"]]
        pfeile = [x for x in g if x["schuetze"] == e["nr"] and x["art"] == "pfeil"]
        auf_ziel = [x for x in pfeile if x["ziel"] == z["nr"]]
        stand = dict(reihen)
        ort = None
        for t, r in reihen:
            if t - start >= 1500:
                ort = (int(r["mx"][e["nr"]]) // 8, int(r["my"][e["nr"]]) // 8)
                break
        print("  Soll-Abstand", e["abstand"], "Hoehe bei Takt 1500:", hoehe, "Ort", ort, "Ziel", (z["x"], z["y"]), "Abstand wirklich", abs(z["x"] - ort[0]) if ort else None, "Pfeile", len(pfeile), "davon aufs Ziel", len(auf_ziel), "Ziel-Leben", (int(reihen[0][1]["leben"][z["nr"]]), int(reihen[-1][1]["leben"][z["nr"]])))


def oel():
    p = neueste("sonder2_g")
    plan = plan_von(p)
    wer = [e for e in plan["einheiten"] if e.get("posten") == "oel" and "nr" in e]
    reihen, _ = ar.reihen_lesen(p, karte)
    start = reihen[0][0]
    g = ar.geschosse_lesen(p, karte)
    print("== Kochoel", os.path.basename(p), "Befehle: holen 0, werfen 800, hingehen 1800, werfen 2400")
    op = next(e for e in wer if e["rolle"] == "opfer")
    for e in wer:
        zeile = []
        for soll in (0, 800, 1800, 2400, 2469):
            t, r = next((t, r) for t, r in reihen if t - start >= soll)
            zeile.append((t - start, int(r["mx"][e["nr"]]) // 8, int(r["my"][e["nr"]]) // 8, int(r["leben"][e["nr"]])))
        print("  ", e["rolle"], e["nr"], "(Takt, x, y, Leben):", zeile)
    k = next(z for z in plan["karte"] if z["posten"] == "oel")
    im = [x for x in g if x["art"] in ("brand", "feuer", "feuer_frei") and k["x"] - 10 <= x["start"][0] // 8 < k["x"] + k["breite"] + 10 and k["y"] - 10 <= x["start"][1] // 8 < k["y"] + k["hoehe"] + 10]
    print("   Brand-Eintraege im Posten:", collections.Counter(x["art"] for x in im), "erster bei", min((x["von"] - start for x in im), default=None), "Opfer", (op["x"], op["y"]))


def hoehen(p, plan, zeile, x0, x1):
    """Hoehe der Felder einer Zeile am Anfang, in der Mitte und am Ende. Die Kartenebenen stehen nur in jedem 25. Rahmen."""
    basis = json.load(open(os.path.join(os.path.dirname(__file__), "feldnummern.json"), encoding="utf-8"))[zeile]
    auf = Aufzeichnung(p)
    ib = auf.namen.index("DAT_TileMapState")
    b0 = auf.bereiche[ib][1]
    adr = karte.adresse("DAT_TileMapState", "HeightLayer[]")[0]
    staende = []
    for r, roh, _ in auf.staende():
        if r.bereich == ib:
            b = bytes(roh)
            staende.append((r.takt - plan["von"], [b[adr - b0 + basis + x] for x in range(x0, x1 + 1)]))
    aus = [staende[0]]
    for s in staende[1:]:
        if s[1] != aus[-1][1]:
            aus.append(s)
    return aus


def tunnel(szene):
    try:
        p = neueste(szene)
    except IndexError:
        print("== Tunnel", szene, ": keine Aufzeichnung")
        return
    plan = plan_von(p)
    print("== Tunnel", szene, os.path.basename(p), "kein Platz", plan["kein_platz"], "nicht gesetzt", plan["nicht_gesetzt"], "Takte", plan["bis"] - plan["von"])
    print("   Karte:", [(k["posten"], k["x"], k["y"]) for k in plan["karte"]])
    wer = [e for e in plan["einheiten"] if e["typ"] == 5 and "nr" in e]
    nr = [e["nr"] for e in wer]
    graben, _ = feld_verlauf(p, "tunnelerFinishedDigging", nr)
    reihen, _ = ar.reihen_lesen(p, karte)
    start = reihen[0][0]
    for e in wer:
        zu, ort, weg, leben = [], [], None, None
        for t, r in reihen:
            if not r["da"][e["nr"]] or r["typ"][e["nr"]] != 5:
                weg = t - start
                break
            z = int(r["zustand"][e["nr"]])
            if not zu or zu[-1][1] != z:
                zu.append((t - start, z))
            o = (int(r["mx"][e["nr"]]) // 8, int(r["my"][e["nr"]]) // 8)
            if not ort or (t - start) - ort[-1][0] >= 100:
                ort.append((t - start, *o))
            leben = int(r["leben"][e["nr"]])
        print("  ", e["posten"], e["rolle"], "Nr", e["nr"], "weg", weg, "Leben", leben)
        print("     Zustaende (Takt, Wert):", zu[:14])
        print("     tunnelerFinishedDigging:", graben[e["nr"]][:10])
        print("     Ort alle 100 Takte:", ort[:24])
        unten = [o for o in ort if o[0] >= 1000]
        if len(unten) > 2:
            h = hoehen(p, plan, unten[0][2], unten[0][1], unten[-1][1])
            print("     Hoehe Zeile", unten[0][2], "x", unten[0][1], "bis", unten[-1][1], "Wechsel", len(h), "Anfang", h[0], "Ende", h[-1])
    # Alle Gebaeude im Verlauf: Eingaenge und Ziele
    auf = Aufzeichnung(p)
    ib = auf.namen.index("DAT_BuildingsState")
    bb = auf.bereiche[ib][1]
    ad = {k: karte.adresse("DAT_BuildingsState", "buildings[]." + f) for k, f in (("da", "logicalState"), ("typ", "buildingType"), ("x", "x"), ("y", "y"), ("leben", "currentHealth"))}
    verlauf = collections.defaultdict(list)
    for r, roh, _ in auf.staende():
        if r.bereich != ib or not r.rein:
            continue
        b = bytes(roh)
        sp = {k: np.ndarray(shape=(v[3],), dtype="<i2", buffer=b, offset=v[0] - bb, strides=(v[2],)) for k, v in ad.items()}
        for i in np.nonzero(np.isin(sp["typ"], [50, 85, 74]))[0]:
            w = (int(sp["typ"][i]), int(sp["da"][i]), int(sp["x"][i]), int(sp["y"][i]), int(sp["leben"][i]))
            if not verlauf[int(i)] or verlauf[int(i)][-1][1:] != w:
                verlauf[int(i)].append((r.takt - plan["von"], *w))
    print("   Gebaeude (Takt, Art, Zustand, x, y, Leben), nur Wechsel:")
    for i, v in sorted(verlauf.items()):
        print("    Nr", i, v[:3], "...", v[-3:] if len(v) > 3 else "", "Wechsel", len(v))
    # Mauer und Felder
    k = next((z for z in plan["karte"] if z["posten"] == "mauer"), None)
    if k and k["felder"]:
        v = ar.logik_verlauf(p, karte, [z[2] for z in k["felder"]])
        print("   Mauerfelder (Takt ab Beginn, Bits):", {f"{z[0]},{z[1]}": [(t - plan["von"], hex(w)) for t, w in v[z[2]][:4]] for z in k["felder"]})


if __name__ == "__main__":
    for f in (graben, hunde, pech, steiger, schussweite, oel, lambda: tunnel("sonder6_g"), lambda: tunnel("sonder7_g")):
        try:
            f()
        except Exception as e:
            print("== FEHLER", repr(e))
