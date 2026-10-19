# -*- coding: utf-8 -*-
"""Welche Speicherstelle stoppt die KI der Ratte MITTEN in der Partie, ohne sie zu beenden? (19.10. 20:20)

Anlass: Daniels erste Lobby-Partie gegen SamurAI (20:16:43) - samurai_wache setzte bei laufendem Spiel alle drei Stellen aus
ki_aus (currentAIArray[2] = 0, PlayerData.aiType = 0, Mensch-Eintrag = 1); 3 s spaeter gameOver, "Samurai gewinnt". Im 1v1 lief
dasselbe nur bei startpause vor dem ersten Takt.

VORHER FESTGELEGT je Variante (eigenes Gefecht Grumpy Neighbors, Ratte = KI 1 auf Spieler 2, Tempo 100):
  bei Tick >= 400 Gebaeude von Spieler 2 zaehlen, Variante setzen, 3.000 Takte laufen lassen.
  BRAUCHBAR = gameOver bleibt 0 UND Spieler 2 baut danach hoechstens 1 Gebaeude dazu (die KI steht).
  Kontrolle "keine": ohne Eingriff baut die Ratte in 3.000 Takten mehr als 1 Gebaeude (sonst misst die Probe nichts).
Aufruf (Instanz frei, samurai_wache angehalten): SHC_INSTANZ=4 python werkzeug/uebernahme_probe.py [varianten=keine,ai,typ,mensch]"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import befehl as kanal
from laden import befehl, peek
from steuerkarte import tick

D = os.path.join(HIER, "..", "daten")
SP = 2
STELLEN = {"ai": (0x0191DE7C + SP * 4, 0), "typ": (0x0115BDF8 + SP * 0x39F4 + 0x2300, 0), "mensch": (0x0191DE10 + SP * 4, 1)}
GEFECHT = {"eigenesGefecht": True, "karte": "Liga_Grumpy Neighbors", "ki": 1, "gegner": 1, "ausgleich": 3,
           "startliste": [0, 1, 246, 246, 246, 246, 246, 246]}


def gebaeude_sp2():
    from waechter import lies_gebaeude
    befehl({"lagebild": True}, 1.0)
    return sum(1 for g in lies_gebaeude().values() if g["besitzer"] == SP)


def warte_tick(ziel, sek=240):
    ende = time.time() + sek
    while time.time() < ende:
        t = tick() or 0
        if t >= ziel or peek(0x0117D500)[0]:
            return t
        time.sleep(0.3)
    return tick()


def versuch(variante):
    from serie import zuruecksetzen
    print("Zuruecksetzen:", zuruecksetzen(), flush=True)
    befehl({"tempo": 100}, 1.0, bis="TEMPO")
    kanal.sende({"player": 1, "pause": False}, 0.5)
    kanal.sende(GEFECHT, 4, bis="LaunchSkirmishGame zurueck")
    befehl({"tempo": 100}, 1.0, bis="TEMPO")
    befehl({"pause": False}, 0.5)
    t0 = warte_tick(400)
    ai = [peek(0x0191DE7C + s * 4)[0] for s in range(0, 9)]
    vor = gebaeude_sp2()
    for name in ([] if variante == "keine" else variante.split("+")):
        adr, wert = STELLEN[name]
        befehl({"poke": adr, "wert": wert}, 1.0, bis="POKE")
    t1 = tick() or 0
    t_end = warte_tick(t1 + 3000)
    vorbei = peek(0x0117D500)[0]
    nach = gebaeude_sp2() if not vorbei else None
    erg = {"variante": variante, "ai_array": ai, "tick_eingriff": t1, "tick_ende": t_end, "gameover": vorbei,
           "gebaeude_sp2": [vor, nach], "brauchbar": (not vorbei) and nach is not None and nach - vor <= 1}
    print("VARIANTE %-12s gameOver %s, Gebaeude Spieler 2 %s -> %s (Tick %s -> %s), KI-Feld %s => %s" % (
        variante, vorbei, vor, nach, t1, t_end, ai, "BRAUCHBAR" if erg["brauchbar"] else "nein"), flush=True)
    return erg


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    alle = []
    for v in arg.get("varianten", "keine,ai,typ,mensch").split(","):
        alle.append(versuch(v))
    befehl({"pause": True}, 0.5)
    pfad = os.path.join(D, "uebernahme_probe_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
    json.dump(alle, open(pfad, "w", encoding="utf-8"), ensure_ascii=False)
    print("gesichert:", pfad)


if __name__ == "__main__":
    main()
