# -*- coding: utf-8 -*-
"""B-182 (Daniel 10.11. 22:56 "Ja, Versuch starten"): Welche Spielfelder halten bei eigenen Einheiten das Gebaeudeziel und das
Schussziel, und reiten Berittene auf ein fernes Angriffsziel los?

Nur Instanz 2. Ablauf: Hauptmenue, frisches Gefecht Liga_Paradise Plains gegen den Rattenfaenger (KI-Nummer 2), Tempo 40,
angehalten, sobald beide Lords stehen und Takt 150 erreicht ist. Neben unseren Lord gesetzt: 1 Sklave (A_SLAVE 71),
1 Arabischer Schwertkaempfer (A_SWORDSMAN 75), 2 Berittene Bogenschuetzen (A_HARCHER 74); fuer Spieler 2 ein Bauer (Typ 1)
rund 25 Felder vor unserem Lord als nahes Ziel. Befehle wie die Module sie geben:
  Sklave            angriff gebaeude G       (G = naechstes gegnerisches Gebaeude; wie der Brandtrupp)
  Schwertkaempfer   angriff gebaeude G       (wie der Nahkampf-Raid an Gebaeuden)
  Reiter A          angriff ziel W_fern      (gegnerischer Arbeiter ab 100 Feldern; wie die Reiterjagd)
  Reiter B          angriff ziel W_nah       (der gesetzte Bauer; Gegenprobe)
Gelesen: alle Felder der Test-Einheiten aus dem Kern (Leitung) vor dem Befehl und laufend bis 1.500 Takte danach.
Erhofft: ein Feld traegt G oder dessen uid (aus der ANGRIFF-Zeile im ucp3.log), eines das Schussziel.
Widerlegt: kein Feld traegt nach dem Befehl eine der Ziel-Nummern.
Reiter (Vermutung aus S110): A bleibt stehen, B schiesst. Widerlegt: A kommt dem Ziel um mehr als 10 Felder naeher.
Abbruch: keine ANGRIFF-Antwort auf einen Befehl, kein Gefecht nach 90 s, oder wir sind nicht Spieler 1.
Aufruf: python s_zielfelder.py   (schreibt zielfelder_<Zeit>.json neben dieses Skript)
"""
import json
import os
import re
import sys
import time

os.environ["SHC_INSTANZ"] = "2"
import selfaware.game.ucp.befehl as kanal  # noqa: E402
import selfaware.micro.tasks.raids as RA  # noqa: E402
from selfaware.game.kern_leitung import Leitung  # noqa: E402
from selfaware.game.ucp.laden import befehl  # noqa: E402
from selfaware.tools.experiments.serie import zuruecksetzen  # noqa: E402

SPIEL = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz2"
HIER = os.path.dirname(os.path.abspath(__file__))
TEMPO = 40
NACHLAUF = 1500


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def ort(d):
    return (d["x"], d["y"])


def setze(spieler, typ, x, y):
    for z in befehl({"setzeEinheit": {"spieler": spieler, "typ": typ, "x": x, "y": y, "anzahl": 1}}, 1.5):
        m = re.search(r"Nummern ([0-9,]+)", z)
        if m:
            nrs = [int(n) for n in m.group(1).split(",") if int(n) > 0]
            if nrs:
                return nrs[0]
    sys.exit("ABBRUCH: setzeEinheit Spieler %d Typ %d ohne Nummer" % (spieler, typ))


def angriff(einheit, **ziel):
    zeilen = befehl({"angriff": {"einheiten": [einheit], **ziel}}, 1.5, bis="ANGRIFF")
    treffer = [z for z in zeilen if "ANGRIFF" in z]
    if not treffer:
        sys.exit("ABBRUCH: keine ANGRIFF-Antwort fuer Einheit %d (%s): %s" % (einheit, ziel, zeilen[-3:]))
    m = re.search(r"Art (\d+), Ziel (\d+) \(uid (\d+)\)", treffer[-1])
    return {"zeile": treffer[-1].strip()[-160:], "art": int(m.group(1)) if m else None,
            "ziel": int(m.group(2)) if m else None, "uid": int(m.group(3)) if m else None}


def main():
    le = Leitung(SPIEL)
    print("Zuruecksetzen:", zuruecksetzen())
    befehl({"tempo": TEMPO}, 1.0, bis="TEMPO")
    kanal.sende({"player": 1, "pause": False}, 0.5)
    g = {"eigenesGefecht": True, "karte": "Liga_Paradise Plains", "ki": 2, "gegner": 1, "ausgleich": 3,
         "startliste": [0, 1, 246, 246, 246, 246, 246, 246]}
    print("Start:", [z.strip()[-90:] for z in kanal.sende(g, 4, bis="LaunchSkirmishGame zurueck")][-2:])
    befehl({"tempo": TEMPO}, 1.0, bis="TEMPO")
    ende = time.time() + 90
    while time.time() < ende:
        w = le.lesen()
        lords = {e["besitzer"]: e for e in w.einheiten.values() if e["typ"] == 55}
        if len(lords) >= 2 and w.tick >= 150:
            break
        time.sleep(0.5)
    else:
        sys.exit("ABBRUCH: nach 90 s kein Gefecht mit zwei Lords")
    befehl({"pause": True}, 0.5)
    befehl({"eigenerPlatz": 1}, 0.8)
    w = le.lesen()
    if w.ich != 1:
        sys.exit("ABBRUCH: Kern meldet ich = %d, nicht 1" % w.ich)
    lords = {e["besitzer"]: e for e in w.einheiten.values() if e["typ"] == 55}
    heim, feind = ort(lords[1]), ort(lords[2])
    print("Takt", w.tick, "Lord 1 bei", heim, "Lord 2 bei", feind)
    # Ziele
    geb = [(schach(heim, ort(b)), n, b) for n, b in w.gebaeude.items() if b["besitzer"] == 2]
    _, G, gb = min(geb)
    fern = [(schach(heim, ort(e)), n) for n, e in w.einheiten.items() if e["besitzer"] == 2 and e["typ"] in RA.ARBEITER]
    fern = sorted(x for x in fern if x[0] >= 100)
    if not fern:
        sys.exit("ABBRUCH: kein gegnerischer Arbeiter ab 100 Feldern")
    W_fern = fern[0][1]
    richtung = ((feind[0] - heim[0]) / max(1, schach(heim, feind)), (feind[1] - heim[1]) / max(1, schach(heim, feind)))
    nah = (int(heim[0] + 25 * richtung[0]), int(heim[1] + 25 * richtung[1]))
    # Test-Einheiten
    t = {"sklave": setze(1, 71, heim[0] + 3, heim[1] + 3), "schwert": setze(1, 75, heim[0] + 4, heim[1] + 3),
         "reiter_fern": setze(1, 74, heim[0] + 3, heim[1] + 4), "reiter_nah": setze(1, 74, heim[0] + 4, heim[1] + 4)}
    W_nah = setze(2, 1, nah[0], nah[1])
    # 10.11. 23:07 (erster Lauf): Im angehaltenen Spiel schreibt der Kern seine Tabelle nicht neu - gesetzte Einheiten fehlen.
    # Darum ein paar Takte laufen lassen, dann wieder anhalten und erst dann den Ausgangsstand lesen.
    t_set = le.lesen().tick
    befehl({"pause": False}, 0.3)
    while le.lesen().tick < t_set + 6:
        time.sleep(0.1)
    befehl({"pause": True}, 0.5)
    w = le.lesen()
    basis = {k: dict(w.einheiten[n]) for k, n in t.items() if n in w.einheiten}
    if len(basis) != 4:
        sys.exit("ABBRUCH: Test-Einheiten fehlen im Kern: %s" % t)
    print("Ziele: Gebaeude", G, "Typ", gb["typ"], "bei", ort(gb), "| Arbeiter fern", W_fern, "bei", ort(w.einheiten[W_fern]),
          "| Bauer nah", W_nah, "bei", ort(w.einheiten[W_nah]) if W_nah in w.einheiten else "?")
    log = os.path.join(SPIEL, "ucp3.log")
    log_vorher = os.path.getsize(log)
    auftraege = {
        "sklave": angriff(t["sklave"], gebaeude=G),
        "schwert": angriff(t["schwert"], gebaeude=G),
        "reiter_fern": angriff(t["reiter_fern"], ziel=W_fern),
        "reiter_nah": angriff(t["reiter_nah"], ziel=W_nah),
    }
    for k, a in auftraege.items():
        print("Auftrag", k, "->", a["zeile"])
    zielwerte = {"G": G, "W_fern": W_fern, "W_nah": W_nah}
    # Nachlauf
    befehl({"pause": False, "tempo": TEMPO}, 0.3)
    t0 = le.lesen().tick
    # Die ausgefuehrten Angriffe stehen erst nach dem Weiterlaufen im ucp3.log ("eingereiht" kommt im angehaltenen Spiel)
    time.sleep(1.5)
    with open(log, "rb") as f:
        f.seek(log_vorher)
        neu = f.read().decode("utf-8", "replace")
    ausgefuehrt = re.findall(r"ANGRIFF Tick (\d+): (\d+) Einheiten, Gruppe (\d+), Art (\d+), Ziel (\d+) \(uid (\d+)\)", neu)
    print("ausgefuehrt laut ucp3.log:", ausgefuehrt)
    if len(ausgefuehrt) < 4:
        befehl({"pause": True}, 0.5)
        sys.exit("ABBRUCH: nur %d von 4 Angriffen ausgefuehrt" % len(ausgefuehrt))
    for i, (_tk, _n, _gr, art, ziel, uid) in enumerate(ausgefuehrt[:4]):
        k = list(auftraege)[i]
        auftraege[k].update(art=int(art), ziel=int(ziel), uid=int(uid))
        zielwerte["uid_" + k] = int(uid)
    verlauf = []
    while True:
        w = le.lesen()
        z = {"t": w.tick, "einheiten": {k: dict(w.einheiten[n]) for k, n in t.items() if n in w.einheiten},
             "ziele": {"G": dict(w.gebaeude[G]) if G in w.gebaeude else None,
                       "W_fern": dict(w.einheiten[W_fern]) if W_fern in w.einheiten else None,
                       "W_nah": dict(w.einheiten[W_nah]) if W_nah in w.einheiten else None}}
        verlauf.append(z)
        if w.tick >= t0 + NACHLAUF:
            break
        time.sleep(0.25)
    befehl({"pause": True}, 0.5)
    # Auswertung
    aus = {"basis": basis, "auftraege": auftraege, "zielwerte": zielwerte, "heim": heim, "feind": feind}
    print("\nFELDER je Test-Einheit, die nach dem Befehl eine Ziel-Nummer tragen (Feld = Wert -> welches Ziel):")
    befund = {}
    for k in t:
        treffer = {}
        for z in verlauf:
            e = z["einheiten"].get(k)
            if not e:
                continue
            for feld, v in e.items():
                if feld in ("nr", "x", "y", "laufx", "laufy", "leben", "besitzer", "typ"):
                    continue
                for name, zw in zielwerte.items():
                    if v == zw and basis[k].get(feld) != zw:
                        treffer.setdefault(feld, set()).add(name)
        befund[k] = {f: sorted(n) for f, n in treffer.items()}
        print("  %-12s %s" % (k, befund[k] or "kein Feld"))
    aus["befund"] = befund
    print("\nWEG: Abstand zum Ziel (Schach) und Leben des Ziels, alle 300 Takte:")
    naechste = 0
    for z in verlauf:
        if z["t"] < naechste:
            continue
        naechste = z["t"] + 300
        teile = []
        for k, zk in (("sklave", "G"), ("schwert", "G"), ("reiter_fern", "W_fern"), ("reiter_nah", "W_nah")):
            e, ziel = z["einheiten"].get(k), z["ziele"].get(zk)
            teile.append("%s %s" % (k, (schach(ort(e), ort(ziel)), ziel["leben"]) if e and ziel else "weg"))
        print("  Takt %6d: %s" % (z["t"], " | ".join(teile)))
    erst, letzt = verlauf[0]["einheiten"].get("reiter_fern"), verlauf[-1]["einheiten"].get("reiter_fern")
    zf0, zf1 = verlauf[0]["ziele"]["W_fern"], verlauf[-1]["ziele"]["W_fern"]
    if erst and letzt and zf0 and zf1:
        d0, d1 = schach(ort(erst), ort(zf0)), schach(ort(letzt), ort(zf1))
        aus["reiter_fern_abstand"] = [d0, d1]
        print("\nReiter fern: Abstand %d -> %d Felder (%s)" % (d0, d1, "reitet los - Vermutung WIDERLEGT" if d0 - d1 > 10 else "bleibt"))
    aus["verlauf"] = verlauf
    pfad = os.path.join(HIER, "zielfelder_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
    json.dump(aus, open(pfad, "w", encoding="utf-8"), default=list)
    print("geschrieben:", pfad)


if __name__ == "__main__":
    main()
