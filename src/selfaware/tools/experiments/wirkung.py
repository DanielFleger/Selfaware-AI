# -*- coding: utf-8 -*-
"""Wirkungstest: was bewirkt ein steuerbares Feld? (Fussabdruck gegen Kontrolle)

1) Zwei Kontroll-Laeufe ohne Eingriff: Selbstspiel, Pause bei Tick 1000, genau
   bis 1100, Schnappschuss. Gleich = das Spiel ist deterministisch.
2) Je Feld ein Lauf: bei Tick 1000 Wert + 5000 schreiben, genau bis 1100,
   Schnappschuss, Vergleich mit Kontrolle 1 - wo ueberall wirkt der Eingriff?

Aufruf:  uv run python -m selfaware.tools.experiments.wirkung <ausgabe.json> [spieler=2]
"""
import io, json, os, re, struct, sys, time

from selfaware.game.ucp.befehl import sende
from selfaware.game.ucp.steuerkarte import tick, laufe, lies, ORDNER, SPIELER_BASIS, SATZ

FELDER = [0x444, 0x448, 0x44C, 0x4D8, 0x20AC, 0x2A54, 0x2AFC, 0x389C,   # gehalten
          0x50C, 0x20EC, 0x2B38, 0x2B3C, 0x39D4]                         # weitergerechnet
SAETZE = {"spieler": (0, 0x39F4), "einheiten": (0, 1168), "gebaeude": (0x14, 812), "aiv": (4, 0x6D98)}

def lauf(name, sp, feld=None):
    sende({"player": 1, "menue": 41}, 3)
    sende({"player": 1, "pause": False}, 0.5)
    sende({"eigenesGefecht": True, "selbstspiel": True, "karte": "Liga_Grumpy Neighbors", "ki": 1,
           "gegner": 2, "startpause": 1000}, 4)
    sende({"player": 1, "tempo": 1000}, 0.5)
    for _ in range(40):
        if tick() == 1000:
            break
        time.sleep(0.5)
    if tick() != 1000:
        return None, "Tick 1000 nicht erreicht"
    info = None
    if feld is not None:
        adr = SPIELER_BASIS + sp * SATZ + feld
        orig = lies(adr)
        sende({"player": 1, "poke": adr, "wert": orig + 5000}, 0.5)
        info = {"original": orig, "geschrieben": orig + 5000}
    if laufe(100) != 1100:
        return None, "Tick 1100 nicht erreicht (Absturz?)"
    sende({"player": 1, "abzug": name}, 1.0)
    info = info or {}
    info["nachher"] = lies(SPIELER_BASIS + sp * SATZ + feld) if feld is not None else None
    return info, None

def lade(name):
    d = {}
    for p in os.listdir(ORDNER):
        m = re.match(re.escape(name) + r"_t\d+_(.+)\.bin$", p)
        if m:
            b = open(os.path.join(ORDNER, p), "rb").read()
            d[m.group(1)] = struct.unpack("<%di" % (len(b) // 4), b[: len(b) // 4 * 4])
    return d

def unterschiede(a, b, ohne=None):
    """Je Bereich: Anzahl verschiedener Woerter und die ersten Stellen (bei Tabellen als Satz/Feld)."""
    erg = {}
    for ber in sorted(a):
        if ber not in b:
            continue
        n = min(len(a[ber]), len(b[ber]))
        idx = [i for i in range(n) if a[ber][i] != b[ber][i] and (ber, i * 4) != ohne]
        if not idx:
            continue
        stellen = []
        for i in idx[:8]:
            if ber in SAETZE:
                kopf, satz = SAETZE[ber]
                o = i * 4 - kopf
                stellen.append("%s%d+0x%X: %d->%d" % (ber[:3], o // satz, o % satz, a[ber][i], b[ber][i]))
            else:
                stellen.append("+0x%X: %d->%d" % (i * 4, a[ber][i], b[ber][i]))
        erg[ber] = {"anzahl": len(idx), "beispiele": stellen}
    return erg

def main():
    ziel, sp = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 2
    s = time.strftime("%H%M%S")
    bericht = {"spieler": sp, "kontrolle": None, "felder": []}
    for k in ("k1", "k2"):
        _, fehler = lauf("w%s_%s" % (s, k), sp)
        if fehler:
            print("Kontrolle", k, "FEHLER:", fehler, flush=True); return
    det = unterschiede(lade("w%s_k1" % s), lade("w%s_k2" % s))
    bericht["kontrolle"] = det
    # Gleich heisst NUR: in diesem Fenster (Tick 1000-1100) bei diesem Aufbau gleich -
    # kein Beweis fuer Determinismus (Daniel, 30.09.). Verschieden widerlegt ihn dagegen.
    print("KONTROLLEN im Fenster Tick 1000-1100:", "gleich (nur dieses Fenster, kein Beweis fuer Determinismus)"
          if not det else "VERSCHIEDEN - damit ist das Spiel sicher nicht deterministisch: %s" % det, flush=True)
    k1 = lade("w%s_k1" % s)
    for feld in FELDER:
        name = "w%s_f%X" % (s, feld)
        info, fehler = lauf(name, sp, feld)
        if fehler:
            print("Feld +0x%X: %s" % (feld, fehler), flush=True)
            bericht["felder"].append({"feld": "+0x%X" % feld, "fehler": fehler}); continue
        wirk = unterschiede(k1, lade(name), ohne=("spieler", sp * SATZ + feld))
        gesamt = sum(v["anzahl"] for v in wirk.values())
        print("Feld +0x%X (%s -> %s, nach 100 Ticks %s): Wirkung an %d Stellen %s" % (
            feld, info["original"], info["geschrieben"], info["nachher"], gesamt,
            {k: v["anzahl"] for k, v in wirk.items()}), flush=True)
        for k, v in wirk.items():
            print("     %-10s %s" % (k, "; ".join(v["beispiele"][:4])), flush=True)
        bericht["felder"].append({"feld": "+0x%X" % feld, **info, "wirkung": wirk})
        io.open(ziel, "w", encoding="utf-8").write(json.dumps(bericht, ensure_ascii=False, indent=1))
    print("FERTIG", flush=True)

if __name__ == "__main__":
    main()
