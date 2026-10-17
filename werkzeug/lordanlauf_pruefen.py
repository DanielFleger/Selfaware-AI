# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel: Lord-Anlauf OHNE Sammelpunkt (12.10. 01:48; Daniel 00:49 "nicht an einem Punkt sammeln, Hauptsache
sie kommen ca. gleich schnell an", 01:42 "warum sammeln sich wieder Assassinen in einem Klump?"). Bedarf hier fest 20.
Vorher festgelegt:
  1. Tick 9.000 (erstes Jahr), 25 Assassinen: KEIN Anlauf, kein Lord-Befehl
  2. Tick 10.000: 5 Assassinen 60 Felder vom Lord, 20 Assassinen 20 Felder: Lord-Befehl nur an die WEITEN (die 5 + so viele
     nahe, wie es braucht, um 20 zu fuellen, aber nur wer >= Takt-3 weg ist) - kein Halte-/Sammelbefehl an einen Punkt
  3. Die Losgelaufenen sind jetzt 21 Felder weg: die Nahen (20 Felder) laufen los -> danach alle 20 unterwegs, Phase angriff
  4. (17.10., Partie 1017c) EINER 60 Felder weg, 19 nah: er laeuft allein los; in der naechsten Runde KEIN "vorbei" (die 19
     Wartenden gehoeren zur Gruppe), Phase bleibt anlauf
Gegenprobe: LORD_TAKT_R = 999 -> Fall 2 rot (alle sofort).
Aufruf: python werkzeug/lordanlauf_pruefen.py [sofort]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
SOFORT = len(sys.argv) > 1 and sys.argv[1] == "sofort"
sys.argv = sys.argv[:1]
import assassinen as A
from ausweichen_pruefen import einheit

LORD = (300, 200)
ORTE = [(100, 200)]


def neu():
    t = A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda nr, p: [True] * len(p))
    t._lord_bedarf = lambda L, G, ereignis: (20, "belegt", None)
    if SOFORT:
        t.LORD_TAKT_R = 999
    return t


def szene():
    L = {500: einheit(55, 2, LORD[0], LORD[1], leben=1500000)}
    for i in range(5):
        L[100 + i] = einheit(73, 1, LORD[0] - 60, LORD[1] - 10 + 4 * i)
    for i in range(20):
        L[200 + i] = einheit(73, 1, LORD[0] - 20, LORD[1] - 40 + 4 * i)
    G = {900: {"besitzer": 2, "typ": 32, "x": 200, "y": 300, "leben": 100, "uid": 1, "erreichbar": 1}}
    return L, G


def lord_an(bef):
    return sorted(n for b in bef if b.get("angriff", {}).get("ziel") == 500 for n in b["angriff"]["einheiten"])


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    t = neu(); L, G = szene()
    t.aufnehmen([n for n in L if n != 500])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=9000)
    pruefe(1, "Tick 9.000: Lord-Befehle %s, Phase %s" % (lord_an(bef), t.lordtrupp["phase"]), not lord_an(bef) and t.lordtrupp["phase"] is None)
    t = neu(); L, G = szene()
    t.aufnehmen([n for n in L if n != 500])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=10000)
    an = lord_an(bef)
    halten = [b for b in bef if "halten" in b]
    pruefe(2, "Tick 10.000: Lord-Befehl an %s (soll nur die 5 weiten 100-104), Halten/Sammeln %d" % (an, len(halten)),
           an == [100, 101, 102, 103, 104] and not halten)
    for n in an:
        L[n].update(x=LORD[0] - 21, laufx=LORD[0], laufy=LORD[1], zielart=4, zieleinheit=500)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=10030)
    an2 = lord_an(bef)
    pruefe(3, "Losgelaufene 21 weg: jetzt Lord-Befehl an %d weitere, Phase %s, unterwegs %d" % (
        len([n for n in an2 if n >= 200]), t.lordtrupp["phase"], len(t.lordtrupp["mitglieder"])),
        len([n for n in an2 if n >= 200]) == 15 and len(t.lordtrupp["mitglieder"]) == 20 and t.lordtrupp["phase"] == "angriff")
    t = neu(); L, G = szene()
    for n in (101, 102, 103, 104, 219):
        L.pop(n)
    t.aufnehmen([n for n in L if n != 500])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=10000)
    an = lord_an(bef)
    for n in an:
        L[n].update(x=LORD[0] - 55, laufx=LORD[0], laufy=LORD[1], zielart=4, zieleinheit=500)
    erg2, bef2 = t.schritt(L, G, sichere_orte=ORTE, tick=10030)
    vorbei = [z for z in erg + erg2 if "vorbei" in z]
    pruefe(4, "einer weit, 19 nah: zuerst an %s, danach vorbei-Meldungen %d, Phase %s, warten %d" % (
        an, len(vorbei), t.lordtrupp["phase"], len(t.lordtrupp.get("warte", ()))),
        an == [100] and not vorbei and t.lordtrupp["phase"] == "anlauf" and len(t.lordtrupp.get("warte", ())) == 19)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
