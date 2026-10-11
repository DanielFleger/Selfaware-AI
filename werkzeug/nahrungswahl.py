# -*- coding: utf-8 -*-
"""Nahrungswahl: die KI rechnet ihre Nahrungsmischung je Karte selbst aus (SAI 11.10. 23:15).

Daniel 22:53: "Brot haengt davon ab, ob du mid- oder lategame eine bessere Essensversorgung willst; Brot ist effektiver bei
weniger Farmplatz und je naeher die Farm am Vorratslager". 23:05 (Frage 1, "ja"): keine Gewichte von Hand - die KI spielt
ihre Versorgung im Voraus durch und waehlt die Mischung, die den Verbrauch mit den wenigsten Arbeitern und dem wenigsten
Holz deckt.

Rechnung (alle Zahlen gemessen, siehe nahrungsmodell.py und Wissensregister L58-L61):
  Bedarf(t) = Leute(t) * Verbrauch je Kopf (Ration). Leute(t) = gemessener Verlauf (Lenker auf Two Montains, Lauf 23:09),
             hoechstens Bevoelkerungsziel.
  Frueh (bis Brot liefern kann): Aepfel. Plantagen auf den fruchtbaren Plaetzen der eigenen Seite, die am dichtesten
             beieinander liegen (gemeinsamer Kornspeicher); ab 3 gilt das Gruppenmodell, darunter der Einzelwert.
  Spaet: fehlenden Bedarf entweder mit weiteren Apfelplantagen (falls Plaetze da sind) oder mit einer Brotkette decken -
             gewaehlt wird, was weniger Arbeiter braucht, bei Gleichstand weniger Holz. Fehlen Plaetze, kommt Brot.
             Brot wird so frueh gebaut, dass es bei Bedarf liefert (erstes Brot ~9.500 Ticks nach dem Bau).
  Jaeger plant die Wahl nicht vorab - Herden sieht man erst im Spiel; das macht der Jaegerweg der Wirtschaft.
Ausgabe: dict mit aepfel, kornspeicher, brot (oder None) und begruendung (jede Zahl der Entscheidung)."""
import json
import math
import os

import nahrungsmodell as M

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
# Leute ueber die Zeit, Lenker auf Two Montains (daten/tm_probe_konsole2.txt, Spalte Leute), bevoelkerung_ziel=90
LEUTE = [(0, 10), (921, 10), (2338, 37), (3694, 48), (6195, 52), (8106, 67), (9624, 79), (11289, 86), (11884, 93)]
VERBRAUCH = {"keine": 0.0, "normal": 0.19, "doppelt": 0.39}        # je Kopf und 1.000 Ticks (L61)
HOLZ = {"apfel": 8, "getreide": 18, "muehle": 18, "baeckerei": 12}   # Ascension-Preise; im Spiel liest der Lenker sie live
GROESSE_APFEL = 10


def leute(t, ziel):
    for (t0, p0), (t1, p1) in zip(LEUTE, LEUTE[1:]):
        if t <= t1:
            p = p0 + (p1 - p0) * (t - t0) / float(t1 - t0)
            return min(p, ziel) if ziel else p
    return min(LEUTE[-1][1], ziel) if ziel else LEUTE[-1][1]


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def apfel_plaetze(kurz, K, feinde):
    from farmen_mischen import lies_karte
    roh = lies_karte(os.path.join(D, "start_%s_platz_apfel.txt" % kurz))
    eigen = [p for p in roh if all(schach(p, K) < schach(p, f) for f in feinde)]
    # nicht ueberlappende 10x10-Plaetze, die naechsten zum Bergfried zuerst
    aus = []
    for p in sorted(eigen, key=lambda q: schach(q, K)):
        if all(abs(p[0] - q[0]) >= GROESSE_APFEL or abs(p[1] - q[1]) >= GROESSE_APFEL for q in aus):
            aus.append(p)
    return aus


def gruppe(plaetze, k, kerne=12):
    """k Plaetze, die am dichtesten beieinander liegen - gebildet nur um die `kerne` Plaetze, die dem Bergfried am naechsten
    sind (Lage vor Laufweg: 23:16 legte die reine Dichtesuche 10 Plantagen samt Kornspeicher 100 Felder vom Bergfried).
    plaetze sind nach Abstand zum Bergfried sortiert. Gibt (Plaetze, Kornspeicher-Mitte, mittlerer Abstand) oder None."""
    beste = None
    for kern in plaetze[:kerne]:
        nah = sorted(plaetze, key=lambda q: schach(q, kern))[:k]
        if len(nah) < k:
            continue
        mx = sum(q[0] for q in nah) / float(k) + GROESSE_APFEL / 2.0
        my = sum(q[1] for q in nah) / float(k) + GROESSE_APFEL / 2.0
        ab = sum(schach((q[0] + 5, q[1] + 5), (mx, my)) for q in nah) / float(k)
        if beste is None or ab < beste[2]:
            beste = (nah, (int(mx), int(my)), ab)
    return beste


def apfel_rate(k, abstand):
    return M.je_1000("apfel_gruppe", abstand) if k >= 3 else M.APFEL_EINZELN_JE_1000


def aepfel_fuer(plaetze, bedarf):
    """Kleinste Apfelgruppe, die `bedarf` deckt, sonst die groesste. Gibt (k, gruppe, rate, gedeckt)."""
    wahl = None
    for k in range(1, len(plaetze) + 1):
        g = gruppe(plaetze, k)
        if not g:
            break
        rate = k * apfel_rate(k, g[2])
        if wahl is None or rate > wahl[2]:
            wahl = (k, g, rate, rate >= bedarf)
        if rate >= bedarf:
            return (k, g, rate, True)
    return wahl


def waehle(kurz, plan, bev_ziel=90, ration="doppelt", horizont=16000):
    info = json.load(open(os.path.join(D, "start_%s.json" % kurz), encoding="utf-8"))
    K = tuple(info["bergfried_eingang"])
    feinde = [tuple(v["eingang"]) for v in info["feind_bergfried"].values()]
    lager = tuple(plan.get("lager_mitte") or plan.get("lager") or K)
    plaetze = apfel_plaetze(kurz, K, feinde)
    grund = {"plaetze_eigene_seite": len(plaetze), "ration": ration, "bev_ziel": bev_ziel}
    if not plaetze:
        return {"aepfel": [], "kornspeicher": None, "brot": None, "ration_frueh": ration,
                "begruendung": dict(grund, fehler="kein fruchtbarer Platz auf der eigenen Seite - nur Jaeger/Kauf")}
    bedarf = lambda r, a, b: max(leute(t, bev_ziel) * VERBRAUCH[r] for t in range(a, b + 1, 500))
    t_brot = M.BROT_ERSTE
    # 1. frueh: nur Aepfel liefern vor dem ersten Brot. Reicht der Boden fuer die gewuenschte Ration nicht, normale Ration.
    ration_frueh = ration
    k, g, rate, ok = aepfel_fuer(plaetze, bedarf(ration, 0, t_brot))
    if not ok and ration == "doppelt":
        ration_frueh = "normal"
        k, g, rate, ok = aepfel_fuer(plaetze, bedarf("normal", 0, t_brot))
    grund.update(bedarf_frueh_1000=round(bedarf(ration_frueh, 0, t_brot), 1), ration_frueh=ration_frueh, aepfel_frueh=k,
                 apfel_abstand=round(g[2], 1), apfel_rate_1000=round(rate, 1), frueh_gedeckt=ok,
                 kornspeicher_zum_bergfried=schach(g[1], K))
    # 2. spaet: die restlichen Plaetze gemeinsam verteilen - b Brotketten (je 1 Platz, der dem Lager naechste zuerst),
    #    der Rest weitere Aepfel; genommen wird die Mischung mit den wenigsten Arbeitern (dann Holz), die den Bedarf deckt
    spaet = bedarf(ration, t_brot, horizont)
    grund["bedarf_spaet_1000"] = round(spaet, 1)
    frei = sorted([p for p in plaetze if p not in g[0]], key=lambda p: schach((p[0] + 4, p[1] + 4), lager))
    optionen = []
    for b in range(0, min(len(frei), 4) + 1):
        farmen = frei[:b]
        brot, baeck, arb_b, holz_b = 0.0, 0, 0, 0
        for f in farmen:
            m, bk, ar = M.brotkette(schach((f[0] + 4, f[1] + 4), lager))
            brot, baeck, arb_b = brot + m, baeck + bk, arb_b + ar
            holz_b += HOLZ["getreide"] + HOLZ["muehle"] + bk * HOLZ["baeckerei"]
        rest = [p for p in plaetze if p not in farmen]
        k2, g2, rate2, ok2 = aepfel_fuer(rest, max(0.0, spaet - brot))
        if ok2 and k2 < k:                      # die fruehen Plantagen stehen ohnehin - mit ihrer Rate rechnen
            k2, g2, rate2 = k, g, rate
        gesamt = brot + rate2
        optionen.append(dict(brotketten=b, brot_1000=round(brot, 1), baeckereien=baeck, aepfel=k2, apfel_1000=round(rate2, 1),
                             gedeckt=gesamt >= spaet, arbeiter=arb_b + k2, holz=holz_b + k2 * HOLZ["apfel"],
                             _farmen=farmen, _gruppe=g2))
    gedeckt = [o for o in optionen if o["gedeckt"]]
    beste = min(gedeckt, key=lambda o: (o["arbeiter"], o["holz"])) if gedeckt else max(optionen, key=lambda o: o["brot_1000"] + o["apfel_1000"])
    grund["optionen"] = [{k_: v for k_, v in o.items() if not k_.startswith("_")} for o in optionen]
    grund["entscheidung"] = ("%d Brotkette(n) + %d Apfelplantagen" % (beste["brotketten"], beste["aepfel"])) +         ("" if beste["gedeckt"] else " - Bedarf NICHT gedeckt (Jaeger/Kauf/Ration noetig)")
    brot = None
    if beste["brotketten"]:
        bedarf_ab = next((tt for tt in range(0, horizont + 1, 250) if leute(tt, bev_ziel) * VERBRAUCH[ration] > rate), horizont)
        brot = dict(getreide=[list(f) for f in beste["_farmen"]], baeckereien=beste["baeckereien"],
                    ab_tick=max(0, bedarf_ab - t_brot), bedarf_ab_tick=bedarf_ab)
    g_end = beste["_gruppe"] or g
    # die fruehen Plantagen zuerst (Reihenfolge = Bauordnung: A-Gruppe), die spaeteren danach
    aepfel = [list(p) for p in g[0]] + [list(p) for p in g_end[0] if p not in g[0]][:max(0, beste["aepfel"] - k)]
    # Kornspeicher: gueltiger Platz laut Platzkarte des Spiels, am naechsten zur Gruppenmitte, ohne Plantagenflaeche
    from farmen_mischen import lies_karte
    speicher = lies_karte(os.path.join(D, "start_%s_platz_speicher.txt" % kurz))
    belegt = [tuple(p) for p in aepfel] + [tuple(f) for f in (brot or {}).get("getreide", [])]
    frei_s = [s for s in speicher if all(s[0] + 4 <= q[0] or q[0] + GROESSE_APFEL <= s[0] or s[1] + 4 <= q[1] or
                                         q[1] + GROESSE_APFEL <= s[1] for q in belegt)]
    ks = min(frei_s, key=lambda s: schach((s[0] + 2, s[1] + 2), g[1])) if frei_s else g[1]
    grund["kornspeicher_von_mitte"] = schach((ks[0] + 2, ks[1] + 2), g[1])
    return {"aepfel": aepfel, "kornspeicher": list(ks), "brot": brot, "ration_frueh": ration_frueh, "begruendung": grund}


if __name__ == "__main__":
    import sys
    for kurz in (sys.argv[1:] or ["M19", "TM"]):
        plan = json.load(open(os.path.join(D, "eroeffnung_plan_%s.json" % kurz), encoding="utf-8"))
        for ration in ("normal", "doppelt"):
            w = waehle(kurz, plan, ration=ration)
            b = w["begruendung"]
            print("%s %s: %s | frueh %d Aepfel (Ration %s, Bedarf %s, Rate %s, gedeckt %s), Kornspeicher %s (%s Felder vom Bergfried), Brot %s" % (
                kurz, ration, b.get("entscheidung", b.get("fehler")), b.get("aepfel_frueh", 0), w["ration_frueh"], b.get("bedarf_frueh_1000"),
                b.get("apfel_rate_1000"), b.get("frueh_gedeckt"), w["kornspeicher"], b.get("kornspeicher_zum_bergfried"),
                {k: w["brot"][k] for k in ("getreide", "baeckereien", "ab_tick")} if w["brot"] else "nein"))
            for o in b.get("optionen", []):
                print("      ", o)
