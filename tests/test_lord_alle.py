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


def test_nur_der_stapel_greift_an_wenn_alle_da_sind():
    """Daniel 16.11.2026 00:10: "die assassinen troepfeln wieder rein ohne stacking". 8 von 12 am Platz: noch kein Angriff; alle 12 da:
    alle 12 zugleich. Laeuft die Zeit ab, greift nur der Stapel an - wer nicht dasteht, raidet weiter statt einzeln hinterherzulaufen."""
    a, L = _szene(12)
    _schritt(a, L, 20000)
    plaetze = dict(a.lordtrupp["platz"])

    def hin(ks):
        for k in ks:
            L[k].update(x=plaetze[k][0], y=plaetze[k][1], laufx=plaetze[k][0], laufy=plaetze[k][1])

    hin(sorted(plaetze)[:8])
    _schritt(a, L, 20200)
    assert a.lordtrupp["phase"] == "bereit", "8 von 12 da: warten, nicht einzeln losschicken"
    hin(sorted(plaetze)[8:])
    ev = _schritt(a, L, 20400)
    assert a.lordtrupp["phase"] == "angriff" and a.angriffe[-1]["groesse"] == 12, [
        z for z in ev if "LORD" in z
    ]


def test_zeit_um_greift_nur_der_stapel_an():
    a, L = _szene(12)
    _schritt(a, L, 20000)
    plaetze = dict(a.lordtrupp["platz"])
    for k in sorted(plaetze)[:8]:
        L[k].update(x=plaetze[k][0], y=plaetze[k][1], laufx=plaetze[k][0], laufy=plaetze[k][1])
    _schritt(a, L, 20200)
    ev = _schritt(a, L, 20000 + a.BEREIT_MAX + 10)
    assert a.lordtrupp["phase"] == "angriff" and a.angriffe[-1]["groesse"] == 8, [
        z for z in ev if "LORD" in z
    ]
    assert not any("ABGEBROCHEN" in z for z in ev)


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


def test_nach_gescheiterter_bereitstellung_erst_stapeln_dann_direkt():
    """Probe 15.11.2026 23:29: zweimal 0 von 6/8 bereit (B-185 #80). Daniel 16.11.2026 00:01: "37 sind nur noetig weil du sie nicht gestackt
    hast sondern einzeln vorgeschickt" - nach dem Abbruch sammeln sich alle am vordersten Assassinen (erreichbar), erst wenn auch das nicht
    ankommt, gehen alle direkt."""
    a, L = _szene(12)
    _schritt(a, L, 20000)
    ev = _schritt(a, L, 20000 + a.BEREIT_MAX + 10)  # keiner kam an
    assert any("ABGEBROCHEN" in z for z in ev) and a._bereit_kaputt
    a.lordtrupp["pause_bis"] = 0
    ev = _schritt(a, L, 30000)
    vorn = min(
        range(200, 212), key=lambda k: (max(abs(L[k]["x"] - 340), abs(L[k]["y"] - 100)), k)
    )  # Schachmass wie im Modul
    assert a.lordtrupp["phase"] == "bereit" and set(a.lordtrupp["platz"].values()) == {
        (L[vorn]["x"], L[vorn]["y"])
    }, ev
    ev = _schritt(a, L, 30000 + a.BEREIT_MAX + 10)  # auch der Sammelpunkt kam nicht an
    assert a._sammel_kaputt
    a.lordtrupp["pause_bis"] = 0
    ev = _schritt(a, L, 40000)
    assert a.lordtrupp["phase"] == "angriff" and len(a.lordtrupp["mitglieder"]) == 12, [
        z for z in ev if "LORD" in z
    ]
    assert any(z.startswith("LORD DIREKT") for z in ev)
    assert a.angriffe[-1]["gestapelt"] is False


def test_einzeln_angekommene_zaehlen_nicht_fuer_den_bedarf():
    a, _L = _szene(1)
    a.angriffe.append(
        {
            "fertig": True,
            "groesse": 14,
            "lord_vorher": 165000,
            "lord_nachher": 103800,
            "gestapelt": False,
        }
    )
    assert a._lord_bedarf_gemessen(103800) is None, "Probe 3: 14 einzeln geschickt - kein Massstab"


def test_neuer_sammelpunkt_am_naechsten_sicheren_mitglied():
    """Probe 5 Takt 19.557: Sammelplatz entdeckt - der Stapel geht zum naechsten sicheren Mitglied, nicht zum Ring."""
    a, L = _szene(3)
    a._sicht = None
    assert a._sammelpunkt_neu(L, {200, 201, 202}, (340, 100), ausser=(250, 90)) == (250, 92)


def test_frist_der_bereitstellung_aus_dem_anmarsch():
    """16.11.2026 (Probe 11, 12, 13c: die erste Bereitstellung kam nie an - Wege bis 208 Felder, 16 Takte je Feld, Frist fest 3.000): die
    Frist waechst mit dem weitesten Anmarsch der Gruppe. Nahe Gruppe: BEREIT_MAX wie bisher; ferne Gruppe: nach BEREIT_MAX + 10 kein
    Abbruch, erst nach ihrer Frist."""
    a, L = _szene(12)
    _schritt(a, L, 20000)
    assert a._bereit_frist() == a.BEREIT_MAX, "Anmarsch 60-90 Felder: die Untergrenze gilt"
    AS = _modul()
    b = AS.Einzeln(1)
    b.lord_aus, b.LORD_SPAETESTENS = False, 0
    L2 = {1: _e(1, 1, 55, 20, 20, leben=150000), 60: _e(60, 2, 55, 380, 380, leben=165000)}
    for i in range(12):
        L2[200 + i] = _e(200 + i, 1, 73, 40, 30 + 2 * i, leben=12500)
    b.aufnehmen(list(range(200, 212)))
    _schritt(b, L2, 20000)
    assert b.lordtrupp["phase"] == "bereit"
    frist = b._bereit_frist()
    weite = max(b.lordtrupp["anmarsch"].values())
    assert (
        weite > 300
        and frist == int(weite * AS.TEMPO * b.BEREIT_ZUSCHLAG + b.BEREIT_VORLAUF) > b.BEREIT_MAX
    )
    ev = _schritt(b, L2, 20000 + b.BEREIT_MAX + 10)
    assert b.lordtrupp["phase"] == "bereit" and not any("ABGEBROCHEN" in z for z in ev), (
        "ferne Gruppe: noch in der Frist"
    )
    ev = _schritt(b, L2, 20000 + frist + 10)
    assert any("ABGEBROCHEN" in z for z in ev), "nach der Frist: Abbruch wie bisher"


def test_sammelplatz_nach_zeit_und_gefahr():
    """16.11.2026 (Probe 11-14: der Platz mit dem kleinsten Schaden lag 176-208 Schritte weit hinter der Burg, keiner kam an; der eine mit
    128 Schritten kam an): Kosten = Anmarsch x TEMPO + Schadensanteil x LEBEN_TAKTE x Lebensgewicht. Ein kleiner Schaden auf einem viel
    kuerzeren Weg schlaegt den schadlosen Umweg; ein Weg, der eine halbe Assassine kostet, nicht."""
    AS = _modul()
    a = AS.Einzeln(1)
    kurz_gekratzt = a._platz_kosten(250.0, 128, 12500)  # 2 % Leben auf 128 Feldern
    lang_sauber = a._platz_kosten(0.0, 190, 12500)
    kurz_toedlich = a._platz_kosten(6250.0, 128, 12500)  # halbe Assassine
    assert kurz_gekratzt < lang_sauber < kurz_toedlich


def test_bereitstellung_gibt_den_naechsten_wegpunkt_jede_runde_und_die_kette_dem_kern():
    """16.11.2026 (Probe 14: ~30 statt 16 Takte je Feld, der naechste Wegpunkt kam hoechstens jede zweite Runde): bereit_routen gibt die
    Wegpunkte fuer die Kette des Kerns; zeigt das Laufziel schon auf einen spaeteren Wegpunkt, gelten die davor als erledigt."""
    a, L = _szene(12)
    _schritt(a, L, 20000)
    assert a.lordtrupp["phase"] == "bereit"
    r = a.bereit_routen()
    assert set(r) == set(range(200, 212)) and all(
        v["gebaeude"] is None and v["punkte"] for v in r.values()
    )
    k = 200
    a.lordtrupp["weg"][k] = [(260, 92), (280, 95), (300, 98), a.lordtrupp["platz"][k]]
    L[k].update(laufx=300, laufy=98)  # der Kern fuehrt ihn schon zum dritten Wegpunkt
    _schritt(a, L, 20200)
    assert a.lordtrupp["weg"][k][0] == (300, 98), a.lordtrupp["weg"][k]
    assert "Einzeln" in type(a).__name__


def test_bereitstellung_platz_und_wegpunkte_im_gebiet_der_assassine():
    """16.11.2026 (Probe 16): Platz und Wegpunkte der Bereitstellung gehen durch feld_nah(punkt, ort der Assassine) - die Wegfuehrung
    rueckt sie ins erreichbare Gebiet. karte_neu gibt den Assassinen die Weg-Ebene und rechnet das Gitter neu."""
    a, L = _szene(12)
    gefragt = []
    a.feld_nah = lambda p, von=None: (gefragt.append((tuple(p), von)), (p[0] + 1, p[1]))[1]
    _schritt(a, L, 20000)
    assert a.lordtrupp["phase"] == "bereit"
    orte = {(L[k]["x"], L[k]["y"]) for k in range(200, 212)}
    assert gefragt and all(v in orte for _, v in gefragt), gefragt[:3]
    plaetze = set(a.lordtrupp["platz"].values())
    assert all((q[0] - 1, q[1]) in {p for p, _ in gefragt} for q in plaetze), (
        "der Platz selbst ging durch feld_nah"
    )
    a._frei, a._gitter_runde = [[True]], (a.runde, object())
    a.karte_neu(["." * 400] * 400)
    assert a.gelaende[0] == "." * 400 and a._frei is None and a._gitter_runde[0] is None


def _im_angriff(n=6):
    """Lord-Gruppe im Angriff: alle am Platz, der Stapel hat angegriffen."""
    a, L = _szene(n)
    _schritt(a, L, 20000)
    for k, p in dict(a.lordtrupp["platz"]).items():
        L[k].update(x=p[0], y=p[1], laufx=p[0], laufy=p[1])
    _schritt(a, L, 20200)
    assert a.lordtrupp["phase"] == "angriff"
    return a, L


def test_im_lord_angriff_erst_die_schuetzen_neben_den_assassinen():
    """Daniel 16.11.2026 22:59 ("er verliert immer noch assassinen ohne ende weil sie nicht auf bogenschuetzen gehen"): ein feindlicher
    Bogenschuetze 3 Felder neben zwei Assassinen wird von hoechstens SCHUETZE_JE angegriffen (Angriff mit Wiederholung im Kern); die anderen
    gehen auf den Lord. Hat der Lord nur noch LORD_FERTIG seines Lebens, geht alles auf den Lord."""
    a, L = _im_angriff(6)
    k1 = 200
    bx, by = L[k1]["x"] + 3, L[k1]["y"]
    L[900] = _e(900, 2, 22, bx, by, leben=1000)
    for k in range(201, 203):  # zwei weitere stehen auch neben dem Bogen
        L[k].update(x=bx - 3, y=by + 1, laufx=bx - 3, laufy=by + 1)
    ev, bef = a.schritt(L, {}, sichere_orte=[(100, 100)], tick=20400)
    auf_bogen = [
        n
        for b in bef
        if "angriff" in b and b["angriff"].get("ziel") == 900
        for n in b["angriff"]["einheiten"]
    ]
    assert len(auf_bogen) == a.SCHUETZE_JE and all(
        b["angriff"].get("durchsetzen") for b in bef if b.get("angriff", {}).get("ziel") == 900
    ), bef
    L[60]["leben"] = int(a.LORD_FERTIG * a.angriffe[-1]["lord_vorher"]) - 1
    ev, bef = a.schritt(L, {}, sichere_orte=[(100, 100)], tick=20600)
    # die Beute-Jagd der Freien (BEUTE_R) bleibt - im Lord-Angriff aber kein Angriff mit Wiederholung mehr auf den Bogen
    assert not any(
        b.get("angriff", {}).get("ziel") == 900 and b["angriff"].get("durchsetzen") for b in bef
    ), "Lord fast tot: alles auf den Lord"


def test_bereitstellungsplaetze_ausserhalb_der_burg():
    """16.11.2026: Ringplaetze 22-31 Felder vom Lord kamen in sechs Partien nie an (am Burgrand entdeckt), 43-46 Felder schon - der Ring
    liegt jetzt bei BEREIT_R = 40/44/48."""
    AS = _modul()
    a = AS.Einzeln(1)
    a._sicht = None
    plaetze = a._bereit_plaetze((200, 200))
    assert (
        plaetze and min(max(abs(x - 200), abs(y - 200)) for x, y in plaetze) >= 28
    )  # Schach: 40 Felder im Kreis sind mind. 28 Schach
    assert min(((x - 200) ** 2 + (y - 200) ** 2) ** 0.5 for x, y in plaetze) >= 39.5
