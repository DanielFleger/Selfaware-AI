# -*- coding: utf-8 -*-
"""Plan aus aufbau_planer.py im Spiel bauen und messen (Daniel 06.10. 20:29: "wenn alles maximal effektiv geht nach
Theorie, baue es im Spiel ... erst 5 von beidem, dann 15, dann 30").

Messpartie, KEIN Benchmark ab Tick 0: Gold gesetzt, Baukosten 0 (Rueckweg im finally), Eisen am Markt gekauft.
Ablauf: Lager erweitern und Markt ZUERST (Messpartie 5: sonst sperrt der Aufbau den Anbau), Wegkarte lesen, planen,
Waffenlager/Schmieden/Gerbereien genau nach Plan (Ort + Richtung), Milchviehhoefe per Platzsuche nahe den Gerbereien,
Eisen kaufen, Schmieden auf Keulen. Dann mitschreiben: alle Arbeiter (einheitwacht alle 2 Ticks), Kuehe (Typ 51) und
Bestand alle 50 Ticks.
Vergleich danach: gemessener Rundgang je Schmiede gegen den geplanten (arbeitsgang_auswerten + plan in der Datei).
Aufruf: uv run python -m selfaware.tools.experiments.aufbau_bauen [n=5] [ticks=12000] [hoefe=3] [tempo=300] [lager=x,y] [kaserne=x,y]
"""

from selfaware import workspace as _workspace
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.game.ucp.befehl as kanal
import selfaware.runtime.live.erstes_spiel as E
import selfaware.services.wegkarte as W
import selfaware.macro.aufbau_planer as P
from selfaware.game.ucp.laden import befehl, peek, TICK
from selfaware.tools.experiments.streitkolben_messen import setze, bestand, warte_ticks, GOLD, EISEN, KEULE
from selfaware.tools.experiments.wege_abstand import kosten_nullen, kosten_zurueck, ART
from selfaware.tools.experiments.arbeitsgang_messen import log_ab
import selfaware.tools.experiments.messumgebung as M

D = os.path.join(_workspace.DATA)
SP = 1
MAPPER = {P.WAFFENLAGER: 81, P.SCHMIEDE: 83, P.GERBEREI: 85}
ARBEITER = {19: "Schmied", 21: "Gerber", 14: "Milchbauer"}


def neue(typ, vorher):
    return {nr: g for nr, g in E.runde_lesen()[2].items() if g["besitzer"] == SP and g["typ"] == typ and nr not in vorher}


def main():
    """Runde 2 (06.10. 20:48): Eisenteil auslesen, Hoefe + Kaserne vor dem Planen, laufend anwerben."""
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    n, dauer, hoefe, tempo = int(arg.get("n", 5)), int(arg.get("ticks", 12000)), int(arg.get("hoefe", 3)), int(arg.get("tempo", 300))
    E.LEERE_KI = True
    E.gefecht_starten(tempo)
    setze(GOLD, 20000)
    alt = kosten_nullen()
    stempel = time.strftime("%Y%m%d_%H%M%S")
    erg = {"n": n, "runde": 2, "kosten_alt": {"0x%08X" % a2: v for a2, v in alt.items()}, "bestand": [], "kuehe": [],
           "gebaut": [], "kaempfer": []}
    try:
        G0 = E.runde_lesen()[2]
        teile = [g for g in G0.values() if g["besitzer"] == SP and g["typ"] == P.LAGER]
        lx, ly = teile[0]["x"], teile[0]["y"]
        if "lager" in arg:                                    # Runde 3 (Daniel 20:48): Lager versetzen
            for nr in [nr for nr, g in G0.items() if g["besitzer"] == SP and g["typ"] == P.LAGER]:
                befehl({"abreissen": {"nr": nr}}, 0.6, bis="ABREISSEN")
            warte_ticks(5)
            lx, ly = map(int, arg["lager"].split(","))
            befehl({"baue": {"mapper": 52, "x": lx, "y": ly, "groesse": 5, "richtung": 0}}, 0.8, bis="BAUE")
            warte_ticks(6)
            neu_teile = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == P.LAGER]
            erg["lager_versetzt"] = {"nach": [lx, ly], "teile": len(neu_teile), "alt": [teile[0]["x"], teile[0]["y"]]}
            print("Lager versetzt nach", (lx, ly), "-", len(neu_teile), "Teile", flush=True)
            if not neu_teile:
                raise RuntimeError("neues Lager nicht gebaut")
        for typ, r in ((P.LAGER, 8), (26, 20)):              # 1. Lager anbauen und Markt zuerst
            erg["gebaut"].append(["vorab", typ, E.baue_schnell(typ, lx, ly, r)])
            warte_ticks(8)
        for _ in range(6):                                    # 2. 30 Eisen - in welches Teil faellt es?
            befehl({"spielbefehl": {"nr": 38, "werte": [0, EISEN]}}, 1.0, bis="SPIELBEFEHL")
        warte_ticks(5)
        G = E.runde_lesen()[2]
        eisen_teil = next((nr for nr, g in G.items() if g["typ"] == P.LAGER and g.get("ware") == EISEN), None)
        erg["eisen_teil"] = eisen_teil
        erg["lagerteile"] = {nr: [g["x"], g["y"], g.get("ware"), g.get("vorrat")] for nr, g in G.items() if g["typ"] == P.LAGER}
        print("Eisen liegt in Lagerteil", eisen_teil, erg["lagerteile"], flush=True)
        vor = set(G)                                          # 3. Hoefe (Gruenland) und Kaserne vor dem Planen
        for _ in range(hoefe):
            E.baue_schnell(33, lx, ly, 45)
            warte_ticks(8)
        hof = neue(33, vor)
        erg["hoefe"] = {nr: [g["x"], g["y"]] for nr, g in hof.items()}
        kx, ky = map(int, arg["kaserne"].split(",")) if "kaserne" in arg else (lx - 12, ly + 12)
        E.baue_schnell(9, kx, ky, 25)
        warte_ticks(8)
        kas = neue(9, vor)
        kaserne = min(kas) if kas else None
        erg["kaserne"] = {nr: [g["x"], g["y"]] for nr, g in kas.items()}
        print("Hoefe", erg["hoefe"], "Kaserne", erg["kaserne"], flush=True)
        xs = [lx] + [g["x"] for g in hof.values()]
        ys = [ly] + [g["y"] for g in hof.values()]
        k = W.holen(max(min(xs) - 25, 0), max(min(ys) - 25, 0), min(max(xs) + 25, 399), min(max(ys) + 25, 399))
        plan, bericht = P.plane(k, n, n, eisen_teil, [tuple(v) for v in erg["hoefe"].values()])   # 4. planen + bauen
        erg["plan"] = bericht
        P.zeichne_plan(plan, os.path.join(D, "aufbau_%s_plan.png" % stempel), "Plan Runde 2: %d+%d" % (n, n))
        for art, x, y, r, e in plan.bauten:
            befehl({"baue": {"mapper": MAPPER[art], "x": x, "y": y, "groesse": 4, "richtung": r}}, 0.8, bis="BAUE")
            warte_ticks(3)
        warte_ticks(5)
        k2 = W.holen(k["x0"], k["y0"], k["x1"], k["y1"])
        steht = [1 for art, x, y, r, e in plan.bauten if k2["f"].get((x, y), (0,) * 6)[5] == art]
        erg["plan_gebaut"] = "%d von %d" % (len(steht), len(plan.bauten))
        for s2 in bericht["schmiede"] + bericht["gerber"]:
            print("  geplant", s2.get("ort"), "R", s2.get("richtung"), "Gang", s2.get("gang_felder"), "Zyklus", s2.get("zyklus_ticks"))
        print("Plan gebaut: %s" % erg["plan_gebaut"], flush=True)
        bx0 = min(x for _, x, _, _, _ in plan.bauten)            # 5. Messumgebung abseits
        by1 = max(y for _, _, y, _, _ in plan.bauten)
        erg["messumgebung"] = M.vorbereiten(bx0 - 10, by1 + 10)
        warte_ticks(10)
        k4 = W.holen(k["x0"], k["y0"], k["x1"], k["y1"])
        p4 = P.Plan(k4)
        we = next(e for art, x, y, r, e in plan.bauten if art == P.WAFFENLAGER)
        dw = p4.abstand(we)
        erg["eingaenge_unerreichbar"] = [e for art, x, y, r, e in plan.bauten if e not in dw]
        print("Eingaenge unerreichbar:", erg["eingaenge_unerreichbar"] or "keine", flush=True)
        G = E.runde_lesen()[2]
        for nr, g in G.items():
            if g["besitzer"] == SP and g["typ"] == P.SCHMIEDE:
                befehl({"spielbefehl": {"nr": 33, "werte": [nr, KEULE, g.get("uid", 0)]}}, 1.0, bis="SPIELBEFEHL")
        erg["gebaeude_liste"] = {nr: g for nr, g in G.items() if g["besitzer"] == SP}
        nummern = {}
        for _ in range(80):                                   # Arbeiter abwarten
            L = E.runde_lesen()[1]
            nummern = {u: e["typ"] for u, e in L.items() if e["besitzer"] == SP and e["typ"] in ARBEITER}
            if sum(1 for t in nummern.values() if t == 19) >= n and sum(1 for t in nummern.values() if t == 21) >= n                     and sum(1 for t in nummern.values() if t == 14) >= hoefe:
                break
            M.pflegen()
            warte_ticks(30)
        erg["arbeiter"] = {str(u): ARBEITER[t] for u, t in nummern.items()}
        print("Arbeiter:", sorted(erg["arbeiter"].values()), flush=True)
        befehl({"einheitwacht": {"nr": sorted(nummern), "alle": 2}}, 1.0, bis="EINHEITWACHT")
        t0 = peek(TICK)[0]
        erg["t0"] = t0
        while peek(TICK)[0] - t0 < dauer:                     # 6. messen und laufend anwerben
            b = bestand()
            erg["bestand"].append({k3: b[k3] for k3 in ("t", "keule", "leder", "eisen", "gold")})
            erg["kuehe"].append([b["t"], b["einheiten"].get("T51", 0)])
            erg["kaempfer"].append([b["t"], b["kaempfer"]])
            if kaserne and b["keule"] and b["leder"] and (b.get("feuer") or 0) > 0:
                befehl({"werbe": {"typ": 26, "gebaeude": kaserne}}, 1.0, bis="WERBE")
            if len(erg["bestand"]) % 10 == 0:
                erg.setdefault("beliebt", []).append([b["t"], M.pflegen()])
            warte_ticks(50)
        befehl({"einheitwacht": False}, 1.0, bis="EINHEITWACHT")
        erg["ew"] = [z.split("INFO|", 1)[-1] for z in log_ab("EINHEITWACHT: scharf") if "EW " in z]
        k3 = W.holen(k["x0"], k["y0"], k["x1"], k["y1"])
        W.zeichnen(k3, os.path.join(D, "aufbau_%s_spiel.png" % stempel), W.gebaeude_typen_aus(k3, {}), zelle=12,
                   titel="Aufbau Runde 2 %d+%d im Spiel (Ende)" % (n, n))
        print("Ende: Bestand", erg["bestand"][-1], "Kaempfer", erg["kaempfer"][-1], "Beliebtheit",
              [x[1]["beliebt"] for x in erg.get("beliebt", [])][::4], flush=True)
    finally:
        kosten_zurueck(alt)
        befehl({"pause": True}, 0.5)
        pfad = os.path.join(D, "aufbau_%s.json" % stempel)
        json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
        import shutil
        shutil.copy(os.path.join(kanal.ABZUG, "wegkarte.txt"), pfad.replace(".json", "_wegkarte.txt"))
        print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
