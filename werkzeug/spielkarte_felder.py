# -*- coding: utf-8 -*-
"""Spielkarte Abschnitt 2 (B-95, 19.10.2026): welche Lagebild-Spalte welches Feld des Spiels ist.
Liest die Strukturen aus der OpenSHC-Referenz (daten/strukturen_kern.txt, werkzeug/ghidra/DumpStrukturen.java) und ordnet
jedem Abstand, den logik.lua liest, den Feldnamen zu. Prueft dabei die Lesebreite (readSmallInteger = 2 Byte, readInteger
= 4 Byte) gegen die Feldgroesse - eine Abweichung heisst: wir lesen halb oder ueber das Feld hinaus.
Einheiten: Feld = Abstand ab Unit-Anfang (Array UnitsState+0x614 = 0x0138854C, wie logik.lua).
Gebaeude:  logik.lua rechnet ab BuildingsState (0xF98520), das Array beginnt bei +0x14 - Feld = Abstand - 0x14.
Aufruf: python werkzeug/spielkarte_felder.py   (schreibt daten/spielkarte_felder.txt)"""
import os
import re

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HIER, "..", "daten")

# (Spalte im Lagebild, Abstand in logik.lua, Lesebreite)  - abgelesen logik_stand_20261019.lua, Befehl "lagebild"
EINHEIT = [("besitzer", 0x96, 2), ("typ", 0x8E, 2), ("x (Feinposition/8)", 0xB6, 2), ("y (Feinposition/8)", 0xB8, 2),
           ("leben", 968, 4), ("zustand", 704, 2), ("zielart", 924, 2), ("zieleinheit", 926, 2), ("zieluid", 928, 4),
           ("zielgebaeude", 822, 2), ("ziel", 782, 2), ("zielx", 784, 2), ("ziely", 786, 2), ("laufx", 0xC8, 2),
           ("laufy", 0xCA, 2), ("auswahlvon", 178, 2), ("auswahlmarke", 180, 2), ("gruppe", 728, 2), ("gruppenuid", 740, 4),
           ("ladung", 904, 2), ("arbeitsplatz", 824, 2), ("nahziel", 830, 2), ("nahangreifer", 942, 2),
           ("Filter 'lebt' (672 == 0)", 672, 2),
           ("Zustand-Existenz (0x8C)", 0x8C, 2), ("uid", 0x98, 4)]
GEBAEUDE = [("zustand (G_ZUSTAND)", 0xE4, 2), ("typ (G_TYP)", 0xE6, 2), ("besitzer (G_BESITZER)", 0xEA, 2),
            ("leben (G_LEBEN)", 0x120, 2), ("maxleben (G_MAXLEBEN)", 0x122, 2), ("x", 0x102, 2), ("y", 0x104, 2),
            ("groesse", 0x10C, 4), ("Feld 0x1A0", 0x1A0, 2), ("uid (Angriff 0xEC)", 0xEC, 4), ("Brandzeit (0x14+702)", 0x14 + 702, 2)]


# Feste Adressen, die unsere Werkzeuge lesen (logik.lua, erstes_spiel.py, samurai_wache.py) - Spieler-Felder fuer Spieler 2
PD2 = 0x0115BDF8 + 2 * 0x39F4
ADRESSEN = [("Ansicht (Menue/Gefecht)", 0x01FE7D1C), ("Pause", 0x01FEA054), ("Spielzeit in Takten (Lenker)", 0x0117CADC),
            ("Spielzeit in Takten (queueCommand)", 0x01FE7DA8), ("Partie vorbei", 0x0117D500), ("'ich'", 0x01A275DC),
            ("Ausloeser", 0x01A275D8), ("Spielart", 0x0191DD80), ("Mensch-Eintrag Spieler 2", 0x0191DE10 + 8),
            ("KI-Nummer Spieler 2", 0x0191DE7C + 8), ("Bauplatz-Pruefung Ergebnis", 0x01FE7B3C), ("Bauplatz-Pruefung Grund", 0x01FE7B40),
            ("Bau-Drehung", 0x01FE7BBC), ("Spieler 2: Beliebtheit", PD2 + 0x60), ("Spieler 2: Platz", PD2 + 116),
            ("Spieler 2: Feuer", PD2 + 136), ("Spieler 2: Leute", PD2 + 8576), ("Spieler 2: Essen (Beliebtheit)", PD2 + 0x2160),
            ("Spieler 2: KI-Art", PD2 + 0x2300), ("Spieler 2: Holz", PD2 + 0x4D0 + 2 * 4), ("Spieler 2: Gold", PD2 + 0x4D0 + 15 * 4)]
GLOBAL = [("DAT_GameState", 0x0112B0B8, "GameStateStructures"), ("DAT_GameCore", 0x01FE7D10, "GameCore"),
          ("DAT_TileMapState", 0x01A93208, "TileMapState"), ("DAT_GameSynchronyState", 0x0191D768, "GameSynchronyState"),
          ("DAT_UnitsState", 0x01387F38, "UnitsState"), ("DAT_BuildingsState", 0x00F98520, "BuildingsState")]
_STRUKTUREN = None


def alle_strukturen():
    global _STRUKTUREN
    if _STRUKTUREN is None:
        _STRUKTUREN = {}
        for datei in ("strukturen_kern.txt", "strukturen_global.txt"):
            name = None
            for z in open(os.path.join(D, datei), encoding="utf-8"):
                if z.startswith("### "):
                    name = z.split()[1]
                    _STRUKTUREN[name] = []
                    continue
                m = re.match(r"\s+\+0x([0-9A-F]+)\s+(\d+)\s+(\S+(?: \S+)?)\s+(\S+)\s*(.*)$", z)
                if name and m:
                    _STRUKTUREN[name].append((int(m.group(1), 16), int(m.group(2)), m.group(3), m.group(4), m.group(5).strip()))
    return _STRUKTUREN


def struktur(name):
    return alle_strukturen().get(name, [])


def aufloesen(name, ab, tiefe=0):
    """Abstand in Struktur `name` -> Pfad durch verschachtelte Strukturen und Felder."""
    f = feld(struktur(name), ab)
    if not f or tiefe > 5:
        return "(+0x%X nicht benannt)" % ab
    off, gr, typ, fname, kom = f
    rest = ab - off
    m = re.match(r"(\w+)\[(\d+)\](?:\[(\d+)\])?$", typ)
    if m and m.group(1) in alle_strukturen():
        el = gr // int(m.group(2))
        return "%s[%d].%s" % (fname, rest // el, aufloesen(m.group(1), rest % el, tiefe + 1))
    if m:
        el = gr // (int(m.group(2)) * (int(m.group(3)) if m.group(3) else 1))
        return "%s[%d]" % (fname, rest // el)
    if typ in alle_strukturen():
        return "%s.%s" % (fname, aufloesen(typ, rest, tiefe + 1))
    return fname + ("+%d" % rest if rest else "")


def feld(felder, ab):
    for off, gr, typ, name, kom in felder:
        if off <= ab < off + gr:
            return off, gr, typ, name, kom
    return None


def tabelle(titel, liste, felder, abzug=0):
    aus = ["## " + titel, "| Spalte | logik.lua | Feld im Spiel (OpenSHC) | Typ | Breite | Bemerkung |", "|---|---|---|---|---|---|"]
    warn = 0
    for spalte, ab, breite in liste:
        f = feld(felder, ab - abzug)
        if not f:
            aus.append("| %s | +0x%X | (nicht benannt) | - | %d | Abstand liegt in keinem benannten Feld |" % (spalte, ab, breite))
            continue
        off, gr, typ, name, kom = f
        bem = []
        if ab - abzug != off:
            bem.append("liest MITTEN im Feld (+%d)" % (ab - abzug - off))
        if breite != gr and not typ.endswith("]"):
            bem.append("Breite %d, Feld %d Byte" % (breite, gr))
            warn += 1
        if kom and "retype" not in kom:
            bem.append(kom[:70])
        aus.append("| %s | +0x%X | `%s` (+0x%X) | %s | %d | %s |" % (spalte, ab, name, off, typ, breite, "; ".join(bem)))
    return aus, warn


def main():
    t1, w1 = tabelle("Einheit (Unit, 1.168 Byte, Array 0x0138854C)", EINHEIT, struktur("Unit"))
    t2, w2 = tabelle("Gebaeude (Building, 812 Byte, Array BuildingsState+0x14 = 0xF98534)", GEBAEUDE, struktur("Building"), 0x14)
    t3 = ["## Feste Adressen unserer Werkzeuge", "| Bedeutung bei uns | Adresse | Feld im Spiel (OpenSHC) |", "|---|---|---|"]
    for text_a, adr in ADRESSEN:
        treffer =[(n, b, s) for n, b, s in GLOBAL if struktur(s) and b <= adr < b + struktur(s)[-1][0] + struktur(s)[-1][1]]
        pfad = "%s.%s" % (treffer[0][0], aufloesen(treffer[0][2], adr - treffer[0][1])) if treffer else "(in keiner bekannten Struktur)"
        t3.append("| %s | `0x%08X` | `%s` |" % (text_a, adr, pfad))
    text = "\n".join(t1 + [""] + t2 + [""] + t3) + "\n"
    open(os.path.join(D, "spielkarte_felder.txt"), "w", encoding="utf-8").write(text)
    print(text)
    print("Breiten-Abweichungen: %d" % (w1 + w2))


if __name__ == "__main__":
    main()
