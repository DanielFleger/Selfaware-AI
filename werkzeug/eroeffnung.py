# -*- coding: utf-8 -*-
"""Eroeffnungsplan: Lager, Holzfaeller, Kornspeicher, Apfelplantagen, Huetten - mit dem Startholz (M14, 04.10.2026).

Daniels Regeln (Spielwissen): erst das Startholz verbauen, dann das leere Lager abreissen und nah am Holz neu
setzen; Kornspeicher nah an die Aepfel; Holzfaeller-Eingang direkt am Baum; jedes Gold zaehlt.
Gemessene Werte (Meilensteine M13d):
  - Holzfaeller: 18 Holz je Gang, Hacken ~2.000 Ticks, Laufen ~26 Ticks je Feld; faellbar nur Baumarten 1-4,
    ein Baum hat bis 9 Einheiten zu je 6 Holz (Baum +120).
  - Lager: ein neues Lager ist ein 4er-Block (6x6 Felder ab der Bau-Stelle), Mitte = Stelle + (3,3);
    ohne Lager darf es ueberall stehen. Kornspeicher-Eingang = Stelle + (2,4), Holzfaeller-Eingang = Stelle + (1,3)
    (rutscht neben einen Baum, wenn dort einer steht).
  - Huette +8 Wohnplaetze, Bergfried 10.
Rechnung:
  1. Lager + Holzfaeller: fuer jede Lagerstelle (jedes 2. Feld, hoechstens 45 Felder vom Bergfried) gierig bis zu
     K Huetten nach dem Holz, das in 20.000 Ticks ankommt = min(Holz je Tick * 20.000, Holz der eigenen Baeume);
     Holz je Tick = 18 / (2000 + 52*Weg Eingang-Lager + 52*Weg Eingang-Baum); mehrere Huetten teilen sich Baeume,
     jedes Holz wird aber nur einmal verplant (Umkreis 6 um den Eingang). Faellbar nur Zustand 2, Stufe < 4,
     Holz > 0 (findTree). Beste Lagerstelle gewinnt.
  2. Kornspeicher + Apfelplantagen: OR-Tools (farmen_mischen) ohne die Felder von Lager und Huetten;
     Kornspeicher abwechselnd an die beste Stelle zu den Farmen (3 Runden).
  3. Wohnhuetten so viele wie noetig, so nah wie moeglich am Bergfried-Eingang.
Grenzen: gierig beim Holz (nicht bewiesen); Baeume werden weniger - siehe holz_lebensdauer().

Aufruf:  python eroeffnung.py [holzfaeller=K] [aepfel=A]   (Daten aus ../daten/start_platz_*.txt, baeume_M7-04_T600.txt)
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farmen_mischen import mische, lies_karte

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
HACKEN, JE_FELD, JE_GANG, HOLZ_JE_EINHEIT = 2000.0, 26.0, 18.0, 6
KOSTEN = {"holzfaeller": 5, "speicher": 5, "apfel": 3, "huette": 5, "steinbruch": 25, "ochsen": 5}
BERGFRIED_EINGANG = (165, 111)

def baeume(datei="baeume_M7-04_T600.txt"):
    B = []
    for z in open(os.path.join(D, datei)).read().split("\n")[1:]:
        w = z.split()
        # faellbar laut findTree (0x004F3B90, gelesen 04.10.): Zustand 2, Stufe < 4, Holz (+120) > 0
        if len(w) >= 7 and int(w[2]) == 2 and int(w[5]) < 4 and int(w[6]) > 0:
            B.append({"nr": int(w[0]), "x": int(w[3]), "y": int(w[4]), "rest": int(w[6])})
    return B

def felder(x, y, g):
    return {(x + a, y + b) for a in range(g) for b in range(g)}

def plane_holz(karte_huette, karte_lager, B, K, horizont=20000, lager_max=45):
    """Lagerstelle + K Huetten so, dass in <horizont> Ticks moeglichst viel Holz im Lager ankommt.
    Je Huette: geliefert = min(Holz je Tick * horizont, Holz ihrer EIGENEN Baeume im Umkreis 6 um den Eingang);
    ein Baum gehoert nur einer Huette. Lager hoechstens <lager_max> Felder (Schachbrett) vom Bergfried-Eingang."""
    kand = []
    for (x, y) in karte_huette:
        ex, ey = x + 1, y + 3
        nah = [b for b in B if abs(b["x"] - ex) <= 6 and abs(b["y"] - ey) <= 6 and math.hypot(b["x"] - ex, b["y"] - ey) <= 6]
        if not nah:
            continue
        d, naechster = min((math.hypot(b["x"] - ex, b["y"] - ey), b["nr"]) for b in nah)
        if d <= 1.5:          # Eingang direkt am Baum (Daniel: Eingang neben einem Baum; 3 Huetten je Baum, 23:23)
            kand.append({"x": x, "y": y, "e": (ex, ey), "baum": d, "baeume": nah, "am_baum": naechster})
    if not kand:
        return None
    if len(karte_lager) <= 4:      # feste Lagerstelle(n) zum Vergleich - kein Filter
        lager = list(karte_lager)
    else:
        lager = [(x, y) for (x, y) in karte_lager if x % 2 == 0 and y % 2 == 0
                 and max(abs(x + 3 - BERGFRIED_EINGANG[0]), abs(y + 3 - BERGFRIED_EINGANG[1])) <= lager_max
                 and any(abs(x + 3 - k["e"][0]) <= 25 and abs(y + 3 - k["e"][1]) <= 25 for k in kand[::5])]
    beste = None
    for (sx, sy) in lager:
        sm = (sx + 3, sy + 3)
        block = felder(sx, sy, 6)
        def rate(k): return JE_GANG / (HACKEN + 2 * JE_FELD * (math.hypot(k["e"][0] - sm[0], k["e"][1] - sm[1]) + k["baum"]))
        wahl, belegt, vergeben, summe = [], set(block), set(), 0.0
        rest_holz = {}   # Baum -> noch nicht verplantes Holz (mehrere Huetten duerfen sich einen Baum teilen, Daniel 22:35)
        je_baum = {}     # Baum -> Huetten mit Eingang direkt daran (hoechstens 3, Daniel 23:23)
        for _ in range(K):
            bester = None
            for k in kand:
                f = felder(k["x"], k["y"], 3) | {k["e"]}
                if f & belegt:
                    continue
                holz = sum(rest_holz.get(b["nr"], HOLZ_JE_EINHEIT * b["rest"]) for b in k["baeume"])
                if holz <= 0:
                    continue
                schon = je_baum.get(k["am_baum"], 0)
                if schon >= 3:
                    continue
                geliefert = min(rate(k) * horizont, holz)
                wert = geliefert * (1.25 if schon in (1, 2) else 1.0)   # Haeufung um einen Baum bevorzugen
                if bester is None or wert > bester[0]:
                    bester = (wert, k, f)
            if bester is None:
                break
            g, k, f = bester
            g = min(rate(k) * horizont, sum(rest_holz.get(b["nr"], HOLZ_JE_EINHEIT * b["rest"]) for b in k["baeume"]))
            je_baum[k["am_baum"]] = je_baum.get(k["am_baum"], 0) + 1
            wahl.append(dict(k, geliefert=g, rate=rate(k))); belegt |= f; summe += g
            offen = g   # das verplante Holz von den naechsten Baeumen abziehen
            for b in sorted(k["baeume"], key=lambda b: math.hypot(b["x"] - k["e"][0], b["y"] - k["e"][1])):
                r = rest_holz.get(b["nr"], HOLZ_JE_EINHEIT * b["rest"])
                nimm = min(r, offen); rest_holz[b["nr"]] = r - nimm; offen -= nimm
                if offen <= 0:
                    break
        if wahl and (beste is None or summe > beste[0]):
            beste = (summe, (sx, sy), wahl, belegt)
    return beste

def plane_essen(karte_apfel, karte_speicher, belegt, A, mitte):
    apfel = {p for p in karte_apfel if not (felder(p[0], p[1], 10) & belegt)}
    ziel = mitte
    speicher, e = None, None
    for runde in range(3):
        e = mische({"apfel": apfel}, mitte, 70, {"apfel": {"wert": 1, "min": A, "max": A, "ziel": ziel}}, sekunden=20)
        if "farmen" not in e:
            return None
        frei = set(belegt)
        for f in e["farmen"]:
            frei |= felder(f["x"], f["y"], 10)
        best = None
        for (x, y) in karte_speicher:
            if abs(x - ziel[0]) > 40 or abs(y - ziel[1]) > 40 or (felder(x, y, 4) | {(x + 2, y + 4)}) & frei:
                continue
            ein = (x + 2, y + 4)
            w = sum(math.hypot(f["x"] + 4.5 - ein[0], f["y"] + 4.5 - ein[1]) for f in e["farmen"])
            if best is None or w < best[0]:
                best = (w, (x, y))
        if best is None:
            return None
        speicher = best[1]
        neues_ziel = (speicher[0] + 2, speicher[1] + 4)
        if neues_ziel == ziel:
            break
        ziel = neues_ziel
    return speicher, e

def plane_haeuser(karte_huette, belegt, H):
    wahl = []
    for (x, y) in sorted(karte_huette, key=lambda p: math.hypot(p[0] + 2 - BERGFRIED_EINGANG[0], p[1] + 2 - BERGFRIED_EINGANG[1])):
        f = felder(x, y, 4) | {(x + 2, y + 4)}
        if f & belegt:
            continue
        wahl.append((x, y)); belegt |= f
        if len(wahl) == H:
            break
    return wahl

def holz_lebensdauer(huetten, lager_mitte, horizont=20000):
    """Je Huette: Holz je 1000 Ticks und was sie in <horizont> Ticks liefert (begrenzt durch ihre eigenen Baeume)."""
    return [{"stelle": (k["x"], k["y"]), "eingang": k["e"], "holz_je_1000_ticks": round(1000 * k["rate"], 1),
             "geliefert_in_%d_ticks" % horizont: int(k["geliefert"]),
             "baeume_leer_nach_ticks": int(k["geliefert"] / k["rate"]) if k["geliefert"] < k["rate"] * horizont else None}
            for k in huetten]

def plane(K=8, A=6, holz=150, bevoelkerung_platz=10, steinbruch=True, huetten_min=0, start=None):
    """start = Kurzname eines mit karten_holen.py geholten Startstands (z. B. "M19"): dann kommen Platzkarten, Baeume
    und der Bergfried-Eingang aus diesem Start (Daniel 05.10.: erst schauen, wo der Bergfried steht)."""
    global BERGFRIED_EINGANG
    info = None
    if start:
        info = json.load(open(os.path.join(D, "start_%s.json" % start), encoding="utf-8"))
        BERGFRIED_EINGANG = tuple(info["bergfried_eingang"])
        vorsilbe, lagerdatei, baumdatei = "start_%s_platz_" % start, "start_%s_platz_lager_keins.txt" % start, "baeume_%s.txt" % start
    else:
        vorsilbe, lagerdatei, baumdatei = "start_platz_", "platzkarte_lager_keins.txt", "baeume_M7-04_T600.txt"
    karten = {n: lies_karte(os.path.join(D, vorsilbe + "%s.txt" % n)) for n in ("holzfaeller", "huette", "apfel", "speicher")}
    karten["lager"] = lies_karte(os.path.join(D, lagerdatei))
    B = baeume(baumdatei)
    eigene_seite = lambda p: True
    if info and info.get("feind_bergfried"):
        # Sicherheit (Daniel 04.10.: "je nach Metrik, z. B. wie nah der Gegner ist"; 05.10. 18:55: erst schauen, wo der
        # Bergfried steht): nur Stellen und Baeume, die naeher an unserem Bergfried liegen als an jedem feindlichen
        feinde = [tuple(v["eingang"]) for v in info["feind_bergfried"].values()]
        def eigene_seite(p):
            d_eigen = max(abs(p[0] - BERGFRIED_EINGANG[0]), abs(p[1] - BERGFRIED_EINGANG[1]))
            return all(d_eigen < max(abs(p[0] - f[0]), abs(p[1] - f[1])) for f in feinde)
        karten = {n: {q for q in k if eigene_seite(q)} for n, k in karten.items()}
        B = [b for b in B if eigene_seite((b[1], b[2]) if isinstance(b, (tuple, list)) else (b["x"], b["y"]))]
    h = plane_holz(karten["holzfaeller"], karten["lager"], B, K)
    if h is None:
        return {"fehler": "keine Holzfaeller-Stelle"}
    gesamt, lager, huetten, belegt = h
    rate = sum(k["rate"] for k in huetten)
    lm = (lager[0] + 3, lager[1] + 3)
    if A == 0:
        # 19.10. 21:08 (Daniel: "egal welche Map, egal welche Position - auf andere Nahrung umschalten, je nachdem was es gibt"):
        # A=0 = hier KEINE Nahrung planen; Kornspeicher, Aepfel, Jaeger, Brot setzt nahrungswahl.py (erstes_spiel.py)
        speicher, farmen = None, {"farmen": [], "status": "Nahrung aus nahrungswahl.py", "weg_summe": 0}
        es = (speicher, farmen)
    else:
        es = plane_essen(karten["apfel"], karten["speicher"], set(belegt), A, lm)
    if es is None:
        return {"fehler": "keine %d Apfelplantagen" % A}
    speicher, farmen = es
    belegt = set(belegt)
    if speicher is not None:
        belegt |= felder(speicher[0], speicher[1], 4) | {(speicher[0] + 2, speicher[1] + 4)}
    for f in farmen["farmen"]:
        belegt |= felder(f["x"], f["y"], 10)
    K = len(huetten)
    # Steinbruch so nah wie moeglich am neuen Lager, Ochsenjoch direkt daneben (Daniels Regel)
    stein = None
    if steinbruch:
        kb = {q for q in lies_karte(os.path.join(D, vorsilbe + "steinbruch.txt")) if eigene_seite(q)}
        ko = {q for q in lies_karte(os.path.join(D, vorsilbe + "ochsen.txt")) if eigene_seite(q)}
        for (x, y) in sorted(kb, key=lambda p: math.hypot(p[0] + 3 - lm[0], p[1] + 3 - lm[1])):
            fb = felder(x, y, 6)
            if fb & belegt:
                continue
            ochs = [(ox, oy) for (ox, oy) in ko if not (felder(ox, oy, 2) & (belegt | fb))
                    and max(abs(ox + 1 - (x + 3)), abs(oy + 1 - (y + 3))) <= 5]
            if ochs:
                o = min(ochs, key=lambda q: math.hypot(q[0] + 1 - lm[0], q[1] + 1 - lm[1]))
                stein = {"steinbruch": (x, y), "ochsen": o}
                belegt |= fb | felder(o[0], o[1], 2)
                break
    arbeiter = K + A + (4 if stein else 0)
    H = max(huetten_min, math.ceil((arbeiter + 2 - bevoelkerung_platz) / 8.0))
    haeuser = plane_haeuser(karten["huette"], belegt, H)
    kosten = KOSTEN["holzfaeller"] * K + KOSTEN["speicher"] + KOSTEN["apfel"] * A + KOSTEN["huette"] * H         + ((KOSTEN["steinbruch"] + KOSTEN["ochsen"]) if stein else 0)
    return {"lager": lager, "lager_mitte": lm, "holz_je_1000_ticks": round(1000 * rate, 1),
            "holz_in_20000_ticks": int(gesamt), "holzfaeller": [(k["x"], k["y"]) for k in huetten], "holz_lebensdauer": holz_lebensdauer(huetten, lm),
            "kornspeicher": speicher, "aepfel": [(f["x"], f["y"]) for f in farmen["farmen"]], "aepfel_status": farmen["status"],
            "aepfel_weg_summe": farmen["weg_summe"], "huetten": haeuser, "stein": stein, "arbeiter": arbeiter,
            "holz_kosten": kosten, "holz_rest": holz - kosten, "gold_kosten": 15 * A,
            "start": start, "spielstand": info["spielstand"] if info else "M7-04 Mensch Grumpy T600",
            "bergfried_eingang": BERGFRIED_EINGANG}

if __name__ == "__main__":
    arg = dict(a.split("=") for a in sys.argv[1:])
    import time
    t0 = time.time()
    p = plane(int(arg.get("holzfaeller", 8)), int(arg.get("aepfel", 6)), steinbruch=arg.get("steinbruch", "ja") == "ja",
              huetten_min=int(arg.get("huetten", 0)), start=arg.get("start"))
    p["sekunden"] = round(time.time() - t0, 1)
    print(json.dumps(p, ensure_ascii=False, indent=1))
    if "fehler" not in p:
        name = "eroeffnung_plan_%s.json" % arg["start"] if arg.get("start") else "eroeffnung_plan.json"
        json.dump(p, open(os.path.join(D, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("-> daten/" + name)
