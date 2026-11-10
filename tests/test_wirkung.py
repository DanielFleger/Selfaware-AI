"""B-181: Einheiten-Katalog, Wirkung je Gold, Kauf nach Wirkung und Nahkampf-Raid, ohne Spiel."""

import pathlib
import re

import pytest

import selfaware.services.schussfeld as schussfeld
from selfaware.baukasten import aufstellung as AF
from selfaware.baukasten import einheiten as EH
from selfaware.baukasten import raid as RB
from selfaware.baukasten import wirkung as WK
from selfaware.micro.tasks import nahkampf as NK

WURZEL = pathlib.Path(__file__).resolve().parents[1]
LENKER = (WURZEL / "src/selfaware/runtime/live/erstes_spiel.py").read_text(encoding="utf-8")
SKLAVE, ASSASSINE, SCHWERT, BOGEN, LORD = 71, 73, 75, 22, 55
# Kleine Tabelle mit Werten in der Groessenordnung der Duelle: Bogen trifft Sklaven hart, den arabischen Schwertkaempfer kaum
TAB = (
    {75: {24: 70.0}, 73: {24: 100.0}, 71: {24: 10.0}, 22: {71: 50.0, 75: 2.4}},
    {71: 6000, 75: 28000, 73: 12500, 22: 10000},
    {22: {71: 50.0, 75: 2.4, 73: 10.0}},
)
GEB = {1: {"rate": 0.4, "leben_max": 100}, 3: {"rate": 0.0, "leben_max": 60}}


def wissen():
    return WK.Wissen(tabelle=TAB, gebaeude=GEB)


def geb(x, y, typ=1, besitzer=2):
    return {"typ": typ, "x": x, "y": y, "besitzer": besitzer}


def einheit(x, y, typ, besitzer=2, leben=1000):
    return {"typ": typ, "x": x, "y": y, "besitzer": besitzer, "leben": leben}


def huetten(n_bogen=0):
    G = {1: geb(50, 0), 2: geb(52, 0)}
    L = {100 + i: einheit(51, 3, BOGEN) for i in range(n_bogen)}
    return L, G


def test_katalog_kennt_alle_achtzehn_arten_und_den_lord():
    quelle = (WURZEL / "src/selfaware/tools/experiments/auge_lauf_s.py").read_text(encoding="utf-8")
    soldaten = {
        int(x)
        for x in re.findall(r"\d+", re.search(r"SOLDATEN = \((.*?)\)", quelle, re.S).group(1))
    }
    assert set(EH.ARTEN) == soldaten and len(soldaten) == 19


def test_der_lord_verteidigt_nur_und_ist_nie_kaufbar():
    assert EH.ARTEN[LORD].rollen == {"verteidigung"}
    assert (
        not EH.darf(LORD, "raid")
        and not EH.darf(LORD, "angriff")
        and not EH.kaufbar_am_posten(LORD)
    )


def test_gold_im_katalog_stimmt_mit_dem_lenker():
    preise = dict(
        re.findall(r"(\d+): (\d+)", re.search(r"^SOELDNER_GOLD = \{(.*?)\}", LENKER, re.M).group(1))
    )
    for typ, gold in preise.items():
        assert EH.ARTEN[int(typ)].gold == int(gold), typ
    assert EH.ARTEN[26].gold == int(re.search(r"^KAEMPFER_GOLD = (\d+)", LENKER, re.M).group(1))
    assert EH.ARTEN[24].gold is None  # nicht gemessen, also nicht geraten


def test_leben_kommt_erst_aus_dem_lagebild_dann_aus_den_duellen():
    w = wissen()
    assert w.leben(SKLAVE) == (6000, "Duell") and w.leben(99) == (WK.LEBEN_ERSATZ, "Ersatz")
    w.lernen({1: einheit(0, 0, SKLAVE, besitzer=1, leben=15000)}, 1)
    assert w.leben(SKLAVE) == (15000, "Lagebild")


def test_ziele_sind_nur_fremde_mit_ihrer_deckung():
    L, G = huetten(n_bogen=2)
    G[3] = geb(10, 10, besitzer=1)
    L[200] = einheit(60, 60, 3)  # feindlicher Holzfaeller, ungedeckt
    z = {x.schluessel: x for x in WK.ziele(L, G, 1)}
    assert set(z) == {("g", 1), ("g", 2), ("e", 200)}
    assert z[("g", 1)].schuetzen == (BOGEN, BOGEN) and z[("e", 200)].schuetzen == ()


def test_schuetzen_greifen_keine_gebaeude_an_und_sklaven_zuenden_alles_an():
    w = wissen()
    L, G = huetten()
    G[3] = geb(60, 0, typ=3)
    z = {x.schluessel: x for x in WK.ziele(L, G, 1)}
    assert w.am_ziel(BOGEN, z[("g", 1)])[1] == 0
    assert (
        w.am_ziel(SCHWERT, z[("g", 3)])[1] == 0
    )  # Assassinen-Rate 0: Nahkampf richtet dort nichts aus
    assert w.am_ziel(SKLAVE, z[("g", 3)]) == (WK.FEUER_TAKTE, 1.0)


def test_ungedeckte_huetten_kauft_er_als_sklaven():
    L, G = huetten()
    k, text = WK.kaufen(wissen(), 300, 20, {SKLAVE: 5, SCHWERT: 100}, (0, 0), WK.ziele(L, G, 1))
    assert k == [(SKLAVE, 1)]
    assert "WIRKUNG-KAUF: 1 Sklave (Typ 71)" in text[0]


def test_stark_gedeckte_huetten_kauft_er_als_schwere_einheit():
    """Daniel 10.11.: Sind die Gebaeude verteidigt, braucht es schwerere Einheiten. Keine Regel sagt das, es kommt aus der Rechnung."""
    L, G = huetten(n_bogen=20)
    k, _ = WK.kaufen(wissen(), 300, 20, {SKLAVE: 5, SCHWERT: 100}, (0, 0), WK.ziele(L, G, 1))
    assert k[0] == (SCHWERT, 1) and dict(k).get(SKLAVE, 0) == 0


def test_was_abgedeckt_ist_zaehlt_fuer_die_naechste_nicht_mehr():
    L, G = huetten(n_bogen=3)
    k, _ = WK.kaufen(wissen(), 1000, 50, {SKLAVE: 5}, (0, 0), WK.ziele(L, G, 1))
    assert (
        1 < dict(k)[SKLAVE] < 10
    )  # mehrere Sklaven, weil jeder einzelne oft faellt, aber nicht ohne Ende


def test_kasse_leute_und_hoechstzahl_begrenzen():
    L, G = huetten(n_bogen=3)
    z = WK.ziele(L, G, 1)
    assert WK.kaufen(wissen(), 4, 20, {SKLAVE: 5}, (0, 0), z)[0] == []
    assert WK.kaufen(wissen(), 1000, 3, {SKLAVE: 5}, (0, 0), z, bleibt={SKLAVE: 2})[0] == [
        (SKLAVE, 1)
    ]
    assert WK.kaufen(wissen(), 1000, 50, {SKLAVE: 5}, (0, 0), z, hoechstens={SKLAVE: 1})[0] == [
        (SKLAVE, 1)
    ]


def test_ohne_ziele_wird_nichts_gekauft():
    assert WK.kaufen(wissen(), 1000, 20, {SKLAVE: 5, SCHWERT: 100}, (0, 0), [])[0] == []


def _lage(**felder):
    L, G = huetten()
    werte = dict(
        runde=1,
        gold=300,
        ruecklage=0,
        ruecklage_soeldner=0,
        feuer=20,
        endspurt=False,
        soeldner_erlaubt=True,
        assassine_erlaubt=True,
        sklaven=0,
        reiter=0,
        schleuderer=0,
        L=L,
        G=G,
        sp=1,
        start=(0, 0),
        steuerbar=frozenset({SKLAVE, SCHWERT, LORD, 24}),
    )
    return RB.Lage(**{**werte, **felder})


def _bestellung():
    b = RB.RaidBestellungNachWirkung()
    b._wissen = wissen()
    return b


def test_bestellung_nach_wirkung_kauft_nur_was_ein_modul_fuehren_kann_und_nie_den_lord():
    b = _bestellung()
    assert b.schritt(_lage()) == [(SKLAVE, 1)]
    assert (
        b.schritt(_lage(steuerbar=frozenset({LORD, 24}))) == []
    )  # Lord nie, Speertraeger brauchen eine Kaserne
    assert b.begruendung == []


def test_bestellung_nach_wirkung_wartet_auf_ungerade_runden_und_beachtet_vergebene_ziele():
    b = _bestellung()
    assert b.schritt(_lage(runde=2)) == []
    assert b.schritt(_lage(belegt=frozenset({("g", 1), ("g", 2)}))) == []
    assert b.schritt(_lage(soeldner_erlaubt=False)) == []


def test_aufstellung_raid_wirkung_steckt_die_neue_bestellung():
    d = AF.laden("raid_wirkung")
    assert AF.Steckplaetze(d["versionen"]).klasse("raidbestellung") is RB.RaidBestellungNachWirkung
    assert d["schalter"] == AF.laden("raid_ohne_angriff")["schalter"]


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, warte, bis=None):
        self.liste.append(b)


def _raid(gelaende=None):
    return NK.NahkampfRaid(1, gelaende, wissen=wissen())


def test_nahkampf_raid_nimmt_nur_bestellte_einheiten():
    r, bf = _raid(), Befehle()
    L, G = huetten()
    L[1] = einheit(0, 0, 24, besitzer=1)  # Starttruppe
    r.schritt(L, G, bf)
    L[2], L[3] = einheit(1, 0, SCHWERT, besitzer=1, leben=28000), einheit(1, 1, 24, besitzer=1)
    r.bestellt(SCHWERT, 1)
    r.schritt(L, G, bf)
    assert r.mitglieder == {2}
    assert bf.liste == [{"angriff": {"einheiten": [2], "gebaeude": 1}}]


def test_nahkampf_raid_laeuft_den_sicheren_weg_und_greift_dann_an(monkeypatch):
    monkeypatch.setattr(
        schussfeld, "sicherer_weg", lambda gel, L, sp, a, b: ([(20, 10), b], 0, 1, None)
    )
    r, bf = _raid(gelaende=["Gs."]), Befehle()
    L, G = huetten()
    r.schritt(L, G, bf)
    L[2] = einheit(0, 0, SCHWERT, besitzer=1, leben=28000)
    r.bestellt(SCHWERT, 1)
    r.schritt(L, G, bf)
    assert bf.liste[-1] == {"angriff": {"einheiten": [2], "lauf": [20, 10]}}
    L[2] = einheit(19, 10, SCHWERT, besitzer=1, leben=28000)
    r.schritt(L, G, bf)
    assert bf.liste[-1] == {"angriff": {"einheiten": [2], "gebaeude": 1}}


def test_nahkampf_raid_zaehlt_und_nimmt_das_naechste_ziel():
    r, bf = _raid(), Befehle()
    L, G = huetten()
    r.schritt(L, G, bf)
    L[2] = einheit(49, 0, SCHWERT, besitzer=1, leben=28000)
    r.bestellt(SCHWERT, 1)
    r.schritt(L, G, bf)
    erstes = r.ziel[2]
    del G[erstes[1]]
    r.schritt(L, G, bf)
    assert r.zerstoert == 1 and r.ziel[2] != erstes
    assert "1 Gebaeude zerstoert" in r.bericht()


def test_nahkampf_raid_schickt_denselben_befehl_nicht_jede_runde():
    r, bf = _raid(), Befehle()
    L, G = huetten()
    r.schritt(L, G, bf)
    L[2] = einheit(0, 0, SCHWERT, besitzer=1, leben=28000)
    r.bestellt(SCHWERT, 1)
    for _ in range(3):
        r.schritt(L, G, bf)
    assert len(bf.liste) == 1


def test_nahkampf_raid_kennt_nur_nahkampf_ohne_eigenes_modul():
    assert SKLAVE not in NK.KANN and ASSASSINE not in NK.KANN and LORD not in NK.KANN
    assert all(EH.ARTEN[t].kampf == "nah" and EH.darf(t, "raid") for t in NK.KANN)


@pytest.mark.parametrize(
    "zeile",
    [
        "raid_e.nahkampf.bestellt(typ_r, n_r)",
        "| raid_e.nahkampf.mitglieder",
        "raid_e.nahkampf.bericht()",
    ],
)
def test_lenker_meldet_bestellungen_schuetzt_mitglieder_und_berichtet(zeile):
    assert zeile in LENKER


def test_gelerntes_leben_gilt_ab_der_naechsten_runde():
    w = wissen()
    L, G = huetten(n_bogen=3)
    z = WK.ziele(L, G, 1)[0]
    vorher = w.am_ziel(SKLAVE, z)[1]
    w.lernen({1: einheit(0, 0, SKLAVE, besitzer=1, leben=15000)}, 1)
    assert w.am_ziel(SKLAVE, z)[1] > vorher


def test_nahkaempfer_am_ziel_zaehlen_nur_fuer_nahkaempfer():
    w = wissen()
    G = {1: geb(50, 0)}
    L = {300 + i: einheit(51, 1, 24) for i in range(5)}
    z = WK.ziele(L, G, 1)[0]
    assert z.nah == (24,) * 5 and w.am_ziel(SKLAVE, z)[1] < 1.0
