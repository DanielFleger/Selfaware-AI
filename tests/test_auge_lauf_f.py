"""B-142: Lauf F ohne Spiel: Menueweg, Einspielen der logik.lua, Programm und Abbruch an einem kuenstlichen Kanal."""
from __future__ import annotations

import pytest

from selfaware.tools.experiments import auge_lauf_f as lf


class Kanal:
    """Antwortet wie das Spiel: Knopf 3 oeffnet die Kartenwahl, der Start-Knopf die Partie."""

    def __init__(self, karten=("Antioch", lf.KARTE, "Tyre"), ansicht=lf.HAUPTMENUE, start_geht=True, knopf3_geht=True):
        self.karten, self.ansicht, self.start_geht, self.knopf3_geht = list(karten), ansicht, start_geht, knopf3_geht
        self.log, self.speicher = [], {}

    def peek(self, adr, n=1):
        if adr == lf.ANSICHT:
            return [self.ansicht]
        if adr == lf.GESAMT:
            return [len(self.karten)]
        if adr == lf.LISTE:
            return list(range(n))
        nr = (adr - lf.NAMEN) // lf.NAMENSLAENGE
        roh = self.karten[nr].encode("latin-1") + b"\0" * (4 * n)
        return [int.from_bytes(roh[i * 4:i * 4 + 4], "little") for i in range(n)]

    def befehl(self, cmd, warte=0.8, bis=None):
        self.log.append(cmd)
        if cmd.get("hauptmenue") == 3 and self.knopf3_geht:
            self.ansicht = lf.KARTENWAHL
        if cmd.get("menue") == lf.HAUPTMENUE:
            self.ansicht = lf.HAUPTMENUE
        return []

    def liste(self, cmds, warte=1.0):
        self.log.append(cmds)
        for c in cmds:
            if "poke" in c:
                self.speicher[c["poke"]] = c["wert"]
            if c.get("knopf") == "SingleplayerMapChoice_ButtonsAndHands" and c["nr"] == lf.KNOPF_START and self.start_geht:
                self.ansicht = lf.IN_PARTIE
        return []


def ohne_warten(_):
    return None


def test_warte_auf_modul_haelt_fehlende_antworten_aus_und_gibt_sonst_auf():
    class Spaet:
        def __init__(self, n):
            self.n = n

        def peek(self, adr, n=1):
            self.n -= 1
            if self.n > 0:
                raise lf.Fehler("keine Antwort")
            return [41]
    lf.warte_auf_modul(Spaet(3), 60, ruhe=ohne_warten)
    zeit = [0.0]

    def uhr():
        zeit[0] += 1.0
        return zeit[0]
    with pytest.raises(lf.Fehler, match="Modul antwortet"):
        lf.warte_auf_modul(Spaet(10 ** 6), 5, ruhe=ohne_warten, uhr=uhr)


def test_burgenbau_waehlt_die_richtige_karte_und_startet():
    k = Kanal()
    e = lf.burgenbau_starten(k, ruhe=ohne_warten)
    assert e["eintrag"] == 1
    assert k.speicher[lf.SCROLL] + k.speicher[lf.MARKIERT] == 1
    assert {"hauptmenue": 3} in k.log and {"eigenerPlatz": 1} in k.log
    assert k.log.index({"hauptmenue": 3}) < k.log.index({"eigenerPlatz": 1})


def test_burgenbau_mit_langer_liste_scrollt_und_zeile_bleibt_im_bild():
    karten = [f"Karte {i}" for i in range(60)]
    karten[50] = lf.KARTE
    k = Kanal(karten)
    lf.burgenbau_starten(k, ruhe=ohne_warten)
    assert k.speicher[lf.SCROLL] + k.speicher[lf.MARKIERT] == 50
    assert 0 <= k.speicher[lf.MARKIERT] <= 12


def test_burgenbau_aus_laufender_partie_geht_erst_ins_hauptmenue():
    k = Kanal(ansicht=lf.IN_PARTIE)
    lf.burgenbau_starten(k, ruhe=ohne_warten)
    assert k.log[0] == {"menue": lf.HAUPTMENUE}


def test_burgenbau_fehlende_karte_bricht_ab_und_startet_nichts():
    k = Kanal(karten=("Antioch", "Tyre"))
    with pytest.raises(lf.Fehler, match="steht nicht in der Kartenliste"):
        lf.burgenbau_starten(k, ruhe=ohne_warten)
    assert not any(isinstance(x, list) for x in k.log)


def test_warte_auf_gibt_nach_der_frist_einen_fehler():
    zeit = [0.0]

    def uhr():
        zeit[0] += 1.0
        return zeit[0]
    with pytest.raises(lf.Fehler, match="nicht erreicht"):
        lf.warte_auf(lambda: False, 5, "nie", uhr=uhr, ruhe=ohne_warten)
    assert lf.warte_auf(lambda: True, 5, "gleich", uhr=uhr, ruhe=ohne_warten) is None


def lua(tmp_path, ende="\r\n", anker=True):
    p = tmp_path / "quelle.lua"
    zeile = f"      {lf.ANKER}{ende}" if anker else ""
    p.write_bytes(f"local HANDLER = {{{ende}{zeile}      Ende = 1,{ende}}}{ende}".encode("latin-1"))
    return str(p)


def test_logik_text_fuegt_den_knopf_einmal_und_mit_gleichem_einzug_ein(tmp_path):
    q = lua(tmp_path)
    t = lf.logik_text(q)
    assert f"      {lf.ANKER}\r\n      {lf.NEU}\r\n" in t
    (tmp_path / "zweit.lua").write_bytes(t.encode("latin-1"))
    assert lf.logik_text(str(tmp_path / "zweit.lua")) == t


CONFIG = """meta:
  version: 1.0.0
active: true
config-sparse:
  modules: {}
  plugins:
    Mod-KI-Team-Liga:
      config: {}
  load-order:
  - extension: Mod-KI-Team-Liga
    version: 2.0.2
config-full:
  load-order:
  - extension: gmResourceModifier
    version: 0.2.0
  - extension: Mod-KI-Team-Liga
    version: 2.0.2
"""


@pytest.mark.parametrize("nl", ["\n", "\r\n"])
def test_modul_eintragen_aendert_nur_die_ladelisten(tmp_path, nl):
    yaml = pytest.importorskip("yaml")
    p = tmp_path / "ucp-config.yml"
    p.write_bytes(CONFIG.replace("\n", nl).encode())
    s = lf.modul_eintragen(str(p), "T1")
    assert open(s, "rb").read() == CONFIG.replace("\n", nl).encode()
    neu = yaml.safe_load(p.read_bytes())
    assert neu["config-sparse"]["modules"] == {"villagestudio": {"config": {}}}
    assert neu["config-sparse"]["load-order"][-1] == {"extension": "villagestudio", "version": "0.1.0"}
    assert neu["config-full"]["load-order"][-1] == {"extension": "villagestudio", "version": "0.1.0"}
    assert len(neu["config-full"]["load-order"]) == 3 and neu["active"] is True
    assert lf.modul_eintragen(str(p), "T2") is None


def test_modul_eintragen_mit_vollen_modulen_bricht_ab_statt_zu_raten(tmp_path):
    pytest.importorskip("yaml")
    p = tmp_path / "ucp-config.yml"
    p.write_text(CONFIG.replace("  modules: {}", "  modules:\n    fremd:\n      config: {}"))
    with pytest.raises(lf.Fehler, match="von Hand"):
        lf.modul_eintragen(str(p))


def test_modul_eintragen_nie_in_instanz_5():
    with pytest.raises(lf.Fehler):
        lf.modul_eintragen(lf.ordner(5) + r"\ucp-config.yml")


def test_lua_probe_findet_syntaxfehler():
    pytest.importorskip("lupa")
    assert lf.lua_fehler("local a = 1") is None
    assert lf.lua_fehler("local a = = 1")


def test_logik_text_ohne_stelle_ist_ein_fehler(tmp_path):
    with pytest.raises(lf.Fehler):
        lf.logik_text(lua(tmp_path, anker=False))


def test_logik_einspielen_sichert_die_alte_datei_und_schreibt_nichts_doppelt(tmp_path):
    q = lua(tmp_path)
    z = tmp_path / "logik.lua"
    z.write_bytes(b"alt")
    s = lf.logik_einspielen(str(z), q, "T1")
    assert open(s, "rb").read() == b"alt"
    assert lf.NEU.encode() in z.read_bytes()
    assert lf.logik_einspielen(str(z), q, "T2") is None
    assert not (tmp_path / "logik.vor_auge_T2.lua").exists()


def test_instanz_5_wird_nie_ziel():
    with pytest.raises(lf.Fehler):
        lf.pruefe_laufinstanz(5)
    with pytest.raises(lf.Fehler):
        lf.logik_einspielen(lf.ordner(5) + r"\ucp\villagestudio\logik.lua", "egal")
    with pytest.raises(lf.Fehler):
        lf.main(["los", "--instanz", "5", "--daniel-ja"])
    assert lf.pruefe_laufinstanz(2) == 2


def test_lauf_ohne_ja_startet_nicht():
    with pytest.raises(lf.Fehler, match="daniel-ja"):
        lf.main(["los", "--instanz", "2"])


def test_kandidaten_sind_verschieden_und_auf_der_karte():
    k = lf.kandidaten((10, 200), 7, 40)
    assert len(k) == len(set(k)) > 10
    assert all(8 <= x <= 391 and 8 <= y <= 391 for x, y in k)
    assert (10, 200) not in k


class Werkzeug:
    def __init__(self, bauen_geht=True):
        self.NACH_TYP = {41: {}, 9: {}, 8: {}, 10: {}, 26: {}}
        self.jetzt, self.bauen_geht, self.geworben = 100, bauen_geht, []

    def takt(self):
        return self.jetzt

    def gebaeude_von(self, sp, typ):
        return []

    def baue_irgendwo(self, typ, kandidaten):
        if not self.bauen_geht:
            return None
        return (typ * 10, kandidaten[0][0], kandidaten[0][1])

    def werbe(self, e, g):
        self.geworben.append((e, g))

    def laufe_bis(self, ziel):
        self.jetzt = ziel
        return ziel

    def laufe_bis_jahre(self, n):
        self.jetzt += 1000
        return self.jetzt


def test_gold_wird_von_den_waren_nicht_ueberschrieben():
    assert 15 not in lf.WAREN
    k = Kanal()
    lf.phase_vorrat(k, Werkzeug(), {})
    assert not any(isinstance(c, dict) and c.get("ware", {}).get("typ") == 15 for c in k.log)


def test_tempotreppe_misst_jede_stufe_ohne_mit_ohne():
    takt = [0]
    k = Kanal()
    uhr = [0.0]

    def jetzt_tempo():
        return [c["tempo"] for c in k.log if "tempo" in c][-1]

    def ruhe(s):
        uhr[0] += s
        takt[0] += int(s * jetzt_tempo())

    def lese(sek, stufe):
        uhr[0] += sek
        takt[0] += int(sek * stufe)
        return {"takte_je_s": float(stufe), "gelesen": 780, "gesamt": 781}
    z = lf.tempotreppe(k, lambda: takt[0], lese, stufen=(1, 1000), sekunden=20, ruhe=ruhe, uhr=lambda: uhr[0])
    assert [x["tempo"] for x in z] == [1, 1000]
    assert z[0]["ohne_1"] == 1.0 and z[1]["mit"] == 1000.0
    assert {"tempo": 1000} in k.log and {"pause": False} in k.log
    assert not any("pause" in c and "tempo" in c for c in k.log)
    assert 1 in lf.STUFEN and 1000 in lf.STUFEN


def test_tempotreppe_bricht_ab_wenn_das_tempo_nicht_wirkt():
    takt = [0]
    uhr = [0.0]

    def ruhe(s):
        uhr[0] += s
        takt[0] += int(s * 200)  # das Spiel bleibt auf 200, wie im Lauf 18:16
    with pytest.raises(lf.Fehler, match="wirkt nicht"):
        lf.tempotreppe(Kanal(), lambda: takt[0], None, stufen=(40,), sekunden=20, ruhe=ruhe, uhr=lambda: uhr[0])


def test_bauen_haelt_das_spiel_nie_an():
    k = Kanal()
    takt = [0]

    def ruhe(_):
        takt[0] += 1
    versuche = []

    def gebaeude(sp, typ):
        return [(7, 5, 5)] if len(k.log) >= 3 else []
    e = lf.baue_ohne_anhalten(k, lambda: takt[0], gebaeude, {"mapper": 61, "b": 7}, 41, [(1, 1), (2, 2), (3, 3), (4, 4)], ruhe=ruhe)
    assert e == (7, 5, 5)
    assert len(k.log) == 3 and all("baue" in c for c in k.log)
    assert not any("pause" in c or "tickpause" in c for c in k.log)


def test_programm_nennt_das_tempo_jeder_phase():
    uhr = iter(float(i) for i in range(1000))
    w = Werkzeug()
    e = lf.programm(Kanal(), w, lambda x: None, phasen=[("warenketten", lf.phase_warenketten)], uhr=lambda: next(uhr))
    assert e[0]["sekunden"] == 1.0 and e[0]["takte_je_s"] == 6000.0


def test_programm_laeuft_alle_phasen_und_schreibt_jede_auf():
    aus = []
    w = Werkzeug()
    e = lf.programm(Kanal(), w, aus.append)
    assert [x["phase"] for x in e] == [p[0] for p in lf.PHASEN]
    assert all(x["ok"] for x in e)
    assert aus == e
    assert (22, 90) in w.geworben and (70, 80) in w.geworben
    assert e[0]["takt_von"] == 100 and e[-1]["takt_bis"] > 100


def test_programm_scheiternde_phase_endet_nur_die_phase():
    e = lf.programm(Kanal(), Werkzeug(bauen_geht=False), lambda x: None)
    burg = [x for x in e if x["phase"] == "burg"][0]
    assert burg["ok"] is False and "Bergfried" in burg["fehler"]
    assert e[-1]["phase"] == "jahre" and e[-1]["ok"] is True
    bauen = [x for x in e if x["phase"] == "bauen"][0]
    assert bauen["daten"]["nicht_gesetzt"] == [8, 9, 10, 26]


def test_wache_bricht_den_ganzen_lauf_ab():
    n = []

    def wache():
        n.append(1)
        if len(n) == 3:
            raise lf.Fehler("Abbruch: Takte fehlen")
    with pytest.raises(lf.Fehler, match="Takte fehlen"):
        lf.programm(Kanal(), Werkzeug(), lambda x: None, wache=wache)
    assert len(n) == 3
