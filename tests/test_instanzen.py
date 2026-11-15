"""B-192/B-197 (Daniel 15.11.2026 14:18/14:24/14:54): Instanzen heissen nach ihrer Rolle - steam und team-liga - aus EINER Liste
(VillageStudio/lib/instanzen.json); ohne Angabe gilt team-liga, die archivierten 3, 4 und 5 brechen laut ab."""

import pytest

from selfaware.game.ucp import instanzen as I


def test_namen_und_nummern_finden_denselben_ordner(monkeypatch):
    monkeypatch.delenv("SHC_INSTANZ", raising=False)
    assert I.eintrag()["name"] == "team-liga"  # B-197: ohne Angabe nie mehr Steams Ordner
    assert I.eintrag("team-liga") == I.eintrag("2") == I.eintrag(2)
    assert I.eintrag("steam")["nummer"] == 1 and I.eintrag("STEAM")["name"] == "steam"
    assert I.spielordner("team-liga").endswith("Stronghold Crusader Extreme Team-Liga")
    assert I.spielordner("steam").endswith("Stronghold Crusader Extreme")
    monkeypatch.setenv("SHC_INSTANZ", "steam")
    assert I.eintrag()["nummer"] == 1


@pytest.mark.parametrize("wahl", ["3", "4", "5"])
def test_archivierte_instanzen_brechen_laut_ab(wahl):
    with pytest.raises(RuntimeError, match="Archiv"):
        I.eintrag(wahl)


def test_unbekannte_instanz_bricht_ab():
    with pytest.raises(RuntimeError, match="gibt es nicht"):
        I.eintrag("vanilla")


def test_keine_selbst_gebauten_instanzpfade_im_code():
    import pathlib
    import re

    from selfaware import workspace

    muster = re.compile(r"Extreme Instanz|Instanz%d|\"%s Instanz")
    treffer = [
        str(p)
        for p in (pathlib.Path(workspace.ROOT) / "src").rglob("*.py")
        if muster.search(p.read_text(encoding="utf-8", errors="replace"))
    ]
    assert treffer == []
