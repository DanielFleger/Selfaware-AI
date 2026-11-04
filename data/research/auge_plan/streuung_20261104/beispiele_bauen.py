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
# Die festen Tabellen, direkt aus dem Speicher von Instanz 2
import struct  # noqa: E402

from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz  # noqa: E402
from selfaware.tools.experiments.spielcode_rufen import Rufer  # noqa: E402

s = k.struktur("DAT_EntityDefinedData")
felder = {n: o for o, tt, gr, n in k.typen[s[3]]["felder"]}
with Rufer(pid_der_instanz(2)) as r:
    b = r.lies(s[0] + felder["DAT_XYOffsetsInAllDirections"], 64 * 8)
    aus["versatz"] = [list(struct.unpack_from("<ii", b, i * 8)) for i in range(64)]
    kurve = struct.unpack("<45i", r.lies(s[0] + felder["DAT_EntityArrayCurveTypeForProjectileType"], 45 * 4))
    wert = struct.unpack("<45i", r.lies(s[0] + felder["DAT_EntityArrayProjectileVelocityForProjectileType"], 45 * 4))
    bremse = struct.unpack("<45f", r.lies(s[0] + felder["field43_0x5c4"], 45 * 4))
    aus["geschoss_tabelle"] = {str(i): [kurve[i], wert[i], round(bremse[i], 4)] for i in range(45) if kurve[i] or wert[i]}
with open(os.path.join(HIER, "flug_beispiele.json"), "w", encoding="utf-8") as f:
    json.dump(aus, f)
print("Fluege", len(aus["fluege"]), je_art, "Feuer", len(aus["feuer"]))
