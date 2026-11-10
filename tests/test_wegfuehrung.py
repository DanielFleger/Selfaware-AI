"""B-182 Wegfuehrung fuer alle Einheiten (Plan_Wegfuehrung.md), ohne Spiel."""

import selfaware.services.schussfeld as SF
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
    st, b = _runde(w, {1: _e(1, 22, 212, 100), 50: _e(2, 3, 250, 100)})  # 38 Felder: Reichweite 40 minus 2
    assert st[1] == "greift_an" and b == [{"einheiten": [1], "ziel": 50}]


def test_neue_gefahr_im_weg_wird_umgangen():
    """Daniel 11.11.: 'er sollte immer adjustieren sollte im lauf eine gefahr in den weg kommen'."""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    L = {1: _e(1, 22, 100, 100), 50: _e(2, 3, 300, 100)}
    _, b1 = _runde(w, L)
    L2 = {**L, 60: _e(2, 22, 150, 100), 61: _e(2, 22, 150, 104)}  # zwei Bogenschuetzen mitten auf dem Weg
    _, b2 = _runde(w, L2)
    assert b2 and b2[0]["lauf"] != b1[0]["lauf"]
    assert SF.gefahr_am(tuple(b2[0]["lauf"]), W.gefahren(L2, {}, 1)) == 0


def test_ziel_in_gefahr_kein_befehl():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7)
    st, b = _runde(w, {1: _e(1, 71, 100, 100), 60: _e(2, 22, 205, 100)}, {7: _e(2, 3, 200, 100)})
    assert st[1] == "gefahr" and b == []


def test_fernkaempfer_haelt_abstand_zu_kuerzerer_reichweite_nicht_zu_gleicher():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    st, _ = _runde(w, {1: _e(1, 22, 100, 100), 50: _e(2, 72, 250, 100)})  # Schleuderer 22: Standplatz 36 ist sicher
    assert st[1] == "unterwegs"
    w2 = W.Wegfuehrung(1)
    w2.fuehre(1, "einheit", 51)
    st, b = _runde(w2, {1: _e(1, 22, 100, 100), 51: _e(2, 22, 250, 100)})  # Bogenschuetze 44: jeder Standplatz in seiner Reichweite
    assert st[1] == "gefahr" and b == []


def test_hoechstens_acht_befehle_je_runde_und_keine_wiederholung():
    """Je Einheit ein eigener Weg (10 Felder Abstand): gleiche Befehle wuerden gebuendelt."""
    w = W.Wegfuehrung(1)
    L = {}
    for i in range(12):
        L[i + 1] = _e(1, 22, 100, 100 + 10 * i)
        L[100 + i] = _e(2, 3, 300, 100 + 10 * i)
        w.fuehre(i + 1, "einheit", 100 + i)
    _, b1 = _runde(w, L)
    _, b2 = _runde(w, L)
    _, b3 = _runde(w, L)
    assert len(b1) == W.BUDGET and len(b2) == 12 - W.BUDGET and b3 == []


def test_wiedervergebene_nummer_ist_kein_ziel():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    _runde(w, {1: _e(1, 22, 100, 100), 50: _e(2, 3, 250, 100)})
    st, b = _runde(w, {1: _e(1, 22, 100, 100), 50: _e(2, 1, 260, 100)})  # Nummer 50 traegt jetzt einen Bauern
    assert st[1] == "ziel_weg" and b == []


def test_verborgene_fallgrube_ist_keine_gefahr_ein_turm_schon():
    """FAIRNESS F12: Holzfallen und Pech des Gegners sind verborgen; Tuerme sind sichtbar."""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7)
    st, _ = _runde(w, {1: _e(1, 71, 100, 100)}, {7: _e(2, 3, 200, 100), 8: _e(2, 67, 201, 100)})
    assert st[1] == "unterwegs"
    w2 = W.Wegfuehrung(1)
    w2.fuehre(1, "gebaeude", 7)
    st, _ = _runde(w2, {1: _e(1, 71, 100, 100)}, {7: _e(2, 3, 200, 100), 9: _e(2, 77, 210, 100)})
    assert st[1] == "gefahr"


def test_nahkaempfer_darf_an_einen_soldaten_heran():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    st, b = _runde(w, {1: _e(1, 75, 100, 100), 50: _e(2, 24, 200, 100)})  # Speertraeger: seine eigene Naehe zaehlt nicht
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
    L2 = {**L, 60: _e(2, 22, G[erstes]["x"] + 5, G[erstes]["y"])}  # ein Bogenschuetze stellt sich ans Ziel
    st, _ = _runde(w, L2, G)
    assert st[1] == "gefahr"
    bt.schritt(L2, G, Befehle())
    assert bt.ziel.get(1) not in (None, erstes) and w.fuehrt(1)


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


def test_vorstoss_gibt_schuetzen_an_die_wegfuehrung_und_holt_sie_zum_vorruecken_zurueck():
    from selfaware.micro.tasks import vorstoss as V

    v = V.Vorstoss(1, (100, 100))
    w = W.Wegfuehrung(1)
    v.weg = w
    b = Befehle()
    v.schritt(500, {1: _e(1, 22, 100, 100), 2: _e(1, 22, 100, 101), 3: _e(2, 3, 130, 110)}, {}, b)
    assert b.liste == [] and w.fuehrt(1) and w.fuehrt(2)  # kein eigener Schussbefehl, die Wegfuehrung fuehrt beide
    b = Befehle()
    v.schritt(600, {1: _e(1, 22, 100, 100), 2: _e(1, 22, 100, 101), 4: _e(2, 3, 260, 100)}, {}, b)  # Ziel weg: vorruecken
    assert b.liste and "lauf" in b.liste[0] and not w.fuehrt(1) and not w.fuehrt(2)


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


def test_gleiche_befehle_gehen_als_einer_hinaus():
    """Wie der Vorstoss bisher: ein Befehl fuer alle Schuetzen auf dasselbe Ziel, nicht einer je Schuetze (Budget S82)."""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    w.fuehre(2, "einheit", 50)
    st, b = _runde(w, {1: _e(1, 22, 212, 100), 2: _e(1, 22, 213, 103), 50: _e(2, 3, 250, 100)})  # Luftlinie 38 und 37,1
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
    L = {1: _e(1, 74, 100, 100), 2: _e(1, 74, 150, 60), 50: _e(2, 3, 150, 100), 51: _e(2, 3, 100, 180)}
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
    L2 = {1: _e(1, 74, 215, 100), 50: _e(2, 13, 250, 100)}  # Nummer 50 traegt jetzt einen anderen Arbeiter
    st, _ = _runde(w, L2)
    assert st[1] == "ziel_weg"
    aus = rj.schritt(L2, {}, Befehle())
    assert rj.getoetet == 1 and any("hat Arbeiter 50 erledigt" in z for z in aus)
    st, b = _runde(w, L2)  # der neue Arbeiter unter Nummer 50 wird gejagt, nicht als "ziel_weg" stehen gelassen
    assert st[1] == "greift_an" and b == [{"einheiten": [1], "ziel": 50}]


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
    """Nach der Wegfuehrung geht der naechste eigene Lauf sofort hinaus, auch wenn er dem letzten gleicht (sonst erst nach NEU_ALLE)."""
    from selfaware.micro.tasks import vorstoss as V

    v = V.Vorstoss(1, (100, 100))
    w = W.Wegfuehrung(1)
    v.weg = w
    fern = {1: _e(1, 22, 100, 100), 2: _e(1, 22, 100, 101), 4: _e(2, 3, 260, 100)}
    b1 = Befehle()
    v.schritt(500, fern, {}, b1)
    assert b1.liste and "lauf" in b1.liste[0]
    v.schritt(510, {**fern, 3: _e(2, 3, 130, 110)}, {}, Befehle())
    assert w.fuehrt(1)
    b3 = Befehle()
    v.schritt(520, fern, {}, b3)
    assert b3.liste == b1.liste and not w.fuehrt(1)


def test_vorstoss_gibt_ein_ziel_ohne_angriff_und_weg_auf():
    from selfaware.micro.tasks import vorstoss as V

    v = V.Vorstoss(1, (100, 100))
    w = _WegAttrappe()
    v.weg = w
    L = {1: _e(1, 22, 100, 100), 2: _e(1, 22, 100, 101), 3: _e(2, 3, 130, 110), 5: _e(2, 3, 128, 80)}
    v.schritt(500, L, {}, Befehle())
    erstes = w.auftraege[1][1]
    w.st = {1: "gefahr", 2: "kein_weg"}
    aus = v.schritt(510, L, {}, Befehle())
    assert any("gibt Ziel %d auf" % erstes in z for z in aus)
    assert w.auftraege[1][1] != erstes and w.auftraege[2][1] != erstes
