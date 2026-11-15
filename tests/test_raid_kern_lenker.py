"""S158 (Daniel 15.11.2026 01:13): die Lenker-Schleife zaehlt, wie viele Takte zwischen zwei Steuerschleifen liegen - ohne Spiel."""

from selfaware.runtime.live import erstes_spiel as ES


def test_steuer_zeile_zaehlt_die_takte_zwischen_zwei_schleifen():
    assert ES.steuer_zeile([]) == "STEUERUNG: noch keine zwei Schleifen"
    z = ES.steuer_zeile([100, 130, 150, 210, 230])
    assert "5 Schleifen" in z and "Median 25.0" in z and "groesster 60" in z
    # ein Partiewechsel (Takt faellt) zaehlt nicht als Abstand
    assert "Median 20" in ES.steuer_zeile([40000, 2, 22]) and "groesster 20" in ES.steuer_zeile([40000, 2, 22])


def test_wirtschaft_rechnet_so_oft_wie_bisher():
    # Partie 26: Median 169,5 Takte zwischen zwei Lenker-Runden
    assert ES.WIRTSCHAFT_TAKTE == 170 and ES.SCHNELLE_STEUERUNG is True


def _einheit(nr, sp, typ, x, y):
    return {"nr": nr, "besitzer": sp, "typ": typ, "x": x, "y": y, "leben": 10000, "zielart": 0, "zieleinheit": 0, "zielgebaeude": 0,
            "laufx": x, "laufy": y, "nahziel": 0}


def test_s167_erster_angriff_nimmt_jede_welle_der_starttruppe_und_uebergibt_an_den_raid(monkeypatch):
    # Partie 32: der erste Angriff lief bei Takt 149, die Starttruppe kam erst bei Takt 202 und 403 - "0 Nahkaempfer"
    # zwei Apfelplantagen des Gegners - der Raid gibt jedem Ziel eine Einheit (Wirkung: ein Ziel je Einheit)
    G = {50: {"nr": 50, "besitzer": 2, "typ": 32, "x": 60, "y": 20, "leben": 1000},
         51: {"nr": 51, "besitzer": 2, "typ": 32, "x": 62, "y": 26, "leben": 1000}}
    lagen = [{}, {330: _einheit(330, 1, 24, 20, 20)}, {330: _einheit(330, 1, 24, 21, 20), 331: _einheit(331, 1, 24, 20, 21)}]
    jetzt = {"L": {}}
    gegeben, zeilen = [], []
    monkeypatch.setattr(ES, "runde_lesen", lambda: ({"t": 1}, jetzt["L"], G))
    monkeypatch.setattr(ES, "befehl", lambda b, *a, **k: gegeben.append(b) or ["OK"])
    monkeypatch.setattr(ES, "schreib", zeilen.append)
    monkeypatch.setattr(ES, "tick", lambda: 1)
    monkeypatch.setattr(ES, "raid_kern", lambda wegf, runde, ereignis: None)        # ohne Spiel kein Kern
    monkeypatch.setattr(ES, "RAIDS", True)
    monkeypatch.setattr(ES, "_KARTE", [])
    monkeypatch.setattr(ES, "_ERSTER", {"nk": None, "wf": None, "zeit": 0.0})
    for wann, L in zip(("beim Start", "erste Welle", "zweite Welle"), lagen):
        jetzt["L"] = L
        ES.erster_angriff(wann)
    nk = ES._ERSTER["nk"]
    assert nk.mitglieder == {330, 331}
    assert sorted(nk.ziel.values()) == [("g", 50), ("g", 51)]
    assert "noch kein eigener Nahkaempfer" in zeilen[0]
    assert any("erste Welle" in z and "[330]" in z for z in zeilen) and any("zweite Welle" in z and "[331]" in z for z in zeilen)
    assert gegeben, "die Starttruppe bekam keinen Befehl"

    class Raid:
        class nahkampf:
            ziel = {331: ("g", 77)}       # was der Raid schon selbst entschieden hat, bleibt

    ES.erster_angriff_uebergeben(Raid, None)
    assert Raid.nahkampf.ziel == {330: nk.ziel[330], 331: ("g", 77)}
