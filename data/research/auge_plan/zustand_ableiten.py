# -*- coding: utf-8 -*-
"""Auge-Plan: Was aendert das Spiel waehrend einer Partie? Rein aus dem Export, ohne Spielstart.
Sucht ab processGameTick alle erreichbaren Funktionen (Aufrufe und Funktionstabellen) und deren Schreibziele.
Lauf aus dem Repo-Stamm: python data/research/auge_plan/zustand_ableiten.py"""
import collections, json, os, re, sys
R = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference"
F = os.path.join(R, "functions")
HIER = os.path.dirname(os.path.abspath(__file__))
idx = json.load(open(os.path.join(R, "index.json"), encoding="utf-8"))
start = {x["address"].lower(): x for x in idx}
ges = sorted(start)
daten = {}
for a in ges:
    daten[a] = json.load(open(os.path.join(F, a + ".json"), encoding="utf-8"))
kurzname = lambda a: daten[a]["name"].split("::")[-1]
wurzel = [a for a in ges if kurzname(a) == "processGameTick"]
# Funktionstabellen: zusammenhaengende DATA-Verweise auf Funktionsanfaenge
eintrag = []
for a in ges:
    for r in daten[a]["entry_references"]:
        if r["kind"] == "DATA" and r["from"] not in start:
            eintrag.append((int(r["from"], 16), a))
eintrag.sort()
tabellen = []
for ad, f in eintrag:
    if tabellen and ad - tabellen[-1][1] in (0, 4):
        tabellen[-1][1] = ad
        tabellen[-1][2].append(f)
    else:
        tabellen.append([ad, ad, [f]])
gross = [t for t in tabellen]
def in_tabelle(z):
    for t in gross:
        if t[0] <= z <= t[1]:
            return t
    return None
AUFRUF = {"UNCONDITIONAL_CALL", "COMPUTED_CALL", "UNCONDITIONAL_JUMP", "COMPUTED_JUMP", "CONDITIONAL_JUMP"}
def nachfolger(a):
    aus = set()
    for r in daten[a]["references"]:
        z = r["to"].lower()
        if r["kind"] in AUFRUF and z in start and z != a:
            aus.add(z)
        elif r["kind"] in ("DATA", "READ", "PARAM"):
            if z in start:
                aus.add(z)
            else:
                try:
                    t = in_tabelle(int(z, 16))
                except ValueError:
                    t = None
                if t:
                    aus.update(t[2])
    return aus
sicht, stapel, von = set(wurzel), list(wurzel), {}
while stapel:
    a = stapel.pop()
    for n in nachfolger(a):
        if n not in sicht:
            sicht.add(n); von[n] = a; stapel.append(n)
print("Wurzel", [(a, kurzname(a)) for a in wurzel], "erreichbar", len(sicht), "von", len(ges), "Tabellen", len(gross))
json.dump({"wurzel": wurzel, "erreichbar": sorted(sicht), "von": von}, open(os.path.join(HIER, "erreichbar.json"), "w"), indent=0)
ein = json.load(open("data/research/funktionswissen/eingang.json", encoding="utf-8"))
print("nach Bereich", collections.Counter(ein.get("0x" + a, {}).get("bereich", "?") for a in sicht).most_common(12))
wichtig = "updateUnits updateBuildings updateEntities updateTribes updateWind updateDateAndTime processSingleTimeTick recomputeAttackInfo queueCommand UpdateTree1 updatePopularity aiBuyAndSellGoods renderTextToScreen playHurtSFXForUnit".split()
print({w: any(kurzname(a) == w for a in sicht) for w in wichtig})

# --- Schreibziele auf Felder abbilden ---
ty = json.load(open(os.path.join(R, "types.json"), encoding="utf-8"))
ZEILE = re.compile(r"^\s*(\d+)\s+(.+?)\s+(\d+)\s+(\S+)\s+\"")
typen = {}
for t in ty:
    d = t.get("definition") or ""
    if "Structure " not in d:
        continue
    gl = []
    for l in d.splitlines():
        m = ZEILE.match(l)
        if m:
            gl.append((int(m.group(1)), m.group(2), int(m.group(3)), m.group(4)))
    na = t["path"].rsplit("/", 1)[-1]
    if na not in typen or t["length"] > typen[na]["laenge"]:  # gleichnamige Typen: der groesste ist die Spielstruktur
        typen[na] = {"laenge": t["length"], "felder": gl}
def aufloesen(typ, off, pfad=""):
    s = typen.get(typ)
    if not s:
        return pfad, off, typ
    for o, tt, gr, na in s["felder"]:
        if o <= off < o + gr:
            m = re.match(r"^(.+?)\[(\d+)\]", tt)
            if m:
                rest = off - o
                el = m.group(1).strip()
                eg = typen[el]["laenge"] if el in typen else (gr // int(m.group(2)) or 1)
                return aufloesen(el, rest % eg, f"{pfad}.{na}[]".lstrip("."))
            return aufloesen(tt.strip(), off - o, f"{pfad}.{na}".lstrip("."))
    return f"{pfad}.+0x{off:x}".lstrip("."), off, "?"
sy = json.load(open(os.path.join(R, "symbols.json"), encoding="utf-8"))
DA, DE = 0x005b6000, 0x0242923f
lab = {}
for s in sy:
    if s["kind"] == "Label" and s["source"] == "USER_DEFINED" and re.fullmatch(r"[0-9a-f]{8}", s["address"]):
        a = int(s["address"], 16)
        if DA <= a <= DE:
            lab.setdefault(a, s["name"])
glob_s = []
for a, n in lab.items():
    t = {"DAT_GameState": "GameStateStructures"}.get(n, n[4:] if n.startswith("DAT_") else n)
    if t in typen:
        glob_s.append((a, a + typen[t]["laenge"], n, t))
    elif n == "SEC_RNG":
        glob_s.append((a, a + typen.get("RNG", {"laenge": 8})["laenge"], n, "RNG"))
glob_s.sort()
labs = sorted(lab)
import bisect
def ziel(adr):
    # verschachtelte Bezeichner: die groesste umfassende Struktur gewinnt, damit Code und Assembly denselben Pfad nennen
    tr = [g for g in glob_s if g[0] <= adr < g[1]]
    if tr:
        g = max(tr, key=lambda g: g[1] - g[0])
        p, _, _ = aufloesen(g[3], adr - g[0])
        return g[2], p
    j = bisect.bisect_right(labs, adr) - 1
    if j >= 0 and adr - labs[j] < 4096:
        return lab[labs[j]], ("+0x%x" % (adr - labs[j]) if adr != labs[j] else "")
    return "ohne_Namen", "%08x" % adr
ein = json.load(open("data/research/funktionswissen/eingang.json", encoding="utf-8"))
def spiel(a):
    return bool(ein.get("0x" + a, {}).get("spiel"))
LHS = re.compile(r"(?<![\w.&*])((?:DAT_\w+|SEC_RNG)(?:\.\w+|\[[^\]]*\])*)\s*(?:=(?!=)|\+=|-=|\|=|&=|\+\+|--)")
schreib = collections.defaultdict(lambda: {"f": set(), "q": set()})
lese = collections.defaultdict(set)
for a in sicht:
    d = daten[a]
    if not spiel(a):
        continue
    for r in d["references"]:
        try:
            z = int(r["to"], 16)
        except ValueError:
            continue
        if DA <= z <= DE:
            if r["kind"] in ("WRITE", "READ_WRITE"):
                k = ziel(z)
                schreib[k]["f"].add(a); schreib[k]["q"].add("asm")
            elif r["kind"] in ("READ", "DATA", "PARAM"):
                lese[ziel(z)].add(a)
    for m in LHS.finditer(d.get("pseudocode") or ""):
        roh = re.sub(r"\[[^\]]*\]", "[]", m.group(1))
        g, _, p = roh.partition(".")
        k = (g, p)
        schreib[k]["f"].add(a); schreib[k]["q"].add("code")
# ausserhalb des Takts geschrieben (Laden, Menue)
aussen = set()
for a in ges:
    if a in sicht:
        continue
    for r in daten[a]["references"]:
        if r["kind"] in ("WRITE", "READ_WRITE"):
            try:
                z = int(r["to"], 16)
            except ValueError:
                continue
            if DA <= z <= DE:
                aussen.add(ziel(z))
pro = collections.Counter(k[0] for k in schreib)
print("GameState", [g for g in glob_s if g[2] == "DAT_GameState"], "State-Bezeichner ohne Typ", [n for a, n in lab.items() if re.fullmatch(r"DAT_\w+State", n) and not any(g[2] == n for g in glob_s)][:30])
print("Globale Strukturen mit Typ", len(glob_s), "Bytes", sum(g[1] - g[0] for g in glob_s))
print("Felder mit Schreibzugriff im Takt", len(schreib), "je Oberbegriff", pro.most_common(45))
print("nur gelesen im Takt, nie im Takt geschrieben:", len([k for k in lese if k not in schreib]), "davon ausserhalb geschrieben:", len([k for k in lese if k not in schreib and k in aussen]))
json.dump({"schreib": [[k[0], k[1], sorted(v["q"]), len(v["f"]), [kurzname(a) for a in sorted(v["f"])[:4]]] for k, v in sorted(schreib.items())],
           "lese_nur": [[k[0], k[1], len(v), k in aussen] for k, v in sorted(lese.items()) if k not in schreib]},
          open(os.path.join(HIER, "zustand_roh.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# --- Vergleich mit dem Auge: Feldname steht im Quelltext von auge.py (gleiche Regel wie auge_abdeckung.py) ---
AUGE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HIER)))), "Selfaware-AI-auge", "werkzeug", "auge.py")
woerter = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", open(AUGE, encoding="utf-8").read()))
def bereich(k):
    g, p = k
    kopf = p.split(".")[0].replace("[]", "") if p else ""
    if g == "DAT_GameState" and kopf in ("playerDataArray", "mapAndTime"):
        return "GameState." + kopf
    return g
def blatt(p):
    t = [x.replace("[]", "") for x in p.split(".") if x and not x.startswith("+")]
    return t[-1] if t else ""
zeilen = []
for k, v in sorted(schreib.items()):
    b = blatt(k[1])
    zeilen.append({"bereich": bereich(k), "global": k[0], "feld": k[1], "quelle": "+".join(sorted(v["q"])), "schreiber": len(v["f"]),
                   "beispiel": " ".join(kurzname(a) for a in sorted(v["f"])[:3]), "liest_auge": "ja" if b and b in woerter else "nein",
                   "name_unklar": "ja" if re.search(r"^field\d+|Unk|unknown|_OR_|FUN_|^$", b) else "nein"})
import csv
with open(os.path.join(HIER, "zustand_felder.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(zeilen[0].keys()), delimiter=";")
    w.writeheader(); w.writerows(zeilen)
tab = collections.defaultdict(lambda: [0, 0, 0])
for z in zeilen:
    t = tab[z["bereich"]]
    t[0] += 1; t[1] += z["liest_auge"] == "ja"; t[2] += z["name_unklar"] == "ja"
print("Felder gesamt", len(zeilen), "liest Auge", sum(z["liest_auge"] == "ja" for z in zeilen), "Name unklar", sum(z["name_unklar"] == "ja" for z in zeilen))
for b, t in sorted(tab.items(), key=lambda x: -x[1][0])[:34]:
    print(f"{b:38s} Felder {t[0]:4d}  Auge {t[1]:4d}  unklar {t[2]:4d}")
