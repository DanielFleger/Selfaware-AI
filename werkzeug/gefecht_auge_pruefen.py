# -*- coding: utf-8 -*-
"""B-273: Gefechtsrechnung aus den Spielwerten des Auges pruefen (Soll je Fall vorher festgelegt, ohne Spiel).
Grundlage: juengste live-Datei daten/spielwerte_*.json (melee_damage: Streitkolben->Lord 70, arab. Schwert->Lord 125,
Assassine->Lord 100). Aufruf: python gefecht_auge_pruefen.py"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import gefecht as G
import kaufrechnung as KR


def neu(sw):
    G.SPIELWERTE, G._TABELLE, G.VERWORFEN = sw, None, None
    G._HOECHST.clear()


def dps(a, z, d=1):
    s, _l, f = G.tabelle()
    return G.dps(a, z, s, f, d)


if __name__ == "__main__":
    sw = KR.spielwerte_laden()
    if sw is None:
        print("UEBERSPRUNGEN: keine live-Datei daten/spielwerte_*.json")
        sys.exit(0)
    md = sw["tabellen"]["einheit.melee_damage"]["werte"]
    hp = sw["tabellen"]["einheit.base_hp"]["werte"]
    neu(sw)
    null = next(((a, z) for a in range(len(md)) for z in range(len(md[a])) if hp[a] > 0 and z < len(hp) and hp[z] > 0
                 and md[a][z] == 0 and any(md[a])), None)
    faelle = [
        ("arab. Schwertkaempfer -> Lord = Spielwert %d (nicht 180)" % md[75][55], dps(75, 55) == md[75][55]),
        ("Streitkolben -> Lord = Spielwert %d" % md[26][55], dps(26, 55) == md[26][55]),
        ("Assassine -> Lord = Spielwert %d" % md[73][55], dps(73, 55) == md[73][55]),
        ("Paarung %s mit Spielwert 0 -> 0, nicht Zeilenmittel" % (null,), null is None or dps(*null) == 0),
        ("Lord -> Streitkolben aus der Tabelle (%d)" % md[55][26], dps(55, 26) == md[55][26]),
        ("Leben aus den Spielwerten (Streitkolben %d)" % hp[26], G.tabelle()[1][26] == hp[26]),
    ]
    # Balance-Gegenprobe: Lord mit 300.000 (eigenes Lord-Leben, nicht Balance) verwirft nicht; Streitkolben mit mehr Leben als
    # die Spielwerte nennen verwirft und schaltet auf die Duelle zurueck
    L = {1: {"typ": 55, "leben": 300000}, 2: {"typ": 26, "leben": hp[26]}}
    faelle.append(("Lord mit 300.000 Leben verwirft die Spielwerte nicht", G.balance_pruefen(L) is None and G.SPIELWERTE is sw))
    L[3] = {"typ": 26, "leben": hp[26] + 5000}
    m = G.balance_pruefen(L)
    faelle.append(("Streitkolben mit %d Leben (> %d) verwirft -> Duell-Messungen" % (hp[26] + 5000, hp[26]),
                   bool(m) and G.SPIELWERTE is None and dps(75, 55) != md[75][55]))
    for name, ok in faelle:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    print("%d von %d gruen (Spielwerte: %s)" % (sum(ok for _, ok in faelle), len(faelle), os.path.basename(sw["_pfad"])))
    sys.exit(0 if all(ok for _, ok in faelle) else 1)
