"""B-182 (Daniel 10.11. 23:07 "Ja, Protokoll"): Das Lageprotokoll schreibt Schuss- und Gebaeudeziel der eigenen Einheiten aus dem
Kern mit (S113: der Abzug des Spiels fuehrt sie nicht; S114: sie stehen in schusseinheit und mauerx/mauery). Ohne Spiel."""

import gzip
import json
import sys
from types import ModuleType, SimpleNamespace

from selfaware.telemetry import lageprotokoll as LP

EIGENE = {
    # Werte wie im Sandkasten vom 10.11. 23:03: Reiter auf Arbeiter 305, Sklave auf das Gebaeude bei (243, 132)
    7: {"nr": 7, "besitzer": 1, "typ": 74, "x": 155, "y": 281, "zielart": 4, "zieleinheit": 305, "zieluid": 23928,
        "schusseinheit": 305, "schussziel_uid": 23928, "mauerx": 0, "mauery": 0, "planx": 0, "plany": 0, "nahziel": 0},
    8: {"nr": 8, "besitzer": 1, "typ": 71, "x": 150, "y": 280, "zielart": 0, "zieleinheit": 0, "zieluid": 0,
        "schusseinheit": 0, "schussziel_uid": 0, "mauerx": 243, "mauery": 133, "planx": 243, "plany": 134, "nahziel": 0},
}
# fremd: der Kern liefert ohnehin nur die freien Felder (EINHEIT_FREMD), keine Zielfelder
FREMD = {9: {"nr": 9, "besitzer": 2, "typ": 1, "x": 251, "y": 126, "leben": 2500}}
WELT = SimpleNamespace(tick=500, ich=1, einheiten={**EIGENE, **FREMD})


class Kern:
    def __init__(self, welt=None, fehler=None):
        self.welt, self.fehler = welt, fehler

    def lesen(self):
        if self.fehler is not None:
            raise self.fehler
        return self.welt


def _abzug(tmp_path, monkeypatch):
    lb, gb = tmp_path / "lagebild.txt", tmp_path / "gebaeude.txt"
    lb.write_text("tick 500\nnr besitzer typ x y\n7 1 74 155 281\n9 2 1 251 126\n", encoding="utf-8")
    gb.write_text("nr besitzer typ x y\n", encoding="utf-8")
    # Der echte Waechter braucht eine Spielinstanz (ohne Spiel: SHC_INSTANZ=99) - er liefert hier nur die zwei Dateipfade
    wa = ModuleType("selfaware.micro.tasks.waechter")
    wa.LAGEBILD, wa.GEBAEUDEDATEI = str(lb), str(gb)
    monkeypatch.setitem(sys.modules, "selfaware.micro.tasks.waechter", wa)
    return tmp_path / "lage.jsonl.gz"


def _zeilen(p):
    with gzip.open(p, "rt", encoding="utf-8") as f:
        return [json.loads(z) for z in f]


def test_eigen_nur_eigene_einheiten_mit_schuss_und_gebaeudeziel(tmp_path, monkeypatch):
    p = _abzug(tmp_path, monkeypatch)
    LP.Lageprotokoll(str(p), kern=Kern(WELT)).schreibe({"t": 500})
    z = _zeilen(p)[0]
    e = LP.eigen_lesen(z)
    assert sorted(e) == [7, 8]  # die fremde Einheit 9 steht nicht darin
    assert (e[7]["schusseinheit"], e[7]["schussziel_uid"], e[7]["zieleinheit"]) == (305, 23928, 305)
    assert (e[8]["mauerx"], e[8]["mauery"]) == (243, 133)
    assert z["eigen"].startswith("kern_tick 500 ich 1")
    assert z["einheiten"].count("\n") == 4  # der Abzug selbst bleibt unveraendert


def test_ohne_kern_wie_bisher(tmp_path, monkeypatch):
    p = _abzug(tmp_path, monkeypatch)
    LP.Lageprotokoll(str(p)).schreibe({"t": 1})
    z = _zeilen(p)[0]
    assert "eigen" not in z and "eigen_fehler" not in z
    assert LP.eigen_lesen(z) == {}


def test_kernfehler_haelt_das_protokoll_nicht_an(tmp_path, monkeypatch):
    p = _abzug(tmp_path, monkeypatch)
    lp = LP.Lageprotokoll(str(p), kern=Kern(fehler=RuntimeError("Kern weg")))
    lp.schreibe({"t": 1})
    lp.schreibe({"t": 2})
    z = _zeilen(p)
    assert [r["t"] for r in z] == [1, 2]
    assert "eigen" not in z[0] and "Kern weg" in z[0]["eigen_fehler"]
    assert "eigen_fehler" not in z[1]  # der Grund steht nur einmal im Protokoll
