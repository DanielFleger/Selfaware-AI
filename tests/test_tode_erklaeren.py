"""S156 (15.11.2026): tools/analysis/tode_erklaeren.py erklaert auf Wunsch die Tode anderer eigener Arten (typen=) - ohne Spiel."""

import gzip
import json

from selfaware.tools.analysis import tode_erklaeren as T

KOPF = (
    "nr besitzer typ x y leben zustand zielart zieleinheit zieluid zielgebaeude ziel zielx ziely laufx laufy auswahlvon "
    "auswahlmarke gruppe gruppenuid ladung arbeitsplatz erreichbar nahziel nahangreifer"
)


def _e(nr, typ, leben, x=100, y=100, zustand=101):
    return " ".join(map(str, [nr, 1, typ, x, y, leben, zustand] + [0] * 7 + [x, y] + [0] * 9))


def _lage(pfad, runden):
    with gzip.open(pfad, "wt", encoding="utf-8") as f:
        for t, zeilen in runden:
            f.write(
                json.dumps(
                    {
                        "t": t,
                        "st": {"t": t},
                        "einheiten": "tick %d\n%s\n%s" % (t, KOPF, "\n".join(zeilen)),
                        "gebaeude": "nr besitzer typ x y leben uid erreichbar vorrat grenze verbund ware feuer",
                    }
                )
                + "\n"
            )


def test_typen_waehlt_die_arten_und_eine_neu_vergebene_nummer_zaehlt_als_tod(tmp_path):
    lage = tmp_path / "lage.jsonl.gz"
    # 5: Speertraeger verliert Leben und verschwindet; 7: Speertraeger, die Nummer traegt danach ein Schwertkaempfer; 9: Assassine
    _lage(
        lage,
        [
            (100, [_e(5, 24, 12500), _e(7, 24, 12500), _e(9, 73, 12500)]),
            (150, [_e(5, 24, 9000), _e(7, 24, 4000), _e(9, 73, 12500)]),
            (200, [_e(7, 75, 32000)]),
        ],
    )
    konsole = tmp_path / "konsole.txt"
    konsole.write_text("", encoding="utf-8")
    speer = T.auswerten(str(konsole), str(lage), typen=(24,))
    assert sorted((b["nr"], b["typ"], b["tick"]) for b in speer) == [(5, 24, 150), (7, 24, 150)]
    assert {b["nr"]: b["leben_vorher"] for b in speer} == {5: 12500, 7: 12500}
    assert [(b["nr"], b["typ"]) for b in T.auswerten(str(konsole), str(lage))] == [(9, 73)]
