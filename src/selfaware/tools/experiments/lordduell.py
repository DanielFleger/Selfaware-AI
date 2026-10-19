# -*- coding: utf-8 -*-
"""M4.04 Lord-Duell: beide Lords zur Kartenmitte schicken, Treffen, erster Treffer, Tod, Ende.

Ablauf:
  1. Stand laden (Standard M7-01, Tick 1100) - jeder Lauf startet gleich (M7.03).
  2. Lord-Wacht scharf: haelt das Ziel fest (die KI holt ihre Lords sonst heim),
     meldet Ankunft, Treffen, ersten Treffer, 10-%-Stufen und Tod; haelt an bei
     erstem Treffer und Tod (je nach Aufruf).
  3. Laufen lassen und das Log mitlesen; bei jedem Halt ein Bild, beim ersten
     Treffer zusaetzlich speichern (Trainingslage "Lord in Gefahr").

Aufruf:  uv run python -m selfaware.tools.experiments.lordduell probe                 nur Ankunftszeiten messen (haelt beim ersten Treffer)
         uv run python -m selfaware.tools.experiments.lordduell duell [lord=ticks]    echter Lauf; z. B. 137=40: Lord 137 startet 40 Ticks spaeter
"""
import io, json, os, re, sys, time

from selfaware.game.ucp.befehl import LOG
from selfaware.game.ucp.laden import lade_stand, befehl, peek, TICK, PAUSE
from selfaware.game.ucp.speichern import speichere
from selfaware.tools.experiments.navigation import bild as _bild

def bild(name, flaeche="karte"):
    return _bild(name, flaeche, vorsilbe="m4-04")

STAND = "M7-01 Speichertest Grumpy T1100"
MITTE = [194, 193]          # naechstes gueltige Feld an der Mitte (200,199) der Burgen (172,113)/(227,284); gemessen 01.10.
ANSICHT = 0x01FE7D1C

class Mitleser:
    """Liest neue Modulzeilen aus ucp3.log (ab jetzt)."""
    def __init__(self):
        self.pos = os.path.getsize(LOG)
    def neu(self):
        with io.open(LOG, encoding="utf-8", errors="replace") as f:
            f.seek(self.pos); t = f.read(); self.pos = f.tell()
        return [z.split("| ", 1)[-1].strip() for z in t.splitlines() if "LORDWACHT" in z or "TEMPO" in z]

def warte(ml, muster, zeit=120):
    """Wartet, bis eine Zeile auf muster passt oder das Spiel pausiert; gibt die Zeilen zurueck."""
    alle = []
    ende = time.time() + zeit
    while time.time() < ende:
        z = ml.neu(); alle += z
        for l in z:
            print("   ", l, flush=True)
        if any(re.search(muster, l) for l in z):
            return alle, True
        time.sleep(0.5)
    return alle, False

def main():
    art = sys.argv[1]
    spaeter, muster = {}, r"ERSTER TREFFER|LORD TOT"
    for a in sys.argv[2:]:
        if a.startswith("warte="):
            muster = a[6:]; continue
        nr, t = a.split("="); spaeter[nr] = int(t)
    lade_stand(STAND, mit_bild=False)
    print(befehl({"lords": True}, 1.2))
    ml = Mitleser()
    halt = ["treffer", "tod"]
    print(befehl({"lordwacht": True, "halt": halt, "alle": 100, "ziel": MITTE, "spaeter": spaeter}, 1.0))
    befehl({"kamera": MITTE}, 0.8)
    befehl({"tempo": 1000 if art == "probe" else 300}, 0.8)
    befehl({"pause": False}, 0.8)
    zeilen, ok = warte(ml, muster, 180)
    t = peek(TICK)[0]
    print("Halt bei Tick %d (Pause %d)" % (t, peek(PAUSE)[0]), flush=True)
    ank = {m.group(2): int(m.group(1)) for m in (re.search(r"ANKUNFT Tick (\d+) - Lord (\d+)", l) for l in zeilen) if m}
    print("Ankunft (Lord -> Tick):", ank)
    if art == "probe" or not ok:
        befehl({"pause": True}, 0.8); befehl({"lordwacht": False}, 0.8)
        return
    # erster Treffer: Bild, speichern, weiter bis zum Tod
    befehl({"zoom": "rein"}, 1.0); befehl({"kamera": MITTE}, 1.0)
    bild("duell_treffer_t%d" % t)
    speichere("M4-04 Lordduell Treffer T%d" % t)
    befehl({"tempo": 1000}, 0.8); befehl({"pause": False}, 0.8)     # der Kampf dauert: 150 Schaden je Treffer
    mitte_bild = False
    ende = time.time() + 600
    while time.time() < ende:
        z = ml.neu()
        for l in z:
            print("   ", l, flush=True)
        if not mitte_bild and any(re.search(r"\(5\d Prozent\)", l) for l in z):   # Stufe um 50 %
            befehl({"pause": True}, 0.8); bild("duell_kampf_t%d" % peek(TICK)[0]); befehl({"pause": False}, 0.8)
            mitte_bild = True
        if any("LORD TOT" in l for l in z):
            break
        time.sleep(0.5)
    t = peek(TICK)[0]
    bild("duell_tod_t%d" % t)
    print("Tod bei Tick %d; Ansicht %d" % (t, peek(ANSICHT)[0]), flush=True)
    # was danach kommt: weiterlaufen lassen und die Ansicht beobachten (Endbildschirm?)
    befehl({"lordwacht": False}, 0.8)
    befehl({"pause": False}, 0.8)
    a0 = peek(ANSICHT)[0]
    for _ in range(60):
        a = peek(ANSICHT)[0]
        if a != a0:
            print("Ansicht wechselt %d -> %d bei Tick %d" % (a0, a, peek(TICK)[0]), flush=True)
            time.sleep(2.0)
            bild("duell_ende_ansicht%d" % a); bild("duell_ende_ansicht%d" % a, "menue")
            break
        time.sleep(1.0)
    else:
        print("60 s nach dem Tod: Ansicht unveraendert %d (kein Endbildschirm)" % a0)
        bild("duell_nach_tod_60s")

if __name__ == "__main__":
    main()
