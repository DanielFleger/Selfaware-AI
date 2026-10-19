# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer partie_vergleich.py (19.10.). Kuenstliche Partie: zwei Spieler mit Bergfried und je 10
Holzfaellerhuetten, die ab Tick 1.000 Ware zeigen; Runden alle 100 Ticks bis 30.000. Vorher festgelegt:
  1. beide gleich -> kein Nachteil
  2. Spieler 2 verliert bei Tick 12.000 8 liefernde Huetten, baut 8 neue (ohne Ware), die bei 13.000 wieder weg sind
     -> Nachteil Spieler 2; Einbruch "liefernde Betriebe" zwischen 10.000 und 14.000; im Geschehen: Spieler 2 verlor
     liefernde Holzfaellerhuette 8 und ohne Ware 8, Spieler 1 keine
  3. wie 2, aber Spieler 2 fuehrt bei 20.000-21.999 kurz (2 Fenster, 15 Huetten) -> "hinten ab" bleibt vor 14.000;
     fuehrt er 6 Fenster lang (20.000-25.999) -> "hinten ab" erst danach (ab 26.000)
  4. bei Tick 29.000 verschwinden Bergfried und alle Gebaeude von Spieler 2 -> ausgewertet bis 28.900, die verschwundenen
     zaehlen NICHT als Verluste (im Geschehen bleibt es bei 8 + 8)
  5. Statuszeile Spieler 2 ab 12.000 mit 25 am Feuer, 50 Leute, 90 Plaetze -> L27-Zeile mit "es fehlen Arbeitsplaetze";
     mit 20 am Feuer -> ohne diesen Zusatz
  6. echte Partie 1018j (wenn die Dateien da sind, sonst UEBERSPRUNGEN): Nachteil Spieler 2, Einbruch in einer
     Wirtschafts-Kennzahl zwischen 15.000 und 19.000; im Geschehen verlor Spieler 2 mindestens 10 liefernde Holzfaeller-
     huetten und mehr als Spieler 1; Spieler 1 verlor mehr Huetten ohne Ware als liefernde (Handauswertung 19.10. 16:40)
Gegenprobe: mit "alt" (a) gilt jeder Betrieb ab dem Bau als liefernd, (b) wird nach dem Bergfried-Verlust weiter
ausgewertet, (c) unterbricht jede Fuehrung den Rueckstand -> Faelle 2, 3, 4 und 6 rot.
Aufruf: python werkzeug/partie_vergleich_pruefen.py [alt]"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import partie_vergleich as P

ALT = len(sys.argv) > 1 and sys.argv[1] == "alt"
if ALT:
    _runde = P.Lauf.runde

    def _alt_runde(self, t, st, E, G, sp_st=None):
        G = [dict(g, vorrat=max(g.get("vorrat", 0), 1)) for g in G]           # (a) jeder Betrieb gilt sofort als liefernd
        self.vorbei = None
        if self.spieler:                                                     # (b) Bergfried-Schnitt aus
            G = G + [{"besitzer": p, "typ": P.BERGFRIED, "x": 0, "y": 0, "uid": 900 + p, "vorrat": 0} for p in self.spieler]
        return _runde(self, t, st, E, G, sp_st)
    P.Lauf.runde = _alt_runde
    P.MIN_STRECKE_ALT = True
    _hinten_ab = P.hinten_ab

    def _alt_hinten_ab(ra, rb):                                              # (c) jede Fuehrung unterbricht
        a, b = P.glatt(ra), P.glatt(rb)
        n = min(len(a), len(b))
        start = None
        for i in range(n - 1, -1, -1):
            if a[i][1] < b[i][1]:
                start = i
            else:
                break
        return None if start is None or n - start < P.MIN_STRECKE else a[start][0]
    P.hinten_ab = _alt_hinten_ab


def g(p, typ, uid, vorrat=0, x=10, y=10):
    return {"besitzer": p, "typ": typ, "x": x, "y": y, "uid": uid, "vorrat": vorrat}


def partie(verlust=False, fuehrung=0, untergang=False, feuer=None):
    """Kuenstliche Partie -> Lauf. fuehrung: Fenster ab 20.000, in denen Spieler 2 15 liefernde Huetten hat."""
    lauf = P.Lauf()
    for t in range(0, 30001, 100):
        G = []
        for p in (1, 2):
            if untergang and p == 2 and t >= 29000:
                continue
            G.append(g(p, P.BERGFRIED, 100 * p))
            for k in range(10):
                weg = p == 2 and verlust and k < 8 and t >= 12000
                if not weg:
                    G.append(g(p, 3, 100 * p + 1 + k, vorrat=1 if t >= 1000 else 0, x=40 + k, y=40 * p))
            if p == 2 and verlust and 12500 <= t < 13000:
                G += [g(2, 3, 300 + k, x=60 + k, y=80) for k in range(8)]           # Neubauten ohne Ware
            if p == 2 and 20000 <= t < 20000 + fuehrung * 1000:
                G += [g(2, 3, 400 + k, vorrat=1, x=70 + k, y=80) for k in range(13)]
        lauf.runde(t, {}, [], G)
        if feuer is not None and t >= 12000:
            lauf.statuszeile(t, {"feuer": feuer, "leute": 50, "platz": 90}, 2)
    return lauf


def main():
    ok = []

    def pruefe(nr, text, bed):
        ok.append(bool(bed))
        print("%-4s %d %s" % ("OK" if bed else "ROT", nr, text), flush=True)

    e1 = P.auswerten(partie())
    pruefe(1, "gleich: Nachteile %s" % [(x["hinten"], x["ab"]) for x in e1["paare"]], not e1["paare"])

    e2 = P.auswerten(partie(verlust=True))
    pa = [x for x in e2["paare"] if x["hinten"] == 2]
    br = pa[0]["einbruch"].get("liefernd") if pa else None
    ges = "\n".join(pa[0]["warum"]) if pa else ""
    pruefe(2, "Verlust: Einbruch liefernd %s; Geschehen: %s" % (br and br[0] * 1000, ges.replace("\n", " | ")[:400]),
           pa and br and 10000 <= br[0] * 1000 <= 14000
           and "Spieler 2 verlor liefernde Betriebe: Holzfaellerhuette 8; verlor Betriebe ohne je gesehene Ware: Holzfaellerhuette 8" in ges
           and "Spieler 1 verlor liefernde Betriebe: keine; verlor Betriebe ohne je gesehene Ware: keine" in ges)

    e3a = P.auswerten(partie(verlust=True, fuehrung=2))
    e3b = P.auswerten(partie(verlust=True, fuehrung=6))
    ab_a = [x["ab"].get("liefernd") for x in e3a["paare"] if x["hinten"] == 2]
    ab_b = [x["ab"].get("liefernd") for x in e3b["paare"] if x["hinten"] == 2]
    pruefe(3, "kurze Fuehrung: hinten ab %s; lange Fuehrung: hinten ab %s" % ([a and a * 1000 for a in ab_a], [b and b * 1000 for b in ab_b]),
           ab_a and ab_a[0] is not None and ab_a[0] * 1000 < 14000 and ab_b and ab_b[0] is not None and ab_b[0] * 1000 >= 26000)

    l4 = partie(verlust=True, untergang=True)
    e4 = P.auswerten(l4)
    pa4 = [x for x in e4["paare"] if x["hinten"] == 2]
    ges4 = "\n".join(pa4[0]["warum"]) if pa4 else ""
    v_lief, v_nie, _ = P.verluste(l4, 2, 0, 40)
    pruefe(4, "Untergang bei 29.000: ausgewertet bis %s, vorbei %s, Verluste ueber die ganze Partie liefernd %d / ohne Ware %d" % (
        e4["bis"], e4["vorbei"], sum(v_lief.values()), sum(v_nie.values())),
        e4["bis"] == 28900 and e4["vorbei"] == 29000 and sum(v_lief.values()) == 8 and sum(v_nie.values()) == 8 and pa4)

    e5a = P.auswerten(partie(verlust=True, feuer=25))
    e5b = P.auswerten(partie(verlust=True, feuer=20))
    z5a = [z for x in e5a["paare"] if x["hinten"] == 2 for z in x["warum"] if "L27" in z]
    z5b = [z for x in e5b["paare"] if x["hinten"] == 2 for z in x["warum"] if "L27" in z]
    pruefe(5, "L27 bei 25: %s | bei 20: %s" % (z5a, z5b),
           z5a and "es fehlen Arbeitsplaetze" in z5a[0] and z5b and "es fehlen Arbeitsplaetze" not in z5b[0])

    D = os.path.join(HIER, "..", "daten")
    lage = [os.path.join(D, "lage_20261019_121535_i4.jsonl.gz"), os.path.join(D, "lage_20261019_121535_i4_sp2.jsonl.gz")]
    ertrag = [os.path.join(D, "ertrag_live_20261019_121535_i4.jsonl"), os.path.join(D, "ertrag_live_20261019_121535_i4_sp2.jsonl")]
    if not all(os.path.exists(p) for p in lage + ertrag):
        print("UEBERSPRUNGEN 6 (Dateien von 1018j fehlen)")
    else:
        e6 = P.analyse(lage, ertrag)
        pa6 = [x for x in e6["paare"] if x["hinten"] == 2]
        g_e, w_e = pa6[0]["entscheidend"] if pa6 else (None, None)
        lauf_w0, lauf_w1 = (w_e - P.UMFELD, w_e + P.UMFELD - 1) if w_e is not None else (0, 0)
        # dieselbe Zaehlung wie im Geschehen, hier aus den Zahlen statt aus dem Text
        import re
        ges6 = "\n".join(pa6[0]["warum"]) if pa6 else ""
        def zahl(sp, art):
            m = re.search(r"Spieler %d verlor liefernde Betriebe: ([^;]*); verlor Betriebe ohne je gesehene Ware: ([^;]*)" % sp, ges6)
            if not m:
                return 0
            teil = m.group(1 if art == "liefernd" else 2)
            m2 = re.search(r"Holzfaellerhuette (\d+)", teil)
            return int(m2.group(1)) if m2 else 0
        l2, l1, n1 = zahl(2, "liefernd"), zahl(1, "liefernd"), zahl(1, "nie")
        pruefe(6, "1018j: Einbruch %s bei %s; Holzfaeller liefernd verloren Sp2 %d, Sp1 %d; Sp1 ohne Ware %d" % (
            g_e, w_e and w_e * 1000, l2, l1, n1),
            pa6 and g_e in P.WIRTSCHAFT and 15000 <= w_e * 1000 <= 19000 and l2 >= 10 and l2 > l1 and n1 > l1)
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
