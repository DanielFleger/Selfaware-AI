"""B-171, Plan_Gehirn Schritt 1: Was bewirkt eine eingesetzte Einheit, und was kostet sie? Aus den Lageaufzeichnungen.

  python -m selfaware.tools.analysis.wirkung_je_einheit [Ausgabe.json]

Zwischen zwei aufeinanderfolgenden Bildern wird jeder Tod und jedes verschwundene Gebaeude einem Verursacher zugeordnet:
  ziel    jemand zielte im Bild davor auf das Opfer (nahziel, zieleinheit, zielgebaeude)
  nah     niemand zielte darauf, aber ein fremder Kaempfer stand in seiner Reichweite. Arbeiter nur, wenn sie verletzt waren:
          Schuetzen melden ihr Ziel oft nicht, unverletzt Verschwundene sind aber abgewandert oder ihre Huette ist weg
  keine   niemand kommt in Frage. Arbeiter und Gebaeude zaehlen dann nicht als Verlust durch den Gegner (Abwanderung, Abriss).
Mehrere Verursacher teilen sich die Gutschrift. Eingesetzte Zeit sind Einheit-Takte je Kaempfer, getrennt nach "heim"
(bis 30 Felder vom eigenen Bergfried) und "draussen". Gezaehlt wird in Stueck, nicht in Gold: Was ein Verlust wert ist,
haengt von der Lage ab (Plan_Gehirn Abschnitt 4).
"""

import collections
import glob
import gzip
import json
import os
import re
import sys

from selfaware import workspace as _workspace

SOLDAT = {22, 23, 24, 25, 26, 27, 28, 70, 71, 72, 73, 74, 75, 76}
ARBEITER = {1, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 19, 21, 31}
LORD = 55
BERGFRIED = {40, 41, 42, 43, 44}
# Gehoeren zu anderen Gebaeuden oder verschwinden von selbst (Fallen beim Ausloesen)
KEIN_ZIEL = {51, 52, 53, 55, 56, 57, 58, 59, 67, 68, 71, 72, 73}
FERN = {22: 40, 23: 40, 70: 40, 74: 40, 72: 18, 76: 11}  # Reichweite in Feldern, S9
NAH = 2  # Nahkampf beginnt im Umkreis von zwei Feldern (processMeleeInitiation)
ZUENDLER = {71, 76}
GEBAEUDE_NAH = 5
ZUENDEN_NAH = 12
HEIM = 30
MAX_DT = 400
TEMPO = 6  # schneller als ein Feld je 6 Takte laeuft niemand: weiter weg ist es ein neuer Bewohner desselben Platzes
NAMEN = {
    22: "Bogen",
    23: "Armbrust",
    24: "Speer",
    25: "Pike",
    26: "Streitkolben",
    27: "Schwert",
    28: "Ritter",
    55: "Lord",
    70: "arab. Bogen",
    71: "Sklave",
    72: "Schleuder",
    73: "Assassine",
    74: "Pferdebogen",
    75: "arab. Schwert",
    76: "Feuerwerfer",
}


def schach(a, b):
    return max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"]))


def kaempfer(e):
    return e["besitzer"] > 0 and (e["typ"] in SOLDAT or e["typ"] == LORD)


def phase(t):
    return "frueh" if t < 10000 else "mitte" if t < 25000 else "spaet"


def tabelle(text):
    """Text einer Lage-Tabelle -> {nr: {spalte: wert}}."""
    zeilen = text.split("\n")
    start = next(
        (i for i, z in enumerate(zeilen[:3]) if {"besitzer", "typ"} <= set(z.split())), None
    )
    if start is None:
        return {}
    kopf = zeilen[start].split()
    aus = {}
    for z in zeilen[start + 1 :]:
        w = z.split()
        if len(w) != len(kopf):
            continue
        try:
            d = dict(zip(kopf, map(int, w), strict=True))
        except ValueError:
            continue
        aus[d["nr"]] = d
    return aus


def _ziele(einheiten):
    z = collections.defaultdict(dict)
    for u in einheiten.values():
        if kaempfer(u):
            for feld in ("nahziel", "zieleinheit"):
                if u.get(feld, 0) > 0:
                    z[u[feld]][u["nr"]] = u
    return z


def _gebaeude_ziele(einheiten):
    z = collections.defaultdict(list)
    for u in einheiten.values():
        if kaempfer(u) and u.get("zielgebaeude", 0) > 0:
            z[u["zielgebaeude"]].append(u)
    return z


def _volles_leben(einheiten):
    v = collections.Counter()
    for u in einheiten.values():
        v[u["typ"]] = max(v[u["typ"]], u.get("leben", 0))
    return v


def _einheit_weg(o, n, dt):
    """War o nach dem zweiten Bild nicht mehr da? Umwandlung (gleicher Besitzer, andere Art) zaehlt nicht."""
    if n is None or n["besitzer"] != o["besitzer"]:
        return True
    if n["typ"] != o["typ"]:
        return False
    return schach(o, n) > dt / TEMPO + 3


def vergleiche(a, b):
    """Zwei Bilder ({"t", "einheiten", "gebaeude"}) -> Ereignisse: Opfer, Verursacher, Sicherheit der Zuordnung."""
    dt = b["t"] - a["t"]
    aus = []
    ziele, voll = None, None
    fremde = [u for u in a["einheiten"].values() if kaempfer(u)]
    for nr, o in a["einheiten"].items():
        if o["besitzer"] <= 0 or not _einheit_weg(o, b["einheiten"].get(nr), dt):
            continue
        art = (
            "lord"
            if o["typ"] == LORD
            else "soldat"
            if o["typ"] in SOLDAT
            else "arbeiter"
            if o["typ"] in ARBEITER
            else None
        )
        if art is None:
            continue
        if ziele is None:
            ziele = _ziele(a["einheiten"])
        taeter = [u for u in ziele.get(nr, {}).values() if u["besitzer"] != o["besitzer"]]
        sicher = "ziel"
        if not taeter:
            taeter = [
                u
                for u in fremde
                if u["besitzer"] != o["besitzer"] and schach(u, o) <= FERN.get(u["typ"], NAH)
            ]
            sicher = "nah"
            if art == "arbeiter":
                voll = voll or _volles_leben(a["einheiten"])
                if o.get("leben", 0) >= voll[o["typ"]]:
                    taeter = []  # unverletzt verschwunden: Abwanderung oder Huette weg, kein Treffer
        if not taeter:
            sicher = "keine"
        aus.append({"t": a["t"], "art": art, "opfer": o, "taeter": taeter, "sicher": sicher})
    gziele = None
    for nr, g in a["gebaeude"].items():
        n = b["gebaeude"].get(nr)
        if g["besitzer"] <= 0 or g["typ"] in KEIN_ZIEL:
            continue
        if n is not None and n["besitzer"] == g["besitzer"] and n["typ"] == g["typ"]:
            continue
        if gziele is None:
            gziele = _gebaeude_ziele(a["einheiten"])
        taeter = [u for u in gziele.get(nr, []) if u["besitzer"] != g["besitzer"]]
        sicher = "ziel"
        if not taeter:
            sicher = "nah"
            reich = ZUENDEN_NAH if g.get("feuer", 0) > 0 else GEBAEUDE_NAH
            taeter = [
                u
                for u in fremde
                if u["besitzer"] != g["besitzer"]
                and schach(u, g) <= reich
                and (u["typ"] in ZUENDLER or reich == GEBAEUDE_NAH)
            ]
        if not taeter:
            sicher = "keine"
        aus.append({"t": a["t"], "art": "gebaeude", "opfer": g, "taeter": taeter, "sicher": sicher})
    return aus


class Partie:
    """Sammelt die Zaehlungen einer Partie je Spieler."""

    def __init__(self):
        self.takte = collections.Counter()  # (besitzer, typ, zone, phase)
        self.gut = collections.Counter()  # (besitzer, typ, art, sicher, phase)
        self.ver = collections.Counter()  # (besitzer, typ, art, sicher, phase)
        self.luecken = 0
        self.spieler = set()

    def nimm(self, a, b):
        dt = b["t"] - a["t"]
        if dt <= 0 or dt > MAX_DT:
            self.luecken += 1
            return []
        burg = {g["besitzer"]: g for g in a["gebaeude"].values() if g["typ"] in BERGFRIED}
        ph = phase(a["t"])
        for u in a["einheiten"].values():
            if kaempfer(u):
                self.spieler.add(u["besitzer"])
                k = burg.get(u["besitzer"])
                zone = "heim" if k is not None and schach(u, k) <= HEIM else "draussen"
                self.takte[(u["besitzer"], u["typ"], zone, ph)] += dt
        ereignisse = vergleiche(a, b)
        for e in ereignisse:
            o = e["opfer"]
            self.ver[(o["besitzer"], o["typ"], e["art"], e["sicher"], ph)] += 1
            for u in e["taeter"]:
                self.gut[(u["besitzer"], u["typ"], e["art"], e["sicher"], ph)] += 1 / len(
                    e["taeter"]
                )
        return ereignisse


def bilder(pfad):
    """Bilder einer Aufzeichnung; beginnt der Takt von vorn, beginnt eine neue Partie (None dazwischen)."""
    vorher = -1
    with gzip.open(pfad, "rt", encoding="utf-8") as f:
        for z in f:
            try:
                d = json.loads(z)
            except ValueError:
                continue
            if d["t"] < vorher:
                yield None
            vorher = d["t"]
            yield {
                "t": d["t"],
                "st": d.get("st") or {},
                "einheiten": tabelle(d.get("einheiten", "")),
                "gebaeude": tabelle(d.get("gebaeude", "")),
            }


def auswerten(pfad, merke=None):
    p, a, letztes = Partie(), None, None
    for b in bilder(pfad):
        if b is None:
            a = None
            continue
        if a is not None:
            ereignisse = p.nimm(a, b)
            if merke is not None:
                merke.extend(ereignisse)
        a, letztes = b, b
    return p, letztes


STEMPEL = re.compile(r"(\d{4})_(\d{6})_(i\d)(_sp2)?$")


def _stempel(name):
    m = STEMPEL.search(name)
    return (m.group(1), int(m.group(2)), m.group(3), bool(m.group(4))) if m else None


def einordnen(namen):
    """Welche Aufzeichnungen zaehlen, und wer spielt? {name: "ki" | "selbst" | "daniel" | None}.
    Zweitaufzeichnung _sp2 derselben Partie faellt weg; hat sie ein Gegenstueck, spielte SamurAI gegen sich selbst."""
    st = {n: _stempel(n) for n in namen}
    aus = {}
    for n, s in st.items():
        if s is None:
            aus[n] = None
            continue
        zwilling = [
            m
            for m, t in st.items()
            if t
            and m != n
            and t[0] == s[0]
            and t[2] == s[2]
            and t[3] != s[3]
            and abs(t[1] - s[1]) < 90
        ]
        if s[3]:
            aus[n] = "daniel" if n.endswith("20261019_224031_i4_sp2") else None
        else:
            aus[n] = "selbst" if zwilling else "ki"
    return aus


def _gruppe(art, besitzer, ich):
    if art == "selbst":
        return "SamurAI gegen sich"
    if art == "daniel":
        return "SamurAI gegen Daniel" if besitzer == 2 else "Daniel"
    return "SamurAI" if besitzer == ich else "KI-Gegner"


def zusammenfassen(dateien):
    """Alle Aufzeichnungen -> Zaehlungen je Gruppe."""
    namen = {os.path.basename(p)[5:-9]: p for p in dateien}
    art = einordnen(namen)
    summe = collections.defaultdict(
        lambda: {
            "takte": collections.Counter(),
            "gut": collections.Counter(),
            "ver": collections.Counter(),
            "partien": 0,
        }
    )
    genutzt, luecken = collections.Counter(), 0
    for name, pfad in namen.items():
        if art[name] is None:
            continue
        p, letztes = auswerten(pfad)
        ich = (letztes or {}).get("st", {}).get("mensch") or 1
        if len(p.spieler) < 2:
            continue
        genutzt[art[name]] += 1
        luecken += p.luecken
        gesehen = set()
        for quelle, ziel in ((p.takte, "takte"), (p.gut, "gut"), (p.ver, "ver")):
            for k, v in quelle.items():
                g = _gruppe(art[name], k[0], ich)
                gesehen.add(g)
                summe[g][ziel][k[1:]] += v
        for g in gesehen:
            summe[g]["partien"] += 1
    return summe, genutzt, luecken


def _kennzahlen(s, phase_=None):
    def passt(k):
        return phase_ is None or k[-1] == phase_

    takte = sum(v for k, v in s["takte"].items() if passt(k))
    draussen = sum(v for k, v in s["takte"].items() if passt(k) and k[1] == "draussen")
    getoetet = collections.Counter()
    for k, v in s["gut"].items():
        if passt(k):
            getoetet[k[1]] += v
    verloren = collections.Counter()
    for k, v in s["ver"].items():
        if passt(k) and (k[1] in ("soldat", "lord") or k[2] != "keine"):
            verloren[k[1]] += v
    je_1000 = 1000 / max(takte, 1)
    return {
        "einheit_takte": takte,
        "anteil_draussen": round(draussen / max(takte, 1), 3),
        "soldaten_getoetet": round(getoetet["soldat"], 1),
        "arbeiter_getoetet": round(getoetet["arbeiter"], 1),
        "gebaeude_zerstoert": round(getoetet["gebaeude"], 1),
        "soldaten_verloren": verloren["soldat"],
        "arbeiter_verloren": verloren["arbeiter"],
        "gebaeude_verloren": verloren["gebaeude"],
        "tausch_soldaten": round(getoetet["soldat"] / max(verloren["soldat"], 1), 2),
        "getoetet_je_1000_takte": round((getoetet["soldat"] + getoetet["arbeiter"]) * je_1000, 3),
        "gebaeude_je_1000_takte": round(getoetet["gebaeude"] * je_1000, 3),
        "verlust_je_1000_takte": round(verloren["soldat"] * je_1000, 3),
    }


def _je_art(s):
    aus = {}
    for typ in sorted({k[0] for k in s["takte"]}):
        takte = sum(v for k, v in s["takte"].items() if k[0] == typ)
        gut = collections.Counter()
        for k, v in s["gut"].items():
            if k[0] == typ:
                gut[k[1]] += v
        tot = sum(v for k, v in s["ver"].items() if k[0] == typ and k[1] in ("soldat", "lord"))
        je = 1000 / max(takte, 1)
        aus[NAMEN.get(typ, str(typ))] = {
            "einheit_takte": takte,
            "soldaten": round(gut["soldat"], 1),
            "arbeiter": round(gut["arbeiter"], 1),
            "gebaeude": round(gut["gebaeude"], 1),
            "tote": tot,
            "wirkung_je_1000": round((gut["soldat"] + gut["arbeiter"] + gut["gebaeude"]) * je, 3),
            "tote_je_1000": round(tot * je, 3),
        }
    return aus


def _sicherheit(s):
    c = collections.Counter()
    for k, v in s["ver"].items():
        c[k[2]] += v
    return dict(c)


def bericht(summe, genutzt, luecken):
    aus = {"aufzeichnungen": dict(genutzt), "luecken_ueber_max_dt": luecken, "gruppen": {}}
    for g, s in sorted(summe.items()):
        aus["gruppen"][g] = {
            "partien": s["partien"],
            "gesamt": _kennzahlen(s),
            "frueh_bis_10000": _kennzahlen(s, "frueh"),
            "mitte_bis_25000": _kennzahlen(s, "mitte"),
            "spaet": _kennzahlen(s, "spaet"),
            "je_art": _je_art(s),
            "zuordnung": _sicherheit(s),
        }
    return aus


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ziel = argv[0] if argv else os.path.join(_workspace.DATA, "wirkung_je_einheit.json")
    dateien = sorted(glob.glob(os.path.join(_workspace.DATA, "lage_*.jsonl.gz")))
    aus = bericht(*zusammenfassen(dateien))
    with open(ziel, "w", encoding="utf-8") as d:
        json.dump(aus, d, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in aus.items() if k != "gruppen"}, ensure_ascii=False))
    for g, w in aus["gruppen"].items():
        print(f"\n{g}: {w['partien']} Partien, Zuordnung {w['zuordnung']}")
        for ph in ("frueh_bis_10000", "mitte_bis_25000", "spaet", "gesamt"):
            print(f"  {ph}: {w[ph]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
