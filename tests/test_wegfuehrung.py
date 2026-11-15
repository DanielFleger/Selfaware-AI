"""B-182 Wegfuehrung fuer alle Einheiten (Plan_Wegfuehrung.md), ohne Spiel."""

import pytest

from selfaware.micro import wegfuehrung as W


def _e(besitzer, typ, x, y, leben=10000):
    return {"besitzer": besitzer, "typ": typ, "x": x, "y": y, "leben": leben}


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, _warte, bis=None):
        self.liste.append(b["angriff"])


def _runde(w, L, G=None):
    b = Befehle()
    st = w.schritt(L, G or {}, b)
    return st, b.liste


def test_fernkaempfer_laeuft_bis_in_reichweite_und_greift_dann_an():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    st, b = _runde(w, {1: _e(1, 22, 100, 100), 50: _e(2, 3, 250, 100)})
    assert st[1] == "unterwegs" and "lauf" in b[0] and b[0]["lauf"][0] > 100
    st, b = _runde(
        w, {1: _e(1, 22, 212, 100), 50: _e(2, 3, 250, 100)}
    )  # 38 Felder: Reichweite 40 minus 2
    assert st[1] == "greift_an" and b == [{"einheiten": [1], "ziel": 50}]


def test_neue_gefahr_im_weg_wird_umgangen():
    """Daniel 11.11.: 'er sollte immer adjustieren sollte im lauf eine gefahr in den weg kommen'."""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    L = {1: _e(1, 22, 100, 100), 50: _e(2, 3, 300, 100)}
    _, b1 = _runde(w, L)
    L2 = {
        **L,
        60: _e(2, 22, 150, 100),
        61: _e(2, 22, 150, 104),
    }  # zwei Bogenschuetzen mitten auf dem Weg
    _, b2 = _runde(w, L2)
    assert b2 and b2[0]["lauf"] != b1[0]["lauf"]
    assert W.Gefahr(L2, {}, 1).an(tuple(b2[0]["lauf"]), 22) == 0


def test_ziel_in_gefahr_kein_befehl():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7)
    st, b = _runde(w, {1: _e(1, 71, 100, 100), 60: _e(2, 22, 205, 100)}, {7: _e(2, 3, 200, 100)})
    assert st[1] == "gefahr" and b == []


def test_fernkaempfer_haelt_abstand_zu_kuerzerer_reichweite_nicht_zu_gleicher():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    st, _ = _runde(
        w, {1: _e(1, 22, 100, 100), 50: _e(2, 72, 250, 100)}
    )  # Schleuderer 22: Standplatz 36 ist sicher
    assert st[1] == "unterwegs"
    w2 = W.Wegfuehrung(1)
    w2.fuehre(1, "einheit", 51)
    st, b = _runde(
        w2, {1: _e(1, 22, 100, 100), 51: _e(2, 22, 250, 100)}
    )  # Bogenschuetze 44: jeder Standplatz in seiner Reichweite
    assert st[1] == "gefahr" and b == []


def test_hoechstens_budget_befehle_je_runde_und_keine_wiederholung():
    """Je Einheit ein eigener Weg (10 Felder Abstand): gleiche Befehle wuerden gebuendelt."""
    w = W.Wegfuehrung(1)
    L = {}
    n = W.BUDGET + 4
    for i in range(n):
        L[i + 1] = _e(1, 22, 100, 20 + 10 * i)
        L[100 + i] = _e(2, 3, 300, 20 + 10 * i)
        w.fuehre(i + 1, "einheit", 100 + i)
    _, b1 = _runde(w, L)
    _, b2 = _runde(w, L)
    _, b3 = _runde(w, L)
    assert len(b1) == W.BUDGET and len(b2) == n - W.BUDGET and b3 == []


def test_wiedervergebene_nummer_ist_kein_ziel():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    _runde(w, {1: _e(1, 22, 100, 100), 50: _e(2, 3, 250, 100)})
    st, b = _runde(
        w, {1: _e(1, 22, 100, 100), 50: _e(2, 1, 260, 100)}
    )  # Nummer 50 traegt jetzt einen Bauern
    assert st[1] == "ziel_weg" and b == []


def test_verborgene_fallgrube_ist_keine_gefahr_ein_schuetze_auf_dem_turm_schon():
    """FAIRNESS F12: Holzfallen und Pech des Gegners sind verborgen. Ein Turm schiesst nicht selbst, die Schuetzen darauf schon
    (Plan_Wegfuehrung.md Nachtrag 11.11. 20:45; Daniel 21:32 auf die Frage, erst die Gefahrenrechnung umzubauen: "Ja, erst Gefahr")."""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7)
    st, _ = _runde(w, {1: _e(1, 71, 100, 100)}, {7: _e(2, 3, 200, 100), 8: _e(2, 67, 201, 100)})
    assert st[1] == "unterwegs"
    w2 = W.Wegfuehrung(1)
    w2.fuehre(1, "gebaeude", 7)
    st, _ = _runde(w2, {1: _e(1, 71, 100, 100)}, {7: _e(2, 3, 200, 100), 9: _e(2, 77, 210, 100)})
    assert st[1] == "unterwegs"  # leerer Turm
    w3 = W.Wegfuehrung(1)
    w3.fuehre(1, "gebaeude", 7)
    L3 = {
        1: _e(1, 71, 100, 100),
        60: _e(2, 22, 212, 102),
    }  # Bogenschuetze auf dem Turm (Grundflaeche 6 x 6 ab 210, 100)
    st, _ = _runde(w3, L3, {7: _e(2, 3, 200, 100), 9: _e(2, 77, 210, 100)})
    assert st[1] == "gefahr"


def test_nahkaempfer_darf_an_einen_soldaten_heran():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    st, b = _runde(
        w, {1: _e(1, 75, 100, 100), 50: _e(2, 24, 200, 100)}
    )  # Speertraeger: seine eigene Naehe zaehlt nicht
    assert st[1] == "unterwegs" and "lauf" in b[0]


def test_brandtrupp_gibt_den_weg_ab_und_wechselt_bei_gefahr_das_ziel():
    """Plan_Wegfuehrung.md: der Brandtrupp waehlt das Ziel, die Wegfuehrung den Weg; meldet sie Gefahr, nimmt er ein anderes."""
    from selfaware.micro.tasks import raids as RA

    bt = RA.Brandtrupp(1, lambda nr: 0)
    w = W.Wegfuehrung(1)
    bt.weg = w
    L = {1: _e(1, 71, 100, 100)}
    G = {7: _e(2, 3, 200, 100), 8: _e(2, 3, 100, 200)}
    b = Befehle()
    bt.schritt(L, G, b)
    assert b.liste == [] and w.fuehrt(1)  # der Brandtrupp selbst befiehlt nichts mehr
    erstes = bt.ziel[1]
    st, b = _runde(w, L, G)
    assert st[1] == "unterwegs" and "lauf" in b[0]
    L2 = {
        **L,
        60: _e(2, 22, G[erstes]["x"] + 5, G[erstes]["y"]),
    }  # ein Bogenschuetze stellt sich ans Ziel
    st, _ = _runde(w, L2, G)
    assert st[1] == "gefahr"
    bt.schritt(L2, G, Befehle())
    assert bt.ziel.get(1) not in (None, erstes) and w.fuehrt(1)


def test_brandtrupp_ohne_freies_ziel_wartet_sicher_vorne():
    """Daniel 11.11. 22:41: "schonmal nach vorne geschickt und dann geraided"; Partie 23:10: nach dem Anzuenden fanden beide Sklaven
    kein Ziel mehr und standen."""
    from selfaware.micro.tasks import raids as RA

    bt = RA.Brandtrupp(1, lambda nr: 0)
    w = W.Wegfuehrung(1)
    bt.weg = w
    L = {
        1: _e(1, 71, 100, 100),
        60: _e(2, 22, 200, 60),
    }  # ein Bogenschuetze (44 Felder) deckt das einzige Ziel, freie Linie
    G = {7: _e(2, 3, 200, 100)}
    aus = bt.schritt(L, G, Befehle())
    assert 1 not in bt.ziel and w.fuehrt(1) and any("wartet vorne" in z for z in aus)
    assert (
        bt.warten[1] == (180, 100) and W.Gefahr(L, G, 1).an(bt.warten[1], 71) == 0
    )  # so nah wie sicher moeglich
    assert W.Gefahr(L, G, 1).an((184, 100), 71) == 1  # einen Schritt naeher waere er in Schussweite
    st, b = _runde(w, L, G)
    assert st[1] == "unterwegs" and "lauf" in b[0]
    assert bt.schritt(L, G, Befehle()) == [] and bt.warten[1] == (
        180,
        100,
    )  # der Platz bleibt, solange er sicher ist
    del L[60]  # der Schuetze ist weg: jetzt greift er an
    bt.schritt(L, G, Befehle())
    assert bt.ziel.get(1) == 7 and 1 not in bt.warten


def test_reiterjagd_fuehrt_ueber_die_wegfuehrung_und_zaehlt_nur_echte_abschuesse():
    """S110: Die Reiterjagd zaehlte jeden toten Arbeiter als eigenen Abschuss. Jetzt nur, wenn ihr Reiter ihn in Reichweite angriff."""
    from selfaware.micro.tasks import raids as RA

    rj = RA.Reiterjagd(1)
    w = W.Wegfuehrung(1)
    rj.weg = w
    b = Befehle()
    rj.schritt({1: _e(1, 74, 100, 100), 50: _e(2, 3, 250, 100)}, {}, b)
    assert b.liste == [] and w.fuehrt(1)  # kein eigener Angriffsbefehl auf das ferne Ziel
    _runde(w, {1: _e(1, 74, 100, 100), 50: _e(2, 3, 250, 100)})
    aus = rj.schritt({1: _e(1, 74, 100, 100)}, {}, Befehle())  # Arbeiter 50 stirbt woanders
    assert rj.getoetet == 0 and any("kein eigener Abschuss" in z for z in aus)
    rj2 = RA.Reiterjagd(1)
    w2 = W.Wegfuehrung(1)
    rj2.weg = w2
    rj2.schritt({1: _e(1, 74, 215, 100), 50: _e(2, 3, 250, 100)}, {}, Befehle())
    st, b = _runde(w2, {1: _e(1, 74, 215, 100), 50: _e(2, 3, 250, 100)})  # 35 Felder: in Reichweite
    assert st[1] == "greift_an" and b == [{"einheiten": [1], "ziel": 50}]
    rj2.schritt({1: _e(1, 74, 215, 100)}, {}, Befehle())
    assert rj2.getoetet == 1


def test_reiterjagd_zaehlt_nur_einen_frischen_angriff_als_abschuss():
    """Partie 12.11. 00:05 (Fehlerwache F4): Reiter 503 griff Arbeiter 344 an, ritt weiter, und 1.303 Takte spaeter verschwand 344 -
    die Reiterjagd meldete den Abschuss, weil sie sich den Angriff bis zum Zielwechsel merkte."""
    from selfaware.micro.tasks import raids as RA

    rj = RA.Reiterjagd(1)
    w = W.Wegfuehrung(1)
    rj.weg = w
    L = {1: _e(1, 74, 215, 100), 50: _e(2, 3, 250, 100)}
    rj.schritt(L, {}, Befehle())
    st, _b = _runde(w, L)
    assert st[1] == "greift_an"
    rj.schritt(L, {}, Befehle())  # merkt sich den Angriff
    weit = {
        1: _e(1, 74, 100, 100),
        50: _e(2, 3, 250, 100),
    }  # das Opfer ist entwischt, der Reiter jagt es von weit her
    for _ in range(RA.ABSCHUSS_RUNDEN + 1):
        _runde(w, weit)
        rj.schritt(weit, {}, Befehle())
    aus = rj.schritt({1: _e(1, 74, 100, 100)}, {}, Befehle())  # jetzt verschwindet es
    assert rj.getoetet == 0 and any("kein eigener Abschuss" in z for z in aus)


def test_vorstoss_gibt_schuetzen_an_die_wegfuehrung_und_holt_sie_zum_vorruecken_zurueck():
    from selfaware.micro.tasks import vorstoss as V

    v = V.Vorstoss(1, (100, 100))
    w = W.Wegfuehrung(1)
    v.weg = w
    b = Befehle()
    v.schritt(500, {1: _e(1, 22, 100, 100), 2: _e(1, 22, 100, 101), 3: _e(2, 3, 130, 110)}, {}, b)
    assert (
        b.liste == [] and w.fuehrt(1) and w.fuehrt(2)
    )  # kein eigener Schussbefehl, die Wegfuehrung fuehrt beide
    b = Befehle()
    v.schritt(
        600, {1: _e(1, 22, 100, 100), 2: _e(1, 22, 100, 101), 4: _e(2, 3, 260, 100)}, {}, b
    )  # Ziel weg: vorruecken
    assert (
        b.liste == [] and w.auftraege[1].art == "ort" and w.auftraege[2].art == "ort"
    )  # Vorruecken fuehrt die Wegfuehrung


class _WegAttrappe:
    """Steht fuer die Wegfuehrung, wenn ein Test nur prueft, wie ein Modul auf ihren Status antwortet."""

    def __init__(self):
        self.auftraege, self.st = {}, {}

    def fuehre(self, nr, art, ziel, zweck=""):
        self.auftraege[nr] = (art, ziel)

    def loslassen(self, nr):
        self.auftraege.pop(nr, None)

    def fuehrt(self, nr):
        return nr in self.auftraege

    def status(self, nr):
        return self.st.get(nr) if nr in self.auftraege else None

    def schuss_moeglich(self, typ, von, ziel_ort, L, G, zweck=""):
        return True  # hier zaehlt nur die Antwort auf den Status: jedes Ziel gilt als sicher zu beschiessen


def test_gleiche_befehle_gehen_als_einer_hinaus():
    """Wie der Vorstoss bisher: ein Befehl fuer alle Schuetzen auf dasselbe Ziel, nicht einer je Schuetze (Budget S82)."""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    w.fuehre(2, "einheit", 50)
    st, b = _runde(
        w, {1: _e(1, 22, 212, 100), 2: _e(1, 22, 213, 103), 50: _e(2, 3, 250, 100)}
    )  # Luftlinie 38 und 37,1
    assert st == {1: "greift_an", 2: "greift_an"} and b == [{"einheiten": [1, 2], "ziel": 50}]


def test_wiedervergebene_nummer_wird_neu_gefuehrt_wenn_das_modul_sie_will():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    _runde(w, {1: _e(1, 22, 100, 100), 50: _e(2, 3, 250, 100)})
    L = {1: _e(1, 22, 100, 100), 50: _e(2, 1, 260, 100)}
    st, _ = _runde(w, L)
    assert st[1] == "ziel_weg"
    w.fuehre(1, "einheit", 50)
    st, _ = _runde(w, L)
    assert st[1] == "unterwegs"  # derselbe Wegpunkt wie zuvor: kein neuer Befehl noetig


def test_reiter_gibt_bei_gefahr_ab_und_nimmt_einen_anderen_die_sperre_gilt_nur_fuer_ihn():
    from selfaware.micro.tasks import raids as RA

    rj = RA.Reiterjagd(1)
    w = _WegAttrappe()
    rj.weg = w
    L = {
        1: _e(1, 74, 100, 100),
        2: _e(1, 74, 150, 60),
        50: _e(2, 3, 150, 100),
        51: _e(2, 3, 100, 180),
    }
    rj.schritt(L, {}, Befehle())
    assert w.auftraege == {1: ("einheit", 50), 2: ("einheit", 50)}
    w.st[1] = "gefahr"
    aus = rj.schritt(L, {}, Befehle())
    assert w.auftraege[1] == ("einheit", 51) and w.auftraege[2] == ("einheit", 50)
    assert any("Reiter 1 gibt Arbeiter 50 auf (gefahr)" in z for z in aus)
    w.st[1] = "unterwegs"
    for _ in range(RA.SPERRE_RUNDEN - 1):
        rj.schritt(L, {}, Befehle())
        assert w.auftraege[1] == ("einheit", 51)


def test_reiterjagd_wiedervergebene_nummer_ist_abschuss_nach_schuss_und_neues_ziel():
    from selfaware.micro.tasks import raids as RA

    rj = RA.Reiterjagd(1)
    w = W.Wegfuehrung(1)
    rj.weg = w
    L = {1: _e(1, 74, 215, 100), 50: _e(2, 3, 250, 100)}
    rj.schritt(L, {}, Befehle())
    st, _ = _runde(w, L)
    assert st[1] == "greift_an"
    rj.schritt(L, {}, Befehle())  # liest "greift_an"
    L2 = {
        1: _e(1, 74, 215, 100),
        50: _e(2, 13, 250, 100),
    }  # Nummer 50 traegt jetzt einen anderen Arbeiter
    st, _ = _runde(w, L2)
    assert st[1] == "ziel_weg"
    aus = rj.schritt(L2, {}, Befehle())
    assert rj.getoetet == 1 and any("hat Arbeiter 50 erledigt" in z for z in aus)
    st, b = _runde(
        w, L2
    )  # der neue Arbeiter unter Nummer 50 wird gejagt, nicht als "ziel_weg" stehen gelassen
    assert st[1] == "greift_an" and b == [{"einheiten": [1], "ziel": 50}]


def test_vorstoss_holt_nachzuegler_zur_gruppe_wenn_er_nicht_vorruecken_kann():
    """Partie 11.11. 23:40 (Fehlerwache F3): A_ARCHER 70 Nr. 422 stand 2.000 Takte zu Hause, 53 Felder hinter seiner Gruppe."""
    from selfaware.micro.tasks import vorstoss as VS

    v = VS.Vorstoss(1, (149, 274), bis=40000)
    w = W.Wegfuehrung(1)
    v.weg = w
    L = {n: _e(1, 22, 199 + n % 3, 185) for n in range(1, 7)}
    L[7] = _e(1, 70, 185, 238)  # der Nachzuegler
    L[50] = _e(
        2, 3, 201, 60
    )  # ein Arbeiter weit vorn - jede Stellung davor liegt im Schussfeld des Turms
    G = {90: _e(2, 74, 201, 133)}  # feindlicher Turm, 48 Felder vor der Gruppe
    aus = v.schritt(1000, L, G, Befehle())
    assert w.fuehrt(7) and w.auftraege[7].art == "ort" and not any(w.fuehrt(n) for n in range(1, 7))
    assert any("Nachzuegler" in z for z in aus)
    treff = w.auftraege[7].ziel
    assert (
        max(abs(treff[0] - 200), abs(treff[1] - 185)) <= 2
    )  # zu den sechs vorn, nicht in die Mitte zwischen allen
    assert (
        v.schritt(1001, L, G, Befehle()) == [] and w.auftraege[7].ziel == treff
    )  # kein neuer Treffpunkt je Runde
    for n in range(1, 7):
        L[n] = _e(1, 22, L[n]["x"], 182)  # die Gruppe rueckt 3 Felder: der Treffpunkt bleibt
    v.schritt(1002, L, G, Befehle())
    assert w.auftraege[7].ziel == treff
    for n in range(1, 7):
        L[n] = _e(
            1, 22, L[n]["x"], 195
        )  # 10 Felder zurueck (ausser Reichweite des Turms): neuer Treffpunkt
    v.schritt(1003, L, G, Befehle())
    assert w.auftraege[7].ziel != treff and w.auftraege[7].ziel[1] == 195


def test_vorstoss_flieht_nicht_vor_schleuderern_und_beschiesst_sie_von_weitem():
    """Partie 11.11. 23:49 (Fehlerwache F2): 14 Schleuderer lagerten 45 Felder vor der Burg; der Vorstoss zog sich achtmal zurueck
    und schoss nie - fuer ihn traf jeder feindliche Fernkaempfer 44 Felder weit, Schleuderer treffen 22."""
    from selfaware.micro.tasks import vorstoss as VS

    v = VS.Vorstoss(1, (100, 300), bis=40000)
    w = W.Wegfuehrung(1)
    v.weg = w
    L = {n: _e(1, 22, 100 + n, 100) for n in range(1, 5)}
    schleuder = {
        50 + i: _e(2, 72, 140, 98 + 2 * i) for i in range(5)
    }  # 35-40 Felder vor der Gruppe
    assert (
        v._schussfeld((102, 100), {**L, **schleuder}, {}, 4) is None
    )  # Schleuderer treffen nur 22 Felder weit
    bogen = {50 + i: _e(2, 22, 140, 98 + 2 * i) for i in range(5)}
    assert (
        v._schussfeld((102, 100), {**L, **bogen}, {}, 4) is not None
    )  # Bogenschuetzen (44) bleiben eine Gefahr
    weit = {
        50 + i: _e(2, 72, 150, 98 + 2 * i) for i in range(5)
    }  # 48 Felder: ausser unserer Schussweite (38)
    aus = v.schritt(1000, {**L, **weit}, {}, Befehle())
    assert any("schiessen auf Typ 72" in z for z in aus) and all(
        w.fuehrt(n) and w.auftraege[n].art == "einheit" for n in L
    )
    st, b = _runde(w, {**L, **weit}, {})
    assert (
        all(st[n] == "unterwegs" for n in L) and b
    )  # die Wegfuehrung stellt sie in eigener, nicht in ihrer Reichweite auf
    weit_bogen = {50 + i: _e(2, 22, 150, 98 + 2 * i) for i in range(5)}
    v2 = VS.Vorstoss(1, (100, 300), bis=40000)
    v2.weg = W.Wegfuehrung(1)
    assert not any(
        "schiessen" in z for z in v2.schritt(1000, {**L, **weit_bogen}, {}, Befehle())
    )  # Bogen ueberreichen wir nicht


def test_vorstoss_ueberspringt_gedeckte_ziele_und_zieht_zu_einem_sicheren():
    """Partie 11.11. 23:53 (Fehlerwache F2): jedes Ziel in 38 Feldern war gedeckt, der Vorstoss probierte sie der Reihe nach und gab sie
    auf, waehrend die Wegfuehrung fuer fast alle anderen feindlichen Einheiten einen sicheren Standplatz fand."""
    from selfaware.micro.tasks import vorstoss as VS

    L = {n: _e(1, 22, 100 + n, 100) for n in range(1, 5)}
    L[50] = _e(
        2, 3, 130, 100
    )  # Arbeiter in 30 Feldern, gedeckt von einem Armbrustschuetzen daneben
    # Daniel 15.11.2026 23:28: gedeckt heisst jetzt - die Gefechtsrechnung erwartet keinen Sieg (4 Bogen gegen 2 Armbrueste: kein
    # Sieg, gemessen mit Vorstoss._gewinnt; 2 sind noch keine Ueberzahl fuer den Rueckzug). Gegen EINEN griffe der Vorstoss jetzt an.
    L[60] = _e(2, 23, 133, 100)
    L[61] = _e(2, 23, 133, 101)
    L[51] = _e(2, 3, 200, 100)  # Arbeiter in 100 Feldern, ungedeckt
    v = VS.Vorstoss(1, (100, 300), bis=40000)
    w = W.Wegfuehrung(1)
    v.weg = w
    aus = v.schritt(1000, L, {}, Befehle())
    assert all(w.auftraege[n].ziel == 51 for n in range(1, 5)) and any(
        "ziehen zu Typ 3" in z for z in aus
    )
    L[52] = _e(2, 3, 100, 130)  # ein ungedeckter Arbeiter in 30 Feldern: der nahe geht vor
    v2 = VS.Vorstoss(1, (100, 300), bis=40000)
    w2 = W.Wegfuehrung(1)
    v2.weg = w2
    aus = v2.schritt(1000, L, {}, Befehle())
    assert all(w2.auftraege[n].ziel == 52 for n in range(1, 5)) and any(
        "schiessen auf Typ 3" in z for z in aus
    )


def test_vorstoss_greift_einen_schuetzen_an_wenn_er_gewinnt():
    """Daniel 15.11.2026 23:28: "auch bogenschuetzen von uns gegen ihre - wenn wir gegen sie gewinnen koennen dann lieber engagen ...
    natuerlich nur bei erwartetem gewinn". 4 eigene Bogenschuetzen gegen EINEN Armbrustschuetzen in 33 Feldern: Sieg erwartet - er ist das
    Ziel, statt zum fernen ungedeckten Arbeiter zu ziehen."""
    from selfaware.micro.tasks import vorstoss as VS

    L = {n: _e(1, 22, 100 + n, 100) for n in range(1, 5)}
    L[50] = _e(2, 3, 130, 100)
    L[60] = _e(2, 23, 133, 100)
    L[51] = _e(2, 3, 200, 100)
    v = VS.Vorstoss(1, (100, 300), bis=40000)
    w = W.Wegfuehrung(1)
    v.weg = w
    aus = v.schritt(1000, L, {}, Befehle())
    assert v._gewinnt((102, 100), L)
    assert all(w.auftraege[n].ziel in (50, 60) for n in range(1, 5)), aus


def test_sicherer_standplatz_haengt_nicht_davon_ab_woher_man_fragt():
    """Partie 11.11. 23:53: aus der Gruppenmitte sah die Frage einen sicheren Punkt, den kein Schuetze von seinem Platz aus pruefte - der
    Vorstoss waehlte das Ziel, die Wegfuehrung meldete fuer alle "gefahr"."""
    w = W.Wegfuehrung(1)
    schuetzen = [
        (244, 196),
        (196, 244),
        (158, 214),
        (214, 157),
        (168, 168),
        (232, 232),
        (160, 190),
        (230, 172),
    ]
    antworten = []
    for k in range(1, len(schuetzen) + 1):
        L = {50: _e(2, 3, 200, 200), **{60 + i: _e(2, 23, *s) for i, s in enumerate(schuetzen[:k])}}
        seiten = {
            w.schuss_moeglich(70, von, (200, 200), L, {})
            for von in ((100, 100), (300, 110), (210, 320), (80, 260), (320, 250))
        }
        assert len(seiten) == 1, (k, seiten)
        antworten.append(seiten.pop())
    assert (
        antworten[0] and not antworten[-1]
    )  # ein Armbrustschuetze laesst Platz, acht rundum keinen
    # fuenf Armbrustschuetzen in 60 Feldern (62, 120, 180, 240, 298 Grad) lassen nur einen schmalen Streifen im Osten frei - die
    # alte, nach der fragenden Einheit gedrehte Pruefung sah ihn aus 0 Grad und nicht aus 11, 20 oder 260 Grad
    ring = [(228, 253), (170, 252), (140, 200), (170, 148), (228, 147)]
    L = {50: _e(2, 3, 200, 200), **{60 + i: _e(2, 23, *s) for i, s in enumerate(ring)}}
    seiten = {
        w.schuss_moeglich(70, von, (200, 200), L, {})
        for von in ((350, 200), (347, 229), (341, 251), (174, 52))
    }
    assert seiten == {True}


def test_standplatz_liegt_begehbar_und_in_schussweite():
    """Ein gesperrter Ring um das Ziel: im Osten rueckt jeder Punkt des Kreises (36 Felder) nach aussen auf 39 Felder - ausser
    Schussweite (38), im Westen nach innen auf 34. Gewaehlt wird ein begehbarer Punkt in Schussweite, nicht der naechste zur Einheit."""
    import math

    def zu(x, y):
        d = math.hypot(x - 200, y - 200)
        return (31 <= d <= 38.9) if x >= 200 else (35 <= d <= 41)

    karte = ["".join("#" if zu(x, y) else "." for x in range(400)) for y in range(400)]
    w = W.Wegfuehrung(1, karte)
    stand, gefahr = w._standplatz((400, 200), (200, 200), 40, lambda p: 0)
    assert (
        karte[stand[1]][stand[0]] == "."
        and math.hypot(stand[0] - 200, stand[1] - 200) <= 40 - W.FERN_ANGRIFF
    )
    assert stand[0] < 200 and gefahr == 0  # im Osten gaebe es nur Punkte ausser Schussweite


def test_vorstoss_laesst_bei_alarm_und_am_ende_los():
    from selfaware.micro.tasks import vorstoss as V

    L = {1: _e(1, 22, 300, 300), 2: _e(1, 22, 300, 301), 3: _e(2, 3, 330, 310)}
    v = V.Vorstoss(1, (100, 100))
    w = W.Wegfuehrung(1)
    v.weg = w
    v.schritt(500, L, {}, Befehle())
    assert w.fuehrt(1) and w.fuehrt(2)
    alarm = {**L, 60: _e(2, 71, 100, 100), 61: _e(2, 71, 101, 100), 62: _e(2, 71, 102, 100)}
    aus = v.schritt(600, alarm, {}, Befehle())
    assert any("Abwehr" in z for z in aus) and not w.fuehrt(1) and not w.fuehrt(2)
    v2 = V.Vorstoss(1, (100, 100), bis=1000)
    w2 = W.Wegfuehrung(1)
    v2.weg = w2
    v2.schritt(500, L, {}, Befehle())
    assert w2.fuehrt(1)
    v2.schritt(1000, L, {}, Befehle())
    assert not w2.fuehrt(1) and not w2.fuehrt(2)


def test_vorstoss_rueckt_nach_dem_schiessen_sofort_wieder_vor():
    """Nach dem Schuss fuehrt die Wegfuehrung die Schuetzen gleich wieder zur Stelle des Vorrueckens."""
    from selfaware.micro.tasks import vorstoss as V

    v = V.Vorstoss(1, (100, 100))
    w = W.Wegfuehrung(1)
    v.weg = w
    fern = {1: _e(1, 22, 100, 100), 2: _e(1, 22, 100, 101), 4: _e(2, 3, 260, 100)}
    b1 = Befehle()
    v.schritt(500, fern, {}, b1)
    assert b1.liste == [] and w.auftraege[1].art == "ort"
    stelle = tuple(w.auftraege[1].ziel)
    v.schritt(510, {**fern, 3: _e(2, 3, 130, 110)}, {}, Befehle())
    assert w.auftraege[1].art == "einheit"
    v.schritt(520, fern, {}, Befehle())
    assert w.auftraege[1].art == "ort" and tuple(w.auftraege[1].ziel) == stelle


def test_vorstoss_gibt_ein_ziel_ohne_angriff_und_weg_auf():
    from selfaware.micro.tasks import vorstoss as V

    v = V.Vorstoss(1, (100, 100))
    w = _WegAttrappe()
    v.weg = w
    L = {
        1: _e(1, 22, 100, 100),
        2: _e(1, 22, 100, 101),
        3: _e(2, 3, 130, 110),
        5: _e(2, 3, 128, 80),
    }
    v.schritt(500, L, {}, Befehle())
    erstes = w.auftraege[1][1]
    w.st = {1: "gefahr", 2: "kein_weg"}
    aus = v.schritt(510, L, {}, Befehle())
    assert any("gibt Ziel %d auf" % erstes in z for z in aus)
    assert w.auftraege[1][1] != erstes and w.auftraege[2][1] != erstes


def test_gebaeude_zwischen_schuetze_und_ort_sperrt_die_linie():
    """L79, der tote Winkel hinter Gebaeuden (Daniel 11.11. 20:30: "toter winkel hat JEDE einheit")."""
    L = {60: _e(2, 22, 200, 100)}
    assert W.Gefahr(L, {}, 1).an((170, 100), 22) == 1
    assert (
        W.Gefahr(L, {5: _e(2, 3, 185, 99)}, 1).an((170, 100), 22) == 0
    )  # Holzfaellerhuette (3 x 3) auf der Linie
    assert (
        W.Gefahr(L, {5: _e(2, 32, 181, 95)}, 1).an((170, 100), 22) == 1
    )  # flaches Feld sperrt nicht
    assert (
        W.Gefahr(L, {5: _e(2, 67, 185, 100)}, 1).an((170, 100), 22) == 1
    )  # Fallgrube: flach und verborgen (F12)


def test_schuetze_auf_dem_turm_schiesst_ueber_gebaeude():
    L = {60: _e(2, 22, 201, 101)}  # steht auf dem Turm (Typ 77, 6 x 6 ab 200, 100)
    assert W.Gefahr(L, {9: _e(2, 77, 200, 100), 5: _e(2, 3, 185, 99)}, 1).an((170, 100), 22) == 1


def test_assassine_ausser_sicht_ist_nicht_in_gefahr():
    """L75: Schuetzen nehmen eine Assassine nur, wenn sie hoechstens ~20 Felder (160 Feinmass, mit Planungsrand 208) von einem
    waehlbaren Feind steht."""
    b = W.Gefahr({60: _e(2, 22, 200, 100)}, {}, 1)
    assert (
        b.an((165, 100), 22) == 1 and b.an((165, 100), W.ASSASSINE) == 0
    )  # 35 Felder: in Reichweite, aber ungesehen
    assert b.an((182, 100), W.ASSASSINE) == 1  # 18 Felder: sichtbar


def test_fernkaempfer_findet_den_standplatz_hinter_einem_gebaeude():
    """Gegen einen Bogenschuetzen am Ziel liegt jeder Standplatz in 36 Feldern in seiner Reichweite - ausser hinter einem Gebaeude."""
    L = {1: _e(1, 22, 100, 100), 50: _e(2, 3, 250, 100), 60: _e(2, 22, 251, 100)}
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    st, _ = _runde(w, L)
    assert st[1] == "gefahr"
    w2 = W.Wegfuehrung(1)
    w2.fuehre(1, "einheit", 50)
    st, b = _runde(
        w2, L, {5: _e(2, 8, 222, 98)}
    )  # Haus (5 x 5) zwischen Standplatz (214, 100) und Bogenschuetze
    assert st[1] == "unterwegs" and "lauf" in b[0]


def test_wegegitter_rechnet_mit_derselben_regel():
    g = W.Gefahr({60: _e(2, 22, 200, 100)}, {5: _e(2, 8, 182, 98)}, 1).gitter(None)
    assert g.schaden_je_tick(g.zelle_von((170, 100))) == 0  # Linie durch das Haus
    assert g.schaden_je_tick(g.zelle_von((170, 120))) == 1  # 37 Felder, freie Linie


def _waechter_lage():
    """Angelehnt an tools/checks/waechter_pruefen.py, Fall 1 - statt drei Assassinen (dort verzichtet die Abwehr nach der
    Gefechtsrechnung) ein feindlicher Sklave an unserem Gebaeude: zwei Waechter greifen an, drei Schuetzen weichen."""

    def e(typ, sp, x, y, **k):
        d = {
            "typ": typ,
            "besitzer": sp,
            "x": x,
            "y": y,
            "leben": 10000,
            "zustand": 1,
            "laufx": x,
            "laufy": y,
            "nahziel": 0,
            "nahangreifer": 0,
            "zieleinheit": 0,
        }
        d.update(k)
        return d

    L = {
        45: e(70, 1, 139, 168, zustand=106, nahziel=156),
        189: e(70, 1, 140, 168, nahangreifer=1),
        60: e(24, 1, 155, 158),
        61: e(24, 1, 156, 158),
        62: e(75, 1, 156, 159),
        156: e(71, 2, 148, 163),
    }
    return L, [(150, 160), (145, 215), (150, 200)]


def test_waechter_gibt_den_angriff_an_die_wegfuehrung(monkeypatch):
    """Daniel 11.11. 21:48 auf die Frage "Sollen die Waechter ueber die Wegfuehrung laufen und unter Beschuss angreifen duerfen?":
    "Ja, freigeben"."""
    try:
        import selfaware.micro.tasks.waechter as WA
    except (
        RuntimeError
    ) as ex:  # ohne Spiel-Instanz (SHC_INSTANZ=99) laesst sich der Waechter nicht laden
        pytest.skip(str(ex))

    gesendet = []
    monkeypatch.setattr(WA, "befehl", lambda b, *a, **k: gesendet.append(b) or [])
    L, gebaeude = _waechter_lage()
    alt = WA.Waechter(1)
    alt.besetzt = True
    alt.schritt(L, gebaeude)
    assert any(
        b.get("angriff", {}).get("ziel") == 156 for b in gesendet
    )  # ohne Wegfuehrung wie bisher
    gesendet.clear()
    w = WA.Waechter(1)
    w.besetzt = True
    w.weg = W.Wegfuehrung(1, trotz_gefahr=("waechter",))
    w.schritt(L, gebaeude)
    angreifer = [n for n, z in w.auftrag.items() if z == 156]
    assert w.ziel == 156 and angreifer and not any("ziel" in b.get("angriff", {}) for b in gesendet)
    assert all(w.weg.fuehrt(n) and w.gefuehrt[n] == "einheit" for n in angreifer)
    st = w.weg.schritt(L, {}, lambda *a, **k: None)
    assert all(
        st[n] in ("unterwegs", "greift_an") for n in angreifer
    )  # mit Freigabe auch unter Beschuss
    ruhig = {n: e for n, e in L.items() if e["besitzer"] == 1}
    w.schritt(ruhig, gebaeude)
    assert not any(
        w.gefuehrt.get(n) == "einheit" for n in angreifer
    )  # ohne Bedrohung endet der Angriff
    assert not w.gefuehrt  # 13.11.2026 23:02: kein Stapeln mehr - ohne Bedrohung fuehrt die Wegfuehrung niemanden fuer den Waechter


def test_ohne_bedrohung_schickt_der_waechter_die_nahkaempfer_nirgends_hin(monkeypatch):
    """Daniel 13.11.2026 23:02: das Stapeln der Nahkaempfer auf das Feld der Fernkaempfer "ueberall entfernen ... Das ist nie eine
    regel gewesen". Lage aus Partie 20261113_220614 (Takt 2611): die Bogenschuetzen fuehrt der Vorstoss, 330-332/336 graben,
    333-335 stehen bei (151,281) - der Waechter gibt ohne Bedrohung keinen Laufbefehl."""
    try:
        import selfaware.micro.tasks.waechter as WA
    except (
        RuntimeError
    ) as ex:  # ohne Spiel-Instanz (SHC_INSTANZ=99) laesst sich der Waechter nicht laden
        pytest.skip(str(ex))

    def e(typ, x, y, **k):
        d = {
            "typ": typ,
            "besitzer": 1,
            "x": x,
            "y": y,
            "leben": 10000,
            "zustand": 1,
            "laufx": x,
            "laufy": y,
            "nahziel": 0,
            "nahangreifer": 0,
            "zieleinheit": 0,
        }
        d.update(k)
        return d

    L = {
        308: e(22, 205, 185, zustand=101),
        309: e(22, 205, 185, zustand=101),
        310: e(22, 207, 183, zustand=101),
        311: e(22, 206, 186, zustand=101),
        312: e(22, 207, 185, zustand=101),
        330: e(24, 192, 236, zustand=124),
        331: e(24, 186, 238, zustand=124),
        332: e(24, 191, 233, zustand=124),
        336: e(24, 192, 235, zustand=124),
        333: e(24, 152, 281),
        334: e(24, 149, 280),
        335: e(24, 151, 282),
    }
    gesendet = []
    monkeypatch.setattr(WA, "befehl", lambda b, *a, **k: gesendet.append(b) or [])
    for eigene_schuetzen in ((), (308, 309, 310, 311, 312)):  # mit und ohne Schuetzen beim Waechter
        w = WA.Waechter(1)
        w.besetzt = True
        w.schritt(
            L,
            [(188, 236)],
            ausgenommen={330, 331, 332, 336} | ({308, 309, 310, 311, 312} - set(eigene_schuetzen)),
        )
        assert not any("lauf" in b.get("angriff", {}) for b in gesendet)
        assert all(w.absicht[n][2] == "no_threat_stays" for n in (333, 334, 335))


def test_der_posten_befehl_der_ersten_runde_laesst_die_schuetzen_des_vorstosses_aus(monkeypatch):
    """13.11.2026 Partie 6: "Stellung: 12 Truppen zum Posten (147, 235)" - auch die 5 Bogenschuetzen, die der Vorstoss im selben
    Takt (674) aufnahm; vorstoss.mitglieder war vor seiner ersten Runde leer. anspruch() nennt sie schon vorher."""
    try:
        import selfaware.micro.tasks.waechter as WA
    except (
        RuntimeError
    ) as ex:  # ohne Spiel-Instanz (SHC_INSTANZ=99) laesst sich der Waechter nicht laden
        pytest.skip(str(ex))
    from selfaware.micro.tasks import vorstoss as V

    def e(typ, x, y):
        return {
            "typ": typ,
            "besitzer": 1,
            "x": x,
            "y": y,
            "leben": 10000,
            "zustand": 1,
            "laufx": x,
            "laufy": y,
            "nahziel": 0,
            "nahangreifer": 0,
            "zieleinheit": 0,
        }

    L = {n: e(22, 151, 280) for n in range(308, 313)}
    L.update({n: e(24, 144, 281) for n in range(330, 337)})
    v = V.Vorstoss(1, (230, 287), bis=40000)
    assert v.mitglieder == set() and v.anspruch(672, L) == set(range(308, 313))
    assert v.anspruch(40000, L) == set()  # nach dem Vorstoss gehoeren sie wieder dem Waechter
    gesendet = []
    monkeypatch.setattr(WA, "befehl", lambda b, *a, **k: gesendet.append(b) or [])
    w = WA.Waechter(1, posten=(147, 235))
    w.schritt(L, [(188, 236)], ausgenommen=v.anspruch(672, L))
    halten = [b["halten"] for b in gesendet if "halten" in b]
    assert halten and set(halten[0]["nr"]) == set(range(330, 337))


def test_vorstoss_wartet_wenn_die_wegfuehrung_die_stelle_nicht_sicher_findet():
    from selfaware.micro.tasks import raids as RA
    from selfaware.micro.tasks import vorstoss as V

    v = V.Vorstoss(1, (100, 100))
    w = _WegAttrappe()
    v.weg = w
    fern = {1: _e(1, 22, 100, 100), 2: _e(1, 22, 100, 101), 4: _e(2, 3, 260, 100)}
    v.schritt(500, fern, {}, Befehle())
    assert w.auftraege[1][0] == "ort"
    w.st = {1: "gefahr", 2: "kein_weg"}
    aus = v.schritt(510, fern, {}, Befehle())
    assert any("Vorruecken nicht sicher" in z for z in aus) and not w.auftraege
    for i in range(RA.SPERRE_RUNDEN - 1):
        v.schritt(520 + i, fern, {}, Befehle())
        assert not w.auftraege


def test_brandtrupp_waehlt_nur_gebaeude_die_die_wegfuehrung_annimmt():
    """Partie 11.11. 22:05 (Fehlerwache F3): der Brandtrupp hielt ein Gebaeude mit einem Bogenschuetzen in 20 bis 44 Feldern fuer
    sicher (alte Regel bis 20), die Wegfuehrung lehnte es ab - die Sklaven pendelten zwischen gesperrten Zielen und standen zu Hause."""
    from selfaware.micro.tasks import raids as RA

    L = {1: _e(1, 71, 100, 100), 60: _e(2, 22, 230, 100)}  # Bogenschuetze 30 Felder vor Gebaeude 7
    G = {7: _e(2, 3, 200, 100), 8: _e(2, 3, 100, 200)}
    ohne = RA.Brandtrupp(1, lambda nr: 0)
    assert ohne.moeglich(7, L, G)  # alte Regel allein: sicher
    bt = RA.Brandtrupp(1, lambda nr: 0)
    w = W.Wegfuehrung(1)
    bt.weg = w
    assert not bt.moeglich(7, L, G) and bt.moeglich(8, L, G)
    bt.schritt(L, G, Befehle())
    assert bt.ziel[1] == 8
    st, _ = _runde(w, L, G)
    assert st[1] == "unterwegs"


def test_steckt_eine_einheit_fest_gilt_der_wegpunkt_als_nicht_erreichbar():
    """Partie 11.11. 22:10 (Fehlerwache F3): derselbe Wegpunkt 2.000 Takte lang, der Sklave ruehrte sich nicht."""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7)
    L, G = {1: _e(1, 71, 100, 100)}, {7: _e(2, 3, 260, 100)}
    _, b = _runde(w, L, G)
    assert "lauf" in b[0]  # zuerst der sichere Weg ueber Wegpunkte
    for _ in range(W.STECKT_RUNDEN):
        st, _b = _runde(w, L, G)  # die Einheit bleibt, wo sie ist
    assert st[1] == "steckt" and all(
        all(z) for z in w._frei
    )  # keine Zelle gesperrt (22:34: das mauerte Wege zu)
    st, b = _runde(w, L, G)
    assert st[1] == "direkt" and b == [
        {"einheiten": [1], "gebaeude": 7}
    ]  # die Wegsuche des Spiels uebernimmt


# --- B-182 (Partie 11.11. 22:37, Daniel 22:41: "warum wird denn der soeldnerposten als unbegehbar gegolten? macht doch keinen
# sinn offensichtlich sammeln die sich dort ja") - Begehbarkeit aus der Weg-Ebene des Spiels, Wegsuche des Spiels nur kurz


def _weg_ebene(gesperrt=(), felder=None):
    """Weg-Ebene wie services/wegkarte.lesen: ueberall Schritte erlaubt, ausser auf gesperrt; felder ueberschreibt einzelne."""
    f = {(x, y): (0xFF, 0, 1, 0, 0, 0) for y in range(400) for x in range(400)}
    for p in gesperrt:
        f[p] = (0, 9, 0, 0x400, 0, 1)
    f.update(felder or {})
    return {"tick": 1, "f": f}


def _soeldnerposten():
    """Wie gemessen 11.11. 22:46 auf Instanz 2: Teil 41 (Typ 8) bei (153..157, 284..288) ohne Schritte, die drei Hof-Teile
    (Typ 57/58/56) mit Schritten - der Sklave stand bei (158, 288)."""
    felder = {}
    for y in range(284, 294):
        for x in range(153, 163):
            haupt = x <= 157 and y <= 288
            felder[(x, y)] = (0, 41, 0, 0x8400, 0, 8) if haupt else (0x3F, 42, 1, 0x8000, 0, 57)
    return _weg_ebene(felder=felder)


def test_soeldnerposten_hof_ist_mit_der_weg_ebene_begehbar():
    from selfaware.services import wegkarte as WK

    k = _soeldnerposten()
    start = [
        "".join("B" if 153 <= x <= 162 and 284 <= y <= 293 else "." for x in range(400))
        for y in range(400)
    ]
    alt = W.Wegfuehrung(1, start)  # die Startkarte: jedes Gebaeudefeld ist "B"
    alt.fuehre(1, "gebaeude", 7)
    L, G = {1: _e(1, 71, 158, 288)}, {7: _e(2, 1, 275, 86)}
    st, b = _runde(alt, L, G)
    assert st[1] == "direkt" and b == [
        {"einheiten": [1], "gebaeude": 7}
    ]  # kein Weg im Gitter: das Spiel fuehrt
    w = W.Wegfuehrung(1, WK.als_gelaende(k))
    w.fuehre(1, "gebaeude", 7)
    st, b = _runde(w, L, G)
    assert (
        st[1] == "unterwegs" and "lauf" in b[0]
    )  # mit der Weg-Ebene: eigener, sicherer Weg vom Hof aus


def test_weg_ebene_verraet_keine_fallgruben_und_kein_pech():
    """FAIRNESS F12: Fallgruben (67) und Pech sieht kein Spieler - ihre Felder gelten als freier Boden."""
    from selfaware.services import wegkarte as WK

    k = _weg_ebene(
        felder={
            (5, 5): (0, 30, 0, 0x400, 0, 67),
            (6, 5): (0, 0, 0, 0x80000000, 0, 0),
            (7, 5): (0, 31, 0, 0x400, 0, 1),
        }
    )
    zeile = WK.als_gelaende(k)[5]
    assert zeile[5] == "." and zeile[6] == "." and zeile[7] == "#" and zeile[4] == "."


def test_karte_holen_nimmt_nur_die_passende_antwort(monkeypatch):
    from selfaware.services import wegkarte as WK

    k = _weg_ebene()
    k["tick"] = 500
    monkeypatch.setattr(WK, "lesen", lambda pfad=None: k)
    gesendet = []

    def antwort(text):
        return lambda b, warte, bis=None: gesendet.append(b) or [text]

    assert WK.karte_holen(antwort("anderes")) is None  # keine Antwort: die alte Karte gilt weiter
    assert (
        WK.karte_holen(antwort("[villagestudio]: WEGKARTE Tick 499 (0,0)-(399,399): 160000 Felder"))
        is None
    )  # alte Datei
    karte = WK.karte_holen(
        antwort("[villagestudio]: WEGKARTE Tick 500 (0,0)-(399,399): 160000 Felder, 160000 mit Weg")
    )
    assert (
        len(karte) == 400
        and set(karte[0]) == {"."}
        and gesendet[-1] == {"wegkarte": {"x0": 0, "y0": 0, "x1": 399, "y1": 399}}
    )


def _eingemauert():
    """Unsere Karte: um (100, 100) ein geschlossener Ring - das Gitter kennt keinen Weg hinaus."""
    return [
        "".join(
            "#"
            if 88 <= x <= 112 and 88 <= y <= 112 and not (92 <= x <= 108 and 92 <= y <= 108)
            else "."
            for x in range(400)
        )
        for y in range(400)
    ]


def test_ohne_weg_im_gitter_fuehrt_das_spiel_sofort_und_nur_bis_die_einheit_heraus_ist():
    """Partie 11.11. 22:37: auf "kein_weg" gab der Brandtrupp das Ziel auf und waehlte es wieder (Sklave 407 fuenfmal); die Wegsuche
    des Spiels kennt keine Gefahr (Sklave 404 lief mit ihr in einen Typ 23 und einen Schleuderer)."""
    w = W.Wegfuehrung(1, _eingemauert())
    w.fuehre(1, "gebaeude", 7)
    G = {7: _e(2, 3, 300, 100)}
    st, b = _runde(w, {1: _e(1, 71, 100, 100)}, G)
    assert st[1] == "direkt" and b == [
        {"einheiten": [1], "gebaeude": 7}
    ]  # sofort, nicht "kein_weg"
    st, b = _runde(w, {1: _e(1, 71, 100 + W.DIREKT_BIS, 100)}, G)
    assert st[1] == "direkt"  # noch nicht weit genug
    st, b = _runde(w, {1: _e(1, 71, 101 + W.DIREKT_BIS, 100)}, G)
    assert st[1] == "unterwegs" and "lauf" in b[0]  # heraus: wieder der eigene Weg mit Gefahr


def test_bewegt_auch_das_spiel_die_einheit_nicht_heisst_es_kein_weg():
    w = W.Wegfuehrung(1, _eingemauert())
    w.fuehre(1, "gebaeude", 7)
    L, G = {1: _e(1, 71, 100, 100)}, {7: _e(2, 3, 300, 100)}
    for _ in range(W.STECKT_RUNDEN):
        st, _b = _runde(w, L, G)
        assert st[1] == "direkt"
    st, b = _runde(w, L, G)
    assert st[1] == "kein_weg" and b == []  # erst jetzt waehlt das Modul ein anderes Ziel


def test_neue_karte_holt_die_einheit_in_die_wegfuehrung_zurueck():
    w = W.Wegfuehrung(1, _eingemauert())
    w.fuehre(1, "gebaeude", 7)
    L, G = {1: _e(1, 71, 100, 100)}, {7: _e(2, 3, 300, 100)}
    st, _b = _runde(w, L, G)
    assert st[1] == "direkt"
    w.karte(["." * 400] * 400)  # der Lenker liest die Weg-Ebene neu: der Ring ist weg
    st, b = _runde(w, L, G)
    assert st[1] == "unterwegs" and "lauf" in b[0]


def test_laufpunkte_auf_gebaeudefeldern_ruecken_aufs_naechste_freie_feld():
    """Partie 11.11. 23:12 (Fehlerwache F2): die Vorrueck-Stelle (168, 234) lag auf einem Apfelhof - das Spiel nahm den Laufbefehl
    an, keiner der drei Schuetzen ging los."""
    karte = [
        "".join("#" if 166 <= x <= 168 and 232 <= y <= 234 else "." for x in range(400))
        for y in range(400)
    ]
    w = W.Wegfuehrung(1, karte)
    w.fuehre(1, "ort", (168, 234))
    st, b = _runde(w, {1: _e(1, 70, 150, 234)})
    assert st[1] == "unterwegs" and b[0]["lauf"] == [
        168,
        235,
    ]  # das naechste begehbare Feld neben dem Hof (gleich nah: kleineres x)
    st, b = _runde(w, {1: _e(1, 70, 169, 235)})
    assert st[1] == "am_ziel" and b == []
    gross = W.Wegfuehrung(
        1,
        [
            "".join("#" if 164 <= x <= 172 and 230 <= y <= 238 else "." for x in range(400))
            for y in range(400)
        ],
    )
    gross.fuehre(
        1, "ort", (168, 234)
    )  # mitten in einem 9 x 9 Gebaeude: das naechste freie Feld liegt 5 weit
    st, b = _runde(gross, {1: _e(1, 70, 163, 234)})
    assert (
        st[1] == "am_ziel" and b == []
    )  # angekommen ist, wer am freien Feld steht, nicht erst am unerreichbaren Punkt
    g = W.Wegfuehrung(
        1,
        [
            "".join("#" if 200 <= x <= 203 and 100 <= y <= 103 else "." for x in range(400))
            for y in range(400)
        ],
    )
    g.fuehre(1, "gebaeude", 7)
    st, b = _runde(g, {1: _e(1, 71, 180, 101)}, {7: _e(2, 3, 201, 101)})
    assert st[1] == "unterwegs" and b[0]["lauf"] == [
        199,
        101,
    ]  # der letzte Wegpunkt vor dem Gebaeude, nicht das Gebaeudefeld


def test_gerade_freie_linie_braucht_keinen_zwischenhalt():
    """Daniel 11.11. 23:28: "warum so viele befehle zur wegfindung kommen die eine einheit unnötig aufhalten"."""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7)
    st, b = _runde(w, {1: _e(1, 71, 100, 100)}, {7: _e(2, 3, 300, 100)})
    assert st[1] == "unterwegs" and b == [
        {"einheiten": [1], "lauf": [300, 100]}
    ]  # 200 Felder frei: gleich bis zum Ziel


def test_um_gefahr_herum_ohne_halt_an_wegpunkten():
    """Daniel 11.11. 23:28: "... die eine einheit unnötig aufhalten": die Einheit laeuft um einen Schuetzen herum zum Ziel, ohne je
    vor Rundenende an einem Wegpunkt anzukommen und auf den naechsten Befehl zu warten, und bleibt ausser Schussweite. 5 Felder je
    Runde: gemessen 11.11. 23:25 sind es 71-80 Takte je Runde, ein Sklave braucht 16 Takte je Feld."""
    import math

    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7)
    G = {7: _e(2, 3, 300, 100)}
    schuetze = _e(2, 22, 200, 130)  # Bogenschuetze (44 Felder) neben der geraden Linie
    ort, ziel, halte, naechste, befehle = (100, 100), None, 0, 10**6, 0
    for _ in range(150):
        st, b = _runde(w, {1: _e(1, 71, *ort), 60: schuetze}, G)
        if st[1] == "greift_an":
            break
        if b:
            ziel, befehle = tuple(b[0]["lauf"]), befehle + 1
        rest = max(abs(ziel[0] - ort[0]), abs(ziel[1] - ort[1]))
        if rest < 5 and ziel != (300, 100):
            halte += 1  # sie kommt vor Rundenende an und steht bis zum naechsten Befehl
        ort = (
            ort[0] + max(-5, min(5, ziel[0] - ort[0])),
            ort[1] + max(-5, min(5, ziel[1] - ort[1])),
        )
        naechste = min(naechste, math.hypot(ort[0] - 200, ort[1] - 130))
    assert st[1] == "greift_an" and halte == 0 and naechste > 40 and befehle <= 6


def test_wegpunkt_wahl_vorlauf_nur_ohne_gefahr_und_gerade_linie_nur_frei():
    """Mauer x 196-203, y bis 150: der Weg biegt bei (198, 154) um die Ecke, die gerade Linie zum Punkt dahinter geht durch die
    Mauer. Partie 11.11. 23:25: 71-80 Takte je Runde - eine Einheit mit 5 Feldern je Runde kaeme mitten in der Runde an."""
    import selfaware.services.schussfeld as SF

    karte = [
        "".join("#" if 196 <= x <= 203 and y <= 150 else "." for x in range(400))
        for y in range(400)
    ]
    w = W.Wegfuehrung(1, karte)
    ecke, dahinter = (198, 154), (222, 154)

    def wahl(ort, weit, gefahr=()):
        g = SF.Gitter(karte, [])
        for c in gefahr:
            g.gefahr[c[1]][c[0]] = 1
        a = W.Auftrag("ort", (300, 154), "")
        a.weg = [ecke, dahinter, (300, 154)]
        w._naechster(a, g, ort, weit)
        return a.weg[0]

    assert (
        wahl((190, 146), 5) == dahinter
    )  # 8 vor der Ecke, 5 Felder je Runde: der naechste geht schon hinaus
    assert wahl((190, 146), 0) == ecke  # sie stand: noch kein Vorlauf
    zelle = SF.Gitter(karte, []).gerade((190, 146), dahinter)[3]
    assert wahl((190, 146), 5, [zelle]) == ecke  # auf der Abkuerzung liegt Gefahr: erst um die Ecke
    assert wahl((150, 154), 0) == (
        300,
        154,
    )  # unterhalb der Mauer ist die Linie bis zum Ziel frei: kein Wegpunkt noetig


def test_gleicher_befehl_geht_nur_an_eine_stehende_einheit_noch_einmal():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7)
    G = {7: _e(2, 3, 300, 100)}
    _, b = _runde(w, {1: _e(1, 71, 100, 100)}, G)
    assert b
    x = 100
    for _ in range(W.NEU_ALLE + 2):  # sie laeuft: kein Befehl, auch nach NEU_ALLE Runden nicht
        x += 3
        _, b = _runde(w, {1: _e(1, 71, x, 100)}, G)
        assert b == []
    _, b = _runde(w, {1: _e(1, 71, x, 100)}, G)  # sie steht: derselbe Befehl noch einmal
    assert b == [{"einheiten": [1], "lauf": [300, 100]}]


def test_lenker_liest_die_weg_ebene_fuer_die_wegfuehrung():
    import pathlib

    lenker = (
        pathlib.Path(__file__).resolve().parents[1] / "src/selfaware/runtime/live/erstes_spiel.py"
    ).read_text(encoding="utf-8")
    # S146: alle WEGKARTE_RUNDEN Runden und sobald ein Gebaeude dazukommt - die Regel steht in services/wegkarte.neu_lesen
    for zeile in (
        "W_karte.neu_lesen(runde, wegf_karte_runde, G, wegf_karte_geb, WEGKARTE_RUNDEN)",
        'neue_karte, wk_art = W_karte.karte_holen(befehl), "ganz"',
        "wegf.karte(neue_karte)",
    ):
        assert zeile in lenker


def test_eine_wiedervergebene_eigene_nummer_wird_nicht_weitergefuehrt():
    """Logbuch, Partie 12.11. 20:53, Takt 24.021: Schuetze 582 (A_ARCHER 70) starb, das Spiel gab seine Nummer einer eigenen Einheit
    vom Typ 52 - die Wegfuehrung fuehrte sie weiter als Vorstoss-Schuetzen."""
    w = W.Wegfuehrung(1)
    G = {7: _e(2, 3, 200, 100)}
    w.fuehre(582, "gebaeude", 7, "vorstoss")
    w.schritt({582: _e(1, 70, 100, 100)}, G, Befehle())
    assert w.fuehrt(582)
    b = Befehle()
    st = w.schritt({582: _e(1, 52, 100, 100)}, G, b)
    assert not w.fuehrt(582) and st == {} and b.liste == []


def test_vorstoss_ohne_ziel_nimmt_das_alte_angriffsziel_zurueck():
    """Logbuch, Partie 12.11. 20:53, Takt 2.566: der Vorstoss meldete "wartet, kein Ziel", die Wegfuehrung fuehrte seine Schuetzen
    weiter zum alten Ziel (path_target). Hier: Runde 1 ziehen sie zu einem Arbeiter, Runde 2 ist er tabu (kein Schaden) und jede
    Stellung vor ihm liegt im Schussfeld eines Turms - der Vorstoss wartet, und die Wegfuehrung fuehrt sie nicht mehr dorthin."""
    from selfaware.micro.tasks import vorstoss as VS

    v = VS.Vorstoss(1, (50, 100), bis=40000)
    w = W.Wegfuehrung(1)
    v.weg = w
    L = {1: _e(1, 22, 100, 100), 2: _e(1, 22, 100, 101), 3: _e(2, 3, 160, 100)}
    G = {
        90: _e(2, 74, 170, 100)
    }  # Turm: 70 Felder von der Gruppe, 40 von jeder Stellung vor dem Arbeiter
    v.schritt(500, L, G, Befehle())
    assert w.auftraege[1].art == "einheit" and w.auftraege[1].ziel == 3
    v.stur[3] = v.runde + 50  # nimmt keinen Schaden: tabu
    v.schritt(600, L, G, Befehle())
    assert (v.absicht[1][0], v.absicht[1][2]) == ("WAIT_STAGING", "no_safe_firing_position")
    assert not w.fuehrt(1) and not w.fuehrt(2)


def test_weglaenge_ist_der_weg_der_wegfuehrung_nicht_die_luftlinie():
    """S150 (Daniel 14.11.2026 23:29 "Niemals nach luftlinie warum auch?"): die Laenge des sicheren Wegs - dieselben Schritte, die die
    Wegfuehrung plant."""
    import selfaware.services.schussfeld as SF

    karte = [
        "".join("#" if 40 <= x <= 160 and 70 <= y <= 75 else "." for x in range(400))
        for y in range(400)
    ]
    g = SF.Gitter(karte, [])
    laenge = W.Wegfuehrung.weglaenge(g, (100, 100))
    assert laenge((100, 140)) == 40  # frei: 10 Zellen
    assert laenge((100, 60)) > 2 * SF.schach(
        (100, 100), (100, 60)
    )  # hinter der Mauer: um ihr Ende herum
    for ziel in ((100, 60), (300, 300), (20, 20)):
        assert laenge(ziel) == (len(g.weg((100, 100), ziel)) - 1) * g.z
    assert laenge((101, 101)) == 1  # in der Startzelle die Schachdistanz


class _KernAttrappe:
    """S155: steht fuer execution/kernweg.Kernweg - merkt sich, was in den Ring ginge."""

    def __init__(self):
        self.uebergeben, self.erlaubt, self.gesendet, self.frei = set(), {}, [], []

    def erlauben(self, nr, gegner):
        self.uebergeben.add(nr)
        self.erlaubt[nr] = gegner
        return True

    def senden(self, liste):
        self.gesendet += liste
        for b in liste:
            self.uebergeben.update(b["angriff"]["einheiten"])
        return []

    def freigeben(self, einheiten):
        self.frei += list(einheiten)
        self.uebergeben -= set(einheiten)


def test_s155_raid_befehle_gehen_ueber_den_kern_das_ziel_ist_der_erlaubte_gegner():
    """S155 (Daniel 15.11.2026 00:04 "sie braucht noch weitere laufbefehle um durchzuspammen", 00:20 "Ja, Kern bauen"): der Laufbefehl einer
    Raid-Einheit geht als durchzusetzender an den Kern, ihr Ziel als erlaubter Gegner; andere Zwecke bleiben beim Modul; am Ziel geht der
    Angriff ohne Durchsetzen hinaus; wer losgelassen wird, ist im Kern frei."""
    w = W.Wegfuehrung(1)
    k = _KernAttrappe()
    w.kern = k
    w.fuehre(1, "einheit", 50, "nahkampfraid")
    w.fuehre(2, "einheit", 50, "vorstoss")
    L = {1: _e(1, 24, 100, 100), 2: _e(1, 24, 100, 110), 50: _e(2, 3, 200, 100)}
    _st, modul = _runde(w, L)
    assert k.erlaubt == {1: 50}
    assert [b["angriff"]["einheiten"] for b in k.gesendet] == [[1]]
    assert k.gesendet[0]["angriff"]["durchsetzen"] is True and "lauf" in k.gesendet[0]["angriff"]
    assert [b["einheiten"] for b in modul] == [[2]] and "durchsetzen" not in modul[0]
    L[1] = _e(1, 24, 199, 100)
    st, _ = _runde(w, L)
    assert st[1] == "greift_an" and k.gesendet[-1] == {"angriff": {"einheiten": [1], "ziel": 50}}
    w.loslassen(1)
    assert k.frei == [1] and not w.kern_fuehrt(1)


def test_s155_was_der_kern_nicht_nimmt_geht_ohne_durchsetzen_ans_modul():
    w = W.Wegfuehrung(1)
    k = _KernAttrappe()
    k.senden = lambda liste: liste  # Ring voll: alles zurueck
    w.kern = k
    w.fuehre(1, "gebaeude", 7, "nahkampfraid")
    _st, modul = _runde(w, {1: _e(1, 24, 100, 100)}, {7: _e(2, 3, 200, 100)})
    assert (
        k.erlaubt == {1: 0}
        and len(modul) == 1
        and "lauf" in modul[0]
        and "durchsetzen" not in modul[0]
    )


class _KettenKern(_KernAttrappe):
    kann_ketten = True

    def __init__(self):
        super().__init__()
        self.ketten = []

    def kette(self, nr, punkte, danach=None):
        self.ketten.append((nr, list(punkte), danach))
        return True


def test_s159_der_kern_bekommt_den_rest_des_wegs_und_den_angriff_und_der_lenker_schickt_nicht_zurueck():
    """S159 (Daniel 15.11.2026 01:10 "sofort reagieren"): mit dem Laufbefehl zum ersten Wegpunkt bekommt der Kern die weiteren Wegpunkte
    und den Angriff am Ende. Hat der Kern die Einheit schon weitergeschickt (ihr Laufziel im Spiel ist ein spaeterer Wegpunkt), schickt
    der Lenker sie nicht zurueck und nicht noch einmal dorthin."""
    karte = [
        "".join("#" if 150 <= x <= 250 and 60 <= y <= 140 else "." for x in range(400))
        for y in range(400)
    ]  # ein Block im Weg
    w = W.Wegfuehrung(1, karte)
    k = _KettenKern()
    w.kern = k
    w.fuehre(1, "einheit", 50, "nahkampfraid")
    L = {1: _e(1, 24, 100, 100), 50: _e(2, 3, 300, 100)}
    _st, _m = _runde(w, L)
    assert len(k.gesendet) == 1 and len(k.ketten) == 1
    nr, punkte, danach = k.ketten[0]
    erster = tuple(k.gesendet[0]["angriff"]["lauf"])
    assert nr == 1 and danach == ("einheit", 50) and len(punkte) >= 1 and erster not in punkte
    assert punkte == [(262, 142), (300, 100)]  # nur die Ecken, keine Zwischenpunkte alle 24 Felder
    # der Kern hat sie zum zweiten Wegpunkt geschickt: kein neuer Befehl in dieser Runde
    L[1] = dict(_e(1, 24, erster[0], erster[1]), laufx=punkte[0][0], laufy=punkte[0][1])
    _st, _m = _runde(w, L)
    assert len(k.gesendet) == 1 and w.auftraege[1].weg[0] == punkte[0]


def test_s159_auf_freiem_feld_ist_die_kette_nur_der_angriff_am_ende():
    w = W.Wegfuehrung(1)
    k = _KettenKern()
    w.kern = k
    w.fuehre(1, "gebaeude", 7, "nahkampfraid")
    _runde(w, {1: _e(1, 24, 100, 100)}, {7: _e(2, 3, 300, 100)})
    assert k.ketten == [(1, [], ("gebaeude", 7))]


def test_s159_ohne_ketten_im_kern_bleibt_alles_wie_bisher():
    w = W.Wegfuehrung(1)
    k = _KernAttrappe()
    w.kern = k
    w.fuehre(1, "einheit", 50, "nahkampfraid")
    _runde(w, {1: _e(1, 24, 100, 100), 50: _e(2, 3, 300, 100)})
    assert len(k.gesendet) == 1 and not hasattr(k, "ketten") and w._ketten == {}
