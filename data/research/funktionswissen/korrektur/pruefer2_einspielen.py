# -*- coding: utf-8 -*-
"""B-141 zweite Pruefstufe: nachgepruefte Funde einspielen. Der Pruefer sah nur den Export, nicht den Paketcode;
Namen aus dem Paketcode sind darum kein Fehler. Lauf aus dem Ordner funktionswissen."""
import glob, json
K = "korrektur"
# Adresse -> (Urteil der Sitzung, Grund, Nummern der verworfenen Ersetzungen; None = alle)
ENTSCHEID = {
    "0x004bde40": ("richtig", "Feldnamen stehen so im Paketcode", None),
    "0x0049b1d0": ("richtig", "Paketcode vergleicht wirklich uneinheitlich (0x13a0f und 80400)", None),
    "0x004a4140": ("richtig", "CONCAT31 steht im Paketcode", None),
    "0x0041eda0": ("kleiner_fehler", "Feldname field261 steht im Paketcode, Versatz-Fund bleibt", {2}),
    "0x00412d50": ("kleiner_fehler", "Namen und Armbrust-Kommentar stehen im Paketcode; nur 'hergestellt wird hier nichts' war ungenau", {0, 1, 2, 3, 4, 5, 6, 7, 8}),
}
EIGEN = {"0x00412d50": [{"alt": "; hergestellt wird hier nichts", "neu": "; am Ende von state 1 zählt er animationCycleCount + 1 und setzt animationCycleCompleted = 1 (Ghidra-Kommentar: 'Done working on product'), die Ware selbst wird in dieser Funktion nicht verbucht"}]}
LISTEN = {"0x00518c50": {
    "liest": ["attackInfo: biggestZone, startZone, scaleZone, nof_fpoints, inv_count, nof_tribes[inv_count], startCon, keepCon, casDis, zoneSize, attacker, Block von attacker (hack, scale, town, gate, moat, wide), lord1/2, high1-3, arch1-3, people1-3, archerPoints/archerPointsNext, supportPoints/supportPointsNext, tentPoints/tentPointsNext, aiTribeSizesPerTribeType, aiTroops, playerTotalTroopValueArray[0..8]", "playerDataArray[currentPlayerSlotID].keep.yEntry", "playerDataArray[1].troopsKilled/troopsLost"],
    "ruft": ["renderTextToScreen", "renderNumberToScreen2", "_sprintf", "__security_check_cookie"]}}
ort = {}
for t in glob.glob(K + "/ergebnisse/*.jsonl"):
    for i, z in enumerate(open(t, encoding="utf-8")):
        if z.strip():
            ort[json.loads(z)["adr"].lower()] = (t, i)
def zaehlen(o, s):
    if isinstance(o, str): return o.count(s)
    if isinstance(o, list): return sum(zaehlen(v, s) for v in o)
    if isinstance(o, dict): return sum(zaehlen(v, s) for v in o.values())
    return 0
def ersetze(o, a, b):
    if isinstance(o, str): return o.replace(a, b)
    if isinstance(o, list): return [ersetze(v, a, b) for v in o]
    if isinstance(o, dict): return {k: ersetze(v, a, b) for k, v in o.items()}
    return o
ok, verworfen, miss, aus, summe = 0, 0, [], [], {}
for z in open(K + "/pruefer2_befunde.jsonl", encoding="utf-8"):
    if not z.strip():
        continue
    b = json.loads(z)
    a = b["adr"].lower()
    urteil, grund, weg = ENTSCHEID.get(a, (b["urteil"], "bestaetigt", set()))
    b["urteil_sitzung"], b["grund_sitzung"] = urteil, grund
    aus.append(json.dumps(b, ensure_ascii=False))
    summe[(b["herkunft"], urteil)] = summe.get((b["herkunft"], urteil), 0) + 1
    t, i = ort[a]
    zeilen = open(t, encoding="utf-8").read().splitlines()
    x = json.loads(zeilen[i])
    ers = []
    for n, e in enumerate(b.get("ersetzen", [])):
        if weg is None or n in weg or e["alt"].startswith('"'):
            verworfen += 0 if e["alt"].startswith('"') else 1
        else:
            ers.append(e)
    ers += EIGEN.get(a, [])
    for e in ers:
        if zaehlen(x, e["alt"]) != 1:
            miss.append((a, zaehlen(x, e["alt"]), e["alt"][:70]))
            continue
        x = ersetze(x, e["alt"], e["neu"])
        ok += 1
    for feld, wert in LISTEN.get(a, {}).items():
        x["p2"][feld] = wert
    if urteil != "richtig":
        x["pruefer2"] = urteil + ": " + (b["befund"] if grund == "bestaetigt" else grund)
    zeilen[i] = json.dumps(x, ensure_ascii=False)
    open(t, "w", encoding="utf-8").write("\n".join(zeilen) + "\n")
open(K + "/pruefer2_befunde.jsonl", "w", encoding="utf-8").write("\n".join(aus) + "\n")
print("ersetzt", ok, "verworfen", verworfen, "nicht eindeutig", len(miss), miss)
print(sorted(summe.items()))
