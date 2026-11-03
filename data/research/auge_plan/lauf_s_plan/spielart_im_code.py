# -*- coding: utf-8 -*-
"""B-142 Plan Lauf S: Wo fragt der Kampfcode die Spielart ab? Nur lesen, aus dem Code-Export (Datei, nicht Speicher; was UCP im Speicher aendert, steht in lauf_k_20261102/code_aenderungen.csv).

Aufruf aus dem Arbeitsbaum:
  python data/research/auge_plan/lauf_s_plan/spielart_im_code.py > data/research/auge_plan/lauf_s_plan/spielart_im_code.txt
"""
import csv
import glob
import json
import os
import re

E = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions"
HIER = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HIER, "..", "Checkliste_Auge.md")
AEND = os.path.join(HIER, "..", "lauf_k_20261102", "code_aenderungen.csv")
SPIELART = re.compile(r"currentGameMode|gameMode_2")


def code(a):
    return (json.load(open(os.path.join(E, "%08x.json" % a), encoding="utf-8")).get("pseudocode") or "").splitlines()


print("=== Funktionen mit Sonderfall Editor (GM_EDITOR)")
n = 0
for f in sorted(glob.glob(E + "/*.json")):
    d = json.load(open(f, encoding="utf-8"))
    t = d.get("pseudocode") or ""
    if isinstance(t, str) and "GM_EDITOR" in t:
        n += 1
        print(" ", d["address"], (d.get("name") or "").split("::")[-1], t.count("GM_EDITOR"))
print("Zusammen", n)

print("\n=== Punkte Lauf S: Spielart-Stellen im Code")
pkt = {}
for s in open(CHECK, encoding="utf-8").read().splitlines()[386:463]:
    m = re.match(r"- \[ \] (P\d+) `([^`]+)` \(0x([0-9a-f]+)\)", s)
    if m:
        pkt[m.group(1)] = (m.group(2), int(m.group(3), 16), "[Spielart]" in s)
print("Punkte", len(pkt))
for p, (name, a, marke) in sorted(pkt.items()):
    z = [s.strip() for s in code(a) if SPIELART.search(s)]
    if z:
        print(" %s %-42s Marke %-4s Stellen %d: %s" % (p, name, "ja" if marke else "nein", len(z), z[0][:90]))

print("\n=== Stellen mit Umgebung, die Regeln statt Ton oder Anzeige betreffen koennten")
ZEIGEN = [("processMeleeInitiation", 0x00549c70, 43, 58), ("UpdateMaceman", 0x00560700, 405, 416), ("processDamageFromKillingPit", 0x00419800, 18, 29), ("shouldUnitsEngageInMelee", 0x00531000, 45, 49),
          ("spawnUnit", 0x0053e440, None, "stoneAmmunition"), ("giveTribeAnInstruction", 0x00527c80, 481, 485), ("UpdateOutpostBuilding", 0x00411540, None, "GM_EDITOR"), ("MenuView_CustomScenarios_Prepare", 0x00425ea0, 25, 31)]
for name, a, von, bis in ZEIGEN:
    z = code(a)
    print("---", name, hex(a))
    if von is None:
        for i, s in enumerate(z):
            if bis in s:
                print("\n".join("  %4d %s" % (j, z[j].rstrip()[:115]) for j in range(max(0, i - 2), i + 2)))
    else:
        print("\n".join("  %4d %s" % (j, z[j].rstrip()[:115]) for j in range(von, bis)))

print("\n=== Reine Ton-Stellen im Schadenscode (kein Einfluss auf den Schaden)")
for name, a in (("processUnitAttackOtherUnit", 0x00531220), ("processEntityDamageToUnit", 0x00531920), ("processDamageToBuilding", 0x00516b80)):
    z = code(a)
    for i, s in enumerate(z):
        if SPIELART.search(s):
            naechste = next((x.strip() for x in z[i + 1:i + 12] if re.search(r"Audio::|playWAV|SFX|setSomeSoundTime", x)), "KEIN TON IN DER NAEHE")
            print(" %-28s Zeile %3d -> %s" % (name, i, naechste[:80]))

print("\n=== Was UCP im Speicher am Kampfweg aendert (Lauf K, code_aenderungen.csv)")
W = re.compile(r"Update(Lord|Maceman|Swordsman|Spearman|Pikeman|Knight|Crusader|Crossbow|Monk|Catapult|Trebuchet|Mangonel|Ballista|FireBallista|Assassin|Slave|Slinger|Arabian|HorseArcher|FireThrower|SiegeTower|BatteringRam|Tunneler)|processEntityDamageToUnit|acquireShootTarget|spawnUnit|ComputeDamageFearFactorBonus|getRemainingRequiredEngineers")
g = {}
for r in csv.DictReader(open(AEND, encoding="utf-8")):
    if W.search(r["funktion"]):
        g.setdefault(r["funktion"].split("::")[-1], []).append("%s %s" % (r["adresse"], r["art"]))
for k in sorted(g):
    print(" %-30s %d Stellen, erste %s" % (k, len(g[k]), g[k][0]))
