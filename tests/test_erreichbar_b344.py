"""B-344 (15.11.2026): Erreichbarkeit vom EIGENEN Bergfried-Eingang und fuer den EIGENEN Spieler. Vorher rechnete logik.lua vom festen
Punkt (165,111) fuer den Platz am Rechner - in Lobby-Partien bekam jedes Feindgebaeude 0, die Assassinen fanden kein Ziel (gemessen
21:07 und 22:00: 49/49 auf 0, 155 Assassinen, 89 auf einem Fleck). Nach dem Fix 22:04: 46/46 Feindgebaeude erreichbar."""

import pathlib

from selfaware import workspace
from selfaware.micro.tasks import waechter as W


def test_lenker_schickt_eingang_und_spieler(monkeypatch, tmp_path):
    gesendet = []
    datei = tmp_path / "lagebild.txt"
    datei.write_text("tick 1\nkopf\n", encoding="utf-8")
    monkeypatch.setattr(W, "LAGEBILD", str(datei))
    monkeypatch.setattr(W, "befehl", lambda cmd, *a, **k: gesendet.append(cmd))
    monkeypatch.setattr(W, "BERGFRIED_EINGANG", (174, 112))
    W.lies_lagebild(True)
    assert gesendet and gesendet[0]["von"] == [174, 112] and "fuer" in gesendet[0]


def test_spielmodul_nimmt_startpunkt_und_spieler_vom_befehl():
    lua = pathlib.Path(workspace.ROOT, "bridge/snapshots/logik_stand_20261115.lua").read_text(
        encoding="utf-8"
    )
    block = lua[lua.index("if cmd.lagebild ~= nil then") :][:4000]
    assert 'type(cmd.von) == "table"' in block and "tonumber(cmd.fuer)" in block
    assert "for r = 1, 4 do" in block, (
        "Eingangsfeld liegt oft in keinem Gebiet - Nachbarn bis 4 Felder"
    )
