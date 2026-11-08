"""B-169: stimmen die neuen Felder des Kerns (Aufbau 5) im laufenden Spiel? Liest nur, fasst nichts an.

  python -m selfaware.tools.experiments.kern_felder_pruefen <Sekunden> <Ausgabe.json>

Die Proben pruefen nicht nur, dass Werte ankommen, sondern was sie bedeuten muessen: der Takt-Abstand des Lords ist der Abstand
seiner Einheit, jede eigene Gruppe steht in der Trupptabelle, das naechste Wegfeld liegt neben der Einheit, Geschossfelder passen
zu x und y. Ein Feld, das nie etwas anderes als 0 liefert, faellt in der Zaehlung auf (falsche Speicherstelle).
"""

import collections
import json
import math
import sys
import time

from selfaware.game import kern_leitung as KL

LORD = 55  # UT_LORD
KARTE = range(0, 400)
BRUTE_ALLE = 40  # teure Probe nur in jedem 40. Bild


def feld_aus(x, y):
    """Feldnummer wie das Spiel in der oberen Kartenhaelfte (gemessen 20.10.: Zeile y beginnt bei x = 199 - y, Feld y * (y + 1))."""
    return y * (y + 1) + x - (199 - y) if y < 200 else None


def feld_xy(feld):
    """Umkehrung von feld_aus fuer die obere Kartenhaelfte; (None, None) in der unteren."""
    if not 0 <= feld < 40200:
        return None, None
    y = int((math.isqrt(4 * feld + 1) - 1) // 2)
    return feld - y * (y + 1) + 199 - y, y


class Pruefung:
    def __init__(self):
        self.verstoss = collections.Counter()
        self.proben = collections.Counter()
        self.beispiel = {}
        self.werte = collections.defaultdict(
            lambda: [0, 0, None, None]
        )  # Feld -> [Lesungen, nicht 0, min, max]
        self.wechsel = collections.Counter()
        self.arten = collections.defaultdict(collections.Counter)
        self.abstaende = []
        self.bilder = 0
        self.vorher = {}
        self.geschoss_vorher = {}

    def _pruefe(self, name, ok, was=None):
        self.proben[name] += 1
        if not ok:
            self.verstoss[name] += 1
            self.beispiel.setdefault(name, was)

    def _zaehle(self, feld, wert):
        z = self.werte[feld]
        z[0] += 1
        z[1] += wert != 0
        z[2] = wert if z[2] is None or wert < z[2] else z[2]
        z[3] = wert if z[3] is None or wert > z[3] else z[3]

    def bild(self, w):
        self.bilder += 1
        for e in w.einheiten.values():
            self._einheit(w, e)
        self._gebaeude(w)
        self._geschosse(w)
        for t in w.trupps.values():
            self.arten["trupp_zustand"][t["zustand"]] += 1
            for n in ("zielx", "ziely", "zielgebaeude", "zielgebaeude_uid"):
                self._zaehle(f"trupp.{n}", t[n])
            self._pruefe("trupp_ziel_auf_karte", t["zielx"] in KARTE and t["ziely"] in KARTE, t)
        self._lord(w)
        if self.bilder % BRUTE_ALLE == 1:
            self._feindabstand(w)
        self.vorher = {
            nr: (e["bild"], e["bildzyklus"], e["teilzustand"]) for nr, e in w.einheiten.items()
        }

    def _einheit(self, w, e):
        for n in KL.EINHEIT_SPIELFELD:
            if n in e:
                self._zaehle(n, e[n])
        self._pruefe(
            "feinposition_passt", e["feinx"] // 8 == e["x"] and e["feiny"] // 8 == e["y"], e
        )
        alt = self.vorher.get(e["nr"])
        if alt is not None:
            for i, n in enumerate(("bild", "bildzyklus", "teilzustand")):
                self.wechsel[n] += e[n] != alt[i]
        if e["besitzer"] != w.ich:
            self._pruefe("fremd_geschwaerzt", not KL.NUR_EIGEN & set(e), e)
            return
        self.arten["wegbedarf"][e["wegbedarf"]] += 1
        self.arten["getoetet"][e["getoetet"]] += 1
        self._pruefe("wegindex_im_weg", 0 <= e["wegindex"] <= max(e["weglaenge"], 0) + 1, e)
        for x, y, n in (
            (e["planx"], e["plany"], "plan"),
            (e["zielx"], e["ziely"], "ziel"),
            (e["mauerx"], e["mauery"], "mauer"),
        ):
            self._pruefe(f"{n}_auf_karte", x in KARTE and y in KARTE, e)
        if e["gruppe"] > 0:
            self._pruefe("eigene_gruppe_in_trupptabelle", e["gruppe"] in w.trupps, e)
        # nahangreifer ist die ZAHL der Nahkaempfer, die gerade auf die Einheit einschlagen (updateUnits), keine Einheitennummer
        self._pruefe("angreiferzahl_klein", 0 <= e["nahangreifer"] <= 30, e)
        if e["schusseinheit"] > 0:
            self._pruefe("schussziel_hat_uid", e["schussziel_uid"] != 0, e)
        if e["naechstesfeld"] > 0:
            x, y = feld_xy(e["naechstesfeld"])
            if x is not None and e["y"] < 198:
                self._pruefe(
                    "naechstes_feld_nebenan", abs(x - e["x"]) <= 3 and abs(y - e["y"]) <= 3, e
                )

    def _gebaeude(self, w):
        for g in w.gebaeude.values():
            self._zaehle("gebaeude.tor", g["tor"])
            if g["tor"]:
                self.arten["tor_je_gebaeudeart"][f"{g['typ']}:{g['tor']}"] += 1

    def _geschosse(self, w):
        jetzt = {}
        for q in w.geschosse.values():
            for n in (
                "typ",
                "besitzer",
                "feinx",
                "feiny",
                "hoehe",
                "weg",
                "feuer",
                "feld",
                "richtung",
            ):
                self._zaehle(f"geschoss.{n}", q[n])
            self.arten["geschoss_typ"][q["typ"]] += 1
            self.arten["geschoss_zustand"][q["zustand"]] += 1
            self._pruefe("geschoss_besitzer", 0 <= q["besitzer"] <= 8, q)
            self._pruefe("geschoss_auf_karte", q["x"] in KARTE and q["y"] in KARTE, q)
            if q["y"] < 200 and q["feld"] > 0:
                self._pruefe("geschoss_feld_passt", feld_aus(q["x"], q["y"]) == q["feld"], q)
            # vcos/vsin enthalten die Geschwindigkeit (initializeProjectileVelocities), ihre Laenge ist nicht 1
            jetzt[q["nr"]] = (q["typ"], q["weg"])
            alt = self.geschoss_vorher.get(q["nr"])
            if alt is not None and alt[0] == q["typ"] and q["weg"] != alt[1]:
                # wird der Weg kleiner, hat ein neues Geschoss denselben Platz belegt
                self._pruefe("geschossweg_waechst", q["weg"] > alt[1] or q["weg"] <= 8, (alt, q))
        self.geschoss_vorher = jetzt

    def _lord(self, w):
        lords = [e for e in w.einheiten.values() if e["besitzer"] == w.ich and e["typ"] == LORD]
        if lords:
            self._zaehle("lord_feindabstand", w.lord_feindabstand)
            self._pruefe(
                "lordabstand_gleich_einheit",
                w.lord_feindabstand == lords[0]["feindabstand"],
                (w.tick, w.lord_feindabstand, lords[0]["feindabstand"]),
            )

    def _feindabstand(self, w):
        """Spielwert gegen selbst gerechneten Abstand zum naechsten Gegner (Spieler 1-8, nur Soldaten sind nicht getrennt)."""
        gegner = [
            (e["feinx"], e["feiny"])
            for e in w.einheiten.values()
            if e["besitzer"] != w.ich and e["besitzer"] > 0
        ]
        if not gegner:
            return
        for e in w.einheiten.values():
            if e["besitzer"] == w.ich and 0 < e["feindabstand"] < 800:
                d = min(math.hypot(e["feinx"] - x, e["feiny"] - y) for x, y in gegner)
                self.abstaende.append((e["feindabstand"], round(d, 1)))

    def ergebnis(self):
        paare = self.abstaende
        return {
            "bilder": self.bilder,
            "proben": dict(self.proben),
            "verstoesse": dict(self.verstoss),
            "beispiele": {k: repr(v)[:500] for k, v in self.beispiel.items()},
            "felder": {
                k: dict(zip(("lesungen", "nicht_0", "min", "max"), v, strict=True))
                for k, v in sorted(self.werte.items())
            },
            "wechsel_von_bild_zu_bild": dict(self.wechsel),
            "arten": {k: dict(sorted(v.items(), key=str)) for k, v in self.arten.items()},
            "feindabstand_paare": len(paare),
            "feindabstand_spiel_durch_rechnung_median": _median([a / b for a, b in paare if b > 0]),
            "feindabstand_korrelation": _korrelation(paare),
        }


def _median(werte):
    return round(sorted(werte)[len(werte) // 2], 3) if werte else None


def _korrelation(paare):
    if len(paare) < 3:
        return None
    n = len(paare)
    mx, my = sum(a for a, _ in paare) / n, sum(b for _, b in paare) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a, _ in paare))
    sy = math.sqrt(sum((b - my) ** 2 for _, b in paare))
    return round(sum((a - mx) * (b - my) for a, b in paare) / (sx * sy), 4) if sx and sy else None


def main(argv=None):
    from selfaware.game.ucp.laden import SPIEL

    argv = sys.argv[1:] if argv is None else argv
    sekunden, ausgabe = float(argv[0]), argv[1]
    ende = time.time() + sekunden
    leitung = None
    while leitung is None and time.time() < ende:
        try:
            leitung = KL.Leitung(SPIEL)
            if leitung.lesen() is None:
                leitung = None
        except (OSError, ValueError, KL.FalscherAufbau):
            leitung = None
        if leitung is None:
            time.sleep(0.5)
    if leitung is None:
        print("Keine Leitung mit Aufbau", KL.AUFBAU)
        return 1
    print("Leitung", leitung.name, flush=True)
    p, takte, luecke, letzter, erster, kern, epochen = Pruefung(), 0, 0, None, None, None, set()
    einheiten, geschosse, trupps = 0, 0, 0
    while time.time() < ende:
        try:
            w = leitung.lesen()
        except KL.FalscherAufbau:
            w = None
        if w is None or w.tick == letzter:
            time.sleep(0.0005)
            continue
        if letzter is not None and w.epoche in epochen and w.tick > letzter:
            luecke = max(luecke, w.tick - letzter)
        elif w.epoche not in epochen:
            p.vorher, p.geschoss_vorher = {}, {}
        erster = w.tick if erster is None or w.epoche not in epochen else erster
        epochen.add(w.epoche)
        letzter, kern = w.tick, w.kern
        takte += 1
        einheiten, geschosse, trupps = (
            max(einheiten, len(w.einheiten)),
            max(geschosse, len(w.geschosse)),
            max(trupps, len(w.trupps)),
        )
        p.bild(w)
    aus = p.ergebnis()
    aus.update(
        kern=kern,
        takte_gelesen=takte,
        letzter_takt=letzter,
        groesste_luecke=luecke,
        epochen=sorted(epochen),
        hoechstens={"einheiten": einheiten, "geschosse": geschosse, "trupps": trupps},
    )
    with open(ausgabe, "w", encoding="utf-8") as d:
        json.dump(aus, d, ensure_ascii=False, indent=1)
    print(
        json.dumps(
            {
                k: aus[k]
                for k in (
                    "kern",
                    "takte_gelesen",
                    "letzter_takt",
                    "groesste_luecke",
                    "verstoesse",
                    "hoechstens",
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
