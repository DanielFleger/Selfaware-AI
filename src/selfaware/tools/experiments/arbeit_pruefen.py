# -*- coding: utf-8 -*-
"""Arbeiten sie nach Zurueckrufen + Loslassen WIRKLICH wieder? (04.10.2026)

gruppe_halten.py mass nur Ziel und Ort. Hier zwei haertere Messungen im selben Zeitfenster
(1200 Ticks nach dem Loslassen) gegen eine Kontrolle ohne jeden Eingriff:
  KREISLAUF  Zustand (+0x2C0) jeder Einheit, alle 100 Ticks gelesen: >= 2 verschiedene Werte
  WARE       Vorrat der Ware bei Spieler (PlayerData + 0x4D0 + Ware*4; Apfel = 13)
  ABLIEFERN  je Einheit: Ware dabei (+0x388 > 0), in der naechsten Aufnahme nicht mehr
Erstes Kriterium (vorher festgelegt, 19:09): Kreislauf >= 90 % UND Warenzuwachs >= halb so gross
wie in der Kontrolle. Es war schlecht gestellt: der Vorrat ist Zulieferung minus Verbrauch und
sank in BEIDEN Laeufen. Neues Kriterium (19:13, nach diesem Befund, offen benannt): Kreislauf
>= 90 % UND Ablieferungen >= halb so viele wie in der Kontrolle. Der Vorrat wird nur mitgeschrieben.

Aufruf:  uv run python -m selfaware.tools.experiments.arbeit_pruefen "<Spielstand>" <spieler> <einheitentyp> <gebaeudetyp> <ware> [--fenster=3600]
         (Ablieferungen zusaetzlich je 600 Ticks: wie lange dauert die Erholung?)
         z. B. "Walltest 4" 2 13 19 13
"""

from selfaware import workspace as _workspace
import io, json, os, re, sys, time

from selfaware.game.ucp.laden import lade_stand, befehl, peek
from selfaware.game.ucp.steuerkarte import laufe

EINTRAG = re.compile(r"(\d+):Z(-?\d+)/U-?\d+/W(-?\d+)/")

def ware(sp, w):
    return peek(0x0115BDF8 + sp * 0x39F4 + 0x4D0 + w * 4)[0]

def zustaende(sp, typ):
    z = " ".join(befehl({"arbeitsplatz": {"spieler": sp, "typ": typ}}, 1.0))
    return {int(a): (int(b), int(c)) for a, b, c in EINTRAG.findall(z)}

FENSTER = 1200

def fenster(sp, typ, w):
    """FENSTER Ticks in 100er-Schritten: Zustaende je Einheit, Warenvorrat."""
    befehl({"tempo": 1000}, 0.5)
    vorrat = [ware(sp, w)]
    verlauf = {}
    for _ in range(FENSTER // 100):
        laufe(100)
        for nr, zw in zustaende(sp, typ).items():
            verlauf.setdefault(nr, []).append(zw)
        vorrat.append(ware(sp, w))
    return verlauf, vorrat

def main():
    global FENSTER
    stand, sp, typ, gtyp, w = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    FENSTER = next((int(a[10:]) for a in sys.argv[6:] if a.startswith("--fenster=")), FENSTER)
    # Kontrolle: 1200 Ticks nichts, dann das Fenster
    lade_stand(stand, mit_bild=False)
    befehl({"tempo": 1000}, 0.5)
    for _ in range(12):
        laufe(100)
    k_verlauf, k_vorrat = fenster(sp, typ, w)
    # Versuch: zurueckrufen + 1200 Ticks halten, loslassen "arbeit", dann das Fenster
    lade_stand(stand, mit_bild=False)
    print(befehl({"halten": {"spieler": sp, "typ": typ, "zu": gtyp}}, 1.0))
    befehl({"tempo": 1000}, 0.5)
    for _ in range(12):
        laufe(100)
    print(befehl({"halten": {"zurueck": "arbeit"}}, 1.0))
    v_verlauf, v_vorrat = fenster(sp, typ, w)
    def kreislauf(verlauf):
        return sum(1 for z in verlauf.values() if len(set(a for a, _ in z)) >= 2), len(verlauf)
    def ablieferungen(verlauf, von=0, bis=10 ** 6):
        return sum(1 for z in verlauf.values() for i, ((a, b), (c, d)) in enumerate(zip(z, z[1:]))
                   if b > 0 and d == 0 and von <= i < bis)
    stufen = [(i, i + 6) for i in range(0, FENSTER // 100, 6)]
    print("ABLIEFERN je 600 Ticks: Kontrolle %s | nach Loslassen %s" % (
        [ablieferungen(k_verlauf, a, b) for a, b in stufen], [ablieferungen(v_verlauf, a, b) for a, b in stufen]))
    kk, kn = kreislauf(k_verlauf)
    vk, vn = kreislauf(v_verlauf)
    ka, va = ablieferungen(k_verlauf), ablieferungen(v_verlauf)
    print("KREISLAUF: Kontrolle %d von %d, nach Loslassen %d von %d" % (kk, kn, vk, vn))
    print("ABLIEFERN: Kontrolle %d, nach Loslassen %d (in %d Ticks, Aufnahme alle 100)" % (ka, va, FENSTER))
    print("VORRAT Ware %d alle 100 Ticks: Kontrolle %s | nach Loslassen %s" % (w, k_vorrat, v_vorrat))
    gilt = vk >= 0.9 * vn and va >= 0.5 * ka
    print("URTEIL: %s" % ("arbeitet wirklich wieder" if gilt else "NICHT erfuellt"))
    io.open(os.path.join(_workspace.DATA, 'arbeit_pruefen_%s.json' % time.strftime('%H%M%S')), "w", encoding="utf-8").write(json.dumps({
        "stand": stand, "spieler": sp, "typ": typ, "ware": w, "kontrolle": {"zustaende": k_verlauf, "vorrat": k_vorrat},
        "versuch": {"zustaende": v_verlauf, "vorrat": v_vorrat}}, indent=1))

if __name__ == "__main__":
    main()
