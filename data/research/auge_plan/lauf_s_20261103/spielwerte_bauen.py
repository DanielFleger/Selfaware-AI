# -*- coding: utf-8 -*-
"""B-142, Wunsch von SAI: Die gemessenen Spielwerte als eine Datei, damit nichts fest eingeschrieben werden muss.

Jeder Wert: Marke (gemessen: im Lauf gesehen; abgelesen: Tabelle des Spiels, im Lauf nicht vorgekommen), Quelle, Spielart (editor oder gefecht). Instanz und Liga-Stand stehen im Kopf.

  PYTHONIOENCODING=utf-8 python data/research/auge_plan/lauf_s_20261103/spielwerte_bauen.py
"""
import collections
import glob
import hashlib
import json
import os
import re

HIER = os.path.dirname(os.path.abspath(__file__))
LIGA = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz2\ucp\plugins\Mod-KI-Team-Liga-2.0.2\resources\balance\liga_ai.json"


def regeln(name):
    p = os.path.join(HIER, name + ".regeln.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def spielart(name):
    return "gefecht" if name.endswith("_g") else "editor"


def laufen():
    aus = []
    for name, befehl in (("laufen", "direkt"), ("laufen_g", "direkt"), ("laufen_trupp", "trupp"), ("laufen_trupp_g", "trupp")):
        j = regeln(name)
        for z in (j or {}).get("zeilen", []):
            if z.get("takte_je_feld") is not None:
                aus.append({"typ": z["typ"], "befehl": befehl, "lage": z.get("lage"), "takte_je_feld": z["takte_je_feld"], "spielart": spielart(name), "marke": "gemessen", "quelle": name + ".regeln.json"})
    return aus


def reichweite():
    """Je Art das hoechste Feld mit Schuss und das naechste ohne, ueber alle Proben: schussweite faehrt grob, schussweite_pfeil genau."""
    je = collections.defaultdict(lambda: {"schiesst": [], "nicht": [], "quellen": set()})
    for name in ("schussweite", "schussweite_pfeil", "geraete_weite", "reichweite", "reichweite_g"):
        for z in (regeln(name) or {}).get("zeilen", []):
            if "typ" not in z:
                continue
            if "abstand" in z:
                a_, ja = z["abstand"], z.get("urteil") == "schiesst" or bool(z.get("auf_ziel"))
            elif z.get("abstand_felder") is not None:
                a_, ja = z["abstand_felder"], bool(z.get("treffer"))
            else:
                continue
            ziel = je[(z["typ"], spielart(name))]
            (ziel["schiesst"] if ja else ziel["nicht"]).append(a_)
            ziel["quellen"].add(name + ".regeln.json")
    aus = []
    for (typ, art), w in sorted(je.items()):
        bis = max(w["schiesst"]) if w["schiesst"] else None
        nicht = sorted(a for a in w["nicht"] if bis is None or a > bis)
        aus.append({"typ": typ, "schiesst_bis_feld": bis, "nicht_ab_feld": nicht[0] if nicht else None, "spielart": art, "marke": "gemessen", "quelle": sorted(w["quellen"])})
    return aus


def geschoss_tempo():
    aus = []
    p = os.path.join(HIER, "geschosse_beschuss.txt")
    for zeile in open(p, encoding="utf-8"):
        if zeile.startswith("{"):
            for art, w in json.loads(zeile).items():
                aus.append({"art": art, "mikro_je_takt": w.get("mikro_je_takt"), "abstand_hoechstens_mikro": w.get("abstand_hoechstens"), "flogen": w.get("flogen"), "traf": w.get("traf"), "spielart": "editor", "marke": "gemessen", "quelle": "geschosse_beschuss.txt"})
            break
    return aus


def schaden_geschoss():
    aus = []
    for name in ("beschuss", "beschuss_g"):
        for z in (regeln(name) or {}).get("zeilen", []):
            for art in ("pfeil", "bolzen", "stein", "feuer"):
                if art in z:
                    gesehen = (z.get("gesehen") or {}).get(art, 0)
                    aus.append({"ziel_typ": z["ziel"], "geschoss": art, "schaden": z[art], "treffer": gesehen, "spielart": spielart(name), "marke": "gemessen" if gesehen else "abgelesen", "quelle": name + ".regeln.json"})
    return aus


def schaden_nahkampf():
    aus = []
    for name in ("nahkampf", "nahkampf_g"):
        for z in (regeln(name) or {}).get("zeilen", []):
            if z.get("treffer"):
                haeufig = max(z["werte"].items(), key=lambda q: q[1])[0] if z.get("werte") else None
                aus.append({"typ": z["schlaeger"], "opfer": z["opfer"], "schaden": int(haeufig) if haeufig is not None else None, "tabelle": z.get("soll"), "treffer": z["treffer"], "takte_zwischen_treffern": z.get("abstaende"), "spielart": spielart(name), "marke": "gemessen", "quelle": name + ".regeln.json"})
    return aus


def schusstakt():
    """Abstand zweier Schuesse desselben Schuetzen, aus der Aufzeichnung der Szene Beschuss (Editor). Lange Pausen (Ziel weg) zaehlen nicht."""
    from selfaware.tools.analysis import auge_regeln as ar
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
    f = sorted(glob.glob(os.path.join(HIER, "..", "laeufe", "lauf_s_*_beschuss.auge")), key=os.path.getmtime)
    if not f:
        return []
    k = Feldkarte.laden(feldliste=FELDLISTE)
    r, _ = ar.reihen_lesen(f[-1], k)
    g = ar.geschosse_lesen(f[-1], k)
    mitte = r[len(r) // 2][1]
    je = collections.defaultdict(list)
    for x in g:
        je[(int(mitte["typ"][x["schuetze"]]), x["art"], x["schuetze"])].append(x["von"])
    abst = collections.defaultdict(collections.Counter)
    for (typ, art, _), v in je.items():
        v = sorted(v)
        for a_, b in zip(v, v[1:]):
            if b - a_ <= 300:
                abst[(typ, art)][b - a_] += 1
    return [{"typ": typ, "geschoss": art, "takte_zwischen_schuessen_haeufig": c.most_common(4), "anzahl": sum(c.values()), "spielart": "editor", "marke": "gemessen", "quelle": os.path.basename(f[-1])} for (typ, art), c in sorted(abst.items())]


def main():
    liga = hashlib.sha256(open(LIGA, "rb").read()).hexdigest() if os.path.exists(LIGA) else None
    d = {
        "stand": "2026-11-04",
        "instanz": 2,
        "liga_datei": "Mod-KI-Team-Liga-2.0.2/resources/balance/liga_ai.json",
        "liga_sha256": liga,
        "marken": {"gemessen": "im Lauf gesehen", "abgelesen": "Wert der Spieltabelle, im Lauf nicht vorgekommen"},
        "einheiten": {"takt": "ein Spieltakt", "feld": "eine Kachel", "mikro": "8 je Feld"},
        "laufen": laufen(),
        "reichweite": reichweite(),
        "geschoss_tempo": geschoss_tempo(),
        "schaden_geschoss": schaden_geschoss(),
        "schaden_nahkampf": schaden_nahkampf(),
        "schusstakt": schusstakt(),
    }
    with open(os.path.join(HIER, "spielwerte_gemessen.json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=0)
    print({k: len(v) for k, v in d.items() if isinstance(v, list)}, "Liga", (liga or "")[:12])
    return d


if __name__ == "__main__":
    main()
