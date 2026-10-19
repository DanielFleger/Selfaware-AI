# -*- coding: utf-8 -*-
"""Steuerkarte: welche Spielerfelder lassen sich steuern, welche berechnet das Spiel?

1) Frisches Selbstspiel, Pause genau bei Tick <start>; Schnappschuss.
2) Tick-genau <schritt> Ticks weiter; zweiter Schnappschuss.
3) Kandidaten = Felder von Spieler <spieler>, die sich dabei bewegt haben.
   Werte mit Betrag >= 100000 werden NICHT angefasst (vermutlich Zeiger/gepackt).
4) Je Kandidat: Original + 1000 schreiben, genau <schritt> Ticks laufen
   (Tick-Pause), zuruecklesen, einordnen, Original zurueckschreiben.

Aufruf:  uv run python -m selfaware.game.ucp.steuerkarte <ausgabe.json> [start=1000] [schritt=100] [spieler=2]
"""
import io, json, os, re, struct, sys, time

from selfaware.game.ucp.befehl import sende, ABZUG

ORDNER = ABZUG
SPIELER_BASIS, SATZ = 0x0115BDF8, 0x39F4

def s32(v): return v - 0x100000000 if v > 0x7FFFFFFF else v

def lies(adr):
    for z in sende({"player": 1, "peek": adr, "worte": 1}, 0.6):
        m = re.search(r"PEEK 0x%08X: (\S+)" % adr, z)
        if m:
            return s32(int(m.group(1), 16) & 0xFFFFFFFF)
    return None

def tick():
    m = re.search(r"Tick (\d+)", " ".join(sende({"player": 1, "zeit": True}, 0.6)))
    return int(m.group(1)) if m else None

def laufe(ticks):
    """Genau <ticks> Ticks weiterlaufen lassen und wieder anhalten."""
    t = tick()
    sende({"player": 1, "tickpause": {"bei": t + ticks}}, 0.5)
    sende({"player": 1, "pause": False}, 0.6)
    for _ in range(20):
        jetzt = tick()
        if jetzt is not None and jetzt >= t + ticks:   # >= statt == (04.10.: bei Tempo 1000 wird der Tick uebersprungen)
            return jetzt
        time.sleep(0.3)
    jetzt = tick()
    if jetzt is None or jetzt <= t:
        # Fehlerkontrolle (Daniel 04.10.): steht die Zeit, ist der Lauf ungueltig - laut abbrechen.
        raise RuntimeError("SPIELZEIT STEHT bei %s (Ziel %d): %s" % (jetzt, t + ticks, spielzustand()))
    return jetzt

def spielzustand():
    """Ansicht 14 = Gefecht, 30 = Endbildschirm, 41 = Hauptmenue; gameOver 0x0117D500."""
    werte = {}
    for name, adr in (("Ansicht", 0x01FE7D1C), ("Pause", 0x01FEA054), ("gameOver", 0x0117D500),
                      ("Spielerplatz", 0x01A275DC)):
        try:
            werte[name] = lies(adr)
        except Exception:
            werte[name] = "?"
    return ", ".join("%s %s" % kv for kv in werte.items())

def abzug(name):
    sende({"player": 1, "abzug": name}, 1.0)
    for p in os.listdir(ORDNER):
        if p.startswith(name + "_t") and p.endswith("_spieler.bin"):
            return open(os.path.join(ORDNER, p), "rb").read()
    return None

def main():
    ziel = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    schritt = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    sp = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    stempel = time.strftime("%H%M%S")

    sende({"player": 1, "menue": 41}, 3)
    sende({"player": 1, "pause": False}, 0.5)
    sende({"eigenesGefecht": True, "selbstspiel": True, "karte": "Liga_Grumpy Neighbors", "ki": 1,
           "gegner": 2, "startpause": start}, 4)
    sende({"player": 1, "tempo": 1000}, 0.5)
    for _ in range(40):
        if tick() == start:
            break
        time.sleep(0.5)
    print("Spiel steht bei Tick", tick(), flush=True)
    a = abzug("sk%s_a" % stempel)
    laufe(schritt)
    b = abzug("sk%s_b" % stempel)
    wa, wb = struct.unpack("<%di" % (len(a) // 4), a), struct.unpack("<%di" % (len(b) // 4), b)
    lo, hi = sp * SATZ // 4, (sp + 1) * SATZ // 4
    kandidaten = [(i * 4 - sp * SATZ, wb[i]) for i in range(lo, hi) if wa[i] != wb[i]]
    grosse = [k for k in kandidaten if abs(k[1]) >= 100000]
    kandidaten = [k for k in kandidaten if abs(k[1]) < 100000]
    print("Kandidaten bei Spieler %d: %d bewegte Felder, davon %d zu gross (nicht angefasst), %d getestet"
          % (sp, len(kandidaten) + len(grosse), len(grosse), len(kandidaten)), flush=True)

    ergebnisse = []
    for nr, (off, _) in enumerate(kandidaten, 1):
        adr = SPIELER_BASIS + sp * SATZ + off
        orig = lies(adr)
        if orig is None:
            continue
        wert = orig + 1000
        sende({"player": 1, "poke": adr, "wert": wert}, 0.5)
        sofort = lies(adr)
        t1 = laufe(schritt)
        danach = lies(adr)
        sende({"player": 1, "poke": adr, "wert": orig}, 0.5)
        if sofort != wert:
            urteil = "nicht angekommen"
        elif danach == wert:
            urteil = "gehalten"
        elif danach == orig:
            urteil = "zurueckgesetzt"
        elif danach is not None and abs(danach - wert) < abs(danach - orig):
            urteil = "weitergerechnet"
        else:
            urteil = "neu berechnet"
        e = {"feld": "+0x%X" % off, "adresse": "0x%08X" % adr, "original": orig, "geschrieben": wert,
             "danach": danach, "tick": t1, "urteil": urteil}
        ergebnisse.append(e)
        print("%3d/%d  %-8s orig %8d -> %8d nach %d Ticks: %8s  %s" % (nr, len(kandidaten), e["feld"], orig, wert,
              schritt, danach, urteil), flush=True)
        io.open(ziel, "w", encoding="utf-8").write(json.dumps({
            "spieler": sp, "start": start, "schritt": schritt, "nicht_angefasst": ["+0x%X" % o for o, _ in grosse],
            "ergebnisse": ergebnisse}, ensure_ascii=False, indent=1))

    zaehl = {}
    for e in ergebnisse:
        zaehl[e["urteil"]] = zaehl.get(e["urteil"], 0) + 1
    print("FERTIG:", zaehl, flush=True)

if __name__ == "__main__":
    main()
