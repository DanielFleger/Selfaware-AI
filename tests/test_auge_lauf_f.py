"""B-142: Lauf F ohne Spiel: Menueweg, Einspielen der logik.lua, Programm und Abbruch an einem kuenstlichen Kanal."""

from __future__ import annotations

import collections
import glob
import itertools
import json
import os
import struct

import pytest

from selfaware.tools.experiments import auge_lauf_f as lf

INSTANZ2 = os.path.isdir(
    r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz2"
)
braucht_instanz2 = pytest.mark.skipif(
    not INSTANZ2, reason="Spielinstanz 2 fehlt (nur auf dem Mess-PC)"
)


class Kanal:
    """Antwortet wie das Spiel: Knopf 3 oeffnet die Kartenwahl, der Start-Knopf die Partie."""

    def __init__(
        self,
        karten=("Antioch", lf.KARTE, "Tyre"),
        ansicht=lf.HAUPTMENUE,
        start_geht=True,
        knopf3_geht=True,
    ):
        self.karten, self.ansicht, self.start_geht, self.knopf3_geht = (
            list(karten),
            ansicht,
            start_geht,
            knopf3_geht,
        )
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
        return [int.from_bytes(roh[i * 4 : i * 4 + 4], "little") for i in range(n)]

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
            if (
                c.get("knopf") == "SingleplayerMapChoice_ButtonsAndHands"
                and c["nr"] == lf.KNOPF_START
                and self.start_geht
            ):
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
        lf.warte_auf_modul(Spaet(10**6), 5, ruhe=ohne_warten, uhr=uhr)


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


def test_burgenbau_wartet_auf_den_menuewechsel():
    class Spaet(Kanal):
        rest = 0

        def befehl(self, cmd, warte=0.8, bis=None):
            self.log.append(cmd)
            if cmd.get("menue") == lf.HAUPTMENUE:
                self.rest = 3  # die Quittung kommt vor dem Wechsel
            if (
                cmd.get("hauptmenue") == 3 and self.ansicht == lf.HAUPTMENUE
            ):  # der Knopf gehoert zum Hauptmenue, sonst tut er nichts
                self.ansicht = lf.KARTENWAHL
            return []

        def peek(self, adr, n=1):
            if adr == lf.ANSICHT and self.rest:
                self.rest -= 1
                if not self.rest:
                    self.ansicht = lf.HAUPTMENUE
            return super().peek(adr, n)

    k = Spaet(ansicht=lf.IN_PARTIE)
    assert lf.burgenbau_starten(k, ruhe=ohne_warten)["eintrag"] == 1


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
    bau = f"    {lf.BAU_ALT}{ende}    log(INFO, {lf.BAU_LOG_ALT}{ende}      0){ende}"
    p.write_bytes(
        f"local HANDLER = {{{ende}{zeile}      Ende = 1,{ende}}}{ende}{bau}".encode("latin-1")
    )
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
    assert neu["config-sparse"]["load-order"][-1] == {
        "extension": "villagestudio",
        "version": "0.1.0",
    }
    assert neu["config-full"]["load-order"][-1] == {
        "extension": "villagestudio",
        "version": "0.1.0",
    }
    assert len(neu["config-full"]["load-order"]) == 3 and neu["active"] is True
    assert lf.modul_eintragen(str(p), "T2") is None


def test_modul_eintragen_mit_vollen_modulen_bricht_ab_statt_zu_raten(tmp_path):
    pytest.importorskip("yaml")
    p = tmp_path / "ucp-config.yml"
    p.write_text(CONFIG.replace("  modules: {}", "  modules:\n    fremd:\n      config: {}"))
    with pytest.raises(lf.Fehler, match="von Hand"):
        lf.modul_eintragen(str(p))


def test_modul_eintragen_nie_in_instanz_5():
    pytest.importorskip("yaml")  # PyYAML kommt nur mit dem Extra "legacy" (B-167)
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


# --- Das ganze Programm gegen ein kuenstliches Spiel: Erfolg und jeder Abbruchgrund ---
ARTEN = {
    t: {"mapper": 200 + t, "b": b, "name": f"Art{t}"}
    for t, b in (
        (41, 7),
        (19, 4),
        (1, 4),
        (10, 5),
        (11, 4),
        (9, 5),
        (8, 5),
        (24, 5),
        (25, 5),
        (38, 9),
        (12, 4),
        (33, 9),
        (62, 2),
        (67, 1),
        (5, 4),
        (20, 6),
    )
}
ARTEN[45] = {"mapper": 147, "b": 7, "name": "Grosses Torhaus"}
ARTEN[46] = {"mapper": 145, "b": 5, "name": "Kleines Torhaus"}
ARTEN[lf.PECHGRABEN] = {"mapper": 99, "b": 1, "name": "Pechgraben"}
ARTEN[lf.PECHGRUBE] = {"mapper": 91, "b": 4, "name": "Pechgrube"}


class KunstSpiel:
    """Antwortet wie das Spiel: Takte laufen mit der Uhr, Bauten erscheinen nach 3 Takten, Waren fliessen 1 Stueck je 4 Takte,
    alle 250 Takte ein Bewohner, alle 200 Takte eine Woche, sobald der Kornspeicher steht. fehler schaltet je einen Defekt ein."""

    def __init__(self, **fehler):
        self.f = fehler
        self.jetzt, self.t, self.tempo, self.pausiert, self.rest = 0.0, 100, 1000, 0, 0.0
        self.geb, self.nr = {}, 1
        self.start = [0] * 25
        self.start[2], self.start[13] = 50, 20
        self.best = [0] * 25
        self.pop, self.deckel, self.feuer, self.bel = 0, 0, 0, 8775
        self.jahr, self.monat, self.woche, self.anzeige = 1196, 0, 0, 2
        self.steuer, self.ration, self.pech, self.fail, self.armee = 2, 2, 0, 0, 0
        self.einh, self.schlaf, self.bits = collections.Counter(), collections.Counter(), {}
        self.warte, self.log, self.protokoll = [], [], []
        self.letzter_bewohner, self.aus = 100, False
        self.neue_felder_bis = self.f.get("neue_felder_bis", 0)
        self.rek_stand = {"fehlend": 0, "gemischt": 0}
        self.bremse = self.f.get("bremse", 0)
        self.gestartet = []

    # Uhr
    def uhr(self):
        return self.jetzt

    def ruhe(self, d):
        self.jetzt += d
        if self.pausiert or self.f.get("stillstand_bei", 10**9) <= self.t:
            return
        rate = min(self.tempo, 825)
        if self.aus and self.tempo >= 1000:
            rate = 825
        elif not self.aus and self.bremse and self.tempo >= 1000:
            rate = 700
        self.rest += d * rate
        while self.rest >= 1:
            self.rest -= 1
            self._takt()

    def _takt(self):
        self.t += 1
        for w in [w for w in self.warte if w[0] <= self.t]:
            self.warte.remove(w)
            self._baue(w[1])
        if not self.f.get("woche_steht") and self.anzeige == 0 and self.t % 200 == 0:
            self.woche += 1
            if self.woche > 3:
                self.woche, self.monat = 0, self.monat + 1
            if self.monat > 11:
                self.monat, self.jahr = 0, self.jahr + 1
        if self.t % 4 == 0 and self.gebaeude_von(lf.BURG) and not self.f.get("waren_haengen"):
            lager = next((w for w in (2, 3, 4, 6, 7, 9, 14, 16) if self.start[w] > 0), None)
            for w in [lager] + [
                w for w in list(range(10, 14)) + list(range(17, 25)) if self.start[w] > 0
            ]:
                if w is not None and not (
                    w >= 17 and sum(self.best[17:25]) >= lf.WAFFENLAGER_FASST
                ):
                    self.start[w] -= 1
                    self.best[w] += 1
        if (
            self.gebaeude_von(lf.BURG)
            and self.pop < self.deckel
            and self.t - self.letzter_bewohner >= 250
            and not self.f.get("kein_bewohner")
        ):
            self.letzter_bewohner = self.t
            self.pop += 1
            self.feuer += 1
        for g in self.geb.values():
            if g["offen"] and self.feuer:
                g["offen"] -= 1
                self.feuer -= 1
        if self.f.get("beliebtheit_faellt"):
            self.bel = max(0, self.bel - 2)
        if self.f.get("beliebtheit_im_steuertest") and self.steuer == 11:
            self.bel = 4000
        elif self.f.get("beliebtheit_im_steuertest") and self.bel < 8775:
            self.bel += 1

    # Kanal
    def befehl(self, cmd, warte=0.8, bis=None):
        self.log.append(cmd)
        self._cmd(cmd)
        self.ruhe(0.03)
        return []

    def liste(self, cmds, warte=1.0):
        self.log.append(cmds)
        for c in cmds:
            self._cmd(c)
        self.ruhe(0.03)
        return []

    def _cmd(self, c):
        if "gold" in c and not self.f.get("gold_kommt_nicht"):
            self.best[15] = c["gold"]
        if "tempo" in c:
            self.tempo = c["tempo"]
        if "pause" in c:
            self.pausiert = 1 if c["pause"] else 0
        if "poke" in c and 0x1000 <= c["poke"] < 0x1000 + 25:
            self.start[c["poke"] - 0x1000] = c["wert"]
        if "baue" in c:
            self.warte.append((self.t + 3, c["baue"]))
        if "abreissen" in c:
            self.geb.pop(c["abreissen"]["nr"], None)
        if "werbe" in c and self.feuer:
            self.feuer -= 1
            self.einh[c["werbe"]["typ"]] += 1
        s = c.get("spielbefehl")
        if s:
            n, w = s["nr"], s["werte"]
            if n == lf.BEFEHL_STEUER and not self.f.get("steuer_wirkt_nicht"):
                self.steuer = w[0]
            if n == lf.BEFEHL_RATION:
                self.ration = w[0]
            if n == lf.BEFEHL_HANDEL:
                if (
                    w[0] == 0
                    and w[1] >= 17
                    and sum(self.best[17:25]) + lf.LOS > lf.WAFFENLAGER_FASST
                ):
                    self.fail = 10  # storageMarketFailState: Lager voll, nichts passiert
                elif w[0] == 1 and self.best[w[1]] < lf.LOS:
                    self.fail = 11
                else:
                    self.best[w[1]] += lf.LOS if w[0] == 0 else -lf.LOS
                    self.best[15] += -10 if w[0] == 0 else 8
            if n == lf.BEFEHL_TOR:
                self.geb[w[0]]["tor"] = lf.TOR_FERTIG if self.f.get("tor_wird_fertig") else w[1]
            if n == lf.BEFEHL_SCHLAF:
                self.schlaf[w[0]] ^= 1
            if n == lf.BEFEHL_MAUER:
                self.bits[(w[0], w[1])] = lf.BIT_MAUER
            if n == lf.BEFEHL_GRABEN:
                self.bits[(w[0], w[1])] = lf.BIT_GRABEN

    def _typ(self, mapper):
        return next(t for t, g in ARTEN.items() if g["mapper"] == mapper)

    def _baue(self, b):
        typ = self._typ(b["mapper"])
        if self.f.get("bau_scheitert") == typ:
            return
        if typ == lf.PECHGRABEN:
            self.pech += 1
            return
        if (
            self.f.get("zweiter_bau_scheitert")
            and typ in (*lf.ZUSATZ, lf.KASERNE)
            and self.gebaeude_von(typ)
        ):
            return
        if typ == lf.KASERNE:
            for n in [n for n, g in self.geb.items() if g["typ"] == typ]:
                del self.geb[n]
        self.geb[self.nr] = {
            "nr": self.nr,
            "typ": typ,
            "x": b["x"],
            "y": b["y"],
            "v": b["richtung"],
            "offen": 1 if typ in (19, 12, 33, 5, 20) else 0,
            "uid": 7000 + self.nr,
            "tor": 0,
        }
        self.nr += 1
        if typ == lf.KORN and not self.f.get("anzeige_bleibt"):
            self.anzeige = 0
        if typ == lf.HUETTE and not self.f.get("huette_ohne_platz"):
            self.deckel = max(self.deckel, 10) + 8
        if typ == lf.BURG:
            self.deckel += 10

    def platzkarte(self, mapper, groesse, x0, y0, x1, y1, sp=1):
        typ = self._typ(mapper)
        if typ == lf.PECHGRUBE or self.f.get("keine_stelle") == typ:
            return ["6" * (x1 - x0 + 1)] * (y1 - y0 + 1)
        return [
            "".join(
                "+" if not any(g["x"] == x and g["y"] == y for g in self.geb.values()) else "l"
                for x in range(x0, x1 + 1)
            )
            for y in range(y0, y1 + 1)
        ]

    # Speicher
    def takt(self):
        if self.f.get("spiel_weg_bei", 10**9) <= self.t:
            raise OSError("Prozess weg")
        return self.t

    def pause(self):
        return self.pausiert

    def kalender(self):
        return self.jahr, self.monat, self.woche

    def spieler(self, name, sp=1):
        if name == "populationCap" and self.f.get("deckel_zuckt"):
            self.zucken = not getattr(self, "zucken", False)
            if self.zucken:
                return 0  # mitten in der Neuberechnung
        return {
            "popularity": self.bel,
            "populationCap": self.deckel,
            "availablePeasantsAtFire": self.feuer,
            "storageMarketFailState": self.fail,
            "armySize": self.armee,
            "totalFood": sum(self.best[10:14]) if not self.f.get("kein_essen") else 0,
            "currentPopulation": self.pop,
            "taxesSetting": self.steuer,
            "rationsSetting": self.ration,
        }[name]

    def waren(self, sp=1):
        return list(self.best)

    def startwaren(self, sp=1):
        return list(self.start)

    def start_adresse(self, w, sp=1):
        return 0x1000 + w

    def anzeige_burg_korn(self):
        return self.anzeige

    def gebaeude(self, sp=1):
        return [dict(g) for g in self.geb.values()]

    def gebaeude_von(self, typ):
        return [g for g in self.geb.values() if g["typ"] == typ]

    def arbeiter_je_typ(self, typ):
        return 1 if typ in (19, 12, 33, 5, 20) else 0

    def pechgraeben(self, sp=1):
        return self.pech

    def schlaeft(self, typ, sp=1):
        return self.schlaf[typ]

    def logik(self, x, y):
        return self.bits.get((x, y), 0)

    def felder_mit_bit(self, bit):
        return (
            []
            if bit == lf.BODEN[lf.PECHGRUBE]
            else [(280, 259)]
            if bit == lf.BODEN[5]
            else [(70, 194)]
        )

    def einheiten(self, sp=1):
        return collections.Counter(self.einh)

    # Rekorder
    def fehler(self):
        return (
            "beendet mit 3: Takt fehlt" if self.f.get("rekorder_tot_bei", 10**9) <= self.t else None
        )

    def aussetzen(self, an):
        self.aus = an
        if (
            not an
            and self.bremse
            and self.f.get("bremse_nur_einmal")
            and self.protokoll
            and any(e.get("bremsprobe") for e in self.protokoll)
        ):
            self.bremse = 0

    def felder(self):
        return {
            "takt": self.t,
            "felder": 5,
            "letzter_neuer_takt": self.t if self.t < self.neue_felder_bis else 0,
        }

    def starten(self, name, tempo, streng=False, felder=False):
        self.gestartet.append((name, tempo, streng))

    def laeuft(self):
        return True

    def beenden(self):
        return dict(self.rek_stand)

    def lese_runde(self, takte, stufe, wach):
        a, t0 = self.t, self.jetzt
        while self.t < a + takte:
            wach()
            self.ruhe(0.005)
        return {
            "takte_je_s": (self.t - a) / (self.jetzt - t0),
            "gelesen": self.t - a,
            "takte": self.t - a,
            "sekunden": self.jetzt - t0,
        }


def lauf_von(g, frist=lf.FRIST, stop=lambda: False):
    return lf.Lauf(
        g, g, ARTEN, g, g.protokoll.append, frist=frist, uhr=g.uhr, ruhe=g.ruhe, stop=stop
    )


def ganzer_lauf(**fehler):
    g = KunstSpiel(**fehler)
    l = lauf_von(g)
    start = g.kalender()
    lf.programm(l)
    return g, l, lf.schluss(l, start)


def test_ganzer_lauf_ohne_fehler_ist_gueltig_und_haelt_das_spiel_nie_an():
    g, l, e = ganzer_lauf()
    assert e["gueltig"], e
    assert (
        e["arten_fehlen"] == []
        and e["offene_arbeitsplaetze"] == 0
        and e["jahreswechsel"] >= 1
        and e["treppe"] == "bestaetigt"
    )
    assert l.funde == [], l.funde
    flach = [c for x in g.log for c in (x if isinstance(x, list) else [x])]
    assert not any(c.get("pause") is True or "tickpause" in c for c in flach)
    # Gerechnet in Takten: Ein Jahr auf Tempo 40 sind 9.600 Takte, streng aufgezeichnet
    assert ("jahr40", lf.TEMPO_JEDER_TAKT, True) in g.gestartet
    jahr = next(x for x in g.protokoll if x.get("abschnitt") == "jahr_tempo40" and "daten" in x)
    assert lf.JAHR <= jahr["takt_bis"] - jahr["takt_von"] <= lf.JAHR + 60
    # Die Frist reicht: virtuelle Dauer des ganzen Laufs unter 10 Minuten
    assert g.jetzt < lf.FRIST


def test_alle_bauten_haben_den_wert_des_mausklicks():
    g, _, _ = ganzer_lauf()
    werte = {
        c["baue"]["mapper"]: c["baue"]["richtung"]
        for x in g.log
        for c in (x if isinstance(x, list) else [x])
        if "baue" in c
    }
    assert werte[147] == 0x50 and werte[145] == 0x50
    assert all(v == 15 for m, v in werte.items() if m not in (147, 145))
    assert g.bits, "Mauer und Graben gesetzt"


def test_pechgrube_ohne_boden_ist_kein_abbruch_und_steht_in_der_liste():
    _, l, e = ganzer_lauf()
    assert l.keine_stelle == [lf.PECHGRUBE] and e["gueltig"]


@pytest.mark.parametrize(
    "fehler, text",
    [
        ({"gold_kommt_nicht": True}, "Gold kam nicht an"),
        ({"huette_ohne_platz": True}, "Wohnplaetze"),
        ({"anzeige_bleibt": True}, "Anzeige 20 bleibt"),
        ({"woche_steht": True}, "Kalender zaehlt nicht"),
        ({"waren_haengen": True}, "Waren kommen"),
        ({"bau_scheitert": lf.KORN}, "kein Gebaeude"),
        ({"bau_scheitert": 12}, "kein Gebaeude"),
        ({"keine_stelle": 12}, "keine vom Spiel erlaubte Stelle"),
        ({"kein_bewohner": True}, "kein neuer Bewohner"),
        ({"beliebtheit_faellt": True}, "Beliebtheit"),
        ({"stillstand_bei": 3000}, "kein neuer Takt"),
        ({"spiel_weg_bei": 3000}, "Spiel laeuft nicht mehr"),
        ({"rekorder_tot_bei": 3000}, "Aufzeichnung"),
        ({"bremse": 1}, "bremst"),
    ],
)
def test_jeder_abbruchgrund_beendet_den_lauf_mit_seinem_namen(fehler, text):
    g = KunstSpiel(**fehler)
    with pytest.raises(lf.Abbruch, match=text):
        lf.programm(lauf_von(g))


def test_bewohner_wache_nur_solange_arbeit_offen_ist_und_nur_bis_zum_ende_der_bauern(monkeypatch):
    offen = [3]
    monkeypatch.setattr(lf, "offene_plaetze", lambda l: offen[0])
    g = KunstSpiel()
    g.pop, g.deckel, g.feuer = 5, 58, 0
    l = lauf_von(g)
    l.lage_pruefen(g.t)
    l.bewohner_wache = False
    l.lage_pruefen(
        g.t + lf.KEIN_BEWOHNER + 1
    )  # Steuertest und Anwerben aendern die Lage: kein Abbruch
    l.bewohner_wache = True
    offen[0] = 0
    l.lage_pruefen(
        g.t + 2 * lf.KEIN_BEWOHNER + 2
    )  # alle Plaetze besetzt: Zuzug ist nicht mehr noetig
    offen[0] = 3
    with pytest.raises(lf.Abbruch, match="kein neuer Bewohner"):
        l.lage_pruefen(g.t + 3 * lf.KEIN_BEWOHNER + 3)


def test_nach_den_bauern_ist_die_bewohner_wache_aus():
    g, l, e = ganzer_lauf()
    assert l.bewohner_wache is False and e["gueltig"]


def test_gold_darf_kurz_brauchen():
    g = KunstSpiel(gold_kommt_nicht=True)
    l = lauf_von(g)
    alt = g.befehl

    def spaet(cmd, warte=0.8, bis=None):
        alt(cmd, warte, bis)
        if "gold" in cmd:
            g.warte.append((g.t + 10, {"_gold": cmd["gold"]}))
        return []

    g.befehl = spaet
    baue = g._baue

    def _baue(b):
        if "_gold" in b:
            g.best[15] = b["_gold"]
        else:
            baue(b)

    g._baue = _baue
    lf.abschnitt_grundstock(l)
    assert g.best[15] >= lf.GOLD - 1000


def test_die_geplanten_waren_passen_in_ihre_lager():
    assert sum(lf.WAFFEN_WAREN.values()) <= lf.WAFFENLAGER_FASST
    assert (
        sum(lf.ESSEN.values()) + 20 <= 250
    )  # der Kornspeicher fasst 250, die Karte bringt 20 Aepfel


def test_zu_viele_waffen_haengen_und_beenden_den_lauf(monkeypatch):
    monkeypatch.setattr(lf, "WAFFEN_WAREN", {w: 20 for w in range(17, 25)})
    with pytest.raises(lf.Abbruch, match="Waren kommen"):
        lf.programm(lauf_von(KunstSpiel()))


def test_handel_testet_jede_ware_und_laesst_waffen_und_platz_zum_anwerben():
    g = KunstSpiel()
    l = lauf_von(g)
    for w in lf.HANDELSWAREN:
        g.best[w] = lf.WAFFEN_WAREN.get(w, 50)
    g.best[15] = lf.GOLD
    lf._handel(l)
    assert l.funde == [], l.funde
    kaufen = next(e for e in g.protokoll if e.get("wirkung") == "kaufen")
    verkaufen = next(e for e in g.protokoll if e.get("wirkung") == "verkaufen")
    assert kaufen["ohne_zuwachs"] == [] and verkaufen["ohne_abgang"] == [], (
        "jede Ware einmal gehandelt"
    )
    voll = next(e for e in g.protokoll if e.get("messung"))
    assert voll["speer"][0] == voll["speer"][1] and voll["fail_state"] == 10, (
        "der Kauf beim vollen Lager wird abgelehnt"
    )
    assert g.best[17:25] == [lf.WAFFEN_WAREN[w] for w in range(17, 25)], (
        "Waffen wie vorher, Platz fuer die Schmieden"
    )


def test_handel_laesst_auch_bei_fast_vollem_waffenlager_die_geplanten_speere():
    g = KunstSpiel()
    l = lauf_von(g)
    for w in lf.HANDELSWAREN:
        g.best[w] = lf.WAFFEN_WAREN.get(w, 50)
    g.best[17] += (
        lf.LOS
    )  # die Bogner haben schon abgeliefert: Fuer die Speere ist nur noch ein Los frei
    lf._handel(l)
    assert g.best[lf.SPEER] == lf.WAFFEN_WAREN[lf.SPEER]


def test_tor_zustand_12_ist_kein_fund():
    g, l, e = ganzer_lauf(tor_wird_fertig=True)
    assert not [f for f in l.funde if f["was"].startswith("Tor")], l.funde


def test_deckel_darf_zucken():
    g, l, e = ganzer_lauf(deckel_zuckt=True)
    assert e["gueltig"], e


def test_zusatzbau_und_zweite_kaserne_sind_keine_grundlage():
    g, l, e = ganzer_lauf(zweiter_bau_scheitert=True)
    was = {f["was"] for f in l.funde}
    assert e["gueltig"], e
    assert {
        f"Zusatzbau Art {t}" for t in lf.ZUSATZ
    } <= was and "zweite Kaserne ersetzt die erste" in was, was


def test_frist_und_handstopp_beenden_den_lauf():
    g = KunstSpiel()
    with pytest.raises(lf.Abbruch, match="Frist"):
        lf.programm(lauf_von(g, frist=20))
    g = KunstSpiel()
    with pytest.raises(lf.Abbruch, match="von Hand"):
        lf.programm(lauf_von(g, stop=lambda: g.t > 2000))


def test_stillstand_auf_tempo_1_ist_zehn_takte_lang():
    l = lauf_von(KunstSpiel())
    l.tempo = 1
    assert l.stillstand_grenze() == 10.0
    l.tempo = 1000
    assert l.stillstand_grenze() == lf.STILLSTAND


def test_einzelner_ruckler_in_der_bremsprobe_ist_kein_abbruch():
    g = KunstSpiel(bremse=1, bremse_nur_einmal=True)
    l = lauf_von(g)
    lf.tempo_setzen(g, 1000)
    lf.bremsprobe(l, "Test")
    versuche = [e for e in g.protokoll if e.get("bremsprobe")]
    assert [e["ergebnis"] for e in versuche][-1] == "bestaetigt" and len(versuche) == 2


def test_schaltung_ohne_wirkung_ist_ein_fund_und_kein_abbruch():
    g, l, e = ganzer_lauf(steuer_wirkt_nicht=True)
    assert e["gueltig"]
    assert any(f["was"] == "Steuern" for f in l.funde)


def test_beliebtheit_im_steuertest_zaehlt_nicht_und_danach_wieder():
    g, l, e = ganzer_lauf(beliebtheit_im_steuertest=True)
    assert e["gueltig"], e
    g = KunstSpiel()
    l = lauf_von(g)
    l.lage_an = True
    g.bel = 4000
    with pytest.raises(lf.Abbruch, match="Beliebtheit"):
        l.lage_pruefen(g.t)
    l.beliebtheit_frei = True
    l.lage_pruefen(g.t)


def test_essen_wird_nachgeliefert_und_steht_im_protokoll():
    g = KunstSpiel(kein_essen=True)
    l = lauf_von(g)
    l.lage_pruefen(g.t)
    assert g.start[13] == 20 + lf.ESSEN_NACH
    assert any(e.get("eingang") == {"13": lf.ESSEN_NACH} for e in g.protokoll)
    l.lage_pruefen(g.t + 1)
    assert g.start[13] == 20 + lf.ESSEN_NACH, "nicht in jeder Runde"


def test_warenketten_enden_am_gemessenen_ende_und_spaetestens_nach_zwei_jahren():
    g = KunstSpiel()
    l = lauf_von(g)
    d = lf.abschnitt_ketten(l)
    assert d["gemessenes_ende"] and lf.JAHR <= d["takte"] < lf.JAHR + 3 * lf.BREMS_TAKTE + 100
    g = KunstSpiel(neue_felder_bis=10**9)
    d = lf.abschnitt_ketten(lauf_von(g))
    assert not d["gemessenes_ende"] and d["takte"] >= 2 * lf.JAHR


def test_treppe_misst_jede_stufe_ohne_mit_ohne_in_takten():
    g = KunstSpiel()
    d = lf.abschnitt_treppe(lauf_von(g))
    z = d["zeilen"]
    assert [x["tempo"] for x in z] == list(lf.STUFEN)
    assert [x["soll"] for x in z] == [20, 100, 1000, 1000, 1000, 1000, 1000]
    assert d["ergebnis"] == "bestaetigt"
    assert not any("pause" in c and "tempo" in c for c in g.log if isinstance(c, dict))


def test_treppe_bricht_ab_wenn_das_tempo_nicht_wirkt():
    class Falsch(KunstSpiel):
        def _cmd(self, c):
            if "tempo" in c:
                self.tempo = 200  # das Spiel bleibt auf 200, wie im Lauf 18:16
                return
            super()._cmd(c)

    with pytest.raises(lf.Abbruch, match="wirkt nicht"):
        lf.abschnitt_treppe(lauf_von(Falsch()))


def test_schluss_nennt_jeden_grund_fuer_ungueltig():
    g, l, e = ganzer_lauf()
    start = (g.jahr - 1, 0, 0)
    assert lf.schluss(l, start)["gueltig"]
    l.ergebnis["jahr40"] = {"fehlend": 1, "gemischt": 0}
    assert not lf.schluss(l, start)["gueltig"]
    l.ergebnis["jahr40"] = {"fehlend": 0, "gemischt": 0}
    assert not lf.schluss(l, (g.jahr, 0, 0))["gueltig"]
    n = next(iter(g.gebaeude_von(33)))["nr"]
    for x in g.gebaeude_von(33):
        del g.geb[x["nr"]]
    r = lf.schluss(l, start)
    assert not r["gueltig"] and 33 in r["arten_fehlen"] and n


def test_anhalten_prueft_ob_der_takt_wirklich_steht():
    class Kanal2:
        def __init__(self):
            self.log = []

        def befehl(self, c, warte=0.8, bis=None):
            self.log.append(c)

    class Stur:
        n = 0

        def takt(self):
            Stur.n += 1
            return Stur.n

    k = Kanal2()
    assert lf.anhalten_und_pruefen(k, Stur(), ruhe=ohne_warten)[0] is False
    assert len(k.log) == 3

    class Steht:
        def takt(self):
            return 5

    assert lf.anhalten_und_pruefen(Kanal2(), Steht(), ruhe=ohne_warten) == (True, 5)


# --- los ohne Spiel: Reihenfolge von Start und Ende, vor allem Anhalten und Sperre ---
def los_ohne_spiel(
    monkeypatch,
    tmp_path,
    programm=lambda l: None,
    steht=True,
    sicherung=None,
    log=("", ""),
    beenden=None,
    menueweg=None,
):
    from selfaware.tools.analysis import auge_ergebnis, auge_feldkarte
    from selfaware.tools.experiments import auge_aufzeichnung as aa

    ablauf = []
    monkeypatch.setenv("SHC_INSTANZ", "2")
    spiel = tmp_path / "spiel"
    spiel.mkdir()
    logdatei = spiel / "ucp3.log"
    logdatei.write_text(log[0], encoding="utf-8")

    def einspielen(ziel, quelle, stempel):
        ablauf.append("logik")
        with open(logdatei, "a", encoding="utf-8") as f:
            f.write(log[1])
        return sicherung

    class Kanal2:
        def befehl(self, c, warte=0.8, bis=None):
            ablauf.append(c)
            return []

    class Sp:
        def __init__(self, q):
            pass

        def takt(self):
            return 1

        def kalender(self):
            return (1196, 0, 0)

        def startwaren(self):
            return []

    class Rek:
        def __init__(self, *a):
            pass

        def starten(self, name, tempo, streng=False, felder=False):
            ablauf.append("aufzeichnung")

        def laeuft(self):
            return True

        def beenden(self):
            ablauf.append("aufzeichnung_beendet")
            if beenden:
                raise beenden
            return {}

    def menue(k):
        ablauf.append("burgenbau")
        return menueweg(k) if menueweg else {}

    for name, wert in (
        ("pruefen", lambda n, laeuft_schon=False: []),
        ("sperre_holen", lambda was: ablauf.append("sperre_holen")),
        ("sperre_freigeben", lambda: ablauf.append("sperre_frei")),
        ("ordner", lambda n: str(spiel)),
        ("logik_einspielen", einspielen),
        ("modul_eintragen", lambda *a: None),
        ("EchterKanal", Kanal2),
        ("warte_auf_modul", lambda k: None),
        ("Speicher", Sp),
        ("Rekorder", Rek),
        ("burgenbau_starten", menue),
        ("tempo_setzen", lambda k, s: ablauf.append(f"tempo {s}")),
        ("Lauf", lambda *a, **kw: "lauf"),
        ("programm", lambda l: (ablauf.append("programm"), programm(l))),
        ("schluss", lambda l, st: {"gueltig": True}),
        ("anhalten_und_pruefen", lambda k, s: (ablauf.append("anhalten"), (steht, 1))[1]),
    ):
        monkeypatch.setattr(lf, name, wert)
    monkeypatch.setattr(aa, "ProzessQuelle", lambda pid: None)
    monkeypatch.setattr(aa, "pid_der_instanz", lambda n: 1)
    monkeypatch.setattr(aa, "standard_bereiche", lambda karte: [])
    monkeypatch.setattr(
        auge_feldkarte.Feldkarte, "laden", staticmethod(lambda feldliste=None: None)
    )
    monkeypatch.setattr(
        auge_ergebnis, "auswerten", lambda basis, e: ablauf.append(("auswertung", e)) or "bericht"
    )
    return ablauf


def protokoll_von(ziel):
    with open(glob.glob(os.path.join(ziel, "lauf_f_*.protokoll.jsonl"))[0], encoding="utf-8") as f:
        return [json.loads(z) for z in f]


@braucht_instanz2
def test_los_reihenfolge_schalter_vor_dem_start_anhalten_vor_der_aufzeichnung_sperre_danach(
    monkeypatch, tmp_path
):
    ablauf = los_ohne_spiel(monkeypatch, tmp_path)
    assert lf.los(2, ziel=str(tmp_path), laeuft_schon=True) == {"gueltig": True}
    assert ablauf == [
        "sperre_holen",
        "logik",
        {"tickpause": "aus"},
        {"ladepause": "aus"},
        "burgenbau",
        f"tempo {lf.TEMPO_LAUF}",
        "aufzeichnung",
        "programm",
        "anhalten",
        "aufzeichnung_beendet",
        "sperre_frei",
        ("auswertung", {"gueltig": True}),
    ]


@braucht_instanz2
def test_los_abbruch_haelt_an_gibt_frei_und_wertet_aus(monkeypatch, tmp_path):
    def kaputt(l):
        raise lf.Abbruch("Kalender zaehlt nicht")

    ablauf = los_ohne_spiel(monkeypatch, tmp_path, programm=kaputt)
    e = lf.los(2, ziel=str(tmp_path), laeuft_schon=True)
    assert e == {"gueltig": False, "abbruch": "Kalender zaehlt nicht"}
    assert ablauf[-4:] == ["anhalten", "aufzeichnung_beendet", "sperre_frei", ("auswertung", e)]
    assert any(z.get("schritt") == "abbruch" for z in protokoll_von(str(tmp_path)))


@braucht_instanz2
def test_los_takt_steht_nicht_die_sperre_bleibt(monkeypatch, tmp_path):
    ablauf = los_ohne_spiel(monkeypatch, tmp_path, steht=False)
    lf.los(2, ziel=str(tmp_path), laeuft_schon=True)
    assert "sperre_frei" not in ablauf
    assert any(z.get("schritt") == "sperre_bleibt" for z in protokoll_von(str(tmp_path)))


@braucht_instanz2
def test_los_aufzeichnung_laesst_sich_nicht_beenden_das_spiel_steht_trotzdem(monkeypatch, tmp_path):
    ablauf = los_ohne_spiel(monkeypatch, tmp_path, beenden=OSError("weg"))
    with pytest.raises(OSError):
        lf.los(2, ziel=str(tmp_path), laeuft_schon=True)
    assert ablauf.index("anhalten") < ablauf.index("aufzeichnung_beendet")
    assert "sperre_frei" not in ablauf


@braucht_instanz2
def test_los_menueweg_scheitert_das_spiel_wird_angehalten_und_die_sperre_frei(
    monkeypatch, tmp_path
):
    def nein(k):
        raise lf.Fehler("Hauptmenue nicht erreicht")

    ablauf = los_ohne_spiel(monkeypatch, tmp_path, menueweg=nein)
    with pytest.raises(lf.Fehler, match="Hauptmenue"):
        lf.los(2, ziel=str(tmp_path), laeuft_schon=True)
    assert ablauf[-3:] == ["anhalten", "aufzeichnung_beendet", "sperre_frei"]


@braucht_instanz2
def test_los_wartet_aufs_nachladen_nur_mit_neuer_logik_und_nur_auf_eine_neue_zeile(
    monkeypatch, tmp_path
):
    zeile = "logik.lua neu geladen\n"
    a = tmp_path / "a"
    a.mkdir()
    ablauf = los_ohne_spiel(monkeypatch, a, sicherung="alt.lua", log=("", zeile))
    assert lf.los(2, ziel=str(a), laeuft_schon=True) == {"gueltig": True}
    assert "programm" in ablauf

    echt = lf.warte_auf
    zaehler = itertools.count()
    b = tmp_path / "b"
    b.mkdir()
    ablauf = los_ohne_spiel(
        monkeypatch, b, sicherung="alt.lua", log=(zeile, "")
    )  # die Zeile stammt von frueher, das Modul hat nicht nachgeladen
    monkeypatch.setattr(
        lf,
        "warte_auf",
        lambda f, s, was, **kw: echt(f, s, was, uhr=lambda: next(zaehler), ruhe=ohne_warten),
    )
    with pytest.raises(lf.Fehler, match="nachgeladen"):
        lf.los(2, ziel=str(b), laeuft_schon=True)
    assert "programm" not in ablauf


def test_stellensuche_nimmt_die_naechste_erlaubte_und_laesst_versuchte_aus():
    z = ["..+..", ".....", "+...+"]
    assert lf.naechste(z, 10, 20, (14, 22)) == (14, 22)
    assert lf.naechste(z, 10, 20, (14, 22), ausser=[(14, 22)]) == (12, 20)
    assert lf.naechste(["..."], 0, 0, (0, 0)) is None


def test_spirale_ist_innen_zuerst_und_auf_der_karte():
    s = lf.spirale((200, 200), 10, 12)
    assert len(s) == len(set(s)) == 12
    assert all(max(abs(x - 200), abs(y - 200)) == 10 for x, y in s[:8])
    assert all(8 <= x <= 391 and 8 <= y <= 391 for x, y in lf.spirale((5, 390), 10, 50))


def test_freier_streifen_findet_ein_ganz_freies_rechteck():
    z = ["+++.", "++++", "++++"]
    assert lf.freier_streifen(z, 7, 9, 4, 2) == (7, 10)
    assert lf.freier_streifen(z, 0, 0, 5, 1) is None


class RohSpeicher:
    """Rohspeicher nach Adressen, wie ihn der Lauf aus dem Prozess liest."""

    def __init__(self):
        self.m = {}

    def block(self, adr, laenge):
        self.m[adr] = bytearray(laenge)
        return self.m[adr]

    def lies(self, adr, n):
        for a, b in self.m.items():
            if a <= adr and adr + n <= a + len(b):
                return bytes(b[adr - a : adr - a + n])
        raise OSError(adr)


def test_speicher_liest_gebaeude_einheiten_anzeige_und_karte_an_den_richtigen_stellen():
    q = RohSpeicher()
    g = q.block(lf.GEBAEUDE, lf.G_SCHRITT * lf.G_ANZAHL)
    b = 3 * lf.G_SCHRITT
    for o, w in (
        (lf.G_ZUSTAND, 2),
        (lf.G_TYP, 19),
        (lf.G_BESITZER, 1),
        (lf.G_X, 205),
        (lf.G_Y, 181),
        (lf.G_BILDWERT, 15),
        (lf.G_OFFEN, 2),
    ):
        struct.pack_into("<h", g, b + o, w)
    struct.pack_into("<i", g, b + lf.G_UID, 99)
    g[b + lf.G_TOR] = 11
    for nr, z, sp in ((4, 3, 1), (5, 2, 2)):  # abgerissen, fremd
        struct.pack_into("<h", g, nr * lf.G_SCHRITT + lf.G_ZUSTAND, z)
        struct.pack_into("<h", g, nr * lf.G_SCHRITT + lf.G_BESITZER, sp)
    s = lf.Speicher(q)
    assert s.gebaeude() == [
        {"nr": 3, "typ": 19, "x": 205, "y": 181, "v": 15, "offen": 2, "uid": 99, "tor": 11}
    ]
    assert [e["nr"] for e in s.gebaeude(sp=None)] == [3, 5]
    struct.pack_into("<I", q.block(lf.ANZEIGEN, 4), 0, 0x9000)
    d = q.block(0x9000, 0x60)
    struct.pack_into("<iiI", d, 8, 7, 0, 0)
    struct.pack_into("<I", d, 0x20, 0x9030)
    struct.pack_into("<ii", d, 0x30 + 8, lf.ANZEIGE_BURG_KORN, 2)
    assert s.anzeige_burg_korn() == 2
    e = q.block(lf.EINHEITEN, lf.E_SCHRITT * 5)
    struct.pack_into("<i", q.block(lf.EINHEITEN_ANZAHL, 4), 0, 5)
    for nr, typ, sp in ((1, 22, 1), (2, 22, 1), (3, 70, 2)):
        struct.pack_into("<h", e, nr * lf.E_SCHRITT + lf.E_DA, 1)
        struct.pack_into("<h", e, nr * lf.E_SCHRITT + lf.E_TYP, typ)
        struct.pack_into("<h", e, nr * lf.E_SCHRITT + lf.E_BESITZER, sp)
    assert s.einheiten() == {22: 2}
    z = q.block(lf.ZEILEN, 400 * 12)
    struct.pack_into("<i", z, 2 * 12 + 8, 100)
    lg = q.block(lf.LOGIK, 4 * lf.KACHELN)
    struct.pack_into("<I", lg, (100 + 3) * 4, lf.BIT_GRABEN)
    assert s.logik(3, 2) == lf.BIT_GRABEN
    ma = q.block(lf.KARTENMASKE, 400 * 400)
    ma[2 * 400 + 3] = 1
    assert s.felder_mit_bit(lf.BIT_GRABEN) == [(3, 2)]


def test_feste_adressen_passen_zum_export():
    from selfaware.tools.analysis.auge_feldkarte import EXPORT, Feldkarte

    if not os.path.exists(os.path.join(EXPORT, "types.json")):
        pytest.skip("Export fehlt")
    assert lf.adressen_gegen_karte(Feldkarte.laden()) == []
