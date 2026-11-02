# -*- coding: utf-8 -*-
"""B-141 Gegenprobe ohne Agenten: haelt Grenzen und Namen der Erklaerungen gegen den Ghidra-Export.

Grenze: "ab 40" und "0x27 < x" teilen an derselben Stelle (Schnitt 40). Verglichen wird der Schnitt der
Erklaerung mit allen Schnitten aus Pseudocode und Assembly (CMP + naechster Sprung).
Meldet Verdacht, kein Urteil: Ein Treffer heisst nur, dass die Stelle so nicht im Export steht.
Lauf aus dem Ordner funktionswissen: python korrektur/gegenprobe.py
"""
import glob, json, os, re, sys

EX = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions"
K = "korrektur"
ZAHL = r"(0x[0-9a-fA-F]+|\d{1,3}(?:\.\d{3})+|\d+)"
UNTEN = {"ab", "mindestens", "unter", "weniger als", "kleiner als", ">=", "<", "≥"}
OBEN = {"mehr als", "über", "ueber", "größer als", "groesser als", "höchstens", "hoechstens", "maximal", "<=", ">", "≤"}
WORT = re.compile(r"(?<![\w.<>=-])(mehr als|über|ueber|größer als|groesser als|höchstens|hoechstens|maximal|mindestens|weniger als|kleiner als|unter|ab|<=|>=|≤|≥|<|>)\s*" + ZAHL + r"(?![\w.]*[A-Za-z_])", re.I)
LINKS = re.compile(r"(?<![\w.])" + ZAHL + r"\s*(<=|>=|<|>)\s*[A-Za-z_(\[*]")
NAME = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
ASM_CMP = re.compile(r"^CMP\s+.*,\s*(0x[0-9a-fA-F]+|\d+)$")
ASM_UNTEN = {"JL", "JGE", "JB", "JAE", "JC", "JNC", "JNL", "JNB"}
ASM_OBEN = {"JLE", "JG", "JBE", "JA", "JNA", "JNG", "JNLE", "JNBE"}


def wert(s):
    s = s.replace(".", "") if not s.lower().startswith("0x") else s
    return int(s, 16) if s.lower().startswith("0x") else int(s)


def schnitte_pseudo(code):
    aus = set()
    for m in re.finditer(r"(?<![<>=!-])(<=|>=|<|>)(?![<>=])\s*(0x[0-9a-fA-F]+|\d+)\b", code):
        aus.add(wert(m.group(2)) + (1 if m.group(1) in ("<=", ">") else 0))
    for m in re.finditer(r"(?<![\w.])(0x[0-9a-fA-F]+|\d+)\s*(<=|>=|<|>)(?![<>=])", code):
        aus.add(wert(m.group(1)) + (1 if m.group(2) in (">=", "<") else 0))
    return aus


def schnitte_asm(zeilen):
    aus = set()
    for i, z in enumerate(zeilen):
        m = ASM_CMP.match(z["text"])
        if not m:
            continue
        for n in zeilen[i + 1:i + 3]:
            op = n["text"].split()[0]
            if op in ASM_UNTEN:
                aus.add(wert(m.group(1)))
            elif op in ASM_OBEN:
                aus.add(wert(m.group(1)) + 1)
            if op.startswith("J"):
                break
    return aus


def ansprueche(text):
    """(Schnitt, Zahl, Fundstelle) je Grenze in einem Satz. "bis" zaehlt nicht: fast immer ein Bereich."""
    aus = []
    for m in WORT.finditer(text):
        w = m.group(1).lower()
        n = wert(m.group(2))
        if n < 2:
            continue
        aus.append((n + (1 if w in OBEN else 0), n, m.group(0)))
    for m in LINKS.finditer(text):
        n = wert(m.group(1))
        if n >= 2:
            aus.append((n + (1 if m.group(2) in ("<", ">=") else 0), n, m.group(0)))
    return aus


def zahlen(code, zeilen):
    aus = {wert(x) for x in re.findall(r"(?<![\w.])(0x[0-9a-fA-F]+|\d+)(?![\w.])", code)}
    for z in zeilen:
        aus |= {wert(x) for x in re.findall(r"(?<![\w.])(0x[0-9a-fA-F]+|\d+)(?![\w.])", z["text"])}
    return aus


def namen_von(text):
    return {t for t in NAME.findall(text) if "_" in t or re.search(r"[a-z][A-Z]", t) or re.search(r"[A-Za-z]\d", t)}


def pakete():
    code, soll = {}, {}
    for p in json.load(open(K + "/liste.json")):
        akt = None
        puffer = []
        for l in open(f"{K}/eingang/{p}.txt", encoding="utf-8"):
            if l.startswith("### "):
                akt = l.split()[1].lower()
                soll[akt] = p
                puffer = []
            elif l.startswith("--- ERKLAERUNG ---"):
                code[akt] = "".join(puffer)
            elif akt:
                puffer.append(l)
    return soll, code


def texte(x):
    r = x.get("p2", {}).get("regeln", [])
    return r if isinstance(r, list) else [str(r)]


def pruefe(x, ex, paketcode):
    """Liefert die Verdachtsstellen einer Erklaerung."""
    code = ex.get("pseudocode") or ""
    zeilen = ex.get("assembly") or []
    cuts = schnitte_pseudo(code) | schnitte_asm(zeilen)
    alle = zahlen(code, zeilen)
    bekannt = namen_von(code) | namen_von(paketcode) | namen_von(" ".join(z["text"] for z in zeilen))
    aus = []
    for r in texte(x):
        for c, n, f in ansprueche(r):
            if c in cuts:
                continue
            art = "grenze_um_eins" if (c - 1 in cuts or c + 1 in cuts) else ("zahl_da_grenze_nicht" if n in alle else "zahl_fehlt")
            aus.append({"art": art, "zahl": n, "schnitt": c, "stelle": f, "regel": r})
    p2 = x.get("p2", {})
    for feld in ("ruft",):
        wert_feld = p2.get(feld, [])
        for t in sorted(namen_von(json.dumps(wert_feld, ensure_ascii=False)) - bekannt):
            aus.append({"art": "name_fehlt", "feld": feld, "name": t})
    return aus


def lade_export(a):
    return json.load(open(os.path.join(EX, a[2:].rjust(8, "0") + ".json"), encoding="utf-8"))


def lade_ergebnisse():
    da = {}
    for t in glob.glob(K + "/ergebnisse/*.jsonl"):
        for z in open(t, encoding="utf-8"):
            if z.strip():
                x = json.loads(z)
                da[x["adr"].lower()] = x
    return da


def zaehle(ergebnis):
    z = {}
    for fl in ergebnis.values():
        for f in fl:
            z[f["art"]] = z.get(f["art"], 0) + 1
    return z, sum(1 for fl in ergebnis.values() if fl)


if __name__ == "__main__":
    soll, code = pakete()
    neu = lade_ergebnisse()
    alt = {}
    for z in open("funktionen_spiel.vor_korrektur.jsonl", encoding="utf-8"):
        if z.strip():
            x = json.loads(z)
            alt[x["adr"].lower()] = x
    fehlt_ex = [a for a in soll if not os.path.exists(os.path.join(EX, a[2:].rjust(8, "0") + ".json"))]
    erg_neu, erg_alt, exporte = {}, {}, {}
    for a in soll:
        if a in fehlt_ex or a not in neu:
            continue
        exporte[a] = lade_export(a)
        erg_neu[a] = pruefe(neu[a], exporte[a], code.get(a, ""))
        if a in alt:
            erg_alt[a] = pruefe(alt[a], exporte[a], code.get(a, ""))
    print("soll", len(soll), "geprueft", len(erg_neu), "ohne Export", len(fehlt_ex))
    print("nachher", zaehle(erg_neu))
    print("vorher ", zaehle(erg_alt))
    # Negativlauf: stimmige Grenze kuenstlich um eins verschieben, die Probe muss anschlagen
    gesamt = treffer = 0
    for a, x in neu.items():
        if a not in exporte:
            continue
        ex = exporte[a]
        cuts = schnitte_pseudo(ex.get("pseudocode") or "") | schnitte_asm(ex.get("assembly") or [])
        for r in texte(x):
            for m in WORT.finditer(r):
                if m.group(1).lower() != "ab" or m.group(2).lower().startswith("0x"):
                    continue
                n = wert(m.group(2))
                if n < 2 or n not in cuts or n + 1 in cuts:
                    continue
                kaputt = dict(x)
                kaputt["p2"] = dict(x["p2"])
                kaputt["p2"]["regeln"] = [r[:m.start()] + f"ab {n + 1}" + r[m.end():]]
                gesamt += 1
                treffer += any(f["art"] != "name_fehlt" for f in pruefe(kaputt, ex, ""))
    print("Negativlauf: verschobene Grenzen", gesamt, "erkannt", treffer)
    # Fangquote an echten Fehlern: die vom Pruefer ersetzten Saetze (alter Wortlaut)
    bef = [json.loads(l) for l in open(K + "/pruefer_befunde.jsonl", encoding="utf-8") if l.strip()]
    stellen = gefangen = 0
    for b in bef:
        a = b["adr"].lower()
        for e in b.get("ersetzen", []):
            stellen += 1
            c = schnitte_pseudo(exporte[a].get("pseudocode") or "") | schnitte_asm(exporte[a].get("assembly") or [])
            gefangen += any(k[0] not in c for k in ansprueche(e["alt"]))
    print("Fangquote an Prueferfunden: alte Saetze", stellen, "davon haette die Probe gemeldet", gefangen)
    json.dump({a: f for a, f in sorted(erg_neu.items()) if f}, open(K + "/gegenprobe.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    for art in ("grenze_um_eins", "zahl_da_grenze_nicht", "zahl_fehlt", "name_fehlt"):
        print("---", art)
        for a, fl in sorted(erg_neu.items()):
            for f in fl:
                if f["art"] == art:
                    r = f.get("regel", "")
                    i = r.find(f.get("stelle", "")) if r else 0
                    print(a, neu[a]["name"], "|", f.get("stelle", f.get("name")), "|", r[max(0, i - 70):i + 60] if r else f.get("feld"))
