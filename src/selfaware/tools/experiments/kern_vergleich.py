"""B-145 S1: Weltbild des Kerns gegen das Lagebild von logik.lua - im selben, angehaltenen Takt.

  python -m selfaware.tools.experiments.kern_vergleich

Haelt das Spiel an (falls es laeuft, danach wieder los), laesst logik.lua das Lagebild schreiben
({"lagebild": true} -> abzug/lagebild.txt, gebaeude.txt) und den Kern sein Weltbild
({"kern": {"welt": true}} -> kern_lagebild.txt, kern_gebaeude.txt) und vergleicht jede Spalte.
"erreichbar" braucht den Wegfinder (S3) und wird ausgelassen. Instanz und Spieler wie immer ueber
SHC_INSTANZ / SHC_SPIELER.
"""

import os
import sys

AUSNAHMEN = frozenset({"erreichbar"})


def lesen(pfad, mit_tick):
    """Datei im Lagebild-Format -> (Takt oder None, Spalten, {nr: {spalte: wert}})."""
    with open(pfad, encoding="utf-8", errors="replace") as f:
        zeilen = [z for z in f.read().splitlines() if z.strip()]
    tick = None
    if mit_tick:
        tick = int(zeilen[0].split()[1])
        zeilen = zeilen[1:]
    kopf = zeilen[0].split()
    daten = {}
    for z in zeilen[1:]:
        werte = z.split()
        daten[int(werte[0])] = dict(zip(kopf, werte, strict=False))
    return tick, kopf, daten


def vergleiche(a, b, ausnahmen=AUSNAHMEN):
    """a, b: {nr: {spalte: wert}} -> (nur in a, nur in b, [(nr, spalte, wert a, wert b)])."""
    nur_a = sorted(set(a) - set(b))
    nur_b = sorted(set(b) - set(a))
    abweichungen = []
    for nr in sorted(set(a) & set(b)):
        for spalte, wert in a[nr].items():
            if spalte not in ausnahmen and b[nr].get(spalte) != wert:
                abweichungen.append((nr, spalte, wert, b[nr].get(spalte)))
    return nur_a, nur_b, abweichungen


def bericht(name, a, b):
    nur_a, nur_b, ab = vergleiche(a, b)
    print(
        f"{name}: Lagebild {len(a)}, Kern {len(b)} | nur Lagebild {len(nur_a)} {nur_a[:5]} | "
        f"nur Kern {len(nur_b)} {nur_b[:5]} | abweichende Werte {len(ab)} {ab[:5]}"
    )
    return len(nur_a) + len(nur_b) + len(ab)


def main():
    from selfaware.game.ucp.laden import PAUSE, SPIEL, befehl, peek

    lief = peek(PAUSE)[0] == 0
    befehl({"pause": True}, 1.0)
    try:
        befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
        print(befehl({"kern": {"welt": True}}, 2.0, bis="KERN welt")[0])
    finally:
        if lief:
            befehl({"pause": False}, 1.0)
    vs = os.path.join(SPIEL, "ucp", "villagestudio")
    ich = os.environ.get("SHC_SPIELER", "1")
    abzug = os.path.join(vs, "abzug" if ich == "1" else f"abzug_sp{ich}")
    t_lua, _, e_lua = lesen(os.path.join(abzug, "lagebild.txt"), True)
    t_kern, _, e_kern = lesen(os.path.join(vs, "kern_lagebild.txt"), True)
    _, _, g_lua = lesen(os.path.join(abzug, "gebaeude.txt"), False)
    _, _, g_kern = lesen(os.path.join(vs, "kern_gebaeude.txt"), False)
    print(f"Takt Lagebild {t_lua}, Kern {t_kern}")
    fehler = (t_lua != t_kern) + bericht("Einheiten", e_lua, e_kern)
    fehler += bericht("Gebaeude", g_lua, g_kern)
    print("GLEICH" if fehler == 0 else f"UNGLEICH ({fehler})")
    return 0 if fehler == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
