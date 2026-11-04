# -*- coding: utf-8 -*-
import json, struct
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments.spielcode_rufen import Rufer
from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz
K = Feldkarte.laden(feldliste=FELDLISTE)
s = K.struktur("DAT_EntityDefinedData")
namen = {n: (o, tt, gr) for o, tt, gr, n in K.typen[s[3]]["felder"]}
print("Struktur", s[:3], len(namen))
for n, v in namen.items():
    if any(x in n for x in ("Curve", "Velocity", "XYOffsets", "field43", "field6_")):
        print(n, v)
print({g: K.struktur(g)[:3] for g in ("SEC_RNG",) if True})
pid = pid_der_instanz(2)
print("pid", pid)
with Rufer(pid) as r:
    print("Takt", r.lies_i(0x0117CADC))
    # Flugarten, Tempo und Bremse je Art
    a0 = s[0] if isinstance(s[0], int) else None
    print("Basis", a0)
    def tab(n, zahl, fmt="<i"):
        o, tt, gr = namen[n]
        b = r.lies(a0 + o, zahl * struct.calcsize(fmt))
        return [struct.unpack_from(fmt, b, i * struct.calcsize(fmt))[0] for i in range(zahl)]
    kurve = tab("DAT_EntityArrayCurveTypeForProjectileType", 96)
    tempo = tab("DAT_EntityArrayProjectileVelocityForProjectileType", 96)
    bremse = tab("field43_0x5c4", 96, "<f")
    print("Art: Kurve Tempo Bremse")
    for i in range(96):
        if kurve[i] or tempo[i]:
            print(i, kurve[i], tempo[i], round(bremse[i], 4))
    o = namen["DAT_XYOffsetsInAllDirections"]
    print("Versatz-Tabelle", o)
    b = r.lies(a0 + o[0], 64 * 8)
    print([struct.unpack_from("<ii", b, i * 8) for i in range(64)])
    print("Patch Feuer", r.lies(0x532495, 64).hex())
    print("Feuer-Tabelle", [r.lies_i(0x0270b9e0 + i * 4) for i in range(90)])
