# -*- coding: utf-8 -*-
"""Szene korb_g (P312): Auf welchen Feldern blieb der Feuerkorb nach Befehl 69 stehen, und was kostet er?

Regel aus dem Code (processEntityHitBuildingOrUnit 00407190), jedes Feld einzeln dagegen gehalten:
  ausserhalb der Karte: Zustand 3, weg. Logik 0x30: zerstoert.
  Feld mit Gebaeude: bleibt nur auf Bergfried, Torhaus, Turm, dort auf jedem Feld, Hoehe = Gesamthoehe.
  Feld ohne Gebaeude: bleibt nur mit Logik 0x100 (Mauer), Hoehe = Hoehenschicht.
Widerlegt wird die Regel durch ein Feld, das abweicht. Ein Mauerstueck, das nicht gebaut wurde, zaehlt nicht als geprueft und steht als NICHT GEBAUT in der Ausgabe.
Die Oberflaeche (getHeightAtTileIncludingOwnersBuildings 004fff10) ist eine eigene Frage: Sie wurde im Stand gefragt, bevor ein Korb stand.
Ausgabe: korb_pruefung.txt. Eingabe: neueste Aufzeichnung lauf_s_*_korb_g.auge, Protokoll lauf_korb_g.log.
"""
import collections
import glob
import json
import os
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

ERLAUBT_GEBAEUDE = (41, 42, 43, 44, 45, 46, 74, 75, 76, 77, 78)
MAUERARTEN = ("hohe Mauer", "Treppe", "Zinne an Mauer", "Zinne allein")
F = {"art": "entityType", "da": "logicalState", "mx": "microX", "my": "microY", "h": "height", "bes": "owner"}


def code_sagt(z):
    """True: der Korb bleibt stehen."""
    if z["aussen"] or z["logik"] & 0x30:
        return False
    if z["gebaeude"]:
        return z["art"] in ERLAUBT_GEBAEUDE
    return bool(z["logik"] & 0x100)


def koerbe_lesen(pfad, k):
    """Je Korb (Nummer, Feld) der erste und der letzte Takt, dazu Hoehe und Zustand. Liest die Liste aller Entities, nicht die Feldlisten."""
    auf = Aufzeichnung(pfad)
    ie = auf.namen.index("DAT_EntityState")
    be = auf.bereiche[ie][1]
    ad = {n: k.adresse("DAT_EntityState", "entityArray[]." + f) for n, f in F.items()}
    koerbe, letzter, stand = {}, None, 0
    for r, p, _ in auf.staende():
        if r.bereich != ie or not r.rein:
            continue
        letzter = r.takt
        stand += 1
        a = bytes(p)
        sp = {n: np.ndarray(shape=(v[3],), dtype={2: "<i2", 4: "<i4"}[v[1]], buffer=a, offset=v[0] - be, strides=(v[2],)) for n, v in ad.items()}
        for i in np.nonzero((sp["art"] == 14) & (sp["da"] != 0))[0]:
            n = (int(i), int(sp["mx"][i]) >> 3, int(sp["my"][i]) >> 3)
            d = koerbe.setdefault(n, {"von": r.takt, "h": set(), "zustand": set(), "besitzer": set()})
            d["bis"] = r.takt
            d["h"].add(int(sp["h"][i]))
            d["zustand"].add(int(sp["da"][i]))
            d["besitzer"].add(int(sp["bes"][i]))
    return koerbe, letzter, stand


def main():
    pfad = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_korb_g.auge")), key=os.path.getmtime)[-1]
    k = Feldkarte.laden(feldliste=FELDLISTE)
    zeilen = [json.loads(z) for z in open(os.path.join(HIER, "lauf_korb_g.log"), encoding="utf-8", errors="replace") if z.startswith('{"schritt": "korb_')]
    je = collections.defaultdict(list)
    for z in zeilen:
        je[z["schritt"]].append(z)
    ziele = je["korb_ziele"][-1]["ziele"]
    koerbe, letzter, staende = koerbe_lesen(pfad, k)
    orte = collections.defaultdict(list)
    for (nr, x, y), d in koerbe.items():
        orte[(x, y)].append(dict(d, nr=nr))
    boden_logik = {z["logik"] for z in ziele if z["art"] == "Boden"}
    aus = ["Datei %s, Takt bis %s, Staende %d" % (os.path.basename(pfad), letzter, staende)]
    aus.append("Karte: %s" % je["korb_maske"][-1])
    aus.append("Gebaeude nicht gesetzt: %s" % je["korb_ziele"][-1]["nicht_gesetzt"])
    aus.append("Befehle: %d. Koerbe je gesehen: %d, davon mit Nummer unter 25: %d" % (len(ziele), len(koerbe), sum(1 for n in koerbe if n[0] < 25)))
    tab = collections.defaultdict(collections.Counter)
    hoehen = collections.defaultdict(set)
    logik = collections.defaultdict(set)
    abw, nicht_gebaut = [], []
    for z in ziele:
        o = orte.get((z["x"], z["y"]), [])
        steht = any(d["bis"] == letzter and d["zustand"] == {2} for d in o)
        name = (str(z["art"]) + (" fremd" if z.get("fremd") else ""), "aussen" if z["aussen"] else "innen" if z["innen"] else "Rand")
        c = tab[name]
        c["Felder"] += 1
        c["steht am Ende" if steht else "kurz gesehen, dann weg" if o else "in keinem Takt gesehen"] += 1
        if z["ober"] is not None:
            c["Oberflaeche ja" if z["ober"] > 0 else "Oberflaeche nein"] += 1
        for d in o:
            hoehen[name] |= d["h"]
        if z["logik"] is not None:
            logik[name].add(hex(z["logik"]))
        if z["art"] in MAUERARTEN and z["logik"] in boden_logik:
            nicht_gebaut.append((z["art"], z["x"], z["y"]))
        elif code_sagt(z) != steht:
            abw.append((z["art"], z["x"], z["y"], "Logik %x" % (z["logik"] or 0), "Code sagt %s, gesehen %s" % (code_sagt(z), o[:1])))
    aus.append("")
    aus.append("Art, Lage: Ergebnis")
    for n in sorted(tab):
        aus.append("  %s, %s: %s, Korb-Hoehe %s, Logik %s" % (n[0], n[1], dict(tab[n]), sorted(hoehen[n]), sorted(logik[n])))
    aus.append("")
    aus.append("NICHT GEBAUT, also nicht geprueft: %d Felder %s" % (len(nicht_gebaut), collections.Counter(a for a, _, _ in nicht_gebaut).most_common()))
    aus.append("Abweichungen von der Regel aus dem Code: %d von %d geprueften Feldern" % (len(abw), len(ziele) - len(nicht_gebaut)))
    aus += ["  %s" % (a,) for a in abw[:40]]
    if koerbe:
        aus.append("Erster Korb Takt %d, letzter neuer Korb Takt %d" % (min(d["von"] for d in koerbe.values()), max(d["von"] for d in koerbe.values())))
    # Doppelprobe: dieselbe Feldnummer, aussen und echt
    aus.append("")
    aus.append("Doppelprobe, dieselbe Feldnummer:")
    alt = {(a[0], a[1]): a for z in je["korb_alt"] for a in z["aussen"]}
    for z in ziele:
        if z["aussen"]:
            a = alt.get((z["x"], z["y"]))
            o = orte.get((z["x"], z["y"]), [])
            e = z.get("echt")
            echt_steht = None
            if e:
                echt_steht = any(d["bis"] == letzter and d["zustand"] == {2} for d in orte.get(tuple(e), []))
            aus.append("  aussen (%d, %d) Feldnummer %d: gesehen %s, Listenkopf nach dem Befehl %s; echt %s: Korb steht %s" % (z["x"], z["y"], z["feld"], [(d["von"], d["bis"], sorted(d["zustand"])) for d in o], a[3:] if a else None, e, echt_steht))
    # Die Lesart der alten Probe auf denselben Feldern
    if je["korb_ende"]:
        stehen = {(z["x"], z["y"]) for z in ziele if any(d["zustand"] == {2} for d in orte.get((z["x"], z["y"]), []))}
        kopf = collections.Counter()
        for x, y, nr, art in je["korb_ende"][-1]["listenkopf"]:
            kopf[("Korb steht" if (x, y) in stehen else "kein Korb", "Listenkopf Art %s" % art)] += 1
        aus.append("")
        aus.append("Lesart der alten Probe (Kopf von EntityLayer am Feld): %s" % dict(kopf))
    aus.append("")
    aus.append("Gold von Spieler 1 (Ware 15):")
    for z in je["korb_gold"]:
        aus.append("  Takt %s, Modus %s, Gold %s, Eingang %s: %s" % (z["takt"], z["modus"], z["gold"], z["start"], z["was"]))
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "korb_pruefung.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
