"""Lord-Kill mit aller Macht (Daniel 15.11.2026 23:10: "immer noch nicht angegriffen wird obwohl es locker reicht fuer den kill, wie gesagt
je frueher der kill kommt desto besser"; 19.10.: "wir gehen alle gleichzeitig mit aller Macht auf den Lord").

Gemessen in Partie 23:05 (data/research/partie_20261115_230555_lenker_sp2.txt): Bedarf gerechnet 5-12, 6 Bereitstellungen abgebrochen,
ein Angriff mit 9 Assassinen - Lord 165.000 -> 95.000, alle 9 tot. Daneben raideten bis zu 140 Assassinen Gebaeude."""

import pytest


def _modul():
    try:
        import selfaware.micro.tasks.assassinen as AS
    except RuntimeError as ex:  # ohne Spielinstanz laesst sich das Modul nicht laden
        pytest.skip(str(ex))
    return AS


def _e(nr, besitzer, typ, x, y, **k):
    d = {
        "nr": nr,
        "gruppe": 0,
        "besitzer": besitzer,
        "typ": typ,
        "x": x,
        "y": y,
        "leben": 10000,
        "zustand": 1,
        "zielart": 0,
        "zieleinheit": 0,
        "laufx": x,
        "laufy": y,
        "ladung": 0,
        "arbeitsplatz": 0,
        "erreichbar": 1,
        "nahziel": -1,
        "nahangreifer": -1,
    }
    d.update(k)
    return d


def _szene(n=12):
    AS = _modul()
    a = AS.Einzeln(1)
    a.lord_aus, a.LORD_SPAETESTENS = False, 0  # wie der Lenker mit lord_sofort=ja (S162)
    L = {1: _e(1, 1, 55, 100, 100, leben=150000), 60: _e(60, 2, 55, 340, 100, leben=165000)}
    for i in range(n):
        L[200 + i] = _e(200 + i, 1, 73, 250, 90 + 2 * i, leben=12500)
    a.aufnehmen(list(range(200, 200 + n)))
    return a, L


def _schritt(a, L, t):
    erg = a.schritt(L, {}, sichere_orte=[(100, 100)], tick=t)
    return erg[0] if isinstance(erg, tuple) else erg


def test_alle_gehen_in_die_lord_gruppe_nicht_nur_der_bedarf():
    a, L = _szene(12)
    ev = _schritt(a, L, 20000)
    assert a.lordtrupp["phase"] == "bereit", ev
    assert len(a.lordtrupp["mitglieder"]) == 12, [z for z in ev if "LORD" in z]


def test_beim_start_greifen_alle_an_auch_wer_noch_anlaeuft():
    a, L = _szene(12)
    _schritt(a, L, 20000)
    plaetze = dict(a.lordtrupp["platz"])
    for k in sorted(plaetze)[:8]:  # 8 von 12 stehen am Platz, 4 laufen noch
        L[k].update(x=plaetze[k][0], y=plaetze[k][1], laufx=plaetze[k][0], laufy=plaetze[k][1])
    ev = _schritt(a, L, 20200)
    assert a.lordtrupp["phase"] == "angriff", [z for z in ev if "LORD" in z]
    assert len(a.lordtrupp["mitglieder"]) == 12 and a.angriffe[-1]["groesse"] == 12


def test_gemessener_bedarf_aus_dem_letzten_angriff():
    a, _L = _szene(1)
    assert a._lord_bedarf_gemessen(165000) is None, "ohne beendeten Angriff keine Messung"
    a.angriffe.append({"fertig": True, "groesse": 9, "lord_vorher": 165000, "lord_nachher": 95000})
    assert (
        a._lord_bedarf_gemessen(165000) == 22
    )  # 70.000 / 9 = 7.778 je Assassine -> 165.000 / 7.778 = 21,2 -> 22
    a.angriffe.append(
        {"groesse": 50, "lord_vorher": 95000, "lord_nachher": 0}
    )  # laeuft noch: zaehlt nicht
    assert a._lord_bedarf_gemessen(95000) == 13
