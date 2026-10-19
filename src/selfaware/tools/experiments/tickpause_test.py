# -*- coding: utf-8 -*-
"""Wie genau haelt { "tickpause": ... } an? Misst Ziel-Tick gegen tatsaechlichen Tick.

1) Pause bei Tick 1 eines neuen Selbstspiels.
2) Je Tempo (100, 1000) dreimal "alle 100 Ticks": Ziel, Tick beim Anhalten
   (Logzeile des Waechters) und Tick danach (ZEIT) - die Differenz zeigt, ob
   nach dem Pausenbefehl noch Ticks im selben Bild durchlaufen.

Aufruf:  uv run python -m selfaware.tools.experiments.tickpause_test
"""
import os, re, sys, time

from selfaware.game.ucp.befehl import sende

def zeit():
    m = re.search(r"Tick (\d+)", " ".join(sende({"player": 1, "zeit": True}, 1.0)))
    return int(m.group(1)) if m else None

def pausen(zeilen):
    return [(int(a), int(b)) for a, b in re.findall(r"TICKPAUSE: angehalten bei Tick (\d+) \(Ziel (\d+)", " ".join(zeilen))]

print("== 1) Pause bei Tick 1 eines neuen Spiels ==")
sende({"player": 1, "menue": 41}, 3)
print("  ", sende({"player": 1, "tickpause": {"bei": 1}}, 1.0))
sende({"player": 1, "pause": False}, 1.0)
z = sende({"eigenesGefecht": True, "selbstspiel": True, "karte": "Liga_Grumpy Neighbors", "ki": 1, "gegner": 2}, 5)
print("   Waechter:", pausen(z), "| Tick jetzt:", zeit())

for tempo in (100, 1000):
    t = zeit()
    print("== 2) alle 100 Ticks bei Tempo %d (Start bei Tick %s) ==" % (tempo, t))
    sende({"player": 1, "tickpause": {"bei": t + 100, "alle": 100, "bis": t + 300}}, 1.0)
    sende({"player": 1, "tempo": tempo}, 0.8)
    for runde in range(3):
        z = sende({"player": 1, "pause": False}, max(2.0, 150 / tempo + 1.0))
        jetzt = zeit()
        for bei, ziel in pausen(z):
            print("   Ziel %d | angehalten bei %d (+%d) | Tick danach %s (+%s)" % (
                ziel, bei, bei - ziel, jetzt, (jetzt - ziel) if jetzt is not None else "?"))
sende({"player": 1, "tempo": 100}, 0.8)
print("Ende: Spiel steht pausiert, Tempo 100.")
