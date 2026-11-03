# -*- coding: utf-8 -*-
"""B-142 Lauf S: Regel-Pruefer. Liest die Aufzeichnung einer Szene und ihren Plan, prueft die Regel an jedem Paar und gibt nur Fallzahlen und Abweichungen aus. Plan: docs/plans/Plan_Lauf_S.md.

  python -m selfaware.tools.analysis.auge_regeln <aufzeichnung.auge>

Ergebnis: <aufzeichnung>.regeln.json, je Paar und Richtung. Die Tabellen kommen aus dem Datenblock derselben Aufzeichnung, damit UCP zaehlt.
"""
import argparse
import collections
import json
import sys

import numpy as np

PLAETZE = 2500
FELDER = {"da": ("logicalState", "<i2"), "typ": ("unitType", "<i2"), "leben": ("health", "<i4"), "schlaegt": ("attackedUnitID", "<i2"), "mx": ("microXPosition", "<i2"), "my": ("microYPosition", "<i2")}
GESCHOSS_ART = {22: "pfeil", 70: "pfeil", 74: "pfeil", 23: "bolzen"}  # Schleuderer und Feuerwerfer: Ihr Schaden ist laut Handbuch 17.10. nicht die Tabelle, dort wird nur gemessen


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


def nahkampf_werten(reihen, einheiten, tab):
    """Regel: Das Opfer verliert je Treffer genau den Tabellenwert Schlaeger gegen Opfer. Laeuft auf Stufe 40, jeder Takt ist da. Wer nicht schlagen kann, darf auch nicht treffen."""
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
            aus.append({"paar": i, "schlaeger": w["typ"], "opfer": o["typ"], "soll": soll, "treffer": len(tr), "werte": dict(werte), "abstaende": dict(abst), "erster": tr[0]["takt"] - t0 if tr else None, "fremde_geschosse": len(fremd), "urteil": urteil})
    return aus


def beschuss_werten(reihen, einheiten, tab):
    """Regel: Der Verlust je Treffer ist der Tabellenwert der Geschossart gegen das Ziel. Schleuderer und Feuerwerfer: nur gemessen. Die Treffer vom Ziel auf den Schuetzen zaehlen hier nicht."""
    aus = []
    t0 = reihen[0][0] if reihen else 0
    for i, p in sorted(_paare(einheiten).items()):
        w, o = p["a"], p["b"]
        tr = treffer_lesen(reihen, w, o)
        art = GESCHOSS_ART.get(w["typ"])
        soll = int(tab[art][o["typ"]]) if art else None
        werte = collections.Counter(x["betrag"] for x in tr if not x["rest"])
        abst = collections.Counter(b["takt"] - a["takt"] for a, b in zip(tr, tr[1:]))
        if not tr:
            urteil = "kein Treffer"
        elif soll is None:
            urteil = "gemessen"
        else:
            urteil = "bestaetigt" if set(werte) <= {soll} and all(x["betrag"] <= soll for x in tr if x["rest"]) else "weicht ab"
        aus.append({"paar": i, "schuetze": w["typ"], "ziel": o["typ"], "soll": soll, "treffer": len(tr), "werte": dict(werte), "abstaende": dict(abst), "erster": tr[0]["takt"] - t0 if tr else None, "urteil": urteil})
    return aus


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
        if r.get("urteil") in ("weicht ab", "kein Treffer", "Treffer ohne Nahkampf"):
            text.append("  " + json.dumps({k: v for k, v in r.items() if k != "paar"}, ensure_ascii=False))
    return "\n".join(text)


def main(argv=None):
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("aufzeichnung")
    a = p.parse_args(argv)
    plan = json.load(open(a.aufzeichnung + ".plan.json", encoding="utf-8"))
    reihen, tab = reihen_lesen(a.aufzeichnung, Feldkarte.laden(feldliste=FELDLISTE))
    if plan["szene"] == "nahkampf":
        zeilen = nahkampf_werten(reihen, plan["einheiten"], tab)
    elif plan["szene"] == "beschuss":
        zeilen = beschuss_werten(reihen, plan["einheiten"], tab)
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
