"""B-145 S4b: der geschlossene Kreis Python -> Kern -> Spiel -> Python, ohne Dateikanal (Instanz ueber SHC_INSTANZ).

  python -m selfaware.tools.experiments.kern_kreis_pruefen

Bei laufendem Spiel: zwei eigene Kaempfer ueber den Auftragsring uebergeben und 5 Felder nach Osten schicken, dann im
gemeinsamen Speicher warten, bis beide in einer neuen Gruppe stehen und ihr Laufziel beim Auftrag liegt. Gemessen: Takte vom
Schreiben bis zur sichtbaren Wirkung. Gegenproben: Auftrag fuer eine nicht uebergebene Einheit -> -4, unbekannte Art -> -5.
"""

import sys
import time

from selfaware.game import kern_leitung as KL

KAEMPFER = {22, 23, 24, 26, 70, 72, 75}


def warte_ergebnis(leitung, nummer, sekunden=3.0):
    ende = time.time() + sekunden
    while time.time() < ende:
        e = leitung.ergebnis(nummer)
        if e is not None:
            return e
    return None


def main():
    from selfaware.game.ucp.laden import SPIEL, befehl

    befehl({"pause": False}, 1.0)
    time.sleep(0.3)
    leitung = KL.Leitung(SPIEL)
    w = leitung.lesen()
    eigene = [e for e in w.einheiten.values() if e["besitzer"] == w.ich and e["typ"] in KAEMPFER]
    if len(eigene) < 3:
        print("zu wenige Kaempfer:", len(eigene))
        return 1
    zwei, fremd = eigene[:2], eigene[2]
    ziel = (zwei[0]["x"] + 5, zwei[0]["y"])
    gruppen_vorher = {e["nr"]: e["gruppe"] for e in zwei}
    t0 = leitung.lesen().tick
    nummern = [leitung.auftrag(KL.UEBERNEHMEN, e["nr"]) for e in zwei]
    nummern += [leitung.auftrag(KL.LAUF, e["nr"], *ziel) for e in zwei]
    gegen_a = leitung.auftrag(KL.LAUF, fremd["nr"], *ziel)
    gegen_b = leitung.auftrag(99, zwei[0]["nr"])
    ergebnisse = [warte_ergebnis(leitung, n) for n in nummern]
    print(
        f"geschrieben bei Takt {t0}: Einheiten {[e['nr'] for e in zwei]} -> {ziel}, Ergebnisse {ergebnisse}"
    )
    print(f"Gegenprobe A (nicht uebergeben {fremd['nr']}): {warte_ergebnis(leitung, gegen_a)}")
    print(f"Gegenprobe B (Art 99): {warte_ergebnis(leitung, gegen_b)}")
    t1, ende = None, time.time() + 5.0
    while time.time() < ende and t1 is None:
        b = leitung.lesen()
        if b is None:
            continue
        da = [b.einheiten.get(e["nr"]) for e in zwei]
        if all(
            d
            and d["gruppe"] != gruppen_vorher[d["nr"]]
            and max(abs(d["laufx"] - ziel[0]), abs(d["laufy"] - ziel[1])) <= 2
            for d in da
        ):
            t1 = b.tick
            print("sichtbar:", [(d["nr"], d["gruppe"], d["laufx"], d["laufy"]) for d in da])
    befehl({"pause": True}, 1.0)
    if t1 is None:
        print("Wirkung in 5 s NICHT gesehen")
        return 1
    print(
        f"Kreis geschlossen: geschrieben Takt {t0}, Wirkung im Speicher bei Takt {t1} -> {t1 - t0} Takte"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
