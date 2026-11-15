"""S170 (Daniel 15.11.2026 11:44): alle Stein- und Eisenvorkommen, das mit dem kuerzesten Laufweg in Zeit zuerst, ohne Anzahl."""

from selfaware.macro import rohstoffe as RO
from selfaware.runtime.live import erstes_spiel as ES
from selfaware.services import wegkarte as W


def _karte(breite, hoehe, wand=()):
    """Weg-Ebene wie im Spiel: je Feld die Bits der erlaubten Schritte; in eine Wand fuehrt kein Schritt."""
    f = {}
    for y in range(hoehe):
        for x in range(breite):
            link = 0
            if (x, y) not in wand:
                for bit, (dx, dy) in W.RICHTUNG.items():
                    n = (x + dx, y + dy)
                    if 0 <= n[0] < breite and 0 <= n[1] < hoehe and n not in wand:
                        link |= bit
            f[(x, y)] = (link, 0, 0, 0, 0, -1)
    # S170-Fix: dasselbe Format wie im Spiel - die Wegfuehrung haelt die Gelaendekarte (wegkarte.als_gelaende), nicht die Feldtabelle
    return W.als_gelaende(
        {"tick": 1, "x0": 0, "y0": 0, "x1": breite - 1, "y1": hoehe - 1, "f": f},
        groesse=max(breite, hoehe),
    )


def test_reihenfolge_nach_laufzeit_nicht_nach_luftlinie():
    # Lager bei (0, 1). Steinbruch-Stelle (3, 0) liegt in Luftlinie naeher als die Minen-Stelle (6, 4); eine Wand zwingt den Weg
    # zum Stein aussen herum - dann kommt die Mine zuerst
    plaetze = {20: {(3, 0)}, 5: {(9, 6)}}
    offen, wand = _karte(16, 12), {(2, y) for y in range(0, 9)} | {(x, 8) for x in range(2, 9)}
    a, b = RO.Rohstoffpflicht(plaetze), RO.Rohstoffpflicht(plaetze)
    assert a.ordnen(offen, [(0, 1)]) and b.ordnen(_karte(16, 12, wand=wand), [(0, 1)])
    assert [t[1] for t in a.liste] == [20, 5]
    assert [t[1] for t in b.liste] == [5, 20]
    assert all(t[0] % RO.TAKTE_JE_FELD == 0 for t in a.liste + b.liste)
    assert not a.ordnen(
        offen, [(0, 1)]
    )  # gleiche Karte, gleiches Lager, gleiche Stellen: nichts neu


def test_ein_bau_nimmt_jede_ueberdeckende_stelle_beider_arten_weg():
    rp = RO.Rohstoffpflicht({20: {(10, 10), (12, 10), (16, 10)}, 5: {(14, 12), (30, 30)}})
    rp.ordnen(_karte(40, 40), [(0, 0)])
    rp.gebaut(20, (10, 10))  # 10..15 x 10..15
    assert rp.plaetze == {20: {(16, 10)}, 5: {(30, 30)}} and len(rp.offen()) == 2


def test_lenker_baut_eins_je_runde_wartet_auf_arbeiter_und_springt_nur_bei_fehlendem_stein(
    monkeypatch,
):
    from selfaware.macro import standort as SO

    gebaut = []
    monkeypatch.setattr(ES, "_KARTE", [])
    monkeypatch.setattr(ES, "_RP", None)
    monkeypatch.setattr(ES, "ROHSTOFFE_ALLE", True)
    monkeypatch.setattr(
        SO, "platzkarte", lambda mapper, b, *a, **k: {(2, 1)} if b == 4 else {(12, 1)}
    )  # Mine naeher
    monkeypatch.setattr(
        ES, "kosten_spiel", lambda typ: {5: {"holz": 20, "stein": 6}, 20: {"holz": 20}}.get(typ, {})
    )
    monkeypatch.setattr(
        ES, "baue_schnell", lambda typ, x, y, r, **kw: gebaut.append((typ, r)) or ((x, y), "gebaut")
    )
    monkeypatch.setattr(ES, "baue_joch", lambda o, **kw: (o[0] + 7, o[1] + 2))

    class Wf:
        gelaende = _karte(20, 8)

    G = {1: {"besitzer": 1, "typ": 10, "x": 0, "y": 0}}
    ev = ES.rohstoffe_bauen(
        {"feuer": 1, "holz": 99, "stein": 99}, G, Wf
    )  # zu wenig Bauern am Feuer: nichts
    assert gebaut == [] and any("platzkarte" in e for e in ev) and any("geordnet" in e for e in ev)
    assert (
        ES.rohstoffe_arbeiter() == ES.ARBEITER_JE[5]
    )  # das Heer laesst die Minenarbeiter am Feuer
    ev = ES.rohstoffe_bauen(
        {"feuer": 9, "holz": 99, "stein": 0}, G, Wf
    )  # der Mine fehlt nur Stein: der Steinbruch
    assert gebaut == [(20, 0)] and any("Steinbruch" in e and "Joch" in e for e in ev)
    ES.rohstoffe_bauen(
        {"feuer": 9, "holz": 99, "stein": 9}, G, Wf
    )  # jetzt die Mine, genau ein Bau je Runde
    assert gebaut == [(20, 0), (5, 0)]


def test_abgelehnte_stelle_holt_eine_frische_platzkarte(monkeypatch):
    from selfaware.macro import standort as SO

    karten = []
    monkeypatch.setattr(ES, "_KARTE", [])
    monkeypatch.setattr(ES, "_RP", None)
    monkeypatch.setattr(
        SO,
        "platzkarte",
        lambda mapper, b, *a, **k: karten.append(b) or ({(5, 5)} if b == 6 else set()),
    )
    monkeypatch.setattr(ES, "kosten_spiel", lambda typ: {20: {"holz": 20}}.get(typ, {}))
    monkeypatch.setattr(ES, "baue_schnell", lambda typ, x, y, r, **kw: (None, "platz"))

    class Wf:
        gelaende = _karte(20, 20)

    G = {1: {"besitzer": 1, "typ": 10, "x": 0, "y": 0}}
    ES.rohstoffe_bauen({"feuer": 9, "holz": 99}, G, Wf)
    assert ES._RP is None  # veraltet: weg
    ES.rohstoffe_bauen({"feuer": 9, "holz": 99}, G, Wf)
    assert karten.count(6) == 2  # zweite Runde: frische platzkarte


def test_nur_ein_entscheider_fuer_steinbrueche_und_minen():
    import pathlib

    src = pathlib.Path(ES.__file__).read_text(encoding="utf-8")
    plan = (pathlib.Path(ES.__file__).parents[2] / "macro" / "ertragsplaner.py").read_text(
        encoding="utf-8"
    )
    # Kausalmodell: 5 und 20 nur ohne Rohstoffpflicht unter den Kandidaten
    assert "(3, 32, 7) + (() if ROHSTOFFE_ALLE else (5, 20))" in src
    # beide Steinpflichten schweigen mit Rohstoffpflicht
    assert src.count("and not ROHSTOFFE_ALLE:    # S170") == 2
    # Ertragsplaner: 20 und 5 raus, sobald der Lenker die Rohstoffpflicht setzt
    assert (
        'kand = [k for k in kand if k["typ"] not in (20, 5)]' in plan
        and "ausbau.rohstoffe_extern = ROHSTOFFE_ALLE" in src
    )


def test_laufzeit_auch_auf_der_startkarte_vor_dem_ersten_wegkarten_lesen():
    # die Wegfuehrung startet mit der Rohstoffkarte (G Gruenland, s Gestruepp, . Boden, b Stein, w Wasser) - Partie 34: TypeError
    start = ["GGsww....", "G.sw.....", "Gs.ww...."]
    d = RO.abstaende(start, [(0, 0)])
    assert (
        d[(2, 2)] == 2 and (3, 0) not in d and (8, 0) not in d
    )  # Wasser sperrt, dahinter nichts erreichbar


def test_steinbruch_bekommt_so_viele_joche_wie_der_weg_verlangt(monkeypatch):
    import selfaware.learning.kausal as KM
    from selfaware.macro import standort as SO

    joche = []
    monkeypatch.setattr(ES, "_KARTE", [])
    monkeypatch.setattr(ES, "_RP", None)
    monkeypatch.setattr(SO, "platzkarte", lambda mapper, b, *a, **k: {(30, 1)} if b == 6 else set())
    monkeypatch.setattr(ES, "kosten_spiel", lambda typ: {20: {"holz": 20}}.get(typ, {}))
    monkeypatch.setattr(ES, "baue_schnell", lambda typ, x, y, r, **kw: ((x, y), "gebaut"))
    monkeypatch.setattr(ES, "baue_joch", lambda o, **kw: joche.append(o) or (o[0] + 7, o[1] + 2))

    class Wf:
        gelaende = _karte(40, 8)

    ES.rohstoffe_bauen(
        {"feuer": 9, "holz": 99}, {1: {"besitzer": 1, "typ": 10, "x": 0, "y": 0}}, Wf
    )
    # Lager 0..2 x 0..2, Bruch an (30, 1): der Laufweg bis neben den Bruch (Spalte 29) ist 27 Felder
    assert len(joche) == KM.ochsen_fuer(27) >= 2
