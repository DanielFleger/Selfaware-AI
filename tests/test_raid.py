"""B-179: Raid als eigenes Modul, ohne Spiel."""

import ast
import pathlib
import re

import pytest

from selfaware.baukasten import aufstellung as AF
from selfaware.baukasten import raid as RB
from selfaware.micro.tasks import raids as RA

LENKER = (
    pathlib.Path(__file__).resolve().parents[1] / "src/selfaware/runtime/live/erstes_spiel.py"
).read_text(encoding="utf-8")
SKLAVE, SCHLEUDER, ASSASSINE, REITER = 71, 72, 73, 74


def lage(**felder):
    """Alles auf Soll, genug Gold, ungerade Runde."""
    werte = {
        "runde": 1,
        "gold": 1000,
        "ruecklage": 0,
        "ruecklage_soeldner": 0,
        "feuer": 20,
        "endspurt": False,
        "soeldner_erlaubt": True,
        "assassine_erlaubt": True,
        "sklaven": RA.SKLAVEN_SOLL,
        "reiter": RA.REITER_SOLL,
        "schleuderer": 0,
    }
    return RB.Lage(**{**werte, **felder})


ALT = RB.RaidBestellung()
KASSE = RB.RaidBestellungMitKasse()


def test_alte_bestellung_gibt_dasselbe_gold_zweimal_aus():
    """P3.12: So lief es in der Partie raid_frueh, die Aufstellung soll das weiter koennen."""
    assert ALT.schritt(lage(gold=78, reiter=2)) == [(ASSASSINE, 1), (REITER, 1)]


def test_alte_bestellung_wirbt_soeldner_nur_in_ungeraden_runden():
    assert ALT.schritt(lage(runde=2, sklaven=0)) == [(ASSASSINE, 1)]
    assert (SKLAVE, RA.SKLAVEN_SOLL) in ALT.schritt(lage(runde=3, sklaven=0))


def test_alte_bestellung_wirbt_im_endspurt_keine_soeldner():
    assert ALT.schritt(lage(endspurt=True, sklaven=0)) == [(ASSASSINE, 1)]


def test_alte_bestellung_wirbt_ohne_erlaubnis_keine_soeldner():
    assert ALT.schritt(lage(soeldner_erlaubt=False, sklaven=0)) == [(ASSASSINE, 1)]


@pytest.mark.parametrize(
    "felder",
    [{"gold": 69}, {"gold": 99, "ruecklage": 30}, {"feuer": 0}, {"assassine_erlaubt": False}],
)
def test_alte_bestellung_assassine_braucht_gold_feuer_und_erlaubnis(felder):
    assert ALT.schritt(lage(**felder)) == []


def test_alte_bestellung_rechnet_die_soeldner_mit_ihrer_eigenen_ruecklage():
    """Mit Heereskasse zaehlt fuer die Soeldner eine andere Ruecklage als fuer die Assassine."""
    assert ALT.schritt(lage(gold=80, ruecklage=500, ruecklage_soeldner=0, reiter=2)) == [
        (REITER, 1)
    ]


def test_kasse_gibt_das_gold_nur_einmal_aus():
    assert KASSE.schritt(lage(gold=78, reiter=2)) == [(REITER, 1)]


def test_kasse_kauft_in_der_reihenfolge_sklaven_reiter_assassinen():
    k = KASSE.schritt(lage(sklaven=RA.SKLAVEN_SOLL - 1, reiter=RA.REITER_SOLL - 1))
    assert k == [(SKLAVE, 1), (REITER, 1), (ASSASSINE, 1)]


def test_was_fehlt_geht_vor_auch_wenn_das_gold_noch_nicht_reicht():
    assert KASSE.schritt(lage(gold=72, reiter=2)) == []


def test_kasse_kauft_nur_so_viele_wie_das_gold_hergibt_und_spart_dann():
    assert KASSE.schritt(lage(gold=160, reiter=0)) == [(REITER, 2)]


def test_in_geraden_runden_wartet_die_assassine_auf_fehlende_soeldner():
    assert KASSE.schritt(lage(runde=2, sklaven=RA.SKLAVEN_SOLL - 1)) == []


def test_in_geraden_runden_kauft_die_assassine_wenn_nichts_fehlt():
    assert KASSE.schritt(lage(runde=2)) == [(ASSASSINE, 1)]


@pytest.mark.parametrize("felder", [{"soeldner_erlaubt": False}, {"endspurt": True}])
def test_soeldner_die_gar_nicht_geworben_werden_halten_niemanden_auf(felder):
    assert KASSE.schritt(lage(sklaven=0, reiter=0, **felder)) == [(ASSASSINE, 1)]


def test_kasse_laesst_die_leute_am_feuer():
    assert KASSE.schritt(lage(feuer=RA.FEUER_MIN + 1, sklaven=0)) == [(SKLAVE, 1)]


def test_kasse_achtet_die_ruecklage():
    assert KASSE.schritt(lage(gold=100, ruecklage=30, reiter=2)) == []
    assert KASSE.schritt(lage(gold=100, ruecklage=500, reiter=2)) == []


def test_kasse_kauft_keine_assassine_ohne_erlaubnis():
    assert KASSE.schritt(lage(assassine_erlaubt=False)) == []


def test_assassine_braucht_nur_einen_am_feuer():
    assert KASSE.schritt(lage(feuer=1)) == [(ASSASSINE, 1)]
    assert KASSE.schritt(lage(feuer=0)) == []


def test_schleuderer_stehen_vor_den_reitern(monkeypatch):
    monkeypatch.setattr(RA, "DECKUNG_SOLL", 2)
    assert KASSE.schritt(lage(reiter=2)) == [(SCHLEUDER, 2), (REITER, 1), (ASSASSINE, 1)]


def test_reihenfolge_laesst_sich_per_aufstellung_aendern():
    k = RB.RaidBestellungMitKasse(("assassinen", "sklaven", "schleuderer", "reiter"))
    assert k.schritt(lage(gold=75, sklaven=RA.SKLAVEN_SOLL - 1)) == [(ASSASSINE, 1), (SKLAVE, 1)]


def test_reihenfolge_lesen():
    assert RB.reihenfolge_lesen("reiter, sklaven,schleuderer,assassinen")[0] == "reiter"


@pytest.mark.parametrize(
    "text", ["", "sklaven", "sklaven,sklaven,reiter,assassinen", "sklaven,schleuderer,reiter,bogen"]
)
def test_falsche_reihenfolge_faellt_auf(text):
    with pytest.raises(ValueError):
        RB.reihenfolge_lesen(text)


class Attrappe:
    def __init__(self, name, log):
        self.name, self.log, self.schutz, self.im_ausweichen = name, log, None, {"x"}

    def plaetze_setzen(self, belegt):
        self.log.append((self.name, "plaetze", belegt))

    def orte(self, L):
        return [self.name]

    def schritt(self, *a):
        self.log.append((self.name, "schritt", len(a)))
        return [self.name]


class Steck:
    def __init__(self, log):
        self.log, self.gebaut = log, {}

    def klasse(self, name):
        def bauen(*a, **k):
            self.gebaut[name] = (a, k)
            return Attrappe(name, self.log)

        return bauen


def test_einsatz_steuert_in_der_reihenfolge_von_bisher():
    log = []
    s = Steck(log)
    e = RB.RaidEinsatz(1, (9, 9), "feuer", s, vorstoss_bis=15000, gelaende=["Gs."])
    assert e.schritt(100, {}, {}, "befehl") == [
        "vorstoss",
        "deckung",
        "brandtrupp",
        "reiterjagd",
        "nahkampfraid",
    ]
    assert [x[:2] for x in log] == [
        ("vorstoss", "plaetze"),
        ("vorstoss", "schritt"),
        ("deckung", "schritt"),
        ("brandtrupp", "schritt"),
        ("reiterjagd", "schritt"),
        ("nahkampfraid", "schritt"),
    ]
    assert log[0][2] == {"x"} and e.brand.schutz == ["deckung", "vorstoss"]
    assert s.gebaut["brandtrupp"] == ((1, "feuer"), {}) and s.gebaut["vorstoss"] == (
        (1, (9, 9)),
        {"bis": 15000},
    )
    assert s.gebaut["nahkampfraid"] == ((1, ["Gs."]), {})


def test_einsatz_ohne_vorstoss():
    e = RB.RaidEinsatz(1, (9, 9), "feuer", Steck([]))
    assert e.vorstoss is None
    assert e.schritt(100, {}, {}, "befehl") == [
        "deckung",
        "brandtrupp",
        "reiterjagd",
        "nahkampfraid",
    ]
    assert e.brand.schutz == ["deckung"]


def _aufrufe(baum, *ziele):
    return [
        k
        for k in ast.walk(baum)
        if isinstance(k, ast.Call)
        and isinstance(k.func, ast.Attribute)
        and k.func.attr == "schritt"
        and isinstance(k.func.value, ast.Name)
        and k.func.value.id in ziele
    ]


def _vorfahren(baum, knoten):
    eltern = {kind: k for k in ast.walk(baum) for kind in ast.iter_child_nodes(k)}
    while knoten in eltern:
        knoten = eltern[knoten]
        yield knoten


def test_raid_und_bier_stehen_nicht_mehr_im_angriffszweig():
    baum = ast.parse(LENKER)
    aufrufe = _aufrufe(baum, "raid_e", "raid_b", "bier")
    assert len(aufrufe) == 3
    for a in aufrufe:
        for k in _vorfahren(baum, a):
            if isinstance(k, ast.If):
                namen = {n.id for n in ast.walk(k.test) if isinstance(n, ast.Name)}
                assert not namen & {"streitkolben", "feldzug"}, ast.unparse(k.test)


def test_ein_fehler_im_raid_beendet_die_partie_nie():
    """Das naechste try um den Aufruf muss das sein, das weiterspielt. Ein try weiter aussen genuegt nicht."""
    baum = ast.parse(LENKER)
    for a in _aufrufe(baum, "raid_e", "raid_b", "bier"):
        naechstes = next(k for k in _vorfahren(baum, a) if isinstance(k, ast.Try))
        fang = "".join(ast.unparse(h) for h in naechstes.handlers)
        assert "Partie laeuft weiter" in fang, a.lineno


def test_ohne_schalter_laeuft_der_raid_nur_mit_feldzug():
    assert "raid_laeuft = raid_e is not None and (feldzug is not None or OHNE_ANGRIFF)" in LENKER


def test_alles_von_soeldnern_und_assassinen_geht_durch_die_eine_bestellung():
    assert "RA.werbung(" not in LENKER


def test_preise_stimmen_mit_dem_lenker_ueberein():
    preise = dict(
        re.findall(r"(\d+): (\d+)", re.search(r"^SOELDNER_GOLD = \{(.*?)\}", LENKER, re.M).group(1))
    )
    assert int(preise["73"]) == RB.ASSASSINE_GOLD
    for typ, preis in RB.EINHEITEN.values():
        assert int(preise[str(typ)]) == preis, typ


def test_die_aufstellungen_trennen_die_wirkung():
    frueh, kasse, ohne = (AF.laden(n) for n in ("raid_frueh", "raid_kasse", "raid_ohne_angriff"))
    assert not frueh.get("versionen")
    assert kasse["schalter"] == frueh["schalter"]
    pfad = "selfaware.baukasten.raid:RaidBestellungMitKasse"
    assert (
        kasse["versionen"] == {"raidbestellung": pfad} and ohne["versionen"] == kasse["versionen"]
    )
    anders = {
        k
        for k in set(ohne["schalter"]) | set(kasse["schalter"])
        if ohne["schalter"].get(k) != kasse["schalter"].get(k)
    }
    assert anders == {"streitkolben", "ohne_angriff"}
    assert ohne["schalter"]["bier"] == "ja"


def test_aufstellung_steckt_die_neue_bestellung():
    versionen = AF.laden("raid_kasse")["versionen"]
    assert AF.Steckplaetze(versionen).klasse("raidbestellung") is RB.RaidBestellungMitKasse
    assert AF.Steckplaetze().klasse("raidbestellung") is RB.RaidBestellung
