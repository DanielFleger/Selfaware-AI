# -*- coding: utf-8 -*-
"""M4.03 Was nach dem Lord-Tod passiert: Spielende-Merker und Verzoegerung bis zum Endbildschirm.

Abgelesen (research/native/dekomp_spielende.c): checkSkirmishGameDefeat (0x00486600, aus processGameTick)
setzt, sobald hoechstens ein Team noch einen lebenden Lord hat, sofort
  MapAndTime.gameOver     (0x0117D500) = 1
  MapAndTime.gameOverTime (0x0117C888) = timeGetTime()   <- Rechneruhr in ms, nicht Ticks
  MapAndTime.playerIsAlive[9] (short, ab 0x0117EF40)
und blendet das Sieg/Niederlage-Fenster ein.

Vorher festgelegt: Ist die Verzoegerung bis zum Endbildschirm (Ansicht 30) eine feste Zeit in
Sekunden, muss sie bei Tempo 300 in Ticks auf etwa ein Drittel von Tempo 1000 schrumpfen und
in Millisekunden gleich bleiben. Bleibt sie in Ticks gleich, ist das widerlegt.

Aufruf:  uv run python -m selfaware.tools.experiments.spielende
"""

from selfaware import workspace as _workspace
import ctypes, io, json, os, sys, time

from selfaware.game.ucp.laden import lade_stand, befehl, peek, TICK
from selfaware.tools.experiments.lordduell import bild

STAND = "M4-04 Lordduell Treffer T3354"
GAMEOVER, GAMEOVERZEIT, LEBT, ANSICHT = 0x0117D500, 0x0117C888, 0x0117EF40, 0x01FE7D1C
uhr = ctypes.windll.winmm.timeGetTime

def lebt():
    w = peek(LEBT, 5)
    b = b"".join(x.to_bytes(4, "little") for x in w)[:18]
    return [int.from_bytes(b[i:i + 2], "little") for i in range(0, 18, 2)]

def lauf(tempo):
    lade_stand(STAND, mit_bild=False)
    r = {"tempo": tempo, "vorher": {"gameOver": peek(GAMEOVER)[0], "lebt": lebt()}}
    befehl({"tempo": tempo}, 0.8)
    befehl({"pause": False}, 0.3)
    ende = time.time() + 120
    while time.time() < ende:
        if "gameOver_tick" not in r and peek(GAMEOVER)[0] == 1:
            r.update(gameOver_tick=peek(TICK)[0], gameOver_uhr=uhr(), gameOverTime=peek(GAMEOVERZEIT)[0], lebt=lebt())
            print("  Spiel vorbei gesetzt: Tick %d, Spieluhr %d, lebt %s" % (r["gameOver_tick"], r["gameOverTime"], r["lebt"]), flush=True)
            bild("sieg_fenster_tempo%d" % tempo)
        a = peek(ANSICHT)[0]
        if a == 30:
            r.update(ende_tick=peek(TICK)[0], ende_uhr=uhr())
            break
        time.sleep(0.2)
    if "ende_tick" in r and "gameOverTime" in r:
        r["abstand_ticks"] = r["ende_tick"] - r["gameOver_tick"]
        r["abstand_ms"] = (r["ende_uhr"] - r["gameOverTime"]) & 0xFFFFFFFF
        print("  Endbildschirm: Tick %d -> %d Ticks und %d ms nach 'Spiel vorbei'" % (
            r["ende_tick"], r["abstand_ticks"], r["abstand_ms"]), flush=True)
    return r

def main():
    erg = [lauf(1000), lauf(300)]
    io.open(os.path.join(_workspace.DATA, 'spielende_%s.json' % time.strftime('%H%M%S')),
            "w", encoding="utf-8").write(json.dumps(erg, indent=1))
    a, b = erg
    if "abstand_ms" in a and "abstand_ms" in b:
        print("Tempo 1000: %d Ticks / %d ms | Tempo 300: %d Ticks / %d ms" % (
            a["abstand_ticks"], a["abstand_ms"], b["abstand_ticks"], b["abstand_ms"]))
        q = b["abstand_ticks"] / float(a["abstand_ticks"])
        print("URTEIL:", "feste ZEIT (Ticks schrumpfen auf %.2f)" % q if q < 0.6 else "WIDERLEGT - Ticks schrumpfen nicht (%.2f)" % q)

if __name__ == "__main__":
    main()
