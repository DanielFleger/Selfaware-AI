# -*- coding: utf-8 -*-
"""Lord-Kampf aus einem Lageprotokoll messen (SAI 12.10., Daniel 00:52: "wie man am Sieg sehen kann: es waren VIEL zu
viel Assassinen" und 00:49 "es wird nicht berechnet, wie viele Verteidiger da sind - man koennte auch mit weniger gewinnen").

Je Runde ab dem ersten Treffer am gegnerischen Lord:
  am_lord   = eigene Assassinen hoechstens NAH Felder neben ihm (die zuschlagen koennen)
  schaden   = Lord-Leben vorher - nachher
  tote      = eigene Assassinen, die in dieser Runde verschwanden und zuletzt hoechstens 3 Felder neben ihm standen
  wache     = feindliche Truppen (ohne Lord) im Umkreis 15, getrennt Fern/Nah
Ausgabe: Schaden je Assassine und Tick (r), Ticks je toter Assassine am Lord (k), Verteidiger, und die Rechnung
"wie viele reichen": n Assassinen, von denen alle k Ticks einer faellt, machen r*k*(n + n-1 + ... + 1) Schaden.
Aufruf: uv run python -m selfaware.tools.analysis.lordkampf_messen <lage_....jsonl.gz> [nah=2]"""
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

from selfaware.telemetry.lageprotokoll import runden

FERNKAMPF = {22, 23, 70, 72, 74, 76}
TRUPPE = {22, 23, 24, 25, 26, 27, 28, 37, 70, 71, 72, 73, 74, 75, 76}


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def messen(pfad, nah=2, sp=1):
    reihe, vorher, alt_lord, start = [], {}, None, None
    for t, st, E, G in runden(pfad):
        lord = next((e for e in E if e["typ"] == 55 and e["besitzer"] not in (0, sp)), None)
        eigen = {e["nr"]: e for e in E if e["typ"] == 73 and e["besitzer"] == sp}
        if lord is None:
            if alt_lord is not None:
                reihe.append(dict(t=t, tot_lord=True))
            break
        lp = (lord["x"], lord["y"])
        if alt_lord is not None and lord["leben"] < alt_lord[1] and start is None:
            start = alt_lord[0]
        if start is not None:
            am = [n for n, e in eigen.items() if schach((e["x"], e["y"]), lp) <= nah]
            tote = [n for n, e in vorher.items() if n not in eigen and schach((e["x"], e["y"]), lp) <= 3]
            wache = [e for e in E if e["besitzer"] not in (0, sp) and e["typ"] in TRUPPE]
            reihe.append(dict(t=t, dt=t - alt_lord[0], leben=lord["leben"], schaden=alt_lord[1] - lord["leben"],
                              am_lord=len(am), tote=len(tote),
                              fern=sum(1 for e in wache if e["typ"] in FERNKAMPF and schach((e["x"], e["y"]), lp) <= 15),
                              nah=sum(1 for e in wache if e["typ"] not in FERNKAMPF and schach((e["x"], e["y"]), lp) <= 15)))
        vorher, alt_lord = eigen, (t, lord["leben"], lp)
    return reihe


def auswerten(reihe):
    k = [z for z in reihe if not z.get("tot_lord")]
    if not k:
        return None
    a_ticks = sum(z["am_lord"] * z["dt"] for z in k)            # Assassinen-Ticks am Lord
    schaden = sum(z["schaden"] for z in k)
    tote = sum(z["tote"] for z in k)
    dauer = k[-1]["t"] - k[0]["t"] + k[0]["dt"]
    r = schaden / a_ticks if a_ticks else None
    kk = dauer / tote if tote else None
    return dict(dauer=dauer, schaden=schaden, assassinen_ticks=a_ticks, r_je_assassine_tick=r, tote_am_lord=tote,
                ticks_je_toten=kk, am_lord_max=max(z["am_lord"] for z in k),
                fern_max=max(z["fern"] for z in k), nah_max=max(z["nah"] for z in k))


def reicht(leben, r, k, bis=200):
    """Kleinste n, fuer die r*k*(n+...+1) >= leben (alle k Ticks faellt einer). Ohne Tote (k None): Zeitrechnung entfaellt."""
    if not r or not k:
        return None
    for n in range(1, bis):
        if r * k * n * (n + 1) / 2 >= leben:
            return n
    return None


if __name__ == "__main__":
    arg = dict(a.split("=", 1) for a in sys.argv[2:])
    reihe = messen(sys.argv[1], int(arg.get("nah", 2)))
    for z in reihe[:3] + ["..."] + reihe[-4:]:
        print(z)
    e = auswerten(reihe)
    print(json.dumps(e, indent=1))
    if e and reihe:
        voll = reihe[0]["leben"] + reihe[0]["schaden"]
        print("reicht rechnerisch (Lord %d Leben): %s Assassinen" % (voll, reicht(voll, e["r_je_assassine_tick"], e["ticks_je_toten"])))
