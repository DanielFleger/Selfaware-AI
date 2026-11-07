"""Spielwerte aus der Messung: Reichweite, Lauftempo, Nahkampfschaden, Schusstakt (P3, B-155).

Quelle: data/research/auge_plan/lauf_s_20261103/spielwerte_gemessen.json (Lauf S, 03./04.11.2026,
UCP3 + Team-Liga 2.0.2) und Wissensregister S1 bis S52. Abgleich gegen die alten Konstanten:
data/research/auge_plan/p3_abgleich.md. Fehlt die Datei, gelten die Werte unter ERSATZ (dieselben
Messwerte, von Hand uebertragen).

Abstaende (beide Mass-Arten sind im Spiel verschieden):
  - Laufen zaehlt Schachfelder: gerade und schraeg gleich viele Takte je Feld (S4).
  - Schiessen prueft Luftlinie: dx^2 + dy^2 <= R^2 in Feldern (acquireShootTarget 0x0054B0D0, aus
    dem Code; gemessen wurde die Reichweite nur auf gerader Linie, S9).

Erfassen und Gefahr: Ein Schuetze erfasst ein Ziel bis ERFASSEN Felder (Luftlinie). Danach zielt er
(ZIELZEIT, L81) und schiesst auch, wenn das Ziel inzwischen weiter weg ist (L91: bis ~300 Takte,
Bolzen aus 42 Feldern in 1018p); das Geschoss fliegt vorausgezielt (S10). Fuer eine fliehende
Einheit ist der gefaehrliche Umkreis deshalb ERFASSEN + der Weg, den sie waehrend des Zielens
schafft, mindestens RAND_MIN Felder (der alte ENTDECKT_RAND aus 1018p). Das ist ein Modell aus L81,
L91 und S10, nicht als Ganzes gemessen.

Lord-Leben: im laufenden Spiel je KI 75.000 bis 180.000, nach dem Laden eines Spielstands 150.000
(K1). Wer kann, nimmt das Leben aus dem Lagebild (sichtbarer Lebensbalken, laut docs/FAIRNESS.md
erlaubt); LORD_LEBEN_NACH_LADEN ist nur Ersatz.
"""

import collections
import json
import os

from selfaware import workspace as _workspace

QUELLE = os.path.join(
    _workspace.DATA, "auge_plan", "lauf_s_20261103", "spielwerte_gemessen.json"
)

# Bogen, Armbrust, arab. Bogen, Pferdebogen, Schleuder, Feuerwerfer
FERNKAMPF = (22, 23, 70, 74, 72, 76)
GESCHOSS = {22: "pfeil", 70: "pfeil", 74: "pfeil", 23: "bolzen", 72: "schleuder", 76: "feuer"}
# Takte vom Erkennen bis zum Abschuss (L81, Editor 17.10.); Pferdebogen ungemessen -> wie der Bogen
ZIELZEIT = {22: 56, 23: 137, 70: 28, 74: 56, 72: 20, 76: 13}
RAND_MIN = 4  # Felder ueber ERFASSEN hinaus mindestens (1018p: Bolzen aus 42 Feldern)
FLIEHER_TEMPO = 16.0  # Takte je Feld einer fliehenden Assassine (S8)
LORD_LEBEN_NACH_LADEN = 150000  # K1: gilt nur nach dem Laden eines Spielstands
TEMPO_ERSATZ = {"direkt": 16.0, "trupp": 12.0}

# Ersatz, falls die Messdatei fehlt (Werte aus Wissensregister S8, S9, S10 und schusstakt)
_TEMPO_DIREKT = {5: 16, 22: 16, 24: 16, 26: 16, 28: 16, 29: 16, 30: 16, 70: 16, 71: 16, 72: 16}
_TEMPO_DIREKT.update({73: 16, 74: 16, 23: 24, 25: 24, 37: 24, 55: 24, 75: 24, 76: 24, 27: 31.6})
_TEMPO_TRUPP = {5: 12.1, 22: 12.2, 24: 12.0, 26: 12.0, 28: 10.7, 29: 12.1, 30: 16.0, 70: 12.2}
_TEMPO_TRUPP.update({71: 12.0, 72: 12.1, 73: 16.0, 74: 11.2, 23: 24.0, 25: 23.7, 37: 24.0})
_TEMPO_TRUPP.update({55: 24.0, 75: 24.0, 76: 24.0, 27: 31.9})
ERSATZ = {
    "erfassen": {
        **{22: 40, 23: 40, 70: 40, 74: 40, 72: 18, 76: 11},
        **{39: 59, 40: 70, 41: 54, 61: 68, 77: 39},
    },
    "tempo": {
        **{("direkt", t): float(v) for t, v in _TEMPO_DIREKT.items()},
        **{("trupp", t): float(v) for t, v in _TEMPO_TRUPP.items()},
    },
    "geschoss_mikro_je_takt": {"pfeil": 5.75, "bolzen": 6.18, "schleuder": 5.63, "feuer": 3.78},
    "schusstakt": {22: 129, 23: 228, 70: 90, 72: 56, 74: 78, 76: 143},
}


def _laden(pfad=QUELLE):
    """Messdatei -> dict mit erfassen, tempo[(befehl, typ)], nahkampf[(angreifer, opfer)],
    geschoss_mikro_je_takt, schusstakt und quelle."""
    try:
        with open(pfad, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return dict(ERSATZ, nahkampf={}, quelle="Ersatzwerte (Messdatei fehlt)")
    erfassen = {}
    for z in d.get("reichweite", []):
        r = z.get("schiesst_bis_feld")
        if z.get("marke") == "gemessen" and r is not None and r > 3:
            erfassen[z["typ"]] = max(erfassen.get(z["typ"], 0), r)
    tempo_l = collections.defaultdict(list)
    for z in d.get("laufen", []):
        if z.get("marke") == "gemessen" and z.get("takte_je_feld"):
            tempo_l[(z["befehl"], z["typ"])].append(z["takte_je_feld"])
    tempo = {k: round(sum(v) / len(v), 2) for k, v in tempo_l.items()}
    nah_l = collections.defaultdict(list)
    for z in d.get("schaden_nahkampf", []):
        takte = z.get("takte_zwischen_treffern") or {}
        if not z.get("schaden") or not takte:
            continue
        haeufig = int(max(takte.items(), key=lambda kv: kv[1])[0])
        nah_l[(z["typ"], z["opfer"])].append(z["schaden"] / float(max(1, haeufig)))
    nahkampf = {k: sum(v) / len(v) for k, v in nah_l.items()}
    geschoss = {
        z["art"]: z["mikro_je_takt"] for z in d.get("geschoss_tempo", []) if z.get("mikro_je_takt")
    }
    schusstakt = {}
    for z in d.get("schusstakt", []):
        h = z.get("takte_zwischen_schuessen_haeufig") or []
        if h:
            schusstakt[z["typ"]] = h[0][0]
    return {
        "erfassen": erfassen or dict(ERSATZ["erfassen"]),
        "tempo": tempo or dict(ERSATZ["tempo"]),
        "nahkampf": nahkampf,
        "geschoss_mikro_je_takt": geschoss or dict(ERSATZ["geschoss_mikro_je_takt"]),
        "schusstakt": schusstakt or dict(ERSATZ["schusstakt"]),
        "quelle": os.path.relpath(pfad, _workspace.ROOT),
    }


W = _laden()
# Luftlinie in Feldern, alle gemessenen Schuetzen und Geraete
ERFASSEN = dict(W["erfassen"])
# nur die sechs Fernkaempfer zu Fuss und zu Pferd
ERFASSEN_FERN = {t: ERFASSEN[t] for t in FERNKAMPF if t in ERFASSEN}


def luftlinie2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def erfassen(typ):
    """Reichweite in Feldern (Luftlinie) oder None, wenn die Art nicht schiesst."""
    return ERFASSEN.get(typ)


def in_reichweite(schuetze, ziel, typ):
    """Kann ein Schuetze der Art typ am Ort schuetze das Ziel jetzt erfassen? (Luftlinie)"""
    r = ERFASSEN.get(typ)
    return r is not None and luftlinie2(schuetze, ziel) <= r * r


def gefahr(typ, flieher_tempo=FLIEHER_TEMPO):
    """Gefaehrlicher Umkreis (Luftlinie, Felder) eines Schuetzen fuer eine fliehende Einheit:
    ERFASSEN + Weg waehrend des Zielens, mindestens RAND_MIN (siehe Kopf). None ohne Schuss."""
    r = ERFASSEN.get(typ)
    if r is None:
        return None
    rand = ZIELZEIT.get(typ, ZIELZEIT[22]) / float(flieher_tempo)
    return r + max(RAND_MIN, rand)


def in_gefahr(schuetze, ziel, typ, flieher_tempo=FLIEHER_TEMPO):
    g = gefahr(typ, flieher_tempo)
    return g is not None and luftlinie2(schuetze, ziel) <= g * g


def _befehl(befehl):
    return "trupp" if befehl in ("trupp", "angriff") else "direkt"


def takte_je_feld(typ, befehl="trupp"):
    """Lauftempo in Takten je Schachfeld. befehl: "direkt" (Einzelbefehl) oder "trupp" (Trupp-
    oder Angriffsbefehl, S8). Ungemessene Arten: 16 direkt, 12 im Trupp."""
    befehl = _befehl(befehl)
    v = W["tempo"].get((befehl, typ))
    return float(v) if v is not None else TEMPO_ERSATZ[befehl]


def tempo_tabelle(befehl="trupp", arten=None):
    """{typ: Takte je Feld} fuer alle gemessenen Arten (oder die genannten)."""
    befehl = _befehl(befehl)
    if arten is None:
        arten = sorted({t for b, t in W["tempo"] if b == befehl})
    return {t: takte_je_feld(t, befehl) for t in arten}


def nahkampf_je_takt(angreifer, opfer, ersatz=None):
    """Nahkampfschaden je Takt von angreifer an opfer (S3: jeden Takt ein Treffer in Hoehe des
    Tabellenwerts). Ohne gemessenes Paar: Mittel der Zeile des Angreifers, sonst ersatz."""
    v = W["nahkampf"].get((angreifer, opfer))
    if v is not None:
        return v
    zeile = [w for (a, _), w in W["nahkampf"].items() if a == angreifer]
    return sum(zeile) / len(zeile) if zeile else ersatz


def schusstakt(typ):
    """Takte zwischen zwei Schuessen (haeufigster Abstand, Lauf S) oder None."""
    return W["schusstakt"].get(typ)


def flugzeit(typ, felder):
    """Takte, die das Geschoss der Art typ fuer so viele Felder braucht (S10; 8 Mikro je Feld)."""
    v = W["geschoss_mikro_je_takt"].get(GESCHOSS.get(typ, ""))
    return felder * 8.0 / v if v else None
