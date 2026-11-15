"""B-182 S139: tools/analysis/befehle_greifen.py - griff jeder Laufbefehl? Ohne Spiel. Fall aus Partie 15 (14.11.2026): der Befehl
an Bogenschuetze 309 nach (186,154) wurde vom Spielmodul bei Takt 3404 ausgefuehrt, sein Laufziel blieb (182,146)."""

import json

from selfaware.tools.analysis import befehle_greifen as B


def _zeile(typ, x, y, zustand, lx, ly):
    return [typ, x, y, zustand, 10000, 3, 0, 0, lx, ly]


def test_ein_befehl_der_nicht_greift_und_einer_der_greift(tmp_path):
    konsole = tmp_path / "aufstellung_20261114_203657_konsole.txt"
    konsole.write_text('BEFEHL Tick 3264 angriff {"lauf":[182,146]} an 1 Einheiten: [309]\n'
                       'BEFEHL Tick 3404 angriff {"lauf":[186,154]} an 1 Einheiten: [309]\n'
                       'BEFEHL Tick 3410 angriff {"ziel":321} an 1 Einheiten: [331]\n', encoding="utf-8")
    m = tmp_path / "mitschrift.jsonl"
    zeilen = [{"t": 3000, "start": True, "e": {"309": _zeile(22, 201, 203, 101, 218, 187),
                                                "308": _zeile(22, 210, 190, 101, 186, 154)}},
              {"t": 3265, "e": {"309": _zeile(22, 212, 192, 101, 182, 146)}},     # 1 Takt nach der Ausfuehrung: gegriffen
              {"t": 3402, "e": {"309": _zeile(22, 202, 180, 101, 182, 146)}},
              {"t": 3500, "e": {"309": _zeile(22, 195, 172, 101, 182, 146)}}]     # nach 3404: Laufziel bleibt
    m.write_text("".join(json.dumps(z) + "\n" for z in zeilen), encoding="utf-8")
    aus = B.greifen(B.befehle(str(konsole)), B.stand_lesen(str(m)))
    assert [(z["takt"], z["gegriffen"], z["belegt_von"]) for z in aus] == [(3264, True, None), (3404, False, 308)]
    assert aus[1]["laufziel_vorher"] == [182, 146] and aus[1]["zustand"] == 101


def test_ohne_die_takte_nach_dem_befehl_ist_er_offen_nicht_ungegriffen(tmp_path):
    """Partie 17 (14.11.2026, S143): ausgewertet, waehrend die Mitschrift noch schrieb - Befehle ohne Takte danach waren 'nicht
    gegriffen' und hatten alle gegriffen."""
    konsole = tmp_path / "k.txt"
    konsole.write_text('BEFEHL Tick 3384 angriff {"lauf":[214,178]} an 1 Einheiten: [336]\n'
                       'BEFEHL Tick 3095 angriff {"lauf":[242,202]} an 1 Einheiten: [333]\n', encoding="utf-8")
    m = tmp_path / "m.jsonl"
    m.write_text(json.dumps({"t": 3000, "start": True, "e": {"336": _zeile(24, 190, 160, 101, 194, 162),
                                                               "333": _zeile(24, 269, 183, 101, 302, 150)}}) + "\n"
                 + json.dumps({"t": 3383, "e": {"336": _zeile(24, 190, 160, 101, 194, 162),
                                                "333": _zeile(24, 285, 168, 101, 302, 150)}}) + "\n", encoding="utf-8")
    aus = {z["einheit"]: z for z in B.greifen(B.befehle(str(konsole)), B.stand_lesen(str(m)))}
    assert aus[336]["gegriffen"] is None and "felder_vorher" not in aus[336]   # die Mitschrift endet 1 Takt vor dem Befehl
    assert aus[333]["gegriffen"] is False                                      # 288 Takte danach: wirklich nicht gegriffen


def test_die_gruppe_kommt_aus_der_letzten_partie_im_protokoll(tmp_path):
    log = tmp_path / "ucp3.log"
    log.write_text("x [villagestudio]: ANGRIFF Tick 5000: 1 Einheiten, Gruppe 1200, Art 17, Ziel 186 (uid 154) - Auswahl=true Befehl=true\n"
                   "x [villagestudio]: ANGRIFF Tick 3404: 1 Einheiten, Gruppe 1239, Art 17, Ziel 186 (uid 154) - Auswahl=true Befehl=true\n",
                   encoding="utf-8")
    assert B.gruppen(str(log)) == {(3404, 186, 154): 1239}


def test_bei_einem_befehl_der_nicht_greift_stehen_die_filterfelder_dabei(tmp_path):
    # S139: Mitschriften ab 14.11.2026 21:05 fuehren hinter dem Laufziel geplantes Ziel, Gruppe und die Filterfelder des Marschbefehls
    konsole = tmp_path / "k.txt"
    konsole.write_text('BEFEHL Tick 3404 angriff {"lauf":[186,154]} an 1 Einheiten: [309]\n', encoding="utf-8")

    def voll(lx, ly, sammel):
        return _zeile(22, 202, 180, 101, lx, ly) + [lx, ly, 1239, 1, 0, 0, 0, sammel, 1]

    m = tmp_path / "m.jsonl"
    m.write_text(json.dumps({"t": 3000, "start": True, "e": {"309": voll(182, 146, 1)}}) + "\n"
                 + json.dumps({"t": 3410, "e": {"309": voll(182, 146, 0)}}) + "\n"
                 + json.dumps({"t": 3430, "e": {"309": voll(182, 146, 0)}}) + "\n", encoding="utf-8")   # bis 26 Takte danach (S143)
    z = B.greifen(B.befehle(str(konsole)), B.stand_lesen(str(m)))[0]
    assert not z["gegriffen"] and z["felder_vorher"]["sammelmerker"] == 1 and z["felder_nachher"]["sammelmerker"] == 0
    assert list(z["felder_vorher"]) == ["planx", "plany", "gruppe", "logikzustand", "laufmerker", "sammelgang", "teleport",
                                        "sammelmerker", "beweglich"]


def test_s155_laufbefehle_des_kerns_kommen_aus_seinem_protokoll(tmp_path):
    kern = tmp_path / "samurai_kern.log"
    kern.write_text("haende tick 99000: Gruppe 3, 1 von 1 Einheiten von Spieler 1, Auftrag Auftrag { art: 17, a: 1, b: 2 }, Vorrang 4 - "
                    "abgesetzt, Einheiten [7]\n"
                    "haende tick 977: Gruppe 8, 2 von 2 Einheiten von Spieler 1, Auftrag Auftrag { art: 17, a: 104, b: 211 }, Vorrang 4 - "
                    "abgesetzt, Einheiten [5, 6]\n"
                    "haende tick 980: Gruppe 9, 1 von 1 Einheiten von Spieler 1, Auftrag Auftrag { art: 4, a: 365, b: 0 }, Vorrang 3 - "
                    "abgesetzt, Einheiten [5]\n", encoding="utf-8")
    assert B.kern_befehle(str(kern)) == [(977, (104, 211), [5, 6])]


def test_s156_durchsetzen_auswerten_trennt_kaempfe_und_ketten(tmp_path):
    """S156: tools/analysis/durchsetzen_auswerten.py - je Kampf Beginn und Ende aus dem Kern-Protokoll, Abstand zum Laufziel aus der
    Mitschrift; eine Kette (dieselbe Einheit, dasselbe Laufziel) gilt als erreicht, sobald die Einheit hoechstens NAH Felder davor steht."""
    from selfaware.tools.analysis import durchsetzen_auswerten as D
    kern = tmp_path / "samurai_kern.log"
    kern.write_text("durchsetzen tick 100: Einheit 5 kaempft gegen 40 - Laufauftrag (120,100) ab jetzt jeden Takt neu\n"
                    "durchsetzen tick 101: Einheit 5 kaempft nicht mehr gegen einen anderen - nach 1 Takten, Laufauftrag 1 mal neu\n"
                    "durchsetzen tick 150: Einheit 5 kaempft gegen 41 - Laufauftrag (120,100) ab jetzt jeden Takt neu\n", encoding="utf-8")
    m = tmp_path / "mitschrift.jsonl"
    zeilen = [{"t": 99, "start": True, "e": {"5": _zeile(24, 100, 100, 106, 120, 100)}},
              {"t": 102, "e": {"5": _zeile(24, 101, 100, 101, 120, 100)}},
              {"t": 149, "e": {"5": _zeile(24, 110, 100, 106, 120, 100)}},
              {"t": 200, "e": {"5": _zeile(24, 118, 100, 101, 120, 100)}}]
    m.write_text("".join(json.dumps(z) + "\n" for z in zeilen), encoding="utf-8")
    eps, ketten = D.auswerten(D.episoden(D.ereignisse(str(kern))), B.stand_lesen(str(m)))
    assert [(p["beginn"], p["ende"], p["mal"], p["abstand_beginn"]) for p in eps] == [(100, 101, 1, 20), (150, None, None, 10)]
    assert eps[0]["zustand_danach"] == 101 and eps[0]["abstand_ende"] == 19
    assert len(ketten) == 1 and ketten[0]["kaempfe"] == 2 and ketten[0]["erreicht"] == 200
