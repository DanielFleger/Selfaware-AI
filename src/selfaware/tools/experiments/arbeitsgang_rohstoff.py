# -*- coding: utf-8 -*-
"""Arbeitsgang der Rohstoff-Arbeiter unter Ascension messen (SAI 12.10., Daniel 01:04 "du musst auch Stein und Eisen
scalen", 01:09 "du brauchst Cash von Steinen/Eisen/Brot", 01:16 "du testest schlau und nachhaltig oder?").

Schlau (Daniel 11.10. 17:12: "per Tick per Entfernung"): je Art DREI Betriebe in gestaffelter Entfernung zum Lager
(abstaende=10,30,50), jeder Arbeiter alle 2 Ticks mitgeschrieben (Modulbefehl einheitwacht) -> je Gang Hinweg, Rueckweg,
Arbeitszeit am Betrieb, Ladung. Daraus die Formel Ertrag(d) = Ladung / (Arbeitszeit + 2 * d * Ticks_je_Feld) fuer JEDE
Entfernung auf jeder Karte, nicht nur fuer die gemessenen drei.
Nachhaltig: Rohdaten (EW-Zeilen, Ladungen, Bestand, Verkaeufe, Stillstaende, Lagerteile) nach data/research/; die Formel geht in
ein Modell, das der Lenker auf jeder Karte nutzt.
VORHER festgelegt (Widerlegung): die Formel aus den Gaengen muss die Bestandsrate desselben Laufs (Zugang + Verkauf je
1.000 Ticks ab der ersten Lieferung) je Art auf 20 % treffen - sonst fehlt ein Faktor (Warten, volles Lager, Abwandern,
Ochse/Traeger als Engpass); dann die Spuren genau darauf durchsehen.
Pruefstand: Grumpy Neighbors gegen eine Ratte mit leerer KI, Gold gesetzt, Baukosten 0 (Sicherung als Datei, Rueckweg im
finally), Rationen keine, Steuer Bestechung (haelt die Beliebtheit; sonst wandern Arbeiter ab, 11.10. 17:17).
Arten: holz (Holzfaeller 3), stein (Steinbruch 20 + je ein Ochsenkarren 4), eisen (Eisenmine 5), hopfen (Hopfenfarm 31),
pech (Pechgraeber 6). Aufruf: SHC_INSTANZ=4 uv run python -m selfaware.tools.experiments.arbeitsgang_rohstoff art=holz,stein,eisen,hopfen [ticks=12000]
[tempo=300] [abstaende=10,30,50]"""

from selfaware import workspace as _workspace
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.game.ucp.befehl as kanal
import selfaware.runtime.live.erstes_spiel as E
import selfaware.services.wegkarte as W
from selfaware.game.ucp.laden import befehl, peek, TICK
from selfaware.tools.experiments.streitkolben_messen import setze, warte_ticks, GOLD
from selfaware.tools.experiments.wege_abstand import kosten_nullen, kosten_zurueck
from selfaware.tools.experiments.arbeitsgang_messen import log_ab
from selfaware.tools.experiments.nahrung_messen import wegtest
from selfaware.macro.farmen_mischen import lies_karte
from selfaware.micro.tasks.waechter import schach
from selfaware.game.ucp.bauen import vorrat

D = os.path.join(_workspace.DATA)
SP = 1
# Art -> (Gebaeudetyp, Platzkarte, Ware, Ware-Nr am Markt, Arbeiter-Einheitstypen)
ARTEN = {"holz": (3, "holzfaeller", "holz", 2, {3: "Holzfaeller"}),
         "stein": (20, "steinbruch", "stein", 4, {7: "Steinmetz", 8: "Steinbrucharbeiter", 9: "Ochse"}),
         "eisen": (5, "eisenmine", "eisen", 6, {31: "Bergmann", 32: "Erztraeger"}),
         "hopfen": (31, "apfel", "hopfen", 3, {12: "Hopfenbauer"}),
         "pech": (6, "pech", "pech", 7, {10: "Pechgraeber"})}
VERKAUF_AB = 30      # ueber so viel Bestand einer gemessenen Ware ein Los verkaufen (Lagerteile frei halten)
GEB_BASIS, GEB_GROESSE = 0xF98520 + 0x14, 0x32C      # Gebaeude-Datensatz (Wissensstand 13t), 203 Worte
GEB_TYPEN = (3, 4, 5, 20, 21, 31, 6)   # Holzfaeller, Ochsenkarren, Eisenmine, Steinbruch, Steinhaufen, Hopfenfarm, Pechgraeber
GEB_ALLE = 50        # 01:26 (Daniel: "in der Mine selbst sind die ganzen Infos - lieber dort messen"): so oft je Betrieb den
                     # GANZEN Datensatz lesen; die Auswertung sucht, welche Worte sich aendern (Vorrat +0x184, Zeitgeber ...)
BAUM_ALLE = 2000     # 01:20 (Daniel: "wie viel ueberhaupt noch abgebaut werden kann"): so oft die Baumkarte lesen
BAUM_R = 25          # Baeume in diesem Umkreis um jeden Holzfaeller zaehlen (Holz-Rest +120 / voll +122 je Baum)


def baeume_lesen():
    """Alle Baeume mit Rest-Holz (Modulbefehl rohstoffkarte -> abzug/baeume.txt: nr art zustand x y stufe rest voll groesse)."""
    befehl({"rohstoffkarte": {}}, 8.0, bis="ROHSTOFF")
    z = open(os.path.join(kanal.ABZUG, "baeume.txt"), encoding="utf-8").read().splitlines()[1:]
    aus = []
    for r in z:
        f = r.split()
        if len(f) >= 8:
            aus.append(dict(art=int(f[1]), zustand=int(f[2]), x=int(f[3]), y=int(f[4]), stufe=int(f[5]), rest=int(f[6]),
                            voll=int(f[7])))
    return aus


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    dauer, tempo = int(arg.get("ticks", 12000)), int(arg.get("tempo", 300))
    arten = [a for a in arg.get("art", "holz,stein,eisen,hopfen").split(",") if a in ARTEN]
    abstaende = [int(x) for x in arg.get("abstaende", "10,30,50").split(",")]
    E.LEERE_KI = True
    E.GEGNER_ERWARTET = ""
    E.LIGA_GEFECHT = dict(E.LIGA_GEFECHT, ki=1)
    E.gefecht_starten(tempo)
    setze(GOLD, 20000)
    kosten_vorher = kosten_nullen()
    json.dump({str(a): v for a, v in kosten_vorher.items()},
              open(os.path.join(D, "kosten_sicherung_i%s.json" % os.environ.get("SHC_INSTANZ", "1")), "w"))
    erg = {"arten": arten, "abstaende": abstaende, "gebaeude": {}, "bestand": [], "arbeiter": {}, "verkauf": [],
           "ew": [], "stillstand": [], "lagerteile": [], "ladungen": []}
    waren = sorted({ARTEN[a][2] for a in arten})
    try:
        info = json.load(open(os.path.join(D, "start_M19.json"), encoding="utf-8"))
        K, F = tuple(info["bergfried_eingang"]), tuple(info["feind_bergfried"]["2"]["eingang"])
        eigen = lambda p: schach(p, K) < schach(p, F)
        teile = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == 10]
        lager = (teile[0]["x"], teile[0]["y"]) if teile else K
        erg["lager"] = lager
        # Lagerteile anbauen, bevor etwas geliefert wird (11.10. 17:22: volles Lager hielt die Arbeiter an)
        for i in range(2):
            erg["gebaeude"]["lager_anbau%d" % i] = E.baue_schnell(10, lager[0], lager[1], 12)
            warte_ticks(20)
        belegt = [(t["x"], t["y"]) for t in teile] + [p for k, p in erg["gebaeude"].items() if p]
        for art in arten:
            typ, kname, _, _, _ = ARTEN[art]
            pfad = os.path.join(D, "start_M19_platz_%s.txt" % kname)
            if not os.path.exists(pfad):
                erg["gebaeude"][art] = "keine Platzkarte %s" % os.path.basename(pfad)
                print("UEBERSPRUNGEN %s: %s fehlt" % (art, pfad), flush=True)
                continue
            # Lauf 3 (01:24): Stein/Eisen auch jenseits der Mitte (Gegner hat leere KI) - auf der eigenen Seite lagen alle
            # Plaetze 52-69 Felder weg, die Formel brauchte Spreizung. Holz nur, wo faellbare Baeume stehen (L69).
            plaetze = [p for p in lies_karte(pfad) if eigen(p) or art in ("stein", "eisen")]
            if art == "holz":
                b0 = baeume_lesen()
                dicht = lambda p: sum(1 for x in b0 if schach((x["x"], x["y"]), p) <= 15 and x["zustand"] == 2 and x["stufe"] < 4
                                      and x["rest"] > 0)
                plaetze = [p for p in plaetze if dicht(p) >= int(arg.get("baeume_min", 8))]
                erg["holz_plaetze_mit_baeumen"] = len(plaetze)
            for i, ab in enumerate(abstaende):
                kand = sorted([p for p in plaetze if all(schach(p, q) >= 8 for q in belegt)],
                              key=lambda p: abs(schach(p, lager) - ab))[:24]
                ort = next((o for o in (E.baue_schnell(typ, p[0], p[1], 2) for p in wegtest(kand)) if o), None)
                erg["gebaeude"]["%s%d" % (art, i)] = (ort, schach(ort, lager) if ort else None)
                if ort:
                    belegt.append(ort)
                    if art == "stein":         # je Steinbruch ein Ochsenkarren am Bruch (Abstand zum Lager zaehlt beim Ochsen)
                        o = E.baue_schnell(4, ort[0], ort[1], 10)
                        erg["gebaeude"]["ochse%d" % i] = o
                        if o:
                            belegt.append(o)
        hu = sorted(lies_karte(os.path.join(D, "start_M19_platz_huette.txt")), key=lambda p: schach(p, K))
        for i in range(6):
            frei = [p for p in hu if all(schach(p, q) >= 5 for q in belegt)][:30]
            o = next((x for x in (E.baue_schnell(1, p[0], p[1], 2) for p in frei[:6]) if x), None)
            erg["gebaeude"]["huette%d" % i] = o
            if o:
                belegt.append(o)
        # Lauf 2 fiel bei Tick 18.501 unter Beliebtheit 50 (Rationen keine) - jetzt normale Rationen, Kornspeicher am
        # Bergfried, Aepfel werden nachgekauft (Gold gesetzt), damit niemand abwandert
        erg["gebaeude"]["kornspeicher"] = E.baue_schnell(19, K[0], K[1], 15)
        warte_ticks(40)
        befehl({"spielbefehl": {"nr": 35, "werte": [2]}}, 1.0, bis="SPIELBEFEHL")     # Rationen normal
        befehl({"spielbefehl": {"nr": 34, "werte": [0]}}, 1.0, bis="SPIELBEFEHL")     # Steuer: Bestechung
        print("gebaut:", erg["gebaeude"], flush=True)
        arbeiter_typen = {}
        for a in arten:
            arbeiter_typen.update(ARTEN[a][4])
        nummern = {}
        for _ in range(80):
            L = E.runde_lesen()[1]
            nummern = {n: e["typ"] for n, e in L.items() if e["besitzer"] == SP and e["typ"] in arbeiter_typen}
            if len(nummern) >= sum(1 for k, v in erg["gebaeude"].items() if v and not k.startswith(("huette", "lager"))):
                break
            warte_ticks(25)
        erg["arbeiter"] = {str(n): arbeiter_typen[t] for n, t in nummern.items()}
        print("Arbeiter:", erg["arbeiter"], flush=True)
        letzte_ladung = {}

        def ew_ernten():
            erg["ew"] += [z.split("INFO|", 1)[-1] for z in log_ab("EINHEITWACHT: scharf")
                          if " EW " in z or "EW Orte" in z or "EW Tick" in z]
        befehl({"einheitwacht": {"nr": sorted(nummern), "alle": 2}}, 1.0, bis="EINHEITWACHT")
        k = W.holen(max(lager[0] - 80, 0), max(lager[1] - 80, 0), min(lager[0] + 80, 399), min(lager[1] + 80, 399))
        erg["wegkarte_fenster"] = [k["x0"], k["y0"], k["x1"], k["y1"]]
        t0 = peek(TICK)[0]
        still = {}
        erg["baeume"] = []
        erg["gebaeude_daten"] = {}          # Nr -> {"typ", "ort", "reihe": [(t, [203 Worte])]}
        geb_letzt = [-GEB_ALLE]
        holzfaeller = {k: v[0] for k, v in erg["gebaeude"].items() if k.startswith("holz") and v and v[0]}

        def baum_stich(t):
            b = baeume_lesen()
            erg["baeume"].append(dict(t=t, je_holzfaeller={k: dict(
                baeume=sum(1 for x in b if schach((x["x"], x["y"]), tuple(o)) <= BAUM_R and x["rest"] > 0),
                rest=sum(x["rest"] for x in b if schach((x["x"], x["y"]), tuple(o)) <= BAUM_R),
                faellbar=sum(1 for x in b if schach((x["x"], x["y"]), tuple(o)) <= BAUM_R and x["zustand"] == 2 and x["stufe"] < 4
                             and x["rest"] > 0)) for k, o in holzfaeller.items()}, alle_rest=sum(x["rest"] for x in b)))
            print("BAEUME Tick %d: %s" % (t, erg["baeume"][-1]["je_holzfaeller"]), flush=True)
        if holzfaeller:
            baum_stich(0)
        while peek(TICK)[0] - t0 < dauer:
            kanal.belege()
            v = vorrat(SP)
            st, L, G = E.runde_lesen()
            t = peek(TICK)[0] - t0
            erg["bestand"].append(dict({w: v.get(w, 0) for w in waren}, t=t, gold=v.get("gold"), beliebt=st.get("beliebt"),
                                       leute=st.get("leute")))
            if v.get("apfel", 0) < 20:          # Nahrung nachkaufen (Beliebtheit halten)
                kanal.sende({"befehle": [{"player": SP, "id": kanal.neue_id(), "spielbefehl": {"nr": 38, "werte": [0, 13]}}]},
                            1.0, bis="SPIELBEFEHL")
                erg.setdefault("nahrung_gekauft", []).append(t)
            for a in arten:                    # Lager frei halten; jeder Verkauf mit Bestand davor/danach
                ware, nr = ARTEN[a][2], ARTEN[a][3]
                if v.get(ware, 0) > VERKAUF_AB:
                    kanal.sende({"befehle": [{"player": SP, "id": kanal.neue_id(), "spielbefehl": {"nr": 38, "werte": [1, nr]}}]},
                                1.0, bis="SPIELBEFEHL")
                    warte_ticks(4)
                    v2 = vorrat(SP)
                    erg["verkauf"].append(dict(t=t, ware=ware, vorher=v.get(ware), nachher=v2.get(ware),
                                               gold=v2.get("gold", 0) - v.get("gold", 0)))
            neu = {n: e["typ"] for n, e in L.items() if e["besitzer"] == SP and e["typ"] in arbeiter_typen and n not in nummern}
            if neu:
                ew_ernten()
                nummern.update(neu)
                erg["arbeiter"].update({str(n): "%s (ab Tick %d)" % (arbeiter_typen[ty], t) for n, ty in neu.items()})
                befehl({"einheitwacht": {"nr": sorted(nummern), "alle": 2}}, 1.0, bis="EINHEITWACHT")
            for n in nummern:
                e = L.get(n)
                if not e:
                    continue
                if letzte_ladung.get(n) != (e.get("zustand"), e.get("ladung")):
                    letzte_ladung[n] = (e.get("zustand"), e.get("ladung"))
                    erg["ladungen"].append((t, n, e["typ"], e.get("zustand"), e.get("ladung"), (e["x"], e["y"])))
                ort = (e["x"], e["y"])
                vo = still.get(n)
                if not vo or vo[0] != ort:
                    still[n] = (ort, t, False)
                elif t - vo[1] >= 1500 and not vo[2]:
                    s = {"nr": n, "wer": arbeiter_typen.get(e["typ"]), "seit": vo[1], "t": t, "ort": ort,
                         "zustand": e.get("zustand"), "ladung": e.get("ladung")}
                    erg["stillstand"].append(s)
                    still[n] = (ort, vo[1], True)
                    print("STILLSTAND:", s, flush=True)
            if t - geb_letzt[0] >= GEB_ALLE:
                geb_letzt[0] = t
                for g_nr, gx in G.items():
                    if gx["besitzer"] == SP and gx["typ"] in GEB_TYPEN:
                        e = erg["gebaeude_daten"].setdefault(str(g_nr), {"typ": gx["typ"], "ort": (gx["x"], gx["y"]), "reihe": []})
                        e["reihe"].append((t, peek(GEB_BASIS + int(g_nr) * GEB_GROESSE, GEB_GROESSE // 4)))
            if holzfaeller and t // BAUM_ALLE != erg["baeume"][-1]["t"] // BAUM_ALLE:
                baum_stich(t)
            if t // 500 != (erg["lagerteile"][-1][0] // 500 if erg["lagerteile"] else -1):
                erg["lagerteile"].append((t, [(int(g), peek(0xF98520 + 0x14 + int(g) * 0x32C + 0x184, 2))
                                              for g, x in G.items() if x["besitzer"] == SP and x["typ"] == 10]))
            if st.get("beliebt", 10000) < 5000:
                erg["ungueltig"] = "Beliebtheit %s unter 50 bei Tick %d" % (st.get("beliebt"), t)
                print("ABBRUCH:", erg["ungueltig"], flush=True)
                break
            warte_ticks(int(arg.get("stich", 100)))
        befehl({"einheitwacht": False}, 1.0, bis="EINHEITWACHT")
        ew_ernten()
        print("EW-Zeilen:", len(erg["ew"]), "| Verkaeufe:", len(erg["verkauf"]), "| Stillstaende:", len(erg["stillstand"]),
              flush=True)
    finally:
        pfad = os.path.join(D, "arbeitsgang_rohstoff_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
        json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
        try:
            kosten_zurueck(kosten_vorher)
        finally:
            befehl({"pause": True}, 0.5)
        import shutil
        try:
            shutil.copy(os.path.join(kanal.ABZUG, "wegkarte.txt"), pfad.replace(".json", "_wegkarte.txt"))
        except OSError:
            pass
        print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
