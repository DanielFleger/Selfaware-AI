# -*- coding: utf-8 -*-
"""Daniels Angaben vom 04.11. 20:56 gegen den Export: Wer liest die Warenbitte, gibt es Geschenke zwischen KI, wo ist Zufall im Geschoss, Holztor, Feuerkorb, Waldsterben."""
import json, os, re, collections
D = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions"
MUSTER = {
    "Warenbitte": r"requestedGoodsArray",
    "Geschenke": r"(?i)giveResource|sendGoods|giftGold|sendResource|giveGold|donate|allyGold|sendGold|transferGold|transferResource",
    "Holztor": r"M_MAPPER_GATE_WOOD\b|BT_WOODGATE",
    "Feuerkorb": r"M_MAPPER_BRAZIER|ET_BRAZIER|spreadBrazierPlacementAlgorithm",
    "Waldsterben": r"(?i)blight|treeDeath|forestDeath|treeDisease|woodDisease|deadTree",
}
treffer = collections.defaultdict(list)
zufall_namen = collections.Counter()
for f in os.listdir(D):
    if not f.endswith(".json"):
        continue
    j = json.load(open(os.path.join(D, f), encoding="utf-8"))
    p = j.get("pseudocode") or ""
    n = (j.get("name") or "").replace("_HoldStrong::", "")
    for k, m in MUSTER.items():
        if re.search(m, p):
            treffer[k].append((f[:-5], n))
    if re.search(r"(?i)projectile|missile|fire|flame|burn", n) and re.search(r"(?i)SEC_RNG|\brand|random|fixedRng|getNextRandom", p):
        zufall_namen[n] += 1
for k, v in treffer.items():
    print(k, len(v), [f"{a} {b}"[:70] for a, b in v][:14])
print("Geschoss und Feuer mit Zufall:", list(zufall_namen)[:30])
