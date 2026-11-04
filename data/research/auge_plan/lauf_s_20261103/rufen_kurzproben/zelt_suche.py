# -*- coding: utf-8 -*-
import collections
import punkte_lesen as pl
P = pl.neueste("sonder24_g")
plan = pl.plan_von(P)
S = plan["von"]
gesehen = {}
for t, w in pl.stand(P, "DAT_BuildingsState", {"typ": "buildings[].buildingType", "x": "buildings[].x", "y": "buildings[].y", "pr": "buildings[].buildingProgress", "ma": "buildings[].currentEmployeeCount", "o": "buildings[].owner"}):
    for i in range(1, 80):
        ty = int(w["typ"][i])
        if ty and (i not in gesehen or gesehen[i][-1][1] != ty):
            gesehen.setdefault(i, []).append((t - S, ty, int(w["x"][i]), int(w["y"][i]), int(w["o"][i])))
print({i: v for i, v in gesehen.items() if any(q[1] in (80, 81, 82, 83, 84, 85, 86, 47) for q in v) or (v[0][0] > 0)})
leute = [e for e in plan["einheiten"] if e.get("posten") == "zelt4"]
for e in leute[:2]:
    fo = []
    for t, u in pl.stand(P, "DAT_UnitsState", {"z": "units[].state", "tr": "units[].tribeID", "x": "units[].x", "y": "units[].y"}):
        x = (int(u["z"][e["nr"]]), int(u["tr"][e["nr"]]))
        if not fo or fo[-1][1] != x:
            fo.append((t - S, x, int(u["x"][e["nr"]]), int(u["y"][e["nr"]])))
    print("Ingenieur", e["nr"], fo[:12])
wer = [e for e in plan["einheiten"] if e.get("posten") == "punkt_halten"]
fen = collections.defaultdict(list)
for t, u in pl.stand(P, "DAT_UnitsState", {"mx": "units[].microXPosition", "my": "units[].microYPosition"}):
    c = collections.Counter((int(u["mx"][e["nr"]]) // 8, int(u["my"][e["nr"]]) // 8) for e in wer)
    fen[(t - S) // 100].append(c.most_common(1)[0][1])
print("Stapel halten, je 100 Takte (von, hoechstens, Mittel):", [(k * 100, max(v), round(sum(v) / len(v), 1)) for k, v in sorted(fen.items())][:30])
