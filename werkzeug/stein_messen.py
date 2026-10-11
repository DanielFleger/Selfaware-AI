# -*- coding: utf-8 -*-
"""Kontrollierter Pruefstand fuer Steinbruch -> Haufen -> Ochse -> Lager.

Variiert werden nur Lagerweg und Zahl der Ochsenjoche. Gold wird gesetzt; Holz,
Gebaeude, Arbeiter, Steinproduktion, Transport und Verkauf laufen echt im Spiel.

Aufruf:
  python werkzeug/stein_messen.py lager=91,268 joche=1 ticks=14000 tempo=300
  python werkzeug/stein_messen.py lager=142,311 joche=2 ticks=18000 tempo=300
"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import befehl as kanal
import erstes_spiel as E
import messumgebung as M
from bauen import vorrat
from laden import befehl, peek, TICK
from lageprotokoll import Lageprotokoll
from streitkolben_messen import baue_und_warte, eigene, setze, warte_ticks

D = os.path.join(HIER, "..", "daten")
SP = 1
GOLD, HOLZ, STEIN = 15, 2, 4
LAGER, MARKT, STEINBRUCH, HAUFEN, JOCH = 10, 26, 20, 21, 4
STEINMETZ, OCHSE = 7, 9


def kaufe(art, lose):
    for _ in range(lose):
        befehl({"spielbefehl": {"nr": 38, "werte": [0, art]}}, 1.0, bis="SPIELBEFEHL")


def verkaufe_stein(erg):
    vorher = vorrat(SP)
    befehl({"spielbefehl": {"nr": 38, "werte": [1, STEIN]}}, 1.0, bis="SPIELBEFEHL")
    warte_ticks(3)
    nachher = vorrat(SP)
    menge = max(0, vorher.get("stein", 0) - nachher.get("stein", 0))
    if menge:
        erg["verkauft"] += menge
        erg["verkaufsvorgaenge"].append({"t": peek(TICK)[0], "menge": menge,
                                          "gold": nachher.get("gold", 0) - vorher.get("gold", 0)})
    return menge


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    lager_ziel = tuple(int(v) for v in arg.get("lager", "91,268").split(","))
    joch_zahl = int(arg.get("joche", 1))
    dauer, tempo = int(arg.get("ticks", 14000)), int(arg.get("tempo", 300))
    if joch_zahl not in (1, 2, 3):
        raise SystemExit("joche muss 1, 2 oder 3 sein")

    stempel = time.strftime("%Y%m%d_%H%M%S")
    E.LEERE_KI = True
    E.gefecht_starten(tempo)
    setze(GOLD, 20000)
    erg = {"start": stempel, "lager_ziel": list(lager_ziel), "joche_soll": joch_zahl,
           "ticks_soll": dauer, "bauten": [], "proben": [], "verkauft": 0, "verkaufsvorgaenge": []}

    # Das alte Lager wird komplett ersetzt. Drei neue Bloecke lassen Holz und spaeter Stein gleichzeitig physisch zu.
    for nr in list(eigene(LAGER)):
        befehl({"abreissen": {"nr": nr}}, 0.8, bis="ABREISSEN")
    warte_ticks(10)
    l1 = baue_und_warte(LAGER, lager_ziel[0], lager_ziel[1], 10, erg["bauten"], "Vorratslager")
    if not l1["nr"]:
        raise SystemExit("ABBRUCH: Vorratslager nicht gebaut")
    lx, ly = l1["x"], l1["y"]
    baue_und_warte(LAGER, lx, ly, 9, erg["bauten"], "Lagerblock 2")
    baue_und_warte(LAGER, lx, ly, 11, erg["bauten"], "Lagerblock 3")

    # Markt, Kornspeicher und Haeuser bleiben aus dem Stein-/Lagerkorridor heraus.
    service = (E.BERGFRIED[0] - 25, E.BERGFRIED[1] - 20)
    markt = baue_und_warte(MARKT, service[0], service[1], 25, erg["bauten"], "Markt ausserhalb Steinkette")
    if not markt["nr"]:
        raise SystemExit("ABBRUCH: Markt nicht gebaut")
    kaufe(HOLZ, 30)
    warte_ticks(10)

    # Derselbe Steinbruch in allen Varianten; nur Lagerweg und Jochzahl duerfen sich aendern.
    bruch = baue_und_warte(STEINBRUCH, 80, 265, 1, erg["bauten"], "Steinbruch")
    if not bruch["nr"]:
        raise SystemExit("ABBRUCH: Steinbruch nicht gebaut")
    joch_ziele = [(87, 263), (85, 259), (87, 269)]
    for i, (x, y) in enumerate(joch_ziele[:joch_zahl], 1):
        j = baue_und_warte(JOCH, x, y, 3, erg["bauten"], "Ochsenjoch %d" % i)
        if not j["nr"]:
            raise SystemExit("ABBRUCH: Ochsenjoch %d nicht gebaut" % i)

    erg["messumgebung"] = M.vorbereiten(service[0], service[1], huetten=8)
    # Wirkliche Erreichbarkeit aus den Gebaeudedaten, nicht bloss ein erfolgreicher Baubefehl.
    G = E.runde_lesen()[2]
    pflicht = [(nr, g) for nr, g in G.items() if g["besitzer"] == SP and g["typ"] in (LAGER, STEINBRUCH, HAUFEN, JOCH)]
    erg["zugang"] = [{"nr": nr, "typ": g["typ"], "ort": [g["x"], g["y"]],
                       "erreichbar": bool(g.get("erreichbar"))} for nr, g in pflicht]
    if not pflicht or not all(g["erreichbar"] for g in erg["zugang"]):
        raise SystemExit("ABBRUCH: mindestens ein Teil der Steinkette ist nicht erreichbar")

    lage = Lageprotokoll(os.path.join(D, "lage_stein_%s_i%d.jsonl.gz" % (stempel, E.INSTANZ)))
    erg["lageprotokoll"] = lage.pfad
    t0, runde = peek(TICK)[0], 0
    erg["t_messbeginn"] = t0
    while peek(TICK)[0] - t0 < dauer:
        st, L, G = E.runde_lesen()
        if st:
            lage.schreibe(st)
        runde += 1
        if runde % 20 == 0:
            M.pflegen(st)
        if runde % 10 == 0:
            v = vorrat(SP)
            while v.get("stein", 0) >= 40:
                if not verkaufe_stein(erg):
                    raise SystemExit("ABBRUCH: Steinlager voll und Verkauf fehlgeschlagen")
                v = vorrat(SP)
            probe = {"t": st.get("t"), "stein": v.get("stein"), "gold": v.get("gold"),
                     "steinmetze": sum(1 for e in L.values() if e["besitzer"] == SP and e["typ"] == STEINMETZ),
                     "ochsen": sum(1 for e in L.values() if e["besitzer"] == SP and e["typ"] == OCHSE),
                     "verkauft": erg["verkauft"]}
            erg["proben"].append(probe)
            print("PROBE", probe, flush=True)

    befehl({"pause": True}, 0.5)
    erg["t_ende"] = peek(TICK)[0]
    pfad = os.path.join(D, "stein_messung_%s.json" % stempel)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(erg, f, ensure_ascii=False, indent=1)
    print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
