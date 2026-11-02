# -*- coding: utf-8 -*-
"""Anzeigefehler: Gebaeudewerte lesen und die Karte in allen vier Drehungen fotografieren. Baut und aendert nichts."""
import collections, json, os, shutil, struct, sys, time
sys.path.insert(0, "src")
from PIL import Image
from selfaware.game.ucp import laden, bauen
from selfaware.game.ucp.befehl import SPIEL
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz
from selfaware.tools.analysis.auge_feldkarte import Feldkarte

GEB, SCHRITT = 0xF98520, 0x32C
AUSRICHTUNG, T, P = 0x01FE7AA4, 0x0117CADC, 0x01FEA054
q = ProzessQuelle(pid_der_instanz(2))
i32 = lambda a: struct.unpack("<i", q.lies(a, 4))[0]
k = Feldkarte.laden()
OFF = {}
for o in range(0, SCHRITT):
    for g, f in k.felder_einer_aenderung(GEB + SCHRITT + o, 1):
        OFF.setdefault(f, o)
FELD = {n: OFF["buildings[]." + n] for n in ("buildingStateUnk", "buildingType", "owner", "x", "y", "buildingVariation", "orientation", "widthOrHeight") if "buildings[]." + n in OFF}
ZU, TY, BE = 0xE4, 0xE6, 0xEA


def gebaeude():
    d = q.lies(GEB, SCHRITT * 2000)
    aus = []
    for i in range(1, 2000):
        b = i * SCHRITT
        z, t, s = (struct.unpack_from("<h", d, b + o)[0] for o in (ZU, TY, BE))
        if z:
            e = {"nr": i, "zustand": z, "typ": t, "sp": s, "x": struct.unpack_from("<h", d, b + 0x102)[0], "y": struct.unpack_from("<h", d, b + 0x104)[0]}
            e["v"] = struct.unpack_from("<h", d, b + FELD["buildingVariation"])[0]
            if "orientation" in FELD:
                e["o"] = struct.unpack_from("<h", d, b + FELD["orientation"])[0]
            aus.append(e)
    return aus


def bild(ziel_ordner, name, mitte=(212, 188), rahmen=(1500, 1000)):
    rel = "ucp/villagestudio/abzug/anzeige_%s.bmp" % name
    quelle = os.path.join(SPIEL, rel.replace("/", os.sep))
    if os.path.exists(quelle):
        os.remove(quelle)
    laden.befehl({"kamera": list(mitte)}, 0.4)
    time.sleep(0.6)
    laden.befehl({"bild": "karte", "datei": rel}, 1.0)
    ende = time.time() + 20
    while time.time() < ende:
        if os.path.exists(quelle) and os.path.getsize(quelle) > 1000:
            time.sleep(0.5)
            break
        time.sleep(0.2)
    else:
        raise RuntimeError("Bild kam nicht: " + name)
    im = Image.open(quelle).convert("RGB")
    os.makedirs(ziel_ordner, exist_ok=True)
    ziel = os.path.join(ziel_ordner, name + ".png")
    im.save(ziel)
    return ziel, im.size


def alle_drehungen(ordner, kennung):
    """Faehrt von der aktuellen Drehung aus einmal im Kreis und kommt dort wieder an."""
    a0 = i32(AUSRICHTUNG)
    erg = []
    for n in range(4):
        a = i32(AUSRICHTUNG)
        z, g = bild(ordner, "%s_r%d" % (kennung, a))
        erg.append((a, z, g))
        print("  Drehung", a, "->", z, g, flush=True)
        laden.befehl({"drehen": "links"}, 0.3)
        soll, ende = (a + 2) % 8, time.time() + 15
        while i32(AUSRICHTUNG) != soll and time.time() < ende:
            time.sleep(0.1)
        if i32(AUSRICHTUNG) != soll:
            raise RuntimeError("Drehung kam nicht an")
        time.sleep(1.0)
    if i32(AUSRICHTUNG) != a0:
        raise RuntimeError("nicht zurueck bei der Startdrehung")
    return erg


if __name__ == "__main__":
    ordner, kennung = sys.argv[1], sys.argv[2]
    if len(sys.argv) > 3 and sys.argv[3] != "-":
        print("Lade", sys.argv[3], "->", laden.lade_stand(sys.argv[3], mit_bild=False), flush=True)
    print("Felder", FELD)
    t0 = i32(T)
    print("Takt", t0, "Pause", i32(P), "Drehung", i32(AUSRICHTUNG))
    g = gebaeude()
    print("Gebaeude", len(g), "je v:", collections.Counter(e["v"] for e in g).most_common())
    je = collections.defaultdict(collections.Counter)
    for e in g:
        je[e["typ"]][e["v"]] += 1
    print("Typ -> Werte:", {t: dict(c) for t, c in sorted(je.items())})
    json.dump(g, open(os.path.join(ordner, kennung + "_gebaeude.json"), "w", encoding="utf-8") if os.path.isdir(ordner) else open(kennung + "_gebaeude.json", "w"), ensure_ascii=False)
    alle_drehungen(ordner, kennung)
    print("Takt danach", i32(T), "Pause", i32(P), "steht" if i32(T) == t0 else "HAT SICH BEWEGT")
