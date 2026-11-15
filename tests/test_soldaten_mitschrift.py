"""B-182 Mitschrift je Takt der eigenen Soldaten (tools/experiments/soldaten_mitschrift.py) - ohne Spiel. Fall aus Partie 10 (S133):
Bogenschuetze 308 verschwand, seine Nummer trug danach ein Bauer."""

from selfaware.tools.experiments import soldaten_mitschrift as SM


def _e(sp, typ, x, y, **k):
    d = {"besitzer": sp, "typ": typ, "x": x, "y": y, "zustand": 1, "leben": 10000, "zielart": 0, "zieleinheit": 0, "nahziel": 0,
         "laufx": x, "laufy": y, "planx": x, "plany": y, "gruppe": 0, "logikzustand": 1, "laufmerker": 0, "sammelgang": 0,
         "teleport": 0, "sammelmerker": 0, "beweglich": 1, "merker413": 0, "gebiet": 1}
    d.update(k)
    return d


def test_eine_nummer_die_zum_bauern_wird_ist_verschwunden_und_nur_aenderungen_zaehlen():
    alt = {308: _e(1, 22, 153, 280, zustand=11), 309: _e(1, 22, 153, 281), 500: _e(2, 24, 200, 200)}
    neu = {308: _e(1, 1, 149, 281, zustand=5, leben=2500), 309: _e(1, 22, 153, 281), 500: _e(2, 24, 201, 200)}
    geaendert, weg = SM.vergleiche(alt, neu, 1)
    # S139/S143/S148: hinter den alten 10 Stellen geplantes Ziel, Gruppe, die 7 Filterfelder, das Gebiet, dann der Besitzer
    assert geaendert == {} and weg == [(308, [1, 149, 281, 5, 2500, 0, 0, 0, 149, 281, 149, 281, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1])]
    neu[309] = _e(1, 22, 154, 281)
    del neu[308]
    geaendert, weg = SM.vergleiche(alt, neu, 1)
    assert list(geaendert) == [309] and weg == [(308, None)]


def test_die_umgebung_nennt_alle_einheiten_bis_12_felder():
    L = {1: _e(1, 22, 100, 100), 2: _e(0, 9, 112, 100), 3: _e(2, 24, 113, 100, nahziel=1)}
    assert [u[0] for u in SM.umgebung(L, (100, 100))] == [1, 2]


def test_ein_laufender_soldat_der_auf_einem_feld_haengt_wird_einmal_mit_seiner_umgebung_gemeldet():
    # Partie 11 (S134): Speertraeger 335 verlor 31 Takte auf 2 Feldern; Speertraeger 12 Takte je flaches Feld -> Grenze 24
    stand = {}
    L = {335: _e(1, 24, 176, 201, zustand=101), 700: _e(0, 9, 177, 201), 800: _e(2, 1, 179, 201)}
    assert SM.stocken(stand, L, 2270, 1) == []
    assert SM.stocken(stand, L, 2294, 1) == []                      # 24 Takte: noch nicht
    aus = SM.stocken(stand, L, 2295, 1)
    assert len(aus) == 1 and aus[0]["stockt"] == 335 and aus[0]["seit"] == 2270 and [u[0] for u in aus[0]["umgebung"]] == [700]
    assert SM.stocken(stand, L, 2400, 1) == []                      # einmal je Halt
    L[335] = _e(1, 24, 175, 200, zustand=101)
    assert SM.stocken(stand, L, 2401, 1) == [] and stand[335][0] == (175, 200)
    L[335] = _e(1, 24, 175, 200, zustand=1)                         # er steht ohne zu laufen: kein Stocken
    assert SM.stocken(stand, L, 2500, 1) == []



def test_vor_der_partie_wartet_die_mitschrift_statt_abzubrechen():
    # Partie 14 (14.11.2026 19:32): mit dem Spiel gestartet, vor der Partie - der Kern hatte noch nichts geschrieben, die Mitschrift
    # brach mit 'Kennung 0x0 / Aufbau 0' ab
    from selfaware.game.kern_leitung import FalscherAufbau

    class Leer:
        def lesen(self):
            raise FalscherAufbau("Kennung 0x0 / Aufbau 0, erwartet 0x4b4d4153 / 5")

    class Laeuft:
        def lesen(self):
            return "Weltbild"

    assert SM.lies(Leer()) is None and SM.lies(Laeuft()) == "Weltbild"
    import inspect
    assert "w = lies(le)" in inspect.getsource(SM.main) and "le.lesen()" not in inspect.getsource(SM.main)
