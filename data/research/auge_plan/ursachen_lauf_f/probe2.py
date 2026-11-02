# -*- coding: utf-8 -*-
"""Lauf F, Ursachen, zweite Probe: Lager fuer Stein; dann jede fehlende Gebaeudeart an einer vom Spiel erlaubten Stelle. Prueft die Wirkung im Speicher."""
import collections, json, struct, sys, time
sys.path.insert(0, "src")
from selfaware.game.ucp import laden, bauen
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz
from selfaware.tools.analysis.auge_feldkarte import Feldkarte

AUS, TMP = sys.argv[1], sys.argv[2]
q = ProzessQuelle(pid_der_instanz(2))
k = Feldkarte.laden()
i32 = lambda a: struct.unpack("<i", q.lies(a, 4))[0]
T, P, BASIS = 0x0117CADC, 0x01FEA054, 0x0115BDF8 + 0x39F4
GEB, SCHRITT, ZUSTAND, TYP, BESITZER, X, Y = 0xF98520, 0x32C, 0xE4, 0xE6, 0xEA, 0x102, 0x104
WARE = {}
for o in range(0, SCHRITT, 2):
    for g, f in k.felder_einer_aenderung(GEB + SCHRITT + o, 2):
        if f.startswith("buildings[].resource") and f not in WARE:
            WARE[f] = o
aus = {"ware_offsets": WARE, "schritte": []}


def speichere():
    json.dump(aus, open(AUS, "w", encoding="utf-8"), ensure_ascii=False, indent=0)


def gebaeude():
    d = q.lies(GEB, SCHRITT * 2000)
    liste = []
    for i in range(1, 2000):
        b = i * SCHRITT
        z, t, s = (struct.unpack_from("<h", d, b + o)[0] for o in (ZUSTAND, TYP, BESITZER))
        if z and s == 1:
            liste.append((i, t, struct.unpack_from("<h", d, b + X)[0], struct.unpack_from("<h", d, b + Y)[0]))
    return liste


def laufe(n):
    t0 = i32(T)
    laden.befehl({"tickpause": {"bei": t0 + n}}, 0.2)
    laden.befehl({"pause": False}, 0.1)
    ende = time.time() + 30  # Schutz gegen Haengen, keine Messgroesse
    while time.time() < ende:
        if i32(T) >= t0 + n and i32(P) == 1:
            return
        time.sleep(0.02)
    laden.befehl({"pause": True}, 0.2)
    raise RuntimeError("Takte kamen nicht an")


def lager_inhalt():
    aus_l = {}
    for nr, t, x, y in gebaeude():
        if t == 10:
            b = GEB + nr * SCHRITT
            werte = {f.split(".")[-1][8:]: struct.unpack("<i", q.lies(b + o, 4))[0] for f, o in WARE.items()}
            aus_l[nr] = {a: v for a, v in werte.items() if v}
    return aus_l


if i32(P) != 1:
    raise SystemExit("Spiel laeuft, Probe abgebrochen")
print("Lager vorher:", lager_inhalt(), flush=True)
g = bauen.NACH_TYP
laden.befehl({"baue": {"mapper": g[10]["mapper"], "x": 219, "y": 195, "groesse": g[10]["b"], "richtung": 0}}, 0.2)
laufe(600)
w = struct.unpack("<25i", q.lies(BASIS + 0x4D0, 100))
s = struct.unpack("<25i", q.lies(BASIS + 0x46C, 100))
stein = {"stein_bestand": w[4], "stein_start": s[4], "lager": lager_inhalt()}
print("Nach 5. Lager:", stein, flush=True)
aus["stein"] = stein
speichere()

fehlt = [t for t in sorted(g) if not any(e[1] == t for e in gebaeude())]
print("Fehlende Arten:", len(fehlt), fehlt, flush=True)
for typ in fehlt:
    gut, alle, _ = bauen.platzkarte(typ, 0, 0, 399, 399, TMP)
    e = {"typ": typ, "name": g[typ].get("name"), "erlaubt": gut}
    if not gut:
        e["ergebnis"] = "keine erlaubte Stelle"
    else:
        karte = open(TMP, encoding="utf-8").read().splitlines()[1:]
        best = None
        for y, z in enumerate(karte):
            for x, c in enumerate(z):
                if c == "+":
                    d = max(abs(x - 212), abs(y - 188))
                    if best is None or d < best[0]:
                        best = (d, x, y)
        vorher = {n for n, t, _, _ in gebaeude() if t == typ}
        t0 = i32(T)
        laden.befehl({"baue": {"mapper": g[typ]["mapper"], "x": best[1], "y": best[2], "groesse": g[typ]["b"], "richtung": 0}}, 0.2)
        laufe(20)
        neu = [a for a in gebaeude() if a[1] == typ and a[0] not in vorher]
        e.update(stelle=best[1:], ergebnis="steht" if neu else "NICHT GEBAUT", eintrag=neu[:1])
    aus["schritte"].append(e)
    speichere()
    print(typ, e.get("name"), e["erlaubt"], e.get("stelle"), e["ergebnis"], flush=True)
ergebnisse = collections.Counter(e["ergebnis"] for e in aus["schritte"])
print(ergebnisse.most_common())
print("Am Ende je Typ:", collections.Counter(e[1] for e in gebaeude()).most_common(8), "Pause", i32(P), "Takt", i32(T))
