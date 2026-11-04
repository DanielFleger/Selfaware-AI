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
       "v": "velocityUnk", "w": "startingAngle", "t": "speedUnk", "vc": "vCos", "vs": "vSin", "wg": "travelledDistance", "gesamt": "field58_0x8c", "frei": "field80_0xba", "rng": "rng_1", "rng2": "rng_2", "sch": "unitID_OR_seaGullID", "ziel": "unitID", "bes": "owner", "boden": "someCounter_OR_hitGround", "bremse": "_elapsedTimeOrGravityAccumulator", "eff": "hasDoneEffectUnk", "ori": "orientation", "rot": "graphicRotationUnk"}
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


NACHBARN = ((1, -1), (1, 1), (-1, 1), (-1, -1))  # Richtungen 1, 3, 5, 7 der Tabelle directionTranslationMatrix
BURG = (41, 42, 43, 44)
RAKETEN = (1, 7, 20, 33, 34)


def trifft_unit(z, art, i, st, vor, te, menschen, h, sch, abstand, durch=None):
    """processEntityDamageToUnit 00531920: Treffer ja oder nein. durch sammelt (Art, Einheit): Freund im Trefferfenster, der laut Regel nicht getroffen wird."""
    if i == sch or i == 0 or vor["stirbt"][i]:
        return False
    typ = int(st["typ"][i])
    boden = int(st["hb"][i]) + int(st["ht"][i])
    im_fenster = boden <= h <= boden + (fm.fenster(typ) if abstand == 0 else fm.fenster_nachbar(typ))
    if te[int(st["bes"][i])] == te[z["bes"]]:
        if fm.freund_verschont(art, typ, z["bes"] in menschen):
            if im_fenster and durch is not None:
                durch.add((art, int(st["bes"][i]), typ))
            return False
    return im_fenster


def vorhersage(z, f, lauf, zeilen, hoehen, aus_takt=(), menschen=(1,), spur=None, durch=None, abpr_log=None):
    """Fliegt den Schuss mit dem Spielstand je Takt. Ergebnis (Art, Takt, Einheit, Mx, My, H) oder None. spur bekommt je Takt (mx, my, h, Schritt, Tempo)."""
    art = z["art"]
    x, y, h0, tx, ty, vc, vs, b, v, w0 = z["mx"], z["my"], z["h0"], z["zx"], z["zy"], z["vc"], z["vs"], z["bremse"], z["v"], z["w"]
    frei, eff, gesamt, rng = z["frei"], z["eff"], z["gesamt"], z["rng"]
    te = lauf.teams
    tk = f[0][0]
    t0 = None
    letzt = (x, y, h0, 0)
    abpr = 0
    while abpr < 5:
        neu = False
        for n, schr, h_e, tt in fm.bahn2(x, y, h0, tx, ty, vc, vs, b, t0=t0):
            tk += 1
            st, vor = lauf.u.get(tk), lauf.u.get(tk - 1)
            if st is None or vor is None:
                return ("takte fehlen", tk, None, None, None, None)
            gel = lauf.stand(lauf.gel, tk)
            bau = lauf.stand(lauf.bau, tk)
            f45 = fm.bildnummer(fm.drehung(vc, vs, b, tt, w0))
            prueft = art in (2, 3, 4) or v > 0x50
            if art == 1 and z["rng2"] == 2:
                prueft = False  # Brandpfeil auf Pech zaehlt keine Einheiten
            schritte = [(a, c, h, wg, True) for a, c, h, wg in schr]
            if schritte:
                letzt = schr[-1]
            if h_e < 3:
                schritte.append((letzt[0], letzt[1], h_e, letzt[3], False))  # updateProjectileHeightAndCollision prueft unter Hoehe 3 noch einmal
            for a, c, h, wg, echt in schritte:
                if echt:
                    frei -= 1
                fx, fy = a >> 3, c >> 3
                if not (0 <= fx < 400 and 0 <= fy < 400):
                    return ("rand", tk, None, a, c, h)
                kn = int(zeilen[fy]) + fx
                if prueft:
                    for i in reihenfolge(st, kn):
                        if (tk, i) not in aus_takt and trifft_unit(z, art, i, st, vor, te, menschen, h, z["sch"], 0, durch):
                            return ("einheit", tk, i, a, c, h, 0)
                    for dx, dy in NACHBARN:
                        nb = int(zeilen[fy + dy]) + fx + dx
                        for i in reihenfolge(st, nb):
                            if st["f90"][i] and (tk, i) not in aus_takt and trifft_unit(z, art, i, st, vor, te, menschen, h, z["sch"], 1, durch):
                                return ("einheit", tk, i, a, c, h, 1)
                hoehe = feldhoehe(kn, gel, bau, lauf, hoehen)
                bn = int(gel["bau"][kn])
                ty_b = int(bau[bn]) if bn else 0
                if bn and (ty_b == 0x3d or 0x4a <= ty_b <= 0x4e) and rng & 4:
                    hoehe += 20
                if h >= hoehe:
                    continue
                lg = int(gel["logik"][kn])
                if art not in RAKETEN:
                    return ("besonders" if (lg & 0x10000500 or bn or lg & 0x40100001) else "boden", tk, None, a, c, h)
                if wg <= gesamt // 2:
                    continue
                if lg & 0x40100001:
                    return ("besonders", tk, None, a, c, h)
                wand = (lg & 0x10000100) != 0 or ty_b in BURG
                if not wand:
                    return ("besonders" if (lg & 8 or bn) else "boden", tk, None, a, c, h)
                if (f45 < 3 and w0 < 0) or eff or frei > 0:
                    continue
                # Abprall: der Takt endet hier, das Geschoss fliegt von diesem Punkt neu los
                def ist_wand(u, w_):
                    k_ = int(zeilen[w_]) + u
                    lw = int(gel["logik"][k_])
                    return (lw & 0x10000100) != 0
                bits = fm.wand_bits(fx, fy, ist_wand)
                tx, ty = fm.abprall_ziel(z["ori"], a, c, z["mx"], z["my"], bits)
                if abpr_log is not None:
                    abpr_log.append({"takt": tk, "ori": z["ori"], "a": a, "c": c, "h": h, "sx": z["mx"], "sy": z["my"], "bits": bits, "vc": vc, "vs": vs, "b": b, "tt": tt, "w0": w0, "v_alt": v})
                v, w0, vc, vs = fm.nach_abprall(fm.drehung(vc, vs, b, tt, w0), v)
                x, y, h0 = a, c, h
                t0 = 0.0
                letzt = (a, c, h, 0)
                abpr += 1
                neu = True
                break
            if neu:
                if spur is not None:
                    spur[tk] = (x, y, h0, 0, v)
                break
            if spur is not None:
                spur[tk] = (letzt[0], letzt[1], h_e, letzt[3], v)
        if not neu:
            return None
    return ("zu viele Abpraller", tk, None, x, y, h0)


def pruefe(pfad, k, zeilen, hoehen):
    lauf = Lauf(pfad, k)
    fl = lauf.fluege
    if not fl:
        return None
    menschen = (1, 2) if "_g" in os.path.basename(pfad) else (1,)
    wk = collections.Counter()
    for sch, f in fl.items():
        z = f[0][1]
        wk[(z["art"], fm.anfang(z["art"], z["gesamt"], z["zz"] - z["h0"], z["v"]) == (z["v"], z["w"]))] += 1
    v1 = {s: vorhersage(f[0][1], f, lauf, zeilen, hoehen, menschen=menschen) for s, f in fl.items()}
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
    gut = abw = 0
    erste = []
    abpraller = collections.Counter()
    orient = collections.Counter()
    for sch, f in fl.items():
        z = f[0][1]
        art = z["art"]
        spur = {}
        durch = set()
        v = vorhersage(z, f, lauf, zeilen, hoehen, aus_takt.get(sch, ()), menschen, spur, durch)
        # Bahn Takt fuer Takt, auch nach einem Abprall
        vorher_t = None
        abprallte = False
        for t1, z1 in f[1:]:
            if z1["da"] != 2 or z1["boden"] != 0:
                break
            if t1 not in spur:
                break
            if vorher_t is not None and z1["t"] == vorher_t and z1["v"] == z["v"]:
                abpraller["Rahmen zeigt noch den Takt davor (Aufnahme)"] += 1
                continue
            vorher_t = z1["t"]
            s_ = spur[t1]
            if z1["v"] != z["v"]:
                abprallte = True
            if (s_[0], s_[1], s_[2], s_[3], s_[4]) == (z1["mx"], z1["my"], z1["h"], z1["wg"], z1["v"]):
                gut += 1
                if abprallte:
                    abpraller["Takte nach dem Abprall gleich"] += 1
            else:
                abw += 1
                if abprallte:
                    abpraller["Takte nach dem Abprall abweichend"] += 1
                if len(erste) < 8:
                    erste.append((sch, "Art", art, "Takt", t1, "Spiel", z1["mx"], z1["my"], z1["h"], z1["wg"], z1["v"], z1["w"], "Modell", s_, "ori", z["ori"], "Start", z["mx"], z["my"], "Ziel", z["zx"], z["zy"]))
                break
        if abprallte:
            abpraller["Fluege mit Abprall"] += 1
            orient[z["ori"]] += 1
        ende = next(((t1, z1) for t1, z1 in f[1:] if z1["da"] != 2 or z1["boden"] != 0), None)
        if ende is None:
            erg[(art, "Aufzeichnung endet vor der Landung")] += 1
            continue
        sp_art = "einheit" if ende[1]["da"] == 3 and ende[1]["boden"] == 9 else "boden"
        if z["rng2"] != 0 and ende[1]["da"] == 7 and v is not None:
            sp_art = v[0]  # Brandpfeil: Zustand 7 an jedem Ende (UpdateArrowEntity), die Art des Endes zeigt erst der Verlust am Opfer
        if v is not None and v[0] != "takte fehlen":
            for art_, bes_, typ_ in durch:
                opfer["Freund durchflogen: Geschoss %d, Spieler %d, Art %d" % (art_, bes_, typ_)] += 1
        if v is None or v[0] in ("takte fehlen", "rand", "zu viele Abpraller"):
            erg[(art, "nicht geprueft: " + (v[0] if v else "Modell ohne Ende"))] += 1
            if v is None or v[0] != "takte fehlen":
                fehl.append((sch, art, "Modell", v, "Spiel", sp_art, ende[0], ende[1]["mx"], ende[1]["my"], ende[1]["h"], ende[1]["da"], ende[1]["boden"], "ziel", z["ziel"]))
            continue
        gleich = (v[0] == sp_art or v[0] == "besonders", v[1] == ende[0], (v[3], v[4]) == (ende[1]["mx"], ende[1]["my"]))
        verlor = None
        if v[0] == "einheit":
            sp, vor = u.get(v[1]), u.get(v[1] - 1)
            verlor = bool(sp is not None and vor is not None and sp["leben"][v[2]] < vor["leben"][v[2]])
            danach = u.get(v[1] + 1)
            if not verlor and danach is not None and vor is not None and danach["leben"][v[2]] < vor["leben"][v[2]]:
                verlor = True  # der Rahmen zeigt die Einheiten noch im Takt davor (Aufnahme, wie Rahmen 7809319)
                abpraller["Verlust erst einen Rahmen spaeter sichtbar (Aufnahme)"] += 1
            opfer["anvisiertes Ziel" if v[2] == z["ziel"] else ("Tier" if vor["bes"][v[2]] == 0 else ("Freund" if vor["bes"][v[2]] == z["bes"] else "anderer Feind"))] += 1
            opfer["%s, Opfer-Art %d, Geschoss %d, Spieler %d" % ("vom Nachbarfeld" if v[6] else "auf dem Feld", int(vor["typ"][v[2]]), art, z["bes"])] += 1
        ok = all(gleich) and verlor is not False
        erg[(art, ("richtig, Ende an Gebaeude oder Wasser" if v[0] == "besonders" else "richtig") if ok else "FALSCH")] += 1
        if not ok:
            fehl.append((sch, art, "Modell", v, "Spiel", sp_art, ende[0], ende[1]["mx"], ende[1]["my"], ende[1]["h"], ende[1]["da"], ende[1]["boden"], "ziel", z["ziel"]))
    return {"datei": os.path.basename(pfad), "fluege": len(fl), "takte": len(u), "anfang": wk, "bahn_gleich": gut, "bahn_abw": abw, "bahn_erste": erste, "abpraller": abpraller, "orient": orient, "ende": erg, "fehl": fehl, "opfer": opfer}


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
    ori = collections.Counter()
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
        ori.update(e["orient"])
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
    aus.append("SUMME Richtungen der Abpraller: " + str(sorted(ori.items())))
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
