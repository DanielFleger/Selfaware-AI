# -*- coding: utf-8 -*-
"""B-170 Durchbruch zum Lord fuer jeden Spieler - aus sturm.plane_ziel herausgeloest (22.10.2026; Daniel 08:39 Bild vor Franz'
Burg: "er geht immer noch gegen Tuerme und einsame Mauern, statt die aufzumachen, die zum Lord fuehren").

GEMESSEN 22.10. (2v2 liga2v2_20261022_082947, Feldzug gegen Lord 141 bei (175,116), Tick 40.643 bis ~64.100): die alte Wahl nahm
die SCHWAECHSTE Burgstelle im Umkreis (Turm 327 Typ 76, 2.000 Leben, 25 Felder vom Lord - auf keinem Weg zum Lord) und Mauerkacheln
am Lord, die keiner traf: (187,116) (184,114) (183,115) "keine Wirkung", (185,96) (177,120) "kommt nicht an". sturm.py brach dieselbe
Burg 5-mal: Weg mit dem wenigsten Beschuss durch die Mauer (mechanik.durchbruch_schritte), jedes Torhaus als Alternative, Zugangsfeld
genau vor der Kachel, dort das Mauerziel jeden Takt festhalten (logik.lua mauerziel halten) und mit Blickrichtung angreifen.

plane(sp, start, maenner, lord)  -> dict art "mauer"/"tor"/"lord", ziel (Kachel / Torhaus-Nr), zug (Zugangsfeld), weg, takte,
                                    belastung, kandidaten - das ERSTE Hindernis auf dem besten Weg zum Lord, sonst nichts
anfrage_und_blick(kachel, sp)    -> (Anfrage-Kachel, Blickrichtung), bei denen das Spiel genau diese Kachel waehlt
feld(xy)                         -> Feldnummer des Spiels (fuer logik.lua mauerziel)
"""
import math

import numpy as np

import mechanik
import speicher

# B-256 (Daniel 26.10. 23:14 "versucht immer wieder durch das Torhaus zu gehen, aber die Zugbruecke wird ignoriert"; Partie
# 230627 Sp2 gegen Lord 3, Lage Tick 62083: vor jedem Typ 46 liegt 5 Felder davor eine Typ 49 - 109/110, 145/157, 146/158, 149/160;
# bauen.NACH_TYP: 45 BT_GATEHOUSELARGE, 46 BT_GATEHOUSESMALL, 49 BT_DRAWBRIDGE, 75 BT_TOWER2): Torhaeuser sind 45 und 46 - bis
# heute stand hier nur 75 (ein Turm). 75 bleibt als Einschlag-Stelle (Messung 22:27: Durchgang neben dem Grundriss)
TORHAEUSER = {45, 46, 75}
# Die Zugbruecke ist fuer uns nie ein Weg und kein Abrissziel (20.10. gegen Franz: 6-mal Ziel, Leben blieb bei 100; Partie 230627:
# 4 Plaene ueber eine Bruecke, alle "BRESCHE ABGESCHNITTEN" - der Planer rechnete sie als Gebaeude mit 100 Leben zum Abreissen)
ZUGBRUECKE = 49


def ebenen():
    wk = speicher.wegkarte()
    return {"link": wk["link"], "bau": wk["gebaeude"], "gebiet": wk["gebiet"], "logik": speicher.ebene(speicher.LOGIK, 4),
            "besitz": speicher.ebene(speicher.BESITZ), "hoehe": speicher.ebene(speicher.HOEHE).astype(int),
            "boden": speicher.ebene(speicher.BODEN).astype(int)}


def feld(xy):
    xs, ys, ks = speicher.felder()
    if not hasattr(feld, "_k"):
        feld._k = {(int(x), int(y)): int(k) for x, y, k in zip(xs, ys, ks)}
    return feld._k.get((int(xy[0]), int(xy[1])))


def sperre_feindbau(bau, G, sp):
    """B-164: feindliche Burgteile sind fuer uns kein Weg; Torhaeuser mit 2 Feldern Rand (ihr Durchgang liegt neben dem Grundriss)."""
    from scipy import ndimage
    from feldzug import BURG_TEILE
    from parteien import freunde_von
    feind = [nr for nr, g_ in G.items() if g_.get("besitzer") not in freunde_von(sp) and g_["typ"] in BURG_TEILE | {ZUGBRUECKE}]
    tore = [nr for nr in feind if G[nr]["typ"] in TORHAEUSER]
    s = np.isin(bau, feind)
    if tore:
        s |= ndimage.binary_dilation(np.isin(bau, tore), structure=np.ones((3, 3), bool), iterations=2)
    return s


def schaden(L, sp, n):
    """Schaden je Takt je Feld aus allen feindlichen Fernkaempfern (L73-Baender, gefecht.FERN_REICH) - wie sturm.schaden_feld."""
    import gefahrenschutz as GS
    import gefecht
    from parteien import freunde_von
    return GS.Lage(L, {}, lambda b: b not in freunde_von(sp), gefecht.FERN_REICH, n=n, raten={}).s


def plane(sp, start, maenner, lord, mk=None, L=None, G=None, gf=None, verworfen=(), e=None):
    """Bester Durchbruch fuer Spieler sp von start zum Lord: Mauerweg oder ein Torhaus - Daniels Regel "maximale Sicherheit, dann
    minimaler Widerstand" (Beschuss-Last, dann Takte) auch zwischen den Kandidaten. verworfen: Mauerkacheln/Torhaeuser, die keine
    Wirkung hatten oder nicht erreichbar waren. Rueckgabe None ohne Weg."""
    from scipy import ndimage
    from parteien import freunde_von
    from waechter import lies_gebaeude, lies_lagebild
    mk = mk or mechanik.streitkolben()
    e = e or ebenen()
    G = lies_gebaeude() if G is None else G
    L = lies_lagebild(neu_holen=False) if L is None else L
    n = e["link"].shape[0]
    gf = schaden(L, sp, n) if gf is None else gf
    sperre = sperre_feindbau(e["bau"], G, sp)
    vsperre = np.zeros(sperre.shape, bool)          # B-268: nur die verworfenen Kacheln
    for q in verworfen:
        if isinstance(q, tuple):
            sperre[q[0], q[1]] = True
            vsperre[q[0], q[1]] = True
    freunde = set(freunde_von(sp)) - {0}
    args = (e["link"], e["logik"], e["bau"], e["besitz"], e["hoehe"], e["boden"], sp, maenner, tuple(start), tuple(lord), mk)
    kand = []
    r = mechanik.durchbruch_schritte(*args, sperre=sperre, gefahr=gf, freunde=freunde)
    if r["weg"]:
        kand.append(("mauer", None, r, None))
    # Gewoehnliche Gebaeude koennen einen Zugang genauso versperren wie ein Tor.
    # Alle zulaessigen Hindernisse gemeinsam rechnen, damit auch zwei hintereinander
    # stehende Gebaeude als zusammenhaengender Weg erkannt werden.
    from gebaeudeziele import angreifbar
    from feldzug import BURG_TEILE
    abriss = np.zeros(e["bau"].shape, float)
    ab_ids = set()
    for nr, g_ in G.items():
        if (g_.get("besitzer") in freunde_von(sp) or nr in verworfen or g_["typ"] == ZUGBRUECKE
                or not angreifbar(g_) or g_.get("leben",0) <= 0 or g_.get("feuer",0)>0):
            continue
        schaden_bau = mk["tor_turm"] if g_["typ"] in BURG_TEILE else mk["gebaeude"]
        kosten = math.ceil(g_["leben"] / max(1,float(schaden_bau)*max(1,maenner))) * mk["takte_je_treffer"]
        abriss[e["bau"] == nr] = max(1,kosten)
        ab_ids.add(nr)
    if ab_ids:
        ra = mechanik.durchbruch_schritte(*args, sperre=sperre, gefahr=gf, freunde=freunde, abriss=abriss)
        if ra["weg"]:
            kand.append(("gebaeude", None, ra, abriss))
    bruecken = np.isin(e["bau"], [nr for nr, g_ in G.items() if g_["typ"] == ZUGBRUECKE
                                  and g_.get("besitzer") not in freunde_von(sp)])
    for nr, g_ in G.items():
        if (g_.get("besitzer") in freunde_von(sp) or g_["typ"] not in TORHAEUSER or g_.get("leben", 1) <= 0 or nr in verworfen):
            continue
        # (B-256: der Rand gibt keine Zugbruecke frei - sie bleibt gesperrt, auch wenn sie bis 2 Felder am Torhaus liegt)
        rand = ndimage.binary_dilation(e["bau"] == nr, structure=np.ones((3, 3), bool), iterations=2) & ~bruecken
        # Einschlagen: Leben / Schaden je Treffer an Tor und Turm (Code UpdateMaceman), je Runde ein Treffer je Mann
        kosten = math.ceil(g_.get("leben", 1500) / float(mk["tor_turm"]) / max(1, maenner)) * mk["takte_je_treffer"]
        # B-268 (Partie 175718 'Riverside Rampage', Daniel 27.10.: Zugang (174,341) 3-mal in EINER Runde verworfen und 3-mal wieder
        # geplant - der Rand um Tor/Turm gab die verworfene Kachel wieder frei): verworfene Kacheln bleiben auch hier gesperrt
        rand_frei = rand & ~vsperre
        rt = mechanik.durchbruch_schritte(*args, sperre=(sperre & ~rand_frei), gefahr=gf, frei=rand_frei, frei_kosten=kosten,
                                          freunde=freunde)
        if rt["weg"] and any(rand[q] for q in rt["weg"]):
            kand.append(("tor", nr, rt, rand))
    if not kand:
        return None
    art, nr, r, rand = min(kand, key=lambda k: (k[2]["belastung"] or 0.0, k[2]["takte"]))
    weg = [tuple(q) for q in r["weg"]]
    # ab dem ZWEITEN Wegfeld suchen (sturm Lauf 00:49: der Start lag selbst auf einem Mauerfeld -> Zugang = der Lord)
    mauern = set(map(tuple, r["mauern"]))
    i_wand = next((i for i, q in enumerate(weg) if i >= 1 and q in mauern), None)
    i_tor = next((i for i, q in enumerate(weg) if i >= 1 and rand is not None and rand[q] and not rand[weg[0]]), None)
    i_bau = next((i for i,q in enumerate(weg) if i>=1 and art=="gebaeude" and rand[q]>0
                  and e["bau"][q] != e["bau"][weg[0]]), None)
    if art == "gebaeude":
        i_tor = None
    gemein = {"weg": weg, "takte": r["takte"], "belastung": r["belastung"], "gefahr": gf, "e": e,
              "kandidaten": [(k[0], k[1], round(k[2]["belastung"] or 0), k[2]["takte"]) for k in kand]}
    if i_bau is not None and (i_wand is None or i_bau<i_wand):
        return dict(gemein, art="gebaeude", ziel=int(e["bau"][weg[i_bau]]), zug=weg[i_bau-1])
    if i_tor is not None and (i_wand is None or i_tor < i_wand):
        return dict(gemein, art="tor", ziel=nr, zug=weg[i_tor - 1])
    if i_wand is not None:
        return dict(gemein, art="mauer", ziel=weg[i_wand], zug=weg[i_wand - 1])
    return dict(gemein, art="lord", ziel=None, zug=None)


def anfrage_und_blick(kachel, sp):
    """(Anfrage-Kachel, Blickrichtung), bei denen das Spiel GENAU kachel als Ziel waehlt (mechanik.spiel_wahl, Nachbildung von
    findFreeSpaceNextToEnemyDefensiveStructureInSameAreaWithinDistance) - None, wenn es keine gibt."""
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
            _, w = mechanik.spiel_wahl(r, g_mann, wk["gebiet"], logik, wk["gebaeude"], {}, besitz, sp, acht, blick[i])
            if w == tuple(kachel):
                return r, i
    return None
