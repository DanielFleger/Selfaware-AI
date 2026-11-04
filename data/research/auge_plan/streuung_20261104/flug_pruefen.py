# -*- coding: utf-8 -*-
"""Haelt den Nachbau (flug_modell.py) gegen aufgezeichnete Laeufe, ohne ein Spiel.

Was widerlegt das Modell: ein Winkel oder Tempo, das nicht passt; ein Flug, dessen Mikro-Ort oder Hoehe in irgendeinem Takt abweicht; ein Schuss, dessen vorhergesagtes Ende (Takt, Ort) oder Opfer nicht mit der Aufzeichnung geht.
Grenze: Geprueft wird nur, wo die Aufzeichnung jeden Takt hat. Wandabpraller und Treffer an Gebaeuden sind nicht nachgebaut: Sie zaehlen als "besonders" und werden genannt, nicht versteckt.
Aufruf: flug_pruefen.py [Muster ...] (Dateien unter laeufe/). Ausgabe: flug_pruefung.txt.
"""
import collections
import glob
import os
import pickle
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import flug_modell as fm  # noqa: E402
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402

ARTEN = [1, 2, 3, 4, 7, 20, 33, 34, 37]
E_F = {"art": "entityType", "da": "logicalState", "uid": "uid", "mx": "microX", "my": "microY", "h": "height", "zx": "targetX", "zy": "targetY", "zz": "targetZ", "h0": "startingHeight", "hd": "heightDifference",
       "v": "velocityUnk", "w": "startingAngle", "t": "speedUnk", "vc": "vCos", "vs": "vSin", "wg": "travelledDistance", "gesamt": "field58_0x8c", "frei": "field80_0xba", "rng": "rng_1", "rng2": "rng_2", "sch": "unitID_OR_seaGullID", "ziel": "unitID", "bes": "owner", "boden": "someCounter_OR_hitGround", "bremse": "_elapsedTimeOrGravityAccumulator", "eff": "hasDoneEffectUnk"}
FLOAT = {"t", "vc", "vs", "bremse"}
U_F = {"da": "logicalState", "x": "x", "y": "y", "hb": "buildingHeight", "ht": "terrainOrClimbHeight", "bes": "owner", "stirbt": "dying", "typ": "unitType", "leben": "health", "next": "nextUnitOnTheSameTile", "f90": "field67_0x90", "feld": "tile"}
DT = {1: "<u1", 2: "<i2", 4: "<i4"}


class Lauf:
    """Eine Aufzeichnung: Geschosse und Einheiten je Takt, Gelaende und Gebaeude je Rahmen."""

    def __init__(self, pfad, k):
        self.pfad = pfad
        self.k = k
        self.fluege = {}
        self.u = {}
        self.gel = []
        self.bau = []
        self.pflanzen = None
        self.teams = None
        self.mitten_drin = set()
        auf = Aufzeichnung(pfad)
        ie, iu, it, ib, il, ig = [auf.namen.index(n) for n in ("DAT_EntityState", "DAT_UnitsState", "DAT_TileMapState", "DAT_BuildingsState", "DAT_LandscapeState", "DAT_GameState")]
        be, bu, bt, bb, bl, bg = [auf.bereiche[i][1] for i in (ie, iu, it, ib, il, ig)]
        ae = {n: k.adresse("DAT_EntityState", "entityArray[]." + f) for n, f in E_F.items()}
        au = {n: k.adresse("DAT_UnitsState", "units[]." + f) for n, f in U_F.items()}
        at = {n: k.adresse("DAT_TileMapState", f) for n, f in (("hoehe", "HeightLayer[]"), ("logik", "LogicLayer[]"), ("bau", "BuildingLayer[]"), ("pflanze", "OrganismLayer[]"))}
        ab = k.adresse("DAT_BuildingsState", "buildings[].buildingType")
        ate = k.adresse("DAT_GameState", "mapAndTime.playerTeams[]")
        for r, p, _ in auf.staende():
            if not r.rein:
                continue
            if r.bereich == ie:
                a = bytes(p)
                sp = {n: np.ndarray(shape=(v[3],), dtype=("<f4" if n in FLOAT else DT[v[1]]), buffer=a, offset=v[0] - be, strides=(v[2],)) for n, v in ae.items()}
                for i in np.nonzero(np.isin(sp["art"], ARTEN) & (sp["da"] != 0))[0]:
                    sch = (int(i), int(sp["uid"][i]))
                    if sch not in self.fluege and (int(sp["wg"][i]) != 0 or abs(float(sp["t"][i]) - float(sp["bremse"][i])) > 1e-6):
                        self.mitten_drin.add(sch)  # erst nach dem Abschuss im Bild: sagt nichts ueber den Start
                    if sch not in self.mitten_drin:
                        self.fluege.setdefault(sch, []).append((r.takt, {n: (float(sp[n][i]) if n in FLOAT else int(sp[n][i])) for n in E_F}))
            elif r.bereich == iu:
                a = bytes(p)
                self.u[r.takt] = {n: np.array(np.ndarray(shape=(v[3],), dtype=DT[v[1]], buffer=a, offset=v[0] - bu, strides=(v[2],))[:2400]) for n, v in au.items()}
            elif r.bereich == it:
                a = bytes(p)
                self.gel.append((r.takt, {n: np.array(np.ndarray(shape=(v[3],), dtype=DT[v[1]], buffer=a, offset=v[0] - bt, strides=(v[2],))) for n, v in at.items()}))
            elif r.bereich == ib:
                self.bau.append((r.takt, np.array(np.ndarray(shape=(ab[3],), dtype="<i2", buffer=bytes(p), offset=ab[0] - bb, strides=(ab[2],)))))
            elif r.bereich == il and self.pflanzen is None:
                self.pflanzen = np.frombuffer(bytes(p), dtype="<u2", offset=0xf78f40 - bl).copy()  # Baumhoehe je Pflanze, Abstand 32 Byte: returnSomeHeight 004ffa6f
            elif r.bereich == ig and self.teams is None:
                self.teams = np.ndarray(shape=(ate[3],), dtype="<i4", buffer=bytes(p), offset=ate[0] - bg, strides=(ate[2],)).copy()

    def stand(self, liste, t):
        """Letzter Rahmen bis Takt t."""
        best = liste[0][1] if liste else None
        for tk, x in liste:
            if tk > t:
                break
            best = x
        return best


def zeilen_lesen():
    return np.load(os.path.join(HIER, "zeilen.npy"))


def bauhoehen():
    return np.load(os.path.join(HIER, "bauhoehen.npy"))


def feldhoehe(kn, gel, bau, lauf, hoehen):
    """returnSomeHeight 004ff990, zweiter Wert 0."""
    lg = int(gel["logik"][kn])
    h = int(gel["hoehe"][kn])
    if lg & 0x10000000:
        return h + fm.gebaeude_hoehe(bau[int(gel["bau"][kn])])
    if not lg & 0x400:
        p = int(gel["pflanze"][kn])
        if lg & 0x80 and not lg & 0x100 and p > 1999 and lauf.pflanzen is not None:
            w = int(lauf.pflanzen[(p - 2000) * 16])
            return h + (70 if w >= 13 else 50 if w >= 9 else 0)
        return h
    ty = int(bau[int(gel["bau"][kn])])
    if ty in (0x28, 0x29, 0x2a, 0x2b, 0x2c):
        return h + fm.gebaeude_hoehe(ty)
    if ty in (0x2d, 0x2e, 0x3d, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e):
        return h + fm.gebaeude_hoehe(ty) + 10
    return h + int(hoehen[ty])


def reihenfolge(st, kn):
    """Einheiten auf dem Feld in der Reihenfolge der Spielliste."""
    alle = np.nonzero((st["feld"] == kn) & (st["da"] != 0))[0]
    if len(alle) < 2:
        return [int(i) for i in alle]
    naechste = {int(st["next"][i]) for i in alle}
    kopf = [int(i) for i in alle if int(i) not in naechste]
    if not kopf:
        return [int(i) for i in alle]
    aus, i = [], kopf[0]
    while i and len(aus) < 200:
        aus.append(i)
        i = int(st["next"][i])
    return aus


def vorhersage(z, f, lauf, zeilen, hoehen, aus_takt=()):
    """Fliegt den Schuss mit den Einheiten des Takts davor. Ergebnis (Art, Takt, Einheit, Mx, My, H) oder None; aus_takt: (Takt, Einheit), die in diesem Takt schon tot sind."""
    t = f[0][0]
    prueft = z["art"] in (2, 3, 4) or z["v"] > 0x50
    if z["art"] == 1 and z["rng2"] == 2:
        prueft = False  # Brandpfeil auf Pech: zaehlt keine Einheiten
    te = lauf.teams
    letzt_schritt = None
    for n, schr, h_e in fm.bahn(z["mx"], z["my"], z["h0"], z["zx"], z["zy"], z["vc"], z["vs"], z["bremse"]):
        tk = t + n
        st = lauf.u.get(tk)
        vor = lauf.u.get(tk - 1)
        if st is None or vor is None:
            return ("takte fehlen", tk, None, None, None, None)
        gel = lauf.stand(lauf.gel, tk)
        bau = lauf.stand(lauf.bau, tk)
        if schr:
            letzt_schritt = schr[-1]
        pruefen = list(schr)
        if h_e < 3 and letzt_schritt is not None:
            pruefen.append((letzt_schritt[0], letzt_schritt[1], h_e, letzt_schritt[3]))
        for x, y, h, wg in pruefen:
            fx, fy = x >> 3, y >> 3
            if not (0 <= fx < 400 and 0 <= fy < 400):
                return ("rand", tk, None, x, y, h)
            kn = int(zeilen[fy]) + fx
            if prueft:
                for i in reihenfolge(st, kn):
                    if i == z["sch"] or i == 0 or (tk, i) in aus_takt or vor["stirbt"][i]:
                        continue
                    if te[int(st["bes"][i])] == te[z["bes"]]:
                        if not (z["art"] in (2, 3) and int(st["typ"][i]) not in (fm.UT_SCHILD, fm.UT_TURM, fm.UT_RAMME)):
                            continue
                    boden = int(st["hb"][i]) + int(st["ht"][i])
                    if boden <= h <= boden + fm.fenster(int(st["typ"][i])):
                        return ("einheit", tk, i, x, y, h)
            hoehe = feldhoehe(kn, gel, bau, lauf, hoehen)
            if h < hoehe and (wg > z["gesamt"] // 2 or z["art"] in (2, 3, 4)):
                lg = int(gel["logik"][kn])
                if lg & 0x10000500 or int(gel["bau"][kn]) or lg & 0x40100001:
                    return ("besonders", tk, None, x, y, h)
                return ("boden", tk, None, x, y, h)
    return None


def pruefe(pfad, k, zeilen, hoehen):
    lauf = Lauf(pfad, k)
    fl = lauf.fluege
    if not fl:
        return None
    wk = collections.Counter()
    for sch, f in fl.items():
        z = f[0][1]
        wk[(z["art"], fm.anfang(z["art"], z["gesamt"], z["zz"] - z["h0"], z["v"]) == (z["v"], z["w"]))] += 1
    gut = abw = 0
    erste = []
    abpraller = collections.Counter()
    for sch, f in fl.items():
        z = f[0][1]
        letzt = (z["mx"], z["my"], 0)
        vorher_t = None
        for (t1, z1), (n, schr, h_e) in zip(f[1:], fm.bahn(z["mx"], z["my"], z["h0"], z["zx"], z["zy"], z["vc"], z["vs"], z["bremse"])):
            if z1["da"] != 2 or z1["boden"] != 0 or t1 != f[0][0] + n:
                break
            if z1["v"] != z["v"]:
                abpraller["Tempo geteilt durch 8" if z1["v"] == z["v"] // 8 else "anderes Tempo"] += 1
                break
            if n > 1 and z1["t"] == vorher_t:
                abpraller["Rahmen zeigt noch den Takt davor (Aufnahme)"] += 1
                continue
            vorher_t = z1["t"]
            if schr:
                letzt = (schr[-1][0], schr[-1][1], schr[-1][3])
            if (letzt[0], letzt[1], h_e, letzt[2]) == (z1["mx"], z1["my"], z1["h"], z1["wg"]):
                gut += 1
            else:
                abw += 1
                if len(erste) < 4:
                    erste.append((sch, t1, "Spiel", z1["mx"], z1["my"], z1["h"], z1["wg"], "Modell", schr[-1] if schr else None, h_e))
                break
    v1 = {s: vorhersage(f[0][1], f, lauf, zeilen, hoehen) for s, f in fl.items()}
    verlust = collections.defaultdict(collections.Counter)
    anspruch = collections.defaultdict(list)
    for s, v in v1.items():
        if v and v[0] == "einheit":
            anspruch[(v[1], v[2])].append(s)
    u = lauf.u
    for (tk, i), l in anspruch.items():
        if len(l) == 1 and tk in u and tk - 1 in u:
            d = int(u[tk - 1]["leben"][i] - u[tk]["leben"][i])
            if d > 0 and not u[tk]["stirbt"][i]:
                verlust[(fl[l[0]][0][1]["art"], int(u[tk]["typ"][i]))][d] += 1
    aus_takt = collections.defaultdict(set)
    for (tk, i), l in anspruch.items():
        if tk not in u or not u[tk]["stirbt"][i] or u[tk - 1]["stirbt"][i]:
            continue
        rest = int(u[tk - 1]["leben"][i])
        for s in sorted(l, key=lambda s: s[0]):
            if rest <= 0:
                aus_takt[s].add((tk, i))
            d = verlust[(fl[s][0][1]["art"], int(u[tk]["typ"][i]))].most_common(1)
            rest -= d[0][0] if d else 10 ** 6
    erg = collections.Counter()
    fehl = []
    opfer = collections.Counter()
    for sch, f in fl.items():
        z = f[0][1]
        art = z["art"]
        ende = next(((t1, z1) for t1, z1 in f[1:] if z1["da"] != 2 or z1["boden"] != 0), None)
        if ende is None:
            erg[(art, "Aufzeichnung endet vor der Landung")] += 1
            continue
        v = vorhersage(z, f, lauf, zeilen, hoehen, aus_takt.get(sch, ()))
        sp_art = "einheit" if ende[1]["da"] == 3 and ende[1]["boden"] == 9 else "boden"
        if v and v[0] == "besonders" and (v[1], v[3], v[4]) == (ende[0], ende[1]["mx"], ende[1]["my"]):
            erg[(art, "richtig, Ende an Gebaeude oder Wasser")] += 1
            continue
        if v is None or v[0] in ("takte fehlen", "besonders", "rand"):
            erg[(art, "nicht geprueft: " + (v[0] if v else "Modell ohne Ende"))] += 1
            if v is None or v[0] == "rand":
                fehl.append((sch, art, "Modell", v, "Spiel", sp_art, ende[0], ende[1]["mx"], ende[1]["my"], ende[1]["h"], ende[1]["da"], ende[1]["boden"], "ziel", z["ziel"]))
            continue
        gleich = (v[0] == sp_art, v[1] == ende[0], (v[3], v[4]) == (ende[1]["mx"], ende[1]["my"]))
        verlor = None
        if v[0] == "einheit":
            sp, vor = u.get(v[1]), u.get(v[1] - 1)
            verlor = bool(sp is not None and vor is not None and sp["leben"][v[2]] < vor["leben"][v[2]])
            opfer["anvisiertes Ziel" if v[2] == z["ziel"] else ("Tier" if vor["bes"][v[2]] == 0 else ("Freund" if vor["bes"][v[2]] == z["bes"] else "anderer Feind"))] += 1
        ok = all(gleich) and verlor is not False
        erg[(art, "richtig" if ok else "FALSCH")] += 1
        if not ok:
            fehl.append((sch, art, "Modell", v, "Spiel", sp_art, ende[0], ende[1]["mx"], ende[1]["my"], ende[1]["h"], ende[1]["da"], ende[1]["boden"], "ziel", z["ziel"]))
    return {"datei": os.path.basename(pfad), "fluege": len(fl), "takte": len(u), "anfang": wk, "bahn_gleich": gut, "bahn_abw": abw, "bahn_erste": erste, "abpraller": abpraller, "ende": erg, "fehl": fehl, "opfer": opfer}


def main():
    k = Feldkarte.laden(feldliste=FELDLISTE)
    zeilen, hoehen = zeilen_lesen(), bauhoehen()
    muster = sys.argv[1:] or ["lauf_s_*_beschuss.auge"]
    dateien = []
    for m in muster:
        dateien += sorted(glob.glob(os.path.join(HIER, "..", "laeufe", m)))
    aus = []
    summe = collections.Counter()
    anf = collections.Counter()
    opf = collections.Counter()
    alle_fehl = []
    bg = ba = 0
    abp = collections.Counter()
    for d in dateien:
        try:
            e = pruefe(d, k, zeilen, hoehen)
        except Exception as x:  # eine kaputte Datei haelt die Reihe nicht an, steht aber im Ergebnis
            aus.append("%s: nicht lesbar: %r" % (os.path.basename(d), x))
            continue
        if e is None:
            continue
        summe.update(e["ende"])
        anf.update(e["anfang"])
        opf.update(e["opfer"])
        bg += e["bahn_gleich"]
        abp.update(e["abpraller"])
        ba += e["bahn_abw"]
        alle_fehl += [(e["datei"],) + x for x in e["fehl"]]
        z = "%s: Fluege %d, Rahmen %d, Bahn %d gleich %d abw, Ende %s" % (e["datei"], e["fluege"], e["takte"], e["bahn_gleich"], e["bahn_abw"], sorted(e["ende"].items(), key=str))
        aus.append(z)
        print(z[:300], flush=True)
        if e["bahn_erste"]:
            aus.append("   erste Bahn-Abweichung: " + str(e["bahn_erste"]))
    aus.append("")
    aus.append("SUMME Anfang (Art, Tempo und Winkel gleich): " + str(sorted(anf.items())))
    aus.append("SUMME Bahn in der Luft: gleich %d, abweichend %d (je Flug bis zur ersten Abweichung)" % (bg, ba))
    aus.append("SUMME Abpraller in der Luft (Vergleich endet dort): " + str(sorted(abp.items())))
    aus.append("SUMME Ende: " + str(sorted(summe.items(), key=str)))
    aus.append("SUMME Opfer: " + str(sorted(opf.items())))
    aus.append("Abweichungen (%d), die ersten 40:" % len(alle_fehl))
    aus += ["  " + str(x) for x in alle_fehl[:40]]
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "flug_pruefung.txt"), "w", encoding="utf-8").write(text)
    pickle.dump(alle_fehl, open(os.path.join(HIER, "flug_fehl.pkl"), "wb"))
    print(chr(10).join(aus[-(len(alle_fehl[:40]) + 5):]))


if __name__ == "__main__":
    main()
