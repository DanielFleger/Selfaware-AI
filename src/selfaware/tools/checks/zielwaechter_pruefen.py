# -*- coding: utf-8 -*-
"""Gegenproben fuer zielwaechter.py, ohne laufendes Spiel."""

from selfaware.runtime.live.zielwaechter import neue_verfehlungen, pruefe


def main():
    tests = []

    # Typischer Fall: Noch viel Zeit; trotz grosser Luecke darf nichts abbrechen.
    p = pruefe(10000, 100, 3000)
    tests.append(("frueher Lauf bleibt offen", all(z["erreichbar"] for z in p)))

    # Unguenstiger Fall: Kurz vor der harten Grenze reicht selbst die doppelte Rekordrate nicht.
    p = pruefe(19100, 100, 500)
    neu, hart = neue_verfehlungen(p)
    tests.append(("harte Unmoeglichkeit erkannt", hart and any(z["name"] == "harte Grenze" for z in neu)))

    # Grenzfall: Ein noch rechtzeitig eintreffendes Los steckt als zusaetzlicher Bilanzwert in habe_gold.
    ohne = pruefe(14200, 100, 600)
    mit = pruefe(14200, 120, 600)
    tests.append(("rettendes Los verhindert Fehlalarm",
                  not next(z for z in ohne if z["name"] == "sehr gut")["erreichbar"] and
                  next(z for z in mit if z["name"] == "sehr gut")["erreichbar"]))

    # Bereits gemeldete Stufen duerfen das Protokoll nicht in jeder Runde fluten.
    p = pruefe(15000, 1000, 1100)
    neu, _ = neue_verfehlungen(p, schon=("sehr sehr gut",))
    tests.append(("Meldung nur einmal", all(z["name"] != "sehr sehr gut" for z in neu)))

    for name, ok in tests:
        print(("OK   " if ok else "FEHLER ") + name)
    if not all(ok for _, ok in tests):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
