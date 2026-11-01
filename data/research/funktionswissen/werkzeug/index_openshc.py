import sys, os, re, json, collections
CPP, SRC, LISTE, OUT = sys.argv[1:5]
MARK = re.compile(r"//\s*(FUNCTION|STUB|LIBRARY|TEMPLATE|SYNTHETIC)\s*:\s*STRONGHOLDCRUSADER\s+0x([0-9A-Fa-f]{8})")
def sammeln(wurzel):
    res = {}
    for d, _, fs in os.walk(wurzel):
        for f in fs:
            if not f.endswith(".cpp"): continue
            p = os.path.join(d, f); t = open(p, encoding="utf-8", errors="replace").read()
            ms = list(MARK.finditer(t))
            for i, m in enumerate(ms):
                ende = ms[i+1].start() if i+1 < len(ms) else len(t)
                body = t[m.start():ende]
                res.setdefault(int(m.group(2), 16), []).append({"datei": os.path.relpath(p, wurzel), "art": m.group(1), "code": body})
    return res
gh = sammeln(CPP); rp = sammeln(SRC)
d = json.load(open(LISTE, encoding="utf-8"))
st = collections.Counter(); out = {}
for x in d:
    a = int(x["adresse"], 16)
    g = gh.get(a); r = rp.get(a)
    quelle = "nachgebaut" if r else ("ghidra" if g else "keine")
    st[(x["spiel"], quelle)] += 1
    out[x["adresse"]] = {"name": x["name"], "bereich": x["bereich"], "spiel": x["spiel"], "quelle": quelle,
        "datei": (r or g or [{}])[0].get("datei"), "code": (r or g or [{"code": ""}])[0]["code"]}
print("Marker ghidra-cpp:", len(gh), " nachgebaut (src):", len(rp))
for k, v in sorted(st.items()): print(("spielrelevant" if k[0] else "rest"), k[1], v)
print("ghidra-cpp-Adressen nicht in unserer Liste:", len(set(gh) - {int(x["adresse"],16) for x in d}))
L = [len(v["code"]) for v in out.values() if v["spiel"]]; print("Zeichen spielrelevant gesamt:", sum(L), "Mittel", sum(L)//len(L))
L2 = [len(v["code"]) for v in out.values()]; print("Zeichen alle:", sum(L2))
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
