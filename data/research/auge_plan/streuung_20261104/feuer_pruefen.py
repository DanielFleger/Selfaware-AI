# -*- coding: utf-8 -*-
"""Haelt die Feuer-Regeln aus dem Code gegen die Aufzeichnung Beschuss, ohne ein Spiel.

Regeln (UpdateFirethrowEntity 00405b70, AFireSpreadFunction 004054e0, UpdateFireEntity 00405680, IgniteFireAtMiniTile 004052e0, processFireDamageToUnit 00532460):
1. Landet eine Flamme, entsteht EIN Feuer am Landepunkt plus Versatz aus der 64er-Tabelle. Steht dort schon Feuer, entsteht keines.
2. Ein Feuer mit Stufe 2 oder mehr zuendet nacheinander die vier Nachbarn an (x-8, x+8, y+8, y-8, je plus Tabellen-Versatz), mit Stufe minus 1.
3. Jeden Takt verliert jede Einheit auf dem Feuerfeld Leben: Tabelle 75, Feuerwerfer-Feuer halb (37).

Was widerlegt das: ein Feuer ausserhalb der Tabelle; ein Kind ausserhalb der Nachbar-Regel; ein Verlust auf einem Feld ohne Feuer, den kein Geschoss erklaert; ein Takt auf dem Feuerfeld ohne Verlust.
Ausgabe: feuer_pruefung.txt.
"""
import collections
import glob
import os
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import flug_pruefen as fp  # noqa: E402
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

VERSATZ = {(0, 0)}
for i in range(1, 8):
    VERSATZ |= {(i, 0), (0, i), (i, i), (-i, i), (-i, -i), (i, -i), (-i, 0), (0, -i)}
VERSATZ |= {(-8, 0), (0, -8), (-8, -8), (8, -8)}
F_F = {"art": "entityType", "da": "logicalState", "uid": "uid", "mx": "microX", "my": "microY", "h": "height", "stufe": "fireParameter_0xb6", "stark": "fireIntensity", "phase": "someTracker", "nachbar": "field79_0xb8", "bild": "unknownAnimationFrameRelated", "bes": "owner", "feld": "tile", "zaehler": "someCounter_OR_hitGround"}


def feuer_lesen(pfad, k):
    auf = Aufzeichnung(pfad)
    ie = auf.namen.index("DAT_EntityState")
    be = auf.bereiche[ie][1]
    ad = {n: k.adresse("DAT_EntityState", "entityArray[]." + f) for n, f in F_F.items()}
    aus = collections.OrderedDict()
    for r, p, _ in auf.staende():
        if r.bereich != ie or not r.rein:
            continue
        a = bytes(p)
        sp = {n: np.ndarray(shape=(v[3],), dtype={2: "<i2", 4: "<i4"}[v[1]], buffer=a, offset=v[0] - be, strides=(v[2],)) for n, v in ad.items()}
        for i in np.nonzero((sp["art"] == 9) & (sp["da"] != 0))[0]:
            aus.setdefault((int(i), int(sp["uid"][i])), []).append((r.takt, {n: int(sp[n][i]) for n in F_F}))
    return aus


def main():
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", sys.argv[1] if len(sys.argv) > 1 else "lauf_s_*_beschuss.auge")), key=os.path.getmtime)[-1]
    k = Feldkarte.laden(feldliste=FELDLISTE)
    lauf = fp.Lauf(pfad, k)
    feuer = feuer_lesen(pfad, k)
    zeilen = fp.zeilen_lesen()
    aus = ["Feuer in der Aufzeichnung: %d" % len(feuer)]
    # Lebensdauer und Stufen
    dauer = collections.Counter()
    stufe = collections.Counter()
    for s, f in feuer.items():
        stufe[(f[0][1]["stufe"], f[0][1]["stark"])] += 1
        lebt = [t for t, z in f if z["da"] != 3 and z["da"] != 7]
        dauer[(f[0][1]["stufe"], len(lebt))] += 1
    aus.append("Feuer je (Stufe, Staerke): " + str(sorted(stufe.items())))
    aus.append("Lebensdauer in Takten je Stufe (Stufe, Takte): Anzahl " + str(sorted(dauer.items())[:30]))
    # 1. Flamme landet -> Feuer
    flammen = [(s, f) for s, f in lauf.fluege.items() if f[0][1]["art"] == 34]
    geb = collections.defaultdict(list)
    for s, f in feuer.items():
        geb[f[0][0]].append((s, f))
    erg = collections.Counter()
    rows = []
    for s, f in flammen:
        ende = next(((t1, z1) for t1, z1 in f[1:] if z1["da"] != 2 or z1["boden"] != 0), None)
        if ende is None:
            erg["Flug endet nicht in der Aufzeichnung"] += 1
            continue
        t, z = ende
        # Erst wenn das Bodenzeichen steht, ruft UpdateFirethrowEntity die Ausbreitung: im selben oder naechsten Takt
        passend = None
        for dt in (0, 1, 2):
            for sf, ff in geb.get(t + dt, ()):
                d = (ff[0][1]["mx"] - z["mx"], ff[0][1]["my"] - z["my"])
                if d in VERSATZ and ff[0][1]["stufe"] == 2 and ff[0][1]["stark"] == 1:
                    passend = (dt, d, sf)
                    break
            if passend:
                break
        rows.append((s, t, z["mx"], z["my"], passend, f[0][1]["ziel"]))
        erg["neues Feuer in der Tabelle" if passend else "kein neues Feuer"] += 1
        if passend:
            erg["  Abstand in Takten %d" % passend[0]] += 1
    aus.append("Flamme landet: " + str(sorted(erg.items())))
    # 2. Nachbarn: Kinder eines Feuers
    kinder = collections.Counter()
    zeiten = collections.Counter()
    ohne = []
    alle = list(feuer.items())
    for s, f in alle:
        z0 = f[0][1]
        if z0["stufe"] >= 2:
            continue
        # Kind sucht Eltern: Feuer gleichen Besitzers mit Stufe+1, lebend, Abstand passt
        t = f[0][0]
        gef = None
        for s2, f2 in alle:
            if s2 == s or f2[0][0] > t:
                continue
            if f2[-1][0] < t - 1:
                continue
            bei = [z for tt, z in f2 if tt in (t - 1, t)]
            if not bei or not any(z["stufe"] >= 2 and z["da"] not in (3, 7) for z in bei):
                continue
            a = f2[0][1]
            for nr, (dx, dy) in enumerate(((-8, 0), (8, 0), (0, 8), (0, -8))):
                d = (z0["mx"] - a["mx"] - dx, z0["my"] - a["my"] - dy)
                if d in VERSATZ:
                    gef = (s2, nr, t - f2[0][0])
                    break
            if gef:
                break
        if gef:
            kinder["Nachbar %d" % gef[1]] += 1
            zeiten[gef[2]] += 1
        else:
            kinder["ohne passende Eltern"] += 1
            ohne.append((s, t, z0["mx"], z0["my"], z0["stufe"]))
    aus.append("Kinder (Stufe 1) nach Nachbar-Nummer: " + str(sorted(kinder.items())))
    aus.append("Takte zwischen Eltern und Kind: " + str(sorted(zeiten.items())[:25]))
    aus.append("Ohne Eltern, Beispiele: " + str(ohne[:6]))
    # 3. Leben: je Takt und Einheit Verlust gegen Feuer auf dem Feld
    u = lauf.u
    takte = sorted(u)
    feld_feuer = collections.defaultdict(set)
    for s, f in feuer.items():
        for t, z in f:
            if z["da"] not in (3, 7) and z["feld"]:
                feld_feuer[t].add(z["feld"])
    geschoss_treffer = collections.Counter()
    for s, f in lauf.fluege.items():
        e = next(((t1, z1) for t1, z1 in f[1:] if z1["da"] == 3 and z1["boden"] == 9), None)
        if e:
            geschoss_treffer[e[0]] += 1
    tab = collections.Counter()
    for a, b in zip(takte, takte[1:]):
        if b != a + 1:
            continue
        va, vb = u[a], u[b]
        leben = (va["da"] != 0) & (va["stirbt"] == 0) & (va["bes"] > 0)
        for i in np.nonzero(leben)[0]:
            auf_feuer = int(vb["feld"][i]) in feld_feuer[b] or int(vb["feld"][i]) in feld_feuer[a]
            d = int(va["leben"][i]) - int(vb["leben"][i])
            if auf_feuer or d == 37:
                tab[("auf Feuer" if auf_feuer else "nicht auf Feuer", d if d in (0, 5, 37, 75) or d < 0 else "anderer Verlust")] += 1
    aus.append("Einheit-Takte (Feuerfeld?, Verlust): " + str(sorted(tab.items(), key=str)))
    # Die vier offenen Schuesse: Flamme, Feuer, Ziel
    aus.append("Flammen und Ziel: Wo landete das Feuer, wo stand das Ziel?")
    st0 = collections.Counter()
    for s, t, mx, my, p, ziel in rows:
        if t not in u:
            continue
        ufeld = int(u[t]["feld"][ziel])
        kn_land = int(zeilen[my >> 3]) + (mx >> 3)
        if p:
            ff = feuer[p[2]][0][1]
            st0[("Feuer auf dem Zielfeld" if ff["feld"] == ufeld else "Feuer daneben", "Landung auf dem Zielfeld" if kn_land == ufeld else "Landung daneben")] += 1
        else:
            st0[("kein neues Feuer", "Landung auf dem Zielfeld" if kn_land == ufeld else "Landung daneben")] += 1
    aus.append(str(sorted(st0.items())))
    # Jeder Flammen-Schuss: Wann brennt das Zielfeld, wann verliert das Ziel Leben?
    feld_von = collections.defaultdict(set)
    for tk, felder in feld_feuer.items():
        for kn in felder:
            feld_von[kn].add(tk)
    klassen = collections.Counter()
    offen = []
    for s, t, mx, my, pa, ziel in rows:
        if t not in u:
            continue
        kn = int(u[t]["feld"][ziel])
        brennt = sorted(x for x in feld_von.get(kn, ()) if t - 3 <= x <= t + 60)
        verlust = [x for x in range(t - 3, t + 61) if x in u and x - 1 in u and u[x]["leben"][ziel] < u[x - 1]["leben"][ziel]]
        stirbt = bool(u[t]["stirbt"][ziel]) or not u[t]["da"][ziel]
        if stirbt:
            klassen["Ziel schon tot"] += 1
        elif not brennt and not verlust:
            klassen["Zielfeld brennt 60 Takte nicht, kein Verlust"] += 1
            offen.append((s, t, mx, my, "Ziel", ziel, "Feld", kn, "Feuer", pa))
        elif not brennt and verlust:
            klassen["Verlust ohne Feuer auf dem Zielfeld"] += 1
            offen.append((s, t, mx, my, "Ziel", ziel, "Verlust", verlust[:3]))
        elif brennt and not verlust:
            klassen["Zielfeld brennt, kein Verlust"] += 1
            offen.append((s, t, mx, my, "Ziel", ziel, "brennt", brennt[:3]))
        else:
            d = verlust[0] - brennt[0]
            klassen["Verlust %+d Takte nach dem ersten Feuer auf dem Feld, %s" % (d, "brannte schon" if brennt[0] < t else "neu")] += 1
    aus.append("Jeder Flammen-Schuss erklaert: " + str(sorted(klassen.items())))
    aus.append("  offen: " + str(offen[:10]))
    # Ablauf eines Feuers
    beispiel = next(f for s, f in feuer.items() if f[0][1]["stufe"] == 2)
    aus.append("Ablauf eines Feuers Stufe 2 (Takt-Abstand: Phase, Bild, Nachbar, Stufe, Zaehler, da):")
    letzt = None
    for tk, z in beispiel:
        w = (z["phase"], z["nachbar"], z["stufe"], z["zaehler"], z["da"])
        if w != letzt:
            aus.append("   +%d: %s Bild %d" % (tk - beispiel[0][0], w, z["bild"]))
        letzt = w
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "feuer_pruefung.txt" if len(sys.argv) < 2 else "feuer_pruefung_" + sys.argv[1].split("*")[-1].replace(".auge", "").strip("_") + ".txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
