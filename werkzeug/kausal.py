# -*- coding: utf-8 -*-
"""Kausalmodell (Daniel 06.10. 23:27: "da wirklich alles Kausalketten hat, aber diese dynamisch sein muessen, heisst es auch,
es muss dynamische Antworten fuer alles geben"; 23:13: "die KI lernt selbst").

Statt fester Schwellen ("Huette, wenn < 6 frei", "Joch nach dem ersten Stein") rechnet der Entscheider fuer jede moegliche
Handlung die Wirkungskette bis zum Zieltick aus der AKTUELLEN Lage und baut, was dort am meisten Gold-Wert bringt:

  Bauer verfuegbar   -> sofort (am Feuer) oder nach Spawn (SPAWN Ticks je Bauer, nur wenn Wohnraum frei)
  Weg zum Arbeitsort -> Abstand Feuer -> Platz x GEHEN Ticks
  erster Ertrag      -> Anlauf der Art (gemessen) + Weg zum Abgabeort
  Ertrag bis Ziel    -> Zyklen bis zum Zieltick x Menge x Verkaufswert
  Wert der Handlung  = Ertrag bis Ziel + Abrissrueckgabe (Haelfte) - Kosten

Huette: Wert = Wert der Arbeit, die die dadurch frueher gespawnten Bauern bis zum Ziel noch leisten - 0, wenn schon Bauern
untaetig sind (die Arbeit braucht keinen neuen Menschen) oder kein Arbeitsplatz auf sie wartet.

Alle Groessen kommen aus MODELL (gemessene Werte, Wissensregister). Der Lernkreis vergleicht nach jedem Lauf Vorhersage
und Wirklichkeit (erste Lieferung, Ertrag) und schreibt korrigierte Werte nach daten/kausal_modell.json - der naechste
Lauf rechnet damit.
"""
import json
import os

HIER = os.path.dirname(os.path.abspath(__file__))
DATEI = os.path.join(HIER, "..", "daten", "kausal_modell.json")

# Gemessen unter Ascension (12.10., Daniel 01:09 "Cash von Steinen/Eisen/Brot", 01:26 "in der Mine selbst messen"):
# Preise L65 (preise_messen.py), Gehtempo L68, Ketten L71 (arbeitsgang_rohstoff.py + gebaeude_auswerten.py).
# Vorher (06.10.): Holz 18 je 1.860 Ticks zu 1 Gold, Stein/Eisen/Hopfen unbekannt - 1012f/g bauten 103-128 Holzfaeller bei 37 Gold.
MODELL = {
    "spawn_ticks": 52,            # L7: ~1 Bauer je 52 Ticks (Wohnraum frei, Beliebtheit hoch)
    "gehen_ticks": 16,            # L68: alle Rohstoff-/Nahrungsarbeiter 16 Ticks je Feld (Holzfaeller 24), mit/ohne Last gleich
    "huette_platz": 8,            # +8 Wohnplaetze je Huette (Platz 26 -> 34 -> 42 ...)
    # rate: je Betrieb und 1.000 Ticks (gemessen, wegunabhaengig) ODER menge/zyklus/gehen: rate(d) = 1000*menge/(zyklus+2*d*gehen)
    # Holz weg-abhaengig (12.10. 01:46, 1012j: Holzfaeller 120 Felder vom Lager gewaehlt): 18 je Gang (L10, Liga), Arbeit 2.580
    # abgeleitet aus 4 je 1.000 bei ~40 Feldern (L71) mit 24 Ticks je Feld (L68) -> 5,9 bei 10, 2,2 bei 120 Feldern
    3: {"menge": 18, "zyklus": 2580, "anlauf": 3700, "wert": 2.0, "gehen": 24, "arbeiter": 1},
    31: {"menge": 3, "zyklus": 2800, "anlauf": 8000, "wert": 18.0, "gehen": 16, "arbeiter": 1},  # L71: growCounter 400->0 ~2.800, 3 je Ernte
    5: {"rate": 0.7, "anlauf": 6600, "wert": 27.0, "gehen": 16, "arbeiter": 2},      # L71: 0,66-0,73 je Mine (3 Laeufe), Traeger haelt mit
    20: {"bruch": 3.3, "ochse_menge": 7, "ochse_laden": 2650, "anlauf": 5200, "wert": 7.0, "gehen": 16, "arbeiter": 3,
         "ochsen_max": 3},                                                           # L71: Bruch 3,3; Ochse 7 je Fahrt, Laden ~2.650
    32: {"menge": 3, "zyklus": 790, "anlauf": 2224, "wert": 3.0, "gehen": 16, "arbeiter": 1},    # Apfel (06.10.), Preis 3 (L65)
    7: {"rate": 3.07, "anlauf": 4427, "wert": 3.0, "gehen": 16, "arbeiter": 1},      # Jaeger 3,07 je 1.000 (06.10.), Fleisch 3 (L65)
}


def lade():
    if os.path.exists(DATEI):
        try:
            MODELL.update({int(k) if k.isdigit() else k: v for k, v in json.load(open(DATEI, encoding="utf-8")).items()})
        except Exception:
            pass
    return MODELL


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def ochsen_rate(d):
    """Stein je Ochse und 1.000 Ticks bei d Feldern Weg Bruch -> Lager (L71: 7 je Fahrt, Laden ~2.650, 16 Ticks je Feld)."""
    m = MODELL[20]
    return 1000.0 * m["ochse_menge"] / (m["ochse_laden"] + 2 * d * m["gehen"])


def ochsen_fuer(d):
    """So viele Ochsen, wie der Bruch bei diesem Weg braucht (hoechstens ochsen_max)."""
    m = MODELL[20]
    k = 1
    while k < m["ochsen_max"] and k * ochsen_rate(d) < m["bruch"]:
        k += 1
    return k


def rate_je_1000(typ, d):
    """Ware je Betrieb und 1.000 Ticks bei d Feldern Weg zur Ablage."""
    m = MODELL[typ]
    if typ == 20:
        return min(m["bruch"], ochsen_fuer(d) * ochsen_rate(d))
    if "rate" in m:
        return m["rate"]
    return 1000.0 * m["menge"] / (m["zyklus"] + 2 * d * m.get("gehen", MODELL["gehen_ticks"]))


def arbeiter(typ, d=0):
    m = MODELL[typ]
    return m.get("arbeiter", 1) + (ochsen_fuer(d) if typ == 20 else 0)


def ertrag_bis(typ, t_start, ziel, weg_abgabe, wert=None):
    """Gold-Wert, den ein Betrieb der Art typ, dessen Arbeiter bei t_start an seinem Platz steht, bis ziel abliefert.
    wert: Gold je Stueck statt MODELL[typ]["wert"] (Knappheitswert, s. entscheide)."""
    m = MODELL[typ]
    t1 = t_start + m["anlauf"] + weg_abgabe * m.get("gehen", MODELL["gehen_ticks"])   # erste Lieferung
    if t1 > ziel:
        return 0.0, t1
    return rate_je_1000(typ, weg_abgabe) * (ziel - t1) / 1000.0 * (m["wert"] if wert is None else wert), t1


def wert_betrieb(typ, ort, jetzt, ziel, feuer_ort, abgabe_ort, kosten, bauer_ab, wert=None):
    """Netto-Wert bis ziel: Ertrag + halbe Kosten zurueck (Abriss im Endspiel) - Kosten. bauer_ab: Tick, ab dem ein Bauer
    fuer diesen Betrieb frei ist (jetzt, wenn einer am Feuer steht; sonst nach Spawn)."""
    g = MODELL[typ].get("gehen", MODELL["gehen_ticks"]) if typ in MODELL else MODELL["gehen_ticks"]
    an_ort = bauer_ab + schach(feuer_ort, ort) * g
    ertrag, t1 = ertrag_bis(typ, an_ort, ziel, schach(ort, abgabe_ort), wert)
    k = sum(kosten.get(w, 0) * (1 if w != "stein" else 5) for w in ("holz", "stein", "gold"))
    return ertrag + k / 2.0 - k, t1


def bauer_ab(jetzt, feuer, frei_wohn, rang):
    """Wann ist der rang-te zusaetzliche Bauer (0 = erster) verfuegbar? Am Feuer sofort; dann Spawn, solange Wohnraum frei;
    sonst nie (None)."""
    if rang < feuer:
        return jetzt
    k = rang - feuer
    if k < frei_wohn:
        return jetzt + (k + 1) * MODELL["spawn_ticks"]
    return None


def entscheide(jetzt, ziel, st, kandidaten, feuer_ort, abgabe_orte, huette_kosten, offene_stellen=0, sparen=True):
    """kandidaten: [(typ, ort, kosten, arbeiter)] - die besten Plaetze je Art (vom Planer). Gibt eine Liste von Handlungen
    [(wert, art, ort, text)] in Wertfolge, nur mit positivem Wert und im Rahmen von Holz/Gold.

    Bauern werden der Reihe nach vergeben (12.10. neu geschrieben, Daniel 01:04 Bild: 128 Holzfaeller, 48 davon leer):
      - offene_stellen = Arbeitsplaetze in stehenden oder bestellten Betrieben ohne Arbeiter. Die naechsten Bauern gehen
        DORTHIN; ein neuer Betrieb bekommt erst den (offene_stellen + 1)-ten.
      - Jeder angenommene Betrieb verbraucht seine Arbeiter, BEVOR der naechste bewertet wird. Vorher wurden alle
        Kandidaten mit demselben ersten Bauern gerechnet (rang wurde in der Bewertung nie hochgezaehlt): bei 4 Bauern am
        Feuer galten 6 neue Holzfaeller als sofort besetzt.
    Reihenfolge: nach dem Wert mit dem naechsten freien Bauern; jeder Kandidat wird dann mit SEINEM Bauern neu gerechnet."""
    feuer, frei_wohn = st.get("feuer", 0), max(0, st.get("platz", 0) - st.get("leute", 0))
    holz, gold, stein = st.get("holz", 0), st.get("gold", 0), st.get("stein", 0)
    rang = max(0, int(offene_stellen))
    handlungen, wartet = [], []
    vorab = []
    ab0 = bauer_ab(jetzt, feuer, frei_wohn, rang)
    for typ, ort, kosten, arbeiter in kandidaten:
        if typ not in MODELL:
            continue
        if ab0 is None:
            wartet.append((typ, ort, kosten))
            continue
        w0, _ = wert_betrieb(typ, ort, jetzt, ziel, feuer_ort, abgabe_orte.get(typ, ort), kosten, ab0)
        vorab.append((w0, typ, ort, kosten, max(1, int(arbeiter or 1))))
    # 12.10. 01:41 Knappheitswert fuer Holz (Daniel 01:39: "wenn du Holz brauchst, mach mehr Holzfaeller, wo Holz ist";
    # 1012i: Startholz bei Tick 130 verbaut, danach Holz ~6 - Eisenmine 40 / Steinbruch 25 Holz nie bezahlbar): Holz ist so viel
    # wert, wie der beste NUR am Holz scheiternde Bau je Holz einbringt (Wert + Holzkosten) / Holzkosten. Holzfaeller werden
    # mit diesem Wert gerechnet, solange er ueber dem Marktpreis liegt - dann entstehen Holzfaeller, bis Holz kein Engpass mehr ist.
    blockiert = [(w0 + k.get("holz", 0)) / float(k["holz"]) for w0, typ, _, k, _ in vorab
                 if typ != 3 and w0 > 0 and k.get("holz", 0) > holz and gold >= k.get("gold", 0) and stein >= k.get("stein", 0)]
    knapp_holz = max(blockiert) if blockiert else None
    if knapp_holz and knapp_holz > MODELL[3]["wert"]:
        neu_vorab = []
        for w0, typ, ort, k, arb in vorab:
            if typ == 3:
                w0, _ = wert_betrieb(typ, ort, jetzt, ziel, feuer_ort, abgabe_orte.get(typ, ort), k, ab0, wert=knapp_holz)
            neu_vorab.append((w0, typ, ort, k, arb))
        vorab = neu_vorab
    # 12.10. (Daniel 01:09/01:26, "Gold je Arbeiter"): Bauern sind knapp - Reihenfolge nach Wert JE ARBEITER, nicht je Gebaeude
    # (sonst gewinnt ein Steinbruch-Paket mit 5 Arbeitern gegen einen Hopfenhof mit einem)
    vorab.sort(key=lambda x: -x[0] / float(x[4]))
    # B-122 (19.10., Partie 20261019_2240): ein unbezahlbarer Betrieb wurde uebersprungen und der naechstbilligere nahm das
    # Holz - die Eisenmine (40 Holz, bester Wert) wartete 27.000 Ticks, 35 Apfelplantagen zu 8 Holz kamen. Jetzt wird fuer
    # den BESTEN Betrieb gespart, dem nur Holz/Gold/Stein fehlt: was danach kommt, darf nichts davon verbrauchen. Ausnahme
    # Holzfaeller, wenn Holz fehlt (Daniel 01:39: "wenn du Holz brauchst, mach mehr Holzfaeller") - sie beheben den Mangel.
    gespart = None
    for _, typ, ort, kosten, arbeiter in vorab:
        ab = bauer_ab(jetzt, feuer, frei_wohn, rang + arbeiter - 1)     # der letzte Arbeiter dieses Betriebs
        if ab is None:
            wartet.append((typ, ort, kosten))
            continue
        w, t1 = wert_betrieb(typ, ort, jetzt, ziel, feuer_ort, abgabe_orte.get(typ, ort), kosten, ab,
                             wert=knapp_holz if (typ == 3 and knapp_holz and knapp_holz > MODELL[3]["wert"]) else None)
        if w <= 0:
            continue
        fehlt = {r: kosten.get(r, 0) - v for r, v in (("holz", holz), ("gold", gold), ("stein", stein)) if kosten.get(r, 0) > v}
        if fehlt:
            if gespart is None and sparen:          # sparen=False: altes Verhalten (Schalter kausal_sparen=nein)
                gespart = {"typ": typ, "ort": ort, "fehlt": fehlt, "kosten": dict(kosten), "wert": w}
            continue
        if gespart and any(kosten.get(r, 0) > 0 for r in gespart["fehlt"]) and not (typ == 3 and "holz" in gespart["fehlt"]):
            continue
        holz -= kosten.get("holz", 0)
        gold -= kosten.get("gold", 0)
        stein -= kosten.get("stein", 0)
        handlungen.append((w, typ, ort, "Wert %.0f bis Tick %d, erste Lieferung %d (Bauer Nr. %d nach %d offenen Stellen)%s" % (
            w, ziel, t1, rang + arbeiter, int(offene_stellen),
            ", Holz-Knappheitswert %.1f Gold je Holz" % knapp_holz if (typ == 3 and knapp_holz and knapp_holz > MODELL[3]["wert"]) else "")))
        rang += arbeiter
    # Huette: lohnt nur, wenn ein Arbeitsplatz mit positivem Wert auf einen Bauern wartet, den es ohne Wohnraum nicht gibt
    if wartet and feuer == 0 and holz >= huette_kosten:
        # Wert: der beste wartende Betrieb, gerechnet mit Spawn nach dem Bau (Huette ~ sofort, Spawn danach)
        best = None
        for typ, ort, kosten in wartet:
            w, t1 = wert_betrieb(typ, ort, jetzt, ziel, feuer_ort, abgabe_orte.get(typ, ort), kosten, jetzt + MODELL["spawn_ticks"])
            if best is None or w > best[0]:
                best = (w, typ, t1)
        if best and best[0] > huette_kosten:
            handlungen.append((best[0] - huette_kosten, 1, None, "Huette: wartender Betrieb Art %d bringt %.0f bis Tick %d" % (
                best[1], best[0], ziel)))
    return handlungen
