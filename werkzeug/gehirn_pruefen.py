# -*- coding: utf-8 -*-
"""Gehirn-Baustein 1 gegen den Pruefstein (offline, kein Spiel). Vorher festgelegt (Daniel 25.10. 20:01 "ja"):
  ZIEL       mindestens 80 % der echten Lebensverluste eines Fensters liegen auf Opfern, die die Prognose genannt hat
             (Opfer-Quote), und Geschoss-/Schusstreffer kommen zu mindestens 80 % auf +-5 Takte
  ABBRUCH    Opfer-Quote unter 50 % -> ein Auge-Teil stimmt nicht: zurueck zu SRE, kein Nachstellen von Werten
  DAZU       Mengen-Verhaeltnis (vorhergesagt / echt) und Trefferquote der Prognose (Anteil vorhergesagten Verlusts auf
             Opfern, die wirklich verloren) - als Hinweis, nicht als Ziel
Fenster: ab jedem Schnappschuss alle SCHRITT Takte, Laenge H. Echte Verluste aus <protokoll>_treffer.json (auge.treffer).
Aufruf: python werkzeug/gehirn_pruefen.py [protokoll.npz] [H=30] [schritt=30] [spielwerte.json] [gehirn|sim]
  sim = Baustein 3 (simulator.py, Takt fuer Takt); Basis fuer "neue Begegnungen" bleibt Baustein 1 allein"""
import collections
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
D = os.path.join(HIER, "..", "daten")


VORGESCHICHTE = 64       # Takte vor dem Fenster fuer die Zug-Phase (laengster Zugabstand im Pruefstein deutlich darunter)


def laden(pfad):
    import auge
    import speicher
    # offline: auge liest die Phasentabellen dann aus der Programmdatei (SRE-Fix 25.10. 20:05)

    def _offline():
        raise RuntimeError("offline")
    speicher.griff = _offline
    return auge.Protokoll.laden(pfad)


def main(argv):
    pfad = argv[0] if argv else os.path.join(D, "auge_protokoll_20261025_191847.npz")
    H = int(argv[1]) if len(argv) > 1 else 30
    schritt = int(argv[2]) if len(argv) > 2 else 30
    sw_pfad = argv[3] if len(argv) > 3 else os.path.join(D, "spielwerte_20261025_145546.json")   # live, mit bewegung.*
    motor = argv[4] if len(argv) > 4 else "gehirn"
    # argv[5] "von-bis": nur Fenster ganz in diesem Taktbereich (z. B. lueckenloser Abschnitt, AU26); argv[6] Teams "0,2,1,..."
    bereich = tuple(int(x) for x in argv[5].split("-")) if len(argv) > 5 and argv[5] not in ("", "-") else None
    teams = [int(x) for x in argv[6].split(",")] if len(argv) > 6 else None
    import gehirn
    sw = json.load(open(sw_pfad, encoding="utf-8"))
    G = gehirn.Gehirn(sw)
    if motor == "sim":
        import simulator
        S = simulator.Simulator(sw)
    P = laden(pfad)
    tr = json.load(open(pfad.replace(".npz", "_treffer.json"), encoding="utf-8"))["treffer"]
    echt_je_takt = collections.defaultdict(list)            # takt -> [(opfer, verlust, quellen)]
    for t in tr:
        echt_je_takt[t["takt"]].append(t)
    takte = sorted(echt_je_takt)
    import bisect
    summe = collections.Counter()
    zeit_ok = zeit_n = 0
    fenster = 0
    letzter = None
    vorher = collections.deque(maxlen=VORGESCHICHTE)     # Baustein 3: Zug-Phase aus den Takten VOR dem Fenster (AU22)
    for s in P:
        vg = list(vorher)
        vorher.append(s)
        t0 = s.kopf()["takt"]
        if bereich and (t0 < bereich[0] + VORGESCHICHTE or t0 + H > bereich[1]):
            continue
        if letzter is not None and t0 - letzter < schritt:
            continue
        letzter = t0
        einh = s.einheiten_liste()
        progn = S.prognose(s, H, einh, vorgeschichte=vg, teams=teams) if motor == "sim" else G.prognose(s, H, einh)
        basis = G.prognose(s, H, einh, begegnung=False)     # Baustein 1 allein - fuer "neue Begegnungen erfasst"
        echt = collections.Counter()
        besitzer = {}
        echt_geschoss = collections.defaultdict(list)
        for t in takte[bisect.bisect_right(takte, t0):bisect.bisect_right(takte, t0 + H)]:
            for ev in echt_je_takt[t]:
                echt[ev["id"]] += ev["verlust"]
                besitzer[ev["id"]] = ev.get("owner")
                if any(q.get("quelle") == "geschoss" for q in ev["quellen"]):
                    echt_geschoss[ev["id"]].append(t)
        if not echt and not progn:
            continue
        fenster += 1
        summe["echt"] += sum(echt.values())
        summe["echt_getroffen"] += sum(v for o, v in echt.items() if o in progn)
        summe["neu_echt"] += sum(v for o, v in echt.items() if o not in basis)
        summe["neu_erfasst"] += sum(v for o, v in echt.items() if o not in basis and o in progn)
        # getrennt ausgewiesen: Opfer ohne Besitzer (Tiere - Jagd, kein Kampf); Besitzer aus der Treffer-Datei
        summe["neu_echt_tiere"] += sum(v for o, v in echt.items() if o not in basis and besitzer.get(o) == 0)
        summe["neu_erfasst_tiere"] += sum(v for o, v in echt.items() if o not in basis and o in progn and besitzer.get(o) == 0)
        summe["progn"] += sum(p["verlust"] for p in progn.values())
        summe["progn_richtig"] += sum(p["verlust"] for o, p in progn.items() if echt.get(o, 0) > 0)
        for o, p in progn.items():
            for q in p["quellen"]:
                if q["art"] in ("geschoss", "schuss") and q["takt"] <= H:
                    zeit_n += 1
                    if any(abs((t0 + q["takt"]) - te) <= 5 for te in echt_geschoss.get(o, ())):
                        zeit_ok += 1
        for art in ("geschoss", "schuss", "nahkampf", "nahkampf_folge", "begegnung", "begegnung_gegen"):
            summe["progn_" + art] += sum(1 for p in progn.values() for q in p["quellen"] if q["art"] == art)
    quote = summe["echt_getroffen"] / float(max(1, summe["echt"]))
    praez = summe["progn_richtig"] / float(max(1, summe["progn"]))
    zeit = zeit_ok / float(max(1, zeit_n))
    erg = {"protokoll": os.path.basename(pfad), "motor": motor, "bereich": bereich, "H": H, "schritt": schritt, "fenster": fenster,
           "opfer_quote": round(quote, 3), "praezision": round(praez, 3),
           "menge_verhaeltnis": round(summe["progn"] / float(max(1, summe["echt"])), 3),
           "zeit_quote_pm5": round(zeit, 3), "zeit_n": zeit_n,
           "neue_begegnungen_erfasst": round(summe["neu_erfasst"] / float(max(1, summe["neu_echt"])), 4), "neu_echt": summe["neu_echt"], "neu_erfasst": summe["neu_erfasst"],
           "neue_begegnungen_ohne_tiere": round((summe["neu_erfasst"] - summe["neu_erfasst_tiere"]) / float(max(1, summe["neu_echt"] - summe["neu_echt_tiere"])), 4),
           "neu_echt_tiere": summe["neu_echt_tiere"], "neu_erfasst_tiere": summe["neu_erfasst_tiere"],
           "echt_verlust": summe["echt"], "progn_verlust": round(summe["progn"]),
           "quellen_vorhergesagt": {k[6:]: v for k, v in summe.items() if k.startswith("progn_") and k[6:] in ("geschoss", "schuss", "nahkampf", "nahkampf_folge", "begegnung", "begegnung_gegen")}}
    urteil = ("ZIEL ERREICHT" if quote >= 0.8 and zeit >= 0.8 else
              "ABBRUCH: Opfer-Quote unter 50 % - Auge pruefen (SRE), nicht nachstellen" if quote < 0.5 else
              "ZWISCHEN 50 und 80 % - Ursachen je Quelle suchen")
    if motor == "sim":
        # Baustein 3 (Daniel 21:53): Ziel >= 90 % neue Begegnungen ohne Rueckschritt bei Opfer-Quote/Praezision; Abbruch < 75 %
        nb = erg["neue_begegnungen_erfasst"]
        urteil = ("BAUSTEIN 3 ZIEL ERREICHT" if nb >= 0.9 and quote >= 0.8 else
                  "BAUSTEIN 3 ABBRUCH: neue Begegnungen unter 75 % - fehlende Auge-Regel an SRE, nicht nachstellen" if nb < 0.75 else
                  "BAUSTEIN 3 ZWISCHEN 75 und 90 % - Luecke je Quelle zerlegen")
    erg["urteil"] = urteil
    print(json.dumps(erg, ensure_ascii=False, indent=1))
    with open(os.path.join(D, "gehirn_pruefung.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(erg, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
