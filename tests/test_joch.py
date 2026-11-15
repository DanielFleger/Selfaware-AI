"""S168 (Daniel 15.11.2026 11:29): Ochsenjoche an den Steinhaufen des Bruchs, mit einem freien Feld dazwischen - ohne Spiel."""
import pathlib
import re

from selfaware.macro import joch as JO
from selfaware.runtime.live import erstes_spiel as ES

SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "selfaware"


def test_haufen_liegt_bei_bruch_plus_7_2():
    # gemessen 15.11.2026: 240 von 240 Steinbruechen in 60 Lageprotokollen, alle vier Kartenviertel
    assert JO.haufen((98, 150)) == (105, 152) and JO.haufen((71, 243)) == (78, 245)


def test_joch_beruehrt_den_haufen_nie_auch_nicht_ueber_eck():
    h = (78, 245)                       # Haufen 78..80 x 245..247
    s = JO.sperre(h)
    assert not JO.frei((78, 243), s)    # Partie 33: dieses Joch stand direkt ueber dem Haufen
    assert not JO.frei((76, 243), s)    # ueber Eck
    assert not JO.frei((81, 246), s)    # rechts daneben
    assert JO.frei((78, 242), s)        # eine freie Reihe (244) dazwischen
    assert JO.frei((82, 246), s)        # eine freie Spalte (81) dazwischen
    assert JO.frei((78, 249), s)        # unten, eine freie Reihe (248)


def test_baue_schnell_nimmt_den_ersten_platz_ausserhalb_der_sperre(monkeypatch):
    gesendet = []

    def befehl(b, *a, **k):
        gesendet.append(b)
        if "platzsuche" in b:
            return ["PLATZSUCHE geprueft: (79,247) (81,246) (82,246) (78,249)"]
        return ["OK"]

    monkeypatch.setattr(ES, "befehl", befehl)
    monkeypatch.setattr(ES, "BUCH", None)
    monkeypatch.setattr(ES, "GZ", None)
    assert ES.baue_joch((71, 243), zweck="Probe") == (82, 246)
    such = next(b["platzsuche"] for b in gesendet if "platzsuche" in b)
    assert (such["x"], such["y"]) == JO.mitte((78, 245)) and such["max"] == 40
    assert next(b["baue"] for b in gesendet if "baue" in b)["x"] == 82


def test_jeder_jochbau_im_spiel_haelt_abstand():
    # jede Stelle, die im laufenden Spiel ein Ochsenjoch (Typ 4) baut, geht ueber die eine Regel (macro/joch.py)
    stellen = []
    for datei in ("runtime/live/erstes_spiel.py", "macro/ertragsplaner.py", "macro/wirtschaft.py"):
        for i, z in enumerate((SRC / datei).read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"(baue_schnell|self\.baue|self\._bau)\(4,", z):
                stellen.append((datei, i, "frei_von=" in z))
    assert stellen and all(ok for _, _, ok in stellen), stellen
