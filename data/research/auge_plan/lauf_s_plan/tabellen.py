# -*- coding: utf-8 -*-
"""B-142 Plan Lauf S: Einheiten-, Schadens- und Gebaeudetabellen, wie sie im Speicher von Instanz 2 standen (Datenblock Lauf K, UCP und Rebalancer aktiv). Nur lesen.
Der Lauf liest sie beim Start neu. Hier dienen sie nur dazu, Grenzen und Vorhersagen zu rechnen.

Aufruf aus dem Arbeitsbaum:
  PYTHONPATH=src python data/research/auge_plan/lauf_s_plan/tabellen.py > data/research/auge_plan/lauf_s_plan/tabellen.txt
"""
import csv
import os
import struct

from selfaware.game.ucp import bauen
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
AUFNAHME = os.path.join(HIER, "..", "laeufe", "lauf_k_20261102_234952_t1.auge")
karte = Feldkarte.laden(feldliste=FELDLISTE)
auf = Aufzeichnung(AUFNAHME)
i = auf.namen.index("datenblock")
BASIS = auf.bereiche[i][1]
block = None
for r, p, _ in auf.staende():
    if r.bereich == i:
        block, takt = bytes(p), r.takt
        break
print("Quelle: Datenblock Lauf K bei Takt", takt)


def lies(adr, n):
    return [struct.unpack_from("<i", block, adr - BASIS + k * 4)[0] for k in range(n)]


def einheit(feld, n=80):
    return lies(karte.adresse("DAT_UnitPropertiesDefinedData", feld)[0], n)


NAME = {5: "Tunnel", 22: "Bogen", 23: "Armbrust", 24: "Speer", 25: "Pike", 26: "Keule", 27: "Schwert", 28: "Ritter", 29: "Leiter", 30: "Ingenieur", 37: "Moench", 39: "Katapult", 40: "Trebuchet", 41: "Mangonel", 55: "Lord", 58: "Turm", 59: "Ramme", 60: "Schild", 61: "Ballista", 70: "aBogen", 71: "Sklave", 72: "Schleuder", 73: "Assassine", 74: "Pferdebogen", 75: "aSchwert", 76: "Feuerwerfer", 77: "Feuerballiste"}
HP, TEMPO, KLETTERN, MASKE = (einheit(f) for f in ("DAT_BASE_HP", "DAT_UNIT_MOVEMENT_SPEED_ARRAY", "DAT_UNIT_CLIMB", "DAT_UNIT_ENEMY_NOTICE_RANGE"))
PFEIL, BOLZEN, STEIN = (einheit(f) for f in ("DAT_ARROW_DAMAGE", "DAT_BOLT_DAMAGE", "DAT_STONE_DAMAGE"))
NAH = lies(karte.adresse("DAT_UnitPropertiesDefinedData", "DAT_MELEE_DAMAGE")[0], 6400)
print("\n%-13s %3s %7s %5s %5s %6s %6s %6s %6s" % ("Art", "Nr", "Leben", "Tempo", "Klett", "Maske", "Pfeil", "Bolzen", "Stein"))
for t, n in sorted(NAME.items()):
    print("%-13s %3d %7d %5d %5d %6d %6d %6d %6d" % (n, t, HP[t], TEMPO[t], KLETTERN[t], MASKE[t], PFEIL[t], BOLZEN[t], STEIN[t]))
reich = lies(karte.adresse("DAT_EntityDefinedData", "DAT_EntityTypeArrayForProjectileRange")[0], 38)
print("\nReichweite je Geschossart, Tabelle:", {k: v for k, v in enumerate(reich) if v})
K = [22, 23, 24, 25, 26, 27, 28, 29, 30, 5, 37, 70, 71, 72, 73, 74, 75, 76, 55]
print("\nNahkampf je Schlag: Zeile schlaegt, Spalte wird getroffen")
print(" " * 12 + "".join("%6s" % NAME[o][:5] for o in K))
for a in K:
    print("%-12s" % NAME[a] + "".join("%6d" % NAH[a * 80 + o] for o in K))
paare = [(HP[o] // NAH[a * 80 + o] + 1, NAME[a], NAME[o]) for a in K for o in K if NAH[a * 80 + o] > 0]
print("\nSchlaege bis zum Tod: Median", sorted(p[0] for p in paare)[len(paare) // 2], "meiste", sorted(paare, reverse=True)[:3], "ohne Schaden", 19 * 19 - len(paare))

LEBEN = lies(karte.adresse("DAT_BuildingDefinedData", "DAT_BUILDING_HP")[0], 110)
HAT = lies(karte.adresse("DAT_BuildingDefinedData", "DAT_BuildingTypeHasHealth")[0], 110)
nach = {g["laufzeitName"]: (t, g) for t, g in bauen.NACH_TYP.items()}
ziele = []
for r in csv.DictReader(open(os.path.join(HIER, "..", "versuche_szenario.csv"), encoding="utf-8"), delimiter=";"):
    if r["gruppe"] == "V4" and r["ziel"] not in ziele:
        ziele.append(r["ziel"])
print("\nZiele V4:", len(ziele), "davon mit Bauzeile in bauen.py:", sum(z in nach for z in ziele))
print("Ohne Bauzeile, Setzen in der Probe klaeren:", [z for z in ziele if z not in nach])
print("Tabelle sagt: hat kein Leben:", [z for z in ziele if z in nach and not HAT[nach[z][0]]])
print("\n%-20s %3s %6s %6s %3s  Steine bis zerstoert: Katapult 20, Trebuchet 60 je Stein (processEntityHitBuildingOrUnit)" % ("Art", "Nr", "Leben", "Mapper", "b"))
zeilen = sorted(((z,) + nach[z] for z in ziele if z in nach and HAT[nach[z][0]]), key=lambda v: -LEBEN[v[1]])
for z, t, g in zeilen:
    print("%-20s %3d %6d %6d %3d %5d %5d" % (z, t, LEBEN[t], g["mapper"], g["b"], LEBEN[t] // 20 + 1, LEBEN[t] // 60 + 1))
