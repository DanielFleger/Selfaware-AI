"""B-184 (15.11.2026): der Kern fuehrt die Einheiten der Plaetze, die SamurAI uebernommen hat - nicht die des Menschen am Rechner.
Partie 34 (Mensch 1, SamurAI 2): 65.473 Kern-Befehle an SamurAIs Einheiten verweigert. Der Lenker schreibt die Plaetze als Bitmaske
in den Ringkopf (RING_START+8); crates/samurai-kern/src/lib.rs (darf_fuehren) liest sie."""

import pathlib
import re

import pytest

from selfaware import workspace
from selfaware.execution import kernweg as KW
from selfaware.game import kern_leitung as KL


def leitung_im_speicher():
    le = object.__new__(KL.Leitung)
    le.speicher = bytearray(KL.GROESSE)
    return le


def test_plaetze_landen_als_maske_im_ringkopf():
    le = leitung_im_speicher()
    assert le.eigene_plaetze() == [], (
        "frisch: nicht gesetzt - der Kern nimmt dann den Platz des Menschen"
    )
    assert le.eigene_plaetze_setzen([2]) == 0b100
    assert int.from_bytes(le.speicher[KL.EIGENE_PLAETZE : KL.EIGENE_PLAETZE + 4], "little") == 0b100
    le.eigene_plaetze_setzen((2, 4))
    assert le.eigene_plaetze() == [2, 4]
    for falsch in ([0], [9], []):
        with pytest.raises(ValueError):
            le.eigene_plaetze_setzen(falsch)


def test_kernweg_gibt_den_platz_weiter(monkeypatch):
    gesetzt = []

    class Attrappe:
        def __init__(self, ordner):
            pass

        def lesen(self):
            return type("Welt", (), {"kern": 40})()

        def eigene_plaetze_setzen(self, plaetze):
            gesetzt.append(tuple(plaetze))

    monkeypatch.setattr(KL, "Leitung", Attrappe)
    assert KW.oeffnen("ordner", plaetze=(2,)) is not None and gesetzt == [(2,)]
    KW.oeffnen("ordner")
    assert gesetzt == [(2,)], "ohne Angabe bleibt die Maske unberuehrt"


def test_lenker_oeffnet_den_kernweg_immer_mit_seinem_platz():
    text = pathlib.Path(workspace.ROOT, "src/selfaware/runtime/live/erstes_spiel.py").read_text(
        encoding="utf-8"
    )
    aufrufe = re.findall(r"KW\.oeffnen\(([^)]*)\)", text)
    assert len(aufrufe) >= 3 and all("plaetze=(SP," in a for a in aufrufe), aufrufe


def test_kern_liest_dieselbe_stelle():
    """Beide Seiten zeigen auf Ringkopf +8: Python EIGENE_PLAETZE, Rust zaehler(8) in eigene_plaetze()."""
    assert KL.EIGENE_PLAETZE == KL.RING_START + 8
    rs = pathlib.Path(workspace.ROOT, "crates/samurai-kern/src/leitung.rs").read_text(
        encoding="utf-8"
    )
    teil = rs[rs.index("pub fn eigene_plaetze") :]
    assert "self.zaehler(8)" in teil[: teil.index("}")]
    lib = pathlib.Path(workspace.ROOT, "crates/samurai-kern/src/lib.rs").read_text(encoding="utf-8")
    assert (
        "if !darf_fuehren(platz, maske)" in lib
        and "i32_bei(SLOT_ICH) };\r\n    if platz != ich" not in lib
    )


def test_zwei_lenker_behalten_beide_plaetze():
    """Daniel 15.11.2026 20:27: 2 SamurAIs gegen den Kriegsfuerst - zwei Lenker, jeder meldet seinen Platz; keiner loescht den anderen."""
    le = leitung_im_speicher()
    le.eigene_plaetze_setzen([2])
    le.eigene_plaetze_setzen([3])
    assert le.eigene_plaetze() == [2, 3]


def test_kernweg_meldet_seine_plaetze_vor_jedem_auftrag():
    """Der Kern leert die Plaetze beim Partiewechsel - darum meldet der Kernweg sie vor jeder Uebernahme neu."""
    folge = []

    class Ring:
        def eigene_plaetze_setzen(self, plaetze):
            folge.append(("plaetze", tuple(plaetze)))

        def auftrag(self, art, nr, *rest):
            folge.append(("auftrag", art, nr))
            return len(folge)

    k = KW.Kernweg(Ring())
    k._uebergeben([7])
    assert folge == [("auftrag", KL.UEBERNEHMEN, 7)], "ohne Plaetze wie frueher"
    folge.clear()
    k.plaetze = (3,)
    k._einreihen([8], KL.UEBERNEHMEN, 0, 0, 0, 100)
    assert folge[0] == ("plaetze", (3,)) and ("auftrag", KL.UEBERNEHMEN, 8) in folge[1:], folge


def test_kern_leert_die_plaetze_beim_partiewechsel():
    rs = pathlib.Path(workspace.ROOT, "crates/samurai-kern/src/leitung.rs").read_text(
        encoding="utf-8"
    )
    teil = rs[rs.index("pub fn eigene_plaetze_leeren") :]
    assert "self.zaehler(8).store(0" in teil[: teil.index("}")]
    lib = pathlib.Path(workspace.ROOT, "crates/samurai-kern/src/lib.rs").read_text(encoding="utf-8")
    arm = lib[lib.index("Ereignis::Epoche { von, nach } => {") :]
    assert "l.eigene_plaetze_leeren()" in arm[: arm.index("schreibe(")]
