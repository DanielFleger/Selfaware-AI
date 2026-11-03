# -*- coding: utf-8 -*-
"""B-142 Lauf S: Regel-Pruefer. Liest die Aufzeichnung einer Szene und ihren Plan, prueft die Regel an jedem Paar und gibt nur Fallzahlen und Abweichungen aus. Plan: docs/plans/Plan_Lauf_S.md.

  python -m selfaware.tools.analysis.auge_regeln <aufzeichnung.auge>
  python -m selfaware.tools.analysis.auge_regeln --vergleich <editor.regeln.json> <gefecht.regeln.json>

Ergebnis: <aufzeichnung>.regeln.json, je Paar und Richtung. Die Tabellen kommen aus dem Datenblock derselben Aufzeichnung, damit UCP zaehlt.
"""
import argparse
import collections
import json
import sys

import numpy as np

PLAETZE = 2500
FEUER_SONST, FEUER = 37.5, {55: 12.5, 76: 5.0}  # je Flamme und Takt, gemessen Lauf S 03.11. (Szene Beschuss)
FELDER = {"da": ("logicalState", "<i2"), "typ": ("unitType", "<i2"), "leben": ("health", "<i4"), "schlaegt": ("attackedUnitID", "<i2"), "mx": ("microXPosition", "<i2"), "my": ("microYPosition", "<i2"), "besitzer": ("owner", "<i2"), "mann": ("digTileX__OR__countCurrentlyManningEnginers__OR__forCowsRandomBelow300", "<i2")}
STEIN = {39: 20, 40: 60, 41: 5}  # Schaden je Stein am Gebaeude, processEntityHitBuildingOrUnit Zeile 480 bis 488


def tabellen_aus(block, basis, karte):
    def t(feld, n=80):
        return np.frombuffer(block, dtype="<i4", offset=karte.adresse("DAT_UnitPropertiesDefinedData", feld)[0] - basis, count=n).copy()

    return {"nah": t("DAT_MELEE_DAMAGE", 6400).reshape(80, 80), "pfeil": t("DAT_ARROW_DAMAGE"), "bolzen": t("DAT_BOLT_DAMAGE"), "stein": t("DAT_STONE_DAMAGE"), "schlaegt": t("DAT_UNIT_CAN_MELEE"), "tempo": t("DAT_UNIT_MOVEMENT_SPEED_ARRAY"), "leben": t("DAT_BASE_HP")}


def reihen_lesen(pfad, karte):
    """(Takt, {Feld: Werte aller Plaetze}) je rein gelesenem Rahmen, dazu die Tabellen."""
    from selfaware.tools.analysis.auge_auswertung import Aufzeichnung

    auf = Aufzeichnung(pfad)
    iu, id_ = auf.namen.index("DAT_UnitsState"), auf.namen.index("datenblock")
    bu, bd = auf.bereiche[iu][1], auf.bereiche[id_][1]
    schritt = karte.adresse("DAT_UnitsState", "units[].logicalState")[2]
    o = {k: karte.adresse("DAT_UnitsState", "units[]." + f)[0] - bu for k, (f, _) in FELDER.items()}
    tabellen, reihen = None, []
    for r, p, _ in auf.staende():
        if r.bereich == id_ and tabellen is None:
            tabellen = tabellen_aus(bytes(p), bd, karte)
        if r.bereich != iu or not r.rein:
            continue
        a = bytes(p)
        reihen.append((r.takt, {k: np.ndarray(shape=(PLAETZE,), dtype=FELDER[k][1], buffer=a, offset=o[k], strides=(schritt,)).copy() for k in FELDER}))
    return reihen, tabellen


GESCHOSSE = {1: "pfeil", 2: "katapult", 3: "trebuchet", 4: "mangonel", 7: "bolzen", 20: "ballista", 23: "kuh", 33: "schleuder", 34: "feuer", 36: "feuer_frei", 37: "feuerballiste"}  # EntityType, Ghidra-Typen
G_FELDER = {"da": "logicalState", "art": "entityType", "ziel": "unitID", "schuetze": "unitID_OR_seaGullID", "besitzer": "owner", "uid": "uid", "zx": "targetX", "zy": "targetY", "mx": "microX", "my": "microY"}


def geschosse_lesen(pfad, karte):
    """Jedes Geschoss einmal: Art, Besitzer, Schuetze, Ziel, erster und letzter Flugtakt, Start und Zielpunkt in Mikro. Fliegt heisst logicalState 2, danach 3 oder beim Feuer 7. Auf Tempo 40 auf den Takt genau, sonst auf den Abstand der Rahmen."""
    from selfaware.tools.analysis.auge_auswertung import Aufzeichnung

    auf = Aufzeichnung(pfad)
    ie = auf.namen.index("DAT_EntityState")
    be = auf.bereiche[ie][1]
    ad = {k: karte.adresse("DAT_EntityState", "entityArray[]." + f) for k, f in G_FELDER.items()}
    arten = list(GESCHOSSE)
    aus = {}
    letzter = None
    for r, p, _ in auf.staende():
        if r.bereich != ie or not r.rein:
            continue
        a = bytes(p)
        sp = {k: np.ndarray(shape=(v[3],), dtype={2: "<i2", 4: "<i4"}[v[1]], buffer=a, offset=v[0] - be, strides=(v[2],)) for k, v in ad.items()}
        for i in np.nonzero(np.isin(sp["art"], arten) & (sp["da"] != 0))[0]:
            sch = (int(i), int(sp["uid"][i]))
            g = aus.get(sch)
            if g is None:
                g = aus[sch] = {"art": GESCHOSSE[int(sp["art"][i])], "besitzer": int(sp["besitzer"][i]), "schuetze": int(sp["schuetze"][i]), "ziel": int(sp["ziel"][i]), "von": r.takt, "bis": None, "start": (int(sp["mx"][i]), int(sp["my"][i])), "punkt": (int(sp["zx"][i]), int(sp["zy"][i]))}
            g["zuletzt"] = r.takt
            if sp["da"][i] != 2 and g["bis"] is None:
                g["bis"] = r.takt
        letzter = r.takt
    for g in aus.values():
        if g["bis"] is None and g["zuletzt"] < letzter:  # zwischen zwei Rahmen gelandet, auf Tempo 200 fehlen viele Takte
            g["bis"] = g["zuletzt"]
    return list(aus.values())


def geschosse_werten(geschosse, reihen):
    """Je Art: Wie viele flogen, wie viele trafen, wie schnell. Getroffen heisst: Das Ziel hatte rund um den Einschlag weniger Leben als davor. Fremde Treffer in diesen Rahmen zaehlen mit, das ist die Grenze dieser Zahl."""
    takte = [t for t, _ in reihen]
    stand = dict(reihen)
    zeilen = collections.defaultdict(lambda: {"flogen": 0, "gelandet": 0, "traf": 0, "verfehlt": 0, "ziel_weg": 0, "mikro_je_takt": [], "abstand": []})
    for g in geschosse:
        z = zeilen[g["art"]]
        z["flogen"] += 1
        if g["bis"] is None:
            continue
        z["gelandet"] += 1
        d = _abstand(*g["start"], *g["punkt"])
        if g["bis"] > g["von"] and d:
            z["mikro_je_takt"].append(d / (g["bis"] - g["von"]))
        z["abstand"].append(d)
        i = np.searchsorted(takte, g["bis"])
        if i == 0 or i >= len(takte) or g["ziel"] <= 0:
            continue
        vor, nach = stand[takte[max(0, i - 3)]], stand[takte[min(len(takte) - 1, i + 1)]]  # der Verlust kam bis zu 2 Takte vor dem Ende des Flugs (Szene Beschuss)
        if not nach["da"][g["ziel"]] or nach["typ"][g["ziel"]] != vor["typ"][g["ziel"]]:
            z["ziel_weg"] += 1
        elif nach["leben"][g["ziel"]] < vor["leben"][g["ziel"]]:
            z["traf"] += 1
        else:
            z["verfehlt"] += 1
    aus = {}
    for art, z in sorted(zeilen.items()):
        tempo, ab = z.pop("mikro_je_takt"), z.pop("abstand")
        aus[art] = {**z, "mikro_je_takt": round(float(np.median(tempo)), 2) if tempo else None, "abstand_hoechstens": max(ab) if ab else None}
    return aus


def _abstand(ax, ay, bx, by):
    """In Mikro, 8 je Feld, nach der Formel des Spiels."""
    a, b = abs(ax - bx), abs(ay - by)
    g, k = max(a, b), min(a, b)
    return g + (2 * k // 5) * k // g if g else 0


def gebaeude_lesen(pfad, karte):
    """(Takt, Leben aller Gebaeude, hoechstes Leben, Zustand) je rein gelesenem Rahmen."""
    from selfaware.tools.analysis.auge_auswertung import Aufzeichnung

    auf = Aufzeichnung(pfad)
    ib = auf.namen.index("DAT_BuildingsState")
    bb = auf.bereiche[ib][1]
    ad = {k: karte.adresse("DAT_BuildingsState", "buildings[]." + f) for k, f in (("leben", "currentHealth"), ("hoechst", "maxHealth"), ("da", "logicalState"))}
    aus = []
    for r, p, _ in auf.staende():
        if r.bereich != ib or not r.rein:
            continue
        a = bytes(p)
        aus.append((r.takt, {k: np.ndarray(shape=(v[3],), dtype="<i2", buffer=a, offset=v[0] - bb, strides=(v[2],)).copy() for k, v in ad.items()}))
    return aus


def _gebaeude_verlauf(reihen_g, nr):
    """Leben am Anfang, Verluste (Betrag je Rahmenabstand), erster Verlust, Takt bis weg."""
    verluste, vor, erster, weg = [], None, None, None
    start = None
    for t, s in reihen_g:
        lz = int(s["leben"][nr])
        start = lz if start is None else start
        if vor is not None and lz < vor:
            verluste.append(vor - lz)
            erster = t if erster is None else erster
        if vor is not None and not s["da"][nr]:
            weg = t
            break
        vor = lz
    return {"leben": start, "hoechst": int(reihen_g[0][1]["hoechst"][nr]) if reihen_g else None, "verluste": verluste, "erster_verlust": erster, "weg": weg}


def besatzung_werten(reihen, geschosse, einheiten):
    """Volle Besatzung handelt, ein Mann zu wenig nicht. Handeln heisst: Es fliegt mindestens ein Geschoss, beim Fahren: mindestens 2 Felder Weg. Dazu Tempo, Schusstakt, Flugtempo."""
    aus = []
    ziele = {e["fall"]: e for e in einheiten if e.get("rolle") == "ziel"}
    for e in einheiten:
        if e.get("rolle") != "geraet":
            continue
        start, erster, letzter, ort, besetzt = None, None, None, None, 0
        for t, s in reihen:
            if s["typ"][e["nr"]] != e["typ"] or not s["da"][e["nr"]]:
                break
            ort = (int(s["mx"][e["nr"]]), int(s["my"][e["nr"]]))
            besetzt = max(besetzt, int(s["mann"][e["nr"]]))
            start = start or ort
            if ort != start and erster is None:
                erster = t
            if ort != start:
                letzter = t
        felder = _abstand(*start, *ort) / 8 if start and ort else 0
        schuesse = sorted(g["von"] for g in geschosse if g["schuetze"] == e["nr"])
        takt = collections.Counter(b - a for a, b in zip(schuesse, schuesse[1:]))
        handelt = len(schuesse) > 0 if e["art"] == "schiessen" else felder >= 2
        soll = e["mann"] >= e["soll"]
        zeile = {"typ": e["typ"], "art": e["art"], "soll_mann": e["soll"], "mann": e["mann"], "besetzt": besetzt, "schuesse": len(schuesse), "schusstakt": takt.most_common(1)[0][0] if takt else None, "felder": round(felder, 1), "takte_je_feld": round((letzter - erster) / felder, 2) if erster is not None and letzter > erster and felder >= 2 else None, "handelt": handelt, "urteil": "bestaetigt" if handelt == soll else "weicht ab"}
        if e["fall"] in ziele:
            lz = [int(s["leben"][ziele[e["fall"]]["nr"]]) for _, s in reihen]
            zeile["ziel_verlor"] = lz[0] - lz[-1] if lz else None
        aus.append(zeile)
    return aus


def belagerung_werten(reihen_g, geschosse, einheiten, gebaeude):
    """Je Geraet und Ziel: Verluste am Gebaeude gegen den festen Wert je Stein. Mehrere Steine im selben Rahmenabstand sind ein Vielfaches. Ohne bekannte Regel (Ballista, Feuerballiste, Ramme) wird gemessen und nicht geurteilt."""
    aus = []
    geraete = {e["fall"]: e for e in einheiten if e.get("rolle") == "geraet"}
    for z in gebaeude:
        if "nr" not in z or z["fall"] not in geraete:
            continue
        g = geraete[z["fall"]]
        v = _gebaeude_verlauf(reihen_g, z["nr"])
        wert = STEIN.get(g["typ"])
        steine = sum(1 for x in geschosse if x["schuetze"] == g["nr"])
        urteil = "gemessen" if wert is None or not v["verluste"] else ("bestaetigt" if all(d % wert == 0 for d in v["verluste"]) else "weicht ab")
        aus.append({"geraet": g["typ"], "ziel": z["name"], "laufzeit": z.get("laufzeit"), "steine": steine, **{k: v[k] for k in ("leben", "hoechst", "erster_verlust", "weg")}, "verluste": dict(collections.Counter(v["verluste"])), "urteil": urteil})
    return aus


def gebaeude_nah_werten(reihen_g, reihen, einheiten, gebaeude):
    """Schlaegt der Nahkaempfer das Gebaeude, und was kostet ein Takt? Auf Tempo 40 ist jeder Verlust ein Takt."""
    aus = []
    wer = {e["fall"]: e for e in einheiten if e.get("rolle") == "angreifer"}
    for z in gebaeude:
        if "nr" not in z or z["fall"] not in wer:
            continue
        e = wer[z["fall"]]
        v = _gebaeude_verlauf(reihen_g, z["nr"])
        abst = collections.Counter(b - a for a, b in zip(*[[t for t, _ in reihen_g][:0]] * 2))
        aus.append({"wer": e["typ"], "ziel": z["name"], **{k: v[k] for k in ("leben", "hoechst", "erster_verlust", "weg")}, "verluste": dict(collections.Counter(v["verluste"])), "urteil": "schlaegt" if v["verluste"] else "kein Treffer"})
    return aus


def _paare(einheiten):
    p = collections.defaultdict(dict)
    for e in einheiten:
        if "paar" in e:
            p[e["paar"]][e["rolle"]] = e
    return p


def treffer_lesen(reihen, wer, opfer):
    """Takte und Betraege der Lebensverluste des Opfers, bis einer der beiden tot oder der Platz neu belegt ist. Mit: ob der Partner das Opfer als Ziel eingetragen hatte."""
    aus, vor = [], None
    for t, s in reihen:
        lo, lw = int(s["leben"][opfer["nr"]]), int(s["leben"][wer["nr"]])
        if s["typ"][opfer["nr"]] != opfer["typ"] or s["typ"][wer["nr"]] != wer["typ"] or not s["da"][opfer["nr"]] or not s["da"][wer["nr"]]:
            break
        if vor is not None and lo < vor:
            aus.append({"takt": t, "betrag": vor - lo, "partner": int(s["schlaegt"][wer["nr"]]) == opfer["nr"], "rest": lo <= 0})  # der letzte Treffer nimmt nur, was noch da ist
        vor = lo
        if lo <= 0 or lw <= 0:
            break
    return aus


def nahkampf_werten(reihen, einheiten, tab, erster_rahmen_alt=False):
    """Regel: Das Opfer verliert je Treffer genau den Tabellenwert Schlaeger gegen Opfer. Laeuft auf Stufe 40, jeder Takt ist da. Wer nicht schlagen kann, darf auch nicht treffen.
    erster_rahmen_alt: Im Gefecht zeigt der erste Rahmen nach dem Weiterlaufen noch den Stand davor (gefecht_gegen_editor.txt), der zweite traegt dann zwei Takte. Ein doppelter Wert genau dort ist also kein Fund, gezaehlt wird er trotzdem."""
    aus = []
    t0 = reihen[0][0] if reihen else 0
    for i, p in sorted(_paare(einheiten).items()):
        for w, o in ((p["a"], p["b"]), (p["b"], p["a"])):
            if w["typ"] == o["typ"] and w["rolle"] == "b":
                continue  # gleiche Art: eine Zeile der Liste, die andere Richtung ist die Gegenprobe im Lauf nicht wert
            tr = treffer_lesen(reihen, w, o)
            soll = int(tab["nah"][w["typ"], o["typ"]])
            kann = bool(tab["schlaegt"][w["typ"]])
            geschoss = {int(tab[n][o["typ"]]) for n in ("pfeil", "bolzen", "stein")}
            doppelt = bool(erster_rahmen_alt and tr and tr[0]["takt"] - t0 == 2 and tr[0]["betrag"] == 2 * soll)
            if doppelt:
                tr[0] = dict(tr[0], betrag=soll)
            ganz = [x for x in tr if not x["rest"]]
            fremd = [x for x in ganz if x["betrag"] - soll in geschoss]  # im selben Takt traf noch ein Geschoss von anderswo, wie in Lauf K
            werte = collections.Counter(x["betrag"] for x in ganz if x not in fremd)
            abst = collections.Counter(b["takt"] - a["takt"] for a, b in zip(tr, tr[1:]))
            if not tr:
                urteil = "schlaegt nicht, wie die Tabelle sagt" if not kann else "kein Treffer"
            elif set(werte) <= {soll} and all(x["betrag"] <= soll for x in tr if x["rest"]):
                urteil = "bestaetigt"
            elif not any(x["partner"] for x in tr):
                urteil = "Treffer ohne Nahkampf"
            else:
                urteil = "weicht ab"
            aus.append({"paar": i, "schlaeger": w["typ"], "opfer": o["typ"], "soll": soll, "treffer": len(tr), "werte": dict(werte), "abstaende": dict(abst), "erster": tr[0]["takt"] - t0 if tr else None, "fremde_geschosse": len(fremd), "erster_doppelt": doppelt, "urteil": urteil})
    return aus


def beschuss_werten(reihen, einheiten, tab):
    """Regel: Jeder Verlust eines Beschossenen ist eine Summe aus den Geschosswerten seiner Art (Pfeil, Bolzen, Stein) und dem Feuer. Schuetzen schiessen nicht nur auf den naechsten Feind (Lauf S 03.11.), darum wird nach dem Opfer gewertet, nicht nach dem Paar.
    Feuer steht in keiner bekannten Tabelle, FEUER ist gemessen: Betraege 37, 75, 112 je Takt, Lord 12, Feuerwerfer 5 und 10."""
    aus = {}
    for e in einheiten:
        if e.get("rolle") == "kontrolle":
            continue
        z = aus.setdefault(e["typ"], {"ziel": e["typ"], "pfeil": int(tab["pfeil"][e["typ"]]), "bolzen": int(tab["bolzen"][e["typ"]]), "stein": int(tab["stein"][e["typ"]]), "gesehen": collections.Counter(), "feuer": 0, "ungeklaert": collections.Counter()})
        arten = {"pfeil": z["pfeil"], "bolzen": z["bolzen"], "stein": z["stein"]}
        vor = None
        for _, s in reihen:
            if s["typ"][e["nr"]] != e["typ"] or not s["da"][e["nr"]]:
                break
            lo = int(s["leben"][e["nr"]])
            if vor is not None and lo < vor:
                d = vor - lo
                einzel = [n for n, w in arten.items() if w == d]
                if einzel:
                    z["gesehen"][einzel[0]] += 1
                elif lo <= 0:
                    pass  # der letzte Treffer nimmt nur, was noch da ist
                else:
                    flammen = _erklaert(d, arten, FEUER.get(e["typ"], FEUER_SONST))
                    if flammen is None:
                        z["ungeklaert"][d] += 1
                    elif flammen:
                        z["feuer"] += 1
                    else:
                        z["gesehen"]["mehrere"] += 1
            vor = lo
            if lo <= 0:
                break
    zeilen = []
    for typ, z in sorted(aus.items()):
        fehlt = [n for n in ("pfeil", "bolzen", "stein") if not z["gesehen"][n]]
        zeilen.append({**z, "gesehen": dict(z["gesehen"]), "ungeklaert": dict(z["ungeklaert"]), "nicht_gesehen": fehlt, "urteil": "weicht ab" if z["ungeklaert"] else "bestaetigt"})
    return zeilen


def _erklaert(d, arten, feuer):
    """Mehrere Geschosse im selben Takt, bis zu 3 je Art, dazu bis zu 3 Flammen. Eine Flamme zaehlt abgerundet. Rueckgabe: Zahl der Flammen, None, wenn nichts passt."""
    w = list(arten.values())
    for f in range(4):
        for a in range(4):
            for b in range(4):
                for c in range(4):
                    if a * w[0] + b * w[1] + c * w[2] + int(f * feuer) == d:
                        return f
    return None


def laufen_werten(reihen, einheiten, felder):
    """Takte je Feld, gemessen vom ersten Feldwechsel bis zum Ziel, das sind felder - 1 Felder: So zaehlt die Zeit bis zum ersten Schritt nicht mit. Tempo-Wert der Tabelle steht daneben; was er in Takten heisst, sagt erst diese Messung."""
    aus = []
    for e in einheiten:
        erster = am_ziel = None
        for t, s in reihen:
            x, y = int(s["mx"][e["nr"]]) // 8, int(s["my"][e["nr"]]) // 8
            if erster is None and (x, y) != (e["x"], e["y"]):
                erster = t
            if (x, y) == tuple(e["ziel"]):
                am_ziel = t
                break
        aus.append({"typ": e["typ"], "lage": e["rolle"], "erster_schritt": erster, "am_ziel": am_ziel, "takte_je_feld": round((am_ziel - erster) / (felder - 1), 2) if erster is not None and am_ziel is not None else None})
    return aus


def masse_werten(reihen, tab, seiten=(1, 2)):
    """Ueberlebende je Takt und Plaetze im Einheitenfeld (Liste V5). Dazu die Regel fuer viele Angreifer: Der Verlust des Opfers ist je Takt die Summe der Tabellenwerte aller, die es als Ziel eingetragen haben. Gewertet wird nur, wo zwischen zwei Rahmen dieselben Angreifer dieselben blieben und das Opfer lebt, sonst ist die Summe nicht bekannt."""
    verlauf, fall = [], collections.Counter()
    vor = None
    for t, s in reihen:
        da = s["da"] != 0
        da[0] = False  # Platz 0 ist ein Merkplatz (Lauf K), er zaehlte hier als Einheit
        verlauf.append((int(t), *[int((da & (s["besitzer"] == p)).sum()) for p in seiten], int(da.sum())))
        if vor is not None:
            fall.update(_summen_pruefen(vor[1], s, tab, t - vor[0]))
        vor = (t, s)
    if not verlauf:
        return {"rahmen": 0}
    gefallen = next((v[0] for v in verlauf if v[1] + v[2] < verlauf[0][1] + verlauf[0][2]), None)
    return {"rahmen": len(verlauf), "start": verlauf[0][1:], "ende": verlauf[-1][1:], "takte": verlauf[-1][0] - verlauf[0][0], "erster_tod_nach": gefallen - verlauf[0][0] if gefallen is not None else None,
            "plaetze_hoechstens": max(v[3] for v in verlauf), "summe": dict(fall), "verlauf": verlauf[::max(1, len(verlauf) // 40)]}


def _summen_pruefen(a, b, tab, dt):
    """Zwischen zwei Rahmen: gleich, wenn der Verlust genau dt mal die Summe ist; zu wenig, wenn Angreifer zwischendurch nicht schlugen; mehr heisst, die Regel haelt nicht."""
    gleich = (a["da"] != 0) & (b["da"] != 0) & (a["typ"] == b["typ"])
    gleich[0] = False
    fest = gleich & (a["schlaegt"] == b["schlaegt"]) & (a["schlaegt"] > 0)
    ziel = a["schlaegt"][fest].astype(np.int64)
    if not len(ziel):
        return {}
    summe = np.zeros(PLAETZE, dtype=np.int64)
    np.add.at(summe, ziel, tab["nah"][a["typ"][fest], a["typ"][ziel]])
    alle_a, alle_b, nur_fest = (np.bincount(x, minlength=PLAETZE) for x in (a["schlaegt"][np.maximum(a["schlaegt"], 0) > 0], b["schlaegt"][np.maximum(b["schlaegt"], 0) > 0], ziel))
    pruef = np.nonzero((summe > 0) & gleich & (alle_a == nur_fest) & (alle_b == nur_fest) & (b["leben"] > 0))[0]
    verlust = a["leben"][pruef] - b["leben"][pruef]
    soll = summe[pruef] * dt
    return {"gleich": int((verlust == soll).sum()), "weniger": int((verlust < soll).sum()), "mehr": int((verlust > soll).sum())}


def reichweite_werten(reihen, einheiten, tab):
    """Je Bahn: Wann laeuft die Einheit los, wie schnell, in welchem Abstand bleibt sie vor dem ersten Treffer stehen, wie oft und in welchem Takt faellt das Leben des Ziels."""
    ziele = {e["paar"]: e for e in einheiten if e.get("rolle") == "ziel"}
    aus = []
    for e in einheiten:
        if e.get("rolle") != "laeufer":
            continue
        z = ziele[e["paar"]]
        start = letzter_ort = erster = letzter = vor = halt_ort = None
        treffer = []
        ziel_ort = None
        for t, s in reihen:
            if s["typ"][e["nr"]] != e["typ"] or not s["da"][e["nr"]] or s["typ"][z["nr"]] != z["typ"]:
                break
            ort = (int(s["mx"][e["nr"]]), int(s["my"][e["nr"]]))
            ziel_ort = ziel_ort or (int(s["mx"][z["nr"]]), int(s["my"][z["nr"]]))
            start = start or ort
            if not treffer and ort != (letzter_ort or start):
                erster = erster if erster is not None else t
                letzter, halt_ort = t, ort
            letzter_ort = ort
            lz = int(s["leben"][z["nr"]])
            if vor is not None and lz < vor:
                treffer.append((t, vor - lz))
            vor = lz
        halt_ort = halt_ort or start
        ab = _abstand(*halt_ort, *ziel_ort) if ziel_ort and halt_ort else None
        gelaufen = (_abstand(*start, *ziel_ort) - ab) / 8 if ab is not None else 0
        schuss = collections.Counter(b[0] - a[0] for a, b in zip(treffer, treffer[1:]))
        aus.append({"typ": e["typ"], "erster_schritt": erster, "halt": letzter, "felder_gelaufen": round(gelaufen, 1), "takte_je_feld": round((letzter - erster) / gelaufen, 2) if erster is not None and gelaufen >= 5 and letzter > erster else None,
                    "tempo_soll": 8 * (int(tab["tempo"][e["typ"]]) + 1), "abstand_mikro": ab, "abstand_felder": round(ab / 8, 1) if ab is not None else None, "treffer": len(treffer), "erster_treffer": treffer[0][0] if treffer else None,
                    "werte": dict(collections.Counter(w for _, w in treffer)), "abstaende": dict(schuss.most_common(5)), "urteil": "trifft" if treffer else "kein Treffer"})
    return aus


def schussweite_werten(geschosse, einheiten):
    """Je Fall: Fliegen Geschosse auf das befohlene Ziel? Der Abstand ist der echte, vom Start des Geschosses zum Zielpunkt. Je Art am Ende: weitester Fall mit Schuss, naechster ohne."""
    ziele = {e["paar"]: e for e in einheiten if e.get("rolle") == "ziel"}
    aus = []
    for e in einheiten:
        if e.get("rolle") != "laeufer":
            continue
        z = ziele[e["paar"]]
        g = [x for x in geschosse if x["schuetze"] == e["nr"]]
        auf = [x for x in g if x["ziel"] == z["nr"]]
        aus.append({"typ": e["typ"], "abstand": e["abstand"], "auf_ziel": len(auf), "andere": len(g) - len(auf), "abstand_mikro": max((_abstand(*x["start"], *x["punkt"]) for x in auf), default=None), "urteil": "schiesst" if auf else "kein Treffer"})
    return aus


def schussweite_grenzen(zeilen):
    """Je Art der groesste Abstand mit Schuss und der kleinste ohne. Liegt ein Schuss jenseits eines Falls ohne Schuss, sagt die Leiter nichts Eindeutiges."""
    aus = {}
    for typ in sorted({z["typ"] for z in zeilen}):
        mit = [z["abstand"] for z in zeilen if z["typ"] == typ and z["auf_ziel"]]
        ohne = [z["abstand"] for z in zeilen if z["typ"] == typ and not z["auf_ziel"]]
        aus[typ] = {"weitester_schuss": max(mit, default=None), "naechster_ohne": min(ohne, default=None), "eindeutig": not mit or not ohne or max(mit) < min(ohne)}
    return aus


def laufziel_werten(geschosse, reihen, einheiten):
    """Geschosse der Schuetzen auf ihren Laeufer, je Art. Die Liste fragt nach der Trefferquote gegen ein laufendes Ziel."""
    schuetzen = {e["nr"]: e for e in einheiten if e.get("rolle") == "schuetze"}
    partner = {e["paar"]: e["nr"] for e in einheiten if e.get("rolle") == "pendel"}
    aus = []
    for nr, e in schuetzen.items():
        g = [x for x in geschosse if x["schuetze"] == nr and x["ziel"] == partner[e["paar"]]]
        w = geschosse_werten(g, reihen)
        aus.append({"typ": e["typ"], "alle_geschosse": sum(1 for x in geschosse if x["schuetze"] == nr), **_vorhalt(g, reihen, partner[e["paar"]]), **{k: v for k, v in w.items()}})
    return aus


def _vorhalt(geschosse, reihen, ziel):
    """Zielt das Geschoss auf den Ort beim Abschuss oder auf den beim Einschlag? Abstand des Zielpunkts zum Laeufer, je Mikro, Median. Der Laeufer laeuft 1 Feld in 12 bis 16 Takten."""
    stand = dict(reihen)
    takte = sorted(stand)
    abschuss, einschlag = [], []
    for g in geschosse:
        if g["bis"] is None:
            continue
        for t, liste in ((g["von"], abschuss), (g["bis"], einschlag)):
            s = stand[takte[min(int(np.searchsorted(takte, t)), len(takte) - 1)]]
            liste.append(_abstand(*g["punkt"], int(s["mx"][ziel]), int(s["my"][ziel])))
    return {"punkt_zum_laeufer_abschuss": int(np.median(abschuss)) if abschuss else None, "punkt_zum_laeufer_einschlag": int(np.median(einschlag)) if einschlag else None}


def haltung_werten(reihen, einheiten):
    """Reagiert heisst: Die Wache verlaesst ihr Feld oder traegt einen Gegner als Ziel ein. Soll aus dem Code: aggressiv bis 25 Felder, defensiv bis 5, stehen gar nicht."""
    aus = []
    for e in einheiten:
        if e.get("rolle") != "wache":
            continue
        erste = None
        for t, s in reihen:
            if (int(s["mx"][e["nr"]]) // 8, int(s["my"][e["nr"]]) // 8) != (e["x"], e["y"]) or s["schlaegt"][e["nr"]] != 0:
                erste = t
                break
        soll = {2: 25, 1: 5, 0: 0}[e["wert"]] >= e["abstand"]
        aus.append({"typ": e["typ"], "haltung": e["haltung"], "abstand": e["abstand"], "soll": soll, "reagiert": erste is not None, "nach_takten": erste - reihen[0][0] if erste is not None else None, "urteil": "bestaetigt" if soll == (erste is not None) else "weicht ab"})
    return aus


def kontrolle_werten(reihen, einheiten):
    """Die Kontrolle steht allein: Leben und Ort bleiben. Sonst stoert etwas, das niemand kennt, und die Szene gilt als gestoert."""
    aus = []
    for e in einheiten:
        if e.get("rolle") != "kontrolle":
            continue
        leben = {int(s["leben"][e["nr"]]) for _, s in reihen}
        orte = {(int(s["mx"][e["nr"]]) // 8, int(s["my"][e["nr"]]) // 8) for _, s in reihen}
        aus.append({"typ": e["typ"], "leben": sorted(leben), "orte": sorted(orte), "ungestoert": len(leben) == 1 and len(orte) == 1})
    return aus


def vergleichen(a, b):
    """Editor gegen Gefecht, Zeile fuer Zeile, nur was in beiden vorkommt. Gleich heisst: dieselben Schadenswerte und dasselbe Urteil, beim Laufen hoechstens 1 Takt je Feld Unterschied."""
    def schluessel(z):
        return tuple(z.get(k) for k in ("schlaeger", "opfer", "ziel", "typ", "lage"))
    zb = {schluessel(z): z for z in b["zeilen"]}
    aus = {"gleich": 0, "anders": [], "nur_erste": 0, "nur_zweite": len(set(zb) - {schluessel(z) for z in a["zeilen"]})}
    for z in a["zeilen"]:
        g = zb.get(schluessel(z))
        if g is None:
            aus["nur_erste"] += 1
        elif _gleich(z, g):
            aus["gleich"] += 1
        else:
            aus["anders"].append({"erste": z, "zweite": g})
    return aus


def _gleich(x, y):
    if "takte_je_feld" in x:
        return x["takte_je_feld"] is not None and y["takte_je_feld"] is not None and abs(x["takte_je_feld"] - y["takte_je_feld"]) <= 1
    if "soll" in x:
        return x["soll"] == y["soll"] and x["urteil"] == y["urteil"] and set(x["werte"]) == set(y["werte"])
    return x["urteil"] == y["urteil"] and (x["pfeil"], x["bolzen"], x["stein"]) == (y["pfeil"], y["bolzen"], y["stein"])


def bericht(szene, zeilen, kontrollen):
    z = collections.Counter(r["urteil"] for r in zeilen if "urteil" in r)
    text = [f"Szene {szene}: {len(zeilen)} Zeilen, {dict(z)}"]
    erste = [r["erster"] for r in zeilen if r.get("erster") is not None]
    if erste:
        abst = collections.Counter()
        for r in zeilen:
            abst.update({int(k): v for k, v in r.get("abstaende", {}).items()})
        text.append(f"Erster Treffer nach Takten: kleinster {min(erste)}, Median {sorted(erste)[len(erste) // 2]}, groesster {max(erste)}. Abstaende zwischen Treffern: {abst.most_common(6)}. Fremde Geschosse: {sum(r.get('fremde_geschosse', 0) for r in zeilen)}")
    if kontrollen:
        text.append("Kontrolle: " + ("ungestoert" if all(k["ungestoert"] for k in kontrollen) else f"GESTOERT {kontrollen}"))
    for r in zeilen:
        if r.get("urteil") in ("weicht ab", "kein Treffer", "Treffer ohne Nahkampf") or szene.startswith(("reichweite", "schussweite", "laufziel", "haltung", "besatzung", "belagerung", "gebaeude_nah")):
            text.append("  " + json.dumps({k: v for k, v in r.items() if k != "paar"}, ensure_ascii=False))
    return "\n".join(text)


def main(argv=None):
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("aufzeichnung", nargs="?")
    p.add_argument("--vergleich", nargs=2)
    a = p.parse_args(argv)
    if a.vergleich:
        v = vergleichen(*[json.load(open(x, encoding="utf-8")) for x in a.vergleich])
        print({k: (len(w) if k == "anders" else w) for k, w in v.items()})
        for z in v["anders"]:
            print("  ", json.dumps(z, ensure_ascii=False)[:400])
        return 0
    plan = json.load(open(a.aufzeichnung + ".plan.json", encoding="utf-8"))
    reihen, tab = reihen_lesen(a.aufzeichnung, Feldkarte.laden(feldliste=FELDLISTE))
    art = plan["szene"].removesuffix("_g").removesuffix("_pfeil").removesuffix("2")
    if art in ("last", "lord") or art.startswith("schlacht"):
        m = masse_werten(reihen, tab)
        json.dump({"szene": plan["szene"], "von": plan["von"], "bis": plan["bis"], **m}, open(a.aufzeichnung + ".regeln.json", "w", encoding="utf-8"), ensure_ascii=False)
        print(plan["szene"], {k: v for k, v in m.items() if k != "verlauf"})
        return 0
    if art == "nahkampf":
        zeilen = nahkampf_werten(reihen, plan["einheiten"], tab, erster_rahmen_alt=plan["szene"].endswith("_g"))
        print("Erster Treffer doppelt, weil der erste Rahmen den alten Stand zeigt:", sum(z["erster_doppelt"] for z in zeilen))
    elif art == "beschuss":
        zeilen = beschuss_werten(reihen, plan["einheiten"], tab)
        g = geschosse_werten(geschosse_lesen(a.aufzeichnung, Feldkarte.laden(feldliste=FELDLISTE)), reihen)
        json.dump(g, open(a.aufzeichnung + ".geschosse.json", "w", encoding="utf-8"), ensure_ascii=False)
        print("Geschosse:", g)
    elif art == "reichweite":
        zeilen = reichweite_werten(reihen, plan["einheiten"], tab)
        g = geschosse_werten(geschosse_lesen(a.aufzeichnung, Feldkarte.laden(feldliste=FELDLISTE)), reihen)
        json.dump(g, open(a.aufzeichnung + ".geschosse.json", "w", encoding="utf-8"), ensure_ascii=False)
        print("Geschosse:", g)
    elif art == "besatzung":
        zeilen = besatzung_werten(reihen, geschosse_lesen(a.aufzeichnung, Feldkarte.laden(feldliste=FELDLISTE)), plan["einheiten"])
        print("Bemannt:", plan.get("bemannt"), "nach", plan.get("bemannt_nach"), "Takten")
    elif art == "belagerung":
        k_ = Feldkarte.laden(feldliste=FELDLISTE)
        zeilen = belagerung_werten(gebaeude_lesen(a.aufzeichnung, k_), geschosse_lesen(a.aufzeichnung, k_), plan["einheiten"], plan["gebaeude"])
        print("Bemannt:", plan.get("bemannt"), "nach", plan.get("bemannt_nach"), "Takten; nicht gesetzt:", plan.get("nicht_gesetzt"), "; nicht gefahren:", plan.get("nicht_gefahren"))
    elif art == "gebaeude_nah":
        k_ = Feldkarte.laden(feldliste=FELDLISTE)
        zeilen = gebaeude_nah_werten(gebaeude_lesen(a.aufzeichnung, k_), reihen, plan["einheiten"], plan["gebaeude"])
        print("Nicht gesetzt:", plan.get("nicht_gesetzt"))
    elif art == "schussweite":
        zeilen = schussweite_werten(geschosse_lesen(a.aufzeichnung, Feldkarte.laden(feldliste=FELDLISTE)), plan["einheiten"])
        print("Grenzen je Art:", schussweite_grenzen(zeilen))
    elif art == "laufziel":
        zeilen = laufziel_werten(geschosse_lesen(a.aufzeichnung, Feldkarte.laden(feldliste=FELDLISTE)), reihen, plan["einheiten"])
    elif art == "haltung":
        zeilen = haltung_werten(reihen, plan["einheiten"])
    else:
        from selfaware.tools.experiments.auge_lauf_s import FELDER_LAUF
        zeilen = laufen_werten(reihen, plan["einheiten"], FELDER_LAUF)
    kontrollen = kontrolle_werten(reihen, plan["einheiten"])
    json.dump({"szene": plan["szene"], "rahmen": len(reihen), "von": plan["von"], "bis": plan["bis"], "zeilen": zeilen, "kontrollen": kontrollen}, open(a.aufzeichnung + ".regeln.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(reihen)} Rahmen in {plan['bis'] - plan['von']} Takten")
    print(bericht(plan["szene"], zeilen, kontrollen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
