# -*- coding: utf-8 -*-
"""Das Spiel steht bei Takt 9593 nach rufen2_g: Was sagen Pech und Graeben jetzt?"""
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments.spielcode_rufen import Rufer
from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz

K = Feldkarte.laden(feldliste=FELDLISTE)
s = K.struktur("DAT_GameState")
print([n for o, tt, gr, n in K.typen[s[3]]["felder"]][:8])
with Rufer(pid_der_instanz(2)) as r:
    a, gr, sch, _ = K.adresse("DAT_GameState", "playerDataArray[].currentResources[]")
    print("Pech 7, Teilpech 8:", r.lies_i(a + sch + 7 * 4), r.lies_i(a + sch + 8 * 4))
    a0, _, sch_m, _ = K.adresse("DAT_TileMapState", "moats[]")
    print("Graeben (Nr, Besitzer, Fuellung, Stufe, Zaehler):", [(i, r.lies(a0 + i * sch_m + 12, 1)[0], r.lies(a0 + i * sch_m + 13, 1)[0], r.lies(a0 + i * sch_m + 14, 1)[0], r.lies(a0 + i * sch_m + 15, 1)[0]) for i in range(1, 5)])
    b = K.adresse("DAT_BuildingsState", "buildings[].resourcePitch")
    tp = K.adresse("DAT_BuildingsState", "buildings[].buildingType")
    for i in range(1, 40):
        t = r.lies_i(tp[0] + i * tp[2], tp[1])
        if t in (6, 10):
            print("Gebaeude", i, "Art", t, "Pech", r.lies_i(b[0] + i * b[2]), "Teilpech", r.lies_i(K.adresse("DAT_BuildingsState", "buildings[].resourcePartialPitch")[0] + i * b[2]))
    for f in ("finalResults.finalPitchProduced[]",):
        try:
            print(f, K.adresse("DAT_GameState", f))
        except KeyError as e:
            print("Feld fehlt", e)
    gs = K.struktur("DAT_GameState")
    for o, tt, gr, n in K.typen[gs[3]]["felder"]:
        if "final" in n.lower():
            print("GameState", n, tt, gr)
    for g in ("DAT_GameCore", "DAT_GameSynchronyState"):
        st = K.struktur(g)
        for o, tt, gr, n in K.typen[st[3]]["felder"]:
            if "final" in n.lower():
                print(g, n, tt, gr)
