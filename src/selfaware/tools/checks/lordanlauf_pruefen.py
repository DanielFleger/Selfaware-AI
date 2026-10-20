# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel: Lord-Angriff mit BEREITSTELLUNG (17.10. Laptop, Partie 1017h: 35x lief genau ein Assassine los, 38 von
93 Toten am Lord mit 4+ Fernkaempfern im Umkreis 20; ~6 Assassinen standen als Lord-Trupp an unserer Burg still) und
Raiden vor dem Lord (Daniel 17.10. "prio ist am Anfang raiden und auch waehrend des laufs spaeter"). Bedarf hier fest 20,
Lord 30.000 Leben (Nomade). Vorher festgelegt:
  1. Tick 9.000 (Lord-Schutz), 25 Assassinen, keine Raid-Plaetze: KEINE Bereitstellung, kein Lord-Befehl
  2. Tick 10.000, keine Raid-Plaetze: Bereitstellung mit den 20 NAECHSTEN (200-219); Laufbefehle nur an sie, jeder Platz
     24-32 Felder vom Lord; KEIN Angriffsbefehl auf den Lord, solange nicht alle bereit sind; 100-104 nicht dabei
  3. Raiden geht vor: 30 lohnende Raid-Plaetze bei 25 Assassinen -> keine Bereitstellung, Meldung "LORD WARTET"
  4. (17.10. Daniel: erst die Wirtschaft entmannen) wie 3, aber 20.000 Ticks spaeter -> weiter KEINE Bereitstellung
  5. 19 von 20 am Platz: noch kein Angriff (Phase bereit)
  6. alle 20 am Platz: Phase angriff, alle 20 bekommen in DERSELBEN Runde einen Befehl auf den Lord (Laufbefehl, weil
     weiter als ANLAUF_NAH), sonst niemand
  7. in der Bereitstellung stirbt einer: ein Freier rueckt nach (Gruppe wieder 20), kein Abbruch
  8. im Angriff steht einer STEH_TICKS ohne Spielziel auf demselben Feld: er faellt aus der Gruppe (Meldung), die anderen bleiben
  9. Raider mit Gebaeude-Ziel steht STEH_TICKS ohne Spielziel: "STILLSTAND geloest", danach wieder ein Ziel
 10. Bereitstellung laenger als BEREIT_MAX: Abbruch, Phase None
Gegenprobe: STEH_TICKS = 10**9 -> 8 und 9 rot.
Aufruf: uv run python -m selfaware.tools.checks.lordanlauf_pruefen [gegenprobe]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

GEGEN = len(sys.argv) > 1 and sys.argv[1] == "gegenprobe"
sys.argv = sys.argv[:1]
import selfaware.micro.tasks.assassinen as A
from selfaware.tools.checks.ausweichen_pruefen import einheit

LORD = (300, 200)
ORTE = [(100, 200)]


def neu(raid=0):
    t = A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda nr, p: [True] * len(p))
    t._lord_bedarf = lambda L, G, ereignis: (20, "belegt", None)
    t._raid_plaetze = raid
    if GEGEN:
        t.STEH_TICKS = 10 ** 9
    return t


def szene():
    L = {500: einheit(55, 2, LORD[0], LORD[1], leben=30000)}
    for i in range(5):
        L[100 + i] = einheit(73, 1, LORD[0] - 60, LORD[1] - 10 + 4 * i)
    for i in range(20):
        L[200 + i] = einheit(73, 1, LORD[0] - 40, LORD[1] - 40 + 4 * i)
    return L, {}


def an_lord(bef):
    aus = set()
    for b in bef:
        a = b.get("angriff", {})
        if a.get("ziel") == 500 or (a.get("lauf") and tuple(a["lauf"]) == LORD):
            aus |= set(a["einheiten"])
    return sorted(aus)


def lauf_an(bef):
    return {n: tuple(b["angriff"]["lauf"]) for b in bef if b.get("angriff", {}).get("lauf") for n in b["angriff"]["einheiten"]}


def an_platz(t, L, nummern):
    for n in nummern:
        p = t.lordtrupp["platz"][n]
        L[n].update(x=p[0], y=p[1], laufx=p[0], laufy=p[1])


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    lt = lambda t: t.lordtrupp
    # 1
    t = neu(); L, G = szene(); t.aufnehmen([n for n in L if n != 500])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=9000)
    pruefe(1, "Tick 9.000: Phase %s, Lord-Befehle %s" % (lt(t)["phase"], an_lord(bef)), lt(t)["phase"] is None and not an_lord(bef))
    # 2
    t = neu(); L, G = szene(); t.aufnehmen([n for n in L if n != 500])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=10000)
    la = lauf_an(bef)
    abst = [A.schach(p, LORD) for p in lt(t)["platz"].values()]
    pruefe(2, "Tick 10.000: Phase %s, Gruppe %s..%s (%d), Laufbefehle an %d, Plaetze %s-%s Felder, Lord-Befehle %s" % (
        lt(t)["phase"], min(lt(t)["mitglieder"] or [0]), max(lt(t)["mitglieder"] or [0]), len(lt(t)["mitglieder"]), len(la),
        min(abst or [0]), max(abst or [0]), an_lord(bef)),
        lt(t)["phase"] == "bereit" and lt(t)["mitglieder"] == set(range(200, 220)) and set(la) == set(range(200, 220))
        and abst and min(abst) >= 24 and max(abst) <= 32 and not an_lord(bef))
    # 3
    t = neu(raid=30); L, G = szene(); t.aufnehmen([n for n in L if n != 500])
    t.runde = 19
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=10000)
    pruefe(3, "30 Raid-Plaetze, 25 Assassinen: Phase %s, Meldung %s" % (lt(t)["phase"], [z[:40] for z in erg if "LORD WARTET" in z]),
           lt(t)["phase"] is None and any("LORD WARTET" in z for z in erg))
    # 4
    t = neu(raid=30); L, G = szene(); t.aufnehmen([n for n in L if n != 500])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=30000)
    pruefe(4, "Tick 30.000, Raid-Plaetze da: Phase %s, Gruppe %d" % (lt(t)["phase"], len(lt(t)["mitglieder"])),
           lt(t)["phase"] is None and not lt(t)["mitglieder"])
    # 5 und 6
    t = neu(); L, G = szene(); t.aufnehmen([n for n in L if n != 500])
    t.schritt(L, G, sichere_orte=ORTE, tick=10000)
    an_platz(t, L, range(200, 219))
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=10030)
    pruefe(5, "19 von 20 bereit: Phase %s, Lord-Befehle %s" % (lt(t)["phase"], an_lord(bef)),
           lt(t)["phase"] == "bereit" and not an_lord(bef))
    an_platz(t, L, [219])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=10060)
    pruefe(6, "alle 20 bereit: Phase %s, Befehl auf den Lord an %d (%s..%s)" % (
        lt(t)["phase"], len(an_lord(bef)), min(an_lord(bef) or [0]), max(an_lord(bef) or [0])),
        lt(t)["phase"] == "angriff" and an_lord(bef) == list(range(200, 220)))
    # 8 (im Angriff aus Fall 6 weiter): 205 steht ohne Spielziel
    for n in range(200, 220):
        L[n].update(laufx=LORD[0], laufy=LORD[1])
    L[205].update(laufx=L[205]["x"], laufy=L[205]["y"])
    for k, tk in enumerate((10090, 10200, 10320)):
        erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=tk)
    raus = [z for z in erg if "LORD-ANGRIFF: 205 steht" in z]
    pruefe(8, "im Angriff steht 205: Meldung %s, 205 in Gruppe %s, Gruppe %d" % (
        bool(raus), 205 in lt(t)["mitglieder"], len(lt(t)["mitglieder"])),
        raus and 205 not in lt(t)["mitglieder"] and len(lt(t)["mitglieder"]) == 19)
    # 7
    t = neu(); L, G = szene(); t.aufnehmen([n for n in L if n != 500])
    t.schritt(L, G, sichere_orte=ORTE, tick=10000)
    L.pop(203)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=10030)
    pruefe(7, "einer tot in der Bereitstellung: Phase %s, Gruppe %d, nachgerueckt %s, Abbruch %s" % (
        lt(t)["phase"], len(lt(t)["mitglieder"]), sorted(lt(t)["mitglieder"] - set(range(200, 220))),
        any("ABGEBROCHEN" in z for z in erg)),
        lt(t)["phase"] == "bereit" and len(lt(t)["mitglieder"]) == 20 and not any("ABGEBROCHEN" in z for z in erg))
    # 9
    t = neu(raid=99); L, G = szene()
    for n in range(200, 220):
        L.pop(n)
    G = {900: {"besitzer": 2, "typ": 32, "x": 160, "y": 200, "leben": 100, "uid": 1, "erreichbar": 1}}
    t.aufnehmen([n for n in L if n != 500])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=10000)
    hatte = {n: g for n, g in t.ziel.items()}
    erg = []
    for tk in (10100, 10250, 10400):
        e, bef = t.schritt(L, G, sichere_orte=ORTE, tick=tk)
        erg += e
    pruefe(9, "Raider stehen ohne Spielziel: Ziele vorher %s, STILLSTAND-Meldung %s, Ziele danach %s" % (
        hatte, [z[:60] for z in erg if "STILLSTAND" in z][:1], t.ziel),
        hatte and any("STILLSTAND geloest" in z for z in erg) and t.ziel)
    # 10
    t = neu(); L, G = szene(); t.aufnehmen([n for n in L if n != 500])
    t.schritt(L, G, sichere_orte=ORTE, tick=10000)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE, tick=10000 + t.BEREIT_MAX + 30)
    pruefe(10, "Bereitstellung zu lang: Phase %s, Meldung %s" % (lt(t)["phase"], [z[:50] for z in erg if "ABGEBROCHEN" in z][:1]),
           lt(t)["phase"] is None and any("ABGEBROCHEN" in z for z in erg))
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
