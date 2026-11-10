"""B-182: Eichung der Wirkungsrechnung aus den Erfolgszeilen der Raid-Module, ohne Spiel."""

import json

import selfaware.services.spielwerte as SW
from selfaware.baukasten import eichung as EI

ZEILEN = [
    "  1000 | x | BRANDTRUPP: Sklave 5 -> Gebaeude 7 (Typ 1) bei (10, 10), 20 Felder",
    "  1500 | x | BRANDTRUPP: Sklave 5 hat Gebaeude 7 (Typ 1) angezuendet (Feuer 300) - weiter",
    "  1600 | x | BRANDTRUPP: Sklave 6 -> Gebaeude 8 (Typ 1) bei (10, 12), 30 Felder",
    "  2000 | x | REITERJAGD: Reiter 9 jagt Arbeiter 40 (Typ 3) in 25 Feldern",
    "  2100 | x | REITERJAGD: Reiter 9 hat Arbeiter 41 erledigt",  # anderes Ziel: zaehlt nicht
    "  2200 | x | NAHKAMPF-RAID: 11 (Typ 75) -> Gebaeude 12 (Typ 3) bei (5, 5), 2 Wegpunkte, 8 Felder",
    "  2900 | x | NAHKAMPF-RAID: 11 (Typ 75) hat Gebaeude 12 erledigt; NAHKAMPF-RAID: 13 (Typ 26) -> Arbeiter 14 (Typ 1) bei (1, 1), 0 Wegpunkte, 3 Felder",
    "ohne Takt: BRANDTRUPP: Sklave 6 hat Gebaeude 8 (Typ 1) angezuendet",
    "  2000 | x | REITERJAGD: Reiter 10 jagt Arbeiter 50 (Typ 3) in 25 Feldern",
    # wie im Spiel: Erfolg mit dem alten Ziel vor der neuen Zuweisung derselben Einheit, in einer Zeile
    "  2600 | x | REITERJAGD: Reiter 10 hat Arbeiter 50 erledigt; REITERJAGD: Reiter 10 jagt Arbeiter 51 (Typ 1) in 30 Feldern",
]
# Reiter 20 wechselt zweimal das Ziel, bevor er trifft: ein Versuch, gezaehlt vom ersten Zuweisen
WECHSEL = [
    "  5000 | x | REITERJAGD: Reiter 20 jagt Arbeiter 60 (Typ 3) in 40 Feldern",
    "  5100 | x | REITERJAGD: Reiter 20 jagt Arbeiter 61 (Typ 3) in 30 Feldern",
    "  5200 | x | REITERJAGD: Reiter 20 jagt Arbeiter 62 (Typ 1) in 20 Feldern",
    "  5900 | x | REITERJAGD: Reiter 20 hat Arbeiter 62 erledigt",
]


def test_paart_zuweisung_und_erfolg_je_einheit_und_ziel():
    roh = EI.aus_zeilen(ZEILEN)
    assert roh[(71, "g")] == {"zuweisungen": 2, "dauer": [500], "weg": [20]}
    # Reiter 9: Erfolg fuer ein anderes Ziel zaehlt nicht; Reiter 10: Erfolg vor der neuen Zuweisung in derselben Zeile zaehlt
    assert roh[(74, "e")] == {"zuweisungen": 3, "dauer": [600], "weg": [25]}
    assert roh[(75, "g")] == {"zuweisungen": 1, "dauer": [700], "weg": [8]}
    assert roh[(26, "e")]["zuweisungen"] == 1  # die Art steht in der Zeile des Nahkampf-Raids


def test_anteil_mit_gedachter_zuweisung_und_takte_am_ziel_ohne_weg():
    d = EI.zusammenfassen(EI.aus_zeilen(ZEILEN), ["a"])
    s = d["arten"]["71"]["g"]
    assert s["anteil"] == round(2 / 4, 4)  # (1 Erfolg + 1) / (2 Zuweisungen + 2)
    assert s["takte_am_ziel"] == round(max(0.0, 500 - 20 * SW.takte_je_feld(71, "trupp")), 1)
    assert d["arten"]["74"]["e"]["anteil"] == round(2 / 5, 4)
    assert d["arten"]["74"]["e"]["takte_am_ziel"] == round(
        max(0.0, 600 - 25 * SW.takte_je_feld(74, "trupp")), 1
    )


def test_laden_nimmt_nur_werte_mit_genug_daten(tmp_path):
    p = tmp_path / "e.json"
    arten = {
        "71": {"g": {"zuweisungen": 40, "erfolge": 9, "anteil": 0.24, "takte_am_ziel": 600.0}},
        "74": {"e": {"zuweisungen": 40, "erfolge": 2, "anteil": 0.07, "takte_am_ziel": 900.0}},
        "75": {"e": {"zuweisungen": 3, "erfolge": 0, "anteil": 0.2, "takte_am_ziel": None}},
    }
    p.write_text(
        json.dumps({"min_zuweisungen": 10, "min_erfolge": 5, "arten": arten}), encoding="utf-8"
    )
    assert EI.laden(str(p)) == {(71, "g"): (0.24, 600.0), (74, "e"): (0.07, None)}
    assert EI.laden(str(tmp_path / "fehlt.json")) == {}


def test_zielwechsel_setzt_den_versuch_fort():
    """B-182 Reihe 10: Die Reiterjagd waehlt jede Runde neu; gezaehlt wird der Versuch bis zum Erfolg, nicht jede Zuweisung."""
    assert EI.aus_zeilen(WECHSEL)[(74, "e")] == {"zuweisungen": 1, "dauer": [900], "weg": [40]}


def test_modul_ohne_erfolgszeile_zaehlt_nicht():
    """Vor B-182 schrieb die Reiterjagd keine Erfolgszeilen; ihre Zuweisungen sind dann keine Fehlschlaege."""
    roh = EI.aus_zeilen([z for z in ZEILEN if "erledigt" not in z and "angezuendet" not in z])
    assert (74, "e") not in roh
    # Brandtrupp und Nahkampf-Raid zaehlen auch ohne Erfolg: Ihre Versuche sind echte Fehlschlaege (Reihe 11: 34 Schwertkaempfer, 0 Erfolge)
    assert roh[(71, "g")] == {"zuweisungen": 2, "dauer": [], "weg": []}
    assert roh[(75, "g")] == {
        "zuweisungen": 1,
        "dauer": [],
        "weg": [],
    }  # Zeile 2900 mit dem Erfolg ist mit herausgefallen


def test_versuch_den_das_partieende_abschneidet_zaehlt_nicht(tmp_path):
    """Ein Versuch, der bei Partieende noch laeuft und juenger ist als der Median bis zum Erfolg, ist kein Fehlschlag."""
    zeilen = [
        "  1000 | x | NAHKAMPF-RAID: 1 (Typ 75) -> Gebaeude 9 (Typ 1) bei (5, 5), 0 Wegpunkte, 10 Felder",
        "  3000 | x | NAHKAMPF-RAID: 1 (Typ 75) hat Gebaeude 9 erledigt",
        "  3500 | x | NAHKAMPF-RAID: 2 (Typ 75) -> Gebaeude 8 (Typ 1) bei (5, 5), 0 Wegpunkte, 10 Felder",
        "  4000 | x | NAHKAMPF-RAID: 3 (Typ 75) -> Gebaeude 7 (Typ 1) bei (5, 5), 0 Wegpunkte, 10 Felder",
        "  6100 | x | Ende",
    ]
    p = tmp_path / "k.txt"
    p.write_text(chr(10).join(zeilen), encoding="utf-8")
    w = EI.aus_mitschriften([str(p)])["arten"]["75"]["g"]
    # Ende bei 6.100: Einheit 2 seit 2.600 und Einheit 3 seit 2.100 Takten offen, laenger als der Median 2.000 - Fehlschlaege
    assert (w["zuweisungen"], w["erfolge"], w["abgeschnitten"]) == (3, 1, 0)
    # Ende bei 5.000: beide juenger als 2.000 Takte - abgeschnitten, keine Fehlschlaege
    p.write_text(chr(10).join(zeilen[:-1] + ["  5000 | x | Ende"]), encoding="utf-8")
    w = EI.aus_mitschriften([str(p)])["arten"]["75"]["g"]
    assert (w["zuweisungen"], w["erfolge"], w["abgeschnitten"]) == (1, 1, 2)
