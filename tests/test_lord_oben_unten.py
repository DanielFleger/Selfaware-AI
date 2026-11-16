"""Lord-Angriff: Kletterweg nur, solange der Lord oben auf seinem Bergfried steht (Daniel 16.11.2026 21:42 "assassinen schienen gar nicht
immer auf den lord zu spammklicken sondern einfach nur auf das keep geschickt zu werden", 21:52 "Ja, bauen").

17.10. (1017i): oben klettert der Angriffsbefehl nicht - darum dort Laufbefehl bis neben ihn. Unten: sofort Angriffsbefehl auf den Lord, aus
jeder Entfernung (das Spiel laeuft dann selbst hin und folgt ihm)."""

import pytest


def _modul():
    try:
        import selfaware.micro.tasks.assassinen as AS
    except RuntimeError as ex:  # ohne Spielinstanz laesst sich das Modul nicht laden
        pytest.skip(str(ex))
    return AS


@pytest.fixture(autouse=True)
def _stapel_wie_vorher(monkeypatch):
    """Diese Szenen pruefen anderes (Gruppe, Frist, Kletterweg, Push) mit 12-14 Assassinen. Die Mindestgroesse des Stapels (LORD_STAPEL_MIN,
    17.11.2026) und das Warten ueber die Frist (BEREIT_WARTEN) haben eigene Tests in test_lord_alle.py - hier wie vor dem 17.11."""
    AS = _modul()
    monkeypatch.setattr(AS.Einzeln, "LORD_STAPEL_MIN", 1)
    monkeypatch.setattr(AS.Einzeln, "BEREIT_WARTEN", 1)


def _e(nr, besitzer, typ, x, y, **k):
    """Einheit wie im Lageprotokoll (gleiche Felder wie test_lord_alle._e - Testdateien importieren einander nicht, die CI kennt kein
    Paket tests)."""
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


def _angriff(lord_oben):
    """12 Assassinen stehen alle am Bereitstellungsplatz -> der Stapel greift an. Rueckgabe: Befehle der Angriffsrunde."""
    AS = _modul()
    a = AS.Einzeln(1)
    a.lord_aus, a.LORD_SPAETESTENS = False, 0
    L = {1: _e(1, 1, 55, 100, 100, leben=150000), 60: _e(60, 2, 55, 340, 100, leben=165000)}
    for i in range(12):
        L[200 + i] = _e(200 + i, 1, 73, 250, 90 + 2 * i, leben=12500)
    a.aufnehmen(list(range(200, 212)))
    # Bergfried des Gegners (Typ 41, 7x7, Ecke links oben): oben = der Lord steht auf seiner Grundflaeche
    G = {
        900: {
            "nr": 900,
            "typ": 41,
            "besitzer": 2,
            "x": 337 if lord_oben else 360,
            "y": 97,
            "leben": 5000,
            "uid": 1,
        }
    }
    a.schritt(L, G, sichere_orte=[(100, 100)], tick=20000)
    plaetze = dict(a.lordtrupp["platz"])
    for k, p in plaetze.items():
        L[k].update(x=p[0], y=p[1], laufx=p[0], laufy=p[1])
    ev, bef = a.schritt(L, G, sichere_orte=[(100, 100)], tick=20200)
    assert a.lordtrupp["phase"] == "angriff", [z for z in ev if "LORD" in z]
    return bef


def _lord_befehle(bef):
    ziel = sorted(
        n
        for b in bef
        if "angriff" in b and b["angriff"].get("ziel") == 60
        for n in b["angriff"]["einheiten"]
    )
    lauf = sorted(
        n
        for b in bef
        if "angriff" in b and b["angriff"].get("lauf") == [340, 100]
        for n in b["angriff"]["einheiten"]
    )
    return ziel, lauf


def test_lord_oben_kletterweg():
    ziel, lauf = _lord_befehle(_angriff(True))
    assert lauf == list(range(200, 212)) and not ziel, (ziel, lauf)


def test_lord_unten_sofort_angriff_aus_jeder_entfernung():
    ziel, lauf = _lord_befehle(_angriff(False))
    assert ziel == list(range(200, 212)) and not lauf, (ziel, lauf)


def test_auf_bergfried_nur_eigener_bergfried():
    sicht = pytest.importorskip("selfaware.services.sicht")
    lord = {"x": 340, "y": 100, "besitzer": 2}
    assert sicht.auf_bergfried(lord, {1: {"typ": 41, "besitzer": 2, "x": 337, "y": 97}})
    assert not sicht.auf_bergfried(lord, {1: {"typ": 41, "besitzer": 1, "x": 337, "y": 97}}), (
        "fremder Bergfried zaehlt nicht"
    )
    assert not sicht.auf_bergfried(lord, {1: {"typ": 41, "besitzer": 2, "x": 330, "y": 97}}), (
        "7 breit: 330..336, Lord bei 340 daneben"
    )
    assert 41 in sicht.BERGFRIED
