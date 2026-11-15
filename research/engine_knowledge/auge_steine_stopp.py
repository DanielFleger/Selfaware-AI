# -*- coding: utf-8 -*-
"""B-252 Luft-Stopp der Steine: an jeder Stoppstelle die Bodenhoehe so nachrechnen, wie das Spiel sie rechnet
(returnSomeHeight 0x004FF990 + Zuschlag in processEntityHitBuildingOrUnit), mit Logik-Ebene je Takt aus dem Fenster
(auge_steine.py aufnahme_mit_logik), Hoehen-Ebene je Takt aus dem Protokoll, Gebaeude-Ebene live.
Aufruf: python werkzeug/engine_knowledge/auge_steine_stopp.py daten/auge_protokoll_<stempel>.npz
"""
import struct
import sys
import os

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HIER))
import auge  # noqa: E402
import speicher  # noqa: E402

BUILDING_HEIGHTS = 0x005BB910
ORGANISM = auge.TILEMAP + 1947024


def bauhoehe(bid, btyp):
    """getBuildingHeightForBuildingID: feste Hoehen fuer Bergfriede/Torhaeuser/Tuerme, sonst 0."""
    return {11: 0x40, 12: 0x5c, 13: 0xbe, 40: 0x80, 41: 0x80, 74: 0x128, 75: 0x94, 76: 0xb4, 77: 0xc0, 78: 0xc0}.get(btyp, 0) if bid else 0


def return_some_height(logik, hoehe, bid, btyp, organism, heights_tab):
    if logik & 0x10000000:
        return hoehe + bauhoehe(bid, btyp), "Bit 0x10000000 -> Hoehe + Bauhoehe(%d)" % bauhoehe(bid, btyp)
    if (logik & 0x400) == 0:
        if (logik & 0x80) and (logik & 0x100) == 0 and organism > 1999:
            return hoehe + 0x32, "Baum (+50/+70)"
        return hoehe, "nur Hoehe"
    if btyp in (40, 41, 42, 43, 44):
        return hoehe + bauhoehe(bid, btyp), "Bit 0x400, Torhaus-Gruppe"
    if btyp in (45, 46, 61, 74, 75, 76, 77, 78):
        return hoehe + bauhoehe(bid, btyp) + 10, "Bit 0x400, Turm-Gruppe +10"
    if btyp == 7:
        return hoehe, "Bit 0x400 Typ 7"
    return hoehe + heights_tab[btyp], "Bit 0x400 -> Hoehe + BuildingHeights[%d]=%d" % (btyp, heights_tab[btyp])


def main(pfad):
    L = auge.Protokoll.laden(pfad)
    lg = np.load(pfad.replace(".npz", "_logik.npz"))
    takte, fenster, x0, y0, n = lg["takte"], lg["fenster"], int(lg["x0"]), int(lg["y0"]), int(lg["groesse"])
    fn = auge.feldnummern()
    heights_tab = struct.unpack("<100i", speicher.lies(BUILDING_HEIGHTS, 400))
    bau = np.frombuffer(speicher.lies(speicher.GEBAEUDE_EBENE, 80400 * 2), dtype="<u2")
    org = np.frombuffer(speicher.lies(ORGANISM, 80400 * 2), dtype="<u2")
    steine = {}
    for s in L:
        e = s.entities
        for i in np.flatnonzero(e["entityType"] == 2):
            steine.setdefault(int(e[i]["uid"]), []).append((s.takt, e[i].copy(), s.hoehe))
    print("Steine", len(steine), "| Logik-Fenster", fenster.shape, "ab", (x0, y0))
    for uid, r in steine.items():
        flug = [x for x in r if int(x[1]["logicalState"]) == 2]
        stopp = next((x for x in r if int(x[1]["logicalState"]) != 2), None)
        if not flug:
            continue
        t_l, g_l, h_l = flug[-1]
        t_s, g_s, h_s = stopp if stopp else (None, None, None)
        g = g_s if g_s is not None else g_l
        fx, fy, h = int(g["xPosition"]), int(g["yPosition"]), int(g["height"])
        print("== Stein %d: letzter Flug Takt %d (trav %d, h %d), Stopp Takt %s bei Feld (%d,%d) h %d, someCounter %d" % (
            uid, t_l, int(g_l["travelledDistance"]), int(g_l["height"]), t_s, fx, fy, h, int(g["someCounter_OR_hitGround"])))
        for (tx, ty) in ((fx, fy), (int(g_l["xPosition"]), int(g_l["yPosition"]))):
            k = int(fn[tx, ty])
            for tt in (t_l, t_s):
                if tt is None:
                    continue
                j = int(np.searchsorted(takte, tt))
                j = min(j, len(takte) - 1)
                lo = int(fenster[j][tx - x0, ty - y0]) if (0 <= tx - x0 < n and 0 <= ty - y0 < n) else -1
                hh = int((h_s if tt == t_s and h_s is not None else h_l)[k])
                bid = int(bau[k])
                btyp = int(L[-1].gebaeude[np.flatnonzero(L[-1]._gebaeude_idx == bid)]["buildingType"][0]) if bid and (L[-1]._gebaeude_idx == bid).any() else 0
                boden, warum = return_some_height(lo, hh, bid, btyp, int(org[k]), heights_tab)
                print("   Feld (%d,%d) Takt %d: Logik 0x%08X  Hoehe %d  Gebaeude %d (Typ %d)  Organism %d  -> Boden %d (%s)%s" % (
                    tx, ty, tt, lo & 0xFFFFFFFF, hh, bid, btyp, int(org[k]), boden, warum, "  <-- Boden > Stein" if boden > h else ""))


if __name__ == "__main__":
    main(sys.argv[1])
