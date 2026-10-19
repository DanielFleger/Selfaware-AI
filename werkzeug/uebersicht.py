# -*- coding: utf-8 -*-
"""MAKRO - die Uebersicht ueber alles (Daniel 19.10. 18:07: "es braucht eine Uebersicht ueber alles - was habe ich, was
haben die Gegner und wer davon was und wo").

Je Runde aus dem Lagebild (alle Einheiten der Karte):
  - je Spieler: Truppen nach Art, Arbeiter, Lord-Leben;
  - VERBAENDE: Truppen eines Spielers, die in einer Kette von hoechstens VERBAND_R Feldern stehen, mit Mitte, Arten,
    Leben, Bewegung (Felder je 100 Takte aus der Vorrunde) und Laufziel (das haeufigste der Mitglieder);
  - je Einheit: Bewegung seit der Vorrunde (steht / laeuft) - das braucht das Mikro ("holt ihn einer ein?").
Nur Lesen und Zusammenfassen - die Uebersicht befiehlt nichts. zeile() gibt eine Zeile fuer die Mitschrift (alle
ZEILE_RUNDEN Runden), damit man beim Zuschauen sieht, was die KI glaubt.
Pruefung ohne Spiel: werkzeug/uebersicht_pruefen.py."""
from collections import Counter

TRUPPE = {22, 23, 24, 25, 26, 27, 28, 55, 70, 71, 72, 73, 74, 75, 76}
LORD = 55
VERBAND_R = 8
STEHT_FELDER = 1          # weniger oder gleich so viele Felder seit der Vorrunde = steht
ZEILE_RUNDEN = 10
NAME = {22: "Bogen", 23: "Armbrust", 24: "Speer", 25: "Pike", 26: "Streitkolben", 27: "Schwert", 28: "Ritter", 55: "Lord",
        70: "arab.Bogen", 71: "Sklave", 72: "Schleuder", 73: "Assassine", 74: "Pferdebogen", 75: "arab.Schwert",
        76: "Feuerwerfer"}


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


class Uebersicht:
    def __init__(self, sp):
        self.sp = sp
        self.vorher = {}          # nr -> (t, x, y)
        self.weg = {}             # nr -> (Felder seit Vorrunde, Takte)
        self.verbaende = []
        self.spieler = {}
        self.t = None
        self.runden = 0

    def runde(self, t, L):
        self.t, self.runden = t, self.runden + 1
        self.weg = {}
        for n, e in L.items():
            v = self.vorher.get(n)
            if v and t > v[0]:
                self.weg[n] = (schach((e["x"], e["y"]), (v[1], v[2])), t - v[0])
        self.vorher = {n: (t, e["x"], e["y"]) for n, e in L.items() if e["typ"] in TRUPPE}
        self.spieler = {}
        for n, e in L.items():
            b = e["besitzer"]
            if b == 0:
                continue
            s = self.spieler.setdefault(b, {"truppen": Counter(), "arbeiter": 0, "lord": None})
            if e["typ"] == LORD:
                s["lord"] = (n, e["leben"], e["x"], e["y"])
            elif e["typ"] in TRUPPE:
                s["truppen"][e["typ"]] += 1
            else:
                s["arbeiter"] += 1
        self.verbaende = self._verbaende(L)
        return self

    def steht(self, nr, L=None):
        """True = hoechstens STEHT_FELDER Felder seit der Vorrunde, False = laeuft, None = keine Vorrunde."""
        w = self.weg.get(nr)
        if w is None:
            return None
        return w[0] <= STEHT_FELDER

    def _verbaende(self, L):
        tr = {n: e for n, e in L.items() if e["besitzer"] != 0 and e["typ"] in TRUPPE and e["typ"] != LORD}
        frei, aus = set(tr), []
        while frei:
            s = frei.pop()
            g, offen = {s}, [s]
            while offen:
                k = offen.pop()
                for n in list(frei):
                    if tr[n]["besitzer"] == tr[k]["besitzer"] and \
                            schach((tr[n]["x"], tr[n]["y"]), (tr[k]["x"], tr[k]["y"])) <= VERBAND_R:
                        frei.discard(n); g.add(n); offen.append(n)
            m = [tr[n] for n in g]
            ziele = Counter((e["laufx"], e["laufy"]) for e in m if e.get("laufx", 0) > 0)
            laeuft = [n for n in g if self.steht(n) is False]
            aus.append({"besitzer": m[0]["besitzer"], "mitglieder": sorted(g), "arten": Counter(e["typ"] for e in m),
                        "mitte": (sum(e["x"] for e in m) // len(m), sum(e["y"] for e in m) // len(m)),
                        "leben": sum(e["leben"] for e in m), "laufziel": ziele.most_common(1)[0][0] if ziele else None,
                        "laeuft": len(laeuft)})
        aus.sort(key=lambda v: -len(v["mitglieder"]))
        return aus

    def bedrohungen(self, orte, r=40):
        """Feindliche Verbaende, deren Mitte oder Laufziel hoechstens r Felder von einem unserer Orte ist -
        mit Abstand (naechster Ort)."""
        aus = []
        for v in self.verbaende:
            if v["besitzer"] == self.sp:
                continue
            d = min((schach(v["mitte"], o) for o in orte), default=999)
            dz = min((schach(v["laufziel"], o) for o in orte), default=999) if v["laufziel"] else 999
            if min(d, dz) <= r:
                aus.append(dict(v, abstand=d, ziel_abstand=dz))
        return sorted(aus, key=lambda v: min(v["abstand"], v["ziel_abstand"]))

    def zeile(self, orte=()):
        """Eine Zeile: je Spieler Truppen (Arten) + Arbeiter + Lord; die 3 groessten Verbaende je Seite mit Ort."""
        teile = []
        for b in sorted(self.spieler):
            s = self.spieler[b]
            arten = ", ".join("%d %s" % (k, NAME.get(t, t)) for t, k in s["truppen"].most_common(5))
            lord = ("Lord %d" % s["lord"][1]) if s["lord"] else "kein Lord"
            vb = [v for v in self.verbaende if v["besitzer"] == b][:3]
            vt = "; ".join("%d bei %s%s" % (len(v["mitglieder"]), v["mitte"],
                                             (" -> %s" % (v["laufziel"],)) if v["laufziel"] and v["laeuft"] else "")
                           for v in vb)
            teile.append("SP%d%s: %s | Arbeiter %d | %s | Verbaende: %s" % (
                b, "(wir)" if b == self.sp else "", arten or "keine Truppen", s["arbeiter"], lord, vt or "-"))
        bd = self.bedrohungen(orte) if orte else []
        if bd:
            teile.append("BEDROHT von %d Verbaenden (naechster %d Mann, %d Felder)" % (
                len(bd), len(bd[0]["mitglieder"]), min(bd[0]["abstand"], bd[0]["ziel_abstand"])))
        return "LAGE Tick %s: %s" % (self.t, " || ".join(teile))
