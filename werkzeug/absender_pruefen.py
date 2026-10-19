# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer B-94 (Absender je Befehl, logik_stand_20261019.lua, 19.10.2026).

1. logik.lua uebersetzt in Lua 5.4 (wie UCP3) ohne Syntaxfehler.
2. logik.lua wird mit nachgebildetem `core` geladen; dabei laeuft der echte Einbau (absenderEinbauen). Der erzeugte
   Maschinencode wird mit capstone (x86, 32 Bit) zerlegt und Befehl fuer Befehl gegen den Plan geprueft:
   Ausfuehrer holen, Absender lesen, Kennung vergleichen, Sprung auf "normal", Auswahl sichern, Ausloeser und "ich"
   setzen, Ausfuehrer rufen, "ich" und Auswahl zurueck; "normal" = pop ebx; call eax; ret. Der Patch bei 0x00489387 ist
   CALL auf den Code + 4 NOP (9 Bytes, wie das Original).
3. Gegenprobe: steht an 0x00489387 ein unerwartetes Byte, baut logik.lua NICHTS ein.
Aufruf: python werkzeug/absender_pruefen.py"""
import os
import sys

import capstone
from lupa import lua54

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HIER, "logik_stand_20261019.lua")
STELLE, CODE, SICHER = 0x00489387, 0x30000000, 0x20000000
ORIGINAL = [0x8B, 0x04, 0x95, 0x10, 0x8E, 0xB3, 0x00, 0xFF, 0xD0]


def laden(bytes_an_stelle):
    lua = lua54.LuaRuntime(unpack_returned_tuples=True)
    erg = {"code": None, "geschrieben": {}, "log": []}
    speicher = dict(zip(range(STELLE, STELLE + 9), bytes_an_stelle))

    def read_byte(a):
        return speicher.get(a, 0)

    def write_code(a, t):
        bs = [t[i] for i in range(1, len(t) + 1)]
        erg["geschrieben"][a] = bs
        for i, v in enumerate(bs):
            speicher[a + i] = v

    def allocate_code(t):
        erg["code"] = [t[i] for i in range(1, len(t) + 1)]
        return CODE

    lua.globals().py = {"read_byte": read_byte, "write_code": write_code, "allocate_code": allocate_code,
                        "log": lambda lvl, s: erg["log"].append(str(s))}
    lua.execute("""
      local py = py
      local leer = function() return 0 end
      core = setmetatable({
        readByte = function(a) return py.read_byte(a) end,
        writeCode = function(a, t) py.write_code(a, t) end,
        allocateCode = function(t) return py.allocate_code(t) end,
        allocate = function(n) return %d end,
      }, { __index = function() return leer end })
      INFO, WARNING, DEBUG, ERROR = 1, 2, 3, 4
      log = function(l, s) py.log(l, s) end
      -- wie UCP3 (gemessen 19.10. 22:55): ein Modul darf keine globale Variable anlegen
      setmetatable(_G, { __index = function() return leer end,
                         __newindex = function(t, k) error("global assignment not permitted in module: " .. tostring(k)) end })
    """ % SICHER)
    quelle = open(QUELLE, encoding="utf-8").read()
    lade = lua.eval("function(s) local f, e = load(s, 'logik.lua', 't'); if f then return f, '' end; return nil, e end")
    f, fehler = lade(quelle)
    if f is None:
        raise SystemExit("ROT Syntax: %s" % fehler)
    try:
        f()
    except Exception as ex:                       # Lauf mit Platzhaltern darf scheitern - Einbau laeuft ganz am Ende
        erg["log"].append("Ladefehler (Platzhalter): %s" % str(ex)[:200])
    return erg, speicher


def main():
    ok = []

    def pruefe(text, wahr, info=""):
        ok.append(bool(wahr))
        print("%-4s %s%s" % ("OK" if wahr else "ROT", text, (" - " + info) if info else ""), flush=True)

    erg, speicher = laden(ORIGINAL)
    pruefe("1 logik.lua uebersetzt (Lua 5.4)", True)
    einbau = [z for z in erg["log"] if "ABSENDER beim Laden" in z]
    pruefe("2 Einbau beim Laden gemeldet", einbau and "eingebaut" in einbau[0], einbau[0] if einbau else str(erg["log"][-3:]))
    code = erg["code"] or []
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    befehle = [(i.address, i.mnemonic, i.op_str) for i in md.disasm(bytes(code), CODE)]
    for a, m, o in befehle:
        print("      0x%08X  %-6s %s" % (a, m, o))
    text = [("%s %s" % (m, o)).strip() for _, m, o in befehle]
    erwartet = [
        "mov eax, dword ptr [edx*4 + 0xb38e10]", "push ebx", "mov ebx, dword ptr [ecx + esi + 0x3c680]", "push ebx",
        "and ebx, 0xffffff00", "cmp ebx, 0x53414d00", "pop ebx", None, "movzx ebx, bl", "push esi", "push edi", "push eax",
        "push ecx", "mov esi, 0x1387fac", "mov edi, 0x%x" % SICHER, "mov ecx, 0x64",
        "rep movsd dword ptr es:[edi], dword ptr [esi]", "pop ecx",
        "pop eax", "pop edi", "pop esi", "mov dword ptr [esi + 0x109e70], ebx", "push dword ptr [esi + 0x109e74]",
        "mov dword ptr [esi + 0x109e74], ebx", "call eax", "pop dword ptr [esi + 0x109e74]", "push esi", "push edi",
        "mov esi, 0x%x" % SICHER, "mov edi, 0x1387fac", "mov ecx, 0x64", "rep movsd dword ptr es:[edi], dword ptr [esi]",
        "pop edi", "pop esi", "pop ebx", "ret", "pop ebx", "call eax", "ret"]
    gleich = len(text) == len(erwartet) and all(e is None or e == t for e, t in zip(erwartet, text))
    pruefe("3 Maschinencode Befehl fuer Befehl wie geplant (%d Befehle)" % len(text), gleich,
           "" if gleich else "Abweichung: %s" % [(e, t) for e, t in zip(erwartet, text) if e and e != t][:3])
    jne = befehle[7] if len(befehle) > 7 else None
    normal = befehle[-3][0] if len(befehle) >= 3 else None
    pruefe("4 jne springt auf 'normal' (pop ebx; call eax; ret)", jne and jne[1] == "jne" and int(jne[2], 16) == normal,
           "%s -> 0x%X" % (jne, normal or 0))
    patch = erg["geschrieben"].get(STELLE)
    ziel = (STELLE + 5 + int.from_bytes(bytes(patch[1:5]), "little", signed=True)) & 0xFFFFFFFF if patch else None
    pruefe("5 Patch bei 0x00489387: CALL auf den Code + 4 NOP", patch and patch[0] == 0xE8 and patch[5:] == [0x90] * 4
           and ziel == CODE and len(patch) == 9, "Ziel 0x%X" % (ziel or 0))
    # 6 Gegenprobe: unerwartetes Byte -> nichts eingebaut
    erg2, _ = laden([0x8B, 0x04, 0x95, 0x10, 0x8E, 0xB3, 0x00, 0xFF, 0xD1])
    meldung = [z for z in erg2["log"] if "ABSENDER beim Laden" in z]
    pruefe("6 Gegenprobe: fremdes Byte an der Stelle -> nichts geschrieben", not erg2["geschrieben"] and meldung
           and "unerwartet" in meldung[0], meldung[0] if meldung else "keine Meldung")
    print("%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
