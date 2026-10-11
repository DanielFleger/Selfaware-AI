# -*- coding: utf-8 -*-
"""Messpartie Nahrungsketten unter der laufenden Balance (SAI 11.10., Daniel 17:03 "leg los mit der Messpartie").

Anlass: die selbstbestimmte Eroeffnung soll Nahrungsquellen nach Lage waehlen (Daniel 16:51: "ohne Aepfel sind Jaeger
besser, Brot fehlt komplett"). Frage-Agent 16:57: fuer Jaeger, Weizen, Muehle, Baeckerei gibt es unter Ascension keinen
Messwert, und Verkaufsgold ist die falsche Waehrung fuer Nahrung. Gemessen wird darum NAHRUNG je 1.000 Ticks.

PRUEFSTAND, kein Spiel um den Sieg: frisches Gefecht (Standard Liga_Grumpy Neighbors, Gegner Nomade - greift erst ab
~Tick 11.900 an), Gold per poke gesetzt. Je EIN Bau: Apfelplantage, Jaegerhuette an der Herde, Milchviehhof, Getreidefarm +
Muehle + Baeckerei; dazu Markt, Kornspeicher, Huetten. Rationen "keine" (nr 35 = 0), damit nichts gegessen wird und der
Bestand die volle Erzeugung zeigt; Steuerstufe 0 (Bestechung) haelt die Beliebtheit. Alle <stich> Ticks: Bestand jeder
Nahrungs- und Vorware, Leute, Beliebtheit.
Ergebnis: daten/nahrung_messung_<balance>.json - je Ware erste Lieferung (Tick nach Baubefehl), Zuwachs, Rate je 1.000
Ticks ab erster Lieferung, Baukosten aus dem laufenden Spiel, Weg zum Kornspeicher.
Aufruf: SHC_INSTANZ=4 python nahrung_messen.py [ticks=9000] [stich=250] [karte=Liga_Grumpy Neighbors] [kurz=M19] [balance=ascension]"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import befehl as kanal
import erstes_spiel as es
from bauen import vorrat
from farmen_mischen import lies_karte
from laden import befehl, peek
from steuerkarte import laufe, tick
from waechter import lies_lagebild, schach

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
PD = 0x0115BDF8 + 0x39F4
WAREN = ("apfel", "fleisch", "kaese", "brot", "weizen", "mehl", "gold")
BAUTEN = {"apfel": 32, "jaeger": 7, "milch": 33, "getreide": 30, "muehle": 34, "baeckerei": 17}


def plaetze_frei(kandidaten, belegt, abstand):
    for p in kandidaten:
        if all(schach(p, q) >= abstand for q in belegt):
            return p
    return None


def bau_erreichbar(typ, kandidaten, belegt, abstand, r=4, versuche=8):
    """Bauen und pruefen, ob das Spiel das Gebaeude als erreichbar meldet (Gebaeudetabelle 'erreichbar'). SAI 11.10.:
    erste Messpartie setzte Apfelhof (178,240) und Muehle (176,225) auf fruchtbare, aber unerreichbare Plaetze - der
    Bauer lief 9.000 Ticks auf sein Feld zu. Unerreichbar -> abreissen, naechster Platz. Gibt (Ort, Versuche)."""
    from waechter import lies_gebaeude
    probiert = 0
    for p in kandidaten:
        if probiert >= versuche:
            break
        if not all(schach(p, q) >= abstand for q in belegt):
            continue
        probiert += 1
        ort = es.baue_schnell(typ, p[0], p[1], r)
        if not ort:
            continue
        laufe(30)
        befehl({"lagebild": True}, 1.5, bis="LAGEBILD")
        G = lies_gebaeude()
        nr = min((n for n, g in G.items() if g["besitzer"] == 1 and g["typ"] == typ),
                 key=lambda n: schach((G[n]["x"], G[n]["y"]), ort), default=None)
        if nr is not None and G[nr].get("erreichbar", 1) == 1:
            return ort, probiert
        if nr is not None:
            befehl({"abreissen": {"nr": nr}}, 0.8, bis="ABREISSEN")
            laufe(5)
            print("unerreichbar, abgerissen: %s bei %s" % (es.NACH_TYP[typ]["name"], ort), flush=True)
    return None, probiert


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    ticks, stich = int(arg.get("ticks", 9000)), int(arg.get("stich", 250))
    kurz, balance = arg.get("kurz", "M19"), arg.get("balance", "ascension")
    import karten_holen
    karten_holen.gefecht_frisch(arg.get("karte", "Liga_Grumpy Neighbors"))
    info = json.load(open(os.path.join(D, "start_%s.json" % kurz), encoding="utf-8"))
    K = tuple(info["bergfried_eingang"])
    F = tuple(info["feind_bergfried"]["2"]["eingang"])
    eigen = lambda p: schach(p, K) < schach(p, F)
    karte = lambda n: sorted([p for p in lies_karte(os.path.join(D, "start_%s_platz_%s.txt" % (kurz, n))) if eigen(p)],
                             key=lambda p: schach(p, K))
    befehl({"tempo": 1000}, 0.5)
    befehl({"pause": False}, 0.5)
    befehl({"poke": PD + 0x50C, "wert": 6000}, 0.8, bis="POKE")          # Pruefstand: Gold
    kosten = {n: es.kosten_spiel(t) for n, t in BAUTEN.items()}
    print("Baukosten (Spiel):", kosten, flush=True)

    def kaufe(nr, lose):
        es.sende({"befehle": [{"player": 1, "id": es.neue_id(), "spielbefehl": {"nr": 38, "werte": [0, nr]}}
                              for _ in range(lose)]}, 2.0, bis="SPIELBEFEHL")
        laufe(10)
    bau = {"markt": es.baue_schnell(26, K[0], K[1], 25)}
    laufe(40)
    kaufe(2, 16)                                                          # 80 Holz fuer die Messbauten
    fruchtbar = karte("apfel")
    bau["kornspeicher"] = es.baue_schnell(19, fruchtbar[0][0], fruchtbar[0][1], 12) if fruchtbar else es.baue_schnell(19, K[0], K[1], 15)
    laufe(100)
    belegt = [bau["kornspeicher"]] if bau["kornspeicher"] else []
    ks = bau["kornspeicher"] or K
    fruchtbar.sort(key=lambda p: schach(p, ks))
    for n in ("apfel", "milch", "getreide"):
        bau[n], v = bau_erreichbar(BAUTEN[n], fruchtbar, belegt, 12)
        print("%s: %s nach %d Versuch(en)" % (n, bau[n], v), flush=True)
        if bau[n]:
            belegt.append(bau[n])
    huette = karte("huette")
    nahe = bau.get("getreide") or ks
    bau["muehle"], _ = bau_erreichbar(34, sorted(huette, key=lambda p: schach(p, nahe)), belegt, 5, r=2)
    bau["baeckerei"], _ = bau_erreichbar(17, sorted(huette, key=lambda p: schach(p, ks)), belegt + [bau["muehle"]] if bau["muehle"] else belegt, 5, r=2)
    L = lies_lagebild(neu_holen=True)
    rehe = [(e["x"], e["y"]) for e in L.values() if e["typ"] == 44 and eigen((e["x"], e["y"])) and schach((e["x"], e["y"]), K) <= 70]
    herde = max(rehe, key=lambda p: sum(1 for q in rehe if schach(p, q) <= 15)) if rehe else None
    bau["jaeger"] = es.baue_schnell(7, herde[0], herde[1], 12) if herde else None
    for i in range(4):
        bau["huette%d" % i] = es.baue_schnell(1, K[0] - 7, K[1] - 2, 25)
    befehl({"spielbefehl": {"nr": 35, "werte": [0]}}, 1.0, bis="SPIELBEFEHL")      # Rationen keine
    befehl({"spielbefehl": {"nr": 34, "werte": [0]}}, 1.0, bis="SPIELBEFEHL")      # Steuerstufe 0 = Bestechung
    print("Gebaut:", bau, "| Herde:", herde, "(%d Rehe eigene Seite <=70)" % len(rehe), flush=True)

    t0, reihe = tick(), []
    stempel = time.strftime("%Y%m%d_%H%M%S")
    aus = open(os.path.join(D, "nahrung_messung_%s_%s.txt" % (balance, stempel)), "w", encoding="utf-8")
    aus.write("# %s Nahrungs-Messpartie (Pruefstand), Bauten %s\ntick %s leute beliebt\n" % (stempel, bau, " ".join(WAREN)))
    while tick() - t0 < ticks:
        kanal.belege()
        laufe(stich)
        v = vorrat(1)
        st = " ".join(befehl({"status": 1}, 1.5, bis="STATUS"))
        leute = int(re.search(r"leute=(\d+)", st).group(1)) if "leute=" in st else -1
        beliebt = int(re.search(r"beliebt=(-?\d+)", st).group(1)) if "beliebt=" in st else -1
        reihe.append((tick() - t0, {w: v.get(w, 0) for w in WAREN}, leute, beliebt))
        aus.write("%d %s %d %d\n" % (reihe[-1][0], " ".join(str(reihe[-1][1][w]) for w in WAREN), leute, beliebt))
        aus.flush()
    erg = {}
    for w in WAREN[:-1]:
        werte = [(t, r[w]) for t, r, _, _ in reihe]
        erst = next((t for (t, x), (_, y) in zip(werte, werte[1:]) if y > x), None)
        zuwachs = sum(max(0, y - x) for (_, x), (_, y) in zip(werte, werte[1:]))
        dauer = (werte[-1][0] - erst) if erst is not None else 0
        erg[w] = {"erste_lieferung_tick": erst, "zuwachs": zuwachs,
                  "je_1000_ticks": round(1000.0 * zuwachs / dauer, 2) if dauer else 0}
    ks = bau.get("kornspeicher")
    wege = {n: (schach(bau[n], ks) if bau.get(n) and ks else None) for n in BAUTEN}
    ergebnis = {"balance": balance, "karte": arg.get("karte", "Liga_Grumpy Neighbors"), "ticks": ticks, "bauten": bau,
                "kosten": kosten, "ertrag": erg, "wege_zum_kornspeicher": wege,
                "leute_min": min(r[2] for r in reihe), "beliebt_min": min(r[3] for r in reihe)}
    json.dump(ergebnis, open(os.path.join(D, "nahrung_messung_%s.json" % balance), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(ergebnis, ensure_ascii=False), flush=True)
    befehl({"pause": True}, 0.5)


if __name__ == "__main__":
    kanal._kanal_frei()
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
