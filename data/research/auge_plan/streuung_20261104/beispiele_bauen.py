# -*- coding: utf-8 -*-
"""Sichert aus den Aufzeichnungen ein paar ganze Fluege und Feuer als Festwerte fuer tests/test_streuung.py (die .auge-Dateien bleiben lokal)."""
import glob
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import feuer_pruefen as fe  # noqa: E402
import flug_pruefen as fp  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

k = Feldkarte.laden(feldliste=FELDLISTE)
pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_streuung.auge")))[-1]
lauf = fp.Lauf(pfad, k)
aus = {"quelle": os.path.basename(pfad), "fluege": [], "feuer": []}
je_art = {}
for s, f in sorted(lauf.fluege.items(), key=lambda x: x[1][0][0]):
    z = f[0][1]
    if je_art.get(z["art"], 0) >= 6:
        continue
    reihe = []
    for t, x in f[1:]:
        if x["da"] != 2 or x["boden"] != 0 or x["v"] != z["v"]:
            break
        if t - f[0][0] != len(reihe) + 1:
            reihe = None  # Takt fehlt: nimmt der Test nicht
            break
        reihe.append([x["mx"], x["my"], x["h"], x["wg"]])
    if reihe and len(reihe) >= 5:
        je_art[z["art"]] = je_art.get(z["art"], 0) + 1
        aus["fluege"].append({"art": z["art"], "mx": z["mx"], "my": z["my"], "h0": z["h0"], "zx": z["zx"], "zy": z["zy"], "zz": z["zz"], "v": z["v"], "w": z["w"], "vc": z["vc"], "vs": z["vs"], "b": z["bremse"], "gesamt": z["gesamt"], "reihe": reihe})
feuer = fe.feuer_lesen(pfad, k)
geb = {}
for s, f in feuer.items():
    geb.setdefault(f[0][0], []).append(f[0][1])
for s, f in lauf.fluege.items():
    z = f[0][1]
    if z["art"] != 34:
        continue
    ende = next(((t, x) for t, x in f[1:] if x["da"] != 2 or x["boden"] != 0), None)
    if ende is None:
        continue
    for ff in geb.get(ende[0], ()):
        d = (ff["mx"] - ende[1]["mx"], ff["my"] - ende[1]["my"])
        if d in fe.VERSATZ and ff["stufe"] == 2 and ff["stark"] == 1:
            aus["feuer"].append({"land": [ende[1]["mx"], ende[1]["my"]], "feuer": [ff["mx"], ff["my"]]})
            break
# Fluege mit Abprall: Punkt des Abpralls und die Takte danach
aus["abprall"] = []
zeilen, hoehen = fp.zeilen_lesen(), fp.bauhoehen()
for muster in ("lauf_s_*_streuung.auge", "lauf_s_*_streuung2.auge"):
    pf = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", muster)))[-1]
    la = fp.Lauf(pf, k)
    gezaehlt = {}
    for s, f in sorted(la.fluege.items(), key=lambda x: x[1][0][0]):
        z = f[0][1]
        log = []
        fp.vorhersage(z, f, la, zeilen, hoehen, abpr_log=log)
        if not log or gezaehlt.get((z["ori"], z["art"]), 0) >= 3:
            continue
        e = log[0]
        ab = [x for t, x in f[1:] if t >= e["takt"] and x["da"] == 2 and x["boden"] == 0]
        if len(ab) < 8 or ab[0]["v"] == z["v"] or not all(t - e["takt"] == i for i, (t, x) in enumerate((t, x) for t, x in f[1:] if t >= e["takt"] and x["da"] == 2 and x["boden"] == 0)):
            continue
        gezaehlt[(z["ori"], z["art"])] = gezaehlt.get((z["ori"], z["art"]), 0) + 1
        e.update(v=ab[0]["v"], w=ab[0]["w"], reihe=[[x["mx"], x["my"], x["h"], x["wg"]] for x in ab[1:13]])
        aus["abprall"].append(e)
print("Abprall-Beispiele", len(aus["abprall"]), sorted({e["ori"] for e in aus["abprall"]}))
# Die festen Tabellen, direkt aus dem Speicher von Instanz 2
import struct  # noqa: E402

from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz  # noqa: E402
from selfaware.tools.experiments.spielcode_rufen import Rufer  # noqa: E402

s = k.struktur("DAT_EntityDefinedData")
felder = {n: o for o, tt, gr, n in k.typen[s[3]]["felder"]}
pid = pid_der_instanz(2)
if pid:
    with Rufer(pid) as r:
        b = r.lies(s[0] + felder["DAT_XYOffsetsInAllDirections"], 64 * 8)
        aus["versatz"] = [list(struct.unpack_from("<ii", b, i * 8)) for i in range(64)]
        kurve = struct.unpack("<45i", r.lies(s[0] + felder["DAT_EntityArrayCurveTypeForProjectileType"], 45 * 4))
        wert = struct.unpack("<45i", r.lies(s[0] + felder["DAT_EntityArrayProjectileVelocityForProjectileType"], 45 * 4))
        bremse = struct.unpack("<45f", r.lies(s[0] + felder["field43_0x5c4"], 45 * 4))
        aus["geschoss_tabelle"] = {str(i): [kurve[i], wert[i], round(bremse[i], 4)] for i in range(45) if kurve[i] or wert[i]}
else:  # Spiel laeuft nicht: Die Tabellen sind fest, sie bleiben aus dem letzten Stand
    alt = json.load(open(os.path.join(HIER, "flug_beispiele.json"), encoding="utf-8"))
    aus["versatz"], aus["geschoss_tabelle"] = alt["versatz"], alt["geschoss_tabelle"]
with open(os.path.join(HIER, "flug_beispiele.json"), "w", encoding="utf-8") as f:
    json.dump(aus, f)
print("Fluege", len(aus["fluege"]), je_art, "Feuer", len(aus["feuer"]))
