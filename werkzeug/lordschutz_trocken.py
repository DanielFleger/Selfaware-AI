# -*- coding: utf-8 -*-
"""Trockenprobe lordschutz.py (SAI 12.10.): gestellte Lagen, kein Spiel. Rueckgabe 0 = alles wie erwartet.
Gegenprobe 'sabotage': BIS = 0 -> Faelle A und F muessen rot werden."""
import sys
import lordschutz as S

if "sabotage" in sys.argv:
    S.BIS = 0
L = {5: {"typ": 55, "besitzer": 1}, 9: {"typ": 55, "besitzer": 2}, 30: {"typ": 73, "besitzer": 1}, 31: {"typ": 70, "besitzer": 1},
     40: {"typ": 70, "besitzer": 2}}
fehler = 0
def pruefe(name, ok):
    global fehler
    fehler += not ok
    print("%s  %s" % ("OK  " if ok else "ROT ", name))

S.aktualisieren(5000, L)
c, m = S.pruefe({"angriff": {"einheiten": [30, 31], "ziel": 9}})
pruefe("A vor 9.600: Angriff auf gegnerischen Lord verworfen", c is None and m)
c, m = S.pruefe({"angriff": {"einheiten": [30, 31], "ziel": 40}})
pruefe("B vor 9.600: Angriff auf gegnerische Truppe bleibt", c is not None and not m)
c, m = S.pruefe({"angriff": {"einheiten": [30], "gebaeude": 77}})
pruefe("C Gebaeudeangriff bleibt", c is not None and not m)
S.aktualisieren(10000, L)
c, m = S.pruefe({"angriff": {"einheiten": [30, 31, 5], "ziel": 9}})
pruefe("D nach 9.600: unser Lord aus dem Lord-Angriff genommen", c is not None and c["angriff"]["einheiten"] == [30, 31] and m)
c, m = S.pruefe({"angriff": {"einheiten": [5], "ziel": 9}})
pruefe("E nach 9.600: unser Lord allein gegen Lord verworfen", c is None and m)
S.STAND.update(t=None)
c, m = S.pruefe({"angriff": {"einheiten": [30], "ziel": 9}})
pruefe("F ohne Tick: Lord-Angriff verworfen (sicherer Rueckfall)", c is None and m)
S.aktualisieren(5000, L)
p, ms = S.filtern({"befehle": [{"angriff": {"einheiten": [30], "ziel": 9}}, {"lagebild": True}]})
pruefe("G Paket: Lord-Befehl raus, andere Befehle bleiben", p is not None and p["befehle"] == [{"lagebild": True}] and ms)
p, ms = S.filtern({"befehle": [{"angriff": {"einheiten": [30], "ziel": 9}}]})
pruefe("H Paket nur mit Lord-Befehl: nichts gesendet", p is None and ms)
p, ms = S.filtern({"eigenesGefecht": True})
pruefe("I andere Pakete unveraendert", p == {"eigenesGefecht": True} and not ms)
print("ERGEBNIS: %d Fehler" % fehler)
raise SystemExit(1 if fehler else 0)
