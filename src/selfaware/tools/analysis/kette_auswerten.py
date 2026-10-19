# -*- coding: utf-8 -*-
"""Auswertung der Messpartie Eisen/Schmiede/Leder (streitkolben_messen.py teil=kette, Daniel 08.10. 00:18).

Je Mine aus dem Lageprotokoll (jede Runde): Arbeiter = Einheiten mit arbeitsplatz = Minennummer; eine Lieferung = die
Ladung eines Arbeiters faellt von >0 auf 0. Rate = gelieferte Stuecke je 1.000 Ticks ab der ersten Lieferung.
Schmiede/Leder/Kuehe aus den Proben (Vorrat) und dem Status (T51 = Kuh).
Aufruf: uv run python -m selfaware.tools.analysis.kette_auswerten data/research/kette_messung_<zeit>.json
"""
import gzip
import json
import os
import sys
from statistics import median


def tabelle(text, kopfzeile):
    z = text.strip().split("\n")[kopfzeile:]
    k = z[0].split()
    return [dict(zip(k, map(int, l.split()))) for l in z[1:] if l.strip()]


def auswerten(pfad):
    erg = json.load(open(pfad, encoding="utf-8"))
    minen = {b["nr"]: b for b in erg["bauten"] if b["typ"] == 5 and b["nr"]}
    schmieden = {b["nr"]: b for b in erg["bauten"] if b["typ"] == 13 and b["nr"]}
    lager = [b for b in erg["bauten"] if b["typ"] == 10 and b["nr"]]
    je = {n: {"arbeiter_ab": None, "lieferungen": [], "arbeiter": set(), "produktion": 0,
              "erste_produktion": None, "vorrat_start": None, "vorrat_ende": None,
              "traeger_start": None, "traeger_ende": None} for n in minen}
    schmied_je = {n: {"arbeiter": set(), "eisen_aufnahmen": [], "eisen_abgaben": [],
                      "keulen_aufnahmen": [], "keulen_abgaben": []}
                  for n in schmieden}
    traeger_vor, schmied_vor, schmied_zustand_vor, mine_vorrat_vor, t_erst, t_letzt, kuehe = {}, {}, {}, {}, None, None, []
    for zeile in gzip.open(erg["lageprotokoll"], "rt", encoding="utf-8"):
        d = json.loads(zeile)
        t = d["t"]
        t_erst = t if t_erst is None else t_erst
        t_letzt = t
        E = tabelle(d["einheiten"], 1)
        G = {g["nr"]: g for g in tabelle(d["gebaeude"], 0)}
        kuehe.append((t, d["st"].get("T51", 0)))
        for n, m in je.items():
            jetzt = G.get(n, {}).get("vorrat", 0)
            if m["vorrat_start"] is None:
                m["vorrat_start"] = jetzt
            vor = mine_vorrat_vor.get(n, jetzt)
            if jetzt > vor:
                m["produktion"] += jetzt - vor
                m["erste_produktion"] = m["erste_produktion"] or t
            m["vorrat_ende"] = jetzt
            mine_vorrat_vor[n] = jetzt
        traeger_ladung = {n: sum(e.get("ladung", 0) for e in E if e["besitzer"] == 1 and e["typ"] == 32
                                 and e.get("arbeitsplatz") == n) for n in minen}
        for n, m in je.items():
            if m["traeger_start"] is None:
                m["traeger_start"] = traeger_ladung[n]
            m["traeger_ende"] = traeger_ladung[n]
        for e in E:
            ap = e.get("arbeitsplatz")
            if e["besitzer"] != 1:
                continue
            jetzt = e.get("ladung", 0)
            if ap in je and e["typ"] == 32:
                key = (e["nr"], ap)
                vor = traeger_vor.get(key, 0)
                m = je[ap]
                m["arbeiter"].add(e["nr"])
                if m["arbeiter_ab"] is None:
                    m["arbeiter_ab"] = t
                if vor > jetzt:
                    m["lieferungen"].append((t, vor - jetzt))
                traeger_vor[key] = jetzt
            if ap in schmied_je and e["typ"] == 19:
                key = (e["nr"], ap)
                vor = schmied_vor.get(key, 0)
                s = schmied_je[ap]
                s["arbeiter"].add(e["nr"])
                # Schmied-Zustaende im echten Ablauf: 3 = Eisen vom Lager zur Schmiede, 6 = Eisen in die Schmiede
                # gegeben, 7 = fertige Keule(n) aufgenommen, 8 = Abgabe im Waffenlager. Das trennt zwei gleich grosse
                # Ladungen sicherer als ihre Position bei dicht nebeneinander stehenden Gebaeuden.
                if jetzt > vor and e.get("zustand") == 3:
                    s["eisen_aufnahmen"].append((t, jetzt - vor))
                if jetzt > vor and e.get("zustand") == 7:
                    s["keulen_aufnahmen"].append((t, jetzt - vor))
                if vor > jetzt and e.get("zustand") == 6:
                    s["eisen_abgaben"].append((t, vor - jetzt))
                if vor > jetzt and schmied_zustand_vor.get(key) == 8:
                    s["keulen_abgaben"].append((t, vor - jetzt))
                schmied_vor[key] = jetzt
                schmied_zustand_vor[key] = e.get("zustand")
    aus = {"messdauer": [t_erst, t_letzt], "minen": []}
    for n, b in minen.items():
        m = je[n]
        l = m["lieferungen"]
        # Jede Verringerung der Traegerladung ist eine echte Ablieferung; Zweierladungen werden vom Spiel teils in
        # zwei Einzelschritten abgelegt und muessen deshalb beide zaehlen.
        stueck = sum(s for _, s in l)
        lose = []
        for t, menge in l:
            if lose and t - lose[-1][0] <= 100:
                lose[-1] = (t, lose[-1][1] + menge)
            else:
                lose.append((t, menge))
        stationaer = (1000.0 * sum(m for _, m in lose[1:]) / (lose[-1][0] - lose[0][0])) \
                     if len(lose) >= 3 and lose[-1][0] > lose[0][0] else None
        gueltig = len(m["arbeiter"]) == 1 and stationaer is not None
        ab_bau = round(1000.0 * stueck / max(1, t_letzt - b["t"]), 3)
        ab_arbeiter = round(1000.0 * stueck / max(1, t_letzt - (m["arbeiter_ab"] or b["t"])), 3)
        aus["minen"].append({"name": b["name"], "nr": n, "weg_felder": b.get("weg_felder"),
                             "weg_luftlinie": b.get("weg_luftlinie"), "gebaut": b["t"],
                             "arbeiter": len(m["arbeiter"]), "arbeiter_ab": m["arbeiter_ab"],
                             "erste_lieferung": l[0][0] if l else None, "lieferungen": len(l), "stueck": stueck,
                             "produziert": m["produktion"], "rest_mine": m["vorrat_ende"],
                             "rest_traeger": m["traeger_ende"], "je_gang": sorted({s for _, s in l}),
                             "transportlose": lose, "eisen_je_1000_ab_bau": ab_bau,
                             "eisen_je_1000_ab_arbeiter": ab_arbeiter,
                             "eisen_je_1000_stationaer": round(stationaer, 3) if stationaer else None,
                             "gueltig": gueltig,
                             "ungueltig_grund": None if gueltig else "Traeger wechselte oder zu wenige volle Transportzyklen"})
    proben = erg["proben"]
    if proben:
        a, z = proben[0], proben[-1]
        ab = erg.get("waffen_abfluss", {})
        keulen = z["keule"] - a["keule"] + ab.get("keule", 0)
        leder = z["leder"] - a["leder"] + ab.get("leder", 0)
        ticks = max(1, z["t"] - a["t"])
        n_schmieden = max(1, len(schmieden))
        aus["schmiede"] = {"keulen_bestand": [a["keule"], z["keule"]], "keulen_gesamt": keulen,
                            "keulen_je_schmied_1000": round(1000.0 * keulen / ticks / n_schmieden, 3),
                            "eisen_bestand": [a["eisen"], z["eisen"]], "ticks": [a["t"], z["t"]],
                            "schmieden": n_schmieden, "verkauft": ab.get("keule", 0)}
        je_schmied = []
        for n, b in schmieden.items():
            s = schmied_je[n]
            eisen = sum(m for _, m in s["eisen_abgaben"])
            keulen_s = sum(m for _, m in s["keulen_abgaben"])
            eisen_t = [t for t, _ in s["eisen_aufnahmen"]]
            keulen_t = [t for t, _ in s["keulen_aufnahmen"]]
            eisen_zyklus = median([b2 - a2 for a2, b2 in zip(eisen_t, eisen_t[1:])]) if len(eisen_t) >= 2 else None
            los_mittel = (float(sum(m for _, m in s["keulen_aufnahmen"])) / len(s["keulen_aufnahmen"])) \
                         if s["keulen_aufnahmen"] else None
            # Bei Eisenmangel entstehen lange Leerzeiten zwischen fertigen Losen. Die Satt-Rate kombiniert deshalb
            # den gemessenen vollen Rundgang mit der gemessenen Losgroesse (abwechselnd 1/2, im Mittel etwa 1,5).
            keulen_rate = (1000.0 * los_mittel / eisen_zyklus) if eisen_zyklus and los_mittel else None
            je_schmied.append({"nr": n, "name": b["name"], "arbeiter": len(s["arbeiter"]),
                               "gang_felder_plan": next((x.get("gang_felder") for x in erg.get("wegplan", {}).get("schmiede", [])
                                                         if tuple(x.get("ort", ())) == (b["x"], b["y"])), None),
                               "eisen_aufnahmen": len(s["eisen_aufnahmen"]), "eisen_verbraucht": eisen,
                               "eisen_je_1000": round(1000.0 * eisen / ticks, 3),
                               "eisen_zyklus_ticks": eisen_zyklus,
                               "eisen_je_1000_bei_eisen_satt": round(1000.0 / eisen_zyklus, 3) if eisen_zyklus else None,
                               "keulen_je_eisen_losmittel": round(los_mittel, 3) if los_mittel else None,
                               "keulen_abgeliefert": keulen_s, "keulen_je_1000": round(1000.0 * keulen_s / ticks, 3),
                               "keulen_je_1000_bei_eisen_satt": round(keulen_rate, 3) if keulen_rate else None})
        eisen_verbraucht = sum(s["eisen_verbraucht"] for s in je_schmied)
        keulen_abgeliefert = sum(s["keulen_abgeliefert"] for s in je_schmied)
        aus["schmiede"]["je_schmied"] = je_schmied
        aus["schmiede"]["eisen_verbraucht_gesamt"] = eisen_verbraucht
        aus["schmiede"]["keulen_von_arbeitern"] = keulen_abgeliefert
        aus["schmiede"]["keulen_je_eisen"] = round(float(keulen_abgeliefert) / eisen_verbraucht, 3) if eisen_verbraucht else None
        satte_raten = [s["eisen_je_1000_bei_eisen_satt"] for s in je_schmied if s["eisen_je_1000_bei_eisen_satt"]]
        aus["schmiede"]["eisenbedarf_je_1000"] = round(1000.0 * eisen_verbraucht / ticks, 3)
        aus["schmiede"]["eisenbedarf_je_1000_bei_eisen_satt"] = round(sum(satte_raten), 3)
        minen_rate = sum(m["eisen_je_1000_ab_bau"] or 0 for m in aus["minen"])
        gueltige_minenraten = [m["eisen_je_1000_stationaer"] for m in aus["minen"] if m["gueltig"]]
        mine_mittel = sum(gueltige_minenraten) / len(gueltige_minenraten) if gueltige_minenraten else None
        aus["kettengleichgewicht"] = {"minen_eisen_je_1000": round(minen_rate, 3),
                                      "schmieden_eisenbedarf_je_1000": aus["schmiede"]["eisenbedarf_je_1000"],
                                      "schmieden_eisenbedarf_satt_je_1000": aus["schmiede"]["eisenbedarf_je_1000_bei_eisen_satt"],
                                      "ueberschuss_eisen_je_1000": round(minen_rate - aus["schmiede"]["eisenbedarf_je_1000"], 3),
                                      "mine_eisen_je_1000_nach_besetzung": round(mine_mittel, 3) if mine_mittel else None,
                                      "minen_noetig_je_schmied": round((sum(satte_raten) / len(satte_raten)) / mine_mittel, 2)
                                      if satte_raten and mine_mittel else None}
        aus["leder"] = {"leder_bestand": [a["leder"], z["leder"]], "leder_gesamt": leder,
                         "ticks": [a["t"], z["t"]], "verkauft": ab.get("leder", 0)}
        # Zeitpunkte jeder neuen Keule / jedes neuen Leders
        for w in ("keule", "leder"):
            spr = []
            for p, q in zip(proben, proben[1:]):
                if (q.get(w) or 0) > (p.get(w) or 0):
                    spr.append((q["t"], q[w] - p[w]))
            aus["%s_zugang" % w] = spr
    aus["kuehe_max"] = max((k for _, k in kuehe), default=0)
    aus["erste_kuh"] = next((t for t, k in kuehe if k > 0), None)
    aus["lager"] = [(b["x"], b["y"]) for b in lager]
    return aus


if __name__ == "__main__":
    print(json.dumps(auswerten(sys.argv[1]), indent=1, ensure_ascii=False))
