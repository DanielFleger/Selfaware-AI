# B-159 (21.10.2026 23:40): schreibt waehrend eines Ladevorgangs JEDE Aenderung von Platz, Mensch-Eintraegen, KI-Eintraegen,
# gameOver, Ansicht, Pause und Spielzeit mit (Speicher lesen, ~1 ms Takt). Endet nach SEKUNDEN oder wenn gameOver 1 wird + 3 s.
# Aufruf: SHC_INSTANZ=5 python daten/laden_spur.py [SEKUNDEN]
import json, os, sys, time
os.environ.setdefault("SHC_INSTANZ", "5")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "werkzeug"))
import shc, speicher
DAUER = float(sys.argv[1]) if len(sys.argv) > 1 else 150
AUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "laden_spur_%s.jsonl" % time.strftime("%Y%m%d_%H%M%S"))
FELDER = {"tick": (shc.TICK, 4, 1), "ansicht": (0x01FE7D1C, 4, 1), "gameOver": (0x0117D500, 4, 1), "platz": (0x01A275DC, 4, 1),
          "mensch": (0x0191DE10, 4, 9), "ki": (0x0191DE7C, 4, 9), "pause": (shc.PAUSE, 4, 1)}
def lies():
    z = {}
    for name, (adr, b, n) in FELDER.items():
        raw = speicher.lies(adr, b * n)
        w = [int.from_bytes(raw[i * b:(i + 1) * b], "little", signed=True) for i in range(n)]
        z[name] = w if n > 1 else w[0]
    return z
t0, alt, ende, n = time.perf_counter(), None, None, 0
with open(AUS, "w", encoding="utf-8") as fh:
    while time.perf_counter() - t0 < DAUER and (ende is None or time.perf_counter() < ende):
        try:
            z = lies()
        except Exception as e:
            z = {"fehler": str(e)[:80]}
        if z != alt:
            fh.write(json.dumps({"ms": round((time.perf_counter() - t0) * 1000, 1), **z}) + "\n")
            n += 1
            alt = z
            if z.get("gameOver") == 1 and ende is None:
                ende = time.perf_counter() + 3
print("SPUR: %d Aenderungen -> %s" % (n, AUS))
