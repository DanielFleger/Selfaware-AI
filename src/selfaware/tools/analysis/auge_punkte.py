# -*- coding: utf-8 -*-
"""B-142: Beleg je Einzelpunkt der Checkliste aus den Aufzeichnungen eines Laufs.

Jeder Punkt nennt Felder im Text. Das Werkzeug sucht sie in der Feldkarte, liest aus der Aufzeichnung, ob und wie sie sich aendern, und schreibt
den Beleg zum Punkt. Ein Urteil faellt es nur, wo es sich rechnen laesst:
  gemessen          Tabelle oder Wert einmal abgelesen, Beleg steht dabei
  bestaetigt        die erwartete Zahl kommt im Feld vor
  widerlegt         das Feld aendert sich, die erwartete Zahl kommt nie vor
  gesehen           das Feld aendert sich, ob das der Erwartung entspricht, muss jemand lesen
  nicht gesehen     das Feld aendert sich im Lauf nie
  nicht zuordenbar  im Text ist kein Feld zu erkennen
"bestaetigt" heisst nur: Die Zahl kam vor. Die Lage kann eine andere gewesen sein, darum ist auch das ein Vorschlag, den jemand gegenliest.
"""
import collections
import dataclasses
import json
import re
import struct

from selfaware.tools.analysis.auge_auswertung import GROSSER_BEREICH, VOLL, Bytekarte, felder_der_teile
from selfaware.tools.analysis.auge_feldkarte import ARRAY

ABSCHNITTE = {"### Lauf F, Start": True, "### Lauf F: Burgenbau": False}
ZEILE = re.compile(r"- \[ \] (P\d+) `([^`]+)` \((0x[0-9a-fA-F]+)\): (.*)")
FELDTEIL = re.compile(r"\*\*Lage:\*\* (.*?)(?: · \*\*Messen:\*\* (.*?))?(?: · \*\*Erwartet:\*\* (.*))?$")
SPIELART = " **[Spielart]**"
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\[[^\]]*\])?(?:\.[A-Za-z_][A-Za-z0-9_]*(?:\[[^\]]*\])?)*")
BEHAELTER = {"buildings": "buildings[]", "playerDataArray": "playerDataArray[]", "units": "units[]", "tribes": "tribes[]", "mapAndTime": "mapAndTime", "moats": "moats[]", "pitchDitches": "pitchDitches[]", "finalResults": "finalResults"}
ZU_ALLGEMEIN = {"state", "count", "resources", "uid", "x", "y", "id", "type", "health", "owner", "stage"}
WARENWOERTER = re.compile(r"\b(Gold|Holz|Stein|Eisen|Pech|Bestand|Bestände|Warenbestand|Steinbestand|Pechbestand|Holzbestand|Eisenbestand|Waffenbestand|Weizen|Mehl|Brot|Hopfen|Bier|Ale)\w*", re.I)
GRENZE_WERTE = 40


@dataclasses.dataclass
class Punkt:
    nr: str
    funktion: str
    adresse: str
    start: bool
    lage: str = ""
    messen: str = ""
    erwartet: str = ""
    schaerfen: str = ""
    spielart: bool = False

    @property
    def text(self):
        return " ".join((self.lage, self.messen, self.schaerfen))


def punkte_lesen(pfad, lauf="F"):
    aus, start = [], None
    abschnitte = ABSCHNITTE if lauf == "F" else {f"### Lauf {lauf}": False}
    for z in open(pfad, encoding="utf-8"):
        z = z.rstrip("\n")
        if z.startswith("### "):
            start = next((v for k, v in abschnitte.items() if z.startswith(k)), None)
            continue
        if start is None:
            continue
        m = ZEILE.match(z)
        if not m:
            continue
        rest = m.group(4)
        spielart = rest.endswith(SPIELART)
        if spielart:
            rest = rest[:-len(SPIELART)]
        p = Punkt(m.group(1), m.group(2), m.group(3), start, spielart=spielart)
        f = FELDTEIL.match(rest)
        if f:
            p.lage, p.messen, p.erwartet = f.group(1), f.group(2) or "", f.group(3) or ""
        else:
            p.schaerfen = rest.split(":** ", 1)[-1]
        aus.append(p)
    return aus


def feldindex(karte):
    """{Blattname: [(Global, Pfad, Adresse, Groesse, Schritt, Anzahl)]} ueber alle benannten Strukturen."""
    index = collections.defaultdict(list)

    def gehe(g, typ, pfad, adr, schritt, anzahl, tiefe):
        for o, tt, gr, na in karte.typen.get(typ, {}).get("felder", ()):
            m = ARRAY.match(tt)
            if m:
                el = m.group(1).strip()
                eg = karte.typen[el]["laenge"] if el in karte.typen else (gr // int(m.group(2)) or 1)
                s, a = (schritt, anzahl) if schritt else (eg, int(m.group(2)))
                p = f"{pfad}.{na}[]".lstrip(".")
                index[na].append((g, p, adr + o, eg, s, a, int(m.group(2))))
                if el in karte.typen and tiefe < 4:
                    gehe(g, el, p, adr + o, s, a, tiefe + 1)
            else:
                p = f"{pfad}.{na}".lstrip(".")
                index[na].append((g, p, adr + o, gr, schritt, anzahl, 1))
                if tt.strip() in karte.typen and tiefe < 4:
                    gehe(g, tt.strip(), p, adr + o, schritt, anzahl, tiefe + 1)

    for start, ende, name, typ in karte.strukturen:
        kurz = name[4:] if name.startswith("DAT_") else name
        index[kurz].append((name, "", start, ende - start, 0, 1, 1))
        gehe(name, typ, "", start, 0, 1, 0)
    return index


def felder_des_punkts(p, index):
    """Alle Felder, die der Text nennt. Mit Behaelter (buildings[id].x) eindeutig; ohne nur lange, seltene Namen."""
    gefunden = {}
    for t in TOKEN.findall(p.text):
        teile = [re.sub(r"\[.*\]", "", x) for x in t.split(".")]
        blatt = teile[-1]
        for kand in (blatt, blatt[4:] if blatt.startswith("DAT_") else "DAT_" + blatt):
            treffer = index.get(kand)
            if treffer:
                break
        if not treffer:
            continue
        if len(teile) > 1:
            behaelter = BEHAELTER.get(teile[0])
            auswahl = [f for f in treffer if behaelter and behaelter in f[1]] or [f for f in treffer if teile[0] in f[0] or teile[0] in f[1]]
        else:
            if blatt in ZU_ALLGEMEIN or len(blatt) < 5 or len(treffer) > 4:
                continue
            auswahl = treffer
        for f in auswahl[:4]:
            gefunden[(f[0], f[1])] = f
    if WARENWOERTER.search(p.text):
        for f in index.get("currentResources", ()):
            gefunden[(f[0], f[1])] = f
    return list(gefunden.values())


def _wert(p, o, gr):
    if gr == 4:
        return struct.unpack_from("<i", p, o)[0]
    if gr == 2:
        return struct.unpack_from("<h", p, o)[0]
    if gr == 1:
        return p[o]
    return None


class Belege:
    """Ein Durchgang durch die Aufzeichnungen: je gewuenschtem Feld Anfangswert, Aenderungen und vorkommende Werte."""

    def __init__(self, felder, karte):
        self.felder = {(f[0], f[1]): f for f in felder}
        self.karte = karte
        self.daten = {k: {"global": k[0], "feld": k[1], "aenderungen": 0, "werte": [], "mehr_werte": False, "min": None, "max": None, "erster_takt": None, "letzter_takt": None, "anfang": None} for k in self.felder}
        self._bytes = Bytekarte(karte)
        self._gewuenscht = {}
        self._liste = list(self.felder)
        self._nummer = {k: i for i, k in enumerate(self._liste)}

    def _merke(self, k, w, takt, aenderung):
        d = self.daten[k]
        if w is None:
            return
        d["min"] = w if d["min"] is None else min(d["min"], w)
        d["max"] = w if d["max"] is None else max(d["max"], w)
        if w not in d["werte"]:
            if len(d["werte"]) < GRENZE_WERTE:
                d["werte"].append(w)
            else:
                d["mehr_werte"] = True
        if aenderung:
            d["aenderungen"] += 1
            d["erster_takt"] = takt if d["erster_takt"] is None else d["erster_takt"]
            d["letzter_takt"] = takt

    def _element(self, k, f, adr_vergleich, basis, p, r, aenderung):
        g, pfad, adr, gr, schritt, anzahl, innen = f
        if gr not in (1, 2, 4):
            # eine ganze Tabelle oder ein Eintrag aus mehreren Feldern: Einmal gelesen genuegt, als Ganzzahlen
            if adr_vergleich is None and 0 <= adr - basis <= len(p) - min(gr, 64):
                for j in range(min(gr, 64) // 4):
                    self._merke(k, _wert(p, adr - basis + j * 4, 4), r.takt, False)
            return
        if schritt:
            if adr_vergleich is None:
                indizes = [1] if "playerDataArray" in pfad else range(min(anzahl, 8))
            else:
                a, b = adr_vergleich
                i0, i1 = max(0, (a - adr) // schritt), min(anzahl - 1, (b - 1 - adr) // schritt)
                indizes = [1] if "playerDataArray" in pfad and i0 <= 1 <= i1 else ([] if "playerDataArray" in pfad else range(i0, i1 + 1))
        else:
            indizes = [0]
        for i in indizes:
            for j in range(min(innen, 64)):
                o = adr + i * (schritt or 0) + j * gr - basis
                if 0 <= o <= len(p) - gr:
                    self._merke(k, _wert(p, o, gr), r.takt, aenderung)

    def _wunsch(self, basis, laenge):
        """Je Byte des Bereichs die Nummer des gewuenschten Felds, sonst -1."""
        import numpy as np

        w = self._gewuenscht.get(basis)
        if w is None:
            ids = self._bytes.bereich(basis, laenge)
            uebersetzung = np.fromiter((self._nummer.get(k, -1) for k in self._bytes.felder), dtype=np.int32, count=len(self._bytes.felder))
            w = self._gewuenscht[basis] = uebersetzung[ids]
        return w

    def lies(self, auf):
        haupt = {b[0] for b in auf.bereiche if b[0] != "datenblock"}
        for r, p, teile in auf.staende():
            name = auf.namen[r.bereich]
            basis, laenge = auf.bereiche[r.bereich][1], auf.bereiche[r.bereich][2]
            if r.art == VOLL:
                for k, f in self.felder.items():
                    if basis <= f[2] < basis + laenge and self.daten[k]["anfang"] is None:
                        vorher = len(self.daten[k]["werte"])
                        self._element(k, f, None, basis, p, r, False)
                        self.daten[k]["anfang"] = self.daten[k]["werte"][:8] if len(self.daten[k]["werte"]) > vorher else None
                continue
            if not teile:
                continue
            if laenge > GROSSER_BEREICH:
                for o, l in teile:
                    for fg, fp in self.karte.felder_einer_aenderung(basis + o, l):
                        if (fg, fp) in self.felder and not (name == "datenblock" and fg in haupt):
                            self._element((fg, fp), self.felder[(fg, fp)], (basis + o, basis + o + l), basis, p, r, True)
                continue
            nummern, stuecke, anfang, laengen = felder_der_teile(self._wunsch(basis, laenge), teile)
            gewuenscht = nummern >= 0
            for n, s in zip(nummern[gewuenscht].tolist(), stuecke[gewuenscht].tolist()):
                k = self._liste[n]
                o = int(anfang[s])
                self._element(k, self.felder[k], (basis + o, basis + o + int(laengen[s])), basis, p, r, True)


def urteil(p, belege):
    """(Urteil, Grund) aus den Belegen eines Punkts. Ob die Funktion stimmt, sagt das nicht: Das Werkzeug sieht Feldwerte, nicht die Lage des Punkts
    (Probe 02.11.2026: "Goldzuwachs je Takt 80" gegen den Goldbestand). Darum nur Hinweise; bestaetigt oder widerlegt schreibt erst, wer die Belege gelesen hat."""
    if not belege:
        return "nicht zuordenbar", "im Text ist kein Feld der Feldkarte zu erkennen"
    if p.start:
        return "gemessen", "einmal abgelesen" if any(b["werte"] for b in belege) else "kein Wert gelesen"
    geaendert = [b for b in belege if b["aenderungen"]]
    if not geaendert:
        return "nicht gesehen", "keines der genannten Felder aendert sich in diesem Lauf"
    m = re.fullmatch(r"\s*(-?\d+)\s*", p.erwartet or "")
    if m:
        zahl = int(m.group(1))
        if any(zahl in b["werte"] for b in belege):
            return "zahl passt", f"{zahl} kommt in einem der Felder vor, die Lage des Punkts ist ungeprueft"
        if not any(b["mehr_werte"] for b in belege):
            return "zahl weicht ab", f"{zahl} kommt in den gesehenen Werten nicht vor, die Lage des Punkts ist ungeprueft"
    return "gesehen", "Feld aendert sich, Urteil muss jemand lesen"


def auswerten(checkliste, aufzeichnungen, karte, lauf="F"):
    """aufzeichnungen: Liste von Aufzeichnung. Rueckgabe: je Punkt nr, funktion, urteil, grund, belege; dazu die Zaehlung."""
    punkte = punkte_lesen(checkliste, lauf)
    index = feldindex(karte)
    je_punkt = {p.nr: felder_des_punkts(p, index) for p in punkte}
    alle = {}
    for fs in je_punkt.values():
        for f in fs:
            alle[(f[0], f[1])] = f
    bel = Belege(list(alle.values()), karte)
    for auf in aufzeichnungen:
        bel.lies(auf)
    aus = []
    for p in punkte:
        b = [bel.daten[(f[0], f[1])] for f in je_punkt[p.nr]]
        u, g = urteil(p, b)
        aus.append({"nr": p.nr, "funktion": p.funktion, "start": p.start, "lage": p.lage or p.schaerfen, "messen": p.messen, "erwartet": p.erwartet, "spielart": p.spielart, "urteil": u, "grund": g, "belege": b})
    return {"punkte": aus, "zaehlung": dict(collections.Counter(a["urteil"] for a in aus))}


def bericht(ergebnis):
    z = ["| Urteil | Punkte |", "|---|---|"]
    for u, n in sorted(ergebnis["zaehlung"].items()):
        z.append(f"| {u} | {n} |")
    for titel, u in (("Zahl weicht ab (von Hand lesen)", "zahl weicht ab"), ("Nicht gesehen", "nicht gesehen"), ("Nicht zuordenbar", "nicht zuordenbar")):
        liste = [a for a in ergebnis["punkte"] if a["urteil"] == u]
        if liste:
            z += ["", f"**{titel}:** " + ", ".join(f"{a['nr']} {a['funktion']}" for a in liste[:60]) + (" ..." if len(liste) > 60 else "")]
    return "\n".join(z) + "\n"


def schreiben(ergebnis, pfad):
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(ergebnis, f, ensure_ascii=False, indent=0)
