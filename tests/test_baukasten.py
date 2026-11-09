"""B-176, B-177: Baukasten, ohne Spiel."""

import ast
import gzip
import json
import pathlib
import re
import sys
import types

import pytest

from selfaware.baukasten import aufstellung as AF
from selfaware.baukasten import formation
from selfaware.baukasten import karte as K
from selfaware.baukasten.ausweichen import NACHLAUF, SCHUSSWEITE, Schussfeld
from selfaware.baukasten.bestellung import ARTEN, Bestellung

LENKER = (
    pathlib.Path(__file__).resolve().parents[1] / "src/selfaware/runtime/live/erstes_spiel.py"
).read_text(encoding="utf-8")


def test_ohne_schalter_duerfen_alle_arten_werben():
    b = Bestellung()
    assert all(b.darf(a) for a in ARTEN)


def test_nur_raid_laesst_angriff_und_verteidigung_nicht_werben():
    b = Bestellung("raid")
    assert b.darf("raid") and not b.darf("angriff") and not b.darf("verteidigung")
    assert str(b) == "raid"


def test_mehrere_arten_gehen():
    b = Bestellung("raid, verteidigung")
    assert b.darf("raid") and b.darf("verteidigung") and not b.darf("angriff")


@pytest.mark.parametrize("text", ["", "raids", "alle,raid"])
def test_falsche_schreibweise_faellt_auf(text):
    with pytest.raises(ValueError):
        Bestellung(text)


def test_unbekannte_art_faellt_auf():
    with pytest.raises(ValueError):
        Bestellung().darf("heer")


def _e(x, y, typ=71, besitzer=1, leben=1000):
    return {"x": x, "y": y, "typ": typ, "besitzer": besitzer, "leben": leben}


def _runde(s, L=None, G=None):
    s.neue_runde(L or {}, G or {})


def test_keine_feinde_kein_ausweichen():
    s = Schussfeld(1)
    _runde(s)
    assert not s.unter_feuer(1, _e(100, 100))


def test_schuetze_in_reichweite_loest_aus_und_ausserhalb_nicht():
    for abstand, erwartet in ((SCHUSSWEITE, True), (SCHUSSWEITE + 1, False)):
        s = Schussfeld(1)
        _runde(s, {9: _e(100 + abstand, 100, typ=22, besitzer=2)})
        assert s.unter_feuer(1, _e(100, 100)) is erwartet, abstand


def test_nahkaempfer_und_eigene_schuetzen_loesen_nicht_aus():
    s = Schussfeld(1)
    _runde(
        s,
        {
            8: _e(105, 100, typ=26, besitzer=2),
            9: _e(105, 100, typ=22, besitzer=1),
            7: _e(105, 100, typ=22, besitzer=0),
        },
    )
    assert not s.unter_feuer(1, _e(100, 100))


def test_tote_schuetzen_loesen_nicht_aus():
    s = Schussfeld(1)
    _runde(s, {9: _e(105, 100, typ=22, besitzer=2, leben=0)})
    assert not s.unter_feuer(1, _e(100, 100))


def test_feindlicher_turm_loest_aus_eigener_nicht():
    s = Schussfeld(1)
    _runde(s, G={5: {"typ": 75, "x": 110, "y": 100, "besitzer": 2}})
    assert s.unter_feuer(1, _e(100, 100))
    s = Schussfeld(1)
    _runde(s, G={5: {"typ": 75, "x": 110, "y": 100, "besitzer": 1}})
    assert not s.unter_feuer(1, _e(100, 100))


def test_wer_leben_verliert_weicht_aus_auch_ohne_sichtbaren_schuetzen():
    s = Schussfeld(1)
    _runde(s)
    assert not s.unter_feuer(1, _e(100, 100, leben=1000))
    _runde(s)
    assert s.unter_feuer(1, _e(100, 100, leben=900))


def test_nachlauf_haelt_das_ausweichen_noch_die_naechsten_runden():
    s = Schussfeld(1)
    _runde(s, {9: _e(105, 100, typ=22, besitzer=2)})
    assert s.unter_feuer(1, _e(100, 100))
    for _ in range(NACHLAUF):
        _runde(s)
        assert s.unter_feuer(1, _e(100, 100))
    _runde(s)
    assert not s.unter_feuer(1, _e(100, 100))


def test_karte_kennt_jeden_spielteil_und_beide_richtungen():
    assert set(K.KARTE) == set(K.SPIELTEILE)
    for teil in K.SPIELTEILE:
        assert K.module_von(teil), teil
        for modul in K.module_von(teil):
            assert teil in K.teil_von(modul)


def test_daniels_spielteile_stehen_auf_der_karte():
    for teil in (
        "apfel",
        "brot",
        "bier",
        "waffen",
        "bestellung_raid",
        "bestellung_angriff",
        "bestellung_verteidigung",
        "scaling",
        "acceleration",
    ):
        assert K.KARTE[teil]


def test_karte_nennt_nur_was_es_gibt():
    assert K.fehlende_stellen() == []
    assert K.fehlende_schalter() == []


def test_karte_laesst_nichts_aus():
    """Daniel: alles von Gehirn und Hand zuordnen. Was neu dazukommt und nicht zugeordnet ist, faellt hier auf."""
    assert K.nicht_auf_der_karte() == []
    assert K.schalter_ohne_modul() == []


def test_karte_datei_ist_aktuell():
    assert K.ZIEL.read_text(encoding="utf-8") == K.markdown()


def test_karte_nennt_den_stand_ehrlich():
    stand = {m.name: K.stand(m) for m in K.alle_module()}
    assert stand["Brandtrupp"] == "steckbar"
    assert stand["Alter Ausbau"] == "nicht benutzt"
    assert stand["Alter Angriffstrupp"] == "nicht benutzt"
    assert stand["Produktion"] == "im Lenker"
    assert stand["Nahrungswahl"] == "eigene Datei"
    assert stand["Weltbild des Kerns"] == "Kern"


HEUTIGE_KLASSEN = {
    "waechter": ("selfaware.micro.tasks.waechter", "Waechter"),
    "einzeln": ("selfaware.micro.tasks.assassinen", "Einzeln"),
    "wirtschaft": ("selfaware.macro.wirtschaft", "Wirtschaft"),
    "ertragsplaner": ("selfaware.macro.ertragsplaner", "Ertragsplaner"),
    "brandtrupp": ("selfaware.micro.tasks.raids", "Brandtrupp"),
    "reiterjagd": ("selfaware.micro.tasks.raids", "Reiterjagd"),
    "deckung": ("selfaware.micro.tasks.raids", "Deckung"),
    "vorstoss": ("selfaware.micro.tasks.vorstoss", "Vorstoss"),
    "feldzug": ("selfaware.micro.tasks.feldzug", "Feldzug"),
    "bierkette": ("selfaware.macro.bierkette", "Bierkette"),
    "brotbau": ("selfaware.macro.brotbau", "BrotBau"),
    "jagdbau": ("selfaware.macro.brotbau", "JagdBau"),
    "kornring": ("selfaware.macro.kornring", "Kornring"),
    "graben": ("selfaware.macro.kornring", "Graben"),
    "fallenwache": ("selfaware.micro.tasks.fallenwache", "Fallenwache"),
}


def test_ohne_aufstellung_baut_der_lenker_die_klassen_von_heute():
    """P3.12: fester Erwartungswert, nicht aus der Karte abgeleitet."""
    s = AF.Steckplaetze()
    for name, (modul, klasse) in HEUTIGE_KLASSEN.items():
        k = s.klasse(name)
        assert (k.__module__, k.__name__) == (modul, klasse)
    assert len(K.steckplaetze()) == 17  # dazu Ausbau und Angriffstrupp, die der Lenker nie baut


def test_lenker_holt_jede_steckklasse_ueber_den_steckplatz():
    namen = {klasse for _, klasse in HEUTIGE_KLASSEN.values()}
    direkt = [
        (k.lineno, getattr(k.func, "attr", getattr(k.func, "id", "")))
        for k in ast.walk(ast.parse(LENKER))
        if isinstance(k, ast.Call) and getattr(k.func, "attr", getattr(k.func, "id", "")) in namen
    ]
    assert direkt == []
    assert sorted(re.findall(r'STECK\.klasse\("(\w+)"\)', LENKER)) == sorted(HEUTIGE_KLASSEN)


def test_code_kennung_sieht_weiter_alle_module():
    """P3.12: Die Kennung folgt den import-Zeilen, darum muessen die Importe trotz Steckplatz stehen bleiben."""
    from selfaware.telemetry import kennung

    dateien = {pathlib.PurePath(d).as_posix() for d in kennung.python_dateien()}
    for pfad in K.steckplaetze().values():
        assert "src/" + pfad.split(":")[0].replace(".", "/") + ".py" in dateien, pfad


def _probe_modul(monkeypatch, klasse):
    m = types.ModuleType("probe_version")
    m.Neu = klasse
    monkeypatch.setitem(sys.modules, "probe_version", m)


def test_neue_version_wird_gesteckt_und_steht_in_der_mitschrift(monkeypatch):
    from selfaware.micro.tasks.raids import Brandtrupp

    class Neu(Brandtrupp):
        pass

    _probe_modul(monkeypatch, Neu)
    s = AF.Steckplaetze({"brandtrupp": "probe_version:Neu"})
    assert s.klasse("brandtrupp") is Neu
    assert s.klasse("reiterjagd").__name__ == "Reiterjagd"
    assert "brandtrupp=probe_version:Neu sha256:" in str(s)
    assert str(AF.Steckplaetze()) == "alle von heute"


def test_version_mit_anderem_aufruf_faellt_vor_dem_start_auf(monkeypatch):
    from selfaware.micro.tasks.raids import Brandtrupp

    class Neu(Brandtrupp):
        def schritt(self, L, G):
            return []

    _probe_modul(monkeypatch, Neu)
    with pytest.raises(ValueError, match="schritt"):
        AF.Steckplaetze({"brandtrupp": "probe_version:Neu"})


def test_version_ohne_alles_faellt_vor_dem_start_auf(monkeypatch):
    class Neu:
        pass

    _probe_modul(monkeypatch, Neu)
    with pytest.raises(ValueError, match="passt nicht"):
        AF.Steckplaetze({"brandtrupp": "probe_version:Neu"})


def test_unbekannter_steckplatz_faellt_auf():
    with pytest.raises(ValueError, match="Unbekannter"):
        AF.Steckplaetze({"gibt_es_nicht": "selfaware.micro.tasks.raids:Brandtrupp"})


def _schreibe(ordner, name, **felder):
    (ordner / f"{name}.json").write_text(json.dumps({"name": name, **felder}), encoding="utf-8")


def test_erben_nimmt_die_basis_und_aendert_nur_das_genannte(tmp_path):
    _schreibe(tmp_path, "a", schalter={"x": "1", "y": "2"}, versionen={"p": "m:A"})
    _schreibe(tmp_path, "b", basis="a", schalter={"y": "3"}, gruende={"y": "weil"})
    d = AF.laden("b", tmp_path)
    assert d["schalter"] == {"x": "1", "y": "3"} and d["versionen"] == {"p": "m:A"}


@pytest.mark.parametrize(
    "felder",
    [
        {"schalter": {"y": "3"}, "gruende": {}},
        {"schalter": {}, "versionen": {"p": "m:B"}, "gruende": {}},
    ],
)
def test_aenderung_ohne_grund_faellt_auf(tmp_path, felder):
    _schreibe(tmp_path, "a", schalter={"y": "2"})
    _schreibe(tmp_path, "b", basis="a", **felder)
    with pytest.raises(ValueError, match="ohne Grund"):
        AF.laden("b", tmp_path)


def test_erben_im_kreis_faellt_auf(tmp_path):
    _schreibe(tmp_path, "a", basis="b", schalter={}, gruende={})
    _schreibe(tmp_path, "b", basis="a", schalter={}, gruende={})
    with pytest.raises(ValueError, match="Kreis"):
        AF.laden("a", tmp_path)


def test_raid_frueh_aendert_nur_die_begruendeten_schalter():
    basis = AF.laden("vorstoss_laptop")["schalter"]
    s = AF.laden("raid_frueh")["schalter"]
    assert {k for k in set(basis) | set(s) if basis.get(k) != s.get(k)} == {
        "bestellung",
        "ausweichen",
        "produktion",
        "endspurt",
    }


def test_raid_frueh_bleibt_im_zweig_der_raids():
    """Steuerung und Werbung der Raids stehen im Lenker unter "if streitkolben:" und "if feldzug is not None:". streitkolben=0 oder ein anderer
    weg schalten sie still ab, und bei feldzug None endet die Partie sofort mit "ZIEL 0 erreicht". Faellt weg, sobald der Raid aus dem Angriffszweig geloest ist."""
    s = AF.laden("raid_frueh")["schalter"]
    assert int(s["streitkolben"]) > 0 and s["weg"] == "feldzug" and s.get("raids", "ja") == "ja"
    assert (
        int(s["assassinen"]) != 0
    )  # ohne das baut phase1 keinen Soeldnerposten, und ohne Posten wirbt keine Raid-Stelle


def test_startzeile_ohne_aufstellung_unveraendert():
    roh = ["tempo=40", "karte=A B"]
    assert AF.startzeile(roh, {"tempo": "40", "karte": "A B"}, None) == roh


def test_startzeile_mit_aufstellung_nennt_jeden_schalter():
    arg, daten = AF.anwenden({"aufstellung": "raid_frueh"})
    z = AF.startzeile(["aufstellung=raid_frueh"], arg, daten)
    for teil in ("bestellung=raid", "karte=The Killing Plains", "aufstellung=raid_frueh"):
        assert teil in z


@pytest.mark.parametrize(
    "von, ziel, n, erwartet",
    [
        (
            (100, 190),
            (200, 200),
            8,
            [
                (200, 192),
                (195, 192),
                (200, 197),
                (195, 197),
                (200, 202),
                (195, 202),
                (200, 207),
                (195, 207),
            ],
        ),
        ((95, 200), (100, 50), 3, [(95, 50), (100, 50), (105, 50)]),
    ],
)
def test_breite_aufstellung_rechnet_wie_bisher_im_vorstoss(von, ziel, n, erwartet):
    assert formation.breit(von, ziel, n, 5, 4) == erwartet


def test_querachse():
    assert formation.querachse((0, 0), (10, 2)) == "y"
    assert formation.querachse((0, 0), (2, 10)) == "x"


def test_lage_zahlen_trennen_starttruppen_raid_und_andere(tmp_path):
    from selfaware.tools.experiments.aufstellung_vergleich import lage_zahlen

    def bild(t, *zeilen):
        return json.dumps(
            {"t": t, "einheiten": "tick %d\nnr besitzer typ\n%s" % (t, "\n".join(zeilen))}
        )

    pfad = tmp_path / "lage.jsonl.gz"
    with gzip.open(pfad, "wt", encoding="utf-8") as f:
        f.write(bild(700, "1 1 22", "2 1 71", "3 2 26") + "\n")  # Starttruppen und ein Feind
        f.write(json.dumps({"t": 800}) + "\n")  # Bild ohne Einheiten
        f.write(
            bild(900, "1 1 22", "2 1 71", "4 1 74", "5 1 26") + "\n"
        )  # neu: Reiter, Streitkolben
        f.write(bild(1000, "1 1 22", "4 1 74", "5 1 26") + "\n")  # Sklave tot
    assert lage_zahlen(pfad) == {"raid": (1, 1), "andere": (1, 0)}


def test_aufstellung_setzt_ihre_schalter_und_die_befehlszeile_geht_vor():
    arg, daten = AF.anwenden({"aufstellung": "raid_frueh", "tempo": "40"})
    assert daten["name"] == "raid_frueh" and arg["bestellung"] == "raid" and arg["tempo"] == "40"
    assert arg["ausweichen"] == "ja" and arg["produktion"] == "nein"


def test_ohne_aufstellung_bleibt_alles_wie_es_ist():
    arg = {"tempo": "40"}
    assert AF.anwenden(arg) == (arg, None)


def test_unbekannte_aufstellung_faellt_auf():
    with pytest.raises(OSError):
        AF.anwenden({"aufstellung": "gibt_es_nicht"})


def test_falscher_name_in_der_datei_faellt_auf(tmp_path):
    (tmp_path / "a.json").write_text('{"name": "b", "schalter": {}}', encoding="utf-8")
    with pytest.raises(ValueError):
        AF.laden("a", tmp_path)


def test_die_alte_schalterliste_steckt_vollstaendig_in_vorstoss_laptop():
    """P3.12: Die lange Befehlszeile des Laptop-Laufs bleibt erhalten, nur ohne die Gegnerpruefung, die auf Instanz 2 nicht passt."""
    konsole = (
        pathlib.Path(__file__).resolve().parents[1]
        / "data/research/vorstoss_1108b_200_i1_konsole.txt"
    ).read_text(encoding="utf-8", errors="replace")
    zeile = next(z for z in konsole.splitlines() if z.startswith("START-BEFEHL"))
    alt = dict(t.strip('"').split("=", 1) for t in re.findall(r'"[^"]+=[^"]+"|\S+=\S+', zeile))
    alt.pop("gegner_erwartet")
    assert AF.laden("vorstoss_laptop")["schalter"] == alt


def test_kennzahlen_nennen_fehlendes_nicht_null():
    from selfaware.tools.experiments.aufstellung_vergleich import kennzahlen

    z = kennzahlen("Ende Phase 2 bei Tick 40182 nach 347 Runden; Brandtrupp: 19 Gebaeude")
    assert z["ende"] == 40182 and z["angezuendet"] == 19 and z["zerstoert"] is None


def _stellen():
    zeilen = LENKER.splitlines()
    return [
        (i, z)
        for i, z in enumerate(zeilen)
        if re.search(r'"werbe":|\bBA\w*\.werbe\(|RA\.werbung\(', z)
        and not z.lstrip().startswith("#")
    ]


def test_jede_rekrutierstelle_steht_hinter_dem_tor():
    """Eine neue Stelle ohne Tor wuerde bestellung=raid still aushebeln: Darum sind Stellen und Tore gezaehlt."""
    zeilen = LENKER.splitlines()
    stellen = _stellen()
    assert len(stellen) == 10, [
        i + 1 for i, _ in stellen
    ]  # RA.werbung und BA_r.werbe sind dieselbe Stelle
    assert LENKER.count("BESTELLUNG.darf(") == 9
    for i, z in stellen:
        davor = "\n".join(zeilen[max(0, i - 50) : i + 1])
        assert "BESTELLUNG.darf(" in davor, (i + 1, z.strip())


def test_arten_der_tore():
    gezaehlt = re.findall(r'BESTELLUNG\.darf\("(\w+)"\)', LENKER)
    assert gezaehlt.count("raid") == 3
    assert gezaehlt.count("angriff") == 5
    assert gezaehlt.count("verteidigung") == 1
