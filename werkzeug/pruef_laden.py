# -*- coding: utf-8 -*-
"""B-159 Ladetest EINZELN (Daniel 21.10.2026 23:46: "warum testest du nicht isoliert nur das Laden und stoppst bei einer Niederlage").
Nur Laden - kein Neustart, kein Sandkasten-Aufbau, kein zweiter Ladeversuch.

Schwerer Fall ohne Neustart: im Hauptmenue genau den Zustand nach einem Spielstart herstellen (Spur laden_spur_20261021_233820,
erste Zeile): Platz 0, Mensch-Eintraege alle -1, KI-Eintraege alle 0 - geschrieben OHNE "player" (sonst legt alsSpieler den
alten Platz zurueck), gelesen DIREKT aus dem Speicher (peek laeuft selbst "als Spieler 1" und zeigt immer Platz 1).
  Lauf 1 GEGENLAUF: kein Fix -> muss kippen. Kippt er nicht, ist der Test hohl und haelt an.
  Lauf 2 ECHTER LADECODE: derselbe Zustand, laden.lade_stand mit Fix -> darf nicht kippen. Genau zwei Ladevorgaenge.
Aufruf: SHC_INSTANZ=5 python werkzeug/pruef_laden.py ["Spielstand"]
"""
import os
import sys
import time

os.environ.setdefault("SHC_INSTANZ", "5")
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import shc  # noqa: E402
from befehl import LOG, neue_id, sende  # noqa: E402
import speicher  # noqa: E402
from laden import KI, MENSCH, PLATZ_ICH  # noqa: E402

NAME = sys.argv[1] if len(sys.argv) > 1 else "SK B140 Burg Franz T40126 oH nS"


# Zustand nach einem Spielstart (abbild_menue_frisch_menue.npz gegen abbild_menue_nach_laden.npz, 21.10. 23:58 - die einzigen
# Unterschiede in GameSynchronyState ausser der Befehlswarteschlange)
FRISCH = [(PLATZ_ICH, 0), (0x0191DD84, 0), (0x0191DE04, 0), (0x0191DEF8, 0)] +          [(MENSCH + 4 * i, -1) for i in range(9)] + [(KI + 4 * i, 0) for i in range(9)]
# Gemessen 21.10. 23:50 (je ein Lauf aus dem Frischstart-Zustand): ohne Fix kippt, A "Platz 1 + Mensch[1] 1 vor dem Knopfdruck"
# haelt, B "Spielmodus 0x0191DD84 = 99" haelt ebenfalls. Im Ladecode steht A (laden.lade_stand) - EIN Weg, nicht zwei.


def poke(paare):
    sende({"befehle": [{"id": neue_id(), "poke": a, "wert": w} for a, w in paare]}, 2.0)   # OHNE "player"


def lauf(art, echter_fix):
    t0 = time.time()
    shc.menue()
    poke(FRISCH)
    lies = lambda a: int.from_bytes(speicher.lies(a, 4), "little", signed=True)
    frisch = all(lies(a) == w for a, w in FRISCH)                 # direkt gelesen, nicht ueber peek
    with open(LOG, encoding="utf-8", errors="replace") as f:
        n0 = sum(1 for _ in f)
    t1 = time.time()
    try:
        text, gekippt = shc.laden(NAME, platz=1, platz_vorher=echter_fix), False
    except shc.Fehler as e:
        text, gekippt = str(e), True
    t2 = time.time()
    with open(LOG, encoding="utf-8", errors="replace") as f:
        erster_takt = [z.split("| ", 1)[-1].strip() for i, z in enumerate(f) if i >= n0 and "LADEPAUSE: vorher" in z]
    print("== %s: Frischstart-Zustand %s | %s | Menue %.1f s, Laden %.1f s" % (
        art, "hergestellt" if frisch else "NICHT hergestellt", "GEKIPPT" if gekippt else "haelt", t1 - t0, t2 - t1), flush=True)
    print("   erster Takt:", erster_takt, flush=True)
    print("   ", text[:200], flush=True)
    return frisch, gekippt


def main():
    f1, g1 = lauf("GEGENLAUF (frisch, ohne Fix)", False)
    if not f1 or not g1:
        print("HOHL: Frischstart-Zustand nicht hergestellt oder Gegenlauf kippte nicht - Test zaehlt nicht")
        sys.exit(2)
    f2, g2 = lauf("ECHTER LADECODE (frisch, laden.lade_stand mit Fix)", True)
    if not f2:
        print("HOHL: Frischstart-Zustand nicht hergestellt")
        sys.exit(2)
    print("ERGEBNIS: %s" % ("KIPPT - Fix wirkt im echten Ladecode nicht" if g2 else "HAELT im schweren Fall"))
    sys.exit(1 if g2 else 0)


if __name__ == "__main__":
    main()
