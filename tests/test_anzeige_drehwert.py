# -*- coding: utf-8 -*-
"""B-144: Gebaeude muessen aus jedem Winkel normal aussehen. Bildwert beim Bauen und Reparatur alter Spielstaende."""
import os
import re
import struct

import pytest

from selfaware.game.ucp.drehwert import drehwert
from selfaware.tools.experiments import anzeige_reparieren as ar
from selfaware.tools.experiments import auge_lauf_f as lf

SRC = os.path.join(os.path.dirname(__file__), "..", "src", "selfaware")
BEWUSST_VARIABEL = {"eingang_messen.py", "streitkolben_messen.py", "haertetest.py"}  # messen den Eingang je Richtung, das Modul setzt trotzdem 15


def alle_quellen():
    for wurzel, _, dateien in os.walk(SRC):
        for d in dateien:
            if d.endswith(".py"):
                yield d, open(os.path.join(wurzel, d), encoding="utf-8").read()


def test_normale_gebaeude_haben_15_tore_die_werte_des_mausklicks():
    assert drehwert(54) == 15 and drehwert(61) == 15 and drehwert(114) == 15
    assert [drehwert(m) for m in (144, 145, 146, 147)] == [0x51, 0x50, 0x51, 0x50]
    assert [drehwert(m) for m in (140, 141, 142, 143)] == [0, 2, 4, 6]


def test_kein_bau_befehl_im_code_schickt_einen_festen_falschen_wert():
    treffer = []
    for name, text in alle_quellen():
        for z in text.splitlines():
            if '"baue"' not in z:
                continue
            m = re.search(r'"richtung":\s*([^}\s]+)', z)
            if m is None and '"mapper"' in z:
                treffer.append((name, "ohne Wert", z.strip()[:80]))
            elif m and m.group(1) not in ("15", 'drehwert(g["mapper"])', "drehwert(51)", "soll") and name not in BEWUSST_VARIABEL:
                treffer.append((name, m.group(1), z.strip()[:80]))
    assert treffer == []


def lua_datei(tmp_path, block=True):
    p = tmp_path / "quelle.lua"
    bau = f"    {lf.BAU_ALT}\r\n    log(INFO, x, {lf.BAU_LOG_ALT}\r\n      y)\r\n" if block else ""
    p.write_bytes(f"local H = {{\r\n      {lf.ANKER}\r\n}}\r\n{bau}".encode("latin-1"))
    return str(p)


def test_modul_setzt_bei_nicht_toren_immer_15_und_laesst_toren_ihren_wert(tmp_path):
    t = lf.logik_text(lua_datei(tmp_path))
    assert "b.richtung or 0" not in t
    assert "befehlAbsetzen(28, { b.x, b.y, b.mapper, b.groesse, drehung, b.trupp or 0 })" in t
    lupa = pytest.importorskip("lupa")
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    lua.execute("function befehlAbsetzen(nr, w) letzter = w[5]; return true end function log() end function tick() return 0 end INFO = 1 x = 1 y = 1")
    i = t.index("    -- B-144")
    koerper = t[i:t.index("    log(INFO, x,")]
    f = lua.eval("function(b) " + koerper + " end")
    for mapper, gegeben, erwartet in ((54, 0, 15), (54, None, 15), (54, 2, 15), (147, 0x50, 0x50), (145, None, 15), (105, 0, 0)):
        b = lua.table_from({"x": 1, "y": 1, "mapper": mapper, "groesse": 4})
        if gegeben is not None:
            b.richtung = gegeben
        f(b)
        assert lua.globals().letzter == erwartet, (mapper, gegeben)


def test_logik_text_ohne_bau_stelle_ist_ein_fehler(tmp_path):
    with pytest.raises(lf.Fehler):
        lf.logik_text(lua_datei(tmp_path, block=False))


def eintrag(typ, v, zustand=2, sp=1):
    roh = bytearray(ar.SCHRITT)
    struct.pack_into("<h", roh, ar.ZUSTAND, zustand)
    struct.pack_into("<h", roh, ar.TYP, typ)
    struct.pack_into("<h", roh, ar.BESITZER, sp)
    struct.pack_into("<h", roh, ar.BILDWERT, v)
    return bytes(roh)


def test_tabelle_lesen_und_nur_normale_arten_berichtigen():
    roh = bytes(ar.SCHRITT) + eintrag(1, 0) + eintrag(1, 15) + eintrag(12, 8) + eintrag(17, 6) + eintrag(45, 0) + eintrag(49, 0) + eintrag(78, 0) + eintrag(1, 0, zustand=0) + eintrag(2, 4)
    liste = ar.gebaeude_lesen(roh)
    assert [e["nr"] for e in liste] == [1, 2, 3, 4, 5, 6, 7, 9]
    assert [e["nr"] for e in ar.falsche(liste)] == [1, 7, 9]


def test_das_nachbarfeld_im_selben_wort_bleibt_erhalten():
    assert ar.neues_wort(0x00000000) == 15
    assert ar.neues_wort(0x0001FFFF) == 0x0001000F
    assert struct.pack("<i", ar.neues_wort(0xABCD0000)) == struct.pack("<I", 0xABCD000F)


def test_berichtigen_nur_im_angehaltenen_spiel_und_mit_nachkontrolle():
    class Quelle:
        def __init__(self, gebaeude, pause):
            self.roh, self.pause = bytearray(gebaeude + bytes(ar.SCHRITT * ar.ANZAHL - len(gebaeude))), pause

        def lies(self, adr, n):
            if adr == ar.PAUSE:
                return struct.pack("<i", self.pause)
            return bytes(self.roh[adr - ar.GEBAEUDE:adr - ar.GEBAEUDE + n])
    s = ar.Spiel.__new__(ar.Spiel)
    s.q = Quelle(bytes(ar.SCHRITT) + eintrag(1, 0), 0)
    s.befehl = lambda c, w=0: None
    with pytest.raises(RuntimeError):
        s.berichtigen()
    s.q = Quelle(bytes(ar.SCHRITT) + eintrag(1, 0), 1)
    with pytest.raises(RuntimeError):   # der Befehl wirkt nicht: Das darf nicht als geschafft durchgehen
        s.berichtigen()

    def poke(c, w=0):
        s.q.roh[c["poke"] - ar.GEBAEUDE:c["poke"] - ar.GEBAEUDE + 4] = struct.pack("<i", c["wert"])
    s.befehl = poke
    assert [e["nr"] for e in s.berichtigen()] == [1]
    assert ar.falsche(s.gebaeude()) == []
