"""B-145 S1: der Vergleich Kern-Weltbild gegen Lagebild findet jede Abweichung (offline)."""

from selfaware.tools.experiments.kern_vergleich import lesen, vergleiche

KOPF = "nr besitzer typ x y leben erreichbar"


def _datei(tmp_path, name, zeilen, tick=None):
    pfad = tmp_path / name
    kopf = [f"tick {tick}"] if tick is not None else []
    pfad.write_text("\n".join(kopf + [KOPF] + zeilen) + "\n", encoding="utf-8")
    return pfad


def test_gleiche_dateien_haben_keine_abweichung(tmp_path):
    a = _datei(tmp_path, "a.txt", ["7 1 75 10 20 28000 1", "9 2 23 11 21 12000 0"], tick=500)
    b = _datei(tmp_path, "b.txt", ["7 1 75 10 20 28000 -9", "9 2 23 11 21 12000 -9"], tick=500)
    ta, _, da = lesen(a, True)
    tb, _, db = lesen(b, True)
    assert ta == tb == 500
    assert vergleiche(da, db) == ([], [], [])


def test_abweichender_wert_und_fehlende_einheit_werden_gemeldet(tmp_path):
    _, _, da = lesen(_datei(tmp_path, "a.txt", ["7 1 75 10 20 28000 1", "9 2 23 11 21 12000 0"]), False)
    _, _, db = lesen(_datei(tmp_path, "b.txt", ["7 1 75 10 20 27999 -9", "8 0 1 5 5 100 -9"]), False)
    nur_a, nur_b, ab = vergleiche(da, db)
    assert nur_a == [9]
    assert nur_b == [8]
    assert ab == [(7, "leben", "28000", "27999")]
