# -*- coding: utf-8 -*-
"""B-142 Feldkarte: Speicheradresse <-> Feldname aus dem Ghidra-Export, ohne Spiel.

Die Feldliste data/research/auge_plan/zustand_felder.csv sagt, was das Spiel im Takt laut Code schreibt.
Der Aenderungsmelder ordnet damit jedes geaenderte Byte ein: bekannt, Technik (Darstellung, Ton, Menue) oder Luecke.
"""
import bisect
import csv
import json
import os
import re

EXPORT = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference"
FELDLISTE = os.path.join("data", "research", "auge_plan", "zustand_felder.csv")
DATEN_ANFANG, DATEN_ENDE = 0x005B6000, 0x0242923F
ZEILE = re.compile(r"^\s*(\d+)\s+(.+?)\s+(\d+)\s+(\S+)\s+\"")
ARRAY = re.compile(r"^(.+?)\[(\d+)\]")
ALIAS = {"DAT_GameState": "GameStateStructures", "SEC_RNG": "RNG"}
# Bereiche ohne Spielzustand; sie werden getrennt gezaehlt, nicht verschwiegen
TECHNIK = re.compile(r"Render|Viewport|Sound|SFX|Bink|Video|Menu|Text|Texture|Mouse|Input|Button|Bitmap|Blend|Font|Gfx|Graphic|Window|DirectDraw|DirectPlay|DirectSound|TIME_|Chat|DPLAY|Lobby")


def typen_lesen(ty):
    """Strukturen aus types.json; bei gleichem Namen gewinnt die groesste, sie ist die Spielstruktur."""
    typen = {}
    for t in ty:
        d = t.get("definition") or ""
        if "Structure " not in d:
            continue
        gl = []
        for l in d.splitlines():
            m = ZEILE.match(l)
            if m:
                gl.append((int(m.group(1)), m.group(2), int(m.group(3)), m.group(4)))
        na = t["path"].rsplit("/", 1)[-1]
        if na not in typen or t["length"] > typen[na]["laenge"]:
            typen[na] = {"laenge": t["length"], "felder": gl}
    return typen


class Feldkarte:
    def __init__(self, typen, strukturen, labels=None, bekannte=()):
        """strukturen: (start, ende, name, typ); labels: {adresse: name}; bekannte: (global, pfad) aus der Feldliste."""
        self.typen = typen
        # verschachtelte Bezeichner: die groesste umfassende Struktur gewinnt
        self.strukturen = []
        for g in sorted(strukturen, key=lambda g: (g[0], -(g[1] - g[0]))):
            if self.strukturen and g[1] <= self.strukturen[-1][1]:
                continue
            self.strukturen.append(g)
        self._anfaenge = [g[0] for g in self.strukturen]
        self.labels = labels or {}
        self._labs = sorted(self.labels)
        self.bekannte = set(bekannte)

    @classmethod
    def laden(cls, export=EXPORT, feldliste=None):
        ty = json.load(open(os.path.join(export, "types.json"), encoding="utf-8"))
        sy = json.load(open(os.path.join(export, "symbols.json"), encoding="utf-8"))
        typen = typen_lesen(ty)
        labels, strukturen = {}, []
        for s in sy:
            if s["kind"] == "Label" and s["source"] == "USER_DEFINED" and re.fullmatch(r"[0-9a-f]{8}", s["address"]):
                a = int(s["address"], 16)
                if DATEN_ANFANG <= a <= DATEN_ENDE:
                    labels.setdefault(a, s["name"])
        for a, n in labels.items():
            t = ALIAS.get(n, n[4:] if n.startswith("DAT_") else n)
            if t in typen:
                strukturen.append((a, a + typen[t]["laenge"], n, t))
        bekannte = []
        if feldliste and os.path.exists(feldliste):
            with open(feldliste, encoding="utf-8", newline="") as f:
                bekannte = [(z["global"], z["feld"]) for z in csv.DictReader(f, delimiter=";")]
        return cls(typen, strukturen, labels, bekannte)

    def _feld(self, typ, off):
        """(Pfad, Ende des Feldes relativ zur Struktur) fuer einen Versatz."""
        pfad, basis, ende = "", 0, off + 1
        while True:
            s = self.typen.get(typ)
            if not s:
                return pfad, ende
            for o, tt, gr, na in s["felder"]:
                if o <= off < o + gr:
                    m = ARRAY.match(tt)
                    if m:
                        el = m.group(1).strip()
                        eg = self.typen[el]["laenge"] if el in self.typen else (gr // int(m.group(2)) or 1)
                        i = (off - o) // eg
                        basis += o + i * eg
                        off = (off - o) % eg
                        ende = basis + eg
                        pfad, typ = f"{pfad}.{na}[]".lstrip("."), el
                    else:
                        basis += o
                        off -= o
                        ende = basis + gr
                        pfad, typ = f"{pfad}.{na}".lstrip("."), tt.strip()
                    break
            else:
                return f"{pfad}.+0x{off:x}".lstrip("."), basis + off + 1

    def ziel(self, adr):
        """(Globaler Name, Pfad) einer Adresse."""
        return self._ziel(adr)[:2]

    def _ziel(self, adr):
        i = bisect.bisect_right(self._anfaenge, adr) - 1
        if i >= 0 and adr < self.strukturen[i][1]:
            g = self.strukturen[i]
            p, e = self._feld(g[3], adr - g[0])
            return g[2], p, g[0] + e
        j = bisect.bisect_right(self._labs, adr) - 1
        if j >= 0 and adr - self._labs[j] < 4096:
            na = self.labels[self._labs[j]]
            return na, ("+0x%x" % (adr - self._labs[j]) if adr != self._labs[j] else ""), adr + 1
        return "ohne_Namen", "%08x" % adr, adr + 1

    def bekannt(self, g, p):
        """Genau gelistet, oder die Liste nennt ein uebergeordnetes Feld (ganzes Feld oder ganze Struktur geschrieben)."""
        if (g, p) in self.bekannte:
            return True
        t = p
        while "." in t:
            t = t.rsplit(".", 1)[0]
            if (g, t) in self.bekannte:
                return True
        return False

    def klasse(self, g, p):
        if self.bekannt(g, p):
            return "bekannt"
        if TECHNIK.search(g):
            return "technik"
        return "luecke"

    def felder_einer_aenderung(self, adr, laenge):
        """Alle Felder, die ein geaenderter Bytebereich beruehrt."""
        aus, z, ende = [], adr, adr + laenge
        while z < ende:
            g, p, e = self._ziel(z)
            aus.append((g, p))
            z = max(e, z + 1)
        return aus

    def struktur(self, name):
        for g in self.strukturen:
            if g[2] == name:
                return g
        raise KeyError(name)

    def adresse(self, g, pfad):
        """(Adresse, Groesse, Schritt, Anzahl) eines Feldes; bei Arrays Element 0, Schritt und Anzahl des aeussersten Arrays."""
        s = self.struktur(g)
        adr, typ, schritt, anzahl = s[0], s[3], 0, 1
        groesse = s[1] - s[0]
        for teil in pfad.split("."):
            na = teil.replace("[]", "")
            for o, tt, gr, n in self.typen[typ]["felder"]:
                if n == na:
                    adr += o
                    groesse = gr
                    m = ARRAY.match(tt)
                    if m:
                        el = m.group(1).strip()
                        eg = self.typen[el]["laenge"] if el in self.typen else (gr // int(m.group(2)) or 1)
                        if not schritt:
                            schritt, anzahl = eg, int(m.group(2))
                        groesse, typ = eg, el
                    else:
                        typ = tt.strip()
                    break
            else:
                raise KeyError(f"{g}.{pfad}: {na}")
        return adr, groesse, schritt, anzahl


if __name__ == "__main__":
    import sys
    karte = Feldkarte.laden(feldliste=FELDLISTE)
    print(len(karte.strukturen), "Strukturen,", len(karte.bekannte), "bekannte Felder")
    for a in sys.argv[1:]:
        z = karte.ziel(int(a, 16))
        print(a, z, karte.klasse(*z))
