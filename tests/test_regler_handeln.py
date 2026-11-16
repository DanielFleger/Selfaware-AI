"""Regler aendern das Handeln (Daniel 16.11.2026 18:18 "am wichtigsten ... dass auch wirklich anders gehandelt wird wenn man regler umstellt";
18:37 "ja, verbinde die regler"). Je Kopplung: Startgewicht = Verhalten wie vorher, verstellter Regler = andere Entscheidung."""

import json

import pytest

from selfaware.baukasten import regler as RG
from selfaware.micro import wegfuehrung as W
from selfaware.services import gefecht


@pytest.fixture
def regler(tmp_path, monkeypatch):
    datei = tmp_path / "regler.json"
    monkeypatch.setattr(RG, "DATEI", str(datei))
    monkeypatch.setattr(RG, "SCHALTER_DATEI", str(tmp_path / "handeln.json"))
    RG.handeln_setzen(
        True, "Test", "Kopplungen pruefen"
    )  # die Kopplungstests brauchen den Schalter an

    def setzen(**gewichte):
        r = [
            {"id": k, "messgroesse": k, "arten": "alle", "gewicht": float(v), "archiviert": False}
            for k, v in gewichte.items()
        ]
        datei.write_text(json.dumps({"regler": r}), encoding="utf-8")
        RG.neu_lesen()

    yield setzen
    RG.neu_lesen()


def test_ohne_datei_und_mit_startgewichten_wie_vorher(regler):
    assert RG.staerke("kehrtwende") == 1.0
    assert (
        RG.wechsel_huerde() == 1.0
        and RG.leer_runden(W.LEER_RUNDEN) == W.LEER_RUNDEN
        and gefecht.behalten() == gefecht.BEHALTEN
    )
    regler(kehrtwende=-1, steht_ohne_wirkung=-1, vorstoss=1)
    assert (
        RG.wechsel_huerde() == 1.0
        and RG.leer_runden(W.LEER_RUNDEN) == W.LEER_RUNDEN
        and gefecht.behalten() == pytest.approx(gefecht.BEHALTEN)
    )


def test_kehrtwende_staerker_hebt_die_huerde(regler):
    regler(kehrtwende=-5)
    assert RG.wechsel_huerde(24) == pytest.approx(1.4)


def test_leben_einsetzen_staerker_nimmt_knappe_gefechte_an(regler):
    regler(vorstoss=5)
    assert gefecht.behalten() == pytest.approx(0.2)


class _B:
    def __init__(self):
        self.liste = []

    def __call__(self, b, _w=None, bis=None):
        self.liste.append(b)


def _e(owner, typ, x, y, leben=10000, **k):
    d = {"besitzer": owner, "typ": typ, "x": x, "y": y, "leben": leben}
    d.update(k)
    return d


def _bis_kein_weg():
    """Runden, bis ein Speertraeger, der neben seinem Ziel steht und nichts bewirkt, 'kein_weg' meldet (#362)."""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7, "nahkampfraid")
    for runde in range(1, 20):
        st = w.schritt({1: _e(1, 24, 199, 101, zustand=2)}, {7: _e(2, 3, 200, 100, leben=60)}, _B())
        if st[1] == "kein_weg":
            return runde
    return None


def test_steht_ohne_wirkung_staerker_wechselt_frueher(regler):
    regler(steht_ohne_wirkung=-1)
    normal = _bis_kein_weg()
    regler(steht_ohne_wirkung=-3)
    schnell = _bis_kein_weg()
    assert normal == 4 and schnell == 2, (
        normal,
        schnell,
    )  # 1 Runde Angriff, dann 3 bzw. 1 Runde ohne Wirkung


# --- Daniel 16.11.2026 18:50 "versuche alle kopplungen zu machen": Gemeinsam gewirkt, Chance verpasst, Zielwerte ---
from selfaware.baukasten import wirkung as WK  # noqa: E402
from selfaware.baukasten import zielvergabe as ZV  # noqa: E402
from selfaware.micro.tasks import nahkampf as NK  # noqa: E402


class _Wissen:
    """Wert je Takt = Wert / (Felder + 1); keine Messtabellen noetig."""

    def wert_je_takt(self, typ, ort, z, felder=None):
        return z.wert / (felder + 1.0), felder + 1.0

    def dps(self, a, b):
        return 100.0, "test"

    def rechnen_mit(self, typ, z, leben=None, nah=None):
        return 10.0, 1.0


def _ziel(art, nr, ort, wert, typ=3):
    return WK.Ziel((art, nr), typ, ort, float(wert), (), ())


def _waehle(ziele, belegt=()):
    nk = NK.NahkampfRaid(1, wissen=_Wissen())
    z = nk._waehlen(1, _e(1, 24, 100, 100), {z.schluessel: z for z in ziele}, set(belegt), {})
    return None if z is None else z.schluessel


def test_neue_kopplungen_ohne_datei_und_mit_startgewichten_wie_vorher(regler):
    assert RG.dazu_vorzug() == 0.0 and RG.chance_radius() == 0.0
    assert RG.zielwert("gebaeude") == RG.zielwert("arbeiter") == RG.zielwert("soldat") == 1.0
    regler(
        gemeinsam=1,
        chance_verpasst=-1,
        gebaeude_schaden=1,
        gebaeude_zerstoert=1,
        bevoelkerung_kill=1,
        einheit_schaden=1,
        einheit_kill=1,
    )
    assert RG.dazu_vorzug() == 0.0 and RG.chance_radius() == 0.0
    assert RG.zielwert("gebaeude") == RG.zielwert("arbeiter") == RG.zielwert("soldat") == 1.0


def test_zielvergabe_vorzug_nimmt_das_besetzte_ziel():
    frei = lambda k: k != "b"  # noqa: E731
    wahl = lambda li: max(li, key=lambda k: {"a": 10, "b": 8}[k])  # noqa: E731
    wert = {"a": 10, "b": 8}.get
    assert ZV.waehle(["a", "b"], frei, wahl) == ("a", False)
    assert ZV.waehle(["a", "b"], frei, wahl, wert=wert, vorzug=0.2) == (
        "a",
        False,
    )  # 8 x 1,2 = 9,6 < 10
    assert ZV.waehle(["a", "b"], frei, wahl, wert=wert, vorzug=0.3) == (
        "b",
        True,
    )  # 8 x 1,3 = 10,4 > 10


def test_gemeinsam_staerker_stellt_sich_dazu(regler):
    # freies Gebaeude 5 Felder weg (Wert 60 -> 10 je Takt), besetztes 5 Felder weg (Wert 54 -> 9 je Takt)
    ziele = [_ziel("g", 7, (105, 100), 60), _ziel("g", 8, (100, 105), 54)]
    regler(gemeinsam=1)
    assert _waehle(ziele, belegt={("g", 8)}) == ("g", 7)
    regler(gemeinsam=3)  # Vorzug 0,2: 9 x 1,2 = 10,8 > 10
    assert _waehle(ziele, belegt={("g", 8)}) == ("g", 8)


def test_chance_verpasst_staerker_holt_den_arbeiter_statt_zu_warten(regler):
    ziele = [_ziel("e", 9, (110, 100), 10)]  # Arbeiter 10 Felder weg, sonst nichts
    regler(chance_verpasst=-1)
    assert (
        _waehle(ziele) is None
    )  # wie vorher: Arbeiter nur direkt am Weg (ARBEITER_MIT), also warten
    regler(chance_verpasst=-3)  # 10 Felder
    assert _waehle(ziele) == ("e", 9)
    regler(chance_verpasst=-2)  # 5 Felder: zu kurz
    assert _waehle(ziele) is None


def test_zielwerte_verschieben_gebaeude_gegen_arbeiter(regler):
    # Gebaeude 5 Felder weg (60 -> 10 je Takt), Arbeiter direkt daneben (10 -> 5 je Takt)
    ziele = [_ziel("g", 7, (105, 100), 60), _ziel("e", 9, (101, 100), 10)]
    regler(gebaeude_schaden=1, gebaeude_zerstoert=1, bevoelkerung_kill=1)
    assert _waehle(ziele) == ("g", 7)
    regler(gebaeude_schaden=1, gebaeude_zerstoert=1, bevoelkerung_kill=3)  # Arbeiter x3: 15 > 10
    assert _waehle(ziele) == ("e", 9)
    regler(gebaeude_schaden=0, gebaeude_zerstoert=0, bevoelkerung_kill=1)  # Gebaeude ohne Lohn
    assert _waehle(ziele) == ("e", 9)


def test_soldat_lohn_staerker_schlaegt_zurueck(regler):
    nk = NK.NahkampfRaid(1, wissen=_Wissen())
    e, g = _e(1, 24, 100, 100), _e(2, 24, 101, 100, leben=1000)
    z = _ziel("g", 7, (110, 100), 60)
    regler(einheit_schaden=1, einheit_kill=1, gebaeude_schaden=1, gebaeude_zerstoert=1)
    w, k, _ = nk._zurueckschlagen(e, g, z, 10)
    assert w > k  # wie vorher: der Soldat deckt das Ziel nicht, also weiter
    regler(einheit_schaden=5, einheit_kill=5, gebaeude_schaden=1, gebaeude_zerstoert=1)
    w, k, _ = nk._zurueckschlagen(e, g, z, 10)
    assert k > w


def test_schalter_aus_handelt_wie_die_startgewichte(regler):
    # Daniel 16.11.2026 19:30 "Ja, so starten": Regler bewerten nur, aufs Handeln wirken sie erst mit dem Schalter
    regler(
        kehrtwende=-5,
        vorstoss=5,
        gemeinsam=5,
        chance_verpasst=-5,
        bevoelkerung_kill=5,
        einheit_kill=5,
    )
    an = (
        RG.wechsel_huerde(),
        gefecht.behalten(),
        RG.dazu_vorzug(),
        RG.chance_radius(),
        RG.zielwert("arbeiter"),
    )
    RG.handeln_setzen(False, "Test", "aus")
    aus = (
        RG.wechsel_huerde(),
        gefecht.behalten(),
        RG.dazu_vorzug(),
        RG.chance_radius(),
        RG.zielwert("arbeiter"),
    )
    assert aus == (1.0, gefecht.BEHALTEN, 0.0, 0.0, 1.0)
    assert an != aus
    st = RG.handeln_lesen()
    assert st["an"] is False
    assert [(v["alt"], v["neu"]) for v in st["verlauf"]] == [
        (False, True),
        (True, False),
    ]  # Verlauf behaelt beides


def test_ohne_schalterdatei_ist_der_schalter_aus(tmp_path, monkeypatch):
    monkeypatch.setattr(RG, "SCHALTER_DATEI", str(tmp_path / "fehlt.json"))
    assert RG.handeln_lesen()["an"] is False


def test_seite_zeigt_schalter_und_seinen_verlauf(regler, tmp_path, monkeypatch):
    from selfaware.telemetry import wertung as WT
    from selfaware.tools.analysis import wertung_seite as WS

    monkeypatch.setattr(WT, "REGLER_DATEI", str(tmp_path / "seite_regler.json"))
    monkeypatch.setattr(WT, "VERLAUF_DATEI", str(tmp_path / "seite_verlauf.jsonl"))
    RG.handeln_setzen(False, "Seite", "aus")
    a = WS.regler_antwort()
    assert a["handeln"]["an"] is False
    texte = [x for v in a["verlauf"] for x in v["aenderungen"]]
    assert (
        "Regler wirken aufs Handeln: aus -> an" in texte
        and "Regler wirken aufs Handeln: an -> aus" in texte
    )
    assert [v["zeit"] for v in a["verlauf"]] == sorted(
        (v["zeit"] for v in a["verlauf"]), reverse=True
    )
