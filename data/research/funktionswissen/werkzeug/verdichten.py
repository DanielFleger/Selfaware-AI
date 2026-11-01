import re, json, sys
def verdichten(c):
    c = re.sub(r"^\s*#include.*$|^\s*using .*;$", "", c, flags=re.M)
    c = re.sub(r"/\*\s*(WARNING|decompilerscript)[^*]*\*/", "", c)
    c = re.sub(r"MACRO_CALL_MEMBER\(\s*([\w:]+)::(\w+)\s*,\s*[\w:]+\s*\)", r"\2", c)
    c = re.sub(r"MACRO_CALL\(\s*([\w:]+)::(\w+)\s*\)", r"\2", c)
    c = re.sub(r"\b(?:OpenSHC::)?(?:\w+::)*(DAT_\w+)::(?:instance|ptr)\b", r"\1", c)
    c = re.sub(r"\bOpenSHC::(?:\w+::)*", "", c)
    c = re.sub(r"\(int\)\(\(int\)\(([^()]*)\)\)", r"\1", c)
    c = re.sub(r"\n\s*\n+", "\n", c)
    return re.sub(r"[ \t]+", " ", c).strip()
if __name__ == "__main__":
    e = json.load(open(sys.argv[1], encoding="utf-8"))
    for v in e.values(): v["kurz"] = verdichten(v["code"])
    L = [len(v["kurz"]) for v in e.values() if v["spiel"]]
    print("verdichtet spielrelevant:", sum(L), "Mittel", sum(L)//len(L), "Median", sorted(L)[len(L)//2], ">20000:", sum(x>20000 for x in L), "<1500:", sum(x<1500 for x in L))
    print("alle:", sum(len(v["kurz"]) for v in e.values()))
    print("ohne Quelle (spiel):", [(a, v["name"]) for a, v in e.items() if v["spiel"] and v["quelle"]=="keine"])
    json.dump(e, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)
    print(e["0x00465e60"]["kurz"][:900])
