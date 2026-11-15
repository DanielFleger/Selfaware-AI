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
    return WK.Wissen(
        tabelle=TAB, gebaeude=GEB, eichung={}, gebaeudeschaden={}
    )  # ohne Eichung und ohne Balance der Instanz: Tests haengen nicht an Partiedaten


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


def test_nur_der_lord_hat_weniger_als_alle_drei_rollen():
    """Daniel 13.11.2026 23:13: "Ja lass diese komischen grenzen raus" (Leitertraeger, Ingenieur, Tunnelgraeber)."""
    assert {t for t, a in EH.ARTEN.items() if a.rollen != EH.ALLE} == {LORD}
    assert all(EH.darf(t, r) for t in (5, 29, 30) for r in EH.ROLLEN)


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


def test_sklaven_wird_nur_zugetraut_was_der_brandtrupp_tut():
    """Reihe 1 (10.11.): Ohne diese Grenze kaufte die Rechnung nur Sklaven, auch gegen Arbeiter, die der Brandtrupp nie jagt."""
    L = {200 + i: einheit(40 + i, 0, 3) for i in range(6)}
    k, _ = WK.kaufen(
        wissen(), 300, 20, {SKLAVE: 5, 74: 75}, (0, 0), WK.ziele(L, {}, 1), zielarten=RB.ZIELARTEN
    )
    assert dict(k).get(SKLAVE, 0) == 0 and dict(k)[74] >= 1


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


def _einsatz():
    """Raid-Einsatz mit den Modulen der Aufstellung raid_wirkung, ohne Spiel."""
    return RB.RaidEinsatz(
        1, (0, 0), lambda nr: 0, AF.Steckplaetze(AF.laden("raid_wirkung")["versionen"])
    )


def test_kauf_traut_sklaven_nur_zu_was_der_brandtrupp_angreift():
    """B-182 Reihe 5 (BierKoenig, 10.11.): Der Brandtrupp konnte meist 0 bis 1 von 21 bis 30 Gebaeuden angreifen, die Rechnung legte 71 %
    ihres Werts auf die anderen und kaufte 224 Sklaven fuer 2 Braende. Jetzt fragt der Kauf den Einsatz."""
    L, G = huetten(n_bogen=3)
    # #360: hinter einem Haus steht der Sklave gedeckt - "gedeckt" heisst hier Schuetzen auf jeder Seite
    L.update({110: einheit(46, 1, BOGEN), 111: einheit(60, 1, BOGEN), 112: einheit(52, 8, BOGEN)})
    e, b = _einsatz(), _bestellung()
    z = {x.schluessel: x for x in WK.ziele(L, G, 1)}
    assert not e.greift_an(SKLAVE, z[("g", 1)], L, G) and e.brand._ziele(L, G, (0, 0), set()) == []
    assert dict(b.schritt(_lage(L=L, G=G))).get(SKLAVE, 0) > 0  # ohne die Frage: wie in Reihe 5
    k = dict(b.schritt(_lage(L=L, G=G, greift_an=e.greift_an)))
    assert (
        k.get(SKLAVE, 0) == 0 and k[SCHWERT] >= 1
    )  # gedeckt: schwere Einheit, die der Nahkampf-Raid auch fuehrt
    L, G = huetten()
    assert b.schritt(_lage(L=L, G=G, greift_an=e.greift_an)) == [
        (SKLAVE, 1)
    ]  # ungedeckt: Sklave wie bisher
    e.brand.brennt.add(1)
    assert [x.schluessel for x in WK.ziele(L, G, 1) if e.greift_an(SKLAVE, x, L, G)] == [
        ("g", 2)
    ]  # brennt schon


def test_kauf_traut_reitern_nur_zu_was_die_reiterjagd_jagt():
    L = {
        200: einheit(40, 0, 3),
        201: einheit(80, 0, 3),
        300: einheit(41, 2, BOGEN),
    }  # 200 gedeckt, 201 frei
    e = _einsatz()
    z = {x.schluessel: x for x in WK.ziele(L, {}, 1)}
    assert not e.greift_an(74, z[("e", 200)], L, {}) and e.greift_an(74, z[("e", 201)], L, {})
    assert not e.greift_an(SKLAVE, z[("e", 201)], L, {})  # Sklaven jagen keine Arbeiter
    assert e.greift_an(
        SCHWERT, z[("e", 200)], L, {}
    )  # Nahkampf-Raid: entscheidet dieselbe Rechnung


def test_kauf_traut_vorstoss_schuetzen_nur_ziele_mit_sicherem_standplatz_zu(monkeypatch):
    """Partie 11.11. 23:53: 4 Arabische Bogenschuetzen gekauft (240 Gold), der Vorstoss stand mit 9 Schuetzen still - an jeder Stellung
    reichten 1-2 feindliche Armbrustschuetzen hin."""
    e = RB.RaidEinsatz(
        1,
        (0, 0),
        lambda nr: 0,
        AF.Steckplaetze(AF.laden("raid_wirkung")["versionen"]),
        vorstoss_bis=40000,
    )
    L = {
        200: einheit(100, 100, 3),
        201: einheit(300, 100, 3),
        300: einheit(302, 100, 23),
    }  # 201 deckt ein Armbrustschuetze
    z = {x.schluessel: x for x in WK.ziele(L, {}, 1)}
    assert e.greift_an(70, z[("e", 200)], L, {}) and not e.greift_an(70, z[("e", 201)], L, {})
    monkeypatch.setattr(
        e.weg, "trotz_gefahr", frozenset({"vorstoss"})
    )  # mit Freigabe darf er auch dorthin
    assert e.greift_an(70, z[("e", 201)], L, {})


def _jagd(L):
    """Eine Runde Reiterjagd samt Wegfuehrung des Raid-Einsatzes: (Ziel je Reiter, gesendete Befehle)."""
    e, gesendet = _einsatz(), []
    e.reiter.schritt(L, {}, lambda b, *a, **k: gesendet.append(b))
    assert (
        gesendet == []
    )  # B-182: die Reiterjagd waehlt nur das Ziel, Weg und Befehl kommen von der Wegfuehrung
    e.weg.schritt(L, {}, lambda b, *a, **k: gesendet.append(b))
    return {n: a.ziel for n, a in e.weg.auftraege.items()}, gesendet


def test_reiterjagd_jagt_nur_ungedeckte_arbeiter_auch_ausser_reichweite():
    """Die Reiterjagd nimmt dieselbe Pruefung wie der Kauf (raids.Reiterjagd.moeglich): in Reichweite der wertvollste freie Arbeiter, sonst
    der naechste freie irgendwo; gedeckte nie."""
    L = {
        1: einheit(30, 0, 74, besitzer=1),
        200: einheit(20, 0, 3),  # Holzfaeller, frei: der Bogen steht 26 Felder weg
        201: einheit(45, 0, 1),  # Bauer, mehr wert, aber der Bogen steht daneben
        300: einheit(46, 2, BOGEN),
    }
    ziele, gesendet = _jagd(L)
    assert ziele == {1: 200} and gesendet == [
        {"angriff": {"einheiten": [1], "ziel": 200}}
    ]  # Bauer 201 ist mehr wert, aber gedeckt
    L = {
        1: einheit(0, 0, 74, besitzer=1),
        202: einheit(60, 0, 3),
        203: einheit(90, 0, 3),
        301: einheit(92, 0, BOGEN),
    }
    ziele, gesendet = _jagd(L)
    assert (
        ziele == {1: 202} and "lauf" in gesendet[0]["angriff"]
    )  # 60 Felder: die Wegfuehrung reitet hin (S114)


def test_bogenschuetzen_kauft_der_lenker_nur_solange_der_vorstoss_fuehrt():
    """B-182 Reihe 6: 42 von 46 Kaufzeilen fuer Arabische Bogenschuetzen kamen nach dem Ende des Vorstosses (Takt 15.000)."""
    from selfaware.micro.tasks import vorstoss as VS

    v = VS.Vorstoss(1, (0, 0), bis=15000)
    assert v.fuehrt(14999) and not v.fuehrt(15000)
    assert (
        'steuerbar_r |= {70} if vorstoss is not None and vorstoss.fuehrt(st["t"]) else set()'
        in LENKER
    )


def _jagden(L):
    return sorted(_jagd(L)[0].items())


def test_reiterjagd_jagt_den_wertvollsten_in_reichweite_auch_zu_zweit():
    """B-182 Reihe 8: Verteilen senkte das Gedraenge, aber nicht die Abschuesse - darum duerfen mehrere Reiter denselben Arbeiter jagen.
    In Reichweite zaehlt der Wert, sonst der naechste ungedeckte irgendwo."""
    reiter = {1: einheit(0, 0, 74, besitzer=1), 2: einheit(1, 0, 74, besitzer=1)}
    assert _jagden({**reiter, 200: einheit(10, 0, 1), 201: einheit(12, 0, 3)}) == [
        (1, 200),
        (2, 200),
    ]
    assert _jagden({**reiter, 202: einheit(60, 0, 3), 203: einheit(90, 0, 1)}) == [
        (1, 202),
        (2, 202),
    ]


def test_reiterjagd_schreibt_jeden_erfolg_in_die_mitschrift():
    """B-182: Die Eichung paart die Zeile "jagt Arbeiter" mit dieser Erfolgszeile und misst die Takte dazwischen."""
    e = _einsatz()
    r = e.reiter
    L = {1: einheit(0, 0, 74, besitzer=1), 200: einheit(10, 0, 1)}
    r.schritt(L, {}, lambda *a, **k: None)
    e.weg.schritt(
        L, {}, lambda *a, **k: None
    )  # S110: erst der Angriff in Reichweite macht es zu unserem Abschuss
    del L[200]
    assert r.schritt(L, {}, lambda *a, **k: None) == [
        "REITERJAGD: Reiter 1 hat Arbeiter 200 erledigt"
    ]
    assert r.getoetet == 1


def test_gemessene_erfolgsanteile_und_takte_ersetzen_die_ersatzwerte():
    """B-182 Eichung: Die Rechnung traute Sklaven sicheren Erfolg nach 165 Takten zu; gemessen in den Reihen 6 bis 9: 18 % der Zuweisungen, 550 Takte am Ziel."""
    L, G = huetten()
    z = WK.ziele(L, G, 1)[0]
    geeicht = WK.Wissen(tabelle=TAB, gebaeude=GEB, eichung={(SKLAVE, "g"): (0.05, 600.0)})
    assert geeicht.am_ziel(SKLAVE, z) == (600.0, 0.05) and wissen().am_ziel(SKLAVE, z) == (
        WK.FEUER_TAKTE,
        1.0,
    )
    nur_takte = WK.Wissen(tabelle=TAB, gebaeude=GEB, eichung={(SKLAVE, "g"): (None, 600.0)})
    assert nur_takte.am_ziel(SKLAVE, z) == (600.0, 1.0)
    # ungedeckte Huetten: ungeeicht der Sklave, geeicht die schwere Einheit, deren Rechnung keine Messung kennt
    preise, ziele = {SKLAVE: 5, SCHWERT: 100}, WK.ziele(L, G, 1)
    assert WK.kaufen(wissen(), 300, 20, preise, (0, 0), ziele)[0][0][0] == SKLAVE
    assert WK.kaufen(geeicht, 300, 20, preise, (0, 0), ziele)[0] == [(SCHWERT, 1)]


def test_was_eigene_einheiten_im_feld_erledigen_zaehlt_fuer_keinen_kauf():
    """B-182 Eichung: Die Rechnung zaehlte jede Runde dieselben Ziele neu, als gaebe es die schon gekauften Einheiten nicht."""
    L, G = huetten()
    z = WK.ziele(L, G, 1)
    assert WK.kaufen(wissen(), 300, 20, {SKLAVE: 5}, (0, 0), z)[0] == [(SKLAVE, 1)]
    assert (
        WK.kaufen(wissen(), 300, 20, {SKLAVE: 5}, (0, 0), z, vorhanden=[(SKLAVE, (49, 0))])[0] == []
    )
    # ein Reiter im Feld deckt keine Gebaeude ab: dort kauft er weiter den Sklaven
    k, _ = WK.kaufen(
        wissen(), 300, 20, {SKLAVE: 5}, (0, 0), z, zielarten=RB.ZIELARTEN, vorhanden=[(74, (49, 0))]
    )
    assert k == [(SKLAVE, 1)]


def test_einsatz_meldet_was_seine_module_fuehren_und_der_lenker_gibt_es_weiter():
    e = _einsatz()
    L = {
        1: einheit(5, 6, SKLAVE, besitzer=1),
        2: einheit(7, 8, 74, besitzer=1),
        3: einheit(9, 9, SKLAVE),
        4: einheit(1, 1, 22, besitzer=1),
    }
    assert e.vorhanden(L) == (
        (SKLAVE, (5, 6)),
        (74, (7, 8)),
    )  # fremde und nicht gefuehrte Einheiten fehlen
    assert "vorhanden=raid_e.vorhanden(L) if raid_e is not None else ()" in LENKER


def test_aufstellung_raid_wirkung_steckt_die_neue_bestellung():
    d = AF.laden("raid_wirkung")
    assert AF.Steckplaetze(d["versionen"]).klasse("raidbestellung") is RB.RaidBestellungNachWirkung
    # dazu, Partie 11.11. 23:25 (Fehlerwache F3): der Vorstoss fuehrt seine Schuetzen bis zum Ende der Partie
    assert d["schalter"] == {**AF.laden("raid_ohne_angriff")["schalter"], "vorstoss_bis": "40000"}


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


def test_nahkampf_raid_nimmt_den_bauern_der_zum_soldaten_wird():
    """Reihe 2b (10.11.): Im Spiel behaelt der angeworbene Bauer seine Nummer, nur die Art wechselt."""
    r, bf = _raid(), Befehle()
    L, G = huetten()
    L[565] = einheit(0, 0, 1, besitzer=1)
    r.schritt(L, G, bf)
    r.bestellt(SCHWERT, 1)
    L[565] = einheit(0, 0, SCHWERT, besitzer=1, leben=28000)
    r.schritt(L, G, bf)
    assert r.mitglieder == {565}


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
    aus = r.schritt(L, G, bf)
    assert r.zerstoert == 1 and r.ziel[2] != erstes
    assert (
        "NAHKAMPF-RAID: 2 (Typ 75) hat Gebaeude %d erledigt" % erstes[1] in aus
    )  # B-182: Erfolgszeile fuer die Eichung
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


def _raid_mit_weg(trotz_gefahr=()):
    from selfaware.micro import wegfuehrung as W

    r = _raid()
    r.weg = W.Wegfuehrung(1, trotz_gefahr=trotz_gefahr)
    return r


def _mit_schwert(r, bf, L, G, n=2, x=0, y=0):
    r.schritt(L, G, bf)
    L[n] = einheit(x, y, SCHWERT, besitzer=1, leben=28000)
    r.bestellt(SCHWERT, 1)
    return r.schritt(L, G, bf)


def test_nahkampf_raid_gibt_den_weg_an_die_wegfuehrung(monkeypatch):
    """B-182 (Daniel 11.11. 00:48 auf die Frage, ob als Naechstes der Nahkampf-Raid umzieht: "Ja, Nahkampf-Raid"): das Modul waehlt
    das Ziel nach Wirkung, Weg und Befehle kommen von der Wegfuehrung."""
    monkeypatch.setattr(
        RB, "TROTZ_GEFAHR", ("nahkampfraid",)
    )  # der Raid-Einsatz reicht die Freigabe an die Wegfuehrung weiter
    e = _einsatz()
    assert e.nahkampf.weg is e.weg and e.weg.trotz_gefahr == {"nahkampfraid"}
    r, bf = _raid_mit_weg(), Befehle()
    L, G = huetten()
    aus = _mit_schwert(r, bf, L, G)
    assert bf.liste == [] and r.weg.fuehrt(2)  # kein eigener Befehl mehr
    assert any("Weg ueber die Wegfuehrung" in z for z in aus)
    assert r.weg.schritt(L, G, bf)[2] == "unterwegs" and "lauf" in bf.liste[-1]["angriff"]
    L[2] = einheit(49, 1, SCHWERT, besitzer=1, leben=28000)
    assert r.weg.schritt(L, G, bf)[2] == "greift_an"
    assert bf.liste[-1] == {"angriff": {"einheiten": [2], "gebaeude": r.ziel[2][1]}}


def test_nahkampf_raid_nimmt_bei_gefahr_ein_anderes_ziel_die_sperre_gilt_je_einheit():
    from selfaware.micro.tasks import raids as RA

    r, bf = _raid_mit_weg(), Befehle()
    L, G = huetten()
    _mit_schwert(r, bf, L, G)
    erstes = r.ziel[2]
    L[300] = einheit(G[erstes[1]]["x"], 5, BOGEN)  # ein Bogenschuetze stellt sich ans erste Ziel
    assert r.weg.schritt(L, G, bf)[2] == "gefahr"
    aus = r.schritt(L, G, bf)
    assert (
        r.ziel[2] != erstes
        and ("NAHKAMPF-RAID: 2 (Typ 75) gibt Gebaeude %d auf (gefahr)" % erstes[1]) in aus
    )
    assert r.gesperrt == {(2, erstes): r.runde + RA.SPERRE_RUNDEN}
    L[3] = einheit(
        0, 1, SCHWERT, besitzer=1, leben=28000
    )  # ein zweiter Schwertkaempfer darf das erste Ziel noch waehlen
    r.bestellt(SCHWERT, 1)
    r.schritt(L, G, bf)
    assert r.ziel[3] == erstes


def test_steinmetz_bei_der_arbeit_ist_kein_ziel_und_der_holzfaeller_braucht_die_gemessene_zeit():
    """S153/S154: ein Steinmetz (7) in Zustand 1 laesst sich nicht angreifen; ein Holzfaeller mit 10000 Leben braucht einen Speertraeger
    10000 / 25 = 400 Takte (gemessen), nicht die Ersatz-50."""
    L = {
        7: dict(einheit(10, 10, 7), zustand=1),
        8: dict(einheit(12, 10, 7), zustand=2),
        9: dict(einheit(14, 10, 3, leben=10000), zustand=1),
    }
    zs = {z.schluessel: z for z in WK.ziele(L, {}, 1)}
    assert ("e", 7) not in zs and ("e", 8) in zs and ("e", 9) in zs
    assert wissen().am_ziel(24, zs[("e", 9)])[0] == 400.0
    assert (
        wissen().am_ziel(73, zs[("e", 9)])[0] == WK.ARBEITER_TAKTE
    )  # ungemessenes Paar: weiter der Ersatz


def test_wert_je_takt_rechnet_mit_dem_sicheren_weg():
    """S150: mit felder die Laenge des sicheren Wegs statt der Luftlinie."""
    import selfaware.services.spielwerte as SW

    w = wissen()
    z = WK.ziele({}, {1: geb(50, 0)}, 1)[0]
    luft = w.wert_je_takt(SCHWERT, (0, 0), z)
    weg = w.wert_je_takt(SCHWERT, (0, 0), z, felder=150)
    assert weg[1] - luft[1] == (150 - 50) * SW.takte_je_feld(SCHWERT, "trupp") and weg[0] < luft[0]


def test_nahkampf_raid_waehlt_nach_dem_sicheren_weg_nicht_nach_luftlinie():
    """S150 (Daniel 23:29): Gebaeude 1 liegt 40 Felder Luftlinie entfernt hinter einer Mauer, Gebaeude 2 52 Felder ohne Hindernis -
    nach der Luftlinie waere es 1, ueber den Weg ist es 2."""
    from selfaware.micro import wegfuehrung as W

    karte = [
        "".join("#" if 40 <= x <= 160 and 70 <= y <= 75 else "." for x in range(400))
        for y in range(400)
    ]
    r, bf = _raid(), Befehle()
    r.weg = W.Wegfuehrung(1, karte)
    L, G = {}, {1: geb(100, 60), 2: geb(100, 152)}
    aus = _mit_schwert(r, bf, L, G, x=100, y=100)
    assert r.ziel[2] == ("g", 2)
    assert any("Gebaeude 2" in z and "auf dem sicheren Weg, 52 Luftlinie" in z for z in aus), aus


def test_nahkampf_raid_wechselt_unterwegs_zu_einem_ziel_das_mehr_wert_je_takt_bringt():
    """S150 (Daniel 23:29 "ein neues besseres ziel auswaehlen das auf dem weg ist oder leicht dahinter"): ein neues Gebaeude auf dem
    Weg bringt mehr Wert je Takt - der Soldat wechselt, ohne Huerde (Daniel 23:32 "kein komischer wert bitte")."""
    r, bf = _raid_mit_weg(), Befehle()
    L, G = {}, {1: geb(100, 300)}
    _mit_schwert(r, bf, L, G, x=100, y=100)
    assert r.ziel[2] == ("g", 1)
    G[5] = geb(100, 130)
    aus = r.schritt(L, G, bf)
    assert r.ziel[2] == ("g", 5) and any(
        "wechselt von Gebaeude 1 zu Gebaeude 5" in z for z in aus
    ), aus
    aus = r.schritt(L, G, bf)
    assert r.ziel[2] == ("g", 5) and not any("wechselt" in z for z in aus)


def test_nahkampf_raid_schlaegt_einen_verteidiger_des_ziels_zurueck_sonst_geht_er_weiter():
    """S150 (Daniel 23:34 "Ja, mit einbauen"): ein gegnerischer Speertraeger kaempft gegen den Raid-Soldaten. Deckt er das Ziel, bringt
    sein Tod dort mehr Erfolg - zurueckschlagen rechnet sich; steht er weit vor dem Ziel, kostet der Kampf nur Zeit - weitergehen
    (gemessen: ein Soldat folgte 1 von 18 Mal)."""
    from selfaware.micro import wegfuehrung as W

    # ein starker Verteidiger: das Ziel wird unsicher (S161: mit dem Gebaeudewert der Assassinen-Tabelle, Huette 60 statt 12, lohnt das
    # Weitergehen mehr - der Verteidiger im Beispiel schlaegt darum haerter zu als vorher 200)
    tab = ({**TAB[0], 24: {75: 400.0}}, {**TAB[1], 24: 1000}, TAB[2])
    r = NK.NahkampfRaid(1, None, wissen=WK.Wissen(tabelle=tab, gebaeude=GEB, eichung={}))
    r.weg = W.Wegfuehrung(1, trotz_gefahr=("nahkampfraid",))
    bf = Befehle()
    L, G = {}, {1: geb(100, 140)}
    _mit_schwert(r, bf, L, G, x=100, y=100)
    L[40] = einheit(100, 134, 24)
    L[2] = dict(einheit(100, 133, SCHWERT, besitzer=1, leben=28000), zustand=106, nahziel=40)
    aus = r.schritt(L, G, bf)
    assert any(
        "kaempft gegen Soldat 40 (Typ 24): schlaegt zurueck" in z and "deckt das Ziel: ja" in z
        for z in aus
    ), aus
    assert (
        r.ziel[2] == ("g", 1)
        and r.weg.auftraege[2].ziel == 40
        and r.absicht[2][2] == "defender_worth_it"
    )
    L[40] = einheit(100, 110, 24)
    L[2] = dict(einheit(100, 109, SCHWERT, besitzer=1, leben=28000), zustand=106, nahziel=40)
    aus = r.schritt(L, G, bf)
    assert any(
        "kaempft gegen Soldat 40 (Typ 24): geht weiter" in z and "deckt das Ziel: nein" in z
        for z in aus
    ), aus
    assert r.weg.auftraege[2].ziel == 1


def test_ein_wechsel_kostet_die_gemessenen_takte():
    """S151 (Daniel 23:48 "Ja, einbauen"): ein neues Ziel zaehlt mit den Takten, die ein neuer Laufbefehl eine laufende Einheit kostet
    (gemessen 15,9 statt 9,5 Takte je Feld). Beispiel mit runden Zahlen: das jetzige Ziel bringt 0,0100 je Takt; ein neues mit
    0,0101 bei 1000 Takten lohnt den Wechsel noch (0,01004), eines mit 0,01005 nicht mehr (0,00999)."""
    assert NK.WECHSEL_TAKTE == 15.9 - 9.5
    assert (
        NK.NahkampfRaid._nach_wechsel(0.0101, 1000)
        > 0.0100
        > NK.NahkampfRaid._nach_wechsel(0.01005, 1000)
    )
    assert NK.NahkampfRaid._nach_wechsel(0.0, None) == 0.0


def test_nahkampf_raid_zaehlt_nur_was_er_am_ziel_angriff():
    r, bf = _raid_mit_weg(), Befehle()
    L, G = huetten()
    _mit_schwert(r, bf, L, G)
    erstes = r.ziel[2]
    del G[erstes[1]]  # das Gebaeude faellt, bevor die Einheit dort war
    aus = r.schritt(L, G, bf)
    assert r.zerstoert == 0 and any("2 war nicht am Ziel - kein eigener Erfolg" in z for z in aus)
    zweites = r.ziel[2]
    L[2] = einheit(G[zweites[1]]["x"] - 1, 0, SCHWERT, besitzer=1, leben=28000)
    assert r.weg.schritt(L, G, bf)[2] == "greift_an"
    r.schritt(L, G, bf)
    del G[zweites[1]]
    aus = r.schritt(L, G, bf)
    assert (
        r.zerstoert == 1
        and ("NAHKAMPF-RAID: 2 (Typ 75) hat Gebaeude %d erledigt" % zweites[1]) in aus
    )


def test_nahkampf_raid_zaehlt_nur_einen_frischen_angriff():
    """Partie 12.11. 00:05 (Fehlerwache F4, bei der Reiterjagd): ein Angriff, der lange zurueckliegt, ist kein Beleg fuer den Erfolg."""
    from selfaware.micro.tasks import raids as RA

    r, bf = _raid_mit_weg(), Befehle()
    L, G = huetten()
    _mit_schwert(r, bf, L, G)
    nr = r.ziel[2][1]
    L[2] = einheit(G[nr]["x"] - 1, 0, SCHWERT, besitzer=1, leben=28000)
    assert r.weg.schritt(L, G, bf)[2] == "greift_an"
    r.schritt(L, G, bf)
    L[2] = einheit(
        G[nr]["x"] - 60, 0, SCHWERT, besitzer=1, leben=28000
    )  # abgedraengt, er laeuft zurueck
    for _ in range(RA.ABSCHUSS_RUNDEN + 1):
        r.weg.schritt(L, G, bf)
        r.schritt(L, G, bf)
    del G[nr]  # jetzt faellt das Gebaeude - durch wen auch immer
    aus = r.schritt(L, G, bf)
    assert r.zerstoert == 0 and any("kein eigener Erfolg" in z for z in aus)


def test_nahkampf_raid_wiedervergebene_gebaeudenummer_ist_ein_erfolg_nach_angriff():
    r, bf = _raid_mit_weg(), Befehle()
    L, G = huetten()
    _mit_schwert(r, bf, L, G)
    nr = r.ziel[2][1]
    L[2] = einheit(G[nr]["x"] - 1, 0, SCHWERT, besitzer=1, leben=28000)
    assert r.weg.schritt(L, G, bf)[2] == "greift_an"
    r.schritt(L, G, bf)
    G[nr] = geb(
        G[nr]["x"], 0, typ=3
    )  # die Nummer traegt jetzt ein anderes Gebaeude: das alte ist gefallen
    assert r.weg.schritt(L, G, bf)[2] == "ziel_weg"
    aus = r.schritt(L, G, bf)
    assert r.zerstoert == 1 and ("NAHKAMPF-RAID: 2 (Typ 75) hat Gebaeude %d erledigt" % nr) in aus


def test_nahkampf_raid_ziel_eines_toten_teilnehmers_ist_wieder_frei():
    """Vorher blieb es belegt: fuer die anderen Teilnehmer und fuer den Kauf (Lenker belegt_r)."""
    for r in (_raid(), _raid_mit_weg()):
        bf = Befehle()
        L, G = huetten()
        _mit_schwert(r, bf, L, G)
        assert 2 in r.ziel
        del L[2]
        r.schritt(L, G, bf)
        assert r.ziel == {} and (r.weg is None or not r.weg.fuehrt(2))


def test_nahkampf_raid_greift_in_gefahr_nur_mit_freigabe_an():
    """Plan_Wegfuehrung.md: am Ziel in Gefahr greift nur an, wessen Zweck Daniel freigibt (raid.TROTZ_GEFAHR)."""
    # Daniel 11.11. 19:40 auf die Frage "Darf der Nahkampf-Raid Ziele unter Beschuss angreifen?": "Gerne freigeben"
    # Daniel 11.11. 21:48 auf die Frage "Sollen die Waechter ueber die Wegfuehrung laufen und unter Beschuss angreifen duerfen?": "Ja, freigeben"
    assert RB.TROTZ_GEFAHR == ("nahkampfraid", "waechter")
    for frei, erwartet in (((), "gefahr"), (("nahkampfraid",), "unterwegs")):
        r, bf = _raid_mit_weg(trotz_gefahr=frei), Befehle()
        L, G = huetten(n_bogen=1)  # ein Bogenschuetze deckt beide Huetten
        _mit_schwert(r, bf, L, G)
        assert r.weg.schritt(L, G, bf)[2] == erwartet


def test_nahkampf_raid_kennt_nur_nahkampf_ohne_eigenes_modul():
    assert SKLAVE not in NK.KANN and ASSASSINE not in NK.KANN and LORD not in NK.KANN
    assert all(EH.ARTEN[t].kampf == "nah" and EH.darf(t, "raid") for t in NK.KANN)


@pytest.mark.parametrize(
    "zeile",
    [
        "raid_e.nahkampf.bestellt(typ_r, n_r)",
        "| raid_e.nahkampf.mitglieder",
        "raid_e.nahkampf.bericht()",
        "greift_an=raid_e.greift_an if raid_e is not None else None",
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


def test_freigabe_gilt_nur_fuer_den_nahkampf_raid():
    """Grundgesetz P1.37: Daniels Freigaben antworteten auf die Fragen nach dem Nahkampf-Raid und den Waechtern - Brandtrupp,
    Reiterjagd und Vorstoss bleiben ohne Freigabe."""
    e = _einsatz()
    assert e.weg.trotz_gefahr == {"nahkampfraid", "waechter"}
    L = {
        1: einheit(0, 0, SCHWERT, besitzer=1, leben=28000),
        2: einheit(0, 2, SKLAVE, besitzer=1),
        100: einheit(51, 3, BOGEN),  # deckt das Gebaeude
    }
    G = {1: geb(50, 0)}
    e.weg.fuehre(1, "gebaeude", 1, "nahkampfraid")
    e.weg.fuehre(2, "gebaeude", 1, "brandtrupp")
    assert e.weg.schritt(L, G, lambda *a, **k: None) == {1: "unterwegs", 2: "gefahr"}


def test_raid_einsatz_rechnet_die_wegfuehrung_nur_selbst_wenn_sie_ihm_gehoert():
    e = _einsatz()
    e.schritt(0, {}, {}, lambda *a, **k: None)
    assert e.weg.runde == 1
    e.weg_selbst = False  # der Lenker rechnet die gemeinsame Wegfuehrung einmal je Runde
    e.schritt(1, {}, {}, lambda *a, **k: None)
    assert e.weg.runde == 1


@pytest.mark.parametrize(
    "zeile", ["w.weg = wegf", "raid_e.weg_selbst = False", "wegf.schritt(L, G, befehl)"]
)
def test_lenker_teilt_eine_wegfuehrung_mit_dem_waechter(zeile):
    assert zeile in LENKER


def test_kauf_bestellt_erst_fuer_ein_ziel_dann_mehr():
    """Daniel 11.11. 22:31 auf die Frage, ob der Kauf hoechstens so viele Sklaven bestellen soll, wie es freie Ziele gibt:
    "erstmal ein ziel dann skalieren" (Partie 22:14: drei Sklaven bestellt, der dritte bekam nie ein Gebaeude)."""
    e = _einsatz()
    L, G = huetten()  # zwei freie Huetten, kein Schuetze
    assert e.sklaven_platz(L, G) == 2
    L[5] = einheit(0, 0, SKLAVE, besitzer=1)  # ein eigener Sklave ohne Ziel
    assert e.sklaven_platz(L, G) == 1
    assert "sklaven_platz=raid_e.sklaven_platz if raid_e is not None else None" in LENKER


def test_erster_raid_sklave_kommt_vor_der_ruecklage_der_wirtschaft():
    """Partie 11.11. 22:37 (Daniel 22:41: "so schnell wie möglich raid sklaven rausgespuckt"): 53 Gold lagen 850 Takte da, alles
    zurueckgelegt fuer die B-Plantagen - der erste Sklave kam erst bei Takt 3902."""
    from selfaware.micro.tasks import raids as RA

    b = _bestellung()
    assert b.schritt(_lage(gold=20, ruecklage=20)) == [
        (SKLAVE, 1)
    ]  # ohne Raid-Sklaven: einer trotz Ruecklage
    assert any("vor der Ruecklage" in z for z in b.begruendung)
    assert (
        b.schritt(_lage(runde=3, gold=20, ruecklage=20)) == []
    )  # nicht gleich noch einer, solange er erscheint
    assert b.schritt(_lage(runde=1 + RB.ERSTER_PAUSE, gold=20, ruecklage=20)) == [(SKLAVE, 1)]
    c = _bestellung()
    assert (
        c.schritt(_lage(gold=20, ruecklage=20, sklaven=1)) == []
    )  # lebt einer, gilt die Ruecklage wieder
    assert (
        c.schritt(_lage(gold=20, ruecklage=20, feuer=RA.FEUER_MIN)) == []
    )  # die Bauern am Feuer bleiben
    assert c.schritt(_lage(gold=4, ruecklage=0)) == []  # ohne 5 Gold kein Sklave


def test_kauf_kappt_sklaven_auf_die_freien_ziele(monkeypatch):
    monkeypatch.setattr(WK, "kaufen", lambda *a, **k: ([(SKLAVE, 3), (SCHWERT, 1)], []))
    bestellung = RB.RaidBestellungNachWirkung()
    bestellung._wissen = wissen()
    L, G = huetten()
    b = RB.Lage(
        runde=1,
        gold=500,
        ruecklage=0,
        ruecklage_soeldner=0,
        feuer=0,
        endspurt=False,
        soeldner_erlaubt=True,
        assassine_erlaubt=False,
        sklaven=0,
        reiter=0,
        schleuderer=0,
        L=L,
        G=G,
        start=(0, 0),
        steuerbar=frozenset({SKLAVE, SCHWERT}),
        sklaven_platz=lambda L, G: 1,
    )
    assert bestellung.schritt(b) == [(SKLAVE, 1), (SCHWERT, 1)]
    assert any("erst ein Ziel, dann skalieren" in z for z in bestellung.begruendung)


@pytest.mark.parametrize("mit_kern", [True, False])
def test_s155_im_kampf_gegen_einen_arbeiter_wiederholt_der_kern_den_laufbefehl(
    monkeypatch, mit_kern
):
    """S155 (Daniel 15.11.2026 00:20 "Ja, Kern bauen"): ein Raid-Soldat kaempft gegen einen Holzfaeller, der nicht sein Ziel ist. Fuehrt der
    Kern ihn, wiederholt der Kern den Laufbefehl - der Raid laesst nichts los; ohne Kern geht der Laufbefehl in dieser Runde neu hinaus (S154).
    Beispiel: ein Holzfaeller ohne Wert, damit er sicher nicht Ziel wird."""
    monkeypatch.setitem(WK.RA.ARBEITER, 3, 0.0)
    r, bf = _raid_mit_weg(), Befehle()
    L, G = {}, {1: geb(100, 300)}
    _mit_schwert(r, bf, L, G, x=100, y=100)
    assert r.ziel[2] == ("g", 1)
    if mit_kern:
        r.weg.kern = object()
    vorher = r.weg.auftraege[2]
    L[40] = einheit(100, 134, 3)
    L[2] = dict(einheit(100, 133, SCHWERT, besitzer=1, leben=28000), zustand=106, nahziel=40)
    aus = r.schritt(L, G, bf)
    assert r.ziel[2] == ("g", 1)
    if mit_kern:
        assert any(
            "kaempft gegen Arbeiter 40 - der Kern wiederholt den Laufbefehl zu Gebaeude 1" in z
            for z in aus
        ), aus
        assert r.weg.auftraege[2] is vorher
    else:
        assert any(
            "haengt im Kampf gegen Arbeiter 40 fest - Laufbefehl neu zu Gebaeude 1" in z
            for z in aus
        ), aus
        assert r.weg.auftraege[2] is not vorher


def test_s161_gebaeude_haben_die_werte_und_zeiten_der_assassinen():
    """S161 (Daniel 15.11.2026 01:32 "kannst du bitte allen auch diese faehigkeiten geben nicht nur assassinen"): Gebaeude gelten mit
    Daniels Rangfolge der Assassinen, und jede Gebaeudeart hat eine Zeit - die Arbeit der Assassine, umgerechnet mit dem
    Gebaeudeschaden der Balance (Beispiel mit den Werten der Liga-Balance: Assassine 75, Schwertkaempfer 100, Speertraeger 10)."""
    from selfaware.micro.tasks import assassinen as AS

    z = {
        zz.schluessel: zz
        for zz in WK.ziele({}, {1: geb(100, 100, typ=9), 2: geb(120, 100, typ=3)}, 1)
    }
    assert z[("g", 1)].wert == AS.WERT[9] == 800 and z[("g", 2)].wert == AS.WERT[3]
    w = WK.Wissen(
        tabelle=TAB, gebaeude=GEB, eichung={}, gebaeudeschaden={73: 75.0, 75: 100.0, 24: 10.0}
    )
    arbeit = AS.ARBEIT.get(9, AS.ARBEIT_SONST)
    assert w.gebaeude_takte(SCHWERT, 9)[0] == arbeit * 75 / 100
    assert w.gebaeude_takte(24, 9)[0] == arbeit * 75 / 10
    unbekannt = next(t for t in AS.WERT if t not in AS.ARBEIT)
    assert w.gebaeude_takte(SCHWERT, unbekannt)[0] == AS.ARBEIT_SONST * 75 / 100
    assert "geschaetzt" in w.gebaeude_takte(SCHWERT, unbekannt)[1]
    # ohne Balance wie bisher
    assert WK.Wissen(tabelle=TAB, gebaeude=GEB, eichung={}, gebaeudeschaden={}).gebaeude_takte(
        SCHWERT, 9
    ) == wissen().gebaeude_takte(SCHWERT, 9)


def test_s161_einen_arbeiter_nimmt_der_raid_nur_mit_wenn_er_direkt_daneben_steht():
    """S161: wie die Assassinen (Daniel 19.10.: "nie gesagt aktiv jagen - mitnehmen, wenn er will") - ein Arbeiter weiter als
    ARBEITER_MIT Felder ist kein Ziel, das Gebaeude in 20 Feldern gewinnt; steht er direkt daneben, nimmt der Soldat ihn mit."""
    w = WK.Wissen(tabelle=TAB, gebaeude=GEB, eichung={}, gebaeudeschaden={73: 75.0, 75: 100.0})
    r, bf = NK.NahkampfRaid(1, None, wissen=w), Befehle()
    L, G = {50: einheit(100, 104, 3)}, {1: geb(100, 120, typ=9)}
    _mit_schwert(r, bf, L, G, x=100, y=100)
    assert NK.ARBEITER_MIT == 2 and r.ziel[2] == ("g", 1)
    # direkt daneben und nur ein billiges Gebaeude weit weg (Weizenfarm 30, 60 Felder): mitnehmen. Gegen die Kaserne (800) in 20 Feldern
    # gewinnt die Kaserne auch gegen einen Arbeiter direkt nebenan (Daniels Rangfolge: Kaserne immer bevorzugen)
    r2, bf2 = NK.NahkampfRaid(1, None, wissen=w), Befehle()
    L2, G2 = {50: einheit(100, 101, 3)}, {1: geb(100, 160, typ=30)}
    _mit_schwert(r2, bf2, L2, G2, x=100, y=100)
    assert r2.ziel[2] == ("e", 50)
    # 5 Felder entfernt ist er nicht "direkt am Weg": dann das billige Gebaeude, nicht der Arbeiter
    r4, bf4 = NK.NahkampfRaid(1, None, wissen=w), Befehle()
    L4, G4 = {50: einheit(100, 105, 3)}, {1: geb(100, 160, typ=30)}
    _mit_schwert(r4, bf4, L4, G4, x=100, y=100)
    assert r4.ziel[2] == ("g", 1)
    r3, bf3 = NK.NahkampfRaid(1, None, wissen=w), Befehle()
    L3, G3 = {50: einheit(100, 101, 3)}, {1: geb(100, 120, typ=9)}
    _mit_schwert(r3, bf3, L3, G3, x=100, y=100)
    assert r3.ziel[2] == ("g", 1)


def test_s161_balance_liest_den_gebaeudeschaden_der_aktiven_datei(tmp_path):
    from selfaware.services import balance as BAL

    d = tmp_path / "ucp" / "plugins" / "Mod-KI-Team-Liga-2.0.2" / "resources" / "balance"
    d.mkdir(parents=True)
    (d / "liga_ai.json").write_text(
        '{"units": {"European spearman": {"buildingDamage": 10}, "Arabian assassin": {"buildingDamage": 75},'
        ' "Arabian slave": {"health": 15000}}}',
        encoding="utf-8",
    )
    (tmp_path / "ucp-config.yml").write_text(
        "    rebalancer:\n      config:\n        balance_config_file_selector:\n          contents:\n"
        "            value: ucp/plugins/Mod-KI-Team-Liga-*/resources/balance/liga_ai.json\n",
        encoding="utf-8",
    )
    assert BAL.gebaeudeschaden(str(tmp_path)) == {24: 10.0, 73: 75.0}
    assert BAL.gebaeudeschaden(str(tmp_path / "fehlt")) == {}


def test_s161_jede_gebaeudeart_der_alten_raid_tabelle_bleibt_ein_ziel():
    """S161 (Daniel 15.11.2026 01:50: zwei Hopfenfarmen nie angegriffen): mit der Assassinen-Tabelle darf keine Art herausfallen, die der
    Raid vorher angriff (Hopfenfarm 31 fehlte)."""
    from selfaware.micro.tasks import assassinen as AS
    from selfaware.micro.tasks import raids as RA

    assert set(RA.WERT) <= set(AS.WERT)
    assert AS.WERT[31] == AS.WERT[32]


def test_s162_greifen_die_assassinen_den_lord_an_gehen_alle_raid_nahkaempfer_mit():
    """S162 (Daniel 15.11.2026 01:50 "ich will den gegnerischen lord so schnell und erbarmungslos wie moeglich killen"): setzt der Lenker
    den Lord (die Assassinen greifen ihn an), wird er das Ziel jedes Raid-Nahkaempfers, auch mitten in einem Raid; ohne Lord wie bisher."""
    r, bf = _raid_mit_weg(trotz_gefahr=("nahkampfraid",)), Befehle()
    L, G = {99: einheit(200, 200, 55)}, {1: geb(100, 130)}
    _mit_schwert(r, bf, L, G, x=100, y=100)
    assert r.ziel[2] == ("g", 1)
    r.lord = 99
    aus = r.schritt(L, G, bf)
    assert (
        r.ziel[2] == ("e", 99) and r.weg.auftraege[2].ziel == 99 and r.absicht[2][2] == "lord_push"
    )
    assert any("geht mit auf den Lord 99" in z for z in aus), aus
    r.lord = None
    r.schritt(L, G, bf)
    assert r.ziel[2] != ("e", 99) or r.absicht[2][2] != "lord_push"


def test_s164_unzerstoerbare_gebaeude_sind_nie_ziel():
    """S164 (Daniel 15.11.2026 01:58: Lager und Steinablage am Steinbruch sind unzerstoerbar - nie ein Angriffsziel)."""
    from selfaware.micro.tasks import assassinen as AS
    from selfaware.micro.tasks import raids as RA

    assert set(AS.UNZERSTOERBAR) == {10, 21}
    assert not set(AS.UNZERSTOERBAR) & (set(AS.WERT) | set(RA.WERT))
    z = WK.ziele(
        {}, {1: geb(100, 100, typ=10), 2: geb(110, 100, typ=21), 3: geb(120, 100, typ=31)}, 1
    )
    assert [x.schluessel for x in z] == [("g", 3)]


def test_zwei_nahkaempfer_greifen_dasselbe_gebaeude_an():
    """Daniel 15.11.2026 22:29 (baukasten/zielvergabe.py): ein einziges Ziel, zwei Schwertkaempfer - beide greifen an, der zweite
    stellt sich dazu statt zu warten (vorher ein Ziel je Einheit)."""
    r, bf = _raid(), Befehle()
    L, G = {}, {1: geb(100, 30)}
    r.schritt(L, G, bf)
    L[2] = einheit(0, 0, SCHWERT, besitzer=1, leben=28000)
    L[3] = einheit(0, 4, SCHWERT, besitzer=1, leben=28000)
    r.bestellt(SCHWERT, 2)
    aus = r.schritt(L, G, bf)
    assert r.ziel.get(2) == r.ziel.get(3) == ("g", 1), aus
    assert sum("dazu (schon besetzt" in z for z in aus) == 1, aus


def test_kein_wechsel_nur_weil_der_weg_zum_jetzigen_ziel_in_dieser_runde_fehlt():
    """Daniel 16.11.2026 00:09: "ein speertraeger lief ewig in eine richtung nur um dann zurueckzugehen fuer ein anderes gebaeude".
    Probe 4: ein Teil der 39 Wechsel kam "statt kein Weg" - der Weg zum jetzigen Ziel fehlte in einer Runde. Dann bleibt das Ziel."""
    r, bf = _raid_mit_weg(), Befehle()
    L, G = {}, {1: geb(100, 300)}
    _mit_schwert(r, bf, L, G, x=100, y=100)
    assert r.ziel[2] == ("g", 1)
    G[5] = geb(160, 100)
    alt = r.weg.weglaenge

    def ohne_weg_zu_1(raster, von):
        f = alt(raster, von)
        return lambda o: None if tuple(o) == (100, 300) else f(o)

    r.weg.weglaenge = ohne_weg_zu_1
    aus = r.schritt(L, G, bf)
    assert r.ziel[2] == ("g", 1) and not any("wechselt" in z for z in aus), aus
