# -*- coding: utf-8 -*-
"""Lauf F: je Bau-Befehl aus ucp3.log nachsehen, was danach wirklich im Gebaeudeblock der Aufzeichnung stand. Nur lesen."""
import collections, json, re, struct, sys, zlib
sys.path.insert(0, "src")
from selfaware.tools.analysis.auge_auswertung import RAHMEN, KENNUNG, VOLL
from selfaware.game.ucp import bauen

PFAD = "data/research/auge_plan/laeufe/lauf_f_20261102_184744.auge"
LOG = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz2\ucp3.log"
AUS = sys.argv[1]
SCHRITT, ZUSTAND, TYP, BESITZER, X, Y = 0x32C, 0xE4, 0xE6, 0xEA, 0x102, 0x104

f = open(PFAD, "rb")
f.read(len(KENNUNG))
n = struct.unpack("<I", f.read(4))[0]
kopf = json.loads(f.read(n).decode("utf-8"))
namen = [b[0] for b in kopf["bereiche"]]
g = namen.index("DAT_BuildingsState")
puffer = None
stand = {}
neu = []
weg = []


def eintrag(i):
    b = i * SCHRITT
    z, t, s, x, y = (struct.unpack_from("<h", puffer, b + o)[0] for o in (ZUSTAND, TYP, BESITZER, X, Y))
    return (z, t, s, x, y) if z else None


while True:
    k = f.read(RAHMEN.size)
    if len(k) < RAHMEN.size:
        break
    art, b, merker, vor, nach, zeit, dauer, rohl, zl = RAHMEN.unpack(k)
    if b != g:
        f.seek(zl + 4, 1)
        continue
    nutz = zlib.decompress(f.read(zl))
    f.read(4)
    betroffen = set()
    if art == VOLL:
        puffer = bytearray(nutz)
        betroffen = set(range(1, len(puffer) // SCHRITT))
    else:
        i = 0
        while i < len(nutz):
            o, l = struct.unpack_from("<II", nutz, i)
            i += 8
            puffer[o:o + l] = nutz[i:i + l]
            i += l
            betroffen.update(range(o // SCHRITT, (o + l) // SCHRITT + 1))
    for i in betroffen:
        if i * SCHRITT + SCHRITT > len(puffer) or i == 0:
            continue
        e = eintrag(i)
        a = stand.get(i)
        if e and (not a or a[1] != e[1] or a[3:] != e[3:]):
            neu.append({"takt": vor, "nr": i, "zustand": e[0], "typ": e[1], "sp": e[2], "x": e[3], "y": e[4]})
        if a and not e:
            weg.append({"takt": vor, "nr": i, "typ": a[1]})
        if e:
            stand[i] = e
        else:
            stand.pop(i, None)

befehle = []
for z in open(LOG, encoding="latin-1"):
    if z[11:19] < "18:47:44":
        continue
    m = re.search(r"BAUE Tick (\d+): Mapper (\d+) bei \((\d+),(\d+)\), Groesse (\d+), Drehung (\d+) - abgesetzt=(\w+)", z)
    if m:
        befehle.append(dict(zip(("takt", "mapper", "x", "y", "groesse", "drehung"), map(int, m.groups()[:6])), ab=m.group(7)))
zu_typ = {g_["mapper"]: g_["laufzeit"] for g_ in bauen.GEBAEUDE.values() if "laufzeit" in g_ and "mapper" in g_}
for b_ in befehle:
    b_["typ"] = zu_typ.get(b_["mapper"])
print("Bau-Befehle", len(befehle), "neue Eintraege", len(neu), "weg", len(weg))
print("Stand am Ende je Typ (Spieler 1):", collections.Counter(e[1] for e in stand.values() if e[2] == 1).most_common())
json.dump({"befehle": befehle, "neu": neu, "weg": weg}, open(AUS, "w", encoding="utf-8"))
