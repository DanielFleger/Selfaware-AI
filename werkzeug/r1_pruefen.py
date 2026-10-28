# -*- coding: utf-8 -*-
"""B-287 Reaktionszeit-Pruefung R1 "Schuetze zielt -> raus aus der Schusslinie" im Kern (Plan_Takt_Kern.md, Schritt 2).

Testaufbau (nur Testgefecht, FAIRNESS.md erlaubt setzen dort): eine angehaltene Partie auf SHC_INSTANZ (shc.py gefecht),
Kern ab Version 22 geladen. Gesetzt werden N eigene Speertraeger und 4 feindliche Armbrueste daneben; die Speertraeger gehen
an den Kern. Alle LOCK_S Sekunden schickt dieses Skript sie ueber den Kern zurueck in die Schusslinie (Kern-Auftrag Laufen),
damit die Armbrueste immer wieder zielen.

Vorher festgelegt (Soll):
  1. R1 an: >= 100 Reflex-Befehle; Reaktion (Befehlstakt - Takt, seit dem das Zielen sichtbar war) <= 1 Takt bei allen;
     das Spiel zeigt das neue Laufziel (R1 ANGEKOMMEN) bei allen, je <= 1 Takt nach dem Befehl; kein NICHT ANGEKOMMEN.
  2. Gegenprobe R1 aus (Schalter zur Laufzeit): 0 Reflex-Befehle, aber "R1 AUS ... in der Schusslinie"-Meldungen (der Kern
     sieht die Lage weiter) - und die Speertraeger verlieren je Takt mehr Leben als mit R1.
Aufruf: SHC_INSTANZ=5 python werkzeug/r1_pruefen.py [sekunden_je_phase] [kern-dll]
Jede Phase in einem frischen Gefecht (shc.py gefecht), Kern wird danach geladen."""
import os
import re
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
os.environ.setdefault("SHC_INSTANZ", "5")
import shc
from laden import befehl

N, LOCK_S = 8, 8
EIGEN = (190, 262)            # Speertraeger
FEIND = (205, 262)            # Armbrueste (15 Felder daneben; Lord bei (143,266) liegt ausserhalb ihrer 44 Felder)


def kern_log():
    import befehl as K
    return os.path.join(K.SPIEL, "ucp", "villagestudio", "samurai_kern.log")


def lagebild():
    import befehl as K
    befehl({"kern": {"welt": True}}, 2.0, bis="KERN")
    z = open(os.path.join(K.SPIEL, "ucp", "villagestudio", "kern_lagebild.txt"), encoding="utf-8").read().splitlines()
    kopf = z[1].split()
    return {int(f[0]): dict(zip(kopf, map(int, f))) for f in (r.split() for r in z[2:]) if f}


def nummern(text):
    return [int(n) for n in re.search(r"Nummern \[([0-9, ]+)\]", text).group(1).split(",")]


def phase(nrs, sekunden, an):
    befehl({"kern": {"lauf": {"x": 1 if an else 0, "y": 0, "einheiten": [-1]}}}, 1.0, bis="KERN")
    befehl({"kern": {"lauf": {"x": 1 if an else 0, "y": 0, "einheiten": [-2]}}}, 1.0, bis="KERN")     # R3 (ab Kern 24) mit
    log = kern_log()
    start = sum(1 for _ in open(log, encoding="utf-8", errors="replace"))
    L0 = lagebild()
    t0 = L0[nrs[0]]["tick"] if "tick" in L0[nrs[0]] else None
    leben0 = sum(L0[n]["leben"] for n in nrs if n in L0)
    befehl({"pause": False}, 0.5)
    ende = time.time() + sekunden
    while time.time() < ende:
        time.sleep(LOCK_S)
        befehl({"kern": {"lauf": {"x": EIGEN[0], "y": EIGEN[1], "einheiten": nrs}}}, 0.8)
    befehl({"pause": True}, 0.5)
    L1 = lagebild()
    leben1 = sum(L1[n]["leben"] for n in nrs if n in L1 and L1[n]["besitzer"] == 1 and L1[n]["typ"] == 24)
    zeilen = open(log, encoding="utf-8", errors="replace").read().splitlines()[start:]
    takte = [int(m.group(1)) for m in (re.match(r"waechter tick (\d+)", z) for z in zeilen) if m]
    return zeilen, leben0 - leben1, (takte[-1] - takte[0]) if len(takte) > 1 else 0, t0


def auswerten(zeilen):
    # je Lage (Einheit, Takt seit dem sie sichtbar ist) zaehlt nur der ERSTE Befehl als Reaktion; weitere Befehle derselben
    # Lage kommen nach der Sperre R1_PAUSE (Einheit stand nach dem Ausweichen noch in der Linie) - Wiederholung, eigens gezaehlt
    erste, wdh = {}, 0
    for m in (re.search(r"R1 Einheit (\d+) bei .* seit Takt (-?\d+) - Reaktion (-?\d+) Takte", z) for z in zeilen):
        if m:
            k = (int(m.group(1)), int(m.group(2)))
            if k in erste:
                wdh += 1
            else:
                erste[k] = int(m.group(3))
    reak = list(erste.values())
    print("   Reaktion je Lage (erste Befehle): %s, Wiederholungen derselben Lage: %d" % (
        {r: reak.count(r) for r in sorted(set(reak))}, wdh))
    ank = [int(m.group(1)) for m in (re.search(r"R1 ANGEKOMMEN .*\(\+(\d+) Takte\)", z) for z in zeilen) if m]
    nicht = sum("NICHT ANGEKOMMEN" in z for z in zeilen)
    aus = sum("R1 AUS" in z for z in zeilen)
    return reak, ank, nicht, aus


def frische_partie(kern):
    """Jede Phase in einem frischen Gefecht: tote Einheiten geben ihre Nummer frei, das Spiel vergibt sie neu (auch an
    Feinde) - frische Nummern halten die Zaehlung sauber. Der Kern wird nach dem Gefecht geladen (laeuft bis zum Neustart)."""
    try:
        shc.gefecht(gegner="1", plaetze="0,1")       # feste Plaetze: unsere Burg (138,262), Gegner (224,282) - gemessen 02:25
    except shc.Fehler as e:                 # Gegner-Bergfried fehlt manchmal - fuer diese Pruefung egal, Partie muss laufen
        print("   (gefecht: %s)" % str(e)[:80])
    z = shc.partie_sicher()
    # nur Testgefecht (FAIRNESS.md): KI von Spieler 2 aus, sonst fuehrt sie die gesetzten Schuetzen weg (gemessen 02:20)
    for adr, wert in ((0x0191DE7C + 2 * 4, 0), (0x0115BDF8 + 2 * 0x39F4 + 0x2300, 0), (0x0191DE10 + 2 * 4, 1)):
        befehl({"poke": adr, "wert": wert}, 1.0, bis="POKE")
    k = [x for x in befehl({"kern": {"laden": kern}}, 3.0, bis="KERN") if "KERN" in x]
    print("   Partie %s Takt %d, %s" % (z["text"], z["tick"], k[-1][-60:] if k else "Kern?"))


def main():
    sek = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    kern = sys.argv[2] if len(sys.argv) > 2 else "samurai_kern_26.dll"
    erg = {}
    for name, an in (("R1 an", True), ("R1 aus", False)):
        frische_partie(kern)
        eigene = nummern(shc.setze("1", "24", str(EIGEN[0]), str(EIGEN[1]), str(N)))
        feinde = nummern(shc.setze("2", "23", str(FEIND[0]), str(FEIND[1]), "4"))
        print("%s: eigene %s, Armbrueste %s" % (name, eigene, feinde))
        befehl({"kern": {"uebernehmen": eigene}}, 1.5, bis="KERN")
        zeilen, verlust, takte, _ = phase(eigene, sek, an)
        reak, ank, nicht, aus = auswerten(zeilen)
        fremd = sum("ist nicht mehr dieselbe" in z for z in zeilen)
        erg[name] = (reak, ank, nicht, aus, verlust, takte)
        print("%s: %d Lagen, Reaktion max %s, Ankunft %d (max +%s), NICHT ANGEKOMMEN %d, AUS-Meldungen %d, aus dem Buch (gestorben oder Nummer neu vergeben) %d, "
              "Leben verloren %d in ~%d Takten" % (name, len(reak), max(reak) if reak else "-", len(ank), max(ank) if ank else "-",
                                                  nicht, aus, fremd, verlust, takte))
    befehl({"kern": {"lauf": {"x": 1, "y": 0, "einheiten": [-1]}}}, 1.0, bis="KERN")      # Schalter zurueck auf an
    befehl({"kern": {"lauf": {"x": 1, "y": 0, "einheiten": [-2]}}}, 1.0, bis="KERN")
    reak, ank, nicht, _, v_an, t_an = erg["R1 an"]
    r2, _, _, aus2, v_aus, t_aus = erg["R1 aus"]
    f = [("1a >= 100 Lagen (erste Reflexe) mit R1 an", len(reak) >= 100),
         ("1b Reaktion <= 1 Takt bei allen", bool(reak) and max(reak) <= 1),
         ("1c jeder Befehl im Spiel angekommen, <= 1 Takt", bool(reak) and bool(ank) and max(ank) <= 1 and nicht == 0),
         ("2a R1 aus: 0 Reflexe, Lage weiter gesehen", not r2 and aus2 > 0),
         ("2b Reflexe aus verliert je Takt mehr Leben", t_an > 0 and t_aus > 0 and v_aus / t_aus > v_an / t_an)]
    for name, ok in f:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    print("%d von %d gruen" % (sum(ok for _, ok in f), len(f)))


if __name__ == "__main__":
    main()
