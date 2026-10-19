# -*- coding: utf-8 -*-
"""Messumgebung mit voller Beliebtheit (Daniel 06.10. 20:41: "waere es nicht sinnvoll, die Beliebtheit auf 100 zu halten?
also einfach dauerhaft Essen kaufen, damit es nicht verfaelscht wird ... mit 0 Beliebtheit sinkt die Bevoelkerung auf
minimum 4 und die Gebaeude werden gar nicht besetzt"). Gemessen am Ende der Aufbau-Messung 20:40: Beliebtheit 0, Leute 4,
Wohnplatz 10, 0 Kuehe in 12.000 Ticks.

vorbereiten(): Kornspeicher + Huetten (Wohnplatz), je Essenssorte Brot/Kaese/Fleisch/Aepfel kaufen (Vielfalt, Liga +125),
Rationen doppelt (Spielbefehl 35, Liga +250), Steuerstufe 0 = Bestechung (Spielbefehl 34, Liga +225),
Beliebtheit zum Start auf 100 setzen (wie das Gold - nur in Messpartien).
pflegen(): Essen nachkaufen, wenn eine Sorte unter MINDEST faellt; gibt Beliebtheit, Leute, Wohnplatz zurueck.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.runtime.live.erstes_spiel as E
from selfaware.game.ucp.laden import befehl
from selfaware.tools.experiments.streitkolben_messen import warte_ticks

SP = 1
PD = 0x0115BDF8 + SP * 0x39F4                   # Spielerdaten (erstes_spiel.PD), +0x60 Beliebtheit x 100
ESSEN = {"brot": 10, "kaese": 11, "fleisch": 12, "apfel": 13}
MINDEST = 15
KORNSPEICHER, HUETTE = 19, 1


def kaufen(ware, lose=1):
    for _ in range(lose):
        befehl({"spielbefehl": {"nr": 38, "werte": [0, ware]}}, 1.0, bis="SPIELBEFEHL")


def vorbereiten(lx, ly, huetten=4):
    """Erst nach Lager-Anbau und Markt aufrufen (Kaufen braucht den Markt). Gibt eine Liste der Schritte."""
    schritte = [("kornspeicher", E.baue_schnell(KORNSPEICHER, lx, ly, 14))]
    warte_ticks(6)
    for _ in range(huetten):
        schritte.append(("huette", E.baue_schnell(HUETTE, lx, ly, 22)))
        warte_ticks(4)
    for ware in ESSEN.values():
        kaufen(ware, 4)
    befehl({"spielbefehl": {"nr": 35, "werte": [4]}}, 1.0, bis="SPIELBEFEHL")     # Rationen doppelt
    befehl({"spielbefehl": {"nr": 34, "werte": [0]}}, 1.0, bis="SPIELBEFEHL")     # Bestechung
    befehl({"poke": PD + 0x60, "wert": 10000}, 0.5, bis="POKE")                   # Beliebtheit 100
    schritte.append(("essen", {k: 20 for k in ESSEN}))
    return schritte


def pflegen(st=None):
    """st = Status aus E.runde_lesen()[0] (sonst neu gelesen). Kauft nach, was unter MINDEST liegt."""
    st = st or E.runde_lesen()[0]
    for name, ware in ESSEN.items():
        if st.get(name, 0) < MINDEST:
            kaufen(ware, 2)
    return {"beliebt": st.get("beliebt", 0) / 100.0, "leute": st.get("leute"), "platz": st.get("platz")}
