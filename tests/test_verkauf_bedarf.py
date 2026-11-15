"""Verkauf nach Bedarf (Daniel 15.11.2026 22:29: "Es soll nur so viel gelagert werden wie fuer die geplante naechste
Wirtschaft gebraucht wird. Theoretisch braucht es nie mehr als 4 Vorratslager").

Anlass (gemessen in data/research/erstes_spiel_log2_sp2.txt, Partie ab 22:22:46): Stein 18 bei Tick 10.107, 406 bei Tick
34.766 - je Ware und Runde ging nur EIN Los, und nur jede dritte Runde; Lagerteile 16."""

from selfaware.runtime.live import erstes_spiel as ES
from selfaware.runtime.live import stillstand as STW


def test_ganzer_ueberschuss_geht_nie_unter_den_bedarf():
    # Daniels Partie: 406 Stein, Bedarf 20 -> 77 Lose zu 5, es bleiben 21
    assert ES.verkaufslose(406, 20, 5, False) == 77
    for menge in range(0, 500, 7):
        k = ES.verkaufslose(menge, 20, 5, False)
        assert menge - k * 5 >= 20 or k == 0, menge
    assert ES.verkaufslose(24, 20, 5, False) == 0, (
        "weniger als ein Los ueber dem Bedarf bleibt liegen"
    )
    assert ES.verkaufslose(25, 20, 5, False) == 1
    assert ES.verkaufslose(0, 0, 5, False) == 0


def test_harte_grenze_geht_bis_unter_die_grenze():
    assert ES.verkaufslose(150, 150, 20, True) == 0
    assert ES.verkaufslose(151, 150, 20, True) == 1
    assert ES.verkaufslose(230, 150, 20, True) == 4


def test_verkaufen_schickt_den_ganzen_ueberschuss_in_buendeln(monkeypatch):
    gesendet = []
    monkeypatch.setattr(ES, "sende", lambda b, *a, **k: gesendet.append(b) or [])
    monkeypatch.setattr(
        ES, "befehl", lambda *a, **k: (_ for _ in ()).throw(AssertionError("Einzelweg benutzt"))
    )
    monkeypatch.setattr(ES, "nahrung_auf_kante", lambda *a, **k: {})
    text = ES.verkaufen({"stein": 406, "eisen": 67, "holz": 22, "leute": 200}, stein_reserve=20)
    lose = [c["spielbefehl"]["werte"][1] for b in gesendet for c in b["befehle"]]
    assert lose.count(ES.WAREN_NR["stein"]) == 77 and lose.count(ES.WAREN_NR["eisen"]) == 13, text
    assert all(len(b["befehle"]) <= ES.VERKAUF_JE_SENDUNG for b in gesendet)
    assert "stein x77" in text and "eisen x13" in text


def test_waren_ohne_gerechneten_bedarf_gehen_einzeln(monkeypatch):
    """Hopfen, Weizen, Mehl, Pech: Reserve 0, Bedarf der Ketten nicht gemessen - weiter ein Los je Runde, nicht alles auf einmal."""
    gesendet = []
    monkeypatch.setattr(ES, "sende", lambda b, *a, **k: gesendet.append(b) or [])
    monkeypatch.setattr(ES, "nahrung_auf_kante", lambda *a, **k: {})
    ES.verkaufen({"hopfen": 50, "weizen": 30, "mehl": 12, "pech": 9, "leute": 100}, stein_reserve=0)
    lose = [c["spielbefehl"]["werte"][1] for b in gesendet for c in b["befehle"]]
    assert sorted(lose) == sorted(ES.WAREN_NR[w] for w in ("hopfen", "weizen", "mehl", "pech"))


class _Lage:
    """Ein Holzfaeller (Typ 3) mit Holz in der Hand steht im Wartezustand 7 am selben Fleck."""

    def __init__(self, teile):
        self.G = {100 + i: {"besitzer": 2, "typ": STW.LAGER} for i in range(teile)}
        self.L = {
            7: {
                "besitzer": 2,
                "arbeitsplatz": 55,
                "typ": 3,
                "zustand": 7,
                "ladung": 4,
                "x": 10,
                "y": 10,
            }
        }


def _waechter(max_teile, gebaut):
    return STW.Stillstand(
        2, lambda n: 48, lambda: gebaut.append(1) or (1, 1), lambda: False, max_teile=max_teile
    )


def test_waechter_baut_kein_fuenftes_vorratslager():
    lage, gebaut = _Lage(ES.LAGER_TEILE_MAX), []
    w = _waechter(ES.LAGER_TEILE_MAX, gebaut)
    w.schritt(0, lage.L, lage.G)
    ev = w.schritt(STW.HANDELN_AB, lage.L, lage.G)
    assert not gebaut and "hoechstens 16 Teilen" in " ".join(ev)


def test_waechter_baut_unter_der_grenze_weiter_an():
    lage, gebaut = _Lage(ES.LAGER_TEILE_MAX - 1), []
    w = _waechter(ES.LAGER_TEILE_MAX, gebaut)
    w.schritt(0, lage.L, lage.G)
    w.schritt(STW.HANDELN_AB, lage.L, lage.G)
    assert gebaut == [1]


def test_lenker_setzt_die_grenze_fuer_jede_partie():
    quelle = open(ES.__file__, encoding="utf-8").read()
    assert ES.LAGER_MAX == 4 and ES.LAGER_TEILE_MAX == 16, (
        "4 Vorratslager zu je 4 Teilen (gemessen)"
    )
    assert (
        "wirt.lager_max_teile = LAGER_TEILE_MAX" in quelle and "max_teile=LAGER_TEILE_MAX" in quelle
    )
    assert "elif voll and runde % 3 == 0:" not in quelle, "Verkauf wieder nur jede dritte Runde"


def test_planer_baut_nicht_ueber_die_grenze_des_lenkers():
    from selfaware.macro import ertragsplaner as EP

    st = {
        "holz": 46,
        "stein": 20,
        "eisen": 20,
    }  # Holz fast voll im Teil (46 von 48), 3 Teile belegt
    assert EP.lager_anbauen(st, 3) == ["holz"], "ohne Lenker-Grenze: wie bisher"
    assert EP.lager_anbauen(st, 3, grenze=ES.LAGER_TEILE_MAX) == ["holz"]
    voll16 = {"holz": 16 * 48 - 2}
    assert EP.lager_anbauen(voll16, 16, grenze=ES.LAGER_TEILE_MAX) == [], (
        "16 Teile = 4 Vorratslager: kein fuenftes"
    )
    assert EP.lager_anbauen(voll16, 15, grenze=ES.LAGER_TEILE_MAX) == ["holz"]
