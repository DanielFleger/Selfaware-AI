# -*- coding: utf-8 -*-
"""Laufwegbeweis fuer die Weg-Ebene (B-211, SRE 24.10.2026).

Frage: Stimmt das, was das Spiel je Feld als erlaubte Schritte fuehrt (PathLinkageLayer 0x01E1E4F8, ein Byte,
acht Bits), mit dem ueberein, was laufende Einheiten WIRKLICH tun? Bisher war W1 nur aus dem Code abgelesen
("ungeprueft"), die Codex-Vergleiche (EK-001/EK-002, 20.000 isolierte Aufrufe) hatten keinen einzigen echten Laufweg.

Quelle, ohne Spielstart: die Arbeitsgang-/Aufbau-Messungen in daten/ (arbeitsgang_messen.py, 06.-12.10.2026).
Jede hat (a) "EW Orte Tick t: nr@(x,y) ..." alle 2 Takte fuer die beobachteten Arbeiter und (b) eine Wegkarte
(_wegkarte.txt, logik.lua-Befehl "wegkarte") aus demselben Spiel: je Feld link:gebaeude:gebiet:logik:hoehe:typ.
Laufen dauert >= 16 Takte je Feld (L1), bei 2 Takten Abtastung wird also kein Schritt uebersprungen.

Totschlagtest (vorher festgelegt):
  H1  Jeder beobachtete Ein-Feld-Schritt (dx, dy) hat im Startfeld das Bit RICHTUNG[(dx, dy)] gesetzt
      (1 N = y-1, 2 NO, 4 O = x+1, 8 SO, 0x10 S, 0x20 SW, 0x40 W, 0x80 NW).
      Widerlegt, wenn die Verstossquote der echten Zuordnung nicht deutlich unter JEDER der 15 anderen
      Zuordnungen (7 Drehungen, 8 Spiegelungen) liegt - dann waere die Richtung der Bits nicht belegt.
      Bekannte Ausnahme (W9): Arbeiter treten auf Lagerteile, obwohl das Byte es verbietet. Die wird getrennt
      gezaehlt (nach Gebaeudeart des Zielfelds), nicht versteckt.
  H3  Rueckrichtung: ist im Zielfeld das Gegenbit gesetzt? (Symmetrie der Ebene, nur Mass, keine These)
Was NICHT geprueft wird: die Gebiets-Ebene (0x01DF70D8). Die logik.lua der Messungen vom 06.-12.10. las sie
noch von 0x01DF6FD8 (B-148: 128 Felder daneben), die Spalte "gebiet" dieser Dateien ist daher unbrauchbar.
Ebenso nicht: Uebergaenge zwischen Gebieten (Torhaus, Treppe, Wegabfrage 0x004A5320) - Arbeiter bleiben am Boden.

Grenze der Quelle: die Wegkarte ist ein Augenblick (Takt im Kopf), die Orte laufen bis zu 20.000 Takte weiter;
spaeter gebaute Gebaeude aendern die Bytes. Deshalb werden Verstoesse auch nach Takt-Abstand zur Wegkarte und
danach getrennt, ob Start- und Zielfeld in der Wegkarte frei (kein Gebaeude) waren.

Aufruf: python werkzeug/engine_knowledge/laufweg_beweis.py [daten/arbeitsgang_*.json ...]
Schreibt daten/laufweg_beweis_<zeit>.json und druckt die Tafel.
"""
import glob
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
WERKZEUG = os.path.dirname(HIER)
sys.path.insert(0, WERKZEUG)
import wegkarte as W  # noqa: E402  (RICHTUNG, GEGEN, lesen, kurzname)

D = os.path.join(WERKZEUG, "..", "daten")
BIT = {v: k for k, v in W.RICHTUNG.items()}          # (dx, dy) -> Bit, die echte Zuordnung
SCHRITTE = list(BIT)                                  # 8 Nachbarn


def zuordnungen():
    """16 Kandidaten: die echte Zuordnung, 7 Drehungen um je 45 Grad, und dieselben 8 gespiegelt (x -> -x).
    Jede ist {(dx, dy): bit}. Nur die echte darf (fast) ohne Verstoss sein."""
    ring = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]   # im Uhrzeigersinn ab N
    bits = [BIT[s] for s in ring]
    aus = {}
    for spiegel in (False, True):
        for dreh in range(8):
            z = {}
            for i, s in enumerate(ring):
                r = (-s[0], s[1]) if spiegel else s
                z[r] = bits[(i + dreh) % 8]
            name = ("gespiegelt " if spiegel else "") + ("echt" if dreh == 0 else "+%d x 45 Grad" % dreh)
            aus[name] = z
    return aus


def orte(ew):
    """{nr: [(t, x, y), ...]} aus den EW-Orte-Zeilen."""
    s = defaultdict(list)
    for z in ew:
        m = re.search(r"EW Orte Tick (\d+): (.*)", z)
        if m:
            t = int(m.group(1))
            for nr, x, y in re.findall(r"(\d+)@\((-?\d+),(-?\d+)\)", m.group(2)):
                s[int(nr)].append((t, int(x), int(y)))
    return s


def schritte(reihe):
    """[(t, von, nach)] - jeder Ortswechsel; Ein-Feld-Schritte und Spruenge (> 1 Feld) werden spaeter getrennt."""
    aus = []
    for a, b in zip(reihe, reihe[1:]):
        if a[1:] != b[1:]:
            aus.append((b[0], a[1:], b[1:]))
    return aus


def pruefen(pfad, Z):
    erg = json.load(open(pfad, encoding="utf-8"))
    k = W.lesen(pfad.replace(".json", "_wegkarte.txt"))
    f = k["f"]
    e = {"datei": os.path.basename(pfad), "wegkarte_tick": k["tick"], "fenster": [k["x0"], k["y0"], k["x1"], k["y1"]],
         "arbeiter": len(erg.get("arbeiter", {})), "schritte": 0, "spruenge": 0, "ausserhalb": 0,
         "verstoesse_je_zuordnung": {}, "verstoesse_echt": [], "ziel_gebaeude": Counter(), "start_gesperrt": 0,
         "beide_frei": {"schritte": 0, "verstoesse": 0}, "nach_takt": defaultdict(lambda: [0, 0]),
         "gegenbit_fehlt": 0, "gegenbit_geprueft": 0}
    alle = []
    for nr, reihe in orte(erg.get("ew", [])).items():
        for t, von, nach in schritte(reihe):
            d = (nach[0] - von[0], nach[1] - von[1])
            if max(abs(d[0]), abs(d[1])) != 1:
                e["spruenge"] += 1
                continue
            if von not in f or nach not in f:
                e["ausserhalb"] += 1
                continue
            alle.append((t, von, nach, d, nr))
    e["schritte"] = len(alle)
    for name, z in Z.items():
        e["verstoesse_je_zuordnung"][name] = sum(1 for t, von, nach, d, nr in alle if not f[von][0] & z[d])
    for t, von, nach, d, nr in alle:
        v, n = f[von], f[nach]
        frei = v[1] == 0 and n[1] == 0
        band = "%d+" % (min((t - k["tick"]) // 2000, 5) * 2000) if t >= k["tick"] else "vor Wegkarte"
        e["nach_takt"][band][0] += 1
        if frei:
            e["beide_frei"]["schritte"] += 1
        if v[0] & BIT[d]:
            e["gegenbit_geprueft"] += 1
            if not n[0] & W.GEGEN[BIT[d]]:
                e["gegenbit_fehlt"] += 1
            continue
        e["nach_takt"][band][1] += 1
        if frei:
            e["beide_frei"]["verstoesse"] += 1
        if v[0] == 0:
            e["start_gesperrt"] += 1
        ziel = W.kurzname(n[5]) if n[1] else "Boden"
        e["ziel_gebaeude"][ziel] += 1
        e["verstoesse_echt"].append({"t": t, "nr": nr, "von": list(von), "nach": list(nach), "link_von": "%02x" % v[0],
                                     "link_nach": "%02x" % n[0], "ziel": ziel, "start": W.kurzname(v[5]) if v[1] else "Boden"})
    e["ziel_gebaeude"] = dict(e["ziel_gebaeude"])
    e["nach_takt"] = dict(e["nach_takt"])
    return e


def main():
    pfade = sys.argv[1:] or sorted(p for p in glob.glob(os.path.join(D, "arbeitsgang*.json")) + glob.glob(os.path.join(D, "aufbau_*.json"))
                                  if not p.endswith(("_auswertung.json", "_formel.json", "_gebaeude.json"))
                                  and os.path.exists(p.replace(".json", "_wegkarte.txt")))
    Z = zuordnungen()
    tafel, gesamt = [], Counter()
    ziel_gesamt, takt_gesamt = Counter(), defaultdict(lambda: [0, 0])
    for p in pfade:
        e = pruefen(p, Z)
        tafel.append(e)
        for name, n in e["verstoesse_je_zuordnung"].items():
            gesamt[name] += n
        gesamt["schritte"] += e["schritte"]
        gesamt["spruenge"] += e["spruenge"]
        gesamt["ausserhalb"] += e["ausserhalb"]
        gesamt["start_gesperrt"] += e["start_gesperrt"]
        gesamt["beide_frei_schritte"] += e["beide_frei"]["schritte"]
        gesamt["beide_frei_verstoesse"] += e["beide_frei"]["verstoesse"]
        gesamt["gegenbit_geprueft"] += e["gegenbit_geprueft"]
        gesamt["gegenbit_fehlt"] += e["gegenbit_fehlt"]
        ziel_gesamt.update(e["ziel_gebaeude"])
        for band, (a, b) in e["nach_takt"].items():
            takt_gesamt[band][0] += a
            takt_gesamt[band][1] += b
        print("%-45s Wegkarte Takt %6d  Arbeiter %2d  Schritte %6d (Spruenge %3d, ausserhalb %5d)  Verstoesse echt %4d  "
              "naechstbeste falsche Zuordnung %5d  Ziele der Verstoesse %s" % (
                  e["datei"], e["wegkarte_tick"], e["arbeiter"], e["schritte"], e["spruenge"], e["ausserhalb"],
                  e["verstoesse_je_zuordnung"]["echt"],
                  min(n for name, n in e["verstoesse_je_zuordnung"].items() if name != "echt"),
                  e["ziel_gebaeude"] or "-"))
    print()
    print("GESAMT %d Messungen, %d Ein-Feld-Schritte (%d Spruenge > 1 Feld und %d Schritte ausserhalb der Wegkarte nicht gezaehlt)" % (
        len(tafel), gesamt["schritte"], gesamt["spruenge"], gesamt["ausserhalb"]))
    print("Verstoesse je Bit-Zuordnung (Negativlauf: nur 'echt' darf klein sein):")
    for name in Z:
        n = gesamt[name]
        print("   %-28s %6d  (%.2f %%)" % (name, n, 100.0 * n / max(gesamt["schritte"], 1)))
    print("Verstoesse der echten Zuordnung nach Zielfeld:", dict(ziel_gesamt))
    print("   davon Startfeld ganz gesperrt (link 00): %d" % gesamt["start_gesperrt"])
    print("   Schritte, bei denen Start und Ziel in der Wegkarte frei waren: %d, davon Verstoesse %d" % (
        gesamt["beide_frei_schritte"], gesamt["beide_frei_verstoesse"]))
    print("   nach Takt-Abstand zur Wegkarte (Schritte, Verstoesse):", {b: tuple(v) for b, v in sorted(takt_gesamt.items())})
    print("Gegenbit im Zielfeld fehlt bei %d von %d erlaubten Schritten" % (gesamt["gegenbit_fehlt"], gesamt["gegenbit_geprueft"]))
    ziel = os.path.join(D, time.strftime("laufweg_beweis_%Y%m%d_%H%M%S.json"))
    json.dump({"erstellt": time.strftime("%Y-%m-%d %H:%M:%S"), "zuordnungen": {n: {"%d,%d" % s: b for s, b in z.items()} for n, z in Z.items()},
               "gesamt": dict(gesamt), "ziel_gebaeude": dict(ziel_gesamt), "nach_takt": {b: v for b, v in takt_gesamt.items()},
               "messungen": tafel}, open(ziel, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("Beleg:", ziel)


if __name__ == "__main__":
    main()
