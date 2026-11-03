# -*- coding: utf-8 -*-
"""Welche Nummer hat ein Spielbefehl? Die Sprungtabelle der Befehle steht in der exe, die Namen im Ghidra-Export.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_plan/befehl_nummern.py > data/research/auge_plan/lauf_s_plan/befehl_nummern.txt

Anker: Befehl 16 ist die Auswahl (MakeUnitSelection, daten/dekomp_befehl_16.c), Befehl 36 giveTribeAnInstruction, beide im Modul benutzt und gemessen.
"""
import glob
import json
import os
import struct

from selfaware.tools.experiments import auge_lauf_f as lf

E = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions"
exe = os.path.join(lf.ordner(2), "Stronghold Crusader.exe")
roh = open(exe, "rb").read()
pe = struct.unpack_from("<I", roh, 0x3C)[0]
n, opt = struct.unpack_from("<H", roh, pe + 6)[0], struct.unpack_from("<H", roh, pe + 20)[0]
basis = struct.unpack_from("<I", roh, pe + 52)[0]
abschnitte = []
for i in range(n):
    o = pe + 24 + opt + i * 40
    vgr, va, rgr, ra = struct.unpack_from("<IIII", roh, o + 8)
    abschnitte.append((basis + va, ra, rgr))


def adresse(datei_ort):
    for v, r, g in abschnitte:
        if r <= datei_ort < r + g:
            return v + datei_ort - r
    return None


namen = {}
for f in glob.glob(os.path.join(E, "*.json")):
    a = int(os.path.basename(f)[:-5], 16)
    if 0x00480000 <= a <= 0x00490000 or "Commands::" in open(f, encoding="utf-8").read(400):
        j = json.load(open(f, encoding="utf-8"))
        if "Commands::" in j.get("name", ""):
            namen[a] = j["name"].split("Commands::")[-1]
print(len(namen), "Befehlsfunktionen mit Namen")
ziel = struct.pack("<I", 0x004847B0)
ort = roh.find(ziel)
treffer = []
while ort >= 0:
    treffer.append(ort)
    ort = roh.find(ziel, ort + 1)
for ort in treffer:
    # Tabelle: zusammenhaengende Zeiger auf Befehlsfunktionen rund um den Treffer
    a = ort
    while struct.unpack_from("<I", roh, a - 4)[0] in namen or 0x00400000 <= struct.unpack_from("<I", roh, a - 4)[0] < 0x00600000:
        a -= 4
    e = ort
    while 0x00400000 <= struct.unpack_from("<I", roh, e)[0] < 0x00600000:
        e += 4
    print("Treffer bei", hex(adresse(ort)), "Tabelle von", hex(adresse(a)), "bis", hex(adresse(e)), "Eintraege", (e - a) // 4, "ClickUnitStance an Stelle", (ort - a) // 4)
    for i in range(a, e, 4):
        w = struct.unpack_from("<I", roh, i)[0]
        print(" ", (i - a) // 4, hex(w), namen.get(w, ""))
