"""B-182 S138: tools/analysis/spur_laufpruefung.py spielt den Weg einer Einheit aus Konsole und Lageprotokoll durch die Laufpruefung
der Kette - ohne Spiel. Partie 14 (14.11.2026): so liess sich der Lauf-Alarm von Speertraeger 334 als Fehlalarm erkennen."""

import gzip
import json

from selfaware.tools.analysis import spur_laufpruefung as S


def _partie(tmp_path, wege, mit_index):
    """wege: {Takt: (x, y)} der Einheit 5 (Speertraeger), eine Gerade nach Osten auf flachem Boden."""
    (tmp_path / "gelaende_Flach.txt").write_text("", encoding="utf-8")
    konsole = tmp_path / "konsole.txt"
    konsole.write_text(
        "KETTE Laufpruefung: Gelaende aus gelaende_Flach.txt\n"
        'BEFEHL Tick 950 angriff {"lauf":[300,100]} an 2 Einheiten: [5, 6]\n'
        'BEFEHL Tick 980 angriff {"lauf":[300,100]} an 1 Einheiten: [6]\n',
        encoding="utf-8",
    )
    lage = tmp_path / "lage.jsonl.gz"
    with gzip.open(lage, "wt", encoding="utf-8") as f:
        for t, (x, y) in sorted(wege.items()):
            einheiten = (
                "tick %d\nnr besitzer typ x y leben zustand laufx laufy\n5 1 24 %d %d 10000 101 300 100\n"
                % (t, x, y)
            )
            eigen = (
                "kern_tick %d ich 1\nnr typ x y wegindex weglaenge tempo\n5 24 %d %d %d 200 1\n"
                % (t, x, y, x - 100)
            )
            f.write(
                json.dumps(
                    {
                        "t": t,
                        "einheiten": einheiten,
                        "gebaeude": "nr besitzer typ x y leben\n",
                        **({"eigen": eigen} if mit_index else {}),
                    }
                )
                + "\n"
            )
    return str(konsole), str(lage)


def test_eine_einheit_im_takt_des_modells_gibt_keinen_alarm_eine_stehende_schon(
    tmp_path, monkeypatch
):
    import selfaware.tools.experiments.gelaende_erheben as GE

    monkeypatch.setattr(S, "tile_function", lambda pfad: lambda x, y: (0x8000, 1, 8))
    monkeypatch.setattr(S._workspace, "DATA", str(tmp_path))
    assert GE.tile_function  # die echte Funktion bleibt unberuehrt
    for mit_index in (True, False):
        laeuft = {
            1000 + 120 * i: (100 + 10 * i, 100) for i in range(8)
        }  # 12 Takte je Feld: wie das Modell
        zeilen = S.nachspielen(*_partie(tmp_path, laeuft, mit_index), 5)
        assert [z[0] for z in zeilen] == sorted(laeuft) and not any(z[6] for z in zeilen)
        steht = {
            t: (min(p[0], 130), 100) for t, p in laeuft.items()
        }  # ab Takt 1360 steht sie auf (130, 100)
        zeilen = S.nachspielen(*_partie(tmp_path, steht, mit_index), 5)
        alarm = [z for z in zeilen if z[6]]
        assert alarm and "WALK BEHIND THE TERRAIN" in alarm[0][6][0] and alarm[0][0] >= 1480


def test_befehle_nur_an_diese_einheit_mit_dem_gelaende_aus_der_konsole(tmp_path):
    konsole, _ = _partie(tmp_path, {1000: (100, 100)}, True)
    befehle, gelaende = S.befehle(konsole, 5)
    assert (
        befehle == [(950, {"angriff": {"lauf": [300, 100], "einheiten": [5]}})]
        and gelaende == "gelaende_Flach.txt"
    )
