# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel (12.10., Daniel 01:04: 128 Holzfaeller, 48 leer): kausal.entscheide darf keinen neuen Betrieb bauen,
solange die offenen Stellen die verfuegbaren Bauern (Feuer + freier Wohnraum) aufbrauchen. Vorher festgelegt:
  1. 0 offene Stellen, 4 am Feuer: Holzfaeller wird gebaut (Wert > 0)
  2. 48 offene Stellen, 4 am Feuer, 0 Wohnraum frei: KEIN Holzfaeller (nur hoechstens eine Huette)
  3. 3 offene Stellen, 4 am Feuer: genau 1 neuer Betrieb (der 4. Bauer), nicht 4
Aufruf: uv run python -m selfaware.tools.checks.kausal_stellen_pruefen [andere_kausal.py]"""
import importlib.util, os, sys
HIER = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) > 1:
    spec = importlib.util.spec_from_file_location("kausal", sys.argv[1]); K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)
else:
    import selfaware.learning.kausal as K

def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text))
    st = {"feuer": 4, "platz": 40, "leute": 40, "holz": 500, "gold": 500, "stein": 0}
    kand = [(3, (100 + i * 3, 100), {"holz": 3}, 1) for i in range(6)]
    def betriebe(offen, s=st):
        h = K.entscheide(1000, 20000, s, kand, (100, 105), {3: (100, 100)}, 6, offene_stellen=offen)
        return [x for x in h if x[1] == 3]
    pruefe(1, "0 offene Stellen, 4 am Feuer: %d Holzfaeller" % len(betriebe(0)), len(betriebe(0)) == 4)
    pruefe(2, "48 offene Stellen, 4 am Feuer, Wohnraum voll: %d Holzfaeller" % len(betriebe(48)), len(betriebe(48)) == 0)
    pruefe(3, "3 offene Stellen, 4 am Feuer: %d Holzfaeller" % len(betriebe(3)), len(betriebe(3)) == 1)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1

if __name__ == "__main__":
    sys.exit(main())
