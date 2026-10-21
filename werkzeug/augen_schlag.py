# -*- coding: utf-8 -*-
"""B-166 Extremtest SCHLAG (Daniel 21.10.2026 22:35: "keine erfundenen Werte - im Code genau rauslesen, wie viel die Einheit pro
Tick haut; die Messung dann abgleichen mit der Realitaet, Differenzen erklaeren, weitere Extremtests").
EIN Streitkolben steht direkt neben EINER Mauerkachel (der ersten auf dem Durchbruch-Weg von (150,150) zu Franz' Lord, Sandkasten
ohne Soldaten) und bekommt den Mauerbefehl auf genau diese Kachel. Jeden Spieltakt direkt aus dem Speicher: Hoehe der Kachel,
animationCycleNumber, nextAttackHurtsWall, Zustand und Feld des Manns.
VORHERSAGE (mechanik.py, aus dem laufenden Spielcode): ein Bild je (animationSpeed+1) Takte, Schlag nach `bilder` Bildern, nur
jeder 2. Schlag trifft, Schaden je Treffer nach Mauernachbarn, erster Treffer evtl. -20. Gemessen wird, ob genau das passiert.
Messgrenze: doppelte vorhergesagte Zeit bis zur Zerstoerung (aus der Vorhersage, nicht angenommen).
Arten (Daniel 22:48 "gerne"): neben - der Mann steht gerade neben der Kachel (erste Fassung, 22:45);
  weg   - der Mann startet am Anfang des Durchbruch-Wegs (150,150): Laufen (Takte je Feld) + Hacken bis das MAUERBIT verschwindet
          (Zerstoerungsmoment laut Code: der Schadenspunkt NACH Hoehe = Boden);
  kante - eine Kachel mit < 2 Mauernachbarn, Hoehe > Boden + 60, ohne Bit 0x10000, mit geradem freien Nachbarfeld in Gebiet 1:
          Code sagt erster Treffer -20 - 7, danach -7.
Ergebnis: daten/augen_schlag.jsonl.  Aufruf: SHC_INSTANZ=5 python werkzeug/augen_schlag.py [art=neben|weg|kante]
"""
import json
import os
import re
import sys
import time

os.environ.setdefault("SHC_INSTANZ", "5")
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import numpy as np  # noqa: E402

import feldzug  # noqa: E402
import mechanik  # noqa: E402
import shc  # noqa: E402
import speicher  # noqa: E402
from laden import befehl  # noqa: E402
from waechter import lies_gebaeude, lies_lagebild  # noqa: E402

AUS = os.path.join(HIER, "..", "daten", "augen_schlag.jsonl")
E0, ES = 0x0138854C, 1168


def feldnr(x, y):
    xs, ys, ks = speicher.felder()
    return int(ks[np.nonzero((xs == x) & (ys == y))[0][0]])


def kante_suchen(m, h, logik, geb, boden_eb, lp):
    """Kachel fuer die Art kante: < 2 gerade Mauernachbarn, hoeher als Boden + 60, ohne Bit 0x10000, ein gerades Nachbarfeld in
    Gebiet 1 (frei) - die dem Lord naechste."""
    beste = None
    xs, ys = np.nonzero(m)
    for x, y in zip(xs.tolist(), ys.tolist()):
        if logik[x, y] & 0x10000 or int(h[x, y]) <= 60:
            continue
        gerade = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        if sum(1 for q in gerade if logik[q] & 0x10000100) >= 2:
            continue
        frei = [q for q in gerade if geb[q] == 1 and not m[q]]
        if frei:
            w = (max(abs(x - lp[0]), abs(y - lp[1])), x, y)
            if beste is None or w < beste[0]:
                beste = (w, (x, y), frei[0])
    return (beste[1], beste[2]) if beste else (None, None)


def main(art="neben"):
    print("OK:", shc.sandkasten(nur_soldaten="ja"), flush=True)
    befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
    L = lies_lagebild(neu_holen=False)
    lp = next((e["x"], e["y"]) for e in L.values() if e["typ"] == 55 and e["besitzer"] == 2 and e["leben"] > 0)
    G = lies_gebaeude()
    wk = speicher.wegkarte()
    m, h = speicher.mauern(2)
    f = feldzug.Feldzug(1, (80, 260))
    geb = f._ohne_feindtore(wk["gebiet"], wk["gebaeude"], G)
    plan = f._durchbruch(geb, m, h, (150, 150), lp)
    logik = speicher.ebene(speicher.LOGIK, 4)
    kq = plan["kachel"]
    if art == "kante":
        kq, neben = kante_suchen(m, h, logik, geb, None, lp)
        if kq is None:
            raise SystemExit("UNGUELTIG: keine Kachel mit < 2 Mauernachbarn, > 60 hoch, ohne Bit 0x10000 und geradem Zugang")
    elif kq is None:
        raise SystemExit("UNGUELTIG: kein Durchbruch-Weg")
    else:
        neben = plan["weg"][plan["weg"].index(kq) - 1]
    start = plan["weg"][0] if art == "weg" else neben
    k = feldnr(*kq)
    nachbarn = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if logik[kq[0] + dx, kq[1] + dy] & 0x10000100)
    mk = mechanik.streitkolben()
    hoehe0 = speicher.lies(speicher.HOEHE + k, 1)[0]
    boden = speicher.lies(speicher.BODEN + k, 1)[0]
    bit = bool(logik[kq] & 0x10000)
    d = mechanik.kachel_schaden(mk["mauer"], nachbarn)
    n_tr = mechanik.treffer_bis_zerstoert(hoehe0, boden, d, True, bit)
    vorher = n_tr * mk["takte_je_treffer"]
    print("Kachel %s Hoehe %d Boden %d (ueber Boden %d), Mauernachbarn %d, Bit 0x10000 %s | Code: %s | Vorhersage: %d Schaden je "
          "Treffer, %d Treffer, %d Takte ab dem ersten Schwung | Mann auf %s" % (
              kq, hoehe0, boden, hoehe0 - boden, nachbarn, bit, mk, d, n_tr, vorher, neben), flush=True)
    t = shc.setze(spieler=1, typ=26, x=start[0] - 1, y=start[1] - 1, anzahl=1)      # setze: 1 Feld weiter (gemessen 17.10.)
    nr = int(re.search(r"Nummern \[([0-9, ]+)\]", t).group(1).split(",")[0])
    b = speicher.lies(E0 + nr * ES, ES)
    steht = (int.from_bytes(b[0xC4:0xC6], "little", signed=True), int.from_bytes(b[0xC6:0xC8], "little", signed=True))
    print("Art %s: Einheit %d steht auf %s (Soll %s), Zugangsfeld %s, Weglaenge bis dort %d Felder" % (
        art, nr, steht, start, neben, plan["weg"].index(kq) if art == "weg" else 0), flush=True)
    befehl({"angriff": {"einheiten": [nr], "mauer": [lp[0], lp[1], 2, 30, kq[0], kq[1]]}}, 1.0)
    lies = speicher.lies
    tick0 = int.from_bytes(lies(shc.TICK, 4), "little")
    befehl({"pause": False, "tempo": 40}, 0.2)
    reihe, letzt = [], None
    # Grenzen nur aus dem Code: vor der Ankunft "steht" der Mann, wenn er 2 Schwuenge lang (takte_je_treffer) das Feld nicht
    # wechselt; ab der Ankunft (gerade neben der Kachel) die doppelte vorhergesagte Hackzeit
    still, ankunft, letzt_feld, ziele, hziel = 0, None, None, {}, []
    while True:
        tk = int.from_bytes(lies(shc.TICK, 4), "little")
        if tk == letzt:
            continue
        letzt = tk
        b = lies(E0 + nr * ES, ES)
        hh = lies(speicher.HOEHE + k, 1)[0]
        mauerbit = int.from_bytes(lies(speicher.LOGIK + 4 * k, 4), "little") & 0x100
        ziel = int.from_bytes(b[0x3A8:0x3AC], "little", signed=True)      # targetedBuildingTile (Code: setDestinationNear...)
        h_ziel = lies(speicher.HOEHE + ziel, 1)[0] if 0 < ziel < 80400 else -1
        ziele[ziel] = ziele.get(ziel, 0) + 1
        hziel.append((tk - tick0, ziel, h_ziel))
        reihe.append((tk - tick0, hh, int.from_bytes(b[mechanik.E_ZYKLUS:mechanik.E_ZYKLUS + 4], "little", signed=True),
                      b[mechanik.E_TREFFER], int.from_bytes(b[0x8C:0x8E], "little", signed=True),
                      int.from_bytes(b[0xC4:0xC6], "little", signed=True), int.from_bytes(b[0xC6:0xC8], "little", signed=True),
                      mauerbit))
        feld = reihe[-1][5:7]
        if ankunft is None and abs(feld[0] - kq[0]) + abs(feld[1] - kq[1]) == 1:
            ankunft = tk - tick0
        still = still + 1 if feld == letzt_feld and (len(reihe) < 2 or reihe[-1][3] == reihe[-2][3]) else 0
        letzt_feld = feld
        if not mauerbit:
            break
        if ankunft is None and still >= mk["takte_je_treffer"]:
            print("ABBRUCH: steht %d Takte vor der Ankunft auf %s" % (still, feld), flush=True)
            break
        if ankunft is not None and tk - tick0 - ankunft >= 2 * vorher:
            break
    befehl({"pause": True}, 0.3)
    luecken = sum(1 for a, c in zip(reihe, reihe[1:]) if c[0] - a[0] != 1)
    schlaege = [r[0] for a, r in zip(reihe, reihe[1:]) if r[3] != a[3]]
    spruenge = [(r[0], a[1] - r[1], r[3]) for a, r in zip(reihe, reihe[1:]) if r[1] != a[1]]
    bildwechsel = [r[0] for a, r in zip(reihe, reihe[1:]) if r[2] != a[2]]
    abst = lambda xs: [b_ - a_ for a_, b_ in zip(xs, xs[1:])]
    erg = {"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "kachel": kq, "hoehe0": hoehe0, "boden": boden, "nachbarn": nachbarn,
           "code": mk, "vorhersage": {"schaden": d, "treffer": n_tr, "takte": vorher}, "takte_gemessen": reihe[-1][0],
           "luecken": luecken, "schlaege": schlaege[:100], "spruenge": spruenge[:100],
           "bildabstand": sorted(set(abst(bildwechsel)))[:20], "schlagabstand": abst(schlaege)[:100],
           "trefferabstand": abst([s[0] for s in spruenge])[:100], "reihe": reihe[:400]}
    xs_, ys_, ks_ = speicher.felder()
    kxy = {int(kk): (int(xx), int(yy)) for xx, yy, kk in zip(xs_, ys_, ks_)}
    erg["ziele"] = {str(kxy.get(z_, z_)): n_ for z_, n_ in ziele.items()}
    zsp = [(a[0], kxy.get(c[1], c[1]), a[2] - c[2]) for a, c in zip(hziel, hziel[1:]) if a[1] == c[1] and c[2] != a[2]]
    erg["ziel_spruenge"] = zsp[:200]
    print("TATSAECHLICHE ZIELE (Kachel: Takte):", erg["ziele"], flush=True)
    print("Hoehenspruenge am tatsaechlichen Ziel (Takt, Kachel, minus):", zsp[:16], flush=True)
    print("Takte gelesen %d, Luecken %d" % (len(reihe), luecken), flush=True)
    print("Bildwechsel-Abstaende (Takte):", erg["bildabstand"], flush=True)
    print("Schlag-Abstaende (nextAttackHurtsWall wechselt):", erg["schlagabstand"][:20], flush=True)
    print("Hoehenspruenge (Takt, minus, Schalter danach):", spruenge[:20], flush=True)
    print("Treffer-Abstaende:", erg["trefferabstand"][:20], flush=True)
    an = next((r for r in reihe if abs(r[5] - kq[0]) + abs(r[6] - kq[1]) == 1), None)
    if art == "weg" and an:
        lauf = [r for r in reihe if r[0] <= an[0]]
        felder = sum(max(abs(a[5] - b_[5]), abs(a[6] - b_[6])) for a, b_ in zip(lauf, lauf[1:]))
        erg["laufen"] = {"angekommen": an[0], "felder": felder, "takte_je_feld": an[0] / float(felder) if felder else None,
                         "feldwechsel": abst([r[0] for a, r in zip(lauf, lauf[1:]) if (r[5], r[6]) != (a[5], a[6])])[:200]}
        print("LAUFEN: angekommen Takt %d nach %d Feldern = %.2f Takte je Feld; Feldwechsel-Abstaende %s" % (
            an[0], felder, erg["laufen"]["takte_je_feld"] or -1, sorted(set(erg["laufen"]["feldwechsel"]))[:15]), flush=True)
    weg_t = next((r[0] for r in reihe if not r[7]), None)
    erster = schlaege[0] if schlaege else None
    erg["mauerbit_weg"] = weg_t
    print("MAUERBIT WEG bei Takt %s (erster Schwung-Wechsel Takt %s) | Treffer bis dahin %d | Vorhersage %d Treffer = %d Takte ab Schwungbeginn" % (
        weg_t, erster, len(spruenge), n_tr, vorher), flush=True)
    with open(AUS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(erg, ensure_ascii=False, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)) + "\n")


if __name__ == "__main__":
    a = dict(x.split("=", 1) for x in sys.argv[1:])
    main(a.get("art", "neben"))
