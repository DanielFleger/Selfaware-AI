# -*- coding: utf-8 -*-
"""Nahrungswahl: die KI rechnet ihre Nahrungsmischung je Karte selbst aus (SAI 11.10.; neu geschrieben 23:28).

Daniel 22:53: "Brot haengt davon ab, ob du mid- oder lategame eine bessere Essensversorgung willst; Brot ist effektiver bei
weniger Farmplatz und je naeher die Farm am Vorratslager". 23:05 (Frage 1, "ja"): keine Gewichte von Hand - die KI spielt
ihre Versorgung im Voraus durch und waehlt die Mischung, die den Verbrauch mit den wenigsten Arbeitern und dem wenigsten
Holz deckt. 23:20: "warum nicht hybrid, z.B. Rehe" und "Kornspeicher naeher an die Baeckereien".

Rechnung (alle Zahlen gemessen, siehe nahrungsmodell.py und Wissensregister L58-L61):
  Bedarf(t) = Leute(t) * Verbrauch je Kopf (Ration). Leute(t) = gemessener Verlauf (Lenker auf Two Montains, Lauf 23:09),
             hoechstens Bevoelkerungsziel.
  Quellen: Jaeger an den Herden der Startzaehlung (karten_holen.rehe_zaehlen; je Herde bis 2 Jaeger mit eigenem
             Kornspeicher - Lauf 23:26: Herde wird nicht leer gejagt), Aepfel in Gruppen (fruchtbare Plaetze nahe am
             Bergfried zuerst - Lage vor Laufweg), Brotketten (Getreidefarm am Platz naechst dem Lager).
  Frueh (bis Brot liefern kann, ~9.500 Ticks nach dem Bau): Jaeger + Aepfel. Spaet: dazu Brot.
  Alle Mischungen (Jaeger x Brotketten x Aepfel) werden durchgerechnet; genommen wird die, die frueh UND spaet deckt, mit
  den wenigsten Arbeitern, dann dem wenigsten Holz. Reicht frueh nichts fuer doppelte Rationen: frueh normal.
  Brot bekommt einen eigenen Kornspeicher am Lager, wenn der Apfel-Kornspeicher mehr als 10 Felder weg liegt.
Ausgabe: dict mit aepfel, kornspeicher, jaeger, brot (oder None) und begruendung (jede Zahl der Entscheidung)."""
import json
import os

import nahrungsmodell as M

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
# Leute ueber die Zeit, Lenker auf Two Montains (daten/tm_probe_konsole2.txt, Spalte Leute), bevoelkerung_ziel=90
LEUTE = [(0, 10), (921, 10), (2338, 37), (3694, 48), (6195, 52), (8106, 67), (9624, 79), (11289, 86), (11884, 93)]
VERBRAUCH = {"keine": 0.0, "normal": 0.19, "doppelt": 0.39}        # je Kopf und 1.000 Ticks (L61)
HOLZ = {"apfel": 8, "getreide": 18, "muehle": 18, "baeckerei": 12, "jaeger": 8}   # Ascension; Lenker liest live
GROESSE_APFEL = 10
JAGD_WEG, JAGD_UMKREIS, JAGD_MIN = 70, 15, 5         # wie der Jaegerweg der Wirtschaft (wirtschaft.py, Lauf 9q)
JAEGER_JE_HERDE = 2          # gemessen mit 2 (Lauf 23:26): Herde blieb; mehr ist ungemessen
# L62 (23:31): weitere Kornspeicher nur angrenzend - Jaeger liefern zum EINEN Kornspeicher-Ort, kein eigener an der Herde


def leute(t, ziel):
    for (t0, p0), (t1, p1) in zip(LEUTE, LEUTE[1:]):
        if t <= t1:
            p = p0 + (p1 - p0) * (t - t0) / float(t1 - t0)
            return min(p, ziel) if ziel else p
    return min(LEUTE[-1][1], ziel) if ziel else LEUTE[-1][1]


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def apfel_plaetze(kurz, K, feinde, erlaubt=lambda p: True):
    """Nicht ueberlappende 10x10-Plaetze der eigenen Seite (Platzkarte des Spiels), die naechsten zum Bergfried zuerst."""
    from farmen_mischen import lies_karte
    roh = lies_karte(os.path.join(D, "start_%s_platz_apfel.txt" % kurz))
    eigen = [p for p in roh if erlaubt(p) and all(schach(p, K) < schach(p, f) for f in feinde)]
    aus = []
    for p in sorted(eigen, key=lambda q: schach(q, K)):
        if all(abs(p[0] - q[0]) >= GROESSE_APFEL or abs(p[1] - q[1]) >= GROESSE_APFEL for q in aus):
            aus.append(p)
    return aus


def gruppe(plaetze, k, kerne=12):
    """k Plaetze, die am dichtesten beieinander liegen - gebildet nur um die `kerne` Plaetze naechst dem Bergfried (23:16:
    die reine Dichtesuche legte 10 Plantagen samt Kornspeicher 100 Felder vom Bergfried). Gibt (Plaetze, Mitte, Abstand)."""
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


def aepfel_fuer(plaetze, bedarf, speicher=None):
    """Kleinste Apfelgruppe, die `bedarf` deckt, sonst die ertragreichste. Gibt (k, gruppe, rate, gedeckt).
    speicher=None: Kornspeicher in der Gruppenmitte; sonst fester Ort - dann die k Plaetze naechst dem Speicher (L62: es gibt
    nur EINEN Kornspeicher-Ort, weitere wachsen angrenzend an)."""
    if bedarf <= 0 or not plaetze:
        return 0, None, 0.0, bedarf <= 0
    wahl = None
    for k in range(1, len(plaetze) + 1):
        if speicher is None:
            g = gruppe(plaetze, k)
        else:
            nah = sorted(plaetze, key=lambda q: schach((q[0] + 5, q[1] + 5), speicher))[:k]
            g = (nah, tuple(speicher), sum(schach((q[0] + 5, q[1] + 5), speicher) for q in nah) / float(k)) if len(nah) == k else None
        if not g:
            break
        rate = k * apfel_rate(k, g[2])
        if rate >= bedarf:
            return k, g, rate, True
        if wahl is None or rate > wahl[2]:
            wahl = (k, g, rate, False)
    return wahl


def herden(info, K, feinde):
    """Herden der eigenen Seite aus der Startzaehlung: je Herde Mitte und Zahl der Rehe (>= JAGD_MIN im Umkreis)."""
    rest = [tuple(p) for p in info.get("rehe", []) if schach(p, K) <= JAGD_WEG and all(schach(p, K) < schach(p, f) for f in feinde)]
    aus = []
    while rest:
        m = max(rest, key=lambda p: sum(1 for q in rest if schach(p, q) <= JAGD_UMKREIS))
        n = sum(1 for q in rest if schach(m, q) <= JAGD_UMKREIS)
        if n < JAGD_MIN:
            break
        aus.append((m, n))
        rest = [q for q in rest if schach(m, q) > JAGD_UMKREIS]
    return aus


def brotketten(frei, b, lager, speicher):
    brot, baeck, arb, holz = 0.0, 0, 0, 0
    for f in frei[:b]:
        m, bk, ar = M.brotkette(schach((f[0] + 4, f[1] + 4), lager), abstand_speicher=max(4, schach(lager, speicher)))
        brot, baeck, arb = brot + m, baeck + bk, arb + ar
        holz += HOLZ["getreide"] + HOLZ["muehle"] + bk * HOLZ["baeckerei"]
    return brot, baeck, arb, holz


# 18.10. (Daniel: "bau den Kornspeicher ein bis auf die Ecken" wie der Nomade, kornring.py): um den Kornspeicher bleibt ein
# Feld frei fuer den Mauerring - in 1018e lag an beiden Plaetzen eine Plantage darauf (3 bzw. 4 Ringkacheln)
RING_RAND = 2      # 19.10.: plus Burggraben (kornring.Graben) auf Abstand 2 - Ring UND Grabenring bleiben frei


def speicherplatz(kurz, punkt, belegt, erlaubt=lambda p: True):
    """Gueltiger Kornspeicher-Platz (Platzkarte des Spiels) naechst `punkt`, ohne Plantagen-/Farmflaeche - mit RING_RAND
    Feldern Abstand fuer den Mauerring."""
    from farmen_mischen import lies_karte
    speicher = lies_karte(os.path.join(D, "start_%s_platz_speicher.txt" % kurz))
    r = RING_RAND
    # belegt: (x, y) = Plantage/Farm (10x10) oder (x, y, Groesse) fuer andere geplante Bauten (Holzfaeller, Huetten, Lager)
    gr = lambda q: q[2] if len(q) > 2 else GROESSE_APFEL
    frei = [s for s in speicher if erlaubt(s) and all(s[0] + 4 + r <= q[0] or q[0] + gr(q) + r <= s[0] or s[1] + 4 + r <= q[1]
                                       or q[1] + gr(q) + r <= s[1] for q in belegt)]
    if not frei:
        raise ValueError("KEIN GUELTIGER KORNSPEICHER: %s - keine ungepruefte Ersatzkoordinate" % kurz)
    return tuple(min(frei, key=lambda s: (schach((s[0] + 2, s[1] + 2), punkt), s)))


def waehle(kurz, plan, bev_ziel=90, ration="doppelt", horizont=16000):
    """23:34 (L62: weitere Kornspeicher nur angrenzend): es gibt EINEN Kornspeicher-Ort - an den Aepfeln oder am Lager.
    Fuer beide Orte werden Jaeger x Brotketten x Aepfel mit den echten Abstaenden durchgerechnet (Aepfel zum Speicher,
    Jaeger von der Herde zum Speicher, Baecker Lager <-> Speicher); genommen wird die Mischung, die frueh UND spaet deckt,
    mit den wenigsten Arbeitern, dann dem wenigsten Holz."""
    info = json.load(open(os.path.join(D, "start_%s.json" % kurz), encoding="utf-8"))
    K = tuple(info["bergfried_eingang"])
    feinde = [tuple(v["eingang"]) for v in info["feind_bergfried"].values()]
    lager = tuple(plan.get("lager_mitte") or plan.get("lager") or K)
    from land import eigene_seite
    erlaubt = eigene_seite(info)
    plaetze = apfel_plaetze(kurz, K, feinde, erlaubt)
    hd = [(m, n) for m, n in herden(info, K, feinde) if erlaubt(m)]
    jaeger_max = sum(min(JAEGER_JE_HERDE, n // JAGD_MIN) for _, n in hd)
    t_brot = M.BROT_ERSTE
    # 19.10. (B-120-Test, bis_tick=6000): endet die Partie vor dem ersten Brot (horizont < t_brot), war der Bereich leer und
    # max() brach ab - dann gilt der Bedarf am Startpunkt des Abschnitts
    bedarf = lambda r, a, b: max(leute(t, bev_ziel) * VERBRAUCH[r] for t in range(a, max(a, b) + 1, 500))
    grund = {"plaetze_eigene_seite": len(plaetze), "herden": [(list(m), n) for m, n in hd], "jaeger_moeglich": jaeger_max,
             "ration": ration, "bev_ziel": bev_ziel, "rehe_gezaehlt": "rehe" in info}

    def jaeger_rate(h, speicher):                # die groessten Herden zuerst, je Herde bis JAEGER_JE_HERDE
        r, rest = 0.0, h
        for m, n in hd:
            if rest <= 0:
                break
            a = min(rest, JAEGER_JE_HERDE, n // JAGD_MIN)
            r += a * M.je_1000("jaeger", schach(m, speicher))
            rest -= a
        return r

    def rechne(r_frueh, ort):
        frueh, spaet = bedarf(r_frueh, 0, t_brot), bedarf(ration, t_brot, horizont)
        am_lager = sorted(plaetze, key=lambda p: schach((p[0] + 4, p[1] + 4), lager))
        opts = []
        for b in range(0, min(len(plaetze), 4) + 1):
            rest = [p for p in plaetze if p not in am_lager[:b]]
            fest = None if ort == "aepfel" else lager
            for h in range(0, jaeger_max + 1):
                # Speicherort: am Lager fest; an den Aepfeln = Mitte der fruehen Gruppe (ohne Aepfel: am Lager)
                k, g, rate, ok = aepfel_fuer(rest, frueh, fest)
                speicher = tuple(g[1]) if g else lager
                fleisch = jaeger_rate(h, speicher)
                if fleisch > 0 and frueh - fleisch < frueh:
                    k, g, rate, ok = aepfel_fuer(rest, frueh - fleisch, fest)
                    speicher = tuple(g[1]) if (g and fest is None) else speicher
                    fleisch = jaeger_rate(h, speicher)
                brot, baeck, arb_b, holz_b = brotketten(am_lager, b, lager, speicher)
                k2, g2, rate2, ok2 = aepfel_fuer(rest, spaet - fleisch - brot, speicher)
                if k2 < k:
                    k2, g2, rate2 = k, g, rate
                opts.append(dict(speicher_ort=ort, jaeger=h, brotketten=b, aepfel=k2, fleisch_1000=round(fleisch, 1),
                                 brot_1000=round(brot, 1), apfel_1000=round(rate2, 1), baeckereien=baeck,
                                 frueh_gedeckt=fleisch + rate >= frueh, spaet_gedeckt=fleisch + brot + rate2 >= spaet,
                                 arbeiter=h + arb_b + k2, holz=h * HOLZ["jaeger"] + holz_b + k2 * HOLZ["apfel"],
                                 speicher_lager=schach(speicher, lager), _farmen=am_lager[:b], _g=g, _g2=g2, _k=k, _rate=rate,
                                 _speicher=speicher))
        return frueh, spaet, opts

    def alle(r_frueh):
        f = s = None
        o = []
        for ort in ("aepfel", "lager"):
            f, s, oo = rechne(r_frueh, ort)
            o += oo
        return f, s, o

    ration_frueh = ration
    frueh, spaet, opts = alle(ration)
    if ration == "doppelt" and not any(o["frueh_gedeckt"] and o["spaet_gedeckt"] for o in opts):
        # 23:36 (Two Montains): doppelt deckt frueh nur OHNE Brot, dann fehlt es spaet - frueh normal essen, damit Platz fuer Brot bleibt
        ration_frueh = "normal"
        frueh, spaet, opts = alle("normal")
    beide = [o for o in opts if o["frueh_gedeckt"] and o["spaet_gedeckt"]]
    beste = min(beide, key=lambda o: (o["arbeiter"], o["holz"])) if beide else \
        max(opts, key=lambda o: (o["frueh_gedeckt"], o["fleisch_1000"] + o["brot_1000"] + o["apfel_1000"]))
    grund.update(ration_frueh=ration_frueh, bedarf_frueh_1000=round(frueh, 1), bedarf_spaet_1000=round(spaet, 1),
                 optionen=[{k_: v for k_, v in o.items() if not k_.startswith("_")}
                           for o in sorted(beide or opts, key=lambda o: (o["arbeiter"], o["holz"]))[:6]],
                 entscheidung="%d Jaeger + %d Brotkette(n) + %d Apfelplantagen, Kornspeicher %s" % (
                     beste["jaeger"], beste["brotketten"], beste["aepfel"],
                     "an den Aepfeln" if beste["speicher_ort"] == "aepfel" else "am Lager")
                 + ("" if beste in beide else " - Bedarf NICHT gedeckt"))
    jaeger, rest_h = [], beste["jaeger"]
    for m, n in hd:
        if rest_h <= 0:
            break
        a = min(rest_h, JAEGER_JE_HERDE, n // JAGD_MIN)
        jaeger.append(dict(herde=list(m), rehe=n, anzahl=a))
        rest_h -= a
    g, g2 = beste["_g"], beste["_g2"] or beste["_g"]
    aepfel = ([list(p) for p in g[0]] if g else []) + [list(p) for p in (g2[0] if g2 else []) if not g or p not in g[0]]
    aepfel = aepfel[:beste["aepfel"]]
    brot = None
    if beste["brotketten"]:
        vorher = beste["fleisch_1000"] + beste["_rate"]
        bedarf_ab = next((tt for tt in range(0, horizont + 1, 250) if leute(tt, bev_ziel) * VERBRAUCH[ration] > vorher), horizont)
        brot = dict(getreide=[list(f) for f in beste["_farmen"]], baeckereien=beste["baeckereien"],
                    ab_tick=max(0, bedarf_ab - t_brot), bedarf_ab_tick=bedarf_ab)
    belegt = [tuple(p) for p in aepfel] + [tuple(f) for f in (brot or {}).get("getreide", [])]
    # 18.10. (Kornring): auch die festen Eroeffnungsbauten meiden - in CloseEncounters pl3-2 laege sonst ein Holzfaeller
    # (231,300) auf dem Ring des Speichers (227,298)
    from bauen import NACH_TYP           # Groessen aus der Bautabelle (Holzfaeller 3, Huette 4); Lagerplatz 4 Teile = 6x6
    belegt += [(p[0], p[1], NACH_TYP[3]["b"]) for p in plan.get("holzfaeller", [])] +               [(p[0], p[1], NACH_TYP[1]["b"]) for p in plan.get("huetten", [])]
    if plan.get("lager"):
        belegt.append((plan["lager"][0], plan["lager"][1], 6))
    ks = list(speicherplatz(kurz, beste["_speicher"], belegt, erlaubt))
    grund["kornspeicher_zum_bergfried"] = schach(tuple(ks), K)
    grund["kornspeicher_zum_lager"] = schach(tuple(ks), lager)
    return {"aepfel": aepfel, "kornspeicher": ks, "brot": brot, "jaeger": jaeger, "ration_frueh": ration_frueh,
            "begruendung": grund}


if __name__ == "__main__":
    import sys
    for kurz in (sys.argv[1:] or ["M19", "TM"]):
        plan = json.load(open(os.path.join(D, "eroeffnung_plan_%s.json" % kurz), encoding="utf-8"))
        for ration in ("normal", "doppelt"):
            w = waehle(kurz, plan, ration=ration)
            b = w["begruendung"]
            print("%s %s: %s | Herden %s | frueh %s, Bedarf %s/%s | Kornspeicher %s | Jaeger %s | Brot %s" % (
                kurz, ration, b["entscheidung"], b["herden"], w["ration_frueh"], b["bedarf_frueh_1000"], b["bedarf_spaet_1000"],
                w["kornspeicher"], [(j["herde"], j["anzahl"]) for j in w["jaeger"]],
                {k: w["brot"][k] for k in ("getreide", "baeckereien", "ab_tick")} if w["brot"] else "nein"))
            for o in b["optionen"][:3]:
                print("      ", o)
